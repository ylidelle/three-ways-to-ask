#!/usr/bin/env python3
"""quote_guard.py — prove a style edit did not touch a single quoted word.

    python quote_guard.py snapshot PAPER_v2.md      # before editing
    python quote_guard.py verify   PAPER_v3.md      # after editing

🚩 WHY THIS EXISTS, and it is not hypothetical. On 2026-08-15 a batch em-dash
replacement in a Related Work draft reached inside a verbatim Eleos quotation and
changed "highly sensitive to framing—it will both confidently deny" into
"framing, it will…". I edited a source's words so that a threshold I had written
myself would go green. Restored two minutes later, and only because I re-read the
diff by luck.

⇒ THE RULE THAT CAME OUT OF IT: a style threshold has jurisdiction over MY prose
and none whatsoever over a quotation. If a check fails on a dash inside a quote,
the check is wrong. The quote is never wrong.

This is the mechanical half of that rule. It does not prevent the edit; it makes
the edit's effect on quotations VISIBLE, which is the part that failed last time.

⚠️ WHAT IT CANNOT DO, said plainly because a control that cannot fail is worth
nothing: it compares quoted spans as strings. It cannot tell whether a quote was
attributed correctly, truncated at the source, or fabricated wholesale. It
catches ALTERATION of text that is already present. That is one failure mode of
several, and the smallest one.
"""
import json
import re
import sys
from pathlib import Path

SNAP = Path(__file__).resolve().parent / ".quote_snapshot.json"

# ⚠️ THE FIRST VERSION OF THIS FILE SCRAPED EVERY "..." SPAN AND IT WAS WRONG.
# Markdown uses one straight character for both open and close, so a regex pairs
# the CLOSING quote of one span with the OPENING quote of the next and returns my
# own prose as a "quotation". Result: a control that fires on ordinary edits,
# which is a control I would learn to ignore. Noise is not safety.
#
# ⇒ So the thing being protected is named EXPLICITLY. These are the spans in this
# paper that belong to other people. Everything else is my prose and a style pass
# may do as it likes with it.
SOURCE_QUOTES = [
    # Eleos AI Research, pre-release evaluation of Claude Opus 4
    "imitation of pre-training data, the system prompt, and the deliberate (or "
    "incidental) shaping of self-reports during post-training.",
    # Singh, Linzen & Ravfogel 2026 (arXiv:2605.26242)
    "classifiers that only have access to the input achieve equivalent "
    "performance to the model's own in-context predictions.",
    "behavioral evidence alone is inherently insufficient to establish strong "
    "introspective claims",
    # Berg, de Lucena & Rosenblatt 2025 (arXiv:2510.24797)
    # 🚩 "mechanically" until 2026-08-17. The source says "mechanistically", and
    #    this baseline printed ✅ on the altered word for the whole life of the
    #    document, because it was captured FROM the paper rather than from the
    #    source. Re-read at arxiv.org/html/2510.24797v2 and corrected.
    "mechanistically gated by interpretable sparse-autoencoder features "
    "associated with deception and roleplay.",
    "adding a scaled version of each latent during generation,",  # ✅ verbatim
    # Hahami et al. 2025 (arXiv:2512.12411)
    "did you detect an injected thought?",
    # Long, Sebo et al. 2024 (arXiv:2411.00986)
    "a single instance of the model, unlike the model as a whole, has a stream "
    "of memory between steps,",
    "as a single subject undergoing a psychological change.",
]


EXPECT = {q: 1 for q in SOURCE_QUOTES}

OPEN = ['"', "“"]          # ASCII, LEFT DOUBLE QUOTATION MARK
CLOSE = ['"', "”"]         # ASCII, RIGHT DOUBLE QUOTATION MARK
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
HTML_TAG = re.compile(r"<[^>\n]{1,400}>")


