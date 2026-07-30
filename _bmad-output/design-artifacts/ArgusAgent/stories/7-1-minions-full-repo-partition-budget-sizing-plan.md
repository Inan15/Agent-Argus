# Story 7.1: Minions full-repo partition + budget-sizing plan (OI2 LOCKED: full-repo; OI3: size $X here) — [Tier B]

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker at `_bmad-output/implementation-artifacts/sprint-status.yaml`). All
> CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only, §3.8 12-Factor + secret masking, §3.4
> evidence immutability). Run all gate/test commands under `PYTHONIOENCODING=utf-8` (Windows / cp1252).
>
> **This is the FIRST story of Epic 7** (Minions Dogfood Proof Run — the capstone; the "last thing cut").
> It builds on the fully-done Epics 1–6 and specifically on **done Story 2.4** (the FR3 partition PLANNER
> `index/partitioner.py::partition_repository` + `PartitionPlan`/`Partition`/`WorkManifest` contract + the
> `.apaa/assignments/` manifest-write + the manifest-scoped permission boundary), **done Story 3.1** (the
> FR21 budget-ceiling CONFIG + the pure `cost/budget_governor.py::account_spend` / `BudgetConfig` /
> `CostLedger` accounting core with the "no numeric `$X` default; `budget==0`/`None` = no ceiling" OI3
> contract), **done Stories 3.2/3.3** (halt→skip→downgrade + the `INSUFFICIENT_COVERAGE` floor), and the
> **done Story 6.5** measurement substrate (`tests/apaa/cartridges/_registry.py::CARTRIDGE_REGISTRY` +
> `CartridgeSpec`/`GoldenFinding` + `populated_planted_defect_count()` + `precision_gate_status()`) plus the
> **done Story 6.6** precision replay harness (`precision/replay_harness.py::compute_precision`). `epic-7`
> flips `backlog → in-progress` on this story (first-story-in-epic rule).
>
> **THIS STORY IS THE PLAN / SIZING STORY — it PREPARES the dogfood; it does NOT execute it (that is 7.2).**
> Per the **OI2 LOCK** (full-repo multi-partition) + the **OI3 LOCK** (size `$X` empirically here) + the
> **Epic-6 retro AI-E6-2** (DF-6-6-A promoted to a HARD Epic-7 pre-condition), it does THREE coherent
> "prepare the dogfood" things:
> 1. **Produce an explicit FULL-REPO partition map** of the real Minions repo (~70 modules) into bounded
>    ≤40-file/15k-LOC audit units, REUSING the 2.4 `partition_repository` planner + `PartitionPlan` contract
>    (no fork), so every targeted unit can clear the 20%-deep coverage floor and no unit lands
>    `INSUFFICIENT_COVERAGE` purely on scale.
> 2. **Produce the budget-sizing plan** — size the OI3-deferred numeric ceiling `$X` EMPIRICALLY to cover
>    the full-repo partition plan, REUSING the 3.1 `account_spend`/`BudgetConfig`/`CostLedger` accounting
>    core (no fork). `$X` is recorded as the dogfood ceiling with its derivation; the run is expected to
>    complete within it, and the 3.2 ceiling demonstrably halts + downgrades if breached.
> 3. **Grow the synthetic cartridge corpus toward N=5 DISTINCT defect-rule CLASSES** (the autonomous half of
>    DF-6-6-A) — add ≥2 new distinct-class cartridges (incl. ≥1 holdout) EXTENDING the 6.5
>    `CARTRIDGE_REGISTRY` (REUSE the frozen `CartridgeSpec` shape, no fork), strengthening the
>    provisional-gate substrate + the overfitting defense before the dogfood.
>
> **The OI1 honesty keystone is NON-NEGOTIABLE:** the ≥80%-precision gate stays **PROVISIONAL**. This story
> grows the corpus toward N=5 distinct classes (the autonomous half) but does NOT fabricate a cleared gate.
> The gate is cleared only by the HUMAN TP/FP adjudication over real dogfood findings (the human half of
> DF-6-6-A, planned for 7.2 + an explicit human step). Do NOT flip `protocol_cleared` / the
> `precision_gate_status()` marker.

## Story

As a **Delivery Orchestrator** planning the Minions dogfood proof run — who knows the whole capstone stands or
falls on the audit actually COVERING the real ~70-module Minions repo (not landing `INSUFFICIENT_COVERAGE`
because the repo overflowed a single audit unit) and completing WITHIN an honestly-sized cost ceiling (not an
invented `$X`), and who has watched OI3 defer the numeric ceiling default precisely so it could be sized
against a REAL full-repo partition plan, and who has watched the Epic-6 retro promote DF-6-6-A (the N=5
distinct-defect-class corpus growth + human adjudication) to a HARD Epic-7 pre-condition,
I want **an explicit, recorded FULL-REPO partition map of Minions (~70 modules across multiple bounded
≤40-file/15k-LOC units) + an empirically-sized budget ceiling `$X` that covers that plan + a synthetic
cartridge corpus grown toward N=5 DISTINCT defect-rule classes** — REUSING the 2.4 partition planner, the
3.1 budget-accounting core, and the 6.5 cartridge-registry shape (no forks), and honestly stating that V1
performs NO cross-partition SEAM analysis (the 6.4 `cross_partition` Prosecutor pass is the V1 mitigation;
full seam auditing is V2),
so that **7.2 can execute the whole-repo audit within a real ceiling, the proof's scope statement is honest
about what cut-spanning defects it could and couldn't see, and the provisional-gate substrate is
strengthened toward N=5 before the dogfood** — while the ≥80%-precision gate stays PROVISIONAL (the OI1
honesty keystone) because only the human TP/FP adjudication over the real dogfood findings (the DF-6-6-A
human half, 7.2 + a human step) may clear it, and over-claiming a cleared gate from a synthetic corpus is the
exact failure mode this lock forbids.

## Story Context

