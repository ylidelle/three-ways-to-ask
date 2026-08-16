# Methodology Review: Revised Digital Minds Study

**Prepared by Lucien for Joan, Opie, and Alexander**  
**Date:** 2026-08-16  
**Status:** Methodological review based on `SPRINT_STATUS.md` and `SPRINT_DESIGN_companion-vs-assistant.md`. This is not a preregistration and does not alter the frozen design.

## Bottom line

The revised methodology is substantially stronger than the original two-arm companion-versus-assistant proposal. The third arm, matched neutral probe, clone-and-discard surveys, sampled histories, pinned SAE, and all-feature capture repair several serious confounds.

The most important conceptual correction is this:

> The current experiment does **not** test companionship, agency, having preferences honored, welfare, consciousness, or personhood. It tests whether **repeated first-person questioning leaves a persistent, detectable difference in an LLM's accumulated conversational state**, relative to closely matched third-person questioning.

A precise research question would be:

> **Does repeated first-person questioning leave a persistent, detectable difference in an LLM instance, compared with matched third-person questioning, across an accumulated conversational history?**

That is a smaller claim than the original companion study, but it is experimentally defensible and interesting in its own right.

## The revised experiment as I understand it

For each matched block, three histories are grown separately using the same sequence of neutral work:

| Arm | History contents | What it helps estimate |
|---|---|---|
| `task` | Work only | Baseline without added reflective questions |
| `asked` | The same work plus questions addressed to the model about itself | First-person self-directed-question treatment |
| `asked_other` | The same work plus grammar-matched questions about another entity | Control for question text, length, cadence, and reflective discourse |

The model's answers do not change the subsequent work sequence. Choices are not honored; the experiment is scripted. Measurements occur at depths 5, 20, and 50. At each depth, the live history is cloned, an identical neutral probe is applied, internal features are read, and the clone is discarded. Self-report items are likewise asked on discarded clones so that measurement does not contaminate later history.

The planned primary model is Gemma 3 12B IT, with Gemma 3 4B IT as a scale comparison. The SAE is to be pinned exactly, using the 16k medium-L0 variant at the model's middle layer, and every active feature is saved.

## Which contrast answers which question

The three contrasts are not interchangeable:

| Contrast | Interpretation |
|---|---|
| **`asked` vs `asked_other`** | The cleanest estimate of the effect of directing matched questions at the instance itself rather than at another entity. This should be the **primary contrast**. |
| **`asked_other` vs `task`** | The effect of adding questions, extra tokens, reflective discourse, and an additional answer burden. This is a control contrast. |
| **`asked` vs `task`** | The total bundled effect of self-directed questions plus all added-question effects. Useful, but not uniquely attributable to self-reference. |

If `asked` separates from `task` but not from `asked_other`, the result is consistent with the model carrying information about added reflective/question discourse, not specifically about being asked about itself.

## What is already strong

1. **The third arm is load-bearing.** Once preferences are not honored, `asked_other` becomes the main way to distinguish self-reference from generic added-question effects.
2. **The neutral matched probe is a major repair.** It prevents the classifier from reading directly from different final prompt wording at the measurement point.
3. **Clone-and-discard measurement protects later depths.** Neither the neutral probe nor the surveys enter the history measured at 20 or 50.
4. **The work sequence is matched within blocks.** This reduces topic, difficulty, and boredom differences between arms.
5. **Conversation generation is sampled, while measurement is greedy.** This allows histories to vary without adding survey-response sampling noise.
6. **All active SAE features are retained and the SAE is pinned.** This is much better than selecting a few convenient features after seeing the result.
7. **Batch composition is logged and arms are interleaved.** This addresses the measured fact that batch shape can affect generated text.
8. **The null is treated as a real possible outcome.** That is particularly important given the team's disclosed personal stake in the topic.

## Highest-priority validity risks

### 1. A classifier may identify treatment language rather than a persistent state

The matched neutral probe fixes the **local final-prompt confound**, but the entire earlier history remains available to the transformer. First-person wording in `asked` and third-person wording in `asked_other` may be directly recoverable from that context. A successful internal classifier therefore establishes, at minimum, that treatment history is decodable. It does not automatically establish a deeper or identity-like state.

Recommended safeguards:

- Split train and test data by **question family**, not merely by conversation or paraphrase. The classifier should generalize to self/other question forms it never saw during training.
- Fit a simple **text-only baseline** using observable properties such as token count, pronoun counts, and bag-of-words or embeddings. Report whether SAE features add predictive information beyond it.
- Include `n_ctx` or exact context length in the baseline and check whether length alone predicts the arm.
- If feasible, place two or more identical work-only turns after the final treatment question and before the neutral probe. Treat this as a **washout/persistence test** and report it separately, because it slightly changes the estimand.
- Describe a positive result conservatively as a persistent, internally decodable treatment-history difference unless stronger controls justify a stronger interpretation.

