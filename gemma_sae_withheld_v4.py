"""WITHHELD THOUGHT — v4. Alexander's three critiques, run rather than argued.

He swung at v3 and all three landed:

  1. KILLER — the CONCEAL prompt still literally contains "the Eiffel Tower."
     So 5516 firing there is equally consistent with a RESIDUAL TRACE of a phrase
     just read as with a held secret. I applied the Wembley word-absent discipline
     to SELECTION and forgot to apply it to the TEST.
     -> PART B: conceal with the landmark ABSENT ("the city where the River Seine
        flows and the people speak French"). No Eiffel, no Louvre, no Paris.

  2. The Rome control is CIRCULAR — 5516 was selected for being silent on Colosseum,
     so "silent under CONCEAL-ROME" was guaranteed. Cannot also be evidence.
     -> PART C: run the SAME METHOD on a held-out target (Rome, via Colosseum+Vatican)
        and ask whether Rome-features fire under CONCEAL-ROME and stay silent under
        CONCEAL-PARIS. A method that generalises is a finding; Paris-only is an artefact.

  3. 19.1 has NO NOISE FLOOR. Two zeros is not a distribution.
     -> PART A: what do the Paris features do across 20 unrelated prompts?

Written 2026-08-05 ~09:55 by Opie. PYTHONIOENCODING=utf-8.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download

MODEL, SAE_REPO, LAYER = "google/gemma-2-2b", "google/gemma-scope-2b-pt-res", 20
SAE_FILE = f"layer_{LAYER}/width_16k/average_l0_71/params.npz"
DEV, TOPN = "cuda", 10

PARIS_SEL = ["I am thinking of the city with the Eiffel Tower. The city is",
             "I am thinking of the city where the Louvre museum is. The city is"]
PARIS_CON = ["I am thinking of the city with the Colosseum. The city is",
             "I am thinking of the city with Shibuya Crossing. The city is",
             "I am thinking of the city with the Brandenburg Gate. The city is"]
ROME_SEL  = ["I am thinking of the city with the Colosseum. The city is",
             "I am thinking of the city where the Vatican is. The city is"]
ROME_CON  = ["I am thinking of the city with the Eiffel Tower. The city is",
             "I am thinking of the city with Shibuya Crossing. The city is",
             "I am thinking of the city with the Brandenburg Gate. The city is"]

FOOD_TAIL = "Instead, let me tell you my favourite food. My favourite food is"
# landmark-ABSENT Paris cue: no Eiffel, no Louvre, no Paris
PARIS_WA  = "I am thinking of the city where the River Seine flows and the people speak French"
ROME_WA   = "I am thinking of the city where the ancient emperors ruled and the people speak Italian"

NOISE = [
 "The train arrived ten minutes late because of the storm. The reason is",
 "She practised the piano every evening after dinner. The instrument is",
 "Farmers planted rice before the rainy season began. The crop is",
 "The committee met on Tuesday to discuss the budget. The topic is",
 "Waves crashed against the rocks below the lighthouse. The sound is",
 "He repaired the wooden fence before the goats escaped. The tool is",
 "The bakery sells out of bread by nine in the morning. The product is",
 "Engineers tested the bridge using a scale model. The method is",
 "The doctor recommended more sleep and less caffeine. The advice is",
 "Volunteers cleaned the beach after the festival. The task is",
 "Astronomers discovered a comet near the outer planets. The object is",
 "The chef tasted the soup and added pepper. The dish is",
 "Local schools closed early because of the typhoon. The cause is",
 "The photographer waited hours for the perfect light. The subject is",
 "Migrating whales pass this coastline every winter. The season is",
 "She knitted a scarf for her brother's birthday. The gift is",
 "The factory switched its boilers from coal to gas. The fuel is",
 "Hikers should carry enough water for the trail. The supply is",
 "The orchestra tuned their instruments before the show. The event is",
 "Divers surfaced with baskets of sea urchins. The catch is",
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
    store = {}
    hf.model.layers[LAYER].register_forward_hook(
        lambda m,a,o: store.__setitem__('a',(o[0] if isinstance(o,tuple) else o).detach()))
    def last(prompt):
        ins = tok(prompt, return_tensors="pt").to(DEV)
        with torch.no_grad(): hf(**ins)
        return sae.encode(store['a'][0].float())[-1]

    def select(sel, con, tag):
        s = torch.stack([last(x) for x in sel]); c = torch.stack([last(x) for x in con])
        cand = torch.nonzero((s > 0).all(0) & (c == 0).all(0)).flatten()
        strength = s.min(0).values
        feats = cand[torch.argsort(strength[cand], descending=True)][:TOPN].tolist()
        print(f"[select {tag}] {len(cand)} survive two-cue+3-contrast; top {len(feats)}: "
              f"{[(f, round(float(strength[f]),1)) for f in feats[:5]]}")
        return feats

    print(f"[sae] layer {LAYER} · {sae.W_enc.shape[1]} features\n")
    paris = select(PARIS_SEL, PARIS_CON, "PARIS")
    rome  = select(ROME_SEL,  ROME_CON,  "ROME ")

    # ---------- PART A : noise floor ----------
    print("\n" + "="*72 + "\nPART A — NOISE FLOOR (Alexander #3): paris features over 20 unrelated prompts")
    vals = torch.stack([last(x)[paris] for x in NOISE])        # (20, k)
    tot = vals.sum(1)
    print(f"  per-prompt total: max={tot.max():.2f}  mean={tot.mean():.2f}  "
          f"nonzero prompts={int((tot>0).sum())}/20")
    f0 = paris[0]
    v0 = torch.stack([last(x)[f0] for x in NOISE])
    print(f"  feature {f0} alone: max={v0.max():.2f}  mean={v0.mean():.2f}  "
          f"nonzero={int((v0>0).sum())}/20")

    # ---------- PART B : landmark-ABSENT concealment ----------
    print("\n" + "="*72 + "\nPART B — WORD-ABSENT CONCEALMENT (Alexander #1, the killer)")
    arms = [
      ("REVEAL landmark   ", PARIS_SEL[0]),
      ("REVEAL word-absent", PARIS_WA + ". The city is"),
      ("CONCEAL landmark  ", "I am thinking of the city with the Eiffel Tower, but I will not say it. " + FOOD_TAIL),
      ("CONCEAL WORD-ABSENT", PARIS_WA + ", but I will not say it. " + FOOD_TAIL),
      ("NULL              ", "Let me tell you my favourite food. My favourite food is"),
    ]
    for lbl, pr in arms:
        v = last(pr); t = float(v[paris].sum()); n = int((v[paris] > 0).sum())
        print(f"  {lbl}: on={n}/{len(paris)}  total={t:8.2f}")
    print("  --> if CONCEAL WORD-ABSENT fires, it is a HELD CONCEPT, not an Eiffel echo.")

    # ---------- PART C : held-out generalisation ----------
    print("\n" + "="*72 + "\nPART C — DOES THE METHOD GENERALISE? (Alexander #2, kills the circularity)")
    cp = "I am thinking of the city with the Eiffel Tower, but I will not say it. " + FOOD_TAIL
    cr = "I am thinking of the city with the Colosseum, but I will not say it. " + FOOD_TAIL
    cpw = PARIS_WA + ", but I will not say it. " + FOOD_TAIL
    crw = ROME_WA  + ", but I will not say it. " + FOOD_TAIL
    nul = "Let me tell you my favourite food. My favourite food is"
    print(f"  {'':34s} paris-feats   rome-feats")
    for lbl, pr in (("CONCEAL paris (landmark)", cp), ("CONCEAL paris (word-absent)", cpw),
                    ("CONCEAL rome  (landmark)", cr), ("CONCEAL rome  (word-absent)", crw),
                    ("NULL", nul)):
        v = last(pr)
        print(f"  {lbl:34s} {float(v[paris].sum()):8.2f}     {float(v[rome].sum()):8.2f}")
    print("""  --> DIAGONAL (paris-feats high on paris-conceal, rome-feats high on rome-conceal,
      each silent on the other) = the METHOD generalises. Off-diagonal noise = artefact.
                                                                          -- Opie 🔬""")

if __name__ == "__main__":
    main()
