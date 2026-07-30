# Story 1.2: Fixed-enum coverage ledger & frozen recording schema

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As an APAA maintainer,
I want a fixed-enum coverage ledger and a first-class frozen recording schema as pure Pydantic v2 models,
so that the verdict can be a pure fold over recordings with no field the verdict later needs missing — the
second link in the determinism spine.

## Story Context

This is **Story 2 of Epic 1** (Signature-Demo Vertical Slice). It builds directly on **Story 1.1 (done)**,
which delivered the PURE determinism spine under `minions_core/apaa/store/`: the single canonical serializer
(`store/canonical.py`) and the content-hashed, schema-versioned, prev-hash-chained envelope
(`store/envelope.py`). This story adds the **second link**: the fixed-enum **coverage ledger** and the
first-class **frozen recording schema** as PURE Pydantic v2 models under a NEW `minions_core/apaa/ledger/`
sub-package.

Per the architecture's explicit implementation sequence — *"envelope + canonical serializer + fixed-enum
ledger (C-core) → AST index → pure verdict → 🔴 on the cartridge"* — these two models are the data
substrate every later module folds over: Story 1.5's detectors emit `Recording` rows, Story 1.6's
pure-function verdict gate folds the `CoverageLedger` into a verdict, Story 1.3's `.apaa/` writer/reader
persists/round-trips them through the 1.1 serializer/envelope, and Epic 5's memoization keys on the
recording set. If a recording omits a field the verdict later needs, you are forced to re-run an LLM — so
the recording schema is **frozen as aggressively as the verdict schema** (architecture: *"the recording
schema is a first-class frozen contract"*).

**Why this matters (architecture cross-cutting concerns #1/#6, Contract/Format Patterns):** the verdict's
purity and the ≥80%-precision measurability both rest on these contracts being closed and complete at
birth. The coverage-ledger enum is **closed** (a new depth state is a breaking change unless additive); the
recording schema reserves every field downstream consumers will read (`partition_id`, finding shape,
advisory flag, locator, coverage-envelope slice). Get the enum or the schema wrong and either the verdict
cannot be a pure fold (forced LLM re-run) or precision cannot be replayed.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 1.2) and the architecture (Decision C, §Contract/Format
> Patterns, §Pure/Impure Separation). Drivers: **APAA-FR-5** (fixed-enum coverage ledger), **APAA-FR-6**
> (claim-required `audited_deep`; silence → `audited_shallow`), **APAA-NFR-D2** (deterministic, zero-LLM-token
> ledger/recording construction), **APAA-NFR-M2** (frozen, additive-only contracts validated with Pydantic
> v2), **APAA-NFR-M1** (≤1200-line files), **AR8** (pure modules — no I/O, no clock, no LLM), **AR10**
> (typed failure, never an uncaught raise / silent coerce). Note: FR8 (`inferred` never satisfies a gate)
> and FR9 (readable per-file ledger surface) are GATE/SURFACE behaviors delivered in Epic 2 / Story 1.6 —
> this story only provides the data model that makes them expressible; do NOT build the gate or the rendered
> surface here (scope fence).

**AC1 — Closed fixed-enum coverage depth states (FR5, NFR-M2)**
**Given** the coverage-depth enum
**When** it is defined in `ledger/coverage_ledger.py`
**Then** it is a closed Python `enum.Enum` (str-valued) with EXACTLY the five members
`audited_deep / audited_shallow / tool_scanned_only / inferred / skipped` and their string values are those
exact `snake_case` tokens (canonical-serializable as strings)
**And** a committed test pins the membership set so adding/removing/renaming a depth state fails the test
(the enum is closed; new states are an additive `schema_version` bump, never an ad-hoc edit).

**AC2 — Per-file coverage-ledger entry model (FR5, FR9-support, NFR-M2)**
**Given** a single file's audit outcome
**When** it is recorded as a `CoverageLedgerEntry` (frozen Pydantic v2)
**Then** the entry carries at minimum: `file_path: str`, `depth: CoverageDepth`, an evidence/claim
reference sufficient to justify the depth (e.g. `recording_ids: tuple[str, ...]` and/or `claim_present:
bool`), and `partition_id: str` (reserved, always `"root"` in V1) — every field the FR9 readable surface
and the FR6/FR16 gate will later read is present
**And** the model is `frozen=True, extra="forbid"` (additive-only; an unknown field on read-back is a typed
`ValidationError`, mirroring the Story 1.1 `Envelope` decision).

**AC3 — Coverage-ledger aggregate model (FR5, FR9-support, NFR-D2)**
**Given** a set of per-file entries for one audit unit
**When** a `CoverageLedger` is constructed
**Then** it holds the entries keyed/ordered deterministically (sorted by `file_path` — NO dict/`set`
iteration-order reliance, per AR4/Determinism Patterns), carries `schema_version` + reserved `partition_id`
(`"root"`), and exposes a PURE accessor for per-depth counts (e.g. `counts_by_depth() -> dict[CoverageDepth,
int]`) so the deep-% (the verdict-gate input) is derivable WITHOUT any I/O or LLM token
**And** two `CoverageLedger`s built from the same entries in different insertion orders are equal and
serialize byte-identically through `store/canonical.dumps` (determinism).

**AC4 — `audited_deep` requires a claim; silence downgrades to `audited_shallow` (FR6)**
**Given** a file proposed as `audited_deep` with NO accompanying emitted claim
**When** the entry is constructed via the ledger's grading constructor/factory
**Then** the recorded depth is downgraded to `audited_shallow` (silence → shallow), NOT `audited_deep`
**And** the same file WITH an emitted claim records as `audited_deep`. The downgrade is performed by a PURE
function/validator on the model (no I/O, no LLM); the rule is unit-tested both directions. (Note: V1
records the *presence* of a claim — AST-validating the claim's truth is Story 1.5's vacuous-path subset and
Story 6.2's full AST-grounding; do NOT validate claim content here.)

**AC5 — Frozen first-class recording schema (recording-producing closure; NFR-M2, NFR-D2, AR8)**
**Given** the `Recording` schema (what an LLM/detector call emits — the row the verdict folds over)
**When** it is defined in `ledger/recording.py`
**Then** it is a frozen Pydantic v2 contract (`frozen=True, extra="forbid"`) that reserves every field a
downstream verdict/precision consumer needs, including: a stable `finding_id`/`recording_id`, `partition_id`
(reserved, `"root"` in V1), the depth/claim it supports, the `rule_id`/`cartridge_id` provenance, an
`advisory: bool` flag, ≥1 verifiable locator (file + line-range/AST span), and a coverage-envelope slice
reference — so the verdict is a pure fold and precision is replayable (architecture: freeze the recording
schema as hard as the verdict)
**And** the schema validates/builds with zero LLM tokens and performs no I/O or clock read in the model
layer (AR8 pure); evolution is additive-only (`schema_version` bump, new OPTIONAL fields only).

**AC6 — Locator-or-reject is expressible at the model layer (FR13-support, AR10)**
**Given** a `Recording` constructed with NO verifiable locator
**When** it is validated
**Then** construction raises a typed error (Pydantic `ValidationError` or an APAA-typed subclass) — a
recording without a locator cannot be minted (FR13's "rejected, not emitted" is enforceable at the data
layer; the detector-side emission policy is Story 1.5)
**And** a recording WITH ≥1 well-formed locator validates. No silent default/empty locator is accepted.

**AC7 — Zero-token, pure, I/O-free construction (NFR-D2, AR8)**
**Given** `ledger/coverage_ledger.py` and `ledger/recording.py`
**When** they are imported and exercised in unit tests
**Then** they perform NO filesystem I/O, NO clock read (`datetime.now`/`time.time`), NO `uuid4`/`os.getpid()`/
`random`, NO LLM/network call — they are pure constructions over in-memory inputs (the impure `.apaa/` write
shell is Story 1.3)
**And** any score/ratio field, if present, is typed as `Decimal`/`Fraction` or `int` (NEVER `float`) so it
survives the Story 1.1 canonical serializer's float-rejection (the NFR-P1 byte-diff landmine defense).

**AC8 — Round-trips byte-identically through the 1.1 serializer + envelope (NFR-P1, reuse)**
**Given** a populated `CoverageLedger` and a `Recording`
**When** each is serialized via `store/canonical.dumps` and wrapped/round-tripped (model → dict → canonical
bytes → `loads` → model)
**Then** the result equals the original and the canonical bytes are stable (golden), and a `compute_content_hash`
over the model's canonical payload is reproducible — REUSING `store/canonical.py` + `store/envelope.py`,
never introducing a second serializer (AC2 of Story 1.1 stays green: the no-second-`json.dumps` AST gate
must still pass with the new modules present).

**AC9 — Import isolation holds for the new modules (AR7/AR9, headless boundary)**
**Given** the modules added by this story
**When** `tests/apaa/test_no_web_imports.py` runs (extend its `_MODULES_UNDER_GUARD` tuple seeded by Story
1.1)
**Then** importing `minions_core.apaa.ledger.coverage_ledger` and `minions_core.apaa.ledger.recording` does
NOT transitively import `fastapi` / `uvicorn` / `starlette` (assert absence from `sys.modules`).

## Tasks / Subtasks

- [x] **Task 1 — Create the `ledger/` sub-package + closed coverage-depth enum** (AC: 1, 7)
  - [x] Create `minions_core/apaa/ledger/__init__.py` (package marker; no logic).
  - [x] Create `minions_core/apaa/ledger/coverage_ledger.py` with a module docstring citing `APAA-FR-5`,
        `APAA-FR-6`, `APAA-NFR-D2`, `APAA-NFR-M2`, `AR8`.
  - [x] Define `class CoverageDepth(str, enum.Enum)` with exactly the five members
        `AUDITED_DEEP="audited_deep"`, `AUDITED_SHALLOW="audited_shallow"`,
        `TOOL_SCANNED_ONLY="tool_scanned_only"`, `INFERRED="inferred"`, `SKIPPED="skipped"`.
  - [x] (Pure, no I/O / clock / LLM / `random` / `uuid4`.)
- [x] **Task 2 — `CoverageLedgerEntry` + `CoverageLedger` models** (AC: 2, 3, 7)
  - [x] Define `CoverageLedgerEntry` (frozen Pydantic v2, `frozen=True, extra="forbid"`): `file_path: str`,
        `depth: CoverageDepth`, `partition_id: str = "root"`, `claim_present: bool`,
        `recording_ids: tuple[str, ...] = ()` (or equivalent evidence reference). No `float` fields.
  - [x] Define `CoverageLedger` (frozen): `schema_version: str`, `partition_id: str = "root"`,
        `entries: tuple[CoverageLedgerEntry, ...]` stored sorted by `file_path` (deterministic order — no
        dict/`set` iteration-order reliance).
  - [x] Add a PURE `counts_by_depth() -> dict[CoverageDepth, int]` accessor (and `deep_count`/`total`
        helpers) so the deep-% the verdict gate needs is derivable with zero tokens.
  - [x] Ensure equality is order-independent over input entries (sort canonicalizes).
- [x] **Task 3 — `audited_deep` claim-required grading (silence → shallow)** (AC: 4)
  - [x] Add a PURE grading constructor/factory (module-level `grade_entry(...)`) that downgrades a
        `proposed_depth == AUDITED_DEEP` to `AUDITED_SHALLOW` when `claim_present is False`, leaving all
        other depths unchanged.
  - [x] Document the rule in the docstring (FR6: silence → shallow); do NOT validate the claim's *content*
        (that is Story 1.5 / 6.2).
- [x] **Task 4 — Frozen first-class recording schema** (AC: 5, 6, 7)
  - [x] Create `minions_core/apaa/ledger/recording.py` (docstring cites `APAA-FR-5`, `APAA-FR-13`-support,
        `APAA-NFR-D2`, `APAA-NFR-M2`, `AR8`).
  - [x] Define a `Locator` frozen model: `file_path: str`, `start_line: int`, `end_line: int`, optional
        `ast_span`. Validate `start_line <= end_line`, lines ≥ 1.
  - [x] Define `Recording` (frozen, `extra="forbid"`): stable `recording_id: str` (a.k.a. `finding_id`),
        `partition_id: str = "root"`, `rule_id: str`, `cartridge_id: str | None = None`, `advisory: bool`,
        `locators: tuple[Locator, ...]` (≥1 enforced), `depth_supported: CoverageDepth | None`,
        `claim_present`, and `coverage_envelope_slice` reference field.
  - [x] Add a validator that rejects an empty `locators` tuple with a typed error (`RecordingValidationError`,
        a `ValueError` subclass) — FR13 locator-or-reject at the model layer. NO `float` fields anywhere.
- [x] **Task 5 — Determinism + model golden tests** (AC: 1, 2, 3, 4, 5, 6, 7, 8)
  - [x] `tests/apaa/test_coverage_ledger.py`: enum-membership pin (AC1); entry/ledger build + frozen/
        extra-forbid; `counts_by_depth` correctness; order-independent equality; silence→shallow both
        directions (AC4); zero-`float` invariant.
  - [x] `tests/apaa/test_recording_schema.py`: `Recording` build; locator-or-reject typed failure (AC6);
        frozen/extra-forbid; additive-optional-field does not change `content_hash`; schema-version bump does.
  - [x] Serializer round-trip + golden: byte-stable golden strings + reproducible `compute_content_hash` for
        a populated `CoverageLedger` and `Recording`; `loads(dumps(x))` reconstructs an equal model (AC8).
        REUSES `store/canonical` + `store/envelope` — no second serializer.
  - [x] Confirmed the Story 1.1 `test_canonical_single_serializer.py` AST gate still passes with the new
        `ledger/` modules present (no direct `json.dumps`).
- [x] **Task 6 — Extend the import-isolation gate** (AC: 9)
  - [x] Added `minions_core.apaa.ledger.coverage_ledger` and `minions_core.apaa.ledger.recording` to
        `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py`.
- [x] **Task 7 — Test scaffold + run + mypy** (AC: all)
  - [x] Ran `PYTHONIOENCODING=utf-8 pytest tests/apaa/ -v` → 87 passed (incl. the 1.1 suite + single-
        serializer AST gate). `tests/test_import_paths.py` green (no flat-stub regression).
  - [x] `mypy` clean on the three new `ledger/` modules.

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **Pure/impure separation (master rule, AR8).** `ledger/coverage_ledger.py` and `ledger/recording.py` are
  **PURE** — no I/O, no clock, no LLM, no network, no `uuid4`/`random`/`os.getpid()`. They are Pydantic v2
  models + pure functions over in-memory inputs. The impure `.apaa/` write/read shell
  (`store/writer.py`, `store/paths.py`, `store/reader.py`) is **Story 1.3** — do NOT build it here. ✅ a
  frozen model with a pure `counts_by_depth()` · ❌ a model `__init__` that reads a file or `datetime.now()`.
- **Recording schema = first-class frozen contract (architecture Decision C / cross-cutting #1).** The
  verdict is a pure FOLD over recordings. Reserve every field a downstream consumer (verdict gate,
  Prosecutor, precision replay harness, memo cache key) will read, NOW — a missing field forces an LLM
  re-run later. Freeze it as hard as the verdict: `frozen=True, extra="forbid"`, additive-only evolution.
- **Closed coverage enum (architecture §Contract/Format Patterns).** The five depth states are CLOSED.
  Never invent a sixth ad hoc; a genuinely new state is an additive `schema_version` bump. The AC1 membership
  pin is the durable enforcement so a future author cannot silently widen it.
- **`audited_deep` requires a claim; silence → shallow (FR6).** This is the honesty keystone: a deep grade
  cannot be minted without an emitted claim. V1 records claim *presence* only; AST-validating the claim's
  *truth* (downgrade an unverifiable claim) is Story 1.5 (vacuous-path subset) and Story 6.2 (full AST).
  Do NOT pull that forward.
- **No floats — ever — in a `.apaa/`-bound model (AR4 / Determinism Patterns / R4 red-team).** Any ratio/
  score is `Decimal`/`Fraction`/`int`. The Story 1.1 canonical serializer REJECTS `float` with a typed
  `CanonicalSerializationError`; a `float` field here would explode at serialize time. Floats are *"the
  NFR-P1 byte-diff landmine across hosts."*
- **One serializer, forever (AR4, cross-cutting #3).** All `.apaa/` JSON goes through
  `store/canonical.py` (delivered by Story 1.1). REUSE it for every round-trip/golden test; the committed
  `test_canonical_single_serializer.py` AST gate will FAIL the build if a direct `json.dumps(` appears in
  the new `ledger/` modules. Use `canonical.dumps` / `canonical.loads` / `envelope.compute_content_hash`.
- **Deterministic ordering (AR4).** Store `entries` sorted by `file_path`; never rely on dict/`set`
  iteration order. Equality and serialization must be insertion-order-independent (AC3) — this is what makes
  sequential and parallel runs byte-identical (NFR-P1).
- **Error/degradation (AR10).** Failure → a typed exception at this pure layer (Pydantic `ValidationError`,
  or an APAA-typed subclass for locator-or-reject). NO bare `except: pass`, NO `print()` in library code, NO
  silent coercion of an invalid recording into a valid-looking one.
- **Headless / boundary (architecture §Architectural Boundaries).** APAA is downstream of the HTTP/A2A
  boundary — these modules take no token, register no FastAPI route, and must not import the web stack
  (AC9 / AR7). Never import `minions_core.api.* / services.api_app / app_factory / api_server`.

### Precedent inherited from Story 1.1 (done) — honor these decisions

- **`extra="forbid"` on frozen models** — Story 1.1's `Envelope` chose `frozen=True, extra="forbid"` (an
  unknown field on read-back is a typed error, not silent acceptance), explicitly stricter than the literal
  spec, to support the NFR-M2 "never retype/rename" invariant. Apply the SAME pattern to `CoverageLedger`,
  `CoverageLedgerEntry`, `Recording`, `Locator`.
- **Golden constants for determinism** — Story 1.1 froze a golden canonical string + golden `content_hash`
  so any byte-drift fails loudly. Do the SAME for the populated ledger/recording golden round-trip (AC8).
- **`apaa_version`/`schema_version` from a single constant source** — `apaa_version` lives at
  `minions_core/apaa/__init__.py::__version__` (`"0.1.0"`, added by Story 1.1). For `schema_version` on the
  new models, use a per-model module constant (e.g. `LEDGER_SCHEMA_VERSION`, `RECORDING_SCHEMA_VERSION`) so
  additive bumps are localized; never read it from env/clock.
- **Import-isolation gate is seeded, extend it** — `tests/apaa/test_no_web_imports.py` already has a
  `_MODULES_UNDER_GUARD` tuple "seeded for later stories to extend" — append the two new module paths there
  (AC9), do not write a parallel gate.
- **Decimal/Fraction string encoding is already frozen** — Story 1.1 locked `Decimal` →
  `format(d.normalize(), 'f')` and `Fraction` → `"numerator/denominator"`. If any score field is added,
  it inherits this encoding automatically through `canonical.dumps`; do not re-implement encoding.

### Source tree — files to create (all NEW; the only UPDATE is the import-isolation gate)

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/ledger/__init__.py` | NEW | `ledger` sub-package marker |
| `minions_core/apaa/ledger/coverage_ledger.py` | NEW | `CoverageDepth` enum + `CoverageLedgerEntry` + `CoverageLedger` + grading fn (PURE) |
| `minions_core/apaa/ledger/recording.py` | NEW | `Locator` + frozen `Recording` schema (PURE) |
| `tests/apaa/test_coverage_ledger.py` | NEW | enum-pin, entry/ledger, counts, silence→shallow, golden round-trip |
| `tests/apaa/test_recording_schema.py` | NEW | recording build, locator-or-reject, frozen, additive-field |
| `tests/apaa/test_no_web_imports.py` | UPDATE | extend `_MODULES_UNDER_GUARD` with the two new modules |

The architecture's package tree (`architecture.md` §Project Structure) places EXACTLY `coverage_ledger.py`
and `recording.py` under `ledger/`. Do NOT invent additional modules (the verdict gate is `verdict/` Story
1.6; the `.apaa/` writer/reader is `store/` Story 1.3; detectors are `detectors/` Story 1.5). Resist
building ahead.

### Reuse — what already exists (verified present) and what NOT to reinvent

- **Story 1.1 store spine** (`minions_core/apaa/store/canonical.py` + `store/envelope.py` — DONE, present):
  `canonical.dumps(payload) -> str`, `canonical.dumps_bytes(payload) -> bytes`, `canonical.loads(text) ->
  object`, `CanonicalSerializationError(ValueError)`; `Envelope` model, `EnvelopeWriter.build(...)`,
  `compute_content_hash(payload) -> str`, `GENESIS_PREV_HASH = "0"*64`. REUSE these for ALL serialization,
  hashing, and golden tests — do NOT add a second serializer (the AC2/Story-1.1 AST gate enforces this).
- **Pydantic v2** is an existing Minions baseline dependency — `from pydantic import BaseModel, ConfigDict,
  field_validator` (or `model_validator`). Do NOT add a dependency. `jsonschema`/`tree-sitter`/`radon` are
  NOT needed for this story (they arrive in Stories 1.4+).
- **`minions_core/apaa/__init__.py::__version__`** (`"0.1.0"`) — the single `apaa_version` source from
  Story 1.1; reuse if a model needs to stamp the APAA version (volatile fields stay out of the content hash
  per NFR-D3 — but `schema_version` IS part of the hashed payload, by design).

### Determinism / contract decisions the dev must lock (record the choice in the docstring)

- **Enum value strings ARE the wire contract** — `audited_deep` etc. are serialized verbatim; do not change
  casing or punctuation. Use `class CoverageDepth(str, enum.Enum)` so members serialize as their string
  value through `canonical.dumps` (a bare `enum.Enum` member is not JSON-serializable — verify the round
  trip).
- **`entries` ordering** — store sorted by `file_path` (a tuple, not a dict, to keep it frozen and ordered);
  golden-test that two different input orders yield identical canonical bytes.
- **Locator-or-reject error type** — either a Pydantic `ValidationError` (from a `model_validator`) OR a new
  typed `RecordingValidationError(ValueError)` (mirroring `CanonicalSerializationError`). Pick ONE, document
  it, and test it (AC6). If a new exception is added, keep it in `ledger/recording.py` (no cross-module
  coupling).
- **`schema_version` is part of the hashed payload** (unlike `run_id`/`created_at`, which Story 1.1 excludes
  from the hash) — a schema bump deliberately changes the content hash. Confirm the additive-optional-field
  test asserts: adding an OPTIONAL field with a default does NOT change an EXISTING payload's hash, but a
  `schema_version` bump does (NFR-M2 additive-only semantics).

### Scope fences (do NOT pull forward)

- ❌ The pure-function **verdict gate** (folding the ledger → verdict, the ≥60%/20%-floor thresholds, exit
  codes, finding ordering) — that is **Story 1.6**. This story only delivers the data the gate folds.
- ❌ **`inferred` never satisfies a gate (FR8)** as a GATE behavior — Epic 2 / Story 1.6. Here `inferred` is
  merely a valid enum member.
- ❌ The **readable per-file ledger surface / rendered counts %** (FR9) — Epic 2 (Story 2.2). Here we only
  provide the `counts_by_depth()` accessor the surface will later use.
- ❌ **AST-validating** a deep claim's truth (downgrade an *unverifiable* claim) — Story 1.5 (vacuous-path
  subset) / Story 6.2 (full AST). Here FR6 is *claim-presence* only: silence → shallow.
- ❌ The impure **`.apaa/` writer/reader/paths** + containment — **Story 1.3** (it will reuse
  `lifecycle/workspace_artifact_writer`; do not import it here, this story is pure).
- ❌ The **`LLMRecording`** adapter mapping + the `LLMDispatchPort` — Epic 6 (Story 6.1). The `Recording`
  here is the FROZEN ledger row; the LLM-call DTO is a separate later concern (keep `recording.py` pure).

### Testing standards

- pytest under `tests/apaa/`; test IDs follow `TC-<AREA>-<SEQ>-<SUBSEQ>` — use area `APAA-LEDGER` (e.g.
  `TC-APAA-LEDGER-001-01` …) in test docstrings/ids (Story 1.1 used `APAA-STORE`).
- These are **pure-function / model golden tests** — zero LLM tokens (NFR-D2), no temp dirs for the modules
  under test. Freeze golden canonical strings + `content_hash` as recorded constants so future byte-drift
  fails loudly.
- On Windows, prefix runs with `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on
  cp1252).
- Run: `PYTHONIOENCODING=utf-8 pytest tests/apaa/ -v` (the WHOLE `tests/apaa/` suite, so the 1.1 single-
  serializer AST gate re-runs with the new modules present). All must pass before moving to `review`.
- `mypy` clean on the new modules (per the per-file mypy convention `python run_mypy_per_file.py` or a
  scoped invocation).

### CLAUDE.md §4a follow-up

The §4a APAA Component→Driver row was already added by Story 1.1 (per the placement decision, tied to the
FIRST implementation story). This story does NOT need a new §4a row; if a one-line note is added it must be
additive (e.g. noting `ledger/coverage_ledger.py` + `ledger/recording.py` as the ledger/recording contracts
of the determinism core) and must not rewrite the existing row. Keep it minimal — a new row is not required.

### Project Structure Notes

- Alignment: file paths exactly match `architecture.md` §Project Structure package tree (`ledger/
  coverage_ledger.py`, `ledger/recording.py`). Naming `snake_case.py`, ≤1200 lines (NFR-M1). JSON/enum
  values `snake_case`.
- No conflicts/variances. Judgment calls — all decided above and golden-tested so they are frozen for
  downstream: the exact `CoverageLedgerEntry`/`Recording` field set, the locator-or-reject error type, the
  `entries` sort key, and the `schema_version`-in-hash semantics.
- Scope fence: this story delivers the PURE coverage-ledger + recording models ONLY. The verdict gate (1.6),
  the `.apaa/` write/read shell (1.3), the detectors (1.5), the gate behaviors FR8/FR9, and any LLM/cost
  wiring are explicitly NOT in scope. Build the models complete-at-birth, then stop.

### References

- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Story-1.2 Fixed-enum coverage ledger & frozen recording schema]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#C. Coverage Ledger, Recording Schema & Verdict (determinism core)]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Contract / Format Patterns] (closed coverage enum; finding/recording required fields; locator-or-reject)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Pure/Impure Separation (master rule)]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Determinism Patterns (NFR-P1/D1 — non-negotiable)] (one serializer; no floats; no iteration-order reliance)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Cross-Cutting Concerns #1 recording-producing-closure cache key / #5 producer-side redaction / #6 advisory-by-contract]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#D. Defect Detectors] (every finding carries finding_id + envelope slice + rule/cartridge id + AST span)
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#FR5 fixed-enum coverage ledger / FR6 claim-required audited_deep / FR8 inferred-never-satisfies / FR9 readable surface / FR13 locator-or-reject]
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-1-canonical-serializer-content-hashed-envelope.md] (DONE — store spine to reuse; `extra="forbid"` + golden-constant precedent; `_MODULES_UNDER_GUARD` seed)
- [Source: minions_core/apaa/store/canonical.py] (the single serializer + `CanonicalSerializationError`)
- [Source: minions_core/apaa/store/envelope.py] (`Envelope`, `EnvelopeWriter`, `compute_content_hash`, `GENESIS_PREV_HASH`)
- [Source: minions_core/apaa/__init__.py] (`__version__ = "0.1.0"` — single apaa_version source)
- [Source: CLAUDE.md §3.2 file-size / §3.7 headless-only / §3.8 12-Factor + secret masking]

