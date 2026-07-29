"""IMPURE AR6 cache-invalidation surface + the V1 rejected-finding SEAM.

Drivers: ArgusAgent-FR-27 (reproduce the same verdict for the same repo + ArgusAgent version —
invalidation is what keeps the reproduction from ossifying a WRONG answer),
ArgusAgent-NFR-D1 (LOCAL content-addressed memoization that INVALIDATES on a detector-set
change and BUSTS a rejected finding's key — the central AR6 driver, the second/
closing line of the "memoization caches errors → reproducibility ≠ correctness"
defense after the 5.2 read-side integrity→MISS), ArgusAgent-NFR-D2 (the bust path is
itself zero-LLM-token), ArgusAgent-NFR-D3 (the rejection record's content-hash excludes
the volatile ``run_id``/``created_at`` — the 1.1 envelope guarantee), ArgusAgent-NFR-P1
(a recompute after a bust round-trips byte-identically to a cold compute — the 5.2
HIT==MISS property is what makes an over-bust SAFE), ArgusAgent-AR4 (single serializer /
no float / no clock / no uuid / no random in the new record payload), ArgusAgent-AR5
(the surface CONSUMES ``derive_cache_key`` / ``detector_set_content_hash`` — it
NEVER re-derives a key), ArgusAgent-AR6 (THE driver — invalidate on detector-set change +
a human-rejected finding busts its own key), ArgusAgent-AR7 (REUSE the 1.3 containment
shell + the 5.2 store + typed errors by import — no fork), ArgusAgent-AR8 (this is the
IMPURE shell — FS DELETE + a redacted-record read are confined here; the new record
payload stays pure / clock-free), ArgusAgent-AR10 (typed degradation — a missing/
already-gone slot bust is a no-op; a permission-denied delete / a corrupt rejection
record degrades to a typed result / safe skip, never an uncaught raise / a
silently-wrong served result), ArgusAgent-NFR-S1/S5 (no source/secret bytes in the
rejection record — it cites ``recording_id`` + ``key`` + redacted metadata and
joins the 4.4 swept union; containment-checked bust/delete paths), ArgusAgent-NFR-M1
(≤1200-line files), ArgusAgent-AR11 (content-addressed filenames — the rejection ledger
is an envelope under ``decisions/`` keyed on its own content hash).

The keystone — the over-bust-safe / under-bust-forbidden asymmetry (AR6 / CC #2)
--------------------------------------------------------------------------------
Invalidation is the safety valve on the memoization optimization.

- **Under-bust is the failure to PREVENT.** After a finding is rejected (or the
  detector set changes) the affected cache entry MUST NOT be re-served — a re-run
  MUST re-compute. Serving the stale rejected finding is the exact AR6 failure
  ("else a false 🔴 is served forever"). The keystone test is RED-then-green: a
  NAIVE path that does NOT bust re-serves the stale 🔴; the busting surface forces
  a MISS → recompute.
- **Over-bust is SAFE (the correctness asymmetry).** Invalidating TOO MUCH —
  busting an entry that did not strictly need busting, or busting under a broader
  scope — is harmless: the next run re-computes and re-stores a result
  byte-identical to a cold compute (the 5.2 HIT==MISS property guarantees a
  recompute is correct). So **when in doubt, BUST.** A stale serve is never
  acceptable; an extra recompute always is. This surface prefers safe over-busting
  to risky under-busting.

Idempotent, containment-safe, leak-free, no-crash (AR8 / AR10 / NFR-S1/S5)
--------------------------------------------------------------------------
- Busting a key that is already absent (already-busted / never-stored) is a NO-OP
  (idempotent — a second bust changes nothing, never raises).
- A bust DELETE path resolves + containment-checks via :class:`ApaaStorePaths`
  (``Path.resolve()`` + ``is_relative_to`` — NEVER ``str.startswith``); a
  traversal / symlink / sibling-prefix key raises
  :class:`WorkspaceContainmentError` BEFORE any delete (NFR-S5).
- A bust DELETES a whole cache slot file (a delete, never a partial rewrite),
  leaving every OTHER cache entry + the surrounding ``.argus/`` tree intact.
- The bust path operates on KEYS + slot files, not payloads — no source/secret
  byte is read, logged, or emitted (NFR-S1).
- A permission-denied / OS error on a DELETE degrades to a typed
  :class:`BustOutcome` (``busted=False``, ``reason="os_error"``), never an
  uncaught raise (AR10).
- A corrupt / wrong-schema / non-UTF-8 / non-file / permission-denied
  :class:`RejectionLedger` read degrades to a safe skip (an empty ledger),
  never a crash (the DN-MISS no-crash discipline applied to the rejection seam —
  the NAMED typed set only; NO bare ``except``).

The V1 rejection SEAM (the live trigger is Epic-6)
--------------------------------------------------
A rejection is a SEPARATE frozen record that CITES a ``recording_id`` + the cache
``key`` it was served under + redacted metadata — NEVER a mutation of the
immutable :class:`Recording` (the schema has no ``rejected`` field; §3.4 evidence
immutability). The :class:`RejectionLedger` is an append-only read/persist surface
an Epic-6 Prosecutor (Story 6.4) / HITL (Story 6.7) caller POPULATES; this story
builds the record + ledger + the busting that CONSUMES it, NOT the live trigger.
An Epic-6 caller substitutes the live trigger ADDITIVELY (it appends a
:class:`RejectedFinding`; this surface consumes it unchanged) — mirroring the 5.1
``V1_MODEL_CHECKPOINT`` placeholder discipline.

LOCAL-only (NFR-D1 / architecture §87)
--------------------------------------
The cache + invalidation surface are local to the audited repo's ``.argus/`` tree.
No shared / cross-machine / network cache (the G4 cross-run shared cache is V4).
The verdict is correct WHETHER OR NOT invalidation has run (wipe + re-run → same
verdict).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from argus.cache.memo_store import MemoStore
from argus.store import canonical
from argus.store.paths import ApaaStorePaths
from argus.store.reader import ApaaStoreReader, StoreIntegrityError
from argus.store.writer import ApaaStoreWriter

__all__ = [
    "REJECTION_LEDGER_SCHEMA_VERSION",
    "REJECTION_LEDGER_PRODUCER",
    "REJECTION_LEDGER_RELATIVE",
    "RejectedFinding",
    "RejectionLedgerPayload",
    "RejectionLedger",
    "BustOutcome",
    "CacheInvalidator",
]

# Rejection-record / ledger schema version (additive-only; part of the hashed
# payload — a bump deliberately changes the ledger content hash).
REJECTION_LEDGER_SCHEMA_VERSION = "1"

# Logical producer token recorded on the rejection-ledger envelope (provenance).
REJECTION_LEDGER_PRODUCER = "argus.cache.invalidation.rejection_ledger"

# The fixed ``.argus/`` slot the V1 rejection ledger persists into. ``decisions/``
# is in ``ArgusAgent_SUBDIRS`` (a rejection is a governance decision, not a cache slot).
# A single fixed-name ledger file (not content-addressed) so an Epic-6 caller can
# read-append-rewrite the append-only set deterministically.
_DECISIONS_SUBDIR = "decisions"
_JSON_SUFFIX = ".json"
REJECTION_LEDGER_RELATIVE = f"{_DECISIONS_SUBDIR}/rejection_ledger{_JSON_SUFFIX}"

_REJECTIONS_KEY = "rejections"


class RejectedFinding(BaseModel):
    """A frozen V1 record that a finding was human-rejected (DN-REJECTION-SEAM).

    CITES the rejected finding by ``recording_id`` + the cache ``key`` it was
    served under + redacted provenance/metadata — NEVER a mutation of the
    immutable :class:`Recording` (§3.4 evidence immutability; the Recording schema
    carries no ``rejected`` field). Carries NO source/secret bytes (NFR-S1): only
    ids, the cache key, a rule/cartridge provenance token, and an OPTIONAL redacted
    reason / actor token. Pure / clock-free (AR4): no float, no ``uuid4``, no
    wall-clock, no ``random`` — the envelope's volatile ``run_id``/``created_at``
    (EXCLUDED from the content-hash per NFR-D3) carry any timestamp, never this
    record.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    recording_id: str = Field(
        ..., min_length=1, description="The rejected finding's recording/finding id (cited, not mutated)."
    )
    key: str = Field(
        ..., min_length=1, description="The 5.1 cache key the rejected finding was served under (the slot to bust)."
    )
    rule_id: str | None = Field(
        default=None, description="Detector rule provenance id of the rejected finding (optional)."
    )
    cartridge_id: str | None = Field(
        default=None, description="Defect-cartridge provenance id (optional)."
    )
    reason: str | None = Field(
        default=None, description="OPTIONAL redacted rejection reason token (NO source/secret bytes — NFR-S1)."
    )
    rejected_by: str | None = Field(
        default=None, description="OPTIONAL redacted actor token (role/id, NOT a credential — NFR-S1)."
    )


