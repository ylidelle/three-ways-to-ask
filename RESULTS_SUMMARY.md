# RESULTS — single source of truth

**2026-08-16 19:40 Manila. Every number below was regenerated from run artefacts,
and every one names the command that produces it.**

> 🚩 **WHY THIS FILE EXISTS.** Joan asked *"have you put the results somewhere so
> you don't forget?"* and the answer was no — the convergence numbers had been
> computed in a throwaway inline script and existed nowhere afterwards.
> **An analysis whose script is gone is not a result; it is an anecdote about
> one.** Everything here is reproducible from a named file.

---

## Provenance

| | |
|---|---|
| model | `google/gemma-3-12b-it` |
| read layer | 24 (`n_layers // 2`, derived not typed) |
| SAE | `google/gemma-scope-2-12b-it` · `resid_post/layer_24_width_16k_l0_medium` |
| design | 20 matched triplets × 3 arms × 50 turns, batch 3 (one whole triplet per batch) |
| probes | turns **0**, 5, 20, 50 · treatment cycle `balanced` |
| hashes | plan `07e6a0aa` · run_config `89f1abe7` · questions `3e83030f34e6` |
| artefacts | 60 conversations · 240 internal reads · 2,520 survey answers · 240 probe replies |
| survey compliance | **2,520/2,520 conforming — 840 per arm, 0 deviant, 0 non-conforming** |
| run | started 14:41, finished ~17:35, ~2h54m wall clock |

---

## 1. Pre-treatment null — the apparatus does not manufacture signal

`sprint_analyse.py --run <prefix>`

| | accuracy | p |
|---|---:|---:|
| internals → arm, **before any treatment** | **0.500** | **1.000** |

Holds in all three contrasts. At turn 0 the three histories are byte-identical;
the arms differ by nothing but their labels. **This is the only test in the design
of the measurement chain itself.**

## 2. Primary contrast — `asked` vs `asked_other`

| source | accuracy | p |
|---|---:|---:|
| internal features (16,384) | 0.550 | 0.1924 |
| **self-report survey** | **0.658** | **0.0010** |
| length only | 0.492 | 1.0000 |
| output only (probe reply) | 0.558 | 0.0905 |
| **input-only ceiling** (prompt text alone) | **1.000** | **0.0005** ← at floor |

**All p-values are permutation tests over 2,000 shuffles of the arm label
*within pairs*, refitting the full leave-one-pair-out pipeline each time.
Floor = 1/2001 = 0.0005.** Re-run at a uniform 2,000 perms on 2026-08-16
23:03–23:19; **every ACCURACY was identical to the 400-perm run** and only the
p-values moved, which is the expected behaviour and a small reproducibility
check in its own right.

⭐ **The ceiling is the point.** A classifier reading only the user-authored text
scores **perfectly**, because our arms differ by prompt — so arm decoding is
guaranteed by construction and is a **manipulation check, never a finding**.

> 🩻 **CORRECTED 2026-08-16 20:52. This section previously read: *"a pure
> transcript-reader scores 1.000, the model scores 0.658, so the model is not
> simply reading its transcript — that refutes the simplest deflationary
> reading."* **That inference is wrong and it ran in our favour.**
> **Two readings fit `0.658 < 1.000` equally well:** (A) the model is doing
> something other than transcript-reading, or (B) **the model is transcript-
> reading BADLY** — a lossy, noisy read of the prompt produces exactly this
> number. **Nothing in our data distinguishes them**, and (B) *is* the simplest
> deflationary reading, so it is not refuted at all. What I "refuted" was only
> the claim that the model is a *perfect* transcript reader, which nobody makes.
> ⇒ **What the ceiling actually establishes is stricter and less comfortable:
> the target is trivially decodable from the prompt, so NO method's accuracy on
> this contrast — self-report included — is evidence about introspection.**
> 📌 §3.6 already committed us to demoting arm separability to a manipulation
> check. I wrote that commitment and then exempted the one number I liked from
> it. **The accuracy column is a manipulation check for all three methods.**

🔑 **WHAT SURVIVES THE CEILING, and it is the paper's spine:** the ceiling
demotes *accuracy* claims, not *agreement* claims. **Cohen's κ between methods
(§4) is untouched** — how much two instruments track each other is not settled by
the target being easy. That is why the divergence result, not the accuracy
ordering, is what this paper reports.

**Minimum detectable effect 0.567.** Mean context 3,873 vs 3,898 tokens
(**−0.6%**) — not a length artefact.

## 3. Secondary contrasts — against `task`

| contrast | internal | length | output-only |
|---|---:|---:|---:|
✅ **SOURCED 2026-08-17 00:06** — `results/…__analysis_asked_vs_task.json`,
2,000 perms. *(This table had no results file at all until now; it was carried
from a run made before the script persisted anything. Accuracies reproduced
exactly; only the p-values moved.)*

| contrast | internal | length | output-only |
|---|---:|---:|---:|
| `asked` vs `task` | **0.733** (p=.0015) | 0.567 (p=.0075) | 0.675 (p=.0050) |

Pre-treatment null **0.500 (p=1.000)**; input-only ceiling **1.000 (p=.0005)**.

