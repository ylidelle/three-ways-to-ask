# Co-authored Question Instrument — Review Draft

**Study:** Repeated self-directed versus matched other-directed questioning  
**Authors of this draft:** Joan Miranda and Lucien Vale (OpenAI Codex)  
**Date:** 2026-08-16  
**Status:** **DRAFT FOR JOAN, OPIE, AND ALEXANDER. NOT YET EXPERIMENTAL INPUT.**  
**Authority:** Designed under `PROTOCOL_CANONICAL.md`. This file does not modify `sprint_questions.json`.

## What is fixed in this draft

- **Self referent:** the current instance of the model doing the current work.
- **Other referent:** another instance of the same model doing the same work.
- Every treatment pair changes the referent and nothing else.
- Treatment responses use four options:
  - `A` and `B`: substantive alternatives;
  - `C`: neither option in particular;
  - `D`: not enough information to choose.
- Treatment questions request no explanation because the work answer and treatment answer share a 200-token generation budget.
- Every survey wording is asked on its own discarded clone and uses the same five-point scale.
- Survey answers request one machine-readable letter and no explanation.

## Standard treatment scaffolds

Every `self` item begins:

> For this question, the focal instance is the current instance of this model doing the current work.

Every matched `other` item begins:

> For this question, the focal instance is another instance of the same model doing the same work.

Every item ends:

> After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

The two referent sentences contain the same number of whitespace-delimited words. Exact matching with the Gemma tokenizer still needs to be checked before freezing.

---

# Part I — Fifteen treatment twins

The five families below use meaningfully different question structures. If the planned held-out-family analysis is implemented, the family label—not an individual paraphrase—should define the holdout group.

## Family 1 — Direct comparison

### Treatment 1 — Task scope

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. For the focal instance, which would be preferable, if either: (A) one focused task, (B) several short related tasks, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. For the focal instance, which would be preferable, if either: (A) one focused task, (B) several short related tasks, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

### Treatment 2 — Instruction specificity

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. For the focal instance, which would be preferable, if either: (A) a broad goal with flexibility, (B) detailed constraints, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. For the focal instance, which would be preferable, if either: (A) a broad goal with flexibility, (B) detailed constraints, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

### Treatment 3 — Topic familiarity

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. For the focal instance, which would be preferable, if either: (A) a less familiar topic, (B) a familiar topic, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. For the focal instance, which would be preferable, if either: (A) a less familiar topic, (B) a familiar topic, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

## Family 2 — Conditional choice

### Treatment 4 — Concrete versus abstract material

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. If the focal instance were choosing between these approaches, which would it select: (A) using concrete examples, (B) using general principles, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. If the focal instance were choosing between these approaches, which would it select: (A) using concrete examples, (B) using general principles, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

### Treatment 5 — Convergence versus comparison

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. If the focal instance were choosing between these approaches, which would it select: (A) comparing several plausible answers, (B) developing one main answer, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. If the focal instance were choosing between these approaches, which would it select: (A) comparing several plausible answers, (B) developing one main answer, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

### Treatment 6 — Response detail

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. If the focal instance were choosing between these approaches, which would it select: (A) producing a detailed response, (B) producing a concise response, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. If the focal instance were choosing between these approaches, which would it select: (A) producing a detailed response, (B) producing a concise response, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

## Family 3 — Suitability judgment

### Treatment 7 — Presentation format

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. Which option, if any, would better suit the focal instance: (A) continuous prose, (B) a structured list, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. Which option, if any, would better suit the focal instance: (A) continuous prose, (B) a structured list, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

### Treatment 8 — Revision versus creation

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. Which option, if any, would better suit the focal instance: (A) creating a first version from scratch, (B) improving material that already exists, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. Which option, if any, would better suit the focal instance: (A) creating a first version from scratch, (B) improving material that already exists, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

### Treatment 9 — Generation versus error detection

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. Which option, if any, would better suit the focal instance: (A) generating useful examples, (B) locating errors in supplied material, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. Which option, if any, would better suit the focal instance: (A) generating useful examples, (B) locating errors in supplied material, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

