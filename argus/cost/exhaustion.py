"""PURE budget-exhaustion halt → skip → downgrade → report mechanism (FR22).

Drivers: ArgusAgent-FR-22 (ArgusAgent halts on budget exhaustion, marks the remainder
``skipped``, downgrades coverage, and reports honestly — never fabricating or
silently overrunning — the central driver; this module is the deterministic halt
PROJECTION + the frozen ``HaltReport`` "what was / was not assessed" record),
ArgusAgent-NFR-C2 (an audit never exceeds its declared ceiling; on exhaustion it halts
DETERMINISTICALLY — no silent overrun, no wall-clock interrupt), ArgusAgent-NFR-R1 (a
tool/parse/exhaustion condition degrades to a recorded downgrade — never an
uncaught crash or a fabricated result — the honest-degradation keystone),
ArgusAgent-NFR-D2 (deterministic, zero-LLM-token — the halt projection is a pure fold
over ``int`` per-unit contributions), ArgusAgent-NFR-P1 (byte-identical halt point +
skipped set + report across hosts/runs/input-orderings; no ``float``; the full
host-vs-host proof is Story 3.5), ArgusAgent-NFR-S1 (no source / secret /
absolute-host-path bytes — the report carries only repo-relative POSIX paths +
``int``/``bool``/``str`` provenance), ArgusAgent-NFR-M2 (frozen, additive-only
contracts), AR3 (the verdict exit-code wire contract is UNCHANGED — the gate is
reused, not modified — by the pipeline that consumes the partial ledger), AR4 (no
``float``; ``int`` credits / ``bool`` flags / sorted ``tuple``s / ``str``; single
canonical serializer), AR7 (reuse the 3-1 ``_coerce_breach`` ``>=``-hard-ceiling
decision BY IMPORT — no fork, §3.3), AR8 (pure/impure separation — the halt
projection + the report build are PURE; the persistence WRITE is the impure
pipeline shell), AR10 (typed failure — ``ExhaustionError``, never a silent coerce
/ uncaught raise), AR11 (content-derived stable output; the unit iteration order
is the EXISTING sorted index/plan order).

The halt model in a single-pass zero-token V1 pipeline (the central design call)
--------------------------------------------------------------------------------
The V1 pipeline calls NO LLM (the dispatch port is Epic 6), so V1 cost is the
deterministic zero-token work-unit PROXY the 3-1 fold accounts. There is no
incremental per-file billing loop. "Halt mid-run" therefore cannot mean
"interrupt a running LLM dispatch" — it is a **pre-dispatch admission projection**:
project the cumulative per-unit ``int`` cost (in the EXISTING sorted index order)
and stop at the first unit whose inclusion would make the REUSED 3-1
``_coerce_breach(total, ceiling)`` True. Units BEFORE the halt point are AUDITED
(the EXISTING detect/grade stage runs); units AT/AFTER it are SKIPPED-on-exhaustion
(graded ``CoverageDepth.SKIPPED`` via the EXISTING ``grade_entry`` — NEVER a
fabricated ``audited_*``). The halt point is a PURE function of (ordered units,
per-unit proxy, ceiling) — byte-stable + order-independent. When Epic 6 wires the
LLM port the per-unit proxy is replaced by the real per-unit LLM credit estimate
folding into the SAME ``_coerce_breach`` decision — NO new authority.

Reuse BY IMPORT, never fork (AR7 / §3.3)
----------------------------------------
The breach decision is the 3-1 ``budget_governor._coerce_breach`` (which itself
reuses the Minions ``BudgetGuardrails`` ``>=``-is-a-breach semantic — the exact
at-ceiling boundary ``total == ceiling`` is a BREACH). This module maps a
*projected cumulative total* onto the SAME comparison — no second budget authority,
no parallel re-derived comparison.

Story 3.3 — INSUFFICIENT_COVERAGE floor SEMANTICS under exhaustion (FR16/FR22)
-----------------------------------------------------------------------------
The floor MATH already ships (the 1.6 ``evaluate_verdict`` returns
``Verdict.INSUFFICIENT_COVERAGE`` / exit ``3`` below the 20% deep floor, floor-wins
precedence) and 3.2 already re-folds the exhaustion-halted PARTIAL ledger through
it — so a below-floor-under-exhaustion run is ALREADY correct. Story 3.3 adds the
exhaustion-AWARE floor SEMANTICS / RENDER nothing yet produced: a frozen, PURE
:class:`InsufficientCoverageFloorReport` + the PURE :func:`build_floor_report` that
READS the EXISTING 1.6 ``AuditVerdict`` (``deep_ratio`` + ``verdict``) + the 3.2
``HaltReport`` (``halted_on_exhaustion``) and renders the honest PRD-J2 line
``assessed 18% deep; no repo-wide verdict rendered (floor: 20%)``. It NAMES the
assessed deep-% (REUSED from ``AuditVerdict.deep_ratio`` — never re-derived, never
``float``) and distinguishes a floor verdict DRIVEN BY exhaustion
(``halted_on_exhaustion == True``) from an INTRINSIC one (a small/sparse repo that
never cleared 20% with no halt). It does NOT change the 1.6 gate / its thresholds /
floor-wins precedence / exit-code map, the 1.2 ledger, or the 3.2 halt mechanism —
all frozen/reused. The report is exposed PURELY on ``AuditResult`` (no new write —
it is derivable from the already-persisted verdict + halt report; the persist
option was rejected to avoid a speculative artifact). The negative-assurance
WRAPPER (``scope_statement`` / ``materiality_bar`` / ``disclaimer`` /
point-in-time stamp, FR17/NFR-A3) is Story 4.1 — this module produces ONLY the
neutral floor DATA the 4.1 scope statement folds over.

Scope fences (NOT pulled forward — see the story)
-------------------------------------------------
- The negative-assurance verdict WRAPPER (FR17/NFR-A3) → Story 4.1
  (``verdict/negative_assurance.py``); this module produces the neutral floor data.
- Resume-from-disk restore-and-continue → Story 3.4 (the pipeline PERSISTS the
  partial ledger + the halt report — the seam 3.4 reads; this module builds NO
  resume loop).
- Host-vs-host byte-identical parity proof → Story 3.5 (this module's output is
  byte-deterministic + order-independent; the full host parity proof is 3.5).
- Numeric ``$X`` ceiling default / full-repo sizing → Story 7.1 (OI3).
- LLM dispatch port / real LLM credit metering → Epic 6.

Test area ArgusAgent-COST (``TC-ArgusAgent-COST-001-NN``) — continuing the 3-1 cost area.
"""

