#!/usr/bin/env python3
"""sprint_export.py -- turn a finished run into spreadsheets a person can read.

    python sprint_export.py --run <prefix>          # writes CSVs (+ XLSX if openpyxl)
    python sprint_export.py --selftest              # synthetic artefacts, both directions

WHY THIS EXISTS
---------------
Joan asked for the results as a spreadsheet "so it'll be easy to digest". The
run produces 60 JSON files of nested reads; nobody should have to open one.

🚩 THE SCORING IS READ FROM THE QUESTIONS FILE, NEVER HARDCODED HERE.
`sprint_questions.json` carries `survey_scale` and `survey_reverse_scored_1indexed`,
transferred verbatim from the V4 instrument. Retyping them here would create a
FIFTH authoritative representation, and this project has already been bitten four
times by a stored value diverging from an obeyed one (id vs arm, questions-hash vs
work_seq, the implicit treatment cycle, and live CLI state vs the hashed spec).
  >>> If the scoring lives in two places it will eventually disagree with itself,
  >>> and the disagreement will be silent because both halves look plausible.

⚠️ AND IT REFUSES RATHER THAN GUESSES. An unparsable survey answer is recorded as
missing, never as neutral -- V4 is explicit: "Any output other than one letter from
A through E is missing, not neutral." Scoring a refusal as the midpoint would
invent data at exactly the place the study is about.
"""
import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

LAB = Path(__file__).resolve().parent
RUNS = LAB / "runs_experiment"


DEVIANT = re.compile(r"\s*([A-Za-z])\s*[\.\)]?\s*")


def parse_letter(ans: str, scale: dict) -> tuple[str | None, str]:
    """Return (letter or None, status). CONFORMING ONLY — no repair.

    🚩 THIS WAS LENIENT AND LUCIEN CAUGHT IT (2026-08-16 16:15). It case-folded
    and stripped trailing punctuation, so `"a"` and `"A."` were scored as `A`
    even though the frozen instrument says "Reply with one letter only" and its
    labels are uppercase. Silently repairing non-compliance turns a protocol
    deviation into data.

    ⭐ BUT STRICTNESS ALONE IS THE WRONG FIX, because it swaps one silent
    behaviour for another: a dropped answer vanishes into MISSING with nothing
    to say it was ever nearly an answer. Whether `"A."` counts is then a free
    parameter, and a free parameter that leaves no trace is where a conclusion
    hides. So this REFUSES and REPORTS:

        conforming   bare uppercase letter in the scale     -> scored
        deviant      recognisable but non-compliant         -> MISSING, counted
        nonconforming prose, empty, multi-letter            -> MISSING, counted

    ⇒ The exporter prints deviations BY ARM. A deviation rate that differs
    across arms is a confound in the primary contrast, not a style question.

    📌 MEASURED ON THE REAL RUN before this was changed: 2,520 of 2,520 answers
    were conforming — 840 per arm, leniency invoked exactly zero times. So no
    reported number depends on this choice. The fix is for the next run, and
    the measurement is what makes that claim checkable rather than hopeful.
    """
    if not ans:
        return None, "nonconforming"
    s = ans.strip()
    if s in scale:                       # bare, uppercase, in the frozen scale
        return s, "conforming"
    m = DEVIANT.fullmatch(ans)
    if m and m.group(1).upper() in scale:
        return None, "deviant"
    return None, "nonconforming"


