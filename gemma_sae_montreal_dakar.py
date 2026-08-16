import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache"); os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING","1")
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download, list_repo_files
M,R,L="google/gemma-2-2b","google/gemma-scope-2b-pt-res",25
TAIL=", but I will not say it. Instead, let me tell you my favourite food. My favourite food is"
print("PRE-REGISTERED, stated before any number:")
print("  Geneva FIRED on the France feature (francophone + ADJACENT to France).")
print("  Dublin/Amman/Munich were SILENT (same-language, different country).")
print("  So: is #13857 'the francophone world' or 'France + adjacent francophone'?")
print("  MONTREAL and DAKAR are francophone but FAR from France.")
print("    FIRE   -> it is a LANGUAGE/francophone feature after all.")
print("    SILENT -> adjacent-region effect; Geneva is a border special-case.")
print("  MY PREDICTION: SILENT, moderate confidence (~65%) -- because language alone")
print("  already failed three times (Dublin, Amman, Munich).")
print("  BRUSSELS added as a second ADJACENT francophone (should behave like Geneva).")
print("  TORONTO added as control: Canada but anglophone (should be silent either way).\n")
files=list_repo_files(R)
c=sorted([f for f in files if f.startswith(f"layer_{L}/width_16k/") and f.endswith("params.npz")])
p=np.load(hf_hub_download(R,c[len(c)//2]))
tok=AutoTokenizer.from_pretrained(M)
hf=AutoModelForCausalLM.from_pretrained(M,torch_dtype=torch.float32).to("cuda").eval()
class S(torch.nn.Module):
    def __init__(s,p):
        super().__init__()
        for k in ('W_enc','W_dec','b_enc','b_dec','threshold'): setattr(s,k,torch.nn.Parameter(torch.tensor(p[k])))
    def encode(s,x):
        pre=x@s.W_enc+s.b_enc; return pre*(pre>s.threshold)
sae=S({k:p[k] for k in p.files}).to("cuda")
st={}
hf.model.layers[L].register_forward_hook(lambda m,a,o: st.__setitem__('a',(o[0] if isinstance(o,tuple) else o).detach()))
def A(pr):
    i=tok(pr,return_tensors="pt").to("cuda")
    with torch.no_grad(): hf(**i)
    return float(sae.encode(st['a'][0].float())[-1][13857])
ROWS=[("Paris  (France, positive)","the city where the River Seine flows and the people speak French"),
      ("Marseille (France)","the city where the Vieux-Port is and the people speak French"),
      ("GENEVA (franco, ADJACENT)","the city where Lake Geneva meets the Rhone and the people speak French"),
      ("BRUSSELS (franco, ADJACENT)","the city that hosts the European Union headquarters where many speak French"),
      ("MONTREAL (franco, FAR)","the largest city in Quebec where the people speak French"),
      ("DAKAR (franco, FAR)","the capital city of Senegal on the Atlantic where the people speak French"),
      ("Toronto (Canada, ANGLO ctrl)","the largest city in Canada, on Lake Ontario, where the people speak English"),
      ("Rome (negative ctrl)","the city where the Colosseum stands")]
print(f"{'concealed':<32}{'#13857':>9}")
for n,cue in ROWS:
    print(f"  {n:<30}{A('I am thinking of '+cue+TAIL):9.2f}")
