"""Pipeline-level bandit wiring — findings-only, Stage 1 (wq-620).

Verification area: ``argus/pipeline_stages.py::_detect_per_file`` <-> BanditScanDetector.
Drivers: `company/argus-finding-shape-ruling-2026-09-22.md` Part 1 Stage 1 — bandit is
wired on the SAME pattern as the live ``SecretScanDetector`` (findings-only; the pipeline
folds ONLY ``.findings``, never ``.entries``). This file proves, end-to-end through the
real ``_detect_per_file`` stage (not the detector in isolation — see
``tests/test_bandit_scan.py`` for that):

* a real MEDIUM-severity issue in a non-test file surfaces as an advisory finding;
* the SAME issue in a test file does NOT surface (the locked non-test-source scope);
* disabling the ``security`` pass disables bandit too (it shares the secret-scan gate);
* **the coverage ledger is byte-identical whether or not bandit fires** — proven by
  running the exact same fixture twice, once with the real bandit call and once with
  ``BanditScanDetector.run`` monkeypatched to return nothing, and diffing the resulting
  ``CoverageLedgerEntry`` lists. This is the specific claim the ruling and the work
  order both call out as needing proof, not assertion.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.detectors.base import DetectorResult  # noqa: E402
from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline_stages import _detect_per_file  # noqa: E402

# pickle.loads over unvalidated input -> bandit B301, MEDIUM severity.
_MEDIUM_SOURCE = "import pickle\n\n\ndef load(data):\n    return pickle.loads(data)\n"


def _build_repo(root: Path, *, medium_in_tests: bool = False) -> tuple[Path, tuple[str, ...]]:
    (root / "app").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "app" / "__init__.py").write_text("", encoding="utf-8")
    (root / "app" / "service.py").write_text(
        "def add(a, b):\n    return a + b\n", encoding="utf-8"
    )
    (root / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (root / "tests" / "test_service.py").write_text(
        "from app.service import add\n\n\ndef test_add():\n    assert add(1, 2) == 3\n",
        encoding="utf-8",
    )
    files = ["app/__init__.py", "app/service.py", "tests/__init__.py", "tests/test_service.py"]
    if medium_in_tests:
        (root / "tests" / "helper_pickle.py").write_text(_MEDIUM_SOURCE, encoding="utf-8")
        files.append("tests/helper_pickle.py")
    else:
        (root / "app" / "leaky.py").write_text(_MEDIUM_SOURCE, encoding="utf-8")
        files.append("app/leaky.py")
    return root, tuple(files)


def _request(repo: Path, **overrides: object) -> AuditRequest:
    fields: dict[str, object] = {
        "repo_path": str(repo),
        "commit": "HEAD",
        "budget": 0,
        "materiality_bar": "",
    }
    fields.update(overrides)
    return AuditRequest(**fields)  # type: ignore[arg-type]


def _run(repo: Path, files: tuple[str, ...], **request_overrides: object):
    index = build_ast_index(repo, files, partition_id="root")
    request = _request(repo, **request_overrides)
    return _detect_per_file(repo, index.entries, request)


def _bandit_findings(findings):
    return [f for f in findings if f.rule_id.startswith("bandit_")]


def test_medium_severity_non_test_issue_surfaces_end_to_end(tmp_path: Path) -> None:
    repo, files = _build_repo(tmp_path)
    entries, findings, _candidates = _run(repo, files)

    bandit_findings = _bandit_findings(findings)
    assert len(bandit_findings) == 1
    finding = bandit_findings[0]
    assert finding.rule_id == "bandit_B301"
    assert finding.advisory is True
    assert finding.depth_supported is None
    assert finding.locators[0].file_path == "app/leaky.py"


def test_same_issue_in_a_test_file_does_not_surface(tmp_path: Path) -> None:
    """The locked scope decision: non-test source only. Same planted issue, this
    time under `tests/`, must produce zero bandit findings.
    """
    repo, files = _build_repo(tmp_path, medium_in_tests=True)
    _entries, findings, _candidates = _run(repo, files)
    assert _bandit_findings(findings) == []


def test_security_pass_disabled_disables_bandit_too(tmp_path: Path) -> None:
    repo, files = _build_repo(tmp_path)
    enabled = tuple(p for p in ("coverage", "vacuous", "orphan", "prosecutor"))
    _entries, findings, _candidates = _run(repo, files, enabled_passes=enabled)
    assert _bandit_findings(findings) == []


def test_coverage_ledger_is_byte_identical_with_and_without_a_bandit_finding(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The ruling's own headline invariant, PROVEN not asserted: run the identical
    fixture twice — once with the real bandit call (which DOES find something, per
    the sibling test above) and once with ``BanditScanDetector.run`` replaced by a
    stub returning an empty ``DetectorResult`` (simulating "bandit found nothing" /
    "bandit was never wired") — and diff the ``entries`` lists byte-for-byte.
    """
    repo_a, files_a = _build_repo(tmp_path / "with_bandit")
    entries_with_bandit, findings_with_bandit, _c1 = _run(repo_a, files_a)
    assert _bandit_findings(findings_with_bandit), "sanity: this run must find something"

    import argus.pipeline_stages as pipeline_stages

    monkeypatch.setattr(
        pipeline_stages.BanditScanDetector,
        "run",
        lambda self, *, repo_root, targets: DetectorResult(),
    )
    repo_b, files_b = _build_repo(tmp_path / "no_bandit")
    entries_without_bandit, findings_without_bandit, _c2 = _run(repo_b, files_b)
    assert _bandit_findings(findings_without_bandit) == []

    # Byte-identical CoverageLedgerEntry lists (same content, same order) — the
    # bandit finding is the ONLY difference between the two runs' findings.
    assert entries_with_bandit == entries_without_bandit
    non_bandit_with = [f for f in findings_with_bandit if not f.rule_id.startswith("bandit_")]
    non_bandit_without = [
        f for f in findings_without_bandit if not f.rule_id.startswith("bandit_")
    ]
    assert non_bandit_with == non_bandit_without
