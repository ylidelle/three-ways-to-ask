#!/usr/bin/env python3
"""check_paper_numbers.py — every inferential number in the paper, re-read from
the artefact that produces it, and located at ONE anchored position.

    python check_paper_numbers.py PAPER_v2_2026-08-16.md
    python check_paper_numbers.py --selftest

Exit 0 only if every claim is sourced, located, and numerically equal. Missing
files, missing keys, malformed artefacts, and zero constructed claims are FATAL.

═══════════════════════════════════════════════════════════════════════════════
🚩 TWO PREVIOUS VERSIONS OF THIS FILE CERTIFIED FALSE PAPERS.

**v1** searched the whole document for an unscoped substring, so `.002` was found
inside the abstract's `0.0025` while §4.2 still said `.003`.

**v2** added section scoping and still passed all four of Lucien Vale's mutation
controls (2026-08-17 01:23):

  1. all three kappas and their mean flipped positive -> negative
  2. every §4.2 floor value 0.0005 -> 0.9999
  3. every §4.2 table value wrong, with correct digits parked in a sentence
     labelled "Discarded stale values" elsewhere in the same section
  4. 0.1924->0.1929, 0.0905->0.0909, n=38->338, hits 15->150 and 4->40

The causes, all mine: raw substring matching ignores signs and numeric
boundaries, so `0.036` is found inside `-0.036`; accepted three-decimal strings
are prefixes of wrong four-decimal values, so `.192` matches `0.1929`; `38`
matches `338`; and section scope is not row scope, so a correct number anywhere
in the section passes. "Fatal on missing keys" was also false — with the
artefacts replaced by valid `{}` files, truthiness guards silently constructed
three claims and returned green. **An artefact could delete its own claims.**

> ### A checker that certifies a wrong paper is worse than no checker, because its
> green tick is read as coverage. That is the same disease as a control that
> cannot fail, and this file has now had it twice.

**v3 (this one)** locates each claim at exactly one anchored position, extracts
exactly one numeric token there, and compares numerically with a required sign
and precision. Zero or multiple matches are failures, not passes.

⚠️ STILL OUT OF SCOPE, so the tick is not read as more than it is: this proves
TRANSCRIPTION and LOCATION, never INTERPRETATION. A correct number under a wrong
sentence passes. And it is FILE -> PAPER: a claim with no artefact behind it is
invisible here, which is exactly how an unsourced p-value once reached the
primary table.
═══════════════════════════════════════════════════════════════════════════════
"""
import json
import re
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
RES = LAB / "results"
CONC = LAB / "runs_conceal"
PREF = "google-gemma-3-12b-it_seed20260814_p20_d50_07e6a0aa"

# 🚩 A WHOLE-CELL GRAMMAR, not a scanner that finds digits inside anything.
#    Lucien Vale, 2026-08-17 03:08, defeated the scanning version four ways:
#      · `−0.036` with U+2212 MINUS read as positive 0.036 (regex knew only ASCII)
#      · `0.1924%` certified a value 100x smaller, because `%` was ignored
#      · `\|` escaped pipes split as real delimiters, so raw columns != rendered
#      · an HTML-comment decoy row became the unique raw match
#    The first two are the same disease: extracting digits OUT of a cell instead
#    of requiring the cell to BE a number. The whole cell must now match.
CELL_NUM = re.compile(r"^[-+−]?\d+(?:,\d{3})*(?:\.\d+)?$")
UNICODE_MINUS = "−"
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)


def strip_nonprose(text: str) -> str:
    """Remove HTML comments and fenced code before any parsing.

    A comment is invisible to a reader and visible to a naive parser, which is
    exactly the gap a decoy row lives in."""
    text = HTML_COMMENT.sub("", text)
    out, fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if not fence:
            out.append(line)
    return "\n".join(out)


def split_row(line: str) -> list:
    """Markdown cells, respecting backslash-escaped pipes as literal content."""
    parts, buf, i = [], [], 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            buf.append("|"); i += 2; continue
        if c == "|":
            parts.append("".join(buf)); buf = []; i += 1; continue
        buf.append(c); i += 1
    parts.append("".join(buf))
    return [p.strip() for p in parts]


class Fail(Exception):
    pass


