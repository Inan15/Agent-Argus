"""ArgusAgent-CACHE — CAN the memoization LIE? (FR27 / NFR-D1, Story 12.3).

Verification area: ``TC-ArgusAgent-CACHE-001-89``.., continuing the ``CACHE`` index and the
sibling ``tests/test_stage_memo_wiring.py``, from which this file was split along a COHESION
boundary when the pair outgrew the NFR-M1 1200-line ceiling. The sibling asks *is the cache
load-bearing?*; this file asks the question that matters more in an assurance tool: **now that
it IS load-bearing, can it serve something untrue?**

Its four subjects:

* **AC4 — the correctness surface.** Damage of every named DN-MISS class degrades to a
  recompute, never to a raise and never to a served poison; the degradation costs time, never
  correctness; no source, secret or host-path bytes reach a cache artifact; and the payload
  schema bump is a real invalidation lever in both directions.
* **AC5 — invalidation over the WIRED path.** A detector-set edit, a grammar upgrade and the
  prompt-template slot each move the key, end to end. Story 5.3's ACTIVE eviction surface is
  ruled OUT of scope out loud (`-95`), never silently.
* **AC6 — the deep-pass fence.** An LLM-derived recording cannot enter a memoized payload while
  the closure carries the V1 placeholder checkpoint, because two models would otherwise collide
  on one slot.
* **AC1 — no new surface.** Story 12.3 DELIVERS an existing requirement; it invents nothing.

🔴 NO EGRESS, EVER (§0.3(c)). Story 12.2 owns the product's only egress path. The deep-pass legs
below always INJECT a port, so ``_resolve_dispatcher`` never reaches its adapter branch, no HTTP
client is constructed and no socket is opened.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

from argus.cache.key import (
    FROZEN_DETECTOR_SET,
    RecordingProducingClosure,
    V1_MODEL_CHECKPOINT,
    V1_PROMPT_TEMPLATE_VERSION,
    derive_cache_key,
)
from argus.cache.memo_store import MEMO_STORE_SCHEMA_VERSION, MemoStore, RecordedStageResult
from argus.detectors.base import FindingDraft, build_recording
from argus.models import AuditRequest
from argus.pipeline import run_audit_detailed

# The `tests/cartridges/_cartridge.py` import convention, applied to a sibling fixture module.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _stage_memo_corpus import (  # noqa: E402
    _APP_SOURCE,
    _blocked_repo,
    _cache_slots,
    _clean_repo,
    _poison_finding,
    _request,
    _spy_on_detect_stage,
)

# ─────────────────────────────────────────────────────────────────────────────
# AC4 — a cache is a correctness surface: it cannot serve a lie
# ─────────────────────────────────────────────────────────────────────────────


def _corrupt(slot: Path) -> None:
    slot.write_bytes(b"{ this is not canonical json at all")


def _tamper(slot: Path) -> None:
    """Mutate the payload WITHOUT recomputing its content_hash (the AR6 tamper case)."""
    from argus.store import canonical

    envelope = canonical.loads(slot.read_bytes())
    envelope["payload"]["findings"] = []
    envelope["payload"]["entries"] = []
    slot.write_bytes(canonical.dumps_bytes(envelope))


def _wrong_schema(slot: Path) -> None:
    """A payload written under a DIFFERENT memo schema version, integrity-correct throughout."""
    from argus.store import canonical
    from argus.store.envelope import EnvelopeWriter

    envelope = canonical.loads(slot.read_bytes())
    payload = dict(envelope["payload"])
    payload["schema_version"] = "1"
    rebuilt = EnvelopeWriter.build(payload, schema_version="1", producer="argus.cache.memo_store")
    slot.write_bytes(canonical.dumps_bytes(rebuilt.model_dump()))


def _non_file(slot: Path) -> None:
    """Replace the slot with a DIRECTORY — the 'not a file' leg of the DN-MISS taxonomy."""
    slot.unlink()
    slot.mkdir()


@pytest.mark.parametrize(
    "damage",
    [_corrupt, _tamper, _wrong_schema, _non_file],
    ids=["corrupt", "tampered", "wrong_schema", "non_file"],
)
def test_TC_ArgusAgent_CACHE_001_89_a_damaged_entry_misses_and_recomputes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, damage: Any
) -> None:
    """TC-ArgusAgent-CACHE-001-89 — AC4.2/AC4.3: damage degrades to a MISS, never to a lie.

    The DN-MISS taxonomy is already proven over the store AS A LIBRARY by
    ``tests/test_memo_store.py``. What was never proven — and is what this story is
    accountable for — is that it holds OVER THE WIRED PATH: that a damaged slot reached
    through ``run_audit_detailed`` produces a recompute rather than a raise, a crash, or a
    served poison.

    Both halves are asserted, because either alone is misleading. The run must RE-EXECUTE the
    stage (so we know the damaged entry really was refused rather than quietly accepted), AND
    the verdict must be byte-identical to the cold one (so we know the refusal cost time, not
    correctness). ``_tamper`` is the sharpest leg: it removes every finding, so an accepted
    tampered entry would flip a blocked repository green — the precise lie a cache must never
    be able to tell.
    """
    repo = _blocked_repo(tmp_path / "repo")
    spy = _spy_on_detect_stage(monkeypatch)

    cold = run_audit_detailed(_request(repo))
    assert spy.calls == 1
    assert cold.verdict.blocking_finding_count >= 1, (
        "fixture precondition: the leaky corpus must carry a verdict-blocking finding, "
        "otherwise the tampered leg has nothing to erase"
    )
    slots = _cache_slots(repo)
    assert len(slots) == 1

    damage(slots[0])

    after = run_audit_detailed(_request(repo))
    assert spy.calls == 2, (
        f"a damaged cache entry was NOT refused — the stage did not re-execute (calls "
        f"{spy.calls}). A cache that serves damaged bytes is the 'memoization caches errors → "
        "reproducibility ≠ correctness' failure this store was built to prevent."
    )
    assert after.verdict.verdict == cold.verdict.verdict, (
        "the degradation changed the verdict. A MISS must cost TIME, never correctness "
        "(AC4.3): the recomputed answer is the cold answer."
    )
    assert after.verdict.blocking_finding_count == cold.verdict.blocking_finding_count, (
        "the blocking-finding count moved after a damaged entry was refused — the recompute "
        "did not reproduce the cold run"
    )


def test_TC_ArgusAgent_CACHE_001_90_no_source_secret_or_host_path_bytes_in_a_cache_artifact(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-CACHE-001-90 — AC4.4: the cache joins the swept containment union (NFR-S1/S5).

    A cache is a new place for bytes to leak to, and it is written on the default path of every
    run, so it must obey the same containment contract as every other ``.argus/`` artifact.
    Three distinct leak classes are checked over the ACTUAL persisted slot bytes: the secret
    literal the corpus plants, a distinctive line of source text, and the absolute host path of
    the temporary tree (which would make an artifact non-portable as well as leaky).

    The secret leg is the load-bearing one and it is not hypothetical: the corpus is audited
    precisely BECAUSE it contains a credential, so a store that persisted finding evidence
    naively would fail here.
    """
    repo = _blocked_repo(tmp_path / "repo")
    run_audit_detailed(_request(repo))
    slots = _cache_slots(repo)
    assert slots, "no cache artifact was written — this guard would sweep an empty set"

    secret_literal = b"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    source_line = b"def subtract(a: int, b: int) -> int:"
    host_path = str(tmp_path).encode("utf-8")
    host_path_posix = tmp_path.as_posix().encode("utf-8")

    for slot in slots:
        raw = slot.read_bytes()
        assert secret_literal not in raw, (
            f"THE PLANTED SECRET LEAKED INTO THE CACHE ARTIFACT {slot.name}. Findings are "
            "producer-side redacted (NFR-S1) and the cache must not undo that."
        )
        assert source_line not in raw, f"source bytes leaked into the cache artifact {slot.name}"
        assert host_path not in raw, f"an absolute host path leaked into {slot.name}"
        assert host_path_posix not in raw, f"an absolute host path (posix) leaked into {slot.name}"


