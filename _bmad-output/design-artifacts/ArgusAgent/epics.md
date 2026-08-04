---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md
  - _bmad-output/design-artifacts/ArgusAgent/architecture.md
  - _bmad-output/planning-artifacts/decisions/2026-06-18-apaa-placement-under-minions-core.md
  - _bmad-output/design-artifacts/ArgusAgent/product-brief-apaa.md
  - _bmad-output/design-artifacts/ArgusAgent/research-technical-2026-06-17.md
  - _bmad-output/design-artifacts/ArgusAgent/implementation-readiness-report-2026-06-18.md
  - _bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md
  - _bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-03.md
  - _bmad-output/design-artifacts/ArgusAgent/deferred-work.md
deltaRuns:
  - date: 2026-08-03
    scope: 'FR16 / FR4 verdict-contract amendment + APAA repo separation (Agent-Argus) — delta only; Epics 1–7 are NOT regenerated'
    supersedes: _bmad-output/planning-artifacts/decisions/2026-06-18-apaa-placement-under-minions-core.md
    signal: _bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-03.md
    approvedBy: Varin
    stepsCompleted:
      - step-01-validate-prerequisites
      - step-02-design-epics
      - step-03-create-stories
      - step-04-final-validation
    status: 'complete'
    openDecisions:
      - 'H0 — who files the Minions-Repo Handoff (H1-H4) against the Minions backlog. UNOWNED.'
    resolvedDecisions:
      - date: 2026-08-03
        id: 'Story 8.1 — decision-row disclosure channel'
        decision: 'Artifact = explicit field (FR16-mandated, free under the DR-4 schema bump). stdout machine summary line = UNCHANGED, pinned by a golden test. stderr human register = distinguishes row 1 from row 4 in prose.'
        rationale: 'The row is already fully derivable from the existing summary line (verdict token + assessed ratio): INSUFFICIENT_COVERAGE with ratio <1/5 => row 1; NOT_READY => row 2; RELEASE_READY => row 3; INSUFFICIENT_COVERAGE with ratio >=1/5 => row 4. Adding a stdout field would be a SECOND wire-contract change stacked on the exit-code shift, for information already present. Matches the addendum precedent that rejected COVERAGE_GATE_UNMET because the distinction was recoverable from the disclosed ratio and assessed population.'
        residualRisk: 'A consumer deriving the row reimplements a slice of the decision table. Mitigated: the artifact carries it authoritatively.'
        correction: 'An earlier AC draft claimed a stdout-parsing consumer could not distinguish row 1 from row 4. It can, from the ratio the line already prints.'
        approvedBy: Varin
    decisions:
      - 'IN-4 depth LOCKED: descriptor-only capability registration (out-of-process CLI); full Flow-Orchestrator wiring deferred'
      - 'Epics 11/12 kept SPLIT: destructive de-vendoring separated from additive integration design'
      - 'Inversion analysis (advanced-elicitation): scariest hypothesis FALSIFIED — the signature demo does NOT depend on a coverage gate; tests/test_cartridge_selfaudit.py:266-273 shows the vacuous cartridge emits a verdict-BLOCKING finding (depth_supported is not None), so row 2 fires before coverage and the demo survives the amendment (more robustly than before). Three real gaps closed: F1 the delta LOOSENS the gate twice (DR-5 + the landed coverage-scope default) with every guard pointing only at over-blocking and NOTHING guarding the PRD-fatal false-RELEASE_READY direction -> false-green counterweight AC on 8.2; F3 no story owns FILING the Minions handoff -> H0 added demanding a named owner or an explicit operator step; F5 nobody re-runs the originating command -> end-to-end symptom-gone AC on 8.5'
      - 'Self-consistency validation (advanced-elicitation): three independent derivations (by requirement cluster, by module ownership, by user outcome) all converge on the SAME 7 stories — no story missing at cluster level. Divergences were all RENDERING surfaces the contract-derived DR list under-named: (1) DR-11 widened to include argus/reports/generator.py, a second verdict surface with its own FR16 reasoning whose critical-paths section Story 8.2 empties; (2) NEW decision AC on where the disclosed row surfaces (artifact / stdout summary line / stderr) — 8.1 requiring disclosure and 8.3 asserting stdout unchanged cannot both be silently true; (3) Story 8.5 precondition — tests/test_dogfood_plan.py has 2 VERIFIED pre-existing failures about the very artifacts it touches. Also: RS-4b scope widened, the stale minions_core path lives in GENERATED artifacts, not only prose.'
      - 'Boundary sweep (advanced-elicitation): 10 edge cases folded into ACs. CORRECTION — Story 8.5 previously asserted the re-derived dogfood outcome would be INSUFFICIENT_COVERAGE/row 4; Story 8.2 changes the inputs (87% deep, 0 blocking findings, only the critical clause blocking) so clearing it yields RELEASE_READY/row 3. The AC now pins the METHOD, not a predetermined verdict. Also pinned: floor-wins-over-blocking survives the reorder; exactly-20% discloses row 4 not row 1; empty critical set must be disclosed (vacuous-gate guard); designation-vs-exclusion precedence; schema bump in the migration note; git rm --cached for a tracked .apaa/'
      - 'Scope decision (operator, 2026-08-03): Minions-repo execution work (RS-2, RS-3, IN-1, IN-3, IN-4) REMOVED from this breakdown and relocated to a Minions-Repo Handoff section, to be filed as a change request against the Minions backlog. ArgusAgent specs carry only work its own CI can verify. Delta epics reduced 3 -> 2 (Epic 8, Epic 9), both Argus-repo. Integration remains planned in full.'
      - 'Assumption audit (advanced-elicitation): A1 falsified (no argus-agent release workflow / index presence) -> NEW IN-0 blocking IN-1; A9 falsified (plain_english NOT VOUCHED branch goes unreachable) -> NEW DR-11; A5 unsupported (Minions exits 3 post-amendment) -> IN-3 advisory-vs-blocking policy decision required before wiring; A4 confirmed (no production importer of minions_core.apaa) -> RS-2 de-risked; A8 -> binding default-field AC on DR-3'
      - 'Subtraction pass (advanced-elicitation): 5 delta epics reduced to 3 (8 -> 9 -> 10). Standalone-Argus epic dissolved (outcome already true: no declared Minions dep + guarded import) -> one prerequisite story on Epic 9; record-truth epic merged into Epic 8; RS-4b bulk prose sweep deferred'
project_name: 'APAA (AI Project Assurance Audit)'
author: 'XAgent007'
date: '2026-06-18'
scope: 'V1 (Tier-A demo-grade spine → Tier-B validation-grade per PRD cut-order); headless; placed at minions_core/apaa/'
driver_namespace: 'APAA-FR-* / APAA-NFR-* (1:1 onto PRD FR1–33 / NFR clusters)'
---

# APAA (AI Project Assurance Audit) — Epic Breakdown

> **Scope note.** This is the epic/story breakdown for **APAA**, the SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It is distinct from the Minions
> platform epics (`_bmad-output/planning-artifacts/epics.md`). APAA reuses Minions infra **by import**
> but ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace, defined in the architecture document.

Date: 2026-06-18 · Primary sources: `E-PRD/prd.md` (33 FRs / 21 NFRs) + `architecture.md` (READY FOR IMPLEMENTATION)
Per-story spec packs (created later by `/bmad-create-story`): `_bmad-output/design-artifacts/ArgusAgent/stories/`

## Overview

This document decomposes the APAA V1 PRD and Architecture into **7 epics** organized by user value
(the PRD journeys J1–J5) and sequenced to honour the architecture's two hard build constraints:

1. **Thin vertical slice first** — Epic 1 delivers the `GitHub green · Sonar green · APAA 🔴 tests
   appear vacuous` signature demo end-to-end on a cartridge, NOT a horizontal "build all schemas"
   scaffolding epic (architecture §Implementation Handoff / pre-mortem guidance).
2. **Tier-A (demo-grade) → Tier-B (validation-grade)** — Epics 1–3 land the non-negotiable demo-grade
   core; Epics 4–7 add the validation-grade trust layer that clears the **≥80%-precision externalization
   gate**. The PRD cut-order (what slips if 90 days is tight) maps to deferring Epic 6/7 work, never
   Epic 1's spine.

**Headless-only (CLAUDE.md §3.7).** No UI/UX stories exist or may be added. Every "user" outcome is an
operator CLI invocation, the `.apaa/` artifact tree, a verdict + deterministic exit code, or an evidence
bundle.

## Requirements Inventory

### Functional Requirements

> **Capability contract (V1, from the PRD).** A capability not listed here will not exist in V1.
> **[Tier B]** = validation-grade additions over the demo-grade core (FR7, FR12, FR19, FR24, FR26).
>
> ⚠️ **FR4 and FR16 were amended 2026-08-03** and are stated below in their **amended** form. Epics 1–7
> were authored against the pre-amendment text and are **not** regenerated; the work closing the gap is
> **Epic 8**. Any story written from this inventory must use the amended text and the decision table in
> §Amendment Delta — not the Epic 1–3 story ACs, which predate it.

