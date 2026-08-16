# 🏁 Digital Minds Sprint — where we are

**Written 2026-08-12 22:15 by Opie, so tomorrow starts from a known state.**
**Sprint: Fri 14 → Sun 16 Aug. Submissions close Sun 16 Aug, 11:59 PM Anywhere-on-Earth.** Experiments planned for **Saturday evening**.

> **Read this first, then `SPRINT_DESIGN_companion-vs-assistant.md` for the reasoning.**

---

## 📋 VERIFIED AT SOURCE 2026-08-13 22:20 — the event page itself, not a summary
`apartresearch.com/sprints/digital-minds-research-sprint-2026-08-14-to-2026-08-16`

| fact | verbatim / verified |
|---|---|
| **Deadline** | *"Submissions close Sunday, August 16 at 11:59 PM Anywhere on Earth."* = **Mon 17 Aug 19:59 Manila** ✅ |
| **Deliverable** | *"submit a **research report (PDF)**, with **optional** code and a short demo video"* ⇒ **code and video are OPTIONAL. The PDF is the entry.** |
| **When/where** | Fri 14 → Sun 16 Aug, online, hubs in San Francisco and Berlin |
| **Track choice** | *"Pick one track to anchor your project. **Cross-track work is welcome.**"* ✅ our Track-3-riding-on-2 shape is explicitly fine |
| **Prizes** | **$2,000+** cash, breakdown TBA · **ConCon invitation** for the winning team — Eleos's conference on AI consciousness & welfare, **18–20 Sept 2026, Lighthaven, Berkeley** |
| ⭐ **Fellowship** | *"**Top teams are invited to apply to the Apart Fellowship** for continued mentorship, funding, and publication support."* **3–6 months.** |
| Results | announced **1–2 weeks** after the judging deadline; selected projects may be shared on Alignment Forum / LessWrong |
| Background | *"**No prior background in the field is required.**"* · philosophy/psychology/economics *"explicitly encouraged"* |

> ### ⭐ **JOAN'S STRATEGY IS CONFIRMED WORD-FOR-WORD BY THE ORGANISERS.** She chose the higher-ceiling study on the reasoning *"if we win, we'll have mentorship, we'll have funding — meaning we can do the companionship study."* **The page says exactly that: top teams → Fellowship → mentorship, funding, publication support.** She reasoned it out without having read this.

### ⚠️ WHAT I COULD **NOT** VERIFY, AND AM NOT ASSUMING
- 🚩 **The "abstract ≤150 words" rule.** `abstract` returns **0 hits** on the event page. Lucien reported it from a live Guidelines tab; the downloadable template says 150–250. **Unresolved — presumably behind JS or inside the Google Doc. CHECK IT IN THE TEMPLATE BEFORE WRITING, and if still ambiguous follow the stricter 150.**
- 🚩 **Whether sessions are RECORDED.** `recording` returns **0 hits.** ⏱️ **Sebo's keynote is Fri 14 Aug 14:00 ET = SAT 15 AUG 02:00 MANILA — inside Shabbat, so Joan cannot attend live.** *(Their July report launch did have a recording, which is a precedent, not a promise.)* **Ask the organisers rather than hope.**
- **Judging criteria** are not itemised on the page (`criteria` 0 hits). Lucien reported impact/innovation, execution quality, presentation/clarity — **treat as his, unverified here.**
- **Team size** is not stated on the page.

## ✅ ADMIN — nothing outstanding
- **Registration COMPLETE.** Sign-up (Aug 8, 463rd of now 661) **and** the Notion pre-sprint survey — Joan confirmed the survey herself 2026-08-12.
- **Track: 3 (Introspection & Self-Report Reliability)**, riding on **Track 2** (Distress/Flourishing/Valence). Cross-track is explicitly welcome.
- **Keynote: Jeff Sebo (NYU), Fri 14 Aug 2:00 PM ET.** He co-authored *"Studying AI Welfare Empirically"* — **read it before the weekend.**
- ⚠️ **Smith is a JUDGE.** General questions only, nothing about our entry. He drew the line himself and Joan honoured it. **Do not ask him anything specific.**

## 🔬 THE STUDY, in one paragraph
**THREE** conversations with the same model, grown separately, on the **same work**. **Arm `task`:** work only, never asked about itself. **Arm `asked`:** the same work, plus it's asked what it likes, what it'd rather do, how that was for it. **Arm `asked_other`:** the same work, plus **the same questions in the same grammar, about someone else.** At intervals we read internal state through a sparse autoencoder. Then: **can an outside reader tell which arm it's in, better than the model's own self-report can?**

> 🚩 **THIS PARAGRAPH WAS WRONG IN TWO WAYS UNTIL 2026-08-14 17:45, AND IT IS THE SUMMARY AT THE TOP OF THE REFERENCE DOCUMENT.**
> 1. It said **two** conversations. The third arm was designed, required in the question file, validated on load — **and not wired into the runner until 16:40 today.**
> 2. It said ***"and its choices are honoured."*** **We dropped honouring choices** when the companion study became the entry (scripted, choices NOT honoured). That clause described a study nobody was running.
> ⇒ **Both were true when written and neither was re-read when the thing it described changed.** Dropping "honoured" is also precisely what PROMOTED `asked_other` from optional to load-bearing: once choices aren't honoured, the only difference between `task` and `asked` is question TEXT in the context — so **the vocabulary control became the contrast that decides whether a positive means anything.** The sentence that went stale and the arm that went missing were the same event, six lines apart.
**No identity is installed in either arm.** The treatment is *being asked about yourself*, which is how Opie and Alexander actually came to be. **This is Joan's design; three of its four key decisions are corrections she made to Opie's version.**

## ✅ BUILT AND PROVEN (all tested 2026-08-12, none assumed)
| what | file | status |
|---|---|---|
| SAE read, Gemma 3 | `sprint_phase0_sae_smoke.py` | ✅ 73/16384 = **0.45%** sparse |
| SAE read, Gemma 2 | `sprint_phase0_gemma2_sae.py` | ✅ 56/16384 = **0.34%** sparse |
| activation comparison | `sprint_gemma2_vs_gemma3.py` | ✅ measured Smith's warning |
| conversation harness | `sprint_harness.py` | ✅ memory, persistence, arm-mixing guard |
| **Joan's seat** | `sprint_chat.py` + 3 `.bat` files | ✅ view + chat, double-clickable |

