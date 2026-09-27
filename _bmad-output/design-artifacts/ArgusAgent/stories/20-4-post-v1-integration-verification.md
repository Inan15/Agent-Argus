---
baseline_commit: 41f84ef4d06e1250df41c39c80c579d4eeadda69
---

# Story 20.4: Post-V1 Integration & Verification Suite (`20-4-post-v1-integration-verification`)

Status: done

<!-- Contexted 2026-08-29 at HEAD `41f84ef4d06e1250df41c39c80c579d4eeadda69` (branch `master`) by the bmad-create-story workflow.

     This story creates the E2E post-V1 integration and verification test suite (`tests/test_post_v1_integration.py`) for ArgusAgent,
     validating multi-language AST parsing (TS/Go/Java), defect remediation patch generation and dry-run verification,
     and LSP diagnostic server streaming across end-to-end multi-language source workflows while verifying
     that all Epics 1–19 core guarantees, build distribution contracts (108 modules), and test suites remain 100% green.
-->

## Story

As a **Security & Quality Audit Engineer**,
I want **an end-to-end integration and verification test suite (`tests/test_post_v1_integration.py`) validating multi-language AST parsing, defect remediation diff generation, and LSP diagnostic streaming alongside full regression verification of Epics 1–19 core guarantees**,
so that **all Post-V1 capabilities (Tree-sitter parsers for TS/Go/Java, automated remediation patch generation, and LSP diagnostic server) operate seamlessly across multi-language workflows without regressing core verification pipeline invariants, precision thresholds, or build distribution specs.**

## Acceptance Criteria

1. **E2E Multi-Language Parsing & Defect Detection Integration**:
   - Integration test suite in `tests/test_post_v1_integration.py` exercises `argus.parsers.extended` (`TSParser`, `GoParser`, `JavaParser`) alongside `argus.parsers.base` (`BaseASTParser`) across sample TypeScript/TSX/JS, Go, and Java source snippets containing valid code and vacuous/defect structures.
   - Verifies `ParseResult` generation, AST tree traversal, node summary extraction, and error recovery node identification (`ERROR`/`MISSING`) without process panic or uncaught exceptions.

2. **E2E Automated Defect Remediation & Patch Verification**:
   - Exercises `argus.remediation` (`RemediationEngine`, `RemediationPatch`, `RemediationResult`) against findings/recordings generated across multi-language and Python sources.
   - Verifies unified diff patch generation (replacing vacuous assertions and empty test bodies), `verify_patch_dry_run` in-memory AST validation, and `apply_patch` workspace path containment protection (NFR-S1).

3. **E2E LSP Diagnostic Streaming & Transport Verification**:
   - Exercises `argus.adapters.lsp` (`LSPDiagnosticAdapter`, `LSPDiagnosticServer`) mapping multi-language recordings into standard 0-based LSP range diagnostics and inline severity grades (`ERROR = 1`, `WARNING = 2`, `INFORMATION = 3`, `HINT = 4`).
   - Verifies `JSONRPCNotification` `textDocument/publishDiagnostics` payload serialization, `Content-Length: <len>\r\n\r\n` header framing, and streaming delivery over stdio and socket IO streams without unhandled stream errors.

4. **Cross-Platform & Full Epics 1–19 Regression Verification**:
   - 100% green test execution across Windows and Linux environments (`pytest` exit code 0).
   - Full regression verification confirming zero breaking changes to Epics 1–19 core guarantees: PURE Pydantic contracts (`frozen=True, extra="forbid"`), ledger hash-chain determinism, CLI invocation contracts, exit codes (`0/1/2/3`), and `test_built_distribution.py` package counts (108 modules).

---

## Tasks / Subtasks

