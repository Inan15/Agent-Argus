"""Two structural facts that promote a seeded-defect-class finding to BLOCKING (wq-1083).

Drivers: wq-1083 (step 1 of 3 toward the pre-registered October number: "advisory
findings of seeded-defect classes become BLOCKING, with the four clean controls as the
precision guard"), cross-cutting #6 (a HEURISTIC-only finding still never blocks — what
this module adds is two facts read off the source, not a threshold), AR8 (PURE: no I/O,
no clock, no LLM; the pipeline hands the text in), AR4 (no float, no iteration-order
reliance in any emitted value).

Why this is not "flip ``depth_supported`` on every ``vacuous_test_heuristic`` / ``orphan_code``"
---------------------------------------------------------------------------------------------
Measured before this module was written, over Minions at ``dcd90233`` (repository scope):
**645** ``vacuous_test_heuristic`` and **1,064** ``orphan_code`` findings, 0 blocking. Every
heuristic finding sits in a test file and every orphan finding names a def with no
name-match caller, so a class-wide flip would have put ~1,700 blocking findings on one real
repository — the false-accusation failure the verdict gate exists to prevent. Each rule
below is instead a NARROW structural fact with its own conservative exits, and a finding
that fails any exit stays exactly as advisory as it was.

1. :func:`cannot_fail_established` — the test CANNOT FAIL (``vacuous_test_cannot_fail``)
   A flagged test span with zero assertion sites on the WIDE vocabulary (bare ``assert``,
   the unittest/mock/pytest primitives incl. ``raises``/``fail``, any ``assert*`` helper)
   whose body, after its docstring, is only ``pass``/``...`` — or is ONE ``try`` whose
   single handler is a broad ``except``/``except Exception``/``except BaseException`` that
   only ``pass``-es. Exits that keep it advisory: a ``raise`` in the body, any decorator
   (skip/xfail/parametrize/given markers), or a call that DELEGATES — to a def in the same
   file, or to a ``check*``/``verify*``/``expect*``/``ensure*``/``validate*`` helper.

   **Why "cannot fail" and not "asserts nothing"** — measured, not argued. The first cut
   of this rule was *zero assertion sites plus the exits above*. It took seeded ``a1``
   (``subtotal(...)``, result discarded) to blocking, and on Minions it blocked **11**
   tests of which **9 were legitimate**: import-smoke tests (``from x import Y  # noqa``)
   and "should not raise" tests (``engine.enforce(valid)``). A test with no assertion is
   still a test when the call under test raises on failure, and ``a1`` is textually the
   same shape as those nine, so no source-level rule separates them; ``a1`` stays advisory.
   A body that cannot raise, or that swallows every exception, has no such reading.

2. :func:`unreferenced_top_level` — the def is referenced by NOTHING (``orphan_code``)
   An ``orphan_code`` finding (no name-match CALLER — the detector's existing fact) whose
   name additionally appears as NO identifier token anywhere in the ingested sources outside
   its own span and ``import`` statements — so no annotation, no
   ``isinstance``, no registry dict, no ``__all__`` string, no docstring or comment mention,
   no fixture parameter. Further exits: the def must be TOP-LEVEL (column 0 — a method may
   be reached by override or protocol dispatch the name graph cannot see), UNDECORATED (a
   decorator is a framework registration), in a NON-test Python file (test helpers and
   ``conftest.py`` fixtures are reached by the runner), NOT re-exported by a package
   ``__init__`` (public API), and in a module a TEST file imports.

   **Why the module must be imported by a test** — measured twice, not argued. Without
   any module exit the rule blocked four of this repository's own cartridges whose verdict
   is pinned ``max_blocking=0`` (``hardcoded_secret``, ``evidence_sentinel``,
   ``tool_breadth``, ``cross_partition_seam``): each carries a module nothing imports
   whose functions nothing calls — the shape of every script, plugin and library API
   root. With "imported by ANY other file" it then blocked ``CostAttributionEngine`` in the
   dogfood self-audit, whose ``argus/``-only snapshot cannot see the test that uses it.
   Dead code is a def nothing mentions INSIDE a module the suite exercises; seeded
   ``c1``/``c2``/``c3`` are that shape, and seeded ``a2`` (whose test never imports
   ``src/cart.py``) is not, so ``a2`` stays advisory.

What stays advisory, said plainly: a test whose only assertion is on a mock (seeded
``d2``) needs value provenance, which this module does not attempt; a module-level def
reached only from a non-ingested file (``pyproject.toml`` entry points, YAML config) is
out of reach of the token scan — ``pyproject.toml``/``setup.cfg`` text is folded in by the
pipeline for exactly that reason.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Mapping

from argus.index.ast_index import CodeEdge, Definition

__all__ = [
    "RULE_CANNOT_FAIL",
    "ReferenceUniverse",
    "cannot_fail_established",
    "reference_universe",
    "unreferenced_top_level",
]

# The rule id a cannot-fail test carries once it is promoted (a sibling of
# ``vacuous_test_ast``: both are source-established, verdict-eligible vacuity facts).
RULE_CANNOT_FAIL = "vacuous_test_cannot_fail"

# Helper names that may assert on the test's behalf. Matched on the bare callee (the
# index's trailing identifier), case-insensitively, with an optional leading underscore.
_DELEGATING_HELPER = re.compile(r"\A_*(check|verify|expect|ensure|validate|assume|require)", re.IGNORECASE)

# Statements that do nothing. A body of only these cannot fail.
_NO_OP = frozenset({"pass", "..."})
# ``except:`` / ``except Exception[ as e]:`` / ``except BaseException[ as e]:`` — a handler
# that swallows everything the try body could raise. A tuple or a narrower class is not
# matched, so the test stays advisory.
_BROAD_EXCEPT = re.compile(r"\Aexcept\s*(?:\(?\s*(?:Exception|BaseException)\s*\)?\s*(?:as\s+\w+\s*)?)?:\Z")
_DOCSTRING_OPEN = re.compile(r"\A[rRuUbB]?(\"\"\"|'''|\"|')")

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_TOP_LEVEL_DEF = re.compile(r"\A(?:async\s+def|def|class)\s+([A-Za-z_][A-Za-z0-9_]*)")


def _line(source_lines: list[str], line_no: int) -> str:
    idx = line_no - 1
    return source_lines[idx] if 0 <= idx < len(source_lines) else ""


def _is_decorated(source_lines: list[str], def_line: int) -> bool:
    """True iff the nearest non-blank line above *def_line* opens a decorator."""
    line_no = def_line - 1
    while line_no >= 1:
        text = _line(source_lines, line_no).strip()
        if text:
            return text.startswith("@")
        line_no -= 1
    return False


def _code(text: str) -> str:
    """*text* stripped, with a trailing ``#`` comment removed when no string could hide one."""
    if "#" in text and "'" not in text and '"' not in text:
        text = text.split("#", 1)[0]
    return text.strip()


