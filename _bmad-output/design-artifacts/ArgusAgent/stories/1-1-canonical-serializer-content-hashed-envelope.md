# Story 1.1: Canonical serializer & content-hashed envelope

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
I want a single canonical JSON serializer and a content-hashed, schema-versioned, prev-hash-chained envelope,
so that every `.apaa/` artifact is byte-reproducible across hosts and tamper-evident — the determinism keystone every later epic folds over.

## Story Context

This is **Story 1 of Epic 1** (Signature-Demo Vertical Slice) and the **very first APAA implementation
story**. There is no previous APAA story to learn from; the package shell `minions_core/apaa/__init__.py`
already exists (reserved, docstring only — confirmed present). This story lays the **determinism spine**:
the single canonical serializer + the content-hashed envelope. Per the architecture's explicit
implementation sequence, this is the first link — *"envelope + canonical serializer + fixed-enum ledger
(C-core) → AST index ... → pure verdict ... → 🔴 on the cartridge"*. Stories 1.2 (ledger/recording schema),
1.3 (`.apaa/` writer/reader), and every artifact-producing module downstream depend on the serializer and
envelope this story delivers.

**Why this matters (architecture cross-cutting concern #3):** NFR-P1 (sequential byte-identical to
parallel) *"dies the day a second `json.dumps` appears with different kwargs."* The single serializer +
the float/clock/uuid prohibitions are the byte-diff landmine defenses. Get this wrong and the entire
reproducibility promise (D1/D3/P1/A1) is unfounded.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 1.1) and the architecture (Decision C, §Determinism Patterns,
> §Contract/Format Patterns). Drivers: **APAA-FR-25** (content-hashed, schema-versioned envelope),
> **APAA-NFR-A1** (schema-versioned, content-hashed, prev-hash-chained, additive-only envelope),
> **APAA-NFR-D3** (hashes cover canonical payload only, exclude volatile `run_id`/`created_at`),
> **APAA-NFR-P1** (byte-identical on-disk state across hosts), **APAA-NFR-M1/M2** (≤1200-line files,
> additive-only frozen contracts), **AR4** (single canonical serializer), **AR10** (typed failure, never
> uncaught raise).

**AC1 — Single canonical serializer (FR25-support, NFR-P1, AR4)**
**Given** any JSON-serializable payload
**When** it is serialized through `apaa/store/canonical.py`
**Then** the output is produced by exactly `json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)` and is `\n`-terminated, encoded UTF-8
**And** the function round-trips: `loads(dumps(x))` equals `x` for all supported inputs.

**AC2 — No competing serializer in any `.apaa/` write path (NFR-P1, AR4, enforcement)**
**Given** the APAA codebase
**When** a committed lint/test scans `minions_core/apaa/` for direct `json.dumps(` / `json.dump(` calls outside `store/canonical.py`
**Then** any direct call in an `.apaa/` write path is rejected (the test fails), so `canonical.dumps(...)` is the only serialization entry point.

**AC3 — Forbidden non-deterministic inputs are rejected before any write (AR4, NFR-P1)**
**Given** a payload containing a Python `float`, a `datetime`/wall-clock value, a `uuid.UUID`, or a `set`
**When** it is routed toward an `.apaa/` write via the canonical serializer
**Then** the serializer raises a typed `CanonicalSerializationError` (a `ValueError` subclass) naming the offending field/type — it does NOT silently coerce
**And** ratios/scores must be supplied as fixed-precision `Decimal` or an exact `Fraction` and are serialized as a stable string form (never a binary float). `datetime.now`/`time.time`/`uuid4`/`os.getpid()`/`random`/dict-or-set-iteration-order reliance are forbidden in the write path.

**AC4 — Content-hashed, schema-versioned, prev-hash-chained envelope (FR25, NFR-A1, NFR-D3)**
**Given** an artifact wrapped by the `EnvelopeWriter` (pure builder)
**When** the envelope is built
**Then** `content_hash` is a sha256 over the **canonical payload only** (excludes the volatile `run_id` and `created_at` fields), `prev_hash` chains to the prior artifact's `content_hash` (or a fixed genesis sentinel for the first), and `schema_version` + `producer` + `apaa_version` fields are present
**And** the envelope schema is a frozen Pydantic v2 contract that evolves additive-only (`schema_version` bump; new fields optional only) — NFR-M2.