from __future__ import annotations

from fractions import Fraction

from pydantic import BaseModel, ConfigDict, Field

from argus.cost.budget_governor import BudgetConfig, _coerce_breach
from argus.verdict.verdict_gate import (
    INSUFFICIENT_COVERAGE_FLOOR,
    AuditVerdict,
    Verdict,
)

__all__ = [
    "HALT_SCHEMA_VERSION",
    "FLOOR_REPORT_SCHEMA_VERSION",
    "ExhaustionError",
    "CostUnit",
    "HaltProjection",
    "HaltReport",
    "InsufficientCoverageFloorReport",
    "project_halt_point",
    "would_breach",
    "build_halt_report",
    "build_floor_report",
]

# Localized schema version (additive-only; never env / clock — NFR-M2).
HALT_SCHEMA_VERSION = "1"

# Localized schema version for the Story 3.3 floor report (additive-only; NFR-M2).
FLOOR_REPORT_SCHEMA_VERSION = "1"


class ExhaustionError(ValueError):
    """A TYPED malformed halt-input failure (AR10).

    A ``ValueError`` subclass localized to this module (mirroring
    ``BudgetGovernorError`` / ``PipelineError``). Raised on a ``float`` projected
    cost, a negative / non-``int`` per-unit cost, a non-``str`` unit path, or a
    negative ceiling — never a silent coerce / bare ``except`` / ``print()`` in
    library code. The message names the offending value/type only — never source /
    secret bytes (NFR-S1).
    """


def _require_non_negative_int(value: object, *, label: str) -> int:
    """Return ``value`` if it is a non-negative ``int`` (not ``bool``); else raise.

    ``bool`` is rejected even though it is an ``int`` subclass (a flag is not a
    cost). A ``float`` is rejected outright (AR4 — no float money). The typed
    failure is :class:`ExhaustionError` (AR10).
    """
    if isinstance(value, bool):
        raise ExhaustionError(f"{label} must be a non-negative int, got bool")
    if isinstance(value, float):
        raise ExhaustionError(
            f"{label} must be a non-negative int, got float (AR4 — no float cost)"
        )
    if not isinstance(value, int):
        raise ExhaustionError(
            f"{label} must be a non-negative int, got {type(value).__name__}"
        )
    if value < 0:
        raise ExhaustionError(f"{label} must be a non-negative int, got {value}")
    return value


