# Story 4.1: Negative-assurance verdict semantics

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As Dana (Head of Quality at a regulated enterprise) consuming an APAA verdict,
I want every verdict expressed in **negative-assurance** terms — a `scope_statement` ("examined X, sampled
Y, did **not** cover Z"), a `materiality_bar`, a `disclaimer`, and a point-in-time stamp — that frames the
result as **"no blocking findings within the audited envelope"**, NEVER "the code is correct" / "certified",
so that legal recognizes audit-grade humility: the verdict is honest about what APAA did NOT establish
(absence of *detected* defects within the *assessed* scope), not a false positive assurance — the FIRST
story of Epic 4 (Negative-Assurance Verdict & Evidence Bundle, Tier-B; epic-4 goes `in-progress` on this
story), wiring the negative-assurance WRAPPER that Stories 3.3 / 3.4 / 2.3 explicitly fenced TO this story
over the EXISTING (frozen, done) 1.6 verdict + 3.3 floor report + 2.3 critical-subsystem set.

## Story Context

This is **Story 1 of Epic 4** (Negative-Assurance Verdict & Evidence Bundle, Tier-B — the "evidence you can
show a regulator" layer, PRD Journey 4). epic-4 transitions `backlog → in-progress` on this story. It builds
on the fully-done Epics 1+2+3 (661 passed, mypy clean, all files ≤1200 lines as of the Epic-3 retro
2026-06-27). It is the **negative-assurance verdict-semantics WRAPPER** story.

**The verdict + its inputs ALREADY ship — this story WRAPS them, it does NOT change the verdict math.** The
honesty surface this story needs already exists and is frozen:

- **Story 1.6 (done) — `verdict/verdict_gate.py` (REUSE verbatim, do NOT edit).** The PURE
  `evaluate_verdict(ledger, findings, *, critical_subsystems_all_deep=True) -> AuditVerdict` fold returns the
  LOCKED three-member vocabulary `Verdict.{RELEASE_READY, NOT_READY_FOR_RELEASE, INSUFFICIENT_COVERAGE}`
  (`BLOCKED` is the documented demo SHORTHAND module-constant alias of `NOT_READY_FOR_RELEASE`, NOT a fourth
  member). The frozen `AuditVerdict` carries `verdict`, `deep_ratio: Fraction`, `deep_count`, `total_count`,
  `counts_by_depth`, `blocking_finding_count`, `ordered_findings`, `critical_subsystems_all_deep`,
  `exit_code`. The exit-code map is `RELEASE_READY→0 · NOT_READY_FOR_RELEASE→2 · INSUFFICIENT_COVERAGE→3 ·
  crash→1` (AR3). **This story READS the `AuditVerdict` — it does NOT change the gate, thresholds, floor-wins
  precedence, exit-code map, or the verdict vocabulary.** Verify NO working-tree diff to `verdict_gate.py`.
- **Story 3.3 (done) — `cost/exhaustion.py::InsufficientCoverageFloorReport` + `build_floor_report` (REUSE
  verbatim, do NOT edit).** The PURE floor report folds the `AuditVerdict` + `HaltReport` into the honest
  "assessed X% deep; floor 20%" surface: `verdict`, `deep_ratio`, `floor`, `below_floor`,
  `driven_by_exhaustion` (= `HaltReport.halted_on_exhaustion` — exhaustion-driven vs intrinsic floor),
  `assessed_count`, `skipped_on_exhaustion_count`, `message`. **3.3 explicitly fenced the negative-assurance
  WRAPPER to THIS story** (3.3 Story Context / Dev Notes: *"The negative-assurance verdict WRAPPER —
  `scope_statement` + `materiality_bar` + `disclaimer` + point-in-time stamp (FR17/NFR-A3) is Story 4.1,
  `verdict/negative_assurance.py`. THIS story produces the NEUTRAL floor DATA the 4.1 scope statement will
  fold over — NOT the wrapper."*). This story consumes that neutral floor data.
- **Story 2.3 (done) — `ledger/critical_subsystems.py::CriticalSubsystemSet` (REUSE verbatim, do NOT edit).**
  The frozen set carries `paths` (sorted critical-file set), `origins` (per-path `CriticalOrigin` =
  `heuristic` | `operator_designated`), `designated_but_unmatched` (operator-forced paths matching no
  candidate). The pipeline ALREADY computes it (`identify_critical_subsystems`) in the shared
  `_assemble_and_persist` fold (`pipeline.py:673`) and feeds `critical_subsystems_all_deep` into the gate —
  but it is currently NOT persisted (only operator INTENT via `request.to_provenance_payload()` is). **This
  story is the home of DF-2-3-B** (see Carry-Forward below): persist the computed `CriticalSubsystemSet` so
  the scope statement can narrate which critical subsystems were / were NOT covered deeply.
- **Story 2.2 (done) — `ledger/coverage_report.py` (REUSE if it fits).** The PURE `DepthAggregate`
  (exact-`Fraction` deep-%) + `build_coverage_report` + `render_text`/`render_json`/`render` — the per-depth
  counts the scope statement narrates ("examined X deep, Y shallow, Z skipped") are ALREADY derivable here.
  Prefer REUSING this surface over forking a parallel per-depth render.
- **Story 1.1 (done) — `store/{canonical,envelope}.py` (REUSE).** The single serializer
  (`canonical.dumps_bytes`, rejects `float`, `Fraction → "num/den"`, `sort_keys=True`); the content-hashed,
  schema-versioned, **prev-hash-chained** envelope. The point-in-time stamp is the envelope's `created_at`
  (NFR-D3: hash-over-canonical-payload-ONLY — the stamp is NEVER in the hashed payload). Any persistence
  goes through this EXISTING shell — no second serializer/writer.
- **Story 1.3 (done) — `store/{writer,paths,reader}.py` (REUSE).** `ApaaStoreWriter.write_payload("state",
  ...)` (content-addressed, `is_relative_to` containment-checked), `store/reader.py` round-trip.
- **Story 3.4 (done) — `pipeline.py::_assemble_and_persist` / `resume_audit_detailed` (UPDATE,
  scope-fenced).** The SHARED fold both the fresh (`run_audit_detailed`) and resume paths run. It already has
  `verdict`, `critical` (`CriticalSubsystemSet`), `floor_report`, `ledger`, `request` all in scope at the
  build site (`pipeline.py:658-692`). This is the SINGLE seam where the negative-assurance wrapper attaches —
  so a RESUMED run produces the SAME wrapper as an uninterrupted run (the 3.4 byte-identity discipline).

**The net-new deliverable of THIS story.** A scope-thin, ADDITIVE, PURE negative-assurance verdict WRAPPER +
its persistence + its e2e proof:

1. a new PURE module **`minions_core/apaa/verdict/negative_assurance.py`** (the architecture-locked home,
   `architecture.md:429`) with:
   - a frozen **`NegativeAssuranceVerdict`** (or locked name) Pydantic v2 model — `frozen=True,
     extra="forbid"`, localized `schema_version` — that WRAPS (does not duplicate) the EXISTING verdict
     surface and adds the FR17/NFR-A3 negative-assurance framing:
     - the underlying `verdict: str` (= `AuditVerdict.verdict.value`) + `exit_code: int` (REUSED, unchanged);
     - a **`scope_statement`** — structured, deterministic, NO prose-only fields: what was examined (deep
       count / paths or count), what was sampled (shallow / tool-scanned counts), and what was **NOT covered**
       (skipped / skipped-on-exhaustion / inferred counts) — the "examined X, sampled Y, did NOT cover Z"
       triad, derived from the EXISTING `AuditVerdict.counts_by_depth` + the `CriticalSubsystemSet` (which
       critical subsystems were / were NOT examined deeply) + the floor report's assessed/skipped counts;
     - a **`materiality_bar`** — the operator-set materiality threshold the audit ran under (REUSED from
       `AuditRequest.materiality_bar`, recorded so the verdict states the bar it judged against);
     - a **`disclaimer`** — a deterministic, fixed negative-assurance statement (e.g. *"This is negative
       assurance: APAA found no blocking findings within the assessed scope. It is NOT a certification, NOT a
       proof of correctness, and NOT assurance about un-assessed code."*) — a module CONSTANT (no clock, no
       interpolation of volatile values into the hashed payload);
   - a PURE **builder** `build_negative_assurance_verdict(verdict: AuditVerdict, floor_report:
     InsufficientCoverageFloorReport, critical: CriticalSubsystemSet, *, materiality_bar: ...) -> ...` that
     folds the EXISTING records into the wrapper — over in-memory inputs, NO I/O, NO clock, NO LLM (AR8). It
     is honest + populated for ALL THREE verdicts (RELEASE_READY frames "no blocking findings within scope";
     INSUFFICIENT_COVERAGE folds the floor-report message into the scope statement; NOT_READY_FOR_RELEASE
     frames the blocking findings within scope) — never an over-claim;
2. **scope-fenced pipeline wiring** in the shared `_assemble_and_persist` fold: build the negative-assurance
   verdict from the EXISTING `verdict` + `floor_report` + `critical` + `request.materiality_bar` AFTER the
   verdict + floor-report build, persist it additively to `.apaa/state/` via the EXISTING
   `ApaaStoreWriter.write_payload("state", ...)`, add the locator to `AuditResult.locators`, AND expose it on
   `AuditResult` as an additive optional field (default-preserving). The point-in-time stamp is the envelope's
   `created_at` on that persisted artifact;
3. **DF-2-3-B closure** — persist the computed `CriticalSubsystemSet` (paths + per-path `origins` +
   `designated_but_unmatched`) to `.apaa/state/` so the scope statement's "which critical subsystems were /
   weren't covered" narration is auditable from disk (the central register's `target_story` for DF-2-3-B is
   `epic-4-negative-assurance-verdict-semantics` = this story);
4. **the no-over-claim assertion** — the verdict language NEVER implies certification / "correct" / "proven
   defect-free"; it is scope-bounded negative assurance, asserted by a test over all three verdicts;
5. **byte-identity discipline** — the wrapper + its message are byte-deterministic (no clock/uuid/random in
   the hashed payload; no float; sorted content-derived fields; stamp is the envelope `created_at`, excluded
   from the content hash per NFR-D3), so 4.2 (integrity lint) and 4.3 (evidence bundle) inherit a determinate
   surface, and a RESUMED run's wrapper is byte-identical to an uninterrupted run's (the 3.4 keystone applied
   to the new surface).

The model + builder + `scope_statement`/`message`/`disclaimer` render are PURE (AR8) and join the
import-isolation gate. The persistence WRITE is the impure pipeline shell.

**Carry-forward from the Epic-3 retro (2026-06-27) + the 3.3/3.4/2.3 discharge (CLAUDE.md §9.1 / L1-E11).**
Each item below is an Epic-4-backlog action item this story discharges (per the L1-E11 operating model:
package the prior retro's action items as the next epic's backlog).
- **AI-E3-1 (test-infra 🟠) — keystone-fixture-adequacy practice (the marquee Epic-3 lesson; apply FIRST to
  4.1).** The 3.4 review FAIL was a green keystone test that structurally COULD NOT catch its keystone bug
  (the fixture's assessed prefix had no non-deep entry, so the byte-identity assertion could never observe the
  dropped coverage). **For this story's keystone tests, the fixture MUST contain ≥1 element of EVERY
  class the equivalence/assertion preserves, AND the test MUST be demonstrated RED against a deliberate
  violation before it is trusted.** Concretely: (a) the "no-over-claim" assertion must run over a
  `RELEASE_READY` AND a `NOT_READY_FOR_RELEASE` AND an `INSUFFICIENT_COVERAGE` verdict (all three vocabulary
  members), and must go RED if the disclaimer/scope language is mutated to a certification phrase; (b) the
  scope-statement "did NOT cover Z" assertion must use a fixture with ≥1 skipped AND ≥1 inferred AND ≥1
  shallow entry (every not-deep class), and go RED if a not-covered class is silently dropped from the scope
  statement; (c) the resume-byte-identity assertion (if added) must put a non-deep entry in the assessed
  prefix (the exact 3.4 mask). Document the RED-then-green demonstration in Completion Notes.
- **AI-E3-3 (governance 🟢) — central defer register.** If this story files a NEW defer, file it append-only
  in `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (the single canonical APAA defer source), not only
  in the story file. **DF-2-3-B is CLOSED by this story** — append a closure note to its central-register
  entry (append-only; do NOT rewrite the original entry per §3.4 evidence immutability). The Epic-3 retro
  re-carried that DF-3-1-A / DF-2-3-A / DF-1-4-A / DF-1-7-A/B remain un-backfilled — out of THIS story's
  scope (do NOT expand), but if convenient, the closure note is the moment to be precise.
- **AI-E3-5 (security 🟢) — close DF-2-3-B in its Epic-4 home (= this story).** Persist the computed
  `CriticalSubsystemSet` (origins + `designated_but_unmatched`) so a reader can distinguish an override of a
  genuine heuristic hit from a no-op exclude — feeding the scope statement's critical-subsystem narration.
- **AI-E3-6 (process 🟢) — keep exercising the L1-E11 loop + the three structural gates + the standing
  cross-env determinism suite.** Append the new `verdict/negative_assurance.py` to `_MODULES_UNDER_GUARD` in
  `tests/apaa/test_no_web_imports.py` (extend, NOT fork); keep the single-serializer AST gate
  (`test_canonical_single_serializer.py`) green (any wrapper JSON goes through `store/canonical.dumps`, never
  a direct `json.dumps`); apply byte-stability + order-independence fixtures to the wrapper surface; apply the
  3.5 cross-env discipline to the new write path (a determinate, sorted, float-free, clock-free payload).
- **AI-E3-2 / AI-E2-1 (process 🟠) — pre-`review` mandatory-test-existence guard.** This story does NOT flip
  `status: review` until ALL mandatory test files (`tests/apaa/test_negative_assurance.py`, the e2e
  negative-assurance assertions in `test_pipeline_signature_demo.py`, the import-isolation extension, the
  round-trip if persisted, the critical-subsystem persistence round-trip) EXIST and pass; the Dev Agent
  Record is filled completely (no blank placeholders). Treat the test-existence precondition as a hard gate on
  the `review` flip.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 4.1) + the architecture / PRD. Drivers: **APAA-FR-17** (express
> every verdict in negative-assurance terms with a scope statement, materiality bar, disclaimer, and
> point-in-time stamp — the CENTRAL driver), **APAA-NFR-A3** (every verdict carries a scope statement,
> materiality bar, disclaimer, and point-in-time stamp), **APAA-FR-15** (the verdict is the pure-function
> gate result this story WRAPS, UNCHANGED), **APAA-FR-18 / AR3** (the exit-code wire contract `0/2/3/1` is
> UNCHANGED — REUSED, not modified), **APAA-FR-16/FR-22** (the floor report this wrapper folds over —
> exhaustion-driven vs intrinsic narration), **APAA-FR-4** (the critical-subsystem set the scope statement
> narrates — DF-2-3-B persistence), **APAA-NFR-D2** (deterministic, zero-LLM-token — the wrapper is a pure
> fold over the EXISTING `AuditVerdict` + floor report + critical set), **APAA-NFR-D3** (the content hash
> covers the canonical payload ONLY — the point-in-time stamp is the envelope `created_at`, EXCLUDED from the
> hash), **APAA-NFR-P1** (byte-identical wrapper + message across hosts/runs/input-orderings; no float; a
> resumed run's wrapper is byte-identical to an uninterrupted run's), **APAA-NFR-S1** (no source / secret /
> absolute-host-path bytes in the wrapper), **APAA-NFR-S5** (any FS write containment-checked via the 1.3
> shell), **APAA-NFR-A1/M2** (frozen, schema-versioned, additive-only contracts; prev-hash-chained envelope),
> **APAA-NFR-M1** (≤1200-line files), **AR4** (no `float`; ratios are exact `Fraction` reused from
> `AuditVerdict.deep_ratio`; single canonical serializer; no clock/uuid/random/iteration-order —
> content-derived, AR11), **AR8** (pure/impure separation — the wrapper model + builder + render are PURE; the
> WRITE is the impure shell), **AR10** (typed failure, never an uncaught raise), **AR11** (`.apaa/` filenames
> content-derived; sorted sets).
>
> **SCOPE FENCE — Tier-B, single-purpose.** This story delivers ONLY: (1) the negative-assurance verdict
> WRAPPER — a frozen, PURE `NegativeAssuranceVerdict` surface (`verdict/negative_assurance.py`) that WRAPS
> the EXISTING 1.6 `AuditVerdict` + 3.3 floor report + 2.3 critical set and adds a structured deterministic
> `scope_statement` ("examined X, sampled Y, did NOT cover Z"), a `materiality_bar` (REUSED from the request),
> and a fixed `disclaimer` constant — framed as scope-bounded negative assurance, NEVER certification /
> "correct"; (2) the point-in-time stamp as the persisted artifact's envelope `created_at` (NFR-D3 — never in
> the hashed payload); (3) the additive persistence of the wrapper + the computed `CriticalSubsystemSet`
> (DF-2-3-B) via the EXISTING writer; (4) the no-over-claim assertion across all three verdicts; (5) the
> byte-identity / resume-byte-identity proof. It does NOT build, and MUST NOT pull forward: the **referential-
> integrity lint** of `.apaa/` state (FR26/NFR-A2 — **Story 4.2**); the **evidence-bundle export** (FR29 —
> **Story 4.3**); the **CI-blocking secret-containment property suite** (FR28 enforcement/NFR-S1/AR9 —
> **Story 4.4**); the **adversarial Prosecutor** (FR19 — Epic 6); the **HITL escalation / decision record**
> (FR23/FR24 — Epic 6); ANY change to the **1.6 verdict gate / its thresholds / floor-wins precedence /
> exit-code map / verdict vocabulary / 1.2 ledger / `grade_entry` / 1.1 serializer / 3.2 halt mechanism / 3.3
> `build_floor_report` / 2.3 `identify_critical_subsystems`** contracts (all frozen/reused). It does NOT add a
> NEW HTTP route / FastAPI surface / UI (§3.7). It does NOT change `cli.py` argv/exit behavior (DF-3-4-A
> `--resume` stays deferred). Wrap the verdict honestly, persist the scope, prove no over-claim, then stop.

**AC1 — Every verdict is wrapped in negative-assurance terms: scope statement, materiality bar, disclaimer, point-in-time stamp (FR17, NFR-A3, NFR-A1)**
**Given** a computed `AuditVerdict` (any of the three vocabulary members), its 3.3 `InsufficientCoverageFloorReport`, and the 2.3 `CriticalSubsystemSet`
**When** the PURE `build_negative_assurance_verdict(...)` folds them with the operator `materiality_bar`
**Then** `verdict/negative_assurance.py` produces a frozen `NegativeAssuranceVerdict` carrying: (a) a
**`scope_statement`** structured as the "examined X, sampled Y, did NOT cover Z" triad — examined =
`audited_deep` count (from `AuditVerdict.counts_by_depth`), sampled = `audited_shallow` + `tool_scanned_only`
counts, NOT-covered = `skipped` + `inferred` counts (+ the floor report's `skipped_on_exhaustion_count` and
`driven_by_exhaustion` flag), plus which critical subsystems were / were NOT examined deeply (from the
`CriticalSubsystemSet` `paths`/`origins`/`designated_but_unmatched`); (b) a **`materiality_bar`** REUSED from
`AuditRequest.materiality_bar`; (c) a fixed **`disclaimer`** (module constant); (d) the underlying `verdict`
value + `exit_code` REUSED unchanged
**And** the **point-in-time stamp** is the envelope `created_at` on the persisted wrapper artifact (NOT a
field in the hashed canonical payload — NFR-D3), so the stamp is present in the on-disk envelope but never
breaks content-addressing.

**AC2 — The verdict language NEVER implies certification or "correct" — scope-bounded negative assurance only (FR17, the no-over-claim keystone)**
**Given** the wrapper produced for EACH of the three verdicts — `RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`
**When** the `scope_statement` + `disclaimer` + any rendered message are inspected
**Then** the language is scope-bounded negative assurance — a `RELEASE_READY` wrapper states "no blocking
findings **within the assessed scope**" (NOT "the code is correct" / "certified" / "proven defect-free" /
"passed"); a `NOT_READY_FOR_RELEASE` wrapper states the blocking findings were found within scope; an
`INSUFFICIENT_COVERAGE` wrapper folds the floor message ("assessed X% deep; floor 20%; no repo-wide verdict
rendered") — and NONE of the three contains a certification/correctness over-claim token (asserted by a test
that scans the serialized wrapper for a forbidden-phrase set, e.g. `{"certif", "is correct", "proven",
"guarantee", "defect-free", "bug-free"}`, case-insensitive)
**And** the no-over-claim test is demonstrated RED against a deliberate violation (mutate the disclaimer to a
certification phrase → the test FAILS), then green on the real text (AI-E3-1 keystone-fixture-adequacy).

**AC3 — The scope statement honestly narrates what was NOT covered, including critical subsystems (FR17, FR4, NFR-A3 — the assessed-scope-honesty driver)**
**Given** a ledger with ≥1 entry of EVERY not-deep class (`audited_shallow`, `tool_scanned_only`, `inferred`,
`skipped`) AND a `CriticalSubsystemSet` with ≥1 critical path that was NOT examined deeply (e.g. graded
`audited_shallow` or `designated_but_unmatched`)
**When** the scope statement is built
**Then** the "did NOT cover Z" portion explicitly accounts for every not-deep class (none silently dropped),
and the critical-subsystem narration names that ≥1 critical subsystem was NOT examined deeply (so a consumer
knows the verdict's scope excluded a critical area) — distinguishing a critical subsystem covered deeply from
one only shallowly seen or `designated_but_unmatched`
**And** this is demonstrated RED against a deliberate violation (drop a not-deep class from the scope
statement, or omit the critical-not-deep narration → the assertion FAILS), then green (AI-E3-1).

**AC4 — The computed `CriticalSubsystemSet` is persisted to `.apaa/state/` (DF-2-3-B closure, FR4, NFR-A1)**
**Given** a completed audit whose pipeline computed a `CriticalSubsystemSet` (via the EXISTING
`identify_critical_subsystems`)
**When** the audit persists run state
**Then** the COMPUTED `CriticalSubsystemSet` (final `paths` + per-path `origins` + `designated_but_unmatched`)
is persisted to `.apaa/state/` via the EXISTING `ApaaStoreWriter.write_payload("state", ...)` — content-
addressed `<content_hash>.json`, containment-checked (NFR-S5), single 1.1 serializer (no second `json.dumps`)
— so a reader can distinguish an override of a genuine heuristic hit from a no-op exclude (the DF-2-3-B
suggested fix), and the negative-assurance scope statement's critical narration is auditable from disk
**And** re-reading via `store/reader.py` reconstructs an EQUAL `CriticalSubsystemSet` + round-trips
byte-identically; the operator-INTENT provenance (`request.to_provenance_payload()`) the run already persists
is UNCHANGED (this ADDS the computed set, it does not replace the intent record — additive, NFR-M2).

**AC5 — The wrapper is frozen, no-`float`, secret-safe, schema-versioned, prev-hash-chained; persists via the EXISTING shell (NFR-M2, NFR-A1, AR4, NFR-S1, NFR-S5, AR11, FR25)**
**Given** a built negative-assurance wrapper
**When** it is inspected / serialized / persisted
**Then** it is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`, localized `schema_version`) with
ALL leaves `str` / `int` / `bool` / `Fraction` (rendered `"x/y"` by the 1.1 serializer) — **NO `float`
anywhere** (the canonical serializer rejects it), NO volatile `run_id`/`created_at` in the hashed payload
(NFR-D3 — the stamp lives in the envelope), NO absolute host path / source / secret byte (only repo-relative
POSIX paths from the already-sanitized `CriticalSubsystemSet` + `int`/`bool`/`str` provenance — never
`repo_path`), verified by an AI-E1-1-style assertion that no source/secret/absolute-host-path byte appears in
the serialized wrapper (and a non-ASCII café/Cyrillic critical path round-trips intact)
**And** the persist goes through `ApaaStoreWriter.write_payload("state", payload, schema_version=...,
producer="apaa.verdict.negative_assurance")` — bytes are `EnvelopeWriter.build(...)` →
`store/canonical.dumps_bytes` (single serializer; the AST gate enforces it), filename content-addressed
`<content_hash>.json` (never arrival order — AR11), the `ApaaStorePaths` `is_relative_to` containment check
guards the path (NFR-S5), the envelope `prev_hash` chains to the prior artifact (NFR-A1), and re-reading via
`store/reader.py` reconstructs an EQUAL model + round-trips byte-identically (NFR-P1).

**AC6 — A run's wrapper is byte-identical across fresh vs resumed execution and across input orderings (NFR-P1, the regression-safe + 3.4-resume keystone)**
**Given** the SAME repo+commit+budget+materiality audited (a) fresh end-to-end and (b) via the 3.4
resume-from-disk path, AND the same inputs presented in different ledger/finding orderings
**When** the negative-assurance wrapper is built + persisted on each path
**Then** the wrapper's canonical payload bytes are BYTE-IDENTICAL across fresh-vs-resumed and across input
orderings (the wrapper is built in the SHARED `_assemble_and_persist` fold both paths run, so a resumed run
cannot diverge — the 3.4 keystone applied to the new surface), and the existing
verdict/ledger/findings/halt-report/floor-report artifacts are UNCHANGED versus the pre-4.1 (3.x) output (the
wrapper + the critical-set artifact are PURELY ADDITIVE new `state/` artifacts that do not alter existing
bytes)
**And** this is proven by an e2e test that compares the wrapper payload bytes across a fresh run and a resumed
run of equivalent budget — with the keystone-fixture-adequacy discipline (AI-E3-1): the fixture has a
non-deep entry in the assessed prefix (the exact 3.4 mask), and the test is demonstrated RED if the wrapper is
made to depend on input order.

**AC7 — The new pure logic is PURE, frozen-contract, deterministic, typed-error, import-isolated; the whole suite green; mypy clean; ≤1200 lines (NFR-D2, NFR-P1, AR8, AR10, M1, M2)**
**Given** the new `NegativeAssuranceVerdict` model + the PURE `build_negative_assurance_verdict` builder (+
any scope-statement / message render helper) in `minions_core/apaa/verdict/negative_assurance.py`
**When** they are imported and exercised in unit tests
**Then** the builder + the model build + the renders perform NO filesystem I/O, NO clock read
(`datetime.now`/`time.time` — the stamp is the envelope `created_at`, set by the impure writer), NO
`uuid4`/`os.getpid()`/`random`, NO LLM/network call, NO dict/`set`-iteration-order reliance — they are PURE
functions over in-memory inputs (the persistence WRITE is the impure pipeline shell)
**And** the new model is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`, localized
`schema_version` — the 1.1/1.2/1.6/3.1/3.2 precedent); NO `float` anywhere (ratios are exact `Fraction`s
REUSED from `AuditVerdict.deep_ratio`; counts are `int`; flags are `bool`; the `materiality_bar` carries its
existing non-float type from `AuditRequest`; paths are `str`); any JSON rendering routes through
`store/canonical.dumps` (single 1.1 serializer — no second `json.dumps`)
**And** a malformed input (a non-`AuditVerdict`, a non-`InsufficientCoverageFloorReport`, a non-
`CriticalSubsystemSet`, or an inconsistent verdict/floor-report pair) raises a typed error (a localized
`NegativeAssuranceError` `ValueError` subclass mirroring `ExhaustionError`/`CriticalSubsystemError`) — never a
silent coerce / bare `except: pass` / `print()` in library code (AR10); any wrapper-stage failure in the
pipeline degrades to the existing typed `PipelineError` (exit `1`), never an uncaught traceback
**And** the new module is appended to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py` (extend,
do NOT fork) and importing it does NOT transitively import `fastapi`/`uvicorn`/`starlette` or any LLM/api
module (assert absence from `sys.modules`)
**And** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` passes (including the
new `tests/apaa/test_negative_assurance.py`: AC1 the four negative-assurance fields over all three verdicts;
AC2 the no-over-claim forbidden-phrase scan [demonstrated RED]; AC3 the "did-NOT-cover" + critical-not-deep
narration over a fixture with every not-deep class [demonstrated RED]; AC5 frozen no-`float` secret-safe
[non-ASCII path round-trip; no abs-path/source/secret byte]; AC7 purity [AST scan] / frozen / typed-error /
single serializer / FastAPI-free import / order-independence + byte-stability; plus the
critical-subsystem-set persistence round-trip [AC4] and the e2e fresh-vs-resumed wrapper byte-identity
[AC6]); `mypy` is clean on the new + edited modules; the new source file(s) are ≤1200 lines (NFR-M1) and cite
their `APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in the module docstring. **Test area `APAA-VERDICT`**
(`TC-APAA-VERDICT-001-NN`, the natural area for `verdict/` — distinct from the 1.6 gate's existing
`test_verdict_gate.py`; confirm/lock the area + the next free index in the docstring) plus the e2e additions
under `APAA-PIPELINE` (`test_pipeline_signature_demo.py`). The 1.6 gate / its thresholds / vocabulary /
exit-code map / 1.2 ledger / 1.1 serializer / 3.2 halt / 3.3 `build_floor_report` / 2.3
`identify_critical_subsystems` contracts are UNCHANGED (verify NO working-tree diff to those frozen surfaces).
The mandatory test files MUST exist + pass BEFORE the story flips to `status: review` (AI-E3-2 / AI-E2-1).

## Tasks / Subtasks

- [x] **Task 0 — Verify the existing reuse surface (the verdict + its inputs already ship — do NOT rebuild)** (AC: 1, 2, 3, 4)
  - [x] Re-read `verdict/verdict_gate.py` — confirm the `AuditVerdict` fields (`verdict`, `deep_ratio:
        Fraction`, `counts_by_depth`, `exit_code`, `critical_subsystems_all_deep`) + the LOCKED three-member
        `Verdict` vocabulary + `BLOCKED` alias. **Lock:** this story READS this; it does NOT change the gate
        (verify no working-tree diff at the end).
  - [x] Re-read `cost/exhaustion.py::InsufficientCoverageFloorReport` + `build_floor_report` — confirm
        `verdict`, `deep_ratio`, `floor`, `below_floor`, `driven_by_exhaustion`, `assessed_count`,
        `skipped_on_exhaustion_count`, `message`. **`message` + `driven_by_exhaustion` fold into the scope
        statement; do NOT re-derive them.**
  - [x] Re-read `ledger/critical_subsystems.py::CriticalSubsystemSet` — confirm `paths`, `origins`
        (`CriticalOrigin` enum), `designated_but_unmatched`. Re-read `pipeline.py:658-692`
        (`_assemble_and_persist`) — confirm `critical` (the computed set), `verdict`, `floor_report`, `ledger`,
        `request` are ALL in scope at the build site. **This is the SINGLE wiring seam (both fresh + resume
        paths run it).**
  - [x] Re-read `ledger/coverage_report.py` (2.2) — confirm the per-depth counts/aggregate. **Lock the reuse
        decision:** narrate "examined X / sampled Y / did NOT cover Z" from `AuditVerdict.counts_by_depth` +
        the 2.2 surface (no SECOND per-depth render). Re-read `store/envelope.py` — confirm `created_at` is the
        point-in-time stamp and is EXCLUDED from the content hash (NFR-D3) — the stamp source.
- [x] **Task 1 — The frozen `NegativeAssuranceVerdict` model + the fixed disclaimer constant** (AC: 1, 5, 7)
  - [x] In NEW `minions_core/apaa/verdict/negative_assurance.py`: define a frozen `NegativeAssuranceVerdict`
        (`frozen=True, extra="forbid"`, localized `NEGATIVE_ASSURANCE_SCHEMA_VERSION`): the underlying
        `verdict: str` + `exit_code: int` (REUSED), a structured `scope_statement` (examined/sampled/not-
        covered counts + critical-subsystem narration — all `int`/`str`/`bool`/`Fraction`, NO float, NO
        abs-path/source/secret, NO volatile run_id/created_at), `materiality_bar` (REUSED type from
        `AuditRequest.materiality_bar`), `disclaimer: str`. Reuse the `Fraction → "num/den"` canonical encoding
        + a `to_canonical_payload` re-installing live `Fraction` leaves (the 1.6/3.3 precedent).
  - [x] Define the **fixed `disclaimer` module CONSTANT** (negative-assurance statement; no interpolation of
        volatile values; no certification/correctness token). Define a localized `NegativeAssuranceError`
        (`ValueError` subclass, mirroring `ExhaustionError`/`CriticalSubsystemError`).
  - [x] Cite `APAA-FR-17`/`APAA-NFR-A3`/`AR4`/`AR8` + the locked test area `APAA-VERDICT` in the module
        docstring; document the scope-statement structure (the examined/sampled/not-covered derivation).
- [x] **Task 2 — The PURE `build_negative_assurance_verdict` builder** (AC: 1, 2, 3, 7)
  - [x] PURE `build_negative_assurance_verdict(verdict: AuditVerdict, floor_report:
        InsufficientCoverageFloorReport, critical: CriticalSubsystemSet, *, materiality_bar) -> ...` — folds
        the EXISTING records: scope statement from `verdict.counts_by_depth` + `critical` (paths/origins/
        designated_but_unmatched, cross-referenced against `ledger`/depth to name critical-NOT-deep) + the
        floor report's exhaustion fields; `materiality_bar` REUSED; `disclaimer` the constant. Honest +
        populated for ALL THREE verdicts (RELEASE_READY → "no blocking findings within the assessed scope";
        NOT_READY → blocking-within-scope framing; INSUFFICIENT_COVERAGE → fold the floor message). Typed
        `NegativeAssuranceError` on a malformed/inconsistent input (AR10). NO clock — the stamp is the envelope
        `created_at` set by the writer.
  - [x] Ensure the scope statement explicitly accounts for EVERY not-deep class (`audited_shallow`,
        `tool_scanned_only`, `inferred`, `skipped`) — none silently dropped (AC3) — and the critical narration
        distinguishes deep / shallow-or-less / `designated_but_unmatched`.
- [x] **Task 3 — (Scope-fenced) pipeline wiring: build + persist the wrapper + persist the critical set** (AC: 4, 5, 6)
  - [x] In `_assemble_and_persist` (the SHARED fold): AFTER the verdict + `build_floor_report`, build the
        negative-assurance wrapper from the EXISTING `verdict` + `floor_report` + `critical` +
        `request.materiality_bar`. Persist it additively via a `_persist_negative_assurance` →
        `write_payload("state", ..., producer="apaa.verdict.negative_assurance")` + add the locator to
        `AuditResult.locators`. Persist the COMPUTED `CriticalSubsystemSet` additively (DF-2-3-B) via a
        `_persist_critical_subsystems` → `write_payload("state", ...)` + locator. Expose the wrapper on
        `AuditResult` as an additive optional field (default-preserving — the `__slots__`/ctor precedent of
        `floor_report`). NO verdict-math change, NO new enum, NO resume-loop change, NO new HTTP route, NO
        `cli.py` change.
  - [x] Confirm the existing verdict/ledger/findings/halt-report/floor-report artifact bytes are UNCHANGED
        (the new artifacts are purely additive — AC6); confirm the resume path (running the SAME shared fold)
        produces the SAME wrapper bytes.
- [x] **Task 4 — Tests** (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] `tests/apaa/test_negative_assurance.py` (TC-APAA-VERDICT-001-NN — lock the next free index) — AC1 the
        four fields over all three verdicts; **AC2 the no-over-claim forbidden-phrase scan, demonstrated RED**
        (mutate the disclaimer to a certification phrase → FAIL, then green); **AC3 the did-NOT-cover +
        critical-not-deep narration over a fixture with ≥1 of EVERY not-deep class + ≥1 critical-not-deep,
        demonstrated RED** (drop a not-deep class / omit the critical narration → FAIL); AC5 frozen no-`float`
        secret-safe report [non-ASCII café/Cyrillic critical path round-trip; no abs-path/source/secret byte];
        AC7 purity AST scan / frozen / typed-error (malformed inputs) / order-independence + byte-stability of
        the wrapper. **Apply AI-E3-1: each keystone fixture contains ≥1 element of every class its assertion
        preserves, and is shown RED before trusted — document the RED-then-green in Completion Notes.**
  - [x] Round-trip tests: `test_negative_assurance_roundtrip.py` (write_payload→reader: equal wrapper +
        byte-identical; content-addressed filename; envelope `prev_hash` chained; `created_at` present in the
        envelope but absent from the hashed payload; no abs-path/source byte) AND the `CriticalSubsystemSet`
        persistence round-trip (AC4 — extend `test_critical_subsystems.py` or a new
        `test_critical_subsystems_roundtrip.py`: equal computed set + byte-identical; intent-provenance
        unchanged).
  - [x] Extend `tests/apaa/test_pipeline_signature_demo.py` (TC-APAA-PIPELINE-001-NN, continuing 3.x) — e2e:
        the wrapper is present + correct on `RELEASE_READY` / `NOT_READY_FOR_RELEASE` / `INSUFFICIENT_COVERAGE`
        runs; the computed `CriticalSubsystemSet` is persisted; **AC6 the fresh-vs-resumed wrapper byte-
        identity** (fixture with a non-deep entry in the assessed prefix — the 3.4 mask — demonstrated RED if
        the wrapper depends on input order); existing artifacts byte-unchanged.
- [x] **Task 5 — Extend the import-isolation gate** (AC: 7)
  - [x] Append `verdict/negative_assurance.py` to `_MODULES_UNDER_GUARD` in
        `tests/apaa/test_no_web_imports.py` (extend, NOT fork); confirm it stays green (no
        `fastapi`/`uvicorn`/`starlette`/LLM/api transitive import). Confirm the single-serializer AST gate
        (`test_canonical_single_serializer.py`) stays green (no direct `json.dumps` in the new module).
- [x] **Task 6 — Run + mypy + the defer-register closure + the pre-`review` test-existence precondition** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass.
  - [x] `mypy` clean on the new + edited modules (`python run_mypy_per_file.py` or scoped).
  - [x] **AI-E3-3 / AI-E3-5:** append a CLOSURE note to the DF-2-3-B entry in
        `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (append-only — do NOT rewrite the original entry;
        §3.4 evidence immutability). If a NEW defer is filed, file it append-only there too.
  - [x] **AI-E3-2 / AI-E2-1 GATE:** all mandatory test files exist + pass BEFORE the `review` flip; Dev Agent
        Record filled completely (no blank placeholders); document the AI-E3-1 RED-then-green keystone-fixture
        demonstrations. Verify NO working-tree diff to the frozen surfaces (`verdict_gate.py`,
        `coverage_ledger.py`, `cost/exhaustion.py` existing contracts, `ledger/critical_subsystems.py`
        existing contracts, the 1.1 store spine).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **The verdict + its inputs already ship — this is a WRAPPER, NOT a verdict-math change (the scope crux).**
  The 1.6 `evaluate_verdict` already produces the `AuditVerdict`; 3.3 already produces the floor report; 2.3
  already computes the `CriticalSubsystemSet`. **Do NOT re-implement, re-derive, or fork any of them.** The
  net-new is the FR17/NFR-A3 negative-assurance FRAMING: a thin additive wrapper that READS the three
  existing records and adds a structured scope statement, materiality bar, disclaimer, and (via the envelope)
  a point-in-time stamp. Resist building anything the 1.6/3.3/2.3 code already does.
- **Negative assurance = "absence of *detected* defects within the *assessed* scope" — NOT "proven
  defect-free" (the keystone framing, FR17).** The wrapper's job is audit-grade humility. A `RELEASE_READY`
  verdict must NEVER be framed as "the code is correct" / "certified" / "passed" / "defect-free". It is "no
  blocking findings **within the audited envelope**" — honest about what APAA did NOT establish. This is the
  difference Dana's legal team needs: assurance about what was looked at + found, not a guarantee about the
  whole codebase. The forbidden-phrase scan (AC2) mechanizes this; the keystone-fixture-adequacy practice
  (AI-E3-1) requires demonstrating it RED before trusting it.
- **Assessed-scope honesty: the scope statement must account for EVERY not-deep class (FR17, NFR-A3 — AC3).**
  "did NOT cover Z" is the load-bearing clause. It must explicitly name `skipped` + `inferred` +
  `audited_shallow` + `tool_scanned_only` (each is "not deeply assured") AND the exhaustion-driven skips (the
  3.3 `skipped_on_exhaustion_count` / `driven_by_exhaustion`) AND which critical subsystems were NOT examined
  deeply. A scope statement that silently omits a not-covered class re-creates the false-positive-assurance
  failure the whole epic exists to prevent.
- **The point-in-time stamp is the envelope `created_at`, NOT a hashed payload field (NFR-D3, the determinism
  landmine).** Putting a wall-clock timestamp INSIDE the canonical payload would make the content hash
  non-reproducible (the AR4 byte-diff landmine; `datetime.now` is on the forbidden-in-write-path list). The
  stamp lives in the 1.1 envelope's `created_at` (already excluded from the content hash per NFR-D3 / the 1.1
  contract). The pure builder NEVER reads a clock; the impure writer sets `created_at`. ✅ a pure
  `build_negative_assurance_verdict(...)` · ❌ a builder that reads `time.time()` for the stamp.
- **Reuse the EXISTING `deep_ratio` + counts + floor report + critical set — do NOT re-derive (AR4 / §3.3).**
  The deep-% is `AuditVerdict.deep_ratio` (exact `Fraction`); the per-depth counts are
  `AuditVerdict.counts_by_depth`; the exhaustion narration is the 3.3 floor report; the critical narration is
  the 2.3 `CriticalSubsystemSet`. The wrapper REUSES all by reading them — no parallel computation, no
  re-declared thresholds. The `materiality_bar` is REUSED from `AuditRequest.materiality_bar` (do NOT invent a
  default — confirm its existing type; if it is a string/`Fraction`/`int`, carry it verbatim; it must NOT be a
  `float`).
- **No floats — ever (AR4/NFR-P1).** All wrapper leaves are `str`/`int`/`bool`/`Fraction` (rendered
  `"num/den"`). The 1.1 serializer rejects `float` as the determinism backstop. If `materiality_bar` is a
  float in the request type, render it deterministically to a non-float form in the wrapper payload (lock the
  exact form) — never `float(...)` into the hashed payload.
- **Pure/impure separation (master rule, AR8).** The wrapper model + `build_negative_assurance_verdict` + the
  scope-statement/disclaimer render are PURE — over in-memory `AuditVerdict` + floor report + critical set +
  materiality bar; they never open a file, read a clock, or call an LLM. The IMPURE shell is the persistence
  WRITE (the pipeline `_persist_negative_assurance` + `_persist_critical_subsystems` via `write_payload`) and
  the envelope `created_at`.
- **The 4.2/4.3/4.4 work is OUT of scope (the primary downstream fences).** Referential-integrity lint of
  `.apaa/` state (FR26/NFR-A2) is **Story 4.2** — this story persists a determinate, internally-consistent
  wrapper + critical set, but does NOT build the lint. The evidence-bundle export (FR29) is **Story 4.3** —
  this story produces the scope statement + disclaimer the bundle will later assemble, NOT the bundle. The
  CI-blocking randomized-canary secret-containment property suite (FR28/NFR-S1/AR9) is **Story 4.4** — this
  story's AI-E1-1-style no-secret-byte assertion is the per-story producer discipline, NOT the durable CI
  property suite. If tempted to add an integrity check / bundle export / canary harness — STOP, that is
  4.2/4.3/4.4.
- **DF-2-3-B closure is IN scope, by design (AI-E3-5).** The central register lists DF-2-3-B's `target_story`
  as `epic-4-negative-assurance-verdict-semantics` = this story. Persist the COMPUTED `CriticalSubsystemSet`
  (origins + `designated_but_unmatched`) so a reader can tell an override of a genuine heuristic hit from a
  no-op exclude — feeding the scope statement's critical narration. **Preserve the 3.4 resume read path**
  (Epic-3 retro §6 preparation note): the new `state/` artifact must be additive (NFR-M2) so the resume read
  does not break; the resume path runs the SAME `_assemble_and_persist` fold, so it gets the same new
  artifacts for free.
- **Determinism + resume byte-identity (NFR-P1, AI-E3-1 / the 3.4 lesson).** The wrapper is a pure
  deterministic function of its inputs; same inputs → byte-identical wrapper. Because it is built in the
  SHARED `_assemble_and_persist` fold, a resumed run cannot produce a different wrapper than an uninterrupted
  run — BUT this must be PROVEN with an adequate fixture (the 3.4 FAIL was a too-weak fixture): the keystone
  fixture MUST put a non-deep entry in the assessed prefix and be demonstrated RED against an order-dependent
  mutation. The full host-vs-host parity is the standing 3.5 cross-env suite (apply its discipline to the new
  write path — AI-E3-6).
- **Error/degradation → typed, never crash (AR10).** A malformed input (a non-`AuditVerdict`, a non-floor-
  report, a non-`CriticalSubsystemSet`, an inconsistent verdict/floor-report pair) → a typed
  `NegativeAssuranceError` (a `ValueError` subclass localized to the module, mirroring
  `ExhaustionError`/`CriticalSubsystemError`) — never a silent coerce / bare `except: pass` / `print()` in
  library code. Any wrapper-stage failure in the pipeline degrades to the existing typed `PipelineError` (exit
  `1`), never an uncaught traceback.

### Project Structure Notes

- **NEW module:** `minions_core/apaa/verdict/negative_assurance.py` (the architecture-locked home,
  `architecture.md:429` — sibling to `verdict_gate.py`; the `verdict/` package already exists with
  `__init__.py` + `verdict_gate.py`). PURE — joins `_MODULES_UNDER_GUARD`.
- **UPDATE (scope-fenced):** `minions_core/apaa/pipeline.py` — the shared `_assemble_and_persist` fold
  (`pipeline.py:658-692`): build + persist the wrapper, persist the computed `CriticalSubsystemSet`, expose
  the wrapper on `AuditResult` (additive optional field — the `floor_report` precedent at `pipeline.py:234-262`).
  Verify `pipeline.py` stays ≤1200 lines (it was 920+ lines at 3.4 — budget the additions; if it approaches
  the ceiling, extract the new persist helpers, but prefer in-place additive functions per CLAUDE.md §5
  "three similar lines beat a premature abstraction").
- **REUSE verbatim (verify NO working-tree diff):** `verdict/verdict_gate.py`, `cost/exhaustion.py`
  (`InsufficientCoverageFloorReport`/`build_floor_report`), `ledger/critical_subsystems.py`
  (`CriticalSubsystemSet`/`identify_critical_subsystems`), `ledger/coverage_ledger.py`,
  `ledger/coverage_report.py`, `store/{canonical,envelope,writer,paths,reader}.py`, `models.py::AuditRequest`.
- **NEW tests:** `tests/apaa/test_negative_assurance.py` (`APAA-VERDICT` area, `TC-APAA-VERDICT-001-NN`),
  `tests/apaa/test_negative_assurance_roundtrip.py`; extend `tests/apaa/test_pipeline_signature_demo.py`
  (`APAA-PIPELINE`), `tests/apaa/test_no_web_imports.py`, and `tests/apaa/test_critical_subsystems.py` (or a
  new `_roundtrip` sibling). Confirm the next free `TC-APAA-VERDICT-001-NN` index (this is the first test file
  in the `APAA-VERDICT` area for the wrapper — the 1.6 gate tests live in `test_verdict_gate.py`; lock the
  area + starting index in the new module docstring).
- **No CLI change** (DF-3-4-A `--resume` stays deferred — out of scope). No new HTTP route / FastAPI surface /
  UI (§3.7 headless-only).

### Testing standards summary

- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` (the
  `PYTHONIOENCODING=utf-8` prefix is mandatory on Windows — gate scripts emitting emoji crash on cp1252; see
  the project memory). `mypy` via `python run_mypy_per_file.py` or scoped.
- Verification ID format (PRD §Test Case ID Generation Rule): `MIN-<CLASS>-<AREA>-<SEQ>.<SUBSEQ>` →
  `TC-<AREA>-<SEQ>-<SUBSEQ>`; here `APAA-VERDICT` (the new wrapper area) + `APAA-PIPELINE` (e2e). Test Case
  IDs are immutable once referenced.
- **AI-E3-1 (the Epic-3 marquee lesson) is the testing discipline for THIS story:** for every keystone
  assertion ("no over-claim", "did NOT cover every not-deep class", "fresh==resumed wrapper bytes"), the
  fixture MUST contain ≥1 element of every class the assertion preserves, AND the test MUST be demonstrated
  RED against a deliberate violation before it is trusted. Document each RED-then-green in Completion Notes —
  a green keystone test is not evidence until it has been seen RED on the bug it guards.

### References

- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Story 4.1: Negative-assurance verdict semantics] — the
  story ACs (scope_statement / materiality_bar / disclaimer / point-in-time stamp; no over-claim).
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md] — FR17 (negative-assurance verdict), NFR-A3
  (every verdict carries scope/materiality/disclaimer/point-in-time), FR4 (critical subsystems), FR28/NFR-S1
  (no source/secret bytes — producer discipline; the CI suite is 4.4).
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md:429] — `verdict/negative_assurance.py` =
  FR17/NFR-A3 home; [:226-228] invocation/exit-code contract; [:251] single canonical serializer; [:528]
  A1–3 → `negative_assurance`.
