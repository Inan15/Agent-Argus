"""Cost-snapshot write/read round-trip + byte-stability (Story 3.1, AC5/AC7).

Verification area ArgusAgent-COST (``TC-ArgusAgent-COST-001-60..69``). Drivers: ArgusAgent-NFR-P1
(byte-identical on-disk state via the single serializer), ArgusAgent-FR-25 (envelope
wrapping), ArgusAgent-FR-31 (the reader deserialize/validate is the Story 3.4 resume
seam — this story PERSISTS the snapshot; 3.4 builds the restore loop), AR4 (single
serializer; no float / Fraction → "num/den"), AR11 (content-addressed filename),
ArgusAgent-NFR-S1 (no absolute path / source byte in the payload).

The cost snapshot is persisted via ``ApaaStoreWriter.write_payload("state", ...)``
over ``CostLedger.to_canonical_payload()`` (LIVE ``Fraction`` → the canonical
``num/den`` encoding, NOT ``model_dump``'s ``str`` coercion). It is read back via
``ApaaStoreReader.read_envelope`` (which re-verifies the content hash — tamper
guard) and re-validated into an EQUAL ``CostLedger`` (the ``_coerce_baseline``
validator turns ``"num/den"`` back into a ``Fraction``).
"""

from __future__ import annotations

from pathlib import Path

from argus.cost.budget_governor import (
    CostLedger,
    account_spend,
    budget_config_from_budget,
)
from argus.store import canonical
from argus.store.reader import ApaaStoreReader
from argus.store.writer import ApaaStoreWriter

_PRODUCER = "argus.pipeline.cost_ledger"


def _ledger() -> CostLedger:
    return account_spend(
        {"files_indexed": 12, "detector_passes": 9, "tool_invocations": 3},
        config=budget_config_from_budget(100),
        build_cost_proxy=200,
    )


def test_cost_snapshot_roundtrip_equal_model(tmp_path: Path) -> None:
    """TC-ArgusAgent-COST-001-60 — write_payload → read_envelope → equal CostLedger model."""
    ledger = _ledger()
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    writer.paths.ensure_tree()

    locator = writer.write_payload(
        "state",
        ledger.to_canonical_payload(),
        schema_version=ledger.schema_version,
        producer=_PRODUCER,
    )
    envelope = reader.read_envelope(locator)  # re-verifies content_hash (tamper guard)
    reloaded = CostLedger.model_validate(envelope.payload)
    assert reloaded == ledger


def test_cost_snapshot_byte_identical_reserialize(tmp_path: Path) -> None:
    """TC-ArgusAgent-COST-001-61 — re-serializing the reloaded model yields the on-disk bytes."""
    ledger = _ledger()
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    writer.paths.ensure_tree()
    locator = writer.write_payload(
        "state",
        ledger.to_canonical_payload(),
        schema_version=ledger.schema_version,
        producer=_PRODUCER,
    )
    envelope = reader.read_envelope(locator)
    reloaded = CostLedger.model_validate(envelope.payload)
    # Re-serializing the reloaded model yields bytes byte-identical to the original
    # payload's canonical bytes (NFR-P1 — the payload round-trips byte-stably).
    assert canonical.dumps_bytes(reloaded.to_canonical_payload()) == canonical.dumps_bytes(
        ledger.to_canonical_payload()
    )
    # The loaded envelope payload (a JSON-primitive dict) equals the canonicalized
    # original payload — the tamper-guard content_hash already re-verified on read.
    assert envelope.payload == canonical.loads(canonical.dumps_bytes(ledger.to_canonical_payload()))


def test_cost_snapshot_filename_content_addressed(tmp_path: Path) -> None:
    """TC-ArgusAgent-COST-001-62 — the snapshot filename is content-addressed (AR11)."""
    ledger = _ledger()
    writer = ApaaStoreWriter(tmp_path)
    writer.paths.ensure_tree()
    locator = writer.write_payload(
        "state",
        ledger.to_canonical_payload(),
        schema_version=ledger.schema_version,
        producer=_PRODUCER,
    )
    assert locator.startswith("state/")
    assert locator.endswith(".json")
    # 64-hex content hash filename.
    name = locator.split("/", 1)[1][: -len(".json")]
    assert len(name) == 64 and all(c in "0123456789abcdef" for c in name)


def test_cost_snapshot_byte_identical_across_hosts(tmp_path: Path) -> None:
    """TC-ArgusAgent-COST-001-63 — two hosts writing the same ledger produce identical bytes (NFR-P1)."""
    ledger = _ledger()
    w1 = ApaaStoreWriter(tmp_path / "host1")
    w2 = ApaaStoreWriter(tmp_path / "host2")
    w1.paths.ensure_tree()
    w2.paths.ensure_tree()
    loc1 = w1.write_payload(
        "state", ledger.to_canonical_payload(), schema_version="1", producer=_PRODUCER
    )
    loc2 = w2.write_payload(
        "state", ledger.to_canonical_payload(), schema_version="1", producer=_PRODUCER
    )
    assert loc1 == loc2
    assert (w1.paths.argus_root / loc1).read_bytes() == (w2.paths.argus_root / loc2).read_bytes()


def test_cost_snapshot_no_abs_path_or_source_byte(tmp_path: Path) -> None:
    """TC-ArgusAgent-COST-001-64 — the on-disk snapshot carries no absolute path / source byte (NFR-S1)."""
    ledger = _ledger()
    writer = ApaaStoreWriter(tmp_path)
    writer.paths.ensure_tree()
    locator = writer.write_payload(
        "state", ledger.to_canonical_payload(), schema_version="1", producer=_PRODUCER
    )
    raw = (writer.paths.argus_root / locator).read_bytes()
    abs_root = str(tmp_path).encode("utf-8")
    assert abs_root not in raw
    for sentinel in (b"/home/", b"/Users/", b".py"):
        assert sentinel not in raw
