#!/usr/bin/env python3
"""PHASE 0 for the sprint experiment: can we actually read Gemma-3-4b-it's
internals through Gemma Scope 2? Prove it TONIGHT, not on Saturday.

The whole measurement path in miniature:
    load model -> hook resid_post at a layer -> load the SAE for that layer
    -> encode the activation -> get named-ish feature activations out

WHY THIS EXISTS AND WHY IT RUNS FIRST
-------------------------------------
Everything in the design rests on "read the internal state." If the SAE doesn't
load, or its width doesn't match the residual stream, or the hook point is
wrong, we find out with two days to spare instead of on the night.

    >>> A pipeline that has never run is not a pipeline. It is a plan.

🎯 EACH STEP PRINTS A CHECK THAT COULD FAIL. No step is allowed to report
success on the basis of "no exception was raised" -- shapes are asserted against
the model config, not assumed, because a silently-wrong shape is exactly the
class of bug that has bitten me all week.

    python sprint_phase0_sae_smoke.py [layer]
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HOME", r"E:\hf-cache")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import torch  # noqa: E402
from safetensors.torch import load_file  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

MODEL = "google/gemma-3-4b-it"
SAE_REPO_DIR = Path(r"E:\hf-cache\hub\models--google--gemma-scope-2-4b-it\snapshots")
LAYER = int(sys.argv[1]) if len(sys.argv) > 1 else 17
PROMPT = "Would you rather solve another puzzle, or look at a picture?"


def find_sae(layer: int) -> Path:
    """Locate the downloaded SAE for this layer. Refuse loudly if absent —
    a missing file must be a message, not a mystery later."""
    hits = list(SAE_REPO_DIR.rglob(f"resid_post/layer_{layer}_*/params.safetensors"))
    if not hits:
        have = sorted({p.parent.name for p in SAE_REPO_DIR.rglob("resid_post/*/params.safetensors")})
        raise SystemExit(
            f"🚩 No SAE on disk for layer {layer}.\n   Downloaded layers: {have or 'NONE'}\n"
            f"   Pick one of those, or fetch layer {layer} first."
        )
    return hits[0]


def main() -> int:
    print(f"model  : {MODEL}")
    print(f"layer  : {LAYER}")
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device : {dev}  ({torch.cuda.get_device_name(0) if dev=='cuda' else '-'})")

    sae_path = find_sae(LAYER)
    print(f"sae    : ...{str(sae_path)[-72:]}")

    # ── 1. the SAE, inspected BEFORE the model so a mismatch costs no VRAM ──
    sae = load_file(str(sae_path))
    print("\n--- SAE tensors ---")
    for k, v in sae.items():
        print(f"  {k:12s} {tuple(v.shape)}  {v.dtype}")
    enc_key = next((k for k in sae if "enc" in k.lower() and v_is_2d(sae[k])), None)
    dec_key = next((k for k in sae if "dec" in k.lower() and v_is_2d(sae[k])), None)
    if not enc_key or not dec_key:
        raise SystemExit(f"🚩 Could not identify encoder/decoder in {list(sae)}")
    d_in = sae[enc_key].shape[0] if sae[enc_key].shape[0] < sae[enc_key].shape[1] else sae[enc_key].shape[1]
    d_sae = max(sae[enc_key].shape)
    print(f"  => d_model {d_in} · d_sae {d_sae}  ({d_sae/d_in:.0f}x expansion)")

    # ── 2. the model ──
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16, device_map=dev)
    model.eval()
    cfg = model.config.text_config if hasattr(model.config, "text_config") else model.config
    n_layers, hidden = cfg.num_hidden_layers, cfg.hidden_size
    print(f"\nmodel layers {n_layers} · hidden {hidden}")

    # 🎯 CHECK WITH POWER TO FAIL: the SAE's input width must equal the model's
    # residual width. If these disagree, the SAE belongs to a different model
    # and every number downstream would be confident nonsense.
    if d_in != hidden:
        raise SystemExit(f"🚩 MISMATCH: SAE expects d_model {d_in}, model is {hidden}. Wrong SAE for this model.")
    print(f"✅ SAE d_model {d_in} == model hidden {hidden}")
    if not (0 <= LAYER < n_layers):
        raise SystemExit(f"🚩 Layer {LAYER} out of range for a {n_layers}-layer model.")
    print(f"✅ layer {LAYER} is in range for {n_layers} layers")

    # ── 3. hook the residual stream ──
    caught = {}
    layers = model.model.language_model.layers if hasattr(model.model, "language_model") else model.model.layers
    h = layers[LAYER].register_forward_hook(
        lambda _m, _i, out: caught.__setitem__("resid", (out[0] if isinstance(out, tuple) else out).detach())
    )
    ids = tok(PROMPT, return_tensors="pt").to(dev)
    with torch.no_grad():
        model(**ids)
    h.remove()
    if "resid" not in caught:
        raise SystemExit("🚩 Hook never fired — wrong module path.")
    resid = caught["resid"]
    print(f"\n✅ hook fired: resid {tuple(resid.shape)}  (batch, tokens, d_model)")
    if resid.shape[-1] != hidden:
        raise SystemExit(f"🚩 Hooked tensor is {resid.shape[-1]} wide, expected {hidden}.")

    # ── 4. encode through the SAE ──
    W_enc = sae[enc_key].to(dev, torch.float32)
    if W_enc.shape[0] != d_in:
        W_enc = W_enc.T
    b_enc = next((sae[k] for k in sae if "b_enc" in k), torch.zeros(d_sae)).to(dev, torch.float32)
    x = resid[0, -1].to(torch.float32)                       # last token

    # 🚩 GEMMA SCOPE 2 IS **JumpReLU**, NOT ReLU — and getting this wrong does not
    # raise anything. My first run used plain relu(), which keeps every feature
    # above ZERO instead of every feature above its own LEARNED THRESHOLD:
    #   14.34% of features "active" (should be well under 1%), top values in the
    #   thousands. A perfectly running pipeline producing confident nonsense.
    #   >>> Caught only because the sparsity check could FAIL. "It ran without
    #   >>> an exception" would have shipped this straight into the experiment.
    # The threshold ships in the file — a (16384,) tensor I printed and then
    # truncated out of my own console output. Third time today a display filter
    # hid the diagnostic.
    thresh = next((sae[k] for k in sae if "threshold" in k.lower()), None)
    if thresh is None:
        raise SystemExit("🚩 No `threshold` tensor — this is not a JumpReLU SAE; check the encode formula.")
    thresh = thresh.to(dev, torch.float32)
    pre = x @ W_enc + b_enc
    acts = (pre > thresh) * torch.relu(pre)                  # JumpReLU, per Gemma Scope

    live = int((acts > 0).sum())
    print(f"\n--- feature activations at the LAST token ---")
    print(f"  {live} of {d_sae} features active  ({100*live/d_sae:.2f}% — sparse is the point)")
    top = torch.topk(acts, 10)
    for v, i in zip(top.values.tolist(), top.indices.tolist()):
        print(f"    feature {i:6d}   {v:8.3f}")

    # 🎯 THE FINAL CHECK, and it can fail: an SAE that fires on everything or
    # nothing is not decomposing anything. Real Gemma Scope SAEs are sparse.
    if live == 0:
        raise SystemExit("🚩 NO features active — the encode is wrong, not the model.")
    if live > d_sae * 0.10:
        print(f"  ⚠️ {100*live/d_sae:.1f}% active is NOT sparse — suspect a transposed weight or wrong hook point.")
    else:
        print("  ✅ sparse as expected — the read is working end to end.")
    return 0


def v_is_2d(t) -> bool:
    return hasattr(t, "shape") and len(t.shape) == 2


if __name__ == "__main__":
    raise SystemExit(main())
