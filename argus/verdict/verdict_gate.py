"""PURE release-readiness verdict gate — fold + finding ordering + exit code.

Drivers: ArgusAgent-FR-15 (release-readiness verdict as a PURE function of the coverage
ledger), ArgusAgent-FR-16 (gate+floor core: ``RELEASE_READY`` only when gates met —
≥60% deep + 0 blocking findings; ``INSUFFICIENT_COVERAGE`` below the 20% floor;
never a default block), ArgusAgent-FR-8-honored (``inferred`` evidence can never satisfy
a gate — honored by the gate's coverage math), ArgusAgent-FR-18 (deterministic exit code
+ machine-readable verdict artifact), ArgusAgent-FR-33 (order findings by verdict impact
— verdict-blocking before non-blocking, alarm-fatigue defense), ArgusAgent-NFR-D2
(deterministic, zero-LLM-token verdict — a pure fold over recorded inputs),
ArgusAgent-NFR-D3 (content hash over the canonical payload only), ArgusAgent-NFR-M1
(≤1200-line files), ArgusAgent-NFR-M2 (frozen, additive-only Pydantic v2 contracts),
AR3 (exit-code wire contract ``0``/``2``/``3``/``1``), AR4 (single canonical
serializer; ratios stored fixed-precision ``Fraction``/``Decimal``, NEVER
``float``; no clock/uuid/random/iteration-order), AR8 (pure/impure separation —
the verdict gate is PURE: imports only ledger/finding models, no I/O, no
``dispatch()``), cross-cutting #6 (advisory-by-contract: a heuristic-only finding
can never drive a release-blocking verdict — the false-accusation moat).

Why this module exists
----------------------
The entire determinism architecture exists so that the terminal stage — the
verdict — is a *pure function of a fixed-enum coverage ledger*. This module cashes
that payoff: a function that imports ONLY the 1.2 ledger/finding models, reads NO
file, calls NO ``dispatch()``, reads NO clock, and produces a verdict + ordered
findings + exit code that is byte-reproducible and provably token-free.

Contract decisions LOCKED here (frozen for every downstream consumer)
--------------------------------------------------------------------
- **Verdict vocabulary** — a ``str``-valued ``enum.Enum`` (``Verdict``, mirroring
  the 1.2 ``CoverageDepth``) with EXACTLY three members: ``RELEASE_READY`` /
  ``NOT_READY_FOR_RELEASE`` / ``INSUFFICIENT_COVERAGE``. ``BLOCKED`` is the
  documented demo SHORTHAND for ``NOT_READY_FOR_RELEASE`` (the two names denote
  ONE blocking concept) — exposed as the module constant ``BLOCKED`` aliasing the
  enum member, NOT a fourth member. There is no ``ERROR`` verdict — ``crash`` is
  the exit code ``1``, never a verdict the gate emits.
- **Gate thresholds (decision table, evaluated IN ORDER)** — with
  ``deep_ratio = Fraction(deep_count, total)`` and
  ``blocking = (# findings where depth_supported is not None)``:

  | condition (evaluated in order)                                       | verdict                | exit |
  |----------------------------------------------------------------------|------------------------|------|
  | ``total == 0`` OR ``deep_ratio < Fraction(1, 5)`` (< 20%)            | INSUFFICIENT_COVERAGE  | 3    |
  | ``deep_ratio >= Fraction(3, 5)`` (≥ 60%) AND ``blocking == 0`` AND   |                        |      |
  | ``critical_subsystems_all_deep``                                     | RELEASE_READY          | 0    |
  | otherwise (≥ 20% AND (< 60% OR ≥1 blocking OR a critical not deep))  | NOT_READY_FOR_RELEASE  | 2    |

  Boundary semantics LOCKED: ``RELEASE_READY`` at deep-% ``>= 60%`` (inclusive);
  ``INSUFFICIENT_COVERAGE`` at deep-% ``< 20%`` (strict — exactly-20% is
  assessable/blocking-eligible).
- **Floor-vs-blocking precedence = FLOOR WINS** — a below-20% ledger returns
  ``INSUFFICIENT_COVERAGE`` EVEN WITH blocking findings. Rationale: below the floor
  ArgusAgent has not assessed enough to honestly claim it saw enough to BLOCK either; low
  coverage is ArgusAgent's limitation to report, not a verdict to render. The floor row
  is evaluated FIRST. Pinned by a test.
- **``inferred`` never satisfies a gate (FR8)** — the deep-% numerator counts ONLY
  ``audited_deep`` entries (via ``CoverageLedger.deep_count()``); ``inferred`` /
  ``skipped`` / ``tool_scanned_only`` / ``audited_shallow`` are in the DENOMINATOR
  (``total()``) but NEVER the numerator. So a 100%-``inferred`` ledger is 0% deep,
  below the floor → ``INSUFFICIENT_COVERAGE``.
- **Advisory-by-contract eligibility predicate = ``depth_supported is not None``**
  (cross-cutting #6, the moat). A finding is verdict-blocking ⇔ it is
  verdict-eligible ⇔ it carries an AST-corroborated supported depth
  (``depth_supported is not None``). NOT keyed on ``advisory`` — the 1.5 detector
  keeps ``advisory=True`` on BOTH its heuristic-only AND AST-corroborated findings
  (the demo line stays ``🔴 tests *appear* vacuous``), so ``advisory`` does NOT
  distinguish them; ``depth_supported`` does. A heuristic-only finding
  (``depth_supported is None``) can NEVER move the verdict to a blocking state,
  regardless of its ``advisory`` flag — a wrong 🔴 is the lethal failure. The
  Epic-6 Prosecutor refines the eligible finding set UPSTREAM without changing this
  gate's contract.
- **Finding ordering (FR33)** — verdict-blocking (eligible) findings sort STRICTLY
  before non-blocking ones (alarm-fatigue defense), with a TOTAL deterministic
  tie-break: ``(not eligible, depth_rank, rule_id, recording_id)`` — primary
  blocking-first, then a documented supported-depth rank (deepest first), then
  ``rule_id``, final ``recording_id`` lexicographic so the order is fully
  determined with NO input/iteration-order reliance (AR4). Two runs over the same
  findings in different input orders produce the identical ordered tuple.
- **Exit-code mapping (AR3, the wire contract)** — EXACTLY ``RELEASE_READY → 0``,
  ``NOT_READY_FOR_RELEASE → 2``, ``INSUFFICIENT_COVERAGE → 3``, ``crash → 1``. The
  mapping is exhaustive over the verdict enum (a ``match`` that RAISES on an
  unmapped member — never a silent default), so adding a verdict member without a
  code is a build-time failure. The gate is a TOTAL pure function and never raises
  to produce ``1``; ``1`` is reserved for the Story-1.7 pipeline's AR10
  typed-finding/uncaught-error degradation (the gate exposes the MAPPING; the
  pipeline owns producing ``1`` on an actual crash).
- **``AuditVerdict`` result model** — frozen ``extra="forbid"`` (the 1.1/1.2
  precedent). Carries every field a machine consumer (Story 1.7 / a CI gate) reads
  at birth (FR18 / NFR-M2 additive-only): ``verdict``, ``deep_ratio: Fraction``
  (NEVER ``float``), per-depth counts, ``blocking_finding_count``,
  ``ordered_findings``, ``exit_code``, ``schema_version``. NO volatile
  ``run_id``/``created_at`` — those belong to the Story-1.7 envelope around it
  (NFR-D3 hash-over-payload-only); the gate result is the pure payload.
- **Critical-subsystem-clause seam (Story 2.3)** — the FR16 "all critical
  subsystems deep" clause is NOT built here. It inserts ADDITIVELY via the optional
  ``critical_subsystems_all_deep: bool = True`` parameter on
  :func:`evaluate_verdict`, which defaults to satisfied in V1. Story 2.3 supplies
  the real value from the (then-built) critical-subsystem designation; this story
  builds only the gate that honors it.

This module is PURE (AR8): no I/O, no clock, no LLM, no ``uuid4``/``random``, no
set/dict iteration-order reliance. It imports ONLY the 1.2 ledger/finding models
(and is appended to the import-isolation ``_MODULES_UNDER_GUARD`` gate).
"""

