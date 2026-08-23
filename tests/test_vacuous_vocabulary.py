"""Which callee names count as an assertion — the WIDE vocabulary, guarded (Story 16.6).

Verification area ArgusAgent-DETECT (``TC-ArgusAgent-DETECT-001-138``..``-144``).

WHY THIS MODULE EXISTS AT ALL
------------------------------
``argus/detectors/vacuous_vocabulary.py`` was carved out of ``vacuous_test.py`` by the
2026-08-22 cohesion split and shipped with **no test module mirroring it**. This module is
that mirror, and it makes the same argument the production split made: *"which names count
as an assertion?"* belongs in one readable place. Its subject is the WIDE table
(``_ASSERTION_CALLEES`` + the project-helper naming convention) — the density NUMERATOR —
and the FROZEN table's inertness under it.

⛔ **IT IS NOT IN ``tests/test_vacuous_density.py``, AND THAT IS A DECISION** (``DN-16-6-3``).
That module is subject-correct and stands at 1,159 of NFR-M1's 1,200, with ``DF-15-2-E``'s
cohesion-split trigger at **1,180** — 21 usable lines against a guard set many times that.
Using it would fire the split-first rule and drag a *test-module split into a
behaviour-change story*, which is precisely what that rule exists to prevent.
``tests/test_vacuous_cross_language.py`` was the closer call — it owns ``DN-14-3-5`` and
``-133`` — but its declared subject is the **cross-language** vocabulary and
``AssertionError`` is a **Python builtin**; filing a Python-only name under a cross-language
heading is how a module's subject dissolves. NFR-M1's remedy is *cohesion*, never free space.

WHAT STORY 16.6 CHANGED, AND WHY THESE GUARDS ARE THE ONLY THING THAT CAN SEE IT
---------------------------------------------------------------------------------
One name: ``"AssertionError"`` joined ``_ASSERTION_CALLEES`` (88 -> 89). ``raise
AssertionError("msg")`` is one of the most rigorous assertions a Python test can make — it is
what pytest's own assertion rewriting produces — and the vocabulary scored it as **zero**,
because a ``raise`` was not an assertion callee and ``\\A_?assert\\w*\\Z`` is CASE-SENSITIVE.

⛔ **The full pre-existing suite is IDENTICALLY GREEN with and without that name.** Measured:
every table invariant that closes over ``_ASSERTION_CALLEES`` asserts ``>= 88``, a
non-membership, a proper-subset relation or flatness, and 89 satisfies all of them. **A fix
no guard can see is a fix that can be silently reverted**, so every case below is written to
go RED under one mutation — *remove ``"AssertionError"`` from ``_ASSERTION_CALLEES``* — and
that mutation was executed, observed RED and restored while this module was written.

MEASURED BLAST RADIUS, recorded here because the number is counter-intuitive
-----------------------------------------------------------------------------
Over the 1,032 recorded ``vacuous_test_heuristic`` findings, read from their PINNED git
objects: **22 carry the idiom** (minions 12 + agent-smith 10; the other three ratified
members contribute ZERO), and the flagged count moves **1,032 -> 1,025**. ⚠️ **The delta is
-7, not -22.** The other 15 gain assertion sites but stay under the ``1/4`` floor, or are
flagged on the ``mock_ratio > 1/2`` limb this table cannot reach. Newly flagged: **0**, and
that is structural rather than lucky — ``assertion_sites`` can only RISE and the floor fires
from BELOW.

EVERY CASE CARRIES ITS NON-VACUITY PREAMBLE AND ITS PINNED CONTROL
-------------------------------------------------------------------
``AI-E11-1``: a case states that its population is non-empty and its seam reachable BEFORE it
asserts anything about it — the index really emitted the callee the case is about, and
``statement_count > 0``. And the **lockstep trap** has fired four times in this epic: a
fixture whose density moves because a ``raise`` line was added is a fixture in which the
numerator AND the denominator both moved, because ``_count_statements`` counts that ``raise``.
Every case therefore varies **only the callee name**, with ``statement_count`` asserted EQUAL
against a control — the shape ``-133`` established.

⛔ OUT OF SCOPE, CITED AND NOT TOUCHED
---------------------------------------
* ``_CORROBORATION_ASSERTION_CALLEES`` stays FROZEN at 23 names (``DN-14-2-1``). ``-142``
  asserts the containment rather than promising it.
* ``SECTION_5_CONDITIONS`` and ``GateDecision.precision_evaluable`` are NOT asserted here and
  ``argus.precision`` is deliberately NOT imported: ``tests/test_gate_breadth.py`` already
  owns that guard, and restating it here would fork one arithmetic across two modules (AR7).
* The BARE ``raise AssertionError`` (no parentheses) stays invisible — a decision measured at
  0 of 1,032, held by ``-141``, and filed as ``DF-16-6-B``.
"""

from __future__ import annotations

import importlib.util
from fractions import Fraction
from pathlib import Path

import pytest