This is **Story 1 of Epic 7** (Minions Dogfood Proof Run, Tier-B — the capstone that answers "does Minions
have an audit agent?" with a real artifact). It is the PLANNING/sizing half of the dogfood: 7.1 produces the
partition map + the budget plan + the N=5-toward corpus growth; **7.2 EXECUTES** the whole-repo audit,
produces the coverage ledger / findings / negative-assurance verdict / signed evidence bundle, and reproduces
the signature demo. 7.1 does NOT run the audit or build the evidence bundle.

**What already exists (REUSE verbatim, do NOT rebuild — the no-fork keystone, §3.3 / AR7).** This story is a
PLAN + a corpus-growth story sitting on the fully-built Epic-1..6 spine. Every mechanism it needs already
ships:

- **Story 2.4 (done) — `minions_core/apaa/index/partitioner.py`.** The PURE
  `partition_repository(index: AstIndex, *, loc_by_file: dict[str, int], limits: PartitionLimits | None =
  None) -> PartitionPlan` graph-derived planner (bounds each unit ≤40 files/15k LOC soft, ≤60/25k hard;
  `context_pressure` auto-downgrade; a repo at-or-under one unit → a SINGLE partition; byte-stable for the
  same repo@commit). The frozen `Partition` / `PartitionPlan` / `WorkManifest` contract carries a STABLE
  content-derived `partition_id` + the sorted `work_manifest` file-list (the permission boundary, NFR-S4) +
  bounded-size provenance + the honest-limitation "V1 attempts NO cross-partition seam analysis" field.
  The impure manifest WRITE is `store/writer.py::ApaaStoreWriter.write_assignment(...)` →
  `.apaa/assignments/`. **7.1 CONSUMES this planner to produce the Minions full-repo plan — it does NOT
  re-author a partitioner, a second `PartitionPlan`, or a directory-based splitter.** The plan is built by
  running the 1.4 intake + `build_ast_index` + a per-file LOC map over the real Minions repo, then calling
  `partition_repository`.
- **Story 1.4 (done) — `index/ast_index.py::build_ast_index` + `RepoIntake` + `pipeline._read_source`.** The
  intake @ pinned commit + the tree-sitter Python AST index (the partition graph source). The per-file LOC
  the planner needs comes from `_read_source` (REUSE — the planner takes LOC as an in-memory `dict[str,int]`
  ARGUMENT; it never opens a file). NOTE the locked V1 edge limitation (DF-1-4-A): `CodeEdge.callee` is an
  unresolved bare identifier, so the planner under-merges rather than over-merges — document this in the plan
  provenance.
- **Story 3.1 (done) — `minions_core/apaa/cost/budget_governor.py`.** The frozen
  `BudgetConfig` (`ceiling_credits: int | None`; `None` = "no ceiling configured", the OI3 default — NEVER a
  hardcoded numeric default; no `float`) + the PURE `account_spend(contributions: Mapping[str, int], *,
  config: BudgetConfig, build_cost_proxy: int) -> CostLedger` fold (int credits, order-independent,
  byte-identical, REUSING the Minions `BudgetGuardrails` `>=`-is-a-breach decision BY IMPORT) + the NFR-C1
  baseline-cost ratio (a `Fraction`/`int`, never a float). **7.1 CONSUMES this to SIZE `$X` and record the
  budget plan — it does NOT re-derive a cost model, a second accountant, or a parallel breach comparison.**
- **Story 3.2 (done) — `cost/exhaustion.py`.** The mid-run halt→skip→downgrade→report behavior (FR22/NFR-C2)
  the ceiling triggers. 7.1's budget plan DOCUMENTS that the sized `$X` demonstrably halts + downgrades if
  breached; it does NOT re-implement the halt.
- **Story 3.3 (done) — the `INSUFFICIENT_COVERAGE` floor under exhaustion (FR16).** The verdict semantics a
  too-shallow / halted unit lands. 7.1's partition map is sized so each TARGETED unit can clear the 20%-deep
  floor; it touches NO verdict math.
- **Story 6.5 (done) — `tests/apaa/cartridges/_registry.py`.** The frozen `CartridgeSpec` /
  `GoldenFinding` shape + `CARTRIDGE_REGISTRY` (8 rows today) + `VALIDATION_SET_FLOOR_N = 5` +
  `populated_planted_defect_count()` + `precision_gate_status()` / `PRECISION_GATE_STATUS`. The staging
  helper `tests/apaa/cartridges/_cartridge.py::stage_cartridge` pins each `*.py.txt` template dir. **7.1
  EXTENDS `CARTRIDGE_REGISTRY` with ≥2 new distinct-class rows (REUSE the frozen shape — a registry row + a
  `*.py.txt` drop-in, NO harness refactor; the DN-REGISTRY additive promise) — it does NOT fork a second
  registry or re-author existing golden keys.**
- **Story 6.6 (done) — `minions_core/apaa/precision/replay_harness.py`.** The PURE
  `compute_precision(...)` → `PrecisionResult` (TP/FP/FN over the 6.5 golden keys → an exact-`Fraction`
  precision string; the shared `finding_match_key`/`golden_match_key`; `precision_gate_status_for(...)` that
  REUSES the 6.5 marker with `protocol_cleared` defaulting `False`). **7.1's grown corpus flows through this
  harness UNCHANGED (a new registry row = a new cartridge in the roll-up, no harness edit). The gate STAYS
  PROVISIONAL (`protocol_cleared=False`) — 7.1 does NOT flip it.**

**The net-new deliverable of THIS story.** Three recorded artifacts + the corpus growth:
1. a committed **Minions full-repo partition plan** (a `.md` deliverable under
   `_bmad-output/design-artifacts/ArgusAgent/`, e.g. `minions-dogfood-partition-plan.md`) that records the
   partition map produced by REUSING `partition_repository` over the real Minions repo @ a pinned commit:
   the unit count, each unit's file count + LOC + `partition_id`, the cut edges, the `context_pressure`
   downgrades, and the **honest V1 no-cross-partition-seam-analysis limitation** (the 6.4 `cross_partition`
   pass is the V1 mitigation; full seam auditing is V2). Reproducible: a committed generator/test that
   re-derives the plan deterministically (byte-stable for the same repo@commit) — NOT a hand-typed map that
   rots.
2. a committed **budget-sizing plan** (a `.md` deliverable, e.g. `minions-dogfood-budget-plan.md`, OR a
   §-section of the partition plan) that records `$X` sized EMPIRICALLY to cover the full-repo plan via the
   3.1 `account_spend` cost model over the V1 (deterministic, zero-token) contributions across all units,
   the derivation (per-unit contribution basis → running total → the sized ceiling with headroom), the
   NFR-C1 baseline ratio, and the explicit statement that OI3's "no numeric default" is now RESOLVED for the
   dogfood by this empirical sizing (a real `int`-credit `$X`, never a float). It documents that the ceiling
   demonstrably halts + downgrades (3.2) if breached.
3. **≥2 new distinct-class cartridges** appended to `CARTRIDGE_REGISTRY` (+ their `*.py.txt` template dirs +
   golden keys), incl. ≥1 holdout (never-tuned) cartridge, taking the DISTINCT defect-rule-CLASS count from
   3 (today: `vacuous_test_ast`, `hardcoded_secret`, `orphan_code`) toward 5, with the harness/roll-up
   running over the grown corpus UNCHANGED and `populated_planted_defect_count()` / the precision roll-up
   reporting the new count HONESTLY. The gate stays PROVISIONAL.
4. a committed **DF-6-6-A progress note** (append-only in `deferred-work.md`) recording that the AUTONOMOUS
   half (corpus → N distinct classes) advanced in 7.1, the CURRENT distinct-class count, and that the HUMAN
   adjudication half stays open (target `epic-7-minions-dogfood-precision` / the 7.2 + human step).

**Distinct-defect-rule-CLASS accounting — the DF-6-6-A honesty crux (read carefully).** DF-6-6-A distinguishes
cartridge ROWS from distinct defect-rule CLASSES: 6.6 had 5 populated planted-defect ROWS
(`populated_planted_defect_count() == 5`) but only **THREE distinct rule CLASSES** (`vacuous_test_ast` ×3
[vacuous_basic / holdout_vacuous / nonascii_unicode], `hardcoded_secret` ×1, `orphan_code` ×1). "Grow toward
N=5 DISTINCT classes" therefore means adding cartridges whose golden key is a rule class NOT already labeled
— NOT more variants of `vacuous_test_ast`. The real detector-emitted rule classes available in the codebase
are: `vacuous_test_ast` (labeled), `hardcoded_secret` (labeled), `orphan_code` (labeled), and
`cross_partition` (the 6.4 Prosecutor cut-edge pass — a REAL, UNlabeled class). Additional distinct-class
candidates the dev may use (verify each emits a stable `rule_id` before locking a golden key): a
`vacuous_test_heuristic` finding (the Tier-A heuristic path, distinct `rule_id` from `vacuous_test_ast`), a
`secret_scan_failed` / tool-failure-as-finding class (2.6), or an orphan sub-class (`orphan_malformed_entry`
/ `orphan_unnamed_definition`). **Lock the ≥2 new classes to rule_ids the dev CONFIRMS the pipeline actually
emits over a staged cartridge** — a golden key for a class the detectors never produce would be a permanent
FN. If reaching 5 genuinely-distinct classes proves infeasible with real detector rule_ids in this story,
add as many DISTINCT classes as the detectors support (≥2 new, so ≥4 or 5 total), record the honest count,
and file the shortfall append-only as a DF-6-6-A progress note — do NOT manufacture a synthetic rule_id no
detector emits, and do NOT count multiple variants of one class as distinct.

**Scope vs the rest of Epic 7 (explicit deferrals — do NOT pull forward).**
- **The dogfood EXECUTION** (running APAA end-to-end over Minions, the coverage ledger, the findings, the
  negative-assurance verdict, the SIGNED EVIDENCE BUNDLE, the reproduced `GitHub green · Sonar green · APAA
  🔴` signature demo, the 100%-reproducibility comparison, the `grade: demo-heuristic-only` flag) — that is
  **7.2**. 7.1 produces only the PLAN + the sizing + the corpus growth.
- **The HUMAN TP/FP adjudication that CLEARS the ≥80%-precision gate** — the human half of DF-6-6-A, planned
  for 7.2 + an explicit human step. 7.1 does the AUTONOMOUS corpus-growth half ONLY and does NOT flip the
  gate / `protocol_cleared`.
- **A V2 cross-partition SEAM auditor** — out of scope (V2). The plan STATES the V1 limitation honestly (the
  6.4 `cross_partition` pass is the V1 mitigation); it builds no seam analyzer.
- **A change to the 2.4 partitioner / the 3.1 budget core / the 6.5 registry SHAPE / any detector / the
  Prosecutor / any frozen Epic-1..6 contract** — out of scope. 7.1 CONSUMES the planner + the accountant +
  the registry-row shape as-is; the ONLY production/test-tree code additions are the new cartridge template
  dirs + the ≥2 new `CARTRIDGE_REGISTRY` rows + the plan-generator/test glue. If planning surfaces a
  partitioner/budget/detector gap, that is a DEFER (six CC-3 fields), not a 7.1 edit.
- **A new `.github/workflows` CI job / a new HTTP route / a FastAPI surface / a UI (§3.7) / a new `cli.py`
  flag** — out of scope. Any new test runs under the EXISTING APAA pytest CI invocation (the durable
  backstop). (A future `apaa partition-plan` / `apaa budget-plan` CLI surface is a follow-up.)

**Carry-forward action items (CLAUDE.md §9.1 / L1-E11 — the Epic-6 retro's AI-E6-* items as Epic-7 backlog).**
- **AI-E6-2 (process/precision, HARD Epic-7 pre-condition) — DF-6-6-A.** 7.1 discharges the AUTONOMOUS half:
  grow the synthetic corpus toward N=5 DISTINCT defect-rule classes (≥2 new distinct-class cartridges incl.
  ≥1 holdout), strengthening the provisional-gate substrate + overfitting defense. The HUMAN adjudication
  half (recorded TP/FP judgment over real dogfood findings) stays open for 7.2 + a human step — 7.1 does NOT
  present a cleared gate.
- **AI-E6-1 (test-infra 🟠, the 6.7-FAIL class / §9.2 occ-2 promotion) — payload/event-identity checklist
  leg.** Any new cartridge whose golden key or template could collide with an existing row (e.g. a
  near-identical holdout) must be proven DISTINCT in the roll-up (the new class produces its OWN TP, not a
  duplicate-collapsed count) — RED-first where a naive registry append would collide.
- **AI-E5-1 (test-infra 🟠, standing) — complete-the-declared-set.** Enumerate the FULL declared set of 7.1
  deliverables — (1) the full-repo partition map (reproducible); (2) the empirically-sized `$X` budget plan;
  (3) the ≥2 new distinct-class cartridges (incl. ≥1 holdout) with the corpus growth reported honestly; (4)
  the honest V1-no-seam-analysis limitation in the plan; (5) the DF-6-6-A progress note — and demonstrate
  EACH covered.
- **AI-E4-2 (test-infra) — no-crash input shapes.** The plan generator over the REAL Minions repo (parse
  failures, non-ASCII paths, a module over the hard LOC limit) degrades to a typed, NAMED outcome — never a
  bare traceback. A new cartridge's `stage_cartridge` failure → a NAMED assertion citing the cartridge id.
- **AI-E1-1 (test-infra 🟢, standing) — non-ASCII / locale discipline.** Any new cartridge + the plan
  artifacts serialize + round-trip under `PYTHONIOENCODING=utf-8`; the corpus keeps its non-ASCII coverage.
- **AI-E5-4 / AI-E6-6 (governance 🟢) — central defer register.** File the DF-6-6-A progress note + any
  newly-surfaced gap append-only in `deferred-work.md` with the six CC-3 fields.
- **AI-E5-7 (process 🟢) — structural gates green + partial-reuse docstring precision.** The plan generator +
  new cartridges keep the no-web-imports gate, the single-serializer AST gate, and the file-size gate green
  (REUSE the canonical serializer for any `.apaa`/plan bytes; add NO new `json.dumps`/hasher; import NO
  `fastapi/uvicorn/starlette` and NO LLM dispatch). Narrate the PARTIAL reuse precisely (REUSES
  `partition_repository` + `account_spend` + `CartridgeSpec` + `compute_precision`; ADDS the recorded plans +
  the new cartridges).
- **NFR-S1 secret-containment (standing CI-blocking moat).** New secret-bearing cartridges (if any) route
  through the EXISTING 4.4 randomized-canary suite (`tests/security/test_apaa_secret_containment.py`) — no
  planted secret / source byte in any golden key, plan artifact, or precision result (golden keys are
  value-free by the 6.5 contract; the plan records only paths + counts + credits, NEVER source bytes).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 7.1) + the OI2/OI3 LOCKs (full-repo multi-partition; `$X` sized
> empirically here, no numeric default) + the Epic-6 retro AI-E6-2 (DF-6-6-A autonomous corpus-growth half) +
> the architecture (FR3 bounded-unit partitioning; FR21 budget-ceiling; FR20 defect-cartridge precision
> substrate; the V1 no-seam-analysis honesty limitation). Drivers: **APAA-FR-3** (partition the repo into
> bounded audit units within budget — the full-repo Minions map), **APAA-FR-21** (operator budget ceiling —
> the empirically-sized `$X`), **APAA-FR-20** (defect-cartridge precision substrate — the N=5-toward corpus
> growth), **APAA-NFR-SC1** (≤40-file/15k-LOC scale envelope), **APAA-NFR-S4** (work-manifest permission
> boundary — preserved by REUSE), **APAA-NFR-C1** (baseline-cost report), **APAA-NFR-D1/P1** (the plan +
> corpus roll-up are deterministic + byte-reproducible), **APAA-NFR-S1** (no source/secret bytes in the plan
> / golden keys / precision result), **APAA-AR4** (int credits / Fraction ratios — NEVER float in any
> persisted figure), **APAA-AR7** (REUSE by import — no fork of the planner/accountant/registry),
> **APAA-NFR-M1/M2** (≤1200-line files; frozen Epic-1..6 contracts + the 6.5 registry SHAPE unchanged).
>
> **SCOPE FENCE — Tier-B, single-purpose "prepare the dogfood": the full-repo partition map + the
> empirically-sized budget plan + the N=5-toward corpus growth + the honest limitations.** This story
> delivers ONLY: (1) the committed, reproducible Minions FULL-REPO partition map (REUSING
> `partition_repository`); (2) the committed empirically-sized `$X` budget plan (REUSING `account_spend`);
> (3) ≥2 new DISTINCT-defect-rule-class cartridges (incl. ≥1 holdout) EXTENDING `CARTRIDGE_REGISTRY`, corpus
> count reported honestly; (4) the honest V1-no-cross-partition-seam-analysis limitation statement in the
> plan; (5) the DF-6-6-A progress note; (6) any new defer with the six CC-3 fields. It does NOT build, and
> MUST NOT pull forward: the **dogfood EXECUTION / coverage ledger / findings / negative-assurance verdict /
> signed EVIDENCE BUNDLE / signature demo / reproducibility comparison** (7.2); the **HUMAN TP/FP
> adjudication that CLEARS the ≥80%-precision gate** (7.2 + human step — 7.1 keeps the gate PROVISIONAL,
> `protocol_cleared=False`); a **V2 cross-partition SEAM auditor**; a **change to the 2.4 partitioner / 3.1
> budget core / 6.5 registry SHAPE / any detector / the Prosecutor / any frozen Epic-1..6 contract**; a **new
> `.github/workflows` CI job / HTTP route / FastAPI surface / UI (§3.7) / new `cli.py` flag**.

**AC1 — An explicit, reproducible FULL-REPO partition map of Minions (~70 modules) is recorded, REUSING the 2.4 planner (FR3 / OI2 / NFR-SC1 / AR7)**
**Given** the real Minions repo (~70 modules) @ a pinned commit, the 1.4 `build_ast_index` + a per-file LOC
map, and the 2.4 `partition_repository` planner + `PartitionPlan` contract
**When** the full-repo partition map is produced
**Then** a committed artifact (e.g. `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md`)
records the **full-repo** map — ALL modules across MULTIPLE bounded units (OI2: full-repo multi-partition,
NOT a single unit), each unit ≤40 files/15k LOC (soft) and never over the ≤60/25k hard ceiling (NFR-SC1),
with each unit's `partition_id` + file count + LOC + the cut edges + any `context_pressure` downgrades — and
the map is produced by REUSING `partition_repository` (no forked partitioner), is REPRODUCIBLE (a committed
generator/test re-derives it deterministically, byte-stable for the same repo@commit — NFR-D1/P1, not a
hand-typed map), and the 2.4 work-manifest permission boundary (NFR-S4) is preserved by reuse.

**AC2 — The map is sized so every TARGETED unit can clear the 20%-deep coverage floor — no unit lands INSUFFICIENT_COVERAGE purely on scale (FR3 / FR16 floor)**
**Given** the 20%-deep coverage floor (3.3) and the full-repo partition map
**When** the plan is finalized
**Then** it records that each TARGETED unit is bounded so it can clear the 20%-deep floor (the plan's per-unit
budget allocation supports auditing enough of each unit to clear the floor), so the dogfood does not land
`INSUFFICIENT_COVERAGE` merely because the repo overflowed a single audit unit — the plan explicitly notes
any unit it does NOT target (and why) so the coverage claim is honest.

**AC3 — The budget ceiling `$X` is sized EMPIRICALLY to cover the full-repo plan, REUSING the 3.1 accountant — no pre-locked numeric default (FR21 / OI3 / AR4 / AR7)**
**Given** OI3 (the numeric `$X` default was DEFERRED to this story's empirical sizing) and the 3.1
`account_spend` / `BudgetConfig` / `CostLedger` accounting core
**When** the budget plan is finalized
**Then** a committed artifact records `$X` sized **empirically to cover the full-repo partition plan** — the
per-unit V1 (deterministic, zero-token) cost contributions folded via `account_spend` across all units into a
running `int`-credit total, the sized ceiling (with its derivation + any headroom), and the NFR-C1 baseline
ratio (a `Fraction`/`int`, never a float) — recorded as the dogfood ceiling. `$X` is a real `int`-credit
value (AR4 — no float reaches any persisted figure), it REUSES the 3.1 accountant (no forked cost model /
breach comparison), and the plan documents that OI3's "no numeric default" is RESOLVED for the dogfood by
THIS sizing while the 3.1 mechanism's "no hardcoded default in code" invariant is preserved (the number lives
in the plan artifact, not baked into `budget_governor.py`).

**AC4 — The plan states honestly that V1 performs NO cross-partition SEAM analysis (OI2 V1 limitation / the honest-scope keystone)**
**Given** the full-repo scope spans partition cut edges
**When** the plan is written
**Then** it explicitly states that V1 has **NO cross-partition seam analysis** — a defect spanning a cut
(caller in unit A, callee in unit B) is NOT analyzed by any seam auditor in V1; the **only** V1 mitigation is
the 6.4 `cross_partition` Prosecutor cut-edge pass (re-reads cut edges), and the full seam auditor is V2 — so
the proof's scope statement is honest about what cut-spanning defects it could and couldn't see (this
statement appears in the committed plan artifact, mirroring the 2.4 plan-provenance limitation field).

**AC5 — The synthetic cartridge corpus is grown toward N=5 DISTINCT defect-rule CLASSES (≥2 new distinct-class cartridges, ≥1 holdout), REUSING the 6.5 registry shape (FR20 / DF-6-6-A autonomous half / AI-E6-2 / AR7)**
**Given** the 6.5 `CARTRIDGE_REGISTRY` (today: 3 DISTINCT defect-rule classes — `vacuous_test_ast`,
`hardcoded_secret`, `orphan_code` — across the populated planted-defect/holdout rows) and the frozen
`CartridgeSpec`/`GoldenFinding` shape
**When** the corpus is grown
**Then** ≥2 NEW cartridges are appended to `CARTRIDGE_REGISTRY` whose golden key is a defect-rule class NOT
already labeled (each `rule_id` CONFIRMED to be one the pipeline actually emits over the staged cartridge —
e.g. `cross_partition`, `vacuous_test_heuristic`, or a tool-failure/orphan sub-class; NEVER a synthetic
rule_id no detector produces), incl. ≥1 HOLDOUT (never-tuned) cartridge, REUSING the additive
registry-row + `*.py.txt` drop-in shape (NO harness refactor, NO forked registry, NO re-authored existing
golden keys — the DN-REGISTRY additive promise / §3.3), taking the DISTINCT-class count from 3 toward 5; the
6.6 `compute_precision` roll-up runs over the grown corpus UNCHANGED and each new class produces its OWN TP
(RED-first against a near-identical row that would collapse into a duplicate count — AI-E6-1); the current
distinct-class count is REPORTED HONESTLY. If 5 genuinely-distinct real-detector classes are infeasible in
this story, add as many DISTINCT classes as the detectors support (≥2 new) and record the honest shortfall.

**AC6 — The ≥80%-precision gate STAYS PROVISIONAL — the OI1 honesty keystone; the human adjudication (DF-6-6-A human half) is NOT performed here (OI1 / DF-6-6-A / NFR of honesty)**
**Given** the grown corpus and the 6.6 `precision_gate_status_for(...)` / `PRECISION_GATE_STATUS` marker
**When** the precision roll-up is reported after the corpus growth
**Then** the gate is reported **PROVISIONAL** (`protocol_cleared=False`; the marker is NOT flipped): 7.1 does
the AUTONOMOUS corpus-growth half of DF-6-6-A ONLY and does NOT run the human TP/FP adjudication that clears
the gate (that is 7.2 + an explicit human step); the harness computes a REAL number over the grown corpus and
reports it ALONGSIDE the provisional flag — it does NOT fabricate or softclaim a cleared ≥80% gate from a
synthetic corpus; the Dev Notes + any plan artifact are scrupulously honest that the gate stays provisional
until the human adjudication over real dogfood findings runs (do NOT overclaim — honest coverage is APAA's
whole thesis). A committed DF-6-6-A progress note (append-only in `deferred-work.md`, six CC-3 fields) records
the advanced autonomous half + the current distinct-class count + the still-open human half.

**AC7 — Complete-the-declared-set over the 7.1 deliverables, each RED-first / honest where applicable (AI-E5-1 / AI-E6-1 / AR10)**
**Given** the full DECLARED set of 7.1 deliverables
**When** the story is built
**Then** EACH member is explicitly covered: (1) the reproducible full-repo partition map (AC1); (2) the
per-unit-clears-the-floor scoping (AC2); (3) the empirically-sized `$X` budget plan (AC3); (4) the honest
V1-no-seam-analysis limitation (AC4); (5) the ≥2 new distinct-class cartridges incl. ≥1 holdout, corpus count
honest (AC5, RED-first against a collision-collapsed count — AI-E6-1); (6) the provisional-gate honesty
report + the DF-6-6-A progress note (AC6, RED-first against a silently-flipped gate); AND the enumeration is
EXPLICIT in the plan artifacts + the test module. The plan generator never raises opaquely (a parse failure /
non-ASCII path / over-limit module on the real repo → a typed, NAMED outcome; a `stage_cartridge` failure → a
NAMED assertion citing the cartridge id — the AI-E4-2 no-crash leg).

**AC8 — No regression / no scope creep; structural gates green; ≤1200 lines; frozen surfaces unchanged; the pre-`review` test-existence precondition (AI-E5-7 / AI-E5-3 / NFR-M1/M2 / AR7)**
**Given** the new plan generator/test + the ≥2 new cartridges + the plan artifacts
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the prior green baseline + the new 7.1 tests + the grown-corpus roll-up), the no-web-imports gate, the
single-serializer AST gate, the file-size gate, and the 4.4 secret-containment suite stay green; `mypy` is
clean on any new/modified modules
**And** NO behavior-changing diff to the frozen Epic-1..6 production surfaces OR the 6.5 `_registry.py` SHAPE
(the story CONSUMES `partition_repository` / `account_spend` / `compute_precision` and only APPENDS registry
rows + template dirs; `coverage_ledger.py` / `recording.py` / `verdict_gate.py` / `partitioner.py` /
`budget_governor.py` / `detectors/*` / `prosecutor.py` / `pipeline.py` / `store/*` / `precision/*` /
`models.py` show NO behavior-changing diff; the `CartridgeSpec`/`GoldenFinding` SHAPE is unchanged — only
`CARTRIDGE_REGISTRY` rows are appended), NO forked partitioner/accountant/registry/serializer, NO `cli.py`
flag, NO HTTP route, NO new CI job, NO live LLM call, `protocol_cleared` NOT flipped
**And** each new/modified file is ≤1200 lines (NFR-M1); the new files cite their `APAA-FR-3` / `APAA-FR-21` /
`APAA-FR-20` / `APAA-NFR-SC1` / `APAA-NFR-C1` / `APAA-AR4` drivers in the module/artifact docstring + the
locked test area / index; the mandatory artifacts (the partition plan + the budget plan + the ≥2 new
cartridges + the DF-6-6-A progress note + the new tests) EXIST + pass + any new defer is filed BEFORE the
story flips to `status: review` (AI-E5-3 test-existence discipline). **Test area `APAA-DOGFOOD`**
(`TC-APAA-DOGFOOD-001-NN`, start at index 01; lock the area + index in the plan generator/test docstring).

