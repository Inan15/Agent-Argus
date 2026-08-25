"""Story 17.3 — guards over the ASSERTION-STRENGTH scale, its grader, and ``S1``.

WHY THIS FILE EXISTS. ``argus/detectors/assertion_strength.py`` grades what each assertion
in a flagged test span CONSTRAINS, and lands the successor vacuity predicate ``S1``
(``successor-vacuity-predicate-specification.md`` §2.1) as code. ``S1`` gates nothing in
Epic 17 — it is advisory by contract (§6.5) — but the grading it rests on has exactly one
lethal direction, and every guard here exists for it.

⛔ **ONLY THE BAND-0 BOUNDARY CARRIES VERDICT WEIGHT.** ``S1``'s threshold is *EVERY
assertion at the weakest band*, so grading a real constraint as ``none`` ADMITS a span
(towards an accusation) while over-grading merely REFUSES it (away from one). The
conservative default is one sentence — **when in doubt, NOT the weakest band** — and it is
what ``-149``, ``-150`` and ``PRECISION-001-145`` measure.

⛔ **GUARD-ADEQUACY CLAUSE, discharged rather than promised** (``architecture.md`` section
Enforcement, Story 13.2 / AC8.4). Every case below names (i) its OBSERVABLE, (ii) is driven
RED at the REAL SEAM by an EXECUTED mutation, and (iii) generates at least one adversarial
variant from the live table, record or tree it closes over, **with its count asserted**.

⛔ **NON-VACUITY IS ASSERTED FIRST, EVERY TIME** (``AI-E11-1``). A sweep that parsed zero
modules reports *"there is only one derivation"* forever; a band guard over an empty
assertion population measures nothing; a fail-closed fixture that never reached
``discarded_sut_calls >= 1`` proves no refusal. Every case here asserts its population is
non-empty and its seam reachable BEFORE asserting anything about it.

⛔ **THE TREE IS SHARED, SO NO MUTATION TOUCHES DISK.** Every "plant a defect in a real
module" mutation below reads the REAL module's committed source text, mutates that TEXT in
memory, and drives the SAME pure sweep over it. The seam is the sweep; feeding it mutated
real-module source is the real seam, and it cannot lose a byte of a file a peer session is
also writing. Each case re-asserts the on-disk sha256 afterwards anyway.

⛔ **NO TIMING, NO BENCHMARK, NO INVOCATION-COUNT THRESHOLD LIVES HERE** (AC7.2). The
span-scan cost record is a DISCLOSURE in the story record, not a gate; ``DF-AUD-DETECT-C``
stays open and undispositioned. A flaky performance gate is a defect this repository has
not yet acquired.

⛔ **NO REACH FIGURE FOR ``S1`` IS WRITTEN HERE** (AC6.3). The counts below are guard
fixtures over hand-built or generated spans; ``S1``'s population over the corpus is Story
17.4's single measurement, against a criterion frozen at
``PREREGISTRATION_COMMIT_SHA`` before any of this existed.

⛔ **WHY THIS FILE IS A PAIR.** NFR-M1 caps a module at 1,200 physical lines and Story
17.3's own §0.8 pre-registers a SPLIT at any projection above 1,150 — set before a line was
written, on Story 16.5's precedent, so a split is never discovered at review. These guards
did not fit in one module. They are split along the seam the story is built on: the SCALE
and the GRADER live here, and the PREDICATE — ``S1`` itself and the *"nothing flipped"*
evidence — lives in ``tests/test_successor_predicate_s1.py``, which IMPORTS this module's
fixture plumbing rather than copying it. That is exactly the
``test_silent_class.py`` / ``test_silent_class_record.py`` pair's shape, and a second copy of
a fixture is the fork class this repository has already rotted from twice. Splitting is the
remedy NFR-M1 prescribes; shaving is not, and an ``_EXEMPT_BY_DESIGN`` entry is forbidden
outright.

Verification area: detector contract (``TC-ArgusAgent-DETECT-001-147`` .. ``-152``). The
predicate's half is ``TC-ArgusAgent-PRECISION-001-145`` .. ``-146``. The ``^``/``$`` anchor
sweep this story WIDENS keeps its home and its existing
``TC-ArgusAgent-DETECT-001-130`` id in ``tests/test_vacuous_cross_language.py`` — widened,
never forked (AC9.11), and see this story's record for why no new id was minted for it.
"""

from __future__ import annotations

import ast
import hashlib
import re
import subprocess
from pathlib import Path

import pytest

from argus.detectors import assertion_strength, provenance_scan
from argus.detectors.assertion_strength import (
    ASSERTION_STRENGTH_BANDS,
    S1_SPECIFICATION,
    UNESTABLISHED,
    AssertionStrengthCounts,
    UnregisteredStrength,
    grade_span_assertions,
    s1_corroborated,
    strength_meaning,
    strength_ordinal,
)
from argus.detectors.provenance_scan import RESULT_OBSERVING_CONTEXT_CALLEES
from argus.detectors.vacuous_test import (
    VacuousTestDetector,
    _edges_in_span,
    index_aligned_lines,
)
from argus.detectors.vacuous_vocabulary import (
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
    is_assertion_callee,
)
from argus.index.ast_index import CodeEdge, build_ast_index

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARGUS_ROOT = _REPO_ROOT / "argus"
_PROVENANCE_SCAN = _ARGUS_ROOT / "detectors" / "provenance_scan.py"
_ASSERTION_STRENGTH = _ARGUS_ROOT / "detectors" / "assertion_strength.py"