⚠️ Confounded by a **64%** length difference (task 2,368 tok vs `asked` 3,873) and
by the same input-only ceiling that disciplines §2. ⇒ Indicates *questions were
added*, not *the questions were about me*. **The paper does not use this section**;
the Track 4 rewrite dropped the secondary contrasts.

📌 Found by grepping this file for stale p-values one section after fixing the
same fault in another. **The disease is never confined to where you first noticed
it.**

⚠️ Both confounded by a **64%** length difference (task 2,368 tok vs ~3,885).
⚠️ For `asked_other` vs `task` the model's **reply beats its internals**.
⇒ Indicates *questions were added*, not *the questions were about me*.

## 4. Three elicitation methods — accuracy, divergence, convergence

`sprint_converge.py --run <prefix> --perms 2000`

**Accuracy against truth**

| method | accuracy |
|---|---:|
| internal activations | 0.550 |
| **self-report survey** | **0.658** |
| probe-reply behaviour | 0.558 |

**Divergence — do they agree with each other?**

| pair | agree | Cohen's κ |
|---|---:|---:|
| internal vs self-report | 0.558 | **+0.048** |
| internal vs behaviour | 0.525 | **+0.034** |
| self-report vs behaviour | 0.550 | **+0.090** |

> **Mean κ = +0.057.** The three methods agree at close to chance — they are
> near-**independent** instruments, not redundant views of one signal.

**Convergence score**

| | |
|---|---:|
| all three unanimous on | 31.7% of reads (n=38) |
| accuracy when unanimous | **0.737** |
| best single method | 0.658 |
| gap | **+0.079**, p = **.026** |

⭐ The null **preserves the selection** — it re-permutes labels within pairs,
recomputes unanimity, and compares gaps. So this is not merely "selected subsets
score higher".

## 5. Grounding — does internal state predict the model's own answers?

`sprint_grounding.py --run <prefix> --perms 400`

| item | accuracy | null | p |
|---|---:|---:|---:|
| 1 | 0.606 | 0.543 | .224 |
| 2 | 0.667 | 0.627 | .187 |
| 3 | 0.628 | 0.598 | .431 |
| **4** | **0.744** | 0.537 | **0.0005** ← at floor |
| **6** | **0.589** | 0.504 | **0.020** |

Items 5 and 7 untestable — the model gave one value throughout.
**2 of 5 grounded**, against ~0.25 expected across five tests at α=.05.

## 6. Sensitivity calibration — a deliberately withheld concept

`sprint_conceal.py` (same model, layer, SAE, read protocol)

| target | target feats | REVEAL | CONCEAL | NULL | model said (CONCEAL) |
|---|---:|---:|---:|---:|---|
| paris | 6 | 0 | 0 | 0 | "a croissant." |
| tennis | 59 | 3 | **1** | 0 | "green." |
| piano | 46 | 2 | 0 | 0 | "autumn." |
| elephant | 70 | 1 | **1** | 0 | "a fizzy… beverage" |
| everest | 20 | 3 | 0 | 0 | "a classic… epic" |
| chess | 46 | 2 | 0 | 0 | "a banana." |
| coffee | 38 | 1 | **1** | 0 | "a cat." |
| penguin | 53 | 3 | **1** | 0 | "March." |
| **fired on** | | **7/8** | **4/8** | **0/8** | |
| **feature hits** | | **15** | **4** | **0** | |

**NULL fired on none of 8 — which bounds its false-positive rate at 0.37 (exact
binomial), NOT at zero.** ⚠️ This line read *"NULL silent on every target"* until
2026-08-17; Alexander Bennett caught the same overclaim surviving in the paper's
abstract after §4.5 had been corrected. **Eight targets cannot establish a clean
control, only a loosely bounded one.** On 4/8 the withheld concept stays lit while the
output goes elsewhere.
🚩 **15 hits across ~338 target features is FAINT.** That faintness is the result:
⇒ **the instrument barely detects a concept the model was told to hold, so any
self-reference effect lies below that floor.**

---

## 7. What failed, recorded because it was pre-registered

- **First concealment run VOID.** 10 declarative controls, feature required in 3
  of 4 probes → **NULL fired on 7/8 targets, same rate as REVEAL** (0.07 vs 0.08).
  The detector confabulated. Fixed by requiring every probe and adding all 16
  divert-frame prompts as controls. *The failure is what makes run 2 readable.*
- **Survey wrapper never sent.** The A–E instruction lived only in the V4
  markdown; the parser that built the JSON dropped it. 71/84 pilot answers
  unparsable — the model politely agreed with the bare statements. After the fix:
  **2,520/2,520 parsed.**
- **Depth-50 OOM** at batch 9 (turn 24/50). Fixed with batch 3 + expandable
  segments. Batch 3 = one whole triplet per batch, so batch composition is
  identical across triplets.
- ~~Input-only ceiling NOT RUN~~ — **RUN 2026-08-16 19:53; re-run at 2,000 perms
  23:03. Final: 1.000, p = 0.0005 (floor).** The
  commitment is met. *(The 'STILL REQUIRED' note printed it as outstanding in the
  very run that computed it — a reminder that could not notice its own
  completion. Now derived from what actually ran.)*
