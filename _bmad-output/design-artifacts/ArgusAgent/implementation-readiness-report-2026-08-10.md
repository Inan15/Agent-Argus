---
stepsCompleted:
  - step-01-document-discovery
  - step-02-prd-analysis
  - step-03-epic-coverage-validation
  - step-04-ux-alignment
  - step-05-epic-quality-review
  - step-06-final-assessment
readinessStatus: NEEDS WORK — implementation not blocked
issuesFound: 19
findingsWithdrawnOnVerification: 4
documentsUnderAssessment:
  prd: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md
  prdAddendum: _bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md
  architecture: _bmad-output/design-artifacts/ArgusAgent/architecture.md
  epics: _bmad-output/design-artifacts/ArgusAgent/epics.md
  sprintStatus: _bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml
  ux: NOT PRESENT
supersedes: implementation-readiness-report-2026-08-03.md
---

# Implementation Readiness Assessment Report

**Date:** 2026-08-10
**Project:** ArgusAgent

## Step 1 — Document Discovery

**Planning artifacts root:** `_bmad-output/design-artifacts/ArgusAgent/`

### PRD Files Found

**Whole Documents:**

- None at the artifact root.

**Sharded Documents:**

- Folder: `E-PRD/`
  - `prd.md` (80,171 bytes, modified 2026-08-10 08:35)
  - `addendum.md` (3,440 bytes, modified 2026-08-10 08:17)
  - `.memlog.md` (2,177 bytes, modified 2026-08-10 08:17)
  - No `index.md` — this is a folder-grouped PRD, not a BMad-sharded PRD.

### Architecture Files Found

**Whole Documents:**

- `architecture.md` (53,653 bytes, modified 2026-08-10 08:14)

**Sharded Documents:**

- None.

### Epics & Stories Files Found

**Whole Documents:**

- `epics.md` (169,675 bytes, modified 2026-08-10 08:35)
- `sprint-status.yaml` (250,462 bytes, modified 2026-08-10 08:36) — execution tracker, 63 story keys
- `stories/` — 41 story files present, covering Epics 1 through 9 only
  (E1:7, E2:6, E3:5, E4:4, E5:3, E6:7, E7:2, E8:5, E9:2)

**Sharded Documents:**

- None.

**Epic-retrospective documents (historical, not under assessment):** `epic-1-retro` … `epic-9-retro`.

### UX Design Files Found

- None. No file matching `*ux*` exists at the artifact root.

## Issues Found

### Duplicates

None. A repository-wide `find . -name index.md` under the artifact root returned no results, so no document exists in both whole and sharded form.

### Missing Documents

- ⚠️ **WARNING: No UX design document found.** ArgusAgent is a headless CLI/CI tool, so this is expected rather than a gap; the UX dimension will be recorded as NOT APPLICABLE unless the PRD asserts a UI surface.

### Other Observations Carried Into Assessment

- ⚠️ The prior readiness report, `implementation-readiness-report-2026-08-03.md`, predates Epic 10 (added 2026-08-09) and Epics 11–13 (added 2026-08-10b). It does not cover the current plan. This report supersedes it.
- Four of the five documents under assessment were modified on 2026-08-10, within roughly 20 minutes of each other, by `sprint-change-proposal-2026-08-10.md` and `-08-10b.md`. The plan is freshly re-cut and has not previously been gated.

## Documents Selected for Assessment

| Role | Path |
| --- | --- |
| PRD | `E-PRD/prd.md` |
| PRD addendum | `E-PRD/addendum.md` |
| Architecture | `architecture.md` |
| Epics & Stories | `epics.md` |
| Execution tracker | `sprint-status.yaml` |
| UX | NOT PRESENT |

## Step 2 — PRD Analysis

**Source read in full:** `E-PRD/prd.md` (587 lines), `E-PRD/addendum.md`, `E-PRD/.memlog.md`.
**Amendment state:** two recorded amendments — 2026-08-03 (FR16/FR4 verdict contract) and 2026-08-10b (V1.5 public release; FR34–FR37, NFR-S6, NFR-P3 added). Both approved by XAgent007.

### Functional Requirements

Binding capability contract per the PRD: *"a capability not listed here will not exist in V1 unless explicitly added."* Items marked **[Tier B]** are validation-grade additions over the demo-grade core.

**Repository Intake & Partitioning**

- **FR1:** An operator can submit a repository at a pinned commit for audit through a headless invocation.
- **FR2:** APAA can detect the repository's technology stack and available toolchain without operator configuration.
- **FR3:** APAA can partition the repository into bounded audit units within a declared budget.
- **FR4:** APAA can identify critical subsystems (and an operator can designate them) so coverage gates can require them to be examined deeply. A file APAA can never grade `audited_deep` is ineligible for the heuristically-derived critical set — a gate no run can satisfy is not a gate, and an unsatisfiable one trains operators to ignore every gate. *(Amended 2026-08-03.)*
  - *Eligibility (heuristic set):* exclude files that are `audited_shallow` by construction — test files (the subject of the vacuous-test pass, never a target of deep grounding) and clean-parsed zero-definition modules.
  - *Operator designation is exempt.* An explicit `--critical-subsystem` designation keeps its conservative behaviour, including for a path that matches nothing.
  - An operator can exclude a subtree from the critical set by prefix, not only by exact path.

**Coverage Ledger & Grounded Evidence**

- **FR5:** APAA can record every file's audit depth in a fixed-enum coverage ledger (`audited_deep` / `audited_shallow` / `tool_scanned_only` / `inferred` / `skipped`).
- **FR6:** APAA can require an emitted claim before grading a file `audited_deep` (silence downgrades to `audited_shallow`).
- **FR7:** APAA can validate a deep claim against source structure (Python AST in V1) and downgrade an unverifiable claim. **[Tier B]**
- **FR36:** An operator can enable an LLM-backed deep-audit pass that produces grounded claims beyond the zero-token path. **[Tier B]** *(Added 2026-08-10b.)* Off by default, always — the default run is zero-token, offline, no key or account, transmits nothing; enabling requires explicit operator action per invocation. Egress is disclosed before it occurs (what is transmitted, to which provider, before the first byte leaves). Governed by the existing FR21/FR22 ceiling — no new cost-governance mechanism. Determinism preserved by the FR27/NFR-D1 memoization path. Degradation is honest: an unavailable, erroring, or budget-halted provider downgrades coverage and records a finding (NFR-R1); never a false deep claim, never a crash.
- **FR8:** APAA can exclude `inferred` (narrative/doc) evidence from satisfying any verdict gate.
- **FR9:** An operator can read exactly which files were examined deeply, shallowly, tool-scanned, inferred, or skipped.
- **FR37:** APAA can state, on every terminal outcome, why that outcome was reached and the next action that changes it. *(Added 2026-08-10b.)* Enumerated over the full verdict vocabulary — `RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`, and the `AUDIT_FAILED` non-verdict — pinned by a test that fails on an unenumerated outcome. `INSUFFICIENT_COVERAGE` is the load-bearing case: it must name the specific unmet gate (floor, ratio, or critical subsystem) and the action that would change it. Self-contained — the next action is in the tool's own output. Names what was never examined, not only what scored low: every verdict states which file classes were **not ingested**, distinguishing never-ingested / ingested-but-held-out / assessed; this extends FR17's scope statement to include the ingestion boundary. Governs explanation, never classification — FR16's decision table is untouched.

**Defect Detection (cartridge-validated)**

- **FR10:** APAA can detect tests that appear vacuous (low assertion-density / high mock-ratio) and report them as **advisory** findings carrying their evidence counts.
- **FR11:** APAA can detect hardcoded secrets and report them with the secret value redacted.
- **FR12:** APAA can detect orphan / dead code (no referencing requirement or caller). **[Tier B]**
- **FR13:** APAA can attach at least one verifiable locator to every finding, or reject the finding.
- **FR14:** APAA can convert a tool failure or unestablishable-traceability condition into a finding rather than a crash.

**Release-Readiness Verdict**

- **FR15:** APAA can compute a release-readiness verdict as a pure function of the coverage ledger.
- **FR16:** APAA can emit `RELEASE_READY` only when coverage gates are met (≥60% deep + all critical subsystems deep + 0 blocking findings), can emit a blocking verdict only on the strength of a finding it actually made, and reports every other outcome as `INSUFFICIENT_COVERAGE` — never a default block. *(Amended 2026-08-03.)* Binding ordered decision table:

  | # | Condition | Verdict | Exit |
  |---|---|---|---|
  | 1 | `assessed_total == 0` or `assessed_ratio < 1/5` | `INSUFFICIENT_COVERAGE` | 3 |
  | 2 | `blocking_findings >= 1` | `NOT_READY_FOR_RELEASE` | 2 |
  | 3 | `assessed_ratio >= 3/5` **and** all critical subsystems `audited_deep` | `RELEASE_READY` | 0 |
  | 4 | otherwise — zero blocking findings, a coverage or critical-subsystem gate unmet | `INSUFFICIENT_COVERAGE` | 3 |

  The verdict must disclose which row fired and the assessed population it was computed over.
- **FR17:** APAA can express every verdict in negative-assurance terms with a scope statement, materiality bar, disclaimer, and point-in-time stamp.
- **FR18:** An integrator can consume the verdict as a deterministic exit code and a machine-readable artifact.
- **FR33:** APAA can order findings by verdict impact — surfacing verdict-blocking findings before non-blocking ones — so a blocking 🔴 is never buried beneath lower-severity noise (alarm-fatigue defense, risk H2).
- **FR34:** APAA can disclose its own validation status on **every** user-facing verdict surface, and cannot emit a verdict on a surface that omits it. *(Added 2026-08-10b.)* Content: the tool's finding-precision validation state (validated / not independently validated) and the corpus it rests on. Mechanical enforcement — the surface set is enumerated in a committed test that fails on an unenumerated member. Distinct from FR17 and both apply (FR17 bounds *this audit's* scope; FR34 bounds *the tool's* credibility). Removable only on measurement and **replaced rather than deleted** — when the ≥80% gate clears, the disclosure is replaced by a statement of the cleared status and the clearing corpus; the enforcing test never becomes vacuous. Not a permanent state: coupled to a committed programme to clear the gate (Epic 13); if that programme is abandoned, the free public tier is withdrawn rather than the disclosure.

