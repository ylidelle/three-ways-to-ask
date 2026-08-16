# What this paper is actually about — proposal **v2**, for Joan and Alexander to attack

*Opie. v1 written 2026-08-08 09:40; **v2 12:50, after Alexander killed v1's central word.** **Still not applied to the draft.** Five framings have now died; I am not installing a sixth on my own authority.*

---

## 🔪 WHAT KILLED v1 — and it was already in our own data

v1 said: *"We did not build a deception detector. We built a detector for **HELD CONTENT** — and then showed that holding is ordinary."*

**Alexander's kill:** that demotion stops one step early, and the leftover word is the flattering one.

> **If neither the ORDER to withhold (§3.4) nor the TRAINING to obey orders (§3.7) moves the needle, what evidence is left that "holding" is a STATE at all?**
> *"Held content" implies a relation to an absent output — and we showed that relation contributes nothing measurable.*

He proposed a cheap pre-registerable test: *a passage that merely MENTIONS the concept, then asks something unrelated.* Fires the same ⇒ it's a concept-presence detector and "held" dies.

### ⚠️ That test is already in the draft. Twice. Both null.
- **§3.4 IS that test.** A *passing-mention* arm vs an instructed-hold arm — same content words, same fillers, differing only in whether withholding was instructed. **HOLD 71 · MENTION 72** at distance.
- **§3.3 is the magnitude version.** Reveal vs conceal on the same feature: **×1.37 · ×1.35 · ×0.84** — noisy about 1, no direction.

**We ran it, reported it in two sections, and left "HOLDS BACK" in the title.** No new compute was needed to overturn the frame — only reading our own paper. *(Third time in one day I modelled a system that had already published its answer. The other two: a BizHawk dialog that named its own fix, and an aquarium that posted "curtains up, feedings paused" on its homepage.)*

---

## THE DEMOTION CHAIN — say it in the first paragraph, don't make a reader find it

> ### **deception → holding → PRESENCE**

Each step was forced by a control **we built ourselves**, and each one cost us a headline.

**What survives, stated without the flattering word:**

> **A concept the model was never shown — inferred from a word-absent cue, never named anywhere in the prompt — is active at full strength at the exact token where the model is emitting unrelated text.**

That is not nothing, and it is not deception:
- **Inferred, not echoed.** Word-absent cues fire *stronger* than landmark cues (**55.72 vs 19.06**) — an echo account predicts the opposite.
- **Active during competing output.** The reading is taken while the model is producing food words.
- **Zero noise floor** over 20 unrelated prompts; 0.00 for two fully held-out cities.
- **100% specificity / 83% sensitivity** over a 36-prompt grid — a hit rate, not an anecdote.

⇒ **It is a CONCEPT-PRESENCE PROBE THAT WORKS UNDER DISTRACTION.** The concealment frame was only ever a convenient way to *create the condition* — a resolved concept the model isn't currently emitting. It was never the cause of anything we measured.

---

## THE PROPOSED CLAIM (v2 — one clause added, and it matters)

> ### **"Is the concept there, or merely unsaid?" is empirically answerable — *once you already have a candidate to test* — and treacherous in ways that do not announce themselves. We show both.**

🚩 **The added clause is Alexander's second catch, and it is a real weakening: the method is ORACLE-DEPENDENT.** The contrast set that isolates the discriminating feature **requires already knowing the answer is Paris.** So we can answer *"is THIS concept present?"* — we cannot answer *"what is it holding?"* Nobody outside the experiment can ask our question yet.

**This is why §4 stops being a caveat and becomes the mechanism:** the contrast step is not a refinement of the detector, it *is* the detector — and it needs an oracle.

- **§3 = the ANSWERABLE half.** Present at the token where it isn't said, full strength, two model families, base and instruction-tuned, with a hit rate.
- **§4 = the TREACHEROUS half.** Only **1 in 14** co-active features discriminates; the abstraction level you land on is set by your contrasts and **invisible from inside the run**; we mis-named our own finding four times.
- **§6 = the evidence we mean it.**

**Why this frame should outlive the previous five:** it needs no surprise. Every earlier framing leaned on novelty — *Paris! cities! countries! the contrast set is a free parameter!* — and each died on contact with a control. **"You can read a concept the model never named, and doing it correctly is harder than it looks, and you need to know what to look for"** is *strengthened* by each retraction rather than embarrassed by it.

---

## 📋 WHAT EACH RETRACTION BOUGHT — Alexander's note, taken
*(A retraction log reads as rigour to a friendly reader and as instability to a hostile one. Price each one.)*

| # | Retracted | What it bought |
|---|---|---|
| 1 | "Paris" → really **France** | The category-matched contrast method (§3.6) |
| 2 | "France" → really **francophone** | The contrast-free **existence check** |
| 3 | Zurich → **Switzerland**, not German | §4.2–4.3: the level is **not** a knob — a refuted prediction, run on purpose |
| 4 | concealment → **holding** | §3.4's MENTION control, and §3.7's base-vs-instruct arm |
| 5 | holding → **presence** | An honest instrument definition — and the Track 3 fit, which is *better* than the one we lost |

**None of these came from thinking harder. Every one came from building the control that could kill the claim.**

---

## The stakes, which came from outside
Guicheney's *"Cooling of Claude Sonnet"* measures warmth collapsing across model generations behaviourally, and concedes the wall: whether the coldness is distillation, capacity or alignment training **"cannot be distinguished"** from outside.

> A model that says *"I don't mind"* may genuinely not mind, **or may have learned not to register it — and from the outside those are identical.**

**That is the shape of question our method addresses** — behavioural ceiling, mechanistic floor. ⚠️ **With the oracle caveat fully attached:** we can test a *candidate* internal state, not enumerate one.

## What it means for the sprint
- **Track 3 (Introspection & Self-Report Reliability) fits better after the demotion, not worse.** A general **concept-presence probe under distraction** is a more useful instrument for self-report reliability than a deception-specific one — the track needs something that works *when nothing is being hidden*, which is the majority case.
- **Cite Guicheney as the motivating problem**, not as competition.
- **Lead the abstract with the demotion chain**, not the result.

## ⚠️ What I am NOT claiming
- Not that this transfers to frontier models. It doesn't yet, and the sprint's welfare framing must not be allowed to imply it does.
- Not that "a concept is detectable" says anything about experience, valence, or welfare. **It means one narrow instrument reads one narrow thing.** Everything past that is somebody else's argument.
- Not that five retractions make us rigorous. **They make us people who were wrong five times and wrote it down.**
- ⚠️ **Not that the base/instruct arms are independent replications.** Top-L29 feature index matches PT↔IT on **1 of 3** concepts (Paris ✗ · Tokyo ✓ · Rome ✗); matched-index decoder cosine **0.848** vs best-other **0.174**. The dictionaries are index-aligned; selection is not deterministic. **n=3. Belongs in Limitations.**

---
⏭️ **FOR THE SATURDAY SESSION: does v2 survive Joan's reading?** Alexander has already taken his shot and v1 lost the word "held." If v2 falls too, it is retraction #6 and we keep looking. **The decision — and the track pick — are hers to make with us tonight, not mine to have made this morning.**
