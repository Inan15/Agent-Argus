"""Family A: a test with NO EFFECTIVE ASSERTION on the code under test (wq-1084).

Drivers: wq-1084 (step 2 of 3 toward the pre-registered October number — family A, six of the
20 seeded defects, detected by deterministic AST rules and BLOCKING in test files), AR8 (PURE:
the pipeline hands in the test file's text, its 1.4 ``AstIndexEntry`` and a read-only mapping
of the repository's Python sources; no I/O, no clock, no LLM), AR4 (findings sorted by span).

Four facts, one rule id each, at most ONE finding per test (checked in this order)
---------------------------------------------------------------------------------
1. ``assertion_swallowed`` — the test's every assertion site (bare ``assert``, an assertion
   call on the wide vocabulary, a ``raise``) sits inside the body of a ``try`` that also calls
   something, and that ``try`` has a BROAD handler (bare ``except``, ``Exception``,
   ``BaseException``, or a tuple naming one) that neither re-raises, asserts, calls an
   assertion helper nor delegates. ``AssertionError`` is an ``Exception``: whatever the call
   does, the test passes. A test with no assertion at all and such a ``try`` is the same fact.
2. ``assertion_after_return`` — every assertion site comes after a ``return`` that ends the
   test on a path with no assertion: either an unconditional top-level ``return``, or a
   top-level ``if <guard>: return`` whose guard reads a name the test bound from a call into
   a NON-standard-library, non-test-framework import (the unit under test). The guard lets the
   value under test choose whether it is checked. A guard on the environment (a platform or an
   optional import — a name not bound from such a call) is a skip written as ``return`` and
   stays silent.
3. ``assertion_on_mock_only`` — the test has at least one bare ``assert`` and no other
   assertion site, and every value each ``assert`` reads is a mock the test built itself
   (``Mock()``/``MagicMock()``/``AsyncMock()``/``NonCallableMock()``/``PropertyMock()``/
   ``create_autospec(...)``, or an attribute, call or item of one) — and NO such mock ever
   ESCAPES: it is never passed as an argument to anything but another mock, never stored on a
   non-mock object, never put in a container, never returned. A mock that escapes may be
   driven by the code under test, and an assertion on it is interaction testing, not vacuity.
4. ``assertion_absent`` — no assertion site at all, no delegation, and either
   (a) the body is only ``pass``/``...`` (undecorated — a ``skip``/``xfail`` marker makes it a
   labelled placeholder), or (b) the test takes no fixture, is undecorated, and every statement
   is a call whose result is thrown away, to a function imported from the repository whose
   source shows it CANNOT signal failure: no ``raise``, no ``assert``, no ``yield``, no
   ``try``/``with``, no store to an attribute or item, no item read (``d[k]``), at least one ``return`` and every
   ``return`` carries a value, it divides, raises to a power, shifts or matrix-multiplies nowhere
   (``/ // % ** << >> @`` reject some operand, wq-1211), and every call it makes is to a pure
   builtin, a pure method of a builtin value, or another function of its own module meeting the
   same bar. Its arguments are
   all literals. A builtin that rejects a well-typed value (``int("x")``, ``max([])``, ``ord("ab")``) is NOT
   pure (wq-1134 adds ``ord``): a callee that validates its input that way can fail, and a test feeding it a valid
   literal is a "should not raise" test (wq-1127).

   **Why (b) and not "asserts nothing".** Measured on wq-1083: "zero assertion sites" blocked
   9 legitimate Minions tests — import-smoke tests and "should not raise" tests
   (``engine.enforce(valid)``). Such a test is a real test because the call raises on failure.
   (b) blocks only when the callee's own source shows it has no failure signal but its return
   value, and the test discards that value. A callee the pipeline did not hand in, a method
   call, a re-export through a package ``__init__`` or a callee that raises stays silent.

Exits shared by all four: a call into a def of the SAME file (a helper may assert), a module no
default runner collects (``assertion_ast.is_collected_test_module`` — fixture data under
``tests/``), a test the runner may SKIP (``assertion_ast.runner_may_skip``: a skip/xfail marker
on the def, any decorator on its class, a ``pytestmark``, a module-level skip — added in wq-1127
after wq-1091 probes p2 and p3, a class-level ``skip`` and a module ``pytestmark``, still
blocked here once ``structural_blocking`` had stopped blocking them; (a)'s own-decorator check
only ever read the def), a file that does not parse, a test the 1.4 index did not anchor (see
``assertion_ast``).

Blocking, not advisory: each finding carries ``depth_supported=AUDITED_SHALLOW``, the depth
``vacuous_test_ast`` carries, so the verdict gate counts it.
"""