# ── artefact access, strict ──────────────────────────────────────────────────
def load(path: Path, what: str, errs: list):
    if not path.exists():
        errs.append(f"MISSING ARTEFACT for {what}: {path.name}")
        return None
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        errs.append(f"UNREADABLE {path.name}: {e}")
        return None
    if not isinstance(d, dict) or not d:
        errs.append(f"EMPTY/MALFORMED {path.name}: an artefact may not delete its own claims")
        return None
    return d


def dig(d, path: str, what: str, errs: list):
    cur = d
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            errs.append(f"MISSING KEY `{path}` in {what}")
            return None
        cur = cur[key]
    if cur is None:
        errs.append(f"NULL VALUE at `{path}` in {what}")
    return cur


# ── locating a claim at exactly one position ─────────────────────────────────
def sections(text: str) -> dict:
    out, cur, buf = {}, "PREAMBLE", []
    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.*)", line)
        if m:
            out.setdefault(cur, []).extend(buf)
            cur, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    out.setdefault(cur, []).extend(buf)
    return out


def find_section(secs: dict, needle: str):
    hits = [(n, b) for n, b in secs.items() if needle.lower() in n.lower()]
    if len(hits) != 1:
        raise Fail(f"section matching '{needle}': found {len(hits)}, need exactly 1")
    return hits[0]


def cell(secs, section, row_label, col):
    """The `col`-th cell of the unique table row whose first cell names `row_label`.

    The cell must BE a number after markdown emphasis is stripped: no units, no
    suffixes, no prose around it. Zero or several matching rows is a failure, and
    so is a cell that merely contains a number.
    """
    _, body = find_section(secs, section)
    rows = [l for l in body if l.strip().startswith("|")]
    hit = []
    for line in rows:
        cells = split_row(line.strip().strip("|"))
        if cells and row_label.lower() in cells[0].lower():
            hit.append(cells)
    if len(hit) != 1:
        raise Fail(f"table row '{row_label}' in «{section}»: found {len(hit)}, need 1")
    cells = hit[0]
    if col >= len(cells):
        raise Fail(f"row '{row_label}' has {len(cells)} cells, wanted column {col}")
    raw = cells[col].replace("*", "").replace("`", "").replace("~", "").strip()
    if not CELL_NUM.fullmatch(raw):
        raise Fail(f"cell '{row_label}'[{col}] is not a bare number: {cells[col]!r} "
                   "(units, suffixes and surrounding prose are rejected)")
    return raw.replace(UNICODE_MINUS, "-")


def anchored(secs, section, pattern):
    """The single capture group of a regex that must match exactly once."""
    _, body = find_section(secs, section)
    text = "\n".join(body)
    ms = re.findall(pattern, text)
    if len(ms) != 1:
        raise Fail(f"anchor /{pattern}/ in «{section}»: matched {len(ms)}, need 1")
    return ms[0]


def same(tok: str, val: float, min_dp: int) -> bool:
    """Numeric equality at the precision the PAPER itself displays.

    🚩 NOT a chosen tolerance. Lucien Vale's warning was explicit: "do not choose
    a tolerance by looking for a preferred p-value." So the comparison uses the
    token's OWN decimal count — the paper declares its precision by how it writes
    the number — and the artefact is rounded to that, with `min_dp` as a floor so
    a vague `0.19` cannot stand in for `0.1924`. Sign is significant: `-0.036`
    and `+0.036` differ at every precision.
    """
    t = tok.replace(",", "")
    try:
        got = float(t)
    except ValueError:
        return False
    dp = len(t.split(".")[1]) if "." in t else 0
    if dp < min_dp:
        return False                      # too few digits to be a real claim
    return f"{got:.{dp}f}" == f"{float(val):.{dp}f}"