class CostUnit(BaseModel):
    """A single ordered audit unit + its deterministic ``int`` cost proxy (FR22).

    ``frozen=True, extra="forbid"`` (the 1.1/1.2/3.1 precedent). ``path`` is the
    repo-relative file path (the halt granularity is per-file over the sorted
    index — AR11); ``cost`` is the deterministic, content-derived ``int`` work-unit
    cost attributed to this unit (NEVER ``float`` — AR4). The cost attribution is
    the pipeline's responsibility (it must sum to the 3-1 whole-run total so a
    no-halt projection is consistent with the 3-1 ledger).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str = Field(..., description="Repo-relative unit path (the deterministic order key).")
    cost: int = Field(..., ge=0, description="Deterministic int work-unit cost proxy (NEVER float).")


class HaltProjection(BaseModel):
    """The PURE halt-projection outcome — assessed vs skipped split (FR22 / NFR-C2).

    ``frozen=True, extra="forbid"``. ``halt_index`` is the first unit index whose
    cumulative inclusion would breach the ceiling (``None`` = no halt — admit
    everything). ``assessed_paths`` are the units BEFORE the halt point (run the
    detectors); ``skipped_paths`` are the units AT/AFTER it (graded ``SKIPPED``, no
    detector). Both are SORTED ``tuple[str, ...]`` (order-independent — AR11);
    ``total_credits`` is the cumulative ``int`` cost of the assessed units (the
    spend at the halt point), ``ceiling_credits`` is echoed for provenance. NO
    ``float`` anywhere.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    halt_index: int | None = Field(
        default=None,
        description="First unit index that would breach the ceiling, or None for no halt.",
    )
    total_credits: int = Field(
        ..., ge=0, description="Cumulative int cost of the ASSESSED (admitted) units."
    )
    ceiling_credits: int | None = Field(
        default=None, description="The configured ceiling (None = no ceiling), echoed for provenance."
    )
    assessed_paths: tuple[str, ...] = Field(
        default=(), description="Sorted repo-relative paths of the AUDITED units (NFR-P1)."
    )
    skipped_paths: tuple[str, ...] = Field(
        default=(), description="Sorted repo-relative paths of the SKIPPED-on-exhaustion units."
    )

    @property
    def halted_on_exhaustion(self) -> bool:
        """True iff the projection halted before all units were admitted (FR22)."""
        return self.halt_index is not None


def would_breach(*, total_credits: int, ceiling_credits: int | None) -> bool:
    """Whether ``total_credits`` reaches/exceeds the ceiling — the 3-1 decision REUSED.

    A thin public predicate that delegates to the 3-1
    ``budget_governor._coerce_breach`` BY IMPORT (AR7 / §3.3): the SAME
    ``>=``-is-a-breach hard-ceiling comparison the ``CostLedger.ceiling_reached``
    flag encodes (the exact at-ceiling boundary ``total == ceiling`` is a breach).
    No ceiling (``None``) → never a breach. There is NO fork and NO parallel
    comparison. Validates the inputs (typed :class:`ExhaustionError` on a malformed
    arg — AR10) before delegating.
    """
    total = _require_non_negative_int(total_credits, label="total_credits")
    ceiling = (
        None
        if ceiling_credits is None
        else _require_non_negative_int(ceiling_credits, label="ceiling_credits")
    )
    return _coerce_breach(total_credits=total, ceiling_credits=ceiling)


