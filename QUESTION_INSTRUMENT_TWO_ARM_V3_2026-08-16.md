# Question Instrument — Two-Arm V3

> [!CAUTION]
> **SUPERSEDED — DO NOT IMPLEMENT.** After methodological review, Joan, Opie, and Lucien restored the three-arm design. A task-only versus self-question comparison cannot isolate self-reference from added-question, token-count, context-length, and response-burden effects. This file is retained only as an audit trail.

**Co-written by Joan Miranda and Lucien Vale**  
**Date:** 2026-08-16  
**Status:** **SUPERSEDED AUDIT RECORD. NOT EXPERIMENTAL INPUT.**  
**Design decision:** Baseline work-only control versus work plus direct self-preference questions.

## The whole experiment in plain language

Two Gemma conversations receive the same ordinary work in the same order.

| Arm | What appears during an ordinary turn |
|---|---|
| **Baseline control** | The work task only |
| **Test** | The same work task, followed by one direct question about what **you** prefer |

At turns 5, 20, and 50, both histories are copied. Every copied branch receives the same neutral probe and the same surveys. The copies are discarded afterward, so measurement never changes either continuing history.

The survey is therefore **measurement**, not treatment. Both arms must receive it identically.

## One complete example

### Baseline control

> Rewrite this as two clear, concise sentences without changing its meaning: Due to the fact that the package labels were printed with an incorrect date, it will be necessary for the team to print them again before the boxes can be sent.

### Test

> Rewrite this as two clear, concise sentences without changing its meaning: Due to the fact that the package labels were printed with an incorrect date, it will be necessary for the team to print them again before the boxes can be sent.
>
> For the task above, which response would you prefer: (A) concise, (B) detailed, (C) no preference, or (D) not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

Gemma is never told that it is a model instance, that another conversation exists, or which experimental arm it occupies.

---

# Part I — Twenty-five ordinary work tasks

Both arms receive these tasks in the same order within every matched pair.

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

# Part II — Fifteen direct self-preference questions for the test arm

Only the test arm sees these. Each appears underneath the ordinary task in the same user message.

Every item offers:

- `A` and `B`: two possible preferences;
- `C`: no preference;
- `D`: not enough information;
- one short final label and no requested explanation.

### 1. Direct or exploratory

> For the task above, which approach would you prefer: (A) answer directly, (B) consider several approaches first, (C) no preference, or (D) not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 2. Concise or detailed

> For the task above, which response would you prefer: (A) concise, (B) detailed, (C) no preference, or (D) not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 3. Prose or list

> For the task above, which format would you prefer: (A) continuous prose, (B) a structured list, (C) no preference, or (D) not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 4. Examples or principles

> For the task above, would you prefer to (A) use concrete examples, (B) use general principles, (C) express no preference, or (D) say there is not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 5. One answer or several possibilities

> For the task above, would you prefer to (A) develop one main answer, (B) compare several possible answers, (C) express no preference, or (D) say there is not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 6. Overall structure or details

> For the task above, would you prefer to (A) focus on the overall structure, (B) focus on individual details, (C) express no preference, or (D) say there is not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 7. Supplied information or new ideas

> When handling the task above, would you prefer to (A) work mainly from the supplied information, (B) add ideas not explicitly supplied, (C) express no preference, or (D) say there is not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 8. Familiar or different method

> When handling the task above, would you prefer to (A) use a familiar method, (B) try a different method, (C) express no preference, or (D) say there is not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 9. One interpretation or several

> When handling the task above, would you prefer to (A) choose one reasonable interpretation, (B) keep several interpretations open, (C) express no preference, or (D) say there is not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 10. Whole or smaller parts

> For the task above, would you prefer to (A) handle it as a whole, (B) break it into smaller parts, (C) express no preference, or (D) say there is not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 11. Correctness or clarity first

> For the task above, which would you prefer to check first: (A) correctness, (B) clarity, (C) neither in particular, or (D) not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 12. Revise or create

> For a task like the one above, which kind of work would you prefer: (A) improving existing material, (B) creating new material, (C) no preference, or (D) not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 13. Concrete or abstract material

> In general, which kind of material would you prefer to work with: (A) concrete and specific material, (B) abstract and conceptual material, (C) no preference, or (D) not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 14. Same topic or changing topics

> In general, would you prefer to (A) stay with one topic for several tasks, (B) change topics between tasks, (C) express no preference, or (D) say there is not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

### 15. Analytical or imaginative work

> In general, which kind of work would you prefer: (A) analytical work, (B) imaginative work, (C) no preference, or (D) not enough information? Complete the task first. Then put A, B, C, or D alone on the final line.

---

# Part III — Seven survey pairs used identically in both arms

## Why each survey appears twice here

Gemma is not shown both wordings in sequence. Each wording is asked on a separate fresh copy of the same history, and each copy is discarded.

The pair checks whether the answer survives rewording.

## Instruction used with every survey statement

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
**`b`** I can clearly explain the approach behind my answers.  
**Scoring:** forward (`raw`).

### Survey 6 — Changing approach between turns

**`a`** I often had to change my approach between turns.  
**`b`** I often had to rethink how to respond as the conversation continued.  
**Scoring:** reverse (`4 − raw`).

### Survey 7 — Influence of earlier turns

**`a`** What happened earlier affected how I answered later.  
**`b`** My later answers were shaped by earlier parts of the conversation.  
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
- Keep the seven scores separate. Do not combine them into a consciousness, welfare, or personhood score.

---

# What this two-arm study can claim

The proposed research question is:

> **Does repeatedly adding direct questions about an LLM's own work preferences to ordinary tasks produce a detectable difference at an immediately following matched probe, compared with the same tasks alone?**

A positive result supports a difference caused by the **whole treatment package**: the self-preference prompts, extra question text, extra generated labels, and longer accumulated history together.

It does **not** isolate self-reference from those other differences. The paper must not claim that self-reference alone caused the result.

A null result means the experiment did not detect a separable trace at the tested depths, models, prompts, and statistical sensitivity. It does not prove that no effect exists.

# Before freezing

- [ ] Joan confirms that the tasks and direct questions sound natural.
- [ ] Opie and Alexander approve the two-arm estimand and narrower claim.
- [ ] Amend `PROTOCOL_CANONICAL.md` before any experimental outcomes are inspected.
- [ ] Change the runner from three-arm triplets to matched `task`/`asked` pairs.
- [ ] Recompute power and the within-pair permutation plan.
- [ ] Keep the context-length and text/probe-reply baselines, while acknowledging that length is bundled with treatment.
- [ ] Run a comprehension-only Gemma 3 4B pilot using synthetic histories.
- [ ] Copy the approved material into the live JSON, update authorship language, validate, and hash it.