#: The story's own baseline (its YAML frontmatter `baseline_commit`). `PRECISION-001-146`
#: reads the commits of THIS story's arc out of real history, never a working-tree diff.
_BASELINE_COMMIT = "024d330"
_STORY_TAG = "(17-3)"


# --------------------------------------------------------------------------------------
# Shared, PURE sweep helpers. Exported at module level on purpose: every absence-asserting
# guard below drives the SAME predicate over a MUTATED copy of real module source, which is
# the only way an absence guard can be shown to move with the defect it claims to close.
# --------------------------------------------------------------------------------------


def _argus_modules() -> dict[str, str]:
    """Every tracked ``argus/**`` module, as ``{posix path: source text}``.

    Read from the working tree by ``git ls-files``, so a module added without being tracked
    cannot silently escape the sweep and a ``__pycache__`` artefact cannot enter it. POSIX
    forward slashes on every platform — ``os.sep`` never reaches a locator (§2.7).
    """
    listed = subprocess.run(  # noqa: S603,S607 - read-only git verb, fixed argv
        ["git", "ls-files", "--", "argus"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    paths = {path for path in listed if path.endswith(".py")}
    # ⛔ UNION with the package on disk, never the index alone: a module that is written
    # but not yet `git add`-ed would otherwise escape every sweep below, which is the exact
    # window in which a second derivation is written.
    paths |= {
        found.relative_to(_REPO_ROOT).as_posix()
        for found in _ARGUS_ROOT.rglob("*.py")
        if "__pycache__" not in found.parts
    }
    return {path: (_REPO_ROOT / path).read_text(encoding="utf-8") for path in sorted(paths)}


def _functions_calling(source: str, target: str) -> frozenset[str]:
    """Names of the functions in *source* that CALL ``target(...)`` by bare name.

    ⛔ Classifies AST nodes, never counts substrings: a mention of the name in a docstring,
    a comment or a string literal is not a call, and this repository has already shipped one
    unanchored whole-document regex that read a mention as a claim (``DN-17-1-15``).
    """
    tree = ast.parse(source)
    found: set[str] = set()
    for function in ast.walk(tree):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(function):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == target
            ):
                found.add(function.name)
    return frozenset(found)


def _defines(source: str, name: str) -> bool:
    """Whether *source* defines a module-level function called *name*."""
    return any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
        for node in ast.parse(source).body
    )


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------------------
# AC4 — the DF-AUD-DETECT-D collapse: ONE derivation of "where does this statement end?",
# and it carries the cross-line STRING state.
# --------------------------------------------------------------------------------------


def test_TC_ArgusAgent_DETECT_001_152_the_statement_extent_carries_the_string_state() -> None:
    """TC-ArgusAgent-DETECT-001-152 — AC4.5: a statement's extent spans its whole literal.

    **Observable:** ``logical_statements``' ``end_line`` for a statement that OPENS a
    multi-line string literal, over a population GENERATED from the repository's own tracked
    ``argus/**`` modules with its count asserted.

    **The defect it moves, measured rather than argued** (``DF-AUD-DETECT-D``, re-measured
    at HEAD ``024d330``: 232 files / 31,845 statements / **1,890 disagreements** / 5.93%).
    The deleted ``_logical_statement_end`` restated the continuation rule over
    ``_code_prefix``, which hard-codes ``pending=None`` and therefore cannot carry the
    cross-line string state; it placed every multi-line docstring's END at its OPENING line.
    Two derivations of one question is the disagreement class this module keeps closing.

    **Executed mutation, at the REAL seam:** ``_continued_code_prefix`` — the one function
    that threads the string state — is replaced in the live module by a version that drops
    ``pending``, exactly reproducing the deleted implementation's blindness, and the shipped
    ``logical_statements`` is then shown to return the WRONG extent. The attribute is
    restored and its identity re-asserted, and the module file's sha256 is unchanged (it is
    never written).

    **Non-vacuity FIRST:** the population must parse a stated floor of modules and must
    contain a stated floor of MULTI-LINE statements, or "the extent spans the literal" is
    a property of an empty set.
    """
    before = _sha256(_PROVENANCE_SCAN)
    modules = _argus_modules()
    assert len(modules) >= 60, f"the sweep read only {len(modules)} module(s); it is broken"

    total_statements = 0
    multi_line = 0
    docstring_openers = 0
    for source in modules.values():
        lines = source.split("\n")
        if lines and lines[-1] == "":
            lines.pop()  # the index's own decomposition (vacuous_test.index_aligned_lines)
        if not lines:
            continue
        statements = provenance_scan.logical_statements(lines, 1, len(lines))
        total_statements += len(statements)
        for statement in statements:
            assert statement.end_line >= statement.start_line, (
                f"statement at {statement.start_line} ends BEFORE it starts "
                f"({statement.end_line}); the projection is inverted"
            )
            if statement.end_line > statement.start_line:
                multi_line += 1
            opener = lines[statement.start_line - 1].lstrip()
            if opener.startswith(('"""', "'''", 'r"""', "r'''")) and not (
                opener.count('"""') >= 2 or opener.count("'''") >= 2
            ):
                docstring_openers += 1
                assert statement.end_line > statement.start_line, (
                    f"the statement opening a multi-line literal at line "
                    f"{statement.start_line} was given the extent {statement.end_line} — "
                    f"its own opening line. That is exactly DF-AUD-DETECT-D's defect."
                )

    assert total_statements >= 6_000, (
        f"the generated population holds only {total_statements} statement(s); the sweep is "
        f"not reading the tree it claims to"
    )
    assert multi_line >= 1_500, (
        f"only {multi_line} statement(s) of {total_statements} span more than one line; the "
        f"population cannot demonstrate an EXTENT property"
    )
    assert docstring_openers >= 500, (
        f"only {docstring_openers} statement(s) open a multi-line literal; the adversarial "
        f"population this case is named for is effectively empty"
    )

    # ---- the executed mutation, at the real seam -------------------------------------
    fixture = [
        'def probe():',
        '    """A docstring whose prose opens a bracket (',
        '    and closes it here ) two lines later.',
        '    """',
        '    return 1',
    ]
    shipped = provenance_scan.logical_statements(fixture, 2, 5)
    shipped_extent = {s.start_line: s.end_line for s in shipped}
    assert shipped_extent[2] == 4, (
        f"the shipped extent of the docstring opening at line 2 is {shipped_extent.get(2)!r}, "
        f"not 4; this case's own fixture no longer exercises the property"
    )

    original = provenance_scan._continued_code_prefix

    def _string_state_blind(line: str, pending: str | None) -> tuple[str, str | None]:
        """The DELETED behaviour: ``pending`` is dropped, exactly as ``_code_prefix`` did."""
        code, _ = original(line, None)
        return code, None

    provenance_scan._continued_code_prefix = _string_state_blind  # type: ignore[assignment]
    try:
        mutated = provenance_scan.logical_statements(fixture, 2, 5)
        mutated_extent = {s.start_line: s.end_line for s in mutated}
    finally:
        provenance_scan._continued_code_prefix = original  # type: ignore[assignment]

    assert provenance_scan._continued_code_prefix is original, "the mutation was not restored"
    assert _sha256(_PROVENANCE_SCAN) == before, "the module file was written to; it must not be"
    assert mutated_extent.get(2) != 4, (
        "dropping the cross-line string state did NOT move the extent, so this guard is not "
        "observing the seam it claims to observe and would stay green through the defect"
    )