**AC5 — Cross-host byte-identical content hash (NFR-P1, golden test, gates downstream)**
**Given** two identical input payloads serialized on two different hosts (simulated by independent serializer invocations + a recorded golden hash)
**When** their canonical bytes and `content_hash` values are compared in a golden test
**Then** they are byte-identical
**And** the same input that differs only in `run_id`/`created_at` produces an identical `content_hash` (NFR-D3 — volatile fields excluded from the hash).

**AC6 — Pure / zero-I/O / zero-token (AR8, NFR-D2)**
**Given** `store/canonical.py` and `store/envelope.py`
**When** they are imported and exercised
**Then** they perform NO filesystem I/O, NO clock read, NO LLM call, NO network — they are pure functions over in-memory payloads (the impure `.apaa/` write shell is Story 1.3, deliberately not in this story).

**AC7 — Import isolation holds (AR7/AR9, headless boundary)**
**Given** the APAA modules added by this story
**When** `tests/apaa/test_no_web_imports.py` runs (seed it in this story if absent)
**Then** importing `minions_core.apaa.store.canonical` and `minions_core.apaa.store.envelope` does NOT transitively import `fastapi` / `uvicorn` / `starlette` (assert absence from `sys.modules`).

## Tasks / Subtasks

- [x] **Task 1 — Create the `store/` sub-package + canonical serializer** (AC: 1, 3, 6)
  - [x] Create `minions_core/apaa/store/__init__.py` (package marker; no logic).
  - [x] Create `minions_core/apaa/store/canonical.py` with module docstring citing `APAA-NFR-P1`, `APAA-NFR-D3`, `AR4`.
  - [x] Implement `dumps(payload) -> str`: `json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)` + trailing `\n`.
  - [x] Implement `dumps_bytes(payload) -> bytes` (UTF-8 encode of `dumps`) for hashing — single encode point so hashing and writing share bytes.
  - [x] Implement `loads(text) -> object` (thin `json.loads` wrapper for the round-trip + reader reuse; also accepts `bytes`).
  - [x] Define `class CanonicalSerializationError(ValueError)`.
  - [x] Add a pre-serialization validator (`canonicalize`) that walks the payload and raises `CanonicalSerializationError` on `float`, `datetime`/`date`/`time`, `uuid.UUID`, `set`/`frozenset`, non-string dict keys, and any non-JSON-primitive leaf — naming the offending type/path (`$.field[i]`). Accepts `Decimal`/`Fraction` only via a frozen deterministic string encoding (`Decimal` → `format(d.normalize(), 'f')`; `Fraction` → `"num/den"`) — documented in the docstring.
- [x] **Task 2 — Content-hashed envelope builder** (AC: 4, 6)
  - [x] Create `minions_core/apaa/store/envelope.py` (docstring cites `APAA-FR-25`, `APAA-NFR-A1`, `APAA-NFR-D3`).
  - [x] Define a frozen Pydantic v2 `Envelope` model (`frozen=True, extra="forbid"`): `schema_version`, `producer`, `apaa_version`, `content_hash`, `prev_hash`, `payload`, plus volatile `run_id: str | None`, `created_at: str | None` (volatile fields excluded from the hash).
  - [x] Implement `compute_content_hash(payload) -> str` = `sha256(canonical.dumps_bytes(payload)).hexdigest()` over the canonical payload ONLY.
  - [x] Implement `EnvelopeWriter.build(...)` — PURE builder; `prev_hash` defaults to `GENESIS_PREV_HASH = "0" * 64` for the chain head.
  - [x] `apaa_version` sourced from the single APAA-owned constant `minions_core/apaa/__init__.py::__version__` (default arg); no literal at call sites; not read from env/clock.
