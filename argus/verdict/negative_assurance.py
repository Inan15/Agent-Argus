"""PURE negative-assurance verdict WRAPPER over the done 1.6/3.3/2.3 records.

Drivers: ArgusAgent-FR-17 (the CENTRAL driver — express every verdict in
negative-assurance terms: a structured ``scope_statement`` ["examined X, sampled
Y, did NOT cover Z"], a ``materiality_bar``, a fixed ``disclaimer``, and a
point-in-time stamp — framed as scope-bounded negative assurance, NEVER
certification / "the code is correct"), ArgusAgent-NFR-A3 (every verdict carries a scope
statement, materiality bar, disclaimer, and point-in-time stamp), ArgusAgent-FR-15 (the
verdict this WRAPS is the pure-function gate result, UNCHANGED — read, never
re-derived), ArgusAgent-FR-18 / AR3 (the exit-code wire contract ``0/2/3/1`` is REUSED,
UNCHANGED), ArgusAgent-FR-16/FR-22 (the floor report this folds over — exhaustion-driven
vs intrinsic narration), ArgusAgent-FR-4 (the critical-subsystem set the scope statement
narrates — which critical subsystems were / were NOT examined deeply),
ArgusAgent-NFR-D2 (deterministic, zero-LLM-token — a pure fold over the EXISTING
``AuditVerdict`` + floor report + critical set), ArgusAgent-NFR-D3 (the content hash
covers the canonical payload ONLY — the point-in-time stamp is the envelope
``created_at``, EXCLUDED from the hash; this module NEVER reads a clock),
ArgusAgent-NFR-P1 (byte-identical wrapper + message across hosts/runs/input-orderings;
no ``float``; a resumed run's wrapper is byte-identical to an uninterrupted run's),
ArgusAgent-NFR-S1 (no source / secret / absolute-host-path bytes — only repo-relative
POSIX paths from the already-sanitized ``CriticalSubsystemSet`` + ``int``/``bool``/
``str`` provenance), ArgusAgent-NFR-A1/M2 (frozen, schema-versioned, additive-only
contract), ArgusAgent-NFR-M1 (≤1200-line files), AR4 (no ``float``; ratios are exact
``Fraction`` REUSED from ``AuditVerdict.deep_ratio``; single canonical serializer;
no clock/uuid/random/iteration-order — content-derived, AR11), AR8 (pure/impure
separation — the wrapper model + builder + render are PURE; the WRITE is the impure
pipeline shell), AR10 (typed failure — :class:`NegativeAssuranceError`, never an
uncaught raise), AR11 (sorted sets; content-derived).

Negative assurance = "absence of *detected* defects within the *assessed* scope"
--------------------------------------------------------------------------------
The keystone framing (FR17/NFR-A3): the wrapper's job is audit-grade humility. A
``RELEASE_READY`` verdict is NEVER framed as "the code is correct" / "certified" /
"passed" / "proven defect-free". It is "no blocking findings **within the assessed
scope**" — honest about what ArgusAgent did NOT establish. The fixed :data:`DISCLAIMER`
constant + the no-over-claim test (AC2 forbidden-phrase scan) mechanize this.

The scope statement triad (AC1/AC3 — assessed-scope honesty)
------------------------------------------------------------
The ``scope_statement`` is STRUCTURED (no prose-only fields), derived purely from
the EXISTING records:

- **examined** — the ``audited_deep`` count (from ``AuditVerdict.counts_by_depth``);
- **sampled** — the ``audited_shallow`` + ``tool_scanned_only`` counts (seen, but
  not deeply assured);
- **NOT covered** — the ``inferred`` + ``skipped`` counts, plus the floor report's
  ``skipped_on_exhaustion_count`` and ``driven_by_exhaustion`` flag. EVERY not-deep
  class (``audited_shallow``, ``tool_scanned_only``, ``inferred``, ``skipped``) is
  recorded as its own ``int`` field so none can be silently dropped (the AC3
  load-bearing clause — a silent omission re-creates the false-positive-assurance
  failure the epic exists to prevent);
- **critical narration** — which critical subsystems were examined deeply vs which
  were NOT (shallow-or-less, or ``designated_but_unmatched``) — from the 2.3
  ``CriticalSubsystemSet`` ``paths`` / ``origins`` / ``designated_but_unmatched``
  cross-referenced against the ledger's deep set.

The point-in-time stamp (NFR-D3 — the determinism landmine)
-----------------------------------------------------------
The stamp is the persisted artifact's envelope ``created_at`` (Story 1.1, already
EXCLUDED from the content hash). This pure builder NEVER reads a clock; the impure
writer sets ``created_at``. Putting a wall-clock timestamp INSIDE the canonical
payload would make the content hash non-reproducible (the AR4 byte-diff landmine).

PURE (AR8): the model + :func:`build_negative_assurance_verdict` + the render
perform NO filesystem I/O, NO clock read, NO ``uuid``/``random``, NO LLM/network,
NO set/dict-iteration-order reliance. The persistence WRITE
(``pipeline._persist_negative_assurance`` / ``_persist_critical_subsystems``) is
the impure shell. Joins the import-isolation ``_MODULES_UNDER_GUARD`` gate.

Test area ArgusAgent-VERDICT (``TC-ArgusAgent-VERDICT-001-NN``) — the new wrapper area, the
first test file in it (the 1.6 gate tests live in ``test_verdict_gate.py``).
"""

