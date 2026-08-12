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

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from argus.cache.key import V1_MODEL_CHECKPOINT, V1_PROMPT_TEMPLATE_VERSION
from argus.ledger.coverage_ledger import CoverageLedgerEntry
from argus.ledger.critical_subsystems import CriticalCandidate
from argus.ledger.recording import Recording
from argus.store import canonical
from argus.store.envelope import EnvelopeWriter
from argus.store.paths import ApaaStorePaths
from argus.store.reader import ApaaStoreReader, StoreIntegrityError

__all__ = [
    "MEMO_STORE_SCHEMA_VERSION",
    "MEMO_STORE_PRODUCER",
    "LLM_DERIVED_RULE_PREFIXES",
    "DeepMemoizationFenceError",
    "RecordedResult",
    "RecordedStageResult",
    "MemoStore",
]

# Cached-payload schema version (additive-only; part of the hashed payload — a
# bump deliberately changes the content hash). Localized here, NOT shared with the
# Recording schema version (which is folded inside each recording).
#
# Bumped "1" → "2" (story 12.3, DN-2). The memoized payload was findings-only
# (:data:`RecordedResult`), but the stage this story memoizes — the deterministic
# per-file detect/grade pass — returns THREE things from ONE loop: ledger entries,
# findings and critical candidates. Memoizing only the findings would have re-run that
# same loop to recover the other two, so the cache would have saved NOTHING while every
# byte-identity test still passed: a provably useless cache, undetectably so. The wider
# payload (:class:`RecordedStageResult`) is what makes the hit real.
#
# The bump is sanctioned by this constant's own additive-only contract — a bump
# DELIBERATELY changes the content hash — and it cost ZERO at this commit and only at
# this commit: measured 2026-08-13, `.argus/cache/` holds 0 persisted entries, so there
# was nothing to migrate. It is NOT the cache KEY schema (`CACHE_KEY_SCHEMA_VERSION`
# stays "3" — story 10.2 paid that cost so 12.3 would not have to) and NOT the
# `Recording` schema. :meth:`MemoStore.lookup_stage` REFUSES a payload written under a
# different value, so an old-shape entry degrades to a MISS rather than being served.
MEMO_STORE_SCHEMA_VERSION = "2"

# Logical producer token recorded on the cache envelope (provenance).
MEMO_STORE_PRODUCER = "argus.cache.memo_store"

# The fixed ``.argus/`` sub-directory the memo store writes into (already created by
# ``ApaaStorePaths.ensure_tree`` — ``cache/`` is in ``ArgusAgent_SUBDIRS``).
_CACHE_SUBDIR = "cache"
_JSON_SUFFIX = ".json"
_RECORDINGS_KEY = "recordings"
_SCHEMA_KEY = "schema_version"
_ENTRIES_KEY = "entries"
_FINDINGS_KEY = "findings"
_CANDIDATES_KEY = "candidates"

# THE AC6.1 FENCE — rule-id prefixes that identify an LLM-DERIVED recording.
#
# The Story 12.2 deep pass is the only producer in the package that can put an
# LLM-influenced row into a finding set, and every recording it mints carries
# ``deep_pass.RULE_DEGRADED_DEEP_READ`` as its rule-id stem. That constant is NOT
# imported here on purpose: ``argus.audit.deep_pass`` pulls the dispatch surface, and
# nothing may drag it onto the memoization path (NFR-S6). The literal is instead pinned
# against the live constant by ``TC-ArgusAgent-CACHE-001-90``, so the two cannot drift
# apart silently.
LLM_DERIVED_RULE_PREFIXES: tuple[str, ...] = ("deep_pass_degraded",)


class DeepMemoizationFenceError(RuntimeError):
    """Raised when an LLM-derived recording would enter a memoized payload (§D.3 / AC6.1).

    NOT an ``AR10`` degradation and deliberately NOT swallowed into a MISS: a MISS would
    hide the defect behind a correct-looking run, and this is a programming error at a
    call site, not a damaged cache entry. It is the one failure this module refuses to
    absorb.
    """