def _body_statement_lines(source_lines: list[str], definition: Definition) -> list[tuple[int, str]] | None:
    """``(indent, code)`` for each body line after the header and a leading docstring.

    ``None`` when the body cannot be read with confidence — a statement on the header line
    (``def test(): pass``) or an unterminated docstring — so the caller stays silent.
    """
    line_no = definition.start_line
    while not _code(_line(source_lines, line_no)).endswith(":"):
        if line_no >= definition.end_line:
            return None
        line_no += 1
    body: list[tuple[int, str]] = []
    for n in range(line_no + 1, definition.end_line + 1):
        raw = _line(source_lines, n)
        code = _code(raw)
        if code:
            body.append((len(raw) - len(raw.lstrip()), code))
    if body and _DOCSTRING_OPEN.match(body[0][1]):
        opener = _DOCSTRING_OPEN.match(body[0][1]).group(1)  # type: ignore[union-attr]
        first = body[0][1]
        if opener in ('"""', "'''"):
            if first.count(opener) >= 2:
                body = body[1:]
            else:
                closing = next((i for i, (_, c) in enumerate(body[1:], 1) if opener in c), None)
                if closing is None:
                    return None
                body = body[closing + 1 :]
        elif first.endswith(opener):
            body = body[1:]
    return body


def _cannot_fail_shape(body: list[tuple[int, str]]) -> bool:
    """True iff the body is no-ops only, or ONE ``try`` whose broad ``except`` only no-ops."""
    if all(code in _NO_OP for _, code in body):
        return True
    if body[0][1] != "try:":
        return False
    base = body[0][0]
    clause_positions = [i for i, (indent, _) in enumerate(body) if indent <= base]
    if len(clause_positions) != 2:
        return False
    handler = clause_positions[1]
    if not _BROAD_EXCEPT.match(body[handler][1]):
        return False
    handler_body = body[handler + 1 :]
    return bool(handler_body) and all(code in _NO_OP for _, code in handler_body)


def cannot_fail_established(
    *,
    source_lines: list[str],
    span_edges: Iterable[CodeEdge],
    definition: Definition,
    assertion_sites: int,
    same_file_names: frozenset[str],
) -> bool:
    """The cannot-fail blocking fact for ONE already-flagged test span (PURE).

    *assertion_sites* is the detector's own WIDE count (calls + bare asserts), so this
    function never re-derives the assertion vocabulary. *same_file_names* is every
    ``Definition`` name in the test's file; a call into one of them is delegation.
    """
    if assertion_sites != 0:
        return False
    if _is_decorated(source_lines, definition.start_line):
        return False
    for line_no in range(definition.start_line + 1, definition.end_line + 1):
        text = _line(source_lines, line_no).strip()
        if text == "raise" or text.startswith(("raise ", "raise(")):
            return False
    for edge in span_edges:
        callee = edge.callee
        if callee != definition.name and callee in same_file_names:
            return False
        if _DELEGATING_HELPER.match(callee):
            return False
    body = _body_statement_lines(source_lines, definition)
    if body is None:
        return False
    return not body or _cannot_fail_shape(body)