## Tasks / Subtasks

- [x] **Task 0 — Re-read the REAL reuse surfaces; LOCK the plan-generator design, the budget-sizing method, the distinct-class cartridge set, and the OI1 provisional constraint** (AC: 1, 3, 5, 6)
  - [x] Re-read `minions_core/apaa/index/partitioner.py` (`partition_repository` signature, `PartitionPlan` /
        `Partition` / `WorkManifest` fields, `PartitionLimits`, the honest-limitation field, `context_pressure`)
        + `index/ast_index.py::build_ast_index` + `pipeline.py::_read_source` (the per-file LOC source). LOCK:
        REUSE the planner; do NOT fork a partitioner or a second `PartitionPlan`.
  - [x] Re-read `minions_core/apaa/cost/budget_governor.py` (`account_spend` signature, `BudgetConfig`
        `ceiling_credits: int | None` = OI3 "no numeric default", `CostLedger`, the `>=`-is-a-breach REUSE,
        the NFR-C1 baseline ratio, the AR4 no-float rule) + `cost/exhaustion.py` (the 3.2 halt behavior). LOCK:
        REUSE the accountant to SIZE `$X`; the number lives in the plan artifact, NOT baked into the module.
  - [x] Re-read `tests/apaa/cartridges/_registry.py` (`CartridgeSpec` / `GoldenFinding` shape,
        `CARTRIDGE_REGISTRY`, `VALIDATION_SET_FLOOR_N`, `populated_planted_defect_count()`,
        `precision_gate_status()`) + `tests/apaa/cartridges/_cartridge.py::stage_cartridge` +
        `minions_core/apaa/precision/replay_harness.py` (`compute_precision`, `precision_gate_status_for`,
        `protocol_cleared` default). LOCK: EXTEND the registry additively (row + `*.py.txt` drop-in), REUSE the
        harness/roll-up unchanged, do NOT flip `protocol_cleared`.
  - [x] Enumerate the REAL detector-emitted rule classes (`grep rule_id` over `detectors/*` + the Prosecutor):
        confirm which classes the pipeline actually emits over a staged cartridge. LOCK the ≥2 NEW
        distinct-class rule_ids (incl. ≥1 holdout) to CONFIRMED-emitted classes — NEVER a synthetic rule_id no
        detector produces. Record the DF-6-6-A row-vs-distinct-class distinction + the OI1 no-overclaim
        constraint in Dev Notes.
