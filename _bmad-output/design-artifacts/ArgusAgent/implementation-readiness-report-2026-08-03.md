---
stepsCompleted:
  - step-01-document-discovery
  - step-02-prd-analysis
  - step-03-epic-coverage-validation
  - step-04-ux-alignment
  - step-05-epic-quality-review
  - step-06-final-assessment
readinessStatus: NEEDS WORK
assessedBy: Implementation Readiness workflow (bmad-check-implementation-readiness)
findingsTotal: 20
requirementCounts:
  functional: 33
  nonFunctional: 21
documentsUnderAssessment:
  prd: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md
  prdAddendum: _bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md
  architecture: _bmad-output/design-artifacts/ArgusAgent/architecture.md
  epics: _bmad-output/design-artifacts/ArgusAgent/epics.md
  stories: _bmad-output/design-artifacts/ArgusAgent/stories/ (34 files)
  ux: NOT FOUND (headless CLI — no UX artifact expected)
supportingContext:
  - _bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-03.md
  - _bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-07-28.md
  - _bmad-output/design-artifacts/ArgusAgent/deferred-work.md
  - _bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml
  - _bmad-output/design-artifacts/ArgusAgent/implementation-readiness-report-2026-06-18.md
missingReferencedInputs:
  - _bmad-output/planning-artifacts/decisions/2026-06-18-apaa-placement-under-minions-core.md
  - _bmad-output/project-context.md
---

# Implementation Readiness Assessment Report

**Date:** 2026-08-03
**Project:** ArgusAgent

## Step 1: Document Inventory

### Path Note

`_bmad/bmm/config.yaml` sets `planning_artifacts` to `{project-root}/_bmad-output/planning-artifacts`, which **does not exist**. All live planning artifacts are under `_bmad-output/design-artifacts/ArgusAgent/`. This report is written alongside them, matching the location of the prior readiness report (2026-06-18).

### PRD Files Found

**Whole Documents:**
- `E-PRD/prd.md` (59,817 bytes, modified 2026-08-03) — `stepsCompleted` through `step-12-complete`, `releaseMode: phased`
- `E-PRD/addendum.md` (3,381 bytes, modified 2026-08-03) — untracked in git; delta layered on the PRD
- `E-PRD/.memlog.md` (2,173 bytes, modified 2026-08-03) — workflow memory sidecar, not an assessment input

**Sharded Documents:** none (no `index.md` present; `E-PRD/` is a container folder, not a shard set)

**Duplicates:** none

### Architecture Files Found

**Whole Documents:**
- `architecture.md` (39,030 bytes, modified 2026-07-30) — `status: complete`, `readiness: READY FOR IMPLEMENTATION`, completed 2026-06-18, scope declares placement at `minions_core/apaa/`

**Sharded Documents:** none
**Duplicates:** none

### Epics & Stories Files Found

**Whole Documents:**
- `epics.md` (122,937 bytes, modified 2026-08-03) — `stepsCompleted` through `step-04-final-validation`, plus a `deltaRuns` entry dated 2026-08-03 (FR16/FR4 verdict-contract amendment + APAA repo separation; Epics 1–7 explicitly NOT regenerated)

**Story Files:**
- `stories/` — 34 story files spanning Epics 1–7

**Epic Retrospectives (context, not assessment inputs):**
- `epic-1-retro` … `epic-7-retro` (7 files, 2026-06-21 → 2026-07-04)

**Duplicates:** none

### UX Design Files Found

**None.** No `*ux*` artifact exists anywhere under `_bmad-output/`.

### Supporting / Change-Control Artifacts

- `sprint-change-proposal-2026-08-03.md` (14,022 bytes) — signal document for the epics delta run
- `sprint-change-proposal-2026-07-28.md` (5,325 bytes)
- `deferred-work.md` (34,344 bytes, 2026-07-04)
- `sprint-status.yaml` (131,455 bytes, 2026-07-30)
- `implementation-readiness-report-2026-06-18.md` (28,554 bytes) — prior run of this workflow
- `product-brief-apaa.md`, `product-brief-apaa-distillate.md`, three research reports (2026-06-17)
- `minions-dogfood-*` plans and proof, `precision-validation-protocol.md`

### Issues Identified

| # | Severity | Issue |
|---|----------|-------|
| 1 | WARNING | No UX artifact exists. Product is a headless CLI, so this is expected — UX assessment will be scoped out unless operator-facing surfaces (CLI output contract, report rendering) are found to need one. |
| 2 | ~~WARNING~~ **RETRACTED** | ~~`planning_artifacts` config path does not exist~~ — **incorrect.** The authoritative merged config (`_bmad/custom/config.toml:25`) deliberately overrides the installer default to `{project-root}/_bmad-output/design-artifacts/ArgusAgent`, with an explanatory comment. Configuration is correct and intentional. The stale value survives only in the legacy `_bmad/bmm/config.yaml`, which this workflow's activation step reads directly instead of the TOML chain. See revised **D1**. |
| 3 | WARNING | Two documents referenced as inputs by `epics.md` / `architecture.md` are missing from disk: `_bmad-output/planning-artifacts/decisions/2026-06-18-apaa-placement-under-minions-core.md` and `_bmad-output/project-context.md`. The first is declared *superseded* by the 2026-08-03 delta run, so its absence is expected; `project-context.md` is simply absent. |
| 4 | WATCH | `architecture.md` (last touched 2026-07-30) still declares scope `placed at minions_core/apaa/`, while the 2026-08-03 delta separated APAA into the standalone Argus repo. Potential staleness — to be verified in Step 3. |
| 5 | WATCH | `epics.md` and `E-PRD/prd.md` were modified 2026-08-03 (delta run) with Epics 1–7 explicitly not regenerated. Alignment of the delta against the un-regenerated epics is the central risk for this assessment. |

**No duplicate document formats found — no blocking resolution required before proceeding.**

---

## Step 2: PRD Analysis

**Source:** `E-PRD/prd.md` (read in full, 491 lines) + `E-PRD/addendum.md` (read in full, 56 lines).

The PRD declares a **binding capability contract** at the head of §Functional Requirements: *"a capability not listed here will not exist in V1 unless explicitly added."* Items marked **[Tier B]** are validation-grade additions over the demo-grade Tier-A core; everything unmarked is non-negotiable core. This makes the FR list authoritative and closed — a strong basis for traceability.

### Functional Requirements

#### Repository Intake & Partitioning
- **FR1:** An operator can submit a repository at a pinned commit for audit through a headless invocation.
- **FR2:** APAA can detect the repository's technology stack and available toolchain without operator configuration.
- **FR3:** APAA can partition the repository into bounded audit units within a declared budget.
- **FR4:** APAA can identify critical subsystems (and an operator can designate them) so coverage gates can require them to be examined deeply. **A file APAA can never grade `audited_deep` is ineligible for the heuristically-derived critical set** — a gate no run can satisfy is not a gate, and an unsatisfiable one trains operators to ignore every gate. *(Amended 2026-08-03.)*
  - *Eligibility (heuristic set):* exclude files that are `audited_shallow` by construction — test files (the subject of the vacuous-test pass, never a target of deep grounding) and clean-parsed zero-definition modules.
  - *Operator designation is exempt.* An explicit `--critical-subsystem` designation keeps its conservative behaviour, including for a path that matches nothing: a human saying "this matters" must still be able to withhold `RELEASE_READY`.
  - An operator can exclude a subtree from the critical set **by prefix**, not only by exact path.

#### Coverage Ledger & Grounded Evidence
- **FR5:** APAA can record every file's audit depth in a fixed-enum coverage ledger (`audited_deep` / `audited_shallow` / `tool_scanned_only` / `inferred` / `skipped`).
- **FR6:** APAA can require an emitted claim before grading a file `audited_deep` (silence downgrades to `audited_shallow`).
- **FR7:** APAA can validate a deep claim against source structure (Python AST in V1) and downgrade an unverifiable claim. **[Tier B]**
- **FR8:** APAA can exclude `inferred` (narrative/doc) evidence from satisfying any verdict gate.
- **FR9:** An operator can read exactly which files were examined deeply, shallowly, tool-scanned, inferred, or skipped.

#### Defect Detection (cartridge-validated)
- **FR10:** APAA can detect tests that appear vacuous (low assertion-density / high mock-ratio) and report them as **advisory** findings carrying their evidence counts.
- **FR11:** APAA can detect hardcoded secrets and report them with the secret value redacted.
- **FR12:** APAA can detect orphan / dead code (no referencing requirement or caller). **[Tier B]**
- **FR13:** APAA can attach at least one verifiable locator to every finding, or reject the finding.
- **FR14:** APAA can convert a tool failure or unestablishable-traceability condition into a finding rather than a crash.

