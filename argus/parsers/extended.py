"""Extended multi-language AST parser adapters for TypeScript, Go, and Java (Story 20.1).

Drivers: ArgusAgent-AR8 (PURE result contracts, frozen models),
AR10 (fault-tolerant, graceful degraded outcomes, zero uncaught crashes).
"""

from __future__ import annotations

import importlib
from typing import Any

from argus.parsers.base import (
    ASTNodeSummary,
    BaseASTParser,
    ParserErrorNode,
    ParseResult,
)

__all__ = [
    "TSParser",
    "GoParser",
    "JavaParser",
]

_DEF_KINDS: dict[str, str] = {
    "function_declaration": "function",
    "function_definition": "function",
    "method_declaration": "function",
    "method_definition": "function",
    "class_declaration": "class",
    "class_definition": "class",
    "interface_declaration": "interface",
    "struct_type": "struct",
    "type_alias_declaration": "type",
}

_CALL_NODE_TYPES: set[str] = {
    "call_expression",
    "call",
    "function_call_expression",
    "method_invocation",
}


def _extract_node_summary(root_node: Any) -> ASTNodeSummary | None:
    if root_node is None:
        return None
    try:
        start_pt = getattr(root_node, "start_point", (0, 0))
        end_pt = getattr(root_node, "end_point", (0, 0))
        children = getattr(root_node, "children", [])
        return ASTNodeSummary(
            type=str(getattr(root_node, "type", "root")),
            start_line=start_pt[0] + 1,
            end_line=end_pt[0] + 1,
            start_col=start_pt[1] + 1,
            end_col=end_pt[1] + 1,
            children_count=len(children),
        )
    except Exception:
        return None


def _traverse_ast(
    root_node: Any,
) -> tuple[tuple[ParserErrorNode, ...], tuple[tuple[str, str], ...], tuple[str, ...]]:
    if root_node is None:
        return (), (), ()

    error_nodes: list[ParserErrorNode] = []
    definitions: list[tuple[str, str]] = []
    edges: list[str] = []

    stack: list[Any] = [root_node]
    while stack:
        node = stack.pop()
        ntype = str(getattr(node, "type", ""))
        is_missing = bool(getattr(node, "is_missing", False))

        if ntype == "ERROR" or is_missing or ntype == "MISSING":
            start_pt = getattr(node, "start_point", (0, 0))
            text_bytes = getattr(node, "text", b"")
            if isinstance(text_bytes, bytes):
                text_str = text_bytes.decode("utf-8", errors="replace")
            else:
                text_str = str(text_bytes)
            error_nodes.append(
                ParserErrorNode(
                    line=start_pt[0] + 1,
                    column=start_pt[1] + 1,
                    node_type="MISSING" if is_missing else ntype,
                    unexpected_text=text_str[:100],
                )
            )

        kind = _DEF_KINDS.get(ntype)
        if kind is not None:
            name_node = None
            if hasattr(node, "child_by_field_name"):
                name_node = node.child_by_field_name("name")
            if name_node is not None and hasattr(name_node, "text") and name_node.text:
                n_text = name_node.text
                n_str = n_text.decode("utf-8", errors="replace") if isinstance(n_text, bytes) else str(n_text)
                definitions.append((kind, n_str))

        if ntype in _CALL_NODE_TYPES:
            fn_node = None
            if hasattr(node, "child_by_field_name"):
                fn_node = node.child_by_field_name("function") or node.child_by_field_name("name")
            if fn_node is not None and hasattr(fn_node, "text") and fn_node.text:
                f_text = fn_node.text
                f_str = f_text.decode("utf-8", errors="replace") if isinstance(f_text, bytes) else str(f_text)
                callee_name = f_str.split(".")[-1]
                edges.append(callee_name)

        children = getattr(node, "children", [])
        stack.extend(children)

    sorted_errors = tuple(sorted(error_nodes, key=lambda e: (e.line, e.column, e.node_type)))
    sorted_defs = tuple(sorted(set(definitions), key=lambda d: (d[0], d[1])))
    sorted_edges = tuple(sorted(set(edges)))

    return sorted_errors, sorted_defs, sorted_edges