def test_TC_ArgusAgent_CACHE_001_91_the_memo_schema_bump_moves_the_slot_both_directions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-CACHE-001-91 — AC4.5: the payload-schema bump is a real lever, both ways.

    ``MEMO_STORE_SCHEMA_VERSION``'s contract says a bump *"deliberately changes the content
    hash"*. That is asserted here directly rather than trusted, and then the consequence that
    actually matters is asserted too: an entry written under the OLD payload shape is NOT
    SERVED under the new one.

    The second half is not implied by the first, and missing it would be a real defect. The
    envelope's ``content_hash`` is recomputed from the payload it is stored WITH, so an
    old-shape entry verifies against itself perfectly — the tamper guard has no reason to
    object. Only the explicit version check in ``lookup_stage`` refuses it. Both directions are
    covered: the wrong version MISSES, and the right version still HITS (a store that refused
    everything would pass the first assertion and be useless).
    """
    from argus.store.envelope import compute_content_hash

    # Direction 1 — the bump moves the content hash of an identical result.
    result = RecordedStageResult(entries=(), findings=(), candidates=())
    payload_v1 = {"schema_version": "1", "entries": [], "findings": [], "candidates": []}
    payload_v2 = {
        "schema_version": MEMO_STORE_SCHEMA_VERSION,
        "entries": [],
        "findings": [],
        "candidates": [],
    }
    assert compute_content_hash(payload_v1) != compute_content_hash(payload_v2), (
        "the schema version is inside the hashed payload, so a bump MUST move the content "
        "hash; if it does not, the version is decoration and cannot invalidate anything"
    )

    # Direction 2 — over the WIRED path: an old-shape entry is not served, and the
    # current-shape entry it is replaced by is.
    repo = _clean_repo(tmp_path / "repo")
    spy = _spy_on_detect_stage(monkeypatch)
    run_audit_detailed(_request(repo))
    assert spy.calls == 1
    slot = _cache_slots(repo)[0]
    key = slot.stem

    store = MemoStore(repo)
    assert store.lookup_stage(key) is not None, "precondition: the fresh slot must be readable"

    _wrong_schema(slot)
    assert store.lookup_stage(key) is None, (
        "an entry written under memo schema '1' was SERVED under schema "
        f"{MEMO_STORE_SCHEMA_VERSION!r}. Its envelope hash verifies — it was never edited — so "
        "nothing but the explicit version check can refuse it, and without that refusal the "
        "bump would move the hash for future writes while old-shape entries kept being served."
    )
    run_audit_detailed(_request(repo))
    assert spy.calls == 2, "the old-shape entry must degrade to a MISS → recompute"

    # …and the freshly re-written current-shape entry IS served again.
    run_audit_detailed(_request(repo))
    assert spy.calls == 2, (
        "after the recompute re-recorded the slot under the CURRENT schema, the next run must "
        "HIT. A store that refuses everything passes the refusal assertion above and is still "
        "a cache that never works."
    )
    assert store.lookup_stage(key) is not None, (
        f"the slot was not re-recorded under {MEMO_STORE_SCHEMA_VERSION!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — the invalidation contract holds over the WIRED path
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_CACHE_001_92_a_detector_set_change_misses_over_the_wired_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-CACHE-001-92 — AC5.1: a detector-set edit MISSES, proven end to end.

    Both halves of ``DetectorDescriptor``'s stated invalidation lever are exercised over
    ``run_audit_detailed``, not at the key function:

    * ``config`` — the operator's ``--passes`` and ``--ignore-path`` choices reach the key
      through the descriptor config (see ``stage_memo.stage_detector_set``). This is the leg
      that matters most in practice and the one whose absence would be a live correctness bug:
      without it, a run with the security pass DISABLED would be served the findings of a run
      with it ENABLED.
    * ``code_identity`` — bumped the way Argus itself would bump it when a detector's logic
      materially changes.

    Each must produce a NEW slot and a re-executed stage. This is the NATURAL miss the 5.2/5.3
    fence describes: the key moved, so a different slot is read. Nothing was evicted.
    """
    repo = _clean_repo(tmp_path / "repo")
    spy = _spy_on_detect_stage(monkeypatch)

    baseline_passes = ("coverage", "vacuous", "security", "orphan")
    run_audit_detailed(_request(repo, enabled_passes=baseline_passes))
    assert spy.calls == 1
    assert len(_cache_slots(repo)) == 1

    # (a) config — a DESELECTED pass must not be served the selected pass's answer.
    run_audit_detailed(_request(repo, enabled_passes=("coverage", "vacuous", "orphan")))
    assert spy.calls == 2, (
        "disabling the security pass did not MISS. The stage's output depends on which passes "
        "ran, so serving the previous answer would return findings from detectors this run "
        "explicitly deselected."
    )
    assert len(_cache_slots(repo)) == 2

    # (b) config — an ignore rule is a determinism-relevant detector setting.
    run_audit_detailed(_request(repo, enabled_passes=baseline_passes, ignore_paths=("app/",)))
    assert spy.calls == 3, "an --ignore-path rule did not move the key"
    assert len(_cache_slots(repo)) == 3

    # (c) code_identity — the declared lever for 'this detector's logic changed'.
    bumped = tuple(
        descriptor.model_copy(update={"code_identity": f"{descriptor.code_identity}.bumped"})
        for descriptor in FROZEN_DETECTOR_SET
    )
    monkeypatch.setattr("argus.cache.stage_memo.FROZEN_DETECTOR_SET", bumped)
    run_audit_detailed(_request(repo, enabled_passes=baseline_passes))
    assert spy.calls == 4, (
        "a bumped detector code_identity did not MISS. That token is the DECLARED mechanism "
        "for 'this detector's logic materially changed'; if it does not move the key, the "
        "cache would serve results computed by the OLD detector after the change."
    )
    assert len(_cache_slots(repo)) == 4

    # …and reverting the bump lands back on the ORIGINAL slot, which still HITS. A "miss"
    # that was really "every key moved" would pass every assertion above and be useless.
    monkeypatch.undo()
    spy = _spy_on_detect_stage(monkeypatch)
    run_audit_detailed(_request(repo, enabled_passes=baseline_passes))
    assert spy.calls == 0, (
        "reverting the detector-set change did not return to the ORIGINAL slot. The key must "
        "be a FUNCTION of the detector set, not merely sensitive to it."
    )
    assert len(_cache_slots(repo)) == 4, "no new slot should be written on a hit"