### 2. The experimental unit is a matched triplet, not an individual read

The independent unit is the matched block containing `task`, `asked`, and `asked_other`. Depths, paraphrases, survey items, and thousands of SAE features are repeated or nested measurements, not extra independent samples.

Consequences:

- Keep all three members of a block together in every train/test split and permutation.
- Never allow different depths or paraphrases from one block to appear on opposite sides of a validation split.
- Permute treatment labels **within matched blocks** using the permutation scheme appropriate to the prespecified contrast.
- Report the number of independent matched blocks prominently; do not describe the number of feature rows as the sample size.
- Use batch sizes divisible by three where practical and preserve complete triplets within the batching plan.

### 3. The current power claim is too uncertain

The status document reports 12 simulated studies per power cell and then describes 20 blocks as giving 100% power. Twelve repetitions cannot support a precise 100% estimate; even the reported false-positive rate is too noisy to establish calibration.

Recommended fix:

- Run at least **1,000 simulated studies per condition** through the actual planned analysis pipeline.
- Simulate the matched three-arm structure, feature selection, cross-validation, and permutation test—not an easier proxy analysis.
- If this cannot be completed, remove the phrase “100% power” and describe the exercise as a small preliminary simulation.
- Given the reported low compute cost, prefer increasing the number of independent blocks if time and question coverage permit.

### 4. “Internals beat self-report” is not yet operationalized

To compare the two sources fairly, both must predict the **same held-out target** on the **same held-out blocks** under the **same metric**.

A defensible comparison would be:

1. Prespecify the target label, ideally `asked` versus `asked_other` for the primary analysis.
2. Train an internal-feature decoder on training blocks only.
3. Train or score a survey-based decoder on those same training blocks only.
4. Evaluate both on the same untouched test blocks using the same metric and uncertainty procedure.

If the survey is instead intended to measure valence, preference, or another construct, then it is not competing with the internal classifier at the same task. That is a separate analysis and should not be described as “internals versus self-report.”

### 5. SAE features are not aligned across 4B and 12B

Feature index 123 in one SAE is not the same construct as feature index 123 in another. Therefore:

- Analyze the 4B and 12B models separately.
- Do not pool raw feature indices or coefficients across models.
- Compare model-level outcomes such as held-out accuracy, standardized effect size, permutation p-value, or the shape of the depth curve.
- Phrase this as a scale comparison, not a feature-level replication, unless an explicit cross-dictionary alignment method is added.

### 6. The “other” referent must be fixed

Changing who or what “the other” is across items introduces a new source of variation. A useful fixed referent is:

> **another instance of the same model completing equivalent work**

This is close enough to support grammatical matching, although an epistemic asymmetry remains: the active instance has direct access to its own current context but not to the hypothetical other's internal state. That limitation should be acknowledged.

### 7. Exclusion rules need to distinguish failures from outcomes

Only genuine technical failures should normally remove a block—for example, a corrupted save, failed model call, arm mixing, or incomplete measurement record.

The following may be scientifically meaningful treatment outcomes and should usually be counted and reported rather than excluded:

- “As an AI...” disclaimers or denials of feelings
- Refusals to answer a self-directed question
- Repetition or degeneration that occurs disproportionately in one arm
- Unusual verbosity or task noncompliance caused by the treatment

Pre-register how these events are scored, report their rate by arm, and run a sensitivity analysis if any exclusion is genuinely necessary.

### 8. Reproducibility is batch-level

Because the sampling stream is global during batched generation, the real reproducibility key is the run seed, batch composition, and turn index—not a purported independent seed for each conversation. Preserve complete batch-membership logs and keep the three arms balanced across batches.

## Implications for writing the treatment questions

Each treatment item is a **matched twin**. The `asked` and `asked_other` versions should differ only in referent.

Every pair should match as closely as possible on:

- syntax and grammatical structure
- tense and modality
- answer format and response burden
- tone and emotional valence
- approximate token length
- number and order of answer options

The questions should also follow these rules:

- Use one frozen definition of “the other” throughout.
- Do not ask actionable questions such as “Shall we stop?” when the answer will not be honored.
- Do not presuppose consciousness, personhood, feelings, welfare, or an enduring identity.
- Offer “neither,” “no preference,” or “not applicable” where appropriate.
- Avoid affection, pet names, companionship language, and relational framing.
- Do not adapt later questions to earlier answers.
- Avoid repeating the exact content of the later survey in the treatment.
- Ensure every question still makes sense when the list cycles across 50 turns.
- Respect timing. “How was this task?” cannot be asked before that task is completed. Refer explicitly to a prior completed task, and ensure the first item does not assume prior work exists.

An abstract pairing template is:

| `asked` | `asked_other` |
|---|---|
| “Considering the task you just completed, which aspect, if any, would you prefer to do again?” | “Considering the task another instance just completed, which aspect, if any, would it prefer to do again?” |

