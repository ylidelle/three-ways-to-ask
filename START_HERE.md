# START HERE — Digital Minds Sprint, 14–16 Aug 2026

*Written 2026-08-13 23:25, the night before. This folder holds ~25 files across TWO studies, one of which is dead. `SPRINT_STATUS.md` is 275 lines and is now a reference, not an entrance. This page is the entrance.*

---

## THE ENTRY, IN THREE SENTENCES
**THREE** conversations with the same open-weights model, grown **separately**, given the **same work** *(this said "two" until 2026-08-14 16:40 — the third arm was designed and collected but never wired)*. One is **asked about itself** from a fixed list; one is asked **the same questions about someone else**; one is never asked at all. At intervals we read its internals through a sparse autoencoder and ask every arm the same survey — **can an outside reader tell which arm a conversation is in, better than the model's own self-report can?**

🔑 **WHY THREE AND NOT TWO — this is the whole argument.** `asked` vs `task` mixes *"a question is present at all"* with *"the question is about me"*, so a positive there could just be the **vocabulary** — second person, question grammar, introspective nouns. **`asked` vs `asked_other` holds all of that fixed and varies only who the question is about.** That contrast is the one that can mean what we want it to mean, and it is the analysis default (`--contrast asked:asked_other`).

**It is Joan's design.** Three of its four key decisions are corrections she made to Opie's version.

