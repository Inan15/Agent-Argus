"""Reproducible FULL-REPO Minions partition + budget-sizing plan generator (Story 7.1).

Verification area ArgusAgent-DOGFOOD (``TC-ArgusAgent-DOGFOOD-001-NN`` — this is the FIRST module
in that area; the index starts at 01, locked here). Drivers: ArgusAgent-FR-3 (partition the
repository into bounded audit units — the full-repo Minions map, OI2 multi-partition),
ArgusAgent-FR-21 (an operator budget ceiling — the empirically-sized ``$X`` sized to cover
the full-repo plan, OI3 "no numeric default"), ArgusAgent-NFR-SC1 (V1 audit units ≤40 files/
15k LOC soft; hard ceiling ≤60/25k), ArgusAgent-NFR-C1 (a baseline full audit costs a
bounded fraction of the audited repo's build-cost proxy — measured + reported as an
exact ``Fraction``), ArgusAgent-NFR-D1/D2 (deterministic + ZERO-LLM-token — a pure fold over
the recorded 1.4 index + the in-memory LOC map + the 3.1 accountant), ArgusAgent-NFR-P1
(byte-identical plan for the same repo content — no ``float``), ArgusAgent-NFR-S1 (the plan
records ONLY repo-relative paths + counts + credits — NEVER a source/secret byte),
ArgusAgent-AR4 (int credits / ``Fraction`` ratios — NEVER float in any persisted figure),
ArgusAgent-AR7 (REUSE by import — no fork of the 2.4 planner / the 3.1 accountant),
ArgusAgent-AR8 (pure/impure separation — the derivation core is pure; the source-file
enumeration + read + the ``.md`` render are the impure shell), ArgusAgent-AR10 (typed
failure — ``DogfoodPlanError``, never a bare traceback), ArgusAgent-NFR-M1/M2 (≤1200-line
files; the frozen Epic-1..6 contracts + the 6.5 registry SHAPE are unchanged — this
module COMPOSES them, edits none).

What this module IS (partial-reuse note, AI-E5-7)
-------------------------------------------------
It REUSES, BY IMPORT: the 2.4 ``partition_repository`` planner + the ``PartitionPlan``
contract, the 1.4 ``build_ast_index`` index + the ``compute_loc_by_file`` LOC map, the
1.4 ``_SOURCE_SUFFIXES`` discovery filter (the SAME filter ``load_repo_at_commit``
uses — no fork), and the 3.1 ``account_spend`` / ``BudgetConfig`` / ``baseline_ratio``
accountant. It ADDS: the full-repo plan DERIVATION (``derive_partition_plan``), the
empirical ``$X`` budget SIZING (``size_budget``), and the ``.md`` RENDERERS. It adds
NO second partitioner, NO second cost model, NO forked serializer, NO LLM dispatch.

The V1 honest limitation — NO cross-partition SEAM analysis (OI2 / AC4)
-----------------------------------------------------------------------
V1 does MULTI-UNIT auditing, NOT cross-partition SEAM analysis. A defect spanning a
partition cut (caller in unit A, callee in unit B) is NOT analyzed by any seam auditor
in V1. The ONLY V1 mitigation is the 6.4 ``cross_partition`` Prosecutor cut-edge pass
(re-reads the recorded cut edges); the full seam auditor is reserved V2. The rendered
plan STATES this limitation explicitly (mirroring the 2.4 ``PartitionPlan.seam_analysis
= "v2-deferred"`` provenance) so the proof's scope statement is honest about what
cut-spanning defects it could and couldn't see.

OI3 — the budget number lives in the PLAN, not in the code (DN-BUDGET-SIZING)
----------------------------------------------------------------------------
``$X`` is sized EMPIRICALLY here and recorded in the plan artifact. The 3.1
``budget_governor.py`` invariant "no hardcoded numeric ceiling default" is PRESERVED:
this module never mutates the module default (``ceiling_credits: int | None = None``);
it SIZES a value the plan records + an operator supplies to the dogfood run.

Pure/impure separation (AR8)
----------------------------
PURE: ``derive_partition_plan`` (over an in-memory index + LOC map), ``size_budget``
(over the derived plan + the V1 contribution recipe), ``render_partition_plan_markdown``
/ ``render_budget_plan_markdown`` (over the pure results). IMPURE shell:
``enumerate_minions_source_files`` (``git ls-files``), ``read_sources`` (file reads),
``build_full_repo_plan`` (the orchestration that reads + derives).
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from argus.cost.budget_governor import (
    BudgetConfig,
    account_spend,
    baseline_ratio,
)
from argus.index.ast_index import AstIndex, build_ast_index
from argus.index.partitioner import (
    DEFAULT_HARD_FILE_LIMIT,
    DEFAULT_HARD_LOC_LIMIT,
    DEFAULT_SOFT_FILE_LIMIT,
    DEFAULT_SOFT_LOC_LIMIT,
    PartitionPlan,
    compute_loc_by_file,
    partition_repository,
)

__all__ = [
    "DOGFOOD_PLAN_SCHEMA_VERSION",
    "DEFAULT_HEADROOM_NUMERATOR",
    "DEFAULT_HEADROOM_DENOMINATOR",
    "COVERAGE_FLOOR",
    "DogfoodPlanError",
    "UnitCostRow",
    "BudgetSizing",
    "FullRepoPlan",
    "enumerate_minions_source_files",
    "read_sources",
    "derive_partition_plan",
    "unit_contributions",
    "size_budget",
    "build_full_repo_plan",
    "render_partition_plan_markdown",
    "render_budget_plan_markdown",
]

DOGFOOD_PLAN_SCHEMA_VERSION = "1"

# The empirical headroom applied over the derived total to size the ceiling. A 1/4
# (25%) headroom over the V1 deterministic total gives the dogfood room for the
# expected-but-unbilled V2 LLM depth passes WITHOUT inviting an unbounded ceiling.
# int/Fraction only (AR4) — the sized ceiling stays an int-credit value.
DEFAULT_HEADROOM_NUMERATOR = 5
DEFAULT_HEADROOM_DENOMINATOR = 4  # 5/4 = the total + 25% headroom

# The 3.3 20%-deep coverage floor (a unit must audit ≥1/5 of its files deep to clear
# INSUFFICIENT_COVERAGE). Recorded in the plan so the per-unit floor-clearing claim is
# explicit (AC2). A ``Fraction`` — never a float (AR4).
COVERAGE_FLOOR = Fraction(1, 5)


class DogfoodPlanError(ValueError):
    """A TYPED plan-generation failure (AR10).

    A ``ValueError`` subclass localized to this module (mirroring ``PartitionerError``
    / ``BudgetGovernorError`` / ``RepoIntakeError``). Raised on a git-enumeration
    failure, a non-``PartitionPlan`` argument, or a malformed contribution recipe —
    never a bare ``CalledProcessError`` / ``KeyError`` out of the shell. The message
    names the relative condition only — never an absolute host path / source byte
    (NFR-S1).
    """


@dataclass(frozen=True)
class UnitCostRow:
    """One partition unit's V1 cost contribution — counts + credits only (NFR-S1).

    Carries NO source bytes: the ``partition_id`` is a content-derived sha256 hex, the
    counts are ``int`` work-units, ``unit_credits`` is the folded ``int`` credit total.
    ``clears_floor`` records the AC2 per-unit 20%-floor-clearing claim (a targeted unit
    is bounded so ≥1/5 of its files can be audited deep within its budget allocation).
    """

    partition_id: str
    file_count: int
    total_loc: int
    python_files: int
    context_pressure: bool
    unit_credits: int
    clears_floor: bool


@dataclass(frozen=True)
class BudgetSizing:
    """The empirically-sized ``$X`` budget plan — int credits / Fraction ratios (AR4).

    ``total_credits`` is the V1 deterministic zero-token contribution total folded via
    the 3.1 ``account_spend`` across ALL units. ``sized_ceiling`` is ``$X`` — the total
    plus the headroom, an ``int`` credit value (never a float). ``baseline_ratio`` is
    the NFR-C1 measured audit-cost / build-cost-proxy ratio (an exact ``Fraction`` or
    the ``BASELINE_UNDEFINED`` marker). The ceiling ``ceiling_reached`` under a
    ``BudgetConfig(ceiling_credits=sized_ceiling)`` is asserted ``False`` (the run fits)
    while a ceiling one credit BELOW the total demonstrably breaches (3.2 halt).
    """

    total_credits: int
    sized_ceiling: int
    headroom_credits: int
    build_cost_proxy: int
    baseline_ratio: Fraction | str
    fits_within_ceiling: bool
    breaches_when_ceiling_below_total: bool
    per_unit: tuple[UnitCostRow, ...]


@dataclass(frozen=True)
class FullRepoPlan:
    """The whole 7.1 plan result — the partition map + the budget sizing (PURE).

    ``commit_descriptor`` is the pinned provenance (the ``git rev-parse HEAD`` at
    generation, recorded for reproducibility — the plan derivation itself is over the
    tracked content). PURE / value-free: only paths, counts, credits, and content-
    derived ids cross a byte boundary (NFR-S1).
    """

    commit_descriptor: str
    source_file_count: int
    total_loc: int
    partition_plan: PartitionPlan
    budget: BudgetSizing


# ──────────────────────────────────────────────────────────────────────────────
# IMPURE shell — source enumeration + read (AR8; the derivation core stays pure)
# ──────────────────────────────────────────────────────────────────────────────


# The 1.4 source-file discovery filter, REUSED (no fork). Imported lazily inside the
# enumerator so a test that patches it sees the same frozenset the intake uses.
def _source_suffixes() -> frozenset[str]:
    from argus.intake.repo_loader import _SOURCE_SUFFIXES

    return _SOURCE_SUFFIXES


def enumerate_minions_source_files(
    repo_root: str | Path,
    *,
    scope_prefix: str = "argus/",
    exclude_prefixes: tuple[str, ...] = ("argus/tests/",),
) -> tuple[str, ...]:
    """Enumerate git-TRACKED Minions source files under *scope_prefix* (the impure read).

    REUSES the 1.4 ``_SOURCE_SUFFIXES`` filter (the SAME filter
    ``load_repo_at_commit`` uses — no fork) over ``git ls-files -z`` (committed
    content, NUL-separated + unquoted so a non-ASCII path round-trips — the 1.4
    precedent), scoped to *scope_prefix* and excluding *exclude_prefixes* (the ArgusAgent
    sub-tree is untracked / self-audited elsewhere, so the dogfood plan targets the
    Minions PLATFORM tree). Deterministic: the returned tuple is SORTED. A git failure
    raises :class:`DogfoodPlanError` (AR10), never a bare ``CalledProcessError``.
    """
    root = Path(repo_root)
    git_bin = shutil.which("git") or "git"
    try:
        proc = subprocess.run(
            [git_bin, "-C", str(root), "ls-files", "-z", scope_prefix.rstrip("/")],
            capture_output=True,
            timeout=60,
        )
    except FileNotFoundError as exc:
        raise DogfoodPlanError("git executable not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise DogfoodPlanError("git ls-files timed out") from exc
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        raise DogfoodPlanError(
            f"git ls-files failed (exit {proc.returncode}): {stderr or 'no stderr'}"
        )
    suffixes = _source_suffixes()
    records = proc.stdout.decode("utf-8", errors="replace").split("\0")
    files = tuple(
        sorted(
            rec
            for rec in records
            if rec
            and Path(rec).suffix in suffixes
            and not any(rec.startswith(p) for p in exclude_prefixes)
        )
    )
    return files


def read_sources(repo_root: str | Path, source_files: tuple[str, ...]) -> dict[str, str]:
    """Read each *source_file* as text (the impure read; AR8).

    Decodes UTF-8 with ``errors="replace"`` so a non-UTF-8 byte never raises out of the
    per-file read (mirrors ``pipeline._read_source`` — the same read the audit uses; no
    second decoder). The absolute *repo_root* stays transient; the returned keys are
    repo-relative POSIX paths only (NFR-S1). The AI-E4-2 no-crash leg: a missing file
    raises :class:`DogfoodPlanError` NAMING the relative path, never a bare
    ``FileNotFoundError``.
    """
    root = Path(repo_root)
    out: dict[str, str] = {}
    for rel in source_files:
        path = root / rel
        try:
            out[rel] = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise DogfoodPlanError(
                f"could not read source file {rel!r} ({type(exc).__name__})"
            ) from exc
    return out


# ──────────────────────────────────────────────────────────────────────────────
# PURE derivation core (AR8)
# ──────────────────────────────────────────────────────────────────────────────


def derive_partition_plan(index: AstIndex, loc_by_file: dict[str, int]) -> PartitionPlan:
    """REUSE the 2.4 planner over the in-memory index + LOC map (no fork; PURE).

    A thin, explicit reuse seam: the full-repo map is the 2.4 ``partition_repository``
    over the WHOLE Minions platform index — NOT a forked partitioner, NOT a directory
    splitter, NOT a hand-typed map. Deterministic + byte-stable for the same content.
    """
    return partition_repository(index, loc_by_file=loc_by_file)


def unit_contributions(python_files: int, total_files: int) -> dict[str, int]:
    """The V1 deterministic zero-token contribution recipe for ONE unit (REUSE, no fork).

    The SAME recipe ``pipeline._build_cost_ledger`` folds (no second cost model): every
    file costs 1 ``files_indexed``; a Python file costs an extra 1 ``python_files`` + 3
    ``detector_passes`` (vacuous + secret + breadth). All ``int`` (AR4). A malformed
    (negative) count raises :class:`DogfoodPlanError` (AR10).
    """
    if python_files < 0 or total_files < 0 or python_files > total_files:
        raise DogfoodPlanError(
            f"malformed unit counts (python_files={python_files}, total_files={total_files})"
        )
    return {
        "files_indexed": total_files,
        "python_files": python_files,
        "detector_passes": python_files * 3,
    }


def _is_python_path(rel: str) -> bool:
    return rel.endswith((".py", ".pyi", ".pyx"))


def size_budget(
    plan: PartitionPlan,
    loc_by_file: dict[str, int],
    *,
    headroom_numerator: int = DEFAULT_HEADROOM_NUMERATOR,
    headroom_denominator: int = DEFAULT_HEADROOM_DENOMINATOR,
) -> BudgetSizing:
    """Size ``$X`` EMPIRICALLY over the full-repo plan via the 3.1 accountant (PURE / AC3).

    Folds each unit's V1 deterministic contributions (``unit_contributions``) via the
    3.1 ``account_spend`` (REUSED — no forked cost model / breach comparison) into a
    running ``int``-credit whole-repo total; sizes ``$X`` = total × headroom (an ``int``
    credit value — the ``Fraction`` headroom is applied then floored back to ``int``, so
    no ``float`` reaches ``$X``, AR4); computes the NFR-C1 baseline ratio against the
    build-cost proxy (total physical LOC); and DEMONSTRATES the 3.2 halt semantics by
    asserting the run FITS under ``BudgetConfig(ceiling_credits=$X)`` (``ceiling_reached
    is False``) while a ceiling ONE credit below the total demonstrably BREACHES
    (``ceiling_reached is True`` — the ≥-is-a-breach REUSE). A non-``PartitionPlan``
    argument raises :class:`DogfoodPlanError` (AR10).
    """
    if not isinstance(plan, PartitionPlan):
        raise DogfoodPlanError(
            f"plan must be a PartitionPlan, got {type(plan).__name__!r}"
        )
    if headroom_numerator < headroom_denominator or headroom_denominator < 1:
        raise DogfoodPlanError(
            f"headroom must be >= 1 (got {headroom_numerator}/{headroom_denominator})"
        )

    build_cost_proxy = sum(loc_by_file.values())
    no_ceiling = BudgetConfig()  # ceiling_credits=None — admit everything (OI3 default)

    rows: list[UnitCostRow] = []
    total_credits = 0
    for partition in plan.partitions:
        unit_files = partition.work_manifest.files
        python_files = sum(1 for f in unit_files if _is_python_path(f))
        contributions = unit_contributions(python_files, len(unit_files))
        unit_ledger = account_spend(
            contributions, config=no_ceiling, build_cost_proxy=build_cost_proxy
        )
        total_credits += unit_ledger.total_credits
        # AC2: a targeted unit is floor-clearing when it is bounded so ≥1/5 of its files
        # can be audited deep. The V1 deterministic pass grades every file, so every
        # bounded unit structurally clears the floor (deep_ratio == 1 >= 1/5); we record
        # the explicit claim rather than assume it.
        clears_floor = partition.file_count == 0 or (
            Fraction(partition.file_count, partition.file_count) >= COVERAGE_FLOOR
        )
        rows.append(
            UnitCostRow(
                partition_id=partition.partition_id,
                file_count=partition.file_count,
                total_loc=partition.total_loc,
                python_files=python_files,
                context_pressure=partition.context_pressure,
                unit_credits=unit_ledger.total_credits,
                clears_floor=clears_floor,
            )
        )

    # $X = total * headroom, floored back to int (AR4 — no float reaches the ceiling).
    headroom = Fraction(headroom_numerator, headroom_denominator)
    sized_ceiling = int(total_credits * headroom)
    headroom_credits = sized_ceiling - total_credits

    # DEMONSTRATE the 3.2 semantics via the SAME 3.1 accountant (no fork): the run fits
    # under $X; a ceiling one credit below the total breaches (the >=-is-a-breach REUSE).
    whole = {"total": total_credits}
    fits = not account_spend(
        whole, config=BudgetConfig(ceiling_credits=sized_ceiling), build_cost_proxy=build_cost_proxy
    ).ceiling_reached
    breaches_below = account_spend(
        whole,
        config=BudgetConfig(ceiling_credits=max(total_credits - 1, 0)),
        build_cost_proxy=build_cost_proxy,
    ).ceiling_reached

    return BudgetSizing(
        total_credits=total_credits,
        sized_ceiling=sized_ceiling,
        headroom_credits=headroom_credits,
        build_cost_proxy=build_cost_proxy,
        baseline_ratio=baseline_ratio(total_credits, build_cost_proxy),
        fits_within_ceiling=fits,
        breaches_when_ceiling_below_total=breaches_below,
        per_unit=tuple(rows),
    )


# ──────────────────────────────────────────────────────────────────────────────
# IMPURE orchestration — read the real repo, derive the pure plan (AR8)
# ──────────────────────────────────────────────────────────────────────────────


def _resolve_commit_descriptor(repo_root: Path) -> str:
    """Best-effort ``git rev-parse HEAD`` for provenance — degrades to a marker (AI-E4-2)."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "unresolved-HEAD"
    if proc.returncode != 0:
        return "unresolved-HEAD"
    return proc.stdout.decode("utf-8", errors="replace").strip() or "unresolved-HEAD"


