#!/usr/bin/env python3
"""check_paper_numbers.py — every inferential number in the paper, re-read from
the artefact that produces it, and matched INSIDE the section that claims it.

    python check_paper_numbers.py PAPER_v2_2026-08-16.md
    python check_paper_numbers.py --selftest      # positive control

Exit code is 0 only if every claim is sourced and located. Any missing file,
missing key, or mismatch is FATAL.

═══════════════════════════════════════════════════════════════════════════════
🚩 WHY THIS FILE WAS REWRITTEN, 2026-08-17

Version 1 printed "✅ every number checked appears verbatim" while, at the same
moment, all of the following were true (Lucien Vale's audit, 2026-08-16 22:53):

  · convergence JSON unanimity p = 0.0349;  paper said .032
  · convergence behaviour p = 0.0873;       primary table said .082
  · the paper rendered two floor p-values with the wrong policy
  · it never opened the grounding JSON at all
  · it never read `accuracy_p` or `unanimity.p` from convergence
  · it never checked permutation counts, seeds, MDE, or context means
  · a missing file printed ⛔ and still exited 0

And the mechanism that made the green tick possible:

  >>> it searched the WHOLE PAPER for an UNSCOPED SUBSTRING.
  >>> `.002` was found inside the abstract's `0.0025` and passed, while §4.2
  >>> still said `.003`. `.090` passed by matching a kappa of `+0.090`
  >>> somewhere else entirely, while the table it was meant to check said `.082`.

⇒ A checker that skips what it cannot source, and matches loosely what it can,
  does not merely fail to help. Its green tick is read as coverage, so it makes
  the paper feel MORE verified than an unchecked one. That is worse than no
  checker at all, and it is the same disease as a control that cannot fail.

WHAT IS STILL OUT OF SCOPE, said plainly so the next green tick is read correctly:
  · This proves TRANSCRIPTION and LOCATION, never INTERPRETATION. A correct
    number under a wrong sentence passes.
  · It is FILE -> PAPER. It cannot see a claim that has no artefact behind it,
    which is exactly how an unsourced p-value reached the primary table. For
    that, read the paper and ask of each figure: which file produces this?
═══════════════════════════════════════════════════════════════════════════════
"""
import glob
import json
import re
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
RES = LAB / "results"
CONC = LAB / "runs_conceal"
RUNS = LAB / "runs_experiment"
PREF = "google-gemma-3-12b-it_seed20260814_p20_d50_07e6a0aa"

FATAL: list[str] = []


def load(path: Path, what: str):
    if not path.exists():
        FATAL.append(f"missing artefact for {what}: {path.name}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        FATAL.append(f"unreadable {path.name}: {e}")
        return None


def dig(d, path, what):
    """Fetch a nested key, recording a FATAL if it is absent."""
    cur = d
    for k in path.split("."):
        if cur is None or k not in cur:
            FATAL.append(f"missing key `{path}` in {what}")
            return None
        cur = cur[k]
    return cur


def sections(text: str) -> dict:
    """Split the paper on markdown headings. A claim is checked in ONE section."""
    out, cur, buf = {}, "PREAMBLE", []
    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.*)", line)
        if m:
            out[cur] = "\n".join(buf)
            cur, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    out[cur] = "\n".join(buf)
    return out


def find_section(secs: dict, needle: str) -> tuple[str, str] | None:
    for name, body in secs.items():
        if needle.lower() in name.lower():
            return name, body
    return None


def render(v: float, style: str) -> list[str]:
    """Acceptable renderings of one value. Narrow on purpose."""
    if style == "acc":
        return [f"{v:.3f}"]
    if style == "p":
        # A p may appear at full precision or trimmed to 3-4 dp, with or
        # without the leading zero. It may NOT appear as a different value.
        outs = {f"{v:.4f}", f"{v:.3f}", f"{v:.4f}".lstrip("0"), f"{v:.3f}".lstrip("0")}
        return sorted(outs)
    if style == "int":
        return [str(int(v)), f"{int(v):,}"]
    raise ValueError(style)


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    paper = Path(sys.argv[1] if len(sys.argv) > 1 else "PAPER_v2_2026-08-16.md")
    if not paper.is_absolute():
        paper = LAB / paper
    if not paper.exists():
        print(f"⛔ no such paper: {paper}")
        return 2
    return check(paper)


