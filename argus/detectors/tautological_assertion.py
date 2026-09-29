"""Family B: a test whose every assertion is TRUE BY CONSTRUCTION (wq-1084).

Drivers: wq-1084 (step 2 of 3 toward the pre-registered October number — family B, five of the
20 seeded defects, detected by a deterministic AST rule and BLOCKING in test files), AR8
(PURE: a function of the test file's text and its 1.4 ``AstIndexEntry``; no I/O, no clock,
no LLM), AR4 (findings sorted by span; no float in any emitted value).

The fact (``tautological_assertion``)
------------------------------------
A ``test*`` function in a test file, with at least one bare ``assert``, in which EVERY
``assert`` is true whatever the code under test does:

- **a truthy literal** — ``assert True``, ``assert "ok"``, ``assert 1``;
- **a non-empty tuple** — ``assert (x == 1, "message")``, which is always truthy;
- **a comparison of literals that holds** — ``assert 1 == 1``, ``assert "a" in "abc"``;
- **``isinstance`` of a literal against a builtin type that holds** — ``assert isinstance(5, int)``;
- **a reflexive comparison** — ``assert x == x`` / ``x is x`` / ``x <= x`` / ``x >= x`` on a
  call-free operand;
- **a literal the test itself bound** — ``expected = 25`` then ``assert expected == 25``: a
  name bound ONCE in the test, to an IMMUTABLE literal, never rebound anywhere in the function,
  is replaced by its literal before the three checks above;
- **an ``or`` with a tautological operand** — ``assert f() == g() or True``; an ``and`` whose
  every operand is tautological.

A false literal comparison (``assert 1 == 2``) is NOT this fact — it always fails, which is a
red suite, not a false green. It is evaluated and left silent.

Exits that keep a test silent, each on the side of not accusing
---------------------------------------------------------------
- **any other assertion** — an assertion call on the wide vocabulary (``assertEqual``,
  ``pytest.raises``, ``mock.assert_called_once_with``, an ``assert*``/``check*``/``verify*``
  helper), a ``raise`` statement, or a call into a def of the SAME file (a helper may assert
  on the test's behalf). A placeholder ``assert True`` beside a real assertion is dead weight,
  not a test that cannot fail, and this rule does not block it;
- **a reflexive comparison in an equality-contract test** — a test whose name mentions
  ``eq``/``equal``/``reflex``/``ident``/``same``/``compar``/``hash``/``order``/``sort`` may be
  testing ``__eq__`` itself, where ``obj == obj`` is the point;
- **a module no default runner collects** — ``tests/**/fixtures/**/dispatch_check.py`` is test
  DATA; its ``assert True`` never runs (``assertion_ast.is_collected_test_module``);
- **a test the runner may skip** — a skip/xfail marker on the def, any decorator on its class,
  a ``pytestmark``, a module-level skip (``assertion_ast.runner_may_skip``, wq-1127): a skipped
  ``assert True`` placeholder never passes green;
- **a file that does not parse, or a test the index did not anchor** — silent (see
  ``assertion_ast``).

Blocking, not advisory
----------------------
A finding carries ``depth_supported=AUDITED_SHALLOW`` — the depth ``vacuous_test_ast`` carries
— so the verdict gate counts it. The rule is a fact read off the source, not a threshold: an
assertion that holds for every input cannot fail for a wrong one.
"""

from __future__ import annotations

import ast
import operator
import re
from typing import TYPE_CHECKING, Any, Callable, Mapping

from argus.detectors.assertion_ast import (
    FunctionNode,
    anchor,
    assertion_calls,
    bare_asserts,
    callee_name,
    delegates,
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
    "RULE_TAUTOLOGICAL_ASSERTION",
    "TautologicalAssertionDetector",
    "is_tautology",
    "test_bound_literals",
]

RULE_TAUTOLOGICAL_ASSERTION = "tautological_assertion"

# A test whose name says it tests equality/ordering/hashing may compare an object to itself on
# purpose; the reflexive branch stays silent there (the literal branches do not).
_EQUALITY_CONTRACT_NAME = re.compile(r"eq|equal|reflex|ident|same|compar|hash|order|sort", re.IGNORECASE)

_BUILTIN_TYPES: Mapping[str, type] = {
    "bool": bool,
    "bytes": bytes,
    "complex": complex,
    "dict": dict,
    "float": float,
    "frozenset": frozenset,
    "int": int,
    "list": list,
    "object": object,
    "set": set,
    "str": str,
    "tuple": tuple,
}

_COMPARE_OPS: Mapping[type, Callable[[Any, Any], Any]] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
}
_REFLEXIVE_OPS = (ast.Eq, ast.Is, ast.LtE, ast.GtE)
_IMMUTABLE = (int, float, complex, str, bytes, bool, type(None))


class _NotLiteral(Exception):
    """The expression reads something other than a literal (internal control flow only)."""


