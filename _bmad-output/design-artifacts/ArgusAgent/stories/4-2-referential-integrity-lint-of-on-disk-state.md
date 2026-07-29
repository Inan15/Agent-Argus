# Story 4.2: Referential-integrity lint of on-disk state — [Tier B]

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/APAA/`; the tracker is `_bmad-output/design-artifacts/APAA/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As an APAA maintainer (and downstream of resumability + evidence-bundle export),
I want a **referential-integrity lint** that verifies the on-disk `.apaa/` state is **internally consistent**
— every cross-reference resolves (a finding/recording referenced by run-state exists; the envelope
`prev_hash` chain is intact; a content-addressed filename matches its internal `content_hash`; a partition /
assignment id referenced by the plan resolves; no dangling, orphaned, or broken locators) —
so that **resumability (Story 3.4) and the evidence bundle (Story 4.3) are built on a store proven
internally consistent**, and a corrupted / partially-written / misfiled `.apaa/` tree surfaces as a **typed
integrity finding, never a crash and never a silently-wrong resume or a leaky bundle** — the SECOND story of
Epic 4 (Negative-Assurance Verdict & Evidence Bundle, Tier-B), building on the done Story 4.1 wrapper +
the persisted `CriticalSubsystemSet`, and the structural complement to the Story 1.3 content-hash tamper
guard (`StoreIntegrityError`).

## Story Context

