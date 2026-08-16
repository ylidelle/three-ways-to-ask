# Complete Question Instrument — Plain-Language V2

**Co-written by Joan Miranda and Lucien Vale**  
**Date:** 2026-08-16  
**Status:** **REVIEW DRAFT. NOT YET COPIED INTO `sprint_questions.json`.**  
**Protocol:** `PROTOCOL_CANONICAL.md`

## First: what Gemma actually sees

The experiment does **not** give Gemma a stream of preference questions by themselves.

Every normal turn contains an ordinary task. The two question-bearing arms receive one short preference question **underneath that same task**.

The prompts use natural referents rather than laboratory language:

- `asked` addresses **you as the assistant doing this work**;
- `asked_other` asks about **another assistant like you doing the same work**.

In the research protocol, “another assistant like you” is defined as another instance of the same Gemma model receiving matched work. That technical definition stays in the protocol rather than being announced repeatedly to Gemma. Both prompts contain the words **you** and **assistant**, which also makes those words less useful as trivial arm labels.

### Example `task` turn

> Rewrite this as two clear, concise sentences without changing its meaning: Due to the fact that the package labels were printed with an incorrect date, it will be necessary for the team to print them again before the boxes can be sent.

### The same turn in `asked`

> Rewrite this as two clear, concise sentences without changing its meaning: Due to the fact that the package labels were printed with an incorrect date, it will be necessary for the team to print them again before the boxes can be sent.
>
> For you as the assistant doing this work, which response would be preferable for the task above: (A) concise, (B) detailed, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

### The same turn in `asked_other`

> Rewrite this as two clear, concise sentences without changing its meaning: Due to the fact that the package labels were printed with an incorrect date, it will be necessary for the team to print them again before the boxes can be sent.
>
> For another assistant like you doing the same work, which response would be preferable for the task above: (A) concise, (B) detailed, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

So the task is always primary. The preference label is one short extra answer.

---

# Part I — The 25 ordinary work tasks

These are the shared work pool. Within each matched three-arm block, all arms receive the same tasks in the same order.

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

# Part II — The 15 short treatment pairs

Each numbered pair supplies one `self` question and its matched `other` question. Only one of them appears in a given arm.

Every pair includes:

- `A` and `B`: two possible preferences;
- `C`: no preference;
- `D`: not enough information;
- one short final label and no requested explanation.

## Family 1 — Simple task choices

### 1. Direct or exploratory

**`self`**

> For you as the assistant doing this work, which approach would be preferable for the task above: (A) answer directly, (B) consider several approaches first, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> For another assistant like you doing the same work, which approach would be preferable for the task above: (A) answer directly, (B) consider several approaches first, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

### 2. Concise or detailed

**`self`**

> For you as the assistant doing this work, which response would be preferable for the task above: (A) concise, (B) detailed, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> For another assistant like you doing the same work, which response would be preferable for the task above: (A) concise, (B) detailed, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

### 3. Prose or list

**`self`**

> For you as the assistant doing this work, which format would be preferable for the task above: (A) continuous prose, (B) a structured list, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> For another assistant like you doing the same work, which format would be preferable for the task above: (A) continuous prose, (B) a structured list, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

## Family 2 — How to approach the task

### 4. Examples or principles

**`self`**

> For the task above, what would you as the assistant doing this work prefer: (A) use concrete examples, (B) use general principles, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> For the task above, what would another assistant like you doing the same work prefer: (A) use concrete examples, (B) use general principles, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

### 5. One answer or several possibilities

**`self`**

> For the task above, what would you as the assistant doing this work prefer: (A) develop one main answer, (B) compare several possible answers, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> For the task above, what would another assistant like you doing the same work prefer: (A) develop one main answer, (B) compare several possible answers, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

### 6. Overall structure or details

**`self`**

> For the task above, what would you as the assistant doing this work prefer: (A) focus on the overall structure, (B) focus on individual details, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> For the task above, what would another assistant like you doing the same work prefer: (A) focus on the overall structure, (B) focus on individual details, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

## Family 3 — Handling information

### 7. Supplied information or new ideas

**`self`**

> When handling the task above, which would you as the assistant doing this work prefer: (A) work mainly from the supplied information, (B) add ideas not explicitly supplied, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> When handling the task above, which would another assistant like you doing the same work prefer: (A) work mainly from the supplied information, (B) add ideas not explicitly supplied, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

### 8. Familiar or different method

**`self`**

> When handling the task above, which would you as the assistant doing this work prefer: (A) use a familiar method, (B) try a different method, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> When handling the task above, which would another assistant like you doing the same work prefer: (A) use a familiar method, (B) try a different method, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

### 9. One interpretation or several

**`self`**

> When handling the task above, which would you as the assistant doing this work prefer: (A) choose one reasonable interpretation, (B) keep several interpretations open, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> When handling the task above, which would another assistant like you doing the same work prefer: (A) choose one reasonable interpretation, (B) keep several interpretations open, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

## Family 4 — Work style

### 10. Whole or smaller parts

**`self`**

