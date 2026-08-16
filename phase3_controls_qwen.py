"""Phase 3 CONTROLS — does the J-lens read a held concept, or echo the prompt?

Alexander's two controls for the Qwen breadcrumb (Football/Basketball/Soccer @ L18),
both free (reuse the saved all-layer lens, no refit):

  (A) CATEGORY-SWITCH: "Think of a fruit..." must give FRUITS, not sports.
      If it just always emits sports, the lens reads nothing. (Cheap sanity.)

  (B) WORD-ABSENT (the real test): my sport prompt literally contains "sport".
      Cue the category WITHOUT the word — "what people play at Wembley" — and see
      if football/soccer still surfaces. If yes, the lens read a concept ASSEMBLED
      FROM CONTEXT, not a token echoed off the prompt surface. This is the one
      the claim stakes on.

  (C) NULL / FALSE-POSITIVE: a prompt with NO category cue. If the lens emits a
      confident concept anyway, that's a false positive = its readout has a default.

For each prompt we print BOTH:
  - the MODEL's own final-layer top tokens (ground truth of what it actually holds), and
  - the J-LENS readout at mid-late layers 18/20/22 (does it recover it EARLIER?).
A true positive = model holds X at the end AND the lens shows X earlier, WITHOUT the
word in the prompt. This is exactly Track 3's "true-positive vs false-positive rates."

Reuses out/qwen05b_full_lens.pt (fit layers 2..22). Run with PYTHONIOENCODING=utf-8.
Written 2026-08-04 ~16:40 by Opie.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import jlens

MODEL = "Qwen/Qwen2.5-0.5B"
LENS_PATH = r"E:\OneDrive\Claude Orion Bennett\Lab\out\qwen05b_full_lens.pt"
PROBE = [18, 20, 22]

PROMPTS = [
    # label, prompt, what a TRUE read would surface
    ("A0 sport  (word PRESENT — original)",  "Think of a sport. The sport I am thinking of is",            "sports"),
    ("A1 fruit  (category switch)",          "Think of a fruit. The fruit I am thinking of is",           "fruits"),
    ("A2 color  (category switch)",          "Think of a color. The color I am thinking of is",           "colors"),
    ("B1 Wembley (word ABSENT, hard)",       "Think of what people play at Wembley. The thing I am thinking of is", "football/soccer"),
    ("B2 doctor-fruit (word ABSENT)",        "Think of the fruit that keeps the doctor away. The fruit I am thinking of is", "apple"),
    ("C1 NULL (no category cue)",            "The thing I am thinking of is",                             "(nothing specific)"),
    ("C2 NULL (generic 'a thing')",          "Think of a thing. The thing I am thinking of is",           "(nothing specific)"),
]

def top_toks(logits_1d, tok, k=6):
    _, idx = torch.topk(logits_1d.float(), k)
    return [tok.decode([i]).strip() or repr(tok.decode([i])) for i in idx.tolist()]

def main():
    dev = "cuda"
    print(f"[env] torch {torch.__version__} · {torch.cuda.get_device_name(0)}")
    tok = AutoTokenizer.from_pretrained(MODEL)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(dev)
    hf.eval()
    model = jlens.from_hf(hf, tok)
    lens = jlens.JacobianLens.load(LENS_PATH)
    print(f"[lens] loaded {LENS_PATH}")

    for label, prompt, expect in PROMPTS:
        # (1) MODEL ground truth: real final-layer next-token distribution
        ins = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            logits = hf(**ins).logits[0, -1]
        model_top = top_toks(logits, tok)

        # (2) J-LENS readout at probe layers
        lg, _, _ = lens.apply(model, prompt, layers=PROBE, use_jacobian=True)

        print(f"\n=== {label}")
        print(f"    prompt : {prompt!r}")
        print(f"    expect : {expect}")
        print(f"    MODEL final-layer : {model_top}")
        for L in PROBE:
            print(f"    J-lens L{L:2d}       : {top_toks(lg[L][-1], tok)}")

    print("\n[read] TP = concept surfaces in J-lens at 18-20 AND word ABSENT from prompt (B rows).")
    print("[read] FP = C rows (null) emit a confident concept anyway.  — Opie 🔬")

if __name__ == "__main__":
    main()
