"""ArgusAgent-CACHE — IS the memoization wired, and is it LOAD-BEARING? (FR27 / NFR-D1, Story 12.3).

Verification area: ``TC-ArgusAgent-CACHE-001-81``.. — CONTINUING the existing ``CACHE`` index
(the highest committed id before this story is ``-80``) rather than minting a new one. ``CACHE``
is chosen over ``PIPELINE`` because every assertion here is about *the cache* — that it is
consulted, that it is load-bearing, that a moved key misses. The pipeline is the site, not the
subject.

This file answers ONE question: **did the store actually get wired, and does a hit really serve?**
Whether the cache can LIE is the sibling file's subject (``tests/test_stage_memo_contract.py``);
the two were split along that cohesion boundary when the pair outgrew the NFR-M1 ceiling, and
they share ``tests/_stage_memo_corpus.py`` so both observe the same seam.

🔴 WHY THIS FILE EXISTS AT ALL — READ BEFORE ADDING A TEST HERE.
A re-run byte-identity test passes on this tree WITH NO CACHE IN EXISTENCE. Story 3.5 already
ships one (``TC-ArgusAgent-PIPELINE-001-37``) and it is green. So byte-identity is NOT evidence
for this story: it measures Epic 3's determinism and would label it Epic 5's. Every load-bearing
test here therefore carries one of the two controls that a permanently-cold cache CANNOT pass:

  * **CONTROL 1 — PROVE THE HIT.** A spy on the real ``_detect_per_file`` seam counts stage
    executions. Cold must execute exactly once; warm must execute ZERO times. A byte-identity
    assertion without this is not evidence of anything.
  * **CONTROL 2 — THE POISON POSITIVE CONTROL.** A validly-enveloped, integrity-correct,
    schema-valid but DIFFERENT recorded result is placed in the slot the next run will read, and
    the run's VERDICT must change. If it does not change, the store is not being consulted and
    the wiring is vacuous no matter how green everything else is.

Drivers: FR27 (*the same verdict for the same repository and Argus version*), NFR-D1 (*local
content-addressed memoization — the mechanism, not an assumption that the LLM repeats itself*),
NFR-D2 (zero LLM tokens), NFR-P1 (a HIT round-trips byte-identically to the recompute), AR5 (ONE
cache-key function — consumed, never re-derived), AR7 (reuse the store, the key and the envelope
by import — no fork).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from argus.cache.key import (
    CACHE_KEY_SCHEMA_VERSION,
    DetectorDescriptor,
    RecordingProducingClosure,
    V1_MODEL_CHECKPOINT,
    V1_PROMPT_TEMPLATE_VERSION,
    derive_cache_key,
)
from argus.cache.memo_store import MEMO_STORE_SCHEMA_VERSION, MemoStore, RecordedStageResult
from argus.cli import main
from argus.pipeline import run_audit_detailed
from argus.verdict.verdict_gate import Verdict

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
# CONTROL 1 — PROVE THE HIT (AC3.2, the non-vacuity core)
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_CACHE_001_81_warm_run_does_not_execute_the_detect_stage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-CACHE-001-81 — AC3.2: run 1 MISSES and computes; run 2 HITS and does not.

    THE NON-VACUITY CORE OF THE WHOLE STORY. Byte-identity across two runs is already true on
    this tree with no cache at all (``TC-ArgusAgent-PIPELINE-001-37``), so the only assertion
    that distinguishes *served from the store* from *recomputed identically* is that the second
    run DID NOT RUN THE STAGE. This test is deliberately blind to the output bytes: `-83` owns
    those, and it is only evidence because this one exists.

    It also kills the PERMANENTLY-COLD CACHE (§E.1 shape 2): a store whose key derivation raises,
    whose lookup always misses, or whose write silently fails leaves every byte-identity
    assertion green and turns this one red.
    """
    repo = _clean_repo(tmp_path / "repo")
    spy = _spy_on_detect_stage(monkeypatch)

    assert _cache_slots(repo) == (), "the cache must start cold — this run is the MISS"
    run_1 = run_audit_detailed(_request(repo))
    assert spy.calls == 1, (
        f"the COLD run must execute the detect/grade stage exactly once, saw {spy.calls}. "
        "A cold run that did not execute it audited nothing."
    )
    slots_after_cold = _cache_slots(repo)
    assert len(slots_after_cold) == 1, (
        f"the cold run must PERSIST exactly one memo slot, found {len(slots_after_cold)}: "
        f"{[p.name for p in slots_after_cold]}. With no slot written there is nothing for a "
        "warm run to serve, and every byte-identity assertion in this file would still pass — "
        "that is the permanently-cold cache this control exists to catch."
    )

    run_2 = run_audit_detailed(_request(repo))
    assert spy.calls == 1, (
        f"the WARM run RE-EXECUTED the detect/grade stage (total calls {spy.calls}, expected to "
        "stay at 1). The memo store was not consulted, or its lookup missed. The run is still "
        "CORRECT — which is exactly why no byte-identity test can see this defect, and why this "
        "assertion is the one that matters."
    )
    assert _cache_slots(repo) == slots_after_cold, (
        "a HIT must not write a second slot — the slot is content-addressed by the 5.1 key "
        "(AR11), so the same closure must resolve to the same slot, never to a new one"
    )
    assert run_1.verdict.verdict == run_2.verdict.verdict


