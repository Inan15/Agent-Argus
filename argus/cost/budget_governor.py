"""PURE budget-ceiling configuration + deterministic cost-accounting core (FR21).

Drivers: ArgusAgent-FR-21 (an operator can set a budget ceiling for an audit — the
central driver; this module is the ceiling CONFIGURATION + the deterministic
COST-ACCOUNTING mechanism it enforces over), ArgusAgent-NFR-C1 (a baseline full audit
costs a bounded fraction of the audited repo's build cost — V1 MEASURES and
REPORTS the baseline as an exact ``Fraction``, not asserted / not gated),
ArgusAgent-NFR-C2 (an audit never exceeds its declared ceiling — *the mid-run halt is
Story 3.2*; this module builds the ceiling + the accounting C2 enforces over and
EXPOSES ``ceiling_reached`` for 3.2 to query), ArgusAgent-NFR-D2 (deterministic,
zero-LLM-token — the fold is a pure reduction over ``int`` contributions),
ArgusAgent-NFR-P1 (byte-identical accounting across hosts/runs + input orderings — no
``float`` money), ArgusAgent-NFR-M2 (frozen, additive-only contracts), AR4 (no
``float`` — ``int`` credits / ``Fraction`` ratios; the single canonical
serializer is the determinism backstop), AR7 (reuse ``minions_core.cost.
budget_guardrails`` BY IMPORT — verified FastAPI-free; no fork of the hard-ceiling
semantic, §3.3), AR8 (pure/impure separation — this module is PURE; the snapshot
WRITE is the impure pipeline shell), AR10 (typed failure — ``BudgetGovernorError``,
never a silent coerce / uncaught raise), AR11 (content-derived stable output).

The OI3 hard rule — NO numeric ``$X`` default (the design crux)
---------------------------------------------------------------
The budget-ceiling ``$X`` numeric default is DEFERRED to the empirical Story 7.1
dogfood sizing (epics §"Open delivery inputs — LOCKED 2026-06-18", OI3). This
module ships the MECHANISM, never a number. The no-ceiling state is FIRST-CLASS:
``ceiling_credits = None`` means "no ceiling configured" — accounting still runs
and reports, it simply admits everything. It is expressed via
``request.budget == 0 → None`` (the existing CLI default), NOT a magic default
int. There is no hardcoded numeric ceiling default anywhere in this module.

Reuse BY IMPORT, never fork (AR7 / §3.3 — the 21-2 ``evaluate_preflight`` precedent)
------------------------------------------------------------------------------------
The hard-ceiling breach decision is the Minions ``BudgetGuardrails``
``>=``-is-a-breach semantic (``evaluate_worker_spend``: ``within = credits_consumed
< max_worker_credits`` ⇒ the exact at-ceiling boundary ``total == ceiling`` is a
BREACH — mirror ``TC-COST-001-46``). ArgusAgent maps its ``int`` running total onto the
SAME comparison by constructing a ``BudgetPolicy(max_worker_credits=ceiling)`` and
calling ``evaluate_worker_spend(total)`` — there is no second budget authority and
no parallel re-derived comparison. The Minions ``BudgetPolicy`` fields are
``float`` — that ``float`` NEVER reaches an ``.argus/`` payload; the import is used
purely for its DECISION over ``int`` ArgusAgent values, and every ArgusAgent-persisted cost
figure is ``int`` credits / a ``Fraction`` ratio (the canonical serializer rejects
``float``). The import is verified FastAPI-free by the import-isolation gate.

Scope fences (NOT pulled forward — see the story)
-------------------------------------------------
- Mid-run HALT / mark-remainder-``skipped`` / downgrade-on-exhaustion → Story 3.2.
  This module EXPOSES ``ceiling_reached`` + the running total; it does NOT halt.
- ``INSUFFICIENT_COVERAGE`` floor under exhaustion → Story 3.3 (verdict math
  UNCHANGED here).
- Resume-from-disk restore-and-continue → Story 3.4 (this module's report is
  persisted additively by the pipeline; the resume loop is 3.4).
- Numeric ``$X`` ceiling default / full-repo sizing → Story 7.1 (OI3).
- LLM dispatch port / real LLM credit metering → Epic 6. V1 cost contributions are
  the deterministic zero-token work units (files indexed / tool invocations /
  detector passes), a forward-compatible proxy — NOT a billed LLM total.

Test area ArgusAgent-COST (``TC-ArgusAgent-COST-001-NN``) — a new per-module verification area.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field, field_validator

from argus.shared.budget_guardrails import BudgetGuardrails, BudgetPolicy

__all__ = [
    "BUDGET_SCHEMA_VERSION",
    "COST_SCHEMA_VERSION",
    "BudgetGovernorError",
    "BudgetConfig",
    "CostLedger",
    "budget_config_from_budget",
    "account_spend",
    "baseline_ratio",
]

# Localized schema versions (additive-only; never env / clock — NFR-M2).
BUDGET_SCHEMA_VERSION = "1"
COST_SCHEMA_VERSION = "1"

# The marker the NFR-C1 baseline ratio takes when the build-cost proxy is 0 (an
# empty repo) — total-safe, never a divide-by-zero / float('inf') (the 1.6
# ``total == 0`` floor-first guard precedent). It is a closed ``str`` sentinel,
# NOT a fabricated number, so the report stays honest and serializable.
BASELINE_UNDEFINED = "undefined/0-build-cost"


class BudgetGovernorError(ValueError):
    """A TYPED malformed-accounting-input failure (AR10).

    A ``ValueError`` subclass localized to this module (mirroring
    ``RepoIntakeError`` / ``DepthSemanticsError`` / ``PartitionerError`` /
    ``CriticalSubsystemError``). Raised on a ``float`` contribution, a negative
    ceiling, a negative or non-``int`` credit, or a non-mapping contributions arg —
    never a silent coerce / bare ``except`` / ``print()`` in library code. The
    message names the offending key/type only — never source / secret bytes.
    """


def _require_non_negative_int(value: object, *, label: str) -> int:
    """Return ``value`` if it is a non-negative ``int`` (not ``bool``); else raise.

    ``bool`` is rejected even though it is an ``int`` subclass (a flag is not a
    credit). A ``float`` is rejected outright (AR4 — no float money). The typed
    failure is :class:`BudgetGovernorError` (AR10).
    """
    if isinstance(value, bool):
        raise BudgetGovernorError(f"{label} must be a non-negative int, got bool")
    if isinstance(value, float):
        raise BudgetGovernorError(
            f"{label} must be a non-negative int, got float (AR4 — no float money)"
        )
    if not isinstance(value, int):
        raise BudgetGovernorError(
            f"{label} must be a non-negative int, got {type(value).__name__}"
        )
    if value < 0:
        raise BudgetGovernorError(f"{label} must be a non-negative int, got {value}")
    return value


class BudgetConfig(BaseModel):
    """Frozen budget-ceiling configuration (FR21 / OI3 / NFR-M2).

    ``ceiling_credits is None`` is the FIRST-CLASS "no ceiling configured" state
    (the OI3 default — admit everything; accounting still runs + reports). A
    positive ``int`` is the configured ceiling. NEVER a ``float`` (AR4); NEVER a
    hardcoded numeric default (OI3 — the ``$X`` default is Story 7.1). Construct
    via :func:`budget_config_from_budget` (``budget == 0 → None``).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=BUDGET_SCHEMA_VERSION,
        description="BudgetConfig schema version (localized constant; additive-only).",
    )
    ceiling_credits: int | None = Field(
        default=None,
        description=(
            "Configured ceiling in int credits, or None for no ceiling (OI3 — "
            "first-class no-ceiling; NEVER a hardcoded numeric default)."
        ),
    )