#### Release-Readiness Verdict
> **Verdict vocabulary (canonical).** The ladder runs `RELEASE_READY` → … → `NOT_READY_FOR_RELEASE`; **`BLOCKED` is the demo shorthand for a blocking (`NOT_READY`) outcome** — one concept, asserting exactly one thing: **APAA found something**. **`INSUFFICIENT_COVERAGE`** is a distinct *not-assessed* state and is **not** blocking. Reached two ways: coverage below the 20% floor, **or** an unmet coverage / critical-subsystem gate with **zero blocking findings** (amended 2026-08-03). Never interchangeable.

- **FR15:** APAA can compute a release-readiness verdict as a pure function of the coverage ledger.
- **FR16:** APAA can emit `RELEASE_READY` only when coverage gates are met (≥60% deep + all critical subsystems deep + 0 blocking findings), can emit a blocking verdict **only on the strength of a finding it actually made**, and reports every other outcome as `INSUFFICIENT_COVERAGE` — never a default block. *(Amended 2026-08-03.)*

  **FR16 decision table (binding, evaluated in order)** — findings before coverage, so a coverage shortfall can never be reported as a defect:

  | # | Condition | Verdict | Exit |
  |---|---|---|---|
  | 1 | `assessed_total == 0` or `assessed_ratio < 1/5` | `INSUFFICIENT_COVERAGE` | 3 |
  | 2 | `blocking_findings >= 1` | `NOT_READY_FOR_RELEASE` | 2 |
  | 3 | `assessed_ratio >= 3/5` **and** all critical subsystems `audited_deep` | `RELEASE_READY` | 0 |
  | 4 | otherwise — zero blocking findings, a coverage or critical-subsystem gate unmet | `INSUFFICIENT_COVERAGE` | 3 |

  The verdict **must disclose which row fired** and the assessed population it was computed over.
- **FR17:** APAA can express every verdict in negative-assurance terms with a scope statement, materiality bar, disclaimer, and point-in-time stamp.
- **FR18:** An integrator can consume the verdict as a deterministic exit code and a machine-readable artifact.
- **FR33:** APAA can order findings by verdict impact — surfacing verdict-blocking findings before non-blocking ones — so a blocking 🔴 is never buried beneath lower-severity noise (alarm-fatigue defense, risk H2).

#### Self-Audit & Trust
- **FR19:** APAA can run an adversarial Prosecutor pass that challenges whether the ledger justifies the verdict and downgrades an unearned verdict. **[Tier B]**
- **FR20:** APAA can validate its own detectors against defect cartridges with golden expected-findings keys, asserted in CI.

#### Cost Governance
- **FR21:** An operator can set a budget ceiling for an audit.
- **FR22:** APAA can halt on budget exhaustion, mark the remainder `skipped`, downgrade coverage, and report honestly — never fabricating or silently overrunning.

#### Governance, Escalation & Evidence Integrity
- **FR23:** APAA can halt at a human STOP/PROCEED gate on a pattern-matched escalation condition, defaulting to STOP — and on gate timeout (no response within a configured window) it **parks at STOP, never auto-PROCEEDs**.
- **FR24:** APAA can record a human escalation decision in an append-only decision record (and log the STOP even if the record is deferred). **[Tier B]**
- **FR25:** APAA can wrap every artifact in a content-hashed, schema-versioned envelope.
- **FR26:** APAA can verify referential integrity of its on-disk state (no dangling references). **[Tier B]**
- **FR27:** APAA can reproduce the same verdict for the same repository and APAA version.
- **FR28:** APAA can redact secrets from stored excerpts and never emit source/secret bytes into ledgers, evidence, logs, or traces.
- **FR29:** An operator can export an evidence bundle (coverage ledger, scope statement, findings, verdict); the operated-service path retains no source.

#### Invocation & Resumability (headless)
- **FR30:** An integrator can invoke APAA headlessly with `repo + commit + budget + materiality_bar` and receive a verdict artifact + exit code.
- **FR31:** APAA can resume an interrupted audit from its on-disk `.apaa/` state.
- **FR32:** APAA can run to completion on a sequential (least-capable) host, producing byte-identical on-disk state to a parallel run.

**Total FRs: 33** — numbering is complete and gap-free (FR1–FR33). Note FR33 is positioned out of numeric sequence (inside the Verdict section, after FR18), a late addition; content is unambiguous.
**Tier B subset (6):** FR7, FR12, FR19, FR24, FR26 — plus NFR-A2. All others are non-negotiable core.

### Non-Functional Requirements

#### Determinism & Reproducibility *(keystone quality attribute)*
- **NFR-D1:** Same repo @ same commit + same APAA version → **identical verdict and identical coverage ledger, 100% reproducibility**, achieved by **local content-addressed memoization** of recorded findings (key = content-hash + model checkpoint + APAA version). Mechanism, *not* an assumption the LLM repeats itself. The shared cross-run cache (Minions layer **e**, V4) is a later optimization, never V1's sole guarantee.
- **NFR-D2:** The verdict gate and coverage-ledger mechanics are deterministic and testable with **zero LLM tokens** (pure functions over recorded findings).
- **NFR-D3:** Artifact content hashes cover the **canonical payload only** (excluding volatile `run_id` / `created_at`); a determinism golden-test gates the envelope before any consumer.

#### Security & Data Protection
- **NFR-S1:** Source code, prompts, responses, and API-key bytes **never** appear in coverage ledgers, evidence bundles, logs, OTLP spans, exception traces, or any response — enforced by a security test suite that **blocks CI on failure**.
- **NFR-S2:** Secret values detected in audited code are **redacted before storage**; the stored form carries a `contained_secret` flag without the value.
- **NFR-S3:** On the operated-service path, **customer source is never retained** after an audit completes.
- **NFR-S4:** An auditor agent can read **only** the files in its work-manifest (permission boundary); off-scope reads are impossible.
- **NFR-S5:** All filesystem writes are **containment-checked** (no path traversal, symlink, or sibling-prefix escape), reusing Minions workspace-containment patterns.

#### Cost Efficiency
- **NFR-C1:** A baseline full audit costs a **bounded fraction of the audited repo's build cost** (tracked target ≤ 10–20% baseline; ~1% for V2 incremental diff-scoped runs). V1 measures and reports the baseline.
- **NFR-C2:** An audit **never exceeds its declared budget ceiling**; on exhaustion it halts deterministically with no silent overrun.
- **NFR-C3:** Deterministic, **zero-token tools perform breadth** so LLM spend is reserved for depth.

#### Reliability & Honest Degradation
- **NFR-R1:** A tool/parse failure or unestablishable-traceability condition **degrades to a recorded finding or coverage downgrade — never an uncaught crash or a fabricated result.**
- **NFR-R2:** An interrupted audit is **fully resumable** from on-disk `.apaa/` state with no loss of prior coverage.

#### Portability
- **NFR-P1:** APAA runs to completion on the **least-capable host (Cline, sequential)**, producing **byte-identical on-disk state** to a parallel-capable host; parallel is a pure speedup.
- **NFR-P2:** The audit is **stack-agnostic by construction** (deep AST-grounding = Python in V1; `claim_emitted` proxy elsewhere); no host- or stack-specific logic in the ledger/verdict core.

#### Auditability & Evidence Integrity
- **NFR-A1:** Every artifact is wrapped in a **schema-versioned, content-hashed, prev-hash-chained envelope**; schemas evolve **additive-only**.
- **NFR-A2:** Referential integrity of on-disk state is **verifiable** (no dangling references). **[Tier B]**
- **NFR-A3:** Every verdict carries a **scope statement, materiality bar, disclaimer, and point-in-time stamp**.

#### Scale Envelope *(V1 bounds)*
- **NFR-SC1:** V1 audits operate within a **bounded context budget** (target ≤ 40 files / 15k LOC per audit unit; hard ceiling ≤ 60 / 25k); larger repos partition into units. Full 10k → 500k LOC scaling (multi-partition + seam auditor) is **V2**.

#### Maintainability
- **NFR-M1:** No single source file exceeds **1200 lines**; business logic stays out of entrypoints (strict modularity).
- **NFR-M2:** Frozen contracts are validated (**Pydantic v2 + JSON Schema**) and evolve **additive-only**.

**Total NFRs: 21** (D×3 + S×5 + C×3 + R×2 + P×2 + A×3 + SC×1 + M×2) — matching the count `epics.md` cites for the PRD.
**Explicitly skipped (justified):** Accessibility (headless — no UI/WCAG surface); user-growth scalability (V1 is internal; replaced by NFR-SC1).

### Additional Requirements, Constraints & Invariants

