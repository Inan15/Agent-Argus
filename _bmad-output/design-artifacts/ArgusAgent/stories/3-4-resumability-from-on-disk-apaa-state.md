# Story 3.4: Resumability from on-disk `.apaa/` state

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As an operator who raised the budget after a budget-exhausted audit halted,
I want APAA to **resume from the `.apaa/` state already on disk** — re-load the prior coverage ledger, the
halt report, and the cost snapshot, **reuse the work it already did** (never re-auditing files it already
graded `audited_deep`), continue only the un-reached remainder, and **reach the SAME deterministic verdict
+ ledger an uninterrupted run of the equivalent budget would have reached** — and to **refuse to resume
from corrupted or tampered on-disk state** (a content-hash mismatch raises, never a silent wrong resume),
so that incremental auditing of a large repo is affordable AND a resumed answer is provably identical to
the never-interrupted answer — the FOURTH story of Epic 3, wiring the 3-2 persisted halt seam (the partial
ledger + `HaltReport` snapshot in `.apaa/state/`) and the 1-3 PURE reader (the tamper-guarded
deserialize/validate primitive) into a deterministic resume loop (FR31 / NFR-R2).

## Story Context

This is **Story 4 of Epic 3** (Honest Degradation & Cost Governance, Tier-A; epic-3 is already
`in-progress` from Stories 3.1 + 3.2 + 3.3, all `done`). It is the **resume-from-disk
restore-and-continue** story. Stories 3.1/3.2/3.3 built everything a resume reads FROM, and Story 1.3 built
the pure read primitive a resume reads WITH — **this story is the deterministic resume orchestration that
joins them**, and the proof that a resumed run does not change the answer:

- **Story 1.3 (done) built the PURE resumability READ primitive.** `store/reader.py::ApaaStoreReader` is
  ALREADY documented (its module docstring) as "the resumability seam": `read_envelope` /
  `read_ledger` / `read_recording` over a contained `.apaa/` tree, each one (1) containment-checks the
  locator via `ApaaStorePaths`, (2) reads the bytes (`FileNotFoundError` on missing), (3) `canonical.loads`
  (wrapping non-UTF-8 / non-JSON as `CanonicalSerializationError`), (4) validates against the frozen
  Pydantic v2 model (`ValidationError` on a bad shape / unknown field — `extra="forbid"`), and (5)
  reconstructs an EQUAL model that re-serializes byte-identically. **Crucially it ALREADY implements the
  tamper guard** AI-E1-1 demands: `read_envelope(verify_hash=True)` re-computes the envelope
  `content_hash` over the loaded payload and raises the typed `StoreIntegrityError` on a mismatch. **This
  story READS WITH this primitive — it does NOT build a second reader, a second deserializer, or a second
  tamper check.**
- **Story 1.1 (done) built the prev-hash-chained envelope.** Every `.apaa/` artifact is wrapped in a
  content-hashed, schema-versioned `Envelope` (`store/envelope.py`); the `content_hash` covers the
  canonical payload only (excludes volatile `run_id`/`created_at` — NFR-D3). The resume reads these
  envelopes through the 1.3 reader; the tamper guard is the envelope hash re-verification.
- **Story 2.4 (done) built the partition assignments.** The bounded-unit `PartitionPlan` +
  per-unit `work_manifest`s persist to `.apaa/assignments/<partition_id>.json` (NFR-S4 permission
  boundary). A resume MAY re-load the plan snapshot from `state/` to re-derive the same audit units (the
  partition plan is a deterministic function of the same repo@commit, so it can equally be RE-DERIVED — see
  Dev Notes "re-derive vs re-load").
- **Story 3.1 (done) built the cost snapshot.** `cost/budget_governor.py` folds the V1 deterministic
  zero-token cost proxy into a `CostLedger` (`total_credits: int`, `ceiling_credits: int | None`,
  `ceiling_reached: bool`, the NFR-C1 `baseline_ratio` Fraction) persisted to `state/` (the 3-1
  `_persist_cost_ledger`). A resume reads the accumulated spend to continue accounting against the RAISED
  budget.
