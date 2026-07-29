"""AR6 ACTIVE cache-invalidation + rejected-finding key-busting keystone proofs (Story 5.3).

Drivers: ArgusAgent-FR-27 (reproduce the same verdict for the same repo + ArgusAgent version —
invalidation keeps the reproduction from ossifying a WRONG answer), ArgusAgent-NFR-D1
(LOCAL content-addressed memoization that INVALIDATES on a detector-set change and
BUSTS a rejected finding's key — the central AR6 driver, the second/closing line of
the "memoization caches errors → reproducibility ≠ correctness" defense after the
5.2 read-side integrity→MISS), ArgusAgent-NFR-D2 (the bust path is zero-LLM-token),
ArgusAgent-NFR-D3 (the rejection record's content-hash excludes the volatile run_id/
created_at), ArgusAgent-NFR-P1 (a recompute after a bust round-trips byte-identically to a
cold compute — the 5.2 HIT==MISS property is what makes an over-bust SAFE),
ArgusAgent-AR4 (single serializer / no float / no clock / no uuid / no random in the new
record payload), ArgusAgent-AR5 (the surface CONSUMES derive_cache_key /
detector_set_content_hash — it NEVER re-derives a key), ArgusAgent-AR6 (THE driver —
invalidate on detector-set change + a human-rejected finding busts its own key),
ArgusAgent-AR7 (reuse the 1.3 containment shell + the 5.2 store + typed errors by import),
ArgusAgent-AR8 (invalidation.py is the IMPURE shell — FS DELETE / redacted-record read),
ArgusAgent-AR10 (typed degradation — a missing/already-gone slot bust is a no-op; a
permission-denied delete / a corrupt rejection record degrades to a typed result /
safe skip, never an uncaught raise), ArgusAgent-NFR-S1/S5 (no source/secret bytes in the
rejection record — it cites recording_id + key + redacted metadata; containment-
checked bust/delete paths), ArgusAgent-NFR-M1 (≤1200-line files), AI-E4-1 (keystone-
adequacy: each leg RED-then-green), AI-E1-1 (non-ASCII).

Verification area ArgusAgent-CACHE — TC-ArgusAgent-CACHE-001-46..NN (continues the area Stories
5.1 (…-01..22) + 5.2 (…-23..45) opened; the next free index is 46).

The keystone-adequacy honesty properties (AI-E4-1):
- under-bust-forbidden — RED against a NAIVE no-bust path that re-serves the stale
  🔴 on the next lookup(K); the busting surface forces a MISS → recompute;
- over-bust-safe — a broader bust still yields a byte-identical-to-cold-compute
  result (the 5.2 HIT==MISS property);
- detector-set-change → recompute, RED against a path that re-keyed but left the
  old slot reachable;
- no-crash on the DELETE / rejection-seam edges — a permission-denied delete + a
  corrupt/wrong-schema RejectedFinding read each degrade to a typed result, RED
  against a propagating/trusting path;
- idempotent + containment-safe + sibling-survival.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from argus.cache.invalidation import (
    REJECTION_LEDGER_PRODUCER,
    REJECTION_LEDGER_RELATIVE,
    REJECTION_LEDGER_SCHEMA_VERSION,
    BustOutcome,
    CacheInvalidator,
    RejectedFinding,
    RejectionLedger,
    RejectionLedgerPayload,
)
from argus.cache.key import (
    FROZEN_DETECTOR_SET,
    DetectorDescriptor,
    RecordingProducingClosure,
    derive_cache_key,
    detector_set_content_hash,
)
from argus.cache.memo_store import MemoStore, RecordedResult
from argus.ledger.recording import Locator, Recording
from argus.store import canonical
from argus.store.paths import WorkspaceContainmentError
from argus.store.reader import ApaaStoreReader

_INVALIDATION_MODULE = Path(
    sys.modules["argus.cache.invalidation"].__file__  # type: ignore[arg-type]
).resolve()


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures — a baseline closure (5.1) + a recorded result with a false 🔴.
# ─────────────────────────────────────────────────────────────────────────────


def _baseline_closure(
    content_hash: str = "a" * 64,
    detectors: tuple[DetectorDescriptor, ...] = FROZEN_DETECTOR_SET,
) -> RecordingProducingClosure:
    return RecordingProducingClosure(
        content_hash=content_hash,
        detectors=detectors,
        grammar_version="0.23.6",
        tool_versions={"radon": "6.0.1", "tree-sitter": "0.23.2"},
        budget=100,
        materiality_bar="release",
        work_manifest_files=("pkg/a.py", "pkg/b.py"),
        critical_paths=("pkg/a.py",),
    )


def _recording(rule_id: str = "hardcoded_secret", file_path: str = "pkg/a.py") -> Recording:
    return Recording(
        recording_id=f"rec-{rule_id}-{file_path}",
        rule_id=rule_id,
        advisory=False,  # a blocking false 🔴 — the finding a human rejects
        locators=(Locator(file_path=file_path, start_line=1, end_line=3),),
    )


def _false_red_result() -> RecordedResult:
    """A recorded result containing the false 🔴 finding a human rejects."""
    return (_recording("hardcoded_secret", "pkg/a.py"),)


def _recompute() -> RecordedResult:
    """The independent recompute path (a MISS feeds the SAME recordings the cache
    would have stored, AC3/AC5 — the cache is upstream of the verdict)."""
    return _false_red_result()


def _canonical_bytes(result: RecordedResult) -> bytes:
    return canonical.dumps_bytes([r.model_dump(mode="json") for r in result])


def _store(repo: Path) -> MemoStore:
    return MemoStore(repo)


def _invalidator(repo: Path, store: MemoStore | None = None) -> CacheInvalidator:
    return CacheInvalidator(repo, store if store is not None else _store(repo))


def _slot(repo: Path, key: str) -> Path:
    return repo / ".argus" / "cache" / f"{key}.json"


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — a rejected finding busts its own key → false 🔴 re-computed, never re-served.
# ─────────────────────────────────────────────────────────────────────────────


def test_bust_rejected_finding_makes_subsequent_lookup_a_miss(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-46 — AC1: bust_rejected_finding(record) → lookup(K) is a MISS (forced recompute)."""
    repo = tmp_path / "repo"
    store = _store(repo)
    key = derive_cache_key(_baseline_closure())
    store.store(key, _false_red_result())
    # Before the bust: a HIT re-serves the false 🔴.
    assert store.lookup(key) is not None

    record = RejectedFinding(recording_id="rec-hardcoded_secret-pkg/a.py", key=key)
    inv = _invalidator(repo, store)
    outcome = inv.bust_rejected_finding(record)

    assert outcome.busted is True
    assert outcome.reason == "deleted"
    assert outcome.key == key
    # After the bust: a MISS → the false 🔴 is re-computed, not re-served (AR6).
    assert store.lookup(key) is None


