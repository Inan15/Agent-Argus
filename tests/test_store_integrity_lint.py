"""Story 4.2 — referential-integrity lint of on-disk ``.argus/`` state (FR26/NFR-A2).

Verification area ArgusAgent-STORE (TC-ArgusAgent-STORE-001-82..). Drivers: ArgusAgent-FR-26 (verify
referential integrity — no dangling references), ArgusAgent-NFR-A2 (referential integrity
verifiable), ArgusAgent-NFR-A1 (prev-hash chain), ArgusAgent-FR-25/NFR-D3 (content-addressed
filename <-> content_hash, DF-1-3-A closure), ArgusAgent-NFR-P1 (byte-stable / order-
independent report; no float), ArgusAgent-NFR-S1 (no source/secret/abs-path byte), AR8
(pure resolver / impure read shell), AR10 (typed error for a programmer arg; a
broken reference is a FINDING not a raise).

AI-E3-1 keystone-fixture-adequacy (the marquee Epic-3 lesson, applied FIRST):
every keystone PLANTS a REAL break on a real ``run_audit`` ``.argus/`` tree AND is
demonstrated RED against a deliberate detector-weakening (a local resolver copy
that drops the specific check MISSES the planted break) before the real lint is
trusted. The RED demonstration is captured durably IN the test (the
``_resolve_*_weakened`` helpers), not only narrated in Completion Notes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.store import canonical  # noqa: E402
from argus.store import integrity as integ  # noqa: E402
from argus.store.envelope import (  # noqa: E402
    GENESIS_PREV_HASH,
)
from argus.store.integrity import (  # noqa: E402
    INTEGRITY_FINDING_KINDS,
    IntegrityFinding,
    IntegrityLintError,
    IntegrityReport,
    _ReadArtifact,
    _resolve_references,
    lint_referential_integrity,
)
from argus.store.reader import ApaaStoreReader  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures — a real run_audit tree + on-disk plant/mutate helpers
# ─────────────────────────────────────────────────────────────────────────────


def _request(repo: Path, budget: int = 100) -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo), commit="HEAD", budget=budget, materiality_bar="default"
    )


def _real_tree(tmp_path: Path, name: str = "repo", cartridge: str = "vacuous_basic") -> Path:
    """Stage a cartridge + run a real audit → a fully-populated ``.argus/`` tree."""
    repo, _sha = stage_cartridge(cartridge, tmp_path / name)
    run_audit_detailed(_request(repo))
    return repo


def _state_dir(repo: Path) -> Path:
    return ApaaStoreReader(repo).paths.resolve("state")


def _findings_dir(repo: Path) -> Path:
    return ApaaStoreReader(repo).paths.resolve("findings")


def _assignments_dir(repo: Path) -> Path:
    return ApaaStoreReader(repo).paths.resolve("assignments")


def _kinds(report: IntegrityReport) -> set[str]:
    return {f.kind for f in report.findings}


# ─────────────────────────────────────────────────────────────────────────────
# AC1 / AC2 — the report shape + the intact-store-passes false-positive floor
# ─────────────────────────────────────────────────────────────────────────────


def test_intact_real_tree_passes_no_false_positives(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-82 — AC2: an intact real run_audit tree lints consistent.

    The false-positive floor (AI-E3-1): a genuinely-consistent store produced by a
    complete real audit (verdict + findings + run-state + plan + assignments + cost
    + halt + 4.1 wrapper + critical set) lints to ``consistent=True``, EMPTY findings,
    and every per-kind count == 0 — the lint must NOT cry wolf.
    """
    repo = _real_tree(tmp_path)
    report = lint_referential_integrity(ApaaStoreReader(repo))

    assert report.consistent is True
    assert report.findings == ()
    assert set(report.counts_by_kind) == set(INTEGRITY_FINDING_KINDS)
    assert all(count == 0 for count in report.counts_by_kind.values())