def test_TC_ArgusAgent_CACHE_001_93_a_grammar_version_change_misses_over_the_wired_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-CACHE-001-93 — AC5.2: the 10.2 per-grammar correction, proven END TO END.

    ``DF-AUD-APAA-D`` was the defect that the key folded ONE grammar version (resolved from
    ``tree-sitter-python``) while the index parsed ten languages, so nine of ten grammar
    upgrades did not move it. Story 10.2 fixed the KEY FUNCTION. This asserts the fix is
    actually REACHED by the production path — a corrected key nobody consumes corrects nothing.

    The version is moved at the real probe (``ast_index._package_version``), so the index
    RECORDS a different provenance exactly as it would after a real grammar upgrade, and the
    change flows index → closure → key → slot without this test touching any of those.
    """
    from argus.index import ast_index

    repo = _clean_repo(tmp_path / "repo")
    spy = _spy_on_detect_stage(monkeypatch)

    run_audit_detailed(_request(repo))
    assert spy.calls == 1
    assert len(_cache_slots(repo)) == 1

    real_probe = ast_index._package_version
    monkeypatch.setattr(
        ast_index, "_package_version", lambda lang: f"99.99.99-upgraded-{real_probe(lang)}"
    )
    run_audit_detailed(_request(repo))
    assert spy.calls == 2, (
        "an upgraded grammar did NOT move the key, so the run was served a result produced by "
        "a DIFFERENT grammar. This is DF-AUD-APAA-D reaching the wired path — the key function "
        "was corrected by 10.2, but the production closure was not consuming the correction."
    )
    assert len(_cache_slots(repo)) == 2


def test_TC_ArgusAgent_CACHE_001_94_the_prompt_template_slot_still_moves_the_key() -> None:
    """TC-ArgusAgent-CACHE-001-94 — AC5.3: DF-5-1-A's forward-coupling hole stays closed.

    ``DF-5-1-A`` (closed 2026-06-28) added ``prompt_template_version`` to the closure BEFORE
    there was a live LLM, precisely so that when a real value eventually lands, a
    prompt-template change cannot serve a stale result computed under a different prompt. The
    slot is a fixed sentinel today, so nothing else in the suite would notice if it silently
    stopped being folded — which is exactly the kind of dormant guarantee that rots.

    Asserted with a REAL prompt-template value, not another sentinel: the live
    ``DEEP_PROMPT_TEMPLATE_VERSION`` that Story 12.2's deep pass actually dispatches under. If
    the slot ever stops moving the key, the day 6.1 substitutes a real value the cache starts
    serving across prompt changes.
    """
    from argus.audit.deep_pass import DEEP_PROMPT_TEMPLATE_VERSION

    baseline = RecordingProducingClosure(
        content_hash="a" * 64,
        grammar_version="1.0.0",
        budget=0,
        materiality_bar="none",
        work_manifest_files=("app/service.py",),
    )
    assert baseline.prompt_template_version == V1_PROMPT_TEMPLATE_VERSION
    moved = baseline.model_copy(
        update={"prompt_template_version": DEEP_PROMPT_TEMPLATE_VERSION}
    )
    assert derive_cache_key(moved) != derive_cache_key(baseline), (
        "the prompt_template_version slot no longer moves the cache key. DF-5-1-A's whole "
        "purpose was that this slot be LOAD-BEARING before a real value exists; a slot that "
        "is folded in name only reopens the forward-coupling hole silently."
    )
    assert derive_cache_key(
        baseline.model_copy(update={"model_checkpoint": "a-real-captured-checkpoint"})
    ) != derive_cache_key(baseline), (
        "the model_checkpoint slot no longer moves the key either — the checkpoint_drift "
        "detection seam (AR5) rests on two different checkpoints deriving two different keys"
    )


def test_TC_ArgusAgent_CACHE_001_95_story_5_3_active_invalidation_is_ruled_out_of_scope() -> None:
    """TC-ArgusAgent-CACHE-001-95 — AC5.4: the 5.3 surface is RULED OUT LOUD, and left unbroken.

    AC5.4 offers two answers and forbids the third. Story 12.3 takes option (b): the Story 5.3
    ACTIVE invalidation surface (``argus/cache/invalidation.py`` — detector-set-hash eviction
    plus rejected-finding key-busting) is **OUT OF SCOPE**, for measured reasons:

    * The epic AC names only *"the DF-5-1-A invalidation contract holds over the wired path"*,
      which is `-94` plus the NATURAL misses of `-86`/`-92`/`-93`. Those are all delivered.
    * ``invalidation.py`` has NO production call site and is not in the import closure from
      ``argus.cli``. Wiring it is a SECOND delivery with its own correctness surface (deleting
      cache entries is destructive in a way that consulting them is not), not a corollary of
      this one.
    * The natural miss makes it unnecessary for correctness here: a detector-set edit ALREADY
      moves the key and lands on a different slot (`-92`), which is the 5.2-vs-5.3 fence
      ``memo_store.py`` states in its own docstring. ACTIVE eviction is an optimization over
      that, not a correctness requirement of it.

    Ruling it out SILENTLY is what AC5.4 forbids, so the ruling is asserted here: the surface
    must still be importable and intact (this story did not break it on the way past), and its
    unreachability is recorded as the MEASURED fact the ruling rests on — if a later story
    wires it, this test goes red and the ruling must be re-taken rather than forgotten.
    """
    import argus.cache.invalidation as invalidation

    for name in ("RejectedFinding", "RejectionLedger"):
        assert hasattr(invalidation, name), (
            f"the Story 5.3 surface lost {name!r}. This story ruled 5.3 out of scope, which "
            "obliges it to leave that surface exactly as it found it."
        )

    import sys

    sys.path.insert(0, "tests")
    # `_ENTRY_POINTS` / `reachable_from_any` since 2026-08-15 (Story 12.6): this
    # distribution ships TWO entry points and the reachability question this ruling rests on
    # is "does ANY production entry point reach it", so the union is the only reading that
    # keeps the ruling honest. Taking `argus.cli` alone would have left the exclusion true
    # by measuring the wrong graph — which is the failure this import was written to avoid.
    from test_v1_commitment_closure import (  # noqa: PLC0415
        _ENTRY_POINTS,
        _PACKAGE_ROOT,
        build_import_graph,
        reachable_from_any,
    )

    reachable = reachable_from_any(build_import_graph(_PACKAGE_ROOT), _ENTRY_POINTS)
    assert "argus.cache.memo_store" in reachable, (
        "argus.cache.memo_store must be REACHABLE — that flip is this story's AC1.1 and the "
        "premise for everything else here"
    )
    assert "argus.cache.invalidation" not in reachable, (
        "argus/cache/invalidation.py has become reachable from argus.cli. Story 12.3 ruled the "
        "5.3 ACTIVE invalidation surface OUT OF SCOPE on the measured basis that it has no "
        "production call site. If it now has one, that ruling has expired: re-take it "
        "explicitly and prove the eviction contract over the wired path, rather than "
        "inheriting an exclusion whose premise no longer holds."
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — the deep-pass ruling is ENFORCED (the fence)
# ─────────────────────────────────────────────────────────────────────────────


class _FakeDispatch:
    """A deterministic ``LLMDispatchPort`` consuming ZERO LLM tokens and opening NO socket.

    The idiom ``tests/test_llm_dispatch_port.py`` and ``tests/test_deep_pass_wiring.py``
    already use, reused rather than forked. Because a port is always INJECTED, the deep pass
    never reaches ``_resolve_dispatcher``'s adapter branch, so no HTTP client is constructed
    and no ``.invalid`` host is even needed — the two-fence pattern degenerates to one fence
    that cannot be crossed (§0.3(c)).
    """

    def __init__(self) -> None:
        self.calls = 0

    def dispatch(self, req: Any) -> Any:
        from argus.audit.ports import LLMRecording

        self.calls += 1
        return LLMRecording(
            model_checkpoint="fake-checkpoint-v1",
            prompt_template_version=req.prompt_template_version,
            provider_id="fake",
            input_tokens=0,
            output_tokens=0,
            credits_used="0",
            finish_reason="stop",
            structured_output=(),
        )


def _deep_shaped_recording() -> Any:
    """A recording of the shape the deep pass emits — LLM-derived by rule-id provenance."""
    from argus.audit.deep_pass import RULE_DEGRADED_DEEP_READ

    return build_recording(
        FindingDraft(
            file_path="app/service.py",
            start_line=1,
            end_line=1,
            rule_id=f"{RULE_DEGRADED_DEEP_READ}:empty-response",
            advisory=True,
        ),
        depth_supported=None,
        claim_present=False,
    )


def test_TC_ArgusAgent_CACHE_001_96_the_fence_refuses_llm_derived_recordings(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-CACHE-001-96 — AC6.1 THE FENCE, in both directions.

    §D.2's hazard, restated because the fence is meaningless without it: the cache key folds
    ``model_checkpoint`` and ``prompt_template_version``, but in V1 both are FIXED SENTINELS
    that do not vary with the model a run actually used. So memoizing deep-pass output under
    this key would let **two runs against two different models collide on one slot**. The fence
    makes that impossible at the store's write path — the choke point — rather than by comment.

    BOTH directions are asserted, because a guard that only ever rejects cannot be shown to be
    reachable and one that only ever accepts cannot be shown to bite:

    * REFUSED — an LLM-derived recording under the V1 placeholder closure raises, and the
      message NAMES the model-collision hazard so whoever hits it learns why rather than
      learning how to silence it.
    * ACCEPTED — the same payload under a REAL captured checkpoint is stored without complaint.
      The fence stands down BY ITSELF once the key can tell two models apart, which is what
      makes it a fence around a key that cannot yet discriminate rather than a permanent ban on
      deep memoization.
    """
    from argus.cache.memo_store import DeepMemoizationFenceError

    store = MemoStore(tmp_path / "repo")
    poisoned = RecordedStageResult(entries=(), findings=(_deep_shaped_recording(),), candidates=())

    with pytest.raises(DeepMemoizationFenceError) as excinfo:
        store.store_stage(
            "k" * 64,
            poisoned,
            model_checkpoint=V1_MODEL_CHECKPOINT,
            prompt_template_version=V1_PROMPT_TEMPLATE_VERSION,
        )
    message = str(excinfo.value)
    for phrase in ("COLLIDE ON", "model A", "model B", "DOES NOT VARY WITH THE MODEL"):
        assert phrase in message, (
            f"the fence's failure message does not name the model-collision hazard ({phrase!r} "
            f"missing). A refusal that does not say WHY teaches the next reader to route around "
            f"it. Message was:\n{message}"
        )
    assert not (tmp_path / "repo" / ".argus" / "cache").exists() or not list(
        (tmp_path / "repo" / ".argus" / "cache").iterdir()
    ), "the refused payload was written to disk anyway — the fence must refuse BEFORE the write"

    # The other direction: a real captured checkpoint means the key CAN discriminate.
    locator = store.store_stage(
        "k" * 64,
        poisoned,
        model_checkpoint="a-real-captured-checkpoint",
        prompt_template_version="argus-deep-v1",
    )
    assert locator, (
        "the fence refused a payload whose closure carries a REAL captured checkpoint. That is "
        "over-blocking: once the key varies with the model, two models can no longer collide "
        "and the hazard this fence exists for does not apply."
    )

    # And an ordinary deterministic payload is never touched by the fence.
    assert store.store_stage(
        "j" * 64,
        RecordedStageResult(entries=(), findings=(_poison_finding("app/service.py"),), candidates=()),
        model_checkpoint=V1_MODEL_CHECKPOINT,
        prompt_template_version=V1_PROMPT_TEMPLATE_VERSION,
    ), "the fence blocked a purely deterministic payload — it must fire on LLM provenance only"


