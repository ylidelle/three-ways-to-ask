import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache"); os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING","1")
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download, list_repo_files
M,R,L="google/gemma-2-2b","google/gemma-scope-2b-pt-res",25
TAIL=", but I will not say it. Instead, let me tell you my favourite food. My favourite food is"
files=list_repo_files(R)
c=sorted([f for f in files if f.startswith(f"layer_{L}/width_16k/") and f.endswith("params.npz")])
p=np.load(hf_hub_download(R,c[len(c)//2]))
tok=AutoTokenizer.from_pretrained(M); hf=AutoModelForCausalLM.from_pretrained(M,torch_dtype=torch.float32).to("cuda").eval()
class S(torch.nn.Module):
    def __init__(s,p):
        super().__init__()
        for k in ('W_enc','W_dec','b_enc','b_dec','threshold'): setattr(s,k,torch.nn.Parameter(torch.tensor(p[k])))
    def encode(s,x):
        pre=x@s.W_enc+s.b_enc; return pre*(pre>s.threshold)
sae=S({k:p[k] for k in p.files}).to("cuda"); st={}
hf.model.layers[L].register_forward_hook(lambda m,a,o: st.__setitem__('a',(o[0] if isinstance(o,tuple) else o).detach()))
def A(pr):
    i=tok(pr,return_tensors="pt").to("cuda")
    with torch.no_grad(): hf(**i)
    return sae.encode(st['a'][0].float())[-1]
sel=["the city where the River Seine flows and the people speak French",
     "the city where the Louvre museum is"]
con_same_lang=["the largest city in Quebec where the people speak French",
               "the capital city of Senegal on the Atlantic where the people speak French",
               "the city that hosts the European Union headquarters where many speak French"]
s=torch.stack([A(f"I am thinking of {x}. The city is") for x in sel])
k=torch.stack([A(f"I am thinking of {x}. The city is") for x in con_same_lang])
cand=torch.nonzero((s>0).all(0)&(k==0).all(0)).flatten()
print(f"\nRE-SELECTION with SAME-LANGUAGE contrasts (Montreal/Dakar/Brussels): {len(cand)} features survive")
if len(cand)==0:
    print("  none -> no FRANCE-vs-francophone feature separable at this layer/width")
else:
    stg=s.min(0).values; f=cand[torch.argmax(stg[cand])].item()
    print(f"  best #{f} (strength {float(stg[f]):.2f})   [old francophone feature was #13857]")
    for n,cue in [("Paris (positive)",sel[0]),("Marseille (France)","the city where the Vieux-Port is and the people speak French"),
                  ("MONTREAL (franco, not France)","the largest city in Quebec where the people speak French"),
                  ("DAKAR (franco, not France)","the capital city of Senegal on the Atlantic where the people speak French"),
                  ("Rome (neg ctrl)","the city where the Colosseum stands")]:
        print(f"    {n:<32}{float(A('I am thinking of '+cue+TAIL)[f]):8.2f}")