def test_intact_clean_control_tree_passes(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-83 — AC2: the clean_control cartridge tree also lints consistent."""
    repo = _real_tree(tmp_path, cartridge="clean_control")
    report = lint_referential_integrity(ApaaStoreReader(repo))
    assert report.consistent is True
    assert report.findings == ()


def test_report_is_integrity_report_with_counts(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-84 — AC1: lint returns a frozen IntegrityReport over the tree."""
    repo = _real_tree(tmp_path)
    report = lint_referential_integrity(ApaaStoreReader(repo))
    assert isinstance(report, IntegrityReport)
    # counts_by_kind covers every closed-enum kind with an int.
    for kind in INTEGRITY_FINDING_KINDS:
        assert isinstance(report.counts_by_kind[kind], int)


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — dangling reference detected (PLANTED real break + demonstrated RED)
# ─────────────────────────────────────────────────────────────────────────────


def test_dangling_finding_reference_detected(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-85 — AC3: a verdict-referenced finding with no findings/ artifact.

    PLANT a real break: delete the ``findings/`` artifact the verdict's
    ``ordered_findings`` references, so the verdict now points at a recording_id with
    no present finding → a ``dangling_reference``.
    """
    repo = _real_tree(tmp_path)
    # Delete every findings/ artifact (the verdict references >=1 of them).
    deleted = 0
    for f in sorted(_findings_dir(repo).glob("*.json")):
        f.unlink()
        deleted += 1
    assert deleted >= 1, "expected the real tree to carry >=1 finding"

    report = lint_referential_integrity(ApaaStoreReader(repo))
    assert report.consistent is False
    assert "dangling_reference" in _kinds(report)
    dangling = [f for f in report.findings if f.kind == "dangling_reference"]
    assert dangling and all(f.referent for f in dangling)
    assert report.counts_by_kind["dangling_reference"] >= 1


def test_dangling_finding_reference_red_when_existence_check_dropped(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-86 — AC3 RED: a resolver weakened to skip the existence check MISSES it.

    The AI-E3-1 demonstration: a local resolver that drops the verdict->findings
    existence check does NOT flag the planted dangling reference — proving the real
    check is load-bearing and the fixture is non-vacuous.
    """
    repo = _real_tree(tmp_path)
    for f in sorted(_findings_dir(repo).glob("*.json")):
        f.unlink()

    artifacts, read_failures = _read_artifacts(repo)
    weakened = _resolve_references_no_finding_existence(artifacts, read_failures)
    # The weakened resolver MISSES the dangling reference (RED proof).
    assert not any(f.kind == "dangling_reference" for f in weakened)
    # The real resolver catches it.
    real = _resolve_references(artifacts, read_failures)
    assert any(f.kind == "dangling_reference" for f in real)


def test_dangling_assignment_reference_detected(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-87 — AC3: a plan-referenced partition_id with no assignments/ artifact."""
    repo = _real_tree(tmp_path)
    deleted = 0
    for f in sorted(_assignments_dir(repo).glob("*.json")):
        f.unlink()
        deleted += 1
    assert deleted >= 1, "expected the real tree to carry >=1 assignment"

    report = lint_referential_integrity(ApaaStoreReader(repo))
    assert report.consistent is False
    assert "dangling_reference" in _kinds(report)


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — broken prev_hash chain link + orphaned artifact (PLANTED + RED)
# ─────────────────────────────────────────────────────────────────────────────


def test_broken_prev_hash_chain_detected(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-88 — AC4: a non-genesis prev_hash resolving to no present envelope.

    PLANT a real break: re-write a state/ envelope's ``prev_hash`` to a bogus
    non-genesis value (recomputing the content_hash so the 1.3 tamper guard PASSES —
    this is referential, not content, breakage). The renamed-stem check would also
    fire if we changed the content_hash, so we keep the filename matching the NEW
    content_hash to isolate the chain break.
    """
    repo = _real_tree(tmp_path)
    bogus_prev = "f" * 64
    target = sorted(_state_dir(repo).glob("*.json"))[0]
    raw = json.loads(target.read_text(encoding="utf-8"))
    raw["prev_hash"] = bogus_prev
    # content_hash is over the payload only — unchanged; filename stem still matches.
    target.write_bytes(canonical.dumps_bytes(raw))

    report = lint_referential_integrity(ApaaStoreReader(repo))
    assert report.consistent is False
    assert "broken_prev_hash_chain" in _kinds(report)
    broken = [f for f in report.findings if f.kind == "broken_prev_hash_chain"]
    assert broken and broken[0].referent == bogus_prev


def test_broken_prev_hash_chain_red_when_chain_check_dropped(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-89 — AC4 RED: a resolver without the chain check MISSES the break."""
    repo = _real_tree(tmp_path)
    target = sorted(_state_dir(repo).glob("*.json"))[0]
    raw = json.loads(target.read_text(encoding="utf-8"))
    raw["prev_hash"] = "f" * 64
    target.write_bytes(canonical.dumps_bytes(raw))

    artifacts, read_failures = _read_artifacts(repo)
    weakened = _resolve_references_no_chain(artifacts, read_failures)
    assert not any(f.kind == "broken_prev_hash_chain" for f in weakened)
    real = _resolve_references(artifacts, read_failures)
    assert any(f.kind == "broken_prev_hash_chain" for f in real)


def test_orphaned_assignment_detected(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-90 — AC4: an assignments/ artifact referenced by no plan is an orphan.

    PLANT a real break: delete the partition-plan snapshot so the still-present
    assignment is referenced by no plan → an ``orphaned_artifact``.
    """
    repo = _real_tree(tmp_path)
    removed = False
    for f in sorted(_state_dir(repo).glob("*.json")):
        env = ApaaStoreReader(repo).read_envelope(f"state/{f.name}")
        if env.producer == "argus.pipeline.partition_plan":
            f.unlink()
            removed = True
            break
    assert removed, "expected a persisted partition plan"

    report = lint_referential_integrity(ApaaStoreReader(repo))
    assert report.consistent is False
    assert "orphaned_artifact" in _kinds(report)


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — filename <-> content_hash mismatch (DF-1-3-A) + assignment-excluded control
# ─────────────────────────────────────────────────────────────────────────────


def test_filename_content_hash_mismatch_detected(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-91 — AC5: a renamed <sha>.json whose stem != internal content_hash.

    PLANT a real break: RENAME a state/ artifact so its filename stem diverges from
    its internal content_hash (a misfiled artifact — the DF-1-3-A gap).
    """
    repo = _real_tree(tmp_path)
    target = sorted(_state_dir(repo).glob("*.json"))[0]
    renamed = target.with_name("0" * 64 + ".json")
    target.rename(renamed)

    report = lint_referential_integrity(ApaaStoreReader(repo))
    assert report.consistent is False
    assert "filename_content_hash_mismatch" in _kinds(report)
    mismatch = [f for f in report.findings if f.kind == "filename_content_hash_mismatch"]
    assert mismatch and mismatch[0].locator.endswith("0" * 64 + ".json")


def test_filename_mismatch_red_when_sha_stem_check_dropped(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-92 — AC5 RED: a resolver without the sha-stem check MISSES the rename."""
    repo = _real_tree(tmp_path)
    target = sorted(_state_dir(repo).glob("*.json"))[0]
    target.rename(target.with_name("0" * 64 + ".json"))

    artifacts, read_failures = _read_artifacts(repo)
    weakened = _resolve_references_no_sha_stem(artifacts, read_failures)
    assert not any(f.kind == "filename_content_hash_mismatch" for f in weakened)
    real = _resolve_references(artifacts, read_failures)
    assert any(f.kind == "filename_content_hash_mismatch" for f in real)


def test_assignment_not_flagged_by_sha_stem_check(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-93 — AC5: a real assignments/<partition_id>.json does NOT trip the sha-stem check.

    The assignment-excluded control: an assignment is keyed by partition_id (NOT a
    payload sha), so an intact tree's assignment must never produce a
    filename_content_hash_mismatch (it would false-positive otherwise).
    """
    repo = _real_tree(tmp_path)
    report = lint_referential_integrity(ApaaStoreReader(repo))
    # The intact tree has assignments AND lints consistent — proving the exclusion.
    assert list(_assignments_dir(repo).glob("*.json"))
    assert "filename_content_hash_mismatch" not in _kinds(report)
    assert report.consistent is True


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — tamper / corrupt artifact → TYPED FINDING, not a crash (PLANTED + RED)
# ─────────────────────────────────────────────────────────────────────────────


def test_tampered_envelope_is_a_typed_finding_not_a_crash(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-94 — AC6: a content-hash tamper surfaces as a finding, never a raise.

    PLANT a real break: mutate a payload WITHOUT recomputing the content_hash (the
    1.3 tamper case). The lint must RETURN a report with a ``content_hash_tamper``
    finding and NOT raise.
    """
    repo = _real_tree(tmp_path)
    target = None
    for f in sorted(_state_dir(repo).glob("*.json")):
        raw = json.loads(f.read_text(encoding="utf-8"))
        payload = raw.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get("ledger"), dict):
            payload["exit_code"] = 999  # tamper: stale content_hash
            f.write_text(json.dumps(raw), encoding="utf-8")
            target = f
            break
    assert target is not None

    # Never raises — returns a report with the typed finding.
    report = lint_referential_integrity(ApaaStoreReader(repo))
    assert report.consistent is False
    assert "content_hash_tamper" in _kinds(report)


def test_corrupt_bytes_artifact_is_a_typed_finding_not_a_crash(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-95 — AC6: corrupt / non-JSON bytes surface as unreadable_artifact, never a raise."""
    repo = _real_tree(tmp_path)
    target = sorted(_state_dir(repo).glob("*.json"))[0]
    target.write_bytes(b"{ this is not valid json :::")

    report = lint_referential_integrity(ApaaStoreReader(repo))
    assert report.consistent is False
    assert "unreadable_artifact" in _kinds(report)


def test_unknown_field_artifact_is_a_typed_finding(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-96 — AC6: an unknown envelope field (extra=forbid) → unreadable_artifact.

    The content_hash is recomputed so the integrity check PASSES and the pydantic
    validation layer is the one that rejects (covering the ValidationError path
    independently of the tamper path).
    """
    repo = _real_tree(tmp_path)
    target = sorted(_state_dir(repo).glob("*.json"))[0]
    raw = json.loads(target.read_text(encoding="utf-8"))
    raw["bogus_envelope_field"] = "x"  # extra=forbid on the Envelope model
    target.write_bytes(canonical.dumps_bytes(raw))

    report = lint_referential_integrity(ApaaStoreReader(repo))
    assert report.consistent is False
    assert "unreadable_artifact" in _kinds(report)


def test_read_failure_detail_never_leaks_payload_bytes(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-97 — AC6/NFR-S1: a read-failure finding names only the locator + error token."""
    repo = _real_tree(tmp_path)
    target = sorted(_state_dir(repo).glob("*.json"))[0]
    target.write_bytes(b'{"secret_marker": "PLANTED_LEAK_TOKEN"')  # corrupt + a planted token

    report = lint_referential_integrity(ApaaStoreReader(repo))
    serialized = canonical.dumps(report.model_dump(mode="json"))
    assert "PLANTED_LEAK_TOKEN" not in serialized


def test_lint_red_when_read_error_allowed_to_propagate(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-98 — AC6 RED: if a read error were allowed to propagate, the walk would crash.

    Demonstrates the no-crash contract is load-bearing: a shell that does NOT catch
    the read error raises out (RED), while the real lint returns a report (green).
    """
    repo = _real_tree(tmp_path)
    target = sorted(_state_dir(repo).glob("*.json"))[0]
    target.write_bytes(b"not json at all")

    reader = ApaaStoreReader(repo)
    # The weakened (no-catch) walk raises — the planted break is real.
    with pytest.raises(Exception):
        _walk_without_catching(reader)
    # The real lint does NOT raise.
    report = lint_referential_integrity(reader)
    assert report.consistent is False


def test_non_file_json_entry_is_a_typed_finding_not_a_crash(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-108 — AC6/FR26/AR10: a non-file ``*.json`` entry is a finding, never a crash.

    PLANT a real break: a DIRECTORY named ``evil.json`` under ``state/`` — the exact
    shape an interrupted / partial write or a botched manual recovery leaves behind.
    ``_list_locators`` enumerates it via ``glob("*.json")`` (which matches dirs), then
    ``read_envelope`` -> ``Path.read_bytes()`` raises ``IsADirectoryError`` (POSIX) /
    ``PermissionError`` (Windows) — both ``OSError`` subclasses that are NOT
    ``FileNotFoundError``. The lint must CATCH it into an ``unreadable_artifact``
    finding and RETURN a report — never propagate the ``OSError``. This is the
    no-crash keystone (FR26 second AC) against its own OSError bug class.
    """
    repo = _real_tree(tmp_path)
    planted = _state_dir(repo) / "evil.json"
    planted.mkdir()  # a DIRECTORY where a content-addressed envelope is expected

    reader = ApaaStoreReader(repo)
    # The weakened (no-catch) walk raises out — the planted break is real (RED).
    with pytest.raises(OSError):
        _walk_without_catching(reader)
    # The real lint does NOT raise — it returns a report with the typed finding (green).
    report = lint_referential_integrity(reader)
    assert report.consistent is False
    assert "unreadable_artifact" in _kinds(report)
    assert any(
        f.kind == "unreadable_artifact" and f.locator == "state/evil.json"
        for f in report.findings
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC7 — purity, frozen, typed-error, determinism, secret-safety, single serializer
# ─────────────────────────────────────────────────────────────────────────────


def test_non_reader_argument_raises_typed_lint_error() -> None:
    """TC-ArgusAgent-STORE-001-99 — AC7/AR10: a non-ApaaStoreReader arg → typed IntegrityLintError."""
    with pytest.raises(IntegrityLintError):
        lint_referential_integrity("not a reader")  # type: ignore[arg-type]
    with pytest.raises(IntegrityLintError):
        lint_referential_integrity(None)  # type: ignore[arg-type]
    assert issubclass(IntegrityLintError, ValueError)


def test_models_are_frozen_extra_forbid() -> None:
    """TC-ArgusAgent-STORE-001-100 — AC7/M2: IntegrityFinding/IntegrityReport are frozen, extra=forbid."""
    finding = IntegrityFinding(kind="orphaned_artifact", locator="findings/x.json", detail="d")
    with pytest.raises(Exception):
        finding.kind = "other"  # type: ignore[misc]
    with pytest.raises(Exception):
        IntegrityFinding(
            kind="orphaned_artifact", locator="x", detail="d", bogus="y"  # type: ignore[call-arg]
        )
    report = IntegrityReport(consistent=True, counts_by_kind={})
    with pytest.raises(Exception):
        report.consistent = False  # type: ignore[misc]


def test_no_float_anywhere_in_report() -> None:
    """TC-ArgusAgent-STORE-001-101 — AC7/AR4: the report serializes through the single serializer (no float)."""
    report = _build_report_with([
        IntegrityFinding(kind="orphaned_artifact", locator="findings/a.json", detail="d"),
    ])
    # The single 1.1 serializer rejects a float leaf — the report must serialize cleanly.
    payload = report.model_dump(mode="json")
    canonical.dumps(payload)  # raises CanonicalSerializationError on a float leaf
    for count in report.counts_by_kind.values():
        assert isinstance(count, int)


def test_report_is_order_independent_and_byte_stable() -> None:
    """TC-ArgusAgent-STORE-001-102 — AC7/NFR-P1: the sorted report is identical regardless of input order."""
    findings = [
        IntegrityFinding(kind="orphaned_artifact", locator="findings/z.json", referent="z", detail="d"),
        IntegrityFinding(kind="broken_prev_hash_chain", locator="state/a.json", referent="aa", detail="d"),
        IntegrityFinding(kind="dangling_reference", locator="state/v.json", referent="rid", detail="d"),
    ]
    report_a = _build_report_with(list(findings))
    report_b = _build_report_with(list(reversed(findings)))
    assert report_a.findings == report_b.findings
    assert canonical.dumps(report_a.model_dump(mode="json")) == canonical.dumps(
        report_b.model_dump(mode="json")
    )


def test_lint_is_pure_no_clock_uuid_random_in_source() -> None:
    """TC-ArgusAgent-STORE-001-103 — AC7/AR8: the integrity module imports no clock/uuid/random surface."""
    import ast

    source = Path(integ.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    banned = {"time", "datetime", "uuid", "random", "os", "secrets"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned), f"integrity.py imports a banned non-deterministic module: {imported & banned}"


def test_lint_writes_nothing_to_argus(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-104 — AC7: the lint is read-only (no new artifact, no mutation)."""
    repo = _real_tree(tmp_path)
    before = {p.name: p.read_bytes() for p in sorted(_state_dir(repo).glob("*.json"))}
    before_findings = sorted(p.name for p in _findings_dir(repo).glob("*.json"))

    lint_referential_integrity(ApaaStoreReader(repo))

    after = {p.name: p.read_bytes() for p in sorted(_state_dir(repo).glob("*.json"))}
    after_findings = sorted(p.name for p in _findings_dir(repo).glob("*.json"))
    assert before == after
    assert before_findings == after_findings


def test_non_ascii_locator_round_trips_intact() -> None:
    """TC-ArgusAgent-STORE-001-105 — AC7/NFR-S1/AI-E1-1: a non-ASCII café/Cyrillic locator survives intact."""
    finding = IntegrityFinding(
        kind="orphaned_artifact",
        locator="findings/café_тест.json",
        referent="rid_café",
        detail="orphan at findings/café_тест.json",
    )
    report = _build_report_with([finding])
    serialized = canonical.dumps(report.model_dump(mode="json"))
    assert "café_тест.json" in serialized
    reloaded = canonical.loads(serialized.encode("utf-8"))
    assert reloaded["findings"][0]["locator"] == "findings/café_тест.json"


def test_findings_contain_no_absolute_host_path(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-106 — AC7/NFR-S1: no absolute host path leaks into any finding."""
    repo = _real_tree(tmp_path)
    # Plant several break classes at once.
    for f in sorted(_findings_dir(repo).glob("*.json")):
        f.unlink()
    target = sorted(_state_dir(repo).glob("*.json"))[0]
    target.rename(target.with_name("0" * 64 + ".json"))

    report = lint_referential_integrity(ApaaStoreReader(repo))
    serialized = canonical.dumps(report.model_dump(mode="json"))
    assert str(repo) not in serialized
    assert "/home/" not in serialized and "C:\\" not in serialized
    assert ":\\" not in serialized


def test_pure_resolver_works_with_zero_io() -> None:
    """TC-ArgusAgent-STORE-001-107 — AC7/AR8: _resolve_references is pure over an in-memory artifact set."""
    verdict_payload = {"ordered_findings": [{"recording_id": "rid-MISSING"}]}
    verdict = _ReadArtifact(
        locator="state/v.json",
        subdir="state",
        stem="v",
        producer="argus.pipeline.verdict",
        prev_hash=GENESIS_PREV_HASH,
        content_hash="v",
        payload=verdict_payload,
    )
    findings = _resolve_references((verdict,), ())
    assert any(f.kind == "dangling_reference" and f.referent == "rid-MISSING" for f in findings)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers: read artifacts + weakened resolvers (the durable AI-E3-1 RED proofs)
# ─────────────────────────────────────────────────────────────────────────────


def _build_report_with(findings: list[IntegrityFinding]) -> IntegrityReport:
    from argus.store.integrity import _build_report

    return _build_report(findings)


def _read_artifacts(
    repo: Path,
) -> tuple[tuple[_ReadArtifact, ...], tuple[IntegrityFinding, ...]]:
    """Re-read the tree into the resolver's in-memory input (mirrors the impure shell)."""
    from argus.store.integrity import (
        _list_locators,
        _read_failure_finding,
    )
    from argus.store.paths import ArgusAgent_SUBDIRS

    reader = ApaaStoreReader(repo)
    artifacts: list[_ReadArtifact] = []
    failures: list[IntegrityFinding] = []
    for subdir in sorted(ArgusAgent_SUBDIRS):
        for locator in _list_locators(reader, subdir):
            try:
                env = reader.read_envelope(locator)
            except Exception as exc:  # noqa: BLE001 — mirrors the shell's typed catch
                failures.append(_read_failure_finding(locator, subdir, exc))
                continue
            artifacts.append(
                _ReadArtifact(
                    locator=locator,
                    subdir=subdir,
                    stem=Path(locator).stem,
                    producer=env.producer,
                    prev_hash=env.prev_hash,
                    content_hash=env.content_hash,
                    payload=env.payload,
                )
            )
    return tuple(artifacts), tuple(failures)


def _resolve_references_no_finding_existence(
    artifacts: tuple[_ReadArtifact, ...], read_failures: tuple[IntegrityFinding, ...]
) -> tuple[IntegrityFinding, ...]:
    """Weakened resolver: trusts every recording_id resolves (drops the AC3 existence check)."""
    findings = list(read_failures)
    present_hashes = frozenset(a.content_hash for a in artifacts)
    for a in artifacts:
        if a.prev_hash != GENESIS_PREV_HASH and a.prev_hash not in present_hashes:
            findings.append(
                IntegrityFinding(kind="broken_prev_hash_chain", locator=a.locator, detail="d")
            )
        if a.subdir in {"state", "findings"} and a.stem != a.content_hash:
            findings.append(
                IntegrityFinding(kind="filename_content_hash_mismatch", locator=a.locator, detail="d")
            )
    return tuple(findings)


def _resolve_references_no_chain(
    artifacts: tuple[_ReadArtifact, ...], read_failures: tuple[IntegrityFinding, ...]
) -> tuple[IntegrityFinding, ...]:
    """Weakened resolver: drops the prev_hash chain check (the AC4 RED proof)."""
    findings = list(read_failures)
    for a in artifacts:
        if a.subdir in {"state", "findings"} and a.stem != a.content_hash:
            findings.append(
                IntegrityFinding(kind="filename_content_hash_mismatch", locator=a.locator, detail="d")
            )
    return tuple(findings)


def _resolve_references_no_sha_stem(
    artifacts: tuple[_ReadArtifact, ...], read_failures: tuple[IntegrityFinding, ...]
) -> tuple[IntegrityFinding, ...]:
    """Weakened resolver: drops the sha-stem check (the AC5 RED proof)."""
    findings = list(read_failures)
    present_hashes = frozenset(a.content_hash for a in artifacts)
    for a in artifacts:
        if a.prev_hash != GENESIS_PREV_HASH and a.prev_hash not in present_hashes:
            findings.append(
                IntegrityFinding(kind="broken_prev_hash_chain", locator=a.locator, detail="d")
            )
    return tuple(findings)


def _walk_without_catching(reader: ApaaStoreReader) -> None:
    """A walk that does NOT catch read errors — raises out (the AC6 RED proof)."""
    from argus.store.integrity import _list_locators
    from argus.store.paths import ArgusAgent_SUBDIRS

    for subdir in sorted(ArgusAgent_SUBDIRS):
        for locator in _list_locators(reader, subdir):
            reader.read_envelope(locator)  # uncaught — raises on the corrupt artifact
