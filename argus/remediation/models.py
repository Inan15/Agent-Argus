"""Data contracts for defect remediation patches and execution results (PURE).

Drivers: Story 20.2 (Defect Remediation Engine), NFR-S1 (workspace path containment),
AR8 (pure data models), AR10 (typed failure).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator

__all__ = [
    "RemediationPatch",
    "RemediationResult",
]


class RemediationPatch(BaseModel):
    """Frozen pure Pydantic model representing a unified diff remediation patch (AC1).

    Enforces relative POSIX path containment (NFR-S1) on ``target_file``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    finding_id: str = Field(
        ..., description="ID of the finding/recording being remediated."
    )
    target_file: str = Field(
        ..., description="Relative POSIX path to target file within workspace containment."
    )
    diff_content: str = Field(
        ..., description="Unified diff patch content string."
    )
    affected_lines: tuple[int, ...] = Field(
        ..., description="Line numbers in the original file affected by the patch."
    )
    patch_id: str = Field(
        ..., description="Unique/stable patch identification string."
    )
    created_at: str = Field(
        ..., description="Timestamp of patch creation in ISO 8601 format."
    )

    @field_validator("target_file")
    @classmethod
    def _validate_target_file(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("target_file cannot be empty")
        if "\\" in v:
            raise ValueError(
                f"target_file '{v}' must be a relative POSIX path with forward slashes ('/')"
            )
        if v.startswith("/") or v.startswith("\\") or ":" in v:
            raise ValueError(f"target_file '{v}' must be a relative path, not an absolute path")
        p = Path(v)
        if p.is_absolute():
            raise ValueError(f"target_file '{v}' must be a relative path, not an absolute path")
        if ".." in p.parts:
            raise ValueError(
                f"target_file '{v}' contains relative path traversal ('..') escaping containment"
            )
        return v


class RemediationResult(BaseModel):
    """Frozen pure Pydantic model representing the result of remediation processing (AC1)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    patches: tuple[RemediationPatch, ...] = Field(
        default=(), description="Remediation patches generated or processed."
    )
    success: bool = Field(
        ..., description="True iff remediation process completed without unhandled errors."
    )
    dry_run_verified: bool = Field(
        ..., description="True iff all patches passed dry-run AST verification."
    )
    applied_count: int = Field(
        default=0, ge=0, description="Number of patches successfully applied to disk."
    )
    errors: tuple[str, ...] = Field(
        default=(), description="Recorded error messages during remediation processing."
    )
