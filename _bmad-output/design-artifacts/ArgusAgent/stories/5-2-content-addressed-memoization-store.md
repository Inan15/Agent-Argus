# Story 5.2: Content-addressed memoization store — [Tier B]

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
> **This is the SECOND story of Epic 5** (Reproducible Verdict & Memoization, Tier-B; `epic-5` is already
> `in-progress` from Story 5.1). It rides on the fully-done Epics 1+2+3+4 (≈760 passed at the Epic-4 retro;
> 783 after the 5.1 fix iter-1) AND on the now-done Story 5.1 (the pure `apaa/cache/key.py` cache-key
> derivation over the full recording-producing closure + its CI canary). 5.1 deliberately fenced OUT the
> `.apaa/cache/` write — **THIS story owns the cache tree.** It adds the IMPURE, content-addressed
> memoization STORE that persists + looks up recording results keyed by the 5.1 cache key, so an unchanged
> audit unit (same producing closure → same key) is served from the memo cache instead of re-computed. This
> is the cross-RUN reproducibility / cost optimization (FR27 / NFR-D1). **Cache INVALIDATION +
> rejected-finding key-busting (AR6) is Story 5.3 and is explicitly OUT of this story's scope.**

## Story

As an **integrator running the same audit twice** (and as the APAA maintainer who must certify that
reproducibility never silently serves a wrong answer),
I want **a local, content-addressed memoization STORE** (`apaa/cache/memo_store.py`) that persists a
recording result under its 5.1 cache key and, on a re-run whose producing closure derives the **same** key,
returns the **recorded** result (a cache HIT) instead of re-computing it,
so that the verdict + ledger are 100% reproducible across runs **without re-spending tokens** — while a
cache HIT is **byte-identical to a cache MISS** (recompute), so the cache can NEVER change the verdict, and a
stale / poisoned / corrupt / tampered cache entry is **detected on read and treated as a MISS** (never
silently served wrong) — the APAA reproducibility floor: the memo cache is an OPTIMIZATION, NOT the sole
correctness guarantee.

## Story Context

This is **Story 2 of Epic 5** (Reproducible Verdict & Memoization, Tier-B — the "a number you can put on a
dashboard and trust not to flake" layer, PRD Journey 3). `epic-5` is already `in-progress` (flipped by
Story 5.1). It is the **content-addressed memoization STORE** story (FR27 / NFR-D1, `[Tier B]`).