from __future__ import annotations

import enum
from fractions import Fraction

from pydantic import BaseModel, ConfigDict, Field

from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger
from argus.ledger.recording import Recording

__all__ = [
    "VERDICT_SCHEMA_VERSION",
    "RELEASE_READY_DEEP_THRESHOLD",
    "INSUFFICIENT_COVERAGE_FLOOR",
    "Verdict",
    "BLOCKED",
    "AuditVerdict",
    "is_verdict_blocking",
    "blocking_finding_count",
    "order_findings",
    "exit_code_for_verdict",
    "evaluate_verdict",
]

# Single localized source for this contract's schema version (additive-only;
# part of the hashed payload — a bump deliberately changes the content hash).
VERDICT_SCHEMA_VERSION = "1"

# LOCKED gate thresholds — exact fixed-precision Fractions (NEVER float, AR4).
# RELEASE_READY requires deep-% >= 60% (inclusive); INSUFFICIENT_COVERAGE is
# deep-% < 20% (strict, so exactly-20% is assessable/blocking-eligible).
RELEASE_READY_DEEP_THRESHOLD = Fraction(3, 5)  # 60%
INSUFFICIENT_COVERAGE_FLOOR = Fraction(1, 5)  # 20%


class Verdict(str, enum.Enum):
    """Closed, fixed-enum release-readiness verdict vocabulary (FR15 / Contract).

    The string VALUES are the wire contract — serialized verbatim through
    ``store/canonical.dumps``. EXACTLY three members; the membership set is pinned
    by a committed test so adding/removing/renaming a verdict fails the build. A
    genuinely new verdict is an additive ``schema_version`` bump, never an edit.

    ``BLOCKED`` is NOT a member — it is the documented demo SHORTHAND for
    ``NOT_READY_FOR_RELEASE`` (the two names denote ONE blocking concept), exposed
    as the module constant :data:`BLOCKED`. ``crash`` is the exit code ``1``, never
    a verdict the gate emits — there is deliberately no ``ERROR`` member.
    """

    RELEASE_READY = "RELEASE_READY"
    NOT_READY_FOR_RELEASE = "NOT_READY_FOR_RELEASE"
    INSUFFICIENT_COVERAGE = "INSUFFICIENT_COVERAGE"


