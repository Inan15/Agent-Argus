"""tree-sitter Python AST / code-graph index (Story 1.4, AC3/AC4/AC5/AC6).

Verification area ArgusAgent-INDEX (TC-ArgusAgent-INDEX-001-NN). Decision B: definitions +
line spans + a call/reference edge set; non-Python → ast_eligible=False proxy
route (NFR-P2); an unparseable .py → parse_failed=True, run continues (AR10); the
resolved grammar_version is recorded (AR1 / Epic-5 cache-key input).

tree-sitter / tree-sitter-python are the optional `[argus]` extra; the
tree-sitter-dependent assertions importorskip so the suite degrades cleanly where
the extra is absent. The non-Python proxy-route assertion still requires building
the index (parser construction), so it is grouped under the same skip.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.index.ast_index import (  # noqa: E402
    AstIndex,
    AstIndexEntry,
    build_ast_index,
)

_FIXTURE = """\
import os


def alpha(x):
    return beta(x) + os.path.join(x)


class Widget(Base):
    def render(self):
        alpha(1)
        self.helper()
"""


def _entry_for(index: AstIndex, path: str) -> AstIndexEntry:
    for entry in index.entries:
        if entry.file_path == path:
            return entry
    raise AssertionError(f"no index entry for {path}")


def test_definitions_and_spans_extracted(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-70 — functions/classes + 1-based spans extracted."""
    (tmp_path / "m.py").write_text(_FIXTURE, encoding="utf-8")
    index = build_ast_index(tmp_path, ("m.py",))

    assert isinstance(index, AstIndex)
    entry = _entry_for(index, "m.py")
    assert entry.ast_eligible is True
    assert entry.parse_failed is False

    by_name = {d.name: d for d in entry.definitions}
    assert set(by_name) == {"alpha", "Widget", "render"}
    assert by_name["alpha"].kind == "function"
    assert by_name["alpha"].start_line == 4  # 1-based
    assert by_name["Widget"].kind == "class"
    # ast_span renders a Locator.ast_span-compatible token.
    assert by_name["alpha"].ast_span == f"function:alpha@{by_name['alpha'].start_line}-{by_name['alpha'].end_line}"


def test_call_reference_edges_extracted(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-71 — call/reference edge set captured (identifier + attribute)."""
    (tmp_path / "m.py").write_text(_FIXTURE, encoding="utf-8")
    index = build_ast_index(tmp_path, ("m.py",))
    entry = _entry_for(index, "m.py")

    callees = {e.callee for e in entry.edges}
    # 'beta', 'alpha' (identifier calls); 'join', 'helper' (attribute calls).
    assert {"beta", "alpha", "join", "helper"} <= callees


def test_grammar_version_recorded(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-72 — resolved grammar_version recorded (Epic-5/AR5 cache key)."""
    (tmp_path / "m.py").write_text("x = 1\n", encoding="utf-8")
    index = build_ast_index(tmp_path, ("m.py",))
    assert index.grammar_version
    assert index.grammar_version != "unknown"
    assert index.partition_id == "root"


def test_non_python_routes_to_proxy(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-73 — a non-Python file is ast_eligible=False (claim_emitted proxy, NFR-P2)."""
    (tmp_path / "main.go").write_text("package main\n", encoding="utf-8")
    index = build_ast_index(tmp_path, ("main.go",))
    entry = _entry_for(index, "main.go")
    assert entry.ast_eligible is False
    assert entry.parse_failed is False
    assert entry.parse_failure_reason == "non_python"
    assert entry.definitions == ()
    assert entry.edges == ()


def test_unparseable_python_degrades(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-74 — a syntactically-broken .py → parse_failed=True, run continues (AR10)."""
    (tmp_path / "good.py").write_text("def ok():\n    return 1\n", encoding="utf-8")
    (tmp_path / "bad.py").write_text("def broken(:\n    pass\n", encoding="utf-8")
    index = build_ast_index(tmp_path, ("bad.py", "good.py"))

    bad = _entry_for(index, "bad.py")
    assert bad.ast_eligible is False
    assert bad.parse_failed is True
    assert bad.parse_failure_reason == "syntax_error"

    # The run continued and produced the good entry.
    good = _entry_for(index, "good.py")
    assert good.ast_eligible is True
    assert any(d.name == "ok" for d in good.definitions)


def test_entries_sorted_and_index_frozen(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-75 — entries sorted by path (AR11); AstIndex frozen."""
    (tmp_path / "b.py").write_text("p = 1\n", encoding="utf-8")
    (tmp_path / "a.py").write_text("q = 1\n", encoding="utf-8")
    index = build_ast_index(tmp_path, ("b.py", "a.py"))
    assert [e.file_path for e in index.entries] == ["a.py", "b.py"]
    with pytest.raises(Exception):
        index.grammar_version = "x"  # type: ignore[misc]
