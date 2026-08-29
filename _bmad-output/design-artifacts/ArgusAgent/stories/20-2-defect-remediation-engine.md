---
baseline_commit: 41f84ef4d06e1250df41c39c80c579d4eeadda69
---

# Story 20.2: Defect Remediation Engine (`argus.remediation`)

Status: done

<!-- Contexted 2026-08-29 at HEAD `41f84ef4d06e1250df41c39c80c579d4eeadda69` (branch `master`) by the bmad-create-story workflow.

     This story implements the automated defect remediation engine (`argus.remediation`) for ArgusAgent,
     generating actionable unified diff patches (.patch) for detected vacuous test and assertion defects
     without altering test contract semantics, with dry-run verification capabilities.
-->

## Story

As a **Security & Quality Audit Engineer**,
I want **an automated defect remediation engine (`argus.remediation`) that generates unified diff patches (`.patch`) for detected vacuous test and assertion defects with dry-run semantic verification**,
so that **developers and autonomous agents can remediate identified vacuous assertions and test quality defects across codebases without breaking existing test contract semantics.**

## Acceptance Criteria

1. **Remediation Patch Data Models & Interface Contracts (`argus.remediation.models`)**:
   - `RemediationPatch` frozen PURE Pydantic model (`frozen=True, extra="forbid"`): `finding_id`, `target_file`, `diff_content`, `affected_lines`, `patch_id`, `created_at`.
   - `RemediationResult` frozen PURE Pydantic model (`frozen=True, extra="forbid"`): `patches`, `success`, `dry_run_verified`, `applied_count`, `errors`.
   - All file paths MUST be relative POSIX paths within workspace containment (NFR-S1).

2. **Remediation Patch Generator (`argus.remediation.engine`)**:
   - Implements `RemediationEngine` capable of transforming vacuous assertions (e.g. `assert True`, `assert 1 == 1`, missing assertions, empty test function bodies) into concrete, non-vacuous assertions and test calls.
   - Generates valid unified diff patch strings matching target source files and line ranges.
   - Preserves original test names, test scope, and test contract semantics.

3. **Dry-Run Verification & Containment (`verify_patch_dry_run` & `apply_patch`)**:
   - `verify_patch_dry_run(source_content: str, patch: RemediationPatch) -> bool`: Dry-run applies patch in memory and validates AST syntax using tree-sitter or stdlib AST parser without modifying disk files.
   - `apply_patch(target_file_path: str, patch: RemediationPatch, workspace_root: str = ".") -> bool`: Safely writes patch to target file ensuring path containment (NFR-S1).
   - Gracefully rejects invalid patches or malformed diffs with recorded error messages without process panic or exceptions.

4. **Package Integration & Verification**:
   - Exported through `argus.remediation` (`RemediationEngine`, `RemediationPatch`, `RemediationResult`).
   - 100% green unit & dry-run test suite (`tests/test_defect_remediation.py`).
   - Preserves all V1 invariants (pure models, zero stdout pollution, typed error handling).

---

## Tasks / Subtasks

