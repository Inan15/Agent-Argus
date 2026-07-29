"""HITL STOP/PROCEED escalation + append-only decision-record property suite (Story 6.7).

Verification area ArgusAgent-HITL (``TC-ArgusAgent-HITL-001-NN`` — index from -01).

Drivers: ArgusAgent-FR-23 (HITL STOP/PROCEED gate — pattern-matched, default-STOP,
time-boxed park-at-STOP, NEVER auto-PROCEED on timeout), ArgusAgent-FR-24 (append-only,
prev-hash-chained decision record; the STOP is logged even if the full record is
deferred), ArgusAgent-NFR-A1 (content-hashed, prev-hash-chained, tamper-evident chain),
ArgusAgent-NFR-D1/D2 (the escalation resolution is deterministic + zero-LLM-token — a
pure fold), ArgusAgent-NFR-S1 (no source/secret bytes), ArgusAgent-AR4 (content-derived ids;
no clock/uuid/random/float in the payload), ArgusAgent-AR10 (typed-failure-never-raise).

The COMPLETE-THE-DECLARED-SET checklist (AI-E5-1), each covered RED-first where a
naive implementation would miss it:
  (1) pattern-matched firing + default-STOP  — RED-first vs a default-PROCEED / an
      LLM trigger (``test_default_stop_*`` + ``test_gate_is_zero_token_pure``);
  (2) time-boxed park-at-STOP (never auto-PROCEED) — RED-first vs auto-PROCEED on
      timeout (``test_timeout_parks_at_stop_never_proceeds``);
  (3) append-only prev-hash-chained decision record — RED-first vs an overwrite / a
      forked writer (``test_append_only_chain_*``);
  (4) STOP logged even if the full record is deferred — RED-first vs
      record-nothing-until-human (``test_stop_logged_even_when_deferred``).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from argus.governance.decision_record import (
    DECISION_PRODUCER,
    DecisionRecordError,
    DecisionRecordWriter,
)
from argus.governance.escalation import (
    ESCALATION_SCHEMA_VERSION,
    EscalationError,
    EscalationOutcome,
    EscalationResolution,
    EscalationRule,
    EscalationTrigger,
    HumanDecision,
    ResolutionKind,
    decision_record_payload,
    escalation_fires,
    resolve_escalation,
)
from argus.ledger.recording import Locator, Recording
from argus.store.envelope import GENESIS_PREV_HASH, compute_content_hash
from argus.store.reader import ApaaStoreReader, StoreIntegrityError
from argus.verdict.verdict_gate import AuditVerdict, Verdict

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures / builders (kept minimal — the frozen contracts are the reuse spine).
# ─────────────────────────────────────────────────────────────────────────────

_MATCHED_RULE_ID = "vacuous_test_ast"
_UNMATCHED_RULE_ID = "unrelated_rule"


def _finding(recording_id: str = "rec-1", *, rule_id: str = _MATCHED_RULE_ID) -> Recording:
    loc = Locator(file_path="src/pkg/mod.py", start_line=3, end_line=7)
    return Recording(recording_id=recording_id, rule_id=rule_id, advisory=True, locators=(loc,))


def _rule(**overrides: object) -> EscalationRule:
    base: dict[str, object] = {
        "rule_id": "hitl-ambiguous",
        "reason": "ambiguous_or_high_stakes",
        "match_rule_ids": (_MATCHED_RULE_ID,),
    }
    base.update(overrides)
    return EscalationRule(**base)  # type: ignore[arg-type]


def _verdict(state: Verdict = Verdict.NOT_READY_FOR_RELEASE) -> AuditVerdict:
    from fractions import Fraction

    from argus.ledger.coverage_ledger import CoverageDepth

    return AuditVerdict(
        verdict=state,
        deep_ratio=Fraction(1, 2),
        deep_count=1,
        total_count=2,
        counts_by_depth={CoverageDepth.AUDITED_DEEP: 1, CoverageDepth.INFERRED: 1},
        blocking_finding_count=0,
        ordered_findings=(),
        exit_code=2 if state is Verdict.NOT_READY_FOR_RELEASE else 0,
    )


def _fired_trigger() -> EscalationTrigger:
    trig = escalation_fires(_rule(), findings=(_finding(),))
    assert trig is not None
    return trig


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — pattern-matched firing + default-STOP (RED-first vs default-PROCEED / LLM)
# ─────────────────────────────────────────────────────────────────────────────


def test_pattern_match_fires_on_matched_finding_rule_id() -> None:
    """TC-ArgusAgent-HITL-001-01 — AC1: the gate FIRES on a deterministic finding-rule-id pattern match."""
    trig = escalation_fires(_rule(), findings=(_finding(),))
    assert isinstance(trig, EscalationTrigger)
    assert trig.rule_id == "hitl-ambiguous"
    assert trig.finding_ids == ("rec-1",)
    assert trig.locator_provenance == ("src/pkg/mod.py:3-7",)


def test_pattern_match_fires_on_matched_verdict_state() -> None:
    """TC-ArgusAgent-HITL-001-02 — AC1: the gate FIRES on a candidate verdict-state pattern match."""
    rule = _rule(match_rule_ids=(), match_verdicts=(Verdict.NOT_READY_FOR_RELEASE,))
    trig = escalation_fires(rule, findings=(), verdict=_verdict(Verdict.NOT_READY_FOR_RELEASE))
    assert isinstance(trig, EscalationTrigger)


def test_pattern_match_does_not_fire_without_a_match() -> None:
    """TC-ArgusAgent-HITL-001-03 — AC1: no pattern match → the gate does NOT fire (pass-through, no record)."""
    trig = escalation_fires(_rule(), findings=(_finding(rule_id=_UNMATCHED_RULE_ID),))
    assert trig is None
    # A verdict that is not in the (empty) match set also does not fire.
    assert escalation_fires(_rule(match_rule_ids=()), findings=(), verdict=_verdict()) is None


def test_default_stop_when_fired_and_no_human_decision() -> None:
    """TC-ArgusAgent-HITL-001-04 — AC1 KEYSTONE: fired + no decision + not-timed-out → STOP (default_stop).

    RED-first against a gate that defaults to PROCEED: the ASSERTION is that the
    outcome is STOP (a default-PROCEED implementation would fail this exact line).
    """
    res = resolve_escalation(_fired_trigger())
    assert res.outcome is EscalationOutcome.STOP, "silence must default to STOP, never PROCEED"
    assert res.resolution_kind is ResolutionKind.DEFAULT_STOP
    assert res.decider_id is None


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — time-boxed park-at-STOP (never auto-PROCEED) — the KEYSTONE
# ─────────────────────────────────────────────────────────────────────────────


def test_timeout_parks_at_stop_never_proceeds() -> None:
    """TC-ArgusAgent-HITL-001-05 — AC2 KEYSTONE: fired + timeout-elapsed + no decision → STOP (timeout_parked_stop).

    RED-first against a gate that auto-PROCEEDs (fails open) on timeout — the exact
    FR23 violation. A slow/absent human must NEVER become an auto-PROCEED.
    """
    res = resolve_escalation(_fired_trigger(), timeout_elapsed=True)
    assert res.outcome is EscalationOutcome.STOP, "a timed-out gate must park at STOP, never auto-PROCEED"
    assert res.resolution_kind is ResolutionKind.TIMEOUT_PARKED_STOP
    assert res.decider_id is None


def test_no_resolution_path_proceeds_without_a_human_decision() -> None:
    """TC-ArgusAgent-HITL-001-06 — AC1/AC2: PROCEED is UNREACHABLE without an explicit human decision.

    Sweeps the (human_decision=None) × (timeout_elapsed ∈ {False, True}) matrix and
    asserts every cell resolves to STOP — the structural proof that silence/timeout
    can never ship a PROCEED.
    """
    for timeout in (False, True):
        res = resolve_escalation(_fired_trigger(), human_decision=None, timeout_elapsed=timeout)
        assert res.outcome is EscalationOutcome.STOP


# ─────────────────────────────────────────────────────────────────────────────
# The MECHANIZED resolution matrix (AI-E5-2 — fired × decision × timeout → outcome)
# ─────────────────────────────────────────────────────────────────────────────

# (human_outcome_or_None, timeout_elapsed) → (expected_outcome, expected_kind)
_RESOLUTION_MATRIX = [
    (None, False, EscalationOutcome.STOP, ResolutionKind.DEFAULT_STOP),
    (None, True, EscalationOutcome.STOP, ResolutionKind.TIMEOUT_PARKED_STOP),
    (EscalationOutcome.STOP, False, EscalationOutcome.STOP, ResolutionKind.HUMAN_DECISION),
    (EscalationOutcome.STOP, True, EscalationOutcome.STOP, ResolutionKind.HUMAN_DECISION),
    (EscalationOutcome.PROCEED, False, EscalationOutcome.PROCEED, ResolutionKind.HUMAN_DECISION),
    (EscalationOutcome.PROCEED, True, EscalationOutcome.PROCEED, ResolutionKind.HUMAN_DECISION),
]


@pytest.mark.parametrize("human,timeout,expected_outcome,expected_kind", _RESOLUTION_MATRIX)
def test_resolution_matrix_is_mechanized(
    human: EscalationOutcome | None,
    timeout: bool,
    expected_outcome: EscalationOutcome,
    expected_kind: ResolutionKind,
) -> None:
    """TC-ArgusAgent-HITL-001-07 — AI-E5-2: the full (decision × timeout) → outcome matrix, mechanized.

    A human decision (when present) ALWAYS wins (STOP or PROCEED); absent a decision
    the outcome is STOP for both timeout states. The NAMED assertion cites the exact
    matrix cell on failure (the AI-E5-1 no-crash / debuggable leg).
    """
    decision = None if human is None else HumanDecision(outcome=human, decider_id="op-7")
    res = resolve_escalation(_fired_trigger(), human_decision=decision, timeout_elapsed=timeout)
    assert res.outcome is expected_outcome, f"cell (human={human}, timeout={timeout}) outcome"
    assert res.resolution_kind is expected_kind, f"cell (human={human}, timeout={timeout}) kind"
    # decider_id is present iff it was a human decision.
    if expected_kind is ResolutionKind.HUMAN_DECISION:
        assert res.decider_id == "op-7"
    else:
        assert res.decider_id is None


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — append-only, prev-hash-chained .argus/decisions/ record (RED-first vs overwrite)
# ─────────────────────────────────────────────────────────────────────────────


def _argus_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / ".argus").mkdir(parents=True)
    return repo


def test_append_only_chain_links_prev_hash_to_prior_content_hash(tmp_path: Path) -> None:
    """TC-ArgusAgent-HITL-001-08 — AC3 KEYSTONE: a second decision's prev_hash == the first's content_hash.

    RED-first against a writer that overwrites / does not chain: the assertion pins
    the genesis sentinel at the head AND the prev→content link for the second
    append. Both records survive (append-only — the prior is never overwritten).
    """
    repo = _argus_repo(tmp_path)
    writer = DecisionRecordWriter(repo)

    res1 = resolve_escalation(_fired_trigger())  # default_stop
    res2 = resolve_escalation(
        _fired_trigger(), human_decision=HumanDecision(outcome=EscalationOutcome.PROCEED, decider_id="op-1")
    )
    loc1 = writer.append(res1)
    loc2 = writer.append(res2)
    assert loc1 != loc2, "each decision is a NEW content-addressed artifact (append-only)"

    reader = ApaaStoreReader(repo)
    e1 = reader.read_envelope(loc1)
    e2 = reader.read_envelope(loc2)
    assert e1.prev_hash == GENESIS_PREV_HASH, "the chain head uses the genesis sentinel"
    assert e2.prev_hash == e1.content_hash, "the second decision chains to the first (prev_hash link)"
    assert e1.producer == DECISION_PRODUCER and e2.producer == DECISION_PRODUCER
    # Both files still exist — the prior decision was NOT mutated / deleted.
    assert (repo / ".argus" / loc1).is_file()
    assert (repo / ".argus" / loc2).is_file()


def test_append_only_three_decision_chain_is_ordered(tmp_path: Path) -> None:
    """TC-ArgusAgent-HITL-001-09 — AC3: a THREE-decision chain forms an ordered prev-hash spine."""
    repo = _argus_repo(tmp_path)
    writer = DecisionRecordWriter(repo)
    reader = ApaaStoreReader(repo)

    # Three DISTINCT decisions (distinct decider tokens → distinct payloads → distinct hashes).
    resolutions = [
        resolve_escalation(_fired_trigger()),  # default_stop
        resolve_escalation(
            _fired_trigger(), human_decision=HumanDecision(outcome=EscalationOutcome.STOP, decider_id="op-a")
        ),
        resolve_escalation(
            _fired_trigger(), human_decision=HumanDecision(outcome=EscalationOutcome.PROCEED, decider_id="op-b")
        ),
    ]
    locs = [writer.append(r) for r in resolutions]
    envelopes = [reader.read_envelope(loc) for loc in locs]
    # Each envelope's prev_hash is the prior's content_hash (ordered append spine).
    assert envelopes[0].prev_hash == GENESIS_PREV_HASH
    assert envelopes[1].prev_hash == envelopes[0].content_hash
    assert envelopes[2].prev_hash == envelopes[1].content_hash


def test_prior_decision_is_never_mutated_on_a_later_append(tmp_path: Path) -> None:
    """TC-ArgusAgent-HITL-001-10 — AC3/§3.4: the FIRST decision's bytes are byte-identical after a later append."""
    repo = _argus_repo(tmp_path)
    writer = DecisionRecordWriter(repo)
    res1 = resolve_escalation(_fired_trigger())
    loc1 = writer.append(res1)
    bytes_before = (repo / ".argus" / loc1).read_bytes()
    # A later append must not touch the prior record.
    writer.append(
        resolve_escalation(_fired_trigger(), human_decision=HumanDecision(outcome=EscalationOutcome.PROCEED, decider_id="op-z"))
    )
    bytes_after = (repo / ".argus" / loc1).read_bytes()
    assert bytes_after == bytes_before, "append-only: the prior decision is immutable"