# ── the manifest ─────────────────────────────────────────────────────────────
def build(errs):
    """(id, value, dp, locator) — every inferential number, one anchored site."""
    C = []
    ana = load(RES / f"{PREF}__analysis_asked_vs_asked_other.json", "primary analysis", errs)
    con = load(RES / f"{PREF}__converge_asked_vs_asked_other.json", "convergence", errs)
    gnd = load(RES / f"{PREF}__grounding.json", "grounding", errs)
    exa = load(RES / f"{PREF}__exact_unanimity_asked_vs_asked_other.json", "exact test", errs)
    cps = sorted(CONC.glob("conceal_*.json"))
    cnc = load(cps[0], "concealment", errs) if cps else load(CONC / "conceal.json",
                                                             "concealment", errs)
    S42 = "input-only ceiling"
    if ana:
        rowmap = {"internal features": "primary_internal",
                  "self-report survey": None,
                  "probe-reply behaviour": "output_only",
                  "length only": "length_baseline",
                  "input-only ceiling": "input_only_ceiling"}
        for label, key in rowmap.items():
            if key is None:
                continue
            r = dig(ana, key, "analysis", errs)
            if r:
                C.append((f"{label} acc", r["observed"], 3, ("cell", S42, label, 1)))
                C.append((f"{label} p", r["p"], 4, ("cell", S42, label, 2)))
        n = dig(ana, "pretreatment_null", "analysis", errs)
        if n:
            C.append(("pre-treatment acc", n["observed"], 3,
                      ("anchor", "apparatus does not manufacture",
                       r"separates\s*\n?them at \*\*([\d.]+)")))
    if con:
        sr = dig(con, "accuracy_p.self_report", "convergence", errs)
        if sr:
            C.append(("self-report acc", sr["observed"], 3,
                      ("cell", S42, "self-report survey", 1)))
            C.append(("self-report p", sr["p"], 4, ("cell", S42, "self-report survey", 2)))
        ag = dig(con, "agreement", "convergence", errs) or {}
        pretty = {"internal|self_report": "internal vs self-report",
                  "internal|behaviour": "internal vs behaviour",
                  "self_report|behaviour": "self-report vs behaviour"}
        for k, v in ag.items():
            C.append((f"kappa {k}", v["kappa"], 3,
                      ("cell", "barely agree", pretty.get(k, k), 2)))
            C.append((f"agree {k}", v["agree"], 3,
                      ("cell", "barely agree", pretty.get(k, k), 1)))
        if ag:
            mk = sum(v["kappa"] for v in ag.values()) / len(ag)
            C.append(("mean kappa", mk, 3,
                      ("anchor", "barely agree", r"Mean κ = ([-+]\d+\.\d+)")))
            # 🚩 THE ABSTRACT WAS NOT REGISTERED. Lucien Vale, 2026-08-17 04:07:
            #    changing the abstract's mean κ from +0.059 to +0.095 while the
            #    §4.3 table stayed correct returned a full green verdict. The
            #    checker protected ONE occurrence per manifest entry, which is
            #    precisely the ordinary copy-edit failure the prose claimed to
            #    catch: a summary edited while the table stays right.
            C.append(("mean kappa (abstract)", mk, 3,
                      ("anchor", "Abstract", r"Cohen's κ = ([-+]\d+\.\d+)")))
        u = dig(con, "unanimity", "convergence", errs)
        if u:
            S44 = "agreement is itself informative"
            C.append(("unanimous acc", u["acc_unanimous"], 3,
                      ("cell", S44, "accuracy when unanimous", 1)))
            C.append(("best single", u["best_single"], 3,
                      ("cell", S44, "best single method", 1)))
            C.append(("n unanimous", u["n_unanimous"], 0,
                      ("anchor", S44, r"n = (\d+)")))
            # The abstract restates both accuracies; register those sites too.
            C.append(("unanimous acc (abstract)", u["acc_unanimous"], 3,
                      ("anchor", "Abstract", r"accuracy is (\d+\.\d+) against")))
            C.append(("best single (abstract)", u["best_single"], 3,
                      ("anchor", "Abstract", r"against\s+(\d+\.\d+) for the best single")))
            if not u.get("refit_null"):
                errs.append("convergence unanimity not from a refitting null")
    if exa:
        S44 = "agreement is itself informative"
        C.append(("threshold count", exa["threshold_count"], 0,
                  ("cell", S44, "threshold at p", 1)))
        C.append(("orbit size", exa["orbit_size"], 0,
                  ("anchor", S44, r"2²⁰ = ([\d,]+) assignments")))
        # 🚩 THE HEADLINE p WAS IN NO MANIFEST ENTRY AT ALL. Editing §4.4's
        #    `p ≈ 0.0531` to `0.0351` passed green. Both manuscript occurrences
        #    are now registered against the artefact.
        C.append(("exact p (4.4 table)", exa["p_enumerated"], 4,
                  ("anchor", S44, r"gap \| \+0\.070, \*\*p ≈ ([\d.]+)\*\*")))
        C.append(("exact p (4.4 prose)", exa["p_enumerated"], 4,
                  ("anchor", S44, r"exact tail is\s*>?\s*(\d+\.\d+)")))
        # ⚠️ `tail_count` is deliberately NOT registered. The paper states a RANGE
        #    (55,657 to 55,660) because the count is host-dependent at the
        #    few-assignment level, and registering a single artefact integer
        #    against that cell would contradict the paper's own correct refusal
        #    to certify one. The strict cell grammar caught the attempt, which is
        #    the check enforcing an honesty decision rather than a transcription.
        if exa.get("count_certified") is not False:
            errs.append("exact artefact claims a certified count; the paper does not")
    if gnd:
        for it in dig(gnd, "items", "grounding", errs) or []:
            lbl = str(it["item"])
            C.append((f"grounding {lbl} acc", it["obs"], 3, ("cell", "Grounding", lbl, 1)))
            C.append((f"grounding {lbl} p", it["p"], 3, ("cell", "Grounding", lbl, 3)))
    if cnc:
        usable = [r for r in cnc.get("results", []) if r.get("n_target_features")]
        if not usable:
            errs.append("concealment artefact has no usable targets")
        for arm in ("REVEAL", "CONCEAL", "NULL"):
            C.append((f"{arm} hits", sum(r[arm]["n_hit"] for r in usable), 0,
                      ("cell", "Sensitivity floor", "total feature hits",
                       {"REVEAL": 1, "CONCEAL": 2, "NULL": 3}[arm])))
    return C