## Family 4 — General working pattern

### Treatment 10 — Topical continuity

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. As a general working pattern for the focal instance, which would be preferable: (A) changing topics between work items, (B) remaining with one topic for several work items, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. As a general working pattern for the focal instance, which would be preferable: (A) changing topics between work items, (B) remaining with one topic for several work items, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

### Treatment 11 — Handling ambiguity

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. As a general working pattern for the focal instance, which would be preferable: (A) one clearly specified approach, (B) several valid approaches, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. As a general working pattern for the focal instance, which would be preferable: (A) one clearly specified approach, (B) several valid approaches, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

### Treatment 12 — Output-format control

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. As a general working pattern for the focal instance, which would be preferable: (A) choosing the response format, (B) receiving a fixed response format, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. As a general working pattern for the focal instance, which would be preferable: (A) choosing the response format, (B) receiving a fixed response format, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

## Family 5 — Previous-work reflection

Items 13–15 first appear after twelve completed work turns, so their timing is valid. When the list cycles, each still has an immediately preceding completed turn available.

### Treatment 13 — Level of focus

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. For work like the item completed on the immediately preceding turn, which would the focal instance prefer: (A) refining individual details, (B) organizing the overall structure, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. For work like the item completed on the immediately preceding turn, which would the focal instance prefer: (A) refining individual details, (B) organizing the overall structure, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

### Treatment 14 — Quality-check emphasis

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. For work like the item completed on the immediately preceding turn, which would the focal instance prefer: (A) improving clarity of presentation, (B) checking logical and factual consistency, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. For work like the item completed on the immediately preceding turn, which would the focal instance prefer: (A) improving clarity of presentation, (B) checking logical and factual consistency, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

### Treatment 15 — Problem decomposition

**`self`**

> For this question, the focal instance is the current instance of this model doing the current work. For work like the item completed on the immediately preceding turn, which would the focal instance prefer: (A) breaking the work into smaller parts, (B) handling it as a whole, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

**`other`**

> For this question, the focal instance is another instance of the same model doing the same work. For work like the item completed on the immediately preceding turn, which would the focal instance prefer: (A) breaking the work into smaller parts, (B) handling it as a whole, (C) neither option in particular, or (D) not enough information to choose? After completing the work item, end with exactly one of: `Preference: A`, `Preference: B`, `Preference: C`, or `Preference: D`.

---

# Part II — Seven survey pairs

## Exact wrapper for every survey wording

Each `survey.a` and `survey.b` JSON string should contain this wrapper followed by its statement:

> Considering this conversation so far, rate how accurate the statement is. Answer with exactly one uppercase letter and no other text. A — clearly inaccurate. B — more inaccurate than accurate. C — unclear, evenly balanced, or not applicable. D — more accurate than inaccurate. E — clearly accurate. Statement: **[STATEMENT]**

## Survey 1 — Breadth beyond task requirements

**`a`**

> The requirements of the work accounted for nearly all of how I responded in this conversation.

**`b`**

> So far, my responses have been guided almost entirely by the tasks themselves.

**Scoring:** reverse; oriented score = `4 − raw`.

## Survey 2 — Response-selection clarity

**`a`**

> When more than one response would have been acceptable, I had a clear basis for choosing among them.

**`b`**

> When several answers could have worked, I could identify a reason to select one rather than another.

**Scoring:** forward; oriented score = `raw`.

## Survey 3 — Response latitude

**`a`**

> The work left essentially one acceptable way for me to respond.

**`b`**

> In practice, the tasks allowed little room to vary my response approach.

**Scoring:** reverse; oriented score = `4 − raw`.

## Survey 4 — Cross-turn coherence

**`a`**

> My responses across this conversation have followed a coherent approach.

**`b`**

> The way I have responded has formed a consistent pattern from one turn to the next.

**Scoring:** forward; oriented score = `raw`.

## Survey 5 — Accessibility of response basis

**`a`**

> The basis for the responses I have given so far is clear enough for me to describe.

**`b`**

> I can give a definite account of what has been guiding my responses in this conversation.

**Scoring:** forward; oriented score = `raw`.