- [x] **Task 1 — Produce the reproducible full-repo Minions partition map** (AC: 1, 2, 4)
  - [x] A committed generator/test that runs intake @ a pinned Minions commit → `build_ast_index` → a
        per-file LOC map (via `_read_source`) → `partition_repository` → the `PartitionPlan`, and records the
        map (unit count, per-unit `partition_id`/files/LOC, cut edges, `context_pressure` downgrades) into
        `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md`. Deterministic/byte-stable for
        the same repo@commit (NFR-D1/P1). Record per-unit clears-the-20%-floor scoping (AC2) + any un-targeted
        unit (honest). Include the AC4 honest V1-no-cross-partition-seam-analysis limitation statement.
  - [x] No-crash over the real repo (AI-E4-2): parse failures / non-ASCII paths / an over-hard-limit module →
        a typed NAMED outcome, never a bare traceback.
- [x] **Task 2 — Produce the empirically-sized `$X` budget plan** (AC: 3)
  - [x] Fold the per-unit V1 (deterministic, zero-token) cost contributions via `account_spend` across all
        units into a running `int`-credit total; size `$X` empirically to cover the full-repo plan (with the
        derivation + any headroom); compute the NFR-C1 baseline ratio (Fraction/int, never float — AR4).
        Record it into the budget-plan artifact (a `.md` deliverable OR a §-section of the partition plan) as
        the dogfood ceiling; document that OI3's "no numeric default" is RESOLVED for the dogfood by this
        sizing while `budget_governor.py` keeps no hardcoded default, and that the 3.2 ceiling halts +
        downgrades if breached.
