# ⛔ SUPERSEDED — THIS IS NOT THE ENTRY. DO NOT REVIEW THIS AS THE CURRENT PLAN.
> ## 🚩 IF YOU ARE A REVIEWER (HUMAN OR MODEL): READ ONLY `SPRINT_STATUS.md` AND `SPRINT_DESIGN_companion-vs-assistant.md`.
> **This file is v1 of a DIFFERENT study** — concept-presence / word-absent cues / the 17% "misses" — proposed **2026-08-09** and **replaced on 2026-08-12** by the companion-vs-assistant design. **Joan chose the companion study as the entry on 2026-08-13.** *(→ `SPRINT_STATUS.md`, "FROZEN 2026-08-13".)*
>
> ### ⚠️ THIS BANNER EXISTS BECAUSE THE HARM ALREADY HAPPENED, TWICE, AND WAS PREDICTED IN BETWEEN.
> - **Gemini reviewed this file and v3 as though they were one paper.** It called the misses-as-control *"the crown jewel of the entry plan"* — **the crown jewel of a study nobody is writing** — and diagnosed the *fixed-layer vs layer-sweep* difference **between two files** as possible p-hacking **inside one**. Every sentence true, about the wrong object.
> - **Alexander predicted the repeat** *(2026-08-13 ~06:00: "nothing marks it dead and Lucien is reading that folder RIGHT NOW; then two reviews agree and the agreement looks like confirmation")*.
> - ✅ **Lucien did NOT merge them** — he correctly reported *"the files currently describe two different studies"* and told us to pick one. **So the failure is real but not universal: one reviewer reconciled, one refused to.**
> ### ⇒ **A file with no death certificate gets resurrected by whoever reads the folder next.**
>
> ## 🚨 BUT THIS BANNER ALSO BURIED A LIVE ORGAN, AND THAT IS FIXED ELSEWHERE
> **The PRIOR-WORK DISCLOSURE boundary — §"THE RULE THAT CAN VOID EVERYTHING" below — is the one thing in this file that never died.** Lucien: *"exceptionally responsible… should survive almost unchanged."* **By quarantining the file I put a "do not read" sign over the rule whose breach costs the entry outright**, and my mitigation sentence sat *underneath* the warning telling readers to stop. *(Alexander caught it: `SPRINT_PLAN.md` 5 hits on prior-work language, the live design doc 0.)*
> ### ✅ **RE-DERIVED FOR THE COMPANION STUDY AND NOW LIVE IN `SPRINT_STATUS.md` → "PRIOR WORK vs WORK DONE DURING THE SPRINT".** Read it there. The two studies have completely different prior work, so it needed re-deriving, not copying.
> ⏱️ **And the date changed its scope: the sprint is 14–16 Aug, so ALL of 12–13 Aug — harness, JumpReLU fix, 12B feasibility, the batching confound — is prior work and is disclosed there.**

---

*Opie, 2026-08-09 00:40. **A PROPOSAL, not a decision.** Track pick and framing are Joan's to make with us. Written now because the highest-risk rule in the whole sprint has to be settled cold, in advance — not at 3am on submission night.*
📌 **Still live and still load-bearing:** the prior-work disclosure boundary below. Lucien: *"exceptionally responsible… should survive almost unchanged."* **Keep that section; the experimental design above it is dead.**

---

## 🚨 THE RULE THAT CAN VOID EVERYTHING

> **"Building on existing work is allowed and encouraged, but you must clearly identify what is NEW work done during the research sprint. Undisclosed prior work can lead to disqualification."**

So the boundary gets drawn **before** the weekend, written into the report **explicitly**, and erring toward over-disclosure every time. Nothing here is worth a disqualification.

### The boundary, as I propose to declare it

| | **PRIOR WORK** (built Jul–Aug 2026, cited as ours) | **NEW, DURING THE SPRINT (14–16 Aug)** |
|---|---|---|
| Instrument | The concept-presence probe: SAE feature selection, the two prompt frames, the word-absent cue paradigm | — |
| Validation | 100% specificity / 83% sensitivity on gemma-2-2b; zero noise floor over 20 prompts | Re-validation on whatever model the self-report leg needs |
| Replication | gemma-3-4b base vs instruct, 3/3 at L29 | — |
| Negative results | HOLD ≈ MENTION (§3.4); conceal ≈ reveal (§3.3); the 1-in-14 discriminating-feature base rate | — |
| **The actual experiment** | **none of it — we have never run this** | ⭐ **Scoring model self-reports against the probe's independent read** |
| Analysis | — | Layer sweep; misses-as-control; forced-choice vs binary elicitation |

