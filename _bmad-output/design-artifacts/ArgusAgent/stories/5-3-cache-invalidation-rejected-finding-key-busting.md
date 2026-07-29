# Story 5.3: Cache invalidation & rejected-finding key-busting

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/APAA/`; the tracker is `_bmad-output/design-artifacts/APAA/sprint-status.yaml`
> (NOT the Minions platform tracker at `_bmad-output/implementation-artifacts/sprint-status.yaml`). All
> CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only, §3.8 12-Factor + secret masking, §3.4
> evidence immutability).
>
> **This is the THIRD and FINAL story of Epic 5** (Reproducible Verdict & Memoization, Tier-B; `epic-5` is
> already `in-progress` from Story 5.1). The Epic-5 retrospective follows this story. It rides on the
> fully-done Epics 1+2+3+4 (≈760 passed at the Epic-4 retro) AND on the now-done Stories 5.1 (the pure
> `apaa/cache/key.py` cache-key derivation over the full recording-producing closure + its CI canary —
> 783 green after the 5.1 fix) and 5.2 (the IMPURE content-addressed memo STORE `apaa/cache/memo_store.py`
> + read-side integrity→MISS — 1000 passed / 1 skipped after 5.2). 5.1 + 5.2 deliberately fenced OUT
> **ACTIVE cache invalidation** and **rejected-finding key-busting** — **THIS story owns the AR6
> invalidation layer.** It adds the deterministic, safe busting/invalidation machinery so reproducibility
> never means "a stable WRONG answer served forever".

## Story

As an **Engineering Lead who rejected a false 🔴** (and as the APAA maintainer who must certify that the
memo cache cannot ossify a wrong answer),
I want **a deterministic, safe cache-invalidation surface** (`apaa/cache/invalidation.py`) that (a) busts the
cache entries for a **human-rejected finding** so the false 🔴 is not re-served on the next run, and (b)
invalidates the affected cache entries when the **enabled detector set changes** (the detector-set
content-hash moves),
so that **reproducibility ≠ correctness** is enforced at the cache layer: a re-run after a rejection (or a
detector edit) RE-COMPUTES the affected unit instead of serving the stale recorded result — while
invalidation is **idempotent, containment-safe, and can never corrupt the store or leak a byte**, and an
**over-bust is always safe** (it just forces a harmless recompute) but an **under-bust (re-serving a stale
rejected finding) is the failure this story exists to prevent**.

## Story Context

This is **Story 3 of Epic 5** (Reproducible Verdict & Memoization, Tier-B — the "a number you can put on a
dashboard and trust not to flake" layer, PRD Journey 3). `epic-5` is already `in-progress` (flipped by
Story 5.1). It is the **cache-invalidation / rejected-finding key-busting** story — the second half of
architecture **AR6** ("Memoization caches errors → reproducibility ≠ correctness: cache entries invalidate
on detector-set-hash change, and a human-rejected finding busts its own cache key — else a false 🔴 is
served forever").

**What this story delivers and what it explicitly does NOT.** This story delivers the deterministic
invalidation surface that turns a cache entry from "served forever" into "busted on the next run after a
rejection or detector change". It has two levers, one of which is fully available today and one of which
needs only a V1 seam:

1. **Detector-set-change invalidation — FULLY AVAILABLE NOW.** The 5.1 `derive_cache_key` ALREADY folds the
   detector-set content-hash (`detector_set_content_hash(FROZEN_DETECTOR_SET)`) into the key, so a
   detector-set edit ALREADY produces a different key → a different cache slot → a NATURAL MISS (the unit is
   re-computed, the stale entry is never read). 5.2 documented that natural miss as in-scope. **THIS story
   adds the ACTIVE half AR6 names:** an explicit `invalidate_on_detector_set_change(...)` that DELETES the
   now-orphaned cache entries keyed under the OLD detector-set hash (so the cache tree does not accumulate
   dead, never-again-reachable slots), AND proves the correctness property — that after a detector-set
   change the affected unit is re-computed (correct), not served (stale).
2. **Rejected-finding key-busting — V1 SEAM (the rejection TRIGGER is Epic-6).** A human-rejected finding
   must bust the cache key under which that finding was served, so the false 🔴 is re-computed (and, once the
   detector/config that produced the false 🔴 is corrected, no longer emitted) rather than re-served. The
   **live rejection SOURCE** — the Prosecutor (Story 6.4) and the HITL STOP/PROCEED escalation +
   append-only decision record (Story 6.7) — is **Epic-6 and is OUT of this story's scope.** This story
   builds the **busting MECHANISM + a V1 rejection-record seam** (a frozen `RejectedFinding` record + a
   `RejectionLedger` that an Epic-6 Prosecutor/HITL caller will populate), and proves that GIVEN a rejection
   record, the corresponding cache entry is busted and the false 🔴 is not re-served. **Do NOT build
   6.4/6.7.**

Keeping 5.3 to the invalidation-mechanism + V1-rejection-seam scope is the thin-slice discipline that held
across Epics 1-4 and Stories 5.1+5.2 (each story folds ONE working capability over the determinism spine).

**The determinism spine + the 5.1 key + the 5.2 store are DONE and proven.** The single canonical serializer
(`apaa/store/canonical.py::dumps_bytes` / `loads`), the content-hashed envelope
(`apaa/store/envelope.py::compute_content_hash` + `EnvelopeWriter.build` + `GENESIS_PREV_HASH`),
`Fraction`-not-`float`, the `.apaa/` containment resolver (`apaa/store/paths.py::ApaaStorePaths` —
`resolve`/`ensure_tree`/`ensure_parent`/`to_locator`, with `cache/` in `APAA_SUBDIRS`), the impure writer
(`apaa/store/writer.py::ApaaStoreWriter`), the PURE-deserialize reader with its tamper guard
(`apaa/store/reader.py::ApaaStoreReader.read_envelope(..., verify_hash=True)` → `StoreIntegrityError`), the
pure cache key (`apaa/cache/key.py::RecordingProducingClosure` + `derive_cache_key` +
`detector_set_content_hash` + `FROZEN_DETECTOR_SET` + `DetectorDescriptor` + `V1_MODEL_CHECKPOINT` +
`V1_PROMPT_TEMPLATE_VERSION` + `CACHE_KEY_SCHEMA_VERSION` + `CacheKeyError`), and the impure memo STORE
(`apaa/cache/memo_store.py::MemoStore` — `store(key, result) -> str` / `lookup(key) -> RecordedResult | None`,
`RecordedResult = tuple[Recording, ...]`, the `cache/<key>.json` key-addressed slot, the DN-MISS swallow
taxonomy) all shipped in Epics 1-3 + Stories 5.1+5.2 and were proven byte-identical / order-independent.
**The invalidation surface COMPOSES these — it is an impure shell that DELETES (busts) cache entries and
reads the rejection seam; it does NOT fork the serializer, the hasher, the containment resolver, the key, or
the store.**

**The keystone — the over-bust-safe / under-bust-forbidden asymmetry (the architecture AR6 / brainstorm CC #2).**
Invalidation is the safety valve on the memoization optimization. The load-bearing properties this story
must prove SHARPLY (the AI-E4-1 keystone-adequacy carry-forward, now landing on the cache-DELETE surface):

1. **Under-bust is the failure to PREVENT.** After a finding is rejected (or the detector set changes), the
   affected cache entry MUST NOT be re-served. A re-run MUST re-compute the affected unit. Serving the stale
   rejected finding is the exact failure mode AR6 names ("else a false 🔴 is served forever"). The keystone
   test is RED-then-green: a NAIVE cache that does NOT bust would re-serve the false 🔴; the busting surface
   forces a recompute.
2. **Over-bust is SAFE (the correctness asymmetry).** Invalidating TOO MUCH — busting an entry that did not
   strictly need busting, or busting under a broader scope than the minimal one — is harmless: the next run
   re-computes the unit and stores it again, producing a byte-identical-to-recompute result (the 5.2
   HIT==MISS property guarantees a recompute is correct). So when in doubt, bust. The invalidation surface
   prefers safe over-busting to risky under-busting, and this asymmetry is documented + tested (a broader
   bust still yields the correct verdict).
3. **Invalidation is deterministic, idempotent, containment-safe, and leak-free.** Busting a key that is
   already absent is a no-op (idempotent). A bust path is containment-checked via `ApaaStorePaths` (a
   traversal/symlink/sibling-prefix key cannot delete outside `.apaa/cache/` — NFR-S5). Invalidation NEVER
   corrupts the store: it deletes a whole cache slot atomically-enough (a delete, never a partial rewrite),
   leaving every OTHER cache entry untouched and the surrounding `.apaa/` tree intact. No source/secret byte
   is read, logged, or emitted by the invalidation path (NFR-S1) — it operates on KEYS and slot files, not
   payloads (when it must read the rejection seam, it reads only the redacted `RejectedFinding` record, never
   source). A bust NEVER raises out of the surface on a benign condition (missing slot, already-busted) and
   degrades a corrupt rejection-record read to a typed finding / safe skip, never an uncaught crash (AR10).

**The 5.1 → 5.2 → 5.3 boundary (the load-bearing scope fence, restated and CLOSED by this story).** 5.1 = the
PURE key (a faithful fingerprint of the producing closure). 5.2 = the STORE that persists/serves a recorded
result under that key, with read-side integrity → MISS. 5.3 (THIS story) = ACTIVE INVALIDATION: (a) a
detector-set-hash change deletes the now-orphaned OLD-hash entries (the active half of the 5.2 natural-MISS),
and (b) a human-rejected finding busts its own cache key so the false 🔴 is re-computed not re-served (AR6).
**5.3 does NOT build the live Prosecutor (6.4) or the live HITL STOP/PROCEED + decision record (6.7) — it
builds a V1 `RejectedFinding` record + `RejectionLedger` SEAM that those Epic-6 callers will populate.** This
CLOSES the 5.x cache layer; the live-LLM dispatch + real checkpoint capture (6.1) and the live rejection
TRIGGER (6.4/6.7) remain Epic-6.

**Why this story is safe to build now even though the live rejection trigger is Epic-6.** The detector-set
half is fully live (the key already folds the detector-set hash). The rejected-finding half is a deterministic
MECHANISM (given a rejection record, bust the key) plus a frozen record/ledger SEAM — it needs no LLM, no
Prosecutor, no HITL gate. An Epic-6 Prosecutor/HITL story (6.4 / 6.7) substitutes the live trigger into the
seam additively (it APPENDS a `RejectedFinding` to the `RejectionLedger`; the 5.3 busting surface consumes it
unchanged). This mirrors the 5.1 `V1_MODEL_CHECKPOINT` / `V1_PROMPT_TEMPLATE_VERSION` placeholder discipline:
ship the deterministic slot/seam now, substitute the live source at 6.1/6.4/6.7.

**Carry-forward from the Epic-4 retro (2026-06-28) + the 5.1/5.2 forward-flags + the standing disciplines
(CLAUDE.md §9.1 / L1-E11).** Each item below is an Epic-5-backlog action item this story discharges (per the
L1-E11 operating model: package the prior retro's action items as the next epic's backlog).
- **AI-E4-1 (test-infra 🟠) — the NO-CRASH-KEYSTONE INPUT-SHAPE CHECKLIST, now landing on the cache-DELETE
  surface.** The 5.1/5.2 stories flagged forward that the cache's filesystem-touching impure shell is the
  surface that produced the 4.2 FAIL class. 5.2 covered the READ path (corrupt/non-file/permission-denied →
  MISS). THIS story covers the DELETE/bust path + the rejection-seam READ path: busting a missing/already-gone
  slot is a no-op (never a crash); a permission-denied / OS error on a delete degrades to a typed result, never
  an uncaught raise; a corrupt / wrong-schema `RejectedFinding` record read degrades to a typed finding /
  safe skip, never a crash (AR10). EACH demonstrated RED-then-green with a distinctive fixture.
- **AI-E4-7 (process 🟢) — keep the three structural gates green + the L1-E11 loop.** `invalidation.py` (and
  the rejection-seam module if separate) is the IMPURE shell (it DOES FS I/O — DELETE + a redacted-record
  read); do NOT add it to a PURITY-asserting guard set (mirror how `store/writer.py` / `store/reader.py` /
  `cache/memo_store.py` are treated). It MUST NOT break the import-isolation gate
  (`tests/apaa/test_no_web_imports.py` — extend the coverage so the new module(s) are asserted FastAPI-free)
  or the single-serializer AST gate (`tests/apaa/test_canonical_single_serializer.py` — the invalidation
  surface REUSES `canonical` / the 1.3 reader / the 5.1 key / the 5.2 store; it adds NO second `json.dumps`
  and NO second `hashlib`). File-size ≤1200 lines.
- **AI-E4-7 (4.4 union extension — the 5.1/5.2 forward-flag continued).** 5.2 extended the 4.4
  secret-containment suite to sweep the `.apaa/cache/` tree. THIS story writes a NEW `.apaa/` artifact class
  (the `RejectedFinding` record / `RejectionLedger` under `decisions/` or `cache/`), so the 4.4
  secret-containment property suite (`tests/security/test_apaa_secret_containment.py`) MUST be extended so any
  new rejection-record artifact class is included in the swept artifact-class union (a planted canary secret
  in an audited unit must be ABSENT from any rejection-record byte too — the record cites a finding by
  `recording_id` + redacted metadata, never source/secret bytes).
- **AI-E1-1 (test-infra 🟢) — non-ASCII / locale discipline (the Epic-1-FAIL class, standing).** A cache key /
  rejection record whose closure includes a non-ASCII file path / non-ASCII content must bust byte-stably
  (explicit UTF-8; the single serializer is `ensure_ascii=False`). Run the suite under
  `PYTHONIOENCODING=utf-8` (project memory — the cp1252 emoji crash). At least one bust fixture carries a
  non-ASCII path/value.
- **AI-E4-4 (governance 🟢) — central defer register.** If this story files a NEW defer, file it append-only
  in `_bmad-output/design-artifacts/APAA/deferred-work.md` (the single canonical APAA defer source), not only
  in the story file, with the six CC-3 fields.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 5.3) + the architecture / PRD. Drivers: **APAA-FR-27**
> (APAA can reproduce the same verdict for the same repository and APAA version — invalidation is what keeps
> the reproduction from ossifying a WRONG answer), **APAA-NFR-D1** (same repo @ same commit @ same APAA
> version → identical verdict + ledger via local content-addressed memoization that invalidates on a
> detector-set change and busts a rejected finding's key — the CENTRAL driver, AR6 half), **APAA-NFR-D2**
> (verdict gate + ledger mechanics deterministic + zero LLM tokens — the bust/invalidation path is itself
> token-free), **APAA-NFR-D3** (content hashes cover the canonical payload only — the rejection record's hash
> excludes volatile `run_id`/`created_at`), **APAA-NFR-P1** (byte-identical on-disk state; a recompute after a
> bust round-trips byte-identically to a cold compute), **APAA-AR4** (single serializer, no float / clock /
> uuid / random in any new record payload), **APAA-AR5** (ONE cache-key function — the invalidation surface
> CONSUMES `derive_cache_key` / `detector_set_content_hash`; it does not re-derive a key), **APAA-AR6** (the
> CENTRAL driver — memoization caches errors → reproducibility ≠ correctness: invalidate on detector-set
> change + a human-rejected finding busts its own key), **APAA-AR7/AR10** (reuse the 1.3 containment shell +
> the 5.2 store + typed errors; a missing/already-gone slot bust is a no-op, a permission-denied delete / a
> corrupt rejection record degrades to a typed result, never an uncaught raise / a silently-wrong served
> result), **APAA-AR8** (`invalidation.py` is the IMPURE shell — FS DELETE / redacted-record read confined
> here; any new record payload stays pure/clock-free), **APAA-NFR-S1/S5** (no source/secret bytes in the
> rejection record — it joins the 4.4 swept union; containment-checked bust/delete paths), **APAA-NFR-M1**
> (≤1200-line files).
>
> **SCOPE FENCE — Tier-B, single-purpose, THIRD + FINAL Epic-5 story.** This story delivers ONLY: (1) the
> IMPURE cache-invalidation surface `apaa/cache/invalidation.py` that BUSTS cache entries — a
> `bust_key(key)` / `bust_rejected_finding(...)` / `invalidate_on_detector_set_change(old_hash, new_hash, ...)`
> surface (or equivalent), each containment-checked + idempotent + deterministic + leak-free; (2) a frozen V1
> rejection SEAM — a `RejectedFinding` record (cites a finding by `recording_id` + the cache `key` it was
> served under + redacted metadata, NO source bytes) + a `RejectionLedger` (append-only read/persist surface
> an Epic-6 Prosecutor/HITL caller populates); (3) the keystone proofs (under-bust-forbidden RED-then-green;
> over-bust-safe; idempotent; containment-safe; detector-set-change → re-compute-not-re-serve; rejected-finding
> → re-compute-not-re-serve); (4) the 4.4 secret-containment-suite extension so any new rejection-record
> artifact class is in the swept union; (5) the import-isolation-gate extension for the new module(s). It does
> NOT build, and MUST NOT pull forward: the **live Prosecutor pass** (Epic-6 Story 6.4) or the **live HITL
> STOP/PROCEED gate + append-only decision RECORD writer** (Epic-6 Story 6.7) — 5.3 builds only the V1
> rejection-record SEAM those callers populate; the **live LLM dispatch port + real API-response
> model-checkpoint capture** (Epic-6 Story 6.1 — use the 5.1 V1 placeholder as-is); a **shared / cross-machine
> G4 cache** (V4 — V1 is LOCAL-only); a **new HTTP route / FastAPI surface / UI** (§3.7); a **`cli.py`
> subcommand** (a cache-invalidation CLI flag is out of scope — library-only OR a thin default-equivalent
> pipeline seam per DN-WIRING); a **new `.github/workflows` CI job** (the tests are normal `tests/apaa/` +
> `tests/security/` tests collected by the existing jobs). Build the impure invalidation surface + the V1
> rejection seam + the keystone proofs + the suite/gate extensions, then stop.

**AC1 — A human-rejected finding busts its own cache key so a false 🔴 is re-computed, never re-served (AR6 / FR27 / NFR-D1 — the central driver)**
**Given** a cache entry stored under key `K` (via the 5.2 `MemoStore.store(K, result)`) whose `result`
contains a finding `F` (a `Recording` with `recording_id = R`), and a V1 `RejectedFinding` record (in the
`RejectionLedger`) that rejects `R` and records the cache `key` `K` it was served under
**When** the invalidation surface processes the rejection (`bust_rejected_finding(record, store)` or
`invalidate(...)` over the rejection ledger)
**Then** the cache entry under `K` is BUSTED (deleted from `.apaa/cache/`) so a subsequent `MemoStore.lookup(K)`
returns a MISS, forcing a RE-COMPUTE of that unit — the false 🔴 is NOT re-served (AR6 "else a false 🔴 is
served forever")
**And** the bust spends ZERO LLM tokens (NFR-D2), is containment-checked via `ApaaStorePaths` (NFR-S5), and
the rejection record carries NO source/secret bytes (it cites `recording_id` + `key` + redacted metadata —
NFR-S1)
**And** the under-bust case is demonstrated RED: a NAIVE path that does NOT bust would re-serve the stale 🔴
on the next `lookup(K)` (the keystone-adequacy proof that the bust is load-bearing).

**AC2 — A detector-set change invalidates the affected cache entries (AR6 / NFR-D1)**
**Given** cache entries stored under keys derived from the OLD detector-set content-hash
(`detector_set_content_hash(OLD_SET)`)
**When** the enabled detector set changes (a `DetectorDescriptor` added/removed, or a `code_identity`/`config`
edited) so `detector_set_content_hash(NEW_SET) != detector_set_content_hash(OLD_SET)`
**Then** (the NATURAL half, already true from 5.1) the new run derives a DIFFERENT key → a different cache
slot → a NATURAL MISS, so the stale OLD-hash entry is NEVER read on the new run; **AND** (the ACTIVE half THIS
story adds) `invalidate_on_detector_set_change(old_hash, new_hash, store)` DELETES the now-orphaned OLD-hash
cache entries so the cache tree does not accumulate dead, never-again-reachable slots
**And** the correctness property holds: after a detector-set change the affected unit is RE-COMPUTED under the
new key (correct), not served from the old slot (stale) — demonstrated over a synthetic two-detector-set
fixture, RED against a path that re-keyed but left the old slot reachable.

**AC3 — Over-bust is SAFE; under-bust is the forbidden failure (the keystone correctness asymmetry — AR6)**
**Given** an invalidation that busts MORE than the strict minimum (e.g. busts a unit's entry that was only
partially affected, or busts under a broader scope)
**When** the affected unit is re-audited with the busted (cold) cache
**Then** the recompute produces a verdict + ledger BYTE-IDENTICAL to a cold compute (the 5.2 HIT==MISS
property guarantees a recompute is correct), so the over-bust is HARMLESS — it only costs a recompute
**And** the inverse is the forbidden case: an UNDER-bust (failing to bust an entry that needed busting →
re-serving a stale rejected finding) is the failure this story prevents, demonstrated RED (a naive surface
that under-busts re-serves the stale 🔴; the 5.3 surface, when uncertain, prefers the safe over-bust)
**And** this asymmetry is documented in the module docstring + Dev Notes (when in doubt, bust — a stale serve
is never acceptable, an extra recompute always is).

**AC4 — Invalidation is deterministic, idempotent, containment-safe, leak-free, and never corrupts the store (AR4/AR8/AR10/NFR-S1/NFR-S5/NFR-P1)**
**Given** the new `apaa/cache/invalidation.py` (+ the V1 rejection-seam record/ledger) (+ its tests)
**When** the suite runs under `PYTHONIOENCODING=utf-8`
**Then** busting a key that is already absent (already-busted / never-stored) is a NO-OP (idempotent — a
second bust changes nothing, never raises); a bust is containment-checked via `ApaaStorePaths` (a
traversal/symlink/sibling-prefix key cannot delete outside `.apaa/cache/` — `WorkspaceContainmentError` BEFORE
any delete, NFR-S5); a bust DELETES a whole cache slot file (never a partial rewrite) leaving EVERY OTHER
cache entry + the surrounding `.apaa/` tree intact (no corruption — verified by asserting sibling entries
survive a bust); the rejection-record payload carries no float / no `uuid4` / no wall-clock / no `random`
(AR4 — its envelope's volatile `run_id`/`created_at` excluded from the content-hash per NFR-D3); a
permission-denied / OS error on a delete degrades to a typed result (a `BustOutcome` / typed finding), never
an uncaught raise (AR10); a corrupt / wrong-schema / non-UTF-8 `RejectedFinding` record read degrades to a
typed finding / safe skip, never a crash (AR10 — the DN-MISS no-crash discipline applied to the rejection
seam); a bust key / rejection record carrying a non-ASCII / Cyrillic path round-trips byte-stably (AI-E1-1)
**And** `invalidation.py` is the IMPURE shell (FS DELETE / redacted-record read confined here, mirroring
`store/writer.py` / `cache/memo_store.py`) — it is NOT a pure module and must NOT be asserted pure; the pure
5.1 `cache/key.py` and the 5.2 `cache/memo_store.py` are NOT modified beyond an additive, byte-identical-to-
today helper if strictly required (the surface CONSUMES `derive_cache_key` / `detector_set_content_hash` /
`MemoStore` — AR5/AR7).

**AC5 — The cache stays correct WHETHER OR NOT invalidation has run; the verdict is stable AND correct (NFR-D1 — the reproducibility floor + AR6)**
**Given** a clean repo audited repeatedly (the flaky-vs-stable comparison from the epic)
**When** it is audited again after a rejection / detector-set change has busted the relevant entries, AND when
audited with `.apaa/cache/` wiped entirely
**Then** the verdict is STABLE (reproducible across runs — FR27/NFR-D1) AND CORRECT (not merely stable: the
busted/recomputed result reflects the rejection / detector change, and a wiped-cache cold rebuild produces the
SAME verdict) — proving invalidation makes reproducibility safe (a poisoned/rejected/stale entry can never be
ossified into a served hit) rather than turning reproducibility into "a stable wrong answer"
**And** the cache + invalidation surface is LOCAL-only (no shared / cross-machine / network cache — the G4
shared cache is V4 and is NEVER the sole guarantee) and is an OPTIMIZATION layered on an independently-correct
recompute path (wipe + re-run → same verdict).

**AC6 — No regression / no scope creep; the structural + security gates stay green; mypy clean (AR8, AI-E4-7, the thin-slice discipline)**
**Given** the new impure invalidation surface + the V1 rejection seam + its tests + the suite/gate extensions
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the 1000-green Story-5.2 baseline + the new `tests/apaa/test_cache_invalidation.py` + the extended
4.4 secret-containment suite), the import-isolation gate (`test_no_web_imports.py` — extended to assert the
new module(s) are FastAPI-free), the single-serializer AST gate (`test_canonical_single_serializer.py` — the
invalidation surface adds NO second `json.dumps` / `hashlib`), the 4.4 secret-containment property suite
(extended to sweep any new rejection-record artifact class), and the file-size gate (≤1200 lines) stay green;
`mypy` is clean on `cache/invalidation.py` (+ any sibling)
**And** the frozen Epic-1..4 + Story-5.1 + Story-5.2 contracts show NO behavioral diff (`store/{canonical,
envelope,paths,writer,reader}.py`, `cache/key.py`, `cache/memo_store.py`, `models.py`, `ledger/*`,
`verdict/*`, `detectors/*`, `pipeline.py` — the invalidation surface COMPOSES them; the ONLY permitted edit to
a pre-existing surface is the thin, additive, opt-in, byte-identical-to-today invalidation WIRING in
`pipeline.py` per DN-WIRING, IF taken — and if taken it must be default-equivalent so every existing pipeline
test passes byte-identically). NO `cli.py` subcommand, NO HTTP route, NO new CI job, NO shared/network cache
(LOCAL-only), NO live Prosecutor/HITL trigger (6.4/6.7), NO live LLM/checkpoint capture (6.1)
**And** the new test file cites its `APAA-FR-27`/`APAA-NFR-D1`/`AR5`/`AR6` drivers in the module docstring +
the locked test area / index; the mandatory artifacts EXIST + pass + the keystone proofs
(under-bust-forbidden RED-then-green; over-bust-safe; idempotent; containment-safe; detector-set-change →
re-compute-not-re-serve; rejected-finding → re-compute-not-re-serve; stable-AND-correct) are documented
BEFORE the story flips to `status: review` (AI-E4-3 / AI-E2-1 test-existence discipline). **Test area
`APAA-CACHE`** (`TC-APAA-CACHE-001-46..NN` — continue the area Stories 5.1+5.2 opened; 5.2 ended at …-45, so
the next free index is **…-46**; confirm/lock it in the module docstring).

## Tasks / Subtasks

- [x] **Task 0 — Re-read + LOCK the reused surfaces; LOCK the invalidation surface shape, the V1 rejection-seam schema, and the bust→MISS / over-bust-safe contract** (AC: 1, 2, 3, 4)
  - [x] Re-read `cache/key.py` (`derive_cache_key`, `detector_set_content_hash`, `FROZEN_DETECTOR_SET`,
        `DetectorDescriptor`, `RecordingProducingClosure`, `CacheKeyError`). LOCK: the invalidation surface
        CONSUMES `derive_cache_key` / `detector_set_content_hash`; it does NOT re-derive a key (AR5). 5.1
        `cache/key.py` is NOT modified.
  - [x] Re-read `cache/memo_store.py` (`MemoStore.store(key, result) -> str`, `MemoStore.lookup(key) ->
        RecordedResult | None`, `RecordedResult = tuple[Recording, ...]`, `_relative_for(key) ->
        "cache/<key>.json"`, the `_paths`/`_reader` composition, the DN-MISS swallow set). LOCK: the
        invalidation surface uses the SAME `cache/<key>.json` slot convention; it busts a slot by DELETING the
        file (containment-checked), and proves the bust by `MemoStore.lookup(key)` then returning a MISS. 5.2
        `cache/memo_store.py` is NOT modified beyond an additive byte-identical helper if STRICTLY required
        (prefer a new module that composes the store).
  - [x] Re-read `store/paths.py::ApaaStorePaths` (`resolve`/`ensure_parent`/`to_locator`; `cache/` in
        `APAA_SUBDIRS`) + `store/reader.py::ApaaStoreReader` (`read_envelope(verify_hash=True)` →
        `StoreIntegrityError`; `CanonicalSerializationError`). LOCK: the bust DELETE path resolves +
        containment-checks via `ApaaStorePaths` (NFR-S5) — never `str.startswith`; the rejection-seam READ
        reuses the 1.3 reader + tamper guard.
  - [x] Re-read the frozen `Recording`/`Locator` schema (`ledger/recording.py`) — NOTE there is NO `rejected`
        field on `Recording` (it is frozen + additive-only); a rejection is a SEPARATE record that CITES a
        `recording_id`, NOT a mutation of the Recording (DN-REJECTION-SEAM below). Re-read
        `store/writer.py::ApaaStoreWriter` (`write_payload`) for persisting the rejection record.
  - [x] **LOCK DN-INVALIDATION-SHAPE:** define the surface — a `CacheInvalidator(repo_root | ApaaStorePaths,
        store: MemoStore)` (mirror `MemoStore`/`ApaaStoreReader` construction) with:
        `bust_key(key: str) -> BustOutcome` (delete `cache/<key>.json` containment-checked; idempotent — a
        missing slot is `BustOutcome(busted=False, ...)` not a raise);
        `bust_rejected_finding(record: RejectedFinding) -> BustOutcome` (bust the `record.key`);
        `invalidate_on_detector_set_change(old_hash: str, new_hash: str, *, known_keys | scan) -> tuple[BustOutcome, ...]`
        (delete the orphaned OLD-hash entries). Decide + document a `BustOutcome` (e.g. `busted: bool`,
        `locator: str | None`, `reason: str`) — a typed result, never a bare bool, so a permission-denied
        delete is a recorded outcome not a crash.
  - [x] **LOCK DN-REJECTION-SEAM:** define the V1 frozen rejection record + ledger — `RejectedFinding`
        (`recording_id: str`, the cache `key: str` it was served under, `rule_id`/`cartridge_id` provenance,
        an optional redacted `reason`/`rejected_by` token; `frozen=True, extra="forbid"`, NO source/secret
        bytes, no float/clock/uuid — AR4/NFR-S1) + `RejectionLedger` (append-only read/persist over
        `decisions/` or `cache/`, content-addressed via the 1.1 envelope + 1.3 writer). LOCK: this is the SEAM
        an Epic-6 Prosecutor (6.4) / HITL (6.7) caller POPULATES; 5.3 builds the record/ledger + the busting
        that CONSUMES it, NOT the live trigger. Document the additive-substitution path (6.4/6.7 append
        records; the 5.3 surface consumes them unchanged).
  - [x] **LOCK DN-OVERBUST:** document the over-bust-safe / under-bust-forbidden asymmetry — when uncertain
        whether an entry needs busting, BUST (a stale serve is never acceptable; an extra recompute always is —
        the 5.2 HIT==MISS guarantees a recompute is correct). The surface prefers safe over-busting.
  - [x] **LOCK DN-MISS (rejection-seam read):** a corrupt / wrong-schema / non-UTF-8 / non-file / permission-
        denied `RejectedFinding` / `RejectionLedger` read degrades to a typed finding / safe skip (the named
        typed set — `StoreIntegrityError` / `CanonicalSerializationError` / `pydantic.ValidationError` /
        `FileNotFoundError` / `OSError`/`PermissionError`) — never a bare `except`, never a crash (AR10).
  - [x] **LOCK DN-WIRING (decide + document):** whether 5.3 wires invalidation into `pipeline.py` as a thin,
        additive, OPT-IN, byte-identical-to-today seam (consult the rejection ledger before serving a cached
        unit; bust orphaned detector-set entries on a detected detector-set change), OR delivers the surface as
        a library-only surface (the DEFAULT/RECOMMENDED scope, mirroring 5.2's library-only DN-WIRING). If
        wired, it MUST be default-equivalent so EVERY existing `pipeline.py` test passes byte-identically
        (an empty rejection ledger + an unchanged detector set → no bust → byte-identical to today). Record the
        decision + rationale.
- [x] **Task 1 — Build the IMPURE invalidation surface `apaa/cache/invalidation.py` + the V1 rejection seam** (AC: 1, 2, 3, 4)
  - [x] `class CacheInvalidator` (docstring cites `APAA-FR-27`, `APAA-NFR-D1`, `AR5`, `AR6`, `AR7`, `AR8`,
        `AR10`, `NFR-S1/S5`) constructed with the audited-repo root (or `ApaaStorePaths`) + a `MemoStore`.
  - [x] `bust_key(key) -> BustOutcome`: resolve `cache/<key>.json` containment-checked (NFR-S5), DELETE the
        slot file (whole-file delete, never a partial rewrite). Idempotent: a missing slot is a no-op outcome.
        A permission-denied / OS delete error degrades to a typed `BustOutcome`, never a raise (AR10). Leaves
        every other slot + the `.apaa/` tree intact.
  - [x] `bust_rejected_finding(record) -> BustOutcome`: bust `record.key` (the cache slot the rejected finding
        was served under). Zero LLM tokens. No source/secret byte read or emitted (operates on the redacted
        record + the slot file).
  - [x] `invalidate_on_detector_set_change(old_hash, new_hash, ...) -> tuple[BustOutcome, ...]`: DELETE the
        orphaned OLD-detector-set-hash cache entries (the active half of the 5.2 natural-MISS). Decide +
        document how the orphaned set is identified (a scan of `cache/` for entries derivable under the old
        hash, OR a known-keys set passed in — keep it deterministic + containment-safe). A no-change
        (`old_hash == new_hash`) is a no-op.
  - [x] `RejectedFinding` (frozen `extra="forbid"`, no source/secret/float/clock/uuid) + `RejectionLedger`
        (append-only read/persist over the 1.1 envelope + 1.3 writer, content-addressed). The DN-MISS swallow
        on a corrupt/wrong-schema read.
  - [x] No clock / uuid / random / float in any new record payload (the envelope's volatile `run_id`/
        `created_at` excluded from the content-hash per NFR-D3).
- [x] **Task 2 — The keystone proofs in NEW `tests/apaa/test_cache_invalidation.py`** (AC: 1, 2, 3, 5)
  - [x] Area `APAA-CACHE`, `TC-APAA-CACHE-001-46..NN` (continue after 5.2's …-45; confirm the next free index
        in the module docstring). **Under-bust-forbidden RED-then-green (AC1):** store a result containing a
        false 🔴 under key `K`; a NAIVE no-bust path re-serves the stale 🔴 on `lookup(K)` (RED); after
        `bust_rejected_finding(record)` the `lookup(K)` is a MISS → recompute (green). The fixture must be
        distinctive so "MISS happened" is a real proof, not vacuous.
  - [x] **Detector-set-change → re-compute-not-re-serve (AC2):** a two-detector-set fixture; entries under the
        OLD-hash key; after a detector edit `detector_set_content_hash` moves → the new key MISSes (natural,
        from 5.1) AND `invalidate_on_detector_set_change(old, new, ...)` deletes the orphaned OLD-hash slots
        (active); demonstrated RED against a path that re-keyed but left the old slot reachable.
  - [x] **Over-bust-safe (AC3):** bust MORE than the minimum; the recompute yields a verdict + ledger
        BYTE-IDENTICAL to a cold compute (harmless). **Idempotent (AC4):** a second `bust_key(K)` on an
        already-busted slot is a no-op outcome, never a raise. **Containment-safe (AC4):** a
        traversal/symlink/sibling-prefix key raises `WorkspaceContainmentError` BEFORE any delete, and a bust
        leaves sibling cache entries + the `.apaa/` tree intact (assert siblings survive).
  - [x] **No-crash on the bust/seam edges (AC4 / AI-E4-1):** a permission-denied / OS delete error degrades to
        a typed `BustOutcome` (RED against a path that lets the OS error propagate); a corrupt / wrong-schema /
        non-UTF-8 `RejectedFinding` read degrades to a typed finding / safe skip (RED against a trusting read).
  - [x] **Stable-AND-correct (AC5):** a clean repo audited repeatedly is stable; after a rejection / detector
        change the busted entry is re-computed (correct, reflects the change); a wiped-`.apaa/cache/` cold
        rebuild yields the SAME verdict. **AI-E1-1:** ≥1 bust fixture carries a non-ASCII / Cyrillic path,
        busts byte-stably, under `PYTHONIOENCODING=utf-8`.
- [x] **Task 3 — Security + structural gate extensions** (AC: 4, 6)
  - [x] Extend the 4.4 secret-containment property suite (`tests/security/test_apaa_secret_containment.py`) so
        the swept artifact-class union INCLUDES any new rejection-record artifact class (the `RejectedFinding`
        / `RejectionLedger` under `decisions/` or `cache/`): a planted canary secret in an audited unit is
        ABSENT from every rejection-record byte (the record cites `recording_id` + `key` + redacted metadata,
        never source/secret bytes; PROVE it is swept).
  - [x] Extend `test_no_web_imports.py` so the new module(s) (`apaa.cache.invalidation` + any rejection-seam
        module) are asserted FastAPI-free (import-isolation). CONFIRM `_MODULES_UNDER_GUARD` is the
        import-isolation set, NOT a purity set: `invalidation.py` is IMPURE (FS DELETE / record read) — add it
        to the import-isolation coverage but NOT to any purity-asserting guard (mirror `store/writer.py` /
        `cache/memo_store.py`). Confirm the single-serializer AST gate stays green (no second
        `json.dumps`/`hashlib`).
- [x] **Task 4 — Run + mypy + the pre-`review` test-existence precondition** (AC: 6)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` → all
        pass (1000 baseline + `test_cache_invalidation.py` + the extended 4.4 suite). `mypy` clean on
        `cache/invalidation.py` (+ any sibling).
  - [x] Confirm NO behavioral diff to the frozen Epic-1..4 + 5.1 + 5.2 surfaces (the invalidation surface
        COMPOSES them; the only permitted pre-existing-file edit is the DN-WIRING `pipeline.py` seam IF taken,
        and only if default-equivalent — every existing pipeline test passes byte-identically). Confirm NO
        `cli.py`/HTTP/CI-job change, NO shared/network cache, NO live Prosecutor/HITL trigger (6.4/6.7), NO
        live LLM/checkpoint capture (6.1).
  - [x] **AI-E4-4 / DN-DEFER:** if a NEW defer is filed, file it append-only in
        `_bmad-output/design-artifacts/APAA/deferred-work.md` with the six CC-3 fields. Do NOT pull 6.4/6.7
        live triggers or 6.1 live-capture into scope.
  - [x] **AI-E4-3 / AI-E2-1 GATE:** the mandatory artifacts (`cache/invalidation.py` + the V1 rejection seam +
        `tests/apaa/test_cache_invalidation.py` with the under-bust-forbidden / over-bust-safe / idempotent /
        containment-safe / detector-set-change / stable-AND-correct proofs + the extended 4.4 suite) EXIST +
        pass + the keystone RED-then-green is documented BEFORE the `review` flip; the Dev Agent Record is
        filled completely (no blank placeholders). This is the FINAL Epic-5 story — confirm the Epic-5
        retrospective is unblocked (all 5.x stories done/green).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **AR6 is THE driver — reproducibility ≠ correctness (architecture §247-250, CC #2, the brainstorm
  keystone).** "Memoization caches errors → cache entries invalidate on detector-set-hash change, and a
  human-rejected finding busts its own cache key (else a false 🔴 is served forever)." 5.1 built the key
  (the detector-set hash is folded), 5.2 built the store + read-side integrity→MISS, **5.3 builds the ACTIVE
  invalidation:** an explicit delete of orphaned detector-set entries + a rejected-finding key-bust. The
  read-side integrity→MISS of 5.2 was the FIRST line of the AR6 defense; this story is the SECOND (and
  closing) line.
- **The over-bust-safe / under-bust-forbidden asymmetry (the keystone correctness property).** Over-busting
  (invalidating too much) is HARMLESS — the next run re-computes and re-stores a byte-identical-to-recompute
  result (the 5.2 HIT==MISS property). Under-busting (re-serving a stale rejected finding) is the FAILURE AR6
  names. So when uncertain, BUST. A stale serve is never acceptable; an extra recompute always is. Document +
  test both directions (over-bust → still correct; under-bust → RED).
- **The invalidation surface COMPOSES the 5.1 key + the 5.2 store + the 1.3 containment/reader — it does NOT
  fork any of them (AR4/AR5/AR7).** NFR-P1 (byte-identical) dies the day a second `json.dumps`/`hashlib`
  appears. The bust uses the SAME `cache/<key>.json` slot convention as `MemoStore`; containment reuses
  `ApaaStorePaths`; the key is `cache/key.py::derive_cache_key` / `detector_set_content_hash` (the surface
  NEVER re-derives a key). The single-serializer AST gate must stay green.
- **`invalidation.py` is the IMPURE shell (AR8).** FS DELETE + a redacted-record read live here (mirroring
  `store/writer.py` / `cache/memo_store.py`) — it is NOT a pure module; do NOT add it to a purity-asserting
  guard set. Any NEW record payload (`RejectedFinding`) stays pure/clock-free (AR4: no float, no `uuid4`, no
  wall-clock, no `random`; the envelope's volatile `run_id`/`created_at` excluded from the content-hash per
  NFR-D3).
- **No-crash on the DELETE + rejection-seam edges is the AR10 / AI-E4-1 discipline (the 5.1/5.2 forward-flag
  continued onto the WRITE/DELETE surface).** Busting a missing/already-gone slot is a no-op `BustOutcome`
  (never a raise). A permission-denied / OS delete error degrades to a typed `BustOutcome`. A corrupt /
  wrong-schema / non-UTF-8 `RejectedFinding` read degrades to a typed finding / safe skip (the named typed set
  — `StoreIntegrityError`, `CanonicalSerializationError`, `pydantic.ValidationError`, `FileNotFoundError` /
  not-a-file, `OSError`/`PermissionError`). NO bare `except: pass`; NO `except Exception`; the named set only
  (so a programming bug still surfaces).
- **The rejected-finding is a SEPARATE record, NOT a Recording mutation (DN-REJECTION-SEAM).** `Recording` is
  frozen + additive-only (`ledger/recording.py`) and carries NO `rejected` field. A rejection is a first-class
  `RejectedFinding` record that CITES a `recording_id` + the cache `key` it was served under + redacted
  metadata — never a mutation of the immutable Recording (§3.4 evidence immutability). The `RejectionLedger`
  is append-only.
- **The live rejection TRIGGER is Epic-6; 5.3 builds only the SEAM (the load-bearing scope fence).** The
  Prosecutor pass (Story 6.4) and the HITL STOP/PROCEED gate + append-only decision RECORD (Story 6.7) are the
  live sources that DECIDE a finding is rejected. They are OUT of 5.3 scope. 5.3 builds the `RejectedFinding`
  record + `RejectionLedger` SEAM + the busting that CONSUMES it; an Epic-6 6.4/6.7 caller substitutes the
  live trigger additively (it APPENDS records; the 5.3 surface consumes them unchanged) — mirroring the 5.1
  `V1_MODEL_CHECKPOINT` / `V1_PROMPT_TEMPLATE_VERSION` placeholder discipline. Do NOT build 6.4/6.7. The
  detector-set-change half (AC2) is FULLY live now (no seam needed — the key already folds the detector-set
  hash).
- **LOCAL-only; never the sole guarantee (NFR-D1 / architecture §87).** The cache + invalidation surface are
  local to the audited repo's `.apaa/cache/` tree. No shared / cross-machine / network cache (the G4 cross-run
  shared cache is V4). The verdict is correct WITHOUT the cache (wipe + re-run → same verdict).
- **No source/secret bytes in the rejection record (NFR-S1 / the 5.1/5.2 forward-flag continued).** THIS story
  writes a NEW `.apaa/` artifact class (the rejection record/ledger), so it MUST extend the 4.4
  secret-containment property suite to sweep that class. The record cites `recording_id` + `key` + redacted
  metadata, never source/secret bytes.
- **Frozen contracts unchanged (AR8/NFR-M2).** The surface COMPOSES the Epic-1..4 + 5.1 + 5.2 surfaces
  read-only. The ONLY permitted edit to a pre-existing surface is the DN-WIRING `pipeline.py` seam IF taken
  (thin, additive, opt-in, default-equivalent — every existing pipeline test passes byte-identically).
  `cache/key.py` and `cache/memo_store.py` are NOT modified (beyond an additive byte-identical-to-today helper
  if STRICTLY required — prefer composition in the new module).

### Project Structure Notes

- **NEW impure module:** `minions_core/apaa/cache/invalidation.py` (the AR6 active invalidation + the V1
  rejection seam; architecture §438 `cache/memo_store.py — NFR-D1 — content-addressed on-disk memo +
  invalidation` — the "+ invalidation" half of that line is THIS story). Decide whether the `RejectedFinding`
  record + `RejectionLedger` live in `invalidation.py` or a thin sibling (e.g.
  `cache/rejection.py`) — keep each ≤1200 lines (NFR-M1). `minions_core/apaa/cache/__init__.py` already exists
  (Story 5.1).
- **NEW test module:** `tests/apaa/test_cache_invalidation.py`. Test area `APAA-CACHE`
  (`TC-APAA-CACHE-001-46..NN` — continue after 5.2's …-45; confirm the next free index in the module
  docstring). ≤1200 lines.
- **EDIT (extend, not fork):** `tests/security/test_apaa_secret_containment.py` (4.4) — add the rejection-
  record artifact class to the swept union. `tests/apaa/test_no_web_imports.py` — assert the new module(s) are
  FastAPI-free (import-isolation; they are IMPURE, so NOT in any purity guard).
- **REUSE read-only (verify NO behavioral diff):** `cache/key.py` (`derive_cache_key`,
  `detector_set_content_hash`, `FROZEN_DETECTOR_SET`, `DetectorDescriptor`, `RecordingProducingClosure`,
  `CacheKeyError`), `cache/memo_store.py` (`MemoStore.store`/`lookup`, `RecordedResult`, the `cache/<key>.json`
  slot convention, the DN-MISS taxonomy), `store/paths.py::ApaaStorePaths` (`resolve`/`ensure_parent`/
  `to_locator` — containment), `store/reader.py::ApaaStoreReader` (`read_envelope(verify_hash=True)` →
  `StoreIntegrityError`; `CanonicalSerializationError`), `store/writer.py::ApaaStoreWriter` (`write_payload`
  — for the rejection ledger), `store/envelope.py` (`EnvelopeWriter.build`/`compute_content_hash`), the frozen
  `Recording`/`Locator` schema (`ledger/recording.py` — the rejection record cites a `recording_id`, never
  mutates a Recording).
- **NO `cli.py` change / NO new HTTP route / FastAPI surface / UI (§3.7). NO new `.github/workflows` CI job**
  (the tests are normal `tests/apaa/` + `tests/security/` tests). **NO shared/network cache (LOCAL-only).**
  **NO live Prosecutor (6.4) / HITL (6.7) trigger; NO 6.1 live LLM / real checkpoint capture.**

### Testing Standards (APAA)

- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` (the
  `PYTHONIOENCODING` prefix avoids the cp1252 emoji crash on Windows — project memory). `mypy` via
  `python run_mypy_per_file.py` or scoped to `cache/invalidation.py`.
- **Verification ID format:** `TC-APAA-CACHE-001-NN` (continue the `cache/` area Stories 5.1+5.2 opened —
  5.1 …-01..22, 5.2 …-23..45; the next free index is **…-46**; confirm/lock it in the module docstring).
- **AI-E4-1 keystone-adequacy (the literal honesty properties of this story):** (a) under-bust-forbidden —
  demonstrated RED against a naive path that does NOT bust (it re-serves the stale 🔴); (b) over-bust-safe —
  a broader bust still yields a byte-identical-to-cold-compute verdict; (c) detector-set-change → recompute,
  RED against a path that re-keyed but left the old slot reachable; (d) no-crash on the DELETE / rejection-seam
  edges — permission-denied delete + corrupt/wrong-schema record each degrade to a typed result, RED against a
  trusting/propagating path; (e) idempotent + containment-safe + sibling-survival. Each leg's fixture must be
  distinctive so a "MISS happened" / "verdict identical" / "no raise" assertion is a real proof, not vacuous.
- **AI-E1-1 non-ASCII discipline:** ≥1 bust fixture carries a non-ASCII / Cyrillic path/value, busts
  byte-stably; run under `PYTHONIOENCODING=utf-8`; explicit UTF-8 (single serializer is `ensure_ascii=False`).
- **Impurity is expected (AR8):** `invalidation.py` DOES FS I/O (DELETE + a redacted-record read — it is the
  impure shell). Do NOT assert it pure. DO assert (import-isolation) it is FastAPI-free, and that it adds no
  second `json.dumps`/`hashlib` (single-serializer AST gate green).
- **The 4.4 secret-containment suite (extended) stays green:** a planted canary in an audited unit is ABSENT
  from every rejection-record byte.
- **The structural gates stay green:** import-isolation (`test_no_web_imports.py`), single-serializer AST gate
  (`test_canonical_single_serializer.py`), file-size (≤1200 lines).

### References

- Epic: `_bmad-output/design-artifacts/APAA/epics.md` — Epic 5 / Story 5.3 (cache invalidation &
  rejected-finding key-busting; FR27; NFR-D1; "a cache that cannot ossify a wrong answer — invalidates on
  detector-set change; a rejected finding busts its own key"; the clean-repo flaky-vs-stable "stable AND
  correct" AC).
- PRD: `_bmad-output/design-artifacts/APAA/E-PRD/prd.md` — FR27 (reproduce the same verdict for the same
  repository and APAA version), NFR-D1 (local content-addressed memoization; key = content-hash + model
  checkpoint + detector-set hash; "NOT an assumption the LLM repeats itself"), NFR-D2 (deterministic +
  zero-LLM-token — the bust path is token-free), NFR-D3 (content hashes cover the canonical payload only —
  volatile `run_id`/`created_at` excluded), NFR-P1 (byte-identical), NFR-S1/S2 (no source/secret bytes — the
  rejection record joins the swept union), NFR-S5 (containment), NFR-M1/M2.
- Architecture: `_bmad-output/design-artifacts/APAA/architecture.md` — §247-250 (content-addressed
  memoization; **invalidate on detector-set change; a human-rejected finding busts its own key — R2/R3**; the
  5.2/5.3 split — 5.2 read-side integrity, 5.3 active invalidation), §87 (self-contained, LOCAL memoization;
  local cost ceiling), §91-96 (CC #1 the KEY is the keystone; CC #2 memoization caches errors →
  reproducibility ≠ correctness — the AR6 lever THIS story rides), §322-324 (the recording schema is upstream
  of verdict AND the memo cache — single source), §350 (one cache-key function — the surface CONSUMES it),
  §430-438 (`cache/memo_store.py` — content-addressed on-disk memo + invalidation), §458-467 (the `.apaa/`
  runtime tree — `cache/` + `decisions/`), §493 (pure/impure boundary — `invalidation` is the IMPURE side),
  AR4 (single serializer / no float), AR5 (one cache-key function — the surface consumes it), AR6 (invalidation
  — the central driver of this story), AR7 (reuse-by-import / leaf modules), AR8 (pure/impure), AR10 (typed
  degradation — no-crash on the DELETE / rejection-seam edges), AR11 (content-addressed filenames).
- Story 5.1: `_bmad-output/design-artifacts/APAA/stories/5-1-cache-key-derivation-recording-producing-closure-ci-canary.md`
  — the pure `cache/key.py` the surface CONSUMES (`derive_cache_key`, `detector_set_content_hash`,
  `FROZEN_DETECTOR_SET`, `DetectorDescriptor`, `CacheKeyError`); the detector-set content-hash is the **AR6
  invalidation lever** Story 5.3 rides; the DN-PLACEHOLDER seam discipline (ship the slot now, substitute the
  live source at 6.x) mirrored by this story's V1 rejection seam.
- Story 5.2: `_bmad-output/design-artifacts/APAA/stories/5-2-content-addressed-memoization-store.md`
  — the impure `cache/memo_store.py` the surface COMPOSES (`MemoStore.store`/`lookup`, `RecordedResult`, the
  `cache/<key>.json` slot, the DN-MISS swallow taxonomy); the explicit 5.2-vs-5.3 fence ("5.2 builds the
  STORE + read-side integrity→MISS; 5.3 builds ACTIVE invalidation + rejected-finding key-busting; a
  detector-set edit already changes the key → a NATURAL MISS — the ACTIVE eviction is 5.3"); the HIT==MISS
  byte-identity property that makes an over-bust safe (a recompute is byte-identical to a cache miss).
- Story 1.3: `_bmad-output/design-artifacts/APAA/stories/1-3-apaa-store-writer-reader-filesystem-containment.md`
  — the `ApaaStorePaths` containment (reused for the bust DELETE path), the `ApaaStoreWriter`/`ApaaStoreReader`
  + the `read_envelope(verify_hash=True)` → `StoreIntegrityError` tamper guard (reused for the rejection-seam
  read).
- Story 4.4: the secret-containment property suite the surface extends (the rejection-record artifact class
  joins the swept union). Story 6.4 (Prosecutor) / Story 6.7 (HITL STOP/PROCEED + decision record) — the
  Epic-6 live rejection TRIGGERS that POPULATE this story's V1 seam (OUT of 5.3 scope).
- Epic-4 retro: `_bmad-output/design-artifacts/APAA/epic-4-retro-2026-06-28.md` — action items AI-E4-1
  (no-crash input-shape checklist — landing on the cache DELETE / rejection-seam surface here), AI-E4-4 (defer
  back-fill), AI-E4-7 (keep structural gates green / extend the 4.4 union to the new artifact class).
- Source: `minions_core/apaa/cache/key.py` (the consumed key + detector-set hash — the AR6 lever),
  `minions_core/apaa/cache/memo_store.py` (the composed store), `minions_core/apaa/store/{paths,reader,writer,
  envelope,canonical}.py` (containment + reader/writer + envelope + serializer),
  `minions_core/apaa/ledger/recording.py` (the frozen `Recording` the rejection record cites — never mutates),
  `minions_core/apaa/pipeline.py` (the DN-WIRING seam, IF taken).
- Test precedent: `tests/apaa/test_memo_store.py` (the 5.2 keystone-adequacy RED-demo pattern to mirror for
  the under-bust/over-bust proofs), `tests/apaa/test_cache_key.py` (the 5.1 canary / detector-set-hash
  pattern), `tests/apaa/test_no_web_imports.py` (import-isolation — extend),
  `tests/apaa/test_canonical_single_serializer.py` (the single-serializer AST gate),
  `tests/security/test_apaa_secret_containment.py` (the 4.4 suite — extend to sweep the rejection-record
  class).
- Defer register: `_bmad-output/design-artifacts/APAA/deferred-work.md` — file any NEW defer append-only here
  with the six CC-3 fields (AI-E4-4).

## Dev Agent Record

### Context Reference

- Story drafted by the BMAD Scrum Master (create-story) on 2026-06-28 from epics.md (Epic 5 / Story 5.3) +
  PRD (FR27 / NFR-D1/D2/D3 / NFR-S1/S5) + architecture.md (content-addressed memoization + invalidation
  §247-250, CC #1/#2 §91-96, AR6, the LOCAL-only §87, the `.apaa/` tree §458-467, `cache/memo_store.py +
  invalidation` §438, the pure/impure boundary §493) + Story 5.1 (the consumed pure `cache/key.py` +
  `detector_set_content_hash` — the AR6 invalidation lever; the DN-PLACEHOLDER seam discipline) + Story 5.2
  (the composed impure `cache/memo_store.py`; the explicit 5.2-vs-5.3 fence; the HIT==MISS property that makes
  an over-bust safe) + Story 1.3 (the reused `ApaaStorePaths` containment + the `read_envelope(verify_hash=
  True)` → `StoreIntegrityError` tamper guard) + Story 4.4 (the secret-containment suite to extend) + the
  Epic-4 retro (AI-E4-1 no-crash input-shape on the DELETE / rejection-seam surface, AI-E4-4 defer back-fill,
  AI-E4-7 structural gates). The brainstorm keystone (the over-bust-safe / under-bust-forbidden asymmetry; a
  rejected finding busts its own key; a detector-set change invalidates; reproducibility ≠ correctness; stable
  AND correct) is the load-bearing AC set (AC1/AC2/AC3/AC5). The live rejection TRIGGER (Prosecutor 6.4 / HITL
  6.7) is EXPLICITLY deferred to Epic-6 — 5.3 builds only the V1 `RejectedFinding` / `RejectionLedger` seam.
  Carries AI-E1-1 (non-ASCII).

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, implement/resume — a prior session was interrupted by a transport
timeout after writing `invalidation.py` + flipping status to `in-progress`, but BEFORE writing the test
suite; this session inspected/confirmed the production module against the ACs and wrote the missing tests
+ the two gate extensions).

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
  **1032 passed, 1 skipped, 4 subtests passed** (the 5.2 baseline of 1000 passed / 1 skipped + 30 new
  `test_cache_invalidation.py` tests + 2 extended 4.4 security tests = +32).
- `python -m mypy minions_core/apaa/cache/invalidation.py` → **Success: no issues found**.
- One RED→fix during test authoring: `test_bust_sibling_prefix_key_raises_containment` initially used
  `../.apaa-evil/cache/x`, which `_relative_for` maps to `cache/../.apaa-evil/...` → resolves INSIDE
  `.apaa/` (contained, no raise). Corrected to `../../.apaa-evil/cache/x`, which resolves to a TRUE sibling
  of `.apaa` (`<repo>/.apaa-evil/...`) so `is_relative_to` rejects it (a `str.startswith(".apaa")` check
  would falsely accept the prefix — the exact NFR-S5 distinction the test pins). Verified the resolution
  empirically before re-asserting.

### Completion Notes List

- **Production surface (`apaa/cache/invalidation.py`, ~448 lines) confirmed complete against all 6 ACs** —
  it was authored by the interrupted session and verified here line-by-line, not rewritten. The surface:
  `CacheInvalidator(repo_root | ApaaStorePaths, store: MemoStore, *, rejection_ledger=None)` with
  `bust_key(key) -> BustOutcome`, `bust_rejected_finding(record) -> BustOutcome`,
  `invalidate_rejections() -> tuple[BustOutcome, ...]`, and
  `invalidate_on_detector_set_change(old_hash, new_hash, *, known_keys) -> tuple[BustOutcome, ...]`; plus
  the V1 rejection SEAM `RejectedFinding` (frozen, `extra="forbid"`, cites `recording_id` + cache `key` +
  redacted `rule_id`/`cartridge_id`/`reason`/`rejected_by`, NO source/secret bytes) + `RejectionLedgerPayload`
  + `RejectionLedger` (append-only read/persist over `decisions/rejection_ledger.json`, content-addressed via
  the 1.1 envelope + the single canonical serializer; read reuses the 1.3 `read_envelope(verify_hash=True)`
  tamper guard) + `BustOutcome` (frozen typed result: `busted`/`key`/`locator`/`reason`).
- **AC1 (rejected-finding key-bust) — proven** TC-APAA-CACHE-001-46..49: bust→MISS; the under-bust RED leg
  (a naive no-bust path re-serves the stale 🔴 on the SAME `lookup(K)` the green leg MISSes — non-vacuous);
  zero-token / no-payload-read; `invalidate_rejections()` busts each ledger record.
- **AC2 (detector-set change) — proven** TC-APAA-CACHE-001-50..53: a `code_identity` edit moves
  `detector_set_content_hash` → moves the key (NATURAL MISS on the new key, from 5.1) AND
  `invalidate_on_detector_set_change(old, new, known_keys=...)` actively deletes the orphaned OLD-hash slot;
  RED against a re-key-only path that leaves the old slot reachable; a no-change (`old==new`) is a no-op;
  the new-key recompute is byte-identical.
- **AC3 (over-bust SAFE / under-bust FORBIDDEN asymmetry) — proven** TC-APAA-CACHE-001-54..55: an over-bust
  (busting an entry that did not strictly need it) recomputes byte-identically to a cold compute (the 5.2
  HIT==MISS property); the under-bust RED leg re-serves the stale 🔴. The asymmetry is documented in the
  module docstring ("when in doubt, BUST").
- **AC4 (idempotent / containment / leak-free / no-crash / no-corruption) — proven** TC-APAA-CACHE-001-56..69:
  idempotent (absent→absent, deleted→absent, never raises); containment (`../../escape` and `../../.apaa-evil/...`
  raise `WorkspaceContainmentError` BEFORE any delete, planted outside file survives); sibling-survival (a bust
  deletes ONE slot, every other slot + the `.apaa/` tree intact); permission-denied delete degrades to
  `BustOutcome(busted=False, reason="os_error")` (RED against a propagating `Path.unlink`); the rejection-seam
  read degrades to an EMPTY ledger on corrupt / non-UTF-8 / tampered (content-hash mismatch) / wrong-schema
  (`extra=forbid`) / missing (the named typed set only); the record payload is pure (no float/clock/uuid; the
  envelope hash excludes `run_id`/`created_at`, NFR-D3); `RejectedFinding` is frozen + `extra="forbid"`; the
  ledger is append-only.
- **AC5 (stable AND correct; LOCAL-only; non-ASCII) — proven** TC-APAA-CACHE-001-70..72: stable repeatedly →
  after a bust re-computed (correct) → wiped-cache cold rebuild yields the SAME result; a bust on repo A does
  not touch repo B; a Cyrillic/`café` closure path + a `ложноположительный` reason bust + round-trip
  byte-stably under `PYTHONIOENCODING=utf-8` (AI-E1-1).
- **AC6 (no regression / gates green / mypy clean) — proven** TC-APAA-CACHE-001-73..75: `BustOutcome` is a
  typed frozen result (not a bare bool); the surface CONSUMES the handed key (`locator == cache/<key>.json`,
  never re-derives — AR5); `invalidation.py` + the test file each ≤1200 lines. The single-serializer AST gate
  (auto-scans `minions_core/apaa/**`) stays green — `invalidation.py` adds NO `json.dumps`/`hashlib`, only
  `canonical.dumps_bytes` + the 1.1 `compute_content_hash`. `_MODULES_UNDER_GUARD` extended (not forked) with
  `minions_core.apaa.cache.invalidation` (import-isolation: FastAPI-free; impure → NOT a purity guard).
- **DN-WIRING decision = library-only** (mirroring 5.2). `pipeline.py` is UNMODIFIED / byte-identical to
  today; the live consult-the-rejection-ledger-before-serving + the live detector-set-change trigger are an
  Epic-6 concern (the V1 surface is the deterministic mechanism the Epic-6 Prosecutor/HITL caller drives).
- **4.4 secret-containment suite extended** (TC-APAA-SECURITY-001-19/20): the `.apaa/decisions/` rejection-
  record artifact class joins the swept union — a planted canary in an audited unit is ABSENT from every
  rejection-record byte (the record cites `recording_id` + `key` + redacted metadata only), and a planted
  raw-secret in a `.apaa/decisions/` byte is CAUGHT by the sweep (keystone-adequacy).
- **No new defer filed.** Scope fences honored: NO live Prosecutor (6.4) / HITL (6.7) trigger, NO 6.1 live
  LLM / real checkpoint capture, NO shared/network cache (LOCAL-only), NO `cli.py`/HTTP/new-CI-job.
- **This is the FINAL Epic-5 story** — with 5.1 + 5.2 done and 5.3 now at `review`, the Epic-5 retrospective
  is unblocked once 5.3 closes.

### File List

- `minions_core/apaa/cache/invalidation.py` (NEW — authored by the interrupted prior session; confirmed
  complete + ACs-compliant this session; ~448 lines, impure shell).
- `tests/apaa/test_cache_invalidation.py` (NEW — the 30 keystone proofs, TC-APAA-CACHE-001-46..75).
- `tests/apaa/test_no_web_imports.py` (EDIT — `_MODULES_UNDER_GUARD` extended with
  `minions_core.apaa.cache.invalidation`).
- `tests/security/test_apaa_secret_containment.py` (EDIT — the `.apaa/decisions/` rejection-record class
  added to the swept union: TC-APAA-SECURITY-001-19/20).
- `_bmad-output/design-artifacts/APAA/sprint-status.yaml` (status `5-3-... → review`; `last_updated` 2026-06-29).
- `_bmad-output/design-artifacts/APAA/stories/5-3-cache-invalidation-rejected-finding-key-busting.md`
  (Status, tasks, Dev Agent Record, Change Log).

## Senior Developer Review (AI)

**Reviewer:** claude-opus-4-8 (BMAD code-review gate, adversarial)
**Date:** 2026-06-29
**Outcome:** PASS (verdict: pass) — iteration 1
**Story key:** 5-3-cache-invalidation-rejected-finding-key-busting

### Verdict & rationale

The AR6 active-invalidation surface (`apaa/cache/invalidation.py`) and its V1 rejection seam are correct,
well-scoped, and the keystone proofs are genuinely load-bearing (verified empirically, not taken on faith).
All 6 ACs are met; tests are green; mypy is clean; the structural + security gates pass. Status → `done`.

### Independent verification (re-run, not trusted)

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
  **1032 passed, 1 skipped, 4 subtests** in 81s (matches the Dev Agent Record's claim; the 1000/1 5.2
  baseline + 30 new `test_cache_invalidation.py` + 2 extended 4.4 security tests).
- `python -m mypy minions_core/apaa/cache/invalidation.py` → **Success: no issues found**.
- `test_canonical_single_serializer.py` (AST gate, auto-scans `minions_core/apaa/**`) → green; a grep over
  `invalidation.py` confirms NO `import hashlib` / `import json` / `json.dumps` / `hashlib.` / `sha256` —
  reuse-not-fork holds (composes `canonical.dumps_bytes` + `compute_content_hash` + the 1.3 reader/writer +
  5.1 key + 5.2 MemoStore only).

### Keystone adequacy — verified ADVERSARIALLY (the load-bearing checks)

1. **UNDER-BUST-FORBIDDEN is non-vacuous.** I monkey-patched `bust_key` to a no-op and re-ran the AC1 green
   path: with a no-op bust, `store.lookup(key)` returns a HIT (not `None`), so the GREEN-leg assertion
   `store.lookup(key) is None` (TC-46/47/55) genuinely fails RED. The bust is proven load-bearing — a stale
   rejected 🔴 is genuinely re-served if the surface does not bust, and the surface forces a recompute.
2. **OVER-BUST-SAFE = recompute byte-identical.** TC-54/55 store two entries, bust both (only one needed it),
   and assert `_canonical_bytes(served) == _canonical_bytes(recompute)` — the 5.2 HIT==MISS property makes the
   over-bust harmless. Asymmetry documented in the module docstring ("when in doubt, BUST").
3. **CONTAINMENT-SAFE delete — `is_relative_to`, not `startswith`.** Verified empirically:
   `cache/../../.apaa-evil/cache/x.json` resolves to a TRUE sibling of `.apaa` and is rejected by
   `WorkspaceContainmentError` BEFORE any delete, while `cache/../.apaa-evil/...` stays inside `.apaa`
   (contained) — exactly the NFR-S5 distinction a `str.startswith(".apaa")` check would get wrong. `bust_key`
   places the containment `resolve()` BEFORE the `try`, so an escape propagates loud-by-design (NOT swallowed);
   the named-typed-set swallow (`PermissionError`/`OSError`) covers only the benign delete edge → typed
   `BustOutcome(reason="os_error")`. Idempotent (`absent`/`deleted`/`absent`), sibling-survival proven.
4. **§3.4 EVIDENCE IMMUTABILITY preserved.** `Recording` is `frozen=True, extra="forbid"` with NO `rejected`
   field; `invalidation.py` never imports or mutates `Recording` — a rejection is a SEPARATE frozen
   `RejectedFinding` citing `recording_id` (a string) + `key` + redacted metadata. No Recording-mutation path
   exists.
5. **No-crash on the rejection-seam read.** `RejectionLedger.read()` swallows ONLY the named typed set
   (`StoreIntegrityError`/`CanonicalSerializationError`/`ValidationError`/`FileNotFoundError`/`PermissionError`/
   `OSError`) → empty ledger; corrupt / non-UTF-8 / tampered (content-hash mismatch) / wrong-schema / missing
   all degrade to a safe no-op (TC-61..65). No bare `except`, no `except Exception` — a programming bug still
   surfaces.

### AR6 lever scope (confirmed NOT a hidden Epic-6 dependency)

- The detector-set-change half is FULLY live: `invalidate_on_detector_set_change(old, new, known_keys=...)`
  actively deletes orphaned OLD-hash slots, riding the 5.1 detector-set hash; the orphan set is passed in by
  the caller (`known_keys`) — a documented, story-sanctioned V1 seam (Task 1 explicitly permitted "a known-keys
  set passed in"), not a scan and not an Epic-6 trigger.
- The live rejection SOURCE (Prosecutor 6.4 / HITL 6.7) is a V1 placeholder seam: `RejectionLedger` is the
  append-only surface an Epic-6 caller populates; the busting surface consumes it unchanged. DN-WIRING =
  library-only — `pipeline.py` contains NO reference to `invalidation`/`CacheInvalidator`/`RejectionLedger`/
  `bust` (grep-confirmed), so it is byte-identical and there is no hidden wiring.

### Findings

- **[Low] `minions_core/apaa/cache/invalidation.py:181-191,262-277` — doc-precision (non-blocking, NOT fixed
  here).** The `RejectionLedger` class docstring claims it "REUSES the 1.3 `ApaaStoreWriter`", but `_write`
  inlines the byte write (`EnvelopeWriter.build` + `ensure_parent` + `write_bytes`) rather than calling
  `ApaaStoreWriter`. This is DEFENSIBLE — the fixed-name `decisions/rejection_ledger.json` slot needs a
  non-content-addressed filename, which `ApaaStoreWriter.write_envelope` (filename = `content_hash`) cannot
  produce — and it does NOT fork the serializer/hasher (it uses the single canonical serializer + the 1.1
  envelope, and the read reuses the 1.3 `read_envelope(verify_hash=True)` tamper guard). This mirrors the same
  Low doc nit accepted on story 5-2 (`store()` inlining). Suggested fix (optional, future): tighten the
  docstring to "reuses the 1.1 envelope + the single canonical serializer; writes through a fixed-name slot
  (the content-addressed `ApaaStoreWriter` filename is intentionally bypassed)". Does not block `done`.

No High or Medium findings. No `decision-needed` or `patch` items. No new defer filed (scope fences honored).

### Scope-fence audit (all green)

NO live Prosecutor (6.4) / HITL (6.7) trigger; NO 6.1 live-LLM / real checkpoint capture; NO shared/network
cache (LOCAL-only — TC-71 proves repo A bust ≠ repo B); NO `cli.py` subcommand / HTTP route / new CI job;
headless (§3.7); files ≤1200 lines (invalidation.py 447, test 695); non-ASCII byte-stable (TC-72, café/Cyrillic
+ `ложноположительный`). This is the FINAL Epic-5 story — the Epic-5 retrospective is now unblocked.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-06-28 | 0.1 | Initial draft (create-story) — Epic 5 / Story 5.3 cache invalidation & rejected-finding key-busting; AR6 active-invalidation layer; detector-set-change half FULLY live (5.1 key folds the detector-set hash), rejected-finding half is a V1 `RejectedFinding`/`RejectionLedger` SEAM with the live trigger (Prosecutor 6.4 / HITL 6.7) deferred to Epic-6; over-bust-safe / under-bust-forbidden keystone; library-only or default-equivalent pipeline wiring; FINAL Epic-5 story. | BMAD Scrum Master |
| 2026-06-29 | 0.3 | code-review iter-1 PASS (claude-opus-4-8, adversarial gate). Independently re-ran the suite (1032 passed / 1 skipped / 4 subtests) + mypy clean + single-serializer AST gate green. Keystone adequacy verified ADVERSARIALLY: monkey-patched bust_key to a no-op → the AC1 GREEN-leg assertion `lookup(K) is None` genuinely fails RED (under-bust is load-bearing, non-vacuous); over-bust byte-identical to cold (5.2 HIT==MISS); containment empirically rejects the sibling-prefix `../../.apaa-evil/...` via is_relative_to BEFORE any delete while keeping the contained `../.apaa-evil/...` inside `.apaa` (the exact NFR-S5 distinction startswith gets wrong); §3.4 — Recording is frozen/no `rejected` field, never mutated, rejection is a separate frozen RejectedFinding citing recording_id; no-crash named-typed-set swallow on the seam read; no 2nd serializer/hasher (grep-confirmed); pipeline.py byte-identical (no invalidation import); files ≤1200; secret-containment sweep extended non-vacuously (asserts decisions_blob non-empty + catches a planted leak). ONE Low doc-precision nit (RejectionLedger docstring says "reuses ApaaStoreWriter" but _write inlines the byte write for the fixed-name slot — defensible, no serializer fork, same nit accepted on 5-2; non-blocking). No High/Med, no decision-needed/patch, no new defer. Status review → done. FINAL Epic-5 story → Epic-5 retro unblocked. | BMAD Reviewer |
| 2026-06-29 | 0.2 | dev-story (implement/resume, claude-opus-4-8). A prior session was interrupted (transport timeout) after writing `apaa/cache/invalidation.py` + flipping status `in-progress`, but BEFORE the test suite. This session CONFIRMED the production module complete + ACs-compliant (CacheInvalidator + bust_key/bust_rejected_finding/invalidate_rejections/invalidate_on_detector_set_change + BustOutcome + the V1 RejectedFinding/RejectionLedgerPayload/RejectionLedger seam; composes 5.1 key + 5.2 MemoStore + 1.3 ApaaStorePaths/reader/writer + 1.1 serializer/envelope — no 2nd serializer/hasher) and WROTE the missing `tests/apaa/test_cache_invalidation.py` (30 keystone proofs, TC-APAA-CACHE-001-46..75): under-bust-forbidden RED-then-green, over-bust-safe, detector-set-change recompute-not-re-serve (RED against a re-key-only path), idempotent, containment-safe (`../../escape` + sibling-prefix `.apaa-evil` raise before any delete), sibling-survival, permission-denied delete → typed BustOutcome (RED), corrupt/non-UTF-8/tampered/wrong-schema/missing rejection-ledger → empty safe-skip, frozen+extra=forbid record, append-only ledger, stable-AND-correct + wiped-cache cold rebuild, LOCAL-only, non-ASCII (AI-E1-1). Extended `_MODULES_UNDER_GUARD` (import-isolation, impure→not a purity guard) + the 4.4 secret-containment suite (`.apaa/decisions/` rejection-record class swept: TC-APAA-SECURITY-001-19/20). DN-WIRING = library-only (pipeline.py byte-identical). Single-serializer AST gate green. Tests: **1032 passed / 1 skipped / 4 subtests** (was 1000/1; +32); mypy clean on invalidation.py. No new defer. Scope fences honored (no 6.4/6.7 trigger, no 6.1 live-LLM/checkpoint, no shared/network cache, no cli/HTTP/CI-job). FINAL Epic-5 story → `review`. | BMAD Developer |