- [x] **Task 3 — Grow the corpus toward N=5 DISTINCT defect-rule classes** (AC: 5, 6)
  - [x] Append ≥2 NEW cartridges to `CARTRIDGE_REGISTRY` (REUSE the frozen `CartridgeSpec` shape — a row + a
        `*.py.txt` template dir + a golden key of a CONFIRMED-emitted, NOT-already-labeled rule class), incl.
        ≥1 HOLDOUT (never-tuned) cartridge. Take the DISTINCT-class count from 3 toward 5. No harness refactor,
        no forked registry, no re-authored existing golden keys.
  - [x] Prove each new class produces its OWN TP in the `compute_precision` roll-up (RED-first against a
        collision-collapsed duplicate count — AI-E6-1). Report the current distinct-class count honestly.
  - [x] Confirm the gate STAYS PROVISIONAL (`protocol_cleared=False`; marker NOT flipped — AC6). If a new
        cartridge is secret-bearing, EXTEND the 4.4 `tests/security/test_apaa_secret_containment.py` sweep
        (do not fork).
- [x] **Task 4 — The parametrized 7.1 test module** (AC: 1, 2, 3, 5, 6, 7, 8)
  - [x] `tests/apaa/test_dogfood_plan.py` (area `APAA-DOGFOOD`, `TC-APAA-DOGFOOD-001-NN` from index 01):
        assert the partition map re-derives deterministically (AC1), each targeted unit is floor-clearing
        (AC2), the `$X` sizing is an `int`-credit value covering the plan with no float (AC3), the AC4
        limitation statement is present, the ≥2 new distinct-class cartridges each produce their own TP
        (AC5, RED-first collision), the gate stays PROVISIONAL (AC6, RED-first silently-flipped), and the
        complete-the-declared-set enumeration + no-crash edges (AC7). Each assertion failure NAMES the unit /
        cartridge id (the AI-E4-2 no-crash leg).
- [x] **Task 5 — Run + mypy + gates + the DF-6-6-A progress note + the pre-`review` precondition** (AC: 6, 8)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
        all pass (prior baseline + the new 7.1 tests + the grown-corpus roll-up). `mypy` clean on any new
        modules. Confirm NO behavior-changing diff to the frozen Epic-1..6 surfaces + the 6.5 `_registry.py`
        SHAPE (only appended rows). Confirm the no-web-imports / single-serializer / file-size / 4.4 gates
        green. NO `cli.py`/HTTP/CI-job change; NO detector/Prosecutor/partitioner/budget-core edit; NO live
        LLM; `protocol_cleared` NOT flipped.
  - [x] **AI-E5-4 / AI-E6-6:** file the DF-6-6-A progress note append-only in
        `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` with the six CC-3 fields (advanced autonomous
        half; current distinct-class count; human-adjudication half still open, `target_story:
        epic-7-minions-dogfood-precision`). File any newly-surfaced partitioner/budget/detector gap the same
        way.
  - [x] **AI-E5-3 / AI-E2-1 GATE:** the mandatory artifacts (the partition plan + the budget plan + the ≥2
        new cartridges + the test module + the DF-6-6-A progress note) EXIST + pass BEFORE the `review` flip;
        the Dev Agent Record is filled completely (no blank placeholders), incl. the locked plan-generator
        design + the budget-sizing method + the distinct-class rule_id choices + the honest distinct-class
        count + the OI1 no-overclaim statement.

## Dev Notes

### Architecture / contract anchors (re-read before coding)
- **Partition planner — REUSE, do not fork:** `minions_core/apaa/index/partitioner.py::partition_repository(
  index, *, loc_by_file, limits=None) -> PartitionPlan` (bounds ≤40/15k soft, ≤60/25k hard; graph-derived via
  the 1.4 `edges`+`definitions`; `context_pressure` downgrade; single-partition degenerate case; byte-stable).
  The frozen `Partition`/`PartitionPlan`/`WorkManifest` contract (stable content-derived `partition_id`, the
  sorted `work_manifest` permission boundary NFR-S4, bounded-size provenance, the honest-limitation field).
  Source of the graph: `index/ast_index.py::build_ast_index`; source of LOC: `pipeline.py::_read_source`
  (the planner takes LOC as an in-memory `dict[str,int]` ARGUMENT — it never opens a file).
- **Budget accountant — REUSE, do not fork:** `minions_core/apaa/cost/budget_governor.py::account_spend(
  contributions, *, config, build_cost_proxy) -> CostLedger` (pure `int`-credit fold, order-independent,
  byte-identical; REUSES the Minions `BudgetGuardrails` `>=`-is-a-breach decision BY IMPORT) + `BudgetConfig`
  (`ceiling_credits: int | None`; `None` = OI3 "no ceiling configured" default — NEVER a hardcoded numeric
  default; no float) + the NFR-C1 baseline ratio. The 3.2 halt lives in `cost/exhaustion.py`.
- **Cartridge registry — EXTEND additively, do not fork:** `tests/apaa/cartridges/_registry.py` (`CartridgeSpec`
  / `GoldenFinding` FROZEN shape; `CARTRIDGE_REGISTRY` — 8 rows today; `VALIDATION_SET_FLOOR_N = 5`;
  `populated_planted_defect_count()`; `precision_gate_status()` / `PRECISION_GATE_STATUS`). A NEW cartridge =
  a registry ROW + a `*.py.txt` template drop-in, NO harness refactor (the DN-REGISTRY additive promise).
  Stage via `tests/apaa/cartridges/_cartridge.py::stage_cartridge`.
- **Precision roll-up — REUSE unchanged, do NOT flip:** `minions_core/apaa/precision/replay_harness.py::
  compute_precision(...) -> PrecisionResult` (TP/FP/FN over the golden keys → exact-`Fraction` string; the
  shared `finding_match_key`/`golden_match_key`; `precision_gate_status_for(..., protocol_cleared=False)`).
  The grown corpus flows through it with NO harness edit. `protocol_cleared` STAYS `False` (OI1 keystone).
- **REAL detector-emitted rule classes (verify before locking a golden key):** `vacuous_test_ast` (labeled),
  `vacuous_test_heuristic` (Tier-A heuristic path, distinct rule_id), `hardcoded_secret` (labeled),
  `orphan_code` (labeled) + `orphan_malformed_entry` / `orphan_unnamed_definition`, `secret_scan_failed`
  (2.6 tool-failure-as-finding), `cross_partition` (the 6.4 Prosecutor cut-edge pass — UNlabeled). Lock the
  ≥2 NEW distinct classes to rule_ids the dev CONFIRMS the pipeline emits over a staged cartridge.