from __future__ import annotations

import ast
import sys
from typing import TYPE_CHECKING, Mapping

from argus.detectors.assertion_ast import (
    FunctionNode,
    anchor,
    assertion_calls,
    bare_asserts,
    body_without_docstring,
    callee_name,
    chain_root,
    delegates,
    is_assertion_call,
    is_collected_test_module,
    own_nodes,
    parse_module,
    raise_statements,
    runner_may_skip,
    same_file_functions,
    test_functions,
)
from argus.detectors.base import DetectorResult, FindingDraft, build_recording
from argus.detectors.vacuous_test import is_test_file
from argus.index.ast_index import AstIndexEntry
from argus.ledger.coverage_ledger import CoverageDepth
from argus.ledger.recording import Recording

__all__ = [
    "RULE_ASSERTION_ABSENT",
    "RULE_ASSERTION_AFTER_RETURN",
    "RULE_ASSERTION_ON_MOCK_ONLY",
    "RULE_ASSERTION_SWALLOWED",
    "IneffectiveAssertionDetector",
    "ineffective_assertion_rule",
]

RULE_ASSERTION_SWALLOWED = "assertion_swallowed"
RULE_ASSERTION_AFTER_RETURN = "assertion_after_return"
RULE_ASSERTION_ON_MOCK_ONLY = "assertion_on_mock_only"
RULE_ASSERTION_ABSENT = "assertion_absent"

_BROAD_EXCEPTIONS = frozenset({"Exception", "BaseException"})
_MOCK_CONSTRUCTORS = frozenset(
    {"Mock", "MagicMock", "AsyncMock", "NonCallableMock", "NonCallableMagicMock", "PropertyMock", "create_autospec"}
)
# Imports whose functions are never the unit under test: the standard library and the test
# frameworks. A guard on a value bound from one of these is an environment check.
_TEST_FRAMEWORKS = frozenset({"pytest", "_pytest", "unittest", "mock", "hypothesis", "pytest_mock"})
_STDLIB = frozenset(sys.stdlib_module_names)

