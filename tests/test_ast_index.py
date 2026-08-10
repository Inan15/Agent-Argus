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


def test_ungrammared_language_routes_to_proxy(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-73 — a file with no installed grammar is ast_eligible=False.

    The degradation reason now NAMES the missing grammar rather than saying
    ``non_python``. Those are two different states with two different remedies —
    "unsupported language" (nothing to do) versus "supported, grammar not installed"
    (one pip install) — and reporting the former for the latter left an operator with
    a zero-coverage verdict and no way to act on it.
    """
    pytest.importorskip("tree_sitter")
    (tmp_path / "main.go").write_text("package main\n", encoding="utf-8")
    index = build_ast_index(tmp_path, ("main.go",))
    entry = _entry_for(index, "main.go")

    assert entry.parse_failed is False
    # The old blanket token must never reappear — it conflated "unsupported language"
    # with "grammar not installed", which have different remedies.
    assert entry.parse_failure_reason != "non_python"

    # Whether the grammar happens to be installed in THIS environment is not the
    # contract; both outcomes must be honest, so assert the one that applies.
    if entry.ast_eligible:
        assert entry.parse_failure_reason is None
    else:
        assert entry.parse_failure_reason == "grammar_missing_go"
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


# ─────────────────────────────────────────────────────────────────────────────
# Story 10.2 / AC4 — provenance names the grammar that actually parsed, per grammar
# ─────────────────────────────────────────────────────────────────────────────
#
# Measured on this tree 2026-08-10: a ten-language index recorded
# `grammar_version = '0.25.0'` — `tree-sitter-python`'s — for a build in which
# tree-sitter-rust 0.24.2, tree-sitter-java 0.23.5 and tree-sitter-ruby 0.23.1 had each
# parsed a file. The recorded provenance was therefore wrong for 7 of the 8 languages
# that grounded, and a Go/Rust/Java/C/C++/Ruby grammar upgrade would not have moved the
# R3 cache key. That is the silent-cache-staleness class DF-5-1-A already files for
# `prompt_template_version`, and the architecture records it as a DESIGN change (R3 was
# designed for one grammar) rather than a defect fix.
#
# The fix is ADDITIVE (PRD :393, story DN-5): `grammar_version` is RETAINED, the
# per-grammar record is added beside it, and `schema_version` is bumped.


def _provenance_map(index: AstIndex) -> dict[str, str]:
    return {record.language: record.version for record in index.grammar_versions}


def test_TC_ArgusAgent_INDEX_001_105_provenance_is_recorded_per_grammar(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-105 — Story 10.2/AC4.1: per-grammar provenance, sorted and frozen.

    One scalar cannot describe a ten-language index. Each grammar that actually parsed is recorded
    with the version of its own package, sorted by language (AR11) in a frozen tuple of frozen
    models (the `Definition`/`CodeEdge` house shape), with no float and no dict-iteration-order
    reliance (AR4/NFR-D1).
    """
    (tmp_path / "m.py").write_text(_FIXTURE, encoding="utf-8")
    index = build_ast_index(tmp_path, ("m.py",))

    assert index.grammar_versions, (
        "AstIndex recorded NO per-grammar provenance for a build that parsed a Python file. The "
        "R3 cache key would then be blind to every grammar that participated (DF-AUD-APAA-D)."
    )
    languages = [record.language for record in index.grammar_versions]
    assert languages == sorted(languages), (
        f"per-grammar provenance is not sorted by language: {languages} (AR11/AR4 — an "
        "unsorted record makes the derived cache key depend on dict iteration order)"
    )
    assert len(languages) == len(set(languages)), (
        f"a language appears twice in the provenance record: {languages}"
    )
    assert isinstance(index.grammar_versions, tuple), (
        "provenance must be a frozen tuple, not a list — the index is a frozen pure contract"
    )
    for record in index.grammar_versions:
        with pytest.raises(Exception):
            record.version = "mutated"  # type: ignore[misc]
        assert isinstance(record.version, str), "no float in a determinism input (AR4)"

    # It names the grammar that actually parsed, with that grammar's own version.
    assert _provenance_map(index) == {"python": index.grammar_version}, (
        "a Python-only build must record exactly the python grammar, at exactly the version the "
        "retained scalar reports — the two must not be able to disagree"
    )


def test_TC_ArgusAgent_INDEX_001_106_only_grammars_that_parsed_are_recorded(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-106 — Story 10.2/AC4.3 + DN-6: both directions, asserted.

    A grammar that parsed IS recorded; a grammar that did not is NOT. Recording every INSTALLED
    grammar would make the key a function of the HOST rather than of the AUDIT — a determinism
    regression (NFR-D1/AR4) and the exact inverse of the defect being closed. This host has all ten
    grammars installed, so the second direction is a live risk here, not a hypothetical one.
    """
    (tmp_path / "m.py").write_text(_FIXTURE, encoding="utf-8")
    (tmp_path / "notes.txt").write_text("not source\n", encoding="utf-8")
    index = build_ast_index(tmp_path, ("m.py", "notes.txt"))

    recorded = set(_provenance_map(index))
    assert recorded == {"python"}, (
        f"a Python-only audit recorded provenance for {sorted(recorded)}. Only grammars that "
        "actually parsed a file in THIS build may be recorded; anything else keys the cache on "
        "the host's installed packages (DN-6)."
    )

    # …and a language whose file IS present is recorded, so the assertion above is not passing by
    # recording nothing at all.
    (tmp_path / "s.go").write_text("package main\n\nfunc Add() int { return 1 }\n", encoding="utf-8")
    with_go = build_ast_index(tmp_path, ("m.py", "s.go"))
    go_entry = _entry_for(with_go, "s.go")
    if go_entry.ast_eligible:
        assert "go" in _provenance_map(with_go), (
            "a Go file parsed cleanly but the go grammar is missing from the provenance record — "
            "a grammar that determined this index's contents is invisible to the cache key"
        )
        assert _provenance_map(with_go)["go"] != "", "the recorded go version is empty"
    else:  # the optional `[languages]` extra is absent in this environment
        assert "go" not in _provenance_map(with_go), (
            "the go grammar could not parse, yet it was recorded as participating provenance"
        )


def test_TC_ArgusAgent_INDEX_001_107_the_scalar_is_retained_and_the_schema_bumped(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-INDEX-001-107 — Story 10.2/AC4.2 + DN-5: additive-only, and the docstring lie fixed.

    PRD `:393` binds schema evolution to additive-only: new fields, `schema_version` bumped,
    determinism preserved. `grammar_version` is therefore RETAINED — roughly ten existing test
    constructions and `argus/dogfood/partition_plan.py` depend on it — and the per-grammar record is
    added beside it. What is corrected is the FIELD DESCRIPTION, which implied the scalar was the
    index's provenance. It never was: it is, and always was, the resolved `tree-sitter-python`
    package version, and reading it as the index's provenance is what misled the R3 design.
    """
    (tmp_path / "m.py").write_text(_FIXTURE, encoding="utf-8")
    index = build_ast_index(tmp_path, ("m.py",))

    assert index.grammar_version, "the retained scalar must still be populated (additive-only)"
    assert index.schema_version == "2", (
        f"AstIndex.schema_version is {index.schema_version!r}; adding the per-grammar provenance "
        "field is a schema change and must bump it (PRD :393, additive-only policy)"
    )

    # The new field is DEFAULTED, so the existing constructions keep working unedited (AC4.4).
    legacy = AstIndex(grammar_version="test", entries=())
    assert legacy.grammar_versions == (), (
        "AstIndex(grammar_version=...) without the new field must still construct, with an empty "
        "provenance record — ~10 existing test constructions and partition_plan.py rely on it"
    )

    description = AstIndex.model_fields["grammar_version"].description or ""
    assert "tree-sitter-python" in description, (
        "the retained scalar's description must say WHAT IT ACTUALLY IS — the resolved "
        "`tree-sitter-python` package version — rather than implying it is the index's provenance. "
        "That implication is what the R3 cache-key design was built on (story §D)."
    )
    provenance_description = AstIndex.model_fields["grammar_versions"].description or ""
    assert "parsed" in provenance_description.lower(), (
        "the per-grammar field's description must state that it records only the grammars that "
        "actually parsed in this build (DN-6)"
    )
