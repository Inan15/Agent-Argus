# Story 2.4: Repository partitioning into bounded audit units + work-manifest permission boundary

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/APAA/`; the tracker is `_bmad-output/design-artifacts/APAA/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As an integrator auditing a large repo (e.g. Minions, ~70 modules),
I want APAA to partition the repo into bounded audit units within the V1 scale envelope — each unit's
`work_manifest` doubling as the auditor's READ PERMISSION BOUNDARY (an off-scope read is impossible) —
so that audits stay inside the ≤40-file/15k-LOC ceiling and an auditor reads ONLY its assigned files,
while V1 honestly attempts NO cross-partition seam analysis (the FIFTH story of Epic 2; this is the
multi-**unit** auditing the OI2-locked dogfood needs, NOT the V2 seam auditor).

## Story Context

This is **Story 5 of Epic 2** (Full Coverage Ledger & Defect Detectors). It is the LAST partitioning/scale
piece of the FR1–4 Intake & Partitioning cluster: Story 1.4 (done) built the repo intake (`RepoIntake` @
pinned commit) + the tree-sitter Python AST/code-graph index (`AstIndex` of per-file `AstIndexEntry` with
`definitions` + a call/reference `edges` set) — explicitly DEFERRING the partitioner (`index/partitioner.py`)
to THIS story, with `partition_id` reserved-and-pinned to `"root"` everywhere in V1. Story 2.3 (done) built
critical-subsystem identification as a content-derived + operator-adjusted FILE SET (also explicitly NOT a
graph partition — "partitioning proper is Story 2.4"). **This story delivers FR3 (bounded-unit partitioning)
+ NFR-S4 (the work-manifest permission boundary) + NFR-SC1 (the ≤40-file/15k-LOC scale envelope).**

**What partitioning IS in V1.** APAA's scale envelope (NFR-SC1) is **≤40 files / 15k LOC per audit unit**
(hard ceiling ≤60 files / 25k LOC). A repo larger than one unit is split into **multiple graph-derived units**
(import/call graph, NOT directories — architecture Decision B). Each unit is bounded, deterministic, and
carries a `work_manifest` — the exact file-list that unit may read. **That manifest IS the permission
boundary (NFR-S4):** an auditor working a partition reads ONLY the files in its manifest; an off-scope read
is impossible because the manifest is the closed set the reader is given. This story builds (a) the pure
graph-derived partition PLANNER (deterministic, byte-stable manifests) and (b) the impure persistence of each
`work_manifest` to `.apaa/assignments/` through the existing containment shell + (c) the
permission-boundary CONTRACT — a manifest-scoped read primitive that refuses an off-scope path.

**The hard V1 limitation this story must state honestly.** V1 does **multi-UNIT** auditing, NOT **cross-
partition seam analysis**. A defect spanning a cut (caller in unit A, callee in unit B) is NOT analyzed by
any seam auditor in V1 — the **only** V1 mitigation is the Story 6.4 `cross_partition` Prosecutor cut-edge
pass (re-reads cut edges), and the full seam auditor + a non-`"root"`-semantics seam analysis is the reserved
**V2** work. `partition_id` becomes a REAL per-unit id in this story (it stops always being `"root"`), but the
ledger/verdict core stays partition-agnostic and no seam-spanning analysis is attempted (OI2 / epics Story
2.4 third AC). This is the V1 mitigation the planning OI2 names; it must appear in the partition plan's
provenance + the module docstring.

**What already exists (REUSE verbatim, do NOT rebuild).** This story is a NET-NEW pure planner + an impure
manifest-write seam — but it sits on a fully-built intake/index/store spine:

- **Story 1.4 (done) — `index/ast_index.py`.** `build_ast_index(repo_root, source_files, partition_id="root")
  -> AstIndex`. `AstIndex.entries` is a SORTED `tuple[AstIndexEntry, ...]`; each `AstIndexEntry` carries
  `file_path` (repo-root-relative POSIX), `ast_eligible: bool`, `parse_failed: bool`,
  `parse_failure_reason: str | None`, `definitions: tuple[Definition, ...]` (each with `name`, `kind`,
  1-based `start_line`/`end_line`), and `edges: tuple[CodeEdge, ...]` (each `callee` name + `line`). **REUSE
  this index as the partition graph source — do NOT re-parse, do NOT build a second index.** NOTE the locked
  V1 edge limitation (DF-1-4-A): `CodeEdge.callee` is the **unresolved** bare callee identifier / trailing
  attribute name with NO scope binding or name resolution. The partitioner must map callee names → defining
  files using the index's `definitions` (a name→file map built from `Definition.name`), accepting that an
  unresolved/ambiguous callee is a best-effort edge (the conservative direction is to NOT over-merge —
  document it; full resolved-call-graph partitioning is Epic-6 depth).
- **Story 1.4 (done) — `RepoIntake` + the per-file source read.** `pipeline.py::_read_source(repo_root,
  rel_path) -> str` already reads each source file once. **REUSE that read** to compute per-file LOC (the
  15k-LOC envelope half) — the planner takes LOC as an in-memory ARGUMENT (an int per file); it never opens a
  file (purity, AR8). `RepoIntake.source_files` is the sorted relative-POSIX file set.
- **Story 1.3 (done) — `store/paths.py` + `store/writer.py`.** `ApaaStorePaths` ALREADY declares
  `assignments/` in its fixed `.apaa/` tree (`state/ assignments/ findings/ decisions/ cache/`) and
  `ensure_tree()` creates it. `ApaaStoreWriter.write_assignment(assignment_id, envelope) -> str` ALREADY
  writes a `work_manifest` to `assignments/<assignment_id>.json` from a STABLE, content-derived
  `assignment_id` (never `uuid4`/counter/arrival order — AR11), through the single-serializer canonical
  bytes + the `is_relative_to` containment check. **REUSE `write_assignment` verbatim** — do NOT add a second
  writer / second path resolver / second serializer.
- **Story 1.1 (done) — `store/canonical.py` + `store/envelope.py`.** Any `.apaa/` bytes go through
  `EnvelopeWriter.build` + `canonical.dumps_bytes` (the single serializer; the AST gate forbids a direct
  `json.dumps(`). The manifest is envelope-wrapped (content-hash over payload only, `prev_hash` chain,
  `schema_version` + `producer` + `apaa_version`).
- **Story 1.2 (done) — `ledger/recording.py::Locator`, `coverage_ledger.py`.** `partition_id` is RESERVED on
  the recording schema and pinned `"root"` in V1; this story is the one that supplies a REAL per-unit
  `partition_id` value — but it does NOT modify the frozen ledger/recording models (the `partition_id` field
  already exists; the planner produces the ids, it does not re-shape the schema).
- **Story 1.7 / `pipeline.py` (done).** `run_audit_detailed` is the IMPURE orchestrator: intake → index →
  per-file detect → ledger → critical-subsystem set → `evaluate_verdict`. The V1 pipeline audits the single
  `"root"` partition. **This story's pipeline touch is SCOPE-FENCED (see below): it MAY persist the partition
  plan + per-unit work-manifests as `.apaa/assignments/` artifacts (the resumability/permission-boundary
  seam) WITHOUT changing the verdict math or splitting the existing single-pass audit into N sub-audits.**
  Driving N independent per-partition audits end-to-end (the multi-pass orchestration) is the OI2 dogfood
  (Story 7.1/7.2) — this story builds the PLAN + the MANIFEST CONTRACT, not the multi-pass run loop.

**The net-new deliverable of THIS story.** A pure partition PLANNER + a frozen partition/manifest contract +
the impure manifest-write seam + the manifest-scoped read permission-boundary primitive:
1. a pure **`partition_repository(...)` planner** (recommended `index/partitioner.py`, the architecture's
   locked home) that, given the 1.4 `AstIndex` (the graph) + a per-file LOC map + the NFR-SC1 limits, produces
   a deterministic, byte-stable set of bounded `Partition` units (each ≤40 files/15k LOC; hard ceiling
   ≤60/25k), graph-derived (import/call graph via the index `edges`+`definitions`, NOT directory layout), with
   `context_pressure` auto-downgrade when a unit nears the ceiling;
2. a frozen **`Partition` / `PartitionPlan` / `WorkManifest`** Pydantic v2 contract (`frozen=True,
   extra="forbid"`, localized `schema_version`) — each `Partition` carries a STABLE content-derived
   `partition_id` + its `work_manifest` (the sorted file-list) + bounded-size provenance (file count, LOC);
3. the **work-manifest permission-boundary primitive** — a manifest IS a closed read scope: a pure
   `is_in_scope(manifest, rel_path) -> bool` + an impure `read_in_scope(...)` (or an explicit
   manifest-scoped reader) that refuses an off-scope path with a typed error (NFR-S4 — off-scope read
   impossible), mirroring the 1.3 containment rigor (a closed allow-set, never a prefix/substring check);
4. the impure **manifest persistence** through `ApaaStoreWriter.write_assignment(...)` (content-addressed,
   envelope-wrapped, containment-checked) so each unit's manifest lands deterministically in
   `.apaa/assignments/`;
