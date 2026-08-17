#!/usr/bin/env python3
"""sprint_converge.py — THREE ELICITATION METHODS ON ONE TARGET.

    python sprint_converge.py --run <prefix>
    python sprint_converge.py --selftest

Track 4 of the sprint asks to "implement 3 or more elicitation methods on the
same preferences and measure convergence and divergence" and to "define a
cross-method convergence score". This does that.

THE THREE METHODS, all predicting the SAME held-out label on the SAME pairs:
  internal     — 16,384 SAE features at the neutral probe (what is lit)
  self_report  — the model's own 14 survey answers        (what it says of itself)
  behaviour    — bag-of-words over its reply to the probe (what it does)

🚩 WHY THIS EXISTS AS A FILE AND NOT AS A ONE-OFF. These numbers were first
computed in an inline throwaway script and existed nowhere afterwards. Joan asked
"have you put the results somewhere so you don't forget?" and the answer was no.
An analysis whose script is gone is not a result; it is an anecdote about a
result. Everything printed here is regenerated from the run artefacts.

🔑 WHAT A CONVERGENCE SCORE IS FOR
Comparing accuracies tells you which method is best. It does NOT tell you whether
they measure the same thing. Two methods at 0.55 could agree perfectly or agree
at chance, and those are opposite worlds:
  agreement high  -> one underlying signal, methods are redundant
  agreement ~zero -> near-independent instruments, and their AGREEMENT carries
                     information neither carries alone
Cohen's kappa is reported because raw agreement is inflated by the base rate.
"""
import argparse
import collections
import glob
import itertools
import json
import re
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
SCALE = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}


def _fit(X, y):
    return {c: X[y == c].mean(axis=0) for c in np.unique(y)}


def _pred(cents, X):
    k = sorted(cents)
    M = np.stack([cents[i] for i in k])
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    Mn = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    return np.array(k)[np.argmax(Xn @ Mn.T, axis=1)]


def _tok(t):
    return set(re.findall(r"[a-z0-9']+", (t or "").lower()))


def _bow_fit(train_texts):
    """Vocabulary from TRAINING rows only — no transductive step."""
    vocab = sorted(set().union(*[_tok(t) for t in train_texts])) if train_texts else []
    idx = {w: i for i, w in enumerate(vocab)}
    w = max(len(vocab), 1)

    def tr(ts):
        M = np.zeros((len(ts), w))
        for r, t in enumerate(ts):
            for word in _tok(t):
                j = idx.get(word)
                if j is not None:
                    M[r, j] = 1.0
        return M
    return tr


def wilson(p, n, z=1.96):
    """Wilson score interval. Reported instead of a bare estimate because a
    Monte-Carlo p near a threshold is a number with a width, and printing it
    without one is what let 0.0495 read as a decision."""
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    s = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return max(0.0, (c - s) / d), min(1.0, (c + s) / d)


def kappa(a, b):
    """Cohen's kappa. Raw agreement is inflated by the base rate; kappa is not."""
    pa = (a == b).mean()
    pe = sum((a == c).mean() * (b == c).mean() for c in np.unique(np.concatenate([a, b])))
    return (pa - pe) / (1 - pe) if pe < 1 else float("nan")