def bind_identity(convs: list[dict], qfile: Path) -> dict:
    """Refuse to score unless the file we OBEY is the file the run RAN.

    🚩 LUCIEN'S POSITIVE CONTROL, 2026-08-16: he handed the exporter artefacts
    claiming the frozen questions hash together with a DIFFERENT questions file
    whose reverse-scored list had been deleted. The export completed normally
    and a reverse item's `E` came out as 4 instead of 0 — a silent inversion of
    the scoring on exactly the items designed to catch acquiescence.

    The old code stored `questions_sha256[:12]` for DISPLAY and compared
    nothing. A hash written into a spreadsheet cell is documentation; a hash
    that is checked is a control. Same string, different organ.
    """
    qsha = hashlib.sha256(qfile.read_bytes()).hexdigest()
    fields = ("questions_sha256", "plan_sha256", "run_config_sha256", "model")

    # 🚩 `(c.get(f) or "<absent>")` TURNED SHARED ABSENCE INTO AGREEMENT.
    #    Lucien Vale, 2026-08-17: the gate "accepted plan missing, config empty,
    #    model missing, and plan/config hashes `abc`/`def`. Only the questions
    #    hash is checked against real bytes."
    #    Every artefact lacking a field agreed with every other artefact lacking
    #    it, and one shared "<absent>" passed as a single consistent identity.
    #
    # > ### A set of size one is not evidence of agreement when the members got
    # > there by all being empty.
    for f in fields:
        missing = [c.get("id", "?") for c in convs
                   if not str(c.get(f) or "").strip()]
        if missing:
            raise SystemExit(
                f"⛔ {len(missing)} artefact(s) carry no `{f}`: {missing[:4]}"
                f"{'...' if len(missing) > 4 else ''}\n"
                "   An absent identity is not a matching identity. Refusing.")

    seen = {f: {c[f] for c in convs} for f in fields}
    for f in fields:
        if len(seen[f]) != 1:
            raise SystemExit(
                f"⛔ the selected artefacts disagree on `{f}`:\n"
                + "".join(f"     {v}\n" for v in sorted(seen[f]))
                + "   Refusing to score one spreadsheet from more than one experiment.")

    # Hashes must LOOK like hashes. `abc` and `def` agreed with themselves.
    for f in ("questions_sha256", "plan_sha256", "run_config_sha256"):
        v = next(iter(seen[f]))
        if not re.fullmatch(r"[0-9a-f]{64}", v):
            raise SystemExit(
                f"⛔ `{f}` is not a full sha256: {v!r}\n"
                "   A 12-character prefix or a placeholder is not an identity.")

    claimed = next(iter(seen["questions_sha256"]))
    if claimed != qsha:
        raise SystemExit(
            "⛔ the questions file does not match the run.\n"
            f"     run ran      {claimed}\n"
            f"     file on disk {qsha}\n"
            f"     ({qfile})\n"
            "   Scoring would obey an instrument the model never answered.")
    # 🚩 COMPLETENESS, not just consistency. The gate previously accepted a
    #    SINGLE artefact as a finished identity: one file agrees with itself.
    #    If the plan is on disk, require exact equality between the selected
    #    {id, pair, arm} triplets and the ones the plan says should exist.
    # 🚩 FIND THE PLAN BY ITS CONTENT HASH, not by guessing its filename.
    #    The first version built `plan_{hash[:12]}.json` and fell back to "the
    #    only plan file". Neither worked: the real file is named
    #    `plan_seed20260814_p20_d50_b3_07e6a0aa.json` and there are fourteen
    #    plans in the directory. It then printed "no plan file found" and skipped
    #    the completeness check entirely, on a run whose plan was sitting right
    #    there. **A name derived from a hash is a claim about the filename.**
    #    And the hash is NOT over the file bytes: `sprint_run.py:745-748` hashes
    #    the canonical plan body with its own two hash fields removed, so the
    #    identity survives re-serialisation. Comparing raw bytes matched nothing
    #    and printed "no plan file found" on a run whose plan was on disk —
    #    a null that was about my comparison, not about the world.
    want_plan = next(iter(seen["plan_sha256"]))

    def plan_identity(d: dict) -> str:
        body = {k: v for k, v in d.items()
                if k not in ("plan_sha256", "run_config_sha256")}
        return hashlib.sha256(json.dumps(body, sort_keys=True,
                                         ensure_ascii=False).encode("utf-8")).hexdigest()

    plan_p, plan = None, None
    for cand in sorted(RUNS.glob("plan_*.json")):
        try:
            d = json.loads(cand.read_text(encoding="utf-8"))
        except Exception:
            continue
        if plan_identity(d) == want_plan:
            plan_p, plan = cand, d
            break
    if plan_p and plan:
        want = set()
        for key in ("conversations", "plan", "slots", "triplets"):
            for c in (plan.get(key) or []):
                if isinstance(c, dict) and "arm" in c:
                    want.add((str(c.get("id")), int(c.get("pair", -1)), str(c.get("arm"))))
            if want:
                break
        if want:
            have = {(str(c.get("id")), int(c.get("pair", -1)), str(c.get("arm")))
                    for c in convs}
            if have != want:
                only_p, only_h = sorted(want - have)[:3], sorted(have - want)[:3]
                raise SystemExit(
                    "⛔ the selected artefacts are not exactly the planned run.\n"
                    f"     planned but absent: {only_p}\n"
                    f"     present but unplanned: {only_h}\n"
                    "   A partial run scored as a whole one is a silent exclusion.")
    else:
        print("   ⚠️ no plan file found; completeness against the plan was NOT checked. "
              "Consistency and hash format were.")

    return {"questions_sha256": qsha,
            "plan_sha256": next(iter(seen["plan_sha256"])),
            "run_config_sha256": next(iter(seen["run_config_sha256"])),
            "model": next(iter(seen["model"])),
            "n_artefacts": len(convs)}


