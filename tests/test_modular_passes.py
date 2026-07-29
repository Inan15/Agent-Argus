"""Tests for ArgusAgent modular pass selection and CLI controls."""

from __future__ import annotations

from pathlib import Path

import pytest

from argus.cli import main, build_parser
from argus.models import AuditRequest


def test_cli_pass_flags() -> None:
    parser = build_parser()
    args = parser.parse_args(["audit", ".", "--commit", "HEAD", "--passes", "coverage,security", "--skip-pass", "security", "--reports", "final-verdict"])
    
    assert args.passes == "coverage,security"
    assert args.skip_pass == ["security"]
    assert args.reports == "final-verdict"


def test_audit_request_pass_defaults() -> None:
    req = AuditRequest(repo_path=".", commit="HEAD", budget=0, materiality_bar="")
    assert "coverage" in req.enabled_passes
    assert "security" in req.enabled_passes
    assert "final-verdict" in req.enabled_reports


def test_audit_request_custom_passes() -> None:
    req = AuditRequest(
        repo_path=".",
        commit="HEAD",
        budget=0,
        materiality_bar="",
        enabled_passes=("coverage",),
        enabled_reports=("coverage-ledger",),
    )
    assert req.enabled_passes == ("coverage",)
    assert req.enabled_reports == ("coverage-ledger",)
    assert "security" not in req.enabled_passes
