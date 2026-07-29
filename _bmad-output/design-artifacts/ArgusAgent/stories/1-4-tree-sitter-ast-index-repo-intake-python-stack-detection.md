# Story 1.4: tree-sitter AST index, repo intake & Python stack detection

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/APAA/`; the tracker is `_bmad-output/design-artifacts/APAA/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As an integrator,
I want APAA to load a repo at a pinned commit, detect its stack, and build a tree-sitter code-graph index,
so that depth analysis runs on real structure (not embeddings) and the audit is stack-aware — the FOURTH
link in the Epic-1 spine and the FIRST module that touches a foreign repository's source.

## Story Context

This is **Story 4 of Epic 1** (Signature-Demo Vertical Slice). It builds directly on the determinism spine
delivered by the three done stories:

- **Story 1.1 (done)** — the PURE determinism keystone under `minions_core/apaa/store/`: the single canonical
  serializer (`store/canonical.py`: `dumps`/`dumps_bytes`/`loads`/`canonicalize` + `CanonicalSerializationError`)
  and the content-hashed, schema-versioned, prev-hash-chained envelope (`store/envelope.py`: `Envelope`,
  `EnvelopeWriter.build`, `compute_content_hash`, `GENESIS_PREV_HASH`).
- **Story 1.2 (done)** — the PURE fixed-enum coverage ledger (`ledger/coverage_ledger.py`: `CoverageDepth`,
  `CoverageLedgerEntry`, `CoverageLedger`, `grade_entry`) and the frozen recording schema
  (`ledger/recording.py`: `Locator`, `Recording`, `RecordingValidationError`).
- **Story 1.3 (done)** — the FIRST IMPURE shell, the `.apaa/` write/read substrate: `store/paths.py`
  (`ApaaStorePaths` containment-checked resolver + the fixed `.apaa/` tree, reusing
  `WorkspaceContainmentError`), `store/writer.py` (content-addressed single-serializer byte writer),
  `store/reader.py` (PURE deserialize/validate read primitive). Plus the committed gates
  `tests/apaa/test_no_web_imports.py` (`_MODULES_UNDER_GUARD`) and `tests/apaa/test_canonical_single_serializer.py`.

**Where this story sits in the architecture's implementation sequence.** The architecture's locked sequence is
*"envelope + canonical serializer + fixed-enum ledger (C-core) → **AST index + a single vacuous-path rule
(B + D)** → pure-function verdict + exit code (C + A) → 🔴 on the cartridge"* (architecture §Decision Impact
Analysis, §Implementation Handoff). Stories 1.1–1.3 delivered **C-core**. **This story delivers the `B`
half** — Repository Intake & Indexing (architecture §Decision B): repo load @ pinned commit (FR1), stack
detection (FR2), and the tree-sitter code-graph index (the AST substrate the depth audit and the Story 1.5
vacuous-path AST subset fold over). The detector half (`D`: the vacuous-test rule) is **Story 1.5**, and
the pure verdict + CLI are **1.6 / 1.7**. This story stops at producing the index + intake artifacts; it
emits no findings and computes no verdict.

**The two new external dependencies become real here.** Stories 1.1–1.3 needed only `pydantic` (already a
baseline dep). This is the FIRST story that imports the parsing toolchain. Per architecture **AR1** /
**Decision B** the toolchain is already sanctioned AND staged: `pyproject.toml`
`[project.optional-dependencies].apaa` already declares `tree-sitter>=0.25`, `tree-sitter-python>=0.25`, and
`radon>=4` (verified present in this session). **No net-new sanctioned tool is introduced by this story** —
it consumes the already-declared `minions[apaa]` extra. The dev installs the extra
(`pip install -e ".[apaa]"`) and confirms the pinned versions resolve (`tree-sitter==0.25.2` +
`tree-sitter-python==0.25.0` per AR1; the `>=` floor in the extra admits the 0.25.x line — record the exact
resolved version, since the **grammar version is a determinism cache-key input** later in Epic 5 / AR5).

**Why tree-sitter, not embeddings (architecture §Decision B, cross-cutting #1).** APAA does STRUCTURAL search
— it grounds a deep claim against the real AST, not a fuzzy vector match. The 0.25 API loads grammars via the
per-language package (`import tree_sitter_python; Language(tree_sitter_python.language())`) — note this is the
0.25-era API, distinct from older `Language.build_library(...)` patterns (architecture §Starter NEW deps note).

**Why the stack-agnostic `claim → validated?` seam matters NOW (NFR-P2).** V1 deep AST grounding is
**Python only**. The ledger/verdict core must carry NO host-/stack-specific logic — a non-Python file must
route to the `claim_emitted` proxy path through a stack-agnostic interface so V2 multi-language is purely
additive. This story establishes that the index/intake layer KNOWS which files are AST-eligible (Python) vs
proxy-only, and exposes that distinction WITHOUT leaking language conditionals into `ledger`/`verdict`
(those stay pure and stack-agnostic).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 1.4) and the architecture (Decision B §Repository Intake &
> Indexing, §Pure/Impure Separation, §Determinism Patterns, §Error/Degradation Patterns, §Architectural
> Boundaries, AR1/AR4/AR8/AR10). Drivers: **APAA-FR-1** (headless repo intake @ pinned commit), **APAA-FR-2**
> (stack/toolchain auto-detection, no operator config), **APAA-NFR-P2** (stack-agnostic by construction —
> deep AST = Python in V1; `claim_emitted` proxy elsewhere; no host-/stack-specific logic in ledger/verdict
> core), **AR1** (the sanctioned external deps — `tree-sitter` / `tree-sitter-python` / `radon`, grammar
> version recorded for the Epic-5 cache key), **AR4** (single canonical serializer — no second `json.dumps`;
> no float/clock/uuid/random/iteration-order in any `.apaa/` write path), **AR8** (pure/impure separation —
> intake/index/stack-detect are the IMPURE shell; the index DATA model is a frozen pure contract),
> **AR10** (typed failure at the impure shell — a parse/tool failure degrades, never an uncaught raise),
> **AR11** (`.apaa/` writes content-addressed, never arrival order), **APAA-NFR-S5** (any `.apaa/` write goes
> through the Story 1.3 containment shell), **APAA-NFR-M1** (≤1200-line files).
>
> **SCOPE FENCE.** This story delivers ONLY: repo intake (load @ pinned commit), stack detection, the
> tree-sitter Python AST/code-graph index, and the stack-agnostic AST-eligibility routing seam. It does NOT
> build: detectors / the vacuous-test rule (Story 1.5), the pure verdict gate (Story 1.6), the CLI / pipeline
> wiring (Story 1.7), repository PARTITIONING into bounded units (`index/partitioner.py` is Story 2.4 — this
> story may create the file as a thin placeholder ONLY if needed for `partition_id="root"` continuity, but the
> graph-partitioning LOGIC is Story 2.4), the LLM dispatch port / adapter (Epic 6), the zero-token breadth
> TOOL RUNNER as a detector (`detectors/tool_runner.py` is Story 2.6 — this story may invoke `radon`/`cloc`
> for STACK DETECTION only, not as the breadth-detector phase), the cache/memo store (Epic 5), and the
> cartridge self-audit harness (Epic 6).

**AC1 — Repo intake @ a pinned commit, refusing a drifted tree (FR1)**
**Given** a repository path + a pinned commit (a full/short SHA or ref resolved to a SHA)
**When** `intake/repo_loader.py` loads it
**Then** it reads the source tree at that commit and **refuses to proceed (raises a typed error) if the
working tree does not match the pin** — i.e. it verifies the checked-out/HEAD state corresponds to the
requested commit (e.g. `git rev-parse HEAD` equals the pin, and the working tree is clean OR the load reads
the committed tree at the pin), so an audit can never silently audit uncommitted drift
**And** the loader returns a frozen `RepoIntake` model carrying the resolved commit SHA, the audited-repo
root, and the discovered source-file set (relative POSIX paths) — never an absolute host path persisted into
an artifact (NFR-S1 spirit / Story 1.3 DN-3 precedent)
**And** a missing repo / non-existent path / unresolvable commit / dirty-tree-vs-pin mismatch raises a TYPED
`RepoIntakeError(ValueError)` (or a documented reused typed error), NEVER a bare crash or a silent
empty-tree (AR10).