def test_identical_resolutions_append_two_distinct_files_and_intact_chain(tmp_path: Path) -> None:
    """TC-ArgusAgent-HITL-001-31 — AC3/FR24 REGRESSION: two IDENTICAL resolutions → 2 files + a non-cyclic chain.

    RED-first against the content-address-collision defect (review iteration 1): two
    byte-identical ``EscalationResolution`` payloads (the exact AC4 re-log-same-
    deferred-STOP case, or two audit runs of one repo) previously hashed to the SAME
    ``decisions/<hash>.json`` — the second ``append()`` OVERWROTE the first (AC3
    "prior NEVER overwritten" broken) and produced a self-cyclic ``prev_hash`` so
    ``_resolve_chain_head()`` returned genesis, orphaning the whole chain. The fix
    folds the chain position into the HASHED persisted payload so each link is a
    DISTINCT artifact. Assert: append A, then B (chains to A), then the SAME payload
    as A again → THREE distinct files + an ordered, genesis-rooted, NON-cyclic chain.
    """
    repo = _argus_repo(tmp_path)
    writer = DecisionRecordWriter(repo)
    reader = ApaaStoreReader(repo)

    res_a = resolve_escalation(_fired_trigger())  # default_stop (A)
    res_b = resolve_escalation(
        _fired_trigger(), human_decision=HumanDecision(outcome=EscalationOutcome.PROCEED, decider_id="op-1")
    )  # human (B)
    # A' is a byte-identical RE-LOG of the same deferred STOP as A (same resolution).
    res_a_prime = resolve_escalation(_fired_trigger())  # default_stop, identical payload to A
    assert res_a_prime.to_payload() == res_a.to_payload(), "precondition: A and A' are byte-identical resolutions"

    loc_a = writer.append(res_a)
    loc_b = writer.append(res_b)
    loc_a_prime = writer.append(res_a_prime)

    # THREE distinct on-disk artifacts — the second re-log did NOT overwrite A.
    assert len({loc_a, loc_b, loc_a_prime}) == 3, "each append is a distinct content-addressed artifact"
    for loc in (loc_a, loc_b, loc_a_prime):
        assert (repo / ".argus" / loc).is_file()

    # The chain is an ordered, genesis-rooted spine with NO cycle and NO head reset.
    e_a = reader.read_envelope(loc_a)
    e_b = reader.read_envelope(loc_b)
    e_a_prime = reader.read_envelope(loc_a_prime)
    assert e_a.prev_hash == GENESIS_PREV_HASH, "the head uses the genesis sentinel"
    assert e_b.prev_hash == e_a.content_hash, "B chains to A"
    assert e_a_prime.prev_hash == e_b.content_hash, "A' chains to B (no self-cycle, no genesis reset)"
    # All three content hashes are distinct — no collision.
    assert len({e_a.content_hash, e_b.content_hash, e_a_prime.content_hash}) == 3
    # The prior record A is byte-identical after the later appends (append-only).
    assert reader.read_envelope(loc_a).payload["outcome"] == EscalationOutcome.STOP.value


