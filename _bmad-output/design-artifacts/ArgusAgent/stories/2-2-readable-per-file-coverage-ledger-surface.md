# Story 2.2: Readable per-file coverage-ledger surface

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As an Engineering Lead answering "how much did APAA actually look at?",
I want to read EXACTLY which files were examined deeply, shallowly, tool-scanned, inferred, or skipped — with
each file's depth state and the evidence/claim that justified it — plus the per-depth counts and percentages
(the deep-% "VP question") derivable directly from that data,
so that the coverage envelope is an inspectable, human/integrator-readable surface and never a black box —
the FR9 readability deliverable (the SECOND story of Epic 2), built as a PURE, deterministic, byte-stable
RENDERING function over the existing 1.2 ledger (NOT a UI; structured text/JSON/markdown for a CLI/integrator)
that carries NO source/secret bytes (NFR-S1 spirit).

## Story Context

This is **Story 2 of Epic 2** (Full Coverage Ledger & Defect Detectors). Story 2.1 (done) locked the
five-state SEMANTICS (`DEPTH_SEMANTICS` table + `classify_depth`) and content-derived `assess_criticality`,
and proved FR8 (`inferred` never satisfies a gate) over synthetic ledgers. This story delivers the **readable
SURFACE** of that ledger: a pure rendering function that turns the 1.2 `CoverageLedger` (per-file depth
states + justifying evidence) into a deterministic, byte-stable, human/integrator-readable artifact, and a
per-depth aggregate (counts + percentages — the deep-% the verdict gate uses, surfaced for the operator).

**What already exists (REUSE verbatim, do NOT rebuild).** The data this surface renders already exists from
Epic 1 + Story 2.1:

- **Story 1.2 (done) — `ledger/coverage_ledger.py`.** `CoverageLedger` (frozen, `entries` sorted by
  `file_path`), `CoverageLedgerEntry` (`file_path`, `depth: CoverageDepth`, `claim_present: bool`,
  `recording_ids: tuple[str, ...]`, `partition_id`), the closed five-member `CoverageDepth` enum, plus the
  PURE aggregate accessors `counts_by_depth() -> dict[CoverageDepth, int]` (zero-filled for EVERY member),
  `deep_count() -> int`, and `total() -> int`. **The data model is COMPLETE — this story does NOT add a field
  to it, does NOT modify it, and does NOT re-implement an accessor.** The render reads it.
- **Story 1.1 (done) — `store/canonical.py`.** THE single canonical serializer
  (`dumps`/`dumps_bytes`/`loads`/`canonicalize`, `sort_keys=True, separators=(",",":"), ensure_ascii=False`,
  `\n`-terminated UTF-8). `Fraction` → `"num/den"`; `Decimal` → plain decimal; `float`/`datetime`/`uuid`/`set`
  REJECTED with `CanonicalSerializationError`. **A JSON rendering of the surface MUST route through this
  serializer — never a second `json.dumps`** (the committed AST gate `test_canonical_single_serializer.py`
  fails the build on a direct `json.dumps(`).
- **Story 2.1 (done) — `ledger/depth_semantics.py`.** `DEPTH_SEMANTICS: dict[CoverageDepth, str]` (the
  one-line grading-rule description per state). The surface MAY reference this table for the per-state legend,
  but it is OPTIONAL context, not a required column.
- **Story 1.6 (done) — `verdict/verdict_gate.py`.** The verdict gate ALREADY surfaces the deep-% as the exact
  `Fraction` `deep_ratio` and `counts_by_depth` on `AuditVerdict`. This story does NOT change the gate; it
  renders the LEDGER side of the same data so an operator can read the coverage envelope WITHOUT needing the
  verdict. The deep-% computed by this surface MUST agree with the gate's `Fraction(deep_count, total)`
  (same exact-fraction arithmetic — reuse, do not re-derive a different formula).

**The net-new deliverable of THIS story.** A single PURE module — recommended `ledger/coverage_report.py`
(cohesive with the ledger layer it renders; the architecture maps FR9 to `ledger/`) — that provides:
1. a pure **per-file render** of the `CoverageLedger`: every entry with its `file_path`, its depth state, and
   the evidence/claim that justified it (`claim_present`, `recording_ids`), in deterministic
   (already-`file_path`-sorted) order;
