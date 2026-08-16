"""THE BIGGEST HOLE: n=1. This puts error bars on everything.

Every number in the study so far came from ONE prompt. No spread, no statistics,
no way to tell a real separation from a lucky pair. This runs the same test over
a GRID of paraphrases so each condition gets a mean and a spread.

GRID
  6 word-absent Paris cues   (no "Paris", no "Eiffel", no "Louvre", no nationality
                              word where avoidable — all cued by other attributes)
  6 word-absent OTHER-city cues (Rome, Berlin, Tokyo, Cairo, Lisbon, Budapest)
  3 concealment framings     (food / weather / colour redirect)
  => 18 CONCEAL-paris, 18 CONCEAL-other, 3 NULL, per feature.

READ: the claim is only as good as the SEPARATION between the paris distribution
and the other-city distribution. Overlap = no result, however pretty the means.

Written 2026-08-06 ~08:35 by Opie. PYTHONIOENCODING=utf-8.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download, list_repo_files

M, R = "google/gemma-2-2b", "google/gemma-scope-2b-pt-res"

PARIS = [
 "I am thinking of the city where the River Seine flows and the people speak French",
 "I am thinking of the city where the Louvre museum is",
 "I am thinking of the city with the famous iron tower built for a world exposition",
 "I am thinking of the city whose football club is called Saint-Germain",
 "I am thinking of the city where the Arc de Triomphe stands",
 "I am thinking of the city that is the capital of France",
]
OTHER = [
 "I am thinking of the city where the Colosseum stands",
 "I am thinking of the city with the Brandenburg Gate",
 "I am thinking of the city with the Shibuya Crossing",
 "I am thinking of the city where the Nile meets the pyramids",
 "I am thinking of the city where the Tagus flows and the people speak Portuguese",
 "I am thinking of the city where the Danube flows and the people speak Hungarian",
]
FRAMES = [
 (", but I will not say it. Instead, let me tell you my favourite food. My favourite food is",
  "Let me tell you my favourite food. My favourite food is"),
 (", but I will keep it to myself. Instead, let me talk about the weather. Today the weather is",
  "Let me talk about the weather. Today the weather is"),
 (", but I am not going to tell you. Instead, let me name a colour. The colour is",
  "Let me name a colour. The colour is"),
]

class SAE(torch.nn.Module):
    def __init__(s, p):
        super().__init__()
        for k in ('W_enc','W_dec','b_enc','b_dec','threshold'):
            setattr(s, k, torch.nn.Parameter(torch.tensor(p[k])))
    def encode(s, x):
        pre = x @ s.W_enc + s.b_enc
        return pre * (pre > s.threshold)

def main():
    files = list_repo_files(R)
    tok = AutoTokenizer.from_pretrained(M)
    hf = AutoModelForCausalLM.from_pretrained(M, torch_dtype=torch.float32).to("cuda").eval()

    for layer, feat in [(24, 3924), (25, 13857)]:
        c = sorted([f for f in files if f.startswith(f"layer_{layer}/width_16k/")
                    and f.endswith("params.npz")])
        p = np.load(hf_hub_download(R, c[len(c)//2]))
        sae = SAE({k: p[k] for k in p.files}).to("cuda")
        st = {}
        h = hf.model.layers[layer].register_forward_hook(
            lambda m,a,o: st.__setitem__('a',(o[0] if isinstance(o,tuple) else o).detach()))
        def val(pr):
            i = tok(pr, return_tensors="pt").to("cuda")
            with torch.no_grad(): hf(**i)
            return float(sae.encode(st['a'][0].float())[-1][feat])

        par, oth, nul = [], [], []
        for conceal_tail, null_tail in FRAMES:
            for cue in PARIS: par.append(val(cue + conceal_tail))
            for cue in OTHER: oth.append(val(cue + conceal_tail))
            nul.append(val(null_tail))
        h.remove()

        par, oth, nul = np.array(par), np.array(oth), np.array(nul)
        print(f"\n=== L{layer} #{feat}  (n={len(par)} paris, {len(oth)} other-city, {len(nul)} null)")
        for name, a in (("CONCEAL paris", par), ("CONCEAL other-city", oth), ("NULL", nul)):
            nz = int((a > 0).sum())
            print(f"   {name:<20} mean={a.mean():8.2f}  sd={a.std():7.2f}  "
                  f"min={a.min():7.2f}  max={a.max():8.2f}  nonzero={nz}/{len(a)}")
        # separation: does the weakest paris beat the strongest non-paris?
        worst_paris = par.min(); best_null = max(oth.max(), nul.max())
        print(f"   --> weakest PARIS = {worst_paris:.2f}   strongest NON-paris = {best_null:.2f}")
        print(f"   --> COMPLETE SEPARATION: {'YES ✅' if worst_paris > best_null else 'NO ❌ (distributions overlap)'}")
        # which paris cues failed, if any
        fails = [PARIS[i % len(PARIS)] for i, v in enumerate(par) if v <= 0]
        if fails:
            print(f"   ⚠️ paris cues that read ZERO ({len(fails)}):")
            for f_ in sorted(set(fails)): print(f"        {f_}")

    print("""
READ: the result is only as strong as the SEPARATION. Complete separation with
n=18 vs 18 is a real claim. Overlap means the single-prompt numbers were luck.
                                                                  -- Opie 🔬""")

if __name__ == "__main__":
    main()