**Repository Intake & Partitioning**
- **FR1:** An operator can submit a repository at a pinned commit for audit through a headless invocation.
- **FR2:** APAA can detect the repository's technology stack and available toolchain without operator configuration.
- **FR3:** APAA can partition the repository into bounded audit units within a declared budget.
- **FR4 (amended 2026-08-03):** APAA can identify critical subsystems (and an operator can designate them) so coverage gates can require them to be examined deeply. **A file APAA can never grade `audited_deep` is ineligible for the heuristically-derived critical set** — a gate no run can satisfy is not a gate. Eligibility excludes files that are `audited_shallow` **by construction** (test files; clean-parsed zero-definition modules). **Operator designation via `--critical-subsystem` is exempt**, including for a path matching nothing. `--exclude-critical` matches **by prefix**, not only exact path. → full text in [§Amendment Delta](#delta-requirements-inventory); source of truth `E-PRD/prd.md` FR4.

**Coverage Ledger & Grounded Evidence**
- **FR5:** APAA can record every file's audit depth in a fixed-enum coverage ledger (`audited_deep` / `audited_shallow` / `tool_scanned_only` / `inferred` / `skipped`).
- **FR6:** APAA can require an emitted claim before grading a file `audited_deep` (silence downgrades to `audited_shallow`).
- **FR7:** APAA can validate a deep claim against source structure (Python AST in V1) and downgrade an unverifiable claim. **[Tier B]**
- **FR8:** APAA can exclude `inferred` (narrative/doc) evidence from satisfying any verdict gate.
- **FR9:** An operator can read exactly which files were examined deeply, shallowly, tool-scanned, inferred, or skipped.

**Defect Detection (cartridge-validated)**
- **FR10:** APAA can detect tests that appear vacuous (low assertion-density / high mock-ratio) and report them as **advisory** findings carrying their evidence counts.
- **FR11:** APAA can detect hardcoded secrets and report them with the secret value redacted.
- **FR12:** APAA can detect orphan / dead code (no referencing requirement or caller). **[Tier B]**
- **FR13:** APAA can attach at least one verifiable locator to every finding, or reject the finding.
- **FR14:** APAA can convert a tool failure or unestablishable-traceability condition into a finding rather than a crash.

**Release-Readiness Verdict**
- **FR15:** APAA can compute a release-readiness verdict as a pure function of the coverage ledger.
- **FR16 (amended 2026-08-03):** APAA can emit `RELEASE_READY` only when coverage gates are met (≥60% deep + all critical subsystems deep + 0 blocking findings), can emit a blocking verdict **only on the strength of a finding it actually made**, and reports every other outcome as `INSUFFICIENT_COVERAGE` — never a default block. Governed by a **binding 4-row decision table evaluated in order** (findings before coverage), and the verdict **must disclose which row fired** and the assessed population. → **the table is stated once**, in [§Amendment Delta → Amended Functional Requirements](#amended-functional-requirements-source-of-truth-e-prdprdmd-amended-2026-08-03); source of truth `E-PRD/prd.md` FR16. *Do not restate it here — a third copy is a third drift surface.*
  - **Vocabulary (binding):** `INSUFFICIENT_COVERAGE` is a *not-assessed* state, **not** a blocking verdict, reached **two** ways — below the 20% floor, **or** an unmet coverage/critical gate with **zero** blocking findings. `NOT_READY_FOR_RELEASE` (demo shorthand `BLOCKED`) asserts exactly one thing: **APAA found something.** Never interchangeable.
- **FR17:** APAA can express every verdict in negative-assurance terms with a scope statement, materiality bar, disclaimer, and point-in-time stamp.
- **FR18:** An integrator can consume the verdict as a deterministic exit code and a machine-readable artifact.
- **FR33:** APAA can order findings by verdict impact — surfacing verdict-blocking findings before non-blocking ones (alarm-fatigue defense).

**Self-Audit & Trust**
- **FR19:** APAA can run an adversarial Prosecutor pass that challenges whether the ledger justifies the verdict and downgrades an unearned verdict. **[Tier B]**
- **FR20:** APAA can validate its own detectors against defect cartridges with golden expected-findings keys, asserted in CI.

**Cost Governance**
- **FR21:** An operator can set a budget ceiling for an audit.
- **FR22:** APAA can halt on budget exhaustion, mark the remainder `skipped`, downgrade coverage, and report honestly — never fabricating or silently overrunning.

**Governance, Escalation & Evidence Integrity**
- **FR23:** APAA can halt at a human STOP/PROCEED gate on a pattern-matched escalation condition, defaulting to STOP — and on gate timeout it **parks at STOP, never auto-PROCEEDs**.
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

### NonFunctional Requirements

**Determinism & Reproducibility (keystone)**
- **NFR-D1:** Same repo @ same commit @ same APAA version → identical verdict + ledger (100% reproducibility) via local content-addressed memoization (key = content-hash + model checkpoint + detector-set hash). NOT an assumption the LLM repeats itself.
- **NFR-D2:** Verdict gate + ledger mechanics are deterministic and testable with **zero LLM tokens** (pure functions over recorded findings).
- **NFR-D3:** Artifact content hashes cover the **canonical payload only** (exclude volatile `run_id`/`created_at`).

**Security & Data Protection**
- **NFR-S1:** Source/prompt/response/API-key bytes never appear in ledgers, evidence, logs, OTLP spans, traces, or any response — CI-blocking security suite (mirrors Minions §3.8 / `tests/security/`).
- **NFR-S2:** Detected secrets are redacted before storage; stored form carries `contained_secret` without the value.
- **NFR-S3:** On the operated-service path, customer source is never retained after an audit completes.
- **NFR-S4:** An auditor agent reads **only** the files in its work-manifest (permission boundary); off-scope reads impossible.
- **NFR-S5:** All filesystem writes are containment-checked (`is_relative_to`, no traversal/symlink/sibling-prefix escape), reusing Minions workspace-containment.

**Cost Efficiency**
- **NFR-C1:** A baseline full audit costs a bounded fraction of the audited repo's build cost (target ≤ 10–20%); V1 measures and reports the baseline.
- **NFR-C2:** An audit never exceeds its declared budget ceiling; on exhaustion it halts deterministically, no silent overrun.
- **NFR-C3:** Deterministic, zero-token tools perform breadth so LLM spend is reserved for depth.

**Reliability & Honest Degradation**
- **NFR-R1:** A tool/parse failure or unestablishable-traceability condition degrades to a recorded finding or coverage downgrade — never an uncaught crash or a fabricated result.
- **NFR-R2:** An interrupted audit is fully resumable from on-disk `.apaa/` state with no loss of prior coverage.

**Portability**
- **NFR-P1:** APAA runs to completion on the least-capable host (Cline, sequential), producing byte-identical on-disk state to a parallel host; parallel is a pure speedup.
- **NFR-P2:** The audit is stack-agnostic by construction (deep AST = Python in V1; `claim_emitted` proxy elsewhere); no host-/stack-specific logic in the ledger/verdict core.

**Auditability & Evidence Integrity**
- **NFR-A1:** Every artifact is wrapped in a schema-versioned, content-hashed, prev-hash-chained envelope; schemas evolve additive-only.
- **NFR-A2:** Referential integrity of on-disk state is verifiable (no dangling references). **[Tier B]**
- **NFR-A3:** Every verdict carries a scope statement, materiality bar, disclaimer, and point-in-time stamp.

**Scale Envelope (V1 bounds)**
- **NFR-SC1:** V1 audit units ≤ 40 files / 15k LOC (hard ceiling ≤ 60 / 25k); larger repos partition. Full 10k→500k LOC scaling is V2.

**Maintainability**
- **NFR-M1:** No single source file exceeds **1200 lines** (mirrors Minions §3.2); business logic out of entrypoints (strict modularity).
- **NFR-M2:** Frozen contracts validated (Pydantic v2 + JSON Schema), additive-only evolution.

### Additional Requirements (from Architecture)

**Starter / bootstrap (NOT a generator step).** The "starter" is the existing Minions repo + the
already-reserved `minions_core/apaa/__init__.py` shell + the `minions[apaa]` extra (already staged). There
is **no project-init story** — the first story is the thin vertical signature-demo slice. Architectural
decisions are **inherited** from Minions (Python 3.11+, Pydantic v2 + JSON Schema, pytest, ≤1200-line
files, 12-Factor config + secret-masking, ADR #18 ledger / budget-guardrails / workspace-containment /
`adapter_portability` by import).

- **AR1 — New external dependencies (the only genuine starter choices, versions verified June 2026):**
  `tree-sitter==0.25.2` + `tree-sitter-python==0.25.0` (AST/code-graph index; **grammar version pinned into
  the determinism cache key**), `radon==4.1.0` (zero-token breadth metrics), `jsonschema>=4` (additive
  schema validation), `httpx` (arrives via the `providers` reuse). All land in the `minions[apaa]` extra.
- **AR2 — CLI framework = stdlib `argparse`** (thin entrypoint, zero new dep, keeps `cli.py` pure wiring);
  Typer/Click rejected.
- **AR3 — Exit-code wire contract:** `0`=RELEASE_READY · `2`=BLOCKED (NOT_READY) · `3`=INSUFFICIENT_COVERAGE
  · `1`=crash (mirrors Minions house style; `3`=not-assessed). Machine-consumable CI gate.
- **AR4 — Single canonical serializer** (`apaa/store/canonical.py`: `sort_keys=True, separators=(",",":"),
  ensure_ascii=False`, `\n`-terminated UTF-8). **Forbidden in any `.apaa/` write path:** wall-clock,
  `uuid4`, `os.getpid()`, `random`, dict/`set`-iteration-order reliance, **float scores** (ratios stored as
  fixed-precision `Decimal`/exact fractions — the NFR-P1 byte-diff landmine).
- **AR5 — One cache-key function** (`apaa/cache/key.py`); the key is the full recording-producing closure
  (detector-set content-hash — NOT a human version string — + model checkpoint captured from the API
  response + tool/grammar versions + budget/materiality + work-manifest scope). A mid-run checkpoint drift
  → `checkpoint_drift` finding → abort/re-audit. CI canary fails when key inputs change without a bump.
- **AR6 — Memoization caches errors → reproducibility ≠ correctness:** cache entries invalidate on
  detector-set-hash change, and a human-**rejected** finding **busts its own cache key** (else a false 🔴
  is served forever).
- **AR7 — Reuse-by-import, leaf modules only:** `cost/budget_guardrails`, `lifecycle/workspace_artifact_writer`,
  `providers/orchestrator` + `providers/base` (all verified FastAPI-free). **Never** import
  `minions_core.api.* / services.api_app / app_factory / api_server`. The LLM is reached only via the
  APAA-owned `audit/ports.py::LLMDispatchPort` (the single seam to the non-deterministic substrate).
- **AR8 — Pure/impure separation (master rule):** pure modules (`ledger`, `verdict`, `canonical`,
  `cache/key`, `prosecutor`, detector *scorers*) take NO I/O, NO clock, NO LLM; impure shell at the edges
  only (`store/writer`, `audit/minions_llm_adapter`, tool/subprocess runner, `cli`).
- **AR9 — Committed/durable CI gates (the trust substrate):** import-isolation (`apaa.* ⊬
  fastapi/uvicorn/starlette`), determinism golden-tests (serializer + cache-key), secret-containment
  property suite (randomized canaries), file-size — all under `tests/apaa/` + `tests/security/`, wired to
  the Minions CI model.
- **AR10 — Failure → typed finding, never an uncaught raise** out of the pipeline; typed exceptions at the
  impure shell (reuse `WorkspaceContainmentError`); no bare `except: pass`, no `print()` in library code.
- **AR11 — `.apaa/` runtime tree (fixed) in the AUDITED repo:** `state/ · assignments/ · findings/ ·
  decisions/ · cache/`; filenames from content-sha256 or stable assignment-id, never arrival order.

**Open delivery inputs — LOCKED 2026-06-18 (operator decision; the architecture flagged these as
epic-planning gaps, not architecture-blocking):**
- **OI1 — Validation-set `N` → LOCKED `N = 5` (V1 gate floor), Minions first.** The precision replay
  harness (Story 6.6) is **designed for N = 5** (ground-truth schema/corpus shape), but **populated
  phased**: 3 labeled repos front-loaded in M1 for early precision signal (PRD risk-forward intent), then
  grown to 5 before the ≥80%-precision gate is declared cleared. Precision is measured over **findings**,
  not repos, so 5 repos with sufficient findings support a defensible 80% number; the gate stays
  **provisional below N = 5**. (PRD floor is the chosen value; ceiling 10 deferred to post-V1 if the
  finding-count denominator proves thin.)
- **OI2 — Minions-dogfood scope → LOCKED "full-repo multi-partition".** Story 7.1 partitions **all ~70
  Minions modules** into bounded ≤40-file/15k-LOC audit units and audits each (most complete proof
  artifact). **V1 limitation preserved:** this is multi-**unit** auditing, NOT the V2 cross-partition
  **seam auditor** — no seam analysis spans cut edges in V1 (the `cross_partition` Prosecutor pass,
  Story 6.4, re-reads cut edges as the V1 mitigation; full seam analysis is V2).
- **OI3 — Budget-ceiling `$X` → DEFERRED to empirical Story 7.1 sizing.** No fixed default is locked now;
  `$X` is set once the full-repo partition plan (OI2) exists, sized to cover it. The budget-ceiling
  *mechanism* (Story 3.1) and *halt behaviour* (Story 3.2) are unaffected — only the numeric default for the
  dogfood is deferred.

### UX Design Requirements

**None — APAA is headless by design (PRD §classification `headless: true`, `skipSections: [ux_ui,
visual_design, user_journeys]`).** No UX Design Specification is an input, and none may be authored
(CLAUDE.md §3.7). The "interface" is the CLI contract, the `.apaa/` artifact tree, the verdict + exit code,
and the evidence bundle — all covered by the FRs above.

### FR Coverage Map

| FR | Epic | Capability |
|----|------|------------|
| FR1 | Epic 1 | Headless repo intake @ pinned commit |
| FR2 | Epic 1 | Stack/toolchain auto-detection |
| FR3 | Epic 2 | Bounded-unit partitioning (≤40 files/15k LOC) |
| FR4 | Epic 2 | Critical-subsystem identification/designation |
| FR5 | Epic 1 | Fixed-enum coverage ledger |
| FR6 | Epic 1 | Claim-required `audited_deep` (silence→shallow) |
| FR7 | Epic 6 | Full Python AST-grounding of deep claims **[Tier B]** |
| FR8 | Epic 2 | `inferred` never satisfies a verdict gate |
| FR9 | Epic 2 | Readable per-file depth ledger |
| FR10 | Epic 1 | Heuristic vacuous-test detector (advisory) |
| FR11 | Epic 2 | Hardcoded-secret detection + redaction |
| FR12 | Epic 6 | Orphan/dead-code detection **[Tier B]** |
| FR13 | Epic 1 | Locator-required findings (or reject) |
| FR14 | Epic 2 | Tool-failure → finding, not crash |
| FR15 | Epic 1 | Pure-function verdict over the ledger |
| FR16 | Epic 1 (gate+floor); Epic 2 (critical-subsystem clause) | Coverage gates + 20% floor |
| FR17 | Epic 4 | Negative-assurance verdict semantics |
| FR18 | Epic 1 | Deterministic exit code + machine-readable artifact |
| FR19 | Epic 6 | Adversarial Prosecutor pass **[Tier B]** |
| FR20 | Epic 6 | Defect-cartridge self-audit (CI-asserted) |
| FR21 | Epic 3 | Operator-set budget ceiling |
| FR22 | Epic 3 | Halt→skip→downgrade→report on exhaustion |
| FR23 | Epic 6 | HITL STOP/PROCEED, default-STOP, time-boxed |
| FR24 | Epic 6 | Append-only decision record **[Tier B]** |
| FR25 | Epic 1 | Content-hashed, schema-versioned envelope |
| FR26 | Epic 4 | Referential-integrity lint **[Tier B]** |
| FR27 | Epic 5 | Reproducible verdict (memoization) |
| FR28 | Epic 2 (producer redaction); Epic 4 (containment suite) | No source/secret bytes in artifacts |
| FR29 | Epic 4 | Evidence-bundle export (no source retention) |
| FR30 | Epic 1 | Headless invocation contract |
| FR31 | Epic 3 | Resume from `.apaa/` state |
| FR32 | Epic 3 | Sequential byte-identical execution |
| FR33 | Epic 1 | Verdict-impact finding ordering |

**All 33 FRs mapped. All 21 NFRs land in ≥1 epic** (D1→E5; D2/D3/A1/M1/M2/S5→E1; S2/S4/C3/R1/SC1→E2;
C1/C2/R2/P1/P2→E3; S1/S3/A2/A3→E4; P2→E6).

## Epic List

### Epic 1: Signature-Demo Vertical Slice — "the false-green catch"
The end-to-end thin slice that proves the concept: an integrator runs APAA headlessly against a repo and
receives a coverage-grounded 🔴 verdict + deterministic exit code when tests appear vacuous — the
`GitHub green · Sonar green · APAA 🔴 tests appear vacuous` demo, reproduced on a cartridge. Establishes
the determinism spine (single canonical serializer → content-hashed envelope → fixed-enum ledger → frozen
recording schema → pure-function verdict gate) and the zero-LLM-token core.
**FRs covered:** FR1, FR2, FR5, FR6, FR10, FR13, FR15, FR16 (gate+floor core), FR18, FR25, FR30, FR33.
**NFRs:** D2, D3, A1, P1, S5, M1, M2.

### Epic 2: Full Coverage Ledger & Defect Detectors
Complete the honesty surface — all five depth states with semantics, `inferred`-never-satisfies-a-gate, a
readable ledger, critical-subsystem identification, bounded-unit partitioning — and add the secret detector
with producer-side redaction plus the zero-token breadth tool runner (tool-failure-as-finding).
**FRs covered:** FR3, FR4, FR8, FR9, FR11, FR14, FR28 (producer redaction).
**NFRs:** S2, S4, C3, R1, SC1.

### Epic 3: Honest Degradation & Cost Governance
APAA never lies under pressure: an operator sets a budget ceiling, APAA halts inside it, downgrades
honestly to `INSUFFICIENT_COVERAGE`, resumes from disk, and runs byte-identically on the least-capable
host.
**FRs covered:** FR21, FR22, FR31, FR32, FR16 (20% floor under exhaustion).
**NFRs:** C1, C2, R2, P1, P2.

### Epic 4: Negative-Assurance Verdict & Evidence Bundle
Every verdict is audit-grade and defensible (scope-bounded, materiality bar, disclaimer, point-in-time),
on-disk state is integrity-linted, and an operator can export an evidence bundle that never leaks source —
enforced by a CI-blocking secret-containment property suite.
**FRs covered:** FR17, FR26, FR29, FR28 (containment enforcement).
**NFRs:** S1, S3, A2, A3.

### Epic 5: Reproducible Verdict & Memoization
The same repo at the same commit yields a byte-identical verdict every time — reproducibility as a system
property — with a cache that cannot ossify a wrong answer (invalidates on detector-set change; a rejected
finding busts its own key).
**FRs covered:** FR27.
**NFRs:** D1.

### Epic 6: Trust Substrate — Self-Audit, Prosecutor & Precision
The validation-grade trust layer that clears the ≥80%-precision externalization gate: full Python
AST-grounding, the LLM dispatch port + Minions adapter, orphan-code detection, an adversarial Prosecutor,
CI-asserted cartridges with a hidden holdout + clean true-negative controls, a measurable precision number,
and HITL escalation with an append-only decision record.
**FRs covered:** FR7, FR12, FR19, FR20, FR23, FR24.
**NFRs:** P2 (stack-agnostic claim interface), trust-substrate plumbing.

### Epic 7: Minions Dogfood Proof Run
The capstone: run the full APAA audit against Minions itself, produce the proof artifact + evidence bundle,
and reproduce the signature demo — answering "does Minions have an audit agent?" with a real artifact and
opening the path to externalization.
**FRs covered:** integration capstone (exercises all clusters); delivers the PRD §Success-Criteria proof
artifact + validation protocol.
**NFRs:** end-to-end exercise of D1/P1/C1/S1 on a real repo.

---

## Epic 1: Signature-Demo Vertical Slice — "the false-green catch"

An integrator can invoke APAA headlessly against a repository and receive a coverage-grounded
release-readiness verdict + deterministic exit code, with a 🔴 produced for vacuous tests — proven on the
vacuous-test cartridge. This epic stands alone (it ships a working, if narrow, auditor) and establishes the
determinism spine every later epic folds over.

### Story 1.1: Canonical serializer & content-hashed envelope

As an APAA maintainer,
I want a single canonical JSON serializer and a content-hashed, schema-versioned, prev-hash-chained envelope,
So that every `.apaa/` artifact is byte-reproducible across hosts and tamper-evident (the determinism keystone).

**Acceptance Criteria:**

**Given** any JSON-serializable payload
**When** it is written through `apaa/store/canonical.py`
**Then** output is `sort_keys=True, separators=(",",":"), ensure_ascii=False`, `\n`-terminated UTF-8
**And** calling `json.dumps` directly anywhere in an `.apaa/` write path is rejected by a committed lint/test.

**Given** a payload containing a float ratio, a wall-clock value, or a `uuid4`
**When** it is routed toward an `.apaa/` write
**Then** the write path forbids it (ratios must be fixed-precision `Decimal`/exact fraction; no `datetime.now`/`time.time`/`uuid4`/`os.getpid()`/`random`/iteration-order reliance) — AR4.

**Given** an artifact wrapped by the `EnvelopeWriter`
**When** the envelope is built
**Then** `content_hash` covers the canonical **payload only** (excludes volatile `run_id`/`created_at`), `prev_hash` chains to the prior artifact, and `schema_version` + `producer` + `apaa_version` are present (FR25, NFR-A1, NFR-D3).

**Given** identical input payloads serialized on two different hosts
**When** their content hashes are compared in a golden test
**Then** the hashes are byte-identical (NFR-P1 envelope-canonicalization golden-test, gating before any consumer).

### Story 1.2: Fixed-enum coverage ledger & frozen recording schema

As an APAA maintainer,
I want a fixed-enum coverage ledger and a first-class frozen recording schema as pure Pydantic v2 models,
So that the verdict can be a pure fold over recordings with no field the verdict later needs missing.

**Acceptance Criteria:**

**Given** the coverage-ledger model
**When** a file's depth is recorded
**Then** it must be one of the closed enum `audited_deep / audited_shallow / tool_scanned_only / inferred / skipped`, and a new depth state cannot be added except additively (`schema_version` bump) — FR5, NFR-M2.

**Given** a file graded `audited_deep`
**When** no emitted claim accompanies it
**Then** the ledger downgrades it to `audited_shallow` (silence → shallow) — FR6.

**Given** the recording schema (what LLM calls emit)
**When** it is defined
**Then** it is a frozen Pydantic v2 contract reserving `partition_id` (always `"root"` in V1), validated and additive-only, with no I/O or clock in the model layer (AR8 pure).

**Given** a coverage ledger and recording set
**When** they are constructed in a unit test
**Then** they build with **zero LLM tokens** (NFR-D2).

### Story 1.3: `.apaa/` store writer & reader with filesystem containment

As an APAA maintainer,
I want the impure `.apaa/` writer/reader shell with reused workspace containment,
So that all on-disk state lands inside the audited repo's `.apaa/` tree and nothing can escape it.

**Acceptance Criteria:**

**Given** a write targeting the `.apaa/` tree
**When** the path is resolved
**Then** it passes an `is_relative_to` containment check (never `str.startswith`), reusing
`lifecycle/workspace_artifact_writer` patterns; a traversal/symlink/sibling-prefix escape raises a typed
`WorkspaceContainmentError` **before any write** (NFR-S5, AR7/AR10).

**Given** the fixed `.apaa/` tree (`state/ · assignments/ · findings/ · decisions/ · cache/`)
**When** an artifact is written
**Then** its filename derives from content-sha256 or a stable assignment-id, never arrival order (AR11).

**Given** a previously written artifact
**When** the reader deserializes it
**Then** it validates against the frozen schema and round-trips byte-identically (pure deserialize/validate).

### Story 1.4: tree-sitter AST index, repo intake & Python stack detection

As an integrator,
I want APAA to load a repo at a pinned commit, detect its stack, and build a tree-sitter code-graph index,
So that depth analysis runs on real structure (not embeddings) and the audit is stack-aware.

**Acceptance Criteria:**

**Given** a repo path + a pinned commit
**When** APAA loads it
**Then** it reads the tree at that commit and refuses to proceed if the working tree does not match the pin (FR1).

**Given** a loaded repo
**When** stack detection runs
**Then** it identifies the technology stack and available toolchain via `cloc`/`radon==4.1.0` + tree-sitter, with **no operator configuration** required (FR2).

**Given** a Python source tree
**When** the AST index is built
**Then** `index/ast_index.py` uses `tree-sitter==0.25.2` + `tree-sitter-python==0.25.0` to produce a structural code-graph (the grammar version is recorded for the later determinism cache key — AR1/AR5).

**Given** a non-Python file
**When** it is indexed
**Then** deep AST analysis is unavailable and the file is routed to the `claim_emitted` proxy path via the stack-agnostic `claim→validated?` interface, with no host-/stack-specific logic in the ledger core (NFR-P2).

### Story 1.5: Heuristic vacuous-test detector + Tier-A vacuous-path AST subset

As an Engineering Lead,
I want APAA to flag tests that appear vacuous, advisory-framed and carrying their evidence counts,
So that a passing-but-meaningless test is surfaced without crying wolf.

**Acceptance Criteria:**

**Given** a test file
**When** the heuristic detector runs
**Then** it computes assertion-density + mock-ratio (stored as fixed-precision, not float) and emits an **advisory** `audited_shallow` finding carrying the counts — never a bare accusation (FR10, AR4).

**Given** the Tier-A vacuous-path AST subset (test files only)
**When** it analyzes a flagged test
**Then** it checks (a) the test body reaches the SUT and (b) asserted values derive from the SUT's output (not mocks/constants); only with both AST facts may the finding be eligible to move the verdict (FR7-subset / R1).

**Given** any emitted finding
**When** it is built by `detectors/base`
**Then** it carries `finding_id` + ≥1 verifiable locator (file + line-range/AST span) + `rule_id`/`cartridge_id` + `advisory: bool` + coverage-envelope slice; a finding without a locator is **rejected, not emitted** (FR13).

**Given** a vacuous-test finding with no AST corroboration
**When** the verdict is computed
**Then** it cannot move the verdict to 🔴 on the heuristic alone (advisory-by-contract).

### Story 1.6: Pure-function verdict gate, finding ordering & exit-code mapping

As an integrator,
I want a pure-function verdict gate that folds the ledger into a verdict and a deterministic exit code,
So that the release decision is reproducible, machine-consumable, and provably token-free.

**Acceptance Criteria:**

**Given** a coverage ledger + findings
**When** the verdict gate runs
**Then** it computes the verdict as a **pure function** with zero LLM tokens (FR15, NFR-D2), importing only ledger/finding models (no I/O, no `dispatch()`).

**Given** ledger coverage
**When** gates are evaluated
**Then** `RELEASE_READY` requires ≥60% `audited_deep` + 0 blocking findings; below the 20% floor the verdict is `INSUFFICIENT_COVERAGE` (not a default block); `inferred` evidence can never satisfy a gate (FR16 core, FR8 honored by the gate).

**Given** a mix of blocking and non-blocking findings
**When** they are ordered for the verdict
**Then** verdict-blocking findings sort before non-blocking ones so a blocking 🔴 is never buried (FR33).

**Given** a computed verdict
**When** it is mapped to a process exit code
**Then** `RELEASE_READY→0 · BLOCKED→2 · INSUFFICIENT_COVERAGE→3 · crash→1` (FR18, AR3).

### Story 1.7: CLI invocation contract & pipeline → signature demo on the vacuous-test cartridge

As an integrator,
I want `apaa audit <repo>` to wire the slice end-to-end and produce the signature 🔴 on a cartridge,
So that the `GitHub green · Sonar green · APAA 🔴 tests appear vacuous` demo is real and repeatable.

**Acceptance Criteria:**

**Given** the `apaa` console entrypoint
**When** it is invoked with `repo + commit + budget + materiality_bar`
**Then** `cli.py` (stdlib `argparse`, thin wiring only — AR2/NFR-M1) builds an `AuditRequest`, runs `pipeline.py` sequentially, and returns a verdict artifact + the FR18 exit code (FR30).

**Given** the vacuous-test cartridge (cartridge #1)
**When** `apaa audit` runs against it
**Then** APAA emits a 🔴 `BLOCKED` verdict citing the vacuous test(s) with evidence counts and exits `2` (the signature demo).

**Given** the same cartridge audited twice
**When** the two `.apaa/` trees are compared
**Then** they are byte-identical (sequential determinism, NFR-P1 — full memoization is Epic 5).

**Given** the pipeline encounters any error
**When** it surfaces
**Then** it degrades to a typed finding / exit `1`, never an uncaught raise out of the pipeline (AR10, NFR-R1 baseline).

---

## Epic 2: Full Coverage Ledger & Defect Detectors

APAA records the complete honesty surface of what it examined — readable, gameable-resistant — and detects
the V1 defect classes (secrets, with redaction) while offloading breadth to zero-token tools. Builds on
Epic 1's ledger + detector base; stands alone as a richer auditor.

### Story 2.1: Complete depth-state semantics + `inferred`-never-satisfies-a-gate

As an Engineering Lead,
I want every file graded into the correct one of the five depth states with `inferred` excluded from gates,
So that narrative/doc evidence can never inflate a verdict (evidence-poisoning defense).

**Acceptance Criteria:**

**Given** files examined at varying depths
**When** the ledger is populated
**Then** each lands in exactly one of `audited_deep / audited_shallow / tool_scanned_only / inferred / skipped` per documented grading rules.

**Given** a file whose only evidence is `inferred` (narrative/doc)
**When** the verdict gate evaluates coverage
**Then** that file's `inferred` evidence cannot satisfy any gate threshold (FR8) — verified by a unit test over a synthetic ledger.

**Given** criticality assessed by content (not filename)
**When** a file is graded
**Then** coverage-gaming by renaming is defeated (criticality is content-derived).

### Story 2.2: Readable per-file coverage ledger surface

As an Engineering Lead (answering "how much did it actually look at?"),
I want to read exactly which files were examined deeply, shallowly, tool-scanned, inferred, or skipped,
So that the coverage envelope is inspectable, not a black box.

**Acceptance Criteria:**

**Given** a completed (or partial) audit
**When** I read the `.apaa/state/` ledger
**Then** every file appears with its depth state and the evidence/claim that justified it (FR9).

**Given** the ledger
**When** it is rendered for an operator
**Then** the per-depth counts and percentages (deep %, the VP question) are derivable directly from it, with no source bytes present (NFR-S1 spirit).

### Story 2.3: Critical-subsystem identification & operator designation

As a Delivery Orchestrator,
I want APAA to identify critical subsystems (and let me designate them) and require them examined deeply,
So that the verdict gate can refuse `RELEASE_READY` when a critical subsystem was only shallowly seen.

**Acceptance Criteria:**

**Given** a repo
**When** APAA analyzes it
**Then** it identifies candidate critical subsystems by content (e.g. auth/governance/security-adjacent), and an operator can add/override designations via the invocation contract (FR4).

**Given** a designated critical subsystem graded below `audited_deep`
**When** the verdict gate runs
**Then** `RELEASE_READY` is withheld (this completes the FR16 "all critical subsystems deep" clause introduced in Epic 1).

### Story 2.4: Repository partitioning into bounded audit units + work-manifest permission boundary

As an integrator auditing a large repo,
I want APAA to partition the repo into bounded units within budget, each unit a permission boundary,
So that audits stay inside the V1 scale envelope and auditors read only their assigned files.

**Acceptance Criteria:**

**Given** a repo larger than one audit unit (e.g. Minions ~70 modules)
**When** partitioning runs
**Then** it produces **multiple** graph-derived units (import/call graph, not directories), each ≤40 files/15k LOC (hard ceiling ≤60/25k), with `context_pressure` auto-downgrade (FR3, NFR-SC1) — multi-**unit** auditing is in V1 scope.

**Given** a partition
**When** its `work_manifest` (file-list) is written to `.apaa/assignments/`
**Then** that manifest **is** the auditor's read permission boundary; an off-scope read is impossible (NFR-S4).

**Given** multiple V1 audit units
**When** they are audited
**Then** **no cross-partition seam analysis is attempted** — a defect spanning a cut is handled only by the Story 6.4 `cross_partition` Prosecutor cut-edge pass; the full seam auditor (and a non-`"root"` `partition_id`) is the reserved **V2** seam (honest V1 limitation).

### Story 2.5: Hardcoded-secret detector with producer-side redaction

As a security-conscious operator,
I want APAA to detect hardcoded secrets and store them redacted, citing locations not bytes,
So that auditing a secret-bearing repo never leaks the secret into APAA's own artifacts.

**Acceptance Criteria:**

**Given** a file containing a hardcoded secret
**When** the secret detector runs (regex + entropy)
**Then** it emits a finding flagged `contained_secret: true` with the value **redacted**, citing the AST span/location — never the secret bytes (FR11, NFR-S2, AR4 producer-side redaction).

**Given** any finding from this detector
**When** it is serialized
**Then** no source/secret bytes appear in the ledger, evidence, logs, or traces (FR28 producer guarantee; the CI property suite that enforces it lands in Epic 4).

### Story 2.6: Zero-token breadth tool runner + tool-failure-as-finding

As an integrator (cost-conscious),
I want deterministic zero-token tools to perform breadth and any tool failure to become a finding,
So that LLM spend is reserved for depth and a broken tool degrades honestly instead of crashing.

**Acceptance Criteria:**

**Given** the breadth phase
**When** `detectors/tool_runner.py` runs `cloc`/`radon`/linters/SAST
**Then** breadth metrics are produced with **zero LLM tokens** and files covered only this way are graded `tool_scanned_only` (NFR-C3, FR5).

**Given** a tool that crashes, times out, or is unavailable
**When** the runner invokes it
**Then** the failure becomes a `tool_failure` finding + coverage downgrade — never an uncaught crash or a fabricated result (FR14, NFR-R1).

**Given** an unestablishable-traceability condition (poor-docs repo)
**When** APAA cannot establish traceability
**Then** it records a "traceability not establishable" finding rather than failing (FR14).

---

## Epic 3: Honest Degradation & Cost Governance

APAA stays inside a declared budget, halts honestly when it runs out, downgrades to a truthful
not-assessed verdict, resumes from disk, and runs byte-identically on the least-capable host. Builds on
Epics 1–2; stands alone as the "trust it under pressure" layer.

### Story 3.1: Budget-ceiling configuration & cost accounting

As an operator,
I want to set a budget ceiling for an audit and have APAA account spend against it,
So that an audit's cost is bounded and predictable.

**Acceptance Criteria:**

**Given** an `AuditRequest` with a budget ceiling
**When** the audit runs
**Then** `cost/budget_governor.py` wraps `minions_core.cost.budget_guardrails` **by import** (verified FastAPI-free — AR7) and accounts spend against the ceiling (FR21).

**Given** a completed baseline audit
**When** cost is reported
**Then** APAA reports the baseline as a fraction of the audited repo's build cost (target ≤10–20%, measured not asserted in V1 — NFR-C1).

### Story 3.2: Halt → skip → downgrade → report on budget exhaustion

As an operator,
I want APAA to stop cleanly when the budget is exhausted and report what it did and didn't cover,
So that it never silently overruns or fabricates coverage.

**Acceptance Criteria:**

**Given** an audit that reaches its budget ceiling mid-run
**When** the ceiling is hit
**Then** APAA halts deterministically, marks the remainder `skipped`, downgrades coverage, and reports honestly — no silent overrun (FR22, NFR-C2).

**Given** the halt
**When** the verdict is computed over the partial ledger
**Then** the pure-function gate still produces a verdict (degraded), never a crash.

### Story 3.3: `INSUFFICIENT_COVERAGE` floor under exhaustion

As an Engineering Lead,
I want low coverage reported as "not assessed", never as a default block,
So that APAA's limitation is owned by APAA, not blamed on the repo.

**Acceptance Criteria:**

**Given** a halted audit that assessed below the 20% deep floor
**When** the verdict is rendered
**Then** it is `INSUFFICIENT_COVERAGE` with the assessed depth (e.g. "assessed 18% deep; floor 20%"), exit `3` — never a default `NOT_READY` (FR16 floor, completes the Epic-1 gate).

**Given** `INSUFFICIENT_COVERAGE`
**When** consumed by a CI gate
**Then** it routes to human review (exit `3`), distinct from `BLOCKED` (exit `2`).

### Story 3.4: Resumability from on-disk `.apaa/` state

As an operator who raised the budget after a halt,
I want APAA to resume from where it stopped with no loss of prior coverage,
So that incremental auditing of a large repo is affordable.

**Acceptance Criteria:**

**Given** an interrupted audit with an `.apaa/` tree on disk
**When** APAA is re-invoked on the same repo+commit
**Then** it resumes from the recorded state, reusing prior coverage, and does not re-audit already-`audited_deep` files (FR31, NFR-R2).

**Given** a resumed run
**When** it completes
**Then** the final `.apaa/` state is identical to an uninterrupted run of equivalent budget (no resume artifacts diverge).

### Story 3.5: Sequential byte-identical execution on the least-capable host

As a Delivery Orchestrator standardizing a fleet gate,
I want the sequential (Cline) path to produce byte-identical on-disk state to a parallel run,
So that the verdict is portable and parallel execution is a pure speedup, not a different answer.

**Acceptance Criteria:**

**Given** the same repo+commit+budget
**When** audited sequentially vs. with the parallel scheduler
**Then** the resulting `.apaa/` trees are byte-identical (NFR-P1) — verified by a host-independent determinism test.

**Given** a least-capable host with no parallelism
**When** the audit runs
**Then** it completes to a full verdict using only the sequential-canonical path (FR32, NFR-P2).

---

## Epic 4: Negative-Assurance Verdict & Evidence Bundle

Every verdict becomes audit-grade and defensible, on-disk state is integrity-linted, and an operator can
export a leak-proof evidence bundle — enforced by a CI-blocking secret-containment property suite. Builds
on Epics 1–3; stands alone as the "evidence you can show a regulator" layer (Journey 4).

### Story 4.1: Negative-assurance verdict semantics

As Dana (Head of Quality at a regulated enterprise),
I want every verdict expressed in negative-assurance terms with scope, materiality, disclaimer, and a stamp,
So that legal recognizes audit-grade humility — "no blocking findings within the audited envelope", never "correct".

**Acceptance Criteria:**

**Given** a computed verdict
**When** it is emitted
**Then** `verdict/negative_assurance.py` attaches a `scope_statement` ("examined X, sampled Y, did not cover Z"), a `materiality_bar`, a `disclaimer`, and a point-in-time stamp (FR17, NFR-A3).

**Given** the verdict language
**When** reviewed
**Then** it never implies certification or "the code is correct" — it is scope-bounded negative assurance (no over-claim).

### Story 4.2: Referential-integrity lint of on-disk state — [Tier B]

As an APAA maintainer,
I want a lint that verifies the `.apaa/` state has no dangling references,
So that resumability and evidence bundles are built on internally consistent state.

**Acceptance Criteria:**

**Given** an `.apaa/` tree
**When** the integrity lint runs
**Then** every reference (finding→ledger entry, decision→assignment, envelope `prev_hash` chain) resolves; a dangling reference is reported (FR26, NFR-A2).

**Given** a broken chain or orphaned reference
**When** linted
**Then** it surfaces as a typed integrity finding, not a crash.

### Story 4.3: Evidence-bundle export with no source retention

As an XAgents engineer on the operated-service path,
I want to export an evidence bundle (ledger, scope statement, findings, verdict) that retains no source,
So that a regulated customer gets defensible evidence without their code ever being kept.

**Acceptance Criteria:**

**Given** a completed audit
**When** `evidence/bundle.py` exports the bundle
**Then** it contains the coverage ledger, scope statement, findings (redacted excerpts only), and the negative-assurance verdict + disclaimer + point-in-time stamp (FR29).

**Given** the operated-service path
**When** the audit completes
**Then** customer source is not retained after completion (NFR-S3) — verified by asserting no source bytes remain in the export or working state.

### Story 4.4: Secret-containment property suite (CI-blocking)

As a security owner,
I want a randomized-canary property suite proving no source/secret bytes ever reach APAA's artifacts,
So that the redaction guarantee is mechanically enforced, not promised.

**Acceptance Criteria:**

**Given** randomized canary secrets planted in a fixture repo
**When** APAA audits it
**Then** `tests/security/test_apaa_secret_containment.py` asserts the canaries are **absent** from {ledger, evidence, logs, traces, verdict envelope} — and the suite **blocks CI on failure** (FR28 enforcement, NFR-S1, AR9).

**Given** a new write path added to APAA
**When** CI runs
**Then** the property suite still holds (the suite is the durable backstop across a fresh clone).

---

## Epic 5: Reproducible Verdict & Memoization

The same repo at the same commit yields a byte-identical verdict every time, via content-addressed
memoization keyed on the full recording-producing closure — with a cache that cannot ossify a wrong answer.
Builds on Epics 1–4; stands alone as the "a number you can put on a dashboard and trust not to flake" layer
(Journey 3).

### Story 5.1: Cache-key derivation (full recording-producing closure) + CI canary

As an APAA maintainer,
I want one pure cache-key function over every determinism-relevant input, with a CI canary,
So that a memo hit can only return a result produced by an identical closure.

**Acceptance Criteria:**

**Given** the cache-key inputs
**When** `apaa/cache/key.py` derives a key
**Then** it folds content-hash + model checkpoint (captured from the API response, not config) + detector-set **content-hash** (not a human version string) + tree-sitter-grammar/tool versions + budget/materiality + work-manifest scope (AR5) — as a pure, golden-tested function.

**Given** a change to any key input (e.g. a detector edit) without a deliberate version bump
**When** the CI canary runs
**Then** it fails, forcing the key derivation to stay honest (AR5).

**Given** a mid-run model checkpoint drift
**When** detected
**Then** APAA emits a `checkpoint_drift` finding and aborts/re-audits rather than mixing checkpoints (AR5/R3).

### Story 5.2: Content-addressed memoization store

As an integrator running the same audit twice,
I want a local content-addressed memo store so a re-run returns the recorded result,
So that the verdict is 100% reproducible without re-spending tokens.

**Acceptance Criteria:**

**Given** a recorded finding under a cache key
**When** the same key recurs
**Then** `apaa/cache/memo_store.py` returns the **recorded** result (cache hit), achieving identical verdict + ledger across runs (FR27, NFR-D1).

**Given** the V1 reproducibility floor
**When** the memo store is used
**Then** it is **local** (the shared G4 cross-run cache is V4 and never the sole guarantee — a safety-critical guarantee must not depend on an external cache).

### Story 5.3: Cache invalidation & rejected-finding key-busting

As an Engineering Lead who rejected a false 🔴,
I want a rejected finding to bust its own cache key and detector changes to invalidate the cache,
So that reproducibility never means "a stable wrong answer served forever".

**Acceptance Criteria:**

**Given** a human-**rejected** finding
**When** the audit re-runs
**Then** that finding's cache key is busted so the false 🔴 is not re-served (AR6/R2 — reproducibility ≠ correctness).

**Given** a change to the enabled detector set (code or config)
**When** the detector-set content-hash changes
**Then** affected cache entries invalidate (AR6).

**Given** a clean repo and a flaky-vs-stable comparison
**When** audited repeatedly
**Then** the verdict is stable AND correct (not merely stable).

---

## Epic 6: Trust Substrate — Self-Audit, Prosecutor & Precision

The validation-grade layer that earns externalization: full AST-grounding, the LLM dispatch port, orphan
detection, an adversarial Prosecutor, CI-asserted cartridges with holdout + clean controls, a measurable
precision number, and HITL escalation. Builds on Epics 1–5; stands alone as the "proven, not asserted,
depth" moat. **The whole epic is the cut-order boundary** — if 90 days is tight, these are the Tier-B
items that slip to V1.5 (the demo-grade core in Epics 1–3 still ships).

### Story 6.1: LLM dispatch port + Minions orchestrator adapter

As an APAA maintainer,
I want the single `LLMDispatchPort` seam with a thin Minions-orchestrator adapter,
So that the pure core never touches the LLM directly and tests inject a fake for zero-token runs.

**Acceptance Criteria:**

**Given** `apaa/audit/ports.py::LLMDispatchPort(Protocol)` with `dispatch(req) -> LLMRecording`
**When** `audit/deep_audit.py` needs an LLM
**Then** it depends on the **port**, never the orchestrator directly (DIP), and a `FakeDispatch` yields 0 LLM tokens in tests (AR7, NFR-D2).

**Given** `audit/minions_llm_adapter.py`
**When** it dispatches
**Then** it holds an `LLMProviderOrchestrator` (`minions_core.providers.orchestrator`, FastAPI-free), maps `LLMRequest`/`LLMResponse` ↔ APAA's frozen `LLMRecording`, and **captures the model checkpoint from the API response** (AR5), inheriting the orchestrator's fallback chain + circuit breaker + cost attribution (no fork, §3.3).

**Given** the import-isolation gate `tests/apaa/test_no_web_imports.py`
**When** CI runs
**Then** it asserts `apaa.*` does not transitively import `fastapi/uvicorn/starlette` (committed/durable — AR9).

### Story 6.2: Full Python AST-grounding of `audited_deep` claims — [Tier B]

As an Engineering Lead,
I want deep claims validated against the full Python AST (not just the vacuous-path subset),
So that a shallow read mis-graded as deep is caught and downgraded.

**Acceptance Criteria:**

**Given** a deep claim about a Python file
**When** `audit/deep_audit.py` validates it
**Then** it checks the claim against the multi-construct AST; an unverifiable claim downgrades to `audited_shallow` (silence/insufficiency → downgrade) — FR7.

**Given** the validator
**When** a non-Python file is encountered
**Then** the stack-agnostic `claim→validated?` interface routes to the `claim_emitted` proxy (Python = impl #1), so V2 multi-language is additive (NFR-P2).

### Story 6.3: Orphan / dead-code detector — [Tier B]

As an Engineering Lead,
I want APAA to detect orphan/dead code (no caller, no referencing requirement),
So that unreachable code surfaces as a finding.

**Acceptance Criteria:**

**Given** the code-graph index
**When** `detectors/orphan_code.py` runs
**Then** it flags functions/classes with no caller and no referencing requirement as orphan findings, each with a verifiable locator (FR12, FR13).

### Story 6.4: Adversarial Prosecutor + cut-edge pass — [Tier B]

As an Engineering Lead,
I want an adversarial Prosecutor that tries to prove the verdict unearned and re-reads partition cut edges,
So that an over-confident verdict is downgraded and seam defects can't hide as `inferred`.

**Acceptance Criteria:**

**Given** a ledger + candidate verdict
**When** `verdict/prosecutor.py` runs
**Then** it is a **pure recording-consumer** (cannot call an LLM), challenges whether the ledger justifies the verdict, and downgrades an unearned verdict (FR19).

**Given** a defect spanning a partition cut (caller in A, callee in B)
**When** the Prosecutor's cut-edge pass runs
**Then** it re-reads cut edges and raises a `cross_partition` finding rather than letting the defect land silently as `inferred` (cross-cutting concern #4).

**Given** a heuristic-only vacuous finding
**When** the Prosecutor evaluates a verdict-moving 🔴
**Then** the 🔴 stands only with AST corroboration AND Prosecutor sign-off (advisory-by-contract, false-accusation moat).

### Story 6.5: Defect-cartridge self-audit harness + holdout + clean controls

As an APAA maintainer,
I want CI-asserted defect cartridges, a hidden holdout, and clean true-negative controls,
So that what the detectors catch is measured empirically and a false 🔴 on clean code fails CI.

**Acceptance Criteria:**

**Given** cartridges #1 (vacuous) / #2 (secret) / #3 (orphan), each a minimal repo + one planted defect + a golden key
**When** `tests/apaa/test_cartridge_selfaudit.py` runs them
**Then** each detector hits its golden key, CI-asserted (FR20).

**Given** a hidden holdout cartridge the detector authors never see
**When** CI runs
**Then** it is exercised and gated (overfitting defense).

**Given** clean (no-planted-defect) control cartridges
**When** audited
**Then** **any 🔴 is an instant CI fail** (the false-accusation floor), and false-negative traps (citation-gaming) are included.

### Story 6.6: Precision replay harness + validation protocol (OI1 LOCKED: N = 5, phased)

As a Business owner gating externalization,
I want a replay harness that diffs findings against labeled ground truth to emit a precision number, plus the validation protocol,
So that the ≥80%-precision gate is empirical, not aspirational.

**Acceptance Criteria:**

**Given** findings carrying `finding_id` + coverage-envelope slice + rule/cartridge id + AST span
**When** `precision/replay_harness.py` diffs them against a labeled ground-truth set
**Then** precision falls out as a number (Tier-A plumbing, not optional).

**Given** the validation protocol (a V1 deliverable), with `N` **locked at 5** (V1 gate floor), Minions first
**When** it is authored
**Then** the harness ground-truth shape is **designed for N = 5**, and the protocol fixes who validates, expert-hours/repo, the precision-adjudication method (sample size, who judges a 🔴 "genuinely real"), and per-metric pass/fail — recorded before the ground-truth schema is frozen (OI1).

**Given** the phased-population plan
**When** the harness is first stood up
**Then** **3 labeled repos are front-loaded in M1** for early precision signal, and the ≥80%-precision gate is reported **provisional until N ≥ 5** (precision is measured over findings, not repos — 5 repos with sufficient findings support a defensible 80%).

**Given** the ground truth
**When** assembled
**Then** it includes clean (true-negative) repos so precision has a false-positive denominator (R6).

### Story 6.7: HITL STOP/PROCEED escalation + append-only decision record

As a Delivery Orchestrator,
I want a pattern-matched human STOP/PROCEED gate that defaults to STOP and logs decisions append-only,
So that a non-deterministic or high-stakes case escalates to a human and the decision is auditable.

**Acceptance Criteria:**

**Given** a pattern-matched escalation condition
**When** it fires
**Then** `governance/escalation.py` halts at a STOP/PROCEED gate **defaulting to STOP** (R1 pattern-matched, not LLM-judgment) — FR23.

**Given** a configured gate-timeout window with no human response
**When** it elapses
**Then** APAA **parks at STOP, never auto-PROCEEDs** (time-boxed-gate default) — FR23.

**Given** a human decision
**When** it is recorded
**Then** `governance/decision_record.py` appends it to `.apaa/decisions/` (append-only) — and the STOP is logged even if the full record is deferred (FR24, Tier B).

---

## Epic 7: Minions Dogfood Proof Run

The capstone: run the full APAA audit against Minions itself, produce the proof artifact + evidence bundle,
and reproduce the signature demo — answering "does Minions have an audit agent?" with a real artifact.
Depends on Epics 1–6 being in place; it is the proof, the last thing cut.

### Story 7.1: Minions full-repo partition + budget-sizing plan (OI2 LOCKED: full-repo; OI3: size $X here)

As a Delivery Orchestrator,
I want an explicit full-repo partition + budget plan for auditing all of Minions (~70 modules),
So that the proof run covers the whole repo and doesn't land `INSUFFICIENT_COVERAGE`.

**Acceptance Criteria:**

**Given** Minions (~70 modules) vs. ≤40-file/15k-LOC units + a 20%-deep floor
**When** the dogfood is planned
**Then** an explicit **full-repo** partition map (all modules across multiple bounded units — OI2 locked) + a per-unit budget allocation is recorded so each targeted unit clears the 20% floor.

**Given** the budget ceiling `$X` was deferred (OI3)
**When** the partition plan is finalized
**Then** `$X` is **sized empirically to cover the full-repo plan** and recorded as the dogfood ceiling — there is no pre-locked numeric default; the run is expected to complete within it (PRD §Success-Criteria cost outcome), with the ceiling demonstrably halting + downgrading if breached.

**Given** the full-repo scope spans partition cut edges
**When** the plan is written
**Then** it explicitly notes that V1 has **no cross-partition seam analysis** (the Story 6.4 `cross_partition` Prosecutor pass is the V1 mitigation; full seam auditing is V2) — so the proof's scope statement is honest about what cut-spanning defects it could and couldn't see.

### Story 7.2: Execute the Minions audit → proof artifact, evidence bundle & repeatable signature demo

As the XAgents platform owner,
I want APAA to fully audit Minions and produce the proof artifact + a repeatable signature demo,
So that the strategic question is answered and the path to the ≥80%-precision gate is open.

**Acceptance Criteria:**

**Given** the partition + budget plan (Story 7.1)
**When** APAA audits Minions end-to-end
**Then** it produces a coverage ledger, findings, a negative-assurance verdict, and an exported evidence bundle — within the budget ceiling (and the ceiling demonstrably halts + downgrades if breached — PRD §Success-Criteria).

**Given** a Minions vacuous-test (planted or real)
**When** the audit runs
**Then** the `GitHub green · Sonar green · APAA 🔴 tests appear vacuous` line is reproduced as a real, repeatable artifact (the moat demo as a success criterion).

**Given** the dogfood run repeated on the same Minions commit
**When** the two verdicts are compared
**Then** they are identical (100% reproducibility on a real repo — NFR-D1).

**Given** the run completes with AST-grounding cut (Tier-A only)
**When** the verdict is presented
**Then** it carries a hard `grade: demo-heuristic-only` flag and is **not** presented as externalization evidence (red-team guard).

---

## Final Validation Summary

- **FR coverage:** all 33 FRs map to a story (see FR Coverage Map + per-epic story ACs). FR16 spans Epic 1
  (gate+floor core) and Epic 2 (critical-subsystem clause); FR28 spans Epic 2 (producer redaction) and
  Epic 4 (containment enforcement) — both deliberate, both fully delivered.
- **NFR coverage:** all 21 NFRs land in ≥1 epic and are asserted by at least one story AC.
- **Tier mapping:** Tier-A demo-grade = Epics 1–3 (+ cartridges #1/#2 in 6.5); Tier-B validation-grade =
  Epics 4–7 (FR7, FR12, FR19, FR24, FR26 + reproducibility + dogfood). The PRD cut-order is honored:
  Epic 6 is the explicit slip boundary; Epic 1's spine never slips.
- **Dependency flow:** each epic stands alone and builds only on earlier epics; no story depends on a future
  story within its epic. Epic 7 depends on 1–6 (it is the capstone proof, "last thing cut").
- **Headless:** zero UI/UX stories (CLAUDE.md §3.7). All outputs are CLI/exit-code/`.apaa/`/evidence-bundle.
- **Open inputs (LOCKED 2026-06-18):** OI1 → `N = 5` V1 gate floor, harness designed for 5, populated
  phased 3→5 (Story 6.6); OI2 → **full-repo multi-partition** dogfood, V2 seam analysis deferred (Story 7.1
  + Story 2.4 wording); OI3 → budget-ceiling `$X` **deferred to empirical Story 7.1 sizing** (no numeric
  default locked). See the "Open delivery inputs — LOCKED" block under Additional Requirements.

## Next Steps

1. **Operator review** of this epic structure (7 epics) and the 3 open delivery-input defaults (OI1–OI3).
2. **`/bmad-sprint-planning`** to seed APAA story keys into a sprint-status tracker (APAA is self-contained
   under `design-artifacts/ArgusAgent/`; decide whether it shares `sprint-status.yaml` or gets its own).
3. **`/bmad-create-story`** per story (starting Story 1.1) to produce the full context-filled spec packs in
   `_bmad-output/design-artifacts/ArgusAgent/stories/`.
4. **CLAUDE.md §4a follow-up** (per the placement decision Consequences): once stories land, add APAA as a
   Component → Driver Map row and note the `apaa/` sub-package — tied to the first implementation story, not
   pre-emptive.

---

# Amendment Delta — FR16 / FR4 Verdict Contract (2026-08-03)

> **Delta scope.** Epics 1–7 above are **delivered and are NOT regenerated or restated**. This section
> covers only the work created by the **2026-08-03 PRD amendment** to FR16 (verdict decision table) and
> FR4 (critical-subsystem eligibility), approved by Varin at the contract gate — step 4 of the
> [sprint change proposal](sprint-change-proposal-2026-08-03.md)'s recommended sequence. Step 5
> (CR-1 + CR-3 + the schema bump) was **blocked on that gate and is now unblocked**; it is the work
> decomposed here.
>
> 🚩 **Repo separation (operator decision, 2026-08-03).** APAA has **moved out of Minions into its own
> repository** — `Agent-Argus` (`https://github.com/Inan15/Agent-Argus.git`), distribution `argus-agent`,
> package `argus/`, console scripts `argus` / `argus-agent` / `repo-audit`. This **supersedes the
> 2026-06-18 placement decision** (`planning-artifacts/decisions/2026-06-18-apaa-placement-under-minions-core.md`)
> and every `minions_core/apaa/` path in the architecture document and in Epics 1–7 above. Two binding
> consequences, carried as **RS-1 … RS-4** below: **(a)** the amendment is implemented in `argus/` only —
> the `minions_core/apaa/` copy is legacy and **must not be modified or back-ported to**; **(b)** APAA
> wiring is **removed from the Minions repo completely**.
>
> 🔗 **Re-integration (operator decision, 2026-08-03).** Removal is **half** of one migration, not an end
> state: Minions must then **consume Argus as an external product** rather than vendor its source. Carried
> as **IN-1 … IN-5** below. The shape is *de-vendor, then re-integrate* — `minions_core/apaa/` (a forked
> copy that drifts) is replaced by a dependency on the published `argus-agent` distribution plus a CI gate
> and a platform capability. **RS-2 and IN-1 must ship together**, or Minions has no audit capability in
> between.

## Delta Requirements Inventory

### Amended Functional Requirements (source of truth: `E-PRD/prd.md`, amended 2026-08-03)

- **FR16 (amended):** APAA can emit `RELEASE_READY` only when coverage gates are met (≥60% deep + all
  critical subsystems deep + 0 blocking findings), can emit a blocking verdict **only on the strength of a
  finding it actually made**, and reports every other outcome as `INSUFFICIENT_COVERAGE` — never a default
  block. The binding decision table, **evaluated in order** (findings before coverage, so a coverage
  shortfall can never be reported as a defect):

  | # | Condition | Verdict | Exit |
  |---|---|---|---|
  | 1 | `assessed_total == 0` or `assessed_ratio < 1/5` | `INSUFFICIENT_COVERAGE` | 3 |
  | 2 | `blocking_findings >= 1` | `NOT_READY_FOR_RELEASE` | 2 |
  | 3 | `assessed_ratio >= 3/5` **and** all critical subsystems `audited_deep` | `RELEASE_READY` | 0 |
  | 4 | otherwise — zero blocking findings, a coverage or critical-subsystem gate unmet | `INSUFFICIENT_COVERAGE` | 3 |

  **The verdict must disclose which row fired and the assessed population it was computed over.**

- **FR4 (amended):** APAA can identify critical subsystems (and an operator can designate them) so coverage
  gates can require them to be examined deeply. **A file APAA can never grade `audited_deep` is ineligible
  for the heuristically-derived critical set.**
  - **Eligibility (heuristic set):** exclude files that are `audited_shallow` **by construction** — test
    files (the *subject* of the vacuous-test pass, never a target of deep grounding) and clean-parsed
    zero-definition modules.
  - **Operator designation is exempt.** An explicit `--critical-subsystem` keeps its conservative
    behaviour, including for a path that matches nothing.
  - An operator can exclude a subtree from the critical set **by prefix**, not only by exact path.

- **Canonical vocabulary (amended, binding on downstream artifacts):** `INSUFFICIENT_COVERAGE` is a
  *not-assessed* state — "I did not examine enough to vouch" — reached **two** ways: coverage below the 20%
  floor, **or** an unmet coverage / critical-subsystem gate with **zero** blocking findings. It is **not**
  a blocking verdict. `NOT_READY_FOR_RELEASE` (demo shorthand `BLOCKED`) asserts exactly one thing:
  **APAA found something.** The two are never interchangeable.

### Derived Delta Requirements (DR) — measured against the shipped tree

Each DR carries its **verified current state** in `argus/` at `faeefd9`. DR-7 is listed for completeness
and requires no new implementation.

| DR | Requirement | Source | Current state (verified) |
|---|---|---|---|
| **DR-1** | Reorder `evaluate_verdict` to the binding 4-row table — findings evaluated **before** coverage | FR16 | ❌ **Open.** `argus/verdict/verdict_gate.py:511-520` still evaluates floor → `RELEASE_READY` → `otherwise NOT_READY` (3 rows) |
| **DR-2** | Row 4: zero blocking findings + an unmet coverage/critical gate → `INSUFFICIENT_COVERAGE`, exit `3` | FR16 | ❌ **Open.** That case currently falls through to `NOT_READY_FOR_RELEASE`, exit `2` — a verdict asserting a defect APAA did not find |
| **DR-3** | The verdict artifact discloses **which decision row fired** and the **assessed population** it was computed over | FR16 | ❌ **Open.** `AuditVerdict` carries `deep_ratio`/`deep_count`/`total_count`/`coverage_scope`/`critical_subsystems_not_deep` but **no decision-row field**. ⚠️ **Binding AC (assumption A8):** `AuditVerdict` is `extra="forbid"` — the new field **must carry a default**, or pre-amendment persisted verdicts stop round-tripping |
| **DR-4** | `VERDICT_SCHEMA_VERSION` `"1"` → `"2"`; verdicts persisted under `.apaa/` **before** the amendment keep their original meaning and stamp and are **not rewritten** | addendum §A1 | ❌ **Open.** `verdict_gate.py:149` is still `"1"` |
| **DR-5** | Heuristic critical-set eligibility filter — exclude `is_test_file` entries and clean-parsed zero-definition modules | FR4 | ❌ **Open.** No eligibility predicate exists in `argus/ledger/critical_subsystems.py` |
| **DR-6** | Operator `--critical-subsystem` designation is **exempt** from DR-5, including an unmatched path | FR4 | ❌ **Open** (the exemption must be explicit and pinned once DR-5 lands) |
| **DR-7** | `--exclude-critical` matches by exact path, directory prefix, or glob | FR4 | ✅ **Landed** (CR-4). `critical_subsystems.py:83,223-236` uses `fnmatchcase` (never `fnmatch` — host case-folding would break byte-identity). **Verify + keep pinned; no new work** |
| **DR-8** | Integrator migration is documented: some runs that exited `2` now exit `3`; a CI step branching only on `0` vs non-zero is unaffected | addendum §A1 | ❌ **Open.** The addendum states it; no release note is published to consumers |
| **DR-9** | The `schema_version` bump is the **only** intentional content-hash change; every other byte of an unscoped run stays identical | NFR-D1/D3, NFR-P1 | ❌ **Open** — a property this delta must *prove*, not assume |
| **DR-10** | Re-derive (or explicitly re-affirm) the shipped proof artifacts that recorded a pre-amendment verdict | consequence of FR16 | ❌ **Open.** The Story 7.2 dogfood recorded `NOT_READY_FOR_RELEASE` / exit `2` at deep-% `13/15` with **0 verdict-eligible findings** (`deferred-work.md` DF-6-6-A-P2) — exactly row 4, so under the amended table it becomes `INSUFFICIENT_COVERAGE` / exit `3`. `minions-dogfood-proof.md`, `_bmad-output/reports/final-verdict.md` and `_bmad-output/audit-reports/final-verdict.md` are stale against the amended contract |
| **DR-11** | **Reconcile the report surfaces with the amended table — BOTH of them.** ⚠️ **Scope widened by the self-consistency pass:** `argus/reports/generator.py` is a *second* verdict-rendering surface with its **own** FR16 reasoning, not merely a call into `plain_english` — it renders *"the critical paths that withheld `RELEASE_READY`"* (`:104`, `:122`) and branches independently on the verdict enum, the deep-ratio threshold and `blocking_finding_count` (`:62-79`, `:304`). Story 8.2 **empties** that critical-paths section, and its *"each must reach `audited_deep`"* guidance becomes wrong once ineligible files are auto-excluded. `argus/reports/plain_english.py` branches `RELEASE_READY` → `INSUFFICIENT_COVERAGE` → `blocking_finding_count > 0` → *else* **"NOT VOUCHED"**. That final branch exists solely to render `NOT_READY_FOR_RELEASE` **with zero blocking findings** — the exact case DR-2 relocates — so it becomes **unreachable** once DR-1/DR-2 land. Either delete it or prove it still reachable, and re-point the `tests/test_plain_english.py` cases that pin the zero-finding/blocking split | consequence of FR16 (assumption A9, **falsified**) | ❌ **Open.** Uncovered by the original DR set — the landed CR-2 presentational fix was the *stopgap* for this bug, and CR-1 makes part of that stopgap dead code |

### Additional Requirements (Architecture + addendum) — constraints on how the delta lands

- **The verdict enum MUST NOT grow.** Adding `COVERAGE_GATE_UNMET` was explicitly considered and rejected
  (addendum §A1 options matrix): it would widen a frozen enum every downstream consumer must learn, to
  distinguish two cases that route identically (human review). One value carries one meaning.
- **Exit codes are unchanged as values** — `0/2/3/1` (AR3 wire contract). No new code is introduced; what
  changes is which runs map to `3` instead of `2`.
- **The verdict gate stays PURE** — no I/O, no clock, no LLM; testable at **zero LLM tokens** over synthetic
  ledgers (NFR-D2, architecture AR8 pure/impure master rule).
- **Determinism patterns bind unchanged** — one canonical serializer; ratios as exact `Fraction`, never
  `float`; no wall-clock/`uuid4`/`getpid()`/iteration-order in any `.apaa/` write path (AR4, NFR-P1).
- **Additive-only schema evolution** (NFR-M2) — the `schema_version` bump is the sanctioned lever for an
  intentional content-hash change, permitted under the rule at `verdict_gate.py:147-149`.
- **Touched modules (addendum §A1):** `argus/verdict/verdict_gate.py` (decision table + version bump) and
  `argus/ledger/critical_subsystems.py` (eligibility filter). `argus/cli.py` and
  `argus/detectors/vacuous_test.py` were already touched by the landed CR-2/CR-5.
- **Driving cross-cutting concern #6** (advisory-by-contract / the false-accusation moat) — currently
  enforced on *findings* but not on the *verdict itself*; this delta closes that asymmetry.
- **NFR-M1** — no source file exceeds 1200 lines; business logic stays out of entrypoints.
### Repo-Separation Requirements (RS) — operator decision, 2026-08-03

APAA is now the standalone **Agent-Argus** repo. The `minions_core/apaa/` tree is legacy. These are
binding on this delta and on every subsequent APAA change.

| RS | Requirement | Current state (verified) |
|---|---|---|
| **RS-1** | **All amendment work lands in `argus/` in the Agent-Argus repo.** The `minions_core/apaa/` copy in Minions is legacy: **no modification, no back-port, no dual maintenance.** DR-1 … DR-10 are satisfied in `argus/verdict/verdict_gate.py` and `argus/ledger/critical_subsystems.py` only | ✅ Constraint stated here; enforced by RS-2 making the Minions copy cease to exist |
| **RS-2** | **Remove APAA wiring from the Minions repo completely** — the package, its tests, its CI gates, its packaging surface, and its runtime directory | ❌ **Open.** All wiring is still present (surface enumerated below). ✅ **De-risked (assumption A4, verified 2026-08-03):** **no production Minions code imports `minions_core.apaa`** — the only importer outside the package and `tests/apaa/` is `tests/security/test_apaa_secret_containment.py`, itself on the removal list. The deletion breaks no Minions runtime code |
| **RS-3** | **Supersede, do not erase, the historical record.** The 2026-06-18 placement decision and the APAA design/implementation artifacts under `_bmad-output/` in Minions are **evidence** (§3.4 evidence immutability, the same append-only rule the deferred-work register follows). Mark them superseded with a forward pointer to Agent-Argus; do **not** delete them | ❌ **Open** |
| **RS-4a** | **Fix the package front door.** `argus/__init__.py:37` still reads *"Lives at `minions_core/argus/`"* — the first thing any reader of the package sees | ❌ **Open** — one line, carried in Epic 8 |
| **RS-4b** | **Bulk provenance sweep** — the remaining ~48 stale `minions_core/apaa/` references in `argus/` docstrings and comments, plus the architecture document and Epics 1–7 above. ⚠️ **Scope note (self-consistency pass):** this is **not prose only** — the committed dogfood budget artifact is auto-generated carrying the header *"AUTO-GENERATED by `minions_core/apaa/dogfood/partition_plan.py`"*, so **generated artifacts** carry the stale path too and a prose-only sweep would miss them | ⏸️ **DEFERRED out of this delta** (subtraction pass, 2026-08-03): unbounded, cosmetic, and it expands to fill available time. To be filed as a `deferred-work.md` entry with an owner when Epic 8's first story lands — the register's convention is that entries carry an `origin_story`, so it is filed there, not pre-emptively |

**Minions-side removal surface (verified by scan, 2026-08-03):**

- `minions_core/apaa/` — the package; and the stale `build/lib/minions_core/apaa/` build artifact
- `tests/apaa/` — the full APAA test tree, including the cartridges
- `tests/security/test_apaa_secret_containment.py` · `tests/governance/test_apaa_standing_red_baseline_gate.py`
- `scripts/check_apaa_standing_red_baseline.py` · `scripts/apaa_standing_red_baseline.txt`, and any CI job invoking them
- `pyproject.toml` — the `[project.optional-dependencies] apaa` extra (line 25), the
  `apaa = "minions_core.apaa.cli:main"` console script (line 38), and the explanatory comments (lines 17–20, 35–36)
- `.apaa/` — the runtime artifact directory at the Minions repo root. ⚠️ **Refined by IN-3:** `.apaa/` is
  the artifact tree of an *audited* repo, and under integration Minions **is** an audited repo — so this is
  **gitignored, not deleted as wiring**
- `CLAUDE.md` §4a — the APAA Component → Driver Map row(s)
- ⚠️ **302 files** across Minions mention `apaa` (code, config, docs, BMAD artifacts). The removal must
  **partition** them: *wiring* (remove) vs *evidence and history* (supersede per RS-3). An
  undifferentiated sweep would destroy the audit trail — which, on an assurance product, is the one
  thing that must not happen.

**Honest scoping note — RS-2 executes in a different repository.** The Minions decommission is real,
enumerated work, but it lands in `d:/ProjectX/XAgents/XAgents/Minions`, not in this repo. It therefore
cannot be verified by this repo's test suite or CI, and it is sequenced **after** the FR16/FR4 amendment
ships in `argus/` (removing the old copy before the new one is correct would leave a window with no
working verdict gate anywhere). Whether it becomes a story in *this* breakdown or a change request filed
against the Minions backlog is a decision for the epic-design step.

**What is already clean:** ArgusAgent has **no hard runtime dependency** on Minions. The single real
import — `argus/audit/minions_llm_adapter.py:21` — is guarded (`try/except ImportError` →
`MINIONS_CORE_AVAILABLE`), so the package installs and runs standalone today. RS-4 is stale prose, not
broken coupling.

### Integration Requirements (IN) — Argus consumed by Minions, 2026-08-03

The other half of the migration. Minions consumes Argus **as a product**, never as vendored source.

| IN | Requirement | Current state (verified) |
|---|---|---|
| **IN-0** | **Make `argus-agent` resolvable by Minions CI — the distribution must exist.** Publish to PyPI, to a private index, or (the honest interim) pin an explicit `git+https://github.com/Inan15/Agent-Argus.git@<tag>` VCS reference, and add the release workflow that produces it | ❌ **Open — and it BLOCKS IN-1.** ⚠️ **Assumption A1, falsified 2026-08-03:** ArgusAgent's `.github/workflows/` contains exactly one file, `audit-ci.yml` — **there is no release or publish workflow**, and `argus-agent` `0.1.0` is on no index. IN-1 as originally written depended on a distribution that does not exist |
| **IN-1** | **Consume `argus-agent` as an external package.** Replace the `[project.optional-dependencies] apaa` extra (`pyproject.toml:25-33`) and the `apaa = "minions_core.apaa.cli:main"` console script (`:38`) with a dependency on the published `argus-agent` distribution, exposed as an **optional extra** (`minions[argus]`) | ❌ **Open.** Minions declares `dependencies = []` — a hard dependency would break that discipline, so the extra is the only correct shape. **Ships together with RS-2** |
| **IN-2** | **Break the dependency cycle — hard prerequisite.** Once Minions depends on Argus, Argus must not depend on Minions. Retire the guarded `import minions_core.providers` at `argus/audit/minions_llm_adapter.py:21` in favour of the already-shipped `argus/audit/open_llm_adapter.py::OpenLLMAdapter`, making the edge strictly one-directional: **Minions → Argus** | ❌ **Open**, but cheap: the import is already `try/except ImportError` and the replacement adapter already exists. **Blocks IN-1** |
| **IN-3** | **CI gate.** Minions CI invokes `argus audit .` as a headless gated step keyed to the exit-code wire contract (`0`/`2`/`3`/`1`), with `INSUFFICIENT_COVERAGE` (exit `3`) routed to **human review, never auto-proceed**. This is PRD Journeys 3 and 5 delivered against a real repo, and it retires `scripts/check_apaa_standing_red_baseline.py` + `tests/governance/test_apaa_standing_red_baseline_gate.py` | ❌ **Open.** Target surface: `.github/workflows/minions_core-ci.yml` (or `conformance-ci.yml`). **Depends on the FR16 amendment shipping first** — under the old table the gate would fire exit `2` on a repo with zero findings. 🚩 **Policy decision required BEFORE wiring (assumption A5, unsupported):** the amendment stops Minions being *falsely accused*; it does **not** make Minions pass. The 7.2 dogfood was row 4 (zero findings, critical clause unmet) → post-amendment `INSUFFICIENT_COVERAGE`, **exit `3`**, which still fails an unconfigured CI step by design. Land the gate **advisory / non-blocking first**, or blocking with explicit `--coverage-scope` / `--exclude-critical` tuning — decided up front, not discovered when CI goes red |
| **IN-4** | **Platform capability registration** — register Argus as an audit capability so a Minions Flow Orchestrator can dispatch an audit (PRD Journey 5; the strategic question *"does Minions have an audit agent?"*). Seam: `minions_core/interop/a2a_capability_registry.py`. **Depth LOCKED 2026-08-03 (operator decision): descriptor only** — the orchestrator can *discover and dispatch* an out-of-process CLI capability; full Flow-Orchestrator workflow-step wiring and programmatic verdict consumption are **deferred**, not in this delta | ❌ **Open**, scope locked (see the constraint below) |
| **IN-5** | **One coordinated migration.** RS-2 (remove vendored copy) + IN-1 (add external dep) land as a single change; IN-3 and IN-4 follow. Argus-side work (the FR16/FR4 amendment, IN-2) ships **before** any of it | ❌ **Open** — a sequencing constraint on epic design, not code |

**🚨 Binding architectural constraint on IN-4.** The APAA architecture places APAA **downstream of the
HTTP/A2A boundary**: *"a CLI/library, takes no A2A token, registers no FastAPI route (ADR #20 boundary
spirit). No web surface in V1."* This is enforced today by the committed import-isolation gate
(`argus.* ⊬ fastapi/uvicorn/starlette`). IN-4 must therefore register a **capability descriptor invoking
Argus out-of-process** (CLI + exit code + `.apaa/` artifacts) — **not** mount Argus in-process behind a
FastAPI route. Mounting it would break the import-isolation gate, the pure/impure boundary, and the
headless-only classification in one move.

**Why the cycle break (IN-2) is not optional.** Argus currently reaches *into* Minions for LLM dispatch
while Minions is about to depend on Argus for auditing. Two repos importing each other cannot both be
installed from a clean index, and it would make the audit tool a dependency of the thing it audits — an
independence problem on an assurance product, not merely a packaging one.

### Open deferred-work interaction

No open entry in [deferred-work.md](deferred-work.md) sits in the amendment's code path. Two are
**downstream consumers** of it: **DF-7-2-A** (human TP/FP precision adjudication over the real dogfood
findings) and **DF-6-6-A** (≥80%-precision gate flip) both read the dogfood artifacts that DR-10 makes
stale — the adjudication should run against re-derived artifacts, not pre-amendment ones. DF-2-3-B
(persisting the computed `CriticalSubsystemSet`) is **closed** and its persisted shape is what DR-5's
eligibility filter must keep honest.

### UX Design Requirements

**None.** APAA is headless by design (PRD `headless: true`, `skipSections: [ux_ui, visual_design,
user_journeys]`); CLAUDE.md §3.7 forbids authoring one. The amendment's entire operator surface is the
verdict artifact, the exit code, and the stderr human register shipped by the landed CR-2 work.

## Delta Epic List

**Two epics**, numbered to continue from the shipped Epic 7. **Sequencing: `8 → 9`.**
**Both execute in the Argus repo.** All Minions-repo work is a handoff (see §Minions-Repo Handoff),
per the operator scope decision of 2026-08-03.

> **Subtraction pass applied 2026-08-03.** An earlier draft had five epics. Three removals were made and
> are recorded here so the reasoning is not lost:
> - **A standalone "Argus Stands Alone" epic was dissolved.** Its stated outcome is **already true**:
>   `pyproject.toml` declares no Minions dependency (`pydantic`, `jsonschema`, `radon`, `httpx`,
>   `tree-sitter`) and the single `minions_core` reference is already `try/except ImportError`-guarded, so
>   `pip install argus-agent` from a clean index already works with no Minions present. What genuinely
>   remained — a committed regression gate plus deleting a dead adapter branch — is **one story**, and it
>   is Epic 9's first story because Epic 9 is the only thing it gates.
> - **"A Record That Matches the Contract" was merged into Epic 8.** Keeping it separate would license
>   shipping the amendment while the published dogfood proof still asserts a verdict the tool would no
>   longer render. On an assurance product, evidence that contradicts the tool is the cardinal defect —
>   closing Epic 8 must not be possible while it stands.
> - **The bulk provenance-prose sweep (RS-4b) was deferred** out of the delta; only the package front
>   door (RS-4a) is carried.

### Epic 8: The Honest Verdict — no block without a finding · *Argus repo*

An operator running `argus audit` on a repository where Argus found nothing wrong receives **"I did not
examine enough to vouch"** (`INSUFFICIENT_COVERAGE`, exit `3`) instead of a verdict asserting a defect it
never found — and the verdict discloses **which decision row fired** and over **what assessed population**.
Critical-subsystem gates become satisfiable rather than permanently unreachable. **The amendment ships
with its evidence:** the published proof artifacts are re-derived under the amended table, and integrators
get a written migration note, so no Argus artifact contradicts the shipped contract.

**Covers:** DR-1 … DR-11 *(DR-7 is verify-only — already landed)* + RS-4a — **FR16 + FR4 (amended)**
**NFRs:** D1, D2, D3, P1, M2
**Files:** `argus/verdict/verdict_gate.py`, `argus/ledger/critical_subsystems.py`,
`argus/reports/plain_english.py` + `tests/test_plain_english.py` (DR-11), `argus/__init__.py`,
the dogfood/report artifacts
**Story ordering constraint:** DR-10 (the dogfood re-derivation — the one heavy, non-code item) is the
**last** story, so if it slips it slips *visibly* rather than silently.
**Standalone:** yes — requires no later epic.

### Epic 9: Make Argus Consumable — stand alone, then ship a release · *Argus repo*

Argus has no import path into the thing it audits, and exists as an **installable, versioned artifact**
another repository can depend on. This is everything the Argus repo owes the integration; the Minions-side
adoption is a handoff (below), not an epic here.

**Covers:** IN-2 + RS-1, IN-0
**Depends on:** Epic 8 (a correct package to release).
**Story 9.1 — break the cycle (IN-2 / RS-1):** retire the guarded `import minions_core.providers` in
favour of the shipped `OpenLLMAdapter`, and add a committed `argus.* ⊬ minions_core` gate mirroring the
existing `⊬ fastapi/uvicorn/starlette` pattern. Argus already installs standalone; this **keeps** it that
way once Minions depends on it.
**Story 9.2 — ship a resolvable distribution (IN-0):** there is no release/publish workflow in ArgusAgent
today (assumption A1, falsified), so nothing exists for Minions to depend on.

> **Scope decision, 2026-08-03 (operator).** The Minions-repo execution work — **RS-2, RS-3, IN-1, IN-3,
> IN-4** — is **removed from this breakdown**. It is prompted and executed in the Minions repository, and
> ArgusAgent's specs carry only work ArgusAgent's own CI can verify. The full requirement detail and the
> enumerated removal surface are preserved in **§Minions-Repo Handoff** below, to be filed as a change
> request against the Minions backlog. The integration remains **planned in full** — it is relocated, not
> dropped.

### Delta Requirements Coverage Map

| Requirement | Epic | Capability |
|---|---|---|
| DR-1 | Epic 8 | Binding 4-row decision table, findings before coverage |
| DR-2 | Epic 8 | Row 4 — zero findings + unmet gate → `INSUFFICIENT_COVERAGE`, exit `3` |
| DR-3 | Epic 8 | Verdict discloses the decision row + assessed population |
| DR-4 | Epic 8 | `VERDICT_SCHEMA_VERSION` `"1"`→`"2"`; prior verdicts not rewritten |
| DR-5 | Epic 8 | Heuristic critical-set eligibility filter |
| DR-6 | Epic 8 | Operator `--critical-subsystem` designation exempt |
| DR-7 | Epic 8 | Prefix/glob `--exclude-critical` — **verify-only** (already landed) |
| DR-8 | Epic 8 | Integrator migration / release note |
| DR-9 | Epic 8 | Schema bump is the only intentional byte change |
| DR-10 | Epic 8 | Re-derive the stale dogfood + verdict-report artifacts *(last story)* |
| DR-11 | Epic 8 | Reconcile **both** report surfaces — `plain_english.py` (unreachable branch) and `generator.py` (critical-paths section) |
| RS-1 | Epic 9 | `argus/` is the only live tree — enforced by a committed gate |
| RS-2 | **Minions handoff** | Remove APAA wiring from Minions |
| RS-3 | **Minions handoff** | Supersede, don't erase, the historical record |
| RS-4a | Epic 8 | Package front door (`argus/__init__.py:37`) |
| RS-4b | — | **Deferred out of the delta**; filed as a `deferred-work.md` entry |
| IN-0 | Epic 9 | Publish/resolve `argus-agent` — **blocks IN-1** *(story 9.2)* |
| IN-1 | **Minions handoff** | `minions[argus]` external dependency |
| IN-2 | Epic 9 | Break the dependency cycle *(story 9.1)* |
| IN-3 | **Minions handoff** | CI gate on the Argus exit code |
| IN-4 | **Minions handoff** | Capability registration (descriptor only) |
| IN-5 | — | Sequencing constraint: `8 → 9` here, then the Minions handoff |

**Every delta requirement is accounted for**: all 11 DRs + RS-1 + RS-4a + IN-0 + IN-2 map to Epics 8–9
here; RS-2, RS-3, IN-1, IN-3, IN-4 are relocated to the Minions-repo handoff with full detail preserved;
RS-4b is deferred with a recorded reason. No epic depends on a later epic to function.

### Assumption audit — outcomes carried into the plan (2026-08-03)

| # | Assumption | Outcome | Where it landed |
|---|---|---|---|
| **A1** | `argus-agent` is published where Minions CI can resolve it | ❌ **Falsified** — only `audit-ci.yml` exists; no release workflow, no index presence | **New IN-0**, blocking IN-1 |
| **A9** | Nothing downstream is coupled to the old decision-table ordering | ❌ **Falsified** — `plain_english.py`'s "NOT VOUCHED" branch becomes unreachable | **New DR-11** |
| **A5** | Minions can adopt the CI gate as blocking on day one | ⚠️ **Unsupported** — Minions lands on row 4 → exit `3`, which still fails CI | Policy flag on IN-3 / handoff **H3** |
| **A4** | No production Minions code imports `minions_core.apaa` | ✅ **Confirmed** — sole importer is a test already on the removal list | De-risk note on RS-2 |
| **A8** | The schema bump preserves read-back of pre-amendment verdicts | ⚠️ Conditional — `extra="forbid"` demands a default on the new field | Binding AC on DR-3 |
| **A3** | The 2026-06-18 placement decision exists and can be superseded | ✅ Verified present in Minions | RS-3 (unchanged) |
| **A2** | DR-10's dogfood re-derivation is feasible and affordable | ⚠️ Untested — a cheaper analytic re-derivation may suffice (the row-4 outcome is already known) | Flagged for story design |
| **A7** | `OpenLLMAdapter` is a drop-in for the `minions_core` provider path | ⚠️ Untested — `tests/test_minions_llm_adapter.py` exists and may pin the old behaviour | Flagged for Epic 9 story A |

---

## Epic 8: The Honest Verdict — no block without a finding · *Argus repo*

An operator running `argus audit` on a repository where Argus found nothing wrong receives
`INSUFFICIENT_COVERAGE` (exit `3`) instead of a verdict asserting a defect it never found, can see **which
decision row fired** and over what population, and finds **no published Argus artifact contradicting the
shipped contract**. Critical-subsystem gates become satisfiable.

**Covers:** DR-1 … DR-11 *(DR-7 verify-only)* + RS-4a · **FR16 + FR4 (amended)** · NFR-D1/D2/D3, P1, M2
**Dependency flow:** 8.1 and 8.2 are each standalone; 8.3–8.5 build only on earlier stories.

### Story 8.1: Findings before coverage — the binding decision table

As an operator running `argus audit`,
I want a blocking verdict only when Argus actually found something,
So that a coverage shortfall is never reported to my team as a defect.

**Acceptance Criteria:**

**Given** a ledger with ≥1 verdict-blocking finding at or above the 20% floor
**When** the verdict is evaluated
**Then** it is `NOT_READY_FOR_RELEASE` / exit `2` — findings are evaluated *before* coverage (row 2, DR-1).

**Given** a ledger with **zero** blocking findings and an unmet coverage or critical-subsystem gate (ratio ≥20% but <60%, or a critical path not deep)
**When** the verdict is evaluated
**Then** it is `INSUFFICIENT_COVERAGE` / exit `3`, never `NOT_READY_FOR_RELEASE` (row 4, DR-2)
**And** this is demonstrated **RED-first** against the current three-row implementation.

**Given** `assessed_total == 0` or `assessed_ratio < 1/5`
**When** the verdict is evaluated
**Then** it is `INSUFFICIENT_COVERAGE` / exit `3` — row 1 keeps precedence over the findings row.

**Given** a ledger **below the 20% floor that also carries ≥1 blocking finding**
**When** the verdict is evaluated
**Then** it is `INSUFFICIENT_COVERAGE`, **never** `NOT_READY_FOR_RELEASE` — the LOCKED *floor-vs-blocking precedence = FLOOR WINS* invariant survives the reorder.
*(Boundary B2: this story's own headline — "findings before coverage" — reads as "put the blocking row first", which would break this. It is the single most likely defect the reorder can introduce.)*

**Given** a ledger where **every coverage gate passes** — ratio ≥ 60%, all critical subsystems deep — **and exactly one blocking finding exists**
**When** the verdict is evaluated
**Then** it is `NOT_READY_FOR_RELEASE` / exit `2` (row 2) — the case a healthy repo actually hits.

**Given** a ledger at **exactly** `assessed_ratio == 1/5` with zero blocking findings and an unmet gate
**When** the verdict is evaluated
**Then** the verdict is `INSUFFICIENT_COVERAGE` and the **disclosed row is 4, not 1** — the floor is strict (`<`), so exactly-20% is assessable. Rows 1 and 4 are otherwise indistinguishable by verdict and exit code, which is precisely why the row must be disclosed (boundary B4).

**Given** the boundary constants
**When** the decision table is reordered
**Then** they are **unchanged**: `RELEASE_READY` at `assessed_ratio >= 3/5` (**inclusive**) and the floor at `< 1/5` (**strict**) — a reorder is exactly when an off-by-one creeps in.

**Given** any evaluated verdict
**When** the artifact is serialized
**Then** it discloses **which row fired** and the **assessed population** (DR-3)
**And** the new field carries a **default**, so a pre-amendment persisted verdict still round-trips under `extra="forbid"` (assumption A8).

**Given** the amendment
**Then** `VERDICT_SCHEMA_VERSION` is `"2"`, and verdicts already persisted under `.apaa/` are **not rewritten** and keep their `"1"` stamp (DR-4).

**Given** the disclosed row must reach a consumer
**When** the run completes
**Then** the row surfaces **per the LOCKED channel decision below** — explicitly on the verdict artifact, in prose on the stderr human register (Story 8.3), and **not** as a new field on the stdout machine summary line, which stays byte-identical.

> **🔒 CHANNEL DECISION — LOCKED 2026-08-03 (operator).**
> **Artifact: explicit field.** Mandated by FR16 (*"the verdict must disclose which row fired"*), and free
> of compatibility cost because `schema_version` is bumping anyway (DR-4).
> **stdout summary line: UNCHANGED.** The row is **already fully derivable** from what the line prints —
> `verdict=<TOKEN> deep_ratio=<num/den> blocking_findings=<n>` (+ `assessed_deep_ratio`/`scope` when
> narrowed): `INSUFFICIENT_COVERAGE` with assessed ratio `< 1/5` ⇒ row 1; `NOT_READY_FOR_RELEASE` ⇒ row 2
> (the only path to it post-amendment); `RELEASE_READY` ⇒ row 3 (likewise); `INSUFFICIENT_COVERAGE` with
> assessed ratio `>= 1/5` ⇒ row 4. Adding a field would be a **second** wire-contract change stacked on
> the exit-code shift, for information already present, against a line `argus/cli.py` documents as
> positionally parsed.
> **Precedent:** the addendum rejected a `COVERAGE_GATE_UNMET` enum value on exactly this reasoning —
> *"the distinction is already recoverable from the disclosed ratio and assessed population."* Deciding
> otherwise here would contradict a decision taken the same day.
> **Accepted residual risk:** a consumer that derives the row reimplements a slice of the decision
> table — the fragility that caused this bug. Mitigated by the artifact carrying the row
> authoritatively, so any consumer needing certainty reads it there rather than re-deriving.
> *(Corrects an earlier draft of this AC, which claimed a stdout-parsing consumer could not distinguish
> row 1 from row 4. It can — from the ratio the line already carries.)*

**Given** two evaluations over the same synthetic ledger
**When** compared byte-for-byte
**Then** they are identical, and the schema bump plus the new field are the **only** intentional content-hash change (DR-9)
**And** the gate remains pure — zero LLM tokens, no I/O, no clock (NFR-D2).

### Story 8.2: Critical-subsystem gates an operator can actually satisfy

As an operator,
I want the critical-subsystem gate to contain only files Argus can grade `audited_deep`,
So that the gate is a real signal rather than one I learn to ignore.

**Acceptance Criteria:**

**Given** test files that `assess_criticality` flags CRITICAL from security tokens in their content
**When** the **heuristic** critical set is derived
**Then** they are excluded — a test file is `audited_shallow` by construction (DR-5).

**Given** a clean-parsed module with zero definitions (`__init__.py`, constants-only, re-export)
**When** the heuristic set is derived
**Then** it is excluded — nothing exists in it to ground a claim against (DR-5).

**Given** an operator passes `--critical-subsystem` for a test file, a zero-definition module, **or a path matching nothing**
**When** the set is derived
**Then** the designation is honoured and can still withhold `RELEASE_READY` — operator designation is exempt from the eligibility filter (DR-6).

**Given** `--exclude-critical` with an exact path, a directory prefix, and a glob
**When** applied
**Then** all three match via `fnmatchcase` (case-sensitive, host-independent) — a regression pin on already-landed behaviour, no new implementation (DR-7).

**Given** a repository whose critical hits were **all** test files, so the eligibility filter empties the critical set
**When** the verdict is computed
**Then** the **empty critical set is disclosed**, and it is never reported as "all critical subsystems examined deeply" — a vacuously-satisfied gate must be visible, since a silent vacuous pass is the exact defect class this product exists to name (boundary B3).

**Given** a path that is **both** operator-designated (`--critical-subsystem`) **and** operator-excluded (`--exclude-critical`)
**When** the set is derived
**Then** a single explicit precedence order governs — eligibility filter vs designation vs exclusion — and it is pinned by test rather than left to implementation order (boundary B5).

**Given** a repository where a genuinely security-relevant module is `audited_shallow` and **not** operator-designated — for example a clean-parsed zero-definition `__init__.py` that re-exports a security boundary
**When** the eligibility filter removes it from the heuristic critical set
**Then** a defect-bearing case proves the loosened gate still **withholds** `RELEASE_READY` where it should, and the residual exposure is documented
*(Inversion F1 — the **false-green counterweight**. Every other guard in this delta points at "don't over-block", but the net effect of DR-5 plus the already-landed `--coverage-scope application` default is that `RELEASE_READY` becomes **easier** to reach. The PRD names **zero false-`RELEASE_READY`** as the fatal error, and the existing clean-control cartridges only guard the false-**red** direction. Without this AC the delta loosens the gate twice with nothing testing the loosening.)*

**Given** ArgusAgent audited against itself with defaults
**When** the heuristic critical set is derived
**Then** the previously unreachable blockers (51 test files + 10 `__init__.py`) are gone — the measured 62 → ~0.

### Story 8.3: The plain-English report stops describing an impossible state

As an operator reading the human output,
I want the report to describe only states the gate can actually produce,
So that I am not shown a branch the tool can no longer reach.

**Acceptance Criteria:**

**Given** a `NOT_READY_FOR_RELEASE` verdict
**When** it is rendered
**Then** it reads "BLOCKED — N verdict-blocking finding(s)" with **N ≥ 1 always** — the zero-finding blocking case is unreachable after Story 8.1.

**Given** `argus/reports/plain_english.py`
**When** its branches are audited
**Then** the trailing "NOT VOUCHED" else-branch is either **removed as unreachable** or retained **with a proof of reachability** — it is not left as untested dead code (DR-11).

**Given** `tests/test_plain_english.py`
**When** the suite runs
**Then** no test asserts a state the amended gate cannot produce; cases pinning the zero-finding/blocking split are re-pointed to `INSUFFICIENT_COVERAGE`.

**Given** two `INSUFFICIENT_COVERAGE` verdicts — one from row 1 (below the floor) and one from row 4 (gate unmet, nothing found)
**When** each is rendered for a human
**Then** they read **differently**: *"I examined too little to say anything"* versus *"I examined plenty and found nothing, but a coverage or critical-subsystem gate was not met."* Both carry exit `3` and the same enum, so the human register is the **only** surface where an operator can tell which action is called for (boundary B4).

**Given** `argus/reports/generator.py` — the **second** verdict-rendering surface, with its own FR16 reasoning
**When** Story 8.2's eligibility filter empties the critical set
**Then** its *"critical paths that withheld `RELEASE_READY`"* section (`:104`, `:122`) renders correctly for an **empty** set, and its *"each must reach `audited_deep`, or be excluded"* guidance no longer instructs an operator to act on paths the filter now removes automatically
**And** its independent branches on the verdict enum, deep-ratio threshold and `blocking_finding_count` (`:62-79`, `:304`) agree with the amended table.

**Given** any run
**When** the machine summary line is emitted
**Then** it is **byte-identical to the pre-amendment format** — `verdict=<TOKEN> deep_ratio=<num/den> blocking_findings=<n>` (+ `assessed_deep_ratio`/`scope`/`held_out` when narrowed) — carrying **no** new decision-row field, per the Story 8.1 LOCKED channel decision
**And** a golden test pins the format so the row is never appended to stdout by drift
**And** the existing determinism and secret-safety properties of both report surfaces remain pinned.

### Story 8.4: Tell integrators what changed

As a CI integrator,
I want a written statement of the exit-code behaviour change,
So that I can tell whether my pipeline needs to change (it likely does not).

**Acceptance Criteria:**

**Given** the amendment has shipped
**When** an integrator reads the release note
**Then** it states that some runs which exited `2` now exit `3`; that a step branching only on `0` vs non-zero is unaffected; and that a step distinguishing `2` from `3` now receives the correct one **with no consumer code change** (DR-8).

**Given** an artifact consumer that validates `schema_version`
**When** it reads the note
**Then** the note also states the **`VERDICT_SCHEMA_VERSION` `"1"` → `"2"` bump** and the new disclosed-row field — a consumer-visible change the exit-code framing alone conceals (boundary B8).

**Given** the `--coverage-scope application` default flip landed earlier without a published note
**Then** the same release note carries it — a pipeline relying on the whole-repository denominator must pass `--coverage-scope repository` explicitly.

**Given** `argus/__init__.py`
**When** read
**Then** it no longer claims the package lives at `minions_core/argus/` (RS-4a).

**Given** the bulk provenance sweep is out of scope
**Then** RS-4b is filed in `deferred-work.md` with the six mandatory fields and this story as its `origin_story`.

### Story 8.5: Re-derive the proof so the evidence matches the tool

As the XAgents platform owner,
I want the published proof artifacts to agree with the shipped contract,
So that Argus is not itself over-claiming — the defect it exists to detect.

> ⚠️ **Precondition — this story starts on a red test file.** `tests/test_dogfood_plan.py` carries **two
> pre-existing failures**, confirmed by running it: `test_committed_partition_plan_artifact_exists_and_matches_live_derivation`
> and `test_budget_reuses_the_31_accountant_no_fork`. They were present on the clean tree at `ae5f00c`
> and are **unrelated to this delta** — but their subject is *the dogfood artifacts this story touches*
> (committed plan stale vs live derivation; `431` absent from the committed budget artifact). The story
> must state explicitly whether it **fixes** them or **leaves** them, and must not absorb them silently
> into the delta's result.

**Acceptance Criteria:**

**Given** the Story 7.2 dogfood recorded `NOT_READY_FOR_RELEASE` / exit `2` at deep-% `13/15` with **0** verdict-eligible findings
**When** it is re-derived under **both** the amended decision table (8.1) **and** the amended critical-set eligibility (8.2)
**Then** the artifact records **whatever outcome honestly results**, together with the row that fired and the inputs it was computed from (DR-10).

> ⚠️ **This AC deliberately does NOT pin an expected verdict** (boundary B1). Story 8.2 changes the
> inputs: the dogfood's *only* blocker was the critical-subsystem clause, and DR-5 exists to clear
> unreachable critical paths. At 87% deep with zero blocking findings, clearing that clause moves the
> run to **row 3 → `RELEASE_READY` / exit `0`** — not row 4 as an earlier draft of this story asserted.
> Pinning a predetermined verdict on an assurance tool's own proof artifact invites the story to be
> "made to pass," which is the failure mode this product exists to name.

**Given** the re-derivation lands on `RELEASE_READY`
**When** the artifact is published
**Then** it still carries the hard `grade: demo-heuristic-only` flag and is **not** presented as externalization evidence — a green result from a Tier-A heuristic run is reportable, never a clearance.

**Given** re-derivation may be analytic rather than a fresh run
**When** the method is chosen
**Then** the artifact **discloses which** — a re-run cites its commit pin and budget; an analytic re-derivation names the inputs it folded and states plainly that **no new audit was executed**.

**Given** `_bmad-output/reports/final-verdict.md` and `_bmad-output/audit-reports/final-verdict.md`
**When** inspected
**Then** both agree with the amended contract.

**Given** DF-6-6-A and DF-7-2-A depend on these artifacts
**Then** an **append-only** note records that the precision adjudication must run against re-derived artifacts — the original entries are not rewritten (§3.4 evidence immutability).

**Given** the ≥80%-precision externalization gate
**Then** it stays **PROVISIONAL** — this story does not flip it.

**Given** the operator command that triggered this entire amendment — `argus audit .` on ArgusAgent, which returned `verdict=NOT_READY_FOR_RELEASE deep_ratio=11/28 blocking_findings=0`
**When** that exact command is re-run after Stories 8.1–8.4
**Then** the reported symptom — **a blocking verdict carrying zero findings** — is **not reproducible**, and the actual result is recorded
*(Inversion F5 — this is the acceptance test for the delta as a whole. Without it every AC could pass while the originally-reported behaviour survives through a path nobody modelled.)*

---

## Epic 9: Make Argus Consumable — stand alone, then ship a release · *Argus repo*

Argus has no import path into the thing it audits, and exists as an installable, versioned artifact
another repository can depend on. This is everything the **Argus repo** owes the Minions integration.

**Covers:** IN-2 + RS-1 (9.1), IN-0 (9.2) · **Depends on Epic 8** (a correct package to release)
**Dependency flow:** 9.1 is standalone; 9.2 builds on 9.1 so the released artifact is already cycle-free.

### Story 9.1: Argus stops importing the thing it audits

As the Argus maintainer,
I want Argus to have no import path into Minions,
So that Minions can depend on Argus without creating a cycle between the auditor and the audited.

**Acceptance Criteria:**

**Given** `argus/audit/minions_llm_adapter.py`
**When** the module is imported
**Then** it references `minions_core` in no form, and the dispatch path routes through the shipped `argus/audit/open_llm_adapter.py::OpenLLMAdapter` (IN-2).

**Given** `tests/test_minions_llm_adapter.py` may pin the old behaviour (assumption A7, untested)
**When** the import is retired
**Then** each affected test is re-pointed at the `OpenLLMAdapter` path or removed **with a recorded reason** — no test is left asserting a code path that no longer exists.

**Given** a committed gate test
**When** `argus.*` is imported in a fresh interpreter
**Then** `minions_core` is absent from `sys.modules` — mirroring the existing `tests/test_no_web_imports.py` pattern (RS-1).

**Given** a clean environment with Minions **not** installed
**When** `argus audit` runs against a fixture repo
**Then** it completes and emits a verdict — standalone operation is **proven**, not assumed.

**Given** `MinionsLLMAdapter` no longer touches Minions
**Then** it is renamed additively (keeping an alias) **or** the retained name is justified in its docstring — a class named for a dependency it no longer has is a future misreading.

### Story 9.2: Ship a distribution another repo can actually resolve

As a downstream integrator,
I want `argus-agent` to exist as an installable, versioned artifact,
So that I can depend on it instead of vendoring a copy that drifts.

**Acceptance Criteria:**

**Given** ArgusAgent has no release workflow today — only `audit-ci.yml` (assumption A1, falsified)
**When** this story completes
**Then** a release workflow produces an installable artifact for a tagged version, and that tag is recorded.

**Given** a consumer's CI must resolve the artifact
**When** the distribution target is chosen — PyPI, a private index, or a `git+https://…@<tag>` VCS pin
**Then** the choice is recorded **with its access requirements**; a private index or VCS pin must state how a consumer's CI authenticates, and a VCS pin is explicitly marked **interim** with the condition for moving to an index.

**Given** `argus-agent` is at version `0.1.0`
**Then** the released version is **pinned and published**, so a consumer can cite an exact version — no floating dependency on an unreleased tree.

**Given** the release artifact
**When** installed into a clean environment
**Then** `argus --help` and a fixture audit both succeed — the artifact is proven, not merely built.

**Given** the release edge cases
**When** a tag or version already exists, a re-tag is attempted, or the working tree is dirty at build time
**Then** the workflow behaves explicitly — refusing a dirty-tree build and refusing a silent overwrite of an existing version — rather than producing an artifact whose provenance cannot be established (boundary B10).

---

## Minions-Repo Handoff — not epics in this breakdown

> **Operator scope decision, 2026-08-03.** RS-2, RS-3, IN-1, IN-3 and IN-4 execute in the **Minions
> repository** and are prompted there. They are recorded here in full so nothing is lost, and are to be
> **filed as a change request against the Minions backlog** — they are *not* stories in ArgusAgent's
> sprint, and ArgusAgent's CI cannot verify them. The integration remains planned in full; it is
> relocated, not dropped.

**Prerequisites before any of this can start:** Epic 8 (correct verdict contract) and Epic 9 (a
cycle-free, published `argus-agent`).

> 🚩 **H0 — FILING THIS HANDOFF IS ITSELF AN UNOWNED ACTION** (inversion F3). H1–H4 describe work in
> another repository; **no story in this breakdown owns filing them**, and no owner is named. A handoff
> nobody files is a handoff that does not exist — this is the single most likely way the integration
> quietly never happens. Before this delta is considered planned, one of the following must be true:
> **(a)** a named owner files H1–H4 against the Minions backlog with a link back to this section, or
> **(b)** it is explicitly recorded that filing is the operator's own step, taken outside this workflow.
> Silence is not an option — it is how this becomes a document nobody actions.

### H1 — Swap the vendored fork for the package *(RS-2 + IN-1, one change)*

Removal surface, verified by scan 2026-08-03:
`minions_core/apaa/` · the stale `build/lib/minions_core/apaa/` copy · `tests/apaa/` ·
`tests/security/test_apaa_secret_containment.py` · `tests/governance/test_apaa_standing_red_baseline_gate.py` ·
`scripts/check_apaa_standing_red_baseline.py` + `scripts/apaa_standing_red_baseline.txt` ·
`pyproject.toml` lines 17–20, 25–33, 35–38 (the `apaa` extra, the `apaa` console script, their comments).

- The **same** change adds an optional `argus` extra depending on the Story 9.2 pinned `argus-agent`.
  Minions declares `dependencies = []` — the dependency must be an **extra**, never a base dependency.
- **Safe to execute:** no production Minions module imports `minions_core.apaa` (assumption A4, verified —
  the sole importer outside the package and `tests/apaa/` is `tests/security/test_apaa_secret_containment.py`,
  itself on the removal list).
- `.apaa/` at the Minions root is **gitignored, not deleted** — under integration Minions is an audited
  repo and `.apaa/` is its artifact tree. ⚠️ **If it is currently git-tracked, `.gitignore` alone does
  nothing** — it needs `git rm --cached` as well, or the AC silently fails to achieve its stated outcome
  (boundary B9).
- CI jobs referencing removed scripts/tests are cleaned in the same change — green on landing.

### H2 — Supersede the record, don't erase it *(RS-3)*

- `_bmad-output/planning-artifacts/decisions/2026-06-18-apaa-placement-under-minions-core.md` gains a
  forward pointer to Agent-Argus + the superseding date; the original text is **not rewritten**
  (§3.4 evidence immutability).
- `_bmad-output/design-artifacts/APAA/` and `_bmad-output/implementation-artifacts/25-13-apaa-standing-red-disposition.md`
  are retained with a superseded marker — never deleted.
- ~302 files mention `apaa`; the sweep must **partition** them into *wiring* (removed in H1) and
  *evidence* (marked, retained), recording which rule applied to each.
- `CLAUDE.md` §4a Component → Driver Map: the APAA row **points at the external Argus product** rather
  than being silently deleted.

### H3 — CI gate on the Argus exit code *(IN-3)*

Minions CI invokes `argus audit .` as a headless gated step keyed to the wire contract (`0`/`2`/`3`/`1`),
with exit `3` routed to human review and never auto-proceed (PRD Journeys 3 and 5). Retires
`scripts/check_apaa_standing_red_baseline.py`. Target: `.github/workflows/minions_core-ci.yml`.

🚩 **Policy decision required before wiring (assumption A5, unsupported):** the amendment stops Minions
being *falsely accused*; it does **not** make Minions pass. The 7.2 dogfood was row 4 — zero findings,
critical clause unmet — so post-amendment Minions lands on `INSUFFICIENT_COVERAGE`, **exit `3`**, which
still fails an unconfigured CI step by design. Land the gate **advisory / non-blocking first**, or
blocking with explicit `--coverage-scope` / `--exclude-critical` tuning. Decide up front, not when CI
goes red.

### H4 — Register Argus as an audit capability *(IN-4, descriptor-only)*

Register Argus in `minions_core/interop/a2a_capability_registry.py` as a **discoverable, dispatchable
out-of-process** audit capability, so a Flow Orchestrator can dispatch an audit — answering *"does Minions
have an audit agent?"* with a running integration rather than a vendored copy.

🚨 **Binding architectural constraint.** APAA is **downstream of the HTTP/A2A boundary**: *a CLI/library,
takes no A2A token, registers no FastAPI route* (ADR #20). The registration must invoke Argus
**out-of-process** (CLI + exit code + `.apaa/` artifacts) and must **not** mount it behind a FastAPI
route — that would break the `argus.* ⊬ fastapi` import-isolation gate, the pure/impure boundary, and the
headless-only classification in one move. Full Flow-Orchestrator workflow-step wiring and programmatic
verdict consumption are **deferred** (depth LOCKED descriptor-only, 2026-08-03).