def _fence_llm_derived(
    findings: tuple[Recording, ...], *, model_checkpoint: str, prompt_template_version: str
) -> None:
    """Refuse to memoize LLM-derived recordings under the V1 PLACEHOLDER closure (AC6.1).

    THE HAZARD THIS MAKES IMPOSSIBLE, stated because a future reader will otherwise
    reasonably think this fence is over-cautious. The 5.1 cache key folds
    ``model_checkpoint`` and ``prompt_template_version``, but in V1 both are FIXED
    SENTINELS (``V1_MODEL_CHECKPOINT`` / ``V1_PROMPT_TEMPLATE_VERSION``) — they do not
    vary with the model a run actually used. The deep pass, meanwhile, dispatches under
    ``DEEP_PROMPT_TEMPLATE_VERSION`` to whatever model ``ARGUS_LLM_MODEL`` /
    ``OLLAMA_MODEL`` resolves, and NEITHER value reaches the key. So if deep-pass output
    were memoized under this key as it stands, **two runs against two different models
    would collide on one cache slot**, and the store would serve a result computed under
    model A to a run that asked for model B. ``cache/key.py`` exists precisely to make
    that impossible: *"a memoization cache hit may ONLY ever return a result produced by
    an IDENTICAL recording-producing closure."*

    The fence is therefore CONDITIONAL on the placeholder, not absolute: once Story 6.1
    substitutes a real captured checkpoint and a real prompt-template version into the
    closure, the key TELLS the two models apart and this guard stands down by itself. It
    fences a key that cannot yet discriminate — it does not forbid deep memoization
    forever.
    """
    placeholder = (
        model_checkpoint == V1_MODEL_CHECKPOINT
        and prompt_template_version == V1_PROMPT_TEMPLATE_VERSION
    )
    if not placeholder:
        return
    offenders = sorted(
        {
            finding.rule_id
            for finding in findings
            if any(finding.rule_id.startswith(p) for p in LLM_DERIVED_RULE_PREFIXES)
        }
    )
    if not offenders:
        return
    raise DeepMemoizationFenceError(
        "REFUSED: an LLM-derived recording may not enter a memoized payload while the "
        f"recording-producing closure carries the V1 PLACEHOLDER checkpoint. Offending "
        f"rule_id(s): {offenders}. The cache key's model_checkpoint is the fixed sentinel "
        f"{V1_MODEL_CHECKPOINT!r} and its prompt_template_version is "
        f"{V1_PROMPT_TEMPLATE_VERSION!r}, so the key DOES NOT VARY WITH THE MODEL THAT "
        "PRODUCED THIS RESULT — two runs against two different models would COLLIDE ON "
        "ONE CACHE SLOT and the store would serve a result computed under model A to a "
        "run that asked for model B. Memoizing the deep pass honestly requires folding "
        "the CAPTURED checkpoint and a real prompt-template version into the closure "
        "(argus/audit/deep_audit.py::build_closure_from_recording plus a claim grammar); "
        "see DF-12-3-A and DF-12-2-D. Do not silence this by widening the payload."
    )