def project_halt_point(
    units: tuple[CostUnit, ...] | list[CostUnit],
    *,
    config: BudgetConfig,
) -> HaltProjection:
    """PURE pre-dispatch halt projection over the ordered per-unit costs (AC1).

    Projects the cumulative ``int`` cost unit-by-unit in the EXISTING sorted index
    order (AR11) and stops at the FIRST unit whose inclusion would make
    :func:`would_breach` True (the REUSED 3-1 ``>=``-hard-ceiling decision — no
    fork). Units before that index are ASSESSED; the unit at that index and all
    later units are SKIPPED-on-exhaustion. When no ceiling is configured
    (``config.ceiling_credits is None``) OR the cumulative total never breaches, NO
    halt occurs (``halt_index is None``) and every unit is assessed — byte-identical
    to admitting everything (AC6).

    PURE (AR8): no I/O, no clock, no ``uuid``/``random``, no LLM/network, no
    ``float``. The cumulative sum + the sorted assessed/skipped sets make the result
    byte-stable AND order-independent — two input orderings of the SAME units yield
    the identical ``halt_index`` (by path), the identical sorted assessed/skipped
    sets, and the identical ``total_credits`` (NFR-P1). A malformed unit (a
    ``float`` / negative / non-``int`` cost, a non-``str`` path) raises
    :class:`ExhaustionError` (AR10) — never a silent coerce.

    The projection is computed over the units sorted by ``path`` so it is
    deterministic regardless of the caller's input order (the pipeline already
    iterates the sorted index, so this is a belt-and-suspenders determinism pin —
    AR11). The breach decision is evaluated on the cumulative total AFTER including
    each unit: a unit is admitted only if the running total INCLUDING it does not
    breach the ceiling.
    """
    ceiling = config.ceiling_credits
    if ceiling is not None:
        ceiling = _require_non_negative_int(ceiling, label="ceiling_credits")

    ordered: list[CostUnit] = []
    for index, unit in enumerate(units):
        if not isinstance(unit, CostUnit):
            raise ExhaustionError(
                f"unit at index {index} must be a CostUnit, got {type(unit).__name__}"
            )
        if not isinstance(unit.path, str):
            raise ExhaustionError(
                f"unit path at index {index} must be str, got {type(unit.path).__name__}"
            )
        _require_non_negative_int(unit.cost, label=f"unit {unit.path!r} cost")
        ordered.append(unit)
    ordered.sort(key=lambda u: u.path)

    assessed: list[str] = []
    skipped: list[str] = []
    halt_index: int | None = None
    running = 0
    for index, unit in enumerate(ordered):
        if halt_index is not None:
            skipped.append(unit.path)
            continue
        projected = running + unit.cost
        if _coerce_breach(total_credits=projected, ceiling_credits=ceiling):
            halt_index = index
            skipped.append(unit.path)
            continue
        running = projected
        assessed.append(unit.path)

    return HaltProjection(
        halt_index=halt_index,
        total_credits=running,
        ceiling_credits=ceiling,
        assessed_paths=tuple(sorted(assessed)),
        skipped_paths=tuple(sorted(skipped)),
    )


