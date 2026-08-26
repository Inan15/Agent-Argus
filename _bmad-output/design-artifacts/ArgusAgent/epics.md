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
    approvedBy: XAgent007
    stepsCompleted:
      - step-01-validate-prerequisites
      - step-02-design-epics
      - step-03-create-stories
      - step-04-final-validation
    status: 'complete'
    openDecisions:
      - 'H0 — who files the Minions-Repo Handoff (H1-H4) against the Minions backlog. CLOSED 2026-08-10b via the pre-authorised option (b): the operator (XAgent007) records filing as their own step, taken outside this workflow. No longer unowned; still not yet filed.'
    resolvedDecisions:
      - date: 2026-08-03
        id: 'Story 8.1 — decision-row disclosure channel'
        decision: 'Artifact = explicit field (FR16-mandated, free under the DR-4 schema bump). stdout machine summary line = UNCHANGED, pinned by a golden test. stderr human register = distinguishes row 1 from row 4 in prose.'
        rationale: 'The row is already fully derivable from the existing summary line (verdict token + assessed ratio): INSUFFICIENT_COVERAGE with ratio <1/5 => row 1; NOT_READY => row 2; RELEASE_READY => row 3; INSUFFICIENT_COVERAGE with ratio >=1/5 => row 4. Adding a stdout field would be a SECOND wire-contract change stacked on the exit-code shift, for information already present. Matches the addendum precedent that rejected COVERAGE_GATE_UNMET because the distinction was recoverable from the disclosed ratio and assessed population.'
        residualRisk: 'A consumer deriving the row reimplements a slice of the decision table. Mitigated: the artifact carries it authoritatively.'
        correction: 'An earlier AC draft claimed a stdout-parsing consumer could not distinguish row 1 from row 4. It can, from the ratio the line already prints.'
        approvedBy: XAgent007
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
driver_namespace: 'APAA-FR-* / APAA-NFR-* (1:1 onto PRD FR1–37 / NFR clusters)'
# CORRECTED 2026-08-10 (implementation-readiness-report-2026-08-10.md, Step 3 CRITICAL): read
# 'FR1–33' until now. The 2026-08-10b amendment added FR34–FR37 + NFR-S6/NFR-P3 to the PRD and
# wrote Epics 11/12/13 in full, but its edit manifest did not include this file's index layer —
# frontmatter, Requirements Inventory, FR Coverage Map, or Final Validation Summary. All four are
# corrected in this pass. `architecture.md` L467 was already correct at FR1–37; its L40/L48 were not.
---

# APAA (AI Project Assurance Audit) — Epic Breakdown

> **Scope note.** This is the epic/story breakdown for **APAA**, the SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It is distinct from the Minions
> platform epics (`_bmad-output/planning-artifacts/epics.md`). APAA reuses Minions infra **by import**
> but ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace, defined in the architecture document.

Date: 2026-06-18 · Primary sources: `E-PRD/prd.md` (**37 FRs / 23 NFRs**) + `architecture.md` (READY FOR IMPLEMENTATION)
*(Count corrected 2026-08-10 — read "33 FRs / 21 NFRs" from 2026-06-18 until the 2026-08-10b amendment's additions were reconciled into this document's index layer.)*
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
> **[Tier B]** = validation-grade additions over the demo-grade core (FR7, FR12, FR19, FR24, FR26, **FR36**).
>
> ⚠️ **FR34–FR37 and NFR-S6/NFR-P3 were added 2026-08-10b** by the V1.5 public-release amendment and are
> stated below in their **binding** form. They were absent from this inventory until 2026-08-10; the
> amendment wrote Epics 11/12/13 in full but did not reconcile this index layer.
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
- **FR36 (added 2026-08-10b):** An operator can enable an **LLM-backed deep-audit pass** that produces grounded claims beyond the zero-token path. **[Tier B]** **Off by default, always** — the default run is zero-token, offline, key-free and transmits nothing; enabling requires explicit operator action per invocation. **Egress is disclosed before it occurs** (what is transmitted, to which provider, before the first byte leaves). Spend flows through the **existing** FR21/FR22 ceiling — no new cost-governance mechanism. Determinism preserved via the FR27/NFR-D1 memoization path. Degradation is honest: an unavailable, erroring or budget-halted provider downgrades coverage and records a finding (NFR-R1) — never a false deep claim, never a crash. → source of truth `E-PRD/prd.md` FR36.
- **FR8:** APAA can exclude `inferred` (narrative/doc) evidence from satisfying any verdict gate.
- **FR9:** An operator can read exactly which files were examined deeply, shallowly, tool-scanned, inferred, or skipped.
- **FR37 (added 2026-08-10b):** APAA can state, on every terminal outcome, **why that outcome was reached and the next action that changes it**. Enumerated over the full verdict vocabulary — `RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE` and the `AUDIT_FAILED` non-verdict — **pinned by a test that fails on an unenumerated outcome**. `INSUFFICIENT_COVERAGE` is the load-bearing case: it must name the specific unmet gate (floor, ratio, or critical subsystem) and the action that would change it. **Self-contained** — the next action is in the tool's own output. **Names what was never examined, not only what scored low:** every verdict states which file classes were **not ingested**, distinguishing *never ingested* / *ingested but held out* / *assessed*; this extends FR17's scope statement to include the ingestion boundary. **Governs explanation, never classification** — FR16's decision table is untouched. → source of truth `E-PRD/prd.md` FR37.

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
- **FR34 (added 2026-08-10b):** APAA can disclose its own validation status on **every** user-facing verdict surface, and **cannot emit a verdict on a surface that omits it**. *Content:* the tool's finding-precision validation state (validated / **not independently validated**) and the corpus it rests on. **Mechanical enforcement, not editorial discipline** — the surface set is **enumerated in a committed test that fails on an unenumerated member**. **Distinct from FR17, and both apply:** FR17 bounds the scope of *this audit*; FR34 bounds the credibility of *the tool itself*. **Removable only on measurement, and replaced rather than deleted** — when the ≥80% gate clears, the disclosure is replaced by a statement of the cleared status and the clearing corpus; the enforcing test never becomes vacuous. **Not a permanent state:** coupled to a committed programme to clear the gate (**Epic 13**); if that programme is abandoned, the free public tier is **withdrawn** rather than the disclosure. → source of truth `E-PRD/prd.md` FR34.

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
- **FR35 (added 2026-08-10b):** A coding agent can invoke an audit and consume the verdict through a **local agent-integration surface**, without a human relaying it. **Two shipped forms:** an **MCP server** (stdio transport) and **packaged assistant command assets** the installer places in the host's configuration. **Bounded by the four §Project Classification constraints:** stdio only — no network listener opened, no port bound; **no HTTP stack**, preserving the `argus.* ⊬ fastapi` import-isolation gate and ADR #20 verbatim; **no new authority** — the same pure `AuditRequest → AuditVerdict` path as the CLI under the same work-manifest permission boundary (NFR-S4); **no credential handling**. **Verdict parity is asserted, not assumed:** the same repository at the same commit produces the same verdict through either surface, pinned by test. → source of truth `E-PRD/prd.md` FR35.

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
- **NFR-S6 (added 2026-08-10b):** **No source code, prompt, or repository content leaves the machine on the default path.** Third-party transmission occurs **only** through the explicitly enabled FR36 deep pass, is **disclosed before the first byte is transmitted**, and names the receiving provider. The FR35 agent-integration surface opens **no network listener and binds no port**. Both properties are enforced by committed gates in the shape of the existing import-isolation tests — **an egress path reachable without opt-in fails CI**.

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
- **NFR-P3 (added 2026-08-10b):** **The default public installation grounds the languages the tool claims to support.** A user who installs through the primary public channel and audits a repository in a documented supported language receives that language's grounding **without discovering an optional extra**. Coverage degraded by a grammar absent from the default install is a **packaging defect** — not a user error and not an honest limitation — and is reported as such. Where a language is deliberately not in the default install, its absence and the reason are stated **in the tool's own output at the point the file is downgraded**. ⚠️ Architecture L446 records this as an **open packaging decision owned by Story 12.5**: the 9 non-Python grammars are currently an optional extra, so the default install grounds Python only — the exact state this NFR classifies as a defect.

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
- **OI1 — Validation-set `N` → ⚠️ REOPENED 2026-08-10b; NOW OWNED BY STORY 13.1. The text below is the
  superseded 2026-06-18 lock, retained per §3.4 and marked, not deleted.**
  **What changed:** the PRD's §Open inputs block records `N` as **assigned, not answered** — PRD
  §Validation Approach (`N ≈ 5–10` **real repositories**) and `precision-validation-protocol.md` §5
  (`N ≥ 5` **labeled planted-defect cartridges**) specify **different corpora and were never reconciled**.
  They measure different quantities: cartridges measure **recall against known plants** (FR20, already
  delivered and CI-asserted); precision measures **how often a blocking finding on unplanted code is real**,
  and only the second gates externalization. **Story 13.1 decides which governs and amends the loser**;
  its recommendation of record is that **the PRD governs**.
  **"Minions first" is now false.** Story 8.5 re-derived the dogfood as a **self-audit of `argus/`**; the
  independent Minions run survives only at `minions-dogfood-proof-story-7-2-superseded.md` and *"can never
  be re-derived in this repository."* The corpus is **N=1 and self-referential**, and Story 13.1 is required
  to **exclude the self-audit from N** and rebuild from repositories Argus did not author.
  > ~~**LOCKED `N = 5` (V1 gate floor), Minions first.** The precision replay harness (Story 6.6) is
  > **designed for N = 5** (ground-truth schema/corpus shape), but **populated phased**: 3 labeled repos
  > front-loaded in M1 for early precision signal (PRD risk-forward intent), then grown to 5 before the
  > ≥80%-precision gate is declared cleared. Precision is measured over **findings**, not repos, so 5 repos
  > with sufficient findings support a defensible 80% number; the gate stays **provisional below N = 5**.
  > (PRD floor is the chosen value; ceiling 10 deferred to post-V1 if the finding-count denominator proves
  > thin.)~~ — *superseded 2026-08-10b; do not use this value for story context.*
- **OI2 — Minions-dogfood scope → LOCKED "full-repo multi-partition".** Story 7.1 partitions **all ~70
  Minions modules** into bounded ≤40-file/15k-LOC audit units and audits each (most complete proof
  artifact). **V1 limitation preserved:** this is multi-**unit** auditing, NOT the V2 cross-partition
  **seam auditor** — no seam analysis spans cut edges in V1 (the `cross_partition` Prosecutor pass,
  Story 6.4, re-reads cut edges as the V1 mitigation; full seam analysis is V2).
- **OI3 — Budget-ceiling `$X` → ✅ CLOSED / LOCKED (PRD §Open inputs, 2026-08-10b). The resolution is
  "there is no default."** `ceiling_credits: int | None`, **no numeric default**, `None` = no ceiling
  configured, `0 → None`. The operator sets it per target; sizing is **empirical per audited repository**
  (Story 7.1). A numeric default was **deliberately refused**: a wrong default silently truncates an audit —
  the failure NFR-C2 exists to prevent. Verified shipped: Story 3.1's code review confirms
  `BudgetConfig().ceiling_credits is None` with `0 → None` first-class.
  *(Corrected 2026-08-10 — this entry read "DEFERRED to empirical Story 7.1 sizing" after the PRD had
  locked it, which would tell a budget story the input was still open.)* The budget-ceiling *mechanism*
  (Story 3.1) and *halt behaviour* (Story 3.2) were never affected.

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
| **FR34** | **Epic 11** (11.1) | **Self-disclosure of validation status on every verdict surface** — re-asserted in 12.6 (MCP surface) and 12.9 (both listings); removal path is Epic 13 (13.3) |
| **FR35** | **Epic 12** (12.6, 12.7) | **Local agent-integration surface** — MCP stdio server + packaged command assets |
| **FR36** | **Epic 12** (12.2) | **Opt-in LLM-backed deep-audit pass** **[Tier B]** |
| **FR37** | **Epic 12** (12.4) | **Every terminal outcome names its next action** + the ingestion boundary |

**All 37 FRs mapped. All 23 NFRs land in ≥1 epic** (D1→E5, delivered E12/12.3; D2/D3/A1/M1/M2/S5→E1,
M1 enforced repo-wide E12/12.1; S2/S4/C3/R1/SC1→E2; C1/C2/R2/P1/P2→E3; S1/S3/A2/A3→E4; P2→E6;
**S6→E12/12.2; P3→E12/12.5**).

> **Correction, 2026-08-10** *(implementation-readiness-report-2026-08-10.md, Step 3 CRITICAL)*. This map
> read **"All 33 FRs mapped. All 21 NFRs…"** from 2026-06-18 until now, and FR34–FR37 / NFR-S6 / NFR-P3
> appeared in **neither** this map nor the Requirements Inventory above — they existed only in the per-epic
> inline `**Covers:**` lines of Epics 11 and 12. Root cause: the 2026-08-10b amendment's own edit manifest
> (`sprint-status.yaml`) lists *"epics.md (Story 10.2 AC1 → 10 sites + closing grep test; Story 10.5 added;
> Epics 11/12/13 written in full)"* — the index layer of this document was never in scope. Recorded as a
> dated correction rather than a silent rewrite (§3.4 evidence immutability).

> **Observation, 2026-08-24** *(sprint-change-proposal-2026-08-24.md)*. This map, the Requirements
> Inventory above and the Final Validation Summary below all stop at **Epic 13** — Epics 14, 15 and
> 16 never updated them, so the 2026-08-10 correction's root cause recurred three more times without
> being recorded. ⛔ **Epics 17 and 18 add NO row here, and that is correct rather than a repeat of
> the omission:** this map answers *"which epic DELIVERS this FR"*, and neither epic delivers a new
> one. Epic 17 **repairs** FR10's detector — its verdict-eligible stage promotes **0 of 1,032**
> (`DF-INV-VACUOUS-A`) — and Epic 18 **repairs** FR11's, where a real hardcoded secret is suppressed
> by a substring (`DF-AUD-DETECT-A`). ⚠️ **Do not read `FR10 | Epic 1` or `FR11 | Epic 2` as
> "finished there."** The Epic 14–16 index drift is **NOT** fixed by this proposal: it predates it
> and fixing it here would be scope creep. Recorded for the Epic 17 retrospective.

> **Correction, 2026-08-26** *(Story `17-5-nothing-points-at-a-closed-story`, measured at HEAD
> `b8eaeee`)*. The paragraph above says *"Epic 17 **repairs** FR10's detector"*. ⛔ **Epic 17 has now
> run, and it did not.** Stories 17.1–17.4 are `done` and Story 17.4's recorded outcome is
> **`UNEVALUABLE`**: sealed contributing members **0**, below the resolved floor of **3**;
> `measured_precision` **null**; 1,032 walked / 0 skipped; S1-eligible **85** across **3**
> contributing members; and the successor predicate `S1` shipped **ADVISORY**, so the
> verdict-eligible stage still promotes **0 of 1,032** — the same figure the paragraph above quotes
> as the reason the epic was needed. ⚠️ **The paragraph is left exactly as written** (§3.4 evidence
> immutability); it was the true intent when it was authored. The full correction, with every figure
> and the six surfaces it applies to, is recorded once in
> [deferred-work.md](deferred-work.md) under *"Story 17.5 dispositions — 2026-08-26"* §(e).

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

> ⚠️ **SCOPE OF THIS SUMMARY, clarified 2026-08-10.** This block was written on **2026-06-18** and validates
> the **7-epic base plan only**. It is **not** a validation of Epics 8–13 or of the FR34–FR37 / NFR-S6 /
> NFR-P3 additions. Until 2026-08-10 it asserted *"all 33 FRs"* / *"all 21 NFRs"* without that qualifier,
> which read as a current certification of a superseded contract — the defect class Story 10.1 exists to
> delete. Counts corrected and scope stated below; the base-plan findings themselves are unchanged.

- **FR coverage (base plan, Epics 1–7):** the 33 FRs then in force map to a story (see FR Coverage Map +
  per-epic story ACs). FR16 spans Epic 1 (gate+floor core) and Epic 2 (critical-subsystem clause); FR28
  spans Epic 2 (producer redaction) and Epic 4 (containment enforcement) — both deliberate, both fully
  delivered. **Post-amendment total: 37 FRs**, all mapped — FR4/FR16 amended by Epic 8, and FR34→Epic 11,
  FR35/FR36/FR37→Epic 12 (see the corrected FR Coverage Map above).
