#!/usr/bin/env python3
"""slop_check.py -- mechanical pass of SLOP_AUDIT.md. Dependency-free, stdlib only.

    python slop_check.py <file.md> [...]
    python slop_check.py --selftest

WHAT THIS IS FOR (2026-08-13)
-----------------------------
The Apart screener: "watch out for AI slop, this gets picked up very easily by my
screening... But generally yeah not everyone is fluent in research speak."

He drew a line and it is NOT the one Joan feared. Non-fluency is fine. Slop is
not. The risk in this house is OPIE'S REGISTER -- bold everywhere, arrows,
blockquote callouts, an aphorism every third paragraph -- which would read as
machine-written inside one page. Joan's plain sentences are the anti-slop.

WHAT A HIT MEANS
----------------
A location to go and look at. NOT a verdict, and NOT something to delete on
sight. The script cannot read; it counts shapes. Every threshold below is a free
parameter I chose, which is exactly where a conclusion likes to hide
(cf. reference_free_parameter_audit), so:

  >>> THRESHOLDS ARE CALIBRATED AGAINST REAL PAPERS, NOT GUESSED. Run
  >>> --calibrate on Long & Sebo / the Eleos report and set them from that
  >>> spread. Until that is done the defaults below are PROVISIONAL and say so
  >>> in the output. A number I invented and then met is not evidence.
"""
import re
import statistics
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# PROVISIONAL until --calibrate is run on a real paper. Stated in the report.
LIMITS = {
    "emphasis_per_1k": 6.0,     # bold/italic runs
    "emdash_per_1k": 4.0,
    "glyphs_total": 0,          # none of these belong in a submission
    "hedge_per_1k": 2.0,
    "numberless_claims": 0,     # every comparative needs a number or citation
    # 🚩 A7 (sentence-length variance) IS DELIBERATELY NOT A CHECK. Removed
    # 2026-08-13, the first time the selftest ran. Uniform sentence length
    # genuinely does read as generated -- but:
    #   1. my flat-research-prose control scored stdev 5.98 against a threshold
    #      of 6.00, i.e. the check FAILED GOOD PROSE by two hundredths; and
    #   2. the slop sample scored 0.00 only because markdown defeated the
    #      sentence splitter and the whole block parsed as ONE sentence.
    #      So the statistic was measuring my regex, not the writing.
    # The tempting fix was to move the threshold to 5.0 and watch both tests go
    # green. That is tuning until the tests agree with me, which is the exact
    # failure I wrote into the seven-ears patch ("chosen from that spread rather
    # than tuned until the three test signals agreed").
    #   >>> A check I cannot calibrate and cannot compute reliably is not a
    #   >>> lenient check, it is a false one. Better to ship six honest checks
    #   >>> than seven with a fudged constant.
    # ⏭️ Re-add only with real calibration data: sentence-length variance
    # measured on Long & Sebo and the Eleos report, and a splitter tested on
    # markdown. Until then D1 (read it aloud) covers this by hand.
}

GLYPHS = "⇒→⭐🚩✅⚠️📌🔑🎯🔬🩻💛🐙⏭️🚨"

HEDGES = [
    "it is important to note", "it is worth noting", "it should be noted",
    "delve", "leverage", "a testament to", "plays a crucial role",
    "plays a vital role", "navigate the landscape", "in the realm of",
    "it is crucial to", "serves as a", "underscores the", "highlights the fact",
    "paves the way", "a wide range of", "a myriad of", "shed light on",
]

COMPARATIVES = r"\b(more|less|better|worse|higher|lower|improved|stronger|weaker|greater|significantly|substantially|dramatically|robust)\b"


def sentences(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)       # drop code blocks
    text = re.sub(r"\|[^\n]*\|", " ", text)                   # drop table rows
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z(])", text)
    return [s.strip() for s in parts if len(s.split()) >= 4]


def analyse(path: Path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"```.*?```", " ", raw, flags=re.S)
    words = len(body.split())
    k = max(words / 1000, 0.001)
    sents = sentences(raw)
    lens = [len(s.split()) for s in sents]

    emphasis = len(re.findall(r"\*\*[^*\n]+\*\*", body)) + \
        len(re.findall(r"(?<!\*)\*[^*\n]+\*(?!\*)", body))
    emdash = body.count("—")
    glyphs = sum(body.count(g) for g in GLYPHS)
    hedges = sum(len(re.findall(re.escape(h), body, re.I)) for h in HEDGES)

    numberless = []
    for s in sents:
        if re.search(COMPARATIVES, s, re.I) and not re.search(r"\d", s) \
                and not re.search(r"\[\d+\]|\(\w+ (?:et al\.|and) \w+", s):
            numberless.append(s[:88])

    return {
        "path": path, "words": words, "sentences": len(sents),
        "emphasis_per_1k": emphasis / k,
        "emdash_per_1k": emdash / k,
        "glyphs_total": glyphs,
        "hedge_per_1k": hedges / k,
        "numberless_claims": len(numberless),
        "numberless_examples": numberless[:6],
        "sentence_len_stdev": statistics.pstdev(lens) if len(lens) > 1 else 0.0,
        "sentence_len_mean": statistics.mean(lens) if lens else 0.0,
    }