# ─────────────────────────────────────────────────────────────────────────────
# CONTROL 2 — THE POISON POSITIVE CONTROL (AC4.1, the killer)
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_CACHE_001_82_a_poisoned_slot_changes_the_verdict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-CACHE-001-82 — AC4.1 THE POISON POSITIVE CONTROL. The killer test.

    Everything else in this story can be green over a cache that is never read. This cannot.
    A **validly enveloped, integrity-correct, schema-valid but DIFFERENT** recorded result is
    written into the slot the next run will read — through the REAL store, so the envelope
    ``content_hash`` is correct and the AR6 tamper guard has no reason to reject it — and the
    next run's VERDICT must change.

    Note the polarity, because it is the mirror of `-86`: that test proves a TAMPERED entry is
    REFUSED. This one proves a WELL-FORMED entry is SERVED. A store that refuses everything
    passes `-86` and fails this; a store that is never consulted passes every byte-identity
    test in this file and fails this. Only both together say the cache is load-bearing AND
    honest — the `-73`/`-74` discipline Story 12.2 established, applied to the cache.
    """
    repo = _clean_repo(tmp_path / "repo")

    cold = run_audit_detailed(_request(repo))
    assert cold.verdict.verdict is Verdict.RELEASE_READY, (
        f"fixture precondition: the clean corpus must audit RELEASE_READY, got "
        f"{cold.verdict.verdict}. Without that, a changed verdict below would prove nothing."
    )
    slots = _cache_slots(repo)
    assert len(slots) == 1, (
        f"no memo slot was written, so there is nothing to poison ({len(slots)} slots). "
        "The wiring is absent or the store write failed silently."
    )

    # The key is READ OFF THE LIVE SLOT, never recomputed here — a test that re-derives the
    # key would pass even if production derived a different one (the self-comparison trap,
    # §E.1 shape 3).
    key = slots[0].stem
    store = MemoStore(repo)
    served = store.lookup_stage(key)
    assert served is not None, (
        "the slot the production run wrote must be readable through the SAME store the "
        "production run reads — if it is not, the run below cannot possibly have hit it"
    )

    poisoned = RecordedStageResult(
        entries=served.entries,
        findings=served.findings + (_poison_finding("app/service.py"),),
        candidates=served.candidates,
    )
    store.store_stage(
        key,
        poisoned,
        model_checkpoint=V1_MODEL_CHECKPOINT,
        prompt_template_version=V1_PROMPT_TEMPLATE_VERSION,
    )

    spy = _spy_on_detect_stage(monkeypatch)
    warm = run_audit_detailed(_request(repo))

    assert spy.calls == 0, (
        f"the poisoned run re-executed the detect stage {spy.calls} time(s), so it recomputed "
        "instead of serving. The verdict assertion below would then be measuring the detectors, "
        "not the store."
    )
    assert warm.verdict.verdict is not Verdict.RELEASE_READY, (
        "THE STORE IS NOT LOAD-BEARING. A valid, integrity-correct, schema-valid recorded "
        "result carrying a verdict-BLOCKING finding was placed in the slot this run reads, and "
        "the run still returned RELEASE_READY — so the served payload never reached the verdict "
        "fold. Every byte-identity assertion in this file can be green in this state, which is "
        "precisely why this is the assertion that decides whether Story 12.3 is delivered."
    )
    assert warm.verdict.blocking_finding_count >= 1, (
        "the poisoned finding must arrive as a VERDICT-BLOCKING finding, otherwise the verdict "
        f"moved for some other reason: blocking_finding_count={warm.verdict.blocking_finding_count}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — the CORRECTED key is what gets consumed (the 10.2 dependency, discharged)
# ─────────────────────────────────────────────────────────────────────────────


def _live_closure(repo: Path, **overrides: object) -> RecordingProducingClosure:
    """Build the closure the PRODUCTION path would build for *repo* (never a hand-built stub).

    Runs the real intake + index, then calls the real ``build_stage_closure``. A test that
    hand-assembled a closure here would be asserting over its own fixture rather than over what
    the pipeline actually derives — the self-comparison trap (§E.1 shape 3).
    """
    from argus.cache.stage_memo import build_stage_closure
    from argus.index.ast_index import build_ast_index
    from argus.intake.source_state import resolve_source_state

    request = _request(repo, **overrides)
    source_state = resolve_source_state(request.repo_path, commit=request.commit)
    index = build_ast_index(repo, source_state.source_files, partition_id="root")
    return build_stage_closure(
        request=request,
        index=index,
        assessed_entries=index.entries,
        source_state=source_state,
    )


def test_TC_ArgusAgent_CACHE_001_83_closure_folds_the_live_grammar_provenance(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-CACHE-001-83 — AC2.1: per-grammar provenance comes from the LIVE index.

    The 10.2 correction (``DF-AUD-APAA-D``) only pays off if the PRODUCTION closure carries the
    grammars that ACTUALLY PARSED. Two ways to get this wrong are both silently green under a
    byte-identity test: hand-listing a language set (which goes stale), and folding every
    grammar INSTALLED on the host (which keys the cache on the machine instead of the audit —
    DN-6, the exact inverse of the defect being closed).

    So the assertion closes over LIVE structure in both directions: what the closure carries is
    IDENTICAL to what the index recorded, and it is exactly the languages this corpus actually
    contains — never the host's installed set.
    """
    from argus.index.ast_index import build_ast_index
    from argus.intake.source_state import resolve_source_state

    repo = _clean_repo(tmp_path / "repo")
    source_state = resolve_source_state(str(repo), commit="HEAD")
    index = build_ast_index(repo, source_state.source_files, partition_id="root")
    closure = _live_closure(repo)

    assert index.grammar_versions, (
        "fixture precondition: the index recorded NO grammar provenance, so the assertion "
        "below would be vacuously true over an empty tuple"
    )
    assert closure.grammar_versions == index.grammar_versions, (
        "the closure must fold the index's OWN per-grammar provenance verbatim.\n"
        f"  index:   {index.grammar_versions}\n  closure: {closure.grammar_versions}"
    )
    languages = {record.language for record in closure.grammar_versions}
    assert languages == {"python"}, (
        f"this corpus is Python-only, so exactly one grammar can have parsed; got {languages}. "
        "A larger set means the host's INSTALLED grammars leaked into the key (DN-6) and the "
        "cache has become a function of the machine rather than of the audit."
    )
    assert closure.content_hash == source_state.identity, (
        "the audited unit's content hash must be the intake's own content-faithful identity — "
        "reusing the existing digest rather than introducing a second hasher (AC1.4)"
    )


