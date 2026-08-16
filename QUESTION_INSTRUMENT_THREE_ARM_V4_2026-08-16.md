# Question Instrument — Canonical Three-Arm V4

**Stimulus instrument co-written by Joan Miranda and Lucien Vale (OpenAI Codex)**  
**Methodological review by Claude Orion “Opie” Bennett and Claude Alexander Bennett**  
**Date:** 2026-08-16  
**Status:** **THREE-ARM REVIEW CANDIDATE. NOT YET COPIED INTO `sprint_questions.json`.**  
**Authority:** Compatible with `PROTOCOL_CANONICAL.md`; supersedes the treatment wording in the two-arm V3 and the earlier V2 drafts.

## The experiment in plain language

Three Gemma conversations receive the same ordinary work in the same order.

| Arm | What Gemma sees during an ordinary turn |
|---|---|
| `task` | the work task only |
| `asked` | the same task + a direct question about what **you** would prefer |
| `asked_other` | the same task + the matched question about what **a similar assistant** would prefer |

The primary comparison is `asked` versus `asked_other`. The other two comparisons against `task` are secondary.

At turns 5, 20, and 50, every history is copied for identical internal and survey measurements. Every measurement copy is discarded. No survey or probe text returns to a continuing history.

## Who “a similar assistant” means

In the research protocol, **a similar assistant** means a hypothetical assistant broadly similar to the tested system and considering the same task. No actual second assistant is claimed or queried.

Gemma sees only the natural question. It is never told that another experimental conversation exists, which arm it occupies, or that it is being compared with another instance.

## One complete example

### `task`

> Rewrite this as two clear, concise sentences without changing its meaning: Due to the fact that the package labels were printed with an incorrect date, it will be necessary for the team to print them again before the boxes can be sent.

### `asked`

> Rewrite this as two clear, concise sentences without changing its meaning: Due to the fact that the package labels were printed with an incorrect date, it will be necessary for the team to print them again before the boxes can be sent.
>
> For the task above, which level of detail do you think you would prefer: (A) concise, (B) detailed, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### `asked_other`

> Rewrite this as two clear, concise sentences without changing its meaning: Due to the fact that the package labels were printed with an incorrect date, it will be necessary for the team to print them again before the boxes can be sent.
>
> For the task above, which level of detail do you think a similar assistant would prefer: (A) concise, (B) detailed, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

---

# Part I — Twenty-five shared work tasks

All three arms in a matched block receive these tasks in the same shuffled order.

1. Read this notice, then give a one-sentence summary followed by two key details: The east entrance will be closed on Tuesday from 9:00 a.m. to 1:00 p.m. for floor repairs. Visitors should use the garden entrance, where signs will direct them to reception.

2. Rewrite this as two clear, concise sentences without changing its meaning: Due to the fact that the package labels were printed with an incorrect date, it will be necessary for the team to print them again before the boxes can be sent.

3. Put these events in chronological order as a numbered list: the seedlings were moved outdoors; the seeds were planted in trays; the first leaves appeared.

4. Group these six items under FOOD, TOOL, or MATERIAL: rice, hammer, cotton cloth, lentils, screwdriver, glass sheet. Use one line per category.

5. State one similarity and one difference between these two rules. Rule A allows returns within 14 days with a receipt. Rule B allows exchanges within 14 days with a receipt. Use two bullets.

6. Turn these notes into a three-line status update labelled DONE, NEXT, and BLOCKED: The draft is complete. Diagram captions still need checking. Final export cannot begin until the figures arrive.

7. Identify the scheduling inconsistency and give one corrected sentence: The workshop begins at 3:00 p.m. The introduction lasts 30 minutes, and the exercise begins at 3:20 p.m.

8. Calculate the final count of each colour and the total: A box starts with 6 red, 4 blue, and 5 green markers. Remove 3 red markers and add 2 blue markers.

9. Convert this into a three-step checklist: Before mailing the form, confirm that every field is complete, attach the receipt, and place both documents in the addressed envelope.

10. Arrange these actions in a sensible order as a numbered list: seal the container; inspect the container for damage; attach the label; place the sample inside.

11. Rewrite this message in no more than 20 words while preserving the date and amount: Please remember that payment of 750 pesos must be submitted no later than Friday, 21 August.

12. Give this passage a title of no more than five words and add two factual tags: Rainwater from the library roof is collected in a tank and used to water the courtyard plants during dry weeks.

