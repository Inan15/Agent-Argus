"""The assertion-density half of the vacuous-test detector (Story 14.2).

Verification area ArgusAgent-DETECT (``TC-ArgusAgent-DETECT-001-113``..``-122``). Two
measured defects and one premise that did not survive:

1. **the DENOMINATOR counted LINES** — a multi-line call, a dict literal, a closing bracket
   and every line of a docstring each scored as a statement, running at **1.907×** CPython's
   own statement count over the 1,848 flagged tests of the pinned minions tree. An inflated
   denominator depresses the density arithmetically and the ``1/4`` floor fires from below,
   so half of a suite was flagged for a reason that was arithmetic rather than evidence;
2. **the assertion TABLE knew no pytest** — all 23 of its names were ``unittest``, and an
   assertion it could not see is present in 13 of the 31 adjudicated spans;
3. **widening that table CAN manufacture a 🔴** — Story 14.1 recorded that passing the table
   into ``provenance_scan`` as a parameter made fact (b) independent of it. It does not, and
   ``-115`` reproduces the false accusation that follows;
4. **the FIRST fix reintroduced the same defect, smaller and differently shaped** — its
   residual against CPython was documented as an under-count "away from a flag" and was in
   fact an OVER-count (64/64 minions, 27/28 agent-smith non-exact spans), biasing TOWARDS a
   flag. ``-121``/``-122`` close it and pin the direction (review iteration 1).

WHY THIS MODULE EXISTS SEPARATELY FROM ``test_vacuous_detector.py``
-------------------------------------------------------------------
That module went 324 → 1,084 lines during Story 14.1 and NFR-M1's ceiling is 1,200. Story
14.2 adds cases and Story 14.3 adds more after it. The split is by **cohesion**, on the
``argus/detectors/provenance_scan.py`` precedent — the density / denominator / assertion-
vocabulary cases live here, the fact-(b) corroboration branch cases stay where they are —
and NOT by an exemption: the size registry may only shrink, and narrowing a population until
it goes green is a defect this project has named
(``tests/test_module_size_ceiling.py:35-39``). It is also the cleaner hand-off to Story 14.3,
which owns the same frozenset across four more languages.

Every case runs the REAL detector over the REAL tree-sitter index. The denominator cases
additionally assert against CPython's own ``ast`` module as GROUND TRUTH rather than against
a hand-transcribed expectation, because a hand-transcribed expectation is the tester
asserting their own arithmetic.
"""

from __future__ import annotations

import ast
import importlib.util
from fractions import Fraction
from pathlib import Path

import pytest

from argus.detectors.provenance_scan import (
    body_statement_count,
    logical_statement_count,
    logical_statement_starts,
    provenance_evidence,
)
from argus.detectors.vacuous_test import (
    _ASSERTION_CALLEES,
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
    ASSERTION_DENSITY_FLOOR,
    MOCK_RATIO_CEILING,
    RULE_AST,
    RULE_HEURISTIC,
    VacuousTestDetector,
    is_assertion_callee,
)
from argus.ledger.coverage_ledger import CoverageDepth

from argus.pipeline_stages import _read_source
from argus.index.ast_index import build_ast_index  # noqa: E402


def _grammar_or_unevaluable() -> None:
    """Assert the Python grammar is present, as a NAMED outcome rather than a skip (AC8.5).

    ⛔ ``pytest.importorskip`` would be a FALSE GREEN here, and the neighbouring module's use
    of it is the pattern this deliberately does not copy. ``tree-sitter`` and
    ``tree-sitter-python`` are **base** dependencies of this project (``pyproject.toml``
    promoted them out of the optional ``[languages]`` extra), not an optional extra, so
    "absent" is a broken environment rather than a supported configuration — and
    ``audit-ci.yml`` sets ``ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`` precisely so a missing grammar
    cannot be answered with a skip. A skipped case reads as a passing case in every summary
    that matters; an ``UNEVALUABLE`` failure reads as what it is.

    The whole of this module measures how the detector reads REAL source through the REAL 1.4
    index. Without the grammar there is nothing to measure, and saying so out loud is the
    honest outcome — the same distinction the corpus measurement draws when it refuses to
    read "0 corroborated findings moved" as a confirmation.
    """
    missing = [
        name
        for name in ("tree_sitter", "tree_sitter_python")
        if importlib.util.find_spec(name) is None
    ]
    if missing:
        pytest.fail(
            f"UNEVALUABLE: {', '.join(missing)} is not importable, so nothing in this module "
            "measured anything. These are BASE dependencies (pyproject.toml), not the "
            "optional `[languages]` extra, so this is a broken environment and not a "
            "supported configuration. It is reported as a FAILURE rather than a skip on "
            "purpose (Story 14.2 / AC8.5): a skip here would read as green."
        )


def _score_one(root: Path, source: str, slug: str):
    """Score the single test function in *source* through the REAL 1.4 index.

    Returns ``(VacuousTestScore, AstIndexEntry, Definition)``. The edge set is what
    tree-sitter actually emits, never a hand-built list — the claims below are about how the
    shipped detector reads real source text, and a hand-built list would assert the tester's
    belief about that instead.
    """
    _grammar_or_unevaluable()
    relative = f"tests/test_{slug}.py"
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8")
    index = build_ast_index(root, (relative,))
    entry = {e.file_path: e for e in index.entries}[relative]
    assert not entry.parse_failed and entry.ast_eligible, f"{slug!r} did not parse"
    definitions = [d for d in entry.definitions if d.kind == "function" and d.name.startswith("test")]
    assert len(definitions) == 1, f"{slug!r} must hold exactly one test function"
    definition = definitions[0]
    score = VacuousTestDetector()._score(source.splitlines(), entry.edges, definition)
    return score, entry, definition