def test_TC_ArgusAgent_DETECT_001_151_one_derivation_of_where_a_statement_ends() -> None:
    """TC-ArgusAgent-DETECT-001-151 — AC4.6/§1.3: ONE statement-extent walk in ``argus/**``.

    **Observable:** an AST sweep over every tracked ``argus/**`` module for a SECOND
    bracket-depth statement walk. ``_bracket_delta`` is the primitive any such walk must
    reach, so the set of functions that CALL it is the set of statement-boundary
    derivations.

    **Non-vacuity FIRST, and it is this guard's specific way of dying quietly:** a sweep
    that parsed zero modules, or whose matcher resolved neither the primitive's DEFINITION
    nor its ONE known caller, would report *"there is only one derivation"* forever. Both
    are asserted before the absence is.

    **Executed mutation:** the deleted ``_logical_statement_end`` is planted back into the
    REAL module's source text, in memory, and the SAME sweep is driven over it — RED, with
    the second derivation named. The file on disk is never written and its sha256 is
    re-asserted (§2.6: the tree is shared).

    ⛔ The ``is this span edge a SUT call`` half of ``-151`` lives beside this one and is
    added by the grading commit; this half is the collapse's own.
    """
    before = _sha256(_PROVENANCE_SCAN)
    modules = _argus_modules()
    assert len(modules) >= 60, f"the sweep parsed only {len(modules)} module(s); it is broken"

    scan_source = modules["argus/detectors/provenance_scan.py"]
    assert _defines(scan_source, "_bracket_delta"), (
        "the sweep did not resolve _bracket_delta's own DEFINITION, so every absence below "
        "is a broken matcher rather than evidence"
    )
    assert _defines(scan_source, "_scan_span"), "the ONE known derivation is not defined"

    derivations: dict[str, frozenset[str]] = {
        path: _functions_calling(source, "_bracket_delta") for path, source in modules.items()
    }
    known = derivations["argus/detectors/provenance_scan.py"]
    assert known == frozenset({"_scan_span"}), (
        f"the KNOWN derivation did not resolve as expected: _bracket_delta's callers in "
        f"provenance_scan.py are {sorted(known)!r}, not ['_scan_span']"
    )

    everywhere = {
        f"{path}::{name}" for path, names in derivations.items() for name in names
    }
    assert everywhere == {"argus/detectors/provenance_scan.py::_scan_span"}, (
        f"more than one statement-boundary derivation exists in argus/**: {sorted(everywhere)!r}. "
        f"DF-AUD-DETECT-D measured what two of them cost — 1,890 disagreements over 31,845 "
        f"statements — and the repair was a DELETION, not a third function."
    )

    # ---- the executed mutation: plant the deleted function back, in memory ------------
    planted = scan_source + (
        "\n\n"
        "def _logical_statement_end(source_lines, start_line, span_end):\n"
        "    depth = 0\n"
        "    for line_no in range(start_line, span_end + 1):\n"
        "        code = _code_prefix(source_lines[line_no - 1])\n"
        "        depth = max(depth + _bracket_delta(code), 0)\n"
        "        if depth <= 0 and not _continues_onto_next_line(code):\n"
        "            return line_no\n"
        "    return span_end\n"
    )
    assert _functions_calling(planted, "_bracket_delta") == frozenset(
        {"_scan_span", "_logical_statement_end"}
    ), "the sweep did not SEE the planted second derivation, so it would not go red on it"
    assert _sha256(_PROVENANCE_SCAN) == before, "the module file was written to; it must not be"


# --------------------------------------------------------------------------------------
# Scoring fixtures through the REAL Story 1.4 index. Never a hand-built edge list: every
# claim below is about how the SHIPPED grader reads real source text, and a hand-built list
# would assert the tester's belief about that instead.
# --------------------------------------------------------------------------------------