- [x] **Task 3 — Enforcement: no-second-serializer lint test** (AC: 2)
  - [x] Added `tests/apaa/test_canonical_single_serializer.py` — AST scan of every `.py` under `minions_core/apaa/` (allow-list: only `store/canonical.py`) detecting `json.dumps(`/`json.dump(` (attribute form) AND `from json import dumps`-bound bare calls; fails on any hit. AST avoids docstring/comment false positives. Negative-control verified.
- [x] **Task 4 — Determinism golden tests** (AC: 1, 3, 4, 5, 6)
  - [x] `tests/apaa/test_canonical_determinism.py`: round-trip; key-order independence; FROZEN golden canonical string + golden `content_hash`; reject-float/datetime/date/uuid/set/frozenset/non-finite-Decimal/non-string-key/arbitrary-object; `Decimal`/`Fraction` stable-string encoding.
  - [x] Envelope tests: `content_hash` excludes `run_id`/`created_at`; `prev_hash` chains; golden `content_hash`; additive-optional-field-does-not-change-hash; frozen-model immutability; envelope round-trips through the canonical serializer.
  - [x] Purity: tests use no temp files / no clock for the modules under test.
- [x] **Task 5 — Import-isolation gate** (AC: 7)
  - [x] Created `tests/apaa/test_no_web_imports.py`: imports `...store.canonical` + `...store.envelope` in a CLEAN subprocess and asserts `fastapi`/`uvicorn`/`starlette` absent from `sys.modules`. Seeded `_MODULES_UNDER_GUARD` tuple for later stories to extend (AR9).
- [x] **Task 6 — Test scaffold + run** (AC: all)
  - [x] Created `tests/apaa/__init__.py`.
  - [x] Ran `PYTHONIOENCODING=utf-8 pytest tests/apaa/ -v` → 39 passed; `mypy` clean on the three new/edited modules.

### Review Findings

> Code-review iteration 1 (2026-06-21). VERDICT pass. All findings below are
> Low-severity / optional polish — none block `done`; recorded so a later
> hardening story can pick them up. No `decision-needed` or `patch` items.

- [ ] [Review][Low] AC2 scanner covers only `json.dumps`/`json.dump` — other serializers (`pickle`, `yaml.dump`, `orjson`, `marshal`) are not in the no-second-serializer gate. In-scope for this story (the AC names `json` explicitly), but a future `.apaa/` write-path story may widen the gate to keep the single-bytes-source invariant airtight. [tests/apaa/test_canonical_single_serializer.py]
- [ ] [Review][Low] `canonicalize` recurses without an explicit depth guard; a pathologically deep author-constructed payload could hit Python's recursion limit and raise `RecursionError` rather than a typed `CanonicalSerializationError`. Inputs here are author-controlled audit data (not untrusted), so Low — but the 17-1 lineage precedent shows the project prefers iterative walks for unbounded structures; consider an iterative rewrite or depth cap if `.apaa/` payloads ever grow deeply nested. [minions_core/apaa/store/canonical.py:96]
- [x] [Review][Dismiss] `loads(dumps(x))` is asymmetric for `Decimal`/`Fraction` (they round-trip back as their canonical string form) — this is documented and intentional (stored-as-string by design); not a defect.

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **Pure/impure separation (master rule, AR8).** `canonical.py` and `envelope.py` are **PURE** — no I/O,
  no clock, no LLM, no network. The impure `.apaa/` write shell (`store/writer.py`, `store/paths.py`,
  `store/reader.py`) is **Story 1.3**, NOT this story. Do not pre-build it here. ✅ `canonical.dumps(payload)`
  · ❌ `canonical.py` opening a file or reading `datetime.now()`.