def budget_config_from_budget(budget: int) -> BudgetConfig:
    """Map the reserved ``AuditRequest.budget`` field to a :class:`BudgetConfig`.

    The OI3 rule expressed in code: ``budget == 0`` (the CLI default / an omitted
    budget) → ``ceiling_credits = None`` (NO ceiling — admit everything), a
    positive ``budget`` → that ``int`` ceiling. There is NO numeric default. The
    ``budget`` field's existing ``ge=0`` model validation already rejects a
    negative value with a typed ``ValidationError`` upstream; this function defends
    the same invariant (a non-``int`` / negative budget → :class:`BudgetGovernorError`)
    so a direct call is total-safe (AR10).
    """
    value = _require_non_negative_int(budget, label="budget")
    return BudgetConfig(ceiling_credits=None if value == 0 else value)


class CostLedger(BaseModel):
    """Frozen cost ledger / report — the whole accounting outcome (FR21 / NFR-M2).

    ALL fields are ``int`` / ``Fraction`` / ``bool`` / ``str`` — NO ``float``
    anywhere (the canonical serializer rejects it; the persisted snapshot is the
    NFR-P1 byte-stable artifact). The per-axis ``breakdown`` is a sorted-key
    mapping of ``int`` work-unit counts (the V1 deterministic contributions). The
    ``ceiling_reached`` flag is the EXPLICIT, typed surface Story 3.2 queries to
    decide the mid-run halt — this story EXPOSES it but does NOT act on it (no
    halt / no ``skipped`` marking here). The ``baseline_ratio`` is the NFR-C1
    measured ratio (a reduced ``Fraction``, or :data:`BASELINE_UNDEFINED` when the
    build-cost proxy is 0). No volatile ``run_id`` / ``created_at`` (NFR-D3).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=COST_SCHEMA_VERSION,
        description="CostLedger schema version (localized constant; additive-only).",
    )
    total_credits: int = Field(
        ..., ge=0, description="Accumulated cost in int credits (NEVER float — AR4)."
    )
    ceiling_credits: int | None = Field(
        default=None,
        description="The configured ceiling (None = no ceiling), echoed for provenance.",
    )
    ceiling_reached: bool = Field(
        ...,
        description=(
            "True when total_credits is at/over the ceiling (the REUSED >=-is-a-breach "
            "decision). Deterministically False when no ceiling. Story 3.2 queries this."
        ),
    )
    breakdown: dict[str, int] = Field(
        default_factory=dict,
        description="Per-axis int work-unit counts (the V1 deterministic contributions).",
    )
    baseline_ratio: Fraction | str = Field(
        ...,
        description=(
            "NFR-C1 measured baseline: total_credits / build_cost_proxy as a reduced "
            "Fraction, or the BASELINE_UNDEFINED marker when the proxy is 0 (total-safe)."
        ),
    )

    @field_validator("baseline_ratio", mode="before")
    @classmethod
    def _coerce_baseline(cls, value: Any) -> Any:
        """Reconstruct a LIVE ``Fraction`` from its canonical ``"num/den"`` string.

        The persisted payload encodes the baseline ratio through the single 1.1
        canonical serializer, which renders ``Fraction → "num/den"``. On read-back
        this turns that canonical string BACK into a ``Fraction`` so the round-trip
        reconstructs an EQUAL model (NFR-P1) — a plain ``Fraction | str`` union would
        otherwise keep the string form and break model equality. The non-ratio
        :data:`BASELINE_UNDEFINED` marker (no ``"/"``) is passed through as a ``str``.
        A live ``Fraction`` is passed through unchanged.
        """
        if isinstance(value, str) and "/" in value:
            try:
                return Fraction(value)
            except (ValueError, ZeroDivisionError):
                return value
        return value

    def to_canonical_payload(self) -> dict[str, object]:
        """Build a canonical-safe payload with LIVE ``Fraction`` leaves (1.6/2.2 precedent).

        Pydantic's ``model_dump`` would coerce a ``Fraction`` via ``str``
        (``Fraction(1, 1) → "1"``), diverging from the LOCKED canonical
        ``Fraction → "num/den"`` encoding. So the persisted snapshot is built here
        with the LIVE ``Fraction`` (or the ``str`` marker) handed straight to the
        single 1.1 ``canonical`` serializer, which applies its frozen ``num/den``
        encoding. Routing the snapshot through THIS payload keeps the on-disk bytes
        byte-stable AND round-trip-equal via the ``_coerce_baseline`` validator. All
        leaves are ``int`` / ``Fraction`` / ``bool`` / ``str`` — never ``float``
        (AR4), never an absolute path / source / secret byte (NFR-S1).
        """
        return {
            "schema_version": self.schema_version,
            "total_credits": self.total_credits,
            "ceiling_credits": self.ceiling_credits,
            "ceiling_reached": self.ceiling_reached,
            "breakdown": dict(self.breakdown),
            "baseline_ratio": self.baseline_ratio,
        }


def _coerce_breach(*, total_credits: int, ceiling_credits: int | None) -> bool:
    """The breach decision, REUSED from ``BudgetGuardrails`` BY IMPORT (AR7 / §3.3).

    When ``ceiling_credits is None`` → no ceiling → admit everything → ``False``
    (the NFR-C1 baseline still records the total). Otherwise ArgusAgent maps its ``int``
    ``total_credits`` onto the SAME D3 ``>=``-is-a-breach hard-ceiling comparison
    the Minions ``BudgetGuardrails.evaluate_worker_spend`` encodes
    (``within = credits_consumed < max_worker_credits``), by constructing a
    ``BudgetPolicy`` whose ``max_worker_credits`` IS the configured ceiling and
    reading ``within_budget``. ``ceiling_reached = not within_budget`` ⇒ the exact
    at-ceiling boundary (``total == ceiling``) is a breach. There is NO fork and NO
    parallel comparison — the Minions guardrails are the single hard-ceiling
    authority. The ``float`` the policy carries internally never leaves this
    function; the ArgusAgent-visible result is a ``bool`` over ``int`` inputs.
    """
    if ceiling_credits is None:
        return False
    guardrails = BudgetGuardrails(BudgetPolicy(max_worker_credits=ceiling_credits))
    evaluation = guardrails.evaluate_worker_spend(total_credits)
    return not evaluation["within_budget"]


def baseline_ratio(total_credits: int, build_cost_proxy: int) -> Fraction | str:
    """The NFR-C1 baseline ratio — audit cost / build-cost proxy (measured, reported).

    Returns an EXACT reduced ``Fraction`` (never a ``float`` — the 2.1/2.2/2.5
    precedent) of ``total_credits / build_cost_proxy``, the audit's cost as a
    fraction of the audited repo's build-cost proxy (V1: a deterministic
    content-derived proxy — total physical LOC from the existing ``compute_loc_by_file``
    map). V1 MEASURES and REPORTS this; it does NOT assert / gate on the ≤10–20%
    target (a post-V1 goal). A degenerate ``build_cost_proxy == 0`` (an empty repo)
    is total-safe — it returns the :data:`BASELINE_UNDEFINED` marker, NEVER a
    divide-by-zero / ``float('inf')`` (the 1.6 ``total == 0`` floor-first guard).
    """
    total = _require_non_negative_int(total_credits, label="total_credits")
    proxy = _require_non_negative_int(build_cost_proxy, label="build_cost_proxy")
    if proxy == 0:
        return BASELINE_UNDEFINED
    return Fraction(total, proxy)


def account_spend(
    contributions: Mapping[str, int],
    *,
    config: BudgetConfig,
    build_cost_proxy: int,
) -> CostLedger:
    """PURE fold of per-axis ``int`` contributions into a :class:`CostLedger` (AC2).

    ``contributions`` is a mapping of per-axis work-unit credit counts (the V1
    deterministic, zero-token contributions — e.g. ``{"files_indexed": 12,
    "tool_invocations": 3, "detector_passes": 9}``). Each value is folded into a
    running ``int`` ``total_credits``; the breach/admission decision is the REUSED
    ``BudgetGuardrails`` ``>=``-is-a-breach hard-ceiling decision when a ceiling is
    configured, else admit-everything (see :func:`_coerce_breach`). The NFR-C1
    baseline ratio is computed against ``build_cost_proxy``.

    PURE (AR8): no filesystem I/O, no clock, no ``uuid``/``random``, no LLM/network,
    no dict/``set``-iteration-order reliance — the total is a sum (order-independent)
    and the ``breakdown`` is rebuilt as an explicit mapping, so the same
    contributions + config yield a BYTE-IDENTICAL ledger across hosts/runs and
    across input orderings (NFR-P1). A malformed contribution (a ``float`` /
    negative / non-``int`` credit, a non-mapping arg) raises
    :class:`BudgetGovernorError` (AR10) — never a silent coerce.
    """
    if not isinstance(contributions, Mapping):
        raise BudgetGovernorError(
            f"contributions must be a mapping, got {type(contributions).__name__}"
        )

    breakdown: dict[str, int] = {}
    total = 0
    for axis, credits in contributions.items():
        if not isinstance(axis, str):
            raise BudgetGovernorError(
                f"contribution axis must be str, got {type(axis).__name__}"
            )
        amount = _require_non_negative_int(credits, label=f"contribution {axis!r}")
        breakdown[axis] = amount
        total += amount

    ceiling = config.ceiling_credits
    return CostLedger(
        total_credits=total,
        ceiling_credits=ceiling,
        ceiling_reached=_coerce_breach(total_credits=total, ceiling_credits=ceiling),
        breakdown=breakdown,
        baseline_ratio=baseline_ratio(total, build_cost_proxy),
    )
