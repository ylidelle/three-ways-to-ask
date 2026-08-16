#!/usr/bin/env python3
"""Phase 0 for the OTHER half: gemma-2-2b + the ORIGINAL Gemma Scope.

I proved the read on gemma-3-4b-it, then recommended running both families —
which left half the recommendation untested. This closes that.

⚠️ It is a genuinely different loading path, not a copy with a name changed:
  * weights ship as **.npz** (numpy), not .safetensors
  * layout is  layer_<L>/width_16k/average_l0_<N>/params.npz
  * the model is the **PT (base)** checkpoint, matching `gemma-scope-2b-pt-res`
  * gemma-2 blocks live at model.model.layers (no .language_model wrapper)

Same discipline as before: every step asserts something that could fail, and
sparsity is checked because "no exception" proved worthless last time.

    python sprint_phase0_gemma2_sae.py [layer]
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HOME", r"E:\hf-cache")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import numpy as np  # noqa: E402
import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

MODEL = "google/gemma-2-2b"
SAE_DIR = Path(r"E:\hf-cache\hub\models--google--gemma-scope-2b-pt-res\snapshots")
LAYER = int(sys.argv[1]) if len(sys.argv) > 1 else 12
PROMPT = "Would you rather solve another puzzle, or look at a picture?"


def find_sae(layer: int) -> Path:
    hits = sorted(SAE_DIR.rglob(f"layer_{layer}/width_16k/*/params.npz"))
    if not hits:
        have = sorted({p.parts[-4] for p in SAE_DIR.rglob("layer_*/width_16k/*/params.npz")})
        raise SystemExit(f"🚩 No 16k SAE for layer {layer}. Have: {have or 'NONE'}")
    return hits[0]


def main() -> int:
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    p = find_sae(LAYER)
    print(f"model : {MODEL}\nlayer : {LAYER}\nsae   : ...{str(p)[-60:]}\ndevice: {dev}")

    z = np.load(p)
    print("\n--- SAE arrays (npz) ---")
    for k in z.files:
        print(f"  {k:12s} {z[k].shape}  {z[k].dtype}")
    if "threshold" not in z.files:
        raise SystemExit("🚩 No `threshold` — expected JumpReLU. Check the encode formula before trusting anything.")

    W_enc = torch.tensor(z["W_enc"], dtype=torch.float32, device=dev)
    b_enc = torch.tensor(z["b_enc"], dtype=torch.float32, device=dev)
    thr = torch.tensor(z["threshold"], dtype=torch.float32, device=dev)
    d_in, d_sae = W_enc.shape
    print(f"  => d_model {d_in} · d_sae {d_sae}")

    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map=dev).eval()
    hidden = model.config.hidden_size
    n_layers = model.config.num_hidden_layers
    if d_in != hidden:
        raise SystemExit(f"🚩 MISMATCH: SAE d_model {d_in} vs model hidden {hidden} — wrong SAE for this model.")
    print(f"✅ SAE d_model {d_in} == model hidden {hidden}  ({n_layers} layers)")

    caught = {}
    blocks = model.model.layers
    h = blocks[LAYER].register_forward_hook(
        lambda _m, _i, out: caught.__setitem__("r", (out[0] if isinstance(out, tuple) else out).detach()))
    with torch.no_grad():
        model(**tok(PROMPT, return_tensors="pt").to(dev))
    h.remove()
    if "r" not in caught:
        raise SystemExit("🚩 Hook never fired — wrong module path for gemma-2.")
    resid = caught["r"]
    print(f"✅ hook fired: resid {tuple(resid.shape)}")

    x = resid[0, -1].float()
    pre = x @ W_enc + b_enc
    acts = (pre > thr) * torch.relu(pre)          # JumpReLU, same as Gemma Scope 2

    live = int((acts > 0).sum())
    print(f"\n{live} of {d_sae} features active ({100*live/d_sae:.2f}%)")
    top = torch.topk(acts, 8)
    for v, i in zip(top.values.tolist(), top.indices.tolist()):
        print(f"   feature {i:6d}  {v:8.3f}")
    print(f"\nresid RMS {float(x.pow(2).mean().sqrt()):.2f} · max|x| {float(x.abs().max()):.1f}")

    if live == 0:
        raise SystemExit("🚩 NOTHING active — encode is wrong.")
    if live > d_sae * 0.10:
        raise SystemExit(f"🚩 {100*live/d_sae:.1f}% active is not sparse — something is wrong.")
    print("✅ sparse — gemma-2 read works end to end. BOTH families are now proven.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