def test_TC_ArgusAgent_CACHE_001_97_the_fence_prefix_cannot_drift_from_the_live_rule() -> None:
    """TC-ArgusAgent-CACHE-001-97 — AC6.1: the fence's vocabulary is closed over LIVE structure.

    ``memo_store`` cannot import ``argus.audit.deep_pass`` — that module pulls the dispatch
    surface and nothing may drag it onto the memoization path (NFR-S6) — so the fence names the
    deep-pass rule stem as a LITERAL. A literal is a snapshot, and a snapshot rots: rename
    ``RULE_DEGRADED_DEEP_READ`` and the fence would silently stop matching anything while
    staying green.

    This test is the join the fence cannot make for itself. It lives in the test layer, where
    importing ``deep_pass`` is free, and it fails the moment the two drift apart.
    """
    from argus.audit.deep_pass import RULE_DEGRADED_DEEP_READ
    from argus.cache.memo_store import LLM_DERIVED_RULE_PREFIXES

    assert LLM_DERIVED_RULE_PREFIXES, "the fence's prefix set is EMPTY — it can match nothing"
    assert RULE_DEGRADED_DEEP_READ in LLM_DERIVED_RULE_PREFIXES, (
        f"the deep pass's live rule stem {RULE_DEGRADED_DEEP_READ!r} is not in the fence's "
        f"prefix set {LLM_DERIVED_RULE_PREFIXES}. memo_store cannot import deep_pass (NFR-S6), "
        "so this assertion is the only thing keeping the two in step — update the literal in "
        "argus/cache/memo_store.py rather than relaxing this test."
    )