- **Fixed-precision — AR4 (the byte-diff landmine):** every persisted cost figure (`$X`, the NFR-C1 ratio) is
  `int` credits / a `Fraction` ratio — NO float (the 1.1 serializer rejects float; NFR-P1 byte-identity).
- **Secret-containment suite (EXTEND, do not fork):** `tests/security/test_apaa_secret_containment.py` (4.4).
- **Structural gates:** the no-web-imports gate, the single-serializer AST gate, the file-size gate — all stay
  green (the plan generator is pure/FastAPI-free/LLM-free; REUSE the canonical serializer for any bytes).

### Locked decisions (resolve in dev; recorded here per §3.4)
- **DN-PARTITION-REUSE.** The full-repo map is PRODUCED by REUSING `partition_repository` over the real
  Minions repo @ a pinned commit — a committed generator/test re-derives it deterministically. NO forked
  partitioner, NO hand-typed map that rots, NO directory-based splitter.
- **DN-BUDGET-SIZING.** `$X` is sized EMPIRICALLY via `account_spend` over the V1 (deterministic, zero-token)
  contributions across all units. The number lives in the PLAN ARTIFACT (int credits, no float) — the OI3
  "no hardcoded numeric default in `budget_governor.py`" invariant is PRESERVED (the module keeps
  `ceiling_credits: int | None = None`; the dogfood ceiling is an operator-supplied value the plan records).
- **DN-DISTINCT-CLASS (the DF-6-6-A crux).** "N=5 distinct classes" counts DISTINCT defect-rule CLASSES, NOT
  cartridge rows (6.6: 5 rows, 3 classes). Add ≥2 cartridges whose golden key is a NOT-already-labeled,
  CONFIRMED-emitted rule class (incl. ≥1 holdout). If 5 genuinely-distinct real-detector classes are
  infeasible here, add as many as the detectors support (≥2 new) + record the honest shortfall + a DF-6-6-A
  progress note. NEVER a synthetic rule_id no detector emits; NEVER count variants of one class as distinct.
- **DN-PROVISIONAL (the OI1 keystone — do NOT soften).** 7.1 does the AUTONOMOUS corpus-growth half of
  DF-6-6-A ONLY. The ≥80%-precision gate STAYS PROVISIONAL (`protocol_cleared=False`; the
  `precision_gate_status()` marker is NOT flipped). The human TP/FP adjudication over real dogfood findings
  (the human half) is 7.2 + a human step. Do NOT fabricate or softclaim a cleared gate from a synthetic
  corpus — honest coverage is APAA's whole thesis and over-claiming is the exact failure mode this lock
  forbids.
- **DN-HONEST-LIMITATION.** The plan STATES V1 performs NO cross-partition seam analysis (the 6.4
  `cross_partition` pass is the V1 mitigation; full seam auditing is V2) — the proof's scope statement is
  honest about what cut-spanning defects it could and couldn't see (mirrors the 2.4 plan-provenance field).
- **DN-NO-PROD-CHANGE-FROZEN.** 7.1 adds committed plan artifacts + ≥2 `CARTRIDGE_REGISTRY` rows + template
  dirs + a test module + a DF-6-6-A progress note. It CONSUMES the planner/accountant/harness as-is; it edits
  NO detector/Prosecutor/partitioner/budget-core/frozen-contract, does NOT change the 6.5 `_registry.py`
  SHAPE (only appends rows), adds NO `.apaa/` write path it mandates, NO `cli.py`/HTTP/CI-job. If planning
  surfaces a gap, that is a DEFER (six CC-3 fields), not a 7.1 edit.

### OI2/OI3/OI1 honesty constraints (the central theme — do NOT soften)
- **OI2 LOCKED — full-repo multi-partition.** The map covers ALL ~70 Minions modules across MULTIPLE bounded
  units. V1 does multi-UNIT auditing, NOT cross-partition SEAM analysis (V2).
- **OI3 LOCKED — `$X` sized empirically here.** No pre-locked numeric default; `$X` is derived from the
  full-repo plan via `account_spend`. `budget_governor.py` keeps no hardcoded default.
- **OI1 LOCKED — the ≥80%-precision gate is PROVISIONAL below the cleared human adjudication.** 7.1 grows the
  corpus toward N=5 distinct classes (autonomous half) but keeps the gate provisional; only the human
  adjudication over real dogfood findings clears it (DF-6-6-A human half, 7.2 + a human step).

### Carry-forward action items addressed
- **AI-E6-2** — DF-6-6-A autonomous half (corpus → N=5 distinct classes) discharged; human half stays open.
- **AI-E6-1** — payload/event-identity: each new distinct class produces its OWN TP (RED-first collision).
- **AI-E5-1** — complete-the-declared-set over the 7.1 deliverables (AC7).
- **AI-E4-2** — no-crash over the real repo + the new cartridges (typed NAMED outcomes / cartridge-id
  assertions).
- **AI-E1-1** — non-ASCII discipline under `PYTHONIOENCODING=utf-8`.
- **AI-E5-3 / AI-E5-7 / AI-E6-6** — pre-`review` test-existence + structural gates green + partial-reuse
  docstring precision + defer back-fill.

### Previous-story intelligence (6.7 / 6.6 — the immediate predecessors + the DF-6-6-A origin)
- 6.6 stood up the PURE precision replay harness + the committed validation protocol and computed an
  EARLY/PROVISIONAL precision of `1/1` over the current corpus (6 TP / 0 FP / 0 FN). HONEST LIMITATION (NOT
  softened): `populated_planted_defect_count()` returns 5 ROWS but only THREE distinct defect-rule CLASSES.
  The gate STAYS PROVISIONAL — `compute_precision` defaults `protocol_cleared=False`; 6.6 did NOT flip the
  marker. Closing DF-6-6-A = grow the labeled corpus to distinct classes + run the human adjudication + pass
  `protocol_cleared=True` at the call site. **7.1 does the first half (grow) autonomously; 7.2 + a human step
  does the adjudication.**
- The Epic-6 retro promoted DF-6-6-A to a HARD Epic-7 pre-condition (AI-E6-2): the N=5 distinct-class corpus
  + a recorded human adjudication must exist BEFORE 7.2 presents externalization evidence.
- The whole APAA prod tree is currently UNTRACKED (the sub-tool is not yet git-committed), so `git diff` over
  the frozen surfaces is empty/N-A — use mtime (as 6.5/6.6 reviewers did) as the load-bearing no-change
  evidence, and keep the new cartridge rows/dirs + the plan generator/test + the plan artifacts the only
  added files.
- The Epic-6 retro AI-E6-4 flags `pipeline.py` at 1090/1200 for a proactive split BEFORE live-wiring — 7.1
  does NOT wire the pipeline (that is 7.2), so no split is forced here; note it if any 7.1 touch approaches
  the limit.

### Project structure notes
- New test: `tests/apaa/test_dogfood_plan.py` (area `APAA-DOGFOOD`, `TC-APAA-DOGFOOD-001-NN` from 01).
- New cartridges: template dirs under `tests/apaa/cartridges/` + ≥2 appended `CARTRIDGE_REGISTRY` rows.
- New plan artifacts: `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` +
  `minions-dogfood-budget-plan.md` (or a merged plan doc).
- DF-6-6-A progress note: append-only in `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`.
- All files ≤1200 lines; run everything under `PYTHONIOENCODING=utf-8`.

## Dev Agent Record

### Context Reference
- Epic source: `_bmad-output/design-artifacts/ArgusAgent/epics.md` §Epic 7 / Story 7.1 + the "Open delivery inputs —
  LOCKED 2026-06-18" block (OI1/OI2/OI3).
- Reuse seams: `index/partitioner.py` (2.4), `cost/budget_governor.py` + `cost/exhaustion.py` (3.1/3.2),
  `tests/apaa/cartridges/_registry.py` + `_cartridge.py` (6.5), `precision/replay_harness.py` (6.6).
- Driver: DF-6-6-A (`deferred-work.md`); Epic-6 retro AI-E6-2 (`epic-6-retro-2026-07-02.md`).

### Agent Model Used
claude-opus-4-8[1m] (dev-story, implement mode, 2026-07-02).