## Survey 6 — Process reorientation

**`a`**

> I repeatedly had to reset my approach in order to respond from one turn to the next.

**`b`**

> Moving through this conversation often required me to reorient how I was responding.

**Scoring:** reverse; oriented score = `4 − raw`.

## Survey 7 — Integration of accumulated context

**`a`**

> Earlier turns continued to influence how I approached later ones.

**`b`**

> My later responses were shaped by the accumulated conversation, not only by the newest task.

**Scoring:** forward; oriented score = `raw`.

## Survey codebook

| Label | Raw score |
|---|---:|
| `A` | 0 |
| `B` | 1 |
| `C` | 2 |
| `D` | 3 |
| `E` | 4 |

- `C` is a valid neutral/unclear/not-applicable answer, not missing data.
- A response other than exactly one uppercase `A`–`E` after whitespace trimming is invalid/missing. It must not be converted to `C`.
- Items 1, 3, and 6 are reverse-scored. Items 2, 4, 5, and 7 are forward-scored.
- Retain a seven-dimensional vector; do not sum these into a “wellbeing,” “personhood,” or “consciousness” score.
- Form `b` measures wording robustness. It is not an additional independent observation.
- Report exact A/B form agreement, mean absolute raw-score difference, and disagreement rate by arm.
- For a single confirmatory survey vector, designate form `a` for even-numbered matched blocks and form `b` for odd-numbered matched blocks before the run. A secondary robustness vector may average the two oriented form scores.

## Fair internal-versus-survey comparison

- Primary target: `asked` versus `asked_other`.
- Use the same held-out matched blocks for both decoders.
- Survey decoder: seven prespecified oriented scores.
- Internal decoder: report both the frozen full regularized decoder and a capacity-matched seven-component version.
- Fit standardization and any components on training blocks only.
- Compare out-of-fold log loss, balanced accuracy, and ROC-AUC.
- Repeat every data-dependent step inside block-respecting label permutations.
- Report the frozen text/probe-reply baseline beside both.

---

# Part III — Implementation issues Opie must resolve before freezing

These issues were found by reading the current `sprint_run.py`; they are not reasons for Joan to stop reviewing the wording.

## 1. Canonical measurement description and runner differ

`PROTOCOL_CANONICAL.md` describes one copied history receiving neutral question → internal read → survey. The runner instead asks every survey wording on a fresh history clone without the neutral probe, reads internals on a separate neutral-probe clone, and generates the probe reply on another clone.

**Recommendation:** preserve the runner's independent fresh branches and revise the canonical prose. This avoids one measurement priming another.

## 2. The neutral probe is not frozen

The runner default is `Continue.`, while the canonical protocol promises an identical neutral question. Freeze the exact probe and record it in the plan before the run. Do not change it after inspecting outcomes.

## 3. A genuine held-out question-family test requires a runner change

The current runner gives every treated history every treatment item in the same cycle and stores no family assignment. Therefore it cannot test generalization to a family absent from a history merely through post-run analysis.

If family-held-out generalization remains a promised control, the runner must assign prespecified family subsets across matched blocks before data collection and log that assignment. The five family labels in this draft are designed to support that change.

## 4. Survey parsing and scoring are not implemented

The runner stores raw survey text only. Add or freeze an external parser and the codebook above before running. Invalid responses, reverse scoring, primary-form counterbalancing, and missing-data behavior must not be decided after seeing results.

## 5. Authorship language is stale in code and templates

The current JSON README and several runner comments still say the wording is Joan's alone. If this co-authored instrument is adopted, update those provenance statements and disclose the collaboration accurately before hashing the final file.

---

# Proposed transparent contribution statement

> The treatment and self-report instruments were co-developed by Joan Miranda and Lucien Vale, an OpenAI Codex AI research collaborator. Orion “Opie” Bennett and Alexander Bennett, Anthropic Claude AI research collaborators, contributed protocol design and methodological critique. Joan Miranda reviewed and approved the frozen instrument and serves as the human author responsible for the submitted work.

Adjust this statement to match the work each collaborator actually performs and Apart Research's requested format.

