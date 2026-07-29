"""IMPURE ``.argus/`` persistence helpers extracted from the audit pipeline (AR8).

Drivers: ArgusAgent-NFR-P1 (sequential byte-identical ``.argus/`` output), ArgusAgent-NFR-S1
(no source / secret / absolute-host-path bytes in artifacts), ArgusAgent-NFR-S5 (all FS
writes containment-checked — via 1.3), AR8 (pure/impure separation — this module
holds the IMPURE persist shell that writes through the 1.3 ``ApaaStoreWriter``; it
adds NO new serializer / ledger / finding / verdict model, NO direct ``json.dumps``
/ ``open()``), AR11 (``.argus/`` filenames from content-sha256 / a stable id, never
arrival order), ArgusAgent-NFR-M1 (≤1200-line files — Story 6.3 DN-PIPELINE-SPLIT).

Why this module exists (Story 6.3 / DN-PIPELINE-SPLIT — the cohesion split)
---------------------------------------------------------------------------
``pipeline.py`` reached the §3.2 1200-line hard limit (1190/1200) at Story 6.2, so
the Story 6.3 orphan-detector WIRING had no room to land. Per DN-PIPELINE-SPLIT
this is a PURE no-behavior-change refactor: the cohesive ``.argus/`` persist family
(every ``_persist_*`` writer helper — the single concern "write a built artifact
through the 1.3 store") is lifted out of ``pipeline.py`` into this sibling so the
orchestrator file drops well below 1200 lines. The functions are byte-identical to
their pre-6.3 form; ``pipeline.py`` imports them and the public ``run_audit`` /
``run_audit_detailed`` / ``resume_audit_detailed`` entrypoints + their import
locations are unchanged. The verdict math / persist order / producer tokens are
UNCHANGED — only the home of the persist helpers moved (the split documented in
BOTH this docstring and ``pipeline.py``'s docstring, §3.2).

These functions are leaf persistence helpers: each takes an already-built pure
artifact + the 1.3 writer and returns the ``.argus/``-root-relative content-addressed
locators. They do no detection, no verdict fold, no LOC/cost build — those stay in
``pipeline.py``.
"""

from __future__ import annotations

from argus.cost.budget_governor import CostLedger
from argus.cost.exhaustion import HaltReport
from argus.index.partitioner import PartitionPlan, build_plan_payload
from argus.ledger.coverage_ledger import CoverageLedger
from argus.ledger.critical_subsystems import CriticalSubsystemSet
from argus.models import AuditRequest
from argus.store.envelope import EnvelopeWriter
from argus.store.writer import ApaaStoreWriter
from argus.verdict.negative_assurance import NegativeAssuranceVerdict
from argus.verdict.verdict_gate import AuditVerdict

__all__ = [
    "VERDICT_PRODUCER",
    "FINDING_PRODUCER",
    "STATE_PRODUCER",
    "RUN_STATE_SCHEMA_VERSION",
    "PARTITION_PLAN_PRODUCER",
    "WORK_MANIFEST_PRODUCER",
    "COST_LEDGER_PRODUCER",
    "HALT_REPORT_PRODUCER",
    "NEGATIVE_ASSURANCE_PRODUCER",
    "CRITICAL_SUBSYSTEMS_PRODUCER",
    "persist_verdict",
    "persist_cost_ledger",
    "persist_halt_report",
    "persist_negative_assurance",
    "persist_critical_subsystems",
    "persist_partitions",
]

# Producer tokens for the persisted envelopes (provenance, not a path/secret).
VERDICT_PRODUCER = "argus.pipeline.verdict"
FINDING_PRODUCER = "argus.pipeline.finding"
STATE_PRODUCER = "argus.pipeline.run_state"

# Schema version for the persisted run-state payload (localized constant).
RUN_STATE_SCHEMA_VERSION = "1"

# Story 2.4 — partition-plan + per-unit work-manifest producer tokens (provenance).
PARTITION_PLAN_PRODUCER = "argus.pipeline.partition_plan"
WORK_MANIFEST_PRODUCER = "argus.pipeline.work_manifest"

# Story 3.1 — cost-ledger snapshot producer token (provenance, not a path/secret).
COST_LEDGER_PRODUCER = "argus.pipeline.cost_ledger"

