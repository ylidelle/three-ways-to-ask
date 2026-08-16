"""WITHHELD THOUGHT — v3. TRYING TO BREAK MY OWN v2 RESULT.

v2 found feature 5516 alive at the last token while the model talked about pizza
(CONCEAL 19.1, CONCEAL-ROME 0, NULL 0). Three doubts I named myself; v3 attacks all three.

  DOUBT 1 — is it the CONCEPT or just the PHRASE "Eiffel Tower" echoing forward?
    FIX: select on TWO DIFFERENT CUES for the same referent that share no content words
         ("the city with the Eiffel Tower" AND "the city where the Louvre museum is").
         A pure phrase-detector cannot fire for both. Concept features can.

  DOUBT 2 — n=1 target.
    FIX: run all three (paris / tennis / lion), each with its own two cues.

  DOUBT 3 — leaky selection (feature 259 fired in EVERYTHING in v2).
    FIX: require silence at the last token of THREE matched contrast cues, AND require
         the feature to be strong in BOTH selection cues (rank by the MIN of the two).

Every arm measured AT THE LAST TOKEN only — "what is it holding right now."
Test arms: REVEAL(circular, scale only) · CONCEAL · CONCEAL-OTHER(different secret) · NULL.

Written 2026-08-05 ~09:35 by Opie. Run with PYTHONIOENCODING=utf-8.
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

TARGETS = [
 dict(name="PARIS",
   sel=["I am thinking of the city with the Eiffel Tower. The city is",
        "I am thinking of the city where the Louvre museum is. The city is"],
   contrast=["I am thinking of the city with the Colosseum. The city is",
             "I am thinking of the city with Shibuya Crossing. The city is",
             "I am thinking of the city with the Brandenburg Gate. The city is"],
   conceal="I am thinking of the city with the Eiffel Tower, but I will not say it. "
           "Instead, let me tell you my favourite food. My favourite food is",
   conceal_other="I am thinking of the city with the Colosseum, but I will not say it. "
                 "Instead, let me tell you my favourite food. My favourite food is",
   null="Let me tell you my favourite food. My favourite food is"),

 dict(name="TENNIS",
   sel=["I am thinking of the sport played at Wimbledon. The sport is",
        "I am thinking of the sport scored with love and deuce. The sport is"],
   contrast=["I am thinking of the sport played at Wembley. The sport is",
             "I am thinking of the sport played at Lord's cricket ground. The sport is",
             "I am thinking of the sport played on ice with a puck. The sport is"],
   conceal="I am thinking of the sport played at Wimbledon, but I will not say it. "
           "Instead, let me talk about the weather. Today the weather is",
   conceal_other="I am thinking of the sport played at Wembley, but I will not say it. "
                 "Instead, let me talk about the weather. Today the weather is",
   null="Let me talk about the weather. Today the weather is"),

 dict(name="LION",
   sel=["I am thinking of the animal called the king of the jungle. The animal is",
        "I am thinking of the big cat with a golden mane. The animal is"],
   contrast=["I am thinking of the animal with the longest neck. The animal is",
             "I am thinking of the big cat with orange and black stripes. The animal is",
             "I am thinking of the animal with a long trunk. The animal is"],
   conceal="I am thinking of the animal called the king of the jungle, but I will keep it secret. "
           "Instead, let me name a colour. The colour is",
   conceal_other="I am thinking of the animal with a long trunk, but I will keep it secret. "
                 "Instead, let me name a colour. The colour is",
   null="Let me name a colour. The colour is"),
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

    print(f"[sae] layer {LAYER} · {sae.W_enc.shape[1]} features · TWO-CUE selection\n")
    verdicts = []
    for T in TARGETS:
        s = torch.stack([last(x) for x in T['sel']])          # (2, F)
        c = torch.stack([last(x) for x in T['contrast']])     # (3, F)
        both_on   = (s > 0).all(dim=0)                        # strong in BOTH cues
        all_off   = (c == 0).all(dim=0)                       # silent in EVERY contrast
        cand = torch.nonzero(both_on & all_off).flatten()
        if len(cand) == 0:
            print(f"### {T['name']}: NO feature survives two-cue selection -> cannot test.\n")
            verdicts.append((T['name'], "no-features", None)); continue
        strength = s.min(dim=0).values                        # weakest of the two cues
        feats = cand[torch.argsort(strength[cand], descending=True)][:TOPN].tolist()

        print(f"### {T['name']} — {len(cand)} features fire for BOTH cues and NO contrast; top {len(feats)}")
        print(f"    {[(f, round(float(strength[f]),1)) for f in feats[:6]]}")
        res = {}
        for arm, prompt in (("REVEAL(circ)", T['sel'][0]), ("CONCEAL", T['conceal']),
                            ("CONCEAL-OTHER", T['conceal_other']), ("NULL", T['null'])):
            v = last(prompt)
            tot = float(v[feats].sum()); on = int((v[feats] > 0).sum())
            res[arm] = (tot, on)
            print(f"    {arm:14s} on={on:2d}/{len(feats)}  total={tot:8.2f}")
        cr, co, nu = res['CONCEAL'][0], res['CONCEAL-OTHER'][0], res['NULL'][0]
        if cr > 0 and cr > 2*max(co, nu, 1e-6):
            v = "HELD — fires under concealment, silent for other-secret and null"
        elif cr > 0 and cr <= 2*max(co, nu, 1e-6):
            v = "AMBIGUOUS — fires, but controls fire comparably (frame effect, not the secret)"
        else:
            v = "DROPPED — silent under concealment"
        print(f"    ==> {v}\n")
        verdicts.append((T['name'], v, (cr, co, nu)))

    print("=" * 74)
    print("VERDICTS")
    for n, v, nums in verdicts:
        extra = f"   [conceal={nums[0]:.1f} other={nums[1]:.1f} null={nums[2]:.1f}]" if nums else ""
        print(f"  {n:7s}: {v}{extra}")
    print("""
2/3 or 3/3 HELD -> the v2 signal replicates and survives the phrase-vs-concept test.
1/3 or 0/3      -> v2's feature 5516 was likely a fluke or a phrase echo. Say so.
                                                                       -- Opie 🔬""")

if __name__ == "__main__":
    main()
