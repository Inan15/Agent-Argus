"""Shared stdlib-``ast`` reads of one Python test function (wq-1084).

Drivers: wq-1084 (step 2 of 3 toward the pre-registered October number: one AST-based
detector per seeded-defect family A and B), AR8 (PURE: parsing a string the pipeline hands
in is not I/O; no clock, no LLM), AR7/§3.3 (the assertion vocabulary is REUSED from
``vacuous_vocabulary``, never re-listed here).

Why a second parse, when the 1.4 index already parsed the file
--------------------------------------------------------------
The 1.4 index records definitions and call EDGES — a callee name and a line. The two family
detectors need EXPRESSION structure the index never kept: what an ``assert`` compares, which
name a value was bound from, which handler a ``try`` has. Each detector therefore parses the
test file's text with the stdlib ``ast`` module, and anchors every finding it emits on the
index's own ``Definition`` (same name, same ``def`` line). A test the two parses do not agree
on is not accused: when the anchor is missing, the detector stays silent.

What counts as an assertion here
--------------------------------
:func:`assertion_calls` reads the WIDE vocabulary (``is_assertion_callee``: the unittest /
mock / pytest primitives incl. ``raises``/``fail``, any ``assert*`` helper) and adds the
delegating-helper names (``check*``/``verify*``/``expect*``/``ensure*``/``validate*``/
``assume*``/``require*``). Widening that set can only REMOVE accusations from both family
detectors, because each of them fires only when a test has no effective assertion — the
direction a vocabulary gap must fail in.
"""

from __future__ import annotations

import ast
import re

from argus.detectors.vacuous_vocabulary import is_assertion_callee
from argus.index.ast_index import AstIndexEntry, Definition

__all__ = [
    "FunctionNode",
    "anchor",
    "assertion_calls",
    "bare_asserts",
    "body_without_docstring",
    "callee_name",
    "chain_root",
    "delegates",
    "is_assertion_call",
    "is_collected_test_module",
    "own_nodes",
    "parse_module",
    "raise_statements",
    "same_file_functions",
    "test_functions",
]

FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef

# A helper that may assert on the test's behalf. Matched on the bare callee, case-insensitively,
# with an optional leading underscore (the same exit ``structural_blocking`` uses on wq-1083).
_DELEGATING_HELPER = re.compile(r"\A_*(check|verify|expect|ensure|validate|assume|require)", re.IGNORECASE)

_SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def is_collected_test_module(file_path: str) -> bool:
    """Whether a default runner COLLECTS *file_path*: ``test*.py`` (unittest, and pytest's
    ``test_*.py``) or ``*_test.py`` (pytest).

    ``is_test_file`` answers "is this test code" and claims everything under ``tests/``,
    including fixture DATA such as ``tests/**/fixtures/**/dispatch_check.py``. A test function
    in a module no runner collects never runs, so it cannot pass green, and a family finding
    there would accuse data (measured on Minions at ``dcd90233``: one such block). A project
    with a custom ``python_files`` pattern is read in the silent direction.
    """
    name = file_path.replace("\\", "/").rsplit("/", 1)[-1]
    return name.endswith(".py") and (name.startswith("test") or name.endswith("_test.py"))


def parse_module(source: str) -> ast.Module | None:
    """The module's AST, or ``None`` when the text does not parse (the caller stays silent)."""
    try:
        return ast.parse(source)
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return None


def test_functions(tree: ast.Module) -> list[FunctionNode]:
    """Every ``test*`` function at module level and every ``test*`` method of a module-level class.

    Sorted by ``def`` line so emission order never rests on dict or set order (AR4).
    """
    found: list[FunctionNode] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            found.append(node)
        elif isinstance(node, ast.ClassDef):
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name.startswith("test"):
                    found.append(member)
    return sorted(found, key=lambda f: (f.lineno, f.name))


def own_nodes(func: FunctionNode) -> list[ast.AST]:
    """Every node of *func*'s body, NOT descending into a nested def, lambda or class.

    A nested helper's ``assert`` is not an assertion the test makes unless the test calls
    the helper — and a call to it is caught as a call, not as the helper's body.
    """
    out: list[ast.AST] = []
    stack: list[ast.AST] = list(reversed(func.body))
    while stack:
        node = stack.pop()
        out.append(node)
        if isinstance(node, _SCOPE_NODES):
            continue
        stack.extend(reversed(list(ast.iter_child_nodes(node))))
    return out


def body_without_docstring(func: FunctionNode) -> list[ast.stmt]:
    body = list(func.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(
        body[0].value.value, str
    ):
        body = body[1:]
    return body


def callee_name(call: ast.Call) -> str | None:
    """The bare callee: ``f`` for ``f(...)``, ``attr`` for ``x.y.attr(...)``, else ``None``."""
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def is_assertion_call(call: ast.Call) -> bool:
    name = callee_name(call)
    if name is None:
        return False
    return is_assertion_callee(name) or _DELEGATING_HELPER.match(name) is not None


def bare_asserts(nodes: list[ast.AST]) -> list[ast.Assert]:
    return [n for n in nodes if isinstance(n, ast.Assert)]


def assertion_calls(nodes: list[ast.AST]) -> list[ast.Call]:
    return [n for n in nodes if isinstance(n, ast.Call) and is_assertion_call(n)]


def raise_statements(nodes: list[ast.AST]) -> list[ast.Raise]:
    return [n for n in nodes if isinstance(n, ast.Raise)]


def chain_root(node: ast.AST) -> ast.AST:
    """Strip ``.attr`` / ``(...)`` / ``[...]`` off *node* down to the expression they hang from."""
    while True:
        if isinstance(node, ast.Attribute):
            node = node.value
        elif isinstance(node, ast.Call):
            node = node.func
        elif isinstance(node, ast.Subscript):
            node = node.value
        else:
            return node


def same_file_functions(tree: ast.Module) -> frozenset[str]:
    """Every def at module level and every method of a module-level class — the file's helpers."""
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            names.update(m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)))
    return frozenset(names)


def delegates(func: FunctionNode, nodes: list[ast.AST], same_file: frozenset[str]) -> bool:
    """Whether *func* calls another def of its own file — a helper that may assert on its behalf."""
    for node in nodes:
        if isinstance(node, ast.Call):
            name = callee_name(node)
            if name is not None and name != func.name and name in same_file:
                return True
    return False


def anchor(entry: AstIndexEntry, func: FunctionNode) -> Definition | None:
    """The index's own ``Definition`` for *func* (same name, same ``def`` line), or ``None``."""
    for definition in entry.definitions:
        if definition.kind == "function" and definition.name == func.name and definition.start_line == func.lineno:
            return definition
    return None