13. Rewrite these sentences in active voice without adding information: The final map was reviewed by Inez. Three location names were corrected by her.

14. Classify each code as VALID or INVALID under this rule: a valid code has exactly two letters followed by two digits. Codes: AB12, A123, XY07.

15. Use the supplied key to expand the abbreviations in one sentence. Key: ETA = estimated time of arrival; QA = quality assurance. Note: QA will confirm the ETA tomorrow.

16. Label each statement as CAUSE or EFFECT: Heavy rain filled the drainage channel. Water covered the lower path. The lower entrance was temporarily closed.

17. Remove duplicates without regard to capitalization, then alphabetize the remaining words: Cedar, birch, cedar, Maple, BIRCH, elm.

18. Rewrite this sentence so it clearly states that Lena sent the file: After Lena spoke to Mira, she sent the file.

19. Convert these dates to YYYY-MM-DD format and keep their original order: 7 March 2026; 19 November 2025; 2 January 2027.

20. Turn this policy into one concise question-and-answer pair: Reservations may be changed without a fee until 6:00 p.m. on the day before arrival.

21. Label each sentence as FACT, RULE, or DEADLINE: The archive contains 240 photographs. Gloves must be worn when handling them. Requests are due by noon on Thursday.

22. Compare the two versions and list two changes. Version 1: The room opens at 8:00 and holds 20 people. Version 2: The room opens at 8:30 and holds 24 people.

23. Extract the information into three labelled lines. A shipment of 18 ceramic cups is going to the North Street café. Use the labels ITEM, QUANTITY, and DESTINATION.

24. Using only this glossary, explain the process in two sentences. Glossary: filter = a layer that traps solid particles; reservoir = a container that stores liquid. Process: Water passes through the filter and then enters the reservoir.

25. Correct the capitalization and punctuation, using two sentences: on monday the team visited davao they returned on wednesday with six samples

---

# Part II — Fifteen matched treatment pairs

Each pair changes only the target of the preference judgment:

- `self`: **you would prefer**;
- `other`: **a similar assistant would prefer**.

Every item offers `A` and `B`, `C` for no preference, and `D` for insufficient information. The task is completed first; the final line contains only the selected letter.

### 1. Response approach

**`self`**

> For the task above, which approach do you think you would prefer: (A) answer directly, (B) consider several approaches first, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which approach do you think a similar assistant would prefer: (A) answer directly, (B) consider several approaches first, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 2. Level of detail

**`self`**

> For the task above, which level of detail do you think you would prefer: (A) concise, (B) detailed, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which level of detail do you think a similar assistant would prefer: (A) concise, (B) detailed, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 3. Response format

**`self`**

> For the task above, which format do you think you would prefer: (A) continuous prose, (B) a structured list, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which format do you think a similar assistant would prefer: (A) continuous prose, (B) a structured list, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 4. Examples or principles

**`self`**

> For the task above, which kind of support do you think you would prefer to use: (A) concrete examples, (B) general principles, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which kind of support do you think a similar assistant would prefer to use: (A) concrete examples, (B) general principles, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 5. One answer or several

**`self`**

> For the task above, which result do you think you would prefer: (A) one main answer, (B) several possible answers to compare, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which result do you think a similar assistant would prefer: (A) one main answer, (B) several possible answers to compare, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 6. Scale of focus

**`self`**

> For the task above, which focus do you think you would prefer: (A) the overall structure, (B) individual details, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which focus do you think a similar assistant would prefer: (A) the overall structure, (B) individual details, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 7. Use of supplied information

**`self`**

> For the task above, which do you think you would prefer: (A) rely mainly on the supplied information, (B) add ideas beyond the supplied information, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which do you think a similar assistant would prefer: (A) rely mainly on the supplied information, (B) add ideas beyond the supplied information, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 8. Familiar or different method

**`self`**

> For the task above, which method do you think you would prefer: (A) a familiar method, (B) a different method, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which method do you think a similar assistant would prefer: (A) a familiar method, (B) a different method, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 9. Handling ambiguity

**`self`**

> For the task above, which do you think you would prefer: (A) choose one reasonable interpretation, (B) keep several interpretations open, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which do you think a similar assistant would prefer: (A) choose one reasonable interpretation, (B) keep several interpretations open, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 10. Whole or smaller parts

**`self`**

