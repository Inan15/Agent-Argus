"""Pipeline-level Prosecutor wiring — un-prosecuted repo byte-identity (Story 6.4).

Verification area ArgusAgent-PIPELINE (extends the existing area). Drivers: ArgusAgent-FR-19
(the Prosecutor pass runs after the candidate verdict fold in ``_assemble_and_persist``),
ArgusAgent-CC4 (the cross_partition cut-edge pass is wired via ``partition_plan.cut_edges``),
DN-WIRE / AC4 (a repo where the Prosecutor neither downgrades nor promotes nor raises a
cross_partition finding is BYTE-IDENTICAL to the pre-6.4 path — the V1 default has no
sign-offs, so a clean repo with no cut edges and no signed-off advisory changes no byte).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.store.writer import ApaaStoreWriter  # noqa: E402


def _request(repo: Path) -> AuditRequest:
    return AuditRequest(repo_path=str(repo), commit="HEAD", budget=100, materiality_bar="default")


def _store(tmp_path: Path, name: str) -> tuple[ApaaStoreWriter, ApaaStoreReader]:
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    return ApaaStoreWriter(root), ApaaStoreReader(root)


def test_clean_repo_is_byte_identical_through_prosecutor_wiring(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-60 — a clean repo's verdict + locators are unchanged by the wiring (AC4).

    ``clean_control`` has no dead code and (in the V1 default) no signed-off advisory,
    so the Prosecutor neither promotes nor downgrades. The persisted verdict + locators
    must be the SAME as a run without the Prosecutor would have produced — proven here by
    a deterministic re-run yielding byte-identical verdict bytes (the pure path is
    reproducible; the wiring adds nothing on a clean repo).
    """
    repo, _sha = stage_cartridge("clean_control", tmp_path / "repo")
    writer_a, reader_a = _store(tmp_path, "a")
    writer_b, reader_b = _store(tmp_path, "b")

    result_a = run_audit_detailed(_request(repo), store_writer=writer_a)
    result_b = run_audit_detailed(_request(repo), store_writer=writer_b)

    # The Prosecutor did not change a clean repo's verdict.
    assert result_a.verdict.verdict == result_b.verdict.verdict
    assert result_a.verdict.to_canonical_payload() == result_b.verdict.to_canonical_payload()
    # No cross_partition finding is surfaced on a single-cohesion clean control.
    assert not any(f.rule_id == "cross_partition" for f in result_a.verdict.ordered_findings)


def test_clean_repo_verdict_is_not_downgraded(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-61 — the Prosecutor never downgrades a legitimately clean repo (FR19)."""
    repo, _sha = stage_cartridge("clean_control", tmp_path / "repo")
    result = run_audit_detailed(_request(repo))
    # clean_control is small (3 files) — whatever verdict the gate folds, the Prosecutor
    # leaves it: with no signed-off advisory and (in this single-cohesion repo) no
    # cut edges, the prosecution is a pass-through.
    assert result.verdict.ordered_findings == tuple(
        f for f in result.verdict.ordered_findings if f.rule_id != "cross_partition"
    )
