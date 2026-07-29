# Story 2.3: Critical-subsystem identification & operator designation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/APAA/`; the tracker is `_bmad-output/design-artifacts/APAA/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As a Delivery Orchestrator,
I want APAA to identify candidate critical subsystems by file CONTENT (and let me ADD or OVERRIDE designations
through the headless invocation contract) and require every critical subsystem to be examined deeply,
so that the verdict gate REFUSES `RELEASE_READY` when a critical subsystem was only shallowly seen — closing
the FR16 "all critical subsystems deep" clause that Stories 1.6 and 2.1 deliberately left as an additive seam
(the SECOND-half of FR4 and the THIRD story of Epic 2).

## Story Context

This is **Story 3 of Epic 2** (Full Coverage Ledger & Defect Detectors). Story 2.1 (done) built the
content-derived criticality ASSESSMENT (`assess_criticality(...)` → the closed `Criticality{CRITICAL, NORMAL}`
enum in `ledger/depth_semantics.py`) and proved FR8 over synthetic ledgers. Story 2.2 (done) built the
readable per-file coverage surface. **This story completes FR4 + the FR16 critical-subsystem clause:** it
(a) IDENTIFIES the set of critical files/subsystems for a repo by reusing the 2.1 `assess_criticality`, (b)
lets the OPERATOR add/override designations through the invocation contract, (c) computes the
`critical_subsystems_all_deep` boolean (a critical subsystem is "all deep" iff EVERY critical file is graded
`audited_deep`), and (d) FEEDS that boolean into the EXISTING 1.6 `evaluate_verdict(..., critical_subsystems_all_deep=...)`
seam so a critical-but-shallow subsystem withholds `RELEASE_READY` — **without forking the verdict math**.

**What already exists (REUSE verbatim, do NOT rebuild).** The mechanism this story completes is mostly
already present from Epic 1 + Story 2.1 — this is largely a **wire-the-seam + give-operator-precedence**
story, NOT a net-new verdict mechanism:

- **Story 2.1 (done) — `ledger/depth_semantics.py`.** `assess_criticality(*, file_path, source, ast_entry=None)
  -> Criticality` (content-derived, Unicode-aware via `str.casefold`, anti-rename-gaming) ALREADY EXISTS and
  is the canonical criticality ASSESSMENT. The closed `Criticality{CRITICAL, NORMAL}` enum, the
  `CRITICALITY_SIGNAL_TOKENS` locked V1 token set, and the `DepthSemanticsError` typed-error ALL EXIST.
  **REUSE `assess_criticality` verbatim — do NOT re-implement criticality detection, do NOT define a second
  criticality enum or a parallel token set.** This story's identifier CALLS it per file.
- **Story 1.6 (done) — `verdict/verdict_gate.py`.** The FR16 critical-subsystem clause is ALREADY a built-in,
  ADDITIVE seam: `evaluate_verdict(ledger, findings, *, critical_subsystems_all_deep: bool = True)` already
  ANDs `critical_subsystems_all_deep` into the `RELEASE_READY` condition (line: `deep_ratio >= 60% AND
  blocking == 0 AND critical_subsystems_all_deep`), and `AuditVerdict.critical_subsystems_all_deep: bool =
  True` is already a frozen field. The 1.6 docstring's "Critical-subsystem-clause seam (Story 2.3)" block
  documents this exact handoff: "Story 2.3 supplies the real value from the (then-built) critical-subsystem
  designation; this story builds only the gate that honors it." **Do NOT change the gate's threshold logic,
  do NOT add a gate parameter, do NOT touch the decision table — this story SUPPLIES the boolean the seam
  already consumes.** The default-`True` means a repo with NO critical subsystems (or none below deep) is
  byte-identical to today (regression-safe).
- **Story 2.1 (done) — `assess_criticality` Low finding (the precedence opportunity).** The 2.1 reviewer
  recorded a non-blocking Low: `assess_criticality` matches the locked tokens as **bare substrings** over the
  casefolded source, so benign code is over-flagged `CRITICAL` (a `tokenize` import, a `tokens` parameter, a
  "retry policy" comment all read `CRITICAL`). The error direction is the SAFE one (over-flagged → MORE
  scrutiny). The 2.1 review explicitly named "Story 2.3's operator designation/override is the documented seam
  to correct a misclassification." **This story builds that seam:** an operator designation/exclusion takes
  PRECEDENCE over the content heuristic (an operator may force a file CRITICAL the heuristic missed, OR mark a
  heuristic false-positive NORMAL). This story does NOT have to TIGHTEN the 2.1 substring matcher (that remains
  a deferred precision pass — see Scope fences); operator precedence is the V1 correction lever.
- **Story 1.7 / `pipeline.py` (done).** `run_audit_detailed` reads source per file, builds the AST index, grades
  per-file depths, builds the `CoverageLedger`, and calls `evaluate_verdict(ledger, tuple(findings))` (with NO
  critical clause today — defaulting to `True`). **This is the ONE call site this story rewires:** compute the
  critical-subsystem set + the `critical_subsystems_all_deep` boolean and pass it into `evaluate_verdict(...,
  critical_subsystems_all_deep=...)`. The per-file read + grading loop is otherwise unchanged.
- **`cli.py` (done) + `models.py::AuditRequest` (done, frozen `extra="forbid"`).** The LOCKED invocation
  contract is `apaa audit <repo> --commit <sha> --budget <int> --materiality-bar <bar>`. `AuditRequest` is
  frozen `extra="forbid"`, so the operator-designation channel is an ADDITIVE field + an ADDITIVE
  `--critical-subsystem`/`--exclude-critical` CLI flag (additive-only, NFR-M2 — pre-existing invocations stay
  valid by construction).

**The net-new deliverable of THIS story.** A pure critical-subsystem module — recommended
`ledger/critical_subsystems.py` (cohesive with the 2.1 `assess_criticality` it consumes; the architecture
maps FR4 to the partition/ledger layer, and partitioning proper is Story 2.4) — that provides:
1. a pure **identification** function over a set of (file_path, source[, ast_entry]) inputs that reuses 2.1
   `assess_criticality` to derive the heuristic critical set;
2. a pure **operator-designation merge** that applies operator ADD / OVERRIDE designations with PRECEDENCE over
   the content heuristic (operator-forced-critical ∪ heuristic-critical, MINUS operator-excluded), returning a
   frozen, deterministic critical-file set + provenance (heuristic vs operator-designated);
3. a pure **`critical_subsystems_all_deep(...)` predicate** that, given the critical set + the `CoverageLedger`,
   returns `True` iff every critical file is graded `audited_deep` (the boolean the 1.6 seam consumes);
4. the **pipeline wiring** that computes that boolean and feeds the existing `evaluate_verdict(...,
   critical_subsystems_all_deep=...)` seam;
5. the **additive invocation channel**: an `AuditRequest` field (e.g. `critical_paths`/`excluded_critical_paths`)
   + the `cli.py` flag that populates it.

It imports ONLY the 2.1 `depth_semantics` (`assess_criticality`/`Criticality`) + the 1.2 ledger models; the
pure modules are PURE (AR8) and join the import-isolation gate. The pipeline + CLI edits are the impure shell.

**Carry-forward from the Epic-1 retro (CLAUDE.md §9.1 / L1-E11 — this story discharges these items).**
- **AI-E1-1 (test-infra 🟠) — adversarial non-ASCII / locale fixtures.** Critical-subsystem identification
  matches over file PATHS + CONTENT (via 2.1 `assess_criticality`) and the operator designation channel
  carries file PATHS. Tests MUST include a **non-ASCII path + non-ASCII-identifier critical fixture** (e.g.
  `auth/café_guard.py`, `модуль/безопасность.py`) proven (a) identified critical by content and (b) designable
  + excludable by an operator path that round-trips intact (not mojibake / not dropped), reusing the 2.1
  `café_guard`/`vérifier_permission` precedent.
