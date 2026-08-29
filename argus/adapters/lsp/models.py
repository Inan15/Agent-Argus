"""PURE Pydantic data contracts for LSP 3.17 diagnostics & JSON-RPC 2.0 (Story 20.3).

Drivers: ArgusAgent-FR-39 (IDE & LSP diagnostic surface), ArgusAgent-NFR-M2
(frozen, additive-only contracts), AR8 (PURE models, zero I/O).

Why this module exists
----------------------
Defines frozen Pydantic data structures for Language Server Protocol (LSP 3.17)
diagnostic notifications (`textDocument/publishDiagnostics`) over JSON-RPC 2.0.
Every model enforces ``model_config = ConfigDict(frozen=True, extra="forbid")``
to preserve immutability and schema integrity.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "LSPPosition",
    "LSPRange",
    "LSPDiagnosticSeverity",
    "LSPLocation",
    "LSPDiagnosticRelatedInformation",
    "LSPDiagnostic",
    "PublishDiagnosticsParams",
    "JSONRPCNotification",
]


class LSPDiagnosticSeverity(IntEnum):
    """LSP 3.17 Diagnostic Severity levels (1=Error, 2=Warning, 3=Info, 4=Hint)."""

    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4


class LSPPosition(BaseModel):
    """0-based position in a text document (LSP 3.17 contract)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    line: int = Field(..., ge=0, description="0-based line number.")
    character: int = Field(..., ge=0, description="0-based character offset.")


class LSPRange(BaseModel):
    """Range in a text document expressed as start and end positions (LSP 3.17 contract)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    start: LSPPosition = Field(..., description="Start position (inclusive).")
    end: LSPPosition = Field(..., description="End position.")


class LSPLocation(BaseModel):
    """Location in a document (URI + Range) for diagnostic related information."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    uri: str = Field(..., description="Target document URI.")
    range: LSPRange = Field(..., description="Range within the target document.")


class LSPDiagnosticRelatedInformation(BaseModel):
    """Secondary location / evidence annotation for an LSP diagnostic."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    location: LSPLocation = Field(..., description="Location of related information.")
    message: str = Field(..., description="Explanation of related information.")


class LSPDiagnostic(BaseModel):
    """An LSP 3.17 textDocument/publishDiagnostics item."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    range: LSPRange = Field(..., description="Diagnostic text range.")
    severity: LSPDiagnosticSeverity = Field(..., description="Diagnostic severity level (1..4).")
    code: str | int | None = Field(default=None, description="Diagnostic code or rule ID.")
    source: str = Field(default="ArgusAgent", description="Diagnostic source provider.")
    message: str = Field(..., description="Human-readable diagnostic message.")
    relatedInformation: list[LSPDiagnosticRelatedInformation] | None = Field(
        default=None, description="Optional related diagnostic locations."
    )


class PublishDiagnosticsParams(BaseModel):
    """Params object for textDocument/publishDiagnostics notification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    uri: str = Field(..., description="URI of the document diagnostics apply to.")
    diagnostics: list[LSPDiagnostic] = Field(..., description="List of diagnostics for the URI.")
    version: int | None = Field(default=None, description="Optional document version integer.")


class JSONRPCNotification(BaseModel):
    """Standard JSON-RPC 2.0 notification payload for publishDiagnostics."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    jsonrpc: Literal["2.0"] = Field(default="2.0", description="JSON-RPC protocol version.")
    method: str = Field(default="textDocument/publishDiagnostics", description="Notification method.")
    params: PublishDiagnosticsParams = Field(..., description="Diagnostic parameters payload.")
