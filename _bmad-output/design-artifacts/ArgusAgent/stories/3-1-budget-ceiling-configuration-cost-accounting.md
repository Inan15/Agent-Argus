# Story 3.1: Budget-ceiling configuration & cost accounting

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
I want to set a budget ceiling for an audit and have APAA account spend against it — with the ceiling
*mechanism* (configuration + deterministic cost accounting) built now, NO hardcoded numeric `$X` default
(OI3 defers the numeric default to the empirical Story 7.1 dogfood sizing), and the baseline cost reported
as a fraction of the audited repo's build cost (NFR-C1, *measured not asserted*) —
so that an audit's cost is bounded and predictable, the spend basis is byte-deterministic across hosts
(no float money), and Story 3.2 has a real accounting surface to halt against
(the FIRST story of Epic 3; epic-3 goes in-progress on this story).

## Story Context

This is **Story 1 of Epic 3** (Honest Degradation & Cost Governance, Tier-A). It opens the cost-governance
cluster (FR21/FR22/NFR-C1/C2). It delivers **FR21** (an operator can set a budget ceiling for an audit) +
the **deterministic cost-accounting MECHANISM** that the rest of Epic 3 folds over, plus the **NFR-C1
baseline-cost reporting** (measured, not asserted). It builds directly on the done Epic-1/2 spine and the
already-reserved `AuditRequest.budget` seam.

**What FR21 IS in V1 — the mechanism, not a number.** The architecture (Decision E / `cost/budget_governor.py`)
and the epic (Story 3.1) call for APAA to "wrap `minions_core.cost.budget_guardrails` **by import** (verified
FastAPI-free — AR7) and account spend against the ceiling (FR21)". This story delivers (a) the **budget-ceiling
configuration surface** — the operator sets a ceiling through the EXISTING `AuditRequest`/CLI seam (the
`budget` field is already reserved and recorded; this story gives it MEANING via a frozen `BudgetPolicy`-shaped
config + an explicit "no numeric default" contract); (b) a **pure, deterministic cost-accounting core** that
folds per-stage/per-file cost contributions into a running total and compares it against the configured ceiling
(reusing the Minions `BudgetGuardrails` hard-ceiling `>=`-is-a-breach semantic BY IMPORT — no fork, §3.3); and
(c) the **NFR-C1 baseline-cost report** that expresses the audit's cost as a *fraction* of the audited repo's
build cost (a `Fraction`/`int` ratio, never a float — *measured and reported*, not asserted in V1).

