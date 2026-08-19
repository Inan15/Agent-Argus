# Story 1.5: Heuristic vacuous-test detector + Tier-A vacuous-path AST subset

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
I want APAA to flag tests that appear vacuous — advisory-framed, carrying their evidence counts, and
corroborated by a minimal AST subset before they can ever move the verdict,
so that a passing-but-meaningless test is surfaced without crying wolf — the FIFTH link in the Epic-1 spine
and the LAST detector-side story before the pure verdict gate (1.6) and the CLI/pipeline (1.7).

## Story Context

This is **Story 5 of Epic 1** (Signature-Demo Vertical Slice). It is the `D` half of the architecture's
locked implementation sequence — *"envelope + canonical serializer + fixed-enum ledger (C-core) → **AST index
+ a single vacuous-path rule (B + D)** → pure-function verdict + exit code (C + A) → 🔴 on the cartridge"*
(architecture §Decision Impact Analysis). Stories 1.1–1.3 delivered **C-core**; Story 1.4 delivered the **B**
half (repo intake + stack detection + the tree-sitter Python AST index). **This story delivers the detector
`D`** — the heuristic vacuous-test detector PLUS the Tier-A "vacuous-path AST subset" — folding over the 1.4
AST index and emitting into the 1.2 recording/finding schema. The pure verdict gate (1.6) and the
CLI/pipeline that wires the whole slice + produces the signature 🔴 on the cartridge (1.7) come next; **this
story emits findings but computes no verdict and runs no pipeline.**

It builds directly on the five done stories of the spine:

- **Story 1.1 (done)** — the PURE determinism keystone (`store/canonical.py` single serializer:
  `dumps`/`dumps_bytes`/`loads` + `CanonicalSerializationError`; `store/envelope.py`: `Envelope`,
  `EnvelopeWriter.build`, `compute_content_hash`, `GENESIS_PREV_HASH`).
- **Story 1.2 (done)** — the PURE fixed-enum coverage ledger (`ledger/coverage_ledger.py`: `CoverageDepth`,
  `CoverageLedgerEntry`, `CoverageLedger`, `grade_entry`) and the frozen recording schema
  (`ledger/recording.py`: `Locator`, `Recording`, `RecordingValidationError`, `RECORDING_SCHEMA_VERSION`).
  **`Recording` is THE finding row this story emits** — it already reserves `recording_id`/`finding_id`,
  `rule_id`, `cartridge_id`, `advisory: bool`, `locators: tuple[Locator, ...]` (≥1 enforced),
  `depth_supported`, `claim_present`, `coverage_envelope_slice`. `Locator` already reserves `ast_span`.
- **Story 1.3 (done)** — the IMPURE `.apaa/` write/read shell (`store/paths.py` `ApaaStorePaths`
  containment resolver + the fixed `.apaa/` tree; `store/writer.py` content-addressed byte writer;
  `store/reader.py` PURE deserialize/validate + `StoreIntegrityError`).
- **Story 1.4 (done)** — the tree-sitter Python AST index (`index/ast_index.py`: `build_ast_index`,
  `AstIndex`, `AstIndexEntry` with `ast_eligible`/`parse_failed`/`parse_failure_reason`, `Definition` with
  `.ast_span` token `"<kind>:<name>@<start>-<end>"`, `CodeEdge(callee, line)`, `grammar_version`). **This is
  the AST substrate this story folds over** — the index entry definitions + edges + `ast_eligible` flag are
  exactly the structural facts the Tier-A vacuous-path subset reads. NOTE the locked 1.4 limitation
  (DF-1-4-A): `CodeEdge` is unresolved-name only (the bare callee identifier / trailing attribute, no scope
  binding) — this story's AST reachability check works ON THAT unresolved edge set and must be honest about
  its precision (see Dev Notes "The Tier-A AST subset — exactly what it can and cannot prove").

**Why this is the credibility keystone (architecture §Resolved Decisions / FR7-SPLIT, R1 first-principles,
cross-cutting #6).** A *truthful* "vacuous" assertion requires two AST facts — (a) the test body reaches the
SUT, and (b) asserted values derive from the SUT's output (not mocks/constants); **assertion-density alone is
neither necessary nor sufficient** (it false-positives on table-driven / snapshot / parametrized tests). The
signature-demo line `🔴 tests *appear* vacuous` is **advisory** and CAN be produced by the FR10 heuristic
alone (Tier-A) — but a *credible, non-cry-wolf* verdict-moving 🔴 needs the AST facts. The architecture's
locked decision is therefore: **carve a minimal "vacuous-path AST subset" (test-body reachability +
assertion-target provenance, test files only) into Tier-A; leave general multi-construct AST-grounding
Tier-B (Story 6.2).** This story implements exactly that split. **Heuristic-only findings are
advisory-by-contract**: a heuristic vacuous finding can never move the verdict to 🔴 on its own — it requires
AST corroboration AND (Epic-6) Prosecutor sign-off. A wrong 🔴 is the lethal failure (the false-accusation
moat); this contract is the moat.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 1.5) and the architecture (Decision D §Defect Detectors,
> §Resolved Decisions FR7-SPLIT, §Contract/Format Patterns finding-shape, §Pure/Impure Separation,
> §Error/Degradation Patterns, §Security/Containment, AR4/AR8/AR10). Drivers: **APAA-FR-10** (heuristic
> vacuous-test detector, advisory, evidence-carrying), **APAA-FR-7-subset** (the Tier-A vacuous-path AST
> subset: test→SUT reachability + assertion-target provenance — the carved-into-Tier-A half of FR7; full
> multi-construct AST grounding is Story 6.2), **APAA-FR-13** (locator-required findings or reject),
> **APAA-FR-33-support** / cross-cutting #6 (advisory-by-contract: no verdict-moving 🔴 on the heuristic
> alone), **APAA-NFR-D2** (deterministic, zero-LLM-token detector core — pure scorers over recorded inputs),
> **APAA-NFR-R1** (parse/analysis failure degrades to a recorded condition, never an uncaught raise),
> **AR4** (single canonical serializer; ratios stored fixed-precision `Decimal`/`Fraction`, NEVER `float`;
> no clock/uuid/random/iteration-order in any `.apaa/` write path), **AR8** (pure/impure separation — the
> detector *scorer* is PURE; only the optional `.apaa/findings/` write touches I/O via the 1.3 shell),
> **AR10** (typed/recorded failure, no bare `except: pass`, no `print()` in library code),
> **APAA-NFR-S5** (any `.apaa/` write through the 1.3 containment shell), **APAA-NFR-M1** (≤1200-line files).
>
> **SCOPE FENCE.** This story delivers ONLY: `detectors/base.py` (the detector `Protocol` + the
> locator-required `Recording`-finding builder, FR13), `detectors/vacuous_test.py` (the heuristic
> assertion-density + mock-ratio scorer AND the Tier-A vacuous-path AST subset over the 1.4 index), and the
> advisory-by-contract eligibility flag a finding carries so a downstream verdict gate (1.6) can honor "no
> 🔴 on the heuristic alone". It does NOT build: the pure verdict gate / finding ordering / exit codes
> (`verdict/*`, Story 1.6), the CLI / pipeline wiring or the cartridge run (`cli.py`/`pipeline.py`/
> `tests/apaa/cartridges/`, Story 1.7), the secret detector (`detectors/secret_scan.py`, Story 2.5), the
> zero-token breadth TOOL RUNNER (`detectors/tool_runner.py`, Story 2.6), the orphan/dead-code detector
> (`detectors/orphan_code.py`, Epic 6), the LLM dispatch port / deep-audit (`audit/*`, Epic 6), the FULL
> multi-construct AST grounding of `audited_deep` claims (Story 6.2), the adversarial Prosecutor / sign-off
> (`verdict/prosecutor.py`, Epic 6), the cache / memo store (`cache/*`, Epic 5), and the
> cartridge-self-audit harness / holdout / clean controls (Story 6.5). Build the detector + AST subset
> complete-and-contained, then stop.

