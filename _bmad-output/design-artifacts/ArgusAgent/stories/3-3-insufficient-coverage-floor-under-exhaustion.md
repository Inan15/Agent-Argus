# Story 3.3: `INSUFFICIENT_COVERAGE` floor under exhaustion

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As an Engineering Lead gating releases on APAA,
I want a budget-exhausted audit whose assessed deep-% landed below the 20% floor to render an
exhaustion-aware **`INSUFFICIENT_COVERAGE`** verdict — an honest "not assessed" floor that names the
assessed depth (the PRD J2 line `assessed 18% deep; no repo-wide verdict rendered (floor: 20%)`) and
routes to a human (exit `3`) — **never** a falsely-`RELEASE_READY` (exit 0) nor a misleading
`NOT_READY_FOR_RELEASE`/`BLOCKED` (exit 2),
so that when budget exhaustion left APAA without enough coverage to render a release verdict, APAA owns
its OWN limitation (low coverage is APAA's to report) instead of blaming the repo — the THIRD story of
Epic 3, wiring the budget-exhaustion-driven skipping (done 3-2) to the EXISTING FR16 floor decision the
done 1.6 gate already makes.

## Story Context

This is **Story 3 of Epic 3** (Honest Degradation & Cost Governance, Tier-A; epic-3 is already
`in-progress` from Stories 3.1 + 3.2, both `done`). It is the **floor-verdict-semantics-under-exhaustion**
story. It is deliberately **scope-thin** because the verdict MATH for the floor already ships:

- **Story 1.6 (done)** built the PURE `evaluate_verdict` gate whose FIRST decision row (floor-wins
  precedence) returns `Verdict.INSUFFICIENT_COVERAGE` (exit `3`) whenever `total == 0` OR
  `deep_ratio < Fraction(1, 5)` (< 20%) — EVEN WITH blocking findings. The floor LOGIC is already locked,
  pinned, and frozen (`INSUFFICIENT_COVERAGE_FLOOR = Fraction(1, 5)`).
- **Story 2.1 (done)** proved FR8: `inferred` / `skipped` / `tool_scanned_only` / `audited_shallow`
  entries land in the denominator (`total()`) but NEVER the deep-% numerator (`deep_count()`), so a run
  that pushes many files to `skipped` drives the deep-% DOWN through the existing gate naturally.
- **Story 3.2 (done)** built the deterministic HALT → SKIP → DOWNGRADE → REPORT mechanism: when budget is
  exhausted mid-run, the un-audited remainder is graded `CoverageDepth.SKIPPED` via the EXISTING
  `grade_entry`, the PARTIAL ledger is re-folded through the UNCHANGED 1.6 gate, and a frozen `HaltReport`
  (assessed vs `skipped`-on-exhaustion files) is persisted to `.apaa/state/`. **3.2 explicitly fenced the
  floor verdict SEMANTICS to THIS story** (3.2 Story Context: *"3.2 = the mechanism + the record; 3.3 =
  the floor verdict's exhaustion semantics"*).

**So the verdict is ALREADY correct after 3.2** — a budget-exhausted run that pushed the deep-% below 20%
ALREADY returns `INSUFFICIENT_COVERAGE` / exit `3` through the UNCHANGED gate. **What this story adds is
the exhaustion-AWARE floor SEMANTICS / RENDERING** the PRD J2 climax demands and that nothing yet
produces: an honest, machine-readable "assessed X% deep; floor 20%; no repo-wide verdict rendered"
surface that (a) names the assessed deep-% the gate decided on, (b) distinguishes a floor verdict that
was DRIVEN BY exhaustion (budget ran out) from a floor verdict that is INTRINSIC (a small/sparse repo that
was never going to clear 20% even with full budget), and (c) is asserted to route to exit `3` (human
review), never a fabricated `RELEASE_READY` (exit 0) and never a misleading `BLOCKED` (exit 2). This is
the verify-the-floor-holds-under-exhaustion + render-it-honestly story.

**The classification of this story: verify-and-lock the floor decision + an ADDITIVE pure floor-report
surface.** Because the floor verdict MATH already ships (1.6) and the partial-ledger fold already ships
(3.2), the dev MUST resist re-implementing the floor decision. The net-new code is small and additive:
a PURE exhaustion-aware floor report that READS the EXISTING `AuditVerdict` (the 1.6 result) + the
EXISTING `HaltReport` (the 3.2 record) and renders the honest floor surface — plus the e2e tests that
prove the three exhaustion verdict outcomes (below-floor-under-exhaustion → `INSUFFICIENT_COVERAGE`/exit
3; above-floor-under-exhaustion → the gate's normal decision; no-fabricated-`RELEASE_READY`). **Run the
already-shipped scope check in spirit:** the floor decision tokens (`INSUFFICIENT_COVERAGE`,
`evaluate_verdict`, the `Fraction(1, 5)` floor) already exist in production — do NOT fork them; extend the
EXISTING gate result via a read-only, additive report seam.

**What FR16-floor-under-exhaustion IS in V1 — the floor SEMANTICS + an honest render, NOT a math change.**
The architecture (Decision A/C; Error/Degradation Patterns: *"the run still produces a verdict (degraded →
`INSUFFICIENT_COVERAGE`)"*) and the epic (Story 3.3) lock this story to: (a) a halted run whose assessed
deep-% landed below the 20% floor renders `INSUFFICIENT_COVERAGE` with the assessed depth named (e.g.
`assessed 18% deep; floor 20%`), exit `3` — never a default `NOT_READY`; (b) `INSUFFICIENT_COVERAGE` when
consumed by a CI gate routes to human review (exit `3`), DISTINCT from `BLOCKED` (exit `2`). **This story
does NOT change the verdict math, thresholds, exit-code mapping, the 1.6 gate, the 1.2 ledger, the 3.2
halt mechanism, or the 3.1 cost core — all frozen/reused.** It folds the EXISTING `AuditVerdict` +
`HaltReport` into an additive, frozen, no-`float`, secret-safe floor-report surface.

**The Tier-A scope boundary — what is 3.3 vs the rest of Epic 3 + Epic 4.** This story is single-purpose:
the **exhaustion-aware `INSUFFICIENT_COVERAGE` floor SEMANTICS + the honest "assessed X% deep; floor 20%"
render + the exit-3-routing proof**. The behavior built around it is explicitly later/other stories and
MUST NOT be pulled forward:
- **The negative-assurance verdict WRAPPER — `scope_statement` ("examined X, sampled Y, did not cover Z")
  + `materiality_bar` + `disclaimer` + point-in-time stamp (FR17 / NFR-A3) is Story 4.1** (Epic 4,
  `verdict/negative_assurance.py`). THIS story produces the exhaustion-aware floor MESSAGE + the assessed
  deep-% + the assessed-vs-skipped counts the 4.1 scope statement will LATER fold over — it does NOT build
  the negative-assurance wrapper, the materiality bar, the disclaimer, or the point-in-time stamp. Keep
  the floor report a thin, additive, neutral data surface so 4.1 inherits it cleanly. Lock + document this
  fence.
- **Resumability from on-disk `.apaa/` state (FR31) is Story 3.4** — the resume-from-disk
  restore-and-continue loop. 3.2 already persists the `HaltReport` + partial ledger (the 3.4 seam); this
  story PERSISTS the additive floor report alongside (if persisted at all — see Dev Notes "persist vs
  pure-render"); it does NOT build the resume loop.
- **Sequential byte-identical execution on the least-capable host (FR32/NFR-P1) is Story 3.5** — the
  host-independent determinism proof. This story's floor report MUST already be byte-deterministic (no
  clock/uuid/random; no float; sorted content-derived fields) so 3.5 has a determinate surface; the full
  host-vs-host parity proof is 3.5.
- **The numeric `$X` ceiling default + full-repo budget sizing is Story 7.1** (OI3) — NOT here. This story
  exercises the floor against an operator-set (or test-set) ceiling that drives the deep-% below 20%; it
  locks NO numeric default.
- **The 2.3 critical-subsystem clause / 2.4 partitioner / Epic-5 memoization / Epic-6 Prosecutor** are all
  out of scope.

**What already exists (REUSE verbatim, do NOT rebuild).** This story sits on the fully-built Epic-1/2
spine + the done 3-1/3-2 cost + halt core:

- **`minions_core/apaa/verdict/verdict_gate.py` (Story 1.6 + 2.3, done — REUSE verbatim, do NOT edit).**
  The PURE `evaluate_verdict(ledger, findings, *, critical_subsystems_all_deep=True) -> AuditVerdict` fold
  ALREADY returns `Verdict.INSUFFICIENT_COVERAGE` (exit `3`) below the 20% floor (`total == 0` OR
  `deep_ratio < INSUFFICIENT_COVERAGE_FLOOR = Fraction(1, 5)`, floor-wins precedence — evaluated FIRST,
  EVEN WITH blocking findings). The frozen `AuditVerdict` result ALREADY carries `verdict`,
  `deep_ratio: Fraction`, `deep_count`, `total_count`, `counts_by_depth`, `blocking_finding_count`,
  `exit_code`. **This story READS the EXISTING `AuditVerdict` — it does NOT change the gate, the
  thresholds (`Fraction(1, 5)` / `Fraction(3, 5)`), the floor-wins precedence, the exit-code map
  (`0/2/3/1`), or `is_verdict_blocking`.** Verify NO working-tree diff to `verdict_gate.py`.
- **`minions_core/apaa/cost/exhaustion.py` (Story 3.2, done — REUSE verbatim, do NOT edit).** The PURE
  `project_halt_point(...)`, `would_breach(...)`, the frozen `HaltProjection` (`halt_index`,
  `total_credits`, `ceiling_credits`, sorted `assessed_paths` / `skipped_paths`, the
  `halted_on_exhaustion` property), the frozen `HaltReport` (`halted_on_exhaustion`, `total_credits`,
  `ceiling_credits`, `assessed_count` / sorted `assessed_files`, `skipped_on_exhaustion_count` / sorted
  `skipped_on_exhaustion_files`, `HALT_SCHEMA_VERSION`), `build_halt_report(...)`, and the typed
  `ExhaustionError`. **`HaltReport.halted_on_exhaustion` IS the signal** this story reads to decide
  whether a floor verdict was DRIVEN BY exhaustion vs intrinsic. REUSE; do NOT add a field to `HaltReport`
  unless genuinely required (prefer a NEW sibling report model — see Dev Notes).
- **`minions_core/apaa/ledger/coverage_ledger.py` (Story 1.2 + 2.1, done — REUSE verbatim).** The closed
  `CoverageDepth` enum, `CoverageLedger` with `deep_count()` / `total()` / `counts_by_depth()`. The
  assessed deep-% the floor report names is exactly `Fraction(deep_count, total)` over the PARTIAL ledger
  — the SAME ratio the 1.6 gate already computed and stored on `AuditVerdict.deep_ratio`. REUSE the
  stored `AuditVerdict.deep_ratio` — do NOT re-derive the ratio.
- **`minions_core/apaa/ledger/coverage_report.py` (Story 2.2, done — REUSE if it fits).** The PURE
  `DepthAggregate` (frozen, exact-`Fraction` deep-% — `frozen=True, extra="forbid"`),
  `build_coverage_report`, and the `render_text` / `render_json` / `render` pure render functions over the
  ledger. **The "assessed X% deep" rendering should REUSE this 2.2 surface where it fits** (the deep-%
  Fraction + the per-depth counts are already rendered here) rather than fork a parallel render. If the
  floor report needs a render, prefer extending/reusing the 2.2 render pattern (same `Fraction → "x/y"`
  canonical encoding, same no-`float` discipline). Do NOT add a SECOND coverage-render surface.
- **`minions_core/apaa/cost/budget_governor.py` (Story 3.1, done — REUSE BY IMPORT, do NOT edit).** The
  `BudgetConfig` (`ceiling_credits: int | None`), `budget_config_from_budget`, `account_spend`,
  `CostLedger`, `_coerce_breach`. Untouched by this story (the floor report reads downstream of the cost
  fold).
- **`minions_core/apaa/pipeline.py` (Story 1.7 + 2.x + 3.1 + 3.2, done — UPDATE, scope-fenced).** The
  IMPURE orchestrator `run_audit_detailed` ALREADY: projects the halt (`_project_halt`), splits assessed
  vs skipped, grades the remainder `SKIPPED`, builds the PARTIAL ledger, re-folds it through
  `evaluate_verdict` (line ~661), builds the `HaltReport` (line ~644), and persists it
  (`_persist_halt_report`, line ~690). **This story's pipeline touch (if any):** build the additive
  exhaustion-aware floor report from the EXISTING `verdict` + `halt_report` AFTER the verdict fold, and
  persist it additively alongside the halt report (via the EXISTING `ApaaStoreWriter.write_payload("state",
  ...)`) — OR expose it purely on `AuditResult` (lock the choice; see Dev Notes). NO verdict-math change,
  NO new HTTP route, NO change to the halt mechanism, NO resume loop (3.4).
- **`minions_core/apaa/store/{canonical,envelope,writer,paths,reader}.py` (Story 1.1 + 1.3, done —
  REUSE).** The single serializer (`canonical.dumps_bytes`, rejects `float`, `Fraction → "num/den"`),
  `ApaaStoreWriter.write_payload("state", ...)` (content-addressed, containment-checked), `store/reader.py`
  round-trip. Any floor-report persistence goes through this EXISTING shell — no second serializer/writer.
- **`minions_core/apaa/models.py::AuditRequest` + `pipeline.AuditResult` (done — REUSE).** The
  `AuditRequest` (`budget`/`commit`/`materiality_bar`/`repo_path`/`critical_paths`/`excluded_critical_paths`);
  `AuditResult(verdict, locators)`. Any new optional field on `AuditResult` (e.g. an additive floor-report
  locator) is ADDITIVE and default-preserving.

**The net-new deliverable of THIS story.** A scope-thin, ADDITIVE, PURE exhaustion-aware floor-verdict
semantics surface + its e2e proof:
1. a frozen **floor-report model** (`InsufficientCoverageFloorReport` or equivalently-named — lock the
   name) — `frozen=True, extra="forbid"`, localized `schema_version` — that records the honest floor
   surface for a run whose `AuditVerdict.verdict == INSUFFICIENT_COVERAGE`: the assessed `deep_ratio`
   (REUSED from `AuditVerdict.deep_ratio`, exact `Fraction`, NEVER `float`), the `floor` threshold
   (`Fraction(1, 5)` = the EXISTING `INSUFFICIENT_COVERAGE_FLOOR`, REUSED — not re-declared), a
   `below_floor: bool`, a `driven_by_exhaustion: bool` (READ from `HaltReport.halted_on_exhaustion`), the
   assessed-vs-skipped counts (REUSED from the `HaltReport`), and a deterministic human-readable
   `message` (the PRD J2 line `assessed 18% deep; no repo-wide verdict rendered (floor: 20%)` — rendered
   from the `Fraction`, deterministic, no `float`);
2. a PURE **builder** `build_floor_report(verdict: AuditVerdict, halt_report: HaltReport) -> ...` that
   folds the two EXISTING records into the floor report — over in-memory inputs, no I/O, no clock, no LLM
   (AR8). It is a no-op-shaped honest surface for a NON-floor verdict too (a `RELEASE_READY` /
   `NOT_READY_FOR_RELEASE` run yields `below_floor=False` + a message stating the verdict was rendered) —
   so the surface is always populated + honest;
3. the **exit-3 routing proof** — the floor verdict maps to exit `3` (the EXISTING `exit_code_for_verdict`
   / `AuditVerdict.exit_code`, REUSED), DISTINCT from `BLOCKED` (exit `2`) and `RELEASE_READY` (exit `0`)
   — proven by an e2e test that a below-floor-under-exhaustion run returns `INSUFFICIENT_COVERAGE` /
   exit `3`, never a fabricated `RELEASE_READY` / never a misleading `BLOCKED`;
4. (optional, lock the choice) the impure **additive persistence** of the floor report to `.apaa/state/`
   via the EXISTING `ApaaStoreWriter.write_payload("state", ...)` — OR a pure surface on `AuditResult`
   with no new write (the report is derivable from the already-persisted `verdict` + `halt_report`; prefer
   the lighter option unless 4.1/3.4 need it persisted — see Dev Notes);
5. a **non-floor / no-exhaustion run is byte-identical to the 3-2 output** on the
   verdict/ledger/findings/halt-report artifacts — the floor report is purely additive when the verdict is
   not `INSUFFICIENT_COVERAGE` (the regression-safe keystone).

The floor-report model + the builder + any message render are PURE (AR8) and join the import-isolation
gate. The persistence WRITE (if chosen) is the impure pipeline shell.

**Carry-forward from the Epic-1/2 retros + the 3.2 discharge (CLAUDE.md §9.1 / L1-E11).**
- **AI-E2-1 (process 🟠) — the premature-`status=review` flip.** This story does NOT flip `status: review`
  until ALL mandatory test files (`tests/apaa/test_insufficient_coverage_floor.py`, the e2e
  exhaustion-verdict test in `test_pipeline_signature_demo.py`, the import-isolation extension if a new
  module lands, the round-trip if persisted) EXIST and pass; the Dev Agent Record is filled completely
  (no blank placeholders). The orchestrator/dev MUST treat the test-existence precondition as a hard gate
  on the `review` flip.
- **AI-E2-5 (process 🟢) — keep exercising the L1-E11 loop + the three structural gates + the determinism
  surface.** Append any new pure module to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py`
  (extend, NOT fork); keep the single-serializer AST gate (`test_canonical_single_serializer.py`) green
  (any floor-report JSON goes through `store/canonical.dumps`, never a direct `json.dumps`); apply
  byte-stability + order-independence fixtures to the floor-report surface (the message + the assessed/
  skipped fields are deterministic — the full host-vs-host 3.5 fixture is the next story).
- **AI-E1-1 (test-infra 🟠) — adversarial fixtures + honest-degradation must never fabricate a pass.**
  Tests MUST prove: (a) a below-floor-under-exhaustion run is `INSUFFICIENT_COVERAGE` / exit `3` and is
  NEVER `RELEASE_READY` (exit 0 — the lethal fabricated-ready failure) and NEVER `BLOCKED` (exit 2 — the
  misleading-block failure); (b) the floor report carries NO source / secret / absolute-host-path byte
  (only repo-relative paths + `int`/`bool`/`str`/`Fraction`-as-`"x/y"` — the 1.3/2.2/3.2 NFR-S1
  precedent); (c) a non-ASCII (café/Cyrillic) file path in the skipped/assessed set round-trips intact in
  the report; (d) the assessed deep-% + the message are byte-stable + order-independent.
- **AI-E2-3 (governance 🟢) — central defer register.** If this story files a NEW defer, file it
  append-only in `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (the single canonical APAA defer
  source), not only in the story file. Carry-watch DF-1-7-A (interim `_persist` OSError edge → Epic 3): if
  the floor-report persistence touches the same `_persist`/`write_payload` path, record whether
  DF-1-7-A's OSError-edge hardening is in scope or stays deferred — do NOT silently expand scope.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 3.3) + the architecture / PRD. Drivers: **APAA-FR-16**
> (emit `INSUFFICIENT_COVERAGE` below the 20% floor — never a default block; the floor-under-exhaustion
> SEMANTICS — the central driver), **APAA-FR-22** (the halt → skip → downgrade → report honest-degradation
> chain whose floor verdict this story renders), **APAA-NFR-R1** (an exhaustion condition degrades to a
> recorded downgrade — never an uncaught crash or a fabricated result — the honest-degradation keystone),
> **APAA-FR-15** (the verdict is the pure-function gate result this story READS, UNCHANGED),
> **APAA-FR-18 / AR3** (the exit-code wire contract `0/2/3/1` is UNCHANGED — `INSUFFICIENT_COVERAGE → 3`,
> DISTINCT from `BLOCKED → 2` and `RELEASE_READY → 0` — reused, not modified), **APAA-FR-8** (the
> `skipped`/`inferred` remainder lands in the denominator, never the deep-% numerator — honored by the
> UNCHANGED gate), **APAA-NFR-D2** (deterministic, zero-LLM-token — the floor report is a pure fold over
> the EXISTING `AuditVerdict` + `HaltReport`), **APAA-NFR-P1** (byte-identical floor report + message
> across hosts/runs/input-orderings; no float; the full host-vs-host proof is Story 3.5),
> **APAA-NFR-S1** (no source / secret / absolute-host-path bytes in the floor report), **APAA-NFR-S5**
> (any FS write containment-checked via the 1.3 shell), **APAA-NFR-M2** (frozen, additive-only contracts),
> **APAA-NFR-M1** (≤1200-line files), **AR4** (no `float`; the deep-% is an exact `Fraction` reused from
> `AuditVerdict.deep_ratio`; single canonical serializer; no clock/uuid/random/iteration-order —
> content-derived, AR11), **AR8** (pure/impure separation — the floor-report model + builder + message
> render are PURE; the WRITE, if any, is the impure shell), **AR10** (typed failure, never an uncaught
> raise — degrade to the existing `PipelineError` / a localized typed error), **AR11** (`.apaa/` filenames
> content-derived; sorted assessed/skipped sets).
>
> **SCOPE FENCE — Tier-A, single-purpose.** This story delivers ONLY: (1) the exhaustion-aware
> `INSUFFICIENT_COVERAGE` floor SEMANTICS — a frozen, PURE floor-report surface that READS the EXISTING
> 1.6 `AuditVerdict` + the 3.2 `HaltReport` and renders the honest "assessed X% deep; floor 20%; no
> repo-wide verdict rendered" message (the PRD J2 line), naming the assessed deep-% (REUSED from
> `AuditVerdict.deep_ratio`) and distinguishing exhaustion-driven from intrinsic floor verdicts (READ from
> `HaltReport.halted_on_exhaustion`); (2) the exit-`3`-routing PROOF (the floor verdict maps to exit `3`,
> DISTINCT from `2`/`0` — reused mapping); (3) the no-fabricated-`RELEASE_READY` / no-misleading-`BLOCKED`
> assertion under exhaustion; (4) (optional, locked) the additive persistence of the floor report via the
> EXISTING writer. It does NOT build, and MUST NOT pull forward: the **negative-assurance verdict WRAPPER**
> — `scope_statement` / `materiality_bar` / `disclaimer` / point-in-time stamp (FR17/NFR-A3 — **Story
> 4.1**, `verdict/negative_assurance.py`; this story produces the neutral floor-message data the 4.1 scope
> statement folds over, NOT the wrapper); the **resume-from-disk loop** (FR31 — **Story 3.4**); the
> **host-vs-host byte-identical parity proof** (FR32/NFR-P1 — **Story 3.5**; this story's output is
> byte-deterministic + ships an order-independence fixture); the **numeric `$X` ceiling default** (OI3 —
> **Story 7.1**); the **LLM dispatch port** (Epic 6); ANY change to the **1.6 verdict gate / its
> thresholds / floor-wins precedence / exit-code map / 1.2 ledger enum / `grade_entry` / 1.1 serializer /
> 3.1 `budget_governor` / 3.2 halt mechanism (`project_halt_point` / `HaltReport` / `build_halt_report`)**
> contracts (all frozen/reused). It does NOT add a NEW HTTP route / FastAPI surface / UI (§3.7). Render the
> floor honestly, prove exit 3, then stop.

**AC1 — A below-floor-under-exhaustion run renders `INSUFFICIENT_COVERAGE` / exit `3` — never a default `NOT_READY`, never a fabricated `RELEASE_READY` (FR16, FR22, NFR-R1, AR3)**
**Given** an audit with a configured budget ceiling whose deterministic 3.2 halt projection skips enough
units that the PARTIAL ledger's assessed deep-% (`Fraction(deep_count, total)`) falls BELOW the 20% floor
(`< Fraction(1, 5)`)
**When** the pipeline runs the EXISTING `evaluate_verdict` over the partial ledger (UNCHANGED gate, the
floor-wins-first decision row)
**Then** the verdict is `Verdict.INSUFFICIENT_COVERAGE` with `AuditVerdict.exit_code == 3` — the
not-assessed floor (FR16 *"never a default block"*) — and it is NEVER `RELEASE_READY` (exit `0`, the
lethal fabricated-ready failure) and NEVER `NOT_READY_FOR_RELEASE` / `BLOCKED` (exit `2`, the misleading
block) for the below-floor case, EVEN IF blocking findings exist on the assessed subset (floor-wins
precedence — the EXISTING gate behavior, asserted here over an exhaustion-halted partial ledger)
**And** the result is proven by an e2e pipeline test: a budget that halts the run below the 20% floor →
`AuditResult.verdict.verdict == INSUFFICIENT_COVERAGE` and `verdict.exit_code == 3`.

**AC2 — The floor report names the assessed deep-% and distinguishes exhaustion-driven from intrinsic floor (FR16, FR22 — the honest "assessed X% deep; floor 20%" surface)**
**Given** a verdict whose `verdict == INSUFFICIENT_COVERAGE`
**When** the PURE floor-report builder folds the EXISTING `AuditVerdict` + the 3.2 `HaltReport`
**Then** the frozen floor report records: the assessed `deep_ratio` (REUSED from `AuditVerdict.deep_ratio`
— an exact `Fraction`, NEVER `float`), the `floor` threshold (the REUSED `INSUFFICIENT_COVERAGE_FLOOR =
Fraction(1, 5)` — NOT re-declared), `below_floor: bool` (here `True`), `driven_by_exhaustion: bool` (READ
from `HaltReport.halted_on_exhaustion`), the assessed-vs-skipped counts (REUSED from the `HaltReport`),
and a deterministic human-readable `message` rendering the PRD J2 line (e.g.
`"assessed 18% deep; no repo-wide verdict rendered (floor: 20%)"` — the percent rendered DETERMINISTICALLY
from the `Fraction`, no `float`)
**And** a floor verdict DRIVEN BY exhaustion (`HaltReport.halted_on_exhaustion == True`) is distinguished
from an INTRINSIC floor verdict (a small/sparse repo that landed below 20% with NO halt —
`halted_on_exhaustion == False`): `driven_by_exhaustion` reflects exactly that flag, so a downstream
consumer (4.1 scope statement, a CI gate) can tell "ran out of budget" from "never had enough to assess",
verified by two tests (exhaustion-driven vs intrinsic, both `INSUFFICIENT_COVERAGE`, distinct
`driven_by_exhaustion`).

**AC3 — `INSUFFICIENT_COVERAGE` routes to human review (exit `3`), DISTINCT from `BLOCKED` (exit `2`) (FR16, FR18, AR3)**
**Given** the three verdict outcomes
**When** each is mapped to a process exit code via the EXISTING `exit_code_for_verdict` /
`AuditVerdict.exit_code` (the UNCHANGED AR3 wire contract)
**Then** `INSUFFICIENT_COVERAGE → 3` (human review / escalate), `NOT_READY_FOR_RELEASE`/`BLOCKED → 2`
(halt + attach findings), `RELEASE_READY → 0` (proceed) — the three are DISTINCT and a CI gate can route
on them; the floor verdict's `3` is asserted DISTINCT from a blocking run's `2` over comparable ledgers
(a below-floor run vs a 20–60%-deep-with-a-blocking-finding run), so a low-coverage run is NEVER conflated
with a blocking run
**And** the exit-code mapping itself is UNCHANGED (verify no working-tree diff to `verdict_gate.py`); this
story only ASSERTS the routing distinction over exhaustion scenarios.

**AC4 — Above-floor-under-exhaustion behaves as the gate's normal decision — the floor does not over-fire (FR16, FR22, NFR-R1)**
**Given** a budget-exhausted run whose assessed deep-% landed AT OR ABOVE the 20% floor (`>= Fraction(1,
5)`) after skipping the remainder
**When** the verdict is computed over the partial ledger
**Then** the verdict is the gate's NORMAL decision — `RELEASE_READY` (exit `0`) iff `deep_ratio >= 60% AND
0 blocking AND all critical deep`, else `NOT_READY_FOR_RELEASE` (exit `2`) — NOT `INSUFFICIENT_COVERAGE`;
the floor is a 20%-FLOOR, not "any exhaustion → INSUFFICIENT_COVERAGE" (a halted run that still assessed
≥20% deep gets a real release verdict), and the floor report reflects `below_floor=False` +
`driven_by_exhaustion` per the `HaltReport`
**And** this is proven by an e2e test: a halt that leaves the assessed deep-% ≥ 20% does NOT yield
`INSUFFICIENT_COVERAGE` (the floor does not over-fire on the mere fact of exhaustion).

**AC5 — The floor report is frozen, no-`float`, secret-safe; (optional) persists via the EXISTING shell (NFR-M2, AR4, NFR-S1, NFR-S5, AR11, FR25)**
**Given** a built floor report
**When** it is inspected / serialized / (optionally) persisted
**Then** it is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`, localized `schema_version`) with
ALL leaves `int` / `bool` / `str` / `Fraction` (rendered `"x/y"` by the 1.1 serializer) — **NO `float`
anywhere** (the canonical serializer rejects it), NO volatile `run_id`/`created_at` in the hashed payload
(NFR-D3), NO absolute host path / source / secret byte — only repo-relative POSIX paths +
`int`/`bool`/`str` provenance (the 1.3 DN-3 / 2.2 / 3.2 NFR-S1 precedent — never `repo_path`), verified by
an AI-E1-1-style assertion that no source/secret/absolute-host-path byte appears in the report (and a
non-ASCII café/Cyrillic path round-trips intact)
**And** IF the floor report is persisted (lock the choice — DN "persist vs pure-render"), the write goes
through the EXISTING `ApaaStoreWriter.write_payload("state", payload, schema_version=...,
producer="apaa.pipeline.floor_report")` — the bytes are `EnvelopeWriter.build(...)` →
`store/canonical.dumps_bytes` (single serializer, no second `json.dumps` — the AST gate enforces it), the
filename is content-addressed `<content_hash>.json` (never arrival order — AR11), the `ApaaStorePaths`
`is_relative_to` containment check guards the path (NFR-S5), and re-reading via `store/reader.py`
reconstructs an EQUAL model + round-trips byte-identically (NFR-P1); if instead it is a PURE surface on
`AuditResult` (no new write), the report is derivable byte-deterministically from the already-persisted
`verdict` + `halt_report` (document the choice + rationale in the Change Log).

**AC6 — A non-floor / no-exhaustion run is BYTE-IDENTICAL to the 3-2 output on the verdict/ledger/findings/halt-report artifacts (NFR-P1, the regression-safe keystone)**
**Given** a run whose verdict is NOT `INSUFFICIENT_COVERAGE` (a `RELEASE_READY` or `NOT_READY_FOR_RELEASE`
run), with or without a halt
**When** the audit runs end-to-end
**Then** the verdict / coverage-ledger / findings / halt-report artifacts (content-addressed names AND
on-disk bytes) are BYTE-IDENTICAL to the pre-3.3 (3-2) output — the floor report is purely additive (a
`below_floor=False` neutral surface when the verdict is not the floor; if persisted, it is a NEW state/
artifact that does NOT change the existing bytes), proven by an e2e test that compares the
verdict+ledger+findings+halt-report bytes across a pre-3.3-equivalent run and a 3.3 non-floor run.

**AC7 — The new pure logic is PURE, frozen-contract, deterministic, typed-error, import-isolated; the whole suite green; mypy clean; ≤1200 lines (NFR-D2, NFR-P1, AR8, AR10, M1, M2)**
**Given** the new floor-report model + the PURE builder (+ any message-render helper) — in
`cost/exhaustion.py` (additive, the natural home alongside `HaltReport`) OR a new sibling
`verdict/coverage_floor.py` (lock the placement; see DN)
**When** they are imported and exercised in unit tests
**Then** the builder + the report build + the message render perform NO filesystem I/O, NO clock read
(`datetime.now`/`time.time`), NO `uuid4`/`os.getpid()`/`random`, NO LLM/network call, NO dict/`set`-
iteration-order reliance — they are PURE functions over in-memory inputs (the persistence WRITE, if
chosen, is the impure pipeline shell)
**And** the new model is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`, localized
`schema_version` — the 1.1/1.2/1.6/3.1/3.2 precedent); NO `float` anywhere (the deep-% + floor are exact
`Fraction`s REUSED from `AuditVerdict.deep_ratio` / `INSUFFICIENT_COVERAGE_FLOOR`; counts are `int`; flags
are `bool`; paths are `str`); any JSON rendering routes through `store/canonical.dumps` (the single 1.1
serializer — no second `json.dumps`)
**And** a malformed input (a non-`AuditVerdict`, a non-`HaltReport`, an inconsistent verdict/report pair)
raises a typed error (a localized sibling of `ExhaustionError` / `BudgetGovernorError`, or the reused
`ExhaustionError`) — never a silent coerce / bare `except: pass` / `print()` in library code (AR10); any
floor-stage failure in the pipeline degrades to the existing typed `PipelineError` (exit `1`), never an
uncaught traceback
**And** the new module (if a new file) is appended to `_MODULES_UNDER_GUARD` in
`tests/apaa/test_no_web_imports.py` (extend, do NOT fork) and importing it does NOT transitively import
`fastapi`/`uvicorn`/`starlette` or any LLM/api module (assert absence from `sys.modules`)
**And** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` passes (including
the new `tests/apaa/test_insufficient_coverage_floor.py`: AC1 below-floor-under-exhaustion →
`INSUFFICIENT_COVERAGE`/exit 3 [never RELEASE_READY/never BLOCKED]; AC2 the assessed-deep-% message +
exhaustion-driven-vs-intrinsic distinction; AC3 the exit-3-vs-exit-2 routing distinction; AC4
above-floor-under-exhaustion → the gate's normal decision [floor does not over-fire]; AC5 frozen
no-`float` secret-safe report [+ round-trip IF persisted; non-ASCII path round-trip]; AC6 the non-floor
byte-identity; AC7 purity [AST scan] / frozen / no-`float` / typed-error / single serializer /
FastAPI-free import); `mypy` is clean on the new + edited modules; the new source file(s) are ≤1200 lines
(NFR-M1) and cite their `APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in the module docstring. **Test area
`APAA-COST`** (`TC-APAA-COST-001-NN`, continuing the 3-1/3-2 cost area) — lock the area in the docstring.
The 1.6 gate / its thresholds / floor-wins precedence / exit-code map / 1.2 ledger / `grade_entry` / 1.1
serializer / 3.1 `budget_governor` / 3.2 `project_halt_point` / `HaltReport` / `build_halt_report`
contracts are UNCHANGED (verify NO working-tree diff to those frozen surfaces). The mandatory test files
MUST exist + pass BEFORE the story flips to `status: review` (AI-E2-1).

## Tasks / Subtasks

- [x] **Task 0 — Verify the existing reuse surface (verify-and-lock — the floor MATH already ships)** (AC: 1, 2, 3, 4)
  - [x] Re-read `verdict/verdict_gate.py` — confirm `evaluate_verdict` ALREADY returns
        `Verdict.INSUFFICIENT_COVERAGE`/exit 3 below `INSUFFICIENT_COVERAGE_FLOOR = Fraction(1, 5)`
        (floor-wins, evaluated first); confirm `AuditVerdict.deep_ratio` (Fraction) + `.exit_code` +
        `.counts_by_depth`. **Lock:** this story READS this result; it does NOT change the gate (verify no
        working-tree diff at the end).
  - [x] Re-read `cost/exhaustion.py` — confirm `HaltReport.halted_on_exhaustion`, the assessed/skipped
        counts + sorted files, `HALT_SCHEMA_VERSION`, `ExhaustionError`. **`halted_on_exhaustion` IS the
        exhaustion-driven-vs-intrinsic signal.** Confirm the frozen `HaltReport` is sufficient to READ
        (no field add needed); if a field genuinely must be added, prefer a NEW sibling report model over
        editing the frozen `HaltReport`.
  - [x] Re-read `ledger/coverage_report.py` (2.2) — confirm `DepthAggregate` (exact-Fraction deep-%) +
        `render_text`/`render_json`. **Lock the render reuse decision:** reuse the 2.2 deep-% render where
        it fits vs a minimal floor-specific message render (no SECOND coverage-render surface).
  - [x] Re-read `pipeline.py` `run_audit_detailed` — confirm the verdict fold (line ~661) + the
        `build_halt_report` (line ~644) + `_persist_halt_report` (line ~690). Lock the minimal additive
        floor-report touch (build after the verdict + halt report; persist additively OR expose on
        `AuditResult`).
- [x] **Task 1 — The frozen floor-report model + the PURE builder** (AC: 2, 5, 7)
  - [x] Define a frozen `InsufficientCoverageFloorReport` (or locked name) — `frozen=True,
        extra="forbid"`, localized `schema_version`: `verdict: str` (the verdict value), `deep_ratio:
        Fraction` (REUSED from `AuditVerdict.deep_ratio`, NEVER float), `floor: Fraction` (REUSED
        `INSUFFICIENT_COVERAGE_FLOOR`), `below_floor: bool`, `driven_by_exhaustion: bool`,
        `assessed_count: int`, `skipped_on_exhaustion_count: int`, `message: str`. NO float; no
        abs-path/source/secret; no volatile run_id/created_at. Lock placement: `cost/exhaustion.py`
        (additive, recommended) OR `verdict/coverage_floor.py` (new sibling) — document + reuse `Fraction`
        canonical encoding from 1.1.
  - [x] PURE `build_floor_report(verdict: AuditVerdict, halt_report: HaltReport) -> ...` — folds the two
        EXISTING records; `below_floor = (verdict.verdict == INSUFFICIENT_COVERAGE)` (or equivalently
        `deep_ratio < floor`, locked + consistent with the gate); `driven_by_exhaustion =
        halt_report.halted_on_exhaustion`; renders the deterministic `message` from the `Fraction` (no
        float). Always populated + honest for a non-floor verdict too (`below_floor=False`, message states
        the verdict was rendered). Typed error on a malformed/inconsistent input (AR10).
  - [x] Deterministic percent render from the `Fraction` (no `float`): document the exact rendering
        (e.g. `f"{int(ratio * 100)}% deep"` or a fixed-precision render that is integer/Fraction-only —
        lock the exact form so the message is byte-stable; the PRD line uses whole-percent "18%").
- [x] **Task 2 — (Scope-fenced) pipeline floor-report wiring** (AC: 1, 4, 5, 6)
  - [x] In `run_audit_detailed`: AFTER the verdict fold + `build_halt_report`, build the floor report from
        the EXISTING `verdict` + `halt_report`. Lock + implement EITHER (a) persist additively via a
        `_persist_floor_report` → `write_payload("state", ...)` + add the locator to `AuditResult.locators`,
        OR (b) expose it on `AuditResult` as a pure field with no new write. NO verdict-math change, NO new
        enum state, NO resume loop, NO new HTTP route. Non-floor run byte-identical (AC6).
- [x] **Task 3 — Tests** (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] `tests/apaa/test_insufficient_coverage_floor.py` (TC-APAA-COST-001-NN, continuing 3-2) — AC1
        below-floor-under-exhaustion → INSUFFICIENT_COVERAGE/exit 3 [NEVER RELEASE_READY, NEVER BLOCKED,
        even with a blocking finding on the assessed subset]; AC2 the assessed-deep-% message + the
        exhaustion-driven-vs-intrinsic distinction (two runs, both INSUFFICIENT_COVERAGE, distinct
        `driven_by_exhaustion`); AC3 exit-3-vs-exit-2 routing distinction; AC4 above-floor-under-exhaustion
        → the gate's normal decision (floor does not over-fire); AC5 frozen no-float secret-safe report
        [non-ASCII café/Cyrillic path round-trip; no abs-path/source/secret byte]; AC7 purity AST scan /
        frozen / typed-error / order-independence + byte-stability of the message.
  - [x] IF persisted: round-trip test (write_payload→reader: equal model + byte-identical; content-
        addressed filename; no abs-path/source byte) — extend `test_halt_report_roundtrip.py` or add
        `test_floor_report_roundtrip.py`.
  - [x] Extend `tests/apaa/test_pipeline_signature_demo.py` (TC-APAA-PIPELINE-001-NN, continuing 3-2's
        ...17-19) — e2e: a budget-exhausted below-floor run → INSUFFICIENT_COVERAGE/exit 3 + the floor
        report present; an above-floor halt → the gate's normal verdict (no floor over-fire); a non-floor
        run byte-identical on verdict/ledger/findings/halt-report (AC6).
- [x] **Task 4 — Extend the import-isolation gate (if a new module lands)** (AC: 7)
  - [x] IF a new module is created (`verdict/coverage_floor.py`), append it to `_MODULES_UNDER_GUARD` in
        `tests/apaa/test_no_web_imports.py` (extend, not fork). If the code lands additively in the
        already-guarded `cost/exhaustion.py`, no gate change is needed (confirm it stays green).
- [x] **Task 5 — Run + mypy + the AI-E2-1 pre-`review` test-existence precondition** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass.
  - [x] `mypy` clean on the new + edited modules (`python run_mypy_per_file.py` or scoped).
  - [x] **AI-E2-1 GATE:** all mandatory test files exist + pass BEFORE the `review` flip; Dev Agent Record
        filled completely (no blank placeholders). Verify NO working-tree diff to the frozen surfaces
        (`verdict_gate.py`, `coverage_ledger.py`, `cost/exhaustion.py`'s existing contracts, `budget_governor.py`,
        the 1.1 store spine).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **The floor MATH already ships — this is verify-and-lock + an ADDITIVE render (the scope crux).** The
  1.6 `evaluate_verdict` ALREADY returns `INSUFFICIENT_COVERAGE`/exit 3 below the 20% floor (floor-wins,
  evaluated first), and 3.2 ALREADY re-folds the exhaustion-halted partial ledger through it. So a
  below-floor-under-exhaustion run is ALREADY correct. **Do NOT re-implement the floor decision.** The
  net-new is the exhaustion-AWARE SEMANTICS/RENDER: the honest "assessed X% deep; floor 20%; no repo-wide
  verdict rendered" surface that NAMES the assessed deep-% and distinguishes exhaustion-driven from
  intrinsic. Read the EXISTING `AuditVerdict` + `HaltReport`; build an additive frozen report. Resist
  building anything the 1.6/3.2 code already does.
- **Honest degradation owns APAA's limitation, not the repo's (FR16, the keystone framing).** The verdict
  vocabulary's `INSUFFICIENT_COVERAGE` is a *not-assessed* floor — "APAA did not assess enough to render a
  release verdict" — NOT a blocking verdict. The message must read as APAA owning its limitation (the PRD
  J2 line: `assessed 18% deep; no repo-wide verdict rendered (floor: 20%)`), never as "the repo failed".
  This is the difference from `BLOCKED` (exit 2 = "APAA found a blocking issue") and the lethal
  `RELEASE_READY` (exit 0 = "APAA cleared it" — a fabricated pass).
- **Never fabricate a `RELEASE_READY` under exhaustion (the lethal failure, AI-E1-1).** A budget-exhausted
  run that skipped most files must NEVER come back `RELEASE_READY` (exit 0). The 1.6 gate prevents this by
  construction (skipped files are in the denominator, not the deep-% numerator — FR8 — so heavy skipping
  drives the deep-% down, and below 20% is the floor). The mandatory test MUST assert exit 3 (not 0, not
  2) for the below-floor-under-exhaustion case.
- **Distinguish exhaustion-driven from intrinsic INSUFFICIENT_COVERAGE (the FR22↔FR16 join, the net-new
  signal).** A floor verdict can arise two ways: (1) budget RAN OUT mid-run and skipped enough to push the
  deep-% below 20% (`HaltReport.halted_on_exhaustion == True`); or (2) a small/sparse repo that was never
  going to clear 20% even with full budget (`halted_on_exhaustion == False`). Both are
  `INSUFFICIENT_COVERAGE`, but a downstream consumer (the 4.1 scope statement, a CI gate, an operator
  deciding whether to raise the budget and resume via 3.4) needs to tell them apart. The floor report's
  `driven_by_exhaustion` reads EXACTLY `HaltReport.halted_on_exhaustion`. This is the deliberate value-add
  of the floor report over the raw verdict.
- **Reuse the EXISTING `deep_ratio` + floor — do NOT re-derive (AR4 / §3.3).** The assessed deep-% is
  ALREADY computed + stored on `AuditVerdict.deep_ratio` (exact `Fraction(deep, total)`), and the floor is
  ALREADY the module constant `INSUFFICIENT_COVERAGE_FLOOR = Fraction(1, 5)`. The floor report REUSES both
  by import — no parallel ratio computation, no re-declared `0.2`/`Fraction(1, 5)`. The `below_floor`
  predicate is consistent with the gate (`verdict == INSUFFICIENT_COVERAGE`, or equivalently `deep_ratio <
  floor` — lock one and pin that they agree).
- **No floats — ever (AR4/NFR-P1).** The deep-% + the floor are exact `Fraction`s; the percent in the
  message is rendered DETERMINISTICALLY from the `Fraction` to an integer/string (lock the exact form so
  the message bytes are stable — e.g. whole-percent `int(ratio * 100)`; never `float(ratio)`). Counts are
  `int`; flags are `bool`; paths are `str`. The 1.1 serializer rejects `float` as the determinism
  backstop; `Fraction → "num/den"` is frozen by 1.1.
- **Pure/impure separation (master rule, AR8).** The floor-report model + `build_floor_report` + the
  message render are PURE — over in-memory `AuditVerdict` + `HaltReport`; they never open a file, read a
  clock, or call an LLM. The IMPURE shell is the persistence WRITE (if chosen), in the pipeline via
  `write_payload`. ✅ a pure `build_floor_report(verdict, halt_report)` · ❌ a builder that reads
  `time.time()` for a stamp (the point-in-time stamp is 4.1, and it is the envelope's `created_at` even
  then — never inside the pure payload).
- **The negative-assurance WRAPPER is Story 4.1 — do NOT build it (the primary scope fence).** FR17/NFR-A3
  (`scope_statement` "examined X, sampled Y, did not cover Z" + `materiality_bar` + `disclaimer` +
  point-in-time stamp) is `verdict/negative_assurance.py`, Epic-4 Story 4.1. This story produces the
  NEUTRAL floor DATA (assessed deep-%, assessed/skipped counts, the floor message) the 4.1 scope statement
  will fold over — NOT the wrapper, NOT the materiality bar, NOT the disclaimer, NOT the stamp. Keep the
  floor report a thin additive data surface. If tempted to add a `scope_statement`/`disclaimer` field —
  STOP, that is 4.1.
- **Persist vs pure-render (lock the choice + document the rationale).** The floor report is DERIVABLE
  from the already-persisted `AuditVerdict` + `HaltReport`, so persisting it is optional. Two options:
  (a) **persist additively** to `.apaa/state/` via the EXISTING `ApaaStoreWriter.write_payload("state",
  ...)` (content-addressed, a NEW state artifact — gives 3.4/4.1 a ready-made on-disk floor surface, at
  the cost of one more write + a round-trip test); (b) **pure surface on `AuditResult`** (no new write —
  lighter, the report is recomputed from the persisted records when needed). RECOMMENDED: option (b) the
  pure surface UNLESS 4.1/3.4 clearly need it persisted — avoid a speculative artifact (three similar
  lines beat a premature abstraction). Lock + document in the Change Log; whichever is chosen, the surface
  is byte-deterministic for 3.5.
- **Determinism (NFR-P1).** The floor report + the message are a pure deterministic function of the
  `AuditVerdict` + `HaltReport`; the same inputs → byte-identical report + message; the assessed/skipped
  sets are already sorted on the `HaltReport`. Pin a byte-stability + order-independence test (the AI-E2-5
  directive). The full host-vs-host parity proof + the canonical fixture is Story 3.5.
- **Error/degradation → typed, never crash (AR10).** A malformed input (a non-`AuditVerdict`, a
  non-`HaltReport`, a verdict/report pair that disagrees on the deep-%) → a typed error (reuse
  `ExhaustionError` if placed in `cost/exhaustion.py`, or a localized sibling). NO bare `except: pass`, NO
  `print()` in library code, NO silent coerce. A floor-stage failure in the pipeline degrades to the
  existing `PipelineError` (exit `1`).
- **No absolute host paths / secrets in artifacts (NFR-S1).** The floor report carries repo-relative POSIX
  paths (REUSED from the `HaltReport`'s already-sanitized assessed/skipped sets) + `int`/`bool`/`str`/
  `Fraction` provenance only — never `repo_path`, never source/secret bytes (the 1.3 DN-3 / 2.2 / 3.2
  precedent).
- **Headless / import boundary (§3.7, AR7/AR9).** No UI, no HTML/CSS/JS, no FastAPI route. The new pure
  logic takes no token, registers no route, imports only the FastAPI-free 1.6 verdict result + the 3.2
  cost/exhaustion module, and joins `_MODULES_UNDER_GUARD` if it is a new file.

### The exhaustion-aware floor report shape (recommended — dev locks + documents)

A frozen model READ-folded from the EXISTING `AuditVerdict` + `HaltReport` (no new computation of the
deep-% / floor):

| field | source | type |
|---|---|---|
| `schema_version` | localized constant (additive-only) | `str` |
| `verdict` | `AuditVerdict.verdict.value` | `str` |
| `deep_ratio` | `AuditVerdict.deep_ratio` (REUSED) | `Fraction` (never float) |
| `floor` | `verdict_gate.INSUFFICIENT_COVERAGE_FLOOR` (REUSED) | `Fraction` (`1/5`) |
| `below_floor` | `verdict == INSUFFICIENT_COVERAGE` (or `deep_ratio < floor` — lock one, pin they agree) | `bool` |
| `driven_by_exhaustion` | `HaltReport.halted_on_exhaustion` (REUSED) | `bool` |
| `assessed_count` | `HaltReport.assessed_count` (REUSED) | `int` |
| `skipped_on_exhaustion_count` | `HaltReport.skipped_on_exhaustion_count` (REUSED) | `int` |
| `message` | deterministic render from `deep_ratio` + `floor` (no float) | `str` |

The `message` for a below-floor verdict renders the PRD J2 line, e.g.
`"assessed 18% deep; no repo-wide verdict rendered (floor: 20%)"` (whole-percent from the `Fraction`,
deterministic). For a NON-floor verdict the report is still built (`below_floor=False`) with a message
stating the verdict was rendered (e.g. `"assessed 72% deep; verdict rendered: RELEASE_READY"`) — always
populated + honest, never absent. The `driven_by_exhaustion` flag is the FR22↔FR16 join the raw verdict
cannot express.

### Decisions the dev must lock (record in the docstring + Change Log)

- **Module placement** — additive in `cost/exhaustion.py` (recommended — it is 343 lines, additive is
  fine, already import-guarded, sits alongside `HaltReport`) vs a new `verdict/coverage_floor.py` sibling.
  Prefer additive unless `exhaustion.py` approaches the 1200-line limit. Lock + document.
- **Persist vs pure-render** — option (b) pure surface on `AuditResult` (recommended, lighter) vs option
  (a) additive persist via `write_payload`. Lock + document the rationale.
- **`below_floor` predicate** — `verdict == INSUFFICIENT_COVERAGE` (recommended, reads the gate's decision
  directly) vs `deep_ratio < INSUFFICIENT_COVERAGE_FLOOR` (re-derives the comparison). Lock one and PIN
  that they agree over the boundary (the gate's `total == 0` short-circuit is also `INSUFFICIENT_COVERAGE`
  but with a 0/1 ratio — handle it).
- **Message render form** — the exact deterministic `Fraction → percent` rendering (lock so the message is
  byte-stable; the PRD uses whole-percent "18%").
- **Floor-report model name** — `InsufficientCoverageFloorReport` / `CoverageFloorReport` /
  `FloorVerdictReport`. Lock.
- **Typed error** — reuse `ExhaustionError` (if placed in `cost/exhaustion.py`) vs a localized sibling.
  Lock.
- **Test area** — `APAA-COST` (`TC-APAA-COST-001-NN`, continuing 3-1/3-2). Lock.

### Precedent inherited from Stories 1.1–1.7 + 2.1–2.6 + 3.1–3.2 (done) — honor these decisions

- **No second serializer / reuse the 1.1 spine.** Any `.apaa/` bytes go through `store/canonical.dumps_bytes`
  via `EnvelopeWriter.build` + the writer; the AST single-serializer gate enforces it (kept green per
  AI-E2-5). No second `json.dumps`.
- **Reuse the 1.6 `AuditVerdict` + `INSUFFICIENT_COVERAGE_FLOOR` BY IMPORT.** The deep-% + floor are
  already computed/locked — REUSE, no re-derive.
- **Reuse the 3.2 `HaltReport` BY IMPORT.** `halted_on_exhaustion` + the assessed/skipped counts/files are
  the floor report's inputs — REUSE verbatim (do NOT edit the frozen `HaltReport`).
- **Reuse the 2.2 `coverage_report` render pattern** for the deep-% rendering where it fits (no SECOND
  coverage-render surface).
- **Frozen `extra="forbid"` models** (1.1 `Envelope`, 1.2 `Recording`/`CoverageLedger`, 1.6 `AuditVerdict`,
  3.1 `BudgetConfig`/`CostLedger`, 3.2 `HaltReport`): the floor report follows the same pattern with a
  localized `schema_version`.
- **`bool`/`int`/`Fraction`/sorted-`tuple`/`str` over `float`** — every floor signal is non-`float`; the
  1.1 serializer rejects it; `Fraction → "num/den"` frozen.
- **Content-derived filenames, never arrival order (AR11)** — if persisted, the floor report lands at a
  content-addressed `<content_hash>.json` in `state/`.
- **No absolute host paths in artifacts (NFR-S1 spirit, 1.3 DN-3 / 2.2 / 3.2)** — repo-relative paths +
  `int`/`bool`/`str`/`Fraction` provenance only; never `repo_path`.
- **`apaa_version`/`schema_version` single source** — `minions_core/apaa/__init__.py::__version__`
  (`"0.1.0"`); per-module `schema_version` is a localized constant, never env/clock.
- **Import-isolation gate seeded, extend it (AI-E2-5)** — append a NEW module to `_MODULES_UNDER_GUARD`;
  do not fork. (No change if the code lands additively in the already-guarded `cost/exhaustion.py`.)

### Source tree — files to create / update

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/cost/exhaustion.py` | UPDATE (additive, recommended) | add the frozen floor-report model + the PURE `build_floor_report(verdict, halt_report)` + the deterministic message render (REUSING `AuditVerdict.deep_ratio` + `INSUFFICIENT_COVERAGE_FLOOR` + `HaltReport.halted_on_exhaustion`); docstring cites drivers + the floor-under-exhaustion SEMANTICS + the 4.1/3.4/3.5/7.1 fences |
| `minions_core/apaa/verdict/coverage_floor.py` | NEW (alternative to additive) | only if `exhaustion.py` placement is rejected — same floor-report model + builder (PURE); append to `_MODULES_UNDER_GUARD` |
| `minions_core/apaa/pipeline.py` | UPDATE (scope-fenced) | build the floor report from the EXISTING `verdict` + `halt_report`; EITHER persist additively via `_persist_floor_report` + locator, OR expose on `AuditResult` (lock the choice); NO verdict-math change, NO new enum state, NO resume loop, NO new HTTP route; a non-floor run byte-identical to 3-2 |
| `tests/apaa/test_insufficient_coverage_floor.py` | NEW | below-floor-under-exhaustion → INSUFFICIENT_COVERAGE/exit 3 [NEVER RELEASE_READY/BLOCKED] + the assessed-deep-% message + exhaustion-driven-vs-intrinsic distinction + exit-3-vs-exit-2 routing + above-floor-under-exhaustion no-over-fire + frozen no-float secret-safe report (non-ASCII round-trip) + purity/typed-error/order-independence/byte-stability |
| `tests/apaa/test_pipeline_signature_demo.py` | UPDATE | +e2e: budget-exhausted below-floor run → INSUFFICIENT_COVERAGE/exit 3 + floor report present; above-floor halt → gate's normal verdict (no over-fire); non-floor run byte-identical on verdict/ledger/findings/halt-report (AC6) |
| `tests/apaa/test_halt_report_roundtrip.py` (or new `test_floor_report_roundtrip.py`) | UPDATE (only IF persisted) | floor-report write_payload→reader round-trip: equal model + byte-identical; content-addressed filename; no abs-path/source byte |
| `tests/apaa/test_no_web_imports.py` | UPDATE (only IF a new module lands) | extend `_MODULES_UNDER_GUARD` with `minions_core.apaa.verdict.coverage_floor` |

Do NOT modify `verdict/verdict_gate.py`, `ledger/coverage_ledger.py`, `ledger/recording.py`,
`ledger/depth_semantics.py`, `ledger/critical_subsystems.py`, `ledger/coverage_report.py` (REUSE the
render pattern, do not edit), `index/ast_index.py`, `index/partitioner.py`, `store/canonical.py`,
`store/envelope.py`, `store/paths.py`, `store/writer.py`, `store/reader.py`, `cost/budget_governor.py`,
or any detector (frozen/reused contracts — verify no working-tree diff after the story). The EXISTING
`cost/exhaustion.py` `HaltReport` / `HaltProjection` / `project_halt_point` / `build_halt_report`
contracts MUST stay byte-identical (the story only ADDS to the module). `minions_core/cost/budget_guardrails.py`
is REUSED BY IMPORT (transitively) and MUST NOT be edited.

### Scope fences (do NOT pull forward)

- ❌ The **negative-assurance verdict WRAPPER** — `scope_statement` / `materiality_bar` / `disclaimer` /
  point-in-time stamp (FR17/NFR-A3) — **Story 4.1** (`verdict/negative_assurance.py`). This story produces
  the NEUTRAL floor DATA the 4.1 scope statement folds over, NOT the wrapper.
- ❌ The **resume-from-disk restore-and-continue loop** (FR31) — **Story 3.4**. 3.2 already persists the
  halt report + partial ledger (the 3.4 seam); this story does NOT build the resume loop.
- ❌ The **host-vs-host byte-identical parity proof + the canonical fixture** (FR32/NFR-P1) — **Story 3.5**.
  This story's output is byte-deterministic + ships an order-independence/byte-stability fixture; the full
  host parity proof is 3.5.
- ❌ The **numeric `$X` ceiling default / full-repo budget sizing** (OI3) — **Story 7.1**. NO hardcoded
  numeric default here.
- ❌ The **LLM dispatch port / real LLM credit metering** (Epic 6). V1 cost is the deterministic zero-token
  work-unit proxy; the exhaustion/floor MECHANISM is forward-compatible.
- ❌ A **new `CoverageDepth` enum member / a new verdict** — `INSUFFICIENT_COVERAGE` IS the floor verdict
  (the 1.6 closed vocabulary). Reuse the EXISTING `Verdict.INSUFFICIENT_COVERAGE`.
- ❌ ANY change to the **1.6 verdict gate / its thresholds (`Fraction(1, 5)` / `Fraction(3, 5)`) /
  floor-wins precedence / exit-code map / `is_verdict_blocking` / 1.2 ledger enum / `grade_entry` / 1.1
  serializer / 3.1 `budget_governor` / 3.2 `project_halt_point` / `HaltReport` / `build_halt_report`**
  contracts — all frozen/reused.
- ❌ A **new HTTP route / FastAPI surface / UI** (§3.7).

### Deferred-work seam (record if surfaced; do NOT build)

- **DF-1-7-A** — interim `_persist` OSError edge → Epic 3 (open per the 1.7 review). IF the floor-report
  persistence touches the same `_persist`/`write_payload` path, evaluate whether DF-1-7-A's OSError-edge
  hardening is in scope or stays deferred; record the decision (do NOT silently expand scope).
- **The V1-cost-is-a-proxy limitation** — V1 has no real LLM credit metering (the dispatch port is Epic 6),
  so the halt that drives the floor projects over a deterministic zero-token work-unit proxy, not a billed
  total. Cut-order-sanctioned. If a NEW defer surfaces, record it with the CC-3 six-field schema in
  `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`; do NOT build it here.
- **AI-E2-3 (defer-register consolidation)** — the central `deferred-work.md` is the single canonical APAA
  defer source; if this story files a new defer, file it there (append-only), not only in the story file.

## Senior Developer Review (AI)

**Reviewer:** BMAD adversarial code-review gate (claude-opus-4-8), 2026-06-25. **Iteration 1.**
**Verdict: PASS** → status `done`.

### Scope reviewed
Additive edits to `minions_core/apaa/cost/exhaustion.py` (`InsufficientCoverageFloorReport` +
`build_floor_report` + `_whole_percent` + `FLOOR_REPORT_SCHEMA_VERSION`), `pipeline.py`
(`AuditResult.floor_report` additive field + wiring), NEW `tests/apaa/test_insufficient_coverage_floor.py`
(21 tests, `TC-APAA-COST-001-95..115`), edited `test_pipeline_signature_demo.py` (e2e
`TC-APAA-PIPELINE-001-20..22`).

### Independent verification
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **619 passed** in 17.19s
  (re-run by the reviewer, matches the Dev Agent Record).
- `python -m mypy --ignore-missing-imports minions_core/apaa/cost/exhaustion.py minions_core/apaa/pipeline.py`
  → **Success: no issues found**.
- `tests/apaa/test_no_web_imports.py` + `tests/apaa/test_canonical_single_serializer.py` → green;
  `exhaustion.py` is in `_MODULES_UNDER_GUARD` (the new `verdict_gate` import is FastAPI-free).
- `exhaustion.py` = 506 physical lines (≤1200, NFR-M1).

### Adversarial findings (all clear)
- **NO FABRICATED READINESS (keystone) — VERIFIED.** `below_floor = verdict.verdict is
  Verdict.INSUFFICIENT_COVERAGE`. The 1.6 gate guarantees `INSUFFICIENT_COVERAGE ⟺ (total==0 OR
  deep_ratio < 1/5)`, and at `total==0` `deep_ratio = Fraction(0,1) < 1/5`, so `below_floor` agrees with
  both `deep_ratio < floor` AND `verdict==INSUFFICIENT_COVERAGE` across the boundary (pinned by
  TC-APAA-COST-001-111). AC1 + e2e TC-APAA-PIPELINE-001-20 assert exit 3 — never RELEASE_READY (exit 0),
  never BLOCKED (exit 2), even with a blocking finding (TC-96, floor-wins precedence). No code path can
  yield a falsely-RELEASE_READY under exhaustion (skipped lands in the denominator, not the deep-%
  numerator — FR8, the gate construction).
- **VERIFY-AND-LOCK HONESTY — VERIFIED.** No floor math is re-derived: `build_floor_report` READS
  `verdict.deep_ratio` and imports `INSUFFICIENT_COVERAGE_FLOOR` (no parallel `Fraction(1,5)` /
  `deep/total` computation). The 1.6 gate, `budget_governor`, `coverage_ledger`, `store/canonical` carry
  no floor-report logic (only pre-existing benign docstring/§3.3 references). The exhaustion-driven vs
  intrinsic distinction reads `HaltReport.halted_on_exhaustion` exactly (TC-98, distinct
  `driven_by_exhaustion` over two below-floor runs).
- **ADDITIVE / BYTE-IDENTITY — VERIFIED.** `floor_report` is option (b): a pure derived surface on
  `AuditResult` with NO new `write_payload` call. `halt_report` is always built before the floor report,
  so a non-halt run builds it harmlessly. AC6 is pinned by e2e TC-APAA-PIPELINE-001-22 (locator bytes
  byte-identical across runs AND no persisted `state/` payload carries `below_floor`). Whole-percent
  render uses `int(ratio * 100)` exact-Fraction truncation (TC-115 pins truncation, not rounding); no
  `float` anywhere (TC-107 recursive no-float scan + `"9/50"`/`"1/5"` canonical encoding via the single
  1.1 serializer; TC-109 byte-identical round-trip including non-ASCII café/Cyrillic paths).
- **DETERMINISM / PURITY / TYPED ERROR — VERIFIED.** Frozen `extra="forbid"` model with localized
  `FLOOR_REPORT_SCHEMA_VERSION` (TC-106); AST purity scan confirms no datetime/time/uuid/random/os/open
  after the additions (TC-114); typed `ExhaustionError` on non-`AuditVerdict`/non-`HaltReport` args
  (TC-112/113). `to_canonical_payload` re-installs live `Fraction` leaves exactly as the 1.6 `AuditVerdict`
  precedent; `arbitrary_types_allowed=True` mirrors that precedent.
- **AI-E1-1 (no fabricated pass) — VERIFIED.** Adversarial fixtures prove exit-3-not-0/2, secret-safety
  (no `/home/`, `/Users/`, `C:\`, UNC sentinels — TC-108), and non-ASCII round-trip.

### Conclusion
All seven ACs are met; tests are green and were independently re-run; the floor decision is reused, not
forked; the surface is additive and byte-identity-safe; no scope was pulled forward (no negative-assurance
wrapper / resume loop / host-parity proof / numeric default). No findings of any severity. No new defer
filed; DF-1-7-A stays deferred (no `_persist`/`write_payload` touch). Promote to `done`.

## References

- Epic: `_bmad-output/design-artifacts/ArgusAgent/epics.md` §"Epic 3" → Story 3.3 (`INSUFFICIENT_COVERAGE` floor
  under exhaustion — the two ACs: a halted run below the 20% deep floor renders `INSUFFICIENT_COVERAGE`
  with the assessed depth named, exit 3, never a default `NOT_READY`; `INSUFFICIENT_COVERAGE` routes to
  human review (exit 3), distinct from `BLOCKED` (exit 2)); the FR Coverage Map (FR16 floor → Epic 1 gate
  + Story 3.3 floor-under-exhaustion).
- PRD: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` → FR16 (≥60% deep + 0 blocking → RELEASE_READY;
  below 20% → `INSUFFICIENT_COVERAGE`; never a default block); the J2 climax line ("It **stops**, marks
  the remainder `skipped`, and reports `INSUFFICIENT_COVERAGE — assessed 18% deep; no repo-wide verdict
  rendered (floor: 20%)`"); J3 ("`INSUFFICIENT_COVERAGE` routing to human review"); the Verdict vocabulary
  (canonical: `INSUFFICIENT_COVERAGE` = a distinct *not-assessed* state, not a blocking verdict); FR22
  (halt → skip → downgrade → report); NFR-R1 (degrade, never crash or fabricate); FR15/FR18 + the exit-code
  wire contract; FR8 (`skipped`/`inferred` never satisfy a gate); NFR-D2 (zero-token deterministic);
  NFR-P1 (byte-identical); NFR-S1/S5 (no leak / containment); NFR-M1/M2 (file-size / frozen additive). The
  FR17/NFR-A3 negative-assurance wrapper is Story 4.1 — NOT this story.
- Architecture: `_bmad-output/design-artifacts/ArgusAgent/architecture.md` §"Core Architectural Decisions" →
  Decision A/C (the exit-code wire contract `0/2/3/1`; `INSUFFICIENT_COVERAGE` = not-assessed floor);
  §"Implementation Patterns" → Error/Degradation Patterns ("the run still produces a verdict (degraded →
  `INSUFFICIENT_COVERAGE`)"), Determinism Patterns (no float / single serializer / no clock-uuid-random),
  Pure/Impure Separation, Contract/Format Patterns (the verdict vocabulary is closed); AR3/AR4/AR8/AR10/AR11.
- Story 1.6 (done): `_bmad-output/design-artifacts/ArgusAgent/stories/1-6-pure-function-verdict-gate-finding-ordering-exit-code-mapping.md`
  (the floor LOGIC is delivered there; AC8 names THIS story as the reuse seam — "Epic-3 Story 3.3 reuses
  THIS gate VERBATIM over a budget-halted partial ledger").
- Story 3.2 (done): `_bmad-output/design-artifacts/ArgusAgent/stories/3-2-halt-skip-downgrade-report-on-budget-exhaustion.md`
  (the halt → skip → downgrade → report mechanism + the `HaltReport`; fences the floor verdict SEMANTICS
  to THIS story — "3.2 = the mechanism + the record; 3.3 = the floor verdict's exhaustion semantics").
- Code: `minions_core/apaa/verdict/verdict_gate.py` (`evaluate_verdict` / `AuditVerdict.deep_ratio` /
  `.exit_code` / `INSUFFICIENT_COVERAGE_FLOOR = Fraction(1, 5)` / `exit_code_for_verdict` — REUSE,
  UNCHANGED); `minions_core/apaa/cost/exhaustion.py` (`HaltReport.halted_on_exhaustion` + assessed/skipped
  counts/files — REUSE; the additive home for the floor report); `minions_core/apaa/ledger/coverage_report.py`
  (the 2.2 deep-% render pattern — REUSE where it fits); `minions_core/apaa/pipeline.py`
  (`run_audit_detailed` — the verdict fold + `build_halt_report` + `_persist_halt_report` — the additive
  floor-report touch point); `minions_core/apaa/__init__.py` (`__version__ = "0.1.0"`).

## Dev Agent Record

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, mode=implement), 2026-06-25.

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **619 passed** (21 new floor unit tests + 3 new pipeline e2e tests).
- `python -m mypy --ignore-missing-imports minions_core/apaa/cost/exhaustion.py minions_core/apaa/pipeline.py` → clean (no issues).
- `tests/apaa/test_no_web_imports.py::test_all_guarded_modules_clean` + `tests/apaa/test_canonical_single_serializer.py` → green (the new verdict_gate import into exhaustion.py is FastAPI-free — verdict_gate imports only the 1.2 ledger/finding models).
- Frozen-surface diff check: `git diff` UNCHANGED on `verdict/verdict_gate.py`, `ledger/coverage_ledger.py`, `cost/budget_governor.py`, `store/canonical.py`, `store/envelope.py`; the existing `cost/exhaustion.py` `HaltReport`/`HaltProjection`/`project_halt_point`/`build_halt_report`/`would_breach`/`CostUnit`/`ExhaustionError` contracts are byte-identical (the story only ADDS to the module).
- `exhaustion.py` = 437 non-blank lines (≤1200, NFR-M1).

### Completion Notes List

- **Verify-and-lock confirmed.** The floor MATH already ships: the done 1.6 `evaluate_verdict` returns `Verdict.INSUFFICIENT_COVERAGE`/exit 3 below `INSUFFICIENT_COVERAGE_FLOOR = Fraction(1, 5)` (floor-wins precedence, evaluated first, even with blocking findings), and 3-2 already re-folds the exhaustion-halted partial ledger through it. No re-implementation of the floor decision; the net-new is the additive PURE render.
- **AC1** — proven both synthetically (1 deep + 9 skipped = 10% < 20% → INSUFFICIENT_COVERAGE/exit 3, never RELEASE_READY, never BLOCKED; floor-wins even with a blocking finding) and e2e (`TC-APAA-PIPELINE-001-20`: budget=1 skips all → INSUFFICIENT_COVERAGE/exit 3).
- **AC2** — the `InsufficientCoverageFloorReport` REUSES `AuditVerdict.deep_ratio` + `INSUFFICIENT_COVERAGE_FLOOR` (no re-derive), renders the PRD-J2 line `assessed 18% deep; no repo-wide verdict rendered (floor: 20%)`, and `driven_by_exhaustion` reads `HaltReport.halted_on_exhaustion` EXACTLY — two below-floor runs (halted vs intrinsic) both INSUFFICIENT_COVERAGE with distinct `driven_by_exhaustion`.
- **AC3** — `INSUFFICIENT_COVERAGE → 3` asserted DISTINCT from `NOT_READY_FOR_RELEASE → 2` over comparable ledgers (a 10% run vs a 50%-deep-with-blocking-finding run) and `RELEASE_READY → 0`; the exit-code map is the UNCHANGED `AuditVerdict.exit_code`.
- **AC4** — above-floor-under-exhaustion does NOT over-fire: a 30% partial ledger → NOT_READY_FOR_RELEASE (not INSUFFICIENT); exactly-20% is at/above the strict floor; e2e (`TC-APAA-PIPELINE-001-21`: budget=6 admits 1 file → 50% deep → real release verdict, `below_floor=False`).
- **AC5** — frozen `frozen=True, extra="forbid"`, localized `FLOOR_REPORT_SCHEMA_VERSION`; ALL leaves `str`/`int`/`bool`/`Fraction` (`deep_ratio` + `floor` serialize `"9/50"`/`"1/5"` via the single 1.1 serializer); NO float (canonical serializer backstop), NO abs-path/source/secret byte, non-ASCII café/Cyrillic path round-trip via reused HaltReport counts. **Persist vs pure-render decision: option (b) PURE surface on `AuditResult` (no new write)** — the report is derivable from the already-persisted verdict + halt report, so a new artifact would be speculative (YAGNI; "three similar lines beat a premature abstraction"). 4.1/3.4 can recompute it from the persisted records.
- **AC6** — a non-floor / no-exhaustion run is byte-identical to 3-2 on verdict/ledger/findings/halt-report (the floor report adds NO persisted bytes — pinned by asserting no `state/` payload carries the distinctive `below_floor` key).
- **AC7** — PURE (AST scan: no datetime/time/uuid/random/os/open after the additions), typed `ExhaustionError` on a non-`AuditVerdict`/non-`HaltReport` argument, single serializer, FastAPI-free import (no `_MODULES_UNDER_GUARD` change needed — the code lands additively in the already-guarded `cost/exhaustion.py`).
- **Scope fences honored.** No negative-assurance wrapper / `scope_statement` / `materiality_bar` / `disclaimer` / point-in-time stamp (Story 4.1); no resume loop (3.4); no host-parity proof (3.5 — output is byte-deterministic + ships an order-independence/byte-stability fixture); no numeric `$X` default (7.1); no new verdict/enum member; no HTTP route. The 1.6 gate / 1.2 ledger / 1.1 serializer / 3.1 budget_governor / 3.2 halt mechanism are UNCHANGED.
- **DF-1-7-A** stays DEFERRED — the floor report is exposed purely (no new `_persist`/`write_payload` call), so it does not touch the interim OSError edge; scope NOT expanded. No new defer filed.

### Change Log

| Date | Change | Rationale |
|---|---|---|
| 2026-06-25 | Added frozen `InsufficientCoverageFloorReport` + PURE `build_floor_report(verdict, halt_report)` + `_whole_percent` render + `FLOOR_REPORT_SCHEMA_VERSION` to `cost/exhaustion.py` (additive). | The exhaustion-aware FR16 floor SEMANTICS/render — names the assessed deep-%, distinguishes exhaustion-driven from intrinsic floor. Locked: additive placement (exhaustion.py 437 lines, sits beside `HaltReport`); typed error = reused `ExhaustionError`; `below_floor = verdict == INSUFFICIENT_COVERAGE` (pinned to agree with `deep_ratio < floor`); message = whole-percent `int(ratio*100)` exact-Fraction truncation. |
| 2026-06-25 | Wired the floor report onto `AuditResult.floor_report` (additive optional field) in `pipeline.run_audit_detailed`. | **Persist vs pure-render: option (b) pure surface (no new write)** — derivable from persisted verdict + halt report; avoids a speculative artifact (YAGNI). A non-floor run's persisted bytes are byte-identical to 3-2 (AC6). |
| 2026-06-25 | Added `tests/apaa/test_insufficient_coverage_floor.py` (21 tests, `TC-APAA-COST-001-95..115`) + 3 e2e tests in `test_pipeline_signature_demo.py` (`TC-APAA-PIPELINE-001-20..22`). | Proves AC1–AC7: below-floor→INSUFFICIENT/exit3 (never RELEASE_READY/BLOCKED), assessed-%+exhaustion-driven-vs-intrinsic, exit-3-vs-2 routing, above-floor no-over-fire, frozen/no-float/secret-safe/round-trip, non-floor byte-identity, purity/typed-error/byte-stability. |

### File List

- `minions_core/apaa/cost/exhaustion.py` (UPDATE — additive: floor-report model + builder + render + schema constant + verdict_gate import)
- `minions_core/apaa/pipeline.py` (UPDATE — additive: `AuditResult.floor_report` field + `build_floor_report` wiring in `run_audit_detailed`)
- `tests/apaa/test_insufficient_coverage_floor.py` (NEW)
- `tests/apaa/test_pipeline_signature_demo.py` (UPDATE — 3 new e2e tests + `Fraction` import)
- `_bmad-output/design-artifacts/ArgusAgent/stories/3-3-insufficient-coverage-floor-under-exhaustion.md` (status + Dev Agent Record)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (status → review)