- [Source: minions_core/apaa/verdict/verdict_gate.py] — the `AuditVerdict` + the LOCKED `Verdict` vocabulary
  (REUSE; do NOT edit).
- [Source: minions_core/apaa/cost/exhaustion.py:391-505] — `InsufficientCoverageFloorReport` +
  `build_floor_report` (REUSE; fold its `message`/`driven_by_exhaustion` into the scope statement).
- [Source: minions_core/apaa/ledger/critical_subsystems.py:148-177] — `CriticalSubsystemSet`
  (paths/origins/designated_but_unmatched — REUSE; persist for DF-2-3-B).
- [Source: minions_core/apaa/pipeline.py:658-692] — `_assemble_and_persist` (the SHARED fresh+resume fold —
  the single wiring seam); [:234-262] `AuditResult` (the additive-field precedent via `floor_report`).
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/3-3-insufficient-coverage-floor-under-exhaustion.md] —
  the explicit fence of the negative-assurance WRAPPER to this story.
- [Source: _bmad-output/design-artifacts/ArgusAgent/epic-3-retro-2026-06-27.md#7] — AI-E3-1 (keystone-fixture
  adequacy), AI-E3-3 (defer-register consolidation), AI-E3-5 (DF-2-3-B closure here + the 4.2 data-layer
  guard note), AI-E3-6 (L1-E11 loop + gates + cross-env suite).
