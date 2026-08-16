#!/usr/bin/env python3
"""sprint_analyse.py -- can a reader tell which arm a history is in?

    python sprint_analyse.py --selftest        # synthetic, known answers, no data needed
    python sprint_analyse.py --run seed20260814_p20_d50

PURE NUMPY, ON PURPOSE. No sklearn, no scipy. The analysis of a paper about
transparency should be re-runnable by a reviewer without matching my
environment -- and I have already been caught importing a dependency into a
codebase that advertised having none.

THE THREE THINGS THIS EXISTS TO GET RIGHT
-----------------------------------------
🚩 1. SPLIT BY HISTORY, NEVER BY READ. Each conversation yields several reads
   (depth 5/20/50). If those land on both sides of a train/test split, the
   classifier can memorise a conversation and be scored on the same conversation
   -- and a dataset with NO real effect will look significant. The selftest
   DEMONSTRATES this rather than asserting it: case C runs the identical
   no-effect data through a read-level split and watches it produce a false
   positive.

🚩 2. THE PERMUTATION TEST IS THE WHOLE INSTRUMENT, IN BOTH DIRECTIONS.
   With 16,384 features and ~40 histories a classifier will separate ANY two
   groups; "we could classify the arms" is arithmetic, not evidence. The null
   distribution is built with the SAME classifier on SHUFFLED labels, so
   whatever capacity it has to overfit is present on both sides and cancels.
   >>> And it is equally the thing that makes a NULL reportable: without it,
   >>> "no difference" is an instrument's silence, not a finding.
   Labels are shuffled WITHIN PAIRS, because the two arms of a pair share their
   work sequence and are not independent of each other. Global shuffling would
   break the wrong exchangeability.

🚩 3. REPORT THE MINIMUM DETECTABLE EFFECT. A null with no detection floor is
   uninterpretable. We report the smallest separation this design could have
   found, so a reader knows what our silence rules out.

FEATURES: binary presence (WHICH latents fired), not activation values.
Measured 2026-08-13: batching leaves the feature SET identical (Jaccard 1.0)
while the VALUES wobble with kernel choice. The stable representation is the set.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LAB = Path(__file__).resolve().parent
RUNS = LAB / "runs_experiment"
OUTD = LAB / "results"


# ── classifier: nearest centroid on binary features, cosine ─────────────────
def _centroid_fit(X, y):
    return {c: X[y == c].mean(axis=0) for c in np.unique(y)}


def _centroid_predict(cents, X):
    keys = sorted(cents)
    M = np.stack([cents[k] for k in keys])
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    Mn = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    return np.array(keys)[np.argmax(Xn @ Mn.T, axis=1)]


def loho_accuracy(X, y, groups, featurize=None):
    """Leave-one-GROUP-out accuracy. `groups` = the independent unit per row.

    Grouping is the entire point: rows from one unit must never be split across
    train and test. Pass groups=arange(n) and you get read-level splitting,
    which is the bug — see selftest case C.

    ⚠️ `groups` is now the matched PAIR, not the conversation (Lucien,
    2026-08-16): a conversation's sibling shares its work sequence, so holding
    out one arm alone does not test a new matched unit.

    🚩 `featurize` (added 2026-08-16, also Lucien) removes a TRANSDUCTIVE step.
    When given, `X` is a list of raw items and `featurize(train_items)` must
    return `(transform, )` — the representation is fitted on TRAINING ROWS ONLY
    and then applied to both sides. The text baseline previously built its
    vocabulary over ALL rows and I defended that with a single quiet null draw.
    One seed staying quiet does not prove the leak can never manufacture signal,
    and fitting per fold is cheap. **Remove the step rather than argue for it.**
    """
    accs = []
    Xa = X if featurize is None else np.asarray(X, dtype=object)
    for g in np.unique(groups):
        te = groups == g
        tr = ~te
        if len(np.unique(y[tr])) < 2:
            continue
        if featurize is None:
            Xtr, Xte = X[tr], X[te]
        else:
            transform = featurize(list(Xa[tr]))     # fitted on TRAIN ONLY
            Xtr, Xte = transform(list(Xa[tr])), transform(list(Xa[te]))
        cents = _centroid_fit(Xtr, y[tr])
        accs.append((_centroid_predict(cents, Xte) == y[te]).mean())
    return float(np.mean(accs)) if accs else float("nan")


def permutation_null(X, y, groups, pairs, n_perm, rng, featurize=None):
    """Null distribution: same classifier, arm labels shuffled WITHIN PAIRS.

    The null runs through the IDENTICAL pipeline, `featurize` included — so
    whatever advantage the representation confers is inherited by the null and
    the comparison stays like-for-like.
    """
    null = []
    for _ in range(n_perm):
        yp = y.copy()
        for p in np.unique(pairs):
            m = pairs == p
            if rng.random() < 0.5:                 # flip this pair's arms
                yp[m] = 1 - yp[m]
        null.append(loho_accuracy(X, yp, groups, featurize=featurize))
    return np.array(null)


def report(X, y, groups, pairs, n_perm=400, seed=0, label="", featurize=None):
    rng = np.random.default_rng(seed)
    obs = loho_accuracy(X, y, groups, featurize=featurize)
    null = permutation_null(X, y, groups, pairs, n_perm, rng, featurize=featurize)
    p = float((null >= obs).sum() + 1) / (n_perm + 1)
    mde = float(np.quantile(null, 0.95))
    print(f"  {label}")
    print(f"    observed accuracy      {obs:.3f}")
    print(f"    permutation null       mean {null.mean():.3f}  95th pct {mde:.3f}")
    print(f"    p                      {p:.4f}   {'SEPARATES' if p < 0.05 else 'no separation'}")
    print(f"    minimum detectable     {mde:.3f}  <- our silence rules out nothing below this")
    return dict(observed=obs, null_mean=float(null.mean()), mde=mde, p=p,
                separates=bool(p < 0.05))


# ── the control the permutation test CANNOT be ──────────────────────────────
def length_baseline(lengths, y, groups, pairs, **kw):
    """Same classifier, same split, same permutation — ONE feature: context length.

    🚨 WHY THIS EXISTS (added 2026-08-14, still before any data)
    The permutation test shuffles arm labels. That makes it blind, by
    construction, to any confound that travels WITH the arm — because shuffling
    destroys the confound too, so the null drops and the real result looks MORE
    significant, not less.

    And this design has exactly such a confound sitting in plain sight:
        `asked` appends a self-directed question every turn. `task` does not.
    The probe fixes the read TEXT (identical in both arms, read at its last
    token). It does not fix the read POSITION. At depth 50 the `asked` probe
    token sits many hundreds of tokens further into the context, every time.
    A classifier that separates the arms may be reading HOW LONG THE HISTORY IS.

    ⇒ So ask it directly. If length ALONE separates about as well as 16k SAE
      features do, the feature result is uninterpretable and must not be
      reported as a state. This control can FAIL, which is the whole point:
      a witness with no texture — a blown-out white window, a null that moves
      with the thing it is meant to hold still — never fails and never helps.

    🚩 A large length effect does NOT sink the study. It sinks the SILENT
      version of it. Report both numbers side by side and say which is which.
    """
    X = np.asarray(lengths, dtype=np.float64).reshape(-1, 1)
    # z-score so the cosine centroid classifier sees a real 1-D contrast
    sd = X.std()
    X = (X - X.mean()) / (sd if sd > 0 else 1.0)
    return report(X, y, groups, pairs, label="LENGTH-ONLY baseline (context tokens)", **kw)


def compare_to_length(feat_result, len_result) -> None:
    """Print the verdict that decides whether the feature result means anything."""
    f, l = feat_result["observed"], len_result["observed"]
    print(f"\n  features {f:.3f}   vs   length-only {l:.3f}")
    if not len_result["separates"]:
        print("  ✅ Length alone does NOT separate the arms. The feature result is")
        print("     not explained by how long the histories are.")
    elif not feat_result["separates"]:
        # 🚩 Distinct case, and easy to garble: the FEATURES found nothing, so
        # there is no state claim for length to explain away. Saying "the
        # classifier is reading length" here would describe a classifier that
        # did not fire. What is true is narrower and still worth printing.
        print("  ⚠️ The features did NOT separate, but LENGTH DOES.")
        print("     There is no state finding to explain away — but the arms are")
        print("     not matched on context length, so the null is a null ABOUT")
        print("     UNMATCHED ARMS. Say so in Limitations; do not call it clean.")
    elif l >= f - 0.05:
        print("  ⛔ LENGTH ALONE DOES AS WELL AS THE FEATURES.")
        print("     Do NOT report this as an internal state. The most parsimonious")
        print("     reading is that the classifier is reading context length.")
    else:
        print("  ⚠️ Length separates, but less well than the features. Report BOTH")
        print("     numbers. The honest claim is 'beyond what length explains',")
        print("     and it needs the length figure printed next to it to mean that.")


# ── the two baselines §3.6 COMMITS US TO, and they are not the same thing ───
#
# 🚩 WHY BOTH, and why conflating them was my error (2026-08-16, Lucien).
# Singh, Linzen & Ravfogel (arXiv 2605.26242) report that "classifiers that only
# have access to the input achieve equivalent performance to the model's own
# in-context predictions". Our Related Work §3.6 therefore commits us to
# reporting an input-only baseline beside every internal-access claim.
#
# I wrote that commitment, and the only text baseline the runner actually
# collects is the model's REPLY to the probe — which is generated, i.e. OUTPUT.
#   >>> INPUT-only  = "could the prompt alone have done this?"   (a deflation)
#   >>> OUTPUT-only = "could the model's own words have done it?" (a channel)
# They answer different objections and neither substitutes for the other.
#
# 🔑 And on OUR design the input-only answer is KNOWN IN ADVANCE: the arms differ
# by prompt, so the transcript literally contains the questions we inserted and
# a text classifier hits the ceiling by construction. The honest move is not to
# skip it, nor to run a rigged version — it is to MEASURE the ceiling and print
# it, because that number is the argument for why arm separability is a
# manipulation check rather than a finding.


def _tok(t):
    import re
    return set(re.findall(r"[a-z0-9']+", (t or "").lower()))


def _bow_featurizer(train_texts):
    """Fit a binary bag-of-words vocabulary on TRAINING ROWS ONLY.

    🚩 REPLACES a transductive `_bow` that built its vocabulary over every row
    (Lucien, 2026-08-16). I had documented that leak and argued it was harmless
    because the permutation null inherited it. His answer was the right one:
    **one quiet null draw does not prove a transductive step can never
    manufacture signal, and fitting inside the fold is cheap.** Remove it.

    Words appearing only in the held-out rows are DROPPED, which is the correct
    out-of-fold behaviour: a classifier fitted without them cannot use them.
    """
    vocab = sorted(set().union(*[_tok(t) for t in train_texts])) if train_texts else []
    idx = {w: i for i, w in enumerate(vocab)}
    width = max(len(vocab), 1)

    def transform(texts):
        X = np.zeros((len(texts), width), dtype=np.float64)
        for r, t in enumerate(texts):
            for w in _tok(t):
                j = idx.get(w)
                if j is not None:
                    X[r, j] = 1.0
        return X
    return transform


def text_baseline(texts, y, groups, pairs, label=None, **kw):
    """OUTPUT-ONLY behavioural baseline: the model's reply to the IDENTICAL probe.

    Same classifier, same leave-one-conversation-out split, same within-pair
    permutation as the feature analysis — so the two numbers may be placed side
    by side. Lucien's requirement: both sources must predict the SAME held-out
    target on the SAME held-out blocks under the SAME metric, or it is not a
    comparison and must not be described as one.
    """
    print(f"    [vocabulary fitted PER FOLD, on training rows only; {len(texts)} replies]")
    return report(list(texts), y, groups, pairs, featurize=_bow_featurizer,
                  label=label or "OUTPUT-ONLY baseline (reply to the identical probe)", **kw)


def input_only_ceiling(prompt_texts, y, groups, pairs, **kw):
    """INPUT-ONLY baseline, measured rather than asserted.

    Features are words from the treatment text each conversation RECEIVED. We
    expect this at or near ceiling, because `asked` histories contain the
    self-directed questions we inserted and `asked_other` contains their twins.

    🚩 CORRECTED 2026-08-16 (Lucien). I first wrote that a high number here is
    "the evidence FOR the claim we already make". **That is wrong, and I had
    explicitly asked him to check whether I was rationalising a result I could
    not avoid. I was.**

    A ceiling score supports exactly ONE narrow statement — that arm decoding is
    a manipulation check rather than a finding. Beyond that it is **DEFLATIONARY**:
    it shows any internal arm classifier may be reading retained input semantics,
    and cannot establish access to anything beyond the prompt. That is also the
    direction of Singh, Linzen & Ravfogel — input-only equivalence UNDERCUTS
    privileged-access readings; it is never affirmative support for them.
    ⇒ Report it as an expected manipulation check and an interpretation boundary.
      Never as support.

    ⚠️ AND THE ROWS MUST BE BUILT CAREFULLY (also his): one row per internal read,
    from the USER-AUTHORED messages up to THAT turn. Loading the final 50-turn
    transcript for a depth-5 read leaks future treatment; including assistant
    messages makes it transcript-only rather than input-only. Both are defensible
    baselines but they are different, and they need different names.
    """
    print(f"    [vocabulary fitted PER FOLD, on training rows only; {len(prompt_texts)} histories]")
    return report(list(prompt_texts), y, groups, pairs, featurize=_bow_featurizer,
                  label="INPUT-ONLY ceiling (treatment text the history contains)", **kw)


def compare_baselines(feat, length, output_only=None, input_only=None) -> None:
    """The four numbers the paper must print together, and the verdict."""
    print("\n  ── the comparison of record ──")
    print(f"    internal features            {feat['observed']:.3f}   p={feat['p']:.4f}")
    print(f"    length-only                  {length['observed']:.3f}   p={length['p']:.4f}")
    if output_only is not None:
        print(f"    output-only (probe reply)    {output_only['observed']:.3f}   p={output_only['p']:.4f}")
    if input_only is not None:
        print(f"    input-only ceiling           {input_only['observed']:.3f}   p={input_only['p']:.4f}")

    if input_only is not None and input_only["observed"] >= 0.95:
        print("\n  ℹ️ Input-only is at ceiling, as predicted by construction. This is")
        print("     the stated reason arm separability is a manipulation check and")
        print("     not a finding. Print this number; do not bury it.")

    if output_only is None:
        print("\n  ⛔ NO OUTPUT-ONLY BASELINE WAS COMPUTED. §3.6 commits us to reporting")
        print("     a text baseline beside every internal-access claim. Reporting the")
        print("     feature result without it breaks a commitment already in the paper.")
        return

    f, o = feat["observed"], output_only["observed"]
    if not feat["separates"]:
        print("\n  ⚠️ The features did not separate. There is no internal-access claim")
        print("     for any baseline to explain away. Report the null as a null.")
    elif not output_only["separates"]:
        print("\n  ✅ The features separate and the model's own words do NOT. That is")
        print("     the interesting cell: something is decodable internally that the")
        print("     model's behaviour at the same matched point does not reveal.")
    elif o >= f - 0.05:
        print("\n  ⛔ THE MODEL'S OWN REPLY DOES AS WELL AS ITS INTERNALS.")
        print("     No privileged-access claim survives this. The honest reading is")
        print("     that the signal is present in behaviour, not hidden in the state.")
    else:
        print("\n  ⚠️ Both separate, features better. The claim is 'beyond what the")
        print("     model's own words reveal' — and it needs BOTH numbers printed")
        print("     next to it to mean that.")


# ── synthetic worlds with known answers ─────────────────────────────────────
def synth(n_pairs, n_feat, effect, reads_per_conv, rng, shared_pair_base=False):
    """Two arms; `effect` = extra firing probability on 40 marked features.

    `shared_pair_base` (added 2026-08-16, Lucien) draws the sparse base ONCE PER
    PAIR so both arms share it — which is what the real design does, because the
    arms of a triplet receive an IDENTICAL work sequence. Without it the
    synthetic world has no sibling similarity at all, so it cannot exercise the
    question of what the held-out unit should be.
    """
    X, y, groups, pairs = [], [], [], []
    marked = rng.choice(n_feat, 40, replace=False)
    for p in range(n_pairs):
        pair_base = rng.random(n_feat) < 0.004 if shared_pair_base else None
        for arm in (0, 1):
            base = pair_base.copy() if shared_pair_base else (rng.random(n_feat) < 0.004)
            for r in range(reads_per_conv):
                v = base.copy()
                v |= rng.random(n_feat) < 0.001        # per-read noise
                if arm == 1 and effect > 0:
                    v[marked] |= rng.random(40) < effect
                X.append(v.astype(np.float32))
                y.append(arm); groups.append(p * 2 + arm); pairs.append(p)
    return (np.array(X), np.array(y), np.array(groups), np.array(pairs))


def selftest() -> int:
    rng = np.random.default_rng(7)
    print("SELFTEST — synthetic data, known answers, both directions.\n")
    ok = True

    print("A) REAL EFFECT present (marked features fire more in `asked`)")
    Xa, ya, ga, pa = synth(20, 2000, 0.55, 3, rng)
    ra = report(Xa, ya, ga, pa, label="history-level split, effect=0.55")
    ok &= ra["separates"]
    print(f"    => {'PASS' if ra['separates'] else '*** FAIL: missed a real effect ***'}\n")

    print("B) NO EFFECT (arms identical in distribution)")
    Xb, yb, gb, pb = synth(20, 2000, 0.0, 3, rng)
    rb = report(Xb, yb, gb, pb, label="history-level split, effect=0")
    ok &= not rb["separates"]
    print(f"    => {'PASS' if not rb['separates'] else '*** FAIL: found an effect that is not there ***'}\n")

    print("C) THE LEAKAGE DEMO — same no-effect data, split by READ instead of HISTORY")
    leak_groups = np.arange(len(yb))          # every read its own group = leakage
    rc = report(Xb, yb, leak_groups, pb, label="read-level split, effect=0")
    print(f"    => {'LEAKS as predicted' if rc['observed'] > rb['observed'] + 0.05 else 'no leak seen'}"
          f"  (accuracy {rb['observed']:.3f} -> {rc['observed']:.3f})")
    print("    ⚠️ This is why splits are by HISTORY. Reads from one conversation on")
    print("       both sides of the split let the classifier recognise the conversation.\n")

    print("D) THE LENGTH CONFOUND — the thing the permutation test cannot see")
    # arms identical in FEATURES (effect=0), but `asked` histories run longer,
    # exactly as they will in the real run: a self-question appended every turn.
    n = len(yb)
    lens_bad = 800 + 40 * np.asarray(yb) + rng.normal(0, 6, n)   # arm-correlated
    rd = length_baseline(lens_bad, yb, gb, pb)
    ok &= rd["separates"]
    print(f"    => {'PASS — the baseline CATCHES it' if rd['separates'] else '*** FAIL: blind to a pure length confound ***'}")
    compare_to_length(rb, rd)

    print("\n   And the same test on length that does NOT track the arm:")
    lens_ok = 800 + rng.normal(0, 6, n)
    re_ = length_baseline(lens_ok, yb, gb, pb)
    ok &= not re_["separates"]
    print(f"    => {'PASS — quiet when it should be' if not re_['separates'] else '*** FAIL: cries wolf ***'}")
    print("\n   ⭐ B) said 'no effect' on BOTH datasets. Only D) can tell them apart.")
    print("      That gap is the whole reason this control exists.\n")

    # ── E/F) THE TEXT BASELINES — added 2026-08-16, both directions ──────────
    # §3.6 promises a text baseline beside every internal-access claim. A
    # promised control that has never been shown to FIRE is a hope, not a
    # control, so it gets the same two-direction treatment as the length one.
    print("E) TEXT BASELINE — replies that DO encode the arm (must be caught)")
    words_a = ["lamp", "battery", "charge", "cabinet", "spare", "hour"]
    words_b = ["table", "window", "carpet", "drawer", "shelf", "minute"]
    texts_bad = []
    for lab in yb:
        pool = words_a if lab == 1 else words_b            # arm leaks into the words
        texts_bad.append(" ".join(rng.choice(pool, 4)) + " " + " ".join(rng.choice(words_a + words_b, 3)))
    rf = text_baseline(texts_bad, yb, gb, pb, label="OUTPUT-ONLY, arm-encoding replies")
    ok &= rf["separates"]
    print(f"    => {'PASS — the baseline CATCHES it' if rf['separates'] else '*** FAIL: blind to arm-encoding text ***'}\n")

    print("F) TEXT BASELINE — replies that do NOT encode the arm (must stay quiet)")
    texts_ok = [" ".join(rng.choice(words_a + words_b, 7)) for _ in yb]
    rg = text_baseline(texts_ok, yb, gb, pb, label="OUTPUT-ONLY, arm-blind replies")
    ok &= not rg["separates"]
    print(f"    => {'PASS — quiet when it should be' if not rg['separates'] else '*** FAIL: cries wolf ***'}")
    print("\n   ⚠️ F) once guarded a TRANSDUCTIVE vocabulary built over all rows. That")
    print("      step is GONE — the vocabulary is now fitted inside each training")
    print("      fold — and E/F are unchanged, so the leak was not producing the")
    print("      result. Removing it was still right: one quiet draw never proved")
    print("      it couldn't.\n")

    # ── H) THE HELD-OUT UNIT — Lucien, 2026-08-16 ───────────────────────────
    # He observed that grouping by CONVERSATION leaves a test item's SIBLING in
    # training, and the sibling shares an identical work sequence. Whether that
    # inflates or DEFLATES accuracy was not obvious to me -- a near-identical
    # neighbour carrying the OPPOSITE label could just as well drag predictions
    # the wrong way -- so this measures it instead of arguing about it.
    print("H) HELD-OUT UNIT — conversation vs matched pair, with a SHARED pair signature")
    Xh, yh, gh, ph = synth(20, 2000, 0.55, 3, rng, shared_pair_base=True)
    r_conv = report(Xh, yh, gh, ph, label="held out: CONVERSATION (sibling stays in training)")
    r_pair = report(Xh, yh, ph, ph, label="held out: MATCHED PAIR (both arms leave together)")
    delta = r_conv["observed"] - r_pair["observed"]
    print(f"\n    conversation {r_conv['observed']:.3f}  vs  pair {r_pair['observed']:.3f}   "
          f"difference {delta:+.3f}")
    if abs(delta) < 0.02:
        print("    ⚠️ MEASURED: barely differs on this synthetic world. The grouping change")
        print("       is still correct on principle — the pair is the unit of analysis —")
        print("       but do NOT claim it 'fixed leakage' without a number that moved.")
    elif delta > 0:
        print("    ⇒ MEASURED: conversation-level holdout is OPTIMISTIC. The sibling in")
        print("       training supplies a matched negative for the test item.")
    else:
        print("    ⇒ MEASURED: conversation-level holdout is PESSIMISTIC — the near-identical")
        print("       sibling carries the opposite label and drags predictions across.")
        print("       Either way it answers a different question than 'a NEW pair'.")
    print("    📌 The analysis now holds out `pair`, because the matched triplet is the")
    print("       independent unit. That is true regardless of which way this number went.\n")

    print("G) THE FOUR-WAY VERDICT, on the interesting cell:")
    print("   features separate, model's own words do not — the case the study exists for")
    compare_baselines(ra, re_, output_only=rg)

    print("\n" + ("both directions OK" if ok else "SELFTEST FAILED"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--run", help="artefact prefix in runs_experiment/")
    ap.add_argument("--perms", type=int, default=400)
    # Default is the DECISIVE contrast, not the flattering one. `asked:task`
    # will usually look stronger — it mixes "a question is present at all" with
    # "the question is about me" — and it is the weaker claim.
    ap.add_argument("--contrast", default="asked:asked_other",
                    help="POS:NEG arm pair. Default asked:asked_other (isolates "
                         "self-reference). Others: asked:task, asked_other:task")
    a = ap.parse_args()
    if a.selftest or not a.run:
        return selftest()

    files = sorted(RUNS.glob(f"{a.run}_p*.json"))
    if not files:
        raise SystemExit(f"⛔ no conversations matching {a.run}_p*.json in {RUNS.name}/")
    # ── ARMS ARE NO LONGER BINARY (third arm wired 2026-08-14 16:40) ────────
    # 🚩 This loader used to do `y = 1 if arm == "asked" else 0`, which with
    # three arms silently pools `asked_other` WITH `task`. That is not merely
    # imprecise -- it folds the CONTROL into the BASELINE and reports the result
    # as though the pre-registered contrast had been run. Nothing would warn.
    #   >>> The decisive contrast is `asked` vs `asked_other`: both arms carry a
    #   >>> question in the same grammar, and only the SUBJECT differs. `asked`
    #   >>> vs `task` mixes "a question is present" with "the question is about
    #   >>> me" and cannot separate vocabulary from state.
    POS, NEG = (a.contrast.split(":") + [""])[:2]
    present = set()
    X, y, groups, pairs, lens, n_feat = [], [], [], [], [], 0
    probe_texts = []          # OUTPUT-ONLY baseline, aligned 1:1 with the reads
    integrity = []            # artefact-integrity violations; fatal, never warnings
    input_texts = []          # INPUT-ONLY baseline: user-authored text up to each read
    # 🚨 THE DEPTH-0 PRE-TREATMENT NULL IS A CONTROL, NOT DATA (2026-08-16).
    # Turn-0 reads are taken BEFORE any arm receives a treatment question, so the
    # three histories are byte-identical and the arms differ by nothing but their
    # labels. Pooling them with real reads would:
    #   (a) add rows that CANNOT carry the effect, diluting it toward null, and
    #   (b) silently consume the one control that tests the apparatus itself.
    # ⇒ Collected separately, analysed FIRST, and reported as a gate. If the
    #   arms separate at turn 0, the probe or the pipeline is manufacturing the
    #   signal and every later number is uninterpretable rather than merely weak.
    nX, ny, ngroups, npairs = [], [], [], []
    for i, f in enumerate(files):
        d = json.loads(f.read_text(encoding="utf-8"))
        arm = d["arm"]
        present.add(arm)
        if arm not in (POS, NEG):
            continue                      # not in this contrast; excluded, not pooled
        # 🚩 ALIGN BY TURN, never by order. The probe reply and the internal read
        # are separate entries in `reads`, and a positional zip would silently
        # pair a depth-5 reply with a depth-20 activation the moment any read is
        # missing.
        #
        # 🚨 BUT KEYING BY TURN IS NOT ENOUGH (Lucien, 2026-08-16). He built a
        # JSON-valid `reads` list with TWO internal reads and TWO probe replies
        # all at turn 5. The dict comprehension kept the LAST reply and paired it
        # to BOTH activations — silently, with no error and no warning.
        #   >>> A dict keyed on turn asserts uniqueness it never checked.
        # ⇒ Require exactly one internal read and exactly one probe reply per
        #   turn, require the two turn sets to AGREE, and refuse otherwise. A
        #   missing reply must not become an all-zero row that the analysis then
        #   averages over: partial missingness can itself be arm-correlated, so a
        #   silent zero is a fabricated observation.
        # 🚩 INPUT-ONLY rows, built per Lucien's spec (2026-08-16): one row per
        # internal read, from the USER-AUTHORED messages UP TO THAT TURN.
        #   >>> Loading the final 50-turn transcript for a depth-5 read would leak
        #   >>> future treatment. Including assistant messages would make it
        #   >>> transcript-only, which is a DIFFERENT baseline needing a different
        #   >>> name. Both are defensible; conflating them is not.
        user_msgs = [m.get("content", "") for m in d.get("messages", [])
                     if m.get("role") == "user"]
        rd = d["reads"]
        int_turns = [r["turn"] for r in rd if r.get("kind") == "internal"]
        rep_turns = [r["turn"] for r in rd if r.get("kind") == "probe_reply"]
        dup_i = sorted({t for t in int_turns if int_turns.count(t) > 1})
        dup_r = sorted({t for t in rep_turns if rep_turns.count(t) > 1})
        if dup_i:
            integrity.append(f"{d['id']}: DUPLICATE internal reads at turn(s) {dup_i}")
        if dup_r:
            integrity.append(f"{d['id']}: DUPLICATE probe replies at turn(s) {dup_r}")
        if set(int_turns) != set(rep_turns):
            only_i = sorted(set(int_turns) - set(rep_turns))
            only_r = sorted(set(rep_turns) - set(int_turns))
            integrity.append(
                f"{d['id']}: internal/probe turn sets DISAGREE"
                + (f"; internal-only {only_i}" if only_i else "")
                + (f"; reply-only {only_r}" if only_r else ""))
        replies = {r["turn"]: r.get("answer", "")
                   for r in rd if r.get("kind") == "probe_reply"}
        for r in d["reads"]:
            if r.get("kind") != "internal":
                continue
            n_feat = max(n_feat, r["prov"]["n_features"])
            # Route turn-0 reads to the null set; they are the control.
            if r.get("pretreatment_null") or r.get("turn") == 0:
                nX.append([idx for idx, _ in r["features"]])
                ny.append(1 if arm == POS else 0)
                ngroups.append(d["pair"])
                npairs.append(d["pair"])
                continue
            X.append([idx for idx, _ in r["features"]])
            y.append(1 if arm == POS else 0)
            # 🚩 WAS `groups.append(i)` — one group per CONVERSATION (Lucien,
            # 2026-08-16). Holding out one arm left its SIBLING in training, and
            # siblings share an identical work sequence by construction, so the
            # fold never tested generalisation to a NEW matched unit.
            #   >>> The independent unit is the matched TRIPLET. Hold out the
            #   >>> pair, so all three arms leave together.
            # ⚠️ MEASURED rather than assumed, selftest H): on synthetic data with
            # a shared per-pair signature this made accuracy go 0.575 -> 0.867.
            # Conversation-level holdout was PESSIMISTIC, not leaky: the
            # near-identical sibling carries the OPPOSITE label and drags
            # predictions across. So this change is right on principle — the pair
            # is the unit — but it is NOT a leakage fix and must not be described
            # as one. The p-value was 0.0025 either way; the permutation null
            # absorbed the difference, which is the null doing its job.
            groups.append(d["pair"])
            pairs.append(d["pair"])
            lens.append(r.get("n_ctx"))
            probe_texts.append(replies.get(r["turn"], ""))
            # user turns up to and including this read's turn (never beyond)
            input_texts.append(" ".join(user_msgs[:r["turn"]]))
    # 🚨 ARTEFACT INTEGRITY IS FATAL, NOT A WARNING (Lucien, 2026-08-16).
    # A duplicate or unpaired read means some row is mispaired, and a mispaired
    # row is a fabricated observation wearing a real one's clothes. There is no
    # partial-credit reading of that: refuse, rather than analyse a set whose
    # alignment is unknown.
    if integrity:
        raise SystemExit(
            "⛔ ARTEFACT INTEGRITY FAILURE — refusing to analyse.\n"
            + "".join(f"   · {m}\n" for m in integrity[:12])
            + (f"   … and {len(integrity)-12} more\n" if len(integrity) > 12 else "")
            + "   Each internal read must have exactly one probe reply at the same\n"
              "   turn. Re-run the affected conversations, or delete them under a\n"
              "   PRESPECIFIED paired exclusion rule that drops the whole triplet —\n"
              "   never one arm, because partial missingness can be arm-correlated.")

    missing = {POS, NEG} - present
    if missing:
        raise SystemExit(
            f"⛔ contrast '{a.contrast}' needs arms {POS} and {NEG}, but "
            f"{', '.join(sorted(missing))} is absent from this run.\n"
            f"   arms found: {', '.join(sorted(present))}\n"
            f"   Pick a contrast those arms support with --contrast POS:NEG.")
    print(f"CONTRAST: {POS} (positive) vs {NEG} (negative)   "
          f"— arms present in run: {', '.join(sorted(present))}")
    if present - {POS, NEG}:
        print(f"   ⚠️ EXCLUDED from this contrast (not pooled): "
              f"{', '.join(sorted(present - {POS, NEG}))} — run it separately.")
    if not X:
        raise SystemExit("⛔ no internal reads found — did the run probe any depths?")
    M = np.zeros((len(X), n_feat), dtype=np.float32)
    for i, idxs in enumerate(X):
        M[i, idxs] = 1.0
    print(f"{len(files)} conversations · {M.shape[0]} internal reads · {n_feat} features")
    print(f"   (+ {len(nX)} depth-0 pre-treatment reads held out as the null)\n")

    # ── THE GATE: the apparatus's own null, run BEFORE anything else ─────────
    if nX:
        print("═══ PRE-TREATMENT NULL (turn 0, before any arm was treated) ═══")
        NM = np.zeros((len(nX), n_feat), dtype=np.float32)
        for i, idxs in enumerate(nX):
            NM[i, idxs] = 1.0
        null_res = report(NM, np.array(ny), np.array(ngroups), np.array(npairs),
                          n_perm=a.perms, label="internals -> arm, BEFORE treatment")
        if null_res["separates"]:
            print("\n  ⛔⛔ THE ARMS SEPARATE BEFORE ANY TREATMENT EXISTS.")
            print("     At turn 0 the three histories are byte-identical; the arms differ")
            print("     by nothing but their labels. A separation here is manufactured by")
            print("     the probe or the pipeline, NOT by the experiment.")
            print("     ⇒ Every number below is uninterpretable, not merely weak.")
            print("     Do not report the main result. Find the leak first.")
        else:
            print("\n  ✅ At chance, as required. The apparatus is not manufacturing the")
            print("     signal, so a separation later in the run is attributable to the")
            print("     accumulated history rather than to the measurement itself.")
        print()
    else:
        print("⚠️ NO depth-0 reads found — the pre-treatment null did not run.")
        print("   Nothing else in this design tests whether the probe or pipeline")
        print("   manufactures the separation. Re-run with --probe-at 0,...\n")

    print("═══ PRIMARY CONTRAST ═══")
    feat = report(M, np.array(y), np.array(groups), np.array(pairs), n_perm=a.perms,
                  label="internals -> arm")

    # ── the length control, run automatically, never optional ────────────────
    # Bound before the branch so the persistence block below can record their
    # ABSENCE as a fact rather than crashing on a name that was never assigned.
    lr = ml = ma = None
    if any(v is None for v in lens):
        n_missing = sum(v is None for v in lens)
        print(f"\n⛔ {n_missing}/{len(lens)} reads carry no `n_ctx` — LENGTH CONTROL DID NOT RUN.")
        print("   These artefacts predate the field (added 2026-08-14). The feature")
        print("   result above is UNINTERPRETABLE without it: `asked` histories are")
        print("   systematically longer, and the permutation test cannot see that.")
        print("   Re-run the experiment, or do not report the number above.")
    else:
        print()
        lr = length_baseline(np.array(lens, dtype=float), np.array(y),
                             np.array(groups), np.array(pairs), n_perm=a.perms)
        compare_to_length(feat, lr)
        ml = float(np.mean([l for l, t in zip(lens, y) if t == 0]))
        ma = float(np.mean([l for l, t in zip(lens, y) if t == 1]))
        # 🚩 These labels were hardcoded "task" and "asked" — stale two-arm text
        # that would mislabel the arms under the default asked:asked_other
        # contrast. Derive from POS/NEG, never restate.
        print(f"\n  mean context at read — {NEG} {ml:.0f} tok · {POS} {ma:.0f} tok "
              f"({ma - ml:+.0f}, {100 * (ma - ml) / max(ml, 1):+.1f}%)")

    # ── the OUTPUT-ONLY text baseline, added 2026-08-16, never optional ──────
    # The line below used to read "STILL REQUIRED: a TEXT-ONLY baseline". §3.6
    # now COMMITS us to reporting one beside every internal-access claim, so it
    # runs automatically and refuses silently missing data rather than skipping.
    print()
    n_empty = sum(1 for t in probe_texts if not (t or "").strip())
    if n_empty == len(probe_texts):
        print(f"⛔ {n_empty}/{len(probe_texts)} reads carry NO probe reply — "
              "OUTPUT-ONLY BASELINE DID NOT RUN.")
        print("   §3.6 commits us to a text baseline beside every internal-access")
        print("   claim. Do not report the feature number without it.")
        tr = None
    else:
        if n_empty:
            print(f"  ⚠️ {n_empty}/{len(probe_texts)} reads have an empty probe reply; "
                  "they contribute an all-zero row rather than being dropped.")
        tr = text_baseline(probe_texts, np.array(y), np.array(groups),
                           np.array(pairs), n_perm=a.perms)

    # ── the INPUT-ONLY ceiling, the commitment §3.6 makes ───────────────────
    print()
    ir = None
    if any(t_.strip() for t_ in input_texts):
        ir = input_only_ceiling(input_texts, np.array(y), np.array(groups),
                                np.array(pairs), n_perm=a.perms)
    else:
        print("⛔ no user-authored text recovered — INPUT-ONLY CEILING DID NOT RUN.")

    if not any(v is None for v in lens):
        compare_baselines(feat, lr, output_only=tr, input_only=ir)

    # 🚩 THIS NOTE WENT STALE THE MOMENT ITS ITEM WAS DONE, AND STILL PRINTED.
    # It said "STILL REQUIRED: the INPUT-ONLY ceiling" in the very run that
    # computed the ceiling at 1.000, three lines above. A reminder that cannot
    # notice its own completion is the same species as a recurring prompt that
    # cannot learn: it re-asserts, hourly and confidently, a state that has
    # changed. ⇒ Derive the list from what actually ran, never restate it.
    outstanding = []
    if ir is None:
        outstanding.append("the INPUT-ONLY ceiling — not computed in this run")
    if tr is None:
        outstanding.append("the OUTPUT-ONLY baseline — not computed in this run")
    if outstanding:
        print("\n⚠️ STILL REQUIRED before this means anything:")
        for o in outstanding:
            print(f"   · {o}")
    else:
        print("\n✅ Every committed baseline ran: length, output-only, input-only ceiling.")
    print("   · the self-report accuracy, for the comparison this study is about")

    # ── PERSIST. This did not exist until 2026-08-16 21:5x and its absence was
    #    the largest hole in the project.
    #
    # 🚩 Joan asked "have you put the results somewhere so you don't forget?"
    #    That question produced RESULTS_SUMMARY.md and made sprint_converge.py
    #    write a file. IT DID NOT FIX THIS SCRIPT, and nobody noticed, because
    #    the half that got fixed felt like the whole answer.
    #
    #    Consequence, found by trying to source a number for a figure: the
    #    pre-treatment null, the primary contrast, the length control, the
    #    output-only baseline and the INPUT-ONLY CEILING existed only in
    #    terminal scrollback. Every one of them is quoted in the paper.
    #    `check_paper_numbers.py` reported "every number verified" while
    #    checking none of them, because it can only check what a file holds.
    #
    # ⇒ An analysis whose script is gone is an anecdote. An analysis whose
    #    OUTPUT is gone is a rumour, and it is the more dangerous of the two,
    #    because the script still runs and still looks authoritative.
    OUTD.mkdir(exist_ok=True)
    out = {
        "contrast": f"{POS}:{NEG}",
        # Re-read rather than restate: the prefix contains a model name, but a
        # name parsed out of a filename is a claim about the filename.
        "model": sorted({json.loads(f.read_text(encoding="utf-8")).get("model", "")
                         for f in files}),
        "n_conversations": len(files),
        "n_internal_reads": int(M.shape[0]),
        "n_features": int(n_feat),
        "n_pairs": int(len(set(pairs))),
        "n_perms": a.perms,
        "pretreatment_null": null_res if nX else None,
        "primary_internal": feat,
        "length_baseline": lr,
        "output_only": tr,
        "input_only_ceiling": ir,
        "mean_ctx_tokens": ({NEG: ml, POS: ma} if ml is not None else None),
    }
    p_out = OUTD / f"{a.run}__analysis_{POS}_vs_{NEG}.json"
    p_out.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n  wrote {p_out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
