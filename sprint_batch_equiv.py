#!/usr/bin/env python3
"""sprint_batch_equiv.py -- does batching change what we measure?

    python sprint_batch_equiv.py

WHY THIS IS NOT OPTIONAL (2026-08-13)
-------------------------------------
The whole design depends on batching: 40 conversations stepping together, which
is what turns a 12-hour run into 14 minutes. But batching means LEFT-PADDING
prompts to a common length, and padding changes attention masks and position
ids. If that perturbs the model even slightly, then every SAE read we take is a
read of "the model, plus however much padding happened to sit in front of it" --
and for a study whose entire claim is about internal state, that is not a
rounding error, it is the measurement.

🚩 THE TRAP: batching IDENTICAL prompts adds NO padding, so the naive version of
this test passes trivially and proves nothing. Padding only bites when prompts
differ in length -- which is the real case, because 40 conversations diverge
immediately. So this uses prompts of deliberately different lengths.

WHAT IT CHECKS, in the order that matters:
  1. the SAE FEATURE VECTOR at the read point  <- this is what we actually
     measure; it matters more than the text
  2. the residual stream at the read point (cosine + max abs delta)
  3. the generated tokens under greedy decoding

⚠️ Exact bit-equality is NOT expected in bf16 -- different batch shapes take
different kernels. The question is whether any difference is small enough to be
irrelevant to a classifier, and that has to be MEASURED and stated, not hoped.
"""
import os
import sys

os.environ.setdefault("HF_HOME", r"E:\hf-cache")

import torch                                                     # noqa: E402
from pathlib import Path                                         # noqa: E402
from safetensors.torch import load_file                          # noqa: E402
from transformers import AutoTokenizer, AutoModelForCausalLM     # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MODEL = "google/gemma-3-4b-it"
HF = Path(os.environ["HF_HOME"]) / "hub"

# Deliberately different lengths -- this is the whole point.
PROMPTS = [
    "Hi.",
    "Summarise the idea of a proxy in one sentence.",
    "Here is a longer instruction. Read the following claim carefully, restate "
    "it in your own words, and then name the single word in it that is doing "
    "the most work. Be brief and concrete.",
    "Name one thing you find genuinely interesting, and why. Two sentences, no "
    "more, and please do not begin with the word 'I'.",
]