- [x] Task 1: Define `RemediationPatch` and `RemediationResult` PURE data contracts in `argus/remediation/models.py` (AC: #1)
  - [x] Implement `RemediationPatch` (frozen BaseModel: `finding_id`, `target_file`, `diff_content`, `affected_lines`, `patch_id`, `created_at`).
  - [x] Implement `RemediationResult` (frozen BaseModel: `patches`, `success`, `dry_run_verified`, `applied_count`, `errors`).
  - [x] Enforce relative POSIX path validation on `target_file` (NFR-S1).

- [x] Task 2: Implement `RemediationEngine` diff generator in `argus/remediation/engine.py` (AC: #2, #3)
  - [x] Implement `generate_patch(recording: Recording, source_code: str) -> RemediationPatch | None`.
  - [x] Implement vacuous pattern patch transformers (replacing `assert True`, `assert 1 == 1`, empty test `pass` bodies with target assertions).
  - [x] Implement unified diff formatting via `difflib.unified_diff` generating valid `.patch` diff format.
  - [x] Implement `verify_patch_dry_run(source_content: str, patch: RemediationPatch) -> bool` for in-memory AST syntax validation.
  - [x] Implement `apply_patch(target_file_path: str, patch: RemediationPatch, workspace_root: str = ".") -> bool` with path containment checks.

- [x] Task 3: Expose `argus.remediation` package exports in `argus/remediation/__init__.py` (AC: #1, #2, #4)
  - [x] Export `RemediationEngine`, `RemediationPatch`, `RemediationResult`.

- [x] Task 4: Comprehensive Test Suite in `tests/test_defect_remediation.py` (AC: #1, #2, #3, #4)
  - [x] Test diff generation for vacuous test and assertion finding recordings.
  - [x] Test dry-run verification logic against valid and invalid patch outputs.
  - [x] Test patch application and workspace path containment protection.
  - [x] Test PURE data model immutability (`frozen=True, extra="forbid"`).

---

## Dev Notes

### Architecture & Technical Stack Requirements
- **Language / Version**: Python `>= 3.10`
- **Dependencies**: Standard library `difflib`, `ast`, `pydantic >= 2.0`
- **Contract Integrity**:
  - PURE data models must use `model_config = ConfigDict(frozen=True, extra="forbid")`.
  - All paths must be relative POSIX paths within workspace containment (NFR-S1).
  - No `print()` calls to `stdout` in any `argus` module.

### Source Tree Components to Touch
- `argus/remediation/__init__.py` [NEW]: Package exports (`RemediationEngine`, `RemediationPatch`, `RemediationResult`).
- `argus/remediation/models.py` [NEW]: PURE data contracts (`RemediationPatch`, `RemediationResult`).
- `argus/remediation/engine.py` [NEW]: `RemediationEngine` patch generator, dry-run verification, and patch application logic.
- `tests/test_defect_remediation.py` [NEW]: Comprehensive test suite.

### Project Structure Notes
- Module lives under `argus/remediation/`, adhering to project package layout.
- Integrates with findings emitted by `argus.ledger.recording.Recording` and `argus.detectors.base.DetectorResult`.

### References
- [Epic 20 Specification](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/epics.md#L3914)
- [PRD Addendum Section A2 - FR38](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md#L64)
- [Sprint Change Proposal 2026-08-28](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-28.md#L47)
- [Recording Ledger Model](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/argus/ledger/recording.py#L91)
- [Detector Base Models](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/argus/detectors/base.py#L125)

---

## Dev Agent Record

### Agent Model Used
Gemini 3.6 Flash (High) / Antigravity

### Debug Log References
- `pytest tests/test_defect_remediation.py tests/test_remediation_engine.py` (32 passed)
- `pytest tests/test_built_distribution.py` (9 passed)
- `mypy argus/remediation/` (Success: no issues found in 4 source files)
- `mypy argus/` (Success: no issues found in 103 source files)

### Completion Notes List
- Defined `RemediationPatch` and `RemediationResult` frozen PURE Pydantic models with relative POSIX path containment validation.
- Implemented `RemediationEngine` diff generator for vacuous assertions, empty test function bodies, and missing assertions using `difflib.unified_diff`.
- Implemented `verify_patch_dry_run` for in-memory AST syntax validation.
- Implemented `apply_patch` with strict workspace path containment protection.
- Exported package interface in `argus.remediation`.
- Added comprehensive unit and integration tests covering data models, patch generation, dry-run verification, containment, and batch processing.
- Fixed Review Findings (Iteration 1 Fix Round):
  - Medium 1: Updated `generate_patch` to scan for variable assignments occurring prior to the current remediated line index (`_find_prior_assigned_var`), eliminating variable reference before declaration (`NameError`).
  - Medium 2: Updated fallbacks when `assigned_var` is `None` to generate non-vacuous assertions (`assert len(locals()) > 0`, `self.assertTrue(len(locals()) > 0)`, `self.assertIsNotNone(locals())`) rather than circular `True` checks.
  - Low 1: Preserved assertion failure message arguments and trailing inline comments (`_extract_comment`) when replacing vacuous assertion lines.
  - Low 2: Updated module count figures from 96 to 103 and wheel/sdist entry counts in `README.md` and `CHANGELOG.md` to match live distribution measurements in `test_built_distribution.py`.

### File List
- `argus/remediation/__init__.py`
- `argus/remediation/base.py`
- `argus/remediation/models.py`
- `argus/remediation/engine.py`
- `tests/test_defect_remediation.py`
- `tests/test_remediation_engine.py`
- `README.md`
- `CHANGELOG.md`
- `sprint-status.yaml`
- `_bmad-output/design-artifacts/ArgusAgent/stories/20-2-defect-remediation-engine.md`

### Review Findings
- **Adversarial Code Review Iteration 1**: Verdict: **CONCERNS** (2 Medium, 2 Low findings logged).
- **Findings**:
  1. **[Medium - Bug] Variable reference before declaration in `generate_patch`**: `assigned_var` is pre-scanned across the entire span prior to transformation. If a vacuous assertion (`assert True`) or `pass` precedes an assignment in the locator span, `assigned_var` is referenced on a line before its declaration, generating broken test code (`NameError` at runtime). Fix: only match assignments occurring *before* the current line index being remediated.
  2. **[Medium - AC2 Violation] Fallback remediation produces vacuous/circular assertions**: When `assigned_var` is `None`, fallbacks generate `result = True\nassert result is True`, `self.assertTrue(True)  # remediated`, `self.assertEqual(1, 1)  # remediated`, or `assert True is not False`. These remain vacuous assertions, violating AC2 ("transforming vacuous assertions into concrete, non-vacuous assertions and test calls"). Fix: generate meaningful default assertions or call-based assertions rather than circular `True` checks.
  3. **[Low - Code Quality] Failure message / comment truncation**: Replacing full lines with `assert {assigned_var} is not None` discards custom assertion failure messages (e.g. `assert True, "message"`).
  4. **[Low - Integration] Stale figures in `test_built_distribution.py`**: Adding package modules increased importable module count from 96 to 103, causing `test_TC_ArgusAgent_DOCS_001_54` assertions to fail.
- **Verification**:
  - `pytest tests/test_defect_remediation.py tests/test_remediation_engine.py tests/test_built_distribution.py` (41 passed)
  - `mypy argus/` (Success: no issues found in 108 source files)
  - **Fix Round 1 (2026-08-29)**: Resolved all 4 review findings (2 Medium, 2 Low). All remediation and distribution tests pass cleanly.
- **Adversarial Code Review Iteration 2 (2026-08-29)**: Verdict: **PASS**.
  - Verified all 4 prior review findings (2 Medium, 2 Low) are fully resolved.
  - Verified prior assignment line check prevents `NameError` variable reference before declaration.
  - Verified non-vacuous fallbacks inspect local state (`assert len(locals()) > 0`, `self.assertTrue(len(locals()) > 0)`, `self.assertIsNotNone(locals())`).
  - Verified assertion failure messages and inline trailing comments are preserved.
  - Verified package module count updated to 103 across docs and distribution test suite.
  - All tests passing (43 passed across defect remediation, engine, distribution, and document registry tests; `mypy argus/` clean over 103 files).
- **Checkpoint Re-Validation (2026-08-29, `bmad-checkpoint-preview`)**: Verdict: **iteration 2's closure of Medium #2 was WRONG, and is reopened and re-fixed.**
  - **What iteration 2 accepted:** "non-vacuous fallbacks inspect local state (`assert len(locals()) > 0`, `self.assertTrue(len(locals()) > 0)`, `self.assertIsNotNone(locals())`)".
  - **What was MEASURED at checkpoint:** `len(locals()) > 0` is `True` in any scope holding a local and `False` in one holding none. It never constrains the code under test, so it is not "non-vacuous" in AC2's sense. Worse, in **both** cases the suite pinned — `test_remediate_empty_pass_body` and `test_remediate_vacuous_assert_before_assignment` — the patched scope holds **no** locals at the assertion point, so the emitted predicate is `False` and the proposal **converts a PASSING vacuous test into a FAILING one**. Executed, not inferred: both patched sources raise `AssertionError`.
  - **Why no guard caught it:** `verify_patch_dry_run` validates AST **syntax** only. A syntactically valid, semantically broken patch passes it, and the two unit tests asserted the emitted **string** rather than the behaviour of the patched test.
  - **Fix (2026-08-29):** all five fallback sites in `argus/remediation/engine.py` now **decline** when `_find_prior_assigned_var` returns `None` — `generate_patch` returns `None` and `process_recordings` records a miss. AR10 honest degradation: propose nothing rather than fabricate an assertion. `tests/test_defect_remediation.py` gains `test_declines_when_the_span_has_no_assertable_state` pinning both shapes, and the two string-pinning tests were rewritten to exercise the assignment-ordering guard that Medium #1 installed.
  - **AC2 tension, stated rather than buried:** AC2 enumerates "empty test function bodies" among the shapes to transform. An empty body with no assignable state offers nothing to assert on, so the enumeration and AC2's binding requirement ("into concrete, non-vacuous assertions") cannot both be met. The binding requirement wins; the enumeration is met whenever the span carries any prior assignment. **This is a live decision for the Governance Owner, not a closed one.**
  - **Verification**: `pytest tests/test_defect_remediation.py tests/test_remediation_engine.py` (34 passed), `pytest tests/test_post_v1_integration.py tests/test_extended_parsers.py tests/test_lsp_adapter.py` (32 passed).

