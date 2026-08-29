---
baseline_commit: 41f84ef4d06e1250df41c39c80c579d4eeadda69
---

# Story 20.3: LSP Diagnostic Adapter (`argus.adapters.lsp`)

Status: done

<!-- Contexted 2026-08-29 at HEAD `41f84ef4d06e1250df41c39c80c579d4eeadda69` (branch `master`) by the bmad-create-story workflow.

     This story implements the LSP JSON-RPC 2.0 diagnostic adapter (`argus.adapters.lsp`) for ArgusAgent,
     streaming findings (`Recording` / `FindingDraft`) directly into IDE code editors (VS Code / Antigravity)
     with inline severity mapping (`textDocument/publishDiagnostics`) over stdio and socket transports.
-->

## Story

As a **Software Security & Quality Audit Engineer**,
I want **an LSP-compatible diagnostic adapter (`argus.adapters.lsp`) streaming ArgusAgent findings as JSON-RPC 2.0 `textDocument/publishDiagnostics` notifications over stdio and socket streams**,
so that **developers using IDE code editors (such as VS Code or Antigravity) receive real-time, inline severity-annotated diagnostics for vacuous assertions, security defects, and code quality issues directly within their editor window.**

## Acceptance Criteria

1. **LSP Data Models & Protocol Contracts (`argus.adapters.lsp.models`)**:
   - `LSPPosition` frozen PURE Pydantic model (`line: int >= 0`, `character: int >= 0`).
   - `LSPRange` frozen PURE Pydantic model (`start: LSPPosition`, `end: LSPPosition`).
   - `LSPDiagnosticSeverity` Enum: `ERROR = 1`, `WARNING = 2`, `INFORMATION = 3`, `HINT = 4`.
   - `LSPDiagnostic` frozen PURE Pydantic model (`range: LSPRange`, `severity: LSPDiagnosticSeverity`, `code: str | int | None`, `source: str`, `message: str`, `relatedInformation: list[LSPDiagnosticRelatedInformation] | None = None`).
   - `PublishDiagnosticsParams` frozen PURE Pydantic model (`uri: str`, `diagnostics: list[LSPDiagnostic]`, `version: int | None = None`).
   - `JSONRPCNotification` frozen PURE Pydantic model (`jsonrpc: Literal["2.0"] = "2.0"`, `method: str = "textDocument/publishDiagnostics"`, `params: PublishDiagnosticsParams`).
   - All PURE models use `model_config = ConfigDict(frozen=True, extra="forbid")`.

2. **Finding to LSP Diagnostic Mapper (`argus.adapters.lsp.adapter`)**:
   - `LSPDiagnosticAdapter` converts Argus findings (`Recording`, `FindingDraft`, or detector findings) into `LSPDiagnostic` instances.
   - Maps 1-based inclusive line spans (`start_line`, `end_line`) from `Locator` into 0-based LSP range line positions (`line = start_line - 1`, `character = 0`).
   - Inline Severity Mapping:
     - Non-advisory blocking findings (`advisory == False`) map to `LSPDiagnosticSeverity.ERROR` (1).
     - Advisory findings with `depth_supported` coverage map to `LSPDiagnosticSeverity.WARNING` (2).
     - Advisory shallow/heuristic findings map to `LSPDiagnosticSeverity.INFORMATION` (3) or `HINT` (4).
   - Generates document URIs in standard `file:///` format (`file_path_to_uri(file_path: str, workspace_root: str = ".") -> str`).

3. **JSON-RPC 2.0 Streaming Server / Transport (`argus.adapters.lsp.server`)**:
   - `LSPDiagnosticServer` / `LSPStreamer` serializes `JSONRPCNotification` into standard LSP header-framed JSON-RPC 2.0 byte/string format (`Content-Length: <len>\r\n\r\n<json_payload>`).
   - Supports streaming diagnostic payloads over `stdio` (stdout stream writer) and `socket` connection streams without process panic or unhandled exceptions.
   - Supports batch publishing of diagnostics aggregated by document URI across multiple findings.

4. **Package Integration & Comprehensive Verification**:
   - Exported through `argus.adapters.lsp` package (`LSPDiagnosticAdapter`, `LSPDiagnosticServer`, `LSPDiagnostic`, `LSPDiagnosticSeverity`, `PublishDiagnosticsParams`, `JSONRPCNotification`).
   - Standard 100% green test matrix in `tests/test_lsp_adapter.py`.
   - Preserves all V1 invariants (PURE models, zero stdout pollution in library paths, typed error handling, POSIX relative path containment under NFR-S1).

---

## Tasks / Subtasks

