"""PURE referential-integrity LINT over the on-disk ``.argus/`` tree.

Drivers: ArgusAgent-FR-26 (verify referential integrity of on-disk state — no dangling
references — the central driver), ArgusAgent-NFR-A2 (referential integrity of on-disk
state is verifiable — no dangling references; ``[Tier B]``), ArgusAgent-NFR-A1 (the
schema-versioned, content-hashed, prev-hash-chained envelope the chain-integrity
check walks), ArgusAgent-FR-25 / ArgusAgent-NFR-D3 (the content-hashed envelope whose
``content_hash`` the filename-stem check verifies — over the canonical payload
ONLY), ArgusAgent-NFR-D2 (deterministic, zero-LLM-token cross-reference fold),
ArgusAgent-NFR-P1 (byte-identical / order-independent report; sorted findings; no
float), ArgusAgent-NFR-S1 (no source / secret / absolute-host-path byte in any
finding — only repo-relative locators / ids / kinds), ArgusAgent-NFR-S5 (every read is
containment-checked via the 1.3 ``ApaaStorePaths`` shell), ArgusAgent-NFR-R1 (a tool /
parse failure or a broken reference degrades to a recorded finding — never an
uncaught crash), AR4 (no ``float``; ``int``/``str``/``bool`` only; single
canonical serializer; content-derived ids), AR8 (pure/impure separation — the
models + ``_resolve_references`` resolver are PURE; the enumerate-and-read of
``.argus/`` bytes is the impure 1.3 reader shell), AR10 (typed failure for a
PROGRAMMER error — a non-``ApaaStoreReader`` argument; a broken reference is a
FINDING, never a raise), AR11 (``.argus/`` enumeration is sorted / deterministic;
content-addressed filenames).

Verification area ArgusAgent-STORE (``TC-ArgusAgent-STORE-001-82..``; the next free index
after ``test_assignments_roundtrip.py``'s ...-80/-81 and
``test_no_web_imports.py``'s ...-50).

What this lint is (and is NOT) — the framing crux (FR26 vs FR25/NFR-D3)
-----------------------------------------------------------------------
This lint is COMPLEMENTARY to the Story 1.3 ``StoreIntegrityError`` content-hash
tamper guard, NOT a duplicate. 1.3's ``read_envelope`` catches a PER-ARTIFACT
CONTENT tamper (a payload mutated WITHOUT re-hashing). THIS lint catches
REFERENTIAL / STRUCTURAL breakage ACROSS artifacts — a dangling reference, a
broken ``prev_hash`` chain link, a content-addressed filename that no longer
matches its internal ``content_hash`` (a renamed / misfiled artifact), and an
orphaned artifact. The two are layers of the same trust substrate: content
integrity (1.3) + referential integrity (4.2). The lint REUSES the 1.3 guard (a
content tamper encountered during the walk becomes one ``content_hash_tamper``
integrity finding) — it does NOT mint a second tamper-error type or fork a second
tamper check.

The keystone contract — a broken reference is a FINDING, never a raise (AR10)
----------------------------------------------------------------------------
The whole point of a lint is to REPORT breakage, not crash on it. The
enumerate-and-read shell CATCHES the typed read errors (``StoreIntegrityError``,
``CanonicalSerializationError``, ``pydantic.ValidationError``, and any
``OSError`` — which subsumes ``FileNotFoundError`` raced-delete,
``IsADirectoryError`` a directory named ``<sha>.json``, and ``PermissionError``)
per-artifact and converts each to an ``IntegrityFinding``;
the cross-reference resolver records each unresolved reference as a finding. The
lint RETURNS an ``IntegrityReport`` (``consistent=False`` with the findings) — it
NEVER raises out. The ONLY raise is a typed ``IntegrityLintError`` (a
``ValueError`` subclass mirroring ``StoreIntegrityError`` / ``ExhaustionError``)
for a PROGRAMMER error (a non-``ApaaStoreReader`` argument).

The reference graph the lint resolves (locked against the REAL persisted tree)
------------------------------------------------------------------------------
Confirmed empirically against a real ``run_audit`` output:

(a) **prev_hash chain integrity (NFR-A1).** Every envelope's ``prev_hash`` is
    EITHER :data:`GENESIS_PREV_HASH` (the chain head) OR equals the
    ``content_hash`` of some PRESENT envelope. A non-genesis ``prev_hash`` that
    points to no present envelope is a ``broken_prev_hash_chain`` finding. V1
    chain-shape note: ArgusAgent writes are content-addressed and ``write_payload``
    defaults ``prev_hash=GENESIS_PREV_HASH`` unless explicitly chained — so the
    V1 tree is NOT a single total linear chain (every artifact is genesis-headed
    today). The lint asserts RESOLVES-to-a-present-content_hash, NOT a single
    linear order — asserting a stricter chain than the spine produces would
    false-positive the intact-store-passes floor (AC2).

(b) **content-addressed filename <-> content_hash (DF-1-3-A closure).** For every
    content-addressed ``<sha>.json`` artifact (``state/`` + ``findings/``), the
    filename stem MUST equal the envelope's internal ``content_hash`` (verified
    via 1.3's ``read_envelope`` / ``compute_content_hash`` over the payload only).
    A mismatch is a ``filename_content_hash_mismatch`` finding (a renamed /
    misfiled artifact). ``assignments/<partition_id>.json`` manifests are keyed by
    a stable content-derived ``partition_id`` (NOT a sha over the envelope
    payload), so they are EXCLUDED from the sha-stem check — an assignment id is
    verified by the plan->assignment resolution in (d), not by sha-stem equality.

(c) **run-state / verdict -> findings references (FR26 "finding->ledger entry").**
    The verdict envelope (producer ``argus.pipeline.verdict``) carries
    ``ordered_findings`` — each a ``Recording`` with a ``recording_id``. Every
    ``recording_id`` the verdict references MUST resolve to a present ``findings/``
    ``Recording``; an unresolved one is a ``dangling_reference`` /
    ``missing_referent``. A ``findings/`` ``Recording`` referenced by NO present
    verdict is an ``orphaned_artifact`` (dangling state).

(d) **partition-plan -> assignment references (FR26 "decision->assignment"
    generalized — the V1 analog).** The partition-plan snapshot (producer
    ``argus.pipeline.partition_plan``) references ``partition_id``s; each MUST
    resolve to a present ``assignments/<partition_id>.json``. A referenced id with
    no assignment is a ``dangling_reference``; an ``assignments/`` artifact
    referenced by no plan is an ``orphaned_artifact``. ``decisions/`` artifacts do
    NOT exist in V1 (FR24 / ``governance/decision_record.py`` is Epic 6) — so the
    literal FR26 "decision->assignment" landing is FENCED to Epic 6 when
    ``decisions/`` artifacts ship; the V1 lint checks the partition->assignment
    analog only and invents NO decision reference that has no V1 producer.

(e) **unreadable / tamper artifacts.** An artifact whose ``read_envelope`` raises
    (a 1.3 ``StoreIntegrityError`` content-hash tamper, a
    ``CanonicalSerializationError`` corrupt / non-UTF-8 / non-JSON, a
    ``pydantic.ValidationError`` unknown-field / bad-shape) becomes a typed
    integrity finding (``content_hash_tamper`` / ``unreadable_artifact``), never an
    uncaught raise.

Pure/impure separation (master rule, AR8)
-----------------------------------------
The ``IntegrityFinding`` / ``IntegrityReport`` models + :func:`_resolve_references`
(the cross-reference resolver, over a pre-read in-memory ``_ReadArtifact`` set) are
PURE — no file open, no clock read, no LLM. The IMPURE shell is
:func:`lint_referential_integrity`: it enumerates + reads the ``.argus/`` bytes
through the 1.3 ``ApaaStoreReader`` (the resumability read primitive — AR8 permits
the byte read) and catches the per-artifact read errors into findings. The lint
WRITES NOTHING (CC-4 read-only spirit).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from argus.store import canonical
from argus.store.envelope import GENESIS_PREV_HASH, Envelope
from argus.store.paths import ArgusAgent_SUBDIRS, WorkspaceContainmentError
from argus.store.reader import ApaaStoreReader, StoreIntegrityError

__all__ = [
    "INTEGRITY_SCHEMA_VERSION",
    "INTEGRITY_FINDING_KINDS",
    "IntegrityLintError",
    "IntegrityFinding",
    "IntegrityReport",
    "lint_referential_integrity",
]

# Localized schema version for the integrity-finding contract (additive-only,
# NFR-M2; localized — the 1.1/1.2/1.6/4.1 precedent).
INTEGRITY_SCHEMA_VERSION = "1"

# The closed set of integrity-finding kinds (FR26 reference-graph breakage classes).
INTEGRITY_FINDING_KINDS: tuple[str, ...] = (
    "dangling_reference",
    "missing_referent",
    "broken_prev_hash_chain",
    "filename_content_hash_mismatch",
    "orphaned_artifact",
    "content_hash_tamper",
    "unreadable_artifact",
)

# Producer tokens the resolver classifies against. Mirrored as small local
# constants from the authoritative pipeline set (``pipeline.py:172-199``) to
# avoid a circular import (``store/integrity.py`` <- ``pipeline.py``); the lint
# classifies by reading the envelope ``producer`` field directly (DN: mirror, not
# fork — no second producer registry).
_VERDICT_PRODUCER = "argus.pipeline.verdict"
_FINDING_PRODUCER = "argus.pipeline.finding"
_PARTITION_PLAN_PRODUCER = "argus.pipeline.partition_plan"
_WORK_MANIFEST_PRODUCER = "argus.pipeline.work_manifest"

# The sub-directories whose content-addressed ``<sha>.json`` filename stem MUST
# equal the internal ``content_hash`` (the DF-1-3-A check). ``assignments/`` is
# keyed by ``partition_id`` (not a payload sha) and is EXCLUDED — its id is
# verified by the plan->assignment resolution instead.
_SHA_STEM_SUBDIRS: frozenset[str] = frozenset({"state", "findings"})


class IntegrityLintError(ValueError):
    """Raised ONLY for a PROGRAMMER error (a non-``ApaaStoreReader`` argument).

    A ``ValueError`` subclass localized to this module (mirroring
    ``StoreIntegrityError`` / ``ExhaustionError`` / ``PartitionerError``). A broken
    reference / tamper / corrupt artifact is NEVER this error — it is an
    :class:`IntegrityFinding` in the returned :class:`IntegrityReport` (the FR26 /
    AR10 keystone). The message names only the offending argument type — no file
    content / payload / secret byte (NFR-S1 spirit).
    """


class IntegrityFinding(BaseModel):
    """A frozen, typed referential-integrity finding (NOT a raw string; FR26).

    Carries ONLY repo-relative POSIX locators, ids, and closed-enum kind / error
    tokens — never a source / secret / absolute-host-path byte (NFR-S1). NO
    ``float`` anywhere.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=INTEGRITY_SCHEMA_VERSION,
        description="Integrity-finding schema version (localized, additive-only).",
    )
    kind: str = Field(..., description="Closed-enum breakage class (INTEGRITY_FINDING_KINDS).")
    locator: str = Field(
        ..., description="The offending artifact's repo-relative POSIX locator (never absolute)."
    )
    referent: str | None = Field(
        default=None,
        description="The unresolved target locator / id (repo-relative / id-only), or None.",
    )
    producer: str | None = Field(
        default=None, description="The producer token of the offending artifact (provenance)."
    )
    detail: str = Field(
        ...,
        description="Deterministic message naming ONLY locators / ids / kinds (no payload bytes).",
    )


