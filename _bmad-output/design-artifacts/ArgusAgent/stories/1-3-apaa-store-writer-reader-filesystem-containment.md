# Story 1.3: `.apaa/` store writer & reader with filesystem containment

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
I want the impure `.apaa/` writer/reader shell with reused workspace containment,
so that all on-disk state lands inside the audited repo's `.apaa/` tree and nothing can escape it — the
THIRD link in the determinism spine (the first IMPURE one).

## Story Context

This is **Story 3 of Epic 1** (Signature-Demo Vertical Slice). It builds directly on:
- **Story 1.1 (done)** — the PURE determinism spine under `minions_core/apaa/store/`: the single canonical
  serializer (`store/canonical.py`: `dumps`/`dumps_bytes`/`loads`/`canonicalize` + `CanonicalSerializationError`)
  and the content-hashed, schema-versioned, prev-hash-chained envelope (`store/envelope.py`: `Envelope`,
  `EnvelopeWriter.build`, `compute_content_hash`, `GENESIS_PREV_HASH`).
- **Story 1.2 (done)** — the PURE fixed-enum coverage ledger (`ledger/coverage_ledger.py`: `CoverageDepth`,
  `CoverageLedgerEntry`, `CoverageLedger`, `grade_entry`) and the frozen recording schema
  (`ledger/recording.py`: `Locator`, `Recording`, `RecordingValidationError`).

Stories 1.1 and 1.2 are **deliberately PURE** — they take no I/O, no clock, no LLM. They each carry an
explicit scope fence stating *"the impure `.apaa/` write/read shell is Story 1.3."* **This story is that
shell.** It is the FIRST impure module in the APAA package: the edge that turns the pure in-memory models
(envelope-wrapped payloads, ledger snapshots, recordings) into real bytes on disk under the audited repo's
`.apaa/` tree, and reads them back, validating + round-tripping byte-identically.

Per the architecture's implementation sequence (*"envelope + canonical serializer + fixed-enum ledger
(C-core) → AST index → pure verdict → 🔴 on the cartridge"*) and Decision **F (Persistence & State)**, the
store shell is the persistence substrate every later impure module folds over: Story 1.4's repo intake reads
the tree, Story 1.6's verdict folds a ledger it loaded from disk, Story 1.7's CLI/pipeline writes the
findings + verdict artifacts and re-reads them for the byte-identical-twice determinism AC, and Epic 3's
resumability (FR31) re-loads the `.apaa/` state to resume. **`store/reader.py` is the resumability seam**
(architecture §FR-cluster → location: "Invocation & Resumability → `store/reader.py`").

**Why filesystem containment is the security keystone (architecture cross-cutting #5, §Security/Containment
Patterns, NFR-S5):** APAA writes into a tree (`.apaa/`) rooted INSIDE a repository it does not control —
including, on the operated-service path, a customer's repo. A path-traversal / symlink-escape / absolute-path
/ sibling-prefix bug at this exact seam would let an audit write outside its sandbox (corrupting the host
repo or escaping onto the host filesystem). The architecture mandates reuse of Minions'
`lifecycle/workspace_artifact_writer` containment pattern — **real `Path.resolve()` + `is_relative_to`,
NEVER `str.startswith`** — raising a typed `WorkspaceContainmentError` BEFORE any write. This story mirrors
that rigor exactly, with property tests for every escape vector.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 1.3) and the architecture (Decision F §Persistence & State,
> §Security/Containment Patterns, §Pure/Impure Separation, §Error/Degradation Patterns, AR11). Drivers:
> **APAA-NFR-S5** (all FS writes containment-checked — `is_relative_to`, no traversal/symlink/sibling-prefix
> escape), **APAA-FR-31** (resumability — reader deserializes/validates `.apaa/` state), **APAA-FR-25 /
> NFR-A1** (writes go through the content-hashed envelope), **APAA-NFR-P1** (byte-identical on-disk state via
> the single serializer), **AR4** (single canonical serializer — no second `json.dumps`), **AR7** (reuse
> Minions leaf modules by import — `lifecycle/workspace_artifact_writer`; never import the web stack),
> **AR8** (pure/impure separation — `writer`/`paths` are the IMPURE shell, `reader` deserialize/validate is
> PURE), **AR10** (typed failure at the impure shell — reuse `WorkspaceContainmentError`; no bare
> `except: pass`, no `print()` in library code), **AR11** (the fixed `.apaa/` tree; filenames from
> content-sha256 or stable assignment-id, never arrival order), **APAA-NFR-M1** (≤1200-line files).
>
> **SCOPE FENCE.** This story delivers ONLY the on-disk write/read shell + path resolver + containment. It
> does NOT build: the verdict gate (Story 1.6), repo intake / AST index (Story 1.4), detectors (Story 1.5),
> the cache/memo store (`cache/memo_store.py`, Epic 5 — `.apaa/cache/` is created as a tree directory but the
> memoization LOGIC is Epic 5), resume ORCHESTRATION (re-driving a partial audit — Epic 3 / Story 3.4; this
> story provides only the read-back primitive the resume will use), the LLM adapter, or any CLI wiring.

**AC1 — `.apaa/` path resolver with containment (NFR-S5, AR11, AR7) — the security keystone**
**Given** a write targeting the `.apaa/` tree, addressed by an audited-repo root + a `.apaa/`-relative
sub-path (e.g. `state/<sha>.json`)
**When** the path is resolved by `store/paths.py`
**Then** the candidate path is resolved via real `Path.resolve()` (which normalises `..` and follows
symlinks) and asserted `is_relative_to` the resolved `.apaa/` root (NEVER a `str.startswith` prefix check),
mirroring `lifecycle/workspace_artifact_writer.WorkspaceArtifactWriter._is_contained`
**And** an escape — `../` traversal, an absolute sub-path, a `..`-only segment, a symlink whose target
escapes the root, a sibling-prefixed sibling dir (`.apaa-evil` vs `.apaa`), a Windows-backslash traversal,
or a drive-letter absolute — raises a typed `WorkspaceContainmentError` **BEFORE any filesystem mutation**
(no partial write, no directory creation on the escaping path).

