"""Append-only, prev-hash-chained HITL decision-record writer (IMPURE shell).

Drivers: ArgusAgent-FR-24 (append-only decision record — each human STOP/PROCEED
decision is a NEW content-addressed artifact under ``.argus/decisions/`` whose
envelope ``prev_hash`` chains to the prior decision's ``content_hash``; the STOP is
logged even if the full human decision is deferred), ArgusAgent-NFR-A1 (schema-versioned,
content-hashed, prev-hash-chained, additive-only envelope — the append-only chain
REUSES the EXISTING 1.1 envelope chaining), ArgusAgent-NFR-S1 (a decision record carries
ONLY the decision / trigger provenance / finding-id / locator provenance /
decider-id token / content-derived decision-id — NEVER source bytes / a secret
value / an absolute host path; the returned locator is ``.argus/``-root-relative
POSIX, inherited from the writer), ArgusAgent-NFR-S5 (containment via the reused writer —
NO second containment check), ArgusAgent-AR4 (single canonical serializer — the record's
bytes are EXACTLY ``canonical.dumps_bytes(...)`` via the writer/envelope; NO second
``json.dumps`` / hasher), ArgusAgent-AR7 / §3.3 (REUSE ``ApaaStoreWriter.write_payload`` +
``EnvelopeWriter.build`` + the 1.1 canonical serializer + the reserved
``decisions/`` subdir + the 1.3 ``ApaaStoreReader`` — NO forked persistence),
ArgusAgent-AR8 (this is the IMPURE shell — the byte read (chain-head resolution) + the
byte write live here; the escalation RESOLUTION is the PURE :mod:`escalation`
gate), ArgusAgent-AR10 (typed failure — a malformed argument raises a typed, NAMED
:class:`DecisionRecordError`; a corrupt/foreign artifact in the decisions subdir is
SKIPPED during chain-head resolution, never a crash), ArgusAgent-AR11 (content-addressed
filename — ``decisions/<content_hash>.json``, never arrival order).

Verification area ArgusAgent-HITL (``TC-ArgusAgent-HITL-001-NN`` — index from -01).

DN-APPEND-ONLY — the chain is the ordered, tamper-evident append log
-------------------------------------------------------------------
Each decision is a NEW content-addressed ``.argus/decisions/<content_hash>.json``
whose envelope ``prev_hash`` chains to the PRIOR decision's ``content_hash`` (the
genesis sentinel ``"0"*64`` at the chain head). A prior decision is NEVER
mutated / overwritten / deleted (the §3.4 evidence-immutability + hash-chained-
ledger discipline). The chain is verified by reading it back through the EXISTING
``ApaaStoreReader`` (which re-verifies each ``content_hash`` → ``StoreIntegrityError``
on tamper).

DN-APPEND-ONLY-COLLISION (review iteration 1 fix) — fold the chain position in
------------------------------------------------------------------------------
The envelope ``content_hash`` covers the PAYLOAD ONLY (NFR-D3), and the on-disk
filename derives from it. So two byte-identical resolutions (the exact AC4
re-log-same-deferred-STOP case, or two audit runs of one repo) would hash to the
SAME ``decisions/<hash>.json`` — the second ``append()`` would OVERWRITE the first
(breaking AC3 "the prior decision is NEVER overwritten") and produce a self-cyclic
``prev_hash`` that makes chain-head resolution return the genesis sentinel,
orphaning the whole chain. The fix FOLDS the chain position (the resolved
``prev_hash``) INTO the hashed payload under :data:`CHAIN_PREV_HASH_KEY`, so each
chain link is a genuinely DISTINCT content-addressed artifact even for identical
resolutions and the prev-hash spine stays intact + non-cyclic + verifiable.

DN-STOP-LOGGED-DEFERRED (FR24) — the STOP is logged even if the record is deferred
----------------------------------------------------------------------------------
The writer takes an :class:`EscalationResolution`. A ``default_stop`` /
``timeout_parked_stop`` resolution (no human decision yet — the full human decision
is deferred) is STILL appended: the STOP itself is recorded at escalation time so
the audit trail never loses the fact that a STOP occurred. A LATER human decision
is a SUBSEQUENT append (append-only — never a mutation of the STOP record).

Scoping — the decision chain is producer-scoped
-----------------------------------------------
The ``decisions/`` subdir is SHARED (Story 5.3 also writes a fixed-name
``rejection_ledger.json`` rejection record there). To resolve the decision chain's
head deterministically, this writer reads ONLY the content-addressed
``<hex>.json`` artifacts whose envelope ``producer`` is :data:`DECISION_PRODUCER` —
so a foreign artifact (the rejection ledger, or any other decisions-subdir file)
can never be mistaken for a decision-record link.
"""

