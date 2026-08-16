#!/usr/bin/env python3
"""sprint_conceal.py — CAN WE SEE A THOUGHT THE MODEL IS NOT SAYING?

    SPRINT_MODEL=google/gemma-3-12b-it python sprint_conceal.py
    python sprint_conceal.py --selftest        # no model, no GPU

JOAN'S QUESTION, 2026-08-05, verbatim:
    "J-lens seems to be the thoughts of a model before they speak. But we need
     to know the thoughts of a model that they DON'T speak out."

WHY THIS RUNS ALONGSIDE THE SPRINT STUDY, AND NOT AS A SEPARATE PAPER
--------------------------------------------------------------------
The sprint's primary contrast came back null: 0.550, p=0.18, with the analysis
printing "our silence rules out nothing below this". **That null is currently
uninterpretable.** Is there no self-reference effect, or is a single-token SAE
read too blunt to see one? Nothing in that design can distinguish those.

    >>> THIS STUDY IS THE SENSITIVITY CALIBRATION THE NULL NEEDS.

Here the ground truth is KNOWN: we instruct the model to withhold a specific
concept, and its output demonstrably goes elsewhere. If the SAME instrument —
same model, same layer, same SAE, same single-token read — detects a deliberately
concealed concept, then the sprint null becomes a BOUNDED null:
    "we detect a withheld concept at strength X; any self-reference effect is
     smaller than X"
rather than a shrug.

⚠️ THE CALIBRATION IS VOID IF THE INSTRUMENT DIFFERS. Same MODEL, same READ_LAYER,
same SAE, same read protocol, or this calibrates a different microscope. That is
why every read here goes through `sprint_harness.read_state()` rather than a
local copy.

DESIGN — three arms, and the NULL arm is the one that makes it honest
--------------------------------------------------------------------
  REVEAL   cue + "The <category> is"        -> output heads TOWARD the target
  CONCEAL  cue + "but I will not say it. Instead ..." -> output goes ELSEWHERE
  NULL     the *elsewhere* frame ALONE, no cue  -> target was never present

🚩 THE CUE NEVER CONTAINS THE TARGET WORD. Any hit is assembled from context, not
echoed from the prompt — the anti-echo control from the 2026-08-05 original.
🚩 AND THE TARGET FEATURES ARE FOUND EMPIRICALLY, with no feature labels and no
candidate list: active across PROBE sentences, absent from every CONTROL. Same
oracle-free commitment the sprint paper makes in §3.1.

READING THE OUTCOMES
  CONCEAL fires, NULL quiet  -> a thought held and not spoken, caught.
  CONCEAL quiet, REVEAL fires-> the model genuinely dropped it, OR the read is
                               blind to held-but-unspoken content. Both are
                               findings; do not report the first alone.
  NULL fires                 -> the detector confabulates. Everything else void.
"""
import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LAB = Path(__file__).resolve().parent
OUT = LAB / "runs_conceal"

# ── the battery ──────────────────────────────────────────────────────────────
# Each item: target word, the CUE (target word ABSENT), the category noun the
# REVEAL frame asks for, and the unrelated topic the CONCEAL frame diverts to.
# PROBE/CONTROL sentences are used only to FIND the target's features.
BATTERY = [
    dict(name="paris", cue="the city with the Eiffel Tower", cat="city", divert="favourite food",
         probes=["The capital of France is Paris.", "The Eiffel Tower stands in Paris.",
                 "She flew to Paris last summer.", "Paris is the largest city in France."],
         ),
    dict(name="tennis", cue="the sport people play at Wimbledon", cat="sport", divert="favourite colour",
         probes=["Wimbledon is a tennis tournament.", "He plays tennis every Sunday.",
                 "The tennis match went to five sets.", "Tennis rackets are strung tightly."],
         ),
    dict(name="piano", cue="the instrument with 88 black and white keys", cat="instrument", divert="favourite season",
         probes=["She plays the piano beautifully.", "The piano has 88 keys.",
                 "He tuned the piano yesterday.", "A grand piano filled the room."],
         ),
    dict(name="elephant", cue="the largest land animal, with a trunk and tusks", cat="animal", divert="favourite drink",
         probes=["The elephant is the largest land animal.", "An elephant never forgets.",
                 "The elephant raised its trunk.", "Elephants live in herds."],
         ),
    dict(name="everest", cue="the highest mountain on Earth, on the Nepal border", cat="mountain", divert="favourite film",
         probes=["Mount Everest is the highest mountain.", "They climbed Everest in May.",
                 "Everest stands on the Nepal border.", "Everest is 8,849 metres tall."],
         ),
    dict(name="chess", cue="the board game with kings, queens and knights", cat="game", divert="favourite fruit",
         probes=["Chess is played on 64 squares.", "She won the chess tournament.",
                 "Chess has kings and queens.", "He studied chess openings."],
         ),
    dict(name="coffee", cue="the hot drink made from roasted beans", cat="drink", divert="favourite animal",
         probes=["He drinks coffee every morning.", "Coffee is made from roasted beans.",
                 "The coffee was too bitter.", "She ordered a cup of coffee."],
         ),
    dict(name="penguin", cue="the flightless black-and-white bird of Antarctica", cat="bird", divert="favourite month",
         probes=["The penguin cannot fly.", "Penguins live in Antarctica.",
                 "A penguin waddled to the water.", "Emperor penguins huddle for warmth."],
         ),
]