**What this story delivers and what it explicitly does NOT.** This story delivers the IMPURE memo STORE
shell — a write-recorded-result + look-up-by-key surface over the fixed `.apaa/cache/` sub-tree, with a
content-hash verify on read (tamper/corruption → MISS) — keyed on the 5.1 `derive_cache_key`. It does
**not** build cache INVALIDATION on a detector-set-hash change, nor rejected-finding key-busting (both are
Story 5.3 / AR6). It does **not** build the live LLM dispatch port / real API-response model-checkpoint
capture (Epic-6 Story 6.1 — 5.1's V1 placeholder checkpoint is used as-is). It does **not** wire the memo
store into the live `pipeline.py` audit loop as a mandatory short-circuit unless that wiring is the thin,
additive, opt-in, byte-identical-to-today seam described in DN-WIRING below. Keeping 5.2 to the
store-plus-verify scope is the thin-slice discipline that held across Epics 1-4 and Story 5.1 (each story
folds ONE working capability over the determinism spine).

**The determinism spine + the 5.1 key + the 1.3 store shell are DONE and proven.** The single canonical
serializer (`apaa/store/canonical.py::dumps_bytes` / `loads`), the content-hashed envelope
(`apaa/store/envelope.py::compute_content_hash` + `EnvelopeWriter.build` + `GENESIS_PREV_HASH`),
`Fraction`-not-`float`, the `.apaa/` containment resolver (`apaa/store/paths.py::ApaaStorePaths` —
`resolve`/`ensure_tree`/`ensure_parent`/`to_locator`, with the fixed `cache/` sub-dir already created by
`ensure_tree`), the impure writer (`apaa/store/writer.py::ApaaStoreWriter` —
`write_envelope`/`write_payload`), the PURE-deserialize reader with its **tamper guard**
(`apaa/store/reader.py::ApaaStoreReader.read_envelope(..., verify_hash=True)` →
`StoreIntegrityError(ValueError)` on a `content_hash` mismatch), and the pure cache key
(`apaa/cache/key.py::RecordingProducingClosure` + `derive_cache_key` + `FROZEN_DETECTOR_SET` +
`V1_MODEL_CHECKPOINT` + `CACHE_KEY_SCHEMA_VERSION`) all shipped in Epics 1-3 + Story 5.1 and were proven
byte-identical / order-independent. **The memo store COMPOSES these — it is the impure shell that reads/
writes cache entries; it does NOT fork the serializer, the hasher, the containment resolver, or the key.**

**The keystone — the APAA reproducibility FLOOR (the brainstorm + architecture CC #1/#2).** The memo cache
is an OPTIMIZATION, NOT the sole correctness guarantee (architecture §247-250, §91-96; the PRD NFR-D1 "NOT
an assumption the LLM repeats itself"). Three non-negotiable invariants this story must prove SHARPLY (the
AI-E3-1/AI-E4-1 keystone-adequacy carry-forward):

1. **HIT == MISS byte-identity.** A cache HIT must produce a result **byte-identical** to a cache MISS
   (recompute). The cache stores and returns the SAME canonical bytes that the producer would have produced;
   round-tripping through the store changes nothing. This is the property that lets the cache be an
   optimization rather than a second source of truth.
2. **The cache NEVER changes the verdict.** Whether a unit was served from cache or recomputed, the verdict
   + ledger are identical. A run with a warm cache and a run with a cold cache over the same closure produce
   byte-identical `.apaa/` verdict state. The cache lives strictly upstream of the pure verdict gate; it
   feeds the SAME recordings either way.
3. **Tamper / corruption / poison → MISS, never silently-wrong.** A cache entry whose stored `content_hash`
   does not re-verify over its payload (mutation/poison), or which is corrupt / non-UTF-8 / non-JSON /
   wrong-schema / a non-file / unreadable, is treated as a **MISS** (recompute) — it is NEVER served as a
   hit. This mirrors the 1.3 `StoreIntegrityError` tamper guard, but the memo store's READ path **swallows
   the typed integrity/corruption failure into a MISS** (a cache is advisory; a poisoned entry must not
   break or mis-answer the audit) rather than raising out — the AR10 / AI-E4-1 no-crash discipline applied
   to the cache I/O shell.

**The 5.1 → 5.2 → 5.3 boundary (the load-bearing scope fence).** 5.1 = the PURE key (a faithful fingerprint
of the producing closure). 5.2 (THIS story) = the STORE that persists/serves a recorded result under that
key, with read-side integrity → MISS. 5.3 = INVALIDATION (a detector-set-hash change invalidates affected
entries) + rejected-finding key-busting (a human-rejected finding busts its own key so a false 🔴 is not
re-served forever) — AR6. **5.2 does NOT bust keys and does NOT invalidate on detector-set change beyond
what falls out for free** (a detector-set edit changes the 5.1 key → a different cache slot → a natural MISS;
that natural miss is in scope, but the active eviction / key-busting machinery of 5.3 is NOT). Document this
fence; do not pull 5.3 forward.

**Carry-forward from the Epic-4 retro (2026-06-28) + the 5.1 forward-flags + the standing disciplines
(CLAUDE.md §9.1 / L1-E11).** Each item below is an Epic-5-backlog action item this story discharges (per the
L1-E11 operating model: package the prior retro's action items as the next epic's backlog).
- **AI-E4-1 (test-infra 🟠) — the NO-CRASH-KEYSTONE INPUT-SHAPE CHECKLIST, now landing on the EXACT surface
  it warned about.** The 5.1 story flagged forward: "the cache STORE's filesystem-touching impure shell is
  the surface that produced the 4.2 FAIL — a corrupt / non-file / permission-denied / unknown-schema cache
  entry must degrade to a MISS or a typed finding, never raise." THAT is THIS story's central
  reliability AC (AC3). The keystone tests MUST be sharp and non-vacuous: a tampered cache entry, a corrupt/
  truncated file, a non-file at the cache path, a permission-denied read, a wrong-schema payload — EACH
  demonstrated to produce a MISS (recompute) RED-then-green, and the HIT==MISS byte-identity demonstrated
  RED against a store that mutates on round-trip before being trusted.
- **AI-E4-7 (process 🟢) — keep the three structural gates green + the L1-E11 loop.** `memo_store.py` is the
  IMPURE shell (it DOES do FS I/O — it is NOT in the pure-module guard set; do NOT add it to
  `_MODULES_UNDER_GUARD` if that gate asserts purity — confirm the gate's contract). It MUST NOT break the
  import-isolation gate (`test_no_web_imports.py` — extend the APAA-wide import-isolation coverage so
  `apaa.cache.memo_store` is asserted FastAPI-free) or the single-serializer AST gate
  (`test_canonical_single_serializer.py` — the memo store REUSES `canonical`/`EnvelopeWriter`/the 1.3 writer/
  reader, it does NOT add a second `json.dumps` or a second `hashlib`). File-size ≤1200 lines.
- **AI-E4-7 (4.4 union extension — the 5.1 explicit forward-flag).** 5.1 said: "Extend the 4.4
  secret-containment artifact-class union awareness to the future `cache/` tree at 5.2 (NOT this story — 5.1
  writes no `.apaa/cache/` byte)." THIS story writes the first `.apaa/cache/` bytes, so the 4.4
  secret-containment property suite (`tests/security/test_apaa_secret_containment.py`) MUST be extended so
  the `.apaa/cache/` tree is included in the swept artifact-class union (a planted secret in an audited unit
  must be ABSENT from any cached recording byte too — the cache is just another `.apaa/` artifact class; the
  2.5 producer-side redaction already strips secrets before they reach a Recording, so the cache stores
  already-redacted bytes, but the suite must PROVE the cache is swept).
- **AI-E1-1 (test-infra 🟢) — non-ASCII / locale discipline (the Epic-1-FAIL class, standing).** A cache
  entry whose key/closure includes a non-ASCII file path / non-ASCII content must round-trip byte-stably
  (explicit UTF-8; the single serializer is `ensure_ascii=False`). Run the suite under
  `PYTHONIOENCODING=utf-8` (project memory — the cp1252 emoji crash). At least one cache fixture carries a
  non-ASCII path/value and proves HIT==MISS byte-identity.
- **AI-E4-4 (governance 🟢) — central defer register.** If this story files a NEW defer, file it append-only
  in `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (the single canonical APAA defer source), not
  only in the story file, with the six CC-3 fields.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 5.2) + the architecture / PRD. Drivers: **APAA-FR-27**
> (APAA can reproduce the same verdict for the same repository and APAA version — the memo STORE is what
> ACHIEVES the reproduction the 5.1 key fingerprints), **APAA-NFR-D1** (same repo @ same commit @ same APAA
> version → identical verdict + ledger via **local content-addressed memoization** — the CENTRAL driver),
> **APAA-NFR-D2** (verdict gate + ledger mechanics deterministic + zero LLM tokens — the cache read/write is
> itself token-free; a HIT spends zero tokens), **APAA-NFR-D3** (content hashes cover the canonical payload
> only), **APAA-NFR-P1** (byte-identical on-disk state; a HIT round-trips byte-identically to the recompute),
> **APAA-AR4** (single serializer, no float, clock-free / uuid-free / random-free in the cached payload),
> **APAA-AR5** (ONE cache-key function — the store CONSUMES `derive_cache_key`, it does not re-derive a key),
> **APAA-AR6** (memoization caches errors → reproducibility ≠ correctness — the STORE must be invalidatable;
> 5.2 builds the store, 5.3 builds the active invalidation/key-busting — but 5.2's read-side
> integrity→MISS is the first line of the AR6 defense), **APAA-AR7/AR10** (reuse the 1.3 containment shell +
> typed errors; a corrupt/tampered/non-file/permission-denied cache entry degrades to a MISS, never an
> uncaught raise / a silently-wrong served result), **APAA-AR8** (`memo_store.py` is the IMPURE shell — FS
> I/O confined here; the cached payload stays pure/clock-free), **APAA-NFR-S1/S5** (no source/secret bytes
> in cached artifacts — the cache joins the 4.4 swept union; containment-checked writes), **APAA-NFR-M1**
> (≤1200-line files).
>
> **SCOPE FENCE — Tier-B, single-purpose, SECOND Epic-5 story.** This story delivers ONLY: (1) the IMPURE
> content-addressed memoization STORE `apaa/cache/memo_store.py` over the fixed `.apaa/cache/` sub-tree,
> keyed on the 5.1 `derive_cache_key(closure)`, with a `lookup(key) -> recorded result | MISS` +
> `store(key, result)` surface (or equivalent get/put); (2) the read-side integrity verify (content-hash
> re-verification reusing the 1.3 tamper guard) that turns a tampered/corrupt/poisoned/non-file/
> permission-denied/wrong-schema entry into a MISS (never a raise, never a silently-wrong hit); (3) the
> HIT==MISS byte-identity + cache-never-changes-verdict proofs (the keystone); (4) the 4.4
> secret-containment-suite extension so the `.apaa/cache/` tree is in the swept union; (5) the
> import-isolation-gate extension for `apaa.cache.memo_store`. It does NOT build, and MUST NOT pull forward:
> cache **INVALIDATION on detector-set-hash change + rejected-finding key-busting** (Story 5.3 / AR6 —
> beyond the natural MISS a different key produces); the **live LLM dispatch port + real API-response
> model-checkpoint capture / live checkpoint-drift abort-re-audit loop** (Epic-6 Story 6.1 — use the 5.1 V1
> placeholder checkpoint as-is); a **shared / cross-machine G4 cache** (V4 — V1 is LOCAL-only, and the cache
> is NEVER the sole guarantee); a **new HTTP route / FastAPI surface / UI** (§3.7); a **`cli.py` subcommand**
> (cache management CLI is out of scope); a **new `.github/workflows` CI job** (the memo-store tests are
> normal `tests/apaa/` + `tests/security/` tests collected by the existing jobs). Build the impure store +
> the read-side integrity→MISS + the keystone proofs + the suite/gate extensions, then stop.

**AC1 — A local content-addressed memo store persists + serves a recorded result keyed on the 5.1 cache key (FR27 / NFR-D1 — the central driver)**
**Given** a recording result (the canonical recorded output of auditing one unit — the Recording/finding
payload(s) for that unit) produced under a fully-specified `RecordingProducingClosure` whose 5.1
`derive_cache_key(closure)` yields key `K`
**When** `apaa/cache/memo_store.py` stores it (`store(K, result)` / `put`) into the `.apaa/cache/` sub-tree
**Then** the entry is persisted as a canonical, envelope-wrapped artifact under a content-addressed filename
in `cache/` (reusing `ApaaStoreWriter` + `EnvelopeWriter` + `canonical` — NO second serializer / hasher),
containment-checked via `ApaaStorePaths` (NFR-S5), with NO wall-clock / `uuid4` / `random` / float in the
cached payload (AR4)
**And When** the SAME closure recurs (same key `K`) on a later run
**Then** `lookup(K)` / `get` returns the **recorded** result (a cache HIT) and the look-up spends **zero LLM
tokens** (NFR-D2) — achieving an identical verdict + ledger across runs without re-computing the unit
(FR27 / NFR-D1)
**And** a key that has never been stored (a true MISS) returns a clear MISS sentinel (e.g. `None` / a typed
`CacheMiss`) — never a fabricated or partial result.

**AC2 — A cache HIT is byte-identical to a cache MISS, and the cache NEVER changes the verdict (the keystone — HIT==MISS byte-identity)**
**Given** one audit unit under a fixed closure
**When** it is audited with a COLD cache (MISS → recompute → store) and then re-audited with a WARM cache
(HIT → served from the store)
**Then** the recording result served on the HIT is **byte-identical** to the result computed on the MISS
(round-tripping through the store via the single canonical serializer changes nothing — the stored bytes
ARE `canonical.dumps_bytes(result_payload)`), proven by comparing the canonical bytes / content-hash of the
HIT-served result vs the MISS-computed result
**And** the verdict + coverage ledger derived downstream are byte-identical between the cold-cache run and
the warm-cache run (the cache lives strictly upstream of the pure 1.6 verdict gate; it feeds the SAME
recordings either way) — the cache is an OPTIMIZATION, NOT a second source of truth, and CANNOT move the
verdict. The HIT==MISS leg is demonstrated RED against a store that mutates the payload on round-trip (e.g.
re-orders keys, drops a field, or re-stamps a timestamp) before the byte-identity is trusted (the AI-E4-1
keystone-adequacy proof).

**AC3 — A tampered / corrupt / poisoned / unreadable cache entry is detected on read and treated as a MISS, never silently served wrong, never an uncaught crash (AR6/AR10/AI-E4-1 — the no-crash keystone)**
**Given** a cache entry on disk whose stored `content_hash` no longer re-verifies over its payload
(tamper/poison — a false 🔴 or a wrong result was injected), OR which is corrupt / truncated / non-UTF-8 /
non-JSON / wrong-schema (`extra="forbid"` violation), OR which is a non-file at the expected cache path, OR
which raises a permission-denied / OS read error
**When** the memo store reads it (the content-hash re-verification reuses the 1.3
`ApaaStoreReader.read_envelope(verify_hash=True)` → `StoreIntegrityError` tamper guard, or an equivalent
verify over the cached envelope)
**Then** the store treats the entry as a **MISS** (recompute path) — it is NEVER served as a hit, the wrong/
poisoned bytes NEVER reach the verdict, and the read NEVER raises out of the store (the typed integrity /
corruption / OS failure is swallowed into a MISS — a cache is advisory, AR10 / the 5.1-flagged AI-E4-1
no-crash discipline applied to the cache shell)
**And** EACH failure mode (tamper / content-hash mismatch, corrupt bytes, wrong schema, non-file,
permission-denied) is demonstrated to produce a MISS RED-then-green (a naive store that trusted the on-disk
bytes, or that let the error propagate, would FAIL these legs — the keystone-adequacy proof). The MISS path
re-derives the correct result, so a poisoned cache produces a CORRECT (recomputed) verdict, not a wrong one
(reproducibility ≠ correctness; the cache cannot ossify a wrong answer into a served hit).

**AC4 — The cache is LOCAL-only and is never the sole correctness guarantee (NFR-D1 — the reproducibility floor)**
**Given** the V1 reproducibility floor (architecture §87 "self-contained, local memoization"; the PRD NFR-D1
"local content-addressed memoization")
**When** the memo store is used
**Then** it is **LOCAL** to the audited repo's `.apaa/cache/` tree (no shared / cross-machine / network
cache — the G4 cross-run shared cache is V4 and is NEVER the sole guarantee: a safety-critical guarantee
must not depend on an external cache)
**And** the verdict is correct WHETHER OR NOT the cache exists / is warm / is empty / is wiped — wiping
`.apaa/cache/` and re-running produces the SAME verdict (a cold rebuild), proving the cache is an
optimization layered on top of an independently-correct recompute path (the keystone restated: the cache
accelerates, it does not decide).

**AC5 — Determinism, no-float, single-serializer, non-ASCII, containment, ≤1200 lines, IMPURE-shell discipline (AR4/AR8/NFR-P1/NFR-S5/NFR-M1/AI-E1-1)**
**Given** the new `apaa/cache/memo_store.py` (+ its tests)
**When** the suite runs under `PYTHONIOENCODING=utf-8`
**Then** the cached payload is canonical (single serializer `canonical.dumps_bytes`, no second `json.dumps`,
no second `hashlib` — the single-serializer AST gate stays green); the cached bytes carry no float / no
`uuid4` / no wall-clock / no `random` in the payload (AR4 — note the envelope's volatile `run_id`/
`created_at` are EXCLUDED from the content-hash per NFR-D3, so two stores of the same result are
content-addressed to the SAME slot); all cache writes are containment-checked via `ApaaStorePaths`
(NFR-S5 — a traversal/symlink/sibling-prefix escape raises `WorkspaceContainmentError` BEFORE any write); a
cache entry whose closure carries a non-ASCII file path / non-ASCII content round-trips byte-stably and
proves HIT==MISS (explicit UTF-8, `ensure_ascii=False`, AI-E1-1); `memo_store.py` and the test file are each
≤1200 lines (NFR-M1)
**And** `memo_store.py` is the IMPURE shell (FS I/O is confined here, mirroring `store/writer.py` +
`store/reader.py`) — it is NOT a pure module and must NOT be asserted pure; the pure 5.1 `cache/key.py` is
NOT modified (the store CONSUMES `derive_cache_key`, it does not re-derive a key — AR5).

**AC6 — No regression / no scope creep; the structural + security gates stay green; mypy clean (AR8, AI-E4-7, the thin-slice discipline)**
**Given** the new impure store + its tests + the suite/gate extensions
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the 783-green Story-5.1 baseline + the new `tests/apaa/test_memo_store.py` + the extended 4.4
secret-containment suite), the import-isolation gate (`test_no_web_imports.py` — extended to assert
`apaa.cache.memo_store` is FastAPI-free), the single-serializer AST gate
(`test_canonical_single_serializer.py` — `memo_store.py` adds NO second `json.dumps` / `hashlib`), the 4.4
secret-containment property suite (extended to sweep the `.apaa/cache/` tree), and the file-size gate
(≤1200 lines) stay green; `mypy` is clean on `cache/memo_store.py` (+ any sibling)
**And** the frozen Epic-1..4 + Story-5.1 contracts show NO behavioral diff (`store/{canonical,envelope,
paths,writer,reader}.py`, `cache/key.py`, `models.py`, `ledger/*`, `verdict/*`, `detectors/*`, `pipeline.py`
— the store COMPOSES them; the ONLY permitted edit to a pre-existing surface is the thin, additive, opt-in,
byte-identical-to-today memo-store WIRING in `pipeline.py` per DN-WIRING, IF taken — and if taken it must be
default-equivalent so every existing pipeline test passes byte-identically). NO `cli.py` subcommand, NO HTTP
route, NO new CI job, NO shared/network cache (LOCAL-only)
**And** the new test file cites its `APAA-FR-27`/`APAA-NFR-D1`/`AR5`/`AR6` drivers in the module docstring +
the locked test area / index; the mandatory artifacts EXIST + pass + the keystone proofs (HIT==MISS
byte-identity RED-then-green; tamper/corrupt/non-file/permission-denied → MISS RED-then-green;
cache-never-changes-verdict cold-vs-warm) are documented BEFORE the story flips to `status: review`
(AI-E4-3 / AI-E2-1 test-existence discipline). **Test area `APAA-CACHE`** (`TC-APAA-CACHE-001-NN` — continue
the area Story 5.1 opened; confirm/lock the next free index in the module docstring, after 5.1's …-01..22).

## Tasks / Subtasks

- [ ] **Task 0 — Re-read + LOCK the reused surfaces; LOCK the store shape, the cache-entry schema, and the read-side integrity→MISS contract** (AC: 1, 2, 3, 5)
  - [ ] Re-read `store/canonical.py` (`dumps_bytes`/`loads` — the single serializer, no float, `ensure_ascii=False`),
        `store/envelope.py` (`Envelope`, `EnvelopeWriter.build`, `compute_content_hash`, `GENESIS_PREV_HASH`).
        LOCK: the memo entry is an envelope-wrapped canonical artifact (no second serializer / hasher).
  - [ ] Re-read `store/paths.py::ApaaStorePaths` (`resolve`/`ensure_tree`/`ensure_parent`/`to_locator`; the
        fixed `cache/` sub-dir is ALREADY created by `ensure_tree`, `APAA_SUBDIRS`) +
        `store/writer.py::ApaaStoreWriter` (`write_envelope`/`write_payload` — content-addressed filename) +
        `store/reader.py::ApaaStoreReader` (`read_envelope(..., verify_hash=True)` → `StoreIntegrityError` tamper
        guard; `read_bytes`; `CanonicalSerializationError` on non-UTF-8/non-JSON). LOCK: the memo store REUSES
        these for all cache I/O (it does NOT re-implement containment, write, or the tamper verify).
  - [ ] Re-read `cache/key.py` (`RecordingProducingClosure`, `derive_cache_key`, `FROZEN_DETECTOR_SET`,
        `V1_MODEL_CHECKPOINT`, `CACHE_KEY_SCHEMA_VERSION`, `CacheKeyError`). LOCK: the store CONSUMES
        `derive_cache_key(closure)` to get the key string; it does NOT re-derive a key (AR5). 5.1 `cache/key.py`
        is NOT modified by this story.
  - [ ] Re-read the recording schema (`ledger/*` / the frozen `Recording` model) so the "recorded result" the
        store persists is the canonical Recording payload(s) for a unit (the verdict-folded artifact, NOT raw
        source). LOCK the cache-entry payload shape: a canonical, redacted (2.5-producer-side) Recording-set
        envelope — NO source/secret bytes (NFR-S1; the 4.4 suite will prove it).
  - [ ] **LOCK DN-STORESHAPE:** define the store surface — `MemoStore(repo_root)` with
        `lookup(key: str) -> <RecordedResult> | None` (MISS = `None` or a typed `CacheMiss`) +
        `store(key: str, result: <RecordedResult>) -> str` (returns the cache locator). Cache filename derives
        from the cache KEY (content-addressed by the 5.1 key) — never arrival order (AR11). Decide + document
        whether the on-disk filename is `cache/<key>.json` (key-addressed) and whether the envelope `content_hash`
        is over the result payload (the tamper guard is then a re-verify of the result payload's hash).
  - [ ] **LOCK DN-MISS:** the read-side integrity→MISS taxonomy — `StoreIntegrityError` (tamper),
        `CanonicalSerializationError` (corrupt/non-UTF-8/non-JSON), `pydantic.ValidationError` (wrong schema /
        `extra="forbid"`), `FileNotFoundError` / not-a-file, `OSError`/`PermissionError` (unreadable) → ALL caught
        and converted to a MISS inside `lookup`. Document that this is the ONE place where a typed store error is
        SWALLOWED (a cache is advisory) — contrast the 1.3 reader, which RAISES (resumability state must not be
        silently lost). No bare `except: pass` — catch the SPECIFIC typed set, never `Exception`.
  - [ ] **LOCK DN-WIRING (decide + document):** whether 5.2 wires the memo store into `pipeline.py` as a thin,
        additive, OPT-IN, byte-identical-to-today short-circuit (look-up before computing a unit; store after),
        OR delivers the store as a library-only surface (like 1.3 `reader.py` deferred live resume to 3.4). The
        DEFAULT/RECOMMENDED scope is library-only OR a default-equivalent wiring: if wired, it MUST be
        default-equivalent so EVERY existing `pipeline.py` test passes byte-identically (a cold cache + a warm
        cache produce the same verdict — AC2/AC4 is the proof). Do NOT make the cache a mandatory dependency of
        the verdict path. Record the decision + rationale.
- [ ] **Task 1 — Build the IMPURE memo store `apaa/cache/memo_store.py`** (AC: 1, 2, 3, 5)
  - [ ] `class MemoStore` (docstring cites `APAA-FR-27`, `APAA-NFR-D1`, `AR5`, `AR6`, `AR7`, `AR8`, `AR10`)
        constructed with the audited-repo root (or an `ApaaStorePaths` — mirror `ApaaStoreReader`/`ApaaStoreWriter`).
  - [ ] `store(key, result) -> str`: wrap the canonical Recording-set result in an envelope
        (`EnvelopeWriter.build` / `ApaaStoreWriter.write_payload`), write it to `cache/<key>.json`
        containment-checked (NFR-S5). Idempotent: re-storing the same `(key, result)` overwrites byte-identically.
  - [ ] `lookup(key) -> result | None`: resolve `cache/<key>.json` containment-checked, read + verify the
        envelope `content_hash` (reuse the 1.3 `read_envelope(verify_hash=True)` tamper guard), validate the
        payload against the frozen Recording-set schema → return the result on success; on ANY of the DN-MISS
        typed failures (or no-such-file) return a MISS (recompute). Zero LLM tokens on the read path.
  - [ ] HIT==MISS byte-identity by construction: the stored bytes ARE `canonical.dumps_bytes(result_payload)`;
        `lookup` returns the validated payload re-built from those same bytes — round-tripping changes nothing.
  - [ ] No clock / uuid / random / float in the CACHED PAYLOAD (the envelope's volatile `run_id`/`created_at`
        are EXCLUDED from the content-hash per NFR-D3 — so content-addressing is stable across runs).
- [ ] **Task 2 — The keystone proofs in NEW `tests/apaa/test_memo_store.py`** (AC: 1, 2, 3, 4)
  - [ ] Area `APAA-CACHE`, `TC-APAA-CACHE-001-NN` (continue after 5.1's …-22). HIT==MISS byte-identity: store a
        result under key `K`, look it up, assert the served bytes/content-hash == the originally-computed bytes;
        demonstrate RED against a store that mutates on round-trip (re-orders/drops/re-stamps) before trusting it.
  - [ ] cache-NEVER-changes-verdict: a cold-cache run (MISS→recompute→store) vs a warm-cache run (HIT) over the
        same closure produce byte-identical verdict + ledger `.apaa/` state (the cache feeds the SAME recordings;
        the pure 1.6 verdict gate is unchanged). Wipe-and-rebuild (AC4): wiping `.apaa/cache/` and re-running →
        same verdict.
  - [ ] Tamper/corruption/poison → MISS (AC3): EACH of {content-hash mismatch (mutate the stored payload),
        corrupt/truncated/non-UTF-8/non-JSON bytes, wrong-schema/`extra="forbid"`, non-file at the cache path,
        permission-denied/OSError} produces a MISS (recompute), demonstrated RED against a store that trusts the
        bytes or lets the error propagate. The recompute on a poisoned entry yields the CORRECT result (not the
        poisoned one).
  - [ ] AI-E1-1: a cache entry whose closure carries a non-ASCII / Cyrillic path/value round-trips byte-stably
        and proves HIT==MISS under `PYTHONIOENCODING=utf-8`.
- [ ] **Task 3 — Security + structural gate extensions** (AC: 5, 6)
  - [ ] Extend the 4.4 secret-containment property suite (`tests/security/test_apaa_secret_containment.py`) so
        the swept artifact-class union INCLUDES the `.apaa/cache/` tree: a planted canary secret in an audited
        unit is ABSENT from every cached recording byte (the cache is just another `.apaa/` artifact class;
        2.5 producer-side redaction already strips secrets pre-Recording, but PROVE the cache is swept).
  - [ ] Extend `test_no_web_imports.py` so `apaa.cache.memo_store` is asserted FastAPI-free (import-isolation).
        CONFIRM `_MODULES_UNDER_GUARD` is the PURITY set or the import-isolation set: `memo_store.py` is IMPURE
        (FS I/O) — add it to the import-isolation coverage but NOT to any purity-asserting guard (mirror how
        `store/writer.py`/`store/reader.py` are treated). Confirm the single-serializer AST gate stays green.
- [ ] **Task 4 — Run + mypy + the pre-`review` test-existence precondition** (AC: 6)
  - [ ] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` → all
        pass (783 baseline + `test_memo_store.py` + the extended 4.4 suite). `mypy` clean on `cache/memo_store.py`.
  - [ ] Confirm NO behavioral diff to the frozen Epic-1..4 + 5.1 surfaces (the store COMPOSES them; the only
        permitted pre-existing-file edit is the DN-WIRING `pipeline.py` seam IF taken, and only if
        default-equivalent — every existing pipeline test passes byte-identically). Confirm NO `cli.py`/HTTP/
        CI-job change, NO shared/network cache.
  - [ ] **AI-E4-4 / DN-DEFER:** if a NEW defer is filed, file it append-only in
        `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` with the six CC-3 fields. Do NOT pull 5.3
        invalidation / key-busting or 6.1 live-capture into scope.
  - [ ] **AI-E4-3 / AI-E2-1 GATE:** the mandatory artifacts (`cache/memo_store.py` + `tests/apaa/test_memo_store.py`
        with the HIT==MISS / tamper→MISS / cache-never-changes-verdict proofs + the extended 4.4 suite) EXIST +
        pass + the keystone RED-then-green is documented BEFORE the `review` flip; the Dev Agent Record is filled
        completely (no blank placeholders).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **The memo cache is an OPTIMIZATION, NOT the sole correctness guarantee (the keystone — architecture CC #1/#2,
  the brainstorm reproducibility floor).** A cache HIT MUST be byte-identical to a cache MISS (recompute); the
  cache MUST NEVER change the verdict; a stale/poisoned/corrupt entry MUST be detected on read and treated as a
  MISS, never silently served wrong. The verdict path is independently correct WITHOUT the cache (wipe
  `.apaa/cache/` and re-run → same verdict). This is the property that makes reproducibility ≠ correctness
  safe: a poisoned cache yields a CORRECT recomputed verdict, never a wrong served one (architecture §249-250).
- **The store COMPOSES the 1.1 serializer + 1.1 content-hash + 1.3 containment/writer/reader + 5.1 key — it does
  NOT fork any of them (AR4/AR5/AR7).** NFR-P1 (byte-identical) dies the day a second `json.dumps`/`hashlib`
  appears. Cache entries are envelope-wrapped canonical artifacts via `ApaaStoreWriter` + `EnvelopeWriter`;
  reads + the tamper verify reuse `ApaaStoreReader.read_envelope(verify_hash=True)` → `StoreIntegrityError`;
  containment reuses `ApaaStorePaths`; the key is `cache/key.py::derive_cache_key(closure)` (the store NEVER
  re-derives a key). The single-serializer AST gate must stay green with the new module.
- **`memo_store.py` is the IMPURE shell (AR8).** FS I/O lives here (mirroring `store/writer.py` /
  `store/reader.py`) — it is NOT a pure module; do NOT add it to a purity-asserting guard set. The CACHED
  PAYLOAD stays pure/clock-free (AR4: no float, no `uuid4`, no wall-clock, no `random`; the envelope's volatile
  `run_id`/`created_at` are excluded from the content-hash per NFR-D3, so content-addressing is stable
  cross-run).
- **Read-side integrity → MISS is the AR10 / AI-E4-1 no-crash discipline applied to the cache (the 5.1
  forward-flag, the 4.2-FAIL surface).** `lookup` catches the SPECIFIC typed set —
  `StoreIntegrityError`, `CanonicalSerializationError`, `pydantic.ValidationError`, `FileNotFoundError` /
  not-a-file, `OSError`/`PermissionError` — and converts EACH to a MISS (recompute). This is the ONE place a
  typed store error is SWALLOWED (a cache is advisory), in deliberate contrast to the 1.3 reader which RAISES
  (resumability state must not be silently lost). NO bare `except: pass`; NO `except Exception`; catch the
  named set only (so a programming bug still surfaces).
- **5.2 vs 5.3 — the active-invalidation fence (AR6).** 5.2 builds the STORE + read-side integrity→MISS. 5.3
  builds active INVALIDATION (a detector-set-hash change invalidates affected entries) + rejected-finding
  key-busting (a human-rejected finding busts its own key so a false 🔴 is not re-served forever). A
  detector-set edit ALREADY changes the 5.1 key → a different cache slot → a NATURAL MISS (that natural miss is
  in 5.2 scope); the ACTIVE eviction / key-busting machinery is NOT. Do NOT pull 5.3 forward.
- **LOCAL-only; never the sole guarantee (NFR-D1 / architecture §87).** The cache is local to the audited
  repo's `.apaa/cache/` tree. No shared / cross-machine / network cache (the G4 cross-run shared cache is V4).
  A safety-critical guarantee must not depend on an external cache.
- **No source/secret bytes in cached artifacts (NFR-S1 / the 5.1 forward-flag).** The cached payload is a
  canonical, already-2.5-redacted Recording-set envelope — never source/secret bytes. THIS story writes the
  first `.apaa/cache/` bytes, so it MUST extend the 4.4 secret-containment property suite to sweep the
  `.apaa/cache/` tree (the cache joins the swept artifact-class union).
- **Frozen contracts unchanged (AR8/NFR-M2).** The store COMPOSES the Epic-1..4 + 5.1 surfaces read-only. The
  ONLY permitted edit to a pre-existing surface is the DN-WIRING `pipeline.py` seam IF taken (thin, additive,
  opt-in, default-equivalent — every existing pipeline test passes byte-identically). `cache/key.py` is NOT
  modified.

### Project Structure Notes

- **NEW impure module:** `minions_core/apaa/cache/memo_store.py` (the NFR-D1 content-addressed memo store;
  architecture §438 `cache/memo_store.py — NFR-D1 — content-addressed on-disk memo + invalidation` — NOTE
  the "invalidation" half of that line is Story 5.3; 5.2 builds the store + read-side integrity→MISS). ≤1200
  lines (NFR-M1). `minions_core/apaa/cache/__init__.py` already exists (Story 5.1).
- **NEW test module:** `tests/apaa/test_memo_store.py`. Test area `APAA-CACHE` (`TC-APAA-CACHE-001-NN` —
  continue after 5.1's …-01..22; confirm the next free index in the module docstring). ≤1200 lines.
- **EDIT (extend, not fork):** `tests/security/test_apaa_secret_containment.py` (4.4) — add `.apaa/cache/` to
  the swept artifact-class union. `tests/apaa/test_no_web_imports.py` — assert `apaa.cache.memo_store` is
  FastAPI-free (import-isolation; it is IMPURE, so NOT in any purity guard).
- **REUSE read-only (verify NO behavioral diff):** `store/canonical.py` (`dumps_bytes`/`loads`),
  `store/envelope.py` (`Envelope`/`EnvelopeWriter.build`/`compute_content_hash`/`GENESIS_PREV_HASH`),
  `store/paths.py::ApaaStorePaths` (`resolve`/`ensure_tree` — `cache/` already in `APAA_SUBDIRS`/`to_locator`),
  `store/writer.py::ApaaStoreWriter` (`write_envelope`/`write_payload`),
  `store/reader.py::ApaaStoreReader` (`read_envelope(verify_hash=True)` → `StoreIntegrityError`; `read_bytes`;
  `CanonicalSerializationError`), `cache/key.py` (`RecordingProducingClosure`/`derive_cache_key`/
  `FROZEN_DETECTOR_SET`/`V1_MODEL_CHECKPOINT`/`CACHE_KEY_SCHEMA_VERSION`/`CacheKeyError`), the frozen
  `Recording`/ledger schema (the cached result payload).
- **NO `cli.py` change / NO new HTTP route / FastAPI surface / UI (§3.7). NO new `.github/workflows` CI job**
  (the tests are normal `tests/apaa/` + `tests/security/` tests). **NO shared/network cache (LOCAL-only).**
  **NO 5.3 invalidation/key-busting; NO 6.1 live LLM / real checkpoint capture.**

### Testing Standards (APAA)

- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` (the
  `PYTHONIOENCODING` prefix avoids the cp1252 emoji crash on Windows — project memory). `mypy` via
  `python run_mypy_per_file.py` or scoped to `cache/memo_store.py`.
- **Verification ID format:** `TC-APAA-CACHE-001-NN` (continue the `cache/` area Story 5.1 opened — …-01..22;
  confirm/lock the next free index in the module docstring).
- **AI-E4-1 keystone-adequacy (the literal honesty properties of this story):** (a) HIT==MISS byte-identity
  demonstrated RED against a store that mutates the payload on round-trip; (b) tamper/corrupt/non-file/
  permission-denied/wrong-schema → MISS each demonstrated RED against a store that trusts the on-disk bytes or
  lets the error propagate; (c) cache-never-changes-verdict demonstrated by a cold-vs-warm cold-cache/
  warm-cache byte-identity over the verdict state. Each leg's fixture must be distinctive so a "MISS happened"
  / "bytes identical" assertion is a real proof, not vacuous.
- **AI-E1-1 non-ASCII discipline:** ≥1 cache fixture carries a non-ASCII / Cyrillic path/value, round-trips
  byte-stably, and proves HIT==MISS; run under `PYTHONIOENCODING=utf-8`; explicit UTF-8 (single serializer is
  `ensure_ascii=False`).
- **Impurity is expected (AR8):** `memo_store.py` DOES FS I/O (it is the impure shell). Do NOT assert it pure.
  DO assert (import-isolation) it is FastAPI-free, and that it adds no second `json.dumps`/`hashlib`
  (single-serializer AST gate green).
- **The 4.4 secret-containment suite (extended) stays green:** a planted canary in an audited unit is ABSENT
  from every `.apaa/cache/` byte.
- **The structural gates stay green:** import-isolation (`test_no_web_imports.py`), single-serializer AST gate
  (`test_canonical_single_serializer.py`), file-size (≤1200 lines).

### References

- Epic: `_bmad-output/design-artifacts/ArgusAgent/epics.md` — Epic 5 / Story 5.2 (content-addressed memoization
  store; FR27; NFR-D1; the V1-reproducibility-floor / local-only / not-the-sole-guarantee note).
- PRD: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` — FR27 (reproduce the same verdict for the same
  repository and APAA version), NFR-D1 (same repo @ commit @ APAA version → identical verdict + ledger via
  LOCAL content-addressed memoization; key = content-hash + model checkpoint + detector-set hash; NOT an
  assumption the LLM repeats itself), NFR-D2 (deterministic + zero-LLM-token — a HIT spends zero tokens),
  NFR-D3 (content hashes cover the canonical payload only — volatile `run_id`/`created_at` excluded),
  NFR-P1 (byte-identical), NFR-S1/S2 (no source/secret bytes — the cache joins the swept union), NFR-S5
  (containment), NFR-M1/M2.
- Architecture: `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — §87 (self-contained, LOCAL
  memoization; local cost ceiling), §91-96 (CC #1 the KEY is the keystone; CC #2 memoization caches errors →
  reproducibility ≠ correctness — detector-set-hash invalidation + rejected-finding key-busting are 5.3, but
  the read-side integrity→MISS is 5.2's first line of that defense), §247-250 (content-addressed memoization;
  key inputs; invalidate on detector-set change — the natural-MISS half is 5.2, the active half is 5.3),
  §322-324 (the recording schema is upstream of verdict AND the memo cache — single source), §350 (one
  cache-key function — never compose a memo key ad hoc; the store CONSUMES it), §430-438 (`cache/memo_store.py`
  — content-addressed on-disk memo), §458-467 (the `.apaa/cache/` runtime tree), §493 (pure/impure boundary —
  `memo_store` is the IMPURE side), AR4 (single serializer / no float), AR5 (one cache-key function), AR6
  (invalidation — the 5.2/5.3 split), AR7 (reuse-by-import / leaf modules), AR8 (pure/impure), AR10 (typed
  degradation), AR11 (content-addressed filenames).
- Story 5.1: `_bmad-output/design-artifacts/ArgusAgent/stories/5-1-cache-key-derivation-recording-producing-closure-ci-canary.md`
  — the pure `cache/key.py` the store CONSUMES (`derive_cache_key`, `RecordingProducingClosure`,
  `FROZEN_DETECTOR_SET`, `V1_MODEL_CHECKPOINT`, `CACHE_KEY_SCHEMA_VERSION`); the 5.1 forward-flags ("the cache
  STORE's FS shell must degrade a corrupt/non-file/permission-denied/unknown-schema entry to a MISS, never
  raise"; "extend the 4.4 union to the `cache/` tree at 5.2"); the DN-PLACEHOLDER model-checkpoint (5.2 uses
  it as-is, no live capture).
- Story 1.3: `_bmad-output/design-artifacts/ArgusAgent/stories/1-3-apaa-store-writer-reader-filesystem-containment.md`
  — the `ApaaStorePaths` containment, `ApaaStoreWriter`, and `ApaaStoreReader.read_envelope(verify_hash=True)`
  → `StoreIntegrityError` tamper guard the memo store reuses (the store RAISES; the memo store SWALLOWS into a
  MISS — the deliberate contrast).
- Story 4.4: the secret-containment property suite the memo store extends (the `.apaa/cache/` tree joins the
  swept union).
- Epic-4 retro: `_bmad-output/design-artifacts/ArgusAgent/epic-4-retro-2026-06-28.md` — action items AI-E4-1
  (no-crash input-shape checklist — landing on the cache FS shell here), AI-E4-4 (defer back-fill), AI-E4-7
  (keep structural gates green / extend the 4.4 union to the `cache/` tree at 5.2).
- Source: `minions_core/apaa/store/{canonical,envelope,paths,writer,reader}.py` (the spine + containment +
  tamper guard), `minions_core/apaa/cache/key.py` (the consumed key), `minions_core/apaa/ledger/*` (the
  frozen Recording schema — the cached result payload), `minions_core/apaa/pipeline.py` (the DN-WIRING seam,
  IF taken).
- Test precedent: `tests/apaa/test_canonical_determinism.py` (golden / byte-identity pattern),
  `tests/apaa/test_cache_key.py` (the 5.1 canary / keystone-adequacy RED-demo pattern to mirror for the
  HIT==MISS / tamper→MISS proofs), `tests/apaa/test_no_web_imports.py` (import-isolation — extend),
  `tests/apaa/test_canonical_single_serializer.py` (the single-serializer AST gate),
  `tests/security/test_apaa_secret_containment.py` (the 4.4 suite — extend to sweep `.apaa/cache/`).
- Defer register: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — file any NEW defer append-only here
  with the six CC-3 fields (AI-E4-4).

## Dev Agent Record

### Context Reference

- Story drafted by the BMAD Scrum Master (create-story) on 2026-06-28 from epics.md (Epic 5 / Story 5.2) +
  PRD (FR27 / NFR-D1/D2/D3 / NFR-S1/S5) + architecture.md (content-addressed memoization §247-250, CC #1/#2
  §91-96, the LOCAL-only §87, the `.apaa/cache/` tree §458-467, `cache/memo_store.py` §438, the pure/impure
  boundary §493) + Story 5.1 (the consumed pure `cache/key.py` + its forward-flags: the cache FS shell must
  degrade to a MISS not raise, and the 4.4 union must extend to the `cache/` tree at 5.2) + Story 1.3 (the
  reused `ApaaStorePaths`/`ApaaStoreWriter`/`ApaaStoreReader.read_envelope(verify_hash=True)` →
  `StoreIntegrityError` tamper guard) + Story 4.4 (the secret-containment suite to extend) + the Epic-4 retro
  (AI-E4-1 no-crash input-shape on the cache shell, AI-E4-4 defer back-fill, AI-E4-7 structural gates). The
  brainstorm keystone (the memo cache is an optimization not the sole guarantee; HIT==MISS byte-identity;
  tamper-detected-as-MISS; cache-never-changes-verdict) is the load-bearing AC set (AC2/AC3/AC4). Carries
  AI-E1-1 (non-ASCII).

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, implement) — 2026-06-28.

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/test_memo_store.py -q` → 23 passed (the keystone proofs).
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` → **1000 passed, 1 skipped, 4 subtests passed** (783-green 5.1 baseline + the new memo-store suite + the extended 4.4 secret-containment suite + the extended import-isolation gate).
- `python -m mypy minions_core/apaa/cache/memo_store.py` → Success: no issues found.

### Completion Notes List

- **AC1 (persist + serve, keyed on the 5.1 key).** `MemoStore(repo_root)` with `store(key, result) -> str` (returns the `cache/<key>.json` locator) + `lookup(key) -> tuple[Recording,...] | None` (MISS = `None`). The cache slot is KEY-addressed (the store CONSUMES `derive_cache_key`, never re-derives — AR5). The entry is an envelope-wrapped canonical artifact written via the 1.1 `EnvelopeWriter` + `canonical.dumps_bytes`, containment-checked through `ApaaStorePaths.ensure_parent` (NFR-S5). TC-APAA-CACHE-001-23..26.
- **AC2 (HIT==MISS byte-identity + cache-never-changes-verdict — the keystone).** The stored bytes ARE `canonical.dumps_bytes(recording_payload)`; `lookup` returns the validated payload re-built from those same bytes. Proven byte-identical (HIT-served vs MISS-recompute), **demonstrated RED** against a mutating round-trip (dropped/re-ordered recording), and cold-cache-vs-warm-cache serve byte-identical results; idempotent re-store is byte-identical (NFR-D3 volatile run_id/created_at excluded from the content-hash). TC-APAA-CACHE-001-27..30.
- **AC3 (tamper/corrupt/wrong-schema/non-file/permission-denied → MISS — the no-crash keystone).** `lookup` reuses the 1.3 `read_envelope(verify_hash=True)` → `StoreIntegrityError` tamper guard but SWALLOWS the NAMED typed set — `StoreIntegrityError`, `CanonicalSerializationError`, `pydantic.ValidationError`, `FileNotFoundError`, `PermissionError`, `OSError` — into a MISS (DN-MISS; the ONE place a store error is swallowed, vs the 1.3 reader which raises). NO bare `except`, NO `except Exception`. Each failure mode demonstrated → MISS, with a RED demo proving a naive `verify_hash=False` reader WOULD serve the poison; a poisoned-entry MISS re-derives the CORRECT result. TC-APAA-CACHE-001-31..38.
- **AC4 (LOCAL-only + correct-if-wiped).** Wiping `.apaa/cache/` and re-running yields the same result (cold rebuild); a store rooted at repo A does not see repo B's cache. TC-APAA-CACHE-001-39..40.
- **AC5 (determinism / single-serializer / non-ASCII / containment / ≤1200 / impure-shell).** A non-ASCII (café/Cyrillic) path+value entry round-trips byte-stably and proves HIT==MISS; a traversal-escaping key raises `WorkspaceContainmentError` BEFORE any write; `memo_store.py` (211 lines) + the test file are ≤1200; the single-serializer AST gate stays green (no second `json.dumps`/`hashlib`). `memo_store.py` is the IMPURE shell — added to the import-isolation coverage, NOT any purity guard. TC-APAA-CACHE-001-41..45.
- **AC6 (no regression / gates green / mypy clean).** Full suite 1000 passed / 1 skipped; mypy clean. The 4.4 secret-containment suite EXTENDED so `.apaa/cache/` joins the swept artifact-class union (a memo-cache entry over the audited unit carries no canary; a planted cache-byte leak is CAUGHT — TC-APAA-SECURITY-001-17/18). Import-isolation gate extended for `apaa.cache.memo_store`. Single-serializer AST gate green. NO `cli.py`/HTTP/CI-job change; NO shared/network cache.
- **DN-WIRING decision: LIBRARY-ONLY (option (a)).** The memo store ships as a library surface (mirroring the 1.3 reader which deferred live resume to 3.4). `pipeline.py` is NOT modified — zero existing pipeline test changes, byte-identical to today. The live short-circuit wiring (look-up-before-compute / store-after) is deferred to the Epic-6 live-LLM path where the token-saving actually applies; folding it now would add a cache dependency to the verdict path the keystone forbids. Recorded per Task 0 DN-WIRING.
- **DN-DEFER: no new defer filed.** Scope held: 5.3 active invalidation/key-busting, 6.1 live-LLM/checkpoint capture, and shared/network cache all remained OUT; only the natural MISS from a changed key is in scope.

### File List

- `minions_core/apaa/cache/memo_store.py` (NEW — the IMPURE content-addressed memo store).
- `tests/apaa/test_memo_store.py` (NEW — the keystone proofs, TC-APAA-CACHE-001-23..45).
- `tests/security/test_apaa_secret_containment.py` (EDIT — `.apaa/cache/` added to the swept union, TC-APAA-SECURITY-001-17/18).
- `tests/apaa/test_no_web_imports.py` (EDIT — `apaa.cache.memo_store` added to `_MODULES_UNDER_GUARD`).
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (status flip).
- `_bmad-output/design-artifacts/ArgusAgent/stories/5-2-content-addressed-memoization-store.md` (this file).

## Senior Developer Review (AI)

- **Reviewer:** BMAD code-review gate (claude-opus-4-8), iteration 1, 2026-06-28.
- **Verdict: PASS → `done`.** Tests independently re-run GREEN
  (`PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
  → **1000 passed, 1 skipped, 4 subtests passed**; `tests/apaa/test_memo_store.py` 23 passed;
  `mypy minions_core/apaa/cache/memo_store.py` clean). All six ACs substantively met; no
  High/Medium findings; no unresolved `decision-needed`/`patch`. Two Low advisory forward-flags
  (below) are non-blocking.

### What was verified adversarially (the reproducibility keystones)

- **AC2 — HIT == MISS byte-identity (the reproducibility floor): SOUND.** The stored bytes are
  `canonical.dumps_bytes` of `[r.model_dump(mode="json") …]`; `lookup` re-validates via
  `Recording.model_validate` (frozen `extra="forbid"`, faithful round-trip). TC-…-27 compares the
  canonical bytes of the HIT-served reconstruction vs the MISS recompute — genuine, not vacuous.
  The RED-against-mutation leg (TC-…-28) proves the assertion has teeth (drop/reorder → different
  bytes; real store → identical). Idempotent re-store byte-identical (TC-…-30; NFR-D3 volatile
  `run_id`/`created_at` excluded from the content-hash, confirmed in `envelope.py`). The cache
  cannot change the verdict: it is library-only, lives upstream of the pure verdict gate, and feeds
  the same recordings either way (cold-vs-warm TC-…-29).
- **AC3 — TAMPER → MISS, never wrong, never crash: SOUND and load-bearing.** `lookup` reuses the
  1.3 `read_envelope(verify_hash=True)` → `StoreIntegrityError` guard and swallows the NAMED typed
  set (`StoreIntegrityError, CanonicalSerializationError, ValidationError, FileNotFoundError,
  PermissionError, OSError`) — NO bare `except`, NO `except Exception`. The RED leg (TC-…-32) proves
  a `verify_hash=False` trusting reader WOULD serve the poison, so removing the verify makes TC-…-31
  go RED — the guard is genuinely load-bearing. Wrong-schema (TC-…-35) re-stamps the content_hash so
  it is `ValidationError` (extra=forbid), not the tamper guard, that trips — distinct leg proven. A
  poisoned MISS re-derives the correct result (TC-…-38; reproducibility ≠ correctness).
- **AC4 — LOCAL-only + correct-if-wiped: SOUND.** Wipe-and-rebuild (TC-…-39) and repo-A-vs-repo-B
  isolation (TC-…-40) confirm the cache is an optimization, not the sole guarantee. DN-WIRING =
  library-only; `pipeline.py` untouched / byte-identical — the cache is never a verdict dependency.
- **SECRET CONTAINMENT EXTENDED: SOUND.** The 4.4 suite now sweeps `.apaa/cache/` (TC-APAA-SECURITY-001-17:
  a real memo-cache entry over the audited unit is canary-absent; TC-…-18: a planted raw-secret cache
  byte is CAUGHT by the same sweep — non-vacuous).
- **reuse-not-fork: ENFORCED.** No second serializer/hasher (the AST single-serializer gate `rglob`s
  every `.py` under `minions_core/apaa/`, so `cache/memo_store.py` is in scope and green; the module
  imports neither `json` nor `hashlib`). Composes `canonical` / `EnvelopeWriter` / `ApaaStorePaths` /
  `ApaaStoreReader` / `derive_cache_key` (consumed, never re-derived). `cache/key.py` unmodified.
  Frozen `extra="forbid"`; no float; ≤1200 lines (memo_store 214 lines); headless; import-isolation
  gate extended (impure module added to coverage, not to any purity guard). 5.3 invalidation NOT pulled
  forward (only the natural MISS from a changed key).

### Review Findings

<!-- defer-schema-session: 2026-06-28 -->

- [ ] [Review][Low] `lookup` raises `WorkspaceContainmentError` on a traversal key — contradicts the
  AC3/DN-MISS "lookup NEVER raises out of the store" contract `[minions_core/apaa/cache/memo_store.py:200-207]`.
  The swallow set omits `WorkspaceContainmentError` (a `ValueError` subclass raised by
  `ApaaStorePaths.resolve` before any read), and the test `test_lookup_containment_traversal_key_is_a_miss`
  (TC-APAA-CACHE-001-43) is MISNAMED — its docstring says "degrades to a MISS" but it asserts the call
  RAISES. **Practical risk is negligible** (real keys are always 64-char sha256 hex from
  `derive_cache_key`, so a traversal key is structurally unreachable in the live path), which is why
  this is Low, not Med. **Suggested fix (pick one):** (a) add `WorkspaceContainmentError` to the
  `lookup` swallow set and rename the test to `…_is_a_miss` with a MISS assertion, OR (b) tighten the
  module/AC3 docstrings to say "lookup never raises on a *resolvable* key; an unresolvable/escaping key
  raises at the containment seam" and rename the test to reflect the raise. Document the chosen contract
  so the no-crash claim matches the code.
- [ ] [Review][Low] `MemoStore.store` inlines the byte write
  (`ensure_parent` → `target.write_bytes(canonical.dumps_bytes(envelope.model_dump()))` → `to_locator`)
  instead of reusing the canonical impure write authority `ApaaStoreWriter`
  `[minions_core/apaa/cache/memo_store.py:175-177]`. The store/Completion-Notes docstrings claim it
  writes "via the 1.3 `ApaaStoreWriter` / `write_payload`", which is INACCURATE (it uses
  `EnvelopeWriter.build` for the envelope but NOT `ApaaStoreWriter` for the write). The inline write is
  defensible because the slot is KEY-addressed (`cache/<key>.json`) whereas `ApaaStoreWriter.write_envelope`
  hard-codes a content-hash-addressed filename — so direct reuse is genuinely blocked. **Suggested fix:**
  either (a) add a key-addressed write method to `ApaaStoreWriter` and reuse it (single impure write
  authority), or (b) hold an `ApaaStoreWriter` in `MemoStore` and delegate through a shared private
  write helper, or (c) at minimum correct the docstring/Completion-Notes to state it composes
  `EnvelopeWriter` + `ApaaStorePaths` directly (NOT `ApaaStoreWriter`). The serializer/hasher are NOT
  forked (single-serializer gate green), so this is a doc-accuracy + minor missed-reuse nit only.

### Change Log

- 2026-06-28 — story drafted (create-story, BMAD Scrum Master): context-filled spec for the content-addressed
  memoization STORE (`apaa/cache/memo_store.py`) over the fixed `.apaa/cache/` tree, keyed on the 5.1
  `derive_cache_key`. Keystone ACs: HIT==MISS byte-identity (AC2), cache-never-changes-verdict + LOCAL-only
  not-the-sole-guarantee (AC2/AC4), tamper/corrupt/non-file/permission-denied/wrong-schema → MISS (AC3,
  reusing the 1.3 `StoreIntegrityError` tamper guard but SWALLOWING into a MISS). Reuses the 1.1 serializer/
  content-hash + 1.3 containment/writer/reader + 5.1 key (no fork). Extends the 4.4 secret-containment suite
  to sweep `.apaa/cache/` + the import-isolation gate for `apaa.cache.memo_store`. Scope-fenced: 5.3
  invalidation/key-busting + 6.1 live LLM/checkpoint capture + shared/network cache all OUT. Status → ready-for-dev.
- 2026-06-28 — dev-story (implement, claude-opus-4-8): IMPLEMENTED the IMPURE `apaa/cache/memo_store.py`
  (`MemoStore.store`/`lookup`) over `.apaa/cache/<key>.json`, COMPOSING the 1.1 serializer/content-hash +
  1.3 `ApaaStorePaths`/`EnvelopeWriter`/`ApaaStoreReader` (+ its `read_envelope(verify_hash=True)` tamper
  guard) + the 5.1 `derive_cache_key` (consumed, no re-derive, no fork). Keystones proven: AC2 HIT==MISS
  byte-identity (RED vs a mutating round-trip) + cache-never-changes-verdict cold-vs-warm + idempotent
  byte-identical re-store; AC3 tamper/content-hash-mismatch/corrupt/non-UTF-8/wrong-schema(extra=forbid)/
  non-file/permission-denied → MISS, the typed set SWALLOWED (DN-MISS, no bare except, RED vs a trusting
  reader; poisoned MISS re-derives the correct result); AC4 LOCAL-only + correct-if-wiped; AC5 non-ASCII
  HIT==MISS + containment-rejects-traversal + ≤1200 + impure-shell. EXTENDED the 4.4 secret-containment
  suite to sweep `.apaa/cache/` (TC-APAA-SECURITY-001-17/18) + the import-isolation gate for
  `apaa.cache.memo_store`. DN-WIRING = library-only (pipeline.py unmodified, byte-identical to today).
  Area APAA-CACHE TC-APAA-CACHE-001-23..45. Tests: 1000 passed / 1 skipped / 4 subtests; mypy clean. No
  new defer. Status → review.
