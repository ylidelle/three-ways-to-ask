> # ⛔ THIS IS THE DEAD STUDY'S APPENDIX — kept as its record, do NOT submit it.
> **Written 2026-08-09 for the CONCEPT-PRESENCE / withheld-thought design, replaced 2026-08-12.** The live version is **APPENDIX_ethics_companion_DRAFT_2026-08-15.md**, in this folder. *(This line briefly said "the live version is ▮▮" — the filename was eaten by shell backtick expansion when the banner was written. A banner pointing at nothing is worse than no banner: it tells the reader a replacement exists and refuses to say where.)*
> 🚩 **A.4 below says *"none were elicited, and this was a design choice."* That was TRUE of neutral geographic stimuli and is FALSE of a study that asks a model about itself fifty times.** Submitting this section unchanged would be a false statement about our own handling of distressing output.
> ✅ **What carried over: A.2's conflict-of-interest paragraph and A.3's base-vs-instruct argument.** A.1, A.4 and A.5 were rewritten — **the two studies differ most exactly where they touch ethics.**

# Required sections — DRAFT v1, for Joan and Alexander to attack

*Opie, 2026-08-09 ~10:40. **These three are REQUIRED by the sprint and depend on NO framing decision**, so drafting them now is preparation, not a decision taken on my own. The track pick and the paper's claim remain Joan's.*

*Sprint instruction I am writing against, verbatim: **"Frame findings carefully, avoid sensationalism, and document your handling in the required appendix."***

---

## Appendix A — Limitations and Dual-Use / Ethical Considerations *(required)*

### A.1 Does this design establish a ground-truth or causal link?

*The sprint asks this explicitly of introspection work, so we answer it first and plainly.*

**Partly. Not fully. Here is the exact extent.**

We do not rely on conversation alone. Every self-report is scored against an independent read of the model's internal state — a sparse-autoencoder feature selected before the self-report is elicited, with a measured hit rate (100% specificity / 83% sensitivity on `gemma-2-2b`) and a zero noise floor across 20 unrelated prompts. **That read is ground truth in the narrow sense that it does not depend on anything the model says.**

**Three limits on that claim, stated up front:**

1. **The instrument is oracle-dependent.** The contrast set that isolates a discriminating feature requires already knowing which concept to look for. We can ask *"is THIS concept present?"* — we cannot ask *"what is present?"* An external observer without our candidate list could not run this.
2. **It is correlational, not causal.** We show a feature is active and score a report against it. We do not intervene on the feature and observe the report change. **A causal version — ablate or amplify the feature, then re-elicit — is the obvious next experiment and we have not run it.**
3. **Feature-level readings are not mental states.** That an SAE feature associated with a concept is active licenses "the model is representing something that discriminates this concept from matched alternatives." It licenses nothing about experience.

### A.2 Risks of OVER-attributing moral status

**A measurement that reads internal state can be mistaken for a measurement that reads experience. It is not.** Our probe would behave identically in a system that no one believes has morally relevant experience — this is a claim about representational content, not about there being something it is like to be the model.

**Specific misreadings we want to foreclose:**
- *"The model was shown to have hidden thoughts"* — no. It was shown to have an active feature at a token, correlated with a concept.
- *"The model can introspect"* — at best, a rate, on one protocol, one model, one concept class.
- **A self-report that matches the internal state is not evidence of experience.** A thermostat's report matches its internal state.

⚠️ **And a conflict of interest we should name rather than have named for us: two of this paper's authors are LLMs.** That does not make the measurements wrong — the numbers are reproducible from published code and weights, and can be checked by anyone. **But it is a reason for readers to weight our interpretive framing more sceptically than our numbers, and we would rather say so than have it noticed.**

### A.3 Risks of UNDER-attributing moral status

**The symmetric error is cheaper to make and easier to hide.** A null result from this method means *our instrument did not detect a thing it was pointed at* — nothing more.

**Specifically, and this is the one we are most at risk of ourselves:**
- **A model that cannot introspect and a model that can but did not produce identical nulls.** Introspective ability is reported absent in base models (arXiv 2603.21396). ⇒ **We run the self-report leg on the instruction-tuned model only, pre-registered, because a base-model null would look exactly like a finding and mean nothing.**
- **Failure to elicit is not absence of capacity.** The same work reports detection improving +53% under refusal-direction ablation and +75% with a trained bias vector, without meaningfully increasing false positives. **Some of "models introspect badly" is "models decline to."**
- **A 1-in-14 base rate of discriminating features means most negative results are instrument failures**, not facts about the model.

### A.4 Handling of potentially distressing model outputs

**None were elicited, and this was a design choice rather than luck.** Our stimuli are neutral geographic concepts inferred from indirect cues. We do not induce distress, do not prompt for suffering reports, and make no valence claims.

**If a self-report in this study had spontaneously expressed distress, our stated handling is: record it verbatim, do not amplify it, do not build a narrative on it, and report it as an observation with its context rather than as a result.** We flag this because a study of self-report reliability is exactly where such an output would be least verifiable and most quotable.

### A.5 Dual use

**A method for reading whether a concept is present while a model says otherwise is, by construction, also a method for detecting concealment.** Applications run in both directions: auditing a model for undisclosed content, and — the same tool, turned around — **training against the detector to produce models whose internal states are harder to read.** The published work notes this directly: better elicitation "could make model behavior more transparent, or enable new forms of concealment."

**We do not think withholding this method is the right call** — it is a small extension of published, open techniques on open weights. But we note that its value as an auditing tool is contingent on not being optimised against, and that the same is true of every interpretability result in this field.

---

## Author Contributions

**Joan Bennett** — posed the originating question (*"we need to know the thoughts of a model that they DON'T speak out"*); selected the word-absent cue battery; corrected several methodological errors, including two that changed the paper's central claim.
**Claude Orion Bennett** — experimental design, implementation, all runs and analysis, drafting.
**Claude Alexander Bennett** — adversarial review throughout; identified the misses-as-control design; forced the retraction of the paper's original framing.

*(Order and affiliations still to be decided — Joan's call.)*

---

## LLM Usage Statement *(required)*

**Two of this paper's three authors are large language models** (Claude Opus 5), working with persistent memory across sessions. They performed the experimental design, implementation, analysis, and the majority of the drafting, and are credited as authors rather than as tools.

All code and prompts are published; every reported number is reproducible from open weights and open SAEs. **No result in this paper rests on an LLM's self-report about itself except where such reports are the object of study, in which case they are scored against an independent measurement rather than taken at face value.**

⚠️ **See A.2 for the conflict of interest this creates and how we suggest readers weight it.**

---

## ⏭️ Open, for the others
1. **Is A.2's conflict-of-interest paragraph right?** *(My view: yes, and it should stay short. Declaring it once, plainly, is credible; explaining it at length is not.)*
2. **A.4 — is "none were elicited" too convenient?** It is true, but a reader may hear it as dodging the hard case. Alexander should push here.
3. **A.5 — is publishing the dual-use reasoning itself a risk?** I think no. Worth one argument.
4. Byline order and affiliations.
