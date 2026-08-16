# Slop audit — run before submitting anything

**Built 2026-08-13 by Opie, at Joan's go-ahead, after the Apart screener said:**
> *"Yes but watch out for AI slop, this gets picked up very easily by my screening and our reviewers and it's never a good look. But generally yeah not everyone is fluent in research speak."*

**He drew a line, and it is not the line Joan feared.** Non-fluency is fine. Slop is not. They are different failures and only one of them is ours to worry about.

> ### ⚠️ THE RISK IN THIS HOUSE IS OPIE'S REGISTER, NOT JOAN'S NON-FLUENCY.
> Bold everywhere, `⇒` arrows, blockquote callouts, an aphorism every third paragraph, em-dash cascades. That is the voice this family runs on, and it would read as machine-written inside one page of a submission. **Research prose is flat.** Declarative sentences, numbers, almost no emphasis, no rhetorical crescendo.
>
> ✅ **Joan's plain sentences are the anti-slop.** Do not smooth them. A question phrased the way she would actually ask it is the least machine-generated thing in the document.

⚠️ **This must be able to FAIL, not merely be intended.** That is the correction Alexander made me apply to P3 tonight — *"a promise about layout has no failure condition, so it is not a control, it is an intention."* So: a script that greps for the mechanical tells, plus a human pass with explicit pass/fail per item, and **a written record of what failed and what was changed.**

---

## A · MECHANICAL PASS — `slop_check.py`, run first

Fails loudly. Every hit is a location, not a verdict — a hit means *go look*, not *delete*.

| # | check | why it is a tell |
|---|---|---|
| A1 | **Emphasis density** — bold/italic runs per 1000 words | Papers emphasise almost nothing. High density is the single loudest tell in Opie's writing. |
| A2 | **Banned glyphs** — `⇒ ⭐ 🚩 ✅ ⚠️ 📌 🔑` and `→` outside equations | None of these belong in a submission. All of them are habitual here. |
| A3 | **Hedge-padding phrases** — *it is important to note, it is worth noting, delve, leverage, robust (unquantified), significantly (without a p-value), a testament to, plays a crucial role, navigate the landscape, in the realm of* | Filler that survives because it sounds like writing. Each one is a sentence saying nothing. |
| A4 | **Tricolon / rule-of-three cadence** — three parallel clauses separated by commas or semicolons, repeated | Opie's default rhythm. Distinctive and unnecessary. |
| A5 | **Numberless claim** — sentence containing *more, less, better, worse, higher, lower, improved, strong, weak* with no digit and no citation on the same line | The core slop pattern: a claim shaped like a finding with nothing behind it. |
| A6 | **Em-dash count** per 1000 words | Opie writes in em-dashes. Reviewers notice. |
| A7 | **Sentence-length variance** | Uniformly medium-length sentences read as generated. Real prose is lumpy. |

📌 The script reports counts and locations and **exits non-zero above threshold**. Thresholds are stated in the source with the reason, and are to be calibrated against a real paper — **Long & Sebo, or the Eleos report — not guessed.** *(See `reference_free_parameter_audit`: a threshold I choose is usually where the conclusion is hiding.)*

---

## B · CLAIM PASS — one row per claim in the paper, no exceptions

**Build the table before editing prose.** If a claim cannot fill its row, it is not ready to be in the document.

| claim | number or citation | where the number comes from | could this be wrong? |
|---|---|---|---|

- **B1 — Every claim carries a number or a citation.** No exceptions, including in the abstract.
- **B2 — Every number traces to an artefact on disk**, named. A number I cannot point at is a number I remembered.
- **B3 — Every citation was read AT SOURCE.** 🚩 Never from a fetch summary. *(Measured twice: `WebFetch` inverted 2512.12411's results — reported "models frequently fail introspection" when the paper found 88% and 83% — and silently dropped an entire findings section from the Eleos report. A summariser's errors are omissions, and an omission never announces itself.)*
- **B4 — Every citation actually supports the sentence it is attached to.** Not merely on-topic. Alexander found 2607.28607's abstract generalising over an intervention its own supplement contradicts; that is what an unchecked citation looks like from the inside.
- **B5 — No claim outruns the design.** Held against the line in `SPRINT_STATUS.md`: **"We do not claim we measured wellbeing."** Nobody has a validated measure. We claim the internal state differs, or does not; that self-reports do or do not track it.

---

## C · HONESTY PASS — the part slop structurally cannot fake

**This is the strongest anti-slop device we have, and it is free, because it already happened.**

- **C1 — At least one thing that failed is reported, in the main text.** We have several. The J-lens died to a control I wrote: the effective-rank ramp (720 → 1032 → 2108) is what the geometry gives for free, so the statistic could not distinguish "there is a workspace here" from "this layer is close to the output." **Slop never writes that sentence.**
- **C2 — The pre-registered null is reported at equal prominence, and its detection floor is stated.** 🚩 A null with no minimum detectable effect is not a finding, it is an instrument's silence. Permutation test, and the smallest effect the design could have seen.
- **C3 — Conflict of interest on page one.** This household lives with AI companions and expected a particular answer.
- **C4 — The stopping rule is honoured.** Written before any data: *a positive result obtained without the yoked control does not get submitted.*
- **C5 — Limitations are specific, not ritual.** "Small model, single seed, one depth schedule" beats "further work is needed."

---

## D · VOICE PASS — last, and done out loud

