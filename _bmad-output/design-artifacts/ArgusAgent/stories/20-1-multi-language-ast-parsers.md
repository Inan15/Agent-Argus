---
baseline_commit: 41f84ef4d06e1250df41c39c80c579d4eeadda69
---

# Story 20.1: Multi-Language AST Parsers (`argus.parsers.extended`)

Status: done


<!-- Contexted 2026-08-28 at HEAD `41f84ef4d06e1250df41c39c80c579d4eeadda69` (branch `master`) by the bmad-create-story workflow.

     This story defines the core BaseASTParser abstraction and Tree-sitter AST parser adapters
     for TypeScript/JavaScript, Go, and Java within the `argus.parsers.extended` package.
-->

## Story

As a **Security & Quality Audit Engineer**,
I want **Tree-sitter AST parser adapters for TypeScript/JavaScript, Go, and Java conforming to a unified `BaseASTParser` interface with graceful error recovery**,
so that **ArgusAgent can perform multi-language AST structural analysis and defect detection across polyglot codebases without process panics on malformed or partial code.**

## Acceptance Criteria

1. **`BaseASTParser` Abstract Interface**:
   - `BaseASTParser` abstract base class defined in `argus.parsers.base` with frozen PURE result contracts (`ParseResult`, `ParserErrorNode`, `ASTNodeSummary`).
   - Standard parser methods: `parse_source(code: str | bytes, file_path: str = "") -> ParseResult` and `supports_language(language: str) -> bool`.
   - Thread-safe and stateless parser invocation design.

2. **Parser Implementations (`argus.parsers.extended`)**:
   - `TSParser` handles TypeScript (`.ts`) and TSX (`.tsx`) as well as JavaScript (`.js`, `.jsx`).
   - `GoParser` handles Go source code (`.go`).
   - `JavaParser` handles Java source code (`.java`).
   - All three parsers pass the standard parser test matrix (`test_extended_parsers.py`).

3. **Syntax Error Recovery & Fault Tolerance**:
   - Partial syntax errors emit error recovery nodes (`ERROR` or `MISSING` tree-sitter AST nodes) in `ParseResult.error_nodes`.
   - Parsing never panics, crashes, or raises uncaught exceptions on syntactically invalid input.
   - `ParseResult.has_errors` correctly signals partial syntax errors while returning the partially constructed AST node hierarchy.

4. **Integration with Tree-sitter Toolchain & Invariants**:
   - Respects `tree-sitter` core version bounds (`>= 0.25.0, < 0.26`) and `argus.shared.grammar_status` canary validations.
   - Preserves all project context rules (frozen PURE contracts, typed error handling, zero stdout pollution).

---

## Tasks / Subtasks