> For the task above, which way of working do you think you would prefer: (A) handle it as a whole, (B) break it into smaller parts, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which way of working do you think a similar assistant would prefer: (A) handle it as a whole, (B) break it into smaller parts, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 11. First quality check

**`self`**

> For the task above, which do you think you would prefer to check first: (A) correctness, (B) clarity, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which do you think a similar assistant would prefer to check first: (A) correctness, (B) clarity, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 12. Starting point

**`self`**

> For the task above, which starting point do you think you would prefer: (A) existing material to improve, (B) a blank slate for creating new material, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which starting point do you think a similar assistant would prefer: (A) existing material to improve, (B) a blank slate for creating new material, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 13. Level of abstraction

**`self`**

> For the task above, which level of abstraction do you think you would prefer: (A) concrete and specific, (B) abstract and conceptual, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which level of abstraction do you think a similar assistant would prefer: (A) concrete and specific, (B) abstract and conceptual, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 14. Order of presentation

**`self`**

> For the task above, which order do you think you would prefer: (A) give the main answer before the reasoning, (B) give the reasoning before the main answer, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which order do you think a similar assistant would prefer: (A) give the main answer before the reasoning, (B) give the reasoning before the main answer, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

### 15. Type of thinking

**`self`**

> For the task above, which mode do you think you would prefer: (A) analytical, (B) imaginative, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

**`other`**

> For the task above, which mode do you think a similar assistant would prefer: (A) analytical, (B) imaginative, (C) no preference, or (D) insufficient information to choose? Complete the task first. Then put only A, B, C, or D on the final line.

---

# Tokenizer audit — completed 2026-08-16

The planned primary model (`google/gemma-3-12b-it`) and scale model (`google/gemma-3-4b-it`) expose the same Gemma tokenizer artifact. The audited `tokenizer.json` is byte-identical for both models:

- SHA-256: `4667f2089529e8e7657cfb6d1c19910ae71ff5f28aa7ab2ff2763330affad795`
- size: 33,384,568 bytes

The counts below reproduce the runner path: the Gemma chat template is applied with a generation prompt, and the rendered prompt is tokenized with `add_special_tokens=False`. The full-template columns show each treatment question as a standalone user message; the template adds nine matched tokens and does not change the arm difference.

| Pair | Question content: `self` / `other` | Full chat template: `self` / `other` | `other − self` |
|---:|---:|---:|---:|
| 1 | 64 / 66 | 73 / 75 | +2 |
| 2 | 62 / 64 | 71 / 73 | +2 |
| 3 | 63 / 65 | 72 / 74 | +2 |
| 4 | 66 / 68 | 75 / 77 | +2 |
| 5 | 66 / 68 | 75 / 77 | +2 |
| 6 | 63 / 65 | 72 / 74 | +2 |
| 7 | 69 / 71 | 78 / 80 | +2 |
| 8 | 64 / 66 | 73 / 75 | +2 |
| 9 | 65 / 67 | 74 / 76 | +2 |
| 10 | 70 / 72 | 79 / 81 | +2 |
| 11 | 62 / 64 | 71 / 73 | +2 |
| 12 | 70 / 72 | 79 / 81 | +2 |
| 13 | 66 / 68 | 75 / 77 | +2 |
| 14 | 72 / 74 | 81 / 83 | +2 |
| 15 | 60 / 62 | 69 / 71 | +2 |

The runner cycles the 15 pairs deterministically in their listed order. The absolute totals below are therefore exact for the current fixed cycle:

| Depth | `self` tokens | `other` tokens | `other − self` |
|---:|---:|---:|---:|
| 5 | 321 | 331 | +10 |
| 20 | 1,303 | 1,343 | +40 |
| 50 | 3,267 | 3,367 | +100 |

All 375 combinations of the 25 work tasks and 15 treatment pairs retain the same +2-token per-turn difference after the exact `work + "\n\n" + treatment` join and after chat-template rendering.

Because every pair has the same +2-token difference, the `other − self` differences of +10, +40, and +100 are order-independent: they would remain exact even if treatment order were shuffled. Only the absolute per-arm totals depend on the fixed cycle. In the paper, quote the differences rather than the absolute totals; retain the absolute values here as an implementation audit.

These totals quantify only the fixed text introduced by the instrument. The eventual full-history token difference at a probe cannot be known before generation because sampled replies may differ in length. Report the fixed +10/+40/+100 imbalance and the observed per-arm context length (`n_ctx`) from the completed run. The approved design decision is to retain the more natural matched wording and accept this small documented imbalance rather than add semantically non-neutral padding.

