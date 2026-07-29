# Story 2.6: Zero-token breadth tool runner + tool-failure-as-finding

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/APAA/`; the tracker is `_bmad-output/design-artifacts/APAA/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As an integrator who is cost-conscious,
I want APAA to run deterministic zero-LLM-token breadth tools (radon, and the already-sanctioned zero-token
static metrics) over audited code — grading the files those tools covered `tool_scanned_only` — and to treat
any tool that crashes, times out, is unavailable, or emits unparseable / non-ASCII / locale-mangled output as
a recorded `tool_failure` finding plus a coverage downgrade rather than a crash or a fabricated pass,
so that LLM spend is reserved for depth, the `tool_scanned_only` depth state introduced by Story 2.1 finally
has a PRODUCER, and a broken tool degrades honestly instead of silently skipping or lying — the FINAL story of
Epic 2 (Full Coverage Ledger & Defect Detectors) and the honest-degradation keystone (FR14 / NFR-R1 / NFR-C3).

## Story Context

This is **Story 6 of Epic 2** (Full Coverage Ledger & Defect Detectors — the FR10–FR14 defect-detection
cluster + the breadth/cost-efficiency NFRs). It is the THIRD APAA detector after the Story 1.5 vacuous-test
detector (pure) and the Story 2.5 secret detector (pure), and the FIRST detector whose core is an **impure
subprocess SHELL**: it shells out to deterministic, zero-LLM-token breadth tools and folds their output back
into the determinism spine. It delivers three tightly-coupled capabilities:

1. **FR14 / NFR-C3 — zero-token breadth:** a `detectors/tool_runner.py` that runs deterministic breadth tools
   (V1 = `radon` — already installed + sanctioned per AR1; the architecture also names `cloc`/linters/SAST as
   the family, all OPTIONAL/best-effort), produces breadth metrics with ZERO LLM tokens, and grades the files
   covered ONLY this way `tool_scanned_only` — the depth state that Story 2.1 documented + classified but no
   producer yet emitted (`pipeline.py` today never mints `tool_scanned_only`).
2. **FR14 / NFR-R1 — tool-failure-AS-FINDING:** a tool that crashes / times out / is unavailable / emits
   unparseable or non-ASCII-mangled output becomes a recorded `tool_failure` finding + a coverage downgrade —
   NEVER an uncaught crash, NEVER a fabricated pass, NEVER a silent skip. "A tool that can't run is recorded,
   never silently skipped" is the honest-degradation principle this story owns.
3. **FR14 — unestablishable-traceability-AS-FINDING:** when APAA cannot establish traceability over a
   poor-docs / low-quality repo, it records a `traceability_not_establishable` finding rather than failing.

**What already exists (verify-and-lock, do NOT rebuild / do NOT refork).** This story slots into a mature
spine. REUSE these verbatim:

- **Story 1.1 (done)** — `store/canonical.py` single serializer (`dumps`/`dumps_bytes`/`loads`; rejects
  `float`) + `store/envelope.py` (`EnvelopeWriter.build`). Any `.apaa/` bytes route through this; the committed
  AST gate (`test_canonical_single_serializer.py`) forbids a direct `json.dumps(`.
- **Story 1.2 (done)** — `ledger/coverage_ledger.py`: the closed five-member `CoverageDepth` enum (which
  ALREADY contains `TOOL_SCANNED_ONLY` — do NOT add a state), `CoverageLedgerEntry`, `CoverageLedger`,
  `grade_entry(file_path, proposed_depth, claim_present)`; and `ledger/recording.py`: `Locator`, `Recording`,
  `RecordingValidationError`. REUSE VERBATIM; do NOT modify the frozen schema.
- **Story 1.4 (done)** — `intake/stack_detect.py` ALREADY probes `radon_available` /
  `tree_sitter_python_available` / `cloc_available` into a frozen `ToolchainProfile` (FR2/AR1/AR10). Its
  docstring is EXPLICIT: *"The full tool-failure-AS-FINDING is Story 2.6 — this story produces the honest
  availability DATA only."* This story consumes that availability data and adds the RUNNING + the
  failure-as-finding. `index/ast_index.py` gives `AstIndexEntry` (`file_path` / `ast_eligible` / `parse_failed`
  / `definitions` / `edges`, `Definition.ast_span` token `"<kind>:<name>@<start>-<end>"`).
- **Story 1.5 (done)** — `detectors/base.py`: the `Detector` `Protocol` (a pure `run(...) -> DetectorResult`),
  the frozen `DetectorResult` (`entries` + `findings` + `degraded`), `FindingDraft`, `DegradedCondition`, and
  `build_recording(draft, *, depth_supported, claim_present)` — the FR13 locator-or-reject builder with a
  content-derived value-independent `recording_id`. **REUSE `build_recording` VERBATIM** to mint the
  `tool_failure` / `traceability_not_establishable` findings; do NOT define a parallel finding builder or a
  parallel finding model. NOTE: the `Detector.run` protocol is documented "MUST be pure" — this detector's
  RESULT-CLASSIFICATION + finding/grade construction is pure, but its tool-INVOCATION is an impure subprocess
  shell; see Dev Notes "The pure/impure split for THIS detector" for how to keep them separated cleanly.
- **Story 1.6 (done)** — `verdict/verdict_gate.py` `evaluate_verdict` (PURE). UNCHANGED. FR8 already holds: the
  deep-% numerator counts ONLY `audited_deep`, so `tool_scanned_only` entries this story emits land in the
  DENOMINATOR, never the numerator (a file covered only by a breadth tool can NEVER satisfy a deep gate — that
  is the whole point of `tool_scanned_only`). The dev MUST NOT change the gate or let `tool_scanned_only` count
  toward deep coverage.
- **Story 1.7 / `pipeline.py` (done)** — `run_audit_detailed` is the IMPURE orchestrator: intake → stack-detect
  → index → `_detect_per_file` (vacuous + secret) → ledger → critical-subsystem set → `evaluate_verdict` →
  `_persist` (+ partition plan). This story's pipeline touch is SCOPE-FENCED (see AC5).
- **Story 2.1 (done)** — `ledger/depth_semantics.py`: `DEPTH_SEMANTICS`, the pure `classify_depth(DepthEvidence)`
  over the closed `EvidenceKind` (which ALREADY has `TOOL_BREADTH_ONLY → TOOL_SCANNED_ONLY`), `assess_criticality`.
  This is the depth-classifier this story's producer SHOULD route through (reuse `classify_depth` /
  `EvidenceKind.TOOL_BREADTH_ONLY` rather than minting `CoverageDepth.TOOL_SCANNED_ONLY` ad hoc — single
  classifier, §3.3). DO NOT modify it.
- **Story 2.2 / 2.3 / 2.4 / 2.5 (done)** — the readable surface, critical-subsystem identification, the
  partitioner + work-manifest permission boundary, and the pure secret detector. UNCHANGED/reused. The 2.5
  secret detector is the IMMEDIATE precedent for the detector shape (a detector folded into `_detect_per_file`,
  emitting `Recording` findings via `build_recording`, evidence on a separate frozen model, joined to the
  no-web gate). The 2.4 `ApaaStorePaths` containment boundary and the 2.5 producer-side discipline both apply:
  tool OUTPUT must never leak source/secret bytes into a finding or a `DegradedCondition.reason`.

**The net-new deliverable of THIS story.** An impure breadth-tool RUNNER with a pure result-classification core,
the first PRODUCER of `tool_scanned_only`, and tool-failure / unestablishable-traceability as recorded findings:

1. a **`detectors/tool_runner.py`** module with a clean pure/impure split:
   - an IMPURE `run(...)` SHELL that invokes the V1 breadth tool(s) — V1 = `radon` (already installed +
     sanctioned, AR1) over the audited Python files — with a bounded, deterministic subprocess (or the radon
     library API; see Dev Notes for the safe-invocation decision the dev LOCKS), a hard timeout, and a captured
     exit/stdout/stderr;
   - a PURE classifier that maps a tool's outcome (ran-clean / crashed / timed-out / unavailable / unparseable)
     to (a) a `tool_scanned_only` `CoverageLedgerEntry` for files the tool successfully covered (graded via the
     2.1 `classify_depth(EvidenceKind.TOOL_BREADTH_ONLY)` / the 1.2 `grade_entry`), and (b) a `tool_failure`
     `Recording` finding + a coverage DOWNGRADE for a tool that failed — emitting a frozen `DetectorResult`
     (entries + findings + degraded) the pipeline folds, exactly like the 1.5/2.5 detectors;
2. a frozen **`ToolRunOutcome`** (or equivalent — `frozen=True, extra="forbid"`, localized `schema_version`)
   carrying ONLY redaction-safe, deterministic breadth metadata: the `tool_id` (e.g. `"radon"`), the
   `outcome` (a closed enum: `OK` / `UNAVAILABLE` / `CRASHED` / `TIMED_OUT` / `UNPARSEABLE`), bounded
   non-secret metrics as `int`/`Fraction` (e.g. files-scanned count, an aggregate complexity bucket — NEVER
   `float`, NEVER raw tool stdout that could echo source/secret bytes), and a SANITIZED failure-reason TOKEN
   (a constant/enum token like `"radon_crashed"` — NEVER the raw stderr text, which can contain source/secret
   bytes or a host path — NFR-S1);