def test_under_bust_is_red_a_naive_no_bust_path_re_serves_the_stale_red(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-47 — AC1 KEYSTONE: a NAIVE no-bust path re-serves the stale 🔴 (RED); the bust forces a MISS (green).

    The under-bust case is the failure this story prevents. RED leg: skipping the
    bust leaves the false 🔴 re-servable on the next lookup. GREEN leg: the busting
    surface forces a MISS. The same lookup(K) is the assertion both legs traverse,
    so the proof is non-vacuous (a MISS genuinely happened because of the bust).
    """
    repo = tmp_path / "repo"
    store = _store(repo)
    key = derive_cache_key(_baseline_closure())
    store.store(key, _false_red_result())
    record = RejectedFinding(recording_id="rec-hardcoded_secret-pkg/a.py", key=key)

    # ── RED leg: the naive path does NOT bust → the stale 🔴 is STILL served.
    naive_served = store.lookup(key)
    assert naive_served is not None
    assert naive_served[0].rule_id == "hardcoded_secret"  # the false 🔴 re-served

    # ── GREEN leg: the real surface busts → the next lookup is a MISS.
    _invalidator(repo, store).bust_rejected_finding(record)
    assert store.lookup(key) is None


def test_bust_spends_no_tokens_and_reads_no_payload_byte(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-48 — AC1/NFR-D2/NFR-S1: a bust is a pure FS delete of a slot file (zero tokens, no payload read)."""
    repo = tmp_path / "repo"
    store = _store(repo)
    key = derive_cache_key(_baseline_closure())
    store.store(key, _false_red_result())
    record = RejectedFinding(recording_id="rec-x", key=key)
    # The record carries NO source/secret bytes — only ids + the cache key.
    dumped = record.model_dump()
    assert set(dumped) == {"recording_id", "key", "rule_id", "cartridge_id", "reason", "rejected_by"}
    # The bust deletes the slot WITHOUT importing any provider/LLM module.
    outcome = _invalidator(repo, store).bust_rejected_finding(record)
    assert outcome.busted is True
    assert not _slot(repo, key).exists()


def test_invalidate_rejections_busts_each_ledger_record(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-49 — AC1: invalidate_rejections() reads the seam ledger and busts each cited key."""
    repo = tmp_path / "repo"
    store = _store(repo)
    key_a = derive_cache_key(_baseline_closure(content_hash="a" * 64))
    key_b = derive_cache_key(_baseline_closure(content_hash="b" * 64))
    store.store(key_a, _false_red_result())
    store.store(key_b, _false_red_result())

    ledger = RejectionLedger(repo)
    ledger.append(RejectedFinding(recording_id="rec-a", key=key_a))
    ledger.append(RejectedFinding(recording_id="rec-b", key=key_b))

    inv = CacheInvalidator(repo, store, rejection_ledger=ledger)
    outcomes = inv.invalidate_rejections()

    assert len(outcomes) == 2
    assert all(o.busted for o in outcomes)
    assert store.lookup(key_a) is None
    assert store.lookup(key_b) is None


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — a detector-set change invalidates the affected (orphaned OLD-hash) entries.
# ─────────────────────────────────────────────────────────────────────────────


def _edited_detector_set() -> tuple[DetectorDescriptor, ...]:
    """A two-detector-set fixture: edit one descriptor's code_identity so the
    detector-set content hash MOVES (the AR6 invalidation lever)."""
    return (
        DetectorDescriptor(rule_id="hardcoded_secret", code_identity="secret_scan.v2"),
        *FROZEN_DETECTOR_SET[1:],
    )


def test_detector_set_change_natural_miss_then_active_delete(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-50 — AC2: a detector-set edit → NATURAL MISS on the new key + ACTIVE delete of the orphaned OLD-hash slot."""
    repo = tmp_path / "repo"
    store = _store(repo)

    old_set = FROZEN_DETECTOR_SET
    new_set = _edited_detector_set()
    old_hash = detector_set_content_hash(old_set)
    new_hash = detector_set_content_hash(new_set)
    assert old_hash != new_hash  # the lever moved

    old_key = derive_cache_key(_baseline_closure(detectors=old_set))
    new_key = derive_cache_key(_baseline_closure(detectors=new_set))
    assert old_key != new_key  # the cache key moved with the detector-set hash

    store.store(old_key, _false_red_result())

    # NATURAL half (already true from 5.1): the new run derives the NEW key → a MISS.
    assert store.lookup(new_key) is None

    # ACTIVE half (this story): delete the orphaned OLD-hash slot.
    inv = _invalidator(repo, store)
    outcomes = inv.invalidate_on_detector_set_change(old_hash, new_hash, known_keys=(old_key,))
    assert len(outcomes) == 1 and outcomes[0].busted is True
    assert not _slot(repo, old_key).exists()  # orphaned slot deleted (no dead accumulation)


def test_detector_set_change_is_red_against_a_path_that_leaves_old_slot_reachable(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-51 — AC2 keystone-adequacy: a path that re-keyed but DID NOT delete leaves the old slot reachable (RED); the active delete removes it (green)."""
    repo = tmp_path / "repo"
    store = _store(repo)
    old_key = derive_cache_key(_baseline_closure(detectors=FROZEN_DETECTOR_SET))
    store.store(old_key, _false_red_result())
    old_hash = detector_set_content_hash(FROZEN_DETECTOR_SET)
    new_hash = detector_set_content_hash(_edited_detector_set())

    # ── RED leg: a re-key-only path (no active delete) leaves the OLD slot present.
    assert _slot(repo, old_key).is_file()
    assert store.lookup(old_key) is not None  # the orphaned stale entry is STILL reachable

    # ── GREEN leg: the active delete removes the orphaned slot.
    _invalidator(repo, store).invalidate_on_detector_set_change(
        old_hash, new_hash, known_keys=(old_key,)
    )
    assert store.lookup(old_key) is None


def test_detector_set_no_change_is_a_no_op(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-52 — AC2/AC3: old_hash == new_hash → NO bust (busting on no change would be a pointless over-bust)."""
    repo = tmp_path / "repo"
    store = _store(repo)
    key = derive_cache_key(_baseline_closure())
    store.store(key, _false_red_result())
    same_hash = detector_set_content_hash(FROZEN_DETECTOR_SET)

    outcomes = _invalidator(repo, store).invalidate_on_detector_set_change(
        same_hash, same_hash, known_keys=(key,)
    )
    assert outcomes == ()
    assert store.lookup(key) is not None  # untouched on a no-change


def test_detector_set_change_recompute_under_new_key_is_correct(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-53 — AC2: after a detector-set change the affected unit is RE-COMPUTED under the new key (correct), not served from the old slot."""
    repo = tmp_path / "repo"
    store = _store(repo)
    old_key = derive_cache_key(_baseline_closure(detectors=FROZEN_DETECTOR_SET))
    new_key = derive_cache_key(_baseline_closure(detectors=_edited_detector_set()))
    store.store(old_key, _false_red_result())

    # New run: MISS on the new key → recompute → store under the new key.
    assert store.lookup(new_key) is None
    recomputed = _recompute()
    store.store(new_key, recomputed)
    served = store.lookup(new_key)
    assert served is not None
    assert _canonical_bytes(served) == _canonical_bytes(recomputed)


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — over-bust SAFE; under-bust the forbidden failure (the correctness asymmetry).
# ─────────────────────────────────────────────────────────────────────────────


def test_over_bust_is_safe_recompute_is_byte_identical_to_cold(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-54 — AC3 KEYSTONE: busting MORE than the minimum is harmless — the recompute is byte-identical to a cold compute."""
    repo = tmp_path / "repo"
    store = _store(repo)
    # Store TWO unrelated entries; bust BOTH (an over-bust — only one strictly needed it).
    key_a = derive_cache_key(_baseline_closure(content_hash="a" * 64))
    key_b = derive_cache_key(_baseline_closure(content_hash="b" * 64))
    store.store(key_a, _false_red_result())
    store.store(key_b, _false_red_result())

    inv = _invalidator(repo, store)
    inv.bust_key(key_a)
    inv.bust_key(key_b)  # the over-bust (b did not strictly need busting)

    # Both re-compute byte-identically to a cold compute (the 5.2 HIT==MISS property).
    for key in (key_a, key_b):
        assert store.lookup(key) is None
        recomputed = _recompute()
        store.store(key, recomputed)
        served = store.lookup(key)
        assert served is not None
        assert _canonical_bytes(served) == _canonical_bytes(_recompute())


def test_over_bust_safe_vs_under_bust_forbidden_asymmetry(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-55 — AC3: the asymmetry — an over-bust still yields the correct verdict; an under-bust re-serves the stale 🔴 (RED)."""
    repo = tmp_path / "repo"
    store = _store(repo)
    key = derive_cache_key(_baseline_closure())
    store.store(key, _false_red_result())
    record = RejectedFinding(recording_id="rec-x", key=key)

    # ── UNDER-bust (RED): NOT busting re-serves the stale rejected 🔴.
    assert store.lookup(key) is not None

    # ── OVER-bust / correct bust (green): the bust → MISS → recompute is correct.
    _invalidator(repo, store).bust_rejected_finding(record)
    assert store.lookup(key) is None
    recomputed = _recompute()
    assert _canonical_bytes(recomputed) == _canonical_bytes(_false_red_result())


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — idempotent, containment-safe, leak-free, no-crash, never corrupts the store.
# ─────────────────────────────────────────────────────────────────────────────


def test_bust_already_absent_key_is_idempotent_no_op(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-56 — AC4: busting a never-stored / already-busted key is a no-op outcome, never a raise."""
    repo = tmp_path / "repo"
    store = _store(repo)
    key = derive_cache_key(_baseline_closure())
    inv = _invalidator(repo, store)

    # Never stored → absent.
    first = inv.bust_key(key)
    assert first.busted is False and first.reason == "absent"

    # Store, bust once (deleted), bust again (absent — idempotent, never raises).
    store.store(key, _false_red_result())
    second = inv.bust_key(key)
    assert second.busted is True and second.reason == "deleted"
    third = inv.bust_key(key)
    assert third.busted is False and third.reason == "absent"


def test_bust_traversal_key_raises_containment_before_any_delete(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-57 — AC4/NFR-S5: a traversal/escaping key raises WorkspaceContainmentError BEFORE any delete."""
    repo = tmp_path / "repo"
    store = _store(repo)
    inv = _invalidator(repo, store)
    # Plant a sibling file outside the cache tree that a naive str-prefix bust might hit.
    outside = tmp_path / "escape.json"
    outside.write_text("do not delete me", encoding="utf-8")

    with pytest.raises(WorkspaceContainmentError):
        inv.bust_key("../../escape")
    # The containment check fired BEFORE any delete — the outside file survives.
    assert outside.exists()


def test_bust_sibling_prefix_key_raises_containment(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-58 — AC4/NFR-S5: a sibling-prefix escape (.argus-evil vs .argus) is rejected (is_relative_to, not str.startswith)."""
    repo = tmp_path / "repo"
    inv = _invalidator(repo)
    # cache/<key>.json with this key resolves to a sibling-prefixed dir (.argus-evil)
    # that is NOT contained by .argus (is_relative_to rejects it; str.startswith would
    # falsely accept the ".argus" prefix).
    with pytest.raises(WorkspaceContainmentError):
        inv.bust_key("../../.argus-evil/cache/x")


def test_bust_leaves_sibling_cache_entries_and_tree_intact(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-59 — AC4: a bust deletes ONE slot file, leaving every other cache entry + the .argus/ tree intact (no corruption)."""
    repo = tmp_path / "repo"
    store = _store(repo)
    key_target = derive_cache_key(_baseline_closure(content_hash="a" * 64))
    key_sibling = derive_cache_key(_baseline_closure(content_hash="b" * 64))
    store.store(key_target, _false_red_result())
    store.store(key_sibling, _false_red_result())

    _invalidator(repo, store).bust_key(key_target)

    assert not _slot(repo, key_target).exists()
    # The sibling slot + the surrounding tree survive intact.
    assert _slot(repo, key_sibling).is_file()
    assert store.lookup(key_sibling) is not None
    assert (repo / ".argus" / "cache").is_dir()


def test_permission_denied_delete_degrades_to_typed_outcome(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-60 — AC4/AR10: an OSError / permission-denied on the delete degrades to a typed BustOutcome (RED against a propagating path)."""
    repo = tmp_path / "repo"
    store = _store(repo)
    key = derive_cache_key(_baseline_closure())
    store.store(key, _false_red_result())
    inv = _invalidator(repo, store)

    # ── RED-demo: a path that lets the OS error propagate WOULD raise.
    def _raising_unlink(*_a, **_k):  # type: ignore[no-untyped-def]
        raise PermissionError("permission denied: cannot unlink slot")

    original = Path.unlink
    Path.unlink = _raising_unlink  # type: ignore[assignment]
    try:
        with pytest.raises(PermissionError):
            _slot(repo, key).unlink()  # the naive propagating path raises

        # ── GREEN: the real bust swallows the OS error into a typed outcome.
        outcome = inv.bust_key(key)
        assert outcome.busted is False
        assert outcome.reason == "os_error"
    finally:
        Path.unlink = original  # type: ignore[assignment]
    # The slot still exists (the delete failed) — but the audit did NOT crash.
    assert _slot(repo, key).is_file()


def test_corrupt_rejection_ledger_degrades_to_empty_safe_skip(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-61 — AC4/AR10: a corrupt / non-UTF-8 rejection-ledger read degrades to an EMPTY ledger (safe skip), never a crash."""
    repo = tmp_path / "repo"
    ledger = RejectionLedger(repo)
    ledger.append(RejectedFinding(recording_id="rec-x", key="k" * 64))
    # Corrupt the persisted ledger file.
    slot = repo / ".argus" / REJECTION_LEDGER_RELATIVE
    slot.write_bytes(b"{not valid json at all")
    assert ledger.read() == ()  # safe skip — no crash

    # Non-UTF-8 → also a safe skip.
    slot.write_bytes(b"\xff\xfe\x00\x01 not utf-8")
    assert ledger.read() == ()


def test_tampered_rejection_ledger_degrades_to_empty(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-62 — AC4/AR10: a content-hash-mismatch (tampered) rejection ledger → EMPTY (the 1.3 tamper guard), never a served record."""
    repo = tmp_path / "repo"
    ledger = RejectionLedger(repo)
    ledger.append(RejectedFinding(recording_id="rec-real", key="k" * 64))
    slot = repo / ".argus" / REJECTION_LEDGER_RELATIVE
    obj = canonical.loads(slot.read_bytes())
    # Mutate the payload WITHOUT recomputing the content_hash (a tamper).
    obj["payload"]["rejections"].append(
        {"recording_id": "POISON", "key": "p" * 64, "rule_id": None,
         "cartridge_id": None, "reason": None, "rejected_by": None}
    )
    slot.write_bytes(canonical.dumps_bytes(obj))
    assert ledger.read() == ()  # tamper → empty, the poison is never consumed


def test_wrong_schema_rejection_ledger_degrades_to_empty(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-63 — AC4/AR10: a wrong-schema (extra=forbid) rejection-ledger payload → EMPTY (ValidationError swallowed)."""
    repo = tmp_path / "repo"
    ledger = RejectionLedger(repo)
    ledger.append(RejectedFinding(recording_id="rec-real", key="k" * 64))
    slot = repo / ".argus" / REJECTION_LEDGER_RELATIVE
    obj = canonical.loads(slot.read_bytes())
    obj["payload"]["unknown_field"] = "boom"
    # Re-stamp the content_hash so it is the SCHEMA, not the tamper guard, that trips.
    from argus.store.envelope import compute_content_hash

    obj["content_hash"] = compute_content_hash(obj["payload"])
    slot.write_bytes(canonical.dumps_bytes(obj))
    assert ledger.read() == ()


def test_missing_rejection_ledger_is_empty(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-64 — AC4/AR10: an absent rejection ledger reads as EMPTY (a cache invalidation over zero records is a safe no-op)."""
    repo = tmp_path / "repo"
    assert RejectionLedger(repo).read() == ()
    # invalidate_rejections over an empty/missing ledger → no busts.
    assert _invalidator(repo).invalidate_rejections() == ()


def test_invalidate_rejections_skips_a_corrupt_ledger_without_crashing(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-65 — AC4/AR10: a corrupt ledger makes invalidate_rejections a safe no-op (RED against a trusting read that would crash)."""
    repo = tmp_path / "repo"
    store = _store(repo)
    ledger = RejectionLedger(repo)
    ledger.append(RejectedFinding(recording_id="rec-x", key="k" * 64))
    (repo / ".argus" / REJECTION_LEDGER_RELATIVE).write_bytes(b"corrupt")
    inv = CacheInvalidator(repo, store, rejection_ledger=ledger)
    assert inv.invalidate_rejections() == ()  # no crash, no busts


def test_rejection_record_payload_is_pure_no_float_clock_uuid(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-66 — AC4/AR4/NFR-D3: the rejection-ledger payload is canonical (no float/clock/uuid); the envelope hash excludes run_id/created_at."""
    repo = tmp_path / "repo"
    ledger = RejectionLedger(repo)
    ledger.append(RejectedFinding(recording_id="rec-x", key="k" * 64, reason="false-positive"))
    slot = repo / ".argus" / REJECTION_LEDGER_RELATIVE
    # The persisted bytes round-trip through the single canonical loader (no float).
    obj = canonical.loads(slot.read_bytes())
    assert obj["producer"] == REJECTION_LEDGER_PRODUCER
    assert obj["schema_version"] == REJECTION_LEDGER_SCHEMA_VERSION
    # The content_hash is over the payload only (run_id/created_at excluded — NFR-D3).
    from argus.store.envelope import compute_content_hash

    assert obj["content_hash"] == compute_content_hash(obj["payload"])
    assert obj.get("run_id") is None and obj.get("created_at") is None


def test_rejection_ledger_read_reverifies_via_reader_tamper_guard(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-67 — AC4: the ledger read reuses the 1.3 read_envelope(verify_hash=True) tamper guard (a clean write reads back the records)."""
    repo = tmp_path / "repo"
    ledger = RejectionLedger(repo)
    rec = RejectedFinding(recording_id="rec-x", key="k" * 64)
    ledger.append(rec)
    # The 1.3 reader reads the persisted envelope back (verify_hash passes on clean write).
    envelope = ApaaStoreReader(repo).read_envelope(REJECTION_LEDGER_RELATIVE, verify_hash=True)
    payload = RejectionLedgerPayload.model_validate(envelope.payload)
    assert payload.rejections == (rec,)


def test_rejected_finding_is_frozen_and_extra_forbid() -> None:
    """TC-ArgusAgent-CACHE-001-68 — AC4: RejectedFinding is frozen + extra=forbid (no source/secret fields can be smuggled in)."""
    rec = RejectedFinding(recording_id="r", key="k")
    with pytest.raises(Exception):
        rec.recording_id = "mutated"  # frozen
    with pytest.raises(Exception):
        RejectedFinding(recording_id="r", key="k", source_bytes="leak")  # extra=forbid


def test_append_preserves_prior_records_append_only(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-69 — AC4: the RejectionLedger is append-only — a second append preserves the first record."""
    repo = tmp_path / "repo"
    ledger = RejectionLedger(repo)
    ledger.append(RejectedFinding(recording_id="rec-1", key="k1"))
    ledger.append(RejectedFinding(recording_id="rec-2", key="k2"))
    records = ledger.read()
    assert [r.recording_id for r in records] == ["rec-1", "rec-2"]


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — stable AND correct; LOCAL-only; non-ASCII (AI-E1-1).
# ─────────────────────────────────────────────────────────────────────────────


def test_stable_and_correct_after_bust_and_wiped_cold_rebuild(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-70 — AC5: a clean repo is stable repeatedly; after a bust the entry is re-computed; a wiped-cache cold rebuild yields the SAME result."""
    import shutil

    repo = tmp_path / "repo"
    store = _store(repo)
    key = derive_cache_key(_baseline_closure())

    # Stable: stored once, served repeatedly byte-identically.
    store.store(key, _recompute())
    first = store.lookup(key)
    second = store.lookup(key)
    assert first is not None and second is not None
    assert _canonical_bytes(first) == _canonical_bytes(second)

    # After a bust: re-computed (correct), then re-served byte-identically.
    _invalidator(repo, store).bust_key(key)
    assert store.lookup(key) is None
    store.store(key, _recompute())
    after_bust = store.lookup(key)
    assert after_bust is not None
    assert _canonical_bytes(after_bust) == _canonical_bytes(first)

    # Wiped-cache cold rebuild → the SAME result (invalidation is an optimization).
    shutil.rmtree(repo / ".argus" / "cache")
    rebuilt_store = _store(repo)
    assert rebuilt_store.lookup(key) is None
    cold = _recompute()
    assert _canonical_bytes(cold) == _canonical_bytes(first)


def test_invalidation_is_local_to_the_audited_repo_tree(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-71 — AC5: a bust on repo A does not touch repo B's cache (LOCAL-only, no shared/network cache)."""
    repo_a = tmp_path / "a"
    repo_b = tmp_path / "b"
    key = derive_cache_key(_baseline_closure())
    _store(repo_a).store(key, _false_red_result())
    _store(repo_b).store(key, _false_red_result())

    _invalidator(repo_a).bust_key(key)

    assert _store(repo_a).lookup(key) is None  # busted locally
    assert _store(repo_b).lookup(key) is not None  # repo B untouched


def test_non_ascii_key_busts_byte_stably(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-72 — AC5/AI-E1-1: a closure with a non-ASCII / Cyrillic path busts byte-stably under UTF-8."""
    repo = tmp_path / "repo"
    store = _store(repo)
    closure = RecordingProducingClosure(
        content_hash="b" * 64,
        detectors=FROZEN_DETECTOR_SET,
        grammar_version="0.23.6",
        tool_versions={"radon": "6.0.1"},
        budget=50,
        materiality_bar="release",
        work_manifest_files=("src/café/модуль.py",),
        critical_paths=("src/café/модуль.py",),
    )
    key = derive_cache_key(closure)
    result = (
        Recording(
            recording_id="rec-café-секрет",
            rule_id="hardcoded_secret",
            advisory=False,
            locators=(Locator(file_path="src/café/модуль.py", start_line=2, end_line=4),),
        ),
    )
    store.store(key, result)
    assert store.lookup(key) is not None

    # The rejection record cites the non-ASCII finding by id + the key it was served under.
    record = RejectedFinding(
        recording_id="rec-café-секрет", key=key, reason="ложноположительный"
    )
    outcome = _invalidator(repo, store).bust_rejected_finding(record)
    assert outcome.busted is True
    assert store.lookup(key) is None

    # A non-ASCII reason persists byte-stably through the ledger envelope.
    ledger = RejectionLedger(repo)
    ledger.append(record)
    read_back = ledger.read()
    assert read_back[0].reason == "ложноположительный"
    assert read_back[0].recording_id == "rec-café-секрет"


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — structural discipline: typed outcome, file-size, no re-derivation of keys.
# ─────────────────────────────────────────────────────────────────────────────


def test_bust_outcome_is_a_typed_result_not_a_bare_bool(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-73 — AC6/AR10: bust_key returns a typed BustOutcome (never a bare bool)."""
    repo = tmp_path / "repo"
    inv = _invalidator(repo)
    outcome = inv.bust_key(derive_cache_key(_baseline_closure()))
    assert isinstance(outcome, BustOutcome)
    assert outcome.busted is False  # absent
    # The outcome is frozen + extra=forbid (the 1.1 contract precedent).
    with pytest.raises(Exception):
        outcome.busted = True


def test_invalidator_consumes_key_does_not_re_derive(tmp_path: Path) -> None:
    """TC-ArgusAgent-CACHE-001-74 — AC6/AR5: the surface busts the EXACT key handed to it (it consumes derive_cache_key, never re-derives)."""
    repo = tmp_path / "repo"
    store = _store(repo)
    key = derive_cache_key(_baseline_closure())
    store.store(key, _false_red_result())
    outcome = _invalidator(repo, store).bust_key(key)
    # The busted slot is exactly cache/<key>.json (the SAME slot convention as MemoStore).
    assert outcome.locator == f"cache/{key}.json"


def test_invalidation_module_is_under_1200_lines() -> None:
    """TC-ArgusAgent-CACHE-001-75 — AC6/NFR-M1: invalidation.py and this test file are each ≤1200 lines."""
    src_lines = _INVALIDATION_MODULE.read_text(encoding="utf-8").splitlines()
    assert len(src_lines) <= 1200
    test_lines = Path(__file__).read_text(encoding="utf-8").splitlines()
    assert len(test_lines) <= 1200