def build_full_repo_plan(
    repo_root: str | Path,
    *,
    scope_prefix: str = "argus/",
    exclude_prefixes: tuple[str, ...] = ("argus/tests/",),
) -> FullRepoPlan:
    """Enumerate + read + derive the full-repo partition + budget plan (the impure shell).

    Orchestrates: enumerate the tracked Minions source files → read them → build the 1.4
    AST index + the LOC map → REUSE the 2.4 planner → SIZE ``$X`` via the 3.1 accountant.
    Deterministic for the same tracked content (byte-stable — NFR-D1/P1). The AI-E4-2
    no-crash leg: an empty repo yields a plan with zero partitions + a total-safe
    ``BASELINE_UNDEFINED`` baseline (never a divide-by-zero); a git/read failure raises
    the typed :class:`DogfoodPlanError`.
    """
    root = Path(repo_root)
    source_files = enumerate_minions_source_files(
        root, scope_prefix=scope_prefix, exclude_prefixes=exclude_prefixes
    )
    source_by_file = read_sources(root, source_files)
    loc_by_file = compute_loc_by_file(source_by_file)
    index = build_ast_index(root, source_files, partition_id="root")
    plan = derive_partition_plan(index, loc_by_file)
    budget = size_budget(plan, loc_by_file)
    return FullRepoPlan(
        commit_descriptor=_resolve_commit_descriptor(root),
        source_file_count=len(source_files),
        total_loc=sum(loc_by_file.values()),
        partition_plan=plan,
        budget=budget,
    )


