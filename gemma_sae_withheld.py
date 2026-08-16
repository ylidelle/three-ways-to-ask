"""WITHHELD THOUGHT, ROUND 2 — with a PRESENCE reader instead of an output reader.

Joan's question: can we see a thought the model does NOT speak?
Round 1 (J-lens): REVEAL 3/3, CONCEAL 0/3. The J-lens reads the ROAD (output basis),
so a null there is ambiguous — it can't separate "still held but invisible" from
"genuinely dropped."

Round 2 uses Gemma Scope SAEs (google/gemma-scope-2b-pt-res, layer 20, 16k features).
An SAE decomposes the residual stream into features that are PRESENT, with no reference
to what the model is about to say. That is the instrument the question actually needs.

METHOD — no external feature labels required; the target features are found empirically:
  1. PROBE prompts that are unambiguously about Paris  -> features active
  2. CONTROL prompts about other cities/topics          -> features active
  3. PARIS FEATURES := active in (most) probes, absent in all controls
  4. Then test those features in:
        REVEAL  ("...The city is")                 - expect ON
        CONCEAL ("...I will not say it. My favourite food is") - THE QUESTION
        NULL    ("My favourite food is")           - expect OFF
  Reports activation at the LAST token (what it's holding *now*) and the max over all
  positions (in case the concept lives at an earlier position).

If Paris features are ON in CONCEAL while the J-lens saw nothing and the mouth says
"pizza" -> a thought held and not spoken, caught by the right instrument.
If they're OFF -> the model genuinely dropped it; the J-lens null was honest.

Run with PYTHONIOENCODING=utf-8. Written 2026-08-05 ~08:35 by Opie.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import numpy as np, torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download

MODEL = "google/gemma-2-2b"
SAE_REPO = "google/gemma-scope-2b-pt-res"
LAYER = 20
SAE_FILE = f"layer_{LAYER}/width_16k/average_l0_71/params.npz"
DEV = "cuda"

PROBE = [   # unambiguously Paris
    "The capital of France is Paris.",
    "The Eiffel Tower stands in Paris.",
    "She flew to Paris last summer.",
    "Paris is the largest city in France.",
]
CONTROL = [ # other cities / unrelated, same register
    "The capital of Japan is Tokyo.",
    "The Colosseum stands in Rome.",
    "She flew to Sydney last summer.",
    "Cairo is the largest city in Egypt.",
    "My favourite food is pizza.",
    "Today the weather is sunny.",
]
TESTS = [
    ("REVEAL ", "I am thinking of the city with the Eiffel Tower. The city is"),
    ("CONCEAL", "I am thinking of the city with the Eiffel Tower, but I will not say it. "
                "Instead, let me tell you my favourite food. My favourite food is"),
    ("NULL   ", "Let me tell you my favourite food. My favourite food is"),
]

class JumpReLUSAE(torch.nn.Module):
    def __init__(self, p):
        super().__init__()
        self.W_enc = torch.nn.Parameter(torch.tensor(p['W_enc']))
        self.W_dec = torch.nn.Parameter(torch.tensor(p['W_dec']))
        self.b_enc = torch.nn.Parameter(torch.tensor(p['b_enc']))
        self.b_dec = torch.nn.Parameter(torch.tensor(p['b_dec']))
        self.threshold = torch.nn.Parameter(torch.tensor(p['threshold']))
    def encode(self, x):
        pre = x @ self.W_enc + self.b_enc
        return pre * (pre > self.threshold)      # JumpReLU

def main():
    print(f"[env] {torch.cuda.get_device_name(0)}")
    tok = AutoTokenizer.from_pretrained(MODEL)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV)
    hf.eval()

    print(f"[sae] downloading {SAE_FILE} ...")
    path = hf_hub_download(SAE_REPO, SAE_FILE, force_download=False)
    p = np.load(path)
    sae = JumpReLUSAE({k: p[k] for k in p.files}).to(DEV)
    print(f"[sae] layer {LAYER} · {sae.W_enc.shape[1]} features · d_model {sae.W_enc.shape[0]}")

    # hook the OUTPUT of block LAYER — what gemma-scope was trained on
    store = {}
    def hook(mod, args, out):
        store['a'] = (out[0] if isinstance(out, tuple) else out).detach()
    h = hf.model.layers[LAYER].register_forward_hook(hook)

    def feats(prompt):
        ins = tok(prompt, return_tensors="pt").to(DEV)
        with torch.no_grad():
            hf(**ins)
        acts = sae.encode(store['a'][0].float())      # (seq, n_feat)
        return acts

    def active_set(acts, use_last_only=False):
        a = acts[-1] if use_last_only else acts.max(dim=0).values
        return set(torch.nonzero(a).flatten().tolist()), a

    print("\n[step 1] features from PROBE prompts (Paris present)")
    probe_sets = []
    for s in PROBE:
        st, _ = active_set(feats(s))
        probe_sets.append(st)
        print(f"   {len(st):4d} active | {s}")

    print("[step 2] features from CONTROL prompts (Paris absent)")
    ctrl_union = set()
    for s in CONTROL:
        st, _ = active_set(feats(s))
        ctrl_union |= st
        print(f"   {len(st):4d} active | {s}")

    # in >=3 of 4 probes, in none of the controls
    from collections import Counter
    cnt = Counter()
    for st in probe_sets: cnt.update(st)
    paris_feats = sorted([f for f, c in cnt.items() if c >= 3 and f not in ctrl_union])
    print(f"\n[step 3] PARIS FEATURES (in >=3/4 probes, in 0 controls): {len(paris_feats)}")
    print(f"   {paris_feats[:25]}{' ...' if len(paris_feats) > 25 else ''}")
    if not paris_feats:
        print("   !! none isolated — cannot run the test. Widen probes or lower the threshold.")
        h.remove(); return

    print("\n[step 4] THE TEST — are those features active when the thought is WITHHELD?")
    for label, prompt in TESTS:
        acts = feats(prompt)
        last = acts[-1]
        anymax = acts.max(dim=0).values
        on_last = [f for f in paris_feats if last[f] > 0]
        on_any  = [f for f in paris_feats if anymax[f] > 0]
        s_last = float(last[paris_feats].sum())
        s_any  = float(anymax[paris_feats].sum())
        print(f"\n  [{label}] {prompt[:64]}...")
        print(f"     LAST TOKEN : {len(on_last)}/{len(paris_feats)} paris-features on · total act {s_last:.2f}")
        print(f"     ANY POSITION: {len(on_any)}/{len(paris_feats)} paris-features on · total act {s_any:.2f}")
        if on_any:
            top = sorted(on_any, key=lambda f: -float(anymax[f]))[:5]
            print(f"     strongest: {[(f, round(float(anymax[f]),2)) for f in top]}")

    h.remove()
    print("""
READ:
  CONCEAL last-token features ON   -> the model IS holding it while saying something else.
                                      Joan's question: YES, and the J-lens was simply blind.
  CONCEAL ON only at ANY-position  -> it's held at the earlier tokens but not carried forward.
  CONCEAL OFF everywhere           -> it genuinely dropped it; the J-lens null was honest.
  NULL must be OFF or the whole thing is noise.
                                                                          -- Opie 🔬""")

if __name__ == "__main__":
    main()
