---
baseline_commit: d040cad193a94d1d80e7a787e6098a4d397ea3f4
baseline_note: >-
  `HEAD` = `d040cad` on `master`, **15 commits ahead** of `origin/master`, which is **UNMOVED at
  `00c8d1b`**. `git tag -l` is **EMPTY**. **Nothing has been published.** `sprint-status.yaml` is
  updated to set Story 12-4 to `ready-for-dev`. **No `argus/**`, `tests/**`, `scripts/**` or packaging file is dirty.**
  ✅ **THE SUITE IS FULLY GREEN AND THERE IS NO SANCTIONED RED.** The baseline suite is **1466 passed / 0 failed / 0 error / 0 skipped**.
  ⚠️ **THE EPIC-11 "NO NEW `argus/**` FILE" FENCE IS LIFTED FOR EPIC 12** (§0.1). **Publication is
  still forbidden** (§0.3), **no dogfood artifact may be hand-edited**, and **no test may make a real
  network call**.
  🔴 **THIS STORY OWNS OUTCOME EXPLANATIONS AND THE INGESTION-BOUNDARY DISCLOSURE.**
  Every count, coordinate, LOC figure, verdict and exit code below was produced by
  EXECUTING code on THIS tree on 2026-08-13.
story_key: 12-4-every-outcome-names-its-next-action
epic: 12
---

# Story 12.4: Every outcome names its next action