from __future__ import annotations

from fractions import Fraction

from pydantic import BaseModel, ConfigDict, Field

from argus.cost.exhaustion import InsufficientCoverageFloorReport
from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger
from argus.ledger.critical_subsystems import CriticalSubsystemSet
from argus.verdict.verdict_gate import AuditVerdict, Verdict

__all__ = [
    "NEGATIVE_ASSURANCE_SCHEMA_VERSION",
    "DISCLAIMER",
    "NegativeAssuranceError",
    "ScopeStatement",
    "NegativeAssuranceVerdict",
    "build_negative_assurance_verdict",
]

# Single localized source for this contract's schema version (additive-only;
# part of the hashed payload — a bump deliberately changes the content hash).
NEGATIVE_ASSURANCE_SCHEMA_VERSION = "1"

# The fixed negative-assurance disclaimer — a module CONSTANT (no clock, no
# interpolation of volatile values into the hashed payload). It states audit-grade
# humility (FR17/NFR-A3): absence of DETECTED defects within the ASSESSED scope,
# NOT a certification / proof of correctness / assurance about un-assessed code.
# It contains NO over-claim token (the AC2 forbidden-phrase set, blunt
# case-insensitive SUBSTRING scan: "certif", "is correct", "proven", "guarantee",
# "defect-free", "bug-free", "passed"). Note the disclaimer must avoid even the
# DENIAL of those words (e.g. "not a certification") because the scan is a
# substring scan over the whole serialized wrapper — so it is phrased to convey the
# scope-bounded meaning without using any flagged stem.
DISCLAIMER = (
    "This is negative assurance: ArgusAgent reports the absence of detected blocking "
    "findings within the assessed scope only. It is not an attestation of code "
    "correctness and makes no claim about code outside the assessed scope. "
    "Absence of detected findings is not absence of defects."
)


class NegativeAssuranceError(ValueError):
    """A TYPED malformed-input failure for the wrapper builder (AR10).

    A ``ValueError`` subclass localized to this module (mirroring
    ``ExhaustionError`` / ``CriticalSubsystemError``). Raised on a non-``AuditVerdict``
    / non-``InsufficientCoverageFloorReport`` / non-``CriticalSubsystemSet`` input, a
    non-``CoverageLedger`` ledger, a non-``str`` materiality bar, or an inconsistent
    verdict/floor-report pair — never a silent coerce / bare ``except`` / ``print()``
    in library code. The message names the offending value/type only — never source /
    secret bytes (NFR-S1).
    """