# Builtins KNOWN never to raise on any argument (wq-1164): they convert or test a value and cannot
# reject one. Every other builtin can fail on some input — ``int``/``float``/``bytes``/``chr``/``ord``/
# ``dict``/``list``/``set``/``tuple``/``sum``/``len`` on content or type, ``max``/``min`` on an empty
# iterable, ``divmod``/``pow`` on a zero — and a callee that runs its input through one validates
# it, so a test that feeds it a valid literal and discards the result is a "should not raise" test,
# not an absent assertion. Closing the class means listing what cannot raise, not what has been
# seen to (wq-1127 removed ``int`` and kin, wq-1134 ``ord``, wq-1147 ``dict``). An item read
# ``d[k]`` (KeyError/IndexError) is excluded the same way — see ``_is_pure``.
#
# Caveat (wq-1211): "cannot raise" holds for a value of a builtin type. ``bool``/``str``/``repr`` call
# the argument's own ``__bool__``/``__str__``/``__repr__``, which can raise (``bool`` of a numpy
# array raises ``ValueError``). A test can only feed this rule's callee literals, so the exposure is
# a value the callee reads from OUTSIDE its arguments — a module-level instance — and a callee that
# runs one through these builtins is still read as unable to fail. The residual false block is
# pinned by ``test_precision_probes_r3_dunder.py::test_dunder_caveat_*``, not hidden.
_NEVER_RAISE_BUILTINS = frozenset({"bool", "callable", "repr", "str"})
# Operators that reject a well-typed operand (wq-1211, wq-1147's r3): ``/ // %`` on a zero divisor,
# ``**`` on ``0 ** -1``, ``<< >>`` on a negative count, ``@`` on mismatched shapes. They are
# ``BinOp``/``AugAssign`` nodes, not ``Call`` nodes, so the builtin list above never saw them — a
# callee that divides validates its input exactly as one that calls ``divmod`` does. ``+ - *`` and
# the bitwise operators on numbers stay admitted.
_RAISING_OPERATORS = (ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.MatMult)
# Methods of builtin values that return a value and change nothing the caller can see. The
# codec and format methods (``decode``/``encode``/``format``) raise on content and are absent
# for the reason above.
_PURE_METHODS = frozenset(
    {
        "capitalize", "casefold", "center", "copy", "count", "endswith", "find", "get", "isalnum",
        "isalpha", "isdigit", "islower", "isspace", "isupper", "items", "join", "keys", "ljust",
        "lower", "lstrip", "partition", "replace", "rfind", "rjust", "rpartition", "rsplit",
        "rstrip", "split", "splitlines", "startswith", "strip", "title", "upper", "values", "zfill",
    }
)
# Mutators, admitted only on a container the function itself created (invisible to its caller).
_LOCAL_MUTATORS = frozenset({"add", "append", "extend", "insert", "setdefault", "update"})
_IMPURE_STATEMENTS = (
    ast.Raise, ast.Assert, ast.Yield, ast.YieldFrom, ast.Await, ast.Global, ast.Nonlocal,
    ast.Try, ast.With, ast.AsyncWith, ast.Delete,
)
_PURITY_DEPTH = 3


# ── shared facts ────────────────────────────────────────────────────────────────────────────


def _assertion_sites(nodes: list[ast.AST]) -> list[ast.AST]:
    return [*bare_asserts(nodes), *assertion_calls(nodes), *raise_statements(nodes)]


def _module_imports(tree: ast.Module) -> dict[str, tuple[str, int, str | None]]:
    """Local name → ``(module, level, imported name or None for a plain ``import``)`` (module level)."""
    imports: dict[str, tuple[str, int, str | None]] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    imports[alias.asname or alias.name] = (node.module or "", node.level, alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".")[0]
                imports[local] = (alias.name if alias.asname else local, 0, None)
    return imports


def _is_project_import(module: str, level: int) -> bool:
    if level > 0:
        return True
    top = module.split(".")[0]
    return bool(top) and top not in _STDLIB and top not in _TEST_FRAMEWORKS


# ── 1. swallowed ────────────────────────────────────────────────────────────────────────────


def _is_broad(handler: ast.ExceptHandler) -> bool:
    kind = handler.type
    if kind is None:
        return True
    names = kind.elts if isinstance(kind, ast.Tuple) else [kind]
    for name in names:
        if isinstance(name, ast.Name) and name.id in _BROAD_EXCEPTIONS:
            return True
        if isinstance(name, ast.Attribute) and name.attr in _BROAD_EXCEPTIONS:
            return True
    return False


def _handler_swallows(handler: ast.ExceptHandler, func: FunctionNode, same_file: frozenset[str]) -> bool:
    nodes = [n for stmt in handler.body for n in ast.walk(stmt)]
    if _assertion_sites(nodes) or delegates(func, nodes, same_file):
        return False
    return True


# `try` and, on 3.11+, `try`/`except*` — read by field name, so both share one path.
_TRY_TYPES: tuple[type, ...] = (ast.Try,) + ((getattr(ast, "TryStar"),) if hasattr(ast, "TryStar") else ())