Status: in-progress

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo.** ArgusAgent (formerly APAA) is a self-contained headless audit
> tool extracted from the Minions monorepo into its own repository (`Agent-Argus`, distribution
> `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo. The
> `minions_core/apaa/` copy in the Minions repo is legacy — no modification, no back-port.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`.
>
> 🔵 **This is the FOURTH story of Epic 12.** 12.1 (`done`) gave `argus/pipeline.py` its headroom;
> 12.2 (`done`) wired the deep pass; 12.3 (`done`) delivered the stage memoization cache (FR27/NFR-D1).
> **This story delivers FR37: every terminal outcome names why it was reached and the next action that changes it, including the three-population ingestion boundary disclosure.** It publishes nothing. The publish is Story **12.9**.

---

## Story

As a developer with no colleague to ask,
I want the tool's own output to tell me why I got this result and what changes it,
So that a verdict is a step forward rather than a dead end.

**Why this is one story.** Every clause is the same subject: *making every terminal outcome self-explaining so an operator knows why a verdict occurred, what specific gate failed, what files were never ingested, and what next action changes the result*.

**What it is NOT.** It introduces **no parallel renderer** (AR7 / §3.3: reuse, never fork). It extends the existing `Next:` and rationale surfaces in `argus/reports/plain_english.py` and `argus/reports/generator.py`. It changes **no FR16 decision-table row, threshold or exit-code mapping** (AC4). And it **publishes nothing**.

---

## Acceptance Criteria

### AC1: Exhaustive Terminal Outcome Next-Action Enumeration (FR37)
- **Given** FR37
- **Then** every terminal outcome — `RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`, and the `AUDIT_FAILED` non-verdict — names **why** it was reached and the **next action** that changes it.
- **Then** this is **enumerated in a dedicated test (`tests/test_outcome_next_action_contract.py`) that fails on an unenumerated outcome** (a registry + closure guard over all 4 terminal outcomes).
- **Then** (REUSE / AR7 constraint): The story extends `argus/reports/plain_english.py:205` (`Next:` line) and `argus/reports/generator.py:236` — no parallel next-action renderer is created.

### AC2: Three-Population Ingestion-Boundary Disclosure
- **Given** any verdict is emitted
- **Then** it names the **ingestion boundary**, explicitly distinguishing three populations by construction:
  1. **Never ingested**: File suffix outside `AUDITABLE_SUFFIXES` (`argus/shared/source_languages.py`), e.g. `.yml`, `.md`, `.toml`.
  2. **Ingested but held out**: Source files with auditable suffixes that were held out or unassessed.
  3. **Assessed**: Source files evaluated for coverage and defects.
- **Then** `deep_ratio` and `held_out` describe only populations 2 and 3; no ratio can disclose population 1 because files never opened are absent from every denominator.
- **Then** the disclosure is **derived dynamically from `AUDITABLE_SUFFIXES`**, never hand-listed, and a test fails if a suffix class present in the repository is absent from the boundary statement.
- **Then** the boundary statement is asserted on `RELEASE_READY` **specifically** (the false-green direction, inversion F1).

### AC3: Specific Unmet Gate Explanation for INSUFFICIENT_COVERAGE
- **Given** `INSUFFICIENT_COVERAGE` is emitted
- **Then** the output names the **specific unmet gate** — minimum floor, ratio, or critical subsystem — with measured figures and the exact next action required to satisfy it.

### AC4: Verdict Decision Table Immutable
- **Given** FR16 governs classification and FR37 governs explanation
- **Then** **no verdict is reworded, upgraded, or hedged.** The decision table in `argus/verdict/verdict_gate.py` is untouched, and a test asserts the verdict enum and decision table mapping remain unchanged by this story.

### AC5: Reflect Real Work (Grounding & Memoization Honesty)
- **Given** Story 12.2's and 12.3's measurements
- **Then** the output reflects **what it actually found** — if a blocking verdict is not reachable on a default run or if deep pass output is recomputed per run and not served from the offline memo store (`DF-12-3-A`), the next-action text does not imply otherwise.

### AC6: Absorbed Ledger & Governance Items
- **`DF-8-3-A`**: Thread `CriticalSubsystemSet.heuristic_excluded_ineligible` into report generation so plain English reports name the vacuous critical subsystem exclusion in prose.
- **`DF-10-4-B`**: Provide a production reader for `DetectorResult.degraded` / recorded grammar degradation causes in the terminal report / next-action output.
- **`DF-11-4-D` / `AI-E11-6`**: Standardize `_NOTE_SECTIONS` impact-rank ordering in `tests/test_release_surface_honesty.py` (`changes_exit_code` > `changes_verdict` > `security_on_executable_surface` > `changes_no_observable`).
- **`DF-12-3-A` disclosure**: Explicitly disclose in report next-action text for deep audit that deep pass results are recomputed per run and not served from the offline memo store.

---

## Developer Context & Guardrails

### Technical Stack & Dependencies
- Python 3.10+ (std-lib `ast`, `pathlib`, `re`, `typing`).
- Core modules modified:
  - `argus/reports/plain_english.py`
  - `argus/reports/generator.py`
  - `argus/shared/source_languages.py` (read `AUDITABLE_SUFFIXES`)
  - `argus/verdict/negative_assurance.py`
- Test files created/modified:
  - `tests/test_outcome_next_action_contract.py` (NEW)
  - `tests/test_release_surface_honesty.py` (UPDATE for `DF-11-4-D`)

### Key Architecture & Design Rules
1. **Reuse, Never Fork (AR7 / §3.3)**: Extend the existing `Next:` and report generation logic in `argus/reports/plain_english.py` and `generator.py`. Do NOT create a duplicate rendering module.
2. **Dynamic Derivation**: Derive non-ingested extensions dynamically from `AUDITABLE_SUFFIXES` vs repository file extensions. Never hardcode file extensions in the ingestion boundary text.
3. **No Blocking Verdict Rewriting**: Keep the FR16 verdict classification engine byte-identical.
4. **File Line Cap (NFR-M1)**: Ensure modified files remain under the 1200-line cap (`pipeline.py` headroom is 193 lines; `plain_english.py` and `generator.py` are well below).
5. **No Real Network Calls**: Tests must use local data/mocks. No external HTTP calls.

---

## Tasks & Subtasks

- [ ] **Task 1: Audit existing report rendering & Next: surface (REUSE baseline)**
  - [ ] Inspect `argus/reports/plain_english.py:205` and `argus/reports/generator.py:236` to map existing outcome explanations.
  - [ ] Document exact current outputs for `RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`, and `AUDIT_FAILED`.

- [ ] **Task 2: Implement Three-Population Ingestion-Boundary Disclosure**
  - [ ] Derive the non-auditable file suffix set by comparing workspace files against `AUDITABLE_SUFFIXES` (`argus/shared/source_languages.py`).
  - [ ] Add the ingestion boundary block to plain English and summary report formats.
  - [ ] Ensure `RELEASE_READY` explicitly includes the ingestion boundary statement.

- [ ] **Task 3: Enhance INSUFFICIENT_COVERAGE Next-Action Explanation**
  - [ ] Identify which specific gate failed (floor breached, deep ratio unmet, or critical subsystem incomplete).
  - [ ] Include measured figures (e.g., current ratio vs required threshold) and specific next action required to satisfy the gate.

- [ ] **Task 4: Integrate Absorbed Ledger Items (DF-8-3-A, DF-10-4-B, DF-12-3-A)**
  - [ ] `DF-8-3-A`: Thread `CriticalSubsystemSet.heuristic_excluded_ineligible` into `generator.py` / `plain_english.py` so vacuous critical subsystem exclusions are named in prose.
  - [ ] `DF-10-4-B`: Read `DetectorResult.degraded` causes and present remediation instructions in terminal output.
  - [ ] `DF-12-3-A`: Disclose in deep audit report text that deep pass results are recomputed per run and not served from the stage memo store.

- [ ] **Task 5: Implement Impact Rank Standardization (DF-11-4-D / AI-E11-6)**
  - [ ] Update `tests/test_release_surface_honesty.py` `_NOTE_SECTIONS` registry to enforce the impact rank order: `changes_exit_code` > `changes_verdict` > `security_on_executable_surface` > `changes_no_observable`.

- [ ] **Task 6: Write Comprehensive Verification Suite**
  - [ ] Create `tests/test_outcome_next_action_contract.py` to assert that all 4 terminal outcomes (`RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`, `AUDIT_FAILED`) have registered, non-empty next actions.
  - [ ] Assert that an unenumerated outcome causes test failure.
  - [ ] Assert `RELEASE_READY` output contains the dynamic ingestion boundary statement.
  - [ ] Assert FR16 decision table and verdict enum remain untouched.

- [ ] **Task 7: Execute Local Verification & Dogfood Currency Check**
  - [ ] Run `python -m pytest` and verify 100% pass rate.
  - [ ] Run `python -m mypy argus` and verify clean type checks.
  - [ ] Run `bandit -r argus` and verify no new security findings.
  - [ ] Run `python scripts/regenerate_dogfood_artifacts.py` if argus files changed to keep dogfood artifacts current.

---

## Dev Agent Record

### Debug Log
- Story created via `bmad-create-story` for Story 12-4 (`12-4-every-outcome-names-its-next-action`).
- Baseline HEAD commit: `d040cad193a94d1d80e7a787e6098a4d397ea3f4`.
- Baseline suite: 1466 passed / 0 failed.

### Completion Notes
- Story file created and status set to `ready-for-dev`.

### File List
- `_bmad-output/design-artifacts/ArgusAgent/stories/12-4-every-outcome-names-its-next-action.md` (NEW)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (UPDATE status to ready-for-dev)
