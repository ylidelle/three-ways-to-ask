#!/usr/bin/env python3
"""conceal_ci.py — exact binomial intervals for the calibration counts.

    python conceal_ci.py

🚩 WHY. Alexander Bennett's criticism of the κ statistic — *"you have written an
entire paper whose thesis is 'a single method cannot supply its own error bar,'
and the statistic carrying that thesis is printed bare"* — applies verbatim one
section along. §4.5 reports **7/8, 4/8 and 0/8** with no uncertainty at all, and
those counts carry the sensitivity-floor argument.

Eight targets is a very small denominator. Saying so with an interval is more
honest than saying it in prose, and it changes what the section can claim:

  · **4/8** is not "half the time". It is compatible with anything from about a
    sixth to five sixths.
  · **0/8** does not establish a clean control. It bounds the false-positive
    rate loosely, and that bound is the honest version of "silent".

Clopper–Pearson is used rather than a normal approximation, which is invalid at
these counts (it gives a zero-width interval at 0/8). Implemented by bisection on
the exact binomial tail so the script has no dependencies beyond the standard
library — scipy is not installed here, and adding a dependency to compute five
intervals would be its own small dishonesty about what the repo needs.
"""
import json
import math
from pathlib import Path

LAB = Path(__file__).resolve().parent
CONC = LAB / "runs_conceal"
OUTD = LAB / "results"


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p**i * (1 - p)**(n - i) for i in range(k + 1))


def _bisect(f, increasing, lo=0.0, hi=1.0, iters=200):
    """Root of a monotone f on [lo, hi]."""
    for _ in range(iters):
        mid = (lo + hi) / 2
        if (f(mid) < 0) == increasing:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial interval.

    🚩 THE FIRST VERSION OF THIS RETURNED [1.000, 0.000] — a lower bound above the
    upper — because one bisection branch moved the wrong endpoint. It was caught
    by reading the printed numbers, not by any check, which is precisely the
    fragile way to catch things. Hence `--selftest` below, against published
    values.

    Lower bound: the p at which P(X >= k) = alpha/2, increasing in p.
    Upper bound: the p at which P(X <= k) = alpha/2, decreasing in p.
    """
    low = 0.0 if k == 0 else _bisect(
        lambda p: (1 - binom_cdf(k - 1, n, p)) - alpha / 2, increasing=True)
    high = 1.0 if k == n else _bisect(
        lambda p: binom_cdf(k, n, p) - alpha / 2, increasing=False)
    return low, high


def selftest() -> int:
    """Against published Clopper-Pearson values, and the sanity the first
    version violated: lower <= point estimate <= upper, always."""
    print("SELFTEST — exact binomial intervals\n")
    KNOWN = [(0, 8, 0.0000, 0.3694), (8, 8, 0.6306, 1.0000),
             (4, 8, 0.1570, 0.8430), (7, 8, 0.4735, 0.9968),
             (0, 10, 0.0000, 0.3085), (5, 10, 0.1871, 0.8129)]
    ok = True
    for k, n, elo, ehi in KNOWN:
        lo, hi = clopper_pearson(k, n)
        good = abs(lo - elo) < 5e-4 and abs(hi - ehi) < 5e-4
        ok &= good
        print(f"  {'PASS' if good else '*** FAIL ***'}  {k}/{n}: "
              f"[{lo:.4f}, {hi:.4f}]  expected [{elo:.4f}, {ehi:.4f}]")
    print()
    for k, n in [(0, 8), (1, 8), (4, 8), (7, 8), (8, 8), (3, 20)]:
        lo, hi = clopper_pearson(k, n)
        good = lo <= k / n <= hi and lo <= hi
        ok &= good
        print(f"  {'PASS' if good else '*** FAIL ***'}  {k}/{n}: "
              f"lo {lo:.3f} <= point {k/n:.3f} <= hi {hi:.3f}")
    print("\n" + ("intervals are correct and ordered" if ok
                  else "*** SELFTEST FAILED ***"))
    return 0 if ok else 1


def main() -> int:
    import sys
    if "--selftest" in sys.argv:
        return selftest()
    cps = sorted(CONC.glob("conceal_*.json"))
    if not cps:
        raise SystemExit("⛔ no runs_conceal/conceal_*.json")
    conc = json.loads(cps[0].read_text(encoding="utf-8"))
    usable = [r for r in conc["results"] if r.get("n_target_features")]
    n = len(usable)

    out = {"source": cps[0].name, "n_targets": n, "method": "Clopper-Pearson exact",
           "alpha": 0.05, "arms": {}}
    print(f"{cps[0].name} · {n} usable targets\n")
    print(f"  {'arm':10s} {'fired':>7s}  {'rate':>6s}   95% exact interval")
    for arm in ("REVEAL", "CONCEAL", "NULL"):
        k = sum(1 for r in usable if r[arm]["n_hit"] > 0)
        lo, hi = clopper_pearson(k, n)
        out["arms"][arm] = {"fired": k, "n": n, "rate": k / n,
                            "ci_lo": lo, "ci_hi": hi}
        print(f"  {arm:10s} {k:>3d}/{n:<3d}  {k/n:>6.3f}   [{lo:.3f}, {hi:.3f}]")

    OUTD.mkdir(exist_ok=True)
    p = OUTD / "conceal_intervals.json"
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n  wrote {p.name}")
    print("\n  ⚠️ With n = 8 these intervals are wide by construction. That width")
    print("     IS the result: the calibration establishes that the floor exists")
    print("     and is low, not where exactly it sits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
