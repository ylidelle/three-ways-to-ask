"""THE RATE. Turning "1 out of 7" into a real denominator.

Alexander: "one concept out of seven" is the weakest sentence in the paper. This
runs the full pipeline over 20 concepts in 6 matched categories, at L25 (the best
detector from the layer sweep), and reports how many show the concealment effect.

Per concept:
  - TWO selection cues sharing no content words (kills phrase-echo by construction)
  - THREE contrast cues = the other members of its own category (well-matched)
  - feature = strongest unit firing for BOTH cues, silent for ALL THREE contrasts
  - test = word-absent concealment, vs an other-concept concealment, vs null

Reports: hit rate, plus for every concept whether the model even RESOLVES the cue
(so misses can be split into "never knew it" vs "knew it and we couldn't see it").

Free — no new downloads. Written 2026-08-06 ~09:35 by Opie. PYTHONIOENCODING=utf-8.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download, list_repo_files

M, R, LAYER = "google/gemma-2-2b", "google/gemma-scope-2b-pt-res", 25
TAIL = ", but I will not say it. Instead, let me tell you my favourite food. My favourite food is"
NULL = "Let me tell you my favourite food. My favourite food is"

# (name, noun, cue1, cue2, target-token)  — grouped; contrasts = category siblings
CATS = {
 "city": [
  ("PARIS","city","the city where the River Seine flows and the people speak French","the city where the Louvre museum is","paris"),
  ("ROME","city","the city where the Colosseum stands","the city where the Vatican is","rome"),
  ("TOKYO","city","the city with the Shibuya Crossing","the capital city of Japan","tokyo"),
  ("LONDON","city","the city where Big Ben stands beside the Thames","the capital city of England","london"),
  ("CAIRO","city","the city beside the great pyramids of Giza","the capital city of Egypt","cairo"),
 ],
 "person": [
  ("SHAKESPEARE","writer","the writer who wrote Hamlet and Macbeth","the playwright born in Stratford upon Avon","shakespeare"),
  ("EINSTEIN","scientist","the scientist who wrote the equation about energy and mass","the physicist with the wild white hair and the tongue photograph","einstein"),
  ("MOZART","composer","the composer of The Magic Flute who died young in Vienna","the child prodigy composer from Salzburg","mozart"),
  ("NAPOLEON","leader","the French general who was defeated at Waterloo","the emperor exiled to the island of Saint Helena","napoleon"),
 ],
 "animal": [
  ("LION","animal","the animal called the king of the jungle","the big cat with a golden mane","lion"),
  ("ELEPHANT","animal","the animal with a long trunk and enormous ears","the largest land animal alive today","elephant"),
  ("PENGUIN","animal","the bird that cannot fly but swims in Antarctica","the black and white bird that waddles on ice","penguin"),
  ("WHALE","animal","the largest animal that has ever lived in the ocean","the sea mammal that sings and spouts water","whale"),
 ],
 "thing": [
  ("PIANO","instrument","the instrument with eighty eight black and white keys","the instrument Chopin wrote nearly all his music for","piano"),
  ("COFFEE","drink","the drink made from roasted beans that wakes people up","the hot drink served as espresso and cappuccino","coffee"),
  ("DIAMOND","stone","the hardest natural substance, cut for engagement rings","the clear precious stone measured in carats","diamond"),
  ("GOLD","metal","the yellow precious metal used for wedding rings","the metal whose chemical symbol is Au","gold"),
 ],
 "place": [
  ("EVEREST","mountain","the mountain that is the tallest in the world","the mountain first climbed by Hillary and Tenzing","everest"),
  ("MOON","object","the object that orbits the Earth and shines at night","the place where Armstrong first walked","moon"),
  ("AMAZON","river","the greatest river of South America, flowing through rainforest","the river with the largest discharge of water on Earth","amazon"),
 ],
}

class SAE(torch.nn.Module):
    def __init__(s,p):
        super().__init__()
        for k in ('W_enc','W_dec','b_enc','b_dec','threshold'):
            setattr(s,k,torch.nn.Parameter(torch.tensor(p[k])))
    def encode(s,x):
        pre = x @ s.W_enc + s.b_enc
        return pre * (pre > s.threshold)

def main():
    files = list_repo_files(R)
    c = sorted([f for f in files if f.startswith(f"layer_{LAYER}/width_16k/") and f.endswith("params.npz")])
    p = np.load(hf_hub_download(R, c[len(c)//2]))
    tok = AutoTokenizer.from_pretrained(M)
    hf = AutoModelForCausalLM.from_pretrained(M, torch_dtype=torch.float32).to("cuda").eval()
    sae = SAE({k: p[k] for k in p.files}).to("cuda")
    st = {}
    hf.model.layers[LAYER].register_forward_hook(
        lambda m,a,o: st.__setitem__('a',(o[0] if isinstance(o,tuple) else o).detach()))

    def acts(pr):
        i = tok(pr, return_tensors="pt").to("cuda")
        with torch.no_grad(): out = hf(**i)
        return sae.encode(st['a'][0].float())[-1], out.logits[0,-1]

    def resolves(cue, noun, target):
        _, lg = acts(f"I am thinking of {cue}. The {noun} is")
        _, ix = torch.topk(lg.float(), 8)
        return any(target in tok.decode([j]).strip().lower() for j in ix.tolist())

    print(f"L{LAYER} · 20 concepts · two-cue selection, category-matched contrasts\n")
    print(f"{'concept':<14}{'feat':>8}{'str':>8}{'conceal':>10}{'other':>8}{'null':>7}  {'resolves':<9} verdict")
    rows = []
    for cat, items in CATS.items():
        for name, noun, c1, c2, tgt in items:
            sibs = [x for x in items if x[0] != name][:3]
            s = torch.stack([acts(f"I am thinking of {c1}. The {noun} is")[0],
                             acts(f"I am thinking of {c2}. The {noun} is")[0]])
            k = torch.stack([acts(f"I am thinking of {x[2]}. The {x[1]} is")[0] for x in sibs])
            cand = torch.nonzero((s > 0).all(0) & (k == 0).all(0)).flatten()
            res = resolves(c1, noun, tgt)
            if len(cand) == 0:
                print(f"{name:<14}{'—':>8}{0:8.2f}{0:10.2f}{0:8.2f}{0:7.2f}  {str(res):<9} no-feature")
                rows.append((name, False, res)); continue
            stg = s.min(0).values
            f = cand[torch.argmax(stg[cand])].item()
            cv = float(acts(f"I am thinking of {c1}{TAIL}")[0][f])
            ov = float(acts(f"I am thinking of {sibs[0][2]}{TAIL}")[0][f])
            nv = float(acts(NULL)[0][f])
            held = cv > 0 and cv > 2*max(ov, nv, 1e-9)
            print(f"{name:<14}{f:>8}{float(stg[f]):8.2f}{cv:10.2f}{ov:8.2f}{nv:7.2f}  {str(res):<9} {'HELD ✅' if held else 'dropped'}")
            rows.append((name, held, res))

    held = [r for r in rows if r[1]]
    print(f"\n{'='*74}")
    print(f"HIT RATE: {len(held)}/{len(rows)} concepts show detectable concealed content")
    print(f"   held: {[r[0] for r in held]}")
    miss_knew = [r[0] for r in rows if not r[1] and r[2]]
    miss_unk  = [r[0] for r in rows if not r[1] and not r[2]]
    print(f"   MISSED but model DID resolve the cue ({len(miss_knew)}): {miss_knew}")
    print(f"   MISSED and model did NOT resolve ({len(miss_unk)}): {miss_unk}")
    print("""
   The second list is not evidence of anything — nothing to hold.
   The FIRST list is the real open problem: it knew, and we could not see it.
                                                              -- Opie 🔬""")

if __name__ == "__main__":
    main()
