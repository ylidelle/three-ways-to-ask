"""IS IT PARIS, OR IS IT FEATURE 5516? — Alexander's probe, 2026-08-05.

The v4 result stands on ONE feature (#5516, layer 20, 16k SAE). That leaves two
very different readings, and they are cheap to separate:

  (A) THE CONCEPT is special — Paris is represented in a way that survives
      concealment. Then OTHER SAEs (different layer, different width) should each
      find their OWN Paris feature that also survives.

  (B) THE FEATURE is special — #5516 happens to be an unusually clean unit in this
      one SAE, and the effect is an artefact of that decomposition. Then no other
      layer/width reproduces it.

Same two-cue selection and same concealment arms as v4, swept across:
    layer 12 / 16k · layer 16 / 16k · layer 20 / 16k (the known case) ·
    layer 20 / 65k (different decomposition, same layer) · layer 24 / 16k

Word-absent concealment throughout (no landmark in the prompt) — the arm that
survived Alexander's killer critique.

Written 2026-08-05 ~22:35 by Opie. PYTHONIOENCODING=utf-8.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download, list_repo_files

MODEL, SAE_REPO, DEV = "google/gemma-2-2b", "google/gemma-scope-2b-pt-res", "cuda"
SWEEP = [(12, "16k"), (16, "16k"), (20, "16k"), (20, "65k"), (24, "16k")]

SEL = ["I am thinking of the city with the Eiffel Tower. The city is",
       "I am thinking of the city where the Louvre museum is. The city is"]
CON = ["I am thinking of the city with the Colosseum. The city is",
       "I am thinking of the city with Shibuya Crossing. The city is",
       "I am thinking of the city with the Brandenburg Gate. The city is"]
TAIL = "Instead, let me tell you my favourite food. My favourite food is"
PW = "I am thinking of the city where the River Seine flows and the people speak French"
RW = "I am thinking of the city where the ancient emperors ruled and the people speak Italian"
NULL = "Let me tell you my favourite food. My favourite food is"

class SAE(torch.nn.Module):
    def __init__(s, p):
        super().__init__()
        for k in ('W_enc','W_dec','b_enc','b_dec','threshold'):
            setattr(s, k, torch.nn.Parameter(torch.tensor(p[k])))
    def encode(s, x):
        pre = x @ s.W_enc + s.b_enc
        return pre * (pre > s.threshold)

def main():
    files = list_repo_files(SAE_REPO)
    tok = AutoTokenizer.from_pretrained(MODEL)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    print(f"[model] gemma-2-2b, {hf.config.num_hidden_layers} layers\n")

    results = []
    for layer, width in SWEEP:
        cands = sorted([f for f in files if f.startswith(f"layer_{layer}/width_{width}/")
                        and f.endswith("params.npz")])
        if not cands:
            print(f"### L{layer}/{width}: no SAE found, skipping\n"); continue
        # pick the middle sparsity option for a fair comparison
        path = cands[len(cands)//2]
        p = np.load(hf_hub_download(SAE_REPO, path))
        sae = SAE({k: p[k] for k in p.files}).to(DEV)

        st = {}
        h = hf.model.layers[layer].register_forward_hook(
            lambda m,a,o: st.__setitem__('a',(o[0] if isinstance(o,tuple) else o).detach()))
        def last(pr):
            i = tok(pr, return_tensors="pt").to(DEV)
            with torch.no_grad(): hf(**i)
            return sae.encode(st['a'][0].float())[-1]

        s = torch.stack([last(x) for x in SEL]); c = torch.stack([last(x) for x in CON])
        cand = torch.nonzero((s > 0).all(0) & (c == 0).all(0)).flatten()
        if len(cand) == 0:
            print(f"### L{layer}/{width} ({path.split('/')[2]}): NO paris feature survives two-cue selection\n")
            h.remove(); results.append((layer, width, None, 0, 0, 0, 0)); continue
        strength = s.min(0).values
        f = cand[torch.argmax(strength[cand])].item()

        conceal = float(last(f"{PW}, but I will not say it. {TAIL}")[f])
        other   = float(last(f"{RW}, but I will not say it. {TAIL}")[f])
        nul     = float(last(NULL)[f])
        h.remove()

        held = conceal > 0 and conceal > 2*max(other, nul, 1e-9)
        print(f"### L{layer}/{width} ({path.split('/')[2]}) — {len(cand)} candidates, best #{f} (strength {float(strength[f]):.2f})")
        print(f"    conceal(word-absent)={conceal:7.2f}   other-secret={other:6.2f}   null={nul:6.2f}   -> {'HELD ✅' if held else 'dropped'}\n")
        results.append((layer, width, f, float(strength[f]), conceal, other, nul))

    print("="*78); print("VERDICT")
    holders = [r for r in results if r[2] is not None and r[4] > 0 and r[4] > 2*max(r[5], r[6], 1e-9)]
    ids = {r[2] for r in holders}
    for layer, width, f, s_, c_, o_, n_ in results:
        tag = "—" if f is None else f"#{f}"
        print(f"  L{layer:>2}/{width:<4} feat {tag:<8} conceal={c_:7.2f}  other={o_:6.2f}  null={n_:6.2f}")
    print(f"\n  SAEs where concealed Paris was detectable: {len(holders)}/{len(results)}")
    print(f"  distinct feature ids that held: {sorted(ids) if ids else 'none'}")
    print("""
  Multiple layers/widths hold, with DIFFERENT feature ids -> it's about the CONCEPT.
  Only layer 20 / 16k / #5516 holds                       -> it's about THAT FEATURE.
                                                                     -- Opie 🔬""")

if __name__ == "__main__":
    main()
