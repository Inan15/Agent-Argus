"""Story 17.4 — the guards over the PRODUCER: one derivation of S1, and no reachable judgement.

Verification area ``TC-ArgusAgent-PRECISION-001-149`` and ``-151``. **No new area is opened**: the
measurement is folded through the pre-registration, so its guards continue the existing
``PRECISION-001`` area exactly as ``tests/test_precision_preregistration.py`` did for Story 17.1.
Ids are minted from ``-147`` upward because ``-146`` was the highest in use at HEAD ``682b074``;
no existing id is renumbered, and an id here is a citation.

**Why this module is separate from ``tests/test_successor_reach_record.py``.** These two guards
read the PRODUCER — its source and its row constructor — and nothing else. They are green before
any measurement has been taken, which is what lets the producer land in its own reviewable commit
ahead of the record (§2.3). The guards that read the committed record live in the sibling module,
and ``-147``, the ordering guard, lives in ``tests/test_successor_output_ordering.py`` because it
asserts a UNIVERSAL over a population **this story creates** and may not land in a commit earlier
than the first successor-output commit (§1.4 / ``DN-17-4-4``). Splitting the three concerns was
also the §0.11 pre-registered split trigger, applied before the second half was written rather
than discovered at review.

⛔ **NO GUARD HERE ASSERTS A PREDICTED VALUE** (``DN-17-4-9``). Story 17.4's acceptance criteria
were written **before the number existed**; a guard asserting *"S1 reaches N"*, or even
*"S1 reaches more than zero"*, would be a prediction, and a prediction is the thing this epic
refuses. What is asserted here is **identity** — the measured predicate is the shipped one,
reached through its one public entry point, with no second derivation anywhere on the producer's
scoring path — and **structural impossibility** — a producer that cannot write a judgement.

⛔ **Both guards are green on the ubuntu CI matrix with NO third-party checkouts present.** They
read committed source and drive a constructor; neither touches the corpus.

⛔ **A guard here is never loosened to go green** (``DF-8-5-B``).
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path
from typing import Mapping

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from argus.detectors.assertion_strength import (  # noqa: E402
    ASSERTION_STRENGTH_BANDS,
    UNESTABLISHED,
)
from argus.precision.silent_class import SILENT_CLASS_RULE_ID, UNADJUDICATED  # noqa: E402
from argus.store.canonical import dumps, loads  # noqa: E402

from precision_preregistration import (  # noqa: E402
    CONSEQUENCE_BELOW,
    CONSEQUENCE_MET,
    CRITERION_OUTCOMES,
    SUCCESSOR_OUTPUT_PATHS,
    evaluate,
)
from successor_reach_model import (  # noqa: E402
    SUCCESSOR_RECORD_PATH,
    SuccessorReachRow,
    seed_successor_row,
)

#: ⛔ The two modules that make up this story's producer. ``-151`` walks BOTH: splitting the
#: record model out of the producer must not create a place a second derivation could hide.
_PRODUCER_MODULES: tuple[str, ...] = (
    "scripts/build_successor_reach_record.py",
    "scripts/successor_reach_model.py",
)

#: The committed adjudication set the population is re-derived from — Story 13.5's, READ.
_ADJUDICATION_SET = (
    _REPO_ROOT
    / "_bmad-output"
    / "design-artifacts"
    / "ArgusAgent"
    / "validation-corpus"
    / "adjudication-set-13-5.json"
)

#: ⛔ The names that ARE ``S1``'s conjuncts, the span scoring, and the statement boundary. Reaching
#: any of them directly from the producer is a SECOND derivation of a predicate that already has
#: exactly one public entry point, which is the ``AR7`` defect Epic 17 exists to close.
_CONJUNCT_NAMES: frozenset[str] = frozenset(
    {
        "s1_corroborated",
        "grade_span_assertions",
        "provenance_evidence",
        "span_provenance",
        "candidate_sut_edges",
        "body_statement_count",
        "logical_statement_count",
        "logical_statements",
        "opens_bare_assert",
        "is_assertion_callee",
        "span_asserts_anything",
        "assertion_statement_lines",
        "sut_call_classification",
        "result_observing_lines",
        "result_observing_blocks",
        "strength_ordinal",
    }
)

#: ⛔ A second GRAMMAR call. ``argus.index.ast_index`` is the SHIPPED index and is not one of
#: these; the bare ``ast`` module and ``compile`` are.
_GRAMMAR_MODULES: frozenset[str] = frozenset({"ast", "tree_sitter", "tree_sitter_languages"})
_GRAMMAR_CALLS: frozenset[str] = frozenset({"compile", "exec", "eval"})

#: ``S1``'s ONE public entry point, and the shipped fact-(b) reading called beside it.
_S1_ENTRY_ATTRIBUTE = "successor_evidence"
_FACT_B_READER = "score_span"


def _sources() -> dict[str, str]:
    return {
        name: (_REPO_ROOT / name).read_text(encoding="utf-8") for name in _PRODUCER_MODULES
    }


# ═════════════════════════════════════════════════════════════════════════════════════════
# The PURE predicate ``-151`` drives, exported so the RED demonstration hits the real seam
# ═════════════════════════════════════════════════════════════════════════════════════════


def second_derivation_offenders(sources: Mapping[str, str]) -> tuple[str, ...]:
    """Sources in, offenders out — PURE, so a mutation can drive the REAL seam.

    ``tests/test_vacuous_cross_language.py:169``'s ``_anchors_on_caret_or_dollar`` shape, reused:
    the guard below asserts this returns empty over the real modules, and then asserts it returns
    NON-empty over an EXECUTED in-memory mutation. A guard that re-implements its own predicate
    inside the assertion can only ever be driven against the re-implementation.

    An offender is one of three things, each a way the producer could acquire a second answer to
    *"does S1 corroborate this span"*:

    1. importing or calling a **second grammar** — the shipped index is the one parser;
    2. reaching a **conjunct** of ``S1`` (or of the span scoring, or of the statement boundary)
       directly instead of through the one public entry point;
    3. losing the entry point itself — a producer that never calls ``successor_evidence`` is not
       measuring the shipped predicate at all.
    """
    offenders: list[str] = []
    for name, source in sorted(sources.items()):
        tree = ast.parse(source)
        entry_calls = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in _GRAMMAR_MODULES:
                        offenders.append(f"{name}: imports the grammar module {alias.name!r}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in _GRAMMAR_MODULES:
                    offenders.append(f"{name}: imports from the grammar module {node.module!r}")
                for alias in node.names:
                    if alias.name in _CONJUNCT_NAMES:
                        offenders.append(
                            f"{name}: imports the S1 conjunct {alias.name!r} directly"
                        )
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name):
                    if func.id in _CONJUNCT_NAMES:
                        offenders.append(f"{name}: calls the S1 conjunct {func.id!r}")
                    elif func.id in _GRAMMAR_CALLS:
                        offenders.append(f"{name}: calls the grammar builtin {func.id!r}")
                elif isinstance(func, ast.Attribute):
                    if func.attr in _CONJUNCT_NAMES:
                        offenders.append(f"{name}: calls the S1 conjunct {func.attr!r}")
                    elif func.attr == _S1_ENTRY_ATTRIBUTE:
                        entry_calls += 1
        if entry_calls > 1:
            offenders.append(
                f"{name}: calls {_S1_ENTRY_ATTRIBUTE!r} {entry_calls} times; S1 is scored once "
                f"per span and a second call site is a second answer waiting to disagree"
            )
    total_entry_calls = sum(
        1
        for source in sources.values()
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == _S1_ENTRY_ATTRIBUTE
    )
    if total_entry_calls != 1:
        offenders.append(
            f"the producer calls {_S1_ENTRY_ATTRIBUTE!r} {total_entry_calls} time(s) across "
            f"{sorted(sources)}; it must be EXACTLY once — zero means S1 is not being measured "
            f"through its one public entry point at all."
        )
    return tuple(offenders)


def test_TC_ArgusAgent_PRECISION_001_151_S1_has_exactly_one_derivation() -> None:
    """TC-ArgusAgent-PRECISION-001-151 — AC5.1/AC5.2/AC5.3: ONE derivation of S1, and it is shipped.

    **Observable.** An ``ast`` walk over every module of this story's producer, classifying its
    imports and its call sites rather than grepping its text.

    **Defect it moves.** ``AR7`` — the fork. Story 17.3 made ``s1_corroborated`` and
    ``successor_evidence`` PUBLIC precisely so that Story 17.4 could measure the shipped predicate
    without re-deriving it, and its docstring says so: *"A private copy buried in the detector
    would force 17.4 to fork the predicate, which is the AR7 defect this epic exists to close."*
    A producer that re-parsed the source, re-graded the bands or re-resolved the SUT names would
    publish a reach for a predicate that is not the one that ships — and nothing downstream could
    tell.

    **Non-vacuity, asserted BEFORE the absence** (``-127``'s own move, reused). An ``ast`` walk
    that parsed zero files, or that failed to resolve a KNOWN-PRESENT outbound edge, reports *"no
    second derivation"* forever. So: both modules are parsed, both resolve their known-present
    edge to ``argus.detectors.assertion_strength``, and the predicate is driven to BOTH outcomes
    by an EXECUTED mutation — ⛔ **in memory, never on disk**, because the tree is shared with a
    peer session.
    """
    sources = _sources()

    # ── Non-vacuity 1: the walk actually parsed both modules and they are not stubs. ──
    assert set(sources) == set(_PRODUCER_MODULES), f"the walk parsed {sorted(sources)}"
    for name, source in sources.items():
        assert len(source.splitlines()) > 100, f"{name} is a stub; the walk proves nothing"

    # ── Non-vacuity 2: each module's KNOWN-PRESENT outbound edge to the grader resolves. ──
    for name, source in sources.items():
        edges = {
            node.module
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert "argus.detectors.assertion_strength" in edges, (
            f"{name} does not resolve its known-present outbound edge to "
            f"argus.detectors.assertion_strength, so this walk's import resolution is broken and "
            f"every absence it reports below is meaningless. Fix the walk, never the assertion."
        )

    # ── THE CLAIM. ──
    assert second_derivation_offenders(sources) == (), (
        f"{second_derivation_offenders(sources)!r}. S1 has exactly ONE derivation and it is the "
        f"shipped one: VacuousTestDetector.successor_evidence, composition-only over the public "
        f"assertion_strength.s1_corroborated and grade_span_assertions. Do not re-implement a "
        f"conjunct here and do not port research/investigate-per-call-scoping.py."
    )

    # ── Non-vacuity 3: the predicate driven RED by an EXECUTED, in-memory mutation. ──
    producer = _PRODUCER_MODULES[0]
    mutated = dict(sources)
    mutated[producer] = "import ast\n" + sources[producer]
    assert second_derivation_offenders(mutated), (
        "the predicate did NOT flag a producer that imports the bare ast module, so it is not "
        "watching for a second grammar at all"
    )

    mutated = dict(sources)
    mutated[producer] = sources[producer].replace(
        "score = score_span(source_lines, edges, start, end)",
        "score = score_span(source_lines, edges, start, end)\n"
        "            _forked = s1_corroborated(source_lines, edges, start, end)",
        1,
    )
    assert mutated[producer] != sources[producer], "the mutation anchor moved; re-anchor it"
    assert second_derivation_offenders(mutated), (
        "the predicate did NOT flag a producer that calls s1_corroborated directly beside the "
        "entry point, which is the exact fork this guard exists to catch"
    )

    mutated = dict(sources)
    mutated[producer] = sources[producer].replace(
        "VacuousTestDetector.successor_evidence(source_lines, edges, start, end)",
        "_locally_reimplemented(source_lines, edges, start, end)",
        1,
    )
    assert mutated[producer] != sources[producer], "the entry-point anchor moved; re-anchor it"
    assert second_derivation_offenders(mutated), (
        "the predicate did NOT flag a producer that stopped calling successor_evidence "
        "altogether — a producer that never reaches the one public entry point is measuring "
        "something else and reporting it as S1"
    )

    # ── And the shipped fact-(b) reader is called BESIDE it, exactly once. ──
    fact_b_calls = sum(
        1
        for source in sources.values()
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == _FACT_B_READER
    )
    assert fact_b_calls == 1, (
        f"the shipped fact (b) reader {_FACT_B_READER!r} is called {fact_b_calls} time(s); it is "
        f"called ONCE, on the SAME (source_lines, span_edges, start, end) tuple S1 was scored on "
        f"— one span resolution, two readings, and silent_class.SpanScore is NOT widened to "
        f"carry s1_corroborated (Story 17.3 §0.7; DETECT-001-119; -143)."
    )


# ═════════════════════════════════════════════════════════════════════════════════════════
# The row: a producer that CANNOT write a judgement, proved by driving it
# ═════════════════════════════════════════════════════════════════════════════════════════


class _Evidence:
    """A stand-in ``SuccessorVacuityEvidence`` — the shipped one is a frozen NamedTuple."""

    def __init__(self, *, s1: bool = True, none: int = 1) -> None:
        self.assertions_none = none
        self.assertions_existence = 0
        self.assertions_value = 0
        self.assertions_unestablished = 0
        self.s1_corroborated = s1


class _Score:
    def __init__(self) -> None:
        self.discarded_sut_calls = 1
        self.consumed_sut_calls = 0
        self.mock_referencing_assertions = 0


def _seed(**overrides: object) -> SuccessorReachRow:
    kwargs: dict[str, object] = {
        "member_id": "minions",
        "rule_id": SILENT_CLASS_RULE_ID,
        "locator": "tests/test_thing.py:12",
        "test_name": "test_thing",
        "pinned_sha": "ec63b7293b7036bf910a0d1b5e61aba7dc551526",
        "evidence": _Evidence(),
        "score": _Score(),
        "shipped_verdict_eligible": False,
    }
    kwargs.update(overrides)
    return seed_successor_row(**kwargs)  # type: ignore[arg-type]


def test_TC_ArgusAgent_PRECISION_001_149_the_producer_cannot_write_a_judgement() -> None:
    """TC-ArgusAgent-PRECISION-001-149 — AC7.1/AC7.2: UNADJUDICATED is the only reachable state.

    **Observable.** The row constructor and the only seeding function the producer can reach,
    DRIVEN — not read.

    **Defect it moves.** *"The automation tagged its own findings TP."* Protocol §2 registers
    ``UNADJUDICATED`` as the ONLY disposition an automated producer may write, and protocol §4's
    ladder has no third rung while ``AI-E16-7`` is UNFILLED. This story therefore adjudicates
    nothing (``DN-17-4-2``), and *"nothing was adjudicated"* is worth far more as a structural
    impossibility than as a promise in a docstring.

    **Non-vacuity.** The happy path is asserted FIRST — a seeded row really is produced and really
    does carry ``UNADJUDICATED`` — so the refusals below are refusals of something the constructor
    can otherwise do, not of a constructor that raises on everything.
    """
    # ── Non-vacuity: the constructor WORKS, and its default state is the honest one. ──
    row = _seed()
    assert row.disposition == UNADJUDICATED
    assert row.adjudicator is None and row.adjudicated_on is None and row.reason is None
    assert row.verdict_eligible is False and row.advisory is True
    assert row.row_id and "." in row.row_id, "the row id must be the derived content-addressed one"

    # ── seed_successor_row has NO parameter that could carry a judgement. ──
    import inspect

    parameters = set(inspect.signature(seed_successor_row).parameters)
    assert not parameters & {"disposition", "adjudicator", "adjudicated_on", "reason", "idiom"}, (
        f"seed_successor_row exposes {sorted(parameters)}; a producer that CAN write a judgement "
        f"has already made 'the automation judged its own findings' a failure mode a reviewer "
        f"has to watch for."
    )

    # ── And the row itself REFUSES one, driven to each refusal. ──
    for field, value in (
        ("disposition", "TP"),
        ("disposition", "FP"),
        ("adjudicator", "XAgent007 (Engineering Lead)"),
        ("adjudicated_on", "2026-08-25"),
        ("verdict_eligible", True),
    ):
        base = {
            "row_id": row.row_id,
            "member_id": row.member_id,
            "rule_id": row.rule_id,
            "locator": row.locator,
            "test_name": row.test_name,
            "pinned_sha": row.pinned_sha,
            "assertions_none": 1,
            "assertions_existence": 0,
            "assertions_value": 0,
            "assertions_unestablished": 0,
            "discarded_sut_calls": 1,
            "consumed_sut_calls": 0,
            "mock_referencing_assertions": 0,
            "shipped_verdict_eligible": False,
        }
        base[field] = value
        with pytest.raises(ValueError):
            SuccessorReachRow(**base)  # type: ignore[arg-type]

    # ── A span S1 does NOT corroborate cannot be seeded: the yield floor's numerator is the
    #    one count this story exists to measure honestly. ──
    with pytest.raises(ValueError):
        _seed(evidence=_Evidence(s1=False))

    # ── A non-portable locator is refused on BOTH legs of the CI split (AI-E13-1). ──
    for bad in ("D:/x/tests/test_thing.py:12", "tests\\test_thing.py:12", "/abs/test.py:12"):
        with pytest.raises(ValueError):
            _seed(locator=bad)