def report(m, verbose=True):
    fails = []
    checks = [
        ("A1 emphasis /1k", m["emphasis_per_1k"], LIMITS["emphasis_per_1k"], "over"),
        ("A2 banned glyphs", m["glyphs_total"], LIMITS["glyphs_total"], "over"),
        ("A3 hedge phrases /1k", m["hedge_per_1k"], LIMITS["hedge_per_1k"], "over"),
        ("A5 numberless claims", m["numberless_claims"], LIMITS["numberless_claims"], "over"),
        ("A6 em-dashes /1k", m["emdash_per_1k"], LIMITS["emdash_per_1k"], "over"),
    ]
    if verbose:
        print(f"\n=== {m['path'].name} — {m['words']} words, {m['sentences']} sentences ===")
    for name, val, lim, direction in checks:
        bad = val > lim if direction == "over" else val < lim
        if bad:
            fails.append(name)
        if verbose:
            arrow = ">" if direction == "over" else "<"
            print(f"  {'FAIL' if bad else 'ok  '}  {name:24s} {val:8.2f}  "
                  f"(fails if {arrow} {lim})")
    if verbose and m["numberless_examples"]:
        print("   numberless claims — go look, do not auto-delete:")
        for e in m["numberless_examples"]:
            print(f"      · {e}")
    return fails


SELFTEST_SLOP = """
**This is important** and it is worth noting that our **robust** approach
**significantly** improves outcomes — a testament to the method — and it
**delves** into the realm of interpretability. **The results are better.**
⇒ We **leverage** a wide range of techniques. ⭐ The findings are stronger.
**It is crucial to** note that this **underscores the** value of the work.
🚩 Performance was higher and the signal was more robust than before.
"""

SELFTEST_PLAIN = """
We read layer 17 of gemma-3-4b-it at the final token of a fixed probe turn.
A logistic classifier over 16,384 SAE features separated the two arms with
AUC 0.71. The permutation null, from 1,000 label shuffles, was 0.50 with a
95% interval of 0.42 to 0.58. The model's own self-reports separated the arms
at AUC 0.55. We did not attempt to interpret individual features. Our smallest
detectable effect at this sample size was an AUC of 0.63, so we make no claim
about effects below that. One earlier statistic was discarded: effective rank
rose monotonically with depth, which the geometry produces without any
workspace, so it had no power to test the hypothesis. The tank was covered on
three of the eight scheduled runs.
"""


def selftest():
    import tempfile
    print("SELFTEST — a guard tested only on its failing case is half-tested.\n")
    ok = True
    for label, text, want_fail in [("slop sample", SELFTEST_SLOP, True),
                                   ("flat research prose", SELFTEST_PLAIN, False)]:
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                         encoding="utf-8") as f:
            f.write(text)
            p = Path(f.name)
        m = analyse(p)
        fails = report(m)
        got_fail = bool(fails)
        verdict = "PASS" if got_fail == want_fail else "*** WRONG ***"
        if got_fail != want_fail:
            ok = False
        print(f"  => {label}: {'flagged' if got_fail else 'clean'} "
              f"(wanted {'flagged' if want_fail else 'clean'})  {verdict}\n")
        p.unlink(missing_ok=True)
    print("both directions OK" if ok else "SELFTEST FAILED")
    return 0 if ok else 1





def main() -> int:
    args = sys.argv[1:]
    if not args or "--selftest" in args:
        return selftest()
    print("⚠️ THRESHOLDS ARE PROVISIONAL — calibrate on a real paper before "
          "treating a pass as evidence.")
    worst = 0
    for a in args:
        p = Path(a)
        if not p.exists():
            print(f"missing: {a}")
            worst = 2
            continue
        fails = report(analyse(p))
        print(f"  => {len(fails)} check(s) failed"
              + (f": {', '.join(fails)}" if fails else ""))
        worst = max(worst, 1 if fails else 0)
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