**AC1 — Heuristic vacuous score: assertion-density + mock-ratio, fixed-precision (FR10, AR4)**
**Given** a Python test file's source + its 1.4 `AstIndexEntry` (definitions + edges)
**When** the heuristic scorer in `detectors/vacuous_test.py` runs
**Then** it computes, per test function, an **assertion-density** (assertion sites ÷ test-body statements
or test-body lines — the dev locks the exact denominator and documents it) and a **mock-ratio** (mock/patch
construction sites ÷ call sites), and BOTH ratios are stored as **fixed-precision `Decimal`/`Fraction`,
NEVER `float`** (the NFR-P1 byte-diff landmine — the Story 1.1 serializer REJECTS `float`)
**And** a test that scores below a documented assertion-density threshold OR above a documented mock-ratio
threshold is FLAGGED as heuristically-vacuous — but the flag alone produces only an **advisory** finding
(see AC3), never a bare accusation; the computed counts/ratios travel WITH the finding as evidence (FR10
"carrying their evidence counts").

**AC2 — Tier-A vacuous-path AST subset: reachability + assertion-target provenance (FR7-subset)**
**Given** a heuristically-flagged test function
**When** the Tier-A vacuous-path AST subset analyzes it over the 1.4 AST index
**Then** it checks the TWO AST facts that make "vacuous" *truthful*, test files only: **(a)** the test body
**reaches the SUT** (a call/reference edge from the test function's span resolves to a non-test, non-mock,
non-stdlib-assertion callee — using the 1.4 `CodeEdge` unresolved-name edge set + definition spans), and
**(b)** the **asserted values derive from the SUT's output** (an assertion's compared value is bound to /
flows from the SUT-call result, NOT a mock return / literal constant) — and BOTH AST facts being present
(test reaches SUT) AND the vacuity signal (assertions do not derive from SUT output) is what makes the
finding **AST-corroborated** and therefore *eligible* to move the verdict
**And** the subset operates ONLY on the unresolved 1.4 edge set + definition spans (it does NOT do name
binding / scope resolution — that is Epic-6 depth, DF-1-4-A), so its corroboration is **conservative**: when
the unresolved edge set cannot establish reachability the finding stays **heuristic-only / advisory** (it
does NOT fabricate corroboration) — documented honestly in Dev Notes.