- **NFR coverage (base plan):** the 21 NFRs then in force land in ≥1 epic and are asserted by at least one
  story AC. **Post-amendment total: 23 NFRs** — NFR-S6→Epic 12 (12.2), NFR-P3→Epic 12 (12.5).
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
> FR4 (critical-subsystem eligibility), approved by XAgent007 at the contract gate — step 4 of the
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

## Epic 10: Specification Debt from the Separation — close the gate that let it through · *Argus repo*

Every capability ArgusAgent ships is specified, and the release gate refuses a verdict it
cannot evidence. This epic closes the debt the repo separation carried in: work that
entered the shipped contract without passing the story gate, and a release status that was
self-attested rather than proven.

**Covers:** DF-AUD-APAA-C (10.1), -D (10.2), -E (10.3), -F (10.4), the `standards_refs` V1/FR conflict
(10.5, added 2026-08-10b) · **Depends on Epic 9**
(a released artifact whose contract is worth correcting)
**Dependency flow:** 10.1 FIRST — it is the control that would have caught 10.2-10.4, and
fixing artifacts while the gate still accepts self-attestation invites recurrence. 10.2
before 10.3 (larger artifact blast radius). 10.4 is independent and may land at any point.

**What 10.1 hands to 10.2-10.4 is the STANDARD, not a number** *(amended 2026-08-10 by Story
10.1; see the amendment note under Story 10.1's third AC below)*. A GitHub Actions run id is
**sha-scoped**: run `31341363300` evidences sha `00c8d1b` and nothing else, so it cannot
evidence any tree that contains 10.2's, 10.3's or 10.4's own commits. Each of those stories
therefore cites **the `audit-ci.yml` run covering its OWN HEAD**, in the citation format 10.1
fixes — *run id **plus** the sha it covers* — or records the status as **NOT ESTABLISHED** and
names the command a human runs to establish it. Reusing 10.1's run id to evidence a later tree
would be the same defect this epic exists to close, one level up.

**Source:** [sprint-change-proposal-2026-08-09.md](sprint-change-proposal-2026-08-09.md)

> ### 📍 Citation audit — Epics 10–13, measured 2026-08-10
>
> Every `file:line` citation in the Epic 10–13 ACs was resolved against the working tree before story
> creation, because these ACs are drafted-not-yet-executed and `bmad-create-story` will carry their
> coordinates into the story files. **12 of 14 were exact; 2 had drifted and are corrected.**
>
> | Citation | Verified | Points at |
> |---|---|---|
> | ~~`argus/audit/deep_audit.py:91`~~ → `argus/audit/deep_audit.py:98` | ❌ **WAS WRONG, corrected 2026-08-13 (Story 12.2)** | `class DeepAuditSeam:` — measured at line **98**; line 91 is inside `build_closure_from_recording`'s kwargs dict. The ✅ was never earned: `architecture.md` §E stated `:91` too, and two documents agreeing read as verification without either having executed anything. **Anchor on the text, never the line number.** |
> | `argus/detectors/base.py:63-87` | ✅ exact | `class FindingDraft(BaseModel):` |
> | `argus/detectors/vacuous_test.py:198` | ✅ exact | the `"test.java", "spec.rb"` tuple line |
> | `argus/precision/replay_harness.py:87-90` | ✅ exact | the `sys.path` insert |
> | `argus/precision/replay_harness.py:223` | ✅ exact | `protocol_cleared: bool = False,` |
> | `argus/shared/source_languages.py:80` | ✅ exact | `AUDITABLE_SUFFIXES` |
> | `action.yml:74` (+`:78,79,80,126`) | ✅ exact | all five `run:` interpolation sites |
> | `pyproject.toml:59-62` | ✅ exact | `[project.scripts]` + the three aliases |
> | `README.md:138-150` | ✅ exact | the slash-command claim |
> | `tests/test_cache_invalidation.py:690` | ✅ exact | `test_invalidation_module_is_under_1200_lines` |
> | `tests/test_cartridge_selfaudit.py:472` | ✅ exact | `test_this_harness_is_under_1200_lines` |
> | `minions-dogfood-proof.md:87` | ✅ exact | the `N=0 … floor N=5` gate-status line |
> | ~~`argus/cli.py:295-299`~~ → **`:368-372`** | ❌ **corrected** | the base-`ValueError` arm (Story 12.8). ⚠️ **A second `except ValueError` exists at `:337`** (ship-readiness rendering) which no AC names — the split must decide both sites or state why one is exempt |
> | ~~`argus/dogfood/proof_run.py:764-765`~~ → **`:643-644`** | ❌ **corrected** | `precision=Fraction(0, 1), n=0` (Story 13.1) |
>
> **Also verified: none of Epics 11–13 is implemented.** `argus/mcp/` absent · `DeepAuditSeam` and
> `memo_store` still unreferenced by `pipeline.py` · `pipeline.py` at **1331 lines**, the only file over the
> NFR-M1 cap · FR34 tokens confined to `argus/dogfood/*`, absent from `cli.py` and `reports/` · `languages`
> still an optional extra · `git tag -l` empty and `release.yml` documenting its own abstention from index
> publish · `protocol_cleared` never passed `True`. Every story's stated precondition reproduces today.

### Story 10.1: A release status must cite evidence, not assert it

As the ArgusAgent maintainer,
I want a release-readiness statement to be refused unless it cites an executed gate,
So that ArgusAgent never publishes about itself the kind of unevidenced green it exists to
catch in other repositories.

**Acceptance Criteria:**

**Given** `sprint-change-proposal-2026-07-28.md` records *"Upgraded from NEEDS TARGETED
REWORK to READY FOR RELEASE!"* on the evidence of a local `pytest` run, while the same
proposal introduced `audit-ci.yml`
**When** that CI workflow's run history is inspected
**Then** its only run on `master` is `failure`, so the status was asserted over a gate that
had never passed — and the record is corrected in place with the correction dated and
reasoned, never silently rewritten (§3.4 evidence immutability).

**Given** any future change proposal or retrospective that states a release status
**When** it is written
**Then** it cites the CI run id (or an equivalent executed gate) that supports the claim, and
a status with no citable run is recorded as **NOT ESTABLISHED** rather than as a verdict —
mirroring the `AUDIT_FAILED`-is-not-a-verdict rule the action already publishes.

**Given** the repaired `audit-ci.yml`
**When** it runs on `master`
**Then** it passes on every matrix leg, and ~~that run id is the evidence 10.2-10.4 cite~~
**the citation STANDARD that run establishes is what 10.2-10.4 apply, each citing the run that
covers its own HEAD**.

> **Amended 2026-08-10 by Story 10.1 (§A.5).** The struck wording invited 10.2-10.4 to cite a
> number that predates their own code. Run ids are **sha-scoped**: run `31341363300` is
> `success` with 3/3 legs green over sha `00c8d1b` and evidences that tree only, so a story
> whose commits are not in `00c8d1b` cannot be evidenced by it. What 10.1 delivers and 10.2-10.4
> inherit is the **format and the rule** — *run id plus the sha it covers*, or **NOT
> ESTABLISHED** — recorded in `architecture.md` §H and enforced by
> `tests/test_evidence_citation.py`. Original wording struck rather than deleted (§3.4 evidence
> immutability).

### Story 10.2: Multi-language grounding is V1 in the specs, and its provenance is honest

As a downstream integrator auditing a non-Python repository,
I want the specs to state the languages ArgusAgent actually grounds and the provenance it
records to name the grammar that actually parsed,
So that a capability I depend on is specified, and a cached or replayed result cannot be
keyed on the wrong grammar.

**Acceptance Criteria:**

**Given** the **complete measured site list** — PRD **L23** (`[Python V1, multi-language V2]`),
**L116** (durable-moat claim), **L174** (design invariant, "V2 multi-language is additive"), **L180**
(V2 roadmap), **L317** (project-type overview, "V1 deep AST-grounding = Python"), **L375**
(risk-mitigation, "V2 multi-language additive"), **L398** (**FR7 — the binding capability contract**),
**L476** (**NFR-P2**); and architecture **L220** ("Deferred (post-V1): multi-language AST") and **L237**
("V1 deep = Python only") — **10 sites, enumerated by measurement on 2026-08-10b**
**When** this story completes
**Then** each is amended to record multi-language grounding as **delivered in V1**, with the
amendment dated and attributed to the 2026-07-28 change proposal — and the V2 roadmap no
longer lists it, so V2 cannot re-scope delivered work.

**Given** this enumeration has now been wrong twice — the original AC named 4 sites, the 2026-08-10
correction named 7, and measurement finds 10
**Then** the story closes with a **committed test that greps for the unamended claim shape** and fails if
any site survives, so the count is asserted rather than counted by hand a fourth time.

**Given** `argus/index/ast_index.py` records one `grammar_version` resolved from
`tree-sitter-python` only, while the index parses 10 languages
**When** a repository in any supported language is indexed
**Then** the recorded provenance names the grammar that actually parsed each file, and the
architecture's R3 cache-key contract (L77-78, L201 — written for a single grammar) is
amended to match, since this is a design change and not a defect fix.

**Given** the Epic-5 memoization store is not wired into the pipeline
**Then** this story does **not** wire it; it makes the key correct **before** anything
depends on it, and records that ordering as deliberate.

**Given** `pyproject.toml` ships a `[languages]` extra and `audit-ci.yml` sets
`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`
**When** a consumer reads README or CHANGELOG
**Then** both name the extra, the languages it enables, and what a missing grammar does to a
file's coverage grade — a capability a consumer cannot discover is a capability they cannot use.

### Story 10.3: The invocation contract says what the CLI accepts

As a downstream integrator,
I want every accepted CLI flag to appear in the invocation contract,
So that the contract Story 1.7 declares LOCKED is the contract the tool actually honours.

**Acceptance Criteria:**

**Given** FR30 and architecture L226 specify `repo + commit + budget + materiality_bar`, and
Story 1.7 declares the flag names LOCKED, while the parser accepts 13 flags
**When** `--passes`, `--skip-pass`, `--ignore-path` and `--ignore-pattern` are traced
**Then** each is found in no epic, PRD, addendum, change proposal, CHANGELOG or README — and
this story **decides** each one: blessed with acceptance criteria and a CHANGELOG entry, or
removed from the parser. Both outcomes are acceptable; leaving them unspecified is not.

**Given** `--ignore-path` and `--ignore-pattern` suppress **security** findings and were
inert until 2026-08-09
**When** a bless decision is considered
**Then** it is accompanied by a threat model stating who may suppress a secret finding and
what is recorded when they do; absent that model, the flags are removed rather than blessed.

**Given** whichever decision is taken
**Then** FR30, architecture L226 and Story 1.7's LOCKED list are updated to match the parser
exactly, and a test asserts parser-vs-contract equality so the two cannot diverge again.

### Story 10.4: A grammar that fails to load names why

As an operator auditing a polyglot repository,
I want a grammar failure to say whether the package is missing or broken,
So that the remedy the report gives me is the remedy that works.

**Acceptance Criteria:**

**Given** `argus/index/ast_index.py::_get_parser_for_lang` catches
`(ImportError, Exception)` and returns `None`, so a **missing** grammar and an **installed
but broken** one both report `grammar_missing_<lang>`
**When** a grammar package is installed but fails to load (ABI mismatch, corrupt build)
**Then** the recorded reason distinguishes the two — a missing package keeps
`grammar_missing_<lang>`; a load failure records a distinct token — so the report never tells
an operator to install a package they already have.

**Given** AR10 and Story 4.3's rule against a bare `except: pass` in library code
**Then** the redundant `(ImportError, Exception)` tuple is replaced by explicit arms, and the
degradation itself is unchanged: a file whose grammar cannot load is still recorded
`ast_eligible=False`, never a false deep claim.

**Given** the coverage denominator moves when a grammar fails
**Then** a test pins both reason tokens, so a silent regression to a single token fails CI.

### Story 10.5: A V1 commitment is delivered, or it is explicitly not V1

*Added 2026-08-10b by [sprint-change-proposal-2026-08-10b.md](sprint-change-proposal-2026-08-10b.md).*

As the ArgusAgent governance owner,
I want a capability the PRD commits to V1 either shipped or explicitly reclassified,
So that the specification and the product stop describing different tools.

**Acceptance Criteria:**

**Given** PRD §Product Scope L168 commits `standards_refs[]` + CWE-required-on-security-findings to
**V1 Core** as *"day-one additive"*, while **no FR in the binding capability contract lists it**, and
**zero occurrences** of `standards_ref` / `cwe` / `asvs` / `owasp` exist in `argus/**/*.py`
(`FindingDraft` at `argus/detectors/base.py:63-87` carries no standards field of any kind)
**When** the conflict is adjudicated
**Then** it is **decided**: either an FR is added and the field ships, or §Product Scope is amended to
move it to V2 with the amendment dated and reasoned. **Leaving the two sections in disagreement is not
an acceptable outcome.**

**Given** FR11 (secret detection) is the security detector this would annotate, and Journey 4 depends on
findings being citable as compliance evidence
**Then** whichever way it is decided, the consequence for Journey 4 is recorded — a security finding with
no standards reference is weaker evidence, and that should be a known trade rather than an accident.

**Given** this conflict arose because a capability lived in §Product Scope and **not** in the FR contract —
the exact inverse of DF-AUD-APAA-D, which was a capability shipping with no spec
**Then** a **sweep** confirms whether any other §Product Scope V1 Core item is missing from FR1–37, and
each result is recorded. One instance found by accident implies the class was never checked.

**Given** the **opposite direction is also unswept** — an FR that *is* in the binding contract but that
**no code path reaches** — and one instance is already known: **FR23** (human STOP/PROCEED escalation,
default-STOP) is delivered as a **library seam** (`governance/escalation.py`,
`governance/decision_record.py`, proven by `tests/apaa/test_hitl_escalation.py`) that **nothing in
`pipeline.py` or `cli.py` invokes** (DF-6-7-A)
**Then** this story sweeps **FR1–37 for requirements with no reachable production call site**, and each
hit takes a **dated disposition**: wired, or explicitly recorded as a library seam for V1.5 with the
call site deferred and a reason. **FR23 is decided by name, not left to the sweep's summary.**
*(Added 2026-08-10b. The precedent is already set in this plan: FR27/NFR-D1 had exactly this shape — a
built, unwired memoization store — and became Story 12.3. FR23 was not listed, which is the
inconsistency this AC closes. Note the sweep may find more: FR7's validator and the FR36 deep pass were
both reachable only from `argus/audit/*` until Epic 12 wires them.)*

---

## Epic 11: Release Integrity — nothing unsafe or untrue can be published · *Argus repo*

Every defect that becomes *worse* by being published is closed, and the tool states its own
validation status wherever it states a verdict. This epic does not make Argus more useful —
that is Epic 12. It makes Argus **safe to hand to someone outside XAgents**.

**Covers:** FR34 (11.1), DF-8-2-B (11.2), DF-9-2-D (11.3), the `tree-sitter` runtime bound (11.4),
DF-9-2-A + DF-9-2-B (11.5) · **Depends on Epic 10 — all five stories**
**Dependency flow:** 11.1 FIRST (no verdict surface ships without disclosure); 11.2-11.4 independent;
11.5 last, because it re-measures a built artifact.
**No story in this epic publishes anything.** The publish is Epic 12's final story, by design —
publishing at the end of this epic would ship a safe tool that is not yet worth installing.

**Source:** [sprint-change-proposal-2026-08-10b.md](sprint-change-proposal-2026-08-10b.md), superseding
the unsigned 2026-08-10 proposal.

**Renumbering from that superseded draft** (recorded so the `sprint-status.yaml` entries can be traced):
old 11.1 -> **11.1** (scope changed) · old 11.3 -> **11.2** · old 11.4 -> **11.3** · old 11.5 -> **11.4**
· old 11.6 -> **11.5** · old 11.7 -> **Epic 12's final story** · **old 11.2 is absorbed** into Epic 12's
deep-audit story, which measures the same question as a precondition of the work rather than as a
standalone spike.

### Story 11.1: The tool discloses its own status, and the disclosure has an expiry

As an independent developer installing Argus,
I want the tool to tell me the validation state of its own findings wherever it gives me a verdict,
So that I can weigh its output correctly — and so that its status cannot quietly become permanent.

**Acceptance Criteria:**

**Given** `demo-heuristic-only` and the `provisional` gate string exist **only** in
`argus/dogfood/proof_run.py` and `argus/dogfood/proof_render.py` — an internal artifact, not a user surface
**When** this story completes
**Then** the disclosure reaches the CLI summary, every generated report, the MCP surface, and the
distribution listing, satisfying FR34.

**Given** AR7 / §3.3 forbid a second mechanism where one exists
**Then** the existing two-sided `DOGFOOD_EXTERNALIZATION_GUARD` test is **extended** (presence AND
over-claim-phrase absence), never duplicated.

**Given** FR34 requires mechanical enforcement
**Then** the surface set is **enumerated in a test that fails on an unenumerated member** — a new verdict
surface either carries the disclosure or fails CI.

**Given** the operator's explicit direction that no permanent provisional state ships
**Then** the disclosure records **what would remove it** (the >=80% gate, cleared per Epic 13) and is
written to be **replaced by the cleared status, never deleted** — and a test asserts the enforcing guard
cannot pass vacuously once the token changes.

**Given** FR37 governs explanation and FR16 governs classification
**Then** no verdict is reworded, upgraded or hedged by this story. The decision table is untouched.

### Story 11.2: A polyglot repository is classified correctly

As a developer auditing a repository that is not Python,
I want file classification to use real word boundaries,
So that an ordinary source file is never mistaken for a test.

**Acceptance Criteria:**

**Given** `"test.java"` and `"spec.rb"` at `argus/detectors/vacuous_test.py:198` carry **no word
separator**, so `latest.java` and `myspec.rb` classify as tests **by name**, with no content check
available to correct it
**When** the separators are added
**Then** a pinned **near-miss corpus** (`latest.java`, `myspec.rb`, `contest.py`, `respec.rb` and their
true-positive counterparts) asserts both directions.

**Given** the exposure is **zero-instance in this repository** — the ledger called it *"latent, lands only
on a polyglot target repo"*
**Then** the story records that **the public audience is that polyglot target**, which is what moves it
from a latent internal item to release-blocking.

**Given** the AC7 two-stages-cannot-disagree invariant
**Then** it is **re-proven**, not assumed to survive the change.

> ⚠️ **THE SURROUNDING CODE HAS CHANGED SINCE THIS STORY WAS DRAFTED.** *(Measured 2026-08-10.)*
> `vacuous_test.py` now splits filename classification into **two** constants, which this story's framing
> predates:
> - **`_UNAMBIGUOUS_TEST_SUFFIXES`** — where `"test.java"` and `"spec.rb"` live. **The defect is here and is
>   untouched**: the citation at `:198` is still exact, the separator is still missing, and this tuple has
>   **no content check by design** (*"the convention is reserved for tests and no production module adopts
>   it"*) — so the AC's *"with no content check available to correct it"* remains true **for these suffixes**.
> - **`_AMBIGUOUS_PYTHON_TEST_SUFFIXES`** (`_test.py`, `test.py`) — **new**: genuinely ambiguous Python
>   suffixes **resolved by CONTENT when an AST entry is available**, added because
>   `argus/detectors/vacuous_test.py` — the detector itself — was being classified as a test file and
>   dropped to `tool_scanned_only`.
>
> **Binding consequences for the story:** (a) the fix belongs in `_UNAMBIGUOUS_TEST_SUFFIXES` **only** —
> do not route Java/Ruby through the Python content-resolution path, which is AST-backed and
> language-specific; (b) the **AC7 re-proof is now the load-bearing AC, not a formality** — the invariant
> must be re-proven across **both** constants and their interaction, since a second classification stage
> now exists that did not when AC7 was written; (c) the near-miss corpus must include a Python case
> (`contest.py`) that exercises the ambiguous path, so the two constants are shown not to disagree.

### Story 11.3: The published action cannot execute a consumer's input

As a developer running the Argus action in my own repository,
I want my workflow inputs to be data, never shell source,
So that using Argus cannot execute code in my CI job.

**Acceptance Criteria:**

**Given** **five** action-input sites are interpolated into `run:` bodies
(`action.yml:74,78,79,80,126`) — **the ledger named only `:127`**
**When** the sweep runs
**Then** all five are bound through `env:` and compared as quoted shell variables, in **one pass**, with
the corrected site count recorded.

**Given** publishing converts a latent finding into a live one in **every consuming repository**
**Then** a guard test fails on **any** action-input interpolation appearing inside a `run:` block.

**Given** the marketplace channel
**Then** this story is a **hard precondition** on it — Epic 12's publish story may ship the index channel
without it, and may not ship the marketplace channel.

### Story 11.4: A wrong grammar version cannot silently produce a false green

As an operator on a machine whose environment I did not build,
I want an unvalidated parser to withhold a verdict rather than compute one,
So that an assurance tool never emits a false green from a dependency it did not check.

**Acceptance Criteria:**

~~**Given** the `tree-sitter <0.26` bound is **load-bearing**: on `0.26.0` the cartridge self-audit flips
`NOT_READY_FOR_RELEASE` -> `RELEASE_READY` because AST corroboration stops firing — a **false negative
from an assurance tool**, the PRD-fatal direction (inversion F1)
**When** an out-of-bound version is present at runtime
**Then** the assertion fires **at runtime**, not only at resolve time — a metadata bound constrains a
resolver, never an already-installed environment.~~

🔴 **CORRECTED IN PLACE 2026-08-12 by Story 11.4 (AC5.3), following the 10.2 precedent for a
premise fix in an unstarted story. The story's INTENT is unchanged; only the false measurement is.**
Struck rather than deleted (§3.4 evidence immutability). **Reason:** the `Given` above was re-measured
by execution and against the upstream release notes and is **NOT REPRODUCIBLE as stated** — 0.26.0's
breaking changes (`Language.version`→`abi_version`, `Language.query()`→`Query(...)`, the
`timeout_micros` removals, `Point` as a tuple subclass) touch **nothing Argus uses**, the minimum
grammar ABI is unchanged, and total AST loss lands the cartridges on `INSUFFICIENT_COVERAGE`/exit 3
because the coverage floor fires first. The cartridge corpus also sits at deep 1/2 = 50%, **below** the
60% gate, so it is structurally incapable of the flip. See `architecture.md` §Packaging.

**Given** an installed parsing toolchain that Argus has never checked — and noting that the
demonstrated failure occurs at an **IN-BOUND** version, so a version comparison cannot be the mechanism
**When** a repository **above** the 60% deep gate is audited with an extraction vocabulary that has
drifted (measured: `NOT_READY_FOR_RELEASE`/exit 2 → `RELEASE_READY`/exit 0, with `deep_ratio` **5/6 in
both runs** — a verdict-eligible `vacuous_test_ast` silently degraded to advisory
`vacuous_test_heuristic`, invisible on every surface Argus prints)
**Then** Argus **behaviourally self-checks** the toolchain per language at the real loader seam — a
pinned canary whose extraction is compared against a frozen expectation — and `RELEASE_READY` is
**unreachable** when it does not match. The declared version range is recorded and checked as a
**second, independent** signal, never as the check itself.

**Given** a metadata bound constrains a *resolver* and constrains nothing on a machine where the
package is already installed, pinned by another tool, vendored or patched
**Then** the defence is asserted **at runtime**, not only at resolve time.

**Given** the degradation must not itself be a crash (NFR-R1)
**Then** it produces a **typed finding and a non-vouching verdict**; `RELEASE_READY` is **never** computed
under an unvalidated parser.

**Given** the failure is silent today
**Then** a test pins the flip — a regression to silence fails CI.

### Story 11.5: The published artifact is complete and says only true things

As a developer installing from a public index,
I want every shipped module to import and every claim in the docs to be true,
So that what I install is what the documentation describes.

**Acceptance Criteria:**

**Given** **5 of 71** wheel modules fail to import (`No module named '_registry'`, from
`argus/precision/replay_harness.py:87-90` inserting `<repo>/tests/cartridges` onto `sys.path`)
**When** the import is made lazy/optional
**Then** the count is **re-measured from a freshly built wheel**, and `_NOT_IMPORTABLE_FROM_DISTRIBUTION`
is pinned **in both directions** so a stale record goes RED.

**Given** **22 bare-word "Minions" subject claims across 14 `argus/**` modules**
**Then** each is read and classified **true-historical (keep)** or **false-subject-claim (rewrite)** —
never a blanket replace.

**Given** README's *"INTERIM — resolve straight from this repository at a tag"* is false (`git tag -l` is
**empty**), and README additionally claims **slash-command registration that does not ship** while its CLI
example omits the `audit` subcommand and the required repo positional
**Then** every false claim is corrected or removed. **The slash-command claim is not deleted** — Epic 12
delivers it (FR35); it is marked as forthcoming with its story reference, so the docs never describe a
capability the artifact lacks.

---

## Epic 12: The Useful Tool — what a developer gets on the first run · *Argus repo*

Argus becomes worth installing. Two capabilities that are **built and unwired** are connected, the
output stops being a dead end, the tool becomes reachable from the agent that wrote the code, and
the result is published. This epic adds **no new assurance capability** (PRD §V1.5) — it delivers
requirements already in the contract and reach the contract now admits.

**Covers:** FR36 (12.2), FR27/NFR-D1 delivery (12.3), FR37 (12.4), NFR-P3 (12.5), FR35 (12.6, 12.7)
· **Depends on Epic 10 (all five) and Epic 11 (all five)**
**Dependency flow:** **12.1 FIRST** — it is a hard enabler; 12.2 and 12.3 both land in
`argus/pipeline.py`, which is already 131 lines over the NFR-M1 cap. **12.2 EARLY** — it carries the
absorbed reachability measurement, which can change what 12.4 must say. 12.3 **depends on Story 10.2**
(the grammar cache key must be correct *before* anything reads it). 12.5 independent. 12.4 -> 12.6 ->
12.7. **12.9 LAST — the only story that publishes anything.**

**Source:** [sprint-change-proposal-2026-08-10b.md](sprint-change-proposal-2026-08-10b.md)

### Story 12.1: The file everything lands in stops breaching its own limit

As the Argus maintainer,
I want `pipeline.py` under the NFR-M1 ceiling and the ceiling enforced repo-wide,
So that the two wirings this epic depends on are not built on a file that already fails the rule.

**Acceptance Criteria:**

**Given** DF-8-2-A recorded `pipeline.py` at **1199/1200** and warned *"the next edit of any size breaches
NFR-M1"*, and it is now **1331 lines**
**When** the extraction completes
**Then** every `argus/**` file is at or under 1200 lines, measured and recorded.

**Given** NFR-M1 is enforced **per-module and ad hoc** (`tests/test_cache_invalidation.py:690`,
`tests/test_cartridge_selfaudit.py:472`) with **no repo-wide sweep and no assertion covering
`pipeline.py`** — which is why 131 lines of drift went uncaught
**Then** a repo-wide sweep test asserts the ceiling over **every** source file, so no file can breach it
silently again.

**Given** DF-8-2-A, DF-8-3-A and DF-8-3-C **all gate on this extraction**
**Then** each is closed or its remaining scope re-recorded with a reason — none is left pointing at work
that has now happened.

**Given** the extraction is pure restructuring
**Then** the full suite passes unchanged and a dogfood re-run produces an **identical verdict** —
behaviour is proven untouched, not assumed.

**Given** DF-8-5-B — three committed-artifact rot checks (`TC-ArgusAgent-DOGFOOD-001-03`, `-06`, `-20`)
compare a committed `.md` against a **live derivation over the working tree**, so any change to
`argus/**` composition re-breaks them with no warning; `-03` and `-06` were **RED across four
consecutive commits** and Story 8.5 had to re-derive its artifacts **three times**
**When** this story restructures `pipeline.py` — and before 12.2, 12.3 and 12.6 change `argus/**` further
**Then** DF-8-5-B is closed here: either a **documented regeneration entry point named in the failure
message of all three assertions**, or a CI step that regenerates and fails on drift.
*(Absorbed 2026-08-10b. Rationale: this epic changes `argus/**` more than any epic since Epic 6, so the
structural two-step lands repeatedly. Invisible to users; a tax on every remaining Epic-12 story.)*

### Story 12.2: The deep audit is wired, opt-in, and honest about what it costs and sends

As a developer who wants a real answer on the code that matters,
I want to enable a deeper pass on demand, with its cost and its egress stated up front,
So that I can get depth when I want it without paying for it or leaking source when I don't.

**Acceptance Criteria:**

**Given** ~~`DeepAuditSeam` at `argus/audit/deep_audit.py:91` is referenced only from `argus/audit/*` and
`argus/dogfood/proof_run.py`~~ — **never from `argus/pipeline.py`**
*(Corrected 2026-08-13 by Story 12.2, struck not deleted. Measured by execution on `2bea92f`: the
anchor `class DeepAuditSeam:` is at line **98**, not `:91`; and the seam had **ZERO production
callers** — the identifier appeared only in its own `class` statement, its own `__all__`, and
`tests/test_llm_dispatch_port.py`. `argus/dogfood/proof_run.py` never imported it; its sole mention
was a docstring saying the seam is a separate injected port NOT used. The third clause held.)*
**When** this story completes
**Then** the seam is reachable from the audit pipeline through an explicit opt-in, satisfying FR36.

**Given** FR36 and NFR-S6
**Then** the pass is **off by default**; the default run remains zero-token, offline, key-free and
transmits nothing; and enabling it **discloses the provider and what will be transmitted before the first
byte leaves**. A committed gate fails if any egress path is reachable without opt-in.

**Given** Story 6.1's determinism quarantine — a subprocess gate proving the pure seam does not import
providers
**Then** that gate **still passes**. Wiring the seam must not move provider imports into the pure path.

**Given** FR21/FR22 already govern spend
**Then** the pass flows through the **existing** ceiling — halt, mark `skipped`, downgrade, report — with
**no new cost-governance mechanism** (AR7/§3.3: reuse, never fork).

**Given** architecture §E justified omitting fallback, circuit-breaking and cost attribution because they
came *"for free"* from the Minions orchestrator, and **Story 9.1 removed that orchestrator**
**Then** those behaviours are supplied here as NFR-R1 acceptance criteria: an unavailable, erroring, or
budget-halted provider downgrades coverage and records a finding. No false deep claim, no crash, no
`RELEASE_READY` computed over a failed pass.

**Given** the absorbed question from the superseded Story 11.2 — `DOGFOOD_EXTERNALIZATION_GUARD` states
every dogfood finding is advisory (`depth_supported is None`), while the epics frontmatter records the
vacuous cartridge emitting a verdict-**blocking** finding, and **both may be true if the paths supply
depth differently — not verified**
**Then** this story **measures**, on the **default** invocation (no LLM, no cartridge harness), whether
`NOT_READY_FOR_RELEASE` is reachable, and **records the result as a yes or a no**.
**And** a measured **"no"** is reported and **escalated** — it is never a licence to loosen a gate and
never grounds for softening Journey 6. If the answer is "no", Story 12.4's output must say so plainly
rather than implying a blocking verdict is available for free.

### Story 12.3: A re-run returns the recorded result

As a developer iterating on my code,
I want a re-audit to reuse what has not changed,
So that running Argus repeatedly is fast enough to be part of my loop.

**Acceptance Criteria:**

**Given** `argus/cache/memo_store.py` exists and `argus/pipeline.py` **never imports it**, while FR27
requires verdict reproduction and NFR-D1 names local content-addressed memoization as the mechanism
**When** the store is wired
**Then** an existing requirement is **delivered** — this story adds no capability to the contract, and
says so.

**Given** **Story 10.2 makes the grammar provenance per-grammar** and explicitly declines to wire this
store, recording that ordering as deliberate — *"it makes the key correct before anything depends on it"*
**Then** this story **depends on 10.2** and consumes the corrected key. Wiring first would bake a wrong
key into a persisted cache and require a `CACHE_KEY_SCHEMA_VERSION` bump plus migration to undo.

**Given** a cache is a correctness surface in an assurance tool
**Then** a hit and a cold run produce **byte-identical** verdicts, pinned by test, and the DF-5-1-A
invalidation contract holds over the wired path.

### Story 12.4: Every outcome names its next action

As a developer with no colleague to ask,
I want the tool's own output to tell me why I got this result and what changes it,
So that a verdict is a step forward rather than a dead end.

**Acceptance Criteria:**

**Given** FR37
**Then** every terminal outcome — `RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`, and
the `AUDIT_FAILED` non-verdict — names why it was reached and the next action that changes it,
**enumerated in a test that fails on an unenumerated outcome**.

> ⚠️ **THIS STORY EXTENDS AN EXISTING MECHANISM — IT DOES NOT CREATE ONE.** *(Measured 2026-08-10.)*
> A next-action surface **already ships**: `argus/reports/plain_english.py:205` renders a `Next:` line and
> states its own rationale — *"a red light with no next action trains an [operator to ignore it]"* — and
> `argus/reports/generator.py:236` reasons about the same gap (*"is unmet but not by what, so there is no
> next action"*). The ACs below read as greenfield because they were drafted from FR37's text rather than
> from the tree.
> **Binding consequence for the story:** the first task is to **measure what the existing `Next:` surface
> already covers**, per outcome, and the story delivers the **difference** — not a second mechanism
> (AR7 / §3.3: reuse, never fork). A parallel next-action renderer beside the shipped one is a defect, not
> a delivery. The **enumerating test is genuinely new** and remains required regardless of what the audit
> of existing coverage finds.
> **What is measurably absent** (grep, 2026-08-10): the **ingestion-boundary disclosure**. Zero matches in
> `argus/**` for the not-ingested populations. The three-population statement — *never ingested* /
> *ingested but held out* / *assessed* — is unimplemented in any form, and it is the load-bearing AC added
> after the `RELEASE_READY` incident below.

**Given** `INSUFFICIENT_COVERAGE` is the load-bearing case
**Then** it names the **specific** unmet gate — floor, ratio, or critical subsystem — with the measured
figures, and the action that would change it.

**Given** FR16 governs classification and FR37 governs explanation
**Then** **no verdict is reworded, upgraded, or hedged.** The decision table is untouched, and a test
asserts the verdict enum is unchanged by this story.

**Given** Story 12.2's measurement
**Then** the output reflects **what it actually found** — if a blocking verdict is not reachable on a
default run, the output does not imply otherwise.

**Given** the measured incident that motivates this AC: `argus audit .` on this repository returned
`verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 held_out=76, exit 0` **while the repository
contained a shell injection in `action.yml`, five non-importable wheel modules, and a README describing a
capability that does not ship** — none of which was a defect the audit missed, because
`AUDITABLE_SUFFIXES` (`argus/shared/source_languages.py:80`) ingests only the 10 supported **source**
languages, so `.yml`, `.md` and `.toml` were **never opened**
**When** any verdict is emitted
**Then** it names the **ingestion boundary**, distinguishing three populations by construction:
**never ingested** (suffix outside `AUDITABLE_SUFFIXES`), **ingested but held out**, and **assessed**.
`deep_ratio` and `held_out` describe only the second and third — **no ratio can disclose the first**,
because a file that never entered is absent from every denominator.

**Given** the boundary must not drift as languages are added or removed
**Then** the disclosure is **derived from `AUDITABLE_SUFFIXES`, never hand-listed**, and a test fails if a
suffix class present in the repository is absent from the statement.

**Given** `RELEASE_READY` is the direction where an undisclosed boundary is most dangerous — the
false-green direction the 2026-08-03 inversion analysis (F1) flagged as unguarded
**Then** the boundary statement is asserted on `RELEASE_READY` **specifically**, not only on the
not-assessed outcomes where a reader is already cautious.
*(Added 2026-08-10b after the operator asked why the self-audit returned `RELEASE_READY` while 22 stories
of release-blocking work were outstanding. The answer — everything outstanding sat outside the audited
envelope — is correct by contract and was **not legible in the output**. This AC makes it legible.)*

### Story 12.5: The default install grounds the languages it claims

As a developer whose project is not Python,
I want the public install to work on my stack,
So that I am not silently given a worse result because of a packaging choice.

**Acceptance Criteria:**

**Given** NFR-P3 classifies coverage degraded by a grammar absent from the default install as a
**packaging defect**, not a user error
**When** the public distribution is installed by its documented primary command
**Then** every language the tool claims to support is grounded, **without the user discovering an optional
extra**.

**Given** a language deliberately outside the default install
**Then** its absence and the reason appear **in the tool's own output at the point the file is
downgraded** — not only in the README.

**Given** Story 10.2 documents the `[languages]` extra and `audit-ci.yml` sets
`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`
**Then** this story reconciles the default install with that documentation so the two cannot describe
different products.

### Story 12.6: A coding agent can run the audit and read the verdict

As a developer building with a coding agent,
I want the agent to run the audit and act on the result itself,
So that the loop that wrote the code contains something that checks it.

**Acceptance Criteria:**

**Given** FR35 and the four §Project Classification constraints
**Then** an **MCP server over stdio** ships in the existing distribution as an entry point — **no network
listener, no bound port, no HTTP stack, no credentials accepted or stored**.

**Given** the `argus.* ⊬ fastapi` import-isolation gate and ADR #20
**Then** both still pass, asserted by the existing committed gates rather than a new mechanism.

**Given** FR35's parity requirement
**Then** the same repository at the same commit yields the **same verdict** through the MCP surface and
the CLI, pinned by test.

**Given** FR34
**Then** the disclosure is present on this surface — it is a user-facing verdict surface and the Story
11.1 enumeration must already cover it.

### Story 12.7: The commands the README promises actually exist

As a developer following the README,
I want the documented commands to be real,
So that the first thing I try is not the first thing that fails.

**Acceptance Criteria:**

**Given** `README.md:138-150` claims *"ArgusAgent registers slash commands in your AI coding assistant"*
and lists seven, while `pyproject.toml:59-62` ships **only** three console aliases to the same
`argus.cli:main` — **no registration mechanism exists**
**When** this story completes
**Then** packaged command assets are placed in the host's configuration by a documented step, and each
documented command resolves to a real invocation.

**Given** Story 11.5 marked the claim as forthcoming rather than deleting it
**Then** that marker is removed and the README describes what ships — the commands, the install step, and
the hosts covered.

**Given** a documented command that is **not** delivered
**Then** it is removed from the README in the same change. The set that ships and the set that is
documented are asserted equal by test.

### Story 12.8: The tool explains itself

As a developer with the tool's output and nothing else,
I want `--help`, error messages, and the docs to answer what I need,
So that I am never sent to a wiki that does not exist.

**Acceptance Criteria:**

**Given** `docs/` contains **one integrator-shaped README** and no first-run surface
**When** this story completes
**Then** a lean first-run page exists covering install, first audit, reading the ledger, and what each
verdict means — **no tutorial prose beyond that**; this persona is a developer, not a novice (PRD §User
Success, tertiary).

**Given** every CLI flag Story 10.3 blessed
**Then** `--help` states what it does and its default, and a test asserts parser-vs-help parity alongside
10.3's parser-vs-contract test.

**Given** an operator error (bad path, unreadable repo, missing grammar, absent key under the deep pass)
**Then** the message names the cause and the fix. NFR-R1's no-crash rule already covers the degradation;
this covers the **diagnosis**, extending Story 10.4's principle to the user-facing surface.

**Given** DF-8-4-D — `argus/cli.py:368-372` catches the **base** `ValueError` while its own comment
enumerates the typed subclasses, and Pydantic's `ValidationError` **is** a `ValueError` subclass, so
*"a genuine internal validation bug is reported as an expected, typed 'audit failed' degradation instead
of surfacing"*
**When** an internal defect occurs on the public entry point
**Then** it is **distinguishable from an expected degradation** — the arms are split to the typed
subclasses the comment already names, and a genuine bug surfaces as a defect the user can report rather
than as a normal outcome. A test pins both directions so the two cannot re-merge.
*(Absorbed 2026-08-10b. Filed 🟢 when every user could read a stack trace; it is not 🟢 for a public CLI
— a masked bug costs the user a next action, which FR37 forbids, and costs the maintainer a bug report.)*

### Story 12.9: The release is published, and its status cites the gate that published it

As a developer installing Argus,
I want a real published artifact whose release status is evidenced,
So that what I install exists and its claims are backed by an executed gate.

**Acceptance Criteria:**

**Given** Story 10.1's evidence standard
**Then** the release status cites the **CI run id on the released commit**, or is recorded **NOT
ESTABLISHED** — never asserted.

**Given** `release.yml` **deliberately abstains from index publish** (its own header) and has **never
executed** — `git tag -l` is empty
**Then** adding publish is a **reviewed, deliberate scope change** to a workflow that documents its own
abstention, recorded as such.

**Given** Story 11.3 is a hard precondition on the marketplace channel
**Then** if 11.3 has not landed the **marketplace channel does not ship**; the index channel may ship
independently.

**Given** FR34
**Then** **both listings carry the disclosure**, and the artifact installs clean in a fresh environment
with `argus --help`, a fixture audit, and an MCP invocation all succeeding — proven, not built.

**Given** this is the first public artifact
**Then** the release edge cases Story 9.2 pinned (dirty tree, existing tag, re-tag, silent overwrite) are
**re-proven against the index channel**, which 9.2 could not exercise.

---

## Epic 13: Earn the Gate — remove the disclosure by measuring, not by deleting · *Argus repo*

The >=80% finding-precision gate is cleared on evidence, or it is recorded as **not cleared** and
the disclosure stays. This epic is the reason FR34 is temporary rather than permanent. **It is the
only work in this plan that can remove the tool's provisional status, and it is not a build task.**

**Covers:** DF-7-2-A, DF-6-6-A / -P1 / -P2 · the architecture's OPEN validation-set input (L152-154)
**Depends on Epic 12** (a published tool whose findings are worth adjudicating)
**Dependency flow:** 13.1 -> 13.2 -> 13.3, strictly sequential. No parallelism — each story's output is
the next one's input. **Amended 2026-08-17: 13.5 is appended, and it depends on Epic 14.**

> ⚠️ **RE-OPENED 2026-08-17** by [sprint-change-proposal-2026-08-17.md](sprint-change-proposal-2026-08-17.md).
> Stories 13.1–13.3 completed and the gate decision was recorded as `BLOCKED` (0 TP / 26 FP / 5
> BORDERLINE over 31 findings). The measurement then established that **the single rule class it
> measured is defective**: `vacuous_test_ast`'s AST corroboration tests whether a test constructs a
> mock, not whether the asserted values derive from the SUT — a conformance gap against
> cross-cutting concern #6. **Epic 13 cannot close on a measurement of a broken instrument.**
> Story 13.5 re-runs it; **Epic 14 blocks 13.5.**
>
> **The 13.1–13.3 records are NOT rewritten.** They are the true, byte-reproducible measurement of
> the detector as it stood on 2026-08-17, and the adjudication record is append-only (§3.4 evidence
> immutability). A correction supersedes; it never erases.

> ✅ **Start condition MET — adjudicator named 2026-08-10b.** This epic required a named human because no
> agent can adjudicate a finding as genuinely real; that is the whole point of the measurement.
> **`sprint-status.yaml` names one: XAgent007**, filling the Engineering Lead role in
> `precision-validation-protocol.md` §2 (primary adjudicator). The QA Lead second and external tie-break
> stay unfilled until a borderline finding requires them (§4). **The item is NOT closed** — an owner is
> named, the measurement has not run. DF-6-6-A/-P1/-P2 follow the same owner by inheritance.
>
> *Corrected 2026-08-10 (readiness report, M-7). This header read* "**This epic cannot start without a
> named human** — DF-7-2-A has been open and **unowned** since Epic 7… Story 13.2 does not begin until an
> adjudicator is named in `sprint-status.yaml`" *— a condition the tracker had already recorded as met.
> The two governing documents disagreed on the single condition gating the public release, and FR34's
> second condition (a programme to clear the gate,* **committed and in flight***) reads as unsatisfied
> from this document alone.*

**Source:** [sprint-change-proposal-2026-08-10b.md](sprint-change-proposal-2026-08-10b.md)

### Story 13.1: Decide what the validation set is, then build it

As the Argus maintainer,
I want one definition of the validation set and a corpus that satisfies it,
So that the gate is cleared against the thing the PRD actually specified.

**Acceptance Criteria:**

**Given** PRD L161 specifies *"N ≈ 5-10 **real** XAgents repos"* and L156 requires findings *"judged
genuinely real by an independent senior engineer"*, while `precision-validation-protocol.md` §5 specifies
*"N >= 5 distinct labeled **planted-defect cartridges**"* with `VALIDATION_SET_FLOOR_N = 5` — **two
different corpora, never reconciled**
**When** this story completes
**Then** one definition governs, the other is amended to match, and the decision is dated and reasoned.
**And** the recommendation of record is that **the PRD governs**: cartridges measure **recall against
known plants** (FR20, already delivered and CI-asserted); precision measures **how often a blocking
finding on unplanted code is real**. These are different quantities and only the second gates
externalization.

**Given** the architecture records at L152-154 that the validation-set input is **OPEN** and *"the one open
input that gates an ARCHITECTURE choice"*
**Then** this story **closes it**, and the architecture is amended from OPEN to resolved with the decision
recorded.

**Given** the corpus went **backwards**: Story 8.5 re-derived the dogfood as a self-audit of `argus/`, the
independent Minions run survives only at `minions-dogfood-proof-story-7-2-superseded.md` and *"can never
be re-derived in this repository"*, and the ledger calls the replacement *"a materially weaker evidence
class … not independent corroboration of anything"*
**Then** the corpus is rebuilt from **repositories Argus did not author**, and the self-audit is
**excluded from N** with that exclusion recorded.

**Given** the PRD's *"usage is not evidence"* guard
**Then** repositories may be **sourced** from anywhere including public users, but **only adjudicated
findings count** toward the measurement. Install counts, run counts and stars are never evidence.

**Given** DF-8-5-C — `argus/dogfood/proof_run.py:643-644` passes `precision=Fraction(0, 1), n=0` as
**literals, not a measurement**, rendering *"N=0 labeled cartridges populated, floor N=5"* into
`minions-dogfood-proof.md:87`, while the shipped registry measures **5 distinct rule classes across 7
populated rows**
**When** this story establishes what the corpus actually is
**Then** the published figure is **derived from the registry, not written by hand**, and the artifact is
regenerated so the corpus it reports is the corpus that exists.
**And** the correction is recorded as a correction: the figure **understated**, so it never made a gate
look cleared — but a hand-written number in a proof artifact about the very gate this epic measures is
the defect class Epic 8 exists to delete.
*(Absorbed 2026-08-10b.)*

### Story 13.2: Adjudicate every finding, by a named human

As the accountable adjudicator,
I want to judge each emitted finding true or false against the recorded protocol,
So that the precision figure is a measurement rather than an estimate.

**Acceptance Criteria:**

**Given** DF-7-2-A is *"the ONLY step that can clear the attested gate"* and has been **open and unowned**
since Epic 7, restated as unowned by Story 9.2 and by the 2026-08-10 proposal
**When** this story starts
**Then** the adjudicator is **named in `sprint-status.yaml`**, and the story does not begin otherwise.

**Given** the protocol's §2 roles (Engineering Lead primary, QA Lead, external tie-break) and §4 method
(**full-corpus exhaustive, not sampled**; borderline -> locator re-examination -> golden-key correction ->
external tie-break)
**Then** the run follows the **committed protocol as written**. Where the corpus definition changed under
13.1, the protocol is amended **before** the run, never reinterpreted during it.

**Given** §3 budgets <=4 expert-hours for a full gate-flip adjudication at N>=5
**Then** actual expert-hours are **recorded**, so the next run can be scheduled on evidence rather than on
the estimate.

**Given** DF-6-6-A, DF-6-6-A-P1 and DF-6-6-A-P2 are open and describe the human half of this same
adjudication
**Then** each is closed here or its remaining scope re-recorded with a reason — none is left pointing at a
run that has now happened.

**Given** §3.4 evidence immutability
**Then** the adjudication record is **append-only**: a finding's disposition is never rewritten, and a
corrected judgement is recorded as a correction with its date and reason.

### Story 13.3: Record the result, and let it decide

As a developer relying on Argus,
I want its stated status to match its measured status,
So that the disclosure disappears only when it has stopped being true.

**Acceptance Criteria:**

**Given** the protocol's §5 thresholds — **>=80% precision (exact Fraction)**, **0 clean-repo blocking
false positives**, **N >= 5**, recall as diagnostic only
**When** the measured figures are in
**Then** the outcome is computed against those thresholds **as written**, with no post-hoc adjustment.
§7's OI1 honesty invariants are **not softened**.

**Given** the gate **clears**
**Then** `protocol_cleared=True` is passed by the harness caller (`argus/precision/replay_harness.py:223`,
`False` and never set `True` to date); PRD L118/L130/L141/L302 are updated from **NOT CLEARED** to cleared
**with the corpus and run that cleared it**; and per FR34 the disclosure is **replaced by the cleared
status, never deleted** — with a test asserting the enforcing guard has not become vacuous.

**Given** the gate **does not clear**
**Then** that is **recorded as the result**, the disclosure **stays**, and the shortfall is reported with
what would close it. **A failed measurement is not a reason to amend the threshold** — it is the
measurement working.

**Given** the attested tier
**Then** clearing this gate authorises **attested externalization** and nothing else; it does not by
itself authorise commercial, enterprise, regulated or operated-service use, each of which carries its own
preconditions.

**Given** the epic-9 retrospective declared the plan FINAL once already, and Epic 10 had to reopen it
**Then** this epic's retrospective states plainly what remains open, rather than letting a cleared gate
read as plan closure. **As of 2026-08-10b that list is: H0 is owned but H1–H4 are still NOT FILED;
assumption A5 remains UNSUPPORTED and H3's blocking-vs-advisory policy decision is unmade; and the
deferred-work entries DF-6-7-A, DF-8-4-B (bytes-example half), DF-8-4-C, DF-8-4-D, DF-8-5-B, DF-8-5-C
and DF-9-2-C are open with no named human.** The retrospective re-derives this list at the time it is
written rather than copying it — the point is that it is measured, not that it matches this sentence.

---

### Story 13.5: Re-measure the gate against the corrected instrument

*Added 2026-08-17 by [sprint-change-proposal-2026-08-17.md](sprint-change-proposal-2026-08-17.md). **Blocked on Epic 14.***

As the Argus maintainer,
I want the gate re-measured once the blocking rule proves what it claims,
So that the recorded decision reflects the instrument Argus actually ships.

**Acceptance Criteria:**

**Given** Epic 14 has closed and `vacuous_test_ast` is granted only on evidence that the asserted
values do not derive from the SUT
**When** the five ratified members are re-audited at their **UNCHANGED** pinned shas
**Then** the new blocking-finding population is adjudicated by the named human (protocol §2), the
rows are **APPENDED as superseding rows** — the record is append-only and 13.1–13.3's 31 rows stay —
and `decide_gate` is re-run over the result.

**Given** correcting the detector is expected to take the corpus to **zero** blocking findings
(measured: minions-wide promotions 24 → 0 under the candidate predicate)
**Then** an empty precision denominator is recorded as **`UNEVALUABLE`, never as `CLEARED`**, and the
FR34 disclosure **stays**. Whatever the arithmetic says is what is recorded — a fix that removes the
findings removes the measurement, not the shortfall.

**Given** `DF-13-3-A` records the `agent-smith` pinned sha as unreachable, and it is reachable
**Then** that entry is corrected **first**, so the re-run measures all five members against their
true pinned trees rather than a reconstruction.

**Given** a re-measurement is the moment a threshold looks negotiable
**Then** the ≥80% threshold, the corpus membership and FR34 are **unchanged** by this story. A failed
measurement is not a reason to amend the threshold — it is the measurement working.

---

## Epic 14: Make the Moat Hold — the blocking rule proves what it claims · *Argus repo*

Epic 13 measured the ≥80%-precision gate and returned **0 TP / 26 FP** over 31 findings in one rule
class. The measurement worked; what it found is that **the instrument is defective**. This epic fixes
the instrument. It does **NOT** re-measure — that is Story 13.5, which does not begin until this epic
closes.

**Covers:** the cross-cutting-#6 conformance gap · the Story 1.5 denominator amendment · the
cross-language assertion vocabulary *(added 2026-08-17b)*
**Depends on:** nothing. **Blocks:** Story 13.5, and therefore Epic 13's closure.
**Source:** [sprint-change-proposal-2026-08-17.md](sprint-change-proposal-2026-08-17.md) ·
Story 14.3 by [sprint-change-proposal-2026-08-17b.md](sprint-change-proposal-2026-08-17b.md)

> ⚠️ **This epic does not clear the gate and cannot.** Correcting the detector is expected to take
> the corpus to zero blocking findings, which `architecture.md` records as `UNEVALUABLE`, never
> `CLEARED`. Clearing requires findings that are *real*, which requires a corpus containing the
> defect class. That is an operator decision recorded at §2.5 of the source proposal — **not work in
> this epic.**

### Story 14.1: A verdict-eligible vacuous finding proves vacuity, not mocking

As the Argus maintainer,
I want the AST corroboration step to be evidence that the asserted values do not derive from the SUT,
So that a 🔴 rests on the fact cross-cutting concern #6 requires rather than on the presence of a mock.

**Acceptance Criteria:**

**Given** `_ast_corroborated`'s fact (b) is `assertion_sites >= 1 and mock_sites >= 1`, and across
**1,836** heuristically-flagged tests in the two contributing corpus members `ast_corroborated` is
equivalent to `mock_sites >= 1` in **1,835** cases
**When** this story completes
**Then** fact (b) discriminates real vacuity from mock-using-but-valid tests, and the equivalence
above **no longer holds** on the same population — **re-measured and recorded, not asserted**.

**Given** the false-accusation moat is the point
**Then** a test whose assertions constrain the real SUT result is **NOT** corroborated, however many
mocks it constructs; **and** a SUT call inside a `pytest.raises` / `assertRaises` context counts as
result-**CONSUMED**, because raising *is* the observation.

**Given** cartridges `vacuous_basic`, `holdout_vacuous` and `nonascii_unicode` assert that a planted
vacuous test emits `vacuous_test_ast` and blocks — `holdout_vacuous` being the anti-overfitting
control (DN-HOLDOUT)
**Then** all three stay green, and the story **records the measured recall** rather than assuming it.

**Given** `TC-ArgusAgent-DETECT-001-86` currently pins corroboration on a test that asserts on the
real SUT result
**Then** it is **re-authored as an intended behaviour change**, with the reason recorded in the story
— never silently adjusted to match new output.

**Given** the module docstring's *"the conservative default is the moat"*
**Then** where the unresolved 1.4 edge set cannot establish fact (b), corroboration is **NOT** granted
and the finding stays `vacuous_test_heuristic` / advisory. It does not fabricate corroboration.

**Given** AR8 (the scorer is PURE), AR4 (`Fraction`, never `float`) and NFR-D2 (deterministic,
zero-token)
**Then** all three hold unchanged, and no clock / uuid / random / iteration-order enters any
`.argus/`-bound output.

**Given** local gates are Windows-only while CI runs an ubuntu matrix, and this repository has
shipped POSIX-only bugs out of a green Windows run
**Then** this story is **not marked done on a local pass alone**.

### Story 14.2: The density scorer counts statements, and knows the assertions the ecosystem writes

As the Argus maintainer,
I want the assertion-density score computed over real statements and real assertions,
So that the advisory signal stops flagging half of every test suite.

**Acceptance Criteria:**

**Given** `_count_statements` counts non-blank/non-comment **LINES**, measured at **2.04×** inflation
against a true statement count over 1,812 flagged tests
**When** this story completes
**Then** the denominator counts **statements**, a multi-line statement counts **once**, and the Story
1.5 locked decision is **amended at its source** with a date and a reason (struck, never erased).

**Given** `_ASSERTION_CALLEES` is documented as *"unittest family + pytest helpers"* and contains **no
pytest helper**
**Then** it recognises `pytest.raises`/`warns`, the `unittest.mock` assertion methods
(`assert_not_called`, `assert_called_once_with`, …) and project-defined helpers by naming convention —
**13 of the 31** adjudicated findings call an assertion it cannot currently see.

**Given** the thresholds `ASSERTION_DENSITY_FLOOR = 1/4` and `MOCK_RATIO_CEILING = 1/2`
**Then** they are **NOT changed by this story**. If the corrected counts argue for different
thresholds, that is a separate, evidenced decision — never a silent re-tune riding on a bug fix.

**Given** the flag rate is **51.6%** of all test functions on the minions tree today
**Then** the story records the **re-measured rate over the same population**, as a number.

**Given** committed dogfood artifacts are detector-output-dependent
**Then** they are regenerated **through their own renderers** and `test_dogfood_artifact_currency.py`
is green.

**Given** local gates are Windows-only while CI runs an ubuntu matrix
**Then** this story is **not marked done on a local pass alone**.

### Story 14.3: The assertion vocabulary crosses the languages the installer ships

*Added 2026-08-17 by [sprint-change-proposal-2026-08-17b.md](sprint-change-proposal-2026-08-17b.md),
APPROVED by XAgent007. **Runs strictly AFTER Story 14.2**, which owns the same frozenset.*

As the Argus maintainer,
I want an assertion to be recognised in every language the default install can parse,
So that a test with a real assertion is never flagged vacuous for being written in TypeScript.

**Acceptance Criteria:**

**Given** `_ASSERTION_CALLEES` holds **23** names and every one of them is `unittest`, while the
shipped index emits `expect`, `toBe` and `assertEquals` as ordinary edges — measured by execution
over six fixtures in the source proposal §1.3
**When** this story completes
**Then** the table recognises the assertion vocabulary of the languages `pyproject.toml` ships a
grammar for and DN-6 admits — at minimum JS/TS (`expect`, `toBe`, `toEqual`, `toThrow`, `assert`,
`ok`, `deepStrictEqual`), Java/JUnit (`assertEquals`, `assertThat`, `assertTrue`, `fail`) and Go
(`Fatal`, `Fatalf`, `Error`, `Errorf`, `NoError`, `Equal`) — **and the JS fixture measured at
`assertions=0 density=0 FLAGGED` is re-measured and is NOT flagged.**

**Given** the change can only raise `assertion_sites`, the NUMERATOR of a ratio whose floor fires
from BELOW
**Then** it is demonstrated **by execution** that no test flagged before is unflagged into a
BLOCKING finding, and that the total flag count **falls or holds** — never rises. A change that can
only remove flags must be shown to have only removed them.

**Given** two ratified corpus members are TypeScript (`xagents-webapp`, `agent-smith`) and the
source proposal's §2.3 corpus-impact claim is explicitly **UNMEASURED** — a derivation from a
measured mechanism, not a measurement
**Then** the flag delta over those members is measured **before and after**, and recorded as a
number. **If the prediction is wrong, this story records that it was wrong** and does not retro-fit
its rationale to the result.

**Given** NFR-P2 confines the language conditional to `argus/index/`
**Then** `_ASSERTION_CALLEES` stays a **FLAT, language-agnostic** name set on the
`_UNAMBIGUOUS_TEST_SUFFIXES` precedent (`vacuous_test.py:212-215`) — **no language field enters the
detector** — and the accepted cross-language collision cost (a Python `expect()` now counts as an
assertion; the error direction is one fewer flag) is recorded with its rejected alternative.

**Given** Story 14.2 owns the same frozenset and adds the pytest helpers to it
**Then** 14.3 runs strictly after 14.2 and does **not** re-open, re-order or re-litigate 14.2's
Python entries — the DN-4 discipline, applied to a second pair.

**Given** `DF-14-3-A` (the `startswith("test")` predicate), `DF-14-3-B` (Go selector calls absent
from the edge set) and `DF-14-3-C` (callback test blocks yielding no definitions) are measured and
filed
**Then** they are **CITED, NOT FIXED HERE**, and this story states plainly that Go and Java tests
remain unscored after it lands. ⛔ **`DF-14-3-A` MUST NOT be fixed alone**: Go tests are silent today
*because* of it, and lowering the predicate's case-sensitivity while `DF-14-3-B` stands would score
every Go test at `assertion_sites=0` and flag it — converting silence into a fresh false accusation
across an entire language. A and B move together or not at all.

**Given** AR8 (the scorer is PURE), AR4 (`Fraction`, never `float`) and NFR-D2 (deterministic,
zero-token)
**Then** all three hold unchanged, and no clock / uuid / random / iteration-order enters any
`.argus/`-bound output.

**Given** local gates are Windows-only while CI runs an ubuntu matrix
**Then** this story is **not marked done on a local pass alone**.

---

## Epic 15: Make the Gate Evaluable — a bench with the defect class in it · *Argus repo*

*Created 2026-08-17 by **operator decision (XAgent007)**, NOT by a change proposal — recorded here
because the distinction matters: `sprint-change-proposal-2026-08-17b.md` §4.4 states "no epic is
created", and that was true of that proposal. This epic is the separate, later container its §3.1
option 1 left unfiled, admitted by direct authorisation on the Story 13.4 precedent.*

Epic 14 repairs the instrument. It **cannot** clear the ≥80% gate, because a corrected detector is
expected to emit **zero** blocking findings on the current five-member corpus, and an empty
precision denominator is `UNEVALUABLE` by construction. Clearing needs **findings that are real**,
which needs a bench that **contains the defect class**. This epic assembles that bench.

**Covers:** the §2.5 operator decision's option (a) — `DF-13-5-A` · the line-numbering contract
between the detector and the 1.4 index (added 2026-08-19 by
[sprint-change-proposal-2026-08-19.md](sprint-change-proposal-2026-08-19.md))
**Depends on:** Epic 14 (a bench measured with a broken instrument measures nothing).
**Blocks:** nothing currently scheduled. It is the **new** attempt at clearing, not a repair of the
old one.

> ⚠️ **This epic does not clear the gate either.** It makes the gate *evaluable*. Whether it clears
> is a measurement, and the stopping rule was **pre-registered on 2026-08-17 in `DF-13-5-A`** —
> **before** any repository was chosen and before any number existed. One round. If that round
> yields zero blocking findings or precision below 80%, the answer is a better detector, **not a
> bigger bench.**

### Story 15.1: A bench with the defect class in it, chosen before anyone looks

As the Argus maintainer,
I want a candidate bench of independent public repositories selected against written criteria
**before** Argus is run over any of them,
So that whatever precision it eventually measures means something.

**Acceptance Criteria:**

**Given** selecting repositories *after* seeing what the tool says about them is the
corpus-shopping failure the 13.1 amendment rejected by name
**When** this story completes
**Then** the selection criteria are written and **frozen in a commit that precedes every commit
containing Argus output over any candidate**, and that commit sha is recorded in the story. Git
history is the evidence; a stated intention is not.

**Given** every criterion must be checkable **without running Argus**
**Then** the criteria are exactly these, and each is observable from the repository alone: an
admitted primary language; a test suite above a stated size floor; **demonstrable use of mocking**
(the defect class lives where mocks live); at least two years of history, so tests have had time to
rot; a permissive licence, recorded; independent provenance — **no XAgents-affiliated repository and
nothing Argus was developed against**; and a resolvable pin.

**Given** DN-6 admits Python, JavaScript, TypeScript, Go, Java and PHP, while `DF-14-3-A`/`-B`
leave Go and Java **unscored** and `DF-14-3-C` leaves callback-style JS/TS suites invisible
**Then** this bench is scoped **Python and TypeScript ONLY**, with that reason recorded. Admitting a
language the detector cannot score would inflate **N** — the number that satisfies the floor —
while contributing nothing to the number that gates. *(The `N` that gates and the `N` that
contributes are already different numbers; this story must not widen the gap.)*

**Given** protocol §6 **R2** makes ratification an **operator act** — *"choosing which repositories
are legitimate members, and fetching third-party source, are not autonomous acts"*
**Then** every candidate enters `tests/corpus/_manifest.py` with `eligible_for_n=False` and
`ineligible_reason="candidate — awaiting operator ratification (protocol §6 R2)"`. The row validates
at construction, so a candidate **cannot** silently count toward N; `MANIFEST_FIELDS` stays a closed
schema and no field is added.

**Given** NFR-S1 forbids third-party source bytes in this repository
**Then** a candidate is **metadata and a pin** — never vendored source — exactly as the five ratified
members already are.

**Given** the target is 12–20 candidates for ≥10 ratified
**Then** the story records **why each candidate was chosen**, and the recorded exclusions for any
repository considered and rejected. An exclusion without a reason is an oversight wearing a
decision's clothes (the DN-4 rule, applied to candidates).

**Given** this story is selection ONLY
**Then** it does **NOT** ratify, does **NOT** run Argus over any candidate, does **NOT** adjudicate
anything, and touches neither the ≥80% threshold, FR34, nor the manifest schema.

**Given** local gates are Windows-only while CI runs an ubuntu matrix
**Then** this story is **not marked done on a local pass alone**.

### Story 15.2: The detector and the index agree on what a line is

*Added 2026-08-19 by [sprint-change-proposal-2026-08-19.md](sprint-change-proposal-2026-08-19.md),
APPROVED by XAgent007 on that date. **Ordering, which travels as a CONSTRAINT and not as a
number:** this story must be `done` **before any commit containing Argus output over any Epic-15
candidate**. Story 15.1 is selection-only — it does not ratify, does not run Argus over any
candidate and does not adjudicate — so **15.1 is NOT blocked by this story and this story is NOT
blocked by 15.1**; the two may proceed in either order or concurrently. 15.1 was not renumbered to
express the ordering because an id in this repository is a **citation**: `stories/15-1-*.md`,
`sprint-status.yaml`, `DF-13-5-A` and the Epic-13 FINAL retrospective §14 all name it. The
precedent is Story 14.3, which was appended after 14.2 carrying a "strictly after 14.2" constraint
on its own record.*

As the Argus maintainer,
I want the detector to read the same lines the index numbered,
So that an invisible character in a file cannot make Argus say a fully-asserted test asserts
nothing.

**Acceptance Criteria:**

**Given** the false flag reproduced in `sprint-change-proposal-2026-08-19.md` §1.3 uses a fixture
with **no mock-bound assertions**, so the fact-(b) corroboration path was **never exercised**, and
the source proposal explicitly declines to assert an answer
**When** this story completes
**Then** it is **DETERMINED BY EXECUTION** whether the shifted line view can carry a finding to
**verdict-eligibility** — i.e. whether the corrupted span can make `ast_corroborated` read `True`
where a correct span reads `False`, or the reverse. The answer is **recorded as a measurement in
either direction**, and if it is *yes* the story records that the severity is higher than the
proposal that created it assumed. **Neither answer may be assumed, and "no reproduction found" is
recorded as exactly that rather than as "cannot happen".**

**Given** `str.splitlines()` splits on eleven things and the Story 1.4 index numbers lines by
newline alone
**Then** the fix is stated and implemented as a **LINE-NUMBERING CONTRACT** — the detector's line
decomposition is the index's line decomposition — and **not** as a special case for any one
character. A patch that names `\x0c` and no other character does **not** satisfy this AC.

**Given** eight characters were measured to survive the production read path
(`argus/pipeline_stages.py:124`, universal newlines) and to desynchronise the two views
**Then** the fix is **MEASURED, not assumed, against every one of them**: `\x0b` (VT), `\x0c` (FF),
`\x1c` (FS), `\x1d` (GS), `\x1e` (RS), `\x85` (NEL), `\u2028` (LS), `\u2029` (PS) — and `\r` and
`\r\n` are measured **too**, with their normalisation at the read path re-verified rather than
inherited from this list. A guard covers each, through the **real index**, and each is shown to go
RED before the fix.

**Given** the corrected decomposition changes what `_score` reads for every file
**Then** it is demonstrated **by execution** that on all-`\n` source the corrected and current
decompositions are **identical**, so the change is inert on the existing corpus and every existing
fixture, and corrective only where the two views currently disagree. Any flag-count delta over the
ratified corpus members is **measured and recorded as a number**, in both directions.

**Given** `TC-ArgusAgent-DETECT-001-107` is **VACUOUS** — `lf.splitlines() == crlf.splitlines()` is
`True`, so its headline assertion is `f(x) == f(x)` on a pure function, and its only live assertion
duplicates `-104` verbatim
**Then** `-107` is **REBUILT around the split rather than deleted** — the split is genuinely
unguarded and deleting the guard would remove the id that names the subject — and it is
demonstrated by a **mutation that makes it RED**, recorded in the story.

**Given** `TC-ArgusAgent-DETECT-001-118` is **WEAK** — `_score_one` scores the in-memory string, and
on Windows `write_text(newline=None)` writes the "LF" arm as CRLF (measured: 11 CRLF / 0 bare CR)
and the "CRLF" arm as `\r\r\n` (11 CRLF / 11 bare CR)
**Then** its terminator arm is made able to fail: the fixtures are written with the terminators they
claim (`newline=""` or `write_bytes`), and the scored source is derived from **the file that was
written** through the same read path production uses — **and its three load-bearing assertions
(`statement_count == 4`, `assertion_sites == 1`, `assertion_density == 1/4`) are preserved
unchanged.**

**Given** `tests/test_vacuous_detector.py` is at **1,161 of NFR-M1's 1,200** — 39 lines — and
`DF-14-3-H` requires the split **first**
**Then** the **COHESION SPLIT** happens **before** any case is added, on the `provenance_scan.py` /
`test_vacuous_density.py` / `test_status_document_registry.py` precedent, with **no function split
across the boundary**, the rejected boundary recorded in the new module's docstring, and **NO
`_EXEMPT_BY_DESIGN` entry and no shave** — `MAINT-001-04`'s registry may only shrink.

**Given** splitting the module that holds the moat's own false-accusation guards risks silently
dropping a case (`AI-E3-1`)
**Then** the `TC-ArgusAgent-*` id inventory is compared **by execution** before and after, and the
counts are shown equal.

**Given** `argus/pipeline.py` is at **1,111** and byte-fenced by Story 12.1
**Then** **no line is added to it.**

**Given** `argus/detectors/provenance_scan.py:63-73`, `:132` and `:452` document themselves as
*"line-terminator-agnostic by construction"* over a `splitlines()`-derived list
**Then** that prose is **re-derived against the corrected decomposition** and corrected if it has
become false. A stale docstring asserting an invariant that no longer holds is how the next author
reintroduces this defect.

**Given** `DF-14-3-A` and `DF-14-3-B` are **COUPLED**, and the one-character fix to `-A` alone
converts Go's harmless silence into a language-wide false accusation
**Then** this story does **NOT** touch `_is_test_function`, the edge extractor, or
`_ASSERTION_CALLEES`, and states plainly that Go and Java remain unscored and callback-style JS/TS
suites remain invisible after it lands (`DF-14-3-C`).

**Given** `argus/detectors/secret_scan.py` carries the **same** contract breach (`:334` counts
newlines, `:447` indexes `splitlines()`), measured in the source proposal §1.6
**Then** it is **cited and NOT fixed here** (`DF-15-2-B`), and the story records that the repair is
scoped to one detector while the contract is repository-wide.

**Given** AR8 (PURE scorer), AR4 (`Fraction`, never `float`), NFR-D2 (deterministic, zero-token) and
NFR-P2 (the language conditional lives in `argus/index/`)
**Then** all four hold unchanged, and **no threshold moves** — not `ASSERTION_DENSITY_FLOOR`, not
`MOCK_RATIO_CEILING`, not the ≥80% gate.

**Given** Story 15.1 is selection-only and does not run Argus over any candidate
**Then** this story does **NOT** block it and is **NOT** blocked by it; but this story must be
`done` **before any commit containing Argus output over any Epic-15 candidate.**

**Given** local gates are Windows-only while CI runs an ubuntu matrix, and `\r\n` handling is
exactly the class that differs across platforms
**Then** this story is **not marked done on a local pass alone.**

---

## Epic 16: Spend the Round Well — strengthen the gate, then measure once · *Argus repo*

*Created 2026-08-20 by [sprint-change-proposal-2026-08-20.md](sprint-change-proposal-2026-08-20.md),
which is **AWAITING OPERATOR APPROVAL** at the time this section is written. The epic and its
stories are filed at `backlog` so the plan has the container SD-5 found missing; **nothing in it may
start before that approval**, because §4.3 of the proposal amends protocol §5 and Story 16.4 spends
`DF-13-5-A`'s ONE round.*

> ✅ **APPROVED 2026-08-20 by XAgent007 (Engineering Lead).** The paragraph above is left exactly as
> written (§3.4 evidence immutability) rather than rewritten to say "approved" — it was the true
> state when the section was authored, and a plan document that silently re-narrates its own
> preconditions is the `DF-8-5-C` class in prose. **What the approval unblocks:** Stories 16.1, 16.2
> and 16.3 may now start and may apply §4.3's three §5 conditions, each deriving and recording its
> own constants. **What it does NOT unblock: Story 16.4**, which still opens by halting on the
> protocol §6 **R2** operator act — ratification and third-party fetch remain a separate,
> not-yet-taken decision, and approval of this epic is not approval to spend `DF-13-5-A`'s round.

Epic 14 repaired the instrument. Epic 15 established, without running the detector over anything,
that the five-member corpus **does not contain the defect class** — 1 co-occurrence file under the
strict predicate across 315 Python test files — and assembled a 14-candidate bench that does
(2,316 test files, 614 co-occurrence files). The gate is therefore `BLOCKED` on an **empty
denominator**, not on a shortfall.

This epic spends that bench. It does so **after** closing the three holes that would otherwise let
the resulting number mean less than it appears to, because closing them afterwards — once a result
exists to bias the choice — is corpus-shopping in the opposite direction.

**Covers:** the Epic 15 retrospective's SD-1 (R2 untaken), SD-5 (no container), SD-6 (the two
NFR-M1 splits) · `DF-13-5-A`'s ONE pre-registered round
**Depends on:** Epic 15 (the bench), Epic 14 (the instrument). A round measured with either missing
is a round spent either way.
**Blocks:** any attested-tier externalization claim. The DISCLOSED tier (FR34) is unaffected and
remains the honest fallback.

> ⚠️ **This epic may not clear the gate, and that is a permitted outcome.** `DF-13-5-A` was answered
> on 2026-08-17 **before any number existed**: **one** round, and if it yields zero blocking findings
> or precision below 80%, **the answer is a better detector, not a bigger bench.** Nothing in this
> epic may be read as licence to expand again.

> 🔒 **BINDING ORDERING CONSTRAINT.** Stories 16.1, 16.2 and 16.3 must land in commits that
> **precede every commit containing Argus output over any bench member**, evidenced by git ancestry
> exactly as Story 15.1's `TC-ArgusAgent-PRECISION-001-75` evidences its own. A guard asserting this
> is part of 16.4, not a promise made in prose.

### Story 16.1: A score drawn from one repository is not a score

As the Argus maintainer,
I want the precision gate to refuse a denominator that is too narrow to mean anything,
So that a figure computed from a single repository and a single rule class cannot be reported as if
it measured the tool.

**Acceptance Criteria:**

**Given** the last adjudicated population was 31 findings from **2 of 5** ratified members across
**1** distinct rule class, and the record computes `concentration.is_concentrated = True` while
stating in terms that it is *"not a threshold and not a distribution requirement"*
**When** this story completes
**Then** breadth is a **§5 condition**: precision is evaluable only over a population drawn from at
least a stated number of distinct contributing members **and** at least a stated number of distinct
rule classes. Below either, the outcome is `UNEVALUABLE` — the state already exists and already
forces the gate provisional. No new terminal state is invented.

**Given** every input to this threshold is **already computed** and recorded
**Then** the implementation reads those existing fields and does **not** re-derive them, so the
disclosure and the threshold can never disagree.

**Given** this project shipped 4 of 35 unreal guards in Epic 14
**Then** the new condition is driven to **both** outcomes by executed mutation — a population that
passes it and a population that fails it — and each mutation is observed RED before the guard is
trusted.

**Given** the constants must be defensible rather than convenient
**Then** the chosen numbers are **derived and recorded with their reasoning, never typed**, and the
derivation names what would have happened to the 2026-08-18 population under them.

**Given** §5 and Story 13.3 / AC5 forbid changes that make clearing easier
**Then** this story records explicitly that it makes clearing **harder**, and touches neither the
≥80% figure, `VALIDATION_SET_FLOOR_N`, the five ratified members, nor `MANIFEST_FIELDS`.

### Story 16.2: Part of the bench is sealed before anything is run

As the Argus maintainer,
I want a partition of the ratified bench sealed before any detector output exists over it,
So that the gate figure is computed over a population the tool was never tuned against.

**Acceptance Criteria:**

**Given** the cartridge corpus has an author-blind holdout (`holdout_vacuous`) and the repository
corpus that actually gates has **none**
**When** this story completes
**Then** the ratified bench is split by a **pre-committed, mechanically reproducible rule** (a
sha-ordered partition, so the split cannot be chosen to flatter a result), and the rule is frozen in
a commit that precedes every commit containing Argus output over any member.

**Given** a holdout that can be peeked at is not a holdout
**Then** the sealed partition is **structurally** distinguishable — a member's partition is a field
on its manifest row, validated at construction — and opening it is a single recorded act, not a
side effect of running the harness.

**Given** the gate must be computed over the sealed partition and tuning must happen only against
the open one
**Then** a guard asserts that any detector change dated after the seal cites which partition its
evidence came from, and the guard is driven to both outcomes.

**Given** N is a locked quantity
**Then** the split does **not** change `VALIDATION_SET_FLOOR_N`, does not drop a member, and does
not re-weight one. It partitions; it does not narrow.

### Story 16.3: A detector that finds nothing has not passed

As the Argus maintainer,
I want the gate to distinguish "accurate" from "silent",
So that a detector emitting three ultra-safe findings cannot score 100% and be called validated.

**Acceptance Criteria:**

**Given** `UNEVALUABLE` closed the emit-nothing hole for an **empty** denominator, but nothing
prevents a **tiny** one from clearing at 100%
**When** this story completes
**Then** a **yield floor** is a §5 condition: over a bench selected *because* it carries the defect
class, a run promoting fewer than a stated number of verdict-eligible findings is recorded as a
finding **about the detector**, not as a pass.

**Given** recall is diagnostic-only by the OI1 lock and this story must not silently re-open that
**Then** the floor is stated as a **yield** condition over the gating corpus and the OI1 bullet is
amended explicitly, struck-not-erased, rather than contradicted in passing.

**Given** the floor could be satisfied by noise
**Then** it composes with 16.1's breadth condition rather than replacing it: quantity without
breadth still fails.

**Given** the number must not be reverse-engineered from a result
**Then** it is derived and frozen **before** 16.4 runs, and the derivation is recorded.

### Story 16.4: Ratify, run, adjudicate, and let the arithmetic decide

As the Engineering Lead,
I want the ratified bench audited at its pins and every blocking finding adjudicated under §4,
So that the gate outcome is a measurement rather than an assertion.

**Acceptance Criteria:**

**Given** protocol §6 **R2** makes ratification an operator act — *"choosing which repositories are
legitimate members, and fetching third-party source, are not autonomous acts"*
**When** this story starts
**Then** it **HALTS** and names the act with options. Promotion is two deliberate edits per row; no
automation may take it. ⛔ **This story is not autonomous and must not be driven to completion by
the dev loop without the operator in the loop.**

**Given** 16.1, 16.2 and 16.3 must precede any output over a bench member
**Then** a guard asserts, from git ancestry, that each of their commits is an ancestor of this
story's first output commit and that none of them touches a candidate-output path — with its
non-vacuity preconditions pinned and the ancestry predicate driven to both outcomes.

**Given** every member must be read from its pinned git object and proved byte-for-byte
**Then** the run produces a corpus-read proof of the same shape as the 2026-08-18 one, so a zero is
again distinguishable from an absence.

**Given** §2 requires every disposition to carry a registered adjudicator and `UNADJUDICATED` is the
only value an automated producer may write
**Then** no row is dispositioned by any automated step, the adjudication is exhaustive under §4's
ladder, and the actual `expert_hours` are recorded as a `Fraction` against the ≤4-hour ceiling **as
a report, never a gate**.

**Given** `DF-13-5-A` permits exactly ONE round
**Then** this story consumes it, records that it has been consumed, and records the pre-registered
fallback verbatim. If the outcome is `UNEVALUABLE` or below threshold, **no further expansion is
proposed by this story.**

**Given** narrowing, dropping or re-weighting to move the ratio is forbidden
**Then** the outcome is recorded whatever it is, and `decide_gate` is re-run unmodified.

### Story 16.5: The record says who judged, and whether they were independent

As a prospective adopter of Argus,
I want the gate record to state whether its adjudication was independent of the tool's authors,
So that I can weigh the precision figure without having to reconstruct who was in the room.

**Acceptance Criteria:**

**Given** §2's QA Lead and External adjudicator are both **unfilled**, and §2 already says an
externalization sign-off *"SHOULD be outside the implementing team"*
**When** this story completes
**Then** the gate decision record carries an **independence status**, derived from the registered
adjudicators on the adjudication record rather than typed, naming which roles were filled and by
whom.

**Given** a non-independent result must not be quotable as an independent one
**Then** the rendered gate-status string carries the independence status wherever it carries the
precision figure, and a guard asserts the two cannot be separated.

**Given** FR34 already enforces provisional-status disclosure on every user-facing surface
**Then** this story **extends** that mechanism rather than forking a second one.

**Given** filling a role is an operator act
**Then** this story does **not** claim independence, does not fill a role, and does not gate on one
being filled. It makes the current state legible, whatever it is.

---

### Story 16.6: The assertion vocabulary recognises the assertion that is a `raise`

> Added by [sprint-change-proposal-2026-08-22.md](sprint-change-proposal-2026-08-22.md), **APPROVED
> by XAgent007 on 2026-08-22**. ⛔ **Precondition: `argus/detectors/vacuous_test.py` sits at
> 1,196/1,200 with `DF-15-2-D` filed. The module SPLIT lands FIRST, alone, in its own commit, with
> no behaviour change.** Four lines is not room for the fix and its guards.

As the Engineering Lead,
I want `raise AssertionError` counted as an assertion,
So that the advisory population is not inflated by tests that assert rigorously in a spelling the
tool cannot read.

**Measured basis (2026-08-22, read-only over pinned git objects):** `is_assertion_callee` recognises
the `_ASSERTION_CALLEES` table **or** the convention `\A_?assert\w*\Z`. That regex is
**case-sensitive**, so `AssertionError` does not match, and a `raise` is a statement rather than a
call to an assertion callee. **22 of the 1,032 flagged findings contain the idiom**, and because the
density scorer counts assertion statements, those tests are scored below their true density — the
tool over-flags, in the accusation direction.

**Acceptance Criteria:**

**Given** the ceiling and `DF-15-2-D`
**Then** the `vacuous_test.py` split lands **first, in its own commit**, byte-equivalent in
behaviour, and `DF-15-2-D` is discharged or re-filed against the new module sizes.

**Given** two assertion vocabularies exist for different questions (`DN-14-2-1`)
**Then** the recognition is added to the **WIDE** vocabulary only — the one that asks *"does this
test assert anything?"* — and ⛔ `_CORROBORATION_ASSERTION_CALLEES` stays **byte-unchanged at 23
names**, because widening the frozen table moves fact (b) toward an accusation.

**Given** a guard that cannot fail proves nothing
**Then** the new recognition is driven **RED by executed mutation**, with the tree restored
byte-exact, and the before/after flagged count over the 22 affected findings is recorded.

**Given** this story changes the advisory tier only
**Then** no finding becomes verdict-eligible, no threshold moves, and the gate outcome is unchanged.

### Story 16.7: Adjudicate the silent-test class before anyone proposes promoting it

> Added by [sprint-change-proposal-2026-08-22.md](sprint-change-proposal-2026-08-22.md), **APPROVED
> by XAgent007 on 2026-08-22**. ⛔ **Preconditions: Story 16.6 done, AND protocol §2's QA Lead role
> FILLED** — §4's borderline ladder terminates there, and this story can produce borderlines.

As the Engineering Lead,
I want the 36-member silent class adjudicated by a named human under §4,
So that any future promotion proposal carries a measurement instead of an estimate.

**Measured basis (2026-08-22):** formulating the per-call question as *"reaches the SUT, discards the
result, and asserts nothing at all"* yields **39** findings, of which **3** are false accusations
from the §16.6 vocabulary gap — **36 survive**. For comparison, the shipped fact (b) reaches **0**,
and dropping its provably-dead mock-referencing clause reaches **6**.

⛔ **Promotion is deliberately NOT proposed.** A spot-check found the class contains the **deliberate
smoke test**, where *"does not raise"* **is** the assertion, stated in a comment no analyser can
read. `DN-3` already carves out the explicit spelling (`pytest.raises`); this is the implicit one,
and the proportion is **unmeasured**. Promoting the class blind would manufacture exactly the false
🔴 that cross-cutting #6 exists to prevent.

**Acceptance Criteria:**

**Given** 16.6 changes what counts as an assertion
**Then** the class is **re-derived after 16.6**, not carried over, and its exact membership recorded.

**Given** protocol §4 requires a named human
**Then** every member carries one live TP/FP/BORDERLINE disposition with an `adjudicator` of the
form `"<who> (<role>)"` from §2's registered three, and ⛔ **no automated step writes a disposition.**

**Given** the smoke-test idiom is a legitimate pattern
**Then** it is adjudicated **explicitly as its own recorded outcome**, never folded into FP without
comment — the whole point of the story is to learn its proportion.

**Given** §3 sets a ≤4-hour expectation
**Then** actual `expert_hours` are recorded as an exact `Fraction` and compared by
`expert_hours_report()` — ⛔ **as a report, never as a gate.** Never trim the adjudication to fit.

**Given** §2 records the External adjudicator as unfilled
**Then** if the ladder reaches an unfilled role the story **STOPS** and reports which rows and why.

**Given** this story measures rather than promotes
**Then** ⛔ **no finding is promoted to verdict-eligible, no threshold moves, `decide_gate` is not
re-run, and no bench expansion is proposed** — in this story, the ledger, or any change proposal.

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
>
> ✅ **CLOSED 2026-08-10b via option (b).** The operator (**XAgent007**) records that **filing H1–H4 against
> the Minions backlog is their own step, taken outside this workflow.** H0 is **no longer UNOWNED**.
>
> **What this closure does and does not mean.** It ends the *ownership* gap — the failure mode where a
> handoff exists in a document and in no backlog. It does **not** mean H1–H4 have been filed. Until they
> are, the integration remains planned-and-relocated, and this repository's CI still cannot verify any
> of it. The prerequisites are unchanged: Epic 8 (correct verdict contract) and Epic 9 (a cycle-free,
> published `argus-agent`) are done; **assumption A5 remains ⚠️ UNSUPPORTED** and H3's blocking-vs-advisory
> policy decision is still required before that CI gate can be made blocking.

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

## Epic 17: Say What The Assertion Constrains — grade strength, not wiring · *Argus repo*

*Created 2026-08-24 by [sprint-change-proposal-2026-08-24.md](sprint-change-proposal-2026-08-24.md).
Filed at `backlog`; **AWAITING OPERATOR APPROVAL**. ⛔ This epic does NOT spend `DF-13-5-A`'s round
and approving it is not approval to spend it — the entry was DECLINED a second time on 2026-08-24
(`7edf74e`) and stays OPEN and UNSPENT.*

> ✅ **APPROVED 2026-08-24 by XAgent007 (Engineering Lead).** The paragraph above is left exactly as
> written (§3.4 evidence immutability) rather than rewritten to say "approved" — it was the true state
> when the section was authored. **What the approval unblocks:** Story 17.1 may start, and only 17.1
> — the BINDING ORDERING CONSTRAINT below is not relaxed by approval, and no successor-predicate
> output may exist over any corpus member until 17.1's pre-registration is committed.
> ⛔ **What it does NOT unblock:** `DF-13-5-A`'s round. The entry stays OPEN and UNSPENT, and approval
> of this epic is not approval to spend it. ⚠️ Story 17.4 additionally requires `AI-E16-7` — protocol
> §4's External adjudicator — to be filled before it can produce an adjudicated borderline, or it STOPS.

Epic 14 repaired the instrument. Epic 15 built a bench. Epic 16 strengthened the gate and did not
spend the round. **This epic fixes the reason the round was not worth spending.**

**Capability delivered:** the vacuous-test detector grades **what a test's assertions actually
constrain about the value the code under test returned**, replacing a mock-provenance vacuity signal
that cannot fire.

**Covers:** FR10 (advisory vacuous-test detector) · FR7 (AST grounding of a claim) · cross-cutting #6
(advisory-by-contract; the false-accusation moat) · `DF-INV-VACUOUS-A` · `DF-14-1-A` · `DF-16-7-A` ·
`DF-16-7-B` · `DF-12-2-D` · `DF-12-3-A` · `DF-AUD-DETECT-D`
**Depends on:** Epic 14 (the instrument), Epic 16 (the seven gate conditions). It depends on **no
bench round** — that is the point.
**Blocks:** nothing currently scheduled. It is the named condition of `DF-13-5-A`'s 2026-08-24
trigger: the entry returns to the operator when shipped promotions rise above zero.

> **Correction, 2026-08-26** *(Story `17-5-nothing-points-at-a-closed-story`, measured at HEAD
> `b8eaeee`)*. ⛔ **This epic's header and three of its acceptance criteria were written 2026-08-24,
> before Epic 18 ran and before any Epic-17 story ran. They are left exactly as written (§3.4) and
> corrected here.** Four statements above are now false, and one is self-defeating:
>
> 1. **"Capability delivered: … replacing a mock-provenance vacuity signal that cannot fire."**
>    Nothing was replaced at the verdict layer. `S1` landed **ADVISORY** in Story 17.3;
>    `argus/detectors/vacuous_test.py:796` is byte-unchanged as a parsed AST expression; no finding's
>    `verdict_eligible` moved.
> 2. **`**Covers:**` lists `DF-INV-VACUOUS-A`, `DF-14-1-A`, `DF-16-7-A`, `DF-16-7-B`, `DF-12-2-D`,
>    `DF-12-3-A`.** ⛔ **None of the six was delivered by Epic 17.** All six are **STILL OPEN**, each
>    now carrying a dated append-only note under its own ledger block with a corrected pointer and a
>    live owner (XAgent007, Engineering Lead). The only entries Epic 17 disposed of are
>    `DF-AUD-DETECT-D` (Story 17.3) and `DF-INV-VACUOUS-B` (Story 17.2).
> 3. **Story 17.5's first AC — *"re-homing notes pointing at Epic 17"*.** ⛔ **A pointer at Epic 17
>    would be the same defect one epic later**, since Epic 17 is itself ending. The six are re-homed
>    to a **named human owner** plus a scope change to be argued through `bmad-correct-course`, on
>    `DF-16-7-B`'s precedent — never to a story or an epic that has already run.
> 4. **Story 17.5's second AC — *"`DF-AUD-DETECT-A`/`-B`/`-E`/`-F` are pointed at Epic 18 and `-D` at
>    Story 17.3 — scheduling notes only"*.** ⛔ **DISCHARGED AND SUPERSEDED.** All five entries
>    already carry terminal dispositions and all five stories are `done`, so executing this literally
>    would point five entries at five closed stories — the exact defect the story exists to end. It
>    is replaced by dated **disposition pointers** naming each disposing story and fix sha
>    (`DF-AUD-DETECT-D` → `2db5ce0`, `-E` → `9e3fdc2`, `-F` → `0ba6a98`).
> 5. **Story 17.5's third AC names *four* modules carrying stale Story-6.2 forward references.**
>    Measured at `b8eaeee` the set is **12 sites across 7 modules**, of which the AC names 5 across
>    4. ⚠️ **One of the twelve, `argus/detectors/assertion_strength.py:64`, was created by Story 17.3
>    on 2026-08-25** — one story before the story chartered to remove the sentence. All twelve are
>    corrected; true-historical references, two behaviour-bearing strings and `tests/**` are carved
>    out by name and left byte-identical.
>
> Full record, with every figure and every line reference:
> [deferred-work.md](deferred-work.md) under *"Story 17.5 dispositions — 2026-08-26"*.

> ⛔ **THE MEASURED REASON THIS EPIC EXISTS** (`7d8c9ba`,
> [research/technical-argusagent-stage-mismatch-measurement-2026-08-24.md](research/technical-argusagent-stage-mismatch-measurement-2026-08-24.md)).
> Over all **1,032** flagged findings at the five pinned shas, stage 1 selects `density_only`
> **1,025 (100%)** and the mock arm has **never fired**; stage 2 asks an exclusively mock-provenance
> question and promotes **0**. The two stages are graded on different definitions of vacuity and
> their intersection on the ratified corpus is **empty**. A bigger bench samples more repositories
> through an aperture that is structurally shut.

> ⛔ **`consumed == 0` IS NOT LOOSENED BY THIS EPIC.** The asymmetry is what keeps the
> false-accusation moat closed, and the 2026-08-21 research is explicit that nothing argues for
> relaxing it. This epic **REPLACES** the vacuity signal; it does not widen fact (b) by clause
> removal. Per `DF-16-7-B`, a different predicate must be **argued** as one — Story 17.2 is that
> argument.

> 🔒 **BINDING ORDERING CONSTRAINT.** Story 17.1 — the pre-registered precision criterion — must land
> in a commit that **precedes every commit containing a successor predicate's output over any corpus
> member**, evidenced by git ancestry exactly as Story 15.1's `TC-ArgusAgent-PRECISION-001-75`
> evidences its own. Yield and precision move in opposite directions; a criterion written once a
> number is in view is not a criterion. A guard asserting the ancestry is part of 17.4, **not a
> promise made in prose**.

> ⚠️ **`Story 6.2` IS DONE AND IS NOT REOPENED.** Four shipped modules and six open ledger entries
> name it as the owner of *"real assertion provenance"*. **It never had that scope** — its story file
> carves out dataflow explicitly and it was scoped to claim-grounding for NON-TEST Python files — and
> Epic 6's retrospective is signed. Story 17.5 re-homes those references here rather than editing a
> closed record. ⛔ `DF-1-7-B` is **not** in that set: it is CLOSED and correctly names 6.2 as its
> closer.

> ⚠️ **PRECONDITION, not a story: `AI-E16-7`.** Protocol §4's ladder still has no step-3 holder. If
> Story 17.4's measurement produces borderlines needing adjudication, the External adjudicator role
> must be filled first, or 17.4 **STOPS** and reports which rows and why.

### Story 17.1: Write down what would count as precision, before the number exists

As an Engineering Lead,
I want the precision criterion for any successor predicate pre-registered before that predicate
exists,
So that a yield increase cannot be graded against a standard chosen once the result is in view.

**Acceptance Criteria:**

**Given** the 2026-08-17 rule's own discipline — the branch was chosen before Story 13.5 ran, before
the bench was chosen, and before any number existed
**When** this story completes
**Then** a committed, dated pre-registration states the population precision will be measured over,
the adjudication protocol version, the acceptance threshold, and the named consequence of falling
below it — **with no successor predicate implemented and no new finding in existence**.

**Given** yield and precision move in opposite directions
**When** the pre-registration is written
**Then** it states the maximum acceptable **false-accusation exposure**, not only a precision floor —
a ratio alone is satisfiable by a tiny denominator.

**Given** `DF-13-5-A` is OPEN and UNSPENT
**Then** the pre-registration ratifies no member, fetches no third-party source, spends no round, and
says so in terms.

### Story 17.2: A different predicate, argued as one

As an Engineering Lead,
I want the successor vacuity signal specified and argued as a genuinely different predicate,
So that it cannot be mistaken for a loosening of fact (b) by clause removal.

**Acceptance Criteria:**

**Given** `DF-16-7-B` records that promoting `V2` would be a genuinely DIFFERENT predicate, and that
**30 of its 36 rows lie outside `V1` entirely**
**When** this story completes
**Then** a committed specification states the successor's definition, the defect shape it claims to
detect, and **which findings each admits that the other does not**.

**Given** `consumed == 0` is what keeps the false-accusation moat closed
**Then** the specification states in terms that the clause is **NOT** loosened, and that the
successor does not reach corroboration by removing it.

**Given** the mock-referencing clause fires **0 times in 1,032**
**Then** the specification records whether mock binding remains an input at all; if it does not,
`DF-INV-VACUOUS-B` is dispositioned **moot-by-replacement** with a dated note rather than left open.

### Story 17.3: Grade what the assertion constrains

As an Engineering Lead,
I want each assertion in a flagged test graded on whether — and how strongly — it constrains a value
derived from the code under test,
So that a test which runs the SUT and tolerates any result is distinguishable from one that checks it.

**Acceptance Criteria:**

**Given** a test span, its source lines and the 1.4 edge set
**When** the detector scores it
**Then** each assertion is graded on a stated, committed scale — at minimum *does not reference an
SUT-derived value* / *constrains only its existence or type* / *constrains its value* — stored as
counts, **never rendered sets** (NFR-D2 / AR4).

**Given** the scorer is PURE (AR8)
**Then** grading reads the source text and the index and nothing else — no re-parse, no second
grammar call, no clock/uuid/random.

**Given** a parse or resolution failure
**Then** it degrades to a recorded condition, never an uncaught raise (NFR-R1); and **given** strength
cannot be established **then** the finding does **NOT** gain verdict-eligibility. The conservative
default stays the moat.

**Given** `DF-AUD-DETECT-D` records that `_logical_statement_end` and `_scan_span` are two derivations
of the same statement-boundary question (AR7 §3.3, one-derivation discipline)
**When** this story extends the span scanner
**Then** the two collapse to **ONE** derivation *before* assertion-grading is layered on it, and the
collapse is proven output-neutral by re-running the 1,032-finding harness and diffing — **byte-identical,
or it is not a collapse**.

**Given** `DF-AUD-DETECT-C` measures the detector layer's hot path in the density denominator
**Then** this story records span-scan cost **before and after** its addition, so a regression is
disclosed rather than discovered later. ⛔ **This is not a performance story** — `-C` stays OPEN and
is not dispositioned here.

### Story 17.4: Run it once, and let the pre-registered criterion decide

As an Engineering Lead,
I want the successor predicate measured over the five already-ratified members and graded against
17.1's criterion,
So that the outcome is decided by arithmetic written before the number existed.

**Acceptance Criteria:**

**Given** the five ratified members at their pinned shas
**When** the measurement runs
**Then** it reports the eligible population, its distribution across contributing members and rule
classes, and the precision measured under the protocol version 17.1 named — with **NO member
ratified, NO third-party source fetched and NO round spent**.

**Given** Epic 16's breadth condition
**Then** a population drawn from too few members or rule classes returns `UNEVALUABLE` — the state
already exists and already forces the gate provisional. **No new terminal state is invented.**

**Given** the binding ordering constraint above
**Then** a committed guard asserts **by git ancestry** that 17.1's commit precedes every commit
carrying successor-predicate output, proven RED against a violating arrangement.

**Given** protocol §4's ladder has no step-3 holder (`AI-E16-7`)
**Then** a persistent adjudication disagreement **STOPS** and reports which rows and why — never
resolves by default.

**Given** the result
**Then** `DF-13-5-A`'s 2026-08-24 trigger is **evaluated and the observation recorded**; the entry
returns to the operator if shipped promotions rose above zero. ⛔ **This story takes no branch.**

### Story 17.5: Nothing points at a closed story

As an Engineering Lead,
I want the dangling forward-references to Story 6.2 re-homed and a guard that stops new ones,
So that work with no container stops being recorded as work that is already scheduled.

**Acceptance Criteria:**

**Given** Story 6.2 is `done`, its epic retrospective signed, and its story file carving out dataflow
explicitly
**When** this story completes
**Then** the six open ledger entries naming it — `DF-12-2-D`, `DF-12-3-A`, `DF-14-1-A`, `DF-16-7-A`,
`DF-16-7-B`, `DF-INV-VACUOUS-A` — carry **dated append-only** re-homing notes pointing at Epic 17,
and `DF-1-7-B` is **left untouched** because it is CLOSED and correctly names 6.2 as its closer.

**Given** the same commit owes the scheduling notes deferred by the change proposal
**Then** `DF-AUD-DETECT-A`/`-B`/`-E`/`-F` are pointed at Epic 18 and `-D` at this epic's Story 17.3 —
**scheduling notes only; nothing is dispositioned, closed or edited above.**

**Given** four shipped modules forward-reference Story 6.2 for work it never contained
**Then** the comments in `argus/detectors/provenance_scan.py`, `argus/audit/deep_pass.py`,
`argus/audit/deep_audit.py` and `argus/audit/__init__.py` name the real owner, with **no behaviour
change** and `argus/**` otherwise byte-unchanged.

**Given** the 2026-08-21 research recommends *"complete Story 6.2 … already scheduled"*
**Then** a dated correction note records that the recommendation rested on the stale reference and
that the work was never scheduled — **the research document is NOT rewritten** (§3.4).

**Given** the defect class this story exists to end
**Then** a committed guard asserts that **no ledger entry's `target_story` names a story whose
`sprint-status.yaml` key is `done`**, proven RED against the pre-fix state.

## Epic 18: The Secret Detector Reports What It Finds — discharge the detector audit · *Argus repo*

*Created 2026-08-24 by [sprint-change-proposal-2026-08-24.md](sprint-change-proposal-2026-08-24.md).
Filed at `backlog`; **AWAITING OPERATOR APPROVAL**.*

> ✅ **APPROVED 2026-08-24 by XAgent007 (Engineering Lead).** The paragraph above is left exactly as
> written (§3.4). **What the approval unblocks:** all four stories, with **18.1 first** — it is the
> live security false negative and the only one of the four where something real is dropped today.
> ⛔ **`DF-AUD-DETECT-A` WAS INDEPENDENTLY RE-VERIFIED BEFORE THIS APPROVAL, by execution rather than
> by reading.** Re-run through the shipped `SecretScanDetector.run()` on 2026-08-24: the `localhost`
> line returns **0** findings, the `example.com` line returns **0**, and the CONTROL — the same value
> with the sentinel substring removed — returns **1**. All three match the entry. Read against the
> source: `is_public_sentinel` (`secret_suppression.py:116`) tests `sentinel in snippet_clean`, it is
> consulted at **step 2** above the Live-Key Safeguard at **step 3**, and `is_live_production_key`
> (`:125`) carries the same `if sentinel in snippet: return False` short-circuit, so the safeguard
> disables itself on the same string. **The entry is sound and its citations resolve.**

⛔ **SEQUENCED BEFORE EPIC 17, DESPITE THE HIGHER NUMBER.** Epic numbers are CREATION order in this
repo and always have been; execution order is stated, not inferred from the number. Epic 18 runs
first because `DF-AUD-DETECT-A` is a **live security false negative** and Epic 17 is five stories of
detector architecture. **Nothing in Epic 17 depends on Epic 18** — the ordering is urgency, not
coupling, and either may be re-sequenced without rework.

**Capability delivered:** a hardcoded credential is no longer silently dropped because the value it
sits in happens to contain the substring `localhost`.

**Covers:** FR11 (detect hardcoded secrets) · FR28 (redaction) · `DF-AUD-DETECT-A` · `-B` · `-E` ·
`-F`
**Depends on:** nothing. Every entry is measured, reproduced and self-contained.
**Blocks:** nothing. ⛔ It does **not** block Epic 17 and must not be used to delay it.

> ⛔ **`DF-10-3-B`'s SAFETY CLAIM IS FALSIFIED, and this epic is where that is repaired.** The
> 2026-08-24 detector audit reproduced it through the shipped `SecretScanDetector.run()`: a real
> credential in `postgres://admin:Tr0ub4dor3@localhost:5432/prod` returns **0 findings**, while the
> same value with the sentinel substring removed returns **1**. The public-sentinel test is
> **substring containment** and it runs at step 2, **above** the Live-Key Safeguard at step 3 — and
> `is_live_production_key` carries the same short-circuit, so the safeguard disables itself on the
> same string.

### Story 18.1: The sentinel table matches values, not substrings of them

As an Engineering Lead,
I want the public-sentinel suppression to match a value rather than appear anywhere inside it,
So that a real credential is not dropped because its host happens to be named `localhost`.

**Acceptance Criteria:**

**Given** `argus/detectors/secret_suppression.py:116` tests `sentinel in snippet` over a table holding
five sentinels shorter than 20 characters
**When** this story completes
**Then** the test is containment-**to-equality** (or a bounded match that cannot fire on a substring
of a larger secret), and the Live-Key Safeguard's own short-circuit is removed so it can no longer
disable itself.

**Given** the audit's three-line reproduction
**Then** a regression test is committed carrying all three lines, proven **RED** before the fix and
**GREEN** after, **including the control line** — the same value with the sentinel removed — which
must still be reported.

**Given** `DF-10-3-B` states a safety claim this measurement falsifies
**Then** it carries a **dated append-only falsification note**; the entry above it is **not
rewritten** (§3.4).

### Story 18.2: The redaction call keeps the evidence it computes

As an Engineering Lead,
I want `run()`'s producer-side redaction to retain the evidence it computes,
So that a call that looks load-bearing either is, or is removed.

**Acceptance Criteria:**

**Given** `DF-AUD-DETECT-B` records that the call computes evidence and discards it
**Then** either the evidence is retained and used, or the call is deleted — and the choice is
recorded with its reason.

**Given** the entry states in terms that **no secret leaks and none can**, the redaction guarantee
being structural
**Then** this story asserts that guarantee still holds after the change, and does not weaken FR28.

### Story 18.3: Two regex precision defects

As an Engineering Lead,
I want the two measured regex defects in `secret_scan` corrected,
So that the detector over-reports less without ever moving toward a false green.

**Acceptance Criteria:**

**Given** `DF-AUD-DETECT-E` records a missing left word boundary and its sibling defect
**Then** both are corrected with a regression test per defect, proven RED before and GREEN after.

**Given** the entry records the error direction is **OVER-reporting, never a false green**
**Then** the change is proven not to remove any finding the pre-fix detector reported for a real
secret.

### Story 18.4: The `Detector` Protocol is load-bearing or it is deleted

As an Engineering Lead,
I want the `Detector` Protocol either used or removed,
So that a contract that reads as load-bearing is not asserted by one test and used by nothing.

**Acceptance Criteria:**

**Given** `DF-AUD-DETECT-F` records the Protocol is asserted by exactly one test and used by nothing
**Then** either the detectors are typed against it — so it constrains something — or it is deleted
and its lone test with it, and the choice is recorded with its reason.

**Given** nothing is wrong at runtime today
**Then** this story changes **no detector output**, proven by re-running the suite and the
1,032-finding harness.

---

## Epic 19: Give The Operator Acts A Container — then let the fold decide · *Argus repo*

*Created 2026-08-26 by [sprint-change-proposal-2026-08-26.md](sprint-change-proposal-2026-08-26.md).
Filed at `backlog`.*

> ✅ **APPROVED 2026-08-26 by XAgent007 (Engineering Lead).** The paragraph above is left exactly as
> written (§3.4). **What the approval unblocks:** the filing of this container and the drafting of
> **19.1** and **19.6**, which are autonomous and depend on no operator act. ⛔ **It unblocks
> NOTHING ELSE.** It ratifies no member, writes no disposition, spends no round and moves no
> threshold. **19.2 and 19.4 are NOT approved by it** — they are operator acts and are filed
> `operator-act` precisely so that approving the epic cannot be mistaken for approving them.

⛔ **THE SEQUENCING IS INVERTED FROM THE NORMAL LOOP, AND THAT IS THE POINT.** Epic 17 froze a
criterion and measured it once; the fold returned **`UNEVALUABLE`** because both of its arms were
true at the same time — the sealed∩ratified intersection is **EMPTY**, and there are **ZERO**
adjudicated rows of any successor class. Neither is a code defect and neither can be cleared by a
dev story. An epic of dev stories placed in front of an unperformed operator act buys a **second**
`UNEVALUABLE` (`AI-E17-4`). So the operator acts come first, and each autonomous story is built to
produce the package the human needs and then **STOP** — the shape Story 13.1's ESCALATION and Story
17.4's HALT already established.

**Capability delivered:** the two blocking prerequisites for ever evaluating a successor predicate
have a container, and every ledger entry has a destination or a dated deferral. ⛔ **NOT a promoted
successor predicate, and NOT a cleared gate.**

**Covers:** `AI-E17-4` · `AI-E17-8` (= `AI-E16-7`) · `AI-E17-7` (= `AI-E18-10`) · `AI-E16-1`
**Depends on:** two dated operator rulings — the `DF-13-5-A` question (§3.4 of the proposal) blocks
19.2, and the External-adjudicator naming blocks 19.4.
**Blocks:** any future epic that proposes to promote a successor predicate.

> ⛔ **THIS EPIC MAY END WITH `NOT_MET`, AND THAT IS A SUCCESS OF IT.** An epic that can only
> succeed by producing a passing number is the artifact Epic 13 exists to make impossible. 19.5
> records whatever the frozen fold returns.

> ⛔ **THE `Covers:` LIST ABOVE IS RE-DERIVED FROM `deferred-work.md` ON DISK AT ROLL-UP** — per
> `AI-E17-13`, before `epic-19: done` may be written. Epic 17's header named six ledger entries it
> would cover and delivered none of the six; the falsification stood until one story happened to be
> chartered to look.

### Story 19.1: The ratification package the operator cannot rule without

As an Engineering Lead,
I want one worksheet carrying, for each sealed bench member, the facts a §6 R2 ratification turns on,
So that the operator act is a judgement on measured evidence rather than on a list of names.

**Acceptance Criteria:**

**Given** `SEALED_PARTITION_TABLE` carries six `sealed` members, all `eligible_for_n = False`
**Then** the worksheet carries, per member, its pinned sha, licence, primary language, size, and the
finding count the **unmodified** shipped detector produces at that sha.

**Given** protocol §6 R2 reads *"choosing which repositories are legitimate members, and fetching
third-party source, are not autonomous acts"*
**Then** this story ratifies nothing, flips no `eligible_for_n`, reaches no network, and ends by
STOPPING at the operator act — asserted structurally over the module's AST, as `-141` does.

### Story 19.2: ⛔ RATIFY SEALED MEMBERS — **OPERATOR ACT (§6 R2)**

⛔ **NOT A DEV STORY.** Filed `operator-act`. A `bmad-dev` subagent must refuse it.
⛔ **BLOCKED** until the `DF-13-5-A` question is ruled, either way, with a date and a name.

### Story 19.3: The successor-class adjudication worklist

As an Engineering Lead,
I want `UNADJUDICATED` rows with locators for the successor class over the ratified-and-sealed
population,
So that the named humans have something to judge and the machine has judged nothing.

**Acceptance Criteria:**

**Given** `UNADJUDICATED` is the only vocabulary member an automated producer may write, and
`AdjudicationRow.__post_init__` raises `UnregisteredAdjudicator` on any attributed row
**Then** every row this story writes carries no adjudicator and no date, and the story STOPS.

**Given** the record today holds 31 rows of the **incumbent** class `vacuous_test_ast`
**Then** those 31 rows are byte-unchanged, and the new rows are distinguishable from them by
`rule_id` alone.

### Story 19.4: ⛔ ADJUDICATE THE SUCCESSOR-CLASS SAMPLE — **NAMED-HUMAN ACT (§4)**

⛔ **NOT A DEV STORY.** Filed `operator-act`. Engineering Lead + QA Lead, per §2.
⛔ **BLOCKED** until §2's **External adjudicator** is named and dated. The one comparable population
produced **5 borderlines in 31 rows (16%)**, so §4's third rung is reached at a rate that is not
low, and a role filled mid-adjudication is indistinguishable on the record from a role filled to
obtain a result (the 2026-08-22 discipline).

### Story 19.5: Re-run the frozen fold and let it decide

As an Engineering Lead,
I want the pre-registered criterion evaluated once more against the record as it then stands,
So that the outcome is the criterion's and not the story's.

**Acceptance Criteria:**

**Given** the criterion was frozen at pre-registration and `CRITERION_OUTCOMES` is closed at three
**Then** nothing is re-frozen, re-derived or re-typed, and `evaluate()` is imported rather than
re-implemented — the `AI-E17-5` one-derivation obligation, with the search recorded.

**Given** `MET`, `NOT_MET` and `UNEVALUABLE` are all admissible results
**Then** the outcome is recorded **whatever it is**, with the counts that produced it, and no
threshold moves in either direction.

### Story 19.6: Every ledger entry has a container or a dated deferral

As an Engineering Lead,
I want every `deferred-work.md` entry whose `target_story` names a `done` story to carry a
destination or a dated deferral,
So that work with no container is visible as such rather than parked behind a stale pointer.

**Acceptance Criteria:**

**Given** `_POINTS_AT_DONE_AT_LANDING` carries **49 pairs across 46 distinct ids** — 6 tagged
`"17-5"` and **43 tagged `"unverified"` that have never been measured against the codebase**
**Then** each is verified against the tree and partitioned, and `DF-AUD-DETECT-C` — which is in
`AI-E17-7` but not in the registry — is included by name.

**Given** the registry **can only shrink** and `-80` fails both on a registered pair that becomes
clean and on any unlisted affirmative stale pointer
**Then** the registry shrinks by exactly the entries that gained a container, in the same commit.
⛔ **No mass re-homing** (`AI-E12-3`) and **no narrowing until it goes green** (Story 12.1's named
anti-pattern).

**Given** `deferred-work.md` carries a **lone CR at line 5459** and is otherwise CRLF-uniform
**Then** every edit is made in binary mode and both byte invariants are re-measured before and after.