2. a pure **aggregate** model: the per-depth counts (reusing `counts_by_depth()`) AND the deep-% as an exact
   `Fraction` (reusing the gate's `Fraction(deep_count, total)` arithmetic — `Fraction(0,1)` at `total==0`),
   plus a per-depth percentage as an exact `Fraction` (NEVER a `float` — AR4);
3. at least one **textual rendering** (structured plain-text or markdown table to stdout) AND a JSON rendering
   THROUGH the 1.1 canonical serializer, both deterministic + byte-stable + secret-free.

It imports ONLY the 1.2 ledger models + the 1.1 serializer (+ optionally the 2.1 `DEPTH_SEMANTICS` table for
the legend); it is PURE (AR8) and joins the import-isolation gate.

**Carry-forward from the Epic-1 retro (CLAUDE.md §9.1 / L1-E11 — this story discharges these items).**
- **AI-E1-1 (test-infra 🟠) — adversarial non-ASCII / locale fixtures.** This surface RENDERS file paths.
  Its tests MUST include a **non-ASCII `file_path` fixture** (e.g. `auth/café_guard.py`, `модуль/тест.py`)
  proving the path is rendered intact (not mojibake / not dropped) in BOTH the textual and the JSON rendering
  (the 1.1 serializer is `ensure_ascii=False`, so the UTF-8 path bytes must round-trip verbatim).
- **AI-E1-4 (process 🟢) — keep the committed gates extended-not-forked.** Append the new module to
  `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py` (do NOT fork the no-web-imports gate); keep
  the single-serializer AST gate (`test_canonical_single_serializer.py`) green (route any JSON through
  `store/canonical.dumps`, never a direct `json.dumps`).
- **AI-E1-5 (process 🟢) — exercise the L1-E11 loop.** This story explicitly references the AI-E1-* items it
  discharges (here).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 2.2) and the architecture / PRD. Drivers: **APAA-FR-9** (an
> operator can read exactly which files were examined deeply, shallowly, tool-scanned, inferred, or skipped —
> the central driver), **APAA-FR-5** (the fixed-enum coverage ledger this surface renders — five states, no
> sixth), **APAA-NFR-S1** (no source / secret / absolute-host-path bytes in the rendered surface — the surface
> carries file PATHS + depth states + counts only), **APAA-NFR-D2** (deterministic, zero-LLM-token — a pure
> render over recorded data), **APAA-NFR-P1** (byte-identical rendering across hosts/runs for the same
> ledger), **APAA-NFR-M2** (frozen, additive-only contracts), **APAA-NFR-M1** (≤1200-line files), **AR4** (no
> `float`; ratios are exact `Fraction`/`Decimal`; single canonical serializer; no clock/uuid/random/
> iteration-order in any rendered/`.apaa/`-bound output), **AR8** (pure module — no I/O, no clock, no LLM; the
> impure caller does the stdout write / `.apaa/` persist), **AR10** (typed failure, never an uncaught raise /
> silent coerce), **AR9** (headless / no web surface — a developer-readable text/JSON artifact, NOT a UI).
>
> **SCOPE FENCE — Tier-A, single-purpose.** This story delivers ONLY: (1) a PURE per-file render of the
> existing 1.2 `CoverageLedger` (each file + its depth state + the justifying evidence/claim) in deterministic
> order; (2) a PURE aggregate (per-depth counts reusing `counts_by_depth()` + the deep-% and per-depth
> percentages as exact `Fraction`s, reusing the gate's `Fraction(deep, total)` arithmetic); (3) ≥1 textual
> rendering + a JSON rendering THROUGH the 1.1 canonical serializer, both deterministic / byte-stable /
> secret-free. It does NOT build, and MUST NOT pull forward: the **critical-subsystem GATE CLAUSE + operator
> DESIGNATION / `--critical-subsystem` flag** (FR4 gate half — Story 2.3); **repository partitioning** (FR3 —
> Story 2.4); the **secret detector** (FR11 — Story 2.5); the **breadth tool runner** that actually PRODUCES
> `tool_scanned_only` grades (FR14 — Story 2.6 — this surface RENDERS the state if present, it does not
> produce it); the **evidence-bundle export** (FR29 — Epic 4 Story 4.3; this is the inspectable per-file
> ledger surface, NOT the regulator-grade bundle with scope statement + disclaimer); the **negative-assurance
> verdict semantics** (FR17 — Epic 4 Story 4.1); any change to the **1.2 ledger / enum / accessors**, the
> **1.6 verdict gate**, or the **1.1 serializer**. It does NOT add a NEW HTTP route, a FastAPI surface, or any
> UI (§3.7 — APAA is headless; this is a CLI/library text/JSON artifact). It does NOT necessarily wire the
> render into `pipeline.py`/`cli.py` (an OPTIONAL additive stdout/persist seam — see AC5 decision); the pure
> render + its tests are the required deliverable.

**AC1 — Every file is readable with its depth state + justifying evidence (FR9, FR5)**
**Given** a completed (or partial) `CoverageLedger` (1.2) with entries spanning multiple depth states
**When** the per-file surface is rendered by the new `ledger/coverage_report.py`
**Then** EVERY ledger entry appears in the rendering with at minimum its `file_path`, its `depth` state (one
of the five closed `CoverageDepth` values, rendered as the `snake_case` token), and the evidence/claim that
justified it — i.e. `claim_present` (the FR6 keystone field) AND the `recording_ids` evidence references
(empty tuple rendered as an empty/`[]` value, never omitted) — so a reader can see WHICH files were examined
at WHICH depth and WHY (FR9 "exactly which files were examined deeply, shallowly, tool-scanned, inferred, or
skipped, and the evidence that justified it")
**And** the per-file rows are in the ledger's deterministic (already-`file_path`-sorted) order — the render
introduces NO re-sort that diverges from `CoverageLedger.entries` order and relies on NO dict/set iteration
order (AR4); a ledger built from the same entries in any input order renders identically
**And** the render covers ALL five states correctly when present (a fixture ledger with one entry per state
renders all five with the correct token); an EMPTY ledger (`total()==0`) renders a well-formed empty surface
(header + zero counts), NOT a crash and NOT a divide-by-zero (the floor-vs-empty case the 1.6 gate also
guards).

**AC2 — Per-depth counts + percentages are derivable directly, as exact non-`float` ratios (FR9, AR4)**
**Given** a rendered ledger surface
**When** the aggregate section is produced
**Then** it carries the per-depth COUNTS (reusing `CoverageLedger.counts_by_depth()` — a count for EVERY one
of the five members, zero-filled, so the surface never silently omits a state) AND the deep-% (the "VP
question") computed as an EXACT `Fraction(deep_count, total)` — the SAME arithmetic the 1.6 gate uses
(`Fraction(0, 1)` when `total()==0`), so the surfaced deep-% AGREES with the verdict gate's `deep_ratio`
(reuse, do NOT re-derive a divergent formula), plus a per-depth percentage as an exact `Fraction` (count/total)
**And** EVERY ratio/percentage in the surface is an exact `Fraction` (or `Decimal`) — NEVER a `float` (the
1.1 serializer rejects `float`; AR4 — the byte-diff landmine); counts are `int`. A `Fraction` renders as its
canonical `"num/den"` form in JSON (the 1.1 frozen encoding) and as a documented human form in text (e.g.
`"3/5"` or a derived percentage string built from the exact fraction, never a binary `float` formatting)
**And** the aggregate is unit-tested for arithmetic correctness against a known fixture (e.g. 3 deep + 1
shallow + 1 inferred → deep-% `Fraction(3, 5)`; the gate's `evaluate_verdict(ledger).deep_ratio` equals the
surface's deep-% on the same ledger — a cross-check test pinning agreement).

**AC3 — The surface is secret-safe — paths + states + counts only, never source/secret bytes (NFR-S1)**
**Given** a `CoverageLedger` whose entries' `recording_ids` reference findings (which, in 2.5+, may concern
secret-bearing files)
**When** the surface is rendered (text AND JSON)
**Then** it contains ONLY the `file_path`, the depth token, `claim_present`, the `recording_ids`
(opaque id strings — NOT finding bodies / source excerpts / secret values), and the aggregate counts/
percentages — it NEVER reads or embeds file source bytes, secret values, or an absolute host path (the
`CoverageLedger` entries hold no source bytes by construction; the render must not introduce any) — the
NFR-S1 producer-side guarantee the Epic-4 containment property suite later enforces mechanically
**And** a test asserts the rendered text + JSON of a ledger with a representative `file_path` and
`recording_ids` contain the path + the id strings + the depth tokens + the counts, and contain NO substring
that is a file-content/secret canary planted only in a SEPARATE source string (i.e. the render never sources
file bytes — it operates purely on the in-memory ledger).

**AC4 — The render is PURE, frozen-contract, deterministic, byte-stable, and import-isolated (NFR-D2, NFR-P1, AR8, AR10, M2)**
**Given** `ledger/coverage_report.py`
**When** it is imported and exercised in unit tests
**Then** it performs NO filesystem I/O, NO clock read (`datetime.now`/`time.time`), NO `uuid4`/`os.getpid()`/
`random`, NO LLM/network call, NO dict/`set`-iteration-order reliance — it is a PURE render over the in-memory
1.2 `CoverageLedger` (the impure caller — `pipeline.py`/`cli.py` or a test — does any stdout write / `.apaa/`
persist; this module returns a string and/or a frozen model, it never `print()`s and never `open()`s)
**And** any model it defines (e.g. a `CoverageReport` / `DepthAggregate` aggregate model) is a frozen
Pydantic v2 model (`frozen=True, extra="forbid"` — the 1.1/1.2/2.1 precedent) with a localized
`schema_version` constant (additive-only, NFR-M2); any ratio field is `Fraction`/`Decimal`/`int`, NEVER
`float` (AR4)
**And** the JSON rendering routes THROUGH `store/canonical.dumps` (the single 1.1 serializer — no second
`json.dumps`, the AST gate enforces it); calling the render twice on the same ledger produces BYTE-IDENTICAL
output (NFR-P1 — pinned by a test that renders the same ledger twice and asserts equality, and renders two
ledgers built from the same entries in different input orders and asserts equality)
**And** a malformed input (a non-`CoverageLedger` argument, or a render-format selector outside the supported
set) raises a typed error — a `ValueError` subclass localized to the module (mirroring
`RecordingValidationError` / `CanonicalSerializationError` / `DepthSemanticsError`) — never a silent coerce /
bare `except: pass` / `print()` in library code (AR10)
**And** `minions_core.apaa.ledger.coverage_report` is appended to `_MODULES_UNDER_GUARD` in
`tests/apaa/test_no_web_imports.py` (extend, do NOT fork) and importing it does NOT transitively import
`fastapi`/`uvicorn`/`starlette` (assert absence from `sys.modules`).

**AC5 — The whole APAA suite green; tests cover the render honestly; mypy clean; ≤1200 lines (NFR-M1)**
**Given** the module + tests added by this story
**When** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` runs
**Then** all pass, including new tests in `tests/apaa/test_coverage_report.py`: the AC1 per-file
completeness (every entry rendered with path + depth + claim_present + recording_ids; all five states; empty
ledger), the AC2 aggregate arithmetic (per-depth counts + exact-`Fraction` deep-% + the gate-agreement
cross-check + the `total==0 → Fraction(0,1)` edge), the AC3 secret-safety (paths/ids/counts only; no source
bytes), the AC4 purity/frozen/no-`float`/byte-stability/typed-error tests, and the **AI-E1-1 non-ASCII
`file_path`** fixture rendered intact in BOTH text and JSON
**And** `ledger/coverage_report.py` is appended to `_MODULES_UNDER_GUARD` and the import-isolation gate stays
green; the 1.1 single-serializer AST gate (`test_canonical_single_serializer.py`) still passes with the new
module present (no direct `json.dumps(` in the new module — JSON goes through `store/canonical.dumps`); the
new source file is ≤1200 lines (NFR-M1) and cites its `APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in the module
docstring; `mypy` is clean on the new module. The 1.2 ledger/enum/accessors, the 1.6 gate, and the 1.1
serializer are UNCHANGED (this story adds a module + tests; the only non-additive edit is the test-only
import-isolation gate file, plus — IF the optional AC5 pipeline/cli seam is taken — an additive,
default-off-or-additive stdout/persist call that does not change the existing exit-code wire contract).

## Tasks / Subtasks

- [x] **Task 0 — Verify the existing data + reuse surface (verify-and-lock)** (AC: 1, 2)
  - [x] Re-read `ledger/coverage_ledger.py`: confirmed `CoverageLedger.entries` (sorted), `counts_by_depth()`
        (zero-filled, all five members), `deep_count()`, `total()` exist; UNCHANGED.
  - [x] Re-read `verdict/verdict_gate.py`: deep-% is `Fraction(deep_count, total)` (`Fraction(0,1)` at
        `total==0`). Surface REUSES this; gate UNCHANGED.
  - [x] Re-read `store/canonical.py`: `dumps`/`dumps_bytes` + `Fraction → "num/den"`; JSON routes through it.
  - [x] Re-read `ledger/depth_semantics.py`: legend table is OPTIONAL — not used (not needed for AC1–AC4).
- [x] **Task 1 — `ledger/coverage_report.py`: pure aggregate model** (AC: 2, 4)
  - [x] Created `minions_core/apaa/ledger/coverage_report.py` (docstring cites the drivers).
  - [x] Frozen `DepthAggregate` (`frozen=True, extra="forbid"`): `counts_by_depth`, `total`, `deep_count`,
        `deep_ratio: Fraction`, `percentages: dict[CoverageDepth, Fraction]` — NEVER `float`. Built via
        `build_depth_aggregate` reusing the 1.2 accessors + the gate's `Fraction(deep, total)`.
  - [x] Localized `COVERAGE_REPORT_SCHEMA_VERSION = "1"`. No `float`; no I/O/clock/LLM (AST test pins it).
- [x] **Task 2 — Pure per-file + textual + JSON render** (AC: 1, 2, 3, 4)
  - [x] Pure per-file render over `ledger.entries` (sorted) → `file_path` + `depth.value` + `claim_present` +
        `recording_ids`. `render_text` (markdown table + aggregate block); `render_json` via
        `store/canonical.dumps` over a live-`Fraction` payload dict.
  - [x] Locked + documented the markdown columns + ordering and the JSON payload shape in the module docstring.
  - [x] `CoverageReportError` (ValueError subclass) on non-`CoverageLedger` arg + unsupported `fmt`.
- [x] **Task 3 — Tests** (AC: 1, 2, 3, 4, 5)
  - [x] `tests/apaa/test_coverage_report.py` — 21 tests TC-APAA-LEDGER-001-110..130: AC1 completeness
        (all-five-states; empty; sorted order); AC2 counts/exact-Fraction percentages + the **gate-agreement
        cross-check** + `total==0 → Fraction(0,1)`; AC3 secret-safety (planted canary absent); AC4 purity
        (AST scan) / frozen / no-float / byte-stability (twice + two input orders) / typed-error / single
        serializer; **AI-E1-1 non-ASCII path** intact in text AND JSON.
  - [x] Test area `APAA-LEDGER`; synthetic ledgers via `CoverageLedger.build(...)`; zero LLM tokens.
- [x] **Task 4 — Extend the import-isolation gate** (AC: 4, 5)
  - [x] Appended `minions_core.apaa.ledger.coverage_report` to `_MODULES_UNDER_GUARD` (extended, NOT forked).
- [x] **Task 5 — (OPTIONAL) additive pipeline/cli render seam** (AC: 5)
  - [x] DECISION: **option (a) — pure-library-only** (minimal scope, recommended default). NO `cli.py`/
        `pipeline.py` change; the 1.7 summary line + exit-code wire contract are untouched by construction.
- [x] **Task 6 — Run + mypy** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → 417 passed.
  - [x] `mypy minions_core/apaa/ledger/coverage_report.py` → clean (no issues).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **This is a RENDER story, not a data-model story.** The 1.2 `CoverageLedger` already carries every field
  this surface reads (`file_path`, `depth`, `claim_present`, `recording_ids`) and every aggregate accessor
  (`counts_by_depth`, `deep_count`, `total`). The net-new artifact is a PURE rendering function + a small
  frozen aggregate model. Resist the temptation to "improve" the 1.2 ledger or add a field to
  `CoverageLedgerEntry` — changing the frozen contract is OUT of scope.
- **FR9 is the central driver (inspectability — the anti-black-box).** The operator must be able to read
  EXACTLY which files were examined at which depth AND the evidence that justified each. The surface renders
  every entry with its depth token + `claim_present` + `recording_ids`. The deep-% (the "VP question") is the
  aggregate headline.
- **No floats — ever — in a rendered / `.apaa/`-bound output (AR4 / Determinism / NFR-P1).** A percentage is
  the obvious `float` trap. Carry it as an exact `Fraction` (the gate's form — `Fraction(deep, total)`) or
  `Decimal`. Render a human percentage by formatting the EXACT fraction deterministically (e.g.
  `f"{frac.numerator}/{frac.denominator}"` or an exact `Decimal`-derived percent string), never
  `float(frac)*100`. Counts are `int`.
- **One serializer (AR4, §3.3) — JSON goes through `store/canonical.dumps`.** The JSON rendering MUST route
  through the single 1.1 serializer (which encodes `Fraction → "num/den"`, rejects `float`, sorts keys,
  `ensure_ascii=False`). A direct `json.dumps(` in the new module fails the committed AST gate
  `test_canonical_single_serializer.py`. Build a canonical-safe payload dict (entries + aggregate) and hand
  it to `canonical.dumps`.
- **Deep-% AGREEMENT with the gate (reuse, do not re-derive).** The surface's deep-% MUST equal
  `evaluate_verdict(ledger).deep_ratio` for the same ledger (both `Fraction(deep_count, total)`,
  `Fraction(0,1)` at `total==0`). A cross-check test pins this. Do NOT invent a second deep-% formula (e.g.
  one that counts `audited_shallow` — that would silently contradict FR8 and the gate).
- **Pure/impure separation (master rule, AR8).** `ledger/coverage_report.py` is PURE — no I/O, no clock, no
  LLM, no `uuid4`/`random`/`os.getpid()`. It RETURNS a string and/or a frozen model; it never `print()`s and
  never `open()`s. The impure caller (a test, or — if AC5 option b is taken — `cli.py`/`pipeline.py`) does the
  stdout write / `.apaa/` persist. ✅ a pure function returning the rendered string · ❌ a function that
  `print()`s or reads `datetime.now()`.
- **Secret-safety by construction (NFR-S1).** The `CoverageLedger` holds NO source/secret bytes (only paths +
  depth tokens + claim flags + opaque recording-id strings). The render must not INTRODUCE any — it never
  reads a source file. `recording_ids` are opaque id strings (not finding bodies / excerpts). The Epic-4
  containment property suite later enforces this mechanically; this story is the producer-side guarantee.
- **Error/degradation → typed, never crash (AR10).** A non-`CoverageLedger` argument or an unsupported render
  format selector → a typed `CoverageReportError` (ValueError subclass) localized to the module. NO bare
  `except: pass`, NO `print()` in library code, NO silent coercion.
- **Headless / no web surface (§3.7, AR9).** This is a developer-readable text/JSON artifact for a CLI /
  integrator — NOT a UI. No HTML/CSS/JS, no FastAPI route, no web stack import. APAA is downstream of the
  HTTP/A2A boundary — the module takes no token, registers no route, joins `_MODULES_UNDER_GUARD`.

### Decisions the dev must lock (record in the docstring + Change Log)

- **Module placement** — recommended `ledger/coverage_report.py` (cohesive with the 1.2 ledger it renders;
  the architecture maps FR9 to `ledger/coverage_ledger.py # FR5/FR6/FR8/FR9`). Do NOT create a top-level
  module if it fits here (NFR-M1 file-size permitting; the module will be small). A `verdict/`-adjacent
  placement is wrong — this renders the LEDGER, not the verdict.
- **Aggregate model shape** — a frozen `DepthAggregate` (or `CoverageReport` carrying entries + aggregate):
  `counts_by_depth: dict[CoverageDepth, int]`, `total: int`, `deep_count: int`, `deep_ratio: Fraction`, and a
  `percentages: dict[CoverageDepth, Fraction]` (or equivalent). Lock + document. NEVER `float`.
- **Textual format** — a deterministic plain-text or markdown table (recommended markdown for integrator
  readability), columns at least `file_path | depth | claim_present | recording_ids`, plus an aggregate block
  (per-depth counts + deep-%). Lock the column set + ordering + the percentage-rendering rule (exact-fraction
  derived, never `float`). Document it as the frozen surface shape.
- **JSON payload shape** — a frozen additive-only dict (entries list + aggregate) routed through
  `store/canonical.dumps`. Lock the key set.
- **Render API** — recommended: separate pure functions (e.g. `build_coverage_report(ledger) -> CoverageReport`,
  `render_text(report) -> str`, `render_json(report) -> str`) OR a single `render(ledger, *, fmt=...)`. Lock
  the chosen API + the supported `fmt` set; an unsupported `fmt` raises `CoverageReportError` (AR10).
- **Typed error type** — `CoverageReportError`, a `ValueError` subclass localized to the module (mirror
  `RecordingValidationError` / `CanonicalSerializationError` / `DepthSemanticsError`).
- **Pipeline/cli seam (AC5 Task 5)** — DECIDE (a) pure-library-only (minimal; recommended default) vs (b)
  additive opt-in stdout/persist in `cli.py`/`pipeline.py`. If (b): keep the existing summary line + exit-code
  wire contract byte-identical (NOT a wire-contract change). Record the decision.

### Precedent inherited from Stories 1.1–1.7 + 2.1 (done) — honor these decisions

- **No second serializer / second enum / second deep-% formula.** Reuse 1.1 `canonical.dumps`, 1.2
  `CoverageDepth` + `CoverageLedger` + accessors, the 1.6 `Fraction(deep, total)` deep-% arithmetic. The AST
  gate + the import-isolation gate enforce it.
- **Frozen `extra="forbid"` models** (1.1 `Envelope`, 1.2 `Recording`/`CoverageLedger`, 1.6 `AuditVerdict`,
  2.1 `DepthEvidence`): any model this story adds follows the same pattern with a localized `schema_version`.
- **`Fraction`/`Decimal`/`int` over `float`** — every ratio/percentage is non-`float`; the 1.1 serializer
  rejects `float`, and 1.6's `AuditVerdict.deep_ratio: Fraction` is the precedent (plus the
  `to_canonical_payload` Fraction-reinstall trick if you serialize a Pydantic model whose `model_dump()`
  would stringify a `Fraction` — see `verdict_gate.AuditVerdict.to_canonical_payload`; reuse the same pattern
  if your aggregate model holds `Fraction` fields and you serialize it).
- **`apaa_version`/`schema_version` single source** — `minions_core/apaa/__init__.py::__version__`
  (`"0.1.0"`); per-module `schema_version` is a localized constant (`COVERAGE_REPORT_SCHEMA_VERSION`), never
  env/clock.
- **Test-area precedent** — use area `APAA-LEDGER` for this story's test ids (`TC-APAA-LEDGER-001-NN`,
  continuing the 1.2/2.1 ledger area), consistent with the 1.x/2.1 convention.
- **Import-isolation gate is seeded, extend it** — append the new module to `_MODULES_UNDER_GUARD`; do not
  fork.
- **AI-E1-1 non-ASCII fixtures (Epic-1 retro / §9.1)** — because this surface RENDERS file paths, its tests
  MUST include a non-ASCII `file_path` proven rendered intact (the 1.4 story's git-ls-files non-ASCII drop was
  the Epic-1 review FAIL; the 2.1 `café_guard.py` fixture is the precedent). The 1.1 serializer is
  `ensure_ascii=False`, so the JSON render carries the UTF-8 path verbatim.

### The FR9 surface shape (the AC1/AC2 reference — lock + document)

Per-file rows (one per `CoverageLedger.entries`, in sorted order):

| field | source | note |
|---|---|---|
| `file_path` | `entry.file_path` | rendered verbatim (UTF-8; AI-E1-1 non-ASCII intact) |
| `depth` | `entry.depth.value` | one of the five `snake_case` `CoverageDepth` tokens |
| `claim_present` | `entry.claim_present` | the FR6 keystone — bool |
| `recording_ids` | `entry.recording_ids` | opaque id strings (NOT finding bodies / source) |

Aggregate block:

| field | source | form |
|---|---|---|
| per-depth counts | `ledger.counts_by_depth()` | `int` per all-five members (zero-filled) |
| `total` | `ledger.total()` | `int` |
| `deep_count` | `ledger.deep_count()` | `int` |
| `deep_ratio` (deep-%) | `Fraction(deep_count, total)` (`Fraction(0,1)` if `total==0`) | exact `Fraction` (== the 1.6 gate's `deep_ratio`) |
| per-depth % | `Fraction(count, total)` (`Fraction(0,1)` if `total==0`) | exact `Fraction`, NEVER `float` |

This block is FR9 expressed as data: the operator reads which files at which depth + the deep-% headline.

### Source tree — files to create (the only UPDATE is the import-isolation gate)

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/ledger/coverage_report.py` | NEW | FR9 — pure per-file + aggregate render of the 1.2 `CoverageLedger` (text + canonical JSON); exact-`Fraction` deep-% (PURE) |
| `tests/apaa/test_coverage_report.py` | NEW | per-file completeness (all five states + empty); aggregate arithmetic + gate-agreement cross-check; secret-safety; purity/frozen/no-float/byte-stability/typed-error; **non-ASCII path (AI-E1-1)** |
| `tests/apaa/test_no_web_imports.py` | UPDATE | extend `_MODULES_UNDER_GUARD` with the new module |
| `minions_core/apaa/cli.py` / `pipeline.py` | OPTIONAL/ADDITIVE | only if AC5 Task 5 option (b) is chosen — an additive opt-in stdout/persist call; the existing summary + exit-code wire contract stay byte-identical |

The architecture's package tree places ledger/render logic under `ledger/`. Do NOT invent additional modules;
do NOT modify `ledger/coverage_ledger.py`, `ledger/recording.py`, `verdict/verdict_gate.py`, or
`store/canonical.py` (this story is additive + a test-only change to the gate file, plus an optional additive
seam). Resist building ahead.

### Scope fences (do NOT pull forward)

- ❌ The **critical-subsystem GATE CLAUSE + operator DESIGNATION / `--critical-subsystem` flag** (FR4 gate
  half) — Story 2.3. (The surface MAY render a criticality column IF the data is present, but this story does
  not build criticality designation or the gate clause; the 1.6 `critical_subsystems_all_deep` seam stays
  defaulted-True until 2.3.)
- ❌ **Repository partitioning into bounded units / work-manifest** (FR3) — Story 2.4. (`partition_id` is
  always `"root"` in V1; render it if useful, but do not partition.)
- ❌ The **hardcoded-secret detector + producer-side redaction** (FR11/FR28) — Story 2.5. (The surface renders
  opaque `recording_ids`, never finding bodies / secret values.)
- ❌ The **zero-token breadth tool runner** that PRODUCES `tool_scanned_only` grades (FR14) — Story 2.6. (This
  surface RENDERS the `tool_scanned_only` state if present; it does not produce it.)
- ❌ The **evidence-bundle export** (ledger + scope statement + disclaimer + point-in-time stamp) (FR29) —
  Epic 4 Story 4.3. This story is the inspectable per-file ledger surface, NOT the regulator-grade bundle.
- ❌ The **negative-assurance verdict semantics** (scope statement / materiality bar / disclaimer) (FR17) —
  Epic 4 Story 4.1.
- ❌ Any change to the **1.2 ledger / enum / accessors**, the **1.6 verdict gate / thresholds**, or the
  **1.1 serializer** — all frozen contracts. This story RENDERS them; it does not modify them.
- ❌ A **new HTTP route / FastAPI surface / UI** (§3.7) — this is a CLI/library text/JSON artifact.

### Testing standards

- pytest under `tests/apaa/`; test ids follow `TC-<AREA>-<SEQ>-<SUBSEQ>` — use area `APAA-LEDGER` (e.g.
  `TC-APAA-LEDGER-001-NN`), continuing the 1.2/2.1 ledger area.
- These are **pure-function / synthetic-ledger tests** — zero LLM tokens (NFR-D2), no temp dirs for the module
  under test. Build synthetic ledgers via `CoverageLedger.build([grade_entry(file_path=..., proposed_depth=
  CoverageDepth.X, claim_present=...), ...])`.
- **The gate-agreement cross-check is MANDATORY** — the surface's deep-% MUST equal
  `evaluate_verdict(ledger).deep_ratio` on the same ledger (reuse, not re-derive). Pin it.
- **Byte-stability is MANDATORY (NFR-P1)** — render the same ledger twice → identical bytes; render two
  ledgers built from the same entries in different INPUT orders → identical bytes.
- **The non-ASCII `file_path` fixture is MANDATORY** (AI-E1-1) — a path like `auth/café_guard.py` or
  `модуль/тест.py` rendered intact (not mojibake, not dropped) in BOTH the text and the JSON rendering.
- **Secret-safety** — assert the render of a ledger contains the paths + ids + depth tokens + counts and never
  sources file bytes (operate purely on the in-memory ledger).
- On Windows, prefix runs with `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on cp1252).
- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` (the WHOLE
  `tests/apaa/` suite, so the 1.1 single-serializer AST gate + the extended no-web-imports gate re-run with
  the new module present). All must pass before moving to `review`.
- `mypy` clean on the new module (`python run_mypy_per_file.py` or a scoped invocation).

### CLAUDE.md §4a follow-up

The §4a APAA Component→Driver row was added by Story 1.1. This story does NOT need a new §4a row; if a
one-line additive note is added it must note `ledger/coverage_report.py` as the FR9 readable per-file
coverage-ledger surface and must NOT rewrite the existing row. Keep it minimal — a new row is not required.

### Project Structure Notes

- Alignment: the new module lives under `ledger/` (cohesive with the 1.2 coverage ledger it renders; the
  architecture maps FR9 to the ledger layer). Naming `snake_case.py`, ≤1200 lines (NFR-M1). Enum/JSON values
  `snake_case`.
- No conflicts/variances. Judgment calls — all decided above and to be documented so they freeze for
  downstream: the module placement, the aggregate model shape, the textual + JSON formats, the render API +
  supported formats, the typed-error type, and the optional pipeline/cli seam decision.
- Scope fence: this story delivers the PURE per-file + aggregate readable surface (text + canonical JSON) of
  the existing 1.2 ledger ONLY. The critical-subsystem gate clause / designation (2.3), partitioning (2.4),
  the secret detector (2.5), the breadth tool runner that produces `tool_scanned_only` (2.6), the
  evidence-bundle export (4.3), the negative-assurance semantics (4.1), and any change to the 1.2 ledger / 1.6
  gate / 1.1 serializer are explicitly NOT in scope. Render the existing data, then stop.

### References

- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Story-2.2 Readable per-file coverage ledger surface] (the two ACs: every file with depth + justifying evidence; per-depth counts + percentages derivable, no source bytes)
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#FR9] ("An operator can read exactly which files were examined deeply, shallowly, tool-scanned, inferred, or skipped")
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#NFR-S1] (no source/prompt/response/secret bytes in ledgers, evidence, logs, traces, or any response)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Package tree] (`ledger/coverage_ledger.py # FR5/FR6/FR8/FR9` — FR9 maps to the ledger layer)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Determinism Patterns] (one serializer; no floats — ratios fixed-precision; no iteration-order reliance; byte-identical across hosts NFR-P1)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Pure/Impure Separation (master rule)] (ledger/render pure — no I/O, no clock, no LLM)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Architectural Boundaries] (APAA downstream of HTTP/A2A; no web surface in V1; import-isolation `apaa.* ⊬ fastapi/uvicorn/starlette`)
- [Source: _bmad-output/design-artifacts/ArgusAgent/epic-1-retro-2026-06-21.md#7. Action Items] (AI-E1-1 adversarial non-ASCII fixtures; AI-E1-4 gates extended-not-forked; AI-E1-5 exercise the L1-E11 loop)
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/2-1-complete-depth-state-semantics-inferred-never-satisfies-a-gate.md] (DONE — `DEPTH_SEMANTICS` table + `classify_depth` + `assess_criticality`; FR8 proofs; the depth-semantics this surface renders)
- [Source: minions_core/apaa/ledger/coverage_ledger.py] (`CoverageDepth`, `CoverageLedger.build`/`entries`/`counts_by_depth`/`deep_count`/`total`, `grade_entry` — REUSE verbatim, do NOT modify)
- [Source: minions_core/apaa/ledger/depth_semantics.py] (DONE — `DEPTH_SEMANTICS` legend table; OPTIONAL per-state description context for the render)
- [Source: minions_core/apaa/verdict/verdict_gate.py] (`evaluate_verdict(...).deep_ratio = Fraction(deep_count, total)` — the deep-% arithmetic the surface REUSES + cross-checks; `AuditVerdict.to_canonical_payload` Fraction-reinstall pattern)
- [Source: minions_core/apaa/store/canonical.py] (THE single serializer — `dumps`/`dumps_bytes`; `Fraction → "num/den"`; rejects `float`; `ensure_ascii=False`. The JSON render routes through it; the AST gate forbids a second `json.dumps`)
- [Source: minions_core/apaa/cli.py] (the existing thin stdout summary + exit-code contract — if the optional AC5 seam is taken, it stays byte-identical)
- [Source: minions_core/apaa/__init__.py] (`__version__ = "0.1.0"` — single apaa_version source)
- [Source: CLAUDE.md §3.2 file-size / §3.7 headless-only / §3.8 12-Factor + secret masking / §9.1 L1-E11 retro-action-items loop]

## Dev Agent Record

### Context Reference

- Implemented by `/bmad-dev-story` (mode=implement) 2026-06-21.

### Agent Model Used

- claude-opus-4-8

### Completion Notes

- Net-new PURE render module `minions_core/apaa/ledger/coverage_report.py` (362 lines, ≤1200 NFR-M1):
  `build_coverage_report`, `build_depth_aggregate`, `render_text`, `render_json`, `render(ledger, *, fmt=...)`,
  plus the frozen `CoverageReport` / `DepthAggregate` models and `CoverageReportError` (ValueError subclass).
- REUSE-only: imports the 1.2 ledger models + the 1.1 `store/canonical` serializer. The 1.2 ledger / enum /
  accessors, the 1.6 verdict gate, and the 1.1 serializer are UNCHANGED (verified — only additive new module +
  the test-only import-isolation gate edit).
- Deep-% reuses the 1.6 `Fraction(deep_count, total)` arithmetic (`Fraction(0,1)` at `total==0`); the MANDATORY
  gate-agreement cross-check (`build_depth_aggregate(ledger).deep_ratio == evaluate_verdict(ledger).deep_ratio`)
  is pinned over three ledgers (TC-APAA-LEDGER-001-118).
- JSON routes through `store/canonical.dumps` (no second `json.dumps` — the AST single-serializer gate stays
  green). `Fraction` leaves handed live so the canonical `"num/den"` encoding applies (the 1.6
  `to_canonical_payload` precedent); `ensure_ascii=False` → non-ASCII paths verbatim. No `float` anywhere.
- Secret-safe by construction (NFR-S1): paths + depth tokens + claim flags + opaque recording-ids + counts only;
  TC-APAA-LEDGER-001-121 proves a planted source/secret canary never appears in the render.
- AI-E1-1 (Epic-1 retro): non-ASCII fixture (`café_guard.py`, `модуль/тест.py`, `日本/モジュール.py`) rendered
  intact in BOTH text and JSON (TC-APAA-LEDGER-001-130). AI-E1-4: import-isolation gate EXTENDED not forked.
  AI-E1-5: the discharged AI-E1-* items are referenced here (L1-E11 loop exercised).
- **Decision (Task 5 / AC5 seam):** option (a) pure-library-only — NO `cli.py`/`pipeline.py` wiring this story
  (minimal scope); the existing 1.7 stdout summary + exit-code wire contract are untouched by construction (no
  wire-contract change).
- Validation: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → 417 passed
  (396 prior + 21 new); `mypy minions_core/apaa/ledger/coverage_report.py` → clean.

### File List

- `minions_core/apaa/ledger/coverage_report.py` (NEW)
- `tests/apaa/test_coverage_report.py` (NEW)
- `tests/apaa/test_no_web_imports.py` (UPDATE — `_MODULES_UNDER_GUARD` extended with the new module)

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-06-21 | 0.1.0 | Story 2.2 implemented: pure FR9 readable per-file coverage-ledger surface (text + canonical JSON) over the 1.2 `CoverageLedger`; frozen `CoverageReport`/`DepthAggregate`; exact-`Fraction` deep-% reusing + cross-checking the 1.6 gate; secret-safe (NFR-S1); pure/byte-stable/import-isolated; non-ASCII path fixture (AI-E1-1). AC5 seam decision: option (a) pure-library-only (no pipeline/cli wiring, no wire-contract change). 417 passed, mypy clean. | dev-story (claude-opus-4-8) |
| 2026-06-21 | 0.1.0 | Code review iter-1 → PASS (status review → done). Adversarial 3-layer review (Blind Hunter / Edge Case Hunter / Acceptance Auditor). All 5 ACs met; 417 passed, mypy clean, 313 non-blank lines. Frozen contracts (1.2 ledger / 1.6 gate / 1.1 serializer) verified UNCHANGED (no working-tree diff). Gate-agreement cross-check (TC-118) real and non-divergent; JSON single-serializer + import-isolation gates green. 1 Low non-blocking observation recorded (markdown-cell robustness for pathological paths). | code-review (claude-opus-4-8) |

## Senior Developer Review (AI)

**Reviewer:** code-review (claude-opus-4-8) · **Date:** 2026-06-21 · **Iteration:** 1
**Verdict:** PASS · **Status set:** review → done

### Summary

Story 2.2 delivers a clean, single-purpose PURE FR9 readable surface
(`minions_core/apaa/ledger/coverage_report.py`, 313 non-blank lines) over the
existing 1.2 `CoverageLedger`. It is correctly a RENDER story: it adds NO field
to the frozen 1.2/1.6/1.1 contracts (verified — those files have no working-tree
diff), re-implements no arithmetic, and routes all JSON through the single 1.1
`store/canonical.dumps`. All five ACs are met and the whole APAA suite is green.

### Adversarial review findings

**Blind Hunter (correctness/security).** No correctness or security defects.
- The surface's `deep_ratio` is the SAME `Fraction(deep_count, total)` form the
  1.6 gate uses (`Fraction(0,1)` at `total==0`) — confirmed line-for-line against
  `verdict_gate.evaluate_verdict`. No divergent second formula. The MANDATORY
  gate-agreement cross-check (TC-APAA-LEDGER-001-118) is real and pins agreement
  over three ledgers including the all-five-states and a 7/7-deep case.
- JSON routes solely through `canonical.dumps`; no second `json.dumps` (the AST
  single-serializer gate is green with the new module present). `Fraction` leaves
  are handed live so the canonical `"num/den"` encoding applies (the 1.6
  `to_canonical_payload` precedent). No `float` anywhere (AR4).
- Secret-safety by construction (NFR-S1): only `file_path` + depth token +
  `claim_present` + opaque `recording_ids` + counts surface; the module never
  reads a source file. TC-121 proves a planted source/secret canary is absent.
- AR10 typed failure: `CoverageReportError(ValueError)` on a non-`CoverageLedger`
  arg and on an unsupported `fmt` — no silent coerce / bare `except` / `print`.

**Edge Case Hunter (boundaries/branches).** No unhandled edge case.
- Empty ledger → `Fraction(0,1)`, no divide-by-zero, well-formed `total: 0`
  surface (TC-114/119). Non-ASCII paths (café / Cyrillic / Japanese) render
  intact in BOTH text and JSON and round-trip through the serializer verbatim
  (TC-130, AI-E1-1). Byte-stability pinned twice + across two input orders
  (TC-125/126). Empty `recording_ids` renders `[]`, never omitted (TC-112).
- The per-depth output iterates the closed `CoverageDepth` enum in declaration
  order (not a dict/set), and entries iterate the already-sorted `ledger.entries`
  — no iteration-order reliance (AR4). Purity is AST-pinned (TC-122).

**Acceptance Auditor (AC/spec conformance).** All five ACs satisfied.
- AC1 per-file completeness + all-five-states + sorted-order + empty: covered.
- AC2 zero-filled counts + exact-`Fraction` deep-% + gate cross-check + total==0:
  covered. AC3 secret-safety canary: covered. AC4 pure/frozen/no-float/byte-
  stable/typed-error/single-serializer + import-isolation gate EXTENDED (not
  forked): covered. AC5 whole suite green (417), mypy clean, ≤1200 lines, drivers
  cited in the docstring, frozen contracts unchanged, AC5 seam = option (a)
  pure-library-only (no wire-contract change): all confirmed.

### Independent verification

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py`
  → **417 passed** (re-run by reviewer). The 1.1 single-serializer AST gate and
  the extended no-web-imports gate re-ran green with the new module present.
- `mypy minions_core/apaa/ledger/coverage_report.py` → clean.
- `git diff` on `coverage_ledger.py` / `verdict_gate.py` / `canonical.py` → empty
  (frozen contracts genuinely untouched; reuse, not fork).

### Action Items

- None blocking. One Low non-blocking observation (NOT a defect for this scope):
  `render_text` emits a markdown table whose cells are `file_path` / depth /
  `claim_present` / `recording_ids`. A pathological `file_path` or `recording_id`
  containing a literal `|` or newline would visually corrupt the markdown table
  (it would not leak secrets — values are repo-relative file paths + opaque ids
  by construction, and JSON is unaffected). Acceptable as-is; if a future story
  surfaces arbitrary tokens in the text table, consider escaping `|`/newline in
  text cells. Not filed as a defer (cosmetic, in-scope-clean).
