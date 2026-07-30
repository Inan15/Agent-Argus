# Story 2.1: Complete depth-state semantics + `inferred`-never-satisfies-a-gate

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As an Engineering Lead,
I want every file graded into the correct one of the five coverage depth states by a single documented
grading rule, criticality assessed by file CONTENT (not filename), and `inferred` evidence provably excluded
from satisfying any verdict gate,
so that narrative/doc evidence can never inflate a release verdict and coverage-gaming by renaming is
defeated — the evidence-poisoning defense (FR8), the FIRST story of Epic 2 (Full Coverage Ledger & Defect
Detectors) and the honesty surface that the readable ledger (2.2), critical-subsystem clause (2.3), and
partitioning (2.4) all fold over.

## Story Context

This is **Story 1 of Epic 2** (Full Coverage Ledger & Defect Detectors). Epic 1 delivered the determinism
spine and a working-if-narrow auditor (the signature 🔴 on the vacuous-test cartridge). Epic 2 completes the
**honesty surface** of the coverage ledger. This story is the surface's keystone: it locks the SEMANTICS of
all five depth states (what evidence earns each state), makes criticality CONTENT-derived (anti-gaming), and
proves — with explicit synthetic-ledger unit tests — that `inferred` (and `skipped`/`tool_scanned_only`)
evidence can NEVER satisfy a coverage gate (FR8).

**What already exists (verify-and-lock, do NOT rebuild).** Two Epic-1 modules already carry most of the
mechanism this story completes — this is largely a **complete-the-semantics + verify-and-lock** story, NOT a
net-new mechanism build:

- **Story 1.2 (done) — `ledger/coverage_ledger.py`.** The closed five-member `CoverageDepth` enum
  (`AUDITED_DEEP / AUDITED_SHALLOW / TOOL_SCANNED_ONLY / INFERRED / SKIPPED`) ALREADY EXISTS and is
  membership-pinned. `CoverageLedger.build(...)`, `counts_by_depth()`, `deep_count()`, `total()`, and the
  pure `grade_entry(...)` (claim-required `audited_deep`; silence → shallow, FR6) ALL EXIST. **Do NOT add a
  sixth state, do NOT modify the enum, do NOT re-implement `grade_entry`.**
- **Story 1.6 (done) — `verdict/verdict_gate.py`.** The FR8 gate-MATH already holds: the deep-% numerator
  counts ONLY `audited_deep` entries (`CoverageLedger.deep_count()`); `inferred`/`skipped`/
  `tool_scanned_only`/`audited_shallow` are in the DENOMINATOR (`total()`) but NEVER the numerator — so a
  100%-`inferred` ledger is 0% deep → `INSUFFICIENT_COVERAGE`. The 1.6 docstring already documents
  "`inferred` never satisfies a gate (FR8)". **The gate is correct; this story does NOT change the gate's
  threshold logic.** What is MISSING at the gate layer is an explicit, named FR8 regression test over a
  synthetic ledger asserting the property directly (1.6's tests focus on the verdict three-way + boundaries +
  the moat; the `inferred`-never-satisfies assertion exists but is not the named FR8 keystone test this
  story makes mandatory and exhaustive).
- **`pipeline.py` (done, 1.7).** Assigns depths today with a coarse rule (`_detect_per_file` /
  `_grade_non_test_python`): non-Python → `skipped`; Python test → `audited_shallow` (via the 1.5 detector);
  Python non-test cleanly-parsed → `audited_deep` (claim-present); unparseable Python → `skipped`. It does
  NOT emit `tool_scanned_only` or `inferred` at all (no breadth tool runner yet — 2.6; no narrative/doc
  intake yet). **This story does NOT rewire the pipeline's per-file grading loop** (that is incrementally
  completed by 2.5/2.6 as detectors land); it provides the documented grading-rule REFERENCE + a pure
  classifier the later detectors and the readable surface (2.2) consume, plus the criticality-by-content
  assessment.

**The net-new deliverable of THIS story.** A single pure module
`minions_core/apaa/ledger/depth_semantics.py` that (a) DOCUMENTS the canonical grading rule for each of the
five depth states (what evidence earns each), (b) provides a pure `assess_criticality(...)` that derives
criticality from file CONTENT signals (not the filename), and (c) provides a pure
`inferred_satisfies_gate(...)`-style assertion surface the FR8 keystone test pins — PLUS the mandatory FR8
regression tests over synthetic ledgers at the GATE layer. It imports ONLY the 1.2 ledger models; it is
PURE (AR8) and joins the import-isolation gate.

**Carry-forward from the Epic-1 retro (CLAUDE.md §9.1 / L1-E11 — this story discharges these items).**
- **AI-E1-1 (test-infra 🟠) — adversarial non-ASCII / locale fixtures for impure-shell parsers.** This story
  is PURE (no subprocess, no FS parse), so the *subprocess*-boundary risk does not apply directly. BUT the
  content-derived criticality assessment (AC3) reads file CONTENT/PATH tokens, so its tests MUST include
  **non-ASCII path + non-ASCII content fixtures** (e.g. `auth/café_guard.py`, a module whose security tokens
  are around non-ASCII identifiers) so the criticality classifier is proven not to silently drop or mis-class
  non-ASCII input. (Reuse / seed a `tests/apaa/fixtures/` helper if 2.5/2.6 have not yet created one.)
- **AI-E1-4 (process 🟢) — keep the three committed gates extended-not-forked.** Append the new module to
  `_MODULES_UNDER_GUARD` (do NOT fork the no-web-imports gate); keep the single-serializer AST gate +
  determinism golden discipline green.
