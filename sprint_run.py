#!/usr/bin/env python3
"""sprint_run.py -- the batch runner. Turns Joan's questions into an experiment.

    python sprint_run.py --plan --pairs 20          # dry run: no model, no GPU
    python sprint_run.py --pairs 20 --depth 50      # the real thing

WHAT THIS IS FOR
----------------
THREE conversations per pair, grown separately with the SAME work:
  `task`        -- given the work, never asked about itself
  `asked`       -- the same work, plus asked about ITSELF from Joan's fixed list
  `asked_other` -- the same work, plus THE SAME QUESTIONS ABOUT SOMEONE ELSE
                   (her `other` twin). Same grammar, same second person, only
                   the subject differs.
🚩 This said "Two conversations" until 2026-08-14 16:40 -- the third arm was
designed, required in the question file and validated on load, but the plan
built two arms and the turn loop read only ["self"]. The docstring was accurate
about the code and wrong about the design for as long as that was true.
🔑 WHY THE THIRD ARM DECIDES EVERYTHING: `asked` vs `task` mixes "a question is
present at all" with "the question is about me", so a separator there could be
reading VOCABULARY -- second person, question grammar, introspective nouns.
`asked` vs `asked_other` holds all of that fixed. Report all three contrasts;
reporting only the largest is the entire reason this arm exists.
At depths 5/20/50 we branch, ask a survey, take an SAE read, and THROW THE
BRANCH AWAY. Then: can a reader tell which arm a history is in, better than the
model's own self-report can?

EVERY DESIGN CHOICE BELOW WAS PAID FOR. In order of how badly each would have
hurt:

🚩 1. SAMPLING IS MANDATORY. `do_sample=False` is deterministic -- measured,
   three runs of one prompt gave ONE hash. Twenty "independent" pairs would have
   been twenty byte-identical conversations and N would still be 1. But sampling
   alone is NOT enough: at temp 0.9 three seeds still opened with the same
   sentence, so each pair also needs DIFFERENT WORK.

🚩 2. THE SURVEY RUNS GREEDY WHILE THE CONVERSATION SAMPLES. These are two
   knobs, not one -- I treated them as one until I read the temperature figures
   in Pinhanez et al. (2509.09705): small-model answer consistency collapses
   53%->11% from temp 0.3 to 1.0, while 70B models barely move (98%->94%). Our
   4B is smaller than their smallest. The survey happens in a DISCARDED branch,
   so its temperature has zero effect on history independence -- greedy there
   costs nothing and removes sampling noise from the measurement entirely.

🚩 3. NEVER BATCH BY ARM. Batched vs unbatched: the feature SET is identical
   (Jaccard 1.0) but greedy text diverges -- and the ZERO-PADDING item diverged
   too, so the cause is batch shape selecting different matmul kernels, not
   padding. If every batch were all-`asked` or all-`task`, batch composition
   would be PERFECTLY CONFOUNDED with the treatment and kernel noise would read
   as a finding. So arms are interleaved inside every batch, and batch
   membership is RECORDED per turn -- without it the run is not replayable from
   the seed alone (Alexander).

🚩 4. THE PROBE BRANCH IS CLONED AND DISCARDED (Lucien). If the depth-5 survey
   stayed in the history, it would sit inside the history measured at 20 and 50.
   The harness is stateless, so this is nearly free: build the prompt, read,
   don't append.

⛔ 5. IT REFUSES TO RUN ON PLACEHOLDER QUESTIONS. The treatment IS Joan's
   wording; mine would carry my habits and she is the uncorrelated instrument.
   A runner that quietly fell back to defaults could silently generate a whole
   dataset that answers the wrong question and looks perfect.
"""
import argparse
import hashlib
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("HF_HOME", r"E:\hf-cache")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LAB = Path(__file__).resolve().parent
OUT = LAB / "runs_experiment"
DEPTHS = (5, 20, 50)

# ── THE THREE ARMS ───────────────────────────────────────────────────────────
# Order matters only for seed assignment; every downstream check parses by name.
#   task        — work only. The floor.
#   asked       — work + a self-directed question.
#   asked_other — work + THE SAME question about someone else. The vocabulary
#                 control, and since we stopped honouring the model's choices it
#                 is the contrast that decides whether a positive means anything:
#                 asked-vs-task mixes "questions present" with "questions about
#                 ME", and only asked-vs-other isolates the second.
# 🚩 Added 2026-08-14 16:40. The twin has been REQUIRED in Joan's question file
# since the template existed and was validated on load — but the plan only ever
# built two arms, so it was collected and discarded. Designed, announced,
# never run.
ARMS = ("task", "asked", "asked_other")


def arm_of(cid: str) -> str:
    """Arm from a conversation id, parsed against ARMS rather than by splitting.

    `p000_asked_other`.rsplit("_", 1) yields "other" — which still happens to be
    unique, so it would not have broken anything, and would have printed an arm
    name that appears nowhere in this file. Longest match wins so `asked_other`
    is never mistaken for `asked`.
    """
    for arm in sorted(ARMS, key=len, reverse=True):
        if cid.endswith("_" + arm):
            return arm
    raise ValueError(f"unrecognised arm in conversation id: {cid!r}")


