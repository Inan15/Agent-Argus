"""End-to-end wiring of ``AuditRequest.coverage_scope`` through the pipeline.

Verification area ArgusAgent-PIPELINE (TC-ArgusAgent-PIPELINE-002-NN). The PURE gate
semantics are pinned in ``test_verdict_scope.py``; this module pins the IMPURE half —
that the request field reaches the gate, that classification uses the multi-language
``is_test_file`` (not a hardcoded ``tests/`` prefix), that the default is unchanged,
and that an unrecognized value degrades toward the STRICTER claim (AR10).
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
from argus.pipeline import _assessment_scope_paths, run_audit  # noqa: E402
from argus.ledger.coverage_ledger import (  # noqa: E402
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
)


def _request(repo: Path, **kwargs: object) -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo),
        commit="HEAD",
        budget=100,
        materiality_bar="default",
        **kwargs,  # type: ignore[arg-type]
    )


def _ledger(*paths: str) -> CoverageLedger:
    return CoverageLedger.build(
        tuple(
            CoverageLedgerEntry(
                file_path=p, depth=CoverageDepth.AUDITED_DEEP, claim_present=True
            )
            for p in paths
        )
    )


def test_default_request_scope_is_repository_wide(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-002-01 — the default is unchanged (no scope on the verdict)."""
    repo, _ = stage_cartridge("clean_control", tmp_path / "repo")
    verdict = run_audit(_request(repo))

    assert verdict.coverage_scope is None


def test_application_scope_attaches_the_disclosure(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-002-02 — opting in reaches the gate and is disclosed."""
    repo, _ = stage_cartridge("clean_control", tmp_path / "repo")
    verdict = run_audit(_request(repo, coverage_scope="application"))

    assert verdict.coverage_scope is not None
    assert verdict.coverage_scope.scope_id == "application"
    assert verdict.coverage_scope.excluded_reason == "test_files"
    # The whole-ledger numbers survive the narrowing (never overwritten).
    assert verdict.total_count >= verdict.coverage_scope.assessed_total_count


def test_unrecognized_scope_degrades_to_the_stricter_repository_claim() -> None:
    """TC-ArgusAgent-PIPELINE-002-03 — AR10: a typo must not buy an easier gate.

    An unknown ``coverage_scope`` falls back to the whole-repository assessment
    (``None``) rather than raising or silently narrowing.
    """
    ledger = _ledger("src/a.py", "tests/test_a.py")
    request = AuditRequest(
        repo_path="/x", commit="HEAD", budget=1, materiality_bar="default",
        coverage_scope="aplication",  # typo
    )

    assert _assessment_scope_paths(request, ledger) is None


def test_scope_uses_multilanguage_test_detection_not_a_path_prefix() -> None:
    """TC-ArgusAgent-PIPELINE-002-04 — reuses ``is_test_file`` across languages.

    The rejected implementation matched a literal ``tests/`` prefix, which misses
    every non-Python convention the detector already understands (and every test file
    that does not live under ``tests/``).
    """
    ledger = _ledger(
        "src/app.py",           # application
        "pkg/handler.go",       # application
        "tests/test_a.py",      # test — directory convention
        "src/api_test.go",      # test — Go suffix, NOT under tests/
        "web/login.spec.ts",    # test — TypeScript spec suffix
        "lib/user_spec.rb",     # test — Ruby spec suffix
    )
    request = AuditRequest(
        repo_path="/x", commit="HEAD", budget=1, materiality_bar="default",
        coverage_scope="application",
    )

    scope = _assessment_scope_paths(request, ledger)

    assert scope == frozenset({"src/app.py", "pkg/handler.go"})