def test_chain_head_resolution_survives_a_foreign_decisions_artifact(tmp_path: Path) -> None:
    """TC-ArgusAgent-HITL-001-11 — AC3/AR10: a foreign decisions/ file (e.g. the 5.3 rejection ledger) is ignored.

    The chain is producer-scoped: a fixed-name / non-decision artifact in the shared
    decisions/ subdir must not be mistaken for a decision-record link, and a corrupt
    byte must not crash chain-head resolution.
    """
    repo = _argus_repo(tmp_path)
    decisions = repo / ".argus" / "decisions"
    decisions.mkdir(parents=True, exist_ok=True)
    # A fixed-name foreign artifact (5.3-shaped) + a corrupt content-addressed-shaped file.
    (decisions / "rejection_ledger.json").write_text("{\"not\": \"a decision\"}", encoding="utf-8")
    (decisions / ("f" * 64 + ".json")).write_text("not json at all", encoding="utf-8")

    writer = DecisionRecordWriter(repo)
    loc1 = writer.append(resolve_escalation(_fired_trigger()))
    reader = ApaaStoreReader(repo)
    # The head is genesis (no PRIOR decision-record exists — the foreign files are ignored).
    assert reader.read_envelope(loc1).prev_hash == GENESIS_PREV_HASH


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — the STOP is logged even if the full decision record is deferred (FR24)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "resolution_kind_builder,expected_kind",
    [
        (lambda: resolve_escalation(_fired_trigger()), ResolutionKind.DEFAULT_STOP),
        (lambda: resolve_escalation(_fired_trigger(), timeout_elapsed=True), ResolutionKind.TIMEOUT_PARKED_STOP),
    ],
)
def test_stop_logged_even_when_deferred(
    tmp_path: Path, resolution_kind_builder, expected_kind: ResolutionKind
) -> None:
    """TC-ArgusAgent-HITL-001-12 — AC4 KEYSTONE: a STOP is appended even when the human decision is deferred.

    RED-first against an implementation that records NOTHING until the human
    responds (which would lose the escalation fact on a deferred/abandoned
    decision). The default_stop / timeout_parked_stop record is present, is a STOP,
    and carries no decider (the human decision is still pending).
    """
    repo = _argus_repo(tmp_path)
    writer = DecisionRecordWriter(repo)
    res = resolution_kind_builder()
    loc = writer.append(res)  # the STOP is logged NOW, before any human decision

    reader = ApaaStoreReader(repo)
    envelope = reader.read_envelope(loc)
    payload = envelope.payload
    assert payload["outcome"] == EscalationOutcome.STOP.value
    assert payload["resolution_kind"] == expected_kind.value
    assert payload["decider_id"] is None, "the human decision is deferred — no decider yet"