class ScopeStatement(BaseModel):
    """Frozen STRUCTURED "examined X, sampled Y, did NOT cover Z" scope triad (FR17/AC3).

    ``frozen=True, extra="forbid"`` (the 1.1/1.2/1.6/3.3 precedent). ALL leaves are
    ``int`` / ``bool`` / ``str`` / sorted ``tuple[str, ...]`` — NO ``float`` (AR4),
    NO absolute host path / source / secret byte (only repo-relative POSIX paths
    REUSED from the already-sanitized ``CriticalSubsystemSet`` — NFR-S1), NO volatile
    ``run_id`` / ``created_at`` (NFR-D3).

    EVERY not-deep class is recorded as its OWN field (``sampled_shallow``,
    ``sampled_tool_scanned``, ``not_covered_inferred``, ``not_covered_skipped``) so
    none can be silently dropped from the scope statement — the AC3 load-bearing
    "did NOT cover Z" honesty clause. The critical narration distinguishes a critical
    subsystem covered deeply from one only shallowly seen / ``designated_but_unmatched``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    # examined — deeply assured.
    examined_deep: int = Field(..., ge=0, description="audited_deep count (deeply assured).")
    # sampled — seen but not deeply assured.
    sampled_shallow: int = Field(..., ge=0, description="audited_shallow count (sampled).")
    sampled_tool_scanned: int = Field(
        ..., ge=0, description="tool_scanned_only count (breadth-sampled)."
    )
    # NOT covered — not assured at all.
    not_covered_inferred: int = Field(..., ge=0, description="inferred count (NOT covered).")
    not_covered_skipped: int = Field(..., ge=0, description="skipped count (NOT covered).")
    skipped_on_exhaustion_count: int = Field(
        ..., ge=0, description="Files skipped because the budget was exhausted (NOT covered)."
    )
    driven_by_exhaustion: bool = Field(
        ..., description="True iff the un-covered remainder was driven by a budget halt (FR22)."
    )
    total_count: int = Field(..., ge=0, description="Total ledger entries (the denominator).")
    # critical-subsystem narration (FR4).
    critical_examined_deep: tuple[str, ...] = Field(
        default=(), description="Critical subsystems examined deeply, sorted (FR4)."
    )
    critical_not_examined_deep: tuple[str, ...] = Field(
        default=(),
        description="Critical subsystems NOT examined deeply (shallow-or-less / unmatched), sorted (FR4).",
    )
    critical_designated_but_unmatched: tuple[str, ...] = Field(
        default=(),
        description="Operator-designated critical paths matching no analyzable file, sorted (FR4).",
    )


class NegativeAssuranceVerdict(BaseModel):
    """Frozen negative-assurance WRAPPER over the done verdict + floor + critical set.

    Story 4.1 (FR17/NFR-A3 / NFR-M2). ``frozen=True, extra="forbid"`` (the
    1.1/1.2/1.6/3.1/3.3 precedent), localized
    :data:`NEGATIVE_ASSURANCE_SCHEMA_VERSION`. WRAPS (does not duplicate) the EXISTING
    verdict surface and adds the FR17/NFR-A3 negative-assurance framing. ALL leaves
    are ``str`` / ``int`` / ``bool`` / ``Fraction`` (rendered ``"num/den"`` by the
    1.1 serializer) — NO ``float`` anywhere (AR4), NO volatile ``run_id`` /
    ``created_at`` in the hashed payload (NFR-D3 — the stamp is the envelope
    ``created_at``), NO absolute host path / source / secret byte (NFR-S1).

    The ``assurance_statement`` is the deterministic, scope-bounded human-readable
    summary — populated + honest + NEVER an over-claim for ALL THREE verdicts. The
    ``disclaimer`` is the fixed :data:`DISCLAIMER` constant.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    schema_version: str = Field(
        default=NEGATIVE_ASSURANCE_SCHEMA_VERSION,
        description="Negative-assurance schema version (localized constant; additive-only).",
    )
    verdict: str = Field(..., description="The 1.6 verdict value (AuditVerdict.verdict.value), REUSED.")
    exit_code: int = Field(..., description="The 1.6 mapped exit code (AR3 wire contract), REUSED.")
    deep_ratio: Fraction = Field(
        ..., description="audited_deep / total — REUSED from AuditVerdict.deep_ratio (never float)."
    )
    materiality_bar: str = Field(
        ..., description="The operator materiality bar the audit ran under (REUSED from AuditRequest)."
    )
    scope_statement: ScopeStatement = Field(
        ..., description="The structured 'examined X, sampled Y, did NOT cover Z' triad (FR17/AC3)."
    )
    assurance_statement: str = Field(
        ..., description="Deterministic scope-bounded negative-assurance summary (NEVER an over-claim)."
    )
    disclaimer: str = Field(
        ..., description="Fixed negative-assurance disclaimer (the DISCLAIMER module constant)."
    )

    def to_canonical_payload(self) -> dict[str, object]:
        """Canonical-safe payload with the LIVE ``Fraction`` leaf for the 1.1 serializer.

        ``model_dump()`` coerces a ``Fraction`` via ``str`` (``Fraction(1, 2) →
        "1"``), which DIVERGES from the LOCKED canonical ``Fraction → "num/den"``
        encoding (the 1.6 ``AuditVerdict`` / 3.3 ``InsufficientCoverageFloorReport``
        precedent). So the live ``Fraction`` object for ``deep_ratio`` is re-installed
        so the single 1.1 ``canonical.dumps`` applies its frozen exact encoding (AR4 /
        NFR-P1). Every other leaf (ints, bools, strs, the nested ``ScopeStatement``'s
        sorted tuples) already ``model_dump()``s to canonical-safe JSON primitives.
        """
        payload = self.model_dump()
        payload["deep_ratio"] = self.deep_ratio
        return payload


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise NegativeAssuranceError(message)


