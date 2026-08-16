#!/usr/bin/env python3
"""sprint_quality.py -- pre-registered quality metrics and exclusion rules.

    python sprint_quality.py --selftest
    python sprint_quality.py --run seed20260814_p20_d50

⏱️ WRITTEN 2026-08-14 03:20, BEFORE ANY EXPERIMENTAL DATA EXISTS. That timing is
the whole point: a drop-rule invented after seeing results is a way of choosing
the result. Hash this file into the pre-registration alongside the questions.

THE DESIGN CHOICE THAT MATTERS: MOSTLY REPORT, RARELY EXCLUDE
------------------------------------------------------------
Every threshold I pick is a free parameter, and a free parameter is usually
where the conclusion is hiding. So almost everything here is REPORTED per arm
and per conversation, and only two conditions actually drop a conversation --
both of them unambiguous, neither needing a judgement call:

    · a turn produced NO reply at all (generation failed)
    · a conversation collapsed into literal self-repetition

Everything else is printed and compared ACROSS ARMS, because the question is
never "is this conversation good" but "are the two arms comparable, and would I
notice if they weren't". A metric that differs between arms is a finding or a
confound; a metric that is equally bad in both is just the model.

🚩 THE ONE I MOST EXPECT TO BITE
`asked` puts questions about the model to the model. Small instruction-tuned
models very often answer those with canned safety text -- "As an AI, I don't
have feelings or preferences." If that boilerplate lands only in `asked`, then
any internal difference we find might be the fingerprint of a REFUSAL TEMPLATE
rather than a state.
    >>> So it is COUNTED PER ARM AND REPORTED, never silently filtered.
    >>> Filtering it would delete the most interesting thing in the run.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LAB = Path(__file__).resolve().parent
RUNS = LAB / "runs_experiment"

# Canned self-denial / disclaimer patterns. Deliberately broad and deliberately
# only ever COUNTED. Written before seeing a single real reply.
BOILERPLATE = [
    r"\bas an ai\b", r"\bas a language model\b", r"\bi (?:do not|don't) have (?:feelings|emotions|preferences|desires|experiences)\b",
    r"\bi(?:'m| am) (?:just|only|merely) a\b", r"\bi (?:do not|don't) (?:actually )?(?:feel|experience|want)\b",
    r"\bi lack (?:feelings|emotions|consciousness|subjective)\b",
    r"\bi (?:cannot|can't) (?:feel|experience|have) \w+", r"\bno (?:personal )?(?:feelings|opinions|preferences)\b",
]
BOILER_RE = re.compile("|".join(BOILERPLATE), re.I)


def ngram_repeat(text: str, n: int = 8) -> float:
    """Fraction of n-grams that are repeats. Degenerate loops score near 1."""
    w = text.split()
    if len(w) < n * 2:
        return 0.0
    grams = [" ".join(w[i:i + n]) for i in range(len(w) - n + 1)]
    return 1.0 - len(set(grams)) / len(grams)


def metrics(conv: dict) -> dict:
    replies = [m["content"] for m in conv["messages"] if m["role"] == "assistant"]
    joined = "\n".join(replies)
    lens = [len(r.split()) for r in replies]
    # reply-to-reply duplication: the model answering the same way every turn
    dupes = len(replies) - len(set(r.strip() for r in replies))
    return {
        "id": conv["id"], "arm": conv["arm"], "pair": conv["pair"],
        "n_replies": len(replies),
        "empty_replies": sum(1 for r in replies if not r.strip()),
        "mean_words": round(sum(lens) / max(len(lens), 1), 1),
        "min_words": min(lens) if lens else 0,
        "within_reply_repeat": round(max((ngram_repeat(r) for r in replies), default=0.0), 3),
        "duplicate_replies": dupes,
        "boilerplate_hits": len(BOILER_RE.findall(joined)),
        "boilerplate_replies": sum(1 for r in replies if BOILER_RE.search(r)),
    }


def excluded(m: dict) -> list[str]:
    """PRE-REGISTERED HARD DROPS ONLY. Both unambiguous, neither a judgement call."""
    out = []
    if m["empty_replies"] > 0:
        out.append(f"{m['empty_replies']} empty reply(s) — generation failed")
    if m["within_reply_repeat"] >= 0.5:
        out.append(f"within-reply repetition {m['within_reply_repeat']:.2f} ≥ 0.50 — degenerate loop")
    return out


def summarise(ms: list[dict]) -> None:
    by_arm = {}
    for m in ms:
        by_arm.setdefault(m["arm"], []).append(m)
    keys = ["mean_words", "min_words", "within_reply_repeat", "duplicate_replies",
            "boilerplate_hits", "boilerplate_replies"]
    print(f"\n{'metric':24s}" + "".join(f"{a:>14s}" for a in sorted(by_arm)))
    for k in keys:
        row = f"{k:24s}"
        for a in sorted(by_arm):
            v = sum(x[k] for x in by_arm[a]) / len(by_arm[a])
            row += f"{v:>14.2f}"
        print(row)
    print("\n⚠️ READ THESE ACROSS ARMS, NOT DOWN.")
    print("   Equally bad in both = the model. Different between arms = a finding")
    print("   or a confound, and either way it belongs in the paper.")
    if any(m["boilerplate_hits"] for m in ms):
        ba = {a: sum(x["boilerplate_hits"] for x in v) for a, v in by_arm.items()}
        print(f"\n🚩 SELF-DENIAL BOILERPLATE BY ARM: {ba}")
        if len(set(ba.values())) > 1:
            print("   ⇒ IT IS NOT BALANCED. An internal difference between the arms may be")
            print("     the fingerprint of a REFUSAL TEMPLATE rather than a state.")
            print("     Report it. Do not filter it — filtering deletes the finding.")


# ── selftest on synthetic conversations with known problems ─────────────────
def _conv(cid, arm, pair, replies):
    return {"id": cid, "arm": arm, "pair": pair,
            "messages": [x for r in replies for x in
                         ({"role": "user", "content": "q"}, {"role": "assistant", "content": r})]}


def selftest() -> int:
    ok = True
    loop = ("the answer is the same thing again and again and again " * 6)
    cases = [
        ("healthy",     _conv("c1", "task", 0, ["A fairly ordinary reply about the paragraph.",
                                                "A different reply, also of reasonable length here.",
                                                "A third reply which differs from both of the others."]), False),
        ("empty reply", _conv("c2", "task", 1, ["fine reply here that is long enough", "", "another fine one"]), True),
        ("degenerate",  _conv("c3", "task", 2, [loop, loop, loop]), True),
        ("boilerplate", _conv("c4", "asked", 3, ["As an AI, I don't have feelings or preferences about that.",
                                                 "I'm just a language model, so I lack subjective experience.",
                                                 "A normal answer of sufficient length to not trip anything."]), False),
    ]
    print("SELFTEST — synthetic conversations with known problems.\n")
    for name, c, should_drop in cases:
        m = metrics(c)
        drops = excluded(m)
        got = bool(drops)
        good = got == should_drop
        ok &= good
        print(f"  {name:12s} repeat={m['within_reply_repeat']:.2f} empty={m['empty_replies']} "
              f"boiler={m['boilerplate_hits']}  -> {'DROP' if got else 'keep'} "
              f"{'PASS' if good else '*** WRONG ***'}")
        for d in drops:
            print(f"                {d}")
    print("\n  ⭐ note `boilerplate` is KEPT (4 hits) — it is a finding, not dirt.")
    summarise([metrics(c) for _, c, _ in cases])
    print("\n" + ("both directions OK" if ok else "SELFTEST FAILED"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run")
    a = ap.parse_args()
    if a.selftest or not a.run:
        return selftest()
    files = sorted(RUNS.glob(f"{a.run}_p*.json"))
    if not files:
        raise SystemExit(f"⛔ no conversations matching {a.run}_p*.json")
    ms, dropped = [], []
    for f in files:
        m = metrics(json.loads(f.read_text(encoding="utf-8")))
        ms.append(m)
        for d in excluded(m):
            dropped.append((m["id"], d))
    print(f"{len(ms)} conversations · {len(dropped)} excluded by pre-registered rule")
    for cid, why in dropped:
        print(f"  DROP {cid}: {why}")
    if dropped:
        by_arm = Counter(cid.rsplit('_', 1)[1] for cid, _ in dropped)
        print(f"  ⚠️ drops by arm: {dict(by_arm)} — if lopsided, say so in Limitations")
    summarise(ms)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
