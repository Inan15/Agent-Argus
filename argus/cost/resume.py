"""PURE resume-plan core — which prior coverage to carry forward vs re-audit (FR31).

Drivers: ArgusAgent-FR-31 (ArgusAgent resumes an interrupted audit from its on-disk ``.argus/``
state — this module is the deterministic resume PLAN: given the prior coverage
ledger + the prior halt report + the current ``repo@commit`` index + the RAISED
budget config, it computes which files are already covered [``audited_deep``
carried forward verbatim] and which remaining units are the resume target,
re-projecting a fresh halt over the remainder against the raised ceiling),
ArgusAgent-NFR-R2 (an interrupted audit is fully resumable from on-disk ``.argus/`` state
with NO loss of prior coverage — the carried-forward set is reused, never
re-audited), ArgusAgent-NFR-D2 (deterministic, zero-LLM-token — the plan is a pure fold
over the loaded records + the current index), ArgusAgent-NFR-P1 (byte-stable +
order-independent — the carried-forward / resume-target / still-skipped sets are
sorted, content-derived; no ``float``; the full host-vs-host proof is Story 3.5),
ArgusAgent-NFR-S1 (no source / secret / absolute-host-path bytes — the plan carries only
repo-relative POSIX paths + ``int``/``bool`` provenance), ArgusAgent-NFR-M2 (frozen,
additive-only contract), AR4 (no ``float``; counts ``int`` / flags ``bool`` /
paths ``str`` / sets sorted ``tuple[str, ...]``; single canonical serializer),
AR7 (reuse the 3-2 ``project_halt_point`` BY IMPORT to re-project the halt over the
remainder — no fork, §3.3), AR8 (pure/impure separation — this module is the PURE
plan builder over in-memory loaded records; the state READ + the resumed-artifact
WRITE are the impure pipeline shell), AR10 (typed failure — a divergent
tree/commit [a carried-forward path absent from the current index] raises the typed
:class:`ResumeError`, never a silent mis-merge), AR11 (the plan sets are sorted /
content-derived, never arrival order).

Why this module exists (the resume PLAN is the net-new — the rest is composition)
--------------------------------------------------------------------------------
Stories 1.3 / 3.2 / 1.6 already built everything a resume reads WITH and folds:
the 1.3 ``ApaaStoreReader`` + ``StoreIntegrityError`` tamper guard (the READ), the
3.2 ``project_halt_point`` (the halt), the 1.6 ``evaluate_verdict`` (the verdict).
The genuinely NEW deliverable is the resume PLAN: a small additive frozen record +
a pure fold that decides which prior coverage to carry forward verbatim vs which
remainder to continue auditing under the RAISED budget. This module is that fold
and NOTHING ELSE — it builds no reader, no tamper check, no verdict math, no I/O.

The pure resume fold (deterministic, no I/O — the AR8 boundary)
---------------------------------------------------------------
``build_resume_plan(prior_ledger, prior_halt_report, current_index_units,
raised_config)``:
  1. CARRIED-FORWARD = EVERY prior-ASSESSED path (the halt report's
     ``assessed_files`` — deep, shallow, tool_scanned_only, AND assessed-but-skipped
     alike), sorted — reused VERBATIM (NFR-R2 "no loss of prior coverage"); these are
     NOT re-audited. Carrying forward only the ``audited_deep`` subset would silently
     drop the assessed-non-deep coverage and break the AC2 byte-identity keystone.
  2. CONSISTENCY (the V1 divergence guard, AR10): every carried-forward path MUST
     exist in ``current_index_units`` — a prior-state path absent from the current
     index means the tree/commit diverged from the prior run, so the resume RAISES
     :class:`ResumeError` (never a silent mis-merge). The full referential-integrity
     lint is Story 4.2; this is the minimal consistency anchor.
  3. REMAINDER = the prior halt report's ``skipped_on_exhaustion_files`` — the units
     the prior budget could not reach.
  4. RE-PROJECT the halt over the remainder against the RAISED ceiling via the 3-2
     ``project_halt_point`` (BY IMPORT — no fork). The already-spent prior credits
     are accounted as a SEED unit so the resume CONTINUES rather than re-spends
     (the raised ceiling is a TOTAL budget, not a fresh allowance). The resume
     target = the assessed remainder; the still-skipped = the remainder the raised
     budget still cannot reach.
  5. ``halts_again = bool(still_skipped)`` — an honest second partial run (AC4).

The result is deterministic + order-independent: two input orderings of the SAME
units yield the identical plan (every set is sorted; the halt projection is itself
order-independent). NO ``float``; NO clock; NO uuid/random; NO LLM/network.

Scope fences (NOT pulled forward — see Story 3.4)
-------------------------------------------------
- The content-addressed memoization cache (NFR-D1) → Epic 5. Resume reuses the
  on-disk LEDGER, NOT a memo-cache hit; this module builds no cache key / memo store.
- The host-vs-host byte-identical parity proof (FR32/NFR-P1) → Story 3.5. This
  module's output is byte-deterministic + order-independent; the full host parity
  proof is 3.5.
- The referential-integrity lint of ``.argus/`` state (FR26/NFR-A2) → Story 4.2.
  This module asserts only the minimal carried-forward-paths-exist consistency
  anchor; the full dangling-reference / prev-hash-chain walk is 4.2.

Test area ArgusAgent-COST (``TC-ArgusAgent-COST-001-NN``) — continuing the 3-1/3-2/3-3 cost area.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from argus.cost.budget_governor import BudgetConfig
from argus.cost.exhaustion import CostUnit, project_halt_point
from argus.ledger.coverage_ledger import CoverageLedger

__all__ = [
    "RESUME_PLAN_SCHEMA_VERSION",
    "ResumeError",
    "ResumePlan",
    "build_resume_plan",
]

# Localized schema version (additive-only; never env / clock — NFR-M2).
RESUME_PLAN_SCHEMA_VERSION = "1"


class ResumeError(ValueError):
    """A TYPED malformed / inconsistent resume-input failure (AR10).

    A ``ValueError`` subclass localized to this module (mirroring
    ``ExhaustionError`` / ``BudgetGovernorError`` / ``PipelineError``). Raised on a
    divergent tree/commit (a carried-forward ``audited_deep`` path absent from the
    current index — the V1 divergence guard), a non-``CoverageLedger`` /
    non-``HaltReport`` argument, or a malformed unit set — never a silent coerce /
    silent mis-merge / bare ``except`` / ``print()`` in library code. The message
    names the offending RELATIVE path / type only — never source / secret bytes
    (NFR-S1).
    """


class ResumePlan(BaseModel):
    """Frozen deterministic resume plan — carry-forward vs resume-target split (FR31).

    ``frozen=True, extra="forbid"`` (the 1.1/1.2/1.6/3.1/3.2 precedent), localized
    :data:`RESUME_PLAN_SCHEMA_VERSION`. Records EVERY prior-ASSESSED path (all depths)
    reused verbatim, the remainder to audit now (bounded by the RAISED ceiling), the
    remainder the raised budget STILL cannot cover, and the spend/ceiling provenance.
    ALL leaves are ``int`` / ``bool`` / ``str`` / sorted ``tuple[str, ...]`` — NO
    ``float`` anywhere (AR4; the canonical serializer is the determinism backstop),
    NO volatile ``run_id`` / ``created_at`` (NFR-D3), NO absolute host path / source
    / secret byte (only repo-relative POSIX paths — NFR-S1).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=RESUME_PLAN_SCHEMA_VERSION,
        description="ResumePlan schema version (localized constant; additive-only).",
    )
    carried_forward_paths: tuple[str, ...] = Field(
        default=(),
        description=(
            "Sorted repo-relative paths reused VERBATIM (EVERY prior-ASSESSED entry — "
            "deep, shallow, tool_scanned_only, AND assessed-but-skipped alike; NOT "
            "re-audited). The authoritative assessed set is the prior halt report's "
            "assessed_files (NFR-R2 'no loss of prior coverage')."
        ),
    )
    resume_target_paths: tuple[str, ...] = Field(
        default=(),
        description="Sorted repo-relative paths of the remainder to audit now (within the raised ceiling).",
    )
    still_skipped_paths: tuple[str, ...] = Field(
        default=(),
        description="Sorted repo-relative paths the raised budget STILL cannot cover (empty when complete).",
    )
    prior_total_credits: int = Field(
        ..., ge=0, description="The int spend already reached by the prior run (continued, not re-spent)."
    )
    raised_ceiling_credits: int | None = Field(
        default=None, description="The RAISED ceiling (None = no ceiling), echoed for provenance."
    )
    halts_again: bool = Field(
        ..., description="True iff the raised budget still cannot cover the entire remainder (AC4)."
    )

    def to_canonical_payload(self) -> dict[str, object]:
        """Canonical-safe payload (all leaves int/bool/str/tuple[str] — no Fraction).

        ``model_dump(mode="json")`` already renders every leaf to a canonical-safe
        JSON primitive (tuples → lists, ``None`` → null); there is no ``Fraction``
        leaf so no LIVE-``Fraction`` re-install is needed. Provided for call-site
        symmetry with the 3-1/3-2 snapshots and to keep the shape explicit.
        """
        return self.model_dump(mode="json")


