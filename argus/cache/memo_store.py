"""IMPURE content-addressed memoization STORE over the fixed ``.argus/cache/`` tree.

Drivers: ArgusAgent-FR-27 (reproduce the same verdict for the same repo + ArgusAgent version —
the memo STORE is what ACHIEVES the reproduction the 5.1 key fingerprints),
ArgusAgent-NFR-D1 (same repo @ commit @ ArgusAgent version → identical verdict + ledger via
LOCAL content-addressed memoization — the central driver), ArgusAgent-NFR-D2 (the cache
read/write is itself zero-LLM-token; a HIT spends zero tokens), ArgusAgent-NFR-D3
(content hashes cover the canonical payload only — volatile ``run_id``/
``created_at`` excluded, so two stores of the same result are content-addressed to
the SAME slot), ArgusAgent-NFR-P1 (a HIT round-trips byte-identically to the recompute),
ArgusAgent-AR4 (single serializer / no float in the cached payload), ArgusAgent-AR5 (the store
CONSUMES ``derive_cache_key`` — it does NOT re-derive a key), ArgusAgent-AR6 (the
read-side integrity→MISS is the first line of the "memoization caches errors →
reproducibility ≠ correctness" defense; the ACTIVE invalidation / rejected-finding
key-busting is Story 5.3), ArgusAgent-AR7 (REUSE the 1.3 containment / writer / reader +
the tamper guard by import — no fork), ArgusAgent-AR8 (this is the IMPURE shell — FS I/O
is confined here; the cached payload stays pure / clock-free), ArgusAgent-AR10 (typed
degradation — a corrupt / tampered / non-file / permission-denied / wrong-schema
cache entry degrades to a MISS, never an uncaught raise / a silently-wrong served
result), ArgusAgent-NFR-S1/S5 (no source / secret bytes in cached artifacts —
containment-checked writes; the cache joins the 4.4 swept union), ArgusAgent-NFR-M1
(≤1200-line files), ArgusAgent-AR11 (content-addressed filenames — the cache slot is
keyed on the 5.1 cache KEY, never arrival order).

The keystone — the ArgusAgent reproducibility FLOOR (architecture CC #1/#2, §247-250)
------------------------------------------------------------------------------
The memo cache is an OPTIMIZATION, NOT the sole correctness guarantee. Three
non-negotiable invariants this module upholds:

1. HIT == MISS byte-identity. The stored bytes ARE
   ``canonical.dumps_bytes(result_payload)``; :meth:`lookup` returns the validated
   payload re-built from those same bytes — round-tripping through the store
   changes nothing. A HIT serves the SAME canonical bytes a MISS would recompute.
2. The cache NEVER changes the verdict. The store lives strictly UPSTREAM of the
   pure 1.6 verdict gate; it feeds the SAME recordings whether served or
   recomputed. A warm-cache run and a cold-cache run over the same closure produce
   byte-identical ``.argus/`` verdict state.
3. Tamper / corruption / poison → MISS, never silently-wrong. :meth:`lookup`
   RE-VERIFIES the envelope ``content_hash`` (reusing the 1.3
   ``read_envelope(verify_hash=True)`` → :class:`StoreIntegrityError` tamper
   guard) and validates the payload schema; on ANY of the named typed failures
   (or a missing / non-file entry) it returns a MISS — the poisoned bytes NEVER
   reach the verdict and the read NEVER raises out of the store.

The DN-MISS swallow taxonomy (the AR10 / AI-E4-1 no-crash discipline)
---------------------------------------------------------------------
:meth:`lookup` catches the SPECIFIC typed set —
:class:`StoreIntegrityError` (tamper / content-hash mismatch),
``canonical.CanonicalSerializationError`` (corrupt / non-UTF-8 / non-JSON),
``pydantic.ValidationError`` (wrong schema / ``extra="forbid"`` violation),
``FileNotFoundError`` (no entry / not-a-file), ``OSError`` /
``PermissionError`` (unreadable) — and converts EACH to a MISS (``None``). This
is the ONE place a typed store error is SWALLOWED (a cache is advisory), in
deliberate contrast to the 1.3 reader which RAISES (resumability state must not be
silently lost). There is NO bare ``except: pass`` and NO ``except Exception`` —
the named set only, so a programming bug still surfaces.

The 5.2 vs 5.3 fence (AR6)
--------------------------
5.2 builds the STORE + read-side integrity→MISS. 5.3 builds ACTIVE invalidation (a
detector-set-hash change invalidates affected entries) + rejected-finding
key-busting. A detector-set edit ALREADY changes the 5.1 key → a different cache
slot → a NATURAL MISS (in scope here); the ACTIVE eviction machinery is NOT.

LOCAL-only (NFR-D1 / architecture §87)
--------------------------------------
The cache is local to the audited repo's ``.argus/cache/`` tree. No shared /
cross-machine / network cache (the G4 cross-run shared cache is V4). The verdict
is correct WHETHER OR NOT the cache exists / is warm / is wiped.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from argus.ledger.recording import Recording
from argus.store import canonical
from argus.store.envelope import EnvelopeWriter
from argus.store.paths import ApaaStorePaths
from argus.store.reader import ApaaStoreReader, StoreIntegrityError

__all__ = [
    "MEMO_STORE_SCHEMA_VERSION",
    "MEMO_STORE_PRODUCER",
    "RecordedResult",
    "MemoStore",
]

# Cached-payload schema version (additive-only; part of the hashed payload — a
# bump deliberately changes the content hash). Localized here, NOT shared with the
# Recording schema version (which is folded inside each recording).
MEMO_STORE_SCHEMA_VERSION = "1"

# Logical producer token recorded on the cache envelope (provenance).
MEMO_STORE_PRODUCER = "argus.cache.memo_store"

# The fixed ``.argus/`` sub-directory the memo store writes into (already created by
# ``ApaaStorePaths.ensure_tree`` — ``cache/`` is in ``ArgusAgent_SUBDIRS``).
_CACHE_SUBDIR = "cache"
_JSON_SUFFIX = ".json"
_RECORDINGS_KEY = "recordings"

# The recorded result the store persists/serves: the canonical Recording-set for
# one audit unit (the verdict-folded artifact, NOT raw source — the cached payload
# is already 2.5-producer-side-redacted; NFR-S1).
RecordedResult = tuple[Recording, ...]


class MemoStore:
    """Content-addressed memoization store over the contained ``.argus/cache/`` tree.

    Constructed with the audited-repo root (or an :class:`ApaaStorePaths`, mirroring
    :class:`ApaaStoreReader` / :class:`ApaaStoreWriter`). All containment delegates
    to :class:`ApaaStorePaths`; all serialization delegates to the single
    ``canonical`` serializer via the 1.3 writer / reader; the cache slot is keyed on
    the 5.1 cache KEY (the store CONSUMES ``derive_cache_key`` — it does not
    re-derive a key, AR5). FS I/O is confined here (AR8 — the IMPURE shell).
    """

    def __init__(self, repo_root: str | Path | ApaaStorePaths) -> None:
        self._paths = (
            repo_root if isinstance(repo_root, ApaaStorePaths) else ApaaStorePaths(repo_root)
        )
        self._reader = ApaaStoreReader(self._paths)

    @property
    def paths(self) -> ApaaStorePaths:
        return self._paths

    def _relative_for(self, key: str) -> str:
        # The cache slot is content-addressed by the 5.1 cache KEY (AR11) — never
        # arrival order. Containment is enforced by ``ApaaStorePaths`` at write/read.
        return f"{_CACHE_SUBDIR}/{key}{_JSON_SUFFIX}"

    @staticmethod
    def _to_payload(result: RecordedResult) -> dict[str, object]:
        # The cached payload is the canonical Recording-set (JSON-primitive mode so
        # the on-disk bytes are byte-identical to the recompute — HIT==MISS).
        return {
            "schema_version": MEMO_STORE_SCHEMA_VERSION,
            _RECORDINGS_KEY: [r.model_dump(mode="json") for r in result],
        }

    def store(self, key: str, result: RecordedResult) -> str:
        """Persist ``result`` under cache slot ``key`` (content-addressed); return the locator.

        Wraps the canonical Recording-set in the 1.1 envelope (``content_hash`` over
        the payload only, ``run_id`` / ``created_at`` EXCLUDED per NFR-D3 — so two
        stores of the same result address the SAME slot) and writes it via the 1.3
        :class:`ApaaStoreWriter`, containment-checked (NFR-S5). Idempotent:
        re-storing the same ``(key, result)`` overwrites byte-identically.

        Raises:
            WorkspaceContainmentError: if ``key`` resolves outside ``.argus/cache/``
                (raised by :class:`ApaaStorePaths` BEFORE any write).
            canonical.CanonicalSerializationError: a non-canonical payload (AR10).
            OSError: propagated on a write failure to a confined path (no
                fabricated locator, no silent partial).
        """
        relative = self._relative_for(key)
        payload = self._to_payload(result)
        # The cache slot is KEY-addressed (``cache/<key>.json``) so ``lookup(key)``
        # finds it by key (AR11). The bytes are the single-serializer canonical bytes
        # of the 1.1 envelope; the envelope ``content_hash`` is over the payload only
        # (NFR-D3), so two stores of the same result write byte-identical bytes
        # (idempotent overwrite). Containment is enforced by ``ensure_parent`` BEFORE
        # any write (NFR-S5) — an escaping key raises ``WorkspaceContainmentError``.
        envelope = EnvelopeWriter.build(
            payload,
            schema_version=MEMO_STORE_SCHEMA_VERSION,
            producer=MEMO_STORE_PRODUCER,
        )
        target = self._paths.ensure_parent(relative)
        target.write_bytes(canonical.dumps_bytes(envelope.model_dump()))
        return self._paths.to_locator(relative)

    def lookup(self, key: str) -> RecordedResult | None:
        """Return the recorded result for ``key`` (a cache HIT), or ``None`` (a MISS).

        Resolves the key-addressed slot containment-checked, reads + RE-VERIFIES the
        envelope ``content_hash`` (reusing the 1.3 ``read_envelope(verify_hash=True)``
        tamper guard), and validates the payload against the frozen Recording-set
        schema. On success returns the validated result (HIT == MISS byte-identity:
        round-tripping the same canonical bytes changes nothing). On ANY of the
        DN-MISS named typed failures — tamper / corrupt / wrong-schema / non-file /
        permission-denied / missing — returns ``None`` (a MISS → recompute path).
        Spends ZERO LLM tokens (NFR-D2). NEVER raises out of the store (a cache is
        advisory, AR10); NEVER serves a tampered / poisoned entry.
        """
        relative = self._relative_for(key)
        try:
            envelope = self._reader.read_envelope(relative, verify_hash=True)
            payload = envelope.payload
            recordings_raw = payload.get(_RECORDINGS_KEY)
            if not isinstance(recordings_raw, list):
                return None
            return tuple(Recording.model_validate(item) for item in recordings_raw)
        except (
            StoreIntegrityError,
            canonical.CanonicalSerializationError,
            ValidationError,
            FileNotFoundError,
            PermissionError,
            OSError,
        ):
            # The ONE place a typed store error is SWALLOWED into a MISS (a cache is
            # advisory; a poisoned entry must not break or mis-answer the audit).
            # The named set only — NO bare except, NO ``except Exception`` — so a
            # programming bug still surfaces. ``FileNotFoundError`` / ``PermissionError``
            # are ``OSError`` subclasses but named explicitly for documentation.
            return None