class TSParser(BaseASTParser):
    """Tree-sitter AST parser adapter for TypeScript (.ts, .tsx) and JavaScript (.js, .jsx)."""

    def supports_language(self, language: str) -> bool:
        return language.lower() in ("typescript", "ts", "tsx", "javascript", "js", "jsx")

    def parse_source(self, code: str | bytes, file_path: str = "") -> ParseResult:
        lang_str = "typescript"
        code_bytes = code.encode("utf-8") if isinstance(code, str) else code
        try:
            tree_sitter = importlib.import_module("tree_sitter")
            ts_mod = importlib.import_module("tree_sitter_typescript")

            is_tsx = file_path.endswith((".tsx", ".jsx"))
            entry_point = "language_tsx" if is_tsx else "language_typescript"
            lang_fn = getattr(ts_mod, entry_point)
            language_obj = tree_sitter.Language(lang_fn())
            parser = tree_sitter.Parser(language_obj)

            tree = parser.parse(code_bytes)
            root = tree.root_node
            summary = _extract_node_summary(root)
            error_nodes, defs, edges = _traverse_ast(root)
            has_errors = bool(getattr(root, "has_error", False)) or len(error_nodes) > 0

            return ParseResult(
                file_path=file_path,
                language=lang_str,
                ast_eligible=True,
                has_errors=has_errors,
                root_node=summary,
                error_nodes=error_nodes,
                definitions=defs,
                edges=edges,
            )
        except Exception:
            return ParseResult(
                file_path=file_path,
                language=lang_str,
                ast_eligible=False,
                has_errors=True,
                root_node=None,
                error_nodes=(
                    ParserErrorNode(
                        line=1,
                        column=1,
                        node_type="ERROR",
                        unexpected_text="tree-sitter-typescript load or execution failed",
                    ),
                ),
                definitions=(),
                edges=(),
            )


class GoParser(BaseASTParser):
    """Tree-sitter AST parser adapter for Go (.go)."""

    def supports_language(self, language: str) -> bool:
        return language.lower() in ("go", "golang")

    def parse_source(self, code: str | bytes, file_path: str = "") -> ParseResult:
        lang_str = "go"
        code_bytes = code.encode("utf-8") if isinstance(code, str) else code
        try:
            tree_sitter = importlib.import_module("tree_sitter")
            go_mod = importlib.import_module("tree_sitter_go")

            lang_fn = getattr(go_mod, "language")
            language_obj = tree_sitter.Language(lang_fn())
            parser = tree_sitter.Parser(language_obj)

            tree = parser.parse(code_bytes)
            root = tree.root_node
            summary = _extract_node_summary(root)
            error_nodes, defs, edges = _traverse_ast(root)
            has_errors = bool(getattr(root, "has_error", False)) or len(error_nodes) > 0

            return ParseResult(
                file_path=file_path,
                language=lang_str,
                ast_eligible=True,
                has_errors=has_errors,
                root_node=summary,
                error_nodes=error_nodes,
                definitions=defs,
                edges=edges,
            )
        except Exception:
            return ParseResult(
                file_path=file_path,
                language=lang_str,
                ast_eligible=False,
                has_errors=True,
                root_node=None,
                error_nodes=(
                    ParserErrorNode(
                        line=1,
                        column=1,
                        node_type="ERROR",
                        unexpected_text="tree-sitter-go load or execution failed",
                    ),
                ),
                definitions=(),
                edges=(),
            )


class JavaParser(BaseASTParser):
    """Tree-sitter AST parser adapter for Java (.java)."""

    def supports_language(self, language: str) -> bool:
        return language.lower() == "java"

    def parse_source(self, code: str | bytes, file_path: str = "") -> ParseResult:
        lang_str = "java"
        code_bytes = code.encode("utf-8") if isinstance(code, str) else code
        try:
            tree_sitter = importlib.import_module("tree_sitter")
            java_mod = importlib.import_module("tree_sitter_java")

            lang_fn = getattr(java_mod, "language")
            language_obj = tree_sitter.Language(lang_fn())
            parser = tree_sitter.Parser(language_obj)

            tree = parser.parse(code_bytes)
            root = tree.root_node
            summary = _extract_node_summary(root)
            error_nodes, defs, edges = _traverse_ast(root)
            has_errors = bool(getattr(root, "has_error", False)) or len(error_nodes) > 0

            return ParseResult(
                file_path=file_path,
                language=lang_str,
                ast_eligible=True,
                has_errors=has_errors,
                root_node=summary,
                error_nodes=error_nodes,
                definitions=defs,
                edges=edges,
            )
        except Exception:
            return ParseResult(
                file_path=file_path,
                language=lang_str,
                ast_eligible=False,
                has_errors=True,
                root_node=None,
                error_nodes=(
                    ParserErrorNode(
                        line=1,
                        column=1,
                        node_type="ERROR",
                        unexpected_text="tree-sitter-java load or execution failed",
                    ),
                ),
                definitions=(),
                edges=(),
            )
