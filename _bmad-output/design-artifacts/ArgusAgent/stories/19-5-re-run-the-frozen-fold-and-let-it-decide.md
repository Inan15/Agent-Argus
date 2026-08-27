---
baseline_commit: cdd339c
---

# Story 19.5: Re-run the frozen fold and let it decide

Status: done

<!-- Contexted 2026-08-27 at HEAD `cdd339c` (branch `docs/merge-strategy-decision`) by the
     create-story workflow (Gemini 3.6 Flash / Antigravity).

     EVERY FIGURE IN §0 WAS READ OFF THIS TREE BY EXECUTION at `cdd339c`, not copied from
     `epics.md` or `sprint-change-proposal-2026-08-26.md`.

     THE CORE INVARIANTS FOR THIS STORY:
       (1) The pre-registration criterion committed in `scripts/precision_preregistration.py`
           MUST NOT be re-frozen, re-derived, or re-typed.
       (2) `evaluate()` MUST be imported directly from `scripts.precision_preregistration`,
           fulfilling the `AI-E17-5` / `AR7` one-derivation obligation, with the search recorded in
           the Dev Agent Record.
       (3) `CRITERION_OUTCOMES` is closed at three (`MET`, `NOT_MET`, `UNEVALUABLE`).
       (4) The outcome is recorded WHATEVER IT IS (`MET`, `NOT_MET`, or `UNEVALUABLE`), with the
           counts and exact Fractions that produced it, and no threshold moves in either direction.
       (5) `DF-13-5-A`'s stopping rule is honored: this story evaluates the criterion against the
           current record and records the result honestly — it does NOT force a re-plan or fake gate clearance.
       (6) Stage by explicit path; NEVER `git add -A`. -->

## Story

As an **Engineering Lead**,
I want **the pre-registered criterion evaluated once more against the record as it then stands**,
so that **the outcome is the criterion's and not the story's.**

### What this story IS

The execution of the **frozen precision fold** (`evaluate()`) against the live adjudication record (`validation-corpus/adjudication-record.json`) and corpus manifest.

Its deliverable is:
1. An **imported execution** of `evaluate()` from `scripts/precision_preregistration.py`;
2. An **honest, un-forced recording** of the evaluation outcome (`MET`, `NOT_MET`, or `UNEVALUABLE`) with all underlying metric details (counts, Fraction values, denominators);
3. **AST structural guard & test coverage** (`TC-ArgusAgent-PRECISION-001-155`) verifying one-derivation compliance (`AI-E17-5` / `AR7`) and deterministic replay.

### What it is NOT

- ⛔ **NOT a re-implementation of the fold.** Must import `evaluate` from `scripts.precision_preregistration`.
- ⛔ **NOT a threshold or gate modification.** Thresholds stay frozen (`Fraction(4, 5)` = 80%).
- ⛔ **NOT a forced outcome.** If `UNEVALUABLE` or `NOT_MET` is returned, that result is recorded as-is without altering protocol rules or criteria definitions.
- ⛔ **NOT a network fetch.** No network calls or third-party fetching are performed (protocol §6 R2).

---

## §0 — PREMISES MEASURED BY EXECUTION at HEAD `cdd339c`

⛔ **Task 0 re-measures every row of this section before a line is written.** Per `AI-E17-11`, **"a row moved" is a first-class outcome that is REPORTED, not absorbed.**

### §0.0 The tree, the paths, the baseline

| fact | value |
|---|---|
| HEAD | `cdd339c` |
| branch | `docs/merge-strategy-decision`, **8 ahead** of `origin/docs/merge-strategy-decision` |
| working tree | clean or explicit story files |
| local suite | **1,779 tests, exit 0**, Windows only |

### §0.1 The pre-registration module & fold function

`scripts/precision_preregistration.py`:
- `evaluate(record_path=..., manifest_module=...) -> CriterionEvaluationResult`
- `CRITERION_OUTCOMES = ("MET", "NOT_MET", "UNEVALUABLE")`
- `PRECISION_GATE_THRESHOLD = Fraction(4, 5)`

⛔ **This function must be imported, never re-implemented (`AI-E17-5`).**

### §0.2 Next free test IDs

| family | max in tree | next free |
|---|---:|---|
| `TC-ArgusAgent-PRECISION-001-*` | 154 | **155** |
| `TC-ArgusAgent-DOCS-001-*` | 80 | **81** |

### §0.3 Byte invariants

| file | CRLF | lone LF | lone CR |
|---|---:|---:|---:|
| `deferred-work.md` | **0** | **8,225** | **1** — at line **5569** |
| `sprint-status.yaml` | 1,403 | 0 | 0 |

---

## §1 — Acceptance Criteria

### AC1: One-Derivation & Import Compliance

**Given** `scripts/precision_preregistration.py` defines `evaluate()`, `CRITERION_OUTCOMES`, and `PRECISION_GATE_THRESHOLD`
**Then** `evaluate()` is imported directly (honoring `AR7` / `AI-E17-5`), no duplicate evaluation or fold logic is written under `argus/` or `tests/`, and AST analysis confirms no re-derivation or literal threshold duplication.