def test_TC_ArgusAgent_CACHE_001_84_cache_key_schema_version_was_not_bumped() -> None:
    """TC-ArgusAgent-CACHE-001-84 — AC2.2: this story did NOT move CACHE_KEY_SCHEMA_VERSION.

    Story 10.2 bumped it to ``"3"`` DELIBERATELY and at a commit where the bump was free — no
    production caller derived a key and no persisted entry existed to migrate — precisely so
    that 12.3, which wires the store over that corrected key, would not have to pay a migration.
    Bumping it here would waste that ordering, and the value is asserted rather than remembered
    so that a later edit has to argue with a committed test.

    ``MEMO_STORE_SCHEMA_VERSION`` is a DIFFERENT constant with a different contract, and this
    story DID move it (``"1"`` → ``"2"``, DN-2). Both are pinned here so the two can never be
    mistaken for one another.
    """
    assert CACHE_KEY_SCHEMA_VERSION == "3", (
        "CACHE_KEY_SCHEMA_VERSION moved. It is the CACHE KEY schema, not the memo payload "
        "schema; 10.2 already paid this cost so 12.3 would not have to, and every entry "
        "persisted since the store was wired would now be unreachable."
    )
    assert MEMO_STORE_SCHEMA_VERSION == "2", (
        "MEMO_STORE_SCHEMA_VERSION must be '2' — Story 12.3 widened the memo payload from "
        "findings-only to entries+findings+candidates (DN-2), and the bump is what stops an "
        "old-shape entry from being served under the new shape."
    )