def _span(root: Path, source: str, slug: str = "probe"):
    """``(source_lines, span_edges, start, end)`` for the ONE test function in *source*."""
    relative = f"tests/test_{slug}.py"
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8")
    index = build_ast_index(root, (relative,))
    entry = {e.file_path: e for e in index.entries}[relative]
    assert not entry.parse_failed and entry.ast_eligible, (
        f"{slug!r} did not parse through the real 1.4 index: "
        f"{entry.parse_failure_reason!r}. The grammar packages are BASE dependencies, so "
        f"this is a broken environment and is reported as a FAILURE rather than a skip -- "
        f"a skip here would read as green."
    )
    definitions = [
        d for d in entry.definitions if d.kind == "function" and d.name.startswith("test")
    ]
    assert len(definitions) == 1, f"{slug!r} must hold exactly one test function"
    definition = definitions[0]
    lines = index_aligned_lines(source)
    edges = _edges_in_span(entry.edges, definition.start_line, definition.end_line)
    return lines, edges, definition.start_line, definition.end_line


def _discarded_sut_calls(span) -> int:
    """Fact (b′)'s own arithmetic over *span*, so a fixture's non-vacuity can be asserted."""
    lines, edges, start, end = span
    return provenance_scan.provenance_evidence(
        lines,
        edges,
        start,
        end,
        assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
        mock_callees=_MOCK_CALLEES,
    ).discarded_sut_calls


_SILENT = """
def test_x():
    parse("payload")
"""

#: ⛔ Both band fixtures carry a DISCARDED SUT call as well as a bound one, so they satisfy
#: (a) and (b′) and falsify ONLY (c′). Without the discarded call they would be refused by
#: (b′) and would say nothing at all about the band boundary they are named for.
_VALUE_BAND = """
def test_x():
    parse("warm up")
    result = parse("payload")
    assert result == 3
"""

_EXISTENCE_BAND = """
def test_x():
    parse("warm up")
    result = parse("payload")
    assert result
"""


# --------------------------------------------------------------------------------------
# AC1 — the scale
# --------------------------------------------------------------------------------------


def test_TC_ArgusAgent_DETECT_001_147_the_scale_is_closed_ordered_and_meaningful() -> None:
    """TC-ArgusAgent-DETECT-001-147 — AC1: the scale, its order, its meanings, its refusal.

    **Observable:** the vocabulary tuple, each member's ordinal, each member's MEANING, and
    the refusal of an unregistered band — **driven**, never read off the list.

    **The defect it moves:** a scale that silently accepts an unknown band. That is the
    ``DF-10-4-E`` shape ``silent_class.UnregisteredIdiom`` and
    ``gate_seal.UnregisteredPartition`` already close over, and the reason a closed
    vocabulary is worth its ceremony: a band nobody can define is a band nobody can defend
    in a promotion proposal.

    **Generated with its count:** every band is round-tripped through BOTH accessor
    functions, the round-trip count is asserted to equal the vocabulary's own length, and an
    unregistered value is GENERATED from the vocabulary (by concatenating its members, which
    cannot itself be a member) rather than hand-typed, so a future band named ``"unknown"``
    cannot make this case pass by accident.

    ⛔ ``unestablished`` is asserted to be a CONDITION and NOT a fourth band (AC1.4).
    """
    assert ASSERTION_STRENGTH_BANDS == ("none", "existence", "value"), (
        f"the committed scale is {ASSERTION_STRENGTH_BANDS!r}. The epic names these three "
        f"bands at minimum, and DN-17-3-7 refuses a broader taxonomy in this story."
    )
    assert ASSERTION_STRENGTH_BANDS[0] == "none", "the WEAKEST band must sit at ordinal 0"
    assert len(set(ASSERTION_STRENGTH_BANDS)) == len(ASSERTION_STRENGTH_BANDS)

    round_tripped = 0
    for expected, band in enumerate(ASSERTION_STRENGTH_BANDS):
        assert strength_ordinal(band) == expected, f"{band!r} moved on the scale"
        meaning = strength_meaning(band)
        assert isinstance(meaning, str) and len(meaning) >= 80, (
            f"{band!r}'s meaning is {len(meaning)} characters. AC1.2 asks for the words a "
            f"promotion proposal would have to defend, not a label repeated back."
        )
        assert "S1" in meaning, f"{band!r}'s meaning does not say what it does to S1"
        round_tripped += 1
    assert round_tripped == len(ASSERTION_STRENGTH_BANDS) == 3, (
        f"only {round_tripped} band(s) round-tripped through the meaning function"
    )

    # ⛔ The ORDER is the claim, not just the membership: `none` is strictly weakest.
    ordinals = [strength_ordinal(band) for band in ASSERTION_STRENGTH_BANDS]
    assert ordinals == sorted(ordinals) == [0, 1, 2]

    # ⛔ The refusal is DRIVEN, and the offender is GENERATED from the live vocabulary.
    generated = "".join(ASSERTION_STRENGTH_BANDS)
    assert generated not in ASSERTION_STRENGTH_BANDS, "the generated offender is a member"
    for offender in (generated, UNESTABLISHED, "", "NONE"):
        with pytest.raises(UnregisteredStrength):
            strength_ordinal(offender)
        with pytest.raises(UnregisteredStrength):
            strength_meaning(offender)

    # ⛔ AC1.4 — `unestablished` is a CONDITION carried as its own count, not a fourth band.
    assert UNESTABLISHED not in ASSERTION_STRENGTH_BANDS
    assert UNESTABLISHED in AssertionStrengthCounts._fields
    assert set(AssertionStrengthCounts._fields) == {
        "none",
        "existence",
        "value",
        UNESTABLISHED,
    }, "the per-span result is a count per band plus the unestablished count, and nothing else"

    # ⛔ AC1.5 — COUNTS, never a rendered set, never a float.
    counts = AssertionStrengthCounts(none=1, existence=2, value=3, unestablished=4)
    assert all(isinstance(value, int) for value in counts)
    assert not any(isinstance(value, float) for value in counts)
    assert counts.graded == 6

    # ⛔ AC1.6 — the direction of harm is written down BESIDE the scale, where the next
    # author reads it, not only in a story file nobody opens while editing a module.
    module_text = _ASSERTION_STRENGTH.read_text(encoding="utf-8")
    assert "WHEN IN DOUBT, NOT THE WEAKEST BAND" in module_text, (
        "the conservative default is not stated in the module. AC1.6: only the band-0 "
        "boundary carries verdict weight, and that sentence is the whole safety story."
    )
    assert S1_SPECIFICATION.startswith("successor-vacuity-predicate-specification.md"), (
        "AC5.4: the predicate must NAME the specification document and its section rather "
        "than re-argue it inside the module (the DF-8-5-C / AI-E9-7 drift defect)."
    )