This is **Story 2 of Epic 4** (Negative-Assurance Verdict & Evidence Bundle, Tier-B — the "evidence you can
show a regulator" layer, PRD Journey 4). epic-4 is ALREADY `in-progress` (flipped by Story 4.1). It builds on
the fully-done Epics 1+2+3 (661 passed at the Epic-3 retro) + the done Story 4.1 (694 passed; the
negative-assurance wrapper + the persisted computed `CriticalSubsystemSet`). It is the **referential-integrity
lint** story (FR26 / NFR-A2, `[Tier B]`).

**The store these references live in ALREADY ships — this story is a READ-ONLY structural LINT over it.** The
`.apaa/` tree, its envelopes, and the cross-references the lint checks are all produced by the done spine. The
net-new is a PURE structural integrity checker that walks the persisted tree and proves every cross-reference
resolves. The honesty surface this lint reasons over already exists and is frozen:

- **Story 1.1 (done) — `store/envelope.py` (REUSE verbatim, do NOT edit).** The frozen `Envelope`
  (`schema_version`, `producer`, `apaa_version`, `content_hash`, `prev_hash`, `payload`, volatile
  `run_id`/`created_at`). `content_hash = sha256(canonical.dumps_bytes(payload))` over the **payload only**
  (NFR-D3). `prev_hash` chains to the prior envelope's `content_hash`; the chain head uses
  `GENESIS_PREV_HASH = "0"*64`. **`compute_content_hash(payload)` is the canonical recompute the lint REUSES
  to verify a content-addressed filename matches its internal `content_hash`** (the DF-1-3-A check — see
  Carry-Forward). The lint READS these; it does NOT change the envelope contract.
- **Story 1.3 (done) — `store/reader.py::ApaaStoreReader` + `StoreIntegrityError` (REUSE verbatim, do NOT
  edit).** `read_envelope(locator, *, verify_hash=True)` already RE-VERIFIES the `content_hash` against a hash
  recomputed over the loaded payload and raises `StoreIntegrityError` (a `ValueError` subclass) on a mismatch
  — **the CONTENT-HASH TAMPER guard.** The lint REUSES `read_envelope` to load + validate + tamper-check every
  envelope it walks. **This story's lint is COMPLEMENTARY, not a duplicate:** 1.3's `StoreIntegrityError`
  catches a payload mutated WITHOUT re-hashing (per-artifact content tamper); THIS lint catches
  REFERENTIAL/STRUCTURAL breakage ACROSS artifacts (a dangling reference, a broken `prev_hash` chain link, a
  filename-vs-`content_hash` mismatch, an orphaned artifact) — the two guards together prove both per-artifact
  content integrity AND inter-artifact referential integrity. **REUSE `StoreIntegrityError` from 1.3 — do NOT
  mint a second tamper-error type; this story adds an INTEGRITY-FINDING surface, not a second tamper error**
  (lock the relationship: a tamper detected during the walk surfaces as one class of integrity finding, never
  an uncaught raise — AR10).
- **Story 1.3 (done) — `store/paths.py::ApaaStorePaths` (REUSE verbatim, do NOT edit).** The
  containment-checked resolver — `resolve` / `to_locator` / the fixed
  `APAA_SUBDIRS = ("state","assignments","findings","decisions","cache")`. The lint enumerates locators
  THROUGH this resolver (every read is containment-checked, NFR-S5). The lint's directory walk REUSES the
  `_list_locators(reader, subdir)` enumeration pattern (`pipeline.py:893-903`: `sorted(.../*.json)` — AR11
  sorted, deterministic) — do NOT fork a second enumerator.
- **Story 1.2 (done) — `ledger/recording.py::Recording` + `coverage_ledger.py::CoverageLedger`/
  `CoverageLedgerEntry` (REUSE verbatim, do NOT edit).** The frozen recording (the `findings/` payload — each
  carries `recording_id` (= `finding_id`), `rule_id`, `locators`) and the coverage ledger (the run-state
  `payload["ledger"]`). The lint resolves run-state → ledger → entries and run-state/verdict → findings
  cross-references over these frozen shapes.
- **Story 2.4 (done) — `index/partitioner.py` (PartitionPlan / Partition / `work_manifest` /
  `partition_id`).** The partition-plan snapshot (`state/`) references partition ids; each partition's
  `work_manifest` is persisted at `assignments/<partition_id>.json` (content-derived id — AR11). The lint
  checks that each `partition_id` the plan references resolves to an `assignments/` artifact (and vice-versa —
  no orphaned assignment).
- **Story 4.1 (done) — `verdict/negative_assurance.py` + the persisted `CriticalSubsystemSet`.** The 4.1
  wrapper + the computed `CriticalSubsystemSet` are additive `state/` artifacts (producers
  `apaa.verdict.negative_assurance` / `apaa.pipeline.critical_subsystems`). The lint treats them as
  walk-targets in the chain + producer-typed integrity checks — but does NOT change them.
- **Story 3.4 (done) — `pipeline.py::_read_prior_state` + `_list_locators` (READ-ONLY reference pattern).**
  The resume path ALREADY enumerates `state/` + `findings/` envelopes (sorted), reads each via the
  tamper-guarded `read_envelope`, and selects by PRODUCER token (`_STATE_PRODUCER`,
  `_HALT_REPORT_PRODUCER`, `_FINDING_PRODUCER`, …). **The lint mirrors this READ discipline (sorted
  enumeration + per-envelope tamper-guarded read + producer-token classification) — REUSE the
  `_list_locators` pattern + the producer-token constants; do NOT fork a second producer registry.** The
  pipeline producer tokens (`pipeline.py:172-199`) are the authoritative producer set the lint classifies
  against.

**The net-new deliverable of THIS story.** A scope-thin, PURE-CORE referential-integrity LINT over the
on-disk `.apaa/` tree + a typed integrity-finding surface + its e2e proof:

1. a new module **`minions_core/apaa/store/integrity.py`** (cohesive with the `store/` spine it lints — the
   reader/paths/envelope it reuses all live here; architecture §store sub-package). It carries:
   - a frozen **`IntegrityFinding`** Pydantic v2 model (`frozen=True, extra="forbid"`, localized
     `schema_version`) — a TYPED finding (NOT a raw string): a closed-enum `kind`
     (e.g. `dangling_reference` | `broken_prev_hash_chain` | `filename_content_hash_mismatch` |
     `orphaned_artifact` | `unreadable_artifact` | `content_hash_tamper` | `missing_referent`), the offending
     **repo-relative POSIX `locator`** (never an absolute host path — NFR-S1), an optional `referent`
     (the unresolved target locator/id, repo-relative / id-only), the `producer` of the offending artifact,
     and a deterministic `detail: str` message that names ONLY locators/ids/kinds — never source/secret/payload
     bytes (NFR-S1). NO `float` anywhere;
   - a frozen **`IntegrityReport`** Pydantic v2 model (`frozen=True, extra="forbid"`) — the sorted tuple of
     `IntegrityFinding`s + a `consistent: bool` (= the findings tuple is empty) + per-kind counts (`int`).
     Sorted deterministically (by `(kind, locator, referent)`) so the report is byte-stable / order-independent
     (NFR-P1);
   - a **(mostly) PURE lint engine** — `lint_referential_integrity(reader: ApaaStoreReader) -> IntegrityReport`
     (or a pure `lint_*` core over a pre-read in-memory artifact set + a thin impure enumerate-and-read shell):
     the IMPURE part is enumerating + reading the `.apaa/` bytes through the 1.3 reader (the resumability read
     primitive — AR8 permits the read off disk); the PURE part is the cross-reference resolution. **A broken
     reference is a typed `IntegrityFinding` in the report — NEVER a raised exception** (the keystone: the lint
     reports breakage, it does not crash on it — AR10 / FR26 second AC). The ONLY raises are for a programmer
     error (a non-`ApaaStoreReader` argument → a typed `IntegrityLintError`, a `ValueError` subclass mirroring
     `StoreIntegrityError` / `ExhaustionError`);
2. the **reference graph the lint resolves** (locked from the persisted spine):
   - **(a) `prev_hash` chain integrity (NFR-A1)** — every envelope's `prev_hash` either equals
     `GENESIS_PREV_HASH` (the chain head) OR equals the `content_hash` of some OTHER envelope present in the
     tree; a `prev_hash` that points to no present envelope (and is not genesis) → a `broken_prev_hash_chain`
     finding. (V1 chain-shape note locked in Dev Notes: APAA writes are content-addressed and each
     `write_payload` defaults `prev_hash=GENESIS` unless explicitly chained — so the V1 lint asserts every
     non-genesis `prev_hash` RESOLVES to a present envelope's `content_hash`, not a single total linear order;
     a non-resolving non-genesis `prev_hash` is the breakage class. Lock the exact V1 chain semantics in Dev
     Notes against the actual writer behavior — do NOT assume a stricter chain than the spine produces);
   - **(b) content-addressed filename ↔ `content_hash` (DF-1-3-A closure — see Carry-Forward)** — for every
     content-addressed `<sha>.json` artifact (the `state/` + `findings/` content-addressed shape), the filename
     stem MUST equal the envelope's internal `content_hash` (recomputed/verified via 1.3's `read_envelope`); a
     mismatch → a `filename_content_hash_mismatch` finding (a renamed/misfiled artifact). Assignment manifests
     (`assignments/<partition_id>.json`) are keyed by a stable content-derived id, NOT a sha — so they are
     EXCLUDED from the sha-stem check (lock this distinction; an assignment id is checked by the
     partition-reference resolution in (d), not by sha-stem equality);
   - **(c) run-state → findings/ledger references (FR26 "finding→ledger entry")** — the run-state envelope's
     ledger (`payload["ledger"]`) entries + the verdict's `ordered_findings` reference `recording_id`s /
     file paths; a referenced `recording_id` that resolves to no present `findings/` `Recording` → a
     `dangling_reference` / `missing_referent` finding; a `findings/` `Recording` referenced by NO present
     run-state/verdict → an `orphaned_artifact` finding (lock the orphan policy in Dev Notes: V1 reports an
     orphan as an integrity finding — a finding with no referencing run-state is dangling state; confirm the
     exact reference shape against the real persisted run-state payload before locking the resolver);
   - **(d) partition-plan → assignment references (FR26 "decision→assignment" generalized; the V1 analog)** —
     the partition-plan snapshot references `partition_id`s; each MUST resolve to a present
     `assignments/<partition_id>.json`; a referenced id with no assignment → `dangling_reference`; an
     `assignments/` artifact referenced by no plan → `orphaned_artifact`. **Decision artifacts
     (`decisions/`) do not exist in V1 (FR24 / `governance/decision_record.py` is Epic 6) — the lint's
     decision→assignment check is SCOPED to the V1 partition→assignment analog; the literal FR26
     "decision→assignment" landing is fenced to Epic 6 when `decisions/` artifacts ship.** Lock this fence
     explicitly so the lint does not invent a decision reference that has no V1 producer;
   - **(e) unreadable / tamper artifacts** — an artifact whose `read_envelope` raises (a 1.3
     `StoreIntegrityError` content-hash tamper, a `CanonicalSerializationError` corrupt/non-UTF-8/non-JSON, a
     `pydantic.ValidationError` unknown-field/bad-shape) → a typed integrity finding (`content_hash_tamper` /
     `unreadable_artifact`), NEVER an uncaught raise (the lint catches the typed read errors at the
     enumerate-and-read shell and converts each to a finding — the FR26 second AC "surfaces as a typed
     integrity finding, not a crash");
3. **NO pipeline auto-wiring REQUIRED by this story (lock the decision).** The lint is a standalone READ-ONLY
   tool over an existing `.apaa/` tree (the architecture frames it as an integrity check, not a per-run
   pipeline stage). The DEFAULT decision (DN-WIRING): the lint is a library + a thin invocation surface
   exercised by tests + (optionally) reused by the resume path / evidence bundle in LATER stories — it does
   NOT add a mandatory pipeline persistence stage, a new HTTP route, or a `cli.py` subcommand in THIS story
   (DF-3-4-A `--resume` / a `--lint` CLI flag stay deferred). If a thin opt-in CLI or a resume-precondition
   wiring is genuinely warranted, prefer to FENCE it to 4.3 (the evidence bundle is the natural consumer of
   "is this store consistent before I export it") — but the testable deliverable is the LINT + its report, not
   a wiring;
4. **the keystone proof (AI-E3-1 keystone-fixture-adequacy — apply FIRST):** the lint's keystone tests MUST
   **actually plant a broken reference and prove it is caught** (a dangling `recording_id`, a broken
   `prev_hash` link, a renamed `<sha>.json` whose stem no longer matches its `content_hash`, an orphaned
   `findings/` artifact, a tampered envelope) AND prove an INTACT store passes (`consistent=True`, empty
   findings) AND prove a broken reference is a TYPED FINDING, not a crash. Each keystone fixture must be
   demonstrated RED against a deliberate detector-weakening before it is trusted (drop the chain check →
   the broken-chain test FAILS; drop the sha-stem check → the renamed-artifact test FAILS);
5. **byte-identity / determinism discipline** — the `IntegrityReport` is a pure deterministic function of the
   on-disk artifact set (sorted findings, no clock/uuid/random, no float, no set/dict iteration-order
   reliance), so the same `.apaa/` tree always lints to the same report (NFR-P1). The lint READS only — it
   NEVER writes to `.apaa/` (no new artifact, no mutation; CC-4 read-only spirit).

The `IntegrityFinding`/`IntegrityReport` models + the cross-reference resolution core are PURE (AR8) and join
the import-isolation gate. The enumerate-and-read of `.apaa/` bytes is the impure shell (the 1.3 reader).

**Carry-forward from the Epic-3 retro (2026-06-27) + the 4.1 discharge (CLAUDE.md §9.1 / L1-E11).** Each item
below is an Epic-4-backlog action item this story discharges (per the L1-E11 operating model).
- **AI-E3-1 (test-infra 🟠) — keystone-fixture-adequacy practice (the marquee Epic-3 lesson; apply FIRST to
  4.2).** The 3.4 review FAIL was a green keystone test that structurally COULD NOT catch its keystone bug.
  **For this lint's keystone tests, the fixture MUST contain a REAL planted broken reference of EVERY class the
  lint claims to detect, AND the test MUST be demonstrated RED against a deliberate detector-weakening before
  it is trusted.** Concretely: (a) the "dangling-reference-detected" assertion must plant a run-state/verdict
  referencing a `recording_id` with NO matching `findings/` artifact, and go RED if the resolver is weakened to
  skip the existence check; (b) the "broken `prev_hash` chain" assertion must plant an envelope whose
  non-genesis `prev_hash` resolves to no present envelope, and go RED if the chain check is dropped; (c) the
  "filename ↔ content_hash mismatch" assertion must RENAME a `<sha>.json` so its stem diverges from its
  internal `content_hash`, and go RED if the sha-stem check is dropped; (d) the "intact-chain-passes" assertion
  must run over a REAL pipeline-produced `.apaa/` tree (a full `run_audit` output) and assert `consistent=True`
  / empty findings (the false-positive floor — the lint must NOT cry wolf on a genuinely consistent store);
  (e) the "broken-reference-is-a-typed-finding-not-a-crash" assertion must plant a tampered/corrupt artifact
  and assert the lint RETURNS a report with the finding, never raises. Document the RED-then-green
  demonstration in Completion Notes.
- **AI-E3-3 (governance 🟢) — central defer register.** If this story files a NEW defer, file it append-only in
  `_bmad-output/design-artifacts/APAA/deferred-work.md` (the single canonical APAA defer source), not only in
  the story file. **DF-1-3-A** (reader does not assert content-addressed filename == internal `content_hash`;
  `target_story: epic-4-secret-containment-property-suite-ci-blocking`) and **DF-1-3-B** (containment
  `_is_contained` mirrored not imported; `target_story: epic-4-referential-integrity-lint-of-on-disk-state` =
  THIS story) are both relevant. **This story's lint CLOSES the DF-1-3-A integrity GAP** (the
  filename ↔ `content_hash` mismatch check is exactly DF-1-3-A's suggested fix, now landed as a lint finding
  rather than a reader-time raise — append a closure/cross-reference note to DF-1-3-A's central-register entry,
  append-only, do NOT rewrite per §3.4). DF-1-3-B (the containment-logic parity test) is a 🟢 nice-to-have
  whose `target_story` names this story — if convenient and in-scope (the lint reuses `ApaaStorePaths`
  containment), add the parity test OR re-target/leave it open with a note; do NOT expand scope to chase it if
  it does not fit cleanly.
