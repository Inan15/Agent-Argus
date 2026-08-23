"""Story 16.7 — guards over the SILENT test class PREDICATE and its containment.

WHY THIS FILE EXISTS. ``argus/precision/silent_class.py`` derives a class of 36 test spans
that reach the system under test, discard the result, and assert nothing at all, and it
publishes them as a QUESTION for a named human. Three separate things can go wrong with
that, and a guard exists here for each:

1. **The derivation could quietly fork the detector's arithmetic or its vocabulary.** It
   composes four shipped helpers, and ``-126`` walks the module's own source to assert it
   contains no second AST-based SUT-call counter and no second assertion-name regex.
2. **The predicate could leak into the detector path and become a shipped promotion.**
   ``-127`` walks the whole ``argus/**`` import graph and asserts the edge runs ONE WAY.
3. **A machine could start answering the human's question.** ``-125`` asserts that the only
   row constructor a producer can reach is structurally incapable of writing a ``TP``, an
   ``FP`` or a ``BORDERLINE``.

⛔ GUARD-ADEQUACY CLAUSE, discharged here rather than promised (``architecture.md``
section Enforcement). Every case below names its OBSERVABLE, is driven RED at the REAL SEAM
by an executed mutation — a real ``build_ast_index`` over real files on disk and the real
``provenance_evidence``, never a reconstruction — and ``-128`` generates its adversarial
variants from the shipped assertion table itself rather than hand-listing them, with the
generated count asserted.

⛔ THE LOCKSTEP TRAP, and this file's specific answer to it. A fixture whose silence changes
because a LINE WAS ADDED OR REMOVED is a fixture in which the numerator and the denominator
both moved; the case then measures the fixture, not the predicate. So the predicate cases
here vary ONE coordinate with everything else PINNED: they score the SAME fixture text
under the shipped WIDE vocabulary and under the FROZEN one, and
:func:`_assert_isolates_the_predicate` asserts that ``statement_count`` and
``discarded_sut_calls`` came out EQUAL across the pair while ``asserts_anything`` differed.
Equal counts on both sides is what makes the difference attributable to the predicate.

⛔ NON-VACUITY IS CHECKED FIRST, EVERY TIME (``AI-E11-1``). Every case asserts its population
is non-empty and its seam reachable — the index really emitted the edges the case is about,
``discarded_sut_calls >= 1``, ``statement_count > 0`` — BEFORE asserting anything about it.
A derivation that returns an empty class passes a *"nothing was promoted"* guard forever,
and an import walk that silently parsed zero files passes a *"nothing imports it"* guard
forever. Both are guarded against below by asserting the walk found something first.

⛔ WHAT THIS FILE DELIBERATELY DOES NOT ASSERT. Nothing here says anything about
``argus/precision/gate_*.py``, and nothing here imports ``gate_decision``. That the gate did
not move is discharged by the NINE EXISTING ``tests/test_gate_*.py`` files staying green and
by both existing builders exiting 0 under ``--check``. Forking a guard that already exists
is the ``AR7`` defect, and it is the defect this whole story is about.

⛔ WHY THIS FILE IS A PAIR. NFR-M1 caps a module at 1,200 physical lines, and the guards
this story needs do not fit in one. They are split along the seam the story itself is built
on (``AR8``): the PREDICATE and its containment live here, and the RECORD — its two closed
vocabularies, its derived figures and the builder that writes it — lives in
``tests/test_silent_class_record.py``, which IMPORTS the fixture plumbing from here rather
than copying it. A second copy of a fixture is the fork class this repository has already
rotted from twice. Splitting is the remedy NFR-M1 prescribes; shaving is not, and an
``_EXEMPT_BY_DESIGN`` entry is forbidden outright — ``MAINT-001-04`` lets that registry
shrink only.

Verification area: precision validation — the silent-class PREDICATE
(``TC-ArgusAgent-PRECISION-001-115`` .. ``-118``, ``-126`` .. ``-128``). The record's half is
``-119`` .. ``-125`` and ``-129`` .. ``-132``.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

from argus.detectors import vacuous_vocabulary
from argus.detectors.provenance_scan import opens_bare_assert, provenance_evidence
from argus.detectors.vacuous_test import index_aligned_lines
from argus.detectors.vacuous_vocabulary import (
    _ASSERTION_CALLEES,
    _ASSERTION_NAMING_CONVENTION,
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
    is_assertion_callee,
)
from argus.index.ast_index import build_ast_index
from argus.precision import adjudication, silent_class
from argus.precision.silent_class import (
    SILENT_CLASS_RECORD_PATH,
    SILENT_CLASS_RULE_ID,
    SILENT_CLASS_WORKLIST_PATH,
    SilentClassRecord,
    SilentClassRow,
    SpanScore,
    definitions_by_start_line,
    rows_from_payload,
    score_span,
    span_asserts_anything,
    span_edges_of,
)
from argus.store.canonical import loads

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "scripts") not in sys.path:  # pragma: no cover - test bootstrap
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

_MODULE_SOURCE_PATH = _REPO_ROOT / "argus" / "precision" / "silent_class.py"
_BUILDER_SOURCE_PATH = _REPO_ROOT / "scripts" / "build_silent_class_record.py"
_RECORD_PATH = _REPO_ROOT / SILENT_CLASS_RECORD_PATH
_WORKLIST_PATH = _REPO_ROOT / SILENT_CLASS_WORKLIST_PATH

# ── The fixture pair. ONE text, scored two ways. ─────────────────────────────────────────
#
# ``test_silent_control`` and ``test_silent_member`` are deliberately IDENTICAL in shape:
# three bare-call statements each, so ``statement_count`` and ``discarded_sut_calls`` come
# out equal, and the ONLY thing that differs is whether one of those callees is a name the
# assertion vocabulary recognises. ``toEqual`` is in the WIDE table, is NOT in the frozen
# corroboration table, and does NOT match the ``_?assert\w*`` naming convention — which is
# what makes it able to isolate the vocabulary coordinate on its own.
_FIXTURE = '''def test_silent_control():
    prepare_fixture()
    build_widget()
    toEqual(1, 1)


def test_silent_member():
    prepare_fixture()
    build_widget()
    finish_up()


def test_bare_assert_is_an_assertion():
    prepare_fixture()
    build_widget()
    assert True


def test_raise_assertion_error_is_an_assertion():
    prepare_fixture()
    build_widget()
    raise AssertionError("boom")


def test_reaches_no_sut_at_all():
    value = 1
    other = value


def test_underscore_naming_convention():
    prepare_fixture()
    build_widget()
    _assert_shape(1)
'''


class _Scored:
    """One scored fixture span, with everything a non-vacuity preamble needs."""

    def __init__(self, name: str, score: SpanScore, edges: tuple, start: int, end: int) -> None:
        self.name = name
        self.score = score
        self.edges = edges
        self.start = start
        self.end = end


def _score_fixture(tmp_path: Path, source: str = _FIXTURE) -> dict[str, _Scored]:
    """Score *source* AT THE REAL SEAM: a real file, a real index, the real provenance scan.

    Nothing is reconstructed and nothing is stubbed. ``build_ast_index`` parses the file off
    disk with the shipped grammar, ``score_span`` calls the shipped ``provenance_evidence``,
    ``body_statement_count``, ``opens_bare_assert`` and ``is_assertion_callee``. A guard
    that scored a hand-built edge list would be measuring its own fixture builder.
    """
    target = tmp_path / "t.py"
    target.write_text(source, encoding="utf-8")
    index = build_ast_index(str(tmp_path), ("t.py",))
    entry = index.entries[0]
    assert not entry.parse_failed, f"the fixture did not parse: {entry.parse_failure_reason!r}"
    assert entry.ast_eligible, "the fixture is not AST-eligible; the seam is not reachable"
    assert entry.edges, "the index emitted ZERO edges: this case would measure nothing"
    lines = index_aligned_lines(source)
    out: dict[str, _Scored] = {}
    for definition in definitions_by_start_line(entry).values():
        edges = span_edges_of(entry, definition)
        out[definition.name] = _Scored(
            name=definition.name,
            score=score_span(lines, edges, definition.start_line, definition.end_line),
            edges=edges,
            start=definition.start_line,
            end=definition.end_line,
        )
    return out


def _assert_seam_is_reachable(scored: _Scored) -> None:
    """The NON-VACUITY PREAMBLE (``AI-E11-1``) — asserted BEFORE anything else, every time."""
    assert scored.edges, f"{scored.name}: the index emitted no edges inside the span"
    assert scored.score.statement_count > 0, f"{scored.name}: the span has no statements"
    assert scored.score.discarded_sut_calls >= 1, (
        f"{scored.name}: discarded_sut_calls is 0, so the span does not reach the seam this "
        f"case is about and every assertion below would be vacuously true"
    )


def _assert_isolates_the_predicate(member: _Scored, control: _Scored) -> None:
    """The LOCKSTEP guard: the pair differs in the PREDICATE, not in the fixture's SHAPE.

    ``statement_count`` and ``discarded_sut_calls`` are asserted EQUAL across the pair. If
    they were not, the difference in membership could be explained by the fixture having
    grown or shrunk, and the case would be measuring the fixture rather than the predicate.
    """
    assert member.score.statement_count == control.score.statement_count, (
        f"lockstep: {member.name} has {member.score.statement_count} statement(s) and "
        f"{control.name} has {control.score.statement_count}. The pair must differ ONLY in "
        f"whether the span asserts; a shape difference makes the comparison meaningless."
    )
    assert member.score.discarded_sut_calls == control.score.discarded_sut_calls, (
        f"lockstep: {member.name} discards {member.score.discarded_sut_calls} SUT call(s) "
        f"and {control.name} discards {control.score.discarded_sut_calls}"
    )
    assert member.score.asserts_anything != control.score.asserts_anything, (
        "the pair does not differ on the coordinate under test at all"
    )


def _committed_record_payload() -> dict:
    assert _RECORD_PATH.is_file(), (
        f"{SILENT_CLASS_RECORD_PATH} is absent. Every case below would then assert over an "
        f"empty population and pass forever (AI-E11-1)."
    )
    return loads(_RECORD_PATH.read_text(encoding="utf-8"))


def _committed_rows() -> tuple[SilentClassRow, ...]:
    rows = rows_from_payload(_committed_record_payload())
    assert rows, "the committed silent-class record carries ZERO rows"
    return rows


def _record_of(rows: tuple[SilentClassRow, ...]) -> SilentClassRecord:
    """A record over *rows*, with header fields that are not what any case is about."""
    return SilentClassRecord(
        protocol_version="V1.3",
        adjudication_unit=adjudication.ADJUDICATION_UNIT,
        class_definition=silent_class.SILENT_CLASS_DEFINITION,
        derivation_source="test fixture",
        derivation_method="test fixture",
        population_walked=max(len(rows), 1),
        population_skipped=0,
        expert_hours=None,
        expert_hours_note="test fixture",
        transcription_note="test fixture",
        rows=rows,
    )


def _judged(row: SilentClassRow, disposition: str, idiom: str, who: str) -> SilentClassRow:
    """A HUMAN judgement, constructed in a test and never by any production path.

    This is the shape ``-125`` proves no producer can reach. It exists here because a
    vocabulary that is never exercised in the human direction is a vocabulary whose human
    branch is untested, and because AC5.2's orthogonality claim needs a row that is both
    ``FP`` and ``DELIBERATE_SMOKE_TEST`` to actually exist.
    """
    return SilentClassRow(
        row_id=row.row_id,
        member_id=row.member_id,
        rule_id=row.rule_id,
        verdict_eligible=row.verdict_eligible,
        advisory=row.advisory,
        locator=row.locator,
        test_name=row.test_name,
        discarded_sut_calls=row.discarded_sut_calls,
        consumed_sut_calls=row.consumed_sut_calls,
        pinned_sha=row.pinned_sha,
        disposition=disposition,
        idiom=idiom,
        adjudicator=who,
        adjudicated_on="2026-08-23",
        reason="test fixture judgement, authored in a test and never by a producer",
    )


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC1 — the class, as derived and as published.
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_115_the_published_class_is_the_measured_class() -> None:
    """TC-ArgusAgent-PRECISION-001-115 — AC1.1/AC1.2/AC1.4/AC4.1: what was published.

    **Observable:** the membership, the per-member split, the file spread and the per-row
    fields of the committed ``silent-class-record.json``.

    **Defect it moves:** a derivation that drifts — from the recorded 1,032-finding
    population, from the 36 members measured at HEAD, or from the agent-smith 22 +
    minions 14 split — changes these numbers, and a re-run of the builder that produced a
    different class would leave this record stale and this case RED.

    Non-vacuity first: the record exists and carries rows before anything is asserted about
    them, because every claim below is vacuously true over an empty record.
    """
    payload = _committed_record_payload()
    rows = _committed_rows()
    assert len(rows) == 36, f"the silent class is {len(rows)} member(s), not 36"
    assert payload["population_walked"] == 1032, (
        f"the derivation walked {payload['population_walked']} finding(s); the committed "
        f"adjudication-set-13-5.json records 1,032 vacuous_test_heuristic findings and the "
        f"class must be derived over ALL of them"
    )
    assert payload["population_skipped"] == 0, "0 skipped and 0 unresolvable is the contract"
    by_member: dict[str, int] = {}
    for row in rows:
        by_member[row.member_id] = by_member.get(row.member_id, 0) + 1
    assert by_member == {"agent-smith": 22, "minions": 14}, by_member
    files = {member: set() for member in by_member}
    for row in rows:
        files[row.member_id].add(row.locator.rpartition(":")[0])
    assert {member: len(paths) for member, paths in files.items()} == {
        "agent-smith": 10,
        "minions": 9,
    }
    assert len({row.finding_id for row in rows}) == 36, "the 36 finding ids are not distinct"
    for row in rows:
        assert row.rule_id == SILENT_CLASS_RULE_ID
        assert row.verdict_eligible is False, "NOTHING is promoted by this story"
        assert row.advisory is True
        assert row.discarded_sut_calls >= 1, f"{row.locator}: the predicate needs disc >= 1"
        assert row.test_name.strip(), f"{row.locator}: no test name"
        assert row.pinned_sha.strip(), f"{row.locator}: no pinned sha"


def test_TC_ArgusAgent_PRECISION_001_116_the_silence_question_uses_the_WIDE_table() -> None:
    """TC-ArgusAgent-PRECISION-001-116 — AC2.1/AC7.1(ii)/AC7.3: ``DN-14-2-1``, executable.

    **Observable:** ``SpanScore.asserts_anything`` for a span whose only assertion is a
    callee the WIDE table knows and the FROZEN table does not.

    **Defect it moves:** routing *"does this span assert anything at all?"* through
    ``_CORROBORATION_ASSERTION_CALLEES`` — the mutation AC7.1(ii) names. Under the frozen
    table ``toEqual`` is invisible, the control span is scored assertion-free, and a test
    that plainly asserts enters a class published to a human as SILENT. That is the false
    accusation the two-table split exists to prevent, reached from the other side, and this
    case is it made executable rather than argued.

    **The pair isolates the predicate:** control and member are scored from the SAME file
    with the SAME shape, and their ``statement_count`` and ``discarded_sut_calls`` are
    asserted equal — so the membership difference cannot be explained by the fixture.
    """
    scored = _score_fixture(_tmp())
    control = scored["test_silent_control"]
    member = scored["test_silent_member"]
    _assert_seam_is_reachable(control)
    _assert_seam_is_reachable(member)
    _assert_isolates_the_predicate(member, control)

    assert member.score.is_silent_class_member, "the silent fixture is not scored a member"
    assert not control.score.is_silent_class_member, (
        "the control asserts through toEqual and must NOT be a member"
    )
    # The vocabulary coordinate, moved on its own over the SAME edges.
    assert is_assertion_callee("toEqual"), "toEqual left the WIDE table; the fixture is stale"
    assert "toEqual" not in _CORROBORATION_ASSERTION_CALLEES, (
        "toEqual entered the FROZEN table; this case can no longer isolate the vocabulary"
    )
    assert not _ASSERTION_NAMING_CONVENTION.match("toEqual"), (
        "toEqual now matches the naming convention, so removing it from the table would "
        "not change is_assertion_callee and this case would stop measuring anything"
    )
    frozen_only_silence = not any(
        edge.callee in _CORROBORATION_ASSERTION_CALLEES for edge in control.edges
    ) and not any(
        opens_bare_assert(line.strip())
        for line in index_aligned_lines(_FIXTURE)[control.start - 1 : control.end]
    )
    assert frozen_only_silence, (
        "the frozen-table mutation must make the control span look SILENT; if it does not, "
        "this case is not exercising DN-14-2-1 at all"
    )


def test_TC_ArgusAgent_PRECISION_001_117_the_assertion_error_name_is_load_bearing() -> None:
    """TC-ArgusAgent-PRECISION-001-117 — AC1.3/AC7.1(i)/AC7.3: the 39 -> 36 mechanism.

    **Observable:** ``asserts_anything`` for a span whose only assertion is
    ``raise AssertionError(...)``.

    **Defect it moves:** removing ``"AssertionError"`` from the WIDE table — the mutation
    AC7.1(i) names. Story 16.6 added that name and its addition removed exactly THREE false
    accusations from this class (39 -> 36, measured at HEAD, and the three named in the
    story record). This case drives the same mutation at the same seam over a real span: the
    span flips from asserting to silent, and the class it belongs to grows by one.

    The mutation is applied to the module GLOBAL and restored in a ``finally``, so the tree
    is never edited and no other case can observe the mutated table.
    """
    scored = _score_fixture(_tmp())
    raising = scored["test_raise_assertion_error_is_an_assertion"]
    member = scored["test_silent_member"]
    _assert_seam_is_reachable(raising)
    _assert_seam_is_reachable(member)
    assert "AssertionError" in _ASSERTION_CALLEES, "16.6's name is gone from the wide table"
    assert not raising.score.is_silent_class_member, (
        "a span whose only assertion is `raise AssertionError(...)` must NOT be in the "
        "silent class: that is precisely the false accusation Story 16.6 removed"
    )

    original = vacuous_vocabulary._ASSERTION_CALLEES
    try:
        vacuous_vocabulary._ASSERTION_CALLEES = frozenset(original - {"AssertionError"})
        mutated = _score_fixture(_tmp())["test_raise_assertion_error_is_an_assertion"]
    finally:
        vacuous_vocabulary._ASSERTION_CALLEES = original
    assert len(vacuous_vocabulary._ASSERTION_CALLEES) == len(original), "restoration failed"

    assert mutated.score.is_silent_class_member, (
        "with AssertionError removed, the raising span must fall INTO the silent class - "
        "that is the 39 -> 36 delta, at the real seam. If it does not move, this guard "
        "cannot fail and proves nothing."
    )
    _assert_isolates_the_predicate(mutated, raising)


def test_TC_ArgusAgent_PRECISION_001_118_the_discard_conjunct_is_load_bearing() -> None:
    """TC-ArgusAgent-PRECISION-001-118 — AC7.1(iii)/AC7.3: dropping ``disc >= 1``.

    **Observable:** membership of a span that asserts nothing and reaches NO system under
    test at all.

    **Defect it moves:** the mutation AC7.1(iii) names — dropping the ``disc >= 1``
    conjunct, which over the real corpus grows the class from 36 towards the 45 spans that
    assert nothing at ANY discard count. Here the same movement is shown at the real seam:
    ``test_reaches_no_sut_at_all`` asserts nothing and is correctly NOT a member, and it
    becomes one the instant the conjunct is dropped.

    This case is deliberately the one place the non-vacuity preamble is applied to the
    CONTROL rather than the subject: the subject's whole point is that ``disc == 0``.
    """
    scored = _score_fixture(_tmp())
    no_sut = scored["test_reaches_no_sut_at_all"]
    member = scored["test_silent_member"]
    _assert_seam_is_reachable(member)
    assert no_sut.score.statement_count > 0, "the disc==0 fixture has no statements at all"
    assert no_sut.score.discarded_sut_calls == 0, "the disc==0 fixture reaches a SUT"
    assert not no_sut.score.asserts_anything, "the disc==0 fixture asserts something"
    assert not no_sut.score.is_silent_class_member, (
        "a span that reaches no SUT is not a silent-class member: the class is about a "
        "result that was PRODUCED and thrown away, not about a test that produces nothing"
    )
    without_conjunct = not no_sut.score.asserts_anything
    assert without_conjunct, (
        "dropping the disc >= 1 conjunct must ADMIT this span - if it would not, the "
        "conjunct is doing no work and AC7.1(iii)'s mutation is unobservable"
    )
    assert member.score.is_silent_class_member and member.score.discarded_sut_calls >= 1


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC2 — the structural cases. Composition, and the one-way edge.
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_126_the_predicate_is_composed_not_reimplemented() -> None:
    """TC-ArgusAgent-PRECISION-001-126 — AC2.1: no second walk, no second scanner.

    **Observable:** an ``ast`` walk of ``argus/precision/silent_class.py``'s OWN source.

    **Defect it moves:** the ``AR7`` fork. *"Two spellings of 'is this an assert line' is
    exactly the disagreement class this detector keeps closing elsewhere."* A second
    AST-based SUT-call counter or a second assertion-name regex in this module would drift
    from the detector's, and the drift would be invisible until the two published different
    numbers about the same span. The ``TC-ArgusAgent-PRECISION-001-87`` / ``-99`` shape.

    Non-vacuity first: the walk must have parsed a non-trivial module before any *"it does
    not contain"* assertion means anything.
    """
    source = _MODULE_SOURCE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    assert len(functions) >= 10, (
        f"the walk found only {len(functions)} function(s); it is not parsing the module "
        f"this case is about, and every absence assertion below would pass vacuously"
    )

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert "ast" not in imported, "the module imports `ast`: it is walking something itself"
    assert "re" not in imported, (
        "the module imports `re`: an assertion-name regex here would be a second vocabulary"
    )
    assert "ast.walk" not in source and "ast.parse" not in source

    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    for shipped in ("provenance_evidence", "is_assertion_callee", "opens_bare_assert",
                    "body_statement_count", "assess_independence", "expert_hours_report",
                    "finding_row_id"):
        assert shipped in called, (
            f"{shipped} is imported but never CALLED. The composition claim is that these "
            f"are used, not that they are named in an import line."
        )

    # The silence question must not reach the FROZEN table. Scoped to the ONE function that
    # answers it, because the frozen table is legitimately named elsewhere in this module
    # (fact (b)'s own arithmetic, inside span_provenance).
    silence = next(fn for fn in functions if fn.name == "span_asserts_anything")
    silence_names = {n.id for n in ast.walk(silence) if isinstance(n, ast.Name)}
    assert "_CORROBORATION_ASSERTION_CALLEES" not in silence_names, (
        "span_asserts_anything reaches the FROZEN corroboration table. DN-14-2-1: that "
        "table answers 'does this CORROBORATE the SUT result', and routing 'does this "
        "assert anything at all' through it manufactures false accusations."
    )
    assert "is_assertion_callee" in silence_names, (
        "span_asserts_anything does not call is_assertion_callee at all"
    )
    provenance = next(fn for fn in functions if fn.name == "span_provenance")
    provenance_names = {n.id for n in ast.walk(provenance) if isinstance(n, ast.Name)}
    assert "_CORROBORATION_ASSERTION_CALLEES" in provenance_names, (
        "fact (b)'s own arithmetic must keep using the FROZEN table; passing the wide one "
        "there would fork provenance_evidence's meaning, which is the mirror-image defect"
    )


def test_TC_ArgusAgent_PRECISION_001_127_the_import_edge_runs_one_way() -> None:
    """TC-ArgusAgent-PRECISION-001-127 — AC2.3: the predicate is unreachable from the detector.

    **Observable:** an ``ast`` walk over EVERY ``argus/**`` module, resolved transitively.

    **Defect it moves:** a scoring predicate that scores test functions becoming a shipped
    promotion because somebody imported it from the detector package or from the gate. The
    class this module derives is explicitly NOT ready to be promoted — its true-positive
    proportion is unmeasured, and it is known to contain deliberate smoke tests. One import
    line is the whole distance between *"a question for a human"* and *"a shipped verdict"*.

    Non-vacuity first, and it is the specific way this guard would go quietly dead: a walk
    that parsed zero files, or that failed to resolve the module's own known-present
    outbound edge, would report *"nothing imports it"* forever.
    """
    package_root = _REPO_ROOT / "argus"
    edges: dict[str, set[str]] = {}
    for path in sorted(package_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(_REPO_ROOT).as_posix()
        edges[rel] = set()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if name.startswith("argus."):
                    parts = name.split(".")
                    edges[rel].add("/".join(parts) + ".py")
                    edges[rel].add("/".join(parts) + "/__init__.py")

    target = "argus/precision/silent_class.py"
    assert len(edges) >= 60, f"the walk parsed only {len(edges)} module(s); it is not working"
    assert target in edges, f"{target} was not parsed at all"
    assert "argus/precision/adjudication.py" in edges[target], (
        "the walk did not resolve the module's own KNOWN outbound edge to adjudication.py, "
        "so its resolution is broken and every absence below is meaningless"
    )

    reaching = {source for source, targets in edges.items() if target in targets}
    changed = True
    while changed:
        changed = False
        for source, targets in edges.items():
            if source in reaching:
                continue
            if targets & reaching:
                reaching.add(source)
                changed = True

    fenced = {
        path
        for path in edges
        if path.startswith("argus/detectors/")
        or path.startswith("argus/precision/gate_")
        or path
        in {
            "argus/precision/adjudication.py",
            "argus/precision/replay_harness.py",
            "argus/precision/__init__.py",
        }
    }
    assert len(fenced) >= 12, f"the fenced set is only {len(fenced)} module(s); it is stale"
    violations = sorted(fenced & reaching)
    assert not violations, (
        f"{violations!r} reach {target}, directly or transitively. The edge must run ONE "
        f"WAY: this module imports the detector and the record, and nothing on the "
        f"detector or gate path imports it. A predicate in the detector package is a "
        f"promotion waiting for someone to wire it up."
    )
    assert target not in reaching, "the module reaches itself; the closure is wrong"


def test_TC_ArgusAgent_PRECISION_001_128_the_adversarial_variants_are_GENERATED() -> None:
    """TC-ArgusAgent-PRECISION-001-128 — AC7.4: variants from the table, not hand-listed.

    **Observable:** one real fixture file per WIDE-only assertion callee that the naming
    convention does NOT already catch, scored at the real seam, with the generated COUNT
    asserted.

    **Defect it moves:** a hand-picked adversarial example that happens to be the one case
    the implementation handles. The population here is CLOSED OVER by the guard — it is
    derived from ``_ASSERTION_CALLEES`` minus ``_CORROBORATION_ASSERTION_CALLEES`` minus the
    names the convention already matches — so a name entering or leaving the wide table
    changes the count and re-runs the adversary automatically. That is the third part of the
    guard-adequacy clause.
    """
    generated = sorted(
        name
        for name in _ASSERTION_CALLEES - _CORROBORATION_ASSERTION_CALLEES
        if not _ASSERTION_NAMING_CONVENTION.match(name)
        and name.isidentifier()
        and name not in _MOCK_CALLEES
    )
    assert len(generated) >= 30, (
        f"only {len(generated)} adversarial variant(s) were generated from the wide table; "
        f"the population is too small to be closing over anything"
    )
    assert "toEqual" in generated and "AssertionError" in generated

    body = "".join(
        f"def test_generated_{index}():\n"
        f"    prepare_fixture()\n"
        f"    build_widget()\n"
        f"    {name}(1)\n\n\n"
        for index, name in enumerate(generated)
    )
    scored = _score_fixture(_tmp(), body)
    assert len(scored) == len(generated), (
        f"the index resolved {len(scored)} of {len(generated)} generated span(s); the "
        f"adversary is not reaching the seam"
    )
    silent_members = []
    for index, name in enumerate(generated):
        case = scored[f"test_generated_{index}"]
        _assert_seam_is_reachable(case)
        if case.score.is_silent_class_member:
            silent_members.append(name)
    assert not silent_members, (
        f"{len(silent_members)} generated span(s) asserting through a registered WIDE name "
        f"were scored SILENT: {silent_members[:5]!r}. Every one of those would be a false "
        f"accusation published to a human as a test that asserts nothing."
    )


# ── fixture plumbing ─────────────────────────────────────────────────────────────────────


def _tmp() -> Path:
    """A fresh scratch directory per scoring run — real files, because the seam is real."""
    import tempfile

    return Path(tempfile.mkdtemp(prefix="argus-silent-class-"))


def test_the_fixture_pair_itself_is_honest() -> None:
    """The fixture the predicate cases lean on is checked before they lean on it.

    Not a numbered verification case: a preamble. If ``_FIXTURE`` ever stopped producing a
    genuine member and a genuine control with equal shape, ``-116`` through ``-128`` would
    keep passing while measuring nothing, which is precisely the failure mode this file's
    docstring is about.
    """
    scored = _score_fixture(_tmp())
    assert set(scored) >= {
        "test_silent_control",
        "test_silent_member",
        "test_bare_assert_is_an_assertion",
        "test_raise_assertion_error_is_an_assertion",
        "test_reaches_no_sut_at_all",
        "test_underscore_naming_convention",
    }
    assert scored["test_silent_member"].score.is_silent_class_member
    assert not scored["test_silent_control"].score.is_silent_class_member
    assert not scored["test_bare_assert_is_an_assertion"].score.is_silent_class_member
    assert not scored["test_underscore_naming_convention"].score.is_silent_class_member
    assert span_asserts_anything(
        index_aligned_lines(_FIXTURE),
        scored["test_bare_assert_is_an_assertion"].edges,
        scored["test_bare_assert_is_an_assertion"].start,
        scored["test_bare_assert_is_an_assertion"].end,
    ), "the bare-assert spelling is not recognised; opens_bare_assert is not being reached"
    evidence = provenance_evidence(
        index_aligned_lines(_FIXTURE),
        list(scored["test_silent_member"].edges),
        scored["test_silent_member"].start,
        scored["test_silent_member"].end,
        assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
        mock_callees=_MOCK_CALLEES,
    )
    assert evidence.discarded_sut_calls == scored["test_silent_member"].score.discarded_sut_calls