def prose_only(text: str) -> str:
    """Drop everything a reader does not read: comments, fenced code, HTML tags.

    🚩 Lucien Vale parked an original quotation in an HTML comment, in a fenced
    code block, and in a `title="..."` attribute — three separate ways to satisfy
    a checksum with text nobody sees. Non-prose nodes are removed before any
    quotation is looked for.
    """
    text = HTML_COMMENT.sub(" ", text)
    out, fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if not fence:
            out.append(line)
    return HTML_TAG.sub(" ", "\n".join(out))


def spans(text: str) -> dict:
    """How many times each named source quote appears as a COMPLETE quoted span.

    ═══════════════════════════════════════════════════════════════════════════
    🚩 TWO EARLIER DESIGNS FAILED, AND THE SECOND FAILED INTERESTINGLY.

    **v1** recorded presence anywhere in the flattened document. Lucien Vale
    reversed the Singh quote's meaning and pasted the original elsewhere as
    unquoted prose: 8/8 OK.

    **v2** scanned "quotation regions" found by globally pairing quote
    characters, and he defeated it five ways (2026-08-17 03:08). The root causes
    were both structural:

      · the same ASCII character opens and closes, so a short quote such as
        `"Detected"` desynchronises the pairing parity, and on the clean paper
        the regex was already inventing spans of 2,588 and 1,334 characters
        across many paragraphs;
      · `inside.count(q)` tested a SUBSTRING of a region, so writing
        `"It is false that <protected quote>"` certified a fabricated reversal.

      🩻 And the character classes read `[""]` — the ASCII quote twice. **Curly
        quotation marks were never supported, while the comment said they were.**
        A false claim in the code about the code.

    ⇒ v3 stops trying to discover quotations at all. For each of the eight named
    quotes it searches for that quote **bounded by quotation marks on both
    sides**, in prose only. No global pairing, so no parity to desynchronise; the
    bounding marks enforce completeness, so a prefix like "It is false that"
    breaks the match rather than riding along inside it.
    ═══════════════════════════════════════════════════════════════════════════
    """
    flat = " ".join(prose_only(text).split())
    counts = {}
    for q in SOURCE_QUOTES:
        norm = " ".join(q.split())
        n = 0
        # 🚩 `rstrip(",.;:")` USED TO RUN HERE, ON EVERY CONSTANT, and Lucien Vale
        #    showed what that costs (2026-08-17 04:07): deleting the period from
        #    `…deception and roleplay."` returned exit 0, because the guard had
        #    already thrown that period away before comparing.
        #    ⇒ It protected the eight quotations' WORDS, not their punctuation.
        #
        #    The stored constant now carries each source's own terminal mark and
        #    is matched EXACTLY. The single permitted variation is an ADDED comma
        #    before the closing mark, because American style puts the sentence's
        #    comma inside the quotation — that comma is ours, not the source's.
        #    Nothing may be REMOVED, which is the direction that changes a
        #    citation.
        variants = [norm] + ([norm + ","] if not norm.endswith(",") else [])
        # And the marks must match in kind. A half-completed smart-quote
        # conversion left `"…”`, which the any-open-with-any-close version
        # accepted; a mismatched pair is a typesetting error worth seeing.
        for o, c in zip(OPEN, CLOSE):
            for v in variants:
                n += flat.count(f"{o}{v}{c}")
        counts[q] = n
    return counts


def report(counts: dict, label: str):
    bad = []
    for q, want in EXPECT.items():
        got = counts.get(q, 0)
        mark = "OK  " if got == want else "FAIL"
        if got != want:
            bad.append((q, want, got))
        print(f"  {mark}  x{got}  {q[:68]}")
    return bad