- **AI-E3-6 (process 🟢) — keep the three structural gates + the standing cross-env determinism suite.** Append
  the new `store/integrity.py` to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py` (extend, NOT
  fork); keep the single-serializer AST gate (`test_canonical_single_serializer.py`) green (any JSON the lint
  emits — if it persisted, which it does NOT in V1 — would go through `store/canonical.dumps`, never a direct
  `json.dumps`); apply byte-stability + order-independence fixtures to the report surface; apply the 3.5
  cross-env discipline (sorted, float-free, clock-free) to the report.
- **AI-E3-2 / AI-E2-1 (process 🟠) — pre-`review` mandatory-test-existence guard.** This story does NOT flip
  `status: review` until ALL mandatory test files
  (`tests/apaa/test_store_integrity_lint.py`, the e2e intact-store assertion in
  `test_pipeline_signature_demo.py` or a dedicated e2e, the import-isolation extension) EXIST and pass; the Dev
  Agent Record is filled completely (no blank placeholders). Treat the test-existence precondition as a hard
  gate on the `review` flip.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 4.2) + the architecture / PRD. Drivers: **APAA-FR-26** (verify
> referential integrity of on-disk state — no dangling references — the CENTRAL driver), **APAA-NFR-A2**
> (referential integrity of on-disk state is verifiable — no dangling references; `[Tier B]`), **APAA-NFR-A1**
> (the schema-versioned, content-hashed, **prev-hash-chained** envelope the chain-integrity check walks),
> **APAA-FR-25** (the content-hashed envelope whose `content_hash` the filename-stem check verifies),
> **APAA-NFR-D3** (the content hash covers the canonical payload ONLY — the lint recomputes over the payload,
> never the volatile `run_id`/`created_at`), **APAA-NFR-D2** (deterministic, zero-LLM-token — the cross-reference
> resolution is a pure fold over the read artifacts), **APAA-NFR-P1** (byte-identical / order-independent
> report for the same `.apaa/` tree; no float; sorted findings), **APAA-NFR-S1** (no source / secret /
> absolute-host-path bytes in any integrity finding — only repo-relative locators / ids / kinds),
> **APAA-NFR-S5** (every read is containment-checked via the 1.3 `ApaaStorePaths` shell),
> **APAA-NFR-R1/FR-14** (a tool/parse failure or a broken reference degrades to a recorded finding — never an
> uncaught crash), **APAA-NFR-M1** (≤1200-line files), **APAA-NFR-M2** (frozen, schema-versioned,
> additive-only contracts), **AR4** (no `float`; single canonical serializer; no clock/uuid/random/
> iteration-order — content-derived, AR11 sorted), **AR8** (pure/impure separation — the models +
> cross-reference resolver are PURE; the enumerate-and-read of `.apaa/` bytes is the impure 1.3 reader shell),
> **AR10** (typed failure for a programmer error, never an uncaught raise; a broken reference is a FINDING not
> a raise), **AR11** (`.apaa/` enumeration is sorted/deterministic; filenames content-derived).
>
> **SCOPE FENCE — Tier-B, single-purpose.** This story delivers ONLY: (1) the referential-integrity LINT —
> a new `store/integrity.py` with a PURE cross-reference resolver + a frozen `IntegrityFinding` /
> `IntegrityReport` surface that walks the persisted `.apaa/` tree and proves every cross-reference resolves
> (prev_hash chain, content-addressed filename ↔ `content_hash`, run-state→findings/ledger, plan→assignment,
> unreadable/tamper); (2) the typed-finding-not-a-crash contract (a broken reference is an `IntegrityFinding`,
> never a raise); (3) the DF-1-3-A integrity-gap closure (filename ↔ `content_hash` mismatch as a lint
> finding); (4) the keystone proofs (dangling-detected / intact-passes / broken-is-a-typed-finding,
> AI-E3-1 RED-then-green); (5) the import-isolation + byte-stability + order-independence discipline. It does
> NOT build, and MUST NOT pull forward: the **evidence-bundle export** (FR29 — **Story 4.3**, the natural
> consumer of "is this store consistent before export"); the **CI-blocking secret-containment property suite**
> (FR28 enforcement / NFR-S1 / AR9 — **Story 4.4**); the **append-only decision record** / `decisions/`
> artifacts (FR24 — Epic 6 — so the literal FR26 "decision→assignment" reference is fenced to Epic 6 when
> `decisions/` ship; V1 lints the partition→assignment analog); the **adversarial Prosecutor** (FR19 — Epic 6);
> ANY change to the **1.1 envelope / 1.3 reader+paths+`StoreIntegrityError` / 1.2 recording+ledger / 2.4
> partitioner / 4.1 wrapper+critical-set** frozen contracts (all reused verbatim); a **second tamper-error
> type** (REUSE 1.3 `StoreIntegrityError`); a **second serializer / enumerator / producer registry**. It does
> NOT add a NEW HTTP route / FastAPI surface / UI (§3.7), and does NOT add a mandatory pipeline stage or a
> `cli.py` subcommand (DN-WIRING — the lint is a standalone read-only library in V1). It does NOT WRITE to
> `.apaa/` (read-only — no new artifact, no mutation). Lint the store, report the breakage as typed findings,
> prove it catches a real planted break, then stop.

**AC1 — The lint walks the `.apaa/` tree and reports an `IntegrityReport` over the resolved reference graph (FR26, NFR-A2)**
**Given** an `.apaa/` tree on disk (produced by a real `run_audit`) accessed via the 1.3 `ApaaStoreReader`
**When** `lint_referential_integrity(reader)` runs
**Then** `store/integrity.py` enumerates the `.apaa/` artifacts (sorted, through the 1.3
`_list_locators`-style containment-checked enumeration — AR11), reads each via the tamper-guarded
`read_envelope`, and resolves the reference graph: (a) **prev_hash chain** — every non-genesis `prev_hash`
resolves to a present envelope's `content_hash`; (b) **content-addressed filename** — every `<sha>.json`
artifact's filename stem equals its internal `content_hash`; (c) **run-state → findings/ledger** — every
`recording_id` / referenced entry the run-state + verdict point at resolves to a present artifact; (d)
**plan → assignment** — every `partition_id` the plan references resolves to a present
`assignments/<partition_id>.json`
**And** it returns a frozen `IntegrityReport` carrying the SORTED tuple of `IntegrityFinding`s + `consistent:
bool` (empty findings ⇒ `True`) + per-kind counts — over in-memory resolved references (the resolution is
PURE; only the byte read is impure).

**AC2 — An intact, genuinely-consistent store passes with no false positives (the false-positive floor; intact-chain-passes keystone)**
**Given** an `.apaa/` tree produced by a complete `run_audit` (a real verdict + findings + run-state +
partition plan + assignments + cost ledger + halt report + the 4.1 wrapper + the persisted
`CriticalSubsystemSet`) on which NOTHING has been tampered
**When** the lint runs
**Then** `consistent=True`, the findings tuple is EMPTY, and every per-kind count is `0` — the lint does NOT
cry wolf on a genuinely consistent store (every reference the real spine writes resolves)
**And** this is demonstrated over a REAL pipeline-produced tree (not a hand-built fixture), proving the lint's
reference model matches what the spine actually persists (AI-E3-1: an intact-passes assertion is as load-bearing
as a break-detected one — a lint that flags a consistent store is as broken as one that misses a break).

**AC3 — A dangling reference is detected (dangling-reference-detected keystone, FR26, NFR-A2)**
**Given** an `.apaa/` tree where a cross-reference does NOT resolve — e.g. a run-state/verdict referencing a
`recording_id` whose `findings/` artifact is absent (deleted / never written), OR a partition plan referencing
a `partition_id` with no `assignments/<partition_id>.json`
**When** the lint runs
**Then** it emits an `IntegrityFinding` of `kind ∈ {dangling_reference, missing_referent}` naming the offending
`locator` + the unresolved `referent` (the missing `recording_id` / `partition_id`), `consistent=False`, and
the per-kind count reflects it
**And** this is demonstrated RED against a deliberate detector-weakening (drop the run-state→findings existence
check → the dangling-reference test FAILS), then green (AI-E3-1) — the fixture PLANTS a real dangling
reference (deletes/omits the referent artifact), it does not merely assert over a synthetic in-memory graph.

**AC4 — A broken `prev_hash` chain link and an orphaned artifact are detected (NFR-A1, FR26)**
**Given** an `.apaa/` tree where an envelope's non-genesis `prev_hash` resolves to NO present envelope (a
broken chain link), AND/OR a `findings/` or `assignments/` artifact is referenced by no present run-state/plan
(an orphan)
**When** the lint runs
**Then** the broken chain link surfaces as a `broken_prev_hash_chain` finding (naming the offending envelope
locator + the unresolved `prev_hash`), and the orphan surfaces as an `orphaned_artifact` finding (naming the
unreferenced locator); `consistent=False`
**And** the broken-chain detection is demonstrated RED if the chain check is dropped, then green (AI-E3-1); the
V1 chain semantics (every non-genesis `prev_hash` must resolve to a present `content_hash`; genesis is the
allowed head) are LOCKED in the module docstring against the actual writer behavior (do NOT assume a stricter
single-linear-chain than the content-addressed spine produces).

**AC5 — A content-addressed filename that does not match its internal `content_hash` is detected (DF-1-3-A closure, FR25, NFR-D3, AR11)**
**Given** an `.apaa/` tree where a content-addressed `<sha>.json` artifact has been RENAMED so its filename
stem no longer equals its internal envelope `content_hash` (a misfiled / renamed artifact — the DF-1-3-A gap)
**When** the lint runs
**Then** it emits a `filename_content_hash_mismatch` finding naming the offending locator (the recompute REUSES
1.3's `read_envelope` / `compute_content_hash` over the payload only — NFR-D3); `consistent=False`
**And** assignment manifests (`assignments/<partition_id>.json`, keyed by a stable content-derived id, NOT a
sha) are EXCLUDED from the sha-stem check (an assignment id is verified by the plan→assignment resolution in
AC1(d), not by sha equality) — so the lint does not false-positive on a legitimately non-sha-named assignment;
this distinction is demonstrated by a test (a real assignment artifact does NOT trip the mismatch check)
**And** the DF-1-3-A central-register entry gets an append-only closure/cross-reference note (the integrity gap
DF-1-3-A flagged is closed by this lint finding — §3.4 append-only, do NOT rewrite the original entry).

**AC6 — A broken reference / tamper / corrupt artifact is a TYPED FINDING, not a crash (FR26 second AC, NFR-R1, AR10 — the no-crash keystone)**
**Given** an `.apaa/` tree containing an artifact that fails to read — a 1.3 `StoreIntegrityError` (content-hash
tamper: payload mutated without re-hashing), a `CanonicalSerializationError` (corrupt / non-UTF-8 / non-JSON
bytes), or a `pydantic.ValidationError` (unknown field / bad shape)
**When** the lint runs
**Then** the lint CATCHES the typed read error at the enumerate-and-read shell and converts it to an
`IntegrityFinding` (`kind ∈ {content_hash_tamper, unreadable_artifact}`) naming the offending locator + the
error class token (NEVER the file content / payload bytes — NFR-S1) — it RETURNS an `IntegrityReport` with the
finding and `consistent=False`, it NEVER raises out of the lint (FR26 "surfaces as a typed integrity finding,
not a crash"); the ONLY raise is a typed `IntegrityLintError` (a `ValueError` subclass mirroring
`StoreIntegrityError`) for a PROGRAMMER error (a non-`ApaaStoreReader` argument)
**And** this is demonstrated RED-then-green (AI-E3-1): plant a tampered envelope (mutate the payload, keep the
stale `content_hash`) and a corrupt-bytes artifact; assert the lint returns a report containing the
typed findings and does NOT raise (and go RED if the lint is weakened to let a read error propagate). The
lint REUSES the 1.3 `StoreIntegrityError` — it does NOT mint a second tamper-error type.

**AC7 — The new pure logic is PURE, frozen-contract, deterministic, secret-safe, import-isolated; the whole suite green; mypy clean; ≤1200 lines (NFR-D2, NFR-P1, NFR-S1, AR8, AR10, M1, M2)**
**Given** the new `IntegrityFinding` / `IntegrityReport` models + the cross-reference resolution core in
`minions_core/apaa/store/integrity.py`
**When** they are imported and exercised in unit tests
**Then** the resolution core + the model builds perform NO clock read (`datetime.now`/`time.time`), NO
`uuid4`/`os.getpid()`/`random`, NO LLM/network call, NO dict/`set`-iteration-order reliance — they are PURE
over the in-memory read-artifact set (the ONLY I/O is the impure enumerate-and-read of `.apaa/` bytes through
the 1.3 reader, the resumability read primitive — AR8); the lint NEVER WRITES to `.apaa/` (read-only)
**And** the new models are frozen Pydantic v2 (`frozen=True, extra="forbid"`, localized `schema_version` — the
1.1/1.2/1.6/4.1 precedent); NO `float` anywhere (counts are `int`; flags are `bool`; locators/kinds/details are
`str`); any JSON rendering (if ever persisted — it is NOT in V1) routes through `store/canonical.dumps` (single
1.1 serializer — no second `json.dumps`); the report findings are SORTED deterministically (by
`(kind, locator, referent)`) so the report is byte-stable + order-independent across enumeration order
**And** no integrity finding contains a source / secret / absolute-host-path byte — only repo-relative POSIX
locators, ids, and closed-enum kind/error tokens (verified by an AI-E1-1-style assertion that no source /
secret / absolute-host-path byte appears in the serialized report, and a non-ASCII café/Cyrillic file path in a
locator round-trips intact)
**And** a malformed input (a non-`ApaaStoreReader` argument) raises a typed `IntegrityLintError` (a `ValueError`
subclass) — never a silent coerce / bare `except: pass` / `print()` in library code (AR10); a broken
reference / tamper / corrupt artifact is a FINDING, never a raise (AC6)
**And** the new module is appended to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py` (extend, do
NOT fork) and importing it does NOT transitively import `fastapi`/`uvicorn`/`starlette` or any LLM/api module
(assert absence from `sys.modules`)
**And** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` passes (including the
new `tests/apaa/test_store_integrity_lint.py`: AC1 the report shape over a real tree; AC2 intact-store-passes
[over a real pipeline tree]; AC3 dangling-reference-detected [demonstrated RED]; AC4 broken-prev_hash-chain +
orphaned-artifact [chain check demonstrated RED]; AC5 filename↔content_hash mismatch [+ assignment-excluded
control]; AC6 tamper/corrupt → typed-finding-not-a-crash [demonstrated RED]; AC7 purity [AST scan] / frozen /
typed-error / single serializer / FastAPI-free import / order-independence + byte-stability / secret-safe
[non-ASCII locator round-trip; no abs-path/source/secret byte]); `mypy` is clean on the new + edited modules;
the new source file is ≤1200 lines (NFR-M1) and cites its `APAA-FR-26`/`APAA-NFR-A2`/`APAA-NFR-A1`/`AR*` drivers
in the module docstring. **Test area `APAA-STORE`** (`TC-APAA-STORE-001-NN` — the natural area for `store/`;
confirm/lock the next free index in the docstring, distinct from the existing `test_store_roundtrip.py` /
`test_containment.py` store tests) plus any e2e additions under `APAA-PIPELINE`. The 1.1 envelope / 1.3
reader+paths+`StoreIntegrityError` / 1.2 recording+ledger / 2.4 partitioner / 4.1 wrapper+critical-set
contracts are UNCHANGED (verify NO working-tree diff to those frozen surfaces). The mandatory test files MUST
exist + pass BEFORE the story flips to `status: review` (AI-E3-2 / AI-E2-1).

## Tasks / Subtasks

- [x] **Task 0 — Verify the existing reuse surface + LOCK the reference graph against the REAL persisted tree** (AC: 1, 2, 3, 4, 5)
  - [x] Re-read `store/envelope.py` — confirmed `Envelope` fields, `compute_content_hash(payload)`,
        `GENESIS_PREV_HASH`, the `prev_hash` chain contract. The lint READS this; NO working-tree diff verified.
  - [x] Re-read `store/reader.py` — confirmed `read_envelope(locator, *, verify_hash=True)` re-verifies the
        `content_hash` + `StoreIntegrityError`. REUSED both; no second tamper-error type. Re-read `store/paths.py`
        — confirmed `APAA_SUBDIRS` + `resolve`/`to_locator` containment.
  - [x] Re-read `pipeline.py:172-199` (producer tokens) + `_list_locators` + `_persist*` / `_assemble_and_persist`.
        Ran a REAL `run_audit` on `vacuous_basic` + inspected the produced `.apaa/` tree (locked below). The
        verdict envelope (`apaa.pipeline.verdict`) carries `ordered_findings[].recording_id`; the partition plan
        (`apaa.pipeline.partition_plan`) carries `partitions[].partition_id`; `findings/` are `apaa.pipeline.finding`
        Recordings; `assignments/<partition_id>.json` are `apaa.pipeline.work_manifest`. `decisions/` is EMPTY in V1.
  - [x] Re-read `ledger/recording.py` (`recording_id`) + `index/partitioner.py` (`PartitionPlan`/`partition_id`) —
        confirmed the exact reference field names the resolver reads.
- [x] **Task 1 — The frozen `IntegrityFinding` + `IntegrityReport` models + the typed `IntegrityLintError`** (AC: 1, 6, 7)
  - [x] `IntegrityFinding` (frozen, extra=forbid, localized `INTEGRITY_SCHEMA_VERSION`): closed-enum `kind`
        (`INTEGRITY_FINDING_KINDS`), repo-relative `locator`, optional `referent`/`producer`, deterministic
        `detail` (locators/ids/kinds only). NO float.
  - [x] `IntegrityReport` (frozen, extra=forbid): `findings` SORTED by `(kind, locator, referent)`, `consistent`,
        `counts_by_kind` (int per closed-enum kind). `IntegrityLintError` (ValueError subclass, programmer-error only).
  - [x] Module docstring cites `APAA-FR-26`/`NFR-A2`/`NFR-A1`/`AR4`/`AR8`/`AR10` + area `APAA-STORE`; documents
        the (a)→(e) reference graph + V1 chain semantics + the 1.3-complementary relationship + the `decisions/` fence.
- [x] **Task 2 — The lint engine: enumerate-and-read shell + PURE cross-reference resolver** (AC: 1, 3, 4, 5, 6)
  - [x] `lint_referential_integrity(reader)`: impure shell enumerates via the REUSED `_list_locators` sorted
        pattern + reads via `read_envelope`, CATCHING `StoreIntegrityError`/`CanonicalSerializationError`/
        `ValidationError`/`FileNotFoundError` per-artifact → typed finding (never propagated). Non-reader arg →
        `IntegrityLintError`.
  - [x] PURE `_resolve_references(artifacts, read_failures)` core over an in-memory `_ReadArtifact` set
        (zero-I/O testable). No clock/uuid/random; sorted findings; no float; the lint NEVER writes.
- [x] **Task 3 — Tests (AI-E3-1: plant a REAL break of every class + demonstrate RED before trusting)** (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] `tests/apaa/test_store_integrity_lint.py` (`APAA-STORE`, `TC-APAA-STORE-001-82..107`, 26 tests):
        AC2 intact-store-passes over REAL `run_audit` trees (vacuous_basic + clean_control); AC3 dangling
        finding + dangling assignment (+ RED via finding-existence-check-dropped resolver); AC4 broken-prev_hash
        (+ RED via chain-check-dropped) + orphaned assignment; AC5 filename↔content_hash mismatch (+ RED via
        sha-stem-check-dropped) + assignment-excluded control; AC6 tamper + corrupt-bytes + unknown-field →
        typed-finding-not-a-crash (+ RED via no-catch walk) + no-leak detail; AC7 typed-error / frozen / no-float /
        order-independence + byte-stability / AST purity scan / read-only / non-ASCII café/Cyrillic round-trip /
        no-abs-path / pure-zero-I/O resolver. Each keystone PLANTS a real on-disk break; the RED proof is the
        durable `_resolve_*_weakened` / `_walk_without_catching` helper in-test.
  - [~] (Optional e2e in `test_pipeline_signature_demo.py`) — NOT added; the AC2 intact-passes floor over a real
        `run_audit` tree already lives in `test_store_integrity_lint.py` (TC-...-82/83), so the optional extension
        would be redundant.
- [x] **Task 4 — Extend the import-isolation gate** (AC: 7)
  - [x] Appended `minions_core.apaa.store.integrity` to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py`
        (extend, not fork) — green (no web/LLM transitive import). Single-serializer AST gate stays green.