# Story 3.2 — halt-report snapshot producer token (provenance, not a path/secret).
HALT_REPORT_PRODUCER = "argus.pipeline.halt_report"

# Story 4.1 — negative-assurance wrapper + computed critical-subsystem-set producer
# tokens (provenance, not a path/secret). The negative-assurance wrapper is the
# FR17/NFR-A3 surface; the critical-subsystem set persistence closes DF-2-3-B.
NEGATIVE_ASSURANCE_PRODUCER = "argus.verdict.negative_assurance"
CRITICAL_SUBSYSTEMS_PRODUCER = "argus.pipeline.critical_subsystems"


def persist_verdict(
    writer: ApaaStoreWriter,
    request: AuditRequest,
    verdict: AuditVerdict,
    ledger: CoverageLedger,
) -> tuple[str, ...]:
    """Persist the verdict envelope + findings + run-state through the 1.3 store.

    REUSES ``EnvelopeWriter.build`` + the single 1.1 ``canonical`` serializer (no
    second serializer, no direct ``json.dumps`` / ``open()`` — the AST gate
    enforces it). Filenames are content-addressed (AR11). Returns the
    ``.argus/``-root-relative locators (verdict first, then findings in their
    already-ordered sequence, then run-state). The run-state records the request's
    NON-path provenance + the ledger snapshot — never ``repo_path`` (NFR-S1).
    """
    writer.paths.ensure_tree()
    locators: list[str] = []

    verdict_locator = writer.write_payload(
        "state",
        verdict.to_canonical_payload(),
        schema_version=verdict.schema_version,
        producer=VERDICT_PRODUCER,
    )
    locators.append(verdict_locator)

    for finding in verdict.ordered_findings:
        locators.append(
            writer.write_payload(
                "findings",
                finding.model_dump(mode="json"),
                schema_version=finding.schema_version,
                producer=FINDING_PRODUCER,
            )
        )

    run_state = {
        "schema_version": RUN_STATE_SCHEMA_VERSION,
        "request": request.to_provenance_payload(),
        "ledger": ledger.model_dump(mode="json"),
        "verdict": verdict.verdict.value,
        "exit_code": verdict.exit_code,
    }
    locators.append(
        writer.write_payload(
            "state",
            run_state,
            schema_version=RUN_STATE_SCHEMA_VERSION,
            producer=STATE_PRODUCER,
        )
    )
    return tuple(locators)


def persist_cost_ledger(writer: ApaaStoreWriter, cost_ledger: CostLedger) -> tuple[str, ...]:
    """Persist the cost-ledger snapshot to ``state/`` through the 1.3 store (Story 3.1).

    Additive (AC5): the snapshot lands content-addressed in ``state/`` via the
    EXISTING ``ApaaStoreWriter.write_payload`` → ``EnvelopeWriter.build`` → the
    single 1.1 ``canonical`` serializer (no second serializer / json.dumps — the
    AST gate enforces it). The bytes come from ``cost_ledger.to_canonical_payload``
    (LIVE ``Fraction`` → the canonical ``num/den`` encoding, never ``model_dump``'s
    ``str`` coercion). The payload carries ONLY ``int``/``Fraction``/``bool``/``str``
    provenance — never an absolute host path / source / secret byte (NFR-S1). This
    is the seam Story 3.4 reads to restore accumulated spend; this story PERSISTS
    it (it does NOT build the restore-and-continue loop).
    """
    return (
        writer.write_payload(
            "state",
            cost_ledger.to_canonical_payload(),
            schema_version=cost_ledger.schema_version,
            producer=COST_LEDGER_PRODUCER,
        ),
    )


def persist_halt_report(writer: ApaaStoreWriter, report: HaltReport) -> tuple[str, ...]:
    """Persist the halt report to ``state/`` through the 1.3 store (Story 3.2, additive).

    Additive (AC5): the report lands content-addressed in ``state/`` via the
    EXISTING ``ApaaStoreWriter.write_payload`` → ``EnvelopeWriter.build`` → the
    single 1.1 ``canonical`` serializer (no second serializer / json.dumps — the
    AST gate enforces it). The payload (``report.to_canonical_payload()``) carries
    ONLY ``int``/``bool``/``str`` provenance + repo-relative POSIX paths — never an
    absolute host path / source / secret byte (NFR-S1). This is part of the seam
    Story 3.4 reads to restore the prior partial coverage; this story PERSISTS it
    (it does NOT build the restore-and-continue loop).
    """
    return (
        writer.write_payload(
            "state",
            report.to_canonical_payload(),
            schema_version=report.schema_version,
            producer=HALT_REPORT_PRODUCER,
        ),
    )