**AC2 — Reuse the Minions containment helper / typed error (AR7, AR10, §3.3 no-fork)**
**Given** the containment requirement
**When** `store/writer.py` and `store/paths.py` are implemented
**Then** they REUSE `minions_core.lifecycle.workspace_artifact_writer` by import — either delegating to
`WorkspaceArtifactWriter` with the `.apaa/` root injected, OR (if root injection is unsupported for the
`.apaa/`-rooted shape) re-using its `WorkspaceContainmentError` typed error and its exact
`Path.resolve()` + `is_relative_to` containment LOGIC — with no second/divergent containment implementation
and no fork of the helper (§3.3 reuse-canonical). The thin-wrap rationale (architecture Decision F:
"thin-wrap if root injection is unsupported") is recorded in the module docstring.
**And** the import-isolation gate still holds: importing the new store modules does NOT transitively pull
`fastapi`/`uvicorn`/`starlette` (`lifecycle/workspace_artifact_writer` is pathlib-only / FastAPI-free —
verified in the architecture cross-cutting #7).

**AC3 — The fixed `.apaa/` tree + content-addressed filenames (AR11)**
**Given** the fixed `.apaa/` runtime tree
**When** the store creates it under an audited-repo root
**Then** it provisions EXACTLY the architecture-fixed sub-directories `state/ · assignments/ · findings/ ·
decisions/ · cache/` (architecture §Runtime artifact tree; the epic AC lists the first four — `cache/` is
included per the architecture tree and Decision F memo store, as a directory only)
**And** an artifact's filename derives from its content-sha256 (e.g. the envelope `content_hash` from Story
1.1) for content-addressed artifacts (findings, state snapshots), OR a stable assignment-id for assignment
manifests — NEVER arrival order / a counter / `uuid4` / wall-clock (AR4/AR11; the determinism keystone — two
hosts produce identically-named files).

**AC4 — Writes go through the single serializer + envelope (AR4, FR25, NFR-P1)**
**Given** an artifact payload to persist
**When** `store/writer.py` writes it
**Then** the bytes written are EXACTLY `store/canonical.dumps_bytes(...)` of the (envelope-wrapped) payload —
REUSING the Story 1.1 `canonical` serializer + `EnvelopeWriter`, with NO direct `json.dumps(` anywhere in the
new store modules (the committed `tests/apaa/test_canonical_single_serializer.py` AST gate must still pass
with the new modules present)
**And** the on-disk bytes for a given payload are byte-identical across two writes / two hosts (NFR-P1) —
verified by a golden/round-trip test over a populated `CoverageLedger` and a `Recording` from Story 1.2.

**AC5 — Reader deserializes, validates against the frozen schema & round-trips byte-identically (FR31, AR8 pure)**
**Given** a previously written artifact on disk
**When** `store/reader.py` reads it
**Then** it loads via `store/canonical.loads`, validates against the frozen Pydantic v2 schema (e.g.
`Envelope` / `CoverageLedger` / `Recording`), and reconstructs a model EQUAL to the original — and
re-serializing the loaded model through `canonical.dumps_bytes` yields bytes byte-identical to what was read
(round-trip stability)
**And** `store/reader.py` is PURE deserialize/validate (it MAY read the bytes off disk as the resumability
read primitive, but performs NO clock read, NO `uuid4`/`random`, NO LLM/network, NO write) — per the
architecture's "store/reader.py — PURE deserialize/validate; resumability (FR31)" classification.

**AC6 — Corrupt / tampered / missing on-disk state degrades to a typed failure, never an uncaught crash (AR10, NFR-R1)**
**Given** an `.apaa/` artifact file that is missing, truncated, non-UTF-8, not valid JSON, or whose payload
fails frozen-schema validation (e.g. an unknown field — `extra="forbid"` from Story 1.1/1.2), or whose
`content_hash` does not match a re-computed hash over its payload (tamper detection)
**When** the reader attempts to load it
**Then** it raises a TYPED error (a `canonical.CanonicalSerializationError`, a Pydantic `ValidationError`,
an APAA-typed store error such as `StoreIntegrityError(ValueError)`, or `FileNotFoundError` for the
missing-file case) — NEVER a bare/uncaught crash, a silent empty model, or a fabricated valid-looking result
**And** no bare `except: pass` and no `print()` appears in the library modules (AR10 / §3.3).

**AC7 — No source/secret bytes ever leak from the store layer (NFR-S1 spirit)**
**Given** the writer/reader/paths modules
**When** they raise an error or are exercised
**Then** error messages name the offending RELATIVE path / artifact id only — never the file CONTENT, never
a secret/source byte, never an absolute host path in a persisted/returned locator (mirror the
`WorkspaceArtifactWriter` DN-3 decision: return the `.apaa/`-root-relative POSIX locator, not an absolute
host path) — so this impure shell does not become a leakage vector (the CI-blocking randomized-canary
property suite that ENFORCES this across all write paths lands in Epic 4 / Story 4.4; this AC is the
producer-side discipline, not the property suite).

**AC8 — Pure modules untouched; store shell is the only new I/O (AR8 master rule)**
**Given** the determinism core delivered by Stories 1.1/1.2
**When** this story is implemented
**Then** `store/canonical.py`, `store/envelope.py`, `ledger/coverage_ledger.py`, `ledger/recording.py` are
NOT modified to add I/O (they stay pure); ALL new filesystem I/O is confined to `store/writer.py` +
`store/paths.py` (impure shell) and the read primitive in `store/reader.py`
**And** the new modules each cite their `APAA-FR-*` / `APAA-NFR-*` / `AR*` drivers in the module docstring
and are ≤1200 lines (NFR-M1).