### AC2: Honest Outcome Recording

**Given** `CRITERION_OUTCOMES` is closed at `("MET", "NOT_MET", "UNEVALUABLE")`
**Then** the outcome returned by `evaluate()` is recorded **whatever it is**, with the exact counts, denominators, and Fraction values that produced it, and no outcome is forced or masked.

### AC3: Zero Gate Threshold Alteration

**Given** protocol §5 externalization gate thresholds and pre-registration criteria are locked
**Then** no threshold moves in either direction, no protocol version is altered, and no finding's verdict eligibility is fabricated.

### AC4: Automated Verification Test

**Given** `validation-corpus/adjudication-record.json` and the corpus manifest
**Then** an automated test (`TC-ArgusAgent-PRECISION-001-155`) imports `evaluate()`, executes it against the live record, and asserts that the recorded outcome matches the evaluated result.

---

## §2 — Technical Requirements & Architecture Guardrails

1. **Re-use existing pre-registration fold** (`AR7` / `AI-E17-5`):
   - Import `evaluate`, `CriterionEvaluationResult`, `CRITERION_OUTCOMES` from `scripts.precision_preregistration`.
   - Do NOT create a parallel fold function or duplicate math.
2. **Exact Fraction arithmetic** (`AR4`):
   - All precision rates, thresholds, and ratios must remain exact `Fraction` instances, never `float`.
3. **Purity & Safety** (`AR8`):
   - No network calls, no clock dependencies, no non-reproducible environment reads.
4. **Explicit Path Staging**:
   - Stage by explicit file path; never use `git add -A`.

---

## §3 — Tasks / Subtasks

- [x] **Task 0: Re-measure Premises at HEAD** (AC: #1, #2, #3, #4)
  - [x] Re-verify HEAD commit, branch status, and byte invariants on `deferred-work.md` and `sprint-status.yaml`.
  - [x] Search codebase for any existing derivations of `evaluate()` to confirm one-derivation compliance (`AI-E17-5`).
- [x] **Task 1: Implement Fold Execution Test** (AC: #1, #2, #4)
  - [x] Create/update test module under `tests/` importing `evaluate()` from `scripts.precision_preregistration`.
  - [x] Add `TC-ArgusAgent-PRECISION-001-155` asserting deterministic execution of `evaluate()` against `validation-corpus/adjudication-record.json`.
- [x] **Task 2: Record Outcome & Metrics** (AC: #2, #3)
  - [x] Document the evaluated result (`MET`, `NOT_MET`, or `UNEVALUABLE`) along with underlying counts (denominator, numerator, Fraction values).
  - [x] Verify no threshold or protocol definition was modified.
- [x] **Task 3: AST One-Derivation & Purity Verification** (AC: #1, #4)
  - [x] Verify AST check ensures `evaluate()` is imported rather than re-implemented.
- [x] **Task 4: Run Test Suite & Verify Invariants** (AC: #1, #2, #3, #4)
  - [x] Run `pytest` on the local Windows environment.
  - [x] Re-verify byte invariants (`deferred-work.md` lone CR at line 5569, `sprint-status.yaml` CRLF-uniform).

---

## Dev Notes

### Architecture & One-Derivation References
- `scripts/precision_preregistration.py`: Contains canonical `evaluate()`.
- `argus/precision/adjudication.py`: Contains adjudication models and helpers.
- `argus/precision/replay_harness.py`: Contains replay harness and fraction definitions.
- `AI-E17-5`: One-derivation obligation (search recorded in Dev Agent Record).

---

## Dev Agent Record

### Agent Model Used
Gemini 3.6 Flash (Antigravity)

### Debug Log References
- Task 0 verification confirmed `deferred-work.md` lone CR at line 5569 and `sprint-status.yaml` CRLF-uniform (1,403 lines).
- One-derivation search confirmed `evaluate()` is exported solely from `scripts/precision_preregistration.py` and imported everywhere directly (`AR7` / `AI-E17-5`).

### Completion Notes List
- Evaluated canonical `evaluate()` fold against live record: outcome returned is `UNEVALUABLE` due to `sealed_contributing_member_count=0` below floor 3.
- Counts: `verdict_eligible_count=85`, `contributing_member_count=3`, `sealed_contributing_member_count=0`, `true_positive_count=0`, `false_accusation_count=0`, `measured_precision=None`.
- Implemented `TC-ArgusAgent-PRECISION-001-155` in `tests/test_precision_preregistration.py` asserting deterministic execution of canonical `evaluate()`, exact metric fields, and non-vacuity via mutation check.

### File List
- `_bmad-output/design-artifacts/ArgusAgent/stories/19-5-re-run-the-frozen-fold-and-let-it-decide.md`
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
- `tests/test_precision_preregistration.py`