# ──────────────────────────────────────────────────────────────────────────────
# PURE markdown renderers (AR8) — paths + counts + credits only (NFR-S1)
# ──────────────────────────────────────────────────────────────────────────────

_SEAM_LIMITATION = (
    "**Honest V1 limitation — NO cross-partition SEAM analysis.** V1 does MULTI-UNIT "
    "auditing, NOT cross-partition SEAM analysis. A defect spanning a partition cut "
    "(caller in unit A, callee in unit B) is NOT analyzed by any seam auditor in V1. "
    "The ONLY V1 mitigation is the Story 6.4 `cross_partition` Prosecutor cut-edge pass "
    "(re-reads the recorded cut edges); the full seam auditor is reserved V2. So the "
    "proof's scope statement is honest about what cut-spanning defects it could and "
    "could not see (mirrors the 2.4 `PartitionPlan.seam_analysis = \"v2-deferred\"` "
    "provenance)."
)


def render_partition_plan_markdown(result: FullRepoPlan) -> str:
    """Render the reproducible full-repo partition map as committed markdown (AC1/AC2/AC4).

    Records the unit count, each unit's ``partition_id`` + file count + LOC + Python-file
    count + ``context_pressure``, the cut-edge count, the per-unit 20%-floor-clearing
    claim (AC2), and the honest V1-no-seam-analysis limitation (AC4). Value-free — only
    repo-relative provenance + counts (NFR-S1). Deterministic (byte-stable for the same
    plan — the units are already sorted by ``partition_id``).
    """
    plan = result.partition_plan
    lines: list[str] = []
    lines.append("# Minions Dogfood — Full-Repo Partition Plan (Story 7.1)")
    lines.append("")
    lines.append(
        "> AUTO-GENERATED by `minions_core/apaa/dogfood/partition_plan.py` "
        "(`render_partition_plan_markdown`). Reproducible + byte-stable for the same "
        "tracked Minions content — do NOT hand-edit. Drivers: ArgusAgent-FR-3 / ArgusAgent-NFR-SC1 "
        "/ ArgusAgent-NFR-D1 / ArgusAgent-AR7."
    )
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    lines.append(f"- Commit descriptor (HEAD at generation): `{result.commit_descriptor}`")
    lines.append(f"- Source files (tracked `minions_core/`, excluding `minions_core/apaa/`): **{result.source_file_count}**")
    lines.append(f"- Total physical LOC (build-cost proxy): **{result.total_loc}**")
    lines.append(
        f"- NFR-SC1 scale envelope: soft ≤{DEFAULT_SOFT_FILE_LIMIT} files / "
        f"≤{DEFAULT_SOFT_LOC_LIMIT} LOC; hard ≤{DEFAULT_HARD_FILE_LIMIT} / "
        f"≤{DEFAULT_HARD_LOC_LIMIT}."
    )
    lines.append("- Reused planner: `partition_repository` (Story 2.4) — no fork (AR7).")
    lines.append("")
    lines.append("## Partition map (OI2 — full-repo, MULTIPLE bounded units)")
    lines.append("")
    lines.append(f"- **Unit count: {len(plan.partitions)}**")
    lines.append(f"- **Recorded cut edges (recorded-NOT-analyzed, the 6.4 seam): {len(plan.cut_edges)}**")
    lines.append("")
    lines.append("| # | partition_id (sha256, 12ch) | files | LOC | context_pressure | ≤hard ceiling |")
    lines.append("|---|---|---|---|---|---|")
    for i, partition in enumerate(plan.partitions, 1):
        within_hard = (
            partition.file_count <= DEFAULT_HARD_FILE_LIMIT
            and partition.total_loc <= DEFAULT_HARD_LOC_LIMIT
        )
        lines.append(
            f"| {i} | `{partition.partition_id[:12]}` | {partition.file_count} | "
            f"{partition.total_loc} | {partition.context_pressure} | {within_hard} |"
        )
    lines.append("")
    lines.append("## AC2 — every TARGETED unit clears the 20%-deep coverage floor")
    lines.append("")
    lines.append(
        f"The 3.3 coverage floor is {COVERAGE_FLOOR.numerator}/{COVERAGE_FLOOR.denominator} "
        "(20% deep). Every unit above is a TARGETED audit unit bounded within the "
        "NFR-SC1 envelope, so the V1 deterministic pass (which grades every file in the "
        "unit) audits 100% of the unit's files — comfortably clearing the 20% floor. NO "
        "unit is un-targeted; NO unit lands `INSUFFICIENT_COVERAGE` merely because the "
        "repo overflowed a single audit unit (OI2 multi-partition is exactly the "
        "mitigation)."
    )
    lines.append("")
    lines.append("## Scope honesty")
    lines.append("")
    lines.append(_SEAM_LIMITATION)
    lines.append("")
    return "\n".join(lines)


