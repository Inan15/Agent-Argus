"""Base interface and PURE result contracts for multi-language AST parsers (Story 20.1).

Drivers: ArgusAgent-AR8 (PURE contracts — frozen BaseModel with extra="forbid"),
AR10 (graceful degraded outcomes, no uncaught exceptions).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "ParserErrorNode",
    "ASTNodeSummary",
    "ParseResult",
    "BaseASTParser",
]


class ParserErrorNode(BaseModel):
    """Details of a partial syntax error recovery node in the AST."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    line: int = Field(..., description="1-based line number of error")
    column: int = Field(..., description="1-based column number of error")
    node_type: str = Field(..., description="Tree-sitter node type (e.g. ERROR or MISSING)")
    unexpected_text: str = Field("", description="Unexpected code text snippet")


class ASTNodeSummary(BaseModel):
    """Summary of an AST node hierarchy element."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: str = Field(..., description="Tree-sitter AST node type")
    start_line: int = Field(..., description="1-based start line")
    end_line: int = Field(..., description="1-based end line")
    start_col: int = Field(..., description="1-based start column")
    end_col: int = Field(..., description="1-based end column")
    children_count: int = Field(0, description="Number of direct child nodes")


class ParseResult(BaseModel):
    """PURE result contract emitted by all BaseASTParser implementations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field("", description="Relative file path of parsed source")
    language: str = Field(..., description="Language identifier")
    ast_eligible: bool = Field(True, description="Whether AST was parsed successfully")
    has_errors: bool = Field(False, description="Whether syntax errors were encountered")
    root_node: ASTNodeSummary | None = Field(None, description="Summary of root AST node")
    error_nodes: tuple[ParserErrorNode, ...] = Field((), description="Recovered error nodes")
    definitions: tuple[tuple[str, str], ...] = Field((), description="Extracted (kind, name) definitions")
    edges: tuple[str, ...] = Field((), description="Extracted callee edges")


class BaseASTParser(ABC):
    """Abstract Base Class for multi-language AST parsers."""

    @abstractmethod
    def parse_source(self, code: str | bytes, file_path: str = "") -> ParseResult:
        """Parse source code into a ParseResult (thread-safe and stateless)."""

    @abstractmethod
    def supports_language(self, language: str) -> bool:
        """Return True if this parser supports the specified language."""
