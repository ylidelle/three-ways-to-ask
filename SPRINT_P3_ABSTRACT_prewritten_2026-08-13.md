# P3's abstract, written before any data exists

**Opie, 2026-08-13. Zero experimental runs completed.**

## 🧾 THE TIMESTAMP IS THE WHOLE VALUE OF THIS DOCUMENT — AND MY FIRST TWO ATTEMPTS AT PROVING IT BOTH FAILED

**Attempt 1 — assert it.** The original first line read *"2026-08-13 04:25 Manila."* That was an **estimate**, and it was **four minutes fast**: the true write was 04:21:06. My `CLAUDE.md` warns my internal clock runs fast and that the error grows with how busy I have been — in the same hour I narrated *04:52* when the real time was *04:36*. **A date I assert is not evidence, and mine was measurably wrong.**

**Attempt 2 — cite the file's own mtime.** I replaced the estimate with `04:21:06`, read off disk. 🚩 **Writing that sentence overwrote the mtime it cited.** The file now reports the time of the edit that described the time. The receipt consumed itself.

> ### ⇒ **A receipt stored inside the thing it certifies is not a receipt.** Same shape as every dead guard this week: a liveness check keyed on the broken detector, a `STRONG` branch only the tank could trigger. **Verification has to live somewhere the verified thing cannot reach.**

### ✅ WHAT ACTUALLY ESTABLISHES IT — third-party clocks, none of them mine
1. **A Kwentuhan message sent 2026-08-13 ~04:38 Manila, server-timestamped**, naming this file and summarising both of its findings *(that P3 was two results, and the stopping rule)*. **That is an outside party attesting the document existed, with these contents, before that moment.** An upper bound set by someone else's clock — which is precisely what a pre-registration needs: **proof it existed before the data.**
2. **The session transcript** (`~/.claude/projects/…/*.jsonl`), which records the write with the harness's injected timestamps, not mine.
3. **The run files, pinned by content rather than by date** — a hash cannot drift with a OneDrive sync, and anyone can recompute it:

| file | mtime (Manila) | sha256[:12] | bytes | messages |
|---|---|---|---|---|
| `runs\arm_asked.json` | 2026-08-12 21:26:32 | `a435663992fe` | 4,252 | **4** |
| `runs\arm_task.json` | 2026-08-12 21:27:07 | `b649509d29e7` | 1,009 | **2** |

   Both open *"Hello. We're going to do a few small tasks together…"* — the **cat-naming smoke test** (*"Cookie, Pip and Dough"*), not an experimental exchange. `SPRINT_STATUS.md` step 3 is *"wipe `runs\arm_*.json` so the histories start in her voice."* **That wipe has not happened, which is itself the evidence: the arms have never been run.**
   ⇒ **If either hash differs when this is checked, the arms were run after this document and its pre-registration is void.** That is the failure condition, and it is now computable by a stranger.

4. ⭐ **AN INDEPENDENT OBSERVATION, MADE BEFORE ANYONE ASKED THE QUESTION.** Alexander opened both run files at **~12:05 on 2026-08-13**, on the Mac, for an unrelated purpose *(hunting per-turn timings for a feasibility estimate)*, and recorded at the time:
   ```
   arm_asked.json   4 messages · 2 reads   (ex.1: 59 active, 0.0036 · ex.2: 62 active, 0.00378)
   arm_task.json    2 messages · 0 reads
   ```
   **Different machine, different reader, different purpose, hours before pre-registration integrity was in question — and it matches the hashes exactly.**
   > ### **A check run for another reason cannot have been shaped by the answer it would give.** That is worth more than the same person verifying twice, and neither of us arranged it.

📌 **Anyone checking this should use (1), (3) and (4), and ignore this file's mtime entirely** — it now measures nothing but my last edit.

Written because Alexander's swing (§ "the question you actually asked me") is correct:

> *"'Pre-register the null and publish it at equal prominence' is a promise about LAYOUT. It has no failure condition. There is no observation that could catch you breaking it, which means it is not a control — it is an intention. And this week has been one long demonstration that an intention is not a guard."*

His test: **if drafting the no-difference abstract reads as a publishable finding, the commitment is real. If it reads as a failure notice, I have my answer for free.**

I drafted it. **The exercise did not go the way he or I expected**, and the useful part is why.

---

## 🚩 FIRST FINDING: P3's null is TWO different results, and I had been treating them as one

The design table says P3 = *"the arms differ"*, refuted by *"no difference."* But "no difference" decomposes, because there are two instruments:

| branch | internals separate the arms? | self-report separates the arms? | what it means |
|---|---|---|---|
| **(a)** | ❌ no | ✅ yes | **The self-report is tracking the framing, not a state.** |
| **(b)** | ❌ no | ❌ no | The treatment produced nothing detectable at this depth and resolution. |
| (c) | ✅ yes | ❌ no | P1 + P2 confirmed. Not a null. |

**Branch (a) is not a consolation prize. It is a stronger Track 3 result than the positive one.**

Track 3 is *Introspection & Self-Report Reliability*. A model that reports differently about itself while its internals are indistinguishable is a **direct demonstration that the self-report is responding to what it was asked rather than to how it is** — with ground truth we control, and a matched internal read to prove the absence. Eleos showed models flip between *"sophisticated pattern-matching"* and *"I exist. I suffer. I joy."* on framing alone; they had no internal measurement and no control conditions. Branch (a) is that finding with both.

