---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-06-18'
readiness: 'READY FOR IMPLEMENTATION'
inputDocuments:
  - _bmad-output/design-artifacts/APAA/E-PRD/prd.md
  - _bmad-output/design-artifacts/APAA/product-brief-apaa.md
  - _bmad-output/design-artifacts/APAA/product-brief-apaa-distillate.md
  - _bmad-output/design-artifacts/APAA/research-domain-2026-06-17.md
  - _bmad-output/design-artifacts/APAA/research-market-2026-06-17.md
  - _bmad-output/design-artifacts/APAA/research-technical-2026-06-17.md
  - _bmad-output/planning-artifacts/decisions/2026-06-18-apaa-placement-under-minions-core.md
  - _bmad-output/project-context.md
workflowType: 'architecture'
project_name: 'APAA (AI Project Assurance Audit)'
user_name: 'XAgent007'
date: '2026-06-18'
scope: 'V1 (Tier-A spine -> Tier-B per PRD cut-order); headless; placed at minions_core/apaa/'
placement_decision: _bmad-output/planning-artifacts/decisions/2026-06-18-apaa-placement-under-minions-core.md
---

# Architecture Decision Document — APAA (AI Project Assurance Audit)

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

> **Scope note:** This is the architecture for **APAA**, a SEPARATE headless audit sub-tool placed at
> `minions_core/apaa/` (placement decision 2026-06-18). It is distinct from the Minions platform
> architecture (`_bmad-output/planning-artifacts/architecture.md`). APAA reuses Minions infra by import
> but ships its own `APAA-*` architecture-driver namespace, defined in this document.

## Project Context Analysis

_Enhanced through a Party-Mode architectural roundtable (Winston · Murat · Amelia · John) and an
Advanced-Elicitation pass (First-Principles · Pre-mortem · Red-Team). Provenance is noted inline._

### Requirements Overview

**Functional Requirements (33):** Eight capability clusters — Repository Intake & Partitioning (FR1–4),
Coverage Ledger & Grounded Evidence (FR5–9), Defect Detection (FR10–14), Release-Readiness Verdict
(FR15–18, FR33), Self-Audit & Trust (FR19–20), Cost Governance (FR21–22), Governance/Escalation/Evidence
Integrity (FR23–29), Invocation & Resumability (FR30–32). Architecturally they form one **deterministic
dataflow** whose terminal stage (the verdict) is a pure function of a fixed-enum coverage ledger.
Tier-B FRs (FR7, FR12, FR19, FR24, FR26) are the validation-grade layer over a demo-grade Tier-A spine
(see the FR7 split decision below).

**Non-Functional Requirements (21):** Determinism/Reproducibility (NFR-D1–3, the keystone — stable-not-
bit-identical via content-addressed memoization), Security/Containment (NFR-S1–5), Cost Efficiency
(NFR-C1–3), Reliability/Honest-Degradation (NFR-R1–2), Portability (NFR-P1–2, sequential byte-identical
to parallel), Auditability (NFR-A1–3, hash-chained additive-only envelope), Scale Envelope (NFR-SC1,
≤40 files/15k LOC/unit), Maintainability (NFR-M1–2).

**Scale & Complexity:** High.
- Primary domain: headless developer-tool / CLI audit engine + contract-producer (frozen artifacts +
  deterministic exit codes). No UI; no V1 HTTP service.
- Complexity level: High (determinism-as-requirement, LLM-as-auditor trust frontier, liability posture,
  context-rot at repo scale).
- Estimated architectural components: ~8–10 (intake/stack-detect, AST/code-graph index + partitioner,
  breadth-tool runner, depth-audit agent, coverage-ledger, defect detectors, pure-function verdict gate +
  Prosecutor, cost governor, `.apaa/` store + envelope, cartridge self-audit harness, CLI/invocation
  contract).

### Technical Constraints & Dependencies

- **Placement:** `minions_core/apaa/` sub-package; dual-use (internal import + external `apaa` CLI via
  `minions[apaa]` extra). Reuses Minions infra BY IMPORT: ADR #18 hash-chained ledger patterns,
  permission tiers, budget guardrails, `adapter_portability`, workspace-containment (no fork).
- **Determinism is the binding constraint:** bit-identical LLM output is infeasible (temp-0 nondeterminism,
  GPU/batch variance, silent model rotation). Mechanism = pure-function ledger/verdict + content-addressed
  memoization with the model checkpoint pinned into the cache key; a model rotation is a re-audit event.
- **The "recording schema" is a first-class frozen contract** (Winston). Determinism rests not only on
  the coverage-ledger enum but on the schema of the RECORDED FINDINGS that LLM calls emit. The verdict is
  a pure fold over recordings; if a recording omits a field the verdict later needs, you are forced to
  re-run an LLM. Freeze the recording schema as aggressively as the verdict schema.