- **Story 3.2 (done) built — and PERSISTED — the resume seam itself.** The pipeline ALREADY: projects the
  deterministic per-file halt point (`_project_halt` → `project_halt_point`, reusing the 3-1
  `_coerce_breach` `>=`-hard-ceiling decision BY IMPORT), runs the detectors over only the ASSESSED files,
  grades the un-reached remainder `CoverageDepth.SKIPPED` via the EXISTING `grade_entry`, re-folds the
  PARTIAL ledger through the UNCHANGED 1.6 gate, builds the frozen `HaltReport`
  (`halted_on_exhaustion: bool`, `total_credits`/`ceiling_credits`, sorted `assessed_files` +
  `skipped_on_exhaustion_files`), and PERSISTS the halt report + the partial-ledger run-state + the cost
  snapshot to `.apaa/state/` content-addressed. **3.2 explicitly fenced the resume LOOP to THIS story** (3.2
  Story Context + AC5: *"this story PERSISTS the partial ledger + the halt/skipped record + the cost
  snapshot (the seam 3.4 reads); it does NOT build the restore-and-continue loop"*).
- **Story 3.3 (done) built the floor SEMANTICS.** The PURE `build_floor_report(verdict, halt_report)` reads
  the verdict + halt report and renders the honest "assessed X% deep; floor 20%" surface. It is purely
  additive (a derivable surface on `AuditResult`, not a persisted artifact). A resumed run that clears the
  floor renders a real release verdict; a resume that still lands below the floor renders
  `INSUFFICIENT_COVERAGE` exactly as 3.3 already decides — this story changes NEITHER.

**So everything a resume reads FROM is on disk after a 3-2 halt, and the reader to read it WITH is the 1-3
primitive.** What this story adds is **the deterministic resume orchestration + the keystone proof**: when
APAA is re-invoked on the SAME `repo + commit` whose `.apaa/state/` shows a prior halted run, it (a)
re-loads the prior coverage ledger + halt report + cost snapshot through the tamper-guarded 1-3 reader, (b)
reuses the prior `audited_deep` coverage (it does NOT re-run detectors over an already-`audited_deep`
file — the affordability win NFR-R2 demands), (c) continues auditing ONLY the prior
`skipped_on_exhaustion` remainder, bounded by the RAISED budget (re-projecting a fresh halt point over the
remaining units), (d) re-folds the merged ledger through the UNCHANGED 1.6 gate, and (e) is **proven
byte-identical** (final `.apaa/` verdict + ledger) to an uninterrupted run of the equivalent (raised)
budget. And it **refuses to resume from corrupted/tampered state** (the 1-3 `StoreIntegrityError` /
`CanonicalSerializationError` propagate → typed `PipelineError` / a localized resume error → exit 1 — never
a silent wrong resume).

**The classification of this story: a NEW pure resume-plan core + a scope-fenced impure resume entrypoint —
NOT a verify-and-lock.** Unlike 3.3 (where the floor math already shipped), the resume LOOP does NOT yet
exist: there is no code path that reads prior state and continues. The net-new is:
1. a PURE resume-plan function that, given the prior ledger (loaded) + the prior halt report (loaded) + the
   current `repo@commit` index + the RAISED `BudgetConfig`, computes (deterministically, no I/O) which
   files are ALREADY covered (`audited_deep` carried forward verbatim) and which remaining units are the
   resume target (re-projecting the halt over the remainder against the raised ceiling), and asserts the
   prior state is consistent with the current repo (the `audited_deep` paths exist in the current index — a
   commit-mismatch / divergent-tree resume is rejected, NOT silently mis-merged);
2. an impure resume ENTRYPOINT in `pipeline.py` (the restore-and-continue loop): load prior state via the
   1-3 reader (tamper-guarded), build the resume plan, run detectors ONLY over the resume target, merge the
   carried-forward coverage with the newly-audited coverage into the FULL ledger, re-fold through the
   UNCHANGED 1.6 gate, persist the resumed verdict/ledger/halt-report/cost-snapshot via the EXISTING store;
3. the **keystone byte-identity proof** — `resume(raised_budget)` after a `halt(small_budget)` produces a
   final `.apaa/` verdict + ledger BYTE-IDENTICAL to a single uninterrupted `run(raised_budget)`;
4. the **tamper-on-resume-raises proof** — a mutated on-disk payload (stale `content_hash`) or a
   non-UTF-8 / unparseable / unknown-field state file makes the resume RAISE a typed error (exit 1), never
   a silent / fabricated resume (AI-E1-1).

**Run the already-shipped scope check in spirit:** the read primitive (`ApaaStoreReader`, `read_ledger`,
`StoreIntegrityError`), the envelope chain (`Envelope`, `compute_content_hash`), the halt seam
(`HaltReport`, `project_halt_point`, `_coerce_breach`), and the verdict gate (`evaluate_verdict`) ALL
already exist in production — do NOT fork them; the resume orchestration COMPOSES them. The dev MUST resist
re-implementing the reader, the tamper check, the halt projection, or the verdict math.

**What FR31 IS in V1 — the deterministic restore-and-continue loop + the resume-reaches-identical-verdict
proof + tamper-on-resume.** The architecture (Decision F: *"filesystem-as-contract `.apaa/{state,...}`;
resumable + portable (FR31)"*; FR-cluster→location: *"Invocation & Resumability (FR30–32) | `cli.py`,
`pipeline.py`, `store/reader.py`"*; NFR validation: *"R1–2 (failure→finding, `store/reader` resume)"*) and
the epic (Story 3.4) lock this story to: (a) **resume from the recorded state, reusing prior coverage** —
re-invoke on the same `repo+commit`, re-load the recorded `.apaa/` state, do NOT re-audit already-
`audited_deep` files (NFR-R2 "no loss of prior coverage"); (b) **the resumed run completes to a final
`.apaa/` state identical to an uninterrupted run** of equivalent budget (no resume artifacts diverge — the
keystone: resume must NOT change the answer). **This story does NOT change the verdict math, thresholds,
exit-code mapping, the 1.6 gate, the 1.2 ledger, the 1.1 serializer/envelope, the 1.3 reader, the 3.1
cost core, the 3.2 halt mechanism, or the 3.3 floor report — all frozen/reused.**

**The Tier-A scope boundary — what is 3.4 vs the rest of Epic 3 + Epic 4/5.** This story is single-purpose:
the **deterministic resume-from-disk loop + the resume-reaches-identical-verdict proof + the
tamper-on-resume-raises guard**. Explicitly later/other stories MUST NOT be pulled forward:
- **Sequential byte-identical execution on the least-capable host (FR32 / NFR-P1) is Story 3.5** — the
  host-vs-host (sequential-vs-parallel-scheduler) byte-identity proof. THIS story's resume output MUST
  already be byte-deterministic (no clock/uuid/random; no float; sorted content-derived sets; the resume
  plan is a pure function of the loaded state + the current index + the raised config) so 3.5 inherits a
  determinate surface, and this story SHOULD ship a byte-stability + order-independence fixture on the
  resume plan; the full host-parity proof (and any parallel scheduler) is 3.5. Resume determinism (same
  inputs → same resumed answer) is THIS story; host-portability of that answer is 3.5.
- **The cache / content-addressed memoization (NFR-D1, the cross-run "same result without re-spending
  tokens" cache) is Epic 5** (`cache/key.py` + `cache/memo_store.py`). Resume (3.4) reuses prior coverage
  by re-loading the on-disk LEDGER (the work already recorded), NOT by a memoization-cache hit; the
  `.apaa/cache/` dir is a directory only in V1 (the memo LOGIC is Epic 5). Do NOT build a cache key, a memo
  store, or a cache-invalidation rule here. The distinction: resume = "continue an interrupted run from its
  persisted partial state"; memoization = "skip re-computing an identical closure across distinct runs".
- **Referential-integrity lint of on-disk state (FR26 / NFR-A2, the `.apaa/` no-dangling-references lint)
  is Story 4.2** (Tier B). This story re-VERIFIES the tamper guard (the envelope `content_hash`, via the
  1-3 reader) on the artifacts it loads to resume, and asserts the loaded state is consistent with the
  current repo (the carried-forward paths exist in the index); it does NOT build the full referential
  integrity lint (finding→ledger, decision→assignment, the whole prev-hash chain walk) — that is 4.2.
- **The negative-assurance verdict WRAPPER (FR17 / NFR-A3 — `scope_statement` / `materiality_bar` /
  `disclaimer` / point-in-time stamp) is Story 4.1.** A resumed verdict carries the SAME neutral 3.3 floor
  data; the scope-statement narration ("examined X, resumed to cover Z") is 4.1's to fold over — do NOT
  build the wrapper here.
- **The numeric `$X` ceiling default + full-repo budget sizing is Story 7.1** (OI3) — NOT here. This story
  exercises resume against an operator-set (or test-set) raised budget; it locks NO numeric default.
- **The LLM dispatch port / real LLM credit metering (Epic 6).** V1 cost is the deterministic zero-token
  work-unit proxy (3-1); the resume MECHANISM folds real credits into the SAME accountant when Epic 6
  lands. Do NOT wire the LLM port here.
- **2.3 critical-subsystem clause / Epic-6 Prosecutor / HITL escalation** — all out of scope.

**What already exists (REUSE verbatim, do NOT rebuild).** This story sits on the fully-built Epic-1/2 spine
+ the done 3-1/3-2/3-3 cost/halt/floor core:

- **`minions_core/apaa/store/reader.py` (Story 1.3, done — REUSE verbatim, do NOT edit; the resume READ
  primitive).** `ApaaStoreReader(repo_root)` with `read_bytes` / `read_envelope(verify_hash=True)` /
  `read_ledger` / `read_recording`, and the typed `StoreIntegrityError` (a `ValueError` subclass) raised on
  a `content_hash` re-verification mismatch. **This IS the tamper-on-resume guard AI-E1-1 demands — REUSE
  it; do NOT build a second tamper check.** A corrupt / non-UTF-8 / unparseable / unknown-field file
  surfaces as `CanonicalSerializationError` / `pydantic.ValidationError`; a missing file as
  `FileNotFoundError`; a path escape as `WorkspaceContainmentError`. The resume entrypoint CATCHES these
  typed errors and maps them to a typed resume failure (exit 1) — never a silent empty/fabricated resume.
- **`minions_core/apaa/store/envelope.py` (Story 1.1, done — REUSE).** `Envelope` (content-hashed,
  schema-versioned, `prev_hash`-chained), `compute_content_hash(payload)`. The resume reads envelopes
  through the 1-3 reader; the prev-hash chain is the integrity backbone (the full chain-walk lint is 4.2).
- **`minions_core/apaa/store/{canonical,paths,writer}.py` (Story 1.1 + 1.3, done — REUSE).** The single
  serializer (`canonical.dumps_bytes` / `canonical.loads`, rejects `float`, `Fraction → "num/den"`),
  `ApaaStorePaths` (the `is_relative_to` containment resolver — NFR-S5), `ApaaStoreWriter.write_payload(
  "state", ...)` (content-addressed). The resumed verdict/ledger/halt-report/cost-snapshot persist through
  this EXISTING shell — NO second serializer / writer / reader / path resolver.
- **`minions_core/apaa/ledger/coverage_ledger.py` (Story 1.2 + 2.1, done — REUSE verbatim, do NOT edit).**
  The closed `CoverageDepth` enum, frozen `CoverageLedgerEntry`, `CoverageLedger.build(entries)` (sorts by
  `file_path` — order-independent), `deep_count()` / `total()` / `counts_by_depth()`, the pure
  `grade_entry`. **The carried-forward coverage is re-loaded as the prior `CoverageLedger` (via
  `read_ledger`); the resume merges the prior `audited_deep` entries with the newly-audited remainder
  entries into a SINGLE `CoverageLedger.build(...)` — `build` re-sorts, so a merged ledger is
  order-independent (the SAME sorted ledger an uninterrupted run produces).** Do NOT add a new enum member;
  a still-unreached file after resume stays `SKIPPED`. Never fabricate an `audited_*` entry.
- **`minions_core/apaa/verdict/verdict_gate.py` (Story 1.6 + 2.3, done — REUSE verbatim, do NOT edit).**
  The PURE `evaluate_verdict(ledger, findings, *, critical_subsystems_all_deep=True) -> AuditVerdict` with
  the frozen thresholds / floor-wins precedence / FR8 exclusion / FR33 ordering / exit-code map (`0/2/3/1`).
  **The resumed (merged) ledger is re-folded through this UNCHANGED gate** — verify no working-tree diff to
  `verdict_gate.py`.
- **`minions_core/apaa/cost/exhaustion.py` (Story 3.2 + 3.3, done — REUSE verbatim, do NOT edit).** The
  PURE `project_halt_point(units, *, config) -> HaltProjection`, `would_breach`, the frozen `HaltProjection`
  (`halt_index`, `total_credits`, `ceiling_credits`, sorted `assessed_paths`/`skipped_paths`,
  `halted_on_exhaustion`), the frozen `HaltReport` (`halted_on_exhaustion`, `total_credits`,
  `ceiling_credits`, sorted `assessed_files`/`assessed_count`, sorted
  `skipped_on_exhaustion_files`/`skipped_on_exhaustion_count`, `HALT_SCHEMA_VERSION`,
  `to_canonical_payload`), `build_halt_report`, the `build_floor_report` (3.3), and the typed
  `ExhaustionError`. **The resume RE-PROJECTS a fresh halt over the REMAINING units against the RAISED
  ceiling** (a resume may itself halt again if the raised budget still does not cover the remainder — a
  second partial run, fully honest). REUSE `project_halt_point`; do NOT add a field to `HaltReport` unless
  genuinely required (prefer a NEW sibling resume-plan model — see Dev Notes).
- **`minions_core/apaa/cost/budget_governor.py` (Story 3.1, done — REUSE BY IMPORT, do NOT edit).**
  `BudgetConfig` (`ceiling_credits: int | None`), `budget_config_from_budget(budget)` (`0 → None`),
  `account_spend`, `CostLedger`, `_coerce_breach`. The resume reads the prior accumulated spend from the
  persisted `CostLedger` snapshot and continues accounting against the RAISED ceiling.
- **`minions_core/apaa/pipeline.py` (Story 1.7 + 2.x + 3.1 + 3.2 + 3.3, done — UPDATE, scope-fenced).** The
  IMPURE orchestrator `run_audit_detailed` ALREADY: loads the repo at the pin (`load_repo_at_commit`),
  detects stack, builds the index, projects the halt (`_project_halt`), splits assessed vs skipped, grades
  the remainder `SKIPPED` (`_skipped_remainder_entries`), builds the partial ledger, re-folds it through
  `evaluate_verdict`, builds the `HaltReport`, persists it (`_persist_halt_report`), builds the floor report
  (`build_floor_report`). The persisted `state/` run-state payload (`_persist`, line ~390) carries
  `{schema_version, request: to_provenance_payload(), ledger: model_dump, verdict, exit_code}`;
  `_RUN_STATE_SCHEMA_VERSION = "1"`; the producer tokens are `apaa.pipeline.{verdict,run_state,halt_report,
  cost_ledger}`. **This story's pipeline touch:** ADD a resume entrypoint (`resume_audit_detailed` or a
  `resume=True` parameter on the existing entrypoint — lock the shape) that re-loads the prior `state/`
  ledger + halt report + cost snapshot via the 1-3 reader, computes the resume plan, runs detectors ONLY
  over the resume target, merges coverage, re-folds the FULL ledger through the UNCHANGED gate, and persists
  the resumed artifacts via the EXISTING `_persist*`. WITHOUT changing the verdict math / a new enum /
  a new HTTP route / the halt mechanism.
- **`minions_core/apaa/models.py::AuditRequest` (done — REUSE).** `repo_path` / `commit` / `budget` /
  `materiality_bar` / `critical_paths` / `excluded_critical_paths` / `to_provenance_payload()`. A resume
  is a new `AuditRequest` on the SAME `repo+commit` with a RAISED `budget`. Any new optional field (e.g. a
  `resume: bool` flag if chosen over a separate entrypoint) is ADDITIVE + default-preserving (a non-resume
  run is byte-identical to today — the regression-safe keystone). `commit` is the consistency anchor:
  resuming on a DIFFERENT commit must be rejected (see DN "commit-consistency").
- **`minions_core/apaa/cli.py` (done — REUSE, optionally extend).** The stdlib-`argparse` thin entrypoint.
  IF a resume is operator-invokable via the CLI (lock the choice), add a thin `--resume` flag (wiring only,
  no logic — AR2/NFR-M1); OR keep resume a library-only entrypoint exercised by tests in V1 and defer the
  CLI flag (document the choice). Either way no business logic lands in `cli.py`.

**The net-new deliverable of THIS story.** A scope-thin NEW pure resume-plan core + a scope-fenced impure
resume entrypoint + the keystone proofs:
1. a PURE **resume-plan model + builder** — a frozen `ResumePlan` (or equivalently-named;
   `frozen=True, extra="forbid"`, localized `schema_version`) recording the carried-forward
   (already-`audited_deep`) paths + the resume-target (remaining) units + the re-projected halt against the
   raised ceiling, and a PURE `build_resume_plan(prior_ledger, prior_halt_report, current_index_units,
   raised_config) -> ResumePlan` that folds the loaded prior records + the current index + the raised
   config into the plan — over in-memory inputs, NO I/O, NO clock, NO LLM (AR8). It is deterministic +
   order-independent (the carried-forward set + the resume target are sorted, content-derived). It asserts
   prior↔current consistency (every carried-forward path exists in the current index — a divergent
   tree/commit raises a typed error, NOT a silent mis-merge);
2. the impure **resume entrypoint** in `pipeline.py` (the restore-and-continue loop): load prior
   `state/` ledger + halt report + cost snapshot via the 1-3 `ApaaStoreReader` (tamper-guarded —
   `StoreIntegrityError` / `CanonicalSerializationError` / `ValidationError` / `FileNotFoundError`
   propagate → typed resume failure / `PipelineError`, exit 1); build the resume plan; run the EXISTING
   `_detect_per_file` ONLY over the resume-target entries; merge the carried-forward `audited_deep` entries
   with the new entries + any still-`skipped` remainder into a SINGLE `CoverageLedger.build(...)`; re-fold
   through the UNCHANGED `evaluate_verdict`; build the resumed `HaltReport` + floor report; persist via the
   EXISTING `_persist*`;
3. the **resume-reaches-identical-verdict proof** (the keystone) — an e2e test: `halt(budget=B1)` (a small
   budget that halts mid-run + persists state) THEN `resume(budget=B2)` (B2 ≥ the cost of the full run)
   produces a FINAL `.apaa/` verdict + coverage-ledger BYTE-IDENTICAL (content-addressed names AND on-disk
   bytes) to a single uninterrupted `run(budget=B2)` — resume does NOT change the answer (FR31 / NFR-R2);
4. the **tamper-on-resume-raises proof** (AI-E1-1) — an e2e test: after a halt, MUTATE a persisted
   `state/` payload byte (without recomputing its `content_hash`) → the resume RAISES `StoreIntegrityError`
   (mapped to a typed resume failure / exit 1), never a silent wrong resume; a non-UTF-8 / unparseable /
   unknown-field state file likewise RAISES (typed, exit 1), never a fabricated resume;
5. the **partial-state-resume proof** — a resume whose RAISED budget STILL does not cover the full
   remainder halts AGAIN (a second honest partial run): the un-reached remainder stays `SKIPPED`, the
   merged ledger reflects the additional coverage gained, the verdict degrades honestly, and the resumed
   `HaltReport` flags `halted_on_exhaustion=True` with the SHRUNKEN remaining-skipped set;
6. a **no-resume run is BYTE-IDENTICAL to the 3-3 output** — the resume entrypoint / flag is purely
   additive; a normal `run_audit` (no resume) produces byte-identical verdict/ledger/findings/halt-report
   to the pre-3.4 (3-3) output (the regression-safe keystone).

The resume-plan model + `build_resume_plan` are PURE (AR8) and join the import-isolation gate. The state
READ (the 1-3 reader) + the resumed-artifact WRITE (the EXISTING store) are the impure shell (in the
pipeline). The 1-3 reader is REUSED, not re-implemented.

**Carry-forward from the Epic-1/2/3 retros + the 3.3 discharge (CLAUDE.md §9.1 / L1-E11).**
- **AI-E1-1 (test-infra 🟠) — tamper-detection on resume; honest-degradation must never fabricate a pass.**
  This is the headline carry-forward for THIS story (the original retro action item): a corrupted /
  tampered on-disk state must **raise**, never silently resume wrong. Tests MUST prove: (a) a mutated
  persisted payload (stale `content_hash`) → `StoreIntegrityError` → typed resume failure / exit 1 (never a
  silent / fabricated resume); (b) a non-UTF-8 / unparseable / unknown-field state file → typed error (exit
  1); (c) the resumed run NEVER re-grades a carried-forward `audited_deep` file as anything else and NEVER
  fabricates an `audited_*` for a still-unreached file; (d) a non-ASCII (café/Cyrillic) path in the
  carried-forward / remaining set round-trips intact through the resume; (e) the resume plan is byte-stable
  + order-independent.
- **AI-E2-1 (process 🟠) — the premature-`status=review` flip.** This story does NOT flip `status: review`
  until ALL mandatory test files (`tests/apaa/test_resume_from_disk.py`, the e2e resume-identity +
  tamper-on-resume tests in `test_pipeline_signature_demo.py`, the import-isolation extension if a new
  module lands) EXIST and pass; the Dev Agent Record is filled completely (no blank placeholders). The
  orchestrator/dev MUST treat the test-existence precondition as a hard gate on the `review` flip.
- **AI-E2-5 (process 🟢) — keep exercising the L1-E11 loop + the three structural gates + the determinism
  surface.** Append any new pure module to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py`
  (extend, NOT fork); keep the single-serializer AST gate (`test_canonical_single_serializer.py`) green
  (any resume-plan / resumed-artifact JSON goes through `store/canonical.dumps`, never a direct
  `json.dumps`); apply byte-stability + order-independence fixtures to the resume-plan surface; the full
  host-vs-host 3.5 fixture is the next story.
- **AI-E2-3 (governance 🟢) — central defer register.** If this story files a NEW defer, file it
  append-only in `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (the single canonical APAA defer
  source), not only in the story file. **Carry-watch DF-1-3-A** (the reader does not assert the
  content-addressed FILENAME stem == the internal `content_hash` — a misfiled/renamed artifact is silently
  accepted; target_story = Epic-4 secret-containment): if the resume LOADS state by a content-addressed
  filename, record whether DF-1-3-A's filename↔hash assertion is in scope here or stays deferred to Epic 4
  — do NOT silently expand scope. **Carry-watch DF-1-3-B** (containment logic mirrored not imported; target
  = 4.2) — out of scope; resume reuses `ApaaStorePaths` as-is. **Carry-watch DF-1-7-A** (interim `_persist`
  OSError edge → Epic 3): if the resumed-artifact persistence touches the same `_persist`/`write_payload`
  path, record whether DF-1-7-A's OSError-edge hardening is in scope or stays deferred.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 3.4) + the architecture / PRD. Drivers: **APAA-FR-31**
> (APAA can resume an interrupted audit from its on-disk `.apaa/` state — the central driver),
> **APAA-NFR-R2** (an interrupted audit is fully resumable from on-disk `.apaa/` state with NO loss of
> prior coverage), **APAA-FR-22 / APAA-NFR-R1** (the resume continues the honest halt→skip→downgrade chain;
> a corrupted/tampered state degrades to a recorded typed failure — never an uncaught crash or a fabricated
> result — the honest-degradation keystone), **APAA-FR-15 / FR-16** (the resumed merged ledger is re-folded
> through the UNCHANGED pure-function gate; the floor semantics are 3.3, UNCHANGED), **APAA-FR-18 / AR3**
> (the exit-code wire contract `0/2/3/1` is UNCHANGED — reused; a resume failure → exit 1),
> **APAA-FR-25 / NFR-A1** (the resume re-verifies the content-hashed, prev-hash-chained envelope on the
> artifacts it loads — the 1-3 tamper guard), **APAA-NFR-D2** (deterministic, zero-LLM-token — the resume
> plan is a pure fold over the loaded records + the current index), **APAA-NFR-P1** (byte-identical resumed
> verdict + ledger vs an uninterrupted run; no float; the full host-vs-host proof is Story 3.5),
> **APAA-NFR-S1** (no source / secret / absolute-host-path bytes in the resume plan / resumed artifacts),
> **APAA-NFR-S5** (every FS read/write containment-checked via the 1-3 `ApaaStorePaths`),
> **APAA-NFR-M2** (frozen, additive-only contracts), **APAA-NFR-M1** (≤1200-line files), **AR4** (no
> `float`; counts `int` / flags `bool` / paths `str` / sorted `tuple`; single canonical serializer; no
> clock/uuid/random/iteration-order — content-derived, AR11), **AR7** (reuse the 1-3 reader / 3-1
> `_coerce_breach` / 3-2 `project_halt_point` BY IMPORT — no fork, §3.3), **AR8** (pure/impure separation —
> the resume-plan model + builder are PURE; the state READ + the resumed-artifact WRITE are the impure
> shell), **AR10** (typed failure, never an uncaught raise — a tamper/corruption/missing/divergent-state
> resume degrades to a typed error → exit 1), **AR11** (`.apaa/` filenames content-derived; carried-forward
> + resume-target sets sorted).
>
> **SCOPE FENCE — Tier-A, single-purpose.** This story delivers ONLY: (1) the DETERMINISTIC resume-from-disk
> RESTORE-AND-CONTINUE loop (re-load prior ledger + halt report + cost snapshot via the tamper-guarded 1-3
> reader, reuse prior `audited_deep` coverage, continue ONLY the remainder bounded by the RAISED budget,
> re-fold the merged ledger through the UNCHANGED 1.6 gate); (2) the RESUME-REACHES-IDENTICAL-VERDICT proof
> (a resumed run's final `.apaa/` verdict + ledger are BYTE-IDENTICAL to an uninterrupted run of equivalent
> budget — resume does NOT change the answer); (3) the TAMPER-ON-RESUME-RAISES guard (a mutated /
> corrupted / unparseable state RAISES a typed error → exit 1, never a silent wrong resume — REUSING the
> 1-3 `StoreIntegrityError`); (4) the PARTIAL-STATE-RESUME case (a resume whose raised budget still does not
> cover the remainder halts AGAIN, honestly). It does NOT build, and MUST NOT pull forward: the
> **host-vs-host byte-identical parity proof / any parallel scheduler** (FR32/NFR-P1 — **Story 3.5**; this
> story's resume is byte-deterministic + ships an order-independence fixture, the host-parity proof is
> 3.5); the **content-addressed memoization cache** (NFR-D1 — **Epic 5**; resume reuses the on-disk LEDGER,
> NOT a memo-cache hit); the **referential-integrity lint of `.apaa/` state** (FR26/NFR-A2 — **Story 4.2**;
> this story re-verifies the envelope tamper guard on the artifacts it loads + asserts prior↔current
> consistency, NOT the full dangling-reference lint); the **negative-assurance verdict WRAPPER**
> (FR17/NFR-A3 — **Story 4.1**); the **numeric `$X` ceiling default** (OI3 — **Story 7.1**); the **LLM
> dispatch port** (Epic 6); ANY change to the **1.6 verdict gate / its thresholds / floor-wins precedence /
> exit-code map / 1.2 ledger enum / `grade_entry` / 1.1 serializer / envelope / 1.3 reader / 3.1
> `budget_governor` / 3.2 halt mechanism / 3.3 floor report** contracts (all frozen/reused). It does NOT add
> a NEW HTTP route / FastAPI surface / UI (§3.7). Resume, reuse prior coverage, prove identical verdict,
> raise on tamper, then stop.

**AC1 — APAA resumes from the recorded `.apaa/` state, reusing prior coverage — already-`audited_deep` files are NOT re-audited (FR31, NFR-R2, AR7, AR8)**
**Given** a prior audit that HALTED on a small budget (Story 3.2) and PERSISTED its `.apaa/state/` (the
partial coverage ledger + the `HaltReport` + the cost snapshot), with some files graded `audited_deep` and
the remainder graded `SKIPPED`-on-exhaustion
**When** APAA is re-invoked on the SAME `repo + commit` with a RAISED budget (resume mode)
**Then** the resume re-loads the prior coverage ledger + halt report + cost snapshot through the EXISTING
1-3 `ApaaStoreReader` (BY IMPORT — no second reader), carries forward every prior `audited_deep` entry
VERBATIM (the SAME `CoverageLedgerEntry`), and runs detectors ONLY over the prior `skipped_on_exhaustion`
remainder (bounded by the raised budget) — it does NOT re-run `_detect_per_file` over an
already-`audited_deep` file (NFR-R2 "no loss of prior coverage" + the affordability win), proven by a test
asserting the carried-forward `audited_deep` paths are present in the resumed ledger and the detector was
invoked ONLY for the remainder
**And** when no prior `.apaa/state/` exists (a first run / a non-resume invocation), the resume entrypoint
either falls back to a normal fresh run OR raises a typed "no prior state to resume" error (lock the choice
+ document) — never a silent empty/fabricated resume.

**AC2 — The resumed run reaches the SAME deterministic verdict + ledger as an uninterrupted run — resume does NOT change the answer (FR31, NFR-R2, NFR-P1 — the KEYSTONE)**
**Given** a repo whose full audit at budget `B2` (uninterrupted) produces a verdict `V` and a coverage
ledger `L`
**When** the repo is instead audited as `halt(budget=B1)` (a small budget that halts mid-run + persists
partial state) THEN `resume(budget=B2)` (B2 ≥ the cost of the full run)
**Then** the FINAL `.apaa/` verdict + coverage-ledger after the resume are BYTE-IDENTICAL (content-addressed
artifact NAMES AND on-disk BYTES) to the single uninterrupted `run(budget=B2)` — the merged ledger is the
SAME `CoverageLedger.build(...)` (`build` re-sorts, so the merge order does not matter), re-folded through
the UNCHANGED 1.6 gate to the SAME `AuditVerdict` (`verdict`, `deep_ratio`, `exit_code`, `counts_by_depth`
all equal) — resume must NOT change the answer (the FR31/NFR-R2 keystone)
**And** this is proven by an e2e pipeline test that runs both paths against the SAME cartridge and compares
the verdict + ledger artifact bytes (a divergence is a hard test failure).

**AC3 — A corrupted / tampered on-disk state RAISES — never a silent wrong resume (FR31, NFR-R1, AR10, AI-E1-1 — the tamper keystone)**
**Given** a persisted `.apaa/state/` from a prior halted run
**When** the resume re-loads it via the 1-3 reader AND a persisted payload has been MUTATED without
recomputing its envelope `content_hash` (the tamper case), OR a state file is non-UTF-8 / unparseable /
carries an unknown field, OR a referenced state file is missing
**Then** the resume RAISES a typed error — `StoreIntegrityError` (the 1-3 tamper guard, REUSED) /
`CanonicalSerializationError` / `pydantic.ValidationError` / `FileNotFoundError` — which the resume
entrypoint maps to a typed resume failure (a localized resume error or the existing `PipelineError`,
exit `1`); it NEVER silently resumes from the corrupted state, NEVER fabricates a valid-looking resumed
verdict, NEVER falls back to a fresh run that masks the corruption (AI-E1-1: a corrupted/tampered state
must raise, never silently resume wrong)
**And** this is proven by a test that mutates a persisted `state/` byte (stale `content_hash`) and asserts
the resume raises `StoreIntegrityError` (mapped to exit 1), plus a test for the unparseable / unknown-field
state file (typed error, exit 1), plus a test that the error message names only the offending RELATIVE
locator — never source / secret / an absolute host path (NFR-S1).

**AC4 — A partial-state resume (raised budget still does not cover the remainder) halts AGAIN, honestly (FR31, FR22, NFR-R1, NFR-R2)**
**Given** a prior halted run AND a resume whose RAISED budget is STILL insufficient to audit the entire
remainder
**When** the resume runs
**Then** it audits as much of the remainder as the raised budget allows (re-projecting a fresh halt over
the remaining units against the raised ceiling via the REUSED `project_halt_point`), merges the newly-gained
`audited_deep` coverage with the carried-forward coverage, leaves the STILL-unreached remainder graded
`SKIPPED`, re-folds the merged ledger through the UNCHANGED gate (degraded, never a crash), and the resumed
`HaltReport` flags `halted_on_exhaustion=True` with the SHRUNKEN remaining-`skipped` set (the resume made
honest forward progress, never fabricated completion, never lost prior coverage)
**And** a follow-on resume with a budget that finally covers the rest reaches the same final verdict +
ledger an uninterrupted run would (AC2 holds transitively across multiple resumes), proven by a test that
chains `halt → resume(partial) → resume(complete)` and compares the final bytes to a single uninterrupted
run.

**AC5 — The resume plan + resumed artifacts are frozen, no-`float`, secret-safe, content-addressed; persisted via the EXISTING shell (NFR-M2, AR4, NFR-S1, NFR-S5, AR11, FR25)**
**Given** a built resume plan and the resumed verdict/ledger/halt-report artifacts
**When** they are inspected / serialized / persisted
**Then** the resume-plan model is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`, localized
`schema_version`) with ALL leaves `int` / `bool` / `str` / sorted `tuple[str, ...]` — **NO `float`
anywhere** (the canonical serializer rejects it), NO volatile `run_id`/`created_at` in any hashed payload
(NFR-D3), NO absolute host path / source / secret byte — only repo-relative POSIX paths +
`int`/`bool`/`str` provenance (the 1.3 DN-3 / 2.2 / 3.2 NFR-S1 precedent — never `repo_path`), verified by
an AI-E1-1-style assertion that no source/secret/absolute-host-path byte appears in the plan or the resumed
artifacts (and a non-ASCII café/Cyrillic path in the carried-forward / remaining set round-trips intact)
**And** the resumed verdict / ledger / halt-report / cost snapshot persist through the EXISTING
`ApaaStoreWriter.write_payload("state", ...)` → `EnvelopeWriter.build(...)` → `store/canonical.dumps_bytes`
(single serializer, no second `json.dumps` — the AST gate enforces it), filenames content-addressed
`<content_hash>.json` (never arrival order — AR11), guarded by the `ApaaStorePaths` `is_relative_to`
containment check (NFR-S5); re-reading the resumed artifacts via `store/reader.py` reconstructs EQUAL models
+ round-trips byte-identically (NFR-P1).

**AC6 — A no-resume run is BYTE-IDENTICAL to the 3-3 output on the verdict/ledger/findings/halt-report artifacts (NFR-P1, the regression-safe keystone)**
**Given** a normal (non-resume) `run_audit` invocation (the resume entrypoint / flag NOT exercised)
**When** the audit runs end-to-end
**Then** the verdict / coverage-ledger / findings / halt-report artifacts (content-addressed names AND
on-disk bytes) are BYTE-IDENTICAL to the pre-3.4 (3-3) output — the resume entrypoint / flag is purely
additive (a new code path; the existing `run_audit` / `run_audit_detailed` behavior is unchanged), proven
by an e2e test that compares the bytes across a pre-3.4-equivalent run and a 3.4 non-resume run; if a
`resume: bool` field is added to `AuditRequest`, its default preserves byte-identity (a `resume=False`
request is byte-identical to a request without the field — additive-only, NFR-M2).

**AC7 — The new pure logic is PURE, frozen-contract, deterministic, typed-error, import-isolated; the whole suite green; mypy clean; ≤1200 lines (NFR-D2, NFR-P1, AR8, AR10, AR7, M1, M2)**
**Given** the new resume-plan model + the PURE `build_resume_plan` builder — in a new sibling
`cost/resume.py` (recommended, the natural home alongside `exhaustion.py`) OR additively in
`cost/exhaustion.py` (lock the placement; see DN)
**When** they are imported and exercised in unit tests
**Then** the resume-plan model + the builder perform NO filesystem I/O, NO clock read
(`datetime.now`/`time.time`), NO `uuid4`/`os.getpid()`/`random`, NO LLM/network call, NO dict/`set`-
iteration-order reliance — they are PURE functions over in-memory inputs (the state READ via the 1-3 reader
and the resumed-artifact WRITE are the impure pipeline shell)
**And** the new model is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`, localized
`schema_version` — the 1.1/1.2/1.6/3.1/3.2 precedent); NO `float` anywhere (counts are `int`; flags are
`bool`; paths are `str`; sets are sorted `tuple`); any JSON rendering routes through `store/canonical.dumps`
(the single 1.1 serializer — no second `json.dumps`); the reuse of the 1-3 reader / 3-1 `_coerce_breach` /
3-2 `project_halt_point` is BY IMPORT, FastAPI-free (AR7 — the import-isolation gate proves it)
**And** a malformed input (a prior ledger whose `audited_deep` path is ABSENT from the current index — a
divergent tree/commit; a non-`CoverageLedger` / non-`HaltReport`; an inconsistent prior↔current pair)
raises a typed error (a localized resume error / a sibling of `ExhaustionError`, or the reused
`ExhaustionError`) — never a silent coerce / a silent mis-merge / a bare `except: pass` / `print()` in
library code (AR10); any resume-stage failure in the pipeline degrades to a typed resume failure /
`PipelineError` (exit `1`), never an uncaught traceback
**And** the new module (if a new file) is appended to `_MODULES_UNDER_GUARD` in
`tests/apaa/test_no_web_imports.py` (extend, do NOT fork) and importing it does NOT transitively import
`fastapi`/`uvicorn`/`starlette` or any LLM/api module (assert absence from `sys.modules`)
**And** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` passes (including
the new `tests/apaa/test_resume_from_disk.py`: AC1 resume reuses prior coverage [carried-forward
`audited_deep` not re-audited; no-prior-state behavior]; AC2 resume-reaches-identical-verdict
[halt→resume byte-identical to uninterrupted run]; AC3 tamper-on-resume-raises [`StoreIntegrityError` /
unparseable / unknown-field / missing → typed error exit 1, secret-safe message]; AC4
partial-state-resume [resume halts again honestly; chained resume reaches identity]; AC5 frozen no-`float`
secret-safe plan + round-trip [non-ASCII path round-trip]; AC7 purity [AST scan] / frozen / typed-error /
single serializer / FastAPI-free import / order-independence + byte-stability of the resume plan); `mypy` is
clean on the new + edited modules; the new source file(s) are ≤1200 lines (NFR-M1) and cite their
`APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in the module docstring. **Test area `APAA-COST`**
(`TC-APAA-COST-001-NN`, continuing the 3-1/3-2/3-3 cost area) for the resume-plan unit tests + **`APAA-PIPELINE`**
(`TC-APAA-PIPELINE-001-NN`, continuing 3-2's ...17-19 / 3-3's ...20-22) for the e2e resume tests — lock the
areas in the docstring. The 1.6 gate / its thresholds / floor-wins precedence / exit-code map / 1.2 ledger
/ `grade_entry` / 1.1 serializer / envelope / **1.3 reader** / 3.1 `budget_governor` / 3.2 halt mechanism /
3.3 floor report contracts are UNCHANGED (verify NO working-tree diff to those frozen surfaces). The
mandatory test files MUST exist + pass BEFORE the story flips to `status: review` (AI-E2-1).

## Tasks / Subtasks

- [x] **Task 0 — Verify the existing reuse surface (the resume reads from / with already-built code)** (AC: 1, 2, 3, 5)
  - [x] Re-read `store/reader.py` (1.3) — confirm `ApaaStoreReader.read_ledger` / `read_envelope(
        verify_hash=True)` / the typed `StoreIntegrityError` tamper guard + the `CanonicalSerializationError`
        / `ValidationError` / `FileNotFoundError` / `WorkspaceContainmentError` error taxonomy. **Lock:** the
        resume READS WITH this primitive; the tamper guard is REUSED, NOT re-implemented (verify no
        working-tree diff at the end).
  - [x] Re-read `pipeline.py` `_persist` (line ~354) — confirm the `state/` run-state payload shape
        (`{schema_version, request: to_provenance_payload(), ledger: model_dump, verdict, exit_code}`),
        `_RUN_STATE_SCHEMA_VERSION = "1"`, and the `_persist_halt_report` / `_persist_cost_ledger` producers.
        **This is what the resume re-LOADS.** Lock whether the resume reads the ledger from the run-state
        envelope (via `read_envelope` → `payload["ledger"]`) or via `read_ledger` over a dedicated ledger
        artifact — document the exact locator the resume reads + how it is discovered (see DN
        "how the resume finds the prior state").
  - [x] Re-read `cost/exhaustion.py` (3.2/3.3) — confirm `HaltReport` (assessed/skipped sets +
        `halted_on_exhaustion`), `project_halt_point`/`HaltProjection`, `build_halt_report`,
        `build_floor_report`, `ExhaustionError`. **The resume re-projects a fresh halt over the REMAINDER
        against the raised ceiling using `project_halt_point` (REUSED).**
  - [x] Re-read `ledger/coverage_ledger.py` (1.2/2.1) — confirm `CoverageLedger.build(entries)` re-sorts
        (so a merged ledger is order-independent), `CoverageDepth`, `grade_entry`. **The merge is a single
        `CoverageLedger.build(carried_forward + newly_audited + still_skipped)`.**
  - [x] Re-read `verdict/verdict_gate.py` (1.6/2.3) — confirm `evaluate_verdict` is PURE + UNCHANGED.
        **The resumed merged ledger is re-folded through the UNCHANGED gate** (no working-tree diff).
  - [x] Re-read `models.py::AuditRequest` (`repo_path`/`commit`/`budget`/`critical_paths`/`to_provenance_payload`)
        + `cli.py`. **Lock the resume invocation shape:** a separate `resume_audit_detailed(...)` entrypoint
        (recommended — keeps `run_audit` byte-identical) OR an additive `resume: bool` on `AuditRequest`;
        lock whether the CLI exposes a `--resume` flag in V1 or defers it (library-only + tests).
- [x] **Task 1 — The frozen resume-plan model + the PURE builder** (AC: 1, 4, 5, 7)
  - [x] Define a frozen `ResumePlan` (or locked name) — `frozen=True, extra="forbid"`, localized
        `schema_version`: `carried_forward_deep_paths: tuple[str, ...]` (sorted; the prior `audited_deep`
        paths reused verbatim), `resume_target_paths: tuple[str, ...]` (sorted; the remainder to audit now),
        `still_skipped_paths: tuple[str, ...]` (sorted; the remainder the raised budget still cannot cover —
        empty when the resume completes), `prior_total_credits: int`, `raised_ceiling_credits: int | None`,
        `halts_again: bool`. NO float; no abs-path/source/secret; no volatile run_id/created_at. Lock
        placement: `cost/resume.py` (new sibling, recommended) OR `cost/exhaustion.py` (additive) —
        document; reuse the `Fraction`/`tuple` canonical encoding from 1.1.
  - [x] PURE `build_resume_plan(prior_ledger: CoverageLedger, prior_halt_report: HaltReport,
        current_index_units: tuple[CostUnit, ...], raised_config: BudgetConfig) -> ResumePlan` — folds the
        loaded prior records + the current index + the raised config. Carried-forward = prior `audited_deep`
        paths; resume target = the prior `skipped_on_exhaustion` set re-projected via `project_halt_point`
        against the raised ceiling (accounting for the already-spent `prior_total_credits` — continue, don't
        re-spend); `still_skipped` = the remainder the raised budget still cannot reach; `halts_again =
        bool(still_skipped)`. Typed error on a malformed/inconsistent input (a carried-forward path absent
        from the current index → divergent tree → raise; AR10). Deterministic + order-independent (sorted
        sets).
  - [x] **Consistency assertion (the commit anchor):** every `carried_forward_deep_path` MUST exist in
        `current_index_units` — a prior-state path that is NOT in the current index means the tree/commit
        diverged from the prior run, and the resume RAISES a typed error (never a silent mis-merge). Document
        this as the V1 divergence guard (the full referential-integrity lint is 4.2).
- [x] **Task 2 — (Scope-fenced) the impure resume entrypoint in `pipeline.py`** (AC: 1, 2, 3, 4, 5, 6)
  - [x] Add `resume_audit_detailed(request, *, store_reader=None, store_writer=None) -> AuditResult` (or the
        locked `resume=True` shape): (1) load prior `state/` ledger + halt report + cost snapshot via the
        1-3 `ApaaStoreReader` (tamper-guarded); WRAP the typed read errors (`StoreIntegrityError` /
        `CanonicalSerializationError` / `ValidationError` / `FileNotFoundError`) → a typed resume failure
        (exit 1) — NEVER a silent fallback (AC3); (2) load the repo at the pin + build the current index
        (the SAME `load_repo_at_commit` + `build_ast_index`); (3) `build_resume_plan(...)`; (4) run
        `_detect_per_file` ONLY over the resume-target entries; (5) MERGE carried-forward `audited_deep`
        entries + newly-audited entries + `still_skipped` `SKIPPED` entries into a SINGLE
        `CoverageLedger.build(...)`; (6) re-fold through the UNCHANGED `evaluate_verdict`; (7) build the
        resumed `HaltReport` + `build_floor_report`; (8) persist via the EXISTING `_persist*`. NO verdict-math
        change, NO new enum, NO new HTTP route, NO second reader/serializer/writer.
  - [x] Keep `run_audit` / `run_audit_detailed` BYTE-IDENTICAL — the resume entrypoint is a NEW path; a
        non-resume run is unchanged (AC6). Carry-watch DF-1-7-A on the resumed persist path.
- [x] **Task 3 — Tests** (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] `tests/apaa/test_resume_from_disk.py` (TC-APAA-COST-001-NN, continuing 3-3) — AC1 resume reuses
        prior coverage [carried-forward `audited_deep` not re-audited; the no-prior-state behavior]; AC4
        partial-state resume [halts again honestly; chained `halt → resume(partial) → resume(complete)`];
        AC5 frozen no-float secret-safe plan [non-ASCII café/Cyrillic path round-trip; no abs-path/source/
        secret byte]; AC7 purity AST scan / frozen / typed-error [divergent-tree path → raise] /
        order-independence + byte-stability of the resume plan.
  - [x] Extend `tests/apaa/test_pipeline_signature_demo.py` (TC-APAA-PIPELINE-001-NN, continuing 3-3's
        ...20-22) — AC2 the KEYSTONE: `halt(B1)` THEN `resume(B2)` final verdict + ledger BYTE-IDENTICAL to
        a single `run(B2)` (compare content-addressed names + on-disk bytes); AC3 tamper-on-resume:
        mutate a persisted `state/` byte → resume raises `StoreIntegrityError` → exit 1 (+ unparseable /
        unknown-field / missing → typed error exit 1; secret-safe message); AC6 a non-resume run
        byte-identical to 3-3 on verdict/ledger/findings/halt-report.
  - [x] (If the resumed artifacts persist) round-trip test (write→read: equal model + byte-identical;
        content-addressed filename; no abs-path/source byte) — extend the existing roundtrip test or add one.
- [x] **Task 4 — Extend the import-isolation gate (if a new module lands)** (AC: 7)
  - [x] IF `cost/resume.py` is created, append `minions_core.apaa.cost.resume` to `_MODULES_UNDER_GUARD` in
        `tests/apaa/test_no_web_imports.py` (extend, not fork). If the code lands additively in the
        already-guarded `cost/exhaustion.py`, no gate change is needed (confirm it stays green).
- [x] **Task 5 — Run + mypy + the AI-E2-1 pre-`review` test-existence precondition** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass.
  - [x] `mypy` clean on the new + edited modules (`python run_mypy_per_file.py` or scoped).
  - [x] **AI-E2-1 GATE:** all mandatory test files exist + pass BEFORE the `review` flip; Dev Agent Record
        filled completely (no blank placeholders). Verify NO working-tree diff to the frozen surfaces
        (`store/reader.py`, `verdict_gate.py`, `coverage_ledger.py`, `cost/exhaustion.py`'s existing
        contracts, `budget_governor.py`, the 1.1 store spine).

### Review Findings

<!-- defer-schema-session: 2026-06-26 -->

Code-review iteration 2 (2026-06-26) — VERDICT: **pass** (re-review of the fix round). All three
iteration-1 findings are RESOLVED and independently re-verified by the reviewer. No new findings, no
new defer; the carry-watches (DF-1-3-A / DF-1-7-A / DF-1-3-B) correctly stay deferred. Status → `done`.
See the iteration-2 Senior Developer Review section below for the full re-verification record.

---

Code-review iteration 1 (2026-06-26) — VERDICT: **fail**. The keystone byte-identity
property (AC2 / NFR-R2 "no loss of prior coverage") is **broken** for any prior run that
assessed a file it did NOT grade `audited_deep`. The 642-green suite does not exercise the
failing path. Action items for the next dev round (leave unchecked):

- [x] **[Review][Patch] Resume drops prior assessed-but-non-`audited_deep` coverage — keystone AC2/NFR-R2 violation [minions_core/apaa/cost/resume.py:217-223 + minions_core/apaa/pipeline.py:968]**
  — RESOLVED (fix iteration 1, 2026-06-26). `build_resume_plan` now carries forward EVERY prior-assessed path (the halt report's `assessed_files`, all depths — `carried_forward = tuple(sorted(str(p) for p in assessed))`, resume.py); the `ResumePlan` field is `carried_forward_paths` (renamed from `carried_forward_deep_paths` to reflect all-depth semantics) and `_carried_forward_entries` reuses the prior ledger entries for ALL `carried_forward_paths` verbatim. The divergence guard covers both assessed and skipped paths. Unit regression `TC-APAA-COST-001-132` pins the all-assessed-depth carry-forward at the pure layer; the e2e keystone below pins it end-to-end (proven RED on the old `audited_deep`-only behavior: resumed `deep_ratio 1/3` vs uninterrupted `1/2`).
  — `build_resume_plan` carries forward ONLY `audited_deep` paths (`entry.depth is CoverageDepth.AUDITED_DEEP`), and `_carried_forward_entries` reuses only those. Any file the prior halted run **assessed** but graded `audited_shallow` (a test file), `tool_scanned_only`, or assessed-but-`skipped` (a parse-failed Python file) is in **neither** the carried-forward set **nor** the `resume_target` (= the prior halt report's `skipped_on_exhaustion_files`). Those entries are **silently dropped** from the merged ledger, so the resumed run is NOT byte-identical to an uninterrupted `run(B2)`.
  Reproduced concretely on a `vacuous_basic` repo + `aaa_test.py` (sorts first, graded `audited_shallow`) + `zzz.py`: `halt(6)` → `resume(100)` yields ledger **3 entries / `deep_ratio = 2/3`**, while uninterrupted `run(100)` yields **4 entries / `deep_ratio = 1/2`** — the persisted verdict envelope, run-state ledger, and halt-report bytes all diverge. The verdict label coincided here (both NOT_READY) but the differing `deep_ratio`/`counts_by_depth` denominator WILL flip the verdict near the 20% floor (the lethal "resume changes the answer" failure). This also violates AC1/NFR-R2 "no loss of prior coverage" (the prior `audited_shallow` coverage is lost) and contradicts the Completion Note "carried-forward entries are reused VERBATIM".
  **Suggested fix:** carry forward **every prior-assessed entry** (not only `audited_deep`). The prior halt report's `assessed_files` is the authoritative assessed set; the resume should reuse the prior ledger entries for ALL `assessed_files` verbatim (deep, shallow, tool_scanned_only, and assessed-but-skipped alike) and detect only the `skipped_on_exhaustion` remainder. Equivalently: `carried = [e for e in prior_ledger.entries if e.file_path in prior_halt_report.assessed_files]`, and keep the divergence guard over both assessed and skipped paths. Re-run the keystone against the new fixture below before re-flipping to review.

- [x] **[Review][Patch] Keystone e2e test cannot catch the AC2 break — add an assessed-prefix non-deep fixture [tests/apaa/test_pipeline_signature_demo.py:672 (TC-APAA-PIPELINE-001-24) + :808 (…-28)]**
  — RESOLVED (fix iteration 1, 2026-06-26). Added `TC-APAA-PIPELINE-001-30` (`test_e2e_resume_identity_with_assessed_prefix_non_deep_file`): a helper stages `vacuous_basic` + an `aaa_test.py` (vacuous-test content → `audited_shallow`) that sorts FIRST, so `halt(6)` admits the shallow test file into the ASSESSED prefix and halts at `src/calculator.py`. The test asserts the precondition (a non-deep file IS in `assessed_files`), that the resumed ledger carries `aaa_test.py` as `audited_shallow` (NOT dropped), and that `halt(6)→resume(100)` verdict/ledger/halt-report bytes are byte-identical to `run(100)`. Verified RED on the old behavior (`deep_ratio 1/3` ≠ `1/2`), green on the fix. The keystone assertion now compares the persisted HALT-REPORT bytes (added a `_halt_report_bytes` helper) on BOTH `...-30` and the existing `...-24`.
  — In `vacuous_basic` the test file (`tests/test_calculator.py`) always sorts AFTER the deep file (`src/calculator.py`), so it is always in the skipped remainder and becomes the `resume_target` — masking the dropped-coverage bug. The keystone test compares verdict + run-state ledger + findings bytes but is structurally unable to fail on this bug.
  **Suggested fix:** add a cartridge (or stage extra files into `vacuous_basic`) where a NON-`audited_deep` file (a test file or a parse-failed `.py`) sorts into the **assessed prefix** of the prior halt, then assert `halt(B1) → resume(B2)` ledger/verdict/halt-report bytes are byte-identical to `run(B2)`. This is the RED-then-green regression that pins the fix. Also extend the keystone assertion to compare the persisted **halt-report** bytes (currently uncompared), since `_resumed_halt_report` reconstructs `assessed_files` independently of `_project_halt`.

- [x] **[Review][Decision] Resumed halt-report `assessed_files` is reconstructed, not re-projected — confirm it matches an uninterrupted run for ALL assessed depths [minions_core/apaa/pipeline.py:1021-1050 (`_resumed_halt_report`)]**
  — RESOLVED (fix iteration 1, 2026-06-26) — DECISION: re-project over the full current index (the simplest, parity-guaranteeing option). The standalone `_resumed_halt_report` reconstruction was removed; `resume_audit_detailed` now builds the resumed halt report via `build_halt_report(_project_halt(index.entries, raised_config))` (pipeline.py:995) — the EXACT same call `run_audit_detailed` makes for an uninterrupted `run(raised_budget)`. This guarantees the persisted halt-report `assessed_files`/`assessed_count`/`total_credits`/`skipped_on_exhaustion_files`/`halted_on_exhaustion` are byte-identical for ALL assessed depths. Pinned by the new `_halt_report_bytes` byte-equality assertions on `TC-APAA-PIPELINE-001-30` and `...-24`.
  — `_resumed_halt_report` builds `assessed = carried_forward_deep_paths ∪ resume_target_paths`, which (per the patch above) omits assessed-but-non-deep files. Once the carry-forward fix lands, the resumed halt report's `assessed_files` / `assessed_count` / `total_credits` must be re-derived so they equal what `build_halt_report(_project_halt(full_index, raised_config))` produces for an uninterrupted run — otherwise the persisted halt-report bytes still diverge even after the ledger is fixed. Decision needed: re-project the halt over the full current index at the raised ceiling (simplest, guarantees parity) vs. continue reconstructing from the plan (must then include all assessed depths + correct cumulative `total_credits`).



- **Resume is COMPOSITION of already-built code — do NOT re-implement the reader, tamper check, halt
  projection, or verdict math (the scope crux).** The 1-3 reader (`ApaaStoreReader` + `StoreIntegrityError`)
  is the PURE deserialize/validate/tamper-guard primitive; the 3-2 `project_halt_point` is the deterministic
  halt; the 1.6 `evaluate_verdict` is the verdict. The net-new is the resume PLAN (which files to carry
  forward vs re-audit) + the resume LOOP that wires the load → plan → continue → merge → re-fold → persist.
  Read the EXISTING records; build a small additive plan; compose. Resist building anything 1.3/3.2/1.6
  already does.
- **Resume must NOT change the answer (the FR31/NFR-R2 keystone, AC2).** A resumed run's final `.apaa/`
  verdict + ledger MUST be BYTE-IDENTICAL to an uninterrupted run of the equivalent budget. The mechanism
  that makes this true: (a) the carried-forward `audited_deep` entries are re-used VERBATIM (the same frozen
  `CoverageLedgerEntry` the prior run minted); (b) the resume-target files are graded by the SAME
  deterministic `_grade_non_test_python` / detector path the uninterrupted run uses; (c) the merge is a
  single `CoverageLedger.build(...)`, which RE-SORTS by `file_path` — so the merged ledger is identical
  regardless of which files were audited in which run; (d) the verdict is the SAME `evaluate_verdict` fold
  over the SAME merged ledger. The e2e test compares the bytes directly — a divergence is a hard failure.
- **A corrupted/tampered state must RAISE, never silently resume wrong (the AI-E1-1 keystone, AC3).** The
  1-3 reader ALREADY re-verifies the envelope `content_hash` (`StoreIntegrityError` on mismatch) and wraps
  non-UTF-8 / non-JSON / unknown-field bytes as typed errors. The resume entrypoint CATCHES these and maps
  them to a typed resume failure (exit 1) — it MUST NOT swallow them and fall back to a fresh run (a fresh
  run would mask the corruption and is a different answer). The lethal failure this story prevents: a
  silently-mis-merged or fabricated resumed verdict from tampered state. Tests MUST plant a tampered byte +
  assert the raise.
- **No loss of prior coverage / no re-audit (NFR-R2, the affordability win, AC1).** A carried-forward
  `audited_deep` file is NOT re-run through the detector — the resume reuses the recorded entry. This is the
  whole point of resume (re-auditing everything is not a resume, it is a re-run). Prove the detector is
  invoked ONLY for the resume-target set.
- **A resume may itself halt again — honest partial progress (AC4).** If the raised budget still cannot
  cover the whole remainder, the resume re-projects a fresh halt over the remaining units (REUSING
  `project_halt_point` against the raised ceiling, accounting for the already-spent prior credits so it
  CONTINUES rather than re-spends), audits as much as it can, and leaves the rest `SKIPPED`. The resumed
  `HaltReport` flags `halted_on_exhaustion=True` with the shrunken skipped set. Honest forward progress,
  never fabricated completion, never lost prior coverage. A chained resume reaches the same final answer an
  uninterrupted run would (AC2 transitively).
- **The commit is the consistency anchor (the V1 divergence guard).** Resume is valid ONLY on the SAME
  `repo + commit` the prior state was recorded against. The pure `build_resume_plan` asserts every
  carried-forward path exists in the CURRENT index — a path in the prior state that is absent from the
  current index means the tree diverged, and the resume RAISES (never a silent mis-merge). The FULL
  referential-integrity lint (every reference resolves; the prev-hash chain walk) is Story 4.2; this story's
  guard is the minimal "carried-forward paths exist in the current index" consistency check + the per-
  artifact envelope tamper guard (REUSED from 1-3). Document this fence; do NOT build the 4.2 lint.
- **Re-derive vs re-load the partition plan / index (lock + document).** The 2.4 `PartitionPlan` and the 1.4
  index are deterministic functions of the same `repo@commit`, so the resume can equally RE-DERIVE them
  (rebuild the index — the recommended V1 approach, since the resume loads the repo anyway to audit the
  remainder) OR re-load the persisted plan snapshot. RECOMMENDED: re-derive the index (the resume loads the
  repo + builds the index for the remainder audit regardless), and load ONLY the prior LEDGER + halt report
  + cost snapshot (the actual prior WORK that cannot be re-derived without re-spending). Lock + document.
- **No floats — ever (AR4/NFR-P1).** The resume plan carries only `int` counts, `bool` flags, `str` paths,
  sorted `tuple`s. The NFR-C1 `Fraction` lives on the 3-1 `CostLedger` (not re-derived here). The 1.1
  serializer rejects `float` as the determinism backstop; `Fraction → "num/den"` is frozen by 1.1.
- **Pure/impure separation (master rule, AR8 — the boundary is the headline of this story).** The PURE side
  is the resume-plan model + `build_resume_plan` (over in-memory loaded records + the current index — no
  I/O, no clock, no LLM). The IMPURE side is the state READ (the 1-3 reader, off disk) + the resumed-artifact
  WRITE (the EXISTING store) — both in the pipeline entrypoint. ✅ a pure `build_resume_plan(prior_ledger,
  prior_halt_report, current_units, raised_config)` · ❌ a `build_resume_plan` that opens the state file
  itself (the READ is the impure entrypoint's job, handed to the pure builder as already-loaded models).
  Keep the boundary clean: the entrypoint reads + writes; the plan builder is a pure fold.
- **The cache/memoization is Epic 5 — resume reuses the LEDGER, not a memo-cache (the primary scope fence).**
  Resume continues an interrupted run from its persisted partial LEDGER (the work recorded). It does NOT
  build a content-addressed cache key (`cache/key.py`), a memo store (`cache/memo_store.py`), or a
  cache-invalidation rule — those are Epic 5 (NFR-D1). The `.apaa/cache/` dir is a directory only in V1. If
  tempted to add a cache-key or a memo lookup — STOP, that is Epic 5.
- **The host-vs-host parity proof is Story 3.5 — resume determinism is THIS story (the secondary fence).**
  THIS story proves resume reaches the SAME answer as an uninterrupted run (resume determinism); 3.5 proves
  that answer is byte-identical across hosts / sequential-vs-parallel. Keep the resume plan byte-deterministic
  (no clock/uuid/random; sorted sets) so 3.5 inherits a determinate surface; ship an order-independence +
  byte-stability fixture on the resume plan; do NOT build the host-parity proof or any parallel scheduler.
- **Error/degradation → typed, never crash (AR10).** A tampered/corrupt/missing state (the 1-3 reader's
  typed errors) → a typed resume failure (exit 1). A divergent-tree resume (a carried-forward path absent
  from the current index) → a typed error from `build_resume_plan`. A malformed input → a localized resume
  error / a reused `ExhaustionError`. NO bare `except: pass`, NO `print()` in library code, NO silent coerce,
  NO silent fallback-to-fresh-run.
- **No absolute host paths / secrets in artifacts (NFR-S1).** The resume plan + resumed artifacts carry
  repo-relative POSIX paths + `int`/`bool`/`str` provenance only — never `repo_path`, never source/secret
  bytes (the 1.3 DN-3 / 2.x / 3.x precedent). The 1-3 reader's error messages name only the RELATIVE locator
  (already enforced).
- **Headless / import boundary (§3.7, AR7/AR9).** No UI, no HTML/CSS/JS, no FastAPI route. The new pure
  logic takes no token, registers no route, imports only the FastAPI-free 1-3 reader + 3-1/3-2 cost cores,
  and joins `_MODULES_UNDER_GUARD` if it is a new file. If a `--resume` CLI flag is added, it is thin
  argparse wiring only.

### How the resume finds the prior state (the central wiring call — lock + document)

The 3-2 pipeline persists the run-state to `state/<content_hash>.json` (content-addressed, producer
`apaa.pipeline.run_state`), the halt report to `state/<content_hash>.json` (producer
`apaa.pipeline.halt_report`), and the cost snapshot (producer `apaa.pipeline.cost_ledger`). The resume must
DISCOVER these locators on a re-invocation. The dev locks the discovery mechanism + documents it:

- **Option A (recommended for V1): the resume entrypoint takes the prior locators (or reads `state/` and
  selects by producer token).** Since the filenames are content-addressed (not a stable name), the resume
  enumerates `state/` envelopes and selects the latest run-state / halt-report by their `producer` field (a
  deterministic, content-derived discovery — read each envelope's `producer`, pick the run-state + halt
  report). The `AuditResult.locators` the prior run returned are also available to a test/caller as the
  explicit seam.
- **Option B: a stable "latest" pointer.** Out of scope for V1 unless Option A proves insufficient (avoid a
  speculative pointer artifact — three similar lines beat a premature abstraction).

Lock the choice (A recommended) + document it in the Change Log. Whichever is chosen, the discovery MUST be
deterministic (no arrival-order reliance — AR11) and the READ MUST go through the 1-3 reader (tamper-guarded).

### Reuse map (do NOT rebuild — the resume composes these)

| Need | Reuse (BY IMPORT, no fork) | Source story |
|---|---|---|
| Read + validate + tamper-guard prior `.apaa/` state | `store/reader.py::ApaaStoreReader` (`read_ledger`/`read_envelope`); `StoreIntegrityError` | 1.3 |
| Content-hash re-verification (the tamper guard) | `store/envelope.py::compute_content_hash`; `read_envelope(verify_hash=True)` | 1.1 / 1.3 |
| Re-project a fresh halt over the remainder | `cost/exhaustion.py::project_halt_point` / `HaltProjection` / `build_halt_report` | 3.2 |
| Breach decision (`>=` hard ceiling) | `cost/budget_governor.py::_coerce_breach` (via `project_halt_point`) | 3.1 |
| Merge + re-sort the coverage ledger | `ledger/coverage_ledger.py::CoverageLedger.build` / `grade_entry` / `CoverageDepth` | 1.2 / 2.1 |
| Re-fold the merged ledger → verdict | `verdict/verdict_gate.py::evaluate_verdict` (UNCHANGED) | 1.6 / 2.3 |
| Floor report on the resumed verdict | `cost/exhaustion.py::build_floor_report` | 3.3 |
| Persist resumed artifacts (content-addressed, contained) | `store/writer.py::ApaaStoreWriter.write_payload`; `store/paths.py::ApaaStorePaths`; `store/canonical` | 1.1 / 1.3 |
| Load the repo at the pin + build the current index | `intake/repo_loader.py::load_repo_at_commit`; `index/ast_index.py::build_ast_index` | 1.4 |
| Run detectors over the resume target | `pipeline.py::_detect_per_file` (UNCHANGED) | 1.5 / 2.x |
| Typed fatal → exit 1 | `pipeline.py::PipelineError` (or a localized resume error) | 1.7 |

### Project Structure Notes

- **Placement (lock):** the resume-plan model + `build_resume_plan` go in a NEW pure sibling
  `minions_core/apaa/cost/resume.py` (recommended — the natural home alongside `exhaustion.py`; keeps
  `exhaustion.py` focused on the halt/floor concern) OR additively in `cost/exhaustion.py`. The impure resume
  entrypoint goes in `pipeline.py` (the existing orchestrator). If `cost/resume.py` is new, append it to
  `_MODULES_UNDER_GUARD` (Task 4).
- **No new flat file at `minions_core/` (the APAA sub-package is under `minions_core/apaa/`, not a flat
  singleton — the §4a allow-list is for the Minions platform, not APAA).**
- **Test areas:** `APAA-COST` (`TC-APAA-COST-001-NN`) for the resume-plan unit tests (continuing
  3-1/3-2/3-3); `APAA-PIPELINE` (`TC-APAA-PIPELINE-001-NN`) for the e2e resume tests (continuing 3-2's
  ...17-19 / 3-3's ...20-22). Lock the next available sequence numbers in the docstrings.
- **Conflicts / variances:** none expected. The resume is additive (a new entrypoint + a new pure model);
  the existing `run_audit` path is byte-identical (AC6). If a `resume: bool` is added to `AuditRequest`, it
  is additive-only with a byte-preserving default.

### References

- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Story 3.4: Resumability from on-disk `.apaa/` state] — the two epic ACs (resume reusing prior coverage; final state identical to an uninterrupted run).
- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Epic 3: Honest Degradation & Cost Governance] — FR21/FR22/FR31/FR32/FR16-floor; NFRs C1/C2/R2/P1/P2.
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md] FR31 (resume from `.apaa/` state); NFR-R2 (fully resumable, no loss of prior coverage); NFR-D2/D3/P1; NFR-S1/S5; NFR-A1; NFR-M1/M2.
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#F. Persistence & State] — filesystem-as-contract `.apaa/{state,...}`, resumable + portable (FR31); the `.apaa/` runtime tree (`state/` = run state + coverage-ledger snapshots, resumable).
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#FR-cluster→location] — Invocation & Resumability (FR30–32) | `cli.py`, `pipeline.py`, `store/reader.py`; NFR R1–2 (`store/reader` resume).
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md] AR4 (single canonical serializer; no float/clock/uuid/random), AR7 (reuse-by-import leaf modules), AR8 (pure/impure separation), AR10 (failure→typed, never uncaught raise), AR11 (`.apaa/` content-addressed filenames).
- [Source: minions_core/apaa/store/reader.py] — `ApaaStoreReader`, `read_ledger`/`read_envelope(verify_hash=True)`, `StoreIntegrityError` (the REUSED tamper guard; module docstring already names FR-31 resumability).
- [Source: minions_core/apaa/cost/exhaustion.py] — `HaltReport`, `project_halt_point`/`HaltProjection`, `build_halt_report`, `build_floor_report`, `ExhaustionError` (REUSE).
- [Source: minions_core/apaa/pipeline.py] — `run_audit_detailed`, `_persist`/`_persist_halt_report`/`_persist_cost_ledger`, `_detect_per_file`, `AuditResult`, `PipelineError`, `_RUN_STATE_SCHEMA_VERSION`, the producer tokens (the resume seam to extend).
- [Source: minions_core/apaa/verdict/verdict_gate.py] — `evaluate_verdict` (UNCHANGED, re-folded over the merged ledger).
- [Source: minions_core/apaa/ledger/coverage_ledger.py] — `CoverageLedger.build` (re-sorts), `CoverageDepth`, `grade_entry` (REUSE).
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/3-2-halt-skip-downgrade-report-on-budget-exhaustion.md] — the persisted resume seam (the halt report + partial ledger + cost snapshot in `state/`).
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/3-3-insufficient-coverage-floor-under-exhaustion.md] — the floor report (additive, derivable) the resumed verdict carries unchanged.
- [Source: _bmad-output/design-artifacts/ArgusAgent/deferred-work.md] — DF-1-3-A (filename↔hash assertion, carry-watch), DF-1-3-B (containment mirror), DF-1-7-A (interim `_persist` OSError edge, carry-watch).
- [Source: CLAUDE.md] §3.2 (≤1200-line files), §3.7 (headless-only), §3.8 (12-Factor + secret masking), §3.4 (evidence immutability), §9.1/§9.2 (L1-E11 retro-as-backlog + rule-of-three guard promotion).