- [x] **Task 5 — Run + mypy + the defer-register closure + the pre-`review` test-existence precondition** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → 720 passed.
  - [x] `mypy` clean on `store/integrity.py` (Success: no issues found).
  - [x] **AI-E3-3:** appended an append-only INTEGRITY-GAP-CLOSED cross-reference note to the **DF-1-3-A** entry +
        a LEFT-OPEN note to **DF-1-3-B** in `deferred-work.md` (original entries NOT rewritten; §3.4). No NEW defer filed.
  - [x] **AI-E3-2 / AI-E2-1 GATE:** all mandatory test files exist + pass BEFORE the `review` flip; Dev Agent
        Record filled completely. NO working-tree diff to the frozen surfaces (verified via `git diff --name-only`:
        `store/{envelope,reader,paths}.py`, `ledger/{recording,coverage_ledger,critical_subsystems}.py`,
        `index/partitioner.py`, `verdict/negative_assurance.py` — all clean).

### Review Findings

<!-- defer-schema-session: 2026-06-27 -->

- [x] [Review][Patch] No-crash keystone leaks an uncaught `OSError` on a non-file `*.json` entry [minions_core/apaa/store/integrity.py:479-484] — The enumerate-and-read shell catches only `(StoreIntegrityError, canonical.CanonicalSerializationError, ValidationError, FileNotFoundError)`. `read_envelope` → `read_bytes` → `Path.read_bytes()` can raise other `OSError` subclasses that are NOT `FileNotFoundError`: `IsADirectoryError` (a directory named `<sha>.json` under `.apaa/state|findings|...`, e.g. an interrupted/partial write or a botched manual recovery) and `PermissionError`. `_list_locators` uses `directory.glob("*.json")`, which matches directories as well as files, so a directory entry IS enumerated and then read — crashing the lint. Reproduced: planting a `state/evil.json` **directory** on a real `vacuous_basic` `run_audit` tree raises `PermissionError` on Windows (`IsADirectoryError` on POSIX) out of `lint_referential_integrity`, instead of returning a report with an `unreadable_artifact` finding. This violates FR26 second AC / AC6 / AR10 ("a broken/misfiled on-disk state surfaces as a typed integrity finding, never a crash") — the exact keystone the lint exists to uphold. Suggested fix: broaden the shell catch to `OSError` (which subsumes `FileNotFoundError`, `IsADirectoryError`, `PermissionError`) — or add `OSError` alongside the existing four — so the per-artifact read converts to an `unreadable_artifact` finding; `_read_failure_finding` already handles the generic case (token = `type(exc).__name__`). NFR-S1 is preserved (the detail names only the locator + error-class token). Keep the typed `IntegrityLintError` programmer-error raise unchanged.
- [x] [Review][Patch] Add a planted-directory (non-file `*.json`) keystone test [tests/apaa/test_store_integrity_lint.py] — The AC6 suite plants tamper / corrupt-bytes / unknown-field breaks but does NOT plant a non-file `*.json` entry, so the `OSError`-escape gap above is uncovered and the green suite does not protect the keystone against it (this is precisely the AI-E3-1 lesson: a keystone test that structurally cannot catch a member of its own bug class). Add a test that creates a directory named `*.json` under `state/` on a real tree and asserts the lint RETURNS a report (`consistent=False`, an `unreadable_artifact` finding) and does NOT raise; demonstrate it RED against the current four-exception shell.



