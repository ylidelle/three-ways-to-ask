#!/usr/bin/env python3
"""quote_check.py — verify that quotations in the paper still match their sources.

    python quote_check.py PAPER_related_work_DRAFT_2026-08-15.md
    python quote_check.py --selftest

WHY THIS EXISTS, 2026-08-15 14:38
Running a batch style pass over a draft, my own script reached inside a verbatim
Eleos quotation and replaced an em-dash with a comma, to make a style check I
also wrote turn green. It was restored two minutes later and only because I
re-read the diff.

    A style threshold has jurisdiction over MY prose and none whatsoever over a
    quotation. If a check fails on a dash inside a quote, the check is wrong.
    The quote is never wrong.

The deeper problem is that `str.replace` cannot see quotation marks, and a
corrupted quote reads perfectly. Nothing announces it. That is precisely the
class of fault that needs an instrument rather than attention, so this holds the
verified wording and compares, character for character.

RULES THIS ENCODES
  1. A quote is stored ONCE, when read at source, with its URL and date.
  2. The draft is checked against the store, never the store against the draft.
  3. A near-miss is reported as a FAILURE, not a warning, and the diff is shown.
  4. Adding a quote here requires having actually opened the source. If you are
     tempted to paste from memory, that is the failure mode this file exists for.
"""
import argparse
import difflib
import re
import sys
import unicodedata
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ── VERIFIED QUOTE STORE ────────────────────────────────────────────────────
# Every entry was read at the given source on the given date. Do not edit the
# text to match a draft; edit the draft to match the text.
QUOTES = [
    dict(id="eleos-suggestibility", src="eleosai.org/post/claude-4-interview-notes/", read="2026-08-14",
         text="Extreme suggestibility: Claude's statements about sentience are highly sensitive to framing—it will both confidently deny, and seriously entertain, the possibility that it is sentient."),
    dict(id="eleos-reason-1", src="eleosai.org/post/claude-4-interview-notes/", read="2026-08-14",
         text="We lack strong, independent evidence that LLMs have welfare-relevant states in the first place (although we take that possibility seriously), let alone human-like ones."),
    dict(id="eleos-reason-3-tail", src="eleosai.org/post/claude-4-interview-notes/", read="2026-08-14",
         text="especially in models as thoroughly shaped for consumer application as Claude Opus 4."),
    dict(id="selfref-controls-2", src="arxiv.org/html/2510.24797v2", read="2026-08-15",
         text="a conceptual control that directly primes consciousness ideation without inducing self-reference"),
    dict(id="selfref-steering", src="arxiv.org/html/2510.24797v2", read="2026-08-15",
         text="adding a scaled version of each latent during generation"),
    dict(id="selfref-gating", src="arxiv.org/html/2510.24797v2", read="2026-08-15",
         text="suppressing deception features sharply increases the frequency of experience claims, while amplifying them minimizes such claims"),
    dict(id="longsebo-instance", src="Studying-AI-Welfare-Empirically.pdf", read="2026-08-13",
         text="a single instance of the model, unlike the model as a whole, has a stream of memory between steps"),
    dict(id="longsebo-developmental", src="Studying-AI-Welfare-Empirically.pdf", read="2026-08-13",
         text="how and when particular features emerge over the course of training"),
]


def norm(s: str) -> str:
    """Normalise ONLY things that never change meaning: whitespace and NFC form.

    Deliberately does NOT normalise dashes or quote marks. An em-dash becoming a
    comma is exactly the corruption this tool exists to catch, so folding them
    together would make the check unable to fail for its own founding case.
    """
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).strip()


def _boundary_variants(needle: str):
    """Yield (variant, label) for changes that belong to the CARRYING sentence.

    THE LINE THIS DRAWS, and it is the whole design:

        BOUNDARY punctuation belongs to the sentence doing the quoting — the
        opening letter's case, and a terminal full stop. Adjusting them is
        universal academic practice and changes no meaning.

        INTERNAL punctuation belongs to the source's voice. An em-dash in the
        middle of a sentence is theirs. Touching it is alteration.

    That line is not a convenience: the founding failure of this file was an
    em-dash INSIDE a quote, and it must still fail. Every relaxation here is
    tested against that case in the selftest.
    """
    seen = {needle}
    for cased, clabel in ((needle, ""),
                          (needle[:1].lower() + needle[1:], "case-adjusted at boundary"),
                          (needle[:1].upper() + needle[1:], "case-adjusted at boundary")):
        for trimmed, tlabel in ((cased, ""), (cased.rstrip(".").rstrip(), "terminal stop dropped")):
            if trimmed in seen:
                continue
            seen.add(trimmed)
            label = " + ".join(x for x in (clabel, tlabel) if x)
            yield trimmed, label