- **AI-E1-4 (process 🟢) — keep the committed gates extended-not-forked.** Append the new pure module(s) to
  `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py` (do NOT fork the no-web-imports gate); keep the
  single-serializer AST gate (`test_canonical_single_serializer.py`) green (any JSON of a designation set goes
  through `store/canonical.dumps`, never a direct `json.dumps`).
- **AI-E1-5 (process 🟢) — exercise the L1-E11 loop.** This story explicitly references the AI-E1-* items it
  discharges (here).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 2.3) and the architecture / PRD. Drivers: **APAA-FR-4** (APAA can
> identify critical subsystems AND an operator can designate them so coverage gates can require them examined
> deeply — the central driver), **APAA-FR-16** (the "all critical subsystems deep" clause of the coverage gate
> — `RELEASE_READY` withheld when a critical subsystem is below `audited_deep`; this story COMPLETES the clause
> the 1.6 gate left as a default-`True` seam), **APAA-FR-30** (the headless invocation contract — the additive
> operator-designation channel), **APAA-NFR-D2** (deterministic, zero-LLM-token — pure identification/predicate
> over recorded inputs), **APAA-NFR-P1** (byte-identical critical set + verdict across hosts/runs for the same
> repo+designations), **APAA-NFR-M2** (frozen, additive-only contracts — additive `AuditRequest` field + gate
> seam, no breaking change), **APAA-NFR-M1** (≤1200-line files), **AR3** (the gate exit-code wire contract is
> UNCHANGED — a critical-but-shallow repo routes to `NOT_READY_FOR_RELEASE`/exit `2`, the existing blocking
> code, NOT a new code), **AR4** (no `float`; closed enums / `bool` / `int`; single canonical serializer; no
> clock/uuid/random/iteration-order in any `.apaa/`-bound output), **AR8** (pure/impure separation — the
> identification + predicate are PURE; the file READ + pipeline wiring + CLI parse are the impure shell), **AR10**
> (typed failure, never an uncaught raise / silent coerce), cross-cutting (hostile-repo robustness: criticality
> by content + the operator override as the documented misclassification-correction lever).
>
> **SCOPE FENCE — Tier-A, single-purpose.** This story delivers ONLY: (1) pure critical-subsystem
> IDENTIFICATION reusing the 2.1 `assess_criticality`; (2) the pure operator-DESIGNATION merge (operator add /
> override / exclude, with PRECEDENCE over the heuristic); (3) the pure `critical_subsystems_all_deep(...)`
> predicate over the critical set + the 1.2 ledger; (4) the pipeline wiring that feeds the EXISTING 1.6
> `evaluate_verdict(..., critical_subsystems_all_deep=...)` seam; (5) the additive `AuditRequest` field + the
> additive `cli.py` flag for the operator channel. It does NOT build, and MUST NOT pull forward: **repository
> partitioning into bounded units / work-manifest / `partitioner.py`** (FR3 / NFR-S4 — Story 2.4 — a critical
> subsystem is a content-derived FILE SET in V1, NOT a graph partition; `partition_id` stays `"root"`); the
> **secret detector** (FR11 — Story 2.5); the **breadth tool runner** (FR14 — Story 2.6); the
> **negative-assurance scope statement** that would NARRATE which critical subsystems were/weren't covered
> (FR17 — Epic 4 Story 4.1; this story computes the gate boolean, not the prose); any change to the **1.6
> verdict THRESHOLDS / decision table / exit-code map** (the seam is consumed, not re-shaped), the **2.1
> `assess_criticality` substring matcher** (the operator override is the V1 correction lever; tightening the
> matcher to identifier-boundary is a deferred precision pass — see DF), the **1.2 enum / `grade_entry`**, or
> the **1.1 serializer**. It does NOT add a NEW HTTP route / FastAPI surface / UI (§3.7 — the operator channel
> is a CLI flag + an `AuditRequest` field). Wire the existing seam + give the operator precedence, then stop.

**AC1 — Critical subsystems are IDENTIFIED by content, reusing the 2.1 assessment (FR4)**
**Given** a repo's set of analyzable files (each with its `file_path`, in-memory `source`, and optionally the
1.4 `ast_entry`)
**When** the new `ledger/critical_subsystems.py` identification function runs
**Then** it derives the heuristic critical-file set by calling the EXISTING Story-2.1
`assess_criticality(*, file_path, source, ast_entry=...)` per file (REUSE verbatim — NO re-implementation, NO
second criticality enum, NO parallel token set) and collects every file assessed `Criticality.CRITICAL` into a
deterministic (sorted-by-`file_path`) frozen set, so a security-critical module renamed to a benign name (e.g.
`utils_misc.py` with auth/hmac content) is identified critical from its CONTENT — coverage-gaming-by-renaming
is defeated at the identification layer (the FR4 anti-gaming requirement)
**And** the identification is PURE (takes the already-read source/AST entries as in-memory ARGUMENTS — it never
opens a file; the impure caller does the read), deterministic, and relies on NO dict/set iteration order (AR4);
the result carries provenance distinguishing a heuristic-identified file from an operator-designated one
(AC2).