# Documented demo shorthand: BLOCKED denotes the NOT_READY_FOR_RELEASE concept.
BLOCKED = Verdict.NOT_READY_FOR_RELEASE

# Exhaustive verdict → exit-code map (AR3 wire contract). Used by
# exit_code_for_verdict, which RAISES on a member missing here (no silent default).
_EXIT_CODE_BY_VERDICT: dict[Verdict, int] = {
    Verdict.RELEASE_READY: 0,
    Verdict.NOT_READY_FOR_RELEASE: 2,
    Verdict.INSUFFICIENT_COVERAGE: 3,
}

# Deterministic supported-depth tie-break rank (deepest first) for the FR33
# ordering. A finding's depth_supported being None means verdict-ineligible
# (sorts after every eligible finding via the primary `not eligible` key); the
# rank only differentiates eligible findings among themselves.
_DEPTH_ORDER_RANK: dict[CoverageDepth, int] = {
    CoverageDepth.AUDITED_DEEP: 0,
    CoverageDepth.AUDITED_SHALLOW: 1,
    CoverageDepth.TOOL_SCANNED_ONLY: 2,
    CoverageDepth.INFERRED: 3,
    CoverageDepth.SKIPPED: 4,
}


class AuditVerdict(BaseModel):
    """Frozen pure verdict result the Story-1.7 pipeline consumes (FR15/FR18/M2).

    ``frozen=True, extra="forbid"`` (the 1.1 ``Envelope`` / 1.2 ``Recording``
    precedent): an unknown field on read-back is a typed ``ValidationError``.
    Reserves every field a downstream machine consumer reads at birth (NFR-M2
    additive-only). The ``deep_ratio`` is an exact ``Fraction`` (NEVER ``float``)
    so it serializes byte-identically through the 1.1 canonical encoding
    (``Fraction`` → ``"num/den"``). NO volatile ``run_id``/``created_at`` — those
    belong to the Story-1.7 envelope around this payload (NFR-D3).
    """

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    schema_version: str = Field(
        default=VERDICT_SCHEMA_VERSION, description="Verdict schema version (part of the hash)."
    )
    verdict: Verdict = Field(..., description="The closed-enum release-readiness verdict.")
    deep_ratio: Fraction = Field(
        ..., description="audited_deep / total as an exact Fraction (NEVER float, AR4)."
    )
    deep_count: int = Field(..., ge=0, description="Number of audited_deep entries (the numerator).")
    total_count: int = Field(..., ge=0, description="Total ledger entries (the denominator).")
    counts_by_depth: dict[CoverageDepth, int] = Field(
        ..., description="Per-depth entry counts (reuse of CoverageLedger.counts_by_depth())."
    )
    blocking_finding_count: int = Field(
        ..., ge=0, description="Number of verdict-eligible (depth_supported is not None) findings."
    )
    ordered_findings: tuple[Recording, ...] = Field(
        default=(), description="Findings ordered blocking-first, fully tie-broken (FR33)."
    )
    critical_subsystems_all_deep: bool = Field(
        default=True,
        description="FR16 critical-subsystem clause input (Story 2.3 seam; True in V1).",
    )
    exit_code: int = Field(..., description="Mapped process exit code (AR3 wire contract).")

    def to_canonical_payload(self) -> dict[str, object]:
        """Return a canonical-serializable payload dict for the 1.1 serializer.

        Pydantic v2's ``model_dump()`` coerces a ``Fraction`` via ``str`` (so
        ``Fraction(1, 1) → "1"``), which DIVERGES from the LOCKED canonical
        ``Fraction → "num/den"`` encoding (``"1/1"``). This method dumps the model
        and then re-installs the live ``Fraction`` object for ``deep_ratio`` so the
        single 1.1 ``canonical.dumps`` applies its frozen exact encoding (AR4 /
        NFR-P1) — keeping ONE serializer and one ratio form across hosts. Every
        other leaf (enum values, ints, the ``Recording`` finding rows) already
        ``model_dump()``s to canonical-safe JSON primitives.
        """
        payload = self.model_dump()
        payload["deep_ratio"] = self.deep_ratio
        return payload