def _import_line_numbers(source_lines: list[str]) -> set[int]:
    """1-based numbers of every physical line that belongs to an ``import`` statement."""
    numbers: set[int] = set()
    open_paren = False
    continued = False
    for line_no, raw in enumerate(source_lines, start=1):
        text = raw.strip()
        if open_paren or continued:
            numbers.add(line_no)
            if open_paren and ")" in text:
                open_paren = False
            continued = text.endswith("\\")
            continue
        if text.startswith("import ") or (text.startswith("from ") and " import " in text):
            numbers.add(line_no)
            open_paren = "(" in text and ")" not in text
            continued = text.endswith("\\")
    return numbers


@dataclass(frozen=True)
class ReferenceUniverse:
    """What the whole repository says about names, read once per audit (PURE value).

    ``tokens`` — identifier occurrences on every NON-import line of every source.
    ``test_import_tokens`` — the identifiers on the ``import`` lines of TEST files (module
    and imported names alike), which is how a module is known to be exercised by the suite.
    ``reexported`` — every identifier on an ``import`` line of an ``__init__.py``: a
    package re-export is public API, whether or not anything in the repository calls it.
    """

    tokens: Counter[str]
    test_import_tokens: frozenset[str]
    reexported: frozenset[str]


def reference_universe(sources: Mapping[str, str], *, test_paths: frozenset[str]) -> ReferenceUniverse:
    """Build the :class:`ReferenceUniverse` over *sources* (repo-relative path → text).

    *test_paths* names which of *sources* are test files; the caller classifies them, so
    this module never re-derives the test-file convention. Deliberately crude in the
    SILENT direction: strings, comments and docstrings count as references, and so does
    any language's text, because a mention is not proof of use but its absence is the only
    fact the blocking rule needs.
    """
    tokens: Counter[str] = Counter()
    test_imported: set[str] = set()
    reexported: set[str] = set()
    for path in sorted(sources):
        lines = sources[path].split("\n")
        imports = _import_line_numbers(lines) if path.endswith(".py") else set()
        imported: set[str] = set()
        for line_no, raw in enumerate(lines, start=1):
            if line_no in imports:
                imported.update(_IDENTIFIER.findall(raw))
            else:
                tokens.update(_IDENTIFIER.findall(raw))
        if path in test_paths:
            test_imported.update(imported)
        if path.rsplit("/", 1)[-1] == "__init__.py":
            reexported.update(imported)
    return ReferenceUniverse(
        tokens=tokens, test_import_tokens=frozenset(test_imported), reexported=frozenset(reexported)
    )


def _module_name(file_path: str) -> str:
    """The name another file imports *file_path* by: its stem, or its package for ``__init__``."""
    parts = file_path.split("/")
    if parts[-1] == "__init__.py":
        return parts[-2] if len(parts) > 1 else ""
    return parts[-1][: -len(".py")]


def unreferenced_top_level(
    *,
    file_path: str,
    source: str | None,
    definition: Definition,
    universe: ReferenceUniverse,
    is_test: bool,
) -> bool:
    """The no-reference blocking fact for ONE ``orphan_code`` finding (PURE).

    True only when the def is a top-level, undecorated, non-test Python def whose name
    occurs nowhere in the reference universe OUTSIDE its own span, is not re-exported by a
    package ``__init__``, and whose MODULE a test file imports. Mentions inside the span —
    its ``def`` line, its docstring, a recursive call — are not a reference from anywhere
    else, so they are subtracted rather than counted.

    The module-is-tested exit is what separates dead code from an entry point or a
    library's public surface: a module no test imports is a script, a plugin or an API
    root, and a def in it with no in-repository caller is the normal case, not a defect.
    A module the suite exercises, carrying a def nothing mentions, is the seeded shape. It
    also keeps a PARTIAL audit silent: a snapshot that carries no tests (the dogfood's
    ``argus/``-only slice) cannot see the test that calls a def, and promotes nothing.
    """
    if is_test or source is None or not file_path.endswith(".py"):
        return False
    if file_path.rsplit("/", 1)[-1] == "conftest.py":
        return False
    lines = source.split("\n")
    match = _TOP_LEVEL_DEF.match(_line(lines, definition.start_line))
    if match is None or match.group(1) != definition.name:
        return False
    if _is_decorated(lines, definition.start_line):
        return False
    if definition.name in universe.reexported:
        return False
    if _module_name(file_path) not in universe.test_import_tokens:
        return False
    within_span = sum(
        _IDENTIFIER.findall(_line(lines, line_no)).count(definition.name)
        for line_no in range(definition.start_line, definition.end_line + 1)
    )
    return universe.tokens.get(definition.name, 0) - within_span == 0
