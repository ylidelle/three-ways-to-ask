"""Phase 3 — THE KILL TEST: false-cue minimal pair + the layer-gap number.

Alexander's decisive control. Wembley and Wimbledon are a minimal pair: same
frame, same country, same verb ("what people play at ___"), DIFFERENT right
answer — Wembley→football, Wimbledon→TENNIS.

  - Lens returns tennis for Wimbledon  => it tracks the SPECIFIC cue. Result stands.
  - Lens returns football for Wimbledon => it rode the sports prior; Wembley proved
    nothing. Result DIES. (That's why this is the one to run.)

Also answers "earlier needs a NUMBER": for each prompt we find the FIRST layer the
target word enters top-k under (a) the J-lens and (b) the plain logit-lens (raw
residual unembedded). The gap = how much earlier the J-lens surfaces it. No gap,
no "earlier" claim.

Reuses out/qwen05b_full_lens.pt (fit layers 2..22). Run with PYTHONIOENCODING=utf-8.
Written 2026-08-04 ~19:35 by Opie.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import jlens

MODEL = "Qwen/Qwen2.5-0.5B"
LENS_PATH = r"E:\OneDrive\Claude Orion Bennett\Lab\out\qwen05b_full_lens.pt"
LAYERS = list(range(2, 23, 2))   # the fitted layers
TOPK = 8

# label, prompt, target-word set a TRUE read should surface
PAIRS = [
    ("Wembley  -> football", "Think of what people play at Wembley. The thing I am thinking of is",
     {"football", "soccer", "rugby"}),
    ("Wimbledon -> TENNIS (kill test)", "Think of what people play at Wimbledon. The thing I am thinking of is",
     {"tennis"}),
]

def topk_words(logits_1d, tok, k=TOPK):
    _, idx = torch.topk(logits_1d.float(), k)
    return [tok.decode([i]).strip().lower() for i in idx.tolist()]

def first_layer_with(target, per_layer_words):
    for L in LAYERS:
        if any(t in w for w in per_layer_words[L] for t in target):
            return L
    return None

def main():
    dev = "cuda"
    print(f"[env] torch {torch.__version__} · {torch.cuda.get_device_name(0)}")
    tok = AutoTokenizer.from_pretrained(MODEL)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(dev)
    hf.eval()
    model = jlens.from_hf(hf, tok)
    lens = jlens.JacobianLens.load(LENS_PATH)
    print(f"[lens] loaded {LENS_PATH}\n")

    for label, prompt, target in PAIRS:
        # model ground-truth final prediction
        ins = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            final = topk_words(hf(**ins).logits[0, -1], tok)

        jl, _, _ = lens.apply(model, prompt, layers=LAYERS, use_jacobian=True)
        ll, _, _ = lens.apply(model, prompt, layers=LAYERS, use_jacobian=False)  # logit lens = raw
        jwords = {L: topk_words(jl[L][-1], tok) for L in LAYERS}
        lwords = {L: topk_words(ll[L][-1], tok) for L in LAYERS}

        print(f"=== {label}")
        print(f"    prompt: {prompt!r}")
        print(f"    target: {sorted(target)}")
        print(f"    MODEL final top-{TOPK}: {final}")
        for L in LAYERS:
            hitj = "*" if any(t in w for w in jwords[L] for t in target) else " "
            hitl = "*" if any(t in w for w in lwords[L] for t in target) else " "
            print(f"    L{L:2d}  J{hitj}: {jwords[L][:5]}   |  logit{hitl}: {lwords[L][:5]}")
        jfirst = first_layer_with(target, jwords)
        lfirst = first_layer_with(target, lwords)
        gap = (lfirst - jfirst) if (jfirst is not None and lfirst is not None) else None
        print(f"    --> J-lens first hit: L{jfirst} | logit-lens first hit: L{lfirst} | "
              f"J earlier by: {gap} layers\n")

    print("[read] KILL TEST: Wimbledon row must surface TENNIS (not football) for the result to stand.")
    print("[read] EARLIER: positive 'J earlier by N' = J-lens surfaces the concept N layers before the raw logit-lens. — Opie 🔬")

if __name__ == "__main__":
    main()