5. an **honest-limitation provenance** field on the plan recording that V1 attempts NO cross-partition seam
   analysis (the Story 6.4 `cross_partition` pass is the V1 mitigation; full seam auditing is V2).

The PLANNER + the contract + `is_in_scope` are PURE (AR8) and join the import-isolation gate. The
manifest WRITE + the per-file LOC READ + `read_in_scope` I/O are the impure shell.

**Carry-forward from the Epic-1 retro (CLAUDE.md §9.1 / L1-E11 — this story discharges these items).**
- **AI-E1-1 (test-infra 🟠) — adversarial non-ASCII / locale fixtures.** Partitioning + manifests carry file
  PATHS; the permission boundary matches PATHS. Tests MUST include a **non-ASCII path fixture** (e.g.
  `auth/café_guard.py`, `модуль/безопасность.py`) proven (a) placed into a partition with its path intact
  (not mojibake / not dropped — reusing the 1.4 TC-APAA-INTAKE-001-78 `git ls-files -z` precedent), (b)
  in-scope for its own manifest and (c) off-scope-rejected for a different manifest, round-tripping intact
  through the canonical serializer.
- **AI-E1-4 (process 🟢) — keep the committed gates extended-not-forked.** Append the new pure module(s) to
  `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py` (do NOT fork the no-web-imports gate); keep the
  single-serializer AST gate (`test_canonical_single_serializer.py`) green (any JSON of a partition/manifest
  goes through `store/canonical.dumps`, never a direct `json.dumps`).
- **AI-E1-5 (process 🟢) — exercise the L1-E11 loop.** This story explicitly references the AI-E1-* items it
  discharges (here).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 2.4) and the architecture / PRD. Drivers: **APAA-FR-3** (APAA can
> partition the repository into bounded audit units within a declared budget — the central driver),
> **APAA-NFR-SC1** (V1 audit units ≤40 files/15k LOC; hard ceiling ≤60/25k; larger repos partition; full
> 10k→500k LOC scaling is V2), **APAA-NFR-S4** (an auditor reads ONLY the files in its work-manifest — the
> permission boundary; off-scope reads impossible), **APAA-NFR-S5** (all filesystem writes containment-checked
> via `is_relative_to`, reusing the 1.3 shell), **APAA-NFR-P1** (byte-identical partition plan + manifests
> across hosts/runs for the same repo@commit), **APAA-NFR-D2** (deterministic, zero-LLM-token — the planner is
> a pure fold over the recorded index + LOC inputs), **APAA-NFR-M2** (frozen, additive-only contracts),
> **APAA-NFR-M1** (≤1200-line files), **AR3** (the gate exit-code wire contract is UNCHANGED — this story adds
> no verdict/exit semantics), **AR4** (no `float`; closed forms / `int` / `str`; single canonical serializer;
> no clock/uuid/random/iteration-order in any `.apaa/`-bound output — partition ids are content-derived, never
> arrival order — AR11), **AR8** (pure/impure separation — the planner + contract + `is_in_scope` are PURE; the
> LOC read + manifest write + scoped read are the impure shell), **AR10** (typed failure, never an uncaught
> raise / silent coerce), **AR11** (`.apaa/` filenames content-derived / stable-id, never arrival order),
> cross-cutting (the V1 honest limitation: NO cross-partition seam analysis — the 6.4 Prosecutor cut-edge pass
> is the V1 mitigation, full seam auditing is V2).
>
> **SCOPE FENCE — Tier-A, single-purpose.** This story delivers ONLY: (1) the pure graph-derived partition
> PLANNER (`partition_repository(...)`) producing deterministic bounded units within NFR-SC1; (2) the frozen
> `Partition` / `PartitionPlan` / `WorkManifest` contract with content-derived `partition_id`s; (3) the
> work-manifest permission-boundary primitive (`is_in_scope` pure predicate + a manifest-scoped read that
> refuses off-scope paths — NFR-S4); (4) the impure manifest persistence to `.apaa/assignments/` via the
> EXISTING `ApaaStoreWriter.write_assignment`; (5) the V1 honest-limitation provenance (no cross-partition
> seam analysis). It does NOT build, and MUST NOT pull forward: any **cross-partition seam auditor** / a
> non-`"root"`-semantics seam analysis / the `cross_partition` finding class + Prosecutor cut-edge pass (FR19 —
> **Story 6.4 [Tier B]** — the V1 mitigation; full seam auditing is V2); the **multi-pass per-partition audit
> orchestration / run loop** that audits each unit end-to-end and merges N ledgers (the OI2 dogfood — Story
> 7.1/7.2); the **secret detector** (FR11 — Story 2.5); the **breadth tool runner** (FR14 — Story 2.6); the
> **budget-ceiling cost accounting** that sizes a unit's $-budget (FR21/FR22 — Epic 3 / Story 3.1 — this story
> bounds units by FILES + LOC per NFR-SC1, NOT by a $-budget; "within a declared budget" in V1 = within the
> file/LOC envelope, the OI3 $-default is deferred to Story 7.1); the **LLM dispatch port / deep audit**
> (Epic 6); the **resolved call-graph** (Epic 6 depth — V1 partitioning uses the unresolved 1.4 edge set
> best-effort); any change to the **1.6 verdict gate / 1.2 ledger enum / 1.1 serializer / 1.4 index / 2.1
> `assess_criticality` / 2.3 critical-subsystem** contracts (all frozen/reused). It does NOT add a NEW HTTP
> route / FastAPI surface / UI (§3.7). Plan + bound + manifest + the permission contract, then stop.

**AC1 — Graph-derived partitioning into bounded units within the NFR-SC1 envelope (FR3, NFR-SC1)**
**Given** a repo larger than one audit unit (e.g. a fixture standing in for Minions ~70 modules) — its 1.4
`AstIndex` (the import/call graph via per-file `definitions` + `edges`) + a per-file LOC map (computed by the
impure caller from the already-read source)
**When** the pure `index/partitioner.py::partition_repository(index, *, loc_by_file, limits=...)` runs
**Then** it produces **multiple** `Partition` units, each within the V1 scale envelope — **≤40 files AND
≤15k LOC** (the soft V1 target), with a hard ceiling **≤60 files / 25k LOC** — where the partition graph is
GRAPH-DERIVED (cohesion via the index's call/reference edges + a callee-name→defining-file map built from
`Definition.name`, NOT directory layout — architecture Decision B); a repo at-or-under one unit yields a
single partition (the regression-safe degenerate case)
**And** `context_pressure` AUTO-DOWNGRADE applies: when a unit approaches the ceiling the planner conservatively
splits / shrinks rather than overflowing a unit (record a `context_pressure` flag/marker on a unit that was
split because it neared the limit), so NO produced unit ever exceeds the HARD ceiling (a single file larger
than 15k LOC on its own is its own unit and is flagged context-pressured — it cannot be split below one file;
document this boundary case)
**And** the partition is PURE (takes the already-built `index` + the in-memory `loc_by_file` as ARGUMENTS — it
never opens a file or re-parses), deterministic, and relies on NO dict/`set` iteration order (AR4); a
non-`ast_eligible` / `parse_failed` file is still PLACED into a partition (it is still in scope and must be
covered — it just routes to the `claim_emitted` proxy downstream; partitioning is over the file SET, not only
the parseable subset).