class IntegrityReport(BaseModel):
    """The frozen referential-integrity report over one ``.argus/`` tree (FR26 / NFR-A2).

    ``findings`` is the SORTED tuple (by ``(kind, locator, referent)``) so the
    report is byte-stable / order-independent across enumeration order (NFR-P1).
    ``consistent`` is exactly the empty-findings predicate. ``counts_by_kind`` maps
    every closed-enum kind to an ``int`` (no ``float``).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(default=INTEGRITY_SCHEMA_VERSION)
    findings: tuple[IntegrityFinding, ...] = Field(
        default=(), description="Sorted by (kind, locator, referent) — byte-stable (NFR-P1)."
    )
    consistent: bool = Field(..., description="True iff the findings tuple is empty.")
    counts_by_kind: dict[str, int] = Field(
        ..., description="Per-kind finding counts; every closed-enum kind present (int)."
    )


@dataclass(frozen=True)
class _ReadArtifact:
    """A single successfully-read ``.argus/`` envelope (the PURE resolver's input row).

    ``locator`` is the repo-relative POSIX locator; ``stem`` is its filename stem
    (the content-address for ``state/`` / ``findings/``). PURE — no I/O lives here.
    """

    locator: str
    subdir: str
    stem: str
    producer: str
    prev_hash: str
    content_hash: str
    payload: dict[str, Any]


def _finding_sort_key(finding: IntegrityFinding) -> tuple[str, str, str]:
    """Total deterministic sort key — ``(kind, locator, referent)`` (NFR-P1, AR4)."""
    return (finding.kind, finding.locator, finding.referent or "")


def _build_report(findings: list[IntegrityFinding]) -> IntegrityReport:
    """Assemble the frozen, SORTED report + the per-kind counts (PURE)."""
    ordered = tuple(sorted(findings, key=_finding_sort_key))
    counts: dict[str, int] = {kind: 0 for kind in INTEGRITY_FINDING_KINDS}
    for finding in ordered:
        counts[finding.kind] = counts.get(finding.kind, 0) + 1
    return IntegrityReport(
        findings=ordered,
        consistent=len(ordered) == 0,
        counts_by_kind=counts,
    )


def _check_chain_and_filename_integrity(
    artifacts: tuple[_ReadArtifact, ...], present_hashes: frozenset[str]
) -> list[IntegrityFinding]:
    findings: list[IntegrityFinding] = []
    for artifact in artifacts:
        # (a) prev_hash chain integrity.
        if artifact.prev_hash != GENESIS_PREV_HASH and artifact.prev_hash not in present_hashes:
            findings.append(
                IntegrityFinding(
                    kind="broken_prev_hash_chain",
                    locator=artifact.locator,
                    referent=artifact.prev_hash,
                    producer=artifact.producer,
                    detail=(
                        f"non-genesis prev_hash '{artifact.prev_hash}' resolves to no "
                        f"present envelope (broken chain link)"
                    ),
                )
            )
        # (b) content-addressed filename <-> content_hash (DF-1-3-A closure).
        if artifact.subdir in _SHA_STEM_SUBDIRS and artifact.stem != artifact.content_hash:
            findings.append(
                IntegrityFinding(
                    kind="filename_content_hash_mismatch",
                    locator=artifact.locator,
                    referent=artifact.content_hash,
                    producer=artifact.producer,
                    detail=(
                        f"filename stem '{artifact.stem}' != internal content_hash "
                        f"'{artifact.content_hash}' (renamed / misfiled artifact)"
                    ),
                )
            )
    return findings


def _check_verdict_finding_references(
    artifacts: tuple[_ReadArtifact, ...]
) -> list[IntegrityFinding]:
    findings: list[IntegrityFinding] = []
    finding_ids: dict[str, str] = {}
    for artifact in artifacts:
        if artifact.producer != _FINDING_PRODUCER:
            continue
        recording_id = artifact.payload.get("recording_id")
        if isinstance(recording_id, str):
            finding_ids[recording_id] = artifact.locator

    referenced_recording_ids: set[str] = set()
    for artifact in artifacts:
        if artifact.producer != _VERDICT_PRODUCER:
            continue
        ordered_findings = artifact.payload.get("ordered_findings")
        if not isinstance(ordered_findings, list):
            continue
        for row in ordered_findings:
            if not isinstance(row, dict):
                continue
            recording_id = row.get("recording_id")
            if not isinstance(recording_id, str):
                continue
            referenced_recording_ids.add(recording_id)
            if recording_id not in finding_ids:
                findings.append(
                    IntegrityFinding(
                        kind="dangling_reference",
                        locator=artifact.locator,
                        referent=recording_id,
                        producer=artifact.producer,
                        detail=(
                            f"verdict references recording_id '{recording_id}' "
                            f"with no present findings/ artifact"
                        ),
                    )
                )
    for recording_id in sorted(finding_ids):
        if recording_id not in referenced_recording_ids:
            findings.append(
                IntegrityFinding(
                    kind="orphaned_artifact",
                    locator=finding_ids[recording_id],
                    referent=recording_id,
                    producer=_FINDING_PRODUCER,
                    detail=(
                        f"findings/ recording_id '{recording_id}' is referenced by "
                        f"no present verdict (orphaned)"
                    ),
                )
            )
    return findings


def _check_partition_assignment_references(
    artifacts: tuple[_ReadArtifact, ...]
) -> list[IntegrityFinding]:
    findings: list[IntegrityFinding] = []
    assignment_ids: dict[str, str] = {}
    for artifact in artifacts:
        if artifact.producer != _WORK_MANIFEST_PRODUCER:
            continue
        partition_id = artifact.payload.get("partition_id")
        if isinstance(partition_id, str):
            assignment_ids[partition_id] = artifact.locator

    referenced_partition_ids: set[str] = set()
    for artifact in artifacts:
        if artifact.producer != _PARTITION_PLAN_PRODUCER:
            continue
        partitions = artifact.payload.get("partitions")
        if not isinstance(partitions, list):
            continue
        for partition in partitions:
            if not isinstance(partition, dict):
                continue
            partition_id = partition.get("partition_id")
            if not isinstance(partition_id, str):
                continue
            referenced_partition_ids.add(partition_id)
            if partition_id not in assignment_ids:
                findings.append(
                    IntegrityFinding(
                        kind="dangling_reference",
                        locator=artifact.locator,
                        referent=partition_id,
                        producer=artifact.producer,
                        detail=(
                            f"partition plan references partition_id '{partition_id}' "
                            f"with no present assignments/ artifact"
                        ),
                    )
                )
    for partition_id in sorted(assignment_ids):
        if partition_id not in referenced_partition_ids:
            findings.append(
                IntegrityFinding(
                    kind="orphaned_artifact",
                    locator=assignment_ids[partition_id],
                    referent=partition_id,
                    producer=_WORK_MANIFEST_PRODUCER,
                    detail=(
                        f"assignments/ partition_id '{partition_id}' is referenced by "
                        f"no present partition plan (orphaned)"
                    ),
                )
            )
    return findings


def _resolve_references(
    artifacts: tuple[_ReadArtifact, ...],
    read_failures: tuple[IntegrityFinding, ...] = (),
) -> tuple[IntegrityFinding, ...]:
    """PURE cross-reference resolver over a pre-read in-memory artifact set (AR8).

    Folds the reference graph (a)-(d) into integrity findings; ``read_failures``
    (the (e) per-artifact unreadable / tamper findings the impure shell already
    converted) are carried through unchanged. Never opens a file, reads a clock,
    or calls an LLM. Deterministic — the inputs are sorted by the caller and every
    derived set is iterated in sorted order.
    """
    findings: list[IntegrityFinding] = list(read_failures)
    present_hashes = frozenset(a.content_hash for a in artifacts)

    findings.extend(_check_chain_and_filename_integrity(artifacts, present_hashes))
    findings.extend(_check_verdict_finding_references(artifacts))
    findings.extend(_check_partition_assignment_references(artifacts))

    return tuple(findings)


def _list_locators(reader: ApaaStoreReader, subdir: str) -> tuple[str, ...]:
    """Sorted ``<subdir>/<name>.json`` locators present in the ``.argus/`` tree (AR11).

    Mirrors the ``pipeline._list_locators`` discipline (sorted enumeration through
    the containment-checked resolver) — a missing sub-dir yields an empty tuple.
    """
    try:
        directory: Path = reader.paths.resolve(subdir)
    except WorkspaceContainmentError:
        raise
    if not directory.is_dir():
        return ()
    return tuple(sorted(f"{subdir}/{child.name}" for child in directory.glob("*.json")))


def _read_failure_finding(locator: str, subdir: str, exc: Exception) -> IntegrityFinding:
    """Convert a per-artifact read error into a typed finding (AC6; never the bytes)."""
    if isinstance(exc, StoreIntegrityError):
        kind = "content_hash_tamper"
        token = "StoreIntegrityError"
    else:
        kind = "unreadable_artifact"
        token = type(exc).__name__
    return IntegrityFinding(
        kind=kind,
        locator=locator,
        referent=None,
        producer=None,
        detail=f"artifact at '{locator}' failed to read ({token})",
    )


def lint_referential_integrity(reader: ApaaStoreReader) -> IntegrityReport:
    """Walk the ``.argus/`` tree and resolve every cross-reference (FR26 / NFR-A2).

    The IMPURE shell: enumerates the ``.argus/`` sub-dirs (sorted — AR11), reads
    each envelope via the tamper-guarded 1.3 ``read_envelope``, CATCHING the typed
    read errors (``StoreIntegrityError`` content-hash tamper /
    ``CanonicalSerializationError`` corrupt / ``pydantic.ValidationError``
    bad-shape / any ``OSError`` — ``FileNotFoundError`` raced-delete,
    ``IsADirectoryError`` a directory named ``<sha>.json``, ``PermissionError``)
    per-artifact into a typed finding (AC6 — never propagated). The
    successfully-read artifacts are folded by
    the PURE :func:`_resolve_references` resolver. Returns a frozen, SORTED
    :class:`IntegrityReport`. The lint WRITES NOTHING.

    A broken reference / tamper / corrupt artifact is a FINDING in the returned
    report, NEVER a raise. The ONLY raise is :class:`IntegrityLintError` for a
    PROGRAMMER error (a non-``ApaaStoreReader`` argument).
    """
    if not isinstance(reader, ApaaStoreReader):
        raise IntegrityLintError(
            f"reader must be an ApaaStoreReader, got {type(reader).__name__!r}"
        )

    artifacts: list[_ReadArtifact] = []
    read_failures: list[IntegrityFinding] = []

    for subdir in sorted(ArgusAgent_SUBDIRS):
        for locator in _list_locators(reader, subdir):
            try:
                envelope: Envelope = reader.read_envelope(locator)
            except (
                StoreIntegrityError,
                canonical.CanonicalSerializationError,
                ValidationError,
                OSError,
            ) as exc:
                read_failures.append(_read_failure_finding(locator, subdir, exc))
                continue
            artifacts.append(
                _ReadArtifact(
                    locator=locator,
                    subdir=subdir,
                    stem=Path(locator).stem,
                    producer=envelope.producer,
                    prev_hash=envelope.prev_hash,
                    content_hash=envelope.content_hash,
                    payload=envelope.payload,
                )
            )

    findings = _resolve_references(tuple(artifacts), tuple(read_failures))
    return _build_report(list(findings))