from argus.detectors import vacuous_test as vacuous_test_module
from argus.detectors import vacuous_vocabulary as vocabulary_module
from argus.detectors.provenance_scan import provenance_evidence
from argus.detectors.vacuous_test import (
    _ASSERTION_CALLEES,
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
    ASSERTION_DENSITY_FLOOR,
    MOCK_RATIO_CEILING,
    VacuousTestDetector,
    _is_test_function,
    index_aligned_lines,
    is_assertion_callee,
)
from argus.index.ast_index import build_ast_index

#: The one name Story 16.6 admitted. Written once, read by every case, so a rename cannot
#: leave half this module asserting about a string that no longer exists.
_THE_NAME = "AssertionError"

#: The vocabulary as it stood BEFORE Story 16.6, derived from the SHIPPED table by removing
#: exactly the one name rather than transcribed from the story record — a transcribed copy
#: would assert the tester's memory of what the detector used to do (``-133``'s rule).
_PRE_16_6_TABLE = frozenset(_ASSERTION_CALLEES - {_THE_NAME})

#: The probe fixture: one SUT call, then ONE line that varies. ``statement_count`` is 2 for
#: every substitution, so the ONLY thing that can move ``heuristically_vacuous`` is whether
#: the callee counts as an assertion — which makes it a clean probe of the TABLE rather than
#: of the denominator (§2.5's lockstep trap, in the shape ``-133`` already uses).
_PROBE = "def test_probe():\n    compute(1)\n    {line}\n"


def _grammar_or_unevaluable() -> None:
    """Assert the Python grammar is present, as a NAMED outcome rather than a skip.

    ⛔ ``pytest.importorskip`` would be a FALSE GREEN. ``tree-sitter`` and
    ``tree-sitter-python`` are BASE dependencies (``pyproject.toml`` promoted them out of the
    optional ``[languages]`` extra at Story 12.5), so "absent" is a broken environment and not
    a supported configuration — and ``audit-ci.yml`` sets ``ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1``
    precisely so a missing grammar cannot be answered with a skip. A skipped case reads as a
    passing case in every summary that matters; an ``UNEVALUABLE`` failure reads as what it is.
    """
    missing = [
        name
        for name in ("tree_sitter", "tree_sitter_python")
        if importlib.util.find_spec(name) is None
    ]
    if missing:
        pytest.fail(
            f"UNEVALUABLE: {', '.join(missing)} is not importable, so nothing in this module "
            "measured anything and the one name Story 16.6 admitted is unwatched. These are "
            "BASE dependencies, not the optional `[languages]` extra, so this is a broken "
            "environment rather than a supported configuration, and it is reported as a "
            "FAILURE rather than a skip on purpose."
        )


def _score_one(root: Path, source: str, slug: str):
    """Score the single test function in *source* through the REAL 1.4 index.

    Returns ``(VacuousTestScore, AstIndexEntry, Definition)``. The edge set is whatever
    tree-sitter actually emits, never a hand-built list — every claim in this module is about
    how the SHIPPED detector reads real source text, and a hand-built list would assert the
    tester's belief about that instead. ``index_aligned_lines`` is the Story 15.2 contract:
    the detector's line decomposition IS the index's, not ``str.splitlines``.
    """
    _grammar_or_unevaluable()
    relative = f"tests/test_{slug}.py"
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8", newline="")
    index = build_ast_index(root, (relative,))
    entry = {e.file_path: e for e in index.entries}[relative]
    assert not entry.parse_failed and entry.ast_eligible, (
        f"{slug!r} did not parse: {entry.parse_failure_reason!r}"
    )
    definitions = [d for d in entry.definitions if _is_test_function(d)]
    assert len(definitions) == 1, (
        f"{slug!r} must yield exactly ONE scored test function, got "
        f"{[(d.kind, d.name) for d in entry.definitions]!r}"
    )
    definition = definitions[0]
    score = VacuousTestDetector()._score(index_aligned_lines(source), entry.edges, definition)
    return score, entry, definition


def _span_callees(entry, definition) -> set[str]:
    """The callees the REAL index emitted inside *definition*'s span. The non-vacuity floor."""
    return {
        e.callee for e in entry.edges if definition.start_line <= e.line <= definition.end_line
    }


def _score_under(monkeypatch, table, root: Path, source: str, slug: str):
    """Score *source* with the wide vocabulary REPLACED by *table*, at the real seam.

    Patches the module global :func:`is_assertion_callee` actually reads, so the comparison
    runs the SHIPPED predicate over a different table rather than a reimplementation of it.
    """
    monkeypatch.setattr(vocabulary_module, "_ASSERTION_CALLEES", table)
    try:
        return _score_one(root, source, slug)
    finally:
        monkeypatch.undo()


# ── -138: the primary recognition ─────────────────────────────────────────────────────────