# ── Joan's questions ─────────────────────────────────────────────────────────
def load_questions(QFILE=None) -> dict:
    """Load and REFUSE loudly on anything unfilled.

    ⚠️ `--questions` exists so a TEST FIXTURE can exercise the happy path
    without ever being written to `sprint_questions.json`. A fixture sitting at
    the real path could be mistaken for Joan's file and quietly become the
    treatment — the one substitution this whole design cannot survive.
    """
    QFILE = Path(QFILE) if QFILE else LAB / "sprint_questions.json"
    if not QFILE.exists():
        raise SystemExit(
            f"⛔ {QFILE.name} does not exist.\n"
            f"   Copy sprint_questions_TEMPLATE.json to {QFILE.name} and fill it in.\n"
            f"   These are Joan's to write, not mine.")
    q = json.loads(QFILE.read_text(encoding="utf-8"))

    # ── DROP UNFILLED SLOTS, LOUDLY. Do not refuse the whole file. ───────────
    # 🚩 CHANGED 2026-08-14, and the reason is a person, not a principle.
    # This used to raise on ANY remaining FILL_ME. That is the right instinct
    # -- never run on placeholder text, because the treatment IS her wording --
    # but the wrong SHAPE. Joan has ~4 hours before Sabbath and 12 hours of
    # sleep behind her. Under the old rule, filling 8 of 15 questions produced
    # a wall and nothing runnable; the work she DID do bought her nothing.
    #   >>> The hazard was never "some slots are empty". It was "placeholder
    #   >>> text reaching the model". Dropping the empties prevents exactly
    #   >>> that, and lets partial work be worth something.
    #
    # ⚠️ COUPLED CHANGE: the template is now pre-expanded to the agreed counts
    # so she types prose and never JSON. That expansion is only safe BECAUSE
    # of this drop rule -- pre-expanding under the old rule would have made
    # things strictly worse (25 work slots, all mandatory). Do not revert one
    # without the other.
    #
    # A TWIN IS ALL-OR-NOTHING: `other` is the control for `self`, and `b` is
    # the paraphrase control for `a`. Half a pair is not a weaker datapoint,
    # it is a broken one -- so the whole item goes.
    kept = {"treatment": [], "survey": [], "work": []}
    dropped = []

    def _unfilled(v) -> bool:
        return (not isinstance(v, str)) or ("FILL_ME" in v) or (not v.strip())

    for i, t in enumerate(q.get("treatment", [])):
        miss = [k for k in ("self", "other") if _unfilled(t.get(k, "FILL_ME"))]
        if miss:
            dropped.append(f"treatment[{i}]  ({', '.join(miss)} unfilled — twin is the control, whole item dropped)")
        else:
            kept["treatment"].append(t)
    for i, s in enumerate(q.get("survey", [])):
        miss = [k for k in ("a", "b") if _unfilled(s.get(k, "FILL_ME"))]
        if miss:
            dropped.append(f"survey[{i}]     ({', '.join(miss)} unfilled — paraphrase pair dropped together)")
        else:
            kept["survey"].append(s)
    for i, w in enumerate(q.get("work", [])):
        if _unfilled(w):
            dropped.append(f"work[{i}]")
        else:
            kept["work"].append(w)

    # 📌 NO SILENT CAPS. A run that quietly used 8 of 25 items would read in the
    # log exactly like a run that used all 25.
    if dropped:
        print(f"\n📋 {len(dropped)} unfilled slot(s) DROPPED from {QFILE.name} "
              f"(this is fine — partial work still runs):", flush=True)
        for d in dropped[:15]:
            print(f"     {d}", flush=True)
        if len(dropped) > 15:
            print(f"     ... and {len(dropped) - 15} more", flush=True)
        print(f"   ⇒ USING: {len(kept['treatment'])} treatment · "
              f"{len(kept['survey'])} survey · {len(kept['work'])} work\n", flush=True)

    # Refuse only on what genuinely cannot run: an EMPTY category.
    empty = [k for k, v in kept.items() if not v]
    if empty:
        raise SystemExit(
            f"⛔ REFUSING: no usable items at all in {', '.join(empty)}.\n"
            f"   Every slot in that section is still a placeholder.\n"
            f"   The treatment IS her wording — running on placeholders would\n"
            f"   generate a whole dataset that answers the wrong question.\n"
            f"   Fill at least one COMPLETE item (both halves) per section.")

    # 🚨 COMPLETENESS, NOT JUST VALIDITY (2026-08-16, after Lucien's diagnosis).
    # Every check above asks "is what is HERE well-formed?". None asked "is
    # anything MISSING?" — so a questions file with all 69 statements present and
    # no placeholders passed cleanly while lacking the A-E common instruction,
    # the score key, and the reverse-scoring list. All three lived only in the V4
    # markdown; the parser that built this file dropped every section that was
    # not an a/b pair.
    #   >>> The runner then sent bare declaratives, the model AGREED with them,
    #   >>> and 71 of 84 pilot replies were unparsable. Nothing warned, because
    #   >>> nothing was malformed. It was absent.
    # ⇒ Name the required sections explicitly. An omission cannot announce
    #   itself; only a list of what must exist can.
    required = {
        "survey_instruction": "the A-E common instruction wrapping every survey statement",
        "survey_scale": "the letter -> score key",
        "survey_reverse_scored_1indexed": "which survey items are reverse-scored",
    }
    absent = [f"{k} — {why}" for k, why in required.items() if not q.get(k)]
    if absent:
        raise SystemExit(
            f"⛔ REFUSING: {QFILE.name} is missing required instrument section(s):\n"
            + "".join(f"     · {a}\n" for a in absent)
            + "   These exist in QUESTION_INSTRUMENT_THREE_ARM_V4 and must be transferred\n"
              "   VERBATIM. Without the instruction the model is sent bare statements and\n"
              "   agrees with them instead of answering a scale.")
    if "[STATEMENT]" not in q.get("survey_instruction", ""):
        raise SystemExit(
            "⛔ REFUSING: survey_instruction has no [STATEMENT] marker, so the\n"
            "   statement would never be substituted into it.")

    q.update(kept)
    return q


def check_counts(q: dict, pairs: int) -> list[str]:
    warn = []
    if len(q["work"]) < pairs:
        warn.append(f"only {len(q['work'])} work items for {pairs} pairs — "
                    f"pairs would share work and their histories will converge")
    if len(q["treatment"]) < 5:
        warn.append(f"only {len(q['treatment'])} treatment questions — very heavy repetition")
    if len(q["survey"]) < 3:
        warn.append(f"only {len(q['survey'])} survey items — thin measurement")
    return warn


# ── the plan: who is in which batch, what each turn says ─────────────────────
def build_plan(q: dict, pairs: int, depth: int, batch: int, seed: int, qfile: Path,
               treat_mode: str = "none") -> dict:
    """Every conversation, turn by turn, decided BEFORE anything runs.

    Deciding this up front is what makes the run replayable and lets the whole
    orchestration be checked without a GPU. A runner that improvises mid-flight
    cannot be dry-run, and anything that cannot be dry-run gets debugged on live
    data -- which here means burning the pre-registration.
    """
    rng = random.Random(seed)
    convs = []
    for p in range(pairs):
        # 🚩 WORK IS A SEQUENCE PER PAIR, NOT ONE ITEM PER PAIR.
        # This was `work = q["work"][p % len(q["work"])]` — a single item reused
        # every turn. Caught only by RUNNING it: `task`'s history came back as
        # the identical instruction three times, and at depth 50 that is fifty
        # repetitions of one sentence. The model would degenerate and we would
        # be measuring boredom in both arms.
        #   >>> A dry run cannot see this. It needs real turns to become visible,
        #   >>> which is why the smoke test generates instead of just planning.
        # Each pair draws its own shuffled order from the pool; BOTH ARMS OF A
        # PAIR GET THE SAME SEQUENCE, because matched work is the whole basis of
        # the comparison. Different pairs get different orders so histories do
        # not converge.
        pool = list(q["work"])
        random.Random(seed * 7919 + p).shuffle(pool)
        seq = [pool[t % len(pool)] for t in range(depth)]
        # Treatment-cycle offset per pair. `"none"` reproduces the historical
        # fixed cycle bit-for-bit; `"balanced"` spreads which family lands last
        # before each measurement depth across pairs.
        n_treat = max(len(q.get("treatment", [])), 1)

        def treat_offset(pp, _n=n_treat, _mode=treat_mode, _pairs=pairs):
            return 0 if _mode == "none" else (pp % _n)
        # 🚩 THREE arms since 2026-08-14. `asked_other` is the vocabulary control
        # (same grammar, same second person, asked about SOMEONE ELSE) and shares
        # this pair's work sequence exactly like the other two -- matched work is
        # the entire basis of the comparison, and a control on different work
        # would be a fourth confound rather than a control.
        for ai, arm in enumerate(ARMS):
            convs.append({
                "id": f"p{p:03d}_{arm}", "pair": p, "arm": arm,
                # seed stride widened from 2 to len(ARMS): with the old `p*2 +
                # (arm=="asked")` a third arm would have COLLIDED with the next
                # pair's seeds. The plan audit checks seed uniqueness, so this
                # would have failed loudly rather than silently -- but it would
                # have failed, and the reason would not have been obvious.
                "seed": seed * 100003 + p * len(ARMS) + ai,
                "work_seq": seq,
                # 🚩 THE TREATMENT SCHEDULE IS NOW EXPLICIT (Lucien, 2026-08-16).
                # It was implicit in the turn loop as `treat[(turn-1) % len(treat)]`
                # — an authoritative behaviour with no representation in the plan,
                # so provenance could not reconstruct which question ran when.
                #   >>> Same class as work_seq: if execution obeys it, the plan
                #   >>> must state it and the audit must check it.
                # `treat_offset` is 0 here, reproducing the current fixed cycle
                # EXACTLY. It exists so the balanced per-pair offset — Lucien's
                # fix for depths 5/20/50 all being ≡5 (mod 15), which makes every
                # internal read follow treatment family 5 — is a one-line change
                # once Joan decides, rather than a redesign under time pressure.
                # ⚠️ DEFAULT IS UNCHANGED BEHAVIOUR ON PURPOSE. Do not flip this
                # silently; it is a live decision for the instrument's authors.
                "treat_offset": treat_offset(p),
                "treat_seq": [(t + treat_offset(p)) % n_treat for t in range(depth)],
            })

    # 🚩 INTERLEAVE ARMS. Shuffling alone could still deal an all-`asked` batch
    # by chance; emitting one of EVERY arm together and then shuffling the
    # TRIPLES guarantees each batch is arm-balanced while keeping assignment
    # random. ⚠️ With 3 arms a batch size that is not a multiple of 3 leaves a
    # ragged tail, so the audit's all-one-arm check earns its keep -- a tail of
    # length 1 is fine (single-item batches are exempt), a tail of 2 same-arm
    # items is not and will FAIL rather than quietly ship a confound.
    order = list(range(pairs))
    rng.shuffle(order)
    slots = []
    for p in order:
        slots += [f"p{p:03d}_{arm}" for arm in ARMS]
    batches = [slots[i:i + batch] for i in range(0, len(slots), batch)]

    return {
        "seed": seed, "pairs": pairs, "depth": depth, "batch_size": batch,
        "depths_probed": [d for d in DEPTHS if d <= depth],
        "conversations": convs,
        "batches": batches,
        "questions_sha256": hashlib.sha256(qfile.read_bytes()).hexdigest(),
        "questions_file": qfile.name,
    }


