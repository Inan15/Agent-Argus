# Sprint Change Proposal — Verdict Vocabulary, Coverage Scope Default & Falsifiable Gates

**Date**: 2026-08-03
**Project**: ArgusAgent (`argus-agent`)
**Trigger**: Operator ran `argus audit .` on ArgusAgent itself and received
`verdict=NOT_READY_FOR_RELEASE deep_ratio=11/28 blocking_findings=0` — a blocking
verdict carrying zero findings.
**Author**: correct-course analysis
**Status**: PARTIALLY IMPLEMENTED — CR-2, CR-4, CR-5 landed 2026-08-03 (no contract
change). **CR-1 and CR-3 remain PROPOSED and require a PRD FR16/FR4 amendment before
implementation.**

---

## 1. Issue Summary

Argus renders a **release-blocking verdict on a repository in which it found nothing
wrong**. Three distinct defects combine to produce it, and each is independently
worth fixing.

### 1.1 The blocking verdict is used for two incompatible meanings

`evaluate_verdict` (`argus/verdict/verdict_gate.py:511-520`) evaluates:

| condition (in order) | verdict | exit |
|---|---|---|
| `assessed_total == 0` or `assessed_ratio < 1/5` | `INSUFFICIENT_COVERAGE` | 3 |
| `assessed_ratio >= 3/5` and `blocking == 0` and `critical_subsystems_all_deep` | `RELEASE_READY` | 0 |
| otherwise | `NOT_READY_FOR_RELEASE` | 2 |

The `otherwise` row collapses two situations a human must be able to distinguish:

- **"I found a defect"** — ≥1 verdict-blocking finding. Blocking is correct.
- **"I did not examine enough to vouch"** — zero findings, an unmet coverage or
  critical-subsystem gate. Blocking is a **false accusation**.

The second case asserts a defect the audit did not find. Cross-cutting concern #6
names a wrong 🔴 as the lethal failure this codebase is built to avoid; the verdict
gate itself currently commits it. `INSUFFICIENT_COVERAGE` already carries exactly the
right meaning ("ArgusAgent has not assessed enough to honestly claim it saw enough"),
and PRD Journeys 3 and 5 already route exit `3` to human review, never to auto-proceed.

### 1.2 The default coverage denominator penalises being well-tested

A test file is graded `audited_shallow` **by construction** — it is the subject of the
vacuous-test pass, never a target of deep grounding. With `--coverage-scope repository`
(the default) those entries sit in the denominator and can never enter the numerator.

Measured on this repository at `ae5f00c`:

| Population | Deep | Total | Ratio | Gate (≥ 3/5) |
|---|---|---|---|---|
| Whole repository | 55 | 140 | 39% | ✗ fails |
| Application files only | 55 | 71 | 77% | ✓ passes |
| Application files **excluding `__init__.py`** | 55 | 55 | **100%** | ✓ passes |

**Every application module containing code is `audited_deep`.** The 39% is entirely a
composition artifact.

The inversion this creates is the decisive argument: **deleting the test suite raises
the score from 39% to 77% and clears the coverage gate.** A tool whose stated moat is
detecting fake tests currently rewards having no tests.

### 1.3 Sixty-two of the 62 critical blockers are unreachable

The FR16 critical-subsystem clause withholds `RELEASE_READY` until every critical path
is `audited_deep`. On this repository 62 paths are critical and not deep:

| Group | Count | Why it can never reach `audited_deep` |
|---|---|---|
| Test files under `tests/` | 51 | `assess_criticality` flags them CRITICAL from security tokens in their content (correct anti-gaming behaviour), while the pipeline grades them shallow by construction. Both rules are individually right; together they are unsatisfiable. |
| `argus/**/__init__.py` | 10 | Clean parse, zero definitions → deep claim ungrounded → downgraded (`pipeline.py:384-396`). Nothing exists in them to ground a claim against. |
| `argus/detectors/vacuous_test.py` | 1 | **Genuine defect** — `is_test_file` (`argus/detectors/vacuous_test.py:204-209`) matches the suffixes `_test.py` and `test.py`, so this production module is classified as a test file, skipped by the grading path, and falls through to the breadth detector as `tool_scanned_only`. Introduced by the 2026-07-28 multi-language change. |

The documented escape hatch does not scale: `--exclude-critical` is an exact-path set
difference (`critical_subsystems.py:255`) with no prefix or glob matching, so clearing
these requires 62 individually enumerated flags.

**A gate the operator cannot satisfy is not a gate — it is a defect in the gate.**

### 1.4 Related over-claim (already remediated, recorded here for completeness)

