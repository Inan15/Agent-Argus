"""Write/read round-trip + byte-stability golden + corrupt-state typed errors.

Verification area ArgusAgent-STORE (TC-ArgusAgent-STORE-001-70..79). Drivers: ArgusAgent-NFR-P1
(byte-identical on-disk state via the single serializer), ArgusAgent-FR-25 (envelope
wrapping), ArgusAgent-FR-31 (reader deserialize/validate/round-trip), AR4 (single
serializer), AR8 (pure reader), AR10 (typed corruption errors), AR11
(content-addressed filenames).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from pydantic import ValidationError

from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    grade_entry,
)
from argus.ledger.recording import Locator, Recording
from argus.store import canonical
from argus.store.envelope import EnvelopeWriter
from argus.store.reader import ApaaStoreReader, StoreIntegrityError
from argus.store.writer import ApaaStoreWriter


def _ledger_payload() -> dict:
    return _populated_ledger().model_dump(mode="json")


def _recording_payload() -> dict:
    return _recording().model_dump(mode="json")


def _populated_ledger() -> CoverageLedger:
    return CoverageLedger.build(
        [
            grade_entry(file_path="b.py", proposed_depth=CoverageDepth.AUDITED_DEEP, claim_present=True),
            grade_entry(file_path="a.py", proposed_depth=CoverageDepth.INFERRED, claim_present=False),
            grade_entry(file_path="c.py", proposed_depth=CoverageDepth.SKIPPED, claim_present=False),
        ]
    )


def _recording() -> Recording:
    return Recording(
        recording_id="rec-001",
        rule_id="vacuous-test",
        advisory=False,
        depth_supported=CoverageDepth.AUDITED_DEEP,
        claim_present=True,
        locators=(Locator(file_path="a.py", start_line=1, end_line=3),),
    )


# ── AC4 — single-serializer bytes, content-addressed filename, byte-stability ──

def test_writer_bytes_are_exactly_canonical_dumps_bytes(tmp_path: Path) -> None:
    """AC4 — on-disk bytes == canonical.dumps_bytes(envelope.model_dump())."""
    writer = ApaaStoreWriter(tmp_path)
    env = EnvelopeWriter.build(_ledger_payload(), schema_version="1", producer="argus.test")
    locator = writer.write_envelope("state", env)

    on_disk = (writer.paths.argus_root / locator).read_bytes()
    assert on_disk == canonical.dumps_bytes(env.model_dump())


def test_filename_is_content_addressed(tmp_path: Path) -> None:
    """AC3/AC11 — the filename derives from the envelope content_hash."""
    writer = ApaaStoreWriter(tmp_path)
    env = EnvelopeWriter.build(_ledger_payload(), schema_version="1", producer="argus.test")
    locator = writer.write_envelope("findings", env)
    assert locator == f"findings/{env.content_hash}.json"


def test_two_writes_same_payload_are_byte_identical(tmp_path: Path) -> None:
    """AC4/NFR-P1 — two writes of the same payload produce byte-identical files."""
    payload = _ledger_payload()
    w1 = ApaaStoreWriter(tmp_path / "host1")
    w2 = ApaaStoreWriter(tmp_path / "host2")
    e1 = EnvelopeWriter.build(payload, schema_version="1", producer="argus.test")
    e2 = EnvelopeWriter.build(payload, schema_version="1", producer="argus.test")
    loc1 = w1.write_envelope("state", e1)
    loc2 = w2.write_envelope("state", e2)

    assert loc1 == loc2  # identical content-addressed name across hosts
    b1 = (w1.paths.argus_root / loc1).read_bytes()
    b2 = (w2.paths.argus_root / loc2).read_bytes()
    assert b1 == b2


def test_golden_content_hash_matches_recomputed(tmp_path: Path) -> None:
    """AC4 — content_hash == sha256 over the canonical payload bytes (golden tie)."""
    payload = _recording_payload()
    env = EnvelopeWriter.build(payload, schema_version="1", producer="argus.test")
    expected = hashlib.sha256(canonical.dumps_bytes(payload)).hexdigest()
    assert env.content_hash == expected


# ── AC5 — reader round-trips byte-identically; equal model ──

def test_envelope_roundtrip_equal_and_byte_stable(tmp_path: Path) -> None:
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    env = EnvelopeWriter.build(_recording_payload(), schema_version="1", producer="argus.test")
    locator = writer.write_envelope("findings", env)

    loaded = reader.read_envelope(locator)
    assert loaded == env
    # re-serializing the loaded model yields bytes identical to what was read.
    on_disk = reader.read_bytes(locator)
    assert canonical.dumps_bytes(loaded.model_dump()) == on_disk


def test_ledger_roundtrip_equal_model(tmp_path: Path) -> None:
    ledger = _populated_ledger()
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    env = EnvelopeWriter.build(ledger.model_dump(mode="json"), schema_version="1", producer="argus.test")
    locator = writer.write_envelope("state", env)

    loaded = reader.read_ledger(locator)
    assert loaded == ledger


def test_recording_roundtrip_equal_model(tmp_path: Path) -> None:
    recording = _recording()
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    env = EnvelopeWriter.build(recording.model_dump(mode="json"), schema_version="1", producer="argus.test")
    locator = writer.write_envelope("findings", env)

    loaded = reader.read_recording(locator)
    assert loaded == recording


def test_write_payload_then_read_envelope(tmp_path: Path) -> None:
    """write_payload wraps + writes; read_envelope round-trips (AC4/AC5)."""
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    payload = _ledger_payload()
    locator = writer.write_payload("state", payload, schema_version="1", producer="argus.test")
    loaded = reader.read_envelope(locator)
    assert loaded.payload == payload


def test_assignment_filename_uses_assignment_id(tmp_path: Path) -> None:
    """AC3 — assignment manifests are named by the stable assignment id."""
    writer = ApaaStoreWriter(tmp_path)
    env = EnvelopeWriter.build({"target": "a.py"}, schema_version="1", producer="argus.test")
    locator = writer.write_assignment("assign-42", env)
    assert locator == "assignments/assign-42.json"


# ── AC6 — corrupt / tampered / missing → typed error, never an uncaught crash ──

def test_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    reader = ApaaStoreReader(tmp_path)
    with pytest.raises(FileNotFoundError):
        reader.read_envelope("state/deadbeef.json")


def test_non_utf8_raises_canonical_error(tmp_path: Path) -> None:
    reader = ApaaStoreReader(tmp_path)
    paths = reader.paths
    target = paths.ensure_parent("state/bad.json")
    target.write_bytes(b"\xff\xfe\x00bad")
    with pytest.raises(canonical.CanonicalSerializationError):
        reader.read_envelope("state/bad.json")


def test_truncated_invalid_json_raises_canonical_error(tmp_path: Path) -> None:
    reader = ApaaStoreReader(tmp_path)
    target = reader.paths.ensure_parent("state/trunc.json")
    target.write_bytes(b'{"schema_version": "1", "produc')
    with pytest.raises(canonical.CanonicalSerializationError):
        reader.read_envelope("state/trunc.json")


def test_extra_field_raises_validation_error(tmp_path: Path) -> None:
    """AC6 — extra='forbid' rejects an unknown field on read-back."""
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    env = EnvelopeWriter.build({"k": "v"}, schema_version="1", producer="argus.test")
    locator = writer.write_envelope("state", env)
    # tamper: append an unknown field to the on-disk object.
    target = writer.paths.argus_root / locator
    obj = canonical.loads(target.read_bytes())
    obj["unexpected_field"] = "x"
    target.write_bytes(canonical.dumps_bytes(obj))
    with pytest.raises(ValidationError):
        reader.read_envelope(locator)


def test_payload_tamper_raises_store_integrity_error(tmp_path: Path) -> None:
    """AC6 — mutating the payload without recomputing content_hash is detected."""
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    env = EnvelopeWriter.build({"depth": "audited_deep"}, schema_version="1", producer="argus.test")
    locator = writer.write_envelope("state", env)
    target = writer.paths.argus_root / locator
    obj = canonical.loads(target.read_bytes())
    obj["payload"]["depth"] = "skipped"  # mutate payload, leave stale content_hash
    target.write_bytes(canonical.dumps_bytes(obj))
    with pytest.raises(StoreIntegrityError):
        reader.read_envelope(locator)


def test_ledger_payload_wrong_shape_raises_validation_error(tmp_path: Path) -> None:
    """AC6 — a valid envelope whose payload is not a ledger fails frozen-schema validation."""
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    env = EnvelopeWriter.build({"not": "a ledger"}, schema_version="1", producer="argus.test")
    locator = writer.write_envelope("state", env)
    with pytest.raises(ValidationError):
        reader.read_ledger(locator)


def test_reader_is_pure_no_write_on_read(tmp_path: Path) -> None:
    """AC5/AC8 — reading mutates nothing on disk."""
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    env = EnvelopeWriter.build(_recording_payload(), schema_version="1", producer="argus.test")
    locator = writer.write_envelope("findings", env)

    before = {p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*")}
    reader.read_envelope(locator)
    reader.read_recording(locator)
    after = {p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*")}
    assert before == after