**AC2 — Each partition is a frozen contract with a STABLE content-derived `partition_id` (AR4, AR11, NFR-M2, NFR-P1)**
**Given** the produced partitions
**When** the `Partition` / `PartitionPlan` model is built
**Then** each `Partition` is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`, localized
`PARTITION_SCHEMA_VERSION`) carrying: a STABLE `partition_id` DERIVED FROM ITS CONTENT (e.g. a sha256 over the
sorted member file-paths — NEVER `uuid4` / a sequential counter / arrival order — AR11/AR4), its
`work_manifest` (the SORTED `tuple[str, ...]` of repo-root-relative POSIX member paths), and bounded-size
provenance (`file_count: int`, `total_loc: int`, an optional `context_pressure: bool`) — NO `float` anywhere
(LOC + counts are `int`; there is NO partition "score") — and the `PartitionPlan` is the sorted (by
`partition_id`) tuple of partitions + the V1-limitation provenance (AC5)
**And** the same repo@commit (same index + same LOC map) yields a BYTE-IDENTICAL `PartitionPlan` across
hosts/runs and across two input orderings of the same files (NFR-P1) — partition membership, ids, and ordering
are a pure deterministic function of content, proven by an order-independence + byte-stability test
**And** the per-file `partition_id` assignment is total and disjoint: EVERY `RepoIntake` source file lands in
EXACTLY ONE partition (no file dropped — the AR1.4 non-ASCII-drop class is the cautionary precedent; no file
in two units), proven by a coverage/partition-of-the-set unit test.

**AC3 — The work-manifest IS the auditor's read PERMISSION BOUNDARY — off-scope read impossible (NFR-S4)**
**Given** a `Partition`'s `work_manifest` (its closed member file-set)
**When** an auditor (or the manifest-scoped read primitive) attempts to read a path
**Then** a pure `is_in_scope(manifest, rel_path) -> bool` returns `True` ONLY for a path that is an EXACT
member of the manifest's closed set (a normalized-path EQUALITY / set-membership check — NEVER a
`str.startswith` / prefix / substring check, mirroring the 1.3 `is_relative_to` containment rigor: a
sibling-prefix `auth/secrets_extra.py` vs an in-scope `auth/secrets.py` must NOT pass), and an impure
manifest-scoped reader (`read_in_scope(repo_root, manifest, rel_path)` or equivalent) reads the file ONLY when
`is_in_scope` passes and otherwise raises a TYPED `PartitionScopeError` (or the localized partitioner error) —
an OFF-SCOPE read is IMPOSSIBLE through this primitive (NFR-S4), never a silent empty read / fabricated content
**And** the boundary normalizes paths so a `./auth/x.py` / `auth/x.py` / backslash-vs-slash variant is matched
correctly (reuse POSIX-normalization; do NOT let a normalization gap become an off-scope-read escape), and a
traversal (`../other_unit/x.py`) is OUT of scope (rejected), proven by adversarial scope tests (in-scope pass;
sibling-prefix reject; traversal reject; non-ASCII in-scope pass + cross-manifest reject — AI-E1-1)
**And** the permission-boundary primitive is documented as the NFR-S4 contract in the module docstring (a
manifest is a closed allow-set; an auditor is GIVEN only its manifest's files; reading outside it is a typed
error, not a policy a caller may opt out of).

**AC4 — Per-unit work-manifests persist to `.apaa/assignments/` via the EXISTING containment shell (NFR-S5, AR4, AR11, FR25)**
**Given** a `PartitionPlan` the pipeline will persist (the resumability / permission-boundary seam)
**When** each partition's `work_manifest` is written
**Then** the write goes through the EXISTING `ApaaStoreWriter.write_assignment(partition_id, envelope)` — the
filename is `assignments/<partition_id>.json` (the STABLE content-derived `partition_id`, never arrival order —
AR11), the bytes are `EnvelopeWriter.build(...)` → `store/canonical.dumps_bytes` (single serializer, no second
`json.dumps` — the AST gate enforces it), and the `ApaaStorePaths` `is_relative_to` containment check guards
the path (NFR-S5) — REUSING the 1.1/1.3 spine with NO second writer / path resolver / serializer
**And** the persisted manifest payload carries ONLY repo-root-relative POSIX paths + the bounded-size
provenance + the `partition_id` — NEVER an absolute host path, NEVER source/secret bytes (NFR-S1 spirit; the
1.3 DN-3 / 2.3 precedent: the run-state never records `repo_path`); re-reading via `store/reader.py`
reconstructs an equal model + round-trips byte-identically (NFR-P1), verified by a round-trip test (mirrors
`test_store_roundtrip`)
**And** the partition PLAN snapshot (the sorted partition ids + the V1-limitation provenance) MAY also persist
to `.apaa/state/` via the SAME envelope/writer spine (content-addressed `<content_hash>.json`); if the dev
defers the plan-snapshot half to the Story-7.1 dogfood pipeline, document that and persist at least the
per-unit `assignments/` manifests (the NFR-S4 boundary artifacts are the in-scope deliverable).

**AC5 — V1 honestly attempts NO cross-partition seam analysis — the limitation is recorded (OI2, epics 2.4 third AC, cross-cutting #4)**
**Given** multiple V1 audit units that span partition cut edges (a caller in unit A whose callee is defined in
unit B)
**When** the partition plan is produced + persisted
**Then** NO cross-partition seam analysis is attempted in V1 — a defect spanning a cut is NOT analyzed by any
seam auditor in this story; the plan's provenance EXPLICITLY records that V1 multi-unit auditing performs no
seam analysis across cut edges, that the **Story 6.4 `cross_partition` Prosecutor cut-edge pass is the V1
mitigation** (it re-reads cut edges; it is Tier-B / Epic 6 — NOT built here), and that the **full seam auditor
is reserved V2** (a `seam_analysis: "v2-deferred"` / equivalent honest-limitation marker on the plan
provenance + the module docstring)
**And** `partition_id` becomes a REAL per-unit content-derived id in this story (it stops always being
`"root"`), but the **1.2 ledger / recording `partition_id` field is NOT re-shaped** (the field already exists
and is reserved — this story SUPPLIES real id VALUES via the plan, it does not modify the frozen ledger/
recording/verdict models); the ledger/verdict core stays partition-agnostic (no seam-spanning logic leaks into
`ledger`/`verdict` — NFR-P2 spirit)
**And** the cut edges the index already exposes (the 1.4 `edges` crossing a partition boundary) MAY be RECORDED
on the plan provenance as the cut-edge set the future 6.4 pass will consume (best-effort, from the
unresolved-name edge set per DF-1-4-A — recorded, NOT analyzed) — this is the seam the 6.4 story folds over;
do NOT analyze them here.

**AC6 — The new pure modules are PURE, frozen-contract, deterministic, and import-isolated (NFR-D2, NFR-P1, AR8, AR10, M2)**
**Given** `index/partitioner.py` (and any frozen model it defines)
**When** it is imported and exercised in unit tests
**Then** the planner + the `Partition`/`PartitionPlan` build + the `is_in_scope` predicate perform NO
filesystem I/O, NO clock read (`datetime.now`/`time.time`), NO `uuid4`/`os.getpid()`/`random`, NO LLM/network
call, NO dict/`set`-iteration-order reliance — they are PURE functions over in-memory inputs (the per-file LOC
READ, the manifest WRITE, and the manifest-scoped READ are the impure shell)
**And** any model it defines is a frozen Pydantic v2 model (`frozen=True, extra="forbid"` — the
1.1/1.2/1.4/1.6/2.1/2.3 precedent) with a localized `PARTITION_SCHEMA_VERSION` (additive-only, NFR-M2); NO
`float` anywhere (LOC + counts are `int`; ids + paths are `str`; `context_pressure` is `bool` — AR4); any JSON
rendering routes through `store/canonical.dumps` (the single 1.1 serializer — no second `json.dumps`)
**And** a malformed input (a non-`AstIndex` argument, a non-`int` LOC value, a negative limit, a non-`str`
path) raises a typed error — a `ValueError` subclass localized to the module (mirroring `RepoIntakeError` /
`DepthSemanticsError` / `CriticalSubsystemError` / `CoverageReportError`) — never a silent coerce / bare
`except: pass` / `print()` in library code (AR10); the impure manifest-scoped read failure surfaces as the
typed `PartitionScopeError`, and any partition-persistence failure degrades to the pipeline's existing typed
`PipelineError` (exit `1`), never an uncaught traceback
**And** `minions_core.apaa.index.partitioner` is appended to `_MODULES_UNDER_GUARD` in
`tests/apaa/test_no_web_imports.py` (extend, do NOT fork) and importing it does NOT transitively import
`fastapi`/`uvicorn`/`starlette` or any LLM/api module (assert absence from `sys.modules`).

**AC7 — The whole APAA suite green; tests cover partitioning + manifest boundary + persistence + the V1 limitation; mypy clean; ≤1200 lines (NFR-M1)**
**Given** the modules + tests added/edited by this story
**When** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` runs
**Then** all pass, including new tests in `tests/apaa/test_partitioner.py`: AC1 bounded-unit partitioning (a
fixture index that EXCEEDS 40 files / 15k LOC splits into ≥2 units each within the soft target / hard ceiling;
a small index stays ONE unit; `context_pressure` auto-downgrade flagged on a near-ceiling split; a single
oversized file is its own context-pressured unit; graph cohesion via edges is exercised); AC2 the
content-derived `partition_id` (stable across runs; sha256-over-sorted-members, never a counter), the
order-independence + byte-stability of the plan, and the total-and-disjoint partition-of-the-set property;
AC3 the permission boundary (`is_in_scope` exact-membership: in-scope pass, sibling-prefix reject, traversal
reject; `read_in_scope` reads in-scope + raises `PartitionScopeError` off-scope — the OFF-SCOPE-READ-IMPOSSIBLE
proof); AC5 the V1 no-seam-analysis provenance marker present + the cut-edge set recorded-not-analyzed; AC6
purity (AST scan) / frozen / no-`float` / typed-error / single serializer; the **AI-E1-1 non-ASCII path**
fixture placed into a partition with its path intact + in-scope for its own manifest + off-scope-rejected for a
different manifest
**And** a `tests/apaa/test_assignments_roundtrip.py` (or extend an existing store round-trip test) proves a
per-unit `work_manifest` written via `ApaaStoreWriter.write_assignment` → read via `store/reader.py` →
equal model + byte-identical re-serialize (NFR-P1), with the filename = `assignments/<partition_id>.json` and
NO absolute path / source byte in the payload
**And** `index/partitioner.py` is appended to `_MODULES_UNDER_GUARD` and the import-isolation gate stays green;
the 1.1 single-serializer AST gate still passes with the new module present (no direct `json.dumps(`); the new
source file(s) are ≤1200 lines (NFR-M1) and cite their `APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in the module
docstring; `mypy` is clean on the new + edited modules. The 1.6 gate / 1.2 enum / 1.1 serializer / 1.4 index /
2.1 `assess_criticality` / 2.3 critical-subsystem contracts are UNCHANGED (this story adds the partitioner
module + the permission-boundary primitive + tests + the manifest-persistence wiring; if it touches
`pipeline.py` it is ONLY to persist the plan/manifests — NOT to change the verdict math or split the
single-pass audit into N sub-audits — and it does NOT modify the frozen index/ledger/verdict/criticality
contracts).

## Tasks / Subtasks

- [x] **Task 0 — Verify the existing reuse surface (verify-and-lock)** (AC: 1, 4, 5)
  - [x] Re-read `index/ast_index.py`: confirm `build_ast_index(...) -> AstIndex` with `AstIndex.entries`
        (sorted `AstIndexEntry` carrying `file_path`, `ast_eligible`, `parse_failed`, `definitions`, `edges`),
        and the locked V1 edge limitation (DF-1-4-A — `CodeEdge.callee` is unresolved). The planner CONSUMES
        this index; it does NOT re-parse.
  - [x] Re-read `store/paths.py` + `store/writer.py`: confirm `assignments/` is in the fixed tree and
        `write_assignment(assignment_id, envelope) -> str` exists (content-addressed, containment-checked).
        REUSE verbatim; do NOT add a second writer / path resolver / serializer.
  - [x] Re-read `pipeline.py`: confirm `run_audit_detailed` + `_read_source` (the per-file source read the
        impure caller reuses to compute LOC) + the typed `PipelineError`. Confirm `partition_id="root"` is the
        current single-partition state. Decide the minimal persistence touch (plan/manifests) WITHOUT changing
        the verdict math or the single-pass audit.
  - [x] Re-read `ledger/recording.py` + `coverage_ledger.py`: confirm the reserved `partition_id` field —
        this story SUPPLIES real id values; it does NOT re-shape the frozen ledger/recording models.
- [x] **Task 1 — `index/partitioner.py`: pure planner + frozen contract + permission boundary** (AC: 1, 2, 3, 5, 6)
  - [x] Create `minions_core/apaa/index/partitioner.py` (docstring cites the drivers + the LOCKED decisions +
        the V1 no-seam-analysis limitation). Pure `partition_repository(index, *, loc_by_file, limits=...)`
        producing bounded graph-derived units (≤40 files/15k LOC soft; ≤60/25k hard; `context_pressure`
        auto-downgrade; every file in exactly one unit).
  - [x] Frozen `Partition` / `PartitionPlan` / `WorkManifest` (`frozen=True, extra="forbid"`, localized
        `PARTITION_SCHEMA_VERSION`): STABLE content-derived `partition_id` (sha256 over sorted members), sorted
        `work_manifest`, `file_count`/`total_loc` `int`, optional `context_pressure: bool`, sorted plan,
        V1-limitation provenance (`seam_analysis="v2-deferred"` + recorded cut-edge set, recorded-not-analyzed).
        NO `float`; no I/O/clock/LLM (pinned by the AST/purity test).
  - [x] Pure `is_in_scope(manifest, rel_path) -> bool` (EXACT normalized-path membership — never prefix/substring;
        traversal out of scope) + `PartitionScopeError` / `PartitionerError` (ValueError subclass) on malformed
        input / off-scope read (AR10). Lock + document the path-normalization rule + the closed-allow-set
        contract.
- [x] **Task 2 — Impure shell: per-file LOC + manifest-scoped read + manifest persistence** (AC: 1, 3, 4)
  - [x] Add the impure per-file LOC computation (reuse the pipeline's `_read_source` output; count lines) and
        feed `loc_by_file` into the pure planner — the planner never opens a file.
  - [x] Add the impure `read_in_scope(repo_root, manifest, rel_path)` (or equivalent) — reads ONLY when
        `is_in_scope` passes; otherwise `PartitionScopeError`. Reuse the 1.3 containment for the actual read
        (the manifest scope is the ADDITIONAL allow-set on top of `.apaa`/repo containment).
  - [x] Persist each partition's `work_manifest` via `ApaaStoreWriter.write_assignment(partition_id,
        EnvelopeWriter.build(payload, ...))` → `assignments/<partition_id>.json` (repo-relative paths only,
        no absolute host path / source bytes). Optionally persist the plan snapshot to `.apaa/state/` via the
        same envelope/writer spine (or document deferral to Story 7.1).
- [x] **Task 3 — (Scope-fenced) pipeline persistence touch** (AC: 4, 5)
  - [x] In `run_audit_detailed` (or a thin sibling): build the partition plan from the existing in-memory
        `index` + a per-file LOC map, and persist the per-unit manifests + (optionally) the plan snapshot.
        DO NOT change the verdict math, DO NOT split the existing single-pass audit into N sub-audits (that is
        the Story 7.1/7.2 dogfood). A no-op / single-unit repo persists one manifest and is otherwise
        byte-identical to today. Keep the typed `PipelineError` wrapping (AR10) intact.
- [x] **Task 4 — Tests** (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] `tests/apaa/test_partitioner.py` — AC1 bounded-unit partitioning (oversized index → ≥2 units within
        soft/hard limits; small → 1 unit; `context_pressure` flagged; oversized-single-file boundary; graph
        cohesion via edges); AC2 content-derived stable `partition_id` + order-independence + byte-stability +
        total-and-disjoint partition-of-the-set; AC3 permission boundary (`is_in_scope` exact membership:
        in-scope pass / sibling-prefix reject / traversal reject; `read_in_scope` off-scope → `PartitionScopeError`
        — the OFF-SCOPE-READ-IMPOSSIBLE proof); AC5 V1 no-seam-analysis provenance + recorded-not-analyzed cut
        edges; AC6 purity (AST scan) / frozen / no-float / typed-error / single serializer; **AI-E1-1 non-ASCII
        path** placed intact + in-scope for own manifest + cross-manifest reject. Test area `APAA-INDEX`
        (`TC-APAA-INDEX-001-NN`, continuing the 1.4 index area; the manifest-boundary may use `APAA-PARTITION`
        if the dev prefers a distinct area — lock the choice); zero LLM tokens for the pure tests.
  - [x] `tests/apaa/test_assignments_roundtrip.py` (or extend `test_store_roundtrip.py`) — `write_assignment`
        → `store/reader.py` round-trip: equal model + byte-identical re-serialize; filename
        `assignments/<partition_id>.json`; no absolute path / source byte in payload.
  - [x] Extend the pipeline e2e test only if Task 3 persists in the run — prove a multi-unit fixture persists
        N manifests and a single-unit repo is byte-identical to today (the regression-safe path).
- [x] **Task 5 — Extend the import-isolation gate** (AC: 6, 7)
  - [x] Append `minions_core.apaa.index.partitioner` to `_MODULES_UNDER_GUARD` (extend, do NOT fork).
- [x] **Task 6 — Run + mypy** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass (the 1.1
        single-serializer AST gate + the extended no-web-imports gate re-run green with the new module present).
  - [x] `mypy` clean on the new + edited modules (`index/partitioner.py`, + `pipeline.py` if touched).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **Graph-derived, not directory-derived (architecture Decision B).** Partitioning uses the import/call graph,
  NOT folder layout. The graph source is the 1.4 `AstIndex`: nodes = files; cohesion edges come from
  `AstIndexEntry.edges` (call/reference) resolved to defining files via a `Definition.name → file` map built
  from the index. **Honor the locked V1 edge limitation (DF-1-4-A):** `CodeEdge.callee` is an UNRESOLVED bare
  name with no scope binding — so the name→file map is best-effort; an ambiguous/unresolved callee yields no
  merge edge. The conservative direction is to UNDER-merge (keep weakly-coupled files in separate small units)
  rather than over-merge into an oversized unit; document the heuristic. A full resolved call graph is Epic-6
  depth — do NOT build it here.
- **Bound by FILES + LOC (NFR-SC1), NOT by a $-budget (FR21 is Epic 3).** The V1 "declared budget" for FR3 is
  the SCALE ENVELOPE: ≤40 files AND ≤15k LOC soft target, ≤60 files / 25k LOC HARD ceiling. The numeric
  $-budget ceiling (OI3) is DEFERRED to the Story 7.1 dogfood sizing — do NOT couple the partitioner to
  `cost/budget_governor.py` (Epic 3). LOC is computed by the impure caller (line count over the already-read
  source) and PASSED IN as an `int` map; the planner is pure over it.
- **`context_pressure` auto-downgrade (architecture Decision B).** When a unit nears the ceiling, split /
  shrink conservatively and FLAG the unit `context_pressure=True`; NO produced unit may exceed the HARD
  ceiling. A single file > 15k LOC is its own unit (cannot split below one file) and is context-pressured —
  document this boundary (it is honest degradation, not a crash).
- **The work-manifest IS the permission boundary (NFR-S4) — mirror the 1.3 containment rigor.** A manifest is
  a CLOSED ALLOW-SET; `is_in_scope` is EXACT normalized-path membership — NEVER `str.startswith` / prefix /
  substring (the 1.3 lesson: a sibling-prefix `auth/secrets_extra.py` vs `auth/secrets.py` must NOT pass; the
  18-2 Minions `is_relative_to`-not-`startswith` precedent). Normalize paths (POSIX, strip `./`, reject `..`
  traversal) before comparison so a normalization gap is not an escape. The impure `read_in_scope` reads ONLY
  on a scope pass and raises `PartitionScopeError` otherwise — an off-scope read is IMPOSSIBLE through the
  primitive (not a policy a caller may opt out of).
- **Content-derived `partition_id`, never arrival order (AR11/AR4).** The `partition_id` is a sha256 (or the
  existing content-hash helper) over the SORTED member paths — stable across runs, byte-identical across hosts.
  NEVER a `uuid4` / sequential counter / arrival-order index. This is the AR11 filename rule (the
  `write_assignment` filename is `<partition_id>.json`) AND the NFR-P1 determinism keystone.
- **No floats — ever (AR4 / NFR-P1).** LOC + file counts are `int`; ids + paths are `str`; `context_pressure`
  is `bool`. There is NO partition "cohesion score" float — if a cohesion metric is needed, it is an `int`
  edge-count or a `Fraction`, never a float. Any JSON of a plan/manifest routes through the single 1.1
  `store/canonical.dumps` (which rejects `float`); the AST gate forbids a second `json.dumps`.
- **Pure/impure separation (master rule, AR8).** `index/partitioner.py` is PURE — the planner + the contract +
  `is_in_scope` over in-memory inputs; it never opens a file, reads a clock, or calls the parser. The IMPURE
  shell is the per-file LOC read, `read_in_scope`, and the `write_assignment` persistence (the pipeline). ✅ a
  pure planner over `(index, loc_by_file)` · ❌ a planner that re-reads the repo or calls `datetime.now()`.
- **Determinism (NFR-P1).** Partition membership, ids, plan ordering are a pure deterministic function of
  content; the same repo@commit yields a byte-identical plan + manifests; two input orderings of the same
  files yield the identical plan. Pin a byte-stability + order-independence test.
- **The V1 honest limitation — NO cross-partition seam analysis (OI2, cross-cutting #4).** This story
  attempts NO seam analysis across cut edges. Record the limitation on the plan provenance
  (`seam_analysis="v2-deferred"`) + the module docstring: the Story 6.4 `cross_partition` Prosecutor cut-edge
  pass is the V1 MITIGATION (Tier-B / Epic 6 — NOT built here); the full seam auditor is V2. The cut edges
  (1.4 `edges` crossing a boundary) MAY be RECORDED on the plan (the set the 6.4 pass will consume) but are
  NOT analyzed.
- **`partition_id` stops being always-`"root"` — but the ledger/recording schema is NOT re-shaped.** The 1.2
  `partition_id` field is already reserved; this story SUPPLIES real per-unit id VALUES via the plan. Do NOT
  add a field to / modify `coverage_ledger.py` / `recording.py` / `verdict_gate.py` (NFR-P2 — the ledger/
  verdict core stays partition-agnostic; no seam-spanning logic leaks in).
- **Error/degradation → typed, never crash (AR10).** A malformed planner input / a non-`AstIndex` arg / a
  negative limit / an off-scope read → a typed `PartitionerError` / `PartitionScopeError` (ValueError
  subclass) localized to the module. NO bare `except: pass`, NO `print()` in library code, NO silent coerce.
  Partition-persistence failure degrades to the pipeline's existing `PipelineError` (exit `1`).
- **Headless / import boundary (§3.7, AR7/AR9).** No UI, no HTML/CSS/JS, no FastAPI route. APAA is downstream
  of the HTTP/A2A boundary; the new pure module takes no token, registers no route, imports no web/LLM stack,
  and joins `_MODULES_UNDER_GUARD`.

### The partition model (the AC1/AC2/AC3/AC5 reference — lock + document)

| concept | source | form |
|---|---|---|
| partition graph | 1.4 `AstIndex.entries` (nodes=files; cohesion via `edges` → `Definition.name`→file map) | in-memory, REUSE |
| per-file LOC | impure line-count over `_read_source` output | `dict[str, int]`, PASSED IN |
| scale limits | NFR-SC1: ≤40 files/15k LOC soft; ≤60/25k hard | `int` limits, the planner arg |
| `Partition` | a bounded unit | frozen: `partition_id` (sha256 over sorted members), sorted `work_manifest: tuple[str,...]`, `file_count: int`, `total_loc: int`, `context_pressure: bool` |
| `partition_id` | sha256 over sorted member paths (AR11) | `str`, stable, content-derived (never counter/uuid/arrival order) |
| `PartitionPlan` | the whole partition of the repo | frozen: sorted `partitions: tuple[Partition,...]`, `seam_analysis="v2-deferred"`, recorded cut-edge set (not analyzed) |
| `is_in_scope` | EXACT normalized-path membership in a manifest (NFR-S4) | `bool` — never prefix/substring |

Invariants: every `RepoIntake` source file in EXACTLY ONE partition (total + disjoint); NO unit > hard ceiling;
plan byte-identical for the same repo@commit; manifest is the closed read allow-set.

### Decisions the dev must lock (record in the docstring + Change Log)

- **Module placement** — recommended `index/partitioner.py` (the architecture's locked home for FR3/FR4; the
  1.4 story explicitly deferred this file here). Do NOT put it under `ledger/` (2.3 lives there but is a file
  SET, not a graph partition). Keep ≤1200 lines (NFR-M1).
- **Partition algorithm** — a deterministic graph-clustering over the index edges, greedily filling units to
  the soft target then splitting at `context_pressure`, with a stable tie-break by sorted `file_path` so the
  result is order-independent. Lock the exact heuristic + the under-merge-on-unresolved-edge rule + document
  it (it freezes for the 7.1 dogfood + Epic-6 6.4 cut-edge consumer).
- **`partition_id` derivation** — sha256 over the sorted member paths (reuse the 1.1 content-hash helper if it
  fits). Lock the exact input shape (it is the `assignments/<id>.json` filename + the cache-key input later).
- **`Partition`/`PartitionPlan` field names + shape** — lock the names + the `seam_analysis` marker value +
  the cut-edge provenance shape (the 6.4 pass consumes it).
- **Permission-boundary primitive** — `is_in_scope(manifest, rel_path) -> bool` (exact normalized membership)
  + `read_in_scope(...)` (impure). Lock the path-normalization rule (POSIX, strip `./`, reject `..`) + the
  `PartitionScopeError` type.
- **Persist-now vs defer plan snapshot to Story 7.1** — per-unit `assignments/` manifests are the in-scope
  deliverable (the NFR-S4 boundary artifacts). Decide whether the plan snapshot also persists to `.apaa/state/`
  now or defers to the 7.1 dogfood pipeline; document the choice.
- **Typed error type** — `PartitionerError` (planner/contract) + `PartitionScopeError` (off-scope read), both
  `ValueError` subclasses localized to the module (mirror `RepoIntakeError` / `DepthSemanticsError` /
  `CriticalSubsystemError`).
- **Test area** — `APAA-INDEX` (continuing 1.4) recommended; `APAA-PARTITION` acceptable if the dev prefers a
  distinct area for the boundary tests — lock the choice.

### Precedent inherited from Stories 1.1–1.7 + 2.1–2.3 (done) — honor these decisions

- **No second serializer / reuse the 1.1 spine.** Any `.apaa/` bytes go through `store/canonical.dumps_bytes`
  via `EnvelopeWriter.build` + the writer; the AST gate enforces it.
- **Reuse the 1.3 store shell + `write_assignment`, do not re-implement.** `ApaaStorePaths` (containment,
  `assignments/` dir) + `ApaaStoreWriter.write_assignment` already provide the content-addressed,
  envelope-wrapped, containment-checked manifest write. REUSE verbatim; mirror the 1.3 round-trip golden.
- **Reuse the 1.4 index as the graph — do not re-parse / build a second index.** `build_ast_index` /
  `AstIndex` / `AstIndexEntry` / `CodeEdge` / `Definition` are the graph source; honor DF-1-4-A (unresolved
  edges → best-effort name→file map).
- **Frozen `extra="forbid"` models** (1.1 `Envelope`, 1.2 `Recording`/`CoverageLedger`/`Locator`, 1.4
  `RepoIntake`/`StackProfile`/`AstIndex`, 1.6 `AuditVerdict`, 2.1 `DepthEvidence`, 2.2 `CoverageReport`, 2.3
  `CriticalSubsystemSet`): any model this story adds follows the same pattern with a localized `schema_version`.
- **`bool`/`int`/closed-form/`str` over `float`** — every signal is non-`float`; the 1.1 serializer rejects it.
- **Single serializer (AR4, §3.3)** — any JSON routes through `store/canonical.dumps`.
- **Content-derived filenames, never arrival order (AR11)** — `partition_id` (sha256 over members) is the
  `assignments/` filename; never a counter / uuid / arrival index.
- **No absolute host paths in artifacts (NFR-S1 spirit, 1.3 DN-3 / 2.3)** — manifests carry repo-relative
  POSIX paths only; the run-state never records `repo_path`.
- **`apaa_version`/`schema_version` single source** — `minions_core/apaa/__init__.py::__version__`
  (`"0.1.0"`); per-module `schema_version` is a localized constant, never env/clock.
- **Import-isolation gate is seeded, extend it** — append the new module to `_MODULES_UNDER_GUARD`; do not fork.
- **AI-E1-1 non-ASCII fixtures (Epic-1 retro / §9.1)** — partitioning + manifests carry paths; tests include a
  non-ASCII path fixture (the 1.4 `git ls-files -z` / 2.1-2.3 `café_guard.py` precedent) placed intact +
  in-scope/cross-manifest-rejected.

### Source tree — files to create / update

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/index/partitioner.py` | NEW | FR3/NFR-SC1/NFR-S4 — pure graph-derived partition planner + frozen `Partition`/`PartitionPlan`/`WorkManifest` + content-derived `partition_id` + `is_in_scope` permission-boundary predicate + the V1 no-seam-analysis provenance (PURE core; `read_in_scope` impure helper may live here behind a clearly-marked impure section, or in the pipeline) |
| `minions_core/apaa/pipeline.py` | UPDATE (scope-fenced) | persist the partition plan + per-unit `work_manifest`s via `write_assignment` (compute the LOC map from `_read_source`); NO verdict-math change, NO multi-pass audit split |
| `tests/apaa/test_partitioner.py` | NEW | bounded-unit partitioning + content-derived stable ids + order-independence + total-and-disjoint + the permission-boundary (off-scope-read-impossible) + V1 no-seam provenance + purity/frozen/no-float/typed-error + non-ASCII (AI-E1-1) |
| `tests/apaa/test_assignments_roundtrip.py` | NEW (or extend `test_store_roundtrip.py`) | `write_assignment` → reader round-trip: equal model + byte-identical; `assignments/<partition_id>.json`; no absolute path/source byte |
| `tests/apaa/test_no_web_imports.py` | UPDATE | extend `_MODULES_UNDER_GUARD` with `minions_core.apaa.index.partitioner` |

