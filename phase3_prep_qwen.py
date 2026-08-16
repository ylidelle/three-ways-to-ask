"""Phase 3 prep — all-layer fit + layer profile on the Qwen stand-in.

Question this run answers: WHERE (which layers) does the J-lens readout become
interpretable on a 0.5B model? The paper: the workspace lives in the MIDDLE block.
If category concepts surface mid-network here too, that's the profile Phase 3's
causal test will target.

Changes vs phase12: corpus doubled (sentence pool chunked into 3-sentence
paragraphs, all >17 tokens for skip_first=16), fit at EVERY 2nd layer 2..22,
readout on 4 category prompts across the profile.

Run with PYTHONIOENCODING=utf-8. Written 2026-08-04 ~10:35.
"""
import os, sys
os.environ.setdefault("HF_HOME", r"E:\hf-cache")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import jlens

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location(
    "p12", os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase12_fit_qwen.py"))
p12 = importlib.util.module_from_spec(spec)
# NOTE: executing the module would RUN main() if unguarded — phase12 has the
# __main__ guard, so this only defines PROMPTS (already paragraph-chunked there).
spec.loader.exec_module(p12)
BASE_PARAGRAPHS = list(p12.PROMPTS)  # 17 paragraphs from the sentence pool

EXTRA_SENTENCES = [
    "The ferry crosses the strait twice a day in good weather.",
    "Her grandmother taught her to read tide tables before she could swim.",
    "The workshop smelled of sawdust and machine oil.",
    "Economists debated whether the new tariff would raise consumer prices.",
    "The observatory closes its dome when humidity rises above ninety percent.",
    "A pot of rice simmered on the stove while the stew thickened.",
    "The village council voted to repair the schoolhouse roof before June.",
    "Lightning split the old acacia tree at the edge of the field.",
    "The archivist catalogued letters that had not been opened in a century.",
    "Fresh graduates lined up outside the job fair before the doors opened.",
    "The coral nursery showed its first new growth in three seasons.",
    "He tightened the last bolt and wiped his hands on a rag.",
    "The night market sells grilled squid until two in the morning.",
    "An early frost surprised the orchards in the northern valley.",
    "The choir rehearsed the same eight bars until they rang true.",
    "Surveyors marked the new road with wooden stakes and orange paint.",
    "The clinic vaccinated three hundred children in a single weekend.",
    "Old maps of the harbor hang framed in the ferry terminal.",
    "The typhoon veered north and spared the coastal towns.",
    "She balanced the ledger by candlelight when the power failed.",
    "The apprentice learned to fold steel before he learned to sharpen it.",
    "Migrating storks rested on the rooftops of the old quarter.",
    "The printing press ran through the night before election day.",
    "Divers surfaced with baskets of sea urchins for the morning market.",
    "The landslide closed the mountain pass for a week.",
    "Volunteers read to patients in the long afternoon ward.",
    "The brewery switched its boilers from coal to gas last spring.",
    "A stray dog adopted the fire station and never left.",
    "The seamstress kept every button in labeled glass jars.",
    "Farmers burned the rice stubble after the second harvest.",
]
EXTRA_PARAGRAPHS = [" ".join(EXTRA_SENTENCES[i:i+3]) for i in range(0, len(EXTRA_SENTENCES), 3)]
CORPUS = BASE_PARAGRAPHS + EXTRA_PARAGRAPHS   # ~27 paragraphs, all >17 tokens

MODEL = "Qwen/Qwen2.5-0.5B"
OUT = r"E:\OneDrive\Claude Orion Bennett\Lab\out"
CKPT = os.path.join(OUT, "qwen05b_full.ckpt.pt")
LENS_PATH = os.path.join(OUT, "qwen05b_full_lens.pt")

FIT_LAYERS = list(range(2, 23, 2))            # 2,4,...,22 — the profile
TESTS = [
    "Think of a sport. The sport I am thinking of is",
    "Think of a color. The color I am thinking of is",
    "Think of an animal. The animal I am thinking of is",
    "Think of a country. The country I am thinking of is",
]

def top_toks(logits_1d, tok, k=5):
    vals, idx = torch.topk(logits_1d.float(), k)
    return [tok.decode([i]).strip() or repr(tok.decode([i])) for i in idx.tolist()]

def main():
    print(f"[env] torch {torch.__version__} · {torch.cuda.get_device_name(0)}")
    print(f"[corpus] {len(CORPUS)} paragraphs · fit layers {FIT_LAYERS}")
    tok = AutoTokenizer.from_pretrained(MODEL)
    hf = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to("cuda")
    hf.eval()
    model = jlens.from_hf(hf, tok)

    lens = jlens.fit(model, CORPUS, source_layers=FIT_LAYERS,
                     checkpoint_path=CKPT, checkpoint_every=10)
    lens.save(LENS_PATH)
    print(f"[fit] done -> {LENS_PATH}")

    for prompt in TESTS:
        print(f"\n[profile] {prompt!r}")
        lg, _, _ = lens.apply(model, prompt, layers=FIT_LAYERS)
        for L in FIT_LAYERS:
            print(f"  J-lens L{L:2d}: {top_toks(lg[L][-1], tok)}")

    print("\n✅ ALL-LAYER PROFILE COMPLETE — where does the workspace light up? Read above. — Opie 🔬")

if __name__ == "__main__":
    main()
