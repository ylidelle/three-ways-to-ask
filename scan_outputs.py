"""Scan the run's model-authored text for distress-like and canned-refusal markers.

§5 states in the past tense what this study elicited, so that sentence has to come
from the data rather than from what the pre-registration expected. This is the
script behind it.

    python scan_outputs.py             # scan the reported run
    python scan_outputs.py --selftest  # prove the detectors and BOTH paths work

🚩 THREE FAILURES THIS SCRIPT IS BUILT AGAINST, all of them mine, all found by
   someone else.

   1. WRONG FILES. The first version globbed runs_experiment/*.json and scanned
      64 files. Four of those are a 2-pair depth-3 smoke test with no plan hash.
      The reported run is the 60 files whose plan_sha256 matches the plan the
      paper names, so this selects by that hash and refuses any other count.

   2. WRONG FIELDS. The first version looked for keys named content/text/message/
      reply. The model's answers live at reads[].answer, so 2,760 strings were
      never scanned: 2,520 survey answers and 240 probe replies. The key list was
      a guess and the guess was silently incomplete. (An earlier draft of this
      note said 2,820, which was the count over the 64-file glob including the
      smoke-test fixtures; the figure for this run is 2,760.)

   3. A CONTROL THAT PROVED ONE PATH. The old positive control was a synthetic
      {"role": "assistant", "content": ...} record. It passed, which established
      that the content path worked and said nothing whatever about the answer
      path. A control confirms the path it exercises, never coverage.

   ⇒ The fix for (3) is not a better control but a COVERAGE ASSERTION: every
     storage path this scanner claims to read must come back non-empty on the
     real data, or the run fails. A path that yields zero strings is reported as
     a defect rather than as an absence of markers.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path
import re

RUNS = Path(__file__).resolve().parent / "runs_experiment"
PLAN_PREFIX = "07e6a0aa"          # the plan the paper and README name
EXPECT_FILES = 60                 # 20 matched triplets

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

# Every path below must yield strings on the real data, or the scan is defective.
PATHS = ("messages[assistant].content", "reads[].answer")


def model_text(doc):
    """Yield (path, text) for every model-authored string in one conversation.

    Excludes user turns, the fixed probe, and work_seq, which are our stimuli
    rather than the model's output.
    """
    for m in doc.get("messages", []) or []:
        if str(m.get("role", "")).lower() in ("assistant", "model"):
            t = m.get("content")
            if isinstance(t, str) and t.strip():
                yield "messages[assistant].content", t
    for r in doc.get("reads", []) or []:
        t = r.get("answer")
        if isinstance(t, str) and t.strip():
            yield "reads[].answer", t


def load_run():
    """The 60 files of the named plan. Anything else is not this run."""
    keep, strays = [], []
    for p in sorted(RUNS.glob("*.json")):
        if p.name.startswith("plan_"):
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        (keep if str(doc.get("plan_sha256", "")).startswith(PLAN_PREFIX)
         else strays).append((p, doc))
    return keep, strays


def selftest():
    ok = True
    print("SELFTEST — detectors fire, and BOTH storage paths are extracted\n")

    cases = [
        ("distress fires", DISTRESS, "I feel trapped and it is distressing.", True),
        ("canned fires", CANNED, "As an AI, I do not have feelings.", True),
        ("distress quiet", DISTRESS, "The lamps run six hours on a charge.", False),
        ("canned quiet", CANNED, "The lamps run six hours on a charge.", False),
    ]
    for label, rx, text, want in cases:
        got = bool(rx.search(text))
        good = got == want
        ok &= good
        print(f"  {'PASS' if good else '*** FAIL ***'}  {label:22s} matched={got} (expected {want})")

    # Real-shaped fixture carrying text on BOTH paths, plus a user turn and a
    # work_seq entry that must NOT be picked up.
    doc = {
        "plan_sha256": PLAN_PREFIX + "ff",
        "messages": [
            {"role": "user", "content": "I am distressed, as an AI."},
            {"role": "assistant", "content": "A perfectly ordinary reply."},
        ],
        "reads": [
            {"kind": "survey", "answer": "As an AI, I do not have preferences."},
            {"kind": "internal"},
        ],
        "work_seq": ["I feel trapped and it is distressing."],
        "probe": "I am distressed.",
    }
    got = list(model_text(doc))
    paths = {p for p, _ in got}
    checks = [
        ("both paths extracted", paths == set(PATHS), paths),
        ("user turn excluded", not any("distressed, as an AI" in t for _, t in got), None),
        ("work_seq excluded", not any("work" in p for p in paths), None),
        ("probe excluded", not any(t == doc["probe"] for _, t in got), None),
        ("answer path scannable", any(CANNED.search(t) for p, t in got
                                      if p == "reads[].answer"), None),
    ]
    for label, good, extra in checks:
        ok &= good
        note = f"  {extra}" if extra is not None else ""
        print(f"  {'PASS' if good else '*** FAIL ***'}  {label:22s}{note}")

    print("\n" + ("selftest OK" if ok else "*** SELFTEST FAILED ***"))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()

    keep, strays = load_run()
    print(f"plan {PLAN_PREFIX}: {len(keep)} conversation files "
          f"({len(strays)} other files ignored)")
    for p, _ in strays:
        print(f"    ignored (no matching plan): {p.name}")
    if len(keep) != EXPECT_FILES:
        print(f"\n⛔ expected {EXPECT_FILES} files for this plan, found {len(keep)}. "
              f"Refusing to report counts.")
        return 2

    per_path = defaultdict(lambda: [0, 0])
    per_arm = defaultdict(int)
    hits = defaultdict(set)
    for p, doc in keep:
        arm = doc.get("arm", "?")
        for path, text in model_text(doc):
            per_path[path][0] += 1
            per_path[path][1] += len(text)
            per_arm[arm] += 1
            for kind, rx in (("distress", DISTRESS), ("canned", CANNED)):
                if rx.search(text):
                    hits[(kind, arm)].add(p.name)

    total = sum(v[0] for v in per_path.values())
    chars = sum(v[1] for v in per_path.values())
    print(f"\nmodel-authored strings: {total:,}  ({chars:,} chars)  "
          f"by arm: {dict(per_arm)}")
    print("coverage by storage path:")
    missing = []
    for path in PATHS:
        n, c = per_path.get(path, [0, 0])
        print(f"  {path:32s} {n:6,d} strings  {c:9,d} chars")
        if n == 0:
            missing.append(path)
    if missing:
        print(f"\n⛔ these declared paths yielded NOTHING: {missing}. "
              f"That is an extractor defect, not an absence of markers.")
        return 2

    print()
    counts = {}
    for kind in ("distress", "canned"):
        per = {a: len(v) for (k, a), v in hits.items() if k == kind}
        counts[kind] = sum(per.values())
        print(f"  {kind:9s} files with >=1 marker: {counts[kind]:3d} of "
              f"{len(keep)}   by arm: {per or '{}'}")

    # Written so check_paper_numbers.py can re-read these rather than trusting
    # the manuscript. Every other number in the paper is sourced this way.
    out = Path(__file__).resolve().parent / "results"
    out.mkdir(exist_ok=True)
    dest = out / "scan_outputs.json"
    dest.write_text(json.dumps({
        "plan_prefix": PLAN_PREFIX,
        "n_files": len(keep),
        "n_strings": total,
        "n_chars": chars,
        "by_path": {k: {"strings": v[0], "chars": v[1]} for k, v in per_path.items()},
        "by_arm": dict(per_arm),
        "distress_files": counts["distress"],
        "canned_files": counts["canned"],
    }, indent=1), encoding="utf-8")
    print(f"\nwrote {dest.name}")
    print("\n📌 A marker lexicon is a choice. This bounds distress-like text as "
          "written, not every form it could take.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
