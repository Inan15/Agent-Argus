"""Enforcement: ``canonical.dumps`` is the ONLY JSON serializer in ArgusAgent (AC2).

Verification area ArgusAgent-STORE (TC-ArgusAgent-STORE-001-40). Story 1.1 / AR4 /
cross-cutting #3: NFR-P1 dies the day a second ``json.dumps`` appears in an
``.argus/`` write path with different kwargs. This committed AST scan fails if any
``.py`` under ``argus/`` (other than the allow-listed
``store/canonical.py``) contains a direct ``json.dumps(`` / ``json.dump(`` call.

AST-based so docstrings/comments/strings that merely mention ``json.dumps`` do
not trip it — only real call sites count.
"""

from __future__ import annotations

import ast
from pathlib import Path

_ArgusAgent_ROOT = Path(__file__).resolve().parents[1] / "argus"

# The ONLY module permitted to call json.dumps/json.dump directly.
_ALLOW_LIST = {_ArgusAgent_ROOT / "store" / "canonical.py"}


def _iter_json_dump_calls(tree: ast.AST) -> list[tuple[int, str]]:
    """Return (lineno, name) for every ``json.dumps``/``json.dump`` call node."""
    hits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        # Match attribute form: json.dumps(...) / json.dump(...)
        if (
            isinstance(func, ast.Attribute)
            and func.attr in {"dumps", "dump"}
            and isinstance(func.value, ast.Name)
            and func.value.id == "json"
        ):
            hits.append((node.lineno, f"json.{func.attr}"))
        # Match bare-imported form: dumps(...)/dump(...) only if imported FROM json
        # (handled separately below via import scan, kept simple here).
    return hits


def _imports_dump_from_json(tree: ast.AST) -> set[str]:
    """Return local names bound to json.dumps/json.dump via ``from json import``."""
    bound: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "json":
            for alias in node.names:
                if alias.name in {"dumps", "dump"}:
                    bound.add(alias.asname or alias.name)
    return bound


def _iter_bare_dump_calls(tree: ast.AST, bound: set[str]) -> list[tuple[int, str]]:
    hits: list[tuple[int, str]] = []
    if not bound:
        return hits
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in bound
        ):
            hits.append((node.lineno, node.func.id))
    return hits


def test_no_second_json_serializer_in_argus_write_path() -> None:
    violations: list[str] = []
    for py in sorted(_ArgusAgent_ROOT.rglob("*.py")):
        if py in _ALLOW_LIST:
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        bound = _imports_dump_from_json(tree)
        for lineno, name in _iter_json_dump_calls(tree) + _iter_bare_dump_calls(tree, bound):
            rel = py.relative_to(_ArgusAgent_ROOT.parents[1])
            violations.append(f"{rel}:{lineno} direct {name}( — route via canonical.dumps (AR4)")
    assert not violations, "Second JSON serializer found in .argus/ write path:\n" + "\n".join(
        violations
    )


def test_allow_list_module_exists() -> None:
    # Guard the guard: if canonical.py is moved/renamed the allow-list must follow.
    assert (_ArgusAgent_ROOT / "store" / "canonical.py").is_file()