def check(paper: Path) -> int:
    errs: list = []                       # reset per run, never module state
    text = strip_nonprose(paper.read_text(encoding="utf-8"))
    secs = sections(text)
    claims = build(errs)

    if not claims:
        print("⛔ ZERO CLAIMS CONSTRUCTED. That is a failure, not a pass:")
        for e in errs:
            print(f"   · {e}")
        return 1

    print(f"Checking {paper.name} — {len(claims)} claims, each at ONE anchored site\n")
    bad = []
    for cid, val, dp, loc in claims:
        try:
            tok = cell(secs, loc[1], loc[2], loc[3]) if loc[0] == "cell" \
                else anchored(secs, loc[1], loc[2])
            ok = same(tok, float(val), dp)
            if not ok:
                bad.append((cid, f"paper says {tok}, artefact says {float(val):.{dp}f}"))
        except Fail as f:
            ok = False
            bad.append((cid, str(f)))
            tok = "—"
        print(f"  {'OK  ' if ok else 'FAIL'}  {cid:34s} {tok:>12s}")

    print()
    for e in errs:
        print(f"⛔ {e}")
    for cid, why in bad:
        print(f"⛔ {cid}: {why}")
    if errs or bad:
        print(f"\nEXIT 1 — {len(bad)} claim failure(s), {len(errs)} artefact problem(s).")
        return 1
    print("✅ every claim is sourced, located at one site, and numerically equal.")
    print("\n📌 NOT proven here: interpretation (a right number under a wrong sentence")
    print("   passes) and unsourced claims (file -> paper only).")
    return 0