These are binding but not FR/NFR-numbered — they are the traps a traceability check must not miss, because nothing in the epics is forced to reference them by ID.

**V1 Design Invariants (forward-compatibility constraints, PRD §Product Scope):**
- **INV-1:** Envelope determinism is golden-tested **+ human-gated before any consumer**.
- **INV-2:** Grounded-claim validation is a **stack-agnostic interface** (`claim → validated?`), Python = impl #1.
- **INV-3:** Reserve `partition_id` in the coverage ledger (always `"root"` in V1) for the V2 seam auditor.
- **INV-4:** **Frozen invariant:** curated memory (G3, ships V4) **never touches the verdict/decision path**.
- **INV-5:** APAA specifies the cost/memory consumption-contracts it will need from Minions (layers a/d/e).
- **INV-6 (schema-design):** `coverage_ledger` accepts a **`claim_emitted` (unvalidated)** claim, with AST-validation as an **optional strengthening flag — never a hard schema requirement**, so AST-grounding can slide to V1.5 without breaking the contract. Severity enum lives **inline in `finding`**, not as a `$ref`.

**Contract-surface constraints (§Developer Tool):**
- **CON-1:** V1 schema set is exactly `envelope`, `finding` ①, `severity.rubric` ② *(a config constant, not a frozen schema)*, `coverage_ledger` ③, `verdict` ⑧, `decision_record` ④ (minimal) + referential-integrity lint.
- **CON-2:** `standards_refs[]` field format-validated (e.g. `^CWE-\d+$`) + **CWE required on every security-category finding** (day-one additive).
- **CON-3:** Exit-code wire contract is a **stable mapping** for `RELEASE_READY` / `BLOCKED` / `INSUFFICIENT_COVERAGE` / crash.
- **CON-4:** Filesystem-as-contract: all state under `.apaa/` (`state/ · assignments/ · findings/ · decisions/`); auditors coordinate **only** through files.
- **CON-5:** Partitioning bound: ≤ 40 files / 15k LOC per unit (hard ceiling ≤ 60 / 25k).
- **CON-6:** Criticality is detected by **content, not filename** (hostile-repo / coverage-gaming defense).
- **CON-7:** `work_manifest` **concept** only in V1 (minimal assignment = file-list = permission boundary); full schema → V3.

**Success-criteria obligations that behave like deliverables:**
- **SC-A:** **Validation protocol is an explicit V1 deliverable** — defines who validates, expert-hours/repo, the precision-adjudication method (sample size, who judges a 🔴 "genuinely real"), and per-metric pass/fail.
- **SC-B:** **≥80% finding-precision** on N ≈ 5–10 real XAgents repos — the externalization gate.
- **SC-C:** **Zero false-`RELEASE_READY`** on the validation set (asymmetric concordance; the fatal error).
- **SC-D:** Self-audit green in CI: **3 cartridges** = full V1/Tier B; **cut-order floor is 2** (vacuous + secret).
- **SC-E:** Each dogfood run emits **≥1 reusable asset** (audit report, concordance label, calibration datum, or a new cartridge on a miss).
- **SC-F:** The **Minions dogfood** is the V1 proof and is explicitly the **last thing cut**.

**Open inputs flagged by the PRD (not blockers):** team headcount, the budget-ceiling `$X`, and `N` for the validation set (5–10).

### PRD Completeness Assessment

**Strengths (unusually high quality for traceability purposes):**
- The FR list is declared a **closed, binding capability contract** — the exact property that makes a coverage check meaningful rather than advisory.
- FR numbering is **complete and gap-free** (FR1–FR33); NFRs are consistently prefixed by category.
- Tier A / Tier B grading and a **pre-agreed cut-order** are stated, so scope reduction has a defined, auditable shape rather than being ad-hoc.
- The 2026-08-03 amendment is **fully specified** — a binding decision table with exit codes, an addendum recording options-considered and rejected, an approval trail, and a named change signal. This is the level of change control that makes delta validation possible.
- Non-goals are explicit (out-of-V1 API surface, skipped UX/accessibility sections), reducing false "missing requirement" signals.

**Weaknesses / risks carried into the coverage check:**
1. **FR33 is out of numeric sequence** and sits inside the Verdict section — a bolt-on. Any epic authored before it was added would not cover it. Priority check in Step 3.
2. **The obligations are not all FR-numbered.** INV-1…6, CON-1…7 and SC-A…F are binding but carry no requirement ID, so a naive FR-only traceability pass would score 100% while leaving these unmapped. These will be traced explicitly.
3. **The amendment (FR16/FR4) post-dates the epics' original authoring** — `epics.md` states Epics 1–7 were **not regenerated**. Whether the delta reached the stories is the single highest-value question in this assessment.
4. **NFR-C1's target is soft** ("tracked target ≤ 10–20% baseline; V1 measures and reports") — testable as *measure-and-report*, not as a pass/fail bar. Acceptable, but stories must implement the measurement, not a threshold.
5. **Three open inputs remain unresolved** (headcount, budget ceiling `$X`, validation-set `N`). The PRD calls them non-blockers to be resolved "in the delivery/functional detail" — i.e. they are owed by the epics/stories layer, and are checked there.
6. **The PRD's own scope line still says APAA is "placed at `minions_core/apaa/`"** in classification context, while the 2026-08-03 change separated it into the standalone Argus repo (the addendum references `argus/verdict/verdict_gate.py`). Location drift to verify in Step 3.

---

## Step 3: Epic Coverage Validation

**Source:** `epics.md` (read in full, 1,751 lines). Structure: Epics 1–7 (34 stories, original breakdown, marked delivered) + an **Amendment Delta** section adding Epics 8–9 (7 stories) and a Minions-Repo Handoff (H0–H4, explicitly *not* epics).

### Coverage Matrix — PRD FR → Epic → Story

| FR | PRD Requirement (abbrev.) | Epic Coverage | Story-level AC | Status |
|---|---|---|---|---|
| FR1 | Submit repo @ pinned commit, headless | Epic 1 | 1.4 (refuses if tree ≠ pin) | ✓ Covered |
| FR2 | Stack/toolchain auto-detect, no config | Epic 1 | 1.4 | ✓ Covered |
| FR3 | Partition into bounded units within budget | Epic 2 | 2.4 | ✓ Covered |
| FR4 | Critical-subsystem ID + operator designation | Epic 2 | 2.3 | ⚠️ Covered (pre-amendment only) |
| FR4 *(amended clause)* | Eligibility predicate; designation exempt; prefix exclusion | Epic 8 | 8.2 (DR-5/6/7) | ✓ Covered |
| FR5 | Fixed-enum coverage ledger | Epic 1 | 1.2, 2.6 | ✓ Covered |
| FR6 | Claim required for `audited_deep`; silence→shallow | Epic 1 | 1.2 | ✓ Covered |
| FR7 **[Tier B]** | Validate deep claim vs Python AST | Epic 6 | 6.2 (+1.5 Tier-A subset) | ✓ Covered |
| FR8 | `inferred` never satisfies a gate | Epic 2 | 2.1, 1.6 | ✓ Covered |
| FR9 | Operator can read per-file depth | Epic 2 | 2.2 | ✓ Covered |
| FR10 | Vacuous-test detector, advisory + evidence counts | Epic 1 | 1.5 | ✓ Covered |
| FR11 | Hardcoded-secret detection, redacted | Epic 2 | 2.5 | ✓ Covered |
| FR12 **[Tier B]** | Orphan / dead-code detection | Epic 6 | 6.3 | ✓ Covered |
| FR13 | ≥1 verifiable locator per finding, or reject | Epic 1 | 1.5, 6.3 | ✓ Covered |
| FR14 | Tool failure / untraceable → finding, not crash | Epic 2 | 2.6 | ✓ Covered |
| FR15 | Verdict = pure function of ledger | Epic 1 | 1.6 | ✓ Covered |
| FR16 | Gates + floor, never a default block | Epic 1 + Epic 2 (+ Epic 3 floor) | 1.6, 2.3, 3.3 | ⚠️ Covered (pre-amendment only) |
| FR16 *(amended)* | Binding 4-row table, findings before coverage, row disclosure | Epic 8 | 8.1 (DR-1/2/3/4/9) | ✓ Covered |
| FR17 | Negative-assurance semantics + scope/materiality/disclaimer/stamp | Epic 4 | 4.1 | ✓ Covered |
| FR18 | Deterministic exit code + machine-readable artifact | Epic 1 | 1.6 | ✓ Covered |
| FR19 **[Tier B]** | Adversarial Prosecutor downgrades unearned verdict | Epic 6 | 6.4 | ✓ Covered |
| FR20 | Cartridge self-validation, CI-asserted | Epic 6 | 6.5 | ⚠️ Covered — **cut-order conflict** (see F3) |
| FR21 | Operator-set budget ceiling | Epic 3 | 3.1 | ✓ Covered |
| FR22 | Halt→skip→downgrade→report on exhaustion | Epic 3 | 3.2 | ✓ Covered |
| FR23 | HITL STOP/PROCEED, default-STOP, timeout parks at STOP | Epic 6 | 6.7 | ⚠️ Covered — **cut-order conflict** (see F3) |
| FR24 **[Tier B]** | Append-only decision record | Epic 6 | 6.7 | ✓ Covered |
| FR25 | Content-hashed, schema-versioned envelope | Epic 1 | 1.1 | ✓ Covered |
| FR26 **[Tier B]** | Referential-integrity lint | Epic 4 | 4.2 | ✓ Covered |
| FR27 | Reproducible verdict | Epic 5 | 5.2 | ✓ Covered |
| FR28 | No source/secret bytes in artifacts | Epic 2 + Epic 4 | 2.5 (producer), 4.4 (CI enforcement) | ✓ Covered |
| FR29 | Evidence-bundle export, no source retention | Epic 4 | 4.3 | ✓ Covered |
| FR30 | Headless invocation contract | Epic 1 | 1.7 | ✓ Covered |
| FR31 | Resume from `.apaa/` state | Epic 3 | 3.4 | ✓ Covered |
| FR32 | Sequential byte-identical execution | Epic 3 | 3.5 | ✓ Covered |
| FR33 | Verdict-impact finding ordering | Epic 1 | 1.6 | ✓ Covered |