def _literal(node: ast.AST, consts: Mapping[str, Any]) -> Any:
    """The value of a literal-only expression, or :class:`_NotLiteral`. Never runs user code."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in consts:
            return consts[node.id]
        raise _NotLiteral
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        if any(isinstance(e, ast.Starred) for e in node.elts):
            raise _NotLiteral
        items = [_literal(e, consts) for e in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(items)
        if isinstance(node, ast.List):
            return items
        try:
            return set(items)
        except TypeError as exc:
            raise _NotLiteral from exc
    if isinstance(node, ast.Dict):
        if any(k is None for k in node.keys):
            raise _NotLiteral
        try:
            return {_literal(k, consts): _literal(v, consts) for k, v in zip(node.keys, node.values) if k is not None}
        except TypeError as exc:
            raise _NotLiteral from exc
    if isinstance(node, ast.UnaryOp):
        value = _literal(node.operand, consts)
        if isinstance(node.op, ast.Not):
            return not value
        if isinstance(value, (int, float, complex)) and not isinstance(value, bool):
            if isinstance(node.op, ast.USub):
                return -value
            if isinstance(node.op, ast.UAdd):
                return +value
        raise _NotLiteral
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
        left, right = _literal(node.left, consts), _literal(node.right, consts)
        numeric = all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (left, right))
        if numeric:
            return left + right if isinstance(node.op, ast.Add) else left - right
        if isinstance(node.op, ast.Add) and type(left) is type(right) and isinstance(left, (str, bytes, tuple)):
            return left + right
        raise _NotLiteral
    if isinstance(node, ast.Compare):
        left = _literal(node.left, consts)
        for op, comparator in zip(node.ops, node.comparators):
            right = _literal(comparator, consts)
            if isinstance(op, (ast.Is, ast.IsNot)):
                # Identity is only defined here for the singletons; `1 is 1` is an
                # implementation detail, not a literal fact.
                if not all(v is None or isinstance(v, bool) for v in (left, right)):
                    raise _NotLiteral
                holds = (left is right) if isinstance(op, ast.Is) else (left is not right)
            else:
                try:
                    holds = bool(_COMPARE_OPS[type(op)](left, right))
                except (TypeError, KeyError) as exc:
                    raise _NotLiteral from exc
            if not holds:
                return False
            left = right
        return True
    if isinstance(node, ast.BoolOp):
        values = [_literal(v, consts) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        return any(values)
    if isinstance(node, ast.Call) and callee_name(node) == "isinstance" and isinstance(node.func, ast.Name):
        if len(node.args) != 2 or node.keywords:
            raise _NotLiteral
        value = _literal(node.args[0], consts)
        return isinstance(value, _builtin_type_spec(node.args[1]))
    raise _NotLiteral


def _builtin_type_spec(node: ast.AST) -> type | tuple[type, ...]:
    if isinstance(node, ast.Name) and node.id in _BUILTIN_TYPES:
        return _BUILTIN_TYPES[node.id]
    if isinstance(node, ast.Tuple) and node.elts:
        return tuple(_single_builtin_type(e) for e in node.elts)
    raise _NotLiteral


def _single_builtin_type(node: ast.AST) -> type:
    if isinstance(node, ast.Name) and node.id in _BUILTIN_TYPES:
        return _BUILTIN_TYPES[node.id]
    raise _NotLiteral


def _is_call_free_operand(node: ast.AST) -> bool:
    """A name, an attribute chain, or a constant subscript of one — reading it twice reads one value."""
    if isinstance(node, (ast.Name, ast.Constant)):
        return True
    if isinstance(node, ast.Attribute):
        return _is_call_free_operand(node.value)
    if isinstance(node, ast.Subscript):
        return _is_call_free_operand(node.value) and isinstance(node.slice, ast.Constant)
    return False


def _root_name(node: ast.AST) -> str | None:
    while isinstance(node, (ast.Attribute, ast.Subscript)):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def call_bound_names(func: FunctionNode) -> frozenset[str]:
    """Names the test binds from an expression holding a call (PURE).

    ``m = mean(xs); assert m == m`` is the not-NaN idiom: the value is computed, and ``nan != nan``,
    so the assert can fail. A reflexive comparison on such a name is not a tautology (wq-1134).
    """
    bound: set[str] = set()

    def _holds_call(value: ast.AST | None) -> bool:
        return value is not None and any(isinstance(n, ast.Call) for n in ast.walk(value))

    def _add(target: ast.AST) -> None:
        bound.update(n.id for n in ast.walk(target) if isinstance(n, ast.Name))

    for node in ast.walk(func):
        if isinstance(node, ast.Assign) and _holds_call(node.value):
            for target in node.targets:
                _add(target)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)) and _holds_call(node.value):
            _add(node.target)
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)) and _holds_call(node.iter):
            _add(node.target)
        elif isinstance(node, ast.withitem) and node.optional_vars is not None and _holds_call(node.context_expr):
            _add(node.optional_vars)
    return frozenset(bound)


def is_tautology(
    node: ast.AST,
    consts: Mapping[str, Any],
    *,
    allow_reflexive: bool = True,
    call_bound: frozenset[str] = frozenset(),
) -> bool:
    """Whether the ``assert`` test expression *node* holds whatever the code under test does (PURE)."""
    if isinstance(node, ast.Tuple) and node.elts:
        return True
    if isinstance(node, ast.BoolOp):
        verdicts = [
            is_tautology(v, consts, allow_reflexive=allow_reflexive, call_bound=call_bound) for v in node.values
        ]
        if isinstance(node.op, ast.Or) and any(verdicts):
            return True
        if isinstance(node.op, ast.And) and all(verdicts):
            return True
    if (
        allow_reflexive
        and isinstance(node, ast.Compare)
        and len(node.ops) == 1
        and isinstance(node.ops[0], _REFLEXIVE_OPS)
        and _is_call_free_operand(node.left)
        and not isinstance(node.left, ast.Constant)
        and _root_name(node.left) not in call_bound
        and ast.dump(node.left) == ast.dump(node.comparators[0])
    ):
        return True
    try:
        return bool(_literal(node, consts))
    except (_NotLiteral, RecursionError, ValueError, OverflowError):
        return False


def test_bound_literals(func: FunctionNode) -> dict[str, Any]:
    """Names the test binds EXACTLY ONCE, to an immutable literal, and never rebinds (PURE).

    Every ``Store`` of a name anywhere inside *func* (nested scopes included), every parameter,
    and every ``global``/``nonlocal`` declaration counts as a binding, so a name that could hold
    anything else at the ``assert`` is never substituted.
    """
    stores: dict[str, int] = {}
    excluded: set[str] = set()
    for node in ast.walk(func):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            stores[node.id] = stores.get(node.id, 0) + 1
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            excluded.update(node.names)
        elif isinstance(node, ast.arg):
            excluded.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node is not func:
            excluded.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            excluded.update((a.asname or a.name).split(".")[0] for a in node.names)
    consts: dict[str, Any] = {}
    for node in own_nodes(func):
        target: ast.AST | None = None
        value: ast.AST | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            target, value = node.target, node.value
        if not isinstance(target, ast.Name) or value is None:
            continue
        name = target.id
        if name in excluded or stores.get(name) != 1:
            continue
        try:
            literal = _literal(value, {})
        except (_NotLiteral, RecursionError, ValueError, OverflowError):
            continue
        if _is_immutable(literal):
            consts[name] = literal
    return consts


def _is_immutable(value: Any) -> bool:
    if isinstance(value, _IMMUTABLE):
        return True
    if isinstance(value, (tuple, frozenset)):
        return all(_is_immutable(v) for v in value)
    return False


def all_assertions_tautological(func: FunctionNode, same_file: frozenset[str]) -> bool:
    """The family-B fact for ONE test function (PURE). See the module docstring."""
    nodes = own_nodes(func)
    asserts = bare_asserts(nodes)
    if not asserts:
        return False
    if assertion_calls(nodes) or raise_statements(nodes) or delegates(func, nodes, same_file):
        return False
    consts = test_bound_literals(func)
    allow_reflexive = _EQUALITY_CONTRACT_NAME.search(func.name) is None
    call_bound = call_bound_names(func)
    return all(
        is_tautology(a.test, consts, allow_reflexive=allow_reflexive, call_bound=call_bound) for a in asserts
    )


class TautologicalAssertionDetector:
    """PURE family-B detector. Findings only — the vacuous detector grades the file (AR8)."""

    rule_id = RULE_TAUTOLOGICAL_ASSERTION

    def run(
        self,
        *,
        file_path: str,
        source: str,
        ast_entry: AstIndexEntry,
        coverage_envelope_slice: str | None = None,
    ) -> DetectorResult:
        if not is_collected_test_module(file_path) or not is_test_file(file_path, ast_entry=ast_entry):
            return DetectorResult()
        if ast_entry.parse_failed or not ast_entry.ast_eligible:
            return DetectorResult()
        tree = parse_module(source)
        if tree is None:
            return DetectorResult()
        same_file = same_file_functions(tree)
        findings: list[Recording] = []
        for func in test_functions(tree):
            if runner_may_skip(tree, func) or not all_assertions_tautological(func, same_file):
                continue
            definition = anchor(ast_entry, func)
            if definition is None:
                continue
            draft = FindingDraft(
                file_path=file_path,
                start_line=definition.start_line,
                end_line=definition.end_line,
                ast_span=definition.ast_span,
                rule_id=RULE_TAUTOLOGICAL_ASSERTION,
                advisory=True,
                coverage_envelope_slice=coverage_envelope_slice,
            )
            findings.append(build_recording(draft, depth_supported=CoverageDepth.AUDITED_SHALLOW, claim_present=False))
        return DetectorResult(findings=tuple(findings))


if TYPE_CHECKING:  # pragma: no cover - static conformance pin (Story 18.4 / AC2)
    from argus.detectors.base import Detector

    _DETECTOR_CONFORMANCE_PIN: Detector = TautologicalAssertionDetector()