### Architecture patterns & constraints (the load-bearing rules)

- **The store + its references already ship — this is a READ-ONLY structural LINT, NOT a new producer (the
  scope crux).** Every artifact the lint walks is written by the done spine (`_persist*` /
  `_assemble_and_persist`). The net-new is the FR26/NFR-A2 referential-integrity checker: a thing that READS
  the `.apaa/` tree and proves every cross-reference resolves. **Do NOT re-implement the writer, the reader,
  the enumerator, or the producer registry.** REUSE `ApaaStoreReader.read_envelope` (tamper-guarded read),
  `ApaaStorePaths` (containment), `compute_content_hash` (payload-only recompute), the `_list_locators` sorted
  enumeration pattern, and the `pipeline.py` producer-token constants. **The lint WRITES NOTHING.**
- **This lint is COMPLEMENTARY to the 1.3 content-hash tamper guard — distinguish the two (the framing crux,
  FR26 vs FR25/NFR-D3).** 1.3's `StoreIntegrityError` (in `read_envelope`) catches a payload mutated WITHOUT
  re-hashing — a PER-ARTIFACT CONTENT tamper. THIS lint catches REFERENTIAL/STRUCTURAL breakage ACROSS
  artifacts — a dangling reference, a broken `prev_hash` chain link, a filename-vs-`content_hash` mismatch
  (a misfiled artifact), an orphaned artifact. The two are layers of the same trust substrate: content
  integrity (1.3) + referential integrity (4.2). The lint REUSES the 1.3 guard (a content tamper encountered
  during the walk becomes one `content_hash_tamper` integrity finding) — it does NOT fork a second tamper
  check or a second tamper-error type.
- **A broken reference is a typed FINDING, never a raise (the keystone, FR26 second AC / AR10 / NFR-R1).** The
  whole point of a lint is to REPORT breakage, not crash on it. The enumerate-and-read shell CATCHES the typed
  read errors (`StoreIntegrityError`, `CanonicalSerializationError`, `pydantic.ValidationError`,
  `FileNotFoundError`) per-artifact and converts each to an `IntegrityFinding`; the cross-reference resolver
  records each unresolved reference as a finding. The lint RETURNS an `IntegrityReport` — `consistent=False`
  with the findings — it does NOT raise out. The ONLY raise is a typed `IntegrityLintError` for a PROGRAMMER
  error (a non-`ApaaStoreReader` argument). ✅ `lint(...) -> IntegrityReport` with findings · ❌ `lint(...)`
  raising on a dangling reference.
- **Lock the reference graph against the REAL persisted tree — do NOT invent references (the correctness
  crux).** Before coding the resolver, run a real `run_audit` and INSPECT the produced `.apaa/` tree. The V1
  references that actually exist: (a) `prev_hash` on every envelope; (b) the `<sha>.json` filename on every
  content-addressed artifact; (c) the run-state `payload["ledger"]` entries + the verdict `ordered_findings`
  pointing at `recording_id`s / file paths in `findings/`; (d) the partition plan's `partition_id`s pointing
  at `assignments/<partition_id>.json`. **`decisions/` is EMPTY in V1** (FR24 / `governance/decision_record.py`
  is Epic 6), so the literal FR26 "decision→assignment" reference has NO V1 producer — the V1 lint checks the
  partition→assignment analog and FENCES the decision→assignment landing to Epic 6. Inventing a reference the
  spine does not write would make AC2 (intact-store-passes) fail on a genuinely consistent store.
- **V1 chain semantics: assert every non-genesis `prev_hash` RESOLVES, not a single linear order (the
  chain-shape crux, NFR-A1).** APAA writes are content-addressed and `write_payload` defaults
  `prev_hash=GENESIS_PREV_HASH` unless explicitly chained (`writer.py:111-118`). So the V1 tree is NOT
  necessarily a single total linear chain — multiple artifacts may be genesis-headed. The V1 lint asserts:
  every envelope's `prev_hash` is EITHER `GENESIS_PREV_HASH` OR equals some PRESENT envelope's `content_hash`;
  a non-genesis `prev_hash` resolving to no present envelope is the `broken_prev_hash_chain` breakage class.
  **Lock the exact chain semantics in the module docstring against the actual writer behavior** — do NOT
  assert a stricter chain than the spine produces (that would false-positive AC2).
- **No floats — ever (AR4/NFR-P1).** All report leaves are `str`/`int`/`bool`. Counts are `int`; flags are
  `bool`; locators/kinds/details/referents are `str`. The 1.1 serializer rejects `float` as the determinism
  backstop (the lint emits no float, so this is trivially satisfied — but keep it disciplined).
- **Determinism: sorted findings, no clock/uuid/random (NFR-P1, the 3.5 cross-env discipline).** The
  `IntegrityReport` is a pure deterministic function of the on-disk artifact set. The findings tuple is SORTED
  (by `(kind, locator, referent)`) so two enumeration orders yield a byte-identical report; the enumeration
  itself REUSES the `_list_locators` sorted pattern. No clock, no uuid, no random, no set/dict iteration-order
  reliance. The same `.apaa/` tree always lints to the same report.