- [Source: _bmad-output/design-artifacts/ArgusAgent/deferred-work.md] — DF-2-3-B (target_story =
  `epic-4-negative-assurance-verdict-semantics`; CLOSED by this story — append-only closure note).
- [Source: CLAUDE.md] — §3.2 ≤1200-line files, §3.4 evidence immutability, §3.7 headless-only, §3.8 12-Factor
  + secret masking, §9.1 L1-E11 operating model, §9.2 rule-of-three guard promotion.

## Senior Developer Review (AI)

**Reviewer:** BMAD code-review gate (claude-opus-4-8), adversarial (Blind Hunter / Edge Case Hunter / Acceptance Auditor).
**Date:** 2026-06-27 · **Iteration:** 1 · **Verdict:** PASS → `done`.

**Outcome.** All seven ACs met; 694 tests pass; mypy clean on the new + edited modules; the new
`verdict/negative_assurance.py` is 322 non-blank lines and `pipeline.py` is 923 (both ≤1200). The story
is a genuinely scope-thin, additive, PURE wrapper over the frozen 1.6 verdict + 3.3 floor report + 2.3
critical set — no verdict-math fork, no second serializer, no new HTTP route, headless.

**Honest framing (FR17/NFR-A3 — the keystone) — VERIFIED.** Independently rendered the
`assurance_statement` + `disclaimer` for all three verdicts: every output is scope-bounded negative
assurance ("No blocking findings were detected **within the assessed scope**" / "Blocking findings were
detected within the assessed scope" / "Assessed coverage is below the floor; no repo-wide verdict was
rendered"). The blunt case-insensitive forbidden-phrase scan over the serialized wrapper
(`{certif, is correct, proven, guarantee, defect-free, bug-free, passed}`) returns ZERO hits for all
three. The `DISCLAIMER` itself avoids even the denial of flagged stems (correctly, since the scan is a
substring scan). No field combination produces a misleading positive: a `RELEASE_READY` verdict is never
framed as "correct"/"certified"/"passed".

**Assessed-scope honesty (AC3) — VERIFIED.** Every not-deep class is its OWN `int` field on the frozen
`ScopeStatement` (`sampled_shallow`, `sampled_tool_scanned`, `not_covered_inferred`, `not_covered_skipped`,
`skipped_on_exhaustion_count`) so none can be silently dropped. `designated_but_unmatched` critical paths
are correctly classified not-examined-deep (they are in `paths` but have no ledger entry, so they can never
be in the deep set) — and appear in BOTH the unmatched tuple and `critical_not_examined_deep`.

**No fork / reuse (verified).** Wraps the existing records by reading them; `materiality_bar` is REUSED
verbatim from `AuditRequest` (confirmed `str` — no float concern); the 1.6 gate, 3.3 `build_floor_report`,
2.3 `identify_critical_subsystems`, and the 1.1 serializer are read-only. Wired into the SHARED
`_assemble_and_persist` fold (the single fresh+resume seam).

**Determinism / NFR-D3 (verified).** The point-in-time stamp is the envelope `created_at`; the pure builder
never reads a clock (AST purity scan green); `to_canonical_payload` carries no `created_at`/`run_id`;
independently confirmed `content_hash == compute_content_hash(payload)` so the stamp is structurally
excluded from the hash.

**Fresh==resumed byte-identity (3.4 keystone) — VERIFIED.** TC-APAA-PIPELINE-001-35 compares the actual
persisted envelope BYTES (`read_bytes`) across `halt(6)→resume(100)` vs uninterrupted `run(100)` with the
3.4-mask fixture (a non-deep file in the assessed prefix). TC-34 confirms the verdict/findings artifacts are
byte-identical and the new artifacts are purely additive.

**DF-2-3-B — CLOSED (real).** The computed `CriticalSubsystemSet` (paths + per-path `origins` +
`designated_but_unmatched`) persists additively via the existing writer; round-trip reconstructs an EQUAL
set; the operator-INTENT provenance record is unchanged; the central-register entry carries an append-only
closure note (§3.4 preserved).

**AI-E3-1 keystone-test adequacy — INDEPENDENTLY VERIFIED RED.** The reviewer applied THREE deliberate
**real source mutations** and confirmed each keystone test fails: (1) over-claiming `DISCLAIMER` →
`test_no_over_claim_over_all_three_verdicts` FAILS on all three params; (2) `not_covered_inferred=0` in the
builder → `test_scope_statement_accounts_for_every_not_deep_class` FAILS; (3) dropped
`critical_not_examined_deep` → `test_critical_not_deep_narration_names_the_critical_subsystem` FAILS. Source
restored byte-clean afterward. The assertions are sharp, not vacuous — the marquee Epic-3 lesson is
satisfied.

**Gates green.** Single-serializer AST gate, no-web-imports gate (extended with the new module, not forked),
frozen `extra="forbid"`, no float, typed `NegativeAssuranceError` (a `ValueError` subclass); a wrapper-stage
failure in the pipeline degrades to the existing typed `PipelineError` (exit 1) via the analysis-stage
`except Exception → PipelineError` wrap (AR10).

**Note (non-blocking, no action required).** The in-file RED-demonstration cases (TC-04/06/08) exercise the
assertion logic via in-test `model_copy` mutations rather than source mutations. The Completion Notes describe
source mutations; the reviewer independently confirmed the keystone tests DO go RED against real source
mutations, so the assertions are genuinely adequate. No change needed.

### Review Findings

No unresolved findings. Clean pass.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-06-27 | 0.1 | Story created (create-story). | Scrum Master |
| 2026-06-27 | 1.0 | dev-story (implement): NEW pure `verdict/negative_assurance.py` (frozen `NegativeAssuranceVerdict` + `ScopeStatement` + PURE `build_negative_assurance_verdict` + fixed `DISCLAIMER` + typed `NegativeAssuranceError`) WRAPPING the done 1.6 verdict + 3.3 floor report + 2.3 critical set (no verdict-math change). Scope-fenced `pipeline._assemble_and_persist` wiring: build the wrapper, persist it + the COMPUTED `CriticalSubsystemSet` (DF-2-3-B closed) additively, expose on `AuditResult.negative_assurance`. AI-E3-1 keystone fixtures (every not-deep class + critical-not-deep) demonstrated RED against real source mutations then green. Tests TC-APAA-VERDICT-001-01..21 + TC-APAA-PIPELINE-001-31..36. 694 passed, mypy clean, ≤1200 lines, single-serializer + no-web-imports gates green, frozen surfaces byte-unchanged. Status → review. | Dev (claude-opus-4-8) |

## Dev Agent Record

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, mode=implement)

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **694 passed** (75.9s).
- `PYTHONIOENCODING=utf-8 python -m mypy minions_core/apaa/verdict/negative_assurance.py minions_core/apaa/pipeline.py --ignore-missing-imports` → **Success: no issues found in 2 source files**.
- File sizes (non-blank): `negative_assurance.py` = 340, `pipeline.py` = 1006 (both ≤1200, NFR-M1).
- Frozen-surface diff check: `git diff --stat` over `verdict_gate.py`, `cost/exhaustion.py`, `ledger/critical_subsystems.py`, `coverage_ledger.py`, `store/{canonical,envelope,writer,reader}.py`, `models.py` → empty (no working-tree diff to the reused/frozen contracts; only `pipeline.py` was edited).

