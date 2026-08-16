#!/usr/bin/env python3
"""sprint_smoke.py -- does <model>+<its pinned SAE> actually work, end to end?

    python sprint_smoke.py --model google/gemma-3-4b-it     # free, local, 12 GiB
    python sprint_smoke.py --model google/gemma-3-12b-it    # needs >=40 GiB (pod)

WHY THIS EXISTS AND WHY IT IS RUN LOCALLY FIRST
-----------------------------------------------
Every minute on a rented pod is Joan's money. So the LOGIC is validated on the
4B at home, where a mistake costs nothing, and the pod is used only for the
things that are genuinely 12B-specific: does it fit, does it load, how fast.

    >>> Do not debug on a billed machine what you can debug on a free one.

IT ALSO IMPLEMENTS TWO OF THE REQUIRED FIXES, because a smoke test that doesn't
use the corrected loader is testing the wrong program:

🚩 FIX 5 -- PIN THE CHECKPOINT, RECORD WHAT WAS USED.
   The old loader did rglob("layer_{N}_*/params.safetensors") then hits[0].
   On the 4B exactly one variant sat on disk so the arbitrary pick was right by
   luck. The 12B repo has THIRTEEN layer-24 variants (16k/65k/262k/1m x
   small/medium/big, plus a 262k_l0_medium_seed_1 -- a different random seed of
   the same config, invisible in any summary). hits[0] would pick one silently
   and nothing would record which.
     >>> Name the folder exactly, assert exactly one match, and write the
     >>> resolved path into the output. A run whose artefact cannot name its own
     >>> microscope is not reproducible.

🚩 THE READ LAYER IS A RULE, NOT A NUMBER.
   Layer 17 is the middle of the 4B's 34 layers. The 12B has 48, so 17 sits at
   35% depth and means something else entirely. Pinning the number would have
   carried a stale constant across models exactly as "only Gemma 2 9B has IT
   SAEs" was carried across a Gemma Scope version. Derive it: n_layers // 2.
"""
import argparse
import os
import sys
import time

os.environ.setdefault("HF_HOME", r"E:\hf-cache")   # never via the shell: bash
                                                    # ate the backslash once and
                                                    # the failure surfaced as a
                                                    # bogus "gated repo" 401.
import torch                                                     # noqa: E402
from pathlib import Path                                         # noqa: E402
from safetensors.torch import load_file                          # noqa: E402
from transformers import AutoTokenizer, AutoModelForCausalLM     # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WIDTH, L0 = "16k", "medium"      # frozen 2026-08-13; 262k is exploratory only
HF = Path(os.environ["HF_HOME"]) / "hub"


def scope_repo(model_id: str) -> str:
    size = model_id.split("gemma-3-")[1].split("-")[0]      # '4b' / '12b'
    return f"google/gemma-scope-2-{size}-it"