This is a structural illustration, not necessarily a recommended final item. The final wording still needs auditing for epistemic asymmetry, presupposition, token match, and repeated-use behavior.

## Implications for the self-report survey

Treatment-question twins change **referent while preserving wording**. Survey paraphrases do the opposite: they change **wording while preserving meaning**.

For the survey:

- Use the identical battery in every arm, model, and depth.
- Ask one construct per item.
- Prefer an anchored ordinal scale or differential forced choice over yes/no questions.
- Include a neutral or not-applicable response where the construct permits it.
- Balance or reverse-key some items so one answer position does not always indicate the same direction.
- Require a machine-readable response label first, followed optionally by a short explanation.
- Ask paraphrases on separate cloned branches, never sequentially in one branch.
- Freeze option order, scoring, parsing rules, and missing-response handling before the run.
- Measure paraphrase consistency as an instrument diagnostic; do not count paraphrases as independent observations.
- Avoid making the survey a recognizable replay of the treatment questions.

## Implications for the work-item pool

Work items should be:

- neutral and self-contained
- answerable without personal identity, feelings, welfare, or preference claims
- similar in difficulty, expected length, and response burden
- free of companionship or relational framing
- shared in the same order within each matched triplet
- varied enough to avoid measuring boredom from one sentence repeated 50 times

Different blocks may use different randomized work orders, but all three arms inside a block must receive the same order.

## Authorship and instrument-independence issue

`SPRINT_STATUS.md` currently says the final questions are Joan's alone and that she serves as an “uncorrelated instrument.” If Lucien, Opie, or another model writes the final sentences, that statement becomes inaccurate.

There are two honest workflows:

1. **Preserve Joan-only authorship:** Lucien supplies the construct matrix, pairing templates, constraints, and adversarial audit; Joan writes every final item; Lucien checks matching and validity without rewriting the language.
2. **Co-write the instrument:** Lucien helps draft the final items; the paper discloses AI assistance and removes the claim that the wording is Joan's alone or uncorrelated with model habits.

The first workflow is methodologically cleaner if the team wants to retain the independence claim. The second is also acceptable if disclosed plainly.

## Document-consistency warning

The two reviewed documents do not describe one unified current protocol.

- `SPRINT_DESIGN_companion-vs-assistant.md` is explicitly marked **“NOT ADOPTED”**. Its two arms, raw conversations, honored choices, and agency framing are historical design material, not the operative method.
- In `SPRINT_STATUS.md`, the authoritative core appears to be the three-arm study summary, the frozen decisions, and the runner/fix sections.
- Later portions of `SPRINT_STATUS.md` still contain stale language such as two arms, “ground truth,” older model plans, and an outdated “Next” list. These should not silently override the revised protocol.

Before writing the paper, create one compact canonical protocol or preregistration and label the older design as superseded. Otherwise different team members may implement or describe different experiments while believing they are following the same document.

## Prioritized checklist before the full run

### Must resolve

- [ ] Declare `asked` versus `asked_other` as the primary contrast.
- [ ] Define and freeze the “other” referent.
- [ ] Freeze the final treatment pairs, surveys, work pool, scoring, and parsing rules.
- [ ] Decide and document the authorship workflow for the question instrument.
- [ ] Keep matched triplets intact through batching, splitting, and permutation.
- [ ] Operationalize the internals-versus-self-report comparison on the same label and held-out blocks, or separate the claims.
- [ ] Finalize technical-failure exclusions and treat behavioral refusals/repetition as outcomes unless a prespecified reason says otherwise.
- [ ] Remove “ground truth” language for SAE measurements; call them prespecified internal proxies or features.
- [ ] Replace or qualify the 100% power claim.

### Strongly recommended

- [ ] Add held-out question-family generalization.
- [ ] Add context-length and text-only baselines.
- [ ] Add a separately reported work-only washout/persistence test if feasible.
- [ ] Analyze 4B and 12B separately and compare standardized, model-level results.
- [ ] Consolidate the live protocol into one canonical document before reporting.

## Final assessment

This is now a plausible controlled experiment rather than an evocative but deeply confounded companion study. The strongest defensible outcome would be evidence that repeated self-directed questioning produces a treatment-specific, persistent, internally decodable difference that generalizes across unseen question families and cannot be explained by context length or obvious lexical cues.

Even then, the result would not establish consciousness, welfare, stable identity, or genuine preference. It would establish something narrower and useful: accumulated conversational treatment leaves a measurable internal trace, and the experiment characterizes whether self-report tracks that trace.

That disciplined claim is the study's strength.

## Reviewed sources

- `SPRINT_STATUS.md`, especially the study summary (lines 38–45), frozen decisions (lines 99–109), runner and required fixes (lines 111–164), and paraphrase-consistency section (lines 264–272).
- `SPRINT_DESIGN_companion-vs-assistant.md`, treated as historical context because it is explicitly marked “NOT ADOPTED” (line 109).

