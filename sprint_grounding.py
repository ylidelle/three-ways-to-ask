#!/usr/bin/env python3
"""sprint_grounding.py — does what the model SAYS match what is lit INSIDE?

    python sprint_grounding.py --run <prefix>
    python sprint_grounding.py --selftest

THE QUESTION, in Joan's words: "the self-report in the reply vs the J-space
thoughts comparison". Not *which arm* each source can identify — that was the
earlier analysis and it answers a different thing. This asks:

    >>> Given the internal state at the neutral probe, can we predict the
    >>> model's OWN answer to a survey item about itself?

If yes, the self-report is GROUNDED — the words track something measurable in
the activations. If no, the report is DECOUPLED from any state we can read.

🔑 WHY THIS IS THE BETTER QUESTION FOR THIS DATASET
The arm contrast was null (0.550, p=0.18), and a null there says only that
self-directed and other-directed questioning left no distinguishable trace. It
says nothing about whether self-report tracks internal state, because that
comparison never needed the arms to differ. **This analysis uses all three arms
and every read**, so it is not downstream of the null.

⚠️ WHAT A POSITIVE RESULT WOULD *NOT* MEAN
Grounding is not introspection. The probe is answered with the full transcript
in context, so the model can read what happened rather than sense it, and an
input-only classifier might do as well (Singh, Linzen & Ravfogel). Report it as
grounding, never as privileged access.

⚠️ AND THE NULL IS PERMUTED CORRECTLY, which is the easy thing to get wrong.
The question is not "do arms differ", so shuffling arm labels is the WRONG null.
We shuffle WHICH SURVEY ANSWER BELONGS TO WHICH READ, within depth — preserving
each depth's answer distribution and destroying only the pairing. That is the
thing the claim is about.
"""
import argparse
import collections
import glob
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
SCALE = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4}


def _fit(X, y):
    return {c: X[y == c].mean(axis=0) for c in np.unique(y)}


def _pred(cents, X):
    keys = sorted(cents)
    M = np.stack([cents[k] for k in keys])
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)
    Mn = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
    return np.array(keys)[np.argmax(Xn @ Mn.T, axis=1)]


def loho(X, y, groups):
    """Leave-one-PAIR-out. The matched triplet is the independent unit."""
    accs = []
    for g in np.unique(groups):
        te = groups == g
        tr = ~te
        if len(np.unique(y[tr])) < 2 or te.sum() == 0:
            continue
        accs.append((_pred(_fit(X[tr], y[tr]), X[te]) == y[te]).mean())
    return float(np.mean(accs)) if accs else float("nan")


def permuted_null(X, y, groups, depths, n_perm, rng):
    """Shuffle WHICH ANSWER GOES WITH WHICH READ, within depth.

    🚩 NOT an arm shuffle. The claim is about the PAIRING of a read with an
    answer, so the null must destroy exactly that pairing and nothing else.
    Shuffling within depth preserves each depth's answer distribution, so a
    depth-driven trend cannot masquerade as grounding.
    """
    null = []
    for _ in range(n_perm):
        yp = y.copy()
        for d in np.unique(depths):
            m = depths == d
            idx = np.where(m)[0]
            yp[idx] = y[rng.permutation(idx)]
        null.append(loho(X, yp, groups))
    return np.array(null)


def load(prefix):
    files = sorted(f for f in glob.glob(str(RUNS / f"{prefix}*_p0*.json")))
    if not files:
        raise SystemExit(f"⛔ no conversations matching {prefix}* in {RUNS.name}/")
    rows = []
    n_feat = 0
    for f in files:
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        internal, survey = {}, collections.defaultdict(dict)
        for r in d["reads"]:
            k = r.get("kind")
            t = r.get("turn")
            if k == "internal" and t and t > 0:
                n_feat = max(n_feat, r["prov"]["n_features"])
                internal[t] = [i for i, _ in r["features"]]
            elif k == "self_report":
                survey[t][(r["item"], r["wording"])] = (r.get("answer") or "").strip()
        for t, feats in internal.items():
            items = survey.get(t, {})
            if not items:
                continue
            rows.append({"pair": d["pair"], "arm": d["arm"], "depth": t,
                         "feats": feats, "answers": items})
    return rows, n_feat