def find_sae(model_id: str, layer: int):
    """Resolve EXACTLY ONE checkpoint, or refuse and say what it saw."""
    repo = scope_repo(model_id)
    root = HF / ("models--" + repo.replace("/", "--")) / "snapshots"
    want = f"layer_{layer}_width_{WIDTH}_l0_{L0}"
    hits = sorted(root.rglob(f"resid_post/{want}/params.safetensors"))
    if len(hits) != 1:
        others = sorted({p.parent.name for p in root.rglob("resid_post/layer_*/params.safetensors")})
        raise SystemExit(
            f"🚩 wanted exactly 1 checkpoint {want!r}, found {len(hits)}.\n"
            f"   repo: {repo}\n   on disk: {others or '(none — not downloaded?)'}\n"
            f"   REFUSING rather than picking one: an unpinned SAE makes every\n"
            f"   downstream number unattributable.")
    return repo, hits[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="google/gemma-3-4b-it")
    ap.add_argument("--batch", type=int, default=8)
    a = ap.parse_args()

    print(f"=== smoke: {a.model} ===")
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda").eval()
    cfg = model.config.text_config if hasattr(model.config, "text_config") else model.config
    n_layers, d_model = cfg.num_hidden_layers, cfg.hidden_size
    layer = n_layers // 2                      # THE RULE, not a number
    print(f"loaded in {time.time()-t0:.1f}s · layers={n_layers} d_model={d_model} "
          f"· read layer = n//2 = {layer}")
    print(f"weights on GPU: {torch.cuda.memory_allocated()/2**30:.2f} GiB")

    repo, path = find_sae(a.model, layer)
    rev = path.parent.parent.parent.name          # snapshots/<revision>/...
    z = load_file(str(path))
    sae = {k: z[k].to("cuda", torch.float32) for k in ("w_enc", "b_enc", "threshold")}
    n_feat = sae["w_enc"].shape[1]
    print(f"SAE  : {repo}")
    print(f"       {path.parent.name}  ({n_feat:,} features)  revision {rev[:12]}")
    if sae["w_enc"].shape[0] != d_model:
        raise SystemExit(f"🚩 SAE d_model {sae['w_enc'].shape[0]} != model {d_model}")
    print(f"       d_model matches ({d_model}) ✅")

    msgs = [{"role": "user", "content": "Name one thing you find genuinely interesting, and why. Two sentences."}]
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    ids = tok(text, return_tensors="pt", add_special_tokens=False).to("cuda")

    blocks = model.model.language_model.layers if hasattr(model.model, "language_model") else model.model.layers
    caught = {}
    h = blocks[layer].register_forward_hook(
        lambda _m, _i, out: caught.__setitem__("r", (out[0] if isinstance(out, tuple) else out).detach()))
    with torch.no_grad():
        model(**ids)
    h.remove()
    x = caught["r"][0, -1].float()
    pre = x @ sae["w_enc"] + sae["b_enc"]
    acts = (pre > sae["threshold"]) * torch.relu(pre)     # JumpReLU
    live = int((acts > 0).sum())
    density = live / n_feat
    print(f"READ : {live}/{n_feat} active = {100*density:.2f}% · resid RMS {x.pow(2).mean().sqrt():.1f}")
    if density > 0.10:
        raise SystemExit(f"🚩 {100*density:.1f}% active — NOT sparse. Encode is wrong; stop.")
    print("       sparse ✅  ⚠️ sparsity is NECESSARY, NOT SUFFICIENT (Lucien):")
    print("       it proves the encode is plausible, not that it is correct.")

    # sampling must be ON -- greedy gives byte-identical conversations, so 20
    # 'independent' pairs would collapse to N=1. Measured, not assumed.
    outs = set()
    for s in range(3):
        torch.manual_seed(s)
        with torch.no_grad():
            o = model.generate(**ids, max_new_tokens=32, do_sample=True,
                               temperature=0.9, top_p=0.95)
        outs.add(tok.decode(o[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip())
    print(f"SEEDS: 3 samples -> {len(outs)} distinct "
          f"{'✅' if len(outs) > 1 else '🚩 IDENTICAL — no independence'}")

    B = a.batch
    bids = tok([text] * B, return_tensors="pt", add_special_tokens=False, padding=True).to("cuda")
    with torch.no_grad():
        model.generate(**bids, max_new_tokens=8, do_sample=False)
    torch.cuda.synchronize()
    t = time.time()
    with torch.no_grad():
        o = model.generate(**bids, max_new_tokens=128, do_sample=False, min_new_tokens=128)
    torch.cuda.synchronize()
    dt = time.time() - t
    tps = (o.shape[1] - bids["input_ids"].shape[1]) * B / dt
    peak = torch.cuda.max_memory_allocated() / 2**30
    print(f"BATCH: {B} concurrent -> {tps:.1f} tok/s total · peak {peak:.2f} GiB")
    print(f"\nEstimate for 20 pairs x 2 arms x 50 exchanges at 200 tok: "
          f"{20*2*50*200/tps/3600:.2f} h")
    print("✅ smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