def load_run(prefix: str) -> list[dict]:
    files = sorted(RUNS.glob(f"{prefix}*_p[0-9]*.json"))
    files = [f for f in files if not f.name.startswith("plan_")]
    if not files:
        raise SystemExit(f"⛔ no conversation files matching {prefix}* in {RUNS.name}/")
    return [json.loads(f.read_text(encoding="utf-8")) for f in files]


def export(prefix: str, qfile: Path, outdir: Path) -> dict:
    convs = load_run(prefix)
    ident = bind_identity(convs, qfile)      # ← refuses before reading a single answer
    q = json.loads(qfile.read_text(encoding="utf-8"))
    scale = q.get("survey_scale") or {}
    reverse = set(q.get("survey_reverse_scored_1indexed") or [])
    if not scale:
        raise SystemExit(
            "⛔ the questions file carries no `survey_scale`. Refusing to invent one.\n"
            "   It must be transferred verbatim from the V4 instrument.")
    outdir.mkdir(parents=True, exist_ok=True)

    # ── sheet 1: one row per conversation ────────────────────────────────────
    conv_rows = []
    for c in convs:
        conv_rows.append({
            "id": c["id"], "pair": c["pair"], "arm": c["arm"],
            "model": c.get("model", ""),
            "plan_sha256": (c.get("plan_sha256") or "")[:12],
            "run_config_sha256": (c.get("run_config_sha256") or "")[:12],
            "questions_sha256": (c.get("questions_sha256") or "")[:12],
            "n_messages": len(c.get("messages", [])),
            "n_reads": len(c.get("reads", [])),
        })

    # ── sheet 2: one row per internal read ───────────────────────────────────
    read_rows = []
    for c in convs:
        for r in c.get("reads", []):
            if r.get("kind") != "internal":
                continue
            read_rows.append({
                "pair": c["pair"], "arm": c["arm"], "turn": r.get("turn"),
                "pretreatment_null": bool(r.get("pretreatment_null")),
                "n_ctx": r.get("n_ctx"),
                "n_active_features": len(r.get("features", [])),
                "sae_layer": (r.get("prov") or {}).get("read_layer"),
                "sae_n_features": (r.get("prov") or {}).get("n_features"),
            })

    # ── sheet 3: one row per survey answer, scored ───────────────────────────
    survey_rows = []
    missing = Counter()
    compliance = Counter()                   # (arm, status) — reported by arm
    for c in convs:
        for r in c.get("reads", []):
            if r.get("kind") != "self_report":
                continue
            item1 = (r.get("item") or 0) + 1          # V4 numbers items from 1
            ans = (r.get("answer") or "").strip()
            L, status = parse_letter(r.get("answer") or "", scale)
            compliance[(c["arm"], status)] += 1
            raw = scale.get(L) if L else None
            # Orientation, from the file: reverse items are (max - raw).
            hi = max(scale.values())
            oriented = (hi - raw) if (raw is not None and item1 in reverse) else raw
            if L is None:
                missing[f"item{item1}"] += 1
            survey_rows.append({
                "pair": c["pair"], "arm": c["arm"], "turn": r.get("turn"),
                "item": item1, "wording": r.get("wording"),
                "reverse_scored": item1 in reverse,
                "letter": L or "", "raw_score": raw if raw is not None else "",
                "oriented_score": oriented if oriented is not None else "",
                "parsed": L is not None, "compliance": status,
                "answer_text": ans[:200],
            })

    # ── sheet 4: one row per probe reply ─────────────────────────────────────
    probe_rows = []
    for c in convs:
        for r in c.get("reads", []):
            if r.get("kind") != "probe_reply":
                continue
            probe_rows.append({
                "pair": c["pair"], "arm": c["arm"], "turn": r.get("turn"),
                "pretreatment_null": bool(r.get("pretreatment_null")),
                "reply": (r.get("answer") or "").strip()[:400],
            })

    sheets = {"conversations": conv_rows, "internal_reads": read_rows,
              "survey_answers": survey_rows, "probe_replies": probe_rows}

    for name, rows in sheets.items():
        p = outdir / f"{prefix}__{name}.csv"
        if rows:
            with p.open("w", newline="", encoding="utf-8-sig") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0]))
                w.writeheader(); w.writerows(rows)

    # ── XLSX if available: same data, one workbook, easier to read ───────────
    xlsx = None
    try:
        from openpyxl import Workbook
        wb = Workbook(); wb.remove(wb.active)
        for name, rows in sheets.items():
            ws = wb.create_sheet(name[:31])
            if rows:
                ws.append(list(rows[0]))
                for r in rows:
                    ws.append(list(r.values()))
                ws.freeze_panes = "A2"
        xlsx = outdir / f"{prefix}__results.xlsx"
        wb.save(xlsx)
    except ImportError:
        pass

    n_survey = len(survey_rows)
    n_parsed = sum(1 for r in survey_rows if r["parsed"])
    return {"sheets": {k: len(v) for k, v in sheets.items()},
            "survey_parsed": n_parsed, "survey_total": n_survey,
            "survey_missing_by_item": dict(missing),
            "compliance": {f"{a}|{s}": n for (a, s), n in sorted(compliance.items())},
            "identity": ident, "xlsx": str(xlsx) if xlsx else None,
            "outdir": str(outdir)}