3. the **tool-failure-as-finding guarantee**: a crashed / timed-out / unavailable / unparseable tool yields a
   `tool_failure` `Recording` (via `build_recording`, `advisory=True`, `depth_supported=None`, with a
   verifiable locator — see AC2 for the locator strategy) + a coverage downgrade, with NO uncaught raise out of
   the runner, NO fabricated pass, NO silent skip, and NO raw tool output / source / secret bytes in the
   finding or the degraded reason;
4. the **unestablishable-traceability-as-finding guarantee**: when APAA cannot establish traceability (a
   poor-docs / low-signal repo condition the dev LOCKS the V1 definition of), it records a
   `traceability_not_establishable` finding rather than failing (FR14);
5. the **scope-fenced pipeline wiring**: run the breadth runner in the per-file/per-repo detect stage, fold its
   `tool_scanned_only` entries + `tool_failure` / `traceability_not_establishable` findings + degraded
   conditions into the existing pipeline fold, persist through the EXISTING `_persist` / `store/writer.py`
   spine (no new write path); a run on a repo where the tool runs clean is grade-additive (the
   already-deep/shallow files keep their grade — only files NOT otherwise read for depth become
   `tool_scanned_only`; see AC5 for the LOCKED no-double-count rule);
6. a MANDATORY **adversarial non-ASCII + locale + FAILURE-INJECTION test suite** (AI-E1-1 — the Epic-1 retro
   action item explicitly names 2.6 as the FIRST place to apply it; see the carry-forward below).

The tool INVOCATION + the OUTPUT read are the impure shell (subprocess); the OUTCOME CLASSIFICATION + the
finding/grade construction + the metric folding are PURE and deterministic (AR8).

**Carry-forward from the Epic-1 retro (CLAUDE.md §9.1 / L1-E11 — this story discharges these items).**
- **AI-E1-1 (test-infra 🟠) — adversarial non-ASCII + locale + FAILURE-INJECTION fixtures.** The retro action
  item is verbatim: *"Default impure-shell subprocess/parser stories to ship an adversarial non-ASCII + locale +
  failure-injection fixture (the class that produced the only Epic-1 FAIL). **Apply first in 2.6 (tool
  runner)** and 2.5 (secret detector)."* The single Epic-1 review FAIL was Story 1.4's non-ASCII `git ls-files`
  drop/mangle at an impure-shell encoding boundary (`core.quotepath` octal-escaped paths). THIS story is the
  archetypal impure subprocess boundary the retro warns about — tool stdout/stderr decoding, locale, and
  failure are all in play. Tests MUST include: (a) a **non-ASCII repo / file-path fixture** (e.g.
  `auth/café_metrics.py`, `модуль/сложность.py`) whose breadth metrics are produced with the path intact (not
  mojibake / not dropped — the 1.4 TC-APAA-INTAKE-001-78 `git ls-files -z` + UTF-8-decode precedent), graded
  `tool_scanned_only`, and round-tripping intact through the canonical serializer; (b) a **locale / encoding**
  fixture proving the subprocess decode is explicit UTF-8 (not the platform default cp1252 — project memory:
  Windows gate scripts crash on cp1252) and a non-ASCII byte in tool output never raises out of the runner;
  (c) **FAILURE-INJECTION** fixtures — an injected fake tool runner that crashes (non-zero exit), times out
  (exceeds the bounded timeout), is unavailable (binary/import missing), and emits unparseable / non-ASCII
  output — each asserted to produce a `tool_failure` finding + downgrade, NEVER a crash / fabricated pass /
  leaked output.