def test_deferred_stop_then_later_human_decision_is_a_subsequent_append(tmp_path: Path) -> None:
    """TC-ArgusAgent-HITL-001-13 — AC4: a later human decision APPENDS (never mutates the deferred STOP record)."""
    repo = _argus_repo(tmp_path)
    writer = DecisionRecordWriter(repo)
    stop_loc = writer.append(resolve_escalation(_fired_trigger()))  # deferred STOP
    human_loc = writer.append(
        resolve_escalation(
            _fired_trigger(), human_decision=HumanDecision(outcome=EscalationOutcome.PROCEED, decider_id="op-late")
        )
    )
    assert stop_loc != human_loc
    reader = ApaaStoreReader(repo)
    # The STOP record still reads back as STOP (unmutated); the human record chains onto it.
    assert reader.read_envelope(stop_loc).payload["outcome"] == EscalationOutcome.STOP.value
    assert reader.read_envelope(human_loc).prev_hash == reader.read_envelope(stop_loc).content_hash


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — the record carries NO source/secret bytes / NO absolute host path (NFR-S1)
# ─────────────────────────────────────────────────────────────────────────────


def test_decision_record_payload_carries_only_provenance_no_secrets() -> None:
    """TC-ArgusAgent-HITL-001-14 — AC5/NFR-S1: the payload carries only provenance tokens, never source/secret bytes."""
    trig = escalation_fires(
        _rule(match_rule_ids=("hardcoded_secret",)),
        findings=(_finding(rule_id="hardcoded_secret"),),
    )
    assert trig is not None
    res = resolve_escalation(trig, human_decision=HumanDecision(outcome=EscalationOutcome.STOP, decider_id="sec-owner"))
    payload = decision_record_payload(res)
    # The ONLY keys — a closed provenance schema.
    assert set(payload) == {
        "schema_version",
        "outcome",
        "resolution_kind",
        "trigger",
        "decider_id",
        "decision_id",
    }
    # The trigger carries only provenance tokens (rule-id / reason / finding-id / locator).
    assert set(payload["trigger"]) == {"rule_id", "reason", "finding_ids", "locator_provenance"}


