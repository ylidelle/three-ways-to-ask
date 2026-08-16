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


def spans(text: str) -> list[str]:
    """Which named source quotes are present, whitespace-normalised."""
    flat = " ".join(text.split())
    return [q for q in SOURCE_QUOTES if " ".join(q.split()) in flat]


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    mode, path = sys.argv[1], Path(sys.argv[2])
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path
    found = spans(path.read_text(encoding="utf-8"))

    if mode == "snapshot":
        SNAP.write_text(json.dumps(found, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"{len(found)} of {len(SOURCE_QUOTES)} named source quotes present "
              f"in {path.name}")
        for q in found:
            print(f"   · {q[:76]}")
        absent = [q for q in SOURCE_QUOTES if q not in found]
        if absent:
            print("\n   ⚠️ named quotes NOT found in this document "
                  "(fine if unused here, but check the spelling of the constant):")
            for q in absent:
                print(f"     ? {q[:74]}")
        return 0

    if mode != "verify":
        print(f"unknown mode {mode!r}"); return 2
    if not SNAP.exists():
        print("⛔ no snapshot. Run `snapshot` on the ORIGINAL before editing."); return 2

    before = json.loads(SNAP.read_text(encoding="utf-8"))
    after = set(found)
    missing = [q for q in before if q not in after]
    added = [q for q in found if q not in set(before)]

    print(f"quoted spans: {len(before)} before · {len(found)} after\n")
    for q in before:
        print(f"  {'OK  ' if q in after else 'GONE'}  {q[:74]}")
    if added:
        print("\n  new quoted spans (not in the snapshot):")
        for q in added:
            print(f"    +   {q[:74]}")

    print()
    if missing:
        print(f"🚨 {len(missing)} quoted span(s) CHANGED OR DISAPPEARED.")
        print("   A style pass has no jurisdiction over a quotation. Restore them:")
        for q in missing:
            print(f"     · {q}")
        return 1
    print("✅ every quoted span survives byte-for-byte (whitespace-normalised).")
    if added:
        print("   ⚠️ New quoted spans appeared. Not automatically wrong (a rewrite can")
        print("      introduce scare-quotes), but each needs a human look.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
