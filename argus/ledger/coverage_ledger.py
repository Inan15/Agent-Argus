"""Fixed-enum coverage ledger — closed depth states + per-file/aggregate models.

Drivers: ArgusAgent-FR-5 (fixed-enum coverage ledger), ArgusAgent-FR-6 (claim-required
``audited_deep``; silence → ``audited_shallow``), ArgusAgent-NFR-D2 (deterministic,
zero-LLM-token construction), ArgusAgent-NFR-M2 (frozen, additive-only contracts),
AR8 (pure — no I/O, no clock, no LLM, no random/uuid), AR10 (typed failure).

Why this module exists
----------------------
The release-readiness verdict (Story 1.6) is a PURE FOLD over coverage. For the
fold to be a pure function the coverage states must be CLOSED and the per-file
ledger must be complete-at-birth — every field the FR9 readable surface and the
FR6/FR16 gate will later read is reserved here. A missing field would force an
LLM re-run downstream; that is the failure this module's aggressiveness prevents.

Contract decisions locked here (frozen for all downstream stories)
------------------------------------------------------------------
- The coverage-depth enum is CLOSED at exactly five members. A new state is an
  additive ``schema_version`` bump, never an ad-hoc edit — the AC1 membership
  pin in ``tests/argus/test_coverage_ledger.py`` enforces this durably.
- ``CoverageDepth`` is a ``str``-valued enum so members serialize verbatim as
  their ``snake_case`` token through ``store/canonical.dumps`` (a bare
  ``enum.Enum`` member is not JSON-serializable).
- ``audited_deep`` requires an emitted claim. The pure grading constructor
  ``grade_entry`` downgrades a proposed ``AUDITED_DEEP`` to ``AUDITED_SHALLOW``
  when no claim is present (silence → shallow, FR6). V1 records claim *presence*
  only — AST-validating the claim's *truth* is Story 1.5 / 6.2.
- ``CoverageLedger.entries`` is stored as a tuple SORTED by ``file_path`` so two
  ledgers built from the same entries in different orders are equal and
  serialize byte-identically (AR4 / NFR-P1) — no dict/set iteration-order
  reliance.
- No ``float`` anywhere: per-depth counts are ``int``; any future ratio is
  ``Decimal``/``Fraction`` (the Story 1.1 serializer rejects ``float``).
"""

from __future__ import annotations

import enum

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "LEDGER_SCHEMA_VERSION",
    "CoverageDepth",
    "CoverageLedgerEntry",
    "CoverageLedger",
    "grade_entry",
]

# Single localized source for this contract's schema version. An additive
# (new OPTIONAL field) evolution bumps this; it is part of the hashed payload.
LEDGER_SCHEMA_VERSION = "1"

# Reserved partition identifier — always "root" in V1 (repository partitioning
# is Story 2.4). Kept as a field so the partition-aware surface needs no schema
# change later (NFR-M2 additive-only).
_DEFAULT_PARTITION_ID = "root"


class CoverageDepth(str, enum.Enum):
    """Closed, fixed-enum coverage-depth states (ArgusAgent-FR-5).

    The string VALUES are the wire contract — serialized verbatim through
    ``store/canonical.dumps``. Exactly five members; the membership set is pinned
    by a committed test so adding/removing/renaming a state fails the build.
    A genuinely new state is an additive ``schema_version`` bump, never an edit.
    """

    AUDITED_DEEP = "audited_deep"
    AUDITED_SHALLOW = "audited_shallow"
    TOOL_SCANNED_ONLY = "tool_scanned_only"
    INFERRED = "inferred"
    SKIPPED = "skipped"


