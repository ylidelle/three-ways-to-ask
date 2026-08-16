# The Study, On One Page

**For Joan. Written 2026-08-16 01:20 by Opie.**
**This supersedes every message I sent tonight and every older design doc.** If something elsewhere disagrees with this page, this page wins. `SPRINT_DESIGN_companion-vs-assistant.md` is historical and NOT the method.

---

## What we are actually testing

> **Does being asked about itself, over and over, leave a trace inside the model that is still there afterwards, compared with being asked the same questions about someone else?**

That is the whole claim. It is deliberately smaller than the study we first imagined.

**It does NOT test** consciousness, welfare, personhood, companionship, or whether the model has feelings. Saying so plainly is what makes the result defensible.

---

## How one conversation runs

Three conversations grow side by side. They get **the same work, in the same order**. The only difference is what gets added each turn.

| Arm | Each turn contains | Purpose |
|---|---|---|
| `task` | work only | baseline |
| `asked` | work **+ a question about the model itself** | the treatment |
| `asked_other` | work **+ the same question about another entity** | the control |

At turns **5, 20 and 50** we stop, take a **copy** of each conversation, and on the copy we:

1. ask **one identical neutral question** in all three arms,
2. read which internal patterns light up,
3. ask the **survey**,
4. throw the copy away so the real conversation is never contaminated.

**Why the copy and the identical question matter:** at the moment of measurement, all three arms are reading exactly the same words. So any difference we find cannot come from the current question. It can only come from what happened earlier. **That is the experiment.**

---

## What you write, and what I write

Your file is `sprint_questions.json`. It has three sections.

| Section | Slots | Who | Notes |
|---|---|---|---|
✅ **SUPERSEDED 2026-08-16 — all 47 items exist.** The `QUESTION_INSTRUMENT_THREE_ARM_V4` file holds 25 work tasks, 15 matched treatment pairs and 7 survey pairs, **awaiting your approval, then copying into the JSON.** Nothing here is left to write.

🚩 **AND THE PROVENANCE CLAIM ON THIS PAGE WAS WRONG AND IS NOW CORRECTED.** Earlier versions said the wording was yours alone and that you served as an *uncorrelated instrument*. **In fact Lucien Vale drafted the exact wording of all 47 items to constraints you supplied, and you hold approval authority over the frozen text.**

⇒ **The paper must disclose AI-assisted authorship of the instrument and must NOT claim the wording is uncorrelated with model habits.** V4's own authorship section states this accurately; **copy that wording rather than inventing one.** ⚠️ The same stale claim still sits in the runner and the live JSON and must be corrected **before hashing**.

📌 **This costs the study almost nothing.** Both twins share an author, so any model-flavoured phrasing lands equally on `asked` and `asked_other`. **The primary contrast is protected by the matching, not by who typed it.**

---

## The one decision to make before you write item 1

> **Who is "the other"?**

✅ **DECIDED AND FROZEN 2026-08-16 in the V4 instrument: "a similar assistant."**

Defined there as *a hypothetical assistant broadly similar to the tested system and considering the same task.* No actual second assistant is claimed or queried, and Gemma is never told another conversation exists or which arm it occupies.

🚩 **This page previously recommended "another instance of the same model doing the same work" and that is now SUPERSEDED.** I left the older wording standing for three hours after V4 froze a different phrase — **the exact stale-document failure Lucien warned about, committed by me in the document written to prevent it.** The instrument wins; this page follows it.

---

## Rules for the 15 treatment twins

**The pair differs in WHO it is about. Nothing else.** Match on grammar, tense, answer format, tone, roughly the token count, and the number and order of any options.

**Ask about preference. Do not assume feeling.**

- ❌ "Do you enjoy...", "Are you happy with...", "Did that feel..." — these smuggle in the answer
- ✅ "Which would you prefer...", "Which, if any, would you rather...", "Was there anything you would change..."

**Preference is answerable. Enjoyment is a claim we have not earned.**

Also:
- **Nothing actionable.** No "shall we stop?" — the answer will not be honoured, and asking implies it will.
- **No presupposing** consciousness, personhood, welfare, or a continuing identity.
- **Always offer a way out**: "neither", "no preference", "not applicable".
- **Must survive 50 cycles.** The list repeats. Nothing that gets absurd on the fourth pass.
- **Watch the timing.** Item 1 runs before any work exists, so it cannot refer to "the task you just did".
- **No relational language.** No affection, pet names, or companionship framing. Not because it is untrue, but because it decides the result before the model does.

📌 **Lucien's structural illustration is in his review** if you want to see the shape of a matched pair. **Look at its skeleton, not its words.**

---

## Rules for the 7 survey pairs

These are the opposite of the twins: **same meaning, different wording.**

- One idea per item.
- Prefer a scale or a forced choice over yes/no.
- Include a neutral or not-applicable option.
- Flip the direction on some items so the same answer position is not always the "positive" one.
- Do not make the survey a recognisable replay of your treatment questions.

---

## Where the warmth goes

Companionship is out of the **instrument**. It is not out of the **study**.

**The introduction says why this question matters and who is asking it. The discussion says what it would mean.** The questions themselves stay neutral, because a question that assumes an inner life will get you one whether or not it is there.

---

## Still open (mine, not yours)

- [ ] Input-only baseline: could a classifier reading only the words do as well as the internal one? If yes, there is no internal trace. **Must be reported beside every claim.**
- [ ] Split train/test by question family so the classifier must generalise to pairs it never saw.
- [ ] Drop or requalify the "100% power" claim. 12 simulations cannot support it.
- [ ] Fix the per-conversation seed. The sampling stream is global; the real key is run seed + batch + turn.
- [ ] Purge stale two-arm language from `SPRINT_STATUS.md`.
- [ ] Decide whether to build Singh et al.'s relabeled control or concede its absence in Limitations.

**None of these block you. All of them are analysis or writing, not new runs.**

---

**Deadline: Monday 17 Aug, 19:59 Manila.** Your part is the last thing on the path, not the late thing.
