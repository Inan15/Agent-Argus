---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-06-18'
readiness: 'READY FOR IMPLEMENTATION'
inputDocuments:
  - _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md
  - _bmad-output/design-artifacts/ArgusAgent/product-brief-apaa.md
  - _bmad-output/design-artifacts/ArgusAgent/product-brief-apaa-distillate.md
  - _bmad-output/design-artifacts/ArgusAgent/research-domain-2026-06-17.md
  - _bmad-output/design-artifacts/ArgusAgent/research-market-2026-06-17.md
  - _bmad-output/design-artifacts/ArgusAgent/research-technical-2026-06-17.md
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

**Functional Requirements (37):** Eight capability clusters — Repository Intake & Partitioning (FR1–4),
Coverage Ledger & Grounded Evidence (FR5–9, **FR36, FR37**), Defect Detection (FR10–14),
Release-Readiness Verdict (FR15–18, FR33, **FR34**), Self-Audit & Trust (FR19–20), Cost Governance
(FR21–22), Governance/Escalation/Evidence Integrity (FR23–29), Invocation & Resumability (FR30–32,
**FR35**). Architecturally they form one **deterministic dataflow** whose terminal stage (the verdict) is
a pure function of a fixed-enum coverage ledger.
Tier-B FRs (FR7, FR12, FR19, FR24, FR26, **FR36**) are the validation-grade layer over a demo-grade Tier-A
spine (see the FR7 split decision below).
*(Count corrected 2026-08-10 — read "(33)" and omitted FR34–FR37 until now. The 2026-08-10b amendment made
10 substitutions in this document, including the §Component↔Driver line at L467 which was already updated
to "PRD FR1–37", but did not reach this overview. See implementation-readiness-report-2026-08-10.md, Step 4.)*

**Non-Functional Requirements (23):** Determinism/Reproducibility (NFR-D1–3, the keystone — stable-not-
bit-identical via content-addressed memoization), Security/Containment (NFR-S1–5, **NFR-S6 — no egress on
the default path**), Cost Efficiency (NFR-C1–3), Reliability/Honest-Degradation (NFR-R1–2), Portability
(NFR-P1–2, sequential byte-identical to parallel, **NFR-P3 — the default public install grounds the
languages the tool claims**), Auditability (NFR-A1–3, hash-chained additive-only envelope), Scale Envelope
(NFR-SC1, ≤40 files/15k LOC/unit), Maintainability (NFR-M1–2).
*(Count corrected 2026-08-10 — read "(21)" and omitted NFR-S6/NFR-P3, both added 2026-08-10b.)*

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
  Key inputs: content-hash + model checkpoint + prompt-template version + tool versions (~~tree-sitter
  grammar~~ **per-grammar tree-sitter provenance**, radon) + budget/materiality config + work-manifest
  scope + **a content-hash of the enabled
  detector SET (code+config), NOT a human-written APAA version string** (R3). The model checkpoint is
  captured from each **API response** (not config); a mid-run **checkpoint drift → `checkpoint_drift`
  finding → abort/re-audit** (R3). The key DERIVATION is itself a pure function to golden-test, with a CI
  canary that fails when key inputs change without a version bump.

  🔧 **R3 DESIGN CHANGE, not a defect fix — 2026-08-10, Story 10.2 (`DF-AUD-APAA-D`).** R3 was
  *designed* for one grammar, and the singular wording above was faithful to that design. It stopped
  being faithful to the product when the index began parsing ten languages: measured on this tree, the
  key folded `tree-sitter-python` 0.25.0 while `tree-sitter-rust` 0.24.2, `tree-sitter-java` 0.23.5 and
  `tree-sitter-ruby` 0.23.1 had each parsed a file, so a Go, Rust, Java, C, C++ or Ruby grammar upgrade
  **did not move the key** — the silent-cache-staleness class `DF-5-1-A` files for
  `prompt_template_version`. **The design is therefore changed, deliberately and with the words said out
  loud: provenance is PER-GRAMMAR, and the key folds only the grammars that PARTICIPATED in the audited
  build.** Both halves are load-bearing and both are pinned by test
  (`TC-ArgusAgent-CACHE-001-77`/`-78`): folding a grammar that did not parse would key the cache on the
  HOST's installed packages rather than on the audit, breaking NFR-P1 across environments — the inverse
  defect, and the easier one to ship by accident. `CACHE_KEY_SCHEMA_VERSION` is bumped `"2"` → `"3"`;
  see §C for why that is free at this commit and only at this commit.
- **Stack:** Python 3.11+ (Minions baseline), Pydantic v2 + JSON Schema frozen contracts; ~~AST = Python in
  V1 (`claim_emitted` proxy elsewhere)~~ **AST grounding is delivered in V1 for every language enumerated
  in `argus/shared/source_languages.py` (the source of truth); the `claim_emitted` proxy carries anything
  outside that set or any file whose grammar is absent**, via a stack-agnostic `claim → validated?`
  interface. *(Amended 2026-08-10, Story 10.2 / `DF-AUD-APAA-D`; the capability was delivered by
  `sprint-change-proposal-2026-07-28.md` with no story and no amendment. This site was missed by all three
  prior enumerations of the drift — it states the scope with no `V2` marker anywhere in it, which is why a
  keyword sweep for "V2" never found it and why the closure guard, not a list, is the remedy.)*
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
  not externalization-ready) while honouring the panel's credibility concern. 
- **Grade flag — corrected trigger and scope.** *(Amended 2026-08-10b.)* The original condition read
  *"if FR7 is cut, the dogfood verdict must carry a hard `grade: demo-heuristic-only` flag and never be
  presented as externalization evidence (red-team)."* **FR7 was not cut** — Story 6.2 delivered its
  validator, which is live. The flag is nonetheless correct, for a different reason now stated: it describes
  the **configuration of the pipeline that produced a given run**, not a permanent property of the product.

  **Two distinct disclosures, deliberately not merged:**

  | | **Run grade** (`grade: demo-heuristic-only`) | **Instrument status** (FR34) |
  |---|---|---|
  | Describes | how *this run* was configured | how the *tool's findings* have been validated |
  | True when | the deep-audit seam was not engaged for this run | the ≥80% precision gate is uncleared |
  | Varies | **per run** — an FR36 `--deep` run is not heuristic-only and must not be labelled so | **per tool version** |
  | Removed by | engaging the deep pass | Epic 13 clearing the gate — nothing else |

  Merging them would produce two wrong outcomes: a `--deep` run mislabelled heuristic-only, and a
  disclosure that appears to lift when a user enables a flag. **Enabling deep audit changes the run's
  grade. It does not validate the instrument.**

  **Unchanged and re-affirmed:** the **dogfood proof artifact is never externalization evidence**,
  regardless of grade or gate state (red-team). Story 8.5's re-derivation made it a self-audit, which
  weakens it further — see PRD §Validation Approach.

  **FR34 extends the existing guard, never a second mechanism** (AR7 / §3.3): the two-sided
  `DOGFOOD_EXTERNALIZATION_GUARD` (presence AND over-claim-phrase absence) is widened to the
  user-facing surface set, enumerated so an unenumerated surface fails CI.
- **Validation-set `N` must be resolved BEFORE precision-harness design** (John) — `N` + the labeling
  protocol define the harness ground-truth shape (schema, corpus, statistical floor for a defensible 80%).
  This is the one open input that gates an ARCHITECTURE choice, not merely scope.
  ~~✅ **CLOSED 2026-08-10b — assigned, not answered.** It was never resolved by decision: the harness
  was built (Story 6.6) and `precision-validation-protocol.md` fixed `N` **implicitly** as `N ≥ 5`
  **labeled cartridges**, while PRD L161 specifies `N ≈ 5–10` **real repositories** — two corpora,
  never reconciled. **Story 13.1 owns the adjudication** and must amend whichever document loses.~~
  *(This marker and the §Still OPEN entry are the SAME item at two sites; the 2026-08-10b proposal
  amended only the latter — recorded here because a two-site claim fixed at one site is the exact
  defect Story 10.2 exists to close.)*

  ✅ **RESOLVED BY DECISION 2026-08-16 (Story 13.1 / DN-1) — the PRD governs.** *(VALIDATION-SET
  RESOLUTION — the identical paragraph is recorded at §Still OPEN and in §Gap Analysis, so no site
  survives saying something else.)* The validation set is **`N ≈ 5–10` real repositories** with a
  floor of **`N ≥ 5`**, per PRD §Validation Approach; `precision-validation-protocol.md` §5's
  conflicting **`N ≥ 5` labeled planted-defect cartridges** floor is **struck**. **Reason:** the two
  documents specified different *quantities*, not two opinions about one — the cartridges measure
  **recall** against defects the team planted and answered, while the gate must measure **precision**
  on code nobody planted. A gate clearable by the team's own plants is not an externalization gate.
  The cartridges are **re-labelled, not demoted**: they remain the FR20 recall instrument, CI-asserted
  and unchanged. **Membership is a closed, machine-readable manifest** —
  `tests/corpus/_manifest.py::VALIDATION_CORPUS` — carrying a pinned commit sha, licence, language
  and provenance per member, with exclusions recorded in the manifest itself and the floor **derived**
  from the same `VALIDATION_SET_FLOOR_N = 5` rather than forked. **This closes the input by DECISION;
  it does not clear the gate.** Measured at resolution: **`N = 0` eligible members**, no adjudication
  run, `protocol_cleared` never `True`. **Updated the same day, 2026-08-16: the operator ratified five
  members under AC3b, so `N = 5` and the floor is MET** — the resolution-time zero is kept struck-not-
  erased because it is the state the DECISION was taken in. Reaching the floor is one of four §5
  conditions; the other three (the adjudication run, the ≥80% figure, zero clean-repo blocking FPs) are
  unmet, so the gate remains **PROVISIONAL**. Enforced by **`tests/test_validation_set_decision.py`**
  (`TC-ArgusAgent-DOCS-001-73`..`-76`).