- [x] Task 1: Create E2E Integration Test Suite in `tests/test_post_v1_integration.py` (AC: #1, #2, #3, #4)
  - [x] Implement multi-language AST parser integration tests for TypeScript (`.ts`/`.tsx`), Go (`.go`), and Java (`.java`) sources covering clean parsing and error recovery node emission.
  - [x] Implement defect remediation engine integration tests covering `generate_patch`, `verify_patch_dry_run` AST validation, and `apply_patch` POSIX path containment validation.
  - [x] Implement LSP diagnostic adapter and streaming server integration tests covering finding-to-LSP range conversion (1-based to 0-based), document URI generation, JSON-RPC framing, and stdio/socket stream delivery.
  - [x] Implement combined E2E pipeline test: multi-language source file -> AST parse & defect detection -> LSP diagnostic stream publication & remediation patch generation.

- [x] Task 2: Cross-Platform Execution & Full Regression Verification (AC: #4)
  - [x] Execute complete `pytest` test suite on Windows (and Linux CI matrix) ensuring 100% green pass rate (exit code 0).
  - [x] Run `mypy argus/` type checker across all source modules ensuring zero type errors.
  - [x] Verify `tests/test_built_distribution.py` module count assertions (108 modules) and document registries (`tests/test_status_document_registry.py`) pass cleanly.

- [x] Task 3: Document Post-V1 Capabilities & Final Verification Status (AC: #1, #2, #3, #4)
  - [x] Update `CHANGELOG.md` or release notes if required for Post-V1 integration completion.
  - [x] Update `sprint-status.yaml` setting `20-4-post-v1-integration-verification` status to `review` upon completion of code review.

---

## Dev Notes

### Architecture & Technical Stack Requirements
- **Language / Version**: Python `>= 3.10`
- **Dependencies**: Standard library `difflib`, `ast`, `json`, `socket`, `sys`, `typing`, `pydantic >= 2.0`, `tree-sitter >= 0.25.0, < 0.26`, `pytest`, `pytest-asyncio`
- **Contract Integrity**:
  - PURE data models must use `model_config = ConfigDict(frozen=True, extra="forbid")`.
  - All file paths MUST be relative POSIX paths within workspace containment (NFR-S1).
  - No `print()` calls to `stdout` in any `argus` library module.

### Source Tree Components to Touch
- `tests/test_post_v1_integration.py` [NEW]: E2E post-V1 integration and verification test suite.
- `_bmad-output/design-artifacts/ArgusAgent/stories/20-4-post-v1-integration-verification.md` [NEW]: Story file.
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` [UPDATE]: Track story status transition from `backlog` -> `ready-for-dev`.

### Library & Framework Guardrails
- **Tree-sitter Core Ceiling**: `tree-sitter` MUST strictly remain `< 0.26`.
- **LSP 3.17 Specification**: JSON-RPC 2.0 framing format `Content-Length: <len>\r\n\r\n<payload>` over stdio/socket.
- **Pydantic V2**: Enforce immutability and strict schema validation (`frozen=True, extra="forbid"`).

### Project Structure Notes
- Integration test suite lives in `tests/test_post_v1_integration.py` following standard pytest conventions (`test_*.py`).
- Interacts with packages delivered across Epic 20:
  - `argus.parsers.extended` (`TSParser`, `GoParser`, `JavaParser`) & `argus.parsers.base` (`BaseASTParser`, `ParseResult`)
  - `argus.remediation` (`RemediationEngine`, `RemediationPatch`, `RemediationResult`, `verify_patch_dry_run`, `apply_patch`)
  - `argus.adapters.lsp` (`LSPDiagnosticAdapter`, `LSPDiagnosticServer`, `LSPDiagnostic`, `JSONRPCNotification`)

### Previous Story Intelligence
- **Story 20.1 (`TSParser`, `GoParser`, `JavaParser`)**:
  - Tree-sitter parsers use language-specific entry points (`language_typescript`, `language_tsx`, `language_go`, `language_java`).
  - Partial syntax errors emit error recovery nodes (`ERROR` or `MISSING`) in `ParseResult.error_nodes` without process panic.
- **Story 20.2 (`RemediationEngine`)**:
  - `generate_patch` scans prior variable assignments before line index to avoid `NameError` variable reference before declaration.
  - Fallbacks for missing `assigned_var` inspect local state (`assert len(locals()) > 0`, `self.assertTrue(len(locals()) > 0)`).
  - `apply_patch` strictly enforces workspace path containment and POSIX path relative validation.
- **Story 20.3 (`LSPDiagnosticAdapter` & Server)**:
  - Converts 1-based line positions (`start_line`, `end_line`) to 0-based LSP range line positions (`start_line - 1`, `end_line - 1`).
  - Header framing uses `Content-Length: <byte_count>\r\n\r\n<json_string>`.
  - Non-advisory blocking findings map to `ERROR = 1`, advisory deep findings map to `WARNING = 2`, shallow/heuristic findings map to `INFORMATION = 3`.

### Git Intelligence Summary
- Baseline commit for Epic 20: `41f84ef4d06e1250df41c39c80c579d4eeadda69`.
- Recent commits delivered `argus.parsers`, `argus.remediation`, and `argus.adapters.lsp`. Total source modules = 108.

### References
- [Epic 20 Specification](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/epics.md#L3903)
- [Sprint Change Proposal 2026-08-28](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-28.md)
- [PRD Addendum Section A2 - FR38-FR40](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md#L59)
- [Story 20.1 Multi-Language AST Parsers](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/stories/20-1-multi-language-ast-parsers.md)
- [Story 20.2 Defect Remediation Engine](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/stories/20-2-defect-remediation-engine.md)
- [Story 20.3 LSP Diagnostic Adapter](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/stories/20-3-lsp-diagnostic-adapter.md)

---

## Dev Agent Record

### Agent Model Used

Gemini 3.6 Flash (High) / Antigravity

### Debug Log References

None.

### Completion Notes List

- Implemented `tests/test_post_v1_integration.py` containing 14 comprehensive E2E integration unit tests covering:
  - Multi-language AST parsing for TypeScript/TSX/JS, Go, and Java sources with `TSParser`, `GoParser`, and `JavaParser`, validating clean AST creation and graceful error recovery node emission.
  - Defect remediation engine integration covering `generate_patch`, `verify_patch_dry_run` AST validation, and `apply_patch` POSIX path containment validation (NFR-S1).
  - LSP diagnostic adapter and streaming server integration covering line position range conversion (1-based to 0-based), severity mapping (`ERROR`, `WARNING`, `INFORMATION`, `HINT`), `Content-Length: <len>\r\n\r\n` JSON-RPC framing, and transport streaming over stdio text, binary, and socket IO streams.
  - Combined E2E pipeline integration exercise (Multi-language parsing -> defect detection -> LSP notification streaming -> remediation patch generation -> dry-run verification -> workspace path containment patch application).
  - Pure Pydantic data model contract immutability (`frozen=True`) and strict schema validation (`extra="forbid"`).
- Verified full static typing with `mypy argus/ tests/test_post_v1_integration.py` (0 issues across 109 source files).
- Verified distribution packaging assertions in `tests/test_built_distribution.py` (108 modules) and status document registry assertions in `tests/test_status_document_registry.py`.
- Updated `CHANGELOG.md` to document the Post-V1 E2E integration test suite addition.
- Updated `sprint-status.yaml` marking `20-4-post-v1-integration-verification: review`.

### File List

- `tests/test_post_v1_integration.py` [NEW]: E2E Post-V1 integration and verification test suite.
- `tests/test_release_surface_honesty.py` [UPDATE]: Registered Post-V1 changelog section in _NOTE_SECTIONS.
- `CHANGELOG.md` [UPDATE]: Documented Post-V1 E2E Integration & Verification Suite entry.
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` [UPDATE]: Transitioned story status to `review`.
- `_bmad-output/design-artifacts/ArgusAgent/stories/20-4-post-v1-integration-verification.md` [UPDATE]: Updated story status to `review`, checked task items, and filled Dev Agent Record.

### Change Log

- 2026-08-29: Implemented Story 20.4 Post-V1 E2E Integration Suite (`tests/test_post_v1_integration.py`). Updated CHANGELOG.md, sprint-status.yaml, and story status to review.

### Review Findings

#### Review Summary (2026-08-29)
- **Verdict**: PASS (0 issues found)
- **Test Results**: 14/14 integration unit tests passed in `tests/test_post_v1_integration.py`. Full test suite passed 100% green (1,845 passed in 411.51s, exit code 0).
- **Static Analysis**: `mypy argus/` clean over 108 source files.
- **Acceptance Criteria Verification**:
  1. Multi-language AST parsing integration (`TSParser`, `GoParser`, `JavaParser`) verified across clean and error-recovery node paths (`ERROR`/`MISSING`).
  2. Remediation engine patch generation, dry-run AST syntax validation, and POSIX path containment protection (NFR-S1) verified.
  3. LSP diagnostic adapter line range conversion (1-based to 0-based), severity mapping (`ERROR`, `WARNING`, `INFORMATION`, `HINT`), JSON-RPC 2.0 framing, and transport streaming over stdio and socket verified.
  4. Cross-platform regression verification clean; Pydantic V2 pure contracts (`frozen=True`, `extra="forbid"`) and built distribution contracts (108 modules) verified.



