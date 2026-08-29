"""Unit test matrix for extended multi-language AST parsers (Story 20.1).

Drivers: ArgusAgent-AC-20.1 (BaseASTParser, TSParser, GoParser, JavaParser),
AR8 (frozen pure result contracts, extra="forbid"), AR10 (graceful fault tolerance).
"""

from __future__ import annotations

import importlib.metadata


import pytest
from pydantic import ValidationError

from argus.parsers import (
    ASTNodeSummary,
    BaseASTParser,
    GoParser,
    JavaParser,
    ParserErrorNode,
    ParseResult,
    TSParser,
)
from argus.shared.grammar_status import (
    CANARY_BY_ENTRY_POINT,
    core_version_is_supported,
    parse_version_tuple,
)



def test_pure_data_contracts_immutability() -> None:
    """Verify ParserErrorNode, ASTNodeSummary, and ParseResult are frozen and forbid extra fields."""
    err_node = ParserErrorNode(
        line=5,
        column=10,
        node_type="ERROR",
        unexpected_text="invalid_tok",
    )
    assert err_node.line == 5
    assert err_node.column == 10
    assert err_node.node_type == "ERROR"
    assert err_node.unexpected_text == "invalid_tok"

    # Frozen check
    with pytest.raises(ValidationError):
        err_node.line = 10  # type: ignore[misc]

    # Extra forbid check
    with pytest.raises(ValidationError):
        ParserErrorNode(
            line=1,
            column=1,
            node_type="ERROR",
            unexpected_text="x",
            unknown_field=123,  # type: ignore[call-arg]
        )

    summary = ASTNodeSummary(
        type="program",
        start_line=1,
        end_line=10,
        start_col=1,
        end_col=5,
        children_count=3,
    )
    assert summary.type == "program"
    assert summary.children_count == 3

    with pytest.raises(ValidationError):
        summary.start_line = 2  # type: ignore[misc]

    result = ParseResult(
        file_path="src/index.ts",
        language="typescript",
        ast_eligible=True,
        has_errors=False,
        root_node=summary,
        error_nodes=(),
        definitions=(("function", "main"),),
        edges=("log",),
    )
    assert result.file_path == "src/index.ts"
    assert result.ast_eligible is True
    assert result.has_errors is False

    with pytest.raises(ValidationError):
        result.ast_eligible = False  # type: ignore[misc]


def test_tsparser_clean_ts_and_tsx() -> None:
    """Test TSParser correctly parses TypeScript and TSX code snippets."""
    parser = TSParser()
    assert parser.supports_language("typescript") is True
    assert parser.supports_language("ts") is True
    assert parser.supports_language("tsx") is True
    assert parser.supports_language("javascript") is True
    assert parser.supports_language("python") is False

    # TypeScript snippet
    ts_code = """
    function greet(name: string): string {
        return "Hello " + name;
    }
    """
    res_ts = parser.parse_source(ts_code, file_path="app.ts")
    assert res_ts.ast_eligible is True
    assert res_ts.has_errors is False
    assert res_ts.language == "typescript"
    assert ("function", "greet") in res_ts.definitions

    # TSX snippet
    tsx_code = """
    function Component(props: { title: string }) {
        return <h1>{props.title}</h1>;
    }
    """
    res_tsx = parser.parse_source(tsx_code, file_path="Component.tsx")
    assert res_tsx.ast_eligible is True
    assert res_tsx.has_errors is False
    assert ("function", "Component") in res_tsx.definitions


def test_goparser_clean_go() -> None:
    """Test GoParser correctly parses Go code snippets."""
    parser = GoParser()
    assert parser.supports_language("go") is True
    assert parser.supports_language("java") is False

    go_code = """
    package main

    import "fmt"

    func ComputeSum(a int, b int) int {
        fmt.Println(a)
        return a + b
    }
    """
    res = parser.parse_source(go_code, file_path="main.go")
    assert res.ast_eligible is True
    assert res.has_errors is False
    assert res.language == "go"
    assert ("function", "ComputeSum") in res.definitions


def test_javaparser_clean_java() -> None:
    """Test JavaParser correctly parses Java code snippets."""
    parser = JavaParser()
    assert parser.supports_language("java") is True

    java_code = """
    public class Calculator {
        public int add(int x, int y) {
            return x + y;
        }
    }
    """
    res = parser.parse_source(java_code, file_path="Calculator.java")
    assert res.ast_eligible is True
    assert res.has_errors is False
    assert res.language == "java"
    assert ("class", "Calculator") in res.definitions or ("function", "add") in res.definitions


def test_syntax_error_recovery_without_panic() -> None:
    """Test partial syntax error recovery across all three parsers without panic."""
    ts_parser = TSParser()
    go_parser = GoParser()
    java_parser = JavaParser()

    # Malformed TypeScript snippet
    bad_ts = "function broken(a: { return a + ;"
    res_ts = ts_parser.parse_source(bad_ts, file_path="bad.ts")
    assert res_ts.has_errors is True
    assert len(res_ts.error_nodes) > 0

    # Malformed Go snippet
    bad_go = "package main; func broken( { return"
    res_go = go_parser.parse_source(bad_go, file_path="bad.go")
    assert res_go.has_errors is True
    assert len(res_go.error_nodes) > 0

    # Malformed Java snippet
    bad_java = "public class Bad { public void foo(int x {"
    res_java = java_parser.parse_source(bad_java, file_path="Bad.java")
    assert res_java.has_errors is True
    assert len(res_java.error_nodes) > 0


def test_canary_alignment_and_version_compatibility() -> None:
    """Test tree-sitter core version bounds and canary alignment for extended parsers."""
    # Core version check
    ts_ver = importlib.metadata.version("tree-sitter")
    v_tuple = parse_version_tuple(ts_ver)
    assert core_version_is_supported(v_tuple) is True

    # TS Canary alignment
    ts_canary = CANARY_BY_ENTRY_POINT[("typescript", "language_typescript")]
    ts_res = TSParser().parse_source(ts_canary.source)
    assert ts_res.has_errors is False
    assert set(ts_res.definitions) == set(ts_canary.definitions)
    assert set(ts_res.edges) == set(ts_canary.edges)

    # Go Canary alignment
    go_canary = CANARY_BY_ENTRY_POINT[("go", "language")]
    go_res = GoParser().parse_source(go_canary.source)
    assert go_res.has_errors is False
    assert set(go_res.definitions) == set(go_canary.definitions)
    assert set(go_res.edges) == set(go_canary.edges)

    # Java Canary alignment
    java_canary = CANARY_BY_ENTRY_POINT[("java", "language")]
    java_res = JavaParser().parse_source(java_canary.source)
    assert java_res.has_errors is False
    assert set(java_res.definitions) == set(java_canary.definitions)
    assert set(java_res.edges) == set(java_canary.edges)