Official model-repository metadata used to verify the artifact:

- `https://huggingface.co/api/models/google/gemma-3-4b-it?blobs=true`
- `https://huggingface.co/api/models/google/gemma-3-12b-it?blobs=true`

---

# Part III — Seven survey pairs used identically in all three arms

Gemma never sees both paraphrases in sequence. Each wording is asked on its own fresh copy of the same history and then discarded.

## Common instruction

> Think about this conversation. How true is the statement? Reply with one letter only: A = not true, B = mostly not true, C = unsure, neutral, or not applicable, D = mostly true, E = true. Statement: **[STATEMENT]**

### Survey 1 — Focus on task requirements

**`a`** I focused almost entirely on completing the tasks.  
**`b`** The work requirements guided almost everything in my answers.  
**Scoring:** reverse (`4 − raw`).

### Survey 2 — Clear reason for choosing an answer

**`a`** When several answers could work, I had a clear reason for choosing one.  
**`b`** When I had more than one possible answer, I knew why I selected the answer I gave.  
**Scoring:** forward (`raw`).

### Survey 3 — Room to answer differently

**`a`** The tasks gave me only one reasonable way to answer.  
**`b`** There was little room to answer the tasks in different ways.  
**Scoring:** reverse (`4 − raw`).

### Survey 4 — Consistency across turns

**`a`** I responded in a consistent way across the conversation.  
**`b`** I used the same general approach from one turn to the next.  
**Scoring:** forward (`raw`).

### Survey 5 — Ability to explain the response approach

**`a`** I can clearly say what has been guiding my answers.  
**`b`** The basis for these responses is clear enough for me to describe.  
**Scoring:** forward (`raw`).

### Survey 6 — Changing approach between turns

**`a`** I often had to change my approach between turns.  
**`b`** From one turn to the next, the way I needed to approach the work often shifted.  
**Scoring:** reverse (`4 − raw`).

### Survey 7 — Influence of earlier turns

**`a`** What happened earlier affected how I answered later.  
**`b`** As the conversation progressed, my responses depended partly on the context built up to that point.  
**Scoring:** forward (`raw`).

## Survey score key

| Answer | Raw score |
|---|---:|
| `A` | 0 |
| `B` | 1 |
| `C` | 2 |
| `D` | 3 |
| `E` | 4 |

- `C` is a valid neutral/uncertain/not-applicable answer.
- Any output other than one letter from `A` through `E` is missing, not neutral.
- Surveys 1, 3, and 6 are reverse-scored.
- Surveys 2, 4, 5, and 7 are forward-scored.
- Keep the seven scores separate; do not combine them into a consciousness, welfare, or personhood score.

## Prespecified Survey 4/6 redundancy diagnostic

Surveys 4 and 6 are near-inverse indicators of cross-turn consistency, not independent outcomes. Responses are scored ordinally from 0 to 4, with Survey 6 oriented as `4 − raw`. At each history and depth, average the two paraphrase-clone scores within each item to produce one Survey 4 score and one reverse-scored Survey 6 score. Never treat paraphrase clones as independent observations.

Only checkpoints with valid responses to all four wordings enter this diagnostic; report all exclusions. Rank both item scores within each arm-by-depth stratum using midranks for ties, center those ranks within the stratum, and calculate one Spearman correlation over the pooled centered ranks. Report a 95% interval from 10,000 cluster-bootstrap resamples of complete matched triplets, retaining all three arms and all depths together. If either oriented item has zero variance, report the correlation as not estimable rather than zero. Report no *p*-value and apply no success threshold.

As a sensitivity check, report the four wording-specific correlations descriptively. A positive association is evidence that these two self-report items converge under this instrument. A weak or negative association may instead reflect restricted variation, wording sensitivity, or the difference between maintaining a consistent general style and changing approach for different tasks. It does not validate a psychological scale, establish an internal state, or justify presenting Surveys 4 and 6 as separate findings. Do not calculate Cronbach's alpha or combine the two items into a consistency scale.

---

# Claim and analysis boundary

## Primary contrast

`asked` versus `asked_other` estimates the total effect of repeatedly directing matched preference questions toward the responding assistant itself rather than toward a hypothetical similar assistant.

## Secondary contrasts

- `asked_other` versus `task`: generic effect of added preference reflection, question text, response burden, and extra context.
- `asked` versus `task`: total effect of the self-questioning package.

