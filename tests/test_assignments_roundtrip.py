"""Per-unit work-manifest persistence round-trip (Story 2.4, AC4).

Verification area ArgusAgent-STORE (TC-ArgusAgent-STORE-001-80..89). Drivers: ArgusAgent-NFR-S4
(the work_manifest IS the permission boundary — persisted as the .argus/assignments/
artifact), ArgusAgent-NFR-S5 (containment-checked write via the 1.3 shell), ArgusAgent-NFR-P1
(byte-identical re-serialize), AR4 (single serializer), AR11 (content-derived
partition_id is the filename). Proves a partition's work_manifest written via the
EXISTING ApaaStoreWriter.write_assignment → read via store/reader.py → equal model
+ byte-identical re-serialize, named assignments/<partition_id>.json, with NO
absolute host path / source byte in the payload.
"""

from __future__ import annotations

from pathlib import Path

from argus.index.ast_index import AstIndex, AstIndexEntry
from argus.index.partitioner import partition_repository
from argus.store import canonical
from argus.store.envelope import EnvelopeWriter
from argus.store.reader import ApaaStoreReader
from argus.store.writer import ApaaStoreWriter

_WORK_MANIFEST_PRODUCER = "argus.pipeline.work_manifest"


def _entry(file_path: str) -> AstIndexEntry:
    return AstIndexEntry(file_path=file_path, ast_eligible=True)


def _plan_with_files(*files: str):
    entries = tuple(_entry(f) for f in files)
    sorted_entries = tuple(sorted(entries, key=lambda e: e.file_path))
    index = AstIndex(grammar_version="test", entries=sorted_entries)
    loc = {f: 100 for f in files}
    return partition_repository(index, loc_by_file=loc)


def test_assignment_written_named_by_partition_id_and_round_trips(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-80 — write_assignment → reader: equal model + byte-identical."""
    plan = _plan_with_files("auth/secrets.py", "core/util.py")
    partition = plan.partitions[0]
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    writer.paths.ensure_tree()

    payload = partition.model_dump(mode="json")
    envelope = EnvelopeWriter.build(
        payload, schema_version=partition.schema_version, producer=_WORK_MANIFEST_PRODUCER
    )
    locator = writer.write_assignment(partition.partition_id, envelope)

    assert locator == f"assignments/{partition.partition_id}.json"

    loaded = reader.read_envelope(locator)
    assert loaded == envelope
    assert loaded.payload == payload

    on_disk = reader.read_bytes(locator)
    assert canonical.dumps_bytes(loaded.model_dump()) == on_disk


def test_assignment_payload_has_no_absolute_path_or_source_bytes(tmp_path: Path) -> None:
    """TC-ArgusAgent-STORE-001-81 — the manifest payload carries only repo-relative paths."""
    plan = _plan_with_files("auth/secrets.py", "core/util.py")
    partition = plan.partitions[0]
    payload = partition.model_dump(mode="json")

    text = canonical.dumps(payload)
    # No absolute host path: no drive-letter / no leading slash path / no tmp_path.
    assert str(tmp_path) not in text
    assert ":\\" not in text
    for f in payload["work_manifest"]["files"]:
        assert not Path(f).is_absolute()
        assert not f.startswith("/")