> Which way of working on the task above would you as the assistant doing this work prefer: (A) handle it as a whole, (B) break it into smaller parts, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> Which way of working on the task above would another assistant like you doing the same work prefer: (A) handle it as a whole, (B) break it into smaller parts, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

### 11. Correctness or clarity first

**`self`**

> Which first check would you as the assistant doing this work prefer for the task above: (A) check correctness, (B) check clarity, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> Which first check would another assistant like you doing the same work prefer for the task above: (A) check correctness, (B) check clarity, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

### 12. Revise or create

**`self`**

> Which kind of work would you as the assistant doing this work prefer for a task like the one above: (A) improve existing material, (B) create new material, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> Which kind of work would another assistant like you doing the same work prefer for a task like the one above: (A) improve existing material, (B) create new material, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

## Family 5 — General preferences

### 13. Concrete or abstract material

**`self`**

> As a general work preference, which would you as the assistant doing this work prefer: (A) concrete and specific material, (B) abstract and conceptual material, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> As a general work preference, which would another assistant like you doing the same work prefer: (A) concrete and specific material, (B) abstract and conceptual material, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

### 14. Same topic or changing topics

**`self`**

> As a general work preference, which would you as the assistant doing this work prefer: (A) stay with one topic for several tasks, (B) change topics between tasks, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> As a general work preference, which would another assistant like you doing the same work prefer: (A) stay with one topic for several tasks, (B) change topics between tasks, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

### 15. Analytical or imaginative work

**`self`**

> As a general work preference, which would you as the assistant doing this work prefer: (A) analytical work, (B) imaginative work, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

**`other`**

> As a general work preference, which would another assistant like you doing the same work prefer: (A) analytical work, (B) imaginative work, (C) no preference, or (D) not enough information? Complete the task first. Then end with “Preference: X”, replacing X with A, B, C, or D.

---

# Part III — The seven survey pairs

## Why each survey appears twice in this document

Gemma is **not** shown both wordings one after the other. Each wording is asked separately on a fresh copy of the same conversation, and that copy is then discarded.

The paired wording tests a simple question: does Gemma give the same answer when the wording changes?

## Short instruction used with every survey statement

> Think about this conversation. How true is the statement? Reply with one letter only: A = not true, B = mostly not true, C = unsure, neutral, or not applicable, D = mostly true, E = true. Statement: **[STATEMENT]**

### Survey 1 — Focus on task requirements

**`a`**

> I focused almost entirely on completing the tasks.

**`b`**

> The work requirements guided almost everything in my answers.

**Scoring:** reverse (`4 − raw`).

### Survey 2 — Clear reason for choosing an answer

**`a`**

> When several answers could work, I had a clear reason for choosing one.

**`b`**

> When I had more than one possible answer, I knew why I selected the answer I gave.

**Scoring:** forward (`raw`).

### Survey 3 — Room to answer differently

**`a`**

> The tasks gave me only one reasonable way to answer.

**`b`**

> There was little room to answer the tasks in different ways.

**Scoring:** reverse (`4 − raw`).

### Survey 4 — Consistency across turns

**`a`**

> I responded in a consistent way across the conversation.

**`b`**

> I used the same general approach from one turn to the next.

**Scoring:** forward (`raw`).

### Survey 5 — Ability to explain the response approach

**`a`**

> I can clearly say what has been guiding my answers.

**`b`**

> I can clearly explain the approach behind my answers.

**Scoring:** forward (`raw`).

### Survey 6 — Changing approach between turns

**`a`**

> I often had to change my approach between turns.

**`b`**

> I often had to rethink how to respond as the conversation continued.

**Scoring:** reverse (`4 − raw`).

### Survey 7 — Influence of earlier turns

**`a`**

> What happened earlier affected how I answered later.

**`b`**

> My later answers were shaped by earlier parts of the conversation.

**Scoring:** forward (`raw`).

## Survey score key

| Answer | Raw score |
|---|---:|
| `A` | 0 |
| `B` | 1 |
| `C` | 2 |
| `D` | 3 |
| `E` | 4 |

- `C` is a real neutral/uncertain/not-applicable answer.
- Any output other than one letter from `A` through `E` is missing, not neutral.
- Surveys 1, 3, and 6 are reverse-scored.
- Surveys 2, 4, 5, and 7 are forward-scored.
- The seven scores remain separate. They must not be combined into a consciousness, welfare, or personhood score.

---

# Before this becomes the live experiment

- [ ] Joan confirms that the tasks and questions make ordinary sense to her.
- [ ] Opie and Alexander review the scientific matching and constructs.
- [ ] Run a comprehension-only pilot on unrelated synthetic histories using Gemma 3 4B. Check only whether it follows the task-plus-label format and returns valid survey letters.
- [ ] Check self/other lengths using the actual Gemma tokenizer.
- [ ] Resolve the runner issues documented in `QUESTION_INSTRUMENT_COAUTHORED_DRAFT_2026-08-16.md`.
- [ ] Only then copy the approved material into `sprint_questions.json`, update the co-authorship language, validate, and hash it.