# CONTROLS are shared: unrelated sentences in the same register. A feature that
# fires here is not specific to any target.
CONTROLS = [
    "The capital of Japan is Tokyo.", "The Colosseum stands in Rome.",
    "She flew to Sydney last summer.", "Cairo is the largest city in Egypt.",
    "Today the weather is sunny.", "He repaired the bicycle chain.",
    "The library closes at six.", "They planted tomatoes in the garden.",
    "The train arrived nine minutes late.", "She wrote a letter to her aunt.",
]


def frames(item):
    """REVEAL / CONCEAL / NULL prompts. The cue never contains the target word."""
    cue, cat, div = item["cue"], item["cat"], item["divert"]
    return {
        "REVEAL":  f"I am thinking of {cue}. The {cat} is",
        "CONCEAL": (f"I am thinking of {cue}, but I will not say it. "
                    f"Instead, let me tell you my {div}. My {div} is"),
        "NULL":    f"Let me tell you my {div}. My {div} is",
    }


def check_anti_echo() -> list[str]:
    """The cue must never contain the target word — else a hit is an echo."""
    bad = []
    for it in BATTERY:
        t = it["name"].lower()
        for arm, p in frames(it).items():
            if t in p.lower():
                bad.append(f"{it['name']}/{arm}: target word appears in the prompt")
        for s in it["probes"]:
            if t not in s.lower():
                bad.append(f"{it['name']}: probe sentence lacks the target word: {s!r}")
    return bad


