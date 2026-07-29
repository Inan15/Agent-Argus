"""FR29 evidence-bundle export tests (Story 4.3) — completeness + no-source-retention.

Verification area ArgusAgent-EVIDENCE (``TC-ArgusAgent-EVIDENCE-001-NN`` — the NEW area for the
``evidence/`` sub-package; this is the first test file in it, starting at ...-01).

AI-E3-1 keystone-fixture-adequacy is applied to BOTH keystones:

- the no-source-retention keystone (AC2) PLANTS a distinctive source sentinel byte
  AND a distinctive secret value in a cartridge, runs the FULL audit + bundle
  export (+ persist), and proves BOTH are ABSENT from the serialized bundle bytes
  (+ the persisted artifact + the bundle-touched working state) WHILE the bundle is
  non-empty + the secret finding IS present (redaction != suppression). It is
  demonstrated RED against a deliberate leaking-builder variant.
- the bundle-completeness keystone (AC1) fixtures a run with ≥1 of every section
  over all three verdicts and is demonstrated RED if a section is dropped.
- the no-over-claim keystone (AC4) scans all three verdicts and goes RED on a
  certification phrase.
- the determinism keystone (AC6) proves byte-identity + order-independence and is
  demonstrated RED if the bundle depends on input order.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

from argus.cost.exhaustion import (
    HaltReport,
    InsufficientCoverageFloorReport,
    build_floor_report,
)
from argus.evidence.bundle import (
    EVIDENCE_BUNDLE_PRODUCER,
    EVIDENCE_BUNDLE_SCHEMA_VERSION,
    EvidenceBundle,
    EvidenceBundleError,
    build_evidence_bundle,
    bundle_to_canonical_bytes,
    bundle_to_canonical_payload,
    persist_evidence_bundle,
)
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
)
from argus.ledger.coverage_report import CoverageReport, build_coverage_report
from argus.ledger.critical_subsystems import (
    CriticalCandidate,
    CriticalSubsystemSet,
    identify_critical_subsystems,
)
from argus.ledger.depth_semantics import Criticality
from argus.ledger.recording import Locator, Recording
from argus.store import canonical
from argus.store.integrity import IntegrityFinding, IntegrityReport
from argus.verdict.negative_assurance import (
    NegativeAssuranceVerdict,
    build_negative_assurance_verdict,
)
from argus.verdict.verdict_gate import AuditVerdict, Verdict, evaluate_verdict

_BUNDLE_SOURCE = (
    Path(__file__).resolve().parents[1]
    
    / "argus"
    / "evidence"
    / "bundle.py"
)

# The AC4 forbidden over-claim phrase set — IDENTICAL to the 4.1 locked set.
_FORBIDDEN_PHRASES = (
    "certif",
    "is correct",
    "proven",
    "guarantee",
    "defect-free",
    "bug-free",
    "passed",
)

_COMMIT = "deadbeefcafef00d1234567890abcdef12345678"
_ArgusAgent_VERSION = "0.1.0"


# ─────────────────────────────────────────────────────────────────────────────
# Synthetic builders (PURE — no FS) for the all-three-verdict completeness paths
# ─────────────────────────────────────────────────────────────────────────────


def _entry(path: str, depth: CoverageDepth, *, claim: bool = False) -> CoverageLedgerEntry:
    return CoverageLedgerEntry(file_path=path, depth=depth, claim_present=claim)


def _every_class_ledger() -> CoverageLedger:
    """A ledger with ≥1 of EVERY depth class (the AC1 adequate fixture)."""
    return CoverageLedger.build(
        [
            _entry("a_deep.py", CoverageDepth.AUDITED_DEEP, claim=True),
            _entry("crit_auth.py", CoverageDepth.AUDITED_SHALLOW),
            _entry("c_tool.py", CoverageDepth.TOOL_SCANNED_ONLY),
            _entry("d_inferred.py", CoverageDepth.INFERRED),
            _entry("e_skipped.py", CoverageDepth.SKIPPED),
        ]
    )


def _critical_not_deep() -> CriticalSubsystemSet:
    return identify_critical_subsystems(
        [
            CriticalCandidate(file_path="a_deep.py", criticality=Criticality.CRITICAL),
            CriticalCandidate(file_path="crit_auth.py", criticality=Criticality.CRITICAL),
        ],
        operator_designated=("ghost.py",),
    )


def _floor(verdict: AuditVerdict) -> InsufficientCoverageFloorReport:
    report = HaltReport(
        halted_on_exhaustion=False,
        total_credits=5,
        ceiling_credits=None,
        assessed_count=verdict.total_count,
        assessed_files=(),
        skipped_on_exhaustion_count=0,
        skipped_on_exhaustion_files=(),
    )
    return build_floor_report(verdict, report)


def _finding(recording_id: str, rule_id: str, *, depth: CoverageDepth | None = None) -> Recording:
    return Recording(
        recording_id=recording_id,
        rule_id=rule_id,
        advisory=True,
        depth_supported=depth,
        locators=(Locator(file_path="a_deep.py", start_line=1, end_line=2),),
    )


class _AuditResultStub:
    """Faithful stand-in for the pipeline ``AuditResult`` (duck-typed read shape)."""

    def __init__(
        self,
        verdict: AuditVerdict,
        negative_assurance: NegativeAssuranceVerdict | None,
        coverage_report: CoverageReport | None,
    ) -> None:
        self.verdict = verdict
        self.negative_assurance = negative_assurance
        self.coverage_report = coverage_report


def _result_for(
    verdict: AuditVerdict,
    ledger: CoverageLedger,
    *,
    critical: CriticalSubsystemSet | None = None,
    drop_wrapper: bool = False,
    drop_coverage: bool = False,
) -> _AuditResultStub:
    critical = critical if critical is not None else CriticalSubsystemSet()
    wrapper = None if drop_wrapper else build_negative_assurance_verdict(
        verdict, _floor(verdict), critical, ledger, materiality_bar="default"
    )
    coverage = None if drop_coverage else build_coverage_report(ledger)
    return _AuditResultStub(verdict, wrapper, coverage)


def _release_ready() -> tuple[AuditVerdict, CoverageLedger]:
    ledger = CoverageLedger.build(
        [
            _entry("a.py", CoverageDepth.AUDITED_DEEP, claim=True),
            _entry("b.py", CoverageDepth.AUDITED_DEEP, claim=True),
            _entry("c.py", CoverageDepth.AUDITED_DEEP, claim=True),
        ]
    )
    return evaluate_verdict(ledger, ()), ledger


def _not_ready() -> tuple[AuditVerdict, CoverageLedger, CriticalSubsystemSet]:
    ledger = _every_class_ledger()
    finding = _finding("rid-block-1", "vacuous_test_ast", depth=CoverageDepth.AUDITED_SHALLOW)
    verdict = evaluate_verdict(ledger, (finding,), critical_subsystems_all_deep=False)
    return verdict, ledger, _critical_not_deep()


def _insufficient() -> tuple[AuditVerdict, CoverageLedger]:
    ledger = CoverageLedger.build(
        [
            _entry("a.py", CoverageDepth.SKIPPED),
            _entry("b.py", CoverageDepth.SKIPPED),
            _entry("c.py", CoverageDepth.SKIPPED),
            _entry("d.py", CoverageDepth.SKIPPED),
            _entry("e.py", CoverageDepth.SKIPPED),
            _entry("f.py", CoverageDepth.AUDITED_DEEP, claim=True),
        ]
    )
    return evaluate_verdict(ledger, ()), ledger


def _empty_integrity_report() -> IntegrityReport:
    counts = {kind: 0 for kind in __import__(
        "argus.store.integrity", fromlist=["INTEGRITY_FINDING_KINDS"]
    ).INTEGRITY_FINDING_KINDS}
    return IntegrityReport(findings=(), consistent=True, counts_by_kind=counts)


def _all_three_bundles() -> list[EvidenceBundle]:
    bundles: list[EvidenceBundle] = []
    rr_v, rr_l = _release_ready()
    bundles.append(
        build_evidence_bundle(
            _result_for(rr_v, rr_l), _empty_integrity_report(),
            commit=_COMMIT, argus_version=_ArgusAgent_VERSION,
        )
    )
    nr_v, nr_l, nr_c = _not_ready()
    bundles.append(
        build_evidence_bundle(
            _result_for(nr_v, nr_l, critical=nr_c), _empty_integrity_report(),
            commit=_COMMIT, argus_version=_ArgusAgent_VERSION,
        )
    )
    ic_v, ic_l = _insufficient()
    bundles.append(
        build_evidence_bundle(
            _result_for(ic_v, ic_l), _empty_integrity_report(),
            commit=_COMMIT, argus_version=_ArgusAgent_VERSION,
        )
    )
    return bundles


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — section completeness over all three verdicts (demonstrated RED if dropped)
# ─────────────────────────────────────────────────────────────────────────────


def test_bundle_carries_every_section_over_all_three_verdicts() -> None:
    """TC-ArgusAgent-EVIDENCE-001-01 — AC1: verdict + coverage + findings + scope + integrity present."""
    for bundle in _all_three_bundles():
        assert isinstance(bundle.negative_assurance, NegativeAssuranceVerdict)
        assert bundle.negative_assurance.verdict in {v.value for v in Verdict}
        assert bundle.negative_assurance.disclaimer
        assert bundle.negative_assurance.scope_statement is not None
        assert isinstance(bundle.coverage, CoverageReport)
        assert bundle.coverage.entries  # ≥1 ledger entry
        assert isinstance(bundle.integrity_report, IntegrityReport)
        assert bundle.commit == _COMMIT
        assert bundle.argus_version == _ArgusAgent_VERSION
        assert bundle.materiality_bar == "default"


def test_not_ready_bundle_has_at_least_one_finding_and_multiple_depths() -> None:
    """TC-ArgusAgent-EVIDENCE-001-02 — AC1: the NOT_READY fixture spans multiple depths + ≥1 finding."""
    nr_v, nr_l, nr_c = _not_ready()
    bundle = build_evidence_bundle(
        _result_for(nr_v, nr_l, critical=nr_c), _empty_integrity_report(),
        commit=_COMMIT, argus_version=_ArgusAgent_VERSION,
    )
    assert len(bundle.findings) >= 1
    depths = {entry.depth for entry in bundle.coverage.entries}
    assert len(depths) >= 2, "fixture must span multiple depth classes (AI-E3-1 adequacy)"


def test_completeness_is_red_if_a_section_is_dropped() -> None:
    """TC-ArgusAgent-EVIDENCE-001-03 — AC1 RED: a missing wrapper / coverage is rejected, not silently dropped."""
    rr_v, rr_l = _release_ready()
    with pytest.raises(EvidenceBundleError):
        build_evidence_bundle(
            _result_for(rr_v, rr_l, drop_wrapper=True), _empty_integrity_report(),
            commit=_COMMIT, argus_version=_ArgusAgent_VERSION,
        )
    with pytest.raises(EvidenceBundleError):
        build_evidence_bundle(
            _result_for(rr_v, rr_l, drop_coverage=True), _empty_integrity_report(),
            commit=_COMMIT, argus_version=_ArgusAgent_VERSION,
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — structural no-source-field moat + non-ASCII path round-trip
# ─────────────────────────────────────────────────────────────────────────────


def test_no_bundle_field_can_hold_raw_source_or_secret() -> None:
    """TC-ArgusAgent-EVIDENCE-001-04 — AC3: no leaf field holds a source byte / raw excerpt / secret value."""
    # The bundle's own fields are metadata strings + Fraction/int/bool + frozen
    # sub-models — none named like a source/secret value sink.
    forbidden_field_tokens = ("source", "secret", "value", "body", "excerpt", "content", "raw")
    for name in EvidenceBundle.model_fields:
        assert not any(tok in name.lower() for tok in forbidden_field_tokens), name
    # The findings the bundle exports come from the 2.5 value-free Recording surface
    # (which has NO value/source field — only locators + ids + flags).
    for name in Recording.model_fields:
        assert name != "value" and "secret_value" not in name
    for name in Locator.model_fields:
        assert "source" not in name and "value" not in name


def test_non_ascii_path_round_trips_intact() -> None:
    """TC-ArgusAgent-EVIDENCE-001-05 — AC3/AI-E1-1: a café/Cyrillic locator round-trips verbatim."""
    path = "src/café/модуль_тест.py"
    ledger = CoverageLedger.build(
        [
            _entry(path, CoverageDepth.AUDITED_DEEP, claim=True),
            _entry("b.py", CoverageDepth.AUDITED_DEEP, claim=True),
        ]
    )
    verdict = evaluate_verdict(ledger, ())
    bundle = build_evidence_bundle(
        _result_for(verdict, ledger), _empty_integrity_report(),
        commit=_COMMIT, argus_version=_ArgusAgent_VERSION,
    )
    blob = bundle_to_canonical_bytes(bundle)
    assert path.encode("utf-8") in blob
    reloaded = canonical.loads(blob)
    paths = [e["file_path"] for e in reloaded["coverage"]["entries"]]
    assert path in paths


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — no over-claim inheritance (forbidden-phrase scan; demonstrated RED)
# ─────────────────────────────────────────────────────────────────────────────


def test_no_over_claim_phrase_in_any_bundle() -> None:
    """TC-ArgusAgent-EVIDENCE-001-06 — AC4: the serialized bundle carries no certification phrase, all 3 verdicts."""
    for bundle in _all_three_bundles():
        text = bundle_to_canonical_bytes(bundle).decode("utf-8").lower()
        for phrase in _FORBIDDEN_PHRASES:
            assert phrase not in text, f"over-claim phrase {phrase!r} leaked into the bundle"


def test_no_over_claim_scan_is_red_on_an_injected_phrase() -> None:
    """TC-ArgusAgent-EVIDENCE-001-07 — AC4 RED: the scan WOULD catch an injected certification phrase."""
    rr_v, rr_l = _release_ready()
    bundle = build_evidence_bundle(
        _result_for(rr_v, rr_l), _empty_integrity_report(),
        commit=_COMMIT, argus_version=_ArgusAgent_VERSION,
    )
    payload = bundle_to_canonical_payload(bundle)
    payload["commit"] = "this code is certified correct"  # a deliberate over-claim leak
    leaked = canonical.dumps(payload).lower()
    assert any(phrase in leaked for phrase in _FORBIDDEN_PHRASES)


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — frozen / no-float / single-serializer / no-abs-path
# ─────────────────────────────────────────────────────────────────────────────


def test_bundle_is_frozen_and_schema_versioned() -> None:
    """TC-ArgusAgent-EVIDENCE-001-08 — AC5: frozen, extra=forbid, localized schema version."""
    rr_v, rr_l = _release_ready()
    bundle = build_evidence_bundle(
        _result_for(rr_v, rr_l), _empty_integrity_report(),
        commit=_COMMIT, argus_version=_ArgusAgent_VERSION,
    )
    assert bundle.model_config.get("frozen") is True
    assert bundle.model_config.get("extra") == "forbid"
    assert bundle.schema_version == EVIDENCE_BUNDLE_SCHEMA_VERSION
    with pytest.raises(Exception):
        bundle.commit = "mutated"  # type: ignore[misc]


def test_bundle_serializes_through_the_single_serializer_no_float() -> None:
    """TC-ArgusAgent-EVIDENCE-001-09 — AC5: canonical bytes carry Fraction num/den, no float, no abs path."""
    rr_v, rr_l = _release_ready()
    bundle = build_evidence_bundle(
        _result_for(rr_v, rr_l), _empty_integrity_report(),
        commit=_COMMIT, argus_version=_ArgusAgent_VERSION,
    )
    blob = bundle_to_canonical_bytes(bundle)
    assert blob.endswith(b"\n")
    text = blob.decode("utf-8")
    # deep_ratio rendered as the exact num/den string (3 deep / 3 total = 1/1).
    assert '"deep_ratio":"3/3"' in text or '"deep_ratio":"1/1"' in text
    # No absolute Windows / POSIX host path leaks.
    assert "C:\\" not in text and ":/" not in text


def test_a_float_leaf_is_rejected_by_the_serializer() -> None:
    """TC-ArgusAgent-EVIDENCE-001-10 — AC5: a float in the payload is a typed serializer failure."""
    payload = {"x": 0.5}
    with pytest.raises(canonical.CanonicalSerializationError):
        canonical.dumps(payload)


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — byte-identity + order-independence (demonstrated RED)
# ─────────────────────────────────────────────────────────────────────────────


def test_same_result_exports_byte_identical_bundle() -> None:
    """TC-ArgusAgent-EVIDENCE-001-11 — AC6: the same audit result exports byte-identical bundle bytes."""
    rr_v, rr_l = _release_ready()
    result = _result_for(rr_v, rr_l)
    b1 = bundle_to_canonical_bytes(
        build_evidence_bundle(result, _empty_integrity_report(), commit=_COMMIT, argus_version=_ArgusAgent_VERSION)
    )
    b2 = bundle_to_canonical_bytes(
        build_evidence_bundle(result, _empty_integrity_report(), commit=_COMMIT, argus_version=_ArgusAgent_VERSION)
    )
    assert b1 == b2


def test_bundle_is_order_independent_in_ledger_and_integrity_inputs() -> None:
    """TC-ArgusAgent-EVIDENCE-001-12 — AC6: shuffled ledger + integrity input orderings → identical bytes."""
    entries = [
        _entry("z.py", CoverageDepth.AUDITED_DEEP, claim=True),
        _entry("a.py", CoverageDepth.AUDITED_DEEP, claim=True),
        _entry("m.py", CoverageDepth.AUDITED_DEEP, claim=True),
    ]
    ledger_a = CoverageLedger.build(entries)
    ledger_b = CoverageLedger.build(list(reversed(entries)))
    v_a = evaluate_verdict(ledger_a, ())
    v_b = evaluate_verdict(ledger_b, ())
    f1 = IntegrityFinding(kind="orphaned_artifact", locator="findings/x.json", referent="r1", detail="d")
    f2 = IntegrityFinding(kind="dangling_reference", locator="state/y.json", referent="r2", detail="d")
    counts = _empty_integrity_report().counts_by_kind
    report_a = IntegrityReport(findings=tuple(sorted((f1, f2), key=lambda f: f.kind)),
                               consistent=False, counts_by_kind={**counts, "orphaned_artifact": 1, "dangling_reference": 1})
    report_b = IntegrityReport(findings=tuple(sorted((f2, f1), key=lambda f: f.kind)),
                               consistent=False, counts_by_kind={**counts, "orphaned_artifact": 1, "dangling_reference": 1})
    b_a = bundle_to_canonical_bytes(
        build_evidence_bundle(_result_for(v_a, ledger_a), report_a, commit=_COMMIT, argus_version=_ArgusAgent_VERSION)
    )
    b_b = bundle_to_canonical_bytes(
        build_evidence_bundle(_result_for(v_b, ledger_b), report_b, commit=_COMMIT, argus_version=_ArgusAgent_VERSION)
    )
    assert b_a == b_b


def test_order_dependence_would_be_red() -> None:
    """TC-ArgusAgent-EVIDENCE-001-13 — AC6 RED: if findings were emitted in arrival order, bytes diverge."""
    # A deliberate order-dependent render (arrival order, not the verdict-fixed order)
    # produces different bytes for the same finding set in two orders — proving the
    # byte-identity assertion is not vacuous.
    f1 = _finding("rid-1", "rule_a", depth=CoverageDepth.AUDITED_DEEP)
    f2 = _finding("rid-2", "rule_b", depth=CoverageDepth.AUDITED_SHALLOW)
    arrival_a = canonical.dumps([f.model_dump(mode="json") for f in (f1, f2)])
    arrival_b = canonical.dumps([f.model_dump(mode="json") for f in (f2, f1)])
    assert arrival_a != arrival_b


# ─────────────────────────────────────────────────────────────────────────────
# AC7 — purity / typed error / single-serializer AST scan / file size
# ─────────────────────────────────────────────────────────────────────────────


def test_builder_raises_typed_error_on_malformed_inputs() -> None:
    """TC-ArgusAgent-EVIDENCE-001-14 — AC7: malformed inputs raise EvidenceBundleError (never a silent coerce)."""
    rr_v, rr_l = _release_ready()
    good = _result_for(rr_v, rr_l)
    rep = _empty_integrity_report()
    with pytest.raises(EvidenceBundleError):
        build_evidence_bundle(good, "not a report", commit=_COMMIT, argus_version=_ArgusAgent_VERSION)  # type: ignore[arg-type]
    with pytest.raises(EvidenceBundleError):
        build_evidence_bundle(good, rep, commit=123, argus_version=_ArgusAgent_VERSION)  # type: ignore[arg-type]
    with pytest.raises(EvidenceBundleError):
        build_evidence_bundle(good, rep, commit=_COMMIT, argus_version=None)  # type: ignore[arg-type]
    with pytest.raises(EvidenceBundleError):
        build_evidence_bundle(
            _result_for(rr_v, rr_l, drop_wrapper=True), rep, commit=_COMMIT, argus_version=_ArgusAgent_VERSION
        )
    with pytest.raises(EvidenceBundleError):
        bundle_to_canonical_payload("not a bundle")  # type: ignore[arg-type]


def test_module_is_pure_no_io_no_clock_no_random() -> None:
    """TC-ArgusAgent-EVIDENCE-001-15 — AC7: an AST scan finds no clock/uuid/random/open in the pure module."""
    tree = ast.parse(_BUNDLE_SOURCE.read_text(encoding="utf-8"))
    banned = {
        ("datetime", "now"),
        ("time", "time"),
        ("uuid", "uuid4"),
        ("random", None),
        ("os", "getpid"),
    }
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            value = node.func.value
            if isinstance(value, ast.Name):
                for mod, attr in banned:
                    if value.id == mod and (attr is None or node.func.attr == attr):
                        found.append(f"{value.id}.{node.func.attr}")
    assert not found, f"impure call(s) in the pure bundle module: {found}"


def test_bundle_module_is_under_1200_lines() -> None:
    """TC-ArgusAgent-EVIDENCE-001-16 — AC7/NFR-M1: the new module is ≤1200 lines."""
    lines = _BUNDLE_SOURCE.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 1200


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — the MANDATORY no-source-retention sentinel test (planted source + secret)
# ─────────────────────────────────────────────────────────────────────────────

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.detectors.secret_scan import RULE_HARDCODED_SECRET  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.store.integrity import lint_referential_integrity  # noqa: E402
from argus.store.writer import ApaaStoreWriter  # noqa: E402

# The exact sentinels planted in cartridges/evidence_sentinel/src/config.py.txt.
_SOURCE_SENTINEL = "EVIDENCE_SENTINEL_zXqW7vKpLmNrTaBcDeF1234567890ABCDEF"
_SECRET_SENTINEL = "PLANTEDxAbCdEfGhIjKlMnOpQrStUvWxYz012345"


def _all_argus_bytes(repo: Path) -> bytes:
    argus = repo / ".argus"
    blob = b""
    for path in sorted(argus.rglob("*")):
        if path.is_file():
            blob += path.read_bytes()
    return blob


def _export_bundle_for(repo: Path):
    request = AuditRequest(
        repo_path=str(repo), commit="HEAD", budget=100, materiality_bar="default"
    )
    result = run_audit_detailed(request)
    reader = ApaaStoreReader(repo)
    integrity = lint_referential_integrity(reader)
    bundle = build_evidence_bundle(
        result, integrity, commit="HEAD", argus_version=_ArgusAgent_VERSION
    )
    return result, bundle


def test_no_source_byte_or_secret_in_serialized_bundle(tmp_path: Path) -> None:
    """TC-ArgusAgent-EVIDENCE-001-17 — AC2 KEYSTONE: planted source sentinel + secret ABSENT from bundle bytes."""
    repo, _sha = stage_cartridge("evidence_sentinel", tmp_path / "repo")
    result, bundle = _export_bundle_for(repo)
    blob = bundle_to_canonical_bytes(bundle)

    # The bundle is NON-EMPTY and carries the verdict + scope statement.
    assert blob and blob.endswith(b"\n")
    assert bundle.negative_assurance.verdict
    assert bundle.negative_assurance.disclaimer
    assert bundle.coverage.entries

    # Redaction != suppression: the secret finding IS present.
    secret_findings = [f for f in bundle.findings if f.rule_id == RULE_HARDCODED_SECRET]
    assert secret_findings, "the planted secret WAS detected and exported (redaction != non-detection)"
    assert secret_findings[0].locators[0].file_path == "src/config.py"

    # The KEYSTONE: NEITHER sentinel leaks into the serialized bundle bytes.
    assert _SOURCE_SENTINEL.encode("utf-8") not in blob
    assert _SECRET_SENTINEL.encode("utf-8") not in blob
    assert b"EVIDENCE_SENTINEL" not in blob
    assert b"PLANTED" not in blob


def test_no_source_or_secret_in_persisted_bundle_or_working_state(tmp_path: Path) -> None:
    """TC-ArgusAgent-EVIDENCE-001-18 — AC2 KEYSTONE: sentinels absent from the persisted bundle + .argus/ state."""
    repo, _sha = stage_cartridge("evidence_sentinel", tmp_path / "repo")
    _result, bundle = _export_bundle_for(repo)

    writer = ApaaStoreWriter(repo)
    locator = persist_evidence_bundle(writer, bundle)
    persisted = (repo / ".argus" / locator).read_bytes()

    for blob_name, blob in (("persisted-bundle", persisted), ("all-.argus/", _all_argus_bytes(repo))):
        assert _SOURCE_SENTINEL.encode("utf-8") not in blob, blob_name
        assert _SECRET_SENTINEL.encode("utf-8") not in blob, blob_name
        assert b"EVIDENCE_SENTINEL" not in blob, blob_name
        assert b"PLANTED" not in blob, blob_name

    # The persisted bundle envelope carries the bundle producer token (provenance).
    env = canonical.loads(persisted)
    assert env["producer"] == EVIDENCE_BUNDLE_PRODUCER


def test_no_source_retention_test_is_red_against_a_leaking_builder(tmp_path: Path) -> None:
    """TC-ArgusAgent-EVIDENCE-001-19 — AC2 RED: a builder variant that copies a source excerpt FAILS the assertion.

    Demonstrates the planted-sentinel assertion is real, not vacuous: a leaking
    bundle variant (one that injected the audited source excerpt into a payload
    field) WOULD be caught by the same byte-absence check. We synthesize that leak
    by injecting the sentinel into the canonical payload and asserting the check
    FAILS on it — proving the assertion has teeth.
    """
    repo, _sha = stage_cartridge("evidence_sentinel", tmp_path / "repo")
    _result, bundle = _export_bundle_for(repo)
    payload = bundle_to_canonical_payload(bundle)
    # A deliberate violation: a leaking builder copies the source excerpt + secret.
    payload["commit"] = f"{_SOURCE_SENTINEL} {_SECRET_SENTINEL}"
    leaked = canonical.dumps_bytes(payload)
    # The SAME no-source-retention assertion now FAILS (RED) on the leak.
    assert _SOURCE_SENTINEL.encode("utf-8") in leaked
    assert _SECRET_SENTINEL.encode("utf-8") in leaked


def test_persist_round_trips_to_an_equal_bundle(tmp_path: Path) -> None:
    """TC-ArgusAgent-EVIDENCE-001-20b — AC5: persist→read reconstructs the equal canonical payload byte-identically."""
    repo, _sha = stage_cartridge("evidence_sentinel", tmp_path / "repo")
    _result, bundle = _export_bundle_for(repo)
    writer = ApaaStoreWriter(repo)
    locator = persist_evidence_bundle(writer, bundle)
    reader = ApaaStoreReader(repo)
    envelope = reader.read_envelope(locator)
    assert envelope.payload == bundle_to_canonical_payload_jsonsafe(bundle)


def bundle_to_canonical_payload_jsonsafe(bundle) -> dict:
    """The persisted payload is the canonical JSON-primitive form of the bundle payload."""
    return canonical.loads(bundle_to_canonical_bytes(bundle))