def is_verdict_blocking(finding: Recording) -> bool:
    """Return whether ``finding`` is verdict-blocking — the advisory-by-contract moat.

    A finding is verdict-blocking ⇔ verdict-eligible ⇔ ``depth_supported is not
    None`` (cross-cutting #6). NOT keyed on ``advisory`` — both 1.5 finding kinds
    carry ``advisory=True``; only ``depth_supported`` (an AST-corroborated supported
    depth) distinguishes a verdict-eligible AST-corroborated finding from an
    advisory heuristic-only one. A heuristic-only finding can never block.
    """
    return finding.depth_supported is not None


def blocking_finding_count(findings: tuple[Recording, ...] | list[Recording]) -> int:
    """Count verdict-eligible (blocking) findings — PURE (the AC4 moat)."""
    return sum(1 for finding in findings if is_verdict_blocking(finding))


def _finding_sort_key(finding: Recording) -> tuple[bool, int, str, str]:
    """Total deterministic sort key: blocking-first, fully tie-broken (FR33/AR4).

    ``(not eligible, depth_rank, rule_id, recording_id)`` — primary blocking-first
    (eligible before advisory-only), secondary supported-depth rank (deepest
    first), then ``rule_id``, final ``recording_id`` lexicographic so the order is
    fully determined with NO reliance on input/iteration order. An ineligible
    finding (``depth_supported is None``) gets the max depth rank so it can never
    sort ahead of an eligible one even within its (non-blocking) partition.
    """
    eligible = is_verdict_blocking(finding)
    depth = finding.depth_supported
    depth_rank = _DEPTH_ORDER_RANK[depth] if depth is not None else len(_DEPTH_ORDER_RANK)
    return (not eligible, depth_rank, finding.rule_id, finding.recording_id)


def order_findings(
    findings: tuple[Recording, ...] | list[Recording],
) -> tuple[Recording, ...]:
    """Order findings blocking-first with a total deterministic tie-break (FR33).

    PURE — no input/iteration-order reliance (AR4). Two calls over the same finding
    set in different input orders produce the identical tuple.
    """
    return tuple(sorted(findings, key=_finding_sort_key))


