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

**Repository Intake & Partitioning**
- **FR1:** An operator can submit a repository at a pinned commit for audit through a headless invocation.
- **FR2:** APAA can detect the repository's technology stack and available toolchain without operator configuration.
- **FR3:** APAA can partition the repository into bounded audit units within a declared budget.
- **FR4:** APAA can identify critical subsystems (and an operator can designate them) so coverage gates can require them to be examined deeply.

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
- **FR16:** APAA can emit a verdict only when coverage gates are met (≥60% deep + all critical subsystems deep + 0 blocking findings), and emit `INSUFFICIENT_COVERAGE` below the 20% floor — never a default block.
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