- **AI-E1-5 (process 🟢) — exercise the L1-E11 loop.** This story explicitly references the AI-E1-* items it
  discharges (here).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 2.1) and the architecture / PRD. Drivers: **APAA-FR-8** (exclude
> `inferred` (narrative/doc) evidence from satisfying any verdict gate — the central driver), **APAA-FR-5**
> (the fixed-enum coverage ledger — five depth states with documented semantics), **APAA-FR-4-support**
> (criticality by content, not filename — the anti-gaming half that Story 2.3 consumes; this story builds the
> content-derived ASSESSMENT, NOT the operator designation / gate clause), **APAA-NFR-D2** (deterministic,
> zero-LLM-token), **APAA-NFR-M2** (frozen, additive-only contracts), **APAA-NFR-M1** (≤1200-line files),
> **AR4** (no `float`; no clock/uuid/random/iteration-order in any `.apaa/`-bound output), **AR8** (pure
> module — no I/O, no clock, no LLM), **AR10** (typed failure, never an uncaught raise / silent coerce),
> cross-cutting (hostile-repo robustness: coverage gaming + evidence poisoning).
>
> **SCOPE FENCE — Tier-A, single-purpose.** This story delivers ONLY: (1) the canonical DOCUMENTED grading
> rule for all five depth states + a pure classifier surface in `ledger/depth_semantics.py`; (2) the pure
> content-derived `assess_criticality(...)` (the FR4 anti-gaming ASSESSMENT only); (3) the MANDATORY FR8
> regression tests over synthetic ledgers proving `inferred`/`skipped`/`tool_scanned_only` can never satisfy
> a gate. It does NOT build, and MUST NOT pull forward: the **readable per-file ledger render** (FR9 — Story
> 2.2); the **critical-subsystem GATE CLAUSE + operator DESIGNATION** (FR4 gate half — Story 2.3 consumes
> this story's `assess_criticality`, but the `RELEASE_READY`-withheld-when-critical-shallow clause and the
> `--critical-subsystem` invocation flag are 2.3); **repository partitioning** (FR3 — Story 2.4); the
> **secret detector** (FR11 — Story 2.5); the **breadth tool runner** that actually PRODUCES
> `tool_scanned_only` grades (FR14 — Story 2.6 — this story only documents/classifies the state, it does not
> run `cloc`/`radon`); **full FR7 AST-truth grounding** of `audited_deep` (Epic-6 Story 6.2 — DF-1-7-B; V1
> stays claim-presence per the Epic-1 cut-order); and any change to the **1.6 verdict thresholds** or the
> **1.2 enum / `grade_entry`**. Verify-and-lock the existing mechanism, complete the semantics + criticality
> assessment + FR8 proof, then stop.

**AC1 — All five depth states have a documented, single-source grading rule (FR5, FR8)**
**Given** a file examined at some depth during an audit
**When** its coverage depth is assigned
**Then** `ledger/depth_semantics.py` documents the canonical grading rule for EXACTLY the five closed states
(reusing the 1.2 `CoverageDepth` enum verbatim — NO new state, NO enum edit) such that each file lands in
EXACTLY ONE state, with the rule recorded as both module docstring prose AND a machine-readable mapping
(e.g. a `DEPTH_SEMANTICS: dict[CoverageDepth, str]` description table or a `classify_depth(...)` pure
function over an evidence descriptor):
- `audited_deep` — an emitted deep claim is present (FR6; V1 = claim-presence — AST-truth grounding is the
  Epic-6 6.2 deferral DF-1-7-B, explicitly noted as the V1 honesty limitation).
- `audited_shallow` — the file was read/analyzed but no qualifying deep claim was emitted (silence → shallow,
  the 1.2 `grade_entry` downgrade), OR a deep claim was emitted but unverifiable (the 6.2 downgrade target —
  seam noted, NOT built here).
- `tool_scanned_only` — the file was covered ONLY by a zero-token breadth tool (`cloc`/`radon`/linter), never
  read for depth (the state Story 2.6 will PRODUCE; this story documents + classifies it).
- `inferred` — the only evidence is narrative/doc (a referencing requirement/comment/README), NOT a direct
  read of the file's own structure — the evidence-poisoning class FR8 excludes from gates.
- `skipped` — examined-but-ungradable / not examined (parse-failed, budget-skipped, non-analyzable) — in the
  denominator, never a deep claim.
**And** the documented rule is the single source of truth the later detectors (2.5/2.6) and the readable
surface (2.2) reference — it does NOT fork the 1.2 enum or re-implement `grade_entry`; a committed test pins
that `classify_depth`/`DEPTH_SEMANTICS` covers all five members (exhaustive, no silent default).

**AC2 — `inferred` (and `skipped`/`tool_scanned_only`) can never satisfy a verdict gate — MANDATORY FR8 proof (FR8)**
**Given** a synthetic `CoverageLedger` (1.2) whose only-or-dominant evidence is `inferred` (narrative/doc)
**When** the 1.6 `evaluate_verdict(ledger, ...)` gate evaluates coverage
**Then** that `inferred` evidence cannot satisfy any gate threshold — a 100%-`inferred` ledger returns
`INSUFFICIENT_COVERAGE` (0% deep, below the 20% floor), NEVER `RELEASE_READY`; and a ledger that is e.g. 59%
`audited_deep` + 41% `inferred` is NOT promoted to `RELEASE_READY` by the `inferred` entries (still < 60%
deep → `NOT_READY_FOR_RELEASE`) — proven by NAMED, explicit unit tests over synthetic ledgers (the
evidence-poisoning defense, the central FR8 driver)
**And** the SAME exclusion is proven for `skipped` and `tool_scanned_only` (only `audited_deep` counts toward
the gate numerator) — three explicit synthetic-ledger tests, one per non-deep-non-shallow state, plus the
"`inferred` cannot tip a sub-60% ledger over the line" test
**And** these tests REUSE the existing 1.6 `evaluate_verdict` + 1.2 `CoverageLedger.build` / `grade_entry`
verbatim (they assert the EXISTING gate honors FR8 — they do NOT modify the gate or the ledger), making FR8 a
named regression that fails loudly if a future author ever lets a non-deep state into the numerator.