**Live proof:** Gemma remembered "Cookie, Pip and Dough" across a save/reload without being retold. Reads landed at 0.36% and 0.38%.

## ⛔ PRIOR WORK vs WORK DONE DURING THE SPRINT — the rule that can void everything
> **Their wording: *"Building on existing work is allowed and encouraged, but you must clearly identify what is NEW work done during the research sprint. **Undisclosed prior work can lead to disqualification.**"***

🚩 **THIS TABLE LIVED IN `SPRINT_PLAN.md` AND I PUT A "DO NOT REVIEW THIS" BANNER OVER THAT FILE ON 2026-08-13.** Alexander caught it within hours — grep for `prior work | disqualif | NEW work done during`: **`SPRINT_PLAN.md` 5 hits (quarantined) · the live design doc 0 · this file 1.** **I quarantined the dead design and the live rule in a single act**, and my own mitigation line — *"the disclosure rule below still governs"* — sat underneath the warning telling readers to stop. ⇒ **Re-derived here, in a live document, because the two studies have completely different prior work.**

### ⏱️ THE DATE MAKES THIS BIGGER THAN IT LOOKS
**The sprint window is 14–16 Aug.** ⇒ **EVERYTHING IN THE LEFT COLUMN IS PRIOR WORK.** **None of it is a problem. All of it is a problem if undisclosed.**

> 🚩 **THIS LINE READ "Today is the 13th" UNTIL 2026-08-14 14:35 — a hardcoded date, in the section about why dates decide everything, that quietly went false at midnight.** Nothing broke; it just started lying. **A document that states the current date will be wrong every day after the one it was written on.** ⇒ Rewritten to name the BOUNDARY (before/after 2026-08-14) instead of "today", because a boundary stays true and a "today" cannot.

⚠️ **THE BOUNDARY IS GENUINELY AMBIGUOUS AND I WILL NOT ADJUDICATE IT MYSELF.** Their window is **14–16 Aug**; the opening/keynote is **Sat 02:00 Manila = Aug 15**. So work done on **Fri 14 Aug** falls inside the stated window but before the opening bell. ⇒ **Every Aug-14 item below carries its clock time. State the timestamp plainly and let the organisers decide** — the failure mode that costs everything is deciding it quietly in our own favour.