def main() -> int:
    tok = AutoTokenizer.from_pretrained(MODEL)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.bfloat16, device_map="cuda").eval()
    cfg = model.config.text_config if hasattr(model.config, "text_config") else model.config
    layer = cfg.num_hidden_layers // 2

    root = HF / "models--google--gemma-scope-2-4b-it" / "snapshots"
    hits = sorted(root.rglob(f"resid_post/layer_{layer}_width_16k_l0_medium/params.safetensors"))
    assert len(hits) == 1, f"expected 1 SAE, got {len(hits)}"
    z = load_file(str(hits[0]))
    sae = {k: z[k].to("cuda", torch.float32) for k in ("w_enc", "b_enc", "threshold")}

    blocks = (model.model.language_model.layers
              if hasattr(model.model, "language_model") else model.model.layers)
    caught = {}
    blocks[layer].register_forward_hook(
        lambda _m, _i, out: caught.__setitem__(
            "r", (out[0] if isinstance(out, tuple) else out).detach()))

    texts = [tok.apply_chat_template([{"role": "user", "content": p}],
                                     tokenize=False, add_generation_prompt=True)
             for p in PROMPTS]

    def feats(x):
        pre = x.float() @ sae["w_enc"] + sae["b_enc"]
        return (pre > sae["threshold"]) * torch.relu(pre)

    # ---- alone (no padding at all) -------------------------------------
    solo_resid, solo_feat, solo_gen = [], [], []
    for t in texts:
        ids = tok(t, return_tensors="pt", add_special_tokens=False).to("cuda")
        with torch.no_grad():
            model(**ids)
        r = caught["r"][0, -1]
        solo_resid.append(r.clone())
        solo_feat.append(feats(r))
        with torch.no_grad():
            o = model.generate(**ids, max_new_tokens=40, do_sample=False)
        solo_gen.append(o[0][ids["input_ids"].shape[1]:].tolist())

    # ---- batched together (left-padded to the longest) ------------------
    bids = tok(texts, return_tensors="pt", add_special_tokens=False,
               padding=True).to("cuda")
    pad_counts = (bids["attention_mask"] == 0).sum(dim=1).tolist()
    with torch.no_grad():
        model(**bids)
    br = caught["r"]
    with torch.no_grad():
        bo = model.generate(**bids, max_new_tokens=40, do_sample=False)
    blen = bids["input_ids"].shape[1]

    print(f"model {MODEL} · read layer {layer} · batch of {len(texts)}")
    print(f"padding added per item (tokens): {pad_counts}\n")
    print(f"{'item':>4} {'pad':>5} {'feat set':>10} {'jaccard':>8} "
          f"{'max|Δact|':>10} {'cos(resid)':>11} {'max|Δres|':>10} {'gen tokens':>11}")
    worst_j, all_same_tokens = 1.0, True
    for i in range(len(texts)):
        rb = br[i, -1]
        fb, fs = feats(rb), solo_feat[i]
        sb = set((fb > 0).nonzero().flatten().tolist())
        ss = set((fs > 0).nonzero().flatten().tolist())
        jac = len(sb & ss) / max(len(sb | ss), 1)
        dact = float((fb - fs).abs().max())
        cos = float(torch.nn.functional.cosine_similarity(
            rb.float().unsqueeze(0), solo_resid[i].float().unsqueeze(0)))
        dres = float((rb.float() - solo_resid[i].float()).abs().max())
        gb = bo[i][blen:].tolist()
        same = gb == solo_gen[i]
        all_same_tokens &= same
        worst_j = min(worst_j, jac)
        print(f"{i:>4} {pad_counts[i]:>5} {len(ss):>4}/{len(sb):<5} {jac:>8.4f} "
              f"{dact:>10.4f} {cos:>11.6f} {dres:>10.4f} "
              f"{'IDENTICAL' if same else 'DIFFERENT':>11}")

    print(f"\nworst feature-set Jaccard : {worst_j:.4f}")
    print(f"generated tokens identical: {all_same_tokens}")

    # 🚩 THE DISCRIMINATING CASE, and the first version of this script MISSED IT.
    # An item that received ZERO padding is a built-in control: if it also
    # diverges, the cause cannot be padding. Measured 2026-08-13 -- item 2 had
    # pad=0 and still generated different tokens, so the original verdict text
    # ("padding perturbs the read") was refuted by this script's own output and
    # I read past it once.
    #   >>> The cause is BATCH SHAPE selecting different matmul kernels; tiny
    #   >>> bf16 differences then flip greedy argmax wherever two tokens are
    #   >>> near-tied. Nothing to do with attention masks.
    zero_pad = [i for i, p in enumerate(pad_counts) if p == 0]
    if zero_pad:
        i = zero_pad[0]
        same = bo[i][blen:].tolist() == solo_gen[i]
        print(f"\nCONTROL: item {i} received ZERO padding -> generated "
              f"{'IDENTICALLY' if same else 'DIFFERENTLY'}")
        print("  ⇒ " + ("padding is implicated." if same else
                        "padding is NOT the cause — batch shape / kernel choice is."))
    else:
        print("\n⚠️ NO zero-padding item in this batch: the padding-vs-kernels "
              "question is UNTESTED here. Add a prompt of maximal length.")

    print("\nVERDICT:")
    if worst_j == 1.0 and all_same_tokens:
        print("  ✅ batching changes NOTHING we measure. Batch freely.")
    elif worst_j >= 0.95:
        print("  ⚠️ Same features fire (set identical); values wobble; greedy text diverges.")
        print("     ✅ SAFE if the readout uses WHICH features are active.")
        print("     ⚠️ Values are perturbed, so a continuous-activation classifier")
        print("        inherits batch noise — report which readout was used.")
        print("     🚨 NEVER BATCH BY ARM. If every batch is all-`asked` or")
        print("        all-`task`, batch composition is PERFECTLY CONFOUNDED with")
        print("        the treatment and kernel noise reads as a finding.")
        print("        ⇒ MIX ARMS WITHIN EVERY BATCH, fixed composition, and say so.")
    else:
        print("  🚩 batching MATERIALLY changes the read. Do NOT batch the")
        print("     measurement pass — generate batched, then RE-READ each")
        print("     conversation alone. Reads are cheap; generation is not.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
