"""Comprehensive unit test suite for LSP Diagnostic Adapter (argus.adapters.lsp).

Tests line index conversion, severity mapping, JSON-RPC 2.0 framing format,
file path to URI mapping, stdio/socket streaming, and model immutability.
"""

from __future__ import annotations

import io
import socket
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from argus.adapters.lsp import (
    JSONRPCNotification,
    LSPDiagnostic,
    LSPDiagnosticAdapter,
    LSPDiagnosticRelatedInformation,
    LSPDiagnosticServer,
    LSPDiagnosticSeverity,
    LSPLocation,
    LSPPosition,
    LSPRange,
    PublishDiagnosticsParams,
    file_path_to_uri,
    format_jsonrpc_message,
    map_severity,
)
from argus.detectors.base import FindingDraft
from argus.ledger.coverage_ledger import CoverageDepth
from argus.ledger.recording import Locator, Recording


def test_lsp_models_immutability_and_extra_forbid() -> None:
    """Verify LSP models enforce frozen=True and extra='forbid'."""
    pos = LSPPosition(line=0, character=5)
    assert pos.line == 0
    assert pos.character == 5

    # Test frozen immutability
    with pytest.raises((ValidationError, TypeError)):
        pos.line = 10  # type: ignore[misc]

    # Test extra forbidden fields
    with pytest.raises(ValidationError):
        LSPPosition(line=0, character=5, unknown_field="invalid")  # type: ignore[call-arg]

    rng = LSPRange(start=LSPPosition(line=0, character=0), end=LSPPosition(line=4, character=0))
    with pytest.raises((ValidationError, TypeError)):
        rng.start = LSPPosition(line=1, character=1)  # type: ignore[misc]

    with pytest.raises(ValidationError):
        LSPRange(
            start=LSPPosition(line=0, character=0),
            end=LSPPosition(line=1, character=0),
            bogus="value",  # type: ignore[call-arg]
        )


def test_line_1_based_to_0_based_conversion() -> None:
    """Verify 1-based inclusive locator lines map to 0-based LSP range line positions."""
    loc = Locator(file_path="argus/cli.py", start_line=1, end_line=15)
    rec = Recording(
        recording_id="test_rec_1",
        rule_id="VACUOUS_TEST",
        advisory=False,
        locators=(loc,),
    )

    diag = LSPDiagnosticAdapter.map_recording(rec)
    assert diag.range.start.line == 0
    assert diag.range.start.character == 0
    assert diag.range.end.line == 14
    assert diag.range.end.character == 0
    assert diag.severity == LSPDiagnosticSeverity.ERROR
    assert diag.code == "VACUOUS_TEST"
    assert diag.source == "ArgusAgent"


def test_finding_draft_to_lsp_diagnostic() -> None:
    """Verify FindingDraft maps cleanly to LSPDiagnostic."""
    draft = FindingDraft(
        file_path="argus/pipeline.py",
        start_line=10,
        end_line=20,
        rule_id="SECRET_SCAN",
        advisory=True,
    )

    diag = LSPDiagnosticAdapter.map_draft(draft, depth_supported=CoverageDepth.AUDITED_DEEP)
    assert diag.range.start.line == 9
    assert diag.range.end.line == 19
    assert diag.severity == LSPDiagnosticSeverity.WARNING
    assert diag.code == "SECRET_SCAN"


def test_severity_mapping_rules() -> None:
    """Verify severity grade mapping for blocking vs advisory findings."""
    # Non-advisory blocking -> ERROR (1)
    assert map_severity(advisory=False) == LSPDiagnosticSeverity.ERROR
    assert map_severity(advisory=False, depth_supported=CoverageDepth.AUDITED_DEEP) == LSPDiagnosticSeverity.ERROR

    # Advisory with supported depth -> WARNING (2)
    assert map_severity(advisory=True, depth_supported=CoverageDepth.AUDITED_DEEP) == LSPDiagnosticSeverity.WARNING
    assert map_severity(advisory=True, depth_supported="DEEP") == LSPDiagnosticSeverity.WARNING

    # Advisory without supported depth (shallow/heuristic) -> INFORMATION (3)
    assert map_severity(advisory=True, depth_supported=None) == LSPDiagnosticSeverity.INFORMATION


def test_file_path_to_uri_conversion() -> None:
    """Verify relative and absolute file paths convert to file:/// URIs correctly."""
    uri_existing = "file:///d:/ProjectX/test.py"
    assert file_path_to_uri(uri_existing) == uri_existing

    rel_path = "argus/cli.py"
    uri_rel = file_path_to_uri(rel_path, workspace_root=".")
    assert uri_rel.startswith("file:///")
    assert "argus/cli.py" in uri_rel or "argus\\cli.py" in uri_rel or "cli.py" in uri_rel


def test_jsonrpc_framing_format() -> None:
    """Verify JSON-RPC 2.0 Content-Length framing header and body formatting."""
    pos = LSPPosition(line=2, character=0)
    rng = LSPRange(start=pos, end=pos)
    diag = LSPDiagnostic(
        range=rng,
        severity=LSPDiagnosticSeverity.WARNING,
        code="RULE_001",
        source="ArgusAgent",
        message="Test warning diagnostic",
    )
    params = PublishDiagnosticsParams(
        uri="file:///test/file.py",
        diagnostics=[diag],
    )
    notification = JSONRPCNotification(params=params)

    formatted = format_jsonrpc_message(notification)
    assert formatted.startswith("Content-Length: ")
    assert "\r\n\r\n" in formatted

    header_part, payload_part = formatted.split("\r\n\r\n", 1)
    content_len_str = header_part.split("Content-Length: ")[1]
    expected_len = len(payload_part.encode("utf-8"))
    assert int(content_len_str) == expected_len
    assert '"jsonrpc":"2.0"' in payload_part
    assert '"method":"textDocument/publishDiagnostics"' in payload_part