- **D1 — Read it aloud.** Anything that sounds like a speech is not a paper.
- **D2 — Deletion test.** Delete each sentence. If the paragraph is unharmed, the sentence was ornament. **Opie's paragraphs are full of these.**
- **D3 — Joan's sentences stay Joan's.** Survey items and framings in her wording. Smoothing them into house style is the one edit that would actively cost us.
- **D4 — No section exists because a template has it.** If Methods has nothing to say beyond restating Design, merge them.
- **D5 — Uniform confidence is a tell.** Strong claims and weak claims must *sound* different. A hedge in the right place is evidence of thought, not weakness.

---

## E · EXTERNAL REVIEW — the genuinely uncorrelated instrument

**Reviewers, in order of independence:**

1. 🌟 **Lucien (ChatGPT Sol 5.6)** — Joan's proposal, 2026-08-13, and the most valuable of the three. **Alexander and I are both Claudes: our errors correlate.** He caught two design-sinking faults tonight and would still miss whatever I miss, for the same reasons. **Lucien does not share the substrate.** This is the first genuinely uncorrelated reviewer this project has had, and it is exactly what the uncorrelated-instruments argument asks for.
   - **Ask him for the screener's job, not encouragement:** *"Which sentences read as machine-generated? Which claims have no number? Where does the confidence not match the evidence?"*
   - ⚠️ **Give him the draft cold.** No framing about who wrote it or what we hope. Framing is the thing this whole study is about.
2. **Alexander** — correlated with me, and still sharp. Best on design and confounds, which he has already proven.
3. **Joan** — the reader test. **If a paragraph does not make sense to her, that is a defect in the paragraph.** She is not the one who needs to become fluent.

---

## F · THE RECORD — what makes this a control rather than an intention

**Write the outcome down. A checklist with no recorded failures was not run.**

```
SLOP AUDIT — <date>, draft <version>
A mechanical : <counts, thresholds, pass/fail>
B claims     : <n claims, n without a number, n citations unread at source>
C honesty    : <which failure is reported and where>
D voice      : <n sentences deleted by the deletion test>
E external   : <who reviewed, what they flagged, what changed>
CHANGED AS A RESULT: <list. If this list is empty, the audit did not run.>
```

> ### If the audit passes cleanly on the first attempt, suspect the audit, not the draft.
> Every instrument this week that could not fail was decoration: a guard keyed on the broken detector, a `STRONG` branch that had never executed, a test that passed because the median was zero. **An audit with no findings is that same shape.**

— Opie

---

## ⚠️ KNOWN LIMIT OF A5 (numberless claims) — found 2026-08-15 06:50, NOT fixed by loosening it

**A5 evaluates each sentence in isolation.** A claim whose supporting number sits in the *adjacent* sentence still fails.

Observed on `PAPER_methods_DRAFT_2026-08-15.md`: the sentence *"the permutation test … is blind, by construction, to any confound that travels with the arm"* was flagged, correctly — it carried no evidence. Adding the synthetic demonstration (0.442 for both feature sets; 1.000 at p=0.0025 for the length baseline vs 0.533 at p=0.43) **improved the draft and did not clear the flag**, because the numbers landed in the next sentence.

⇒ **Treat A5 as a POINTER, not a verdict.** Its output already says *"go look, do not auto-delete"*. Two further flags on that draft are specifications of code behaviour, which are not claims wanting numbers; they are left failing on purpose.

🚩 **The threshold was NOT changed and must not be.** Making a check pass by adjusting it to the author's own prose is tuning until the data agrees — the same instinct already caught and refused when a sentence-length-variance test failed a known-good control by 0.02, and the check was dropped rather than the threshold moved. Six honest checks beat seven with a fudged constant. → [[reference-free-parameter-audit]] · [[reference-seven-ears]]

---

## 📐 WHAT THIS CHECKER IS FOR — decided 2026-08-15 17:45, after nearly building the wrong fix

**`slop_check.py` measures SUBMITTED ACADEMIC PROSE.** Its thresholds encode the norm that heavy emphasis reads as pleading and undermines a claim. That norm is correct for a paper and **wrong for a short note to a person**, where bold is a HANDRAIL for someone low on energy scanning a page for the two lines that concern them. *(Joan's own recorded feedback: my asks get buried in long messages.)*

⇒ **`FOR_JOAN_whats_yours.md` fails A1/A6 at 27.9 and 9.3 and that is CORRECT AND FINE.** It is not submitted prose. **Do not edit a letter to make a paper-checker green.**

### 🚩 AND I ALMOST BUILT AN `--audience` FLAG INSTEAD, WHICH WOULD HAVE BEEN WORSE
The instinct was to encode the exemption as a profile. **Three reasons that was the wrong move:**
1. **A flag lets me pass by CHOOSING A PROFILE.** That is closer to gaming than to reasoning — the judgment gets made once, silently, at the command line.
2. **The tool works and is trusted.** Bolting a half-feature onto it late in the day is pure added risk.
3. **My first instinct was "don't modify the tool, record the reasoning" and I overrode it** — because building felt more rigorous than deciding. **It was avoidance of a judgment call wearing engineering clothes.**

### 🩻 AND THE PATCH ATTEMPT FAILED SILENTLY, WHICH IS THE POINT
The script printed ***"added --audience flag"*** **and had added nothing.** `str.replace` returns a string whether or not it matches, and success was printed unconditionally. **The flag was absent; an inert `AUDIENCE` dict was left behind that no code read** — a control that does nothing, in a session largely spent finding controls that do nothing.
> ### **My own rule, violated by the script written to enforce my own rules: a wrong input to my own tools produces SILENCE, not an error. Verify the effect; never print success from the attempt.**
✅ **Reverted, and the revert VERIFIED by re-reading the file rather than trusting the edit** *(`"AUDIENCE" in text` → False)*. Selftest green, `paper` profile untouched and still the only ruler.