- [x] Task 1: Define LSP PURE Pydantic Data Models & Protocol Contracts in `argus/adapters/lsp/models.py` (AC: #1, #2)
  - [x] Implement `LSPPosition` (frozen BaseModel: `line`, `character`).
  - [x] Implement `LSPRange` (frozen BaseModel: `start`, `end`).
  - [x] Implement `LSPDiagnosticSeverity` Enum (`ERROR = 1`, `WARNING = 2`, `INFORMATION = 3`, `HINT = 4`).
  - [x] Implement `LSPDiagnostic` (frozen BaseModel: `range`, `severity`, `code`, `source`, `message`, `relatedInformation`).
  - [x] Implement `PublishDiagnosticsParams` (frozen BaseModel: `uri`, `diagnostics`, `version`).
  - [x] Implement `JSONRPCNotification` (frozen BaseModel: `jsonrpc = "2.0"`, `method = "textDocument/publishDiagnostics"`, `params`).

- [x] Task 2: Implement `LSPDiagnosticAdapter` finding-to-diagnostic mapper in `argus/adapters/lsp/adapter.py` (AC: #2)
  - [x] Implement 1-based to 0-based line index conversion (`start_line - 1`, `end_line - 1`).
  - [x] Implement `file_path_to_uri` converting workspace relative file paths to `file:///` URIs.
  - [x] Implement severity grade mapping rules (`advisory == False` -> `ERROR`, `advisory == True` with `depth_supported` -> `WARNING`, default -> `INFORMATION`).
  - [x] Implement `map_recording(recording: Recording, workspace_root: str = ".") -> LSPDiagnostic`.
  - [x] Implement `map_recordings_by_uri(recordings: Sequence[Recording], workspace_root: str = ".") -> dict[str, list[LSPDiagnostic]]`.

- [x] Task 3: Implement JSON-RPC 2.0 framing and streaming server in `argus/adapters/lsp/server.py` (AC: #3)
  - [x] Implement `format_jsonrpc_message(notification: JSONRPCNotification) -> str` formatting `Content-Length: <len>\r\n\r\n{json_body}`.
  - [x] Implement `LSPDiagnosticServer` class with `publish_diagnostics(stream: TextIO | BinaryIO | socket, params: PublishDiagnosticsParams) -> int`.
  - [x] Implement stdio and socket streaming channels with graceful error handling and zero unhandled exceptions.

- [x] Task 4: Expose package exports in `argus/adapters/__init__.py` and `argus/adapters/lsp/__init__.py` (AC: #4)
  - [x] Export `LSPDiagnosticAdapter`, `LSPDiagnosticServer`, `LSPDiagnostic`, `LSPDiagnosticSeverity`, `LSPPosition`, `LSPRange`, `PublishDiagnosticsParams`, `JSONRPCNotification`.

- [x] Task 5: Comprehensive Test Suite in `tests/test_lsp_adapter.py` (AC: #1, #2, #3, #4)
  - [x] Test line 1-based to 0-based conversion and range calculation.
  - [x] Test severity mapping for blocking vs advisory findings.
  - [x] Test JSON-RPC 2.0 `Content-Length` framing format.
  - [x] Test file path to URI conversion and workspace containment.
  - [x] Test stdio and socket streaming transport mock execution.
  - [x] Test model immutability (`frozen=True, extra="forbid"`).

---

## Dev Notes

### Architecture & Technical Stack Requirements
- **Language / Version**: Python `>= 3.10`
- **Dependencies**: Standard library `json`, `socket`, `sys`, `typing`, `pydantic >= 2.0`
- **Contract Integrity**:
  - PURE data models must use `model_config = ConfigDict(frozen=True, extra="forbid")`.
  - All file paths MUST be relative POSIX paths within workspace containment (NFR-S1).
  - No `print()` calls to `stdout` in any `argus` module during normal operation (streaming server output must be explicitly directed through specified streams or `sys.stdout.buffer`).

### Source Tree Components to Touch
- `argus/adapters/__init__.py` [NEW]: Parent adapters package exports.
- `argus/adapters/lsp/__init__.py` [NEW]: LSP adapter package exports.
- `argus/adapters/lsp/models.py` [NEW]: PURE Pydantic data contracts (`LSPPosition`, `LSPRange`, `LSPDiagnosticSeverity`, `LSPDiagnostic`, `PublishDiagnosticsParams`, `JSONRPCNotification`).
- `argus/adapters/lsp/adapter.py` [NEW]: `LSPDiagnosticAdapter` finding-to-LSP diagnostic mapper.
- `argus/adapters/lsp/server.py` [NEW]: `LSPDiagnosticServer` JSON-RPC 2.0 streaming server over stdio/socket.
- `tests/test_lsp_adapter.py` [NEW]: Comprehensive unit and transport test suite.

### Project Structure Notes
- Package structure: `argus/adapters/lsp/` under `argus/`.
- Integrates with Argus findings (`argus.ledger.recording.Recording` and `argus.detectors.base.FindingDraft`).
- LSP 3.17 protocol standard: `textDocument/publishDiagnostics` notification method.
- LSP positions use 0-based line and character indexing (`start_line - 1`, `character = 0`).

### Technical Specifics & Latest Knowledge (LSP 3.17 & JSON-RPC 2.0)
- **JSON-RPC 2.0 Protocol**:
  - Request format: `{"jsonrpc": "2.0", "method": "textDocument/publishDiagnostics", "params": {...}}`
  - Framing: `Content-Length: <byte_count>\r\n\r\n<utf8_encoded_json_payload>`
- **Severity Levels**:
  - `1` = Error (Blocking defects, `advisory=False`)
  - `2` = Warning (Advisory with deep audit depth)
  - `3` = Information (Advisory shallow findings)
  - `4` = Hint (Informational suggestions)

### Previous Story Intelligence
- **Story 20.1 & 20.2 Learnings**:
  - Always enforce `model_config = ConfigDict(frozen=True, extra="forbid")` on Pydantic models.
  - Maintain relative POSIX path validation (NFR-S1).
  - Use `__all__` in `__init__.py` files to expose clean package interfaces.
  - Keep distribution tests (`test_built_distribution.py`) and module count documentation up to date when adding new files/packages.

### References
- [Epic 20 Specification](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/epics.md#L3920)
- [PRD Addendum Section A2 - FR39](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md#L67)
- [Sprint Change Proposal 2026-08-28](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-28.md#L48)
- [Recording Model](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/argus/ledger/recording.py#L91)
- [Detector Base Models](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/argus/detectors/base.py#L70)

---

## Dev Agent Record

### Agent Model Used

Gemini 3.6 Flash (High) / Antigravity

### Debug Log References

- `tests/test_lsp_adapter.py`
- `tests/test_built_distribution.py`

### Completion Notes List

- Implemented LSP 3.17 frozen PURE Pydantic data contracts in `argus/adapters/lsp/models.py` (`LSPPosition`, `LSPRange`, `LSPDiagnosticSeverity`, `LSPLocation`, `LSPDiagnosticRelatedInformation`, `LSPDiagnostic`, `PublishDiagnosticsParams`, `JSONRPCNotification`).
- Implemented `LSPDiagnosticAdapter` in `argus/adapters/lsp/adapter.py` with 1-based to 0-based line index conversion, URI formatting, inline severity grade mapping, and batch URI grouping.
- Implemented `LSPDiagnosticServer` and `format_jsonrpc_message` in `argus/adapters/lsp/server.py` with standard `Content-Length` header framing and graceful stdio/socket streaming.
- Exported package interfaces through `argus/adapters/__init__.py` and `argus/adapters/lsp/__init__.py`.
- Updated published distribution module figures in `CHANGELOG.md` to reflect the 108 shipped modules.
- Created comprehensive unit and transport test matrix in `tests/test_lsp_adapter.py` (12/12 passed, 100% green).
- Verified `mypy argus/` clean across all 108 source files.

### File List

- `argus/adapters/__init__.py`
- `argus/adapters/lsp/__init__.py`
- `argus/adapters/lsp/models.py`
- `argus/adapters/lsp/adapter.py`
- `argus/adapters/lsp/server.py`
- `tests/test_lsp_adapter.py`
- `CHANGELOG.md`
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
- `_bmad-output/design-artifacts/ArgusAgent/stories/20-3-lsp-diagnostic-adapter.md`

---

## Review Findings

### Review Round 1 (2026-08-29)

- **Reviewer**: BMAD Code Reviewer Subagent
- **Verdict**: PASS
- **Issues**: None
- **Tests**: PASS — `pytest tests/test_lsp_adapter.py` (12 passed in 0.19s), `pytest tests/test_built_distribution.py` (9 passed in 11.86s), `mypy argus/` clean across 108 source files.

#### Summary:
1. **Adversarial Security & Invariant Audit**: Verified frozen model immutability (`frozen=True, extra="forbid"`) across all LSP Pydantic models. Verified zero stdout pollution in normal adapter library paths, zero process panics on stream IO errors/broken pipe socket connections.
2. **Acceptance Criteria Verification**: Verified 100% compliance with AC #1 through #4:
   - AC1: Implemented frozen PURE Pydantic contracts (`LSPPosition`, `LSPRange`, `LSPDiagnosticSeverity`, `LSPDiagnostic`, `PublishDiagnosticsParams`, `JSONRPCNotification`).
   - AC2: Implemented `LSPDiagnosticAdapter` line position 1-based -> 0-based conversion, file path to `file:///` URI formatting, and severity mapping rules.
   - AC3: Implemented `LSPDiagnosticServer` and `format_jsonrpc_message` with standard `Content-Length` header framing over stdio and sockets.
   - AC4: Exported package contracts in `argus.adapters` & `argus.adapters.lsp`, with full green unit test coverage in `tests/test_lsp_adapter.py`.

