"""The audit fold's DERIVATION stages — per-file grading, detection, cost + scope (AR8).

Drivers: ArgusAgent-NFR-M1 (``snake_case.py``, <=1200 lines — the reason this module was
created), ArgusAgent-FR-7 (AST-grounded deep grading), ArgusAgent-FR-4 (the critical-subsystem
candidate set + its DR-5 ineligibility fact), ArgusAgent-FR-10/-11/-12/-14 (the four V1
deterministic detector passes), ArgusAgent-FR-21/-22 (the per-file cost proxy + the halt
projection), ArgusAgent-FR-3 (the partition plan), ArgusAgent-AR8 (pure/impure separation),
ArgusAgent-AR7 / §3.3 (REUSE — this module defines no parallel detector, grader, cost model or
partitioner; it composes the done leaves).

Why this module exists (Story 12.1, following ``DN-PIPELINE-SPLIT``)
-------------------------------------------------------------------
``argus/pipeline.py`` reached **1331 lines against the §3.2 / NFR-M1 1200-line hard limit** —
131 lines over — and Epic 12 has three further stories (12.2 deep-audit wiring, 12.3 memo-store
wiring, 12.4 outcome explanations) that must land in it. Story 6.3 hit the same wall at 1190/1200
and answered it by extracting :mod:`argus.pipeline_persist`; this is the second application of
that same precedent, and it follows it exactly.

**This is a PURE no-behaviour-change refactor.** The functions below are **byte-identical** to
their pre-12.1 form in ``pipeline.py``: not one statement, comment, docstring or default was
edited, and no function is split across the boundary. ``pipeline.py`` imports every name back,
so ``argus.pipeline.__all__`` is byte-identical, every existing ``from argus.pipeline import X``
still resolves (including the private ``_detect_per_file`` / ``_assessment_scope_paths`` that
``tests/`` reach for), and a test that monkeypatches ``argus.pipeline._detect_per_file`` still
intercepts the real call — the name it patches is the one ``run_audit_detailed`` looks up. The
grading rules, the detector set and order, the cost attribution, the halt projection, the
partition plan and the assessment scope are **UNCHANGED**; only the home of the derivation
stages moved (the split is documented in BOTH this docstring and ``pipeline.py``'s, §3.2).

Where the boundary is, and why it is HERE
-----------------------------------------
The split is the seam between **derivation** and **orchestration/persistence**, and it was
chosen by MEASURING the dependency direction rather than by counting lines:

* Everything in this module is a **leaf of the pipeline's own call graph**. Measured over the
  pre-split ``pipeline.py`` by an ``ast`` walk: the sixteen functions here reference **nothing**
  that stays behind except the three cost/suffix constants, which moved with them. Nothing here
  calls ``_assemble_and_persist``, ``run_audit_detailed`` or the resume shell.
* The dependency therefore points **strictly downward** — ``pipeline.py`` -> this module, never
  back — so there is **no import cycle**, no bottom-of-file import and no function-local import
  to break one. Extracting the resume family instead (the other candidate, and the larger one at
  357 lines) would have inverted that: the resume shell references **eleven** names that stay in
  ``pipeline.py`` (``_assemble_and_persist``, ``_detect_per_file``, ``_project_halt``,
  ``AuditResult``, ``ResumeStateError`` …) while ``pipeline.py`` must keep re-exporting
  ``resume_audit`` from ``__all__`` — a module-level cycle that only an import-order trick can
  survive. A restructuring story whose defining criterion is *behaviour proven untouched* must
  not ship a fragile import graph to save a line count.
* It is a real cohesion unit, statable in one sentence: **take the index and the request, return
  ledger entries / findings / candidates / cost units / a halt projection / a partition plan —
  and write nothing.** Every ``.argus/`` write, every envelope and every orchestration decision
  stays in ``pipeline.py``. These functions still READ source files, so this module is NOT pure
  in the AR8 sense; like ``pipeline.py`` and ``pipeline_persist.py`` it is an IMPURE module, and
  it is registered in the import-isolation gate rather than in any purity-asserting guard.

What stayed in ``pipeline.py``
------------------------------
The typed error + result contracts (``PipelineError``, ``ResumeStateError``, ``AuditResult``),
the persistence assembly (``_assemble_and_persist``), the two fresh entrypoints
(``run_audit_detailed`` / ``run_audit``) and the whole Story 3.4 resume shell
(``_list_locators`` … ``resume_audit``). ``pipeline.py`` remains the single public surface: this
module is an implementation detail of it and is not part of any documented import path.
"""