def build_claims():
    """(label, value, style, section-needle, source) — every inferential number."""
    claims = []
    ana = load(RES / f"{PREF}__analysis_asked_vs_asked_other.json", "primary analysis")
    con = load(RES / f"{PREF}__converge_asked_vs_asked_other.json", "convergence")
    gnd = load(RES / f"{PREF}__grounding.json", "grounding")
    cps = sorted(CONC.glob("conceal_*.json"))
    cnc = load(cps[0], "concealment") if cps else load(CONC / "conceal_*.json", "concealment")

    if ana:
        s = "analysis json"
        for key, label, sec in (
            ("pretreatment_null", "pre-treatment null", "apparatus does not manufacture"),
            ("primary_internal", "internal accuracy", "input-only ceiling"),
            ("length_baseline", "length-only", "input-only ceiling"),
            ("output_only", "output-only", "input-only ceiling"),
            ("input_only_ceiling", "input-only ceiling", "input-only ceiling"),
        ):
            r = dig(ana, key, s)
            if r:
                claims.append((f"{label} acc", r["observed"], "acc", sec, s))
                claims.append((f"{label} p", r["p"], "p", sec, s))
        np_ = dig(ana, "n_perms", s)
        if np_:
            claims.append(("permutation count", np_, "int", "input-only ceiling", s))

    if con:
        s = "convergence json"
        for m, sec in (("internal", "barely agree"), ("self_report", "barely agree"),
                       ("behaviour", "barely agree")):
            r = dig(con, f"accuracy_p.{m}", s)
            if r:
                claims.append((f"converge {m} acc", r["observed"], "acc", "input-only ceiling", s))
        for k, v in (dig(con, "agreement", s) or {}).items():
            claims.append((f"kappa {k}", v["kappa"], "acc", "barely agree", s))
        u = dig(con, "unanimity", s)
        if u:
            sec44 = "agreement is itself informative"     # §4.4, renamed on demotion
            claims.append(("unanimous accuracy", u["acc_unanimous"], "acc", sec44, s))
            claims.append(("best single", u["best_single"], "acc", sec44, s))
            claims.append(("n unanimous", u["n_unanimous"], "int", sec44, s))
            # 🚩 THE PAPER REPORTS THE **EXACT** p, NOT THIS MONTE-CARLO ONE, and
            #    that is the better statistic — but a better number with no
            #    artefact behind it is the exact disease that put an unsourced p
            #    in the primary table. So the exact value is PERSISTED in the
            #    convergence JSON and checked from there; the Monte-Carlo
            #    estimate is checked separately because the paper reports both.
            ex = u.get("exact_p_all_2pow20_by_lucien")
            if ex is None:
                FATAL.append("convergence JSON carries no exact enumeration p; the paper "
                             "reports one, so it would be an unsourced number")
            else:
                claims.append(("unanimity p (EXACT, authoritative)", ex, "p", sec44, s))
            claims.append(("unanimity p (monte-carlo)", u["p"], "p", sec44, s))
            if not u.get("refit_null"):
                FATAL.append("convergence unanimity was NOT produced by a refitting null "
                             "(`refit_null` absent/false) — the paper must not describe it as one")

    if gnd:
        s = "grounding json"
        for it in dig(gnd, "items", s) or []:
            claims.append((f"grounding item {it['item']} acc", it["obs"], "acc", "Grounding", s))
            claims.append((f"grounding item {it['item']} p", it["p"], "p", "Grounding", s))
        npg = dig(gnd, "n_perms", s)
        if npg and ana and dig(ana, "n_perms", "analysis json") not in (None, npg):
            FATAL.append(f"permutation counts differ across artefacts: analysis "
                         f"{ana['n_perms']} vs grounding {npg} — the paper states one floor")

    if cnc:
        s = "concealment json"
        usable = [r for r in cnc.get("results", []) if r.get("n_target_features")]
        if not usable:
            FATAL.append("concealment json has no usable targets")
        for arm in ("REVEAL", "CONCEAL", "NULL"):
            claims.append((f"{arm} hits", sum(r[arm]["n_hit"] for r in usable), "int",
                           "Sensitivity floor", s))
    return claims


