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

Verification area: detector contract (``TC-ArgusAgent-DETECT-001-147`` .. ``-152``) and
precision validation (``TC-ArgusAgent-PRECISION-001-145`` .. ``-146``). The ``^``/``$``
anchor sweep this story widens keeps its home in ``tests/test_vacuous_cross_language.py``
and takes ``TC-ArgusAgent-DETECT-001-153`` there — widened, never forked (AC9.11).
"""

from __future__ import annotations

import ast
import hashlib
import subprocess
from pathlib import Path

from argus.detectors import provenance_scan

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARGUS_ROOT = _REPO_ROOT / "argus"
_PROVENANCE_SCAN = _ARGUS_ROOT / "detectors" / "provenance_scan.py"


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
    return {
        path: (_REPO_ROOT / path).read_text(encoding="utf-8")
        for path in listed
        if path.endswith(".py")
    }


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
