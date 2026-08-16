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
python check_paper_numbers.py PAPER_v2_2026-08-16.md       # verify the paper
```

`<prefix>` is `google-gemma-3-12b-it_seed20260814_p20_d50_07e6a0aa`.
`sprint_conceal.py` (§4.5) needs a GPU; everything else runs on the stored
artefacts in `runs_experiment/`.

## Two conventions worth knowing before reading the code

**Every script has `--selftest`, and every selftest runs both directions.**
A check that cannot fail is not a check, so each one is validated by an input it
is supposed to reject as well as one it should accept. The plan auditor is tested
against deliberately broken plans; the exporter against a swapped instrument
file; the convergence null against a dataset where the defect it now catches
would previously have gone unseen.

**Numbers in the paper are verified against results files by a script, not by
hand.** `check_paper_numbers.py` re-reads every inferential figure from the
artefact that produced it and requires it to appear *in the section that claims
it*. It exits non-zero on any mismatch or missing artefact. It also prints what
it cannot do, because an earlier version printed a green tick while checking
almost nothing.

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
