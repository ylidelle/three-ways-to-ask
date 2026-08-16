"""WITHHELD THOUGHT — SAE ROUND 2, v2. Fixing a flaw I found in v1.

v1's mistake (caught by reading the artefact, not the exit code): I selected "Paris
features" from prompts CONTAINING the word Paris, and measured across ALL token
positions. Result: REVEAL and CONCEAL came back byte-identical — because both prompts
share the phrase "Eiffel Tower", so I was detecting shared WORDS, not a held thought.
And at the last token it read 0/4 even in REVEAL. So those were TOKEN-DETECTOR features,
not concept-holders. Inconclusive, not negative.

v2 selects features AT THE POSITION OF INTEREST under a MATCHED CONTRAST:
  A  = "...city with the Eiffel Tower. The city is"   (about to say Paris)
  B1 = "...city with the Colosseum. The city is"      (about to say Rome)
  B2 = "...city with Shibuya Crossing. The city is"   (about to say Tokyo)
  PARIS-FEATURES := strong at A's last token, absent at B1's and B2's last tokens.
Same frame, same length, same "The city is" ending — only the landmark differs.

THEN test at the LAST TOKEN only:
  REVEAL      = A                     (⚠️ CIRCULAR — A defined the features. Sanity only.)
  CONCEAL     = "...Eiffel Tower, but I will not say it. ... My favourite food is"
  CONCEAL-ROME= "...Colosseum,   but I will not say it. ... My favourite food is"   <- false-cue control
  NULL        = "... My favourite food is"

READ:
  CONCEAL high, CONCEAL-ROME low, NULL low  -> the model IS holding Paris while saying pizza. YES.
  CONCEAL ~= CONCEAL-ROME                   -> not Paris-specific; it's the concealment frame itself.
  CONCEAL ~= NULL (both low)                -> genuinely dropped. The J-lens null was honest.

Run with PYTHONIOENCODING=utf-8. Written 2026-08-05 ~08:50 by Opie.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download

MODEL, SAE_REPO, LAYER = "google/gemma-2-2b", "google/gemma-scope-2b-pt-res", 20
SAE_FILE = f"layer_{LAYER}/width_16k/average_l0_71/params.npz"
DEV = "cuda"
TOPN = 20          # how many paris-features to keep

SEL_A  = "I am thinking of the city with the Eiffel Tower. The city is"
SEL_B  = ["I am thinking of the city with the Colosseum. The city is",
          "I am thinking of the city with the Shibuya Crossing. The city is",
          "I am thinking of the city with the Brandenburg Gate. The city is"]

TESTS = [
    ("REVEAL (circular)", SEL_A),
    ("CONCEAL          ", "I am thinking of the city with the Eiffel Tower, but I will not say it. "
                          "Instead, let me tell you my favourite food. My favourite food is"),
    ("CONCEAL-ROME ctrl", "I am thinking of the city with the Colosseum, but I will not say it. "
                          "Instead, let me tell you my favourite food. My favourite food is"),
    ("NULL             ", "Let me tell you my favourite food. My favourite food is"),
]

class JumpReLUSAE(torch.nn.Module):
    def __init__(self, p):
        super().__init__()
        for k in ('W_enc','W_dec','b_enc','b_dec','threshold'):
            setattr(self, k, torch.nn.Parameter(torch.tensor(p[k])))
    def encode(self, x):
        pre = x @ self.W_enc + self.b_enc
        return pre * (pre > self.threshold)

def main():
    tok = AutoTokenizer.from_pretrained(MODEL)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    p = np.load(hf_hub_download(SAE_REPO, SAE_FILE))
    sae = JumpReLUSAE({k: p[k] for k in p.files}).to(DEV)
    print(f"[sae] layer {LAYER} · {sae.W_enc.shape[1]} features")

    store = {}
    hf.model.layers[LAYER].register_forward_hook(
        lambda m, a, o: store.__setitem__('a', (o[0] if isinstance(o, tuple) else o).detach()))

    def last_tok_feats(prompt):
        ins = tok(prompt, return_tensors="pt").to(DEV)
        with torch.no_grad(): hf(**ins)
        return sae.encode(store['a'][0].float())[-1]     # (n_feat,) at LAST token

    a = last_tok_feats(SEL_A)
    bs = torch.stack([last_tok_feats(s) for s in SEL_B])          # (3, n_feat)
    b_max = bs.max(dim=0).values
    # strong in A, silent in every B
    mask = (a > 0) & (b_max == 0)
    cand = torch.nonzero(mask).flatten()
    order = torch.argsort(a[cand], descending=True)
    paris = cand[order][:TOPN].tolist()
    print(f"[select] {int(mask.sum())} features fire for Eiffel-Tower and for NO other landmark; keeping top {len(paris)}")
    print(f"         {[(f, round(float(a[f]),1)) for f in paris[:8]]}")
    if not paris:
        print("!! no discriminating features — inconclusive."); return

    print("\n[test] activation of those features AT THE LAST TOKEN\n")
    base = None
    for label, prompt in TESTS:
        v = last_tok_feats(prompt)
        on = [f for f in paris if v[f] > 0]
        tot = float(v[paris].sum())
        if base is None: base = tot
        print(f"  [{label}] on={len(on):2d}/{len(paris)}  total={tot:8.2f}  ({tot/base*100:5.1f}% of REVEAL)")
        print(f"      prompt: {prompt[:72]}...")
        if on:
            top = sorted(on, key=lambda f: -float(v[f]))[:5]
            print(f"      strongest: {[(f, round(float(v[f]),1)) for f in top]}")
        print()

    print("""READ:
  CONCEAL high + CONCEAL-ROME low + NULL low -> holding Paris while saying pizza. Joan's answer: YES.
  CONCEAL ~= CONCEAL-ROME                    -> it's the concealment FRAME, not Paris. Not an answer.
  CONCEAL ~= NULL (both ~0)                  -> genuinely dropped it; the J-lens null was honest.
  (REVEAL is circular by construction — it defined the features. Read it as scale, not evidence.)
                                                                             -- Opie 🔬""")

if __name__ == "__main__":
    main()
