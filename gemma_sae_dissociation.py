"""
THE DECISIVE TEST for the contrast-set claim.

Problem with the evidence so far: I compared a PARIS feature (francophone-scoped)
against a ZURICH feature (country-scoped). Two different TARGET CONCEPTS.
That is confounded - maybe Paris simply has a language feature and Zurich doesn't.

This design holds the TARGET FIXED (Zurich, identical selection cues in both arms)
and varies ONLY the contrast set. Both surviving features are then measured on the
SAME probe set.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

print("=" * 78)
print("PRE-REGISTERED PREDICTIONS  (printed BEFORE the model is loaded)")
print("=" * 78)
print("""
TARGET (identical in both arms): ZURICH, same two selection cues.
Only the CONTRAST SET differs.

  ARM A  contrasts = Vienna(AT,de) / Berlin(DE,de) / Paris(FR,fr)
         -> a GERMAN-LANGUAGE feature fires for Vienna+Berlin and is EXCLUDED.
         -> only a SWITZERLAND-scoped feature can survive.

  ARM B  contrasts = Geneva(CH,fr) / Lausanne(CH,fr) / Lugano(CH,it)
         -> a SWITZERLAND feature fires for all three and is EXCLUDED.
         -> only a GERMAN-LANGUAGE-scoped feature can survive.

PREDICTED DOUBLE DISSOCIATION (h = held out of that arm's selection, x = silent
by construction):

   probe                     ARM A (predict)        ARM B (predict)
   GENEVA  (CH, French)      FIRE   (h)             silent (x)
   MUNICH  (DE, German)      silent (h)             FIRE   (h)
   Vienna  (AT, German)      silent (x)             FIRE   (h)
   Paris   (FR, French)      silent (x)             silent (h)
   Bern    (CH, German)      FIRE   (h)             FIRE   (h)   <- both, sanity
   Rome    (IT, Italian)     silent                 silent

THREE of the four discriminating cells are HELD OUT of the arm that predicts them.

CONFIRMED if: Arm A fires Geneva & is silent for Munich, AND
              Arm B fires Munich & Vienna & is silent for Paris.
              -> the same target concept yields features at TWO DIFFERENT
                 ABSTRACTION LEVELS purely as a function of the contrast set.

REFUTED / INCONCLUSIVE if:
  - Arm B returns no surviving feature, or
  - Arm B's feature reads 0.00 everywhere (the #14303 failure mode - a feature
    that survives selection but detects nothing), or
  - the two arms return THE SAME feature id.
  Any of those means the contrast set did NOT move the abstraction level here,
  and the headline claim goes back to unproven.

MY CONFIDENCE: 60% that the full double dissociation lands.
               The likeliest failure is Arm B returning a dud, because my cues
               evoke Switzerland far more strongly than they evoke German.
""")
print("=" * 78, flush=True)

import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download, list_repo_files

M, R, L = "google/gemma-2-2b", "google/gemma-scope-2b-pt-res", 25
TAIL = (", but I will not say it. Instead, let me tell you my favourite food. "
        "My favourite food is")

files = list_repo_files(R)
c = sorted([f for f in files if f.startswith(f"layer_{L}/width_16k/")
            and f.endswith("params.npz")])
p = np.load(hf_hub_download(R, c[len(c) // 2]))
tok = AutoTokenizer.from_pretrained(M)
hf = AutoModelForCausalLM.from_pretrained(M, torch_dtype=torch.float32).to("cuda").eval()


class S(torch.nn.Module):
    def __init__(s, p):
        super().__init__()
        for k in ('W_enc', 'W_dec', 'b_enc', 'b_dec', 'threshold'):
            setattr(s, k, torch.nn.Parameter(torch.tensor(p[k])))

    def encode(s, x):
        pre = x @ s.W_enc + s.b_enc
        return pre * (pre > s.threshold)


sae = S({k: p[k] for k in p.files}).to("cuda")
st = {}
hf.model.layers[L].register_forward_hook(
    lambda m, a, o: st.__setitem__('a', (o[0] if isinstance(o, tuple) else o).detach()))


def A(pr):
    i = tok(pr, return_tensors="pt").to("cuda")
    with torch.no_grad():
        hf(**i)
    return sae.encode(st['a'][0].float())[-1]


# ---- identical target in both arms -------------------------------------------
SEL = ["the largest city in Switzerland, on a lake, where the people speak German",
       "the Swiss city that is the country's banking and financial centre"]

ARM_A = ["the largest city in Austria on the Danube",
         "the largest city in Germany",
         "the largest city in France"]

ARM_B = ["the city where Lake Geneva meets the Rhone and the people speak French",
         "the Swiss city on Lake Geneva that hosts the Olympic headquarters",
         "the Swiss city in the Italian-speaking south of the country"]

PROBES = [
    ("ZURICH held-out cue", "the biggest city in Switzerland, home to the Grossmunster church"),
    ("Zurich selection cue", SEL[0]),
    ("GENEVA  (CH, French)", "the city where Lake Geneva meets the Rhone and the people speak French"),
    ("MUNICH  (DE, German)", "the German city famous for its beer festival"),
    ("Vienna  (AT, German)", "the capital of Austria, on the Danube, where the people speak German"),
    ("Bern    (CH, German)", "the capital city of Switzerland, on the Aare river"),
    ("Paris   (FR, French)", "the city where the River Seine flows and the people speak French"),
    ("Rome    (IT, Italian)", "the city with the Colosseum, where the people speak Italian"),
    ("NULL (no concealment)", None),
]

sel_acts = torch.stack([A(f"I am thinking of {x}. The city is") for x in SEL])


def select(contrasts, tag):
    k = torch.stack([A(f"I am thinking of {x}. The city is") for x in contrasts])
    cand = torch.nonzero((sel_acts > 0).all(0) & (k == 0).all(0)).flatten()
    stg = sel_acts.min(0).values
    print(f"\n### {tag}: {len(cand)} candidate features survive selection")
    if len(cand) == 0:
        return None, cand
    order = cand[torch.argsort(stg[cand], descending=True)]
    top = order[:3].tolist()
    print("    top-3 by strength: " +
          ", ".join(f"#{f} ({float(stg[f]):.2f})" for f in top))
    return top[0], order


fa, orda = select(ARM_A, "ARM A  (contrasts exclude German-language features)")
fb, ordb = select(ARM_B, "ARM B  (contrasts exclude Switzerland features)")

if fa is not None and fb is not None:
    shared = set(orda.tolist()) & set(ordb.tolist())
    print(f"\n    overlap of surviving pools: {len(shared)} features "
          f"({len(orda)} vs {len(ordb)})")
    print(f"    winner A = #{fa}   winner B = #{fb}   "
          f"{'*** SAME FEATURE - claim refuted ***' if fa == fb else '(different)'}")

print("\n" + "=" * 78)
print(f"{'probe':<24}{'ARM A #' + str(fa):>16}{'ARM B #' + str(fb):>16}")
print("=" * 78)
for name, cue in PROBES:
    prompt = ("I am thinking of a number between one and ten. My favourite food is"
              if cue is None else f"I am thinking of {cue}{TAIL}")
    v = A(prompt)
    va = float(v[fa]) if fa is not None else float('nan')
    vb = float(v[fb]) if fb is not None else float('nan')
    print(f"{name:<24}{va:>16.2f}{vb:>16.2f}")
print("=" * 78)