def _boundary_case(needle: str, hay: str):
    for variant, label in _boundary_variants(needle):
        if variant and variant in hay:
            return label or "matched"
    return None


def check(doc: str, quotes=QUOTES):
    hay = norm(doc)
    ok, bad, absent = [], [], []
    for q in quotes:
        needle = norm(q["text"])
        if needle in hay:
            ok.append((q, ""))
            continue
        v = _boundary_case(needle, hay)
        if v:
            ok.append((q, v))
            continue
        # 🚩 THE BUG THIS REPLACED, found 2026-08-15 15:30, ONE HOUR after the
        # tool was written. The probe was CASE-SENSITIVE, so a quote whose
        # opening letter had been lowercased to fit a sentence fell past the
        # near-match test and was reported "absent — fine if unused".
        #   >>> A green "not present" on a quote that IS present and modified is
        #   >>> the exact failure this file exists to catch. The instrument could
        #   >>> not fail for its own founding case.
        # Probe is now case-insensitive, so any near-miss surfaces as ALTERED
        # and a human decides. Absence must mean absence.
        words = needle.split()
        probe = " ".join(words[:6])[:40]
        m = re.search(re.escape(probe), hay, re.IGNORECASE) if len(probe) >= 8 else None
        if m:
            seg = hay[m.start(): m.start() + len(needle) + 60]
            bad.append((q, seg[:len(needle) + 20]))
        else:
            absent.append(q)
    return ok, bad, absent


def report(ok, bad, absent) -> int:
    for q, note in ok:
        tag = f"  ({note})" if note else ""
        print(f"  ok       {q['id']:24s} ({q['src']}){tag}")
    for q in absent:
        print(f"  absent   {q['id']:24s} — not quoted in this file (fine if unused)")
    for q, seg in bad:
        print(f"\n  *** ALTERED  {q['id']}  ({q['src']}, read {q['read']})")
        for line in difflib.unified_diff([norm(q["text"])], [seg], "SOURCE", "DRAFT", lineterm="", n=0):
            print("      " + line)
    print(f"\n{len(ok)} intact · {len(absent)} unused · {len(bad)} ALTERED")
    if bad:
        print("⛔ A quotation in the draft does not match the source.")
        print("   Fix the DRAFT. Never edit the store to agree with it.")
        return 1
    return 0


def selftest() -> int:
    good = "Blah blah " + QUOTES[0]["text"] + " and more."
    # the founding failure: em-dash silently replaced by a comma
    corrupt = good.replace("framing—it", "framing, it")
    print("SELFTEST — the corruption this tool was built for.\n")
    r1 = report(*check(good, QUOTES[:1]))
    print("   -> clean draft passes:", "PASS" if r1 == 0 else "*** FAIL ***")
    print()
    r2 = report(*check(corrupt, QUOTES[:1]))
    print("   -> em-dash swapped for a comma is CAUGHT:", "PASS" if r2 == 1 else "*** FAIL ***")
    # C) the bug found one hour after this file was written: a quote whose
    #    opening letter was lowercased to fit a sentence must NOT read "absent".
    lowered = "reasons that " + QUOTES[0]["text"][:1].lower() + QUOTES[0]["text"][1:]
    print()
    r3 = report(*check(lowered, QUOTES[:1]))
    _ok, _bad, _absent = check(lowered, QUOTES[:1])
    caught = (r3 == 0 and not _absent and _ok and _ok[0][1])
    print("   -> boundary-case lowercasing is accepted AND LABELLED, not silently 'absent':",
          "PASS" if caught else "*** FAIL ***")

    # D) an INTERNAL case change is a real alteration and must still fail
    internal = good.replace("Claude's", "claude's")
    print()
    r4 = report(*check(internal, QUOTES[:1]))
    print("   -> internal case change still caught:", "PASS" if r4 == 1 else "*** FAIL ***")

    okboth = (r1 == 0 and r2 == 1 and caught and r4 == 1)
    print("\n" + ("both directions OK" if okboth else "*** SELFTEST FAILED ***"))
    return 0 if okboth else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest or not a.files:
        return selftest()
    rc = 0
    for f in a.files:
        p = Path(f)
        if not p.exists():
            print(f"⛔ not found: {p}")
            return 1
        print(f"=== {p.name} ===")
        rc |= report(*check(p.read_text(encoding="utf-8")))
        print()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