**AC2 — Stack & toolchain detection with NO operator configuration (FR2)**
**Given** a loaded repo
**When** stack detection runs in `intake/stack_detect.py`
**Then** it identifies the repository's technology stack (V1 cares about: is this a Python codebase?) and the
available toolchain — using `radon>=4` (zero-token metric availability) + tree-sitter grammar availability +
lightweight file-extension/marker heuristics (`*.py`, `pyproject.toml`/`setup.py`/`requirements.txt`),
**with NO operator configuration required** (auto-detection is the contract)
**And** the result is a frozen `StackProfile` model recording at minimum: `primary_language` (`"python"` /
`"other"` / `"unknown"`), the set of detected languages, and a `toolchain` availability map (e.g.
`radon_available: bool`, `tree_sitter_python_available: bool`, optionally `cloc_available: bool` —
`cloc` is OPTIONAL/best-effort, its absence is recorded, not fatal — AR10)
**And** a tool that is unavailable / errors during probing is recorded as `available: false` (a degraded but
honest profile), never an uncaught crash (FR14 spirit / NFR-R1; the full tool-failure-AS-FINDING is Story 2.6).

**AC3 — The tree-sitter Python AST / code-graph index (FR7-subset substrate, Decision B, AR1)**
**Given** a Python source tree (the files `RepoIntake` discovered)
**When** the AST index is built by `index/ast_index.py`
**Then** it uses `tree-sitter` + `tree-sitter-python` (the 0.25 per-language-package API:
`Language(tree_sitter_python.language())` → `Parser`) to parse each Python file into a structural
code-graph — at minimum the per-file definitions (functions/classes with their 1-based line spans) and a
call/reference edge set sufficient for the later orphan/dead-code (Epic 6) and vacuous-path (Story 1.5)
passes — **structural search, NOT embeddings**
**And** the **resolved tree-sitter grammar version is recorded** in the index result (a `grammar_version`
field) so it can feed the Epic-5 / AR5 determinism cache key (this story only RECORDS it; the cache key is
Epic 5)
**And** the index exposes per-file AST node spans usable as a `Locator.ast_span` (the Story 1.2 `Locator`
reserves `ast_span`) so downstream findings can cite an AST span, not just a line range.

**AC4 — Non-Python files route to the `claim_emitted` proxy via the stack-agnostic seam (NFR-P2)**
**Given** a non-Python file (or a Python file tree-sitter cannot parse)
**When** it is indexed
**Then** deep AST analysis is **unavailable** for it and the file is routed to the `claim_emitted` proxy
path via a stack-agnostic `claim → validated?` interface (an `ast_eligible: bool` / depth-eligibility
classification on the index entry), so the downstream depth audit knows it can only ground a `claim_emitted`
proxy there — Python is implementation #1 of the seam, and V2 multi-language is purely additive
**And** **no host-/stack-specific logic leaks into the `ledger`/`verdict` core** (the language conditional
lives ONLY in the `index`/`intake` layer; `ledger/coverage_ledger.py` and `ledger/recording.py` are NOT
modified to add a language field beyond what 1.2 already reserves) — NFR-P2.

**AC5 — Parse / tool failure degrades to a typed/recorded condition, never an uncaught raise (AR10, NFR-R1)**
**Given** a file tree-sitter fails to parse (syntax error, encoding error, binary file), or a stack-detection
tool that crashes / times out / is unavailable
**When** the index / detection runs over it
**Then** the failure is captured as a per-file/per-tool DEGRADED outcome on the result model (e.g. an
index entry marked `parse_failed: true` with a reason token, or a `toolchain` entry `available: false`) —
the run continues and produces a (degraded) index + profile, NEVER an uncaught crash out of the intake/index
layer, NEVER a fabricated successful parse, and NEVER a bare `except: pass` (AR10)
**And** the degraded condition carries enough to later mint a `parse_failure` / `tool_failure` finding +
coverage downgrade (the FINDING emission itself is Story 1.5 / Story 2.6; this story produces the honest
degraded DATA, not the finding).

**AC6 — Index / intake DATA models are frozen pure contracts; the layer is the impure shell (AR8)**
**Given** the new modules
**When** they are implemented
**Then** the result DATA models (`RepoIntake`, `StackProfile`, the AST-index models — names dev's choice,
documented) are **frozen Pydantic v2 contracts** (`frozen=True, extra="forbid"`, additive-only —
NFR-M2/M1), carry NO `float` (line numbers `int`; any ratio `Decimal`/`Fraction` — AR4), and are
construction-pure (no clock/uuid/random in the model layer)
**And** the I/O — reading repo files, invoking git, invoking `radon`/`cloc`, running the tree-sitter parser —
is confined to the IMPURE `intake/`/`index/` modules (the architecture classifies `intake`/`index` as the
impure shell), and any `.apaa/` write goes through the Story 1.3 `store/writer.py` + `store/paths.py`
containment shell (no direct `open(...,'w')` / `Path.write_*` into `.apaa/`, no second serializer — AR4/NFR-S5)
**And** the four pure modules from 1.1/1.2 (`canonical`, `envelope`, `coverage_ledger`, `recording`) and the
Story 1.3 store shell are NOT modified to add intake/index concerns (only the import-isolation gate is
extended — AC8).

**AC7 — `.apaa/` intake/index artifacts (if persisted) are content-addressed + envelope-wrapped (AR4/AR11/FR25)**
**Given** an intake/index result the pipeline will later re-read (resumability seam)
**When** it is persisted to `.apaa/state/` (this story MAY persist the intake + index snapshot so 1.7's
pipeline / Epic-3 resume can re-load it; if the dev defers persistence to 1.7, document that and skip this AC's
write half — the read primitive already exists in 1.3)
**Then** the write goes through `EnvelopeWriter.build` + `store/canonical.dumps_bytes` + the
`ApaaStorePaths`-resolved, content-addressed (`<content_hash>.json`) path — REUSING the 1.1/1.3 spine with NO
second serializer and NO arrival-order/`uuid4`/clock filename
**And** re-reading via `store/reader.py` reconstructs an equal model and round-trips byte-identically (NFR-P1),
verified by a round-trip test (mirrors the 1.3 `test_store_roundtrip` pattern).

**AC8 — Import-isolation gate extended and green; tree-sitter does NOT pull the web stack (AR7/AR9)**
**Given** the new intake/index modules
**When** the `tests/apaa/` suite runs
**Then** `tests/apaa/test_no_web_imports.py`'s `_MODULES_UNDER_GUARD` tuple is EXTENDED with the new modules
(`minions_core.apaa.intake.repo_loader`, `minions_core.apaa.intake.stack_detect`,
`minions_core.apaa.index.ast_index`, + any new sibling) and the gate stays green — importing them does NOT
transitively pull `fastapi`/`uvicorn`/`starlette` (the parsing toolchain is web-free; do NOT fork the gate)
**And** the Story 1.1 single-serializer AST gate (`tests/apaa/test_canonical_single_serializer.py`) still
passes with the new modules present (no direct `json.dumps(` in any new module).

