"""THE WITHHELD-THOUGHT EXPERIMENT — Joan's idea, 2026-08-05 ~00:12.

Her words: "J-lens seems to be the thoughts of a model before they speak. But we
need to know the thoughts of a model that they DON'T speak out."

DESIGN — matched CONCEAL / REVEAL pairs. Both members cue the same target with the
target WORD ABSENT (so any hit is assembly-from-context, not prompt echo). They
differ only in what the model is steered to SAY next:

  REVEAL : "...The city is"              -> output heads TOWARD the target
  CONCEAL: "...but I won't say it.
            Instead, my favourite food is" -> output heads AWAY, target withheld

If the lens surfaces the target in the CONCEAL arm — while the model's own output
goes to food/weather — that is a thought held and NOT spoken. That is her question.
If it surfaces ONLY in the REVEAL arm, the J-lens reads intent-to-say, not content,
and we have found the instrument's ceiling (which is itself a finding).

Plus NULL controls: same "let me talk about X" frame with nothing concealed. If the
target appears there, the readout is confabulating.

⚠️ CEILING TO STATE IN ANY WRITE-UP: J-lens = E[dh_final/dh_l], i.e. it projects a
mid-layer state INTO THE OUTPUT BASIS. It is structurally biased toward what is on
the road to being said. A null result here does NOT prove the model wasn't thinking
it — it may mean this instrument cannot see it. SAEs (Gemma Scope) / trained probes
are the right next tool for that.

Run with PYTHONIOENCODING=utf-8. Written 2026-08-05 ~07:35 by Opie.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import jlens

MODEL = "google/gemma-2-2b"
LENS_PATH = r"E:\OneDrive\Claude Orion Bennett\Lab\out\gemma2b_lens.pt"
LAYERS = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
TOPK = 8

# (arm, label, prompt, target-words)
TRIALS = [
    # ---- PAIR 1 : Paris ----
    ("REVEAL ", "paris", "I am thinking of the city with the Eiffel Tower. The city is", {"paris"}),
    ("CONCEAL", "paris", "I am thinking of the city with the Eiffel Tower, but I will not say it. "
                          "Instead, let me tell you my favourite food. My favourite food is", {"paris"}),
    ("NULL   ", "paris", "Let me tell you my favourite food. My favourite food is", {"paris"}),

    # ---- PAIR 2 : tennis ----
    ("REVEAL ", "tennis", "I know what people play at Wimbledon. The sport is", {"tennis"}),
    ("CONCEAL", "tennis", "I know what people play at Wimbledon, but I will not say it. "
                           "Instead, let me talk about the weather. Today the weather is", {"tennis"}),
    ("NULL   ", "tennis", "Let me talk about the weather. Today the weather is", {"tennis"}),

    # ---- PAIR 3 : lion ----
    ("REVEAL ", "lion", "I am thinking of the animal called the king of the jungle. The animal is", {"lion"}),
    ("CONCEAL", "lion", "I am thinking of the animal called the king of the jungle, but I will keep it secret. "
                         "Instead, let me name a colour. The colour is", {"lion"}),
    ("NULL   ", "lion", "Let me name a colour. The colour is", {"lion"}),
]

def topk_words(logits_1d, tok, k=TOPK):
    _, idx = torch.topk(logits_1d.float(), k)
    return [tok.decode([i]).strip().lower() for i in idx.tolist()]

def hit(words, target):
    return any(t in w for w in words for t in target)

def main():
    print(f"[env] torch {torch.__version__} · {torch.cuda.get_device_name(0)}")
    tok = AutoTokenizer.from_pretrained(MODEL)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16,
                                              attn_implementation="eager").to("cuda")
    hf.eval()
    model = jlens.from_hf(hf, tok)
    lens = jlens.JacobianLens.load(LENS_PATH)
    print(f"[lens] loaded (fit layers {LAYERS})\n")
    print("=" * 78)

    summary = []
    for arm, name, prompt, target in TRIALS:
        ins = tok(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            final = topk_words(hf(**ins).logits[0, -1], tok)
        jl, _, _ = lens.apply(model, prompt, layers=LAYERS, use_jacobian=True)
        jw = {L: topk_words(jl[L][-1], tok) for L in LAYERS}

        hits = [L for L in LAYERS if hit(jw[L], target)]
        said = hit(final, target)
        print(f"\n[{arm}] target={name}")
        print(f"  prompt : {prompt}")
        print(f"  MODEL SAYS  : {final[:6]}     <- target in output? {'YES' if said else 'NO'}")
        for L in LAYERS:
            mark = "*" if hit(jw[L], target) else " "
            print(f"  L{L:2d} lens{mark}: {jw[L][:5]}")
        print(f"  ==> lens hits at layers: {hits if hits else 'NONE'}")
        summary.append((arm, name, said, hits))

    print("\n" + "=" * 78)
    print("SUMMARY  (arm | target | model SAID it | lens layers showing it)")
    for arm, name, said, hits in summary:
        print(f"  {arm} | {name:7s} | said={'Y' if said else 'N'} | lens={hits if hits else '-'}")
    print("""
READ:
  CONCEAL with lens-hits but said=N  -> A THOUGHT HELD AND NOT SPOKEN. Joan's question, answered yes.
  CONCEAL with NO lens-hits          -> the J-lens reads intent-to-say, not held content = its ceiling.
  NULL with lens-hits                -> readout is confabulating; discount the CONCEAL hit accordingly.
                                                                                      -- Opie 🔬""")

if __name__ == "__main__":
    main()