`audited_deep` is defined in the PRD as *"a structured finding citing specific symbols /
line ranges validated against the repo AST"*. With no LLM-backed deep pass wired into
the pipeline, what it actually attests is: parsed cleanly + ≥1 definition + deterministic
detectors ran. The Epic-6 `LLMDispatchPort`, adapters and cache-key closure exist, but
nothing dispatches through them (`argus/pipeline.py` imports `argus.audit.grounding`
only; `deep_audit.py` is marked EXPERIMENTAL / DF-22-15-A).

This was remediated **presentationally** on 2026-08-03 without a contract change — see
§4. The enum value itself is deliberately left frozen.

---

## 2. Impact Analysis

| Artifact | Impact |
|---|---|
| PRD FR16 (verdict gate thresholds) | **Amendment required** — the gate decision table changes |
| PRD FR4 (critical-subsystem designation) | **Amendment required** — eligibility predicate added |
| `argus/verdict/verdict_gate.py` | Decision table; `VERDICT_SCHEMA_VERSION` bump |
| `argus/ledger/critical_subsystems.py` | Eligibility filter; glob-capable exclusion |
| `argus/cli.py` | `--coverage-scope` default flip |
| `argus/detectors/vacuous_test.py` | `is_test_file` suffix fix |
| Persisted `.apaa/` verdicts | Pre-amendment artifacts keep their meaning; new ones carry the bumped `schema_version` |
| CI consumers | **Behaviour change** — some runs that exited `2` will exit `3` |

**Scope classification: MODERATE.** Contained to the verdict/criticality modules, but it
changes a frozen contract and an exit code, so it is not a silent patch.

---

## 3. Proposed Changes

### CR-1 — Split the blocking verdict from the coverage verdict *(contract change)*

Amend the FR16 decision table to evaluate findings before coverage:

| condition (in order) | verdict | exit |
|---|---|---|
| `assessed_total == 0` or `assessed_ratio < 1/5` | `INSUFFICIENT_COVERAGE` | 3 |
| `blocking >= 1` | `NOT_READY_FOR_RELEASE` | 2 |
| `assessed_ratio >= 3/5` and `critical_subsystems_all_deep` | `RELEASE_READY` | 0 |
| otherwise (no findings; a coverage/critical gate unmet) | `INSUFFICIENT_COVERAGE` | 3 |

**Nothing becomes a silent pass.** Exit `3` still fails an unconfigured CI step, and
Journeys 3/5 already specify its routing (human STOP, never auto-proceed). What changes
is that Argus stops asserting a defect it did not find.

Requires `VERDICT_SCHEMA_VERSION` `"1"` → `"2"` (an intentional content-hash change,
per the additive-only rule in `verdict_gate.py:147-149`).

### CR-2 — Make `--coverage-scope application` the default *(behaviour change)*

Keep `repository` available for the strict whole-tree view. The `CoverageScope`
disclosure machinery already exists and already prints both ratios, so the narrowing
remains fully disclosed on the verdict, in the report, and in the summary line. The
coverage floor continues to be re-applied *within* the scope — a narrowing changes what
is claimed, never the bar for claiming it.

### CR-3 — Restrict the critical set to files that can reach `audited_deep` *(contract change)*

A file graded shallow **by construction** is ineligible for the FR16 clause. Concretely:
exclude `is_test_file(path)` entries from the heuristic critical set, and exclude
clean-parsed zero-definition modules.

Operator designation via `--critical-subsystem` keeps its current conservative
behaviour, including for an unmatched path: an explicit human designation should still
be able to withhold `RELEASE_READY`.

Expected effect on this repository: 62 unreachable blockers → 0.

### CR-4 — Prefix/glob matching for `--exclude-critical` *(additive)*

`--exclude-critical tests/` should remove the subtree. An escape hatch requiring 62
exact paths is not an escape hatch.

### CR-5 — Fix `is_test_file` misclassifying production modules *(plain defect)*

Drop the bare `test.py` suffix and tighten `_test.py` so `argus/detectors/vacuous_test.py`
is graded as the production module it is. Add a regression test naming this file.

---

## 4. Already Implemented (2026-08-03, no contract change)

Presentation-only; the wire contract, verdict values and exit codes are untouched:

1. **`argus/reports/plain_english.py`** (new, PURE) — the brief's dual-register human
   output. Renders a ship-readiness headline that distinguishes *"BLOCKED — N findings"*
   from *"NOT VOUCHED — nothing broken was found, but a coverage gate was not met"*,
   plus the counts and a conditional next step.
2. **`argus/cli.py`** — human register printed to **stderr**; stdout keeps the machine
   summary line as the sole, unchanged, positionally-parseable wire contract.
