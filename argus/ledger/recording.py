"""Frozen first-class recording schema — the row the verdict folds over.

Drivers: ArgusAgent-FR-5 (fixed-enum coverage ledger / recording substrate), ArgusAgent-FR-13
(locator-or-reject — model-layer support), ArgusAgent-NFR-D2 (deterministic,
zero-LLM-token construction), ArgusAgent-NFR-M2 (frozen, additive-only contracts),
AR8 (pure — no I/O, no clock, no LLM, no random/uuid), AR10 (typed failure).

Why this module exists
----------------------
The release-readiness verdict is a PURE FOLD over recordings. If a recording
omits a field the verdict (or precision-replay, or the memo cache key) later
needs, you are forced to re-run an LLM — so the recording schema is frozen as
aggressively as the verdict schema (architecture Decision C / cross-cutting #1):
``frozen=True, extra="forbid"``, additive-only evolution. Every field a
downstream consumer reads is reserved at birth.

Contract decisions locked here (frozen for all downstream stories)
------------------------------------------------------------------
- A ``Recording`` MUST carry ≥1 verifiable ``Locator``. FR13's "rejected, not
  emitted" is enforced at the DATA layer: an empty ``locators`` tuple raises
  :class:`RecordingValidationError` (an ArgusAgent-typed ``ValueError`` subclass,
  mirroring ``CanonicalSerializationError``) — no silent default/empty locator
  is accepted. The detector-side emission policy is Story 1.5.
- ``Locator`` enforces ``start_line <= end_line`` and ``line >= 1`` so a
  malformed span cannot be minted.
- No ``float`` anywhere (the Story 1.1 serializer rejects ``float``); line
  numbers are ``int``.
- ``advisory: bool`` (cross-cutting #6 advisory-by-contract), ``rule_id`` /
  ``cartridge_id`` provenance, the supported depth/claim the verdict folds, and
  a coverage-envelope-slice reference are all reserved now.
- This is the FROZEN ledger row. The LLM-call DTO (``LLMRecording``) + dispatch
  port are a separate later concern (Epic 6, Story 6.1) — kept out of this pure
  module.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from argus.ledger.coverage_ledger import CoverageDepth

__all__ = [
    "RECORDING_SCHEMA_VERSION",
    "RecordingValidationError",
    "Locator",
    "Recording",
]

# Single localized source for this contract's schema version (additive-only;
# part of the hashed payload — a bump deliberately changes the content hash).
RECORDING_SCHEMA_VERSION = "1"

_DEFAULT_PARTITION_ID = "root"


class RecordingValidationError(ValueError):
    """Raised when a :class:`Recording` cannot be minted (AR10 typed failure).

    A ``ValueError`` subclass (mirroring ``store.canonical.CanonicalSerializationError``)
    — the typed failure for the FR13 locator-or-reject rule at the data layer.
    """


class Locator(BaseModel):
    """A verifiable code locator: file + 1-based inclusive line span (frozen).

    ``ast_span`` reserves an optional AST-node span reference for AST-grounded
    detectors (Story 6.2) without a later schema change (NFR-M2 additive-only).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="File the recording refers to.")
    start_line: int = Field(..., ge=1, description="1-based inclusive start line (>= 1).")
    end_line: int = Field(..., ge=1, description="1-based inclusive end line (>= start_line).")
    ast_span: str | None = Field(
        default=None, description="Reserved optional AST-node span reference (Story 6.2)."
    )

    @field_validator("end_line")
    @classmethod
    def _end_not_before_start(cls, end_line: int, info: ValidationInfo) -> int:
        start_line = info.data.get("start_line")
        if start_line is not None and end_line < start_line:
            raise ValueError(
                f"end_line ({end_line}) must be >= start_line ({start_line})"
            )
        return end_line


class Recording(BaseModel):
    """Frozen first-class recording — the row the verdict folds over (FR5/M2).

    ``frozen=True, extra="forbid"`` (Story 1.1 ``Envelope`` precedent): an unknown
    field on read-back is a typed ``ValidationError``. Reserves every field a
    downstream verdict/precision consumer reads. Builds with zero LLM tokens and
    performs no I/O / clock read (AR8 pure); evolution is additive-only.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=RECORDING_SCHEMA_VERSION, description="Recording schema version (part of the hash)."
    )
    recording_id: str = Field(
        ..., description="Stable content-derived recording/finding id (a.k.a. finding_id)."
    )
    partition_id: str = Field(
        default=_DEFAULT_PARTITION_ID, description="Reserved audit-partition id ('root' in V1)."
    )
    rule_id: str = Field(..., description="Detector rule provenance id.")
    cartridge_id: str | None = Field(
        default=None, description="Defect-cartridge provenance id (optional)."
    )
    advisory: bool = Field(
        ..., description="Advisory-by-contract flag (cross-cutting #6); advisory never blocks."
    )
    depth_supported: CoverageDepth | None = Field(
        default=None, description="The coverage depth this recording supports (verdict fold input)."
    )
    claim_present: bool = Field(
        default=False, description="Whether this recording carries an emitted claim (FR6)."
    )
    locators: tuple[Locator, ...] = Field(
        ..., description="≥1 verifiable locator (FR13 locator-or-reject at the data layer)."
    )
    coverage_envelope_slice: str | None = Field(
        default=None, description="Reference to the coverage-envelope slice this recording falls in."
    )

    @field_validator("locators")
    @classmethod
    def _require_at_least_one_locator(cls, locators: tuple[Locator, ...]) -> tuple[Locator, ...]:
        if len(locators) == 0:
            raise RecordingValidationError(
                "a Recording requires >= 1 verifiable locator (FR13 locator-or-reject); "
                "an empty/absent locator is rejected, not emitted"
            )
        return locators

    @property
    def finding_id(self) -> str:
        """Alias for ``recording_id`` (the finding/recording id are the same row)."""
        return self.recording_id