- **One serializer, forever (AR4 / cross-cutting #3).** All `.apaa/` JSON MUST go through
  `apaa/store/canonical.py`. The exact kwargs are non-negotiable:
  `json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)` + a trailing `\n`,
  UTF-8. The no-second-serializer test (Task 3) is the durable enforcement.
- **Forbidden in any `.apaa/` write path** (architecture §Determinism Patterns): wall-clock
  (`datetime.now`/`time.time`), `uuid4`, `os.getpid()`, `random`, dict/`set`-iteration-order reliance,
  and **float scores**. Ratios/scores are stored as fixed-precision `Decimal`/exact `Fraction` — *floats
  are an NFR-P1 byte-diff landmine across hosts (R4, red-team)*. The serializer is the choke point that
  rejects these (AC3) so a downstream author cannot accidentally leak one in.
- **Hash covers the canonical payload ONLY (NFR-D3).** `content_hash = sha256(canonical bytes of payload)`.
  Volatile fields `run_id` and `created_at` live on the envelope but are EXCLUDED from the hash — otherwise
  two identical audits on two hosts (different run ids/timestamps) would diff, breaking NFR-P1/D1.
- **Envelope = frozen, additive-only contract (NFR-A1/NFR-M2).** Pydantic v2 `model_config =
  ConfigDict(frozen=True)`. Schema evolution is additive-only: bump `schema_version`, add OPTIONAL fields
  only — never remove/rename/retype an existing field. A new optional field must not change an existing
  payload's `content_hash` (test it).
- **prev-hash chaining (NFR-A1, ADR #18 patterns by import-spirit).** Each envelope's `prev_hash` is the
  prior envelope's `content_hash`; the chain head uses a fixed genesis sentinel (`"0" * 64`). This mirrors
  the Minions hash-chained ledger (`minions_core/governance/ledger.py`) conceptually — but APAA does NOT
  fork or import the Minions ledger for this story; the envelope is APAA-owned and self-contained.
- **Error/degradation (AR10, NFR-R1).** Failure → a typed exception (`CanonicalSerializationError`,
  `ValueError` subclass) at this pure layer; NO bare `except: pass`, NO `print()` in library code. The
  typed-finding-instead-of-crash pipeline behavior is later stories (1.7); here the contract is "reject
  with a typed, named error," never silently coerce or emit non-canonical bytes.
- **Headless / boundary (architecture §Architectural Boundaries).** APAA is downstream of the HTTP/A2A
  boundary — these modules take no token, register no FastAPI route, and must not import the web stack
  (AC7 / AR7). Never import `minions_core.api.* / services.api_app / app_factory / api_server`.

### Source tree — files to create (all NEW; nothing to UPDATE except possibly `__init__.py`)

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/store/__init__.py` | NEW | `store` sub-package marker |
| `minions_core/apaa/store/canonical.py` | NEW | THE single serializer + `CanonicalSerializationError` (PURE) |
| `minions_core/apaa/store/envelope.py` | NEW | `Envelope` model + `EnvelopeWriter` + `compute_content_hash` (PURE) |
| `minions_core/apaa/version.py` *(or extend `__init__.py`)* | NEW/UPDATE | single `apaa_version` constant source |
| `tests/apaa/__init__.py` | NEW (if absent) | test package marker |
| `tests/apaa/test_canonical_determinism.py` | NEW | golden serializer + envelope determinism |
| `tests/apaa/test_canonical_single_serializer.py` | NEW | no-second-`json.dumps` enforcement |
| `tests/apaa/test_no_web_imports.py` | NEW (seed) | import-isolation gate (AR9, durable) |

`minions_core/apaa/__init__.py` already exists (reserved shell). The architecture's package tree
(`architecture.md` §Project Structure) places exactly these files under `store/`; do NOT invent additional
modules. Tier-B / later modules (`store/paths.py`, `store/writer.py`, `store/reader.py`) are explicitly
out of scope here.

### Reuse — what already exists (verified present) and what NOT to reinvent

- **Workspace containment** (`minions_core/lifecycle/workspace_artifact_writer.py` — verified FastAPI-free,
  `is_relative_to`-based, raises `WorkspaceContainmentError`). This is the pattern Story **1.3** reuses for
  `.apaa/` write containment — **NOT this story** (this story is pure, no FS writes). Do not import it here;
  noted so the next story author knows it exists and must not reinvent containment.
- **Hash-chained ledger** (`minions_core/governance/ledger.py` — verified present). Conceptual precedent
  for `prev_hash` chaining; APAA's envelope is self-contained and does not import it for V1.
- **Pydantic v2** is already a Minions baseline dependency — use `from pydantic import BaseModel,
  ConfigDict`; do not add a new dependency. `jsonschema`/`tree-sitter`/`radon` are NOT needed for this
  story (they arrive in Stories 1.4+).

### Determinism encoding decisions the dev must lock (record the choice in the docstring)

- **`Decimal`/`Fraction` encoding:** pick ONE deterministic string form (recommended: `Decimal` →
  `format(d.normalize(), 'f')` or a canonical `str` that is stable across hosts; `Fraction` →
  `f"{f.numerator}/{f.denominator}"`). Whatever is chosen, golden-test it (AC4) so it is frozen.
- **Genesis `prev_hash` sentinel:** `"0" * 64` (64-char zero sha256) — document it as the chain-head marker.
- **`content_hash` algorithm:** `sha256` hexdigest over `canonical.dumps_bytes(payload)`. Use the SAME
  `dumps_bytes` the writer would use so hashed bytes == written bytes (single source of truth).

### Testing standards

- pytest under `tests/apaa/`; test IDs follow the project convention `TC-<AREA>-<SEQ>-<SUBSEQ>` — use area
  `APAA-STORE` (e.g. `TC-APAA-STORE-001-01` … in test docstrings/ids).
- These are **pure-function golden tests** — zero LLM tokens (NFR-D2), no temp dirs for the modules under
  test. Golden values (canonical string, `content_hash`) are recorded constants so a future byte-drift
  fails loudly.
- On Windows, prefix runs with `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on
  cp1252).
- Run: `PYTHONIOENCODING=utf-8 pytest tests/apaa/ -v`. All must pass before moving to `review`.

### CLAUDE.md §4a follow-up (do in this story per the placement decision)

The APAA placement decision says: *once stories land, add APAA as a Component → Driver Map row and note
the `apaa/` sub-package — tied to the FIRST implementation story.* This IS the first story. Add a brief
APAA row/note to CLAUDE.md §4a (component: APAA audit sub-tool; module root `minions_core/apaa/`; drivers
`APAA-FR-*`/`APAA-NFR-*`) and note `store/canonical.py` + `store/envelope.py` as the determinism spine.
Keep it additive — do not rewrite existing §4a rows.

### Project Structure Notes

- Alignment: file paths exactly match `architecture.md` §Project Structure package tree. Naming is
  `snake_case.py`, ≤1200 lines (NFR-M1). JSON fields `snake_case` (NFR/Pydantic convention).
- No conflicts/variances. The only judgment call is the `Decimal`/`Fraction` string encoding and the
  genesis sentinel — both decided above and golden-tested so they are frozen for downstream stories.
- Scope fence: this story delivers the PURE serializer + envelope only. The impure `.apaa/` write/read
  shell (1.3), the fixed-enum ledger + recording schema (1.2), and any LLM/cost wiring are explicitly NOT
  in scope. Resist building ahead.

### References

- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Story-1.1 Canonical serializer & content-hashed envelope]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#C. Coverage Ledger, Recording Schema & Verdict (determinism core)]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Determinism Patterns (NFR-P1/D1 — non-negotiable)]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Contract / Format Patterns] (envelope: content-hash over payload-only, prev_hash chaining, one EnvelopeWriter)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Cross-Cutting Concerns #3 Envelope canonicalization / single serializer]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#AR4 Single canonical serializer / AR8 Pure-impure separation / AR9 committed CI gates / AR10 typed failure]
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#FR25 content-hashed schema-versioned envelope / NFR-A1 / NFR-D3 / NFR-P1]
- [Source: minions_core/lifecycle/workspace_artifact_writer.py] (containment pattern — reused in Story 1.3, not here)
- [Source: minions_core/governance/ledger.py] (hash-chain precedent)
- [Source: CLAUDE.md §3.2 file-size / §3.7 headless-only / §3.8 12-Factor]