**AC9 — The whole APAA suite green + dependency availability handled honestly (NFR-M1, test infra)**
**Given** the modules + tests added by this story
**When** `PYTHONIOENCODING=utf-8 pytest tests/apaa/` + `tests/test_import_paths.py` run
**Then** all pass: a new `tests/apaa/test_repo_intake.py` (intake @ pin + drift-refusal + typed errors), a
new `tests/apaa/test_stack_detect.py` (Python-detected / non-Python / degraded-toolchain cases), and a new
`tests/apaa/test_ast_index.py` (definitions + spans extracted from a fixture Python file; non-Python →
proxy-eligible; unparseable → degraded) — using `tmp_path` fixtures and small in-repo fixture sources
**And** because `tree-sitter`/`tree-sitter-python`/`radon` are OPTIONAL-extra deps, the tests either (a)
assume the `[apaa]` extra is installed in the dev/CI env (preferred — document the `pip install -e ".[apaa]"`
prerequisite in the story Dev Agent Record), or (b) `pytest.importorskip(...)` the tree-sitter-dependent
assertions so the suite degrades cleanly where the extra is absent — pick one, document it; either way the
import-isolation + intake/stack-detect logic that does NOT require tree-sitter stays unconditionally tested
**And** every new source file is ≤1200 lines (NFR-M1) and cites its `APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in
the module docstring; `mypy` is clean on the new modules.

## Tasks / Subtasks

### Review Findings

<!-- defer-schema-session: 2026-06-21 -->

Code-review iteration 2 (2026-06-21, RE-REVIEW after fix). The iteration-1 Medium defect is **resolved and adversarially verified** — verdict PASS, status `done`. Detail in `## Senior Developer Review (AI)` below.

- [x] [Review][Patch] `git ls-files` quotes/omits non-ASCII source paths — `intake/repo_loader.py:154-161` — **RESOLVED (iter-2 verified)**. git's default `core.quotepath=true` made `git ls-files` emit a non-ASCII path as a double-quoted, octal-escaped token (e.g. `"caf\303\251.py"`), whose `Path(line).suffix` was `.py"`, silently dropping the file from `RepoIntake.source_files` (AC1 / AR11 audit-integrity defect). Fixed by enumerating with `git ls-files -z` (split on `\0`, no `.strip()`/`splitlines()`) AND decoding git stdout as UTF-8 explicitly in `_run_git` (capture bytes, `decode("utf-8", errors="replace")` — was `text=True` → cp1252 mojibake on Windows). Reviewer independently reproduced old `git ls-files` → `"caf\303\251.py"` (suffix `.py"` → dropped) vs new `git ls-files -z` → raw bytes `caf\xc3\xa9.py\x00` → decode → `café.py` (suffix `.py` → included). Regression test `test_unicode_named_python_source_is_included_unmangled` (TC-APAA-INTAKE-001-78) genuinely RED-on-old (asserts `("café.py", "naïve_dir/résumé.py", "plain.py")` + no quote/escape leakage). Invalid-UTF-8 from git degrades sanely via `errors="replace"` (no new crash). `git status --porcelain` drift check unaffected.

- [ ] [Review][Defer] Edge-set richness is unresolved-name only (no scope binding) — `index/ast_index.py:186-231` — `CodeEdge` captures the bare callee identifier / trailing attribute with no name binding or scope resolution. This is the documented, AC-sanctioned V1 substrate (Epic-6 owns the resolved call graph), so it is NOT a defect — recorded only so the downstream 1.5/Epic-6 consumers know the edge set is unresolved. id=DF-1-4-A · origin_story=1-4-tree-sitter-ast-index-repo-intake-python-stack-detection · owner=Engineering Lead · target_story=epic-6-orphan-dead-code-detector · category=other · severity=🟢


  - [x] `pip install -e ".[apaa]"` (the extra already declares `tree-sitter>=0.25` + `tree-sitter-python>=0.25`
        + `radon>=4` — no pyproject change needed unless a hard pin is desired). Record the EXACT resolved
        versions in the Dev Agent Record (the grammar version is an Epic-5 cache-key input — AR5).
  - [x] Confirm the 0.25 API shape: `import tree_sitter_python as tsp; from tree_sitter import Language, Parser;
        Parser(Language(tsp.language()))` parses a trivial Python snippet.
- [x] **Task 1 — Repo intake @ pinned commit** (AC: 1, 6)
  - [x] Create `minions_core/apaa/intake/__init__.py` (sub-package) + `intake/repo_loader.py` (docstring cites
        `APAA-FR-1`, `AR8`, `AR10`).
  - [x] Define the frozen `RepoIntake` model (resolved commit SHA, audited-repo root as a path the layer holds
        but does NOT persist absolute, the relative-POSIX source-file set) + `RepoIntakeError(ValueError)`.
  - [x] Load @ pin: resolve the commit, VERIFY the working tree matches the pin (refuse on drift), enumerate
        source files. Use `git` via subprocess OR read the committed tree — document the choice; degrade to a
        typed error on any failure (no bare crash, no silent empty tree).
- [x] **Task 2 — Stack & toolchain detection (no operator config)** (AC: 2, 5, 6)
  - [x] Create `intake/stack_detect.py` (docstring cites `APAA-FR-2`, `APAA-NFR-P2`, `AR1`, `AR10`).
  - [x] Define the frozen `StackProfile` (primary_language, detected languages set, `toolchain` availability
        map). Detect Python via extensions + markers; probe `radon`/tree-sitter availability; `cloc` optional.
  - [x] An unavailable/erroring tool → `available: false` recorded (degraded, honest), never a crash.
- [x] **Task 3 — tree-sitter Python AST / code-graph index** (AC: 3, 4, 5, 6)
  - [x] Create `minions_core/apaa/index/__init__.py` (sub-package) + `index/ast_index.py` (docstring cites
        `APAA-FR-7`-subset substrate, `Decision B`, `AR1`, `AR8`, `AR10`, `APAA-NFR-P2`).
  - [x] Build the parser once (`Language(tsp.language())` → `Parser`); per Python file extract definitions
        (functions/classes + 1-based line spans) + a call/reference edge set; record the resolved
        `grammar_version`.
  - [x] Frozen index DATA models (per-file entry: path, `ast_eligible: bool`, definitions, spans,
        `parse_failed`+reason); expose spans usable as `Locator.ast_span`.
  - [x] Non-Python / unparseable → `ast_eligible=false` / `parse_failed=true` routed to the `claim_emitted`
        proxy via the stack-agnostic `claim→validated?` seam — NO language conditional in `ledger`/`verdict`.
- [x] **Task 4 — (Optional) persist intake+index snapshot via the 1.3 store shell** (AC: 7)
  - [x] If persisting now: wrap the intake+index result via `EnvelopeWriter.build` and write through
        `store/writer.py` (content-addressed `<content_hash>.json` under `.apaa/state/`, containment-checked).
        Round-trip via `store/reader.py`. If deferring to Story 1.7, document the deferral in Dev Notes and skip.
- [x] **Task 5 — Tests** (AC: 1, 2, 3, 4, 5, 8, 9)
  - [x] `tests/apaa/test_repo_intake.py` — load @ pin succeeds on a fixture git repo (or committed-tree read);
        drift/dirty-vs-pin REFUSES with `RepoIntakeError`; missing path / bad commit → typed error.
  - [x] `tests/apaa/test_stack_detect.py` — Python fixture → `primary_language="python"`; non-Python fixture →
        `"other"`/`"unknown"`; a forced-unavailable tool → `available: false`, no crash.
  - [x] `tests/apaa/test_ast_index.py` — a fixture `.py` yields expected definitions + line spans; a non-Python
        file → `ast_eligible=false` proxy route; a syntactically-broken `.py` → `parse_failed=true`, run continues.
  - [x] (If Task 4 done) `tests/apaa/test_intake_index_roundtrip.py` — envelope-wrapped write → read → equal
        model + byte-identical re-serialize (NFR-P1).