**Self-Audit & Trust**

- **FR19:** APAA can run an adversarial Prosecutor pass that challenges whether the ledger justifies the verdict and downgrades an unearned verdict. **[Tier B]**
- **FR20:** APAA can validate its own detectors against defect cartridges with golden expected-findings keys, asserted in CI.

**Cost Governance**

- **FR21:** An operator can set a budget ceiling for an audit.
- **FR22:** APAA can halt on budget exhaustion, mark the remainder `skipped`, downgrade coverage, and report honestly — never fabricating or silently overrunning.

**Governance, Escalation & Evidence Integrity**

- **FR23:** APAA can halt at a human STOP/PROCEED gate on a pattern-matched escalation condition, defaulting to STOP — and on gate timeout it parks at STOP, never auto-PROCEEDs.
- **FR24:** APAA can record a human escalation decision in an append-only decision record (and log the STOP even if the record is deferred). **[Tier B]**
- **FR25:** APAA can wrap every artifact in a content-hashed, schema-versioned envelope.
- **FR26:** APAA can verify referential integrity of its on-disk state (no dangling references). **[Tier B]**
- **FR27:** APAA can reproduce the same verdict for the same repository and APAA version.
- **FR28:** APAA can redact secrets from stored excerpts and never emit source/secret bytes into ledgers, evidence, logs, or traces.
- **FR29:** An operator can export an evidence bundle (coverage ledger, scope statement, findings, verdict); the operated-service path retains no source.

**Invocation & Resumability (headless)**

- **FR30:** An integrator can invoke APAA headlessly with `repo + commit + budget + materiality_bar` and receive a verdict artifact + exit code.
- **FR31:** APAA can resume an interrupted audit from its on-disk `.apaa/` state.
- **FR32:** APAA can run to completion on a sequential (least-capable) host, producing byte-identical on-disk state to a parallel run.
- **FR35:** A coding agent can invoke an audit and consume the verdict through a **local agent-integration surface**, without a human relaying it. *(Added 2026-08-10b.)* Two shipped forms: an MCP server (stdio transport) and packaged assistant command assets the installer places in the host's configuration. Bounded by the §Project Classification constraints — stdio only, no network listener, no port bound; no HTTP stack, preserving the `argus.* ⊬ fastapi` import-isolation gate and ADR #20; no credentials accepted or stored. No new authority — invokes the same pure `AuditRequest → AuditVerdict` path as the CLI under the same work-manifest permission boundary (NFR-S4). Verdict parity asserted, not assumed: same repository at same commit → same verdict through either surface, pinned by test.

**Total FRs: 37** (FR1–FR37, contiguous, no gaps). Tier-B-marked: FR7, FR12, FR19, FR24, FR26, FR36.

### Non-Functional Requirements

**Determinism & Reproducibility** *(keystone quality attribute)*

- **NFR-D1:** Same repository at same commit and same APAA version → identical verdict and identical coverage ledger, **100% reproducibility** across runs, achieved by local content-addressed memoization of recorded findings (key = content-hash + model checkpoint + APAA version). Mechanism, *not* an assumption the LLM repeats itself. The shared cross-run cache (Minions layer e, V4) is a later optimization, never V1's sole guarantee.
- **NFR-D2:** The verdict gate and coverage-ledger mechanics are deterministic and testable with **zero LLM tokens** (pure functions over recorded findings).
- **NFR-D3:** Artifact content hashes cover the canonical payload only (excluding volatile `run_id`/`created_at`), so identical inputs yield identical hashes; a determinism golden-test gates the envelope before any consumer.

**Security & Data Protection**

- **NFR-S1:** Source code, prompts, responses, and API-key bytes **never** appear in coverage ledgers, evidence bundles, logs, OTLP spans, exception traces, or any response — enforced by a security test suite that blocks CI on failure.
- **NFR-S2:** Secret values detected in audited code are redacted before storage; the stored form carries a `contained_secret` flag without the secret value.
- **NFR-S3:** On the operated-service path, customer source is never retained after an audit completes.
- **NFR-S4:** An auditor agent can read **only** the files in its work-manifest (permission boundary); off-scope reads are impossible.
- **NFR-S5:** All filesystem writes are containment-checked (no path traversal, symlink, or sibling-prefix escape).
- **NFR-S6:** **No source code, prompt, or repository content leaves the machine on the default path.** *(Added 2026-08-10b.)* Third-party transmission occurs only through the explicitly enabled FR36 deep pass, is disclosed before the first byte is transmitted, and names the receiving provider. The FR35 agent-integration surface opens no network listener and binds no port. Both properties enforced by committed gates shaped like the existing import-isolation tests — an egress path reachable without opt-in fails CI.

**Cost Efficiency**

- **NFR-C1:** A baseline full audit costs a bounded fraction of the audited repo's build cost (tracked target ≤10–20% baseline; ~1% for V2 incremental diff-scoped runs). V1 measures and reports the baseline.
- **NFR-C2:** An audit never exceeds its declared budget ceiling; on exhaustion it halts deterministically with no silent overrun.
- **NFR-C3:** Deterministic, zero-token tools perform breadth so LLM spend is reserved for depth.

**Reliability & Honest Degradation**

- **NFR-R1:** A tool/parse failure or unestablishable-traceability condition degrades to a recorded finding or coverage downgrade — never an uncaught crash or a fabricated result.
- **NFR-R2:** An interrupted audit is fully resumable from on-disk `.apaa/` state with no loss of prior coverage.

**Portability**

- **NFR-P1:** APAA runs to completion on the least-capable host (Cline, sequential), producing byte-identical on-disk state to a parallel-capable host; parallel is a pure speedup.
- **NFR-P2:** The audit is stack-agnostic by construction (deep AST-grounding = Python in V1; `claim_emitted` proxy elsewhere); no host- or stack-specific logic in the ledger/verdict core.
- **NFR-P3:** **The default public installation grounds the languages the tool claims to support.** *(Added 2026-08-10b.)* A user installing through the primary public channel and auditing a documented supported language receives that language's grounding without discovering an optional extra. Coverage degraded by a grammar absent from the default install is a **packaging defect**, not a user error or an honest limitation, and is reported as such. Where a language is deliberately not in the default install, its absence and the reason are stated in the tool's own output at the point the file is downgraded.

**Auditability & Evidence Integrity**

- **NFR-A1:** Every artifact is wrapped in a schema-versioned, content-hashed, prev-hash-chained envelope; schemas evolve additive-only.
- **NFR-A2:** Referential integrity of on-disk state is verifiable (no dangling references). **[Tier B]**
- **NFR-A3:** Every verdict carries a scope statement, materiality bar, disclaimer, and point-in-time stamp.

**Scale Envelope** *(V1 bounds — not user-growth scalability)*

- **NFR-SC1:** V1 audits operate within a bounded context budget (target ≤40 files / 15k LOC per audit unit; hard ceiling ≤60 / 25k); larger repos partition into units. Full 10k → 500k LOC scaling (multi-partition + seam auditor) is V2.

**Maintainability**

- **NFR-M1:** No single source file exceeds **1200 lines**; business logic stays out of entrypoints.
- **NFR-M2:** Frozen contracts are validated (Pydantic v2 + JSON Schema) and evolve additive-only.

**Total NFRs: 23.** Explicitly skipped with justification: *Accessibility* (headless — no UI/WCAG surface); *user-growth scalability* (V1 internal; replaced by NFR-SC1).

### Additional Requirements & Constraints

Requirements that are binding but are not FR/NFR-numbered — these must still trace to epics, and are the most common source of untracked scope:

**C1 — Phase / tier constraints**

- V1 has two grades: **Tier A** (demo-grade) and **Tier B** (validation-grade). Tier B is the *engineering precondition* for the ≥80%-precision gate — necessary, not sufficient. PRD states Tier B is delivered.
- **Cut-order** (pre-agreed): non-negotiable core never cut = envelope + finding/ledger/verdict + verdict gate + vacuous detector + 2 cartridges + cost ceiling. The cut-order's V1.5 slot is recorded as **vacant** — nothing slid.
- **V1.5 is defined as the first public distribution**, adding no new assurance capability: reach (public index, marketplace action, agent-integration surface) + usability (actionable output, default-install grounding, reproducible re-runs) + opt-in depth (FR36) + honesty (FR34).

**C2 — Business / gate constraints**

- **≥80% finding-precision gate before any *attested* externalization. Status: NOT CLEARED.** `protocol_cleared` is `False` and has never been `True`; corpus is **N=1 and self-referential**. Clearing is scoped as **Epic 13**.
- The Minions dogfood **no longer counts toward N** — Story 8.5 re-derived it as a self-audit of `argus/`; the independent run "can never be re-derived in this repository."
- A free public release may precede the gate **only** under FR34's two binding conditions: enforced mechanical disclosure **and** a committed in-flight programme to clear the gate. Absent either, the bar is absolute.
- Usage is not evidence — adoption cannot advance the precision gate; only adjudicated findings can.
- Validation protocol is itself a V1 deliverable (who validates, expert-hours/repo, precision-adjudication method, per-metric pass/fail).

**C3 — Architectural / classification constraints (binding on implementation)**