- 🆕 **Minions-dogfood scale risk** (R5, pre-mortem) — Minions is ~70 modules; V1 audit units are
  ≤40 files/15k LOC with a 20%-deep floor. The single proof artifact risks landing as
  `INSUFFICIENT_COVERAGE` ("not assessed"), leaving the strategic question ("does Minions have an audit
  agent?") unanswered. **Requires an explicit dogfood partition + budget-sizing plan as an architecture
  concern.**
  ✅ **CLOSED 2026-08-10b — the risk materialised and was handled, which is the honest outcome.**
  Story 7.1 delivered the partition + budget-sizing plan
  ([minions-dogfood-partition-plan.md](minions-dogfood-partition-plan.md),
  [minions-dogfood-budget-plan.md](minions-dogfood-budget-plan.md)); Story 7.2 executed the run.
  The proof **did** land as a non-vouching outcome for Minions (row 4 — zero findings, critical clause
  unmet), exactly as R5 predicted. The strategic question was answered by the run existing, not by the
  verdict being green. ⚠️ Note the later regression, recorded so this closure is not read as stronger
  than it is: Story 8.5 re-derived the dogfood as a **self-audit of `argus/`**, and the independent
  Minions run *"can never be re-derived in this repository"* — see PRD §Validation Approach and
  Story 13.1.

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
  code-graph index. ~~**The grammar version is pinned into the determinism cache key (R3).**~~ **Every
  grammar that PARSED is pinned into the determinism cache key, at its own package version (R3) —
  per-grammar, not one scalar.** *(Amended 2026-08-10, Story 10.2 / `DF-AUD-APAA-D` — a DESIGN CHANGE,
  not a defect fix; see the R3 note in §Cache key above.)* Note the 0.25 API loads grammars via the
  per-language package — and that **not every per-language package exports a bare `language()`**:
  `tree_sitter_typescript` exports `language_typescript`/`language_tsx` and `tree_sitter_php` exports
  `language_php`/`language_php_only`, so grammar loading resolves a per-language entry point
  (`argus/index/ast_index.py::_ENTRY_POINT_BY_LANGUAGE`, with a suffix-level override for `.tsx`).
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
**Deferred (post-V1):** ~~multi-language AST,~~ seam auditor, mutation-grade vacuous, consume Minions layers
(d)/(a)/(e), hosted runner + HTTP API/auth. *(Amended 2026-08-10, Story 10.2 / `DF-AUD-APAA-D`:
multi-language AST grounding is **delivered in V1** — `argus/shared/source_languages.py` is the source of
truth — and is struck from this list rather than deleted, per §3.4. Every other item is untouched and
remains deferred. Delivered by `sprint-change-proposal-2026-07-28.md`.)*

### A. Execution & Invocation
- **CLI framework:** stdlib **`argparse`** (thin entrypoint, zero new dep, keeps `cli.py` pure wiring —
  NFR-M1). Typer/Click rejected (dep + parallel toolchain).
- **Invocation contract:** ~~`repo + commit + budget + materiality_bar → verdict artifact + exit code`
  (FR30); pure `AuditRequest → AuditVerdict`.~~
  **`accepted argv → verdict artifact + exit code` (FR30); pure `AuditRequest → AuditVerdict`. The
  ACCEPTED SURFACE IS `argus/cli.py::build_parser` — that function is the source of truth and this
  document deliberately does not restate it as a list.** The contract commits to these *categories*,
  each of which must remain expressible: the determinism **pin** (`--commit`) and its enforcement
  (`--strict`, the release-gate refusal); the cost **ceiling** (`--budget`); the **materiality bar**;
  **operator designation** of the critical set (`--critical-subsystem` / `--exclude-critical`, FR4);
  **pass and report selection** (`--passes` / `--skip-pass` / `--reports` / `--report-dir`);
  **security-finding suppression** (`--ignore-path` / `--ignore-pattern`, bounded by §G's suppression
  threat model); and **assessment scope** (`--coverage-scope`). *(Amended 2026-08-10, Story 10.3 /
  `DF-AUD-APAA-E`: the original four-parameter wording described what the tool accepted in Story 1.7
  and six flags had since entered the parser specified nowhere. Struck rather than deleted, §3.4. A
  hand-typed flag list is deliberately refused here — that is the AI-E9-7 drift class, and the
  `source_languages.py` precedent FR7 set on 2026-08-10 applies. Equality between this contract and
  the parser is enforced by `tests/test_invocation_contract.py`; see §Enforcement.)*
- **Exit-code wire contract:** `0`=RELEASE_READY · `2`=BLOCKED · `3`=INSUFFICIENT_COVERAGE · `1`=crash
  (mirrors Minions house style `0/1/2`, `3`=not-assessed). Machine-consumable CI gate (FR18).
  *(Amended 2026-08-15 by Story 12.8 / AC8 — no code added, one meaning made explicit. `2` means, and
  can only mean, THE AUDIT RAN AND FOUND AT LEAST ONE VERDICT-BLOCKING FINDING. Until this story every
  argparse USAGE error also exited `2`, and `action.yml:129` publishes `2` as
  `verdict=NOT_READY_FOR_RELEASE assessed=true` — so a mistyped flag published a fabricated assessment
  of a repository for a run that never happened. A parser rejection now returns the reserved `1`, which
  the map already renders `AUDIT_FAILED` / `assessed=false`; `--help` still exits `0`. The mapping lives
  in `cli.main`, never in `build_parser`, so `build_parser().parse_args` stays byte-identical for every
  guard that drives it and for the second invocation surface, which already ruled a parse rejection is
  not a verdict.)*
- **Execution model:** sequential-canonical; parallel = pure byte-identical speedup (NFR-P1).
- **Entry points — two, converging on one core.** *(Added 2026-08-10b, FR35.)*

  | Surface | Transport | Ships as |
  |---|---|---|
  | **CLI** (canonical) | process argv + exit code | console scripts `argus` / `argus-agent` / `repo-audit` |
  <!-- Story 12.8 / FR37, 2026-08-15: the CLI row is now COMPLETE as an operator surface, which is the
       half that was outstanding rather than the transport. It explains its own failures — every typed
       error names a cause AND an act that changes it, an internal Argus defect is distinguishable on
       stderr from a degradation of the caller's repository, an unknown token on a closed vocabulary is
       refused instead of silently disabling the passes it names, `--help` states every argument's live
       default, and a parser rejection returns the reserved no-verdict code instead of publishing one.
       `docs/first-run.md` orients a first run and is deliberately NOT where any answer lives (FR37). -->
  | **MCP server** | **stdio only** | an entry point in the same distribution |
  | *Assistant command assets* | *(not an entry point — configuration data)* | packaged files placed in the host's config |

  ✅ **The third row became a delivery on 2026-08-15 (Story 12.7 / FR35, second half).** The assets ship in
  the wheel and the sdist as `argus/assets/commands/*.md`, and *"placed in the host's config"* is now one
  documented, packaged step: the **second sub-command** `argus install-commands` — not a third entry point,
  which is why the table's row count is unchanged and why this is recorded here rather than by adding a row.
  The reasoning is DN-1's: the step's transport is argv, identical to the CLI's, so a separate console alias
  would be a fork of an entry point rather than an extension of one (AR7 / §3.3), whereas 12.6's second
  alias was justified by a genuinely different transport. `argus/commands/installer.py` splits a PURE fold
  (assets × hosts × destination → resolved `(path, bytes)` writes) from a THIN impure write, and it is the
  only place in this product that writes outside the audited repository at all — so constraint 3 below
  ("no new authority") is joined by a containment rule of the same kind as NFR-S4/NFR-S5: every write
  resolves inside the destination root, and a `..` segment, an absolute asset name or a symlinked
  configuration directory is refused with a typed error.

  **The invariant that makes this cheap: both entry points construct the same `AuditRequest` and consume
  the same `AuditVerdict`.** The MCP server is **impure I/O wiring** in the §Pure/Impure master-rule sense
  — a protocol adapter, exactly as `cli.py` is an argv adapter. It contains **no audit logic, no verdict
  logic, and no second decision path**. A behaviour reachable through MCP and not through the CLI is an
  architecture violation, not a feature.

  **Binding constraints** (mirrors PRD §Project Classification; each is testable, not aspirational):
  1. **stdio only** — no network listener is opened, no port is bound. Asserted by gate.
  2. **No HTTP stack** — the `argus.* ⊬ fastapi/uvicorn/starlette` import-isolation gate (§H) extends to
     the new module unchanged. ADR #20's *"downstream of the HTTP/A2A boundary — takes no A2A token,
     registers no route"* is preserved verbatim.
  3. **No new authority** — same work-manifest permission boundary (NFR-S4). No capability the CLI lacks.
  4. **No credential handling** — accepts and stores no keys, tokens or accounts. `--deep` (FR36) reads its
     provider credential through the existing adapter's environment contract, never through this surface.
  5. **Verdict parity** — same repo, same commit, same verdict through either surface, pinned by test.

  **Command assets are data, not code.** They instruct a host to invoke the CLI. They introduce no
  execution path of their own, which is why they need no threat model beyond the CLI's — and it is why
  they are listed here as configuration rather than as a third entry point.

  **Why stdio rather than HTTP:** the excluded surface at PRD §Project Classification is a *hosted
  service* — somebody else's audit on somebody else's machine, requiring endpoints, auth, rate limits, an
  SDK and API versioning. A stdio process is the user's audit on the user's machine, speaking a protocol
  instead of a shell. Choosing stdio is what keeps constraints 1–4 true by construction rather than by
  discipline.

### B. Repository Intake & Indexing
- **AST/code-graph index FIRST** via `tree-sitter==0.25.2` + `tree-sitter-python==0.25.0`; structural
  search, not embeddings.
- **Graph-derived partitioning** (import/call graph, not directories); ≤40 files/15k LOC units, conservative
  budgets + `context_pressure` auto-downgrade.
- **Stack detection** via `cloc`/`radon==4.1.0` + tree-sitter; ~~V1 deep = Python only, `claim_emitted` proxy
  elsewhere~~ **V1 deep grounding is delivered for every language enumerated in
  `argus/shared/source_languages.py`, with the `claim_emitted` proxy for anything outside that set or any
  file whose grammar is absent**, via a stack-agnostic `claim→validated?` interface (NFR-P2). *(Amended
  2026-08-10, Story 10.2 / `DF-AUD-APAA-D`; delivered by `sprint-change-proposal-2026-07-28.md`.)*

### C. Coverage Ledger, Recording Schema & Verdict (determinism core)
- **Fixed-enum Pydantic v2 ledger** (`audited_deep/_shallow/tool_scanned_only/inferred/skipped`); reserve
  `partition_id` (always `"root"` V1).
- **Recording schema = first-class frozen contract** — the verdict folds over recordings; freeze as hard as
  the verdict.
- **Pure-function verdict gate, 0 LLM tokens**, isolated module; **Prosecutor = distinct pure-consumer pass**
  (cannot call an LLM — FR15/FR19).
- **Content-addressed memoization; cache key = full recording-producing closure**: detector-set content-hash
  (NOT a human version string) + model-checkpoint-captured-from-API-response + ~~tree-sitter-grammar/tool
  versions~~ **per-grammar tree-sitter provenance (every grammar that PARSED, at its own version) + tool
  versions** *(amended 2026-08-10, Story 10.2 / `DF-AUD-APAA-D` — a DESIGN CHANGE, not a defect fix)*
  + budget/materiality + work-manifest scope. **Invalidate on detector-set change; a human-rejected
  finding busts its own key** (R2/R3). Cache-key derivation is a pure golden-tested function + CI canary.
- **Memoization is specified here and NOT YET WIRED into the pipeline.** *(Recorded 2026-08-10b.)*
  `argus/cache/memo_store.py` exists; `argus/pipeline.py` does not import it. **This is a delivery gap,
  not a design gap** — the design above stands. **Wiring order is load-bearing and deliberate:**
  1. **Story 10.2 first** — the cache key currently folds **one** `grammar_version` resolved from
     `tree-sitter-python` while the index parses **10 languages**, so a non-Python grammar change would not
     move the key. 10.2 makes provenance per-grammar and explicitly declines to wire the store.
  2. **Story 12.3 second** — wires the store over the corrected key.

  Wiring first would persist a key that is wrong for 9 of 10 languages, and undoing it would cost a
  `CACHE_KEY_SCHEMA_VERSION` bump plus a migration. **Free now, expensive later** — the same
  silent-staleness failure DF-5-1-A flags for `prompt_template_version`.

  ✅ **Step 1 is DONE — 2026-08-10, Story 10.2.** The key was corrected **before** anything depended on
  it. Provenance is per-grammar, `CACHE_KEY_SCHEMA_VERSION` is bumped `"2"` → `"3"`, and the bump cost
  exactly one constant because the measurement that licensed it held at the moment it was taken: **no
  production caller derives a key.** ~~`argus/pipeline.py` imports neither `argus.cache.key` nor
  `argus.cache.memo_store`, and it still does not — Story 10.2 added not one line to that file.~~ **Not
  wiring the store was a positive requirement of Story 10.2 (its AC6), not an omission.** Had the order
  been reversed, the first persisted entries would have been keyed on a fingerprint that was wrong for
  nine of ten languages, and correcting it hours later would have cost the migration this ordering exists
  to avoid.

  ⚠️ **The struck sentence was TWICE overtaken and is corrected here, not deleted (§3.4) — amended
  2026-08-13 by Story 12.3.** Both corrections were produced by re-measuring rather than by re-reading:

  1. **Story 12.2 falsified its first half before 12.3 began.** `argus/audit/deep_audit.py` imports
     `GrammarProvenance` + `RecordingProducingClosure` and `argus/index/ast_index.py` imports
     `GrammarProvenance`, so `argus.cache.key` was **already production-imported and in the static import
     closure from `argus.cli`** while this paragraph still said otherwise. 10.2's *substantive* claim
     survived unharmed — **reachable is not the same as derives-a-key** — but the evidence quoted for it
     had stopped describing the tree. The mechanical fence quoted here (*`grep -rn
     "derive_cache_key\|MemoStore"` must not name `pipeline.py`*) was likewise a fence for Story 10.2's
     duration only; it has now been deliberately crossed by 12.3 and is retired, not violated.
  2. **Story 12.3 completed step 2.** `argus/cache/stage_memo.py` derives a key on every run and
     `argus/pipeline.py` consults `MemoStore` around the deterministic detect/grade stage.

  ✅ **Step 2 is DONE — 2026-08-13, Story 12.3.** The hook is UNIT-level and wraps the detect/grade +
  orphan stage only. Consequently `CACHE_KEY_SCHEMA_VERSION` is **frozen at `"3"` in the expensive
  sense**: persisted entries now exist, so a key-shape change from here on costs the migration the
  ordering was designed to pre-pay. The memo PAYLOAD schema is a different constant and did move
  (`MEMO_STORE_SCHEMA_VERSION` `"1"` → `"2"`), because a findings-only payload would have re-run the very
  loop it was meant to skip — a cache that saves nothing while every byte-identity test passes.

  🔴 **SCOPE, stated because omitting it would overclaim: memoization covers the DETERMINISTIC stage
  only.** The opt-in `--deep-audit` pass (FR36) runs downstream and is never served from the store, so
  **PRD §501's claim that determinism under the deep pass is preserved by this path is NOT delivered** —
  with `--deep-audit` on, a re-run dispatches again. Filed as `DF-12-3-A`. A committed fence
  (`memo_store._fence_llm_derived`) makes it impossible for an LLM-derived recording to enter a memoized
  payload while the closure carries the V1 placeholder checkpoint, because the key does not vary with the
  model and two models would otherwise collide on one slot.

  **Wiring delivers FR27 / NFR-D1; it adds no requirement.** A cache is a correctness surface in an
  assurance tool: a hit and a cold run must produce **byte-identical** verdicts, pinned by test —
  `TC-ArgusAgent-CACHE-001-87`. Byte-identity alone is **not** evidence here, because it is green with no
  cache at all: `-81` proves the warm run does not execute the stage and `-82` poisons the slot to prove
  the served value reaches the verdict.
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
  - ~~`apaa/audit/minions_llm_adapter.py` → thin adapter holding an `LLMProviderOrchestrator`
    (`minions_core.providers.orchestrator`), mapping `LLMRequest`/`LLMResponse` ↔ APAA's frozen
    `LLMRecording`.~~
    **Superseded by Story 9.1 (IN-2 / RS-1).** Argus imports `minions_core` in **no form**, and a committed
    gate asserts it is absent from `sys.modules` in a fresh interpreter. The live dispatch path is
    **`argus/audit/open_llm_adapter.py::OpenLLMAdapter`**, behind the opt-in **`[llm]`** extra. The port
    contract (`LLMDispatchPort`, single `dispatch(req) -> LLMRecording`), the
    checkpoint-captured-from-API-response rule (R3), and the `FakeDispatch` injection for zero-token tests
    are **unchanged**. Struck rather than deleted (§3.4). *(Corrected 2026-08-10b.)*
  - **Consequence of the separation, recorded:** the *"no fork (§3.3) — inherits the orchestrator's
    fallback chain, circuit breaker and cost attribution **for free**"* rationale below **no longer holds
    automatically.** Those behaviours are now Argus's own responsibility on the `OpenLLMAdapter` path.
    Story 12.2's honest-degradation ACs (NFR-R1) are what supply them; they are not inherited.
  - `apaa/audit/deep_audit.py` depends on `LLMDispatchPort`, **never the orchestrator directly**; tests inject
    a `FakeDispatch` → 0 LLM tokens.
  - **No fork (§3.3):** inherits the orchestrator's fallback chain + circuit breaker + cost attribution, which
    feeds APAA cost governance + honest degradation for free.
  - **Tiered routing** (cheap triage → premium deep-read) + **prompt caching** for multi-perspective passes
    over a cached partition (research: 59–70% savings; the cache doubles as the determinism mechanism).
  - ~~**Packaging:** `minions[apaa]` extra gains `httpx` (providers' only third-party dep).~~ **Corrected
    2026-08-10b:** `httpx` is a **base dependency of `argus-agent`**; the LLM path ships behind the
    optional **`[llm]`** extra. See §I.
- **Deep audit is OFF by default** (FR36, added 2026-08-10b). ~~`DeepAuditSeam`
  (`argus/audit/deep_audit.py:91`) is referenced today only from `argus/audit/*` and
  `argus/dogfood/proof_run.py` — **never from `argus/pipeline.py`**. Story 12.2 wires it as an explicit
  opt-in.~~
  **Corrected 2026-08-13 (Story 12.2), struck not deleted — two of the three claims were false when
  written and neither had ever been checked.** Measured by execution on `2bea92f`: (1) `class
  DeepAuditSeam:` is at **`argus/audit/deep_audit.py:98`**, not `:91` — line 91 is inside
  `build_closure_from_recording`'s kwargs dict. Both this document and `epics.md` stated `:91`, and
  their agreement read as verification without either having measured it; anchor on the text `class
  DeepAuditSeam:`, never on a line number. (2) The seam had **ZERO production callers** — more
  unwired than "referenced only from …" claims. The identifier appeared in exactly three places:
  its own `class` statement, its own `__all__`, and `tests/test_llm_dispatch_port.py`.
  **`argus/dogfood/proof_run.py` never imported it**; its only mention was a docstring saying the
  seam is a separate injected port *not* used. (3) *"never from `argus/pipeline.py`"* **HELD**.
  **Story 12.2 has now wired it** as an explicit opt-in: `--deep-audit` → the existing `deep` pass
  token → a **function-local** import at the `argus/pipeline.py` call site → `argus/audit/deep_pass.py`
  → `DeepAuditSeam` over the injected `LLMDispatchPort`. The deferred import is what lets the seam be
  in the STATIC closure from `argus.cli` (so FR36's `wired` disposition is proven, not asserted) while
  remaining absent from `sys.modules` on a default run (so NFR-S6 holds). Both directions are gated —
  see **Deferred-import positive control** below.
  - **Default path stays zero-token and offline** (NFR-C3, NFR-D2, NFR-S6) — no key, no account, no
    transmission. **A default-on deep pass would trade away the free default, the clean privacy posture,
    and NFR-D1 determinism simultaneously**; it is forbidden by the FR contract, not merely discouraged.
  - **Egress is disclosed before the first byte is transmitted**, naming the provider (NFR-S6). A committed
    gate fails if any egress path is reachable without opt-in — the shape of the existing import-isolation
    gates.
  - **Spend flows through the existing ceiling** (FR21/FR22) — halt → skip → downgrade → report. **No new
    cost-governance mechanism** (AR7/§3.3).
  - **Story 6.1's determinism quarantine holds unchanged:** the subprocess gate proving the pure seam does
    not import providers must still pass after wiring. Wiring is an adapter change, never a purity change.
  - **Tiered routing and prompt caching** (above) remain the design; they now describe the `OpenLLMAdapter`
    path.

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

**Suppression threat model** *(added 2026-08-10 by Story 10.3 / `DF-AUD-APAA-E`)* — the specification
artifact on which the bless of `--ignore-path` and `--ignore-pattern` stands. The epic's condition was
explicit: *absent this model, the flags are removed rather than blessed.* Four questions, answered in
these terms; this is a specification, not a security review of Argus at large.

- **Who may suppress a secret finding — and why that is the wrong question.** There is exactly one
  principal. The audit runs with the invoker's authority under the existing work-manifest permission
  boundary (NFR-S4); Argus opens no listener, accepts no token and registers no route (ADR #20/AR9), so
  there is no second party to authorise anything against. Anyone who can pass `--ignore-pattern` can
  already edit the source, delete the finding, or not run the audit at all. **Suppression is therefore
  not an access-control question, it is an evidence question** — and the answer to an evidence question
  is recording, not permission. The threat this model addresses is not a malicious operator defeating a
  control they own; it is **an audit that reports green while a credential it found sits unmentioned**,
  and a reader of that report who cannot tell the difference between "clean" and "quiet".
- **What is recorded when they do.** A suppression an operator's own flag caused is emitted as a
  non-blocking, redacted `operator_suppressed_secret:<reason>` finding carrying its reason token
  (`custom_ignore_pattern` / `custom_ignore_path`) and its repo-relative locator **and nothing else** —
  never the secret, never source bytes, never the operator's pattern (which is operator-supplied text
  and may itself be secret bytes), never an absolute host path (NFR-S1/NFR-S2/AR8). Every run also
  prints one stderr line stating how many such suppressions occurred, **including when the answer is
  none**: a disclosure that appears only when something was hidden is indistinguishable from an unwired
  feature. Attribution is conservative — where a built-in default already matched, the operator's flag
  caused nothing and is not credited. The record is `depth_supported=None`, so it is ineligible to
  block a verdict by construction: disclosure can never itself become a gate. This is the register
  `--coverage-scope` established — **a narrowing is permitted, disclosed, and never allowed to lower a
  bar.**
- **What each flag can and cannot reach.** The Live-Key Safeguard (`LIVE_KEY_PATTERNS` in
  `argus/detectors/secret_suppression.py` — AWS access key, GitHub PAT, PEM private-key header, Slack
  token) is now evaluated **above both flags**, so neither can suppress a high-confidence live
  production key. Measured on 2026-08-10, this was true of `--ignore-path` and **false of
  `--ignore-pattern`**: the CLI arm ran above the safeguard the module's own docstring promised, and
  `--ignore-pattern "A"` suppressed every live key in the repository while recording nothing. The two
  flags were never the same risk, which is why they took different rulings. The single remaining
  override is the inline `# argus:ignore` annotation, preserved deliberately: it lands in a pull
  request beside the line it exempts, which is a different accountability class from an argv flag.
- **The residual risk, accepted and not engineered away.** `--ignore-pattern` matches by **bare
  substring**, so a short pattern remains a wide net over everything the safeguard does not cover — the
  generic assigned-secret and high-entropy classes, which are the majority of real findings. Bounding
  the *matching semantics* (anchoring, a minimum length, requiring a locator scope) is a behavioural
  redesign of a shipped flag and is out of this story's scope; it is filed as **`DF-10-3-C`**. Also
  accepted and filed: built-in suppressions — the public sentinels, the inline annotation and
  `DEFAULT_TEST_PATH_PATTERNS` — are **not** disclosed, because no operator flag caused them and
  folding them in would move the finding count on runs that passed no flags (**`DF-10-3-B`**).

  Referenced from the CHANGELOG entry that specifies the two flags, so a consumer reading about them
  reaches this section. Pinned by `tests/test_secret_suppression_recording.py`
  (`TC-ArgusAgent-SECRET-001-15`..`-22`).

### H. Self-Audit & CI (trust substrate)
- **Defect cartridges** under `tests/apaa/cartridges/` (vacuous, secret, orphan) **+ hidden holdout + clean
  true-negative controls** (any 🔴 on a clean control = CI fail) — FR20.
- **Import-isolation gate** `tests/apaa/test_no_web_imports.py` (`apaa.* ⊬ fastapi/uvicorn/starlette`) —
  committed/durable. (Verified today: all reuse targets, incl. `providers`, are FastAPI-free.)
- **Determinism golden-tests** — cache-key derivation + envelope canonicalization.
- **Evidence-citation rule for status claims** *(added 2026-08-10 by Story 10.1; satisfies AI-E9-7)* —
  **a document that asserts a release or release-readiness status cites an executed gate — a GitHub
  Actions run URL or run id, together with the sha that run covers — or records the status as NOT
  ESTABLISHED.** Three parts, all binding:
  - **The sha is part of the citation, not decoration.** A run id is sha-scoped, so a bare id looks like
    evidence while covering an unknown tree — including trees created after the run. `run 31341363300`
    is a half-truth; `run 31341363300 (00c8d1b, 3/3 legs green)` is the claim.
  - **A local run is necessary, not sufficient.** `pytest`/`mypy`/`bandit` on a developer workstation is
    not the gate and cannot see the runner's host; it is recorded as LOCAL and never on its own
    discharges the rule. `DF-AUD-APAA-C` is the worked example: `sprint-change-proposal-2026-07-28.md`
    declared READY FOR RELEASE on a local `pytest` run while the CI gate that same proposal had just
    created had never passed (run `30774175196`, `failure`).
  - **NOT ESTABLISHED is a first-class recordable state**, not a gap. This is the governance twin of
    **`AUDIT_FAILED`-is-not-a-verdict** (`action.yml:33-48`) and of `INSUFFICIENT_COVERAGE` (AR10): the
    tool refuses to dress a non-result as an assessment, and the project's own record is held to the
    identical rule — one principle, applied to the tool's output and to its governance alike.

  Enforced by `tests/test_evidence_citation.py` and `tests/test_status_document_registry.py`
  (`TC-ArgusAgent-DOCS-001-20`..`-23`) — *(amended 2026-08-17 by Story 13.4)*: the first holds the
  DERIVATION (`-20`, `-21b`, `-23`, and Story 12.9's `-24`/`-25`/`-25b`) — what a status claim and an
  executed-gate citation are; the second holds the POPULATION (`-21`, `-22`) — which planning records
  are governed and whether that set is closed. One rule, two cohesive halves, no id renumbered. See
  §Enforcement.

### I. Packaging & Deployment
- ~~**`minions[apaa]` optional extra**: `["pydantic>=2","jsonschema","radon","httpx","tree-sitter",
  "tree-sitter-python"]`; **`apaa` console script** (wired by the CLI story).~~
  **Superseded 2026-08-10b — factually stale since the 2026-08-03 repository separation.** Argus is no
  longer packaged inside Minions. The `minions[apaa]` extra and the `apaa` console script are
  **Minions-side removal surface** and belong to handoff **H1**, not to this repository. Original text
  struck rather than deleted (§3.4 evidence immutability).

**Shipped package, ~~measured in place 2026-08-10b~~ — SUPERSEDED, see the corrected table below:**

| | |
|---|---|
| Distribution | **`argus-agent` 0.1.0**, module `argus`, flit backend |
| Python | `>=3.10` |
| ~~Console scripts~~ | ~~`argus`, `argus-agent`, `repo-audit` — all → `argus.cli:main`~~ |
| ~~Base deps~~ | ~~`pydantic>=2.0` · `jsonschema>=4.0` · `radon>=4.1.0` · `httpx>=0.24.0` · `tree-sitter>=0.25.0,<0.26` · `tree-sitter-python>=0.25.0,<0.26`~~ |
| ~~Extras~~ | ~~`[dev]` · `[llm]` (`litellm>=1.0.0`) · `[languages]` (9 grammars)~~ |
| ~~Grounded languages~~ | ~~**10** — Python (base) + 9 via `[languages]`~~ |

🔴 **CORRECTED 2026-08-15 by Story 12.9 / AC6.1 — four cells above were measurably STALE at
`de05dec`.** Struck, not deleted (§3.4 evidence immutability). This is the architecture's own statement
of *what the release contains*, and Story 12.9 is the release story, so a stale one here is the kind of
published falsehood the Epic-11 retrospective §4.4 filed. What moved, and when: **Story 12.6** added a
fourth console script (`argus-mcp`), and **Story 12.5** promoted the nine non-Python grammars into the
base dependencies under NFR-P3, which made `[languages]` a backward-compatibility **alias** rather than
a feature and made *"Python (base) + 9 via `[languages]`"* false in both halves.

**Shipped package, measured in place 2026-08-15 (`de05dec`), and now held by a guard:**

| | |
|---|---|
| Distribution | **`argus-agent` 0.1.0**, module `argus`, flit backend |
| Python | `>=3.10` |
| Console scripts | **4** — `argus`, `argus-agent`, `repo-audit` → `argus.cli:main`; `argus-mcp` → `argus.mcp.server:main` (Story 12.6 / FR35) |
| Base deps | `pydantic>=2.0` · `jsonschema>=4.0` · `radon>=4.1.0` · `httpx>=0.24.0` · `tree-sitter>=0.25.0,<0.26` · **all ten** tree-sitter grammars (`-python`, `-javascript`, `-typescript`, `-go`, `-rust`, `-java`, `-c`, `-cpp`, `-ruby`, `-php`) |
| Extras | `[dev]` · `[llm]` (`litellm>=1.0.0`) · `[languages]` — **a retained backward-compatibility ALIAS, not a feature**: every line in it is already an ordinary dependency, so it adds nothing to an install (Story 12.5 / NFR-P3) |
| Grounded languages | **10**, all in the DEFAULT install — `pip install argus-agent` grounds every language the tool claims to support |

**A form a guard can hold, which is why this table is now shaped as it is.** Each cell above is derived
from `pyproject.toml` and the live registry by `tests/test_installed_artifact.py`
(`TC-ArgusAgent-DOCS-001-72`), in both directions: a fifth console script, an eleventh grammar or a
promoted/demoted extra turns that guard RED rather than leaving this paragraph quietly wrong for two
epics, which is exactly what happened between 2026-08-10b and 2026-08-15.

**Index channel, exit condition RE-AFFIRMED 2026-08-15 (Story 12.9 / DN-1).** `argus-agent` still ships
to **no package index** and no publish was attempted. The reasoning is unchanged and is recorded in four
places (`README.md`, `.github/workflows/release.yml`'s header, `CHANGELOG.md`'s *Resolving
`argus-agent`* table, and Story 9.2 / D1-D13): an index publish is **permanently irreversible**, needs a
credential this repository cannot prove exists, and is an operator decision taken with credentials in
hand. `epics.md:2465` is **permissive** (*the index channel "may ship independently"*), not mandatory.
The named exit condition — the distribution name claimed on PyPI **and** a Trusted Publisher (OIDC)
configured for this repository — is restated here **with a date** so *"interim"* keeps an end rather
than becoming permanent by silence.

~~🚩 **The `tree-sitter <0.26` upper bound is LOAD-BEARING, not hygiene.** On `0.26.0` the cartridge
self-audit flips `NOT_READY_FOR_RELEASE` → `RELEASE_READY` because AST corroboration stops firing —
**a false negative from an assurance tool**, the PRD-fatal direction.~~ A metadata bound constrains a
*resolver*, never an already-installed environment on a machine we do not control, so it **must also be
asserted at runtime** (Story 11.4). Do not widen without re-running `tests/test_cartridge_selfaudit.py`.

🔴 **CORRECTED 2026-08-12 by Story 11.4 — the struck sentence above was measured and is NOT
REPRODUCIBLE as stated.** Struck, not deleted, per §3.4 evidence immutability. Two independent
measurements, both LOCAL (Windows / CPython 3.11.15; see AI-E10-1 — **no CI run covers any Epic 10 or
Epic 11 sha**, `NOT ESTABLISHED`; a human establishes one by running `audit-ci.yml` against a pushed
sha):

1. **Upstream.** `py-tree-sitter` 0.26.0's breaking changes are `Language.version` → `Language.abi_version`,
   `Language.query()` → `Query(language, source)`, `Parser.timeout_micros` / `QueryCursor.timeout_micros`
   → `progress_callback`, and `Point` becoming a tuple subclass rather than a namedtuple. **Argus uses
   none of them** — it uses `Language()`, `Parser()`, `parse()`, `root_node`, `has_error`, `.type`,
   `.children`, `.child_by_field_name`, `.start_point[0]`, `.text` — and the minimum grammar ABI is
   unchanged. (Sources: the `py-tree-sitter` releases page and its 0.26.0 documentation, read 2026-08-12.)
2. **Behavioural.** When AST extraction is made to fail *totally* — the shape a core/ABI break would
   have — the cartridges land on **`INSUFFICIENT_COVERAGE` / exit 3 / `row_1_below_floor`**, never
   `RELEASE_READY`: zero definitions means zero deep coverage, and the **floor row fires first**. The
   cartridge corpus also sits at deep 1/2 = 50%, **below** the 60% row-3 gate, so it is structurally
   incapable of the flip the struck sentence names.

**The hazard is real and worse than the sentence, and it is not a version problem.** Measured on a
staged repository *above* the 60% gate — the shape a real user's repository has, and the shape this
repository has at `assessed_deep_ratio` 61/77 — a **drifted extraction vocabulary at an IN-BOUND
`tree-sitter 0.25.2`** flipped `NOT_READY_FOR_RELEASE` / exit 2 → `RELEASE_READY` / exit 0, with
`deep_ratio` **unchanged at 5/6 in both runs**: `vacuous_test_ast` (verdict-eligible) silently became
`vacuous_test_heuristic` (advisory-only), and cross-cutting #6 guarantees an advisory finding cannot
move a verdict. **No surface Argus prints can see that loss.**

**The pin is RETAINED, with its reason restated honestly:** 0.26 is *unproven here*, not *proven
unsafe*, and conservative-by-default is the right posture for an assurance tool. Widening it remains a
packaging decision owned by **Story 12.5 / the operator** (NFR-P3). **What now carries the guarantee is
the runtime defence Story 11.4 added**, precisely so that the pin stops being the only one: a
**per-language behavioural canary** at `argus/index/ast_index.py::_get_parser_for_lang` (ARM 5) parses
a pinned snippet through the real loader seam and compares the extraction against the frozen
expectation in `argus/shared/grammar_status.py`; a mismatch — or a core version outside the declared
range, checked as a second and independent signal — withholds the parser and records
`tree_sitter_runtime_unvalidated`, which degrades through the **existing** floor row to
`INSUFFICIENT_COVERAGE` with no change to `verdict_gate.py`, `pipeline.py`, the FR16 decision table or
any threshold. Guard: `tests/test_grammar_runtime_validation.py`.

~~⚠️ **Open packaging decision, owned by Story 12.5 (NFR-P3).** The 9 grammars are an **optional extra**,
so the default public install grounds **Python only** — which NFR-P3 classifies as a packaging defect for
the V1.5 audience. Resolving it means either promoting the grammars to base dependencies (larger install,
no discovery burden) or making the documented public install command carry the extra (smaller default, a
step the user must not miss). **Recorded as a decision, not decided here.**~~

✅ **Packaging decision RESOLVED by Story 12.5 (NFR-P3)** *(decided 2026-08-15; the paragraph above is
STRUCK, not deleted — §3.4 evidence immutability. It was true of every release up to this change, and the
record of what the default install used to be is what makes the change auditable).* **Promoting to base
dependencies is the option taken**, and the other one is rejected on the NFR's own words: an install
command carrying an extra is still a step the user must not miss, and NFR-P3 classifies degraded coverage
from a missing grammar as a *packaging defect, not a user error*. The 9 non-Python grammars now sit in
`pyproject.toml` `[project.dependencies]`, so `pip install argus-agent` grounds all 10 supported source
languages with nothing to discover. `[project.optional-dependencies] languages` is RETAINED as a
backward-compatibility alias — Story 10.2 documented it publicly, so `pip install "argus-agent[languages]"`
exists in somebody's script and must not start failing — and is pinned equal to the default requirements so
the alias can never become a second source of truth. The cost accepted with eyes open: a larger default
install (nine wheels) for every user, including a Python-only one. Guards:
`tests/test_grammar_runtime_validation.py` (`TC-ArgusAgent-DOCS-001-61`, over the real `pyproject.toml`).

✅ **The residual case is now DISCLOSED rather than assumed away (NFR-P3, second clause).** A grammar can
still be absent at run time — uninstalled, vendored, broken for the host runtime, or a core that does not
pass the Story 11.4 canary — and a default install no longer makes that a user's own doing. So the reason
is stated **at the point the file is downgraded**: `argus/reports/generator.py::_render_grammar_downgrade_section`
names each downgraded file, the depth it reached and the grammar package that would have grounded it, and
`argus/reports/plain_english.py::render_grammar_downgrade_summary` states the same facts once per failure
class in the human register. This closes `DF-10-4-A` — Story 10.4's callout fires only when *nothing*
parsed, so a polyglot repository whose Python parsed learned nothing about its failed Go grammar. It is a
SEPARATE surface, not a widening of that trigger: 10.4's sentence ("no file could be parsed") is false for
a partially-parsed repository, and `TC-ArgusAgent-REPORT-002-35`/`-36` pin both halves of the fence.

**V1.5 distribution channels** *(added 2026-08-10b; mirrors PRD §Developer Tool)*: public index (primary)
· marketplace action (**gated on Story 11.3**) · **MCP server as an entry point in this same distribution
— not a separate channel**, so it inherits the release workflow, version and gate evidence · packaged
assistant command assets. Desktop stores and OS package managers **deferred with reasons**; hosted runner
remains **V4**.

**Verified privacy posture** *(measured 2026-08-10b)*: network egress confined to
`argus/audit/open_llm_adapter.py` ~~behind the opt-in `[llm]` extra~~ · committed import gates · **no
telemetry** · MIT licensed. NFR-S6 binds this: the default path transmits nothing, and the agent surface
opens no listener.

> **Correction, 2026-08-13 (Story 12.2), struck not deleted. THE `[llm]` EXTRA IS NOT AN EGRESS GATE,
> and this sentence implied it was.** Measured in `pyproject.toml` on `2bea92f`: the `[llm]` extra
> contains **only `litellm`**, while **`httpx>=0.24.0` is a BASE dependency** of `argus-agent`.
> `OpenLLMAdapter.dispatch` falls back to `_dispatch_httpx` when `litellm` is absent, and that method
> performs a real `httpx.Client().post(...)`. **So a plain `pip install argus-agent` — with no extras
> at all — already contains a complete, working egress path.** The extra gates the *multi-provider
> convenience layer*, not egress. This mattered directly: it is why FR36's opt-in **cannot** be a
> packaging extra, and (with `OpenLLMAdapter` silently absorbing six environment variables on
> construction) why it cannot be an environment variable either. The opt-in is an explicit act at the
> invocation — `--deep-audit`. What actually confines egress is the **import quarantine** plus that
> flag, both committed gates; the extra was never doing that work.

**No container/hosting in V1/V1.5** (CLI + library + local stdio surface); runs on a parallel-capable
assistant host and a sequential-canonical fallback.

### Driver Namespace
- **`APAA-FR-*` / `APAA-NFR-*`**, mapped 1:1 onto the PRD FR1–37 / NFR clusters *(FR34–37 added 2026-08-10b)*; the full component↔driver
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
- ~~Validation-set `N` (gates precision-harness ground-truth shape — resolve before harness build).~~
  ~~**Still open, and the "resolve before harness build" condition was not met.** The harness was built
  (Story 6.6) and `precision-validation-protocol.md` resolved `N` **implicitly** — as `N ≥ 5` **labeled
  cartridges** — while PRD L161 specifies `N ≈ 5–10` **real repositories**. **Two corpora, never
  reconciled.** L152-154 called this *"the one open input that gates an ARCHITECTURE choice"*; it was
  closed by implementation rather than by decision. **Owned by Story 13.1**, which must pick one
  definition and amend the other.~~ *(Recorded 2026-08-10b.)*

  ✅ **RESOLVED BY DECISION 2026-08-16 (Story 13.1 / DN-1) — the PRD governs.** *(VALIDATION-SET
  RESOLUTION — the identical paragraph is recorded at §Architectural Decisions and in §Gap Analysis,
  so no site survives saying something else.)* The validation set is **`N ≈ 5–10` real repositories**
  with a floor of **`N ≥ 5`**, per PRD §Validation Approach; `precision-validation-protocol.md` §5's
  conflicting **`N ≥ 5` labeled planted-defect cartridges** floor is **struck**. **Reason:** the two
  documents specified different *quantities*, not two opinions about one — the cartridges measure
  **recall** against defects the team planted and answered, while the gate must measure **precision**
  on code nobody planted. A gate clearable by the team's own plants is not an externalization gate.
  The cartridges are **re-labelled, not demoted**: they remain the FR20 recall instrument, CI-asserted
  and unchanged. **Membership is a closed, machine-readable manifest** —
  `tests/corpus/_manifest.py::VALIDATION_CORPUS` — carrying a pinned commit sha, licence, language
  and provenance per member, with exclusions recorded in the manifest itself and the floor **derived**
  from the same `VALIDATION_SET_FLOOR_N = 5` rather than forked. **This closes the input by DECISION;
  it does not clear the gate.** Measured at resolution: **`N = 0` eligible members**, no adjudication
  run, `protocol_cleared` never `True`. **Updated the same day, 2026-08-16: the operator ratified five
  members under AC3b, so `N = 5` and the floor is MET** — the resolution-time zero is kept struck-not-
  erased because it is the state the DECISION was taken in. Reaching the floor is one of four §5
  conditions; the other three (the adjudication run, the ≥80% figure, zero clean-repo blocking FPs) are
  unmet, so the gate remains **PROVISIONAL**. Enforced by **`tests/test_validation_set_decision.py`**
  (`TC-ArgusAgent-DOCS-001-73`..`-76`).

  **On the two-site history, which is the reason this entry is worded identically at three sites:**
  the 2026-08-10b proposal amended this site and left the §Architectural Decisions marker saying
  `CLOSED`, producing a plan that contradicted itself for three epics — one site reading
  *closed-as-assigned*, the other *still open*. Closing one again would have repeated it exactly.
- ~~Minions-dogfood partition + budget-sizing plan (so the proof run doesn't land
  `INSUFFICIENT_COVERAGE`).~~ ✅ **CLOSED 2026-08-10b — DELIVERED by Story 7.1.** Artifacts on disk:
  `minions-dogfood-partition-plan.md`, `minions-dogfood-budget-plan.md`.
- ~~Budget-ceiling `$X` default.~~ ✅ **CLOSED 2026-08-10b — resolved as OI3, LOCKED, and the
  resolution is "there is no default."** The epic-6 retrospective records *"OI3 (`$X` sized empirically
  in 7.1) are LOCKED design inputs, not open questions."* Shipped code agrees:
  `argus/cost/budget_governor.py` declares `ceiling_credits: int | None` with **no numeric default**,
  treats `None` as the first-class *no-ceiling-configured* state, and maps `0 → None`. The operator
  sets the ceiling per target; sizing is empirical per audited repository. **A numeric default was
  deliberately refused** — a wrong default silently truncates an audit, which is the honest-degradation
  failure NFR-C2 exists to prevent.

*(Section reviewed end-to-end 2026-08-10b. All three entries are now closed or assigned; none is
left as a bare OPEN marker with no owner.)*

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
- **A degraded outcome records the cause it actually had**, and **a recorded reason token names a remedy that works**
  *(added 2026-08-10 by Story 10.4 / `DF-AUD-APAA-F`)*. A token that names the wrong cause is a
  named reason in **form only** — it satisfies PRD `:473` ("a named reason token — never a silent drop")
  on the page while handing the operator a remedy that cannot help. Corollaries: **classify by ARM
  POSITION**, never by exception message or exception type (the same broken grammar surfaces as
  `ValueError`/`TypeError`/`OSError`, and ABI text is a C format string a release may change); a broad
  `except Exception` is permitted only with `# noqa: BLE001` **and** a comment naming the degraded
  outcome it records; a caught-exception tuple whose members subclass one another
  (`except (ImportError, Exception)`) is **forbidden** — it reads as if it discriminates and does not;
  and **no exception message, `repr`, traceback or host path is ever persisted** (NFR-S1). `BaseException`
  stays uncaught: AR10 degrades *errors*, never *signals*.

### Enforcement
**All APAA agents MUST:** route JSON through `canonical`; emit findings with a locator or not at all; keep
pure modules I/O-free; import only FastAPI-free leaf modules. **Enforced by:** the import-isolation gate,
determinism golden-tests (serializer + cache-key), the secret-containment property suite, and the
repo-wide file-size sweep registered below — all committed under `tests/`.

> **Correction, 2026-08-12 (Story 12.1).** The sentence above previously read *"…and file-size CI —
> committed under `tests/apaa/` + the Minions CI model."* **Both halves were false as written and are
> corrected here rather than left standing.** Measured on this tree: `tests/apaa/` **does not exist**
> (the 2026-08-03 separation moved the suite to a flat `tests/`), and `grep` over all three workflows
> — `argus-student-audit.yml`, `audit-ci.yml`, `release.yml` — finds **no file-size step**. So the
> architecture asserted an enforcement that had **never been built**, which is exactly the defect class
> the rest of this section exists to close: a rule stated in prose, believed to be enforced, and
> structurally unable to notice that it was not. `argus/pipeline.py` drifted from 1199 to **1331**
> lines under that false assurance. The claim is made TRUE in the same change that corrects it — see
> **Module-size enforcement** below — and it is a committed test rather than a CI step, so it holds on
> every local run too. **CI evidence for the correction: NOT ESTABLISHED** (no CI run covers any Epic
> 10, 11 or 12 sha).

**Governance enforcement** *(added 2026-08-10 by Story 10.1; amended 2026-08-17 by Story 13.4)*: the §H
**evidence-citation rule for status claims** is enforced by **`tests/test_evidence_citation.py`** and
**`tests/test_status_document_registry.py`** (`TC-ArgusAgent-DOCS-001-20`..`-23`). It
resolves `sprint-change-proposal-*.md` and `epic-*-retro-*.md` by **glob** under the artifact directory —
so a proposal cannot escape the rule by being new — and fails any status claim carrying neither an
executed-gate citation (run id **plus** the sha it covers) nor a **NOT ESTABLISHED** marker. A rule that
lives only in a test is not a rule and a rule that lives only in prose is not enforced, so `-23` asserts
this section and the §H rule text are both still present. **The two hosts split along a COHESION
boundary, not a line-count one** (Story 13.4 / DN-1): `tests/test_evidence_citation.py` owns the
DERIVATION — what a status claim is, what a citation is, and whether the records and consumer surfaces
carry them (`-20`, `-21b`, `-23`, `-24`, `-25`, `-25b`) — and
`tests/test_status_document_registry.py` owns the POPULATION and its glob closure (`-21`, `-22`,
`_STATUS_DOCUMENTS`, `_STATUS_DOCUMENT_PATTERNS`, `_EXCLUDED_BY_DESIGN`). The split was forced, and is
recorded here rather than only in a story, because the derivation module reached **exactly 1200/1200**
against NFR-M1 and **no further status document could be registered at all** — the deadlock `AI-E13-2`
filed. It was taken as the sanctioned cohesion split (`test_module_size_ceiling.py::_REMEDY`), **never
as a line-shave and never as an `_EXEMPT_BY_DESIGN` entry**, both of which `AI-E13-2` forbids by name;
no id was renumbered, no assertion was weakened, and the globs were not narrowed.

**Status-document registration enforcement** *(added 2026-08-17 by Story 13.4 / AC6.3, writing down
`AI-E12-1`'s second half)*. **The rule: any document matching `sprint-change-proposal-*.md` or
`epic-*-retro-*.md` under the artifact directory is registered in `_STATUS_DOCUMENTS` in the same change
that creates it; the retrospective and change-proposal steps do not hand off until their own output is
registered and the guard is green.** This is not a style preference — it is the observed failure mode,
three times over: a retrospective or proposal lands, `-22`'s glob closure sees it immediately (which is
the closure working as designed), and the tree goes red in someone else's session. Registration is
ordinarily INERT — for most retrospectives `_status_assertions()` returns 0, so `-21`'s per-document loop
short-circuits — so the cost of doing it in the creating change is one line, while the cost of deferring
it is a red master. `-23` asserts one anchor phrase from this paragraph, so the rule cannot be deleted
silently. **Scope note:** the orchestrator-side half of `AI-E12-1` — editing the dev-loop retrospective
skill's own definition-of-done — is not discharged here and stays with its named owner; what this
paragraph does is give the rule a reader inside this repository, which is what `AI-E9-8` demands.

**Validation-set enforcement** *(added 2026-08-16 by Story 13.1 / AC2)*: the **VALIDATION-SET
RESOLUTION** above — *the ≥80%-precision externalization gate is measured over a corpus of real
repositories, never over the planted-defect cartridges* — is enforced by
**`tests/test_validation_set_decision.py`** (`TC-ArgusAgent-DOCS-001-73`..`-76`) and
**`tests/test_validation_corpus.py`** (`TC-ArgusAgent-PRECISION-001-21`..`-30`,
`TC-ArgusAgent-DOGFOOD-001-53`..`-55`). The resolution text must be present **at all three sites
that state it** — §Architectural Decisions, §Still OPEN and §Gap Analysis — and identical at each,
because this input spent three epics recorded as `CLOSED` at one site and *"still open"* at another,
and closing one site again would have reproduced that exactly. Membership is a **closed** manifest:
an unregistered member raises rather than resolving, a usage-shaped field (`stars`, `installs`,
`downloads`) can never be added to the schema, an exclusion without a written reason fails, and the
floor is **derived** from the single `VALIDATION_SET_FLOOR_N` rather than transcribed. The published
gate figure is derived too — `TC-ArgusAgent-DOGFOOD-001-54` asserts the committed proof artifact
carries the **live derivation**, so a hand-written corpus number fails before it is published
(`DF-8-5-C`). An architecture decision with no guard is how this one drifted for three epics.

**Invocation-contract enforcement** *(added 2026-08-10 by Story 10.3 / `DF-AUD-APAA-E`)*: the §A
**invocation contract** is enforced by **`tests/test_invocation_contract.py`**
(`TC-ArgusAgent-CLI-001-35`..`-41`, `TC-ArgusAgent-DOCS-001-28`). The accepted surface is **derived at
run time from `argus/cli.py::build_parser`** — never transcribed — and compared against a declared
contract registry in **both directions**: a flag the parser accepts and no document specifies fails,
and a flag a document names and the parser rejects fails. Defaults and shapes are compared too, and
every divergence must be a **named exemption carrying its reason** (DN-8's `coverage_scope` case) rather
than silence. Each registry entry names its specifying site **by anchor text**, and the anchor must be
findable in that file — a registry is not a contract, a document is. Every `argus …` command line
committed in `README.md`, `action.yml` and `.github/workflows/*.yml` must parse through the live parser,
so a documented invocation that would give a consumer an argparse usage error fails here first. Because
the walk uses argparse private API, a non-vacuity assertion is mandatory (`-39`): an argparse-internals
change must turn this red, not silently green. **A red result when a new flag lands (`--deep`/FR36, any
MCP-era flag) is the guard working, not a defect** — registration is meant to cost a deliberate edit.
*(Amended 2026-08-15 by Story 12.7: the derivation is now a **closure over every sub-command** in
`_SubParsersAction.choices`. It was scoped to one hand-named sub-command — every call site passed the
literal `"audit"` — so a SECOND sub-command's flags were invisible to `-35`/`-37`/`-38`, which is
`DF-AUD-APAA-E` reconstructed by the guard written to close it. The parsed corpus also gains the shipped
command-asset tree `argus/assets/commands/*.md` **by glob**, with a `> 0` floor in `-39`, so a rename or a
move turns it red rather than silently shrinking the corpus.)*
*(Amended 2026-08-15 by Story 12.8 / FR37: the parsed corpus gains `docs/*.md` **by glob**, with its own
`> 0` floor in `-39` — `docs/first-run.md` is where a reader with no prior exposure copies their FIRST
command line from. `parse_failure` was CORRECTED at the same time: it read `SystemExit(0)` — argparse
ACCEPTING a line and printing help — as *"argparse rejected the documented command line"*, which made it
structurally unable to admit a documented `--help` invocation. A usage error still exits `2` and `2` is
still a failure there; the check is corrected, not loosened.
**`--help` PROSE is now under contract too, in the sibling module `tests/test_help_contract.py`**
(`TC-ArgusAgent-CLI-001-52`..`-54`) — split out along a cohesion boundary when this file crossed the
NFR-M1 ceiling, on the `tests/invocation_sources.py` precedent, with `live_actions` imported rather than
re-implemented. It holds every argument's RENDERED help against the LIVE `action.default`, so a default
stated in prose cannot drift from the one the parser holds; the mechanism is
`argparse.ArgumentDefaultsHelpFormatter` rather than a per-flag sentence, because a hand-typed default is
the AI-E9-7 transcription class one layer out from what `-35`/`-37` already close. Three help strings
additionally carry the operator-consequence fact their contract paragraph records (`--reports` is inert
without `--report-dir`; `--ignore-pattern` matches by bare substring; neither `--ignore-*` can suppress a
live production key), pinned by exact substring with the reason in the test.)*

**Operator-diagnosis enforcement** *(added 2026-08-15 by Story 12.8 / FR37, NFR-R1, AR10, NFR-S1)*: the
§A **error/degradation** rules above are enforced at the USER SURFACE, not only at the raise site.
`argus/reports/plain_english.py` holds the ONE diagnosis vocabulary — `TYPED_FAILURE_CLASSES` plus
`render_audit_failed_next_action`, the FR37 renderer Story 12.4 shipped and which had **zero production
callers** until this story wired it — and all three arms that print an audit failure (the CLI's audit
arm, the CLI's ship-readiness arm and the second invocation surface's) render from it, so one failure
cannot be described two ways. Three properties are enforced:
- **Every typed failure names a CAUSE and an ACT that changes it.** A cause-only message is a red light
  with no next action, which is what trains an operator to ignore it (FR37).
- **An INTERNAL DEFECT is distinguishable from an expected degradation** (`DF-8-4-D`, closed). The
  distinction is carried **from the wrap site** by `pipeline.UnexpectedStageError`, because
  `pipeline.py`'s stage wraps already converted any unexpected exception into a `PipelineError` — one of
  the classes the CLI enumerates as expected — so a CLI-only `except` split could not have told them
  apart. Exit stays `1` for both; the distinction lives in the message (AR3 frozen, AR7 reuse-never-fork).
- **No diagnosis carries an absolute host path** (NFR-S1). Enforced as a PROPERTY over the surface —
  `TC-ArgusAgent-CLI-001-61` drives the real failure paths with a `tmp_path` whose absolute string, in
  every spelling including the `repr`-escaped one, must be absent from stdout AND stderr.
Closed vocabularies (`--passes`/`--skip-pass`/`--reports`) are REFUSED inside `parse_args` against the
one definition of each; open ones (`--critical-subsystem`/`--exclude-critical`, `--reports` without
`--report-dir`) are DISCLOSED on stderr. And **a usage error is not a verdict**: a parser rejection maps
in `main()` — never in `build_parser` — to the reserved AR3 code `1`, because `action.yml` publishes exit
`2` as `NOT_READY_FOR_RELEASE assessed=true` and a typo was therefore fabricating an assessment for a run
that never happened. `--help` still exits `0`.

**Command-asset enforcement** *(added 2026-08-15 by Story 12.7 / FR35, second half)*: the §A rule
*"Command assets are data, not code — they instruct a host to invoke the CLI and introduce no execution
path of their own"* is enforced by **`tests/test_command_assets.py`** (verification area
`TC-ArgusAgent-ASSETS-001-01`..`-12`). Four claims, each derived rather than declared. **(1) Packaged:**
the assets are resolved through `importlib.resources` over a real package — never `__file__` arithmetic,
which breaks in a zip-imported or relocated distribution — and are asserted present in a freshly built
**wheel and sdist**, because those are built from different populations (the whole package directory
versus VCS-tracked files) and the asymmetry is silent. **(2) No authority:** every executable line in every
shipped asset is an `argus …` invocation the REAL parser accepts, no asset carries an interpolation
construct, and none enables the egress opt-in — a file placed in a user's configuration directory can
never constitute that operator act. **(3) Set equality:** the shipped set is DERIVED from the asset names
× the host registry, and every surface that publishes a command list is compared against it in both
directions, with the surface population resolved by **scanning tracked markdown** so a fourth list added
later is red rather than invisible, and with §3.4 struck spans excluded so an honest retraction stays
writable. **Exactly one** command-asset tree may exist in the repository — that is what forced the
`adapters/**` stubs to be resolved rather than left as a second source of truth. **(4) Containment and
FR34:** the one new write path refuses any target escaping the resolved destination root (`..`, an
absolute name, a symlinked configuration directory), and the instrument-status disclosure is **rendered at
write time** from the one constant — asserted absent from every committed asset AND present in every
written one, which is `-49`'s corrected shape at a new seam.

**Degradation-diagnosis enforcement** *(added 2026-08-10 by Story 10.4 / `DF-AUD-APAA-F`)*: the
§Error/Degradation rule above — *a degraded outcome records the cause it actually had, and a recorded
reason token names a remedy that works* — is enforced by **`tests/test_grammar_diagnosis.py`**
(`TC-ArgusAgent-INDEX-001-108`..`-119`, `TC-ArgusAgent-REPORT-002-25`..`-29`,
`TC-ArgusAgent-DOCS-001-29`). The token vocabulary lives in ONE pure module,
`argus/shared/grammar_status.py`, imported by the producer (`index/ast_index.py`) and the consumer
(`reports/generator.py`) alike, so neither side may re-parse a token with its own `startswith`. The
load-bearing half is a **closure over the code, not over a list**: the guard parses
`argus/index/ast_index.py` with the stdlib `ast` module, walks `_get_parser_for_lang`'s own control
flow, and rejects any handler that is bare, a lone `pass`, catches a signal, or catches a **redundant
tuple** whose members subclass one another — plus every exit must return a **registered**
`GrammarFailure`, so a **fifth** arm turns this red until it is registered *and* driven by the
behavioural matrix. Story 10.2's hand-written site list was wrong three times; a list closes today's
instances, a closure closes the class. Because a source-walking guard goes green by finding nothing, a
non-vacuity assertion is mandatory (`-118`): a rename or move of the loader must turn this **red**, not
silently green. `-29` asserts the rule text above and this registration are both still present.

**Delivery-closure enforcement** *(added 2026-08-11 by Story 10.5 / `DF-6-7-A`)*. **The rule, which this section establishes and which binds every future story: a V1 commitment is delivered only when a production call site reaches it — mapping to a module is not delivery, and a commitment with neither a call site nor a dated reclassification is a defect.** It is enforced by **`tests/test_v1_commitment_closure.py`** (`TC-ArgusAgent-DOCS-001-30`..`-41`) through **two closures that meet in the middle**, because neither closes the class alone. *Forward*: the population of V1 commitments is derived by **claim SHAPE across the whole `E-PRD/prd.md`**, never by section heading — the `standards_refs[]` commitment bound V1 at **three** coordinates while every planning document since 2026-08-03 named **one**, and the invisible site was invisible exactly because it sat under a heading nobody thought to sweep. Every atom must carry exactly one dated, reasoned disposition from a **closed** vocabulary, in both directions, so a disposition cannot outlive the claim it disposed. *Reverse*: FR ids are enumerated by shape from §Functional Requirements, every FR carries one delivery disposition, and **`wired` is PROVEN, never asserted** — the guard builds the `argus/**` import graph **statically** (stdlib `ast`, source read as text, **no `import argus`**: lazy imports would defeat a runtime walk, optional extras would make CI legs disagree, and a test that executes no `argus` line cannot perturb the coverage figure) and refutes any `wired` claim over a module outside the closure from `argus/cli.py`. **Symmetrically**, a `library-seam` disposition over a module that IS reachable fails, so when Story 12.1 or 12.3 wires a seam this goes red until the disposition is updated — **that red is the guard working.** The walk is a **closure device that forces a classification, never the classifier**: *module unreachable* is not *FR undelivered* (~~FR27 holds by determinism while its memoization mechanism is unwired~~ — **superseded 2026-08-13 by Story 12.3, which WIRED that mechanism; FR27 is now disposed `wired` and the worked example of the asymmetry is FR20/FR23/FR24/FR26/FR29, not FR27**), and a guard that equated them would manufacture the false accusations this product exists to prevent. Because both closures go green by finding nothing, non-vacuity is mandatory (`-39`): a heading rename, a package move or an `ast.parse` failure must turn this **red**. `-38` additionally pins the items this story was most likely to close by accident — H0's unfiled Minions handoff and `DF-7-2-A`'s open adjudication — so the guard defends against its own author, and `-41` asserts the rule text above and this registration are both still present.

**Instrument-status enforcement** *(added 2026-08-11 by Story 11.1 / FR34)*. **The rule: no verdict surface ships without disclosure — every user-facing surface that emits a verdict also states how the tool's own findings have been validated, and the tool cannot emit a verdict on a surface that omits it.** Instrument status is NOT the run grade, and the distinction is the load-bearing half: `grade: demo-heuristic-only` describes how a single RUN was configured and is removed by engaging the deep pass; instrument status describes how the tool's FINDINGS have been validated, varies per tool VERSION, and is removed by Epic 13 clearing the >=80% precision gate — nothing else. Merging them would mislabel a deep run and, far worse, make the disclosure appear to lift when a user enables a flag, so the `DOGFOOD_EXTERNALIZATION_GUARD` sentence is deliberately NOT reused; what is widened to the user-facing surface set is the two-sided (presence AND over-claim-absence) GUARD MECHANISM, by IMPORTING `_affirmative_over_claims` from `tests/test_release_surface_honesty.py` rather than re-authoring a substring scan that would reopen the trailing-negation escape `-17b` closed. The vocabulary is a CLOSED two-member enum in ONE existing pure module, `argus/verdict/negative_assurance.py`, beside the FR17 `DISCLAIMER` it is the sibling of — FR17 bounds *this audit*, FR34 bounds *the instrument*, and both apply, because an audit can be perfectly scoped and still be produced by an unvalidated instrument. It is enforced by **`tests/test_instrument_disclosure.py`** (`TC-ArgusAgent-DOCS-001-42`..`-52`, `TC-ArgusAgent-CLI-001-50`..`-51`, `TC-ArgusAgent-REPORT-002-30`..`-32`) through **two closures**, because a surface LIST closes today's instances and this project has re-measured five hand-counted enumerations and found all five wrong. *Code side*: the guard parses `argus/reports/generator.py` with the stdlib `ast` module and requires every `write_text` call inside `generate_reports` — the single write point for all four report artifacts — to receive a value produced by the disclosure helper, so a **fifth** report added without it turns this red. *Non-code side*: the listing/note surfaces are resolved by glob and compared **against the constant**, never transcribed (AI-E9-7), with the one-line summary fields carrying a shortened constant whose SUBSTRING relation to the full text is itself asserted. ~~The MCP surface does not exist and this story does not build it (FR35 is Story 12.6's); instead a registered pin fails the day an MCP module, entry point or extra appears without being a registered disclosure surface — **that red is the guard working**.~~ **RESOLVED 2026-08-15 by Story 12.6** (struck above, not deleted — §3.4): the MCP surface EXISTS (`argus/mcp/**`, entry point `argus-mcp`), and the pin fired on its first commit exactly as designed. `_MCP_DISCLOSURE_SURFACES` is populated and `TC-ArgusAgent-DOCS-001-49`'s registered-surface loop — which had **never executed** (`# pragma: no cover - empty until 12.6`) — was CORRECTED at the same time, and the correction is recorded rather than made quietly: **as written it asserted the literal disclosure text was a substring of the registered module's SOURCE**, which would have forced a transcribed copy of the constant into `argus/mcp/**` — the exact AI-E9-7 drift this regime exists to prevent, demanded by the guard that exists to prevent it. It now asserts three DERIVED things instead: that no registered Python module contains the constant's text at all; that every function on a registered surface which renders a verdict (derived as *calls `summary_line` or `render_ship_readiness`*, never declared per file) also calls `render_instrument_disclosure` — the `-31` `unrouted_write_text_calls` device at this seam, so a SECOND verdict renderer added later without the disclosure turns it red with no registry edit; and that a listing surface discharges by carrying the text — with a `> 0` non-vacuity floor on routed functions so the loop cannot return to proving nothing. The status is declared WITHOUT importing `argus/precision/replay_harness.py`, whose module-level `sys.path` insert and `from _registry import ...` are Story 11.5's wheel defect and must never reach a user-facing path; a static import walk (no `import argus`) asserts that non-reachability, and a committed guard imports the harness — tests may — and asserts the two AGREE: the declared status is *not independently validated* if and only if no production call site passes `protocol_cleared=True`, with the test-side call sites exempted BY NAME with their reason. **That is the expiry, mechanised**: when Story 13.3 passes `protocol_cleared=True`, the guard goes red until the disclosure is **replaced** by the cleared statement — the surface never becomes silent and the enforcing test never becomes vacuous (FR34.4). Because both closures go green by finding nothing, non-vacuity is mandatory: written reports, resolved surfaces and `write_text` calls found each carry a `> 0` floor, so a rename, a module move or an `ast.parse` failure must turn this **red**. `-51` additionally proves the guard cannot pass vacuously once the token changes — it renders the *validated* member and asserts every surface would go red against it — and `-52` asserts this registration is still present.

**Name-classification enforcement** *(added 2026-08-11 by Story 11.2 / `DF-8-2-B`)*. **The rule: a name-based classification convention matches a WORD, never a letter sequence — every registered convention carries a real word boundary, and an entry without one fails CI.** The boundary is whatever that ecosystem actually uses: a leading `_` or `.` for a suffix convention, an uppercase initial for a case-sensitive one (Java's separator IS the CamelCase capital — Maven Surefire's four defaults are all CamelCase, so spelling the convention `"_test.java"` would delete every Java true positive, and lowercasing the basename before matching destroys the only boundary the name has), or whole-name equality for a basename rule. It is enforced by **`tests/test_classification_word_boundary.py`** (`TC-ArgusAgent-DETECT-001-96`..`-99`, `TC-ArgusAgent-PIPELINE-002-10`..`-13`, `TC-ArgusAgent-DOCS-001-53`, plus `TC-ArgusAgent-DETECT-001-100` in `tests/test_vacuous_detector.py`) over the tier structure declared exactly ONCE in `argus/detectors/vacuous_test.py` and READ by both public predicates (AR7/§3.3 — the guard never transcribes a table, and no second classifier is forked into `pipeline.py` or `reports/`). **Why a closure and not the list of three fixes:** the defect was documented as *two* entries by four planning documents and was **three** — the sixth hand-counted enumeration in this project to be re-measured and found wrong. So `-97` reads the tables out of the module and requires every entry to carry a REGISTERED boundary, failing while naming itself; `-98` **synthesizes** each adversarial near-miss from those same tables and asserts BOTH directions, because a change that removed the false positives by deleting the conventions would pass a one-directional check; and `-99` closes over the GROUNDED LANGUAGE SET derived from `argus/shared/source_languages.py`, so every language either carries a convention or is a **registered exemption carrying its reason** (today exactly `c` and `php`, filed as `DF-11-2-B`). That closure **forces a decision and does not authorise adding a convention**: the missing conventions are false NEGATIVES, a different defect class that would MOVE classification on real repositories, filed as `DF-11-2-A` rather than fixed. What made this release-blocking rather than cosmetic is measured, not argued: a production `.java` file Argus assesses CRITICAL was excluded from the FR4 critical set under the false reason `test_file`, **emptying** the set, so FR16's *"all critical subsystems deep"* clause was satisfied **vacuously** — a false green in the fatal direction (inversion F1), pinned by `-12`. `-10`/`-11` **re-prove** the Story 8.2 AC7 invariant across both constants rather than assume it survived: behaviourally over a polyglot fixture, and structurally by an `ast` walk of `argus/pipeline.py` (read-only) showing `is_test_file` is evaluated once per file and the same value reaches `_critical_ineligibility` on both the fresh and the resume path — a **third** derivation is the one mechanism by which the two stages could come to disagree, and it turns this red. Because every closure goes green by finding nothing, non-vacuity is mandatory: tables resolved, registrations read, adversarial pairs synthesized, languages enumerated and functions parsed each carry a `> 0` floor, so a rename, a constant move or an `ast.parse` failure must turn this **red**, and `-10` additionally proves its own invariant assertion FIRES by running it against a synthetic disagreement. `-53` asserts this registration is still present.

**Toolchain-validation enforcement** *(added 2026-08-12 by Story 11.4)*. **The rule: Argus does not vouch on top of a parsing toolchain it has not checked — an unvalidated parser withholds a verdict rather than computes one.** Every other verdict Argus emits was already defended (the floor against too little coverage, row 2 against blocking findings, cross-cutting #6 against a wrong 🔴); **nothing defended against a wrong 🟢 caused by the parser itself.** It is enforced by **`tests/test_grammar_runtime_validation.py`** (`TC-ArgusAgent-INDEX-001-120`..`-127`, `TC-ArgusAgent-REPORT-002-33`..`-34`, `TC-ArgusAgent-DOCS-001-54`..`-55`). **The check is BEHAVIOURAL, not a version comparison, and that is the load-bearing decision** — measured, not argued: the demonstrated false green happens at an **IN-BOUND** `tree-sitter 0.25.2`, so `assert tree-sitter < 0.26` would be green on the exact tree where the defect is live; the epic's stated reason for that pin was separately re-measured and found **false as written** (see §Packaging above); and grammar packages drift independently of the core — this host runs ten grammars across **four** different minor lines, all in bound — so a single core version number tells you nothing about the nine packages that actually produce the nodes. What ships instead is a **per-`(language, entry point)` canary**: a pinned snippet parsed through the **real** loader seam (`_get_parser_for_lang`, ARM 5) whose extraction is compared against a frozen expectation in the pure `argus/shared/grammar_status.py`, with the declared version range checked as a **second, independent** signal (`-127` proves the bound fires on its own; `-125` proves the behavioural check fires on its own at an in-bound version — neither is sufficient alone). The observable is the **live intersection of the parsed tree's node types with Argus's own extraction tables**, not merely the extracted output, and that distinction is what keeps the corpus honest in two directions at once: it catches a drifted grammar *and* a drifted table, and it stays non-empty — therefore falsifiable — for the **four** languages (`c`, `cpp`, `ruby`, `rust`) that legitimately extract **zero definitions** on this tree under the open, filed `DF-10-2-A`. A canary asserting "≥1 definition" uniformly would fire on four **healthy** grammars and take every polyglot audit to `INSUFFICIENT_COVERAGE` — a false-green fix that ships a mass false red — so `-123` pins those four **by name**. The degradation reuses the machinery that exists rather than inventing a second one (AR7/§3.3): a fifth `GrammarFailure` member, `RUNTIME_UNVALIDATED`, recording the unsuffixed token `tree_sitter_runtime_unvalidated` and degrading through the **existing** floor row, so `verdict_gate.py` and `pipeline.py` are byte-unchanged and no row, threshold or exit-code mapping moves. It also closes **`DF-10-4-E`**: `_render_grammar_remedy`'s trailing unconditional fallthrough is now an explicit final arm plus a `raise`, so a sixth cause can never silently render a fifth's remedy, and `-33` drives all five causes to the operator surface and proves an unregistered member raises. Because every guard here goes green by finding nothing, non-vacuity is mandatory: `-121` refuses an empty pinned vocabulary, `-122` counts canary executions inside a **real** `build_ast_index` call and requires a non-zero count (and exactly one per language, so the existing load cache still bounds the cost), and `-124` closes the corpus over `LANGUAGE_BY_SUFFIX` in **both** directions so an eleventh language cannot escape the check — `canary_for` fails **closed**, so that red is the guard working. Above all, `-125` keeps the defect itself permanently reproducible: it reconstructs the **pre-fix** loader in memory and asserts the false green still appears there (`RELEASE_READY`/exit 0) with `deep_ratio` **unchanged**, before asserting the fix removes it. A test written after the fix, over a defect never demonstrated, is `AI-E3-1` — a keystone test green over its own keystone bug — and this file refuses to be one. `-55` asserts the corrected premise carries its correction everywhere it was written.

**Module-size enforcement** *(added 2026-08-12 by Story 12.1 / `DF-8-2-A`)*. **The rule: NFR-M1's ≤1200-line ceiling holds over EVERY tracked `.py` file in this repository — `argus/**` and `tests/**` alike — and an exception is a named, dated, reasoned and FILED exemption that expires, never a narrowed population and never silence.** It is enforced by **`tests/test_module_size_ceiling.py`** (`TC-ArgusAgent-MAINT-001-01`..`-05`, a NEW verification area), and it replaces the §Enforcement claim corrected at the top of this section — the file-size CI that claim named had never been built, and the `tests/apaa/` directory it said held it does not exist. **Why a population and not another per-module line:** the ceiling was already asserted **eight** times, file by file, by the tests that happened to think of it (`test_cache_invalidation.py`, `test_cartridge_selfaudit.py`, `test_dogfood_module_split.py`, `test_dogfood_plan.py`, `test_dogfood_proof.py`, `test_evidence_bundle.py`, `test_hitl_escalation.py`, `test_memo_store.py`) — and **not one of them covered `argus/pipeline.py`**, which is precisely why it drifted 131 lines past the cap across four epics with every gate green. A rule that is stated, locally asserted, and structurally unable to see the one place it is broken is this project's dominant defect class (`AI-E11-1`); the answer is a **closure over `git ls-files -- '*.py'`**, re-derived every run, never a list. The population is the git **INDEX** deliberately, so a module is swept the moment it is `git add`-ed (the mirror-image blind spot — a module never staged — is measured and filed as `DF-12-1-D` rather than left unsaid). **The breach was NOT confined to `argus/**`**: re-measured 2026-08-12, **four** of 169 tracked files exceeded the cap (`argus/pipeline.py` 1331, `tests/test_pipeline_signature_demo.py` 1326, `tests/test_v1_commitment_closure.py` 1308, `tests/test_grammar_diagnosis.py` 1203), and test files are unambiguously in scope because this repository's own per-module assertions say *"this test file is ≤1200 lines"*. Narrowing the sweep to `argus/**` until it went green was rejected as the exact move this project files as a defect; the three test files are `_EXEMPT_BY_DESIGN` entries carrying a reason, an ISO date, an owner and a `deferred-work.md` id (`DF-12-1-A`/`-B`/`-C`), and `-04` makes the registry **shrink**: an exemption naming a file that no longer exists **or that is no longer over the cap** fails, so it can never become a parking lot, and `argus/pipeline.py` is asserted to be unaddable to it. Because a sweep goes green by finding nothing, non-vacuity is mandatory: `-01` refuses an empty, one-sided or partly-missing enumeration (a broken glob turns it **red**, not silently green), `-03` pins the boundary in both directions through the sweep's **own** predicate (exactly 1200 passes, 1201 fails), and `-05` **generates** an over-ceiling adversarial variant of **every file in the live population** and requires the predicate to flag each one, with the count asserted. The rule was made true in the same change that corrected the claim: `argus/pipeline.py` went 1331 → 944 by extracting `argus/pipeline_stages.py` under the Story 6.3 `DN-PIPELINE-SPLIT` doctrine, proven a pure restructuring by byte-identical moved definitions and a byte-identical 848-file `.argus/` and 4-file report A/B across the change.

**Dogfood-artifact currency enforcement** *(added 2026-08-12 by Story 12.1, closing `DF-8-5-B` + `DF-10-4-D` together)*. **The rule: a committed auto-generated artifact may not describe a tree that no longer exists — an artifact is CURRENT iff the provenance sha it cites is a real commit AND an ancestor of `HEAD`, and `argus/**` has not changed since that sha; and any guard that can go red on staleness must name the regeneration entry point in its failure message.** It is enforced by **`tests/test_dogfood_artifact_currency.py`** (`TC-ArgusAgent-DOGFOOD-001-49`..`-52`) plus the remedy sentence now carried by all five committed-artifact assertions in `tests/test_dogfood_plan.py` and `tests/test_dogfood_proof.py`, and the remedy it names — **`python scripts/regenerate_dogfood_artifacts.py`** — is a real committed entry point that re-renders all three artifacts through their **own** renderers and refuses to run on a dirty `argus/` tree. **Why the entries' own stated remedy was necessary and NOT sufficient:** both describe the class as guards that break too often, and both are right; but measured at `ca37283` on 2026-08-12 the **silent** direction was live and worse — all three committed artifacts were **already stale** (provenance `a9cc933` vs `ca37283`, total LOC 19783 vs 20454, cut edges 57 vs 64, unit-2 LOC 14793 vs 14997, unit-3 3660 vs 4127, the NFR-C1 ratio `360/19783` vs `60/3409`) **while all five assertions were GREEN**, because `-03`'s docstring claimed *"the artifact cannot silently rot away from the generator"* and its code checked three tokens. So *"name a regeneration entry point in the failure message"* improved a red that never appeared. `-03` and `-20` are **widened** to the derived figures their docstrings always promised (population, total LOC, per-unit file counts and LOC) — a strengthening, which `DF-8-5-B` welcomes; **no assertion was loosened or deleted**, which it forbids. The currency property is a **closure over the real `argus/**` content delta**, not over tokens the artifact happens to contain, and it was RED-first **for free** on the live defect with no reconstruction; it does not fail always, and `-52` proves both halves from live history on every run by classifying every commit reachable from `HEAD` with the same predicate and requiring **both** classes to be non-empty. `-51` closes the registry over the artifact directory by glob, so a fourth committed artifact cannot escape the rule by being new, with the frozen Story-7.2 superseded record exempt **by name with its reason**. It also mechanises the operator ruling of 2026-08-12 (*"every regenerated artifact must cite a truthful provenance sha that is an ancestor of HEAD"*) into an assertion, and it settles the provenance/enumeration split `DF-10-4-D` asked to be decided: the renderers now **label the enumeration honestly** (the population comes from the git index; the commit descriptor is `git rev-parse HEAD`), and the guard fails unless those two trees agree over `argus/`. `TC-ArgusAgent-DOCS-001-59` asserts both registrations above are still present.

**Opt-in egress enforcement** *(added 2026-08-13 by Story 12.2 / FR36 / NFR-S6)*. **The rule: no egress path is reachable without an EXPLICIT INVOCATION-LEVEL opt-in, and neither an environment variable nor a packaging extra constitutes one.** It is enforced by **`tests/test_no_web_imports.py`** (`TC-ArgusAgent-PIPELINE-001-10`..`-12`, `TC-ArgusAgent-AUDIT-001-62`) and **`tests/test_deep_pass_wiring.py`** (`TC-ArgusAgent-AUDIT-001-60`..`-72`). **Why the negative half of the rule is the load-bearing half, measured rather than argued:** this document asserted egress was *"behind the opt-in `[llm]` extra"*, and it is not — the extra contains only `litellm` while `httpx` is a BASE dependency, so a no-extras install already ships a complete egress path (corrected in §Packaging above). Independently, `OpenLLMAdapter.__init__` silently absorbs **six** environment variables and defaults its API key to the literal `"mock-key"`, so merely CONSTRUCTING the adapter is already a configuration decision taken by the ambient environment. Neither packaging nor the environment can therefore be consent; the opt-in is `--deep-audit`, a registered flag in the LOCKED invocation contract, `store_true`, default `False`. **The forbidden surface and the entry-point population are DERIVED from the package, never listed** (`AI-E10-5`): the hand-written forbidden tuple omitted `argus/audit/open_llm_adapter.py` — the one module that can open a socket — and the hand-written entry-point tuple `(models, pipeline, cli)` had never learned about `pipeline_persist.py` or `pipeline_stages.py`, so two thirds of the pipeline surface sat outside the gate; `-12` proves the derivation non-vacuous by GENERATING a new `argus/audit/*` module and requiring it to be covered with no registry edit and a count that grows by exactly one. `-62` derives the environment-variable population by an `ast` walk over the adapter's own `os.getenv` calls — so the seventh variable someone adds is covered the day it lands — and proves that with every one of them set to a live-looking value and the flag absent, the run loads no dispatch surface at all. The one legitimate live-egress observation is the **absence** of one: every test dispatches through an injected `FakeDispatch` (NFR-D2, zero tokens) and none contacts a provider. Egress is disclosed **before the first byte** and the gate proves the ORDERING, not the presence of a sentence — the fake port snapshots the disclosure stream at the moment `dispatch` is ENTERED (`-65`), because a check that the final stdout contains a provider name cannot distinguish *before* from *after*. `TC-ArgusAgent-DOCS-001-60` asserts this registration is still present.

**Deferred-import positive-control enforcement** *(added 2026-08-13 by Story 12.2 / `AI-E11-1`)*. **The rule: an import-absence gate over a DEFERRED code path must carry its positive direction — a guard that is green because the code it guards never executed is not evidence, and must be paired with an observation that the guarded thing DOES happen when it is supposed to.** It is enforced by **`tests/test_no_web_imports.py`** (`TC-ArgusAgent-PIPELINE-001-11`), which runs both directions in a FRESH subprocess each. **Why this rule exists at all is that Story 12.2 created the hazard deliberately.** FR36 needs two properties that read as opposites: `argus.audit.deep_audit` must be in the STATIC import closure from `argus.cli` (that is what makes its `wired` disposition PROVEN by `TC-ArgusAgent-DOCS-001-34` rather than asserted), and it must be ABSENT from `sys.modules` after a default run (NFR-S6). A **function-local import satisfies both**, because `build_import_graph` walks with `ast.walk`, which descends into function bodies, while the statement itself never executes on a default run. The cost is exact and was stated before the code was written: from that moment `TC-ArgusAgent-PIPELINE-001-10` is green **by construction**, for a reason that has nothing to do with safety. The positive control is what converts that green into evidence — opt-in absent → the seam is not loaded; opt-in present → it IS — and without it the quarantine would assert only that unreached code does not run. **This generalises beyond FR36**: the same shape is the deferred-import form of the vacuous guard the Epic-11 retrospective named this project's dominant defect class, and any future story that defers an import to satisfy a quarantine owes the same pairing. `TC-ArgusAgent-DOCS-001-60` asserts this registration is still present.

**GUARD-ADEQUACY CLAUSE** *(added 2026-08-16 by Story 13.2 / AC8.4, closing `AI-E12-5` — asked by the Epic-11, Epic-12 and two earlier retrospectives; **fourth consecutive request, first registration**)*. **The rule: for every committed guard, the story states (i) the guard's OBSERVABLE, (ii) a demonstration that the defect MOVES that observable — RED at the REAL SEAM, not against a reconstruction — and (iii) at least one adversarial variant GENERATED from the grammar, registry, table or record the guard closes over, with its count, rather than hand-listed. The question in all three parts is one question: *can the defect exist while my observable is unchanged?*** It carries an **input-side twin** the Epic-12 retrospective §3.5 measured and this registration adopts with it: **a guard over the SHAPE of an input is not a guard over its EFFECT** — validating that an input parses, is well-formed, or matches a registry says nothing about what the system does with it, and the two are routinely conflated by guards that were written while thinking about the input. It is enforced by **`tests/test_governance_record_integrity.py`** (`TC-ArgusAgent-DOCS-001-77`) which asserts this rule's text is present in this section, and it is APPLIED — with (i)/(ii)/(iii) discharged in each guard's own docstring — by `tests/test_gate_flip_path.py` (`TC-ArgusAgent-PRECISION-001-32`..`-38`) and `tests/test_adjudication_record.py` (`TC-ArgusAgent-PRECISION-001-39`..`-52`). **Why it is registered by Story 13.2 rather than by the Architect it was assigned to:** `AI-E12-5` names the reason itself — *"Story 13.3 asks for a non-vacuity proof on the single most consequential guard in the project, and the rule that answers it has been unregistered for three epics"* — and 13.2 is the story immediately before it, and the story that builds the guard 13.3 must prove non-vacuous. **Why registration is not ceremony, measured rather than argued:** the Epic-11 retrospective identified the vacuous guard as this project's dominant defect class from five instances; Epic 12 then produced **eleven** more with the rule unregistered; and the class has now been demonstrated twice inside Epic 13 itself — `TC-ArgusAgent-DOCS-001-75` **required** a stale literal (`N = 0`) and so *enforced a falsehood* while staying green (13.1 code review R1), and `compute_precision` reported a **cleared** gate for a corpus that emitted nothing at all, with the entire precision suite green (13.2 / AC1b). A rule that is stated, locally applied, and structurally unable to see the place it is broken is exactly the shape this clause exists to refuse. **Two rules that remain UNREGISTERED and are NOT registered here, recorded so the count is honest** (`AI-E11-8`): workflow input containment (Story 11.3) and built-artifact inspection (Story 11.5). Both are outside this story's write set — neither concerns the precision gate — and re-homing them is recorded in `deferred-work.md` under `AI-E11-8` with a named owner rather than left to a fifth retrospective to re-ask.

**Adjudication-record enforcement** *(added 2026-08-16 by Story 13.2 / AC3, closing the `DF-6-6-A` / `DF-7-2-A` instrument half)*. **The rule: the >=80%-precision externalization gate may be cleared only from a COMMITTED, append-only, machine-readable adjudication record in which every emitted blocking finding carries exactly ONE LIVE disposition attributed to a human role `precision-validation-protocol.md` §2 registers; a partial, unattributed, non-reproducible or empty record yields `Unevaluable`, RECORDED with its residual count — never a pass over the adjudicated subset, and never a silent skip.** It is enforced by **`argus/precision/adjudication.py`** (the properties are structural: `AdjudicationRow.__post_init__` raises on an unregistered disposition, on an unregistered adjudicator role, on an absolute/backslash locator, and — the load-bearing direction — on an `UNADJUDICATED` row that carries an adjudicator id, so an automated producer that began filling in the named human's judgements fails at CONSTRUCTION) and asserted by **`tests/test_adjudication_record.py`** (`TC-ArgusAgent-PRECISION-001-39`..`-52`). **Four supporting properties, each of which was a live defect before this story:** (a) `n` counts the population that was actually folded — a 2-member injected corpus reported `N=7`; (b) an empty precision denominator is `UNEVALUABLE`, not the `Fraction(1, 1)` convention that read as *"cleared"*; (c) §5's clean-repo blocking-FP condition NAMES its population and reports NOT APPLICABLE where no member can satisfy it, because a condition that cannot fail is not a threshold; (d) the record carries the `protocol_version` it was adjudicated under and a guard asserts it equals the change log's current head, so amending the protocol after a run turns the suite red instead of silently reinterpreting it. **The arithmetic is shared, not forked** (AR7): `precision_fraction`, `gate_is_provisional`, `PRECISION_GATE_THRESHOLD` and `precision_gate_status_for` are the same objects the cartridge fold uses — one arithmetic, two populations. `TC-ArgusAgent-DOCS-001-77` asserts this registration is still present.

**Gate-decision enforcement** *(added 2026-08-17 by Story 13.3 / AC1, extending Adjudication-record enforcement above)*. **The rule: the outcome of the >=80%-precision externalization gate is recorded in a CLOSED THREE-MEMBER vocabulary — `CLEARED` / `NOT_CLEARED` / `BLOCKED` — that RAISES on an unregistered member; `NOT_CLEARED` may be recorded ONLY when the measurement RAN (the record is byte-reproducible AND exhaustively adjudicated AND the precision denominator is non-empty), and `BLOCKED` — which is NOT a §5 outcome — may never be rendered, serialized, summarised or committed as *"the gate did not clear"*, in any artifact, in any wording.** *A gate that did not clear because findings were judged and enough of them were false is a **measurement**; a gate whose adjudication has not terminated is an **absence**.* A two-member vocabulary cannot tell a reader which happened, and every downstream surface inherits the ambiguity — permanently, because the artifact outlives the story. **Two further clauses ride with it:** (a) protocol §5's four conditions are reported **individually**, each with its own measured value, its own verdict from a closed verdict vocabulary and its own countable *"what would close it"* — never as one boolean, and `NOT_APPLICABLE` is not a synonym for `MET` (a `CLEARED` decision carrying a non-`MET` condition RAISES at construction, which is §5's *"it may not count it as met by default"* made unexpressible rather than written down); (b) **the result DISCLOSES THE CONCENTRATION OF ITS OWN DENOMINATOR** — contributing members vs. ratified members, per-member finding counts and the distinct rule-class count — **derived, never typed** (`DF-8-5-C` / `AI-E9-7`), in **both** branches, because §5's `N >= 5` is satisfied by member COUNT while the ratio is computed over whichever members contributed, and *the N that gates and the N that contributes are different numbers*. The disclosure is **not** a distribution requirement: the concentration is disclosed, never corrected by narrowing the corpus, which would be a threshold change wearing a hat. It is enforced by **`argus/precision/gate_decision.py`** and **`argus/precision/gate_disclosure.py`** (structural: `GateDecision.__post_init__` raises on an unregistered outcome, on a condition set that is not exactly ~~§5's four in §5's order~~ **AMENDED 2026-08-20 by Story 16.1 / AC1 — STRUCK, never erased (§3.4): §5's conditions in §5's order, a set that is now FIVE and that §5 amends by dated ADDITION — the count is derived from `SECTION_5_CONDITIONS` in the refusal's own message so a further amendment does not require editing a shipped gate's error text**, on `CLEARED` with a non-`MET` condition, on a `BLOCKED` decision carrying no closure path, and on any §5 outcome recorded over a fold that is not evaluable; ~~`decide_gate` raises `VacuousDecisionError` on an empty record or an empty emitted population BEFORE asserting anything about them~~ **AMENDED 2026-08-18 by Story 13.5 / AC5 — STRUCK, never erased (§3.4): `decide_gate` still raises `VacuousDecisionError` on an empty record unconditionally, and still raises on an empty EMITTED POPULATION that carries no positive corpus-read proof; but an empty emitted population accompanied by a `CorpusReadProof` whose every conjunct holds — members audited at their PINNED shas with each staged file proved against the pin by git's own blob hash, source files scanned, test functions scored, two runs byte-identical — is ADMITTED and returns `BLOCKED` with protocol §5's precision condition `UNEVALUABLE`. **The floor is narrowed, never removed, and both directions are guarded** (`TC-ArgusAgent-PRECISION-001-69`), because the unconditional form conflated *"the corpus could not be read"* with *"the corpus was read and nothing was promoted"*, and Epic 14's corrected detector made the second one real: 1,960 in-scope source files at the pins, 5,129 test functions scored, 4,284 advisory findings emitted, **0** promoted to verdict-eligible. As shipped, that outcome was INEXPRESSIBLE by the instrument built to record it) and asserted by **`tests/test_gate_decision.py`** (`TC-ArgusAgent-PRECISION-001-53`..`-64`). **Measured on the day it landed, which is why it is a rule and not a preference:** the committed record held 26 TP/FP dispositions and **5 `BORDERLINE`** whose §4 ladder had not terminated, so the fold was `Unevaluable` — and folding it anyway would have produced a confident, fully-green *"the gate did not clear"* drawn from an adjudication nobody finished, in wording no downstream reader could distinguish from an honest shortfall. `TC-ArgusAgent-DOCS-001-77` asserts this registration is still present. **⚖️ AMENDED 2026-08-20 by Story 16.1 / AC1 — a FIFTH §5 condition: THE DENOMINATOR MUST BE BROAD ENOUGH TO MEAN SOMETHING.** **The added rule: the precision ratio is EVALUABLE only over a population drawn from at least `(VALIDATION_SET_FLOOR_N + 1) // 2` DISTINCT CONTRIBUTING members of the ratified repository corpus; below that, §5's PRECISION condition is recorded `UNEVALUABLE` with the counts that made it so and the outcome is `BLOCKED` with a countable closure path — while the breadth condition's OWN verdict is `MET` or `FAILED`, because it WAS evaluated over a named population and a measured result is not an unobservable one.** Clause (b) above already required the concentration to be DISCLOSED; **this is the clause that lets the record act on it.** It is enforced by **`argus/precision/gate_breadth.py`** (the floor is a FUNCTION of the one locked floor, never the integer it evaluates to; the predicate is pure; the counts are READ from the very `ConcentrationDisclosure` the decision publishes, never recounted, so the threshold and the disclosure cannot disagree) and asserted by **`tests/test_gate_breadth.py`** (`TC-ArgusAgent-PRECISION-001-82`..`-85`), whose populations are GENERATED one per contributing-member count and which assert **where the verdict flips**, not merely that it has two values. **The positional read is repaired in the same change** — `decide_gate` read its own recorded-cleared verdict as `conditions[3].verdict`, correct for four conditions in §5's order and a latent FALSE GREEN the moment §5 is amended by addition, since an index returns a well-formed verdict belonging to another condition with no shape a reader, a schema or a guard could notice; it is now `section_5_condition(conditions, <id>)`, which RAISES (`TC-ArgusAgent-PRECISION-001-80`/`-81`). **The RULE-CLASS arm was derived and deliberately NOT landed** (operator decision, XAgent007, 2026-08-20): measured by two independent instruments, the maximum achievable distinct verdict-eligible rule-class count is **1**, so a floor of ≥2 would be a shutdown rather than a strengthening and a floor of 1 could not fail — filed as `DF-16-1-A`, with the count still disclosed on every decision. **No change-log version was taken:** the amendment sits under the existing V1.3 because the committed record carries 31 human judgements made under it, and re-stamping them would be the re-interpretation `decide_gate`'s own refusal names.

**Corpus-pin provenance enforcement** *(added 2026-08-18 by Story 13.5 / AC1, extending Gate-decision enforcement above)*. **The rule: a validation-corpus member is audited from the bytes of its PINNED GIT OBJECT, and the runner REFUSES BY NAME when the materialized bytes cannot be shown to be the pinned bytes.** Until this rule the pin was enforced by comparing `git rev-parse HEAD` to the manifest sha and the snapshot was then staged from **working-tree** bytes — two different claims. **Measured on the day it landed, which is why it is a rule and not a preference:** `agent-smith` sat exactly on its pin with six dirty in-scope sources, so an audit labelled `agent-smith@9ab774d7` measured the pin plus uncommitted edits and still reported `byte_reproducible_across_two_runs = True` — two runs over the same wrong bytes are reproducible. ***Reproducibility is not provenance.*** It is enforced by **`scripts/pinned_corpus_snapshot.py`** (`pinned_tree` reads `git ls-tree -r <pin>`, never the index; `materialize_pinned_bytes` writes blobs read with `git cat-file --batch`; `verify_pinned_bytes` re-hashes every staged file with git's own blob identity and `PinVerification.proves_pinned_bytes` is False on a count mismatch, a missing file or a one-byte difference — and False over an empty population, because 0 of 0 passes forever) and by **`scripts/audit_validation_corpus.py`** (`PinUnreachable` is a NAMED `Unevaluable` outcome for a member and never a fallback to the working tree; a Windows `MAX_PATH` overrun is a refusal BEFORE the write, because a partially-extracted tree audits clean). It is asserted by **`tests/test_pinned_corpus_snapshot.py`** (`TC-ArgusAgent-PRECISION-001-65`..`-68`), whose adversarial variants are GENERATED by mutating a real materialized snapshot rather than by constructing a fake verification. **No corpus member's working tree is ever mutated** — no `checkout`, no `stash`, no `clean`, no `worktree`: the ratified checkouts belong to other projects and `ls-tree` + `cat-file` are pure reads. `TC-ArgusAgent-DOCS-001-77` asserts this registration is still present.

**Ledger-claim cross-check enforcement** *(added 2026-08-16 by Story 13.2 / AC8.2, closing `AI-E12-6`)*. **The rule: a story record that claims a `DF-*` ledger closure is checked against the ledger — a claimed closure `deferred-work.md` never received fails CI, and the check is over the EXISTENCE of the disposition, not over the `+n / -0` shape of a write.** It is enforced by **`tests/test_governance_record_integrity.py`** (`TC-ArgusAgent-DOCS-001-78`), which extracts every `DF-*` a story file claims to close and requires `deferred-work.md` to carry a matching dated disposition, with a non-vacuity floor (`> 0` claims extracted) so a broken extractor goes red rather than silently green. **Why this rule and not a reviewer instruction:** Epic 12 produced **four** instances — Stories 12.4 and 12.5 recorded closures of `DF-8-3-A`, `DF-10-4-A`, `DF-10-4-B` and `DF-12-3-A` that the ledger never received — and **every review passed them**; the reviews that did check the ledger checked the shape of a write, never its existence. The Epic-12 retrospective asked for this guard *"before 13.2 files its adjudication record"*, and the reason is exact: 13.2's entire deliverable is a recorded governance claim of precisely this shape, so a story that filed one while its own ledger claims went unchecked would be demonstrating the defect inside the fix for it. `TC-ArgusAgent-DOCS-001-77` asserts this registration is still present.

**Disposition-reason refutation enforcement** *(added 2026-08-13 by Story 12.3 / `DF-12-1-B`, extending the §Delivery-closure rule above)*. **The rule: a disposition's REASON is as binding as its LABEL — where a reason makes a claim about reachability, that claim must be REFUTABLE, and a disposition whose stated reason the import graph falsifies fails CI.** It is enforced by **`tests/test_v1_commitment_closure.py`** (`delivered_differently_refutations`, driven by `TC-ArgusAgent-DOCS-001-34` over the live registry and by `TC-ArgusAgent-DOCS-001-37c` over a synthetic graph), and it closes a hole that was **measured by executing the guard's own code, not by reading it**. `reachability_refutations` refutes exactly two shapes — `wired`-over-unreachable and `library-seam`-over-reachable — and Story 12.2 added a third for `not-built`. `delivered-differently` was left unrefutable **by design and correctly**, since the label makes no reachability claim and a walk that assigned it one would manufacture false accusations. **But the label was never the only thing making claims.** FR27's reason asserted *"the memoization MECHANISM is unwired (`DF-AUD-APAA-A`) … Mechanism deferred to Story 12.3"*, and executed on `58c8f6b` with `argus.cache.memo_store` forced REACHABLE, `reachability_refutations` returned `()` while the identical tuple disposed `library-seam` fired immediately. So wiring the store — the thing that sentence was *about* — would have turned **nothing** red, and this repository would have gone on asserting that its memoization mechanism was unbuilt, behind a fully green suite. **That also makes `DF-12-1-B`'s stated trigger measurably FALSE as written**: it predicted this wiring would *"flip a `library-seam` disposition red"*, and FR27 was never disposed `library-seam`; the substance the entry was pointing at is real, but the mechanism it named would never have fired. The new direction is deliberately **as narrow as Story 12.2's**: it fires only when the reason contains a registered unwiredness/deferral marker AND the module that reason is about is reachable, so the disposition's legitimate use — *"delivered by another mechanism, divergence named"* — is untouched. The remedy when it fires is to **re-derive the disposition**, never to soften the sentence until it stops matching. Because a refutation nobody has watched fire is a refutation nobody knows is reachable, `-37c` drives all three outcomes over a synthetic graph (refuted / silent-because-unreachable / silent-because-no-claim), and the fix was proven **RED-first with the final committed code** against the real pre-fix registry state. `TC-ArgusAgent-DOCS-001-41` asserts this registration is still present.

**Vacuity-corroboration enforcement** *(added 2026-08-17 by [sprint-change-proposal-2026-08-17.md](sprint-change-proposal-2026-08-17.md), implemented by Story 14.1)*. **The rule: a `vacuous_test_ast` finding is verdict-eligible ONLY on evidence that the asserted values do not derive from the SUT — NEVER on the mere presence of a mock.** Cross-cutting concern #6 has required *"`audited_deep` AST corroboration AND Prosecutor sign-off"* since this architecture was written; the Story 1.5 detector shipped **`AUDITED_SHALLOW` with no sign-off**, and its fact (b) reduced to `assertion_sites >= 1 and mock_sites >= 1` — which is *"the test constructs a mock"*, a fact the heuristic already had. **Measured on the day it was found, which is why this is a rule and not a preference:** over the ratified 5-repository corpus the rule class emitted **31** blocking findings and the named human adjudicated **0** of them true (26 FP / 5 BORDERLINE); across **1,836** heuristically-flagged tests in the two contributing members `ast_corroborated` was equivalent to `mock_sites >= 1` in **1,835** cases, so the corroboration step **added no evidence the heuristic did not already have** — it re-read one input and treated the agreement as confirmation. **The Epic-6 Prosecutor does not close this, and relying on it was the error:** `argus/verdict/prosecutor.py:56-57` leaves an ALREADY-verdict-eligible finding **UNCHANGED**, so sign-off gates only the *promotion* path (advisory → eligible), and the V1 call site at `pipeline.py:535` passes **no `sign_offs`** by design (the deterministic zero-token default). *"AST corroboration AND Prosecutor sign-off"* is therefore an `AND` only for the findings that do not need it, and an `OR` for the one class that does. **The moat is consequently enforced AT THE DETECTOR**, and the conservative default is restored: where the unresolved 1.4 edge set (DF-1-4-A) cannot establish fact (b), corroboration is **NOT granted** and the finding stays `vacuous_test_heuristic` / advisory. The V1 signal is **name-level and a proxy** — full dataflow-grounded assertion provenance remains **Story 6.2**'s scope (`DF-14-1-A`) — and it is measured against three populations, never argued: the planted-vacuous cartridges (recall, incl. the `holdout_vacuous` anti-overfitting control), the 31 adjudicated locators (precision), and the whole flagged population (promotion rate).

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

**Added 2026-08-10b (FR35):**

```text
argus/mcp/              # FR35 stdio protocol adapter — impure wiring, no audit logic
argus/assets/commands/  # packaged assistant command assets (data, not code)
argus/commands/         # FR35 `argus install-commands` — pure host registry + pure fold + thin write
```

✅ **Both reserved paths are now occupied** — `argus/mcp/` by Story 12.6, `argus/assets/commands/` by Story
12.7 — and the placement recorded here in advance turned out to be the one that shipped. `argus/commands/`
is the one addition this proposal did not anticipate, and it exists for NFR-M1's *"NO business logic in the
entrypoint"*: the installer's logic could not live in `argus/cli.py`, and putting it beside the DATA in
`argus/assets/` would have made an inert data package executable.

*(The tree header above still reads `minions_core/apaa/` — stale since the 2026-08-03 separation, on the
same correction path as §I Packaging. Recorded here; the tree-wide rename is not this proposal's scope.)*

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

- **`argus/mcp/**` (or equivalent) is an ADAPTER layer.** *(Added 2026-08-10b.)* It may import the pure
  core and the same request/verdict types the CLI uses. It may **not** be imported by the pure core, must
  not introduce a scheduling or concurrency model of its own (the sequential-canonical execution model at
  §A is unchanged), and is subject to the §H import-isolation gate. The dependency arrow points **inward
  only** — identical to `cli.py`.

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

> ⚠️ **SCOPE, clarified 2026-08-10.** This validation was performed against the **pre-amendment contract
> (33 FRs / 21 NFRs)**. It is **not** a validation of FR34–FR37 or NFR-S6/NFR-P3, which the 2026-08-10b
> amendment added. Until 2026-08-10 it read *"All 33 FRs"* / *"All 21 NFRs"* with no qualifier, which reads
> as a current certification of a superseded contract. The post-amendment additions are covered below and
> map to modules named in this document; they have **not** been re-validated through this section's method.

- **All 33 FRs of the base contract** map to a concrete module (FR-cluster→location table). No FR is unsupported.

> ⚠️ **WHAT "SUPPORTED" MEANS HERE, clarified 2026-08-11 by Story 10.5 / AC4.5.** The bullet above is true and it is not a coverage certification: the FR-cluster→location table **certifies module PLACEMENT, not reachability**, and *mapping to a module is not delivery*. Measured on 2026-08-11 by a static import walk of `argus/**` (stdlib `ast`, transitive closure from `argus/cli.py`, the only entry point — `pyproject.toml` ships three console aliases and all three are `argus.cli:main`): **53 of 72 modules are reachable; 19 are not**, and **4 FRs of the base contract are LIBRARY SEAMS with no production call site — FR23, FR24, FR26 and FR29.** All four sit in a **single row** of the table above (*Governance/Integrity (FR23–29)*), every module that row names genuinely exists, and each of the four is built, typed and test-proven — which is precisely why placement read as coverage for five weeks. Each is now amended in the PRD, struck-not-deleted and dated, and filed in `deferred-work.md` (`DF-6-7-A`, `DF-10-5-A`, `-B`, `-C`). ⛔ **This caveat does not re-run this section's validation method and does not alter the table above**; it bounds the claim. The scope caveat immediately above says *which* contract was validated — this one says *what validation established*. Both are needed. Enforced from 2026-08-11 by **`tests/test_v1_commitment_closure.py`**, which refutes a `wired` disposition mechanically rather than trusting this document.
- **All 21 NFRs of the base contract** supported: D1–3 (`cache/`, `canonical`, pure `verdict`), S1–5
  (containment + redaction + `tests/security/`), C1–3 (`budget_governor`, `tool_runner`), R1–2
  (failure→finding, `store/reader` resume), P1–2 (`canonical`, stack-agnostic `claim→validated?`), A1–3
  (`envelope`, `negative_assurance`), SC1 (`partitioner`), M1–2 (file-size CI, Pydantic v2).
- **Post-amendment additions (2026-08-10b) — module placement recorded, delivery owned by Epics 11–12:**
  **FR34** → the run-grade vs instrument-status distinction (§L158-173), extending the existing
  `DOGFOOD_EXTERNALIZATION_GUARD`, never a second mechanism · **FR35** → ~~`argus/mcp/**`, an adapter layer
  with no audit logic and no second decision path (§L272-303, L631-634)~~ ✅ **DELIVERED IN PART by Story
  12.6, 2026-08-15** (struck above, not deleted — §3.4; the PLACEMENT it recorded was right and has now become
  a delivery): `argus/mcp/` ships as the console alias `argus-mcp` = `argus.mcp.server:main` in the SAME
  distribution — a JSON-RPC 2.0 stdio adapter with one `audit_repository` tool that reaches `run_audit`
  through `argus/cli.py`'s OWN request projection, so it carries no audit logic, no verdict logic and no
  second decision path, and the verdict is the CLI's BY CONSTRUCTION rather than by discipline. All five §A
  binding constraints are asserted mechanically (`tests/test_mcp_server.py`, verification area
  `ArgusAgent-MCP-001`). ~~⚠️ **SCOPE, so this row does not over-claim the FR:** the packaged assistant command
  assets and any registration mechanism are **Story 12.7's** — the wheel still ships ZERO data assets and
  installing this distribution registers no slash command in any assistant~~ ✅ **COMPLETED by Story 12.7,
  2026-08-15** (struck above, not deleted — §3.4; the residual it named was right and has now been closed):
  the assets ship as DATA under `argus/assets/commands/**` (asserted in the built **wheel and sdist** by
  `TC-ArgusAgent-ASSETS-001-12`, so `BuiltDistribution.data_assets` is non-empty), and the documented step
  that places them is a **second sub-command on the CLI entry point** — `argus install-commands`
  (`argus/commands/installer.py`, closed host registry `argus/commands/hosts.py`), which is DN-1's ruling:
  the transport is argv, identical to the CLI's, so a separate console alias would have been a fork of an
  entry point rather than an extension of one (AR7 / §3.3). It therefore adds **no** `[project.scripts]`
  entry, and the second surface's published tool schema — derived from the `audit` sub-parser alone — is
  untouched. The set that ships equals the set every publishing surface documents, in both directions
  (`TC-ArgusAgent-ASSETS-001-06`), and the FR34 disclosure is RENDERED into each placed file at write time
  from the one constant rather than committed into an asset (AI-E9-7 / DN-7). Publishing anything at all
  remains **Story 12.9's** · **FR36** → `DeepAuditSeam`
  (`argus/audit/deep_audit.py`), off by default, spend through the existing ceiling (§L381-388) ·
  **FR37** → `argus/reports/plain_english.py` + `argus/reports/generator.py`, the two verdict-rendering
  surfaces · **NFR-S6** → the no-egress-without-opt-in committed gate (§L385-388, L460) ·
  **NFR-P3** → ~~⚠️ **open packaging decision owned by Story 12.5** (§L446-447): the 9 non-Python grammars are
  an optional extra, so the default install grounds **Python only** — the exact state NFR-P3 classifies as a
  packaging defect.~~ ✅ **RESOLVED by Story 12.5, 2026-08-15** (struck above, not deleted — §3.4): the 9
  non-Python tree-sitter grammars are promoted to `[project.dependencies]`, so the default install grounds
  all 10 supported source languages out of the box, and a grammar nonetheless missing at run time states
  its package and its `pip install` remedy at the point the file is downgraded (§L669-693).

### Implementation Readiness Validation ✅
- Decisions complete with verified versions; patterns enforceable (committed gates: import-isolation,
  determinism golden-tests, secret-containment property suite, file-size); structure specific (every file
  named, boundaries explicit).

### Gap Analysis
- **Critical gaps:** none — the architecture does not block implementation.
- **Important gaps (pre-epic delivery inputs, resolve in epic planning):** ~~validation-set `N` (gates the
  precision-harness ground-truth shape)~~ **— see the VALIDATION-SET RESOLUTION below**; Minions-dogfood
  partition + budget-sizing plan (so the proof run doesn't land `INSUFFICIENT_COVERAGE`) — CLOSED
  2026-08-10b, delivered by Story 7.1; budget-ceiling `$X` default — CLOSED 2026-08-10b as OI3, the
  resolution being "there is no default".

  ✅ **RESOLVED BY DECISION 2026-08-16 (Story 13.1 / DN-1) — the PRD governs.** *(VALIDATION-SET
  RESOLUTION — the identical paragraph is recorded at §Architectural Decisions and at §Still OPEN,
  so no site survives saying something else.)* The validation set is **`N ≈ 5–10` real repositories**
  with a floor of **`N ≥ 5`**, per PRD §Validation Approach; `precision-validation-protocol.md` §5's
  conflicting **`N ≥ 5` labeled planted-defect cartridges** floor is **struck**. **Reason:** the two
  documents specified different *quantities*, not two opinions about one — the cartridges measure
  **recall** against defects the team planted and answered, while the gate must measure **precision**
  on code nobody planted. A gate clearable by the team's own plants is not an externalization gate.
  The cartridges are **re-labelled, not demoted**: they remain the FR20 recall instrument, CI-asserted
  and unchanged. **Membership is a closed, machine-readable manifest** —
  `tests/corpus/_manifest.py::VALIDATION_CORPUS` — carrying a pinned commit sha, licence, language
  and provenance per member, with exclusions recorded in the manifest itself and the floor **derived**
  from the same `VALIDATION_SET_FLOOR_N = 5` rather than forked. **This closes the input by DECISION;
  it does not clear the gate.** Measured at resolution: **`N = 0` eligible members**, no adjudication
  run, `protocol_cleared` never `True`. **Updated the same day, 2026-08-16: the operator ratified five
  members under AC3b, so `N = 5` and the floor is MET** — the resolution-time zero is kept struck-not-
  erased because it is the state the DECISION was taken in. Reaching the floor is one of four §5
  conditions; the other three (the adjudication run, the ≥80% figure, zero clean-repo blocking FPs) are
  unmet, so the gate remains **PROVISIONAL**. Enforced by **`tests/test_validation_set_decision.py`**
  (`TC-ArgusAgent-DOCS-001-73`..`-76`).
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
- **Future enhancement:** ~~multi-language AST (V2),~~ seam auditor (V2), mutation-grade vacuous (V2), consume
  Minions layers (d)/(a)/(e), hosted runner + HTTP API (V4). *(Amended 2026-08-10, Story 10.2 /
  `DF-AUD-APAA-D`: multi-language AST grounding is **delivered in V1** — see
  `argus/shared/source_languages.py` — and is struck here rather than deleted, per §3.4. The other items are
  untouched. This site, like `§Stack` above, was missed by all three prior enumerations. Delivered by
  `sprint-change-proposal-2026-07-28.md`.)*

### Implementation Handoff
- **AI agents must:** follow these decisions exactly; route JSON through `canonical`; keep pure modules
  I/O-free; emit findings with a locator or not at all; import only FastAPI-free leaf modules.
- **First implementation priority:** the THIN VERTICAL signature-demo slice — envelope + canonical serializer
  + fixed-enum ledger → AST index + one vacuous-path rule → pure verdict + exit code → 🔴 on the Minions
  vacuous-test cartridge. NOT a horizontal determinism epic.