def _cpython_body_statements(source: str, name: str) -> int:
    """GROUND TRUTH: every ``ast.stmt`` in *name*'s body, recursively, from CPython itself.

    The denominator's claim is "count what Python executes". CPython's own parser is the only
    non-circular way to check that; the detector cannot use it (it must work on TypeScript,
    Go and Java source too, through the 1.4 tree-sitter index), but a TEST can.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return sum(
                1 for statement in node.body for sub in ast.walk(statement) if isinstance(sub, ast.stmt)
            )
    raise AssertionError(f"{name!r} not found in the fixture")


# ── -113: the denominator counts LOGICAL STATEMENTS ───────────────────────────────────────
#
# Every branch of the new denominator, each reached by a fixture built for it. The last
# element is whether the count must equal CPython's exactly; the ONE row where it may not is
# the documented, bounded under-count (an inline compound header ``with x: y()`` is two
# statements to CPython and one line here), recorded as a row rather than left to be
# discovered — and its error direction RAISES density, i.e. moves away from a flag.
_DENOMINATOR_SHAPES: tuple[tuple[str, str, int, bool], ...] = (
    (
        "single-line-statements",
        "def test_x():\n"
        "    a()\n"
        "    b()\n"
        "    c()\n"
        "    assert d()\n",
        4,
        True,
    ),
    (
        "bracket-wrapped-call-counts-once",
        "def test_x():\n"
        "    sut(\n"
        "        1,\n"
        "        2,\n"
        "    )\n"
        "    assert sut(3)\n",
        2,
        True,
    ),
    (
        "backslash-continuation-counts-once",
        "def test_x():\n"
        "    result = \\\n"
        "        sut(1, 2)\n"
        "    assert result\n",
        2,
        True,
    ),
    (
        "semicolon-compound-counts-once-per-simple-statement",
        "def test_x():\n"
        "    sut(1); sut(2); sut(3)\n"
        "    assert sut(4)\n",
        4,
        True,
    ),
    (
        "trailing-semicolon-ends-nothing-new",
        "def test_x():\n"
        "    sut(1);\n"
        "    assert sut(2)\n",
        2,
        True,
    ),
    (
        "triple-quoted-docstring-counts-once",
        'def test_x():\n'
        '    """One statement.\n'
        "\n"
        "    However many lines of prose it runs to,\n"
        "    and however many blank lines it contains.\n"
        '    """\n'
        "    assert sut()\n",
        2,
        True,
    ),
    (
        "single-quoted-docstring-counts-once",
        'def test_x():\n'
        '    "A one-line docstring."\n'
        "    assert sut()\n",
        2,
        True,
    ),
    (
        "multi-line-string-literal-in-an-assignment-counts-once",
        'def test_x():\n'
        '    payload = """\n'
        "    line one\n"
        "    line two\n"
        '    """\n'
        "    assert sut(payload)\n",
        2,
        True,
    ),
    (
        "comment-only-and-blank-lines-count-for-nothing",
        "def test_x():\n"
        "    # a leading comment\n"
        "\n"
        "    a()\n"
        "\n"
        "    # a trailing comment\n"
        "    assert b()\n",
        2,
        True,
    ),
    (
        "dict-literal-counts-once",
        "def test_x():\n"
        "    payload = {\n"
        "        'a': 1,\n"
        "        'b': 2,\n"
        "    }\n"
        "    assert sut(payload)\n",
        2,
        True,
    ),
    (
        "nested-block-counts-header-and-body",
        "def test_x():\n"
        "    for value in (1, 2):\n"
        "        sut(value)\n"
        "    assert sut(3)\n",
        3,
        True,
    ),
    (
        "statement-inside-a-with-block",
        "def test_x():\n"
        "    with opened() as handle:\n"
        "        sut(handle)\n"
        "    assert sut(1)\n",
        3,
        True,
    ),
    (
        "wrapped-def-header-is-not-a-body-statement",
        "def test_x(\n"
        "    alpha,\n"
        "    beta,\n"
        "):\n"
        "    sut(alpha)\n"
        "    assert sut(beta)\n",
        2,
        True,
    ),
    (
        # The DOCUMENTED under-count, recorded rather than discovered. `with x(): y()` is a
        # `With` node plus an `Expr` to CPython — two statements — and one line here. The
        # error direction RAISES density, which moves AWAY from a flag; the whole story is
        # about not manufacturing accusations, so a bounded under-count in that direction is
        # the acceptable side of the trade and is stated here so nobody has to rediscover it.
        "inline-compound-header-under-counts-by-design",
        "def test_x():\n"
        "    with opened(): sut(1)\n"
        "    assert sut(2)\n",
        2,
        False,
    ),
)