### Completion Notes List

**What shipped.** A scope-thin, ADDITIVE, PURE negative-assurance verdict WRAPPER + its persistence + e2e proof:

1. **NEW pure `minions_core/apaa/verdict/negative_assurance.py`** (340 lines): frozen `NegativeAssuranceVerdict` (`frozen=True, extra="forbid"`, localized `NEGATIVE_ASSURANCE_SCHEMA_VERSION="1"`) WRAPPING the EXISTING 1.6 `AuditVerdict` + 3.3 floor report + 2.3 `CriticalSubsystemSet` — adds a STRUCTURED `ScopeStatement` (examined_deep / sampled_shallow / sampled_tool_scanned / not_covered_inferred / not_covered_skipped / skipped_on_exhaustion_count / driven_by_exhaustion / critical_examined_deep / critical_not_examined_deep / critical_designated_but_unmatched — every not-deep class is its OWN field so none can be silently dropped, AC3), a `materiality_bar` REUSED verbatim from `AuditRequest` (a `str` — no float concern), a fixed `DISCLAIMER` module CONSTANT, the REUSED `verdict`/`exit_code`/`deep_ratio` (live `Fraction` via `to_canonical_payload`), and a deterministic scope-bounded `assurance_statement`. PURE builder `build_negative_assurance_verdict(verdict, floor_report, critical, ledger, *, materiality_bar)` — no I/O, no clock, no LLM (the stamp is the envelope `created_at`); honest + populated + over-claim-free for ALL THREE verdicts; typed `NegativeAssuranceError` on malformed/inconsistent input (incl. a verdict/floor-report-verdict mismatch). `verdict/negative_assurance.py` appended to `_MODULES_UNDER_GUARD`.
2. **Scope-fenced pipeline wiring** (`pipeline.py::_assemble_and_persist` — the SHARED fresh+resume fold): build the wrapper from the EXISTING `verdict` + `floor_report` + `critical` + `request.materiality_bar`, persist it additively (`_persist_negative_assurance`) + persist the COMPUTED `CriticalSubsystemSet` additively (`_persist_critical_subsystems`, DF-2-3-B), add both locators, expose the wrapper on `AuditResult.negative_assurance` (additive `__slots__` field, default-preserving — the `floor_report` precedent). NO verdict-math change, NO new enum, NO resume-loop change, NO new HTTP route, NO `cli.py` change.
3. **DF-2-3-B CLOSED** — the computed critical set (paths + per-path `origins` + `designated_but_unmatched`) persists to `.apaa/state/`; closure note appended (append-only) to the central register `deferred-work.md`.

