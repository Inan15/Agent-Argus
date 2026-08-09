"""Tests for ArgusAgent end-user report generation engine (argus.reports)."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger, grade_entry
from argus.models import AuditRequest
from argus.reports.formatter import format_locator_link, mask_secret, render_markdown_table
from argus.reports.generator import (
    generate_reports,
    render_architecture_review_report,
    render_final_verdict_report,
    render_security_review_report,
)
from argus.verdict.verdict_gate import AuditVerdict, Verdict, evaluate_verdict


def test_mask_secret() -> None:
    assert mask_secret("") == ""
    assert mask_secret("short") == "*****"
    assert mask_secret("AKIAIOSFODNN7EXAMPLE") == "AKIA****************"


def test_format_locator_link() -> None:
    assert format_locator_link("argus/cli.py") == "`argus/cli.py`"
    assert format_locator_link("argus\\cli.py", 42) == "`argus/cli.py:42`"


def test_render_markdown_table() -> None:
    headers = ["Col 1", "Col 2"]
    rows = [["Val 1", "Val 2"], ["Val 3", "Val 4"]]
    table = render_markdown_table(headers, rows)
    assert "| Col 1 | Col 2 |" in table
    assert "| Val 1 | Val 2 |" in table


def test_render_final_verdict_report() -> None:
    req = AuditRequest(repo_path=".", commit="HEAD", budget=0, materiality_bar="")
    entries = [grade_entry(file_path=f"file_{i}.py", proposed_depth=CoverageDepth.AUDITED_DEEP, claim_present=True) for i in range(5)]
    ledger = CoverageLedger.build(entries)
    verdict = evaluate_verdict(ledger, ())

    markdown = render_final_verdict_report(req, verdict, ledger, 0)
    assert "RELEASE_READY" in markdown
    assert "5/5" in markdown
    assert "Negative Assurance & Scope Disclaimer" in markdown


def test_generate_reports(tmp_path: Path) -> None:
    req = AuditRequest(
        repo_path=".",
        commit="HEAD",
        budget=0,
        materiality_bar="",
        enabled_reports=("final-verdict", "security-review", "architecture-review"),
    )
    entries = [
        grade_entry(file_path="file_1.py", proposed_depth=CoverageDepth.AUDITED_DEEP, claim_present=True),
        grade_entry(file_path="file_2.py", proposed_depth=CoverageDepth.AUDITED_SHALLOW, claim_present=False),
    ]
    ledger = CoverageLedger.build(entries)
    verdict = evaluate_verdict(ledger, ())
    findings = [

        {
            "detector_id": "secret_scan",
            "rule_id": "hardcoded_secret",
            "file_path": "config.py",
            "line_number": 12,
            "snippet": "AKIA1234567890SECRET",
        },
        {
            "detector_id": "orphan_code",
            "rule_id": "orphan_code",
            "file_path": "unused.py",
            "line_number": 5,
            "message": "Unreferenced function 'foo'",
        },
    ]

    out_dir = tmp_path / "reports"
    generated = generate_reports(req, verdict, ledger, findings, out_dir)

    assert "final-verdict" in generated
    assert "security-review" in generated
    assert "architecture-review" in generated

    sec_content = generated["security-review"].read_text(encoding="utf-8")
    assert "AKIA****************" in sec_content  # Masked secret
    assert "`config.py:12`" in sec_content

    arch_content = generated["architecture-review"].read_text(encoding="utf-8")
    assert "Unreferenced function 'foo'" in arch_content


# ── Regression: the reports must read the SHAPE THE PIPELINE ACTUALLY EMITS ──
#
# The suite above builds finding dicts by hand with `detector_id` / `file_path` /
# `line_number` / `snippet`. A real finding has NONE of those keys: the pipeline
# passes `Recording.model_dump()`, which carries `rule_id` + a `locators` LIST.
# Because the hand-built shape agreed with the implementation's assumption, a filter
# on `detector_id` passed every test while dropping 100% of real secret findings —
# the security report told operators "no hardcoded credentials detected" on a repo
# where the scanner had just written a `hardcoded_secret` row to `.argus/findings/`.
#
# These tests mint findings through the REAL `build_recording` path, so the fixture
# cannot drift from the contract again without failing.


def _real_finding(rule_id: str, file_path: str, line: int, *, ast_span: str | None = None) -> dict[str, object]:
    """A finding dict exactly as the pipeline produces it (`Recording.model_dump()`)."""
    from argus.detectors.base import FindingDraft, build_recording

    draft = FindingDraft(
        file_path=file_path,
        start_line=line,
        end_line=line,
        ast_span=ast_span,
        rule_id=rule_id,
        advisory=True,
    )
    return build_recording(draft, depth_supported=None, claim_present=False).model_dump()


def test_security_report_reports_real_recording_secret_findings() -> None:
    """A real `hardcoded_secret` Recording MUST appear in the security report."""
    req = AuditRequest(repo_path=".", commit="HEAD", budget=0, materiality_bar="")
    findings = [
        _real_finding("hardcoded_secret", "config.py", 12),
        _real_finding("orphan_code", "unused.py", 5),
    ]

    content = render_security_review_report(req, findings)

    assert "**Total Security Findings**: **1**" in content
    assert "`config.py:12`" in content
    # The false-negative sentence must NOT be emitted when a secret was found.
    assert "No high-entropy secrets or hardcoded credentials detected" not in content


def test_security_report_never_prints_a_secret_value() -> None:
    """A real Recording carries no value, so no value may appear (NFR-S2)."""
    req = AuditRequest(repo_path=".", commit="HEAD", budget=0, materiality_bar="")
    content = render_security_review_report(
        req, [_real_finding("hardcoded_secret", "config.py", 12)]
    )
    assert "value discarded at detection" in content


def test_architecture_report_locates_real_recording_findings() -> None:
    """A real `orphan_code` Recording must carry a populated Location + Details."""
    req = AuditRequest(repo_path=".", commit="HEAD", budget=0, materiality_bar="")
    findings = [_real_finding("orphan_code", "unused.py", 5, ast_span="function:foo@5-9")]

    content = render_architecture_review_report(req, findings)

    assert "**Architecture Findings Count**: **1**" in content
    assert "`unused.py:5`" in content
    assert "function:foo@5-9" in content


def test_reports_agree_on_finding_identity_across_both_shapes() -> None:
    """The real and legacy shapes must classify to the same rule id (one reader)."""
    from argus.reports.generator import _finding_rule_id

    real = _real_finding("hardcoded_secret", "a.py", 1)
    legacy = {"detector_id": "secret_scan", "file_path": "a.py", "line_number": 1}
    assert _finding_rule_id(real) == "hardcoded_secret"
    assert _finding_rule_id(legacy) == "secret_scan"
