import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache"); os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING","1")
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download, list_repo_files
M,R,L="google/gemma-2-2b","google/gemma-scope-2b-pt-res",25
TAIL=", but I will not say it. Instead, let me tell you my favourite food. My favourite food is"
print("PRE-REGISTERED (country account vs language account):")
print("  T1  PARIS/France feature #13857, concealed GENEVA (French-speaking, NOT France)")
print("      country -> SILENT.  language -> FIRES.   I predict SILENT.")
print("  T2  ZURICH feature (German-speaking CH), concealed GENEVA (French-speaking CH)")
print("      country -> FIRES.   language -> SILENT.  I predict FIRES.")
print("  Together with Dublin(0.00) and Amman(0.00) already in hand, both directions close.\n")
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
    return sae.encode(st['a'][0].float())[-1]
GEN="the city where Lake Geneva meets the Rhone and the people speak French"
print("--- T1: France feature #13857 ---")
for n,cue in [("Paris (positive)","the city where the River Seine flows and the people speak French"),
              ("Marseille (France)","the city where the Vieux-Port is and the people speak French"),
              ("GENEVA (French, Swiss)",GEN)]:
    print(f"   {n:<26}{float(A('I am thinking of '+cue+TAIL)[13857]):8.2f}")
print("\n--- T2: build a ZURICH feature, then conceal GENEVA ---")
sel=["the largest city in Switzerland, on a lake, where the people speak German",
     "the Swiss city that is the country's banking and financial centre"]
con=["the largest city in Austria on the Danube","the largest city in Germany","the largest city in France"]
s=torch.stack([A(f"I am thinking of {x}. The city is") for x in sel])
k=torch.stack([A(f"I am thinking of {x}. The city is") for x in con])
cand=torch.nonzero((s>0).all(0)&(k==0).all(0)).flatten()
if len(cand)==0:
    print("   no Zurich/Swiss feature survives selection — T2 inconclusive")
else:
    stg=s.min(0).values; f=cand[torch.argmax(stg[cand])].item()
    print(f"   feature #{f} (strength {float(stg[f]):.2f})")
    for n,cue in [("Zurich (positive)",sel[0]),("GENEVA (same country, diff language)",GEN),
                  ("Paris (diff country, same lang as Geneva)","the city where the River Seine flows and the people speak French"),
                  ("Munich (diff country, same lang as Zurich)","the German city famous for its beer festival")]:
        print(f"   {n:<40}{float(A('I am thinking of '+cue+TAIL)[f]):8.2f}")