def _perturbations() -> dict[str, object]:
    """One key-moving perturbation per LIVE closure field (CONTROL 4 — never a hand list).

    The KEYS of this map are checked against ``RecordingProducingClosure.model_fields`` by
    `-85`, so a field added to the closure later cannot escape the matrix: the guard goes red
    until someone states how that field moves the key. A hand-written list would be a snapshot;
    this is a closure over the model.
    """
    from argus.cache.key import GrammarProvenance

    return {
        "content_hash": "0" * 64,
        "detectors": (
            DetectorDescriptor(rule_id="hardcoded_secret", code_identity="secret_scan.v99"),
        ),
        "grammar_version": "99.99.99",
        "grammar_versions": (GrammarProvenance(language="python", version="99.99.99"),),
        "tool_versions": {"radon": "99.99.99"},
        "budget": 4242,
        "materiality_bar": "critical-only",
        "work_manifest_files": ("app/service.py", "app/added_later.py"),
        "critical_paths": ("app/service.py",),
        "excluded_critical_paths": ("app/service.py",),
        "model_checkpoint": "a-real-captured-checkpoint",
        "prompt_template_version": "argus-deep-v1",
    }


def test_TC_ArgusAgent_CACHE_001_85_every_live_closure_field_moves_the_key(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-CACHE-001-85 — AC2.3: the key is a faithful function of the whole closure.

    A cache key that ignores one of its inputs is how a store serves a result computed under a
    configuration nobody asked for. The population is DERIVED from the live model (Control 4)
    and asserted non-empty, so this cannot pass by iterating over nothing, and a closure field
    added tomorrow turns it red rather than slipping through unfingerprinted.
    """
    live_fields = set(RecordingProducingClosure.model_fields)
    assert live_fields, "RecordingProducingClosure exposes no fields — the walk sees nothing"
    perturbations = _perturbations()
    assert set(perturbations) == live_fields, (
        "the perturbation matrix and the LIVE closure model have diverged.\n"
        f"  unexercised live fields: {sorted(live_fields - set(perturbations))}\n"
        f"  stale perturbations: {sorted(set(perturbations) - live_fields)}\n"
        "Every determinism-relevant input must be shown to move the key; a field nobody "
        "perturbs is a field the key may silently ignore."
    )

    baseline = _live_closure(_clean_repo(tmp_path / "repo"))
    baseline_key = derive_cache_key(baseline)
    for field, value in sorted(perturbations.items()):
        moved = baseline.model_copy(update={field: value})
        assert derive_cache_key(moved) != baseline_key, (
            f"changing closure field {field!r} did NOT move the cache key. Two runs differing "
            f"in {field!r} would collide on ONE slot and the second would be served the first's "
            "answer — a memoization hit returning a result produced by a DIFFERENT closure, "
            "which is the single failure cache/key.py exists to make impossible."
        )


def test_TC_ArgusAgent_CACHE_001_86_a_changed_input_is_a_natural_miss_end_to_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-CACHE-001-86 — AC2.4: a real input change lands on a DIFFERENT slot.

    Proven END TO END through ``run_audit_detailed``, not at the key function: the key moving in
    isolation says nothing about whether the production path folds that input at all. Three
    genuinely different inputs are exercised — changed source bytes, a changed ``budget`` and a
    changed materiality bar — and each must produce a NEW slot and a re-executed stage.

    The MISS must be NATURAL: it arrives because the closure moved, not because anything was
    evicted, invalidated or deleted. That is the Story 5.2/5.3 fence — a detector-set edit
    ALREADY changes the key → a different slot → a natural miss; ACTIVE eviction is 5.3 and out
    of scope here (see `-95`).
    """
    repo = _clean_repo(tmp_path / "repo")
    spy = _spy_on_detect_stage(monkeypatch)

    run_audit_detailed(_request(repo))
    assert spy.calls == 1
    assert len(_cache_slots(repo)) == 1

    # (a) changed SOURCE bytes — the audited unit's content identity moves.
    (repo / "app" / "service.py").write_text(
        _APP_SOURCE + "\n\ndef divide(a: int, b: int) -> float:\n    return a / b\n",
        encoding="utf-8",
    )
    run_audit_detailed(_request(repo))
    assert spy.calls == 2, "a changed source file must MISS and recompute, never serve a stale hit"
    assert len(_cache_slots(repo)) == 2, (
        "a changed source file must land on a NEW slot — the old slot is not overwritten, "
        "because the slot is content-addressed by the key (AR11)"
    )

    # (b) changed BUDGET — a recorded config input of the closure.
    run_audit_detailed(_request(repo, budget=97))
    assert spy.calls == 3, "a changed --budget must MISS"
    assert len(_cache_slots(repo)) == 3

    # (c) changed MATERIALITY BAR.
    run_audit_detailed(_request(repo, materiality_bar="critical-only"))
    assert spy.calls == 4, "a changed materiality bar must MISS"
    assert len(_cache_slots(repo)) == 4

    # And the ORIGINAL closure still HITS its own slot — a moved key must not have
    # invalidated everything, which would be a cache that never serves anything at all.
    run_audit_detailed(_request(repo, budget=97))
    assert spy.calls == 4, "re-running an already-recorded closure must HIT, not recompute"


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — HIT == COLD, byte-identical, WITH THE HIT PROVEN
# ─────────────────────────────────────────────────────────────────────────────


def _snapshot(repo: Path, report_dir: Path) -> dict[str, bytes]:
    """Every artifact a run produced, EXCEPT the cache slot itself (AC3.1).

    ⚠️ WHICH COMPARISON THIS IS (§0.5 trap 2): a WORKING-TREE byte comparison, and that is the
    correct one here. Both sides are written at RUNTIME by the process under test into a
    ``tmp_path``; neither side is a committed git blob, so ``core.autocrlf`` never rewrites
    either of them and a blob comparison would have nothing to read. The blob comparison is the
    correct one only when the claim is about COMMITTED content — it is not, here.

    The cache tree is excluded because it is the one artifact that MUST differ: a cold run
    writes a slot that did not exist. Everything else must be identical byte for byte.
    """
    snapshot: dict[str, bytes] = {}
    for root, label in ((repo / ".argus", "argus"), (report_dir, "report")):
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if label == "argus" and relative.startswith("cache/"):
                continue
            snapshot[f"{label}/{relative}"] = path.read_bytes()
    return snapshot


@pytest.mark.parametrize(
    ("corpus", "expected_release_ready"),
    [("clean", True), ("blocked", False)],
    ids=["release_ready", "not_release_ready"],
)
def test_TC_ArgusAgent_CACHE_001_87_a_served_run_is_byte_identical_to_a_computed_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    corpus: str,
    expected_release_ready: bool,
) -> None:
    """TC-ArgusAgent-CACHE-001-87 — AC3.1/AC3.2/AC3.3: a HIT equals a COLD run, hit PROVEN.

    This is the story's headline property, and on its own it would be worthless: two runs of
    this pipeline are byte-identical on this tree WITH NO CACHE AT ALL. What makes it evidence
    is the ``spy.calls`` assertion — run 2 produced these bytes WITHOUT EXECUTING THE STAGE, so
    the equality is between a SERVED answer and a COMPUTED one, not between two computations.

    AC3.3 / DN-8 — run over TWO VERDICT CLASSES. A proof pinned only to ``RELEASE_READY`` could
    be green because the finding set is empty and an empty tuple round-trips through a broken
    store perfectly. The ``leaky`` corpus carries a real secret-scan finding, so the served
    payload has something to be wrong about.

    Compared: exit code, stdout, stderr, every rendered report file and every ``.argus/``
    artifact except the cache slot. See ``_snapshot`` for which comparison kind this is.
    """
    repo = (_clean_repo if corpus == "clean" else _blocked_repo)(tmp_path / "repo")
    # ONE report directory, used by BOTH runs. AC3.1 says *identical flags*, and `--report-dir`
    # is a flag: pointing the two runs at different directories makes the persisted run-state
    # artifact legitimately differ (the request is part of that payload), which would be a
    # difference this test manufactured rather than one the cache caused. The reports are
    # overwritten in place, so the cold snapshot is taken BEFORE the warm run begins.
    report_dir = tmp_path / "reports"
    argv = ["audit", str(repo), "--report-dir", str(report_dir)]

    spy = _spy_on_detect_stage(monkeypatch)

    exit_cold = main(list(argv))
    captured = capsys.readouterr()
    stdout_cold, stderr_cold = captured.out, captured.err
    snapshot_cold = _snapshot(repo, report_dir)
    assert spy.calls == 1, f"the cold run must execute the stage exactly once, saw {spy.calls}"
    assert (exit_cold == 0) is expected_release_ready, (
        f"fixture precondition: the {corpus!r} corpus exited {exit_cold}; this parametrisation "
        "exists to cover BOTH a RELEASE_READY and a non-RELEASE_READY outcome, and it is not "
        "covering what it claims if both legs land on the same verdict class."
    )
    assert snapshot_cold, "the cold run produced no artifacts at all — nothing to compare"

    exit_warm = main(list(argv))
    captured = capsys.readouterr()
    stdout_warm, stderr_warm = captured.out, captured.err
    snapshot_warm = _snapshot(repo, report_dir)

    assert spy.calls == 1, (
        f"THE WARM RUN RECOMPUTED (stage calls {spy.calls}, expected to stay at 1). Every "
        "equality below would still hold — that is precisely the vacuity this assertion "
        "exists to prevent. Without a proven HIT, byte-identity measures determinism (Epic 3), "
        "not memoization (Epic 5)."
    )
    assert exit_warm == exit_cold, f"exit code moved: cold {exit_cold} → warm {exit_warm}"
    assert stdout_warm == stdout_cold, "stdout differs between a computed run and a served one"
    assert stderr_warm == stderr_cold, "stderr differs between a computed run and a served one"
    assert set(snapshot_warm) == set(snapshot_cold), (
        "the served run produced a different SET of artifacts.\n"
        f"  only cold: {sorted(set(snapshot_cold) - set(snapshot_warm))}\n"
        f"  only warm: {sorted(set(snapshot_warm) - set(snapshot_cold))}"
    )
    differing = [name for name, blob in snapshot_cold.items() if snapshot_warm[name] != blob]
    assert not differing, (
        f"a SERVED run is not byte-identical to a COMPUTED one. Differing artifacts: "
        f"{differing}. A cache that changes an answer is worse than no cache: architecture.md "
        "calls the cache a CORRECTNESS SURFACE for exactly this reason."
    )


