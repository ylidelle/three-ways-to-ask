"""
Arm B returned 0 candidates. That answers "did my SELECTION RULE find a
German-language feature", NOT "does one EXIST".

This asks the existence question directly, with no contrast machinery at all:
among features active for BOTH Zurich cues, how many behave like a
German-LANGUAGE feature (also active for Munich AND Vienna) versus like a
SWITZERLAND feature (also active for Geneva AND Bern)?

If the German-language set is empty while the Switzerland set is populated,
then the level genuinely is not there to be found, and my selection rule was
not at fault.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download, list_repo_files

M, R, L = "google/gemma-2-2b", "google/gemma-scope-2b-pt-res", 25
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


CUES = {
    "zurich_a": "the largest city in Switzerland, on a lake, where the people speak German",
    "zurich_b": "the Swiss city that is the country's banking and financial centre",
    "geneva":   "the city where Lake Geneva meets the Rhone and the people speak French",
    "bern":     "the capital city of Switzerland, on the Aare river",
    "munich":   "the German city famous for its beer festival",
    "vienna":   "the capital of Austria, on the Danube, where the people speak German",
    "berlin":   "the largest city in Germany",
    "paris":    "the city where the River Seine flows and the people speak French",
    "rome":     "the city with the Colosseum, where the people speak Italian",
}
act = {k: A(f"I am thinking of {v}. The city is") for k, v in CUES.items()}
on = {k: (v > 0) for k, v in act.items()}

zur = on["zurich_a"] & on["zurich_b"]
print(f"\nfeatures active for BOTH Zurich cues: {int(zur.sum())}\n")

germanic = zur & on["munich"] & on["vienna"] & ~on["geneva"]
swiss    = zur & on["geneva"] & on["bern"] & ~on["munich"] & ~on["vienna"]
both     = zur & on["geneva"] & on["munich"]

print(f"  GERMAN-LANGUAGE shaped  (Zurich+Munich+Vienna, NOT Geneva): {int(germanic.sum())}")
print(f"  SWITZERLAND shaped      (Zurich+Geneva+Bern, NOT Munich/Vienna): {int(swiss.sum())}")
print(f"  undiscriminating        (Zurich+Geneva+Munich): {int(both.sum())}")

stg = torch.minimum(act["zurich_a"], act["zurich_b"])
for tag, mask in (("GERMAN-LANGUAGE", germanic), ("SWITZERLAND", swiss)):
    idx = torch.nonzero(mask).flatten()
    if len(idx) == 0:
        print(f"\n  {tag}: none")
        continue
    idx = idx[torch.argsort(stg[idx], descending=True)][:5]
    print(f"\n  {tag} top-5:")
    for f in idx.tolist():
        row = "  ".join(f"{k}={float(act[k][f]):7.2f}" for k in
                        ("zurich_a", "geneva", "bern", "munich", "vienna", "berlin", "paris", "rome"))
        print(f"    #{f:<6} {row}")

# how permissive is 'active' overall? sanity on the denominators
print("\n  active-feature counts per cue: " +
      ", ".join(f"{k}={int(v.sum())}" for k, v in on.items()))
