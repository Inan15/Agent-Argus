# Story 3.2: Halt → skip → downgrade → report on budget exhaustion

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As an operator,
I want APAA to stop cleanly the moment its audit budget is exhausted mid-run — marking the un-audited remainder
`skipped`, re-folding the partial coverage ledger through the UNCHANGED pure verdict gate, and reporting
exactly what it did and did NOT assess — so that an audit that runs out of budget **degrades honestly** and
never silently overruns the ceiling, never fabricates coverage for the partitions it never reached, and never
presents a partial run as a complete one (the HONEST-DEGRADATION principle, FR22 / NFR-C2 — *the second story
of Epic 3, building on the done 3-1 budget-config + cost-accounting `ceiling_reached` signal that 3-1
exposed-but-did-NOT-act-on*).

## Story Context

This is **Story 2 of Epic 3** (Honest Degradation & Cost Governance, Tier-A; epic-3 is already `in-progress`
from Story 3.1). It is the **act-on-exhaustion** story: 3-1 built the budget-ceiling MECHANISM (`BudgetConfig`,
the pure `account_spend` fold, the `CostLedger` with a `ceiling_reached` flag) and *exposed* `ceiling_reached`
explicitly **for this story to query** — but 3-1 deliberately did NOT halt, did NOT mark anything `skipped`, and
did NOT change the verdict. **This story makes the pipeline ACT on budget exhaustion**: it delivers the
HALT → SKIP → DOWNGRADE → REPORT mechanism (FR22) so that when the running cost total reaches the configured
ceiling mid-audit, APAA stops dispatching new audit work, records every not-yet-audited partition/file as
`skipped` (the closed-enum 1.2 honesty state — examined-in-the-denominator, NEVER fabricated-deep), re-folds the
PARTIAL ledger through the UNCHANGED pure 1.6 `evaluate_verdict` gate, and reports what was and was not assessed.

