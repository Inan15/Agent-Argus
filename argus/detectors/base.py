"""Detector ``Protocol`` + the locator-required ``Recording`` finding builder (PURE).

Drivers: ArgusAgent-FR-13 (every finding carries ≥1 verifiable locator or is rejected,
not emitted), ArgusAgent-FR-33-support / cross-cutting #6 (advisory-by-contract: the
finding carries the eligibility signal a downstream verdict gate (Story 1.6)
reads so a heuristic-only finding can never move the verdict to 🔴 on its own),
AR8 (PURE — the builder performs no I/O, no clock, no ``uuid4``/``random``, no
LLM), AR10 (typed failure — a locator-less finding is rejected via a typed error,
never minted; no bare ``except: pass``, no ``print()``).

Why this module exists
----------------------
Every ArgusAgent detector emits the SAME finding row — the Story 1.2 ``Recording`` —
and the SAME locator-or-reject discipline (FR13). This module owns that single
builder so a detector never reimplements finding construction or a parallel
finding model (§3.3 reuse-canonical). The ``Recording`` / ``Locator`` models are
reused VERBATIM; this module does NOT modify ``ledger/recording.py``.

Contract decisions locked here (frozen for downstream detectors)
----------------------------------------------------------------
- The detector ``Protocol`` is a ``typing.Protocol`` (``run(...) -> DetectorResult``).
  A concrete detector (Story 1.5 ``vacuous_test``) satisfies it structurally — no
  inheritance required.
- ``DetectorResult`` is a frozen ``extra="forbid"`` pure model (the Story 1.1/1.2
  precedent): the per-file ``CoverageLedgerEntry`` candidates the detector graded
  via ``grade_entry``, the ``Recording`` findings, and the per-file DEGRADED
  conditions (AR10) the Story 1.7 pipeline folds. The detector does NOT assemble
  the whole ``CoverageLedger`` (that aggregation is the pipeline's job).
- The finding builder ``build_recording`` mints a 1.2 ``Recording`` from a
  ``FindingDraft``. The FR13 locator-or-reject rule is enforced at the DATA layer
  (the ``Recording`` raises ``RecordingValidationError`` on an empty ``locators``
  tuple); the builder SURFACES that — it never silently mints a locator-less
  finding and never swallows the rejection.
- The recording id is CONTENT-DERIVED (a sha256 over the canonical draft payload
  via the single Story 1.1 serializer) — NEVER ``uuid4`` / a counter / arrival
  order (AR4/AR11). Two hosts that flag the same finding mint the same id.
"""

from __future__ import annotations

import hashlib
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from argus.ledger.coverage_ledger import CoverageLedgerEntry
from argus.ledger.recording import (
    Locator,
    Recording,
    RecordingValidationError,
)
from argus.store import canonical

__all__ = [
    "FindingDraft",
    "DegradedCondition",
    "DetectorResult",
    "Detector",
    "build_recording",
]


class FindingDraft(BaseModel):
    """A pre-validation finding description the builder turns into a ``Recording``.

    Frozen ``extra="forbid"`` (the Story 1.1/1.2 precedent). Carries the inputs
    the FR13 builder needs: the file + 1-based line span, an optional 1.4
    ``Definition.ast_span`` token, the ``rule_id`` provenance, the
    advisory-by-contract flag, the supported coverage depth (the verdict-fold
    input), and the evidence the finding carries WITH it (FR10 "carrying their
    evidence counts" — a JSON-primitive dict of fixed-precision/int leaves).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="File the finding refers to.")
    start_line: int = Field(..., ge=1, description="1-based inclusive start line (>= 1).")
    end_line: int = Field(..., ge=1, description="1-based inclusive end line (>= start_line).")
    ast_span: str | None = Field(
        default=None, description="Optional 1.4 Definition.ast_span token for Locator.ast_span."
    )
    rule_id: str = Field(..., description="Detector rule provenance id.")
    advisory: bool = Field(..., description="Advisory-by-contract flag (cross-cutting #6).")
    cartridge_id: str | None = Field(default=None, description="Optional defect-cartridge id.")
    coverage_envelope_slice: str | None = Field(
        default=None, description="Reference to the coverage-envelope slice this finding falls in."
    )


class DegradedCondition(BaseModel):
    """A per-file degraded outcome (AR10) — recorded, never a false flag / crash.

    An un-parseable / un-analyzable / non-test file routes here instead of being
    flagged vacuous. A later story (1.7) MAY mint a ``parse_failure``-style finding
    or a coverage downgrade from it; this V1 detector only RECORDS the condition.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="File whose analysis degraded.")
    reason: str = Field(..., description="Degradation reason token (e.g. 'parse_failed').")