Do NOT modify `index/ast_index.py`, `verdict/verdict_gate.py`, `ledger/coverage_ledger.py`,
`ledger/recording.py`, `ledger/depth_semantics.py` (`assess_criticality`), `ledger/critical_subsystems.py`,
`store/canonical.py`, `store/envelope.py`, `store/paths.py`, or `store/writer.py` (frozen/reused contracts —
verify no working-tree diff after the story; the ONLY exception is the additive `pipeline.py` persistence
touch + the import-isolation gate file).

### Scope fences (do NOT pull forward)

- ❌ **Any cross-partition SEAM AUDITOR** / `cross_partition` finding class / Prosecutor cut-edge pass (FR19) —
  **Story 6.4 [Tier B]**. V1 attempts NO seam analysis; the 6.4 pass is the V1 mitigation; full seam auditing
  is V2. This story RECORDS the cut edges + the limitation; it does NOT analyze them.
- ❌ The **multi-pass per-partition audit run loop** (audit each unit end-to-end + merge N ledgers) — the OI2
  dogfood, **Story 7.1/7.2**. This story builds the PLAN + the MANIFEST CONTRACT + persistence, NOT the N-unit
  run orchestration.
- ❌ The **$-budget ceiling cost accounting / `cost/budget_governor.py`** (FR21/FR22) — **Epic 3 / Story 3.1**.
  V1 bounds units by FILES + LOC (NFR-SC1), not $; OI3 defers the numeric default to Story 7.1.