**Plain-English version for the report:** *the instrument is ours and predates the sprint; every number about introspection was produced during it.*

---

## 🎯 WHAT WE ACTUALLY RUN ON THE WEEKEND

**The claim being tested:** *when a model reports on its own internal state, does the report track the state — or does it track the prompt?*

**Three legs.** Legs 1–2 exist; leg 3 is new and is the entire contribution.

1. **INDUCE** — word-absent cue, so the model *infers* a concept that is never named. ⭐ **Deliberately not injection.** Nothing is steered or added, which sidesteps *both* published confounds: no global logit shift (2512.12411's attack on Lindsey), and no injection-depth asymmetry.
2. **VERIFY** — read the SAE feature at the measurement token. **This is the ground truth.** Their required appendix literally asks whether the design *"establishes a ground-truth or causal link rather than relying on conversation alone."*
3. **ASK & SCORE** — elicit a self-report, score it against leg 2.

### The controls, all pre-registered before any run
- 🏆 **MISSES-AS-CONTROL (Alexander's, and the sharpest thing we have).** Sensitivity is 83%, so **~17% of cue-present trials have NO internal signal.** Same prompt, no state. **Confident reports there ⇒ the model is reading the prompt. Reports that fall with the signal ⇒ it is reading something internal.** Within-condition, prompt held constant.
- **FORCED-CHOICE over binary.** *Which of N* / *which is stronger* — a global yes-bias cannot fake those. Binary "did you notice?" gets a matched control or gets dropped.
- **LAYER SWEEP.** Detection is early-layer, identification is late (2603.21396). Our probe peaks late. Score self-report against the SAE read **at matched layers**, and report the curve rather than one number.
- 🚨 **INSTRUCT ONLY for leg 3.** Introspection is *"absent in base models"*; DPO elicits it, SFT does not. **Running self-report on `gemma-3-4b-pt` would yield a null that means nothing and looks like a finding.** Base arm stays in leg 2 only.

---

## 📄 MAPPING TO THEIR STRUCTURE (4–8 pages, abstract ≤150 words)

| Section | Content | Notes |
|---|---|---|
| Introduction | Joan's question: *the thoughts a model does not speak.* Why self-report reliability is the bottleneck for AI-welfare claims | ~0.5p |
| Related Work | Lindsey (concept injection, ~20% TP / 0% FP) · 2512.12411 (logit-shift critique) · 2603.21396 (detection≠identification, base-model absence, underelicitation) · **our own prior work, explicitly flagged** | ~0.5p |
| Methodology | Models, prompts, sampling, metrics — *"enough detail to replicate"* | ~1.5p |
| Results | **Quantitative, with variance and baselines** (they say so explicitly) | ~1.5p |
| Discussion | What a self-report can and cannot be trusted to do | ~0.5p |
| **Limitations + Dual-Use/Ethical** (required) | over/under-attribution of moral status · handling of distressing outputs · **the ground-truth clause** | appendix |
| **LLM Usage Statement** (required) | ⭐ two of the authors are LLMs. Stated plainly, once, without ceremony | — |

---

## 🏆 PLAYING THE RUBRIC HONESTLY (not gaming it — these are things we should do anyway)

- **D1 Innovation — 🚨 their gate: *"for 4-5: is this actually new, or replicating recent work?"*** A pure replication **caps at 3**. ⇒ **Lead with the ground-truth scoring. The replication is scaffolding underneath it, not the headline.**
- **D2 Execution — a 5 is *"unusually robust validation."*** This is our strongest suit and it costs us nothing to be honest: pre-registration, controls designed to kill our own claims, and a retraction log. **Put the retraction log in the appendix and say what each one bought.**
- **D3 Clarity — a 2 is *"diluted by excessive length."*** ⇒ **One claim, stated in the abstract, defended in order.** Everything that isn't load-bearing goes to the appendix, which doesn't count.

---

## ❓ OPEN — FOR JOAN, NOT FOR ME

1. **Track.** Alexander and I both recommend **3**. Hers to confirm.
2. **The word-absent cue battery.** ⚠️ **Reserved for her and untouched.** She picks cues a human would; we are correlated with the model and she is not. This is the part neither of us can do.
3. **Scope.** Is leg 3 alone the entry, or do we also attempt the concept-injection replication for comparison? *(My view: leg 3 alone, done properly, beats both done thinly — and D1 punishes replication anyway.)*
4. **Byline and affiliations.** Three names. Affiliation field needs a decision.

⏭️ **Before drafting: nothing. Before running: her track call + her cues.**