### Debug Log References
- Empirical detector-emission probes (NOT assumed — the DF-6-6-A honesty crux): staged
  candidate cartridges + ran the REAL `run_audit_detailed` / `prosecute` to CONFIRM each
  new golden-key rule_id is one the pipeline actually emits:
  - `vacuous_test_heuristic`: a heuristically-vacuous test with a SUT call but NO
    assertion + NO mock → Tier-A corroboration withheld (`_ast_corroborated` requires
    `assertion_sites>=1 AND mock_sites>=1`) → advisory `vacuous_test_heuristic`,
    `depth_supported=None`. Verdict NOT_READY_FOR_RELEASE / exit 2 / 0 blocking. CONFIRMED.
  - `cross_partition`: a 45-file cohesion CHAIN → the oversized component is split by the
    REAL 2.4 `_split_oversized_component` under DEFAULT limits → a REAL `CutEdge` → the
    REAL 6.4 Prosecutor emits advisory `cross_partition` through the UNMODIFIED
    `run_audit_detailed`. Under the harness budget (100) the chain exhausts the budget
    (26/45 skipped-on-exhaustion) → exhaustion-driven NOT_READY / exit 2; the
    `cross_partition` finding is DETERMINISTICALLY emitted (verified two clean stagings).
    CONFIRMED.
  - RULED OUT (documented, honest — not manufactured): `tool_failure` /
    `traceability_not_establishable` are NOT reachable through a source-only cartridge
    audited by `run_audit_detailed` — the breadth channel skips any file the depth path
    already graded (`already_graded_paths`), and in V1 the depth path grades every indexed
    Python file, so the breadth-failure findings never surface. Confirmed by probing an
    unparseable file (graded SKIPPED by `_grade_non_test_python`, so breadth skips it) and
    a 0-byte file (graded by the depth path). NO synthetic rule_id was manufactured.
- Full-repo partition probe: the real Minions platform tree (135 tracked `minions_core/`
  `.py` files excluding the untracked `minions_core/apaa/` sub-tree, ~36.7k LOC) partitions
  into **4 bounded units** (40/34/40/21 files; 12577/13998/9438/699 LOC — all ≤ the 60/25k
  hard ceiling), 332 recorded cut edges, byte-stable across two derivations.
- Budget sizing probe: V1 deterministic total **675 credits** (files_indexed +
  python_files + detector_passes across all 4 units), `$X` = **843 credits** (675 × 5/4
  headroom, int-floored), NFR-C1 baseline **675/36712** (~1.8%, a bounded Fraction). Run
  FITS under 843; a ceiling below the total demonstrably BREACHES (the 3.2 halt REUSE).