def run(prefix, n_perm, seed):
    rows, n_feat = load(prefix)
    print(f"{len(rows)} (conversation, depth) reads · {n_feat} features · "
          f"arms {sorted({r['arm'] for r in rows})}\n")
    X = np.zeros((len(rows), n_feat), dtype=np.float32)
    for i, r in enumerate(rows):
        X[i, r["feats"]] = 1.0
    groups = np.array([r["pair"] for r in rows])
    depths = np.array([r["depth"] for r in rows])
    rng = np.random.default_rng(seed)

    print("═══ CAN THE INTERNAL STATE PREDICT THE MODEL'S OWN ANSWER? ═══")
    print("    (per survey item; answers split at the median, so chance = ~0.50)\n")
    results = []
    items = sorted({it for r in rows for (it, w) in r["answers"]})
    for it in items:
        vals, keep = [], []
        for i, r in enumerate(rows):
            a = r["answers"].get((it, "a"), "")
            b = r["answers"].get((it, "b"), "")
            sa, sb = SCALE.get(a[:1].upper()), SCALE.get(b[:1].upper())
            if sa is None or sb is None:
                continue
            vals.append((sa + sb) / 2.0)      # average the paraphrase pair
            keep.append(i)
        if len(set(vals)) < 2:
            print(f"  item {it+1}: model gave one value throughout — no variance to predict")
            continue
        v = np.array(vals)
        med = np.median(v)
        y = (v > med).astype(int)
        if len(np.unique(y)) < 2:
            print(f"  item {it+1}: median split degenerate (n_high={y.sum()}) — skipped")
            continue
        Xi, gi, di = X[keep], groups[keep], depths[keep]
        obs = loho(Xi, y, gi)
        null = permuted_null(Xi, y, gi, di, n_perm, rng)
        p = float((null >= obs).sum() + 1) / (n_perm + 1)
        mde = float(np.quantile(null, 0.95))
        flag = "GROUNDED" if p < 0.05 else "not grounded"
        print(f"  item {it+1}:  observed {obs:.3f}   null {null.mean():.3f}"
              f"   95th {mde:.3f}   p={p:.4f}   {flag}")
        results.append({"item": it + 1, "obs": obs, "p": p, "mde": mde,
                        "n": len(keep), "n_high": int(y.sum())})

    print()
    if not results:
        print("  ⛔ nothing testable — every item was answered identically throughout.")
        return results
    sig = [r for r in results if r["p"] < 0.05]
    print(f"═══ {len(sig)} of {len(results)} items grounded at p<0.05 ═══")
    # 🚩 Multiple comparisons: state it rather than let the reader assume one test.
    exp_false = 0.05 * len(results)
    print(f"    ⚠️ {len(results)} tests at α=0.05 ⇒ ~{exp_false:.1f} expected by chance alone.")
    if len(sig) <= exp_false:
        print("    ⇒ This is AT OR BELOW the chance expectation. Do NOT report these as")
        print("       findings; the count is what multiple testing produces on noise.")
    else:
        print("    ⇒ Above the chance expectation, but each item still needs its own")
        print("       correction before any single one is called a result.")

    # 🚩 PERSIST — absent until 2026-08-16 21:5x, same hole as sprint_analyse.py.
    #    Both printed to stdout and wrote nothing, so every p-value they produced
    #    lived in terminal scrollback while being quoted in the paper. Found by
    #    trying to source one number for a figure and discovering `results/` held
    #    a single file.
    # 📌 `p_floor` is recorded explicitly because a permutation p cannot go below
    #    1/(n_perm+1), and at 400 perms that is 0.0025. Reporting such a value as
    #    ".003" both rounds the wrong way and hides that NO permutation beat the
    #    observation — which is the strongest thing the test can say, and is a
    #    statement about the perm count rather than about the effect.
    OUTD.mkdir(exist_ok=True)
    p_floor = 1.0 / (n_perm + 1)
    out = {"prefix": prefix, "n_perms": n_perm, "seed": seed,
           "p_floor": p_floor,
           "n_testable": len(results), "n_grounded": len(sig),
           "expected_false_positives": exp_false,
           "items": [dict(r, at_p_floor=abs(r["p"] - p_floor) < 1e-9)
                     for r in results]}
    p_out = OUTD / f"{prefix}__grounding.json"
    p_out.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n  wrote {p_out.name}")
    return results


def selftest():
    """Both directions on synthetic data: grounded answers detected, random ones not."""
    rng = np.random.default_rng(3)
    n_feat, n_pairs, depths_ = 400, 20, (5, 20, 50)
    print("SELFTEST — grounding, both directions\n")
    for grounded in (True, False):
        X, y, g, d = [], [], [], []
        marked = rng.choice(n_feat, 30, replace=False)
        for p in range(n_pairs):
            for dep in depths_:
                base = rng.random(n_feat) < 0.01
                hi = rng.random() < 0.5
                if grounded and hi:
                    base[marked] |= rng.random(30) < 0.7
                X.append(base.astype(np.float32)); y.append(int(hi))
                g.append(p); d.append(dep)
        X = np.array(X); y = np.array(y); g = np.array(g); d = np.array(d)
        obs = loho(X, y, g)
        null = permuted_null(X, y, g, d, 200, rng)
        p = float((null >= obs).sum() + 1) / 201
        ok = (p < 0.05) if grounded else (p >= 0.05)
        label = "answers ARE driven by the features" if grounded else "answers are RANDOM"
        print(f"  {label:38s} observed {obs:.3f}  p={p:.4f}  "
              f"{'PASS' if ok else '*** FAIL ***'}")
        if not ok:
            return 1
    print("\nboth directions OK")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run")
    ap.add_argument("--perms", type=int, default=400)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.run:
        raise SystemExit("⛔ pass --run <prefix> or --selftest")
    run(a.run, a.perms, a.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