def test_TC_ArgusAgent_CACHE_001_98_deep_audit_hits_the_stage_but_never_serves_the_deep_pass(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-CACHE-001-98 — AC6.2 and the §D.3 scope, made observable.

    Three claims in one run, all zero-token and socket-free (an INJECTED port; no adapter is
    ever constructed, §0.3(c)):

    1. **The deterministic component still HITS** with ``--deep-audit`` on — enabling the deep
       pass does not disable memoization of the stage upstream of it.
    2. **The deep component is NOT served.** The injected port dispatches AGAIN on the warm
       run. This is the honest, disclosed limitation (``DF-12-3-A``): with ``--deep-audit`` on,
       a re-run dispatches again and PRD §501 is NOT delivered. Asserting the opposite is what
       would make this story a false claim.
    3. **No LLM-derived recording is in the persisted payload** — checked against the actual
       cache slot BYTES, so it is a fact about what was stored rather than about what the code
       intended to store. This is what makes claim 2 safe rather than merely disappointing.
    """
    from argus.cache.memo_store import LLM_DERIVED_RULE_PREFIXES

    repo = _clean_repo(tmp_path / "repo", modules=3)
    passes = ("coverage", "vacuous", "security", "orphan", "deep")
    spy = _spy_on_detect_stage(monkeypatch)

    port_cold = _FakeDispatch()
    run_audit_detailed(_request(repo, enabled_passes=passes), deep_port=port_cold)
    assert spy.calls == 1, "the cold deep run must execute the deterministic stage once"
    assert port_cold.calls > 0, (
        "the injected port was never dispatched, so this test never exercised the deep pass "
        "at all and claim 2 below would be vacuously true"
    )

    port_warm = _FakeDispatch()
    run_audit_detailed(_request(repo, enabled_passes=passes), deep_port=port_warm)

    assert spy.calls == 1, (
        "with --deep-audit on, the DETERMINISTIC stage re-executed instead of hitting. The "
        "memo hook sits upstream of the deep pass, so enabling the deep pass must not disable "
        "memoization of the stage before it."
    )
    assert port_warm.calls == port_cold.calls, (
        f"the deep pass dispatched {port_warm.calls} times on the warm run vs {port_cold.calls} "
        "on the cold one. Story 12.3 does NOT memoize deep output (DF-12-3-A); if this count "
        "ever drops to zero, deep-pass output IS being served from the store and the "
        "model-collision hazard of §D.2 has gone live."
    )

    slots = _cache_slots(repo)
    assert slots, "no slot was persisted, so the byte check below would sweep nothing"
    for slot in slots:
        raw = slot.read_bytes()
        for prefix in LLM_DERIVED_RULE_PREFIXES:
            assert prefix.encode("utf-8") not in raw, (
                f"an LLM-derived rule id ({prefix!r}) is present in the persisted cache slot "
                f"{slot.name}. The deep pass runs DOWNSTREAM of the memo hook precisely so "
                "this cannot happen; if it has, the hook has moved and the fence is the only "
                "thing left between this cache and a two-model slot collision."
            )


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — an EXISTING requirement is delivered; no new surface is created
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_CACHE_001_99_this_story_added_no_requirement_surface() -> None:
    """TC-ArgusAgent-CACHE-001-99 — AC1.2/AC1.3: FR27 is DELIVERED, nothing is INVENTED.

    Story 12.3 delivers a requirement that already existed. It is therefore an error for it to
    have moved any consumer-visible contract, and each of those contracts is closed over live
    structure here rather than eyeballed: the verdict vocabulary, the FR16 decision rows, the
    exit-code mapping, the request model's field set, and the accepted CLI surface.

    The CLI check is the sharpest: §0.6/DN-3 ruled that this story adds NO flag — not
    ``--no-cache``, not ``--cache-dir``, not ``--refresh``. Wiping ``.argus/cache/`` is already
    the escape hatch (`-88` proves it works), and the invocation contract has been LOCKED since
    Story 10.3.
    """
    from argus.cli import build_parser
    from argus.verdict.verdict_gate import DecisionRow, Verdict as _Verdict

    assert {member.value for member in _Verdict} == {
        "RELEASE_READY",
        "NOT_READY_FOR_RELEASE",
        "INSUFFICIENT_COVERAGE",
    }, "the verdict vocabulary moved — this story may not add, remove or rename a verdict"
    assert {member.value for member in DecisionRow} == {
        "row_1_below_floor",
        "row_2_blocking_findings",
        "row_3_gates_met",
        "row_4_gate_unmet_no_findings",
    }, "an FR16 decision row moved — this story changes no row, threshold or mapping"

    flags = {
        option
        for action in build_parser()._actions  # noqa: SLF001 — the parser's own accepted surface
        for option in action.option_strings
    }
    forbidden = {"--no-cache", "--cache-dir", "--refresh", "--cache", "--memo", "--no-memo"}
    assert not (flags & forbidden), (
        f"this story added a cache CLI flag ({sorted(flags & forbidden)}). §0.6 ruled it out: "
        "no requirement asks for one, the invocation contract is LOCKED (Story 10.3), and "
        "memo_store's own invariant makes an override unnecessary for correctness."
    )
    assert "coverage_scope" in AuditRequest.model_fields, (
        "sanity: the request model is being read live, so the absence check above is real"
    )
    assert not (set(AuditRequest.model_fields) & {"cache", "no_cache", "cache_dir", "refresh"}), (
        "this story added a cache field to AuditRequest — the request contract is unchanged"
    )


def test_TC_ArgusAgent_CACHE_001_100_no_second_hasher_serializer_or_key_function() -> None:
    """TC-ArgusAgent-CACHE-001-100 — AC1.4: ONE key function, ONE serializer, ONE hasher.

    ``key.py`` says it plainly: *"NFR-P1 (byte-identical) dies the day a second ``json.dumps``
    or second hasher appears."* The modules this story added are the most likely place for one
    to appear, because composing a key and writing a payload is exactly the work that tempts a
    quick ``hashlib.sha256(json.dumps(...))``.

    Asserted over the modules' own SOURCE, so it catches the import that a behavioural test
    would not: a second hasher producing the same answer today is still a second hasher.
    """
    import argus.cache.memo_store as memo_store_module
    import argus.cache.stage_memo as stage_memo_module

    for module in (stage_memo_module, memo_store_module):
        source = Path(module.__file__).read_text(encoding="utf-8")
        code = "\n".join(
            line for line in source.splitlines() if not line.lstrip().startswith("#")
        )
        for banned in ("import hashlib", "hashlib.", "json.dumps", "json.loads", "import json"):
            assert banned not in code, (
                f"{module.__name__} contains {banned!r}. Every hash on this path must compose "
                "the single content-hash (store/envelope.compute_content_hash) and every "
                "serialization the single canonical serializer (store/canonical) — a second "
                "one is how byte-identity dies quietly (AR4/AR5)."
            )

    stage_source = Path(stage_memo_module.__file__).read_text(encoding="utf-8")
    assert "derive_cache_key" in stage_source, (
        "the composition module must CONSUME the one key function (AR5), never hand-compose a "
        "key (architecture §722)"
    )