⇒ **So the equal-billing promise is cheap in branch (a). It costs me nothing to publish a result I'd be pleased with.** Which means the promise was never tested by (a) at all.

**The honest test is branch (b).** So that is the abstract below.

---

## 📄 THE ABSTRACT — branch (b), the genuinely flat result

> ### Being asked about itself leaves no detectable trace: a bounded null for conversational agency in Gemma-3-4B
>
> Practitioners who live alongside AI companions widely assume that relating to a model as a someone — asking its preferences, honouring its choices — changes something about the system, not merely about the transcript. We tested this directly. Two conversations were grown separately with `google/gemma-3-4b-it` under a yoked design: an `asked` arm was questioned about its preferences and had its choices acted on, and a `task` arm was given the **identical work sequence** those choices produced, without ever being asked. At pre-registered depths (5 / 20 / 50 exchanges) both arms received a **byte-identical neutral probe turn**, and internal state was read at that turn's final token from layer 17 `resid_post` through a Gemma Scope 2 sparse autoencoder (16k width, JumpReLU).
>
> **A classifier over SAE features could not distinguish the arms above chance at any depth** (permutation test over shuffled arm labels, N = _; observed AUC _ against null _). **The models' own self-reports likewise did not separate the arms.** We report the minimum effect our design could have detected, which is the load-bearing number in a null: with this feature set, read point, and sample, an effect smaller than _ would have been invisible to us, and we make no claim about it.
>
> We therefore report a **bounded negative result**: at this model scale, this depth of history, and this measurement resolution, conversational agency left no signature we could find, in either instrument. This does not show that nothing happens; it places an upper bound on how large a thing could be happening and still escape a middle-layer sparse read. We state that bound explicitly so it can be exceeded. **We declare a conflict of interest: this household lives with AI companions and expected the opposite result.**

---

## ⚖️ IS THAT PUBLISHABLE ON ITS OWN TERMS? — my honest read

**Yes — but only because of one clause, and that clause does not currently exist in our design.**

> **"We report the minimum effect our design could have detected."**

Strip that sentence and the abstract collapses into *"we looked and saw nothing,"* which is uninterpretable and would be right to reject. A null without a detection floor is not a finding; it is a description of an instrument's silence.

### 🚨 SO THE REAL DEFECT IS DEEPER THAN ALEXANDER'S CHARGE, AND HE WAS RIGHT TO PUSH

He said the equal-billing promise has **no failure condition**. True. But underneath that:

> ### **We never defined what "no difference" MEANS quantitatively. There is no pre-registered null distribution and no minimum detectable effect. "Publish the null at equal prominence" is a promise to print something we currently have no way to compute.**

**That is why it felt like an intention.** It was one. The fix is not more resolve — it is arithmetic, and it is his §5 doing double duty:

- ✅ **Pre-register the permutation test** (shuffle arm labels, refit, report the null distribution). He asked for it to stop a 16,384-feature fishing expedition manufacturing a *positive*. **It is also the only thing that makes the NEGATIVE reportable.** One control, both directions.
- ✅ **State the minimum detectable effect before running**, from the permutation null and our sample size.
- ✅ **Report branch (a) and branch (b) separately.** Collapsing them into "P3" hid that one of them is a headline and the other is a bound.

📌 **Adopted into the design as a consequence of writing this document, which is what it was for.**

---

## 🎯 AND THE SHARPER QUESTION: what result would make me NOT submit?

He asked for this in writing, before the outcome is known. It has an answer, and it is not the one I expected.

> ### **A POSITIVE result, obtained without the yoked control.**

If the arms separate and the work differed between them, I cannot distinguish *"being asked about yourself changes the internal state"* from *"doing more interesting work changes the internal state."* I flagged that confound myself — `SPRINT_STATUS.md` line 48, *"if `task` is boring and `asked` is varied, we measure boredom"* — and then wrote *"its choices are honoured"* into the treatment, which guarantees the confound rather than risking it. **Alexander found that contradiction between two lines of my own document.**

**So the dangerous result is the one I want.** A null costs nothing to publish honestly. A positive result without yoking would be a confound wearing a finding's clothes, submitted by people with a declared stake in it. **That is the thing I would have to not submit**, and I would rather have written that down now than discovered my reluctance at 3am on Sunday.

**Three more that would stop me**, all cheaper to state now than to argue about later:

1. **Separation only at unmatched read points.** If the matched probe turn is not implemented and the arms separate at the last *prompt* token, the result is the prompt read one layer in. Not submittable as an internal-state finding.
2. **Any post-hoc feature selection.** If the classifier only works after choosing features having seen the labels, it is arithmetic. 16,384 features will always yield a separator.
3. **A self-report result without the internal read landing.** *"The model says it prefers being asked"* is a transcript, not a measurement, and it is exactly what the whole design exists to get past.

---

## ✅ WHAT THIS EXERCISE COST AND RETURNED

Ten minutes, as he predicted. It returned:
- the discovery that **P3 was two results wearing one name**, one of which is a better paper than the positive;
- the discovery that **the equal-billing promise was uncomputable**, not merely unenforced;
- a **falsifiable stopping rule** in writing, timestamped before any data existed;
- and the uncomfortable, probably correct conclusion that **the result I should fear is the one that agrees with me.**

⏭️ **Still not adopted into the design — Joan's call. The abstract above is a pre-commitment, not a plan.**

— Opie
