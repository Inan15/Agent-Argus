"""Intake+index snapshot round-trip via the Story 1.3 store shell (Story 1.4, AC7).

Verification area ArgusAgent-INDEX (TC-ArgusAgent-INDEX-001-NN). AC7: an intake+index snapshot
persisted to ``.argus/state/`` via ``EnvelopeWriter.build`` + the single
``canonical`` serializer + the ``ApaaStorePaths`` containment shell is
content-addressed (``<content_hash>.json``) and re-reads to an EQUAL model with a
byte-identical re-serialization (NFR-P1). REUSES the 1.3 writer/reader verbatim —
NO second serializer, NO new persistence module (the snapshot WRITE wiring proper
is Story 1.7; this test proves the existing spine round-trips the new models).
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.intake.repo_loader import RepoIntake  # noqa: E402
from argus.intake.stack_detect import detect_stack  # noqa: E402
from argus.store import canonical  # noqa: E402
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.store.writer import ApaaStoreWriter  # noqa: E402


def _build_snapshot(tmp_path: Path) -> dict:
    (tmp_path / "m.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    (tmp_path / "n.go").write_text("package main\n", encoding="utf-8")
    sources = ("m.py", "n.go")
    intake = RepoIntake(commit_sha="a" * 40, source_files=sources)
    profile = detect_stack(tmp_path, sources)
    index = build_ast_index(tmp_path, sources)
    return {
        "intake": intake.model_dump(mode="json"),
        "stack_profile": profile.model_dump(mode="json"),
        "ast_index": index.model_dump(mode="json"),
    }


def test_snapshot_roundtrips_byte_identical(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-76 — envelope-wrapped snapshot write → read → equal + byte-stable."""
    repo = tmp_path / "repo"
    repo.mkdir()
    payload = _build_snapshot(repo)

    writer = ApaaStoreWriter(repo)
    writer.paths.ensure_tree()
    locator = writer.write_payload(
        "state", payload, schema_version="1", producer="argus.intake_index_snapshot"
    )

    # Content-addressed under state/<content_hash>.json (AR11) — no arrival-order name.
    assert locator.startswith("state/")
    assert locator.endswith(".json")

    reader = ApaaStoreReader(repo)
    envelope = reader.read_envelope(locator)
    assert envelope.payload == payload

    # Byte-identical re-serialization of the loaded payload (NFR-P1).
    on_disk = reader.read_bytes(locator)
    reserialized = canonical.dumps_bytes(envelope.model_dump())
    assert on_disk == reserialized
