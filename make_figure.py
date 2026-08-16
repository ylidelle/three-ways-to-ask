#!/usr/bin/env python3
"""make_figure.py — Figure 1 for the paper.

Three panels, one story:
  A  three elicitation methods on the SAME held-out target, against chance
  B  how much they agree with EACH OTHER (Cohen's kappa, ~0 = independent)
  C  the sensitivity calibration: what the instrument can see at all

🚩 EVERY NUMBER IS READ FROM A RESULTS FILE, never typed in. A figure with
hardcoded numbers is a fifth authoritative representation, and this project has
already been bitten four times by a stored value diverging from an obeyed one.
If a results file is missing, this refuses rather than drawing something plausible.

⚠️ Legibility is a submission requirement ("Ensure text in figures is legible!"),
so: large fonts, no colour-only encoding, values printed on the marks.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LAB = Path(__file__).resolve().parent
RES = LAB / "results"
CONC = LAB / "runs_conceal"
PREF = "google-gemma-3-12b-it_seed20260814_p20_d50_07e6a0aa"

conv_p = RES / f"{PREF}__converge_asked_vs_asked_other.json"
if not conv_p.exists():
    sys.exit(f"⛔ missing {conv_p.name} — run sprint_converge.py first. "
             "Refusing to draw numbers I cannot source.")
conv = json.loads(conv_p.read_text(encoding="utf-8"))

cps = sorted(CONC.glob("conceal_*.json"))
if not cps:
    sys.exit("⛔ missing runs_conceal/conceal_*.json — run sprint_conceal.py first.")
conc = json.loads(cps[0].read_text(encoding="utf-8"))

# 🚩 THE INPUT-ONLY CEILING BELONGS IN PANEL A, and until 2026-08-16 it was
# absent from the figure entirely. Panel A read "only self-report separates
# (p=.003)", which invites exactly the introspection reading the ceiling rules
# out: the arms differ BY PROMPT, so a classifier over the prompt text alone
# scores 1.000 and every accuracy in this panel is a manipulation check.
# Drawing 0.658 next to 1.000 makes that visible without a caption.
ana_p = RES / f"{PREF}__analysis_asked_vs_asked_other.json"
if not ana_p.exists():
    sys.exit(f"⛔ missing {ana_p.name} — run sprint_analyse.py first.\n"
             "   Refusing to draw the ceiling from a number typed by hand: this "
             "figure's rule is that every value is read from a results file.")
ana = json.loads(ana_p.read_text(encoding="utf-8"))
if not ana.get("input_only_ceiling"):
    sys.exit("⛔ the analysis file carries no input-only ceiling. Re-run with the "
             "baseline enabled; the panel is dishonest without it.")

plt.rcParams.update({"font.size": 12, "axes.titlesize": 13, "axes.labelsize": 12})
fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))

# ── A: accuracy of each method ───────────────────────────────────────────────
acc = conv["accuracy"]
names = ["internal", "self_report", "behaviour"]
labels = ["internal\nactivations", "self-report\nsurvey", "probe-reply\nbehaviour"]
vals = [acc[n] for n in names]
ceil = float(ana["input_only_ceiling"]["observed"])
labels = labels + ["input-only\nCEILING"]
vals = vals + [ceil]
bars = ax[0].bar(labels, vals,
                 color=["#8c8c8c", "#2b6cb0", "#8c8c8c", "#c53030"],
                 edgecolor="black")
ax[0].axhline(0.5, ls="--", c="black", lw=1.2)
ax[0].text(3.45, 0.515, "chance", ha="right", fontsize=10)
ax[0].axhline(ceil, ls=":", c="#c53030", lw=1.4)
for b, v in zip(bars, vals):
    ax[0].text(b.get_x() + b.get_width() / 2, v + 0.015, f"{v:.3f}",
               ha="center", fontweight="bold")
ax[0].set_ylim(0.4, 1.16)
ax[0].set_ylabel("leave-one-pair-out accuracy")
ax[0].set_title("A  Three methods, same target\n"
                "all far below what the PROMPT ALONE gives")

# ── B: agreement between methods ─────────────────────────────────────────────
ag = conv["agreement"]
pretty = {"internal|self_report": "internal\nvs self-report",
          "internal|behaviour": "internal\nvs behaviour",
          "self_report|behaviour": "self-report\nvs behaviour"}
ks = [(pretty.get(k, k), v["kappa"]) for k, v in ag.items()]
b2 = ax[1].bar([k for k, _ in ks], [v for _, v in ks],
               color="#b7791f", edgecolor="black")
ax[1].axhline(0, c="black", lw=1.2)
for b, (_, v) in zip(b2, ks):
    ax[1].text(b.get_x() + b.get_width() / 2, v + 0.012, f"{v:+.3f}",
               ha="center", fontweight="bold")
ax[1].set_ylim(-0.05, 0.55)
ax[1].set_ylabel("Cohen's κ")
ax[1].axhspan(-0.05, 0.20, color="#eeeeee", zorder=0)
ax[1].text(2.45, 0.23, "κ > 0.2 would mean\nredundant methods",
           ha="right", fontsize=10)
ax[1].set_title("B  They barely agree with each other\nnear-independent instruments")

# ── C: the calibration ───────────────────────────────────────────────────────
usable = [r for r in conc["results"] if r.get("n_target_features")]
arms = ["REVEAL", "CONCEAL", "NULL"]
fired = [sum(1 for r in usable if r[a]["n_hit"] > 0) for a in arms]
hits = [sum(r[a]["n_hit"] for r in usable) for a in arms]
b3 = ax[2].bar(arms, fired, color=["#2f855a", "#2b6cb0", "#c53030"], edgecolor="black")
for b, f, h in zip(b3, fired, hits):
    ax[2].text(b.get_x() + b.get_width() / 2, f + 0.12,
               f"{f}/{len(usable)}\n({h} hits)", ha="center", fontweight="bold", fontsize=11)
ax[2].set_ylim(0, 9.6)
ax[2].set_ylabel(f"targets detected (of {len(usable)})")
ax[2].set_title("C  Calibration: a withheld concept\nNULL silent — the floor is real but low")

for a in ax:
    a.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
out = LAB / "figure1.png"
fig.savefig(out, dpi=200, bbox_inches="tight")
print(f"wrote {out.name}")
print(f"  A accuracies      {dict(zip(names + ['input_only'], [round(v,3) for v in vals]))}")
print(f"  B kappas          {[(k, round(v,3)) for k, v in ks]}")
print(f"  C fired / hits    {dict(zip(arms, list(zip(fired, hits))))}")