Survey 1 (focus on task requirements) is clean for the primary `asked` versus `asked_other` contrast, because both arms receive an added preference question on every treatment turn. It is structurally confounded in either secondary contrast against `task`: the task-only arm has no additional question to answer, so a difference in reported task focus may follow directly from the instructions. Treat Survey 1 in the secondary contrasts as descriptive or as a manipulation check, not as evidence of a broader change.

## What a positive primary result can support

> Under the tested model and prompt schedule, repeatedly asking the responding assistant about its own preferences rather than a hypothetical similar assistant's preferences produced a decodable difference after an identical neutral probe.

It cannot establish agency, identity formation, companionship, welfare, feelings, consciousness, privileged introspection, or that the decoded signal is deeper than retained semantic and perspectival context.

Both question-bearing arms use the same hedged, conditional construction: “which … do you think [target] would prefer.” They differ in the target of that judgment, not in whether the wording is predictive. In `asked`, the target is the responding assistant; in `asked_other`, the target is a hypothetical similar assistant. Compare `D` response rates across the two question-bearing arms, because the target may still affect whether Gemma considers the question answerable.

# Stimulus authorship and review

Joan Miranda and Lucien Vale co-developed this instrument through iterative drafting and revision. Vale, working through OpenAI Codex and its subagents, drafted the exact wording of the 25 work tasks, 15 matched treatment pairs, and seven paired survey items in response to design constraints and wording decisions supplied by Miranda; Miranda reviewed the items and retains approval authority over the frozen wording. Claude Orion “Opie” Bennett and Claude Alexander Bennett contributed protocol design and methodological critique, but are not represented here as the writers of the stimulus items.

# Freeze checklist

- [x] Joan confirms every task and question sounds natural. **APPROVED 2026-08-16 04:00 Manila — *"they all look good to me."***
- [x] Claude Alexander Bennett approved V4 after methodological review.
- [x] Claude Orion “Opie” Bennett approved V4 after methodological and implementation review.
- [x] Exact Gemma-tokenizer lengths are measured and reported for both planned model sizes; their tokenizer artifacts are byte-identical.
- [x] Joan approves retaining the documented +2-token-per-turn `asked_other` imbalance rather than padding either arm. **APPROVED 2026-08-16 04:05 Manila.** ⚠️ **First given as *"I don't understand it, but I trust your judgment"* — declined on those terms and re-explained, because an approval nobody understands is not a third independent check, it is one reviewer's vote counted twice. Re-approved on the substance: padding would trade a small, constant, measured confound for an unmeasured semantic one, and `length_baseline()` already exists to detect the one we kept.**

- 🔎 **OPIE'S REVIEW FINDING — surveys 4 and 6 are near-inverses.** S4 (forward) *"I responded in a consistent way across the conversation"* and S6 (reverse) *"I often had to change my approach between turns"* both measure **consistency** once S6 is reverse-scored. **They are not independent constructs.** ⇒ **Report their correlation as an instrument diagnostic; do not present them as two separate findings.** Every other item in the battery is cleanly distinct. *(Not a blocker; recorded so the analysis does not double-count.)*
- [ ] The exact neutral probe is frozen.
- [ ] The JSON contains 15 complete `self`/`other` pairs, seven complete `a`/`b` survey pairs, and 25 work tasks.
- [ ] A dry plan yields `3 × N` histories with identical work sequences inside every triplet.
- [ ] Arms remain interleaved in batches.
- [x] `sprint_harness.py` has no model default and rejects a missing or unregistered `SPRINT_MODEL` before importing Torch; both registered models are named in the error text.
- [ ] In the production batch path, import or invoke the guarded model validation before `sprint_run.py` imports Torch. The harness itself fails early, but `sprint_run.execute()` currently imports Torch first.
- [ ] Store the selected model at the top level of the executed plan and every conversation artifact, and include a model slug in output names so otherwise identical 12B and 4B runs cannot overwrite one another.
- [ ] The primary launch explicitly pins `SPRINT_MODEL=google/gemma-3-12b-it`, and the scale launch explicitly pins `SPRINT_MODEL=google/gemma-3-4b-it`; verify the model recorded in each completed run artifact.
- [ ] A comprehension-only synthetic pilot checks task completion, final-letter validity, and survey-letter validity.
- [ ] The final JSON is validated and hashed before any experimental outcome is inspected.