def test_the_denominator_counts_logical_statements_not_lines(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-113 — AC1.1: every branch of the new denominator, against CPython.

    THE DEFECT THIS PINS, measured before it was fixed (Story 14.2 / §0.2)
    ----------------------------------------------------------------------
    ``_count_statements`` counted every non-blank, non-comment LINE of the span. Over the
    1,848 heuristically-flagged tests of the pinned minions tree that denominator summed to
    **29,093** against CPython's **15,255** — **1.907×** ground truth. (The 2.04× the sprint
    change proposal records does NOT reproduce, and it is not a definitional difference
    either: counting only TOP-LEVEL body statements gives 2.664×, so 2.04 is neither. The
    defect is real and large; that particular multiplier was stale.) After this change the
    same population sums to **15,255** — **1.0000×**, exact on **1,848 of 1,848** spans.
    (Iteration 1 of this story landed at 15,334 / 1.0052× / 1,784-of-1,848; the remaining 64
    spans were all OVER-counts and are closed by ``-121``, whose docstring records why the
    direction mattered more than the magnitude.)

    The expectations below are asserted against CPython's own ``ast`` module rather than
    transcribed, because a transcribed number tests the author's arithmetic. Both are
    asserted: the ground-truth equality AND the specific per-branch count, so a fixture that
    silently stopped exercising its branch would fail rather than pass.
    """
    exact = 0
    for slug, source, expected, matches_cpython in _DENOMINATOR_SHAPES:
        score, _, _ = _score_one(tmp_path, source, slug.replace("-", "_"))
        assert score.statement_count == expected, (
            f"{slug!r}: expected {expected} logical statements, got {score.statement_count}. "
            "A count that matches the LINE count again means the denominator has gone back to "
            "counting what the author typed instead of what Python executes (AC1.1)."
        )
        truth = _cpython_body_statements(source, "test_x")
        if matches_cpython:
            exact += 1
            assert score.statement_count == truth, (
                f"{slug!r}: CPython counts {truth} body statements, the detector counts "
                f"{score.statement_count}. Ground truth is not negotiable here — if this "
                "branch genuinely has to differ, move the row to matches_cpython=False and "
                "record WHY and in which direction, as the inline-compound row does."
            )
        else:
            assert score.statement_count != truth, (
                f"{slug!r} is declared a documented divergence but now AGREES with CPython "
                f"({truth}). Delete the exemption rather than leaving a stale one — a "
                "recorded limitation that no longer exists is how folklore starts."
            )

    # Non-vacuity: the table must be dominated by rows that really are checked against
    # ground truth, or the exemption becomes the rule.
    assert exact >= len(_DENOMINATOR_SHAPES) - 1 and exact > 0, (
        f"only {exact}/{len(_DENOMINATOR_SHAPES)} rows are ground-truth-checked"
    )


def test_a_semicolon_inside_a_docstring_is_prose_not_a_statement_separator(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-114 — AC2.3: the mechanism that GAINED two flags, pinned.

    THE DEFECT THIS PINS, and it is a defect of the FIX rather than of the shipped code
    ------------------------------------------------------------------------------------
    The obvious way to build this denominator is to reuse ``logical_statement_starts`` as it
    stood, since fact (b) already had to answer "where does a statement start?". Measured,
    that lands at 1.134× of ground truth and — far worse — **GAINS two flags** on the pinned
    corpora, on a change advertised as flag-*reducing*:

        agent-smith/agentsmith-core/tests/test_sim_real_boundary.py:405   8 -> 9 statements
            "…manifest object; the sim path never enforces the KMS key gate (presence-only)."

        agent-smith/agentsmith-plugin/tests/test_plugin_fail_closed.py:376  12 -> 13
            '"No parseable envelope on stdout" is the rule; a framework argument error also'

    Both are a ``;`` in DOCSTRING PROSE. The scan read one physical line at a time and
    carried no cross-line string state, so every line of a docstring looked like its own
    statement and a semicolon inside one looked like a statement separator. A change that
    quietly manufactures two new accusations is the exact defect class Epic 14 exists to
    close, so the fix carries the cross-line state (``provenance_scan._scan_span``) and the
    measured result is **0 flags gained, 1,572 lost**.

    The assertion is an EQUIVALENCE — the same function with and without the semicolon must
    score identically — because that is the actual requirement. A future scanner cannot
    satisfy it by being uniformly stricter or uniformly looser.
    """
    without = (
        'def test_x():\n'
        '    """A docstring with no separator in it.\n'
        "\n"
        "    More prose, ordinary punctuation only.\n"
        '    """\n'
        "    sut(1)\n"
        "    assert sut(2)\n"
    )
    with_semicolons = (
        'def test_x():\n'
        '    """A docstring; it contains a semicolon.\n'
        "\n"
        "    More prose; and another one here; and a third.\n"
        '    """\n'
        "    sut(1)\n"
        "    assert sut(2)\n"
    )
    plain, _, _ = _score_one(tmp_path, without, "docstring_plain")
    seeded, _, _ = _score_one(tmp_path, with_semicolons, "docstring_semicolons")

    assert plain.statement_count == seeded.statement_count == 3, (
        f"a ';' inside docstring PROSE changed the statement count "
        f"({plain.statement_count} -> {seeded.statement_count}). The scan has lost its "
        "cross-line string state, and the measured consequence is new flags on tests that "
        "did nothing but write a semicolon in their own documentation."
    )
    assert plain.assertion_density == seeded.assertion_density
    assert plain.heuristically_vacuous == seeded.heuristically_vacuous

    # …and the ';' really is inside the string rather than eliminated by the fixture: a ';'
    # in CODE still separates simple statements, which is the other direction of the same
    # claim and the reason this is not passing by ignoring semicolons altogether.
    in_code = (
        "def test_x():\n"
        "    sut(1); sut(2)\n"
        "    assert sut(3)\n"
    )
    code_score, _, _ = _score_one(tmp_path, in_code, "semicolon_in_code")
    assert code_score.statement_count == 3, (
        "a ';' between two SIMPLE STATEMENTS stopped being a separator — the fix bought "
        "docstring safety by going blind to semicolons entirely"
    )


# ── -115: the moat. Widening the table CAN corroborate; the frozen vocabulary stops it ────

#: §0.4's fixture, reproduced verbatim: an ORDINARY mock-interaction test. The SUT is called
#: and its result discarded (which is what mock-interaction tests do — the point is the
#: interaction), and the only assertion is ``fake.calculate.assert_called_once_with()``.
#: Nothing about it is vacuous, and nothing about it is exotic.
_MOCK_INTERACTION_SOURCE = """from unittest.mock import Mock

from app.service import compute


def test_compute_calls_the_dependency():
    compute([1, 2])
    fake = Mock()
    fake.calculate.return_value = 6
    fake.calculate()
    fake.calculate.assert_called_once_with()
"""