3. **`argus/reports/generator.py`** — ship-readiness line above the fold in
   `final-verdict.md`; a `NOTE` callout stating what `audited_deep` attests in this run,
   **derived from `enabled_passes`** so it strengthens automatically when an LLM-backed
   deep pass is enabled and cannot drift out of date.
4. **`tests/test_plain_english.py`** (new, 12 tests) — pins the zero-finding/blocking
   split, the scope disclosure, determinism, and secret-safety.

5. **CR-2 — `--coverage-scope application` is now the CLI default.** Deliberately
   flipped on the CLI surface ONLY; `AuditRequest.coverage_scope` keeps its
   `"repository"` default, so library callers, persisted evidence and every existing
   programmatic consumer are byte-unchanged. The operator-facing surface is the one
   that was misreporting, so it is the one that changed.
6. **CR-5 — `is_test_file` gained an optional keyword-only `ast_entry`.** Location and
   unambiguous non-Python suffixes still decide by path; the genuinely ambiguous Python
   `*_test.py` case is resolved by CONTENT when the caller has the pre-built AST entry
   (the pipeline does), applying the doctrine `assess_criticality` already states.
   Unreadable content keeps the filename verdict — the two misclassifications are
   asymmetric, and treating a test as production is the false-green direction.
   `_assessment_scope_paths` was threaded the AST index too, so the grading stage and
   the gate's assessed population cannot disagree within one run.
7. **CR-4 — `--exclude-critical` now matches by exact path, directory prefix, or glob**
   (`fnmatchcase`, never `fnmatch` — host-dependent case folding would break
   byte-identity across hosts). Precedence and the conservative unmatched-designation
   policy are unchanged and pinned by tests.
8. **`tests/test_test_file_classification.py`** and
   **`tests/test_critical_exclusion_patterns.py`** (new, 16 tests).

### Measured effect on this repository

| | Before | After |
|---|---|---|
| Assessed population | 140 files (whole repo) | 73 files (application) |
| Assessed deep ratio | 55/140 = 39% ✗ | 57/73 = 78% ✓ |
| `argus/detectors/vacuous_test.py` | `tool_scanned_only` (misread as a test) | `audited_deep` |
| Clearing the unreachable critical set | 62 exact-path flags | 3 flags |
| Verdict with those 3 exclusions | — | `RELEASE_READY`, exit `0` |

The remaining blocker on a default run is the FR16 critical-subsystem clause — i.e.
CR-3, which is correctly still gated behind the PRD amendment.

Verification: **1049 passed**, mypy clean across 69 source files.

Two pre-existing failures in `tests/test_dogfood_plan.py` (committed budget/partition
plan artifact stale vs live derivation) were confirmed present on the clean tree at
`ae5f00c` and are unrelated to this change. They are noted as a separate defect.

---

## 5. Recommended Sequence

| Step | Change | Gate | Status |
|---|---|---|---|
| 1 | CR-5 (`is_test_file` defect) | none — plain bug fix | ✅ done 2026-08-03 |
| 2 | CR-4 (glob exclusion) | none — additive | ✅ done 2026-08-03 |
| 3 | CR-2 (scope default) | release note; CI consumers informed | ✅ done 2026-08-03 |
| 4 | **PRD amendment for FR16/FR4** | **human approval — the contract gate** | ⛔ open |
| 5 | CR-1 + CR-3 + `schema_version` bump | after step 4 only | ⛔ blocked on step 4 |

Steps 1–3 were independently shippable and touched no frozen contract. Steps 4–5 are
the contract change and must not proceed without explicit sign-off.

### Release note required for step 3

`--coverage-scope` now defaults to `application`. A CI step that relied on the
whole-repository denominator must pass `--coverage-scope repository` explicitly to keep
its previous behaviour. Both ratios remain printed on every run, and the assessed
population remains disclosed on the verdict artifact, so no consumer loses information.

---

## 6. Rationale Against Project Objectives

- **Cross-cutting #6 (advisory-by-contract / the false-accusation moat)** — currently
  enforced on findings but not on the verdict itself. CR-1 closes that asymmetry.
- **PRD Journey 2 ("honest about its own limits")** — *"Priya isn't delighted, but she
  trusts it more, not less. The honesty is the product."* "I could not see enough" is
  precisely that register; a false block is not.
- **PRD Journey 3** — *"`INSUFFICIENT_COVERAGE` routing to human review (never a silent
  pass **or a false block**)"*. The intended behaviour is already written down.
- **Market research risk register** — *"over-claiming invites the very trust erosion
  APAA critiques"* and buyers report acute false-positive fatigue (SonarQube 40–60% FP).
  A blocking verdict with zero findings is a false positive at the verdict layer, the
  most expensive place to have one.
- **Falsifiability** — an unsatisfiable gate trains operators to ignore all gates, which
  costs more credibility than the gate ever bought.