- **Pure/impure separation (master rule, AR8).** The `IntegrityFinding`/`IntegrityReport` models + the
  `_resolve_references` cross-reference resolver are PURE — over an in-memory read-artifact set; they never
  open a file, read a clock, or call an LLM. The IMPURE shell is the enumerate-and-read of `.apaa/` bytes
  through the 1.3 `ApaaStoreReader` (the resumability read primitive — AR8 permits the byte read here). Split
  them so the resolver is testable with zero I/O (over a hand-built in-memory artifact set) AND the keystone
  tests plant REAL breaks on disk (AI-E3-1 requires a real planted break, not only the synthetic graph).
- **Secret/path safety (NFR-S1).** No integrity finding may contain a source / secret / absolute-host-path
  byte. Findings name ONLY repo-relative POSIX locators (from `to_locator`), ids (`recording_id`/
  `partition_id`), closed-enum kinds, and error-class tokens. The `detail` message is built from those tokens
  only — never the offending payload bytes, never the repo absolute path. Assert this with an AI-E1-1-style
  no-leak scan over the serialized report (and a non-ASCII café/Cyrillic locator round-trips intact).
- **DF-1-3-A closure is IN scope, by design (AI-E3-3).** DF-1-3-A flagged that the reader does not assert the
  content-addressed filename == the internal `content_hash` — a renamed/misfiled artifact is silently accepted.
  Its suggested fix is exactly this lint's `filename_content_hash_mismatch` check (landed as a lint finding,
  not a reader-time raise — keeping the 1.3 reader contract frozen). DF-1-3-A's `target_story` names Story 4.4,
  but its integrity GAP is naturally closed by THIS lint — append a closure/cross-reference note to its
  central-register entry (append-only, §3.4). DF-1-3-B (the containment-logic parity test) `target_story`s THIS
  story — address it if it fits cleanly, else leave it open with a note.
- **Wiring is OUT of scope in V1 — the lint is a standalone read-only library (DN-WIRING).** The architecture
  frames the integrity lint as a verifiable check, not a mandatory per-run pipeline stage. This story does NOT
  add a pipeline persistence stage, a new HTTP route, or a `cli.py` `--lint` subcommand. The natural CONSUMER
  of "is this store consistent before I act on it" is the evidence bundle (Story 4.3) and/or a resume
  precondition — FENCE any such wiring to 4.3, do NOT pull it forward. The testable deliverable is the LINT +
  its report.
- **The 4.3/4.4 work is OUT of scope (the primary downstream fences).** The evidence-bundle export (FR29) is
  **Story 4.3** — this lint proves the store is consistent so the bundle is built on solid ground, but it does
  NOT assemble the bundle. The CI-blocking randomized-canary secret-containment property suite (FR28/NFR-S1/
  AR9) is **Story 4.4** — this story's AI-E1-1-style no-secret-byte assertion is the per-story producer
  discipline, NOT the durable CI property suite. The Prosecutor (FR19) + HITL/decision-record (FR23/FR24) are
  Epic 6. If tempted to assemble a bundle / build a canary harness / add a decision reference — STOP.
- **Error/degradation → typed, never crash (AR10).** A programmer error (a non-`ApaaStoreReader` argument)
  raises a typed `IntegrityLintError` (a `ValueError` subclass localized to the module, mirroring
  `StoreIntegrityError`/`ExhaustionError`/`CriticalSubsystemError`) — never a silent coerce / bare
  `except: pass` / `print()` in library code. A broken reference / tamper / corrupt artifact is a FINDING in
  the returned report, never an uncaught traceback.

### Project Structure Notes

- **NEW module:** `minions_core/apaa/store/integrity.py` (cohesive with the `store/` spine it lints — the
  reader/paths/envelope it reuses all live in `store/`; architecture §store sub-package). PURE core + thin
  impure read shell — joins `_MODULES_UNDER_GUARD`. Budget the file ≤1200 lines (NFR-M1; it should be well
  under — a focused lint module).
- **REUSE verbatim (verify NO working-tree diff):** `store/envelope.py` (`Envelope` / `compute_content_hash` /
  `GENESIS_PREV_HASH`), `store/reader.py` (`ApaaStoreReader` / `read_envelope` / `StoreIntegrityError`),
  `store/paths.py` (`ApaaStorePaths` / `APAA_SUBDIRS`), `store/canonical.py` (the single serializer),
  `ledger/recording.py` (`Recording`/`recording_id`), `ledger/coverage_ledger.py`
  (`CoverageLedger`/`CoverageLedgerEntry`), `index/partitioner.py` (`PartitionPlan`/`partition_id`),
  `verdict/negative_assurance.py` (4.1 wrapper), `ledger/critical_subsystems.py` (`CriticalSubsystemSet`).
- **REUSE the pattern (do NOT fork):** `pipeline.py::_list_locators` (`pipeline.py:893-903` — sorted
  `*.json` enumeration), the producer-token constants (`pipeline.py:172-199`), `_read_prior_state`'s
  read-and-classify discipline (`pipeline.py:906-958`). If a producer-token or `_list_locators` reuse forces
  a circular import (`store/integrity.py` ← `pipeline.py`), prefer to define the lint's needed producer-token
  set as a small local constant mirrored from the authoritative pipeline set (document the mirror) OR consume
  the tokens by reading the envelope `producer` field directly — do NOT create a circular dependency; lock the
  chosen approach in Dev Notes.
- **NO pipeline.py change REQUIRED (DN-WIRING)** — if a thin e2e hook is added to
  `test_pipeline_signature_demo.py`, it imports + calls the lint, it does not modify `pipeline.py` persistence.
- **NEW tests:** `tests/apaa/test_store_integrity_lint.py` (`APAA-STORE` area, `TC-APAA-STORE-001-NN` — confirm
  the next free index; the existing `test_store_roundtrip.py` / `test_containment.py` are the other `store/`
  tests — lock the area + starting index in the new module docstring). Extend `tests/apaa/test_no_web_imports.py`
  (the `_MODULES_UNDER_GUARD` list) and optionally `tests/apaa/test_pipeline_signature_demo.py`.
- **No CLI change** (DF-3-4-A `--resume` / a `--lint` flag stay deferred — out of scope). No new HTTP route /
  FastAPI surface / UI (§3.7).

### References

- **Epic + ACs:** `_bmad-output/design-artifacts/APAA/epics.md#Story-4.2` (referential-integrity lint; FR26 /
  NFR-A2; `[Tier B]`); the Epic-4 framing (`epics.md:691-695`, "on-disk state is integrity-linted").
- **PRD drivers:** `_bmad-output/design-artifacts/APAA/E-PRD/prd.md` — FR26 (verify referential integrity of
  on-disk state — no dangling references; `epics.md:94/242`), NFR-A2 (referential integrity verifiable —
  `epics.md:133`), NFR-A1 (prev-hash-chained envelope), FR25/NFR-D3 (content-hashed payload-only envelope),
  NFR-S1/S5 (no leak / containment), NFR-R1/FR14 (failure → finding not crash), NFR-P1/D2 (determinism).
- **Architecture:** `architecture.md` §store sub-package (`architecture.md:430-435`), §envelope chain contract
  (`architecture.md:372`), §runtime artifact tree (`architecture.md:458-467`), AR4/AR8/AR10/AR11.
- **Reuse surface (read these — the load-bearing existing code):**
  `minions_core/apaa/store/envelope.py` (`compute_content_hash` / `GENESIS_PREV_HASH` / chain contract),
  `minions_core/apaa/store/reader.py` (`read_envelope` tamper guard / `StoreIntegrityError`),
  `minions_core/apaa/store/paths.py` (`ApaaStorePaths` / `APAA_SUBDIRS` / containment),
  `minions_core/apaa/pipeline.py:172-199` (producer tokens) + `:893-958` (`_list_locators` / `_read_prior_state`)
  + `:413-787` (`_persist*` / `_assemble_and_persist` — the reference graph source of truth),
  `minions_core/apaa/ledger/recording.py` (`recording_id`/`locators`),
  `minions_core/apaa/ledger/critical_subsystems.py`, `minions_core/apaa/index/partitioner.py`.
- **Prior story (learnings):** `_bmad-output/design-artifacts/APAA/stories/4-1-negative-assurance-verdict-semantics.md`
  (the 4.1 wrapper + the persisted `CriticalSubsystemSet`; the AI-E3-1 keystone-fixture-adequacy discipline
  applied at 4.1 — apply the SAME RED-then-green rigor here).
- **Defer register:** `_bmad-output/design-artifacts/APAA/deferred-work.md` — DF-1-3-A (filename↔`content_hash`,
  closed by this lint's finding), DF-1-3-B (containment parity, `target_story` = this story), DF-2-3-B
  (CLOSED by 4.1).
- **Project guidance:** `CLAUDE.md` §3.2 (≤1200 lines), §3.4 (evidence immutability / append-only), §3.7
  (headless-only), §9.1 (L1-E11 retro-action-items-as-backlog), §9.2 (rule-of-three guard promotion).

## Dev Agent Record

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, mode=implement) — 2026-06-27.
claude-opus-4-8 (BMAD dev-story, mode=fix — iteration 1, review-finding resolution) — 2026-06-27.

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/test_store_integrity_lint.py -q` → 26 passed (implement).
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → 720 passed in ~40s (implement).
- `PYTHONIOENCODING=utf-8 python -m mypy minions_core/apaa/store/integrity.py --ignore-missing-imports` → Success.
- `git diff --name-only` over the frozen surfaces → empty (no diff to envelope/reader/paths/recording/
  coverage_ledger/partitioner/negative_assurance/critical_subsystems).
- `store/integrity.py` = 438 non-blank lines (≤1200, NFR-M1).
- **(fix iter 1)** RED proof for the new planted-directory keystone: with the catch tuple reverted to the
  original four exceptions, `PYTHONIOENCODING=utf-8 python -m pytest
  tests/apaa/test_store_integrity_lint.py::test_non_file_json_entry_is_a_typed_finding_not_a_crash` →
  FAILED with `PermissionError` escaping `lint_referential_integrity` (the reproduced keystone bug).
- **(fix iter 1)** GREEN after broadening the shell catch to `OSError`: the same test → passed; full
  `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **721 passed in ~49s**
  (+1 = the new `test_non_file_json_entry_is_a_typed_finding_not_a_crash`); `mypy minions_core/apaa/store/integrity.py`
  → Success.

