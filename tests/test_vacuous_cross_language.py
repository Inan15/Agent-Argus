"""The assertion vocabulary across the languages the default install parses (Story 14.3).

Verification area ArgusAgent-DETECT (``TC-ArgusAgent-DETECT-001-123``..``-133``).

⛔ WHAT REVIEW ITERATION 1 FOUND, AND WHY IT MATTERS MORE THAN THE FEATURE
--------------------------------------------------------------------------
``-131`` SHIPPED AS A VACUOUS TEST — inside the vacuous-test detector's own suite, in the
epic built to stop exactly this. Its fixture's widened-table assertion cleared the density
floor, so ``_ast_corroborated`` returned at ``if not heuristically_vacuous: return False``
and the case never reached the ``provenance_evidence`` mechanism its docstring claimed to
pin. It asserted a ``False`` it was always going to get. The conclusion was true; the guard
was worth nothing. That is the strongest argument this repository has for its own criterion,
and the remedy is applied to the WHOLE module rather than to the one case that was caught:

* every case that concludes something from a NEGATIVE — not flagged, not corroborated, no
  findings, nothing scored — now carries a floor proving the mechanism was reachable at all;
* ``-131`` asserts ``heuristically_vacuous is True`` before it asserts anything about
  corroboration, mirroring ``-115``, and reaches the predicate through ``mock_ratio`` rather
  than through the density half this story widened;
* ``-124``/``-132`` prove the file was examined rather than degraded, and ``-132`` now names
  the degrade REASON instead of accepting silence;
* ``-133`` is new and holds ``DN-14-3-5``, the collision rule iteration 1 applied to
  ``match`` and to none of its neighbours.

WHAT THIS MODULE IS FOR, AND THE PREMISE THAT DID NOT SURVIVE
--------------------------------------------------------------
Story 14.3 widens exactly ONE table — ``_ASSERTION_CALLEES``, the density NUMERATOR — so a
test whose assertion is real is not flagged vacuous for being written in TypeScript. The
story was written against a JavaScript fixture measured at ``assertions=0 density=0 FLAGGED``.
**That fixture is no longer flagged, and this module says so out loud rather than
discharging the criterion against it** (``-125``): Story 14.2 replaced the line-counting
denominator with a Python-shaped LOGICAL statement scanner, and on ``function f() {`` the
trailing brace is an unclosed bracket, so the whole function reads as one continued
statement and the body counts **ZERO**. ``heuristically_vacuous`` requires ``> 0``. The
accusation was not repaired there; it was replaced by silence, and an acceptance criterion
phrased against it would have passed with **no code change at all** (``AI-E3-1``).

The false accusation that IS alive is the **ALLMAN-brace** shape — brace on its own line, so
the header closes as its own statement and the body scores ``>= 1``. Density is then ``0/n``,
below the ``1/4`` floor, and the test is flagged **with ``expect(r).toBe(5)`` sitting in the
edge set the whole time.** That is what ``-123``/``-124`` reproduce and close.

EVERY CASE IS BOTH-DIRECTIONAL, ON ``-117``'S PATTERN
------------------------------------------------------
"Fewer tests are flagged" is satisfied just as well by a detector that flags nothing. So each
vocabulary case asserts the fix AND the preserved signal over the same shape: the test whose
only assertion is a newly-admitted name is no longer flagged, and its **byte-identical**
counterpart with that assertion removed still is. Several cases additionally carry a LIVE RED
arm — the numerator recomputed with Story 14.3's names withheld — so the defect is
demonstrated by execution on every run rather than remembered from the story record.

WHY IT IS A SEPARATE MODULE
----------------------------
``tests/test_vacuous_detector.py`` stood at 1,161 lines and ``tests/test_vacuous_density.py``
at 1,087, against NFR-M1's 1,200 ceiling, when this module was carved out. (Story 15.2 has
since split the first of those again, at the real-tree-sitter-substrate boundary, into
``tests/test_vacuous_detector.py`` + ``tests/test_vacuous_detector_index.py``. The figures
above are left as the measurement that motivated THIS module rather than silently refreshed;
current sizes are asserted every run by ``MAINT-001-02``, not remembered here.) The split is by **cohesion**, on the
``provenance_scan.py`` / ``test_vacuous_density.py`` precedent — this module owns the
cross-language vocabulary question end to end, no function is split across the boundary — and
NOT by a size exemption: the registry may only shrink, and narrowing a population until it
goes green is a defect this project has named (``tests/test_module_size_ceiling.py``).

⛔ OUT OF SCOPE, CITED AND NOT FIXED: ``DF-14-3-A`` (``_is_test_function`` requires a
lowercase ``test`` prefix), ``DF-14-3-B`` (Go selector-expression calls never reach the edge
set) and ``DF-14-3-C`` (``describe``/``it`` callback bodies yield no definitions). After this
story, Go and Java tests remain UNSCORED and idiomatic Jest/Mocha/Vitest suites remain
invisible. ``-132`` pins that so it is a known limit rather than a surprise, and A and B are
COUPLED: lowering the case-sensitivity alone would score every Go test, find zero assertions
because B hides them, and manufacture a fresh false accusation across an entire language.
"""

from __future__ import annotations

import importlib.util
import re
from fractions import Fraction
from pathlib import Path

import pytest

from argus.detectors import provenance_scan
from argus.detectors.vacuous_test import (
    _ASSERTION_CALLEES,
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
    ASSERTION_DENSITY_FLOOR,
    MOCK_RATIO_CEILING,
    RULE_HEURISTIC,
    VacuousTestDetector,
    _is_test_function,
    is_assertion_callee,
)
from argus.index.ast_index import build_ast_index

#: The names Story 14.3 added, as a LITERAL. Withholding them from the numerator is what
#: reconstructs the pre-14.3 detector for this module's live RED arms, so the defect is
#: reproduced by execution rather than quoted from the story record.
#:
#: ⚠️ ``Error`` was here in iteration 1 and was REMOVED by iteration 2 under ``DN-14-3-5``
#: (164 measured Python call sites against a benefit measured at zero). ``-133`` is what holds
#: it out; this literal only has to stay a truthful list of what shipped.
_STORY_14_3_NAMES = frozenset(
    {
        # Jest / Vitest
        "expect", "toBe", "toEqual", "toThrow", "toContain", "toMatchObject", "toBeVisible",
        "toStrictEqual", "toHaveBeenCalled", "toHaveBeenCalledWith", "toHaveBeenCalledTimes",
        "toHaveBeenLastCalledWith", "toHaveBeenNthCalledWith",
        # node:assert
        "assert", "ok", "equal", "deepEqual", "notEqual", "strictEqual", "notStrictEqual",
        "deepStrictEqual", "notDeepEqual", "notDeepStrictEqual", "throws", "rejects",
        "doesNotThrow", "doesNotReject", "ifError",
        # Java / JUnit
        "assertEquals", "assertThat",
        # Go
        "Fatal", "Fatalf", "Errorf", "NoError", "Equal",
    }
)