- ❌ The **hardcoded-secret detector** (FR11) — Story 2.5; the **zero-token breadth tool runner** (FR14) —
  Story 2.6; the **LLM dispatch port / deep audit** (Epic 6).
- ❌ A **resolved call graph** (name binding / scope resolution) — Epic-6 depth (DF-1-4-A). V1 partitioning
  uses the unresolved 1.4 edge set best-effort.
- ❌ Any change to the **1.6 verdict gate / 1.2 ledger enum / `grade_entry` / 1.1 serializer / 1.4 index / 2.1
  `assess_criticality` / 2.3 critical-subsystem** contracts — all frozen/reused.
- ❌ A **new HTTP route / FastAPI surface / UI** (§3.7).

### Deferred-work seam (record if surfaced; do NOT build)

- **Cross-partition seam analysis (the V1 limitation itself)** — the full seam auditor is V2; the Story 6.4
  `cross_partition` Prosecutor cut-edge pass is the V1 mitigation. This is the OI2-locked decision, already
  tracked in the epics (Story 6.4 + 7.1). If a NEW defer beyond this surfaces during dev (e.g. the
  under-merge heuristic proves too coarse on the dogfood), record it with the CC-3 six-field schema; do NOT
  build it in this story.
- **DF-1-4-A (unresolved edge set)** — already open (owner Engineering Lead, target
  `epic-6-orphan-dead-code-detector`). This story CONSUMES the unresolved edge set best-effort and surfaces
  no new defer for it; it documents the under-merge-on-unresolved heuristic as the conservative V1 choice.

