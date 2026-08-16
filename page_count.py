#!/usr/bin/env python3
"""page_count.py — how long is the paper, using constants MEASURED in a layout
engine rather than invented.

    python page_count.py PAPER_v2_2026-08-16.md

🚩 WHY THIS EXISTS. For several hours I reported page counts from this formula:

    pages = words/600 + table_rows*0.022 + headings*0.012 + 0.35

Every constant was a guess. Joan set a 5-6 page target and made an editorial
decision on my number, so the guess was load-bearing. On 2026-08-17 00:52 I
measured all four in Chrome at the geometry a submission template uses
(A4, 1in margins, 11pt/1.15 serif, 159.2mm column):

    quantity            I assumed    MEASURED     off by
    words per page          600         765        28%   <- the big one
    pages per table row     0.022       0.0206     fine
    pages per heading       0.012       0.0327     2.7x, small absolute effect
    pages for the figure    0.35        0.19       derived from its real aspect

⇒ The paper was reported as **6.2 pages** when it was **5.3**. I trimmed ~120
words to satisfy a limit it had never exceeded, and one of those trims silently
dropped a comma from inside a verbatim quotation while another deleted two source
quotes from the paper entirely.

> ### A number I invent can send me to edit a quotation. That is the whole lesson:
> a free parameter is not just where a conclusion hides, it is where an ACTION
> comes from.

⚠️ WHAT THIS STILL CANNOT DO. These constants are measured, but for ONE geometry
and ONE font stack. A different template, font, or column width moves them. The
authoritative count is whatever the submission document itself reports once the
text is in it. **This is a good estimate, not the answer**, and it says so rather
than printing a bare number that will be read as certainty.
"""
import re
import sys
from pathlib import Path

# Measured 2026-08-17 in Chrome. A4, 1in margins, 11pt/1.15 Georgia,
# 159.2mm content column, 246.2mm content height (= 931px at 96dpi).
WORDS_PER_PAGE = 765
PG_PER_TABLE_ROW = 0.0206
PG_PER_HEADING = 0.0327
FIG_ASPECT = 3.35            # figure1.png, width/height
COLUMN_MM, PAGE_MM = 159.2, 246.2
PG_PER_FIGURE = (COLUMN_MM / FIG_ASPECT) / PAGE_MM

src = Path(sys.argv[1] if len(sys.argv) > 1 else "PAPER_v2_2026-08-16.md")
if not src.is_absolute():
    src = Path(__file__).resolve().parent / src
text = src.read_text(encoding="utf-8")

body, _, refs = text.partition("## References")
lines = body.splitlines()
words = len(re.findall(r"\S+", " ".join(
    l for l in lines if not l.strip().startswith("|") and not l.strip().startswith("#"))))
rows = sum(1 for l in lines if l.strip().startswith("|"))
heads = sum(1 for l in lines if l.strip().startswith("#"))
figs = len(re.findall(r"^!\[", body, re.M))
ref_words = len(re.findall(r"\S+", refs))

pages = (words / WORDS_PER_PAGE + rows * PG_PER_TABLE_ROW
         + heads * PG_PER_HEADING + figs * PG_PER_FIGURE)

print(f"{src.name}\n")
print(f"  prose      {words:5d} words   {words/WORDS_PER_PAGE:5.2f} pg")
print(f"  tables     {rows:5d} rows    {rows*PG_PER_TABLE_ROW:5.2f} pg")
print(f"  headings   {heads:5d}         {heads*PG_PER_HEADING:5.2f} pg")
print(f"  figures    {figs:5d}         {figs*PG_PER_FIGURE:5.2f} pg")
print(f"  {'':-<38}")
print(f"  ESTIMATE   {pages:5.1f} pages excluding references")
print(f"             {pages + ref_words/WORDS_PER_PAGE:5.1f} pages including them")
print("\n  Constants measured in a layout engine, not assumed. But measured for")
print("  ONE geometry: the real count is whatever the submission document says.")
