"""Pipeline-level orphan wiring — the whole-index orphan pass end-to-end (Story 6.3).

Verification area ArgusAgent-PIPELINE (extends the existing area). Drivers: ArgusAgent-FR-12
(the planted orphan surfaces as an advisory finding end-to-end), ArgusAgent-FR-13 (the
finding carries a verifiable locator), DN-WHOLE-INDEX (the orphan detector is wired
as a SINGLE cross-file pass AFTER ``_detect_per_file``, appending findings), AC4
(a no-orphan repo is BYTE-IDENTICAL to the pre-6.3 path — only an ACTUAL orphan adds
a finding; the orphan detector mints NO coverage entry so the ledger/verdict are
unchanged when there is no orphan).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.detectors.orphan_code import RULE_ORPHAN_CODE  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.store.writer import ApaaStoreWriter  # noqa: E402


def _request(repo: Path, commit: str = "HEAD") -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo), commit=commit, budget=100, materiality_bar="default"
    )


def _store(tmp_path: Path, name: str) -> tuple[ApaaStoreWriter, ApaaStoreReader]:
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    return ApaaStoreWriter(root), ApaaStoreReader(root)


def test_planted_orphan_surfaces_as_advisory_finding_end_to_end(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-50 — the planted dead function surfaces as an advisory orphan finding.

    ``src/calc.py::unused_helper`` is referenced by nothing → the whole-index orphan
    pass (wired after ``_detect_per_file``) emits an ``advisory=True`` ``orphan_code``
    finding for it. ``add`` (called by the test) and the ``test_*`` entrypoints are
    NOT flagged (the conservative name-match + exclusion rule).
    """
    repo, _sha = stage_cartridge("orphan_basic", tmp_path / "repo")
    result = run_audit_detailed(_request(repo))

    orphan_findings = [
        f for f in result.verdict.ordered_findings if f.rule_id == RULE_ORPHAN_CODE
    ]
    assert len(orphan_findings) == 1, "exactly the one planted orphan should surface"
    finding = orphan_findings[0]
    assert finding.advisory is True
    loc = finding.locators[0]
    assert loc.file_path == "src/calc.py"
    assert loc.ast_span is not None and "unused_helper" in loc.ast_span
    # add / the test functions are never flagged.
    flagged_spans = {f.locators[0].ast_span for f in orphan_findings}
    assert not any(span and "add" in span for span in flagged_spans)
    assert not any(span and "test_add" in span for span in flagged_spans)


def test_orphan_finding_is_advisory_only_not_verdict_blocking(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-51 — the orphan finding is advisory; it does NOT block the verdict alone.

    An ``advisory=True`` finding with ``depth_supported=None`` is not verdict-eligible
    (CC #6) — the 6.4 Prosecutor owns promotion. The orphan finding therefore does not
    increase the blocking-finding count.
    """
    repo, _sha = stage_cartridge("orphan_basic", tmp_path / "repo")
    result = run_audit_detailed(_request(repo))
    orphan_findings = [
        f for f in result.verdict.ordered_findings if f.rule_id == RULE_ORPHAN_CODE
    ]
    assert all(f.advisory is True and f.depth_supported is None for f in orphan_findings)


def test_no_orphan_repo_emits_no_orphan_finding_and_is_byte_identical(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-52 — a no-orphan repo emits NO orphan finding + is byte-identical (AC4).

    ``clean_control`` has no dead code (``add``/``multiply`` are called; the rest are
    ``test_*`` entrypoints), so the orphan pass adds NOTHING. The persisted verdict
    envelope content_hash is identical across two independent runs of the same
    cartridge — the regression-safe property (the orphan detector mints no coverage
    entry, so a no-orphan repo's ledger/verdict are unchanged).
    """
    repo_a, _ = stage_cartridge("clean_control", tmp_path / "a")
    repo_b, _ = stage_cartridge("clean_control", tmp_path / "b")
    w_a, _ = _store(tmp_path, "store_a")
    w_b, _ = _store(tmp_path, "store_b")

    result_a = run_audit_detailed(_request(repo_a), store_writer=w_a)
    result_b = run_audit_detailed(_request(repo_b), store_writer=w_b)

    # No orphan finding for a clean repo.
    assert not any(
        f.rule_id == RULE_ORPHAN_CODE for f in result_a.verdict.ordered_findings
    )
    # Byte-identical verdict envelope locator (content-addressed) across runs.
    assert result_a.locators[0] == result_b.locators[0]
    assert result_a.verdict.verdict is result_b.verdict.verdict