**No FR appears in the epics that is absent from the PRD.** The delta requirements (DR-1…11, RS-1…4, IN-0…5) are correctly derived from amended FR16/FR4 and architecture constraints, not invented scope.

### NFR Coverage

All **21** NFRs are mapped in the epics' own NFR map (`D1→E5; D2/D3/A1/M1/M2/S5→E1; S2/S4/C3/R1/SC1→E2; C1/C2/R2/P1/P2→E3; S1/S3/A2/A3→E4; P2→E6`). Verified: the map enumerates 21 distinct NFR IDs with no omission, and each has at least one story AC asserting it.

### Coverage Statistics

- **Total PRD FRs:** 33
- **FRs covered in epics (map level):** 33 — **100%**
- **FRs covered by a named story AC:** 33 — **100%**
- **Total PRD NFRs:** 21 · **NFRs covered:** 21 — **100%**
- **Unnumbered binding obligations traced (INV/CON/SC):** 19 identified · **13 covered · 4 missing · 2 partial** — **68% full coverage**

### 🔴 Missing / Defective Coverage

Headline FR/NFR traceability is 100%. Every gap below sits in the layer a requirement-ID-only pass cannot see.

#### F1 — CRITICAL: `epics.md` carries the **pre-amendment FR16 and FR4** in its own Requirements Inventory · ✅ **RESOLVED 2026-08-03**

> **✅ Fixed during this session.** `epics.md:93` (FR4) and `:111` (FR16) now carry the amended text, plus a
> vocabulary note on `INSUFFICIENT_COVERAGE` vs `NOT_READY_FOR_RELEASE`, and a warning banner on the
> Requirements Inventory heading directing story-writers to the amended text and away from the Epic 1–3
> story ACs that predate it. **The decision table was deliberately *not* copied a third time** — both
> entries link to the single authoritative statement in §Amendment Delta. A third copy would have been a
> third drift surface, which is the defect this finding names. Original analysis retained below.

The delta section restates the amended FR16/FR4 correctly (`epics.md:1115-1138`). But the document's primary **Requirements Inventory** — the section a developer or story-writer reads first — still carries the superseded text:

- `epics.md:111` — *"FR16: APAA can emit a verdict only when coverage gates are met …, and emit `INSUFFICIENT_COVERAGE` below the 20% floor — never a default block."* No 4-row table, no findings-before-coverage ordering, no row-disclosure obligation.
- `epics.md:93` — *"FR4: APAA can identify critical subsystems (and an operator can designate them) …"* No eligibility predicate, no designation exemption, no prefix exclusion.

**Impact:** one document states two different contracts for the same requirement, 1,000 lines apart, with nothing at the stale copy pointing forward. On a product whose entire thesis is *"evidence that contradicts the tool is the cardinal defect,"* this is the same defect class internally. A `/bmad-create-story` run or a dev agent reading the inventory implements the superseded table.
**Recommendation:** amend `epics.md:93` and `:111` in place to the amended text, or add an explicit `⚠️ SUPERSEDED — see §Amendment Delta` marker on both. This is a one-edit fix and should not wait for the delta epics.

#### F2 — HIGH: **CON-2 (CWE required on every security-category finding) has no story anywhere**

PRD §Compliance and §Product Scope both bind this as **day-one additive V1** scope: *"`standards_refs[]` field (format-validated, e.g. `^CWE-\d+$`) + **CWE required on every security-category finding** — the cheapest, most mechanical, highest-stakes mapping."*

Searched all 41 stories: no AC mentions `standards_refs`, CWE, or a security-category mapping. Story 2.5 (the secret detector — the one security-category finding producer in V1) requires `contained_secret`, redaction and a locator, but **no CWE**.

**Impact:** a binding V1 capability with zero implementation path. It is also the requirement most directly load-bearing for the Journey 4 regulated-evidence story, and being *additive* it is far cheaper now than after the finding schema is frozen and content-hashed.
**Recommendation:** add an AC to Story 2.5 (and to `detectors/base` in Story 1.5, where the finding contract is defined) requiring a format-validated `standards_refs[]` with CWE mandatory when `category == security`.

#### F3 — HIGH: two **non-negotiable-core** FRs are stranded inside the epic declared wholly slippable

`epics.md:867-868` declares: *"**The whole epic [6] is the cut-order boundary** — if 90 days is tight, these are the Tier-B items that slip to V1.5."* But Epic 6 contains two requirements the PRD marks as **never cut**:

- **FR20** (cartridge self-audit) is **not** `[Tier B]`. The PRD cut-order names *"**2 cartridges (vacuous + secret)**"* in the non-negotiable core and is emphatic: *"Floor is 2, not 1 — Tier A ships redaction, and cartridge #2 is its only validator; cutting it would ship an unvalidated security path."* FR20's only story is **6.5**, which bundles all three cartridges + hidden holdout + clean controls into one unit inside the slip boundary.
- **FR23** (HITL STOP/PROCEED gate) is **not** `[Tier B]` — only FR24 (`decision_record`) is. The PRD cut-order slide list is explicit: *"(4) `decision_record` (but still **log the STOP**)"*. FR23 and FR24 are bundled together in a single story, **6.7**, again inside the slip boundary.

