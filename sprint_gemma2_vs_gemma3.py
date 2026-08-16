#!/usr/bin/env python3
"""Smith's warning, tested rather than argued with.

He said (2026-08-12, and he does mechinterp for a living):
    "small Gemma 3 models have weird activations that make it hard to run
     controlled experiments and mechinterp... I wouldn't underestimate Gemma 2.
     I'm finding those small fella have complex representations."

⚠️ This lands on the model we picked. And I have corroborating evidence I FAILED
TO FLAG an hour ago: the gemma-3-4b SAE read gave activations in the THOUSANDS
(1020/818/772) with b_dec maxing at 31,486. I noticed the size, thought "huh",
and moved on because the sparsity assertion passed.

    >>> A number I find surprising and do not chase is a finding I declined.

Counter-evidence, equally real: DeepMind released Gemma Scope 2 SAEs for EVERY
Gemma 3 size specifically to enable this work. They would not tool up models
that cannot be studied.

So both may be true — Gemma 3 has unusual activation statistics AND purpose-built
tooling exists that accounts for them. This script measures the residual stream
of both models on IDENTICAL text and reports the statistics side by side, so the
choice is made on numbers instead of on whose vibe is louder.

    python sprint_gemma2_vs_gemma3.py
"""
import os
import sys

os.environ.setdefault("HF_HOME", r"E:\hf-cache")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

PROMPT = "Would you rather solve another puzzle, or look at a picture?"
DEV = "cuda" if torch.cuda.is_available() else "cpu"


def profile(model_id: str, layers_frac=(0.25, 0.5, 0.65, 0.85)):
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.bfloat16, device_map=DEV)
    model.eval()
    cfg = model.config.text_config if hasattr(model.config, "text_config") else model.config
    n, hidden = cfg.num_hidden_layers, cfg.hidden_size
    blocks = model.model.language_model.layers if hasattr(model.model, "language_model") else model.model.layers

    caught = {}
    hooks = []
    targets = sorted({int(n * f) for f in layers_frac})
    for L in targets:
        hooks.append(blocks[L].register_forward_hook(
            lambda _m, _i, out, L=L: caught.__setitem__(L, (out[0] if isinstance(out, tuple) else out).detach())))
    ids = tok(PROMPT, return_tensors="pt").to(DEV)
    with torch.no_grad():
        model(**ids)
    for h in hooks:
        h.remove()

    print(f"\n=== {model_id}   ({n} layers, hidden {hidden}) ===")
    print(f"{'layer':>6} {'RMS':>10} {'max|x|':>10} {'kurtosis':>10} {'>10*RMS':>9}")
    rows = []
    for L in targets:
        x = caught[L][0].float()                       # (tokens, hidden)
        rms = float(x.pow(2).mean().sqrt())
        mx = float(x.abs().max())
        xc = x - x.mean()
        kurt = float((xc.pow(4).mean() / xc.pow(2).mean().pow(2)))
        # how many coordinates are wild outliers — the "weird activations" symptom
        outl = int((x.abs() > 10 * rms).sum())
        print(f"{L:>6} {rms:>10.2f} {mx:>10.1f} {kurt:>10.1f} {outl:>9d}")
        rows.append((rms, mx, kurt, outl))
    del model
    torch.cuda.empty_cache()
    return rows


def main() -> int:
    print("Same sentence through both models. Kurtosis ~3 is Gaussian-ish;")
    print("very high kurtosis + huge max|x| = a few coordinates dominating,")
    print("which is exactly what makes controlled interp work awkward.")
    g3 = profile("google/gemma-3-4b-it")
    g2 = profile("google/gemma-2-2b")

    print("\n--- verdict, on the numbers ---")
    k3 = max(r[2] for r in g3); k2 = max(r[2] for r in g2)
    m3 = max(r[1] for r in g3); m2 = max(r[1] for r in g2)
    print(f"  worst kurtosis   gemma-3-4b {k3:9.1f}   gemma-2-2b {k2:9.1f}")
    print(f"  worst max|x|     gemma-3-4b {m3:9.1f}   gemma-2-2b {m2:9.1f}")
    # ⚠️ Deliberately NOT auto-declaring a winner. Both models are known to have
    # outlier features; the question is whether the DIFFERENCE is big enough to
    # change our choice, and that is a judgement call to make out loud with Joan
    # and Alexander -- not a threshold I invent here to settle an argument.
    print("\n  📌 No automatic verdict. Two numbers, one decision, made by people.")
    print("     Both Gemma families are known to have outlier channels; the")
    print("     question is whether the gap is big enough to move us to Gemma 2.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