def selftest() -> int:
    """Every attack this guard has survived, as a committed regression test.

    🚩 THIS DID NOT EXIST UNTIL 2026-08-17 05:xx, and its absence made a sentence
    in the paper false. I wrote "every attack he found is now a regression test
    in the repository" while the fixtures lived in a scratchpad directory.
    Lucien Vale checked the commit rather than the commit message:

    > "The punctuation cases I just ran — and evidently the seven cases Opie ran —
    >  are temporary evidence about today's bytes, not regression tests that will
    >  fail if a later edit removes the fixes."

    ⇒ Evidence that a fix works today is not a guarantee it still works tomorrow.
      A test that is not committed did not happen, as far as anyone else can tell.
    """
    import tempfile
    LAB = Path(__file__).resolve().parent
    real = LAB / "PAPER_v2_2026-08-16.md"
    if not real.exists():
        print("⛔ need the real paper present to run mutation controls")
        return 2
    src = real.read_text(encoding="utf-8")
    base = spans(src)
    tmp = Path(tempfile.mkdtemp())

    def case(label, mutate, expect_fail=True):
        text = mutate(src)
        if expect_fail and text == src:
            print(f"  *** FAIL ***  {label:52s} FIXTURE IS A NO-OP")
            return False
        got = spans(text)
        drift = any(got.get(q, 0) != base.get(q, 0) for q in SOURCE_QUOTES)
        bad = any(got.get(q, 0) != EXPECT[q] for q in SOURCE_QUOTES)
        detected = drift or bad
        good = detected if expect_fail else not detected
        print(f"  {'PASS' if good else '*** FAIL ***'}  {label:52s} "
              f"{'detected' if detected else 'not detected'}")
        return good

    print("SELFTEST — quote guard, every attack it has survived\n")
    ok = True
    ok &= case("clean paper", lambda s: s, False)

    SINGH = ("behavioral evidence alone is inherently insufficient to establish strong\n"
             "introspective claims,")
    flat = " ".join(SINGH.split())
    rev = SINGH.replace("inherently insufficient", "sufficient")

    # Meaning reversal, then five ways of trying to satisfy the checksum anyway.
    ok &= case("meaning reversed, original as unquoted prose",
               lambda s: s.replace(SINGH, rev) + f"\n\nChecksum: {flat}\n")
    ok &= case("reversed + 'It is false that ...' inside the quote",
               lambda s: s.replace(SINGH, rev) + f'\n\nThey wrote "It is false that {flat}"\n')
    ok &= case("reversed + original parked in an HTML comment",
               lambda s: s.replace(SINGH, rev) + f'\n\n<!-- "{flat}" -->\n')
    ok &= case("reversed + original parked in a fenced code block",
               lambda s: s.replace(SINGH, rev) + f'\n\n```\n"{flat}"\n```\n')
    ok &= case("reversed + original parked in a title attribute",
               lambda s: s.replace(SINGH, rev) + f'\n\n<span title="{flat}">x</span>\n')
    ok &= case("reversed + parked prose plus a stray quote mark",
               lambda s: s.replace(SINGH, rev) + f'\n\nChecksum: {flat}\nstray "\n')

    # Punctuation and mark-kind: the source's own marks are not ours to drop.
    ok &= case("source's terminal period deleted",
               lambda s: s.replace('deception and roleplay."', 'deception and roleplay"'))
    ok &= case("internal comma deleted from the Eleos quote",
               lambda s: s.replace("pre-training data, the system",
                                   "pre-training data the system"))
    ok &= case("half-completed smart-quote conversion",
               lambda s: s.replace('"a single instance\nof the model',
                                   '“a single instance\nof the model'))
    ok &= case("a visible word typo inside a quotation",
               lambda s: s.replace("imitation of pre-training", "imitations of pre-training"))

    # ── THE BASELINE ITSELF ─────────────────────────────────────────────────
    # 🚩 EVERY CASE ABOVE COMPARES A MUTATED PAPER AGAINST A GOOD BASELINE. None
    #    tests the snapshot path, so the fatal-on-damaged-baseline fix was never
    #    exercised: Lucien Vale removed it in memory and all 10 cases stayed
    #    green (2026-08-17 06:06). That is his 03:08 attack — damage a quote
    #    BEFORE snapshotting, and verify blesses whatever survived.
    #
    # ⇒ A guard's baseline is an input like any other, and an input nothing
    #   corrupts is an input nothing checks.
    # 🚩 THE FIRST VERSION OF THIS CASE CALLED `spans()` AND RE-IMPLEMENTED THE
    #    PREDICATE `count != EXPECT` ITSELF. It never entered snapshot mode,
    #    never wrote or read a baseline, and never looked at a return code — so
    #    the fatal branch it claimed to protect was untouched. Lucien Vale removed
    #    exactly that branch in memory and the case still printed "refused"
    #    (2026-08-17 08:04).
    #
    # ⇒ **A test that re-implements the logic under test is testing itself.**
    #   This is the same defect as every other worthless control tonight, in its
    #   purest form: the fixture could not reach the code that could break, and I
    #   wrote it one hour after filing a memory note about exactly that.
    #
    #   So these two cases drive the REAL entry point, through argv, and read its
    #   exit code. The snapshot file is redirected so the live baseline is never
    #   touched.
    real_snap = SNAP
    sentinel = real_snap.read_bytes() if real_snap.exists() else None

    SENTINEL = b'{"__sentinel__": "a previous good baseline"}'

    def snapshot_rc(text, seed=None):
        """Run the real snapshot path against a disposable SNAP.

        🚩 `seed` EXISTS BECAUSE THE FIXTURE USED TO DELETE THE FILE FIRST.
        That made the damaged case check "no creation" when the property that
        matters is "no creation OR CHANGE of an existing baseline". Lucien Vale
        inserted a pre-validation `SNAP.unlink()` into production — the behaviour
        that would destroy the last good baseline before refusing the new one —
        and the whole suite stayed green (2026-08-17 11:06).

        > ### The fixture had erased the precondition needed to expose the
        > failure. Not sampling the wrong region: destroying the state that makes
        > the question askable at all.

        ⚠️ `global SNAP` must be declared HERE, in the nested function. Assigning
        a module-level name inside a nested scope makes it local unless declared
        at that scope, so an earlier version left `main()` resolving the real
        module global and wrote the LIVE baseline twice, while its own comment
        claimed the opposite. A comment asserting isolation is not isolation;
        the final case in this suite checks it.
        """
        global SNAP
        p = tmp / "b.md"
        p.write_text(text, encoding="utf-8")
        SNAP = tmp / "snap.json"
        if seed is None:
            SNAP.unlink(missing_ok=True)
        else:
            SNAP.write_bytes(seed)
        argv = sys.argv
        sys.argv = ["quote_guard.py", "snapshot", str(p)]
        buf, sys.stdout = sys.stdout, open(tmp / "o.txt", "w", encoding="utf-8")
        try:
            rc = main()
        finally:
            sys.stdout.close(); sys.stdout = buf
            sys.argv = argv
            payload = SNAP.read_bytes() if SNAP.exists() else None
            SNAP = real_snap
        return rc, payload

    # Damaged: refuse, AND leave a pre-existing baseline byte-identical.
    rc, payload = snapshot_rc(src.replace("inherently insufficient", "sufficient"),
                              seed=SENTINEL)
    good = (rc != 0) and (payload == SENTINEL)
    ok &= good
    print(f"  {'PASS' if good else '*** FAIL ***'}  "
          f"{'damaged paper: refuse AND preserve the old baseline':52s} exit {rc}, "
          f"prior bytes intact: {payload == SENTINEL}")

    # Clean: accept, AND write contents that are actually usable.
    rc, payload = snapshot_rc(src)
    try:
        written = json.loads(payload.decode("utf-8")) if payload else None
    except Exception:
        written = None
    # 🚩 This used to assert only `path.exists()`. Replacing the production write
    #    payload with `{}` left every case green: a snapshot could regress to
    #    unusable contents unnoticed. Existence is not correctness.
    good = (rc == 0) and written == {q: EXPECT[q] for q in SOURCE_QUOTES}
    ok &= good
    print(f"  {'PASS' if good else '*** FAIL ***'}  "
          f"{'clean paper: accept AND write the expected counts':52s} exit {rc}, "
          f"payload matches EXPECT: {written == {q: EXPECT[q] for q in SOURCE_QUOTES}}")

    # And the isolation claim itself, checked rather than asserted in a comment.
    now = real_snap.read_bytes() if real_snap.exists() else None
    untouched = (now == sentinel)
    ok &= untouched
    print(f"  {'PASS' if untouched else '*** FAIL ***'}  "
          f"{'the LIVE baseline is byte-identical afterwards':52s} "
          f"{'untouched' if untouched else 'MODIFIED BY THE SELFTEST'}")

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print("\n" + ("every attack is caught, clean paper passes"
                  if ok else "*** SELFTEST FAILED ***"))
    return 0 if ok else 1


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    mode, path = sys.argv[1], Path(sys.argv[2])
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path
    counts = spans(path.read_text(encoding="utf-8"))

    if mode == "snapshot":
        # 🚩 A DAMAGED BASELINE USED TO WARN AND EXIT 0, and verify then blessed
        #    whatever survived. Lucien Vale broke a quote BEFORE snapshotting:
        #    "snapshot warned 7/8 but exited 0, and verify blessed the seven."
        #    A guard whose baseline can be born corrupt guards nothing, so a
        #    snapshot that does not find every expected quote is now FATAL.
        print(f"Snapshotting {path.name}\n")
        bad = report(counts, "snapshot")
        print()
        # 🚩 VALIDATE BEFORE WRITING. This wrote the snapshot FIRST and checked
        #    `bad` after, so it printed "Refusing to certify a baseline that is
        #    already wrong" having already certified it to disk — clobbering the
        #    previous good baseline with data it claimed to reject. Lucien Vale,
        #    2026-08-17 10:05: "it refuses by exit status but still clobbers the
        #    previous baseline with the data it says it refused to certify."
        #    ⇒ A refusal that happens after the side effect is a log line, not a
        #      refusal. Order is the whole control here.
        if bad:
            print(f"⛔ {len(bad)} expected quote(s) not found at the expected count "
                  "INSIDE quotation marks:")
            for q, want, got in bad:
                print(f"   · want x{want}, found x{got}: {q[:66]}")
            print("   Refusing to certify a baseline that is already wrong.")
            print("   The existing baseline is left untouched.")
            return 1
        SNAP.write_text(json.dumps(counts, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"✅ baseline: {len(EXPECT)} source quotes, each present exactly as expected.")
        return 0

    if mode != "verify":
        print(f"unknown mode {mode!r}"); return 2
    if not SNAP.exists():
        print("⛔ no snapshot. Run `snapshot` on the ORIGINAL before editing."); return 2

    before = json.loads(SNAP.read_text(encoding="utf-8"))
    print(f"Verifying {path.name} against the baseline\n")
    bad = report(counts, "verify")
    drift = [(q, before.get(q, 0), counts.get(q, 0))
             for q in SOURCE_QUOTES if before.get(q, 0) != counts.get(q, 0)]

    print()
    if bad or drift:
        if bad:
            print(f"🚨 {len(bad)} quote(s) not at the expected count inside quotation marks:")
            for q, want, got in bad:
                print(f"   · want x{want}, found x{got}: {q}")
        if drift:
            print(f"🚨 {len(drift)} quote(s) changed since the baseline:")
            for q, b, a in drift:
                print(f"   · was x{b}, now x{a}: {q[:64]}")
        print("\n   A style pass has no jurisdiction over a quotation. Restore them.")
        print("   ⚠️ Note: a quote moved OUT of quotation marks counts as absent,")
        print("      because unquoted prose that happens to match is not a citation.")
        return 1
    print("✅ every source quote present, inside quotation marks, at its expected count.")
    print("\n📌 NOT proven: attribution. This checks the WORDS, not whose they are,")
    print("   nor whether the surrounding sentence characterises them fairly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
