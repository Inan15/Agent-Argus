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
    "collected_class_names",
    "delegates",
    "is_assertion_call",
    "is_collected_test_module",
    "own_nodes",
    "parse_module",
    "raise_statements",
    "runner_may_skip",
    "same_file_functions",
    "test_functions",
    "uncollected_test_methods",
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


def _base_name(base: ast.expr) -> str | None:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    return None


def collected_class_names(tree: ast.Module) -> frozenset[str]:
    """Module-level classes a default runner collects test methods from (PURE).

    pytest collects a class named ``Test*``; unittest collects any ``TestCase`` subclass whatever
    its name. A base is read as ``TestCase`` when its bare name ends in ``TestCase``, or when it
    is a collected class of the same file (inheritance). A base imported under another name is
    not resolved: the class stays uncollected, the direction that cannot accuse a non-test.
    """
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    collected = {c.name for c in classes if c.name.startswith("Test")}
    changed = True
    while changed:
        changed = False
        for cls in classes:
            if cls.name in collected:
                continue
            bases = {_base_name(b) for b in cls.bases}
            if any(b is not None and (b.endswith("TestCase") or b in collected) for b in bases):
                collected.add(cls.name)
                changed = True
    return frozenset(collected)


def uncollected_test_methods(tree: ast.Module) -> list[FunctionNode]:
    """Every ``test*`` method of a module-level class no runner collects from (a fake, a helper)."""
    collected = collected_class_names(tree)
    return sorted(
        (
            member
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name not in collected
            for member in node.body
            if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name.startswith("test")
        ),
        key=lambda f: (f.lineno, f.name),
    )


def test_functions(tree: ast.Module) -> list[FunctionNode]:
    """Every ``test*`` function at module level and every ``test*`` method of a COLLECTED class.

    A method of a class that is neither ``Test*`` nor a ``TestCase`` subclass is never run, so it
    is not a test (wq-1134: a ``FakeDriver.test_connection`` is a fake's method, not a test).
    Sorted by ``def`` line so emission order never rests on dict or set order (AR4).
    """
    collected = collected_class_names(tree)
    found: list[FunctionNode] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            found.append(node)
        elif isinstance(node, ast.ClassDef) and node.name in collected:
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


# Marker and decorator names that tell a runner not to run a test, or not to fail it: pytest's
# ``skip``/``skipif``/``xfail``/``importorskip`` and unittest's ``skip``/``skipIf``/
# ``skipUnless``/``expectedFailure``/``SkipTest``. Matched on a bare name or an attribute tail.
_SKIP_NAMES = frozenset(
    {"skip", "skipif", "xfail", "importorskip", "skipIf", "skipUnless", "expectedFailure", "SkipTest"}
)


def _names_a_skip(node: ast.AST) -> bool:
    return any(
        (isinstance(n, ast.Name) and n.id in _SKIP_NAMES) or (isinstance(n, ast.Attribute) and n.attr in _SKIP_NAMES)
        for n in ast.walk(node)
    )


def _assigns_pytestmark(stmt: ast.stmt) -> bool:
    if isinstance(stmt, ast.Assign):
        targets = stmt.targets
    elif isinstance(stmt, (ast.AnnAssign, ast.AugAssign)):
        targets = [stmt.target]
    else:
        return False
    return any(isinstance(t, ast.Name) and t.id == "pytestmark" for t in targets)


def runner_may_skip(tree: ast.Module, func: FunctionNode) -> bool:
    """Whether the runner may SKIP *func* (or not fail it), read from anything that can say so.

    A test the runner skips never passes green, so no family fact about a green-but-vacuous test
    holds for it (wq-1091 probes p2, p3). Four places, each read in the silent direction:

    - a skip/xfail marker among *func*'s OWN decorators (``@pytest.mark.skip``,
      ``@unittest.skipIf(...)``, ``@pytest.mark.xfail``);
    - ANY decorator on the module-level class that holds *func* — pytest and unittest both
      apply a class marker to every method, and the rule never has to parse what it means;
    - a ``pytestmark`` assignment at module level or in that class's body;
    - a module-level statement that can skip the whole module: a ``skip``/``importorskip``
      call or a ``raise ... SkipTest`` anywhere outside a def or class (an ``if`` guarding
      ``pytest.skip(..., allow_module_level=True)`` included).

    A runner configured elsewhere (``conftest.py`` hooks, ``-m`` expressions, ``setup.cfg``)
    is out of reach; the rule stays as it was for those.
    """
    if any(_names_a_skip(d) for d in func.decorator_list):
        return True
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and any(member is func for member in node.body):
            if node.decorator_list or any(_assigns_pytestmark(s) for s in node.body):
                return True
    for stmt in tree.body:
        if _assigns_pytestmark(stmt):
            return True
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for node in ast.walk(stmt):
            if isinstance(node, ast.Call) and callee_name(node) in ("skip", "importorskip"):
                return True
            if isinstance(node, ast.Raise) and node.exc is not None and _names_a_skip(node.exc):
                return True
    return False


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