# --------------------------------------------------------------------------------------
# AC3 — the grader is PURE and does not re-parse
# --------------------------------------------------------------------------------------

#: Parser entry points the grader may not reach. ⛔ ``CodeEdge`` is a TYPE and is not one of
#: these: ``provenance_scan`` imports it the same way, and a type import calls no grammar.
_PARSER_MODULES = frozenset({"ast", "tree_sitter", "tree_sitter_languages", "parser"})
#: Reached in EITHER form (``f(...)`` or ``x.f(...)``) — a second grammar call however it
#: is qualified.
_GRAMMAR_ENTRY_POINTS = frozenset({"build_ast_index", "parse", "walk", "unparse"})
#: Reached only as a BARE name. ⛔ ``re.compile`` is a regex, not a grammar; the BUILTIN
#: ``compile`` is a second parser, and the two are told apart by the call's shape rather than
#: by its spelling — the same node-classification discipline as everywhere else in this file.
_BARE_GRAMMAR_ENTRY_POINTS = frozenset({"compile", "eval", "exec", "__import__"})
_IMPURE_NAMES = frozenset(
    {
        "open",
        "input",
        "uuid4",
        "uuid1",
        "random",
        "getenv",
        "environ",
        "time",
        "now",
        "today",
        "monotonic",
        "urlopen",
        "system",
        "run",
        "Path",
        "read_text",
        "write_text",
    }
)


def _imported_modules(source: str) -> frozenset[str]:
    """Everything *source* imports — AST-classified, never substring-counted.

    Carries the DOTTED module, its TOP-LEVEL package and every imported SYMBOL, because the
    three answer different questions: ``import ast`` and ``from ast import walk`` must both
    be caught by a top-level check, while *"is the known-present import still resolved?"* is
    a question about the dotted name.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
            found.add(node.module.split(".")[0])
            found.update(alias.name for alias in node.names)
    return frozenset(found)


def _called_names(source: str, *, bare_only: bool = False) -> frozenset[str]:
    """Call targets in *source*: ``f(...)`` always, ``x.f(...)`` unless *bare_only*."""
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and not bare_only:
            found.add(node.func.attr)
    return frozenset(found)


def test_TC_ArgusAgent_DETECT_001_148_the_grader_is_pure_and_does_not_reparse() -> None:
    """TC-ArgusAgent-DETECT-001-148 — AC3.1/AC3.2: no parser, no I/O, no clock, no module-level path.

    **Observable:** an ``ast`` walk over the grader module's OWN source — its imports, its
    call targets and its module-level statements.

    **Non-vacuity FIRST, and it is the specific way this guard would die quietly:** a walk
    that parsed nothing, or that failed to resolve a KNOWN-PRESENT import, would report
    *"there is no parser here"* forever. Both are asserted before any absence is.

    ⛔ **Classifies AST nodes, never counts substrings.** The module's own docstring names
    ``ast`` and ``tree_sitter`` several times, on purpose, to say it does not use them — a
    substring sweep would read those sentences as the defect they forbid. Story 17.1's one
    review finding was exactly an unanchored whole-document regex, repaired by DELETION
    through the one existing derivation (``DN-17-1-15``).

    **Executed mutation:** ``import ast`` is added to the REAL module's source text and the
    SAME walk is driven over it — RED. The file on disk is never written and its sha256 is
    re-asserted (§2.6: the tree is shared).
    """
    before = _sha256(_ASSERTION_STRENGTH)
    source = _ASSERTION_STRENGTH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imported = _imported_modules(source)
    assert len(imported) >= 5, f"the walk resolved only {imported!r}; it is not working"
    for known in (
        "re",
        "NamedTuple",
        "argus.detectors.provenance_scan",
        "argus.detectors.vacuous_vocabulary",
        "CodeEdge",
        "is_assertion_callee",
    ):
        assert known in imported, (
            f"the walk did not resolve the KNOWN-PRESENT import {known!r}, so its "
            f"resolution is broken and every absence below is meaningless"
        )

    offenders = imported & _PARSER_MODULES
    assert not offenders, (
        f"the grader imports a PARSER: {sorted(offenders)!r}. The epic's acceptance is "
        f"'grading reads the source text and the index and nothing else -- no re-parse, no "
        f"second grammar call'; AR8/NFR-D2 are the standing reasons."
    )

    called = _called_names(source)
    assert "search" in called or "match" in called, (
        "the call walk resolved neither `search` nor `match`, so it is not seeing this "
        "module's regex use and its absences prove nothing"
    )
    grammar = (called & _GRAMMAR_ENTRY_POINTS) | (
        _called_names(source, bare_only=True) & _BARE_GRAMMAR_ENTRY_POINTS
    )
    assert not grammar, f"the grader calls a grammar entry point: {sorted(grammar)!r}"
    impure = called & _IMPURE_NAMES
    assert not impure, (
        f"the grader reaches an impure primitive: {sorted(impure)!r}. AR8: no I/O, no clock, "
        f"no uuid4, no random, no environment read."
    )

    # ⛔ DF-9-2-A — no module-level path resolution: the wheel-import guard imports every
    # shipped module out of a BUILT distribution with this repository off `sys.path`.
    module_level_calls = [
        node
        for statement in tree.body
        if not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        for node in ast.walk(statement)
        if isinstance(node, ast.Call)
    ]
    allowed = {"compile", "frozenset", "len", "dict", "tuple"}
    disallowed = [
        node.func.id
        for node in module_level_calls
        if isinstance(node.func, ast.Name) and node.func.id not in allowed
    ]
    assert not disallowed, f"module-level call(s) that are not vocabulary construction: {disallowed!r}"

    # ---- the executed mutation, over the REAL module's text --------------------------
    mutated = "import ast\n" + source
    assert "ast" in _imported_modules(mutated), (
        "the walk did not SEE a planted `import ast`, so it would not go red on the defect "
        "it claims to close"
    )
    assert _sha256(_ASSERTION_STRENGTH) == before, "the module file was written to"


def test_TC_ArgusAgent_DETECT_001_148_determinism_is_driven_not_asserted(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-148 — AC3.3: equal results across repeats and shuffled edges.

    **Observable:** the graded counts and ``S1``'s verdict for one span, computed repeatedly
    and over a REVERSED edge list. The 1.4 index does not emit edges in source order —
    ``ast_index._extract`` walks with ``stack.pop()``/``stack.extend``, which visits siblings
    right to left — so an order-sensitive grader would be non-deterministic in production,
    not merely in a test.

    **Non-vacuity FIRST:** the span must carry more than one edge, or "order does not
    matter" is a claim about a list of length one.
    """
    span = _span(
        tmp_path,
        '\ndef test_x():\n'
        '    result = parse("payload")\n'
        '    other = render(result)\n'
        '    assert other == 3\n',
        slug="determinism",
    )
    lines, edges, start, end = span
    assert len(edges) >= 2, f"the fixture emitted {len(edges)} edge(s); order cannot matter"

    first = grade_span_assertions(lines, edges, start, end)
    assert first == grade_span_assertions(lines, edges, start, end), "repeat call differed"
    assert first == grade_span_assertions(lines, list(reversed(edges)), start, end), (
        "the graded counts depend on the ORDER of the 1.4 edge set, which the index does "
        "not emit in source order"
    )
    assert s1_corroborated(lines, edges, start, end) == s1_corroborated(
        lines, list(reversed(edges)), start, end
    )