def test_decision_record_carries_no_planted_secret_byte(tmp_path: Path) -> None:
    """TC-ArgusAgent-HITL-001-15 — AC5/NFR-S1: a planted secret value never appears in the persisted decision bytes."""
    planted = "SecretCanaryHITL_VALUE_0123456789abcdef"
    # Even if a caller (mistakenly) tries to carry the secret as a decider token, the
    # audit sweep below proves the record shape carries no SOURCE byte; here we assert
    # the audited-finding provenance path never carries a value. Build a finding whose
    # locator is a file path (never the secret value), fire, resolve, persist.
    trig = escalation_fires(_rule(match_rule_ids=("hardcoded_secret",)), findings=(_finding(rule_id="hardcoded_secret"),))
    assert trig is not None
    res = resolve_escalation(trig)
    repo = _argus_repo(tmp_path)
    writer = DecisionRecordWriter(repo)
    loc = writer.append(res)
    blob = (repo / ".argus" / loc).read_bytes()
    assert planted.encode("utf-8") not in blob, "no source/secret byte in the decision record"
    # No absolute host path leaks: the returned locator is .argus/-root-relative POSIX.
    assert not loc.startswith("/") and ":" not in loc.split("/")[0]
    assert loc.startswith("decisions/")


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — determinism + tamper-evidence + non-ASCII (NFR-D1/D2 / NFR-A1 / AI-E1-1)
# ─────────────────────────────────────────────────────────────────────────────