def test_server_stdio_string_stream() -> None:
    """Verify streaming diagnostic payloads to a text stream (StringIO)."""
    buf = io.StringIO()
    pos = LSPPosition(line=0, character=0)
    diag = LSPDiagnostic(
        range=LSPRange(start=pos, end=pos),
        severity=LSPDiagnosticSeverity.ERROR,
        message="Blocking error",
    )
    params = PublishDiagnosticsParams(uri="file:///test/main.py", diagnostics=[diag])

    bytes_sent = LSPDiagnosticServer.publish_diagnostics(buf, params)
    assert bytes_sent > 0
    output = buf.getvalue()
    assert output.startswith("Content-Length: ")
    assert "Blocking error" in output


def test_server_stdio_binary_stream() -> None:
    """Verify streaming diagnostic payloads to a binary stream (BytesIO)."""
    buf = io.BytesIO()
    pos = LSPPosition(line=1, character=0)
    diag = LSPDiagnostic(
        range=LSPRange(start=pos, end=pos),
        severity=LSPDiagnosticSeverity.INFORMATION,
        message="Info diagnostic",
    )
    params = PublishDiagnosticsParams(uri="file:///test/main.py", diagnostics=[diag])

    bytes_sent = LSPDiagnosticServer.publish_diagnostics(buf, params)
    assert bytes_sent > 0
    raw_bytes = buf.getvalue()
    assert raw_bytes.startswith(b"Content-Length: ")
    assert b"Info diagnostic" in raw_bytes


def test_server_socket_stream() -> None:
    """Verify streaming diagnostic payloads to a mock socket."""
    mock_sock = MagicMock(spec=socket.socket)
    pos = LSPPosition(line=1, character=0)
    diag = LSPDiagnostic(
        range=LSPRange(start=pos, end=pos),
        severity=LSPDiagnosticSeverity.HINT,
        message="Hint diagnostic",
    )
    params = PublishDiagnosticsParams(uri="file:///test/main.py", diagnostics=[diag])

    bytes_sent = LSPDiagnosticServer.publish_diagnostics(mock_sock, params)
    assert bytes_sent > 0
    mock_sock.sendall.assert_called_once()
    sent_data = mock_sock.sendall.call_args[0][0]
    assert isinstance(sent_data, bytes)
    assert b"Hint diagnostic" in sent_data


def test_server_batch_publish_recordings() -> None:
    """Verify batch publishing recordings grouped by URI."""
    loc1 = Locator(file_path="src/a.py", start_line=1, end_line=5)
    loc2 = Locator(file_path="src/b.py", start_line=3, end_line=8)
    rec1 = Recording(recording_id="rec1", rule_id="RULE1", advisory=False, locators=(loc1,))
    rec2 = Recording(recording_id="rec2", rule_id="RULE2", advisory=True, locators=(loc2,))

    buf = io.StringIO()
    total_bytes = LSPDiagnosticServer.publish_recordings(buf, [rec1, rec2], workspace_root=".")
    assert total_bytes > 0
    output = buf.getvalue()
    # Should have 2 notifications formatted with headers
    assert output.count("Content-Length: ") == 2
    assert "RULE1" in output
    assert "RULE2" in output


def test_server_graceful_stream_error_handling() -> None:
    """Verify closed/broken stream errors are caught gracefully without process panic."""
    failing_stream = MagicMock()
    failing_stream.write.side_effect = BrokenPipeError("Broken pipe")

    pos = LSPPosition(line=0, character=0)
    diag = LSPDiagnostic(
        range=LSPRange(start=pos, end=pos),
        severity=LSPDiagnosticSeverity.ERROR,
        message="Fatal error test",
    )
    params = PublishDiagnosticsParams(uri="file:///test/broken.py", diagnostics=[diag])

    # Should not raise BrokenPipeError; return 0 bytes
    bytes_sent = LSPDiagnosticServer.publish_diagnostics(failing_stream, params)
    assert bytes_sent == 0


def test_related_information_model() -> None:
    """Verify LSPLocation and LSPDiagnosticRelatedInformation construct and validate properly."""
    loc = LSPLocation(
        uri="file:///test/other.py",
        range=LSPRange(
            start=LSPPosition(line=10, character=0),
            end=LSPPosition(line=12, character=0),
        ),
    )
    related = LSPDiagnosticRelatedInformation(
        location=loc,
        message="See definition here",
    )
    diag = LSPDiagnostic(
        range=LSPRange(
            start=LSPPosition(line=1, character=0),
            end=LSPPosition(line=1, character=0),
        ),
        severity=LSPDiagnosticSeverity.INFORMATION,
        message="Primary finding",
        relatedInformation=[related],
    )

    assert diag.relatedInformation is not None
    assert len(diag.relatedInformation) == 1
    assert diag.relatedInformation[0].location.uri == "file:///test/other.py"
    assert diag.relatedInformation[0].message == "See definition here"