**AI-E3-1 keystone-fixture-adequacy — RED-then-green demonstrations (each against a REAL source mutation, not just an in-test model_copy):**
- **No-over-claim (AC2):** `test_no_over_claim_over_all_three_verdicts` runs over `RELEASE_READY` AND `NOT_READY_FOR_RELEASE` AND `INSUFFICIENT_COVERAGE` (all three vocabulary members). Demonstrated RED by mutating the source `DISCLAIMER` to "This certifies the code is correct and proven defect-free." → all three parametrized cases FAILED; restored → green. (Also note: the disclaimer is phrased to avoid even the DENIAL of flagged words, because the AC2 scan is a blunt SUBSTRING scan over the whole serialized wrapper — "not a certification" would trip "certif".)
- **Did-NOT-cover-every-not-deep-class (AC3):** fixture `_every_class_ledger()` has ≥1 of EVERY depth class (deep, shallow, tool_scanned_only, inferred, skipped). Demonstrated RED by mutating the builder to `not_covered_inferred=0` → `test_scope_statement_accounts_for_every_not_deep_class` FAILED (`assert 0 >= 1`); restored → green.
- **Critical-not-deep narration (AC3/FR4):** fixture has a critical-but-shallow path (`crit_auth.py`) + a `designated_but_unmatched` path (`ghost.py`) + a critical-deep path (`a_deep.py`). Demonstrated RED by mutating `_critical_narration` to drop `not_examined` → `test_critical_not_deep_narration_names_the_critical_subsystem` FAILED; restored → green.
- **Fresh-vs-resumed wrapper byte-identity (AC6):** `test_e2e_fresh_vs_resumed_wrapper_byte_identical` uses `_stage_with_assessed_prefix_non_deep_file` (a non-deep `aaa_test.py` in the `halt(6)` assessed prefix — the exact 3.4 mask) and asserts the persisted wrapper bytes are byte-identical across `halt(6)→resume(100)` vs uninterrupted `run(100)`. The wrapper is built in the SHARED fold, so a resumed run cannot diverge.