## Dev Agent Record

### Agent Model Used

claude-opus-4-8[1m] (BMAD dev-story worker)

### Debug Log References

- `PYTHONIOENCODING=utf-8 pytest tests/apaa/ -v` → 39 passed in ~0.7s.
- `mypy minions_core/apaa/store/canonical.py minions_core/apaa/store/envelope.py minions_core/apaa/__init__.py` → Success, no issues.
- `pytest tests/test_import_paths.py -q` → green (apaa is a sub-package; §4a flat-file allow-list unaffected).
- Negative control: the single-serializer AST scanner detects both `json.dumps(...)` and `from json import dumps as d; d(...)`.

### Completion Notes List

- **Determinism spine landed (PURE — AR8).** `store/canonical.py` is the single canonical serializer:
  `json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)` + trailing `\n`, UTF-8;
  `dumps_bytes` is the single encode point shared by hashing and (future) writing.
- **Frozen encoding decisions (golden-tested, so they cannot drift):** `Decimal` → `format(d.normalize(), 'f')`
  (no exponent, trailing-zero-normalized; NaN/Infinity rejected); `Fraction` → `"numerator/denominator"`
  (reduced); genesis `prev_hash` sentinel = `"0" * 64`; `content_hash` = `sha256(dumps_bytes(payload))` over the
  **payload only**. Golden canonical string + golden `content_hash` recorded as frozen constants.
