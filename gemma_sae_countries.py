import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache"); os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING","1")
import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download, list_repo_files
M,R,L="google/gemma-2-2b","google/gemma-scope-2b-pt-res",25
TAIL=", but I will not say it. Instead, let me tell you my favourite food. My favourite food is"
print("PRE-REGISTERED: after Paris's feature fired for Marseille/Lyon/Bordeaux, I predict")
print("ALL FIVE 'city' features are really COUNTRY features and will fire for same-country")
print("cities. If any stays silent for its own countrymen, that one IS city-specific.\n")
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
def A(pr,f):
    i=tok(pr,return_tensors="pt").to("cuda")
    with torch.no_grad(): hf(**i)
    return float(sae.encode(st['a'][0].float())[-1][f])
TESTS=[
 ("PARIS",13857,"the city where the River Seine flows and the people speak French",
   [("Marseille","the city where the Vieux-Port is and the people speak French"),
    ("Lyon","the city where the Rhone and Saone meet and the people speak French")],
   ("Rome (other country)","the city where the Colosseum stands")),
 ("ROME",5458,"the city where the Colosseum stands",
   [("Milan","the city with the Duomo and the fashion houses in Italy"),
    ("Naples","the Italian city beside Mount Vesuvius where pizza was invented"),
    ("Venice","the Italian city built on canals with gondolas")],
   ("Paris (other country)","the city where the Louvre museum is")),
 ("TOKYO",3953,"the city with the Shibuya Crossing",
   [("Osaka","the Japanese city famous for street food and Dotonbori"),
    ("Kyoto","the old Japanese capital with thousands of temples")],
   ("Seoul (other country)","the capital city of South Korea")),
 ("LONDON",11705,"the city where Big Ben stands beside the Thames",
   [("Manchester","the English city known for its two football clubs and rain"),
    ("Liverpool","the English port city where the Beatles formed")],
   ("Dublin (other country)","the capital city of Ireland")),
 ("CAIRO",999,"the city beside the great pyramids of Giza",
   [("Alexandria","the Egyptian port city founded by Alexander the Great"),
    ("Luxor","the Egyptian city with the Valley of the Kings")],
   ("Amman (other country)","the capital city of Jordan")),
]
print(f"{'feature':<10}{'own city':>10}   same-country cities                other-country")
for name,f,own,sames,other in TESTS:
    o=A(f"I am thinking of {own}{TAIL}",f)
    ss=[(n,A(f"I am thinking of {cue}{TAIL}",f)) for n,cue in sames]
    on,ocue=other; ov=A(f"I am thinking of {ocue}{TAIL}",f)
    txt="  ".join(f"{n} {v:.1f}" for n,v in ss)
    fired=sum(1 for _,v in ss if v>0)
    print(f"{name:<10}{o:10.2f}   {txt:<42} {on.split()[0]} {ov:.2f}   [{fired}/{len(ss)} same-country fired]")
