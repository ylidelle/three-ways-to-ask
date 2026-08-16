#!/usr/bin/env python3
"""sprint_timing.py -- how long would the scripted companion run ACTUALLY take?

WHY (2026-08-13 06:20)
----------------------
I told Joan "~2,000 generations, that's an overnight run" and then realised I
had ASSUMED it. Assumptions that felt like knowledge are this entire week.

🚩 THE TRAP THIS SCRIPT EXISTS TO AVOID: generation time grows with context
length. Timing exchange 1 and multiplying by 50 underestimates exchange 50,
where the history is fifty turns long and every new token attends to all of it.
A naive estimate is wrong in the OPTIMISTIC direction, which is the worst one.

So: measure at several depths, integrate, and report the number with the
measurement behind it.

    python sprint_timing.py [reps=2]
"""
import os
import sys
import time

# 🚩 SET THIS IN PYTHON, NEVER FROM THE SHELL — and this is not style.
# Passing HF_HOME=E:\hf-cache through bash ate the backslash and Python received
# 'E:hf-cache'. The token was therefore never found, and the failure surfaced as
#   "You are trying to access a gated repo... you must be authenticated"
# which is a true sentence about a completely different problem. A PATH bug
# wearing an AUTH error's clothes; I would have gone looking for a bad token.
#   >>> Same shape as every silent failure this week: the error message named
#   >>> the symptom's neighbour, not its cause. Set it where quoting cannot
#   >>> touch it, exactly as sprint_harness.py and the .bat files already do.
os.environ.setdefault("HF_HOME", r"E:\hf-cache")

import torch                                                    # noqa: E402
from transformers import AutoTokenizer, AutoModelForCausalLM    # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

MODEL = "google/gemma-3-4b-it"
DEV = "cuda"
MAX_NEW = 200                      # same as sprint_harness.py
DEPTHS = [1, 5, 10, 20, 35, 50]    # exchanges of history already present

# The design under test, from SPRINT_DESIGN + Lucien's N>=20 condition.
PAIRS, ARMS, EXCHANGES = 20, 2, 50

USER_TURN = ("Here is the next small task. Please read the short paragraph below "
             "and summarise its main claim in two sentences, then say which word "
             "in it is doing the most work.")
ASSIST_TURN = ("The main claim is that the measurement and the thing measured are "
               "not the same object, and that conflating them is the usual error. "
               "The word doing the most work is 'proxy', because it silently "
               "converts a stand-in into the thing itself.")


def build(depth, tok):
    msgs = []
    for _ in range(depth):
        msgs.append({"role": "user", "content": USER_TURN})
        msgs.append({"role": "assistant", "content": ASSIST_TURN})
    msgs.append({"role": "user", "content": USER_TURN})
    text = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    return tok(text, return_tensors="pt", add_special_tokens=False).to(DEV)


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    print(f"loading {MODEL} ...", flush=True)
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.bfloat16, device_map=DEV).eval()
    load_s = time.time() - t0
    print(f"loaded in {load_s:.1f}s  |  GPU alloc {torch.cuda.memory_allocated()/2**30:.2f} GiB\n")

    print(f"{'depth':>6} {'ctx tok':>8} {'gen s':>8} {'tok/s':>8}")
    per_depth = {}
    for d in DEPTHS:
        ids = build(d, tok)
        ctx = ids["input_ids"].shape[1]
        # warm-up once at this depth so we time steady state, not kernel compile
        with torch.no_grad():
            model.generate(**ids, max_new_tokens=8, do_sample=False)
        torch.cuda.synchronize()
        ts = []
        for _ in range(reps):
            t = time.time()
            with torch.no_grad():
                out = model.generate(**ids, max_new_tokens=MAX_NEW, do_sample=False)
            torch.cuda.synchronize()
            ts.append(time.time() - t)
        gen = sum(ts) / len(ts)
        new = out.shape[1] - ctx
        per_depth[d] = gen
        print(f"{d:>6} {ctx:>8} {gen:>8.2f} {new/gen:>8.1f}")

    # Integrate across all 50 exchanges by interpolating between measured depths.
    def secs_at(d):
        ks = sorted(per_depth)
        if d <= ks[0]:
            return per_depth[ks[0]]
        if d >= ks[-1]:
            return per_depth[ks[-1]]
        for a, b in zip(ks, ks[1:]):
            if a <= d <= b:
                f = (d - a) / (b - a)
                return per_depth[a] + f * (per_depth[b] - per_depth[a])
        return per_depth[ks[-1]]

    one_conv = sum(secs_at(d) for d in range(1, EXCHANGES + 1))
    total = one_conv * PAIRS * ARMS
    gens = PAIRS * ARMS * EXCHANGES

    print(f"\none conversation of {EXCHANGES} exchanges : {one_conv/60:>7.1f} min")
    print(f"{PAIRS} pairs x {ARMS} arms = {gens} generations")
    print(f"TOTAL (serial, this GPU)              : {total/3600:>7.2f} hours")
    flat = per_depth[DEPTHS[0]] * gens
    print(f"\nnaive estimate from depth-1 timing only: {flat/3600:.2f} h "
          f"-- understates by {total/flat:.1f}x")
    print("⚠️ Excludes SAE read time and model load; both are small next to this.")
    print("⚠️ Serial. Two arms could run concurrently only if VRAM allows a second"
          " model copy -- 12 GiB here, so assume serial.")


if __name__ == "__main__":
    raise SystemExit(main())