- **NFR-D3 verified:** two envelopes differing only in `run_id`/`created_at` share an identical `content_hash`.
- **AR4 enforcement** seeded as a committed AST gate (no second `json.dumps` in any `.apaa/` write path).
- **AR9 import-isolation** seeded (subprocess clean-`sys.modules` assertion; `fastapi`/`uvicorn`/`starlette` absent).
- **Design decision:** `Envelope` uses `extra="forbid"` (additive-only contract is strict — an unknown field on a
  read-back is a typed error, not silent acceptance). This is stricter than the story's literal spec and supports the
  NFR-M2 "never retype/rename" invariant; the round-trip test confirms it does not break serialize→deserialize.
- **Scope fence honored:** no FS/clock/LLM/network; the impure `.apaa/` write shell (writer/paths/reader) is Story 1.3
  and was deliberately NOT built. CLAUDE.md §4a APAA row added per the placement-decision follow-up (additive).

### File List

- `minions_core/apaa/__init__.py` (MODIFIED — added `__version__ = "0.1.0"` single source for `apaa_version`)
- `minions_core/apaa/store/__init__.py` (NEW — store sub-package marker)
- `minions_core/apaa/store/canonical.py` (NEW — THE single canonical serializer + `CanonicalSerializationError`)
- `minions_core/apaa/store/envelope.py` (NEW — `Envelope` model + `EnvelopeWriter` + `compute_content_hash` + `GENESIS_PREV_HASH`)
- `tests/apaa/__init__.py` (NEW — test package marker)
- `tests/apaa/test_canonical_determinism.py` (NEW — golden serializer + envelope determinism)
- `tests/apaa/test_canonical_single_serializer.py` (NEW — AR4 no-second-serializer AST gate)
- `tests/apaa/test_no_web_imports.py` (NEW — AR9 import-isolation gate, seeded)
- `CLAUDE.md` (MODIFIED — additive §4a APAA Component→Driver row)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (MODIFIED — status → review; last_updated 2026-06-21)

## Change Log

| Date | Change |
|---|---|
| 2026-06-21 | Story 1.1 implemented: PURE canonical serializer + content-hashed/schema-versioned/prev-hash-chained envelope under `minions_core/apaa/store/`. 39 tests green (golden determinism + AR4 single-serializer AST gate + AR9 import-isolation gate). mypy clean. AC1–AC7 satisfied. Status → review. |
| 2026-06-21 | Senior Developer Review (AI) — VERDICT pass. 39/39 tests green (independently re-run); golden content_hash independently recomputed and confirmed; mypy clean on the 3 modules. AC1–AC7 all met. Only Low/optional cleanups (no blockers). Status review → done. |

## Senior Developer Review (AI)