def _swallowing_try_bodies(
    func: FunctionNode, nodes: list[ast.AST], same_file: frozenset[str]
) -> list[list[ast.stmt]]:
    """The ``try`` bodies (not handlers, ``else`` or ``finally``) a broad handler swallows."""
    found: list[list[ast.stmt]] = []
    for node in nodes:
        if not isinstance(node, _TRY_TYPES):
            continue
        body: list[ast.stmt] = getattr(node, "body")
        handlers: list[ast.ExceptHandler] = getattr(node, "handlers")
        body_calls = [
            n for stmt in body for n in ast.walk(stmt) if isinstance(n, ast.Call) and not is_assertion_call(n)
        ]
        if not body_calls:
            continue
        if any(_is_broad(h) and _handler_swallows(h, func, same_file) for h in handlers):
            found.append(body)
    return found


def _swallowed(func: FunctionNode, nodes: list[ast.AST], same_file: frozenset[str]) -> bool:
    bodies = _swallowing_try_bodies(func, nodes, same_file)
    if not bodies:
        return False
    protected = {id(n) for body in bodies for stmt in body for n in ast.walk(stmt)}
    return all(id(site) in protected for site in _assertion_sites(nodes))


# ── 2. after return ─────────────────────────────────────────────────────────────────────────


def _is_bare_return(stmt: ast.stmt) -> bool:
    return isinstance(stmt, ast.Return) and (
        stmt.value is None or (isinstance(stmt.value, ast.Constant) and stmt.value.value is None)
    )


def _names_bound_from_project_call(
    stmts: list[ast.stmt], imports: Mapping[str, tuple[str, int, str | None]]
) -> set[str]:
    bound: set[str] = set()
    for stmt in stmts:
        if not (isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call)):
            continue
        root = chain_root(stmt.value)
        if not isinstance(root, ast.Name) or root.id not in imports:
            continue
        module, level, _ = imports[root.id]
        if not _is_project_import(module, level):
            continue
        for target in stmt.targets:
            if isinstance(target, ast.Name):
                bound.add(target.id)
    return bound


def _after_return(func: FunctionNode, imports: Mapping[str, tuple[str, int, str | None]]) -> bool:
    body = body_without_docstring(func)
    for index, stmt in enumerate(body):
        before = [n for s in body[:index] for n in _stmt_nodes(s)]
        after = [n for s in body[index + 1 :] for n in _stmt_nodes(s)]
        if isinstance(stmt, ast.Return):
            return not _assertion_sites(before) and bool(_assertion_sites(after))
        if (
            isinstance(stmt, ast.If)
            and not stmt.orelse
            and len(stmt.body) == 1
            and _is_bare_return(stmt.body[0])
            and not _assertion_sites(before)
            and not _assertion_sites(list(ast.walk(stmt.test)))
            and _assertion_sites(after)
        ):
            guarded = {n.id for n in ast.walk(stmt.test) if isinstance(n, ast.Name)}
            if guarded & _names_bound_from_project_call(body[:index], imports):
                return True
    return False


def _stmt_nodes(stmt: ast.stmt) -> list[ast.AST]:
    """Every node under *stmt*, not descending into a nested def, lambda or class."""
    out: list[ast.AST] = []
    stack: list[ast.AST] = [stmt]
    while stack:
        node = stack.pop()
        out.append(node)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        stack.extend(ast.iter_child_nodes(node))
    return out


# ── 3. mock only ────────────────────────────────────────────────────────────────────────────


def _parents(func: FunctionNode) -> dict[int, ast.AST]:
    parents: dict[int, ast.AST] = {}
    for node in ast.walk(func):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    return parents


def _builds_or_reads_mock(expr: ast.AST, mocks: set[str]) -> bool:
    node = expr
    while True:
        if isinstance(node, ast.Call):
            if callee_name(node) in _MOCK_CONSTRUCTORS:
                return True
            node = node.func
        elif isinstance(node, (ast.Attribute, ast.Subscript)):
            node = node.value
        else:
            return isinstance(node, ast.Name) and node.id in mocks