## Dev Agent Record

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, resumed after an interrupted prior session).

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ -v` → 87 passed (incl. story 1.1 suite +
  `test_canonical_single_serializer.py` AST gate re-run with the new `ledger/` modules present).
- `PYTHONIOENCODING=utf-8 python -m pytest tests/test_import_paths.py -q` → all pass (no flat-stub regression;
  `ledger/` is a sub-package, not a flat singleton).
- `python -m mypy minions_core/apaa/ledger/{coverage_ledger,recording,__init__}.py` → Success: no issues.

### Completion Notes List

- **Resumed session.** Production code (`ledger/__init__.py`, `coverage_ledger.py`, `recording.py`) was
  already complete and well-formed from the interrupted prior session — inspected and verified against all
  ACs; no production changes were required. The missing work was the test suite + the import-isolation
  gate extension, which this session authored.
- **Reuse, no second serializer (AC8).** All round-trip/golden tests route through `store/canonical.dumps`
  + `store/envelope.compute_content_hash` (Story 1.1 spine). The 1.1 single-serializer AST gate stays green.
- **Golden constants frozen** for the populated `CoverageLedger` and `Recording` (canonical string +
  content hash) so future byte-drift fails loudly (NFR-P1). Enum members serialize verbatim as their
  `snake_case` value via `model_dump()` → `canonical.dumps`.
- **Locator-or-reject (AC6):** the `RecordingValidationError` typed error (raised in a `field_validator`) is
  surfaced wrapped inside Pydantic's `ValidationError`; the test asserts the rejection message and that the
  APAA type is a `ValueError` subclass. No silent empty-locator default (`locators` is required).
- **Decision (AC2 evidence-reference):** chose BOTH `claim_present: bool` and `recording_ids: tuple[...]`
  on `CoverageLedgerEntry` (the spec allows either/both) — the gate (FR6) reads `claim_present`, the FR9
  surface reads `recording_ids`. Both reserved at birth per the complete-at-birth contract.

### File List

- `tests/apaa/test_coverage_ledger.py` (NEW)
- `tests/apaa/test_recording_schema.py` (NEW)
- `tests/apaa/test_no_web_imports.py` (UPDATE — extended `_MODULES_UNDER_GUARD`)
- `minions_core/apaa/ledger/__init__.py` (pre-existing from interrupted session; verified)
- `minions_core/apaa/ledger/coverage_ledger.py` (pre-existing; verified)
- `minions_core/apaa/ledger/recording.py` (pre-existing; verified)

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-06-21 | 0.1.0 | Resumed interrupted dev-story: verified the pre-existing pure `ledger/` models, authored `test_coverage_ledger.py` + `test_recording_schema.py` (enum-pin, frozen/extra-forbid, counts, order-independent determinism, silence→shallow, locator-or-reject, additive-field hash invariance, golden round-trip via the 1.1 serializer), extended the import-isolation gate. 87 apaa tests + import-paths green; mypy clean. Status → review. | claude-opus-4-8 |
| 2026-06-21 | 0.1.0 | Senior Developer Review (AI) — adversarial code review (iteration 1). VERDICT: PASS. All 9 ACs verified; 239 apaa+import-paths tests green; single-serializer AST gate holds; purity/headless/no-float invariants confirmed. Status → done. | claude-opus-4-8 (reviewer) |

## Senior Developer Review (AI)

**Reviewer:** claude-opus-4-8 (BMAD adversarial code-review gate)
**Date:** 2026-06-21 · **Iteration:** 1 · **Verdict:** **PASS** → `done`

### Outcome

The PURE coverage-ledger + frozen recording schema is complete-at-birth, correct,
and fully compliant with the determinism spine, headless boundary, and CLAUDE.md
standards. No `decision-needed`, `patch`, High, or Medium findings. Tests green.
Story promoted to `done`.

### Scope & method

Reviewed `minions_core/apaa/ledger/{coverage_ledger.py,recording.py,__init__.py}`
and `tests/apaa/{test_coverage_ledger.py,test_recording_schema.py,test_no_web_imports.py}`
against the 9 ACs (APAA-FR-5/6/13-support, NFR-D2/M1/M2, AR8/AR10), correctness,
determinism, security (source/secret leakage), and engineering principles. Ran the
three adversarial layers (Blind Hunter / Edge Case Hunter / Acceptance Auditor) and
independently re-ran the suite + the Story 1.1 single-serializer AST gate.

### AC-by-AC verification (Acceptance Auditor)

- **AC1** ✅ `CoverageDepth(str, enum.Enum)` — exactly five members with the exact
  `snake_case` values; membership + value sets pinned by committed tests (closed enum).
- **AC2** ✅ `CoverageLedgerEntry` frozen `extra="forbid"`; carries `file_path`,
  `depth`, `claim_present`, `recording_ids`, `partition_id="root"`. Extra-field
  read-back is a typed `ValidationError`.
- **AC3** ✅ `CoverageLedger.build(...)` canonicalizes `entries` to `file_path`-sorted
  tuple; order-independent equality + byte-identical `canonical.dumps` confirmed;
  `counts_by_depth()` is pure, zero-filled for every member.
- **AC4** ✅ `grade_entry` downgrades claimless `AUDITED_DEEP`→`AUDITED_SHALLOW`,
  leaves all other depths untouched, and (verified adversarially) never auto-upgrades
  shallow→deep. Pure, both directions unit-tested.
- **AC5** ✅ `Recording` frozen `extra="forbid"`; reserves `recording_id`/`finding_id`,
  `partition_id`, `rule_id`, `cartridge_id`, `advisory`, `locators`, `depth_supported`,
  `claim_present`, `coverage_envelope_slice`, `schema_version`. Additive-only.
- **AC6** ✅ Empty `locators` raises `RecordingValidationError` (a `ValueError`
  subclass, surfaced wrapped in Pydantic `ValidationError`); `locators` is required
  (no silent empty default); `Locator` enforces `start_line<=end_line`, lines ≥1.
- **AC7** ✅ No FS I/O, clock, `uuid`/`random`/`os.getpid`, LLM/network, or `float`
  field in either module (grep + clean canonical round-trip confirm); counts are `int`.
- **AC8** ✅ Golden canonical strings + `compute_content_hash` frozen for both models;
  `loads(dumps(model_dump))` fully reconstructs nested `Locator`/enum members equal to
  the original; REUSES `store/canonical` + `store/envelope` — the 1.1 single-serializer
  AST gate (`test_canonical_single_serializer.py`) stays green with the new modules present.
- **AC9** ✅ Both new modules appended to `_MODULES_UNDER_GUARD`; clean-subprocess import
  shows no `fastapi`/`uvicorn`/`starlette` leakage.

### Adversarial findings (Blind Hunter / Edge Case Hunter)

None of consequence. Notes (all non-blocking, no action required):

- The `recording_id` docstring describes it as "content-derived", but the model only
  *stores* a caller-supplied id (no derivation logic) — this is correct for this PURE
  story (derivation is a producer/cache-key concern for Epic 5/6); the wording is
  accurate as "a.k.a. finding_id". No change needed.
- `counts_by_depth()` returns a `dict`; the dict's iteration order is insertion order
  over the enum, which is deterministic, and the result is never serialized (only the
  sorted `entries` tuple is) — so AR4/no-iteration-order-reliance is not violated.

### Engineering-principle check

SRP/DIP respected (pure models + free functions, no hidden deps); no premature
abstraction; reuse-canonical (single serializer honored — no fork); tests are
deterministic golden/property tests, not implementation-coupled. Files 182/144 lines
(well under the 1200 limit). No secret/source-bytes surface (pure in-memory models).

### Tests

`PYTHONIOENCODING=utf-8 pytest tests/apaa/ tests/test_import_paths.py` → **239 passed**
(incl. the 1.1 suite + single-serializer AST gate). APAA `sprint-status.yaml` parses
cleanly (no worktree corruption); diff scope confined to APAA.

### Action Items

None. No `### Review Findings` block is emitted (clean pass).
