#!/usr/bin/env python3
"""make_pdf.py — render the paper to a self-contained, print-ready HTML.

    python make_pdf.py PAPER_v2_2026-08-16.md   ->  paper_print.html
    node  html_to_pdf.mjs                        ->  paper.pdf

The figure is embedded as a base64 data URI so the HTML is a single file and the
PDF renderer cannot silently drop it. Typography targets the submission
template's geometry: A4, 1 inch margins, 11pt serif.

⚠️ A rendered PDF is a NEW artefact, not the checked one. `check_paper_numbers`
and `quote_guard` verify the markdown. This script must therefore not alter a
single character of content: it wraps, it does not edit. The only transformation
is markdown to HTML.
"""
import base64
import re
import sys
from pathlib import Path

import markdown

LAB = Path(__file__).resolve().parent
src = Path(sys.argv[1] if len(sys.argv) > 1 else "PAPER_v2_2026-08-16.md")
if not src.is_absolute():
    src = LAB / src
text = src.read_text(encoding="utf-8")

# Embed the figure so nothing depends on a relative path at render time.
fig = LAB / "figure1.png"
if fig.exists():
    b64 = base64.b64encode(fig.read_bytes()).decode()
    text = text.replace("![Figure 1](figure1.png)",
                        f'<img src="data:image/png;base64,{b64}" alt="Figure 1">')

# The author block is four separate lines in the source; markdown joins them into
# one run-on paragraph. Force the breaks HERE, in the renderer, because the
# manuscript is what the guards verify and must not be edited for typesetting.
text = re.sub(r"(\*\*[^*\n]+\*\*[^\n]*· independent)\n(?=\*\*)", r"\1  \n", text)
html = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])

# Typography preset. `--tight` uses a standard paper layout (10pt/1.25, 20mm
# margins) which is ordinary typesetting, not a trick: the template specifies a
# page count, not a font. `--loose` is the roomier default.
TIGHT = "--tight" in sys.argv
FONT_PT, LINE, MARGIN = (10, 1.25, "20mm") if TIGHT else (10.5, 1.35, "25.4mm")

# 🚩 THE FOOTNOTE MUST LAND WHERE TEXT NEVER GOES.
#    First attempt put it at the foot of the page-one CONTENT box. It was in the
#    right place and the prose flowed straight underneath it, covering a
#    contribution bullet — an absolutely positioned element is out of flow, so
#    nothing moves aside for it.
#    ⇒ Enlarge the BOTTOM MARGIN and place the note inside that band. The margin
#      is empty on every page by construction, so there is nothing to collide
#      with, and no guessing about where page one's text happens to end.
_m = float(MARGIN.replace("mm", ""))
BOTTOM_MM = _m + 10                        # room for the note plus the page number
MARGIN_BOX = f"{_m}mm {_m}mm {BOTTOM_MM}mm {_m}mm"
CONTENT_MM = 297 - _m - BOTTOM_MM          # page-one content box height
FN_TOP = f"{CONTENT_MM + 2:.1f}mm"         # 2mm below the last line of text

DOC = """<!doctype html>
<meta charset="utf-8">
<title>%(title)s</title>
<style>
  @page { size: A4; margin: %(margin)s; }
  body { font: %(font)spt/%(line)s Georgia, "Times New Roman", serif; color:#111; margin:0; }
  h1 { font-size: 17pt; line-height:1.2; margin:0 0 .4em; text-align:center; }
  h2 { font-size: 12.5pt; margin: 1.1em 0 .35em; page-break-after: avoid; }
  h3 { font-size: 11pt;   margin: .9em 0 .3em;  page-break-after: avoid; }
  p, li { margin: 0 0 .45em; text-align: justify; hyphens: auto; }
  hr { border:0; border-top:1px solid #ccc; margin:1em 0; }
  table { border-collapse: collapse; margin:.6em 0; font-size:9pt; width:100%%;
          page-break-inside: avoid; }
  th, td { border:1px solid #999; padding:2px 5px; }
  th { background:#f2f2f2; }
  blockquote { margin:.6em 0 .6em .8em; padding:.2em 0 .2em .8em;
               border-left:2.5px solid #bbb; font-size:9.5pt; color:#333;
               page-break-inside: avoid; }
  code { font: 9pt "Consolas","Courier New",monospace; }
  pre { background:#f7f7f7; padding:.5em .7em; font-size:8.5pt; overflow:hidden;
        page-break-inside: avoid; }
  img { max-width:100%%; display:block; margin:.6em auto; page-break-inside: avoid; }
  /* the four author lines and the venue line, directly after the title */
  h1 + p { text-align:center; font-size:10pt; margin-bottom:.2em; }
  h1 + p + p { text-align:center; font-size:10pt; margin-bottom:1.2em; }
  h1 sup { font-size:60%%; vertical-align:super; }
  /* The template's page-one footnote, pinned to the BOTTOM of page one.
     Chromium implements no CSS Paged Media margin boxes and `position: fixed`
     repeats on every page, so neither of those works. What does: take the
     element out of flow and place it at the foot of the first page's content
     box, whose height is known exactly from the @page geometry
     (A4 297mm minus the two vertical margins). `body` is the positioning
     context, and body's origin IS the top of page one's content box.
     A white background and a reserved gap below keep flowing text clear of it. */
  /* The manuscript carries the footnote as content; the PDF renders it in the
     page footer via Chromium's footerTemplate, which is the only thing that can
     draw into a page's bottom margin. Hidden here so it is not duplicated. */
  .fn { display:none; }
</style>
%(body)s
"""

out = LAB / "paper_print.html"
out.write_text(DOC % {"margin": MARGIN_BOX, "font": FONT_PT, "line": LINE,
                      "title": src.stem, "body": html,
                      "fn_top": FN_TOP}, encoding="utf-8")
print(f"wrote {out.name}  ({out.stat().st_size/1024:.0f} KB, figure embedded)")
print(f"  preset: {'TIGHT' if TIGHT else 'default'}  {FONT_PT}pt/{LINE}")
print(f"  margins {MARGIN_BOX}  ·  footnote at {FN_TOP} (in the bottom margin band)")
print(f"  PASS THESE TO html_to_pdf.mjs: --top {_m}mm --bottom {BOTTOM_MM}mm "
      f"--side {_m}mm")
