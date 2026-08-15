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

FR7 (Story 6.2, the V1 deep numerator): ``_grade_non_test_source`` consults the
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

Story 12.1 — the SECOND module split (the same DN-PIPELINE-SPLIT doctrine)
--------------------------------------------------------------------------
This module reached **1331 lines against the same 1200-line NFR-M1 hard limit** — 131
lines over, drifted from the 1199 that ``DF-8-2-A`` recorded at Story 8.2 — while Epic
12 has three further stories that must land here (12.2 deep-audit wiring, 12.3
memo-store wiring, 12.4 outcome explanations). The audit fold's DERIVATION stages
(``_is_python`` … ``_assessment_scope_paths`` — grade one file, run the four V1
detectors over it, derive the FR4 critical candidates, the per-file cost units, the
halt projection, the partition plan and the assessment scope) were extracted VERBATIM
into the sibling :mod:`argus.pipeline_stages`. **A PURE no-behaviour-change refactor:**
the moved functions are byte-identical to their pre-12.1 form, no function is split
across the boundary, this module imports every one of them back under its original
private name, ``__all__`` is byte-identical and every import path — public and private
— is unchanged. The verdict math, the detector set and order, the grading rules, the
cost attribution and the persist order are UNCHANGED; only the home of the derivation
stages moved (the split documented in BOTH this docstring and
``pipeline_stages.py``'s, §3.2).

The boundary is the seam between DERIVATION and ORCHESTRATION/PERSISTENCE, and it was
chosen by measuring the dependency direction: the extracted family references nothing
that stays behind (only the three cost/suffix constants, which moved with it), so the
dependency points strictly downward and there is **no import cycle**. What stays here
is the orchestration: the typed error/result contracts, ``_assemble_and_persist``,
``run_audit_detailed`` / ``run_audit`` and the whole Story 3.4 resume shell. NFR-M1 is
now enforced repo-wide by ``tests/test_module_size_ceiling.py``
(``TC-ArgusAgent-MAINT-001-01``..``-05``) rather than per-module, which is why the
drift this split repairs cannot recur silently.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import ValidationError

from argus.cache.memo_store import RecordedStageResult
from argus.cache.stage_memo import memoize_detect_stage
from argus.detectors.orphan_code import RULE_ORPHAN_CODE
from argus.index.ast_index import AstIndex, build_ast_index
from argus.cost.budget_governor import budget_config_from_budget
from argus.cost.exhaustion import (
    HaltReport,
    InsufficientCoverageFloorReport,
    build_floor_report,
    build_halt_report,
)
from argus.cost.resume import (
    ResumeError,
    ResumePlan,
    build_resume_plan,
)
from argus.intake.repo_loader import (
    RepoIntake,
    RepoIntakeError,
    load_repo_at_commit,
    to_native_fs_path,
)
from argus.intake.source_state import (
    SourceState,
    SourceStateError,
    resolve_source_state,
)
from argus.intake.stack_detect import detect_stack
from argus.ledger.coverage_ledger import CoverageLedger, CoverageLedgerEntry
from argus.ledger.coverage_report import CoverageReport, build_coverage_report
from argus.ledger.critical_subsystems import (
    CriticalCandidate,
    critical_subsystems_not_deep,
    identify_critical_subsystems,
)
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

# Story 12.1 (following Story 6.3's DN-PIPELINE-SPLIT) — the audit fold's DERIVATION stages
# now live in :mod:`argus.pipeline_stages`, the single source of truth for them. They are
# imported back HERE, under their original private names, so `argus.pipeline.__all__` is
# byte-identical, every existing `from argus.pipeline import X` (including the private
# `_detect_per_file` / `_assessment_scope_paths` that `tests/` reach for) still resolves, and a
# test that monkeypatches `argus.pipeline._detect_per_file` still intercepts the real call —
# the orchestrators below look the name up in THIS module's namespace at call time.
from argus.pipeline_stages import (
    _assessment_scope_paths,
    _build_cost_ledger,
    _build_cost_units,
    _build_partition_plan,
    _compute_loc_map,
    _critical_candidate,
    _critical_candidates,
    _critical_ineligibility,
    _detect_per_file,
    _grade_non_test_source,
    _is_python,
    _orphan_findings,
    _project_halt,
    _read_source,
    _skipped_remainder_entries,
    _unit_cost,
)
from argus.reports.generator import generate_reports

# The ONE deep-pass token (Story 12.2). Imported from its single declaration site, so the
# flag, the pass set, the gated call site below and the disclosure cannot drift apart
# (AR7 / §3.3 — reuse, never fork). `plain_english` is a PURE renderer with no provider
# dependency, so this import does not touch the zero-token quarantine.
from argus.reports.plain_english import deep_pass_enabled

# The ONE grammar-failure classifier (Story 10.4 / DN-3). Imported for the pure fold that
# puts the downgraded-file population on `AuditResult` (Story 12.8 / AC7) — a `startswith`
# at this call site is the defect that module's docstring names.
from argus.shared.grammar_status import downgrade_reasons
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

# ⚠️ `UnexpectedStageError` (Story 12.8 / AC5) is DELIBERATELY ABSENT from this list, and the
# absence is a decision rather than an oversight. `__all__` here is a FROZEN pin: Story 12.1
# promised across the `pipeline_stages` extraction that the published import surface did not
# move, and `tests/test_pipeline_split_surface.py` (`-14`/`-15`/`-16`) holds it against the
# IMMUTABLE pre-split blob `ca37283:argus/pipeline.py` — so the pin cannot accommodate an
# addition without being re-anchored, which would be a second, unrelated published-surface
# change taken inside a story whose DN-6 states it adds explanation and not surface. The
# class is fully importable (`from argus.pipeline import UnexpectedStageError`; `__all__`
# governs only `import *`), documented at its own definition and in `argus/cli.py`'s contract
# block, and ENUMERATED where the enumeration is load-bearing — `plain_english
# .TYPED_FAILURE_CLASSES`, which `TC-ArgusAgent-REPORT-003-08` closes over the real classes to
# keep honest. Widening this list is the right move for a story that says so.
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



class PipelineError(ValueError):
    """A TYPED fatal pipeline failure the CLI maps to exit ``1`` (AR10 / NFR-R1).

    A ``ValueError`` subclass (mirroring ``RepoIntakeError`` /
    ``WorkspaceContainmentError`` / ``CanonicalSerializationError``). Wraps an
    unexpected error so the CLI prints a secret-safe stderr message + returns ``1``
    rather than letting a bare Python traceback escape. The message names the
    failing STAGE + the typed reason only — never an absolute host path, never
    source / secret bytes (NFR-S1).
    """


class UnexpectedStageError(PipelineError):
    """An UNEXPECTED exception inside a stage — an Argus defect, not a degradation (``DF-8-4-D``).

    Story 12.8 / AC5. The entry was filed against ``cli.py``'s ``except ValueError`` arm, and
    the measured trap is that splitting THAT arm alone cannot close it: the four wrap sites in
    this module already converted **any** unexpected exception into a ``PipelineError``, which
    is one of the typed classes the CLI's own comment enumerates as an EXPECTED degradation. So
    an internal defect arrived at the CLI **pre-disguised**, and no amount of ``except``
    precision downstream could tell it apart from a stage that refused for a good reason.

    The distinction is therefore carried FROM THE WRAP SITE, which is the only place that
    still knows the difference. This subclass is the smallest honest mechanism:

    * it is a ``PipelineError``, so every existing ``except PipelineError`` / ``except
      ValueError`` handler catches it exactly as before — nothing downstream changes shape;
    * it changes NO exit code. Both stay ``1`` (AR3 is frozen; AR7 — reuse, never fork). The
      distinction lives in the MESSAGE, which is what the ledger entry asks for;
    * it carries ``type(exc).__name__`` and **never** ``str(exc)`` — ``DF-10-4-C``'s rule and
      NFR-S1's, because ``str(OSError)`` is ``[Errno 13] Permission denied: '<absolute host
      path>'``.

    The alternative considered and rejected (recorded in the story's Dev Agent Record): a
    boolean/flag attribute on ``PipelineError`` set at the wrap sites. It needs no new class,
    but an attribute is invisible to ``except``, so every consumer would have to remember to
    read it — and a distinction a caller can forget to check is the one that goes back to
    being silent. A type is checked by the language.
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

    Story 12.8 (NFR-P3 / ``DF-10-4-C`` / AC7): ``grammar_downgrade_reasons`` carries the
    recorded ``parse_failure_reason`` TOKENS of the files a grammar failure downgraded, so
    the CLI can render ``plain_english.render_grammar_downgrade_summary`` on a DEFAULT run.
    Before it, that sentence had exactly one production caller — the report renderer, which
    runs only when ``--report-dir`` is set — so an operator on a default invocation saw a
    lower coverage ratio and NO reason for it, which reads as a judgement about their code.
    It rides HERE and not on ``AuditVerdict`` deliberately (DN-4): the verdict is the frozen,
    PERSISTED FR18/AR3 contract and a field there costs a schema bump; this class is
    explicitly *a thin value holder (NOT a persisted model)* and already carries three
    optional additive fields added by Stories 3.3, 4.1 and 4.3 by exactly this reasoning.
    **Nothing new is persisted** — the tokens are already on the AST index this is derived
    from, and the exception MESSAGE is never carried (10.4 / DN-5, NFR-S1).

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
        "grammar_downgrade_reasons",
    )

    def __init__(
        self,
        verdict: AuditVerdict,
        locators: tuple[str, ...],
        floor_report: InsufficientCoverageFloorReport | None = None,
        negative_assurance: NegativeAssuranceVerdict | None = None,
        coverage_report: CoverageReport | None = None,
        grammar_downgrade_reasons: tuple[str, ...] = (),
    ) -> None:
        self.verdict = verdict
        self.locators = locators
        self.floor_report = floor_report
        self.negative_assurance = negative_assurance
        self.coverage_report = coverage_report
        self.grammar_downgrade_reasons = grammar_downgrade_reasons


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
    source_state: SourceState | None = None,
    deep_port: object = None,
    disclose: object = None,
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
    # Story 12.2 (FR36 / DN-DEEP-OPT-IN): the OPT-IN LLM-backed deep pass runs HERE,
    # after the deterministic detect/grade stage produced the ledger entries and BEFORE
    # the verdict fold — because its whole job is to justify (or withdraw) the
    # `audited_deep` grades those entries claim, and a grade that is withdrawn must move
    # the ratio the FR16 gate reads.
    #
    # THE IMPORT IS FUNCTION-LOCAL AND THAT IS LOAD-BEARING, NOT STYLE. `ast.walk`
    # descends into function bodies, so the STATIC closure from `argus.cli` contains
    # `argus.audit.deep_pass` → `argus.audit.deep_audit` (which is what proves FR36
    # `wired` — TC-ArgusAgent-DOCS-001-34); but the statement never EXECUTES on a default
    # run, so `argus.audit.deep_audit` stays absent from `sys.modules` and the NFR-S6
    # zero-token quarantine holds (TC-ArgusAgent-PIPELINE-001-10). Because that green is
    # obtained by NOT EXECUTING, it is not evidence on its own — TC-ArgusAgent-PIPELINE-001-11
    # is the positive control that makes it one.
    #
    # `deep` is absent from `_ALL_PASSES`, so a bare invocation never enters this branch
    # and a default run is byte-identical to a pre-12.2 run (AC2.4). The shape mirrors
    # the `if "prosecutor" in request.enabled_passes:` precedent below.
    deep_outcome = None
    if deep_pass_enabled(request.enabled_passes):
        from argus.audit.deep_pass import run_deep_pass

        deep_result = run_deep_pass(
            entries=tuple(entries),
            index_entries=index.entries,
            budget=request.budget,
            spent_credits=halt_report.total_credits,
            port=deep_port,  # type: ignore[arg-type]
            disclose=disclose,
        )
        entries = list(deep_result.entries)
        findings = findings + list(deep_result.findings)
        deep_outcome = deep_result.outcome

    # The merged ledger (CoverageLedger.build re-sorts, so the merge order does not
    # matter — a resumed merge is the SAME sorted ledger an uninterrupted run
    # produces, AC2) is re-folded through the UNCHANGED 1.6 evaluate_verdict.
    ledger = CoverageLedger.build(entries)
    critical = identify_critical_subsystems(
        candidates,
        operator_designated=request.critical_paths,
        operator_excluded=request.excluded_critical_paths,
    )
    # The offending paths ARE the boolean's evidence (all_deep ⇔ not_deep is empty),
    # so both come from one call and cannot disagree.
    not_deep = critical_subsystems_not_deep(critical.paths, ledger)
    all_deep = not not_deep
    # Resolved ONCE and reused by the Prosecutor's re-fold below, so both folds
    # assess the identical population.
    scope_paths = _assessment_scope_paths(request, ledger, index)
    verdict = evaluate_verdict(
        ledger,
        tuple(findings),
        critical_subsystems_all_deep=all_deep,
        critical_subsystems_not_deep=not_deep,
        scope_paths=scope_paths,
        deep_pass=deep_outcome,
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
            scope_paths=scope_paths,
            # Audit-unit membership, so the cut-edge pass reports one finding per
            # SEAM rather than one per crossing call (which restates the call graph).
            file_to_partition={
                path: partition.partition_id
                for partition in partition_plan.partitions
                for path in partition.work_manifest.files
            },
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
        generate_reports(
            request,
            verdict,
            ledger,
            finding_dicts,
            target_dir,
            source_state=source_state,
            ast_index=index,
        )


    return AuditResult(
        verdict=verdict,
        locators=locators,
        floor_report=floor_report,
        negative_assurance=negative_assurance,
        coverage_report=build_coverage_report(ledger),
        # Story 12.8 / AC7 — DERIVED from the index this run already built, persisted
        # nowhere, and classified by the ONE classifier (`grammar_status.classify_reason`).
        # This is the channel 12.5 left open by name: the downgrade sentence existed and
        # only the report renderer could reach it, so a default run said nothing.
        grammar_downgrade_reasons=downgrade_reasons(index.entries),
    )



def run_audit_detailed(
    request: AuditRequest,
    *,
    store_writer: ApaaStoreWriter | None = None,
    deep_port: object = None,
    disclose: object = None,
) -> AuditResult:
    """Run the sequential audit pipeline → :class:`AuditResult` (verdict + locators).

    The IMPURE shell: it reads the FS (1.4 loader/index, source reads) and writes
    the ``.argus/`` tree (1.3 store); the pure cores it folds (ledger build, verdict
    fold, serializer) stay pure. The DEFAULT path calls NO LLM (zero-token, NFR-D2).

    Story 12.2 adds two OPTIONAL keyword seams, both inert unless the operator opted in
    with ``--deep-audit`` (FR36 — off by default, always):

    * *deep_port* — an injected :class:`~argus.audit.ports.LLMDispatchPort` (AR7). Typed
      ``object`` deliberately: annotating it with the port TYPE would require importing
      ``argus.audit.ports`` at module scope, which is precisely the import the NFR-S6
      zero-token quarantine forbids on this path. The seam validates it structurally.
      Tests inject a ``FakeDispatch`` and consume zero LLM tokens (NFR-D2).
    * *disclose* — a one-argument callable receiving the egress disclosure BEFORE the
      first dispatch (AC2.5). The CLI passes its stderr writer.

    Raises:
        RepoIntakeError: the repo cannot be loaded at the pin (missing path /
            drifted tree / unresolvable commit) — the CLI maps this to exit ``1``.
        WorkspaceContainmentError: a ``.argus/`` write escaped containment — exit ``1``.
        CanonicalSerializationError: a payload was not canonically serializable — exit ``1``.
        PipelineError: any other unexpected stage failure (wrapped, typed) — exit ``1``.
    """
    try:
        # Resolve whichever source state is present rather than demanding a clean
        # commit up front (AR10). ``strict=True`` restores the original refuse-on-drift
        # contract for a release gate; the default audits what is actually there and
        # RECORDS which state it was.
        source_state = resolve_source_state(
            request.repo_path, commit=request.commit, strict=request.strict
        )
        intake = RepoIntake(
            commit_sha=source_state.identity, source_files=source_state.source_files
        )
    except (RepoIntakeError, SourceStateError):
        raise  # already typed (AR10) — the CLI maps it to exit 1
    except Exception as exc:  # noqa: BLE001 — wrap as a TYPED fatal (never a bare raise)
        raise UnexpectedStageError(f"intake stage failed: {type(exc).__name__}") from exc

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
        else:
            assessed_entries = index.entries

        def _run_detect_stage() -> RecordedStageResult:
            """The recording-producing closure itself: the detect/grade + orphan passes.

            Story 6.3 (DN-WHOLE-INDEX): the single cross-file orphan pass runs AFTER the
            per-file detect stage, over the ASSESSED entries only. Findings-only —
            appended to the existing accumulation; a no-orphan repo stays byte-identical.
            """
            staged, found, cands = _detect_per_file(repo_root, assessed_entries, request)
            return RecordedStageResult(
                entries=tuple(staged),
                findings=tuple(found) + tuple(_orphan_findings(index, assessed_entries, request)),
                candidates=tuple(cands),
            )

        # Story 12.3 (FR27 / NFR-D1 / DN-1): THE MEMOIZATION HOOK. It wraps the
        # deterministic stage above and nothing else — a second run over an unchanged
        # closure is SERVED the recorded result instead of recomputing it, and the served
        # answer is byte-identical to the computed one because it IS the same canonical
        # bytes. The store is advisory: every typed cache failure degrades to a recompute,
        # so the verdict is correct whether or not the cache exists, is warm, or is wiped.
        #
        # 🔴 SCOPE: this covers the DETERMINISTIC component ONLY. The opt-in deep pass runs
        # DOWNSTREAM, inside `_assemble_and_persist`, and is never served from the store —
        # so with `--deep-audit` on, a re-run dispatches again and PRD §501 is NOT
        # delivered (DF-12-3-A; the reasoning and the model-collision hazard are in
        # `argus/cache/stage_memo.py`'s module docstring, and the fence that makes the
        # hazard impossible is `memo_store._fence_llm_derived`).
        stage = memoize_detect_stage(
            repo_root=repo_root,
            request=request,
            index=index,
            assessed_entries=assessed_entries,
            source_state=source_state,
            compute=_run_detect_stage,
        )
        entries = list(stage.result.entries)
        findings = list(stage.result.findings)
        candidates = list(stage.result.candidates)
        if halt_projection.halted_on_exhaustion:
            # Appended OUTSIDE the memoized payload: the skipped remainder is a pure
            # function of the halt projection, not of the detectors, so memoizing it would
            # store a derivable value. `work_manifest_files` already folds the ASSESSED
            # set into the key, so a run that halts at a different point reads a different
            # slot and cannot be served this one's entries.
            entries = entries + _skipped_remainder_entries(halt_projection.skipped_paths)
        halt_report = build_halt_report(halt_projection)
    except (WorkspaceContainmentError, RepoIntakeError):
        raise
    except Exception as exc:  # noqa: BLE001 — wrap unexpected failures as TYPED (AR10)
        raise UnexpectedStageError(f"analysis stage failed: {type(exc).__name__}") from exc

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
        source_state=source_state,
        deep_port=deep_port,
        disclose=disclose,
    )


def run_audit(
    request: AuditRequest,
    *,
    store_writer: ApaaStoreWriter | None = None,
    deep_port: object = None,
    disclose: object = None,
) -> AuditVerdict:
    """Run the pipeline and return the pure :class:`AuditVerdict` (FR30).

    The simple entry the CLI calls: wires the six stages, persists the artifacts,
    and returns the verdict the CLI reads ``exit_code`` from. See
    :func:`run_audit_detailed` for the write locators, the full typed-error contract,
    and the two Story-12.2 deep-pass seams (*deep_port* / *disclose*), which are inert
    unless the operator opted in.
    """
    return run_audit_detailed(
        request, store_writer=store_writer, deep_port=deep_port, disclose=disclose
    ).verdict


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


def _to_native_payload(payload: Any) -> Any:
    """Re-express a payload read back from ``.argus/`` in the host's NATIVE string form.

    THE RESUME HALF of the host-locale boundary, and the exact mirror of the repair
    ``store.canonical.canonicalize`` applies to every string on the way OUT.

    The in-memory convention everywhere else in this module is the OS-NATIVE path
    string: a fresh run gets its file set from ``resolve_source_state`` (an ``os.walk``,
    which inherits the host's filename decoding) and ``load_repo_at_commit`` now matches
    it. Only the serializer converts to the portable recorded form, so ``.argus/`` bytes
    are identical on every host (NFR-P1).

    Resume is the ONE place that flow runs backwards: prior paths re-enter memory in
    their RECORDED form. On POSIX under ``LC_ALL=C`` those two forms differ — the ledger
    holds ``'src/caf\\xe9_calc.py'`` while the current index holds
    ``'src/caf\\udcc3\\udca9_calc.py'`` — so ``build_resume_plan`` found every
    carried-forward path "absent from the current index" and refused the resume as a
    diverged tree (a plausible-looking, entirely wrong diagnosis: nothing had diverged).

    Converting the whole payload tree rather than named path fields is deliberate. It
    mirrors ``canonicalize``'s own blanket walk, so the two cannot drift apart as models
    gain fields, and it cannot silently miss a nested locator. Non-path strings round
    trip exactly (the serializer restores them on write), so the persisted bytes are
    unchanged and the AC2 byte-identity keystone holds. On a UTF-8 host every conversion
    is an identity.
    """
    if isinstance(payload, str):
        return to_native_fs_path(payload)
    if isinstance(payload, dict):
        return {key: _to_native_payload(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_to_native_payload(item) for item in payload]
    return payload


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
            candidate = CoverageLedger.model_validate(_to_native_payload(payload["ledger"]))
            if candidate.deep_count() > best_deep:
                best_deep = candidate.deep_count()
                prior_ledger = candidate
        elif producer == _HALT_REPORT_PRODUCER:
            candidate_report = HaltReport.model_validate(_to_native_payload(payload))
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
            findings.append(Recording.model_validate(_to_native_payload(envelope.payload)))
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
        raise UnexpectedStageError(f"intake stage failed: {type(exc).__name__}") from exc

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
        new_entries, new_findings, _target_candidates = _detect_per_file(
            repo_root, target_entries, request
        )
        # ── The FR4 critical-candidate set must span the WHOLE assessed population ──
        # `_detect_per_file` returns candidates only for the entries it was given, and
        # this call is deliberately narrowed to the resume TARGETS (the affordability
        # win). Using its candidate list directly therefore silently omitted every
        # CARRIED-FORWARD file from `identify_critical_subsystems`, which feeds both
        # the persisted critical-subsystem artifact and the `critical_subsystems_all_deep`
        # clause of the verdict. A resumed run could then persist a different critical
        # set — and reach a different verdict — than the uninterrupted
        # `run(raised_budget)` this function's AC2 keystone promises to be
        # byte-identical to.
        #
        # Criticality is a pure content-derived property of a file (`assess_criticality`
        # + the DR-5 eligibility fact), not a property of WHEN it was audited, so it is
        # re-derived here over the full assessed set. This costs one source read per
        # carried-forward file and no detector dispatch, so the affordability win the
        # narrowing exists for is preserved.
        assessed_resume_set = target_set | frozenset(plan.carried_forward_paths)
        assessed_resume_entries = tuple(
            e for e in index.entries if e.file_path in assessed_resume_set
        )
        candidates = _critical_candidates(repo_root, assessed_resume_entries)
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
        # `assessed_resume_entries` is the SAME population the critical-candidate set
        # above was derived over — resolved once, so the two cannot disagree.
        merged_findings = _merge_findings(
            merged_findings, _orphan_findings(index, assessed_resume_entries, request)
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
        raise UnexpectedStageError(f"resume analysis stage failed: {type(exc).__name__}") from exc

    # Provenance for the RENDERED reports only. A fresh run resolves this and passes
    # it; the resume path omitted it, so a resumed run's report silently dropped the
    # "which source state was audited" disclosure. Resolution is best-effort and
    # non-fatal: the resume itself already validated the tree via the intake above, so
    # a failure here must degrade the DISCLOSURE, never the run (AR10). It does not
    # touch the persisted `.argus/` bytes, so AC2 byte-identity is unaffected.
    try:
        resumed_source_state: SourceState | None = resolve_source_state(
            request.repo_path, commit=request.commit, strict=request.strict
        )
    except (SourceStateError, RepoIntakeError):  # pragma: no cover - disclosure-only degrade
        resumed_source_state = None

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
        source_state=resumed_source_state,
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
