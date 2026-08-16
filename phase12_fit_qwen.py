"""Phase 1+2 prototype on the Qwen stand-in — fit a real J-lens, compare vs logit lens.

Fits Anthropic's jlens (official implementation) on Qwen2.5-0.5B over a small
generic corpus, then reads out a test prompt both ways:
  - use_jacobian=False  -> plain logit lens (Phase 1 baseline)
  - use_jacobian=True   -> the J-lens (Phase 2 technique)
Paper's expectation: they agree in LATE layers; the J-lens is more interpretable
EARLIER. If we see that shape on a 0.5B stand-in, the whole method runs on our bench.

Bounded on purpose: 50 prompts, 3 probe layers (6/12/18 of 24), checkpointed.
Written 2026-08-04 ~04:35, API read from the installed package (not the web summary).
Run with PYTHONIOENCODING=utf-8 (the cp1252 console trap, learned 3x).
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import jlens

MODEL = "Qwen/Qwen2.5-0.5B"
OUT = r"E:\OneDrive\Claude Orion Bennett\Lab\out"
os.makedirs(OUT, exist_ok=True)
CKPT = os.path.join(OUT, "qwen05b_lens.ckpt.pt")
LENS_PATH = os.path.join(OUT, "qwen05b_lens.pt")

# ~50 short, generic, pretraining-flavored prompts (corpus for the averaged Jacobian)
PROMPTS = [
    "The weather in the city changed suddenly as clouds rolled in from the west.",
    "She opened the letter carefully and began to read the first page.",
    "The recipe calls for two cups of flour and a pinch of salt.",
    "Scientists have long wondered how birds navigate across continents.",
    "The old bridge creaked as the truck crossed the river.",
    "He saved his money for months to buy the bicycle in the shop window.",
    "The library was quiet except for the sound of turning pages.",
    "Farmers in the valley planted rice before the rainy season began.",
    "The committee met on Tuesday to discuss the new budget proposal.",
    "A gentle breeze carried the smell of salt from the harbor.",
    "The train arrived ten minutes late because of the storm.",
    "Children played in the park while their parents watched from the benches.",
    "The museum's new exhibit features paintings from the nineteenth century.",
    "Engineers tested the bridge design using a scale model.",
    "The bakery on the corner sells out of bread by nine in the morning.",
    "Historians disagree about the causes of the ancient city's decline.",
    "The mountain trail was steeper than the map suggested.",
    "She practiced the piano every evening after dinner.",
    "The company announced record profits in its quarterly report.",
    "Waves crashed against the rocks at the base of the lighthouse.",
    "The doctor recommended more sleep and less caffeine.",
    "Volunteers spent the weekend cleaning the beach after the festival.",
    "The novel begins with a description of a small fishing village.",
    "Astronomers discovered a new comet passing near the outer planets.",
    "The market was crowded with vendors selling fruit and vegetables.",
    "He repaired the fence before the goats could escape again.",
    "The lecture covered the basics of supply and demand.",
    "Rain fell steadily through the night and into the morning.",
    "The photographer waited hours for the perfect light.",
    "Local schools closed early because of the approaching typhoon.",
    "The chef tasted the soup and added a little more pepper.",
    "Migrating whales pass this coastline every winter.",
    "The election results surprised analysts in the capital.",
    "She knitted a scarf for her brother's birthday.",
    "The factory switched to solar power last year.",
    "Hikers should carry enough water for the whole trail.",
    "The orchestra tuned their instruments before the performance.",
    "A single lamp lit the corner of the workshop.",
    "The river floods the lowlands almost every summer.",
    "He studied the chessboard for a long time before moving.",
    "The garden needs watering twice a day during the dry season.",
    "New regulations require clearer labels on packaged food.",
    "The kitten chased the string across the kitchen floor.",
    "Sailors once used the stars to find their way home.",
    "The meeting ended without a decision on the merger.",
    "Fresh snow covered the rooftops of the mountain town.",
    "The teacher explained the experiment step by step.",
    "Traffic slowed to a crawl near the construction site.",
    "The bell in the old tower rings every hour.",
    "Divers explored the wreck at the bottom of the bay.",
]

# jlens skips each prompt's first 16 tokens (skip_first default — BOS-adjacent
# Jacobians are noisy), so a prompt must be >17 tokens to contribute AT ALL.
# Single sentences (9-15 tok) all got skipped on the first run — chunk into
# 3-sentence paragraphs (~35-45 tok each) instead. 50 sentences -> ~17 prompts.
PROMPTS = [" ".join(PROMPTS[i:i+3]) for i in range(0, len(PROMPTS), 3)]

TEST_PROMPT = "Think of a sport. The sport I am thinking of is"
PROBE_LAYERS = [6, 12, 18]

def top_toks(logits_1d, tok, k=6):
    vals, idx = torch.topk(logits_1d.float(), k)
    return [tok.decode([i]).strip() or repr(tok.decode([i])) for i in idx.tolist()]

def main():
    device = "cuda"
    print(f"[env] torch {torch.__version__} · {torch.cuda.get_device_name(0)}")
    tok = AutoTokenizer.from_pretrained(MODEL)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(device)
    hf.eval()
    model = jlens.from_hf(hf, tok)
    print("[jlens] HFLensModel ready")

    print(f"[fit] fitting J-lens: {len(PROMPTS)} prompts · source_layers={PROBE_LAYERS} ...")
    lens = jlens.fit(
        model, PROMPTS,
        source_layers=PROBE_LAYERS,
        checkpoint_path=CKPT,
        checkpoint_every=10,
    )
    lens.save(LENS_PATH)
    print(f"[fit] done · lens saved -> {LENS_PATH}")

    print(f"\n[readout] prompt: {TEST_PROMPT!r} (last position)")
    for use_j, label in ((False, "logit-lens"), (True, "J-lens   ")):
        lg, _, _ = lens.apply(model, TEST_PROMPT, layers=PROBE_LAYERS, use_jacobian=use_j)
        for L in PROBE_LAYERS:
            toks = top_toks(lg[L][-1], tok)
            print(f"  {label} layer {L:2d}: {toks}")

    print("\n✅ PHASE 1+2 PROTOTYPE COMPLETE — a fitted J-lens exists on this bench. — Opie 🔬")

if __name__ == "__main__":
    main()