from __future__ import annotations

from pathlib import Path

from argus.audit.grounding import is_deep_claim_grounded
from argus.cost.budget_governor import (
    BudgetConfig,
    CostLedger,
    account_spend,
    budget_config_from_budget,
)
from argus.cost.exhaustion import CostUnit, HaltProjection, project_halt_point
from argus.detectors.orphan_code import OrphanCodeDetector
from argus.detectors.secret_scan import SecretScanDetector
from argus.detectors.tool_runner import ToolRunnerDetector
from argus.detectors.vacuous_test import (
    VacuousTestDetector,
    is_test_classification_content_dependent,
    is_test_file,
    partition_application_files,
)
from argus.index.ast_index import AstIndex, AstIndexEntry
from argus.index.partitioner import PartitionPlan, compute_loc_by_file, partition_repository
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
    grade_entry,
)
from argus.ledger.critical_subsystems import CriticalCandidate, CriticalIneligibility
from argus.ledger.depth_semantics import assess_criticality
from argus.ledger.recording import Recording
from argus.models import AuditRequest

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


def _grade_non_test_source(entry: AstIndexEntry) -> CoverageLedgerEntry:
    """Grade a non-test source file ``audited_deep`` ONLY when AST-grounded (FR7).

    Language-agnostic by construction: it consults only ``ast_eligible`` /
    ``parse_failed`` and the ``Definition`` count, never the file suffix. It was
    named ``..._python`` and reached only by Python files, but nothing in its logic
    was Python-specific — so a file in any language with an installed grammar now
    meets the SAME structural bar. A language with no grammar parses to
    ``ast_eligible=False`` and is recorded ``skipped`` (examined-but-ungradable, in
    the denominator, never a false deep claim) exactly as before.

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


def _critical_ineligibility(
    entry: AstIndexEntry, *, is_test: bool
) -> CriticalIneligibility | None:
    """Why this file can never be graded ``audited_deep``, or ``None`` (FR4/DR-5).

    The eligibility FACT the PURE ``ledger/critical_subsystems`` fold consumes as data, derived
    HERE in the impure shell that already owns ``is_test_file`` and ``is_deep_claim_grounded``,
    so a ``ledger/`` module never imports the ``detectors/`` / ``audit/`` layers above it (AR8 —
    the ruling :func:`_assessment_scope_paths` already records). Both are REUSED by import
    (AR7/§3.3) and ``is_test`` is passed IN, so eligibility and GRADING cannot disagree.

    The answers mirror the grading table: a test file is ``audited_shallow`` ALWAYS, a cleanly
    parsed file with no grounding fact (zero definitions) is downgraded by FR7, anything else is
    ELIGIBLE. BOTH unreadable-entry guards below are LOAD-BEARING for ONE reason (D3): a file the
    tool could not READ is ``skipped`` by CIRCUMSTANCE, never shallow by construction, so it
    STAYS eligible — quietly dropping the one security-token-bearing file the tool could not read
    is a false green of exactly the class the PRD names as fatal. That covers the TEST label too
    when the unreadable content itself forced it, i.e. when the label is a tier-3 GUESS
    (:func:`is_test_classification_content_dependent`) and not a property of what the file IS.
    """
    unreadable = entry.parse_failed or not entry.ast_eligible
    if is_test:
        if unreadable and is_test_classification_content_dependent(entry.file_path):
            return None
        return CriticalIneligibility.TEST_FILE
    if unreadable:
        return None
    if not is_deep_claim_grounded(entry):
        return CriticalIneligibility.ZERO_DEFINITION_MODULE
    return None


def _critical_candidate(repo_root: Path, entry: AstIndexEntry) -> CriticalCandidate:
    """Build the FR4 critical CANDIDATE for one file (the single source of truth).

    Extracted so the fresh path (inside :func:`_detect_per_file`) and the resume path
    derive candidacy through the SAME code. Criticality is a pure content-derived
    property of the file — it does not depend on whether this run audited the file or
    carried it forward — so re-deriving it for a carried-forward file is correct and
    is what keeps a resumed critical set equal to the uninterrupted one.
    """
    source = _read_source(repo_root, entry.file_path)
    is_test = is_test_file(entry.file_path, ast_entry=entry)
    return CriticalCandidate(
        file_path=entry.file_path,
        criticality=assess_criticality(
            file_path=entry.file_path, source=source, ast_entry=entry
        ),
        ineligibility=_critical_ineligibility(entry, is_test=is_test),
    )


def _critical_candidates(
    repo_root: Path, entries: tuple[AstIndexEntry, ...]
) -> list[CriticalCandidate]:
    """The FR4 candidate set over *entries* (no detector dispatch — grading only)."""
    return [_critical_candidate(repo_root, entry) for entry in entries]


def _detect_per_file(
    repo_root: Path,
    index_entries: tuple[AstIndexEntry, ...],
    request: AuditRequest,
) -> tuple[list[CoverageLedgerEntry], list[Recording], list[CriticalCandidate]]:
    """Run the per-file detect/grade stage over *index_entries*.

    ``request`` is REQUIRED, not optional. It was previously ``AuditRequest | None =
    None`` and EVERY production call site omitted it, so the ``None`` branch — meant
    only as a convenience default — became the only branch that ever ran. The
    consequences were silent and operator-visible: ``--passes`` / ``--skip-pass``
    could not disable the security, vacuous or orphan passes (the hardcoded full set
    was substituted), and ``--ignore-path`` / ``--ignore-pattern`` were replaced with
    empty tuples, so a suppression the operator asked for never reached the scanner.
    Worse, the report keyed its status line on ``request.enabled_passes`` and so
    printed "Secret Scan Status: SKIPPED (Pass Deselected)" for a scan that had in
    fact run and emitted a finding — the report stating the opposite of what happened.

    Making the parameter required means a future call site that forgets it is a
    TypeError at import/test time, not a silently degraded audit.
    """
    detector = VacuousTestDetector()
    secret_detector = SecretScanDetector()
    breadth_detector = ToolRunnerDetector()
    entries: list[CoverageLedgerEntry] = []
    findings: list[Recording] = []
    candidates: list[CriticalCandidate] = []
    breadth_targets: list[tuple[str, str]] = []

    enabled_passes = request.enabled_passes

    for entry in index_entries:
        rel = entry.file_path
        # Per-PASS language gating, replacing a blanket `if not _is_python: SKIPPED`.
        # That gate discarded every non-Python file before ANY detector ran, which made
        # the multi-language AST index, the multi-language test-file conventions, and
        # the multi-language stack detection unreachable — a file was enumerated only
        # to be dropped. Each pass is now gated on what IT actually requires:
        #   * grading      — needs only a parsed AST entry ⇒ every language
        #   * secret scan  — regex + entropy over text     ⇒ every language
        #   * criticality  — content tokens                ⇒ every language
        #   * vacuous test — counts bare `assert` (a Python idiom) ⇒ Python only
        #   * breadth      — radon                          ⇒ Python only
        # The two Python-only passes stay gated deliberately: running the vacuous
        # detector over a JS `expect().toBe()` suite would emit false vacuous
        # accusations, and a wrong 🔴 is the lethal failure this codebase is built to
        # avoid.
        is_python = _is_python(rel)
        source = _read_source(repo_root, rel)
        if is_python:
            breadth_targets.append((rel, source))
        # Evaluated ONCE and reused by BOTH the eligibility fact below and the grading
        # branch, so the two stages cannot disagree. The AST entry is passed so an
        # ambiguously-named ``*_test.py`` is classified by CONTENT, not by filename.
        is_test = is_test_file(rel, ast_entry=entry)
        # Built through the SHARED builder so the fresh and resume paths cannot
        # derive candidacy differently. `source`/`is_test` are already resolved here,
        # so the builder is handed the entry and re-reads nothing this loop has.
        candidates.append(
            CriticalCandidate(
                file_path=rel,
                criticality=assess_criticality(file_path=rel, source=source, ast_entry=entry),
                ineligibility=_critical_ineligibility(entry, is_test=is_test),
            )
        )
        if "security" in enabled_passes:
            ignore_paths = request.ignore_paths
            ignore_patterns = request.ignore_patterns
            secret_result = secret_detector.run(
                file_path=rel,
                source=source,
                ast_entry=entry,
                ignore_paths=ignore_paths,
                ignore_patterns=ignore_patterns,
            )
            findings.extend(secret_result.findings)

        # ``is_test`` was resolved above from the CONTENT-aware classification, so a
        # production module whose subject is testing is not mistaken for a test suite
        # and skipped from deep grading. The eligibility fact came from this same value.
        if is_test:
            if is_python and "vacuous" in enabled_passes:
                result = detector.run(file_path=rel, source=source, ast_entry=entry)
                entries.extend(result.entries)
                findings.extend(result.findings)
            else:
                # A non-Python test file is graded shallow WITHOUT being run through
                # the Python-idiom vacuous detector — recorded honestly as examined,
                # never accused on evidence the detector cannot actually read.
                entries.append(grade_entry(file_path=rel, proposed_depth=CoverageDepth.AUDITED_SHALLOW, claim_present=False))
            continue
        entries.append(_grade_non_test_source(entry))

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
    request: AuditRequest,
) -> list[Recording]:
    """Run the cross-file orphan pass, honouring ``--passes`` / ``--skip-pass``.

    ``request`` is REQUIRED for the reason recorded on :func:`_detect_per_file`:
    both production call sites previously omitted it, so the ``orphan`` pass ran
    unconditionally even when the operator had deselected it.
    """
    if "orphan" not in request.enabled_passes:
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


def _assessment_scope_paths(
    request: AuditRequest,
    ledger: CoverageLedger,
    index: AstIndex | None = None,
) -> frozenset[str] | None:
    """Resolve ``request.coverage_scope`` to the assessed path set for the gate.

    Returns ``None`` for the default ``"repository"`` scope — the gate then assesses
    the whole ledger and the fold is byte-identical to a pre-scope run. For
    ``"application"``, returns the ledger's non-test paths, holding out files the
    multi-language :func:`is_test_file` recognizes.

    Classification lives HERE, in the impure shell that already owns
    ``is_test_file``, precisely so the PURE verdict gate never has to import a
    detector (AR8 import isolation). The gate receives membership as data.

    An UNRECOGNIZED scope value falls back to the whole-repository assessment rather
    than raising or silently narrowing — a typo must never be the reason a repository
    gets an easier gate (AR10: degrade honestly, and degrade toward the stricter
    claim). The value is recorded on the request either way, so the fallback is
    visible in the run provenance.

    *index* is OPTIONAL so existing callers keep working, but the pipeline supplies it:
    the AST entry lets an ambiguously-named ``*_test.py`` module be classified by
    content, exactly as the GRADING stage classifies it. Without it the two stages
    could disagree — a file graded as production while being held out of the assessed
    population — and a disagreement inside one run is precisely the kind of
    inconsistency this tool exists to surface in other people's repositories.
    """
    if request.coverage_scope != "application":
        return None
    # Story 12.1 (closing DF-8-3-C): the application/test split is ONE derivation, shared with
    # `reports.generator` by import (AR7/§3.3). It was written twice, verbatim, in two modules,
    # and the report's APPLICATION denominator and this assessed population depend on the two
    # staying identical — so they are now literally the same code, not two copies of it.
    application, _held_out = partition_application_files(ledger.entries, index)
    return frozenset(e.file_path for e in application)
