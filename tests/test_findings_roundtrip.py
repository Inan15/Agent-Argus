"""Finding persistence round-trip via the Story 1.3 store shell (Story 1.5, AC8).

Verification area ArgusAgent-DETECT (TC-ArgusAgent-DETECT-001-NN). The Story 1.5 detector
emits 1.2 ``Recording`` findings. This story does NOT own a finding-write call
site (the pipeline that persists a finding-set is Story 1.7) — but the
persistence SEAM is the REUSED 1.1/1.3 spine with NO second serializer. This test
proves a detector ``Recording`` round-trips byte-identically through
``EnvelopeWriter.build`` → ``ApaaStoreWriter`` → ``ApaaStoreReader`` (NFR-P1),
mirroring the 1.3/1.4 golden pattern, so Story 1.7 inherits a proven write path.
"""

from __future__ import annotations

from pathlib import Path

from argus.detectors.base import FindingDraft, build_recording
from argus.ledger.coverage_ledger import CoverageDepth
from argus.ledger.recording import RECORDING_SCHEMA_VERSION, Recording
from argus.store import canonical
from argus.store.envelope import EnvelopeWriter
from argus.store.reader import ApaaStoreReader
from argus.store.writer import ApaaStoreWriter


def _finding() -> Recording:
    draft = FindingDraft(
        file_path="tests/test_widget.py",
        start_line=4,
        end_line=9,
        ast_span="function:test_widget@4-9",
        rule_id="vacuous_test_ast",
        advisory=True,
        coverage_envelope_slice="root",
    )
    return build_recording(
        draft, depth_supported=CoverageDepth.AUDITED_SHALLOW, claim_present=False
    )


def test_finding_roundtrips_byte_identically(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-95 — finding → envelope → write → read → equal + byte-stable."""
    finding = _finding()
    payload = finding.model_dump(mode="json")
    envelope = EnvelopeWriter.build(
        payload, schema_version=RECORDING_SCHEMA_VERSION, producer="vacuous_test_detector"
    )

    writer = ApaaStoreWriter(tmp_path)
    writer.paths.ensure_tree()
    locator = writer.write_envelope("findings", envelope)
    assert locator == f"findings/{envelope.content_hash}.json"

    reader = ApaaStoreReader(tmp_path)
    reloaded = reader.read_recording(locator)
    assert reloaded == finding

    # Re-serialize → byte-identical to the on-disk bytes (NFR-P1).
    on_disk = reader.read_bytes(locator)
    rebuilt = EnvelopeWriter.build(
        reloaded.model_dump(mode="json"),
        schema_version=RECORDING_SCHEMA_VERSION,
        producer="vacuous_test_detector",
    )
    assert canonical.dumps_bytes(rebuilt.model_dump()) == on_disk