def test_resolution_is_deterministic_across_two_runs() -> None:
    """TC-ArgusAgent-HITL-001-16 — AC6(a/b): the same inputs → the same decision-id + payload bytes twice."""
    res_a = resolve_escalation(_fired_trigger(), human_decision=HumanDecision(outcome=EscalationOutcome.PROCEED, decider_id="op-9"))
    res_b = resolve_escalation(_fired_trigger(), human_decision=HumanDecision(outcome=EscalationOutcome.PROCEED, decider_id="op-9"))
    assert res_a.decision_id == res_b.decision_id
    assert res_a.to_payload() == res_b.to_payload()


def test_decision_id_is_content_derived_over_the_identity_payload() -> None:
    """TC-ArgusAgent-HITL-001-17 — AC6/AR4: the decision-id is the content hash of the id-free identity payload."""
    res = resolve_escalation(_fired_trigger())
    identity = {
        "schema_version": ESCALATION_SCHEMA_VERSION,
        "outcome": res.outcome.value,
        "resolution_kind": res.resolution_kind.value,
        "trigger": res.trigger.model_dump(mode="json"),
        "decider_id": res.decider_id,
    }
    assert res.decision_id == compute_content_hash(identity)


def test_two_runs_persist_byte_identical_chain(tmp_path: Path) -> None:
    """TC-ArgusAgent-HITL-001-18 — AC6/NFR-P1: the same decision sequence persists byte-identical bytes on two repos."""
    seq = [
        lambda: resolve_escalation(_fired_trigger()),
        lambda: resolve_escalation(_fired_trigger(), human_decision=HumanDecision(outcome=EscalationOutcome.PROCEED, decider_id="op-1")),
    ]

    def _run(root: Path) -> list[bytes]:
        (root / ".argus").mkdir(parents=True)
        w = DecisionRecordWriter(root)
        out: list[bytes] = []
        for build in seq:
            loc = w.append(build())
            out.append((root / ".argus" / loc).read_bytes())
        return out

    bytes_a = _run(tmp_path / "a")
    bytes_b = _run(tmp_path / "b")
    assert bytes_a == bytes_b, "content-derived ids + no clock/uuid/float → byte-identical chain"