### Completion Notes List

- **Reference graph LOCKED against a REAL `run_audit` tree (the correctness crux).** Before coding the
  resolver I ran a real `run_audit` on `vacuous_basic` and inspected the produced `.apaa/` tree. Confirmed:
  (1) every V1 envelope is genesis-headed (`prev_hash = "0"*64`) — so V1 chain semantics = "every non-genesis
  `prev_hash` RESOLVES to a present `content_hash`", NOT a single linear chain (asserting stricter would
  false-positive AC2); (2) `state/` + `findings/` filename stem == `content_hash` (content-addressed), while
  `assignments/` stem == `partition_id` (NOT a payload sha → EXCLUDED from the sha-stem check); (3) the verdict
  envelope (`apaa.pipeline.verdict`) carries `ordered_findings[].recording_id` → resolved against `findings/`
  `apaa.pipeline.finding` Recordings; (4) the partition plan (`apaa.pipeline.partition_plan`) carries
  `partitions[].partition_id` → resolved against `assignments/<partition_id>.json`. `decisions/` is EMPTY in V1
  (FR24 = Epic 6) — the lint invents NO decision reference; the FR26 "decision→assignment" is fenced to Epic 6,
  V1 lints the partition→assignment analog.
- **COMPLEMENTARY to 1.3, not a duplicate.** The lint REUSES `read_envelope` (which raises `StoreIntegrityError`
  on a content-hash tamper) and converts that raise into one `content_hash_tamper` `IntegrityFinding` — no second
  tamper-error type, no second serializer/enumerator/producer-registry. Producer tokens are mirrored as small
  local constants (documented) to avoid a circular import (`store/integrity.py` ← `pipeline.py`); the lint
  classifies by reading the envelope `producer` field directly.
- **The keystone: a broken reference is a FINDING, never a raise.** The enumerate-and-read shell catches
  `StoreIntegrityError` / `CanonicalSerializationError` / `ValidationError` / `FileNotFoundError` per-artifact;
  the resolver records each unresolved reference. The lint RETURNS an `IntegrityReport` (`consistent=False`) and
  never raises out. The ONLY raise is `IntegrityLintError` for a non-`ApaaStoreReader` argument (AR10).
- **AI-E3-1 RED-then-green keystone-fixture-adequacy (applied FIRST).** Every keystone PLANTS a REAL on-disk
  break on a real `run_audit` tree (not a synthetic in-memory graph) AND is demonstrated RED. The RED proof is
  captured DURABLY in-test, not only narrated:
  - **AC3 dangling reference** (delete the `findings/` artifact the verdict references; delete the assignment the
    plan references) — RED via `_resolve_references_no_finding_existence` (a weakened resolver that drops the
    existence check MISSES the planted dangling reference); green via the real `_resolve_references`. (TC-...-85/86/87)
  - **AC4 broken `prev_hash` chain** (rewrite a `state/` envelope's `prev_hash` to a bogus non-genesis value,
    `content_hash` over the payload unchanged so the filename stem still matches → isolates the chain break) —
    RED via `_resolve_references_no_chain`; green via real. (TC-...-88/89) + orphaned assignment (TC-...-90).
  - **AC5 filename↔content_hash mismatch** (RENAME a `state/` `<sha>.json` to `0*64.json`) — RED via
    `_resolve_references_no_sha_stem`; green via real; PLUS the assignment-excluded control (an intact tree's
    real `assignments/<partition_id>.json` does NOT trip the sha-stem check). (TC-...-91/92/93)
  - **AC6 tamper/corrupt → typed-finding-not-a-crash** (mutate a payload with a stale `content_hash`; write
    non-JSON bytes; add an unknown envelope field with a recomputed hash so pydantic is the rejecting layer) —
    each RETURNS a report with the typed finding and does NOT raise; RED via `_walk_without_catching` (a no-catch
    walk that raises out). (TC-...-94/95/96/97/98)
  - **AC2 intact-store-passes false-positive floor** over REAL `run_audit` trees for BOTH `vacuous_basic` and
    `clean_control` (`consistent=True`, empty findings, all per-kind counts 0) — proving the lint's reference
    model matches what the spine actually persists and the lint does not cry wolf. (TC-...-82/83)
- **DF-1-3-A integrity GAP closed** — the filename↔`content_hash` check is exactly DF-1-3-A's suggested fix,
  landed as a LINT FINDING (keeping the 1.3 reader contract frozen). Append-only cross-reference note added to
  the central register; DF-1-3-B left open with a note (the lint reuses `ApaaStorePaths` containment but adds no
  new containment impl, so the parity test does not exercise a 4.2 code path — out of clean scope).
- **Determinism/secret-safety** — findings SORTED by `(kind, locator, referent)` (order-independent + byte-stable
  via the single 1.1 serializer); no float/clock/uuid/random (AST purity scan + import scan pinned); findings
  name only repo-relative locators/ids/kinds/error tokens (no abs-path/source/secret byte — non-ASCII
  café/Cyrillic locator round-trips intact; a planted leak token in corrupt bytes is ABSENT from the report).
- **Scope fences honored** — read-only (no `.apaa/` write); no pipeline stage / CLI / HTTP wiring (DN-WIRING;
  evidence-bundle consumer fenced to 4.3); no second tamper-type/serializer/enumerator/producer-registry; the
  4.4 secret-containment CI suite + Prosecutor/HITL/decision-record (Epic 6) are out of scope.

#### Fix iteration 1 (2026-06-27) — review-finding resolution (verdict FAIL → resolved)

- **[High][Patch] no-crash keystone OSError leak — RESOLVED.** The enumerate-and-read shell caught only
  `(StoreIntegrityError, CanonicalSerializationError, ValidationError, FileNotFoundError)`, so a non-file
  `*.json` entry under `.apaa/` (a DIRECTORY named `<sha>.json` from an interrupted/partial write or botched
  recovery, enumerated by `glob("*.json")` then read) raised `IsADirectoryError` (POSIX) / `PermissionError`
  (Windows) — both `OSError`-not-`FileNotFoundError` — escaping `lint_referential_integrity` as an uncaught
  crash, violating FR26 second AC / AC6 / AR10. **Fix:** broadened the shell catch from `FileNotFoundError` to
  `OSError`, which subsumes `FileNotFoundError` (raced-delete) + `IsADirectoryError` (non-file `*.json`) +
  `PermissionError`. `_read_failure_finding` already handles the generic case (`kind="unreadable_artifact"`,
  `token = type(exc).__name__`), so the non-file entry now converts to an `unreadable_artifact` finding.
  NFR-S1 preserved (the detail names only the locator + error-class token — no payload/path bytes). The typed
  `IntegrityLintError` programmer-error raise is unchanged. Module + `lint_referential_integrity` docstrings
  updated to enumerate the `OSError` subclasses caught.
- **[Med][Patch] planted-directory keystone test gap — RESOLVED.** Added
  `test_non_file_json_entry_is_a_typed_finding_not_a_crash` (TC-APAA-STORE-001-108): on a real `vacuous_basic`
  `run_audit` tree it creates a DIRECTORY named `state/evil.json`, asserts the weakened no-catch walk
  (`_walk_without_catching`) RAISES `OSError` (the planted break is real — RED), and asserts the real
  `lint_referential_integrity` RETURNS a report (`consistent=False`, an `unreadable_artifact` finding naming
  `state/evil.json`) and does NOT raise (green). **RED-then-green demonstrated explicitly:** with the catch
  reverted to the original four exceptions the new test FAILED with `PermissionError`; after broadening to
  `OSError` it passed (full suite 720 → 721). Closes the AI-E3-1 recurrence (a keystone test set that
  structurally could not catch a member of its own OSError bug class).

### File List

- `minions_core/apaa/store/integrity.py` (NEW — the referential-integrity lint: `IntegrityFinding` /
  `IntegrityReport` / `IntegrityLintError` + pure `_resolve_references` + impure `lint_referential_integrity`).
- `tests/apaa/test_store_integrity_lint.py` (NEW + EDITED in fix iter 1 — `APAA-STORE`
  `TC-APAA-STORE-001-82..108`, 27 tests; +1 = the planted-directory `OSError` keystone TC-...-108).
- `tests/apaa/test_no_web_imports.py` (EDITED — appended `store.integrity` to `_MODULES_UNDER_GUARD`).
- `_bmad-output/design-artifacts/APAA/deferred-work.md` (EDITED — append-only DF-1-3-A closure + DF-1-3-B note).
- `_bmad-output/design-artifacts/APAA/sprint-status.yaml` (EDITED — status flip + last_updated).
- `_bmad-output/design-artifacts/APAA/stories/4-2-referential-integrity-lint-of-on-disk-state.md` (EDITED — this file).

