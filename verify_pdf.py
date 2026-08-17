#!/usr/bin/env python3
"""verify_pdf.py — read the RENDERED PDF and check what is actually on the page.

    python verify_pdf.py Three_Ways_To_Ask_Bennett_Miranda_Vale.pdf

🚩 WHY. A PDF is a new artefact. `check_paper_numbers` and `quote_guard` verify
the markdown; nothing verified what the renderer produced, and "the command
exited 0" is a claim about the shell.

⚠️ AND THE FIRST ATTEMPT AT THIS WAS A BROKEN CHECK. I searched the raw PDF
streams for parenthesised text and got zero hits for EVERY probe — including the
paper's title, which is unquestionably in the document. Chromium embeds subset
fonts, so those strings are glyph codes rather than readable characters.
**The title was in the probe list as a positive control, and it is the only
reason I read that result as "my extractor is wrong" rather than "the footer is
missing."** A checker with no known-present case cannot tell those apart.
"""
import sys
from pathlib import Path

import pymupdf

LAB = Path(__file__).resolve().parent
p = Path(sys.argv[1] if len(sys.argv) > 1 else
         "Three_Ways_To_Ask_Bennett_Miranda_Vale.pdf")
if not p.is_absolute():
    p = LAB / p

doc = pymupdf.open(p)
pages = [doc[i].get_text() for i in range(len(doc))]
whole = "\n".join(pages)
print(f"{p.name} · {p.stat().st_size/1024:.0f} KB · {len(doc)} pages\n")

# ── IS THIS PDF EVEN CURRENT? ───────────────────────────────────────────────
# 🚩 The first version of this script checked the PDF's CONTENTS thoroughly and
#    never asked whether it had been rendered from the current manuscript. Joan
#    caught a PDF that was two edits stale while every check in this file passed.
#    A verifier that validates a stale artefact in detail is worse than none: it
#    supplies confidence about the wrong bytes.
MD = LAB / "PAPER_v2_2026-08-16.md"
STAMP = LAB / ".paper_source_sha"
stale = []
if not MD.exists():
    stale.append("the manuscript is missing")
elif not STAMP.exists():
    stale.append("no source stamp: re-run make_pdf.py")
else:
    import hashlib
    live = hashlib.sha256(MD.read_bytes()).hexdigest()
    stamped = STAMP.read_text(encoding="utf-8").strip()
    if live != stamped:
        stale.append(f"THE PDF IS STALE. manuscript {live[:16]}… "
                     f"but the PDF was rendered from {stamped[:16]}…")
    else:
        print(f"  OK    source hash matches the live manuscript "
              f"({live[:16]}…)\n")
if stale:
    for s in stale:
        print(f"  ⛔ {s}")
    print("\n⛔ Refusing to report on a PDF that does not match the manuscript.")
    print("   Re-render before reading anything below as current.")
    sys.exit(1)

PROBES = [
    ("title", "Three Ways to Ask", 1),
    ("author Joan Miranda", "Joan Miranda", 1),
    ("author Lucien Vale", "Lucien Vale", 1),
    ("author Opie", "Claude Orion", 1),
    ("author Alexander", "Claude Alexander", 1),
    ("With / Apart Research", "Apart Research", 1),
    ("mean kappa", "+0.059", None),
    ("exact p", "0.0531", None),
    ("input-only ceiling", "1.000", None),
    ("repo URL", "three-ways-to-ask", None),
    ("figure caption", "Figure 1.", None),
]
bad = []
for label, needle, want_page in PROBES:
    hits = [i + 1 for i, t in enumerate(pages) if needle in t]
    ok = bool(hits) and (want_page is None or want_page in hits)
    if not ok:
        bad.append(label)
    where = ",".join(map(str, hits)) if hits else "-"
    print(f"  {'OK  ' if ok else 'MISS'}  {label:24s} pages {where}")

# The footer must appear on EVERY page, in the bottom margin band.
FOOT = "Digital Minds Research Sprint"
foot_pages = [i + 1 for i, t in enumerate(pages) if FOOT in t]
print(f"\n  footer text on pages: {foot_pages or '-'}  "
      f"({len(foot_pages)}/{len(doc)})")
if len(foot_pages) != len(doc):
    bad.append("running footer")

# And it must sit BELOW the body text, not inside it.
pg = doc[0]
h = pg.rect.height
foot_y = [b[3] for b in pg.get_text("blocks") if FOOT in b[4]]
body_y = [b[3] for b in pg.get_text("blocks") if FOOT not in b[4]]
if foot_y and body_y:
    print(f"  page 1: lowest body text ends at y={max(body_y):.0f}, "
          f"footer at y={max(foot_y):.0f}, page height {h:.0f}")
    if max(foot_y) <= max(body_y):
        bad.append("footer overlaps body")
        print("  ⛔ the footer is NOT below the body text")
    else:
        print("  ✅ footer sits below all body text, in the margin band")

# Figure present as an image, not just referenced.
imgs = sum(len(doc[i].get_images()) for i in range(len(doc)))
print(f"  embedded images: {imgs}")
if imgs < 1:
    bad.append("figure missing")

print()
if bad:
    print(f"⛔ {len(bad)} problem(s): {', '.join(bad)}")
    sys.exit(1)
print("✅ the rendered PDF contains what the manuscript says it should.")