class RecordedStageResult(BaseModel):
    """The memoized payload: the WHOLE output of one deterministic detect/grade stage.

    Frozen + ``extra="forbid"`` (the 1.1/1.2 precedent). Carries all THREE products of
    the single per-file loop, because they are produced together and recomputing any one
    of them re-runs the loop that produces the other two — see the
    ``MEMO_STORE_SCHEMA_VERSION`` note on why a findings-only payload is a cache that
    saves nothing.

    Every member is an EXISTING frozen model, reused verbatim (AR7): the payload
    introduces no parallel entry / finding / candidate schema, and each element is
    already producer-side redacted, so the containment properties of the recordings
    (NFR-S1) carry into the cache artifact unchanged.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    entries: tuple[CoverageLedgerEntry, ...] = Field(
        default=(), description="Per-file coverage ledger entries the stage graded (FR5/FR6)."
    )
    findings: tuple[Recording, ...] = Field(
        default=(), description="Recordings the stage's detectors emitted, in emission order."
    )
    candidates: tuple[CriticalCandidate, ...] = Field(
        default=(), description="FR4 critical candidates the stage assessed."
    )

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

    # ─────────────────────────────────────────────────────────────────────────
    # Story 12.3 — the STAGE payload (entries + findings + candidates)
    # ─────────────────────────────────────────────────────────────────────────
    #
    # Added ALONGSIDE store/lookup rather than replacing them: the findings-only pair is
    # the 5.2 library contract that `tests/test_memo_store.py` and
    # `tests/test_cache_invalidation.py` pin, and this story has no mandate to move it.
    # The two payload shapes use DISJOINT keys ("recordings" vs "entries"/"findings"/
    # "candidates"), so neither reader can half-decode the other's slot: `lookup` over a
    # stage slot finds no "recordings" list and misses, which is the correct answer.

    def store_stage(
        self,
        key: str,
        result: RecordedStageResult,
        *,
        model_checkpoint: str,
        prompt_template_version: str,
    ) -> str:
        """Persist a whole detect/grade stage result under slot ``key``; return the locator.

        The checkpoint arguments are REQUIRED and are not decoration: they are the
        closure slots the caller derived its key under, and passing them is what lets
        this write path enforce the AC6.1 deep-memoization fence at the choke point.
        Making them optional would leave the fence advisory — a caller could memoize
        LLM-derived output simply by not mentioning the model it ran under, which is the
        exact silence the fence exists to break.

        Raises:
            DeepMemoizationFenceError: an LLM-derived recording under the V1 placeholder
                closure (see :func:`_fence_llm_derived` — the model-collision hazard).
            WorkspaceContainmentError: ``key`` resolves outside ``.argus/cache/``.
            canonical.CanonicalSerializationError: a non-canonical payload (AR10).
            OSError: propagated on a write failure to a confined path.
        """
        _fence_llm_derived(
            result.findings,
            model_checkpoint=model_checkpoint,
            prompt_template_version=prompt_template_version,
        )
        payload = {
            _SCHEMA_KEY: MEMO_STORE_SCHEMA_VERSION,
            _ENTRIES_KEY: [e.model_dump(mode="json") for e in result.entries],
            _FINDINGS_KEY: [f.model_dump(mode="json") for f in result.findings],
            _CANDIDATES_KEY: [c.model_dump(mode="json") for c in result.candidates],
        }
        envelope = EnvelopeWriter.build(
            payload,
            schema_version=MEMO_STORE_SCHEMA_VERSION,
            producer=MEMO_STORE_PRODUCER,
        )
        target = self._paths.ensure_parent(self._relative_for(key))
        target.write_bytes(canonical.dumps_bytes(envelope.model_dump()))
        return self._paths.to_locator(self._relative_for(key))

    def lookup_stage(self, key: str) -> RecordedStageResult | None:
        """Return the recorded stage result for ``key`` (a HIT), or ``None`` (a MISS).

        Same DN-MISS taxonomy as :meth:`lookup` — tamper / corrupt / wrong-schema /
        non-file / permission-denied / missing all degrade to a MISS and NEVER raise out
        of the store — plus ONE additional refusal that :meth:`lookup` has no equivalent
        of: a payload whose ``schema_version`` is not the CURRENT
        ``MEMO_STORE_SCHEMA_VERSION`` is a MISS.

        That refusal is load-bearing and is not implied by the tamper guard. The envelope
        ``content_hash`` is recomputed from the payload it is stored with, so an entry
        written under the OLD payload shape verifies against itself perfectly — the hash
        proves the bytes were not edited, never that they mean what this version thinks
        they mean. Without the explicit check, a schema bump would move the hash for
        FUTURE writes while old-shape entries kept being served: the "memoization caches
        errors" failure arriving through the very lever meant to prevent it.
        """
        relative = self._relative_for(key)
        try:
            envelope = self._reader.read_envelope(relative, verify_hash=True)
            payload = envelope.payload
            if payload.get(_SCHEMA_KEY) != MEMO_STORE_SCHEMA_VERSION:
                return None
            raw = {
                name: payload.get(name)
                for name in (_ENTRIES_KEY, _FINDINGS_KEY, _CANDIDATES_KEY)
            }
            if not all(isinstance(value, list) for value in raw.values()):
                return None
            return RecordedStageResult.model_validate(raw)
        except (
            StoreIntegrityError,
            canonical.CanonicalSerializationError,
            ValidationError,
            FileNotFoundError,
            PermissionError,
            OSError,
        ):
            return None