## Dev Agent Record

### Agent Model Used

claude-opus-4-8 (dev-story, implement) — 2026-06-25.

### Debug Log References

- (fix iteration 1, 2026-06-26) `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py`
  → **644 passed** (17 `TC-APAA-COST-001-116..132` resume-plan unit tests incl. the new `...-132`
  all-assessed-depth carry-forward regression + 8 `TC-APAA-PIPELINE-001-23..30` e2e resume tests incl. the new
  `...-30` assessed-prefix-non-deep keystone fixture). `python -m mypy minions_core/apaa/cost/resume.py
  minions_core/apaa/pipeline.py` → clean. Frozen-surface `git diff --stat` empty (reader / verdict_gate /
  coverage_ledger / exhaustion / budget_governor / models / canonical / envelope unchanged). no-web-imports +
  single-serializer gates green. The `...-30` keystone proven RED on the old `audited_deep`-only behavior
  (resumed `deep_ratio 1/3` ≠ uninterrupted `1/2`), green on the fix.
- (implement, 2026-06-25) `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **642 passed** (16
  `TC-APAA-COST-001-116..131` resume-plan unit tests + 7 `TC-APAA-PIPELINE-001-23..29` e2e resume tests).
- `python -m mypy minions_core/apaa/cost/resume.py minions_core/apaa/pipeline.py --ignore-missing-imports`
  → **Success: no issues found in 2 source files**.
- `test_canonical_single_serializer.py` + `test_no_web_imports.py` (incl. the new
  `minions_core.apaa.cost.resume` guard row) → green.
- Smoke-verified the keystone before formalizing: `halt(6)` → `resume(100)` verdict + run-state-ledger bytes
  BYTE-IDENTICAL to a single `run(100)`; tamper-on-resume raises `ResumeStateError`; no-prior-state raises.

### Completion Notes List

- **Locked decisions.** (1) Placement: a NEW pure sibling `minions_core/apaa/cost/resume.py` (recommended in
  the story — keeps `exhaustion.py` frozen). (2) Invocation shape: a SEPARATE `resume_audit_detailed(request,
  *, store_reader=None, store_writer=None)` entrypoint + a `resume_audit(...)` simple wrapper (NOT a
  `resume: bool` on `AuditRequest`) — so `run_audit`/`run_audit_detailed` stay byte-identical and no field is
  added to the frozen `AuditRequest` (AC6 regression-safe keystone). The CLI `--resume` flag is DEFERRED to a
  follow-up (library-only + tests in V1) — `cli.py` is UNCHANGED (no new business logic; DF noted below).
  (3) Prior-state discovery: enumerate `state/` envelopes (sorted locators — AR11) + select by PRODUCER token
  (`apaa.pipeline.run_state` for the ledger via `payload["ledger"]`, `apaa.pipeline.halt_report` for the halt
  report), reading each via the 1-3 `read_envelope(verify_hash=True)` (tamper guard REUSED). For a CHAINED
  resume that accumulates multiple records, latest-progress is selected content-deterministically (the ledger
  with the MOST `audited_deep`, the halt report with the LARGEST `assessed_count`) — no clock / recency
  pointer. (4) Index: RE-DERIVED (the resume loads the repo to audit the remainder anyway); only the prior
  LEDGER + halt report + findings are RE-LOADED (the actual prior work). (5) Findings: the carried-forward
  findings are re-loaded from `findings/` and merged (deduped by content-derived `recording_id`) with the
  resume-target detector findings; `evaluate_verdict`'s `order_findings` re-sorts, so the union matches the
  uninterrupted run's finding set (AC2).
- **(fix iteration 1, 2026-06-26) Carry-forward-every-assessed-depth + halt-report re-projection (the review fixes).**
  The iteration-1 review found the resume carried forward ONLY `audited_deep` entries, silently dropping prior
  assessed-but-non-deep coverage (`audited_shallow` / `tool_scanned_only` / assessed-`skipped`) and breaking the
  AC2 byte-identity keystone. FIX: (1) `build_resume_plan` carries forward EVERY path in the prior halt report's
  `assessed_files` (all depths), the `ResumePlan` field renamed `carried_forward_deep_paths → carried_forward_paths`,
  and `_carried_forward_entries` reuses the prior ledger entries for ALL of them verbatim; (2) the resumed halt
  report is re-projected over the FULL current index via `build_halt_report(_project_halt(index.entries, raised_config))`
  — the SAME call the uninterrupted run makes — so its `assessed_files`/`assessed_count`/`total_credits` are
  byte-identical for all depths; (3) a new keystone fixture (`TC-APAA-PIPELINE-001-30`, an `aaa_test.py` shallow
  file in the assessed prefix) + a unit regression (`TC-APAA-COST-001-132`) pin both, with the keystone now
  comparing the persisted HALT-REPORT bytes. The prior interrupted-session partial fix (model + `_carried_forward_entries`)
  was completed by reconciling the `ResumePlan` field name with the unit tests (the AttributeError) and adding the
  missing tests.
- **Byte-identity mechanism (AC2 keystone).** The carried-forward assessed entries (ALL depths) are reused VERBATIM
  from the prior ledger; the resume-target files are graded by the SAME `_detect_per_file`; the merge is a
  single re-sorting `CoverageLedger.build(carried + new + still_skipped)`; the verdict is the SAME
  `evaluate_verdict` fold. The resume plan re-projects the halt over the remainder against the RAISED ceiling
  with the already-spent prior credits SEEDED (a sentinel `""`-path unit sorted first, cost = prior spend) so
  the raised ceiling is a TOTAL budget and the resume admits exactly the same suffix prefix an uninterrupted
  `run(B2)` would. Verified: verdict + run-state-ledger + findings bytes are byte-identical to `run(B2)`.
- **Tamper-on-resume (AC3 / AI-E1-1).** A mutated persisted payload (stale `content_hash`) → the 1-3
  `StoreIntegrityError` propagates and is mapped to a typed `ResumeStateError` (a `PipelineError`/`ValueError`
  subclass → exit 1); an unknown-field / unparseable / missing state → `ValidationError` /
  `CanonicalSerializationError` / `FileNotFoundError` → `ResumeStateError`. NEVER a silent fallback to a fresh
  run (which would mask the corruption), NEVER a fabricated verdict. The error message names only the typed
  reason + relative locator — no absolute host path / source / secret byte (asserted).
- **Partial-state resume (AC4).** A raised budget still short halts AGAIN: the still-skipped remainder stays
  `SKIPPED`, the resumed `HaltReport` flags `halted_on_exhaustion=True` with the shrunken skipped set, and a
  follow-on resume that finally covers the rest reaches the SAME final bytes a single `run(B2)` would (proven
  by `halt(6) → resume(11, partial) → resume(100, complete)` over the 3-file clean_control cartridge).
- **Divergence guard (V1).** `build_resume_plan` raises the typed `ResumeError` (→ `ResumeStateError`) when a
  carried-forward / prior-skipped path is absent from the current index (the tree/commit diverged) — never a
  silent mis-merge. The full referential-integrity lint (FR26/NFR-A2) stays DEFERRED to Story 4.2 (scope not
  expanded).
- **Reuse, no fork (AR7/§3.3).** REUSES the 1-3 `ApaaStoreReader`/`StoreIntegrityError`, the 3-2
  `project_halt_point`, the 1.2 `CoverageLedger.build`/`grade_entry`/`CoverageDepth`, the 1.6
  `evaluate_verdict`, the 3-1 `BudgetConfig`/`budget_config_from_budget`, the 3-3 `build_floor_report`, and
  the EXISTING `_persist*` — all BY IMPORT. No second reader / tamper check / serializer / writer / verdict
  math / halt projection. The fresh-run analysis assembly was extracted into `_assemble_and_persist` so the
  resume folds the merged ledger through the EXACT SAME persist path (the byte-identity keystone).
- **Frozen surfaces UNCHANGED (verified no edit).** `store/reader.py`, `verdict/verdict_gate.py`,
  `ledger/coverage_ledger.py`, `cost/exhaustion.py`, `cost/budget_governor.py`, `models.py`, the 1.1 store
  spine (`canonical.py`/`envelope.py`/`paths.py`/`writer.py`). Only `pipeline.py` was edited (additive resume
  entrypoint + the shared `_assemble_and_persist` extraction) and `cost/resume.py` was created.
- **Carry-watches.** DF-1-3-A (filename↔hash assertion): the resume discovers state by PRODUCER token (not by
  a content-addressed filename stem), so DF-1-3-A is NOT in scope here and stays DEFERRED to Epic 4. DF-1-7-A
  (interim `_persist` OSError edge): the resumed-artifact persistence reuses the EXISTING `_persist*` path
  unchanged, so DF-1-7-A stays DEFERRED (no scope expand). DF-1-3-B (containment mirror) out of scope.
- **New defer filed.** DF-3-4-A (🟢 process) — the `--resume` CLI flag is library-only in V1 (the resume
  entrypoint is exercised by tests; the operator-facing CLI wiring is deferred). Filed append-only in
  `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`. Resume requires the `.apaa/` store to live OUTSIDE
  the audited working tree (an injected reader/writer) since the resume re-loads the repo at the pin and the
  loader refuses a drifted tree — the V1 resume seam (documented; the in-tree `.gitignore`d-`.apaa/`
  ergonomics ride along with the deferred CLI flag).

### File List

- `minions_core/apaa/cost/resume.py` (NEW — pure `ResumePlan` [field `carried_forward_paths`, all-assessed-depth] +
  `build_resume_plan` + `ResumeError`; ~285 lines).
- `minions_core/apaa/pipeline.py` (EDITED — `resume_audit_detailed`/`resume_audit`/`ResumeStateError` +
  `_read_prior_state`/`_list_locators`/`_carried_forward_entries` [all assessed depths]/`_merge_findings` + the
  resumed halt report re-projected over the full current index + the shared `_assemble_and_persist` extraction; ≤1200).
- `tests/apaa/test_resume_from_disk.py` (NEW + fix-iter-1 — `TC-APAA-COST-001-116..132`, 17 resume-plan unit tests;
  field rename `carried_forward_deep_paths → carried_forward_paths`; new `...-132` all-assessed-depth carry-forward regression).
- `tests/apaa/test_pipeline_signature_demo.py` (EXTENDED + fix-iter-1 — `TC-APAA-PIPELINE-001-23..30`, 8 e2e resume tests;
  new `...-30` assessed-prefix-non-deep keystone fixture + `_halt_report_bytes`/`_stage_with_assessed_prefix_non_deep_file`
  helpers; halt-report-byte comparison added to `...-24` and `...-30`).
- `tests/apaa/test_no_web_imports.py` (EXTENDED — appended `minions_core.apaa.cost.resume` to `_MODULES_UNDER_GUARD`).
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (APPENDED — DF-3-4-A).
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (3-4 → `review`; `last_updated` 2026-06-26).

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-06-25 | 0.1 | Story created (create-story). | Scrum Master |
| 2026-06-25 | 1.0 | Implemented FR31/NFR-R2 resumability: NEW pure `cost/resume.py` (frozen `ResumePlan` + `build_resume_plan`, divergence guard, prior-spend-seeded halt re-projection) + the impure `resume_audit_detailed`/`resume_audit` entrypoint in `pipeline.py` (tamper-guarded 1-3 read → plan → detect-remainder-only → merge → re-fold → persist via the EXISTING shell). Keystone proven: `halt(B1)` → `resume(B2)` verdict + ledger BYTE-IDENTICAL to `run(B2)`. AI-E1-1 tamper-on-resume → typed `ResumeStateError`/exit 1 (never silent wrong resume); partial-state resume halts again honestly; no-resume run byte-identical to 3-3 (AC6). 642 passed, mypy clean, single-serializer + web-import gates green. DF-3-4-A filed (CLI `--resume` deferred); DF-1-3-A / DF-1-7-A stay deferred. | Dev (claude-opus-4-8) |
| 2026-06-26 | 1.3 | Code-review iteration 2 (re-review of the fix round) — VERDICT **pass**. All three iteration-1 findings RESOLVED + independently re-verified: [High] carry forward EVERY prior-assessed path (all depths) — reviewer reverted to old deep-only behavior and confirmed `TC-APAA-PIPELINE-001-30` goes RED (`deep_ratio 1/3`≠`1/2`) + `TC-APAA-COST-001-132` RED (`carried_forward_paths ()`≠`('a_test.py',)`), green on the fix; [Med] keystone now compares persisted halt-report bytes on `...-30` and `...-24`; [Decision] resumed halt report re-projected via the identical `build_halt_report(_project_halt(index, raised_config))` call. 644 passed (reviewer-run), mypy clean, single-serializer + no-web-imports gates green, frozen surfaces + `cli.py`/`AuditRequest` unchanged, files ≤1200, headless. No new findings, no new defer. Status → `done`. | Reviewer (claude-opus-4-8) |
| 2026-06-26 | 1.2 | Fix iteration 1 — resolved all 3 review findings. [High] resume now carries forward EVERY prior-assessed path (all depths) via the halt report's `assessed_files`, not just `audited_deep` (`ResumePlan.carried_forward_paths`; `_carried_forward_entries` reuses all assessed entries verbatim) — completes the interrupted-session partial fix by reconciling the renamed model field with the unit tests (the AttributeError). [Med] added `TC-APAA-PIPELINE-001-30` keystone fixture (`aaa_test.py` shallow file in the assessed prefix, proven RED on old behavior `deep_ratio 1/3`≠`1/2`) + `TC-APAA-COST-001-132` unit regression; keystone now compares persisted halt-report bytes. [Decision] resumed halt report re-projected over the full current index (`build_halt_report(_project_halt(index.entries, raised_config))`) = the uninterrupted-run call, byte-identical for all depths. 644 passed, mypy clean, frozen surfaces unchanged, gates green. Status → `review`. | Dev (claude-opus-4-8) |
| 2026-06-26 | 1.1 | Code-review iteration 1 — VERDICT **fail**. Found a High-severity correctness bug breaking the AC2/NFR-R2 keystone: the resume carries forward ONLY `audited_deep` entries, silently dropping prior assessed-but-non-deep coverage (`audited_shallow` test files / `tool_scanned_only` / assessed-`skipped`). Reproduced: `halt(6)→resume(100)` ledger `deep_ratio 2/3` vs uninterrupted `run(100)` `1/2` — verdict/ledger/halt-report bytes diverge. The 642-green keystone test cannot catch it (the non-deep file always sorts into the skipped remainder in `vacuous_basic`). Status → `in-progress`; findings written for the next dev round. | Reviewer (claude-opus-4-8) |

## Senior Developer Review (AI)

**Reviewer:** claude-opus-4-8 (adversarial code-review gate) · **Date:** 2026-06-26 · **Iteration:** 2 · **Outcome:** **PASS** (status → `done`).

### Summary

The iteration-1 High finding (resume carried forward only `audited_deep`, silently dropping prior
assessed-but-non-deep coverage and breaking the AC2/NFR-R2 byte-identity keystone) and both Med
findings (the keystone test could not catch it; resumed halt-report bytes diverged) are **resolved and
independently re-verified by the reviewer**. The fix is correct in substance, not just green:

1. **[High] resolved — carry forward EVERY prior-assessed path (all depths).** `build_resume_plan`
   now derives `carried_forward` from the prior halt report's `assessed_files`
   (`tuple(sorted(str(p) for p in assessed))`), and `_carried_forward_entries` reuses the prior ledger
   entries for ALL of those paths verbatim (`[e for e in prior_ledger.entries if e.file_path in wanted]`)
   — deep, shallow, tool_scanned_only, and assessed-but-skipped alike. The `ResumePlan` field was
   correctly renamed `carried_forward_deep_paths → carried_forward_paths` and reconciled with the unit
   tests (the interrupted-session AttributeError is gone). The divergence guard covers both the assessed
   and the prior-skipped sets; the prior-ledger-consistency guard additionally rejects an assessed path
   with no prior ledger entry.
2. **[Med] resolved — the keystone test now catches the bug.** `TC-APAA-PIPELINE-001-30` stages
   `vacuous_basic` + an `aaa_test.py` (vacuous-test content → `audited_shallow`) that sorts FIRST, so
   `halt(6)` admits the shallow test file into the ASSESSED prefix and halts at `src/calculator.py`. The
   test asserts the precondition (the non-deep file IS in `assessed_files`), that the resumed ledger
   carries `aaa_test.py` as `audited_shallow` (NOT dropped), and that the persisted verdict + run-state
   ledger + **halt-report** bytes are byte-identical to a single uninterrupted `run(100)`. The unit
   regression `TC-APAA-COST-001-132` pins the all-assessed-depth carry-forward at the pure layer.
3. **[Decision] resolved — resumed halt-report parity by construction.** The standalone
   `_resumed_halt_report` reconstruction was removed; `resume_audit_detailed` now builds the resumed
   halt report via `build_halt_report(_project_halt(index.entries, raised_config))` — the EXACT same
   call `run_audit_detailed` makes for an uninterrupted `run(raised_budget)`. This guarantees the
   persisted halt-report `assessed_files`/`assessed_count`/`total_credits`/`skipped_on_exhaustion_files`/
   `halted_on_exhaustion` are byte-identical for all assessed depths, pinned by the new
   `_halt_report_bytes` byte-equality assertions on `...-30` AND `...-24`.

### Independent re-verification (run by the reviewer)

- **Both regression tests genuinely go RED on the old behavior.** The reviewer temporarily reverted
  `build_resume_plan` to the old `audited_deep`-only carry-forward and re-ran: `TC-APAA-PIPELINE-001-30`
  fails with `deep_ratio 1/3` (resumed) vs `1/2` (uninterrupted) — i.e. the dropped-coverage bug is
  reproduced and caught; `TC-APAA-COST-001-132` fails with `carried_forward_paths == ()` vs
  `('a_test.py',)`. The correct file was then restored and both go green. The fixtures are non-vacuous
  RED-then-green regressions, not green-by-construction.
- **Full suite green.** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py`
  → **644 passed** (re-run by the reviewer). `mypy minions_core/apaa/cost/resume.py
  minions_core/apaa/pipeline.py` → clean. The single-serializer AST gate + the no-web-imports gate
  (with the `minions_core.apaa.cost.resume` row present in `_MODULES_UNDER_GUARD`) are green.