**AC9 — Determinism, containment & import-isolation gates green (NFR-P1, NFR-S5, AR7/AR9)**
**Given** the modules added by this story
**When** the `tests/apaa/` suite runs
**Then** (a) `tests/apaa/test_containment.py` (NEW — the architecture-named containment property test) asserts
every escape vector in AC1 raises before any write and a confined path succeeds; (b) a write/read
golden/round-trip test asserts byte-stability (AC4/AC5); (c) `tests/apaa/test_no_web_imports.py` is EXTENDED
(append the new store module paths to `_MODULES_UNDER_GUARD`) and stays green; (d) the Story 1.1
single-serializer AST gate still passes with the new modules present; (e) the WHOLE `tests/apaa/` suite +
`tests/test_import_paths.py` pass (no flat-stub regression — `store/` is a sub-package).

## Tasks / Subtasks

- [x] **Task 1 — `.apaa/` path resolver + containment** (AC: 1, 2, 3)
  - [x] Create `minions_core/apaa/store/paths.py` (docstring cites `APAA-NFR-S5`, `AR7`, `AR10`, `AR11`).
  - [x] Define the fixed `.apaa/` tree constant (the EXACT sub-dir set `state/ · assignments/ · findings/ ·
        decisions/ · cache/`) and a resolver that, given an audited-repo root + a `.apaa/`-relative sub-path,
        returns the resolved absolute target AFTER a `Path.resolve()` + `is_relative_to` containment check
        against the resolved `.apaa/` root — REUSING `WorkspaceContainmentError` from
        `minions_core.lifecycle.workspace_artifact_writer` (do NOT define a second containment error).
  - [x] Containment raises `WorkspaceContainmentError` BEFORE any FS mutation for: `../` traversal, absolute
        sub-path, `..`-only segment, symlink escape, sibling-prefix (`.apaa-evil` vs `.apaa`), Windows
        backslash traversal, drive-letter absolute.
  - [x] Provide a helper to ensure/create the fixed sub-dirs idempotently (`mkdir(parents=True,
        exist_ok=True)` — only AFTER the containment check passes).
- [x] **Task 2 — Impure writer** (AC: 2, 3, 4, 7)
  - [x] Create `minions_core/apaa/store/writer.py` (docstring cites `APAA-FR-25`, `APAA-NFR-P1`, `AR4`,
        `AR7`, `AR8`, `AR10`, `AR11`; record the thin-wrap-vs-delegate rationale per architecture Decision F).
  - [x] Write API: takes an audited-repo root + an envelope-wrapped payload (or a model + envelope metadata),
        derives the content-addressed filename from the envelope `content_hash` (or a stable assignment-id for
        assignments), resolves+containment-checks via `paths.py`, then writes EXACTLY
        `canonical.dumps_bytes(...)` (REUSE Story 1.1 `canonical` + `EnvelopeWriter` — NO direct `json.dumps`).
  - [x] Return the `.apaa/`-root-relative POSIX locator (never an absolute host path — DN-3 precedent). No
        `print()`, no bare `except: pass`.