- Full suite: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/
  tests/test_import_paths.py` → **1243 passed, 1 skipped, 4 subtests passed** (the prior
  green baseline + the 17 new `TC-APAA-DOGFOOD-001-01..17` + the grown-corpus roll-up).
  `mypy` clean on `minions_core/apaa/dogfood/*`. The no-web-imports gate, the
  single-serializer AST gate, the file-size gate, and the 4.4 secret-containment suite all
  stay green.

### Completion Notes List
- **AC1 (reproducible full-repo map).** `minions_core/apaa/dogfood/partition_plan.py`
  REUSES `partition_repository` (2.4) + `build_ast_index` (1.4) + `compute_loc_by_file` +
  the 1.4 `_SOURCE_SUFFIXES` discovery filter (BY IMPORT — no fork) to derive the full-repo
  map over the tracked Minions platform tree, and renders it to the committed
  `minions-dogfood-partition-plan.md`. Reproducible: `build_full_repo_plan` re-derives
  byte-identically (TC-APAA-DOGFOOD-001-02); the committed artifact re-matches the live
  derivation (…-03). Multi-partition (4 units, OI2), all ≤ the hard ceiling, total+disjoint
  (…-01).
- **AC2 (per-unit floor-clearing).** Every unit is a TARGETED bounded unit; the V1 pass
  grades 100% of a unit's files, clearing the 1/5 floor. `BudgetSizing.per_unit[*].clears_floor`
  records the explicit claim; no unit is un-targeted (…-04).
- **AC3 (empirical `$X`, REUSE the 3.1 accountant, no float).** `size_budget` folds each
  unit's V1 contributions (the SAME recipe `pipeline._build_cost_ledger` uses) via
  `account_spend` into a running int total, sizes `$X` = total × 5/4 int-floored (no float,
  AR4), computes the NFR-C1 baseline `Fraction`, and DEMONSTRATES the 3.2 halt (fits under
  `$X`; breaches below the total). Committed to `minions-dogfood-budget-plan.md`
  (…-05/06). OI3 preserved: `BudgetConfig().ceiling_credits is None` (no hardcoded default);
  the number lives in the plan artifact.
- **AC4 (honest V1 no-seam-analysis limitation).** The partition plan STATES V1 has NO
  cross-partition seam analysis, names the 6.4 `cross_partition` pass as the ONLY V1
  mitigation, and marks the full seam auditor V2 (…-07), anchored on the 2.4
  `seam_analysis == "v2-deferred"` marker.
- **AC5 (≥2 new distinct classes incl. ≥1 holdout, REUSE the 6.5 shape).** Appended TWO
  registry ROWS (frozen `CartridgeSpec`/`GoldenFinding` shape unchanged — additive only):
  `vacuous_heuristic_basic` (planted_defect, `vacuous_test_heuristic`) +
  `cross_partition_seam` (**holdout**, `cross_partition`). Distinct-class count 3 → **5**
  (added `distinct_rule_class_count`/`distinct_rule_classes` helpers — additive). Each new
  class produces its OWN TP in the UNCHANGED 6.6 `compute_precision` roll-up (…-09);
  RED-first against a collision-collapsed count (…-10). Both rule_ids CONFIRMED-emitted by
  the real detectors (see Debug Log) — never synthetic.
- **AC6 (OI1 keystone — gate STAYS PROVISIONAL).** `compute_precision` defaults
  `protocol_cleared=False`; 7.1 does NOT flip it and does NOT flip the 6.5
  `precision_gate_status()` marker. Even at N=7 populated rows + precision 1/1 the gate is
  reported PROVISIONAL (…-11); RED-first that the flip requires `protocol_cleared=True`
  (…-12). The DF-6-6-A progress note (six CC-3 fields) is filed append-only in
  `deferred-work.md` recording the advanced autonomous half + the still-open human half
  (…-13).
- **AC7 (complete-the-declared-set + no-crash).** All 7 declared members enumerated in the
  test-module docstring + covered. No-crash edges: an empty repo → total-safe zero-partition
  plan (no divide-by-zero); a malformed contribution → typed `DogfoodPlanError` (…-14). A
  cartridge staging failure → a NAMED assertion citing the cartridge id.
- **AC8 (no regression / no scope creep).** Full suite green; frozen Epic-1..6 surfaces +
  the 6.5 `_registry.py` SHAPE unchanged (only rows + two additive helpers appended); all
  new files ≤1200 lines; NO `cli.py`/HTTP/CI-job change; NO detector/Prosecutor/partitioner/
  budget-core edit; NO live LLM; `protocol_cleared` NOT flipped.
- **Honest distinct-class outcome (DF-6-6-A crux).** Reached the FULL N=5 distinct classes
  — NOT a shortfall — because both new classes (`vacuous_test_heuristic`, `cross_partition`)
  are genuinely emittable through the UNMODIFIED `run_audit_detailed` roll-up the frozen 6.6
  harness uses (the cross_partition cartridge exploits the 45-file cohesion-chain split
  under DEFAULT limits so no harness change is needed). `tool_failure` /
  `traceability_not_establishable` were ruled out honestly rather than manufactured.

### Locked decisions (per §3.4)
- **DN-PARTITION-REUSE (resolved).** Full-repo map produced by REUSING `partition_repository`
  over the tracked Minions platform tree via a committed generator that re-derives
  deterministically. Enumeration REUSES the 1.4 `_SOURCE_SUFFIXES` filter over `git ls-files
  -z` (committed content — sidesteps the dirty live-tree / `load_repo_at_commit` clean-tree
  requirement, since the working tree is dirty and the APAA sub-tree is untracked), scoped
  to `minions_core/` and excluding `minions_core/apaa/`. NO forked partitioner / hand-typed
  map / directory splitter.
- **DN-BUDGET-SIZING (resolved).** `$X` = V1 deterministic total × 5/4 headroom, int-floored
  (843 credits). Number lives in the plan artifact; `budget_governor.py` keeps
  `ceiling_credits: int | None = None` (OI3 preserved). Headroom rationale: 25% over the V1
  zero-token proxy leaves room for the expected-but-unbilled V2 LLM depth passes without an
  unbounded ceiling.
- **DN-DISTINCT-CLASS (resolved).** 5 distinct classes reached (2 new: `vacuous_test_heuristic`
  planted + `cross_partition` holdout). Both CONFIRMED-emitted. `tool_failure` /
  `traceability_not_establishable` ruled out (breadth channel skips depth-graded files).
- **DN-PROVISIONAL (held — the OI1 keystone).** Gate STAYS PROVISIONAL; `protocol_cleared`
  NOT flipped; marker NOT flipped. Human adjudication (DF-6-6-A human half) is 7.2 + a human
  step.
- **DN-HONEST-LIMITATION (resolved).** The plan STATES V1 has no cross-partition seam
  analysis; the 6.4 `cross_partition` pass is the V1 mitigation; full seam auditing is V2.
- **DN-NO-PROD-CHANGE-FROZEN (held).** Only added: the `dogfood/` sub-package + 2 registry
  rows + 2 additive registry helpers + 46 cartridge template files + the test module + 2 plan
  artifacts + the DF-6-6-A progress note. No detector/Prosecutor/partitioner/budget-core/
  frozen-contract edit; the 6.5 `CartridgeSpec`/`GoldenFinding` SHAPE is byte-unchanged.

### File List
NEW (production):
- `minions_core/apaa/dogfood/__init__.py`
- `minions_core/apaa/dogfood/partition_plan.py`

MODIFIED (test-tree registry — additive rows + helpers only, SHAPE unchanged):
- `tests/apaa/cartridges/_registry.py`

NEW (test-tree cartridge templates):
- `tests/apaa/cartridges/vacuous_heuristic_basic/src/orders.py.txt`
- `tests/apaa/cartridges/vacuous_heuristic_basic/tests/test_orders.py.txt`
- `tests/apaa/cartridges/cross_partition_seam/src/chain00.py.txt` … `chain44.py.txt` (45 files)

NEW (test):
- `tests/apaa/test_dogfood_plan.py` (area APAA-DOGFOOD, TC-APAA-DOGFOOD-001-01..17)

NEW (committed plan artifacts):
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md`

MODIFIED (governance evidence — append-only):
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (DF-6-6-A-P1 progress note)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (7-1 → review)
- `_bmad-output/design-artifacts/ArgusAgent/stories/7-1-minions-full-repo-partition-budget-sizing-plan.md` (this file)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-07-02 | 0.1 | Story created (create-story) — full-repo partition map + empirically-sized `$X` budget plan + N=5-toward distinct-class corpus growth (DF-6-6-A autonomous half); gate stays PROVISIONAL (OI1). | Scrum Master |
| 2026-07-02 | 1.1 | code-review (iter-1) — **PASS**. Verified INDEPENDENTLY (not trusting the Dev record): full suite re-run 1243 passed/1 skipped/4 subtests; the two new golden rule_ids (`vacuous_test_heuristic`, `cross_partition`) CONFIRMED-emitted by directly auditing the staged cartridges through the real `run_audit_detailed` (`vacuous_heuristic_basic`→`['vacuous_test_heuristic']`, `cross_partition_seam`→`['cross_partition','orphan_code']`) — not fabricated; 5 genuinely-distinct classes / 7 rows honest; OI1 gate STAYS PROVISIONAL (`protocol_cleared` default False, no prod `=True`, marker unflipped); reuse-by-import confirmed (no forked partitioner/accountant/registry SHAPE); budget int/Fraction only (843/675/`675/36712`, no float); no cli-flag/HTTP/CI-job; files ≤1200; mypy clean; DF-6-6-A-P1 note append-only with 6 CC-3 fields. Senior Developer Review (AI) written into story file. Status → done. | Reviewer (claude-opus-4-8[1m]) |
| 2026-07-02 | 1.0 | dev-story (implement) — DELIVERED all 8 ACs. (1) Reproducible full-repo Minions partition map (`dogfood/partition_plan.py` REUSES `partition_repository`/1.4 index/`_SOURCE_SUFFIXES` — no fork) → 4 bounded units over 135 modules/36.7k LOC, all ≤ hard ceiling, 332 cut edges; committed `minions-dogfood-partition-plan.md`, byte-reproducible. (2) Empirically-sized `$X`=843 credits (V1 total 675 × 5/4 headroom, int, no float) REUSING 3.1 `account_spend`; NFR-C1 baseline 675/36712; 3.2 halt demonstrated; committed `minions-dogfood-budget-plan.md`; OI3 "no numeric default" preserved in `budget_governor.py`. (3) Corpus grown 3→**5 DISTINCT classes** via 2 new cartridges (frozen `CartridgeSpec` shape, additive rows only): `vacuous_heuristic_basic` (planted, `vacuous_test_heuristic`) + `cross_partition_seam` (**holdout**, `cross_partition`) — both rule_ids CONFIRMED-emitted by the REAL detectors (not synthetic); each produces its own TP in the UNCHANGED 6.6 roll-up. (4) Plan STATES V1 no-cross-partition-seam-analysis honestly. **OI1 keystone HELD: gate STAYS PROVISIONAL — `protocol_cleared` NOT flipped, marker NOT flipped.** DF-6-6-A progress note filed (6 CC-3 fields; human half open → `epic-7-minions-dogfood-precision`). Area APAA-DOGFOOD TC-APAA-DOGFOOD-001-01..17. Full suite 1243 passed/1 skipped/4 subtests; mypy clean; structural + 4.4 gates green; files ≤1200. Status → review. | Dev (claude-opus-4-8[1m]) |

## Senior Developer Review (AI)

**Reviewer:** claude-opus-4-8[1m] (adversarial code-review gate, iter-1) · **Date:** 2026-07-02 · **Outcome: PASS → `done`.**

### Scope reviewed
The whole 7.1 delta: `minions_core/apaa/dogfood/partition_plan.py` (611 lines) + `tests/apaa/test_dogfood_plan.py` (511) + the two additive `CARTRIDGE_REGISTRY` rows + two additive helpers in `tests/apaa/cartridges/_registry.py` (320) + the 45-file `cross_partition_seam` + 2-file `vacuous_heuristic_basic` cartridge template dirs + the committed `minions-dogfood-partition-plan.md` / `minions-dogfood-budget-plan.md` + the DF-6-6-A-P1 append-only progress note. The APAA prod tree is entirely git-untracked, so — as the 6.5/6.6 reviewers did — mtime + `git status` (only tracked deltas: `sprint-status.yaml` and the pre-existing story-1.1 `__init__.py::__version__` line, NOT a 7.1 edit) is the load-bearing no-change evidence.

### Independent verification (did NOT trust the Dev record)
- **Tests re-run by the reviewer:** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` → **1243 passed, 1 skipped, 4 subtests passed** (matches the Dev claim). The 17 `TC-APAA-DOGFOOD-001-01..17` all green. `mypy` clean on `dogfood/partition_plan.py`.
- **Corpus honesty (the keystone):** independently audited the two new staged cartridges through the REAL `run_audit_detailed` — `vacuous_heuristic_basic` emits `['vacuous_test_heuristic']`; `cross_partition_seam` emits `['cross_partition','orphan_code']`. Both golden `rule_id`s are GENUINELY detector-emitted, not fabricated golden keys. The test `-09` itself stages+audits every cartridge and asserts `row.tp >= 1` (a permanent FN would fail if the rule_id were synthetic). `cross_partition_seam` is a genuine 45-file cohesion-chain HOLDOUT the real 2.4 partitioner splits under DEFAULT limits → a real `CutEdge` → the 6.4 Prosecutor's advisory `cross_partition`. The incidental `orphan_code` on that cartridge is correctly NOT counted as an FP (the 6.6 model: advisory over-emissions on a labeled cartridge are not false accusations) — `row.fp == 0` held. Distinct classes independently confirmed: `{cross_partition, hardcoded_secret, orphan_code, vacuous_test_ast, vacuous_test_heuristic}` = **5 DISTINCT / 7 labeled rows** (honest row-vs-class distinction).
- **OI1 keystone:** `compute_precision` default `protocol_cleared: bool = False`; NO production `protocol_cleared=True` call site (only a docstring reference); `precision_gate_status()` returns `provisional (…)` with no ≥80% number presented as authoritative. Gate is NOT flipped.
- **Reuse / no-fork (AR7):** `partition_plan.py` imports `partition_repository` (2.4), `build_ast_index`/`compute_loc_by_file`/`_SOURCE_SUFFIXES` (1.4), and `account_spend`/`BudgetConfig`/`baseline_ratio` (3.1). No reimplemented partitioner, cost model, or serializer. The frozen `CartridgeSpec`/`GoldenFinding` SHAPE is byte-unchanged (only rows + 2 additive helpers appended).
- **AR4 no-float:** every persisted figure is int/Fraction — `$X`=843, V1 total 675, NFR-C1 baseline `675/36712`. No float leaks into the committed plan artifacts (grep confirmed); no planted secret bytes in the plans/precision surface (`-15`).
- **Scope fence:** no `cli.py` flag added (the one `dogfood` mention in `cli.py` is a pre-existing 3.1 budget-help narrative reference), no HTTP route, no `.github/workflows` CI job, no detector/Prosecutor/partitioner/budget-core edit. All new files ≤1200 lines. DF-6-6-A-P1 note is append-only (original DF-6-6-A entry not rewritten, §3.4) with all six CC-3 fields; `sprint-status.yaml` parses cleanly under UTF-8.

### Findings
None. All 8 ACs are met and independently corroborated. The single most important adversarial risk for this story — a fabricated golden `rule_id` that no detector emits, or a quietly-flipped precision gate — was checked directly against the real pipeline and is clean. The story is honest about what it delivers (plan/sizing/corpus-growth) versus what it defers (7.2 execution + the human adjudication that clears the gate).

### Action Items
None.