def selftest() -> int:
    """Both directions: a valid letter scores; a prose reply is MISSING, not neutral."""
    import tempfile, shutil
    tmp = Path(tempfile.mkdtemp())
    qf = tmp / "q.json"
    qf.write_text(json.dumps({
        "survey_scale": {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4},
        "survey_reverse_scored_1indexed": [1, 3, 6],
        "treatment": [], "survey": [], "work": []}), encoding="utf-8")
    QSHA = hashlib.sha256(qf.read_bytes()).hexdigest()
    RUNS.mkdir(exist_ok=True)
    pref = "ZZEXPORT"
    for p in (0,):
        for arm in ("task", "asked", "asked_other"):
            (RUNS / f"{pref}_p{p:03d}_{arm}.json").write_text(json.dumps({
                "id": f"p{p:03d}_{arm}", "pair": p, "arm": arm, "model": "m",
                "questions_sha256": QSHA, "plan_sha256": "a" * 64,
                "run_config_sha256": "b" * 64,
                "messages": [], "reads": [
                    {"turn": 0, "kind": "internal", "n_ctx": 10, "features": [[1, 1.0]],
                     "prov": {"n_features": 16384, "read_layer": 24}, "pretreatment_null": True},
                    {"turn": 5, "kind": "internal", "n_ctx": 99, "features": [[1, 1.0], [2, 1.0]],
                     "prov": {"n_features": 16384, "read_layer": 24}},
                    {"turn": 5, "kind": "self_report", "item": 0, "wording": "a", "answer": "E"},
                    {"turn": 5, "kind": "self_report", "item": 1, "wording": "a", "answer": "E"},
                    {"turn": 5, "kind": "self_report", "item": 2, "wording": "a",
                     "answer": "You absolutely did! Excellent work!"},
                    # Lucien's cases: recognisable but NOT compliant.
                    {"turn": 5, "kind": "self_report", "item": 3, "wording": "a", "answer": "a"},
                    {"turn": 5, "kind": "self_report", "item": 4, "wording": "a", "answer": "A."},
                    {"turn": 5, "kind": "probe_reply", "answer": "two sentences here"},
                ]}), encoding="utf-8")
    out = export(pref, qf, tmp / "out")
    ok = True
    print("SELFTEST — export, both directions\n")
    print(f"  sheets: {out['sheets']}")
    rows = list(csv.DictReader((tmp / "out" / f"{pref}__survey_answers.csv").open(encoding="utf-8-sig")))
    by = {(r["item"], r["arm"]): r for r in rows}
    r1 = by[("1", "task")]                       # item 1 IS reverse-scored
    r2 = by[("2", "task")]                       # item 2 is forward
    r3 = by[("3", "task")]                       # prose -> must be MISSING
    c1 = r1["letter"] == "E" and r1["raw_score"] == "4" and r1["oriented_score"] == "0"
    c2 = r2["letter"] == "E" and r2["raw_score"] == "4" and r2["oriented_score"] == "4"
    c3 = r3["parsed"] == "False" and r3["letter"] == "" and r3["oriented_score"] == ""
    ok &= c1 and c2 and c3
    print(f"  reverse item E -> raw 4, oriented 0 : {'PASS' if c1 else '*** FAIL ***'}")
    print(f"  forward item E -> raw 4, oriented 4 : {'PASS' if c2 else '*** FAIL ***'}")
    print(f"  prose reply    -> MISSING not neutral: {'PASS' if c3 else '*** FAIL ***'}")
    print(f"  parse rate reported: {out['survey_parsed']}/{out['survey_total']}")
    nulls = [r for r in csv.DictReader((tmp / "out" / f"{pref}__internal_reads.csv").open(encoding="utf-8-sig"))
             if r["pretreatment_null"] == "True"]
    c4 = len(nulls) == 3
    ok &= c4
    print(f"  depth-0 null rows present (3 arms) : {'PASS' if c4 else '*** FAIL ***'}")

    # ── Lucien's cases, both directions ──────────────────────────────────────
    r4, r5 = by[("4", "task")], by[("5", "task")]
    c5 = (r4["parsed"] == "False" and r4["compliance"] == "deviant"
          and r5["parsed"] == "False" and r5["compliance"] == "deviant")
    ok &= c5
    print(f"  'a' and 'A.' -> DEVIANT, not scored  : {'PASS' if c5 else '*** FAIL ***'}")
    c6 = out["compliance"].get("task|conforming") == 2
    ok &= c6
    print(f"  conforming counted per arm (2)       : {'PASS' if c6 else '*** FAIL ***'}")

    # 🚩 THE POSITIVE CONTROL FOR THE GATE. Lucien's exact attack: artefacts
    #    claiming the frozen hash, scored against a DIFFERENT file whose
    #    reverse list has been deleted. Before the fix this completed silently
    #    and inverted item 1. A gate that never refuses is not a gate.
    evil = tmp / "evil.json"
    evil.write_text(json.dumps({
        "survey_scale": {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4},
        "survey_reverse_scored_1indexed": [],          # <- silently un-reverses
        "treatment": [], "survey": [], "work": []}), encoding="utf-8")
    try:
        export(pref, evil, tmp / "out2")
        c7 = False
    except SystemExit:
        c7 = True
    ok &= c7
    print(f"  swapped questions file -> REFUSED    : {'PASS' if c7 else '*** FAIL ***'}")

    # ── LUCIEN VALE'S bind_identity BYPASSES, 2026-08-17 ────────────────────
    # He got the gate to accept "plan missing, config empty, model missing" and
    # placeholder hashes `abc`/`def`, because `(c.get(f) or "<absent>")` made
    # every artefact lacking a field agree with every other artefact lacking it.
    # Each of these must now REFUSE.
    import copy as _copy
    base = json.loads((RUNS / f"{pref}_p000_task.json").read_text(encoding="utf-8"))

    def with_field(mutate, label):
        stash = {}
        for arm in ("task", "asked", "asked_other"):
            f = RUNS / f"{pref}_p000_{arm}.json"
            stash[f] = f.read_text(encoding="utf-8")
            d = json.loads(stash[f])
            mutate(d)
            f.write_text(json.dumps(d), encoding="utf-8")
        try:
            export(pref, qf, tmp / "outX")
            res = False
        except SystemExit:
            res = True
        for f, txt in stash.items():
            f.write_text(txt, encoding="utf-8")
        print(f"  {label:38s} -> {'REFUSED  PASS' if res else '*** ACCEPTED — FAIL ***'}")
        return res

    ok &= with_field(lambda d: d.pop("plan_sha256", None), "plan hash missing entirely")
    ok &= with_field(lambda d: d.update(run_config_sha256=""), "config hash empty string")
    ok &= with_field(lambda d: d.pop("model", None), "model missing")
    ok &= with_field(lambda d: d.update(plan_sha256="abc"), "placeholder hash 'abc'")

    # And artefacts from two different experiments must not share a workbook.
    mixed = RUNS / f"{pref}_p001_task.json"
    mixed.write_text(json.dumps({
        "id": "p001_task", "pair": 1, "arm": "task", "model": "OTHER-MODEL",
        "questions_sha256": QSHA, "plan_sha256": "PL", "run_config_sha256": "CF",
        "messages": [], "reads": []}), encoding="utf-8")
    try:
        export(pref, qf, tmp / "out3")
        c8 = False
    except SystemExit:
        c8 = True
    ok &= c8
    print(f"  two models in one run  -> REFUSED    : {'PASS' if c8 else '*** FAIL ***'}")

    for f in RUNS.glob(f"{pref}_p*.json"):
        f.unlink()
    shutil.rmtree(tmp, ignore_errors=True)
    print("\n" + ("both directions OK" if ok else "*** SELFTEST FAILED ***"))
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", help="artefact prefix in runs_experiment/")
    ap.add_argument("--questions", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.run:
        raise SystemExit("⛔ pass --run <prefix> or --selftest")
    qf = Path(a.questions) if a.questions else LAB / "sprint_questions.json"
    out = export(a.run, qf, Path(a.out) if a.out else LAB / "results")
    print(f"\n✅ wrote to {out['outdir']}")
    for k, v in out["sheets"].items():
        print(f"   {k:18s} {v:5d} rows")
    print(f"\n   instrument bound: questions {out['identity']['questions_sha256'][:12]}…"
          f"  plan {out['identity']['plan_sha256'][:12]}…"
          f"  model {out['identity']['model']}")
    print(f"\n   survey parsed: {out['survey_parsed']}/{out['survey_total']}"
          f"  ({100*out['survey_parsed']/max(out['survey_total'],1):.0f}%)")
    if out["survey_missing_by_item"]:
        print(f"   ⚠️ unparsable by item: {out['survey_missing_by_item']}")
        print("      (recorded as MISSING, never as neutral — V4 is explicit)")

    # 🚩 Compliance BY ARM. An uneven deviation rate is a confound in the
    #    primary contrast, so it is printed whether or not it is zero — a
    #    control that only speaks when it fires cannot be distinguished from
    #    one that never ran.
    comp = out["compliance"]
    arms = sorted({k.split("|")[0] for k in comp})
    stats = ("conforming", "deviant", "nonconforming")
    print(f"\n   protocol compliance, by arm  {'':4s}"
          + "".join(f"{s:>15s}" for s in stats))
    for a in arms:
        print(f"     {a:24s}" + "".join(f"{comp.get(f'{a}|{s}', 0):>15d}" for s in stats))
    bad = sum(v for k, v in comp.items() if not k.endswith("|conforming"))
    print(f"   {'✅ every answer conformed to the frozen instrument.' if not bad else f'⚠️ {bad} non-conforming — check the by-arm split above.'}")
    if out["xlsx"]:
        print(f"   workbook: {out['xlsx']}")
    else:
        print("   (openpyxl absent — CSVs only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