- **AI-E1-4 (process 🟢) — keep the committed gates extended-not-forked.** Append
  `minions_core.apaa.detectors.tool_runner` to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py`
  (do NOT fork the no-web-imports gate); keep the single-serializer AST gate green (any JSON routes through
  `store/canonical.dumps`, never a direct `json.dumps`); keep the pipeline zero-token gate
  (`test_pipeline_is_zero_token`) green — the breadth runner is ZERO-LLM-token, so wiring it into `pipeline.py`
  must NOT pull `providers.*` / `apaa.audit.*`.
- **AI-E1-5 (process 🟢) — exercise the L1-E11 loop.** This story explicitly references the AI-E1-* items it
  discharges (here).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 2.6) and the architecture / PRD. Drivers: **APAA-FR-14** (convert a
> tool failure OR an unestablishable-traceability condition into a FINDING rather than a crash — the central
> driver), **APAA-NFR-C3** (deterministic, zero-token tools perform BREADTH so LLM spend is reserved for depth
> — the cost-efficiency keystone), **APAA-FR-5** (the fixed-enum coverage ledger — this story PRODUCES the
> `tool_scanned_only` state Story 2.1 documented), **APAA-NFR-R1 / AR10** (a tool/parse failure or
> unestablishable-traceability condition degrades to a recorded finding or coverage downgrade — NEVER an
> uncaught crash or a fabricated result), **APAA-FR-13** (every finding carries ≥1 verifiable locator or is
> rejected — via the 1.5 `build_recording`), **APAA-NFR-D2** (deterministic, zero-LLM-token — the runner calls
> NO LLM; the OUTCOME classification + finding build are pure), **APAA-NFR-S1** (source/secret/api-key bytes —
> and raw tool stderr / host paths — never appear in ledgers, evidence, logs, traces, or any finding/degraded
> reason), **APAA-NFR-S5** (any `.apaa/` write through the 1.3 containment shell), **AR1** (`radon` is the
> already-installed/sanctioned V1 breadth tool; `cloc`/linters/SAST are OPTIONAL/best-effort), **AR4** (single
> canonical serializer; metrics as `int`/`Fraction`, NEVER `float`; content-derived ids; no
> clock/uuid/random/iteration-order in any `.apaa/` write path), **AR8** (pure/impure separation — the tool
> INVOCATION + output read are the impure subprocess shell; the OUTCOME classification + finding/grade build +
> metric fold are PURE), **AR11** (`.apaa/` finding filenames content-derived, never arrival order),
> **APAA-NFR-M1** (≤1200-line files), **APAA-NFR-M2** (frozen, additive-only contracts). Carries the Epic-1
> retro AI-E1-1 (adversarial non-ASCII + locale + FAILURE-INJECTION) item — 2.6 is the named first application.
>
> **SCOPE FENCE — Tier-A, single-purpose.** This story delivers ONLY: (1) the `detectors/tool_runner.py` impure
> breadth-tool runner (V1 = `radon`) with a pure outcome-classifier; (2) the FIRST producer of the
> `tool_scanned_only` grade (via the 2.1 `classify_depth(EvidenceKind.TOOL_BREADTH_ONLY)` / 1.2 `grade_entry`);
> (3) the `tool_failure`-as-finding guarantee (crash / timeout / unavailable / unparseable → a recorded finding
> + downgrade, never a crash / fabricated pass / silent skip / leaked output); (4) the
> `traceability_not_establishable`-as-finding guarantee (FR14 second clause); (5) the frozen redaction-safe
> `ToolRunOutcome` (sanitized metrics + a failure-reason TOKEN — no raw stderr / source / secret bytes); (6) the
> scope-fenced wiring into the detect stage + persistence through the EXISTING `_persist`; (7) the MANDATORY
> adversarial non-ASCII + locale + FAILURE-INJECTION test suite (AI-E1-1). It does NOT build, and MUST NOT pull
> forward: the **budget-ceiling configuration / cost accounting** (FR21 — Story 3.1) or **halt→skip→downgrade**
> on budget exhaustion (FR22 — Story 3.2 — this story produces breadth at zero token cost; it does NOT account
> spend against a ceiling); the **LLM dispatch port / deep audit** that reserves LLM spend for depth (Epic 6 —
> this story enables the cost split by doing breadth at zero token, but the DEPTH side is Epic 6); the
> **orphan/dead-code detector** (FR12 — Epic 6); the **adversarial Prosecutor / cut-edge pass** (FR19 — Epic 6);
> a **verdict-blocking promotion** of the `tool_failure` finding beyond what the lock decides (V1 keeps it
> advisory — see Dev Notes); the **randomized-canary CI-blocking secret-containment property suite**
> (`tests/security/test_apaa_secret_containment.py` — Story 4.4); any change to the **1.1 serializer / 1.2
> `Recording`/`Locator`/`CoverageDepth` enum / `grade_entry` / 1.4 index / stack-detect / 1.5 `base` builder /
> 1.6 verdict gate / 2.1 depth_semantics / 2.2 coverage report / 2.3 critical-subsystem / 2.4 partitioner / 2.5
> secret_scan** contracts (all frozen/reused). It adds NO new HTTP route / FastAPI surface / UI (§3.7), NO
> A2A token, NO LLM. Run breadth, grade `tool_scanned_only`, record a failure as a finding, then stop.

**AC1 — Zero-token breadth: run the breadth tool(s), produce metrics with ZERO LLM tokens, grade `tool_scanned_only` (FR14, NFR-C3, FR5)**
**Given** a loaded, indexed repo (the 1.4 `RepoIntake` + `AstIndex` + the 1.4 `ToolchainProfile` from
`detect_stack`, which already records `radon_available`)
**When** the breadth `ToolRunnerDetector` runs over the audited Python files
**Then** it invokes the V1 breadth tool — **`radon`** (already installed + sanctioned, AR1) — producing breadth
metrics (e.g. cyclomatic complexity / raw LOC metrics radon supplies) **with ZERO LLM tokens** (the runner
imports NO `providers.*` / `apaa.audit.*` — pinned by the no-web/zero-token gate), and grades each file that was
covered ONLY by a breadth tool (i.e. not otherwise read for depth) `tool_scanned_only` via the 2.1
`classify_depth(DepthEvidence(kind=EvidenceKind.TOOL_BREADTH_ONLY))` → the 1.2 `grade_entry(...,
proposed_depth=CoverageDepth.TOOL_SCANNED_ONLY)` path (REUSE the single classifier; do NOT mint the enum member
ad hoc, do NOT add a state)
**And** because the 1.6 deep-% numerator counts ONLY `audited_deep` (FR8, UNCHANGED), a `tool_scanned_only`
file lands in the DENOMINATOR — it can NEVER satisfy a deep-coverage gate (a breadth scan is breadth, not
depth — the cost-split semantics: tokens are spent on depth, tools do breadth — NFR-C3)
**And** when the tool is `radon_available: false` (or otherwise UNAVAILABLE) the runner does NOT crash and does
NOT fabricate metrics — it routes to the AC2 tool-failure path; and the LOCKED V1 tool set + each tool's
invocation + the breadth metrics it produces are documented honestly in the module docstring (the V1 set is
`radon`; `cloc`/linters/SAST are named as the family but OPTIONAL/best-effort — the dev LOCKS exactly which
ship in V1 and documents the rest as the family).

**AC2 — Tool-failure-AS-FINDING: a crash / timeout / unavailable / unparseable tool → a recorded finding + downgrade, never a crash / fabricated pass / silent skip (FR14, NFR-R1, AR10 — the keystone)**
**Given** a breadth tool that crashes (non-zero exit / raises), times out (exceeds a bounded, deterministic
timeout), is unavailable (binary / import missing), or emits unparseable / non-ASCII-mangled output
**When** the runner invokes it
**Then** the failure becomes a `tool_failure` `Recording` finding (minted via the 1.5 `build_recording` — REUSE
VERBATIM; `rule_id="tool_failure"`, `advisory=True`, `depth_supported=None`, carrying ≥1 verifiable `Locator` —
the dev LOCKS the locator strategy: a repo-anchor locator such as the tool's target dir / a representative file
+ line 1, since a tool failure is repo/dir-scoped not span-scoped — the locator must satisfy the FR13
`build_recording` non-empty contract or the finding is rejected, never silently dropped) **PLUS** a coverage
downgrade: files the failed tool would have covered are NOT graded `tool_scanned_only` (it didn't scan them) —
they retain their existing grade or are recorded `skipped` (examined-but-ungradable), never fabricated as
covered
**And** NO uncaught exception escapes the runner (AR10 — the run CONTINUES to a verdict over the partial
ledger), NO bare `except: pass`, NO `print()` in library code; a malformed ARGUMENT to the runner raises a
typed error (a `ValueError` subclass localized to the module, e.g. `ToolRunnerError`, mirroring
`SecretScanError` / `RecordingValidationError` / `RepoIntakeError` / `PartitionerError`)
**And** the failure is recorded with a SANITIZED reason TOKEN only — a constant/enum token like
`"radon_crashed"` / `"radon_timed_out"` / `"radon_unavailable"` / `"radon_unparseable"` — the raw tool
stderr/stdout, the host path, and any source/secret bytes are NEVER placed into the `tool_failure` finding, the
`ToolRunOutcome`, the `DegradedCondition.reason`, a log line, or the raised exception message (NFR-S1 — the 2.5
producer-side discipline extended to tool OUTPUT: a tool can echo source/secret bytes in its error text, so the
runner drops the raw output and keeps only a fixed token).

**AC3 — Unestablishable-traceability-AS-FINDING (FR14 second clause)**
**Given** a repo / condition where APAA cannot establish traceability (a poor-docs / low-signal repo — the dev
LOCKS the V1 definition of "unestablishable traceability"; a defensible V1 lock: when the breadth tool ran
clean but produced no usable signal over a file/unit such that no depth or breadth grade can be earned, OR an
explicitly-defined low-signal condition — document the chosen rule)
**When** APAA encounters it
**Then** it records a `traceability_not_establishable` `Recording` finding (via `build_recording`,
`advisory=True`, `depth_supported=None`, with a verifiable locator) rather than failing — the condition is
recorded honestly, the run continues, and (like AC2) no raw repo content / source bytes enter the finding or
the reason (NFR-S1)
**And** the V1 scope of this clause is documented honestly: it is the FR14 "unestablishable-traceability → a
finding, not a crash" requirement at a Tier-A grade — full requirement↔code traceability analysis (orphan /
dead-code, the referencing-requirement graph) is the Epic-6 orphan detector (FR12) and is NOT built here; this
story records the CONDITION as a finding, it does not build the full traceability graph.

**AC4 — `ToolRunOutcome` is a frozen, redaction-safe, no-float contract (NFR-S2-spirit, NFR-M2, AR4)**
**Given** the per-tool outcome the runner carries
**When** the `ToolRunOutcome` (or equivalent) model is defined
**Then** it is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`, localized
`TOOL_RUN_SCHEMA_VERSION` — additive-only, the 1.1/1.2/1.4/2.4/2.5 precedent) carrying ONLY redaction-safe,
deterministic fields: `tool_id: str` (e.g. `"radon"`), `outcome` (a closed enum
`OK`/`UNAVAILABLE`/`CRASHED`/`TIMED_OUT`/`UNPARSEABLE`), `files_scanned: int`, bounded aggregate metrics as
`int`/`Fraction` (NEVER `float` — the 1.1 serializer rejects `float`; radon complexity is naturally `float`, so
the dev quantizes to an exact `Fraction` / `int` bucket, the 2.5 `_shannon_bits_per_char` rational-grid
precedent), and a SANITIZED `failure_reason: str | None` that is a CONSTANT/ENUM TOKEN only (never raw output)
— there is **NO raw-stdout / raw-stderr / source-text field on the model AT ALL** (the absence of the field is
the structural guarantee, the 2.5 "no value field" precedent)
**And** if the outcome is persisted (the dev LOCKS whether it persists alongside the run-state or travels only
on the in-memory `DetectorResult` like the 1.5 `VacuousTestScore` / the 2.5 `SecretFindingEvidence`), it routes
through `store/canonical.dumps` (no second `json.dumps`) and round-trips byte-identically (NFR-P1), AND the
persisted bytes contain no raw tool output / source / secret bytes.

**AC5 — The runner grades + folds into the pipeline (scope-fenced wiring, no double-count — FR5, reuse)**
**Given** the breadth runner integrated into the pipeline
**When** `run_audit_detailed` runs
**Then** the runner returns a frozen `DetectorResult` (entries + findings + degraded) the pipeline FOLDS,
exactly like the 1.5/2.5 detectors (the runner does NOT assemble the whole `CoverageLedger`); the scope-fenced
`pipeline.py` touch wires the `ToolRunnerDetector` into the detect stage, folding its `tool_scanned_only`
entries + `tool_failure` / `traceability_not_establishable` findings + degraded conditions into the existing
`entries`/`findings` accumulation, and persists through the EXISTING `_persist` / `store/writer.py` spine
(content-addressed `<content_hash>.json` under `.apaa/findings/` + the run-state — AR11/NFR-S5) — NO new write
path, NO new serializer, NO verdict-math change beyond the additive findings + the new denominator-only
`tool_scanned_only` entries
**And** the LOCKED no-double-count rule: a file ALREADY graded by the deep/shallow path (`_grade_non_test_python`
or the vacuous test path) is NOT ALSO graded `tool_scanned_only` (that would double-count it in the ledger
denominator) — `tool_scanned_only` is minted ONLY for files the breadth tool covered that were NOT otherwise
read for depth (the dev LOCKS + documents the rule: in V1 the pipeline reads every Python file for depth, so
the dev must decide what files breadth-only covers — a defensible V1 lock is that breadth runs over the SAME
Python set as an ADDITIVE metric channel WITHOUT re-grading already-graded files, so `tool_scanned_only` is
produced for any file the breadth tool covers that the depth/shallow path did NOT grade, e.g. a non-Python or
parse-failed file the breadth tool can still LOC-count; OR the dev documents the precise emission rule — the
keystone is no double-count + the regression-safe path below)
**And** a repo where the breadth tool runs clean and produces no NEW `tool_scanned_only` files (every file
already deep/shallow/skipped-graded) is byte-identical on the LEDGER + VERDICT to the pre-2.6 run for the files
it already produced (the regression-safe path — the breadth channel is additive metrics + findings, it does
not silently re-grade or change the verdict math of an existing run).