**What FR22 IS in V1 — the halt/skip/downgrade/report MECHANISM, NOT the floor verdict.** The architecture
(Decision E / `cost/budget_governor.py`) calls for `halt → skip → downgrade → report (FR22/NFR-C2)`, and the
epic (Story 3.2) ACs lock it to: (a) **halt deterministically** when the ceiling is hit mid-run; (b) **mark the
remainder `skipped`**; (c) **downgrade coverage** (the partial ledger carries the un-audited files as `skipped`,
so the deep-% denominator honestly reflects what was NOT reached); (d) **report honestly** (an explicit,
typed, serialized record of which partitions/files were assessed vs `skipped`-on-exhaustion — "did not cover
Z"); (e) **never silently overrun** (no audit work is dispatched once `ceiling_reached` is true) and **never
fabricate** (a `skipped`-on-exhaustion file is NEVER graded `audited_deep`/`audited_shallow`); and (f) the
**pure-function gate still produces a verdict (degraded), never a crash** over the partial ledger.

**The Tier-A scope boundary — what is 3.2 vs the rest of Epic 3.** This story is single-purpose: the
**halt/skip/downgrade/report MECHANISM + the report of what was skipped**. The behavior built ON the mechanism,
and the verdict semantics, are explicitly later stories and MUST NOT be pulled forward:
- **The `INSUFFICIENT_COVERAGE` floor under exhaustion (FR16 floor) is Story 3.3** — the verdict *semantics* of
  a halted run whose assessed deep-% landed below the 20% floor (e.g. "assessed 18% deep; floor 20%" → exit 3,
  never a default `NOT_READY`). **This story does NOT change the verdict math.** It re-folds the partial ledger
  through the UNCHANGED frozen 1.6 `evaluate_verdict` gate and lets the gate's EXISTING thresholds decide. The
  gate ALREADY returns `INSUFFICIENT_COVERAGE` below 20% deep (`INSUFFICIENT_COVERAGE_FLOOR = Fraction(1, 5)`)
  and ALREADY excludes `skipped` from the deep-% numerator (FR8) — so a halt that pushes many files to `skipped`
  *naturally* drives a lower deep-% through the existing gate. 3.3 wires the *floor verdict's exhaustion-aware
  scope statement / "assessed X% deep" rendering*; this story produces the partial ledger + the skipped-record
  the gate already consumes. Lock + document this fence: **3.2 = the mechanism + the record; 3.3 = the floor
  verdict's exhaustion semantics.**
- **Resumability from on-disk `.apaa/` state (FR31) is Story 3.4** — the resume-from-disk restore-and-continue
  loop (re-invoke with a raised budget, reuse the prior coverage, do not re-audit `audited_deep` files). This
  story PERSISTS the partial ledger + the halt/skipped record + the cost snapshot (the seam 3.4 reads); it does
  NOT build the restore-and-continue loop.
- **Sequential byte-identical execution on the least-capable host (FR32/NFR-P1) is Story 3.5** — the host-
  independent determinism proof. This story's halted/partial-run output MUST already be byte-deterministic
  (the `skipped`-on-exhaustion set is content-derived + order-independent; no clock/uuid/random; no float) so
  3.5 has a determinate surface AND ships the halted-run byte-identity fixture (AI-E2-5). This story SHOULD
  include a byte-stability + order-independence test on the new halt/partial-ledger determinism surface (the
  AI-E2-5 discipline applied as each Epic-3 module lands); the full host-vs-host parity proof is 3.5.
- **The numeric `$X` ceiling default + full-repo budget sizing is Story 7.1** (OI3) — NOT here. This story
  exercises the halt MECHANISM against an operator-set (or test-set) ceiling; it locks NO numeric default.

**The V1-cost-is-a-proxy reality (inherited from 3-1, load-bearing for the halt point).** The Epic-1/2/3
pipeline calls **NO LLM** (the dispatch port is Epic 6), so V1 cost is the deterministic, zero-token work-unit
PROXY that 3-1 folds (`files_indexed` / `python_files` / `detector_passes` — counted from the index). There is
NO incremental per-file billing loop in V1: 3-1 computes the cost ledger ONCE, AFTER the single-pass detect/grade
stage, over the whole index. **This is the central design tension for 3.2** and the dev MUST resolve it
deterministically and honestly (see Dev Notes "The halt model in a single-pass zero-token V1 pipeline" — the
recommended approach is a **deterministic pre-dispatch admission decision per audit unit/file driven by a
pure incremental cost-projection over the SAME 3-1 contribution proxy**, so the halt point is a pure function of
the index + the ceiling, byte-stable across runs, and folds real LLM credits into the SAME accountant when
Epic 6 lands — NO new cost authority, NO clock-driven mid-flight interrupt). The halt MUST be deterministic
(NFR-C2 "halts deterministically"); a wall-clock / nondeterministic interrupt is forbidden (AR4).

**What already exists (REUSE verbatim, do NOT rebuild).** This story is the scope-fenced pipeline halt/skip
logic + an additive frozen halt-report contract + the partial-ledger fold — sitting on the fully-built
Epic-1/2 spine and the done 3-1 cost core:

- **`minions_core/apaa/cost/budget_governor.py` (Story 3.1, done — REUSE BY IMPORT, do NOT edit).** The pure
  `BudgetConfig` (`ceiling_credits: int | None`, `None` = no ceiling — OI3), `budget_config_from_budget(budget)`
  (`0 → None`), `account_spend(contributions, *, config, build_cost_proxy) -> CostLedger`, and the frozen
  `CostLedger` carrying `total_credits: int`, `ceiling_credits: int | None`, the deterministic
  **`ceiling_reached: bool`** flag (the REUSED `BudgetGuardrails` `>=`-is-a-breach decision — `total == ceiling`
  is a breach), `breakdown: dict[str, int]`, and the NFR-C1 `baseline_ratio`. **`ceiling_reached` is the
  EXPLICIT seam 3-1 built FOR THIS STORY to query.** REUSE the `account_spend` fold + the `_coerce_breach`
  hard-ceiling decision (BY IMPORT, no fork — §3.3) to decide whether a *projected* cumulative total reaches the
  ceiling. If a pure incremental-projection helper is needed (e.g. "would folding the next unit's contribution
  breach the ceiling?"), add it ADDITIVELY to `budget_governor.py` reusing the SAME `_coerce_breach` decision —
  NEVER a parallel comparison.
- **`minions_core/apaa/ledger/coverage_ledger.py` (Story 1.2 + 2.1, done — REUSE verbatim, do NOT edit).** The
  closed `CoverageDepth` enum (`audited_deep / audited_shallow / tool_scanned_only / inferred / skipped`),
  `CoverageLedgerEntry` (frozen), `CoverageLedger.build(entries)` (sorts by `file_path` — order-independent),
  `counts_by_depth()` / `deep_count()` / `total()`, and the pure `grade_entry(*, file_path, proposed_depth,
  claim_present, ...)`. **A `skipped`-on-exhaustion file is graded `CoverageDepth.SKIPPED` via the EXISTING
  `grade_entry`** (`proposed_depth=CoverageDepth.SKIPPED, claim_present=False`) — the SAME path the pipeline
  already uses for a non-Python / unparseable file (`_grade_non_test_python` / the non-Python branch). It lands
  in the denominator (`total()`), NEVER the deep-% numerator — so the downgrade is honest by construction. Do
  NOT add a new enum member; `skipped` IS the exhaustion-remainder state (architecture §Contract: "Never invent
  a new depth state"). Do NOT fabricate a `audited_*` entry for an unreached file.
- **`minions_core/apaa/verdict/verdict_gate.py` (Story 1.6 + 2.x, done — REUSE verbatim, do NOT edit).** The
  PURE `evaluate_verdict(ledger, findings, *, critical_subsystems_all_deep=True) -> AuditVerdict` fold with the
  LOCKED, frozen thresholds (`INSUFFICIENT_COVERAGE` below 20% deep; `RELEASE_READY` ≥60% deep + 0 blocking + all
  critical deep; else `NOT_READY_FOR_RELEASE`), the `inferred`/`skipped`-never-in-numerator rule (FR8), the
  finding ordering (FR33), and the exit-code map (`0/2/3/1`). **This story re-folds the PARTIAL ledger through
  this UNCHANGED gate** — it does NOT touch the verdict math, thresholds, or exit-code mapping (the
  `INSUFFICIENT_COVERAGE` floor *semantics* are 3.3; this story produces the partial ledger the gate consumes).
- **`minions_core/apaa/pipeline.py` (Story 1.7 + 2.x + 3.1, done — UPDATE, scope-fenced).** The IMPURE
  orchestrator `run_audit_detailed` (intake → stack → index → `_detect_per_file` → `CoverageLedger.build` →
  critical → `evaluate_verdict` → partition plan → `_build_cost_ledger` → `_persist*`) with the typed
  `PipelineError` (AR10), the per-file detect/grade loop in `_detect_per_file`, the `_compute_loc_map` /
  `_build_partition_plan` (the LOC map + the bounded-unit `PartitionPlan` — the **audit-unit granularity** the
  halt can iterate over), `_build_cost_ledger` (the 3-1 cost fold), and `_persist*` (verdict/findings/run-state
  + partitions + cost snapshot). **This story's pipeline touch:** introduce the deterministic halt decision so
  that, once the projected cumulative cost reaches the ceiling, the remaining audit units/files are NOT audited
  (no detector dispatch) but recorded `skipped`-on-exhaustion; build the PARTIAL ledger from the audited entries
  + the skipped-remainder entries; re-fold it through the UNCHANGED gate; build + persist the additive halt
  report; keep the typed `PipelineError` wrapping. WITHOUT changing the verdict math, WITHOUT a new HTTP route,
  WITHOUT the 3.4 resume loop.
- **`minions_core/apaa/index/partitioner.py` (Story 2.4, done — REUSE verbatim).** `compute_loc_by_file`,
  `partition_repository(index, loc_by_file)` → `PartitionPlan` with bounded `Partition`s (≤40 files/15k LOC).
  The **partition is the natural halt-granularity unit** (the architecture's "bounded audit units"); a halt that
  stops at a partition boundary marks every file in the un-started partitions `skipped`. The dev locks the halt
  granularity (per-partition recommended — see Dev Notes; per-file is an acceptable simpler V1 alternative if
  documented) reusing the EXISTING plan/index ordering (sorted, deterministic — AR11).
- **`minions_core/apaa/store/{canonical,envelope,writer,paths,reader}.py` (Story 1.1 + 1.3, done — REUSE).**
  The single serializer (`canonical.dumps_bytes` via `EnvelopeWriter.build`, rejects `float`, `Fraction →
  "num/den"`), `ApaaStoreWriter.write_payload("state", ...)` (content-addressed, containment-checked), and
  `store/reader.py` round-trip. **The halt report + the partial ledger persist to `.apaa/state/` through this
  EXISTING shell** — no second serializer / writer / path resolver.
- **`minions_core/apaa/models.py::AuditRequest` (done — REUSE; `budget`/`commit`/`materiality_bar`/`repo_path`
  + `to_provenance_payload()`).** The `budget` field already carries the ceiling (3-1 gave it enforcement
  meaning). No model re-shape; any new optional field is ADDITIVE (default preserving byte-identity).

**The net-new deliverable of THIS story.** A scope-fenced pipeline halt/skip mechanism + an additive frozen
halt-report contract + the deterministic pre-dispatch admission decision + the partial-ledger fold + the
additive persistence:
1. a **deterministic halt decision** — a PURE projection (over the SAME 3-1 contribution proxy, reusing the
   `_coerce_breach` `>=`-hard-ceiling decision BY IMPORT) of whether continuing to audit the next unit/file
   would reach the configured ceiling; when `ceiling_reached` would become true, audit work STOPS (NFR-C2 — no
   silent overrun) — pure, byte-stable, order-independent (the unit iteration order is the EXISTING sorted
   plan/index order, AR11);
2. the **skip + downgrade** — every not-yet-audited unit/file is recorded `CoverageDepth.SKIPPED` via the
   EXISTING `grade_entry` (`claim_present=False`), so the PARTIAL ledger's deep-% denominator honestly reflects
   what was NOT reached; NO `audited_*` entry is ever fabricated for an unreached file (the keystone honesty
   invariant);
3. the **partial-ledger verdict** — the PARTIAL `CoverageLedger.build(audited_entries + skipped_entries)` is
   re-folded through the UNCHANGED 1.6 `evaluate_verdict` (degraded, never a crash — the floor *semantics* are
   3.3);
4. a frozen **`HaltReport`** (or equivalently-named) additive Pydantic v2 contract (`frozen=True,
   extra="forbid"`, localized `HALT_SCHEMA_VERSION`) recording: whether the run halted on exhaustion
   (`halted_on_exhaustion: bool`), the `total_credits`/`ceiling_credits` at halt, the count + sorted list of
   units/files **assessed** vs **`skipped`-on-exhaustion** (the FR22 "report what it did and did not cover"
   surface), all `int`/`bool`/`str`/sorted-`tuple`, NO `float`, NO absolute host path / source / secret byte;
5. the impure **additive persistence** of the halt report + the partial ledger + the (3-1) cost snapshot to
   `.apaa/state/` via the EXISTING `ApaaStoreWriter.write_payload("state", ...)` (content-addressed) — the seam
   Story 3.4 resumes from;
6. a **non-halting run is byte-identical to today** — when no ceiling is configured (`ceiling_credits is None`)
   OR the projected total never reaches the ceiling, NO unit is skipped-on-exhaustion, NO halt report flags a
   halt, and the verdict/ledger/findings payloads are byte-identical to the 3-1 output (the regression-safe
   path — the keystone back-compat property).

The halt-decision projection + the `HaltReport` model + the partial-ledger fold are PURE (AR8) and join the
import-isolation gate. The persistence WRITE is the impure shell (in the pipeline).

**Carry-forward from the Epic-1/2 retros (CLAUDE.md §9.1 / L1-E11 — this story discharges these items).**
- **AI-E2-1 (process 🟠) — the premature-`status=review` flip.** This story explicitly: (a) does NOT flip
  `status: review` until ALL mandatory test files (`tests/apaa/test_budget_exhaustion.py`, the halt-report
  round-trip, the import-isolation extension, the e2e pipeline halt test) EXIST and pass; (b) fills the Dev
  Agent Record completely (no blank placeholder fields). The orchestrator/dev MUST treat the test-existence
  precondition as a hard gate on the `review` flip.
- **AI-E2-5 (process 🟢) — keep exercising the L1-E11 loop + the three structural gates + the new determinism
  surface.** This story cites the AI-E2-* items it discharges (here); appends any new pure module to
  `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py` (extend, NOT fork); keeps the single-serializer
  AST gate (`test_canonical_single_serializer.py`) green (any halt-report / partial-ledger JSON goes through
  `store/canonical.dumps`, never a direct `json.dumps`); and **applies byte-stability + order-independence
  fixtures to the new halted/partial-run determinism surface** (the AI-E2-5 directive names the
  halted/partial-run surface explicitly — apply it here; the full host-vs-host 3.5 fixture is the next story).
- **AI-E1-1 (test-infra 🟠) — adversarial fixtures + honest-degradation must never fabricate a pass.** Tests
  MUST prove: (a) a `skipped`-on-exhaustion file is NEVER recorded `audited_deep`/`audited_shallow` (the
  honest-degradation keystone — no fabricated completion); (b) the halt report carries NO source / secret /
  absolute-host-path byte (the 1.3/2.3 NFR-S1 precedent — never `repo_path`); (c) a non-ASCII (café/Cyrillic)
  file path in the skipped-remainder round-trips intact in the report; (d) the halt point + the skipped set are
  order-independent + byte-stable.
- **AI-E2-3 (governance 🟢) — central defer register.** If this story files a NEW defer, file it append-only in
  `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (the single canonical APAA defer source), not only in
  the story file. Carry-watch DF-1-7-A (interim `_persist` OSError edge → Epic 3): if the halt-report
  persistence touches the same `_persist` path, record whether DF-1-7-A's OSError-edge hardening is in scope or
  stays deferred — do NOT silently expand scope.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 3.2) + the architecture / PRD. Drivers: **APAA-FR-22** (APAA halts
> on budget exhaustion, marks the remainder `skipped`, downgrades coverage, and reports honestly — never
> fabricating or silently overrunning — the central driver), **APAA-NFR-C2** (an audit never exceeds its
> declared ceiling; on exhaustion it halts DETERMINISTICALLY, no silent overrun), **APAA-NFR-R1** (a
> tool/parse/exhaustion condition degrades to a recorded downgrade — never an uncaught crash or a fabricated
> result — the honest-degradation keystone), **APAA-FR-15/FR-16** (the pure-function gate still produces a
> verdict over the PARTIAL ledger — UNCHANGED gate; the `INSUFFICIENT_COVERAGE` floor *semantics* are Story
> 3.3), **APAA-FR-8** (the `skipped` remainder lands in the denominator, never the deep-% numerator —
> honored by the UNCHANGED gate), **APAA-NFR-D2** (deterministic, zero-LLM-token — the halt projection is a
> pure fold over `int` contributions), **APAA-NFR-P1** (byte-identical halt point + skipped set + report across
> hosts/runs/input-orderings; no float; the full host-vs-host proof is Story 3.5), **APAA-NFR-S1** (no source /
> secret / absolute-host-path bytes in the halt report / partial ledger), **APAA-NFR-S5** (all FS writes
> containment-checked via the 1.3 shell), **APAA-NFR-M2** (frozen, additive-only contracts), **APAA-NFR-M1**
> (≤1200-line files), **AR3** (the exit-code wire contract `0/2/3/1` is UNCHANGED — the gate is reused, not
> modified), **AR4** (no `float`; `int` credits / `bool` flags / sorted `tuple`s / `str`; single canonical
> serializer; no clock/uuid/random/iteration-order — content-derived, AR11), **AR7** (reuse the 3-1
> `account_spend` / `_coerce_breach` `>=`-hard-ceiling decision BY IMPORT — no fork, §3.3), **AR8** (pure/impure
> separation — the halt projection + report model + partial-ledger fold are PURE; the WRITE is the impure
> shell), **AR10** (typed failure, never an uncaught raise / silent coerce — degrade to the existing
> `PipelineError`), **AR11** (`.apaa/` filenames content-derived; unit iteration order = the EXISTING sorted
> plan/index order).
>
> **SCOPE FENCE — Tier-A, single-purpose.** This story delivers ONLY: (1) the DETERMINISTIC HALT decision (a
> pure projection over the 3-1 contribution proxy, reusing the `_coerce_breach` `>=`-hard-ceiling decision BY
> IMPORT — stop audit work before the ceiling is overrun); (2) the SKIP + DOWNGRADE (every unreached unit/file
> recorded `CoverageDepth.SKIPPED` via the EXISTING `grade_entry`, NEVER a fabricated `audited_*`); (3) the
> PARTIAL-LEDGER verdict (re-fold through the UNCHANGED 1.6 gate); (4) the frozen `HaltReport` "what was / was
> not assessed" record; (5) the additive persistence of the halt report + partial ledger to `.apaa/state/` via
> the EXISTING `ApaaStoreWriter`. It does NOT build, and MUST NOT pull forward: the **`INSUFFICIENT_COVERAGE`
> floor verdict semantics / "assessed X% deep" exhaustion-aware rendering** (FR16 floor — **Story 3.3**; the
> frozen 1.6 gate + its thresholds are UNCHANGED here); the **resume-from-disk restore-and-continue loop**
> (FR31 — **Story 3.4**; this story PERSISTS the partial state the 3.4 seam reads, NOT the resume loop); the
> **host-vs-host byte-identical parity proof** (FR32/NFR-P1 — **Story 3.5**; this story's output is
> byte-deterministic + ships an order-independence fixture, the full parity proof is 3.5); the **numeric `$X`
> ceiling default / full-repo budget sizing** (OI3 — **Story 7.1**); the **LLM dispatch port / real LLM credit
> metering** (Epic 6 — V1 cost is the deterministic zero-token work-unit proxy; the halt MECHANISM folds real
> credits into the SAME accountant when Epic 6 lands); any change to the **1.6 verdict gate / 1.2 ledger enum /
> `grade_entry` / 1.1 serializer / 1.4 index / 2.x detectors / 2.4 partitioner / 3.1 `budget_governor`**
> contracts (all frozen/reused — `budget_governor` may gain an ADDITIVE pure projection helper, never a fork).
> It does NOT add a NEW HTTP route / FastAPI surface / UI (§3.7). Halt, skip, downgrade, report, then stop.

**AC1 — APAA halts DETERMINISTICALLY when the projected cost reaches the configured ceiling mid-run — no silent overrun (FR22, NFR-C2, AR7, NFR-D2)**
**Given** an audit with a configured budget ceiling (`AuditRequest.budget > 0` → `BudgetConfig.ceiling_credits =
N`) whose per-unit cost projection over the 3-1 contribution proxy would reach `N` before all audit units/files
are audited
**When** the pipeline runs and projects the cumulative cost unit-by-unit (in the EXISTING sorted plan/index
order — AR11) reusing the 3-1 `_coerce_breach` `>=`-hard-ceiling decision BY IMPORT (the SAME `total >= ceiling`
breach the 3-1 `CostLedger.ceiling_reached` encodes — `total == ceiling` is a breach; no fork / no parallel
comparison — §3.3)
**Then** audit work STOPS at the first unit whose inclusion would reach/exceed the ceiling — no detector is
dispatched for that unit or any later unit (NFR-C2 "never exceeds its declared ceiling; halts deterministically,
no silent overrun"); the halt point is a PURE function of the index + the ceiling (no wall-clock interrupt, no
nondeterministic mid-flight abort — AR4/NFR-D2), so the same repo@commit + ceiling yields the SAME halt point
across hosts/runs and across two input orderings of the units (NFR-P1, proven by an order-independence +
byte-stability test)
**And** when NO ceiling is configured (`ceiling_credits is None` — the OI3 default) OR the projected total never
reaches the ceiling, NO halt occurs, NO unit is skipped-on-exhaustion, and the run audits everything exactly as
it does today (the regression-safe path — AC6).

**AC2 — The un-audited remainder is recorded `skipped`, NEVER fabricated as `audited_*` (FR22, NFR-R1, AR8 — the honest-degradation keystone)**
**Given** a run that halted on exhaustion with one or more un-audited units/files remaining
**When** the partial coverage ledger is built
**Then** every not-yet-audited file is recorded `CoverageDepth.SKIPPED` via the EXISTING `grade_entry(file_path
=..., proposed_depth=CoverageDepth.SKIPPED, claim_present=False)` (the SAME closed-enum honesty state the
pipeline already uses for a non-Python / unparseable file — NO new enum member, architecture §Contract "never
invent a new depth state"); a `skipped`-on-exhaustion file is **NEVER** recorded `audited_deep` /
`audited_shallow` / `tool_scanned_only` / `inferred` (the keystone: honest degradation NEVER fabricates a
pass / a coverage it did not perform — AI-E1-1), verified by a test that asserts the skipped-remainder entries
are exactly `SKIPPED` and that NO `audited_*` entry exists for an unreached file
**And** the `skipped` remainder lands in the partial ledger's denominator (`CoverageLedger.total()`) but NEVER
the deep-% numerator (`deep_count()` counts only `audited_deep`) — so the DOWNGRADE is honest by construction
(FR8 honored by the EXISTING gate): a halt that pushes files to `skipped` lowers the deep-% exactly as much as
the un-reached coverage warrants, with no fabricated inflation.

**AC3 — The pure verdict gate still produces a verdict over the PARTIAL ledger — degraded, never a crash; gate UNCHANGED (FR15, FR16, AR3, NFR-R1)**
**Given** the PARTIAL ledger (audited entries + `skipped`-on-exhaustion remainder)
**When** the verdict is computed
**Then** the UNCHANGED pure 1.6 `evaluate_verdict(partial_ledger, findings, critical_subsystems_all_deep=...)`
folds it into an `AuditVerdict` (degraded), never raising / crashing (NFR-R1) — the gate's frozen thresholds,
`inferred`/`skipped`-never-in-numerator rule, finding ordering, and exit-code map (`0/2/3/1`) are UNCHANGED
(this story touches NO verdict math — the `INSUFFICIENT_COVERAGE` floor *semantics* under exhaustion are Story
3.3); the EXISTING gate ALREADY returns `INSUFFICIENT_COVERAGE` (exit 3) when the partial deep-% falls below the
20% floor and `NOT_READY_FOR_RELEASE` / `RELEASE_READY` per its existing thresholds otherwise — the partial
ledger simply drives the gate's existing decision
**And** the pipeline's typed `PipelineError` wrapping (AR10) is intact — any unexpected failure in the
halt/skip/fold stage degrades to `PipelineError` (exit `1`), never an uncaught traceback; a `verdict_gate`
import / signature change is explicitly OUT of scope (verify no working-tree diff to `verdict_gate.py`).

**AC4 — APAA reports what it DID and did NOT assess — a frozen, no-`float`, secret-safe halt report (FR22, NFR-M2, AR4, NFR-S1)**
**Given** a completed (halted or non-halted) audit
**When** the halt report is built
**Then** it is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`, localized `HALT_SCHEMA_VERSION`)
recording: `halted_on_exhaustion: bool`, the `total_credits: int` reached + the `ceiling_credits: int | None` at
halt, the count + a SORTED `tuple[str, ...]` of the units/files **assessed**, and the count + a SORTED
`tuple[str, ...]` of the units/files **`skipped`-on-exhaustion** (the FR22 "report what it did and did not
cover" — the "examined X; did not cover Z" surface the Epic-4 negative-assurance scope statement folds over) —
ALL `int`/`bool`/`str`/sorted-`tuple`, **NO `float` anywhere** (the canonical serializer rejects it), NO
volatile `run_id`/`created_at` in the hashed payload (NFR-D3)
**And** the report carries ONLY repo-relative POSIX paths + `int`/`bool`/`str` provenance — NEVER an absolute
host path, NEVER source/secret bytes, NEVER `repo_path` (the 1.3 DN-3 / 2.3 / `to_provenance_payload()`
precedent — NFR-S1), verified by an AI-E1-1-style assertion that no source/secret/absolute-host-path byte
appears in the persisted report
**And** a NON-halted run (no ceiling, or the ceiling never reached) produces a report with
`halted_on_exhaustion = False`, an EMPTY skipped-on-exhaustion list, and the full assessed list — so the report
is always populated + honest, and its presence does NOT change the verdict/ledger/findings payloads (the report
is purely additive — AC6).

**AC5 — The halt report + partial ledger persist to `.apaa/state/` via the EXISTING containment shell — content-addressed, round-trip-stable (NFR-S5, NFR-S1, AR4, AR11, FR25)**
**Given** a completed accounting + halt fold + report
**When** the artifacts are persisted
**Then** the writes go through the EXISTING `ApaaStoreWriter.write_payload("state", payload, schema_version=...,
producer="apaa.pipeline.halt_report")` (or equivalent) — the bytes are `EnvelopeWriter.build(...)` →
`store/canonical.dumps_bytes` (single serializer, no second `json.dumps` — the AST gate enforces it), the
filename is content-addressed `<content_hash>.json` (never arrival order — AR11), and the `ApaaStorePaths`
`is_relative_to` containment check guards the path (NFR-S5) — REUSING the 1.1/1.3 spine with NO second writer /
path resolver / serializer; the PARTIAL ledger persists through the SAME `_persist` run-state path the pipeline
already uses (the partial ledger IS the ledger snapshot for a halted run)
**And** re-reading via `store/reader.py` reconstructs an EQUAL halt-report model + round-trips byte-identically
(NFR-P1), verified by a round-trip test (mirrors `test_store_roundtrip` / the 3-1 `test_cost_snapshot_roundtrip`)
**And** the persisted artifacts are the seam **Story 3.4** (resumability) reads to restore the prior partial
coverage + the accumulated spend across a re-invoke — this story PERSISTS them; it does NOT build the
restore-and-continue resume loop (3.4); carry-watch DF-1-7-A (interim `_persist` OSError edge → Epic 3): if the
halt-report persistence touches `_persist`, record whether the OSError-edge hardening is in scope or stays
deferred (do NOT silently expand scope).

**AC6 — A non-halting run is BYTE-IDENTICAL to the 3-1 output on the verdict/ledger/findings artifacts (NFR-P1, the regression-safe keystone)**
**Given** a run with NO ceiling configured (`ceiling_credits is None`) OR a ceiling the projected total never
reaches
**When** the audit runs end-to-end
**Then** NO unit is skipped-on-exhaustion, the halt report flags `halted_on_exhaustion = False`, and the
verdict / coverage-ledger / findings artifacts (content-addressed names AND on-disk bytes) are BYTE-IDENTICAL to
the pre-3.2 (3-1) output — the halt mechanism + the halt report are purely additive when no halt fires (the
keystone back-compat property), proven by an e2e test that compares the verdict + ledger + findings bytes across
a pre-3.2-equivalent run and a 3.2 no-halt run.

**AC7 — The new pure logic is PURE, frozen-contract, deterministic, typed-error, import-isolated; the whole suite green; mypy clean; ≤1200 lines (NFR-D2, NFR-P1, AR8, AR10, AR7, M1, M2)**
**Given** the new halt-decision projection + the `HaltReport` model (in `cost/budget_governor.py` or a new
sibling `cost/exhaustion.py` — lock the placement) + any halt helper
**When** they are imported and exercised in unit tests
**Then** the halt projection + the report build + the partial-ledger fold perform NO filesystem I/O, NO clock
read (`datetime.now`/`time.time`), NO `uuid4`/`os.getpid()`/`random`, NO LLM/network call, NO dict/`set`-
iteration-order reliance — they are PURE functions over in-memory inputs (the persistence WRITE is the impure
pipeline shell)
**And** any new model is a frozen Pydantic v2 model (`frozen=True, extra="forbid"` — the 1.1/1.2/3.1 precedent)
with a localized `schema_version` (additive-only, NFR-M2); NO `float` anywhere (credits + counts are `int`;
flags are `bool`; paths/ids are `str`; lists are sorted `tuple` — AR4); any JSON rendering routes through
`store/canonical.dumps` (the single 1.1 serializer — no second `json.dumps`); the reuse of the 3-1
`_coerce_breach` / `account_spend` is BY IMPORT, FastAPI-free (AR7 — the import-isolation gate proves it)
**And** a malformed input (a `float` projected cost, a negative ceiling, a non-`int` credit) raises a typed
error — the EXISTING `BudgetGovernorError` (`ValueError` subclass) reused, or a localized sibling — never a
silent coerce / bare `except: pass` / `print()` in library code (AR10); any halt-stage failure in the pipeline
degrades to the existing typed `PipelineError` (exit `1`), never an uncaught traceback
**And** the new module (if a new file) is appended to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py`
(extend, do NOT fork) and importing it does NOT transitively import `fastapi`/`uvicorn`/`starlette` or any
LLM/api module (assert absence from `sys.modules`)
**And** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` passes (including the
new `tests/apaa/test_budget_exhaustion.py`: AC1 deterministic halt point [order-independence + byte-stability;
the `>=`-hard-ceiling decision REUSED from the 3-1 core incl. the at-ceiling boundary; no-ceiling / never-reached
→ no halt]; AC2 the skip+downgrade [unreached files exactly `SKIPPED`; NO fabricated `audited_*`; `skipped` in
the denominator not the numerator]; AC3 the partial-ledger verdict over the UNCHANGED gate [degraded, no crash];
AC4 the frozen no-`float` `HaltReport` [assessed vs skipped lists; `halted_on_exhaustion`; secret/abs-path/
source-byte absent; non-ASCII path round-trip]; AC5 the round-trip; AC6 the no-halt byte-identity; AC7 purity
[AST scan] / frozen / no-`float` / typed-error / single serializer / FastAPI-free import); a
`tests/apaa/test_halt_report_roundtrip.py` (or extend `test_store_roundtrip.py`) proves the halt-report
write→read round-trip (equal model + byte-identical re-serialize; content-addressed filename; no absolute path /
source byte); `mypy` is clean on the new + edited modules; the new source file(s) are ≤1200 lines (NFR-M1) and
cite their `APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in the module docstring. **Test area `APAA-COST`**
(`TC-APAA-COST-001-NN`, continuing the 3-1 cost area) — lock the area in the docstring. The 1.6 gate / 1.2 ledger
/ 1.1 serializer / 1.4 index / 2.x detectors / 2.4 partitioner / 3.1 `budget_governor` (except an ADDITIVE pure
projection helper) contracts are UNCHANGED (verify no working-tree diff to those frozen surfaces). The mandatory
test files MUST exist + pass BEFORE the story flips to `status: review` (AI-E2-1).

## Tasks / Subtasks

- [x] **Task 0 — Verify the existing reuse surface (verify-and-lock)** (AC: 1, 2, 3, 5)
  - [x] Re-read `cost/budget_governor.py` — confirmed `account_spend`, `CostLedger.ceiling_reached`, and the
        module-private `_coerce_breach(*, total_credits, ceiling_credits)`. **DECISION (b):** added a public
        `would_breach(...)` + `project_halt_point(...)` in a NEW sibling `cost/exhaustion.py` that import
        `_coerce_breach` BY IMPORT and delegate to it — no fork of the comparison.
  - [x] Re-read `ledger/coverage_ledger.py` — confirmed `CoverageDepth.SKIPPED` + `grade_entry(SKIPPED,
        claim_present=False)` + `CoverageLedger.build` (sorts) + `total()`/`deep_count()`. Skipped-remainder
        uses the EXISTING grade_entry SKIPPED path; no new enum member; no fabricated audited_*.
  - [x] Re-read `verdict/verdict_gate.py` — confirmed `evaluate_verdict` PURE + UNCHANGED + returns
        `INSUFFICIENT_COVERAGE` below 20% + excludes `skipped` from the numerator (FR8). Re-folds the PARTIAL
        ledger through the UNCHANGED gate; floor semantics deferred to 3.3 (no working-tree diff).
  - [x] Re-read `pipeline.py` — confirmed `run_audit_detailed`, `_detect_per_file`, `_compute_loc_map`,
        `_build_cost_ledger`, `_persist`/`_persist_cost_ledger`, `PipelineError`. Locked the minimal
        scope-fenced halt/skip touch.
  - [x] Re-read `index/partitioner.py` + `store/{canonical,writer,reader}.py`. REUSE verbatim. **Halt
        granularity LOCKED = per-file over the sorted index** (simplest, finest-grained, already the detect-loop
        order).
- [x] **Task 1 — The deterministic halt-projection core (PURE)** (AC: 1, 2, 7)
  - [x] Added PURE `project_halt_point(units, *, config) -> HaltProjection` in the NEW `cost/exhaustion.py`
        (docstring cites drivers + AR7 reuse + the deterministic-halt rule + the 3.3/3.4/3.5/7.1 fences +
        APAA-COST). Returns the first-breaching halt index over the cumulative `_coerce_breach` decision
        (REUSED BY IMPORT). No ceiling → no halt. Pure / order-independent / byte-stable (pinned by tests).
        Unit granularity = per-file (`CostUnit{path, cost:int}`).
  - [x] Typed-error path: localized `ExhaustionError` (ValueError subclass) on a `float`/negative/non-`int`
        cost / negative ceiling / non-`str` path / non-`CostUnit` element — never a silent coerce (AR10).
- [x] **Task 2 — The frozen `HaltReport` contract (PURE)** (AC: 4, 7)
  - [x] Frozen `HaltReport` (`frozen=True, extra="forbid"`, `HALT_SCHEMA_VERSION="1"`): `halted_on_exhaustion`,
        `total_credits`, `ceiling_credits: int|None`, sorted `assessed_files` + `assessed_count`, sorted
        `skipped_on_exhaustion_files` + `skipped_on_exhaustion_count`. NO float; no abs-path/source/secret; no
        volatile run_id/created_at. `to_canonical_payload()` = `model_dump(mode="json")` (all leaves
        int/bool/str/tuple[str] — canonical-safe, no Fraction).
- [x] **Task 3 — (Scope-fenced) pipeline halt → skip → downgrade → report wiring** (AC: 1, 2, 3, 5, 6)
  - [x] In `run_audit_detailed`: build the `BudgetConfig`, project the halt over the sorted index (per-file
        `_unit_cost` proxy = 1 non-Python / 5 Python — sums to the 3-1 total), split AUDITED (run
        `_detect_per_file`) vs SKIPPED (graded `CoverageDepth.SKIPPED`, no detector). Build the PARTIAL ledger,
        re-fold through the UNCHANGED `evaluate_verdict`, build the `HaltReport`, persist it additively via
        `_persist_halt_report` → `write_payload("state", ...)`. Kept the 3-1 cost build/persist + the typed
        `PipelineError`. Halt-report locator added to `AuditResult.locators`. No verdict-math change, no new enum
        state, no resume loop, no wall-clock interrupt. No-halt run byte-identical (AC6).
  - [x] **V1 halt-model decision LOCKED in the pipeline + exhaustion docstrings + Change Log** — a deterministic
        PRE-DISPATCH per-unit admission projection (forward-compatible to Epic 6 real LLM credits via the SAME
        `_coerce_breach` accountant; no new authority; no wall-clock interrupt).
- [x] **Task 4 — Tests** (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] `tests/apaa/test_budget_exhaustion.py` (TC-APAA-COST-001-70..89) — AC1 deterministic halt
        (order-independence + byte-stability + `>=`-hard-ceiling reuse incl. at-ceiling boundary; no-ceiling /
        never-reached → no halt); AC2 skip+downgrade (unreached files exactly SKIPPED; NO fabricated audited_*;
        skipped in denominator not numerator via the REAL gate); AC3 partial-ledger verdict over the UNCHANGED
        gate (degraded, no crash); AC4 frozen no-float HaltReport (assessed/skipped; halted flag; secret/abs-
        path/source-byte absent; non-ASCII café/Cyrillic round-trip); AC7 purity AST scan / frozen / typed-error.
  - [x] `tests/apaa/test_halt_report_roundtrip.py` (TC-APAA-COST-001-90..94) — write_payload→read_envelope
        round-trip: equal model + byte-identical re-serialize; content-addressed filename; byte-identical across
        hosts; no abs-path/source byte.
  - [x] Extended `tests/apaa/test_pipeline_signature_demo.py` (TC-APAA-PIPELINE-001-17..19) — a budget-exhausted
        run halts + skips + persists the halt report + degrades the verdict; ceiling-below-first-unit →
        INSUFFICIENT_COVERAGE/exit 3; a no-halt run is byte-identical on verdict/ledger/findings (AC6).
- [x] **Task 5 — Extend the import-isolation gate** (AC: 7)
  - [x] Appended `minions_core.apaa.cost.exhaustion` to `_MODULES_UNDER_GUARD` in
        `tests/apaa/test_no_web_imports.py` (extended, not forked).
- [x] **Task 6 — Run + mypy + the AI-E2-1 pre-`review` test-existence precondition** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → 595 passed.
  - [x] `mypy minions_core/apaa/cost/exhaustion.py minions_core/apaa/pipeline.py --ignore-missing-imports` →
        Success: no issues found in 2 source files.
  - [x] **AI-E2-1 GATE:** all 3 mandatory test files exist + pass BEFORE the `review` flip; Dev Agent Record
        filled completely (no blank placeholders).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **Honest degradation NEVER fabricates a pass (the keystone, FR22/NFR-R1/AI-E1-1).** An audit that runs out of
  budget MUST degrade honestly: the un-audited remainder is recorded `skipped` (examined-in-the-denominator),
  NEVER `audited_deep`/`audited_shallow`/`tool_scanned_only`/`inferred`. A `skipped`-on-exhaustion file that
  showed up as `audited_*` would be a fabricated completion — the lethal failure this story exists to prevent.
  A test MUST assert the skipped-remainder entries are exactly `SKIPPED` and that NO `audited_*` entry exists for
  an unreached file.
- **Deterministic halt — NO wall-clock interrupt (NFR-C2 "halts deterministically", AR4/NFR-D2).** The halt
  point MUST be a PURE function of the index + the ceiling, not a nondeterministic mid-flight abort. Project the
  cumulative cost unit-by-unit (in the EXISTING sorted plan/index order) and stop at the first unit whose
  inclusion would breach the ceiling. The same repo@commit + ceiling → the SAME halt point across hosts/runs.
- **Reuse the 3-1 `>=`-hard-ceiling decision BY IMPORT, never fork (AR7/§3.3).** The breach decision is the
  3-1 `_coerce_breach` (which itself reuses the Minions `BudgetGuardrails.evaluate_worker_spend` `>=`-is-a-breach
  semantic). The halt projection maps a *projected cumulative total* onto the SAME comparison — no second budget
  authority, no parallel re-derived comparison. The exact at-ceiling boundary (`total == ceiling`) is a BREACH
  (the 3-1 / TC-COST-001-46 boundary). If `_coerce_breach` is module-private, promote it to a public predicate
  or add a public sibling that delegates to it — never copy the comparison.
- **The verdict gate is UNCHANGED — the floor semantics are Story 3.3 (the scope crux).** This story re-folds
  the PARTIAL ledger through the EXISTING frozen 1.6 `evaluate_verdict`. The gate ALREADY: returns
  `INSUFFICIENT_COVERAGE` below the 20% deep floor (`INSUFFICIENT_COVERAGE_FLOOR = Fraction(1, 5)`, floor-wins
  precedence), excludes `skipped` from the deep-% numerator (FR8), orders findings (FR33), and maps exit codes
  (`0/2/3/1`). So a halt that pushes files to `skipped` NATURALLY drives a lower deep-% → the gate's existing
  decision (often `INSUFFICIENT_COVERAGE` for an early halt). Story 3.3 wires the floor verdict's
  *exhaustion-aware scope statement / "assessed X% deep; floor 20%" rendering*; **this story does NOT change the
  verdict math, thresholds, or exit-code mapping** — verify no working-tree diff to `verdict_gate.py`.
- **No floats — ever (AR4/NFR-P1).** Credits + counts are `int`; flags are `bool`; paths/ids are `str`; lists
  are sorted `tuple[str, ...]`. The halt report has no ratio (the NFR-C1 `Fraction` lives on the 3-1
  `CostLedger`), so `model_dump(mode="json")` is canonical-safe for the report; the canonical serializer rejects
  `float` as the determinism backstop. The 3-1 `to_canonical_payload` LIVE-`Fraction` workaround is only needed
  if the report carries a `Fraction` — it does not in the recommended shape.
- **Pure/impure separation (master rule, AR8).** The halt projection + the `HaltReport` build + the
  partial-ledger fold are PURE — over in-memory inputs; they never open a file, read a clock, or call an LLM. The
  IMPURE shell is the persistence WRITE (in the pipeline, via `write_payload`) + the detect-stage source reads
  (already impure). ✅ a pure `project_halt_point(units, config)` · ❌ a halt that reads `time.time()` mid-loop.
- **Zero LLM tokens in V1 (NFR-D2).** The pipeline calls NO LLM (the dispatch port is Epic 6), so V1 cost is the
  deterministic, zero-token work-unit proxy 3-1 folds. The halt MECHANISM is built so that when Epic 6 wires the
  LLM port, real credits fold into the SAME accountant + the SAME halt projection. Document this: the V1 halt
  point is computed over a deterministic proxy, not a billed LLM total.
- **The skip granularity (lock + document).** The partition (the 2.4 bounded audit unit) is the natural halt
  granularity — a halt that stops at a partition boundary marks every file in the un-started partitions
  `skipped`. Per-file is an acceptable simpler V1 alternative (iterate the sorted index entries, project per
  file, skip the remainder). Recommended: per-file over the sorted index (simplest, finest-grained, already the
  detect-loop order) — but lock the choice + document it; the assessed/skipped sets in the `HaltReport` are
  file-level either way.
- **The snapshot is the Story 3.4 resume seam, persisted not resumed.** Persist the halt report + the partial
  ledger to `.apaa/state/` (content-addressed, the 1.3 store). Story 3.4 reads them to restore the prior
  coverage + the accumulated spend on a re-invoke with a raised budget; this story does NOT build the
  restore-and-continue loop. Keep the halt-report shape simple + additive so 3.4 does not inherit a richer shape
  than needed.
- **Determinism (NFR-P1).** The halt point, the skipped set, and the report are a pure deterministic function of
  the units + config; the same repo@commit + config → a byte-identical halt + report; two input orderings of the
  units → the identical halt point + sorted assessed/skipped sets. Pin a byte-stability + order-independence test
  (the AI-E2-5 directive names the halted/partial-run determinism surface explicitly). The full host-vs-host
  parity proof + the canonical halted-run fixture is Story 3.5.
- **Error/degradation → typed, never crash (AR10).** A malformed halt input (a `float` projected cost / negative
  ceiling / non-`int`) → the EXISTING typed `BudgetGovernorError` (or a localized sibling). NO bare
  `except: pass`, NO `print()` in library code, NO silent coerce. A halt-stage failure in the pipeline degrades
  to the existing `PipelineError` (exit `1`). The verdict gate over the partial ledger never crashes (it is a
  total pure fold).
- **No absolute host paths / secrets in artifacts (NFR-S1).** The halt report carries repo-relative POSIX paths
  + `int`/`bool`/`str` provenance only — never `repo_path`, never source/secret bytes (the 1.3 DN-3 / 2.3 /
  `to_provenance_payload()` precedent).
- **Headless / import boundary (§3.7, AR7/AR9).** No UI, no HTML/CSS/JS, no FastAPI route. The new pure logic
  takes no token, registers no route, imports only the FastAPI-free 3-1 cost core (which imports the FastAPI-free
  `budget_guardrails` leaf), and joins `_MODULES_UNDER_GUARD` if it is a new file.

### The halt model in a single-pass zero-token V1 pipeline (the central design call — lock + document)

The V1 pipeline computes cost ONCE, after the single-pass detect/grade stage (3-1 `_build_cost_ledger` folds
`files_indexed` / `python_files` / `detector_passes` over the WHOLE index). There is no incremental per-file
billing loop. So "halt mid-run" cannot mean "interrupt a running LLM dispatch" (there is no LLM in V1). The
deterministic, honest V1 model is a **pre-dispatch admission projection**:

| concept | source | form |
|---|---|---|
| audit units (ordered) | the EXISTING sorted index entries (or 2.4 partitions) | `tuple[str, ...]` (file-level recommended) |
| per-unit projected cost | the SAME 3-1 contribution proxy, per unit (e.g. a fixed `detector_passes`-per-Python-file proxy) | `int` credits per unit |
| ceiling | `BudgetConfig.ceiling_credits` (3-1; `None` = no ceiling) | `int | None` |
| halt point | first unit index where cumulative `_coerce_breach(total, ceiling)` is True | `int | None` (None = no halt) |
| assessed units | units before the halt point (run the EXISTING detectors) | sorted `tuple[str, ...]` |
| skipped-on-exhaustion units | units at/after the halt point (graded `SKIPPED`, no detector) | sorted `tuple[str, ...]` |

The dev locks the EXACT per-unit cost proxy (it MUST be a deterministic, content-derived `int` per unit — e.g.
the per-Python-file detector-pass count the 3-1 fold already uses, attributed per file; document the attribution
so the cumulative projection matches the 3-1 whole-run total when no halt fires). The halt is a PURE function of
(ordered units, per-unit proxy, ceiling) — byte-stable, order-independent. When Epic 6 wires the LLM port, the
per-unit proxy is replaced by the real per-unit LLM credit estimate folding into the SAME `_coerce_breach`
decision — NO new authority. This is the cut-order-sanctioned V1 limitation (the mechanism is forward-compatible).

### Decisions the dev must lock (record in the docstring + Change Log)

- **Module placement** — the halt projection in `cost/budget_governor.py` (additive, alongside `account_spend`)
  vs a new pure `cost/exhaustion.py` sibling. Prefer the new sibling ONLY if `budget_governor.py` approaches the
  1200-line limit (it is 343 lines today — additive is fine); avoid a speculative split. Lock + document.
- **`_coerce_breach` reuse** — promote it to a public predicate, or add a public `project_halt_point(...)` /
  `would_breach(total, ceiling)` that delegates to it. Lock the choice (no fork of the comparison).
- **Halt granularity** — per-file over the sorted index (recommended) vs per-partition (2.4 units). Lock.
- **Per-unit cost proxy attribution** — how the 3-1 whole-run contribution proxy is attributed per unit so the
  cumulative projection is consistent with the 3-1 total (document the attribution).
- **`HaltReport` field names + shape** — lock the names + `HALT_SCHEMA_VERSION` + the assessed/skipped list keys
  (additive-only — the 3.4 resume seam folds over it).
- **Typed error type** — reuse `BudgetGovernorError`, or a localized sibling. Lock.
- **Test area** — `APAA-COST` (`TC-APAA-COST-001-NN`, continuing the 3-1 cost area). Lock the choice.

### Precedent inherited from Stories 1.1–1.7 + 2.1–2.6 + 3.1 (done) — honor these decisions

- **No second serializer / reuse the 1.1 spine.** Any `.apaa/` bytes go through `store/canonical.dumps_bytes`
  via `EnvelopeWriter.build` + the writer; the AST single-serializer gate enforces it (kept green per AI-E2-5).
- **Reuse the 1.3 store shell + `write_payload`.** `ApaaStorePaths` (containment, `state/`) +
  `ApaaStoreWriter.write_payload("state", ...)` provide the content-addressed, envelope-wrapped,
  containment-checked write. REUSE verbatim; mirror the 1.3 / 3-1 round-trip golden.
- **Reuse the 3-1 cost core + `_coerce_breach` BY IMPORT (AR7), FastAPI-free.** The hard-ceiling `>=` decision is
  the single authority — no fork (§3.3).
- **Reuse the 1.2 `grade_entry` SKIPPED path + the closed `CoverageDepth` enum.** No new enum member; `skipped`
  IS the exhaustion-remainder state. Reuse `CoverageLedger.build` (sorts entries — order-independent).
- **Reuse the 1.6 `evaluate_verdict` UNCHANGED.** Re-fold the partial ledger through it; do not touch the math.
- **Frozen `extra="forbid"` models** (1.1 `Envelope`, 1.2 `Recording`/`CoverageLedger`, 1.6 `AuditVerdict`,
  3.1 `BudgetConfig`/`CostLedger`): the `HaltReport` follows the same pattern with a localized `schema_version`.
- **`bool`/`int`/sorted-`tuple`/`str` over `float`** — every halt signal is non-`float`; the 1.1 serializer
  rejects it.
- **Content-derived filenames, never arrival order (AR11)** — the halt report lands at a content-addressed
  `<content_hash>.json` in `state/`; the unit iteration order is the EXISTING sorted index/plan order.
- **No absolute host paths in artifacts (NFR-S1 spirit, 1.3 DN-3 / 2.3)** — the halt report carries
  repo-relative paths + `int`/`bool`/`str` provenance only; the run-state never records `repo_path`.
- **`apaa_version`/`schema_version` single source** — `minions_core/apaa/__init__.py::__version__` (`"0.1.0"`);
  per-module `schema_version` is a localized constant, never env/clock.
- **Import-isolation gate seeded, extend it (AI-E1-4/AI-E2-5)** — append a new module to
  `_MODULES_UNDER_GUARD`; do not fork.

### Source tree — files to create / update

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/cost/budget_governor.py` | UPDATE (additive) OR keep frozen | add the PURE halt-projection helper (+ promote/`would_breach` reuse of `_coerce_breach`) IF placed here; else leave frozen and place the projection in `cost/exhaustion.py` |
| `minions_core/apaa/cost/exhaustion.py` | NEW (if chosen) | FR22 — PURE halt projection (`project_halt_point` reusing the 3-1 `>=`-hard-ceiling decision BY IMPORT) + frozen `HaltReport` (`int`/`bool`/`str`/sorted-`tuple`, no `float`) + typed error; docstring cites drivers + AR7 + the deterministic-halt rule + the 3.3/3.4/3.5/7.1 fences |
| `minions_core/apaa/pipeline.py` | UPDATE (scope-fenced) | compute the halt point, split audited vs skipped-on-exhaustion, grade the remainder `SKIPPED` (no detector), build the PARTIAL ledger, re-fold through the UNCHANGED gate, build + persist the halt report additively; NO verdict-math change, NO new enum state, NO resume loop (3.4), NO wall-clock interrupt; a no-halt run byte-identical to today |
| `tests/apaa/test_budget_exhaustion.py` | NEW | deterministic halt (order-independence + byte-stability + `>=`-hard-ceiling reuse incl. at-ceiling boundary; no-ceiling/never-reached → no halt) + skip+downgrade (unreached files exactly `SKIPPED`; NO fabricated `audited_*`; `skipped` in denominator not numerator) + partial-ledger verdict over the UNCHANGED gate + frozen no-`float` `HaltReport` (assessed/skipped; secret/abs-path/source-byte absent; non-ASCII round-trip) + purity/frozen/typed-error/single-serializer/FastAPI-free |
| `tests/apaa/test_halt_report_roundtrip.py` | NEW (or extend `test_store_roundtrip.py`) | `write_payload("state", ...)` → reader round-trip: equal model + byte-identical; content-addressed filename; no absolute path/source byte |
| `tests/apaa/test_pipeline_signature_demo.py` | UPDATE | +e2e: a budget-exhausted run halts + skips + persists the report + degrades the verdict over the partial ledger; a no-halt run byte-identical to the 3-1 verdict/ledger/findings (AC6) |
| `tests/apaa/test_no_web_imports.py` | UPDATE (if `cost/exhaustion.py` is new) | extend `_MODULES_UNDER_GUARD` with `minions_core.apaa.cost.exhaustion` |

Do NOT modify `verdict/verdict_gate.py`, `ledger/coverage_ledger.py`, `ledger/recording.py`,
`ledger/depth_semantics.py`, `ledger/critical_subsystems.py`, `index/ast_index.py`, `index/partitioner.py`,
`store/canonical.py`, `store/envelope.py`, `store/paths.py`, `store/writer.py`, `store/reader.py`, or any
detector (frozen/reused contracts — verify no working-tree diff after the story). `cost/budget_governor.py` may
gain an ADDITIVE pure projection helper (or a public reuse of `_coerce_breach`) but its existing `BudgetConfig`/
`CostLedger`/`account_spend`/`baseline_ratio` contracts MUST stay byte-identical. `minions_core/cost/budget_guardrails.py`
is REUSED BY IMPORT (transitively, via the 3-1 core) and MUST NOT be edited.

### Scope fences (do NOT pull forward)

- ❌ The **`INSUFFICIENT_COVERAGE` floor verdict semantics / "assessed X% deep; floor 20%" exhaustion-aware
  rendering** (FR16 floor) — **Story 3.3**. This story re-folds the partial ledger through the UNCHANGED 1.6
  gate; the gate's existing thresholds decide. NO verdict-math change.
- ❌ The **resume-from-disk restore-and-continue loop** (FR31) — **Story 3.4**. This story PERSISTS the partial
  ledger + the halt report (the seam 3.4 reads); it does NOT build the resume loop.
- ❌ The **host-vs-host byte-identical parity proof + the canonical halted-run fixture** (FR32/NFR-P1) —
  **Story 3.5**. This story's output is byte-deterministic + ships an order-independence/byte-stability fixture;
  the full host parity proof is 3.5.
- ❌ The **numeric `$X` ceiling default / full-repo budget sizing** (OI3) — **Story 7.1**. NO hardcoded numeric
  default here.
- ❌ The **LLM dispatch port / real LLM credit metering** (Epic 6). V1 cost is the deterministic zero-token
  work-unit proxy; the halt MECHANISM folds real credits into the SAME accountant when Epic 6 lands.
- ❌ A **new `CoverageDepth` enum member** — `skipped` IS the exhaustion-remainder state (architecture §Contract:
  "never invent a new depth state"). Reuse the EXISTING `grade_entry` SKIPPED path.
- ❌ Any change to the **1.6 verdict gate / 1.2 ledger enum / `grade_entry` / 1.1 serializer / 1.4 index / 2.x
  detectors / 2.4 partitioner / 3.1 `BudgetConfig`/`CostLedger`/`account_spend`** contracts — all frozen/reused.
- ❌ A **new HTTP route / FastAPI surface / UI** (§3.7).

### Deferred-work seam (record if surfaced; do NOT build)

- **DF-1-7-A** — interim `_persist` OSError edge → Epic 3 (open per the 1.7 review). If the halt-report
  persistence touches the same `_persist` path, evaluate whether DF-1-7-A's OSError-edge hardening is in scope or
  stays deferred; record the decision (do NOT silently expand scope).
- **The V1-cost-is-a-proxy limitation** — V1 has no real LLM credit metering (the dispatch port is Epic 6), so
  the halt projects over a deterministic zero-token work-unit proxy, not a billed total. This is the
  cut-order-sanctioned V1 limitation (the mechanism is forward-compatible). If a NEW defer beyond this surfaces
  during dev (e.g. the per-unit proxy proves too coarse to halt at a meaningful boundary for the dogfood),
  record it with the CC-3 six-field schema in `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`; do NOT
  build it here.
- **AI-E2-3 (defer-register consolidation)** — the central `deferred-work.md` is the single canonical APAA defer
  source; if this story files a new defer, file it there (append-only), not only in the story file.

## References

- Epic: `_bmad-output/design-artifacts/ArgusAgent/epics.md` §"Epic 3" → Story 3.2 (halt → skip → downgrade → report on
  budget exhaustion — the two ACs: deterministic halt + mark-remainder-`skipped` + downgrade + report honestly,
  no silent overrun; the pure gate still produces a degraded verdict over the partial ledger, never a crash);
  §"Open delivery inputs — LOCKED 2026-06-18" → OI3 (budget-ceiling `$X` deferred to Story 7.1; mechanism
  unaffected); the FR Coverage Map (FR22 → Epic 3; FR16 floor → Epic 1 gate + Story 3.3 floor-under-exhaustion).
- PRD: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` → FR22 (halt on budget exhaustion, mark remainder
  `skipped`, downgrade, report honestly — never fabricating / silently overrunning), NFR-C2 (never exceed the
  ceiling; halt deterministically, no silent overrun), NFR-R1 (a tool/parse/exhaustion condition degrades to a
  recorded downgrade — never an uncaught crash or a fabricated result), FR16 (the 20% floor — Story 3.3), FR8
  (`inferred`/`skipped` never satisfy a gate), NFR-D2 (zero-token deterministic), NFR-P1 (byte-identical),
  NFR-S1/S5 (no leak / containment), NFR-M1/M2 (file-size / frozen additive).
- Architecture: `_bmad-output/design-artifacts/ArgusAgent/architecture.md` §"Core Architectural Decisions" → Decision
  E (Cost Governance: reuse `cost/budget_guardrails` BY IMPORT; **halt→skip→downgrade→report**); §"Implementation
  Patterns" → Error/Degradation Patterns ("Failure → typed finding, never an uncaught raise; the run still
  produces a verdict (degraded → `INSUFFICIENT_COVERAGE`)"), Determinism Patterns (no float / single serializer /
  no clock-uuid-random), Pure/Impure Separation, Contract/Format Patterns ("the coverage-ledger enum is closed
  … never invent a new depth state"); §"Project Structure" → `cost/budget_governor.py` (FR21/FR22 — wraps
  `cost/budget_guardrails`; halt→skip→downgrade); AR3/AR4/AR7/AR8/AR10/AR11.
- Done predecessor (Story 3.1): `_bmad-output/design-artifacts/ArgusAgent/stories/3-1-budget-ceiling-configuration-cost-accounting.md`
  (the `BudgetConfig`/`account_spend`/`CostLedger`/`ceiling_reached`/`_coerce_breach` cost core — `ceiling_reached`
  was exposed EXPLICITLY "for Story 3.2 to query, exposed not acted on"; the V1-cost-is-a-proxy framing; the
  Fraction-not-float / single-serializer / frozen-contract precedent; DF-3-1-A `ceiling_credits` lacks `ge=0`
  — defensive-only, not reachable through the operator seam).
- Reuse targets (BY IMPORT / verbatim — unedited): `minions_core/apaa/cost/budget_governor.py` (`account_spend` /
  `_coerce_breach` / `CostLedger.ceiling_reached`), `minions_core/apaa/ledger/coverage_ledger.py`
  (`CoverageDepth.SKIPPED` / `grade_entry` / `CoverageLedger.build`), `minions_core/apaa/verdict/verdict_gate.py`
  (`evaluate_verdict` — UNCHANGED), `minions_core/apaa/index/partitioner.py` (`PartitionPlan` / sorted units),
  `minions_core/apaa/pipeline.py` (`run_audit_detailed` / `_detect_per_file` / `_compute_loc_map` / `_persist` /
  `PipelineError`), `minions_core/apaa/store/{canonical,envelope,writer,paths,reader}.py`.
- Retros (carry-forward): `_bmad-output/design-artifacts/ArgusAgent/epic-1-retro-2026-06-21.md` (AI-E1-1 adversarial
  fixtures — honest-degradation must never fabricate a pass; AI-E1-4 gates extended-not-forked);
  `_bmad-output/design-artifacts/ArgusAgent/epic-2-retro-2026-06-24.md` (AI-E2-1 pre-`review` test-existence guard /
  premature status flip; AI-E2-3 defer-register consolidation; AI-E2-5 L1-E11 loop + the three structural gates
  + **byte-stability + order-independence fixtures on the new halted/partial-run determinism surface** — named
  explicitly for this Epic-3 work; §6 Epic-3 readiness).
- Deferred-work: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (the central APAA defer register;
  DF-1-7-A interim `_persist` OSError edge → Epic 3; DF-3-1-A `ceiling_credits` `ge=0` defensive nit).

## Dev Agent Record

### Context Reference

- Story file: `_bmad-output/design-artifacts/ArgusAgent/stories/3-2-halt-skip-downgrade-report-on-budget-exhaustion.md`
- Epic: `_bmad-output/design-artifacts/ArgusAgent/epics.md` §"Epic 3" → Story 3.2; the floor verdict semantics are Story 3.3, resume is 3.4, host parity is 3.5, numeric `$X` is 7.1.
- Done predecessor (the cost core REUSED): Story 3.1 — `cost/budget_governor.py` (`account_spend` / `_coerce_breach` `>=`-hard-ceiling / `CostLedger.ceiling_reached` exposed FOR this story).
- Reuse targets (verbatim / BY IMPORT — unedited): `ledger/coverage_ledger.py` (`CoverageDepth.SKIPPED` / `grade_entry` / `CoverageLedger.build`), `verdict/verdict_gate.py` (`evaluate_verdict` — UNCHANGED), `index/partitioner.py`, `store/{canonical,envelope,writer,paths,reader}.py`, `pipeline.py` (`run_audit_detailed` / `_detect_per_file` / `_persist` / `PipelineError`).

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, mode=implement) — 2026-06-24.

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **595 passed** in ~15s
  (includes the new `test_budget_exhaustion.py`, `test_halt_report_roundtrip.py`, the extended
  `test_pipeline_signature_demo.py`, the single-serializer AST gate `test_canonical_single_serializer.py`, and
  the no-web-imports gate `test_no_web_imports.py` with the new module under guard).
- `mypy minions_core/apaa/cost/exhaustion.py minions_core/apaa/pipeline.py --ignore-missing-imports` →
  **Success: no issues found in 2 source files.**
- `cost/exhaustion.py` = 294 non-blank lines (≤1200, NFR-M1).

### Completion Notes List

- **AC1 (deterministic halt, no silent overrun)** — PURE `project_halt_point` over the sorted index +
  per-file proxy; halts at the FIRST unit whose cumulative inclusion makes the REUSED 3-1 `_coerce_breach`
  True (`would_breach` delegates BY IMPORT — no fork). At-ceiling boundary breaches (TC-70). No ceiling /
  never-reached → no halt (TC-72/73). Order-independence + byte-stability pinned (TC-74/75). No wall-clock
  interrupt — the halt is a pure function of (sorted index, proxy, ceiling).
- **AC2 (skip + downgrade, never fabricated)** — the un-audited remainder is graded `CoverageDepth.SKIPPED`
  via the EXISTING `grade_entry(claim_present=False)`; the honest-degradation keystone test asserts NO
  `audited_*` entry for an unreached file (TC-77) and that `skipped` lands in `total()` not `deep_count()`,
  driving a lower deep-% through the REAL frozen 1.6 gate (TC-78).
- **AC3 (partial-ledger verdict, degraded, no crash; gate UNCHANGED)** — the partial ledger re-folds through
  the UNCHANGED `evaluate_verdict` (TC-79: a 100%-skipped ledger → INSUFFICIENT_COVERAGE/exit 3, no crash).
  No working-tree change to `verdict_gate.py` (verified — only `pipeline.py` + `test_no_web_imports.py` edited
  among non-new files; `budget_governor.py`/`coverage_ledger.py`/`store/*`/`partitioner.py` untouched).
- **AC4 (frozen no-float secret-safe HaltReport)** — `frozen=True, extra="forbid"`, `HALT_SCHEMA_VERSION`,
  int/bool/str/sorted-tuple only (TC-82/83); no abs-path/source byte (TC-84); non-ASCII café/Cyrillic skipped
  path round-trips intact (TC-85); a non-halted run → halted=False + empty skipped + full assessed (TC-81).
- **AC5 (persist via the EXISTING containment shell)** — `_persist_halt_report` → `write_payload("state", ...)`
  → `EnvelopeWriter.build` → the single 1.1 canonical serializer; content-addressed filename; round-trip
  equal model + byte-identical re-serialize + byte-identical across hosts (TC-90..94). DF-1-7-A note: the
  report uses the SAME `write_payload("state")` path the 3-1 cost snapshot uses; the interim `_persist`
  OSError-edge hardening stays DEFERRED (DF-1-7-A — NOT silently expanded; no new behavior added to it).
- **AC6 (no-halt byte-identity — regression-safe keystone)** — proven e2e (TC-PIPELINE-001-19): a no-ceiling
  (budget=0) run and a ceiling-never-reached (budget=100) run produce byte-identical verdict + findings
  artifacts (content-addressed names AND bytes); the halt report is a purely additive new `state/` artifact.
- **AC7 (pure / frozen / deterministic / typed-error / import-isolated; suite green; mypy clean; ≤1200)** —
  AST purity scan (TC-86) proves no datetime/time/uuid/random/os/open import or call; typed `ExhaustionError`
  on malformed input (TC-87/88); the new module joins `_MODULES_UNDER_GUARD` (FastAPI-free + LLM-free import
  verified). Test area APAA-COST (`TC-APAA-COST-001-70..94`) + APAA-PIPELINE (`-17..19`).
- **Scope fences honored** — NO change to the verdict math/thresholds/exit-code map (3.3); NO resume loop
  (3.4); output is byte-deterministic + order-independent (the full host parity proof is 3.5); NO numeric `$X`
  default (7.1); NO LLM dispatch (Epic 6 — V1 cost is the zero-token proxy). NO new HTTP route / UI.
- **Carry-forwards discharged** — AI-E2-1 (all mandatory test files exist + pass before the `review` flip;
  Dev Agent Record fully filled); AI-E2-5 (extended the import-isolation gate not-forked; single-serializer
  AST gate green; byte-stability + order-independence fixtures applied to the new halted/partial-run surface);
  AI-E1-1 (the honest-degradation never-fabricates-a-pass assertion + secret/abs-path-absent + non-ASCII
  round-trip).
- **No new defer filed.** The V1-cost-is-a-proxy limitation is the cut-order-sanctioned, already-recorded
  limitation (the per-file proxy halts at a meaningful file boundary for the demo); nothing new surfaced.

### File List

- `minions_core/apaa/cost/exhaustion.py` (NEW — PURE halt projection + `HaltReport` + typed `ExhaustionError`)
- `minions_core/apaa/pipeline.py` (UPDATED — scope-fenced halt → skip → downgrade → report wiring + persist)
- `tests/apaa/test_budget_exhaustion.py` (NEW — TC-APAA-COST-001-70..89)
- `tests/apaa/test_halt_report_roundtrip.py` (NEW — TC-APAA-COST-001-90..94)
- `tests/apaa/test_pipeline_signature_demo.py` (UPDATED — TC-APAA-PIPELINE-001-17..19)
- `tests/apaa/test_no_web_imports.py` (UPDATED — `_MODULES_UNDER_GUARD` extended with `cost.exhaustion`)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (UPDATED — 3-2 → review)

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-06-24 | 0.1 | Initial story draft created (create-story) — the FR22 halt → skip → downgrade → report MECHANISM on budget exhaustion: a DETERMINISTIC pre-dispatch halt projection (reusing the 3-1 `_coerce_breach` `>=`-hard-ceiling decision BY IMPORT — no fork; no wall-clock interrupt), the un-audited remainder graded `CoverageDepth.SKIPPED` via the EXISTING `grade_entry` (NEVER a fabricated `audited_*` — the honest-degradation keystone), the PARTIAL ledger re-folded through the UNCHANGED 1.6 `evaluate_verdict` (degraded, never a crash), a frozen `HaltReport` recording what was assessed vs `skipped`-on-exhaustion, and additive persistence to `.apaa/state/` (the 3.4 resume seam). Scope fences: the `INSUFFICIENT_COVERAGE` floor verdict semantics are Story 3.3 (gate UNCHANGED here), resume is 3.4, host byte-parity is 3.5, numeric `$X` is 7.1, real LLM credit metering is Epic 6. Fraction/no-float, single serializer, frozen contracts, byte-deterministic + order-independent halt. Carries AI-E2-1 (pre-`review` test-existence) + AI-E2-5 (L1-E11 loop / gates / byte-stability + order-independence on the new halted-run surface) + AI-E1-1 (honest-degradation never fabricates a pass; secret/abs-path-absent; non-ASCII round-trip). | Scrum Master (Bob) |
## Senior Developer Review (AI)

**Reviewer:** BMAD code-review gate (claude-opus-4-8), iteration 1 — 2026-06-24.
**Outcome:** **PASS** → status `done`. Tests green (595 passed), mypy clean, all 7 ACs met,
all scope fences honored.

### Verdict rationale

A textbook honest-degradation implementation. The keystone invariants were each verified
non-bypassable by reading the actual code paths and the persisted artifacts, not just the
test names:

- **Honest degradation (the keystone, AC2 / FR22 / NFR-R1) — VERIFIED non-bypassable.** The
  un-audited remainder is graded `CoverageDepth.SKIPPED` through the EXISTING
  `grade_entry(proposed_depth=SKIPPED, claim_present=False)` (`pipeline._skipped_remainder_entries`)
  — the same closed-enum path a non-Python/unparseable file already uses. There is **no** code
  path where exhaustion fabricates an `audited_*` grade: the halted branch runs `_detect_per_file`
  ONLY over `assessed_entries` (filtered from `index.entries` by the assessed set) and grades the
  **disjoint** remainder SKIPPED. Disjointness is structural (`project_halt_point` appends each unit
  to exactly one of assessed/skipped) AND asserted at the e2e level (TC-PIPELINE-001-17 reads the
  persisted run-state ledger and asserts `depths[skipped] == "skipped"` and `not in (audited_deep,
  audited_shallow)`). A skipped file lands in `total()` (denominator) and never `deep_count()`
  (numerator), so it drives the deep-% down through the REAL frozen 1.6 gate (TC-78) — no falsely
  complete / RELEASE_READY verdict is reachable on exhaustion.

- **Determinism / purity (AC1 / AC7 / NFR-C2 / NFR-D2 / AR4) — VERIFIED.** `project_halt_point` is a
  pure pre-dispatch projection: it sorts units by path (belt-and-suspenders over the already-sorted
  index), folds the cumulative `int` cost, and halts at the first unit whose inclusion breaches —
  no clock/uuid/random/float (AST scan TC-86 + import-isolation gate, both green). Order-independence
  (TC-74, forward vs reversed) and byte-stability (TC-75) are pinned. The per-file proxy
  (`_unit_cost`: 1 non-Python / 5 Python = 1 files_indexed + 1 python_files + 3 detector_passes)
  is documented to sum to the EXACT 3-1 whole-run total, keeping the no-halt projection consistent
  with the 3-1 ledger.

- **Reuse not fork (AR7 / §3.3) — VERIFIED.** `would_breach` and `project_halt_point` both delegate
  the breach decision to the 3-1 `budget_governor._coerce_breach` BY IMPORT — no parallel comparison.
  TC-70 asserts `would_breach == _coerce_breach` (the imported symbol) across `{0,50,99,100,101,500}`
  including the at-ceiling boundary (`total == ceiling` is a breach). The 1.6 `verdict_gate.py` is
  re-used UNCHANGED (the partial ledger is re-folded through `evaluate_verdict`; floor semantics
  correctly deferred to 3.3) — confirmed no edit to the frozen gate / ledger / serializer / budget_governor
  surfaces (only `pipeline.py` + `test_no_web_imports.py` touched among pre-existing modules).

- **No-halt byte-identity (AC6, the regression keystone) — VERIFIED.** The no-halt branch is
  `_detect_per_file(repo_root, index.entries)` — structurally identical to pre-3.2. The halt report
  is a purely additive new `state/` artifact. TC-PIPELINE-001-19 genuinely pins verdict + findings
  byte-identity (content-addressed names AND bytes) across a no-ceiling (budget=0) and a
  ceiling-never-reached (budget=100) run, and both halt reports flag `halted_on_exhaustion=False`
  with an empty skipped set.

- **Contract / persistence / safety (AC4 / AC5 / NFR-S1 / NFR-S5 / NFR-M2) — VERIFIED.** `HaltReport`
  is `frozen=True, extra="forbid"` with a localized `HALT_SCHEMA_VERSION`, all leaves int/bool/str/
  sorted-tuple, no float (TC-83), no abs-path/source byte (TC-84/94), non-ASCII café/Cyrillic path
  round-trips intact (TC-85). Persistence reuses the EXISTING `write_payload("state", ...)` →
  `EnvelopeWriter.build` → single 1.1 canonical serializer (AST single-serializer gate green),
  content-addressed filename (TC-92), equal-model + byte-identical re-serialize round-trip
  (TC-90/91/93). DF-1-7-A (interim `_persist` OSError edge) is correctly left DEFERRED — the report
  reuses the same `write_payload("state")` path without expanding the OSError-edge scope.

- **Typed error / file size / headless (AC7) — VERIFIED.** `ExhaustionError(ValueError)` on
  float/negative/non-int/non-CostUnit input (TC-87/88); `cost/exhaustion.py` = 294 non-blank lines
  (≤1200); no HTTP route / UI; FastAPI-free import proven via the extended (not forked)
  `_MODULES_UNDER_GUARD`.

### Independent verification

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **595 passed**
  (re-run by the reviewer; includes `test_budget_exhaustion.py`, `test_halt_report_roundtrip.py`,
  the extended `test_pipeline_signature_demo.py`, the single-serializer AST gate, and the
  no-web-imports gate with the new module under guard).
- `mypy minions_core/apaa/cost/exhaustion.py minions_core/apaa/pipeline.py --ignore-missing-imports`
  → **Success: no issues found in 2 source files**.

### Review Findings

No blocking or non-blocking findings. The implementation is clean: scope fences (3.3 floor / 3.4
resume / 3.5 host-parity / 7.1 numeric-$X / Epic-6 LLM) are all honored, no new defer surfaced,
the Dev Agent Record is fully populated, and AI-E2-1 / AI-E2-5 / AI-E1-1 carry-forwards are
discharged.

(Observation, not a finding) `project_halt_point` calls the imported `_coerce_breach` directly
on line 255 rather than the public `would_breach`; both delegate to the single 3-1 authority, so
there is no fork — the cumulative `projected` is derived from already-validated non-negative ints,
so the bypass of `would_breach`'s redundant input validation is harmless.

---

| 2026-06-24 | 1.0 | dev-story (implement) — shipped the FR22 halt → skip → downgrade → report mechanism. NEW pure `cost/exhaustion.py` (`CostUnit`, `HaltProjection`, `project_halt_point`, `would_breach`, frozen `HaltReport`, typed `ExhaustionError`) — the deterministic PRE-DISPATCH per-unit admission projection reusing the 3-1 `_coerce_breach` `>=`-hard-ceiling decision BY IMPORT (no fork, no wall-clock interrupt; at-ceiling boundary breaches). Decisions locked: new `cost/exhaustion.py` sibling (budget_governor frozen); `_coerce_breach` reuse via a public delegating `would_breach`/`project_halt_point` (option b); halt granularity = per-file over the sorted index; per-file cost proxy = 1 non-Python / 5 Python (1 files_indexed + 1 python_files + 3 detector_passes), summing to the EXACT 3-1 whole-run total so a no-halt projection is consistent; typed `ExhaustionError`; test area `APAA-COST`. Scope-fenced `pipeline.py` wiring: project the halt over the index, run `_detect_per_file` over the ASSESSED entries only, grade the remainder `CoverageDepth.SKIPPED` via the EXISTING `grade_entry` (NEVER fabricated audited_*), build the PARTIAL ledger, re-fold through the UNCHANGED 1.6 gate (degraded, never a crash — floor semantics deferred to 3.3), build + persist the `HaltReport` additively to `state/` via `write_payload` (single 1.1 serializer; content-addressed; the 3.4 resume seam). A no-halt run is BYTE-IDENTICAL on verdict/ledger/findings (AC6, e2e-proven). DF-1-7-A stays deferred (the report uses the existing `write_payload("state")` path; the OSError edge is NOT expanded). 595 passed; mypy clean; `cost/exhaustion.py` 294 non-blank lines; import-isolation + single-serializer gates green. AI-E2-1/E2-5/E1-1 discharged. No new defer. | Dev (claude-opus-4-8) |