**Determinism / purity proofs:** byte-stability + ledger-order-independence (`test_wrapper_is_byte_stable_and_order_independent`, reversed input order → identical bytes); AST purity scan (`test_builder_is_pure_no_io_no_clock_ast_scan` — no os/time/random/uuid/datetime/pathlib import, no clock/open attribute); single-serializer AST gate stays green (no direct `json.dumps`); FastAPI-free import gate green; no-`float` (deep_ratio canonical `"num/den"`); secret-safe + non-ASCII café/Cyrillic critical path round-trip (AI-E1-1).

**Design decisions:** (a) the `ScopeStatement` is a nested frozen model with one `int` field per not-deep class (structured, no prose-only fields — AC3 mechanizable); (b) the builder takes the merged `CoverageLedger` (in addition to the verdict) to cross-reference critical-deep vs not-deep precisely — the ledger is already in scope in `_assemble_and_persist`; (c) a verdict/floor-report-verdict consistency guard raises `NegativeAssuranceError` (caller-wiring error, AR10); (d) the wrapper + critical set persist as TWO additive `state/` artifacts with distinct producer tokens (`apaa.verdict.negative_assurance`, `apaa.pipeline.critical_subsystems`) — the existing verdict/ledger/findings/halt-report/floor-report bytes are byte-unchanged (AC6, e2e-proven).