- [x] **Task 3 — Pure reader** (AC: 5, 6)
  - [x] Create `minions_core/apaa/store/reader.py` (docstring cites `APAA-FR-31`, `AR8` (pure
        deserialize/validate), `AR10`).
  - [x] Read primitive: load bytes for a given `.apaa/` locator (containment-checked via `paths.py`),
        `canonical.loads`, validate against the target frozen model (`Envelope` / `CoverageLedger` /
        `Recording` — generic-over-model or per-type readers, dev's choice; document it), reconstruct an equal
        model, and (optionally) verify the envelope `content_hash` matches a re-computed hash (tamper guard).
  - [x] Corrupt/missing/tampered → TYPED error (AC6): pick + document the error taxonomy (reuse
        `CanonicalSerializationError` / Pydantic `ValidationError` / `FileNotFoundError`, add
        `StoreIntegrityError(ValueError)` ONLY for the hash-mismatch/tamper case if no existing type fits).
  - [x] NO clock/`uuid4`/`random`/LLM/network/write in the reader (pure deserialize/validate).
- [x] **Task 4 — Containment property test (the architecture-named gate)** (AC: 1, 9)
  - [x] Create `tests/apaa/test_containment.py`: parametrize every escape vector in AC1; assert each raises
        `WorkspaceContainmentError` AND that NO file/dir was created on the escaping path (check the FS after);
        assert a legitimately-confined path writes successfully and returns a relative locator. Use `tmp_path`.
  - [x] Include the sibling-prefix case explicitly (`.apaa-evil` must NOT be treated as inside `.apaa`) — the
        `str.startswith` regression guard.
- [x] **Task 5 — Write/read round-trip + determinism golden** (AC: 4, 5, 9)
  - [x] Create `tests/apaa/test_store_roundtrip.py`: write a populated `CoverageLedger` and a `Recording`
        (built via Story 1.2 models) through the writer; read them back via the reader; assert model equality
        AND byte-stability (re-serialize == read bytes); assert the on-disk filename is content-addressed
        (matches the envelope `content_hash`); assert two writes of the same payload produce byte-identical
        files (NFR-P1). REUSE `store/canonical` + `store/envelope` — no second serializer.
  - [x] Corrupt-state test: truncated/non-UTF-8/invalid-JSON/extra-field/hash-mismatch each raise the
        expected typed error (AC6).
- [x] **Task 6 — Extend the import-isolation gate** (AC: 2, 9)
  - [x] Append `minions_core.apaa.store.paths`, `minions_core.apaa.store.writer`,
        `minions_core.apaa.store.reader` to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py`
        (do NOT write a parallel gate). Confirm `lifecycle/workspace_artifact_writer` import does not leak the
        web stack.
- [x] **Task 7 — Test scaffold + run + mypy** (AC: all)
  - [x] Run `PYTHONIOENCODING=utf-8 pytest tests/apaa/ -v` (the WHOLE suite, so the 1.1 single-serializer AST
        gate re-runs with the new store modules present) → all pass. `tests/test_import_paths.py` green.
  - [x] `mypy` clean on the three new `store/` modules (`python run_mypy_per_file.py` or scoped).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **Pure/impure separation (master rule, AR8).** `store/writer.py` and `store/paths.py` are the IMPURE shell
  (filesystem I/O lives here and ONLY here, plus the read primitive in `reader.py`). `store/reader.py` is
  classified PURE deserialize/validate by the architecture — it MAY read bytes off disk (it is the
  resumability read primitive) but does NO clock/uuid/random/LLM/network/write. Do NOT add I/O to the four
  pure modules from 1.1/1.2 (`canonical`, `envelope`, `coverage_ledger`, `recording`). ✅ `writer` calls
  `canonical.dumps_bytes` then `Path.write_bytes` · ❌ `canonical.py` opening a file.
- **Containment is the security keystone (cross-cutting #5, §Security/Containment Patterns, NFR-S5).** Real
  `Path.resolve()` + `is_relative_to`, NEVER `str.startswith`. A breach raises a typed error BEFORE any
  write. Mirror `WorkspaceArtifactWriter._is_contained` EXACTLY (`candidate.is_relative_to(root) and
  candidate != root`, `except ValueError: return False`). The `.apaa/` root is itself resolved once; every
  sub-path is checked against it.
- **Reuse the Minions helper — no fork (AR7, §3.3).** `lifecycle/workspace_artifact_writer` is the canonical
  containment authority (Minions §4a #3; verified pathlib-only / FastAPI-free). Either delegate to it with
  the `.apaa/` root injected, or reuse its `WorkspaceContainmentError` + containment logic via a thin wrap —
  but DO NOT write a second, divergent containment check (the exact failure class this story exists to
  prevent). Record which path you took and why in the docstring.
- **One serializer, forever (AR4, cross-cutting #3).** ALL `.apaa/` bytes go through `store/canonical.py`
  (Story 1.1). The writer emits exactly `canonical.dumps_bytes(...)`; the reader loads via `canonical.loads`.
  The committed `tests/apaa/test_canonical_single_serializer.py` AST gate FAILS the build if a direct
  `json.dumps(` appears in the new store modules — never add one.
- **Content-addressed filenames, never arrival order (AR11, determinism).** Filenames derive from
  content-sha256 (reuse the envelope `content_hash` from Story 1.1) or a stable assignment-id — never a
  counter / `uuid4` / wall-clock / arrival order. This is what makes two hosts produce identically-named
  files (NFR-P1).
- **Envelope wrapping (FR25, NFR-A1).** Persisted artifacts are wrapped via `EnvelopeWriter.build` (Story
  1.1) — content-hash over payload only, `prev_hash` chaining, `schema_version` + `producer` + `apaa_version`.
  Reuse it; do not re-implement hashing or chaining.
- **Error/degradation (AR10, NFR-R1).** Failure → a TYPED exception at the impure shell (reuse
  `WorkspaceContainmentError` for containment; `CanonicalSerializationError` / Pydantic `ValidationError` /
  `FileNotFoundError` for read failures; a small typed `StoreIntegrityError(ValueError)` ONLY if needed for
  hash-mismatch). NO bare `except: pass`, NO `print()` in library code, NO silent empty-model fallback, NO
  fabricated valid-looking result.
- **No secret/source-byte leakage (NFR-S1 spirit, §Security/Containment Patterns).** Error messages cite the
  RELATIVE path / artifact id, never file content; returned locators are `.apaa/`-root-relative POSIX, never
  an absolute host path (DN-3 precedent from `WorkspaceArtifactWriter`). The CI-blocking randomized-canary
  property suite that ENFORCES no-leakage across all write paths is Epic 4 / Story 4.4 — out of scope here;
  this story is the producer-side discipline that suite will later verify.
- **Headless / boundary (§Architectural Boundaries).** APAA is downstream of the HTTP/A2A boundary — these
  modules take no token, register no FastAPI route, and must not import the web stack (AC9 / AR7). Never
  import `minions_core.api.* / services.api_app / app_factory / api_server`.

### Precedent inherited from Stories 1.1/1.2 (done) — honor these decisions

- **`WorkspaceArtifactWriter` is the containment exemplar to mirror.** Read
  `minions_core/lifecycle/workspace_artifact_writer.py` (Minions story 18-2): it resolves the root once at
  construction, builds `candidate = (root / ... ).resolve()`, checks `_is_contained` (`is_relative_to` +
  `!= root`, `except ValueError: return False`), raises `WorkspaceContainmentError` (a `ValueError` subclass)
  BEFORE any write, `mkdir(parents=True, exist_ok=True)` only after, and returns a root-relative POSIX
  locator. This story applies the IDENTICAL pattern to the `.apaa/` root. Its tests live at
  `tests/security/` (TC-SEC-003-33/-34) — the APAA equivalent is `tests/apaa/test_containment.py`.
- **`extra="forbid"` frozen models** — the reader validates against models that reject unknown fields (an
  unknown field on read-back is a typed `ValidationError`, NOT silent acceptance). This is the AC6 corruption
  guard for free — assert it.
- **Golden constants for determinism** — Stories 1.1/1.2 froze golden canonical strings + `content_hash` so
  byte-drift fails loudly. Do the SAME for the on-disk write/read golden (the written bytes for a populated
  ledger/recording are a golden constant).
- **Single serializer / envelope reuse** — `store/canonical.py` (`dumps`/`dumps_bytes`/`loads`) and
  `store/envelope.py` (`Envelope`, `EnvelopeWriter.build`, `compute_content_hash`, `GENESIS_PREV_HASH`) are
  present and done. REUSE verbatim — no second serializer (the AST gate enforces this).
- **Import-isolation gate is seeded, extend it** — `tests/apaa/test_no_web_imports.py` has a
  `_MODULES_UNDER_GUARD` tuple "later stories APPEND to". Append the three new store module paths there
  (AC9); do not fork the gate.
- **`apaa_version` / `schema_version` from a single source** — `apaa_version` is
  `minions_core/apaa/__init__.py::__version__` (`"0.1.0"`); the writer passes it through `EnvelopeWriter`
  (which already defaults to it). Per-artifact `schema_version` is a module constant on the writer/store, not
  read from env/clock.

### Source tree — files to create (all NEW; the only UPDATE is the import-isolation gate)

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/store/paths.py` | NEW | `.apaa/` fixed-tree constant + containment-checked path resolver (REUSE `WorkspaceContainmentError`) |
| `minions_core/apaa/store/writer.py` | NEW | IMPURE writer — content-addressed filename, `canonical.dumps_bytes` write, relative-locator return |
| `minions_core/apaa/store/reader.py` | NEW | PURE deserialize/validate read primitive (FR31 resumability seam); typed corruption errors |
| `tests/apaa/test_containment.py` | NEW | containment property test — every escape vector raises before any write (architecture-named gate) |
| `tests/apaa/test_store_roundtrip.py` | NEW | write/read round-trip + byte-stability golden + corrupt-state typed errors |
| `tests/apaa/test_no_web_imports.py` | UPDATE | extend `_MODULES_UNDER_GUARD` with the three new store modules |

The architecture's package tree (`architecture.md` §Project Structure) places EXACTLY `canonical.py`,
`envelope.py`, `paths.py`, `writer.py`, `reader.py` under `store/`. `canonical.py` + `envelope.py` exist
(Story 1.1); this story adds `paths.py` + `writer.py` + `reader.py`. Do NOT invent additional modules (the
cache/memo store is `cache/` Epic 5; the verdict gate is `verdict/` Story 1.6; detectors are `detectors/`
Story 1.5). Resist building ahead.

### Reuse — what already exists (verified present) and what NOT to reinvent

- **Story 1.1 store spine** (`minions_core/apaa/store/canonical.py` + `store/envelope.py` — DONE, present):
  `canonical.dumps(payload) -> str`, `canonical.dumps_bytes(payload) -> bytes`, `canonical.loads(text) ->
  object`, `CanonicalSerializationError(ValueError)`; `Envelope` model, `EnvelopeWriter.build(...)`,
  `compute_content_hash(payload) -> str`, `GENESIS_PREV_HASH = "0"*64`. REUSE for ALL serialization, hashing,
  envelope wrapping, and goldens — no second serializer (the AST gate enforces this).
- **Story 1.2 ledger/recording models** (`minions_core/apaa/ledger/coverage_ledger.py` +
  `ledger/recording.py` — DONE, present): `CoverageDepth`, `CoverageLedgerEntry`, `CoverageLedger`,
  `grade_entry`; `Locator`, `Recording`, `RecordingValidationError`. Use these as the payloads the
  writer/reader round-trip in tests.
- **Minions containment helper** (`minions_core/lifecycle/workspace_artifact_writer.py` — DONE, present):
  `WorkspaceArtifactWriter` (resolve-once root, `materialize(run_id, relative_path, content)`,
  `_is_contained`), `WorkspaceContainmentError(ValueError)`. REUSE by import (AR7 §3.3 no-fork) — verified
  pathlib-only / FastAPI-free.
- **Pydantic v2** is an existing baseline dep — `from pydantic import BaseModel, ConfigDict` etc. Do NOT add
  a dependency. `tree-sitter`/`radon`/`jsonschema` are NOT needed for this story (they arrive Stories 1.4+).
- **`minions_core/apaa/__init__.py::__version__`** (`"0.1.0"`) — the single `apaa_version` source.

### Determinism / contract decisions the dev must lock (record the choice in the docstring)

- **Delegate vs. thin-wrap the containment helper** — decide whether `WorkspaceArtifactWriter` can be reused
  directly with the `.apaa/` root injected (its `materialize` takes `run_id` + `relative_path`, which may map
  onto `.apaa/` sub-paths), OR whether a thin wrap that reuses only `WorkspaceContainmentError` + the
  `Path.resolve()`/`is_relative_to` logic is cleaner for the `.apaa/`-rooted, content-addressed shape. EITHER
  is acceptable; the binding constraint is NO second/divergent containment check and NO fork. Document the
  decision + rationale in `paths.py`/`writer.py`.
- **Filename derivation** — content-addressed artifacts (state snapshots, findings) → `<content_hash>.json`
  (the envelope `content_hash`); assignment manifests → `<assignment_id>.json` (a stable, content-derived or
  caller-supplied stable id, NEVER `uuid4`/counter/arrival order). Lock + document the scheme.
- **Read taxonomy** — generic-over-model reader vs. per-type readers (`read_envelope`, `read_ledger`,
  `read_recording`). Pick one, document it; the AC only requires deserialize→validate→equal-model + typed
  failures, not a specific shape.
- **Tamper guard** — whether the reader RE-VERIFIES the envelope `content_hash` against a re-computed hash
  over the payload on read (recommended — cheap, and it makes AC6's tamper case real). If added, the
  mismatch raises a typed `StoreIntegrityError(ValueError)`; document it.
- **Relative-locator return** — the writer returns the `.apaa/`-root-relative (or audited-repo-root-relative)
  POSIX locator, never an absolute host path (DN-3 precedent / NFR-S1 spirit). Lock the relativity base and
  document it.

### Scope fences (do NOT pull forward)

- ❌ The **memoization / cache store** (`cache/memo_store.py`, `cache/key.py`) — Epic 5. This story creates
  the `.apaa/cache/` DIRECTORY (AR11 fixed tree) but NOT the memoization LOGIC.
- ❌ **Resume ORCHESTRATION** (re-driving a partial audit, skipping already-`audited_deep` files) — Epic 3 /
  Story 3.4. This story provides only the `store/reader.py` read-back PRIMITIVE that resume will later use.
- ❌ The pure-function **verdict gate** — Story 1.6.
- ❌ **Repo intake / AST index / partitioner** — Story 1.4.
- ❌ **Detectors / finding emission** (`detectors/*`) — Story 1.5.
- ❌ The **LLM dispatch port / adapter** (`audit/*`) — Epic 6 / Story 6.1.
- ❌ The **CLI / pipeline wiring** — Story 1.7.
- ❌ The **CI-blocking randomized-canary secret-containment property suite** (`tests/security/
  test_apaa_secret_containment.py`) — Epic 4 / Story 4.4. AC7 here is producer-side discipline only.

### Testing standards

- pytest under `tests/apaa/`; test IDs follow `TC-<AREA>-<SEQ>-<SUBSEQ>` — use area `APAA-STORE` (e.g.
  `TC-APAA-STORE-001-60` …) in test docstrings/ids (Stories 1.1 used `APAA-STORE`, 1.2 used `APAA-LEDGER`).
- The containment + round-trip tests USE the filesystem (this is the impure shell) — use `pytest`'s
  `tmp_path` fixture; assert post-condition FS state (no file/dir created on an escaping path).
- Freeze golden on-disk bytes + content-addressed filename as recorded constants so byte-drift fails loudly
  (NFR-P1).
- On Windows, prefix runs with `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on cp1252).
  Include at least one Windows-shaped escape vector (backslash traversal, drive-letter absolute) in the
  containment test so the guard holds cross-platform.
- Run: `PYTHONIOENCODING=utf-8 pytest tests/apaa/ -v` (the WHOLE `tests/apaa/` suite, so the 1.1 single-
  serializer AST gate re-runs with the new modules present). All must pass before moving to `review`.
- `mypy` clean on the new modules (`python run_mypy_per_file.py` or a scoped invocation).

### CLAUDE.md §4a follow-up

The §4a APAA Component→Driver row was already added by Story 1.1. This story does NOT need a new §4a row; if
a one-line additive note is added it must note `store/paths.py` + `store/writer.py` + `store/reader.py` as
the impure `.apaa/` persistence shell (containment-checked) of the determinism core, and must NOT rewrite the
existing row. Keep it minimal — a new row is not required.

### Project Structure Notes

- Alignment: file paths exactly match `architecture.md` §Project Structure package tree (`store/paths.py`,
  `store/writer.py`, `store/reader.py`). Naming `snake_case.py`, ≤1200 lines (NFR-M1). JSON/enum values
  `snake_case`.
- No conflicts/variances. Judgment calls — all decided above and to be golden-tested so they freeze for
  downstream: the containment delegate-vs-thin-wrap choice, the filename-derivation scheme, the read taxonomy,
  the tamper-guard decision, and the relative-locator base.
- Scope fence: this story delivers the impure `.apaa/` write/read shell + path containment ONLY. The verdict
  gate (1.6), intake/AST (1.4), detectors (1.5), cache/memo (Epic 5), resume orchestration (Epic 3), LLM
  wiring (Epic 6), and CLI (1.7) are explicitly NOT in scope. Build the shell complete-and-contained, then
  stop.

### References

- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Story-1.3 `.apaa/` store writer & reader with filesystem containment]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#F. Persistence & State] (NO database; filesystem-as-contract; containment reuse; thin-wrap if root injection unsupported)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Security / Containment Patterns] (all FS writes via the containment helper — `is_relative_to`, never `str.startswith`; breach raises before any write)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Pure/Impure Separation (master rule)] (`store/*` writer impure; `reader` PURE deserialize/validate)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Determinism Patterns (NFR-P1/D1)] (one serializer; content-addressed filenames; no arrival order/uuid/clock)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Cross-Cutting Concerns #3 single serializer / #5 producer-side redaction / #7 import-isolation gate]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Runtime artifact tree (.apaa/)] (fixed tree: state/ assignments/ findings/ decisions/ cache/)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Architectural Boundaries] (filesystem boundary; import boundary; downstream of HTTP/A2A)
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#FR25 content-hashed envelope / FR31 resume from .apaa state / NFR-S5 containment-checked writes / NFR-P1 byte-identical state / NFR-A1 hash-chained envelope]
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-1-canonical-serializer-content-hashed-envelope.md] (DONE — serializer + envelope spine to reuse; golden-constant + `_MODULES_UNDER_GUARD` seed; scope-fence "impure shell is 1.3")
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-2-fixed-enum-coverage-ledger-frozen-recording-schema.md] (DONE — ledger/recording models the writer/reader round-trip; `extra="forbid"` corruption guard)
- [Source: minions_core/apaa/store/canonical.py] (the single serializer — `dumps`/`dumps_bytes`/`loads` + `CanonicalSerializationError`)
- [Source: minions_core/apaa/store/envelope.py] (`Envelope`, `EnvelopeWriter.build`, `compute_content_hash`, `GENESIS_PREV_HASH`)
- [Source: minions_core/apaa/ledger/coverage_ledger.py + ledger/recording.py] (the payloads to persist/round-trip)
- [Source: minions_core/lifecycle/workspace_artifact_writer.py] (the containment exemplar to REUSE — `Path.resolve()` + `is_relative_to`, `WorkspaceContainmentError`, relative-locator return; NEVER `str.startswith`)
- [Source: CLAUDE.md §3.2 file-size / §3.7 headless-only / §3.8 12-Factor + secret masking / §4a #3 WorkspaceArtifactWriter]

## Dev Agent Record

### Agent Model Used

claude-opus-4-8 (BMAD Developer / dev-story)

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **267 passed** (includes
  the 1.1 single-serializer AST gate re-run with the new store modules present, the extended no-web-imports
  gate, the new containment property test, and the round-trip/corruption suite).
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/test_containment.py -v` → **12 passed** (all AC1 escape
  vectors raise before any FS mutation; symlink case ran, not skipped, on this host).
- `python -m mypy minions_core/apaa/store/{paths,writer,reader}.py` → **Success: no issues found in 3 source files**.

### Completion Notes List

- **Containment reuse decision (AC2): thin-wrap.** `WorkspaceArtifactWriter.materialize` is hard-wired to a
  `<root>/<run_id>/<relative_path>` UTF-8 *text* write; the `.apaa/` store is content-addressed (`<sha>.json`),
  writes canonical *bytes* (single serializer, AR4), and roots at a `.apaa/` dir inside an arbitrary audited
  repo — a poor fit for root injection. Per architecture Decision F ("thin-wrap if root injection is
  unsupported") I REUSE the canonical `WorkspaceContainmentError` typed error (imported, re-exported) AND
  mirror its EXACT `_is_contained` logic (`is_relative_to` + `!= root`, `except ValueError: return False`) —
  no second/divergent containment check, no fork. Rationale recorded in `store/paths.py` + `store/writer.py`
  docstrings. The reuse is pinned by `test_reuses_minions_containment_error_no_fork` (`WorkspaceContainmentError
  is MinionsWorkspaceContainmentError`).
- **Filename derivation (AC3): locked.** Content-addressed artifacts → `<subdir>/<envelope.content_hash>.json`
  (Story 1.1 envelope hash); assignment manifests → `assignments/<assignment_id>.json` (caller-supplied stable
  id). Never `uuid4`/counter/arrival order.
- **Read taxonomy (AC5/AC6): per-type readers over a shared generic core** — `read_envelope` / `read_ledger` /
  `read_recording`, each containment-checked → bytes → `canonical.loads` → frozen Pydantic validate.
- **Tamper guard (AC6): taken.** `read_envelope` re-verifies `content_hash` against `compute_content_hash` over
  the loaded payload; a mismatch raises the new `StoreIntegrityError(ValueError)` (added only for this case —
  no existing type fit). Corruption taxonomy: missing → `FileNotFoundError`; non-UTF-8 / non-JSON →
  `CanonicalSerializationError` (wrapped); unknown field / wrong shape → Pydantic `ValidationError`
  (`extra="forbid"` from 1.1/1.2); payload tamper → `StoreIntegrityError`. No bare `except: pass`, no `print()`.
- **Relative-locator base (AC7): `.apaa/`-root-relative POSIX** (mirrors `WorkspaceArtifactWriter` DN-3); error
  messages name the relative path/id only, never content / an absolute host path.
- **Payload-fidelity decision (AC4/AC5):** persisted payloads are JSON-primitive dicts (`model_dump(mode="json")`
  — enums→str, tuples→lists). The content hash is taken over, and the reader reconstructs, the canonical JSON
  form, so write→read envelope-equality holds byte-for-byte. Documented in `store/writer.py` docstring.
- **Purity (AC8):** the four 1.1/1.2 pure modules are untouched; new FS I/O is confined to `paths.py`/`writer.py`
  + the read primitive in `reader.py` (no clock/uuid/random/LLM/network/write in the reader — pinned by
  `test_reader_is_pure_no_write_on_read`). All three new modules cite their `APAA-*`/`AR*` drivers and are
  well under 1200 lines.

### File List

- `minions_core/apaa/store/paths.py` (NEW) — `.apaa/` fixed tree + containment-checked resolver (reuses `WorkspaceContainmentError`).
- `minions_core/apaa/store/writer.py` (NEW) — IMPURE content-addressed, single-serializer byte writer; relative-locator return.
- `minions_core/apaa/store/reader.py` (NEW) — PURE deserialize/validate read primitive (FR31 seam) + `StoreIntegrityError` tamper guard.
- `minions_core/apaa/store/__init__.py` (UPDATE) — docstring now notes the impure shell exists.
- `tests/apaa/test_containment.py` (NEW) — containment property test: every escape vector raises before any write.
- `tests/apaa/test_store_roundtrip.py` (NEW) — write/read round-trip + byte-stability + typed corruption errors.
- `tests/apaa/test_no_web_imports.py` (UPDATE) — `_MODULES_UNDER_GUARD` extended with the three new store modules.

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-06-21 | 0.1.0 | Story created (create-story): context-filled spec for the impure `.apaa/` writer/reader + path containment shell — the third (first impure) link in the determinism spine. ACs cover containment property vectors (traversal/symlink/absolute/sibling-prefix/Windows-backslash/drive-letter), single-serializer reuse, content-addressed filenames, envelope wrapping, pure-reader round-trip + typed corruption errors, no-leakage discipline, and the import-isolation gate extension. Honors 1.1/1.2 precedents (no second serializer; reuse Minions `WorkspaceArtifactWriter` containment, no fork). Status → ready-for-dev. | claude-opus-4-8 (Scrum Master) |
| 2026-06-21 | 0.2.0 | Implemented (dev-story): `store/paths.py` (containment-checked resolver + fixed tree, thin-wraps the Minions `WorkspaceContainmentError`), `store/writer.py` (IMPURE content-addressed single-serializer byte writer, relative-locator return), `store/reader.py` (PURE deserialize/validate read primitive + `StoreIntegrityError` tamper guard). Extended the no-web-imports gate; added `tests/apaa/test_containment.py` (12 escape-vector cases, all raise before any FS mutation incl. symlink + sibling-prefix `str.startswith` guard) and `tests/apaa/test_store_roundtrip.py` (byte-stability golden, content-addressed filename, two-host byte-identical, per-type round-trip, full corruption taxonomy). All 8 ACs satisfied. `pytest tests/apaa/ tests/test_import_paths.py` → 267 passed (1.1 single-serializer AST gate green with new modules present); mypy clean on the 3 new modules. Status → review. | claude-opus-4-8 (Developer) |
| 2026-06-21 | 0.3.0 | Code review (bmad-code-review, adversarial, iteration 1): VERDICT pass. Security keystone empirically verified — `Path.resolve()` + `is_relative_to` (never `str.startswith`); every AC1 escape vector (`..` traversal, deep traversal, `..`-only, absolute POSIX, drive-letter, Windows backslash, symlink-escape, sibling-prefix `.apaa-evil`) raises `WorkspaceContainmentError` BEFORE any FS mutation (no partial write). Empty/`.` resolve to root and are rejected by the `!= root` guard. `WorkspaceContainmentError` reused by import (no fork; pinned by test); single serializer preserved (only `canonical.py` calls `json.dumps`; AST gate green); reader pure (no clock/uuid/random/write); tamper guard (payload-vs-`content_hash`) correct → `StoreIntegrityError`. 267 passed; mypy clean; all files ≤1200 lines; headless. Two non-blocking Low items recorded below. Status → done. | claude-opus-4-8 (Reviewer) |

## Senior Developer Review (AI)

**Reviewer:** claude-opus-4-8 (BMAD bmad-code-review, adversarial gate) · **Date:** 2026-06-21 · **Iteration:** 1 · **Verdict: PASS**

### Summary

The impure `.apaa/` write/read shell is correct, contained, and deterministic. The filesystem-containment security keystone — the entire reason this story exists — is implemented exactly as the architecture mandates: the `.apaa/` root is resolved once at construction, every candidate sub-path is `(root / rel).resolve()` then asserted `is_relative_to` the root with a `!= root` guard inside a `try/except ValueError`, mirroring `WorkspaceArtifactWriter._is_contained`. There is NO `str.startswith` anywhere. I empirically reproduced every escape vector in AC1 and confirmed each raises `WorkspaceContainmentError` BEFORE any directory creation or byte write (filesystem snapshot unchanged), including the symlink-escape (ran, not skipped, on this Windows host) and the sibling-prefix `.apaa-evil` regression case. The single serializer is preserved (only `canonical.py` emits `json.dumps`; the 1.1 AST gate re-ran green with the new modules present), filenames are content-addressed (`content_hash`) or stable-assignment-id (never `uuid4`/counter/arrival order), the reader is pure deserialize/validate with a sound payload-vs-hash tamper guard, and the typed-error taxonomy for missing/non-UTF-8/non-JSON/extra-field/wrong-shape/tamper is complete. The `WorkspaceContainmentError` is reused by import (no fork — pinned by `test_reuses_minions_containment_error_no_fork`).

### Evidence

- `PYTHONIOENCODING=utf-8 pytest tests/apaa/ tests/test_import_paths.py` → **267 passed** (incl. AST single-serializer gate, extended no-web-imports gate, 12 containment vectors, full round-trip + corruption taxonomy).
- `pytest tests/apaa/test_containment.py::test_symlink_escape_raises_before_write -rs` → **1 passed** (not skipped).
- `mypy minions_core/apaa/store/{paths,writer,reader}.py` → **Success: no issues found in 3 source files**.
- Manual adversarial probes: empty/`.` rejected by `!= root`; writer `subdir="../evil"` raises before write; internal byte/hash/filename consistency confirmed.

### AC coverage

AC1–AC9 all met. Containment property gate (AC1/AC9a) green with all six listed + symlink + sibling vectors; single-serializer/byte-stability (AC4/AC9b) green; no-web-imports gate extended with the three new modules (AC2/AC9c); 1.1 AST gate green with new modules present (AC9d); whole suite + import-paths green (AC9e). Pure modules from 1.1/1.2 untouched (AC8). Thin-wrap reuse decision documented in `paths.py`/`writer.py` docstrings per architecture Decision F (AC2).

### Engineering-principles assessment

Reuse-canonical (§3.3) is honored at the error-type level (imported, not forked). The containment LOGIC is *mirrored* rather than imported — explicitly authorized by the story (architecture Decision F "thin-wrap if root injection is unsupported"), since `WorkspaceArtifactWriter.materialize` is hard-wired to a `<root>/<run_id>/<rel>` UTF-8 text write that does not fit the content-addressed byte-write shape. Pure/impure separation (AR8) is clean. No SOLID/DRY/YAGNI violations of note. Two Low hardening items below.

### Review Findings

<!-- defer-schema-session: 2026-06-21 -->

- [x] [Review][Defer] Reader does not assert content-addressed filename == internal `content_hash` [minions_core/apaa/store/reader.py:105] — deferred, defense-in-depth beyond AC6. The required tamper case (mutate payload, leave stale `content_hash`) IS detected via the payload-vs-hash guard. However a file whose *name* diverges from its internal `content_hash` (e.g. a renamed/misfiled artifact) is silently accepted. For a content-addressed store this invariant (locator stem == `content_hash`) is implied but unenforced. Suggested fix: in `read_envelope`, when the locator stem is a 64-hex sha, assert it equals the verified `content_hash`, raising `StoreIntegrityError` on mismatch. Non-blocking; the AC-required guard holds.
  - id: DF-1-3-A · origin_story: 1-3-apaa-store-writer-reader-filesystem-containment · owner: Security Owner · target_story: epic-4-secret-containment-property-suite-ci-blocking · category: security · severity: 🟢
- [x] [Review][Defer] Containment `_is_contained` LOGIC is mirrored, not imported, from the importable `WorkspaceArtifactWriter._is_contained` staticmethod [minions_core/apaa/store/paths.py:65] — deferred, future-drift hardening. The story explicitly authorizes the thin-wrap of logic (architecture Decision F) and the two implementations are currently byte-identical, but the canonical check is an importable `@staticmethod`, so the strictly-better option (import + reuse it, or add a parity test pinning logical equivalence) was available. Risk: if the canonical containment is hardened later (e.g. a future escape-vector fix), the APAA mirror silently diverges. Suggested fix: either `from ...workspace_artifact_writer import WorkspaceArtifactWriter` and call `._is_contained`, OR add a parity test that drives both implementations over the same vector matrix. Non-blocking.
  - id: DF-1-3-B · origin_story: 1-3-apaa-store-writer-reader-filesystem-containment · owner: Security Owner · target_story: epic-4-referential-integrity-lint-of-on-disk-state · category: security · severity: 🟢