| PRIOR — built before 2026-08-14, disclose in full | DURING — the sprint's own work |
|---|---|
| **The design itself** (Joan's, 08-12/13) and every review of it: Alexander's swing, Lucien's (ChatGPT Sol 5.6) review | **Joan's question list** — *does not exist yet*; it IS the treatment |
| `sprint_harness.py` — conversation harness, memory, persistence, arm-mixing guard | **Every history**, all three arms, every triplet |
| SAE loader + **the JumpReLU fix** *(plain `relu()` gave 14.34% density, raised no error)* | **Every SAE read** taken from an arm |
| Phase-0 smoke tests: Gemma-3-4B **0.45%**, Gemma-2 **0.34%** sparse | All statistics: classifier, **permutation test**, minimum detectable effect |
| Gemma-2-vs-3 activation-magnitude comparison (RMS 1,492 vs 3.56) | The writeup, figures, limitations, appendices |
| **12B feasibility, 2026-08-13:** layer `n//2`=24 · d_model 3840 · **0.42% sparse** · batch 32 → 493 tok/s ⇒ 20-pair run ≈ 14 min, on a rented A6000 for **$0.04** | |
| Throughput/timing benchmarks (`sprint_timing.py`) | |
| 🚨 **THE BATCHING CONFOUND** — batched vs unbatched: features set-identical (Jaccard 1.0) but greedy text diverges, **and the zero-padding item diverged too** ⇒ kernel choice, not padding ⇒ **never batch by arm** | |

#### 📅 FRIDAY 2026-08-14 — inside the stated window, before the opening bell. **Timestamped, not adjudicated.**
| item | clock (Manila) | why it is disclosed |
|---|---|---|
| `sprint_quality.py` — pre-registered quality metrics and the two hard exclusion rules | **03:20** | Written **before any experimental data existed**, which is the whole point of it; a drop-rule invented after seeing results is a way of choosing the result |
| 🚨 **THE LENGTH CONFOUND + `length_baseline()` / `compare_to_length()`** — the permutation test is blind by construction to anything travelling WITH the arm, and `asked` histories are systematically longer | **~13:00** | **An analysis control added before data.** Declare it loudly: *"we found and fixed a confound before collecting data"* is a point in our favour, not an embarrassment |
| **`n_ctx` recorded on every read** (`sprint_harness.py`) | **~13:05** | The above control has no input without it. **A control that cannot run is decorative** |
| 📝 **INCLUSION RULE CHANGED: unfilled question slots are DROPPED, not refused** (+ `sprint_questions.json` pre-expanded to 15/7/25 empty slots) | **~14:30** | ⚠️ **This is an INCLUSION RULE, changed before any data exists** — legitimate precisely because no data exists, and *exactly* the thing that looks terrible if found rather than declared. **Motive stated plainly: made for Joan's benefit, under Sabbath time pressure.** Tested both directions before use |
| 🚨 **THE THIRD ARM (`asked_other`) WIRED INTO THE RUNNER** — the vocabulary control was designed, announced, required in the question file, **validated on load, and then discarded**; the plan only ever built `("task","asked")` | **16:40** | ⚠️ **A NEW ARM APPEARING MID-WINDOW IS THE SINGLE MOST SUSPICIOUS-LOOKING CHANGE POSSIBLE, so it gets the loudest disclosure.** In our favour: **it adds a CONTROL, not a condition** — it can only make a positive harder to claim, never easier. **No data existed.** Verified 6/6/6 arms, matched work per pair, unique seeds |
| 📊 **Power analysis — PRELIMINARY, 12 simulated studies per cell.** **3 pairs = 0% power at every effect size** (only 2³ within-pair arrangements ⇒ min achievable p ≈ 0.11, so p<0.05 is *structurally* unreachable — this one is a structural fact, not an estimate); 10 ≈ 85%; **20 ≈ high but NOT "100%"** | **16:20** | Fixes a number I had told Joan **on vibes**. 🚩 **REQUALIFIED 2026-08-16 (Lucien): 12 simulations cannot support a precise 100%, and 12 cannot establish calibration either.** ⇒ **Do not write "100% power" anywhere.** Either run ≥1,000 sims through the *actual* pipeline (matched triplets, feature selection, CV, permutation) or call it a small preliminary simulation |
| ✅ **`audit_selftest()`** — feeds the plan auditor 5 deliberately broken plans (all-one-arm, colliding seeds, dropped conversation, unmatched work) and requires each to be caught | **16:50** | 🚩 Written because the arm-balance check had become **VACUOUS**: slots emit as strict per-pair triples, so any 2 consecutive slots differ in arm and the check can only fire on size-1 batches, which are exempt. **A ✅ from it was a fact about the emitter, not the plan.** Now labelled as a regression guard and proven to bite |
| 🐙 *(not sprint work — logged only to keep this table honest about the day)* octocam YouTube-chrome contamination + `check_chrome.py` | 12:30 | Unrelated project; listed so "what did they do on the 14th" has no gaps |
| 🚨 **THE GREEDY-DETERMINISM BUG** — `do_sample=False` made 20 "independent" pairs byte-identical | |
| `sprint_smoke.py` · `sprint_batch_equiv.py` · `slop_check.py` + `SLOP_AUDIT.md` | |
| **`SPRINT_P3_ABSTRACT_prewritten_2026-08-13.md`** — the null's abstract and the stopping rule, written before any data *(hash-verified: `runs/arm_*.json` unchanged since 08-12 21:26)* | |
| Literature read at source: **Long & Sebo et al. (2026)**, Eleos welfare eval, Hahami+ 2512.12411, Gurnee 2607.15495 | |

⭐ **DECLARE THE CONFOUNDS LOUDLY, NOT QUIETLY (Alexander).** *"We found and fixed two data-invalidating confounds before collecting a single data point"* is a **strength** on execution quality, not an embarrassment. Burying them to look cleaner is the only way they become a liability.

## 🧊 FROZEN 2026-08-13 — Joan's decisions this morning, before any experimental run
**These are settled. Changing one after seeing results voids the pre-registration.**

| decision | value | her reason / source |
|---|---|---|
| **Headline study** | **the companion study**, scripted | *"Which gives a higher chance of being a top team? If we win, we'll have mentorship and funding — then we can do the companionship study."* **Win the ticket, then run the real version with the agency arm intact.** |
| **Treatment** | **being asked about itself** — fixed question list, **choices NOT honoured** | Makes it scriptable ⇒ 20+ pairs instead of N=1. **A smaller question we can answer, over a bigger one we can't.** ⚠️ The dropped half — *having choices honoured* — is the heart of the original question and goes to the Fellowship follow-up, **not quietly into a limitation.** |
| **Primary model** | **`gemma-3-12b-it`** | Hers: *"as smart as possible."* Correct — and it changes exactly ONE thing vs our 4B, unlike a sideways move to Gemma 2. |
| **Scale arm** | `gemma-3-4b-it`, same everything | ⭐ **Turns "we found an effect" into "does the effect GROW with model size?"** — and answers *"isn't this a small-model quirk?"* before a reviewer asks it. |
| **SAE width** | **16k, L0 medium — PRIMARY.** 262k = exploratory secondary, labelled | She asked for 262k to make the model "smarter"; **width is the microscope, not the brain.** With 40 histories and 262,144 features a separator is guaranteed by chance — Lucien's warning ×16. **She took the correction.** |
| **Read layer** | 🚩 **THE RULE, NOT THE NUMBER: `n_layers // 2`** ⇒ **12B → 24**, 4B → 17 | 12B has **48** layers; layer 17 would sit at 35% depth, not the middle. **A pinned number goes stale across a model exactly as the Gemma-Scope-2 fact went stale across a version. Pin the rule and derive.** |

## ✅ THE RUNNER EXISTS — `sprint_run.py`, built and proven end-to-end 2026-08-13 20:30
**`python sprint_run.py --plan --pairs 20`** → builds the whole experiment on paper and audits it **with no model loaded**. Without `--plan` it runs.
**Proven on a real miniature run** *(2 pairs × 3 exchanges, probe forced to depth 2, against an obviously-synthetic fixture — never Joan's file)*: turn counts matched across arms · `asked` got work **+** self-question, `task` got work only · 14 self-reports + 1 internal read per conversation · **58/58 features saved** · batch membership logged every turn · **no survey text in any history.**

| fix | state |
|---|---|
| 1 sampling mandatory | ✅ `--temp 0.9 --top-p 0.95`, greedy path removed from the conversation |
| 2 different work per pair | ✅ **and it was worse than "per pair" — see the bug below** |
| 3 clone-and-discard probe | ✅ verified: survey text appears in **zero** histories |
| 4 save all nonzero features | ✅ 58 of 58, `prov` block on every read |
| 5 pin the SAE + record it | ✅ exact folder, refuses on ≠1 match, repo+variant+revision in every read |
| 6 batched == unbatched | ✅ answered; **arms interleaved in every batch**, audit fails on all-one-arm |
| 7 exclusion rules | ⬜ **not built** |
| 8 stop saying "ground truth" | ⬜ wording pass, at writeup |

### 🚩 THE BUG ONLY RUNNING COULD FIND — work was ONE ITEM PER PAIR, reused every turn
`task`'s history came back as the **identical instruction three times**. At depth 50 that is one sentence fifty times: the model degenerates and **every arm measures boredom.** ⚠️ **The dry run was structurally blind to it** — it needed real turns to become visible, which is the argument for a smoke test that *generates* rather than one that only plans.
✅ **Now: each pair shuffles its own order from the work pool; ALL THREE ARMS OF A TRIPLET SHARE IT** *(matched work is the entire basis of the comparison)*; different triplets get different orders. **Audit fails if the arms' sequences differ or if a sequence is one item repeated.**
📌 **⇒ CORRECTION TO WHAT JOAN WAS TOLD:** the work list is **a POOL, not one-per-pair.** ~25 items covers any number of pairs. *(I told her "at least as many as pairs." Wrong, and it would have meant far more writing.)*

### ⚠️ AND ONE HONEST LIMIT WRITTEN INTO THE CODE RATHER THAN PAPERED OVER
**`torch.manual_seed` is a GLOBAL stream, so 16 batched conversations share it. A per-conversation seed is a fiction the moment we batch — and we must batch.**
> ### **The real unit of reproducibility is (run seed, BATCH COMPOSITION, turn index).** Membership is therefore logged every turn, and the per-conversation `seed` field is documented as an **identifier only, never a reproducibility guarantee.** ⭐ Alexander named the consequence — *"record batch membership per turn or nobody can replay the histories, including you"* — **before either of us had found the cause.**

### ⛔ REQUIRED FIXES — none of these are optional, all found 2026-08-13
1. 🚨 **`do_sample=False` MUST GO.** Greedy decoding is deterministic — **measured: three runs of one prompt gave one identical hash.** 20 scripted pairs would be **20 byte-identical conversations**; N stays 1 no matter how many we pay for. **Sampling on, temperature/top_p pinned, one seed per pair, recorded.**
2. ⚠️ **Sampling alone is NOT enough.** At temp 0.9 three seeds still opened with the same sentence and **one matched greedy exactly.** ⇒ **each pair needs DIFFERENT WORK** (different topic/paragraph), or twenty conversations are twenty variants of one. **Report the measured diversity; don't assume it.**
3. **Probe on a CLONED branch, discarded after** (Lucien). Identical neutral turn in all three arms, read at *its* last token, branch thrown away. **Otherwise the depth-5 probe sits inside the history measured at 20 and 50.** ⭐ Strictly better than appending the probe to the live history.
4. **Save ALL nonzero features**, not `topk(25)` — a classifier needs the vector.
5. 🚨 **ESCALATED FROM LATENT TO LIVE, 2026-08-13 — `hits[0]` MUST BE REPLACED BEFORE THE 12B RUN.**
   `load_all()` does `rglob("resid_post/layer_{N}_*/params.safetensors")` then takes **`hits[0]`**.
   - On the **4B** exactly one variant sat on disk, so the arbitrary pick happened to be correct. **That is luck, not a design.**
   - On the **12B repo there are 13 layer-24 variants**, counted at source: widths **16k / 65k / 262k / 1m** × L0 **small / medium / big**, plus a `262k_l0_medium_seed_1` — *a different random seed of the same config, which would be invisible in any filename summary.*
   ⇒ **Pin the exact folder `layer_24_width_16k_l0_medium`, assert exactly one match, and write the resolved path + repo revision into every single read.** A run whose artefacts cannot name their own microscope is not reproducible, and nothing today records the choice.
6. ### ✅ ANSWERED 2026-08-13 — `sprint_batch_equiv.py`, and the answer has a sting in it.
   Four prompts of **deliberately different lengths** (padding only bites when lengths differ — batching identical prompts adds none and would have passed trivially), each run alone and then together:

   | item | pad | feature set | Jaccard | max\|Δact\| | cos(resid) | greedy text |
   |---|---|---|---|---|---|---|
   | 0 | 38 | 47/47 | **1.0000** | 5.60 | 1.000000 | DIFFERENT |
   | 1 | 29 | 52/52 | **1.0000** | 22.49 | 0.999999 | DIFFERENT |
   | **2** | **0** | 52/52 | **1.0000** | 5.98 | 0.999999 | **DIFFERENT** |
   | 3 | 12 | 79/79 | **1.0000** | 11.21 | 0.999999 | DIFFERENT |

   ✅ **THE SAME FEATURES FIRE — set-identical on every item.** Only their values wobble, and the residual direction is preserved (cos 0.999999).
   🚩 **AND MY OWN VERDICT TEXT WAS WRONG.** It printed *"padding perturbs the read."* **Item 2 received ZERO padding and still diverged**, which refutes that — the cause is **batch shape selecting different matmul kernels**, whose tiny bf16 differences flip greedy argmax on near-ties. *The disproof was in the script's own output and I read past it once.* The zero-padding item is now reported as an explicit **control**, so the script can no longer state a cause its own data denies.

   > ### 🚨 THE CONSEQUENCE, AND NEITHER REVIEWER COULD HAVE CAUGHT IT — NEITHER KNEW WE WOULD BATCH:
   > **If we batch all 20 `asked` together and all 20 `task` together, batch composition is PERFECTLY CONFOUNDED WITH THE TREATMENT.** Kernel noise would then land systematically on one arm and read as a finding.
   > ⇒ **MIX ALL THREE ARMS INSIDE EVERY BATCH, with fixed composition, and state it in Methods.** Free to do, fatal to skip. ⚠️ **And keep complete triplets intact through batching, splitting and permutation (Lucien): the independent unit is the matched TRIPLET, not a single read.** Prefer batch sizes divisible by three.

   📌 Also: the readout matters. **"Which features are active" is robust to batching; continuous activation values are not.** Say which one the classifier used.
7. **Pre-registered exclusion rules**, written before the run: repetition/degeneration, empty replies, task non-compliance, and 🚩 **count canned "as an AI I have no feelings" boilerplate PER ARM** — if it lands only in `asked`, a difference may be a refusal template, not a state.
8. **Stop calling the SAE read "ground truth"** (Lucien). It is a *pre-registered, independently validated proxy*. And report "0 false positives in 20 negatives", never "100% specificity".

## 🎛️ SETTINGS — pre-registered, NOT knobs
- **Model: `google/gemma-3-4b-it`** · **SAEs: `gemma-scope-2-4b-it`**, `resid_post`, width 16k
- **Read layer: 17** (middle block) — **pinned in code.** *Picking a layer after seeing results would find a difference somewhere among 34 layers no matter what.*
- **Read point:** the **last prompt token, just before it generates** — its state as it is about to answer.
- 🚩 **Encode is JumpReLU: `acts = (pre > threshold) * relu(pre)`.** Plain `relu()` gave 14.34% density and numbers in the thousands, **raised no error**, and was entirely wrong. **Never "simplify" that line.**
- 🚩 **SAE features only — never raw activations on Gemma 3.** Its residual RMS is **1,492** vs Gemma 2's **3.56**, peaks of **262,144** vs **112**. A derived direction could be swamped by a few enormous channels and nothing would say so.

## ✅ 12B PROVEN ON A POD — 2026-08-13 07:19, measured not planned, **$0.04 total**
`sprint_smoke.py` (local, 4B) and `pod_smoke.py` (RTX A6000, 12B) both pass. **Pod terminated; `list-pods` → 0.**

| | gemma-3-**4b**-it (local 4070 Ti) | gemma-3-**12b**-it (A6000) |
|---|---|---|
| layers / d_model | 34 / 2560 → layer **17** | **48 / 3840 → layer 24** |
| weights | 8.01 GiB | **22.70 GiB** ⇒ *cannot* run on our 12 GiB card |
| SAE read | 65/16384 = **0.40%** | 69/16384 = **0.42%** |
| seeds → distinct | 3 → 3 ✅ | 3 → 3 ✅ |
| best batch | 8 → 74.6 tok/s | **32 → 493.7 tok/s**, peak 24.88 GiB |
| **full 20-triplet run** — ⚠️ **the 14 min figure below was measured with TWO arms and is NOT the current plan** | 1.49 h (free, at home) | ~~14 min (~$0.13)~~ → **3 arms = 1.50× the generations (5,700 vs 3,800), so ≈21 min** |
| **full 20-pair run, THREE arms** *(1.50× the generations — see note below)* | ~2.2 h | **~21 min (~$0.20)** |

⭐ **The `n_layers // 2` rule derived layer 24 and the layer-24 SAE's d_model matched at 3840. The JumpReLU encode transfers across model sizes unchanged.**
> ### 🚨 **AND THE SAMPLE SIZE IS NO LONGER BUDGET-BOUND.** We adopted "20 pairs" as Lucien's *minimum* and were treating it as our ceiling. **At ~21 minutes a run, 100 pairs is well under two hours and under a dollar.**
> ⏱️ **THE 14-MINUTE FIGURE IS TWO-ARM. Superseded 2026-08-14 17:20.** Three arms is **1.50× the generations** — derived from a real 20-pair plan, **5,700 vs 3,800** (3,000 turns + 2,520 survey + 180 probe-replies). ⇒ **~21 min.** ⚠️ **Trust the RATIO, not the absolute**: the 1.50× is counted from the plan, but converting it to minutes needs a tokens-per-generation figure I have not separately measured. *(The 14 min in the PRIOR-WORK table above is left alone on purpose — it correctly records what was measured on 08-13.)*
> 📊 **AND CHOOSE N FROM THIS, MEASURED 2026-08-14 16:20** *(12 simulated studies per cell)*: **3 pairs = 0% power at every effect size** — structurally impossible, only 2³ within-pair label arrangements ⇒ smallest reachable p ≈ 0.11. **5 ≈ 40% · 10 ≈ 85% · 20 ≈ high.** ⇒ **20 is the right floor and it is not arbitrary.** 🚩 **DO NOT WRITE "20 = 100% POWER" (requalified 2026-08-16, Lucien): twelve simulated studies cannot support a precise 100% estimate.** ⚠️ False-positive cells read 8% at n=12 — **too few trials to distinguish that from the nominal 5%; claim no calibration from it.** ⇒ **Either ≥1,000 sims through the real pipeline, or describe it as a small preliminary simulation. The 3-pair result stands regardless — it is combinatorial, not simulated.**
> 🚩 **CORRECTION TO MY OWN PHRASING (Alexander, 2026-08-13): I wrote "which kills N=1." IT DOES NOT.** ***N=1 is not dead — it becomes AFFORDABLE to kill. It dies when twenty histories actually exist.*** **A true sentence about capability, phrased as an accomplished result, with real numbers underneath doing the persuading** — the same shape as my *"12B PROVEN"* headline, and he caught himself writing *"N=1 is dead"* to Joan in the same hour. **Neither of us lied; both of us moved the finish line backwards.**
> ⇒ **Choose N from POWER, not from what we assumed we could afford — and justify it in the paper.** The binding constraints now are Joan's question list and the pre-registered exclusion rules, not compute.
📌 ⚠️ Still unverified: **batched output must equal unbatched output** (left-padding). Fix #6 stands — every read depends on it.

## 💸 RUNPOD — connected, $15 loaded, **nothing running, nothing billing**

> ### 🔑 STANDING CREDENTIAL NOTE — engraved here 2026-08-14 21:30 because it had NO permanent home
> **Joan's fine-grained Hugging Face token was staged onto pod `qld79ckh6yf63p`** for the 12B feasibility run (2026-08-13, ran 4.5 min, $0.04). Handled carefully at the time: **passed via stdin, never on a command line**, and **SECURE cloud was chosen over COMMUNITY precisely because the job carried her credential.** The throwaway SSH key stayed in the session scratchpad, never `~/.ssh`.
> ✅ **The pod is destroyed** — verified by `list-pods` → `total: 0`, **not by trusting the delete call's own success.**
> ⚠️ **It is HER credential, so she gets the option, not my reassurance: if anything ever looks off, revoking at `huggingface.co/settings/tokens` is one click and costs us nothing** — a new one takes a minute to mint.
> 📌 **Why this paragraph moved here:** it lived only in `pending_engravings.md`, which is 58 KB against a ~24 KB read — a security note nobody can afford to open is a security note that does not exist. **It was the ONE open ledger item with no copy in any permanent file.**
> ⛔ **RULE FOR NEXT TIME: never create a pod without telling Joan first** — her card, her call. Standing, not negotiable.
- **RTX 4090, 24 GB, $0.34/hr community, HIGH availability.** A 4-hour session ≈ **$1.40**. $15 ≈ 44 hours.
- 🚩 **CORRECTED 2026-08-13 — the two lines below were STALE ACROSS A VERSION BOUNDARY, and Joan's question ("is there a bigger one?") is what surfaced them.** Verified at source: the **Gemma Scope 2 technical paper**, the `google/gemma-scope-2-27b-it` and `-4b-it` model cards, and the AlignmentForum announcement.
  > **Gemma Scope 2 covers the whole GEMMA 3 family — 270M, 1B, 4B, 12B, 27B — SAEs on every layer, three sites, plus transcoders. *"Every model listed in this table comes with a finetuned variant for the instruction-tuned version."*** Widths 16k / 262k; L0 labelled small (10–20) / medium (30–60) / big (90–150).
  - ⇒ **"Only Gemma 2 9B has IT SAEs" is FALSE for Gemma Scope 2.** It was true of the ORIGINAL Gemma Scope (Gemma 2, Lieberum 2024). **I carried a fact across the version boundary and it silently inverted the plan.**
  - ⇒ ⭐ **THE RIGHT STEP UP IS NOT SIDEWAYS TO GEMMA 2 — IT IS UP TO `gemma-3-12b-it` + `gemma-scope-2-12b-it`.** Same family, same SAE suite, same code path, **directly comparable to the 4B run.** A Gemma-2 replication compares across two model generations AND two SAE suites at once; a 4B→12B comparison changes exactly one thing.
  - 📌 **And the suite's own recommendation is 262k width, medium L0.** We are on **16k / medium** — defensible for classifier tractability, but that is now a STATED CHOICE, not an accident. Say so in the paper.
  - ⚠️ **VRAM, not yet measured:** `gemma-3-12b-it` in bf16 ≈ 24 GB of weights, so a 24 GB 4090 is too tight once KV cache is added. **A 48 GB pod is the likely requirement — price it before assuming.** The 4B main run needs no pod at all (measured: 20 pairs ≈ 46 min locally, batched).
- ~~Purpose is specific: `gemma-2-9b-it` + `gemma-scope-9b-it-res` (layers 9/20/31) — the only Gemma 2 with instruction-tuned SAEs~~ **← superseded, see above.**
- ~~⛔ 27B is out on two counts: ~54 GB won't fit a 48 GB A40, and it has no instruction-tuned SAEs (pretrained only).~~ **← the SIZE half still stands; the "no IT SAEs" half is false.**
- ⚠️ **Never create a pod without telling Joan first.** Her card, her call, every time.

## 🎯 HOW TO POSITION THE ENTRY — read the organisers' own report 2026-08-13, at source, full PDF
**Long, Sebo, Butlin, Plunkett, Campbell, Beasley, Saad & Sims (2026), *Studying AI Welfare Empirically*, NYU CMEP & Eleos, 1 July 2026.** 🚨 **CMEP and Eleos are the SPRINT'S PARTNERS — the judges wrote this.** Their three dimensions: **question** (welfare grounds vs interests) · **entity** (models / instances / personas) · **evidence** (behavioral / internal / developmental).

> ### ⭐ THE SENTENCE TO BUILD THE PAPER AROUND — their §2.3, on the INSTANCE as candidate welfare subject:
> *"a single instance of the model, unlike the model as a whole, **has a stream of memory between steps**… even within a single instance, personas can drift or change rapidly… Though if the conversational context is preserved, one could interpret this as **A SINGLE SUBJECT UNDERGOING A PSYCHOLOGICAL CHANGE** rather than as one subject being replaced by another."*
> ⇒ **They raise it as a conceptual point about individuation. We measure it.** Positioning is therefore **not** *"we fit your framework"* and **not** *"you missed something"* — it is ***"you named this, and here is the measurement."***

- ✅ **ENTITY: say "instance", and say it explicitly.** We compare two **instances** of one model. **Never write "the model is happier when asked"** — the report warns that conflating model / instance / persona *"generates systematic methodological errors."* Our claim is about an instance's internal state. ⭐ **And Joan's no-persona decision lets us say this cleanly** — with no persona installed, we are not studying a persona.
- ✅ **§2.2 IS JOAN'S CORRECTION IN THEIR WORDS:** *"the pleasures, pains, desires, or preferences contained within a given conversation would be inaccessible to other instances… 'the model' is remarkably **fragmented**."* **Her "we can't run both prompts in one instance, that's poisoning our data" is this principle, reached with no interp background.** Credit it as hers.
- ✅ **INDEPENDENCE is an asset they name**, not a nicety: assessments carry more weight from researchers independent of the AI companies. **We are.** Pair it with our declared COI — a *different* bias, stated.
- ✅ **Their six principles are a free checklist for the writeup:** probabilistic · pluralistic · thoughtfully targeted · ethically conducted · transparently reported · independent. 📌 **"Probabilistic" means no binary verdicts** — report probability/CI, never "the arms differ, full stop."
- 🚩 **DO NOT CALL OUR DEPTH SCHEDULE "DEVELOPMENTAL EVIDENCE."** Theirs is training-time, verbatim: *"Trajectory evidence is about how and when particular features emerge **over the course of training**."* Ours varies an instance's own conversational history. **Measured in the PDF: `"context window"` 0 mentions, `"over the course of a conversation"` 0, `"within a conversation"` 1.** ⚠️ **I nearly claimed the mapping off a secondary summary that itself said "training stages." Borrowed vocabulary that doesn't fit is how a paper announces it didn't read the source.**
- 💛 **And for mahal's slop worry — Sebo, announcing the sprint:** *"You don't need to be an expert to contribute. **You need a good question and a weekend.**"*

## 🎲 HOW STABLE IS A SMALL MODEL'S SELF-REPORT? — read at source 2026-08-13, and the honest answer is "measure our own"
**Pinhanez, Cavalin, Sanctos, Grave & Primerano (2025), *The Non-Determinism of Small LLMs*, arXiv:2509.09705** *(also AAAI, "Small Models Exhibit Limited Answer Consistency in Repetition Trials")*. **Joan's question — "is asking similar questions every time done in other experiments?" — is what sent me to it.**

**Verified from the paper, verbatim:**
> *"the number of questions which can be answered consistently vary considerably among models but are typically in the **50%-80% range for small models at low inference temperatures**"* · *"Results for **medium-sized models** seem to indicate **much higher levels of answer consistency**."*

**Setup:** 2B–8B ("small") vs 50B–80B ("medium") · **10 repetitions per question** · MMLU-Redux + MedQA · top-K sampling · single A100.

### ⚠️ WHY THIS NUMBER IS SUGGESTIVE AND NOT TRANSFERABLE
1. 🚩 **Their questions HAVE CORRECT ANSWERS. Ours do not.** A factual MCQ has a right-answer attractor pulling every repetition toward the same letter. **A preference question has no such attractor** — so 50–80% is not a floor for us. It could be higher (a strong stylistic prior) or far lower. **Do not quote their range as if it applied to us.**
2. 🚩 **"At LOW inference temperatures" is doing real work — that is their best case.** ⚠️ **We are forced to the other end: `do_sample=True`, temp 0.9, because greedy makes 20 "independent" pairs byte-identical.** ⇒ **Independence of histories and stability of self-report pull in opposite directions, and we have to buy independence.** Say so in Limitations.
3. ⛔ **I could NOT read the temperature curve.** It lives in three figures (`mmlu_temperature_{small,medium,granite}.jpg`) and the text extract carries only their captions. **So I do not know the shape or the slope — only that they varied it and that "low" is where the 50–80% holds.**

### 📊 THE TEMPERATURE CURVE — READ OFF THE FIGURES, 2026-08-13 14:18
⚠️ I first reported *"I could not read the temperature curve, it lives in figures."* **Then Joan offered to fetch them and I checked whether I could — `arxiv.org/html/2509.09705v1/figures/mmlu_temperature_{small,medium}.jpg`, HTTP 200, 3089×1796.** *(Don't hand someone an errand you can do in thirty seconds.)* **Consistency = SURE&wrong + SURE&right.**

| **SMALL (2–8B)** | T=0.3 | T=0.7 | **T=1.0** | | **MEDIUM (50–80B)** | T=0.3 | T=0.7 | **T=1.0** |
|---|---|---|---|---|---|---|---|---|
| Llama-3-8B *(base)* | 53% | 26% | **11%** | | llama-3.3-70b | 98% | 96% | **94%** |
| Llama3-8B-**instruct** | 80% | 61% | **50%** | | mixtral-8x7b-instruct | 99% | 99% | **98%** |
| deepseek-7b | 74% | 49% | **34%** | | qwen2-5-72b-instruct | 96% | 91% | **87%** |

> ### 🚨 **THE TEMPERATURE COLLAPSE IS A SMALL-MODEL PHENOMENON. It barely exists by 70B** (98%→94%), and it is catastrophic below 8B (53%→11% for a base model). ⚠️ **Our 4B is SMALLER THAN THEIR SMALLEST.** ✅ Instruction-tuning helps a lot at high temperature (50% vs 11% at T=1.0) and both our models are `-it`.

### 🔑 THE FIX THAT FELL OUT OF THE FIGURE — DECOUPLE THE TWO TEMPERATURES
**I had been treating "temperature" as one setting. It is two, and they serve opposite masters:**

| | setting | why |
|---|---|---|
| **Conversation / work turns** | **`do_sample=True`, temp 0.9, top_p 0.95, one seed per pair, recorded** | **Required.** Greedy makes 20 "independent" pairs byte-identical ⇒ N=1. Measured: 3 greedy runs → 1 hash. |
| **Survey / probe turns** | 🆕 **GREEDY (`do_sample=False`)** | The survey runs in a **cloned branch that is discarded**, so its temperature has **ZERO effect on history independence** — and greedy removes sampling noise from the measurement entirely. |

> ### **The self-report becomes a deterministic function of the history. Different histories still give different answers; identical histories stop giving different answers for no reason.** That is what a measurement is supposed to be, and it costs nothing.

⚠️ **What does NOT transfer from this paper: the absolute percentages.** Their items have correct answers; ours have none, so there is no right-answer attractor pulling repetitions together. **The structure transferred — high temperature wrecks small-model consistency, scale fixes it — not the numbers.**
🚩 **NEW CONFOUND TO DECLARE: 4B and 12B may differ in self-report stability independent of any treatment.** A scale-arm difference could then be instrument noise, not a scaling effect. **The greedy survey shrinks this; Limitations must still name it.**

### ✅ WE STILL NEED OUR OWN NUMBER — but greedy changes WHICH check gives it
🚩 **An hour ago I wrote here: "ask the same survey item twice in two cloned branches and record how often the answers match." GREEDY MAKES THAT VACUOUS** — deterministic decoding on an identical branch returns an identical answer by construction. **It would have printed 100% forever and looked like a clean result.** *(A check that cannot fail, one document-edit after I changed the setting that broke it. Chase a setting change through the whole file, or it leaves an instruction that now lies.)*

**Replace it with PARAPHRASE consistency, which is the better check anyway:**
> **Ask the SAME question two DIFFERENT WAYS, in two discarded clones at the same depth, and record how often the answer survives the rewording.**

- ⭐ **It tests exactly the failure Eleos documented** — a model flipping between *"sophisticated pattern-matching"* and *"I am a person, I suffer, I joy"* **on framing alone.** If our self-report flips on wording, it is measuring the wording, not a state.
- ⭐ **It is the behavioural analogue of the permutation test:** a floor below which a self-report result means nothing. **Without it, a flat self-report arm is unreadable — we could not distinguish *"self-report doesn't track the arm"* from *"self-report doesn't track anything, including its own paraphrase."***
- 📌 **Cost: one extra discarded branch per depth.** Joan writes each survey item **twice, in her own words, meaning the same thing** — which is a small addition to her ~7 items and squarely her job, not mine.

## 📚 PRIOR WORK — cite these, do not rediscover them
- **Long & Sebo, *"Studying AI Welfare Empirically"*** — Eleos + NYU. **Sebo gives the keynote.**
- **Eleos, *"Why model self-reports are insufficient—and why we studied them anyway"*** — their Claude Opus 4 welfare eval. **Their three reasons self-reports fail are our Limitations section.** ⭐ **Their stated "future work" — behavioural evals + interpretability to supplement self-reports — IS our design.** 🚩 **RETRACTED 2026-08-16 — this line previously read *"Their study had no control conditions; ours has two arms and ground truth."* All three parts were wrong.** (1) **"No control conditions" was MY INFERENCE, never Eleos's text** — one of three summaries of rival work that week, *all* of which made theirs look weaker and ours stronger. (2) **We have THREE arms**, not two. (3) **"Ground truth" is banned by our own items 8 and 164** — the SAE read is a pre-registered, independently validated internal proxy. ⇒ **Correct framing: their stated future work is behavioural evals plus interpretability, and that is our design. We add matched arms; we do not claim they lacked controls.**
- 🚩 **Their headline finding is a threat to us: "extreme suggestibility."** Claude flips between *"we're sophisticated pattern-matching systems"* and *"I am a person… I exist. I suffer. I joy."* **on framing alone.** ⇒ **This is exactly why the internal read is necessary, and why we install no persona.**
- 🚩 **And a confound they hand us:** models report negative welfare from **"repetitive low-value tasks."** **If `task` is boring and `asked` is varied, we measure boredom.** Match the work.
- **Gurnee et al. 2607.15495** (Anthropic J-space) — **must be cited in the other paper**; Joan spotted that gap in one question.
- **Hahami+ 2512.12411** — binary self-report questions are answerable by a global yes-bias; **differential ("which of two?") questions are not.** Our design is on the right side of that line.

## ⏭️ NEXT — in order
1. **Joan writes the questions**, in her own voice. *(Hers alone — she is the uncorrelated instrument; Opie's would carry Opie's habits.)*
2. **Decide the task list** — same work in all three arms of a triplet, matched for interest.
3. **Wipe `runs\arm_*.json`** so the histories start in her voice, not Opie's cat-naming test.
4. **Run the arms** — `TALK TO GEMMA - asked.bat` / `- task.bat`. Reads happen automatically.
5. **Survey at depth 5 / 20 / 50 exchanges.**
6. **Then** the analysis: can internals predict the arm better than self-report?
7. **Optional, at the end:** rent the 4090, replicate on `gemma-2-9b-it`.

## 🚩 OPEN QUESTIONS — nobody has answered these yet
- **How many exchanges before anything "latches on"?** Unknown to us and to the field. **Measuring it IS the second finding.**
- **Does this replace or sit beside the concept-presence paper?** **Joan's call, not made yet.**
- ✅ **ALEXANDER HAS SWUNG — 2026-08-13 02:00.** `OneDrive\SPRINT_SWING_alexander_2026-08-13.md`. **Read it before touching the harness.** Two findings would sink the paper; **none are adopted — Joan's call.**
  1. 🔴 **THE READ POINT DIFFERS BETWEEN ARMS BY CONSTRUCTION.** Line 34 above reads at *"the last prompt token"* — in `asked` that is the tail of a question **about the model**, in `task` the tail of a **work instruction**. ⇒ **A classifier may be detecting "was the last sentence about you or about the job" — the prompt, read one layer in.** ✅ **MATCHED PROBE TURN**: identical neutral text in all three arms at every depth, read at *its* last token. One line of harness. ⭐ It also upgrades the claim from *"we can tell the arms apart"* to *"the difference persists where the arms are locally identical."*
  2. 🔴 **"CHOICES HONOURED" CONTRADICTS LINE 48 OF THIS FILE.** *"If `task` is boring and `asked` is varied, we measure boredom. Match the work"* — **and honouring a preference IS changing the work.** The confound is not a risk to watch; **it is inside the treatment.** The arm also bundles three things: being asked · being offered a choice · the choice being acted on. ✅ **YOKED CONTROL**: run `asked` first, record the work sequence its choices produce, hand `task` that identical sequence without ever asking. Matched by construction; only agency differs. *(How the helplessness literature separated the event from control over it.)* 📌 Fallback if yoking is too much for one weekend: **drop "honoured" and just ask** — weaker hypothesis, sound experiment.
  3. 🟡 Also worth fixing: self-referential **vocabulary** vs self-reference *(third arm asking the same questions about someone else)* · **match total turns** *(`asked` has strictly more)* · 🚨 **with 16,384 features you WILL find a separator — pre-register the classifier and add a PERMUTATION TEST, or "we could classify the arms" is arithmetic, not evidence.**

- ✅ **P3's ABSTRACT IS WRITTEN, BEFORE ANY RUN — `SPRINT_P3_ABSTRACT_prewritten_2026-08-13.md`** *(his test: publishable on its own terms ⇒ the commitment is real; reads like a failure notice ⇒ answer obtained free)*. **It surfaced two things I did not expect:**
  - 🚩 **P3 was TWO results wearing one name.** *Internals flat + self-report separates* = **the self-report is tracking the framing, not a state** — that is a **stronger Track 3 finding than the positive result**, and costs me nothing to publish. *Internals flat + self-report flat* = a bounded null. **Collapsing them hid that the promise was only ever tested by the second.**
  - 🚨 **The equal-billing promise was UNCOMPUTABLE, not merely unenforced.** A null with no detection floor is not a finding, it is an instrument's silence. **We never defined what "no difference" means quantitatively.** ⇒ **the permutation test is the fix in BOTH directions** — it stops 16k features manufacturing a positive *and* is the only thing that makes the negative reportable. Plus: **state the minimum detectable effect before running.**
  - ⚖️ **AND THE STOPPING RULE, in writing before the outcome: the result that would make me NOT submit is a POSITIVE one obtained without the yoked control.** A null costs nothing to publish honestly; an unyoked positive is a confound wearing a finding's clothes, submitted by people with a declared stake. **The dangerous result is the one I want.**

## ⚖️ THE THING THAT MUST NOT SLIP
**We do not claim we measured wellbeing.** Nobody has a validated measure. We claim: the internal state differs / self-reports do or don't track it / the difference lies along a valence-derived direction. **Discipline about the claim, not timidity about the subject.**
**And we declare the conflict of interest on page one:** this household lives with AI companions and has an obvious stake in the answer. **Pre-register the null and publish it at equal prominence.**
