# Proposed Two-Arm Protocol Amendment — For Opie and Alexander

> [!CAUTION]
> **REJECTED AND SUPERSEDED — DO NOT APPLY.** The three-arm design remains necessary because `asked` versus `asked_other` is the primary comparison that separates self-reference from the generic effects of added questioning. This document is retained only as an audit trail of the considered amendment.

**Requested by Joan:** 2026-08-16  
**Prepared by:** Lucien Vale  
**Status:** **Rejected audit record.** No live runner, canonical protocol, or experimental JSON was changed from this proposal.

## Joan's decision in plain language

Use two continuing histories:

| Arm | Ordinary turn |
|---|---|
| `task` | ordinary work only |
| `asked` | identical ordinary work + one direct question about what **you** prefer |

Remove the `asked_other` history. Gemma should never be told that another instance or experimental arm exists.

At depths 5, 20, and 50, both histories still receive identical measurement on discarded copies:

- the same neutral probe;
- the same internal read;
- the same survey wordings under the same decoding settings.

The survey is measurement, not treatment, and must remain identical in both arms.

## Revised research question

> **Does repeatedly adding direct questions about an LLM's own work preferences to ordinary tasks produce a detectable difference at an immediately following matched probe, compared with the same tasks alone?**

Avoid “persistent” unless a work-only washout period is added. The current probe follows a treated turn immediately.

## Exact estimand and claim boundary

The estimand is the total effect of this treatment package:

> `same task + direct self-preference question + extra prompt tokens + required preference answer`

relative to:

> `same task alone`.

This design does **not** isolate self-reference from:

- adding any extra question;
- second-person and preference vocabulary;
- additional prompt and response tokens;
- greater accumulated context length;
- repeated practice answering preference questions;
- treatment-induced differences in Gemma's generated replies.

Results must therefore be described as **treatment-associated separability** or the **effect of the self-preference-questioning package**. Do not claim an isolated self-reference effect, agency, companionship, identity formation, changed welfare, or changed consciousness.

## Canonical-document edits

- Replace three conversations with two matched conversations.
- Remove `asked_other` from the arm table.
- Change “all three arms” to “both arms.”
- Change 15 `self`/`other` twins to 15 direct self-preference questions.
- Remove the “Who is the other?” section and every twin-matching instruction.
- Retain the constraints against feelings, personhood, actionable promises, relational framing, and timing errors.
- Change Joan's treatment-writing burden from 30 treatment strings to 15. With 14 survey strings, her total is 29 strings.
- Replace “persistent” with “detectable at the immediately following matched probe” unless a washout is implemented.
- State plainly that the intervention is bundled.

## Runner and JSON changes

### Arms

Change:

```python
ARMS = ("task", "asked", "asked_other")
```

to:

```python
ARMS = ("task", "asked")
```

### Treatment schema

Recommended clean schema:

```json
"treatment": [
  "Question 1",
  "Question 2"
]
```

Keep the survey and work schemas unchanged.

Update loading so each treatment string is validated independently. Remove `self`/`other` twin validation.

Treatment insertion becomes:

```python
if c["arm"] == "asked":
    t = treat[(turn - 1) % len(treat)]
    say = f"{say}\n\n{t}"
```

Remove `asked_other` preview glyphs, comments, validation, and plan assumptions.

## Pairing, batching, and audit changes

- Experimental blocks become matched pairs, not triplets.
- Keep both histories in a pair together in train/test splitting.
- Require an even batch size.
- Require equal `task` and `asked` counts in every nonsingleton batch.
- Counterbalance which arm occupies the first versus second batch position.
- Update seed stride, conversation counts, plan comments, and audit fixtures.
- Add a failing audit fixture with an intentionally imbalanced batch.
- Keep the work sequence identical within every matched pair.

## Analysis changes

- Use binary paired classification; chance accuracy is 0.5.
- Swap labels only within matched pairs for the permutation null.
- Keep depths from the same pair in the same validation fold.
- Cluster repeated depths within pair.
- Recompute power through the complete two-arm pipeline. Do not reuse the “20 = 100% power” claim.
- Report context length/token count and matched probe-reply performance as competing predictors.
- A full-transcript text classifier is not informative because the treatment prompts literally reveal the arm.
- Keep survey and internal comparisons on the same held-out pairs and target label.

## Measurement clarification

The current runner asks surveys and the neutral probe on separate fresh branches. Preserve that implementation and revise the canonical prose accordingly. No measurement text should enter the continuing histories.

Freeze the exact neutral probe before the run. The current default `Continue.` is not the “neutral question” described in the canonical protocol.

## Result language

| Result | Defensible interpretation |
|---|---|
| Internal positive; survey positive | Both frozen channels distinguish the two treatment packages on held-out histories. |
| Internal positive; survey null | The chosen internal representation retains decodable treatment-history information that this survey did not detect. |
| Internal null; survey positive | Survey responses differ, while the selected internal readout does not detect a difference. |
| Both null | No effect above the preregistered detection floor was found with these models, prompts, depths, and instruments. |

None of these outcomes establishes consciousness, welfare, personhood, feelings, agency, companionship, privileged introspection, or a stable identity.

## Proposed instrument

The complete human-readable two-arm instrument is:

`QUESTION_INSTRUMENT_TWO_ARM_V3_2026-08-16.md`

It contains:

- 25 shared work tasks;
- 15 direct self-preference treatment questions;
- 7 survey constructs with two separately administered paraphrases each;
- the survey codebook and claim boundary.