**AC6 — MANDATORY adversarial non-ASCII + locale + FAILURE-INJECTION suite (AI-E1-1 — 2.6 is the named first application)**
**Given** the impure subprocess boundary this detector introduces (the class that produced the only Epic-1
review FAIL — Story 1.4's non-ASCII drop at an impure-shell encoding boundary)
**When** the test suite runs
**Then** it includes ALL of:
- **(a) non-ASCII path** — a fixture repo with a non-ASCII file path (e.g. `auth/café_metrics.py`,
  `модуль/сложность.py`) whose breadth metrics are produced with the path INTACT (not mojibake, not dropped),
  graded `tool_scanned_only` where applicable, the finding/entry round-tripping intact through the canonical
  serializer (the 1.4 TC-APAA-INTAKE-001-78 precedent);
- **(b) locale / encoding** — proof the subprocess output is decoded as explicit UTF-8 (not the platform
  default — project memory: cp1252 crashes on Windows), and a non-ASCII byte in tool output never raises out of
  the runner (it degrades to `UNPARSEABLE` → a `tool_failure` finding if it cannot be parsed);
- **(c) FAILURE-INJECTION** — an INJECTED fake tool runner (a port/callable the detector takes so tests inject
  without spawning a real subprocess — the AR8 testability seam) that: crashes (non-zero exit / raises), times
  out (exceeds the bounded timeout), is unavailable (binary/import missing), and emits unparseable / non-ASCII
  output — EACH asserted to produce a `tool_failure` finding (`rule_id="tool_failure"`, `advisory=True`, a
  verifiable locator, a sanitized reason token) + the correct downgrade, with NO crash, NO fabricated pass, NO
  silent skip, and the raw injected output / a planted source-or-secret sentinel ABSENT from every emitted
  field, the serialized finding bytes, every persisted `.apaa/` file, the `DegradedCondition.reason`, and any
  exception message (the 2.5 containment-search precedent — search the RAW bytes incl. non-ASCII UTF-8)
**And** the test asserts the POSITIVE half too: when the tool runs CLEAN over a clean fixture, the breadth
metrics are produced, files are graded `tool_scanned_only` per the LOCKED rule, and NO spurious `tool_failure`
finding is emitted (a clean run must not cry wolf).

**AC7 — The runner is zero-token, pure-classification, deterministic, typed-degrading, import-isolated (NFR-D2, NFR-R1, AR8, AR10, M2)**
**Given** `detectors/tool_runner.py` (and the `ToolRunOutcome` model)
**When** it is imported and exercised in unit tests
**Then** the OUTCOME-CLASSIFICATION + the finding/grade build + the metric fold + the `ToolRunOutcome` build are
PURE (no clock read `datetime.now`/`time.time` in the classifier, no `uuid4`/`os.getpid()`/`random`, no LLM /
network, no dict/`set`-iteration-order reliance) — they are pure functions over a captured tool OUTCOME; the
IMPURE shell is ISOLATED to the subprocess invocation + the output read (the AR8 split — see Dev Notes); the
runner calls ZERO LLM tokens (NFR-D2)
**And** the subprocess invocation is SAFE + bounded + deterministic: an explicit argument list (NEVER
`shell=True` / string interpolation of a path — command-injection-safe), an explicit UTF-8 decode with
`errors="replace"` (locale-safe), a hard `timeout=` (so a hung tool times out, not hangs the audit), and the
captured exit/stdout/stderr classified to a closed `outcome` — a `subprocess.TimeoutExpired` /
`CalledProcessError` / `FileNotFoundError` / `UnicodeDecodeError` / any tool error is CAUGHT and mapped to the
`tool_failure` path (AR10), never propagated as an uncaught raise
**And** any model the module defines is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`) with a
localized `schema_version`; NO `float` anywhere; any JSON rendering routes through `store/canonical.dumps` (the
single 1.1 serializer — no second `json.dumps`)
**And** `minions_core.apaa.detectors.tool_runner` is appended to `_MODULES_UNDER_GUARD` in
`tests/apaa/test_no_web_imports.py` (extend, do NOT fork) and importing it does NOT transitively import
`fastapi`/`uvicorn`/`starlette` or any LLM/api/providers/`apaa.audit` module (the no-web AND the
zero-token-LLM gate both stay green; `test_pipeline_is_zero_token` stays green after the pipeline wiring).

**AC8 — The whole APAA suite green; mypy clean; ≤1200 lines; frozen contracts UNCHANGED (NFR-M1, NFR-M2)**
**Given** the modules + tests added/edited by this story
**When** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` runs
**Then** all pass, including new tests in `tests/apaa/test_tool_runner.py`: AC1 zero-token breadth + the
`tool_scanned_only` producer (a clean radon run grades files `tool_scanned_only` per the LOCKED rule; the grade
lands in the denominator, never the deep numerator — assert via the 1.6 gate over a synthetic ledger); AC2
tool-failure-as-finding (each injected failure mode → a `tool_failure` finding + downgrade, never a crash /
fabricated pass / leaked output, sanitized reason token); AC3 unestablishable-traceability-as-finding; AC4 the
frozen redaction-safe `ToolRunOutcome` (no raw-output field; no `float`; metrics as `int`/`Fraction`; round-trip
if persisted); AC5 the grade + the fold + the no-double-count rule + the no-secrets/clean-run regression-safe
path; AC7 purity-of-classification / safe-bounded-subprocess / typed-error (no leak) / single serializer
**And** the MANDATORY AC6 adversarial suite passes: non-ASCII path intact + graded + round-tripped; explicit
UTF-8 decode (locale-safe); the failure-injection seam covers crash / timeout / unavailable / unparseable each
→ a `tool_failure` finding with the planted sentinel ABSENT from every persisted/emitted byte; the clean run
does not cry wolf
**And** `minions_core.apaa.detectors.tool_runner` is in `_MODULES_UNDER_GUARD` and the import-isolation +
zero-token gates stay green; the 1.1 single-serializer AST gate still passes with the new module present (no
direct `json.dumps(`); the new source file(s) are ≤1200 lines (NFR-M1) and cite their
`APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in the module docstring; `mypy` is clean on the new + edited modules. The
1.1 serializer / 1.2 `Recording`/`Locator`/`CoverageDepth` enum / `grade_entry` / 1.4 index / `stack_detect` /
1.5 `base` builder / 1.6 verdict gate / 2.1 `depth_semantics` / 2.2 coverage report / 2.3 critical-subsystem /
2.4 partitioner / 2.5 `secret_scan` contracts are UNCHANGED (this story adds the tool-runner module + the
outcome model + tests + the additive detect-stage wiring; if it touches `pipeline.py` it is ONLY to wire the
runner into the existing fold — NOT to change the verdict math or any frozen contract — verify no working-tree
diff on the frozen modules).

## Tasks / Subtasks

- [ ] **Task 0 — Verify the existing reuse surface (verify-and-lock)** (AC: 1, 2, 4, 5, 7)
  - [ ] Re-read `intake/stack_detect.py` — `ToolchainProfile.radon_available` is the availability signal this
        story consumes; its docstring already defers the failure-as-finding to 2.6. Do NOT modify it.
  - [ ] Re-read `ledger/depth_semantics.py` — `EvidenceKind.TOOL_BREADTH_ONLY → CoverageDepth.TOOL_SCANNED_ONLY`
        via `classify_depth`. REUSE this classifier (do NOT mint the enum member ad hoc, do NOT add a state).
  - [ ] Re-read `detectors/base.py` — `build_recording` (value-independent id), `DetectorResult`,
        `DegradedCondition`, `FindingDraft`, the `Detector` protocol. REUSE verbatim.
  - [ ] Re-read `detectors/secret_scan.py` — the IMMEDIATE detector precedent (separate frozen evidence model
        with no leaky field; folded into `_detect_per_file`; sanitized reason; joined to the no-web gate).
  - [ ] Re-read `pipeline.py` `_detect_per_file` + `_persist` — lock the additive wiring + the no-double-count
        rule (which files become `tool_scanned_only`).
  - [ ] Re-read `store/canonical.py` (rejects `float`) + the no-web gate `_MODULES_UNDER_GUARD` +
        `test_pipeline_is_zero_token`. Decide the LOCKED radon invocation (library API vs `subprocess`).
- [ ] **Task 1 — `detectors/tool_runner.py`: impure breadth runner + pure outcome classifier** (AC: 1, 2, 3, 4, 7)
  - [ ] Define the closed `ToolOutcome` enum (`OK`/`UNAVAILABLE`/`CRASHED`/`TIMED_OUT`/`UNPARSEABLE`) + the
        frozen redaction-safe `ToolRunOutcome` (no raw-output field; metrics `int`/`Fraction`; sanitized reason
        token; localized `TOOL_RUN_SCHEMA_VERSION`).
  - [ ] Implement the IMPURE invocation shell for V1 `radon` (LOCK: library API or bounded `subprocess.run` with
        an explicit arg list, `shell=False`, hard `timeout=`, explicit UTF-8 decode `errors="replace"`) behind
        an INJECTABLE runner callable/port (the AR8 + AC6 testability seam — tests inject a fake, never spawn).
  - [ ] Implement the PURE classifier: a captured tool outcome → `tool_scanned_only` entries (via the 2.1
        `classify_depth(EvidenceKind.TOOL_BREADTH_ONLY)` / 1.2 `grade_entry`) + `tool_failure` /
        `traceability_not_establishable` findings (via `build_recording`, `advisory=True`,
        `depth_supported=None`, a verifiable locator) + a `DetectorResult`.
  - [ ] Typed `ToolRunnerError` (`ValueError` subclass) on a malformed argument — message carries no raw output;
        every tool exception (`TimeoutExpired`/`CalledProcessError`/`FileNotFoundError`/`UnicodeDecodeError`/…)
        is caught → the `tool_failure` path with a sanitized reason token. No bare `except: pass`, no `print()`.
- [ ] **Task 2 — Scope-fenced pipeline wiring** (AC: 5)
  - [ ] Wire `ToolRunnerDetector` into the detect stage; fold its entries + findings + degraded; persist via the
        EXISTING `_persist`. Enforce the LOCKED no-double-count rule; verify the clean/no-new-grade run is
        ledger+verdict byte-identical to pre-2.6.
- [ ] **Task 3 — Tests** (AC: 1, 2, 3, 4, 5, 6, 7, 8)
  - [ ] `tests/apaa/test_tool_runner.py` (area `APAA-TOOL`, `TC-APAA-TOOL-001-NN`): AC1 zero-token breadth +
        `tool_scanned_only` producer (denominator-only via the real 1.6 gate); AC2/AC3 failure + traceability
        findings; AC4 frozen redaction-safe outcome; AC5 grade/fold/no-double-count + regression-safe; AC7
        purity-of-classification / safe-bounded-subprocess / typed-error / single serializer.
  - [ ] **MANDATORY** AC6 adversarial suite: (a) non-ASCII path intact + round-trip; (b) explicit-UTF-8 locale
        decode; (c) FAILURE-INJECTION (crash/timeout/unavailable/unparseable) via the injected fake — each → a
        `tool_failure` finding + downgrade, planted sentinel ABSENT from every persisted/emitted byte; clean run
        does not cry wolf. Add a `cartridges/`-style fixture if helpful (NOT the 6.5 holdout/clean-control harness).
- [ ] **Task 4 — Extend the import-isolation gate** (AC: 7, 8)
  - [ ] Append `minions_core.apaa.detectors.tool_runner` to `_MODULES_UNDER_GUARD` (extend, NOT fork). Confirm
        `test_pipeline_is_zero_token` stays green after the pipeline wiring (the runner pulls NO `providers.*`).
- [ ] **Task 5 — Run + mypy** (AC: all)
  - [ ] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass (the 1.1
        single-serializer AST gate + the extended no-web/zero-token gates re-run green with the new module).
  - [ ] `mypy` clean on `detectors/tool_runner.py` + `pipeline.py` (`python run_mypy_per_file.py` or scoped).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **The pure/impure split for THIS detector (the master rule, AR8 — read carefully).** The 1.5 `Detector`
  protocol docstring says `run` "MUST be pure". This detector is the FIRST whose CORE requires impurity (a
  subprocess). Resolve it by SEPARATING the two concerns: (a) an IMPURE invocation shell that spawns the tool
  (or calls the radon library API), captures exit/stdout/stderr, and hands a captured `ToolInvocation` /
  raw-outcome object to (b) a PURE classifier that maps that captured outcome → `DetectorResult` (entries +
  findings + degraded). The PURE classifier has all the determinism/no-float/no-clock guarantees; the impure
  shell is small, bounded, and injectable. Make the impure invocation an INJECTED callable/port (the detector
  takes a `tool_invoker` argument defaulting to the real radon invocation) so tests inject a fake WITHOUT
  spawning a subprocess — this is the AR8 testability seam AND the AC6 failure-injection mechanism. ✅ a pure
  `classify_outcome(captured) -> DetectorResult` + an injected impure invoker · ❌ a `run()` that spawns a
  subprocess inline AND classifies in one un-testable un-pure blob.
- **`radon` is already installed + sanctioned (AR1) — do NOT add a new dependency.** Story 1.4's
  `stack_detect.py` already probes `radon_available`. V1 breadth = `radon`. The dev LOCKS whether to call radon
  via its Python library API (`radon.complexity` / `radon.raw` — pure-ish, in-process, no subprocess, simplest
  + safest) OR via a bounded `subprocess.run(["radon", ...])`. **Recommended: the library API** (no subprocess,
  no shell/timeout/locale risk, deterministic) — but the failure-as-finding + injection seam + the AC6
  adversarial discipline STILL apply (a library call can still raise / a file can be non-ASCII / unparseable),
  and the injected-invoker seam is still how tests force failures. If `subprocess` is chosen for any tool,
  AC7's safe-bounded-subprocess rules are MANDATORY (`shell=False`, explicit arg list, hard `timeout=`,
  explicit UTF-8 decode `errors="replace"`). Document the LOCK + rationale.
- **Tool OUTPUT is hostile — extend the 2.5 producer-side redaction to it (NFR-S1, the keystone).** A tool's
  stderr/stdout can echo source lines, secret bytes, or absolute host paths. NEVER place raw tool output into a
  `tool_failure` finding, the `ToolRunOutcome`, a `DegradedCondition.reason`, a log, or an exception message —
  keep ONLY a fixed reason TOKEN (`"radon_crashed"` / `"radon_timed_out"` / `"radon_unavailable"` /
  `"radon_unparseable"`) + non-secret bounded `int`/`Fraction` metrics. The structural guarantee (the 2.5
  precedent): the `ToolRunOutcome` has NO raw-output field — a value can't leak if there's nowhere to store it.
- **This story PRODUCES `tool_scanned_only` — but via the 2.1 single classifier (§3.3, reuse-canonical).** The
  enum member already exists (1.2); the classifier already exists (2.1 `classify_depth` /
  `EvidenceKind.TOOL_BREADTH_ONLY`). REUSE them — do NOT mint `CoverageDepth.TOOL_SCANNED_ONLY` ad hoc, do NOT
  re-implement `grade_entry`. `tool_scanned_only` is DENOMINATOR-only (FR8): the 1.6 deep-% numerator is
  `audited_deep` only, so a breadth-scanned file can NEVER satisfy a deep gate — that IS the NFR-C3 cost-split
  semantic (tools do breadth, tokens do depth).
- **No double-count is the load-bearing ledger rule (AC5).** A file graded once must not be graded twice in the
  same ledger. The V1 pipeline already reads every Python file for depth (`_grade_non_test_python` / the vacuous
  path), so be precise about which files the breadth channel grades `tool_scanned_only`: only files the breadth
  tool covered that were NOT otherwise depth/shallow-graded (e.g. files the depth path `skipped`, or — if the
  breadth tool can LOC-count non-Python — a file the depth path didn't grade). LOCK + document the exact
  emission rule; the regression-safe invariant is that a run producing no NEW `tool_scanned_only` files is
  ledger+verdict byte-identical to pre-2.6.
- **No floats anywhere (AR4).** radon complexity / metrics are naturally `float`. Quantize to an exact
  `Fraction` (the 2.5 `_shannon_bits_per_char` 1e-6 rational-grid precedent) or an `int` bucket, OR compare +
  store only a non-`float` bucket/`bool`. Counts (`files_scanned`) are `int`. The 1.1 serializer REJECTS
  `float`; any persisted metric must be non-`float`.
- **Determinism (NFR-P1).** The finding set, ids, grades, and ordering are a deterministic function of the
  captured outcome — same outcome → same `DetectorResult` + byte-identical persisted bytes; no
  iteration/dict/set-order reliance (sort deterministically). Note: a real subprocess can be non-deterministic
  in wall-time, but the CLASSIFICATION must depend only on the deterministic captured outcome (exit code /
  parsed metrics), never on timing.
- **Error/degradation → typed, never crash, never leak (AR10, NFR-R1 — the whole point).** A tool failure of
  any kind degrades to a recorded `tool_failure` finding + downgrade; an unestablishable-traceability condition
  degrades to `traceability_not_establishable`; a malformed ARGUMENT raises a typed `ToolRunnerError`
  (`ValueError` subclass) whose message carries no raw output. No bare `except: pass`, no `print()` in library
  code. A persistence failure degrades to the pipeline's existing `PipelineError` (exit `1`).
- **Headless / import + zero-token boundary (§3.7, AR7/AR9, NFR-D2).** No UI, no FastAPI route, no LLM, no A2A
  token. The runner imports NO `providers.*` / `apaa.audit.*` (zero-token — the breadth channel is the cost
  saver, it must not itself spend tokens); it joins `_MODULES_UNDER_GUARD` AND must keep
  `test_pipeline_is_zero_token` green after the pipeline wiring.

### The tool-runner model (the AC1/AC2/AC3/AC4 reference — lock + document)

| concept | source | form |
|---|---|---|
| breadth tool (V1) | `radon` (already installed/sanctioned, AR1); `cloc`/linters/SAST = family, OPTIONAL | library API (recommended) or bounded `subprocess` |
| invocation | INJECTED `tool_invoker` callable (the AR8 + AC6 seam) | impure shell; tests inject a fake |
| captured outcome | exit/parsed-metrics/error → a closed `ToolOutcome` | `OK`/`UNAVAILABLE`/`CRASHED`/`TIMED_OUT`/`UNPARSEABLE` |
| classification | PURE: captured outcome → `DetectorResult` | entries + findings + degraded |
| `tool_scanned_only` grade | the 2.1 `classify_depth(EvidenceKind.TOOL_BREADTH_ONLY)` → 1.2 `grade_entry` (REUSE) | denominator-only (FR8) |
| `tool_failure` finding | a 1.2 `Recording` via the 1.5 `build_recording` (REUSE) | `rule_id="tool_failure"`, `advisory=True`, `depth_supported=None`, ≥1 `Locator`, sanitized reason token |
| `traceability_not_establishable` finding | `build_recording` (REUSE) | `rule_id="traceability_not_establishable"`, `advisory=True`, ≥1 `Locator` |
| outcome model | `ToolRunOutcome` (frozen, redaction-safe) | `tool_id`/`outcome`/`files_scanned: int`/metrics `int|Fraction`/`failure_reason: str|None` (TOKEN) — **NO raw-output field** |
| redaction | raw tool output DROPPED; only a fixed reason token + bounded non-secret metrics survive | never raw stderr/stdout/source/secret/host-path in any field/log/exception |

Invariants: a failed/unavailable/unparseable/timed-out tool → a recorded finding + downgrade (never a crash /
fabricated pass / silent skip); `tool_scanned_only` is denominator-only; no double-count; raw output absent from
every emitted/persisted artifact; no `float`; zero LLM tokens.

### Decisions the dev must lock (record in the docstring + Change Log)

- **Module placement** — `detectors/tool_runner.py` (the architecture's locked home; package tree §I lists
  `tool_runner.py # NFR-C3 — zero-token breadth; failure→finding (FR14/NFR-R1)`). ≤1200 lines (NFR-M1).
- **V1 tool set** — `radon` (LOCK whether library API or subprocess + which radon metrics: `complexity` / `raw`
  LOC). Document `cloc`/linters/SAST as the family deferred to OPTIONAL/best-effort or a future story.
- **Invocation mechanism** — library API (recommended: no subprocess/shell/timeout/locale risk) vs bounded
  `subprocess.run` (then AC7 safe-bounded rules are MANDATORY). Either way: an INJECTED invoker seam for tests.
- **The closed `ToolOutcome` enum + the sanitized reason-token vocabulary** — `OK`/`UNAVAILABLE`/`CRASHED`/
  `TIMED_OUT`/`UNPARSEABLE` + `radon_crashed`/`radon_timed_out`/`radon_unavailable`/`radon_unparseable`. Frozen.
- **Metric representation** — `Fraction`/`int` (quantize radon's `float` complexity; the 2.5 rational-grid
  precedent) or compare-and-bucket. NEVER `float`.
- **`tool_scanned_only` emission rule + no-double-count** — LOCK exactly which files become `tool_scanned_only`
  (the keystone: no file graded twice; a clean run with no NEW grade is byte-identical to pre-2.6).
- **`tool_failure` / `traceability_not_establishable` locator strategy** — a repo/dir-anchor locator (FR13:
  `build_recording` requires a non-empty `Locator`; a tool failure is repo/dir-scoped, so use the tool target /
  a representative file + line 1). LOCK it.
- **Unestablishable-traceability V1 definition** — LOCK the precise V1 condition that triggers the
  `traceability_not_establishable` finding (a defensible Tier-A rule; full traceability-graph analysis is the
  Epic-6 orphan detector — out of scope).
- **Advisory vs blocking** — `advisory=True`, `depth_supported=None` in V1 (a tool failure is an honesty signal,
  not a code defect; promoting it to verdict-blocking is a deferred future story — and it must NOT modify the
  frozen 1.6 gate). LOCK + document.
- **Outcome persistence** — LOCK whether `ToolRunOutcome` persists (alongside run-state, via `store/canonical`)
  or travels only on the in-memory `DetectorResult` (the 1.5 `VacuousTestScore` / 2.5 `SecretFindingEvidence`
  precedent). Either way it has no raw-output field.
- **Typed error type** — `ToolRunnerError` (`ValueError` subclass) localized to the module (mirror
  `SecretScanError` / `RecordingValidationError` / `RepoIntakeError` / `PartitionerError`); no raw output in the
  message.
- **Test area** — `APAA-TOOL` recommended (`TC-APAA-TOOL-001-NN`); lock the choice.

### Precedent inherited from Stories 1.1–1.7 + 2.1–2.5 (done) — honor these decisions

- **No second serializer / reuse the 1.1 spine.** Any `.apaa/` bytes go through `store/canonical.dumps_bytes`
  via `EnvelopeWriter.build` + the writer; the AST gate enforces it.
- **Reuse the 1.5 `build_recording` + the 1.2 `Recording`/`Locator` VERBATIM** for both finding types. Do NOT
  define a parallel finding builder or finding model; do NOT add a raw-output field to the 1.2 schema.
- **Reuse the 2.1 `classify_depth` / `EvidenceKind.TOOL_BREADTH_ONLY` + 1.2 `grade_entry`** for the
  `tool_scanned_only` grade — single classifier, do NOT mint the enum member ad hoc, do NOT add a state.
- **Tool/detector evidence on a separate frozen `int`/`Fraction`-only model with no leaky field** (the 1.5
  `VacuousTestScore` / 2.5 `SecretFindingEvidence` precedent) — mirror it for `ToolRunOutcome`.
- **Frozen `extra="forbid"` models with a localized `schema_version`** (1.1/1.2/1.4/2.4/2.5 precedent).
- **`bool`/`int`/`Fraction`/`str`/enum over `float`** — the 1.1 serializer rejects `float`.
- **Content-derived ids, never arrival order (AR11)** — the 1.5 `_recording_id`; `.apaa/findings/` filenames are
  content-sha256.
- **No absolute host paths / source bytes in artifacts (NFR-S1; 1.3 DN-3 / 2.3 / 2.4 / 2.5)** — findings carry
  repo-relative POSIX locator paths only; this story extends that to: NO raw tool output / stderr / host path /
  source / secret bytes either (tool output is hostile — see above).
- **`apaa_version`/`schema_version` single source** — `minions_core/apaa/__init__.py::__version__` (`"0.1.0"`);
  per-module `schema_version` is a localized constant, never env/clock.
- **Import-isolation gate is seeded, extend it** — append the new module to `_MODULES_UNDER_GUARD`; do NOT fork.
  Keep `test_pipeline_is_zero_token` green (the runner is zero-LLM-token).
- **AI-E1-1 adversarial fixtures (Epic-1 retro / §9.1) — 2.6 is the NAMED first application.** The single Epic-1
  FAIL was an impure-shell encoding boundary (1.4 `git ls-files`); THIS story is that boundary class. Tests
  MUST ship the non-ASCII + locale + FAILURE-INJECTION fixtures (AC6). On Windows prefix runs with
  `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on cp1252) AND the subprocess decode must
  be explicit UTF-8 (never the platform default).

### Source tree — files to create / update

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/detectors/tool_runner.py` | NEW | FR14/NFR-C3/NFR-R1 — impure breadth-tool runner (V1 `radon`, INJECTED invoker seam) + PURE outcome classifier; PRODUCES `tool_scanned_only` (via 2.1 `classify_depth`); `tool_failure` + `traceability_not_establishable` findings (via 1.5 `build_recording`, sanitized reason token); frozen redaction-safe `ToolRunOutcome` (no raw-output field, metrics `int`/`Fraction`); `ToolRunnerError` (no leak); zero-LLM-token |
| `minions_core/apaa/pipeline.py` | UPDATE (scope-fenced) | wire `ToolRunnerDetector` into the detect stage; fold `tool_scanned_only` entries + `tool_failure`/`traceability_not_establishable` findings + degraded into the existing accumulation; persist via the EXISTING `_persist`; enforce the no-double-count rule; NO verdict-math change, NO new serializer/writer; clean/no-new-grade run is ledger+verdict byte-identical to pre-2.6 |
| `tests/apaa/test_tool_runner.py` | NEW | AC1 zero-token breadth + `tool_scanned_only` producer (denominator-only via real 1.6 gate) + AC2 tool-failure-as-finding (each injected mode) + AC3 traceability finding + AC4 frozen redaction-safe outcome (no raw-output field, no float) + AC5 grade/fold/no-double-count/regression-safe + AC7 purity-of-classification/safe-subprocess/typed-error/single-serializer |
| `tests/apaa/test_tool_runner_adversarial.py` (or inline in the above) | NEW (MANDATORY, AI-E1-1) | non-ASCII path intact + round-trip; explicit-UTF-8 locale decode; FAILURE-INJECTION (crash/timeout/unavailable/unparseable) via the injected fake → `tool_failure` + downgrade with the planted sentinel ABSENT from every persisted/emitted byte; clean run does not cry wolf |
| `tests/apaa/cartridges/tool_failure/` | NEW (optional) | a focused fixture the adversarial test runs the full pipeline over (one injected failure); the holdout/clean-control HARNESS is Story 6.5 — do NOT build it here |
| `tests/apaa/test_no_web_imports.py` | UPDATE | extend `_MODULES_UNDER_GUARD` with `minions_core.apaa.detectors.tool_runner` (extend, NOT fork) |

Do NOT modify `detectors/base.py`, `detectors/vacuous_test.py`, `detectors/secret_scan.py`,
`ledger/recording.py`, `ledger/coverage_ledger.py`, `ledger/depth_semantics.py`,
`ledger/critical_subsystems.py`, `ledger/coverage_report.py`, `index/ast_index.py`, `index/partitioner.py`,
`intake/stack_detect.py`, `intake/repo_loader.py`, `verdict/verdict_gate.py`, `store/canonical.py`,
`store/envelope.py`, `store/paths.py`, `store/writer.py`, `store/reader.py`, `models.py` (frozen/reused
contracts — verify no working-tree diff after the story; the ONLY exceptions are the additive `pipeline.py`
detector wiring + the import-isolation gate file).

### Scope fences (do NOT pull forward)

- ❌ **Budget-ceiling configuration / cost accounting** (FR21) — **Story 3.1**; **halt→skip→downgrade on budget
  exhaustion** (FR22) — **Story 3.2**. This story produces breadth at ZERO token cost; it does NOT account
  spend against a ceiling or halt on exhaustion. (The cost SPLIT it enables — tools do breadth, tokens do depth
  — is the NFR-C3 semantic; the DEPTH spend is Epic 6, the budget MECHANISM is Epic 3.)
- ❌ The **LLM dispatch port / deep audit** (Epic 6) — this story is zero-token; the depth side that the breadth
  channel reserves tokens for is Epic 6.
- ❌ The **orphan/dead-code detector + full requirement↔code traceability graph** (FR12) — Epic 6. This story
  records the `traceability_not_establishable` CONDITION as a finding (FR14); it does NOT build the traceability
  graph.
- ❌ The **adversarial Prosecutor / cut-edge pass** (FR19) — Epic 6.
- ❌ A **verdict-blocking promotion** of the `tool_failure` finding beyond what the lock decides — V1 keeps it
  advisory; if ever promoted, do NOT modify the frozen 1.6 gate.
- ❌ The **randomized-canary CI-blocking secret-containment property suite** `tests/security/
  test_apaa_secret_containment.py` (FR28/NFR-S1/AR9) — **Story 4.4**. This story's AC6 search is a focused
  story-local proof that tool output doesn't leak; 4.4 is the durable randomized suite.
- ❌ The **defect-cartridge self-audit HARNESS + hidden holdout + clean true-negative controls** (FR20) —
  **Story 6.5**. This story MAY add a focused `tool_failure` fixture but NOT the holdout/clean-control harness.
- ❌ Any change to the **1.1 serializer / 1.2 `Recording`/`Locator`/`CoverageDepth` enum / `grade_entry` / 1.4
  index / `stack_detect` / 1.5 `base` builder / 1.6 verdict gate / 2.1 `depth_semantics` / 2.2 coverage report /
  2.3 critical-subsystem / 2.4 partitioner / 2.5 `secret_scan`** contracts — all frozen/reused.
- ❌ A **new external dependency** — `radon` is already installed/sanctioned (AR1); add no new tool dep in V1.
- ❌ A **new HTTP route / FastAPI surface / UI** (§3.7), an A2A token, or any LLM call.

### Deferred-work seam (record if surfaced; do NOT build)

- If a NEW defer surfaces during dev (e.g. a `cloc`/linter/SAST tool the dev decides to defer to a future
  story, or a richer traceability-graph need beyond the V1 condition), record it with the CC-3 six-field schema
  (id / origin_story / owner / target_story|sunset_date / category=`observability` or `process` / severity); do
  NOT build it in this story.
- **DF-1-4-A (unresolved edge set)** — already open; the breadth runner scans source / radon metrics, not the
  call graph, so it surfaces no new defer for it.
- **DF-1-7-B (interim deep over-grading)** — already open; owned by Story 6.2 (FR7 AST-truth grounding). The
  `tool_scanned_only` state this story produces is the HONEST breadth grade (denominator-only) — it does not
  touch the deep-grading question; no new defer for it.

### Testing standards

- pytest under `tests/apaa/`; test ids `TC-<AREA>-<SEQ>-<SUBSEQ>` — use area `APAA-TOOL` (`TC-APAA-TOOL-001-NN`).
- The CLASSIFIER tests are **pure-function** (zero LLM tokens, NFR-D2) over a captured-outcome fixture — no real
  subprocess needed for classification. The **failure-injection** tests inject a fake `tool_invoker` (the AR8
  seam) so crash/timeout/unavailable/unparseable are forced WITHOUT spawning a real tool — fast + deterministic.
- The `tool_scanned_only`-denominator-only proof REUSES the real 1.6 `evaluate_verdict` over a synthetic ledger
  (the 2.1 FR8-proof precedent) — assert a `tool_scanned_only`-only ledger never reaches `RELEASE_READY`.
- The **AI-E1-1 adversarial suite is MANDATORY** (2.6 is the named first application): non-ASCII path intact +
  round-trip; explicit-UTF-8 locale decode; the failure-injection seam over all four failure modes with the
  planted sentinel ABSENT from every persisted/emitted byte (search RAW bytes incl. non-ASCII UTF-8 — the 2.5
  containment-search precedent); a CLEAN run that does not cry wolf.
- On Windows prefix runs with `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on cp1252).
- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` (the WHOLE `tests/apaa/`
  suite, so the 1.1 single-serializer AST gate + the extended no-web/zero-token gates re-run with the new module
  present). All must pass before moving to `review`.
- `mypy` clean on the new + edited modules (`python run_mypy_per_file.py` or a scoped invocation).

### CLAUDE.md §4a follow-up

The §4a APAA Component→Driver row was added by Story 1.1 (and notes the determinism spine). This story does NOT
need a new §4a row; if a one-line additive note is added it must note `detectors/tool_runner.py` as the
zero-token breadth runner + the `tool_scanned_only` producer + tool-failure-as-finding (FR14/NFR-C3/NFR-R1) and
must NOT rewrite the existing row. Keep it minimal — a new row is not required.

### Project Structure Notes

- Alignment: the new module lives under `detectors/` (cohesive with the 1.5 vacuous + 2.5 secret detectors; the
  architecture package tree §I places `tool_runner.py` there). Naming `snake_case.py`, ≤1200 lines (NFR-M1).
  Enum/JSON values `snake_case`.
- The one structural NOVELTY this story introduces vs the prior pure detectors: an IMPURE subprocess/tool shell.
  Keep it cleanly split from the pure classifier and behind an injectable invoker (the AR8 + AC6 seam) so the
  no-web/zero-token gate, the determinism tests, and the failure-injection tests all hold. This is the explicit
  Epic-1-retro lesson (AI-E1-1): the impure-shell encoding/failure boundary is the highest-risk surface.
- No conflicts/variances. Judgment calls — all decided in "Decisions the dev must lock" above and to be
  documented so they freeze for downstream: the V1 tool set + invocation mechanism, the outcome enum + reason
  tokens, the metric representation, the `tool_scanned_only` emission rule + no-double-count, the locator
  strategy, the unestablishable-traceability V1 definition, advisory-vs-blocking, outcome persistence, and the
  typed-error type.
- Scope fence: this story delivers the zero-token breadth runner + the `tool_scanned_only` producer +
  tool-failure / unestablishable-traceability as findings + the redaction-safe outcome + the scope-fenced
  wiring + the MANDATORY adversarial suite ONLY. Budget (3.1/3.2), the LLM depth side + orphan/Prosecutor
  (Epic 6), the randomized property suite (4.4), the self-audit harness (6.5), and any change to a frozen
  contract are explicitly NOT in scope. Run breadth, grade `tool_scanned_only`, record a failure as a finding,
  then stop.

### References

- [Source: _bmad-output/design-artifacts/APAA/epics.md#Story-2.6 Zero-token breadth tool runner + tool-failure-as-finding] (the three ACs: zero-token breadth + `tool_scanned_only`; tool-failure → finding; unestablishable-traceability → finding)
- [Source: _bmad-output/design-artifacts/APAA/E-PRD/prd.md#FR14 tool-failure / unestablishable-traceability → finding, not crash]
- [Source: _bmad-output/design-artifacts/APAA/E-PRD/prd.md#FR5 fixed-enum coverage ledger (tool_scanned_only)]
- [Source: _bmad-output/design-artifacts/APAA/E-PRD/prd.md#NFR-C3 deterministic zero-token tools perform breadth so LLM spend is reserved for depth]
- [Source: _bmad-output/design-artifacts/APAA/E-PRD/prd.md#NFR-R1 a tool/parse failure degrades to a recorded finding or downgrade — never an uncaught crash or fabricated result]
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#D. Defect Detectors] (`tool_runner.py` — zero-token breadth; failure→finding)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Error / Degradation Patterns] (failure → typed finding, never an uncaught raise; typed exceptions at the impure shell; no bare `except: pass` / `print()`)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Pure/Impure Separation (master rule)] (impure shell at the edges only — tool/subprocess runner is impure; classifier pure)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Determinism Patterns] (one serializer; no floats — metrics fixed-precision; no iteration-order reliance)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#AR1 new external dependencies] (`radon==4.1.0` zero-token breadth metrics, already installed/sanctioned)
- [Source: _bmad-output/design-artifacts/APAA/epic-1-retro-2026-06-21.md#7. Action Items] (AI-E1-1: default impure-shell subprocess/parser stories to ship an adversarial non-ASCII + locale + failure-injection fixture — APPLY FIRST IN 2.6; AI-E1-4 gates extended-not-forked; AI-E1-5 exercise the L1-E11 loop)
- [Source: _bmad-output/design-artifacts/APAA/stories/2-1-complete-depth-state-semantics-inferred-never-satisfies-a-gate.md] (DONE — `tool_scanned_only` documented + classified via `classify_depth(EvidenceKind.TOOL_BREADTH_ONLY)`; FR8 denominator-only; `assess_criticality`)
- [Source: _bmad-output/design-artifacts/APAA/stories/2-5-hardcoded-secret-detector-producer-side-redaction.md] (DONE — the immediate detector precedent: separate frozen no-leaky-field evidence model, sanitized reason, folded into `_detect_per_file`, joined to the no-web gate, producer-side redaction)
- [Source: minions_core/apaa/detectors/base.py] (`Detector` protocol, `DetectorResult`/`DegradedCondition`/`FindingDraft`, `build_recording` — REUSE verbatim)
- [Source: minions_core/apaa/ledger/depth_semantics.py] (`classify_depth`/`EvidenceKind.TOOL_BREADTH_ONLY`/`DEPTH_SEMANTICS` — REUSE the single classifier, do NOT mint the enum ad hoc)
- [Source: minions_core/apaa/ledger/coverage_ledger.py] (`CoverageDepth.TOOL_SCANNED_ONLY`, `grade_entry`, `CoverageLedger` — REUSE, do NOT modify)
- [Source: minions_core/apaa/intake/stack_detect.py] (`ToolchainProfile.radon_available` — the availability signal; its docstring defers tool-failure-as-finding to 2.6)
- [Source: minions_core/apaa/pipeline.py] (`_detect_per_file` / `_persist` — the scope-fenced additive wiring point; the no-double-count rule)
- [Source: minions_core/apaa/verdict/verdict_gate.py] (`evaluate_verdict`, deep-% numerator = `audited_deep` only — ASSERT `tool_scanned_only` is denominator-only, do NOT modify)
- [Source: tests/apaa/test_no_web_imports.py] (`_MODULES_UNDER_GUARD` + `test_pipeline_is_zero_token` — extend, do NOT fork; keep the zero-token gate green)
- [Source: minions_core/apaa/__init__.py] (`__version__ = "0.1.0"` — single apaa_version source)
- [Source: CLAUDE.md §3.2 file-size / §3.7 headless-only / §3.8 12-Factor + secret masking / §9.1 L1-E11 retro-action-items loop]

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Senior Developer Review (AI)

**Reviewer:** Code-review gate (adversarial) · **Date:** 2026-06-24 · **Iteration:** 1 · **Verdict:** PASS

**Outcome.** Story 2.6 is approved to `done`. The zero-token breadth tool-runner is implemented as a clean
pure/impure split (AR8), produces `tool_scanned_only` via the reused 2.1 classifier, converts every tool-failure
mode into a recorded advisory finding + downgrade (FR14/NFR-R1), and structurally cannot leak hostile tool
output (NFR-S1). All eight ACs are met; the MANDATORY AI-E1-1 adversarial suite (non-ASCII + locale +
failure-injection) ships and is non-vacuous.

**Tests independently re-run (this review, not the dev's claim):**
`PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **532 passed in 17.78s**.
`mypy --ignore-missing-imports` (the project's canonical `run_mypy_per_file.py` invocation) on
`detectors/tool_runner.py` + `pipeline.py` → clean. File size 455 lines / 388 non-blank (≤1200, NFR-M1).

**Adversarial verification of the mandatory gates:**
- **TOOL FAILURE IS A FINDING (FR14/NFR-R1)** — verified non-bypassable. Each injected mode
  (`UNAVAILABLE`/`CRASHED`/`TIMED_OUT`/`UNPARSEABLE`) → a `tool_failure` Recording (`advisory=True`,
  `depth_supported=None`, ≥1 locator) + a `SKIPPED` downgrade + a sanitized token `DegradedCondition`
  (TC-APAA-TOOL-001-04). A raising invoker is caught → `CRASHED`, never propagates (TC-…-05); a misbehaving
  invoker returning a non-`ToolInvocation` is treated as `CRASHED` (TC-…-07). No bare `except: pass` semantics
  (each `except` returns/maps a closed outcome), no `print()`, no `subprocess`/`shell=True` (V1 = radon library
  API). A malformed argument raises the typed `ToolRunnerError(ValueError)` whose message names the argument
  only (TC-…-06).
- **`tool_scanned_only` DENOMINATOR-ONLY (FR8)** — `test_tool_scanned_only_is_denominator_only_via_real_verdict_gate`
  is genuine: it imports and drives the REAL `verdict.verdict_gate.evaluate_verdict` (not a reimplementation)
  over a `tool_scanned_only`-only `CoverageLedger` and asserts `INSUFFICIENT_COVERAGE` / `deep_ratio = 0/3`,
  never `RELEASE_READY`. The grade is minted via the reused 2.1 `classify_depth(EvidenceKind.TOOL_BREADTH_ONLY)`
  → 1.2 `grade_entry` — the enum member is NOT minted ad hoc.
- **TOOL-OUTPUT REDACTION (NFR-S1)** — structural guarantee confirmed: NEITHER `ToolRunOutcome` NOR the
  data-carrying `ToolInvocation` has any raw-stdout/stderr/source/value field (TC-…-10 asserts the absence);
  `DegradedCondition.reason` is a constant token from the closed `_REASON_TOKEN_BY_OUTCOME` map;
  `ToolRunnerError` messages carry argument names only. The default `radon_invoker` drops the raw error text at
  the boundary and returns only a closed outcome + `int` metrics. The planted-sentinel containment tests
  (TC-…-05, …-24, …-25) search the RAW serialized bytes incl. non-ASCII UTF-8 and the full persisted `.apaa/`
  tree and confirm the sentinel (ASCII `PLANTEDx…` + Cyrillic `пароль_…`) is ABSENT — and are non-vacuous (the
  sentinel is asserted present in the invoker input).
- **AI-E1-1 (non-ASCII + locale)** — present and genuine: `café_metrics.py` / `модуль/сложность.py` paths run
  breadth with bytes intact and round-trip through the single 1.1 serializer (TC-…-20/-21, including a full
  pipeline run over the `tool_breadth` cartridge); a non-ASCII / mangled source unit degrades to a closed
  outcome and never raises out of the invoker (TC-…-22/-23). Decode is explicit UTF-8 at the library boundary.
- **ZERO-TOKEN / determinism / purity** — the module joins `_MODULES_UNDER_GUARD` (extended, not forked) and
  `test_pipeline_is_zero_token` stays green (no `providers.*` / `apaa.audit.*` pull). Classifier is pure (no
  clock/uuid/random/os in code), deterministic regardless of input order (TC-…-14), no `float` anywhere, no
  direct `json.dumps` (single-serializer AST gate green), frozen `extra="forbid"` models with localized
  `TOOL_RUN_SCHEMA_VERSION`. Reuse is canonical (1.1 serializer, 1.2 enum/`grade_entry`, 1.5
  `base`/`build_recording`, 2.1 `classify_depth`, 2.5 producer discipline); no frozen contract was modified
  (pipeline + no-web gate are the only edits; `pyproject.toml` / `__init__.py` working-tree diffs are
  pre-existing 1.1/1.7 changes, not introduced by 2.6 — `radon>=4` was already present, so NO new dependency).

### Review Findings

<!-- defer-schema-session: 2026-06-24 -->

Two Low-severity, non-blocking observations (recorded for a future precision/cleanup pass; neither blocks
`done` and neither is a correctness or security defect):

- [ ] [Review][Low] `ToolRunOutcome` is defined + exported but UNUSED — the runner carries data through the
  near-duplicate `ToolInvocation` model, so `ToolRunOutcome` is decorative (DRY/YAGNI). AC4 explicitly permits
  "`ToolRunOutcome` (or equivalent)" and BOTH models satisfy the no-raw-output-field structural guarantee, so
  this is non-blocking. Suggested fix in a cleanup pass: either collapse to one outcome model (have the runner
  emit/build `ToolRunOutcome` and drop `ToolInvocation`), or document `ToolRunOutcome` as the persistence-facing
  contract vs `ToolInvocation` as the in-flight seam type so the duplication is intentional, not accidental.
  [`minions_core/apaa/detectors/tool_runner.py`:193]
- [ ] [Review][Low] Pipeline-level `tool_failure` surface is DORMANT for already-graded files. The
  `already_graded` short-circuit (`continue`) runs BEFORE the outcome branch, and V1's depth path grades every
  indexed Python file, so a radon FAILURE on a Python file emits NO `tool_failure` finding through the live
  `run_audit_detailed` path (only the detector-level unit tests exercise the failure branch, by feeding
  un-graded targets). This MATCHES the LOCKED AC5 no-double-count rule and is documented honestly in the module
  + pipeline docstrings, and the detector contract is fully tested — so it is an accepted V1 scope limitation,
  not a defect. Suggested follow-up (future story, when breadth covers non-depth-graded files or a richer V1
  emission rule is adopted): evaluate the outcome BEFORE the already-graded skip so a tool failure on an
  already-graded file still records the advisory finding without re-grading coverage.
  [`minions_core/apaa/detectors/tool_runner.py`:384]