- **Cache key = the full recording-producing closure, not just the model checkpoint** (Winston + Murat).
  Key inputs: content-hash + model checkpoint + prompt-template version + tool versions (tree-sitter
  grammar, radon) + budget/materiality config + work-manifest scope + **a content-hash of the enabled
  detector SET (code+config), NOT a human-written APAA version string** (R3). The model checkpoint is
  captured from each **API response** (not config); a mid-run **checkpoint drift → `checkpoint_drift`
  finding → abort/re-audit** (R3). The key DERIVATION is itself a pure function to golden-test, with a CI
  canary that fails when key inputs change without a version bump.
- **Stack:** Python 3.11+ (Minions baseline), Pydantic v2 + JSON Schema frozen contracts; AST = Python in
  V1 (`claim_emitted` proxy elsewhere), via a stack-agnostic `claim → validated?` interface.
- **Headless-only** (CLAUDE.md §3.7): artifacts + exit codes; no UI/HTTP-service surface in V1.
- **Cross-product boundary:** APAA CONSUMES (never builds) Minions layers (a)/(d)/(e) [V2–V4]; V1 is
  self-contained (local memoization, local cost ceiling).

### Cross-Cutting Concerns Identified

1. **Recording-producing-closure cache key** — the determinism keystone is the KEY, not the verdict math
   (which is trivially pure-testable). Enumerate every input; golden-test the derivation (Winston + Murat).
2. **Memoization caches ERRORS → reproducibility ≠ correctness** (R2, pre-mortem + red-team). A stable
   false 🔴 is worse than a flaky one — consistently wrong and trusted-as-stable. Cache entries MUST
   invalidate on detector-set-hash change, and a human-**rejected** finding must **bust its own cache key**
   (else a false 🔴 is served forever).
3. **Envelope canonicalization / single serializer** — NFR-P1 (sequential byte-identical to parallel) dies
   the day a second `json.dumps` appears with different kwargs. Pin ONE `apaa/store/canonical.py`
   (`sort_keys=True, separators=(",",":"), ensure_ascii=False`, `\n`-terminated UTF-8); forbid wall-clock /
   `uuid4` / `getpid()` / dict-iteration-order / `set`-iteration in any `.apaa/` write path. **Heuristic
   ratio scores stored as fixed-precision decimal / exact fraction — floats are an NFR-P1 byte-diff
   landmine across hosts** (R4, red-team).
4. **`cross_partition` finding class + Prosecutor cut-edge pass** (Winston) — graph-partitioning moves
   seam-loss into edge-cut quality; a defect spanning a cut (caller in A, callee in B) is invisible to any
   single deep audit and must not land silently as `inferred`. The Prosecutor specifically re-reads cut edges.
5. **Redaction is a property of the recording PRODUCER, not a post-filter** (Winston) — line-range citations
   can reconstruct source; cite locations, never bytes. Findings carry AST spans + counts, never excerpts of
   secret-bearing source.
6. **Heuristic findings are advisory-by-contract** (Murat) — the vacuous-test detector (assertion-density +
   mock-ratio, which FPs on table-driven/snapshot tests) emits `audited_shallow` evidence-carrying findings;
   it cannot move the verdict to 🔴 without `audited_deep` AST corroboration AND Prosecutor sign-off.
   Protects the false-accusation moat (a wrong 🔴 is the lethal failure).
7. **Import-isolation as a committed gate** (Winston + Amelia) — `apaa.*` must never transitively import
   FastAPI/uvicorn/starlette; a committed `tests/apaa/test_no_web_imports.py` (asserting absence from
   `sys.modules` after import) keeps the `minions[apaa]` external-install seam clean across a fresh clone.
   Confirmed feasible: `cost/budget_guardrails.py` (dataclass/stdlib) and `lifecycle/workspace_artifact_
   writer.py` (pathlib-only) are already FastAPI-free; FastAPI enters only via `api/` + `services/api_app.py`
   + `app_factory.py` + `api_server.py`.