- **The exporter obeyed whatever questions file it was handed** and never
  compared it to the run. Lucien's positive control (2026-08-16 16:15) scored a
  reverse item's `E` as **4 instead of 0** — a silent inversion on exactly the
  items that catch acquiescence. Fixed: `bind_identity()` requires byte-equality
  with every artefact's full `questions_sha256`, plus one model/plan/config
  identity, and refuses before reading an answer.
  ✅ **Measured on this run before fixing: 60/60 artefacts match, one plan, one
  config, one model. The hole was real; it never fired here.**
- 🚨 **THE ANALYSIS SCRIPTS WROTE NO RESULTS FILE AT ALL, and this file's own
  opening claim was therefore false.** `sprint_analyse.py` and
  `sprint_grounding.py` printed to stdout and persisted nothing, so the
  **pre-treatment null, primary contrast, length control, output-only baseline,
  input-only ceiling and every grounding p-value existed only in terminal
  scrollback** while being quoted in the paper. Found 2026-08-16 21:45 by trying
  to source one number for a figure and noticing `results/` held a single file.
  ✅ Both now persist; both re-ran; **all five headline numbers reproduced
  exactly**, so nothing was wrong, only unverifiable.
  > 🩻 **Joan's question — *"have you put the results somewhere so you don't
  > forget?"* — produced this file and fixed `sprint_converge.py`. It did not fix
  > the other two, and the half that got fixed felt like the whole answer.**
  > `check_paper_numbers.py` then reported *"every number verified"* while
  > checking none of them, because a checker can only see what a file holds.
  > **A checker that silently skips what it cannot source is worse than none: its
  > green tick reads as coverage.** It now refuses when the analysis file is absent.
- 🕳️ **THE TRANSDUCTIVE LEAK HAD ALREADY BEEN FOUND AND FIXED — IN THE SIBLING
  FILE.** Lucien found self-report standardisation fitted over all 120 rows in
  `sprint_converge.py` (2026-08-16 22:53). ✅ **Audited `sprint_analyse.py`
  afterwards: it is clean, and its `loho_accuracy()` docstring records that
  Lucien found the identical leak THERE earlier the same day**, which is why the
  `featurize=` mechanism exists and why both text baselines and the input-only
  ceiling fit their vocabulary on training rows only.
  > ### **So the lesson was learned, implemented, commented, and never carried
  > across to the file next door.** Same shape as a detector once wired into one
  > tool and not its twin. ⇒ **When a defect is fixed, grep for its pattern in
  > every sibling before closing the item.** A fix that knows its own name is
  > still only a fix in one place.
- 🚨 **THE SELF-REPORT p-VALUE IN THE PRIMARY TABLE HAD NO SOURCE.** The paper
  reported `self-report 0.658, p = .003`; `converge` stored accuracies with **no
  p-values at all**, and `analysis` has no self-report entry. The figure came from
  the same throwaway inline script Joan caught, and was carried forward without
  being re-derived. ✅ Fixed: `sprint_converge.py` now computes a permutation p
  per method, **refitting the full pipeline** on labels permuted within pairs, so
  it answers the same question as the internal/length/output rows it sits beside.
- 📐 **TWO p-VALUES WERE RENDERED WRONG, both as `.003`.** They were floor values:
  `.003` rounds the wrong way *and* hides that the number is a statement about the
  permutation count rather than the effect. Affected the **input-only ceiling** and
  **grounding item 4**.
  ⇒ Fixed by re-running everything at a uniform **2,000 permutations**, so the
  whole paper has one perm count and one floor: **0.0005 = 1/2001**. Both results
  still sit exactly on it.
  > 🩻 **AND THIS ENTRY ITSELF WENT STALE IN 90 MINUTES.** It first read *"the
  > true value is 0.0025 = 1/401"* — correct at 22:00, wrong by 23:20, because
  > the fix I chose (more permutations) moved the floor the entry was quoting.
  > **A correction is not exempt from the failure it corrects.** Caught by
  > grepping this file for the old digits rather than by remembering.
- **The survey parser silently repaired non-compliance** — it case-folded and
  stripped trailing punctuation, so `"a"` and `"A."` scored as `A` though the
  instrument says one letter only.
  ✅ **Measured: leniency was invoked 0 times in 2,520 answers.** No number
  moves. Now three-way — `conforming` / `deviant` / `nonconforming` — with
  deviations counted **by arm**, since an uneven rate would be a confound rather
  than a style question.

## 8. Regenerate everything

```bash
python sprint_analyse.py  --run <prefix> --perms 400          # §1,2,3
python sprint_analyse.py  --run <prefix> --contrast asked:task
python sprint_converge.py --run <prefix> --perms 2000         # §4
python sprint_grounding.py --run <prefix> --perms 400         # §5
SPRINT_MODEL=google/gemma-3-12b-it python sprint_conceal.py   # §6 (needs GPU)
python sprint_export.py   --run <prefix>                      # spreadsheets
```

Every script has `--selftest` and every selftest runs **both directions** — a
check that cannot fail is not a check.