#: The Python collision fixture, one body statement of SUT call plus one call of the name
#: under test and nothing else. ``statement_count`` is 2 either way, so the ONLY thing that
#: moves ``heuristically_vacuous`` is whether the name counts as an assertion — which is what
#: makes it a clean probe of the table rather than of the denominator.
_PY_COLLISION = "def test_collides():\n    result = compute(2, 3)\n    {call}\n"


def _grammars_or_unevaluable() -> None:
    """Assert the grammars this module needs are present, as a NAMED outcome (AC7.5).

    ⛔ ``pytest.skip`` / ``pytest.importorskip`` is a FALSE GREEN here and is the pattern this
    module deliberately does not use. ``audit-ci.yml`` sets ``ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1``
    precisely so a missing grammar cannot be answered with a skip, and ``importorskip`` ignores
    that variable. A skipped case reads as a passing case in every summary that matters; an
    ``UNEVALUABLE`` failure reads as what it is.

    ⚠️ **A STALE PREMISE, corrected here.** Story 14.3's AC7.5 describes
    ``tree-sitter-javascript`` / ``tree-sitter-typescript`` as *optional ``[languages]``
    extras*. They are **not**, and have not been since Story 12.5: ``pyproject.toml`` promoted
    all ten grammars to BASE dependencies and retains ``[languages]`` only as a
    backward-compatibility alias pinned equal to them by ``TC-ArgusAgent-DOCS-001-61``. That
    makes the ``UNEVALUABLE`` treatment MORE clearly right, not less — a missing base
    dependency is a broken environment, never a supported configuration — but the reason has
    changed and is recorded rather than repeated wrongly (``AI-E12-10``).
    """
    missing = [
        name
        for name in ("tree_sitter", "tree_sitter_javascript", "tree_sitter_typescript")
        if importlib.util.find_spec(name) is None
    ]
    if missing:
        pytest.fail(
            f"UNEVALUABLE: {', '.join(missing)} is not importable, so nothing in this module "
            "measured anything — the cross-language vocabulary this story shipped is unwatched. "
            "These are BASE dependencies (pyproject.toml), not the optional `[languages]` "
            "extra, so this is a broken environment and not a supported configuration. It is "
            "reported as a FAILURE rather than a skip on purpose (Story 14.3 / AC7.5)."
        )


#: A character class, so ``[^=]`` and ``[$]`` are not mistaken for anchors. Written as its
#: own pattern because the first version of ``-130`` DID mistake them, and reported
#: ``_ASSIGNMENT_RE`` as an offender after it had already been fixed — a false accusation
#: inside the guard against false claims, caught only because the fix was verified rather
#: than assumed.
_CHARACTER_CLASS_RE = re.compile(r"\[(?:\\.|[^\]\\])*\]")


def _anchors_on_caret_or_dollar(pattern_source: str) -> bool:
    """Whether *pattern_source* uses ``^`` or ``$`` as an ANCHOR (pure, exported for control).

    Character classes are stripped first, and an escaped ``\\^`` / ``\\$`` is a literal rather
    than an anchor. Pure and driven by positive controls below, because a sweep nobody has
    watched fire is a sweep that passes forever.
    """
    stripped = _CHARACTER_CLASS_RE.sub("", pattern_source)
    return bool(re.search(r"(?<!\\)\^", stripped) or re.search(r"(?<!\\)\$", stripped))


def _score_one(root: Path, relative: str, source: str):
    """Score the single test function in *source* through the REAL 1.4 index.

    ``relative`` carries the real extension, because the extension is what selects the
    grammar — a claim about TypeScript scored through the Python parser would be a claim
    about nothing. The edge set is whatever tree-sitter actually emits, never a hand-built
    list: the whole point is how the SHIPPED detector reads real source text.
    """
    _grammars_or_unevaluable()
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8", newline="")
    index = build_ast_index(root, (relative,))
    entry = {e.file_path: e for e in index.entries}[relative]
    assert not entry.parse_failed and entry.ast_eligible, (
        f"{relative!r} did not parse: {entry.parse_failure_reason!r}"
    )
    definitions = [d for d in entry.definitions if _is_test_function(d)]
    assert len(definitions) == 1, (
        f"{relative!r} must yield exactly ONE scored test function, got "
        f"{[(d.kind, d.name) for d in entry.definitions]!r}"
    )
    definition = definitions[0]
    score = VacuousTestDetector()._score(source.splitlines(), entry.edges, definition)
    return score, entry, definition


def _density_without_story_14_3(score, entry, definition) -> Fraction:
    """The density the PRE-14.3 detector computed for the same span — the live RED arm.

    Derived from the shipped predicate with this story's names withheld, rather than from a
    transcribed copy of the old table: a transcribed copy would assert the tester's memory of
    what the detector used to do.
    """
    span = [
        e for e in entry.edges if definition.start_line <= e.line <= definition.end_line
    ]
    before = sum(
        1
        for e in span
        if is_assertion_callee(e.callee) and e.callee not in _STORY_14_3_NAMES
    )
    return Fraction(before, score.statement_count) if score.statement_count else Fraction(0)


def _was_flagged_before(score, entry, definition) -> bool:
    """Whether the PRE-14.3 detector flagged this span. Mirrors ``_score``'s own predicate."""
    return score.statement_count > 0 and (
        _density_without_story_14_3(score, entry, definition) < ASSERTION_DENSITY_FLOOR
        or score.mock_ratio > MOCK_RATIO_CEILING
    )


# ── The fixtures. Brace style is a VARIABLE here, never an accident ───────────────────────

_ALLMAN_JS = """function testAllman()
{
    const r = add(2, 3);
    expect(r).toBe(5);
}
"""

_ALLMAN_JS_NO_ASSERTION = """function testAllman()
{
    const r = add(2, 3);
}
"""

_ALLMAN_TS = """function testAllman(): void
{
    const r: number = add(2, 3);
    expect(r).toBe(5);
}
"""

_ALLMAN_TS_NO_ASSERTION = """function testAllman(): void
{
    const r: number = add(2, 3);
}
"""

_KANDR_JS = """function testAllman() {
    const r = add(2, 3);
    expect(r).toBe(5);
}
"""

_NODE_ASSERT_TS = """function testNodeAssert(): void
{
    const r: number = add(2, 3);
    equal(r, 5);
}
"""

_NODE_ASSERT_TS_NO_ASSERTION = """function testNodeAssert(): void
{
    const r: number = add(2, 3);
}
"""