- **No regression of what passed in iteration 1.** Tamper-on-resume (`...-25`, real persisted-byte
  mutation → `ResumeStateError`/`PipelineError`, message asserted free of abs-path/`C:\`/`/home/`/repo
  path — NFR-S1), unknown-field-with-valid-hash (`...-26`, Validationation layer rejects independently),
  no-prior-state (`...-27`, typed error, never a silent fresh run), chained partial→complete
  (`...-28`, compares to a single uninterrupted run), no-resume byte-identity to 3-3 (`...-29`, AC6) all
  pass. Reuse-by-import (1-3 reader/`StoreIntegrityError`, 3-2 `project_halt_point`, 1.2 ledger, 1.6
  `evaluate_verdict`, 3-1 `budget_governor`, 3-3 `build_floor_report`) is intact — no fork, no second
  serializer/reader/tamper-check.
- **Frozen surfaces unchanged.** `store/reader.py`, `verdict/verdict_gate.py`, `ledger/coverage_ledger.py`,
  `cost/exhaustion.py`, `cost/budget_governor.py`, `models.py`, the 1.1 store spine — no resume logic
  leaked in (the only `resume` mentions in those files are pre-existing 3-2/3-3/1-3 docstring references).
  `cli.py` / `AuditRequest` unchanged (the resume entrypoint is a separate function; `--resume` deferred
  as DF-3-4-A). Only `cost/resume.py` (new, 251 non-blank lines) and `pipeline.py` (920 non-blank lines)
  carry the story's edits — both ≤1200 (NFR-M1). Headless (no HTTP route / FastAPI / UI).

### Correctness note on the byte-identity argument (accepted)

The keystone holds because: (a) the carried-forward entries are reused VERBATIM from the prior ledger,
and per-file grading is deterministic, so a file assessed `audited_shallow` under B1 is exactly what an
uninterrupted `run(B2)` would grade it; (b) the resume-target files are graded by the SAME
`_detect_per_file`; (c) the merge is a single re-sorting `CoverageLedger.build(carried + new +
still_skipped)`, so order does not matter; (d) the verdict is the SAME `evaluate_verdict` fold; and (e)
the resumed halt report is the identical `build_halt_report(_project_halt(full_index, raised_config))`
projection. The prior-spend SEED unit (a sentinel `""`-path cost = prior credits, sorted first) makes
the raised ceiling a TOTAL budget so the resume admits exactly the suffix prefix an uninterrupted run
would. The reviewer confirmed `carried_forward ∪ resume_target ∪ still_skipped` reconstructs the full
index for the tested cartridges (verified via the byte-identity of the persisted ledger + halt report).

### Verdict rationale

The story's stated keystone (resume must not change the answer; no loss of prior coverage) is now
genuinely pinned by RED-then-green regressions at both the pure and e2e layers, including the previously
uncompared halt-report bytes. Tests are green AND pin the property they claim. No unresolved
`decision-needed`/`patch` findings, no High/Med issues, tests/lint/types green, all ACs met. PASS → `done`.

### Action Items

None. All iteration-1 findings closed. No new defer filed.

---

**Reviewer:** claude-opus-4-8 (adversarial code-review gate) · **Date:** 2026-06-26 · **Iteration:** 1 · **Outcome:** **FAIL** (status → `in-progress`).

### Summary

The story's composition discipline is exemplary: the 1-3 reader / `StoreIntegrityError` tamper
guard, the 3-2 `project_halt_point`, the 1.2 `CoverageLedger.build`/`grade_entry`, the 1.6
`evaluate_verdict`, the 3-1 `budget_governor`, and the 3-3 `build_floor_report` are all reused BY
IMPORT with no fork; `ResumePlan` is frozen/`extra="forbid"`/no-`float`; `cost/resume.py` is pure
(AST-pinned) and joins `_MODULES_UNDER_GUARD`; the shared `_assemble_and_persist` extraction is a
clean way to share the persist path; tamper-on-resume, no-prior-state, and the divergence guard are
genuinely proven (real persisted-byte mutation, not a mocked guard); DF-3-4-A is schema-valid. The
no-resume run is byte-identical (AC6 holds). Tests: **642 passed**, mypy reported clean by the dev.

**However, the headline keystone (AC2 / NFR-R2 "resume must not change the answer / no loss of
prior coverage") is broken.** The resume reuses only the prior `audited_deep` entries; any file the
prior halted run *assessed* but graded at another depth (a test file → `audited_shallow`, a
parse-failed `.py` → assessed-`skipped`, a `tool_scanned_only` breadth grade) is **silently dropped**
from the merged ledger. The suite is green only because the `vacuous_basic` cartridge's single test
file always sorts after the deep file (so it lands in the skipped remainder and is recovered as the
resume target), structurally masking the bug.

### Reproduction (concrete, run by the reviewer)

Staged `vacuous_basic` + `aaa_test.py` (sorts first, `audited_shallow`) + `zzz.py` (`audited_deep`):
- uninterrupted `run(100)` → ledger **4 entries**, `deep_ratio = 1/2`, `counts {deep:2, shallow:2}`.
- `halt(6)` → `resume(100)` → ledger **3 entries** (`aaa_test.py` dropped), `deep_ratio = 2/3`,
  `counts {deep:2, shallow:1}`. Persisted verdict envelope, run-state ledger, and halt-report bytes
  all diverge. The verdict label coincided (both NOT_READY) but the differing `deep_ratio` denominator
  will flip RELEASE_READY / NOT_READY / INSUFFICIENT_COVERAGE at the 20% floor boundary.

### Verdict rationale

A story whose stated keystone is byte-identity cannot pass when a realistic resume scenario produces
a different verdict surface and loses prior coverage. The tests are green but do not pin the property
they claim to (no fixture exercises a non-deep file in the assessed prefix; the halt-report bytes are
never compared in the keystone). Per the gate rule, green-but-not-pinning is a FAIL, not a pass.

### Action Items

See the `### Review Findings` subsection above (1 Patch on `cost/resume.py`/`pipeline.py`, 1 Patch on
the test fixture, 1 Decision on the resumed halt-report `assessed_files` re-derivation). No new defer
filed; the carry-watches (DF-1-3-A / DF-1-7-A / DF-1-3-B) correctly stay deferred. No frozen-surface
edits detected (the bug is in the new `cost/resume.py` + `pipeline.py` resume merge, in scope).
