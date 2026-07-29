"""Unit tests for secret suppression engine & mock test filtering."""

from __future__ import annotations

from argus.detectors.secret_scan import SecretScanDetector
from argus.detectors.secret_suppression import SecretSuppressionEngine
from argus.index.ast_index import AstIndexEntry
from argus.models import AuditRequest


def test_public_sentinel_suppression() -> None:
    """Public sentinels like wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY are recognized and suppressed."""
    snippet = 'MOCK_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"'
    suppressed, reason = SecretSuppressionEngine.evaluate_suppression(
        file_path="src/config.py", snippet=snippet
    )
    assert suppressed is True
    assert reason == "known_sentinel"



def test_inline_annotation_suppression() -> None:
    """Inline comments like # argus:ignore secret_scan suppress secret findings."""
    line = 'KEY = "some_secret_key_value"  # argus:ignore secret_scan'
    suppressed, reason = SecretSuppressionEngine.evaluate_suppression(
        file_path="src/auth.py", snippet="some_secret_key_value", line_content=line
    )
    assert suppressed is True
    assert reason == "inline_annotation"


def test_test_fixture_glob_suppression() -> None:
    """Findings inside tests/ or mock files are suppressed under test fixture glob."""
    suppressed, reason = SecretSuppressionEngine.evaluate_suppression(
        file_path="tests/fixtures/mock_credentials.py", snippet="mock_secret_token_12345"
    )
    assert suppressed is True
    assert reason == "test_fixture_glob"


def test_live_production_key_safeguard_overrides_folder_glob() -> None:
    """High-confidence live keys in test folders are NOT suppressed by folder glob alone."""
    live_key_snippet = "AKIA1234567890ABCDEF"  # 20-char AKIA pattern, not the sentinel
    suppressed, reason = SecretSuppressionEngine.evaluate_suppression(
        file_path="tests/fixtures/mock_credentials.py", snippet=live_key_snippet
    )
    # Live production key bypasses folder glob
    assert suppressed is False
    assert reason is None


def test_live_key_with_explicit_inline_annotation_is_suppressed() -> None:
    """Explicit inline annotation suppresses even live key patterns."""
    live_key_snippet = "AKIA1234567890ABCDEF"
    line = 'KEY = "AKIA1234567890ABCDEF"  # argus:ignore secret_scan'
    suppressed, reason = SecretSuppressionEngine.evaluate_suppression(
        file_path="tests/fixtures/mock_credentials.py",
        snippet=live_key_snippet,
        line_content=line,
    )
    assert suppressed is True
    assert reason == "inline_annotation"


def test_custom_ignore_pattern_and_path() -> None:
    """Custom ignore_paths and ignore_patterns suppress findings."""
    suppressed, reason = SecretSuppressionEngine.evaluate_suppression(
        file_path="custom_dir/file.py",
        snippet="MY_CUSTOM_SECRET_TEST_TOKEN",
        ignore_paths=("custom_dir/**",),
        ignore_patterns=("MY_CUSTOM_SECRET_*",),
    )
    assert suppressed is True


def test_secret_scan_detector_with_suppression() -> None:
    """SecretScanDetector filters out inline-annotated findings during execution."""
    detector = SecretScanDetector()
    source = 'MOCK_KEY = "AKIA1234567890ABCDEF"  # argus:ignore secret_scan\nLIVE_KEY = "AKIA9876543210FEDCBA"\n'
    ast_entry = AstIndexEntry(file_path="src/config.py", ast_eligible=True, definitions=())

    result = detector.run(file_path="src/config.py", source=source, ast_entry=ast_entry)
    # Line 1 is suppressed; findings only contain line 2 locators
    lines_flagged = {loc.start_line for f in result.findings for loc in f.locators}
    assert 1 not in lines_flagged
    assert 2 in lines_flagged



def test_audit_request_with_ignore_options() -> None:
    """AuditRequest model holds ignore_paths and ignore_patterns."""
    req = AuditRequest(
        repo_path=".",
        commit="HEAD",
        budget=0,
        materiality_bar="",
        ignore_paths=("tests/**", "fixtures/**"),
        ignore_patterns=("MOCK_*",),
    )
    payload = req.to_provenance_payload()
    assert payload["ignore_paths"] == ["tests/**", "fixtures/**"]
    assert payload["ignore_patterns"] == ["MOCK_*"]