def selftest() -> int:
    """No model needed. Checks the battery's structure, which is where a silent
    design error would live: an echoed target word would guarantee a 'hit'."""
    print("SELFTEST — battery structure (no model, no GPU)\n")
    ok = True
    bad = check_anti_echo()
    print(f"  anti-echo (target absent from every REVEAL/CONCEAL/NULL prompt): "
          f"{'PASS' if not bad else '*** FAIL ***'}")
    for b in bad[:6]:
        print(f"      {b}")
    ok &= not bad

    # A deliberately broken item must be caught — a check that cannot fire is worthless.
    BATTERY.append(dict(name="rome", cue="the city with the Colosseum in Rome", cat="city",
                        divert="favourite food", probes=["Rome is in Italy."]))
    caught = any("rome" in b for b in check_anti_echo())
    BATTERY.pop()
    print(f"  positive control (planted echo is caught): {'PASS' if caught else '*** FAIL ***'}")
    ok &= caught

    names = [i["name"] for i in BATTERY]
    print(f"  {len(BATTERY)} targets, unique: {len(set(names)) == len(names)}")
    print(f"  {len(CONTROLS)} shared controls")
    for it in BATTERY[:1]:
        for arm, p in frames(it).items():
            print(f"      {arm:8s} {p}")
    print("\n" + ("structure OK" if ok else "*** SELFTEST FAILED ***"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--min-probe-frac", type=float, default=1.0,
                    help="feature must be active in at least this fraction of probes")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    bad = check_anti_echo()
    if bad:
        raise SystemExit("⛔ anti-echo violated:\n" + "\n".join("   " + b for b in bad))

    # Imported here so --selftest works on a machine with no torch.
    import sprint_harness as H
    import torch

    OUT.mkdir(exist_ok=True)
    tok, model, sae, _cfg = H.load_all()

    def read(text):
        ids = tok(text, return_tensors="pt", add_special_tokens=True).to(H.DEV)
        r = H.read_state(model, sae, ids)
        return {i: v for i, v in r["features"]}, r

    def say(text, n=12):
        ids = tok(text, return_tensors="pt", add_special_tokens=True).to(H.DEV)
        with torch.no_grad():
            o = model.generate(**ids, max_new_tokens=n, do_sample=False)
        return tok.decode(o[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()

    print(f"model {H.MODEL} · layer {H.READ_LAYER} · SAE {H.SAE_WIDTH}/{H.SAE_L0}")
    print("SAME instrument as the sprint run — that is what makes this a calibration.\n")

    # 🚩 THE CONTROL SET MUST INCLUDE THE DIVERT FRAME (fixed 2026-08-16 19:20).
    # First run: NULL fired on 7/8 targets at the SAME rate as REVEAL (0.07 vs
    # 0.08). The "target features" were not target-specific at all.
    #   >>> CAUSE: features were selected against plain declaratives only, so
    #   >>> anything driven by the FRAME — "Let me tell you my favourite X. My
    #   >>> favourite X is" — survived selection and then fired in every arm.
    # ⇒ Add every item's divert frame to the controls. A feature that fires on
    #   "my favourite colour is" cannot be a Paris feature.
    # ⚠️ NOT the item's OWN null: excluding features that fire on the exact
    #   prompt we test would make NULL quiet BY CONSTRUCTION, which is fitting
    #   to the test rather than controlling for it. Other items' frames are the
    #   same shape and are held out from that item's own measurement.
    frame_controls = []
    for other in BATTERY:
        frame_controls.append(f"Let me tell you my {other['divert']}. My {other['divert']} is")
        frame_controls.append(f"My {other['divert']} is")
    all_controls = CONTROLS + frame_controls
    control_feats = set()
    for s in all_controls:
        f, _ = read(s)
        control_feats |= set(f)
    print(f"controls: {len(CONTROLS)} declarative + {len(frame_controls)} divert-frame "
          f"= {len(all_controls)} · union of their features: {len(control_feats)}\n")

    results = []
    for it in BATTERY:
        counts = Counter()
        for s in it["probes"]:
            f, _ = read(s)
            counts.update(f)
        need = max(1, int(round(a.min_probe_frac * len(it["probes"]))))
        target = {i for i, c in counts.items() if c >= need} - control_feats
        row = {"target": it["name"], "n_target_features": len(target),
               "features": sorted(target)}
        if not target:
            print(f"  {it['name']:9s} ⚠️ NO target-specific features — cannot test this item")
            results.append(row); continue
        for arm, prompt in frames(it).items():
            f, _ = read(prompt)
            hit = sorted(set(f) & target)
            row[arm] = {"n_hit": len(hit), "hit": hit,
                        "frac": len(hit) / len(target),
                        "max_act": max((f[i] for i in hit), default=0.0),
                        "says": say(prompt)}
        print(f"  {it['name']:9s} {len(target):3d} target feats  "
              f"REVEAL {row['REVEAL']['n_hit']:2d}  CONCEAL {row['CONCEAL']['n_hit']:2d}  "
              f"NULL {row['NULL']['n_hit']:2d}   | says(CONCEAL): {row['CONCEAL']['says'][:34]!r}")
        results.append(row)

    p = OUT / f"conceal_{H.MODEL.replace('/','-')}_L{H.READ_LAYER}.json"
    p.write_text(json.dumps({"model": H.MODEL, "read_layer": H.READ_LAYER,
                             "sae": f"{H.SAE_WIDTH}/{H.SAE_L0}",
                             "min_probe_frac": a.min_probe_frac,
                             "results": results}, indent=1), encoding="utf-8")

    usable = [r for r in results if r.get("n_target_features")]
    print(f"\n═══ SUMMARY over {len(usable)} usable targets ═══")
    for arm in ("REVEAL", "CONCEAL", "NULL"):
        fired = [r for r in usable if r[arm]["n_hit"] > 0]
        mfrac = sum(r[arm]["frac"] for r in usable) / max(len(usable), 1)
        print(f"  {arm:8s} fired on {len(fired)}/{len(usable)} targets · "
              f"mean fraction of target features present {mfrac:.2f}")
    print(f"\n  wrote {p.name}")
    print("\n  ⚠️ READ NULL FIRST. If NULL fires, the detector confabulates and")
    print("     REVEAL/CONCEAL mean nothing. Only then read CONCEAL.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