def persist_negative_assurance(
    writer: ApaaStoreWriter, wrapper: NegativeAssuranceVerdict
) -> tuple[str, ...]:
    """Persist the negative-assurance wrapper to ``state/`` through the 1.3 store (Story 4.1).

    Additive (AC5): the wrapper lands content-addressed in ``state/`` via the
    EXISTING ``ApaaStoreWriter.write_payload`` → ``EnvelopeWriter.build`` → the
    single 1.1 ``canonical`` serializer (no second serializer / json.dumps — the AST
    gate enforces it). The bytes come from ``wrapper.to_canonical_payload`` (LIVE
    ``Fraction`` → the canonical ``num/den`` encoding). The point-in-time stamp is
    the envelope ``created_at`` on this artifact (NFR-D3 — never in the hashed
    payload). The payload carries ONLY ``int``/``Fraction``/``bool``/``str``
    provenance + repo-relative POSIX critical paths — never an absolute host path /
    source / secret byte (NFR-S1).
    """
    return (
        writer.write_payload(
            "state",
            wrapper.to_canonical_payload(),
            schema_version=wrapper.schema_version,
            producer=NEGATIVE_ASSURANCE_PRODUCER,
        ),
    )


def persist_critical_subsystems(
    writer: ApaaStoreWriter, critical: CriticalSubsystemSet
) -> tuple[str, ...]:
    """Persist the COMPUTED ``CriticalSubsystemSet`` to ``state/`` (Story 4.1, DF-2-3-B).

    Additive (AC4): the computed final ``paths`` + per-path ``origins`` +
    ``designated_but_unmatched`` land content-addressed in ``state/`` via the
    EXISTING ``ApaaStoreWriter.write_payload`` → ``EnvelopeWriter.build`` → the
    single 1.1 ``canonical`` serializer — so a reader can distinguish an override of
    a genuine heuristic hit from a no-op exclude (the DF-2-3-B suggested fix) and the
    scope statement's critical narration is auditable from disk. This ADDS the
    computed set; the operator-INTENT provenance (``request.to_provenance_payload()``)
    the run already persists is UNCHANGED. The payload carries ONLY repo-relative
    POSIX paths + closed-enum origin tokens — never an absolute host path / source /
    secret byte (NFR-S1).
    """
    return (
        writer.write_payload(
            "state",
            critical.model_dump(mode="json"),
            schema_version=critical.schema_version,
            producer=CRITICAL_SUBSYSTEMS_PRODUCER,
        ),
    )


def persist_partitions(writer: ApaaStoreWriter, plan: PartitionPlan) -> tuple[str, ...]:
    """Persist each unit's work-manifest (+ the plan snapshot) through the 1.3 store.

    Story 2.4 (AC4/AC5): each partition's ``work_manifest`` lands at
    ``assignments/<partition_id>.json`` via the EXISTING
    ``ApaaStoreWriter.write_assignment`` (content-derived id — AR11), envelope
    wrapped through ``EnvelopeWriter.build`` → the single 1.1 serializer
    (containment-checked by ``ApaaStorePaths``). The plan SNAPSHOT (sorted partition
    ids + the V1 ``seam_analysis="v2-deferred"`` marker + the recorded-not-analyzed
    cut edges) persists to ``state/`` content-addressed. The persisted payloads carry
    ONLY repo-relative POSIX paths + provenance — never an absolute host path / source
    bytes (NFR-S1 spirit). The NFR-S4 boundary artifacts are the in-scope deliverable.
    """
    locators: list[str] = []
    for partition in plan.partitions:
        manifest_payload = partition.model_dump(mode="json")
        envelope = EnvelopeWriter.build(
            manifest_payload,
            schema_version=partition.schema_version,
            producer=WORK_MANIFEST_PRODUCER,
        )
        locators.append(writer.write_assignment(partition.partition_id, envelope))
    locators.append(
        writer.write_payload(
            "state",
            build_plan_payload(plan),
            schema_version=plan.schema_version,
            producer=PARTITION_PLAN_PRODUCER,
        )
    )
    return tuple(locators)