**AC2 — An operator can ADD / OVERRIDE / EXCLUDE designations, with PRECEDENCE over the heuristic (FR4, FR30)**
**Given** an operator-supplied set of designated-critical paths AND/OR excluded paths (via the invocation
contract — AC4)
**When** the designation merge runs over the heuristic set (AC1)
**Then** the final critical-file set is `(heuristic_critical ∪ operator_designated_critical) − operator_excluded`,
i.e. an operator can FORCE a file critical that the heuristic missed (a true critical the substring matcher did
not catch) AND can EXCLUDE a file the heuristic over-flagged (the documented correction for the 2.1 Low
substring-over-match finding) — **operator designation/exclusion takes PRECEDENCE over the content heuristic**
**And** the merge is PURE + deterministic (sorted output, no iteration-order reliance, AR4); an operator path
that matches no analyzable file is handled per a LOCKED, documented policy (recommended: a force-critical path
that is not in the analyzable set is RECORDED as designated-but-unmatched — it cannot be graded deep, so it
behaves conservatively toward withholding `RELEASE_READY`, OR is surfaced as a typed-warning per the dev's
locked decision; an exclude path that matches nothing is a no-op) — never a silent drop that would let an
operator typo quietly weaken the gate; the policy is documented in the module docstring + the Change Log
**And** the precedence + merge semantics are unit-tested: operator-force-critical adds a heuristic-NORMAL file;
operator-exclude removes a heuristic-CRITICAL file; the union/minus order is exercised (an excluded path wins
over both heuristic and force-critical if the same path is in both add and exclude — LOCK + document the
add-vs-exclude tie policy, recommended: exclude wins, so an explicit exclude is the unambiguous "this is not
critical" lever).

**AC3 — `critical_subsystems_all_deep` withholds `RELEASE_READY` when a critical file is below deep (FR16)**
**Given** the final critical-file set (AC2) + the completed `CoverageLedger` (1.2)
**When** the new pure `critical_subsystems_all_deep(critical_paths, ledger)` predicate runs
**Then** it returns `True` iff EVERY critical file appears in the ledger graded `CoverageDepth.AUDITED_DEEP`
(an empty critical set returns `True` — vacuously all-deep, the regression-safe default that keeps a
no-critical repo byte-identical to today); a critical file graded `audited_shallow` / `tool_scanned_only` /
`inferred` / `skipped` (or a designated-critical file ABSENT from the ledger, per the AC2 unmatched policy)
returns `False`
**And** that boolean is FED into the EXISTING 1.6 `evaluate_verdict(ledger, findings, *,
critical_subsystems_all_deep=<computed>)` seam at the pipeline call site — so a repo that is ≥60% deep with 0
blocking findings BUT has a critical subsystem only `audited_shallow` returns `NOT_READY_FOR_RELEASE` (exit
`2`), NOT `RELEASE_READY` (the FR16 clause the 1.6 gate left as a default-`True` seam is now SUPPLIED) — proven
by NAMED synthetic-ledger unit tests over the REAL `evaluate_verdict` (import-verified, NOT a fork): (a) a
clean ≥60%-deep ledger with a critical-shallow file → `NOT_READY_FOR_RELEASE`; (b) the SAME ledger with that
file `audited_deep` → `RELEASE_READY`; (c) a no-critical ledger is unchanged from the 1.6 default
(`critical_subsystems_all_deep=True`, byte-identical verdict)
**And** the 1.6 gate is NOT modified — the threshold logic, the decision table, the exit-code map, and the
`evaluate_verdict` signature are UNCHANGED; this story SUPPLIES the boolean argument the seam already accepts
(verify-and-lock: the 1.6 `verdict_gate.py` has no working-tree diff after this story).

**AC4 — The operator-designation channel is an ADDITIVE invocation field + CLI flag (FR30, NFR-M2, headless)**
**Given** the LOCKED V1 invocation contract `apaa audit <repo> --commit <sha> --budget <int> --materiality-bar
<bar>`
**When** an operator designates/excludes critical subsystems
**Then** the channel is purely ADDITIVE (NFR-M2 — pre-existing invocations stay valid by construction): a new
optional `AuditRequest` field (recommended `critical_paths: tuple[str, ...] = ()` and `excluded_critical_paths:
tuple[str, ...] = ()`, frozen `extra="forbid"`, both `tuple[str, ...]`, NEVER `float`, defaulting to empty so
the request round-trips byte-identically when unused — the 2.1/1.6 frozen-contract precedent) populated by a
new optional `cli.py` flag (recommended `--critical-subsystem <path>` repeatable / `action="append"` and
`--exclude-critical <path>` repeatable, stdlib `argparse` only — AR2; thin wiring, NO business logic in the
entrypoint — NFR-M1)
**And** the designation paths are recorded into the persisted run-state provenance via the EXISTING
`AuditRequest.to_provenance_payload()` (additive keys — the designation paths are repo-RELATIVE, secret-safe,
NOT absolute host paths; NFR-S1) so a reader of the `.apaa/` state can see which subsystems the operator
designated; the run-state still NEVER records `repo_path` (the 2.1/models precedent)
**And** the additive field + flag are documented as the LOCKED V1 designation contract in the module/CLI
docstrings; the existing exit-code wire contract is UNCHANGED (AR3 — a critical-shallow repo is
`NOT_READY_FOR_RELEASE`/exit `2`, the EXISTING blocking code, never a new code) — this is NOT a wire-contract
change (no new HTTP route, no exit-code added/changed).

**AC5 — The new pure modules are PURE, frozen-contract, deterministic, and import-isolated (NFR-D2, NFR-P1, AR8, AR10, M2)**
**Given** `ledger/critical_subsystems.py` (and any frozen model it defines)
**When** it is imported and exercised in unit tests
**Then** the identification + designation-merge + `critical_subsystems_all_deep` predicate perform NO filesystem
I/O, NO clock read (`datetime.now`/`time.time`), NO `uuid4`/`os.getpid()`/`random`, NO LLM/network call, NO
dict/`set`-iteration-order reliance — they are PURE functions over in-memory inputs (the file READ + pipeline
wiring + CLI parse are the impure shell)
**And** any model it defines (e.g. a frozen `CriticalSubsystemSet` carrying the sorted critical paths + per-path
provenance) is a frozen Pydantic v2 model (`frozen=True, extra="forbid"` — the 1.1/1.2/1.6/2.1 precedent) with
a localized `schema_version` constant (additive-only, NFR-M2); NO `float` anywhere (criticality is the closed
2.1 `Criticality` enum; the predicate returns `bool`; counts are `int` — AR4); any JSON rendering routes through
`store/canonical.dumps` (the single 1.1 serializer — no second `json.dumps`)
**And** a malformed input (a non-`str` designation path, a non-`CoverageLedger` argument to the predicate, a
non-iterable designation set) raises a typed error — a `ValueError` subclass localized to the module (mirroring
`DepthSemanticsError` / `CoverageReportError` / `RecordingValidationError`) — never a silent coerce / bare
`except: pass` / `print()` in library code (AR10)
**And** `minions_core.apaa.ledger.critical_subsystems` is appended to `_MODULES_UNDER_GUARD` in
`tests/apaa/test_no_web_imports.py` (extend, do NOT fork) and importing it does NOT transitively import
`fastapi`/`uvicorn`/`starlette` or any LLM/api/writer module (assert absence from `sys.modules`).

**AC6 — The whole APAA suite green; tests cover identification + designation + the gate clause honestly; mypy clean; ≤1200 lines (NFR-M1)**
**Given** the modules + tests added/edited by this story
**When** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` runs
**Then** all pass, including new tests in `tests/apaa/test_critical_subsystems.py`: AC1 content-identification
(benign-named-but-critical identified; benign not; reuses the REAL 2.1 `assess_criticality` — import-verified);
AC2 operator precedence (force-critical adds a heuristic-NORMAL file; exclude removes a heuristic-CRITICAL file;
the add-vs-exclude tie policy; the unmatched-path policy); the **MANDATORY AC3 FR16 synthetic-ledger proofs**
(critical-shallow → `NOT_READY_FOR_RELEASE`/exit `2`; same-file-deep → `RELEASE_READY`; no-critical →
unchanged from the 1.6 default — all over the REAL `evaluate_verdict`); AC4 the additive `AuditRequest` field +
the `cli.py` flag (a repeatable `--critical-subsystem`/`--exclude-critical` populates the request; an invocation
WITHOUT the flag is byte-identical to today); AC5 purity (AST scan) / frozen / no-`float` / typed-error / single
serializer; the **AI-E1-1 non-ASCII path + identifier** fixture identified + designable + excludable intact
**And** an end-to-end pipeline test (extending the 1.7 signature-demo style) proves the wired pipeline:
a fixture repo with a critical file graded below `audited_deep` yields `NOT_READY_FOR_RELEASE`/exit `2` via
the wired `evaluate_verdict(..., critical_subsystems_all_deep=...)`, and the SAME repo with that file deep (or
the operator excluding it) yields the expected non-withheld verdict — and a repo with NO critical files +
NO operator designation is byte-identical to the pre-2.3 pipeline (the regression-safe default)
**And** `ledger/critical_subsystems.py` is appended to `_MODULES_UNDER_GUARD` and the import-isolation gate
stays green; the 1.1 single-serializer AST gate still passes with the new module present (no direct `json.dumps(`);
the new source file(s) are ≤1200 lines (NFR-M1) and cite their `APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in the
module docstring; `mypy` is clean on the new + edited modules. The 1.6 gate / 1.2 enum / 1.1 serializer / 2.1
`assess_criticality` are UNCHANGED (this story adds module(s) + tests + the additive `AuditRequest` field + the
additive CLI flag + the single pipeline call-site wiring; it modifies the import-isolation gate file, `models.py`,
`cli.py`, and `pipeline.py` — but NOT the frozen verdict/enum/serializer/criticality contracts).

## Tasks / Subtasks

- [x] **Task 0 — Verify the existing seam + reuse surface (verify-and-lock)** (AC: 1, 3)
  - [x] Re-read `verdict/verdict_gate.py`: confirm `evaluate_verdict(..., critical_subsystems_all_deep: bool =
        True)` and `AuditVerdict.critical_subsystems_all_deep` exist and need NO change. SUPPLY the boolean;
        do NOT modify the gate.
  - [x] Re-read `ledger/depth_semantics.py`: confirm `assess_criticality(*, file_path, source, ast_entry=None)
        -> Criticality` + `Criticality{CRITICAL, NORMAL}` exist. REUSE verbatim — do NOT re-implement.
  - [x] Re-read `pipeline.py`: confirm the single `evaluate_verdict(ledger, tuple(findings))` call site in
        `run_audit_detailed` (the ONE site to rewire). Confirm source is read per file (`_read_source`) so the
        critical set can be computed from the same in-memory source.
  - [x] Re-read `models.py::AuditRequest` (frozen `extra="forbid"`, `to_provenance_payload`) + `cli.py` (the
        LOCKED contract + `_summary_line`) — the additive field + flag attach here.
- [x] **Task 1 — `ledger/critical_subsystems.py`: pure identification + designation merge + predicate** (AC: 1, 2, 3, 5)
  - [x] Create `minions_core/apaa/ledger/critical_subsystems.py` (docstring cites the drivers + the LOCKED
        decisions). Pure identification reusing 2.1 `assess_criticality` per file.
  - [x] Pure designation merge: `(heuristic ∪ operator_designated) − operator_excluded`, sorted output,
        provenance per path; LOCK + document the add-vs-exclude tie (exclude wins) + the unmatched-path policy.
  - [x] Pure `critical_subsystems_all_deep(critical_paths, ledger) -> bool` (True iff every critical path is
        `AUDITED_DEEP`; empty set → True). Frozen `CriticalSubsystemSet` (`frozen=True, extra="forbid"`,
        localized `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION`); `CriticalSubsystemError` (ValueError subclass) on
        malformed input (AR10). No `float`; no I/O/clock/LLM (pinned by the AST test).
- [x] **Task 2 — Additive invocation channel: `AuditRequest` field + `cli.py` flag** (AC: 4)
  - [x] Add optional `critical_paths: tuple[str, ...] = ()` + `excluded_critical_paths: tuple[str, ...] = ()`
        to `AuditRequest` (frozen, additive, default empty → byte-identical when unused); add them to
        `to_provenance_payload()` (repo-relative, secret-safe; still NEVER `repo_path`).
  - [x] Add repeatable `--critical-subsystem` (`action="append"`) + `--exclude-critical` to `cli.py`
        (stdlib argparse, thin wiring); populate the request. NO business logic in the entrypoint.
- [x] **Task 3 — Pipeline wiring (the ONE call site)** (AC: 3, 6)
  - [x] In `run_audit_detailed`: build the critical set from the per-file in-memory source (reusing the
        already-read `_read_source` output + index entries) + the operator designations, compute
        `critical_subsystems_all_deep(...)`, and pass it into `evaluate_verdict(ledger, tuple(findings),
        critical_subsystems_all_deep=<computed>)`. A no-critical/no-designation run stays byte-identical (the
        default-True path). Keep the impure-shell typed-error contract (AR10) intact.
- [x] **Task 4 — Tests** (AC: 1, 2, 3, 4, 5, 6)
  - [x] `tests/apaa/test_critical_subsystems.py` — AC1 content-identification (reuses the REAL 2.1
        `assess_criticality`, import-verified); AC2 operator precedence (force/exclude/tie/unmatched); the
        **MANDATORY AC3 FR16 synthetic-ledger proofs** over the REAL `evaluate_verdict`
        (critical-shallow → NOT_READY/exit 2; same deep → RELEASE_READY; no-critical → unchanged default);
        AC5 purity (AST scan) / frozen / no-float / typed-error / single serializer; **AI-E1-1 non-ASCII path +
        identifier** identified + designable + excludable intact. Test area `APAA-LEDGER`
        (`TC-APAA-LEDGER-001-NN`, continuing the 1.2/2.1/2.2 area); zero LLM tokens.
  - [x] Extend the CLI test (`test_cli.py`) for the additive flags (repeatable; absent → byte-identical) and
        add/extend a pipeline e2e test (`test_pipeline_signature_demo.py` style) proving the wired clause
        end-to-end (critical-shallow → exit 2; deep/excluded → expected; no-critical → byte-identical).
- [x] **Task 5 — Extend the import-isolation gate** (AC: 5, 6)
  - [x] Append `minions_core.apaa.ledger.critical_subsystems` to `_MODULES_UNDER_GUARD` (extend, do NOT fork).
- [x] **Task 6 — Run + mypy** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass (the 1.1
        single-serializer AST gate + the extended no-web-imports gate re-run green with the new module present).
  - [x] `mypy` clean on the new + edited modules (`ledger/critical_subsystems.py`, `models.py`, `cli.py`,
        `pipeline.py`).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **This is a WIRE-THE-SEAM + operator-precedence story, not a new verdict mechanism.** The FR16
  critical-subsystem clause is ALREADY built into the 1.6 gate as the additive `critical_subsystems_all_deep:
  bool = True` parameter; the 2.1 `assess_criticality` ALREADY derives content-criticality. The net-new
  artifacts are: (a) the pure identification (reuse 2.1) + operator-designation merge; (b) the pure
  `critical_subsystems_all_deep` predicate; (c) the single pipeline call-site wiring; (d) the additive
  `AuditRequest` field + CLI flag. **Resist re-shaping the 1.6 gate or re-implementing criticality** — both are
  frozen/reused contracts. Changing the gate signature/thresholds or forking `assess_criticality` is OUT of
  scope and breaks §3.3 reuse-canonical.
- **EXTEND the gate via the existing additive seam — do NOT fork the verdict math (the moat + locked
  vocabulary stay intact).** The 1.6 decision table (floor-first; `RELEASE_READY` requires ≥60% deep AND 0
  blocking AND `critical_subsystems_all_deep`), the three-member `Verdict` enum, the advisory-by-contract
  `depth_supported is not None` moat, the FR33 ordering, and the AR3 exit-code map are ALL frozen. This story
  supplies ONE boolean into the seam the gate already exposes. The exit code for a critical-shallow repo is the
  EXISTING `NOT_READY_FOR_RELEASE`/`2` — NOT a new code (AR3 unchanged, no wire-contract change).
- **FR4 is the central driver (identify + designate critical subsystems).** Identification is content-derived
  (anti-rename-gaming, reusing 2.1); designation is operator-supplied with PRECEDENCE over the heuristic. The
  union/minus merge is the V1 model: a critical subsystem is a content-derived + operator-adjusted FILE SET,
  NOT a graph partition (partitioning proper is Story 2.4; `partition_id` stays `"root"`).
- **Operator precedence is the documented correction for the 2.1 substring Low finding.** The 2.1 reviewer
  named "Story 2.3's operator designation/override is the documented seam to correct a misclassification." This
  story IS that seam: `--exclude-critical <path>` lets an operator drop a heuristic false-positive (a `tokenize`
  import wrongly read CRITICAL), and `--critical-subsystem <path>` lets an operator force a true critical the
  substring matcher missed. **This story does NOT have to tighten the 2.1 matcher** (identifier-boundary
  matching is a deferred precision pass — see DF below); operator precedence is the V1 correction lever.
- **Empty-critical-set default is the regression-safety keystone.** `critical_subsystems_all_deep(∅, ledger)`
  is `True` (vacuously all-deep), and a no-critical/no-designation pipeline run passes `True` into
  `evaluate_verdict` — byte-identical to the pre-2.3 default. The wired clause can ONLY withhold
  `RELEASE_READY`, never grant it, and only when a real critical-below-deep file exists. Pin a "no-critical →
  byte-identical verdict" regression test.
- **No floats — ever (AR4 / Determinism / NFR-P1).** Criticality is the closed 2.1 `Criticality` enum; the
  predicate returns `bool`; counts are `int`; designation paths are `str`. A criticality SCORE would be the
  obvious float trap — there is none. Any JSON of a designation/critical set routes through the single 1.1
  `store/canonical.dumps` (which rejects `float`); the AST gate forbids a second `json.dumps`.
- **Pure/impure separation (master rule, AR8).** `ledger/critical_subsystems.py` is PURE — identification +
  merge + predicate over in-memory inputs; it never opens a file or reads a clock. The IMPURE shell is the
  pipeline (which already reads source via `_read_source` — reuse that output to feed identification) + the CLI
  (argv parse). ✅ a pure predicate over `(critical_paths, ledger)` · ❌ a function that re-reads the repo or
  calls `datetime.now()`.
- **Determinism (NFR-P1).** Critical-set output is sorted by `file_path`; the merge relies on no set-iteration
  order; the same repo+designations yields a byte-identical critical set + verdict across hosts/runs. Pin a
  byte-stability/order-independence test (same designations in two input orders → identical result).
- **Error/degradation → typed, never crash (AR10).** A malformed designation path / a non-`CoverageLedger`
  predicate arg → a typed `CriticalSubsystemError` (ValueError subclass) localized to the module. NO bare
  `except: pass`, NO `print()` in library code, NO silent coerce. The pipeline keeps its existing typed-fatal
  wrapping (`PipelineError`) so a designation failure degrades to exit `1`, never an uncaught traceback.
- **Headless / import boundary (§3.7, AR7/AR9).** The operator channel is a CLI flag + a frozen-model field —
  NOT a UI, NO HTML/CSS/JS, NO FastAPI route. APAA is downstream of the HTTP/A2A boundary; the new pure module
  takes no token, registers no route, imports no web/LLM stack, and joins `_MODULES_UNDER_GUARD`.

### The critical-subsystem model (the AC1/AC2/AC3 reference — lock + document)

| concept | source | form |
|---|---|---|
| heuristic critical set | per-file `assess_criticality(...)` == `Criticality.CRITICAL` (2.1, REUSE) | sorted `tuple[str, ...]` of `file_path` |
| operator-designated critical | `AuditRequest.critical_paths` (CLI `--critical-subsystem`, repeatable) | `tuple[str, ...]`, repo-relative |
| operator-excluded | `AuditRequest.excluded_critical_paths` (CLI `--exclude-critical`, repeatable) | `tuple[str, ...]`, repo-relative |
| FINAL critical set | `(heuristic ∪ operator_designated) − operator_excluded` (exclude wins on a tie) | sorted `tuple[str, ...]` |
| `critical_subsystems_all_deep` | `True` iff every FINAL critical path is `AUDITED_DEEP` in the ledger (∅ → True) | `bool` → the 1.6 seam |

The `RELEASE_READY` condition (1.6, UNCHANGED): `deep_ratio >= 60% AND blocking == 0 AND
critical_subsystems_all_deep`. This story supplies the third conjunct.

### Decisions the dev must lock (record in the docstring + Change Log)

- **Module placement** — recommended `ledger/critical_subsystems.py` (cohesive with the 2.1
  `depth_semantics.assess_criticality` it consumes; partitioning proper is `index/partitioner.py`, Story 2.4 —
  do NOT put this there). Do NOT create a top-level module if it fits here (NFR-M1; the module will be small).
- **`AuditRequest` field names + shape** — recommended `critical_paths: tuple[str, ...] = ()` +
  `excluded_critical_paths: tuple[str, ...] = ()` (frozen `extra="forbid"`, additive, default empty). Lock the
  names + `to_provenance_payload` keys.
- **CLI flag names** — recommended `--critical-subsystem` (`action="append"`, repeatable) + `--exclude-critical`
  (repeatable). Lock the names + the dest mapping into the request.
- **Add-vs-exclude tie policy** — recommended EXCLUDE WINS (an explicit exclude is the unambiguous
  "not critical" lever). Lock + document.
- **Unmatched-path policy** — recommended: a force-critical path not in the analyzable set is RECORDED as
  designated-but-unmatched and behaves conservatively (it cannot be graded deep → withholds `RELEASE_READY`),
  OR surfaces a typed-warning — DECIDE + document; an exclude path matching nothing is a no-op. Never a silent
  drop that lets an operator typo quietly weaken the gate.
- **Critical-set provenance** — a frozen `CriticalSubsystemSet` carrying the sorted final paths + a per-path
  origin (heuristic / operator-designated). Lock the model shape; localized `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION`.
- **Typed error type** — `CriticalSubsystemError`, a `ValueError` subclass localized to the module (mirror
  `DepthSemanticsError` / `CoverageReportError` / `RecordingValidationError`).

### Precedent inherited from Stories 1.1–1.7 + 2.1 + 2.2 (done) — honor these decisions

- **No second criticality enum / no second token set / no fork of `assess_criticality`.** Reuse the 2.1
  `Criticality` + `assess_criticality` + `CRITICALITY_SIGNAL_TOKENS` verbatim. The import-isolation gate + the
  identifier reuse enforce it.
- **No re-shape of the 1.6 gate / no second verdict math.** Supply the boolean into the existing
  `evaluate_verdict` seam; the gate is frozen.
- **Frozen `extra="forbid"` models** (1.1 `Envelope`, 1.2 `Recording`/`CoverageLedger`, 1.6 `AuditVerdict`,
  2.1 `DepthEvidence`, 2.2 `CoverageReport`/`DepthAggregate`): any model this story adds follows the same
  pattern with a localized `schema_version`.
- **`bool`/`int`/closed-enum/`str` over `float`** — every signal is non-`float`; the 1.1 serializer rejects
  `float`.
- **Single serializer (AR4, §3.3)** — any JSON routes through `store/canonical.dumps`; the AST gate forbids a
  direct `json.dumps`.
- **`apaa_version`/`schema_version` single source** — `minions_core/apaa/__init__.py::__version__`
  (`"0.1.0"`); per-module `schema_version` is a localized constant, never env/clock.
- **Test-area precedent** — use area `APAA-LEDGER` (`TC-APAA-LEDGER-001-NN`), continuing the 1.2/2.1/2.2 area.
- **Import-isolation gate is seeded, extend it** — append the new module to `_MODULES_UNDER_GUARD`; do not fork.
- **AI-E1-1 non-ASCII fixtures (Epic-1 retro / §9.1)** — identification matches over paths/content and the
  designation channel carries paths, so tests include a non-ASCII path + identifier fixture (the 2.1
  `café_guard.py` / `vérifier_permission` precedent), proven identified + designable + excludable intact.

### Source tree — files to create / update

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/ledger/critical_subsystems.py` | NEW | FR4/FR16 — pure identification (reuse 2.1) + operator-designation merge + `critical_subsystems_all_deep` predicate + frozen `CriticalSubsystemSet` (PURE) |
| `minions_core/apaa/models.py` | UPDATE (additive) | optional `critical_paths` + `excluded_critical_paths` frozen fields + `to_provenance_payload` keys |
| `minions_core/apaa/cli.py` | UPDATE (additive) | repeatable `--critical-subsystem` / `--exclude-critical` flags → populate the request (thin wiring) |
| `minions_core/apaa/pipeline.py` | UPDATE (one call site) | compute the critical set + `critical_subsystems_all_deep` and feed `evaluate_verdict(..., critical_subsystems_all_deep=...)` |
| `tests/apaa/test_critical_subsystems.py` | NEW | identification + operator precedence + the MANDATORY FR16 gate-clause proofs + purity/frozen/no-float/typed-error + non-ASCII (AI-E1-1) |
| `tests/apaa/test_cli.py` | UPDATE | the additive flags (repeatable; absent → byte-identical) |
| `tests/apaa/test_pipeline_signature_demo.py` | UPDATE/NEW e2e | wired clause end-to-end (critical-shallow → exit 2; deep/excluded → expected; no-critical → byte-identical) |
| `tests/apaa/test_no_web_imports.py` | UPDATE | extend `_MODULES_UNDER_GUARD` with the new module |

Do NOT modify `verdict/verdict_gate.py`, `ledger/depth_semantics.py` (`assess_criticality`),
`ledger/coverage_ledger.py`, `ledger/recording.py`, or `store/canonical.py` (frozen/reused contracts — verify
no working-tree diff after the story). Do NOT create `index/partitioner.py` (Story 2.4).

### Scope fences (do NOT pull forward)

- ❌ **Repository partitioning into bounded units / work-manifest / `partitioner.py`** (FR3 / NFR-S4) — Story
  2.4. A critical subsystem is a content-derived + operator-adjusted FILE SET in V1, NOT a graph partition;
  `partition_id` stays `"root"`.
- ❌ The **hardcoded-secret detector + producer-side redaction** (FR11/FR28) — Story 2.5.
- ❌ The **zero-token breadth tool runner** (FR14) — Story 2.6.
- ❌ The **negative-assurance scope statement** narrating which critical subsystems were/weren't covered
  (FR17) — Epic 4 Story 4.1. This story computes the gate BOOLEAN, not the prose.
- ❌ **Tightening the 2.1 `assess_criticality` substring matcher** to identifier-boundary / dotted-reference
  matching — a deferred precision pass (operator override is the V1 correction lever; see DF-2-3-A below).
- ❌ Any change to the **1.6 verdict THRESHOLDS / decision table / exit-code map / `evaluate_verdict`
  signature**, the **1.2 enum / `grade_entry`**, or the **1.1 serializer** — all frozen. This story SUPPLIES
  the seam boolean + RENDERS no new verdict.
- ❌ A **new HTTP route / FastAPI surface / UI** (§3.7) — the operator channel is a CLI flag + a frozen-model
  field.

### Deferred-work seam (record if surfaced; do NOT build)

- **DF-2-3-A (process / precision, 🟢)** — the 2.1 `assess_criticality` bare-substring matcher over-flags benign
  tokens (`tokenize`, a `tokens` param, "retry policy"). The SAFE direction (over-flag → more scrutiny) + the
  operator `--exclude-critical` override make this non-blocking for V1. A future precision pass may tighten the
  matcher to identifier-boundary / import-name / dotted-reference signals. Owner: QA Lead. Target: a 2.x
  precision pass (or Epic-6 trust-substrate). NOT in this story's scope.

### Testing standards

- pytest under `tests/apaa/`; test ids follow `TC-<AREA>-<SEQ>-<SUBSEQ>` — use area `APAA-LEDGER` (e.g.
  `TC-APAA-LEDGER-001-NN`), continuing the 1.2/2.1/2.2 ledger area.
- These are **pure-function / synthetic-ledger tests** for the identification + predicate (zero LLM tokens,
  NFR-D2; no temp dirs for the pure module) PLUS an impure pipeline e2e test (real fixture repo via the 1.7
  signature-demo harness). Build synthetic ledgers via `CoverageLedger.build([grade_entry(file_path=...,
  proposed_depth=CoverageDepth.X, claim_present=...), ...])`.
- **The FR16 gate-clause proofs are MANDATORY** — over the REAL 1.6 `evaluate_verdict` (import-verified, NOT a
  fork): a clean ≥60%-deep ledger with a critical-shallow file → `NOT_READY_FOR_RELEASE`/exit `2`; the SAME
  ledger with that file `audited_deep` → `RELEASE_READY`; a no-critical ledger → byte-identical to the 1.6
  default (`critical_subsystems_all_deep=True`).
- **Operator-precedence proofs are MANDATORY** — force-critical adds a heuristic-NORMAL file; exclude removes a
  heuristic-CRITICAL file; the add-vs-exclude tie (exclude wins); the unmatched-path policy.
- **Byte-stability / order-independence** — same designations in two input orders → identical critical set +
  verdict (NFR-P1).
- **The non-ASCII path + identifier fixture is MANDATORY** (AI-E1-1) — a path like `auth/café_guard.py` or
  `модуль/безопасность.py` identified critical by content AND designable/excludable by an operator path
  round-tripped intact (not mojibake / not dropped).
- **The additive-channel regression is MANDATORY** — an invocation WITHOUT the new flags + a repo with NO
  critical files is byte-identical to the pre-2.3 pipeline (the default-True path).
- On Windows, prefix runs with `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on cp1252).
- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` (the WHOLE
  `tests/apaa/` suite, so the 1.1 single-serializer AST gate + the extended no-web-imports gate re-run with the
  new module present). All must pass before moving to `review`.
- `mypy` clean on the new + edited modules (`python run_mypy_per_file.py` or a scoped invocation).

### CLAUDE.md §4a follow-up

The §4a APAA Component→Driver row was added by Story 1.1. This story does NOT need a new §4a row; if a one-line
additive note is added it must note `ledger/critical_subsystems.py` as the FR4/FR16 critical-subsystem
identification + operator designation + the wired `critical_subsystems_all_deep` clause, and must NOT rewrite
the existing row. Keep it minimal — a new row is not required.

### Project Structure Notes

- Alignment: the new module lives under `ledger/` (cohesive with the 2.1 `depth_semantics` it consumes; the
  architecture maps FR4 to the partition/ledger layer, and partitioning proper is `index/partitioner.py`, Story
  2.4 — not this story). Naming `snake_case.py`, ≤1200 lines (NFR-M1). Enum/JSON values `snake_case`.
- No conflicts/variances. Judgment calls — all decided above and to be documented so they freeze for downstream:
  the module placement, the `AuditRequest` field names + shape, the CLI flag names, the add-vs-exclude tie
  policy, the unmatched-path policy, the critical-set provenance model, and the typed-error type.
- Scope fence: this story delivers critical-subsystem IDENTIFICATION (reuse 2.1) + operator DESIGNATION + the
  `critical_subsystems_all_deep` predicate wired into the EXISTING 1.6 gate seam + the additive invocation
  channel ONLY. Partitioning (2.4), the secret detector (2.5), the breadth tool runner (2.6), the
  negative-assurance scope prose (4.1), tightening the 2.1 matcher (DF-2-3-A), and any change to the 1.6 gate /
  1.2 enum / 1.1 serializer / 2.1 `assess_criticality` are explicitly NOT in scope. Wire the seam, give the
  operator precedence, then stop.

### References

- [Source: _bmad-output/design-artifacts/APAA/epics.md#Story-2.3 Critical-subsystem identification & operator designation] (the two ACs: identify candidates by content + operator add/override via the invocation contract; a designated critical subsystem below `audited_deep` withholds `RELEASE_READY` — completes the FR16 critical-subsystem clause)
- [Source: _bmad-output/design-artifacts/APAA/E-PRD/prd.md#FR4] ("APAA can identify critical subsystems (and an operator can designate them) so coverage gates can require them to be examined deeply")
- [Source: _bmad-output/design-artifacts/APAA/E-PRD/prd.md#FR16] ("emit a verdict only when coverage gates are met (≥60% deep + all critical subsystems deep + 0 blocking findings)")
- [Source: _bmad-output/design-artifacts/APAA/E-PRD/prd.md#Hostile / low-quality-repo robustness] ("Coverage gaming (criticality detected by content, not filename)")
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Package tree] (`index/partitioner.py # FR3/FR4` — partitioning is Story 2.4; criticality identification reuses the 2.1 ledger-layer `assess_criticality`)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Determinism Patterns] (one serializer; no floats; no iteration-order reliance; byte-identical across hosts NFR-P1)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Pure/Impure Separation (master rule)] (identification/predicate pure — no I/O, no clock, no LLM; the pipeline/CLI is the impure shell)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Architectural Boundaries] (APAA downstream of HTTP/A2A; no web surface in V1; import-isolation `apaa.* ⊬ fastapi/uvicorn/starlette`)
- [Source: _bmad-output/design-artifacts/APAA/epic-1-retro-2026-06-21.md#7. Action Items] (AI-E1-1 adversarial non-ASCII fixtures; AI-E1-4 gates extended-not-forked; AI-E1-5 exercise the L1-E11 loop)
- [Source: _bmad-output/design-artifacts/APAA/stories/2-1-complete-depth-state-semantics-inferred-never-satisfies-a-gate.md] (DONE — `assess_criticality` + `Criticality` + `CRITICALITY_SIGNAL_TOKENS`; the Low substring-over-match finding whose correction lever is THIS story's operator override; `critical_subsystems_all_deep` seam stays defaulted-True until 2.3)
- [Source: _bmad-output/design-artifacts/APAA/stories/1-6-pure-function-verdict-gate-finding-ordering-exit-code-mapping.md] (DONE — `evaluate_verdict(..., critical_subsystems_all_deep: bool = True)` + `AuditVerdict.critical_subsystems_all_deep`; the additive Story-2.3 seam this story SUPPLIES)
- [Source: minions_core/apaa/ledger/depth_semantics.py] (`assess_criticality(*, file_path, source, ast_entry=None) -> Criticality`, `Criticality{CRITICAL, NORMAL}`, `CRITICALITY_SIGNAL_TOKENS`, `DepthSemanticsError` — REUSE verbatim, do NOT modify)
- [Source: minions_core/apaa/verdict/verdict_gate.py] (`evaluate_verdict(ledger, findings, *, critical_subsystems_all_deep=True)`, `AuditVerdict.critical_subsystems_all_deep` — SUPPLY the boolean, do NOT modify the gate)
- [Source: minions_core/apaa/pipeline.py] (`run_audit_detailed` — the single `evaluate_verdict(ledger, tuple(findings))` call site to rewire; `_read_source` provides the in-memory source for identification)
- [Source: minions_core/apaa/models.py] (`AuditRequest` frozen `extra="forbid"` + `to_provenance_payload` — the additive designation field attaches here; never persists `repo_path`)
- [Source: minions_core/apaa/cli.py] (the LOCKED `apaa audit <repo> --commit --budget --materiality-bar` contract + `build_parser` — the additive `--critical-subsystem`/`--exclude-critical` flags attach here)
- [Source: minions_core/apaa/ledger/coverage_ledger.py] (`CoverageDepth`, `CoverageLedger`, `CoverageLedgerEntry`, `grade_entry` — REUSE verbatim for the predicate + synthetic-ledger tests)
- [Source: minions_core/apaa/__init__.py] (`__version__ = "0.1.0"` — single apaa_version source)
- [Source: CLAUDE.md §3.2 file-size / §3.7 headless-only / §3.8 12-Factor + secret masking / §9.1 L1-E11 retro-action-items loop]

## Dev Agent Record

### Context Reference

- Story file (this), epics.md#Story-2.3, prd.md FR4/FR16/FR30, architecture.md (determinism/pure-impure/boundaries),
  epic-1-retro-2026-06-21.md (AI-E1-1/4/5).
- REUSED verbatim (no diff): `verdict/verdict_gate.py` (`evaluate_verdict(..., critical_subsystems_all_deep=...)`),
  `ledger/depth_semantics.py` (`assess_criticality`/`Criticality`), `ledger/coverage_ledger.py`, `store/canonical.py`.

### Agent Model Used

- claude-opus-4-8 (BMAD dev-story, mode=implement).

### Completion Notes

- WIRE-THE-SEAM story completed. New pure module `ledger/critical_subsystems.py`: content identification
  (REUSES the real 2.1 `assess_criticality` per candidate — no second enum/token set/matcher), the operator
  designation merge `(heuristic ∪ operator_designated) − operator_excluded`, and the
  `critical_subsystems_all_deep(critical_paths, ledger)` predicate. Frozen `CriticalSubsystemSet`
  (`frozen=True, extra="forbid"`, localized `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION="1"`); `CriticalCandidate`
  in-memory descriptor; `CriticalOrigin` provenance enum; `CriticalSubsystemError` (ValueError subclass, AR10).
- LOCKED decisions (documented in the module docstring + here): (1) module placement = `ledger/`; (2) merge
  formula = union-then-minus with operator PRECEDENCE; (3) **add-vs-exclude tie = EXCLUDE WINS**; (4)
  **unmatched-path policy = conservative** — a force-critical path matching no candidate IS in the final set
  AND in `designated_but_unmatched`, has no ledger entry, so it can never be `audited_deep` → withholds
  `RELEASE_READY` (an operator typo can only make the gate STRICTER, never weaker; an exclude matching nothing
  is a no-op); (5) provenance model `CriticalSubsystemSet` (sorted paths + per-path origin + unmatched set);
  (6) typed error `CriticalSubsystemError`; (7) `AuditRequest` fields `critical_paths` / `excluded_critical_paths`
  (`tuple[str,...] = ()`); (8) CLI flags `--critical-subsystem` / `--exclude-critical` (repeatable, additive).
- Pipeline wiring: ONE call site rewired in `run_audit_detailed`. `_detect_per_file` now also assesses each
  PYTHON file's criticality over the SAME in-memory source it reads (single read for non-test Python; no double
  read for test files) and returns candidates; the call site builds the critical set with operator designations
  and feeds the computed boolean into `evaluate_verdict(..., critical_subsystems_all_deep=...)`. Empty set →
  True → byte-identical to the pre-2.3 default (regression keystone, pinned by TC-APAA-PIPELINE-001-12 +
  TC-APAA-LEDGER-001-145).
- Purity/determinism: AST-scan test pins no I/O/clock/uuid/random/LLM; order-independence test pins
  byte-identical output across two input orders; single 1.1 serializer honored (no second `json.dumps`,
  AST gate green); no `float` anywhere.
- Carry-forward discharged: AI-E1-1 (non-ASCII path `auth/café_guard.py` + Cyrillic `модуль/безопасность.py`
  + non-ASCII AST identifier `authorize_açõ` identified critical + designable + excludable intact,
  TC-APAA-LEDGER-001-153..155); AI-E1-4 (extended `_MODULES_UNDER_GUARD`, did not fork; single-serializer AST
  gate green); AI-E1-5 (referenced here).
- Frozen contracts UNCHANGED (verified no working-tree diff): `verdict_gate.py`, `depth_semantics.py`,
  `coverage_ledger.py`, `recording.py`, `store/canonical.py`. Did NOT create `index/partitioner.py` (Story 2.4).
- Results: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → 450 passed;
  mypy clean on the 4 new/edited modules; `critical_subsystems.py` is 286 lines (≤1200, NFR-M1).
- Deferred: DF-2-3-A (the 2.1 substring matcher precision pass) recorded in the story; NOT built (operator
  override is the V1 correction lever).

### File List

- NEW `minions_core/apaa/ledger/critical_subsystems.py`
- UPDATE (additive) `minions_core/apaa/models.py`
- UPDATE (additive) `minions_core/apaa/cli.py`
- UPDATE (one call site) `minions_core/apaa/pipeline.py`
- NEW `tests/apaa/test_critical_subsystems.py`
- UPDATE `tests/apaa/test_cli.py`
- UPDATE `tests/apaa/test_pipeline_signature_demo.py`
- UPDATE `tests/apaa/test_no_web_imports.py` (extended `_MODULES_UNDER_GUARD`)

## Senior Developer Review (AI)

**Reviewer:** code-review (claude-opus-4-8), adversarial gate — iteration 1.
**Date:** 2026-06-21.
**Verdict: PASS** → status `done`. 450 passed, mypy clean on the 4 new/edited modules.

### Scope reviewed

NEW `ledger/critical_subsystems.py` (pure identification + operator-designation merge + `critical_subsystems_all_deep` predicate + frozen `CriticalSubsystemSet`/`CriticalCandidate`/`CriticalOrigin` + `CriticalSubsystemError`); additive `AuditRequest.critical_paths`/`excluded_critical_paths` + provenance keys (`models.py`); additive repeatable `--critical-subsystem`/`--exclude-critical` CLI flags (`cli.py`); ONE pipeline call-site rewire (`pipeline.py`); NEW `tests/apaa/test_critical_subsystems.py`; edited `test_cli.py`/`test_pipeline_signature_demo.py`/`test_no_web_imports.py`.

### Adversarial findings (the high-stakes judgments)

- **SEAM, NOT FORK — CONFIRMED.** `pipeline.run_audit_detailed` computes `critical_subsystems_all_deep(critical.paths, ledger)` and passes the boolean into the EXISTING `evaluate_verdict(ledger, tuple(findings), critical_subsystems_all_deep=all_deep)`. No verdict math is reimplemented; `verdict_gate.py` is unchanged (the `RELEASE_READY` condition still ANDs the third conjunct in-gate; thresholds, three-member `Verdict` enum, `depth_supported is not None` advisory moat, FR33 ordering, and the `0/2/3` exit map are all intact). The advisory-by-contract moat is untouched.
- **BYTE-IDENTITY REGRESSION (keystone) — GENUINELY PINNED.** `test_e2e_no_designation_is_byte_identical_to_pre_2_3` (TC-APAA-PIPELINE-001-12) compares the content-addressed verdict locator AND the actual on-disk bytes between a plain `_request` (no 2.3 fields) and a `_request_with_designation` carrying empty designations — both the sha256 locator string and `read_bytes(...)` are asserted equal. `critical_subsystems_all_deep(())` short-circuits to `True` (vacuously all-deep) before any ledger scan. The empty-set path is a true no-op. TC-APAA-LEDGER-001-145 corroborates at the unit level via canonical-bytes equality of `to_canonical_payload()`.
- **OPERATOR PRECEDENCE / ANTI-GAMING — CORRECT AND AUDITED.** Merge is `(heuristic ∪ designated) − excluded` with exclude-wins on a tie (TC-...-136). A force-critical TYPO lands in `paths` + `designated_but_unmatched`, has no ledger entry, so the predicate returns `False` → can only make the gate STRICTER (TC-...-137, TC-...-142). An exclude typo is a no-op, so it cannot weaken the gate either (TC-...-138). A DELIBERATE exclude of a genuinely-critical path does weaken the gate — but that is the intended V1 correction lever for the 2.1 substring over-flag (locked in AC2), and it is AUDITED: `excluded_critical_paths` is recorded via `AuditRequest.to_provenance_payload()` into the persisted `.apaa/` run-state, so a reader can see exactly what the operator excluded. This is NOT a silent coverage-honesty bypass.
- **WIRE CONTRACT — UNCHANGED (AR3).** `AuditRequest` gains two optional `tuple[str,...] = ()` fields (frozen `extra="forbid"`); CLI gains two optional repeatable flags. No exit code added/changed — a critical-but-shallow repo routes to the EXISTING `NOT_READY_FOR_RELEASE`/exit 2 (TC-...-143, e2e TC-APAA-PIPELINE-001-10). No new HTTP route/FastAPI surface (headless preserved).
- **DETERMINISM / PURITY — VERIFIED.** AST-scan purity test (no I/O/clock/uuid/random/LLM); sorted `paths`/`designated_but_unmatched`; order-independence test over two input orders + canonical-bytes equality (TC-...-152). `origins` dict is rendered through the sorting single 1.1 serializer. No `float` anywhere; `CriticalSubsystemError` (ValueError subclass) on malformed input (TC-...-149/-150). Frozen models. `_MODULES_UNDER_GUARD` EXTENDED (not forked); no-web-imports + single-serializer AST gates green. AI-E1-1 non-ASCII path/identifier identified + designable + excludable intact (TC-...-153/-154/-155). All files ≤1200 lines (largest edited: pipeline.py 351).

### Review Findings

<!-- defer-schema-session: 2026-06-21 -->
- [x] [Review][Defer] Persisted state records operator designation INTENT, not the computed critical set — DF-2-3-B [minions_core/apaa/pipeline.py:265] — The run-state persists `request.to_provenance_payload()` (the raw `critical_paths`/`excluded_critical_paths` the operator supplied), but NOT the computed `CriticalSubsystemSet` (final paths + per-path `origins` + `designated_but_unmatched`). A reader of `.apaa/` state sees what the operator asked to exclude/force, but cannot tell from state alone whether an excluded path was overriding a genuine heuristic-critical hit. The exclusion lever is auditable (intent IS recorded), and the negative-assurance narration of which critical subsystems were/weren't covered is explicitly scoped to Epic 4 Story 4.1 — so this is acceptable for V1 and not blocking. Owner: QA Lead. Target: epic-4-negative-assurance. Category: governance. Severity: 🟢.

| Date | Version | Description | Author |

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-06-21 | 0.1.0 | Story 2.3 implemented (dev-story): new pure `ledger/critical_subsystems.py` (content identification REUSING the real 2.1 `assess_criticality`; operator-designation merge `(heuristic ∪ designated) − excluded` with **operator precedence**, **exclude-wins tie**, **conservative unmatched-path** policy; pure `critical_subsystems_all_deep` predicate; frozen `CriticalSubsystemSet`/`CriticalCandidate`/`CriticalOrigin`; `CriticalSubsystemError`). Additive `AuditRequest.critical_paths`/`excluded_critical_paths` + provenance keys; additive repeatable `--critical-subsystem`/`--exclude-critical` CLI flags. ONE pipeline call-site rewired to feed the EXISTING 1.6 `evaluate_verdict(..., critical_subsystems_all_deep=...)` seam (NO gate fork; empty-set → True → byte-identical to pre-2.3). Discharged AI-E1-1 (non-ASCII path/identifier identified+designable+excludable intact), AI-E1-4 (`_MODULES_UNDER_GUARD` extended, single-serializer AST gate green), AI-E1-5. 450 passed; mypy clean; `critical_subsystems.py` 286 lines. Frozen verdict/depth/ledger/serializer contracts UNCHANGED. Status → review. | dev-story (claude-opus-4-8) |
| 2026-06-21 | 0.1.0 | Story 2.3 drafted (create-story): critical-subsystem identification (reuse 2.1 `assess_criticality`) + operator designation/exclusion (with precedence over the content heuristic — the documented correction lever for the 2.1 substring Low) + the pure `critical_subsystems_all_deep` predicate wired into the EXISTING 1.6 `evaluate_verdict(..., critical_subsystems_all_deep=...)` seam (NO gate fork) + the additive `AuditRequest` field + `cli.py` flag. Status → ready-for-dev. | create-story (claude-opus-4-8) |
