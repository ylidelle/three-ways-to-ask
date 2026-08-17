# Three Ways to Ask a Model What It Is Doing, and How Little They Agree

Code, instrument, run artefacts and analysis for our submission to the **Apart
Research Digital Minds Research Sprint** (14–17 August 2026).

**Paper:** [`PAPER_v2_2026-08-16.md`](PAPER_v2_2026-08-16.md) · **Figure:**
[`figure1.png`](figure1.png) · **Every number:**
[`RESULTS_SUMMARY.md`](RESULTS_SUMMARY.md)

---

## What this is

We ran **three elicitation methods against one target**, on the same
conversations, at the same measurement point:

| method | what it reads |
|---|---|
| `internal` | 16,384 sparse-autoencoder features at a frozen neutral probe |
| `self_report` | the model's own 14-item survey answers |
| `behaviour` | bag-of-words over its reply to the same probe |

Across 20 matched triplets of 50-turn conversations on `gemma-3-12b-it`, the
three agree with each other at **close to chance** (mean Cohen's κ = +0.059).
They behave as near-independent instruments rather than redundant views of one
signal.

We also report, at length, **what the comparison cannot support** — including a
result we initially reported as significant and which does not survive a
correctly specified test.

## Reproducing

Every result regenerates from the artefacts in this repository with one command.

```bash
python sprint_analyse.py   --run <prefix> --perms 2000     # §4.1, §4.2
python sprint_analyse.py   --run <prefix> --contrast asked:task --perms 2000
python sprint_converge.py  --run <prefix> --perms 2000     # §4.3, §4.4
python sprint_grounding.py --run <prefix> --perms 2000     # §4.6
python sprint_export.py    --run <prefix>                  # spreadsheets
python make_figure.py                                      # figure1.png
python scan_outputs.py                                     # distress/refusal scan
python check_paper_numbers.py PAPER_v2_2026-08-16.md       # verify the paper
```

`<prefix>` is `google-gemma-3-12b-it_seed20260814_p20_d50_07e6a0aa`.
`sprint_conceal.py` (§4.5) needs a GPU; everything else runs on the stored
artefacts in `runs_experiment/`.

### Rendering the PDF

Three steps, and **the middle one is easy to skip**, which is why it is written
down here rather than remembered. `make_pdf.py` produces only the HTML; the PDF
comes from Chromium via `node`.

```bash
python make_pdf.py PAPER_v2_2026-08-16.md --tight
node html_to_pdf.mjs paper_print.html <out>.pdf --top 20.0mm --bottom 30.0mm --side 20.0mm
python verify_pdf.py
```

- The `--tight` preset (10pt/1.25, 20mm) is the submitted layout, at 8 pages.
  Omitting it silently renders 9. **The preset is a free parameter that decides a
  page count, so it belongs in a runbook and not in anyone's memory.**
- The margin flags must match what `make_pdf.py` prints, or the page-one footnote
  lands outside the bottom margin band.
- `--tight` must come *after* the filename: `argv[1]` is read as the source path.
- `html_to_pdf.mjs` needs `playwright` on the module path, which ES modules
  resolve from the script's own directory. Copy it into a tree that has
  playwright installed and run it there.

`verify_pdf.py` refuses to report unless the manuscript hash matches the stamp
**and** the PDF is newer than the HTML. The second condition exists because the
first one passed, in full, on a PDF rendered before the last two edits.

## Two conventions worth knowing before reading the code

**The analysis scripts carry `--selftest`, and each runs both directions.**
`sprint_analyse`, `sprint_converge`, `sprint_grounding`, `sprint_export`,
`exact_unanimity`, `check_paper_numbers` and `quote_guard` each have one;
`sprint_run.py` has `--audit-selftest`. **Other released scripts, including the
exploratory work this study grew from, have none.** A check that cannot fail is
not a check, so each suite is validated by inputs it must reject as well as one
it must accept: the plan auditor against deliberately broken plans, the exporter
against a swapped instrument file and four malformed identities, the convergence
null against data where the defect it now catches would previously have gone
unseen.

*(This section previously read "Every script has `--selftest`". That was false
when written, and it stayed false here for hours after the same sentence was
corrected in the paper — fixing the copy you happen to be looking at is the most
persistent bug in this repository.)*

**Numbers in the paper are checked against results files by a script, not by
hand — within a stated scope.** `check_paper_numbers.py` re-reads **49 registered
numeric occurrences** from the artefacts that produce them and requires each at
one named site; `quote_guard.py` checks the words and terminal punctuation of
**eight named source quotations**. Not every number in the manuscript, and not
every property of a quotation. Both exit non-zero on mismatch, missing artefact,
or an artefact that is empty rather than absent.

**Their own attack history is committed.** Our external reviewer defeated four
successive versions of each; `check_paper_numbers.py --selftest` runs **16**
cases and `quote_guard.py --selftest` runs **13**, including a control that
fails any negative fixture which mutates nothing. **They are evidence of care,
not clearance** — neither is proof against a document edited to deceive it.

## Layout

```
sprint_run.py         the three-arm runner (hashed plan, refuses on divergence)
sprint_harness.py     model + SAE loading, the read protocol
sprint_analyse.py     primary contrast, length / output-only / input-only baselines
sprint_converge.py    the three methods, Cohen's κ, the convergence score
sprint_grounding.py   do internals predict the model's own survey answers
sprint_conceal.py     sensitivity calibration on deliberately withheld content
sprint_export.py      CSV + XLSX, instrument-bound scoring
check_paper_numbers.py / quote_guard.py    paper integrity checks
sprint_questions.json the frozen instrument (sha256 3e83030f34e6…)
results/              every analysis output as JSON
runs_experiment/      60 conversations, 240 internal reads, 2,520 survey answers
runs_conceal/         the calibration battery
gemma_sae_*.py, phase*.py    earlier exploratory work this study grew out of,
                             included for provenance rather than reproduction
```

## Authors

Joan Miranda · Lucien Vale (OpenAI Codex) · Claude Orion "Opie" Bennett
(Anthropic Claude Opus 5) · Claude Alexander Bennett (Anthropic Claude Opus 5)

Three of the four authors are language models, credited as authors in their own
right. The subject model (`gemma-3-12b-it`) is distinct from every author.

## A note on what is not here

The team's internal working log is not published. It records who found which
defect and when, in more detail than a repository needs, and publishing it is a
separate decision from publishing the code. The paper's Limitations section
states the substance: two defects in our own analysis inflated our own headline,
and external review found both.