class RejectionLedgerPayload(BaseModel):
    """The frozen append-only rejection-ledger payload (the envelope body).

    A schema-versioned wrapper around the ordered tuple of :class:`RejectedFinding`
    records an Epic-6 caller appends. Frozen + ``extra="forbid"`` (the 1.1/1.2
    precedent). The content-hash is taken over THIS payload only (NFR-D3).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=REJECTION_LEDGER_SCHEMA_VERSION, description="Rejection-ledger schema version (part of the hash)."
    )
    rejections: tuple[RejectedFinding, ...] = Field(
        default=(), description="Append-only ordered set of rejection records."
    )


class RejectionLedger:
    """IMPURE append-only read/persist surface for the V1 rejection seam.

    Constructed with the audited-repo root (or an :class:`ApaaStorePaths`,
    mirroring :class:`MemoStore` / :class:`ApaaStoreReader`). REUSES the 1.3
    :class:`ApaaStoreWriter` (content-addressed envelope) for the persist and the
    1.3 :class:`ApaaStoreReader` (``read_envelope(verify_hash=True)`` tamper guard)
    for the read. The SEAM an Epic-6 Prosecutor (6.4) / HITL (6.7) caller
    populates: it APPENDS records; the :class:`CacheInvalidator` consumes them
    unchanged. FS I/O is confined here (AR8 — the IMPURE shell).
    """

    def __init__(self, repo_root: str | Path | ApaaStorePaths) -> None:
        self._paths = (
            repo_root if isinstance(repo_root, ApaaStorePaths) else ApaaStorePaths(repo_root)
        )
        self._reader = ApaaStoreReader(self._paths)
        self._writer = ApaaStoreWriter(self._paths)

    @property
    def paths(self) -> ApaaStorePaths:
        return self._paths

    def read(self) -> tuple[RejectedFinding, ...]:
        """Read the persisted rejection records, or an EMPTY tuple (DN-MISS / AR10).

        Reads + RE-VERIFIES the envelope ``content_hash`` (reusing the 1.3 tamper
        guard) and validates the payload against the frozen schema. On ANY of the
        named typed failures — tamper / corrupt / non-UTF-8 / wrong-schema /
        non-file / permission-denied / missing — degrades to an EMPTY ledger (a
        safe skip), NEVER a crash and NEVER a silently-wrong served record. Spends
        ZERO LLM tokens. Reads only the redacted records (no source/secret bytes).
        """
        try:
            envelope = self._reader.read_envelope(
                REJECTION_LEDGER_RELATIVE, verify_hash=True
            )
            payload = RejectionLedgerPayload.model_validate(envelope.payload)
            return payload.rejections
        except (
            StoreIntegrityError,
            canonical.CanonicalSerializationError,
            ValidationError,
            FileNotFoundError,
            PermissionError,
            OSError,
        ):
            # The DN-MISS swallow set (the AR10 no-crash discipline on the rejection
            # seam read): a corrupt / tampered / wrong-schema / unreadable / missing
            # ledger degrades to an EMPTY set (a cache invalidation over zero records
            # is a safe no-op; a poisoned ledger must not break or mis-answer the
            # audit). The NAMED set only — NO bare except, NO ``except Exception`` —
            # so a programming bug still surfaces. ``FileNotFoundError`` /
            # ``PermissionError`` are ``OSError`` subclasses but named for clarity.
            return ()

    def append(self, record: RejectedFinding) -> str:
        """Append ONE :class:`RejectedFinding`, persist the ledger, return the locator.

        Reads the current records (degrading a corrupt read to empty per
        :meth:`read`), appends ``record``, wraps the new payload in the 1.1
        envelope (content-hash over the payload only, NFR-D3) and writes it via the
        1.3 :class:`ApaaStoreWriter`, containment-checked (NFR-S5). The fixed-name
        slot is overwritten with the new append-only set (the prior records are
        preserved + the new one added). Idempotent re-append of an identical record
        is permitted (the seam is V1; de-dup is an Epic-6 caller concern).
        """
        existing = self.read()
        payload = RejectionLedgerPayload(
            schema_version=REJECTION_LEDGER_SCHEMA_VERSION,
            rejections=(*existing, record),
        )
        return self._write(payload)

    def write_all(self, records: tuple[RejectedFinding, ...]) -> str:
        """Persist an explicit append-only record set (the Epic-6 populate seam)."""
        payload = RejectionLedgerPayload(
            schema_version=REJECTION_LEDGER_SCHEMA_VERSION, rejections=records
        )
        return self._write(payload)

    def _write(self, payload: RejectionLedgerPayload) -> str:
        # The ledger lives at a FIXED ``decisions/rejection_ledger.json`` slot (not
        # content-addressed) so a caller can read-append-rewrite the append-only set
        # deterministically. The writer's content-addressed filename is bypassed by
        # writing through the fixed relative path; the bytes are still the single
        # canonical serializer's bytes of the 1.1 envelope (no second serializer).
        from argus.store.envelope import EnvelopeWriter

        envelope = EnvelopeWriter.build(
            payload.model_dump(mode="json"),
            schema_version=REJECTION_LEDGER_SCHEMA_VERSION,
            producer=REJECTION_LEDGER_PRODUCER,
        )
        target = self._paths.ensure_parent(REJECTION_LEDGER_RELATIVE)
        target.write_bytes(canonical.dumps_bytes(envelope.model_dump()))
        return self._paths.to_locator(REJECTION_LEDGER_RELATIVE)


class BustOutcome(BaseModel):
    """A typed result of a single bust — never a bare bool (AR10).

    ``busted`` is True iff a slot file was actually deleted; ``locator`` is the
    ``.argus/``-root-relative POSIX locator of the targeted slot; ``reason`` is a
    machine token explaining the outcome (``"deleted"`` / ``"absent"`` /
    ``"os_error"`` / ``"no_change"``). A permission-denied / OS error on the DELETE
    is a RECORDED outcome (``busted=False, reason="os_error"``), NOT a crash —
    so the surface NEVER raises out on a benign delete edge.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    busted: bool = Field(..., description="True iff a cache slot file was actually deleted.")
    key: str = Field(..., min_length=1, description="The cache key targeted by the bust.")
    locator: str = Field(
        ..., min_length=1, description="The .argus/-root-relative POSIX locator of the targeted slot."
    )
    reason: str = Field(
        ..., min_length=1, description="Outcome token: deleted | absent | os_error | no_change."
    )