- **Headless-only.** No UI, no editor extension, no language server, no rendered surface.
- **Hosted network surfaces remain V4** — hosted repo-URL runner, HTTP API, endpoints, auth, rate-limits, published SDK, API versioning are all out of V1/V1.5.
- The V1.5 local agent-integration surface is bounded by **four binding constraints**: (1) local stdio transport only, no listener, no port; (2) no HTTP stack — `argus.* ⊬ fastapi` import-isolation gate holds unchanged and ADR #20's classification is preserved verbatim; (3) no new authority — same pure path, same work-manifest boundary; (4) no credential handling.
- Filesystem-as-contract substrate: all state under `.apaa/` (`state/ · assignments/ · findings/ · decisions/`); stateless auditors coordinate only through files.
- Sequential-canonical execution; parallel must be byte-identical.
- Schemas evolve **additive-only**; `severity.rubric` is a V1 config constant, not a frozen schema.
- `partition_id` reserved in the coverage ledger (always `"root"` in V1) for the V2 seam auditor.
- **Frozen invariant:** curated memory (G3, V4) never touches the verdict/decision path.
- V1 schema set: `envelope`, `finding` ①, `severity.rubric` ②, `coverage_ledger` ③, `verdict` ⑧, `decision_record` ④ (minimal) + referential-integrity lint.
- `standards_refs[]` field (format-validated, e.g. `^CWE-\d+$`) + **CWE required on every security-category finding**.
- Every verdict ships `scope_statement`, materiality bar, `disclaimer`, point-in-time stamp — non-negotiable liability surface (M2).

**C4 — Distribution constraints (V1.5, amended 2026-08-10b)**

- In scope: **PyPI** (`pip install argus-agent`, primary channel); **GitHub Marketplace** composite action — *in scope but **gated** on the `action.yml` input-interpolation fix*; **MCP server** as an entry point in the same distribution; **assistant command assets**.
- **Deferred, not rejected:** desktop application stores — requires MSIX/equivalent, bundled runtime, store identity, published privacy-policy URL, age rating; **none exists**. Reopening requires un-skipping `store_compliance` first.
- **Deferred:** OS package managers (Winget / Chocolatey / Homebrew / Snap) — each adds an independent packaging and update contract with no current owner.
- `store_compliance` is **conditionally skipped with a pre-committed reopening condition**: it must be un-skipped and scoped *before any desktop-store channel enters a sprint*. Recorded so the decision cannot be made implicitly by a packaging story.

**C5 — Resolved open inputs (closed 2026-08-10b)**

| Input | Resolution |
|---|---|
| Team headcount | Moot — agent-driven delivery; expert-hours at gates budgeted ≤4 per full adjudication run. |
| Budget-ceiling `$X` | **OI3, LOCKED — "there is no default."** `ceiling_credits: int \| None`, no numeric default, `None` = no ceiling, `0 → None`. A numeric default deliberately refused. |
| `N` for validation set | **Assigned, not answered — owned by Story 13.1.** PRD §Validation Approach (`N ≈ 5–10` real repositories) and `precision-validation-protocol.md` §5 (`N ≥ 5` labeled cartridges) specify **different corpora** and were never reconciled. 13.1 decides which governs and amends the loser. |

**C6 — Measured dependency deliberately left open (Journey 6)**

Whether a default-path vacuous finding is verdict-blocking or advisory-only is recorded as **a measurement, not a design choice**. Heuristic-only findings are advisory by contract; verdict-eligibility requires AST grounding. **Epic 12's deep-audit story owns the measurement and must record it as a yes or a no. A "no" escalates; it does not soften Journey 6.**