### Testing standards

- pytest under `tests/apaa/`; test ids follow `TC-<AREA>-<SEQ>-<SUBSEQ>` — use area `APAA-INDEX` (e.g.
  `TC-APAA-INDEX-001-NN`), continuing the 1.4 index area (or `APAA-PARTITION` if the dev locks a distinct area).
- The planner / contract / `is_in_scope` tests are **pure-function tests** (zero LLM tokens, NFR-D2; no temp
  dirs for the pure core) — build a synthetic `AstIndex` (fixture `AstIndexEntry`s + `CodeEdge`s) + an
  in-memory `loc_by_file` map; the manifest-persistence + `read_in_scope` tests USE the filesystem (impure
  shell) via `tmp_path` + the 1.3 store shell.
- **The bounded-unit proofs are MANDATORY** — an index exceeding 40 files / 15k LOC splits into ≥2 units each
  within the soft target / hard ceiling; a small index stays ONE unit; `context_pressure` flagged on a
  near-ceiling split; a single oversized file is its own context-pressured unit.
- **The total-and-disjoint partition-of-the-set proof is MANDATORY** — every `RepoIntake` source file in
  EXACTLY ONE partition (no file dropped — the AR1.4 non-ASCII-drop class is the cautionary precedent; no file
  in two units).
- **The permission-boundary proof is MANDATORY (NFR-S4)** — `is_in_scope` exact membership (in-scope pass;
  sibling-prefix `auth/secrets_extra.py` reject; traversal `../x.py` reject); `read_in_scope` reads in-scope +
  raises `PartitionScopeError` off-scope (the OFF-SCOPE-READ-IMPOSSIBLE proof).
- **Byte-stability / order-independence is MANDATORY (NFR-P1)** — same index+LOC in two input orderings →
  identical `PartitionPlan` + manifests + ids.
- **The V1 no-seam-analysis provenance proof is MANDATORY (OI2)** — the plan carries the
  `seam_analysis="v2-deferred"` marker + the cut-edge set is recorded-not-analyzed.
- **The non-ASCII path fixture is MANDATORY (AI-E1-1)** — a path like `auth/café_guard.py` or
  `модуль/безопасность.py` placed into a partition intact (not mojibake / not dropped) + in-scope for its own
  manifest + off-scope-rejected for a different manifest, round-tripped through the canonical serializer.
- **The assignments round-trip is MANDATORY** — `write_assignment` → `store/reader.py` → equal model +
  byte-identical re-serialize; filename `assignments/<partition_id>.json`; no absolute path / source byte.
- On Windows, prefix runs with `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on cp1252).
- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` (the WHOLE
  `tests/apaa/` suite, so the 1.1 single-serializer AST gate + the extended no-web-imports gate re-run with the
  new module present). All must pass before moving to `review`.
- `mypy` clean on the new + edited modules (`python run_mypy_per_file.py` or a scoped invocation).

### CLAUDE.md §4a follow-up

The §4a APAA Component→Driver row was added by Story 1.1. This story does NOT need a new §4a row; if a one-line
additive note is added it must note `index/partitioner.py` as the FR3/NFR-SC1 bounded-unit partitioner +
the NFR-S4 work-manifest permission boundary (with the honest V1 no-cross-partition-seam-analysis limitation),
and must NOT rewrite the existing row. Keep it minimal — a new row is not required.

### Project Structure Notes

- Alignment: the new module lives at `index/partitioner.py` — EXACTLY the architecture §Project Structure
  package-tree home for FR3/FR4 (`index/partitioner.py # FR3/FR4 — graph-derived partitions; context_pressure
  auto-downgrade`), the file the 1.4 story explicitly deferred to Story 2.4. Naming `snake_case.py`, ≤1200
  lines (NFR-M1). Enum/JSON values `snake_case`.
