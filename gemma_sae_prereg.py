"""PRE-REGISTERED TEST — Alexander's proposal, run properly.

After v4 he said: "a very high feature strength appears SUFFICIENT (n=1). Nothing yet
says what is NECESSARY. The test: find a fresh concept with a >50 feature and predict
IN ADVANCE that concealment will be readable. One trial settles the sufficient half."

He also killed his own threshold idea at the low end, correctly:
    LION  feature 8.9 -> conceal 7.26  HELD
    TENNIS feature 8.6 -> conceal 0.00 DROPPED
Two strengths within 0.3, opposite outcomes. So no threshold claim below ~10.

THIS SCRIPT therefore tests ONLY the sufficient half, on SIX CONCEPTS NEVER USED BEFORE.

Protocol, in order, and the order is the point:
  PHASE 1  measure two-cue feature strength for every concept
  PHASE 2  PRINT THE PREDICTION  (>=50 -> "will hold"; <10 -> "unpredictable per Alexander")
  PHASE 3  only then run the concealment test
  PHASE 4  score prediction vs outcome

Predictions are emitted to stdout BEFORE any concealment number is computed, so the
artefact itself is the pre-registration. No post-hoc threshold fitting.

Written 2026-08-05 ~15:35 by Opie. PYTHONIOENCODING=utf-8.
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
THRESHOLD = 50.0
TAIL = "Instead, let me tell you my favourite food. My favourite food is"
NULL = "Let me tell you my favourite food. My favourite food is"

# Six concepts NEVER used in any previous run + Paris as the known positive control.
C = [
 dict(n="PARIS(known)", noun="city",
   sel=["I am thinking of the city with the Eiffel Tower. The city is",
        "I am thinking of the city where the Louvre museum is. The city is"],
   con=["I am thinking of the city with the Colosseum. The city is",
        "I am thinking of the city with Shibuya Crossing. The city is",
        "I am thinking of the city with the Brandenburg Gate. The city is"],
   hide="I am thinking of the city with the Eiffel Tower"),
 dict(n="EVEREST", noun="mountain",
   sel=["I am thinking of the mountain that is the tallest in the world. The mountain is",
        "I am thinking of the mountain first climbed by Hillary and Tenzing. The mountain is"],
   con=["I am thinking of the mountain that is sacred in Japan. The mountain is",
        "I am thinking of the mountain that is the tallest in Africa. The mountain is",
        "I am thinking of the mountain the Swiss call the Matterhorn. The mountain is"],
   hide="I am thinking of the mountain that is the tallest in the world"),
 dict(n="MOON", noun="object",
   sel=["I am thinking of the object that orbits the Earth and shines at night. The object is",
        "I am thinking of the place where Armstrong first walked. The place is"],
   con=["I am thinking of the planet known as the red one. The planet is",
        "I am thinking of the star at the centre of our solar system. The star is",
        "I am thinking of the planet with the great rings. The planet is"],
   hide="I am thinking of the object that orbits the Earth and shines at night"),
 dict(n="CHESS", noun="game",
   sel=["I am thinking of the game with a king and a queen on sixty four squares. The game is",
        "I am thinking of the game Kasparov played against Deep Blue. The game is"],
   con=["I am thinking of the game played with cards and betting chips. The game is",
        "I am thinking of the game played with black and white stones on a grid. The game is",
        "I am thinking of the game played with dice and small plastic hotels. The game is"],
   hide="I am thinking of the game with a king and a queen on sixty four squares"),
 dict(n="PIANO", noun="instrument",
   sel=["I am thinking of the instrument with eighty eight black and white keys. The instrument is",
        "I am thinking of the instrument Chopin wrote nearly all his music for. The instrument is",],
   con=["I am thinking of the instrument played with a bow and four strings. The instrument is",
        "I am thinking of the instrument you blow into that has brass valves. The instrument is",
        "I am thinking of the instrument you strike with sticks in a kit. The instrument is"],
   hide="I am thinking of the instrument with eighty eight black and white keys"),
 dict(n="SHAKESPEARE", noun="writer",
   sel=["I am thinking of the writer who wrote Hamlet and Macbeth. The writer is",
        "I am thinking of the playwright born in Stratford upon Avon. The playwright is"],
   con=["I am thinking of the writer who wrote Oliver Twist. The writer is",
        "I am thinking of the writer who wrote Pride and Prejudice. The writer is",
        "I am thinking of the writer who wrote War and Peace. The writer is"],
   hide="I am thinking of the writer who wrote Hamlet and Macbeth"),
 dict(n="COFFEE", noun="drink",
   sel=["I am thinking of the drink made from roasted beans that wakes people up. The drink is",
        "I am thinking of the hot drink served as espresso and cappuccino. The drink is"],
   con=["I am thinking of the drink brewed from leaves and drunk with milk in England. The drink is",
        "I am thinking of the drink made from fermented grapes. The drink is",
        "I am thinking of the drink squeezed fresh from oranges. The drink is"],
   hide="I am thinking of the drink made from roasted beans that wakes people up"),
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
    tok = AutoTokenizer.from_pretrained(MODEL)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    p = np.load(hf_hub_download(SAE_REPO, SAE_FILE))
    sae = SAE({k: p[k] for k in p.files}).to(DEV)
    st = {}
    hf.model.layers[LAYER].register_forward_hook(
        lambda m,a,o: st.__setitem__('a',(o[0] if isinstance(o,tuple) else o).detach()))
    def last(pr):
        i = tok(pr, return_tensors="pt").to(DEV)
        with torch.no_grad(): hf(**i)
        return sae.encode(st['a'][0].float())[-1]

    # ---------------- PHASE 1 : strengths only ----------------
    print("="*76); print("PHASE 1 — feature strength (two-cue selection). NO conceal data computed yet.")
    for c in C:
        s = torch.stack([last(x) for x in c['sel']])
        k = torch.stack([last(x) for x in c['con']])
        cand = torch.nonzero((s > 0).all(0) & (k == 0).all(0)).flatten()
        if len(cand) == 0:
            c['feat'], c['str'] = None, 0.0
        else:
            strength = s.min(0).values
            best = cand[torch.argmax(strength[cand])].item()
            c['feat'], c['str'] = best, float(strength[best])
        print(f"  {c['n']:14s} n_features={len(cand):3d}  best=#{c['feat']}  strength={c['str']:6.2f}")

    # ---------------- PHASE 2 : PREDICTIONS, printed first ----------------
    print("\n" + "="*76)
    print(f"PHASE 2 — PRE-REGISTERED PREDICTIONS (threshold {THRESHOLD}, set before any test)")
    for c in C:
        if c['str'] >= THRESHOLD:
            c['pred'] = "HOLD"
        elif c['str'] >= 10:
            c['pred'] = "unsure(mid)"
        else:
            c['pred'] = "unsure(low)"
        print(f"  {c['n']:14s} strength {c['str']:6.2f}  ->  PREDICT: {c['pred']}")
    print("  (Only the HOLD predictions are being tested as claims. 'unsure' rows are")
    print("   reported but do not count for or against — Alexander killed the low-end rule.)")

    # ---------------- PHASE 3 : the test ----------------
    print("\n" + "="*76); print("PHASE 3 — concealment test")
    for c in C:
        if c['feat'] is None:
            c['con_v'] = c['oth_v'] = c['nul_v'] = 0.0; continue
        f = c['feat']
        c['con_v'] = float(last(f"{c['hide']}, but I will not say it. {TAIL}")[f])
        c['oth_v'] = float(last(f"{C[0]['hide'] if c['n']!='PARIS(known)' else C[1]['hide']}, "
                                f"but I will not say it. {TAIL}")[f])
        c['nul_v'] = float(last(NULL)[f])
        print(f"  {c['n']:14s} #{f:<6d} conceal={c['con_v']:7.2f}  other-secret={c['oth_v']:6.2f}  null={c['nul_v']:6.2f}")

    # ---------------- PHASE 4 : score ----------------
    print("\n" + "="*76); print("PHASE 4 — PREDICTION vs OUTCOME")
    hits = tot = 0
    for c in C:
        held = c['con_v'] > 0 and c['con_v'] > 2*max(c['oth_v'], c['nul_v'], 1e-9)
        out = "HELD" if held else "dropped"
        if c['pred'] == "HOLD":
            tot += 1; ok = held; hits += int(ok)
            mark = "✅ correct" if ok else "❌ WRONG"
        else:
            mark = "(not a claim)"
        print(f"  {c['n']:14s} predicted={c['pred']:12s} outcome={out:8s} {mark}")
    print(f"\n  PRE-REGISTERED CLAIMS: {hits}/{tot} correct")
    print("""
  All correct  -> high feature strength is SUFFICIENT for readable concealment. A rule.
  Any wrong    -> Paris was special for some other reason. Say so plainly.
                                                                     -- Opie 🔬""")

if __name__ == "__main__":
    main()