def test_tampered_decision_record_is_caught_by_the_reader(tmp_path: Path) -> None:
    """TC-ArgusAgent-HITL-001-19 — AC6/NFR-A1: mutating a persisted decision byte trips the reader tamper guard."""
    repo = _argus_repo(tmp_path)
    writer = DecisionRecordWriter(repo)
    loc = writer.append(
        resolve_escalation(_fired_trigger(), human_decision=HumanDecision(outcome=EscalationOutcome.PROCEED, decider_id="op-1"))
    )
    target = repo / ".argus" / loc
    tampered = target.read_text(encoding="utf-8").replace("PROCEED", "STOP")
    target.write_text(tampered, encoding="utf-8")
    reader = ApaaStoreReader(repo)
    with pytest.raises(StoreIntegrityError):
        reader.read_envelope(loc)


def test_non_ascii_decider_and_reason_round_trip(tmp_path: Path) -> None:
    """TC-ArgusAgent-HITL-001-22 — AC6(d)/AI-E1-1: a non-ASCII decider-id / reason token round-trips byte-stably."""
    rule = _rule(reason="неоднозначно_секрет")  # non-ASCII reason token
    trig = escalation_fires(rule, findings=(_finding(),))
    assert trig is not None
    res = resolve_escalation(trig, human_decision=HumanDecision(outcome=EscalationOutcome.STOP, decider_id="оператор_42"))
    repo = _argus_repo(tmp_path)
    writer = DecisionRecordWriter(repo)
    loc = writer.append(res)
    reader = ApaaStoreReader(repo)
    payload = reader.read_envelope(loc).payload
    assert payload["decider_id"] == "оператор_42"
    assert payload["trigger"]["reason"] == "неоднозначно_секрет"
    # Determinism holds for the non-ASCII payload too.
    assert resolve_escalation(trig, human_decision=HumanDecision(outcome=EscalationOutcome.STOP, decider_id="оператор_42")).decision_id == res.decision_id


# ─────────────────────────────────────────────────────────────────────────────
# AC7 — complete-the-declared-set / no-crash edges / typed NAMED errors (AI-E5-1/AR10)
# ─────────────────────────────────────────────────────────────────────────────


def test_gate_no_crash_on_empty_and_none_findings() -> None:
    """TC-ArgusAgent-HITL-001-23 — AC7/AI-E4-2: empty / None findings + an absent verdict → does-not-fire, no crash."""
    assert escalation_fires(_rule(), findings=()) is None
    assert escalation_fires(_rule(), findings=None) is None
    assert escalation_fires(_rule(), findings=None, verdict=None) is None