8. **Append-only auditability** — hash-chained, additive-only artifact evolution across every decision
   (reuses ADR #18 ledger patterns).

### Precision Measurement & Trust Substrate

- **Precision must be architecturally MEASURABLE, not vibe-judged** (John + Murat). Every finding emits at
  birth: a stable `finding_id`, the coverage-envelope slice it came from, the rule/cartridge that fired, and
  the AST evidence span — feeding a REPLAY HARNESS that diffs findings against a labeled ground-truth set so
  precision falls out as a number. This recorded-finding schema + replay harness is **Tier-A plumbing**, not
  optional; it is what makes the ≥80%-precision gate empirical, not aspirational.
- **N=3 cartridges cannot SUPPORT an 80%-precision claim** (Murat). V1 guardrails, non-negotiable:
  (a) a HIDDEN HOLDOUT cartridge the detector authors never see, CI-gated; (b) CLEAN (no-planted-defect)
  CONTROL cartridges where ANY 🔴 is an instant CI fail (the false-accusation floor); (c) cartridges include
  false-NEGATIVE traps (citation-gaming defense), not just plant-and-find.
- **Ground truth needs CLEAN (true-negative) repos, not only defect-bearing ones** (R6, pre-mortem) — else
  precision has no false-positive denominator. Ties to the clean-control cartridges above.
- **Containment + honest-degradation are CI-BLOCKING property tests** (Murat) — randomized canary secrets
  asserted absent from {ledger, evidence, logs, traces, verdict envelope}; fault-injected AST/tool ports
  asserting failure → finding + degraded verdict, never crash/silent-pass.

### Resolved & Flagged Decisions (for the formal architecture steps)

- **FR7 (Python AST-grounding) — SPLIT, do not wholesale-reclassify** (R1, first-principles). First
  principles: a *truthful* "vacuous" assertion requires two AST facts — (a) the test body reaches the SUT,
  and (b) asserted values derive from the SUT's output (not mocks/constants); assertion-density alone is
  neither necessary nor sufficient. The signature demo line `🔴 tests *appear* vacuous` is advisory and
  CAN be produced by FR10 alone (Tier-A) — but a *credible, non-cry-wolf* 🔴 needs the AST facts.
  **Decision: carve a minimal "vacuous-path AST subset" (test-body reachability + assertion-target
  provenance, test files only) into Tier-A; leave general multi-construct AST-grounding Tier-B.** This
  keeps the PRD cut-order coherent (the PRD is internally consistent: a cut V1 is explicitly demo-grade,
  not externalization-ready) while honouring the panel's credibility concern. If FR7 is cut, the dogfood
  verdict must carry a hard `grade: demo-heuristic-only` flag and never be presented as externalization
  evidence (red-team).
- **Validation-set `N` must be resolved BEFORE precision-harness design** (John) — `N` + the labeling
  protocol define the harness ground-truth shape (schema, corpus, statistical floor for a defensible 80%).
  This is the one open input that gates an ARCHITECTURE choice, not merely scope. ⚠️ OPEN.
- 🆕 **Minions-dogfood scale risk** (R5, pre-mortem) — Minions is ~70 modules; V1 audit units are
  ≤40 files/15k LOC with a 20%-deep floor. The single proof artifact risks landing as
  `INSUFFICIENT_COVERAGE` ("not assessed"), leaving the strategic question ("does Minions have an audit
  agent?") unanswered. **Requires an explicit dogfood partition + budget-sizing plan as an architecture
  concern.** ⚠️ OPEN.

## Starter Template Evaluation

### Primary Technology Domain

**Python CLI / library audit engine inside an existing monorepo package** — brownfield-adjacent, not a
greenfield web/app bootstrap. The stack is INHERITED from the Minions repo, not selected from scratch
(the inverse of the typical `create-*-app` scenario this step targets).

### Starter Options Considered

| Option | Verdict |
|---|---|
| External Python scaffold (cookiecutter/copier, Typer/Click template) | ❌ Rejected — APAA must live at `minions_core/apaa/` and reuse Minions infra BY IMPORT; an external scaffold forks repo conventions, pulls a parallel toolchain, and breaks the import-isolation seam. |
| A fresh standalone repo | ❌ Rejected — contradicts the placement decision (dual-use UNDER minions_core) and the reuse-by-import architecture. |
| **Inherit the Minions repo as the foundation** | ✅ Selected — the "starter" is the existing repo conventions + the already-reserved `minions_core/apaa/` shell. |

### Selected "Starter": the Minions repo + reserved `minions_core/apaa/` shell

**Rationale:** the placement decision already committed APAA to live inside Minions and reuse its infra;
the repo's conventions ARE the starter. Adopting anything else fights the architecture.

**Initialization (NOT a generator command — already created/staged this session):**

```text
minions_core/apaa/__init__.py                          # reserved package shell (docstring only)
pyproject.toml [project.optional-dependencies].apaa     # minions[apaa] extra
# First implementation story bootstraps the THIN VERTICAL SLICE (ingest -> AST index -> vacuous-test rule -> verdict),
# NOT a horizontal scaffolding epic (per the pre-mortem / John guidance).
```

**Architectural decisions INHERITED from Minions (no choice needed):**
- Language & runtime: Python 3.11+ (`>=3.10` floor).
- Contracts: Pydantic v2 + JSON Schema, frozen additive-only (NFR-M2).
- Testing: pytest · pytest-asyncio (cartridges as parametrized tests under `tests/apaa/`).
- Modularity: ≤1200-line files, strict-modularity entrypoints (NFR-M1).
- Infra reuse-by-import: ADR #18 hash-chained ledger, budget guardrails, workspace-containment, `adapter_portability`.
- Config: 12-Factor env vars, secret-masking (NFR-S1).

**NEW external dependencies (the only genuine "starter" choices) — versions verified June 2026:**
- `tree-sitter==0.25.2` (Python bindings, Sep 2025) + `tree-sitter-python==0.25.0` (grammar) — AST/
  code-graph index. **The grammar version is pinned into the determinism cache key (R3).** Note the 0.25
  API loads grammars via the per-language package.
- `radon==4.1.0` — zero-token breadth metrics (NFR-C3).
- `jsonschema>=4` — additive-only schema validation.
- **CLI framework — DEFERRED to architecture decisions (step-04):** lean stdlib `argparse` (thin
  entrypoint, zero new dep) vs. Typer (ergonomics).

**Note:** the package shell + extra already exist, so "project init" is not a story — the first story is
the thin vertical signature-demo slice.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical (block implementation):** CLI/invocation contract + exit codes (A); AST/code-graph index +
graph-partitioning (B); fixed-enum ledger + frozen recording schema + pure-function verdict + memoization
cache-key closure + single canonical serializer (C); filesystem-as-contract `.apaa/` + containment reuse (F).
**Important (shape architecture):** vacuous-test detector (heuristic + Tier-A AST subset) + finding shape
(D); budget + LLM-dispatch-via-port reuse (E); CI cartridge/import-isolation/determinism gates (H).
**Deferred (post-V1):** multi-language AST, seam auditor, mutation-grade vacuous, consume Minions layers
(d)/(a)/(e), hosted runner + HTTP API/auth.

### A. Execution & Invocation
- **CLI framework:** stdlib **`argparse`** (thin entrypoint, zero new dep, keeps `cli.py` pure wiring —
  NFR-M1). Typer/Click rejected (dep + parallel toolchain).
- **Invocation contract:** `repo + commit + budget + materiality_bar → verdict artifact + exit code`
  (FR30); pure `AuditRequest → AuditVerdict`.
- **Exit-code wire contract:** `0`=RELEASE_READY · `2`=BLOCKED · `3`=INSUFFICIENT_COVERAGE · `1`=crash
  (mirrors Minions house style `0/1/2`, `3`=not-assessed). Machine-consumable CI gate (FR18).
- **Execution model:** sequential-canonical; parallel = pure byte-identical speedup (NFR-P1).

### B. Repository Intake & Indexing
- **AST/code-graph index FIRST** via `tree-sitter==0.25.2` + `tree-sitter-python==0.25.0`; structural
  search, not embeddings.
- **Graph-derived partitioning** (import/call graph, not directories); ≤40 files/15k LOC units, conservative
  budgets + `context_pressure` auto-downgrade.
- **Stack detection** via `cloc`/`radon==4.1.0` + tree-sitter; V1 deep = Python only, `claim_emitted` proxy
  elsewhere via a stack-agnostic `claim→validated?` interface (NFR-P2).

### C. Coverage Ledger, Recording Schema & Verdict (determinism core)
- **Fixed-enum Pydantic v2 ledger** (`audited_deep/_shallow/tool_scanned_only/inferred/skipped`); reserve
  `partition_id` (always `"root"` V1).
- **Recording schema = first-class frozen contract** — the verdict folds over recordings; freeze as hard as
  the verdict.
- **Pure-function verdict gate, 0 LLM tokens**, isolated module; **Prosecutor = distinct pure-consumer pass**
  (cannot call an LLM — FR15/FR19).
- **Content-addressed memoization; cache key = full recording-producing closure**: detector-set content-hash
  (NOT a human version string) + model-checkpoint-captured-from-API-response + tree-sitter-grammar/tool
  versions + budget/materiality + work-manifest scope. **Invalidate on detector-set change; a human-rejected
  finding busts its own key** (R2/R3). Cache-key derivation is a pure golden-tested function + CI canary.
- **Single `apaa/store/canonical.py` serializer** (`sort_keys=True, separators=(",",":"),
  ensure_ascii=False`, `\n`-terminated UTF-8); ratios stored as fixed-precision decimal — no floats (R4/NFR-P1).

### D. Defect Detectors
- **Vacuous-test:** heuristic (advisory `audited_shallow`, evidence-carrying) **+ Tier-A "vacuous-path AST
  subset"** (test→SUT reachability + assertion-target provenance) for a credible verdict-moving 🔴
  (FR10 + the FR7 split, R1). **Advisory-by-contract:** no verdict-moving 🔴 without AST corroboration AND
  Prosecutor sign-off.
- **Secret detection:** V1 regex + entropy; **redact-before-store as a producer property** (cite locations,
  never bytes); reuse Minions secret-masking patterns (FR11/NFR-S2).
- **Orphan/dead code:** graph-reachability (Tier-B, FR12).
- **Every finding** carries a stable `finding_id` + coverage-envelope slice + rule/cartridge id + AST span →
  feeds the precision replay harness (Tier-A plumbing).

### E. Cost Governance & LLM Dispatch
- **Budget:** reuse `minions_core.cost.budget_guardrails` **by import** (verified FastAPI-free); halt→skip→
  downgrade→report (FR22/NFR-C2).
- **LLM dispatch — reuse the orchestrator BY IMPORT, behind ONE narrow APAA-owned port** (DIP, and required
  by NFR-D2 injectability — so NOT a speculative abstraction):
  - `apaa/audit/ports.py` → `LLMDispatchPort(Protocol)` with a single `dispatch(req) -> LLMRecording`.
  - `apaa/audit/minions_llm_adapter.py` → thin adapter holding an `LLMProviderOrchestrator`
    (`minions_core.providers.orchestrator`, verified FastAPI-free), mapping `LLMRequest`/`LLMResponse`
    (`minions_core.providers.base`) ↔ APAA's frozen `LLMRecording`, **capturing the model checkpoint from
    the API response** (R3).
  - `apaa/audit/deep_audit.py` depends on `LLMDispatchPort`, **never the orchestrator directly**; tests inject
    a `FakeDispatch` → 0 LLM tokens.
  - **No fork (§3.3):** inherits the orchestrator's fallback chain + circuit breaker + cost attribution, which
    feeds APAA cost governance + honest degradation for free.
  - **Tiered routing** (cheap triage → premium deep-read) + **prompt caching** for multi-perspective passes
    over a cached partition (research: 59–70% savings; the cache doubles as the determinism mechanism).
  - **Packaging:** `minions[apaa]` extra gains `httpx` (providers' only third-party dep).

### F. Persistence & State
- **NO database** — filesystem-as-contract `.apaa/{state,assignments,findings,decisions}/`; resumable +
  portable (FR31).
- **Containment:** reuse `lifecycle/workspace_artifact_writer` with injected root `.apaa/` (`is_relative_to`,
  not prefix); thin-wrap if root injection is unsupported (NFR-S5).
- **Memoization store:** local content-addressed on-disk cache (the V1 reproducibility floor; shared G4
  cross-run cache is V4, never the sole guarantee).
- **Audit trail:** append-only, ADR #18 hash-chained envelope patterns by import.

### G. Security & Governance
- **AuthN/Z: none / N-A** — headless CLI, no HTTP service in V1 (auth/rate-limit/SDK = V4).
- **Secret containment:** CI-blocking property tests (`tests/security/` pattern, randomized canaries) — no
  source/secret bytes in ledger/evidence/logs/traces/envelope (NFR-S1).
- **HITL gate:** pattern-matched escalation, default-STOP, time-boxed park-at-STOP (FR23); append-only
  decision record (FR24, Tier-B).

### H. Self-Audit & CI (trust substrate)
- **Defect cartridges** under `tests/apaa/cartridges/` (vacuous, secret, orphan) **+ hidden holdout + clean
  true-negative controls** (any 🔴 on a clean control = CI fail) — FR20.
- **Import-isolation gate** `tests/apaa/test_no_web_imports.py` (`apaa.* ⊬ fastapi/uvicorn/starlette`) —
  committed/durable. (Verified today: all reuse targets, incl. `providers`, are FastAPI-free.)
- **Determinism golden-tests** — cache-key derivation + envelope canonicalization.

### I. Packaging & Deployment
- **`minions[apaa]` optional extra**: `["pydantic>=2","jsonschema","radon","httpx","tree-sitter",
  "tree-sitter-python"]`; **`apaa` console script** (wired by the CLI story). No container/hosting in V1
  (CLI/library); runs on Claude Code (parallel) + Cline (sequential).

### Driver Namespace
- **`APAA-FR-*` / `APAA-NFR-*`**, mapped 1:1 onto the PRD FR1–33 / NFR clusters; the full component↔driver
  table is built in the components step.

### Decision Impact Analysis

**Implementation sequence (the thin vertical slice first — pre-mortem/John):** envelope+canonical serializer
+ fixed-enum ledger (C-core) → AST index + a single vacuous-path rule (B + D) → pure-function verdict +
exit code (C + A) → 🔴 on the Minions vacuous-test cartridge (signature demo) → then breadth-tool runner,
memoization, Prosecutor, remaining detectors, cost/LLM port, evidence bundle.

**Cross-component dependencies:** the **recording schema** is upstream of verdict, memoization, AND the
precision harness (freeze first). The **canonical serializer** underpins envelope determinism + NFR-P1 +
the memo cache (single source). The **`LLMDispatchPort`** is the only seam between the pure core and the
non-deterministic LLM substrate.

### Still OPEN (delivery-detail, not architecture-blocking)
- Validation-set `N` (gates precision-harness ground-truth shape — resolve before harness build).
- Minions-dogfood partition + budget-sizing plan (so the proof run doesn't land `INSUFFICIENT_COVERAGE`).
- Budget-ceiling `$X` default.

## Implementation Patterns & Consistency Rules

**Critical conflict points identified: 12** — areas where two AI agents could implement compatibly-looking
but divergent code that breaks determinism, containment, or the frozen contracts.

### Pure/Impure Separation (master rule)
- **Pure modules take NO I/O, NO clock, NO LLM:** `ledger`, `verdict`, `canonical`, `cache_key`,
  `prosecutor`, detector *scorers*. **Impure shell at the edges only:** `store/*` writer,
  `minions_llm_adapter`, tool/subprocess runner, `cli`.
- ✅ verdict gate imports only ledger models · ❌ verdict gate reads a file or calls `dispatch()`.

### Determinism Patterns (NFR-P1/D1 — non-negotiable)
- **One serializer.** All `.apaa/` JSON goes through `apaa/store/canonical.py`
  (`json.dumps(sort_keys=True, separators=(",",":"), ensure_ascii=False)` + `\n`, UTF-8). **Never call
  `json.dumps` directly elsewhere.**
- **Forbidden in any `.apaa/` write path:** wall-clock (`datetime.now`/`time.time`), `uuid4`,
  `os.getpid()`, `random`, dict/`set`-iteration-order reliance, **float scores** (use fixed-precision
  `Decimal`/exact fractions).
- **One cache-key function** (`apaa/cache/key.py`); never compose a memo key ad hoc.
- ✅ `canonical.dumps(payload)` · ❌ `json.dumps(payload, indent=2)`.

### Naming & Structure Patterns
- **Modules:** `snake_case.py`, ≤1200 lines (NFR-M1); sub-packages
  `apaa/{intake,index,ledger,detectors,verdict,store,cache,audit,cli}/`.
- **`.apaa/` tree (fixed):** `state/ · assignments/ · findings/ · decisions/`; filenames from
  content-sha256 or stable assignment-id, never arrival order.
- **Tests:** `tests/apaa/...`; cartridges in `tests/apaa/cartridges/<id>/`; test IDs
  `TC-<AREA>-<SEQ>-<SUBSEQ>`; driver cites `APAA-FR-*`/`APAA-NFR-*` in module docstrings.
- **JSON fields:** `snake_case` (Minions/Pydantic v2 convention).

### Contract / Format Patterns
- **Coverage-ledger enum is closed:** `audited_deep · audited_shallow · tool_scanned_only · inferred ·
  skipped`. Never invent a new depth state — evolution is additive-only (`schema_version` bump, new
  optional fields only).
- **Every finding MUST carry:** `finding_id` (stable) · ≥1 verifiable locator (file + line-range/AST
  span) · `rule_id`/`cartridge_id` · `advisory: bool` · coverage-envelope slice. A finding without a
  locator is rejected, not emitted (FR13).
- **Verdict vocabulary (canonical):** `RELEASE_READY` / `NOT_READY_FOR_RELEASE` (`BLOCKED`=demo
  shorthand) / `INSUFFICIENT_COVERAGE`; exit codes `0/2/3/1`. Downstream artifacts use this vocabulary
  verbatim.
- **Envelope:** content-hash over payload-only (exclude `run_id`/`created_at`); `prev_hash` chaining;
  one `EnvelopeWriter`.

### Security / Containment Patterns
- **Redaction is producer-side:** findings cite locations, never source bytes; secret values stored only
  as `contained_secret: true` + redacted form. Never put source/secret/prompt/response bytes in ledger,
  evidence, logs, or traces.
- **All FS writes via the containment helper** (`is_relative_to`, never `str.startswith`); a containment
  breach raises a typed error before any write.

### Reuse / Import Patterns
- **Import leaf modules** (`from minions_core.providers.orchestrator import LLMProviderOrchestrator`);
  never import `minions_core.api.*` / `services.api_app` / `app_factory` / `api_server`.
- **Depend on the port, not the impl:** `deep_audit` depends on `LLMDispatchPort`; only
  `minions_llm_adapter` imports the orchestrator.

### Error / Degradation Patterns
- **Failure → typed finding, never an uncaught raise** out of the pipeline (NFR-R1). Tool/parse failure
  becomes a `tool_failure`/`parse_failure` finding + coverage downgrade; the run still produces a verdict
  (degraded → `INSUFFICIENT_COVERAGE`).
- **Typed exceptions** at the impure shell (reuse `WorkspaceContainmentError`); no bare `except: pass`;
  no `print()` in library code (structured, secret-safe logging).

### Enforcement
**All APAA agents MUST:** route JSON through `canonical`; emit findings with a locator or not at all; keep
pure modules I/O-free; import only FastAPI-free leaf modules. **Enforced by:** the import-isolation gate,
determinism golden-tests (serializer + cache-key), the secret-containment property suite, and file-size CI
— committed under `tests/apaa/` + the Minions CI model.

## Project Structure & Boundaries

### Package tree (`minions_core/apaa/`)

```
minions_core/apaa/
├── __init__.py                  # reserved shell (exists)
├── cli.py                       # FR30/FR18 — thin argparse entrypoint → AuditRequest → exit code
├── pipeline.py                  # orchestrates AuditRequest → AuditVerdict (sequential-canonical, NFR-P1)
├── models.py                    # Pydantic v2 frozen contracts (AuditRequest, AuditVerdict, Finding, LLMRecording)
├── intake/
│   ├── repo_loader.py           # FR1 — load repo @ pinned commit
│   └── stack_detect.py          # FR2 — stack/toolchain detection (cloc/radon/tree-sitter)
├── index/
│   ├── ast_index.py             # FR7-subset/B — tree-sitter code-graph index (structural, not embeddings)
│   └── partitioner.py           # FR3/FR4 — graph-derived partitions; context_pressure auto-downgrade
├── ledger/
│   ├── coverage_ledger.py       # FR5/FR6/FR8/FR9 — fixed-enum ledger (PURE)
│   └── recording.py             # frozen recording schema (PURE, first-class contract)
├── detectors/
│   ├── base.py                  # detector Protocol + Finding builder (locator-required, FR13)
│   ├── vacuous_test.py          # FR10 + FR7-subset — heuristic (advisory) + AST corroboration
│   ├── secret_scan.py           # FR11 — regex/entropy + producer-side redaction
│   ├── orphan_code.py           # FR12 [Tier-B] — graph reachability
│   └── tool_runner.py           # NFR-C3 — zero-token breadth; failure→finding (FR14/NFR-R1)
├── verdict/
│   ├── verdict_gate.py          # FR15/FR16/FR33 — PURE function, 0 LLM tokens
│   ├── prosecutor.py            # FR19 [Tier-B] — PURE recording-consumer; cut-edge pass
│   └── negative_assurance.py    # FR17/NFR-A3 — scope/materiality/disclaimer/point-in-time
├── store/
│   ├── canonical.py             # NFR-P1 — THE single serializer (no other json.dumps)
│   ├── envelope.py              # FR25/NFR-A1 — EnvelopeWriter (payload-only hash, prev_hash)
│   ├── paths.py                 # .apaa/ path resolver via containment
│   ├── writer.py                # IMPURE — reuse lifecycle/workspace_artifact_writer
│   └── reader.py                # PURE deserialize/validate; resumability (FR31)
├── cache/
│   ├── key.py                   # R3 — single cache-key derivation (PURE) + CI canary
│   └── memo_store.py            # NFR-D1 — content-addressed on-disk memo + invalidation
├── audit/
│   ├── ports.py                 # LLMDispatchPort (Protocol) — the only LLM seam
│   ├── minions_llm_adapter.py   # decision E — reuse LLMProviderOrchestrator → LLMRecording
│   └── deep_audit.py            # depends on LLMDispatchPort; AST-grounded audited_deep claims
├── cost/
│   └── budget_governor.py       # FR21/FR22 — wraps cost/budget_guardrails; halt→skip→downgrade
├── governance/
│   ├── escalation.py            # FR23 — pattern-matched STOP/PROCEED, default-STOP, time-boxed
│   └── decision_record.py       # FR24 [Tier-B] — append-only
├── evidence/
│   └── bundle.py                # FR29 — evidence bundle export (ledger, scope, findings, verdict)
└── precision/
    └── replay_harness.py        # Tier-A plumbing — finding_id↔ground-truth diff → precision number
```

*(Every file ≤1200 lines (NFR-M1); `__init__.py` per sub-package omitted for brevity. Tier-B / thin-in-V1
modules are marked. Sub-package count is intentional: it honours the pure/impure split and keeps the
determinism core isolated and independently testable.)*

### Runtime artifact tree (`.apaa/` — in the AUDITED repo, not the package)

```
<audited-repo>/.apaa/
├── state/         # run state + coverage-ledger snapshots (resumable, FR31)
├── assignments/   # work_manifests = auditor permission boundaries (NFR-S4)
├── findings/      # per-partition finding recordings (canonical-serialized)
├── decisions/     # human STOP/PROCEED decision records (FR24)
└── cache/         # content-addressed memoization store (NFR-D1)
```

### Test tree (`tests/apaa/` + `tests/security/`)

```
tests/apaa/
├── test_no_web_imports.py          # import-isolation gate (apaa.* ⊬ FastAPI) — committed/durable
├── test_canonical_determinism.py   # golden serializer + envelope canonicalization
├── test_cache_key.py               # cache-key derivation golden + CI canary on input changes
├── test_verdict_gate.py            # PURE verdict over synthetic ledgers (0 tokens, NFR-D2)
├── test_containment.py             # FS containment property tests
├── test_cartridge_selfaudit.py     # parametrized cartridge runner (FR20)
└── cartridges/
    ├── vacuous_test/  hardcoded_secret/  orphan_function/   # #1–3 (CI-asserted)
    ├── _holdout/                                            # hidden holdout (authors never see)
    └── _clean_control/                                      # true-negative; any 🔴 = CI fail
tests/security/
└── test_apaa_secret_containment.py # randomized-canary property test (NFR-S1, CI-blocking)
```

### Architectural Boundaries

- **HTTP/A2A boundary:** APAA is DOWNSTREAM of it — a CLI/library, takes no A2A token, registers no
  FastAPI route (ADR #20 boundary spirit). No web surface in V1.
- **Import boundary (enforced):** `apaa.* ⊬ minions_core.api.* / services.api_app / app_factory /
  api_server`.
- **Pure/impure boundary:** pure core (`ledger`, `verdict`, `canonical`, `cache/key`, `prosecutor`,
  detector scorers) ⟂ impure shell (`store/writer`, `audit/minions_llm_adapter`, `detectors/tool_runner`,
  `cli`).
- **LLM boundary:** `audit/ports.py::LLMDispatchPort` — the single seam to the non-deterministic substrate;
  everything downstream is pure folds over recordings.
- **Filesystem boundary:** all writes via the containment helper into `.apaa/`; nothing escapes the
  audited-repo root.

### FR-cluster → location mapping

| FR cluster | Location |
|---|---|
| Intake & Partitioning (FR1–4) | `intake/`, `index/` |
| Coverage Ledger (FR5–9) | `ledger/` |
| Defect Detection (FR10–14) | `detectors/` |
| Verdict (FR15–18, FR33) | `verdict/`, `cli.py` |
| Self-Audit (FR19–20) | `verdict/prosecutor.py`, `tests/apaa/cartridges/` |
| Cost Governance (FR21–22) | `cost/budget_governor.py` |
| Governance/Integrity (FR23–29) | `governance/`, `store/envelope.py`, `cache/`, `evidence/` |
| Invocation & Resumability (FR30–32) | `cli.py`, `pipeline.py`, `store/reader.py` |

## Architecture Validation Results

### Coherence Validation ✅
- **Decision compatibility:** Python 3.11+ · Pydantic v2 · tree-sitter 0.25.x · radon 4.1 · httpx — mutually
  compatible and FastAPI-free (verified 2026-06-18). No contradictory decisions.
- **Pattern consistency:** the pure/impure split + single-serializer + cache-key rules directly enforce the
  determinism decisions (C); reuse-by-import patterns enforce the import boundary (E/H).
- **Structure alignment:** the tree isolates the pure determinism core, places the LLM seam behind one port,
  and routes all writes through containment — the structure IS the boundary set.

### Requirements Coverage Validation ✅
- **All 33 FRs** map to a concrete module (FR-cluster→location table). No FR is unsupported.
- **All 21 NFRs** supported: D1–3 (`cache/`, `canonical`, pure `verdict`), S1–5 (containment + redaction +
  `tests/security/`), C1–3 (`budget_governor`, `tool_runner`), R1–2 (failure→finding, `store/reader` resume),
  P1–2 (`canonical`, stack-agnostic `claim→validated?`), A1–3 (`envelope`, `negative_assurance`), SC1
  (`partitioner`), M1–2 (file-size CI, Pydantic v2).

### Implementation Readiness Validation ✅
- Decisions complete with verified versions; patterns enforceable (committed gates: import-isolation,
  determinism golden-tests, secret-containment property suite, file-size); structure specific (every file
  named, boundaries explicit).

### Gap Analysis
- **Critical gaps:** none — the architecture does not block implementation.
- **Important gaps (pre-epic delivery inputs, resolve in epic planning):** validation-set `N` (gates the
  precision-harness ground-truth shape); Minions-dogfood partition + budget-sizing plan (so the proof run
  doesn't land `INSUFFICIENT_COVERAGE`); budget-ceiling `$X` default.
- **Nice-to-have:** a worked envelope/cache-key example doc; a `cloc`/SAST tool-availability probe.

### Architecture Completeness Checklist
**Requirements Analysis** — [x] context analyzed · [x] scale/complexity assessed · [x] constraints
identified · [x] cross-cutting concerns mapped
**Architectural Decisions** — [x] critical decisions w/ versions · [x] tech stack specified · [x] integration
patterns defined · [x] performance addressed (budget, context_pressure)
**Implementation Patterns** — [x] naming · [x] structure · [x] communication (filesystem-as-contract + port)
· [x] process (error/degradation)
**Project Structure** — [x] directory structure · [x] component boundaries · [x] integration points · [x]
requirements→structure mapping

**All 16 items ✅.**

### Architecture Readiness Assessment
- **Overall Status:** ✅ **READY FOR IMPLEMENTATION** (all 16 checklist items `[x]`; no Critical Gaps — the
  3 open items are delivery inputs for epic planning, not architecture blockers).
- **Confidence:** High.
- **Key strengths:** determinism quarantined to one seam; LLM behind a single injectable port; reuse-by-import
  verified FastAPI-free; every FR/NFR traced to a module; the false-accusation moat protected by
  advisory-by-contract + holdout/clean cartridges.
- **Future enhancement:** multi-language AST (V2), seam auditor (V2), mutation-grade vacuous (V2), consume
  Minions layers (d)/(a)/(e), hosted runner + HTTP API (V4).

### Implementation Handoff
- **AI agents must:** follow these decisions exactly; route JSON through `canonical`; keep pure modules
  I/O-free; emit findings with a locator or not at all; import only FastAPI-free leaf modules.
- **First implementation priority:** the THIN VERTICAL signature-demo slice — envelope + canonical serializer
  + fixed-enum ledger → AST index + one vacuous-path rule → pure verdict + exit code → 🔴 on the Minions
  vacuous-test cartridge. NOT a horizontal determinism epic.