**AC3 — Criticality is assessed by file CONTENT, not filename — anti-gaming (FR4-support, hostile-repo robustness)**
**Given** a file whose path/name does NOT advertise criticality (e.g. a security-critical module renamed to
`utils_misc.py`) but whose CONTENT carries criticality signals (auth/crypto/governance/secret-handling/
policy/permission tokens, imports, or AST shapes)
**When** `assess_criticality(...)` runs in `ledger/depth_semantics.py`
**Then** it derives a criticality signal from the file's CONTENT (token/import/structure signals over the
source text and/or the 1.4 AST entry) — NOT from the filename alone — so renaming a critical file to a benign
name does NOT hide its criticality (coverage-gaming-by-renaming is defeated, the PRD §hostile-repo +
§risk-mitigation requirement: "criticality detected by content, not filename")
**And** `assess_criticality` is a PURE function (no I/O — it takes the already-read source text and/or the AST
entry as in-memory arguments; the file READ is the impure caller's job, AR8), is deterministic, returns a
fixed-precision / enum / bool signal (NEVER a `float` score — AR4), and is unit-tested with at least: a
content-critical-but-benign-named file (flagged critical), a benign file (not flagged), and a
**non-ASCII path + non-ASCII-identifier file** (AI-E1-1 — correctly classified, not silently dropped)
**And** the V1 boundary is documented: `assess_criticality` produces the criticality ASSESSMENT only; the
operator DESIGNATION/override and the `RELEASE_READY`-withheld-when-a-critical-subsystem-is-below-deep GATE
CLAUSE are Story 2.3 (which consumes this function) — this story does NOT add the gate clause or the
invocation flag (the 1.6 `critical_subsystems_all_deep` seam stays defaulted-True until 2.3 wires it).

**AC4 — The depth-semantics module is PURE, frozen-contract, and import-isolated (NFR-D2, AR8, AR10, M2)**
**Given** `ledger/depth_semantics.py`
**When** it is imported and exercised in unit tests
**Then** it performs NO filesystem I/O, NO clock read (`datetime.now`/`time.time`), NO `uuid4`/`os.getpid()`/
`random`, NO LLM/network call, NO dict/`set`-iteration-order reliance — it is a pure classifier + pure
criticality assessor over in-memory inputs (the impure file READ is the caller's; this module never opens a
file)
**And** any model/result it defines is a frozen Pydantic v2 model (`frozen=True, extra="forbid"` — the
1.1/1.2 precedent) with a localized `schema_version` constant (additive-only, NFR-M2); any score/ratio field
is `Decimal`/`Fraction`/`int`/`bool`/enum, NEVER `float` (AR4)
**And** a malformed/empty evidence descriptor raises a typed error (a `ValueError` subclass localized to the
module, mirroring `RecordingValidationError`) — never a silent coerce / bare `except: pass` / `print()` in
library code (AR10)
**And** `minions_core.apaa.ledger.depth_semantics` is appended to `_MODULES_UNDER_GUARD` in
`tests/apaa/test_no_web_imports.py` (extend, do NOT fork) and importing it does NOT transitively import
`fastapi`/`uvicorn`/`starlette` (assert absence from `sys.modules`).

**AC5 — The whole APAA suite green; tests cover the semantics honestly; mypy clean; ≤1200 lines (NFR-M1)**
**Given** the module + tests added by this story
**When** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` runs
**Then** all pass, including new tests in `tests/apaa/test_depth_semantics.py`: the AC1 five-state
exhaustiveness pin (`classify_depth`/`DEPTH_SEMANTICS` covers every `CoverageDepth` member, no silent
default); the **MANDATORY AC2 FR8 synthetic-ledger proofs** (100%-`inferred` → `INSUFFICIENT_COVERAGE`;
`skipped`-only and `tool_scanned_only`-only never count toward the numerator; `inferred` cannot tip a sub-60%
ledger to `RELEASE_READY`); the AC3 criticality-by-content tests (benign-named-but-critical flagged;
benign not flagged; non-ASCII path/identifier correctly classified); the AC4 purity/frozen/no-`float`/typed-
error tests
**And** `ledger/depth_semantics.py` is appended to `_MODULES_UNDER_GUARD` and the import-isolation gate stays
green; the 1.1 single-serializer AST gate (`test_canonical_single_serializer.py`) still passes with the new
module present (no direct `json.dumps(` in the new module); the new source file is ≤1200 lines (NFR-M1) and
cites its `APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in the module docstring; `mypy` is clean on the new module.
The 1.2 enum + `grade_entry` and the 1.6 gate are UNCHANGED (this story adds a module + tests; it modifies
ONLY the import-isolation gate file).

## Tasks / Subtasks

- [x] **Task 0 — Verify the existing mechanism (verify-and-lock)** (AC: 1, 2)
  - [x] Re-read `ledger/coverage_ledger.py`: confirmed `CoverageDepth` (five members), `CoverageLedger.build`/
        `counts_by_depth`/`deep_count`/`total`, and `grade_entry` exist and need NO change. Left unmodified.
  - [x] Re-read `verdict/verdict_gate.py`: confirmed the deep-% numerator is `deep_count()` (audited_deep ONLY)
        and the floor/threshold logic already honors FR8. ASSERTED via named FR8 tests; gate UNCHANGED.
  - [x] Re-read `pipeline.py` grading note (no `tool_scanned_only`/`inferred` emitted yet). The pipeline loop
        is NOT rewired by this story.
- [x] **Task 1 — `ledger/depth_semantics.py`: documented five-state grading rule** (AC: 1, 4)
  - [x] Created `minions_core/apaa/ledger/depth_semantics.py` (docstring cites `APAA-FR-5`, `APAA-FR-8`,
        `APAA-FR-4`-support, `APAA-NFR-D2`, `APAA-NFR-M2`, `AR4`, `AR8`, `AR10`).
  - [x] Defined BOTH `DEPTH_SEMANTICS: dict[CoverageDepth, str]` (one grading-rule line per member) AND a pure
        `classify_depth(DepthEvidence) -> CoverageDepth` exhaustive over `EvidenceKind` (raises typed error,
        no silent default). Reuses the 1.2 enum verbatim; adds NO state.
  - [x] Localized `DEPTH_SEMANTICS_SCHEMA_VERSION = "1"`. No `float`; no I/O/clock/LLM (pinned by AST test).
- [x] **Task 2 — `assess_criticality(...)`: content-derived, anti-gaming** (AC: 3, 4)
  - [x] Implemented PURE `assess_criticality(*, file_path, source, ast_entry=None) -> Criticality` deriving
        criticality from locked CONTENT token signals over the in-memory source + the 1.4 AST entry's
        definition/edge names; filename is a weak hint, never the decision (documented).
  - [x] Returns the closed `Criticality{CRITICAL, NORMAL}` enum (never `float`, AR4); V1 boundary documented
        (assessment only; designation + gate clause are Story 2.3).
  - [x] Typed `DepthSemanticsError` (ValueError subclass) on a malformed/empty descriptor (AR10).
- [x] **Task 3 — Tests** (AC: 1, 2, 3, 4, 5)
  - [x] `tests/apaa/test_depth_semantics.py` (28 tests): AC1 exhaustiveness pin; **MANDATORY AC2 FR8 proofs**
        (100%-inferred → INSUFFICIENT_COVERAGE; skipped-only / tool_scanned_only-only never in the numerator;
        inferred cannot tip sub-60% to RELEASE_READY + the all-deep control); AC3 criticality-by-content
        (benign-named-critical flagged; benign + critical-named-benign not; **non-ASCII path + identifier**
        classified, AI-E1-1; AST def/edge signals); AC4 purity (AST scan) / frozen / no-`float` / typed-error.
  - [x] Non-ASCII + criticality fixtures inlined in the test module (no shared `tests/apaa/fixtures/` helper
        existed yet from 2.5/2.6; inlined per-test, AI-E1-1 covered).
- [x] **Task 4 — Extend the import-isolation gate** (AC: 4, 5)
  - [x] Appended `minions_core.apaa.ledger.depth_semantics` to `_MODULES_UNDER_GUARD` in
        `tests/apaa/test_no_web_imports.py` (extended, NOT forked). No web/LLM/api/writer leak.
- [x] **Task 5 — Run + mypy** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → 396 passed (the 1.1
        single-serializer AST gate + the extended no-web-imports gate re-ran green with the new module present).
  - [x] `mypy minions_core/apaa/ledger/depth_semantics.py` → Success: no issues found.

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **This is a complete-the-semantics + verify-and-lock story, not a net-new mechanism.** The five-state enum
  (1.2) and the FR8 gate-math (1.6) ALREADY EXIST and are correct. The net-new artifacts are: (a) the
  documented single-source grading-rule reference + pure classifier; (b) the content-derived criticality
  ASSESSMENT (anti-gaming); (c) the MANDATORY named FR8 regression tests proving the existing gate excludes
  `inferred`/`skipped`/`tool_scanned_only`. Resist the temptation to "improve" the 1.2 enum or the 1.6 gate —
  changing either is OUT of scope and would break the frozen contract.
- **FR8 is the central driver (evidence-poisoning defense).** `inferred` (narrative/doc) evidence can never
  satisfy a verdict gate. The 1.6 gate honors this by counting ONLY `audited_deep` in the deep-% numerator.
  This story makes that property an EXPLICIT, NAMED, mandatory regression test over synthetic ledgers — so a
  future detector that tries to let `inferred`/`tool_scanned_only` count toward coverage fails loudly. The
  test asserts the EXISTING gate; it does not re-derive coverage math.
- **Criticality by CONTENT, not filename (FR4-support, anti-gaming).** PRD §hostile-repo + §risk-mitigation:
  "criticality detected by content, not filename" defeats coverage-gaming-by-renaming. `assess_criticality`
  reads content/import/AST signals, never trusts the filename as the decision. This story builds the
  ASSESSMENT; Story 2.3 builds the operator designation + the gate clause that consumes it (the 1.6
  `critical_subsystems_all_deep` seam — defaulted-True until 2.3).
- **Pure/impure separation (master rule, AR8).** `ledger/depth_semantics.py` is PURE — no I/O, no clock, no
  LLM, no `uuid4`/`random`/`os.getpid()`. `assess_criticality` takes the already-read source text / AST entry
  as in-memory ARGUMENTS; the file READ is the impure caller's job (the pipeline / a future detector). ✅ a
  pure classifier over an in-memory descriptor · ❌ a function that opens a file or calls `datetime.now()`.
- **No floats — ever — in a `.apaa/`-bound output (AR4 / Determinism / NFR-P1).** A criticality SCORE is the
  obvious `float` trap — return a `bool` or a small frozen enum (recommended) or a `Fraction`/`Decimal`,
  NEVER a `float`. The 1.1 serializer rejects `float`. Counts are `int`.
- **One enum / one grading fn / one serializer (AR4, reuse-canonical, §3.3).** Reuse the 1.2 `CoverageDepth`
  + `grade_entry` + `CoverageLedger` and the 1.1 serializer verbatim. Do NOT define a parallel depth enum, a
  parallel grading function, or a second serializer. The committed `test_canonical_single_serializer.py` AST
  gate fails the build on a direct `json.dumps(`.
- **Error/degradation → typed, never crash (AR10, NFR-R1).** A malformed evidence/criticality descriptor →
  a typed `ValueError` subclass localized to the module (mirror `RecordingValidationError`). NO bare
  `except: pass`, NO `print()` in library code, NO silent coercion.
- **Headless / import boundary (§Architectural Boundaries, AR7/AR9).** APAA is downstream of the HTTP/A2A
  boundary — `ledger/depth_semantics.py` takes no token, registers no FastAPI route, imports no web stack,
  imports NO LLM. Never import `minions_core.api.* / services.api_app / app_factory / api_server /
  providers.* / apaa.audit.* / apaa.store.writer`. The new module joins `_MODULES_UNDER_GUARD`.

### The five-state grading rule (the AC1 reference — lock + document)

| state | earned when (V1 rule) | counts toward deep-% numerator? |
|---|---|---|
| `audited_deep` | an emitted deep claim is present (FR6 claim-presence; AST-truth grounding is Epic-6 6.2 / DF-1-7-B) | YES |
| `audited_shallow` | read/analyzed, no qualifying deep claim (silence → shallow, 1.2 `grade_entry`) OR a deep claim emitted-but-unverifiable (the 6.2 downgrade target — seam, not built here) | no |
| `tool_scanned_only` | covered ONLY by a zero-token breadth tool, never read for depth (Story 2.6 PRODUCES this; this story documents + classifies) | no |
| `inferred` | only evidence is narrative/doc (referencing requirement / comment / README), not a direct structural read — **the FR8 evidence-poisoning class** | **no (FR8)** |
| `skipped` | examined-but-ungradable / not examined (parse-failed, budget-skipped, non-analyzable) | no |

Only `audited_deep` is in the numerator (the 1.6 gate's `deep_count()`); every other state is denominator-
only. This table IS FR8 expressed as data.

### Decisions the dev must lock (record in the docstring + Change Log)

- **Grading-rule representation** — `DEPTH_SEMANTICS: dict[CoverageDepth, str]` description table (simplest,
  documents the rule as data) vs a `classify_depth(evidence_descriptor) -> CoverageDepth` pure classifier
  (richer — encodes the rule executably) vs both. Recommended: BOTH a `DEPTH_SEMANTICS` table (exhaustiveness-
  pinned) AND a `classify_depth` over a small frozen evidence descriptor, so later detectors can call it. Lock
  + document.
- **Criticality return type** — `bool` (simplest) vs a frozen `Criticality{CRITICAL, NORMAL}` enum
  (recommended — mirrors the 1.2 closed-enum precedent, extends additively if 2.3 wants tiers). NEVER `float`.
- **Criticality signal set** — the content token/import/AST signals (auth/crypto/governance/secret/policy/
  permission). Lock the V1 signal set + document that filename is at most a weak hint, never the decision.
- **Typed error type** — a `ValueError` subclass localized to `depth_semantics.py` (mirror
  `RecordingValidationError` / `CanonicalSerializationError`).
- **Where `assess_criticality` lives** — recommended `ledger/depth_semantics.py` (cohesive with the depth
  semantics it feeds, and the architecture places criticality/ledger logic in the ledger layer). Do NOT
  create a new top-level module if it fits here (NFR-M1 file-size permitting; the module will be small).

### Precedent inherited from Stories 1.1–1.6 (done) — honor these decisions

- **No second serializer / second enum / second grading fn.** Reuse 1.1 `canonical`, 1.2 `CoverageDepth` +
  `grade_entry` + `CoverageLedger`, 1.6 `evaluate_verdict`. The AST gate + the membership pin enforce it.
- **`depth_supported is not None` is the verdict-eligibility predicate (1.5/1.6 moat)** — unrelated to this
  story's depth-state classification, but do NOT conflate "depth a FINDING supports" (the moat) with "depth a
  FILE is graded" (this story). They are distinct fields; keep them separate.
- **Frozen `extra="forbid"` models** (1.1 `Envelope`, 1.2 `Recording`/`CoverageLedger`): any model this story
  adds follows the same pattern.
- **`Fraction`/`Decimal`/`int`/`bool`/enum over `float`** — the criticality signal is non-`float`.
- **Closed enum + membership/exhaustiveness pin (1.2 `CoverageDepth` / 1.6 `Verdict` precedent)** — the
  `classify_depth`/`DEPTH_SEMANTICS` coverage of all five members is pinned by a committed test.
- **`apaa_version`/`schema_version` single source** — `minions_core/apaa/__init__.py::__version__`
  (`"0.1.0"`); per-module `schema_version` is a localized constant (`DEPTH_SEMANTICS_SCHEMA_VERSION`), never
  env/clock.
- **Test-area precedent** — use area `APAA-LEDGER` for this story's test ids
  (`TC-APAA-LEDGER-001-NN`, continuing the 1.2 ledger area), consistent with the 1.x convention.
- **Import-isolation gate is seeded, extend it** — append the new module to `_MODULES_UNDER_GUARD`; do not
  fork.

### Source tree — files to create (the only UPDATE is the import-isolation gate)

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/ledger/depth_semantics.py` | NEW | FR5/FR8/FR4-support — documented five-state grading rule + pure `classify_depth`/`DEPTH_SEMANTICS` + content-derived `assess_criticality` (PURE) |
| `tests/apaa/test_depth_semantics.py` | NEW | five-state exhaustiveness pin; MANDATORY FR8 synthetic-ledger proofs; criticality-by-content (incl. non-ASCII); purity/frozen/no-float/typed-error |
| `tests/apaa/fixtures/` | NEW or REUSE | non-ASCII + criticality content fixtures (AI-E1-1) — reuse if 2.5/2.6 already created the helper |
| `tests/apaa/test_no_web_imports.py` | UPDATE | extend `_MODULES_UNDER_GUARD` with the new module |

The architecture's package tree places ledger/criticality logic under `ledger/`. Do NOT invent additional
modules; do NOT modify `ledger/coverage_ledger.py`, `ledger/recording.py`, `verdict/verdict_gate.py`, or
`pipeline.py` (this story is additive + a test-only change to the gate file). Resist building ahead.

### Scope fences (do NOT pull forward)

- ❌ The **readable per-file ledger render / counts % surface** (FR9) — Story 2.2. This story provides the
  semantics the surface references, not the render.
- ❌ The **critical-subsystem GATE CLAUSE + operator DESIGNATION / `--critical-subsystem` flag** (FR4 gate
  half) — Story 2.3. This story builds the content-derived `assess_criticality` ONLY; the 1.6
  `critical_subsystems_all_deep` seam stays defaulted-True until 2.3 wires it.
- ❌ **Repository partitioning into bounded units / work-manifest** (FR3) — Story 2.4.
- ❌ The **hardcoded-secret detector + producer-side redaction** (FR11/FR28) — Story 2.5.
- ❌ The **zero-token breadth tool runner** that PRODUCES `tool_scanned_only` grades + tool-failure-as-finding
  (FR14) — Story 2.6. This story documents/classifies the `tool_scanned_only` state; it does NOT run
  `cloc`/`radon`/linters.
- ❌ **Full FR7 AST-truth grounding** of `audited_deep` (downgrade an unverifiable claim) — Epic-6 Story 6.2
  (DF-1-7-B). V1 stays claim-presence per the Epic-1 cut-order; note the limitation, do NOT close it here.
- ❌ Any change to the **1.6 verdict thresholds** or the **1.2 enum / `grade_entry`** — both are frozen
  contracts. This story ASSERTS them (FR8 tests) and references them; it does not modify them.
- ❌ Re-wiring the **pipeline per-file grading loop** — incrementally completed by 2.5/2.6 as detectors land.

### Testing standards

- pytest under `tests/apaa/`; test ids follow `TC-<AREA>-<SEQ>-<SUBSEQ>` — use area `APAA-LEDGER` (e.g.
  `TC-APAA-LEDGER-001-NN`), continuing the 1.2 ledger area.
- These are **pure-function / synthetic-ledger tests** — zero LLM tokens (NFR-D2), no temp dirs for the module
  under test. Build synthetic ledgers via `CoverageLedger.build([grade_entry(file_path=..., proposed_depth=
  CoverageDepth.INFERRED, claim_present=False), ...])` and run them through the 1.6 `evaluate_verdict` to
  prove FR8.
- **The FR8 `inferred`-never-satisfies tests are MANDATORY** (the central driver / evidence-poisoning defense)
  — a 100%-`inferred` ledger → `INSUFFICIENT_COVERAGE`; `skipped`-only and `tool_scanned_only`-only never in
  the numerator; `inferred` cannot tip a sub-60%-deep ledger to `RELEASE_READY`.
- **The criticality tests MUST include a non-ASCII path + non-ASCII-identifier fixture** (AI-E1-1 — the
  Epic-1 retro action item: the content classifier must not silently drop non-ASCII input).
- On Windows, prefix runs with `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on cp1252).
- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` (the WHOLE
  `tests/apaa/` suite, so the 1.1 single-serializer AST gate + the extended no-web-imports gate re-run with
  the new module present). All must pass before moving to `review`.
- `mypy` clean on the new module (`python run_mypy_per_file.py` or a scoped invocation).

### CLAUDE.md §4a follow-up

The §4a APAA Component→Driver row was added by Story 1.1. This story does NOT need a new §4a row; if a
one-line additive note is added it must note `ledger/depth_semantics.py` as the five-state grading-rule
reference + content-derived criticality (FR5/FR8/FR4-support) and must NOT rewrite the existing row. Keep it
minimal — a new row is not required.

### Project Structure Notes

- Alignment: the new module lives under `ledger/` (cohesive with the 1.2 coverage ledger it semantically
  completes; the architecture places ledger/criticality logic in the ledger layer). Naming `snake_case.py`,
  ≤1200 lines (NFR-M1). Enum/JSON values `snake_case`.
- No conflicts/variances. Judgment calls — all decided above and to be documented so they freeze for
  downstream: the grading-rule representation (table + classifier), the criticality return type + signal set,
  the typed-error type, and the module placement.
- Scope fence: this story delivers the documented five-state grading rule + pure classifier + content-derived
  criticality assessment + the mandatory FR8 proof tests ONLY. The readable surface (2.2), the
  critical-subsystem gate clause / designation (2.3), partitioning (2.4), the secret detector (2.5), the
  breadth tool runner that produces `tool_scanned_only` (2.6), full AST grounding (6.2), and any change to the
  1.2 enum / 1.6 gate are explicitly NOT in scope. Verify-and-lock + complete the semantics, then stop.

### References

- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Story-2.1 Complete depth-state semantics + `inferred`-never-satisfies-a-gate] (the three ACs: five-state grading; inferred-never-satisfies; criticality by content)
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#FR5 fixed-enum coverage ledger / FR8 inferred-never-satisfies / FR4 critical-subsystem identification]
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#Hostile / low-quality-repo robustness] ("Coverage gaming (criticality detected by content, not filename) and evidence poisoning (inferred narrative can never satisfy a verdict gate)")
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#risk-mitigation] ("Hostile repo → content-based criticality + inferred-never-satisfies-a-gate")
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Contract / Format Patterns] (coverage-ledger enum is closed: audited_deep · audited_shallow · tool_scanned_only · inferred · skipped; additive-only)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Pure/Impure Separation (master rule)] (ledger modules pure — no I/O, no clock, no LLM)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Determinism Patterns] (one serializer; no floats — ratios fixed-precision; no iteration-order reliance)
- [Source: _bmad-output/design-artifacts/ArgusAgent/epic-1-retro-2026-06-21.md#7. Action Items] (AI-E1-1 adversarial non-ASCII fixtures; AI-E1-4 gates extended-not-forked; AI-E1-5 exercise the L1-E11 loop)
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-2-fixed-enum-coverage-ledger-frozen-recording-schema.md] (DONE — `CoverageDepth` five-member closed enum + `CoverageLedger`/`grade_entry`; closed-enum membership pin; frozen `extra="forbid"`; no-float)
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-6-pure-function-verdict-gate-finding-ordering-exit-code-mapping.md] (DONE — `evaluate_verdict`; FR8 honored by the deep-% numerator = audited_deep only; the `critical_subsystems_all_deep` Story-2.3 seam)
- [Source: minions_core/apaa/ledger/coverage_ledger.py] (`CoverageDepth`, `CoverageLedger.build`/`counts_by_depth`/`deep_count`/`total`, `grade_entry` — REUSE verbatim, do NOT modify)
- [Source: minions_core/apaa/verdict/verdict_gate.py] (`evaluate_verdict`, deep-% numerator = `deep_count()`; `critical_subsystems_all_deep` seam — ASSERT FR8, do NOT modify)
- [Source: minions_core/apaa/pipeline.py] (`_detect_per_file`/`_grade_non_test_python` — current coarse grading; NOT rewired here)
- [Source: minions_core/apaa/__init__.py] (`__version__ = "0.1.0"` — single apaa_version source)
- [Source: CLAUDE.md §3.2 file-size / §3.7 headless-only / §3.8 12-Factor + secret masking / §9.1 L1-E11 retro-action-items loop]

## Senior Developer Review (AI)

**Reviewer:** Claude (BMAD code-review gate, adversarial). **Date:** 2026-06-21. **Iteration:** 1.
**Outcome: PASS** → status `done`.

### Verdict rationale

A clean, correctly-scoped verify-and-lock + complete-the-semantics story. The five-state grading
rule is documented once (`DEPTH_SEMANTICS` table + the exhaustive pure `classify_depth`), the
content-derived `assess_criticality` defeats rename-gaming in the load-bearing direction, and the
**mandatory FR8 proofs are genuine** — they assert the REAL Story-1.6 gate, not a reimplementation.
ACs 1–5 all met; tests green; mypy clean; ≤1200 lines; headless/pure/import-isolated.

### What was verified (adversarially)

- **FR8 inferred-never-satisfies (the core invariant) — PROVEN, not promised.** The five named
  synthetic-ledger tests (TC-APAA-LEDGER-001-97..101) build ledgers via the REAL
  `CoverageLedger.build([grade_entry(...)])` and run them through the REAL
  `verdict.verdict_gate.evaluate_verdict` — confirmed by import inspection, not a fork. A
  100%-`inferred` ledger → `INSUFFICIENT_COVERAGE` (0% deep); `skipped`-only and
  `tool_scanned_only`-only never enter the numerator; the keystone "10 deep + 7 inferred = 10/17 =
  58.8% < 60% → NOT_READY_FOR_RELEASE" proves `inferred` only inflates the DENOMINATOR; the 17/17 →
  `RELEASE_READY` control proves numerator sensitivity from the other side. `grade_entry`'s
  `AUDITED_DEEP`-only downgrade is exercised correctly (inferred specs stay inferred).
- **1.2 enum / `grade_entry` / 1.6 gate are UNCHANGED.** `git status` shows
  `coverage_ledger.py` and `verdict_gate.py` are untracked pre-existing Epic-1 modules with no diff;
  the only edits this story makes are the additive new module + new test + the extend-not-fork append
  to `_MODULES_UNDER_GUARD` (test-only). The §3.3 single-enum / single-gate / single-serializer
  invariants hold; no direct `json.dumps(` in the new module (1.1 AST gate green).
- **`assess_criticality` anti-gaming.** A security module renamed `utils_misc.py` with auth/secret/
  hmac content → `CRITICAL` (rename-gaming defeated); a critical-SOUNDING name `auth_guard.py` with
  arithmetic body → `NORMAL` (filename is a weak hint, not the decision); AST def/edge-callee names
  also carry the signal. The Unicode `casefold` path is correct: `auth/café_guard.py` with
  `vérifier_permission`/`charger_credential`/`autorisé` → `CRITICAL` (non-ASCII not dropped, AI-E1-1).
- **Determinism / purity / contracts.** Pure (no clock/uuid/random/I/O — pinned mechanically by the
  AST-scan test TC-117); exhaustive `classify_depth` raises the localized `DepthSemanticsError`
  (ValueError subclass) on an unmappable/non-descriptor input (AR10); `Criticality` is a closed enum,
  never a `float` (AR4); `DepthEvidence` is `frozen=True, extra="forbid"`; AST-index import is
  `TYPE_CHECKING`-only so the no-web/zero-token isolation holds (subprocess gate green).
- **Suite:** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` →
  **396 passed**. `mypy minions_core/apaa/ledger/depth_semantics.py` → Success. Module = 337 lines.

### Action Items

- **[Low / non-blocking]** `assess_criticality` matches the locked tokens as **bare substrings** over
  the whole casefolded source, so benign code is over-flagged `CRITICAL`: a `tokenize` import / a
  `tokens` parameter (substring of `token`), or a "retry policy" comment (substring of `policy`)
  all read `CRITICAL`. This does NOT violate AC3 and the error direction is the SAFE one for an
  assurance gate (an over-flagged file gets MORE scrutiny, never less — the rename-gaming
  no-false-negative property is the load-bearing half and is satisfied), and Story 2.3's operator
  designation/override is the documented seam to correct a misclassification. Suggested future
  hardening (defer to 2.3 or a 2.x precision pass, not required for `done`): tighten matching to
  identifier-boundary / dotted-reference / import-name signals (or word-boundary `token`/`policy`)
  rather than raw substrings, to cut V1 false positives. No fix required to close this story.

## Dev Agent Record

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, mode=implement).

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/test_depth_semantics.py -q` → 28 passed.
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → 396 passed in ~8.8s
  (the 1.1 single-serializer AST gate `test_canonical_single_serializer.py` + the extended no-web-imports
  gate `test_no_web_imports.py` re-ran green with the new module present).
- `mypy minions_core/apaa/ledger/depth_semantics.py` → Success: no issues found.
- `wc -l` on the new module → 337 lines (≤1200, NFR-M1).

### Completion Notes List

**Decisions LOCKED (frozen for downstream — recorded in the module docstring):**
- **Grading-rule representation = BOTH** a `DEPTH_SEMANTICS: dict[CoverageDepth, str]` description table
  (rule-as-data, exhaustiveness-pinned) AND a pure `classify_depth(DepthEvidence) -> CoverageDepth` that
  encodes the rule executably (exhaustive over a closed `EvidenceKind` input enum; a `DEEP_READ` disambiguates
  on `claim_present` per the 1.2 grade_entry rule). Reuses the 1.2 `CoverageDepth` verbatim — NO new state, NO
  enum edit, does NOT re-implement `grade_entry`.
- **Criticality return type = closed `Criticality{CRITICAL, NORMAL}` enum** (mirrors the 1.2/1.6 closed-enum
  precedent; extends additively for Story 2.3 tiers). NEVER a `float` score (AR4 — the obvious float trap).
- **Criticality signal set (V1, LOCKED)** = a tuple of lower-cased content tokens (auth/crypto/encrypt/secret/
  credential/password/token/signature/hmac/governance/policy/permission/authoriz/privilege) matched
  case-insensitively + **Unicode-aware via `str.casefold`** over the source text + the 1.4 AST entry's
  definition/edge-callee names. Filename is a weak hint, NEVER the decision (proven by a `auth_guard.py`-with-
  benign-content → NORMAL test).
- **Typed error = `DepthSemanticsError`**, a `ValueError` subclass localized to the module (mirrors
  `RecordingValidationError` / `CanonicalSerializationError`).
- **Module placement = `ledger/depth_semantics.py`** (cohesive with the 1.2 ledger it completes).

**FR8 (the central driver) — proven, not promised.** Five named synthetic-ledger regression tests assert the
EXISTING 1.6 `evaluate_verdict` honors FR8 (the gate is NOT modified): 100%-`inferred` → INSUFFICIENT_COVERAGE;
`skipped`-only and `tool_scanned_only`-only never enter the numerator; 10×`audited_deep` + 7×`inferred`
(10/17 ≈ 58.8% < 60%) → NOT_READY_FOR_RELEASE (`inferred` cannot tip it over the line — it inflates the
denominator only); plus an all-`audited_deep` 17/17 = 100% → RELEASE_READY control proving numerator
sensitivity. If a future detector ever lets a non-deep state into the numerator, these fail loudly.

**Epic-1 retro carry-forward discharged (CLAUDE.md §9.1 / L1-E11):**
- **AI-E1-1** (non-ASCII/locale fixtures) — `assess_criticality` is content-touching, so its tests include a
  non-ASCII path + non-ASCII-identifier fixture (`auth/café_guard.py` with `vérifier_permission` /
  `charger_credential` / `autorisé`) classified CRITICAL (not silently dropped) plus a benign non-ASCII
  control (NORMAL). `str.casefold` is the Unicode-aware matcher.
- **AI-E1-4** (gates extended-not-forked) — appended the new module to `_MODULES_UNDER_GUARD` (no fork); the
  single-serializer AST gate and the no-web-imports/zero-token gates stay green.
- **AI-E1-5** (exercise the L1-E11 loop) — this record references the AI-E1-* items it discharges.

**Scope fences honored.** No readable surface (2.2), no critical-subsystem gate clause/operator designation
(2.3 — `assess_criticality` is the ASSESSMENT only; the 1.6 `critical_subsystems_all_deep` seam stays
defaulted-True), no partitioning (2.4), no secret detector (2.5), no breadth tool runner (2.6 — the
`tool_scanned_only` state is documented/classified, not produced), no FR7 AST-truth grounding (6.2 / DF-1-7-B).
The 1.2 enum + `grade_entry` and the 1.6 gate are UNCHANGED; the only non-additive edit is the test-only
import-isolation gate file. Module is PURE (no I/O/clock/uuid/random/LLM — pinned by an AST scan test) and the
AST-index import is typing-only (`TYPE_CHECKING`) so the no-web/zero-token isolation holds.

### Change Log

| Date | Change |
|---|---|
| 2026-06-21 | Implemented story 2.1 — added pure `ledger/depth_semantics.py` (documented five-state grading rule `DEPTH_SEMANTICS` + pure `classify_depth`/`DepthEvidence`/`EvidenceKind` + content-derived `assess_criticality`/`Criticality` anti-gaming, FR8/FR5/FR4-support); added `tests/apaa/test_depth_semantics.py` (28 tests incl. the mandatory FR8 synthetic-ledger proofs + non-ASCII AI-E1-1 fixtures); extended `_MODULES_UNDER_GUARD` in `test_no_web_imports.py`. 396 passed, mypy clean. Status → review. |

### File List

- `minions_core/apaa/ledger/depth_semantics.py` (NEW)
- `tests/apaa/test_depth_semantics.py` (NEW)
- `tests/apaa/test_no_web_imports.py` (UPDATE — extended `_MODULES_UNDER_GUARD`)
- `_bmad-output/design-artifacts/ArgusAgent/stories/2-1-complete-depth-state-semantics-inferred-never-satisfies-a-gate.md` (story file — status, tasks, Dev Agent Record, Change Log)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (status → review)