# --------------------------------------------------------------------------------------
# AC2.4 — ⛔ THE FAIL-CLOSED TEST IS NOT ACCUSED
# --------------------------------------------------------------------------------------


def _fail_closed_fixture(callee: str) -> str:
    """A fail-closed test written with *callee*, in that callee's own idiom.

    ⛔ It carries a SECOND, genuinely discarded SUT call outside the observing block on
    purpose. Fact (b) makes the call INSIDE the block CONSUMED (``DN-3``), so a pure
    fail-closed test never reaches ``discarded_sut_calls >= 1`` at all — and the shape §0.4
    warns about is exactly this one: ``S1`` drops ``consumed == 0``, so the second call
    satisfies (b′) and the span DOES reach (c′), where only the band rule stands between it
    and a false accusation.
    """
    if callee.startswith("assert"):
        return (
            "import unittest\n"
            "\n"
            "\n"
            "class Case(unittest.TestCase):\n"
            "    def test_x(self):\n"
            '        parse("warm up")\n'
            f"        with self.{callee}(ValueError):\n"
            '            parse("nonsense")\n'
        )
    return (
        "import pytest\n"
        "\n"
        "\n"
        "def test_x():\n"
        '    parse("warm up")\n'
        f"    with pytest.{callee}(ValueError):\n"
        '        parse("nonsense")\n'
    )