**AC3 — Advisory-by-contract: no verdict-moving 🔴 on the heuristic alone (cross-cutting #6, FR33-support)**
**Given** a heuristically-flagged test with NO AST corroboration (AC2 facts absent or not establishable)
**When** its `Recording` finding is built
**Then** the finding is `advisory=True` and carries an eligibility marker (e.g. `depth_supported=None` and a
documented `verdict_eligible: false`-equivalent surfaced in the finding/`rule_id` contract) such that a
downstream verdict gate (1.6) **cannot move the verdict to 🔴 on it alone** — the heuristic-only finding is
informational
**And** a finding WITH AC2 AST corroboration is built so the verdict gate (1.6) MAY treat it as
verdict-eligible — BUT the architecture's full contract ("AST corroboration AND Prosecutor sign-off") means
the Prosecutor sign-off half is Epic-6; in V1/Epic-1 the AST-corroborated finding is the strongest the
detector emits and the cartridge 🔴 (Story 1.7) rests on it (the demo line is `🔴 tests *appear* vacuous`,
advisory framing preserved). Document the V1 boundary: detector-side eligibility is delivered here; the
verdict gate's consumption of it is Story 1.6; Prosecutor sign-off is Epic-6.

**AC4 — Every finding carries a locator or is rejected, not emitted (FR13, via the 1.2 schema)**
**Given** a vacuous-test finding
**When** it is built by `detectors/base.py`'s finding builder
**Then** it is a 1.2 `Recording` carrying a stable `recording_id`/`finding_id`, ≥1 verifiable `Locator`
(the flagged test's `file_path` + 1-based line span AND, where available, the `Definition.ast_span` token
from the 1.4 index dropped into `Locator.ast_span`), a `rule_id` (e.g. `"vacuous_test_heuristic"` /
`"vacuous_test_ast"` — dev locks the rule-id vocabulary), an optional `cartridge_id`, `advisory: bool`, and
the `coverage_envelope_slice` reference — REUSING the 1.2 `Recording`/`Locator` models VERBATIM (do NOT
define a parallel finding model; do NOT modify the 1.2 schema)
**And** a finding that cannot supply ≥1 locator is **rejected, not emitted** — enforced by the 1.2
`Recording`'s existing `RecordingValidationError` on an empty `locators` tuple; the detector builder must
surface a rejection (raise / skip-with-recorded-reason) rather than mint a locator-less finding (FR13).

**AC5 — Vacuous finding pairs with an `audited_shallow` coverage grade (FR10, 1.2 reuse)**
**Given** a flagged test file
**When** the detector records its coverage outcome
**Then** the test file is graded `audited_shallow` (the heuristic examined it but did not deeply ground it),
produced via the 1.2 `grade_entry(...)` PURE constructor (REUSE — do NOT re-implement grading); the detector
does NOT mint `audited_deep` (deep grounding is Epic-6) — so the FR10 "advisory `audited_shallow` finding
carrying the counts" contract holds
**And** the detector does NOT itself assemble the whole `CoverageLedger` (that aggregation is the pipeline's
job, Story 1.7) — it returns per-file entries + findings the pipeline folds; the detector's output shape is a
frozen pure result (dev's choice, documented) the 1.7 pipeline consumes.

**AC6 — The detector scorer is PURE; zero LLM tokens; no float/clock/uuid/random (NFR-D2, AR8, AR4)**
**Given** the scorer + AST-subset logic
**When** it is exercised in unit tests
**Then** it performs NO LLM/network call (zero tokens — NFR-D2), NO clock read, NO `uuid4`/`os.getpid()`/
`random`, NO `float` field on any emitted model (ratios `Decimal`/`Fraction`, counts/lines `int` — AR4), and
NO dict/`set`-iteration-order reliance in any `.apaa/`-bound output (AR4) — it is a pure function over
(source text + the 1.4 `AstIndexEntry`)
**And** the `detectors/` modules do NOT import `minions_core.api.* / services.api_app / app_factory /
api_server / providers.*` (no LLM in V1 detectors), do NOT import the web stack, and confine any I/O (the
optional `.apaa/findings/` persistence) to a clearly impure boundary that routes through the 1.3
`store/writer.py` + `store/paths.py` containment shell (no second serializer, no direct `open(...,'w')` into
`.apaa/` — AR4/NFR-S5).

**AC7 — Parse/analysis failure degrades to a recorded condition, never an uncaught raise (AR10, NFR-R1)**
**Given** a test file the 1.4 index marked `parse_failed=True` / `ast_eligible=False`, or a file the AST
subset cannot analyze (no resolvable test functions, a malformed body)
**When** the detector runs over it
**Then** it degrades to a recorded outcome — the file is NOT flagged as vacuous on un-analyzable input (no
false accusation on un-parseable code), the condition is captured as a per-file degraded result (so a later
story can mint a `parse_failure`-style finding / coverage downgrade), the run CONTINUES, and NO uncaught
raise escapes the detector, NO bare `except: pass`, NO `print()` in library code, NO fabricated successful
analysis (AR10)
**And** a non-test file (the detector only runs on test files in V1 — see Dev Notes on test-file
identification) is skipped cleanly, not mis-flagged.

**AC8 — `.apaa/findings/` persistence (if done now) is envelope-wrapped + content-addressed (AR4/AR11/FR25)**
**Given** a finding-set the pipeline will later re-read (resumability seam)
**When** it is persisted to `.apaa/findings/` (this story MAY persist via the 1.3 shell; if the dev defers
the WRITE to Story 1.7's pipeline, document the deferral and skip this AC's write half — the pure detector +
the 1.2 `Recording` model are the deliverable either way)
**Then** the write goes through `EnvelopeWriter.build` + `store/canonical.dumps_bytes` + the
`ApaaStorePaths`-resolved, content-addressed (`<content_hash>.json`) path under `.apaa/findings/` — REUSING
the 1.1/1.3 spine with NO second serializer and NO arrival-order/`uuid4`/clock filename
**And** re-reading via `store/reader.py` reconstructs an equal `Recording` and round-trips byte-identically
(NFR-P1), mirroring the 1.3/1.4 round-trip golden pattern.

**AC9 — Import-isolation gate extended + green; single-serializer AST gate still green (AR7/AR9)**
**Given** the new `detectors/` modules
**When** the `tests/apaa/` suite runs
**Then** `tests/apaa/test_no_web_imports.py`'s `_MODULES_UNDER_GUARD` tuple is EXTENDED with the new modules
(`minions_core.apaa.detectors.base`, `minions_core.apaa.detectors.vacuous_test`, + any new sibling) and the
gate stays green — importing them does NOT transitively pull `fastapi`/`uvicorn`/`starlette` (do NOT fork the
gate)
**And** the Story 1.1 single-serializer AST gate (`tests/apaa/test_canonical_single_serializer.py`) still
passes with the new modules present (no direct `json.dumps(` in any new module).

**AC10 — The whole APAA suite green; tests cover both layers honestly (NFR-M1, test infra)**
**Given** the modules + tests added by this story
**When** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` runs
**Then** all pass, including new tests: `tests/apaa/test_vacuous_detector.py` (heuristic score on a
fixture-vacuous test vs. a genuine test; fixed-precision ratio invariant / zero-`float`; advisory-only
heuristic finding; AST-corroborated eligible finding; un-parseable/un-analyzable degrades, no false flag;
locator-or-reject) and `tests/apaa/test_detector_base.py` (the finding builder mints a valid `Recording`,
rejects a locator-less finding) — using small in-repo fixture test sources (a deliberately vacuous test and
a genuine one). Tree-sitter-dependent assertions follow the 1.4 strategy (the `[apaa]` extra is installed in
dev/CI — `pip install -e ".[apaa]"`; OR `pytest.importorskip` the tree-sitter-dependent assertions — pick
one, document it; the pure heuristic-over-given-counts logic stays unconditionally tested)
**And** every new source file is ≤1200 lines (NFR-M1) and cites its `APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in
the module docstring; `mypy` is clean on the new modules; the false-accusation guard is explicitly tested (a
genuine, well-asserting test is NOT flagged; a clean/non-test file is NOT flagged).

## Tasks / Subtasks

- [x] **Task 0 — Confirm the spine + extra are present** (AC: all)
  - [x] Confirm the `[apaa]` extra is installed (`pip install -e ".[apaa]"`) so `tree-sitter`/
        `tree-sitter-python` resolve (the 1.4 index is imported); record the resolved versions if not already
        recorded by 1.4 (grammar version is an Epic-5 cache-key input — AR5).
  - [x] Confirm the done spine is present: `store/canonical.py`, `store/envelope.py`, `ledger/recording.py`
        (`Recording`/`Locator`/`RecordingValidationError`), `ledger/coverage_ledger.py` (`grade_entry`),
        `store/paths.py`/`writer.py`/`reader.py`, `index/ast_index.py` (`build_ast_index`/`AstIndexEntry`/
        `Definition`/`CodeEdge`).
- [x] **Task 1 — `detectors/` sub-package + the detector base (Protocol + finding builder)** (AC: 3, 4, 6)
  - [x] Create `minions_core/apaa/detectors/__init__.py` (sub-package shell, docstring) + `detectors/base.py`
        (docstring cites `APAA-FR-13`, `AR8`, `AR10`, cross-cutting #6).
  - [x] Define the detector `Protocol` (a `typing.Protocol` — e.g. `run(...) -> DetectorResult`) and a PURE
        finding builder that mints a 1.2 `Recording` from (file_path, line span, optional `ast_span`, rule_id,
        advisory, counts/evidence, coverage_envelope_slice) — REUSING `Recording`/`Locator`; surfaces the
        FR13 locator-or-reject (raise/skip-with-reason on a locator-less finding, never mint one).
  - [x] Decide + document the detector result shape (a frozen pure model: per-file `CoverageLedgerEntry`
        candidates via `grade_entry` + the `Recording` findings); do NOT assemble the whole `CoverageLedger`
        (Story 1.7 pipeline).
- [x] **Task 2 — Heuristic vacuous score (assertion-density + mock-ratio, fixed-precision)** (AC: 1, 5, 6, 7)
  - [x] Create `detectors/vacuous_test.py` (docstring cites `APAA-FR-10`, `APAA-FR-7`-subset, `APAA-NFR-D2`,
        `AR4`, `AR8`, `AR10`, cross-cutting #6).
  - [x] Identify test functions in a test file (document the rule — e.g. `test_*` functions / `Test*` class
        methods; test-file identification: path under `tests/` or `*_test.py`/`test_*.py` — lock + document).
  - [x] Compute per-test `assertion_density` + `mock_ratio` as `Decimal`/`Fraction` (NEVER `float`); apply
        documented thresholds to FLAG. Pure over (source + the 1.4 `AstIndexEntry`); zero tokens.
  - [x] Grade the flagged test file `audited_shallow` via `grade_entry(...)` (REUSE); carry the counts as
        finding evidence (FR10). Un-parseable / non-test / un-analyzable → recorded degraded, NOT flagged (AC7).
- [x] **Task 3 — Tier-A vacuous-path AST subset (reachability + assertion-target provenance)** (AC: 2, 3)
  - [x] Over the 1.4 index for the flagged test: check (a) test-body → SUT reachability (a `CodeEdge` from the
        test function span resolves to a non-test/non-mock/non-assertion callee) and (b) asserted values
        derive from the SUT result (the asserted value is bound to the SUT-call result, not a mock/constant).
  - [x] Operate ONLY on the unresolved 1.4 edge set + definition spans (NO name binding/scope — DF-1-4-A);
        when corroboration cannot be established, leave the finding heuristic-only/advisory (do NOT fabricate).
  - [x] Set the finding's advisory-by-contract eligibility: heuristic-only → `advisory=True`,
        verdict-ineligible; AST-corroborated → eligible (the verdict gate's consumption is Story 1.6;
        Prosecutor sign-off is Epic-6). Document the V1 boundary in the docstring + Dev Notes.
- [x] **Task 4 — (Optional) persist findings via the 1.3 store shell** (AC: 8)
  - [x] If persisting now: wrap the finding set via `EnvelopeWriter.build` + `store/writer.py`
        (content-addressed `<content_hash>.json` under `.apaa/findings/`, containment-checked); round-trip via
        `store/reader.py`. If deferring to Story 1.7, document the deferral in Dev Notes and skip.
- [x] **Task 5 — Tests** (AC: 1, 2, 3, 4, 5, 6, 7, 9, 10)
  - [x] `tests/apaa/test_detector_base.py` — the finding builder mints a valid `Recording`; a locator-less
        finding is rejected (FR13); the Protocol contract holds.
  - [x] `tests/apaa/test_vacuous_detector.py` — fixture deliberately-vacuous test → flagged + advisory finding
        with counts; AST-corroborated case → eligible finding; **a genuine well-asserting test → NOT flagged**
        (false-accusation guard); a non-test/clean file → NOT flagged; an un-parseable test → degraded, no
        flag, no crash; fixed-precision ratio / zero-`float` invariant; `audited_shallow` grade via `grade_entry`.
  - [x] (If Task 4 done) `tests/apaa/test_findings_roundtrip.py` — envelope-wrapped write → read → equal
        `Recording` + byte-identical re-serialize (NFR-P1).
- [x] **Task 6 — Extend the import-isolation gate** (AC: 9)
  - [x] Append the new `detectors/*` modules to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py`
        (do NOT fork the gate). Confirm no web-stack leak.
- [x] **Task 7 — Run + mypy** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass (the 1.1
        single-serializer AST gate + the extended no-web-imports gate re-run with the new modules present).
  - [x] `mypy` clean on the new modules (`python run_mypy_per_file.py` or scoped).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **Pure/impure separation (master rule, AR8).** The detector **scorer** is PURE — a pure function over
  (test source text + the 1.4 `AstIndexEntry`) → flags + counts + findings. The architecture explicitly
  lists "detector *scorers*" among the pure modules. The ONLY impure boundary in this story is the OPTIONAL
  `.apaa/findings/` persistence (Task 4), which routes through the 1.3 `store/writer.py` shell. ✅ a pure
  `score(source, ast_entry) -> VacuousScore` · ❌ a scorer that reads a file or calls `dispatch()`.
- **Advisory-by-contract (cross-cutting #6 — THE keystone of this story).** A heuristic vacuous finding
  CANNOT move the verdict to 🔴 on its own. The detector emits an eligibility signal: heuristic-only →
  `advisory=True`, verdict-ineligible; AST-corroborated → eligible. The architecture's full rule is "AST
  corroboration AND Prosecutor sign-off" — the Prosecutor half is Epic-6, so in V1 the AST-corroborated
  finding is the strongest the detector produces and the Story-1.7 cartridge 🔴 rests on it. A wrong 🔴 is
  the lethal failure — be conservative.
- **The FR7 split (architecture §Resolved Decisions, R1).** Tier-A here = the "vacuous-path AST subset"
  (test→SUT reachability + assertion-target provenance, **test files only**). General multi-construct
  AST-grounding of `audited_deep` claims is Tier-B (Story 6.2). Do NOT pull Story 6.2's full grounding
  forward; build exactly the two-fact subset.
- **No floats — ever — in a `.apaa/`-bound model (AR4 / Determinism / R4 red-team).** Assertion-density +
  mock-ratio are RATIOS — the obvious `float` trap. Store them as `Decimal` or `Fraction`. The Story 1.1
  serializer REJECTS `float` with `CanonicalSerializationError`; a `float` field would explode at serialize
  time. `Decimal` → `format(d.normalize(),'f')` and `Fraction` → `"num/den"` are already frozen by 1.1 —
  inherited automatically through `canonical.dumps`.
- **One serializer / one finding model / one grader (AR4, reuse-canonical, §3.3).** The finding row is the
  1.2 `Recording` — do NOT define a parallel finding model. The coverage grade is `grade_entry` — do NOT
  re-implement grading. Any `.apaa/` bytes go through `store/canonical.dumps_bytes` via `store/writer.py` —
  the committed `test_canonical_single_serializer.py` AST gate fails the build on a direct `json.dumps(`.
- **Locator-or-reject is already enforced at the data layer (FR13, 1.2).** The 1.2 `Recording` raises
  `RecordingValidationError` on an empty `locators` tuple. The detector builder must SURFACE that (raise or
  skip-with-recorded-reason), never try to mint a locator-less finding. Every finding cites the test's
  `file_path` + line span and, where available, the `Definition.ast_span` token from the 1.4 index.
- **Containment for any `.apaa/` write (NFR-S5, reuse Story 1.3).** Any persistence goes through
  `ApaaStorePaths` + `store/writer.py` (`Path.resolve()` + `is_relative_to`, never `str.startswith`). Do NOT
  write a second containment path; do NOT `open(...)` into `.apaa/` directly.
- **No source bytes in findings (NFR-S1 / producer-side redaction, cross-cutting #5).** A finding cites
  LOCATIONS (file + line span + ast_span) + COUNTS — never excerpts of the test source. (This detector reads
  test code, not secrets, but the producer-side discipline is uniform: cite, do not quote.)
- **Error/degradation → recorded, never crash (AR10, NFR-R1).** An un-parseable test (1.4
  `parse_failed=True`), a non-test file, or a body the subset cannot analyze → a recorded degraded outcome
  and NO false flag — the run continues. NO bare `except: pass`, NO `print()` in library code, NO fabricated
  analysis.
- **Headless / import boundary (§Architectural Boundaries, AR7/AR9).** APAA is downstream of the HTTP/A2A
  boundary — these modules take no token, register no FastAPI route, import no web stack, and import NO LLM
  in V1 (the detector is zero-token). Never import `minions_core.api.* / services.api_app / app_factory /
  api_server`. The new modules join `_MODULES_UNDER_GUARD`.

### The Tier-A AST subset — exactly what it can and cannot prove (honest scope)

The 1.4 index gives an UNRESOLVED edge set: `CodeEdge(callee, line)` is the bare callee identifier or
trailing attribute name, with **no scope binding / name resolution** (the locked 1.4 limitation DF-1-4-A,
target `epic-6-orphan-dead-code-detector`). The Tier-A subset therefore works on NAME-level structural
facts, not a resolved call graph:

- **Reachability (fact a)** — a `CodeEdge` whose `line` falls inside the flagged test function's
  `Definition` span and whose `callee` is NOT a known assertion primitive (`assert*`, `assertEqual`, …) and
  NOT an obvious mock constructor (`Mock`, `MagicMock`, `patch`, …) is treated as a candidate SUT call. This
  is **conservative**: a SUT reached only via an aliased / dynamically-dispatched name may be MISSED (a false
  negative — acceptable; we under-claim corroboration rather than over-accuse).
- **Assertion-target provenance (fact b)** — the V1 heuristic for "asserted value derives from the SUT
  output" is name-level: the value compared in an assertion shares a binding with a SUT-call result on the
  same span, vs. a mock-return / literal. Because there is no dataflow analysis, this is **best-effort**;
  when it cannot be established the finding stays heuristic-only/advisory (do NOT fabricate corroboration).
- **The conservative default is the moat.** When the unresolved edge set is insufficient, the finding does
  NOT gain verdict-eligibility — it remains advisory. False negatives (a real vacuous test left advisory) are
  tolerable; a false 🔴 is not. Document this explicitly in the `vacuous_test.py` docstring so 1.6/Epic-6
  consumers know the corroboration's strength. Full dataflow/scope-resolved grounding is Story 6.2.

### Precedent inherited from Stories 1.1–1.4 (done) — honor these decisions

- **No second serializer / reuse the 1.1 spine.** `store/canonical.py` + `store/envelope.py` are the only
  serializer + envelope; reuse for any persistence + goldens. The AST gate enforces it.
- **The finding row IS the 1.2 `Recording`.** It already reserves `recording_id`/`finding_id`, `rule_id`,
  `cartridge_id`, `advisory`, `locators` (≥1, `RecordingValidationError` on empty), `depth_supported`,
  `claim_present`, `coverage_envelope_slice`. Reuse it VERBATIM; do NOT modify `ledger/recording.py`.
- **The coverage grade IS `grade_entry`.** Grade the flagged file `audited_shallow` via the 1.2 pure
  constructor; do NOT re-implement grading and do NOT mint `audited_deep`.
- **`Locator.ast_span` is reserved + the 1.4 index produces the token.** `Definition.ast_span` renders
  `"<kind>:<name>@<start>-<end>"` — drop it straight into `Locator.ast_span`. Do NOT modify `Locator`.
- **Frozen `extra="forbid"` models** (1.1 `Envelope`, 1.2 `Recording`/`Locator`, 1.4 `AstIndex*`): any NEW
  detector result/score model follows the SAME pattern (`frozen=True, extra="forbid"`).
- **`partition_id` is always `"root"` in V1.** Partitioning is Story 2.4 — operate on the single `"root"`
  partition; do NOT build the partitioner.
- **`apaa_version`/`schema_version` single source** — `minions_core/apaa/__init__.py::__version__`
  (`"0.1.0"`) via `EnvelopeWriter`; per-model `schema_version` is a module constant, never env/clock.
- **Test-area precedent** — use area `APAA-DETECT` for this story's test ids (`TC-APAA-DETECT-001-NN`),
  consistent with the 1.x convention (`APAA-STORE`, `APAA-LEDGER`, `APAA-INTAKE`, `APAA-INDEX`).
- **Import-isolation gate is seeded, extend it** — append the new modules to `_MODULES_UNDER_GUARD`; do not
  fork.

### Source tree — files to create (all NEW; the only UPDATE is the import-isolation gate)

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/detectors/__init__.py` | NEW | `detectors/` sub-package shell (docstring) |
| `minions_core/apaa/detectors/base.py` | NEW | FR13 — detector `Protocol` + locator-required `Recording`-finding builder (PURE) |
| `minions_core/apaa/detectors/vacuous_test.py` | NEW | FR10 + FR7-subset — heuristic (advisory) scorer + Tier-A vacuous-path AST subset (PURE) |
| `tests/apaa/test_detector_base.py` | NEW | finding builder mints valid `Recording`; locator-or-reject |
| `tests/apaa/test_vacuous_detector.py` | NEW | heuristic flag + advisory; AST-corroborated eligible; false-accusation guard; degrade; fixed-precision |
| `tests/apaa/test_findings_roundtrip.py` | NEW (only if Task 4 persists) | envelope round-trip byte-stability |
| `tests/apaa/test_no_web_imports.py` | UPDATE | extend `_MODULES_UNDER_GUARD` with the new modules |

The architecture's package tree (`architecture.md` §Project Structure) places EXACTLY `detectors/base.py`,
`detectors/vacuous_test.py`, `detectors/secret_scan.py`, `detectors/orphan_code.py`, `detectors/tool_runner.py`
in this sub-package. **`secret_scan.py` is Story 2.5, `tool_runner.py` is Story 2.6, `orphan_code.py` is
Epic-6** — do NOT build them here. Do not invent additional modules; the verdict gate is `verdict/` (1.6),
the CLI/pipeline are `cli.py`/`pipeline.py` (1.7), the LLM seam is `audit/` (Epic 6). Resist building ahead.

### Determinism / contract decisions the dev must lock (record the choice in the docstring)

- **Test-function + test-file identification** — what counts as a test (`test_*` funcs / `Test*` methods) and
  a test file (path under `tests/` / `*_test.py` / `test_*.py`). Lock + document; the detector runs on test
  files only in V1.
- **Assertion-density denominator + thresholds** — assertion sites ÷ (statements | lines); the
  assertion-density floor + mock-ratio ceiling that FLAG. Document the values + that they are heuristic (FP on
  table-driven/snapshot is the known cost — the AST subset is the corroboration that protects the moat).
- **Ratio type** — `Decimal` vs `Fraction` (either is fine; both serialize through the 1.1-frozen encoding).
  NEVER `float`.
- **`rule_id` vocabulary** — e.g. `"vacuous_test_heuristic"` (advisory-only) vs `"vacuous_test_ast"`
  (AST-corroborated, verdict-eligible), or a single rule with an eligibility field. Lock + document.
- **Verdict-eligibility surface** — how the finding tells the 1.6 gate "advisory-only, do not 🔴 on me"
  (e.g. `advisory=True` + `depth_supported=None`, or a documented marker). It must be expressible WITHIN the
  1.2 `Recording` fields (do NOT modify the schema); document the convention 1.6 will read.
- **Detector result shape** — the frozen pure result the 1.7 pipeline consumes (per-file
  `CoverageLedgerEntry` candidates + `Recording` findings + degraded-condition records). Lock + document.
- **Persist-now vs defer to 1.7** — whether findings are written to `.apaa/findings/` here (via the 1.3
  shell) or deferred to the 1.7 pipeline. If deferred, document it and skip AC8's write half.
- **Optional-dep test strategy** — `pip install -e ".[apaa]"` (preferred) vs `pytest.importorskip` for the
  tree-sitter-dependent assertions (mirror the 1.4 choice). Pick one, document it.

### Scope fences (do NOT pull forward)

- ❌ The pure-function **verdict gate** / finding ordering / exit codes (`verdict/verdict_gate.py`) — Story
  1.6. This story emits advisory-vs-eligible findings; it computes NO verdict.
- ❌ The **CLI / pipeline wiring** + the cartridge run + the signature 🔴 (`cli.py`/`pipeline.py`/
  `tests/apaa/cartridges/`) — Story 1.7.
- ❌ The **secret detector** (`detectors/secret_scan.py`) — Story 2.5. The **zero-token breadth tool runner**
  (`detectors/tool_runner.py`) — Story 2.6. The **orphan/dead-code detector** (`detectors/orphan_code.py`) —
  Epic 6.
- ❌ The **FULL multi-construct AST grounding** of `audited_deep` claims (`audit/deep_audit.py`, FR7 general)
  — Story 6.2. This story builds ONLY the test-files-only two-fact vacuous-path subset.
- ❌ The **adversarial Prosecutor** + sign-off (`verdict/prosecutor.py`) — Epic 6. V1 stops at detector-side
  AST corroboration; Prosecutor sign-off is the Epic-6 second half of the "🔴 needs AST + Prosecutor" rule.
- ❌ The **LLM dispatch port / adapter / deep-audit** (`audit/*`) — Epic 6. The detector is zero-token; no
  LLM import.
- ❌ The **cache / memo store** (`cache/key.py`, `cache/memo_store.py`) — Epic 5.
- ❌ The **cartridge self-audit harness** + holdout/clean controls (`tests/apaa/test_cartridge_selfaudit.py`)
  — Story 6.5. (This story's fixtures are inline unit fixtures, NOT the CI-asserted cartridge corpus.)

### Testing standards

- pytest under `tests/apaa/`; test ids follow `TC-<AREA>-<SEQ>-<SUBSEQ>` — use area `APAA-DETECT` (e.g.
  `TC-APAA-DETECT-001-80`), consistent with the 1.x convention.
- The scorer tests are PURE over (source text + a constructed/fixture `AstIndexEntry`) — prefer building the
  `AstIndexEntry` from a real tiny fixture `.py` via `build_ast_index` (so the test exercises the real 1.4
  substrate) OR constructing it directly for the pure-logic cases. Use `tmp_path` + small fixture sources for
  the build-index path.
- **The false-accusation guard is mandatory** (cross-cutting #6 / the lethal-failure moat): an explicit test
  that a genuine, well-asserting test is NOT flagged, and that a clean/non-test file is NOT flagged.
- `tree-sitter`/`tree-sitter-python` are optional-extra deps: install `[apaa]` in dev/CI (preferred) or
  `pytest.importorskip` the tree-sitter assertions (document the choice, mirror 1.4). The pure heuristic logic
  over given counts stays unconditionally tested.
- On Windows, prefix runs with `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on cp1252).
- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` (the WHOLE
  `tests/apaa/` suite, so the 1.1 single-serializer AST gate + the extended no-web-imports gate re-run with
  the new modules present). All must pass before moving to `review`.
- `mypy` clean on the new modules (`python run_mypy_per_file.py` or a scoped invocation).

### CLAUDE.md §4a follow-up

The §4a APAA Component→Driver row was already added by Story 1.1. This story does NOT need a new §4a row; if a
one-line additive note is added it must note `detectors/base.py` + `detectors/vacuous_test.py` as the
heuristic vacuous-test detector + Tier-A vacuous-path AST subset (FR10 + the FR7-subset, advisory-by-contract)
and must NOT rewrite the existing row. Keep it minimal — a new row is not required.

### Project Structure Notes

- Alignment: file paths exactly match `architecture.md` §Project Structure package tree
  (`detectors/base.py`, `detectors/vacuous_test.py`). `secret_scan.py`/`tool_runner.py`/`orphan_code.py` are
  deferred (2.5/2.6/Epic-6). Naming `snake_case.py`, ≤1200 lines (NFR-M1). JSON/enum values `snake_case`.
- No conflicts/variances. Judgment calls — all decided above and to be documented so they freeze for
  downstream: test identification, the assertion-density denominator + thresholds, the ratio type, the
  `rule_id` vocabulary + verdict-eligibility surface, the detector result shape, persist-now-vs-defer, and the
  optional-dep test strategy.
- Scope fence: this story delivers the heuristic vacuous-test detector + the Tier-A vacuous-path AST subset +
  the locator-required finding builder ONLY. Verdict (1.6), CLI/pipeline + cartridge (1.7), other detectors
  (2.5/2.6/Epic-6), full AST grounding (6.2), Prosecutor (Epic-6), cache (Epic-5) are explicitly NOT in scope.

### References

- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Story-1.5 Heuristic vacuous-test detector + Tier-A vacuous-path AST subset]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#D. Defect Detectors] (vacuous-test heuristic advisory `audited_shallow` + Tier-A vacuous-path AST subset; every finding carries finding_id + envelope slice + rule/cartridge id + AST span)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Resolved & Flagged Decisions — FR7 SPLIT] (two AST facts: test→SUT reachability + assertion-target provenance, test files only, carved into Tier-A; general AST grounding Tier-B)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Cross-Cutting Concerns #6 advisory-by-contract] (no verdict-moving 🔴 without AST corroboration AND Prosecutor sign-off; false-accusation moat)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Pure/Impure Separation (master rule)] (detector *scorers* are PURE; impure shell at the edges)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Determinism Patterns / Contract Format Patterns] (one serializer; no floats — ratios fixed-precision; finding shape; locator-or-reject)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Error / Degradation Patterns] (parse failure → recorded condition, never an uncaught raise; no bare except: pass / print())
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Project Structure & Boundaries] (package tree: detectors/base.py, detectors/vacuous_test.py; secret_scan/tool_runner/orphan_code deferred)
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#FR10 vacuous-test detection (advisory, evidence counts) / FR7 Python AST grounding (subset) / FR13 locator-or-reject / NFR-D2 zero-token / NFR-R1 honest degradation]
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-1-canonical-serializer-content-hashed-envelope.md] (DONE — serializer + envelope spine + `_MODULES_UNDER_GUARD` seed + single-serializer AST gate + Decimal/Fraction encoding)
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-2-fixed-enum-coverage-ledger-frozen-recording-schema.md] (DONE — `Recording`/`Locator`/`RecordingValidationError` = the finding row; `grade_entry`; `Locator.ast_span` reserved; frozen extra="forbid")
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-3-apaa-store-writer-reader-filesystem-containment.md] (DONE — `ApaaStorePaths` + writer/reader to REUSE for any `.apaa/findings/` persistence)
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-4-tree-sitter-ast-index-repo-intake-python-stack-detection.md] (DONE — `build_ast_index`/`AstIndexEntry`/`Definition.ast_span`/`CodeEdge` = the AST substrate; DF-1-4-A: edges are unresolved-name only — the conservative-corroboration constraint)
- [Source: minions_core/apaa/ledger/recording.py] (`Recording`/`Locator`/`RecordingValidationError` — the finding model to reuse verbatim)
- [Source: minions_core/apaa/ledger/coverage_ledger.py] (`grade_entry` — the `audited_shallow` grader to reuse)
- [Source: minions_core/apaa/index/ast_index.py] (`build_ast_index`, `AstIndexEntry`, `Definition`, `CodeEdge` — the AST facts the subset folds over)
- [Source: minions_core/apaa/store/canonical.py + store/envelope.py + store/paths.py + store/writer.py + store/reader.py] (the serializer/envelope/containment spine to reuse for any `.apaa/` write)
- [Source: minions_core/apaa/__init__.py] (`__version__ = "0.1.0"` — single apaa_version source)
- [Source: CLAUDE.md §3.2 file-size / §3.7 headless-only / §3.8 12-Factor + secret masking / §4a APAA row]

## Dev Agent Record

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, mode=implement)

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` — all pass
  (full APAA suite incl. the 1.1 single-serializer AST gate + the extended no-web-imports gate).
- `python -m mypy minions_core/apaa/detectors/base.py minions_core/apaa/detectors/vacuous_test.py` — clean.
- Two TDD red→green fixes during implementation: (1) `is_test_file` legitimately matches `*_test.py`
  basenames so the test was corrected to a non-`_test` SUT name (the `*_test.py` convention is the
  locked V1 rule, not a bug); (2) the vacuous fixtures were strengthened to actually trip a documented
  threshold (mock_ratio > 1/2 needs ≥2 mock sites vs 1 SUT call) — the original 1-mock fixtures scored
  1/2 (not strictly above the ceiling), which correctly did NOT flag (the moat working as designed).

### Completion Notes List

**Locked contract decisions (frozen for 1.6 / Epic-6 consumers — documented in the module docstrings):**
- **Test-file id (V1):** path under a `tests/` segment OR basename `test_*.py` / `*_test.py`. Detector
  runs on test files ONLY; a non-test file degrades `not_a_test_file` (not mis-flagged) — AC7.
- **Test-function id:** a `Definition` of kind `function` whose name starts with `test`.
- **Assertion-density denominator = test-body STATEMENTS** ~~(non-blank/non-comment body lines, def header
  excluded) — robust to multi-line statements~~ **— AMENDED 2026-08-17 by
  [sprint-change-proposal-2026-08-17.md](../sprint-change-proposal-2026-08-17.md) / Story 14.2.**
  The struck text is self-contradictory: a count of **LINES** is not *robust to multi-line statements* —
  it is the thing multi-line statements break. Measured against a true `ast`-module statement count over
  the 1,812 flagged tests in the `minions` corpus member at its pinned sha, the line count inflates the
  denominator **2.04×**, and correcting it alone lifts **14 of the 31** adjudicated false positives back
  above the `1/4` floor. **The decision was validly taken** — AC1 explicitly delegated the choice of
  denominator to the dev — **so it is amended on the record, not treated as a gap** (§3.4 evidence
  immutability: it was the state this story was written in). The denominator is now real statements;
  a multi-line statement counts **once**. Assertion sites = assertion-primitive call edges + bare
  `assert` statements counted from the source span (a bare `assert` is not a tree-sitter `call` node, so
  it is absent from the 1.4 edge set — counted deterministically from source lines).
  - **FIGURE CORRECTED 2026-08-18 by Story 14.2 (the story that implemented the amendment above).**
    The `2.04×` and `1,812` in the 2026-08-17 amendment are **superseded**; they are left standing
    rather than overwritten, for the same §3.4 reason the original text is struck rather than erased —
    a figure that was acted on is part of the record even once it is known to be wrong. **Re-measured
    by execution on `966ceba`**, through the shipped `build_ast_index` and `VacuousTestDetector`, over
    the `minions` member staged at its unchanged pinned sha `ec63b729`, against CPython's own `ast`
    module as ground truth (every `ast.stmt` in the function body, recursively): the flagged population
    is **1,848** tests, not 1,812, and the line count inflates the denominator **1.907×**
    (29,093 lines ÷ 15,255 statements), not 2.04×. The gap is not definitional — counting only
    TOP-LEVEL body statements gives 2.664×, so 2.04 is neither. **The defect was real and large and
    the amendment was right; only the multiplier was stale**, most likely carried from an earlier tree
    (Story 14.1 rewrote this detector on 2026-08-18). The corrected denominator measures **1.005×** of
    ground truth, exact on 1,784 of the 1,848 spans. The *"14 of the 31"* attribution above **does
    reproduce exactly** and is unchanged. Recorded here because this is where the number lives; the
    full re-measurement is `stories/14-2-…md` §0.2.
- **Thresholds (heuristic, documented as such):** FLAG when `assertion_density < 1/4` OR `mock_ratio > 1/2`.
- **Ratio type = `Fraction`** (exact, NEVER `float` — the 1.1 serializer rejects `float`). Proven by
  serializing the emitted finding payload through `canonical.dumps_bytes` (TC-APAA-DETECT-001-92).
- **rule_id vocabulary:** `"vacuous_test_heuristic"` (advisory-only, NOT verdict-eligible) vs
  `"vacuous_test_ast"` (AST-corroborated, verdict-eligible).
- **Verdict-eligibility surface (read by 1.6):** heuristic-only → `advisory=True` + `depth_supported=None`
  (the 1.6 gate MUST NOT 🔴 on it). AST-corroborated → `advisory=True` (demo line stays `🔴 tests *appear*
  vacuous`) + `depth_supported=AUDITED_SHALLOW` + `rule_id="vacuous_test_ast"` (the 1.6 gate MAY treat it
  as eligible). Expressed entirely WITHIN the 1.2 `Recording` fields — schema unmodified.
- **Detector result shape:** `DetectorResult(entries, findings, degraded)` — a frozen `extra="forbid"`
  pure model the 1.7 pipeline folds. The detector grades per-file via `grade_entry` (REUSE) and does NOT
  assemble the whole `CoverageLedger` (1.7's job).
- **recording_id = content-derived sha256** over the canonical draft identity via the single 1.1
  serializer (`<rule_id>:<sha>`) — NEVER `uuid4`/counter/arrival order (AR4/AR11); stable across re-flags.
- **Persist-now = DEFERRED to 1.7** for the live write call site; AC8's SEAM is proven (not deferred) by
  `test_findings_roundtrip.py` — a detector `Recording` round-trips byte-identically through the REUSED
  1.1/1.3 spine (`EnvelopeWriter` + `ApaaStoreWriter`/`ApaaStoreReader`, no second serializer).
- **Optional-dep strategy:** `pytest.importorskip("tree_sitter"/"tree_sitter_python")` for the
  integration cases (mirror 1.4); the pure heuristic-over-given-counts cases stay UNCONDITIONALLY tested
  (the `AstIndexEntry` is constructed directly).

**Tier-A AST subset — honest scope (DF-1-4-A conservative corroboration).** Works on the UNRESOLVED 1.4
edge set + definition spans (NO name binding / scope / dataflow — that is Story 6.2). Corroborates ONLY
when BOTH facts hold: (a) the test reaches a candidate SUT (≥1 non-assertion/non-mock call edge in the
span), AND (b) the vacuity signal (the test asserts yet is mock-dominated — `mock_sites ≥ 1` — so the
asserted values plausibly derive from a mock, not the SUT result). When (a) is un-establishable, the
finding stays heuristic-only/advisory — it does NOT fabricate corroboration. False negatives (a real
vacuous test left advisory) are tolerable; a false 🔴 is the lethal failure — the conservative default IS
the moat.

**False-accusation guard (MANDATORY) — tested for real:** a genuine well-asserting test is NOT flagged
(TC-APAA-DETECT-001-88, and the integration TC-APAA-DETECT-001-94 over the real 1.4 index); a clean
non-test file is NOT flagged (TC-APAA-DETECT-001-89). Un-parseable / no-test-function input degrades to a
recorded condition, never a flag/crash (TC-APAA-DETECT-001-90/91 — AR10).

**Scope fences honored:** NO verdict gate (1.6), NO CLI/pipeline/cartridge (1.7), NO secret/tool-runner/
orphan detectors (2.5/2.6/Epic-6), NO full multi-construct AST grounding (6.2), NO Prosecutor (Epic-6),
NO cache (Epic-5), NO LLM import (zero-token). The 1.2 `Recording`/`Locator` + `grade_entry` are reused
VERBATIM (no parallel finding model, no re-implemented grader, no schema change). New `detectors/*`
modules appended to `_MODULES_UNDER_GUARD` (gate green); the 1.1 single-serializer AST gate stays green
(no direct `json.dumps`). No new §4a row needed (the APAA row was added by 1.1).

### File List

- `minions_core/apaa/detectors/__init__.py` (NEW — sub-package shell)
- `minions_core/apaa/detectors/base.py` (NEW — detector `Protocol`, `FindingDraft`, `DegradedCondition`,
  `DetectorResult`, `build_recording` locator-or-reject builder)
- `minions_core/apaa/detectors/vacuous_test.py` (NEW — heuristic scorer + Tier-A vacuous-path AST subset)
- `tests/apaa/test_detector_base.py` (NEW)
- `tests/apaa/test_vacuous_detector.py` (NEW)
- `tests/apaa/test_findings_roundtrip.py` (NEW)
- `tests/apaa/test_no_web_imports.py` (UPDATED — `_MODULES_UNDER_GUARD` extended with the two new modules)

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-06-21 | 0.1.0 | Story drafted (create-story) — heuristic vacuous-test detector + Tier-A vacuous-path AST subset over the 1.4 AST index, emitting into the 1.2 `Recording`/`grade_entry` schema, advisory-by-contract. Status → ready-for-dev. | claude-opus-4-8 (Scrum Master) |
| 2026-06-21 | 0.2.0 | Implemented `detectors/base.py` (Protocol + locator-or-reject `Recording` builder, content-derived id) + `detectors/vacuous_test.py` (fixed-precision `Fraction` assertion-density + mock-ratio heuristic scorer + Tier-A two-fact AST subset, conservative corroboration over the unresolved 1.4 edge set). Advisory-by-contract eligibility surface (`vacuous_test_heuristic`/`advisory`/`depth_supported=None` vs `vacuous_test_ast`/`AUDITED_SHALLOW`). Reuses 1.2 `Recording`/`Locator`/`grade_entry` verbatim + 1.1/1.3 store spine (findings round-trip seam proven). MANDATORY false-accusation guard tested (genuine test + non-test file NOT flagged; un-parseable/no-test degrades, no crash). Import-isolation gate extended; 1.1 single-serializer gate green. Full `tests/apaa/` + `tests/test_import_paths.py` pass; mypy clean. Status → review. | claude-opus-4-8 (Developer) |
| 2026-06-21 | 0.3.0 | Code review (adversarial, iter-1): PASS. All 10 ACs met; advisory-by-contract / false-accusation moat verified non-bypassable; 307 passed, mypy clean. Status → done. | claude-opus-4-8 (Reviewer) |

## Senior Developer Review (AI)

**Reviewer:** claude-opus-4-8 (BMAD adversarial code-review gate)
**Date:** 2026-06-21
**Outcome:** PASS — status `review` → `done`.

### Scope reviewed

`minions_core/apaa/detectors/base.py`, `detectors/vacuous_test.py`, `detectors/__init__.py`,
and `tests/apaa/test_detector_base.py`, `test_vacuous_detector.py`, `test_findings_roundtrip.py`,
`test_no_web_imports.py` (extended). Three adversarial layers run: Blind Hunter (correctness/security),
Edge Case Hunter (boundary/branch), Acceptance Auditor (AC/spec conformance).

### Verification performed (independent)

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **307 passed** in 5.66s.
- `python -m mypy` on the three new modules → **clean** (no issues).
- Single-serializer AST gate (`test_canonical_single_serializer.py`) → green; its `rglob` scan covers the new
  `detectors/` tree, so AC9's "stays green with the new modules present" is independently confirmed.
- `grep` confirmed: no `json.dumps`/`import json`, no real `float` usage (docstrings only), no
  `time`/`random`/`uuid`/`getpid`/`datetime` imports in `detectors/`. Purity (AR8/AR4/NFR-D2) verified.
- Confirmed at runtime that `canonical.dumps(Fraction(1,4)) == '"1/4"'` and `canonical.dumps(0.25)` raises
  `CanonicalSerializationError` — so the AC1/AC6 fixed-precision/zero-float invariant has a real teeth.
- File sizes: 204 / 418 / 21 lines — all ≤1200 (NFR-M1).

### The keystone — advisory-by-contract / false-accusation moat (verified non-bypassable)

This was scrutinized hardest. Traced the only promotion path (`_ast_corroborated`, `vacuous_test.py:392-418`):
a finding can become verdict-eligible (`rule_id="vacuous_test_ast"` + `depth_supported=AUDITED_SHALLOW`)
ONLY when **all** of: (1) `heuristically_vacuous` is True; (2) `reaches_sut` — derived from a REAL non-assertion,
non-mock `CodeEdge` inside the test span (`_sut_call_sites`), never fabricated, never invented when the
unresolved DF-1-4-A edge set cannot establish it; AND (3) `vacuity_signal = assertion_sites >= 1 and
mock_sites >= 1`. The `rule_id`/`depth_supported` in `run` are bound strictly to `score.ast_corroborated`,
so a heuristic-only finding is provably `vacuous_test_heuristic` + `advisory=True` + `depth_supported=None` —
the 1.6 gate has no input to 🔴 on it. Corroboration cannot manufacture reachability: it counts only edges
the 1.4 index actually produced. The mandatory false-accusation guard tests are real and load-bearing — a
genuine well-asserting test (TC-88, and the real-index TC-94) and a clean non-test file (TC-89) are NOT
flagged; un-parseable / no-test-function inputs degrade to a recorded condition without flag or crash
(TC-90/91, AR10). The conservative default (false-negatives tolerable, no false 🔴) is implemented as the moat
the architecture demands.

### Reuse / determinism / standards

- Emits the 1.2 `Recording`/`Locator` schema VERBATIM (no parallel finding model; `ledger/recording.py`
  unmodified). Grades via `grade_entry` (no parallel grader; never mints `audited_deep`). Round-trip seam
  reuses the single 1.1 serializer + envelope + `ApaaStore*` (no second `json.dumps`).
- `recording_id` is content-derived sha256 over the canonical draft identity — no `uuid4`/counter/arrival
  order (AR4/AR11), stable across re-flags, distinct per finding (TC-80/81).
- All emitted models frozen `extra="forbid"` (TC-83). Detector satisfies the `Detector` Protocol (TC-84).
- Headless: new modules appended to `_MODULES_UNDER_GUARD`; no web/LLM/api imports (AC9, gate green).

### Findings

No High or Medium findings. Two Low / informational observations, NOT blocking and NOT requiring rework:

1. **[Low — accepted, documented Tier-A limitation]** Fact (b) is a name-level mock-domination proxy
   (`mock_sites >= 1`), not true dataflow provenance. A genuine test that mocks a dependency but asserts on the
   real SUT return and happens to trip the density floor could be AST-corroborated. This is explicitly in-scope
   per the story (conservative best-effort; full dataflow grounding is Story 6.2) and is mitigated by the
   finding remaining `advisory=True` plus the architecture's required Epic-6 Prosecutor sign-off before any
   real 🔴. No moat bypass. No action needed in V1.
2. **[Low — cleanliness]** `build_recording`'s `depth_supported: object | None` + `# type: ignore[arg-type]`
   (base.py:166,200) loosens typing to avoid importing `CoverageDepth` into `base`. mypy is clean and the call
   sites pass real `CoverageDepth | None`; acceptable. A future tightening to `CoverageDepth | None` (importing
   the enum, as `recording.py` already does) would remove the ignore. Optional.
