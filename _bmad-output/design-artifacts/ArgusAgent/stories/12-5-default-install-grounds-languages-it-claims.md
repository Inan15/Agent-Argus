# Story 12.5: The default install grounds the languages it claims

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo.** ArgusAgent (formerly APAA) is a self-contained headless audit
> tool extracted from the Minions monorepo into its own repository (`Agent-Argus`, distribution
> `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`.
>
> 🔵 **This is the FIFTH story of Epic 12.** 12.1 (`done`) gave `argus/pipeline.py` its headroom;
> 12.2 (`done`) wired the deep pass; 12.3 (`done`) delivered the stage memoization cache (FR27/NFR-D1);
> 12.4 (`review`) delivered FR37 outcome explanations and ingestion boundary disclosures.
> **This story delivers NFR-P3: promoting the 9 multi-language tree-sitter grammars to default dependencies (or explicitly reconciling packaging and output disclosures so a missing grammar states its reason at the point of downgrade).** It publishes nothing until Story **12.9**.

---

## Story

As a developer whose project is not Python,
I want the public install to work on my stack out of the box,
So that I am not silently given a worse result because of a packaging choice.

**Why this is one story.** Every clause addresses **NFR-P3**: *ensuring the default public installation grounds the languages the tool claims to support without requiring a user to discover an optional extra, and stating the absence and reason in the tool's own output whenever a language grammar is uninstalled or downgraded*.

**What it is NOT.** It introduces no new parsing engine or new language grammars beyond the 10 auditable source languages (`Python`, `JavaScript`, `TypeScript`, `Go`, `Rust`, `Java`, `C`, `C++`, `Ruby`, `PHP`). It does NOT alter the AST index canary validation engine (`argus/shared/grammar_status.py`, `argus/index/ast_index.py`). And it **publishes nothing**.

---

## Acceptance Criteria

### AC1: Default Package Dependencies Include All 10 Supported Language Grammars (NFR-P3)
- **Given** NFR-P3 classifies coverage degraded by a grammar absent from the default install as a packaging defect
- **When** `argus-agent` is installed via its primary public install command (`pip install argus-agent`)
- **Then** `pyproject.toml` promotes the 9 non-Python language grammars (`tree-sitter-javascript`, `tree-sitter-typescript`, `tree-sitter-go`, `tree-sitter-rust`, `tree-sitter-java`, `tree-sitter-c`, `tree-sitter-cpp`, `tree-sitter-ruby`, `tree-sitter-php`) from optional dependencies (`[project.optional-dependencies] languages`) into core dependencies (`[project.dependencies]`).
- **Then** installing `argus-agent` without extras grounds all 10 supported source languages out of the box.

### AC2: Explicit Downgrade Reason Reporting in Tool Output
- **Given** a environment where a language grammar is uninstalled or deliberately missing
- **Then** its absence and the exact remediation reason appear **in the tool's own output at the point the file is downgraded** (`audited_shallow`), including the specific missing grammar package name (e.g. `tree-sitter-go`) and the `pip install` command required to restore deep grounding.
- **Then** the terminal report and plain English summary state the specific missing grammar package per missing language class.

### AC3: Reconcile Documentation & CI Environment Guards
- **Given** Story 10.2 documented `[languages]` extra and `audit-ci.yml` sets `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`
- **Then** `README.md`, `CHANGELOG.md`, `architecture.md`, and `pyproject.toml` are reconciled so the documentation and package metadata describe the same default grounding behavior.
- **Then** `[project.optional-dependencies] languages` is retained as an alias or documented backward-compatibility extra so existing `pip install "argus-agent[languages]"` commands continue to work without error.

### AC4: Verification Suite & NFR-M1 Compliance
- **Given** changes to `pyproject.toml`, `README.md`, `CHANGELOG.md`, and report output
- **Then** tests in `tests/test_grammar_runtime_validation.py` and `tests/test_release_surface_honesty.py` are updated to assert that all 10 language grammars are declared in core dependencies and that downgrade explanations state exact remedies.
- **Then** all files remain strictly under the NFR-M1 1200-line cap.

---

## Developer Context & Guardrails

### Technical Stack & Dependencies
- Python 3.10+ (std-lib `ast`, `pathlib`, `typing`).
- Core files modified:
  - `pyproject.toml` (promote 9 grammars from `optional-dependencies.languages` to `dependencies`)
  - `argus/reports/plain_english.py` / `argus/reports/generator.py`
  - `README.md`, `CHANGELOG.md`, `architecture.md`
- Test files modified:
  - `tests/test_grammar_runtime_validation.py`
  - `tests/test_release_surface_honesty.py`

### Key Architecture & Design Rules
1. **Packaging Precision (NFR-P3)**: All 10 supported language grammars are part of the base `dependencies` in `pyproject.toml`.
2. **Backward Compatibility**: Keep `languages` in `[project.optional-dependencies]` pointing to the grammars (or empty alias) so `pip install ".[languages]"` does not fail.
3. **No Network Calls in Tests**: All tests must run offline with local mocks/canaries.
4. **File Line Cap (NFR-M1)**: Ensure all modified files remain under the 1200-line limit.

---

## Tasks & Subtasks

- [ ] **Task 1: Promote Language Grammars in `pyproject.toml`**
  - [ ] Move the 9 tree-sitter grammar dependencies (`tree-sitter-javascript`, `tree-sitter-typescript`, `tree-sitter-go`, `tree-sitter-rust`, `tree-sitter-java`, `tree-sitter-c`, `tree-sitter-cpp`, `tree-sitter-ruby`, `tree-sitter-php`) into `[project.dependencies]`.
  - [ ] Retain `[project.optional-dependencies] languages` for backward compatibility.

- [ ] **Task 2: Enhance Downgrade Explanation in Plain English & Summary Reports**
  - [ ] Audit `_render_grammar_remedy` in `argus/reports/generator.py` and `plain_english.py`.
  - [ ] Verify that when any grammar is missing or unvalidated, the tool output explicitly names the missing package and exact `pip install` command at the point of file downgrade (`audited_shallow`).

- [ ] **Task 3: Reconcile Documentation & Surface Registration**
  - [ ] Update `README.md`, `CHANGELOG.md`, and `architecture.md` to reflect that all 10 supported source languages are grounded by default in `argus-agent`.
  - [ ] Register the new release note section in `tests/test_release_surface_honesty.py` `_NOTE_SECTIONS`.

- [ ] **Task 4: Execute Verification Gates & Dogfood Currency Check**
  - [ ] Run `python -m pytest` and verify 100% pass rate across the full test suite.
  - [ ] Run `python -m mypy argus` and verify clean static typing.
  - [ ] Run `bandit -r argus` and verify no new security findings.
  - [ ] Run `python scripts/regenerate_dogfood_artifacts.py` if `argus/` files changed to keep dogfood artifacts current.

---

## Dev Agent Record

### Debug Log
- Story created via `bmad-create-story` for Story 12-5 (`12-5-default-install-grounds-languages-it-claims`).
- Baseline HEAD commit: `2821301`.

### Completion Notes
- Story file created and status set to `ready-for-dev`.

### File List
- `_bmad-output/design-artifacts/ArgusAgent/stories/12-5-default-install-grounds-languages-it-claims.md` (NEW)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (UPDATE: 12-5 status set to ready-for-dev)