def test_widening_the_assertion_table_must_not_reach_the_corroboration_path(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-115 — AC6.1/6.3 / DN-14-2-1: the moat, made structural.

    THE PREMISE THAT DID NOT SURVIVE, REPRODUCED BEFORE IT WAS CLOSED
    -----------------------------------------------------------------
    Story 14.1 moved fact (b) into ``provenance_scan.py`` and left the callee vocabularies in
    ``vacuous_test.py``, passed in as parameters, recording that this made the guarantee
    structural: *"nothing in this module can grow a dependency on a table it cannot see."*
    **That sentence is false as written.** The module CAN see the table — it is the
    ``assertion_callees`` parameter — and it reads it in two places, both of which can move
    TOWARDS an accusation when it widens: the SUT loop (a widened callee stops being a
    candidate SUT call, which can drop ``consumed_sut_calls`` to zero and flip
    ``sut_result_is_discarded`` true) and ``_assertion_statement_lines`` (a widened callee
    makes another line an assertion statement, which can raise ``mock_referencing_assertions``
    from zero).

    Measured end to end on the fixture above, through the real index and the real detector::

        23-name table : asserts=0 stmts=5 density=0   flagged=True corroborated=False  advisory
        widened table : asserts=1 stmts=5 density=1/5 flagged=True corroborated=True   🔴

    Density rises to 1/5, which is **still below the 1/4 floor**, so the test stays flagged
    and is now VERDICT-ELIGIBLE. A perfectly ordinary mock-interaction test becomes a
    build-blocking false accusation, produced by Story 14.2's own fix for the assertion
    table — the exact class Epic 14 exists to close.

    ⚠️ **The corpus cannot adjudicate this and must not be read as reassurance.** Over both
    pinned members, widening the table moved corroboration for **0** tests in every direction
    measured — but only because **0 of 4,673** are corroborated at all after Story 14.1. That
    is an EMPTY DENOMINATOR: ``UNEVALUABLE``, not a confirmation, and a guard resting on it
    would be ``AI-E3-1`` (a test that proves nothing). The mechanism below is the evidence.

    So this guard asserts the RED and the GREEN in one place, which is what makes it
    falsifiable rather than decorative: the widened vocabulary genuinely WOULD corroborate,
    the frozen one genuinely does NOT, and the shipped detector emits the advisory rule.
    """
    score, entry, definition = _score_one(
        tmp_path, _MOCK_INTERACTION_SOURCE, "mock_interaction"
    )
    span = [
        e for e in entry.edges if definition.start_line <= e.line <= definition.end_line
    ]

    # The fixture is heuristically flagged under BOTH vocabularies, so the only thing under
    # test is PROMOTION. (Without this the guard could pass by the test ceasing to be flagged.)
    assert score.heuristically_vacuous is True
    assert score.assertion_sites == 1 and score.statement_count == 5
    assert score.assertion_density == Fraction(1, 5) < ASSERTION_DENSITY_FLOOR

    # ── THE RED. Had the corroboration path been routed through the WIDENED vocabulary — the
    # one-table design this story rejected — both fact-(b) clauses would hold and this
    # ordinary test would be verdict-eligible. ────────────────────────────────────────────
    widened_evidence = provenance_evidence(
        _MOCK_INTERACTION_SOURCE.splitlines(),
        span,
        definition.start_line,
        definition.end_line,
        assertion_callees=_ASSERTION_CALLEES,
        mock_callees=_MOCK_CALLEES,
    )
    widened_sut = [
        e for e in span if e.callee not in _ASSERTION_CALLEES and e.callee not in _MOCK_CALLEES
    ]
    assert (
        len(widened_sut) >= 1
        and widened_evidence.sut_result_is_discarded
        and widened_evidence.mock_referencing_assertions >= 1
    ), (
        "the RED arm no longer reproduces, so this guard is now asserting nothing. Either the "
        "fixture stopped exercising the mechanism (repair the FIXTURE) or fact (b) changed "
        "shape (re-derive the mechanism and re-author this case with its reason) — do NOT "
        "delete the arm: a guard written over a defect never demonstrated is AI-E3-1."
    )

    # ── THE GREEN. Production hands fact (b) the FROZEN vocabulary, so the same source is
    # read the same way it was before the table widened. ─────────────────────────────────
    frozen_evidence = provenance_evidence(
        _MOCK_INTERACTION_SOURCE.splitlines(),
        span,
        definition.start_line,
        definition.end_line,
        assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
        mock_callees=_MOCK_CALLEES,
    )
    assert frozen_evidence.mock_referencing_assertions == 0, (
        "the FROZEN vocabulary now sees the mock's assertion method too, so it has started "
        "tracking `_ASSERTION_CALLEES` — which is precisely what DN-14-2-1 forbids. A false "
        "🔴 on ordinary mock-interaction tests is one edit away; do not 'tidy' the two tables "
        "into one."
    )

    # …and the whole detector agrees, on the default path an operator actually runs.
    result = VacuousTestDetector().run(
        file_path="tests/test_mock_interaction.py",
        source=_MOCK_INTERACTION_SOURCE,
        ast_entry=entry,
    )
    assert len(result.findings) == 1
    assert result.findings[0].rule_id == RULE_HEURISTIC, (
        "an ordinary mock-interaction test was promoted to verdict-eligible. Widening the "
        "assertion table has reached the corroboration path (DN-14-2-1 / AC6.1), and this is "
        "the lethal failure class — a false 🔴 manufactured by Epic 14's own fix."
    )
    assert result.findings[0].depth_supported is None
    assert score.ast_corroborated is False


def test_the_frozen_corroboration_vocabulary_is_pinned_and_separate() -> None:
    """TC-ArgusAgent-DETECT-001-116 — AC6.2 / AC7: the hand-off Story 14.3 inherits.

    Two vocabularies, two QUESTIONS (DN-14-2-4). The heuristic asks *"does this test assert
    anything?"* and wants BREADTH; facts (a) and (b) ask *"which edges are not SUT calls?"*
    and want STABILITY. A reviewer must not be able to read the second table as an accidental
    duplicate of the first, and Story 14.3 must not be able to widen it by reflex.

    This pins the contract in the three ways it can be broken:

    1. the frozen table is **exactly** Story 14.1's 23 names — no more, no fewer;
    2. the widened table is a strict superset of it (so the density half never LOSES a name
       the corroboration half has, which would be a silent recall regression), while the
       frozen half gains nothing;
    3. neither is derived from the other at runtime, which is checked the only way it can be
       from outside: the names Story 14.2 added are absent from the frozen table, and the
       cross-language names Story 14.3 added are in the WIDENED table and in NEITHER the
       frozen one.

    ⚠️ **RE-AUTHORED 2026-08-18 (Story 14.3), and it is an INTENDED BEHAVIOUR CHANGE — the
    ``-86`` treatment Story 14.1 established, not a nudge to match new output.** Arm 3 was
    written by Story 14.2 as ``assert not (cross_language & _ASSERTION_CALLEES)``: a
    deliberate, dated assertion that *"Story 14.3 has not happened yet"*, whose stated purpose
    was to go RED on the day it did, so that widening the density table could not be done
    absent-mindedly. **Story 14.3 is that day, and this guard going red is the guard
    WORKING.** The assertion is therefore INVERTED rather than deleted or weakened: the same
    twelve names, the same table, the opposite expectation — the density half must now
    recognise every one of them, and the frozen half must still recognise none.

    The direction matters as much as the fact. Inverting it keeps a live claim on both tables
    from a single literal, so a later story that "tidies" the two vocabularies together, or
    that reverts the cross-language vocabulary, still trips exactly this case. Deleting the
    arm — the tempting move, since it had "served its purpose" — would have left the moat
    unwatched from this direction and is the ``AI-E3-1`` shape. The other three arms are
    UNCHANGED and still assert.
    """
    assert len(_CORROBORATION_ASSERTION_CALLEES) == 23, (
        f"the FROZEN fact-(a)/(b) vocabulary now holds "
        f"{len(_CORROBORATION_ASSERTION_CALLEES)} names, not the 23 Story 14.1 shipped. This "
        "table is the moat: widening it re-opens the false accusation `-115` reproduces. "
        "Story 14.3 widens `_ASSERTION_CALLEES` and leaves this one alone."
    )
    assert _CORROBORATION_ASSERTION_CALLEES < _ASSERTION_CALLEES, (
        "the density vocabulary no longer contains every frozen name, so a name the "
        "corroboration path treats as an assertion is counted as a SUT call by the heuristic "
        "— the two halves have started to disagree in the direction that ADDS flags"
    )

    widened_only = _ASSERTION_CALLEES - _CORROBORATION_ASSERTION_CALLEES
    assert {"raises", "warns", "assert_called_once_with", "assertIsInstance"} <= widened_only, (
        "Story 14.2's additions must live in the DENSITY table only"
    )
    assert not (widened_only & _CORROBORATION_ASSERTION_CALLEES)

    # Story 14.3 / AC5.2 — the INVERSION. This literal is byte-for-byte the set Story 14.2
    # asserted was ABSENT; only the expectation moved, and it moved because the work happened.
    cross_language = {"expect", "toBe", "toEqual", "toThrow", "deepStrictEqual", "assertEquals",
                      "assertThat", "Fatal", "Fatalf", "Errorf", "NoError", "ok"}
    assert cross_language <= _ASSERTION_CALLEES, (
        f"the cross-language assertion vocabulary Story 14.3 shipped has been REMOVED from the "
        f"density table: {sorted(cross_language - _ASSERTION_CALLEES)}. Every one of these is a "
        f"real assertion in a language the default install parses, and a test whose only "
        f"assertion is one of them scores `assertion_sites=0`, falls below the 1/4 floor and is "
        f"FALSELY FLAGGED — the exact accusation Epic 14 exists to close, reproduced RED in "
        f"tests/test_vacuous_cross_language.py before it was closed."
    )
    assert not (cross_language & _CORROBORATION_ASSERTION_CALLEES), (
        f"cross-language names reached the FROZEN table: "
        f"{sorted(cross_language & _CORROBORATION_ASSERTION_CALLEES)}. Story 14.3 widens the "
        f"DENSITY numerator only; the moat stays at Story 14.1's 23 names (DN-14-2-1)."
    )

    # AC7.1 — FLAT and language-agnostic. No language field, sub-table or grouping key enters
    # the detector (NFR-P2 confines the language conditional to `argus/index/`), so both
    # tables must be flat sets of plain strings and nothing else.
    for table in (_ASSERTION_CALLEES, _CORROBORATION_ASSERTION_CALLEES):
        assert isinstance(table, frozenset)
        assert all(isinstance(name, str) for name in table)


def test_the_assertion_vocabulary_moves_in_both_directions(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-117 — AC7.2/7.4: the fix found the assertions, and kept the signal.

    A ONE-DIRECTIONAL CHECK WOULD PASS ON A CHANGE THAT DELETED THE CAPABILITY
    ---------------------------------------------------------------------------
    "Fewer tests are flagged" is satisfied just as well by a detector that flags nothing. So
    both directions are asserted over the same shape:

    * a test whose ONLY assertion is one the old 23-name table could not see — a
      ``unittest.mock`` assertion method, a ``pytest.raises`` block, a project helper named
      ``assert_*`` — is **no longer flagged**; and
    * the byte-identical test with that assertion REMOVED **still is**.

    The pair is what makes each row a statement about the assertion vocabulary rather than
    about the fixture's length. The third arm is the naming-convention predicate
    (DN-14-2-3), which is a separate named predicate rather than entries smuggled into the
    frozenset (AC7.2) precisely so it can be pointed at here.
    """
    rows = (
        (
            "unittest-mock-assertion-method",
            "def test_x():\n"
            "    publish(payload)\n"
            "    client.flush()\n"
            "    client.send.assert_called_once_with(payload)\n",
            "def test_x():\n"
            "    publish(payload)\n"
            "    client.flush()\n"
            "    client.close()\n",
        ),
        (
            "pytest-raises-block",
            "def test_x():\n"
            "    prepare()\n"
            "    warm_up()\n"
            "    with pytest.raises(ValueError):\n"
            "        parse('bad')\n",
            "def test_x():\n"
            "    prepare()\n"
            "    warm_up()\n"
            "    with opened():\n"
            "        parse('bad')\n",
        ),
        (
            "project-helper-naming-convention",
            "def test_x():\n"
            "    prepare()\n"
            "    warm_up()\n"
            "    assert_one_rejection(result)\n",
            "def test_x():\n"
            "    prepare()\n"
            "    warm_up()\n"
            "    record_one_rejection(result)\n",
        ),
    )
    for label, asserting, assertion_free in rows:
        seen, _, _ = _score_one(tmp_path, asserting, f"vocab_{label.replace('-', '_')}")
        assert seen.assertion_sites >= 1 and seen.heuristically_vacuous is False, (
            f"{label!r}: the assertion is still invisible to the density numerator "
            f"(assertion_sites={seen.assertion_sites}, density={seen.assertion_density}). "
            "This is the shape present in 13 of the 31 adjudicated spans — a real test "
            "accused because the table knew only unittest."
        )
        blind, _, _ = _score_one(
            tmp_path, assertion_free, f"vocab_{label.replace('-', '_')}_free"
        )
        assert blind.assertion_sites == 0 and blind.heuristically_vacuous is True, (
            f"{label!r}: the assertion-FREE counterpart is no longer flagged either "
            f"(assertion_sites={blind.assertion_sites}). The vocabulary fix removed the "
            "SIGNAL rather than the blind spot — that is a recall regression wearing a "
            "precision fix's clothes, and only this arm can see it."
        )

    # The convention predicate itself, in both directions and with its accepted collision
    # cost named. Unicode-aware by construction (AC8.3): `\\w` is a Unicode class on `str`
    # patterns, so a non-ASCII helper name matches exactly as an ASCII one does.
    for name in ("assert_valid", "_assert_one_rejection", "assertSomethingProjectSpecific",
                 "assert_café_vide", "assert_тесты_passed"):
        assert is_assertion_callee(name), f"{name!r} must match the naming convention"
    for name in ("compute_total", "reset_mock", "_private_helper", "asser", "reassert",
                 "somme_totale", "проверить"):
        assert not is_assertion_callee(name), f"{name!r} must NOT match"


def test_the_denominator_is_identical_on_CRLF_and_LF_source(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-118 -- AC8.4: the DENOMINATOR specifically, across terminators.

    RE-AUTHORED 2026-08-19 by Story 15.2, `-86`-style: an INTENDED behaviour change with the
    reason recorded, never an assertion adjusted until it matched output. **The three
    load-bearing assertions at the end are byte-unchanged** -- what changed is the arm that
    could not fail.

    WHY THE OLD TERMINATOR ARM COULD NOT FAIL -- two independent reasons, both measured
    ------------------------------------------------------------------------------------
    1. ``_score_one`` scores ``source.splitlines()`` of the **in-memory** string, not the file
       it had just written. So the denominator's input was byte-identical in both arms *by
       construction*, and ``lf.splitlines() == crlf.splitlines()`` is ``True`` anyway.
    2. The on-disk bytes were not what the fixture claimed either. ``write_text(source,
       encoding="utf-8")`` uses ``newline=None``, so on Windows the "LF" arm was written as
       **11 CRLF / 0 bare LF** and the "CRLF" arm as ``\r\r\n`` (**11 CRLF / 11 bare CR**).
       Neither arm ever presented an LF file to the parser, and both produced an identical
       index. Re-measured at HEAD ``72a95ef``; exactly those counts.

    So the guard asserted ``f(x) == f(x)`` on a pure function while believing it was varying a
    terminator. Its sibling ``-107`` had the same defect by a different route (it called
    ``splitlines()`` on its own fixture, erasing the variable at the seam it varied it across).
    **Both are one defect: the variable under test was constant.**

    WHAT IT DOES NOW (AC6.1 / AC6.2)
    --------------------------------
    The terminators are written as BYTES with ``write_bytes``, the bytes are ASSERTED before
    anything is scored, and the scored source is read back through **the production read path**
    (``argus/pipeline_stages._read_source``) rather than taken from the in-memory string.

    AC6.5 / `DN-15-2-4`: THE ARM IS *STILL* TRUE BY CONSTRUCTION, AND THAT IS SAID OUT LOUD
    ----------------------------------------------------------------------------------------
    Reading through the production path does not rescue the original equality: ``read_text``'s
    universal-newline decoding collapses ``\r\n`` to ``\n`` before the detector exists, so the
    two arms become the SAME STRING and comparing their scores is once again an identity.
    ⛔ **A guard that cannot fail is not repaired by moving where its input comes from.** So the
    equality is no longer what this arm asserts. It now asserts **the normalisation itself** --
    that the CRLF file really was written with CRLF bytes, and that what the read path returns
    for it contains no ``\r`` and is byte-identical to the LF file's text. That is a property of
    ``pipeline_stages`` which CAN fail, and Story 15.2's entire scope decision rests on it: it
    is why ``\r`` / ``\r\n`` cannot reach the detector while the eight exotic separators can.

    The REJECTED alternative (`DN-15-2-4`): delete the arm as unfalsifiable. Rejected because
    the normalisation it sits on is load-bearing and was, until now, asserted nowhere -- the
    scope of an entire story rests on a behaviour no guard pinned.

    MUTATION OBSERVED TO MAKE IT RED (AC6.4 / AC9.1): replacing ``_read_source``'s
    ``read_text(encoding="utf-8", errors="replace")`` with
    ``read_bytes().decode("utf-8", "replace")`` -- which does not do universal newlines -- leaves
    ``\r`` in the returned text and reddens the normalisation assertions. Executed and observed.

    The fixture deliberately contains a **docstring** and a **wrapped statement**, because those
    are the two places the representations could diverge: the docstring is where the cross-line
    string state lives, and the wrapped statement is where bracket depth carries across a
    terminator.
    """
    lf = (
        'def test_x():\n'
        '    """A docstring; with a semicolon in its prose.\n'
        "\n"
        "    And a second paragraph, so it really does span lines.\n"
        '    """\n'
        "    result = sut(\n"
        "        1,\n"
        "        2,\n"
        "    )\n"
        "    fake = Mock()\n"
        "    assert result == fake.value\n"
    )
    crlf = lf.replace("\n", "\r\n")
    assert "\r\n" in crlf  # the fixture really is CRLF

    # ---- the terminators are WRITTEN as claimed, and the bytes are asserted (AC6.1) ----
    _grammar_or_unevaluable()
    written = {}
    for label, source in (("lf", lf), ("crlf", crlf)):
        target = tmp_path / f"tests/test_terminator_{label}.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        # write_bytes, never write_text(newline=None) -- the platform rewrite is the whole
        # reason this arm was weak.
        target.write_bytes(source.encode("utf-8"))
        written[label] = target.read_bytes()
    assert written["lf"].count(b"\r") == 0, (
        f"the LF arm was written with {written['lf'].count(bytes([13]))} CR bytes; on Windows "
        "`write_text(newline=None)` used to make this 11, which is what made the arm vacuous"
    )
    assert written["lf"].count(b"\n") == 11
    assert written["crlf"].count(b"\r\n") == 11
    assert written["crlf"].count(b"\r") == 11, "the CRLF arm must be CRLF, never `\\r\\r\\n`"

    # ---- the NORMALISATION, which is the property this arm can actually falsify (AC6.5) ----
    lf_text = _read_source(tmp_path, "tests/test_terminator_lf.py")
    crlf_text = _read_source(tmp_path, "tests/test_terminator_crlf.py")
    assert "\r" not in crlf_text, (
        "the CRLF file reached the detector with its CR intact; the read path at "
        "argus/pipeline_stages.py:124 is supposed to normalise it, and Story 15.2's scope "
        "decision -- that CR/CRLF cannot desynchronise the detector from the index while the "
        "eight exotic separators can -- rests entirely on that"
    )
    assert crlf_text == lf_text, (
        f"the two arms did not normalise to the same text: {ascii(crlf_text[:60])} vs "
        f"{ascii(lf_text[:60])}"
    )
    assert crlf_text == lf, "the read path must return exactly the LF spelling of the source"

    # ---- and only THEN the arithmetic, scored from the file that was written (AC6.2) ----
    lf_score, _, _ = _score_one(tmp_path, lf_text, "terminator_lf_scored")
    crlf_score, _, _ = _score_one(tmp_path, crlf_text, "terminator_crlf_scored")
    assert lf_score == crlf_score, (
        f"the score differs across line terminators: {lf_score} vs {crlf_score}"
    )
    # ...and it is the INTERESTING arithmetic, not a degenerate agreement on zero: docstring
    # once, wrapped call once, four body statements in total.
    assert lf_score.statement_count == 4
    assert lf_score.assertion_sites == 1
    assert lf_score.assertion_density == Fraction(1, 4)


def test_the_contract_surface_and_thresholds_are_unchanged(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-119 — AC3: the thresholds and the emitted shape did not move.

    A failed measurement is not a reason to amend a threshold (protocol §5, Story 13.3 /
    AC5), and this story re-derived the arithmetic UNDER two fixed thresholds rather than
    around them. So both are pinned here beside the change that could most plausibly have
    been paid for by moving one, together with the parts of the emitted contract Story 1.6
    and the verdict gate read.
    """
    assert ASSERTION_DENSITY_FLOOR == Fraction(1, 4)
    assert MOCK_RATIO_CEILING == Fraction(1, 2)

    source = (
        "def test_x():\n"
        "    m = Mock()\n"
        "    m.value.return_value = 4\n"
        "    warm_up()\n"
        "    pretended = m.value()\n"
        "    assert pretended == 4\n"
    )
    score, entry, _ = _score_one(tmp_path, source, "contract_surface")

    # AR4 — exact Fractions, never float, on BOTH ratios.
    assert isinstance(score.assertion_density, Fraction)
    assert isinstance(score.mock_ratio, Fraction)
    assert not isinstance(score.assertion_density, float)
    assert score.assertion_density == Fraction(1, 5)

    # Frozen + extra="forbid", unchanged field set.
    assert score.model_config["frozen"] is True
    assert score.model_config["extra"] == "forbid"
    with pytest.raises(Exception):
        score.statement_count = 99  # type: ignore[misc]
    assert set(type(score).model_fields) == {
        "test_name", "start_line", "end_line", "assertion_sites", "statement_count",
        "call_sites", "mock_sites", "assertion_density", "mock_ratio",
        "heuristically_vacuous", "ast_corroborated",
    }

    # The Story 1.6 verdict-eligibility surface: advisory + depth_supported + rule_id.
    result = VacuousTestDetector().run(
        file_path="tests/test_contract_surface.py", source=source, ast_entry=entry
    )
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.advisory is True
    assert finding.rule_id in {RULE_AST, RULE_HEURISTIC}
    assert finding.rule_id == RULE_AST and finding.depth_supported is CoverageDepth.AUDITED_SHALLOW


def test_the_statement_scan_is_one_derivation_read_by_both_consumers(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-120 — AC1.2 / AR7 §3.3: no second statement scanner.

    Two spellings of *"where does a statement start?"* is the disagreement class this
    detector keeps closing elsewhere, and it is the reason the cross-line string state was
    added in ``provenance_scan`` rather than in the scorer. The structural claim is checkable
    from outside: the public counter and the public boundary map must agree about the SAME
    source, because they are projections of one scan.

    Non-vacuity: the fixture is one where a naive line-based count and the logical count
    genuinely differ (8 non-blank body LINES, 5 logical statements), so an implementation
    that had quietly forked would disagree here rather than coincide.
    """
    source = (
        'def test_x():\n'
        '    """A docstring; with a semicolon.\n'
        "\n"
        "    Second paragraph.\n"
        '    """\n'
        "    payload = {\n"
        "        'a': 1,\n"
        "    }\n"
        "    sut(payload); sut(2)\n"
        "    assert sut(3)\n"
    )
    lines = source.splitlines()
    body = logical_statement_count(lines, 2, len(lines))
    whole = logical_statement_count(lines, 1, len(lines))
    assert body == 5 and whole == 6, (body, whole)
    assert body_statement_count(lines, 1, len(lines)) == body, (
        "the body count and the span count disagree about the def header — one of them is "
        "walking the source a second way (AR7/§3.3)"
    )

    score, _, _ = _score_one(tmp_path, source, "one_derivation")
    assert score.statement_count == body, (
        f"the detector's denominator ({score.statement_count}) and provenance_scan's own "
        f"count ({body}) disagree over identical source. A second statement scanner has "
        "appeared, which is the fork AC1.2 exists to prevent."
    )
    # …and the naive LINE count really is different, so this is not a coincidence.
    naive = sum(
        1 for line in lines[1:] if line.strip() and not line.strip().startswith("#")
    )
    assert naive == 8 and naive != body


# ── -121: a continuation-clause header is not a statement of its own ──────────────────────
#
# ``except`` / ``else`` / ``finally`` / ``case`` headers are CLAUSES of a compound statement,
# not statements. CPython builds ONE ``ast.Try`` however many handlers it carries, ONE
# ``ast.If`` however its ``orelse`` is spelled and ONE ``ast.Match`` however many ``case``
# arms it has — ``ast.ExceptHandler`` and ``ast.match_case`` are not ``ast.stmt`` subclasses
# at all. The last element is the count CPython derives; every row is checked against it, so
# there is no exemption column here and none is wanted.
#
# ⛔ ``elif`` is NOT one of them and is carried below as a NEGATIVE control: ``if/elif`` is a
# nested ``ast.If``, i.e. a genuine extra statement, so a fix that swept ``elif`` in with the
# rest would under-count and this row would fail.
_CLAUSE_HEADER_SHAPES: tuple[tuple[str, str, int], ...] = (
    (
        # The review's minimal repro, verbatim: three continuation-clause headers, +3.
        "try-except-else-finally-is-one-statement-plus-its-bodies",
        "def test_x():\n"
        "    try:\n"
        "        a()\n"
        "    except ValueError:\n"
        "        pass\n"
        "    else:\n"
        "        b()\n"
        "    finally:\n"
        "        c()\n",
        5,
    ),
    (
        "if-else",
        "def test_x():\n"
        "    if sut(1):\n"
        "        a()\n"
        "    else:\n"
        "        b()\n"
        "    assert c()\n",
        4,
    ),
    (
        "for-else",
        "def test_x():\n"
        "    for value in sut():\n"
        "        a(value)\n"
        "    else:\n"
        "        b()\n"
        "    assert c()\n",
        4,
    ),
    (
        "while-else",
        "def test_x():\n"
        "    while sut():\n"
        "        a()\n"
        "    else:\n"
        "        b()\n"
        "    assert c()\n",
        4,
    ),
    (
        # ``case`` is a SOFT keyword, so the predicate has to be shape-based rather than
        # word-based. ``ast.match_case`` is not a statement; the two arms are +2 today.
        "match-case",
        "def test_x():\n"
        "    match sut():\n"
        "        case 1:\n"
        "            a()\n"
        "        case _:\n"
        "            b()\n"
        "    assert c()\n",
        4,
    ),
    (
        # A clause header wrapped over several lines is still one clause header — the
        # predicate has to read the ASSEMBLED logical statement, not the physical line.
        "wrapped-except-header",
        "def test_x():\n"
        "    try:\n"
        "        a()\n"
        "    except (\n"
        "        ValueError,\n"
        "        TypeError,\n"
        "    ):\n"
        "        b()\n"
        "    assert c()\n",
        4,
    ),
    (
        # NEGATIVE control 1: ``elif`` IS a statement. Correct before the fix; must stay so.
        "elif-is-a-real-statement",
        "def test_x():\n"
        "    if sut(1):\n"
        "        a()\n"
        "    elif sut(2):\n"
        "        b()\n"
        "    assert c()\n",
        5,
    ),
    (
        # NEGATIVE control 2: a clause header carrying its body INLINE still counts, because
        # the body is a real statement. Correct before the fix; must stay so.
        "clause-header-with-an-inline-body-still-counts",
        "def test_x():\n"
        "    try:\n"
        "        a()\n"
        "    except ValueError: b()\n"
        "    assert c()\n",
        4,
    ),
    (
        # NEGATIVE control 3: ``case`` as an ordinary NAME. A shape-based predicate keyed on
        # "starts with ``case`` and ends with a colon" must not eat an annotated assignment.
        "case-as-an-ordinary-name",
        "def test_x():\n"
        "    case: int = sut(1)\n"
        "    assert case\n",
        2,
    ),
    (
        # A DECORATOR is an expression hung off the definition it decorates, not a statement.
        # After the clause-header rule this was the ONLY remaining over-count in the whole
        # 4,673-function pinned population (one nested ``@property``).
        "a-decorator-is-not-a-statement",
        "def test_x():\n"
        "    class Stub:\n"
        "        @property\n"
        "        def value(self):\n"
        "            return sut()\n"
        "    assert Stub().value\n",
        4,
    ),
    (
        # …and a decorator wrapped over several lines is still ONE decorator.
        "a-wrapped-decorator-is-not-a-statement-either",
        "def test_x():\n"
        "    class Stub:\n"
        "        @registered(\n"
        "            name='v',\n"
        "        )\n"
        "        def value(self):\n"
        "            return sut()\n"
        "    assert Stub().value\n",
        4,
    ),
    (
        # NEGATIVE control 4: ``@`` as the matrix-multiply OPERATOR. It cannot BEGIN an
        # expression, so a statement using it starts at the left operand and is not matched.
        "matrix-multiply-is-not-a-decorator",
        "def test_x():\n"
        "    product = left() @ right()\n"
        "    assert product\n",
        2,
    ),
)


def test_a_continuation_clause_header_is_not_a_statement_of_its_own(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-121 — AC1.1/AC1.4: the residual's DIRECTION, measured.

    THE DEFECT THIS PINS, and it is a defect of the FIX rather than of the shipped code
    ---------------------------------------------------------------------------------------
    ``-113`` recorded the residual against CPython as *"a bounded under-count in the direction
    that RAISES density, i.e. away from a flag"*, citing the inline ``with x: y()`` compound.
    **That was measured wrong, and in a story whose whole method is "measured, not asserted"
    the direction of a SAFETY claim is exactly the thing that may not be asserted.** Of the 64
    (minions) / 28 (agent-smith) non-exact spans in the 1,784-of-1,848 population, 64/64 and
    27/28 were OVER-counts — the opposite direction, which LOWERS density and biases TOWARDS a
    flag. The dominant mechanism was this one: ``_scan_span`` opened a new logical statement on
    every ``except`` / ``else`` / ``finally`` / ``case`` header, none of which corresponds to
    any ``ast.stmt`` node at all.

    Measured on the review's own minimal repro before the fix: ``try/except/else/finally``
    scored **8** against CPython's **5**. Two real corpus instances the review located
    independently: ``test_prosecutor.py::test_malformed_top_level_arguments_raise_typed_error``
    (15 vs. 11) and ``test_llm_provider_conformance.py::test_secret_not_in_exception_repr``
    (39 vs. 35).

    The error direction of the FIX is the safe one and is structural rather than hoped for:
    the denominator can only SHRINK, ``assertion_density`` can only RISE, the ``1/4`` floor
    fires from BELOW, and ``mock_ratio`` is over ``call_sites`` and never touches the statement
    count — so no test can GAIN a flag from this. Measured: 0 gained on both pinned corpora.

    Every row is checked against CPython's own ``ast`` module, and four rows are NEGATIVE
    controls (``elif``, an inline clause body, ``case`` as an ordinary name, ``@`` as the
    matrix-multiply operator) so a predicate that over-reached would fail here rather than
    quietly under-count.
    """
    for slug, source, truth in _CLAUSE_HEADER_SHAPES:
        assert _cpython_body_statements(source, "test_x") == truth, (
            f"{slug!r}: the row's own expectation ({truth}) disagrees with CPython "
            f"({_cpython_body_statements(source, 'test_x')}) — fix the row, not the scanner."
        )
        score, _, _ = _score_one(tmp_path, source, slug.replace("-", "_"))
        assert score.statement_count == truth, (
            f"{slug!r}: CPython counts {truth} body statements, the detector counts "
            f"{score.statement_count}. A HIGHER count means a clause header is being read as "
            "a statement of its own, which LOWERS density and biases TOWARDS a flag — the "
            "direction this story exists to remove. A LOWER count means the predicate has "
            "over-reached and swallowed a real statement (see the elif control)."
        )


def test_the_clause_header_rule_does_not_move_fact_b(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-122 — AC6: the DENOMINATOR fix stays out of fact (b).

    ``logical_statement_starts`` is fact (b)'s statement-boundary map, and Story 14.1's moat
    rests on it. Excluding a clause header from the density DENOMINATOR must not change which
    line a call is attributed to, or a denominator fix would have reached into the
    corroboration path — the coupling class ``-115`` exists to prevent, arriving through a
    different door.

    So the exclusion is applied where the counting happens and NOT in the scan: every line of
    the span still maps to the first line of its own logical statement, clause headers
    included, exactly as before.
    """
    source = (
        "def test_x():\n"
        "    try:\n"
        "        result = sut(\n"
        "            1,\n"
        "        )\n"
        "    except ValueError:\n"
        "        result = fallback()\n"
        "    else:\n"
        "        observe(result)\n"
        "    assert result\n"
    )
    lines = source.splitlines()
    starts = logical_statement_starts(lines, 1, len(lines))
    assert starts == {1: 1, 2: 2, 3: 3, 4: 3, 5: 3, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10}, starts

    # …while the COUNT drops the two clause headers, and agrees with CPython.
    assert body_statement_count(lines, 1, len(lines)) == _cpython_body_statements(
        source, "test_x"
    ) == 5

    score, _, _ = _score_one(tmp_path, source, "clause_header_fact_b")
    assert score.statement_count == 5