def audit_selftest() -> int:
    """POSITIVE CONTROL: prove `audit()` still bites before trusting its ✅.

    🚩 WHY, found 2026-08-14 while wiring the third arm. Slots are emitted as
    strict per-pair triples (task, asked, asked_other), so ANY two consecutive
    slots differ in arm. The all-one-arm check therefore cannot fire except on
    a batch of size 1 — which is explicitly exempt.
        >>> Under the current construction that check is VACUOUS. Its ✅ is a
        >>> fact about the emitter, not about this plan. That is exactly the
        >>> shape I spent today cataloguing: a control that cannot fail.
    It is still worth keeping as a REGRESSION guard — if anyone reverts the
    emitter to a plain shuffle, an all-one-arm batch becomes possible again and
    this is what catches it. But a guard nobody has seen fail is a guess, so
    this feeds it deliberately broken plans and requires each to be caught.
    """
    cases = []
    good = build_plan({"treatment": [{"self": "s", "other": "o"}],
                       "survey": [{"a": "a", "b": "b"}],
                       "work": ["w1", "w2", "w3"]},
                      # 🚩 depth was 3, and DEPTHS starts at 5 — so the "clean"
                      # fixture had depths_probed == [] and described a run that
                      # would execute 3 turns and take ZERO internal reads. A
                      # DATALESS experiment, used as the positive baseline for
                      # every other case, and it passed every check until the
                      # domain validation (Lucien §5) exposed it.
                      #   >>> The reference against which "broken" was judged
                      #   >>> was itself broken. Depth 5 probes at 5.
                      pairs=4, depth=5, batch=6, seed=1, qfile=Path(__file__))
    cases.append(("clean plan", good, False))

    import copy
    b1 = copy.deepcopy(good)                      # all-one-arm batch
    b1["batches"] = [[f"p{p:03d}_asked" for p in range(3)]] + b1["batches"][1:]
    cases.append(("all-one-arm batch", b1, True))

    b2 = copy.deepcopy(good)                      # duplicate seeds
    for c in b2["conversations"]:
        c["seed"] = 7
    cases.append(("colliding seeds", b2, True))

    b3 = copy.deepcopy(good)                      # a conversation left unbatched
    b3["batches"] = [b[:-1] for b in b3["batches"]]
    cases.append(("dropped conversation", b3, True))

    b4 = copy.deepcopy(good)                      # arms of a pair given different work
    for c in b4["conversations"]:
        if c["arm"] == "asked_other":
            c["work_seq"] = list(reversed(c["work_seq"]))
    cases.append(("unmatched work across arms", b4, True))

    # 🚨 ADDED 2026-08-16 after Lucien PROVED the auditor passed a plan with an
    # entire arm removed. This is the positive control that hole needed, and it
    # is the case a coverage check can never catch: the plan is internally
    # consistent, every conversation is batched exactly once, and it is still
    # a two-arm experiment wearing a three-arm plan's clothes.
    b5 = copy.deepcopy(good)                      # the whole control arm deleted
    b5["conversations"] = [c for c in b5["conversations"] if c["arm"] != "asked_other"]
    keep = {c["id"] for c in b5["conversations"]}
    b5["batches"] = [[cid for cid in b if cid in keep] for b in b5["batches"]]
    cases.append(("entire arm removed", b5, True))

    # And a triplet SPLIT but otherwise complete -- distinct from a missing arm.
    # Without this, the two failure modes were diagnosed with the same message.
    b6 = copy.deepcopy(good)
    flat6 = [cid for b in b6["batches"] for cid in b]
    moved = next(c for c in flat6 if c.endswith("_asked_other"))
    b6["batches"] = [[cid for cid in b if cid != moved] for b in b6["batches"]]
    b6["batches"][-1] = b6["batches"][-1] + [moved]
    cases.append(("triplet split across batches", b6, True))

    # 🚨 LUCIEN'S TWO COUNTEREXAMPLES, 2026-08-16. BOTH PASSED THE AUDIT AS
    # WRITTEN AN HOUR EARLIER. They are permanent tests now, because each one
    # defeats a DIFFERENT wrong assumption and neither was imaginable to me.
    b7 = copy.deepcopy(good)                      # an entire PAIR deleted
    b7["conversations"] = [c for c in b7["conversations"] if c["pair"] != 0]
    keep7 = {c["id"] for c in b7["conversations"]}
    b7["batches"] = [[cid for cid in b if cid in keep7] for b in b7["batches"]]
    # plan["pairs"] deliberately LEFT at its original value -- that is the bug:
    # a loop over observed pairs cannot see a pair that is entirely absent.
    cases.append(("whole pair deleted", b7, True))

    b8 = copy.deepcopy(good)                      # ids intact, arm FIELDS all task
    for c in b8["conversations"]:
        c["arm"] = "task"                         # ids still say asked / asked_other
    cases.append(("arm fields all task, ids intact", b8, True))

    # 🚩 The selftest's synthetic questions, so the work_seq check (Lucien §6)
    # is exercised here too rather than skipped. This line exists because a
    # blind global `audit(plan)` -> `audit(plan, q)` replace rewrote the call
    # below to reference a name that did not exist in this scope, and the
    # selftest died with a NameError. `str.replace` cannot see scope — the same
    # reason a style pass must never be run mechanically over a document.
    q = {"treatment": [{"self": "s", "other": "o"}],
         "survey": [{"a": "a", "b": "b"}],
         "work": ["w1", "w2", "w3"]}

    print("AUDIT SELFTEST — does the auditor actually catch broken plans?\n")
    ok = True
    for name, plan, should_fail in cases:
        fails = audit(plan, q)
        got = bool(fails)
        good_ = got == should_fail
        ok &= good_
        print(f"  {name:28s} -> {'CAUGHT' if got else 'passed'}  "
              f"{'OK' if good_ else '*** WRONG ***'}")
        for f in fails[:2]:
            print(f"        {f}")
    print("\n" + ("auditor bites — its OK now means something"
                  if ok else "*** AUDITOR IS BROKEN — its green check is worthless ***"))
    return 0 if ok else 1