def _mock_names(func: FunctionNode) -> set[str]:
    """Names every binding of which is a mock the test built, or a read of one (fixed point)."""
    # name -> every value bound to it; None marks a binding whose value is unknown (a parameter,
    # a tuple target, a loop or `with ... as` target, `+=`, `del`).
    bindings: dict[str, list[ast.AST | None]] = {}
    recorded: set[int] = set()
    for node in ast.walk(func):
        if isinstance(node, ast.arg):
            bindings.setdefault(node.arg, []).append(None)
        elif isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) for t in node.targets):
            for target in node.targets:
                assert isinstance(target, ast.Name)
                bindings.setdefault(target.id, []).append(node.value)
                recorded.add(id(target))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            bindings.setdefault(node.target.id, []).append(node.value)
            recorded.add(id(node.target))
    for node in ast.walk(func):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)) and id(node) not in recorded:
            bindings.setdefault(node.id, []).append(None)
    mocks: set[str] = set()
    changed = True
    while changed:
        changed = False
        for name, values in bindings.items():
            if name in mocks or not values or any(v is None for v in values):
                continue
            if all(_builds_or_reads_mock(v, mocks) for v in values if v is not None):
                mocks.add(name)
                changed = True
    return mocks


def _chain_top(node: ast.AST, parents: Mapping[int, ast.AST]) -> ast.AST:
    """Climb from a name to the largest ``.attr`` / ``(...)`` / ``[...]`` chain it roots."""
    while True:
        parent = parents.get(id(node))
        if isinstance(parent, ast.Attribute) and parent.value is node:
            node = parent
        elif isinstance(parent, ast.Call) and parent.func is node:
            node = parent
        elif isinstance(parent, ast.Subscript) and parent.value is node:
            node = parent
        else:
            return node


def _inside_assert(node: ast.AST, parents: Mapping[int, ast.AST]) -> bool:
    current: ast.AST | None = node
    while current is not None:
        if isinstance(current, ast.Assert):
            return True
        current = parents.get(id(current))
    return False


def _escapes(name_node: ast.Name, mocks: set[str], parents: Mapping[int, ast.AST]) -> bool:
    top = _chain_top(name_node, parents)
    if _inside_assert(top, parents):
        return False
    parent = parents.get(id(top))
    if isinstance(parent, ast.Expr):
        return False
    if isinstance(parent, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
        targets = parent.targets if isinstance(parent, ast.Assign) else [parent.target]
        if any(t is top for t in targets):
            return False  # configuring the mock: `fake.compute.return_value = 25`
        return not all(
            isinstance(t, ast.Name) or _builds_or_reads_mock(t, mocks) for t in targets
        )
    if isinstance(parent, ast.Call) and (top in parent.args or any(k.value is top for k in parent.keywords)):
        return not _builds_or_reads_mock(parent.func, mocks) and callee_name(parent) not in _MOCK_CONSTRUCTORS
    return True


def _assert_subjects(assertion: ast.Assert, mocks: set[str], parents: Mapping[int, ast.AST]) -> list[str]:
    subjects = []
    for node in ast.walk(assertion.test):
        if not (isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)):
            continue
        parent = parents.get(id(node))
        if isinstance(parent, ast.Call) and parent.func is node and node.id not in mocks:
            continue  # the function being called (`len`, `round`, the SUT), not a value read
        subjects.append(node.id)
    return subjects


def _mock_only(func: FunctionNode, nodes: list[ast.AST]) -> bool:
    asserts = bare_asserts(nodes)
    if not asserts or assertion_calls(nodes) or raise_statements(nodes):
        return False
    mocks = _mock_names(func)
    if not mocks:
        return False
    parents = _parents(func)
    own = {id(n) for n in nodes}
    for node in ast.walk(func):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in mocks:
            if id(node) not in own or _escapes(node, mocks, parents):
                return False
    for assertion in asserts:
        subjects = _assert_subjects(assertion, mocks, parents)
        if not subjects or any(s not in mocks for s in subjects):
            return False
    return True


# ── 4. absent ───────────────────────────────────────────────────────────────────────────────