The epics document half-registers this at `:1062` (*"Tier-A demo-grade = Epics 1–3 (+ cartridges #1/#2 in 6.5)"*) — but a parenthetical is not a splittable work unit. Exercising the pre-agreed cut as written drops an unvalidated security-redaction path and the default-STOP gate.
**Recommendation:** split 6.5 → a Tier-A story (cartridges #1/#2 + clean controls) and a Tier-B story (#3 + holdout); split 6.7 → a Tier-A story (FR23 gate + STOP logging) and a Tier-B story (FR24 append-only record). Cheaper as a planning edit than as a mid-cut discovery.

#### F4 — MEDIUM: **SC-E (credibility-flywheel asset per dogfood run) is unstoried**

PRD §Business Success: *"each dogfood run emits **≥1 reusable asset** — audit report, concordance label, calibration datum, or (on a miss) a new defect cartridge."* Story 7.2 produces the proof artifact and evidence bundle, but no AC requires the concordance label, calibration datum, or the **promote-a-miss-to-a-cartridge** step. (Holdout rotation is correctly deferred to V2; *promote-a-miss* is not scoped as V2 in the Business Success criterion.)
**Impact:** the PRD names this as the measurable proxy for the moat compounding. Without an AC, a dogfood run can complete "successfully" while the flywheel records nothing.

#### F5 — MEDIUM: **INV-5 and the Minions-PRD action have no owner** — the same defect the delta's own H0 flags

PRD §Product Scope: *"APAA specifies the cost/memory consumption-contracts it will need from Minions (a)/(d)/(e)"*, and §Dependencies: *"📝 **Minions-PRD action:** record (a)+(d)+(e) + (b)+(c) as Minions epics/features."* Neither appears in any epic or story.

This is structurally identical to **H0** — which the delta's own inversion analysis correctly identified and escalated (*"a handoff nobody files is a handoff that does not exist"*). The same reasoning applies here and was not applied.
**Impact:** low for V1 execution (all three layers are V2–V4 consumption), but it is a declared V1 deliverable and it is the second unowned cross-repo filing action in the plan. **H0 itself remains `UNOWNED` in the frontmatter `openDecisions`** — a blocking-severity planning gap the document raises and does not close.

#### F6 — MEDIUM: **INV-4 (curated memory never touches the verdict/decision path) is declared "frozen now" and stated nowhere in the epics**

PRD: *"**Frozen invariant declared now:** curated memory (G3, ships V4) **never touches the verdict/decision path**."* No epic, story, AC, or architectural-constraint note carries it. The architecture's AR8 pure/impure rule is adjacent but does not name it.
**Impact:** low today (G3 is V4), but the PRD's intent in declaring it *now* is precisely that it be recorded before the verdict path solidifies. An invariant recorded in no downstream artifact is not frozen.

#### F7 — LOW/PARTIAL: two invariants covered mechanically but missing their stated guard

- **INV-1** — Story 1.1 delivers the envelope determinism golden test ✓, but the PRD's *"**human-gated** before any consumer"* clause has no AC. The PRD calls this *"the single highest-leverage correctness item."*
- **INV-6** — `claim_emitted` unvalidated + AST-as-optional-strengthening is covered (1.2 / 1.5 / 6.2) ✓, but the paired clause *"severity enum lives **inline in `finding`**, not as a `$ref` to the config rubric"* is asserted in no AC, nor is `severity.rubric`'s status as a **config constant rather than a frozen schema** (CON-1).

#### F8 — NOTED (already self-identified, tracked): **SC-C, zero false-`RELEASE_READY`**

The PRD names this **the fatal error**. In the original Epics 1–7, the only cartridge guard is Story 6.5's clean-control AC — *"any 🔴 is an instant CI fail"* — which guards the false-**red** direction only. The delta's own inversion analysis found this independently (*"every guard points only at over-blocking and NOTHING guarding the PRD-fatal false-`RELEASE_READY` direction"*) and added the F1 false-green counterweight AC to Story 8.2. **Correctly caught and correctly placed** — recorded here only to confirm it is closed for the delta's own loosening, not as a general false-green regression guard across Epics 1–7.

### Coverage Assessment

Numeric traceability is exemplary — **33/33 FRs and 21/21 NFRs**, an explicit FR Coverage Map, a separate Delta Requirements Coverage Map with every DR/RS/IN accounted for, and relocated work preserved rather than dropped. The delta's advanced-elicitation passes (inversion, self-consistency, boundary sweep, assumption audit) are unusually rigorous and caught several real defects before this review.

The failures are all in the same blind spot: **obligations the PRD binds without an FR number**. The requirement-ID pass scores 100%; the unnumbered-obligation pass scores 68%. F2 (CWE) is a missing V1 capability, F3 is a cut-order defect that would only surface under schedule pressure — the worst possible moment — and F1 is an internal contradiction of exactly the kind this product exists to detect.

---

## Step 4: UX Alignment Assessment

### UX Document Status

**Not Found — and correctly so.** This is not a gap. Three independent artifacts agree, and the agreement is explicit rather than incidental:

| Source | Statement |
|---|---|
| `prd.md` frontmatter | `headless: true`; `skipSections: [ux_ui, visual_design, user_journeys]` |
| `prd.md` §Classification | *"**Headless-only** — verdicts and evidence are artifacts and API surfaces, never screens (no UI/UX)."* |
| `prd.md` §NFR | *"**Skipped (justified):** Accessibility (headless — no UI/WCAG surface)"* |
| `architecture.md:56, 85` | *"deterministic exit codes. **No UI**; no V1 HTTP service."* · *"Headless-only (CLAUDE.md §3.7): artifacts + exit codes; no UI/HTTP-service surface in V1."* |
| `epics.md:240-245, 1261-1265` | *"**None — APAA is headless by design** … No UX Design Specification is an input, and **none may be authored** (CLAUDE.md §3.7)."* |

**Is UX implied anywhere?** Checked deliberately rather than assumed:
- No web, mobile, IDE-plugin, or visual component appears in any FR, NFR, or architecture decision.
- The hosted-runner / HTTP / API surface is explicitly **out of V1** (→ V4).
- All five PRD journeys are operator-CLI or system-to-system; J4's "evidence bundle" is a file artifact, hand-delivered.
- The architecture places APAA **downstream of the HTTP/A2A boundary** with a committed CI gate (`argus.* ⊬ fastapi/uvicorn/starlette`) mechanically preventing a web surface from appearing.

**Verdict: no UX document is required, and authoring one is correctly forbidden.** No warning is warranted on the absence itself.

### The surface that *substitutes* for UX — and is unspecified

A headless tool still has an operator-comprehension surface, and this PRD binds it as a **User Success criterion**, not a nicety:

> *"**Actionable, not a hedge:** a plain-English line (*"BLOCKED — 3 vacuous tests, coverage 62% deep"*) the user acts on while retaining the decision."*
> *"**No cry-wolf:** a 🔴 is credible enough to forward to the team, not mute."*

That surface is `argus/reports/` — and it is **absent from both the architecture and Epics 1–7**.

#### F9 — HIGH: the `reports/` rendering layer exists in code but appears in no design artifact

| Check | Result |
|---|---|
| Exists on disk | ✅ `argus/reports/` → `plain_english.py`, `generator.py`, `formatter.py` |
| In the architecture package tree (`architecture.md:405-452`) | ❌ **Absent** |
| In the architecture FR-cluster→location map (`:503-512`) | ❌ **Absent** — FR15–18/FR33 map to `verdict/`, `cli.py` only |
| Owned by a story in Epics 1–7 | ❌ **No story** — `plain_english` appears nowhere in the original breakdown |
| Specified anywhere | ⚠️ Only **retroactively and partially**, by delta Story 8.3 / DR-11 |

The delta's self-consistency pass caught the consequence but not the cause. It found that `generator.py` is *"a **second** verdict-rendering surface with its **own** FR16 reasoning"* branching independently on the verdict enum, deep-ratio threshold and `blocking_finding_count` — and widened DR-11 to cover it. That is a correct fix for this amendment. But the underlying condition stands: **two independent implementations of FR16's presentation logic exist, neither traceable to a design artifact.** That is precisely how the original bug arose — the FR16 reasoning drifted in a surface nobody was tracking — and nothing in the plan prevents the third occurrence.

This also means the PRD's two operator-facing User Success criteria have **no acceptance criteria anywhere in Epics 1–7**. Story 8.3 now pins how two `INSUFFICIENT_COVERAGE` states must read *differently* to a human — genuinely good operator-comprehension work — but it is scoped to the amendment, not to the success criterion.

#### F10 — MEDIUM: the architecture package tree has drifted from the shipped package

`reports/` is not the only omission. Comparing `architecture.md:405-452` against `argus/`:

| Module on disk | In architecture tree? |
|---|---|
| `argus/reports/` | ❌ Missing |
| `argus/dogfood/` | ❌ Missing (yet Story 7.1's partition plan is generated from it) |
| `argus/shared/` | ❌ Missing |
| `argus/pipeline_persist.py` | ❌ Missing |

Four modules, one of them a whole rendering layer. The architecture is stamped `status: complete` / `readiness: READY FOR IMPLEMENTATION` and was last modified 2026-07-30 — after all seven epics were retro'd. It is being treated as current while describing a package that no longer matches.

#### Architecture staleness — placement (already tracked)

The architecture still declares placement at `minions_core/apaa/` throughout (`:66, :173, :308, :355, :403-452`), superseded by the 2026-08-03 repo separation into `argus/`. This is **correctly tracked** as RS-4b and **explicitly deferred** with a recorded reason. Not a new finding — but note it compounds F10: the tree is wrong in both *location* and *content*, and only the location half is on the register.

### UX ↔ PRD ↔ Architecture Alignment

| Dimension | Status |
|---|---|
| UX ↔ PRD | ✅ N/A by design, consistently declared in both |
| UX ↔ Architecture | ✅ N/A, and mechanically enforced by the import-isolation gate |
| Operator-comprehension surface ↔ PRD | ❌ Two User Success criteria have no owning story (F9) |
| Operator-comprehension surface ↔ Architecture | ❌ Entire `reports/` layer unmodelled (F9/F10) |
| Architecture ↔ shipped package | ❌ Four modules missing from the tree (F10) |

### Warnings

1. **No warning is issued for the missing UX document** — headless is declared, justified, and enforced.
2. ⚠️ **F9 (HIGH):** the operator-facing report layer carries duplicated FR16 presentation logic in two files, is traceable to no story or architecture entry, and hosts the exact drift that produced the bug this whole delta exists to fix.
3. ⚠️ **F10 (MEDIUM):** the architecture document is stamped READY FOR IMPLEMENTATION while omitting four shipped modules. Anyone using it as the structural contract will not find them.
4. ℹ️ **Recommendation:** add `reports/` to the architecture package tree and FR-cluster map with a single stated owner for verdict presentation, and add an AC — to Story 8.3, since it is already in that file — requiring that **FR16 presentation logic live in exactly one place**. That converts DR-11 from a one-time reconciliation into a structural guarantee.

---

## Step 5: Epic Quality Review

Scope: **9 epics, 41 stories** (34 in Epics 1–7, 7 in delta Epics 8–9), assessed against create-epics-and-stories standards.

### A. User Value Focus

| Epic | Title framing | Verdict |
|---|---|---|
| 1 | Signature-Demo Vertical Slice — "the false-green catch" | ✅ User outcome; explicitly a vertical slice, not a scaffolding epic |
| 2 | Full Coverage Ledger & Defect Detectors | ✅ Goal states the operator outcome ("read exactly what was examined") |
| 3 | Honest Degradation & Cost Governance | ✅ Journey 2 outcome |
| 4 | Negative-Assurance Verdict & Evidence Bundle | ✅ Journey 4 outcome |
| 5 | Reproducible Verdict & Memoization | ✅ Journey 3 outcome ("a number you can put on a dashboard") |
| 6 | Trust Substrate — Self-Audit, Prosecutor & Precision | ⚠️ Weakest — see Q4 |
| 7 | Minions Dogfood Proof Run | ✅ The strategic proof artifact |
| 8 | The Honest Verdict — no block without a finding | ✅ Exemplary — states the operator experience directly |
| 9 | Make Argus Consumable | ✅ Downstream-integrator outcome |

**No purely technical-milestone epics.** Every epic states a user or integrator outcome. This is materially better than the norm.

### B. Epic Independence — declared vs. actual

**Declared:** every epic states its dependency, all backward (`epics.md:1065-1066`: *"each epic stands alone and builds only on earlier epics; no story depends on a future story within its epic"*). At the *stated* level this is clean.

**Actual: the claim does not hold.** Three forward dependencies exist in acceptance criteria.

#### 🔴 Q1 — CRITICAL: Epic 5 cannot function on Epics 1–4 alone — it requires Epic 6 twice

Epic 5 is declared *"Builds on Epics 1–4."* Two of its ACs require capabilities delivered only in Epic 6:

1. **Story 5.1** requires the cache key to fold *"model checkpoint **(captured from the API response, not config)**"*. That capture is delivered by **Story 6.1**, whose AC reads: *"**captures the model checkpoint from the API response** (AR5)."* Until 6.1 lands there is no API response to capture from — `audit/minions_llm_adapter.py` is the only thing that produces one.
2. **Story 5.3** requires *"**Given** a human-**rejected** finding **When** the audit re-runs **Then** that finding's cache key is busted."* Human rejection is recorded by the decision-record mechanism in **Story 6.7** (FR24, `[Tier B]`). Epic 5 has no channel through which a rejection can be expressed.

**Impact:** NFR-D1 — the *keystone quality attribute* — has an unsatisfiable acceptance path until Epic 6. And Epic 6 is the declared cut boundary, so under the pre-agreed cut, reproducibility ships with a cache key missing its model-checkpoint input. AR5 exists precisely because a key that omits the checkpoint can serve a result produced by a different model.
**Recommendation:** move Story 6.1 (LLM dispatch port) to Epic 3 or earlier — it is infrastructure, not Tier-B trust work, and Epic 3's cost accounting arguably needs it too. Then re-sequence 5.3's rejection AC behind a minimal STOP-logging capability, or state explicitly that 5.3 is gated on 6.7.

#### 🟠 Q2 — MAJOR: Tier-A obligations depend on stories in Tier-B epics

Same defect class as F3 in Step 3, found from the dependency side rather than the cut-order side:

- **Story 2.5** (secret detector, Tier-A non-negotiable) AC: *"no source/secret bytes appear in the ledger… (FR28 producer guarantee; **the CI property suite that enforces it lands in Epic 4**)."* NFR-S1 is specified as **CI-blocking** — the mechanism that makes redaction a guarantee rather than a promise is **Story 4.4**, in an epic classified Tier-B (`epics.md:1062`). Tier A ships redaction; under the cut it ships it *unenforced*.
- **Story 2.4** (partitioning, Tier-A) AC: *"a defect spanning a cut is handled **only by the Story 6.4** `cross_partition` Prosecutor cut-edge pass."* Epic 6 is the cut boundary. Cutting it leaves V1 doing multi-partition auditing with **zero** cut-edge mitigation — and OI2 locks the Minions dogfood to *full-repo multi-partition*, so the proof run is exactly the scenario that loses its only defense.

Both references are *documentary* — Epics 2 functions without 4 and 6 — so neither breaks build order. Both are nonetheless real: a non-negotiable guarantee whose enforcement is optional is not a guarantee.

#### 🟡 Q3 — MINOR: forward reference inside Epic 8

Story 8.1's channel-decision AC requires the row to surface *"in prose on the stderr human register **(Story 8.3)**"*, while Epic 8 declares *"8.1 and 8.2 are each standalone."* 8.1 is completable — the artifact field and the unchanged stdout line are its own — but one clause of its AC is satisfied by a later story. Restate as "8.1 owns the artifact field; 8.3 owns the stderr prose."

### C. Epic Cohesion

#### 🟠 Q4 — MAJOR: Epic 6 is a grab-bag carrying disproportionate risk

Seven stories spanning: an LLM infrastructure port (6.1), AST grounding (6.2), a detector (6.3), the Prosecutor (6.4), the cartridge harness (6.5), a precision harness + a written protocol (6.6), and HITL governance (6.7). These share no user outcome beyond "things that earn externalization."

Cohesion alone would be a minor concern. It compounds badly:
- it is the **declared cut boundary** — the whole epic slips as a unit;
- it holds **two non-negotiable-core FRs** (FR20, FR23 — Step 3 F3);
- it holds **Epic 5's missing dependencies** (Q1);
- it holds **Epic 2's only cut-edge mitigation** (Q2).

Four independent problems all resolve to *"Epic 6 is where the un-cuttable work was parked in the cuttable epic."* Splitting Epic 6 into a Tier-A half (6.1 port, cartridges #1/#2, FR23 STOP gate) and a Tier-B half (AST grounding, orphan, Prosecutor, holdout, precision, decision record) resolves F3, Q1, Q2 and Q4 in one move. **This is the single highest-leverage structural fix in the plan.**

### D. Story Sizing

| Story | Concern |
|---|---|
| **6.5** | 🟠 Five deliverables in one story: cartridges #1, #2, #3, hidden holdout, clean controls + false-negative traps. Also blocks the F3 Tier-A split. |
| **6.6** | 🟠 A code harness **and** a written validation protocol (SC-A, a distinct PRD deliverable) **and** a phased 3→5 population plan. Split the protocol out — it is a document with its own reviewers. |
| **6.7** | 🟠 FR23 (non-negotiable) + FR24 (`[Tier B]`) bundled, preventing the cut the PRD pre-agreed. |
| **8.1** | 🟡 Large (DR-1/2/3/4/9, 9 ACs) but cohesive — one decision table. Acceptable. |
| **2.4** | 🟡 Three concerns: partitioning (FR3), permission boundary (NFR-S4), no-seam-analysis limitation. Cohesive enough. |
| **1.1–1.3** | 🟡 "As an APAA maintainer" foundation stories — serializer, schemas, store. Strictly these are the *"create all models upfront"* pattern the standards flag. **Justified deviation:** the architecture designates envelope determinism *"the single highest-leverage correctness item,"* golden-tested and gated **before any consumer**, so it must precede. Recorded as a knowing deviation, not a defect. |

All other stories are appropriately sized.

### E. Acceptance Criteria Quality

**Format:** Given/When/Then applied consistently across all 41 stories — no exceptions found. Error paths are covered where they matter (1.7 degradation, 2.6 tool failure, 9.2 release edge cases). Boundary conditions in Epic 8 are unusually rigorous (exactly-20% row disclosure, floor-vs-blocking precedence, empty-critical-set disclosure). **This is the strongest dimension of the whole plan.**

Four ACs fail the testability bar:

#### 🟠 Q5 — MAJOR: Story 3.1's cost AC depends on an input that exists nowhere

> *"**Then** APAA reports the baseline as a fraction of **the audited repo's build cost** (target ≤10–20%, measured not asserted in V1 — NFR-C1)."*

Nothing in the PRD, architecture, or any story defines how *"the audited repo's build cost"* is obtained. There is no FR to ingest it, no CLI parameter carrying it, no module computing it. The PRD's own §Dependencies places cost estimation in **Minions layer (a), consumed at V3**. As written the AC cannot be satisfied in V1, so NFR-C1 — an explicitly *"scariest risk"* NFR — has no verifiable acceptance path.
**Recommendation:** either add an operator-supplied `--repo-build-cost` input, or restate the AC as "reports absolute audit spend + the denominator it was given, or records that no denominator was available."

#### 🟡 Q6 — MINOR: three non-machine-testable ACs

- **Story 4.1:** *"**When** reviewed **Then** the language never implies certification"* — no reviewer named, no checklist, no test. Given the PRD's liability posture (M2), this deserves a named human gate or a forbidden-phrase lint.
- **Story 2.1:** *"**Then** coverage-gaming by renaming is defeated"* — asserts an outcome without specifying the adversarial test that demonstrates it.
- **Story 6.6:** *"3 labeled repos front-loaded in M1"* — no AC names who produces the labels or what labeling quality is acceptable, though SC-A's protocol partially absorbs this.

### F. Special Implementation Checks

**Starter template:** The architecture explicitly **rejects** an external scaffold (`architecture.md:173`) and states *"there is **no project-init story**"*, because *"the starter is the existing Minions repo + the already-reserved `minions_core/apaa/__init__.py` shell + the `minions[apaa]` extra (already staged)."* Under the original placement this correctly satisfied the standard.

#### 🟠 Q7 — MAJOR: the "no project-init story" justification is void after the repo separation

Every premise of that rationale is now false — APAA is a standalone repo, not a sub-package; there is no reserved shell in a host repo; the `minions[apaa]` extra is being *removed* (RS-2). ArgusAgent is now, structurally, a **greenfield standalone project**, and the standards for one apply: project setup, environment config, and **CI/CD early**.

The evidence confirms the gap rather than contradicting it: `.github/workflows/` contains exactly **one** file, `audit-ci.yml` — no release, publish, or packaging workflow. The delta caught the symptom (assumption A1 falsified → IN-0 → Story 9.2) but treated it as an *integration* need. It is really the project-init work the original plan was excused from doing. Story 9.2 is correctly scoped for release infrastructure; what remains unowned is the rest of a standalone repo's baseline.

**Greenfield/brownfield indicators:** Integration points are well handled — IN-0…IN-5 and H1–H4 are unusually thorough for cross-repo work, and the sequencing constraint (Argus-side before Minions-side; RS-2 + IN-1 together) is correct and explicitly reasoned.

**Database/entity timing:** N/A — filesystem-as-contract. Schema creation in Story 1.2 is upfront by design (frozen, additive-only contracts for a declared contract-producer). Not a violation.

#### 🟠 Q8 — MAJOR: the delta epics have no story spec packs and no sprint entries

| Epic | Story specs in `stories/` | In `sprint-status.yaml` |
|---|---|---|
| 1–7 | ✅ 34 files (7·6·5·4·3·7·2) | ✅ |
| **8–9** | ❌ **0 files** | ❌ **No entries** |

The 7 delta stories exist only as AC blocks inside `epics.md`. They are the work that is *next*, and they are the only work without context-filled specs. `epics.md:1078` names `/bmad-create-story` as the step that produces them — it has not been run for 8.x/9.x, and `/bmad-sprint-planning` has not been re-run since the delta. `sprint-status.yaml` was last modified 2026-07-30, four days before the delta.

### Best-Practices Compliance Checklist

| Criterion | Epics 1–7 | Epics 8–9 |
|---|---|---|
| Epic delivers user value | ✅ (Epic 6 weak) | ✅ |
| Epic functions independently | ❌ Epic 5 needs Epic 6 (Q1) | ✅ |
| Stories appropriately sized | ⚠️ 6.5 / 6.6 / 6.7 oversized | ✅ |
| No forward dependencies | ❌ Q1, Q2 | ⚠️ Q3 (minor) |
| Entity creation when needed | ✅ N/A / justified | ✅ |
| Clear acceptance criteria | ⚠️ Q5, Q6 | ✅ Exemplary |
| Traceability to FRs maintained | ✅ 33/33 | ✅ every DR/RS/IN mapped |
| Story specs exist | ✅ 34 | ❌ 0 (Q8) |

### Quality Findings by Severity

**🔴 Critical**
- **Q1** — Epic 5 has two forward dependencies on Epic 6 (model-checkpoint capture, human-rejection channel), leaving NFR-D1 unsatisfiable until the cut-boundary epic lands.

**🟠 Major**
- **Q2** — Tier-A guarantees (FR28 enforcement, cut-edge mitigation) depend on stories in Tier-B epics.
- **Q4** — Epic 6 is a low-cohesion grab-bag that concentrates F3, Q1 and Q2 in one slippable unit.
- **Q5** — Story 3.1's NFR-C1 acceptance criterion depends on an input defined nowhere in V1.
- **Q7** — The "no project-init story" rationale is void post-separation; standalone-repo baseline work is unowned.
- **Q8** — Epics 8–9 have no story spec packs and no sprint-status entries.
- Story sizing: **6.5**, **6.6**, **6.7** each bundle separable deliverables and block the F3 Tier-A split.

**🟡 Minor**
- **Q3** — Story 8.1 references Story 8.3's deliverable within its own AC.
- **Q6** — Three non-machine-testable ACs (4.1 certification language, 2.1 rename-gaming, 6.6 labeling ownership).
- Stories 1.1–1.3 are maintainer-facing foundation stories — a knowing, architecture-justified deviation.

### Remediation Priority

1. **Split Epic 6** into Tier-A and Tier-B halves — resolves F3, Q1, Q2 and Q4 together, and forces the 6.5 / 6.7 story splits as a side effect. Highest leverage in the plan.
2. **Fix `epics.md:93` and `:111`** (Step 3 F1) — a two-line edit removing a contradictory contract.
3. **Run `/bmad-create-story` for Stories 8.1–9.2 and re-run `/bmad-sprint-planning`** (Q8) — this is the next work and it is unspecced.
4. **Add the CWE AC** (Step 3 F2) and **restate Story 3.1's cost AC** (Q5).
5. **Name an owner for H0** and the Minions-PRD action (Step 3 F5).

---

## Summary and Recommendations

**Date:** 2026-08-03 · **Assessor:** Implementation Readiness workflow · **Project:** ArgusAgent (APAA)

### Delivery-state calibration (read this before the severities)

Epics 1–7 are **delivered** — `sprint-status.yaml` records 74 stories `done`, seven epic retrospectives exist, and the code ships. The work actually facing implementation is **Epics 8–9 (7 stories)**.

That changes what several findings mean, and saying so plainly matters more than a dramatic severity count:

- **Live findings** affect Epics 8–9 or name a V1 capability that was never built. These gate the next sprint.
- **Retrospective findings** describe planning defects in Epics 1–7 whose risk window has closed — the pre-agreed cut was never exercised, so the cut-order and sequencing hazards did not materialise. They convert from *planning gaps* into *verification questions* ("is this actually true in the shipped code?") and into lessons for the next scope decision.

The Step 3–5 analysis stands as written. This section re-scores its **implications**.

### Overall Readiness Status

# 🟠 NEEDS WORK

**Not blocked — but not ready to hand Epics 8–9 to a developer today.** Two live issues must clear first; both are hours of work, not days.

The planning quality here is genuinely high: **33/33 FRs and 21/21 NFRs traced**, Given/When/Then applied without exception across all 41 stories, a closed and binding capability contract, an explicit pre-agreed cut-order, and change control on the 2026-08-03 amendment (options matrix, rejected alternatives, approval trail, named change signal) that is better than most teams manage. The delta's own adversarial passes — inversion, self-consistency, boundary sweep, assumption audit — independently found and closed several real defects before this review, including the false-green counterweight and the unowned-handoff problem. That is the behaviour a product built on falsifiable evidence should exhibit, and it does.

The findings cluster in one blind spot: **obligations the PRD binds without a requirement ID**. Requirement-ID traceability scores 100%; the 19 unnumbered binding obligations score **68%**.

### Critical Issues Requiring Immediate Action

#### ✅ 1. `epics.md` states two contradictory versions of FR16 and FR4 *(F1 — **RESOLVED 2026-08-03**)*

> **Fixed in this session.** FR4 and FR16 in the Requirements Inventory now carry their amended text with
> a pointer to the single authoritative decision table, and the inventory heading carries a banner warning
> that Epics 1–7 predate the amendment. **One blocker remains (item 2).** Original analysis:
The primary Requirements Inventory at [`epics.md:93`](epics.md) and [`:111`](epics.md) still carries the **pre-amendment** text — no 4-row decision table, no findings-before-coverage ordering, no critical-set eligibility predicate — with no forward pointer. The amended text sits 1,000 lines below in the delta section.

**Why it blocks:** the next action is `/bmad-create-story` for Stories 8.1–8.5, which reads this file. A story-writer or dev agent consulting the inventory implements the superseded contract — reintroducing the exact bug Epic 8 exists to fix. On a product whose thesis is *"evidence that contradicts the tool is the cardinal defect,"* this is that defect, internally.
**Fix:** two-line edit — amend in place, or mark both `⚠️ SUPERSEDED — see §Amendment Delta`.

#### 🔴 2. Epics 8–9 have no story spec packs and no sprint entries *(Q8 — LIVE, blocking)*
34 spec files exist for Epics 1–7; **zero** for the 7 delta stories. `sprint-status.yaml` was last touched 2026-07-30 — four days before the delta — and its header still declares *"Source epics: … (7 epics / 34 stories)."* The only work that is genuinely *next* is the only work without context-filled specs.
**Fix:** run `/bmad-create-story` for 8.1–9.2, then re-run `/bmad-sprint-planning`.

### Major Issues — fix in parallel, do not block on them

| # | Finding | Status | Action |
|---|---|---|---|
| **F2** | **CWE-on-security-findings has no story anywhere.** PRD binds `standards_refs[]` + CWE-required-on-security as day-one additive V1. Zero of 41 stories mention it — including Story 2.5, V1's only security-finding producer. | 🔴 **LIVE** — a V1 capability that was never built | Add an AC to the finding contract (`detectors/base`) and to 2.5. Cheap now, expensive after the finding schema is frozen and content-hashed. |
| **F9** | **`argus/reports/` exists in code and in no design artifact** — absent from the architecture tree, the FR-cluster map, and every story in Epics 1–7. It holds **two** independent implementations of FR16 presentation logic. | 🔴 **LIVE** — Story 8.3 edits this layer | Add `reports/` to the architecture; add an AC to 8.3 requiring FR16 presentation logic in exactly one place. Converts DR-11 from cleanup into a structural guarantee. |
| **F10** | Architecture omits four shipped modules (`reports/`, `dogfood/`, `shared/`, `pipeline_persist.py`) while stamped `READY FOR IMPLEMENTATION`. | 🔴 **LIVE** | Update the package tree. The known `minions_core/apaa/` staleness is tracked as deferred RS-4b; this *content* drift is on no register. |
| **Q7** | The *"no project-init story"* rationale is void post-separation — every premise (host repo, reserved shell, staged extra) is now false. `.github/workflows/` holds exactly one file. | 🔴 **LIVE** | Story 9.2 covers release infra; scope the remaining standalone-repo baseline. |
| **F5** | **H0 is `UNOWNED` in the epics' own frontmatter** — nobody owns filing H1–H4 against the Minions backlog. INV-5 and the PRD's Minions-PRD action are the same unowned pattern, unrecognised. | 🔴 **LIVE** | Name an owner, or record that filing is the operator's step outside this workflow. The delta says it best: *"a handoff nobody files is a handoff that does not exist."* |
| **Q5** | Story 3.1 requires reporting cost as a fraction of *"the audited repo's build cost"* — an input defined in no FR, CLI flag, or module. PRD places cost estimation in Minions layer (a) at **V3**. | ⚠️ **VERIFY** — story marked done | Confirm how NFR-C1 was actually satisfied, or restate the AC as "absolute spend + the denominator given, or record that none was available." |
| **F4** | SC-E (≥1 reusable asset per dogfood run — concordance label, calibration datum, promote-a-miss cartridge) is unstoried. | 🟠 **LIVE** — Story 8.5 re-derives the dogfood | Add to 8.5 while the artifacts are being touched anyway. |
| **Q1** | Epic 5 required Epic 6 twice — model-checkpoint capture (6.1) and the human-rejection channel (6.7). NFR-D1's acceptance path was unsatisfiable until the cut-boundary epic landed. | ⚠️ **RETROSPECTIVE → VERIFY** | Sequencing risk has passed (both delivered). Confirm the shipped cache key folds the model checkpoint **from the API response**, and that rejected-finding key-busting works. AR5 exists because a key omitting the checkpoint serves results from a different model. |
| **F3 / Q2 / Q4** | Non-negotiable-core FRs (FR20 cartridges, FR23 STOP gate) and Tier-A guarantees (FR28 enforcement, cut-edge mitigation) were stranded inside epics classified Tier-B / declared slippable. Epic 6 concentrated all of it. | ⚠️ **RETROSPECTIVE** — the cut was never exercised | No harm materialised. **Lesson for the next scope decision:** the cut-order boundary must be drawn at story granularity, not epic granularity. If any Epic 6 work remains open, the Epic 6 split is still the highest-leverage fix. |

### Minor Issues

- **F6** — INV-4 (*"curated memory never touches the verdict/decision path"*, declared **frozen now**) appears in no downstream artifact. An invariant recorded nowhere is not frozen.
- **F7** — INV-1's *human-gated* clause and INV-6's *severity-inline-not-`$ref`* clause have no AC.
- **Q3** — Story 8.1's AC references Story 8.3's deliverable while Epic 8 declares 8.1 standalone. Restate the ownership split.
- **Q6** — Three non-machine-testable ACs: 4.1 (*"never implies certification"* — no reviewer or lint named, notable given the M2 liability posture), 2.1 (rename-gaming *"defeated"*), 6.6 (label ownership).
- **D1** *(revised)* — **Two config sources disagree.** The authoritative merged chain is correct: `_bmad/custom/config.toml:25` deliberately overrides `planning_artifacts` to `_bmad-output/design-artifacts/ArgusAgent`, with a comment explaining the override. But the **legacy `_bmad/bmm/config.yaml:7` still holds the installer default** (`_bmad-output/planning-artifacts`, a path that does not exist) — and several skill activation steps, including this workflow's, read that file directly rather than resolving the TOML chain. Any skill taking the legacy path will look in the wrong place. Fix: delete or realign `_bmad/bmm/config.yaml`. *(An earlier draft of this report recorded this as "the config is wrong"; the authoritative config is right — only the legacy copy is stale.)*
- **D2** — `sprint-status.yaml`'s PATH NOTE is self-cancelling: *"may still say `design-artifacts/ArgusAgent/`; read those as `design-artifacts/ArgusAgent/`"* — both sides identical after a partial rename edit, in the machine-read tracker.
- **F8** — Zero-false-`RELEASE_READY` (SC-C, *the fatal error*): guarded only in the false-**red** direction across Epics 1–7. The delta's inversion pass caught this and added the counterweight AC to Story 8.2. ✅ **Correctly closed** for the delta's own loosening; no general regression guard exists across Epics 1–7.

### Recommended Next Steps

1. ~~**Amend `epics.md:93` and `:111`** to the post-amendment FR16/FR4 text.~~ ✅ **DONE 2026-08-03** — both entries carry the amended text and link to the single authoritative decision table; the inventory heading warns that Epics 1–7 predate the amendment.
2. **Run `/bmad-create-story` for Stories 8.1–9.2**, then **`/bmad-sprint-planning`** to seed the delta stories into the tracker.
3. **While writing those specs, fold in:** the CWE AC (F2), the single-FR16-presentation-surface AC on 8.3 (F9), the SC-E flywheel AC on 8.5 (F4), and the 8.1/8.3 ownership split (Q3).
4. **Update `architecture.md`:** add `reports/`, `dogfood/`, `shared/`, `pipeline_persist.py` to the package tree and FR-cluster map (F10).
5. **Resolve H0** — name an owner for the Minions handoff filing, or record it as the operator's own step (F5).
6. **Verify, don't re-plan, the retrospective items:** cache key folds the API-response checkpoint (Q1), and how NFR-C1's build-cost denominator was actually satisfied (Q5).
7. **Optional but recommended:** delete or realign the legacy `_bmad/bmm/config.yaml` so it stops contradicting the authoritative `_bmad/custom/config.toml` (D1), and fix the self-cancelling PATH NOTE in `sprint-status.yaml` (D2).

### Final Note

This assessment identified **20 issues across 5 categories** (requirements traceability, unnumbered obligations, architecture alignment, epic structure, and document hygiene) — of which **2 are blocking**, **9 are major**, and **9 are minor**. Of the 20, **13 are live** and **7 are retrospective verification items** against already-delivered work.

Nothing found undermines the plan's foundation. FR/NFR traceability is complete, the acceptance criteria are strong, and the change control on the 2026-08-03 amendment is exemplary. The two blocking items are a two-line documentation fix and a workflow run that was simply never executed after the delta.

Address items 1 and 2, and Epics 8–9 are ready for implementation. The remainder can proceed in parallel or be consciously accepted — that call is yours, not this report's.