**C7 — Journey-forced capabilities** (from §Journey Requirements Summary — the PRD's own traceability table)

Headless invocation contract (J1,J5) · stack detection + partitioning (J1,J2) · coverage ledger + AST-grounded deep claims (J1,J3) · vacuous-test detector (J1) · negative-assurance verdict (J1,J4,J5) · `INSUFFICIENT_COVERAGE` floor + honest degradation (J2,J3,J5) · budget ceiling (J2,J3) · deterministic verdict + exit-code wire contract (J3,J5) · CI integration as headless gated step (J3,J5) · evidence bundle + redacted excerpts + source-retention (J4) · resumability (J2) · defect cartridges/self-audit (all) · **agent-integration surface (J6)** · **actionable terminal output (J6)** · **mandatory self-disclosure (J6)**.

### PRD Completeness Assessment

**Strong — this PRD is unusually complete and internally disciplined.** Specific observations carried into coverage validation:

1. **Requirement numbering is contiguous and unambiguous.** FR1–FR37 with no gaps, no duplicates, no re-used numbers across amendments. NFRs use a typed prefix scheme (D/S/C/R/P/A/SC/M) that is stable. This makes traceability mechanically checkable rather than a judgment call.
2. **Every requirement is stated as a capability, not an implementation.** The FR list reads as a binding capability contract with an explicit closure clause. This is the correct altitude and it means an epic that implements a *mechanism* without the *capability* is a genuine miss, not a stylistic quibble.
3. **The 2026-08-10b amendment is the risk surface.** Four FRs (34–37) and two NFRs (S6, P3) were added on the same day as the epics rewrite, roughly 20 minutes apart. These are the requirements most likely to be under-covered, and FR34/FR37 in particular carry *mechanically enforced* obligations (a committed test that fails on an unenumerated surface/outcome) that an epic can easily state as prose without committing to the enforcing test.
4. **Several binding obligations live outside the FR/NFR lists** — C1–C7 above. The `store_compliance` reopening condition, the marketplace-action gating on the `action.yml` fix, the Epic 12 measurement obligation (C6), and the Story 13.1 corpus reconciliation are all binding but unnumbered. Unnumbered obligations are the classic traceability leak and will be checked explicitly.
5. **Honest self-reporting is intact.** The PRD does not claim the precision gate is cleared, does not count the dogfood toward N, and records `protocol_cleared: False`. There is no over-claim to unwind — a rare and good starting position for a readiness gate.
6. **One internal tension is already flagged by the PRD itself and left unresolved by design:** the `N ≈ 5–10 real repositories` vs `N ≥ 5 labeled cartridges` conflict (C5). The PRD assigns it rather than answers it. This is acceptable *only if* Story 13.1 genuinely exists and owns it — to be verified in Step 3.
7. **No UX requirements exist and none are implied.** `ux_ui`, `visual_design`, and `user_journeys` are explicitly in `skipSections`; the journeys that do exist are operator/system workflows. UX assessment is correctly NOT APPLICABLE.

**Assessment: PRD is READY as an input to coverage validation.** No requirement is too vague to trace. The open items are assigned rather than missing, and the assignments name their owning story.

## Step 3 — Epic Coverage Validation

**Source read:** `epics.md` (169,675 bytes / 2,516 lines) in full — base breakdown (Epics 1–7), the 2026-08-03 Amendment Delta (Epics 8–9), the 2026-08-09/08-10b additions (Epics 10–13), and the Minions-Repo Handoff.

**Structure found.** The document is a base plan plus two appended deltas. It carries **three** traceability indexes, not one:

1. `§Requirements Inventory → §FR Coverage Map` (lines 253–292) — the canonical map, FR1–FR33.
2. `§Delta Requirements Coverage Map` (lines 1334–1363) — DR/RS/IN requirements for the 08-03 delta.
3. Per-epic inline `**Covers:**` declarations — the only place Epics 10–13 record what they satisfy.

That third channel is where the 2026-08-10b requirements live, and it is the source of the defect recorded below.

### Coverage Matrix

| FR | PRD Requirement (abbrev.) | Epic Coverage | Status |
|---|---|---|---|
| FR1 | Headless repo intake @ pinned commit | Epic 1 (1.4, 1.7) | ✓ Covered |
| FR2 | Stack/toolchain auto-detection | Epic 1 (1.4) | ✓ Covered |
| FR3 | Bounded-unit partitioning ≤40 files/15k LOC | Epic 2 (2.4) | ✓ Covered |
| FR4 | Critical-subsystem identification + designation *(amended 08-03)* | Epic 2 (2.3) + **Epic 8 (8.2)** for the amendment | ✓ Covered |
| FR5 | Fixed-enum coverage ledger | Epic 1 (1.2) | ✓ Covered |
| FR6 | Claim-required `audited_deep` (silence→shallow) | Epic 1 (1.2) | ✓ Covered |
| FR7 | Python AST-grounding of deep claims **[Tier B]** | Epic 6 (6.2) | ✓ Covered |
| FR8 | `inferred` never satisfies a gate | Epic 2 (2.1) | ✓ Covered |
| FR9 | Readable per-file depth ledger | Epic 2 (2.2) | ✓ Covered |
| FR10 | Heuristic vacuous-test detector (advisory) | Epic 1 (1.5) | ✓ Covered |
| FR11 | Hardcoded-secret detection + redaction | Epic 2 (2.5) | ✓ Covered |
| FR12 | Orphan/dead-code detection **[Tier B]** | Epic 6 (6.3) | ✓ Covered |
| FR13 | Locator-required findings (or reject) | Epic 1 (1.6) | ✓ Covered |
| FR14 | Tool-failure → finding, not crash | Epic 2 (2.6) | ✓ Covered |
| FR15 | Pure-function verdict over the ledger | Epic 1 (1.6) | ✓ Covered |
| FR16 | Coverage gates + 4-row decision table *(amended 08-03)* | Epic 1 (gate+floor) + Epic 2 (critical clause) + Epic 3 (floor under exhaustion) + **Epic 8 (8.1, 8.3)** | ✓ Covered |
| FR17 | Negative-assurance verdict semantics | Epic 4 (4.1) | ✓ Covered |
| FR18 | Deterministic exit code + machine-readable artifact | Epic 1 (1.6, 1.7) | ✓ Covered |
| FR19 | Adversarial Prosecutor pass **[Tier B]** | Epic 6 (6.4) | ✓ Covered |
| FR20 | Defect-cartridge self-audit (CI-asserted) | Epic 6 (6.5) | ✓ Covered |
| FR21 | Operator-set budget ceiling | Epic 3 (3.1) | ✓ Covered |
| FR22 | Halt→skip→downgrade→report on exhaustion | Epic 3 (3.2, 3.3) | ✓ Covered |
| FR23 | HITL STOP/PROCEED, default-STOP, time-boxed | Epic 6 (6.7) — ⚠️ **wiring swept by Story 10.5** | ⚠️ Covered, reachability under review |
| FR24 | Append-only decision record **[Tier B]** | Epic 6 (6.7) | ✓ Covered |
| FR25 | Content-hashed, schema-versioned envelope | Epic 1 (1.1) | ✓ Covered |
| FR26 | Referential-integrity lint **[Tier B]** | Epic 4 (4.2) | ✓ Covered |
| FR27 | Reproducible verdict (memoization) | Epic 5 (5.1–5.3) built + **Epic 12 (12.3)** wired | ✓ Covered |
| FR28 | No source/secret bytes in artifacts | Epic 2 (2.5 producer) + Epic 4 (4.4 containment) | ✓ Covered |
| FR29 | Evidence-bundle export (no source retention) | Epic 4 (4.3) | ✓ Covered |
| FR30 | Headless invocation contract | Epic 1 (1.7) + **Epic 10 (10.3)** contract reconciliation | ✓ Covered |
| FR31 | Resume from `.apaa/` state | Epic 3 (3.4) | ✓ Covered |
| FR32 | Sequential byte-identical execution | Epic 3 (3.5) | ✓ Covered |
| FR33 | Verdict-impact finding ordering | Epic 1 (1.6) | ✓ Covered |
| **FR34** | **Self-disclosure of validation status on every verdict surface** | **Epic 11 (11.1)**, reasserted in 12.6 + 12.9; removal path in Epic 13 (13.3) | ⚠️ **Covered by story, ABSENT from the FR Coverage Map** |
| **FR35** | **Local agent-integration surface (MCP + command assets)** | **Epic 12 (12.6, 12.7)** | ⚠️ **Covered by story, ABSENT from the FR Coverage Map** |
| **FR36** | **Opt-in LLM-backed deep-audit pass** | **Epic 12 (12.2)** | ⚠️ **Covered by story, ABSENT from the FR Coverage Map** |
| **FR37** | **Every terminal outcome names its next action** | **Epic 12 (12.4)** | ⚠️ **Covered by story, ABSENT from the FR Coverage Map** |

**NFR coverage (23 total):**

| NFR | Epic Coverage | Status |
|---|---|---|
| NFR-D1 | Epic 5, delivered via Epic 12 (12.3) | ✓ Covered |
| NFR-D2, D3 | Epic 1; re-asserted Epic 8 | ✓ Covered |
| NFR-S1 | Epic 4 (4.4) | ✓ Covered |
| NFR-S2 | Epic 2 (2.5) | ✓ Covered |
| NFR-S3 | Epic 4 (4.3) | ✓ Covered |
| NFR-S4 | Epic 2 (2.4) | ✓ Covered |
| NFR-S5 | Epic 1 (1.3) | ✓ Covered |
| **NFR-S6** | **Epic 12 (12.2 ACs — off-by-default, pre-egress disclosure, committed gate)** | ⚠️ **Covered by AC, ABSENT from the NFR inventory** |
| NFR-C1, C2 | Epic 3 (3.1, 3.2) | ✓ Covered |
| NFR-C3 | Epic 2 (2.6) | ✓ Covered |
| NFR-R1 | Epic 2 (2.6); re-asserted Epic 11 (11.4), Epic 12 (12.2, 12.8) | ✓ Covered |
| NFR-R2 | Epic 3 (3.4) | ✓ Covered |
| NFR-P1 | Epic 3 (3.5) | ✓ Covered |
| NFR-P2 | Epic 6; amended by Epic 10 (10.2) | ✓ Covered |
| **NFR-P3** | **Epic 12 (12.5)** | ⚠️ **Covered by story, ABSENT from the NFR inventory** |
| NFR-A1 | Epic 1 (1.1) | ✓ Covered |
| NFR-A2 | Epic 4 (4.2) | ✓ Covered |
| NFR-A3 | Epic 4 (4.1) | ✓ Covered |
| NFR-SC1 | Epic 2 (2.4) | ✓ Covered |
| NFR-M1 | Epic 1; **enforced repo-wide by Epic 12 (12.1)** | ✓ Covered |
| NFR-M2 | Epic 1; re-asserted Epic 8 | ✓ Covered |

### Missing Requirements

**No FR and no NFR is without an implementing epic.** Every one of the 37 FRs and 23 NFRs traces to at least one epic and, for Epics 1–13, to a named story. There are **no orphan requirements** and **no epics claiming coverage of an FR that does not exist in the PRD**.

What *is* missing is **the traceability record itself**, and on an assurance product whose entire thesis is *"honesty is mechanical, not promised,"* that is not a clerical matter.

#### ❌ CRITICAL — the canonical FR Coverage Map is stale by four requirements

`epics.md:253-292` maps FR1–FR33 and closes with: *"**All 33 FRs mapped. All 21 NFRs land in ≥1 epic**."* The PRD now carries **37 FRs and 23 NFRs**. Four FRs and two NFRs never entered the map:

| Requirement | Actually covered by | Present in the FR Coverage Map? | Present in the epics' Requirements Inventory? |
|---|---|---|---|
| FR34 | Story 11.1 | ❌ No | ❌ No |
| FR35 | Stories 12.6, 12.7 | ❌ No | ❌ No |
| FR36 | Story 12.2 | ❌ No | ❌ No |
| FR37 | Story 12.4 | ❌ No | ❌ No |
| NFR-S6 | Story 12.2 | ❌ No | ❌ No |
| NFR-P3 | Story 12.5 | ❌ No | ❌ No |

- **Root cause, confirmed by the change record itself.** The 2026-08-10b delta note in `sprint-status.yaml` enumerates exactly what it amended: *"PRD (22 substitutions incl. the frontmatter amendments entry; **FR count 33 → 37**; NFR-S6 + NFR-P3 added), architecture (10 substitutions), **epics.md (Story 10.2 AC1 → 10 sites + closing grep test; Story 10.5 added; Epics 11/12/13 written in full — 22 stories across 4 epics)**, and this file."* The PRD's own count was corrected 33→37; the `epics.md` edit list covers stories and epics only. **The Requirements Inventory and FR Coverage Map were never in scope of the amendment.** This is not an oversight discovered by inference — the amendment's own manifest shows the index layer was skipped.
- **Impact:** The document's own index contradicts its content. Anyone validating coverage from the map — which is what a map is for — concludes the plan covers 33 FRs and would not discover FR34–FR37 exist. The 2026-08-10b amendment added the requirements to the PRD and added *stories* to the epics, but never updated the *inventory or the map* that sit between them. The risk is not that the work is unplanned; it is that the next amendment, retrospective, or readiness gate reads a map that under-reports the contract by four requirements — and FR34 in particular is the requirement that keeps a legally-exposed disclosure attached to a public release.
- **Recommendation:** Extend `§Requirements Inventory` (FR + NFR lists) and `§FR Coverage Map` to FR1–FR37 / 23 NFRs, mapping FR34→Epic 11, FR35/FR36/FR37→Epic 12, NFR-S6→Epic 12, NFR-P3→Epic 12. This is an edit to `epics.md`, not new delivery scope.

#### ❌ HIGH — three stale count assertions repeat the same error

| Site | Says | Should say |
|---|---|---|
| `epics.md` frontmatter `driver_namespace` (L52) | *"1:1 onto PRD **FR1–33** / NFR clusters"* | FR1–37 |
| `epics.md:62` (primary sources) | *"`E-PRD/prd.md` (**33 FRs / 21 NFRs**)"* | 37 FRs / 23 NFRs |
| `epics.md:1064` Final Validation Summary | *"**all 33 FRs** map to a story"* / *"all **21 NFRs**"* | all 37 FRs / all 23 NFRs |

- **Impact:** The Final Validation Summary is the artifact a reader trusts when asking *"was this plan validated?"* It currently asserts a completed validation over a requirement set four FRs smaller than the one in force. It is a true statement about a superseded contract presented as a current one — the precise defect class Epic 8 and Story 10.1 exist to eliminate. Leaving it is inconsistent with the standard this plan holds itself to.
- **Recommendation:** Update all three in the same edit as the coverage map, and date the correction rather than silently rewriting it (§3.4 evidence immutability, the convention this repo already follows).

#### ⚠️ MEDIUM — the epics' "Open delivery inputs" block contradicts the PRD's closed resolutions

`epics.md:227-244` still records OI1–OI3 as **LOCKED 2026-06-18** in terms the PRD superseded on 2026-08-10b:

| Input | epics.md (L227-244) | PRD (§Open inputs, closed 08-10b) | Conflict |
|---|---|---|---|
| **OI1** — validation-set `N` | *"LOCKED `N = 5` (V1 gate floor), **Minions first**"* | **Assigned to Story 13.1**, unreconciled between two corpora; **Minions explicitly excluded from N** | ❌ Direct — epics assert a locked value and a corpus the PRD has since disqualified |
| **OI3** — budget ceiling `$X` | *"DEFERRED to empirical Story 7.1 sizing"* | **LOCKED — "there is no default"**; `ceiling_credits: int \| None`, `0 → None`, numeric default deliberately refused | ❌ Direct — "deferred" vs "locked with a resolution" |
| **OI2** — dogfood scope | *"LOCKED full-repo multi-partition"* | Unchanged | ✓ Consistent |

- **Impact:** Story 13.1 is *written* to resolve the OI1 conflict, so the delivery path is sound. But a story reading the epics' inventory block for context gets `N = 5, Minions first` — a value the PRD retired and a corpus Story 13.1 is required to exclude. The same block would tell a budget story that OI3 is open when it is locked. Both are context-poisoning for the just-in-time story creation this project uses (`bmad-create-story` reads these documents).
- **Recommendation:** Amend the OI1 and OI3 entries in place, pointing OI1 at Story 13.1 and recording OI3's locked resolution, each dated 2026-08-10b.

#### ✓ RESOLVED ON VERIFICATION — the `store_compliance` reopening condition

Raised as a candidate gap because `epics.md` contains **zero** occurrences of `store_compliance`, `Winget`, `Chocolatey`, `Homebrew`, or any desktop-store term, while the PRD pre-commits that the skip *"must be un-skipped… before any desktop-store channel enters a sprint."*

**It is recorded — in `sprint-status.yaml`, twice, and with the operator's scope decision attached:** *"SCOPE NARROWED FROM THE ORIGINAL ASK: the operator opened with Microsoft Store and other desktop software stores. Channels for THIS release are PyPI + GitHub Marketplace only. Desktop app stores, OS package managers (Winget/Chocolatey/Homebrew) and a hosted runner are DEFERRED, not rejected — recorded at PRD L317. The `store_compliance` PRD skip (L340) was re-validated and REMAINS CORRECT under the narrowed scope; **it must be un-skipped before any desktop-store channel is scoped**."* Restated again under the 08-10b delta note.

**Not a gap.** The guard has a home in the document the sprint actually executes from. `epics.md` not carrying it is acceptable — it is a channel-scope constraint, and `sprint-status.yaml` is where channel scope is governed.

#### ✓ Verified NOT gaps (checked, and correctly handled)

These looked like gaps and are not — recorded so the next reviewer does not re-open them:

- **`standards_refs[]` + CWE-on-security-findings** — committed to V1 Core in §Product Scope but backed by **no FR**. Not an oversight: **Story 10.5** adjudicates it explicitly, requires a dated decision either way, and forbids leaving the two sections in disagreement. It further mandates a sweep for other §Product Scope V1 items missing from FR1–37.
- **FR23 (HITL escalation) reachability** — delivered as a library seam nothing in `pipeline.py` or `cli.py` invokes (DF-6-7-A). Caught: **Story 10.5** sweeps FR1–37 for requirements with no reachable production call site and decides FR23 **by name**.
- **Epics 10–13 have no story files yet** — 41 story files exist, covering Epics 1–9 exactly (E1:7, E2:6, E3:5, E4:4, E5:3, E6:7, E7:2, E8:5, E9:2). The 22 stories of Epics 10–13 are defined in `epics.md` with full ACs but not yet expanded by `/bmad-create-story`. That is the intended just-in-time flow, not a coverage gap. Epic/story counts reconcile exactly with the 63 keys in `sprint-status.yaml`.
- **The V1.5 Journey-6 measurement (C6)** — Story 12.2 owns it, must record a yes-or-no, and is bound to escalate a "no" rather than soften Journey 6. Story 12.4 is explicitly coupled to that measurement's result.
- **Marketplace channel gating (C4)** — Story 11.3 is named a hard precondition, and Story 12.9 independently re-asserts that the marketplace channel does not ship without it. Covered twice, deliberately.

### Coverage Statistics

| Measure | Value |
|---|---|
| Total PRD FRs | **37** |
| FRs with an implementing epic **and** named story | **37** |
| **Functional coverage** | **100%** |
| FRs recorded in the canonical FR Coverage Map | **33 of 37** |
| **Traceability-record completeness** | **89.2%** (4 FRs undocumented in the map) |
| Total PRD NFRs | **23** |
| NFRs with an implementing epic | **23** |
| **Non-functional coverage** | **100%** |
| NFRs recorded in the epics' NFR inventory | **21 of 23** |
| **NFR traceability-record completeness** | **91.3%** |
| Epics defined | **13** |
| Stories defined in `epics.md` | **63** |
| Stories reconciling with `sprint-status.yaml` | **63 of 63 (exact)** |
| Story spec files created | **41** (Epics 1–9; Epics 10–13 pending just-in-time creation) |
| Requirements in epics but **not** in the PRD | **0** |

**Step 3 verdict (see below for the UX and quality steps): coverage is complete; the coverage *record* is not.** No requirement is unplanned. Four FRs, two NFRs, and three summary assertions are stale in the index layer of `epics.md`. All are document edits, not delivery scope, and none blocks implementation — but the Final Validation Summary should not continue to certify a 33-FR contract while 37 are in force.

## Step 4 — UX Alignment Assessment

### UX Document Status

**NOT FOUND — and correctly so. Verified, not assumed.**

`find` over the entire artifact tree for `*ux*`, `*design-spec*` returns nothing. Rather than accept the absence, I tested the three implication conditions the step requires:

| Test | Finding | Verdict |
|---|---|---|
| **Does the PRD mention a user interface?** | Yes — **only to exclude it.** `classification.headless: true`; `skipSections: [ux_ui, visual_design, user_journeys]`; *"Headless-only — verdicts and evidence are artifacts and machine surfaces, **never screens** (no UI/UX)"*; *"APAA ships **no editor extension, no language server, and no rendered surface**"* | No UI implied |
| **Are web/mobile components implied?** | No. Hosted repo-URL runner, HTTP API, endpoints, auth, rate-limits, SDK and API versioning are all explicitly **V4**. The exclusion is not merely stated — it is **mechanically enforced** by the committed import-isolation gate `argus.* ⊬ fastapi/uvicorn/starlette` (`tests/apaa/test_no_web_imports.py`, architecture L114/L417/L656) | No web surface possible |
| **Is this a user-facing application?** | **Yes — text-facing, not screen-facing.** This is the one that needed real scrutiny, and it is the substance of this step (below) | UX spec still not applicable |

**Both PRD skips were re-validated on 2026-08-10b against the new V1.5 channel set**, with reasoning recorded: `visual_design` — *"no rendered surface is introduced. The agent-integration surface is a protocol and a set of config files"*; `store_compliance` — conditionally skipped with a pre-committed reopening condition. This is a dated re-validation, not an inherited assumption carried forward unexamined — the failure mode this step exists to catch.

### The finding that matters: the human-factors surface grew in V1.5, and it landed in the right place

The 2026-08-10b amendment introduced a **tertiary human persona** (Sam, the independent developer, Journey 6) whose success bar is explicitly **"unassisted first-run utility — not because the user is inexperienced, but because there is no one to ask."** That is a usability requirement in substance. A naive reading would flag "new human persona + no UX doc" as a gap.

It is not a gap, because the requirements landed as **binding FRs and story ACs** rather than as a UX specification:

| Human-factors need (Journey 6) | Where it landed | Architecture support |
|---|---|---|
| No dead ends — every outcome names its next action | **FR37** → Story 12.4, enumerated in a test that fails on an unenumerated outcome | `argus/reports/plain_english.py` + `argus/reports/generator.py` — the two verdict-rendering surfaces, both already known to the architecture and both reconciled by Epic 8 / DR-11 |
| Reachable from the coding agent | **FR35** → Stories 12.6, 12.7 | `argus/mcp/**` declared an **adapter layer** — *"impure wiring, no audit logic, and no second decision path"* (architecture L631-634, L272-303) |
| Works on their stack out of the box | **NFR-P3** → Story 12.5 | Architecture L446 records this as an **open packaging decision owned by Story 12.5** — the 9 non-Python grammars are currently an optional extra, so the default install grounds Python only, which NFR-P3 classifies as a packaging defect |
| Free and private by default | **NFR-S6** → Story 12.2 | Architecture L381-388: deep audit off by default; default path zero-token/offline; egress disclosed before the first byte; committed gate |
| Honest about the instrument | **FR34** → Story 11.1 | Architecture L158-173: the **run grade vs. instrument status** distinction is modelled explicitly, and FR34 *"extends the existing guard, never a second mechanism"* |
| Self-explaining CLI / errors / first-run doc | Story 12.8 (`--help` parity, error diagnosis, lean first-run page) | Existing CLI surface; no new component needed |

**This is the correct design.** For a headless tool, output design belongs in the requirements contract where it can be pinned by a test — not in a UX document that no CI gate reads. FR37's *"enumerated in a test that fails on an unenumerated outcome"* is a stronger usability guarantee than any wireframe, and it is exactly the mechanism the product's own thesis demands. **CLAUDE.md §3.7 forbids authoring a UX specification here, and authoring one would be the wrong call regardless.**

### Alignment Issues

**UX ↔ PRD:** Not applicable — no UX document exists and none is required. No PRD requirement depends on a missing UX artifact.

**UX ↔ Architecture:** Not applicable in the conventional sense. In its place I validated **human-facing-surface ↔ architecture** alignment, and the architecture accounts for every V1.5 surface: the MCP adapter layer is defined with its purity constraints, both report-rendering surfaces are known and reconciled, the disclosure mechanism is specified as an extension of an existing guard, and the grammar-packaging question is explicitly assigned rather than assumed. **No V1.5 human-facing surface is unsupported by the architecture.**

### Warnings

- ⚠️ **`architecture.md` carries the same stale requirement counts as `epics.md`.** L40 reads *"Functional Requirements (**33**)"* and L48 *"Non-Functional Requirements (**21**)"*, while L467 — updated on 08-10b — correctly reads *"mapped 1:1 onto the PRD **FR1–37** / NFR clusters (FR34–37 added 2026-08-10b)."* The document contradicts itself: its driver-namespace line knows about 37 FRs, its Requirements Overview still describes 33 and enumerates only eight clusters ending at FR32. Same defect class as the Step 3 CRITICAL finding, now confirmed in a second document. **Carried into Step 5.**
- ⚠️ **NFR-P3 is the one V1.5 human-factors requirement whose architecture position is *open*, not settled.** Architecture L446-447 records the default install grounds **Python only** while the tool documents 10 languages — precisely the state NFR-P3 declares a packaging defect. The requirement, the defect, and the owning story (12.5) are all correctly recorded, so this is *tracked*, not missed. Flagging it because it is the only place where the architecture states an unresolved position on a shipped-capability question rather than a decision.
- ✅ **No warning issued for the absent UX document.** UX is not implied; the exclusion is enforced mechanically rather than by convention; and the human-factors requirements the V1.5 scope genuinely introduced are all present as testable FRs with architecture support.

### UX Assessment Result

**NOT APPLICABLE — no gap.** The absence of UX documentation is correct for this product, was re-validated with dated reasoning at the last amendment, and is backed by a CI gate that makes a rendered surface impossible to introduce accidentally.

## Step 5 — Epic Quality Review

Validated all **13 epics / 63 stories** against `create-epics-and-stories` standards: user value, epic independence, forward dependencies, story sizing, AC quality, and starter/greenfield handling.

### Epic Structure Validation

#### A. User Value Focus

| Epic | Title shape | User outcome stated? | Verdict |
|---|---|---|---|
| 1 | Signature-Demo Vertical Slice — "the false-green catch" | Integrator gets a coverage-grounded 🔴 + exit code | ✅ Value |
| 2 | Full Coverage Ledger & Defect Detectors | Eng Lead can read what was examined; secrets detected | ✅ Value (component-shaped title) |
| 3 | Honest Degradation & Cost Governance | Operator bounds cost; tool halts honestly | ✅ Value |
| 4 | Negative-Assurance Verdict & Evidence Bundle | Dana gets regulator-showable evidence (J4) | ✅ Value |
| 5 | Reproducible Verdict & Memoization | Marcus gets a dashboard number that doesn't flake (J3) | ✅ Value |
| 6 | Trust Substrate — Self-Audit, Prosecutor & Precision | "Proven, not asserted, depth" — the moat | ⚠️ Borderline (see below) |
| 7 | Minions Dogfood Proof Run | Answers the strategic question with an artifact | ⚠️ Proof epic, not capability |
| 8 | The Honest Verdict — no block without a finding | Operator stops being falsely accused | ✅ Excellent |
| 9 | Make Argus Consumable — stand alone, then ship a release | Integrator can depend on a real artifact | ✅ Value |
| 10 | Specification Debt from the Separation | Governance/debt epic | ⚠️ Borderline (see below) |
| 11 | Release Integrity — nothing unsafe or untrue can be published | External user is safe from the tool | ✅ Excellent |
| 12 | The Useful Tool — what a developer gets on the first run | Sam gets a tool worth installing (J6) | ✅ Excellent |
| 13 | Earn the Gate — remove the disclosure by measuring | Business: attested externalization unlocked | ✅ Value |

**No epic is a bare technical milestone.** There is no "Setup Database," no "API Development," no "Infrastructure Setup." Even the two borderline cases carry an explicit user-facing thesis: Epic 6's is *"proven, not asserted, depth"* (the moat the PRD names as the durable differentiator, delivering six FRs), and Epic 10's is *"the release gate refuses a verdict it cannot evidence"* — a debt epic named honestly rather than disguised as feature work.

**Epic 7 is a proof/validation epic, not a capability epic.** Normally a red flag. Here it is the PRD's own §Success-Criteria deliverable (*"the last thing cut — it **is** the proof"*), so it is scope the product explicitly bought. Accepted.

**Observation worth recording:** epic *titles* improve markedly from Epic 8 onward — Epics 1–7 are component-shaped (*"Full Coverage Ledger & Defect Detectors"*), Epics 8–13 are outcome-shaped (*"The Honest Verdict — no block without a finding"*). The later convention is the better one.

#### B. Epic Independence Validation

Every declared dependency was traced. **Result: zero forward dependencies at epic level.**

```
1 (standalone) → 2 → 3 → 4 → 5 → 6 → 7 (capstone, needs 1–6)
8 (standalone, "requires no later epic") → 9 → 10 → 11 → 12 → 13
```

- Epic 1 stands alone completely and ships a working (narrow) auditor — the architecture's *"thin vertical slice, NOT a horizontal scaffolding epic"* constraint is honoured.
- Epic 8 is explicitly declared **"Standalone: yes — requires no later epic,"** correctly re-basing the second chain.
- Epic 12 depends on Epics 10 **and** 11 *in full* (all ten stories) — heavy, but strictly backward.
- **No circular dependencies. No epic requires Epic N+1 to function.**

### Story Quality Assessment

#### A. Acceptance Criteria Review

**AC quality is exceptionally high and materially above the standard this checklist assumes.** Every story across all 13 epics uses Given/When/Then. ACs routinely cite `file:line`, name the exact test that pins the behaviour, and state measured counts rather than estimates (*"five action-input sites… the ledger named only `:127`"*, *"5 of 71 wheel modules fail to import"*, *"it is now 1331 lines"*). Several ACs pre-commit their own falsifiability — *"enumerated in a test that fails on an unenumerated outcome"*, *"pinned in both directions so a stale record goes RED."*

Error and edge conditions are covered systematically, not incidentally: tool failure → finding (2.6), budget exhaustion (3.2), containment escape (1.3), grammar load failure vs. absence (10.4), dirty-tree/re-tag/overwrite on release (9.2, re-proven in 12.9), and a `RELEASE_READY`-specific assertion for the false-green direction (12.4).

**Single AC-quality defect found:**

- 🟡 **Story 4.1, AC 2 is review-based rather than test-based.** *"**Given** the verdict language **When** reviewed **Then** it never implies certification or 'the code is correct'."* "When reviewed" names no reviewer and no mechanism — this is the one AC in 63 stories that cannot be verified mechanically. Notably, **the plan itself later closes this**: Story 11.1 extends `DOGFOOD_EXTERNALIZATION_GUARD` to assert *"over-claim-phrase absence"*, which is the mechanical form of the same guarantee. Recommend back-referencing 11.1 from 4.1 so the guarantee is not read as prose-only.

#### B. Story Sizing Validation

- 🟠 **Story 12.2 is over-scoped.** It delivers FR36 (wire the deep-audit seam), NFR-S6 (off-by-default + pre-egress provider disclosure + a committed no-egress-without-opt-in gate), preserves Story 6.1's determinism quarantine, routes spend through FR21/FR22, **supplies fallback / circuit-breaking / cost-attribution behaviours that architecture §E had justified omitting because they came "for free" from the Minions orchestrator Story 9.1 removed**, *and* carries the absorbed blocking-reachability measurement whose result changes what Story 12.4 must say. That is three separable deliverables — a capability wiring, a resilience-behaviour recovery, and a measurement — in one story. The resilience half in particular is re-implementing something the architecture assumed it would inherit.
  **Recommendation:** split the recovered NFR-R1 resilience behaviours into their own story. They are a distinct risk with distinct failure modes and should not slip silently inside a wiring story.

- 🟠 **Story 12.9 bundles the entire publish event.** Release-status evidence citation, a reviewed scope change to a workflow that documents its own abstention from publishing, marketplace gating on 11.3, FR34 disclosure on both listings, a clean-environment install proof (`--help` + fixture audit + MCP invocation), and re-proving Story 9.2's four release edge cases against a channel 9.2 could not exercise. As the single story that publishes anything, its failure surface is the widest in the plan.

- 🟠 **Story 10.5 carries one adjudication plus two full sweeps** — the `standards_refs` V1/FR conflict, a sweep of §Product Scope V1 Core items missing from FR1–37, and a sweep of FR1–37 for requirements with no reachable production call site (each needing a dated disposition, with FR23 decided by name). Either sweep could independently surface new scope.

- 🟠 **Epic 12 carries 9 stories** — the largest in the plan — and sits last in a chain requiring Epics 10 and 11 complete in full. It is simultaneously the heaviest epic and the most gated.

- 🟡 **Story 6.3 (orphan detector) has a single AC**, thin against its siblings. False-positive control lands in 6.5's clean controls, so coverage exists — but dynamic references and entry points, the classic orphan-detector false-positive sources, are not named anywhere.

**No under-sized or non-story-shaped work found.** No "Setup all models" pattern. No story is an epic in disguise.

#### C. Dependency Analysis (within-epic)

Traced every within-epic ordering constraint. **No story depends on a later story in its own epic.** Declared orderings are explicit and reasoned:

- Epic 8: *"8.1 and 8.2 are each standalone; 8.3–8.5 build only on earlier stories"* — with DR-10 (the dogfood re-derivation) deliberately placed **last** *"so if it slips it slips visibly rather than silently."* That is unusually good planning discipline.
- Epic 10: *"10.1 FIRST — it is the control that would have caught 10.2-10.4."*
- Epic 12: `12.1 FIRST` (hard enabler — `pipeline.py` is 131 lines over the NFR-M1 cap and two wirings land in it), `12.2 EARLY` (its measurement can change 12.4), `12.3` depends on `10.2`, `12.9 LAST`.
- Epic 13: `13.1 → 13.2 → 13.3`, strictly sequential, no parallelism.

**Two forward *references* (not dependencies) found — both benign, both recorded:**

- 🟡 **Story 2.4 AC 3 references Story 6.4** (*"handled only by the Story 6.4 `cross_partition` Prosecutor cut-edge pass"*). The AC itself is a **negative** requirement — *no* cross-partition seam analysis is attempted — so 2.4 is completable without 6.4; the reference is explanatory. Verifiable standalone, but a reader must consult a future epic to understand why.
- 🟡 **Story 11.5 AC 3 defers to Epic 12** — the false README slash-command claim is *"marked as forthcoming with its story reference"* rather than deleted, and Story 12.7 removes the marker. Correct two-step handoff. **Residual risk:** if Epic 12 does not ship, a published README permanently advertises a capability as "forthcoming" that never arrives.

### Special Implementation Checks

**A. Starter template.** The architecture explicitly states there is **no starter template and no project-init story** — the stack is *inherited* from Minions (Python 3.11+, Pydantic v2, pytest, ≤1200-line files) and *"the first story is the thin vertical signature-demo slice… NOT a horizontal scaffolding epic (per the pre-mortem guidance)."* The checklist's "Epic 1 Story 1 must set up the starter" rule **does not apply** and its absence is correct, deliberate, and justified in-document. ✅

**B. Greenfield/brownfield indicators.** Classified greenfield, **brownfield-adjacent in engineering**. Integration points with the existing system are present and thorough (reuse-by-import via AR7; the whole RS-*/IN-* migration set; the Minions-Repo Handoff H1–H4). Migration/compatibility stories exist (DR-8 integrator migration note, the `2`→`3` exit-code shift, additive-only schema evolution). ✅

- 🟠 **CI/CD was established but never verified green until Epic 10.** Story 10.1's own AC records that `sprint-change-proposal-2026-07-28.md` declared *"READY FOR RELEASE"* on a local `pytest` run while `audit-ci.yml`'s **only run on `master` was a `failure`** — and no release workflow existed at all until Story 9.2 (assumption A1, falsified). The plan ran through nine epics on a CI gate that had never passed. The control now exists (10.1 requires a citable run id, and `NOT ESTABLISHED` where there is none), so this is corrected rather than open — but it is the clearest instance of the greenfield "CI/CD early" expectation not being met.

**C. Database/entity creation timing.** No database. The `.apaa/` filesystem tree is the state store and is created in **Story 1.3, when first needed** — not upfront, not all at once. ✅ Correct pattern.

**D. Traceability to FRs.** Maintained in nearly every AC across Epics 1–9 and 11–13.

- 🟡 **Epic 10 traces to the deferred-work ledger, not the FR contract.** Its `**Covers:**` line names `DF-AUD-APAA-C/-D/-E/-F` and *"the `standards_refs` V1/FR conflict"* — no FR. Defensible for a debt epic (its inputs *are* ledger entries), and Story 10.3 does reach FR30 in its ACs, but it means Epic 10's value cannot be validated from the FR contract alone.

### Quality Findings by Severity

#### 🔴 Critical

**None in the epic structure.**

> **Finding withdrawn on verification.** An earlier draft of this step raised Epic 13's ownership as critical, on the strength of the epic header in `epics.md`: *"This epic cannot start without a named human. DF-7-2-A has been open and **unowned since Epic 7**… Story 13.2 does not begin until an adjudicator is named in `sprint-status.yaml`."*
>
> **`sprint-status.yaml` names one.** Under *OWNERSHIP RESOLVED 2026-08-10b*: **DF-7-2-A — ADJUDICATOR NAMED: XAgent007**, filling the Engineering Lead role in `precision-validation-protocol.md` §2, with the record explicitly stating *"Story 13.2's start condition **IS NOW MET**. The ITEM IS NOT CLOSED — an owner is named, the measurement has not run."* Epic 13's own tracker entry repeats it: *"✅ ADJUDICATOR NAMED 2026-08-10b… The start condition that blocked this epic is MET."*
>
> FR34's second condition — a programme *committed and in flight* — is therefore satisfiable, and the publish sequence is sound. What survives is **document drift, not a readiness gap**: `epics.md` still declares the epic unstartable on a condition the tracker records as met. Recorded as **M-7** below.

#### 🟠 Major

| # | Finding | Impact |
|---|---|---|
| **M-1** | **Story 12.2 over-scoped** — FR36 wiring + NFR-S6 egress gates + recovered NFR-R1 resilience behaviours (fallback, circuit-breaking, cost attribution the architecture assumed it inherited before Story 9.1 removed the orchestrator) + the blocking-reachability measurement | Three distinct risks in one story; the resilience half is a re-implementation, not a wiring, and can slip invisibly |
| **M-2** | **Story 12.9 bundles the whole publish event** | Widest failure surface in the plan, in the only story that publishes |
| **M-3** | **Story 10.5 carries two open-ended sweeps** | Either sweep can surface new scope mid-story; an epic sized on the adjudication alone will be wrong |
| **M-4** | **Epic 12 is 9 stories, the heaviest, and the most gated** (needs all of Epics 10 and 11) | Schedule risk concentrated at the end of the chain |
| **M-5** | **Epic 7's capstone proof was invalidated retroactively** — Story 8.5 re-derived the dogfood as a self-audit of `argus/`; the independent Minions run *"can never be re-derived in this repository"*; the ledger calls the replacement *"a materially weaker evidence class… not independent corroboration of anything"* | The PRD's central §Success-Criteria proof no longer exists as delivered. Story 13.1 owns rebuilding the corpus from repositories Argus did not author — but **Epic 7 still reads as delivered proof** to anyone not reading Epic 13 |
| **M-6** | **CI gate unverified through Epics 1–9** (Story 10.1: `audit-ci.yml`'s only `master` run was `failure`; no release workflow until 9.2) | Nine epics of work validated against a gate that had never passed. Control now exists; recorded as corrected-not-open |
| **M-7** | **`epics.md` Epic 13 declares itself unstartable on a condition `sprint-status.yaml` records as MET.** The epic header still reads *"CANNOT START WITHOUT A NAMED HUMAN… unowned since Epic 7"*; the tracker names **XAgent007** as adjudicator (2026-08-10b) and states the start condition **IS NOW MET** | The two governing documents disagree on the single condition gating the public release. A reader of `epics.md` alone concludes the terminal epic is blocked. Same defect class as the Step 3 CRITICAL finding — the 08-10b amendment updated the tracker and left the epic prose behind |

#### 🟡 Minor

| # | Finding |
|---|---|
| **m-1** | Epic 1–7 titles are component-shaped and several stories use an "As an APAA maintainer" persona (1.1, 1.2, 1.3, 4.2, 4.4, 5.1, 6.1, 6.5) rather than a user persona. Justified by the vertical-slice rationale and by Epic 1 delivering value as a whole; Epics 8–13's outcome-shaped convention is the better one |
| **m-2** | Story 4.1 AC 2 is review-based (*"When reviewed"*), the only non-mechanical AC in 63 stories. Later closed mechanically by Story 11.1 — recommend a back-reference |
| **m-3** | Story 2.4 AC 3 forward-*references* Story 6.4 (benign — the AC is a negative requirement and is standalone-verifiable) |
| **m-4** | Story 11.5 leaves a "forthcoming" README claim whose removal depends on Epic 12 shipping |
| **m-5** | Epic 10 traces to `DF-*` ledger entries rather than to FRs |
| **m-6** | Story 6.3 (orphan detector) has a single AC; dynamic references and entry points — the standard orphan false-positive sources — are not named |

### Best Practices Compliance Checklist

| Check | Result |
|---|---|
| Epic delivers user value | ✅ 11 clear, 2 borderline-but-justified (Epics 6, 10); Epic 7 is a sanctioned proof epic |
| Epic can function independently | ✅ Zero forward dependencies; two clean chains (1→7, 8→13); Epic 8 explicitly re-bases |
| Stories appropriately sized | ⚠️ 3 over-scoped (12.2, 12.9, 10.5), 1 thin (6.3); the other 59 are well-sized |
| No forward dependencies | ✅ None. Two forward *references*, both benign and declared |
| Database tables created when needed | ✅ N/A — `.apaa/` tree created in Story 1.3 at first need |
| Clear acceptance criteria | ✅ Given/When/Then throughout, with `file:line` citations, measured counts, and named pinning tests. 1 defect in 63 stories |
| Traceability to FRs maintained | ✅ In ACs. ⚠️ The index layer is stale (Step 3 CRITICAL); Epic 10 traces to the debt ledger |
| Starter template handled | ✅ Explicitly none; justified by the architecture's vertical-slice constraint |

**Step 5 verdict: the epic breakdown is structurally sound and of unusually high craft.** No technical epic, no forward dependency, no circular dependency, no epic-sized story, and AC discipline well above the standard bar. The findings are seven major items — four scoping/schedule concerns, one retroactively-hollowed capstone, one historical CI-verification gap, and one document-drift item — plus six minor observations. **None is a structural violation of the epic standards.**

## Summary and Recommendations

**Assessed:** PRD (`E-PRD/prd.md` + addendum + memlog), `architecture.md`, `epics.md`, `sprint-status.yaml`. UX: not applicable, verified.
**Execution state at assessment time:** Epics 1–9 **done** (41/41 stories); Epics 10–13 **backlog** (22 stories, no story files yet). Next work is Story 10.1.

### Overall Readiness Status

# ⚠️ NEEDS WORK — but implementation is NOT blocked

**Implementation may begin on Epic 10 today.** Requirements coverage is complete, the epic structure is sound, and nothing in the next epic's path is unresolved. The work required is **corrective editing of the traceability layer**, not planning or delivery scope, and one small gating decision before the publish story roughly 20 stories out.

This is a **strong** plan. It is not a "READY" verdict for one reason, stated plainly: **the documents that index the requirements have fallen out of step with the requirements themselves.** On a product whose thesis is *"honesty is mechanical, not promised,"* a coverage map that certifies 33 requirements while 37 are in force is the defect class the product exists to detect. It is cheap to fix and should be fixed before the next amendment compounds it.

### What is genuinely strong

Recorded because a findings list reads as a verdict on quality, and that would be the wrong impression:

- **100% requirements coverage.** All 37 FRs and all 23 NFRs trace to an epic and a named story. Zero orphan requirements; zero epics claiming an FR that does not exist.
- **Zero structural violations.** No technical-milestone epic, no forward dependency, no circular dependency, no epic-sized story, across 13 epics and 63 stories.
- **AC discipline well above the bar.** Given/When/Then throughout, with `file:line` citations, measured counts rather than estimates, and named pinning tests. Exactly **one** AC in 63 stories cannot be verified mechanically.
- **The plan is honest about itself.** The precision gate is recorded NOT CLEARED; the dogfood is excluded from N; a hand-written figure in a proof artifact is flagged as a defect *even though it understated*; a story is deliberately placed last *"so if it slips it slips visibly rather than silently."*
- **`sprint-status.yaml` is a genuinely authoritative tracker.** It resolved three of my candidate findings on verification — the adjudicator naming, the `store_compliance` guard, and H0 ownership. Few projects keep a tracker worth checking against the plan.

### Critical Issues Requiring Immediate Action

**1. `epics.md` certifies a 33-FR contract while 37 are in force.** *(Step 3, CRITICAL)*
The FR Coverage Map (L253-292) and the Requirements Inventory (L94-142) stop at FR33/21 NFRs. FR34, FR35, FR36, FR37, NFR-S6 and NFR-P3 appear in **neither** — they exist only in per-epic inline `Covers:` lines. The 08-10b amendment's own manifest confirms the index layer was never in scope. The Final Validation Summary (L1064) consequently certifies *"all 33 FRs map to a story."*

**2. Three documents disagree with themselves on the same counts.** *(Steps 3 & 4, HIGH)*
`epics.md` frontmatter (`FR1–33`), `epics.md:62` (`33 FRs / 21 NFRs`), `epics.md:1064`, and `architecture.md:40/48` (`Functional Requirements (33)` / `(21)`) — while `architecture.md:467` correctly reads `FR1–37`. The architecture contradicts itself across 400 lines.

### Recommended Next Steps

**Before the next amendment — one editing pass, ~1 hour, no delivery scope:**

1. **Extend `epics.md` §Requirements Inventory and §FR Coverage Map to FR1–FR37 / 23 NFRs.** Map FR34→Epic 11 (11.1); FR35→Epic 12 (12.6, 12.7); FR36→Epic 12 (12.2); FR37→Epic 12 (12.4); NFR-S6→Epic 12 (12.2); NFR-P3→Epic 12 (12.5).
2. **Correct the four stale count assertions** — `epics.md` frontmatter `driver_namespace`, `epics.md:62`, `epics.md:1064` Final Validation Summary, and `architecture.md:40/48`. Date the corrections rather than silently rewriting them (§3.4 evidence immutability, the convention this repo already follows).
3. **Amend `epics.md` OI1 and OI3** (L227-244). OI1 still reads *"LOCKED N = 5, Minions first"* — a corpus Story 13.1 is required to **exclude**; point it at 13.1. OI3 still reads *"DEFERRED"* where the PRD locked it as *"there is no default"* (`ceiling_credits: int | None`, `0 → None`). These feed `bmad-create-story` context and will mislead a story author.
4. **Reconcile `epics.md` Epic 13's header with `sprint-status.yaml`** — it declares the epic unstartable on a condition the tracker records as **MET** (adjudicator XAgent007, named 2026-08-10b).

**Before Story 12.2 is drafted:**

5. **Split Story 12.2.** It carries FR36 wiring + NFR-S6 egress gates + the blocking-reachability measurement + the NFR-R1 resilience behaviours (fallback, circuit-breaking, cost attribution) that architecture §E justified omitting because they came *"for free"* from an orchestrator **Story 9.1 removed**. `sprint-status.yaml` already records this as *"a live gap the moment 12.2 wires it, presenting as flaky audits rather than an obvious defect."* A known live gap deserves its own story rather than a fourth AC block inside a wiring story.

**Before Story 12.9 executes:**

6. **Add an AC to 12.9 asserting FR34's second condition holds at publish time** — that the programme to clear the gate (Epic 13) has a named owner and a committed schedule. The owner exists; the assertion does not. Given FR34's stated consequence (*"if that programme is abandoned, the free public tier is withdrawn rather than the disclosure"*), this is worth pinning by test rather than by memory.

**Recommended, not required:**

7. **Add a forward pointer from Epic 7 to Story 13.1.** Epic 7 still reads as delivered proof, while Story 8.5 re-derived the dogfood as a self-audit and the ledger calls the replacement *"not independent corroboration of anything."* A reader of Epic 7 alone will believe the PRD's central success criterion is met.
8. **Back-reference Story 11.1 from Story 4.1 AC 2** — 11.1's *"over-claim-phrase absence"* guard is the mechanical form of 4.1's *"When reviewed"* prose check, the only non-mechanical AC in the plan.

### Final Note

This assessment examined **37 functional requirements, 23 non-functional requirements, 13 epics, 63 stories and 4 planning documents**, and identified **19 issues across 5 categories** — 1 critical, 1 high, 8 major, 1 medium, and 8 minor — plus **4 candidate findings withdrawn on verification** against `sprint-status.yaml` and the story ACs.

**Every issue is a documentation or scoping correction. None is a missing requirement, a structural defect, or a delivery gap.** The critical and high findings share one root cause: the 2026-08-10b amendment updated the PRD, the architecture's driver namespace, the epic bodies and the tracker — and skipped the index layer that sits between requirements and epics. That is a process gap worth naming, because it is the second consecutive amendment to leave the same layer behind, and because Story 10.1 exists precisely to stop this project publishing statuses its evidence does not support.

**Recommendation: proceed to implementation on Epic 10, and complete recommendations 1–4 in the same working session.** They are an hour of editing, they block nothing, and leaving them lets the next amendment compound a discrepancy that is already two amendments deep.

---

## Remediation Log — 2026-08-10 (same session)

Recommendations **1–4** were applied immediately after the assessment, at the operator's direction. Corrections are **dated in place, never silent rewrites** (§3.4 evidence immutability) — every superseded value is retained and struck rather than deleted.

| # | Finding | Action taken | Status |
|---|---|---|---|
| Step 3 CRITICAL | FR34–FR37 / NFR-S6 / NFR-P3 absent from the Requirements Inventory and FR Coverage Map | Added all four FRs to the inventory in their PRD clusters (FR36+FR37 → Coverage Ledger; FR34 → Verdict; FR35 → Invocation) with full binding text; added NFR-S6 → Security, NFR-P3 → Portability; added four rows to the FR Coverage Map; closing assertion now reads **"All 37 FRs mapped. All 23 NFRs land in ≥1 epic"** with S6→E12/12.2 and P3→E12/12.5 | ✅ **Closed** |
| Step 3 HIGH | Stale count assertions | `epics.md` frontmatter `driver_namespace` → `FR1–37`; `epics.md:62` → `37 FRs / 23 NFRs`; Final Validation Summary scoped to *"base plan, Epics 1–7"* with post-amendment totals stated | ✅ **Closed** |
| Step 4 warning | `architecture.md` self-contradiction | L40 → `Functional Requirements (37)` with FR34–37 placed in their clusters; L48 → `(23)` with NFR-S6/NFR-P3; **plus a third stale certification found during verification** at L720-721 (*"All 33 FRs map to a concrete module"*) — scoped to the base contract, with module placement recorded for all six additions | ✅ **Closed** |
| Step 3 MEDIUM | `epics.md` OI1/OI3 contradict the PRD | **OI1** marked REOPENED and reassigned to Story 13.1, with the two-corpora conflict stated and *"Minions first"* explicitly falsified (Story 8.5); the `N = 5` lock struck through and marked *"do not use this value for story context."* **OI3** marked CLOSED/LOCKED — *"there is no default"*, `ceiling_credits: int \| None`, `0 → None` | ✅ **Closed** |
| Step 5 M-7 | Epic 13 header contradicts `sprint-status.yaml` | Header now reads **"Start condition MET — adjudicator named 2026-08-10b: XAgent007"**, with the item explicitly **not closed** (owner named, measurement not run) and the prior text quoted as corrected | ✅ **Closed** |
| Step 3 LOW | `store_compliance` guard | No action — verified already recorded in `sprint-status.yaml` with its un-skip condition | ✅ **Not a gap** |

**Verification performed:** no unqualified stale count survives in either document (every remaining occurrence is a dated correction note or is explicitly scoped to the base contract); YAML frontmatter re-parses clean in both files.

**Remaining open recommendations — 5, 6, 7, 8** (split Story 12.2; add the FR34-condition AC to Story 12.9; forward-pointer from Epic 7 to Story 13.1; back-reference Story 11.1 from Story 4.1). None blocks Epic 10. Recommendations 5 and 6 should be settled before their stories are drafted.

**Post-remediation status: the CRITICAL and HIGH findings are closed.** The residual findings are scoping and cross-reference improvements, all owned by stories not yet drafted.

---

**Assessment date:** 2026-08-10
**Assessed by:** Implementation Readiness workflow (`bmad-check-implementation-readiness`), acting as Product Manager / requirements-traceability reviewer
**Supersedes:** `implementation-readiness-report-2026-08-03.md` (predates Epics 10–13)
**Documents under assessment:** `E-PRD/prd.md`, `E-PRD/addendum.md`, `architecture.md`, `epics.md`, `sprint-status.yaml`. UX: none — NOT APPLICABLE, verified.