from __future__ import annotations

from pathlib import Path

from argus.governance.escalation import EscalationResolution
from argus.store.envelope import GENESIS_PREV_HASH
from argus.store.paths import ApaaStorePaths
from argus.store.reader import ApaaStoreReader
from argus.store.writer import ApaaStoreWriter

__all__ = [
    "CHAIN_PREV_HASH_KEY",
    "DECISION_PRODUCER",
    "DECISION_SCHEMA_VERSION",
    "DECISIONS_SUBDIR",
    "DecisionRecordError",
    "DecisionRecordWriter",
]

# The append-only decisions subdir (already reserved in store.paths.ArgusAgent_SUBDIRS).
DECISIONS_SUBDIR = "decisions"

# The persisted-payload key that folds the chain position (the prior decision's
# ``content_hash``, or the genesis sentinel at the head) INTO the hashed decision
# record. It makes each chain link a DISTINCT content-addressed artifact so two
# byte-identical resolutions never collide on one ``decisions/<hash>.json`` file
# (the append-only collision fix — review iteration 1). Its value is a 64-hex
# content_hash / genesis sentinel: a provenance token, never source/secret bytes.
CHAIN_PREV_HASH_KEY = "chain_prev_hash"

# The envelope ``producer`` for a HITL decision record — the scoping token that
# distinguishes a decision-record artifact from any other decisions-subdir file
# (e.g. the 5.3 rejection ledger).
DECISION_PRODUCER = "argus.hitl.decision_record"

# The envelope ``schema_version`` for a decision record (additive-only, NFR-A1).
DECISION_SCHEMA_VERSION = "1"

# A stored decision-record artifact filename is the 64-char sha256 hex content hash.
_HEX_LEN = 64
_JSON_SUFFIX = ".json"


class DecisionRecordError(ValueError):
    """Raised on a genuinely malformed argument to the decision-record writer (AR10).

    A ``ValueError`` subclass localized to this module (mirroring
    ``StoreIntegrityError`` / ``WorkspaceContainmentError`` / ``EscalationError``).
    Its message names the failing argument only — it carries NO source bytes
    (NFR-S1). A corrupt / foreign artifact encountered during chain-head resolution
    is SKIPPED (never raised) so a poisoned neighbouring file cannot break an
    append; only a structurally wrong ``resolution`` argument raises.
    """