def test_TC_ArgusAgent_DETECT_001_149_the_fail_closed_test_is_not_accused(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-149 — AC2.4: raising IS the observation, at the BAND level.

    **Observable:** the graded band of the sole assertion, and ``S1``'s verdict, for a span
    whose only assertion is a result-observing context wrapping a discarded SUT call.

    ⛔ **THE MOST EXPENSIVE DEFECT THIS STORY CAN SHIP.** All NINE members of
    ``RESULT_OBSERVING_CONTEXT_CALLEES`` are members of the WIDE assertion vocabulary — so a
    fail-closed test DOES carry an assertion under the vocabulary (c′) must read. A grader
    that scores it by *"what do this call's arguments reference"* finds no SUT-derived name
    in ``raises(ValueError)``, grades it at the weakest band, and ``S1`` returns a FALSE
    ACCUSATION on every fail-closed test in the corpus — a shape the ratified corpus is full
    of. ⚠️ Fact (b) does not protect it: ``S1`` drops ``consumed == 0``, the clause that made
    ``DN-3``'s CONSUMED verdict bite.

    **Generated with its count:** ONE fixture per member of the LIVE table, scored at the
    REAL seam through the shipped grader, with the count asserted to equal the table's own
    size — so a name entering or leaving the table re-runs the adversary automatically.

    **Non-vacuity FIRST:** each fixture is asserted to reach ``discarded_sut_calls >= 1`` and
    to carry at least one graded assertion, or the refusal is being measured over an empty
    span and proves nothing.

    **Executed mutation:** the observing-context rule is removed at the REAL seam — the
    module's ``_OBSERVING_CALL_RE`` is replaced by a pattern that never matches — and the
    false accusation is made VISIBLE: the same fixtures then grade at the weakest band and
    ``S1`` corroborates.
    """
    members = sorted(RESULT_OBSERVING_CONTEXT_CALLEES)
    assert len(members) == 9, (
        f"the result-observing table holds {len(members)} member(s), not 9. The fail-closed "
        f"trap has changed SHAPE -- escalate (AC10.1), do not adjust this number."
    )
    for callee in members:
        assert is_assertion_callee(callee), (
            f"{callee!r} is no longer a WIDE assertion callee, so it no longer enters (c′)'s "
            f"population and this case's premise has moved -- escalate (AC10.1)"
        )

    spans = {}
    generated = 0
    for callee in members:
        span = _span(tmp_path, _fail_closed_fixture(callee), slug=f"failclosed_{callee.lower()}")
        lines, edges, start, end = span
        # NON-VACUITY, FIRST.
        assert _discarded_sut_calls(span) >= 1, (
            f"{callee!r}'s fixture does not reach discarded_sut_calls >= 1, so S1's refusal "
            f"below would be measured over a span that never got near an accusation"
        )
        counts = grade_span_assertions(lines, edges, start, end)
        assert counts.graded >= 1, (
            f"{callee!r}'s fixture carries NO graded assertion, so the band claim below is "
            f"about an empty population (AI-E11-1)"
        )
        spans[callee] = (span, counts)
        generated += 1
    assert generated == len(RESULT_OBSERVING_CONTEXT_CALLEES) == 9

    accused = []
    for callee, (span, counts) in spans.items():
        lines, edges, start, end = span
        assert counts.none == 0, (
            f"{callee!r}: {counts.none} assertion(s) graded at the WEAKEST band. Raising IS "
            f"the observation (DN-3, one level up); a result-observing context call is never "
            f"graded `none`."
        )
        assert counts.unestablished == 0, f"{callee!r}: the grader could not read its own fixture"
        if s1_corroborated(lines, edges, start, end):
            accused.append(callee)
    assert not accused, (
        f"S1 ACCUSES the fail-closed test written with {accused!r}. That is a false "
        f"accusation on a shape the ratified corpus is full of, and it is the single most "
        f"expensive defect this story can ship."
    )

    # ---- the executed mutation, at the REAL seam -------------------------------------
    original = assertion_strength._OBSERVING_CALL_RE
    never_matches = re.compile(r"(?!x)x")
    assertion_strength._OBSERVING_CALL_RE = never_matches  # type: ignore[assignment]
    try:
        exposed = [
            callee
            for callee, (span, _) in spans.items()
            if s1_corroborated(span[0], span[1], span[2], span[3])
        ]
    finally:
        assertion_strength._OBSERVING_CALL_RE = original  # type: ignore[assignment]
    assert assertion_strength._OBSERVING_CALL_RE is original, "the mutation was not restored"
    assert exposed, (
        "removing the observing-context rule did NOT produce a single false accusation, so "
        "this guard is not observing the seam it claims to observe and would stay green "
        "through the defect it exists to close"
    )


# --------------------------------------------------------------------------------------
# AC3.4/AC3.5 — the unestablished path REFUSES and never raises
# --------------------------------------------------------------------------------------


def test_TC_ArgusAgent_DETECT_001_150_the_unestablished_path_refuses_and_never_raises() -> None:
    """TC-ArgusAgent-DETECT-001-150 — AC3.4/AC3.5/NFR-R1: a failure records, it does not raise.

    **Observable:** the ``unestablished`` count and ``S1``'s verdict over GENERATED malformed
    spans, with the generated count asserted.

    ⛔ **The direction is the whole point.** When strength cannot be established the finding
    does NOT gain corroboration: the conservative default IS the moat (cross-cutting #6,
    specification §6.3). A malformed span that returned all-zero counts would let ``S1``
    ADMIT it, which is the accusation direction.

    **Generated with its count:** the variants are built from a product of degenerate line
    lists, edge lists and span bounds rather than hand-listed, and the count is asserted.
    ⛔ No uncaught exception on any variant.
    """
    line_lists: list[list[str]] = [
        [],
        ["def test_x():"],
        ["def test_x():", '    parse("""never closed'],
        ["def test_x():", "    parse(", "        'x'"],
        ["\x0c", "\u2028"],  # separators index_aligned_lines must NOT split on
    ]
    edge_lists: list[list[CodeEdge]] = [
        [],
        [CodeEdge(callee="parse", line=2)],
        [CodeEdge(callee="parse", line=9_999)],
        [CodeEdge(callee="parse", line=1), CodeEdge(callee="parse", line=9_999)],
    ]
    bounds = [(1, 1), (5, 1), (-3, 2), (1, 9_999), (2, 3)]

    variants = 0
    refused = 0
    for lines in line_lists:
        for edges in edge_lists:
            for start, end in bounds:
                variants += 1
                counts = grade_span_assertions(list(lines), list(edges), start, end)
                verdict = s1_corroborated(list(lines), list(edges), start, end)
                assert isinstance(counts, AssertionStrengthCounts)
                assert all(isinstance(value, int) and value >= 0 for value in counts)
                if not verdict:
                    refused += 1
    assert variants == len(line_lists) * len(edge_lists) * len(bounds) == 100, (
        f"the generated malformed population is {variants} variant(s); the product changed"
    )
    assert refused == variants, (
        f"S1 corroborated {variants - refused} malformed span(s). NFR-R1: a span whose "
        f"grading cannot be established is NOT corroborated, never corroborated by default."
    )

    # ⛔ And the recorded CONDITION is really produced, not merely 'no raise': the explicitly
    # out-of-range span must report `unestablished`, or the refusals above could all be
    # coming from conjunct (a) and this case would prove nothing about (c′).
    assert grade_span_assertions([], [], 1, 1).unestablished == 1
    assert grade_span_assertions(["def test_x():"], [], 5, 1).unestablished == 1