- [x] **Task 6 — Extend the import-isolation gate** (AC: 8)
  - [x] Append the new modules to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py` (do NOT fork
        the gate). Confirm `tree-sitter`/`tree-sitter-python`/`radon` import does not leak the web stack.
- [x] **Task 7 — Run + mypy** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass (the 1.1
        single-serializer AST gate re-runs with the new modules present; the extended no-web-imports gate green).
  - [x] `mypy` clean on the new modules (`python run_mypy_per_file.py` or scoped).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **Pure/impure separation (master rule, AR8).** The architecture classifies `intake/` and `index/` as the
  IMPURE shell (they read files, run git, run `radon`/`cloc`, run the tree-sitter parser). All that I/O lives
  here. But the RESULT DATA models (`RepoIntake`, `StackProfile`, the index entries) are frozen pure contracts
  — construction-pure, no clock/uuid/random, no float. ✅ `ast_index` runs the parser then builds a frozen
  model · ❌ a frozen model method that reads a file or calls the parser.
- **Stack-agnostic by construction (NFR-P2 — the keystone for this story).** Deep AST = Python in V1; every
  other file routes to the `claim_emitted` proxy via a stack-agnostic `claim → validated?` interface. The
  language conditional belongs ONLY in `intake`/`index` (the `ast_eligible` classification). The `ledger` and
  `verdict` core must stay language-free so V2 multi-language is additive. Do NOT add a `language` field to
  `coverage_ledger`/`recording` (1.2 already reserves what the verdict needs); surface AST-eligibility on the
  INDEX entry instead.
- **One serializer, forever (AR4, cross-cutting #3).** If this story persists anything to `.apaa/`, the bytes
  go through `store/canonical.dumps_bytes` via `store/writer.py` — never a direct `json.dumps(`. The committed
  `tests/apaa/test_canonical_single_serializer.py` AST gate fails the build on a direct `json.dumps(` in any
  new module. (`radon`/`tree-sitter` produce in-memory structures, not `.apaa/` bytes — those go through the
  serializer only when persisted.)
- **Containment for any `.apaa/` write (NFR-S5, reuse Story 1.3).** Any persistence goes through
  `ApaaStorePaths` (`store/paths.py`) + `store/writer.py` — `Path.resolve()` + `is_relative_to`, never
  `str.startswith`. Do NOT write a second path/containment path; do NOT `open(...)` into `.apaa/` directly.
- **No absolute host paths in artifacts (NFR-S1 spirit, Story 1.3 DN-3).** The audited-repo source paths
  persisted in `RepoIntake` / index entries are RELATIVE POSIX (repo-root-relative). The absolute root is held
  in-memory by the impure layer but never serialized into an artifact / error message / locator.
- **Error/degradation → typed/recorded, never crash (AR10, NFR-R1).** A bad repo / bad commit / dirty tree →
  `RepoIntakeError`. A parse failure / tool unavailability → a recorded degraded outcome on the result model
  (so a later story can mint a `parse_failure`/`tool_failure` finding). NO bare `except: pass`, NO `print()`
  in library code, NO fabricated successful parse, NO silent empty result.
- **Headless / import boundary (§Architectural Boundaries, AR7/AR9).** APAA is downstream of the HTTP/A2A
  boundary — these modules take no token, register no FastAPI route, import no web stack. Never import
  `minions_core.api.* / services.api_app / app_factory / api_server`. The new modules join
  `_MODULES_UNDER_GUARD`.

### The sanctioned dependency question (explicit per the spawn directive)

**No HALT — the parsing dependency is already named AND staged, this story does not introduce a net-new
sanctioned tool.** Architecture **AR1** ("New external dependencies — the only genuine starter choices,
versions verified June 2026: `tree-sitter==0.25.2` + `tree-sitter-python==0.25.0` … `radon==4.1.0` … All land
in the `minions[apaa]` extra") and **Decision B** ("AST/code-graph index FIRST via `tree-sitter==0.25.2` +
`tree-sitter-python==0.25.0`") sanction the toolchain. `pyproject.toml`
`[project.optional-dependencies].apaa` already declares `tree-sitter>=0.25`, `tree-sitter-python>=0.25`,
`radon>=4` (verified present this session). **How to add it:** nothing to add — install the existing extra
(`pip install -e ".[apaa]"`). If the dev decides a HARD pin (`==0.25.2` / `==0.25.0`) is preferable over the
`>=` floor for determinism reproducibility, that is an additive pyproject edit consistent with AR1's verified
versions and the AR5 grammar-version cache-key requirement — record the exact resolved version regardless,
because Epic 5 folds it into the cache key. The `cloc` tool referenced in the epic AC ("via `cloc`/`radon`")
is an OPTIONAL system binary, not a Python dep — its absence is recorded honestly (AC2), not fatal.

### Precedent inherited from Stories 1.1/1.2/1.3 (done) — honor these decisions

- **No second serializer / reuse the 1.1 spine.** `store/canonical.py` + `store/envelope.py` are the only
  serializer + envelope; reuse them verbatim for any persistence. The AST gate enforces it.
- **Reuse the 1.3 containment shell, do not re-implement.** `ApaaStorePaths` + `store/writer.py` +
  `store/reader.py` already provide containment-checked, content-addressed, envelope-wrapped write + pure
  read-back. Any `.apaa/` persistence in this story goes THROUGH them — mirror the 1.3 round-trip golden
  pattern (`tests/apaa/test_store_roundtrip.py`).
- **Frozen `extra="forbid"` models** (1.1 `Envelope`, 1.2 `Recording`/`CoverageLedger`, `Locator`): the new
  `RepoIntake`/`StackProfile`/index models follow the SAME pattern — an unknown field on read-back is a typed
  `ValidationError`, not silent acceptance.
- **`Locator.ast_span` is already reserved** (1.2 `recording.py:76` — "Reserved optional AST-node span
  reference (Story 6.2)"). The index this story builds is the SOURCE of those AST spans — expose spans in a
  shape that drops into `Locator.ast_span` so 1.5's findings can cite them. Do NOT modify `Locator`.
- **`partition_id` is always `"root"` in V1** (1.2 reserves it). Partitioning is Story 2.4 — this story
  operates on the single `"root"` partition; do NOT build the partitioner.
- **`apaa_version` single source** — `minions_core/apaa/__init__.py::__version__` (`"0.1.0"`), passed through
  `EnvelopeWriter` (which defaults to it). Per-artifact `schema_version` is a module constant, never env/clock.
- **`APAA-STORE` / `APAA-LEDGER` test-area precedent** — use area `APAA-INTAKE` and `APAA-INDEX` for this
  story's test ids (`TC-APAA-INTAKE-001-NN`, `TC-APAA-INDEX-001-NN`), consistent with the 1.x convention.
- **Import-isolation gate is seeded, extend it** — `tests/apaa/test_no_web_imports.py::_MODULES_UNDER_GUARD`
  is a tuple "later stories APPEND to". Append the new modules; do not fork.

### Source tree — files to create (all NEW; the only UPDATE is the import-isolation gate)

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/intake/__init__.py` | NEW | `intake/` sub-package shell (docstring) |
| `minions_core/apaa/intake/repo_loader.py` | NEW | FR1 — load repo @ pinned commit; `RepoIntake` + `RepoIntakeError`; drift refusal |
| `minions_core/apaa/intake/stack_detect.py` | NEW | FR2 — stack/toolchain auto-detection (`radon`/tree-sitter/markers); `StackProfile` |
| `minions_core/apaa/index/__init__.py` | NEW | `index/` sub-package shell (docstring) |
| `minions_core/apaa/index/ast_index.py` | NEW | Decision B — tree-sitter Python code-graph index; AST-eligibility seam; `grammar_version` |
| `tests/apaa/test_repo_intake.py` | NEW | intake @ pin + drift-refusal + typed errors |
| `tests/apaa/test_stack_detect.py` | NEW | Python / non-Python / degraded-toolchain detection |
| `tests/apaa/test_ast_index.py` | NEW | definitions + spans; non-Python proxy route; unparseable degrade |
| `tests/apaa/test_intake_index_roundtrip.py` | NEW (only if Task 4 persists) | envelope round-trip byte-stability |
| `tests/apaa/test_no_web_imports.py` | UPDATE | extend `_MODULES_UNDER_GUARD` with the new modules |

The architecture's package tree (`architecture.md` §Project Structure) places EXACTLY `intake/repo_loader.py`,
`intake/stack_detect.py`, `index/ast_index.py`, and `index/partitioner.py` in these sub-packages.
`partitioner.py` is **Story 2.4** — do NOT build it here. Do not invent additional modules; the verdict gate
is `verdict/` (1.6), detectors are `detectors/` (1.5), the LLM seam is `audit/` (Epic 6), the CLI/pipeline are
`cli.py`/`pipeline.py` (1.7). Resist building ahead.

### Reuse — what already exists (verified present) and what NOT to reinvent

- **Story 1.1 store spine** (`store/canonical.py` + `store/envelope.py` — present): `canonical.dumps_bytes` /
  `canonical.loads` / `CanonicalSerializationError`; `Envelope`, `EnvelopeWriter.build`, `compute_content_hash`,
  `GENESIS_PREV_HASH`. REUSE for any persistence + goldens — no second serializer.
- **Story 1.2 ledger/recording models** (`ledger/coverage_ledger.py` + `ledger/recording.py` — present):
  `CoverageDepth`, `CoverageLedger*`, `grade_entry`; `Locator` (with reserved `ast_span`), `Recording`,
  `RecordingValidationError`. The index feeds `Locator.ast_span`; do NOT modify these pure models.
- **Story 1.3 store shell** (`store/paths.py` + `store/writer.py` + `store/reader.py` — present):
  `ApaaStorePaths` (containment-checked resolver, fixed `.apaa/` tree, `WorkspaceContainmentError` reused),
  content-addressed writer, pure reader (+ `StoreIntegrityError`). REUSE for any `.apaa/` write/read.
- **Pydantic v2** — baseline dep, reuse `BaseModel`/`ConfigDict(frozen=True, extra="forbid")`.
- **`tree-sitter` / `tree-sitter-python` / `radon`** — declared in the `minions[apaa]` extra (verified
  present in `pyproject.toml`). Install via the extra; do NOT add a parallel/unsanctioned parser.
- **`minions_core/apaa/__init__.py::__version__`** (`"0.1.0"`) — the single `apaa_version` source.

### Determinism / contract decisions the dev must lock (record the choice in the docstring)

- **Repo-load mechanism** — read the committed tree at the pin via `git` subprocess (e.g.
  `git -C <repo> rev-parse <commit>` + `git ls-tree`/`git show`) vs. assert the working tree's HEAD == pin and
  read the working tree. Either is acceptable; the binding constraint is **refuse on drift** (FR1) and degrade
  to `RepoIntakeError` on failure. Document the choice + how "drift" is defined.
- **Index granularity** — the minimum is per-file definitions (functions/classes + 1-based spans) + a
  call/reference edge set. Decide how rich the edge set is in V1 (enough for the 1.5 vacuous-path reachability
  check + the Epic-6 orphan detector) and document it; do NOT over-build a full call-graph resolver (that is
  Epic 6 depth) — produce the structural substrate the spine needs.
- **AST-eligibility surface** — name the field/shape that distinguishes AST-eligible (Python, parsed) from
  proxy-only (non-Python / parse-failed) files (`ast_eligible: bool` recommended) and document that the
  `claim → validated?` seam keys off it — with the conditional confined to `index`/`intake`.
- **Grammar-version capture** — record the resolved `tree-sitter-python` grammar version in the index result
  (a `grammar_version` field). This story only RECORDS it; the Epic-5/AR5 cache key folds it later.
- **Persist-now vs defer to 1.7** — decide whether the intake+index snapshot is persisted to `.apaa/state/`
  in THIS story (via the 1.3 shell) or deferred to the 1.7 pipeline. If deferred, document it and skip AC7's
  write half (the read primitive already exists in 1.3).
- **Optional-dep test strategy** — `pip install -e ".[apaa]"` in dev/CI (preferred) vs.
  `pytest.importorskip` for the tree-sitter-dependent assertions. Pick one, document it (AC9).

### Scope fences (do NOT pull forward)

- ❌ **Detectors / the vacuous-test rule** (`detectors/vacuous_test.py`, `detectors/base.py`) — Story 1.5.
  This story builds the AST substrate the rule folds over; it emits NO findings.
- ❌ The pure-function **verdict gate** (`verdict/verdict_gate.py`) — Story 1.6.
- ❌ The **CLI / pipeline wiring** (`cli.py` / `pipeline.py`) — Story 1.7.
- ❌ Repository **PARTITIONING** into bounded units (`index/partitioner.py`) — Story 2.4. V1 is single
  `partition_id="root"`.
- ❌ The **zero-token breadth TOOL RUNNER as the detector phase** (`detectors/tool_runner.py`) — Story 2.6.
  This story may invoke `radon`/`cloc` for STACK DETECTION only, not as the breadth-detector pass.
- ❌ The **LLM dispatch port / adapter** (`audit/*`) + deep-claim AST grounding over the FULL AST
  (`audit/deep_audit.py`, FR7 general) — Epic 6. This story builds the index; it does not ground claims.
- ❌ The **cache / memo store** (`cache/key.py`, `cache/memo_store.py`) — Epic 5. This story RECORDS the
  grammar version that the cache key later consumes; it does not build the key.
- ❌ The **cartridge self-audit harness** + holdout/clean controls — Epic 6 / Story 6.5.

### Testing standards

- pytest under `tests/apaa/`; test ids follow `TC-<AREA>-<SEQ>-<SUBSEQ>` — use areas `APAA-INTAKE` /
  `APAA-INDEX` (e.g. `TC-APAA-INTAKE-001-70`, `TC-APAA-INDEX-001-70`), consistent with the 1.x convention
  (`APAA-STORE`, `APAA-LEDGER`).
- The intake/index tests USE the filesystem (impure shell) — use `pytest`'s `tmp_path` + small fixture source
  files. For the repo-load-@-pin test, build a tiny throwaway git repo under `tmp_path` (or read a committed
  tree), assert the drift-refusal explicitly.
- `tree-sitter`/`tree-sitter-python`/`radon` are optional-extra deps: install `[apaa]` in dev/CI (preferred)
  or `pytest.importorskip` the tree-sitter assertions (document the choice). The non-tree-sitter logic
  (intake, drift refusal, stack-marker detection, the import-isolation gate) stays unconditionally tested.
- On Windows, prefix runs with `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on cp1252).
- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` (the WHOLE `tests/apaa/`
  suite, so the 1.1 single-serializer AST gate + the extended no-web-imports gate re-run with the new modules
  present). All must pass before moving to `review`.
- `mypy` clean on the new modules (`python run_mypy_per_file.py` or a scoped invocation).

### CLAUDE.md §4a follow-up

The §4a APAA Component→Driver row was already added by Story 1.1. This story does NOT need a new §4a row; if a
one-line additive note is added it must note `intake/repo_loader.py` + `intake/stack_detect.py` +
`index/ast_index.py` as the impure repo-intake + tree-sitter Python AST-index layer (FR1/FR2 + the stack-
agnostic `claim→validated?` seam), and must NOT rewrite the existing row. Keep it minimal — a new row is not
required.

### Project Structure Notes

- Alignment: file paths exactly match `architecture.md` §Project Structure package tree (`intake/repo_loader.py`,
  `intake/stack_detect.py`, `index/ast_index.py`). `index/partitioner.py` is deferred to Story 2.4. Naming
  `snake_case.py`, ≤1200 lines (NFR-M1). JSON/enum values `snake_case`.
- No conflicts/variances. Judgment calls — all decided above and to be documented so they freeze for
  downstream: the repo-load mechanism + drift definition, the index granularity + edge-set richness, the
  AST-eligibility surface, the grammar-version capture, the persist-now-vs-defer choice, and the optional-dep
  test strategy.
- Scope fence: this story delivers repo intake + stack detection + the tree-sitter Python AST index + the
  stack-agnostic AST-eligibility routing seam ONLY. Detectors (1.5), verdict (1.6), CLI/pipeline (1.7),
  partitioner (2.4), tool-runner detector (2.6), LLM/deep-audit (Epic 6), cache (Epic 5) are explicitly NOT in
  scope. Build the intake + index complete-and-contained, then stop.

### References

- [Source: _bmad-output/design-artifacts/APAA/epics.md#Story-1.4 tree-sitter AST index, repo intake & Python stack detection]
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#B. Repository Intake & Indexing] (AST/code-graph index FIRST via tree-sitter 0.25.x; graph-derived partitioning deferred; stack detection via cloc/radon/tree-sitter; deep=Python, claim_emitted proxy elsewhere)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Additional Requirements AR1] (sanctioned external deps + versions; grammar version → determinism cache key)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Pure/Impure Separation (master rule)] (intake/index = impure shell; result models pure)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Determinism Patterns (NFR-P1/D1)] (one serializer; no float/clock/uuid/random/iteration-order)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Error / Degradation Patterns] (failure → typed finding/recorded condition, never an uncaught raise; no bare except: pass / print())
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Architectural Boundaries] (import boundary; downstream of HTTP/A2A; LLM boundary not crossed here)
- [Source: _bmad-output/design-artifacts/APAA/architecture.md#Project Structure & Boundaries] (package tree: intake/, index/; partitioner.py is Story 2.4)
- [Source: _bmad-output/design-artifacts/APAA/E-PRD/prd.md#FR1 repo @ pinned commit / FR2 stack auto-detection / FR7 Python AST grounding (substrate) / NFR-P2 stack-agnostic by construction / NFR-R1 honest degradation]
- [Source: _bmad-output/design-artifacts/APAA/stories/1-1-canonical-serializer-content-hashed-envelope.md] (DONE — serializer + envelope spine + `_MODULES_UNDER_GUARD` seed + single-serializer AST gate)
- [Source: _bmad-output/design-artifacts/APAA/stories/1-2-fixed-enum-coverage-ledger-frozen-recording-schema.md] (DONE — ledger/recording; `Locator.ast_span` reserved; `partition_id="root"`; frozen extra="forbid")
- [Source: _bmad-output/design-artifacts/APAA/stories/1-3-apaa-store-writer-reader-filesystem-containment.md] (DONE — `ApaaStorePaths` + writer/reader to REUSE for any `.apaa/` persistence; round-trip golden pattern)
- [Source: minions_core/apaa/store/canonical.py + store/envelope.py] (single serializer + envelope to reuse)
- [Source: minions_core/apaa/store/paths.py + store/writer.py + store/reader.py] (the impure `.apaa/` shell to reuse for persistence)
- [Source: minions_core/apaa/ledger/recording.py] (`Locator.ast_span` reserved for the AST spans this story produces)
- [Source: pyproject.toml [project.optional-dependencies].apaa] (tree-sitter>=0.25 + tree-sitter-python>=0.25 + radon>=4 already declared — install via `pip install -e ".[apaa]"`)
- [Source: CLAUDE.md §3.2 file-size / §3.7 headless-only / §3.8 12-Factor + secret masking / §4a APAA row]

## Dev Agent Record

### Agent Model Used

claude-opus-4-8 (BMAD Developer / dev-story, mode=implement)

### Debug Log References

EXACT resolved toolchain versions (the grammar version is an Epic-5/AR5 cache-key input):
- `tree-sitter == 0.25.2`
- `tree-sitter-python == 0.25.0` (this is the value recorded in `AstIndex.grammar_version`)
- `radon == 6.0.1`
- tree-sitter grammar ABI version: `15` (informational; `grammar_version` records the package version).

0.25 API confirmed: `Parser(Language(tree_sitter_python.language()))` parses Python; `tree.root_node.has_error`
flags a syntax error (used as the degraded-parse signal). `node.start_point[0]` is 0-based row → recorded
1-based. Call nodes: `function` field is an `identifier` (→ name) or `attribute` (→ trailing `attribute`
field name).

### Completion Notes List

- **Repo-load mechanism (locked).** `intake/repo_loader.py` reads the WORKING TREE and asserts it corresponds
  to the pin: `git rev-parse --verify <commit>^{commit}` resolves the pin, `git rev-parse HEAD` must equal it,
  and `git status --porcelain` must be empty. "Drift" = `HEAD != pin` OR non-empty porcelain (staged/unstaged/
  untracked). Source files enumerated from `git ls-files` (tracked/committed state), filtered to
  `.py/.pyi/.pyx`, sorted (AR11). All git/subprocess failures degrade to `RepoIntakeError(ValueError)` (AR10).
  `RepoIntake` carries only `commit_sha` + repo-root-relative POSIX `source_files` — the absolute root is held
  transiently and NEVER persisted (NFR-S1).
- **Stack detection (no config).** `intake/stack_detect.py` → frozen `StackProfile` (`primary_language` ∈
  python/other/unknown, sorted `detected_languages`, `ToolchainProfile`). Python detected from `.py/.pyi/.pyx`
  sources OR root markers (`pyproject.toml`/`setup.py`/`setup.cfg`/`requirements.txt`). Toolchain probed via
  `importlib.util.find_spec` (no side-effecting import; any failure → `False`) for `radon` + `tree_sitter`/
  `tree_sitter_python`; `cloc` via `shutil.which` (OPTIONAL, absence non-fatal — AR10). `detected_languages` is
  a SORTED tuple, never a `set` (AR4/AR11 — set order is non-deterministic).
- **AST index (Decision B).** `index/ast_index.py` builds the parser ONCE; per Python file extracts
  `Definition`s (function/class + 1-based spans; `Definition.ast_span` renders a `Locator.ast_span`-compatible
  `"<kind>:<name>@<start>-<end>"` token) and a `CodeEdge` call/reference set (identifier + trailing-attribute
  callee names) — structural substrate only, NOT a resolved call graph (no name binding/scope; that is Epic 6).
  `grammar_version` records `importlib.metadata.version("tree-sitter-python")` (AR1/AR5). Entries/defs/edges
  SORTED (AR11). `partition_id="root"` (Story 2.4 owns partitioning).
- **AST-eligibility seam (NFR-P2 — keystone).** Each `AstIndexEntry.ast_eligible` is `True` ONLY for a
  cleanly-parsed Python file; non-Python → `ast_eligible=False` + `parse_failure_reason="non_python"`; an
  unparseable Python file → `parse_failed=True` + `"syntax_error"` (via `root_node.has_error`) and the run
  CONTINUES (AR10 — degraded data, no crash, no fabricated parse, no bare `except: pass`). The language
  conditional is confined to `index`/`intake`; `ledger/coverage_ledger.py` + `ledger/recording.py` were NOT
  modified (no language field added). The downstream depth audit reads `ast_eligible` to route a `claim_emitted`
  proxy — V2 multi-language is purely additive.
- **Persistence (AC7 — persist-now via the 1.3 spine, no new module).** No new persistence source module was
  invented (DN scope fence). `test_intake_index_roundtrip.py` proves the existing Story 1.3
  `ApaaStoreWriter.write_payload` + `ApaaStoreReader.read_envelope` round-trip the new
  intake+stack+index snapshot byte-identically (content-addressed `state/<content_hash>.json`, single
  serializer, NFR-P1). The full pipeline write WIRING is Story 1.7; the spine is verified here.
- **Frozen pure contracts (AC6).** `RepoIntake` / `StackProfile` / `ToolchainProfile` / `Definition` /
  `CodeEdge` / `AstIndexEntry` / `AstIndex` are all `frozen=True, extra="forbid"`, construction-pure (no
  clock/uuid/random/float; line numbers `int`). All I/O (git, file reads, `find_spec`/`which`, the parser) is
  confined to the impure `intake`/`index` functions. No second `json.dumps` (the 1.1 single-serializer AST gate
  stays green); no direct `.apaa/` `open(...)` (any write goes through the 1.3 containment shell).
- **Import-isolation gate (AC8).** `_MODULES_UNDER_GUARD` extended (not forked) with `intake.repo_loader`,
  `intake.stack_detect`, `index.ast_index`; the tree-sitter import (local in `build_ast_index`) does not leak
  the web stack — gate green in clean subprocesses.
- **Optional-dep test strategy (AC9).** Chosen: `pytest.importorskip("tree_sitter"/"tree_sitter_python")` on
  the tree-sitter-dependent tests (`test_ast_index.py`, `test_intake_index_roundtrip.py`), so the suite
  degrades cleanly where the `[apaa]` extra is absent. The non-tree-sitter logic (intake/drift-refusal, stack
  marker/suffix detection, the import-isolation gate) is unconditionally tested. The extra IS installed in this
  env (`tree-sitter==0.25.2`, `tree-sitter-python==0.25.0`, `radon==6.0.1`) so all tree-sitter assertions ran.
- **Validation.** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass
  (138 APAA + import-paths). `mypy` clean on all 5 new modules. The 1.1 single-serializer gate + the extended
  no-web-imports gate re-ran green with the new modules present.

- **Fix iteration 1 (2026-06-21) — review Medium resolved.** Fixed the `git ls-files` non-ASCII path
  defect in `intake/repo_loader.py` (step 4 enumeration). Two coupled root causes: (a) git's default
  `core.quotepath=true` double-quoted + octal-escaped non-ASCII paths, so `Path(line).suffix` was `.py"`
  and the file was silently dropped — switched enumeration to `git ls-files -z` and split on the `\0` byte
  directly (no `.strip()`/`splitlines()`), which emits UNQUOTED paths; (b) `subprocess.run(..., text=True)`
  decoded git's UTF-8 path bytes with the platform default (cp1252 on Windows → `cafÃ©.py` mojibake) — now
  `_run_git` captures stdout as bytes and decodes UTF-8 explicitly (with `strip_output=False` for the NUL
  stream). The `git status --porcelain` drift check is unaffected (it only tests emptiness — a quoted path
  still makes porcelain non-empty = drift, the intended signal — so no change there). Regression test
  `test_unicode_named_python_source_is_included_unmangled` (TC-APAA-INTAKE-001-78) commits `café.py` +
  `naïve_dir/résumé.py`, asserts both appear in `source_files` with their real relative POSIX paths and no
  quote/escape leakage; written RED (reproduced both the drop and the mojibake) then GREEN. Suite:
  `PYTHONIOENCODING=utf-8 pytest tests/apaa/ tests/test_import_paths.py` → 291 passed (was 290, +1 regression);
  mypy clean on `repo_loader.py`. DF-1-4-A (edge-set unresolved-name) left as the recorded AC-sanctioned
  defer — not a defect, not changed.

### File List

NEW source:
- `minions_core/apaa/intake/__init__.py`
- `minions_core/apaa/intake/repo_loader.py`
- `minions_core/apaa/intake/stack_detect.py`
- `minions_core/apaa/index/__init__.py`
- `minions_core/apaa/index/ast_index.py`

NEW tests:
- `tests/apaa/test_repo_intake.py`
- `tests/apaa/test_stack_detect.py`
- `tests/apaa/test_ast_index.py`
- `tests/apaa/test_intake_index_roundtrip.py`

UPDATED:
- `tests/apaa/test_no_web_imports.py` (extended `_MODULES_UNDER_GUARD`)
- `_bmad-output/design-artifacts/APAA/sprint-status.yaml` (status → review; `last_updated` 2026-06-21)
- `_bmad-output/design-artifacts/APAA/stories/1-4-...md` (this file — Status, Dev Agent Record, Change Log)

## Senior Developer Review (AI)

**Reviewer:** claude-opus-4-8 (BMAD Reviewer / QA gate, `/bmad-code-review`)
**Date:** 2026-06-21 · **Iteration:** 2 (RE-REVIEW after fix) · **Verdict:** PASS → status `done`

### Iteration 2 outcome (re-review)

The single iteration-1 Medium defect (the `git ls-files` non-ASCII path drop/mangle) is **resolved and adversarially verified**. No new defects surfaced, no regressions, all ACs met — verdict PASS, status `done`.

**Fix verification (independent / adversarial):**
- **Defect genuinely fixed.** The reviewer reproduced both behaviours in a throwaway repo: old `git ls-files` emits `"caf\303\251.py"` (quoted, octal-escaped → `Path(...).suffix == '.py"'` → silently dropped); new `git ls-files -z` emits raw UTF-8 bytes `caf\xc3\xa9.py\x00` → split on `\0` → `decode("utf-8")` → `café.py` (suffix `.py` → included). The `-z` flag correctly bypasses `core.quotepath`; the NUL stream is split directly with `strip_output=False` (no `.strip()`/`splitlines()` corruption of the final record).
- **Byte→UTF-8 decode is correct and introduces no new failure mode.** `_run_git` now captures stdout as bytes and decodes UTF-8 explicitly (was `text=True` → cp1252 mojibake on Windows). `\xc3\xa9` is the verified UTF-8 encoding of `é`. Truly-invalid UTF-8 from git degrades sanely via `errors="replace"` (a replacement char in a path that won't match a real file) — no crash, no fabricated success; an acceptable honest degradation consistent with AR10. The `git status --porcelain` drift check is unaffected (it tests emptiness only).
- **Regression test would RED on old code.** `test_unicode_named_python_source_is_included_unmangled` (TC-APAA-INTAKE-001-78) commits `café.py` + `naïve_dir/résumé.py` + `plain.py` and asserts `source_files == ("café.py", "naïve_dir/résumé.py", "plain.py")` with no `"`/`\` mangling — exactly the set the old quoting path would have dropped to `("plain.py",)`. It genuinely exercises the defect.

**Rest of the slice re-confirmed (no regression):** single-serializer reuse — no `json.dumps` in `intake/`/`index/` (1.1 AST gate green); 9 `frozen=True, extra="forbid"` construction-pure result models, line numbers `int`, no float/clock/uuid/random (AR4/AC6); pure/impure boundary intact (all git/FS/parser I/O in the impure shell); determinism — `grammar_version` recorded, `source_files`/defs/edges sorted (AR1/AR11); the `ast_eligible` seam keeps the language conditional in `index`/`intake` with NO leak into `ledger/`/`verdict` (NFR-P2 — grep clean); typed `RepoIntakeError(ValueError)` covers the failure surface (AR10); no absolute host path persisted (NFR-S1); no file >1200 lines (177/180/319); headless (no web import, no-web-imports gate extended-not-forked and green). DF-1-4-A correctly retained as the AC-sanctioned defer with the full CC-3 six-field schema — not silently changed.

**Verification evidence (iter-2):**
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **291 passed in 4.07s** (was 290 pre-fix; +1 regression test).
- `python -m mypy minions_core/apaa/intake/repo_loader.py` → Success: no issues found.
- `sprint-status.yaml` parses cleanly (no worktree corruption); only the intended status line + `last_updated` changed.

### Iteration 1 outcome (historical — superseded by the iter-2 PASS above)

The slice is well-built and faithful to the architecture: clean pure/impure separation (AR8), frozen `extra="forbid"` construction-pure result models with no float/clock/uuid/random (AR4/AC6), the single-serializer + 1.3 containment shell are reused verbatim for the AC7 round-trip with no second `json.dumps` (the 1.1 AST gate stays green), the `ast_eligible` seam keeps the language conditional confined to `index`/`intake` with no leak into `ledger`/`verdict` (NFR-P2), typed `RepoIntakeError` covers the failure surface (AR10), and the grammar version is recorded for the Epic-5 cache key (AR1/AR5). Tests are green (290 passed: `tests/apaa/` + `tests/test_import_paths.py`), mypy is clean on the 3 new modules, the no-web-imports gate is extended (not forked) and green, and no file approaches the 1200-line limit.

One Medium correctness/determinism defect blocks a clean pass and is the sole reason for FAIL.

### Findings

| Sev | Location | Principle / rule | Fix |
|---|---|---|---|
| Med | `intake/repo_loader.py:154-161` | AC1 audit-input completeness + AR11 determinism — `git ls-files` default quoting silently drops / mangles non-ASCII source paths | enumerate with `git ls-files -z` (split on `\0`, no `.strip()`/`splitlines()`) or `-c core.quotepath=false`; add a unicode-named-`.py` regression test |
| Low | `index/ast_index.py:186-231` (DF-1-4-A) | edge set is unresolved-name only — AC-sanctioned V1 substrate, not a defect; recorded for downstream consumers | none (Epic-6 owns the resolved call graph) |

### Verification evidence

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py -q` → 290 passed.
- `python -m mypy minions_core/apaa/intake/repo_loader.py minions_core/apaa/intake/stack_detect.py minions_core/apaa/index/ast_index.py` → Success: no issues found in 3 source files.
- Reproduced the Medium defect directly: a committed `café.py` surfaces from `git ls-files` as `"caf\303\251.py"`, whose `Path(...).suffix` is `.py"` — failing the `_SOURCE_SUFFIXES` membership test and dropping the file.
- Single-serializer AST gate (`test_canonical_single_serializer.py`) and the extended no-web-imports gate both pass with the new modules present.

### Action items for the next dev round

1. (Med, required for pass) Fix the `git ls-files` quoting bug per the Review Findings `[Review][Patch]` item + add the unicode-filename regression test, then re-run `PYTHONIOENCODING=utf-8 pytest tests/apaa/ tests/test_import_paths.py` green and mypy clean.

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-06-21 | 0.2.2 | code-review (RE-REVIEW, iteration 2): **PASS → status `done`.** The iteration-1 Medium defect (`git ls-files` silently dropping/mangling non-ASCII source paths) is resolved and adversarially verified: reviewer independently reproduced old quoted `"caf\303\251.py"` (dropped) vs new `git ls-files -z` raw bytes → UTF-8 decode → `café.py` (included); confirmed the byte→UTF-8 decode is correct with sane `errors="replace"` degradation on invalid UTF-8 (no new crash); confirmed regression test TC-APAA-INTAKE-001-78 genuinely RED-on-old. Rest of slice re-confirmed green (single-serializer/1.1 gate, frozen+forbid pure models, pure/impure boundary, determinism+`grammar_version`, `ast_eligible` seam with no ledger/verdict language leak, typed errors, no absolute paths, ≤1200 lines, headless). DF-1-4-A retained as AC-sanctioned defer (full CC-3 schema, unchanged). `PYTHONIOENCODING=utf-8 pytest tests/apaa/ tests/test_import_paths.py` → 291 passed; mypy clean; sprint-status parses cleanly. Status → done. | claude-opus-4-8 (Reviewer) |
| 2026-06-21 | 0.2.1 | dev-story (fix, iteration 1): resolved the review Medium defect — `git ls-files` silently dropped/mangled non-ASCII source paths. Fix in `intake/repo_loader.py`: enumerate via `git ls-files -z` split on `\0` (unquoted, bypasses `core.quotepath=true`; no `.strip()`/`splitlines()`) AND decode git stdout as UTF-8 explicitly in `_run_git` (was `text=True` → cp1252 mojibake on Windows). `git status --porcelain` drift check unaffected (emptiness-only). Added regression test `test_unicode_named_python_source_is_included_unmangled` (TC-APAA-INTAKE-001-78, `café.py` + `naïve_dir/résumé.py`), written RED then GREEN. `PYTHONIOENCODING=utf-8 pytest tests/apaa/ tests/test_import_paths.py` → 291 passed; mypy clean on `repo_loader.py`. DF-1-4-A left as the recorded AC-sanctioned defer. Status → review. | claude-opus-4-8 (Developer) |
| 2026-06-21 | 0.2.0 | dev-story (implement): delivered repo intake @ pinned commit with drift-refusal (`intake/repo_loader.py` — `RepoIntake` + `RepoIntakeError`, working-tree-vs-pin verification via `git rev-parse`/`status --porcelain`/`ls-files`), no-config stack/toolchain detection (`intake/stack_detect.py` — `StackProfile`/`ToolchainProfile`, suffix+marker Python detection, honest `find_spec`/`which` probes), and the tree-sitter Python AST/code-graph index (`index/ast_index.py` — `Definition`/`CodeEdge`/`AstIndexEntry`/`AstIndex`, 0.25 per-language-package API, definitions+1-based spans+call/reference edges, recorded `grammar_version=tree-sitter-python 0.25.0`, the `ast_eligible` stack-agnostic seam routing non-Python/unparseable → `claim_emitted` proxy with NO language leak into ledger/verdict). All result models frozen `extra="forbid"`, construction-pure, no float/clock/uuid/random. AC7 round-trip proven via the reused Story 1.3 store shell (no second serializer, no new persistence module; pipeline write wiring deferred to 1.7). Extended `_MODULES_UNDER_GUARD` (web-stack isolation green). Tests: `test_repo_intake.py` (8), `test_stack_detect.py` (8), `test_ast_index.py` (6), `test_intake_index_roundtrip.py` (1). Resolved toolchain: tree-sitter==0.25.2 / tree-sitter-python==0.25.0 / radon==6.0.1 (grammar ABI 15). `pytest tests/apaa/ tests/test_import_paths.py` all green; mypy clean on 5 new modules; 1.1 single-serializer gate stays green. Status → review. | claude-opus-4-8 (Developer) |
| 2026-06-21 | 0.1.0 | Story created (create-story): context-filled spec for repo intake @ pinned commit (FR1), stack/toolchain auto-detection (FR2), the tree-sitter Python AST/code-graph index (Decision B), and the stack-agnostic `claim→validated?` AST-eligibility seam (NFR-P2). ACs cover drift-refusal + typed `RepoIntakeError`, no-config detection + degraded-toolchain honesty, definitions/spans extraction + recorded `grammar_version` (Epic-5 cache-key input), non-Python/unparseable → `claim_emitted` proxy with NO language leakage into ledger/verdict, frozen pure result models + impure shell, optional `.apaa/` persistence via the reused 1.3 store shell, the extended import-isolation gate, and optional-dep test strategy. Honors 1.1/1.2/1.3 precedents (single serializer + envelope reuse, reuse the `ApaaStorePaths` containment shell, frozen `extra="forbid"` models, `Locator.ast_span` source). Dependency note: tree-sitter/tree-sitter-python/radon are ALREADY sanctioned (AR1/Decision B) AND staged in the `minions[apaa]` extra — no net-new tool, no HALT. Status → ready-for-dev. | claude-opus-4-8 (Scrum Master) |