**Reviewer:** BMAD Reviewer / QA gate (adversarial code-review, iteration 1)
**Date:** 2026-06-21
**Outcome:** **PASS** — status `review → done`.

### Scope reviewed
PURE store spine: `minions_core/apaa/store/canonical.py`, `minions_core/apaa/store/envelope.py`,
`minions_core/apaa/store/__init__.py`, `minions_core/apaa/__init__.py` (`__version__` addition),
tests under `tests/apaa/`, and the additive CLAUDE.md §4a APAA row. Drivers: APAA-FR-25,
APAA-NFR-A1/D2/D3/P1/M1/M2; AR4/AR8/AR9/AR10.

### Verification performed (independent)
- `PYTHONIOENCODING=utf-8 pytest tests/apaa/ -v` → **39 passed in 0.68s** (re-run by reviewer).
- `mypy minions_core/apaa/store/canonical.py minions_core/apaa/store/envelope.py minions_core/apaa/__init__.py`
  → **Success, no issues** (3 files).
- Golden `content_hash` recomputed independently from the canonical bytes →
  `e92e7a08d90c60a840baf8e3e1de2870138db158df0095e2269cb734d1c1352b` (matches the frozen golden).
- Adversarial edge probes (not all in the suite, all behaved correctly): NaN/Inf float rejected;
  `bytes`/`complex`/arbitrary-object leaves rejected with accurate `$.path` naming; bool dict-key
  rejected (bool-is-int-subclass ordering correct); nested non-string key path naming correct;
  `Decimal('-0')`/`-0.5`/`1E-7`/`1E+30` all render in plain (no-exponent) notation; nested-dict
  key-order content-hash stability confirmed; non-dict payload to `EnvelopeWriter.build` rejected by
  Pydantic (typed failure, AR10); tuple and list serialize byte-identically.

### Acceptance-criteria audit
| AC | Verdict | Evidence |
|---|---|---|
| AC1 single canonical serializer (exact kwargs, `\n`, UTF-8, round-trip) | ✅ | `test_exact_kwargs_*`, `test_round_trip_primitives`, `test_non_ascii_not_escaped` |
| AC2 no second serializer (committed AST scan + allow-list) | ✅ | `test_no_second_json_serializer_in_apaa_write_path`, guard-the-guard `test_allow_list_module_exists` |
| AC3 forbidden inputs rejected (typed, no coercion); Decimal/Fraction string | ✅ | `TestForbiddenInputs`, `TestExactNumericEncoding`; `CanonicalSerializationError(ValueError)` |
| AC4 content-hash over payload only, prev-hash chain, schema fields, frozen Pydantic | ✅ | `compute_content_hash`, `test_prev_hash_chains`, `test_envelope_is_frozen`; `frozen=True, extra="forbid"` |
| AC5 cross-host byte-identical hash; volatile fields excluded | ✅ | `test_content_hash_golden_frozen`, `test_content_hash_excludes_volatile_fields` |
| AC6 pure / zero-I/O / zero-token | ✅ | source read confirms no FS/clock/LLM/network; import-isolation subprocess |
| AC7 import isolation (no fastapi/uvicorn/starlette) | ✅ | `tests/apaa/test_no_web_imports.py` (clean-subprocess `sys.modules` assertion) |

### Engineering-principle check
- AR8 pure/impure separation: honored — modules import only stdlib + pydantic + `apaa.__version__`.
- AR4 single-serializer choke point: enforced by committed AST gate (durable, not reviewer-vigilance).
- AR10 typed failure: `CanonicalSerializationError` (ValueError subclass) on every reject path; no
  bare `except`, no `print` in library code.
- §3.2 file size: both modules well under 1200 lines. §3.7 headless: no web surface. §3.8: `__version__`
  is a constant, not env/clock-derived. No speculative abstraction; reuse-by-import respected (no fork of
  the Minions ledger).

### Review Findings (Low / optional — none blocking; left for a future story's consideration)
See `### Review Findings` under Tasks/Subtasks. All triaged Low; none gate `done`.