- [x] Task 1: Define `BaseASTParser` and PURE data contracts in `argus/parsers/base.py` (AC: #1, #3)
  - [x] Implement `ParserErrorNode` (frozen BaseModel: `line`, `column`, `node_type`, `unexpected_text`).
  - [x] Implement `ASTNodeSummary` (frozen BaseModel: `type`, `start_line`, `end_line`, `start_col`, `end_col`, `children_count`).
  - [x] Implement `ParseResult` (frozen BaseModel: `file_path`, `language`, `ast_eligible`, `has_errors`, `root_node`, `error_nodes`, `definitions`, `edges`).
  - [x] Implement `BaseASTParser` ABC with abstract method `parse_source(code: str | bytes, file_path: str = "") -> ParseResult`.

- [x] Task 2: Implement `TSParser`, `GoParser`, and `JavaParser` in `argus/parsers/extended.py` (AC: #2, #3, #4)
  - [x] Implement `TSParser` with dynamic dialect selection (`language_typescript` vs `language_tsx`).
  - [x] Implement `GoParser` wrapping `tree-sitter-go`.
  - [x] Implement `JavaParser` wrapping `tree-sitter-java`.
  - [x] Implement Tree-sitter AST traversal in each parser to extract definitions, edges, and error nodes (`ERROR` / `MISSING`).

- [x] Task 3: Expose `argus.parsers` package exports in `argus/parsers/__init__.py` (AC: #1, #2)
  - [x] Export `BaseASTParser`, `ParseResult`, `ParserErrorNode`, `ASTNodeSummary`, `TSParser`, `GoParser`, `JavaParser`.

- [x] Task 4: Comprehensive Test Matrix in `tests/test_extended_parsers.py` (AC: #1, #2, #3, #4)
  - [x] Test clean parsing of valid TypeScript, TSX, JS, Go, and Java source snippets.
  - [x] Test partial syntax error recovery for invalid syntax across all three parsers without panic.
  - [x] Test `BaseASTParser` contract compliance and PURE data model immutability.
  - [x] Test tree-sitter core version compatibility and canary alignment.

---

## Dev Notes

### Architecture & Technical Stack Requirements
- **Language / Version**: Python `>= 3.10`
- **Dependencies**: `tree-sitter >= 0.25.0, < 0.26`, `pydantic >= 2.0`
- **Contract Integrity**:
  - PURE data models must use `model_config = ConfigDict(frozen=True, extra="forbid")`.
  - All paths must be relative POSIX paths (NFR-S1).
  - No `print()` calls to `stdout` in any `argus` module.

### Source Tree Components to Touch
- `argus/parsers/__init__.py` [NEW]: Package exports.
- `argus/parsers/base.py` [NEW]: Base class `BaseASTParser` & PURE contracts (`ParseResult`, `ParserErrorNode`, `ASTNodeSummary`).
- `argus/parsers/extended.py` [NEW]: `TSParser`, `GoParser`, `JavaParser` implementations.
- `tests/test_extended_parsers.py` [NEW]: Standard parser test matrix and error recovery unit tests.

### Library & Framework Guardrails
- **Tree-sitter Core Ceiling**: `tree-sitter` MUST strictly remain `< 0.26`.
- **Grammar Entry Points**:
  - `tree-sitter-typescript` uses `language_typescript` for `.ts`/`.js` and `language_tsx` for `.tsx`/`.jsx`.
  - `tree-sitter-go` uses `language`.
  - `tree-sitter-java` uses `language`.
- **Canary Compatibility**: Parsers must align with `argus.shared.grammar_status.CANARY_BY_ENTRY_POINT`.

### References
- [Epic 20 Specification](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/epics.md#L3903)
- [Sprint Change Proposal 2026-08-28](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-28.md)
- [PRD Addendum Section A2](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md#L59)
- [Grammar Status Module](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/argus/shared/grammar_status.py)
- [AST Index Module](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/argus/index/ast_index.py)

---

## Dev Agent Record

### Agent Model Used
Gemini 3.6 Flash (High) / Antigravity

### Debug Log References

### Completion Notes List
- Implemented `ParserErrorNode`, `ASTNodeSummary`, `ParseResult` frozen PURE data models (`extra="forbid"`) in `argus/parsers/base.py`.
- Defined `BaseASTParser` abstract base class with `parse_source` and `supports_language` methods.
- Implemented `TSParser`, `GoParser`, and `JavaParser` in `argus/parsers/extended.py` with tree-sitter AST traversal and graceful error recovery.
- Exported all models and parser adapters in `argus/parsers/__init__.py`.
- Added unit tests in `tests/test_extended_parsers.py` (5/5 passed cleanly).
- Verified mypy clean over 99 source files.

### File List
- `argus/parsers/__init__.py`
- `argus/parsers/base.py`
- `argus/parsers/extended.py`
- `tests/test_extended_parsers.py`

### Review Findings
- **Adversarial Code Review**: Clean review — all review layers passed (Blind Hunter, Edge Case Hunter, Acceptance Auditor).
- **Verification**:
  - `python -m pytest tests/test_extended_parsers.py` (6 passed in 0.12s)
  - `python -m mypy argus/parsers/ tests/test_extended_parsers.py` (clean, 4 source files verified)
- **Canary Alignment**: `TSParser`, `GoParser`, and `JavaParser` tested and aligned with `argus.shared.grammar_status.CANARY_BY_ENTRY_POINT`.
- **Version Compatibility**: Verified tree-sitter core version bounds (`>= 0.25.0, < 0.26`).

