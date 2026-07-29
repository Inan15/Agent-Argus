"""IMPURE sequential audit pipeline — wires the six done spine modules (FR30).

Drivers: ArgusAgent-FR-30 (headless invocation contract: ``repo + commit + budget +
materiality_bar → verdict artifact + exit code`` — this is the orchestrator half),
ArgusAgent-NFR-P1 (sequential byte-identical ``.argus/`` output across repeated runs),
ArgusAgent-NFR-R1 / AR10 (failure → typed finding / a TYPED error the CLI maps to exit
``1`` — never an uncaught raise out of the pipeline), ArgusAgent-NFR-D2 (the verdict
path is ZERO-LLM-token — this module imports NO ``providers.*`` and NO LLM
dispatch surface; Story 6.2 adds the ONE allowed ``argus.audit`` import, the PURE
provider-free ``audit.grounding`` FR7 validator), ArgusAgent-NFR-S1 (no source / secret / absolute-host-path bytes in
artifacts), ArgusAgent-NFR-S5 (all FS writes containment-checked — reused via 1.3), AR8
(pure/impure separation — this is the IMPURE shell that orchestrates the pure
cores; it adds NO new serializer / ledger / finding / verdict model, NO direct
``json.dumps``, NO direct ``open()``), AR11 (``.argus/`` filenames from
content-sha256 / a stable id, never arrival order).

Why this module exists (the Epic-1 capstone)
-------------------------------------------
Stories 1.1–1.6 delivered six building blocks; this module is the ONLY one that
WIRES them into a running pipeline. It REUSES each verbatim (§3.3): the 1.4
loader / stack-detect / AST index, the 1.5 vacuous-test detector, the 1.2 ledger,
the 1.6 verdict fold, the 1.1 serializer / envelope, and the 1.3 store shell. It
defines NO parallel of any of them.

The sequential-canonical dataflow (straight-line fold)
------------------------------------------------------
``run_audit(request)``:
  1. ``load_repo_at_commit(repo_path, commit)`` → ``RepoIntake`` (FR1; refuses drift)
  2. ``detect_stack(repo_root, source_files)`` → ``StackProfile`` (FR2; recorded)
  3. ``build_ast_index(repo_root, source_files, partition_id="root")`` → ``AstIndex``
  4. per indexed file:
       - a Python TEST file → ``VacuousTestDetector().run(...)`` → entries + findings
       - a Python NON-test file that parsed cleanly → graded ``audited_deep`` ONLY
         when AST-GROUNDED (FR7: ≥1 real Definition); an ungrounded claim downgrades
         to ``audited_shallow`` (Story 6.2 — the deep numerator, no longer the FR6
         presence proxy)
       - anything else → recorded shallow / skipped (degraded, never flagged)
  5. ``CoverageLedger.build(entries)`` (FR5/FR6)
  6. ``evaluate_verdict(ledger, findings)`` → ``AuditVerdict`` (FR15/FR16/FR33 — PURE)
  7. persist the verdict envelope + findings + ledger/run state THROUGH the 1.3
     ``ApaaStoreWriter`` (content-sha256 filenames — AR11/NFR-S5/FR25)

Deep-coverage grading (FR7 AST-grounded — Story 6.2 CLOSES DF-1-7-B)
-------------------------------------------------------------------
The vacuous-test detector grades TEST files ``audited_shallow``. A non-test
(source-under-test) Python file emits a deep claim, but the claim is HONOURED
``audited_deep`` ONLY when it is AST-GROUNDED — the FR7 truth-validation that
replaces the interim FR6 claim-PRESENCE proxy.

Interim (Epic 1–5, the DF-1-7-B over-grading, NOW REMOVED): every cleanly-parsed
non-test Python file was graded ``audited_deep`` via ``grade_entry(
proposed_depth=AUDITED_DEEP, claim_present=True)`` — deep merely because it
parsed, not because its claim was verified.

FR7 (Story 6.2, the V1 deep numerator): ``_grade_non_test_python`` consults the
pure ``audit.grounding.is_deep_claim_grounded`` over the PRE-BUILT 1.4 AST entry
(no re-parse — AR7/§3.3) and passes ``claim_present=(claim_emitted AND
claim_grounded)`` into the UNCHANGED 1.2 ``grade_entry`` (DN-GROUNDED —
``coverage_ledger.py`` stays byte-identical). The V1 grounding fact (DN-GROUND-RULE)
is structural-presence-of-auditable-definitions: GROUNDED iff the AST entry has
≥1 real ``Definition`` (a function/class a deep read could examine). A clean-parsed
ZERO-definition module (constants-only / re-export / ``__all__``-only /
docstring-only / dunder-glue) is UNGROUNDED → it downgrades to ``audited_shallow``
(silence/insufficiency → downgrade, FR7) — the deep-% now reflects GROUNDED depth,
not mere parse-success. A non-Python / unparseable file is recorded ``skipped``
(examined-but-ungradable; in the denominator, never a false deep claim) exactly as
before. The conservative bar grounds the STRUCTURE a claim is about, not a specific
claim's truth (that is the 6.1 LLM port + 6.4 Prosecutor — DN-V1-DETERMINISTIC); the
pipeline default grading path stays PURE + zero-token + deterministic (NFR-D1/D2).

Story 3.2 — halt → skip → downgrade → report on budget exhaustion (LOCKED)
--------------------------------------------------------------------------
FR22 / NFR-C2. The V1 pipeline calls NO LLM, so "halt mid-run" is a DETERMINISTIC
PRE-DISPATCH ADMISSION PROJECTION, not a wall-clock interrupt (AR4/NFR-D2). Locked
decisions (recorded here per the story):
  - **Module placement**: a new pure sibling ``cost/exhaustion.py`` (the 3-1
    ``budget_governor.py`` stays frozen; the halt mechanism is a distinct concern).
  - **``_coerce_breach`` reuse**: ``cost/exhaustion.py`` imports the 3-1
    ``_coerce_breach`` BY IMPORT and exposes a public ``would_breach`` /
    ``project_halt_point`` that delegate to it (no fork of the comparison — AR7).
  - **Halt granularity**: per-file over the EXISTING sorted index (AR11) —
    simplest, finest-grained, already the detect-loop order.
  - **Per-unit cost proxy attribution**: every file costs 1 (files_indexed); a
    Python file costs an extra 1 + 3 = 5 (python_files + detector_passes). The
    cumulative sum equals the 3-1 whole-run total so a no-halt projection is
    consistent with the cost ledger (AC6). When Epic 6 wires the LLM port, the
    per-unit proxy is replaced by the real per-unit LLM credit estimate folding into
    the SAME ``_coerce_breach`` decision — NO new authority (forward-compatible).
The pipeline projects the halt point over the index; AUDITED units run the EXISTING
detect/grade stage; the SKIPPED-on-exhaustion remainder is graded
``CoverageDepth.SKIPPED`` via the EXISTING ``grade_entry`` (NEVER a fabricated
``audited_*``). The PARTIAL ledger is re-folded through the UNCHANGED 1.6
``evaluate_verdict`` (degraded, never a crash — the floor semantics are Story 3.3).
A frozen ``HaltReport`` (assessed vs skipped) is persisted additively to ``state/``
(the 3.4 resume seam). A no-halt run (no ceiling / never-reached) is BYTE-IDENTICAL
to the pre-3.2 verdict/ledger/findings output (the regression-safe keystone).
DF-1-7-A note: the halt report persists through the SAME ``write_payload("state",
...)`` path the 3-1 cost snapshot uses; the interim ``_persist`` OSError edge stays
DEFERRED (DF-1-7-A — out of scope; not silently expanded).

Degrade-vs-fatal split (LOCKED + documented — AR10)
---------------------------------------------------
FATAL (→ a TYPED error the CLI maps to exit ``1``, never an uncaught traceback):
the repo cannot be loaded at all — ``RepoIntakeError`` (missing path / drifted
tree / unresolvable commit), a ``WorkspaceContainmentError`` on write, a
``CanonicalSerializationError`` on serialize, or any unexpected error (wrapped in
:class:`PipelineError`). DEGRADED-TO-VERDICT (the run continues): a per-file parse
failure is ALREADY recorded by the 1.4 index (``parse_failed``) and routes to the
``skipped`` grade — it never aborts the run. The pipeline raises typed errors;
``cli.py`` owns the ONLY user-facing stdout/stderr (no ``print()`` here, no bare
``except: pass``).

Story 6.3 — module split (DN-PIPELINE-SPLIT) + the whole-index orphan pass
--------------------------------------------------------------------------
This module reached the §3.2 1200-line hard limit (1190/1200) at Story 6.2, so the
6.3 orphan-detector WIRING needed room. Per DN-PIPELINE-SPLIT the cohesive ``.argus/``
persist family (``_persist`` + the ``_persist_*`` helpers — the single concern
"write a built artifact through the 1.3 store") was extracted VERBATIM into the
sibling :mod:`argus.pipeline_persist` (a PURE no-behavior-change
refactor — the verdict math / persist order / producer tokens / public entrypoints
are UNCHANGED; this module imports the moved helpers). After the split the 6.3
orphan detector is wired as a SINGLE whole-index pass (DN-WHOLE-INDEX) AFTER the
per-file detect stage (``_detect_per_file``): its advisory ``orphan_code`` findings
are APPENDED to the existing ``findings`` accumulation (a finding-only detector — it
mints NO coverage entry, so a no-orphan repo is BYTE-IDENTICAL to the pre-6.3
ledger + verdict, the regression-safe keystone). On a halted/partial run the orphan
pass runs over the ASSESSED entries only (consistent with ``_detect_per_file``).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from argus.audit.grounding import is_deep_claim_grounded
from argus.detectors.orphan_code import RULE_ORPHAN_CODE, OrphanCodeDetector
from argus.detectors.secret_scan import SecretScanDetector
from argus.detectors.tool_runner import ToolRunnerDetector
from argus.detectors.vacuous_test import VacuousTestDetector, is_test_file
from argus.index.ast_index import AstIndex, AstIndexEntry, build_ast_index
from argus.cost.budget_governor import (
    BudgetConfig,
    CostLedger,
    account_spend,
    budget_config_from_budget,
)
from argus.cost.exhaustion import (
    CostUnit,
    HaltProjection,
    HaltReport,
    InsufficientCoverageFloorReport,
    build_floor_report,
    build_halt_report,
    project_halt_point,
)
from argus.cost.resume import (
    ResumeError,
    ResumePlan,
    build_resume_plan,
)
from argus.index.partitioner import (
    PartitionPlan,
    compute_loc_by_file,
    partition_repository,
)
from argus.intake.repo_loader import RepoIntakeError, load_repo_at_commit
from argus.intake.stack_detect import detect_stack
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
    grade_entry,
)
from argus.ledger.coverage_report import CoverageReport, build_coverage_report
from argus.ledger.critical_subsystems import (
    CriticalCandidate,
    critical_subsystems_all_deep,
    identify_critical_subsystems,
)
from argus.ledger.depth_semantics import assess_criticality
from argus.ledger.recording import Recording
from argus.models import AuditRequest
from argus.pipeline_persist import (
    COST_LEDGER_PRODUCER as _COST_LEDGER_PRODUCER,
    FINDING_PRODUCER as _FINDING_PRODUCER,
    HALT_REPORT_PRODUCER as _HALT_REPORT_PRODUCER,
    STATE_PRODUCER as _STATE_PRODUCER,
    persist_cost_ledger,
    persist_critical_subsystems,
    persist_halt_report,
    persist_negative_assurance,
    persist_partitions,
    persist_verdict,
)
from argus.reports.generator import generate_reports
from argus.store import canonical
from argus.store.envelope import Envelope
from argus.store.paths import WorkspaceContainmentError
from argus.store.reader import ApaaStoreReader, StoreIntegrityError
from argus.store.writer import ApaaStoreWriter
from argus.verdict.negative_assurance import (
    NegativeAssuranceVerdict,
    build_negative_assurance_verdict,
)
from argus.verdict.prosecutor import prosecute
from argus.verdict.verdict_gate import AuditVerdict, evaluate_verdict

__all__ = [
    "PipelineError",
    "ResumeStateError",
    "AuditResult",
    "run_audit",
    "run_audit_detailed",
    "resume_audit_detailed",
    "resume_audit",
]

# Story 6.3 (DN-PIPELINE-SPLIT) — the persisted-envelope producer tokens + the
# persist helpers now live in :mod:`argus.pipeline_persist` (the single
# source of truth). The four tokens the resume-discovery path reads below
# (_STATE_PRODUCER / _HALT_REPORT_PRODUCER / _COST_LEDGER_PRODUCER / _FINDING_PRODUCER)
# are imported from that module (aliased to the historical private names).

# Story 6.3 — the orphan-detector rule id (cross-file findings are NOT carried
# forward on resume — they are recomputed over the resumed assessed set; see
# resume_audit_detailed). Sourced from the detector module (single source of truth).
_ORPHAN_RULE_ID = RULE_ORPHAN_CODE

# Story 3.4 — the producer tokens the resume DISCOVERS in the prior .argus/ state.
# Discovery enumerates state/ + findings/ envelopes (sorted locators — AR11) and
# selects by producer token, reading each via the 1-3 reader (tamper-guarded).
_RESUME_DISCOVERABLE_STATE_PRODUCERS = frozenset(
    {_STATE_PRODUCER, _HALT_REPORT_PRODUCER, _COST_LEDGER_PRODUCER}
)

_PYTHON_SUFFIXES: frozenset[str] = frozenset({".py", ".pyi", ".pyx"})

# Story 3.2 — the deterministic per-unit (per-file) cost proxy attribution.
# It MUST sum to the 3-1 whole-run total so a no-halt projection is consistent
# with the 3-1 ledger (AC6 byte-identity): the 3-1 fold counts
# ``files_indexed`` (1 per indexed file) + ``python_files`` (1 per Python file) +
# ``detector_passes`` (3 per Python file). Attributed per file: every file costs 1
# (files_indexed); a Python file costs an extra 1 + 3 = 5 total. The cumulative sum
# over all units therefore equals len(entries) + python_files + python_files*3 —
# the EXACT 3-1 whole-run total (NEVER float — AR4).
_NON_PYTHON_UNIT_COST = 1
_PYTHON_UNIT_COST = 5


class PipelineError(ValueError):
    """A TYPED fatal pipeline failure the CLI maps to exit ``1`` (AR10 / NFR-R1).

    A ``ValueError`` subclass (mirroring ``RepoIntakeError`` /
    ``WorkspaceContainmentError`` / ``CanonicalSerializationError``). Wraps an
    unexpected error so the CLI prints a secret-safe stderr message + returns ``1``
    rather than letting a bare Python traceback escape. The message names the
    failing STAGE + the typed reason only — never an absolute host path, never
    source / secret bytes (NFR-S1).
    """


class ResumeStateError(PipelineError):
    """A TYPED resume-from-disk failure the CLI maps to exit ``1`` (Story 3.4, AR10/AI-E1-1).

    A :class:`PipelineError` subclass — the localized typed failure for a resume
    that cannot proceed from the on-disk ``.argus/`` state: a tamper / corruption /
    unparseable / unknown-field / missing-state read error (the 1-3 reader's
    ``StoreIntegrityError`` / ``CanonicalSerializationError`` / ``ValidationError`` /
    ``FileNotFoundError``), a divergent tree/commit (the ``cost.resume.ResumeError``),
    or no prior state to resume. The resume entrypoint NEVER silently resumes from
    corrupted state, NEVER fabricates a valid-looking resumed verdict, and NEVER
    falls back to a fresh run that masks the corruption (AI-E1-1: a corrupted /
    tampered state must RAISE). The message names the failing reason + the offending
    RELATIVE locator only — never an absolute host path / source / secret byte
    (NFR-S1).
    """


class AuditResult:
    """The pipeline outcome — the verdict plus the ``.argus/`` write locators.

    A thin value holder (NOT a persisted model): ``verdict`` is the pure 1.6
    :class:`AuditVerdict` the CLI reads ``exit_code`` from; ``locators`` are the
    ``.argus/``-root-relative POSIX paths the pipeline wrote (verdict + findings +
    run-state), useful for tests / a future resume. ``run_audit`` returns the
    verdict directly for the simple call; ``run_audit_detailed`` returns this.

    Story 3.3 (FR16/FR22): ``floor_report`` is the additive, PURE exhaustion-aware
    :class:`InsufficientCoverageFloorReport` READ-folded from the verdict + halt
    report — the honest "assessed X% deep; floor 20%" surface that names the assessed
    deep-% and distinguishes exhaustion-driven from intrinsic floor verdicts. It is
    exposed PURELY here (DERIVABLE from the already-persisted verdict + halt report,
    so NOT persisted as a new artifact — the no-new-write option), so a non-floor /
    no-exhaustion run's persisted bytes are BYTE-IDENTICAL to 3-2 (AC6).

    Story 4.1 (FR17/NFR-A3): ``negative_assurance`` is the additive, frozen
    :class:`NegativeAssuranceVerdict` WRAPPER built in the SHARED
    ``_assemble_and_persist`` fold from the EXISTING verdict + floor report +
    critical set + ``request.materiality_bar`` and PERSISTED additively to
    ``state/`` (the wrapper + the computed ``CriticalSubsystemSet`` are PURELY
    ADDITIVE new artifacts — they do not alter the existing verdict/ledger/findings/
    halt-report/floor-report bytes, AC6). It is an additive optional field
    (default-preserving — the ``floor_report`` precedent).

    Story 4.3 (FR29): ``coverage_report`` is the additive, PURE 2.2
    :class:`CoverageReport` (per-file depth states + per-depth counts + exact-%)
    built from the merged ledger in the SHARED ``_assemble_and_persist`` fold. Like
    ``floor_report`` it is exposed PURELY in-memory (DERIVABLE from the ledger, NOT
    a new persisted artifact — the no-new-write option), so a run's persisted bytes
    are BYTE-IDENTICAL to 4.1/4.2 (AC6). The 4.3 evidence-bundle export reads it.
    """

    __slots__ = (
        "verdict",
        "locators",
        "floor_report",
        "negative_assurance",
        "coverage_report",
    )

    def __init__(
        self,
        verdict: AuditVerdict,
        locators: tuple[str, ...],
        floor_report: InsufficientCoverageFloorReport | None = None,
        negative_assurance: NegativeAssuranceVerdict | None = None,
        coverage_report: CoverageReport | None = None,
    ) -> None:
        self.verdict = verdict
        self.locators = locators
        self.floor_report = floor_report
        self.negative_assurance = negative_assurance
        self.coverage_report = coverage_report


def _is_python(rel_path: str) -> bool:
    return Path(rel_path).suffix in _PYTHON_SUFFIXES


def _read_source(repo_root: Path, rel_path: str) -> str:
    """Read a repo-relative source file as text (the impure read; AR8).

    Decodes UTF-8 with ``errors="replace"`` so a non-UTF-8 byte never raises out
    of the per-file path (the detector degrades on un-analyzable content). The
    repo-relative path keeps the read confined to the audited tree; the absolute
    root stays transient (NFR-S1).
    """
    return (repo_root / rel_path).read_text(encoding="utf-8", errors="replace")


def _grade_non_test_python(entry: AstIndexEntry) -> CoverageLedgerEntry:
    """Grade a non-test Python file ``audited_deep`` ONLY when AST-grounded (FR7).

    Story 6.2 (CLOSES DF-1-7-B). A Python file the 1.4 index could not parse
    cleanly (``parse_failed`` / not ``ast_eligible``) is recorded ``skipped``
    (examined-but-ungradable — in the denominator, never a false deep claim).

    For a cleanly-parsed file the deep claim is emitted (V1 always emits the
    claim, the FR6 ``claim_emitted`` proxy) but is now GROUNDED before it is
    honoured: ``is_deep_claim_grounded`` (the FR7 ``claim → validated?`` interface)
    computes a pure structural fact over the PRE-BUILT 1.4 AST entry (≥1 real
    ``Definition`` — DN-GROUND-RULE; no re-parse — AR7/§3.3). The grounding result
    is carried into the UNCHANGED 1.2 ``grade_entry`` by passing ``claim_present =
    (claim_emitted AND claim_grounded)`` (DN-GROUNDED — ``coverage_ledger.py`` stays
    byte-identical): a GROUNDED file (≥1 def) stays ``audited_deep``; an UNGROUNDED
    file (clean-parse, ZERO defs — a constants-only / re-export / docstring-only
    module) downgrades to ``audited_shallow`` (silence/insufficiency → downgrade,
    FR7), removing the interim over-grading.
    """
    if entry.parse_failed or not entry.ast_eligible:
        return grade_entry(
            file_path=entry.file_path,
            proposed_depth=CoverageDepth.SKIPPED,
            claim_present=False,
        )
    claim_emitted = True
    claim_grounded = is_deep_claim_grounded(entry)
    return grade_entry(
        file_path=entry.file_path,
        proposed_depth=CoverageDepth.AUDITED_DEEP,
        claim_present=claim_emitted and claim_grounded,
    )


def _detect_per_file(
    repo_root: Path,
    index_entries: tuple[AstIndexEntry, ...],
    request: AuditRequest | None = None,
) -> tuple[list[CoverageLedgerEntry], list[Recording], list[CriticalCandidate]]:
    detector = VacuousTestDetector()
    secret_detector = SecretScanDetector()
    breadth_detector = ToolRunnerDetector()
    entries: list[CoverageLedgerEntry] = []
    findings: list[Recording] = []
    candidates: list[CriticalCandidate] = []
    breadth_targets: list[tuple[str, str]] = []

    enabled_passes = request.enabled_passes if request is not None else ("coverage", "vacuous", "security", "orphan", "prosecutor")

    for entry in index_entries:
        rel = entry.file_path
        if not _is_python(rel):
            entries.append(
                grade_entry(
                    file_path=rel,
                    proposed_depth=CoverageDepth.SKIPPED,
                    claim_present=False,
                )
            )
            continue
        source = _read_source(repo_root, rel)
        breadth_targets.append((rel, source))
        candidates.append(
            CriticalCandidate(
                file_path=rel,
                criticality=assess_criticality(file_path=rel, source=source, ast_entry=entry),
            )
        )
        if "security" in enabled_passes:
            secret_result = secret_detector.run(file_path=rel, source=source, ast_entry=entry)
            findings.extend(secret_result.findings)
        if is_test_file(rel):
            if "vacuous" in enabled_passes:
                result = detector.run(file_path=rel, source=source, ast_entry=entry)
                entries.extend(result.entries)
                findings.extend(result.findings)
            else:
                entries.append(grade_entry(file_path=rel, proposed_depth=CoverageDepth.AUDITED_SHALLOW, claim_present=False))
            continue
        entries.append(_grade_non_test_python(entry))

    already_graded_paths = tuple(e.file_path for e in entries)
    breadth_result = breadth_detector.run(
        targets=breadth_targets, already_graded_paths=already_graded_paths
    )
    entries.extend(breadth_result.entries)
    findings.extend(breadth_result.findings)

    return entries, findings, candidates


def _orphan_findings(
    index: AstIndex,
    assessed_entries: tuple[AstIndexEntry, ...],
    request: AuditRequest | None = None,
) -> list[Recording]:
    if request is not None and "orphan" not in request.enabled_passes:
        return []
    if assessed_entries == index.entries:
        scoped = index
    else:
        scoped = index.model_copy(update={"entries": assessed_entries})
    return list(OrphanCodeDetector().run(index=scoped).findings)



def _build_cost_ledger(
    request: AuditRequest,
    index_entries: tuple[AstIndexEntry, ...],
    loc_by_file: dict[str, int],
) -> CostLedger:
    """Build the Story 3.1 cost ledger from the V1 deterministic contributions (PURE-of-persistence).

    Scope-fenced (FR21 / NFR-C1): derives the budget config from the reserved
    ``request.budget`` (``0`` → no ceiling, OI3 — no numeric default), folds the V1
    deterministic, zero-token work-unit contributions (the LLM dispatch port is
    Epic 6, so V1 cost is a deterministic PROXY, not a billed LLM total), and
    computes the NFR-C1 baseline against the audited repo's build-cost proxy. The
    contributions are content-derived counts already produced by the pipeline:

      - ``files_indexed``   — every file the 1.4 index examined (the denominator).
      - ``python_files``    — Python files run through the detect/grade stage.
      - ``detector_passes`` — per-Python-file detector invocations (vacuous +
        secret + breadth = 3 passes per Python file in V1).

    The NFR-C1 build-cost proxy is the audited repo's TOTAL physical LOC (summed
    from the EXISTING ``compute_loc_by_file`` map — content-derived, deterministic,
    reused, no second read/parser). The fold + ratio are pure; the snapshot WRITE
    is the impure shell. NO ``float``; the same repo@commit + budget → a byte-stable
    ledger (NFR-P1). This does NOT change the verdict math or halt the run (3.2).
    """
    config = budget_config_from_budget(request.budget)
    python_files = sum(1 for e in index_entries if _is_python(e.file_path))
    contributions = {
        "files_indexed": len(index_entries),
        "python_files": python_files,
        "detector_passes": python_files * 3,
    }
    build_cost_proxy = sum(loc_by_file.values())
    return account_spend(
        contributions, config=config, build_cost_proxy=build_cost_proxy
    )


def _unit_cost(entry: AstIndexEntry) -> int:
    """The deterministic per-file cost proxy for the halt projection (Story 3.2).

    A Python file costs :data:`_PYTHON_UNIT_COST` (1 files_indexed + 1 python_files
    + 3 detector_passes — the 3-1 per-Python-file attribution); a non-Python file
    costs :data:`_NON_PYTHON_UNIT_COST` (1 files_indexed). The cumulative sum equals
    the 3-1 whole-run total so a no-halt projection is consistent with the cost
    ledger (AC6). Content-derived ``int`` — NEVER ``float`` (AR4).
    """
    return _PYTHON_UNIT_COST if _is_python(entry.file_path) else _NON_PYTHON_UNIT_COST


def _build_cost_units(index_entries: tuple[AstIndexEntry, ...]) -> tuple[CostUnit, ...]:
    """Map the sorted index entries to ordered per-file :class:`CostUnit`s (Story 3.2, PURE).

    The unit granularity is per-file over the EXISTING sorted index order (AR11).
    Each unit carries the deterministic :func:`_unit_cost` proxy. No detector is run
    here — this is the pre-dispatch admission input only.
    """
    return tuple(
        CostUnit(path=entry.file_path, cost=_unit_cost(entry)) for entry in index_entries
    )


def _project_halt(
    index_entries: tuple[AstIndexEntry, ...], config: BudgetConfig
) -> HaltProjection:
    """Project the deterministic pre-dispatch halt point over the index (Story 3.2, PURE).

    Reuses the pure :func:`project_halt_point` (which delegates the breach decision
    to the 3-1 ``_coerce_breach`` BY IMPORT — no fork). No ceiling configured OR a
    cumulative total that never breaches → no halt (every unit assessed). The halt
    is a PURE function of (sorted index, per-file proxy, ceiling) — deterministic +
    order-independent (NFR-C2 / NFR-P1).
    """
    return project_halt_point(_build_cost_units(index_entries), config=config)


def _skipped_remainder_entries(
    skipped_paths: tuple[str, ...],
) -> list[CoverageLedgerEntry]:
    """Grade the un-audited remainder ``CoverageDepth.SKIPPED`` — the honest downgrade (AC2).

    Every not-yet-audited file is recorded via the EXISTING ``grade_entry``
    (``proposed_depth=CoverageDepth.SKIPPED, claim_present=False``) — the SAME
    closed-enum honesty state the pipeline already uses for a non-Python /
    unparseable file. NO detector is dispatched (no silent overrun — NFR-C2); a
    ``skipped``-on-exhaustion file is NEVER recorded ``audited_*`` (the
    honest-degradation keystone — FR22/NFR-R1). It lands in the partial ledger's
    denominator, never the deep-% numerator (FR8 honored by the UNCHANGED gate).
    """
    return [
        grade_entry(
            file_path=path,
            proposed_depth=CoverageDepth.SKIPPED,
            claim_present=False,
        )
        for path in skipped_paths
    ]


def _compute_loc_map(repo_root: Path, source_files: tuple[str, ...]) -> dict[str, int]:
    """Per-file LOC map over the audited source files (the impure read; AR8).

    Reuses the impure ``_read_source`` (the same read the detect stage uses — no
    second parser) + the PURE ``compute_loc_by_file``. Computed ONCE in the runner
    and shared by both the 2.4 partition plan and the 3.1 cost-baseline proxy (no
    double read — the 3.1 cost touch is additive, not a new repo scan).
    """
    source_by_file = {rel: _read_source(repo_root, rel) for rel in source_files}
    return compute_loc_by_file(source_by_file)


def _build_partition_plan(index: AstIndex, loc_by_file: dict[str, int]) -> PartitionPlan:
    """Build the FR3/NFR-SC1 partition plan from the in-memory index + a LOC map.

    Story 2.4 (SCOPE-FENCED): folds the PURE :func:`partition_repository` over the
    EXISTING in-memory ``index`` + the precomputed LOC map (Story 3.1 lifted the
    LOC read to :func:`_compute_loc_map` in the runner so the same map feeds the
    cost baseline — no second read). It does NOT change the verdict math and does
    NOT split the single-pass audit into N sub-audits (the multi-pass per-partition
    run loop is the Story 7.1/7.2 dogfood).
    """
    return partition_repository(index, loc_by_file=loc_by_file)


def _assemble_and_persist(
    *,
    request: AuditRequest,
    repo_root: Path,
    index: AstIndex,
    source_files: tuple[str, ...],
    entries: list[CoverageLedgerEntry],
    findings: list[Recording],
    candidates: list[CriticalCandidate],
    halt_report: HaltReport,
    store_writer: ApaaStoreWriter | None,
) -> AuditResult:
    """Shared post-detection assembly + persistence (the fold both paths share).

    Story 3.4 extracts the verdict-fold + partition/cost build + persistence that
    ``run_audit_detailed`` (fresh) and ``resume_audit_detailed`` (resume) BOTH run,
    so the resumed run folds the merged ledger through the EXACT SAME path as an
    uninterrupted run (the byte-identity keystone, AC2). The pure cores it folds
    (ledger build, verdict fold, serializer) stay pure; this remains the IMPURE
    shell (it reads the LOC map + writes the ``.argus/`` tree). The verdict math / the
    persist order / the producer tokens are UNCHANGED.
    """
    # The merged ledger (CoverageLedger.build re-sorts, so the merge order does not
    # matter — a resumed merge is the SAME sorted ledger an uninterrupted run
    # produces, AC2) is re-folded through the UNCHANGED 1.6 evaluate_verdict.
    ledger = CoverageLedger.build(entries)
    critical = identify_critical_subsystems(
        candidates,
        operator_designated=request.critical_paths,
        operator_excluded=request.excluded_critical_paths,
    )
    all_deep = critical_subsystems_all_deep(critical.paths, ledger)
    verdict = evaluate_verdict(
        ledger, tuple(findings), critical_subsystems_all_deep=all_deep
    )
    loc_by_file = _compute_loc_map(repo_root, source_files)
    partition_plan = _build_partition_plan(index, loc_by_file)
    cost_ledger = _build_cost_ledger(request, index.entries, loc_by_file)

    # Story 6.4 (FR19 / CC #4 / DN-WIRE): the adversarial Prosecutor pass runs HERE,
    # after the candidate verdict + partition plan are built. It consumes the candidate
    # verdict + ledger + findings + the 2.4 partition_plan.cut_edges and produces the
    # FINAL prosecuted verdict + refined finding set (the CC #4 cross_partition seam
    # findings appended; an advisory finding promoted ONLY with AST corroboration AND
    # sign-off — DN-PROMOTE). The V1 default has NO sign-offs (the deterministic,
    # zero-token path), so an un-prosecuted repo (no cut edges, no signed-off advisory,
    # an earned verdict) is BYTE-IDENTICAL to pre-6.4 (the 6.3 additive precedent — only
    # an actual challenge/promotion/seam changes a byte). The Prosecutor LOGIC lives in
    # verdict/prosecutor.py; this is the minimal call site only (DN-PIPELINE-SIZE).
    if "prosecutor" in request.enabled_passes:
        prosecution = prosecute(
            verdict=verdict,
            ledger=ledger,
            findings=tuple(findings),
            cut_edges=partition_plan.cut_edges,
        )
        verdict = prosecution.verdict

    floor_report = build_floor_report(verdict, halt_report)
    negative_assurance = build_negative_assurance_verdict(
        verdict,
        floor_report,
        critical,
        ledger,
        materiality_bar=request.materiality_bar,
    )

    writer = store_writer if store_writer is not None else ApaaStoreWriter(repo_root)
    locators = persist_verdict(writer, request, verdict, ledger)
    locators = locators + persist_partitions(writer, partition_plan)
    locators = locators + persist_cost_ledger(writer, cost_ledger)
    locators = locators + persist_halt_report(writer, halt_report)
    locators = locators + persist_negative_assurance(writer, negative_assurance)
    locators = locators + persist_critical_subsystems(writer, critical)

    if request.report_dir:
        target_dir = Path(request.report_dir)
        finding_dicts = [f.model_dump() for f in findings]
        generate_reports(request, verdict, ledger, finding_dicts, target_dir)


    return AuditResult(
        verdict=verdict,
        locators=locators,
        floor_report=floor_report,
        negative_assurance=negative_assurance,
        coverage_report=build_coverage_report(ledger),
    )



def run_audit_detailed(
    request: AuditRequest,
    *,
    store_writer: ApaaStoreWriter | None = None,
) -> AuditResult:
    """Run the sequential audit pipeline → :class:`AuditResult` (verdict + locators).

    The IMPURE shell: it reads the FS (1.4 loader/index, source reads) and writes
    the ``.argus/`` tree (1.3 store); the pure cores it folds (ledger build, verdict
    fold, serializer) stay pure. The Epic-1 path calls NO LLM (zero-token, NFR-D2).

    Raises:
        RepoIntakeError: the repo cannot be loaded at the pin (missing path /
            drifted tree / unresolvable commit) — the CLI maps this to exit ``1``.
        WorkspaceContainmentError: a ``.argus/`` write escaped containment — exit ``1``.
        CanonicalSerializationError: a payload was not canonically serializable — exit ``1``.
        PipelineError: any other unexpected stage failure (wrapped, typed) — exit ``1``.
    """
    try:
        intake = load_repo_at_commit(request.repo_path, request.commit)
    except RepoIntakeError:
        raise  # already typed (AR10) — the CLI maps it to exit 1
    except Exception as exc:  # noqa: BLE001 — wrap as a TYPED fatal (never a bare raise)
        raise PipelineError(f"intake stage failed: {type(exc).__name__}") from exc

    repo_root = Path(request.repo_path)

    try:
        detect_stack(repo_root, intake.source_files)  # FR2 — probed/recorded provenance
        index = build_ast_index(repo_root, intake.source_files, partition_id="root")
        # Story 3.2 (FR22/NFR-C2): the DETERMINISTIC pre-dispatch halt projection.
        # Over the SAME sorted index + the per-file cost proxy, project whether the
        # cumulative cost reaches the configured ceiling (the REUSED 3-1
        # >=-hard-ceiling decision BY IMPORT — no fork, no wall-clock interrupt). No
        # ceiling / never-reached → no halt (assessed == every entry → byte-identical
        # to today, AC6). When a halt fires, the detect/grade stage runs ONLY over
        # the ASSESSED entries (no detector dispatch for the remainder — no silent
        # overrun) and the un-audited remainder is graded SKIPPED via the EXISTING
        # grade_entry (NEVER fabricated audited_* — the honest-degradation keystone).
        budget_config = budget_config_from_budget(request.budget)
        halt_projection = _project_halt(index.entries, budget_config)
        assessed_set = frozenset(halt_projection.assessed_paths)
        if halt_projection.halted_on_exhaustion:
            assessed_entries = tuple(
                e for e in index.entries if e.file_path in assessed_set
            )
            entries, findings, candidates = _detect_per_file(repo_root, assessed_entries)
            entries = entries + _skipped_remainder_entries(halt_projection.skipped_paths)
        else:
            assessed_entries = index.entries
            entries, findings, candidates = _detect_per_file(repo_root, index.entries)
        # Story 6.3 (DN-WHOLE-INDEX): the single cross-file orphan pass, AFTER the
        # per-file detect stage, over the ASSESSED entries only. Findings-only —
        # appended to the existing accumulation; a no-orphan repo stays byte-identical.
        findings = findings + _orphan_findings(index, assessed_entries)
        halt_report = build_halt_report(halt_projection)
    except (WorkspaceContainmentError, RepoIntakeError):
        raise
    except Exception as exc:  # noqa: BLE001 — wrap unexpected failures as TYPED (AR10)
        raise PipelineError(f"analysis stage failed: {type(exc).__name__}") from exc

    return _assemble_and_persist(
        request=request,
        repo_root=repo_root,
        index=index,
        source_files=intake.source_files,
        entries=entries,
        findings=findings,
        candidates=candidates,
        halt_report=halt_report,
        store_writer=store_writer,
    )


def run_audit(
    request: AuditRequest,
    *,
    store_writer: ApaaStoreWriter | None = None,
) -> AuditVerdict:
    """Run the pipeline and return the pure :class:`AuditVerdict` (FR30).

    The simple entry the CLI calls: wires the six stages, persists the artifacts,
    and returns the verdict the CLI reads ``exit_code`` from. See
    :func:`run_audit_detailed` for the write locators + the full typed-error
    contract.
    """
    return run_audit_detailed(request, store_writer=store_writer).verdict


# ─────────────────────────────────────────────────────────────────────────────
# Story 3.4 — resumability from on-disk .argus/ state (FR31 / NFR-R2)
# ─────────────────────────────────────────────────────────────────────────────
#
# The IMPURE resume shell: load the prior state via the 1-3 reader (tamper-guarded),
# build the PURE resume plan (cost/resume.py), run detectors ONLY over the
# resume-target remainder, merge the carried-forward audited_deep coverage with the
# newly-audited coverage + the still-skipped remainder, re-fold through the
# UNCHANGED 1.6 gate, and persist via the EXISTING _assemble_and_persist. A
# tampered / corrupt / unparseable / unknown-field / missing / divergent-tree state
# RAISES a typed ResumeStateError (exit 1) — never a silent wrong resume (AI-E1-1).


def _list_locators(reader: ApaaStoreReader, subdir: str) -> tuple[str, ...]:
    """List the sorted ``<subdir>/<name>.json`` locators present in the .argus/ tree.

    Deterministic discovery (sorted — AR11): enumerate the resolved sub-directory
    and return the ``.argus/``-root-relative locators. A missing sub-dir yields an
    empty tuple (a first-run / no-prior-state signal the caller maps to a typed
    error). The byte READ of each locator goes through the tamper-guarded 1-3 reader.
    """
    try:
        directory: Path = reader.paths.resolve(subdir)
    except WorkspaceContainmentError:
        raise
    if not directory.is_dir():
        return ()
    return tuple(
        sorted(f"{subdir}/{child.name}" for child in directory.glob("*.json"))
    )


def _read_prior_state(
    reader: ApaaStoreReader,
) -> tuple[CoverageLedger, HaltReport, list[Recording]]:
    """Load the prior run-state ledger + halt report + findings (tamper-guarded, AC3).

    Enumerates ``state/`` + ``findings/`` envelopes (sorted — AR11) and selects by
    PRODUCER token, reading each via the 1-3 ``read_envelope`` (which re-verifies the
    content_hash — the tamper guard). The run-state envelope carries the prior
    coverage ledger under ``payload["ledger"]``; the halt-report envelope carries the
    3-2 ``HaltReport`` shape; each ``findings/`` envelope is a 1.2 ``Recording``. A
    tamper (``StoreIntegrityError``) / corruption (``CanonicalSerializationError``) /
    unknown-field (``pydantic.ValidationError``) / missing (``FileNotFoundError``)
    read PROPAGATES to the caller, which maps it to a typed :class:`ResumeStateError`
    (exit 1) — never a silent fallback (AI-E1-1).
    """
    # Latest-progress selection (deterministic, content-derived — AR11): a CHAINED
    # resume accumulates multiple run-state ledgers + halt reports in state/ (each
    # resume persists its own). Since each resume makes MONOTONIC forward progress,
    # the latest state = the MOST progress: the run-state ledger with the MOST
    # audited_deep entries, and the halt report with the LARGEST assessed_count. A
    # single (un-chained) prior run collapses to its one record. This needs no clock
    # / recency pointer — it is a pure content-derived selection over the scan.
    prior_ledger: CoverageLedger | None = None
    best_deep = -1
    prior_halt_report: HaltReport | None = None
    best_assessed = -1
    for locator in _list_locators(reader, "state"):
        envelope: Envelope = reader.read_envelope(locator)  # re-verifies content_hash
        producer = envelope.producer
        payload = envelope.payload
        if producer == _STATE_PRODUCER and isinstance(payload.get("ledger"), dict):
            candidate = CoverageLedger.model_validate(payload["ledger"])
            if candidate.deep_count() > best_deep:
                best_deep = candidate.deep_count()
                prior_ledger = candidate
        elif producer == _HALT_REPORT_PRODUCER:
            candidate_report = HaltReport.model_validate(payload)
            if candidate_report.assessed_count > best_assessed:
                best_assessed = candidate_report.assessed_count
                prior_halt_report = candidate_report

    if prior_ledger is None or prior_halt_report is None:
        raise ResumeStateError(
            "no prior .argus/ run-state + halt-report to resume "
            "(run a fresh audit first)"
        )

    findings: list[Recording] = []
    for locator in _list_locators(reader, "findings"):
        envelope = reader.read_envelope(locator)  # re-verifies content_hash
        if envelope.producer == _FINDING_PRODUCER:
            findings.append(Recording.model_validate(envelope.payload))
    return prior_ledger, prior_halt_report, findings


def _carried_forward_entries(
    prior_ledger: CoverageLedger, carried_forward_paths: tuple[str, ...]
) -> list[CoverageLedgerEntry]:
    """Reuse EVERY prior-ASSESSED entry VERBATIM — no re-audit (AC1, NFR-R2).

    The carried-forward entries are taken straight from the prior ledger (the SAME
    frozen ``CoverageLedgerEntry`` the prior run minted) for EVERY path in
    ``carried_forward_paths`` (the prior halt report's assessed set — ``audited_deep``,
    ``audited_shallow``, ``tool_scanned_only``, AND assessed-but-``skipped`` alike) —
    never re-graded, never a fabricated ``audited_*`` (the honest-degradation
    keystone). Reusing only the ``audited_deep`` subset would silently drop the
    assessed-non-deep coverage and break the AC2 byte-identity keystone. This is also
    the affordability win: a carried-forward file is NOT re-run through
    ``_detect_per_file``.
    """
    wanted = frozenset(carried_forward_paths)
    return [entry for entry in prior_ledger.entries if entry.file_path in wanted]


def resume_audit_detailed(
    request: AuditRequest,
    *,
    store_reader: ApaaStoreReader | None = None,
    store_writer: ApaaStoreWriter | None = None,
) -> AuditResult:
    """Resume an interrupted audit from on-disk ``.argus/`` state (FR31 / NFR-R2).

    The restore-and-continue loop (Story 3.4): (1) load the prior ``state/`` ledger
    + halt report + ``findings/`` via the 1-3 ``ApaaStoreReader`` (tamper-guarded —
    a tamper / corruption / unparseable / unknown-field / missing read maps to a
    typed :class:`ResumeStateError`, exit 1, NEVER a silent fallback — AI-E1-1); (2)
    load the repo at the pin + build the CURRENT index (the SAME loader/index as a
    fresh run); (3) build the PURE resume plan (``cost.resume.build_resume_plan`` —
    a divergent tree/commit raises ``ResumeError`` → ``ResumeStateError``); (4) run
    ``_detect_per_file`` ONLY over the resume-target entries (NOT the carried-forward
    files — the affordability win, AC1); (5) MERGE the carried-forward ``audited_deep``
    entries (reused verbatim) + the newly-audited entries + the still-skipped
    ``SKIPPED`` remainder into a SINGLE ``CoverageLedger.build`` (which re-sorts, so
    the merged ledger is the SAME an uninterrupted run produces — AC2); (6) re-fold
    through the UNCHANGED 1.6 gate + persist via the EXISTING ``_assemble_and_persist``.

    The resulting final ``.argus/`` verdict + ledger are BYTE-IDENTICAL to a single
    uninterrupted ``run(raised_budget)`` (the FR31/NFR-R2 keystone, AC2): the
    carried-forward entries are reused verbatim, the resume-target files are graded
    by the SAME deterministic detector path, the merge is a single re-sorting
    ``CoverageLedger.build``, and the verdict is the SAME ``evaluate_verdict`` fold.
    A resume whose RAISED budget still cannot cover the whole remainder halts AGAIN
    honestly (the still-skipped remainder stays ``SKIPPED``, the resumed halt report
    flags ``halted_on_exhaustion=True`` with the shrunken skipped set — AC4).

    Raises:
        ResumeStateError: a tamper / corruption / unparseable / unknown-field /
            missing-state read, a divergent tree/commit, or no prior state to resume
            (a :class:`PipelineError` subclass the CLI maps to exit ``1``).
        RepoIntakeError: the repo cannot be loaded at the pin — exit ``1``.
        WorkspaceContainmentError / CanonicalSerializationError / PipelineError: as
            for :func:`run_audit_detailed`.
    """
    try:
        intake = load_repo_at_commit(request.repo_path, request.commit)
    except RepoIntakeError:
        raise
    except Exception as exc:  # noqa: BLE001 — wrap as a TYPED fatal (never a bare raise)
        raise PipelineError(f"intake stage failed: {type(exc).__name__}") from exc

    repo_root = Path(request.repo_path)
    reader = store_reader if store_reader is not None else ApaaStoreReader(repo_root)

    # The prior-state READ (the impure 1-3 reader) — tamper-guarded. The 1-3 typed
    # read errors are mapped to a typed ResumeStateError (exit 1) — NEVER a silent
    # fallback to a fresh run that would mask the corruption (AI-E1-1, AC3).
    try:
        prior_ledger, prior_halt_report, prior_findings = _read_prior_state(reader)
    except ResumeStateError:
        raise
    except (StoreIntegrityError, canonical.CanonicalSerializationError) as exc:
        raise ResumeStateError(f"prior .argus/ state failed integrity check: {exc}") from exc
    except FileNotFoundError as exc:
        raise ResumeStateError(
            "a referenced prior .argus/ state file is missing (cannot resume)"
        ) from exc
    except ValidationError as exc:
        raise ResumeStateError(
            "prior .argus/ state has an invalid / unknown-field shape (cannot resume)"
        ) from exc
    except WorkspaceContainmentError:
        raise
    except Exception as exc:  # noqa: BLE001 — wrap unexpected read failures (AR10)
        raise ResumeStateError(f"prior .argus/ state read failed: {type(exc).__name__}") from exc

    try:
        detect_stack(repo_root, intake.source_files)
        index = build_ast_index(repo_root, intake.source_files, partition_id="root")
        raised_config = budget_config_from_budget(request.budget)
        # The PURE resume plan over the loaded prior records + the current index +
        # the raised config. A divergent tree/commit (a carried-forward path absent
        # from the current index) raises the typed ResumeError (mapped below).
        units = _build_cost_units(index.entries)
        plan: ResumePlan = build_resume_plan(
            prior_ledger, prior_halt_report, units, raised_config
        )
        # Detect ONLY over the resume-target entries (NOT the carried-forward files —
        # the affordability win, AC1). EVERY prior-assessed entry (all depths) is
        # reused VERBATIM from the prior ledger (NFR-R2 "no loss of prior coverage").
        target_set = frozenset(plan.resume_target_paths)
        target_entries = tuple(e for e in index.entries if e.file_path in target_set)
        new_entries, new_findings, candidates = _detect_per_file(repo_root, target_entries)
        carried = _carried_forward_entries(prior_ledger, plan.carried_forward_paths)
        still_skipped = _skipped_remainder_entries(plan.still_skipped_paths)
        merged_entries = carried + new_entries + still_skipped
        # Merge the carried-forward findings (loaded) with the newly-audited findings.
        # evaluate_verdict re-orders via order_findings, so the union (deduped by the
        # content-derived recording_id) matches the uninterrupted run's finding set
        # (AC2) — a carried-forward file is NOT re-detected, so its findings come from
        # the persisted set, never a second emission.
        #
        # Story 6.3 (DN-WHOLE-INDEX): orphan findings are CROSS-FILE, not per-file, so
        # they MUST NOT be carried forward — a prior PARTIAL run computed them over a
        # SUBSET of the repo (a smaller referenced-name universe ⇒ possibly MORE
        # apparent orphans), which would diverge from an uninterrupted run. They are
        # DROPPED from the prior set and RECOMPUTED fresh over the resumed assessed set
        # (carried-forward ∪ resume-target from the CURRENT index — the still-skipped
        # remainder excluded, mirroring run_audit_detailed). This makes the resumed
        # finding set byte-identical to an uninterrupted run(raised_budget) (AC2).
        prior_non_orphan = [f for f in prior_findings if f.rule_id != _ORPHAN_RULE_ID]
        merged_findings = _merge_findings(prior_non_orphan, new_findings)
        assessed_resume_set = target_set | frozenset(plan.carried_forward_paths)
        assessed_resume_entries = tuple(
            e for e in index.entries if e.file_path in assessed_resume_set
        )
        merged_findings = _merge_findings(
            merged_findings, _orphan_findings(index, assessed_resume_entries)
        )
        # The resumed halt report is RE-PROJECTED over the FULL current index at the
        # RAISED ceiling — the EXACT SAME call an uninterrupted run(raised_budget)
        # makes (run_audit_detailed: build_halt_report(_project_halt(index, config))).
        # This GUARANTEES the persisted halt-report bytes (assessed_files /
        # assessed_count / total_credits / skipped_on_exhaustion_files /
        # halted_on_exhaustion) are byte-identical to the uninterrupted run for ALL
        # assessed depths (AC2 keystone) — never reconstructed independently from the
        # plan (which omitted assessed-non-deep files and could diverge). The resume
        # PLAN still drives which files are detected vs carried-forward; the halt
        # REPORT is the deterministic projection over the same raised budget. A
        # divergence between the plan's split and this projection is impossible: both
        # use the SAME costs + the SAME >=-hard-ceiling decision over the SAME sorted
        # index (the plan seeds prior spend; the projection sums the same prefix).
        resumed_halt_report = build_halt_report(_project_halt(index.entries, raised_config))
    except ResumeError as exc:
        raise ResumeStateError(f"resume plan rejected the prior state: {exc}") from exc
    except (WorkspaceContainmentError, RepoIntakeError):
        raise
    except Exception as exc:  # noqa: BLE001 — wrap unexpected failures as TYPED (AR10)
        raise PipelineError(f"resume analysis stage failed: {type(exc).__name__}") from exc

    return _assemble_and_persist(
        request=request,
        repo_root=repo_root,
        index=index,
        source_files=intake.source_files,
        entries=merged_entries,
        findings=merged_findings,
        candidates=candidates,
        halt_report=resumed_halt_report,
        store_writer=store_writer,
    )


def _merge_findings(
    prior_findings: list[Recording], new_findings: list[Recording]
) -> list[Recording]:
    """Union the carried-forward + newly-audited findings, deduped by recording_id.

    The carried-forward files are NOT re-detected, so their findings are taken from
    the persisted ``findings/`` set; the resume-target files are freshly detected.
    Dedup by the content-derived ``recording_id`` (a finding the prior run already
    persisted is not double-counted if it also re-emits). ``evaluate_verdict``
    re-orders the union via ``order_findings``, so the result matches the
    uninterrupted run's finding set regardless of accumulation order (AC2).
    """
    by_id: dict[str, Recording] = {}
    for finding in prior_findings + new_findings:
        by_id.setdefault(finding.recording_id, finding)
    return list(by_id.values())


def resume_audit(
    request: AuditRequest,
    *,
    store_reader: ApaaStoreReader | None = None,
    store_writer: ApaaStoreWriter | None = None,
) -> AuditVerdict:
    """Resume an audit and return the pure :class:`AuditVerdict` (FR31).

    The simple resume entry mirroring :func:`run_audit`; see
    :func:`resume_audit_detailed` for the write locators + the full typed-error
    contract.
    """
    return resume_audit_detailed(
        request, store_reader=store_reader, store_writer=store_writer
    ).verdict