- No conflicts/variances. Judgment calls — all decided above and to be documented so they freeze for
  downstream (Story 6.4 cut-edge consumer + Story 7.1 dogfood): the partition algorithm + under-merge
  heuristic, the `partition_id` derivation, the `Partition`/`PartitionPlan` field shape + `seam_analysis`
  marker, the permission-boundary normalization rule + `PartitionScopeError`, the persist-now-vs-defer choice,
  and the typed-error types.
- Scope fence: this story delivers bounded-unit PARTITIONING (graph-derived, ≤40 files/15k LOC) + the
  work-manifest PERMISSION BOUNDARY (off-scope read impossible) + per-unit manifest persistence via the
  existing store shell + the V1 honest no-seam-analysis limitation ONLY. The cross-partition seam auditor
  (6.4 / V2), the multi-pass per-partition run loop (7.1/7.2), the $-budget accounting (3.1), the secret
  detector (2.5), the tool runner (2.6), the LLM/deep audit (Epic 6), and any change to the frozen 1.x/2.x
  contracts are explicitly NOT in scope. Plan + bound + manifest + the permission contract, then stop.

### References

- [Source: _bmad-output/design-artifacts/APAA/epics.md#Story-2.4 Repository partitioning into bounded audit units + work-manifest permission boundary] (the three ACs: multiple graph-derived ≤40-file/15k-LOC units with context_pressure auto-downgrade; the work_manifest IS the read permission boundary, off-scope read impossible; NO cross-partition seam analysis — the 6.4 cross_partition Prosecutor pass is the V1 mitigation, full seam auditor + non-"root" partition_id is V2)
- [Source: _bmad-output/design-artifacts/APAA/E-PRD/prd.md#FR3] ("APAA can partition the repository into bounded audit units within a declared budget")
- [Source: _bmad-output/design-artifacts/APAA/E-PRD/prd.md#NFR-S4] ("An auditor agent reads ONLY the files in its work-manifest (permission boundary); off-scope reads impossible")
- [Source: _bmad-output/design-artifacts/APAA/E-PRD/prd.md#NFR-SC1] ("V1 audit units ≤ 40 files / 15k LOC (hard ceiling ≤ 60 / 25k); larger repos partition. Full 10k→500k LOC scaling is V2")
- [Source: _bmad-output/design-artifacts/APAA/epics.md#Open delivery inputs OI2] (Minions-dogfood scope LOCKED full-repo multi-partition; V1 limitation = multi-UNIT auditing, NOT the V2 seam auditor; the cross_partition Prosecutor pass (Story 6.4) re-reads cut edges as the V1 mitigation; full seam analysis is V2)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#B. Repository Intake & Indexing] (Graph-derived partitioning, import/call graph not directories; ≤40 files/15k LOC units; context_pressure auto-downgrade)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#F. Persistence & State] (filesystem-as-contract .apaa/{state,assignments,findings,decisions}/; assignments/ = work_manifests = auditor permission boundaries NFR-S4)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Project Structure & Boundaries] (package tree: index/partitioner.py # FR3/FR4 — graph-derived partitions; .apaa/assignments/ = work_manifests = auditor permission boundaries NFR-S4; filesystem boundary: all writes via containment helper)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Pure/Impure Separation (master rule)] (index = impure shell; result models pure; the planner is pure over the recorded index + LOC inputs)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Determinism Patterns (NFR-P1/D1)] (one serializer; no float/clock/uuid/random/iteration-order; content-addressed filenames AR11)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Error / Degradation Patterns] (failure → typed error/recorded condition, never an uncaught raise; no bare except: pass / print())
- [Source: _bmad-output/design-artifacts/APAA/stories/1-4-tree-sitter-ast-index-repo-intake-python-stack-detection.md] (DONE — RepoIntake + AstIndex/AstIndexEntry/CodeEdge/Definition the partition graph folds over; partition_id="root" reserved; partitioner deferred HERE; DF-1-4-A unresolved-edge limitation)
- [Source: _bmad-output/design-artifacts/APAA/stories/1-3-apaa-store-writer-reader-filesystem-containment.md] (DONE — ApaaStorePaths assignments/ dir + ApaaStoreWriter.write_assignment to REUSE for manifest persistence; round-trip golden; is_relative_to containment rigor)
- [Source: _bmad-output/design-artifacts/APAA/stories/2-3-critical-subsystem-identification-operator-designation.md] (DONE — critical subsystem is a content-derived FILE SET, NOT a graph partition; partitioning proper deferred to THIS story; partition_id stays "root" there)
- [Source: minions_core/apaa/index/ast_index.py] (build_ast_index/AstIndex/AstIndexEntry/CodeEdge/Definition — the partition graph source to reuse)
- [Source: minions_core/apaa/store/paths.py + store/writer.py] (ApaaStorePaths assignments/ + ApaaStoreWriter.write_assignment — the manifest-persistence shell to reuse)
- [Source: minions_core/apaa/pipeline.py] (run_audit_detailed + _read_source — the impure orchestrator + per-file source read to reuse for the LOC map)
- [Source: minions_core/apaa/ledger/recording.py] (reserved partition_id field — this story supplies real per-unit values; do NOT re-shape the frozen model)
- [Source: CLAUDE.md §3.2 file-size / §3.7 headless-only / §3.8 12-Factor + secret masking / §3.4 evidence immutability / §9.1 L1-E11 retro carry-forward AI-E1-1]

## Dev Agent Record

### Context Reference
- Implemented by `/bmad-dev-story` (mode=implement) 2026-06-21.

### Agent Model Used
- claude-opus-4-8 (BMAD Developer worker).

### Completion Notes — locked decisions (frozen for Story 6.4 cut-edge consumer + Story 7.1 dogfood)

- **Module placement.** `minions_core/apaa/index/partitioner.py` (645 lines, ≤1200 NFR-M1) — the
  architecture's locked FR3/FR4 home that Story 1.4 deferred here. PURE planner core + a clearly-marked
  IMPURE shell section (`compute_loc_by_file`, `read_in_scope`); the frozen contract + `is_in_scope` are pure.
- **Partition algorithm (LOCKED).** Two-phase, deterministic, order-independent: (1) build a best-effort
  `Definition.name → file` map (a name defined in EXACTLY one file resolves; zero/multiple → dropped =
  DF-1-4-A under-merge), derive undirected cohesion pairs from the unresolved 1.4 `edges`, union-find into
  connected components (the cohesion **blobs**); (2) a blob that itself exceeds the soft target is split into
  context-pressured sub-units (`_split_oversized_component`), and the fitting blobs are greedily **bin-packed**
  (`_bin_pack`) into units ≤ the soft target. A unit capped because the next blob didn't fit is flagged
  `context_pressure`; the final never-capped unit is not. A single file > the hard LOC ceiling is its own
  context-pressured unit (cannot split below one file — AC1 boundary). Tie-break is sorted `file_path`
  throughout → byte-stable across two input orderings (proven by `test_plan_is_byte_stable_and_order_independent`).
- **`partition_id` derivation (LOCKED).** `sha256("\n".join(sorted(member_paths)).encode("utf-8"))` — the
  `assignments/<partition_id>.json` filename (AR11), never a counter/uuid/arrival order
  (`test_partition_id_is_sha256_over_sorted_members`).
- **Contract field shape (LOCKED).** `WorkManifest{schema_version, files: sorted tuple[str,...]}`,
  `Partition{schema_version, partition_id, work_manifest, file_count: int, total_loc: int,
  context_pressure: bool}`, `PartitionPlan{schema_version, partitions: sorted-by-id tuple, seam_analysis=
  "v2-deferred", cut_edges: tuple[CutEdge]}`, `CutEdge{caller_file, callee_file, callee}`. All
  `frozen=True, extra="forbid"`, localized `PARTITION_SCHEMA_VERSION="1"`. NO `float` anywhere (AR4).
- **Permission boundary (LOCKED).** `is_in_scope(manifest, rel_path)` = EXACT normalized-path set membership
  (NEVER prefix/substring — `auth/secrets_extra.py` vs `auth/secrets.py` rejected). `normalize_rel_path`
  strips a leading `./`, collapses `\` → `/`, and rejects absolute (leading `/`, drive-letter, PureWindowsPath
  absolute) + any `..` traversal segment with `PartitionScopeError`. `read_in_scope` reads ONLY on a scope
  pass, else raises `PartitionScopeError` (off-scope read impossible — NFR-S4).
- **Persist-now decision.** BOTH the per-unit `assignments/<partition_id>.json` work-manifests AND the
  partition-plan snapshot (to `state/`, content-addressed) persist in `run_audit_detailed` now — scope-fenced
  to ADD artifacts only (no verdict-math change, no multi-pass split). The single-unit / default run is
  otherwise byte-identical to pre-2.4 (existing pipeline + determinism tests stay green).
- **Typed errors (LOCKED).** `PartitionerError` (ValueError subclass; malformed input / bad LOC map / invalid
  limits) + `PartitionScopeError(PartitionerError)` (off-scope read). Persist failure degrades to the existing
  `PipelineError` (exit 1) via the unchanged analysis-stage try/except wrapping.
- **Test area.** `APAA-INDEX` (`TC-APAA-INDEX-001-80..104`) continuing the 1.4 index area; assignments
  round-trip under `APAA-STORE` (`TC-APAA-STORE-001-80/81`); pipeline e2e `TC-APAA-PIPELINE-001-13/14`.
- **No new defer surfaced.** The under-merge heuristic is the documented conservative V1 choice (DF-1-4-A
  already open). V1 records `seam_analysis="v2-deferred"` + the recorded-not-analyzed cut-edge set (the
  Story 6.4 seam). Frozen 1.1/1.2/1.4/1.6/2.1/2.3 contracts untouched (no working-tree diff).

### File List
- `minions_core/apaa/index/partitioner.py` (NEW)
- `minions_core/apaa/pipeline.py` (UPDATE — scope-fenced partition-plan + manifest persistence)
- `tests/apaa/test_partitioner.py` (NEW)
- `tests/apaa/test_assignments_roundtrip.py` (NEW)
- `tests/apaa/test_pipeline_signature_demo.py` (UPDATE — 2 partition-persistence e2e tests)
- `tests/apaa/test_no_web_imports.py` (UPDATE — `_MODULES_UNDER_GUARD` += partitioner)

### Validation
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **484 passed** (incl. the
  1.1 single-serializer AST gate + the extended no-web-imports gate, re-run with the new module present).
- `python -m mypy minions_core/apaa/index/partitioner.py minions_core/apaa/pipeline.py` → **clean**.

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-06-21 | 0.1.0 | FR3/NFR-SC1 graph-derived bounded-unit partitioner (`partition_repository`) + frozen `Partition`/`PartitionPlan`/`WorkManifest`/`CutEdge` contract (content-derived `partition_id`, `context_pressure` auto-downgrade) + the NFR-S4 work-manifest permission boundary (`is_in_scope` exact membership + `read_in_scope` off-scope-impossible) + scope-fenced pipeline persistence of per-unit manifests via the existing `write_assignment` shell + the V1 `seam_analysis="v2-deferred"` honest-limitation provenance with recorded-not-analyzed cut edges. 484 passed, mypy clean. | dev-story |

## Senior Developer Review (AI)

**Reviewer:** XAgentsLabs007 (BMAD adversarial code-review gate)
**Date:** 2026-06-21
**Outcome:** PASS — status `review → done`
**Iteration:** 1

### Scope reviewed

`minions_core/apaa/index/partitioner.py` (NEW, 645 lines / 539 non-blank), the scope-fenced `pipeline.py`
persistence touch (`_build_partition_plan` + `_persist_partitions` + the additive `run_audit_detailed` wiring),
the additive `__init__.py` `__version__`, and the four test files
(`test_partitioner.py`, `test_assignments_roundtrip.py`, the extended `test_pipeline_signature_demo.py` and
`test_no_web_imports.py`). Reviewed against the architecture (Decision B graph-derived partitioning, the
pure/impure master rule, the determinism patterns), the PRD drivers (FR3/NFR-SC1/NFR-S4/NFR-S5/NFR-P1/D2/M2),
and CLAUDE.md §3.2/§3.4/§3.7/§3.8.

### Verification (independently re-run)

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **486 passed** in 21.1s
  (the single-serializer AST gate + the extended no-web-imports gate re-run green with the new module present).
- `python -m mypy minions_core/apaa/index/partitioner.py minions_core/apaa/pipeline.py` → **Success: no issues**.
- File size: partitioner.py = 645 lines (≤1200, NFR-M1). No frozen 1.x/2.x contract diff (only the additive
  partitioner module + the scope-fenced pipeline persistence + the import-gate extension).

### Adversarial findings (the security/determinism/bounds keystones)

1. **Permission boundary (NFR-S4) — EXACT-membership, verified safe.** `is_in_scope` is
   `normalize_rel_path(rel_path) in frozenset(manifest.files)` — true set membership, NEVER a
   `str.startswith`/prefix/substring check. The sibling-prefix attack (`auth/secrets_extra.py` vs
   `auth/secrets.py`), the `auth/secrets` truncation, the bare-dir `auth`, the `../` traversal, and the
   cross-manifest non-ASCII case are all proven rejected (TC-APAA-INDEX-001-92/93/94/96/104). `normalize_rel_path`
   rejects absolute (POSIX leading `/`, `PureWindowsPath`-absolute, `C:`-drive-letter), UNC (`//…` → leading-`/`
   reject), and any `..` segment with `PartitionScopeError` BEFORE comparison; `read_in_scope` reads only on a
   scope pass — an off-scope read is impossible through the primitive. **No bypass found — this is the 1.3
   `is_relative_to` rigor applied correctly.**
2. **Determinism / byte-stability (NFR-P1) — verified.** Pure over `(index, loc_by_file)`; union-find merges the
   lexicographically-smaller root, components sort by first member, blobs bin-pack in sorted order, `partition_id`
   is `sha256("\n".join(sorted(members)))`, the plan sorts by `partition_id`, cut edges sort a tuple-set. The
   reversed-input order-independence + byte-identical canonical-dumps proof (TC-APAA-INDEX-001-90) passes. No
   clock/uuid/random/`os` (AST-scanned, TC-APAA-INDEX-001-102); no dict/set iteration-order reliance.
3. **Bounds (NFR-SC1) — hard ceiling holds.** `_bin_pack` opens a new unit when the next blob would push past the
   SOFT target, so a packed unit never exceeds soft (⊂ hard) on either dimension; `_split_oversized_component`
   flushes at soft. The only by-design hard-ceiling exception is a single file whose LOC exceeds the hard limit —
   it becomes its own context-pressured unit (cannot split below one file), documented and tested
   (TC-APAA-INDEX-001-85). The 200-file / hard-ceiling-respected proof passes (TC-APAA-INDEX-001-83).
   `context_pressure` auto-downgrade flagged on the near-ceiling split (TC-APAA-INDEX-001-84).
4. **V1 honesty (OI2/AC5) — verified.** `seam_analysis="v2-deferred"` recorded on every plan; cut edges are
   recorded-NOT-analyzed (`CutEdge` carries caller/callee_file/callee, derived from the unresolved DF-1-4-A edge
   set); the `_name_to_file` under-merge rule drops zero/multi-defined names (conservative — never over-merges,
   never silently drops a file). No cross-partition coverage is claimed.
5. **Total + disjoint partition-of-the-set — verified.** Every index file lands in exactly one unit (120-file
   proof TC-APAA-INDEX-001-91); a `parse_failed`/non-eligible file is still placed (TC-APAA-INDEX-001-88); the
   AI-E1-1 non-ASCII paths (`auth/café_guard.py`, `модуль/безопасность.py`) are placed intact and round-trip
   through the canonical serializer without mojibake/drop.
6. **Reuse + contract hygiene — verified.** Single serializer (no direct `json.dumps`; `build_plan_payload` is a
   thin `model_dump(mode="json")` routed through `store/canonical`); reuses 1.4 `AstIndex`, the 1.3
   `write_assignment` shell, the 1.1 envelope/canonical spine — no second writer/resolver/serializer. All models
   `frozen=True, extra="forbid"` with localized `PARTITION_SCHEMA_VERSION`; no `float` anywhere (counts/LOC are
   `int`). Typed errors (`PartitionerError`/`PartitionScopeError`) on every malformed input; pipeline persist
   failure degrades to the existing `PipelineError`. Headless — no route/UI/web import (gate green).

### Triage outcome

No `decision-needed`, no `patch`, no High/Med findings. Two **Low / dismiss-tier observations** (no action
required, recorded for the downstream 6.4/7.1 consumers, NOT deferred):

- `is_in_scope` normalizes the QUERY path but compares against the raw `manifest.files`. This is safe because
  manifest files are always emitted by the planner as clean sorted repo-relative POSIX paths (never `./`-prefixed
  or backslash forms), so the asymmetry cannot produce a false negative in practice. If a future caller ever
  constructs a `WorkManifest` by hand from un-normalized paths, normalizing the manifest side at construction
  would be belt-and-suspenders. Dismissed for V1 (no real defect; the only producer is the planner).
- `read_in_scope` relies on `normalize_rel_path`'s `..`/absolute rejection for repo-root confinement rather than
  an independent `is_relative_to(repo_root)` re-check. Equivalent in effect (a member path is traversal-free by
  construction), and the manifest membership is the authoritative gate. Dismissed — no escape is reachable.

### Conclusion

All seven ACs met; the security keystone (exact-membership permission boundary), determinism, hard-ceiling
bounds, and V1 honesty are correct and adversarially proven. Tests green, mypy clean, contracts frozen and
reused. **Verdict: PASS → `done`.**