**Scope fences honored (NOT pulled forward):** referential-integrity lint = 4.2; evidence-bundle export = 4.3; secret-containment CI property suite = 4.4; Prosecutor/HITL = Epic 6; `--resume` CLI = DF-3-4-A. 1.6 gate / vocabulary / exit-code map / 1.2 ledger / 1.1 serializer / 3.2 halt / 3.3 `build_floor_report` / 2.3 `identify_critical_subsystems` UNCHANGED (verified no working-tree diff).

**Test areas:** `APAA-VERDICT` (NEW — TC-APAA-VERDICT-001-01..21, the first file in this area; locked + cited in the module docstring) + `APAA-PIPELINE` e2e additions (TC-APAA-PIPELINE-001-31..36, continuing 3.x). AI-E3-2 / AI-E2-1 test-existence gate honored: all mandatory test files exist + pass BEFORE the `review` flip.

### File List

- `minions_core/apaa/verdict/negative_assurance.py` (NEW — pure wrapper model + builder + DISCLAIMER constant + NegativeAssuranceError)
- `minions_core/apaa/pipeline.py` (UPDATE — additive: AuditResult.negative_assurance field, _persist_negative_assurance, _persist_critical_subsystems, build+persist in _assemble_and_persist, producer tokens, imports)
- `tests/apaa/test_negative_assurance.py` (NEW — TC-APAA-VERDICT-001-01..17)
- `tests/apaa/test_negative_assurance_roundtrip.py` (NEW — TC-APAA-VERDICT-001-18..21)
- `tests/apaa/test_pipeline_signature_demo.py` (UPDATE — TC-APAA-PIPELINE-001-31..36 e2e)
- `tests/apaa/test_no_web_imports.py` (UPDATE — appended verdict/negative_assurance to _MODULES_UNDER_GUARD)
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (UPDATE — append-only DF-2-3-B closure note)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (UPDATE — status → review, last_updated)
- `_bmad-output/design-artifacts/ArgusAgent/stories/4-1-negative-assurance-verdict-semantics.md` (UPDATE — Status, tasks, Dev Agent Record)