def test_a_test_whose_only_assertion_is_a_raise_is_no_longer_flagged(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-138 — AC1.1/AC1.2/AC5.1: ``raise AssertionError`` asserts.

    **Observable:** for a Python test whose only assertion is ``raise AssertionError("…")``,
    ``assertion_sites`` is **1**, ``assertion_density`` clears the ``1/4`` floor, and
    ``heuristically_vacuous`` is **False** — where the 88-name table scored it ``0 / 0 /
    True`` and falsely accused a rigorously-asserting test.

    **The defect MOVES the observable, at the real seam.** The pre-16.6 arm below is the
    SHIPPED predicate run over the SHIPPED table minus one name, through a real
    ``build_ast_index`` and the real scorer — not a reconstruction. It reproduces the false
    accusation on every run.

    **The control** is the byte-identical fixture with the ``raise`` line replaced by ``pass``:
    its ``statement_count`` is asserted EQUAL and it stays flagged, so this case measures the
    NAME and not the fixture's shape (the lockstep trap, §2.5).
    """
    source = _PROBE.format(line='raise AssertionError("a bad verdict must raise")')
    score, entry, definition = _score_one(tmp_path, source, "raise_assertion_error")

    # ── NON-VACUITY FIRST (AI-E11-1): the seam this case is about must be reachable.
    span = _span_callees(entry, definition)
    assert {_THE_NAME, "compute"} <= span, (
        f"non-vacuity: the index emitted {sorted(span)} for this fixture, so the "
        f"`{_THE_NAME}` call edge this whole story depends on is not even present and every "
        f"assertion below would hold for the wrong reason"
    )
    assert score.statement_count > 0, (
        "non-vacuity: `heuristically_vacuous` requires statement_count > 0, so a zero "
        "denominator would make the flag predicate unreachable and this case silent"
    )

    # ── THE FIX.
    assert is_assertion_callee(_THE_NAME) is True, (
        f"`{_THE_NAME}` no longer counts as an assertion. It was admitted under DN-14-3-5 on "
        f"a measured 182 in-`raise` sites against 2 non-`raise` collisions (91x) over 5,086 "
        f"Python files, and it un-flags 7 of the 1,032 recorded findings. Removing it "
        f"re-opens a false accusation against every test that asserts by raising."
    )
    assert score.assertion_sites == 1
    assert score.assertion_density >= ASSERTION_DENSITY_FLOOR
    assert score.heuristically_vacuous is False, (
        "a Python test whose contract assertion is `raise AssertionError(...)` is flagged "
        "vacuous — the accusation direction, and the defect Story 16.6 closes"
    )

    # ── THE DEFECT, REPRODUCED LIVE. Same fixture, same seam, one name withheld.
    before, _, _ = _score_under(
        pytest.MonkeyPatch(), _PRE_16_6_TABLE, tmp_path, source, "raise_assertion_error_pre"
    )
    assert before.statement_count == score.statement_count, (
        "the pre-16.6 arm must differ ONLY in the vocabulary; a moved denominator would make "
        "this a comparison of two fixtures rather than of two tables"
    )
    assert before.assertion_sites == 0 and before.heuristically_vacuous is True, (
        "the false accusation this story closes no longer reproduces on the 88-name table, "
        "so the arm above is passing for some other reason"
    )

    # ── THE CONTROL: same shape, no assertion. Still flagged, under BOTH tables.
    control, _, _ = _score_one(tmp_path, _PROBE.format(line="pass"), "raise_control")
    assert control.statement_count == score.statement_count, (
        f"the control's denominator moved ({control.statement_count} vs "
        f"{score.statement_count}), so the case above measured the fixture's SHAPE rather "
        f"than the callee NAME — the lockstep trap this epic has hit four times"
    )
    assert control.assertion_sites == 0 and control.heuristically_vacuous is True


# ── -139: nothing is counted twice ────────────────────────────────────────────────────────


def test_the_raise_form_is_counted_once_and_composes_with_a_bare_assert(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-DETECT-001-139 — AC2.3/AC2.4/AC5.3: the double-count trap, closed.

    **Observable:** ``assertion_sites`` is **1** for a span holding exactly one
    ``raise AssertionError("x")``, and **2** for a span holding one bare ``assert`` and one
    ``raise AssertionError("x")``.

    **Why this is the most consequential case in the module.**
    ``assertion_sites = assertion_call_sites + bare_asserts`` runs TWO independent counters
    over the same span: one over the index's call EDGES, one over the SOURCE LINES. The
    ``raise AssertionError("msg")`` form already emits an edge, so the table entry counts it
    once — but a future "completeness" change adding a ``raise``-matching LINE scanner would
    count all 22 corpus findings TWICE and inflate the numerator. A ``2`` in the first arm is
    exactly that regression, and this case is what stops it landing silently.

    ⚠️ **The second arm asserts on ``assertion_sites``, NOT on the flag.** ``1/3`` already
    clears the ``1/4`` floor, so ``heuristically_vacuous`` is ``False`` in BOTH columns there
    and a case written against a flag flip would be vacuous — §2.5's lockstep trap in its
    cheapest form. The flag is asserted only where it actually moves.
    """
    # ── ARM 1: the raise alone. ONE, not two.
    solo_source = _PROBE.format(line='raise AssertionError("x")')
    solo, entry, definition = _score_one(tmp_path, solo_source, "count_once")
    assert _THE_NAME in _span_callees(entry, definition), (
        "non-vacuity: no `AssertionError` edge, so there is nothing that COULD be "
        "double-counted and this arm would pass trivially"
    )
    assert solo.statement_count == 2 and solo.assertion_sites == 1, (
        f"`raise AssertionError(\"x\")` scored {solo.assertion_sites} assertion site(s). A 2 "
        f"means the edge path AND a source-line scanner both counted it — the double count "
        f"DN-16-6-2 rejected, which inflates the numerator for all 22 corpus findings."
    )
    assert solo.assertion_density == Fraction(1, 2)
    assert solo.heuristically_vacuous is False

    # ── ARM 2: a bare `assert` AND a raise. The two counters compose without overlapping.
    mixed_source = (
        "def test_probe():\n"
        "    r = compute(1)\n"
        "    assert r\n"
        '    raise AssertionError("x")\n'
    )
    mixed, mixed_entry, mixed_definition = _score_one(tmp_path, mixed_source, "count_composes")
    assert _THE_NAME in _span_callees(mixed_entry, mixed_definition)
    assert mixed.statement_count == 3, (
        "non-vacuity: the denominator must be the one this arm was measured against, or the "
        "density below is a claim about a different fixture"
    )
    assert mixed.assertion_sites == 2, (
        f"one bare `assert` plus one `raise AssertionError(...)` scored "
        f"{mixed.assertion_sites}. A 1 means one counter stopped seeing its half; a 3 means "
        f"the raise was counted by both."
    )
    assert mixed.assertion_density == Fraction(2, 3)

    # ── THE CONTROL for arm 2, with the denominator PINNED: the same three statements with
    # the raise replaced by a non-assertion call. The numerator drops by exactly one and
    # `statement_count` does not move, so the delta is the NAME rather than the line.
    control_source = (
        "def test_probe():\n"
        "    r = compute(1)\n"
        "    assert r\n"
        "    use(r)\n"
    )
    control, _, _ = _score_one(tmp_path, control_source, "count_control")
    assert control.statement_count == mixed.statement_count
    assert control.assertion_sites == 1, (
        "the control must lose exactly the raise's contribution; anything else means the two "
        "fixtures differ in more than the callee name"
    )


# ── -140: the accepted collision cost, made executable ────────────────────────────────────


def test_the_accepted_collision_cost_of_admitting_assertion_error_is_asserted(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-DETECT-001-140 — AC5.2/AC1.5: DN-14-3-5's cost, by execution.

    **Observable:** a fixture in which ``AssertionError("x")`` appears **outside** a ``raise``
    scores ``assertion_sites == 1`` and is NOT flagged, where the 88-name table scored it
    ``0`` and flagged it. That is the price of admitting the name, and it is asserted here so
    it can never be re-discovered later as if it were news — recording an accepted cost in
    prose ALONE was the mistake ``-133``'s own docstring exists to stop repeating.

    **The measured trade DN-14-3-5 accepted**, re-derived with stdlib ``ast`` (never Argus's
    own index — deriving a collision argument from the thing under test is circular) over
    **5,086** unique ``*.py`` paths: **182** in-``raise`` sites against **2** non-``raise``
    sites, **91x**. The two collisions are NAMED rather than summarised:
    ``site-packages/stevedore/tests/test_extension.py:118``, and Argus's own
    ``tests/test_open_llm_adapter.py:391`` — ``post_error=AssertionError("must not POST")``,
    an ``AssertionError`` CONSTRUCTED as a tripwire for a fake to raise later, which is still
    an assertion device. Both error directions here are flag-REDUCING.

    ⚠️ **THE REGISTER OF ACCEPTED COLLISION COSTS IS NOW IN TWO PLACES.**
    ``tests/test_vacuous_cross_language.py::…-133`` holds the five cross-language names
    (``ok``, ``equal``, ``Equal``, ``throws``, ``rejects``); ``AssertionError`` is the SIXTH
    admitted name and its cost is registered HERE, because it is a Python builtin and ``-133``
    is the cross-language module (``DN-16-6-3``). Neither case is the complete register on its
    own, and each points at the other so an auditor reading one cannot under-count.
    """
    source = "def test_probe():\n    compute(1)\n    e = AssertionError(\"x\")\n    use(e)\n"
    cost, entry, definition = _score_one(tmp_path, source, "collision_cost")

    span = _span_callees(entry, definition)
    assert {_THE_NAME, "compute", "use"} <= span, (
        f"non-vacuity: the index emitted {sorted(span)}, so the constructor call this case "
        f"prices is not in the edge set and the cost below is not the one being paid"
    )
    assert cost.statement_count == 3 and cost.statement_count > 0

    assert cost.assertion_sites == 1, (
        "an `AssertionError` CONSTRUCTED outside a `raise` no longer counts. That is the "
        "collision DN-14-3-5 priced at 2 sites against 182 (91x) and ACCEPTED; if it has "
        "changed, re-derive the census — do not simply update this expectation."
    )
    assert cost.heuristically_vacuous is False, (
        "the accepted cost is that this synthetic shape DOES un-flag. It is accepted on the "
        "measured RARITY of the shape, not on it being impossible, and it is asserted rather "
        "than remembered."
    )

    # ── THE CONTROL, denominator PINNED: the same three statements with the constructor
    # replaced by a plain call. Same statement_count, no assertion, still flagged.
    control, _, _ = _score_one(
        tmp_path,
        "def test_probe():\n    compute(1)\n    e = build(\"x\")\n    use(e)\n",
        "collision_control",
    )
    assert control.statement_count == cost.statement_count, (
        "the control's denominator moved, so this case measured the fixture's SHAPE rather "
        "than the callee NAME"
    )
    assert control.assertion_sites == 0 and control.heuristically_vacuous is True

    # ── THE COST IS THE NAME'S, not the fixture's: withhold the one name at the real seam
    # and the same fixture is flagged again.
    before, _, _ = _score_under(
        pytest.MonkeyPatch(), _PRE_16_6_TABLE, tmp_path, source, "collision_cost_pre"
    )
    assert before.assertion_sites == 0 and before.heuristically_vacuous is True


# ── -141: the bare-`raise` residual, recorded as a DECISION ───────────────────────────────


def test_the_bare_raise_spelling_stays_invisible_by_measured_decision(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-DETECT-001-141 — AC5.4/``DN-16-6-2``: the residual, pinned.

    **Observable:** a fixture whose only assertion is ``raise AssertionError`` — **no
    parentheses** — still scores ``assertion_sites == 0`` and stays flagged, **identically
    under the 88-name and the 89-name table.**

    ⛔ **THIS IS A DECISION AND NOT AN OVERSIGHT, and the difference is measured.** The bare
    form is a ``Name``, not a ``Call``, so it emits **no edge** and no table entry can reach
    it. Closing it needs a source-LINE scanner, and over the ratified corpus that scanner buys
    exactly **ZERO**: the spelling census over all 1,032 recorded findings classified every
    ``ast.Raise`` in every flagged span and found **22 call-form / 0 bare**. Worse, a line
    scanner combined with the table entry would count all 22 call-form spans TWICE (``-139``).
    So: **do not "complete" this into a double count.** The residual is filed as ``DF-16-6-B``
    and this case is what keeps it a recorded decision rather than a gap.

    **The pinned control** is a ``pass``-bodied fixture scoring identically, so this case
    cannot pass by measuring the fixture's SHAPE instead of the NAME.
    """
    source = _PROBE.format(line="raise AssertionError")
    bare, entry, definition = _score_one(tmp_path, source, "bare_raise")

    # ── NON-VACUITY, in the direction this case actually needs: the fixture must really be
    # scored (a live `compute` edge, a live denominator) while the `AssertionError` edge is
    # genuinely ABSENT — that absence IS the observable.
    span = _span_callees(entry, definition)
    assert "compute" in span, (
        f"non-vacuity: the index emitted {sorted(span)} — the span was not scored at all, so "
        f"the absence below would be an absence of measurement rather than of an edge"
    )
    assert _THE_NAME not in span, (
        "the bare `raise AssertionError` DOES emit a call edge on this index after all. Then "
        "DN-16-6-2's premise has changed and the residual must be re-derived — and check "
        "-139 first, because a table entry would now count this spelling too."
    )
    assert bare.statement_count == 2 and bare.statement_count > 0

    assert bare.assertion_sites == 0 and bare.heuristically_vacuous is True

    # ── AND IDENTICALLY UNDER THE PRE-16.6 TABLE. Both columns the same is the point.
    before, _, _ = _score_under(
        pytest.MonkeyPatch(), _PRE_16_6_TABLE, tmp_path, source, "bare_raise_pre"
    )
    assert (before.assertion_sites, before.heuristically_vacuous) == (
        bare.assertion_sites,
        bare.heuristically_vacuous,
    ), "the bare form moved under the widening, which is exactly what DN-16-6-2 says it cannot"

    # ── THE PINNED CONTROL: a `pass` body scores identically, so the case above is not
    # measuring the fixture's shape.
    control, _, _ = _score_one(tmp_path, _PROBE.format(line="pass"), "bare_raise_control")
    assert control.statement_count == bare.statement_count
    assert (control.assertion_sites, control.heuristically_vacuous) == (
        bare.assertion_sites,
        bare.heuristically_vacuous,
    )


# ── -142: containment — the frozen table and facts (a)/(b) do not move ────────────────────


def test_the_widening_cannot_reach_the_frozen_table_or_the_corroboration_facts(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-DETECT-001-142 — AC1.3/AC3.1/AC3.2/AC3.4: nothing is promoted.

    **Observable:** across a fixture set, ``ast_corroborated``, ``mock_ratio``, ``call_sites``
    and ``statement_count`` are **identical** under the 88-name and 89-name tables, and
    ``assertion_sites`` is **monotonically non-decreasing** — it never falls, and
    ``heuristically_vacuous`` never goes ``False -> True``.

    **Why the corroboration half is unreachable STRUCTURALLY**, not by luck: ``_sut_call_sites``
    filters on ``_CORROBORATION_ASSERTION_CALLEES``, ``_ast_corroborated`` passes that same
    FROZEN table into ``provenance_evidence``, ``mock_ratio`` reads ``_MOCK_CALLEES``,
    ``call_sites`` is ``len(span_edges)`` and ``statement_count`` is the source scanner. **None
    of the four reads the wide table** (``DN-14-2-1``). The measurement below is the check on
    that reading, not the argument for it.

    ⛔ **THE POPULATION IS ASSERTED NON-DEGENERATE FIRST, and this is the whole point of the
    case.** A fixture set in which ``ast_corroborated`` is ``False`` everywhere for an
    unrelated reason proves nothing — that is the ``AI-E3-1`` shape this project files rather
    than tolerates, and ``-131`` shipped as exactly that defect inside this very detector's
    own suite. So at least one fixture must corroborate ``True``, with fact (a), the discarded
    SUT result and a mock-referencing assertion each non-trivially exercised. ⚠️
    ``mock_referencing_assertions`` measures **0 across all 1,032** real findings, so a
    fixture is the ONLY way to reach a non-degenerate population here — expected, not a defect.
    """
    # ── NON-VACUITY OF THE COMPARISON ITSELF: the two tables must genuinely differ by the
    # one name, or every "identical under both" assertion below is a tautology.
    assert _ASSERTION_CALLEES - _PRE_16_6_TABLE == {_THE_NAME}, (
        f"non-vacuity: the shipped table and the pre-16.6 table differ by "
        f"{sorted(_ASSERTION_CALLEES - _PRE_16_6_TABLE)!r}, not by exactly "
        f"{{{_THE_NAME!r}}}, so this case is comparing a table against itself"
    )
    assert len(_ASSERTION_CALLEES) == 89 and len(_PRE_16_6_TABLE) == 88

    # ── AC1.3: the FROZEN table is untouched, by count AND by non-membership.
    assert len(_CORROBORATION_ASSERTION_CALLEES) == 23, (
        "the FROZEN corroboration vocabulary changed size. DN-14-2-1 pins it at Story 14.1's "
        "23 names: `provenance_scan` reads it in two places and BOTH move TOWARD an "
        "accusation when it widens. Story 16.6 widens the DENSITY table and this one only."
    )
    assert _THE_NAME not in _CORROBORATION_ASSERTION_CALLEES
    assert _CORROBORATION_ASSERTION_CALLEES < _ASSERTION_CALLEES, (
        "the frozen table must stay a PROPER subset of the wide one"
    )
    # AC1.6 — the neighbours this story must not have touched.
    assert len(_MOCK_CALLEES) == 10
    assert ASSERTION_DENSITY_FLOOR == Fraction(1, 4)
    assert MOCK_RATIO_CEILING == Fraction(1, 2)
    assert vocabulary_module._ASSERTION_NAMING_CONVENTION.pattern == r"\A_?assert\w*\Z", (
        "the project-helper convention regex moved. DN-16-6-1 REJECTED making it "
        "case-insensitive: that would admit `Assertion`, `AssertionRegistry`, `Asserter`, "
        "`ASSERT_MODE` and every other identifier starting with those nine letters, over an "
        "unbounded and unmeasured collision population. One measured name, not a looser regex."
    )

    #: The corroborating fixture: the SUT is called and its result DISCARDED, a `Mock()` is
    #: bound to `fake`, and the only assertion is a FROZEN-table callee referencing that
    #: mock-bound name. Every clause of fact (b) is live here.
    corroborating = (
        "def test_compute_calls_the_dependency():\n"
        "    compute([1, 2])\n"
        "    fake = Mock()\n"
        "    fake.calculate.return_value = 6\n"
        "    fake.calculate()\n"
        "    self.assertEqual(fake.calculate.call_count, 1)\n"
    )
    fixtures = {
        "corroborating": corroborating,
        "raise_form": _PROBE.format(line='raise AssertionError("x")'),
        "constructed": "def test_probe():\n    compute(1)\n    e = AssertionError(\"x\")\n    use(e)\n",
        "bare_form": _PROBE.format(line="raise AssertionError"),
        "mock_heavy": "def test_probe():\n    fake = Mock()\n    other = MagicMock()\n    fake.run()\n",
        "assertion_free": _PROBE.format(line="pass"),
    }

    corroborated_seen = 0
    for slug, source in fixtures.items():
        now, entry, definition = _score_one(tmp_path, source, f"contain_{slug}")
        before, _, _ = _score_under(
            pytest.MonkeyPatch(), _PRE_16_6_TABLE, tmp_path, source, f"contain_{slug}_pre"
        )
        assert now.statement_count > 0, f"non-vacuity: {slug!r} scored an empty denominator"

        # AC3.2 — the three untouched terms are byte-identical under both tables.
        assert (now.mock_ratio, now.call_sites, now.statement_count) == (
            before.mock_ratio,
            before.call_sites,
            before.statement_count,
        ), (
            f"{slug!r}: a term the wide table does not feed moved under the widening "
            f"({now.mock_ratio}/{now.call_sites}/{now.statement_count} vs "
            f"{before.mock_ratio}/{before.call_sites}/{before.statement_count}) — the "
            f"widening has reached something it must not read"
        )
        # AC3.1 — corroboration is unmoved.
        assert now.ast_corroborated == before.ast_corroborated, (
            f"{slug!r}: ast_corroborated moved under a DENSITY-table widening. The "
            f"corroboration path reads the FROZEN table and must be unreachable from here "
            f"(DN-14-2-1) — this is the false-🔴 class Epic 14 exists to close."
        )
        # AC3.4 — one-way, never toward an accusation.
        assert now.assertion_sites >= before.assertion_sites, (
            f"{slug!r}: assertion_sites FELL under a widening, which is arithmetically "
            f"impossible unless the numerator changed shape"
        )
        assert not (now.heuristically_vacuous and not before.heuristically_vacuous), (
            f"{slug!r}: a span became flagged that was not flagged before — the forbidden "
            f"direction. Measured 0 of 1,032 on the real corpus, and structurally impossible."
        )
        if now.ast_corroborated:
            corroborated_seen += 1
            # The population is non-degenerate BECAUSE each clause of fact (b) is live.
            span_edges = [
                e
                for e in entry.edges
                if definition.start_line <= e.line <= definition.end_line
            ]
            sut = VacuousTestDetector._sut_call_sites(span_edges)
            evidence = provenance_evidence(
                index_aligned_lines(source),
                span_edges,
                definition.start_line,
                definition.end_line,
                assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
                mock_callees=_MOCK_CALLEES,
            )
            assert len(sut) >= 1, "fact (a) is not exercised by the corroborating fixture"
            assert evidence.sut_result_is_discarded is True
            assert evidence.mock_referencing_assertions >= 1, (
                "the mock-referencing clause is not exercised, so `ast_corroborated` here is "
                "True for some other reason and the population is degenerate after all"
            )

    assert corroborated_seen >= 1, (
        "non-vacuity (AI-E11-1 / AI-E3-1): NOT ONE fixture corroborated, so every "
        "'ast_corroborated is unmoved' assertion above compared False against False and "
        "proved nothing. This is the exact shape `-131` shipped as, inside this detector's "
        "own suite, and it is a reason to go RED rather than a reason to pass."
    )


# ── -143: the re-export surface the cohesion split created ────────────────────────────────


def test_the_vacuous_test_re_export_surface_is_unchanged_and_shares_objects() -> None:
    """TC-ArgusAgent-DETECT-001-143 — AC6.4: the split's API promise, asserted.

    **Observable:** ``vacuous_test.__all__`` still carries **9** entries, and
    ``_ASSERTION_CALLEES``, ``_CORROBORATION_ASSERTION_CALLEES`` and ``is_assertion_callee``
    imported from ``argus.detectors.vacuous_test`` are the **SAME OBJECTS** (``is``, never
    ``==``) as the ones imported from ``argus.detectors.vacuous_vocabulary``.

    ⛔ **THIS IS THE SURFACE THAT BREAKS SILENTLY.** The 2026-08-22 cohesion split moved the
    tables out of ``vacuous_test.py`` and promised the move was *"re-exported, not relocated,
    from the caller's point of view"* — a maintainability act that may not become an API
    change in disguise. The follow-up commit then had to repair four currency guards the split
    re-armed. A shrunk ``__all__``, or a re-export rebound to a COPY of a frozenset rather than
    to the object itself, would leave every other guard in this story green while existing
    callers silently read a stale table.

    **The negative control makes the ``is`` check falsifiable**: a genuine COPY of the table
    compares ``==`` and fails ``is``, so ``is`` is demonstrably a stronger claim here rather
    than an incidentally-true one.

    ⚠️ Importing from ``argus.detectors.**`` is deliberate and is NOT the ``argus.precision``
    prohibition this module observes: ``SECTION_5_CONDITIONS`` and ``precision_evaluable``
    belong to ``tests/test_gate_breadth.py`` and are not restated here (AR7).
    """
    assert len(vacuous_test_module.__all__) == 9, (
        f"`vacuous_test.__all__` carries {len(vacuous_test_module.__all__)} entries, not 9. "
        f"The 2026-08-22 cohesion split promised the public surface was unchanged; a shrunk "
        f"__all__ is that promise breaking silently: {sorted(vacuous_test_module.__all__)!r}"
    )
    assert len(set(vacuous_test_module.__all__)) == len(vacuous_test_module.__all__)

    for name in ("_ASSERTION_CALLEES", "_CORROBORATION_ASSERTION_CALLEES", "is_assertion_callee"):
        via_host = getattr(vacuous_test_module, name)
        via_home = getattr(vocabulary_module, name)
        assert via_host is via_home, (
            f"`vacuous_test.{name}` is no longer the SAME object as "
            f"`vacuous_vocabulary.{name}`. A re-export rebound to a copy leaves both modules "
            f"answering 'which names count as an assertion?' from two tables that drift — the "
            f"AR7 defect, and invisible to every other guard in this story."
        )

    # ── THE NEGATIVE CONTROL: `is` really is stronger than `==` for these objects.
    # ⚠️ `frozenset(x)` RETURNS `x` when `x` is already a frozenset (a CPython interning
    # optimisation), so the obvious spelling of this control passes `is` and proves nothing.
    # Built through an intermediate iterable so the copy is genuinely a second object.
    copy = frozenset(sorted(vocabulary_module._ASSERTION_CALLEES))
    assert copy == vocabulary_module._ASSERTION_CALLEES
    assert copy is not vocabulary_module._ASSERTION_CALLEES, (
        "non-vacuity: a fresh frozenset compared identical BY IDENTITY, so the `is` checks "
        "above cannot distinguish a re-export from a copy and prove nothing"
    )
    # And the one name really is reachable through the re-export path.
    assert vacuous_test_module.is_assertion_callee(_THE_NAME) is True


# ── -144: the adversarial variants, GENERATED from the table ──────────────────────────────


def test_generated_near_miss_variants_of_every_admitted_name_are_rejected(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-DETECT-001-144 — AC5.6/AC1.4: the guard-adequacy clause's third part.

    **Observable:** every one of the **89** admitted names is recognised, and a variant set
    **GENERATED from that same table** — case-folded, case-raised and suffixed near misses —
    is rejected except where a variant is itself an admitted name or matches the documented
    project-helper convention. The generated population's size is asserted, so the sweep
    cannot go silent.

    **Why generated and not hand-listed.** A hand-listed adversarial set tests the names its
    author thought of. Closing the generator over ``_ASSERTION_CALLEES`` means the sweep grows
    with the table, and it is the check that would catch the ``DN-16-6-1`` alternative this
    story REJECTED: making ``_ASSERTION_NAMING_CONVENTION`` case-insensitive to admit
    ``AssertionError`` would also admit ``assertionerror``, ``ASSERTIONERROR``, ``Assertion``,
    ``AssertionRegistry`` and ``Asserter`` — an unbounded, unmeasured collision population.
    Every one of those is generated below and every one must be refused.

    The final arm takes it to the real seam: ``raise AssertionErrorish("x")`` emits an edge
    with a near-miss callee, and the scorer must still score that span as assertion-free.
    """
    assert len(_ASSERTION_CALLEES) == 89, (
        f"the wide vocabulary holds {len(_ASSERTION_CALLEES)} names, not 89. Story 16.6 took "
        f"it from 88 to 89 by admitting exactly `{_THE_NAME}`; any other size means a name "
        f"was added or dropped without a DN-14-3-5 measurement."
    )
    for admitted in _ASSERTION_CALLEES:
        assert is_assertion_callee(admitted) is True, (
            f"{admitted!r} is in the table but `is_assertion_callee` refuses it — the "
            f"predicate and the table disagree about the one question they both answer"
        )

    # ── THE GENERATED ADVERSARIAL POPULATION, closed over the table itself.
    generated = {
        variant
        for name in _ASSERTION_CALLEES
        for variant in (
            name.lower(),
            name.upper(),
            name + "ish",
            "My" + name,
            name + "s",
        )
        if variant not in _ASSERTION_CALLEES
        and not vocabulary_module._matches_assertion_convention(variant)
    }
    # The floor is DERIVED from the table rather than typed as a magic number, so the sweep
    # is required to grow with the vocabulary. Measured on the 89-name table: 283 variants.
    minimum = 3 * len(_ASSERTION_CALLEES)
    assert len(generated) >= minimum, (
        f"non-vacuity: the generator produced only {len(generated)} near-miss variant(s) from "
        f"a {len(_ASSERTION_CALLEES)}-name table (floor {minimum}), so this sweep has gone "
        f"nearly silent"
    )
    assert {"ASSERTIONERROR", "MyAssertionError", "AssertionErrorish"} <= generated, (
        "the generator stopped producing the case-folded variants of the one name this story "
        "admitted — which are exactly what a case-insensitive convention regex (DN-16-6-1, "
        "REJECTED) would wrongly admit"
    )
    # ⚠️ MEASURED AND RECORDED RATHER THAN SMOOTHED: the all-lowercase `assertionerror` is
    # NOT in the generated population, because the SHIPPED case-sensitive convention
    # `\A_?assert\w*\Z` already admits it — it reads as a project helper. That spelling was
    # never the defect; the CAPITALISED builtin was, and it is the only thing Story 16.6
    # moved. The generator's filter is what surfaces the distinction rather than hiding it.
    assert is_assertion_callee("assertionerror") is True
    assert "assertionerror" not in generated
    offenders = sorted(v for v in generated if is_assertion_callee(v))
    assert offenders == [], (
        f"{len(offenders)} generated near-miss variant(s) count as assertions: "
        f"{offenders[:12]!r}. Either a name was smuggled into the table or "
        f"`_ASSERTION_NAMING_CONVENTION` was loosened — DN-16-6-1 rejected the "
        f"case-insensitive form precisely because its collision population is unbounded."
    )

    # ── AND AT THE REAL SEAM: a near-miss raise is still assertion-free.
    near_miss, entry, definition = _score_one(
        tmp_path, _PROBE.format(line='raise AssertionErrorish("x")'), "near_miss"
    )
    assert "AssertionErrorish" in _span_callees(entry, definition), (
        "non-vacuity: the index did not emit the near-miss callee, so the span below is "
        "assertion-free for a reason that has nothing to do with the vocabulary"
    )
    assert near_miss.statement_count > 0
    assert near_miss.assertion_sites == 0 and near_miss.heuristically_vacuous is True