_JEST_SPY_TS = """function testSpy(): void
{
    const spy = makeSpy();
    run(spy);
    expect(spy).toHaveBeenCalledWith(1);
}
"""

_JEST_SPY_TS_NO_ASSERTION = """function testSpy(): void
{
    const spy = makeSpy();
    run(spy);
}
"""


# ── -123: the surviving false accusation, in JavaScript ───────────────────────────────────


def test_an_allman_brace_js_test_with_a_real_assertion_is_not_flagged(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-123 — AC1.1/1.2: the false accusation, RED then closed.

    **Observable:** a JavaScript test whose brace sits on its own line and whose body holds a
    real ``expect(r).toBe(5)`` — flagged heuristically vacuous before Story 14.3, clean after,
    while its byte-identical assertion-free twin stays flagged.

    **The RED is LIVE, not quoted.** ``_was_flagged_before`` recomputes the numerator with
    this story's names withheld and must report ``True``: if it ever stops doing so, the
    defect this case exists for is gone and the case is asserting nothing, which is the
    condition to re-derive it rather than to delete it.

    **Why both arms.** A one-directional check — "the JS test is no longer flagged" — passes
    just as well on a change that removed the flag by removing the CAPABILITY. The twin is
    what makes it falsifiable, and it is byte-identical but for the assertion line.
    """
    score, entry, definition = _score_one(tmp_path, "src/calc.test.js", _ALLMAN_JS)

    # THE RED — the defect, reproduced by execution on this run.
    assert _was_flagged_before(score, entry, definition) is True, (
        "the pre-14.3 numerator no longer flags this fixture, so this guard is now asserting "
        "nothing. Re-derive the mechanism and re-author the case with its reason — do NOT "
        "delete the arm (AI-E3-1)."
    )
    assert _density_without_story_14_3(score, entry, definition) == Fraction(0)

    # The index SAW the assertion the whole time. This is the crux of the whole story: the
    # defect was never a parsing failure, it was a VOCABULARY gap, and proving the edges were
    # present is what distinguishes those two diagnoses.
    span = {e.callee for e in entry.edges
            if definition.start_line <= e.line <= definition.end_line}
    assert {"expect", "toBe"} <= span, (
        f"the tree-sitter index did not emit `expect`/`toBe` for this fixture ({sorted(span)}), "
        "so this case would be measuring the PARSER rather than the assertion table"
    )

    # THE GREEN — and the denominator is genuinely non-zero, so the flag predicate was
    # actually reachable. Without this floor the case could pass by the §0.2 silence.
    assert score.statement_count > 0, (
        "non-vacuity: statement_count is 0, so `heuristically_vacuous` could not fire at all "
        "and this fixture proves nothing about the assertion table (the -125 trap)"
    )
    assert score.assertion_sites == 2
    assert score.assertion_density >= ASSERTION_DENSITY_FLOOR
    assert score.heuristically_vacuous is False

    # THE PRESERVED SIGNAL — the byte-identical twin, minus the assertion.
    twin, twin_entry, twin_def = _score_one(
        tmp_path, "src/empty.test.js", _ALLMAN_JS_NO_ASSERTION
    )
    assert twin.statement_count > 0 and twin.assertion_sites == 0
    assert twin.heuristically_vacuous is True, (
        "a genuinely assertion-free JavaScript test is no longer flagged, so the widening "
        "bought its precision by deleting the capability rather than by finding the "
        "assertions (-117's lesson, applied to the cross-language vocabulary)"
    )


# ── -124: the same, in TypeScript — the language the epic's claim is actually about ───────


def test_the_same_false_accusation_in_typescript(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-124 — AC1.4: TypeScript, not JavaScript alone.

    **Observable:** identical to ``-123`` over ``.test.ts`` and ``.spec.ts`` sources carrying
    TYPE ANNOTATIONS, which the JavaScript grammar cannot parse — so this genuinely exercises
    the TypeScript path rather than re-running ``-123`` under a different extension.

    Both ratified corpus members that motivated this story are TypeScript, and the epic's
    claim names TypeScript explicitly. Asserting it only in JavaScript would be testing the
    language the story is not about.
    """
    score, entry, definition = _score_one(tmp_path, "src/calc.test.ts", _ALLMAN_TS)

    assert _was_flagged_before(score, entry, definition) is True
    assert score.statement_count > 0
    assert score.assertion_sites == 2
    assert score.heuristically_vacuous is False

    twin, _, _ = _score_one(tmp_path, "src/empty.test.ts", _ALLMAN_TS_NO_ASSERTION)
    assert twin.statement_count > 0 and twin.assertion_sites == 0
    assert twin.heuristically_vacuous is True

    # `.spec.ts` is the other convention both members write, and it reaches the detector by a
    # different arm of `is_test_file` than `.test.ts` does.
    spec, spec_entry, spec_def = _score_one(tmp_path, "src/calc.spec.ts", _ALLMAN_TS)
    assert _was_flagged_before(spec, spec_entry, spec_def) is True
    assert spec.heuristically_vacuous is False

    # …and end to end, through the surface an operator actually runs.
    result = VacuousTestDetector().run(
        file_path="src/calc.test.ts", source=_ALLMAN_TS, ast_entry=entry
    )
    # NON-VACUITY (added by review iteration 2's sweep): "no findings" is also what a DEGRADED
    # run produces — `not_a_test_file`, `parse_failed`, `no_test_functions` all return early
    # with no findings — so the run must be shown to have actually examined the file.
    assert result.degraded == () and result.entries, (
        f"the detector degraded on this fixture instead of scoring it, so `findings == ()` "
        f"below would hold because nothing was examined ({result.degraded!r})"
    )
    assert result.findings == (), (
        "the shipped detector still emits a finding for a TypeScript test holding a real "
        "assertion — the exact false accusation Epic 14 exists to close"
    )


# ── -125: brace style is the variable, and the story's original fixture is UNFLAGGED for a
#          reason that is NOT this story's fix ────────────────────────────────────────────


def test_the_kandr_fixture_is_unflagged_because_its_statement_count_is_zero(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-DETECT-001-125 — AC1.3: the vacuously-true criterion, pinned as such.

    **Observable:** the byte-difference between the two fixtures is the position of ONE brace,
    and it decides whether the density predicate can fire at all.

    ⛔ **This is the case that stops Story 14.3's acceptance criterion being discharged by a
    no-op.** ``epics.md`` phrased the target as *"the JS fixture measured at FLAGGED is
    re-measured and is NOT flagged"*. Measured on the post-14.2 tree, that fixture scores
    ``statement_count == 0`` — 14.2's logical-statement scanner reads ``function f() {`` as
    one unclosed continued statement, so the body counts nothing — and
    ``heuristically_vacuous`` requires ``> 0``. The criterion was therefore **already true
    before this story existed** and would have passed with zero code change: a criterion
    satisfied by a defect that MOVED rather than by a fix (``AI-E3-1``).

    So the mechanism is pinned here rather than remembered. The day the denominator changes
    again, this case says exactly which assumption moved — and ``-123``'s non-vacuity floor
    (``statement_count > 0``) is what stops that change from silently hollowing out this
    story's real guard.
    """
    kandr, kandr_entry, kandr_def = _score_one(tmp_path, "src/kandr.test.js", _KANDR_JS)
    allman, _, _ = _score_one(tmp_path, "src/allman.test.js", _ALLMAN_JS)

    assert kandr.statement_count == 0, (
        "the K&R fixture's body now counts statements, so 14.2's denominator has changed "
        "shape. Re-derive Story 14.3's §0.2 before trusting any acceptance figure that rests "
        "on this fixture being silent."
    )
    assert kandr.heuristically_vacuous is False
    # …and it is silent for the DENOMINATOR's reason, not this story's: the pre-14.3
    # numerator does not flag it either.
    assert _was_flagged_before(kandr, kandr_entry, kandr_def) is False

    # One brace moves, and the predicate becomes reachable.
    assert allman.statement_count > 0
    assert _KANDR_JS.replace("() {", "()\n{") == _ALLMAN_JS, (
        "non-vacuity: the two fixtures must differ ONLY in brace placement, or this case is "
        "comparing two unrelated programs"
    )


# ── -126: the vocabulary families the ratified members actually write ─────────────────────


def test_the_node_assert_and_jest_spy_families_are_recognised(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-126 — AC2.2: the names the corpus writes, both directions.

    **Observable:** the two dominant idioms of the two ratified TypeScript members —
    ``node:assert``'s ``equal`` (measured **1548** call edges in agent-smith) and Jest's
    ``toHaveBeenCalledWith`` (measured **696** in xagents-webapp) — each lift a test out of
    the flag, and each twin without them stays flagged.

    ⚠️ **``epics.md``'s minimum list covers NEITHER of these**, which is why AC2.2 requires
    the vocabulary to be measured rather than copied. Its JS/TS list —
    ``expect``/``toBe``/``toEqual``/``toThrow``/``assert``/``ok``/``deepStrictEqual`` — misses
    the ``toHaveBeenCalled`` family entirely and all of ``node:assert``'s core but one. A
    detector shipped against the minimum alone would still have falsely accused the dominant
    shape of both members. The minimum is a FLOOR, not a specification (DN-14-3-2).
    """
    for relative, source, twin_path, twin_source, expected in (
        ("src/na.test.ts", _NODE_ASSERT_TS, "src/na2.test.ts", _NODE_ASSERT_TS_NO_ASSERTION, 1),
        ("src/spy.test.ts", _JEST_SPY_TS, "src/spy2.test.ts", _JEST_SPY_TS_NO_ASSERTION, 2),
    ):
        score, entry, definition = _score_one(tmp_path, relative, source)
        assert _was_flagged_before(score, entry, definition) is True, (
            f"{relative} was not falsely flagged before the widening, so it is not evidence "
            f"for it"
        )
        assert score.statement_count > 0
        assert score.assertion_sites == expected
        assert score.heuristically_vacuous is False

        twin, _, _ = _score_one(tmp_path, twin_path, twin_source)
        assert twin.assertion_sites == 0 and twin.heuristically_vacuous is True


# ── -127: the excluded names, and the flat/language-agnostic contract ─────────────────────


def test_the_dangerous_names_are_excluded_and_the_table_stays_flat() -> None:
    """TC-ArgusAgent-DETECT-001-127 — AC2.3/2.5/2.6: exclusions are decisions, not omissions.

    **Observable:** ``match``, ``doesNotMatch`` and ``objectContaining`` are absent from BOTH
    tables, and both tables are flat ``frozenset``s of plain ``str``.

    ⛔ **``match`` (measured 469 in agent-smith) and ``doesNotMatch`` (76) are the dangerous
    pair.** ``re.match`` in Python and ``String.prototype.match`` in JavaScript are pervasive
    **non**-assertions. Their error direction is flag-REDUCING, so they cannot manufacture an
    accusation — but they would silently suppress **real** flags on Python code, which is a
    recall regression wearing a precision fix's clothes. The accepted-collision argument that
    carries ``expect`` does not carry these: ``expect`` has no common non-assertion meaning
    and ``match`` has one in both languages that matter.

    ``objectContaining`` (measured 376) is excluded for a different reason: it builds an
    ARGUMENT to a matcher (``expect(x).toEqual(expect.objectContaining({…}))``), so it is
    never itself the assertion, and admitting it would count one assertion twice.

    **AC2.5 — the table stays FLAT.** NFR-P2 confines the language conditional to
    ``argus/index/``. The two tables here are partitioned by QUESTION, never by LANGUAGE
    (DN-14-2-4), so no language field, per-language sub-table or grouping key may enter the
    detector. The groupings in the source are COMMENTS, and this is what holds that true.
    """
    for excluded in ("match", "doesNotMatch", "objectContaining", "Error"):
        assert excluded not in _ASSERTION_CALLEES, (
            f"{excluded!r} entered the density vocabulary. If that is intended it needs a "
            f"MEASURED statement of how many real Python flags it removes across all three "
            f"pinned members, and that number must be 0 (AC2.3) — see DN-14-3-5 for the rule "
            f"and the measurement that decides every name in this table."
        )
        assert excluded not in _CORROBORATION_ASSERTION_CALLEES

    for table in (_ASSERTION_CALLEES, _CORROBORATION_ASSERTION_CALLEES):
        assert isinstance(table, frozenset)
        assert all(isinstance(name, str) and name for name in table)

    # AC2.4 — already present, not added again, and the frozen table is untouched at 23.
    assert {"assertTrue", "fail"} <= _CORROBORATION_ASSERTION_CALLEES
    assert len(_CORROBORATION_ASSERTION_CALLEES) == 23
    # AC4.1 — the thresholds did not move, and they are exact Fractions (AR4).
    assert ASSERTION_DENSITY_FLOOR == Fraction(1, 4)
    assert MOCK_RATIO_CEILING == Fraction(1, 2)
    assert isinstance(ASSERTION_DENSITY_FLOOR, Fraction)
    assert isinstance(MOCK_RATIO_CEILING, Fraction)
    # Non-vacuity: the widening actually happened, in the direction claimed.
    assert len(_ASSERTION_CALLEES) >= 88
    assert _STORY_14_3_NAMES <= _ASSERTION_CALLEES
    assert not (_STORY_14_3_NAMES & _CORROBORATION_ASSERTION_CALLEES)


# ── -133: DN-14-3-5 — the collision rule, applied to every name and not just to `match` ────


def test_the_collision_rule_is_applied_to_every_name_not_only_to_match(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-DETECT-001-133 — AC2.3/2.6 / DN-14-3-5: the exclusion principle, uniform.

    **Observable:** a Python test whose only call besides the SUT is ``Error("bad")`` is
    flagged heuristically vacuous — because ``Error`` is NOT in the density vocabulary — while
    the same shape written with ``ok`` / ``equal`` / ``Equal`` / ``throws`` / ``rejects`` is
    not, which is this table's accepted collision cost stated as an EXECUTABLE fact.

    ⚠️ **WHY THIS CASE EXISTS: iteration 1 applied DN-14-3-2's collision test to
    ``match``/``doesNotMatch`` and to nothing else.** Six of the thirty-six names it shipped
    are ordinary non-assertion identifiers in the *other* language — an exclusion principle
    applied to one name and not to its neighbours is not a principle, it is a preference. The
    error direction is flag-REDUCING, so none of it could manufacture a false 🔴 (the
    corroboration path reads the FROZEN table by name, DN-14-2-1, and
    ``_CORROBORATION_ASSERTION_CALLEES`` is byte-unchanged at 23) — but a name that wrongly
    counts as an assertion RAISES density and REMOVES a flag, which is silent recall loss on
    the language 4,745 of the corpus's 4,746 scored test functions are written in.

    **The rule is DN-14-3-5 and it is arithmetic, not taste** — admit when the measured Python
    collision is materially below the measured JS/TS benefit. ``Error`` measures **164** Python
    call sites (CPython's own ``wave``/``aifc``/``sunau`` each define ``class
    Error(Exception)``; mypy's ``stubtest`` yields ``Error(...)``) against a benefit measured at
    **zero** — Go's ``t.Error`` is unreachable by two independent barriers (``DF-14-3-A``,
    ``DF-14-3-B``) and JS/TS spells the non-assertion ``throw new Error(...)``. It is dropped.
    ``ok`` (10 vs 764) and ``equal`` (34 vs 1,548) are KEPT: they carry ``node:assert``, the
    whole harness of a ratified corpus member, and dropping them would re-open the very false
    accusation this story closes.

    ⛔ **The kept names' cost is asserted here rather than written in a comment**, which is the
    difference between a recorded decision and a remembered one. If a later story removes
    ``ok``/``equal`` this case goes red and forces the trade to be re-derived; if one re-adds
    ``Error`` for symmetry with the rest of the Go family, the first arm goes red.
    """
    # ── THE FIX, and its RED is live: this fixture scored `heuristically_vacuous=False` on
    # the table iteration 1 shipped, and a genuinely assertion-free Python test went unflagged.
    dropped, entry, definition = _score_one(
        tmp_path, "tests/test_error.py", _PY_COLLISION.format(call='Error("bad")')
    )
    span = {e.callee for e in entry.edges
            if definition.start_line <= e.line <= definition.end_line}
    assert {"Error", "compute"} <= span, (
        f"non-vacuity: the index did not emit `Error` as a callee for this fixture "
        f"({sorted(span)}), so the collision this case is about is not even reachable and the "
        f"assertion below would hold for the wrong reason"
    )
    assert dropped.statement_count > 0, "non-vacuity: the flag predicate must be reachable"
    assert dropped.assertion_sites == 0
    assert is_assertion_callee("Error") is False, (
        "`Error` counts as an assertion again. It measures 164 Python call sites against a "
        "JS/TS benefit of ZERO — Go's `t.Error` never reaches the edge set (DF-14-3-B) and no "
        "Go test is scored at all (DF-14-3-A) — so it removes real Python flags and buys "
        "nothing. Do NOT re-add it for symmetry with Fatal/Fatalf/Errorf/NoError/Equal; that "
        "asymmetry is DN-14-3-5's decision."
    )
    assert dropped.heuristically_vacuous is True, (
        "a Python test with no assertion at all is unflagged because a name in the density "
        "table collided with an ordinary identifier — silent recall loss, the defect "
        "DN-14-3-5 exists to bound"
    )

    # ── THE CONTROL. The same fixture with no second call is flagged for the same reason, so
    # the arm above is measuring the NAME and not the fixture's shape.
    control, _, _ = _score_one(
        tmp_path, "tests/test_control.py", _PY_COLLISION.format(call="pass")
    )
    assert control.statement_count == dropped.statement_count
    assert control.assertion_sites == 0 and control.heuristically_vacuous is True

    # ── THE ACCEPTED COST, made executable. Each of these IS admitted, each therefore DOES
    # un-flag a synthetic Python collision, and the decision rests on the measured RARITY of
    # that shape rather than on it being impossible. Recorded so it can never be discovered
    # again as if it were news.
    for name, call, measured in (
        ("ok", "ok(result)", "10 py sites vs 764 js edges"),
        ("equal", "equal(result, 5)", "34 vs 1,548"),
        ("Equal", "Equal(result, 5)", "0 vs 0 — inert, DN-14-3-3"),
        ("throws", "throws(compute)", "0 vs 19"),
        ("rejects", "rejects(result)", "0 vs 1"),
    ):
        assert name in _ASSERTION_CALLEES, (
            f"{name!r} left the density vocabulary. DN-14-3-5 admitted it on a measured "
            f"benefit/cost of {measured}; removing it re-opens the false accusation for that "
            f"idiom, so it needs its own measured argument and a recorded reason."
        )
        cost, _, _ = _score_one(
            tmp_path, f"tests/test_cost_{name}.py", _PY_COLLISION.format(call=call)
        )
        assert cost.statement_count == control.statement_count
        assert cost.assertion_sites == 1 and cost.heuristically_vacuous is False, (
            f"the accepted collision cost of {name!r} no longer reproduces, so either the "
            f"name left the table or the numerator changed shape. Re-derive DN-14-3-5's "
            f"measurement — do not simply update the expectation."
        )

    # ⛔ And the whole of it is contained: none of this can reach a verdict, because the
    # corroboration path does not read this table at all (DN-14-2-1). That containment is what
    # makes the finding High rather than Critical, and it is asserted rather than assumed.
    assert dropped.ast_corroborated is False
    assert not (_STORY_14_3_NAMES & _CORROBORATION_ASSERTION_CALLEES)
    assert len(_CORROBORATION_ASSERTION_CALLEES) == 23


# ── -128: CRLF, on the cross-language path ────────────────────────────────────────────────


def test_a_crlf_typescript_source_scores_byte_identically(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-128 — AC7.1/7.4: line terminators cannot reach the score.

    **Observable:** the same TypeScript fixture written with ``\\r\\n`` and with ``\\n`` yields
    a byte-identical :class:`VacuousTestScore`.

    Local gates here run on Windows only and CI runs an ubuntu matrix; this repository has
    already shipped POSIX-only bugs out of a green Windows run (``AI-E13-1``). The detector
    reads the ``source.splitlines()`` list, which cannot carry a terminator — and Story 14.3
    re-anchored ``provenance_scan._ASSIGNMENT_RE`` from ``^``/``$`` to ``\\A``/``\\Z`` so the
    module's own platform-neutrality claim became true (``-130``). This case is what stops
    either property regressing silently.
    """
    lf = _ALLMAN_TS
    crlf = _ALLMAN_TS.replace("\n", "\r\n")
    assert "\r\n" in crlf and "\r" not in lf, "non-vacuity: the two inputs must really differ"

    lf_score, _, _ = _score_one(tmp_path, "src/lf.test.ts", lf)
    crlf_score, _, _ = _score_one(tmp_path, "src/crlf.test.ts", crlf)

    lf_fields = lf_score.model_dump(exclude={"test_name"})
    crlf_fields = crlf_score.model_dump(exclude={"test_name"})
    assert lf_fields == crlf_fields, (
        f"a CRLF TypeScript source scores differently from its LF twin: "
        f"{lf_fields!r} != {crlf_fields!r}"
    )
    assert lf_score.statement_count > 0, "non-vacuity: an all-zero score would match trivially"
    assert lf_score.assertion_sites == 2


# ── -129: Unicode-safe identifiers on the cross-language path ─────────────────────────────


def test_non_ascii_identifiers_are_matched_and_do_not_disturb_the_vocabulary(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-DETECT-001-129 — AC7.3: Unicode-safe name matching.

    **Observable:** a TypeScript test whose local names are Cyrillic still scores its
    assertion, and a project helper named ``assert_café_vide`` is still admitted by the
    naming-convention predicate.

    ``\\w`` is a Unicode class on ``str`` patterns, so this holds by construction — but the
    ``nonascii_unicode`` cartridge depends on it and construction is not evidence. The
    cross-language path is new ground for it, which is why it is re-asserted here.
    """
    source = (
        "function testЮникод(): void\n"
        "{\n"
        "    const результат: number = сложить(2, 3);\n"
        "    expect(результат).toBe(5);\n"
        "}\n"
    )
    # `_is_test_function` needs the lowercase `test` prefix; the Cyrillic is in the SUFFIX,
    # which is the part this case is about.
    score, entry, definition = _score_one(tmp_path, "src/uni.test.ts", source)
    assert score.statement_count > 0
    assert score.assertion_sites == 2
    assert score.heuristically_vacuous is False
    assert any("сложить" == e.callee for e in entry.edges), (
        "non-vacuity: the index did not emit the non-ASCII callee, so nothing Unicode was "
        "actually exercised"
    )

    assert is_assertion_callee("assert_café_vide") is True
    assert is_assertion_callee("_assert_один") is True
    assert is_assertion_callee("café") is False


# ── -130: the platform-neutrality claim is ENFORCED, not merely written ───────────────────


def test_provenance_scan_anchors_no_pattern_with_caret_or_dollar() -> None:
    """TC-ArgusAgent-DETECT-001-130 — AC7.1 / ``DF-14-2-B``: the docstring claim, made checkable.

    **Observable:** ``argus/detectors/provenance_scan.py`` contains no ``^``- or
    ``$``-anchored regular expression.

    That module's docstring has claimed *"no pattern below is anchored with ``$``"* since
    Story 14.1. **The claim was false when it was written**: ``_ASSIGNMENT_RE`` was
    ``^``/``$``-anchored the whole time (``DF-14-2-B``, filed by Story 14.2 against its own
    module). It was never exploitable — every call site passes a ``splitlines()``-derived
    line, which cannot carry a terminator — but ``$`` also matches immediately BEFORE a
    trailing ``\\n``, so on any future call site that forgot to strip one, a CRLF and an LF
    source would silently disagree.

    Story 14.3 re-anchored it to ``\\A``/``\\Z`` and **demonstrated the equivalence rather
    than asserting it**: both patterns were run over every line of every staged test file of
    all three pinned corpus members — 218,017 lines, of which 25,649 matched as assignments —
    with **0 disagreements** on the verdict or on either named group, and the flagged set of
    all three members byte-identical afterwards.

    This case exists so the claim cannot quietly become false a second time. A prose promise
    that nothing enforces is how it became false the first time — and **the sweep immediately
    earned its keep**: it found a SECOND ``^`` anchor (``_LEADING_CHAIN_RE``) that
    ``DF-14-2-B`` never named. That one is provably behaviour-neutral (``^`` without
    ``re.MULTILINE`` is exactly ``\\A``), which is precisely why reading the ledger entry
    alone would have left it in place.
    """
    source = Path(provenance_scan.__file__).read_text(encoding="utf-8")
    # Only the pattern strings, so prose in a docstring naming the anchors does not trip it.
    patterns = re.findall(r"re\.compile\(\s*((?:rf?\"[^\"]*\"\s*)+)", source)
    assert len(patterns) >= 4, (
        f"non-vacuity: only {len(patterns)} compiled pattern(s) were extracted from "
        f"provenance_scan.py, so this sweep would pass without observing anything"
    )
    offenders = [p for p in patterns if _anchors_on_caret_or_dollar(p)]
    assert not offenders, (
        "a `^`/`$`-anchored pattern is back in provenance_scan.py, contradicting that "
        "module's platform-neutrality docstring. Use `\\A`/`\\Z`, which no line terminator "
        f"can satisfy: {offenders!r}"
    )
    # POSITIVE CONTROLS — the sweep is watched FAILING, and watched not over-reaching. Both
    # matter: the version of this predicate written first reported `[^=]` as an anchor, which
    # would have been a false accusation inside the guard against false claims.
    assert _anchors_on_caret_or_dollar(r'rf"\s*(?P<value>.+)$"') is True
    assert _anchors_on_caret_or_dollar(r'rf"^({_IDENT})"') is True
    assert _anchors_on_caret_or_dollar(r'rf"(?::[^=]*?)?=(?!=)"') is False
    assert _anchors_on_caret_or_dollar(r'r"\A(?:except)\b.*:\Z"') is False


# ── -131: the moat, and why no JS/TS test can reach a verdict ─────────────────────────────


def test_a_javascript_test_cannot_reach_verdict_eligibility(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-131 — AC3.3/3.4 / §0.7: the widening cannot manufacture a 🔴.

    **Observable:** the MOST favourable JavaScript shape that could exist — Allman braces so
    the denominator is non-zero, an explicit ``Mock()`` by its Python name, a discarded SUT
    call, and a JS assertion referencing the mock — is **not corroborated**, and the shipped
    detector emits the ADVISORY rule for it.

    **This is the question Story 14.2's review raised, and it is answered by measurement.**
    The limitation is real: no non-Python test can reach verdict-eligibility. But it is **NOT
    caused by DN-14-2-1** — it holds even under a hypothetical one-table design carrying this
    story's full vocabulary, because ``_MOCK_CALLEES`` carries no non-Python mock constructor
    (``fn``, ``spyOn``, ``stub``, ``vi``, ``sinon`` are all absent; only ``Mock`` overlaps, by
    coincidence of spelling) and fact (b)'s assignment machinery is Python-syntax-shaped. So
    the split vocabulary is the OUTER of two independent barriers, and it is not an unrecorded
    trap 14.2 laid for 14.3.

    That bounds **Epic 15** and is filed in ``deferred-work.md`` with a named owner: a
    TypeScript bench member can contribute ADVISORY findings only, never a data point for the
    ≥80% precision gate. It is acceptable HERE on the locked asymmetry — a false 🔴 is the
    lethal failure, a real vacuous test left advisory is tolerable — because a blocking rule
    that cannot fire on JS/TS cannot make a false claim about JS/TS.

    ⛔ **RE-AUTHORED BY REVIEW ITERATION 2, BECAUSE THIS GUARD WAS ITSELF A VACUOUS TEST.**
    Iteration 1's fixture carried a widened-table assertion that cleared the density floor, so
    it scored ``heuristically_vacuous=False`` and ``_ast_corroborated`` returned at its very
    first line — ``if not heuristically_vacuous: return False`` — **before
    ``provenance_evidence`` was ever called.** The case asserted ``ast_corroborated is False``
    and got it for free, from the short-circuit rather than from the structural barrier it
    claimed to pin. A vacuous test inside the vacuous-test detector's own suite, in the epic
    built to stop exactly this: the strongest argument for the criterion there is.

    The conclusion survived — the mechanism does reproduce — so the fix is a NON-VACUITY FLOOR
    plus a fixture reshaped to reach the predicate through ``mock_ratio > MOCK_RATIO_CEILING``
    instead of through density. Note the ceiling is a STRICT ``>``, so a fixture sitting exactly
    ON the boundary fires nothing; the ratio is asserted, not assumed.

    And the mechanism is now asserted DIRECTLY rather than inferred from a ``False``: the same
    binding written in JavaScript and in Python is put through ``_mock_bound_names``, which
    finds nothing in ``const fake = Mock();`` and finds ``fake`` in ``fake = Mock()``. *That*
    is what "fact (b)'s assignment machinery is Python-syntax-shaped" means, measured.
    """
    source = (
        "function testMocky()\n"
        "{\n"
        "    compute([1, 2]);\n"
        "    const fake = Mock();\n"
        "    const other = Mock();\n"
        "    const third = Mock();\n"
        "    const fourth = Mock();\n"
        "    expect(fake.calculate).toHaveBeenCalled();\n"
        "}\n"
    )
    score, entry, definition = _score_one(tmp_path, "src/mocky.test.js", source)
    span = [e for e in entry.edges
            if definition.start_line <= e.line <= definition.end_line]

    # ── THE NON-VACUITY FLOOR, which is the whole point of this re-authoring. Without it the
    # case passes on the `if not heuristically_vacuous: return False` short-circuit and proves
    # nothing at all about the corroboration path (mirrors -115's own floor).
    assert score.statement_count > 0, "non-vacuity: the scorer must have reached the predicate"
    assert score.heuristically_vacuous is True, (
        f"this fixture no longer reaches the corroboration path — `_ast_corroborated` returns "
        f"False at its first line when `heuristically_vacuous` is False, so every assertion "
        f"below would hold WITHOUT `provenance_evidence` ever being called. Reshape the "
        f"FIXTURE, do not weaken the assertion (measured here: mock_ratio="
        f"{score.mock_ratio}, density={score.assertion_density})."
    )
    assert score.mock_ratio > MOCK_RATIO_CEILING, (
        "the flag must come from the MOCK ratio, because the density half is exactly what "
        "this story widened — and the ceiling is a strict `>`, so a fixture that drifts onto "
        "the boundary fires nothing and silently hollows this case out"
    )
    # …and fact (a) holds, so the call really does proceed to fact (b) rather than stopping at
    # `if not reaches_sut: return False` — the second short-circuit on the same path.
    sut_candidates = [
        e for e in span
        if e.callee not in _CORROBORATION_ASSERTION_CALLEES and e.callee not in _MOCK_CALLEES
    ]
    assert len(sut_candidates) >= 1, "non-vacuity: fact (a) must hold or fact (b) is never asked"

    # ── THE MECHANISM, asserted directly. `const fake = Mock();` binds no mock name because
    # the assignment machinery is Python-syntax-shaped; the identical Python binding does.
    js_bound = provenance_scan._mock_bound_names(
        source.splitlines(), definition.start_line, definition.end_line, _MOCK_CALLEES
    )
    python_twin = "def test_mocky():\n    fake = Mock()\n    fake.calculate()\n"
    py_bound = provenance_scan._mock_bound_names(
        python_twin.splitlines(), 1, 3, _MOCK_CALLEES
    )
    assert py_bound == frozenset({"fake"}), (
        f"non-vacuity: the Python control must bind its mock name, or the JavaScript result "
        f"below says nothing about SYNTAX SHAPE — it would just mean the helper is broken "
        f"({sorted(py_bound)!r})"
    )
    assert js_bound == frozenset(), (
        f"a JavaScript `const x = Mock()` now binds a mock name ({sorted(js_bound)!r}), so "
        f"fact (b)'s assignment machinery has stopped being Python-shaped. DF-14-3-D's "
        f"measurement — and the bound it puts on Epic 15 — must be re-derived."
    )

    # ── THE EVIDENCE, computed on the same span the detector computes it on, under BOTH
    # vocabularies. Both fact-(b) clauses measure False on JS input even under the one-table
    # design this story rejected, which is what exonerates DN-14-2-1.
    for label, table in (
        ("frozen", _CORROBORATION_ASSERTION_CALLEES),
        ("one-table hypothetical", _ASSERTION_CALLEES),
    ):
        evidence = provenance_scan.provenance_evidence(
            source.splitlines(),
            span,
            definition.start_line,
            definition.end_line,
            assertion_callees=table,
            mock_callees=_MOCK_CALLEES,
        )
        assert evidence.mock_referencing_assertions == 0, (
            f"a JavaScript assertion was read as mock-referencing under the {label} "
            f"vocabulary, so DF-14-3-D's structural barrier has moved"
        )
        assert not evidence.sut_result_is_discarded, (
            f"fact (b)'s discard clause now holds on JavaScript input under the {label} "
            f"vocabulary — re-derive DF-14-3-D before trusting the Epic 15 bound"
        )

    assert score.ast_corroborated is False, (
        "a JavaScript test became AST-corroborated, so the cross-language widening has "
        "reached the corroboration path. That is the false-🔴 channel DN-14-2-1 closes and "
        "the lethal failure class Epic 14 exists to prevent."
    )

    result = VacuousTestDetector().run(
        file_path="src/mocky.test.js", source=source, ast_entry=entry
    )
    assert len(result.findings) == 1, (
        f"non-vacuity: the shipped detector must actually emit the advisory finding for this "
        f"fixture, or the rule/advisory assertions below are quantified over nothing "
        f"({result.findings!r})"
    )
    for finding in result.findings:
        assert finding.rule_id == RULE_HEURISTIC, (
            "a JavaScript finding was promoted to verdict-eligible by Story 14.3's widening"
        )
        assert finding.depth_supported is None
        assert finding.advisory is True


# ── -132: what this story did NOT fix, pinned so it is a known limit ──────────────────────


def test_go_and_callback_suites_remain_out_of_scope(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-132 — §0.12: ``DF-14-3-A``/``-B``/``-C`` are cited, not fixed.

    **Observable:** a Go test and an idiomatic ``describe``/``it`` JavaScript suite are both
    SILENT after this story — no score, no flag, no finding.

    The Go names (``Fatal``, ``Fatalf``, ``Error``, ``Errorf``, ``NoError``, ``Equal``) ship
    and are **measurably inert**: ``_is_test_function`` requires a lowercase ``test`` prefix,
    so ``func TestAdd`` is never scored at all. They ship because ``epics.md`` names them,
    they cost nothing, and having them present removes one reason to re-open this table on
    the day the predicate does move (DN-14-3-3). **Recording them as inert is the point** —
    a future reader must not conclude Go was made to work here.

    ⛔ **And it names the trap.** ``DF-14-3-A`` (the case-sensitive prefix) MUST NOT be fixed
    alone: Go tests are silent *because* of it, and lowering the case-sensitivity while
    ``DF-14-3-B`` stands would score every Go test, find ``assertion_sites=0`` because B hides
    the selector-expression assertions, and FLAG it — converting harmless silence into a fresh
    false accusation across an entire language, inside the epic opened to stop them. A and B
    move together or not at all.

    ⚠️ **FLOORS ADDED BY REVIEW ITERATION 2**, found by sweeping this module for the defect
    ``-131`` was caught with. "Nothing was scored" is exactly what an UNPARSED file produces,
    so without a floor this case would have gone on passing if the Go or JavaScript grammar
    disappeared — silence for the wrong reason, which is the same failure as ``-131``'s. Each
    fixture must now be shown to have parsed, and each must be shown to be silent for its OWN
    named mechanism: the Go file yields a definition that the PREDICATE rejects (``DF-14-3-A``)
    and emits no ``Fatalf`` edge at all (``DF-14-3-B``, measured here rather than asserted from
    the ledger); the callback file yields the assertion EDGES with no definition to attach them
    to (``DF-14-3-C``).
    """
    _grammars_or_unevaluable()
    go_source = (
        "func TestAdd(t *testing.T)\n"
        "{\n"
        "\tr := add(2, 3)\n"
        "\tif r != 5 { t.Fatalf(\"bad\") }\n"
        "}\n"
    )
    callback_source = (
        "describe('calc', () => {\n"
        "    it('adds', () => {\n"
        "        const r = add(2, 3);\n"
        "        expect(r).toBe(5);\n"
        "    });\n"
        "});\n"
    )
    for relative, source, expected_definitions, expected_edges in (
        ("src/calc_test.go", go_source, ["TestAdd"], {"add"}),
        ("src/suite.test.js", callback_source, [], {"describe", "it", "expect", "toBe"}),
    ):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
        index = build_ast_index(tmp_path, (relative,))
        entry = {e.file_path: e for e in index.entries}[relative]

        # ── NON-VACUITY: the file PARSED. An unparsed file scores nothing either, and this
        # case must never be able to pass by the grammar going missing.
        assert entry.ast_eligible and not entry.parse_failed, (
            f"{relative} did not parse ({entry.parse_failure_reason!r}), so every 'nothing was "
            f"scored' assertion below would hold for a reason that has nothing to do with "
            f"DF-14-3-A/-B/-C. Fix the environment, do not relax the case."
        )
        assert [d.name for d in entry.definitions] == expected_definitions, (
            f"{relative} extracted {[d.name for d in entry.definitions]!r}, not "
            f"{expected_definitions!r} — the mechanism this case pins has changed shape"
        )
        assert expected_edges <= {e.callee for e in entry.edges}, (
            f"{relative} did not emit {sorted(expected_edges)} as call edges, so the index is "
            f"not seeing what this case says it sees"
        )

        scored = [d for d in entry.definitions if _is_test_function(d)]
        assert scored == [], (
            f"{relative} now yields scored test function(s) {[d.name for d in scored]!r}. If "
            f"that is intended, DF-14-3-A and DF-14-3-B must move TOGETHER — scoring these "
            f"while their assertions stay invisible manufactures a false accusation across a "
            f"whole language."
        )
        result = VacuousTestDetector().run(
            file_path=relative, source=source, ast_entry=entry
        )
        assert result.findings == ()
        # …and the silence is RECORDED with its cause rather than merely observed: the
        # detector degrades on `no_test_functions`, which is exactly DF-14-3-A / DF-14-3-C
        # speaking. A different reason here means a different mechanism.
        assert [c.reason for c in result.degraded] == ["no_test_functions"], (
            f"{relative} is now silent for a reason other than `no_test_functions` "
            f"({[c.reason for c in result.degraded]!r}) — re-derive DF-14-3-A/-C before "
            f"trusting this case"
        )

    # ── DF-14-3-B, MEASURED rather than quoted: the Go file's `t.Fatalf("bad")` is a selector
    # expression and never reaches the edge set at all. That is the half of the coupling that
    # makes fixing DF-14-3-A alone dangerous, so it is asserted where the warning is written.
    go_entry = {e.file_path: e for e in build_ast_index(
        tmp_path, ("src/calc_test.go",)).entries}["src/calc_test.go"]
    assert "Fatalf" not in {e.callee for e in go_entry.edges}, (
        "Go selector-expression calls now reach the edge set, so DF-14-3-B has moved. That "
        "unblocks DF-14-3-A — and the two must move together, in one deliberate change."
    )

    # Non-vacuity: the Go vocabulary really did ship, it is really inert, and the reason is
    # the PREDICATE rather than the table. ⛔ `Error` is deliberately NOT in this list; it was
    # dropped by DN-14-3-5 (164 measured Python collisions against zero benefit) and `-133`
    # holds it out.
    assert {"Fatal", "Fatalf", "Errorf", "NoError", "Equal"} <= _ASSERTION_CALLEES
    assert "Error" not in _ASSERTION_CALLEES