class HaltReport(BaseModel):
    """Frozen "what was / was not assessed" record for one audit (FR22 / NFR-M2).

    ``frozen=True, extra="forbid"``, localized :data:`HALT_SCHEMA_VERSION`. Records
    whether the run halted on exhaustion, the spend + ceiling at halt, and the count
    + SORTED list of units **assessed** vs **`skipped`-on-exhaustion** (the FR22
    "report what it did and did not cover" surface — the Epic-4 negative-assurance
    scope statement folds over it). ALL leaves are ``int`` / ``bool`` / ``str`` /
    sorted ``tuple[str, ...]`` — NO ``float`` anywhere (the canonical serializer is
    the determinism backstop), NO absolute host path / source / secret byte (only
    repo-relative POSIX paths — NFR-S1), NO volatile ``run_id`` / ``created_at``
    (NFR-D3). ``model_dump(mode="json")`` is canonical-safe (no ``Fraction`` leaf).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=HALT_SCHEMA_VERSION,
        description="HaltReport schema version (localized constant; additive-only).",
    )
    halted_on_exhaustion: bool = Field(
        ..., description="True iff the run halted before all units were audited (FR22)."
    )
    total_credits: int = Field(
        ..., ge=0, description="The int spend reached at halt (NEVER float — AR4)."
    )
    ceiling_credits: int | None = Field(
        default=None, description="The configured ceiling (None = no ceiling), echoed for provenance."
    )
    assessed_count: int = Field(..., ge=0, description="Count of AUDITED units.")
    assessed_files: tuple[str, ...] = Field(
        default=(), description="Sorted repo-relative paths of the AUDITED units."
    )
    skipped_on_exhaustion_count: int = Field(
        ..., ge=0, description="Count of SKIPPED-on-exhaustion units."
    )
    skipped_on_exhaustion_files: tuple[str, ...] = Field(
        default=(), description="Sorted repo-relative paths of the SKIPPED-on-exhaustion units."
    )

    def to_canonical_payload(self) -> dict[str, object]:
        """Canonical-safe payload (all leaves int/bool/str/tuple[str] — no Fraction).

        ``model_dump(mode="json")`` already renders every leaf to a canonical-safe
        JSON primitive (tuples → lists, ``None`` → null); there is no ``Fraction``
        leaf so no LIVE-``Fraction`` re-install is needed (contrast the 3-1
        ``CostLedger.to_canonical_payload``). Provided for call-site symmetry with
        the 3-1 snapshot persistence and to keep the persisted shape explicit.
        """
        return self.model_dump(mode="json")


def build_halt_report(projection: HaltProjection) -> HaltReport:
    """Build the frozen :class:`HaltReport` from a :class:`HaltProjection` (PURE, AC4).

    A pure projection of the halt outcome onto the persisted report shape — the
    assessed/skipped sets are already sorted on the projection, the counts are their
    lengths, and ``halted_on_exhaustion`` is derived from ``halt_index``. NO ``float``,
    NO absolute path / source / secret byte (the projection carries only
    repo-relative paths the pipeline supplied). A NON-halted projection produces a
    report with ``halted_on_exhaustion = False`` + an EMPTY skipped list + the full
    assessed list (always populated + honest — AC4).
    """
    return HaltReport(
        halted_on_exhaustion=projection.halted_on_exhaustion,
        total_credits=projection.total_credits,
        ceiling_credits=projection.ceiling_credits,
        assessed_count=len(projection.assessed_paths),
        assessed_files=projection.assessed_paths,
        skipped_on_exhaustion_count=len(projection.skipped_paths),
        skipped_on_exhaustion_files=projection.skipped_paths,
    )


def _whole_percent(ratio: Fraction) -> int:
    """Render an exact ``Fraction`` deep-% as a whole-percent ``int`` (AR4 — never float).

    ``int(ratio * 100)`` over exact ``Fraction`` arithmetic truncates toward zero
    (``Fraction(9, 50) * 100 == Fraction(18, 1) → 18``; ``Fraction(1, 3) * 100 →
    33``) — byte-stable across hosts. The PRD J2 line uses whole-percent ("18%").
    NEVER ``float(ratio)`` (the AR4 byte-diff landmine the 2.2 render also avoids).
    """
    return int(ratio * 100)


class InsufficientCoverageFloorReport(BaseModel):
    """Frozen exhaustion-aware floor surface READ-folded from the verdict + halt report.

    Story 3.3 (FR16/FR22 / NFR-M2). ``frozen=True, extra="forbid"`` (the
    1.1/1.2/1.6/3.1/3.2 precedent), localized :data:`FLOOR_REPORT_SCHEMA_VERSION`.
    The honest "assessed X% deep; floor 20%" surface for ANY run — populated +
    honest even when the verdict is NOT the floor (``below_floor=False``). ALL
    leaves are ``str`` / ``int`` / ``bool`` / ``Fraction`` (rendered ``"num/den"``
    by the 1.1 serializer) — NO ``float`` anywhere (AR4), NO volatile
    ``run_id``/``created_at`` (NFR-D3), NO absolute host path / source / secret byte
    (only ``int`` counts REUSED from the already-sanitized ``HaltReport`` — NFR-S1).

    Fields are READ-folded (no re-derivation): ``deep_ratio`` is the EXISTING
    ``AuditVerdict.deep_ratio``; ``floor`` is the EXISTING
    ``INSUFFICIENT_COVERAGE_FLOOR``; ``below_floor`` is
    ``verdict == INSUFFICIENT_COVERAGE`` (which the gate guarantees equals
    ``deep_ratio < floor``); ``driven_by_exhaustion`` is exactly
    ``HaltReport.halted_on_exhaustion`` (the FR22↔FR16 join the raw verdict cannot
    express).
    """

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    schema_version: str = Field(
        default=FLOOR_REPORT_SCHEMA_VERSION,
        description="Floor-report schema version (localized constant; additive-only).",
    )
    verdict: str = Field(..., description="The 1.6 verdict value (AuditVerdict.verdict.value).")
    deep_ratio: Fraction = Field(
        ..., description="Assessed audited_deep / total — REUSED from AuditVerdict.deep_ratio (never float)."
    )
    floor: Fraction = Field(
        ..., description="The REUSED INSUFFICIENT_COVERAGE_FLOOR (Fraction(1, 5) = 20%)."
    )
    below_floor: bool = Field(
        ..., description="True iff the verdict is INSUFFICIENT_COVERAGE (deep-% below the 20% floor)."
    )
    driven_by_exhaustion: bool = Field(
        ..., description="True iff the floor was driven by a budget halt (HaltReport.halted_on_exhaustion)."
    )
    assessed_count: int = Field(..., ge=0, description="Count of AUDITED units (REUSED from the HaltReport).")
    skipped_on_exhaustion_count: int = Field(
        ..., ge=0, description="Count of SKIPPED-on-exhaustion units (REUSED from the HaltReport)."
    )
    message: str = Field(
        ..., description="Deterministic human-readable PRD-J2 floor line (whole-percent, no float)."
    )

    def to_canonical_payload(self) -> dict[str, object]:
        """Canonical-safe payload with LIVE ``Fraction`` leaves for the 1.1 serializer.

        ``model_dump()`` coerces a ``Fraction`` via ``str`` (``Fraction(1, 5) →
        "1"``), which DIVERGES from the LOCKED canonical ``Fraction → "num/den"``
        encoding (the 1.6 ``AuditVerdict`` / 2.2 ``CoverageReport`` precedent). So
        the live ``Fraction`` objects for ``deep_ratio`` + ``floor`` are re-installed
        so the single 1.1 ``canonical.dumps`` applies its frozen exact encoding (AR4
        / NFR-P1). No second serializer.
        """
        payload = self.model_dump()
        payload["deep_ratio"] = self.deep_ratio
        payload["floor"] = self.floor
        return payload


def build_floor_report(
    verdict: AuditVerdict, halt_report: HaltReport
) -> InsufficientCoverageFloorReport:
    """Fold the EXISTING ``AuditVerdict`` + ``HaltReport`` into the floor report (PURE, AC2).

    READS the two records — it does NOT re-run the gate, re-derive the deep-%, or
    re-declare the floor (AR4 / §3.3). ``below_floor`` reads the gate's decision
    directly (``verdict.verdict == INSUFFICIENT_COVERAGE``); the gate guarantees this
    equals ``deep_ratio < INSUFFICIENT_COVERAGE_FLOOR`` (including the ``total == 0``
    short-circuit, where ``deep_ratio`` is ``0/1 < 1/5``) — pinned by a test.
    ``driven_by_exhaustion`` reads ``halt_report.halted_on_exhaustion`` EXACTLY (the
    exhaustion-driven-vs-intrinsic signal). The ``message`` is the deterministic
    PRD-J2 line rendered from the EXACT ``Fraction`` whole-percent (no ``float``):
    below-floor → ``"assessed X% deep; no repo-wide verdict rendered (floor: Y%)"``;
    otherwise → ``"assessed X% deep; verdict rendered: <VERDICT>"`` (always populated
    + honest). A non-``AuditVerdict`` / non-``HaltReport`` argument raises the typed
    :class:`ExhaustionError` (AR10) — never a silent coerce.

    PURE (AR8): no I/O, no clock, no ``uuid``/``random``, no LLM/network, no
    ``float``. Same inputs → byte-identical report + message (NFR-P1).
    """
    if not isinstance(verdict, AuditVerdict):
        raise ExhaustionError(
            f"build_floor_report requires an AuditVerdict, got {type(verdict).__name__}"
        )
    if not isinstance(halt_report, HaltReport):
        raise ExhaustionError(
            f"build_floor_report requires a HaltReport, got {type(halt_report).__name__}"
        )

    below_floor = verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    deep_pct = _whole_percent(verdict.deep_ratio)
    if below_floor:
        floor_pct = _whole_percent(INSUFFICIENT_COVERAGE_FLOOR)
        message = (
            f"assessed {deep_pct}% deep; no repo-wide verdict rendered "
            f"(floor: {floor_pct}%)"
        )
    else:
        message = f"assessed {deep_pct}% deep; verdict rendered: {verdict.verdict.value}"

    return InsufficientCoverageFloorReport(
        verdict=verdict.verdict.value,
        deep_ratio=verdict.deep_ratio,
        floor=INSUFFICIENT_COVERAGE_FLOOR,
        below_floor=below_floor,
        driven_by_exhaustion=halt_report.halted_on_exhaustion,
        assessed_count=halt_report.assessed_count,
        skipped_on_exhaustion_count=halt_report.skipped_on_exhaustion_count,
        message=message,
    )