def _is_literal(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return all(_is_literal(e) for e in node.elts)
    if isinstance(node, ast.Dict):
        return all(k is not None and _is_literal(k) for k in node.keys) and all(_is_literal(v) for v in node.values)
    if isinstance(node, ast.UnaryOp):
        return _is_literal(node.operand)
    return False


def _cannot_fail_body(func: FunctionNode) -> bool:
    if func.decorator_list:
        return False
    return all(
        isinstance(s, ast.Pass) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))
        for s in body_without_docstring(func)
    )


def _module_candidates(test_path: str, module: str, level: int) -> list[str]:
    parts = [p for p in module.split(".") if p]
    if level > 0:
        base = test_path.split("/")[:-1]
        if level - 1 > len(base):
            return []
        base = base[: len(base) - (level - 1)]
        stem = "/".join(base + parts)
        return [f"{stem}.py", f"{stem}/__init__.py"] if parts else [f"{'/'.join(base)}/__init__.py"]
    if not parts:
        return []
    stem = "/".join(parts)
    return [f"{stem}.py", f"{stem}/__init__.py", f"src/{stem}.py", f"src/{stem}/__init__.py"]


def _top_level_def(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    matches = [
        n for n in tree.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign))
        and _defines(n, name)
    ]
    if len(matches) == 1 and isinstance(matches[0], ast.FunctionDef):
        return matches[0]
    return None


def _defines(node: ast.AST, name: str) -> bool:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name == name
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]  # type: ignore[attr-defined]
    return any(isinstance(n, ast.Name) and n.id == name for t in targets for n in ast.walk(t))


def _is_pure(fn: ast.FunctionDef, module: ast.Module, depth: int, seen: frozenset[str]) -> bool:
    """Whether *fn*'s own source shows no failure signal but its return value (see docstring, 4b)."""
    if fn.decorator_list or depth > _PURITY_DEPTH or fn.name in seen:
        return False
    nodes = own_nodes(fn)
    if any(isinstance(n, _IMPURE_STATEMENTS) for n in nodes):
        return False
    returns = [n for n in nodes if isinstance(n, ast.Return)]
    if not returns or any(
        r.value is None or (isinstance(r.value, ast.Constant) and r.value.value is None) for r in returns
    ):
        return False
    params = {a.arg for a in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs)}
    params.update(a.arg for a in (fn.args.vararg, fn.args.kwarg) if a is not None)
    for node in nodes:
        if isinstance(node, (ast.Attribute, ast.Subscript)) and isinstance(node.ctx, (ast.Store, ast.Del)):
            return False
        if isinstance(node, ast.Subscript) and not isinstance(node.slice, ast.Slice):
            return False  # an item read raises KeyError/IndexError on input: a validating callee
        if isinstance(node, (ast.BinOp, ast.AugAssign)) and isinstance(node.op, _RAISING_OPERATORS):
            return False  # a division/power/shift raises on some operand: a validating callee
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            if func.id in _NEVER_RAISE_BUILTINS:
                continue
            callee = _top_level_def(module, func.id)
            if callee is not None and _is_pure(callee, module, depth + 1, seen | {fn.name}):
                continue
            return False
        if isinstance(func, ast.Attribute):
            if func.attr in _PURE_METHODS:
                continue
            receiver = func.value
            if func.attr in _LOCAL_MUTATORS and isinstance(receiver, ast.Name) and receiver.id not in params:
                continue
        return False
    return True