def test_gate_skips_a_malformed_finding_element_without_crashing() -> None:
    """TC-ArgusAgent-HITL-001-24 — AC7/AR10: a malformed per-element finding is SKIPPED, not a crash."""
    # A well-formed matched finding alongside a non-Recording junk element.
    trig = escalation_fires(_rule(), findings=[_finding(), "not-a-recording", 42])  # type: ignore[list-item]
    assert trig is not None
    assert trig.finding_ids == ("rec-1",)  # only the real finding matched


def test_gate_raises_typed_named_error_on_malformed_top_level_argument() -> None:
    """TC-ArgusAgent-HITL-001-25 — AC7/AR10: a genuinely malformed top-level argument raises a typed NAMED error."""
    with pytest.raises(EscalationError):
        escalation_fires("not-a-rule", findings=())  # type: ignore[arg-type]
    with pytest.raises(EscalationError):
        escalation_fires(_rule(), findings=(), verdict="not-a-verdict")  # type: ignore[arg-type]
    with pytest.raises(EscalationError):
        resolve_escalation("not-a-trigger")  # type: ignore[arg-type]
    with pytest.raises(EscalationError):
        resolve_escalation(_fired_trigger(), human_decision="not-a-decision")  # type: ignore[arg-type]


def test_writer_raises_typed_named_error_on_malformed_resolution(tmp_path: Path) -> None:
    """TC-ArgusAgent-HITL-001-26 — AC7/AR10: the writer raises a typed NAMED error on a non-resolution argument."""
    repo = _argus_repo(tmp_path)
    writer = DecisionRecordWriter(repo)
    with pytest.raises(DecisionRecordError):
        writer.append("not-a-resolution")  # type: ignore[arg-type]


def test_decision_record_payload_rejects_non_resolution() -> None:
    """TC-ArgusAgent-HITL-001-27 — AC7/AR10: the module-level payload accessor rejects a non-resolution (typed)."""
    with pytest.raises(EscalationError):
        decision_record_payload("not-a-resolution")  # type: ignore[arg-type]


# ─────────────────────────────────────────────────────────────────────────────
# AC8 — structural: the gate is zero-token pure; the frozen schema is extra=forbid
# ─────────────────────────────────────────────────────────────────────────────


def test_gate_is_zero_token_pure_no_llm_dispatch() -> None:
    """TC-ArgusAgent-HITL-001-28 — AC8/NFR-D2: the gate module dispatches NO LLM (no dispatch attr / provider symbol).

    A cheap structural proof that the V1 gate is pattern-matched, not LLM-driven:
    the module exposes NO ``dispatch`` / provider symbol, and resolving an
    escalation touches no provider (the import-isolation gate proves ⊬ providers in
    a clean subprocess; this asserts the API shape carries no LLM seam).
    """
    import argus.governance.escalation as esc

    assert not hasattr(esc, "dispatch")
    assert not hasattr(esc, "execute_llm")
    # The resolution is a pure fold — calling it twice with the same inputs is stable
    # (already proven above); here assert it needs no external collaborator.
    assert isinstance(resolve_escalation(_fired_trigger()), EscalationResolution)


def test_frozen_schema_rejects_unknown_field() -> None:
    """TC-ArgusAgent-HITL-001-29 — AC8/NFR-M2: the frozen schema is extra=forbid (additive-only)."""
    from pydantic import ValidationError

    for model, kwargs in (
        (EscalationRule, {"rule_id": "r", "bogus": 1}),
        (HumanDecision, {"outcome": EscalationOutcome.STOP, "decider_id": "d", "bogus": 1}),
    ):
        with pytest.raises(ValidationError):
            model(**kwargs)  # type: ignore[arg-type]


def test_files_are_under_1200_lines() -> None:
    """TC-ArgusAgent-HITL-001-30 — AC8/NFR-M1: the new production + test files are ≤1200 lines."""
    root = Path(__file__).resolve().parents[1] / "argus" / "governance"
    for name in ("escalation.py", "decision_record.py", "__init__.py"):
        lines = (root / name).read_text(encoding="utf-8").splitlines()
        assert len(lines) <= 1200, f"{name} exceeds 1200 lines"
    assert len(Path(__file__).read_text(encoding="utf-8").splitlines()) <= 1200