**The OI3 hard rule this story must honor — NO numeric `$X` default.** Per planning OI3 (epics §"Open delivery
inputs — LOCKED 2026-06-18" + the epics Story 3.1/7.1 ACs): the budget-ceiling `$X` numeric default is
**DEFERRED to empirical Story 7.1 sizing**. This story builds the budget-ceiling *mechanism* (config +
accounting); it must **NOT** lock or ship any hardcoded numeric ceiling default. The absence of a ceiling is a
first-class, explicit state ("no ceiling configured" → accounting still runs and reports, but admits everything
— there is no silent fabricated number). The numeric default is set once the full-repo partition plan exists
(Story 7.1). APAA V1 keeps a **crude in-product cost-governance ceiling** (this mechanism) — NOT the deferred
shared Minions pre-flight estimator layer (Minions Epic 21 / ADR #22); that estimator is a Minions-platform
concern and is explicitly out of APAA V1 scope.

**The Tier-A scope boundary — what is 3.1 vs what is later in Epic 3.** This story is single-purpose: the
**configuration + accounting MECHANISM + the baseline report**. The behavior built ON the mechanism is the
rest of Epic 3 and MUST NOT be pulled forward:
- **Halt → skip → downgrade → report on budget exhaustion (FR22/NFR-C2) is Story 3.2** — the mid-run halt that
  marks the remainder `skipped`, downgrades coverage, and re-folds the partial ledger through the gate. This
  story builds the accounting surface 3.2 *queries* (is the running total at/over the ceiling?) and the typed
  exhaustion signal 3.2 *consumes* — it does NOT itself halt the pipeline mid-run or mark files `skipped`.
- **The `INSUFFICIENT_COVERAGE` floor under exhaustion (FR16 floor) is Story 3.3** — the verdict semantics when
  a halted run assessed below 20% deep. This story touches NO verdict math (the frozen 1.6 gate is unchanged).
- **Resumability from on-disk `.apaa/` state (FR31) is Story 3.4** — persisting/restoring accumulated spend
  across a re-invoke. This story MAY persist the accounting snapshot additively to `.apaa/state/` (the seam
  3.4 reads), but it does NOT build the resume/restore-and-continue logic.
- **Sequential byte-identical execution (FR32/NFR-P1) is Story 3.5** — but this story's accounting MUST already
  be byte-deterministic (no float, content-derived, order-independent) so 3.5 has a determinate surface.
- **The numeric `$X` ceiling default + the full-repo budget sizing is Story 7.1** (OI3) — NOT here.

**What already exists (REUSE verbatim, do NOT rebuild).** This story is a NET-NEW pure cost-accounting core
+ a frozen cost/config contract + an additive config seam — sitting on the fully-built Epic-1/2 spine:

- **`minions_core/cost/budget_guardrails.py` (Minions, verified FastAPI-free — AR7).** `BudgetPolicy`
  (dataclass) + `BudgetGuardrails` with the **D3 hard-ceiling `>=`-is-a-breach** semantic
  (`evaluate(...)` / `evaluate_worker_spend(credits_consumed) -> {within_budget, overage, ...}` where
  `within = credits_consumed < max_worker_credits`, so the exact at-ceiling boundary is a breach) and
  `evaluate_preflight(estimate_total, budget) -> {admitted, action, overage}` (`admitted = estimate_total <
  ceiling`). **REUSE this hard-ceiling comparison BY IMPORT** — APAA's accounting maps its running cost total
  onto the same `>=`-is-a-breach decision; do NOT re-derive a parallel comparison (§3.3, the 21-2
  `evaluate_preflight` precedent). NOTE the Minions `BudgetPolicy` fields are `float` — APAA must NOT let a
  `float` reach any `.apaa/` payload (AR4); the import is used for its DECISION semantic over `int`/`Fraction`
  APAA values, and any APAA-persisted cost figure is `int` credits / a `Fraction` ratio (the canonical
  serializer REJECTS `float`).
- **`minions_core/apaa/models.py::AuditRequest` (Story 1.7 + 2.3, done).** Already carries
  `budget: int = Field(..., ge=0, ...)` ("credits, an `int`, NEVER `float` — AR4; V1 RECORDS the budget for
  provenance but does NOT enforce a ceiling / halt mid-run (the budget governor is Epic 3 — the seam is
  documented)") + `to_provenance_payload()`. **This story is the one that gives `budget` ENFORCEMENT MEANING**
  (it becomes the configured ceiling the accounting compares against) — but it does NOT re-shape the frozen
  model's existing fields. Any new optional config field is ADDITIVE (default preserving byte-identity for a
  pre-3.1 invocation — the 2.3 `critical_paths` precedent). The `budget` field already has `ge=0`; the OI3
  "no numeric default" rule is expressed by treating `budget == 0` (the CLI default) as **"no ceiling
  configured"** (admit-everything accounting), NOT as a zero-credit hard ceiling — lock + document this.
- **`minions_core/apaa/cli.py` (Story 1.7 + 2.3, done).** `--budget` (`type=int`, `default=0`, "recorded, not
  enforced in V1") already wires `AuditRequest.budget`. **This story flips `--budget` from recorded-only to
  the configured ceiling** + documents the "no numeric default; 0 = no ceiling" rule + (if a richer config is
  needed) adds an ADDITIVE flag. NO new sub-command; the CLI stays thin argparse wiring (AR2/NFR-M1).
- **`minions_core/apaa/store/canonical.py` + `envelope.py` (Story 1.1, done).** The single serializer
  (`canonical.dumps_bytes` via `EnvelopeWriter.build`) that REJECTS `float` and encodes `Fraction → "num/den"`,
  `Decimal → plain`. **Any `.apaa/` cost payload routes through this** (the AST single-serializer gate enforces
  it). No second serializer.
- **`minions_core/apaa/store/writer.py` + `paths.py` (Story 1.3, done).** `ApaaStoreWriter.write_payload("state",
  ...)` (content-addressed, containment-checked) for any cost-accounting snapshot persisted to `.apaa/state/`.
  REUSE verbatim — no second writer / path resolver.
- **`minions_core/apaa/pipeline.py` (Story 1.7 + 2.x, done).** `run_audit_detailed` is the IMPURE orchestrator
  (intake → stack → index → detect → ledger → critical → `evaluate_verdict` → partition plan → persist) with
  the typed `PipelineError` (AR10). The V1 pipeline calls **NO LLM** (zero-token, NFR-D2) — so in V1 the only
  real cost contributions are deterministic tool/breadth + per-file work units, NOT LLM credits (the LLM
  dispatch port is Epic 6). **This story's pipeline touch is SCOPE-FENCED:** it MAY construct the budget
  config + the accounting core, fold the V1 (deterministic, zero-token) cost contributions into a running
  total, persist the accounting snapshot + the NFR-C1 baseline report additively to `.apaa/state/`, and expose
  the accumulated total to the verdict-build seam — WITHOUT changing the verdict math, WITHOUT halting the run
  mid-stream (that is 3.2), and WITHOUT splitting the single-pass audit.

**The net-new deliverable of THIS story.** A pure cost-accounting core + a frozen budget-config/accounting
contract + the additive config seam + the impure accounting snapshot persistence + the NFR-C1 baseline report:
1. a frozen **`BudgetConfig`** (or equivalently-named) Pydantic v2 contract (`frozen=True, extra="forbid"`,
   localized `BUDGET_SCHEMA_VERSION`) holding the configured ceiling as `ceiling_credits: int | None`
   (`None` = "no ceiling configured", the OI3 default — NEVER a hardcoded numeric default), with NO `float`;
2. a pure **`account_spend(...)` / `CostAccountant`** core that folds per-contribution `int`-credit costs into
   a running `int` total and, GIVEN the ceiling, computes a deterministic admission/breach decision REUSING the
   Minions `BudgetGuardrails` `>=`-is-a-breach hard-ceiling semantic BY IMPORT (no fork) — pure (no clock /
   uuid / random / float / I/O), order-independent, byte-stable;
3. a frozen **`CostLedger` / `CostReport`** (or equivalent) recording the accumulated total + the per-axis
   breakdown + the ceiling + whether the ceiling was reached — all `int`/`Fraction`/`str`/`bool`, no `float`;
4. the **NFR-C1 baseline-cost report** — the audit's cost expressed as a `Fraction` ratio of the audited repo's
   build-cost proxy (a deterministic, measured `int`-derived ratio — *measured and reported*, not asserted /
   not a float), recorded on the cost report;
5. the impure **accounting-snapshot persistence** through `ApaaStoreWriter.write_payload("state", ...)` so the
   cost ledger + baseline report land deterministically in `.apaa/state/` (the seam Story 3.4 resumes from);
6. the additive **config seam** — `budget == 0` (CLI default) → `ceiling_credits = None` (no ceiling; admit
   everything, accounting still runs); a positive `--budget` → the configured ceiling. No numeric default
   anywhere (OI3).

The `BudgetConfig` + the `CostAccountant`/`account_spend` core + the `CostLedger`/`CostReport` contract are
PURE (AR8) and join the import-isolation gate. The snapshot WRITE is the impure shell.

**Carry-forward from the Epic-1/2 retros (CLAUDE.md §9.1 / L1-E11 — this story discharges these items).**
- **AI-E2-1 (process 🟠) — the premature-`status=review` flip.** Epic 2 surfaced (occurrence 1 for APAA) a
  worker setting `status=review` BEFORE writing the mandatory test suite, under session-limit interruptions.
  This story explicitly: (a) does NOT flip `status: review` until ALL mandatory test files
  (`tests/apaa/test_cost_accounting.py`, the import-isolation extension, the round-trip) EXIST and pass; (b)
  fills the Dev Agent Record completely (no blank placeholder fields — the 2.6 evidence-completeness nit).
  The orchestrator/dev MUST treat the test-existence precondition as a hard gate on the `review` flip.
- **AI-E2-5 (process 🟢) — keep exercising the L1-E11 loop + the three structural gates.** This story cites the
  AI-E2-* items it discharges (here); appends the new pure module(s) to `_MODULES_UNDER_GUARD` in
  `tests/apaa/test_no_web_imports.py` (extend, NOT fork); keeps the single-serializer AST gate
  (`test_canonical_single_serializer.py`) green (any cost JSON goes through `store/canonical.dumps`, never a
  direct `json.dumps`); and applies byte-stability + order-independence fixtures to the new cost-accounting
  determinism surface (the discipline that held byte-stable across all of Epic 2).
- **AI-E1-1 (test-infra 🟠) — adversarial fixtures.** Epic 3 adds no new impure-subprocess surface (cost
  accounting + persistence are FS/in-memory, per the Epic-2 retro §6), so the non-ASCII/subprocess-decode risk
  class is LOWER here than 2.6. Still, the cost report carries no paths/secrets; tests MUST prove no source /
  secret / absolute-host-path byte appears in the persisted cost snapshot (the 1.3/2.3 NFR-S1 precedent — the
  run-state never records `repo_path`), and the accounting determinism is order-independent + byte-stable.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 3.1) and the architecture / PRD. Drivers: **APAA-FR-21** (an
> operator can set a budget ceiling for an audit — the central driver), **APAA-NFR-C1** (a baseline full audit
> costs a bounded fraction of the audited repo's build cost, target ≤10–20%; V1 MEASURES and REPORTS the
> baseline — measured, not asserted), **APAA-NFR-C2** (an audit never exceeds its declared budget ceiling; on
> exhaustion it halts deterministically — *the halt itself is Story 3.2; this story builds the ceiling +
> the deterministic accounting C2 enforces over*), **APAA-NFR-D2** (deterministic, zero-LLM-token — the
> accounting core is a pure fold over `int` cost contributions), **APAA-NFR-P1** (byte-identical accounting
> snapshot + report across hosts/runs for the same repo@commit + config; no float money), **APAA-NFR-S1** (no
> source / secret / absolute-host-path bytes in the persisted cost artifacts), **APAA-NFR-S5** (all FS writes
> containment-checked via the 1.3 shell), **APAA-NFR-M2** (frozen, additive-only contracts), **APAA-NFR-M1**
> (≤1200-line files), **AR3** (the gate exit-code wire contract is UNCHANGED — this story adds no verdict/exit
> semantics), **AR4** (no `float`; `int` credits / `Fraction` ratios / closed forms; single canonical
> serializer; no clock/uuid/random/iteration-order in any `.apaa/`-bound output — content-derived, AR11), **AR7**
> (reuse `minions_core.cost.budget_guardrails` BY IMPORT, verified FastAPI-free — no fork of the hard-ceiling
> semantic, §3.3), **AR8** (pure/impure separation — the config + accounting core + report are PURE; the
> snapshot write is the impure shell), **AR10** (typed failure, never an uncaught raise / silent coerce),
> **AR11** (`.apaa/` filenames content-derived / stable, never arrival order), **OI3** (the budget-ceiling `$X`
> numeric default is DEFERRED to Story 7.1 — NO hardcoded numeric default here; the mechanism only).
>
> **SCOPE FENCE — Tier-A, single-purpose.** This story delivers ONLY: (1) the budget-ceiling CONFIGURATION
> surface (frozen `BudgetConfig` via the additive `AuditRequest`/CLI seam; `budget==0` → `None` no-ceiling;
> NO numeric default — OI3); (2) the pure deterministic COST-ACCOUNTING core (`account_spend`/`CostAccountant`
> folding `int` contributions, reusing the Minions `BudgetGuardrails` `>=` hard-ceiling decision BY IMPORT);
> (3) the frozen `CostLedger`/`CostReport` contract (`int`/`Fraction`/`bool`/`str`, no `float`); (4) the NFR-C1
> baseline-cost report (`Fraction` ratio of audit cost to repo build-cost proxy — measured, reported); (5) the
> impure accounting-snapshot persistence to `.apaa/state/` via the EXISTING `ApaaStoreWriter`. It does NOT
> build, and MUST NOT pull forward: the **mid-run HALT / mark-remainder-`skipped` / downgrade-on-exhaustion**
> behavior (FR22/NFR-C2 — **Story 3.2**); any **verdict-math change / `INSUFFICIENT_COVERAGE` floor semantics**
> (FR16 floor — **Story 3.3**, the frozen 1.6 gate is UNCHANGED); the **resume-from-disk restore-and-continue**
> logic (FR31 — **Story 3.4** — this story MAY persist the snapshot the 3.4 seam reads, NOT the resume loop);
> the **numeric `$X` ceiling default / full-repo budget sizing** (OI3 — **Story 7.1**); the **LLM dispatch port
> / real LLM credit metering** (Epic 6 — V1 cost is the deterministic zero-token work units only); the **shared
> Minions pre-flight estimator layer** (Minions Epic 21 / ADR #22 — explicitly OUT of APAA V1, the "crude
> in-product ceiling" is the V1 choice); any change to the **1.6 verdict gate / 1.2 ledger / 1.1 serializer /
> 1.4 index / 2.x detectors / partitioner** contracts (all frozen/reused). It does NOT add a NEW HTTP route /
> FastAPI surface / UI (§3.7). Configure + account + report, then stop.

**AC1 — An operator can set a budget ceiling through the EXISTING `AuditRequest`/CLI seam — NO numeric default (FR21, OI3, NFR-M2)**
**Given** an operator invoking `apaa audit <repo> --commit <sha> --budget <int> ...` (the existing CLI) — or
constructing an `AuditRequest` directly
**When** the request is built and the budget config is derived
**Then** a positive `--budget N` configures a ceiling of `N` `int` credits; `--budget 0` (the existing CLI
default) / an omitted budget configures **NO ceiling** (`ceiling_credits = None`) — there is **NO hardcoded
numeric ceiling default anywhere** (OI3: the `$X` default is deferred to Story 7.1); the `budget` field's
existing `ge=0` validation is preserved, and a negative budget is rejected by the existing model validation
(a typed `ValidationError`, never a silent coerce — AR10)
**And** the budget config is a frozen Pydantic v2 contract (`frozen=True, extra="forbid"`, localized
`BUDGET_SCHEMA_VERSION`) carrying `ceiling_credits: int | None` (NEVER `float` — AR4) — and the
no-ceiling state (`None`) is a FIRST-CLASS, explicit value (an audit with no ceiling is a legitimate V1 audit:
accounting still runs and reports, it simply admits everything), NOT a fabricated zero or a magic sentinel int
**And** the config is derived ADDITIVELY from the existing reserved `AuditRequest.budget` field — a pre-3.1
invocation (no budget / `--budget 0`) yields `ceiling_credits = None` and is byte-identical to the pre-3.1
persisted run-state EXCEPT for the new additive cost-accounting snapshot artifact (the verdict/ledger/findings
payloads are unchanged); the OI3 "mechanism, not a number" rule + the "0 = no ceiling, not a zero ceiling"
decision are documented in the module docstring + the Change Log.

**AC2 — Deterministic cost accounting folds `int` contributions into a running total, reusing the Minions hard-ceiling decision BY IMPORT (FR21, AR7, NFR-D2, NFR-P1)**
**Given** a set of per-stage / per-file cost contributions (V1: the deterministic, zero-token work units the
pipeline performs — e.g. files indexed, tool/breadth invocations, detector passes — each an `int`-credit
contribution; V1 has NO LLM credits, the LLM port is Epic 6)
**When** the pure `cost/budget_governor.py::account_spend(contributions, *, config)` (or a `CostAccountant`
fold) runs
**Then** it folds the contributions into a running `int` total (`Fraction` if a fractional credit is ever
needed — NEVER `float`, AR4), and — when a ceiling is configured (`ceiling_credits is not None`) — computes a
deterministic breach/admission decision by REUSING `minions_core.cost.budget_guardrails.BudgetGuardrails` BY
IMPORT (the D3 `>=`-is-a-breach hard-ceiling semantic — `total >= ceiling` is a breach, mapping APAA's `int`
total onto the SAME comparison `evaluate_worker_spend` / `evaluate_preflight` encode; the exact at-ceiling
boundary is a breach), with **no fork / no parallel re-derived comparison** (§3.3, the 21-2 precedent)
**And** when no ceiling is configured (`ceiling_credits is None`) the accounting still produces the running
total + the report but the breach decision is "no ceiling — admitted" (admit everything; the total is still
recorded for the NFR-C1 baseline)
**And** the accounting core is PURE (AR8) — it takes the contributions + the config as in-memory ARGUMENTS, it
performs NO filesystem I/O, NO clock read, NO `uuid4`/`os.getpid()`/`random`, NO LLM/network call, NO
dict/`set`-iteration-order reliance — so the same contributions + config yield a BYTE-IDENTICAL total + decision
across hosts/runs and across two input orderings of the same contributions (NFR-P1 — proven by an
order-independence + byte-stability test); the `float`-rejecting canonical serializer is the determinism
backstop for any persisted figure.

**AC3 — The cost ledger / report is a frozen, no-`float` contract; the ceiling-reached flag is exposed for Story 3.2 (FR21, NFR-M2, AR4, NFR-C2 seam)**
**Given** a completed accounting fold
**When** the `CostLedger` / `CostReport` model is built
**Then** it is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`, localized `COST_SCHEMA_VERSION`)
carrying: the accumulated `total_credits: int`, the configured `ceiling_credits: int | None`, a deterministic
`ceiling_reached: bool` (False when no ceiling), and a per-axis breakdown (e.g. `int` counts of files indexed /
tool invocations / detector passes — the V1 deterministic work units) — ALL `int`/`Fraction`/`bool`/`str`,
**NO `float` anywhere** (the canonical serializer rejects it), and NO volatile `run_id`/`created_at` in the
hashed payload (NFR-D3)
**And** the `ceiling_reached` flag (and the running total) is the EXPLICIT, typed surface **Story 3.2** queries
to decide the mid-run halt — this story EXPOSES it but does NOT act on it (no halt, no `skipped` marking here);
the report documents that the halt/downgrade behavior is Story 3.2's
**And** when no ceiling is configured, `ceiling_reached` is deterministically `False` and the report is still
fully populated (the total + breakdown + baseline are recorded regardless of whether a ceiling exists — the
mechanism is decoupled from the presence of a number, per OI3).

**AC4 — The NFR-C1 baseline-cost report expresses audit cost as a measured `Fraction` of the repo build-cost proxy — measured, not asserted, not float (NFR-C1, AR4)**
**Given** a completed audit with its accumulated `total_credits` + a deterministic proxy for the audited repo's
build cost (V1: a content-derived, deterministic proxy — e.g. total LOC / total file count / total indexed
units — computed from the already-built index + the LOC map the partitioner already produces; lock the exact
proxy + document it)
**When** the NFR-C1 baseline is reported
**Then** the audit's cost-as-a-fraction-of-build-cost is expressed as an exact `Fraction` (`audit_cost /
build_cost_proxy`, reduced — NEVER a `float`; the 2.1/2.2/2.5 `Fraction`-not-float precedent) recorded on the
cost report; the report MEASURES and REPORTS the baseline (V1 does NOT assert / gate on the ≤10–20% target —
NFR-C1 is "V1 measures and reports", per the epic Story 3.1 second AC) and documents that the target is a
post-V1 measurement goal, not a V1 pass/fail
**And** the build-cost proxy is deterministic + content-derived (no clock / no float), so the baseline ratio is
byte-identical for the same repo@commit + config (NFR-P1); a degenerate `build_cost_proxy == 0` (empty repo) is
handled with a typed, total-safe rule (no divide-by-zero — mirror the 1.6 `total == 0` floor-first guard:
report a defined "baseline undefined / 0 build cost" marker, never a crash or a `float('inf')`).

**AC5 — The accounting snapshot + baseline report persist to `.apaa/state/` via the EXISTING containment shell — secret-safe, content-addressed (NFR-S5, NFR-S1, AR4, AR11, FR25)**
**Given** a completed accounting fold + report
**When** the cost snapshot is persisted
**Then** the write goes through the EXISTING `ApaaStoreWriter.write_payload("state", payload,
schema_version=..., producer="apaa.pipeline.cost_ledger")` (or equivalent) — the bytes are
`EnvelopeWriter.build(...)` → `store/canonical.dumps_bytes` (single serializer, no second `json.dumps` — the
AST gate enforces it), the filename is content-addressed `<content_hash>.json` (never arrival order — AR11),
and the `ApaaStorePaths` `is_relative_to` containment check guards the path (NFR-S5) — REUSING the 1.1/1.3
spine with NO second writer / path resolver / serializer
**And** the persisted cost payload carries ONLY `int`/`Fraction`/`bool`/`str` provenance (the total, ceiling,
ceiling_reached, the per-axis breakdown, the baseline `Fraction`, the schema_version) — NEVER an absolute host
path, NEVER source/secret bytes, NEVER `repo_path` (the 1.3 DN-3 / 2.3 / `to_provenance_payload()` precedent —
NFR-S1); re-reading via `store/reader.py` reconstructs an equal model + round-trips byte-identically (NFR-P1),
verified by a round-trip test (mirrors `test_store_roundtrip` / `test_assignments_roundtrip`)
**And** the snapshot is the seam **Story 3.4** (resumability) reads to restore accumulated spend across a
re-invoke — this story PERSISTS it; it does NOT build the restore-and-continue resume loop (3.4); if the dev
defers the snapshot persistence half, it MUST document the deferral and still deliver the in-memory accounting
core + report (the FR21 mechanism is the in-scope deliverable).

**AC6 — The new pure modules are PURE, frozen-contract, deterministic, typed-error, and import-isolated (NFR-D2, NFR-P1, AR8, AR10, AR7, M2)**
**Given** `cost/budget_governor.py` (and any frozen model it defines)
**When** it is imported and exercised in unit tests
**Then** the `account_spend`/`CostAccountant` fold + the `BudgetConfig`/`CostLedger`/`CostReport` build + the
baseline-ratio computation perform NO filesystem I/O, NO clock read (`datetime.now`/`time.time`), NO
`uuid4`/`os.getpid()`/`random`, NO LLM/network call, NO dict/`set`-iteration-order reliance — they are PURE
functions over in-memory inputs (the snapshot WRITE is the impure shell, in the pipeline)
**And** the import of `minions_core.cost.budget_guardrails` is verified FastAPI-free at import time (AR7) — it
does NOT transitively pull `fastapi`/`uvicorn`/`starlette` (the architecture's verified-FastAPI-free reuse
target); any model `cost/budget_governor.py` defines is a frozen Pydantic v2 model (`frozen=True,
extra="forbid"` — the 1.1/1.2/1.4/1.6/2.x precedent) with a localized `schema_version` (additive-only, NFR-M2);
NO `float` anywhere (credits + counts are `int`; ratios are `Fraction`; flags are `bool`; ids + reasons are
`str` — AR4); any JSON rendering routes through `store/canonical.dumps` (the single 1.1 serializer — no second
`json.dumps`)
**And** a malformed input (a `float` contribution, a negative ceiling, a non-`int` credit, a non-mapping
contributions arg) raises a typed error — a `ValueError` subclass localized to the module (mirroring
`RepoIntakeError` / `DepthSemanticsError` / `PartitionerError` — call it `BudgetGovernorError` /
`CostAccountingError`) — never a silent coerce / bare `except: pass` / `print()` in library code (AR10); any
cost-accounting failure in the pipeline degrades to the existing typed `PipelineError` (exit `1`), never an
uncaught traceback
**And** `minions_core.apaa.cost.budget_governor` is appended to `_MODULES_UNDER_GUARD` in
`tests/apaa/test_no_web_imports.py` (extend, do NOT fork) and importing it does NOT transitively import
`fastapi`/`uvicorn`/`starlette` or any LLM/api module (assert absence from `sys.modules`).

**AC7 — The whole APAA suite green; tests cover config + accounting + the no-ceiling default + the baseline + persistence; mypy clean; ≤1200 lines (NFR-M1)**
**Given** the modules + tests added/edited by this story
**When** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` runs
**Then** all pass, including new tests in `tests/apaa/test_cost_accounting.py`: AC1 config derivation
(positive `--budget` → ceiling; `--budget 0` / omitted → `ceiling_credits is None` no-ceiling; **NO hardcoded
numeric default** — a test asserts no magic default int leaks; negative budget rejected by the existing
`ge=0`); AC2 the accounting fold (running `int` total; order-independence + byte-stability of the total +
decision; the `>=`-is-a-breach decision REUSED from `BudgetGuardrails` — including the exact at-ceiling
boundary is a breach, mirroring `TC-COST-001-46`; no-ceiling → admit-everything); AC3 the frozen
`CostLedger`/`CostReport` (no-`float`; `ceiling_reached` exposed True at/over ceiling, False below + False when
no ceiling); AC4 the NFR-C1 baseline `Fraction` (measured + reported; deterministic; the `build_cost_proxy ==
0` total-safe guard, no divide-by-zero); AC6 purity (AST scan) / frozen / no-`float` / typed-error / single
serializer / FastAPI-free import; the **AI-E1-1-style** assertion that no source / secret / absolute-host-path
byte appears in the persisted cost snapshot
**And** a `tests/apaa/test_cost_snapshot_roundtrip.py` (or extend `test_store_roundtrip.py`) proves the cost
snapshot written via `ApaaStoreWriter.write_payload("state", ...)` → read via `store/reader.py` → equal model
+ byte-identical re-serialize (NFR-P1), with a content-addressed filename and NO absolute path / source byte in
the payload
**And** `cost/budget_governor.py` is appended to `_MODULES_UNDER_GUARD` and the import-isolation gate stays
green; the 1.1 single-serializer AST gate still passes with the new module present (no direct `json.dumps(`);
the new source file(s) are ≤1200 lines (NFR-M1) and cite their `APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in the
module docstring; `mypy` is clean on the new + edited modules. The 1.6 gate / 1.2 ledger / 1.1 serializer / 1.4
index / 2.x detector / partitioner contracts are UNCHANGED (this story adds the cost module + the config seam +
tests + the additive snapshot persistence; if it touches `pipeline.py`/`models.py`/`cli.py` it is ONLY to
construct the config, fold the V1 deterministic contributions, persist the snapshot additively, and flip
`--budget`/`budget` from recorded-only to the configured ceiling — NOT to change the verdict math, halt the run
mid-stream, or split the single-pass audit). The mandatory test files MUST exist + pass BEFORE the story flips
to `status: review` (AI-E2-1).

## Tasks / Subtasks

- [x] **Task 0 — Verify the existing reuse surface (verify-and-lock)** (AC: 1, 2, 5)
  - [x] Re-read `minions_core/cost/budget_guardrails.py`: confirm `BudgetGuardrails.evaluate_worker_spend` /
        `evaluate_preflight` encode the D3 `>=`-is-a-breach hard-ceiling semantic (`within = consumed < max`;
        `admitted = estimate_total < ceiling`); confirm it is FastAPI-free (dataclass/stdlib). Lock the EXACT
        reuse point (which method / which decision APAA maps onto). Do NOT fork the comparison.
  - [x] Re-read `models.py::AuditRequest`: confirm `budget: int = Field(..., ge=0, ...)` + the "recorded, not
        enforced in V1 (Epic 3)" docstring + `to_provenance_payload()`. This story gives `budget` enforcement
        meaning; the additive config field (if any) defaults to preserve byte-identity. Lock "0 = no ceiling".
  - [x] Re-read `cli.py`: confirm `--budget type=int default=0` "recorded, not enforced in V1". This story
        flips it to the configured ceiling + documents the no-numeric-default rule. Decide whether a richer
        config flag is needed (prefer reusing `--budget` only — minimal seam).
  - [x] Re-read `pipeline.py`: confirm `run_audit_detailed`, the typed `PipelineError`, the per-file detect
        loop, the LOC map (`compute_loc_by_file` / `_build_partition_plan`) the baseline proxy can reuse, and
        the `_persist` / `write_payload("state", ...)` seam. Decide the minimal scope-fenced accounting +
        persistence touch (NO halt, NO verdict-math change).
  - [x] Re-read `store/canonical.py` (Fraction → "num/den", float rejected) + `store/writer.py`
        (`write_payload`) + `store/reader.py` round-trip. REUSE verbatim.
- [x] **Task 1 — `cost/budget_governor.py`: pure config + accounting core + cost report** (AC: 1, 2, 3, 4, 6)
  - [x] Create `minions_core/apaa/cost/budget_governor.py` (+ `cost/__init__.py` if the sub-package is new;
        docstring cites the drivers + AR7 reuse + the OI3 no-numeric-default rule + the "0 = no ceiling, not a
        zero ceiling" decision + the Story 3.2/3.3/3.4/7.1 scope fences).
  - [x] Frozen `BudgetConfig` (`frozen=True, extra="forbid"`, `BUDGET_SCHEMA_VERSION`): `ceiling_credits: int |
        None` (None = no ceiling, OI3 — NO numeric default). A pure `budget_config_from_request(request) ->
        BudgetConfig` mapping `request.budget == 0 → None`, `> 0 → ceiling`.
  - [x] Pure `account_spend(contributions, *, config) -> CostLedger` (or a `CostAccountant` fold): running
        `int` total over the contributions; when `ceiling_credits is not None`, the `>=`-is-a-breach decision
        REUSED from `BudgetGuardrails` BY IMPORT (no fork); when None, admit-everything. Order-independent +
        byte-stable (pinned by tests).
  - [x] Frozen `CostLedger` / `CostReport` (`frozen=True, extra="forbid"`, `COST_SCHEMA_VERSION`):
        `total_credits: int`, `ceiling_credits: int | None`, `ceiling_reached: bool`, the per-axis `int`
        breakdown, and the NFR-C1 baseline `Fraction` (`audit_cost / build_cost_proxy`, total-safe on proxy
        0). NO `float`; no I/O/clock/LLM (pinned by the AST/purity test).
  - [x] Pure NFR-C1 baseline computation (deterministic content-derived `build_cost_proxy` — lock + document
        the proxy, e.g. total LOC from the existing LOC map; `Fraction` ratio; total-safe `proxy == 0` guard).
  - [x] `BudgetGovernorError` / `CostAccountingError` (`ValueError` subclass) on malformed input (a `float`
        contribution / negative ceiling / non-`int` credit) — typed, AR10.
- [x] **Task 2 — Config seam: `AuditRequest`/`cli.py` (additive; flip `--budget` to the configured ceiling)** (AC: 1)
  - [x] If a richer config field is needed, add it ADDITIVELY to `AuditRequest` (default preserving
        byte-identity — the 2.3 precedent); otherwise reuse the existing `budget` field. Document "0 = no
        ceiling; NO numeric default (OI3)".
  - [x] In `cli.py`: update the `--budget` help to "the configured audit ceiling in credits; omitted / 0 = no
        ceiling (OI3 — no numeric default; the dogfood ceiling is sized in Story 7.1)". NO new sub-command; thin
        wiring only (AR2/NFR-M1).
- [x] **Task 3 — (Scope-fenced) pipeline accounting + snapshot persistence** (AC: 2, 4, 5)
  - [x] In `run_audit_detailed` (or a thin sibling): build the `BudgetConfig` from the request, collect the V1
        deterministic (zero-token) cost contributions (files indexed / tool/breadth invocations / detector
        passes — the work units the pipeline already performs), fold them via `account_spend`, compute the
        NFR-C1 baseline (reuse the existing LOC map for the build-cost proxy), and persist the `CostLedger`/
        `CostReport` snapshot additively to `.apaa/state/` via `write_payload("state", ...)`. DO NOT halt the
        run mid-stream (Story 3.2), DO NOT change the verdict math (the frozen 1.6 gate is unchanged), DO NOT
        split the single-pass audit. A no-ceiling run persists the snapshot + report and is otherwise
        byte-identical to today's verdict/ledger/findings payloads. Keep the typed `PipelineError` wrapping
        (AR10) intact. Add the cost locators to `AuditResult.locators`.
- [x] **Task 4 — Tests** (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] `tests/apaa/test_cost_accounting.py` — AC1 config (positive ceiling; `0`/omitted → None no-ceiling; NO
        magic default int; negative rejected by `ge=0`); AC2 fold (running int total; order-independence +
        byte-stability; the `>=` hard-ceiling decision REUSED from `BudgetGuardrails` incl. the exact
        at-ceiling-is-a-breach boundary; no-ceiling admit-everything); AC3 frozen report (no-`float`;
        `ceiling_reached` True at/over, False below + False no-ceiling); AC4 NFR-C1 baseline `Fraction`
        (measured + reported; deterministic; `build_cost_proxy == 0` total-safe, no divide-by-zero); AC6
        purity (AST scan) / frozen / no-`float` / typed-error / single serializer / FastAPI-free import;
        the secret/abs-path/source-byte-absent assertion on the snapshot. **Test area `APAA-COST`**
        (`TC-APAA-COST-001-NN` — a NEW area for the cost module, continuing the per-module-area convention
        `APAA-INTAKE`/`INDEX`/`LEDGER`/`SECRET`/`TOOL`/`VERDICT`/`PIPELINE`/`STORE`/`CLI`/`DETECT`); zero LLM
        tokens for the pure tests. Lock the area choice in the docstring.
  - [x] `tests/apaa/test_cost_snapshot_roundtrip.py` (or extend `test_store_roundtrip.py`) — `write_payload`
        → `store/reader.py` round-trip: equal model + byte-identical re-serialize; content-addressed filename;
        no absolute path / source byte in payload.
  - [x] Extend the pipeline e2e test only if Task 3 persists in the run — prove a budget-configured run persists
        the cost snapshot and a no-ceiling run is byte-identical to today on the verdict/ledger/findings
        artifacts (the regression-safe path).
- [x] **Task 5 — Extend the import-isolation gate** (AC: 6, 7)
  - [x] Append `minions_core.apaa.cost.budget_governor` to `_MODULES_UNDER_GUARD` (extend, do NOT fork). Assert
        the `budget_guardrails` reuse stays FastAPI-free.
- [x] **Task 6 — Run + mypy + the AI-E2-1 pre-`review` test-existence precondition** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass (the 1.1
        single-serializer AST gate + the extended no-web-imports gate re-run green with the new module present).
  - [x] `mypy` clean on the new + edited modules (`cost/budget_governor.py`, + `pipeline.py`/`models.py`/
        `cli.py` if touched).
  - [x] **AI-E2-1 GATE:** confirm ALL mandatory test files exist + pass BEFORE flipping `status: review`; fill
        the Dev Agent Record completely (no blank placeholder fields).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **The mechanism, NOT a number (OI3 — the design crux).** Build the budget-ceiling CONFIGURATION + the
  deterministic COST ACCOUNTING. Ship **NO hardcoded numeric `$X` ceiling default** — the numeric default is
  deferred to the empirical Story 7.1 dogfood sizing (epics §"Open delivery inputs — LOCKED 2026-06-18" / OI3).
  The no-ceiling state is FIRST-CLASS: `ceiling_credits = None` (admit everything, accounting still runs +
  reports). Express it via `request.budget == 0 → None`, NOT a magic default int. A test must assert no numeric
  default leaks. APAA V1 keeps a **crude in-product ceiling** (this mechanism) — NOT the deferred shared Minions
  pre-flight estimator layer (Minions Epic 21 / ADR #22), which is out of APAA V1 scope.
- **Reuse `budget_guardrails` BY IMPORT, never fork (AR7 / §3.3).** The hard-ceiling decision is the Minions
  `BudgetGuardrails` `>=`-is-a-breach semantic (`evaluate_worker_spend`: `within = consumed < max`;
  `evaluate_preflight`: `admitted = estimate_total < ceiling`). APAA maps its `int` running total onto the SAME
  comparison — there is no second budget authority and no parallel re-derived comparison (the 21-2
  `evaluate_preflight` precedent: "Reuse, NOT fork — the breach comparison is the SAME D3 `>=`-is-a-breach
  hard-ceiling semantic"). The exact at-ceiling boundary (`total == ceiling`) is a BREACH (mirror
  `TC-COST-001-46`). The import is verified FastAPI-free (the architecture's reuse-target list) — the
  import-isolation gate proves it.
- **No floats — ever (AR4 / NFR-P1).** Credits + work-unit counts are `int`; the NFR-C1 baseline ratio is an
  exact `Fraction` (`audit_cost / build_cost_proxy`, reduced); flags are `bool`; ids/reasons are `str`. The
  Minions `BudgetPolicy` fields are `float` — that float NEVER reaches an `.apaa/` payload; the import is used
  for its DECISION over `int`/`Fraction` APAA values, and the canonical serializer REJECTS `float` as the
  determinism backstop. The 1.6 gate / 2.1 deep-% / 2.5 entropy `Fraction`-not-float precedent applies.
- **Pure/impure separation (master rule, AR8).** `cost/budget_governor.py` is PURE — the config + the
  accounting fold + the report + the baseline ratio over in-memory inputs; it never opens a file, reads a clock,
  or calls an LLM. The IMPURE shell is the snapshot WRITE (in the pipeline, via `write_payload`). ✅ a pure
  `account_spend(contributions, config)` · ❌ an accountant that reads the FS or calls `datetime.now()`.
- **Zero LLM tokens in V1 (NFR-D2).** The Epic-1/2 pipeline calls NO LLM (the dispatch port is Epic 6), so the
  ONLY V1 cost contributions are the deterministic, zero-token work units (files indexed / tool/breadth
  invocations / detector passes). There is NO real LLM credit metering in V1 — the accounting MECHANISM is
  built so that when Epic 6 wires the LLM port, real credits fold into the SAME accountant. Document this: the
  V1 contributions are a deterministic proxy, not a billed LLM total.
- **NFR-C1 is MEASURE-and-REPORT, not gate (epic Story 3.1 second AC).** Report the audit cost as a `Fraction`
  of the build-cost proxy; do NOT assert / fail on the ≤10–20% target in V1 (it is a post-V1 measurement goal).
  The build-cost proxy is deterministic + content-derived (reuse the existing LOC map — `compute_loc_by_file`)
  so the ratio is byte-stable. Guard `build_cost_proxy == 0` total-safe (the 1.6 `total == 0` floor-first guard
  precedent) — never a divide-by-zero / `float('inf')`.
- **The ceiling-reached flag is the Story 3.2 seam, exposed not acted on.** This story EXPOSES `ceiling_reached`
  + the running total; Story 3.2 QUERIES it to halt + mark the remainder `skipped` + downgrade. Do NOT halt the
  run, do NOT mark files `skipped`, do NOT touch the verdict math here. The frozen 1.6 gate is UNCHANGED.
- **The snapshot is the Story 3.4 resume seam, persisted not resumed.** Persist the `CostLedger`/`CostReport`
  to `.apaa/state/` (content-addressed, the 1.3 store). Story 3.4 reads it to restore accumulated spend; this
  story does NOT build the restore-and-continue loop. (Epic-2 retro §6: 3.4 resumability rides the persisted
  run-state + the 2.4 snapshots — keep the cost snapshot shape simple + additive so 3.4 does not inherit a
  richer shape than needed.)
- **Determinism (NFR-P1).** The total, the decision, the report, and the baseline ratio are a pure
  deterministic function of the contributions + config; the same repo@commit + config yields a byte-identical
  snapshot; two input orderings of the same contributions yield the identical result. Pin a byte-stability +
  order-independence test (the discipline that held byte-stable across all of Epic 2; apply it to this new
  cost-accounting determinism surface per AI-E2-5).
- **Error/degradation → typed, never crash (AR10).** A malformed accounting input (a `float` contribution / a
  negative ceiling / a non-`int` credit) → a typed `BudgetGovernorError` / `CostAccountingError` (ValueError
  subclass) localized to the module. NO bare `except: pass`, NO `print()` in library code, NO silent coerce.
  Cost-accounting failure in the pipeline degrades to the existing `PipelineError` (exit `1`).
- **No absolute host paths / secrets in artifacts (NFR-S1).** The cost snapshot carries `int`/`Fraction`/`bool`/
  `str` provenance only — never `repo_path`, never source/secret bytes (the 1.3 DN-3 / 2.3 /
  `to_provenance_payload()` precedent — the run-state never records the absolute repo root).
- **Headless / import boundary (§3.7, AR7/AR9).** No UI, no HTML/CSS/JS, no FastAPI route. APAA is downstream of
  the HTTP/A2A boundary; the new pure module takes no token, registers no route, imports only the FastAPI-free
  `budget_guardrails` leaf, and joins `_MODULES_UNDER_GUARD`.

### The cost-accounting model (the AC1–AC4 reference — lock + document)

| concept | source | form |
|---|---|---|
| budget ceiling | operator via `AuditRequest.budget` / `--budget` | `ceiling_credits: int | None` (None = no ceiling, OI3 — NO numeric default) |
| cost contributions | V1 deterministic zero-token work units (files indexed / tool invocations / detector passes) | `int` credits each, PASSED IN (pure planner over them) |
| running total | the fold | `total_credits: int` |
| breach decision | REUSED `BudgetGuardrails` `>=`-is-a-breach (no fork) | `bool` (`total >= ceiling`; no-ceiling → admit) |
| `ceiling_reached` | the decision, exposed for Story 3.2 | `bool` (False when no ceiling) |
| NFR-C1 baseline | `audit_cost / build_cost_proxy` (proxy = content-derived, reuse LOC map) | `Fraction` (reduced; never float; total-safe on proxy 0) |
| `CostLedger`/`CostReport` | the whole accounting outcome | frozen: total + ceiling + ceiling_reached + per-axis `int` breakdown + baseline `Fraction` |

Invariants: no `float` anywhere; the same repo@commit + config → a byte-identical snapshot; the breach decision
is the REUSED Minions hard-ceiling semantic; no-ceiling is a first-class admit-everything state; NO numeric
default (OI3).

### Decisions the dev must lock (record in the docstring + Change Log)

- **Module placement** — `cost/budget_governor.py` (the architecture's locked home for FR21/FR22; add
  `cost/__init__.py` if the sub-package is new). Keep ≤1200 lines (NFR-M1).
- **Config field** — prefer reusing the existing `AuditRequest.budget` (`int`, `ge=0`) with `0 = no ceiling`;
  add a NEW additive field ONLY if a richer config is genuinely needed (avoid a speculative abstraction —
  CLAUDE.md §5). Lock the choice + the `0 → None` mapping + the OI3 no-numeric-default rule.
- **Accounting API shape** — `account_spend(contributions, *, config) -> CostLedger` (a pure fold) vs a
  `CostAccountant` stateful-but-pure folder. Lock the exact signature + the contribution shape (a mapping /
  sequence of `int`-credit work units) + the per-axis breakdown keys.
- **The reuse point in `budget_guardrails`** — which method's `>=`-is-a-breach decision APAA maps onto
  (`evaluate_worker_spend` is the closest `credits_consumed`-vs-`max` shape; `evaluate_preflight` is the
  admit/reject shape). Lock + document (no fork).
- **The NFR-C1 build-cost proxy** — lock the deterministic content-derived proxy (recommended: total LOC from
  the existing `compute_loc_by_file` map; alt: total indexed file count). Document why it is a proxy (V1 has no
  real build-cost telemetry) + the `proxy == 0` total-safe rule.
- **`CostLedger`/`CostReport` field names + shape** — lock the names + the `schema_version` + the breakdown
  keys (additive-only — the 3.4 resume seam + a future Epic-6 LLM-credit axis fold over it).
- **Persist-now vs defer the snapshot to Story 3.4** — the in-memory accounting core + report is the in-scope
  deliverable; the snapshot persistence to `.apaa/state/` is the 3.4 resume seam. Decide whether to persist now
  (recommended — it is additive + the 3.4-ready artifact) or defer; document the choice.
- **Typed error type** — `BudgetGovernorError` / `CostAccountingError` (`ValueError` subclass) localized to the
  module (mirror `RepoIntakeError` / `DepthSemanticsError` / `PartitionerError` / `CriticalSubsystemError`).
- **Test area** — `APAA-COST` (`TC-APAA-COST-001-NN`) — a new area for the cost module, continuing the
  per-module-area convention. Lock the choice.

### Precedent inherited from Stories 1.1–1.7 + 2.1–2.6 (done) — honor these decisions

- **No second serializer / reuse the 1.1 spine.** Any `.apaa/` bytes go through `store/canonical.dumps_bytes`
  via `EnvelopeWriter.build` + the writer; the AST single-serializer gate enforces it (kept green per AI-E2-5).
- **Reuse the 1.3 store shell + `write_payload`, do not re-implement.** `ApaaStorePaths` (containment, `state/`
  dir) + `ApaaStoreWriter.write_payload("state", ...)` already provide the content-addressed, envelope-wrapped,
  containment-checked write. REUSE verbatim; mirror the 1.3 round-trip golden (`test_store_roundtrip`).
- **Reuse `budget_guardrails` BY IMPORT (AR7), verified FastAPI-free.** The same reuse-by-import pattern proven
  across Epics 1–2; the hard-ceiling `>=` decision is the canonical authority — no fork (§3.3).
- **Frozen `extra="forbid"` models** (1.1 `Envelope`, 1.2 `Recording`/`CoverageLedger`/`Locator`, 1.4
  `RepoIntake`/`StackProfile`/`AstIndex`, 1.6 `AuditVerdict`, 2.1 `DepthEvidence`, 2.2 `CoverageReport`, 2.3
  `CriticalSubsystemSet`, 2.4 `Partition`/`PartitionPlan`): any model this story adds follows the same pattern
  with a localized `schema_version`.
- **`bool`/`int`/`Fraction`/closed-form/`str` over `float`** — every cost signal is non-`float`; the 1.1
  serializer rejects it; ratios are exact `Fraction` (the 2.1/2.2 deep-%, 2.5 entropy precedent).
- **Single serializer (AR4, §3.3)** — any JSON routes through `store/canonical.dumps`.
- **Content-derived filenames, never arrival order (AR11)** — the cost snapshot lands at a content-addressed
  `<content_hash>.json` in `state/`.
- **No absolute host paths in artifacts (NFR-S1 spirit, 1.3 DN-3 / 2.3)** — the cost snapshot carries
  `int`/`Fraction`/`bool`/`str` provenance only; the run-state never records `repo_path`.
- **`apaa_version`/`schema_version` single source** — `minions_core/apaa/__init__.py::__version__` (`"0.1.0"`);
  per-module `schema_version` is a localized constant, never env/clock.
- **Import-isolation gate is seeded, extend it (AI-E1-4/AI-E2-5)** — append the new module to
  `_MODULES_UNDER_GUARD`; do not fork.
- **Total-safe divide guard (1.6 `total == 0` floor-first precedent)** — the NFR-C1 baseline `proxy == 0`
  empty-repo case is handled total-safe (a defined "baseline undefined" marker), never a crash / `float('inf')`.

### Source tree — files to create / update

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/cost/budget_governor.py` | NEW | FR21/NFR-C1/NFR-C2 — pure `BudgetConfig` (ceiling `int | None`, NO numeric default — OI3) + `account_spend`/`CostAccountant` fold (reusing the Minions `BudgetGuardrails` `>=` hard-ceiling decision BY IMPORT, no fork) + frozen `CostLedger`/`CostReport` (`int`/`Fraction`/`bool`, no `float`) + the NFR-C1 baseline `Fraction` (measured, reported, total-safe) + `BudgetGovernorError` (typed) — PURE core |
| `minions_core/apaa/cost/__init__.py` | NEW (if absent) | sub-package shell (docstring only) |
| `minions_core/apaa/pipeline.py` | UPDATE (scope-fenced) | build the config, fold the V1 deterministic contributions, compute the NFR-C1 baseline (reuse the LOC map), persist the cost snapshot additively to `.apaa/state/`, add cost locators; NO halt (3.2), NO verdict-math change, NO single-pass split |
| `minions_core/apaa/models.py` | UPDATE (additive, if needed) | give `budget` enforcement meaning + (only if needed) an additive config field defaulting to byte-identity; document "0 = no ceiling; NO numeric default (OI3)" |
| `minions_core/apaa/cli.py` | UPDATE (thin) | flip `--budget` from recorded-only to the configured ceiling; update help to "omitted/0 = no ceiling (OI3 — Story 7.1 sizes the dogfood ceiling)"; NO new sub-command |
| `tests/apaa/test_cost_accounting.py` | NEW | config (no-ceiling default, NO magic int) + accounting fold (order-independence + byte-stability + `>=` hard-ceiling reuse incl. at-ceiling boundary) + frozen no-`float` report + NFR-C1 baseline `Fraction` (proxy-0 total-safe) + purity/frozen/typed-error/single-serializer/FastAPI-free + secret/abs-path-absent |
| `tests/apaa/test_cost_snapshot_roundtrip.py` | NEW (or extend `test_store_roundtrip.py`) | `write_payload("state", ...)` → reader round-trip: equal model + byte-identical; content-addressed filename; no absolute path/source byte |
| `tests/apaa/test_no_web_imports.py` | UPDATE | extend `_MODULES_UNDER_GUARD` with `minions_core.apaa.cost.budget_governor` |

Do NOT modify `verdict/verdict_gate.py`, `ledger/coverage_ledger.py`, `ledger/recording.py`,
`ledger/depth_semantics.py`, `ledger/critical_subsystems.py`, `index/ast_index.py`, `index/partitioner.py`,
`store/canonical.py`, `store/envelope.py`, `store/paths.py`, `store/writer.py`, or any detector (frozen/reused
contracts — verify no working-tree diff after the story; the ONLY exceptions are the additive `pipeline.py`
accounting/persistence touch + the additive `models.py`/`cli.py` config seam + the import-isolation gate file).
`minions_core/cost/budget_guardrails.py` is REUSED BY IMPORT and MUST NOT be edited (it is Minions-platform
evidence; APAA consumes it, never mutates it).

### Scope fences (do NOT pull forward)

- ❌ The **mid-run HALT / mark-remainder-`skipped` / downgrade-on-exhaustion** behavior (FR22/NFR-C2) —
  **Story 3.2**. This story EXPOSES `ceiling_reached` + the running total (the surface 3.2 queries); it does
  NOT halt the run or mark files `skipped`.
- ❌ Any **verdict-math change / `INSUFFICIENT_COVERAGE` floor semantics under exhaustion** (FR16 floor) —
  **Story 3.3**. The frozen 1.6 gate is UNCHANGED.
- ❌ The **resume-from-disk restore-and-continue** loop (FR31) — **Story 3.4**. This story PERSISTS the snapshot
  the 3.4 seam reads; it does NOT build the resume loop.
- ❌ The **numeric `$X` ceiling default / full-repo budget sizing** (OI3) — **Story 7.1**. NO hardcoded numeric
  default here.
- ❌ The **LLM dispatch port / real LLM credit metering** (Epic 6). V1 cost is the deterministic zero-token work
  units only; the mechanism is built so Epic 6 folds real credits into the SAME accountant.
- ❌ The **shared Minions pre-flight estimator layer** (Minions Epic 21 / ADR #22) — explicitly OUT of APAA V1.
  APAA V1 keeps the crude in-product ceiling (this mechanism).
- ❌ Any change to the **1.6 verdict gate / 1.2 ledger enum / `grade_entry` / 1.1 serializer / 1.4 index / 2.x
  detectors / 2.4 partitioner** contracts — all frozen/reused.
- ❌ A **new HTTP route / FastAPI surface / UI** (§3.7).

### Deferred-work seam (record if surfaced; do NOT build)

- **DF-1-7-A** — interim `_persist` OSError edge → Epic-3 (already open per the 1.7 review, target Epic 3). If
  the cost-snapshot persistence touches the same `_persist` path, evaluate whether DF-1-7-A's OSError-edge
  hardening is in scope or stays deferred; record the decision (do NOT silently expand scope).
- **The V1-cost-is-a-proxy limitation** — V1 has no real LLM credit metering (the dispatch port is Epic 6), so
  the accounting folds a deterministic zero-token work-unit proxy, not a billed total. This is the
  cut-order-sanctioned V1 limitation (the mechanism is forward-compatible). If a NEW defer beyond this surfaces
  during dev (e.g. the work-unit proxy proves too crude for the dogfood baseline), record it with the CC-3
  six-field schema in `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`; do NOT build it here.
- **AI-E2-3 (defer-register consolidation)** — the central `deferred-work.md` is the single canonical APAA defer
  source; if this story files a new defer, file it there (append-only), not only in the story file.

## References

- Epic: `_bmad-output/design-artifacts/ArgusAgent/epics.md` §"Epic 3" → Story 3.1 (budget-ceiling configuration &
  cost accounting); §"Open delivery inputs — LOCKED 2026-06-18" → OI3 (budget-ceiling `$X` deferred to Story
  7.1; mechanism unaffected); the FR Coverage Map (FR21 → Epic 3).
- PRD: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` → FR21 (operator-set budget ceiling), FR22 (halt on
  exhaustion — Story 3.2), NFR-C1 (baseline cost as a bounded fraction; V1 measures + reports), NFR-C2 (never
  exceed ceiling; halt deterministically), NFR-D2 (zero-token deterministic), NFR-P1 (byte-identical),
  NFR-S1/S5 (no leak / containment), NFR-M1/M2 (file-size / frozen additive).
- Architecture: `_bmad-output/design-artifacts/ArgusAgent/architecture.md` §"Core Architectural Decisions" → Decision
  E (Cost Governance: reuse `cost/budget_guardrails` BY IMPORT, halt→skip→downgrade→report); §"Implementation
  Patterns" → Pure/Impure Separation, Determinism Patterns (no float / single serializer), Reuse/Import
  Patterns (FastAPI-free leaf), Error/Degradation Patterns (typed finding, never crash); §"Project Structure"
  → `cost/budget_governor.py` (FR21/FR22); AR4/AR7/AR8/AR10/AR11; the FR-cluster → location table (Cost
  Governance → `cost/budget_governor.py`).
- Reuse target: `minions_core/cost/budget_guardrails.py` (`BudgetPolicy` + `BudgetGuardrails` D3
  `>=`-is-a-breach hard-ceiling semantic; `evaluate_worker_spend` / `evaluate_preflight`; verified FastAPI-free).
- Done spine: `minions_core/apaa/models.py` (`AuditRequest.budget` reserved seam), `cli.py` (`--budget`
  recorded-only seam), `pipeline.py` (`run_audit_detailed` / `_persist` / `compute_loc_by_file` /
  `PipelineError`), `store/canonical.py` (Fraction-not-float single serializer), `store/writer.py`
  (`write_payload`), `store/reader.py` (round-trip), `index/partitioner.py` (`compute_loc_by_file` — the
  build-cost proxy source).
- Retros (carry-forward): `_bmad-output/design-artifacts/ArgusAgent/epic-1-retro-2026-06-21.md` (AI-E1-1 adversarial
  fixtures, AI-E1-4 gates extended-not-forked); `_bmad-output/design-artifacts/ArgusAgent/epic-2-retro-2026-06-24.md`
  (AI-E2-1 pre-`review` test-existence guard / premature status flip; AI-E2-3 defer-register consolidation;
  AI-E2-5 L1-E11 loop + three structural gates + byte-stability/order-independence on new determinism surfaces;
  §6 Epic-3 readiness — 3.1 wraps `budget_guardrails` by import, no new impure-subprocess surface).
- Deferred-work: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (the central APAA defer register;
  DF-1-7-A interim `_persist` OSError edge → Epic 3).

## Dev Agent Record

### Context Reference

- Story file: `_bmad-output/design-artifacts/ArgusAgent/stories/3-1-budget-ceiling-configuration-cost-accounting.md`
- Epic: `_bmad-output/design-artifacts/ArgusAgent/epics.md` §"Epic 3" → Story 3.1; OI3 (numeric `$X` default deferred to Story 7.1).
- Reuse target (BY IMPORT, AR7 — unedited): `minions_core/cost/budget_guardrails.py` — `BudgetGuardrails.evaluate_worker_spend` (D3 `>=`-is-a-breach: `within = credits_consumed < max_worker_credits`).
- Spine reused verbatim: `store/canonical.py`, `store/envelope.py`, `store/writer.py` (`write_payload`), `store/reader.py` (`read_envelope`), `index/partitioner.py` (`compute_loc_by_file`), `models.py` (`AuditRequest.budget`), `pipeline.py` (`run_audit_detailed` / `_persist` / `PipelineError`).

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, mode=implement).

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → 567 passed (was 532; +35 new cost tests + 2 e2e pipeline cost tests; net +33 over the pre-3.1 532 baseline + the new files).
- `python -m mypy --ignore-missing-imports` on `cost/budget_governor.py`, `cost/__init__.py`, `pipeline.py`, `cli.py`, `models.py` → Success: no issues found in 5 source files.
- Structural gates re-run green with the new module present: `test_canonical_single_serializer.py` (no second `json.dumps`), `test_no_web_imports.py` (FastAPI/LLM-free import incl. the `budget_guardrails` reuse leaf).
- Mid-implementation findings resolved RED→green: (a) Pydantic `model_dump` coerces `Fraction(1,1) → "1"`, diverging from the canonical `"1/1"` — fixed by a `to_canonical_payload()` that hands LIVE `Fraction` to the 1.1 serializer (the 1.6/2.2 precedent); (b) `Fraction | str` union kept the read-back string form and broke round-trip model equality — fixed by a `_coerce_baseline` `mode="before"` validator that turns `"num/den"` back into a `Fraction`.

### Completion Notes List

- **AC1** — `BudgetConfig` (frozen, `extra="forbid"`, `BUDGET_SCHEMA_VERSION`) carries `ceiling_credits: int | None`; `budget_config_from_budget(budget)` maps `0 → None` (first-class no-ceiling, OI3), `>0 → ceiling`. An AST test asserts NO numeric default literal on the `ceiling_credits` field (OI3); negative budget → typed `ValidationError` (model `ge=0`) AND a typed `BudgetGovernorError` on the direct call.
- **AC2** — pure `account_spend(contributions, *, config, build_cost_proxy) -> CostLedger` folds `int` contributions into a running `int` total (order-independent + byte-stable, pinned by a two-ordering test); the breach decision REUSES `BudgetGuardrails.evaluate_worker_spend` BY IMPORT via `BudgetPolicy(max_worker_credits=ceiling)` (no fork; the exact at-ceiling boundary is a breach, asserted against the imported guardrails directly); no-ceiling → admit-everything.
- **AC3** — `CostLedger` frozen, no-`float` (all `int`/`Fraction`/`bool`/`str`); `ceiling_reached` exposed True at/over, False below + False when no ceiling (the Story 3.2 seam — exposed, not acted on).
- **AC4** — `baseline_ratio(total, proxy)` returns an exact reduced `Fraction` (measured + reported, NOT gated); `proxy == 0` → the `BASELINE_UNDEFINED` str marker (total-safe, no divide-by-zero). Build-cost proxy = total physical LOC from the existing `compute_loc_by_file` map (locked + documented).
- **AC5** — the snapshot persists to `state/` via the EXISTING `ApaaStoreWriter.write_payload` over `to_canonical_payload()` (content-addressed; single serializer; round-trip equal model + byte-identical re-serialize proven; no abs-path/source/secret byte).
- **AC6** — pure (AST-scan pinned, no I/O/clock/uuid/random/float); typed `BudgetGovernorError` on float/negative/bool/non-int/non-mapping/non-str-axis inputs; FastAPI-free + LLM-free import (gate extended, not forked).
- **AC7** — 567 passed, mypy clean, `budget_governor.py` 343 lines (≤1200); single-serializer + no-web-imports gates green; the 1.6 gate / 1.2 ledger / 1.1 serializer / 1.4 index / 2.x detectors / partitioner contracts UNCHANGED (Minions `budget_guardrails.py` unedited).
- **Scope fences honored** — NO mid-run halt / `skipped` marking (3.2), NO verdict-math change / floor (3.3), NO resume loop (3.4 reads the persisted snapshot), NO numeric `$X` default (7.1), NO LLM credit metering (Epic 6 — V1 cost is the deterministic zero-token work-unit proxy). The pipeline LOC read was lifted to `_compute_loc_map` (computed once, shared by the 2.4 plan + the 3.1 baseline — no second read).
- **Carry-forwards** — AI-E2-1: all mandatory test files (`test_cost_accounting.py`, `test_cost_snapshot_roundtrip.py`, the import-gate extension, the e2e pipeline cost tests) EXIST + pass BEFORE the `review` flip; Dev Agent Record filled completely (no blank fields). AI-E2-5: gates extended-not-forked, byte-stability + order-independence fixtures applied. AI-E1-1: source/secret/abs-path-absent assertions on the persisted snapshot. No new defer surfaced (the V1-cost-is-a-proxy limitation is the cut-order-sanctioned, forward-compatible V1 choice; the work-unit proxy is adequate for the V1 baseline-report mechanism).

### File List

- `minions_core/apaa/cost/__init__.py` (NEW — sub-package shell)
- `minions_core/apaa/cost/budget_governor.py` (NEW — pure `BudgetConfig` + `account_spend`/`CostLedger` + `baseline_ratio` + `BudgetGovernorError`)
- `minions_core/apaa/pipeline.py` (UPDATE — scope-fenced cost-ledger build + additive `state/` snapshot persistence; LOC map lifted to `_compute_loc_map`)
- `minions_core/apaa/models.py` (UPDATE — `budget` field docstring: enforcement meaning + `0 = no ceiling`, OI3)
- `minions_core/apaa/cli.py` (UPDATE — `--budget` help flipped to the configured ceiling + the no-numeric-default rule)
- `tests/apaa/test_cost_accounting.py` (NEW — config / fold / frozen report / baseline / purity / typed-error / secret-absent)
- `tests/apaa/test_cost_snapshot_roundtrip.py` (NEW — write→read round-trip; content-addressed; byte-stable; no leak)
- `tests/apaa/test_pipeline_signature_demo.py` (UPDATE — +2 e2e cost tests: snapshot persisted with ceiling; no-ceiling verdict/findings byte-identical)
- `tests/apaa/test_no_web_imports.py` (UPDATE — `_MODULES_UNDER_GUARD` extended with `cost.budget_governor`)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (status → review)

## Senior Developer Review (AI)

**Reviewer:** Review (AI, adversarial code-review gate — Blind Hunter + Edge Case Hunter + Acceptance Auditor)
**Date:** 2026-06-24 · **Iteration:** 1 · **Outcome:** **PASS → status `done`**

### Summary

A clean, scope-disciplined Tier-A slice. The story delivers exactly the FR21 budget-ceiling
configuration + the pure deterministic cost-accounting mechanism + the NFR-C1 baseline report — and
nothing beyond it. Every load-bearing constraint was independently verified against the live code and
the running test suite (not merely accepted from the Dev Agent Record): the OI3 no-numeric-default rule,
the reuse-by-import of the Minions hard-ceiling decision, the no-float invariant, byte-stable round-trip,
and the scope fence (verdict math unchanged, `ceiling_reached` exposed-not-acted-on). Tests are green
(567 passed), mypy is clean, the file is 343 lines, and the structural gates (single-serializer AST,
web-import isolation, LLM-isolation) all pass with the new module present.

### Verification performed (independent, not delegated to the dev record)

- **Tests re-run:** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **567 passed** in ~14s.
- **mypy:** `--ignore-missing-imports` on `cost/budget_governor.py`, `cost/__init__.py`, `pipeline.py`, `cli.py`, `models.py` → **Success: no issues found in 5 source files**.
- **Structural gates:** `test_canonical_single_serializer.py` + `test_no_web_imports.py` (web + LLM isolation, incl. the `budget_guardrails` reuse leaf) + the two new cost test files → 39 passed.
- **Reuse-not-fork (§3.3 / AR7):** confirmed `_coerce_breach` constructs `BudgetPolicy(max_worker_credits=ceiling)` and reads `evaluate_worker_spend(total)["within_budget"]`, mapping `ceiling_reached = not within_budget`. Verified live that at-ceiling (`total == ceiling`) breaches and `total == ceiling-1` does not — identical to the imported `BudgetGuardrails` (the TC-COST-001-46 boundary). `TC-APAA-COST-001-13` asserts this against the imported guardrails directly across `{0,50,99,100,101,500}`. No parallel comparison; the `float` the policy carries internally never leaves the function (only the `bool` does).
- **Money/credits never float (AR4):** verified the canonical serializer genuinely raises `CanonicalSerializationError` on a `float` leaf (the determinism backstop is real). `baseline_ratio` is an exact reduced `Fraction`; the `to_canonical_payload()` live-Fraction handoff emits `1/1` (not `model_dump`'s `"1"`) and round-trips to an EQUAL model via `_coerce_baseline` — same pattern as 1.6/2.2. `proxy == 0` → `BASELINE_UNDEFINED` str marker, no divide-by-zero / `float('inf')`.
- **OI3 no-hardcoded-default:** `BudgetConfig.ceiling_credits` defaults to `None`; `budget == 0 → None` (first-class no-ceiling). `TC-APAA-COST-001-04` AST-scans the module to prove no numeric default literal on the field; verified directly that `BudgetConfig().ceiling_credits is None`.
- **Scope fence / byte-identity:** `test_e2e_no_ceiling_run_byte_identical_verdict_ledger_findings` genuinely compares verdict + findings bytes (content-addressed names AND bytes) across a no-ceiling vs ceiling-configured run and asserts equality — the cost snapshot is purely additive. `ceiling_reached` is exposed on `CostLedger` but never read by the pipeline (no halt, no `skipped`, no verdict-math change). The LOC map is lifted to `_compute_loc_map`, computed once, and shared by the 2.4 partition plan and the 3.1 baseline (no second read).
- **Purity / typed-error / secret-safety:** AST purity scan green (no I/O/clock/uuid/random/pathlib import); `BudgetGovernorError` raised on float/negative/bool/non-int/non-mapping/non-str-axis; the persisted snapshot carries only `int`/`Fraction`/`bool`/`str` with a closed key set and no abs-path / source / secret byte (proven on-disk).

### Acceptance Criteria — all met

AC1 (config seam, no numeric default) ✅ · AC2 (deterministic fold + reused hard-ceiling decision) ✅ ·
AC3 (frozen no-float ledger, `ceiling_reached` exposed) ✅ · AC4 (NFR-C1 baseline Fraction, proxy-0 total-safe) ✅ ·
AC5 (snapshot persistence via the existing containment shell, content-addressed, round-trip) ✅ ·
AC6 (pure / FastAPI-free / typed-error / import-isolated) ✅ · AC7 (suite green, mypy clean, ≤1200 lines, gates green, frozen contracts unchanged) ✅.
AI-E2-1 (test-existence before `review`) / AI-E2-5 (gates extended-not-forked, byte-stability + order-independence) / AI-E1-1 (secret/abs-path-absent) all discharged.

### Action Items

- **DF-3-1-A (Low, non-blocking, defensive-only):** `BudgetConfig.ceiling_credits` has no `ge=0` Field constraint, whereas `CostLedger.total_credits` does. A directly-constructed `BudgetConfig(ceiling_credits=-5)` is therefore accepted (it produces deterministic always-breach behavior, not a crash). This path is **not reachable** through the operator seam — `budget_config_from_budget` guards via `_require_non_negative_int` and the `AuditRequest.budget` field is `ge=0` — so it is a defensive-consistency nit, not a correctness defect. Suggested fix (a future hardening pass): add `ge=0` to the `ceiling_credits` Field (or reject a negative ceiling in `BudgetConfig`'s validator) for symmetry with `total_credits`. Owner: APAA dev. Not a release blocker.

---

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-06-24 | 0.1 | Initial story draft created (create-story) — budget-ceiling configuration + deterministic cost-accounting mechanism + NFR-C1 baseline report; NO numeric `$X` default (OI3 → Story 7.1); halt/skip/downgrade is Story 3.2, floor is 3.3, resumability is 3.4; reuse `budget_guardrails` `>=`-hard-ceiling BY IMPORT (no fork); Fraction-not-float, single serializer, frozen contracts; carries AI-E2-1 (pre-`review` test-existence) + AI-E2-5 (L1-E11 loop / gates). | Scrum Master (Bob) |
| 2026-06-24 | 1.1 | code-review (iter-1) → PASS / status done. Adversarial review (Blind Hunter + Edge Case Hunter + Acceptance Auditor) re-ran the full suite (567 passed) + mypy clean + the single-serializer/import-isolation gates green with the new module present, and independently verified: the at-ceiling boundary breach is the REUSED `BudgetGuardrails.evaluate_worker_spend` semantic (asserted live against the imported guardrails, no fork); the canonical serializer genuinely rejects `float` (the determinism backstop is real, not asserted); `Fraction(1,1)` serializes as `1/1` (the `to_canonical_payload` workaround works where `model_dump` would coerce to `"1"`) and round-trips to an equal model; `proxy==0` → `BASELINE_UNDEFINED` total-safe; OI3 no-numeric-default confirmed (AST test + direct check); scope fence holds (verdict/findings byte-identical across no-ceiling vs ceiling runs; `ceiling_reached` exposed but never acted on; LOC map computed once and shared with the 2.4 plan). 1 Low non-blocking note recorded (DF-3-1-A: `BudgetConfig.ceiling_credits` lacks a `ge=0` constraint — defensive only, the operator seam is fully guarded). | Review (AI) |
| 2026-06-24 | 1.0 | dev-story implement — NEW pure `cost/budget_governor.py`: frozen `BudgetConfig` (`ceiling_credits: int \| None`, `0 → None` no-ceiling, NO numeric default — OI3), pure `account_spend` fold (running `int` total; REUSES `BudgetGuardrails.evaluate_worker_spend` `>=`-is-a-breach BY IMPORT, no fork; at-ceiling boundary breaches), frozen `CostLedger` (no-`float`; `ceiling_reached` exposed for 3.2), NFR-C1 `baseline_ratio` (exact reduced `Fraction` over total-LOC proxy; `proxy==0` total-safe `BASELINE_UNDEFINED` marker), typed `BudgetGovernorError`. Config seam: `cli.py` `--budget` flipped to the configured ceiling + `models.py` `budget` docstring enforcement meaning (additive, byte-identity preserved). Scope-fenced `pipeline.py`: build the cost ledger from V1 deterministic zero-token contributions + persist the snapshot additively to `state/` via the EXISTING `write_payload` (LOC map computed once, shared with the 2.4 plan); NO halt (3.2) / NO verdict-math change / NO single-pass split. Round-trip via `to_canonical_payload()` (LIVE `Fraction` → canonical `num/den`) + `_coerce_baseline` validator (equal model on read-back). Import-isolation gate extended (not forked). 567 passed, mypy clean, 343 lines. AI-E2-1/E2-5/E1-1 discharged. Status → review. | Dev (Amelia) |
