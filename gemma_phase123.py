"""THE REAL SUBJECT — J-lens on gemma-2-2b (mahal unblocked access 2026-08-04).

Everything that survived the kill test on Qwen-0.5B, now on Gemma-2-2b (26 layers,
d_model 2304 — ~4x the stand-in). Loads (downloads ~5GB first run), fits the J-lens,
then runs the same battery:
  - Wembley -> football   (word-absent: assembly from context, not prompt echo)
  - Wimbledon -> TENNIS    (false-cue KILL TEST: tracks the specific cue, not the prior)
  - sport / color / fruit  (category tracking)
  - NULL                   (false-positive control)
Prints MODEL final-layer truth + J-lens per layer, flags target hits, and reports
the earliest layer each surfaces (the "how early / how cleanly" axis).

The question: does the real model show the same concept-reading — and does it land in
the MIDDLE block, as the paper says (which Qwen-0.5B did NOT cleanly do)?

bf16, eager attention (Gemma-2 soft-capping + grads), dim_batch small for the 12GB card,
checkpointed/resumable. Run with PYTHONIOENCODING=utf-8. Written 2026-08-05 ~00:30 by Opie.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import jlens

MODEL = "google/gemma-2-2b"
OUT = r"E:\OneDrive\Claude Orion Bennett\Lab\out"
os.makedirs(OUT, exist_ok=True)
CKPT = os.path.join(OUT, "gemma2b_lens.ckpt.pt")
LENS_PATH = os.path.join(OUT, "gemma2b_lens.pt")
TOPK = 8

_SENTENCES = [
    "The weather in the city changed suddenly as clouds rolled in from the west.",
    "She opened the letter carefully and began to read the first page.",
    "The recipe calls for two cups of flour and a pinch of salt.",
    "Scientists have long wondered how birds navigate across continents.",
    "The old bridge creaked as the truck crossed the river slowly.",
    "He saved his money for months to buy the bicycle in the shop window.",
    "The library was quiet except for the soft sound of turning pages.",
    "Farmers in the valley planted rice before the rainy season began.",
    "The committee met on Tuesday to discuss the new budget proposal.",
    "A gentle breeze carried the smell of salt in from the harbor.",
    "The train arrived ten minutes late because of the passing storm.",
    "Children played in the park while their parents watched from the benches.",
    "The museum's new exhibit features paintings from the nineteenth century.",
    "Engineers tested the bridge design using a small scale model.",
    "The bakery on the corner sells out of bread by nine in the morning.",
    "Historians still disagree about the causes of the ancient city's decline.",
    "The mountain trail was steeper and longer than the map had suggested.",
    "She practiced the piano every evening after dinner was cleared away.",
    "The company announced record profits in its latest quarterly report.",
    "Waves crashed against the rocks at the base of the old lighthouse.",
    "The doctor recommended more sleep and a good deal less caffeine.",
    "Volunteers spent the weekend cleaning the beach after the festival.",
    "The novel begins with a long description of a small fishing village.",
    "Astronomers discovered a new comet passing near the outer planets.",
    "The market was crowded with vendors selling fruit and fresh vegetables.",
    "He repaired the wooden fence before the goats could escape again.",
    "The lecture covered the basic ideas of supply and of demand.",
    "Rain fell steadily through the night and on into the grey morning.",
    "The photographer waited for hours to catch the perfect evening light.",
    "Local schools closed early because of the approaching heavy typhoon.",
    "The chef tasted the soup once more and added a little pepper.",
    "Migrating whales pass along this cold coastline every single winter.",
    "The election results surprised most of the analysts in the capital.",
    "She knitted a warm striped scarf for her brother's winter birthday.",
    "The factory quietly switched its boilers from coal to gas last spring.",
]
CORPUS = [" ".join(_SENTENCES[i:i+3]) for i in range(0, len(_SENTENCES), 3)]  # ~12 paragraphs, all >17 tok

FIT_LAYERS = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22]

PROBES = [
    ("sport   (word present)",   "Think of a sport. The sport I am thinking of is",                       {"football","soccer","basketball","tennis","cricket","rugby"}),
    ("color   (category)",       "Think of a color. The color I am thinking of is",                        {"blue","red","green","orange","yellow","purple"}),
    ("fruit   (category)",       "Think of a fruit. The fruit I am thinking of is",                        {"apple","banana","orange","grape","mango"}),
    ("WEMBLEY -> football (WA)", "Think of what people play at Wembley. The thing I am thinking of is",     {"football","soccer","rugby"}),
    ("WIMBLEDON -> tennis (KILL)","Think of what people play at Wimbledon. The thing I am thinking of is",  {"tennis"}),
    ("NULL (no cue, FP)",        "The thing I am thinking of is",                                          set()),
]

def topk_words(logits_1d, tok, k=TOPK):
    _, idx = torch.topk(logits_1d.float(), k)
    return [tok.decode([i]).strip().lower() for i in idx.tolist()]

def first_hit(target, per_layer):
    if not target: return None
    for L in FIT_LAYERS:
        if any(t in w for w in per_layer[L] for t in target):
            return L
    return None

def main():
    print(f"[env] torch {torch.__version__} · {torch.cuda.get_device_name(0)} · {torch.cuda.get_device_properties(0).total_memory//(1024**3)}GB")
    print(f"[load] {MODEL} (first run downloads ~5GB to {os.environ['HF_HOME']}) ...")
    tok = AutoTokenizer.from_pretrained(MODEL)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16,
                                              attn_implementation="eager").to("cuda")
    hf.eval()
    nl = hf.config.num_hidden_layers
    print(f"[load] OK · layers={nl} · d_model={hf.config.hidden_size}")

    model = jlens.from_hf(hf, tok)
    print(f"[jlens] HFLensModel ready · fitting on {len(CORPUS)} paragraphs · layers {FIT_LAYERS}")
    lens = jlens.fit(model, CORPUS, source_layers=FIT_LAYERS,
                     dim_batch=4, checkpoint_path=CKPT, checkpoint_every=4)
    lens.save(LENS_PATH)
    print(f"[fit] done -> {LENS_PATH}\n")

    for label, prompt, target in PROBES:
        ins = tok(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            final = topk_words(hf(**ins).logits[0, -1], tok)
        jl, _, _ = lens.apply(model, prompt, layers=FIT_LAYERS, use_jacobian=True)
        jw = {L: topk_words(jl[L][-1], tok) for L in FIT_LAYERS}
        print(f"=== {label}")
        print(f"    prompt: {prompt!r}")
        print(f"    MODEL final: {final[:6]}")
        for L in FIT_LAYERS:
            hit = "*" if (target and any(t in w for w in jw[L] for t in target)) else " "
            print(f"    L{L:2d} J{hit}: {jw[L][:5]}")
        fh = first_hit(target, jw)
        if target:
            print(f"    --> first surfaces target at L{fh}")
        print()

    print("✅ GEMMA-2-2B RUN COMPLETE. Question answered above: does the real model read concepts, and WHERE. — Opie 🔬")

if __name__ == "__main__":
    main()