def _require_ledger(value: object) -> CoverageLedger:
    if not isinstance(value, CoverageLedger):
        raise ResumeError(
            f"build_resume_plan requires a CoverageLedger prior_ledger, got "
            f"{type(value).__name__}"
        )
    return value


def build_resume_plan(
    prior_ledger: CoverageLedger,
    prior_halt_report: object,
    current_index_units: tuple[CostUnit, ...] | list[CostUnit],
    raised_config: BudgetConfig,
) -> ResumePlan:
    """Fold the loaded prior records + the current index + the raised config → plan (PURE, AC1/4).

    PURE (AR8): no I/O, no clock, no ``uuid``/``random``, no LLM/network, no
    ``float``. Same inputs → byte-identical plan (NFR-P1). Deterministic +
    order-independent — the carried-forward / resume-target / still-skipped sets are
    sorted, and the halt re-projection is itself order-independent.

    Carried-forward = EVERY prior-ASSESSED path (the halt report's ``assessed_files``,
    all depths — reused VERBATIM, NFR-R2). Every carried-forward path MUST exist in
    ``current_index_units`` — a
    divergent tree/commit raises the typed :class:`ResumeError` (AR10 — never a
    silent mis-merge; the full referential-integrity lint is Story 4.2). The resume
    target is the prior ``skipped_on_exhaustion`` remainder re-projected through the
    REUSED 3-2 ``project_halt_point`` against the RAISED ceiling, accounting for the
    already-spent ``prior_total_credits`` as a SEED unit so the resume CONTINUES
    rather than re-spends (the raised ceiling is a TOTAL budget). ``still_skipped`` =
    the remainder the raised budget still cannot reach; ``halts_again`` = whether any
    remainder remains skipped (AC4).
    """
    ledger = _require_ledger(prior_ledger)
    # Duck-typed read of the 3-2 HaltReport (avoid a hard import cycle / a tight
    # isinstance fence on an evolving sibling — the fields are the contract). A
    # missing field is a typed ResumeError, never an AttributeError traceback.
    assessed = getattr(prior_halt_report, "assessed_files", None)
    skipped = getattr(prior_halt_report, "skipped_on_exhaustion_files", None)
    prior_credits = getattr(prior_halt_report, "total_credits", None)
    if assessed is None or skipped is None or prior_credits is None:
        raise ResumeError(
            f"build_resume_plan requires a HaltReport prior_halt_report, got "
            f"{type(prior_halt_report).__name__}"
        )
    if not isinstance(prior_credits, int) or isinstance(prior_credits, bool) or prior_credits < 0:
        raise ResumeError("prior halt report total_credits must be a non-negative int")

    units = tuple(current_index_units)
    units_by_path: dict[str, CostUnit] = {}
    for index, unit in enumerate(units):
        if not isinstance(unit, CostUnit):
            raise ResumeError(
                f"current_index_units[{index}] must be a CostUnit, got {type(unit).__name__}"
            )
        units_by_path[unit.path] = unit

    # Carry forward EVERY prior-ASSESSED entry verbatim (NFR-R2 "no loss of prior
    # coverage") — the prior halt report's assessed_files is the authoritative
    # assessed set across ALL depths (audited_deep, audited_shallow,
    # tool_scanned_only, AND assessed-but-skipped). Carrying forward only the
    # audited_deep entries silently drops the assessed-non-deep coverage and breaks
    # the AC2 byte-identity keystone (a resumed run would NOT equal an uninterrupted
    # run of the equivalent budget). The prior ledger holds the verbatim entries for
    # these paths; the pipeline reuses them by file_path (the same frozen entries).
    carried_forward = tuple(sorted(str(p) for p in assessed))
    known_paths = frozenset(entry.file_path for entry in ledger.entries)
    for path in carried_forward:
        if path not in units_by_path:
            raise ResumeError(
                f"carried-forward assessed path '{path}' is absent from the current "
                f"index — the tree/commit diverged from the prior run; refusing to resume "
                f"(re-run a fresh audit on the current commit)"
            )
        if path not in known_paths:
            raise ResumeError(
                f"prior halt report assessed path '{path}' has no entry in the prior "
                f"coverage ledger — the prior .argus/ state is inconsistent; refusing to resume"
            )

    remainder_paths = tuple(sorted(str(p) for p in skipped))
    for path in remainder_paths:
        if path not in units_by_path:
            raise ResumeError(
                f"prior skipped-on-exhaustion path '{path}' is absent from the current "
                f"index — the tree/commit diverged from the prior run; refusing to resume"
            )

    # Re-project the halt over the remainder against the RAISED ceiling, seeding the
    # already-spent prior credits so the resume CONTINUES (the raised ceiling is a
    # TOTAL budget, not a fresh allowance). The seed is a sentinel unit sorted ahead
    # of every remainder path (the empty string sorts first) so it is admitted first
    # and the remainder is projected against the running total INCLUDING prior spend.
    _SEED_PATH = ""
    remainder_units: list[CostUnit] = [
        CostUnit(path=_SEED_PATH, cost=prior_credits)
    ]
    remainder_units.extend(units_by_path[path] for path in remainder_paths)
    projection = project_halt_point(remainder_units, config=raised_config)

    resume_assessed = tuple(
        sorted(p for p in projection.assessed_paths if p != _SEED_PATH)
    )
    still_skipped = tuple(
        sorted(p for p in projection.skipped_paths if p != _SEED_PATH)
    )

    return ResumePlan(
        carried_forward_paths=carried_forward,
        resume_target_paths=resume_assessed,
        still_skipped_paths=still_skipped,
        prior_total_credits=prior_credits,
        raised_ceiling_credits=raised_config.ceiling_credits,
        halts_again=bool(still_skipped),
    )