def _discards_only_pure_calls(
    func: FunctionNode,
    tree_imports: Mapping[str, tuple[str, int, str | None]],
    test_path: str,
    module_sources: Mapping[str, str],
) -> bool:
    args = func.args
    positional = [a.arg for a in (*args.posonlyargs, *args.args)]
    if positional not in ([], ["self"], ["cls"]) or args.kwonlyargs or args.vararg or args.kwarg:
        return False
    if func.decorator_list:
        return False
    body = body_without_docstring(func)
    if not body:
        return False
    for stmt in body:
        if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)):
            return False
        call = stmt.value
        if not isinstance(call.func, ast.Name) or call.func.id not in tree_imports:
            return False
        if not all(_is_literal(a) for a in call.args) or not all(
            k.arg is not None and _is_literal(k.value) for k in call.keywords
        ):
            return False
        module, level, original = tree_imports[call.func.id]
        if original is None or not _is_project_import(module, level):
            return False
        resolved = [p for p in _module_candidates(test_path, module, level) if p in module_sources]
        if len(resolved) != 1:
            return False
        callee_source = module_sources.get(resolved[0])
        callee_tree = parse_module(callee_source) if callee_source is not None else None
        if callee_tree is None:
            return False
        callee = _top_level_def(callee_tree, original)
        if callee is None or not _is_pure(callee, callee_tree, 0, frozenset()):
            return False
    return True


# ── the detector ────────────────────────────────────────────────────────────────────────────


def ineffective_assertion_rule(
    func: FunctionNode,
    *,
    same_file: frozenset[str],
    imports: Mapping[str, tuple[str, int, str | None]],
    test_path: str,
    module_sources: Mapping[str, str],
) -> str | None:
    """The family-A rule id *func* establishes, or ``None`` (PURE). See the module docstring."""
    nodes = own_nodes(func)
    if delegates(func, nodes, same_file):
        return None
    if _swallowed(func, nodes, same_file):
        return RULE_ASSERTION_SWALLOWED
    if _after_return(func, imports):
        return RULE_ASSERTION_AFTER_RETURN
    if _mock_only(func, nodes):
        return RULE_ASSERTION_ON_MOCK_ONLY
    if not _assertion_sites(nodes) and (
        _cannot_fail_body(func) or _discards_only_pure_calls(func, imports, test_path, module_sources)
    ):
        return RULE_ASSERTION_ABSENT
    return None


class IneffectiveAssertionDetector:
    """PURE family-A detector. Findings only — the vacuous detector grades the file (AR8)."""

    rule_id = RULE_ASSERTION_ABSENT

    def run(
        self,
        *,
        file_path: str,
        source: str,
        ast_entry: AstIndexEntry,
        module_sources: Mapping[str, str] | None = None,
        coverage_envelope_slice: str | None = None,
    ) -> DetectorResult:
        """Findings for *file_path*. *module_sources* (repo path → text) resolves a callee for 4b;
        without it 4b stays silent and the other three facts are unaffected."""
        if not is_collected_test_module(file_path) or not is_test_file(file_path, ast_entry=ast_entry):
            return DetectorResult()
        if ast_entry.parse_failed or not ast_entry.ast_eligible:
            return DetectorResult()
        tree = parse_module(source)
        if tree is None:
            return DetectorResult()
        same_file = same_file_functions(tree)
        imports = _module_imports(tree)
        sources: Mapping[str, str] = module_sources if module_sources is not None else {}
        findings: list[Recording] = []
        for func in test_functions(tree):
            if runner_may_skip(tree, func):
                continue
            rule_id = ineffective_assertion_rule(
                func, same_file=same_file, imports=imports, test_path=file_path, module_sources=sources
            )
            if rule_id is None:
                continue
            definition = anchor(ast_entry, func)
            if definition is None:
                continue
            draft = FindingDraft(
                file_path=file_path,
                start_line=definition.start_line,
                end_line=definition.end_line,
                ast_span=definition.ast_span,
                rule_id=rule_id,
                advisory=True,
                coverage_envelope_slice=coverage_envelope_slice,
            )
            findings.append(build_recording(draft, depth_supported=CoverageDepth.AUDITED_SHALLOW, claim_present=False))
        return DetectorResult(findings=tuple(findings))


if TYPE_CHECKING:  # pragma: no cover - static conformance pin (Story 18.4 / AC2)
    from argus.detectors.base import Detector

    _DETECTOR_CONFORMANCE_PIN: Detector = IneffectiveAssertionDetector()
