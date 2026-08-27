---
project_name: 'ArgusAgent'
user_name: 'User'
date: '2026-08-27'
sections_completed: ['technology_stack', 'language_rules', 'mcp_rules', 'testing_rules', 'edge_case_rules', 'anti_patterns']
status: 'complete'
rule_count: 14
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

- **Python**: `>= 3.10`
- **Build Backend**: `flit_core >= 3.2, < 4` (uses `flit_core.buildapi`)
- **Core Dependencies**:
  - `pydantic >= 2.0`
  - `jsonschema >= 4.0`
  - `radon >= 4.1.0`
  - `httpx >= 0.24.0`
  - `tree-sitter >= 0.25.0, < 0.26` *(Strict `<0.26` upper ceiling bound per NFR-P3 and Story 12.5)*
  - Grammars: `tree-sitter-python`, `javascript`, `typescript`, `go`, `rust`, `java`, `c`, `cpp`, `ruby`, `php` (all `>= 0.23.0/0.25.0, < 0.26`)
- **Development & Test Tooling**:
  - `pytest >= 7.0`, `pytest-asyncio`, `pytest-cov`
  - `mypy >= 1.0`
  - `build >= 1.0`, `flit_core >= 3.2, < 4`
- **Optional Dependencies**:
  - `litellm >= 1.0.0`
- **Console Entrypoints**:
  - `argus`, `argus-agent`, `repo-audit` -> `argus.cli:main`
  - `argus-mcp` -> `argus.mcp.server:main` (stdio JSON-RPC, stdlib-only)

---

## Critical Implementation Rules

### Architectural & Language Rules
- **Mechanical Honesty & Coverage Grounding**: Verdicts (`AuditVerdict`) are pure functions of `audited_deep` evidence in the coverage ledger. Never claim code correctness; only state coverage-grounded release readiness.
- **Schema & Verdict Integrity**: Any change to `AuditRequest`, `AuditVerdict`, or evidence models MUST update JSON schemas and pass `tests/test_verdict_schema_bump.py`.
- **Evidence & History Immutability**: Retain prior architectural corrections and strikethroughs (e.g. `~~struck statement~~`) in code comments and docstrings per evidence immutability rules.
- **Headless & Deterministic Execution**: Output state must be written to `.argus/` or specified output paths. Execution must be deterministic and headless with discrete exit codes.

### MCP & Isolation Rules
- **Stdlib-Only MCP Server**: `argus-mcp` MUST NOT import `mcp` SDK, `starlette`, or `uvicorn` (ADR #20 requirement). All JSON-RPC parsing must use `sys.stdin`/`sys.stdout` and Python standard library only.
- **Stdio Stream Hygiene in MCP**: `stdout` is strictly reserved for JSON-RPC protocol frames in `argus.mcp`. Never use `print()` or write logs to `stdout`; redirect all logging and debug output to `sys.stderr` or `.argus/`.
- **No-Network Test Isolation**: Test suite builds must be executable with `--no-isolation` without reaching out to external networks.

### Testing & Grammar Rules
- **Built Distribution Testing**: Any packaging changes must pass `tests/test_built_distribution.py` under `--no-isolation`.
- **Grammar Runtime Validation**: Changes touching `tree-sitter` grammars must validate against `argus/shared/grammar_status.py` and pass `tests/test_grammar_runtime_validation.py`.

### Boundary & Edge Case Mitigations
- **AST Extraction Failure Graceful Degradation**: When AST extraction fails or a grammar parser is absent, depth degrades to shallow enumeration, tripping `INSUFFICIENT_COVERAGE` (exit code 3). NEVER fallback to `RELEASE_READY`.
- **Runtime Toolchain Canaries**: Do not rely solely on package metadata bounds. Use `ast_index.py` runtime behavioral canary checks to verify tree-sitter parser capabilities before parsing.

### Critical Don't-Miss Anti-Patterns
- **Do NOT bump tree-sitter beyond `< 0.26`** without updating `grammar_status.SUPPORTED_CORE_RANGE` and explicit verification.
- **Do NOT bypass `GRAMMAR_PACKAGE_BY_LANGUAGE`** or `grammar_status.py` checks when registering new language parsers.
- **Do NOT print to `stdout` in `argus.mcp`** modules.

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code in ArgusAgent.
- Follow ALL rules exactly as documented.
- When in doubt, prefer the more restrictive option.

**For Humans:**
- Keep this file lean and focused on agent needs.
- Update when technology stack or core ADR constraints change.

Last Updated: 2026-08-27