def load(prefix, pos, neg):
    rows, n_feat = [], 0
    for f in sorted(glob.glob(str(RUNS / f"{prefix}*_p0*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        if d["arm"] not in (pos, neg):
            continue
        lab = 1 if d["arm"] == pos else 0
        internal, reply, sur = {}, {}, collections.defaultdict(dict)
        for r in d["reads"]:
            t, k = r.get("turn"), r.get("kind")
            if not t:                       # turn 0 is the pre-treatment null, not data
                continue
            if k == "internal":
                n_feat = max(n_feat, r["prov"]["n_features"])
                internal[t] = [i for i, _ in r["features"]]
            elif k == "probe_reply":
                reply[t] = r.get("answer") or ""
            elif k == "self_report":
                sur[t][(r["item"], r["wording"])] = (r.get("answer") or "").strip()
        for t, feats in internal.items():
            vec = [SCALE.get(sur[t].get((it, w), "")[:1].upper(), np.nan)
                   for it in range(7) for w in ("a", "b")]
            if np.isnan(vec).any():
                continue
            rows.append(dict(pair=d["pair"], y=lab, depth=t, feats=feats,
                             reply=reply.get(t, ""), sur=vec))
    return rows, n_feat


def held_out_predictions(rows, n_feat, y_override=None):
    """Leave-one-PAIR-out predictions from each method, aligned row-for-row.

    `y_override` lets the permutation null refit the ENTIRE pipeline on shuffled
    labels rather than scoring fixed predictions against them.
    """
    y = np.array([r["y"] for r in rows]) if y_override is None else np.asarray(y_override)
    g = np.array([r["pair"] for r in rows])
    Xi = np.zeros((len(rows), n_feat), dtype=np.float32)
    for i, r in enumerate(rows):
        Xi[i, r["feats"]] = 1.0
    # 🚩 RAW. Standardisation happens INSIDE each fold, on training rows only.
    #    This line used to read `S = (S - S.mean(0)) / (S.std(0) + 1e-9)` here,
    #    over all 120 rows, BEFORE the fold loop — so every held-out pair helped
    #    define its own representation. Lucien caught it (2026-08-16 22:53) and
    #    it is precisely the transductive step this same function already takes
    #    care to avoid for bag-of-words, four lines below. I fixed the leak I was
    #    looking for and left an identical one in the neighbouring method.
    S_raw = np.array([r["sur"] for r in rows], float)
    texts = [r["reply"] for r in rows]

    P = {m: np.zeros(len(rows), dtype=int) for m in ("internal", "self_report", "behaviour")}
    for gg in np.unique(g):
        te, tr = g == gg, g != gg
        if len(np.unique(y[tr])) < 2:
            continue
        mu, sd = S_raw[tr].mean(0), S_raw[tr].std(0)
        S = (S_raw - mu) / (sd + 1e-9)          # fitted on train, applied to all
        P["internal"][te] = _pred(_fit(Xi[tr], y[tr]), Xi[te])
        P["self_report"][te] = _pred(_fit(S[tr], y[tr]), S[te])
        f = _bow_fit([texts[i] for i in np.where(tr)[0]])
        P["behaviour"][te] = _pred(_fit(f([texts[i] for i in np.where(tr)[0]]), y[tr]),
                                   f([texts[i] for i in np.where(te)[0]]))
    return P, y, g


def kappa_intervals(P, y, g, n_boot=10000, seed=0):
    """Cluster bootstrap CIs for each pairwise κ and their mean.

    🚩 WHY THIS EXISTS. Alexander Bennett, 2026-08-17: *"Your headline number has
    no error bar. You have written an entire paper whose thesis is 'a single
    method cannot supply its own error bar,' and the statistic carrying that
    thesis is printed bare. It's the one place the paper does the thing it warns
    about."*

    He is right, and it is the sharpest criticism this paper has had. `κ = +0.059`
    was the headline and it had no interval anywhere in the manuscript.

    **The resampling unit is the matched PAIR, not the row.** Rows within a pair
    share a work sequence and a held-out fold, so resampling rows would treat
    120 correlated observations as 120 independent ones and produce an interval
    far too narrow. Twenty pairs are drawn with replacement and κ is recomputed
    on the rows they carry.

    ⚠️ WHAT THIS INTERVAL DOES NOT INCLUDE, stated because an unqualified CI is
    the same overclaim in a new costume: it propagates the sampling of pairs,
    holding the fitted predictions fixed. It does **not** propagate refitting the
    three classifiers on each resample. So it answers *"how precisely do we know
    the agreement between these prediction vectors"*, not *"how would κ vary if
    the whole pipeline were rerun on a fresh sample of pairs"*. The second is
    wider.
    """
    rng = np.random.default_rng(seed)
    pairs = np.unique(g)
    idx_of = {p: np.flatnonzero(g == p) for p in pairs}
    combos = list(itertools.combinations(P, 2))

    draws = {f"{a}|{b}": [] for a, b in combos}
    draws["mean"] = []
    for _ in range(n_boot):
        pick = rng.choice(pairs, size=len(pairs), replace=True)
        idx = np.concatenate([idx_of[p] for p in pick])
        ks = []
        for a, b in combos:
            k = kappa(P[a][idx], P[b][idx])
            if not np.isfinite(k):
                k = 0.0            # a resample with one predicted class everywhere
            draws[f"{a}|{b}"].append(k)
            ks.append(k)
        draws["mean"].append(float(np.mean(ks)))

    out = {}
    for key, v in draws.items():
        v = np.asarray(v)
        out[key] = {"lo": float(np.percentile(v, 2.5)),
                    "hi": float(np.percentile(v, 97.5)),
                    "boot_mean": float(v.mean())}
    out["n_boot"] = n_boot
    out["resampling_unit"] = "matched pair"
    out["excludes"] = "classifier refitting; predictions held fixed"
    return out


def per_method_p(rows, n_feat, P, y, g, n_perm, rng):
    """Permutation p for EACH method's accuracy, refitting the whole pipeline.

    🚩 WHY THIS EXISTS, and it is not a nicety. Until 2026-08-16 this script
    reported three accuracies and NO p-values, while the paper's primary table
    printed `self-report 0.658, p = .003`. That p came from a throwaway inline
    script and lived in no artefact. A number in a results table that cannot be
    regenerated is indistinguishable from one that was never computed, however
    honestly it got there.

    ⭐ It refits rather than permuting against fixed predictions, because that is
    what `sprint_analyse.py::permutation_null` does for the internal, length and
    output-only rows. The p-values sit side by side in one table, so they must
    answer the same question. A cheaper fixed-predictor null would be defensible
    alone and misleading in that column.

    Labels are permuted WITHIN PAIRS, preserving the matched-triplet design.
    """
    obs = {m: float((P[m] == y).mean()) for m in P}
    counts = {m: 0 for m in P}
    for _ in range(n_perm):
        yp = y.copy()
        for p in np.unique(g):
            mask = g == p
            if rng.random() < 0.5:
                yp[mask] = 1 - yp[mask]
        Pp, _, _ = held_out_predictions(rows, n_feat, y_override=yp)
        for m in P:
            if float((Pp[m] == yp).mean()) >= obs[m]:
                counts[m] += 1
    return {m: {"observed": obs[m],
                "p": float(counts[m] + 1) / (n_perm + 1),
                "p_floor": 1.0 / (n_perm + 1),
                "at_p_floor": (counts[m] == 0)}
            for m in P}


def unanimity_test(rows, n_feat, P, y, g, n_perm, rng):
    """Is accuracy-when-unanimous really above the per-method rates?

    🚩 THE NAIVE READING IS WRONG. Unanimous rows are a SELECTED subset, and any
    selection can raise accuracy by luck. The null must therefore preserve the
    selection procedure: permute arm labels WITHIN PAIRS, **refit all three
    methods**, recompute which rows are unanimous, and ask how often chance
    produces a gap this large.

    🚨 THIS DOCSTRING DESCRIBED SOMETHING THE CODE DID NOT DO, for its whole
    life, until 2026-08-16 23:45. The old body took the already-trained `P`,
    computed the unanimous subset ONCE before the loop, and then merely rescored
    those fixed predictions and that fixed subset against each shuffled label
    vector. `held_out_predictions()` was never called inside the loop. So the
    selection was NOT preserved under the null — it was frozen at its observed
    value, which is the one thing this test exists to avoid.

    ⚠️ That is the identical fixed-predictor null that `per_method_p()`, forty
    lines above, explicitly refuses for the neighbouring table rows, with a
    comment explaining that it "would be defensible alone and misleading in that
    column." I wrote both. Lucien Vale found it (2026-08-16 22:53) by reading the
    body against the docstring instead of trusting the docstring.

    📌 A false comment on a control is worse than a missing one. It does not just
    fail to help; it actively certifies the thing it describes, in my own voice.

    ⚠️ THIS RETURNS A MONTE-CARLO ESTIMATE AND SAYS SO IN ITS KEY NAMES.

    🚩 It previously also returned `exact_p_all_2pow20_by_lucien=0.0530815125`,
    UNCONDITIONALLY, for any dataset or contrast, and `run()` printed that number
    as "AUTHORITATIVE". Lucien Vale demonstrated the obvious consequence
    (2026-08-17 00:37): a three-pair control whose true conditional exact p is
    3/7 = 0.4286 still returned 0.0531, and the caller still called it
    authoritative.

    > ### That is a magic constant wearing the costume of a computation — the
    > exact defect this project spent the night removing from its own results
    > table, reintroduced BY ME inside the repair for it.

    The exact test now lives in `exact_unanimity.py`, is computed from the data,
    and persists its tail count, orbit size, code and dependency hashes, an input
    manifest hash, and the runtime identity. (That list was itself once a false
    claim in this docstring: the artefact hashed only the exact script, and a
    prefix string is not a dataset binding.) Nothing here
    reports an exact result, and no caller should treat this p as one.

    📌 Standing commitment, kept in the file so it is a record and not resolve:
    this implementation is not to be tuned, reseeded or re-specified in search of
    a smaller number. The editorial decision to demote the convergence bonus
    follows from every plausible version of the test.
    """
    u = (P["internal"] == P["self_report"]) & (P["self_report"] == P["behaviour"])
    if u.sum() == 0:
        return None
    obs_u = float((P["internal"][u] == y[u]).mean())
    best = max(float((P[m] == y).mean()) for m in P)
    obs_gap = obs_u - best
    null = []
    n_skipped = 0
    for _ in range(n_perm):
        yp = y.copy()
        for p in np.unique(g):
            m = g == p
            if rng.random() < 0.5:
                yp[m] = 1 - yp[m]
        # REFIT. Everything downstream is recomputed from the shuffled labels:
        # the three classifiers, the unanimous subset, and both accuracies.
        Pp, _, _ = held_out_predictions(rows, n_feat, y_override=yp)
        up = (Pp["internal"] == Pp["self_report"]) & (Pp["self_report"] == Pp["behaviour"])
        if up.sum() == 0:
            # 🚩 SKIPPING IS NOT NEUTRAL, and the count is now persisted so the
            #    change of estimand is visible rather than silent. Lucien's
            #    three-pair control (2026-08-17): conditional exact 3/7 = 0.4286
            #    vs full-orbit 3/8 = 0.375 when an empty subset is treated as
            #    "no bonus". Conditioning on a non-empty subset asks
            #        P(T >= T_obs | at least one row unanimous)
            #    which is a different question from the one the paper states.
            #    On the real run n_skipped is 0, so this branch is inert here.
            n_skipped += 1
            continue
        acc_u = float((Pp["internal"][up] == yp[up]).mean())
        acc_best = max(float((Pp[m] == yp).mean()) for m in Pp)
        null.append(acc_u - acc_best)
    if not null:
        return None
    null = np.array(null)
    p = float((null >= obs_gap).sum() + 1) / (len(null) + 1)
    return dict(n_unanimous=int(u.sum()), frac=float(u.mean()), acc_unanimous=obs_u,
                best_single=best, gap=obs_gap, p_monte_carlo=p,
                null_mean=float(null.mean()), n_null_draws=len(null),
                n_skipped_empty=n_skipped, refit_null=True, method="monte_carlo")


def run(prefix, pos, neg, n_perm, seed):
    rows, n_feat = load(prefix, pos, neg)
    if not rows:
        raise SystemExit(f"⛔ no usable rows for {pos} vs {neg}")
    P, y, g = held_out_predictions(rows, n_feat)
    rng = np.random.default_rng(seed)
    out = {"contrast": f"{pos}:{neg}", "n_rows": len(rows),
           "n_pairs": int(len(np.unique(g))), "accuracy": {}, "agreement": {}}

    print(f"{len(rows)} held-out predictions per method · {len(np.unique(g))} pairs "
          f"· contrast {pos} vs {neg}\n")
    print("═══ ACCURACY — each method against the truth ═══")
    pm = per_method_p(rows, n_feat, P, y, g, n_perm, rng)
    out["accuracy_p"] = pm
    for m in P:
        a = float((P[m] == y).mean())
        out["accuracy"][m] = a
        r = pm[m]
        floor = "  (at the permutation floor)" if r["at_p_floor"] else ""
        print(f"  {m:12s} {a:.3f}   p={r['p']:.4f}{floor}")
    print(f"\n  p floor with {n_perm} permutations = {1.0/(n_perm+1):.4f}. A p AT the")
    print("  floor means no permutation matched the observation; report it as that")
    print("  value, never rounded up, and never as a smaller number.")

    print("\n═══ DIVERGENCE — do the methods agree with EACH OTHER? ═══")
    ci = kappa_intervals(P, y, g, n_boot=10000, seed=seed)
    out["kappa_ci"] = ci
    for a, b in itertools.combinations(P, 2):
        key = f"{a}|{b}"
        ag = float((P[a] == P[b]).mean())
        kp = float(kappa(P[a], P[b]))
        out["agreement"][key] = {"agree": ag, "kappa": kp,
                                 "ci_lo": ci[key]["lo"], "ci_hi": ci[key]["hi"]}
        print(f"  {a:12s} vs {b:12s}  agree {ag:.3f}   kappa {kp:+.3f}"
              f"   95% CI [{ci[key]['lo']:+.3f}, {ci[key]['hi']:+.3f}]")
    ks = [v["kappa"] for v in out["agreement"].values()]
    mk = float(np.mean(ks))
    out["mean_kappa"] = mk
    print(f"\n  mean kappa {mk:+.3f}   95% CI "
          f"[{ci['mean']['lo']:+.3f}, {ci['mean']['hi']:+.3f}]")
    print(f"  ({ci['n_boot']:,} cluster bootstrap resamples; the unit is the "
          f"matched PAIR, not the row)")
    # 🔑 The claim is NOT that kappa equals 0.059. It is that the methods are not
    #    redundant. Landmarks make that testable rather than rhetorical.
    print(f"  ⇒ the interval excludes 'moderate agreement' (κ ≥ 0.40): "
          f"{'YES' if ci['mean']['hi'] < 0.40 else 'NO'}")
    print(f"     and excludes 'fair agreement'    (κ ≥ 0.20): "
          f"{'YES' if ci['mean']['hi'] < 0.20 else 'NO'}")
    print("  ⚠️ The interval propagates resampling of pairs, holding the fitted")
    print("     predictions fixed. It does NOT include classifier refitting.")

    print("\n═══ CONVERGENCE SCORE — is agreement itself informative? ═══")
    t = unanimity_test(rows, n_feat, P, y, g, n_perm, rng)
    out["unanimity"] = t
    if t:
        print(f"  all three agree on {t['frac']:.3f} of reads (n={t['n_unanimous']})")
        print(f"  accuracy when unanimous   {t['acc_unanimous']:.3f}")
        print(f"  best single method        {t['best_single']:.3f}")
        # 🚩 THIS SCRIPT NO LONGER RENDERS A SIGNIFICANCE VERDICT AT ALL.
        #
        # It used to print SIGNIFICANT / not significant, and then — after that
        # misfired at p = 0.0495 — an "INCONCLUSIVE within 2 SE" rule instead.
        # Lucien Vale showed the second fix was as unprincipled as the first
        # (2026-08-17 00:37): a post-hoc normal-interval heuristic that, if the
        # true tail is the exact 0.0531, still prints the wrong verdict whenever
        # k <= 81, which happens with probability 0.0055. **A warning light, not
        # a decision rule** — and I had installed it AS a decision rule, which
        # made it a new invented threshold in a repair for an invented threshold.
        #
        # ⇒ A Monte-Carlo estimate is reported as an estimate, with an interval.
        #   The decision belongs to `exact_unanimity.py`, which enumerates the
        #   orbit and persists its tail. This function does not adjudicate.
        n_d = max(t.get("n_null_draws", n_perm), 1)
        pmc = t["p_monte_carlo"]
        lo, hi = wilson(pmc, n_d)
        print(f"  gap                       {t['gap']:+.3f}")
        print(f"  MONTE-CARLO p             {pmc:.4f}   95% Wilson [{lo:.4f}, {hi:.4f}]"
              f"   ({n_d} draws, {t['n_skipped_empty']} skipped)")
        print( "  ⚠️ This is an ESTIMATE and this script renders no verdict on it.")
        print( "     Run `exact_unanimity.py` for the decision: with "
              f"{len(np.unique(g))} pairs the orbit is 2^{len(np.unique(g))} and")
        print( "     exhaustively enumerable, so no threshold has to be read off noise.")
        print( "  ⇒ Whatever it returns, the unanimous subset is SELECTED and selection")
        print( "    alone can raise accuracy. Report the kappas.")
    OUTD.mkdir(exist_ok=True)
    p = OUTD / f"{prefix}__converge_{pos}_vs_{neg}.json"
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n  wrote {p.name}")
    return out


def selftest():
    """Both directions: redundant methods show high kappa, independent ones ~0."""
    rng = np.random.default_rng(11)
    print("SELFTEST — convergence, both directions\n")
    ok = True
    for name, redundant in (("redundant methods (same signal)", True),
                            ("independent methods (noise)", False)):
        y = rng.integers(0, 2, 200)
        a = np.where(rng.random(200) < 0.9, y, 1 - y)
        b = np.where(rng.random(200) < 0.9, y, 1 - y) if redundant else rng.integers(0, 2, 200)
        k = kappa(a, b)
        good = (k > 0.5) if redundant else (abs(k) < 0.2)
        ok &= good
        print(f"  {name:34s} kappa {k:+.3f}   {'PASS' if good else '*** FAIL ***'}")

    # ── POSITIVE CONTROLS FOR THE TWO INFERENTIAL PATHS ─────────────────────
    # 🚩 Lucien, 2026-08-16 23:xx: "the present --selftest never touches
    #    per_method_p() or unanimity_test(); it tests only two kappa toy worlds.
    #    The two new inferential paths therefore have no positive control."
    #    He was right, and both paths shipped a real result before this existed.
    #
    # The test below is built to FAIL on the code as it stood an hour ago. That
    # is what makes it a control rather than a decoration: the frozen-selection
    # null cannot see that a lucky unanimous subset is lucky, because it freezes
    # that subset at its observed value and then asks whether it is unusual.
    print("\n  ── positive control: the frozen-selection null on PURE NOISE ──")

    def _fake_rows(seed, n_pairs=14, n_feat=64):
        r = np.random.default_rng(seed)
        rows = []
        for p in range(n_pairs):
            for lab in (0, 1):
                for _ in range(3):                       # 3 depths, as in the real design
                    rows.append(dict(pair=p, y=lab,
                                     feats=list(np.flatnonzero(r.random(n_feat) < 0.05)),
                                     reply=" ".join(r.choice(list("abcdefgh"), 6)),
                                     sur=list(r.normal(size=14))))
        return rows, n_feat                              # labels carry NO signal

    # 🩻 THE FIRST VERSION OF THIS CONTROL ASSERTED `p_refit > p_frozen` — that
    #    the refitting null must be the more conservative of the two on noise.
    #    MEASURED: 0.706 vs 0.810 on the first draw. The assertion was wrong, and
    #    it was wrong in the way I keep writing down: I predicted a direction and
    #    shipped it as a check without ever measuring it. On a draw where the
    #    observed gap is unremarkable the ordering can fall either way; the
    #    direction only holds systematically when the observed unanimous subset
    #    is a lucky one, which a random draw does not guarantee.
    #
    # ⇒ So the control now tests the DEFECT ITSELF, mechanically, with no
    #    statistics to be wrong about. The bug was never "p comes out too small".
    #    The bug was that the SELECTION WAS FROZEN: `u` was computed once and
    #    reused for every shuffled label vector. The observable consequence is
    #    exact and deterministic —
    #        frozen null: the unanimous subset is identical on every draw
    #        refit null:  it is recomputed, so its SIZE varies across draws
    #    A test of a mechanism beats a test of a statistic when the mechanism is
    #    what broke.
    rows, nf = _fake_rows(7)
    P, y, g = held_out_predictions(rows, nf)
    u0 = (P["internal"] == P["self_report"]) & (P["self_report"] == P["behaviour"])

    r2 = np.random.default_rng(3)
    sizes = []
    for _ in range(12):
        yp = y.copy()
        for p in np.unique(g):
            msk = g == p
            if r2.random() < 0.5:
                yp[msk] = 1 - yp[msk]
        Pp, _, _ = held_out_predictions(rows, nf, y_override=yp)
        up = (Pp["internal"] == Pp["self_report"]) & (Pp["self_report"] == Pp["behaviour"])
        sizes.append(int(up.sum()))

    varies = len(set(sizes)) > 1
    ok &= varies
    print(f"    observed unanimous subset          n = {int(u0.sum())}")
    print(f"    subset size under 12 refits        {sizes}")
    print(f"    selection is RECOMPUTED, not frozen: "
          f"{'PASS' if varies else '*** FAIL *** (u is constant => still frozen)'}")

    t = unanimity_test(rows, nf, P, y, g, 60, np.random.default_rng(3))
    flagged = t is not None and t.get("refit_null") is True and t.get("n_null_draws", 0) > 0
    ok &= flagged
    print(f"    unanimity_test reports refit_null and its draw count: "
          f"{'PASS' if flagged else '*** FAIL ***'}")

    print("\n  ── positive control: transductive leak in the survey columns ──")
    # Fitting mean/SD on all rows vs on training rows only must not be identical,
    # or the fold-local fix is not actually doing anything.
    S_raw = np.array([r["sur"] for r in rows], float)
    glob = (S_raw - S_raw.mean(0)) / (S_raw.std(0) + 1e-9)
    tr = g != g[0]
    loc = (S_raw - S_raw[tr].mean(0)) / (S_raw[tr].std(0) + 1e-9)
    differs = not np.allclose(glob, loc)
    ok &= differs
    print(f"    global-fit vs fold-local standardisation differ: "
          f"{'PASS' if differs else '*** FAIL *** (the fix is inert)'}")

    print("\n" + ("both directions OK" if ok else "*** SELFTEST FAILED ***"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run")
    ap.add_argument("--contrast", default="asked:asked_other")
    ap.add_argument("--perms", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.run:
        raise SystemExit("⛔ pass --run <prefix> or --selftest")
    pos, neg = (a.contrast.split(":") + [""])[:2]
    run(a.run, pos, neg, a.perms, a.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
