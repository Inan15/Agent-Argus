"""E2E Post-V1 Integration & Verification Test Suite (`tests/test_post_v1_integration.py`).

Drivers: Story 20.4 (Post-V1 Integration & Verification Suite).
Validates end-to-end integration across multi-language AST parsing (TS/Go/Java),
automated defect remediation patch generation, dry-run verification, workspace path containment (NFR-S1),
and LSP diagnostic server JSON-RPC streaming over stdio and socket transports.
"""

from __future__ import annotations

import io
import socket
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from argus.adapters.lsp import (
    JSONRPCNotification,
    LSPDiagnostic,
    LSPDiagnosticAdapter,
    LSPDiagnosticServer,
    LSPDiagnosticSeverity,
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
from argus.parsers import (
    ASTNodeSummary,
    BaseASTParser,
    GoParser,
    JavaParser,
    ParserErrorNode,
    ParseResult,
    TSParser,
)
from argus.remediation import (
    RemediationEngine,
    RemediationPatch,
    RemediationResult,
    apply_patch,
    verify_patch_dry_run,
)


def _make_recording(
    recording_id: str = "rec_e2e_001",
    file_path: str = "tests/test_sample.py",
    start_line: int = 1,
    end_line: int = 4,
    rule_id: str = "vacuous_test_ast",
    advisory: bool = True,
) -> Recording:
    locator = Locator(file_path=file_path, start_line=start_line, end_line=end_line)
    return Recording(
        recording_id=recording_id,
        rule_id=rule_id,
        advisory=advisory,
        locators=(locator,),
    )


class TestPostV1DataModelsPureContract:
    """Verify all Post-V1 pure data models enforce immutability and forbid extra fields."""

    def test_parser_models_pure_contract(self) -> None:
        """Verify ParseResult, ParserErrorNode, and ASTNodeSummary contracts."""
        err = ParserErrorNode(line=10, column=4, node_type="ERROR", unexpected_text="let = ;")
        with pytest.raises((ValidationError, TypeError)):
            err.line = 20  # type: ignore[misc]
        with pytest.raises(ValidationError):
            ParserErrorNode(line=1, column=1, node_type="ERROR", unexpected_text="x", invalid_field=True)  # type: ignore[call-arg]

        summary = ASTNodeSummary(type="program", start_line=1, end_line=50, start_col=0, end_col=10, children_count=5)
        with pytest.raises((ValidationError, TypeError)):
            summary.children_count = 10  # type: ignore[misc]

        res = ParseResult(
            file_path="src/app.ts",
            language="typescript",
            ast_eligible=True,
            has_errors=False,
            root_node=summary,
            error_nodes=(),
            definitions=(("function", "app"),),
            edges=(),
        )
        assert res.ast_eligible is True
        with pytest.raises((ValidationError, TypeError)):
            res.ast_eligible = False  # type: ignore[misc]
        with pytest.raises(ValidationError):
            ParseResult(
                file_path="x.ts",
                language="ts",
                ast_eligible=True,
                has_errors=False,
                root_node=None,
                error_nodes=(),
                definitions=(),
                edges=(),
                extra_attr="invalid",  # type: ignore[call-arg]
            )

    def test_remediation_models_pure_contract(self) -> None:
        """Verify RemediationPatch and RemediationResult contracts."""
        patch = RemediationPatch(
            finding_id="f1",
            target_file="src/utils.py",
            diff_content="--- a/src/utils.py\n+++ b/src/utils.py\n",
            affected_lines=(5,),
            patch_id="patch:f1",
            created_at="2026-08-29T00:00:00Z",
        )
        with pytest.raises((ValidationError, TypeError)):
            patch.target_file = "other.py"  # type: ignore[misc]
        with pytest.raises(ValidationError):
            RemediationPatch(
                finding_id="f1",
                target_file="src/utils.py",
                diff_content="...",
                affected_lines=(1,),
                patch_id="p1",
                created_at="2026-08-29T00:00:00Z",
                extra_field="fail",  # type: ignore[call-arg]
            )

        res = RemediationResult(
            patches=(patch,),
            success=True,
            dry_run_verified=True,
            applied_count=1,
            errors=(),
        )
        with pytest.raises((ValidationError, TypeError)):
            res.success = False  # type: ignore[misc]

    def test_lsp_models_pure_contract(self) -> None:
        """Verify LSP models enforce frozen=True and extra='forbid'."""
        pos = LSPPosition(line=5, character=10)
        with pytest.raises((ValidationError, TypeError)):
            pos.line = 0  # type: ignore[misc]
        with pytest.raises(ValidationError):
            LSPPosition(line=1, character=1, invalid_arg=123)  # type: ignore[call-arg]

        rng = LSPRange(start=LSPPosition(line=0, character=0), end=LSPPosition(line=10, character=0))
        diag = LSPDiagnostic(
            range=rng,
            severity=LSPDiagnosticSeverity.ERROR,
            code="VACUOUS_TEST",
            source="ArgusAgent",
            message="Vacuous assertion detected",
        )
        with pytest.raises((ValidationError, TypeError)):
            diag.severity = LSPDiagnosticSeverity.WARNING  # type: ignore[misc]
        with pytest.raises(ValidationError):
            LSPDiagnostic(range=rng, severity=LSPDiagnosticSeverity.ERROR, message="m", extra_key="err")  # type: ignore[call-arg]


class TestE2EMultiLanguageASTParsing:
    """E2E Multi-Language AST Parsing Integration Tests (AC #1)."""

    def test_tsparser_clean_and_error_recovery(self) -> None:
        """Exercise TSParser across TypeScript, TSX, and JS sources."""
        parser = TSParser()
        assert issubclass(TSParser, BaseASTParser)
        assert parser.supports_language("typescript")
        assert parser.supports_language("tsx")
        assert parser.supports_language("javascript")

        # Clean TypeScript snippet
        clean_ts = """
        interface User {
            id: number;
            name: string;
        }
        function getUserName(user: User): string {
            return user.name;
        }
        """
        res_ts = parser.parse_source(clean_ts, file_path="src/user.ts")
        assert res_ts.ast_eligible is True
        assert res_ts.has_errors is False
        assert res_ts.language == "typescript"
        assert res_ts.root_node is not None
        assert res_ts.root_node.type == "program"
        assert len(res_ts.definitions) > 0

        # Clean TSX snippet
        clean_tsx = """
        export const Button = ({ label }: { label: string }) => {
            return <button>{label}</button>;
        };
        """
        res_tsx = parser.parse_source(clean_tsx, file_path="src/Button.tsx")
        assert res_tsx.ast_eligible is True
        assert res_tsx.has_errors is False

        # Malformed TypeScript snippet (error recovery)
        bad_ts = "function broken(x: string { const y = ;"
        res_bad = parser.parse_source(bad_ts, file_path="src/bad.ts")
        assert res_bad.ast_eligible is True
        assert res_bad.has_errors is True
        assert len(res_bad.error_nodes) > 0
        err_node = res_bad.error_nodes[0]
        assert err_node.node_type in ("ERROR", "MISSING")

    def test_goparser_clean_and_error_recovery(self) -> None:
        """Exercise GoParser across Go source snippets."""
        parser = GoParser()
        assert issubclass(GoParser, BaseASTParser)
        assert parser.supports_language("go")

        clean_go = """
        package main

        import "fmt"

        type Account struct {
            ID   string
            Balance float64
        }

        func (a *Account) Deposit(amount float64) float64 {
            a.Balance += amount
            fmt.Println("Deposited", amount)
            return a.Balance
        }
        """
        res_go = parser.parse_source(clean_go, file_path="pkg/account.go")
        assert res_go.ast_eligible is True
        assert res_go.has_errors is False
        assert res_go.language == "go"
        assert ("function", "Deposit") in res_go.definitions or ("method", "Deposit") in res_go.definitions or ("struct", "Account") in res_go.definitions

        # Malformed Go snippet
        bad_go = "package main; func broken(a int { fmt.Println("
        res_bad = parser.parse_source(bad_go, file_path="pkg/bad.go")
        assert res_bad.ast_eligible is True
        assert res_bad.has_errors is True
        assert len(res_bad.error_nodes) > 0

    def test_javaparser_clean_and_error_recovery(self) -> None:
        """Exercise JavaParser across Java source snippets."""
        parser = JavaParser()
        assert issubclass(JavaParser, BaseASTParser)
        assert parser.supports_language("java")

        clean_java = """
        package com.example;

        public class Service {
            private String name;

            public Service(String name) {
                this.name = name;
            }

            public String getName() {
                return this.name;
            }
        }
        """
        res_java = parser.parse_source(clean_java, file_path="src/main/java/Service.java")
        assert res_java.ast_eligible is True
        assert res_java.has_errors is False
        assert res_java.language == "java"
        assert ("class", "Service") in res_java.definitions or ("function", "getName") in res_java.definitions

        # Malformed Java snippet
        bad_java = "public class Bad { public void run( {"
        res_bad = parser.parse_source(bad_java, file_path="src/main/java/Bad.java")
        assert res_bad.ast_eligible is True
        assert res_bad.has_errors is True
        assert len(res_bad.error_nodes) > 0


class TestE2EAutomatedDefectRemediation:
    """E2E Automated Defect Remediation & Patch Verification (AC #2)."""

    def test_patch_generation_vacuous_assertion(self) -> None:
        """Verify remediation engine patch generation for vacuous assertions."""
        source = (
            "def test_calculator():\n"
            "    val = compute_total()\n"
            "    assert True\n"
        )
        rec = _make_recording(start_line=1, end_line=3)
        engine = RemediationEngine()
        patch = engine.generate_patch(rec, source)

        assert patch is not None
        assert patch.target_file == "tests/test_sample.py"
        assert "assert val is not None" in patch.diff_content
        assert patch.affected_lines == (3,)

    def test_patch_dry_run_verification(self) -> None:
        """Verify dry-run in-memory AST syntax validation of generated patches."""
        source = (
            "def test_valid():\n"
            "    data = fetch_data()\n"
            "    assert 1 == 1\n"
        )
        rec = _make_recording(start_line=1, end_line=3)
        engine = RemediationEngine()
        patch = engine.generate_patch(rec, source)
        assert patch is not None

        # Valid dry run
        is_valid = verify_patch_dry_run(source, patch)
        assert is_valid is True

        # Invalid dry run with corrupt diff
        corrupt_patch = RemediationPatch(
            finding_id="f_corrupt",
            target_file="tests/test_sample.py",
            diff_content=(
                "--- a/tests/test_sample.py\n"
                "+++ b/tests/test_sample.py\n"
                "@@ -1,3 +1,3 @@\n"
                " def test_valid():\n"
                "     data = fetch_data()\n"
                "-    assert 1 == 1\n"
                "+    assert ((( invalid syntax\n"
            ),
            affected_lines=(3,),
            patch_id="p_corrupt",
            created_at="2026-08-29T00:00:00Z",
        )
        assert verify_patch_dry_run(source, corrupt_patch) is False

    def test_apply_patch_workspace_containment_nfr_s1(self) -> None:
        """Verify apply_patch workspace path containment protection (NFR-S1)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            ws_root = Path(tmp_dir).resolve()
            test_dir = ws_root / "tests"
            test_dir.mkdir(parents=True, exist_ok=True)
            target = test_dir / "test_sample.py"
            source = "def test_sub():\n    res = calculate()\n    assert True\n"
            target.write_text(source, encoding="utf-8")

            rec = _make_recording(file_path="tests/test_sample.py", start_line=1, end_line=3)
            engine = RemediationEngine(workspace_root=str(ws_root))
            patch = engine.generate_patch(rec, source)
            assert patch is not None

            # Apply within containment -> SUCCESS
            applied = apply_patch("tests/test_sample.py", patch, workspace_root=str(ws_root))
            assert applied is True
            patched_content = target.read_text(encoding="utf-8")
            assert "assert res is not None" in patched_content

            # Traversal escape -> REJECTED safely
            escaped = apply_patch("../outside_file.py", patch, workspace_root=str(ws_root))
            assert escaped is False


class TestE2ELSPDiagnosticStreaming:
    """E2E LSP Diagnostic Streaming & Transport Verification (AC #3)."""

    def test_lsp_finding_mapping_and_severities(self) -> None:
        """Verify recording/finding to LSP diagnostic 0-based range and severity mapping."""
        # Non-advisory blocking -> ERROR = 1
        rec_blocking = _make_recording(start_line=1, end_line=10, advisory=False)
        diag_blocking = LSPDiagnosticAdapter.map_recording(rec_blocking)
        assert diag_blocking.range.start.line == 0
        assert diag_blocking.range.end.line == 9
        assert diag_blocking.severity == LSPDiagnosticSeverity.ERROR

        # Advisory with supported depth -> WARNING = 2
        draft_warning = FindingDraft(
            file_path="argus/pipeline.py",
            start_line=5,
            end_line=15,
            rule_id="SECRET_SCAN",
            advisory=True,
        )
        diag_warning = LSPDiagnosticAdapter.map_draft(draft_warning, depth_supported=CoverageDepth.AUDITED_DEEP)
        assert diag_warning.range.start.line == 4
        assert diag_warning.range.end.line == 14
        assert diag_warning.severity == LSPDiagnosticSeverity.WARNING

        # Advisory without supported depth -> INFORMATION = 3
        diag_info = LSPDiagnosticAdapter.map_draft(draft_warning, depth_supported=None)
        assert diag_info.severity == LSPDiagnosticSeverity.INFORMATION

        # Explicit severity helper check
        assert map_severity(advisory=False) == LSPDiagnosticSeverity.ERROR
        assert map_severity(advisory=True, depth_supported=CoverageDepth.AUDITED_DEEP) == LSPDiagnosticSeverity.WARNING
        assert map_severity(advisory=True, depth_supported=None) == LSPDiagnosticSeverity.INFORMATION

    def test_jsonrpc_framing_and_serialization(self) -> None:
        """Verify JSON-RPC 2.0 notification framing and Content-Length header format."""
        pos = LSPPosition(line=0, character=0)
        diag = LSPDiagnostic(
            range=LSPRange(start=pos, end=pos),
            severity=LSPDiagnosticSeverity.ERROR,
            code="VACUOUS_TEST",
            source="ArgusAgent",
            message="Vacuous test pattern found",
        )
        uri = file_path_to_uri("tests/test_foo.py", workspace_root=".")
        params = PublishDiagnosticsParams(uri=uri, diagnostics=[diag])
        notification = JSONRPCNotification(params=params)

        message = format_jsonrpc_message(notification)
        assert message.startswith("Content-Length: ")
        assert "\r\n\r\n" in message

        header, body = message.split("\r\n\r\n", 1)
        length_str = header.split("Content-Length: ")[1]
        assert int(length_str) == len(body.encode("utf-8"))
        assert '"jsonrpc":"2.0"' in body
        assert '"method":"textDocument/publishDiagnostics"' in body
        assert '"VACUOUS_TEST"' in body

    def test_lsp_server_streaming_transports(self) -> None:
        """Verify LSP server streaming over text (StringIO), binary (BytesIO), and socket IO."""
        pos = LSPPosition(line=2, character=0)
        diag = LSPDiagnostic(range=LSPRange(start=pos, end=pos), severity=LSPDiagnosticSeverity.WARNING, message="Warn")
        params = PublishDiagnosticsParams(uri="file:///src/main.ts", diagnostics=[diag])

        # Text stream (StringIO)
        text_stream = io.StringIO()
        bytes_text = LSPDiagnosticServer.publish_diagnostics(text_stream, params)
        assert bytes_text > 0
        text_out = text_stream.getvalue()
        assert "Content-Length: " in text_out
        assert "file:///src/main.ts" in text_out

        # Binary stream (BytesIO)
        bin_stream = io.BytesIO()
        bytes_bin = LSPDiagnosticServer.publish_diagnostics(bin_stream, params)
        assert bytes_bin > 0
        bin_out = bin_stream.getvalue()
        assert b"Content-Length: " in bin_out
        assert b"file:///src/main.ts" in bin_out

        # Mock socket stream
        mock_sock = MagicMock(spec=socket.socket)
        bytes_sock = LSPDiagnosticServer.publish_diagnostics(mock_sock, params)
        assert bytes_sock > 0
        mock_sock.sendall.assert_called_once()
        sent_bytes = mock_sock.sendall.call_args[0][0]
        assert isinstance(sent_bytes, bytes)
        assert b"Content-Length: " in sent_bytes

    def test_lsp_server_broken_stream_error_handling(self) -> None:
        """Verify broken or closed streams are handled gracefully without process panic."""
        broken_stream = MagicMock()
        broken_stream.write.side_effect = OSError("Connection reset by peer")

        pos = LSPPosition(line=0, character=0)
        diag = LSPDiagnostic(range=LSPRange(start=pos, end=pos), severity=LSPDiagnosticSeverity.ERROR, message="Err")
        params = PublishDiagnosticsParams(uri="file:///src/broken.py", diagnostics=[diag])

        bytes_sent = LSPDiagnosticServer.publish_diagnostics(broken_stream, params)
        assert bytes_sent == 0


class TestCombinedPostV1Pipeline:
    """Combined E2E Pipeline: Parsing -> Defect Detection -> LSP Notification -> Remediation Patch (AC #1, #2, #3, #4)."""

    def test_e2e_pipeline_multi_language_to_remediation_and_lsp(self) -> None:
        """Full end-to-end integration flow across all Post-V1 components."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            ws_root = Path(tmp_dir).resolve()
            tests_dir = ws_root / "tests"
            tests_dir.mkdir(parents=True, exist_ok=True)

            # 1. Source file in workspace containing a vacuous assertion defect
            test_file = tests_dir / "test_integration.py"
            source_code = (
                "def test_service_health():\n"
                "    status = check_health()\n"
                "    assert True\n"
            )
            test_file.write_text(source_code, encoding="utf-8")

            # 2. Multi-language AST parse check (Python/TS/Go/Java)
            ts_parser = TSParser()
            go_parser = GoParser()
            java_parser = JavaParser()

            ts_res = ts_parser.parse_source("function test() { return true; }", file_path="test.ts")
            go_res = go_parser.parse_source("package main; func test() {}", file_path="test.go")
            java_res = java_parser.parse_source("public class Test {}", file_path="Test.java")

            assert ts_res.ast_eligible and not ts_res.has_errors
            assert go_res.ast_eligible and not go_res.has_errors
            assert java_res.ast_eligible and not java_res.has_errors

            # 3. Simulate detection & recording generation for vacuous test
            rec = _make_recording(
                recording_id="rec_pipeline_01",
                file_path="tests/test_integration.py",
                start_line=1,
                end_line=3,
                rule_id="vacuous_test_ast",
                advisory=True,
            )

            # 4. Stream LSP diagnostic notification over stdio text buffer
            lsp_stream = io.StringIO()
            bytes_streamed = LSPDiagnosticServer.publish_recordings(
                stream=lsp_stream,
                recordings=[rec],
                workspace_root=str(ws_root),
            )
            assert bytes_streamed > 0
            lsp_payload = lsp_stream.getvalue()
            assert "Content-Length: " in lsp_payload
            assert "vacuous_test_ast" in lsp_payload

            # 5. Defect remediation patch generation & dry-run AST verification
            engine = RemediationEngine(workspace_root=str(ws_root))
            patch = engine.generate_patch(rec, source_code)
            assert patch is not None
            assert "assert status is not None" in patch.diff_content

            dry_run_passed = verify_patch_dry_run(source_code, patch)
            assert dry_run_passed is True

            # 6. Apply remediation patch to workspace file within containment bounds
            applied = apply_patch("tests/test_integration.py", patch, workspace_root=str(ws_root))
            assert applied is True

            # 7. Verify file on disk now has remediated code
            remediated_code = test_file.read_text(encoding="utf-8")
            assert "assert status is not None" in remediated_code
            assert "assert True" not in remediated_code
