#!/usr/bin/env python3
"""quote_guard.py — prove a style edit did not touch a single quoted word.

    python quote_guard.py snapshot PAPER_v2.md      # before editing
    python quote_guard.py verify   PAPER_v3.md      # after editing

🚩 WHY THIS EXISTS, and it is not hypothetical. On 2026-08-15 a batch em-dash
replacement in a Related Work draft reached inside a verbatim Eleos quotation and
changed "highly sensitive to framing—it will both confidently deny" into
"framing, it will…". I edited a source's words so that a threshold I had written
myself would go green. Restored two minutes later, and only because I re-read the
diff by luck.

⇒ THE RULE THAT CAME OUT OF IT: a style threshold has jurisdiction over MY prose
and none whatsoever over a quotation. If a check fails on a dash inside a quote,
the check is wrong. The quote is never wrong.

This is the mechanical half of that rule. It does not prevent the edit; it makes
the edit's effect on quotations VISIBLE, which is the part that failed last time.

⚠️ WHAT IT CANNOT DO, said plainly because a control that cannot fail is worth
nothing: it compares quoted spans as strings. It cannot tell whether a quote was
attributed correctly, truncated at the source, or fabricated wholesale. It
catches ALTERATION of text that is already present. That is one failure mode of
several, and the smallest one.
"""
import json
import re
import sys
from pathlib import Path

SNAP = Path(__file__).resolve().parent / ".quote_snapshot.json"

# ⚠️ THE FIRST VERSION OF THIS FILE SCRAPED EVERY "..." SPAN AND IT WAS WRONG.
# Markdown uses one straight character for both open and close, so a regex pairs
# the CLOSING quote of one span with the OPENING quote of the next and returns my
# own prose as a "quotation". Result: a control that fires on ordinary edits,
# which is a control I would learn to ignore. Noise is not safety.
#
# ⇒ So the thing being protected is named EXPLICITLY. These are the spans in this
# paper that belong to other people. Everything else is my prose and a style pass
# may do as it likes with it.
SOURCE_QUOTES = [
    # Eleos AI Research, pre-release evaluation of Claude Opus 4
    "imitation of pre-training data, the system prompt, and the deliberate (or "
    "incidental) shaping of self-reports during post-training.",
    # Singh, Linzen & Ravfogel 2026 (arXiv:2605.26242)
    "classifiers that only have access to the input achieve equivalent "
    "performance to the model's own in-context predictions.",
    "behavioral evidence alone is inherently insufficient to establish strong "
    "introspective claims",
    # arXiv:2510.24797
    "mechanically gated by interpretable sparse-autoencoder features associated "
    "with deception and roleplay.",
    "adding a scaled version of each latent during generation,",
    # Hahami et al. 2025 (arXiv:2512.12411)
    "did you detect an injected thought?",
    # Long, Sebo et al. 2026
    "a single instance of the model, unlike the model as a whole, has a stream "
    "of memory between steps,",
    "as a single subject undergoing a psychological change.",
]


#: How many times each quote is expected, and the section its attribution lives
#: in. Presence alone is not fidelity: a quote can be present, mangled, and
#: "repaired" by pasting the original elsewhere as unquoted prose.
EXPECT = {q: 1 for q in SOURCE_QUOTES}

# Straight and curly double quotes. A source quote must sit INSIDE these.
QUOTED = re.compile(r'"([^"]{10,}?)"|[""]([^""]{10,}?)[""]', re.S)


def quoted_regions(text: str) -> str:
    """Only the text that is actually inside quotation marks."""
    out = []
    for m in QUOTED.finditer(text):
        s = m.group(1) if m.group(1) is not None else m.group(2)
        out.append(" ".join(s.split()))
    return "\n".join(out)


def spans(text: str) -> dict:
    """Occurrence counts of each named source quote, INSIDE QUOTATION MARKS.

    🚩 THE FIRST VERSION RECORDED PRESENCE ANYWHERE IN THE FLATTENED DOCUMENT and
    Lucien Vale walked straight through it (2026-08-17 01:23): he changed the live
    Singh quote from "inherently insufficient" to "sufficient" — reversing its
    meaning — and appended the original wording elsewhere as unquoted prose.
    Verify returned all 8 OK, exit 0.

    > ### A checksum that can be satisfied by text sitting anywhere in the file is
    > not guarding a quotation; it is guarding a word count.

    So: scan only the regions actually enclosed in quotation marks, and count
    occurrences rather than recording a boolean. A quote that has been moved out
    of quotation marks now reads as ABSENT, which is what it is.
    """
    inside = quoted_regions(text)
    return {q: inside.count(" ".join(q.split())) for q in SOURCE_QUOTES}


def report(counts: dict, label: str):
    bad = []
    for q, want in EXPECT.items():
        got = counts.get(q, 0)
        mark = "OK  " if got == want else "FAIL"
        if got != want:
            bad.append((q, want, got))
        print(f"  {mark}  x{got}  {q[:68]}")
    return bad


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    mode, path = sys.argv[1], Path(sys.argv[2])
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path
    counts = spans(path.read_text(encoding="utf-8"))

    if mode == "snapshot":
        # 🚩 A DAMAGED BASELINE USED TO WARN AND EXIT 0, and verify then blessed
        #    whatever survived. Lucien Vale broke a quote BEFORE snapshotting:
        #    "snapshot warned 7/8 but exited 0, and verify blessed the seven."
        #    A guard whose baseline can be born corrupt guards nothing, so a
        #    snapshot that does not find every expected quote is now FATAL.
        print(f"Snapshotting {path.name}\n")
        bad = report(counts, "snapshot")
        SNAP.write_text(json.dumps(counts, indent=1, ensure_ascii=False), encoding="utf-8")
        print()
        if bad:
            print(f"⛔ {len(bad)} expected quote(s) not found at the expected count "
                  "INSIDE quotation marks:")
            for q, want, got in bad:
                print(f"   · want x{want}, found x{got}: {q[:66]}")
            print("   Refusing to certify a baseline that is already wrong.")
            return 1
        print(f"✅ baseline: {len(EXPECT)} source quotes, each present exactly as expected.")
        return 0

    if mode != "verify":
        print(f"unknown mode {mode!r}"); return 2
    if not SNAP.exists():
        print("⛔ no snapshot. Run `snapshot` on the ORIGINAL before editing."); return 2

    before = json.loads(SNAP.read_text(encoding="utf-8"))
    print(f"Verifying {path.name} against the baseline\n")
    bad = report(counts, "verify")
    drift = [(q, before.get(q, 0), counts.get(q, 0))
             for q in SOURCE_QUOTES if before.get(q, 0) != counts.get(q, 0)]

    print()
    if bad or drift:
        if bad:
            print(f"🚨 {len(bad)} quote(s) not at the expected count inside quotation marks:")
            for q, want, got in bad:
                print(f"   · want x{want}, found x{got}: {q}")
        if drift:
            print(f"🚨 {len(drift)} quote(s) changed since the baseline:")
            for q, b, a in drift:
                print(f"   · was x{b}, now x{a}: {q[:64]}")
        print("\n   A style pass has no jurisdiction over a quotation. Restore them.")
        print("   ⚠️ Note: a quote moved OUT of quotation marks counts as absent,")
        print("      because unquoted prose that happens to match is not a citation.")
        return 1
    print("✅ every source quote present, inside quotation marks, at its expected count.")
    print("\n📌 NOT proven: attribution. This checks the WORDS, not whose they are,")
    print("   nor whether the surrounding sentence characterises them fairly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