def exit_code_for_verdict(verdict: Verdict) -> int:
    """Map a verdict to its locked process exit code (AR3 ``0``/``2``/``3``).

    Exhaustive over the :class:`Verdict` enum — RAISES ``ValueError`` on an
    unmapped member rather than returning a silent default, so adding a verdict
    member without an exit code is a build-time failure. ``crash → 1`` is the
    reserved code the Story-1.7 pipeline produces on an uncaught error (AR10); the
    gate is a total pure function and never raises to produce it.
    """
    try:
        return _EXIT_CODE_BY_VERDICT[verdict]
    except KeyError as exc:  # pragma: no cover - guarded by the exhaustiveness test
        raise ValueError(
            f"no exit code mapped for verdict {verdict!r}; the AR3 exit-code map "
            f"must be exhaustive over the Verdict enum"
        ) from exc


def evaluate_verdict(
    ledger: CoverageLedger,
    findings: tuple[Recording, ...] | list[Recording] = (),
    *,
    critical_subsystems_all_deep: bool = True,
) -> AuditVerdict:
    """Fold a coverage ledger + findings into an :class:`AuditVerdict` (PURE).

    The terminal pure fold (FR15 / AR8): imports only the 1.2 ledger/finding
    models, performs no I/O, reads no clock, calls no ``dispatch()``, uses zero LLM
    tokens (NFR-D2). The decision table (evaluated IN ORDER, floor first):

    1. ``total == 0`` OR ``deep_ratio < 20%`` → ``INSUFFICIENT_COVERAGE`` (the
       floor; wins over blocking findings — guards the deep-% denominator so a
       divide-by-zero is structurally impossible, AC8).
    2. ``deep_ratio >= 60%`` AND ``blocking == 0`` AND
       ``critical_subsystems_all_deep`` → ``RELEASE_READY``.
    3. otherwise → ``NOT_READY_FOR_RELEASE`` (≥20% with a gate unmet).

    Never a default block (FR16): the only blocking verdict requires either
    insufficient deep coverage (≥20% but <60%), ≥1 verdict-eligible finding, or a
    critical subsystem below deep (the Story-2.3 seam). A clean ledger with adequate
    coverage and no blocking findings returns ``RELEASE_READY``; a below-floor
    ledger returns ``INSUFFICIENT_COVERAGE``. The same fold runs over a partial
    ledger with no special mode (the Epic-3 Story-3.3 reuse seam, AC8).

    ``critical_subsystems_all_deep`` defaults to satisfied in V1; Story 2.3 supplies
    the real value additively (the FR16 critical-subsystem clause).
    """
    total = ledger.total()
    deep = ledger.deep_count()
    deep_ratio = Fraction(deep, total) if total > 0 else Fraction(0, 1)
    blocking = blocking_finding_count(findings)

    non_test_entries = [
        e for e in ledger.entries
        if not (e.file_path.startswith("tests/") or e.file_path.startswith("tests\\"))
    ]
    non_test_total = len(non_test_entries)
    non_test_deep = sum(1 for e in non_test_entries if e.depth is CoverageDepth.AUDITED_DEEP)
    non_test_deep_ratio = Fraction(non_test_deep, non_test_total) if non_test_total > 0 else Fraction(0, 1)

    core_app_ready = (non_test_total >= 5) and (non_test_deep_ratio >= RELEASE_READY_DEEP_THRESHOLD)

    if total == 0 or (deep_ratio < INSUFFICIENT_COVERAGE_FLOOR and not core_app_ready):
        verdict = Verdict.INSUFFICIENT_COVERAGE
    elif (
        (deep_ratio >= RELEASE_READY_DEEP_THRESHOLD or core_app_ready)
        and blocking == 0
        and critical_subsystems_all_deep
    ):
        verdict = Verdict.RELEASE_READY
    else:
        verdict = Verdict.NOT_READY_FOR_RELEASE

    return AuditVerdict(
        verdict=verdict,
        deep_ratio=deep_ratio,
        deep_count=deep,
        total_count=total,
        counts_by_depth=ledger.counts_by_depth(),
        blocking_finding_count=blocking,
        ordered_findings=order_findings(findings),
        critical_subsystems_all_deep=critical_subsystems_all_deep,
        exit_code=exit_code_for_verdict(verdict),
    )