class CoverageLedgerEntry(BaseModel):
    """A single file's audit outcome (frozen, additive-only — ArgusAgent-FR-5/M2).

    ``frozen=True, extra="forbid"`` mirrors the Story 1.1 ``Envelope`` decision:
    an unknown field on read-back is a typed ``ValidationError``, not silent
    acceptance. Carries every field the FR9 readable surface and the FR6/FR16
    gate will later read.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="Audited file path (the deterministic sort key).")
    depth: CoverageDepth = Field(..., description="Closed-enum coverage depth for this file.")
    claim_present: bool = Field(
        ..., description="Whether an emitted claim accompanies this entry (FR6 keystone)."
    )
    recording_ids: tuple[str, ...] = Field(
        default=(), description="Evidence reference: ids of recordings justifying the depth."
    )
    partition_id: str = Field(
        default=_DEFAULT_PARTITION_ID, description="Reserved audit-partition id ('root' in V1)."
    )


class CoverageLedger(BaseModel):
    """Aggregate per-file coverage ledger for one audit unit (frozen — FR5/M2).

    ``entries`` are stored SORTED by ``file_path`` (deterministic order, AR4) so
    two ledgers built from the same entries in any input order are equal and
    serialize byte-identically (NFR-P1). Exposes a PURE per-depth count accessor
    so the deep-% the verdict gate needs is derivable with zero tokens (NFR-D2).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=LEDGER_SCHEMA_VERSION, description="Ledger schema version (part of the hash)."
    )
    partition_id: str = Field(
        default=_DEFAULT_PARTITION_ID, description="Reserved audit-partition id ('root' in V1)."
    )
    entries: tuple[CoverageLedgerEntry, ...] = Field(
        default=(), description="Per-file entries, canonicalized to file_path-sorted order."
    )

    @classmethod
    def build(
        cls,
        entries: tuple[CoverageLedgerEntry, ...] | list[CoverageLedgerEntry],
        *,
        schema_version: str = LEDGER_SCHEMA_VERSION,
        partition_id: str = _DEFAULT_PARTITION_ID,
    ) -> "CoverageLedger":
        """Construct a ledger with ``entries`` canonicalized to sorted order.

        Sorting by ``file_path`` makes equality and serialization
        insertion-order-independent (AC3 / AR4). Pure — no I/O, no clock.
        """
        ordered = tuple(sorted(entries, key=lambda e: e.file_path))
        return cls(schema_version=schema_version, partition_id=partition_id, entries=ordered)

    def counts_by_depth(self) -> dict[CoverageDepth, int]:
        """Per-depth entry counts — PURE, zero-token (the verdict-gate input).

        Returns a count for EVERY member (zero-filled) so the deep-% is derivable
        without re-deriving the enum membership downstream.
        """
        counts: dict[CoverageDepth, int] = {depth: 0 for depth in CoverageDepth}
        for entry in self.entries:
            counts[entry.depth] += 1
        return counts

    def deep_count(self) -> int:
        """Number of ``audited_deep`` entries (PURE)."""
        return sum(1 for entry in self.entries if entry.depth is CoverageDepth.AUDITED_DEEP)

    def total(self) -> int:
        """Total entry count (PURE)."""
        return len(self.entries)


def grade_entry(
    *,
    file_path: str,
    proposed_depth: CoverageDepth,
    claim_present: bool,
    recording_ids: tuple[str, ...] = (),
    partition_id: str = _DEFAULT_PARTITION_ID,
) -> CoverageLedgerEntry:
    """Grade a per-file entry, downgrading claimless ``audited_deep`` (FR6).

    The honesty keystone: a proposed ``AUDITED_DEEP`` with no accompanying claim
    is recorded as ``AUDITED_SHALLOW`` (silence → shallow). Every other depth is
    recorded unchanged. PURE — no I/O, no clock, no LLM. This records the
    *presence* of a claim only; AST-validating the claim's *truth* is Story 1.5
    (vacuous-path subset) / Story 6.2 (full AST grounding).
    """
    depth = proposed_depth
    if proposed_depth is CoverageDepth.AUDITED_DEEP and not claim_present:
        depth = CoverageDepth.AUDITED_SHALLOW
    return CoverageLedgerEntry(
        file_path=file_path,
        depth=depth,
        claim_present=claim_present,
        recording_ids=recording_ids,
        partition_id=partition_id,
    )