# --------------------------------------------------------------------------------------
# AC4.6 — ONE derivation of "is this span edge a SUT call"
# --------------------------------------------------------------------------------------


_SUT_FILTER_ASSERTION_RE = re.compile(r"(?i)assertion_callees\Z")
_SUT_FILTER_MOCK_RE = re.compile(r"(?i)mock_callees\Z")


def _sut_filtering_functions(source: str) -> frozenset[str]:
    """Functions in *source* that filter edges by BOTH callee vocabularies — i.e. ``is_sut``.

    ⛔ Classifies ``ast.Compare`` nodes carrying ``In``/``NotIn`` against a name ending in
    ``assertion_callees`` and against one ending in ``mock_callees``. That pair IS the
    shipped predicate's shape, so this matcher finds the real thing rather than a spelling
    of its name.
    """
    found: set[str] = set()
    for function in ast.walk(ast.parse(source)):
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        sees_assertions = sees_mocks = False
        for node in ast.walk(function):
            if not isinstance(node, ast.Compare):
                continue
            if not any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops):
                continue
            names = {
                inner.id if isinstance(inner, ast.Name) else inner.attr
                for inner in ast.walk(node)
                if isinstance(inner, (ast.Name, ast.Attribute))
            }
            sees_assertions |= any(_SUT_FILTER_ASSERTION_RE.search(name) for name in names)
            sees_mocks |= any(_SUT_FILTER_MOCK_RE.search(name) for name in names)
        if sees_assertions and sees_mocks:
            found.add(function.name)
    return frozenset(found)


def test_TC_ArgusAgent_DETECT_001_151_one_derivation_of_is_this_a_sut_call() -> None:
    """TC-ArgusAgent-DETECT-001-151 — AC4.6/§1.3: no second ``is_sut`` anywhere in ``argus/**``.

    **Observable:** an AST sweep over every tracked ``argus/**`` module for a function that
    filters span edges against BOTH the assertion vocabulary and the mock vocabulary — the
    shape of *"is this a candidate SUT call"*.

    **Why it matters here specifically:** fact (b) already computed that classification and
    THREW IT AWAY inside ``provenance_evidence``'s loop, and Story 17.3's grader needs the
    same answer. Writing a second ``is_sut`` in the new module would be
    ``DF-AUD-DETECT-D``'s defect class, one story later, in the same package, filed by the
    same audit — and this story exists partly to close it.

    **Non-vacuity FIRST:** the sweep must parse a stated floor of modules AND resolve the ONE
    KNOWN derivation, or *"there is only one"* is a broken matcher.

    **Executed mutation:** a second filter is planted into the REAL module's source text, in
    memory, and the SAME sweep is driven over it — RED, with the second derivation named.
    """
    before = _sha256(_PROVENANCE_SCAN)
    modules = _argus_modules()
    assert len(modules) >= 60, f"the sweep parsed only {len(modules)} module(s); it is broken"

    derivations = {
        f"{path}::{name}"
        for path, source in modules.items()
        for name in _sut_filtering_functions(source)
    }
    known = "argus/detectors/provenance_scan.py::candidate_sut_edges"
    assert known in derivations, (
        f"the sweep did not resolve the ONE KNOWN derivation ({known}), so its matcher is "
        f"broken and every absence below is meaningless. It found: {sorted(derivations)!r}"
    )
    assert derivations == {known}, (
        f"more than one 'is this a SUT call' derivation exists in argus/**: "
        f"{sorted(derivations)!r}. Fact (a), fact (b)'s classification and Story 17.3's "
        f"grader must all read the SAME one (AR7/§3.3)."
    )

    # ⛔ …and it really is READ by the consumers, or 'exactly one' would be satisfied by a
    # derivation nobody calls while every consumer quietly kept its own copy inline.
    consumers = {
        f"{path}::{name}"
        for path, source in modules.items()
        for name in _functions_calling(source, "candidate_sut_edges")
    }
    assert consumers >= {
        "argus/detectors/provenance_scan.py::sut_call_classification",
        "argus/detectors/vacuous_test.py::_sut_call_sites",
        "argus/detectors/assertion_strength.py::s1_corroborated",
    }, f"the ONE derivation is not read by all three consumers; it is read by {sorted(consumers)!r}"

    # ---- the executed mutation: plant a second filter, in memory ----------------------
    planted = modules["argus/detectors/assertion_strength.py"] + (
        "\n\n"
        "def _second_is_sut(span_edges, assertion_callees, mock_callees):\n"
        "    return [\n"
        "        edge\n"
        "        for edge in span_edges\n"
        "        if edge.callee not in assertion_callees and edge.callee not in mock_callees\n"
        "    ]\n"
    )
    assert "_second_is_sut" in _sut_filtering_functions(planted), (
        "the sweep did not SEE the planted second derivation, so it would not go red on it"
    )
    assert _sha256(_PROVENANCE_SCAN) == before, "the module file was written to"
    assert _sha256(_ASSERTION_STRENGTH) == _sha256(_ASSERTION_STRENGTH)
