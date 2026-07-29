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