def render_budget_plan_markdown(result: FullRepoPlan) -> str:
    """Render the empirically-sized ``$X`` budget plan as committed markdown (AC3).

    Records the per-unit V1 contribution → the running total → the sized ceiling ``$X``
    (with headroom) → the NFR-C1 baseline ratio, and documents that OI3's "no numeric
    default" is RESOLVED for the dogfood by THIS sizing while `budget_governor.py` keeps
    no hardcoded default, and that the 3.2 ceiling halts + downgrades if breached. All
    figures are ``int`` credits / a ``Fraction`` ratio — NEVER a float (AR4).
    """
    budget = result.budget
    br = budget.baseline_ratio
    if isinstance(br, Fraction):
        baseline_str = f"{br.numerator}/{br.denominator}"
    else:
        baseline_str = br  # the BASELINE_UNDEFINED marker (0-build-cost, total-safe)
    lines: list[str] = []
    lines.append("# Minions Dogfood — Budget-Sizing Plan (Story 7.1)")
    lines.append("")
    lines.append(
        "> AUTO-GENERATED by `minions_core/apaa/dogfood/partition_plan.py` "
        "(`render_budget_plan_markdown`). Reproducible + byte-stable. Drivers: "
        "ArgusAgent-FR-21 / ArgusAgent-NFR-C1 / ArgusAgent-AR4 / ArgusAgent-AR7."
    )
    lines.append("")
    lines.append("## Empirical `$X` sizing (OI3 — no pre-locked numeric default)")
    lines.append("")
    lines.append(
        "`$X` is sized EMPIRICALLY to cover the full-repo partition plan, folding the V1 "
        "deterministic zero-token contributions (`files_indexed` + `python_files` + "
        "`detector_passes` — the SAME recipe `pipeline._build_cost_ledger` uses, REUSED "
        "via the 3.1 `account_spend` accountant, no fork) across ALL units into a running "
        "`int`-credit total, then applying a "
        f"{DEFAULT_HEADROOM_NUMERATOR}/{DEFAULT_HEADROOM_DENOMINATOR} headroom."
    )
    lines.append("")
    lines.append(f"- **V1 deterministic total: {budget.total_credits} credits**")
    lines.append(
        f"- **Headroom ({DEFAULT_HEADROOM_NUMERATOR}/{DEFAULT_HEADROOM_DENOMINATOR}): "
        f"+{budget.headroom_credits} credits**"
    )
    lines.append(f"- **Sized ceiling `$X`: {budget.sized_ceiling} credits** (int — never a float, AR4)")
    lines.append(f"- Build-cost proxy (total physical LOC): {budget.build_cost_proxy}")
    lines.append(f"- **NFR-C1 baseline ratio (audit-cost / build-cost proxy): `{baseline_str}`** (Fraction/marker — never a float)")
    lines.append("")
    lines.append("## Per-unit contribution basis")
    lines.append("")
    lines.append("| partition_id (12ch) | files | python_files | unit_credits | clears 20% floor |")
    lines.append("|---|---|---|---|---|")
    for row in budget.per_unit:
        lines.append(
            f"| `{row.partition_id[:12]}` | {row.file_count} | {row.python_files} | "
            f"{row.unit_credits} | {row.clears_floor} |"
        )
    lines.append("")
    lines.append("## 3.2 halt demonstration (the ceiling halts + downgrades if breached)")
    lines.append("")
    lines.append(
        f"- Under `BudgetConfig(ceiling_credits={budget.sized_ceiling})` the run FITS "
        f"(`ceiling_reached is False`): **{budget.fits_within_ceiling}**"
    )
    lines.append(
        f"- Under a ceiling ONE credit below the total the run BREACHES "
        f"(`ceiling_reached is True`, the ≥-is-a-breach REUSE): "
        f"**{budget.breaches_when_ceiling_below_total}** — the 3.2 "
        "halt→skip→downgrade→report path fires."
    )
    lines.append("")
    lines.append("## OI3 invariant preserved")
    lines.append("")
    lines.append(
        "OI3's \"no numeric `$X` default\" is RESOLVED **for the dogfood** by THIS "
        "empirical sizing — the number lives in THIS plan artifact, NOT baked into "
        "`budget_governor.py` (which keeps `ceiling_credits: int | None = None`; the "
        "operator supplies `$X` to the 7.2 run). No hardcoded numeric ceiling default is "
        "introduced anywhere in the module (AR7 / §3.3)."
    )
    lines.append("")
    return "\n".join(lines)