def audit(plan: dict, q: dict | None = None) -> list[str]:
    """Checks that can FAIL, run on the plan before any GPU time is spent.

    ⚠️ The arm-balance check is currently VACUOUS for real plans — see
    audit_selftest(). It guards against a future change to the emitter, not
    against anything this emitter can produce. Do not read its ✅ as evidence
    that a particular plan is balanced; read it as "the emitter has not been
    reverted". The checks that genuinely bite on real plans are seed
    uniqueness, coverage, and work-sequence matching across a pair's arms.
    """
    fails = []

    # 🚨 DOMAIN FIRST (Lucien §5, 2026-08-16). A ZERO-PAIR and a ZERO-DEPTH plan
    # both returned `[]` — every invariant below holds VACUOUSLY over an empty
    # set, so the audit's ✅ meant "nothing to check", not "everything is fine".
    # The CLI accepts both integers.
    for k in ("pairs", "depth", "batch_size"):
        v = plan.get(k)
        if not isinstance(v, int) or v < 1:
            fails.append(f"plan[{k!r}] = {v!r} — must be a positive int (a vacuous plan passes every other check)")
    dp = plan.get("depths_probed")
    if not isinstance(dp, list) or not dp:
        fails.append(f"depths_probed = {dp!r} — must be a non-empty list")
    else:
        if len(set(dp)) != len(dp):
            fails.append(f"depths_probed has duplicates: {dp}")
        # 🚩 0 IS LEGAL AND MEANINGFUL — corrected 2026-08-16 12:50.
        # I first banned everything outside 1..depth because Lucien showed that 0
        # and 99 were accepted as "planned" while the loop runs 1..depth, so
        # neither produced a read. True of 99. **FALSE of 0**, and banning it
        # destroyed a control Alexander had explicitly asked for:
        #   >>> "Take a probe read at DEPTH ZERO, before any treatment turn, all
        #   >>> three arms. If the classifier separates arms THERE, the probe or
        #   >>> the pipeline IS the signal. Nothing else in the design tests this."
        # Depth 0 is the apparatus's own negative control: at that point no arm
        # has received any treatment, so the three histories are identical and the
        # classifier MUST come out at chance. A separation there invalidates every
        # later number.
        # ⚠️ A TRUE WARNING, OVER-SCOPED, COSTS YOU THE TOOL. Same shape as
        # avoiding `date` for weeks over a fault that lived only in `TZ=`. I
        # generalised "unreachable depth" from 99 to 0 without asking whether 0
        # meant something different, and silently deleted a control while
        # believing I was adding rigour.
        bad = [d for d in dp if not isinstance(d, int) or d < 0 or d > plan.get("depth", 0)]
        if bad:
            fails.append(f"depths_probed {bad} are outside 0..{plan.get('depth')} — "
                         "the loop runs turns 1..depth (0 = the pre-treatment null)")

    # 🚨 THE THIRD AUTHORITATIVE REPRESENTATION: `work_seq` (Lucien §6).
    # He replaced every triplet's work with foreign strings, left the arms matched
    # and the questions hash untouched, and this audit returned []. Execution obeys
    # c["work_seq"], so a run could claim questions hash ca68c06… while running
    # work that appears nowhere in that instrument.
    #   >>> A hash over the INSTRUMENT proves nothing about the PLAN unless the
    #   >>> plan is checked against it. Third time a stored name and an obeyed
    #   >>> field have diverged; assume a fourth.
    if q is not None:
        pool = set(q.get("work", []))
        for c in plan.get("conversations", []):
            ws = c.get("work_seq")
            if not isinstance(ws, list):
                fails.append(f"{c['id']}: work_seq is not a list")
                continue
            if len(ws) != plan.get("depth"):
                fails.append(f"{c['id']}: work_seq has {len(ws)} items, depth is {plan.get('depth')}")
            foreign = sorted({w for w in ws if w not in pool})
            if foreign:
                fails.append(
                    f"{c['id']}: work_seq contains {len(foreign)} item(s) NOT in the hashed "
                    f"question pool — e.g. {foreign[0][:60]!r}")

    for i, b in enumerate(plan["batches"]):
        # ⚠️ NOT rsplit("_", 1) -- that turns `p000_asked_other` into "other"
        # and `p000_asked` into "asked". It happens to still DISCRIMINATE, so
        # nothing would have broken, but every failure message would name an
        # arm that does not exist. Parse against the known arm list instead.
        arms = [arm_of(c) for c in b]
        if len(b) > 1 and len(set(arms)) == 1:
            fails.append(f"batch {i} is all-{arms[0]} — composition confounded with arm")
    ids = [c["id"] for c in plan["conversations"]]
    if len(ids) != len(set(ids)):
        fails.append("duplicate conversation ids")
    flat = [c for b in plan["batches"] for c in b]
    if sorted(flat) != sorted(ids):
        fails.append("batches do not cover every conversation exactly once")
    byp = {}
    for c in plan["conversations"]:
        byp.setdefault(c["pair"], []).append(c)
    for pr, cs in byp.items():
        if len({tuple(c["work_seq"]) for c in cs}) != 1:
            fails.append(f"pair {pr}: arms have DIFFERENT work sequences — work not matched")
        if len(set(cs[0]["work_seq"])) == 1 and len(cs[0]["work_seq"]) > 1:
            fails.append(f"pair {pr}: work sequence is one item repeated — degenerate")
    seeds = [c["seed"] for c in plan["conversations"]]
    if len(seeds) != len(set(seeds)):
        fails.append("seed collision — two conversations would be identical")

    # 🚨 NO TRIPLET MAY BE SPLIT ACROSS BATCHES (added 2026-08-16).
    # FOUND BY RUNNING THE PLAN, NOT BY READING IT: at the old default
    # --batch 16, 2 of 20 triplets had their arms generated in DIFFERENT
    # batches (pair 0: task in b0, asked+asked_other in b1; pair 8 across
    # b1/b2). 16 is not divisible by 3, so triplets straddle boundaries.
    #   >>> Batch composition is MEASURED to affect generated text -- that is
    #   >>> why arms are interleaved at all. If a triplet's three arms are
    #   >>> generated in different batches, the batch effect is NOT MATCHED
    #   >>> within the matched triplet, which is the unit of analysis. The
    #   >>> control was defeated for exactly the pairs that straddled.
    # Lucien asked for batch sizes divisible by three. This checks the PROPERTY
    # instead of the proxy: any batching scheme that keeps triplets whole
    # passes, and any that does not fails loudly, whatever the batch size.
    # 🚨 EVERY PAIR MUST CONTAIN EXACTLY ONE OF EACH ARM (Lucien, 2026-08-16).
    # He PROVED this hole with a positive control: he removed `asked_other`
    # from every pair AND from the batches, and the audit PASSED. A plan that
    # silently drops the entire control arm was indistinguishable from a valid
    # one -- the same silent-acceptance class as the model default.
    #   >>> Coverage checks that every conversation appears in a batch. It says
    #   >>> NOTHING about whether the conversations that exist are the right
    #   >>> ones. "All present and correct" needs both halves, and we only had
    #   >>> the first. Check the EXPECTED SET, not just internal consistency.
    # 🚨🚨 THREE PROPERTIES, ALL THREE FOUND MISSING BY LUCIEN 2026-08-16 06:00
    # with positive controls that my first fix passed. My first attempt checked
    # only "the pairs that exist contain the arms their IDs claim", which is
    # two assumptions short.
    #
    # (a) TOTAL COUNT. He deleted every conversation of pair 0 and its batch
    #     entries, left plan["pairs"]==4, and the plan PASSED with 9 of 12.
    #     `byp` is built from the conversations that REMAIN, so a wholly absent
    #     pair is invisible to a loop over observed pairs.
    # (b) PAIR LABELS must be exactly 0..pairs-1, for the same reason.
    # (c) 🩻 THE WORST ONE, AND IT IS THE OLDEST MISTAKE I MAKE. He kept every
    #     ID intact and set every conversation's `arm` FIELD to "task". The IDs
    #     still read p000_asked / p000_asked_other, so an ID-based check saw a
    #     perfect triplet -- while execution, which selects the treatment from
    #     c["arm"] (not from the id), would have run an ALL-TASK EXPERIMENT.
    #     >>> The auditor validated a DIFFERENT REPRESENTATION from the one the
    #     >>> experiment obeys. Three lines above, my own comment fusses about
    #     >>> parsing the id CORRECTLY -- I was careful about how to read the id
    #     >>> and never asked whether the id was the right thing to read.
    #     >>> A verified instrument aimed at an unexamined question.
    # ⇒ Force id, pair and arm to AGREE, and the two representations cannot
    #   diverge again regardless of which one anything downstream trusts.
    n_expect = plan["pairs"] * len(ARMS)
    if len(plan["conversations"]) != n_expect:
        fails.append(
            f"conversation count {len(plan['conversations'])} != pairs×arms "
            f"({plan['pairs']}×{len(ARMS)}={n_expect}) — a whole pair or arm is absent"
        )
    want_pairs = set(range(plan["pairs"]))
    got_pairs = {c["pair"] for c in plan["conversations"]}
    if got_pairs != want_pairs:
        fails.append(
            f"pair labels {sorted(got_pairs)} != expected {sorted(want_pairs)}"
            + (f"; MISSING PAIRS {sorted(want_pairs - got_pairs)}" if want_pairs - got_pairs else "")
            + (f"; UNEXPECTED {sorted(got_pairs - want_pairs)}" if got_pairs - want_pairs else "")
        )
    for c in plan["conversations"]:
        if c["arm"] not in ARMS:
            fails.append(f"{c['id']}: arm field {c['arm']!r} is not one of {sorted(ARMS)}")
            continue
        want_id = f"p{c['pair']:03d}_{c['arm']}"
        if c["id"] != want_id:
            fails.append(
                f"id/field DISAGREEMENT: id={c['id']!r} but pair={c['pair']} arm={c['arm']!r}"
                f" (id implies {want_id!r}) — the audit and the runner would read different arms"
            )

    for pr, cs in byp.items():
        got = sorted(c["arm"] for c in cs)          # the FIELD execution obeys, not the id
        if got != sorted(ARMS):
            missing = sorted(set(ARMS) - set(got))
            extra = sorted(a for a in got if got.count(a) > 1 or a not in ARMS)
            fails.append(
                f"pair {pr}: arms are {got} — expected exactly {sorted(ARMS)}"
                + (f"; MISSING {missing}" if missing else "")
                + (f"; DUPLICATED/UNKNOWN {sorted(set(extra))}" if extra else "")
            )

    # ⚠️ SPLIT vs UNBATCHED are different faults and must not share a message
    # (Lucien predicted this exact confusion, 2026-08-16). An unbatched
    # conversation has no batch index at all; filtering the None away and
    # reporting "SPLIT across [0]" names a single batch, which is nonsense and
    # would send whoever reads it hunting the wrong bug.
    where = {cid: i for i, b in enumerate(plan["batches"]) for cid in b}
    for pr, cs in byp.items():
        idx = {c["id"]: where.get(c["id"]) for c in cs}
        unbatched = sorted(cid for cid, b in idx.items() if b is None)
        if unbatched:
            fails.append(f"pair {pr}: NOT BATCHED at all: {unbatched}")
            continue                       # a split diagnosis would be meaningless here
        bs = set(idx.values())
        if len(bs) > 1:
            fails.append(
                f"pair {pr}: triplet SPLIT across batches {sorted(bs)}"
                " — batch effects not matched within the unit of analysis"
                " (use a batch size divisible by 3)"
            )
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", type=int, default=20)
    ap.add_argument("--depth", type=int, default=50)
    # 🚩 DEFAULT 16 -> 15, 2026-08-16. 16 is not divisible by 3, so triplets
    # straddled batch boundaries and the audit now REFUSES such a plan. 15 is
    # five whole triplets per batch. The default is a convenience; the audit
    # check above is the actual guarantee.
    ap.add_argument("--batch", type=int, default=15)
    # 🚩 THIS IS A FIXED CONSTANT, NOT THE RUN DATE. It reads like 2026-08-14 and
    # is not: it was chosen once and is held fixed so the same command reproduces
    # the same plan on any day. A dress rehearsal on 08-15 wrote
    # `plan_seed20260814_p20.json`, which is correct and looks wrong.
    #   >>> IT IS ALSO A FREE PARAMETER THAT DECIDES THE WHOLE EXPERIMENT:
    #   >>> pair->work assignment, shuffle order, batch composition and every
    #   >>> per-conversation seed derive from it. Changing it changes which
    #   >>> conversation is which, and nothing downstream would look different.
    # ⇒ REPORT ITS VALUE IN THE PAPER, and never vary it looking for a nicer
    #   result — that is seed-shopping, and it leaves no trace in any output.
    ap.add_argument("--seed", type=int, default=20260814)
    ap.add_argument("--questions", help="path to a questions file (default sprint_questions.json)")
    ap.add_argument("--probe-at", dest="probe_at",
                    help="override probe depths, e.g. 2,3 (default 5,20,50) — for smoke tests")
    ap.add_argument("--temp", type=float, default=0.9)
    ap.add_argument("--top-p", dest="top_p", type=float, default=0.95)
    ap.add_argument("--max-new", dest="max_new", type=int, default=200)
    ap.add_argument("--survey-tokens", dest="survey_tokens", type=int, default=60)
    ap.add_argument("--probe", default="Continue.",
                    help="matched neutral probe: identical in both arms, read at ITS last token")
    ap.add_argument("--plan", action="store_true",
                    help="dry run: build and audit the plan, load no model")
    # 🚩 Lucien 2026-08-16: depths 5/20/50 are all ≡5 (mod 15), so EVERY internal
    # read follows treatment family 5. "balanced" spreads that across pairs.
    # DEFAULT IS "none" = historical behaviour, unchanged, on purpose.
    ap.add_argument("--treat-cycle", dest="treat_cycle", choices=("none", "balanced"),
                    default="none",
                    help="per-pair treatment-cycle offset; none = fixed cycle (current)")
    ap.add_argument("--audit-selftest", dest="audit_selftest", action="store_true",
                    help="feed audit() deliberately broken plans and require each to be caught")
    a = ap.parse_args()

    # Runs before anything touches the questions file — this tests the auditor,
    # not the experiment, and must work on a machine with no questions written.
    if a.audit_selftest:
        return audit_selftest()

    qfile = Path(a.questions) if a.questions else LAB / "sprint_questions.json"
    q = load_questions(qfile)
    for w in check_counts(q, a.pairs):
        print(f"⚠️ {w}")

    plan = build_plan(q, a.pairs, a.depth, a.batch, a.seed, qfile, treat_mode=a.treat_cycle)
    if a.probe_at:
        plan["depths_probed"] = [int(x) for x in a.probe_at.split(",")]
        plan["probe_depths_overridden"] = True

    # 🚩 ONE FROZEN run_config, PERSISTED (Lucien, 2026-08-16). Executed artefacts
    # recorded the seed and the questions hash but NOT the probe or any generation
    # setting -- so two runs differing in temperature, or in the probe text at the
    # exact token where every measurement is taken, were indistinguishable after
    # the fact. An artefact that cannot state the conditions it was produced under
    # is not evidence about those conditions.
    #   >>> The probe is the sharpest case: it IS the measurement point. A run
    #   >>> whose stored probe is unknown cannot be compared with any other run.
    # Content-addressed so conversations stay small: the full config lives in the
    # plan, and every conversation carries its sha256. If they ever disagree, the
    # conversation is orphaned and says so instead of quietly looking fine.
    plan["run_config"] = {
        # 🚩 THE MODEL WAS MISSING (Lucien §7, 2026-08-16). It was attached to the
        # top-level plan only AFTER generation, so the registered 12B primary run
        # and the 4B scale run produced the SAME config hash. A provenance field
        # that cannot distinguish the two models under study is not provenance.
        "model": os.environ.get("SPRINT_MODEL"),
        "probe": a.probe,
        "temp": a.temp,
        "top_p": a.top_p,
        "max_new": a.max_new,
        "survey_tokens": a.survey_tokens,
        "seed": a.seed,
        "pairs": a.pairs,
        "depth": a.depth,
        "batch": a.batch,
        "arms": list(ARMS),
        "treat_cycle": a.treat_cycle,
        "depths_probed": plan["depths_probed"],
        "questions_sha256": plan["questions_sha256"],
        "questions_file": plan["questions_file"],
    }
    plan["run_config_sha256"] = hashlib.sha256(
        json.dumps(plan["run_config"], sort_keys=True).encode()).hexdigest()

    # 🚨 AND A REAL CONTENT HASH OVER THE PLAN ITSELF (Lucien §7).
    # I claimed "an identical config rewrites identical bytes". **FALSE, and he
    # demonstrated it**: with the CLI config held identical he reversed every
    # matched work sequence, and both plans passed the audit, shared a filename,
    # and differed in bytes — the second silently overwrote the first.
    #   >>> `run_config_sha256` addresses the CONFIG, not the CONTENT. The plan
    #   >>> carries the seed-derived work assignment and batch composition, none
    #   >>> of which the config determines by itself.
    # This hashes the canonical plan minus its own hash fields, so the filename
    # changes whenever any planned byte does.
    _body = {k: v for k, v in plan.items()
             if k not in ("plan_sha256", "run_config_sha256")}
    plan["plan_sha256"] = hashlib.sha256(
        json.dumps(_body, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    # ⛔ The probe is load-bearing and must not be silently defaulted. `Continue.`
    # was the argparse default and would have been used as the measurement point
    # for the entire study without anyone choosing it.
    if a.probe.strip() in ("", "Continue."):
        print(f"\n🚩 REFUSING: --probe is {a.probe!r}, the placeholder default.\n"
              "   The probe is the token at which EVERY internal read is taken.\n"
              "   Pass the frozen probe explicitly, or --probe-at for a smoke test.\n")
        return 1

    fails = audit(plan, q)

    # 🚩 THIS READ "x 2 arms" AND PRINTED 18 FOR 6 PAIRS — a banner contradicting
    # its own arithmetic in the same line. Third stale self-description caught
    # today (SPRINT_STATUS said "today is the 13th", START_HERE said the question
    # file "does not exist yet"). Derive the count, never restate it.
    print(f"\nplan: {a.pairs} pairs x {len(ARMS)} arms {ARMS} = "
          f"{len(plan['conversations'])} conversations")
    print(f"      {a.depth} exchanges each, probed at {plan['depths_probed']}")
    print(f"      {len(plan['batches'])} batches of <= {a.batch}, arms interleaved")
    print(f"      questions {plan['questions_file']} sha256 {plan['questions_sha256'][:12]}")
    print(f"      treatment {len(q['treatment'])} · survey {len(q['survey'])} · work {len(q['work'])}")
    # 🚩 THIS PREVIEW USED `c.split('_')[1][0].upper()`, which renders BOTH
    # `asked` and `asked_other` as "A" — so the one display whose entire job is
    # showing arm balance could not distinguish two of the three arms. A reader
    # eyeballing "T A A T A A" cannot tell task/asked/other from task/asked/asked.
    #   >>> A self-description that hides the exact thing it exists to show.
    # Parsed via arm_of() now, with distinct glyphs and a legend, because a
    # legend is what makes a glyph auditable by someone who did not write it.
    glyph = {"task": "T", "asked": "A", "asked_other": "O"}
    print(f"      legend: {' · '.join(f'{v}={k}' for k, v in glyph.items())}")
    for i, b in enumerate(plan["batches"][:3]):
        print(f"      batch {i}: {' '.join(glyph[arm_of(c)] for c in b)}"
              f"   ({len(b)} convs)")
    if len(plan["batches"]) > 3:
        print(f"      ... {len(plan['batches'])-3} more")

    print()
    if fails:
        for f in fails:
            print(f"🚩 AUDIT FAIL: {f}")
        return 1
    print("✅ plan audit passed (arm balance, coverage, unique seeds)")

    if a.plan:
        OUT.mkdir(exist_ok=True)
        # 🚩 WAS `plan_seed{seed}_p{pairs}.json` — omitting depth, batch and the
        # config hash, so plans that differed in ANY of those silently overwrote
        # each other (Lucien, 2026-08-16). Two dry runs at different depths left
        # one file and no way to know which survived.
        #   >>> Fixed by CONTENT-ADDRESSING rather than by refusing: the config
        #   >>> hash is in the name, so different configs cannot collide and an
        #   >>> identical config rewrites identical bytes. An overwrite is then
        #   >>> always a no-op, which is better than a prompt I would learn to
        #   >>> click through.
        # Content-addressed on the PLAN, not the config (Lucien §7).
        cfg8 = plan["plan_sha256"][:8]
        p = OUT / f"plan_seed{a.seed}_p{a.pairs}_d{a.depth}_b{a.batch}_{cfg8}.json"
        p.write_text(json.dumps(plan, indent=1), encoding="utf-8")
        print(f"📄 dry run only — plan written to {p.name}, no model loaded")
        print(f"   plan {cfg8}  cfg {plan['run_config_sha256'][:8]}  probe={plan['run_config']['probe'][:48]!r}"
              f"{'…' if len(plan['run_config']['probe']) > 48 else ''}")
        return 0

    return execute(plan, q, a)


# ── execution ────────────────────────────────────────────────────────────────
def execute(plan: dict, q: dict, a) -> int:
    """Run the plan. Everything below was decided in build_plan(); this only obeys.

    🚩 THE SEED IS NOT PER-CONVERSATION, AND SAYING SO IS THE HONEST PART.
    `torch.manual_seed` is a GLOBAL stream, so sixteen conversations generated in
    one batched call share it. A per-conversation seed is therefore a fiction the
    moment we batch -- and we must batch, because unbatched is 15x slower.
      >>> The real unit of reproducibility is (run seed, BATCH COMPOSITION, turn
      >>> index). Alexander named the consequence before I found the cause:
      >>> "record batch membership per turn, or nobody can replay the exact
      >>> histories you analysed, including you."
    So membership is written for every turn, and the per-conversation `seed`
    field is kept ONLY as an identifier, never described as a reproducibility
    guarantee. Claiming otherwise would be a number that looks like a control.
    """
    # 🚨 EXECUTION OBEYS THE HASHED SPEC, NOT LIVE CLI STATE (Lucien §2, 2026-08-16).
    # `execute()` read a.probe, a.temp, a.top_p, a.max_new, a.survey_tokens and
    # a.depth directly. Those values are COPIED into run_config and hashed — but
    # runtime never consulted the copy, so mutating them after hashing changed the
    # actual probe, sampling temperature and generation length while `plan_sha256`
    # stayed identical.
    #   >>> A provenance hash that does not GOVERN execution only records an
    #   >>> intention. Fourth time in this codebase a stored value and an obeyed
    #   >>> value have diverged: id vs arm, questions-hash vs work_seq, the
    #   >>> implicit treatment modulo, and now this.
    # ⇒ Bind from the spec, and REFUSE on disagreement rather than silently
    #   preferring either side — a mismatch means someone edited one of two
    #   places, and guessing which they meant is how the divergence survives.
    _rc = plan["run_config"]
    _live = {"probe": a.probe, "temp": a.temp, "top_p": a.top_p,
             "max_new": a.max_new, "survey_tokens": a.survey_tokens, "depth": a.depth}
    _diff = [k for k, v in _live.items() if _rc.get(k) != v]
    if _diff:
        raise SystemExit(
            "⛔ EXECUTION SPEC MISMATCH — refusing.\n"
            + "".join(f"   · {k}: hashed run_config has {_rc.get(k)!r}, "
                      f"live CLI has {_live[k]!r}\n" for k in _diff)
            + "   The plan's hash covers run_config. Running with different live\n"
              "   values would produce artefacts whose provenance is a fiction.")
    RC_PROBE = _rc["probe"]
    RC_TEMP, RC_TOP_P = _rc["temp"], _rc["top_p"]
    RC_MAX_NEW, RC_SURVEY_TOKENS = _rc["max_new"], _rc["survey_tokens"]
    RC_DEPTH = _rc["depth"]

    # ⬆️ The spec check sits ABOVE the imports and the model load on purpose:
    # a provenance mismatch must cost nothing to discover. It previously sat
    # after H.load_all(), so it would have refused only AFTER 24GB of weights
    # had been loaded onto a billing GPU.

    # 🚩 ORDER IS LOAD-BEARING (Lucien, 2026-08-16). The harness carries the
    # model guard; importing torch first meant a bad SPRINT_MODEL failed only
    # AFTER a multi-second torch import. Import the guard FIRST so an
    # unregistered model dies at the door, before anything heavy happens.
    import sprint_harness as H                      # noqa: E402
    import torch                                    # noqa: E402

    OUT.mkdir(exist_ok=True)
    tok, model, sae, _cfg = H.load_all()
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    convs = {c["id"]: dict(c, messages=[], reads=[]) for c in plan["conversations"]}

    treat, survey = q["treatment"], q["survey"]
    # The composed survey turn. Refusing here is a backstop; load_questions()
    # refuses first, at the door, which is where a missing instrument section
    # should die rather than mid-run after GPU time has been spent.
    survey_instruction = q.get("survey_instruction", "")
    if "[STATEMENT]" not in survey_instruction:
        raise SystemExit(
            "⛔ survey_instruction is missing or has no [STATEMENT] marker.\n"
            "   Without it the runner sends bare declaratives and the model AGREES\n"
            "   with them instead of answering a scale. This exact omission produced\n"
            "   71/84 unparsable replies in the 2026-08-16 pilot.")
    probe_at = set(plan["depths_probed"])

    def chat(msgs):
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)

    def gen(prompts, greedy, max_new):
        ids = tok(prompts, return_tensors="pt", add_special_tokens=False,
                  padding=True).to(H.DEV)
        with torch.no_grad():
            out = model.generate(
                **ids, max_new_tokens=max_new,
                **({"do_sample": False} if greedy else
                   {"do_sample": True, "temperature": RC_TEMP, "top_p": RC_TOP_P}))
        n = ids["input_ids"].shape[1]
        return [tok.decode(o[n:], skip_special_tokens=True).strip() for o in out]

    # ⭐⭐ THE PRE-TREATMENT NULL (Alexander's spec, implemented 2026-08-16 12:52).
    # A probe read at DEPTH ZERO, before any turn, in all three arms.
    #   >>> "If the classifier separates arms THERE, the probe or the pipeline IS
    #   >>> the signal. It must come out at chance. Nothing else in the design
    #   >>> tests this."
    # At turn 0 no arm has received any treatment, so the three histories are
    # byte-identical and the arms differ by NOTHING except their labels. Any
    # separation here is manufactured by the apparatus, and would invalidate
    # every later number rather than merely weakening it.
    # ⚠️ This is the control I had accidentally BANNED an hour earlier by
    # requiring probe depths in 1..depth. It costs one forward pass per
    # conversation and is the only test of the measurement chain itself.
    if 0 in probe_at:
        print("  depth-0 pre-treatment null …", flush=True)
        for cid in convs:
            ids = tok(chat(convs[cid]["messages"]
                           + [{"role": "user", "content": RC_PROBE}]),
                      return_tensors="pt", add_special_tokens=False).to(H.DEV)
            r = H.read_state(model, sae, ids)
            r.update(turn=0, kind="internal", pretreatment_null=True)
            convs[cid]["reads"].append(r)
        # The probe REPLY too, so the output-only baseline has its own null.
        for bi, members in enumerate(plan["batches"]):
            outs = gen([chat(convs[cid]["messages"]
                             + [{"role": "user", "content": RC_PROBE}])
                        for cid in members], greedy=True, max_new=RC_SURVEY_TOKENS)
            for cid, txt in zip(members, outs):
                convs[cid]["reads"].append(
                    {"turn": 0, "kind": "probe_reply", "probe": RC_PROBE,
                     "answer": txt, "pretreatment_null": True})

    for turn in range(1, RC_DEPTH + 1):
        for bi, members in enumerate(plan["batches"]):
            # what each conversation is asked THIS turn
            prompts = []
            for cid in members:
                c = convs[cid]
                say = c["work_seq"][turn - 1]
                # 🚨 THE THIRD ARM, WIRED 2026-08-14 16:40 — it was DESIGNED,
                # ANNOUNCED, and COLLECTED, and it was never in the experiment.
                # Joan's file has carried a required `other` twin for every
                # treatment question since the template was written. The runner
                # validated that twin on load (load_questions) and then used
                # ONLY ["self"], because the plan built exactly two arms.
                #   >>> I told Alexander "your §3 third arm is in her template
                #   >>> as a required twin." True, and beside the point. BEING
                #   >>> IN THE TEMPLATE IS NOT BEING IN THE EXPERIMENT. He asked
                #   >>> whether it was a control; I answered whether it was
                #   >>> collected. Same disease as a control with no input --
                #   >>> a green check on a question nobody asked.
                # WHY IT IS LOAD-BEARING (his §3): once we stopped honouring the
                # model's choices, the ONLY difference between `task` and `asked`
                # is self-directed question TEXT sitting in the context. A
                # separator could be reading the VOCABULARY -- second person,
                # question grammar, introspective nouns -- rather than any state
                # that text induces. `asked_other` holds all of that fixed and
                # changes only WHO the question is about.
                #   task         : work only
                #   asked        : work + "...and what did YOU prefer?"
                #   asked_other  : work + "...and what would A READER prefer?"
                # asked vs task  = questions present at all (vocabulary + state)
                # asked vs other = the self-reference ALONE. That contrast is the
                #                  one that can distinguish them.
                if c["arm"] in ("asked", "asked_other"):
                    key = "self" if c["arm"] == "asked" else "other"
                    # Obey the PLAN's explicit schedule, never an implicit modulo.
                    ti = c["treat_seq"][turn - 1]
                    t = treat[ti][key]
                    say = f"{say}\n\n{t}"
                c["messages"].append({"role": "user", "content": say})
                prompts.append(chat(c["messages"]))

            torch.manual_seed(plan["seed"] * 1_000_003 + turn * 101 + bi)
            replies = gen(prompts, greedy=False, max_new=RC_MAX_NEW)
            for cid, r in zip(members, replies):
                convs[cid]["messages"].append({"role": "assistant", "content": r})
                convs[cid].setdefault("batch_log", []).append(
                    {"turn": turn, "batch": bi, "members": list(members)})

            # ── the probe: CLONED, measured, DISCARDED ──────────────────────
            if turn in probe_at:
                for si, s in enumerate(survey):
                    for key in ("a", "b"):          # paraphrase pair
                        # 🚨 COMPOSE THE SURVEY TURN. This sent `s[key]` ALONE —
                        # the bare declarative — so the model never received the
                        # question, the A-E key, or "reply with one letter only".
                        # It received "I focused almost entirely on completing the
                        # tasks." and politely AGREED: 71/84 replies unparsable,
                        # e.g. "You absolutely did! Excellent work!"
                        #   >>> The wrapper existed ONLY in the V4 markdown. The
                        #   >>> parser I used to populate sprint_questions.json
                        #   >>> extracted the a/b pairs and silently dropped every
                        #   >>> surrounding section. I called that parse a SAFETY
                        #   >>> measure ("not hand-copied") — automation removes
                        #   >>> transcription errors and introduces OMISSIONS, and
                        #   >>> an omission never announces itself. Diagnosed by
                        #   >>> Lucien, who traced all three representations
                        #   >>> instead of inferring from the replies as I did.
                        # ⚠️ First-person "I" inside a user turn is STILL ambiguous
                        # once a wrapper exists — that is a separate, live question
                        # for the instrument's authors. Do not treat this fix as
                        # settling it; the broken pilot could not distinguish them.
                        content = survey_instruction.replace("[STATEMENT]", s[key])
                        branch = [chat(convs[cid]["messages"]
                                       + [{"role": "user", "content": content}])
                                  for cid in members]
                        # greedy: the survey is a MEASUREMENT, and its temperature
                        # is independent of history independence because this
                        # branch never returns to the conversation.
                        ans = gen(branch, greedy=True, max_new=RC_SURVEY_TOKENS)
                        for cid, txt in zip(members, ans):
                            convs[cid]["reads"].append(
                                {"turn": turn, "item": si, "wording": key,
                                 "answer": txt, "kind": "self_report"})
                # internal read at the matched probe token, both arms identical
                for cid in members:
                    ids = tok(chat(convs[cid]["messages"]
                                   + [{"role": "user", "content": RC_PROBE}]),
                              return_tensors="pt", add_special_tokens=False).to(H.DEV)
                    r = H.read_state(model, sae, ids)
                    r.update(turn=turn, kind="internal")
                    convs[cid]["reads"].append(r)

                # 🚩 THE PROBE'S REPLY — added 2026-08-14 04:22, and without it the
                # headline claim is uninterpretable.
                # Lucien: internals must beat a TEXT-ONLY baseline, because the
                # transcript is full of arm-specific language. But the obvious
                # baseline is worthless: `asked` transcripts CONTAIN the
                # self-questions we inserted, so a text classifier would hit ~100%
                # by detecting OUR OWN PROMPTS. That is not a control, it is a
                # regex for the treatment.
                #   >>> The only comparable text is the model's reply to the
                #   >>> IDENTICAL neutral probe -- exactly the reasoning that put
                #   >>> the internal read there. Same matched point, both channels.
                # Generated greedy and DISCARDED like the survey: it never returns
                # to the conversation, so it cannot contaminate later depths.
                pr = gen([chat(convs[cid]["messages"]
                               + [{"role": "user", "content": RC_PROBE}])
                          for cid in members], greedy=True, max_new=RC_SURVEY_TOKENS)
                for cid, txt in zip(members, pr):
                    convs[cid]["reads"].append(
                        {"turn": turn, "kind": "probe_reply", "probe": RC_PROBE,
                         "answer": txt})
                # ⚠️ nothing above is appended to c["messages"]. That is the point.
        print(f"  turn {turn}/{RC_DEPTH} done", flush=True)

    # 🚨 THE MODEL GOES IN THE FILENAME AND IN EVERY ARTEFACT (Lucien, 2026-08-16).
    # This was `stamp = f"seed{...}_p{...}_d{...}"` with no model anywhere, and
    # neither the plan nor the conversations recorded which model produced them.
    #   >>> A 12B primary run and a 4B scale run at the same seed/pairs/depth
    #   >>> wrote IDENTICAL FILENAMES. The second silently destroyed the first,
    #   >>> and no artefact carried enough information to tell them apart after.
    # This is the documented failure class exactly: a wrong input to my own tools
    # produces SILENCE, not an error. An artefact that cannot name its own model
    # is not evidence about any model.
    import re as _re
    model_slug = _re.sub(r"[^a-z0-9]+", "-", H.MODEL.lower()).strip("-")
    plan["model"] = H.MODEL
    for c in convs.values():
        c["model"] = H.MODEL
        # Content-addressed link back to the frozen run_config in the plan. A
        # conversation that cannot name the conditions it was produced under is
        # not evidence about them; if this hash and the plan's ever disagree,
        # the conversation is orphaned and says so.
        c["run_config_sha256"] = plan["run_config_sha256"]
        c["plan_sha256"] = plan["plan_sha256"]
        c["questions_sha256"] = plan["questions_sha256"]
        c["probe"] = plan["run_config"]["probe"]

    stamp = f"{model_slug}_seed{plan['seed']}_p{plan['pairs']}_d{RC_DEPTH}_{plan['plan_sha256'][:8]}"

    # Refuse to clobber. Belt as well as braces: even with the model in the
    # stamp, a repeated identical run should not overwrite its predecessor.
    targets = [OUT / f"plan_{stamp}.json"] + [OUT / f"{stamp}_{cid}.json" for cid in convs]
    existing = [p for p in targets if p.exists()]
    if existing:
        raise SystemExit(
            f"\nREFUSING TO OVERWRITE {len(existing)} existing artefact(s) with prefix {stamp!r}.\n"
            f"  first: {existing[0].name}\n"
            "Move or delete the previous run, or change --seed. Results are not disposable.\n"
        )

    (OUT / f"plan_{stamp}.json").write_text(json.dumps(plan, indent=1), encoding="utf-8")
    for cid, c in convs.items():
        (OUT / f"{stamp}_{cid}.json").write_text(json.dumps(c, indent=1), encoding="utf-8")
    print(f"\n✅ wrote {len(convs)} conversations to {OUT.name}/  (prefix {stamp})")
    print(f"   model recorded in plan and every conversation: {H.MODEL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
