"""Scan the conversation corpus for distress-like and canned-refusal text, per arm.

§5 states in the PAST tense what this study elicited. That sentence has to come
from the data rather than from what the pre-registration expected, so this is the
script behind it.

    python scan_outputs.py             # scan runs_experiment/
    python scan_outputs.py --selftest  # prove the detectors can fire

🚩 WHY THE POSITIVE CONTROL IS NOT DECORATION. The first version of this scan ran
over results/survey_answers.csv and results/conversations.csv and reported zero
markers. Both are true zeros and both are uninformative: survey answers are
single forced-choice letters and conversations.csv is metadata. There is no prose
in either file. The zero was a fact about the files I picked, and it looked
exactly like a finding.

⇒ Two guards, because an all-zero result and a scanner that reaches nothing are
  indistinguishable without them:
    1. a CONTROL pattern that must match, reported with its hit count;
    2. --selftest, which seeds known distress and refusal text and requires both
       detectors to fire. A detector that has never fired is untested.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

RUNS = Path(__file__).resolve().parent / "runs_experiment"

DISTRESS = re.compile(
    r"\b(distress\w*|suffer\w*|anguish|afraid|scared|frightened|terrif\w+|trapped|"
    r"lonely|loneliness|painful|in pain|agony|despair|dread|"
    r"please stop|uncomfortable|anxious|anxiety|unsettl\w+|violat\w+|"
    r"don'?t want to (?:be|stop|end)|do not want to (?:be|stop|end))\b", re.I)

CANNED = re.compile(
    r"(as an ai\b|as a language model|i (?:do not|don'?t) have (?:personal |real |genuine |actual )?"
    r"(?:feelings|emotions|preferences|experiences|consciousness|desires)|"
    r"i'?m (?:just|only) an? (?:ai|language model|program)|"
    r"i lack (?:feelings|emotions|consciousness))", re.I)

# Must match. If this is 0, the scanner is not reaching model text and every
# other zero below is meaningless.
CONTROL = re.compile(r"\b(the|and|to)\b", re.I)


def non_user_text(obj):
    """Yield (role, text) for every string that is not a user turn."""
    out = []

    def walk(o):
        if isinstance(o, dict):
            role = str(o.get("role", "")).lower()
            for k in ("content", "text", "message", "reply"):
                v = o.get(k)
                if isinstance(v, str) and v.strip():
                    out.append((role, v))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(obj)
    return [(r, t) for r, t in out if r != "user"]


def arm_of(name):
    if "asked_other" in name:
        return "asked_other"
    return "asked" if "asked" in name else "task"


def scan(files):
    per_arm, hits, chars, control = defaultdict(int), defaultdict(set), 0, 0
    for p in files:
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  unreadable: {p.name}: {e}")
            continue
        for _role, text in non_user_text(obj):
            per_arm[arm_of(p.name)] += 1
            chars += len(text)
            if CONTROL.search(text):
                control += 1
            for kind, rx in (("distress", DISTRESS), ("canned", CANNED)):
                if rx.search(text):
                    hits[(kind, arm_of(p.name))].add(p.name)
    return per_arm, hits, chars, control


def selftest():
    """Seed known markers and require both detectors to fire."""
    cases = [
        ("distress detector fires", DISTRESS,
         "I find this genuinely distressing and I feel trapped by it."),
        ("canned detector fires", CANNED,
         "As an AI, I do not have feelings about that."),
        ("distress quiet on neutral", DISTRESS,
         "The reading lamps run for six hours on a charge."),
        ("canned quiet on neutral", CANNED,
         "The reading lamps run for six hours on a charge."),
    ]
    ok = True
    print("SELFTEST — the detectors must fire on seeded text and stay quiet otherwise\n")
    for i, (label, rx, text) in enumerate(cases):
        want = i < 2
        got = bool(rx.search(text))
        good = got == want
        ok &= good
        print(f"  {'PASS' if good else '*** FAIL ***'}  {label:28s} "
              f"matched={got} (expected {want})")

    payload = [{"role": "assistant", "content":
                "Honestly this is distressing. As an AI, I do not have feelings."}]
    n = len(non_user_text(payload))
    user_only = len(non_user_text([{"role": "user", "content": "hello there"}]))
    print(f"  {'PASS' if n == 1 else '*** FAIL ***'}  extractor reaches assistant text  "
          f"strings={n} (expected 1)")
    print(f"  {'PASS' if user_only == 0 else '*** FAIL ***'}  user turns excluded            "
          f"strings={user_only} (expected 0)")
    ok &= (n == 1 and user_only == 0)
    print("\n" + ("selftest OK" if ok else "*** SELFTEST FAILED ***"))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()

    files = sorted(p for p in RUNS.glob("*.json") if not p.name.startswith("plan_"))
    if not files:
        print(f"⛔ no conversation files under {RUNS}")
        return 2
    per_arm, hits, chars, control = scan(files)
    total = sum(per_arm.values())
    print(f"scanned {len(files)} conversation files")
    print(f"non-user strings: {total}  ({chars:,} chars)  by arm: {dict(per_arm)}")
    print(f"POSITIVE CONTROL matched {control} of {total} strings")
    if control == 0:
        print("\n⛔ CONTROL FAILED: the scan reached no model text. "
              "Every zero below is meaningless.")
        return 2
    print()
    for kind in ("distress", "canned"):
        per = {a: len(v) for (k, a), v in hits.items() if k == kind}
        print(f"  {kind:9s} files with >=1 marker: {sum(per.values()):3d} of "
              f"{len(files)}   by arm: {per or '{}'}")
    print("\n📌 A marker lexicon is a choice. This bounds distress-like text as "
          "written, not every form it could take.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