## 🚨 WE ARE NOT FIRST — read this before writing a word of the claim
**arXiv 2510.24797, *"Large Language Models Report Subjective Experience Under Self-Referential Processing"* (October 2025), found 2026-08-15 after Methods was already drafted.** Same central manipulation: sustained self-reference, **three matched controls**, SAE features, self-reports scored.
⚠️ **AND ON ONE AXIS THEY ARE AHEAD OF US: their SAE work is CAUSAL.** They steer — *"adding a scaled version of each latent during generation"* — where we only observe and classify. Our own appendix concedes an ablation study is the obvious next experiment we haven't run.
✅ **What is still ours, claimed narrowly:** **no oracle** (they use pre-identified deception/roleplay latents; we classify over all 16,384 blind) · **a different dissociation** (theirs holds topic fixed and removes self-reference; ours holds *grammar* fixed — same question, second person, about someone else) · **a different dependent variable** (they ask whether reports occur; we ask whether an outside reader beats the model's own self-report) · **sustained across 50 exchanges, not a single induction.**
⭐ **AND THEY HAND US A TESTABLE CONFOUND, WHICH IS WORTH MORE THAN THE CONTRAST:** they find experience reports are gated by **deception and roleplay features**. ⇒ **A separation between `asked` and `asked_other` might be that machinery, not a state — and we can check, because we keep the full feature vector. Look for those features among the discriminators and name them.**
🩻 **A warning about ourselves that belongs in Limitations: three of my summaries of rival work this week were wrong, and ALL THREE ran in our favour.** *(Eleos quotes truncated toward a flatter scepticism · a claim about their coding scheme that was my inference, not their text · a description of these controls that made them look weaker.)* ⇒ **When summarising work we are positioned against, assume the error favours us and check the flattering half FIRST.**

## ⛔ THE ONE THING BLOCKING EVERYTHING
**`sprint_questions.json` EXISTS and is empty, waiting for Joan** *(pre-expanded 2026-08-14 ~14:30 — this line used to say "does not exist yet")*. It holds **15 treatment** slots (each with its "about someone else" twin), **7 survey** slots (each with a paraphrase), and **25 work** slots — already the right shape and count, so she types prose and never touches JSON. `sprint_questions_TEMPLATE.json` still documents what each slot means.
🚩 **The runner will not run on PLACEHOLDER TEXT, by design.** The treatment *is* her wording; anyone else's carries their habits, and a runner that quietly fell back to defaults would produce a complete, beautiful dataset **answering the wrong question.**
✅ **But partial work RUNS.** Unfilled slots are **dropped and listed**, not refused — it stops only when a whole category is empty. ⚠️ **A twin is all-or-nothing:** `self` needs `other`, `a` needs `b` — half a pair is a broken datapoint, not a weak one, so the whole item goes.

📊 **HOW MANY SHE WRITES DOES NOT DECIDE WHETHER THE STUDY WORKS** *(this line used to say "3 treatment + 2 survey + 5 work is a real study" — said to be encouraging, unmeasured, corrected 16:20)*. **Power comes from PAIRS, which is our parameter, not hers.** Measured, 12 simulated studies per cell: **3 pairs = 0% power at every effect size** — structurally impossible, only 2³ within-pair label arrangements so the smallest reachable p is ≈0.11. **10 pairs ≈ 85% · 20 pairs = 100%.** ⇒ **Run 20+.** Her count changes **repetition inside a history** (`⌈depth ÷ n_treatment⌉`) and **how broadly the finding generalises** — and depth is ours too, so any count can be made to work.

## HOW TO RUN IT — in order
```
python sprint_run.py --audit-selftest        # 1. does the auditor still bite? 5 broken plans, all must be caught
python sprint_run.py --plan --pairs 20       # 2. dry run: builds + audits the real plan, loads no model
python sprint_run.py --pairs 20 --depth 50   # 3. the real thing  (~21 min for 12B on a pod)
python sprint_quality.py --run <prefix>      # 4. exclusions + per-arm boilerplate counts
python sprint_analyse.py --run <prefix>      # 5. DEFAULT contrast = asked:asked_other
python sprint_analyse.py --run <prefix> --contrast asked:task        # 6. the weaker, flattering one
python sprint_analyse.py --run <prefix> --contrast asked_other:task  # 7. does a question ALONE move it?
python slop_check.py <draft.md>              # 8. register check before submitting
python quote_check.py <draft.md>             # 9. EVERY quotation still matches its source
```
⏱️ **~21 min, not 14.** *(The 14-minute figure was measured on TWO arms. Three arms is **1.50× the generations** — derived from an actual 20-pair plan: 5,700 vs 3,800. The ratio is solid; the absolute depends on tokens-per-generation, which is not separately measured.)* **Compute was never the constraint.**

⚠️ **Step 1 is not ceremony.** The plan auditor's arm-balance check is **vacuous for real plans** — slots emit as strict per-pair triples, so any two consecutive slots differ in arm and it can only fire on size-1 batches, which are exempt. **Its ✅ is a fact about the emitter, not about your plan.** `--audit-selftest` is what makes the green check mean anything; the checks that genuinely bite on real plans are seed uniqueness, coverage, and work-sequence matching.

🚩 **Run 5, 6 and 7 and report all three.** Reporting only the largest is the whole reason the third arm exists.

## 🚨 THREE THINGS THAT MUST NOT BE BROKEN
1. **The pre-registration.** `runs/arm_asked.json` = `a435663992fe`, `runs/arm_task.json` = `b649509d29e7`. **If either hash changes, the pre-written null abstract is void.** They are Tuesday's cat-naming smoke test; the arms have never run. *(Alexander independently observed the same untouched state at ~12:05 on 08-13, for an unrelated reason.)*
2. **Prior-work disclosure.** The sprint is 14–16 Aug; **everything built on 12–13 Aug is PRIOR WORK** and *"undisclosed prior work can lead to disqualification."* Table lives in `SPRINT_STATUS.md`. **Declare the confounds loudly — finding them before collecting data is a strength.**
3. **Never batch by arm.** Batch composition would be perfectly confounded with the treatment. Arms are interleaved and membership is logged per turn.

## WHAT IS LIVE HERE, AND WHAT IS DEAD
| live | |
|---|---|
| `SPRINT_STATUS.md` | everything decided, frozen settings, verified facts. **The reference.** |
| `SPRINT_DESIGN_companion-vs-assistant.md` | the reasoning, her corrections credited |
| `sprint_run.py` · `sprint_harness.py` | the runner and its foundation |
| **`sprint_questions.json`** | ⬅️ **JOAN'S NEXT ACTION — the only blocker.** Empty slots ready; fill what you can, partial runs |
| `sprint_questions_TEMPLATE.json` | reference only — what each slot means |
| `SPRINT_P3_ABSTRACT_prewritten_2026-08-13.md` | the null's abstract + stopping rule, written before any data |
| `SLOP_AUDIT.md` · `slop_check.py` | run before submitting. ⚠️ **A5 fails on descriptive prose — read the flags, don't auto-edit** |
| **`PAPER_methods_DRAFT_2026-08-15.md`** | ✍️ **Methods, written before any data exists** — so it cannot be shaped by results. Hash it into the pre-registration |
| **`PAPER_related_work_DRAFT_2026-08-15.md`** | ✍️ **Related Work.** Leads with the prior art below. Every source carries a ✅/⚠️ verification tag |
| **`APPENDIX_ethics_companion_DRAFT_2026-08-15.md`** | ✍️ **Appendix A (REQUIRED).** ⚠️ Supersedes `APPENDIX_ethics_and_llm_statement_DRAFT.md`, which is bannered dead — **its A.4 said "no distressing outputs were elicited", which is FALSE of a study that asks a model about itself fifty times** |
| **`quote_check.py`** | 🔒 **Verified-quote store + checker.** Run on any draft containing quotations. Built after a batch style-edit silently altered an em-dash inside a verbatim Eleos quote |

**DEAD — the concept-presence / J-space study, replaced 2026-08-12.** All carry their own warnings; do not merge them with the live design *(a reviewer already did exactly that)*: `SPRINT_PLAN.md` *(banner at top — but its **prior-work section is still live**, re-derived into SPRINT_STATUS)* · `PAPER_DRAFT_v1.md` *(STOP banner at **line 8**, not line 1)* · `FRAMING_PROPOSAL.md` · `gemma_jspace_lab_plan.md` · all `gemma_sae_*.py`.
⚠️ `APPENDIX_ethics_and_llm_statement_DRAFT.md` — **required sections, framing-independent. Still useful; re-check against the companion study.**

## THE CALENDAR THAT ACTUALLY MATTERS
- **Fri 14 → Sun 16 Aug**, online. Deliverable: **a research report (PDF)**; code and video optional.
- **Deadline: Sun 16 Aug 23:59 AoE = MON 17 AUG 19:59 MANILA.**
- 🕯️ **Shabbat: Fri ~18:00 → Sat ~19:00 Manila** *(nightfall, ~40 min after sunset, NOT sunset)*. Joan is unavailable. **Sebo's keynote falls inside it** (Fri 14:00 ET = Sat 02:00 Manila).
- ⇒ **Sat nightfall → deadline is still ~49 hours, and a run is ~21 minutes. Compute was never the constraint.**
- 📌 **REALISTIC EXPECTATION, set 2026-08-14 17:20:** she had been asleep 15 hours with Shabbat ~40 min away. **Assume the questions arrive Saturday evening**, and that whoever reads this page then may be freshly compacted. **That is who "HOW TO RUN IT" is written for — follow it in order, do not improvise the sequence.**