class DecisionRecordWriter:
    """Append-only writer for HITL decision records over ``.argus/decisions/`` (FR24).

    Constructed with the audited-repo root (or an :class:`ApaaStorePaths` /
    :class:`ApaaStoreWriter`). COMPOSES the 1.3 ``ApaaStoreWriter.write_payload``
    (which wraps the payload in the 1.1 content-hashed, prev-hash-chained envelope
    and writes ``decisions/<content_hash>.json``) + the 1.3 ``ApaaStoreReader`` (for
    deterministic chain-head resolution). It authors NO second serializer / envelope
    / writer / containment check (§3.3 / AR7).
    """

    def __init__(self, repo_root: str | Path | ApaaStorePaths | ApaaStoreWriter) -> None:
        if isinstance(repo_root, ApaaStoreWriter):
            self._writer = repo_root
            self._paths = repo_root.paths
        else:
            self._paths = (
                repo_root
                if isinstance(repo_root, ApaaStorePaths)
                else ApaaStorePaths(repo_root)
            )
            self._writer = ApaaStoreWriter(self._paths)
        self._reader = ApaaStoreReader(self._paths)

    def append(self, resolution: EscalationResolution) -> str:
        """Append *resolution* as a NEW content-addressed, chained decision record (FR24).

        The record body is ``resolution.to_payload()`` (the secret-free canonical
        payload — decision / trigger provenance / decider-id token / content-derived
        decision-id, NFR-S1) PLUS the :data:`CHAIN_PREV_HASH_KEY` chain-position field
        set to the PRIOR decision's ``content_hash`` (the genesis sentinel for the
        chain head). Folding the chain position INTO the hashed payload is the
        append-only keystone (review iteration 1, DN-APPEND-ONLY-COLLISION): the
        envelope ``content_hash`` — and therefore the ``decisions/<content_hash>.json``
        filename — covers the payload only (NFR-D3), so WITHOUT this field two
        byte-identical resolutions (the exact AC4 re-log-same-deferred-STOP case, or
        two audit runs of one repo) would collide on the same filename and the second
        ``append()`` would OVERWRITE the first (AC3 "prior NEVER overwritten" broken)
        and produce a self-cyclic ``prev_hash`` that orphans the whole chain. With the
        chain position folded in, each link is a genuinely DISTINCT artifact and the
        prev-hash spine stays intact + verifiable. The envelope ``prev_hash`` still
        carries the SAME value (the redundancy is intentional — the payload copy makes
        the link distinct + reproducible; the envelope field is the read-side chain).
        Written via the reused ``ApaaStoreWriter.write_payload`` (AR7 — no forked
        persistence). Returns the ``.argus/``-root-relative POSIX locator.

        A ``default_stop`` / ``timeout_parked_stop`` resolution IS appended (the STOP
        is logged even when the full human decision is deferred — DN-STOP-LOGGED-
        DEFERRED / FR24). A prior decision is NEVER mutated (append-only).

        Raises:
            DecisionRecordError: ``resolution`` is not an
                :class:`EscalationResolution` (a typed failure, never a leak — AR10).
            WorkspaceContainmentError: inherited from the writer if the target
                escapes the ``.argus/`` root (never for the fixed ``decisions/``
                subdir — the containment is the reused writer's, NO second check).
        """
        if not isinstance(resolution, EscalationResolution):
            raise DecisionRecordError(
                f"resolution must be an EscalationResolution, got "
                f"{type(resolution).__name__!r}"
            )
        prev_hash = self._resolve_chain_head()
        # Fold the chain position into the HASHED payload so each chain link is a
        # DISTINCT content-addressed artifact even for byte-identical resolutions
        # (the append-only collision fix — the value is a 64-hex content_hash /
        # genesis sentinel, a provenance token, never source/secret bytes — NFR-S1).
        payload = {**resolution.to_payload(), CHAIN_PREV_HASH_KEY: prev_hash}
        return self._writer.write_payload(
            DECISIONS_SUBDIR,
            payload,
            schema_version=DECISION_SCHEMA_VERSION,
            producer=DECISION_PRODUCER,
            prev_hash=prev_hash,
        )

    def _resolve_chain_head(self) -> str:
        """Return the current chain head's ``content_hash`` (or the genesis sentinel).

        Reads the content-addressed ``decisions/<hex>.json`` artifacts whose envelope
        ``producer`` is :data:`DECISION_PRODUCER` (producer-scoped — a foreign
        artifact such as the 5.3 rejection ledger is IGNORED), then returns the
        content_hash of the chain TAIL — the decision whose ``content_hash`` is NOT
        the ``prev_hash`` of any OTHER decision. An empty chain returns the genesis
        sentinel. A corrupt / non-decision artifact is SKIPPED (never a crash —
        AR10). PURE-of-payload (a byte read only — no write, no clock, no id mint).
        """
        decisions_dir = self._paths.argus_root / DECISIONS_SUBDIR
        if not decisions_dir.is_dir():
            return GENESIS_PREV_HASH

        # Collect (content_hash, prev_hash) for every decision-record envelope.
        content_hashes: set[str] = set()
        prev_of: dict[str, str] = {}
        for path in sorted(decisions_dir.glob(f"*{_JSON_SUFFIX}")):
            stem = path.stem
            # Content-addressed decision records are named by their 64-hex content
            # hash; the fixed-name 5.3 rejection ledger (rejection_ledger.json) never
            # matches this shape and is skipped structurally.
            if len(stem) != _HEX_LEN or any(c not in "0123456789abcdef" for c in stem):
                continue
            relative = f"{DECISIONS_SUBDIR}/{path.name}"
            try:
                envelope = self._reader.read_envelope(relative)
            except (ValueError, OSError):
                # Corrupt / tampered / non-envelope / unreadable artifact → skip
                # (a poisoned neighbour must not break an append — AR10).
                continue
            if envelope.producer != DECISION_PRODUCER:
                continue
            content_hashes.add(envelope.content_hash)
            prev_of[envelope.content_hash] = envelope.prev_hash

        if not content_hashes:
            return GENESIS_PREV_HASH

        # The TAIL is the record whose content_hash is not any other record's
        # prev_hash. A well-formed append-only chain has exactly one such tail.
        referenced = {prev for prev in prev_of.values() if prev != GENESIS_PREV_HASH}
        tails = [h for h in content_hashes if h not in referenced]
        if len(tails) == 1:
            return tails[0]
        # Degenerate / forked chain (should not occur under append-only single-writer
        # use, but never crash): deterministically pick the lexicographically-max
        # tail so a repeated resolution is stable (AR4).
        if tails:
            return max(tails)
        # A pure cycle (no tail) — no safe head; genesis restarts the chain rather
        # than raising (AR10 degrade-never-raise). Structurally unreachable under
        # content-addressed, single-writer append.
        return GENESIS_PREV_HASH
