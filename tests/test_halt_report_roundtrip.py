"""Halt-report write/read round-trip + byte-stability (Story 3.2, AC5/AC7).

Verification area ArgusAgent-COST (``TC-ArgusAgent-COST-001-90..94``). Drivers: ArgusAgent-NFR-P1
(byte-identical on-disk state via the single serializer), ArgusAgent-FR-25 (envelope
wrapping), ArgusAgent-FR-31 (the reader deserialize/validate is the Story 3.4 resume
seam — this story PERSISTS the report; 3.4 builds the restore loop), AR4 (single
serializer; no float), AR11 (content-addressed filename), ArgusAgent-NFR-S1 (no absolute
path / source byte in the payload).

The halt report is persisted via ``ApaaStoreWriter.write_payload("state", ...)``
over ``HaltReport.to_canonical_payload()`` (all leaves int/bool/str/tuple[str] —
no Fraction, so model_dump(mode="json") is canonical-safe). It is read back via
``ApaaStoreReader.read_envelope`` (which re-verifies the content hash — tamper
guard) and re-validated into an EQUAL ``HaltReport``.
"""

from __future__ import annotations

from pathlib import Path

from argus.cost.budget_governor import BudgetConfig
from argus.cost.exhaustion import (
    HaltReport,
    build_halt_report,
    project_halt_point,
)
from argus.cost.exhaustion import CostUnit
from argus.store import canonical
from argus.store.reader import ApaaStoreReader
from argus.store.writer import ApaaStoreWriter

_PRODUCER = "argus.pipeline.halt_report"


def _report() -> HaltReport:
    proj = project_halt_point(
        (
            CostUnit(path="src/a.py", cost=5),
            CostUnit(path="src/b.py", cost=5),
            CostUnit(path="src/c.py", cost=5),
        ),
        config=BudgetConfig(ceiling_credits=8),
    )
    return build_halt_report(proj)


def test_halt_report_roundtrip_equal_model(tmp_path: Path) -> None:
    """TC-ArgusAgent-COST-001-90 — write_payload → read_envelope → equal HaltReport model."""
    report = _report()
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    writer.paths.ensure_tree()
    locator = writer.write_payload(
        "state",
        report.to_canonical_payload(),
        schema_version=report.schema_version,
        producer=_PRODUCER,
    )
    envelope = reader.read_envelope(locator)  # re-verifies content_hash (tamper guard)
    reloaded = HaltReport.model_validate(envelope.payload)
    assert reloaded == report


def test_halt_report_byte_identical_reserialize(tmp_path: Path) -> None:
    """TC-ArgusAgent-COST-001-91 — re-serializing the reloaded model yields the on-disk bytes."""
    report = _report()
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    writer.paths.ensure_tree()
    locator = writer.write_payload(
        "state",
        report.to_canonical_payload(),
        schema_version=report.schema_version,
        producer=_PRODUCER,
    )
    envelope = reader.read_envelope(locator)
    reloaded = HaltReport.model_validate(envelope.payload)
    assert canonical.dumps_bytes(reloaded.to_canonical_payload()) == canonical.dumps_bytes(
        report.to_canonical_payload()
    )


def test_halt_report_filename_content_addressed(tmp_path: Path) -> None:
    """TC-ArgusAgent-COST-001-92 — the halt-report filename is content-addressed (AR11)."""
    report = _report()
    writer = ApaaStoreWriter(tmp_path)
    writer.paths.ensure_tree()
    locator = writer.write_payload(
        "state", report.to_canonical_payload(), schema_version="1", producer=_PRODUCER
    )
    assert locator.startswith("state/")
    assert locator.endswith(".json")
    name = locator.split("/", 1)[1][: -len(".json")]
    assert len(name) == 64 and all(c in "0123456789abcdef" for c in name)


def test_halt_report_byte_identical_across_hosts(tmp_path: Path) -> None:
    """TC-ArgusAgent-COST-001-93 — two hosts writing the same report produce identical bytes (NFR-P1)."""
    report = _report()
    w1 = ApaaStoreWriter(tmp_path / "host1")
    w2 = ApaaStoreWriter(tmp_path / "host2")
    w1.paths.ensure_tree()
    w2.paths.ensure_tree()
    loc1 = w1.write_payload(
        "state", report.to_canonical_payload(), schema_version="1", producer=_PRODUCER
    )
    loc2 = w2.write_payload(
        "state", report.to_canonical_payload(), schema_version="1", producer=_PRODUCER
    )
    assert loc1 == loc2
    assert (w1.paths.argus_root / loc1).read_bytes() == (w2.paths.argus_root / loc2).read_bytes()


def test_halt_report_no_abs_path_or_source_byte(tmp_path: Path) -> None:
    """TC-ArgusAgent-COST-001-94 — the on-disk report carries no absolute path / source byte (NFR-S1)."""
    report = _report()
    writer = ApaaStoreWriter(tmp_path)
    writer.paths.ensure_tree()
    locator = writer.write_payload(
        "state", report.to_canonical_payload(), schema_version="1", producer=_PRODUCER
    )
    raw = (writer.paths.argus_root / locator).read_bytes()
    abs_root = str(tmp_path).encode("utf-8")
    assert abs_root not in raw
    for sentinel in (b"/home/", b"/Users/"):
        assert sentinel not in raw