_CACHE_SUBDIR = "cache"


class CacheInvalidator:
    """IMPURE AR6 cache-invalidation surface — busts cache slots, consumes the seam.

    Constructed with the audited-repo root (or an :class:`ApaaStorePaths`) + a
    :class:`MemoStore` (the 5.2 store whose ``cache/<key>.json`` slot convention it
    busts). It CONSUMES ``derive_cache_key`` / ``detector_set_content_hash`` (via
    the keys it is handed) — it NEVER re-derives a key (AR5). Containment delegates
    to :class:`ApaaStorePaths`; serialization (for the rejection seam) delegates to
    the single ``canonical`` serializer via the 1.3 reader/writer. FS DELETE +
    rejection-seam read are confined here (AR8 — the IMPURE shell).
    """

    def __init__(
        self,
        repo_root: str | Path | ApaaStorePaths,
        store: MemoStore,
        *,
        rejection_ledger: RejectionLedger | None = None,
    ) -> None:
        self._paths = (
            repo_root if isinstance(repo_root, ApaaStorePaths) else ApaaStorePaths(repo_root)
        )
        self._store = store
        self._ledger = (
            rejection_ledger if rejection_ledger is not None else RejectionLedger(self._paths)
        )

    @property
    def paths(self) -> ApaaStorePaths:
        return self._paths

    @property
    def store(self) -> MemoStore:
        return self._store

    @property
    def rejection_ledger(self) -> RejectionLedger:
        return self._ledger

    def _relative_for(self, key: str) -> str:
        # The SAME slot convention as ``MemoStore`` (AR5/AR7 — no fork). Containment
        # is enforced by ``ApaaStorePaths.resolve`` at bust time (NFR-S5).
        return f"{_CACHE_SUBDIR}/{key}{_JSON_SUFFIX}"

    def bust_key(self, key: str) -> BustOutcome:
        """Delete the ``cache/<key>.json`` slot, containment-checked + idempotent.

        Resolves the slot via :class:`ApaaStorePaths` (``Path.resolve()`` +
        ``is_relative_to`` — a traversal/symlink/sibling-prefix key raises
        :class:`WorkspaceContainmentError` BEFORE any delete, NFR-S5). DELETES the
        whole slot file (a delete, never a partial rewrite), leaving every OTHER
        slot + the ``.argus/`` tree intact. Idempotent: a missing/already-gone slot
        is ``BustOutcome(busted=False, reason="absent")``, NOT a raise. A
        permission-denied / OS error on the delete degrades to
        ``BustOutcome(busted=False, reason="os_error")`` (AR10), never an uncaught
        raise. Spends ZERO LLM tokens; reads no payload byte.

        Raises:
            WorkspaceContainmentError: if ``key`` resolves outside ``.argus/cache/``
                (raised by :class:`ApaaStorePaths` BEFORE any delete — the
                CONTAINMENT failure is loud by design, NOT swallowed: an escaping
                key is a programming bug / attack, not a benign delete edge).
        """
        relative = self._relative_for(key)
        # Containment check FIRST (raises WorkspaceContainmentError on an escape,
        # BEFORE any FS mutation). This is deliberately NOT swallowed — an escaping
        # key is not a benign edge (NFR-S5 / AR10 named-set discipline).
        target = self._paths.resolve(relative)
        locator = self._paths.to_locator(relative)
        try:
            if not target.is_file():
                # Idempotent no-op: never stored / already busted (a directory at the
                # path is also "no slot file to bust" — leave it untouched).
                return BustOutcome(
                    busted=False, key=key, locator=locator, reason="absent"
                )
            target.unlink()
            return BustOutcome(busted=True, key=key, locator=locator, reason="deleted")
        except (PermissionError, OSError):
            # A permission-denied / OS error on the DELETE degrades to a typed
            # outcome (AR10 no-crash on the DELETE edge) — NEVER an uncaught raise.
            # The NAMED set only (no bare except). ``PermissionError`` is an
            # ``OSError`` subclass, named for clarity.
            return BustOutcome(
                busted=False, key=key, locator=locator, reason="os_error"
            )

    def bust_rejected_finding(self, record: RejectedFinding) -> BustOutcome:
        """Bust the cache slot a rejected finding was served under (AR6 / AC1).

        Busts ``record.key`` (the cache slot the false 🔴 was served under) so a
        subsequent :meth:`MemoStore.lookup` returns a MISS → recompute — the
        rejected finding is NOT re-served. Spends ZERO LLM tokens (NFR-D2);
        operates on the redacted ``record`` + the slot file, never a source/secret
        byte (NFR-S1); containment-checked (NFR-S5). Idempotent + no-crash via
        :meth:`bust_key`.
        """
        return self.bust_key(record.key)

    def invalidate_rejections(self) -> tuple[BustOutcome, ...]:
        """Bust every cache slot named by the persisted rejection ledger (AR6).

        Reads the V1 :class:`RejectionLedger` (degrading a corrupt/missing read to
        an EMPTY set — a safe no-op, AR10) and busts each record's ``key``. The
        Epic-6 Prosecutor/HITL trigger POPULATES the ledger; this consumes it
        unchanged. Returns one :class:`BustOutcome` per record (in ledger order).
        An empty ledger → an empty result (no-op).
        """
        records = self._ledger.read()
        return tuple(self.bust_rejected_finding(record) for record in records)

    def invalidate_on_detector_set_change(
        self,
        old_hash: str,
        new_hash: str,
        *,
        known_keys: tuple[str, ...],
    ) -> tuple[BustOutcome, ...]:
        """Delete the orphaned OLD-detector-set-hash cache entries (AR6 / AC2 — active half).

        The 5.1 key already folds the detector-set content-hash, so a detector-set
        edit ALREADY derives a DIFFERENT key → a different slot → a NATURAL MISS
        (the new run never reads the stale OLD-hash entry). This is the ACTIVE half
        AR6 names: it DELETES the now-orphaned OLD-hash entries (passed as
        ``known_keys`` — the deterministic, containment-safe set the caller knows
        were derived under ``old_hash``) so the cache tree does not accumulate
        dead, never-again-reachable slots.

        ``known_keys`` are the cache keys derived under the OLD detector-set hash
        (the caller knows them — e.g. from its own per-unit key derivation under the
        old set). Each is busted via :meth:`bust_key` (containment-checked,
        idempotent, no-crash). A no-change (``old_hash == new_hash``) is a NO-OP
        (returns an empty tuple — busting on no change would be a pointless
        over-bust). When uncertain, over-busting is SAFE (the next run re-computes a
        byte-identical result — the 5.2 HIT==MISS property); under-busting (leaving
        a stale slot reachable) is the failure to avoid.

        Returns one :class:`BustOutcome` per busted key (in ``known_keys`` order).
        """
        if old_hash == new_hash:
            return ()
        return tuple(self.bust_key(key) for key in known_keys)