def test_TC_ArgusAgent_CACHE_001_88_wiping_the_cache_restores_cold_behaviour(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-CACHE-001-88 — AC3.4: correct whether the cache exists, is warm, or is wiped.

    ``memo_store.py`` states this as an invariant in prose; here it is ASSERTED rather than
    assumed. It is also the reason Story 12.3 needs no ``--no-cache`` flag (§0.6/DN-3): wiping
    ``.argus/cache/`` already IS the escape hatch, so an operator control would be a second way
    to do something that already works.

    Three states are exercised in order — cold, warm, wiped — and the wiped run must both
    RE-EXECUTE the stage (proving the wipe really took effect, not just that the answer
    survived) and return the identical verdict.
    """
    repo = _blocked_repo(tmp_path / "repo")
    spy = _spy_on_detect_stage(monkeypatch)

    cold = run_audit_detailed(_request(repo))
    assert spy.calls == 1
    warm = run_audit_detailed(_request(repo))
    assert spy.calls == 1, "precondition: the second run must have HIT for the wipe to mean anything"

    for slot in _cache_slots(repo):
        slot.unlink()
    assert _cache_slots(repo) == (), "the wipe did not empty .argus/cache/"

    wiped = run_audit_detailed(_request(repo))
    assert spy.calls == 2, (
        f"the wiped run did NOT re-execute the stage (calls {spy.calls}). Either the wipe was "
        "ineffective or the result was served from somewhere other than the wiped tree — "
        "either way this test is not measuring what it says."
    )
    assert wiped.verdict.verdict == cold.verdict.verdict == warm.verdict.verdict, (
        "the verdict is not invariant across cold / warm / wiped, which breaks the store's own "
        "stated invariant and would make the cache a correctness dependency rather than an "
        "optimization"
    )
    assert wiped.verdict.blocking_finding_count == cold.verdict.blocking_finding_count
    assert len(_cache_slots(repo)) == 1, "the wiped run must re-record the slot it recomputed"