## Senior Developer Review (AI)

**Reviewer:** BMAD Reviewer / QA gate (adversarial code-review) — claude-opus-4-8.
**Date:** 2026-06-27. **Iteration:** 2 (re-review after fix). **Outcome:** APPROVED (verdict: pass — the iter-1 keystone FAIL is resolved and adversarially re-verified).

### Iteration 2 — re-review (the fix verdict)

The iteration-1 [High] no-crash keystone FAIL (FR26/AC6/AR10) and its companion [Med] test-coverage gap are both RESOLVED and independently re-verified:

- **[High] resolved + adversarially verified.** The enumerate-and-read shell catch is broadened from `FileNotFoundError` to `OSError` (`integrity.py:483-488`). I confirmed the breadth is correct: `OSError` genuinely subsumes `IsADirectoryError` + `PermissionError` + `FileNotFoundError` (the raced-delete / non-file-`*.json` / permission-denied classes), each routing through `_read_failure_finding` → `kind="unreadable_artifact"`, `token=type(exc).__name__` (a class name, never payload/path bytes — NFR-S1 preserved). The breadth is NOT too broad: the read chain (`read_envelope` → `_load_object`/`read_bytes` → `Path.resolve()` + `Path.read_bytes()`) only surfaces I/O errors here; the typed `StoreIntegrityError` (tamper → `content_hash_tamper`) and `pydantic.ValidationError` (bad-shape) are still caught FIRST and token-ized distinctly, and `WorkspaceContainmentError` is a `ValueError` subclass (NOT an `OSError`) so a containment escape still propagates rather than being silently swallowed. The typed `IntegrityLintError` programmer-error raise (non-`ApaaStoreReader` arg, raised before the loop) is unchanged. The 1.3 `read_envelope`/`StoreIntegrityError` semantics are untouched (no working-tree diff to `reader.py`).
- **[Med] resolved.** `test_non_file_json_entry_is_a_typed_finding_not_a_crash` (TC-APAA-STORE-001-108) plants a real `state/evil.json` DIRECTORY on a real `vacuous_basic` tree, asserts the weakened no-catch walk `_walk_without_catching` RAISES `OSError` (the break is real — RED proof), and asserts the real lint RETURNS a report (`consistent=False`, an `unreadable_artifact` finding naming exactly `state/evil.json`) and does NOT raise — the assertion is sharp (kind + locator pinned, not merely "consistent is False"). The dev additionally documented the RED-against-the-old-four-exception-catch demonstration (test FAILED with `PermissionError` before the broadening, passed after).
- **No regression.** Re-ran `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **721 passed** (720 → 721, +1 = the new keystone). mypy clean on `store/integrity.py` (Success: no issues found); 441 non-blank lines (≤1200). The intact-store-passes floor (AC2, two real cartridges) still yields zero findings; the no-web-imports + single-serializer AST gates are green; the frozen surfaces (envelope/reader/paths/recording/coverage_ledger/partitioner/negative_assurance) carry no tracked diff. Reuse-not-fork, DF-1-3-A closure, frozen `extra="forbid"`, no-float, sorted/byte-stable report — all intact.

All seven ACs are now MET (AC6's no-crash sub-clause is closed). No unresolved findings; no new defer.

---

**Reviewer:** BMAD Reviewer / QA gate (adversarial code-review) — claude-opus-4-8.
**Date:** 2026-06-27. **Iteration:** 1. **Outcome:** CHANGES REQUESTED (verdict: fail — one keystone-contract violation).

### Summary

The implementation is well-structured, scoped, and disciplined: a thin impure enumerate-and-read shell over the 1.3 `ApaaStoreReader` plus a genuinely pure `_resolve_references` resolver over an in-memory `_ReadArtifact` set; frozen `IntegrityFinding`/`IntegrityReport` (`frozen=True, extra="forbid"`, localized `schema_version`, no `float`); sorted/byte-stable report; reuse-canonical (no second tamper-type, serializer, enumerator, or producer registry — producer tokens mirrored as documented local constants to avoid a `pipeline.py` circular import). The reference graph (prev_hash chain / sha-stem / verdict→findings / plan→assignment / orphans / tamper) is locked against a real `run_audit` tree, and the AI-E3-1 RED-then-green keystone discipline is real and durable (weakened-resolver and no-catch helpers live in-test, not just narrated). The intact-store-passes floor runs over two real cartridge trees (`vacuous_basic` + `clean_control`) and produces zero findings — the false-positive floor holds. DF-1-3-A closure is real (filename↔content_hash mismatch lands as a finding) and the central-register note is append-only. 720 tests pass; the import-isolation gate is extended (not forked); the module is 437 non-blank lines (≤1200, headless). mypy was reported clean.

**However**, the marquee keystone — "a broken/misfiled on-disk state surfaces as a TYPED integrity finding, NEVER a crash" (FR26 second AC / AC6 / AR10) — does NOT hold for one reachable corrupt-tree class. The shell catches only `(StoreIntegrityError, CanonicalSerializationError, ValidationError, FileNotFoundError)`. A non-file `*.json` entry under `.apaa/` (e.g. a directory named `<sha>.json` from an interrupted/partial write or a botched recovery — the exact corruption this lint exists to detect) is enumerated by `glob("*.json")` and then read, raising `IsADirectoryError` (POSIX) / `PermissionError` (Windows) — both `OSError` subclasses NOT in the catch tuple — which escapes `lint_referential_integrity` as an uncaught exception. Reproduced live: planting `state/evil.json` as a directory on a real `vacuous_basic` tree crashes the lint with `PermissionError` instead of returning an `unreadable_artifact` finding. Because the no-crash contract is THE keystone (and is uncovered by the AC6 test set — the AI-E3-1 lesson recurring), this blocks `review → done`.

### Acceptance Criteria coverage

- AC1 (report shape over a real tree) — MET.
- AC2 (intact real tree, no false positives, over two real cartridges) — MET (load-bearing floor green).
- AC3 (dangling reference detected, RED-then-green) — MET.
- AC4 (broken prev_hash chain + orphan, chain check RED-then-green; V1 chain semantics locked) — MET.
- AC5 (filename↔content_hash mismatch + assignment-excluded control, RED-then-green; DF-1-3-A closure) — MET.
- AC6 (broken/tamper/corrupt → typed finding, NOT a crash, RED-then-green) — **PARTIALLY MET**: tamper / corrupt-bytes / unknown-field paths are correct and proven, but the `OSError`-on-non-file path escapes uncaught. The no-crash keystone is therefore not fully satisfied.
- AC7 (pure/frozen/typed-error/determinism/secret-safe/import-isolated/≤1200/suite green/mypy clean) — substantially MET (the no-crash sub-clause of AC7 inherits the AC6 gap).

### Findings

See `### Review Findings` above. One High (keystone no-crash violation, the [Patch] in `integrity.py`) plus its companion uncovered-test [Patch]. No `decision-needed`. No new defer filed.

### Verdict

**fail** — the FR26/AC6/AR10 no-crash keystone is violated by a reachable corrupt-tree input. Status set to `in-progress` for one fix round. Recommended fix is a one-line catch broadening (`OSError`) plus a planted-directory keystone test demonstrated RED. Everything else is pass-quality.

## Change Log

| Date | Change |
|------|--------|
| 2026-06-27 | dev-story (fix, iter 1): resolved the review FAIL — the FR26/AC6/AR10 no-crash keystone leaked an uncaught `OSError` (`IsADirectoryError`/`PermissionError`) on a non-file `*.json` entry (a directory named `<sha>.json` under `.apaa/`, enumerated by `glob("*.json")` then read). Broadened the enumerate-and-read shell catch from `FileNotFoundError` to `OSError` (subsumes `FileNotFoundError`+`IsADirectoryError`+`PermissionError`) → the entry now converts to an `unreadable_artifact` finding (NFR-S1 preserved; typed `IntegrityLintError` unchanged). Added the planted-directory keystone test `test_non_file_json_entry_is_a_typed_finding_not_a_crash` (TC-APAA-STORE-001-108), demonstrated RED against the original four-exception shell (`PermissionError` escaped) then green after the fix. Suite 720 → 721 passed; mypy clean; frozen surfaces unchanged. Both `### Review Findings` ticked. Status `in-progress` → `review`. |
| 2026-06-27 | dev-story (implement): shipped the FR26/NFR-A2 referential-integrity LINT — NEW pure `store/integrity.py` (`IntegrityFinding`/`IntegrityReport`/`IntegrityLintError` + pure `_resolve_references` resolver + impure enumerate-and-read shell over the 1.3 reader) that walks the on-disk `.apaa/` tree and proves every cross-reference resolves (prev_hash chain, content-addressed filename↔`content_hash` [DF-1-3-A closure], verdict→findings `recording_id`, plan→`assignments/<partition_id>`, orphans, tamper/corrupt). Keystone: a broken reference is a TYPED finding in the returned report, NEVER a raise. AI-E3-1 keystone fixtures plant a REAL break of every class + demonstrate RED via durable weakened-resolver helpers + an intact-store-passes floor over real `run_audit` trees. REUSES 1.3 `read_envelope`/`StoreIntegrityError`/`ApaaStorePaths`/`compute_content_hash` + the `_list_locators` pattern + pipeline producer tokens — no fork. Read-only; no pipeline/CLI/HTTP wiring. 720 passed, mypy clean, 437 non-blank lines, frozen surfaces unchanged. DF-1-3-A integrity gap closed (append-only note); DF-1-3-B left open. No new defer. |
