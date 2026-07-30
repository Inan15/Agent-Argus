# Story 5.1: Cache-key derivation (full recording-producing closure) + CI canary — [Tier B]

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker at `_bmad-output/implementation-artifacts/sprint-status.yaml`). All
> CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only, §3.8 12-Factor + secret masking, §3.4
> evidence immutability).
>
> **This is the FIRST story of Epic 5** (Reproducible Verdict & Memoization, Tier-B). It flips `epic-5` to
> `in-progress`. It builds on the fully-done Epics 1+2+3+4 (760 passed at the Epic-4 retro). It is the
> **reproducibility FOUNDATION** of the epic: the single, pure, golden-tested cache-key derivation over the
> full recording-producing closure + a CI canary that fails when the closure changes without the key
> changing (or vice versa). The memoization STORE (5.2) and INVALIDATION + rejected-finding key-busting
> (5.3) ride on the key this story defines — they are explicitly OUT of this story's scope.

## Story

As an **APAA maintainer** who must be able to certify that a memoization cache hit can ONLY ever return a
result that was produced by an IDENTICAL recording-producing closure (so reproducibility never silently
serves a result computed under a different detector, grammar, config, or model),
I want **one pure cache-key derivation function** (`apaa/cache/key.py`) that folds EVERY
determinism-relevant input that determines a recording's output — the content-hash of what was audited, the
**content-hash of the enabled detector SET** (code+config, NOT a human version string), the tree-sitter
grammar version + tool versions, the budget/materiality config, the work-manifest scope, and the model
checkpoint (a **testable V1 placeholder** until Epic-6 Story 6.1 wires the live API-response capture) —
into a deterministic key, **plus a CI canary** that FAILS when the producing closure changes without the
key changing (catching silent cache-staleness, the AR5 honesty mechanism),
so that Epic-5's memoization (5.2 store, 5.3 invalidation) has a key it can trust to be a faithful fingerprint
of the closure, and a future maintainer who edits a detector / bumps a grammar / changes config without
re-deriving the key is caught by a red CI build rather than by a stale, wrong cache hit served forever.

## Story Context

This is **Story 1 of Epic 5** (Reproducible Verdict & Memoization, Tier-B — the "a number you can put on a
dashboard and trust not to flake" layer, PRD Journey 3), and the FIRST Epic-5 story (so it flips `epic-5`
to `in-progress`). It builds on the fully-done Epics 1+2+3+4 (the Epic-4 retro recorded 760 passed, mypy
clean, all files ≤1200 lines, a four-epic clean determinism/security-gate streak). It is the **cache-key
derivation + CI canary** story (FR27 foundation / NFR-D1 / AR5, `[Tier B]`).

**What this story delivers and what it explicitly does NOT.** This story delivers the PURE KEY-DERIVATION
function and its CI canary — the reproducibility foundation. It does **not** build the memoization STORE
(reading/writing recorded results under the key — Story 5.2) and it does **not** build INVALIDATION or
rejected-finding key-busting (Story 5.3). The key is a pure fingerprint; using it to store/serve/invalidate
results is the next two stories. Keeping 5.1 to the key-derivation-only scope is the thin-slice discipline
that held across Epics 1-4 (each story folds ONE working capability over the determinism spine).

**The determinism spine this key folds over is DONE and proven byte-identical across environments.** The
single canonical serializer (`apaa/store/canonical.py::dumps_bytes`), the content-hashed envelope
(`apaa/store/envelope.py::compute_content_hash`), `Fraction`-not-`float`, sorted/order-independent merges,
and the explicit-UTF-8 impure shell all shipped in Epics 1-3 and were proven byte-identical across
`PYTHONHASHSEED` / locale-encoding / CWD legs by Story 3.5. The cache key MUST derive from the SAME
canonical bytes — it is a fingerprint OVER the determinism spine, not a second hasher. **There is ONE
serializer and ONE content-hash function; the cache key composes them, it does not fork them** (AR4 / the
single-serializer gate, and the AR5 "one cache-key function" rule).

**The closure inputs (AR5 / architecture §76-82, §247-250) and their V1 availability.** The cache key is
"the full recording-producing closure, not just the model checkpoint." Enumerate EVERY input that
determines a recording's output:

| Closure input | V1 source (REAL, available now) | Notes |
|---|---|---|
| **content-hash** of the audited unit | `compute_content_hash(payload)` / `dumps_bytes` (1.1) over the canonical content/recording payload | The single content-hash function — REUSE, do not re-hash. |
| **detector-set content-hash** (code+config, NOT a human version string) | a NEW declared, enumerated **detector descriptor set** (rule_id + code-identity + config) canonical-hashed via the single serializer | The rule_ids exist as scattered constants today (`detectors/secret_scan.py::RULE_HARDCODED_SECRET`, `detectors/tool_runner.py::RULE_TOOL_FAILURE` / `RULE_TRACEABILITY_NOT_ESTABLISHABLE`, the vacuous-test rule, etc.) — there is NO central registry yet. DECISION DN-DETECTORSET below: declare a small, explicit, frozen detector-descriptor list in `cache/key.py` (or a tiny sibling) and content-hash it; this is the AR6/5.3 invalidation lever. |
| **tree-sitter grammar version** | `index/ast_index.py::_grammar_version()` → `AstIndex.grammar_version` (recorded by 1.4) | REAL + available now — the retro KEY FORWARD NOTE: grammar_version IS a real closure input already available. REUSE the recorded value; do not re-probe. |
| **tool versions** (radon, etc.) | `importlib.metadata.version("radon")` (and grammar above) — the AR1 pinned tools | A degraded `"unknown"` fallback that never raises (mirror `_grammar_version`'s AR10 contract). |
| **budget / materiality config** | `AuditRequest.budget` (int) + `AuditRequest.materiality_bar` (str) (1.7/3.1 — recorded provenance) | Already in the request half; REUSE the recorded values. |
| **work-manifest scope** | the 2.4 work-manifest file-list / partition scope (`partition_id` is `"root"` in V1) + 2.3 critical-subsystem designation (`AuditRequest.critical_paths` / `excluded_critical_paths`) | Scope determines WHAT is audited → it is a closure input. Fold the sorted manifest membership + designation. |
| **model checkpoint** (captured from the API response) | **NOT available in V1** — the live LLM dispatch port + Minions adapter is **Epic-6 Story 6.1** | **DN-PLACEHOLDER (the load-bearing forward-coupling decision, flagged by the Epic-4 retro §9 + §6).** In V1 Tier-A the deep path is heuristic/claim-proxy with NO live LLM, so 5.1 MUST define the checkpoint input as a STABLE, TESTABLE V1 placeholder (a fixed/derived sentinel, e.g. a `model_checkpoint: str` field defaulting to a constant like `"v1-heuristic-no-llm"`), shaped so that when 6.1 wires the real API-response capture it is an ADDITIVE substitution of a real value into the SAME key slot — NOT a key-shape change. Do NOT build 6.1 here. Do NOT block on it. The `checkpoint_drift` ABORT/re-audit behaviour (AR5 / AC3) likewise has its DETECTION SEAM defined here as a placeholder-comparison (two different checkpoint values → would derive different keys), with the live mid-run drift capture deferred to 6.1. |

**The CI canary (AR5 / architecture §81-82, §250, §304 — the AI-E3-1/AI-E4-1 lesson applied).** The canary
is "a CI canary that fails when key inputs change without a version bump." Concretely: a committed
golden-test that pins the derived key for a FIXED, fully-specified closure to a recorded golden value, AND
asserts that perturbing EACH closure input (one at a time) PRODUCES A DIFFERENT KEY. The honesty property
is bidirectional:
- **closure changes → key MUST change** (catches the dangerous case: a maintainer edits a detector / bumps
  the grammar / changes config, but the key derivation forgot to fold that input, so a stale wrong result
  would be served — the silent cache-staleness AR6/CC-2 warns about); and
- **the same closure → the SAME key** (deterministic, byte-stable, order-independent — the reproducibility
  property; NFR-P1/D1).
The canary is the engineered guard for the "did the key forget an input?" failure mode — exactly the
§9.2 / AI-E4-1 rule-of-three move: a recurring correctness risk promoted to a committed test that goes RED
when the closure drifts from the key.

**Carry-forward from the Epic-4 retro (2026-06-28) + the standing disciplines (CLAUDE.md §9.1 / L1-E11).**
Each item below is an Epic-5-backlog action item this story discharges (per the L1-E11 operating model:
package the prior retro's action items as the next epic's backlog).
- **AI-E4-1 (test-infra 🟠) — the NO-CRASH-KEYSTONE INPUT-SHAPE CHECKLIST (the "too-weak keystone test"
  failure mode is now 2 epics running).** Although the heaviest cache I/O lands in 5.2/5.3, 5.1's
  derivation MUST degrade honestly on a malformed closure input (a missing grammar version, an absent tool
  version, an empty detector set) — a typed error or a documented degraded value, NEVER an uncaught raise
  that produces a silently-wrong key. The canary set MUST fixture the perturbation of EACH input (the
  "closure changes → key changes" matrix) demonstrated RED before trusted (a derivation that ignores an
  input would pass a naive same-key test but FAIL the perturbation canary — that is the keystone-adequacy
  proof for THIS story).
- **AI-E4-1 forward to 5.2/5.3 (note, not this story's work):** the cache STORE's filesystem-touching
  impure shell is the surface that produced the 4.2 FAIL — a corrupt / non-file / permission-denied /
  unknown-schema cache entry must degrade to a MISS or a typed finding, never raise. That is 5.2/5.3 work;
  flag it forward, do NOT pull it into 5.1 (5.1 is the PURE key, no FS I/O).
- **AI-E4-5 (process 🟡) — DF-1-7-B (interim Python deep over-grading) is IMMINENT, owned by Story 6.2.**
  NOT this story's work, but the runway is Epic 5 → Epic 6 (6.2) → Epic 7 (dogfood). Do not let 5.1's
  model-checkpoint placeholder (6.1-owned) be confused with the 6.2 AST-grounding deliverable; they are
  distinct Epic-6 owners. Keep the placeholder shaped for a clean 6.1 substitution.
- **AI-E4-7 (process 🟢) — keep the three structural gates green + the L1-E11 loop.** The new `cache/key.py`
  must not break the import-isolation gate (`test_no_web_imports.py`), the single-serializer AST gate
  (`test_canonical_single_serializer.py` — the cache key REUSES `dumps_bytes`, it does NOT add a second
  `json.dumps`), or the file-size gate (≤1200 lines). Extend (NOT fork) `_MODULES_UNDER_GUARD` with the new
  `cache/key.py` (it is pure, FastAPI-free, no-LLM). Extend the 4.4 secret-containment artifact-class union
  awareness to the future `cache/` tree at 5.2 (NOT this story — 5.1 writes no `.apaa/cache/` byte).
- **AI-E1-1 (test-infra 🟢) — non-ASCII / locale discipline (the Epic-1-FAIL class, standing).** A closure
  whose inputs include a non-ASCII file path / non-ASCII content must derive a stable key (explicit UTF-8;
  the single serializer is `ensure_ascii=False`). Run the suite under `PYTHONIOENCODING=utf-8` (project
  memory — the cp1252 emoji crash). At least one canary fixture carries a non-ASCII path/value.
- **AI-E4-4 (governance 🟢) — central defer register.** If this story files a NEW defer, file it
  append-only in `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (the single canonical APAA defer
  source), not only in the story file, with the six CC-3 fields.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 5.1) + the architecture / PRD. Drivers: **APAA-FR-27**
> (APAA can reproduce the same verdict for the same repository and APAA version — the cache key is the
> reproducibility FINGERPRINT this rests on; the STORE that achieves the reproduction is 5.2), **APAA-NFR-D1**
> (same repo @ same commit @ same APAA version → identical verdict + ledger via local content-addressed
> memoization; **key = content-hash + model checkpoint + detector-set hash** — the CENTRAL driver),
> **APAA-AR5** (ONE cache-key function `apaa/cache/key.py`; the key is the full recording-producing closure;
> a mid-run checkpoint drift → `checkpoint_drift` finding → abort/re-audit; **CI canary fails when key inputs
> change without a bump**), **APAA-NFR-D2** (the derivation is a PURE function, zero LLM tokens), **APAA-NFR-D3**
> (content hashes cover the canonical payload only), **APAA-NFR-P1** (byte-identical / deterministic key
> across environments), **APAA-AR4** (single serializer, no float, clock-free / uuid-free / random-free),
> **APAA-AR8** (`cache/key.py` is a PURE module — no I/O, no clock, no LLM), **APAA-NFR-M1** (≤1200-line
> files), **APAA-AR10** (a malformed closure input degrades to a typed error, never an uncaught raise that
> yields a silently-wrong key).
>
> **SCOPE FENCE — Tier-B, single-purpose, FIRST Epic-5 story.** This story delivers ONLY: (1) the PURE
> cache-key derivation function `apaa/cache/key.py` over the full recording-producing closure (content-hash
> + detector-set content-hash + grammar/tool versions + budget/materiality + work-manifest scope + a
> TESTABLE V1 model-checkpoint placeholder); (2) the declared, enumerated, frozen **detector-descriptor set**
> that the detector-set content-hash is taken over (DN-DETECTORSET — the AR6 invalidation lever 5.3 will use);
> (3) the CI canary (golden key + per-input perturbation matrix: closure changes → key changes; same closure
> → same key); (4) the `checkpoint_drift` DETECTION SEAM as a placeholder-comparison (two checkpoint values →
> different keys), with live capture deferred to 6.1. It does NOT build, and MUST NOT pull forward: the
> **memoization STORE** (read/write recorded results under the key — Story 5.2); **cache invalidation /
> rejected-finding key-busting** (Story 5.3); the **live LLM dispatch port + Minions adapter / real
> API-response model-checkpoint capture** (Epic-6 Story 6.1 — use the V1 placeholder, do NOT block); the
> **mid-run checkpoint-drift live capture + the `checkpoint_drift` finding's pipeline wiring + abort/re-audit
> loop** (the FINDING shape may be defined, but the live drift capture is 6.1); any **`.apaa/cache/` write**
> (5.2 owns the cache tree — 5.1 writes NO cache byte; it is a pure function); a **new `.github/workflows`
> CI job** (the canary is a normal `tests/apaa/` test collected by the existing `test` job — no new job);
> a **new HTTP route / FastAPI surface / UI** (§3.7); a **`cli.py` subcommand**. Build the pure key + the
> detector-descriptor set + the canary, prove the perturbation matrix RED-then-green, then stop.

**AC1 — One PURE cache-key function derives a deterministic key over the FULL recording-producing closure (AR5 / NFR-D1 — the central driver)**
**Given** the cache-key inputs — the content-hash of the audited unit, the enabled detector SET, the
tree-sitter-grammar + tool versions, the budget + materiality config, the work-manifest scope, and the
model-checkpoint (V1 placeholder)
**When** `apaa/cache/key.py` derives a key from a fully-specified closure object
**Then** it folds ALL of: content-hash + model-checkpoint (the V1 placeholder, captured from the API response
post-6.1) + detector-set **content-hash** (NOT a human version string) + tree-sitter-grammar/tool versions +
budget/materiality + work-manifest scope — as a PURE function (NFR-D2: no I/O, no clock, no `uuid4`, no
`random`, no `os.getpid()`, no `datetime.now`/`time.time`, no float, no dict/set-iteration-order reliance —
AR4/AR8), composing the SINGLE canonical serializer (`store/canonical.py::dumps_bytes`) + the SINGLE
content-hash (`store/envelope.py::compute_content_hash` or sha256-over-`dumps_bytes`) — NEVER a second
`json.dumps` or a second hasher
**And** the derived key is a stable string (e.g. a hex content-hash over the canonical closure payload), the
SAME closure ALWAYS yields the SAME key (byte-stable + order-independent — proven across input orderings),
and the function is golden-tested.

**AC2 — A change to ANY key input changes the key (AR5 — the CI canary's honesty property; the keystone)**
**Given** a fixed, fully-specified baseline closure with a recorded GOLDEN key
**When** the CI canary perturbs EACH closure input ONE AT A TIME — a different content-hash, an edited
detector descriptor (the detector-set content-hash changes), a bumped grammar version, a changed tool
version, a different budget, a different materiality_bar, a changed work-manifest scope / critical
designation, a different model-checkpoint placeholder value
**Then** EACH perturbation derives a DIFFERENT key from the baseline golden (the closure is faithfully folded
— a forgotten input is caught here), demonstrated as a committed per-input matrix
**And** the baseline closure re-derives the recorded golden key byte-identically (closure unchanged → key
unchanged), so the canary is bidirectional: it FAILS if a real input change does NOT move the key (silent
cache-staleness) AND it FAILS if the key drifts for an unchanged closure (non-determinism). The
keystone-adequacy proof (AI-E4-1): each perturbation leg is demonstrated RED against a derivation that
ignores that input before being trusted.

**AC3 — The detector-set is a declared, enumerated, content-hashed descriptor set, NOT a human version string (AR5 / AR6 — the 5.3 invalidation lever)**
**Given** the enabled detectors (the 2.5 secret scanner, the 2.6 tool-runner failure/traceability detectors,
the 1.5 vacuous-test heuristic, and any other live detector)
**When** the detector-set content-hash is computed
**Then** it is taken over a DECLARED, frozen, enumerated **detector-descriptor set** (each descriptor
carrying at least its `rule_id` + a code-identity token + its config) serialized through the SINGLE canonical
serializer (DN-DETECTORSET) — NOT a hand-written `apaa_version` string (the explicit AR5/R3 rule: "a
content-hash of the enabled detector SET (code+config), NOT a human-written APAA version string")
**And** editing a descriptor (adding/removing a detector, or changing a detector's config) CHANGES the
detector-set content-hash → CHANGES the derived key (the AR6 invalidation lever Story 5.3 will ride: a
detector-set change invalidates affected cache entries). The descriptor set is the canonical, single source
of "which detectors are enabled" for the key.

**AC4 — The model-checkpoint input is a stable, testable V1 placeholder, shaped for a clean 6.1 substitution (AR5 / the Epic-4-retro forward-coupling decision — DN-PLACEHOLDER)**
**Given** that the live LLM dispatch port + Minions adapter (real API-response model-checkpoint capture) is
Epic-6 Story 6.1, and V1 Tier-A's deep path is heuristic/claim-proxy with NO live LLM
**When** the cache key folds the model-checkpoint input
**Then** the checkpoint is a STABLE, TESTABLE V1 placeholder (a fixed/derived constant, e.g.
`model_checkpoint="v1-heuristic-no-llm"`), the key derivation does NOT depend on a live LLM (NFR-D2: zero
tokens), and the placeholder occupies a key slot shaped so that 6.1 substitutes a REAL captured checkpoint
value into the SAME slot ADDITIVELY (no key-shape / schema change — additive-only, NFR-M2)
**And** the `checkpoint_drift` detection SEAM is defined here as a placeholder-comparison (two DIFFERENT
checkpoint values derive DIFFERENT keys — so a mixed-checkpoint result can never be served as a hit), with
the LIVE mid-run drift capture + the `checkpoint_drift` finding's pipeline-wiring + abort/re-audit loop
explicitly DEFERRED to Story 6.1 (do NOT build it here; document the deferral).

**AC5 — Determinism, no-float, single-serializer, non-ASCII, ≤1200 lines, PURE (AR4/AR8/NFR-P1/NFR-M1/AI-E1-1)**
**Given** the new `apaa/cache/key.py` (+ the detector-descriptor set + the canary fixtures)
**When** the suite runs under `PYTHONIOENCODING=utf-8`
**Then** the derivation is PURE (an AST-scan / banned-import assertion confirms no `datetime`/`time`/`uuid`/
`random`/`os.getpid`/float/`json.dumps`/FS/LLM in `cache/key.py`); the key is byte-stable + order-independent
(proven RED on a set-vs-sorted round-trip, the 3.5 precedent); a closure carrying a non-ASCII file path /
non-ASCII content derives a stable key (explicit UTF-8, `ensure_ascii=False` single serializer — the
Epic-1-FAIL encoding class); `cache/key.py` and the test file are each ≤1200 lines (NFR-M1)
**And** a malformed closure input (a missing grammar version, an empty detector set, an absent required
field) degrades to a TYPED error (a `cache/key.py`-local `CacheKeyError`, a `ValueError` subclass), NEVER an
uncaught raise that yields a silently-wrong key (AR10 / AI-E4-1 — the no-crash input-shape discipline applied
to the pure derivation).

**AC6 — No regression / no scope creep; the structural gates stay green; mypy clean (AR8, AI-E4-7, the thin-slice discipline)**
**Given** the new pure module + its tests
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the 760-green Epic-4 baseline + the new `tests/apaa/test_cache_key.py`), the import-isolation gate
(`test_no_web_imports.py` — extended to include `cache/key.py`), the single-serializer AST gate
(`test_canonical_single_serializer.py` — `cache/key.py` adds NO second `json.dumps`), and the file-size gate
(≤1200 lines) stay green; `mypy` is clean on `cache/key.py` + any sibling
**And** the frozen Epic-1..4 contracts show NO working-tree diff (`store/{canonical,envelope}.py`,
`index/ast_index.py`, `models.py::AuditRequest`, `ledger/*`, `verdict/*`, `detectors/*`, `pipeline.py` —
the key COMPOSES them read-only; it does not edit them). `_MODULES_UNDER_GUARD` is EXTENDED (not forked) with
`cache/key.py`. NO `.apaa/cache/` byte is written (5.2 owns the store), NO `cli.py` subcommand, NO HTTP route,
NO new CI job
**And** the new test file cites its `APAA-FR-27`/`APAA-NFR-D1`/`AR5` drivers in the module docstring + the
locked test area / index; the mandatory artifacts EXIST + pass + the perturbation-matrix RED-then-green is
documented BEFORE the story flips to `status: review` (AI-E4-3 / AI-E2-1 test-existence discipline). **Test
area `APAA-CACHE`** (`TC-APAA-CACHE-001-NN` — the natural area for `cache/`; confirm/lock the next free index
in the module docstring).

## Tasks / Subtasks

- [x] **Task 0 — Enumerate + LOCK the closure inputs against the REAL surfaces; LOCK the detector-descriptor set + the V1 checkpoint placeholder** (AC: 1, 3, 4)
  - [x] Re-read `store/canonical.py` (`dumps`/`dumps_bytes` — the single serializer, no float, `ensure_ascii=False`)
        + `store/envelope.py` (`compute_content_hash` — sha256 over `dumps_bytes`). LOCK: the cache key COMPOSES
        these (no second `json.dumps`, no second hasher).
  - [x] Re-read `index/ast_index.py` (`AstIndex.grammar_version` + `_grammar_version()` — the RECORDED grammar
        version, AR10 `"unknown"` fallback). LOCK grammar_version as a REAL, available closure input (the retro
        KEY FORWARD NOTE). Add a `radon` (+ any AR1 tool) version probe mirroring `_grammar_version`'s
        no-raise/`"unknown"`-fallback contract.
  - [x] Re-read `models.py::AuditRequest` (`budget: int`, `materiality_bar: str`, `commit`, `critical_paths`,
        `excluded_critical_paths` — the recorded provenance) + the 2.4 work-manifest / partition scope (`partition_id`
        is `"root"` in V1). LOCK budget + materiality + sorted work-manifest membership + critical designation as
        closure inputs (REUSE the recorded values; do not re-derive).
  - [x] Re-read the detector rule_id constants (`detectors/secret_scan.py::RULE_HARDCODED_SECRET`,
        `detectors/tool_runner.py::RULE_TOOL_FAILURE`/`RULE_TRACEABILITY_NOT_ESTABLISHABLE`, the 1.5 vacuous-test
        rule). **LOCK DN-DETECTORSET:** there is NO central detector registry — declare a small, explicit, FROZEN
        detector-descriptor set in `cache/key.py` (or a tiny sibling `cache/detector_set.py`) enumerating each live
        detector's `rule_id` + a code-identity token + config; content-hash it via the single serializer. This is
        the AR6 invalidation lever 5.3 rides.
  - [x] **LOCK DN-PLACEHOLDER:** define the `model_checkpoint` input as a stable V1 constant (e.g.
        `"v1-heuristic-no-llm"`), in a key slot shaped for a clean ADDITIVE 6.1 substitution. Define the
        `checkpoint_drift` detection SEAM as a placeholder-comparison (two values → two keys); defer the live
        mid-run capture + the finding's pipeline wiring + abort/re-audit to 6.1 (document the deferral).
- [x] **Task 1 — Build the PURE cache-key derivation `apaa/cache/key.py`** (AC: 1, 3, 4, 5)
  - [x] A FROZEN (Pydantic v2 `frozen=True, extra="forbid"`, no float) `RecordingProducingClosure` model
        carrying every locked input (content_hash, detector_set_hash-or-descriptors, grammar_version, tool_versions,
        budget, materiality_bar, work_manifest scope, model_checkpoint placeholder).
  - [x] A PURE `derive_cache_key(closure) -> str` that canonical-serializes the closure (single serializer) and
        returns a sha256 hex key (compose `compute_content_hash` / `dumps_bytes` — no second hasher). No I/O / clock
        / uuid / random / float (AR4/AR8/NFR-D2).
  - [x] A PURE `detector_set_content_hash(descriptors) -> str` over the declared frozen descriptor set
        (DN-DETECTORSET).
  - [x] A typed `CacheKeyError(ValueError)` for a malformed closure (missing grammar version, empty detector set,
        absent required field) — degrade typed, never uncaught (AR10 / AI-E4-1).
- [x] **Task 2 — The CI canary: golden key + per-input perturbation matrix** (AC: 2, 5)
  - [x] In NEW `tests/apaa/test_cache_key.py` (area `APAA-CACHE`, `TC-APAA-CACHE-001-NN`): pin the GOLDEN key for
        a fixed fully-specified baseline closure (the determinism golden — closure unchanged → key unchanged,
        byte-stable + order-independent).
  - [x] The PERTURBATION matrix: for EACH closure input, perturb it ONE at a time and assert the key CHANGES
        (content-hash, detector descriptor edit, grammar bump, tool-version change, budget, materiality_bar,
        work-manifest scope / critical designation, model-checkpoint placeholder). Each leg demonstrated RED against
        a derivation that IGNORES that input (the AI-E4-1 keystone-adequacy proof) before being trusted.
  - [x] AI-E1-1: a non-ASCII path/value closure derives a stable key (explicit UTF-8). Run under
        `PYTHONIOENCODING=utf-8`.
- [x] **Task 3 — Purity / no-float / single-serializer / no-crash input-shape assertions** (AC: 5)
  - [x] An AST-scan / banned-import test that `cache/key.py` imports no `datetime`/`time`/`uuid`/`random`/
        `os.getpid`/float-literal-score/`json.dumps`/FS/LLM (PURE — AR8). Extend `test_no_web_imports.py`'s
        `_MODULES_UNDER_GUARD` (not fork) + confirm the single-serializer AST gate stays green.
  - [x] No-crash input-shape (AI-E4-1, applied to the pure derivation): a missing grammar version / empty detector
        set / absent required field → `CacheKeyError`, demonstrated RED, NEVER an uncaught raise / silently-wrong key.
- [x] **Task 4 — Run + mypy + the pre-`review` test-existence precondition** (AC: 6)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` → all
        pass (760 baseline + the new `test_cache_key.py`). `mypy` clean on `cache/key.py` (+ sibling).
  - [x] Confirm NO working-tree diff to the frozen Epic-1..4 producer/spine surfaces (the key COMPOSES them
        read-only). Confirm NO `.apaa/cache/` byte written, NO `cli.py`/HTTP/CI-job change.
  - [x] **AI-E4-4 / DN-DEFER:** if a NEW defer is filed, file it append-only in
        `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` with the six CC-3 fields. Do NOT pull 5.2 store /
        5.3 invalidation / 6.1 live-capture into scope.
  - [x] **AI-E4-3 / AI-E2-1 GATE:** the mandatory artifacts (`cache/key.py` + the detector-descriptor set +
        `tests/apaa/test_cache_key.py` with the perturbation matrix + the documented RED-then-green) EXIST + pass
        BEFORE the `review` flip; the Dev Agent Record is filled completely (no blank placeholders).

### Review Findings

<!-- defer-schema-session: 2026-06-28 -->

- [x] [Review][Defer] prompt-template version closure input has no key slot (forward-coupling, Low) [minions_core/apaa/cache/key.py:172] — architecture §77 explicitly enumerates `prompt-template version` among the recording-producing-closure key inputs; `RecordingProducingClosure` folds every other listed input but not this one. Out of V1 scope (no live LLM in Tier-A), BUT — unlike `model_checkpoint`, which was given a placeholder slot to pre-empt exactly this — the prompt-template version has no slot. When 6.1 wires the live LLM, a prompt-template change would NOT move the key (silent cache staleness). The `CACHE_KEY_SCHEMA_VERSION` bump lever + `extra="forbid"` model allow a clean 6.1 addition. Filed as DF-5-1-A (see `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`). Interim doc-only mitigation for THIS round: add a `key.py` docstring forward-note that prompt-template version is an Epic-6 LLM-path closure input deferred to 6.1 (so the deferral is recorded next to the slot it will occupy). target_story: 6-1-llm-dispatch-port-minions-orchestrator-adapter.
  - **RESOLVED 2026-06-28 (dev-story fix iter-1) — DF-5-1-A CLOSED.** Applied the reviewer's
    full suggested fix (not the interim doc-only mitigation): added a `prompt_template_version`
    field to `RecordingProducingClosure` mirroring the `model_checkpoint` DN-PLACEHOLDER slot
    (stable V1 sentinel `V1_PROMPT_TEMPLATE_VERSION = "v1-no-prompt-template"`, additive-shaped
    for a clean 6.1 substitution), folded it into `_closure_payload`, added a non-blank validator
    leg, bumped `CACHE_KEY_SCHEMA_VERSION` `1 → 2`, and regenerated the pinned golden key to
    `2628b9a6ecb72e845d6fb83286ca838db326fb888837dfbd9483a05de550ca87` (documented intentional
    invalidation). Added a `prompt_template_version` perturbation-matrix leg (covered by the
    `_key_ignoring` keystone-adequacy RED demo), a placeholder-default test (TC-APAA-CACHE-001-21)
    and a drift-seam test (TC-APAA-CACHE-001-22). The future silent-cache-staleness hole (a
    prompt-template change not moving the key at 6.1) is closed: two values → two keys. DF-5-1-A
    closed append-only in `deferred-work.md`. 783 passed (was 779; +4), mypy clean, structural
    gates green.

## Senior Developer Review (AI) — Iteration 2 (RE-REVIEW)

**Reviewer:** code-review gate (claude-opus-4-8) · **Date:** 2026-06-28 · **Iteration:** 2
**Verdict:** PASS — the iter-1 CONCERNS finding (DF-5-1-A) is fully and correctly resolved, closure-completeness now holds against architecture §77, all V1 ACs are met, all tests green, no regression. Status set `review` → `done`.

### Iteration-2 fix verification (DF-5-1-A — RESOLVED, adversarially verified)

The dev applied the reviewer's full suggested fix (not the interim doc-only mitigation):

- **The `prompt_template_version` slot IS genuinely in the key closure.** A `prompt_template_version` field (default `V1_PROMPT_TEMPLATE_VERSION = "v1-no-prompt-template"`) is on `RecordingProducingClosure` (frozen, `extra="forbid"`, `min_length=1` + non-blank validator), folded into `_closure_payload` at the canonical key `"prompt_template_version"`. Two distinct values → two distinct keys, independently confirmed: `derive_cache_key` over the baseline vs a closure differing only in `prompt_template_version` produces different keys (TC-APAA-CACHE-001-22).
- **Covered by the bidirectional canary's REAL-derivation RED demo.** The new leg is in `_PERTURBATIONS` (line 135), so it is exercised by both the perturbation matrix (TC-04, key MUST move) AND the keystone-adequacy `_key_ignoring` RED demo (TC-05) — and `_key_ignoring` traverses the REAL `_closure_payload` then drops the field, so the "key changed" assertion is a non-vacuous proof that the genuine derivation folds it. A derivation that forgot the slot would pass a naive same-key test but FAIL this leg.
- **Clean additive 6.1 placeholder, not a hidden 6.1 dependency.** The slot mirrors the `model_checkpoint` DN-PLACEHOLDER pattern exactly: a stable V1 sentinel, no live-LLM dependency (zero tokens, purity preserved), shaped so 6.1 substitutes a real captured value into the SAME slot additively (no key-shape change beyond a future value). Module docstring forward-note records the deferral next to the slot.
- **Schema bump + golden regeneration correct and stable.** `CACHE_KEY_SCHEMA_VERSION` is `"2"` (folded into the payload — the documented intentional-invalidation lever); the pinned golden was regenerated to `2628b9a6ecb72e845d6fb83286ca838db326fb888837dfbd9483a05de550ca87`, which I re-derived byte-identically from a fresh interpreter. The golden is pinned (TC-APAA-CACHE-001-03) and re-derives deterministically.

### Closure-COMPLETENESS re-swept (the iter-2 mandate — now COMPLETE)

Re-checked the full `RecordingProducingClosure` against the architecture's authoritative enumeration (§77 — the canonical list). Every enumerated input now has a folded slot, with NO remaining gap:

| §77 closure input | Folded slot |
|---|---|
| content-hash | `content_hash` |
| model checkpoint | `model_checkpoint` (V1 placeholder) |
| **prompt-template version** | **`prompt_template_version` (V1 placeholder — NEW, the iter-2 fix)** |
| tool versions (tree-sitter grammar, radon) | `grammar_version` + `tool_versions` |
| budget/materiality config | `budget` + `materiality_bar` |
| work-manifest scope | `work_manifest_files` + `critical_paths` + `excluded_critical_paths` |
| detector SET content-hash (code+config) | `detector_set_hash` (derived from `detectors` / `FROZEN_DETECTOR_SET`) |

No further missing input. The closure is complete vs §77; the iter-1 single-finding-only risk is closed.

### Tests independently re-run (GREEN)

- `PYTHONIOENCODING=utf-8 pytest tests/apaa/ tests/test_import_paths.py` → **783 passed** (was 779 at iter-1; +4 from the `prompt_template_version` leg + TC-APAA-CACHE-001-21/22).
- `pytest tests/apaa/test_cache_key.py tests/apaa/test_no_web_imports.py tests/apaa/test_canonical_single_serializer.py` → **48 passed** (cache canary + both structural gates green).
- `mypy minions_core/apaa/cache/key.py minions_core/apaa/cache/__init__.py` → Success, no issues (2 files).
- Golden key `2628b9a6…550ca87` re-derived byte-identically from a fresh interpreter.

### No-regression confirmation

Single serializer / single hasher (no `hashlib`, no `json.dumps` in `key.py` — composes `compute_content_hash`/`dumps_bytes`; single-serializer AST gate green); purity (AST + banned-import scans, no clock/uuid/random/float/FS/LLM); order-independence (sorted manifests/detectors/tool_versions); non-ASCII stability; typed `CacheKeyError(ValueError)`; frozen `extra="forbid"` models; no float; no `.apaa/cache/` write (pure module, no FS I/O); `key.py` 304 lines / `test_cache_key.py` 392 lines (≤1200); headless; `_MODULES_UNDER_GUARD` extended (not forked) with `minions_core.apaa.cache.key`. DF-5-1-A closed append-only in `deferred-work.md`. The iter-1 accepted design points (`commit` not a closure input — content-addressed; empty `work_manifest_files` permitted but empty detector-set rejected) remain correct.

### AC verification (iter-2)

- **AC1** (pure key over full closure, single serializer/hasher): MET.
- **AC2** (bidirectional canary): MET — 11-input perturbation matrix (was 10; +`prompt_template_version`) + non-vacuous `_key_ignoring` keystone RED demos over the REAL derivation.
- **AC3** (declared, content-hashed detector descriptor set): MET.
- **AC4** (V1 checkpoint placeholder + drift seam): MET — and now mirrored by the `prompt_template_version` placeholder + its own drift seam (two values → two keys).
- **AC5** (determinism / no-float / single-serializer / non-ASCII / ≤1200 / pure / typed error): MET.
- **AC6** (no regression / gates green / no scope creep / mypy): MET.

---

### Iteration 1 (superseded by the PASS above — preserved for the audit trail)

**Reviewer:** code-review gate (claude-opus-4-8) · **Date:** 2026-06-28 · **Iteration:** 1
**Verdict:** CONCERNS (Low) — core is correct and all V1 ACs are met; one forward-coupling closure-completeness gap warrants a documented defer + an interim doc note before the story is fully clean. Status set `review` → `in-progress`.

### Summary

`apaa/cache/key.py` is a clean, pure, single-serializer cache-key derivation over the recording-producing closure, with a genuinely non-vacuous bidirectional CI canary. The single-hasher discipline (no `hashlib`/`json.dumps` in the module; composes `compute_content_hash`/`dumps_bytes`), purity (AST-scanned, no clock/uuid/random/float/FS/LLM), order-independence (sorted manifests/detectors/tool_versions), non-ASCII stability, typed `CacheKeyError` degradation, frozen `extra="forbid"` models, and the DN-PLACEHOLDER / DN-DETECTORSET decisions are all correctly implemented and tested. The keystone-adequacy proof is real: `_key_ignoring` traverses the actual `_closure_payload` derivation and drops one payload key, so each "key changed" assertion is demonstrably a proof that the real derivation folds that input (RED-then-green per leg). No second serializer/hasher; the two structural gates stay green. File sizes 267 / 367 lines (≤1200). mypy clean.

The one substantive finding is closure-completeness relative to the architecture: §77 enumerates `prompt-template version` as a closure key input, and it has no slot. This is correctly out of V1 scope (no live LLM), but the asymmetry with `model_checkpoint` (which got a placeholder slot for exactly this reason) creates a future silent-staleness risk at 6.1. Non-blocking for V1 correctness; recorded as DF-5-1-A.

### Tests independently re-run (GREEN)

- `PYTHONIOENCODING=utf-8 pytest tests/apaa/ tests/test_import_paths.py` → **779 passed** (incl. 37 `test_cache_key.py` + import-isolation + single-serializer gates).
- `pytest tests/apaa/test_cache_key.py tests/apaa/test_no_web_imports.py tests/apaa/test_canonical_single_serializer.py` → **44 passed**.
- `pytest tests/security/` → **192 passed, 1 skipped** (host-conditional 3.5 portability leg), 4 subtests passed.
- `mypy minions_core/apaa/cache/key.py minions_core/apaa/cache/__init__.py` → Success, no issues.
- Golden key `14fc9123…b90694` re-derived byte-identically.

### AC verification

- **AC1** (pure key over full closure, single serializer/hasher): MET — `derive_cache_key` composes `compute_content_hash`; no `hashlib`/`json.dumps`; golden-tested; pure (AST + banned-import scans).
- **AC2** (bidirectional canary): MET — 10-input perturbation matrix + non-vacuous `_key_ignoring` keystone RED demos; `excluded_critical_paths` keystone-leg exclusion is correct and honestly documented (still fully covered by the general matrix).
- **AC3** (declared, content-hashed detector descriptor set): MET — `FROZEN_DETECTOR_SET` of `DetectorDescriptor(rule_id+code_identity+config)`, order-independent, empty-set → `CacheKeyError`, config-edit moves the key (AR6 lever).
- **AC4** (V1 checkpoint placeholder + drift seam): MET — `V1_MODEL_CHECKPOINT` constant, additive-shaped slot, two values → two keys; live capture deferred to 6.1.
- **AC5** (determinism / no-float / single-serializer / non-ASCII / ≤1200 / pure / typed error): MET.
- **AC6** (no regression / gates green / no scope creep / mypy): MET — `_MODULES_UNDER_GUARD` extended (not forked); no `.apaa/cache/` byte; no CLI/HTTP/CI-job; frozen Epic-1..4 surfaces unedited (only the tracked `apaa/__init__.py` working-tree diff is the pre-existing story-1.1 `__version__` constant, unrelated to 5.1).

### Accepted design points (not findings)

- `commit` (`AuditRequest`) is not a closure input — the closure is content-addressed via `content_hash`; two commits with identical audited content legitimately collide to the same key (the intended NFR-D1 content-addressing). Accepted.
- Empty `work_manifest_files` is permitted (a legitimately-empty scope derives a deterministic, distinct key — not silently wrong), in contrast to the empty-detector-set guard (a key over zero detectors is a lie). Accepted asymmetry.

### Action items

1. (Low / 6.1) Add a `prompt_template_version` key slot mirroring the `model_checkpoint` placeholder pattern + a perturbation-matrix leg + a `CACHE_KEY_SCHEMA_VERSION` bump — DF-5-1-A.
2. (Low / interim, this story) Add a `key.py` docstring forward-note recording that prompt-template version is an Epic-6 LLM-path closure input deliberately deferred to 6.1, so the deferral sits next to the slot it will occupy.

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **This is the reproducibility FOUNDATION, not the cache itself (the scope crux).** The KEY is the
  determinism keystone (architecture CC #1: "the determinism keystone is the KEY, not the verdict math").
  5.1 builds the PURE key + its canary; 5.2 builds the STORE that uses the key; 5.3 builds INVALIDATION +
  rejected-finding key-busting. Do NOT build 5.2/5.3 here. 5.1 writes NO `.apaa/cache/` byte and reads no
  cache — it is a pure function over a closure object.
- **ONE serializer, ONE content-hash — the cache key COMPOSES them (AR4/AR5).** NFR-P1 (byte-identical)
  dies the day a second `json.dumps` appears with different kwargs. The key derivation canonical-serializes
  the closure via `store/canonical.py::dumps_bytes` and hashes via the SAME path as `compute_content_hash`
  (sha256 over `dumps_bytes`). Do NOT introduce a second serializer or a second hasher. The single-serializer
  AST gate must stay green with the new module.
- **The detector-set hash is a CONTENT-hash of the enabled detector SET (code+config), NOT a human version
  string (AR5/R3 — DN-DETECTORSET, the load-bearing design decision).** There is no central detector
  registry today (rule_ids are scattered constants). Declare a small, explicit, FROZEN detector-descriptor
  set (rule_id + code-identity token + config per detector) and content-hash it. This is the canonical
  "which detectors are enabled" source and the AR6 invalidation lever 5.3 rides (a detector edit changes the
  set hash → changes the key → invalidates affected entries). Resist the temptation to hash an `apaa_version`
  string — the architecture explicitly forbids it.
- **The model-checkpoint is a TESTABLE V1 PLACEHOLDER (DN-PLACEHOLDER — the Epic-4-retro forward-coupling
  decision, §6 + §9).** The live API-response model-checkpoint capture is Epic-6 Story 6.1. In V1 Tier-A the
  deep path is heuristic/claim-proxy with NO live LLM. So the checkpoint input is a fixed/derived constant
  (e.g. `"v1-heuristic-no-llm"`) occupying a key slot shaped for a clean ADDITIVE 6.1 substitution of a real
  value — NOT a key-shape change. The derivation must NOT depend on a live LLM (NFR-D2 zero tokens). The
  `checkpoint_drift` ABORT/re-audit (AR5) has its DETECTION SEAM here (two checkpoint values → two keys);
  the live mid-run capture + the finding's pipeline wiring is deferred to 6.1. **Do NOT build 6.1. Do NOT
  block on it.**
- **The CI canary is the engineered guard for "did the key forget an input?" (AR5 / §9.2 / AI-E4-1).** It is
  a committed golden-test (closure unchanged → key unchanged) PLUS a per-input perturbation matrix (each
  input changed → key changes). The bidirectional property is the honesty: a forgotten input is caught by a
  perturbation leg that fails to move the key; non-determinism is caught by the golden drifting. This is the
  AR5 "CI canary that fails when key inputs change without a bump." It is a normal `tests/apaa/` test (the
  `test` job collects it) — NO new `.github/workflows` job.
- **PURE module, no-crash input shape (AR8/AR10/AI-E4-1).** `cache/key.py` takes no I/O, no clock, no LLM,
  no float, no uuid/random/os.getpid/datetime. A malformed closure degrades to a typed `CacheKeyError`
  (`ValueError` subclass) — never an uncaught raise that yields a silently-wrong key. The 5.2/5.3 cache I/O
  no-crash discipline (corrupt/non-file/permission-denied cache entry → MISS or typed finding) is flagged
  forward, NOT pulled into 5.1.
- **No floats / determinism — inherited (AR4/NFR-P1).** Any ratio-shaped input is `Fraction`/string, never
  float; the single serializer raises on a float leaf (the existing backstop). The key is order-independent
  (sorted/canonical), proven RED on a set-vs-sorted round-trip (the 3.5 precedent).
- **Frozen contracts unchanged (AR8/NFR-M2).** The key COMPOSES the Epic-1..4 surfaces read-only. Verify NO
  working-tree diff to `store/{canonical,envelope}.py`, `index/ast_index.py`, `models.py::AuditRequest`,
  `ledger/*`, `verdict/*`, `detectors/*`, `pipeline.py`. The new `cache/key.py` joins `_MODULES_UNDER_GUARD`
  (extend, NOT fork).

### Project Structure Notes

- **NEW pure module:** `minions_core/apaa/cache/key.py` (the AR5 single cache-key function; architecture
  §437 `cache/key.py — R3 — single cache-key derivation (PURE) + CI canary`). Optionally a tiny sibling
  `minions_core/apaa/cache/detector_set.py` for the frozen detector-descriptor set (or inline in `key.py`
  if small). ≤1200 lines each (NFR-M1). A `minions_core/apaa/cache/__init__.py` if not already present.
- **NEW test module:** `tests/apaa/test_cache_key.py` (architecture §475 `test_cache_key.py — cache-key
  derivation golden + CI canary on input changes`). Test area `APAA-CACHE` (`TC-APAA-CACHE-001-NN` — confirm
  the next free index in the module docstring; distinct from existing areas APAA-STORE / APAA-LEDGER /
  APAA-VERDICT / APAA-COST / APAA-PIPELINE / APAA-SECRET / APAA-SECURITY / APAA-PORT / APAA-INTAKE /
  APAA-EVIDENCE). ≤1200 lines.
- **REUSE read-only (verify NO working-tree diff):** `store/canonical.py` (`dumps_bytes`), `store/envelope.py`
  (`compute_content_hash`), `index/ast_index.py` (`AstIndex.grammar_version` / `_grammar_version`),
  `models.py::AuditRequest` (`budget` / `materiality_bar` / `commit` / `critical_paths` /
  `excluded_critical_paths`), the 2.4 work-manifest, the detector rule_id constants.
- **EXTEND (not fork) `_MODULES_UNDER_GUARD`** in `tests/apaa/test_no_web_imports.py` with `cache/key.py`
  (+ sibling). Confirm the single-serializer AST gate (`tests/apaa/test_canonical_single_serializer.py`)
  stays green.
- **NO `.apaa/cache/` write (5.2 owns the cache tree). NO `cli.py` change / NO new HTTP route / FastAPI
  surface / UI (§3.7). NO new `.github/workflows` CI job** (the canary is a normal `tests/apaa/` test).

### Testing Standards (APAA)

- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` (the
  `PYTHONIOENCODING` prefix avoids the cp1252 emoji crash on Windows — project memory). `mypy` via
  `python run_mypy_per_file.py` or scoped to `cache/key.py` (+ sibling).
- **Verification ID format:** `TC-APAA-CACHE-001-NN` (the new `cache/` area; confirm/lock the next free index
  in the module docstring).
- **AI-E4-1 keystone-adequacy (the literal honesty property of this story):** each perturbation leg of the
  CI canary (closure input changed → key changes) MUST be demonstrated RED against a derivation that IGNORES
  that input before it is trusted — a derivation that forgot an input would pass a naive same-key test but
  FAIL the perturbation canary. Each closure-input token is distinctive so a "key changed" assertion is a
  real proof, not a vacuous one.
- **AI-E1-1 non-ASCII discipline:** ≥1 canary closure carries a non-ASCII / Cyrillic path/value; run under
  `PYTHONIOENCODING=utf-8`; explicit UTF-8 (the single serializer is `ensure_ascii=False`).
- **Purity (AR8):** an AST-scan / banned-import test confirms `cache/key.py` has no `datetime`/`time`/`uuid`/
  `random`/`os.getpid`/float/`json.dumps`/FS/LLM.
- **The three structural gates stay green:** import-isolation (`test_no_web_imports.py`), single-serializer
  AST gate (`test_canonical_single_serializer.py`), file-size (≤1200 lines).

### References

- Epic: `_bmad-output/design-artifacts/ArgusAgent/epics.md` — Epic 5 / Story 5.1 (cache-key derivation, full
  recording-producing closure, + CI canary; FR27; NFR-D1; AR5).
- PRD: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` — FR27 (reproduce the same verdict for the same
  repository and APAA version), NFR-D1 (same repo @ commit @ APAA version → identical verdict + ledger via
  local content-addressed memoization; key = content-hash + model checkpoint + detector-set hash; NOT an
  assumption the LLM repeats itself), NFR-D2 (deterministic + zero-LLM-token), NFR-D3 (content hashes cover
  the canonical payload only), NFR-P1 (byte-identical across hosts/environments), NFR-M1/M2.
- Architecture: `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — §76-82 (cache key = full
  recording-producing closure; detector-set content-hash NOT a human version string; checkpoint from API
  response; mid-run drift → `checkpoint_drift` → abort/re-audit; CI canary), §91-96 (CC #1 the KEY is the
  keystone; CC #2 memoization caches errors → reproducibility ≠ correctness, detector-set-hash invalidation
  + rejected-finding key-busting), §247-250 (content-addressed memoization; key inputs; invalidate on
  detector-set change), §304 (determinism golden-tests — cache-key derivation), §337-350 (pure modules take
  no I/O/clock/LLM; ONE cache-key function `apaa/cache/key.py` — never compose a memo key ad hoc), §437
  (`cache/key.py — R3 — single cache-key derivation (PURE) + CI canary`), §475 (`test_cache_key.py`), AR1
  (pinned tool versions: tree-sitter / radon), AR4 (single serializer / no float / clock-free), AR5 (one
  cache-key function), AR6 (invalidation), AR8 (pure/impure), AR10 (typed degradation).
- Epic-4 retro: `_bmad-output/design-artifacts/ArgusAgent/epic-4-retro-2026-06-28.md` — §6 Next-Epic Preview
  (5.1 folds the closure; the model-checkpoint input is "captured from the API response" but the dispatch
  port is Epic-6 6.1 → 5.1 must define a stable, testable V1 placeholder; flag as a 5.1 readiness note),
  §9 Significant-Discovery Alert (the AR5 model-checkpoint forward-coupling — define a testable V1
  placeholder, do NOT block on 6.1), action items AI-E4-1 (no-crash input-shape checklist), AI-E4-4 (defer
  back-fill), AI-E4-5 (DF-1-7-B imminent, owned by 6.2), AI-E4-7 (keep structural gates green / extend the
  4.4 union to the future `cache/` tree at 5.2).
- Source: `minions_core/apaa/store/{canonical,envelope}.py` (the single serializer + content-hash),
  `minions_core/apaa/index/ast_index.py` (`AstIndex.grammar_version` / `_grammar_version`),
  `minions_core/apaa/models.py` (`AuditRequest`: `budget` / `materiality_bar` / `commit` / `critical_paths` /
  `excluded_critical_paths`), `minions_core/apaa/detectors/{secret_scan,tool_runner}.py` (the detector
  rule_id constants the descriptor set enumerates), `minions_core/apaa/pipeline.py` (the work-manifest /
  partition scope).
- Test precedent: `tests/apaa/test_canonical_determinism.py` (the golden serializer + envelope
  canonicalization pattern), `tests/apaa/test_no_web_imports.py` (`_MODULES_UNDER_GUARD` — extend),
  `tests/apaa/test_canonical_single_serializer.py` (the single-serializer AST gate).
- Defer register: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — file any NEW defer append-only
  here with the six CC-3 fields (AI-E4-4).

## Dev Agent Record

### Context Reference

- Story drafted by the BMAD Scrum Master (create-story) on 2026-06-28 from epics.md (Epic 5 / Story 5.1) +
  PRD (FR27 / NFR-D1/D2/D3) + architecture.md (AR5 cache-key closure, CC #1/#2, §437/§475) + the Epic-4 retro
  forward-coupling note (model-checkpoint is Epic-6 6.1 → use a testable V1 placeholder) + the live
  `store/{canonical,envelope}.py` single-serializer/content-hash surfaces + `index/ast_index.py`
  `grammar_version` (the real, available closure input) + `models.py::AuditRequest` + the scattered detector
  rule_id constants (→ DN-DETECTORSET declared descriptor set). Carries AI-E4-1 (no-crash input-shape +
  keystone-adequacy perturbation matrix), AI-E1-1 (non-ASCII), AI-E4-7 (structural gates green).

### Agent Model Used

claude-opus-4-8 (dev-story, implement) — 2026-06-28.

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/test_cache_key.py tests/apaa/test_no_web_imports.py tests/apaa/test_canonical_single_serializer.py -q` → all pass (the cache canary + the two extended structural gates).
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` → **971 passed, 1 skipped, 4 subtests passed** (the 760-green Epic-4 baseline + the new `test_cache_key.py` + the rest of the APAA/security/import suites; the 1 skip is the pre-existing 3.5 portability leg, host-conditional).
- `python -m mypy minions_core/apaa/cache/key.py minions_core/apaa/cache/__init__.py --ignore-missing-imports` → Success: no issues found in 2 source files.
- Golden key for the fixed baseline closure: `14fc91236a5e576bbb6a2e060e2779619959711f9346c6db5440f207ebb90694` (pinned in `test_golden_key_pinned`).
- fix iter-1 (DF-5-1-A): `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → **783 passed** (was 779; +4 from the `prompt_template_version` leg + TC-APAA-CACHE-001-21/22). RED-then-green confirmed: pre-bump golden assertion FAILED (only `test_golden_key_pinned`), all new legs green; golden regenerated to `2628b9a6ecb72e845d6fb83286ca838db326fb888837dfbd9483a05de550ca87` (the `CACHE_KEY_SCHEMA_VERSION` `1 → 2` intentional invalidation). `python -m mypy minions_core/apaa/cache/key.py minions_core/apaa/cache/__init__.py --ignore-missing-imports` → Success, no issues. Structural gates (`test_no_web_imports.py`, `test_canonical_single_serializer.py`) green.

### Completion Notes List

- **AC1 — one PURE key over the full closure.** `derive_cache_key(closure)` composes the SINGLE 1.1 serializer (`store/canonical.dumps_bytes`, via `compute_content_hash`) — NO second `json.dumps`, NO second hasher (`hashlib` is NOT imported in `cache/key.py`; the single-serializer AST gate stays green). Folds content-hash + detector-set content-hash + grammar/tool versions + budget/materiality + work-manifest scope (sorted, order-independent) + model-checkpoint. Pure: no I/O / clock / uuid / random / os.getpid / float (AST purity + banned-import scans, TC-APAA-CACHE-001-16/17/18). Golden-tested (…-03).
- **AC2 — bidirectional canary (the keystone).** Per-input perturbation matrix (`_PERTURBATIONS`, TC-…-04) asserts EACH of the 10 inputs moves the key one-at-a-time; `_baseline()` re-derives the pinned golden (closure unchanged → key unchanged). AI-E4-1 keystone-adequacy: `_key_ignoring(...)` reproduces a buggy derivation that DROPS each input, and TC-…-05 demonstrates that the ignoring-derivation does NOT move the key — the exact silent-cache-staleness bug the matrix catches (RED-then-green proof, per-input parametrized).
- **AC3 — DN-DETECTORSET.** The detector-set hash is taken over a DECLARED, FROZEN, enumerated `FROZEN_DETECTOR_SET` of `DetectorDescriptor(rule_id + code_identity + config)` (mirroring the live scattered rule_id constants: `hardcoded_secret`, `tool_failure`, `traceability_not_establishable`, `vacuous_test_heuristic`, `vacuous_test_ast`) — NOT a human `apaa_version` string. `detector_set_content_hash` is order-independent (sorted before hash) and an empty set → `CacheKeyError`. Editing a descriptor config moves the set hash → moves the key (TC-…-06, the AR6/5.3 invalidation lever).
- **AC4 — DN-PLACEHOLDER + checkpoint_drift seam.** `model_checkpoint` defaults to the stable V1 constant `V1_MODEL_CHECKPOINT = "v1-heuristic-no-llm"` occupying a key slot shaped for a clean ADDITIVE 6.1 substitution of a real captured value (no key-shape change). The drift detection SEAM = two checkpoint values derive two keys (TC-…-10). Live mid-run drift capture + the `checkpoint_drift` finding's pipeline wiring + abort/re-audit loop are DEFERRED to Epic-6 Story 6.1 (NOT built here; NOT blocked on).
- **AC5 — determinism / no-float / single-serializer / non-ASCII / ≤1200 / PURE.** Order-independent over manifest + detectors + tool_versions (TC-…-07/08, the 3.5 sorted-vs-set precedent). Non-ASCII closure (café/модуль/テスト paths + Cyrillic materiality_bar) derives a stable key under `PYTHONIOENCODING=utf-8` via the `ensure_ascii=False` single serializer (TC-…-11, AI-E1-1). Malformed inputs degrade to a typed `CacheKeyError(ValueError)` — empty detector set, non-closure arg, blank/missing required field (TC-…-12/13/14/15, AR10). `cache/key.py` is ~270 lines; `test_cache_key.py` ~340 lines (both ≤1200, NFR-M1).
- **AC6 — no regression / gates green / no scope creep.** `_MODULES_UNDER_GUARD` EXTENDED (not forked) with `minions_core.apaa.cache.key`; import-isolation + single-serializer + file-size gates green; mypy clean. NO `.apaa/cache/` byte written (verified — no `.apaa/cache` dir created; `cache/key.py` is pure, no FS I/O). NO `cli.py` / HTTP / FastAPI / new `.github/workflows` CI job (the canary is a normal `tests/apaa/` test). Frozen Epic-1..4 surfaces UNCHANGED — only edits this session: NEW `minions_core/apaa/cache/{__init__,key}.py` + NEW `tests/apaa/test_cache_key.py` + the one-tuple `_MODULES_UNDER_GUARD` extension in `tests/apaa/test_no_web_imports.py`. (The whole APAA tree is git-untracked, consistent with prior Epic-1..4 stories — no committed baseline to diff against; no spine source file was opened for write.)
- **Scope fences honored:** 5.2 memoization store, 5.3 invalidation / rejected-finding key-busting, 6.1 live LLM dispatch + real API-response checkpoint capture — all OUT. No new defer filed.

### File List

- NEW `minions_core/apaa/cache/__init__.py` — cache sub-package shell (Epic-5 driver docstring).
- NEW `minions_core/apaa/cache/key.py` — the single PURE cache-key derivation + `FROZEN_DETECTOR_SET` (DN-DETECTORSET) + `V1_MODEL_CHECKPOINT` (DN-PLACEHOLDER) + `RecordingProducingClosure` + `derive_cache_key` + `detector_set_content_hash` + typed `CacheKeyError`.
- NEW `tests/apaa/test_cache_key.py` — golden key + bidirectional CI canary (per-input perturbation matrix + AI-E4-1 keystone-adequacy RED demos + order-independence + non-ASCII + typed-degradation + purity AST scans). Area APAA-CACHE, TC-APAA-CACHE-001-01..20.
- EDIT `tests/apaa/test_no_web_imports.py` — extended `_MODULES_UNDER_GUARD` with `minions_core.apaa.cache.key` (extend, not fork).
- EDIT (fix iter-1) `minions_core/apaa/cache/key.py` — added `V1_PROMPT_TEMPLATE_VERSION` + `prompt_template_version` closure slot (DF-5-1-A), folded into `_closure_payload`, validator leg, `CACHE_KEY_SCHEMA_VERSION` `1 → 2`, docstring forward-note.
- EDIT (fix iter-1) `tests/apaa/test_cache_key.py` — added `prompt_template_version` perturbation leg + TC-APAA-CACHE-001-21/22 (placeholder default + drift seam); regenerated golden key to `2628b9a6…550ca87`.
- EDIT (fix iter-1) `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — DF-5-1-A append-only CLOSED note.

### Change Log

- 2026-06-28 — dev-story (implement, claude-opus-4-8): shipped the PURE cache-key derivation `apaa/cache/key.py` over the full recording-producing closure + the declared frozen detector-descriptor set + the bidirectional CI canary (golden + per-input perturbation matrix, each leg RED-then-green vs an ignoring-derivation). Composes the single 1.1 serializer/content-hash (no second hasher); pure/no-float/typed `CacheKeyError`; model-checkpoint V1 placeholder + checkpoint_drift detection seam (live capture deferred to 6.1). 971 passed / 1 skipped, mypy clean, structural gates green. Status → review.
- 2026-06-28 — dev-story (fix iter-1, claude-opus-4-8): resolved the sole CONCERNS finding (DF-5-1-A, Low). Added the `prompt_template_version` closure slot (architecture §77 input) mirroring the `model_checkpoint` DN-PLACEHOLDER pattern — stable V1 sentinel `V1_PROMPT_TEMPLATE_VERSION`, additive-shaped for a clean 6.1 substitution; folded into `_closure_payload`; bumped `CACHE_KEY_SCHEMA_VERSION` `1 → 2`; regenerated the pinned golden to `2628b9a6…550ca87`. Added a perturbation-matrix leg (RED-then-green via the `_key_ignoring` keystone demo) + TC-APAA-CACHE-001-21/22 (placeholder default + drift seam). DF-5-1-A CLOSED append-only in `deferred-work.md`. 783 passed / mypy clean / structural gates green. Status `in-progress` → review.
- 2026-06-28 — code-review (claude-opus-4-8, iter-1): VERDICT **concerns** → Status `review` → `in-progress`. Tests independently re-run GREEN (779 apaa+import-paths, 192+1-skip security, 44 cache+gate, mypy clean). All V1 ACs met; single-serializer/purity/determinism/non-ASCII/typed-degradation verified; canary keystone-adequacy is non-vacuous (the `_key_ignoring` RED demos traverse the real derivation). ONE Low forward-coupling finding (DF-5-1-A): the architecture §77-enumerated `prompt-template version` closure input has no key slot — out of V1 scope (no live LLM) but, unlike `model_checkpoint`, given no placeholder slot, so it must be folded by 6.1 to avoid a future silent-cache-staleness hole. See `### Review Findings`. No High/Med issues; core is correct.
- 2026-06-28 — code-review (claude-opus-4-8, iter-2, RE-REVIEW): VERDICT **pass** → Status `review` → `done`. Verified the iter-1 fix adversarially: the `prompt_template_version` slot is genuinely in the key closure (two values → two keys, TC-APAA-CACHE-001-22), covered by the bidirectional canary's REAL-derivation `_key_ignoring` RED demo (the new `_PERTURBATIONS` leg), and shaped as a clean additive 6.1 placeholder (no live-LLM dependency, purity preserved). `CACHE_KEY_SCHEMA_VERSION` `2` folded; golden regenerated to `2628b9a6…550ca87` and re-derived byte-identically. Closure-COMPLETENESS re-swept against §77 — every enumerated input (content-hash, model checkpoint, prompt-template version, grammar/tool versions, budget/materiality, work-manifest scope, detector-set content-hash) now has a folded slot; NO remaining gap. No regression: single serializer/single hasher, purity, order-independence, non-ASCII, typed `CacheKeyError`, frozen `extra="forbid"`, no float, no `.apaa/cache/` write, ≤1200 lines, headless, `_MODULES_UNDER_GUARD` extended-not-forked. Tests GREEN (783 apaa+import-paths, 48 cache+structural-gates, mypy clean). DF-5-1-A closure append-only/real.