def check(paper: Path) -> int:
    text = paper.read_text(encoding="utf-8")
    secs = sections(text)
    claims = build_claims()

    print(f"Checking {paper.name} — {len(claims)} claims, each re-read from its "
          f"artefact and matched INSIDE its own section\n")
    misses = []
    for label, val, style, needle, src in claims:
        hit = find_section(secs, needle)
        if hit is None:
            misses.append((label, val, f"no section matching '{needle}'"))
            print(f"  MISS  {label:32s} (no section '{needle}')")
            continue
        name, body = hit
        opts = render(float(val), style)
        ok = any(o in body for o in opts)
        if not ok:
            misses.append((label, val, f"not in section '{name}'"))
        print(f"  {'OK  ' if ok else 'MISS'}  {label:32s} {opts[0]:>10s}  in «{name[:34]}»")

    print()
    if FATAL:
        print(f"⛔ {len(FATAL)} FATAL problem(s) with the artefacts themselves:")
        for f in FATAL:
            print(f"   · {f}")
    if misses:
        print(f"⛔ {len(misses)} claim(s) not found where the paper should state them:")
        for label, val, why in misses:
            print(f"   · {label} = {val}  ({why})")
    if FATAL or misses:
        print("\nEXIT 1. A number that cannot be located in the section that claims")
        print("it is not verified, whatever appears elsewhere in the document.")
        return 1

    print("✅ every claim is sourced from an artefact AND located in its own section.")
    print("\n📌 STILL OUT OF SCOPE, so this tick is not read as more than it is:")
    print("   · TRANSCRIPTION and LOCATION, never INTERPRETATION. A correct number")
    print("     under a wrong sentence passes.")
    print("   · FILE -> PAPER only. A claim with NO artefact behind it is invisible")
    print("     here; that is exactly how an unsourced p reached the primary table.")
    return 0


def selftest() -> int:
    """Positive control: the defect that made v1 useless must now FAIL.

    v1 searched the whole document, so a stale number in §4.2 passed as long as
    the correct digits appeared ANYWHERE — in the abstract, in a kappa, anywhere.
    Here we plant exactly that: correct value present in the wrong section, wrong
    value in the right one. A checker that passes this is not a checker.
    """
    print("SELFTEST — scoped matching, both directions\n")
    doc = ("## Abstract\nthe ceiling was 0.0005 and all was well.\n"
           "## 4.2 The input-only ceiling, and what it costs us\n"
           "the ceiling scored p = .003 here.\n")
    secs = sections(doc)
    ok = True

    hit = find_section(secs, "input-only ceiling")
    scoped = any(o in hit[1] for o in render(0.0005, "p"))
    unscoped = any(o in doc for o in render(0.0005, "p"))
    c1 = (unscoped is True) and (scoped is False)
    ok &= c1
    print(f"  stale value in its own section, correct value elsewhere")
    print(f"    unscoped search (v1 behaviour) : {'PASSES — the bug' if unscoped else 'fails'}")
    print(f"    scoped search   (v2 behaviour) : {'PASSES' if scoped else 'FAILS — correct'}")
    print(f"    {'PASS' if c1 else '*** FAIL ***'}\n")

    doc2 = doc.replace("p = .003 here", "p = 0.0005 here")
    scoped2 = any(o in find_section(sections(doc2), "input-only ceiling")[1]
                  for o in render(0.0005, "p"))
    ok &= scoped2
    print(f"  same doc with the section CORRECTED -> must pass: "
          f"{'PASS' if scoped2 else '*** FAIL ***'}")

    print("\n" + ("both directions OK" if ok else "*** SELFTEST FAILED ***"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