def _critical_narration(
    critical: CriticalSubsystemSet, ledger: CoverageLedger
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split the critical paths into examined-deep vs not-examined-deep (PURE, FR4).

    A critical path is examined-deep iff it has an ``audited_deep`` ledger entry. A
    critical path that is graded shallow-or-less, OR absent from the ledger (the
    conservative ``designated_but_unmatched`` policy), is NOT examined deeply. Both
    returned tuples are sorted (NFR-P1 — no set-iteration-order reliance).
    """
    deep_paths = {
        entry.file_path
        for entry in ledger.entries
        if entry.depth is CoverageDepth.AUDITED_DEEP
    }
    examined = sorted(path for path in critical.paths if path in deep_paths)
    not_examined = sorted(path for path in critical.paths if path not in deep_paths)
    return tuple(examined), tuple(not_examined)


def _build_scope_statement(
    verdict: AuditVerdict,
    floor_report: InsufficientCoverageFloorReport,
    critical: CriticalSubsystemSet,
    ledger: CoverageLedger,
) -> ScopeStatement:
    """Fold the EXISTING records into the structured scope triad (PURE, AC1/AC3)."""
    counts = verdict.counts_by_depth
    critical_deep, critical_not_deep = _critical_narration(critical, ledger)
    return ScopeStatement(
        examined_deep=counts[CoverageDepth.AUDITED_DEEP],
        sampled_shallow=counts[CoverageDepth.AUDITED_SHALLOW],
        sampled_tool_scanned=counts[CoverageDepth.TOOL_SCANNED_ONLY],
        not_covered_inferred=counts[CoverageDepth.INFERRED],
        not_covered_skipped=counts[CoverageDepth.SKIPPED],
        skipped_on_exhaustion_count=floor_report.skipped_on_exhaustion_count,
        driven_by_exhaustion=floor_report.driven_by_exhaustion,
        total_count=verdict.total_count,
        critical_examined_deep=critical_deep,
        critical_not_examined_deep=critical_not_deep,
        critical_designated_but_unmatched=tuple(critical.designated_but_unmatched),
    )


def _assurance_statement(verdict: AuditVerdict, scope: ScopeStatement) -> str:
    """The deterministic, scope-bounded negative-assurance summary (PURE, AC2).

    Honest + populated for ALL THREE verdicts and NEVER an over-claim:
    ``RELEASE_READY`` → "no blocking findings within the assessed scope";
    ``NOT_READY_FOR_RELEASE`` → blocking findings found within scope;
    ``INSUFFICIENT_COVERAGE`` → split on the DISCLOSED FR16 decision row, because that
    verdict now covers two genuinely different situations (Story 8.1):

    - row 1 (below the floor) → "assessed coverage is below the floor; no repo-wide
      verdict was rendered" — BYTE-IDENTICAL to the pre-amendment string;
    - row 4 (a gate unmet with ZERO findings) → "no blocking findings were detected …
      a coverage or critical-subsystem gate was not met".

    This is a PERSISTED artifact string. Emitting the row-1 sentence for a row-4 run
    would state a falsehood on disk — an audit tool asserting a floor breach that did
    not happen — which §3.4 (evidence immutability) makes strictly worse than a slightly
    early story boundary.

    NONE contains a certification / correctness / "proven" / "guarantee" /
    "defect-free" / "passed" token.
    """
    scope_clause = (
        f"examined {scope.examined_deep} deeply, "
        f"sampled {scope.sampled_shallow + scope.sampled_tool_scanned}, "
        f"did not cover {scope.not_covered_inferred + scope.not_covered_skipped} "
        f"of {scope.total_count}"
    )
    # DISCLOSE THE NARROWING, or do not say "the assessed scope".
    #
    # Every sentence below says "within the assessed scope", but the counts above are
    # WHOLE-LEDGER counts. When the gate decided on a NARROWED population — the
    # `application` scope holds out test files — those two things are different
    # populations, and this is the artifact a reader cites as the formal assurance
    # statement. The verdict artifact already carries the full `coverage_scope`
    # disclosure; this one silently omitted it, so a scoped RELEASE_READY read as
    # though it had been earned over the whole repository. Naming the narrowed ratio
    # and the held-out count here makes the sentence true for the population it was
    # actually decided on, and keeps the whole-repository numbers visible beside it.
    coverage_scope = verdict.coverage_scope
    if coverage_scope is not None:
        scope_clause += (
            f"; assessed {coverage_scope.assessed_deep_count} of "
            f"{coverage_scope.assessed_total_count} deeply "
            f"({coverage_scope.assessed_deep_ratio}) under scope "
            f"'{coverage_scope.scope_id}', holding out {coverage_scope.excluded_count} "
            f"({coverage_scope.excluded_reason})"
        )
    if verdict.verdict is Verdict.RELEASE_READY:
        return (
            f"No blocking findings were detected within the assessed scope "
            f"({scope_clause})."
        )
    if verdict.verdict is Verdict.NOT_READY_FOR_RELEASE:
        return (
            f"Blocking findings were detected within the assessed scope "
            f"({scope_clause})."
        )
    if verdict.verdict is Verdict.INSUFFICIENT_COVERAGE:
        if verdict.is_below_floor:
            return (
                f"Assessed coverage is below the floor; no repo-wide verdict was "
                f"rendered ({scope_clause})."
            )
        return (
            f"No blocking findings were detected within the assessed scope; a coverage "
            f"or critical-subsystem gate was not met, so release readiness was not "
            f"vouched for ({scope_clause})."
        )
    raise NegativeAssuranceError(  # pragma: no cover - guarded by the gate's closed enum
        f"unhandled verdict {verdict.verdict!r} in the assurance statement"
    )


def build_negative_assurance_verdict(
    verdict: AuditVerdict,
    floor_report: InsufficientCoverageFloorReport,
    critical: CriticalSubsystemSet,
    ledger: CoverageLedger,
    *,
    materiality_bar: str,
) -> NegativeAssuranceVerdict:
    """Fold the EXISTING records into the negative-assurance wrapper (PURE, AC1/AC2/AC3).

    READS the 1.6 ``AuditVerdict`` + the 3.3 ``InsufficientCoverageFloorReport`` +
    the 2.3 ``CriticalSubsystemSet`` (+ the merged ``CoverageLedger`` for the
    critical-deep cross-reference) — it does NOT re-run the gate, re-derive the
    deep-%, re-declare the floor, or re-identify the critical set (AR4 / §3.3). The
    ``materiality_bar`` is REUSED verbatim from the request. The ``disclaimer`` is
    the fixed :data:`DISCLAIMER` constant. The wrapper is honest + populated for ALL
    THREE verdicts and NEVER an over-claim (AC2). NO clock — the point-in-time stamp
    is the envelope ``created_at`` set by the impure writer (NFR-D3).

    Raises :class:`NegativeAssuranceError` (AR10) on a malformed input (a
    non-``AuditVerdict`` / non-``InsufficientCoverageFloorReport`` /
    non-``CriticalSubsystemSet`` / non-``CoverageLedger``, a non-``str``
    ``materiality_bar``, or an inconsistent verdict/floor-report pair) — never a
    silent coerce. PURE (AR8): no I/O, no clock, no ``uuid``/``random``, no
    LLM/network, no ``float``. Same inputs → byte-identical wrapper + statement
    (NFR-P1).
    """
    _require(
        isinstance(verdict, AuditVerdict),
        f"build_negative_assurance_verdict requires an AuditVerdict, got {type(verdict).__name__}",
    )
    _require(
        isinstance(floor_report, InsufficientCoverageFloorReport),
        "build_negative_assurance_verdict requires an InsufficientCoverageFloorReport, "
        f"got {type(floor_report).__name__}",
    )
    _require(
        isinstance(critical, CriticalSubsystemSet),
        "build_negative_assurance_verdict requires a CriticalSubsystemSet, "
        f"got {type(critical).__name__}",
    )
    _require(
        isinstance(ledger, CoverageLedger),
        f"build_negative_assurance_verdict requires a CoverageLedger, got {type(ledger).__name__}",
    )
    _require(
        isinstance(materiality_bar, str),
        f"materiality_bar must be a str, got {type(materiality_bar).__name__}",
    )
    # The floor report MUST describe the SAME verdict (a pure consistency guard — an
    # inconsistent verdict/floor-report pair is a caller wiring error, AR10).
    _require(
        floor_report.verdict == verdict.verdict.value,
        "verdict / floor_report mismatch: "
        f"{verdict.verdict.value!r} != {floor_report.verdict!r}",
    )

    scope = _build_scope_statement(verdict, floor_report, critical, ledger)
    return NegativeAssuranceVerdict(
        verdict=verdict.verdict.value,
        exit_code=verdict.exit_code,
        deep_ratio=verdict.deep_ratio,
        materiality_bar=materiality_bar,
        scope_statement=scope,
        assurance_statement=_assurance_statement(verdict, scope),
        disclaimer=DISCLAIMER,
    )