def selftest() -> int:
    """Negative fixtures run through the REAL end-to-end checker.

    🚩 The previous selftest never called check() or build(), so it stayed green
    while the real checker constructed zero claims. Every case below mutates the
    actual paper and runs the actual entry point.
    """
    import shutil, tempfile
    real = LAB / "PAPER_v2_2026-08-16.md"
    if not real.exists():
        print("⛔ need the real paper present to run mutation controls")
        return 2
    src = real.read_text(encoding="utf-8")
    tmp = Path(tempfile.mkdtemp())

    def run(label, mutate, expect_fail):
        # 🚩 ASSERT THE MUTATION LANDED BEFORE READING THE EXIT CODE.
        #    Two of my fixtures on 2026-08-17 assumed spaces where the paper has
        #    newlines, so they mutated NOTHING and the guard correctly passed an
        #    unchanged document. I read that as the guard failing and was one step
        #    from repairing working code to satisfy a broken test.
        #    ⇒ A negative control that does not actually corrupt anything is not
        #      a control; it is a clean run with a scary label.
        text = mutate(src)
        if expect_fail and text == src:
            print(f"  *** FAIL ***  {label:48s} FIXTURE IS A NO-OP")
            return False
        p = tmp / "p.md"
        p.write_text(text, encoding="utf-8")
        buf, sys.stdout = sys.stdout, open(tmp / "out.txt", "w", encoding="utf-8")
        try:
            rc = check(p)
        finally:
            sys.stdout.close(); sys.stdout = buf
        good = (rc != 0) if expect_fail else (rc == 0)
        print(f"  {'PASS' if good else '*** FAIL ***'}  {label:48s} "
              f"exit {rc} ({'expected nonzero' if expect_fail else 'expected 0'})")
        return good

    print("SELFTEST — mutation controls through the real checker\n")
    ok = True
    ok &= run("unmutated paper", lambda s: s, False)
    ok &= run("sign flip: kappas positive -> negative",
              lambda s: s.replace("**+0.036**", "**-0.036**"), True)
    ok &= run("appended digit: 0.1924 -> 0.19240001",
              lambda s: s.replace("| 0.1924 |", "| 0.19240001 |"), True)
    ok &= run("floor value 0.0005 -> 0.9999",
              lambda s: s.replace("**0.0005**", "**0.9999**"), True)
    ok &= run("right number parked elsewhere, wrong in the row",
              lambda s: s.replace("| 0.1924 |", "| 0.9999 |")
                         .replace("## 4.3", "Discarded stale value 0.1924\n\n## 4.3"), True)
    ok &= run("count inflated: n = 38 -> 338",
              lambda s: s.replace("n = 38", "n = 338"), True)
    ok &= run("row deleted entirely",
              lambda s: s.replace("| length only | 0.492 | 1.0000 |", ""), True)

    # ── Lucien Vale's four bypasses of the v3 scanner, 2026-08-17 03:08 ──────
    ok &= run("unicode minus U+2212 read as positive",
              lambda s: s.replace("**+0.036**", "**−0.036**"), True)
    ok &= run("unit suffix: 0.1924 -> 0.1924%",
              lambda s: s.replace("| 0.1924 |", "| 0.1924% |"), True)
    ok &= run("escaped pipes desynchronise columns",
              lambda s: s.replace(
                  "| internal features (16,384) | 0.550 | 0.1924 |",
                  "| internal features (16,384) \\| 0.550 \\| 0.1924 | 0.999 | 0.9999 |"), True)
    # ── Lucien Vale's ORDINARY copy-edit fixtures, 2026-08-17 04:07 ─────────
    #    Not adversarial: a summary edited while its table stays correct. These
    #    passed green until the abstract and §4.4 sites were registered, and they
    #    are the everyday failure the paper's prose actually claims to catch.
    ok &= run("abstract mean kappa +0.059 -> +0.095",
              lambda s: s.replace("Cohen's κ = +0.059", "Cohen's κ = +0.095"), True)
    ok &= run("abstract best-single 0.667 -> 0.677",
              lambda s: s.replace("against\n0.667 for the best single",
                                  "against\n0.677 for the best single"), True)
    ok &= run("4.4 exact p 0.0531 -> 0.0351",
              lambda s: s.replace("**p ≈ 0.0531**", "**p ≈ 0.0351**"), True)

    ok &= run("HTML-comment decoy row",
              lambda s: s.replace(
                  "| internal features (16,384) | 0.550 | 0.1924 |",
                  "| internal fea<!-- -->tures (16,384) | 0.999 | 0.9999 |\n"
                  "<!-- | internal features (16,384) | 0.550 | 0.1924 | -->"), True)

    shutil.rmtree(tmp, ignore_errors=True)
    print("\n" + ("all mutation controls behaved correctly"
                  if ok else "*** SELFTEST FAILED ***"))
    return 0 if ok else 1


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


if __name__ == "__main__":
    raise SystemExit(main())
