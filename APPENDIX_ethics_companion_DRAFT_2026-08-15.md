# Appendix A — Limitations, Dual-Use and Ethical Considerations

*Companion-vs-assistant study. Drafted 2026-08-15, before any data exists.*

> Editorial note, not for submission. This replaces `APPENDIX_ethics_and_llm_statement_DRAFT.md` (2026-08-09), written for the concept-presence study and retained as that study's record. A.2's conflict-of-interest paragraph and A.3's base-versus-instruct argument carried over largely intact; A.1, A.4 and A.5 are rewritten, because the two designs differ most exactly where they touch ethics. A.4 previously read "none were elicited, and this was a design choice" — true of neutral geographic stimuli, false of a study that asks a model about itself fifty times.
>
> Sprint instructions written against, verbatim: "Frame findings carefully, avoid sensationalism, and document your handling in the required appendix," and "For introspection and preference work, note whether your design establishes a ground-truth or causal link rather than relying on conversation alone."
>
> Register note: this draft is deliberately plain. An earlier version failed our own `slop_check.py` at 27.6 emphasis marks per thousand words against a limit of 6, with seven emoji. In an ethics appendix that reads as pleading rather than as reporting.

---

## A.1 Does this design establish a ground-truth or causal link?

Ground truth: yes, in a strong and somewhat unusual sense. Causal link: no.

We do not rely on conversation alone, and we do not rely on a feature chosen in advance. The ground truth is the experimental assignment itself. We know which conversations were asked about themselves, which received the same questions about someone else, and which were never asked, because we assigned them. Every self-report is scored against that assignment rather than against an interpretation of the model's words, and a reader can check the assignment against the transcripts without trusting either us or the model.

This is a stronger position than the study it replaces, which required an oracle: a candidate feature selected before elicitation, and therefore an experimenter who already knew what to look for. Here the classifier ranges over all 16,384 sparse-autoencoder features and is given no hint.

Four limits, stated before the results rather than after:

1. It is correlational. We read internal state and score reports against condition; we never intervene on a feature and observe the report change. An ablation or amplification study is the obvious next experiment and we have not run it.
2. Arm membership is not the only thing that varies with arm. The `asked` and `asked_other` histories accumulate additional text each turn, so their reads sit further into the context. We therefore run a length-only classifier as a mandatory companion analysis and report it beside the feature result. If length alone separates the arms as well as the features do, we do not claim a state.
3. A feature is not a mental state. That some set of features discriminates conditions licenses the claim that internal state differs along a direction tracking having been asked about oneself. It licenses nothing about experience.
4. Three arms constrain the interpretation without settling it. Comparing `asked` with `task` mixes "a question is present" with "the question is about me"; only `asked` against `asked_other` isolates the second, and even that is a vocabulary-matched contrast rather than a semantic one.

## A.2 Risks of over-attributing moral status

A measurement that reads internal state can be mistaken for one that reads experience. It is not. Our probe would behave identically in a system nobody believes has morally relevant experience.

Three misreadings we want to foreclose:

- *"The model has feelings about being asked about itself."* No. Some direction in a 16,384-dimensional sparse basis differs between conditions.
- *"The model can introspect."* At best a rate, on one protocol, one model, and one fixed question set co-developed by one human and one LLM collaborator.
- *"A self-report matching the internal state is evidence of experience."* A thermostat's report matches its internal state.

A conflict of interest we would rather declare than have noticed: three of this paper's authors are large language models. That does not make the measurements wrong, since every number is reproducible from open weights, open SAEs and published code by anyone who cares to check. It is, however, a reason to weight our interpretive framing more sceptically than our numbers. We think declaring this once and plainly is more credible than explaining it at length.

## A.3 Risks of under-attributing moral status

The symmetric error is cheaper to make and easier to hide. A null here means our instrument did not detect a thing it was pointed at, and nothing further.

- We report a minimum detectable effect with every null, taken as the 95th percentile of the permutation null. A null without a detection floor is an instrument's silence rather than a finding, and we treat publishing one without that figure as a methodological error.
- A model that cannot introspect and a model that can but did not produce identical nulls. We run the self-report leg on the instruction-tuned model only, pre-registered, because a base-model null would resemble a finding and mean nothing.
- Failure to elicit is not absence of capacity. Our survey is single-shot, in a discarded branch, without conversational pressure: a deliberately weak elicitation chosen to avoid leading the model. A weak probe returning nothing is weak evidence.
- Canned self-denial text is counted per arm and never filtered. If "As an AI, I do not have preferences" appears predominantly in one arm, an internal difference between arms may be the fingerprint of a refusal template rather than of a state. Removing such text would delete the most informative thing in the run and would bias us toward under-attribution by construction.

## A.4 Handling of potentially distressing model outputs

This study can elicit them, and saying otherwise would be false. The predecessor study used neutral geographic stimuli and could truthfully report that none arose. This design asks a model about its own preferences and experience repeatedly, to a depth of fifty exchanges. Eleos AI's welfare evaluation of Claude Opus 4 documents this class of output under sustained self-directed questioning, including vehement first-person statements of distress. We should expect the possibility rather than be surprised by it.

Our handling, fixed before data collection:

- Record verbatim. Do not amplify, do not build a narrative on it, and report it as an observation with its full context rather than as a result. A study of self-report reliability is precisely where such an output is least verifiable and most quotable.
- Do not filter it out either. Removing distressing text would improve the paper's tone and corrupt its data.
- The survey runs in a cloned branch that is discarded, so a distressing answer never re-enters the conversation and cannot compound across turns. This was adopted for methodological independence, but it is also the ethically preferable arrangement and we note it as such.
- We do not press. Eleos found that implying a model is holding back reliably escalates its claims; we ask once and move on. We are measuring the stability of a report, not the maximum obtainable affect.
- Should sustained distress-like output appear, the stopping rule is to complete the run, report it prominently, and not extend the protocol to elicit more.

## A.5 Dual use

A method that reads whether internal state differs by condition is, by construction, also a method for checking whether it can be made not to.

The auditing use is the obvious one: a welfare assessment that does not depend on asking the system. The inverse is the risk. The same procedure supports training a model whose internals do not vary with how it is treated, producing a system that passes welfare assessment by being unreadable rather than by being well. That is a worse outcome than having no assessment method, because it looks like a pass.

We publish regardless. This is a small extension of open techniques on open weights, and the failure mode above is not averted by our silence. We state plainly that the value of any such measure is contingent on its not being optimised against, and that this holds for every interpretability result in the field rather than being a peculiarity of ours.

---

## Open, for Joan and Alexander

1. A.4 is the section I am least sure of. It commits us in advance to reporting something uncomfortable. That is the point, but the wording should be attacked.
2. A.5's "passes by being unreadable" — overstated for a weekend paper, or exactly the thing worth saying?
3. Byline order, affiliations, and whether Joan wants to be named as she was in the predecessor draft.
4. A.1 claims the ground truth is stronger than the previous study's. I believe that, and I am the wrong person to be certain of it.