class DetectorResult(BaseModel):
    """The frozen pure result the Story 1.7 pipeline folds (AR8).

    ``entries`` are per-file ``CoverageLedgerEntry`` candidates the detector graded
    via ``grade_entry`` (the detector does NOT assemble the whole ``CoverageLedger``).
    ``findings`` are the 1.2 ``Recording`` rows. ``degraded`` are the AR10 recorded
    conditions. All tuples (deterministic, no set/dict-order reliance).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    entries: tuple[CoverageLedgerEntry, ...] = Field(
        default=(), description="Per-file coverage entries (graded via grade_entry)."
    )
    findings: tuple[Recording, ...] = Field(
        default=(), description="The 1.2 Recording findings emitted (each carries >=1 locator)."
    )
    degraded: tuple[DegradedCondition, ...] = Field(
        default=(), description="Per-file degraded conditions (AR10 recorded, not flagged)."
    )


@runtime_checkable
class Detector(Protocol):
    """The detector contract — a pure ``run`` producing a :class:`DetectorResult`.

    A concrete detector satisfies this structurally (``typing.Protocol``); no
    base-class inheritance is required. ``run`` MUST be pure (AR8): a function over
    recorded inputs (test source text + the Story 1.4 ``AstIndexEntry``), no I/O,
    no clock, no LLM, no ``uuid4``/``random``.
    """

    rule_id: str

    def run(self, *args: object, **kwargs: object) -> DetectorResult:  # pragma: no cover - protocol
        ...


def _recording_id(draft: FindingDraft) -> str:
    """Content-derived recording id: sha256 over the canonical draft (AR4/AR11).

    Uses the single Story 1.1 serializer so the id is byte-stable across hosts —
    NEVER ``uuid4`` / a counter / arrival order. The id covers the locating
    identity (file/span/rule/ast_span/advisory) so two distinct findings on the
    same file get distinct ids while a re-flag of the same finding is stable.
    """
    identity = {
        "file_path": draft.file_path,
        "start_line": draft.start_line,
        "end_line": draft.end_line,
        "ast_span": draft.ast_span,
        "rule_id": draft.rule_id,
        "advisory": draft.advisory,
        "cartridge_id": draft.cartridge_id,
    }
    digest = hashlib.sha256(canonical.dumps_bytes(identity)).hexdigest()
    return f"{draft.rule_id}:{digest}"


def build_recording(
    draft: FindingDraft,
    *,
    depth_supported: object | None = None,
    claim_present: bool = False,
) -> Recording:
    """Mint a 1.2 ``Recording`` from a ``FindingDraft`` (FR13 locator-or-reject).

    Builds exactly ONE verifiable ``Locator`` from the draft's file + line span +
    optional ``ast_span`` and reuses the 1.2 ``Recording`` VERBATIM. The
    locator-or-reject rule is enforced at the DATA layer — the ``Recording`` raises
    :class:`RecordingValidationError` on an empty ``locators`` tuple; this builder
    surfaces that (it constructs the locator first and would raise rather than mint
    a locator-less finding). PURE — no I/O, no clock, no LLM, no ``uuid4``.

    Raises:
        RecordingValidationError: if a verifiable locator cannot be supplied
            (FR13 — rejected, not emitted), or the line span is malformed.
    """
    try:
        locator = Locator(
            file_path=draft.file_path,
            start_line=draft.start_line,
            end_line=draft.end_line,
            ast_span=draft.ast_span,
        )
    except ValueError as exc:
        raise RecordingValidationError(
            f"cannot build a verifiable locator for a {draft.rule_id} finding "
            f"on '{draft.file_path}': {exc} (FR13 locator-or-reject)"
        ) from exc

    return Recording(
        recording_id=_recording_id(draft),
        rule_id=draft.rule_id,
        cartridge_id=draft.cartridge_id,
        advisory=draft.advisory,
        depth_supported=depth_supported,  # type: ignore[arg-type]
        claim_present=claim_present,
        locators=(locator,),
        coverage_envelope_slice=draft.coverage_envelope_slice,
    )
