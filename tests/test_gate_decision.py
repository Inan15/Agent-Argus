"""Story 13.3 / AC1–AC5 — the gate decision, and the guards that keep it a measurement.

``TC-ArgusAgent-PRECISION-001-53``..``-58``, ``-69``, ``-70``. A **NEW** module, for the
reason AC8.5 states and this story re-measured on its own baseline:
``tests/test_evidence_citation.py`` is at **1199/1200** lines,
``tests/test_built_distribution.py`` at **1198/1200** and
``tests/test_instrument_disclosure.py`` at **1194/1200**. Three files are effectively full,
the sanctioned remedy is a cohesion split (12.8), and *"do not shave a file to fit"* is the
rule this module exists to obey rather than to test.

⛔ **SPLIT 2026-08-20 (Story 16.3 / Task 1), and the rule it exists to obey was applied to
itself.** This module reached **1,191 of 1,200** with **no ledger entry at all** — 16.2's
contexted story flagged it at 1,193 and said it *"gets the same rule"*, then split the
production module (``DF-16-1-B``) and left this one unfiled. §5's SEVENTH condition forces an
edit to ``-55``, because ``expected_section_5_outcome`` takes its dispatch terms as REQUIRED
keyword arguments with no default — deliberately, so no caller silently inherits the old
answer — and that edit does not fit in nine lines. The remedy is the sanctioned one, taken
FIRST and in its own commit (the ``95819bc`` precedent): the six guards over the **ARTIFACT
the decision publishes** (``-59``..``-64``: the concentration disclosure, the completion
bound, locators-and-counts, the disclosure's persistence, no-threshold-moved, the
``UNEVALUABLE`` sentence) moved **byte-for-byte** to
``tests/test_gate_decision_artifact.py``. What stayed is the guards over the **decision
FUNCTION itself**. The boundary is the test-side mirror of the split 16.2 already made in
production — ``gate_conditions.py`` (what a condition IS) against ``gate_evidence.py`` (what
one is MEASURED FROM) — and it was confirmed by an AST walk before a line moved. The shared
fixtures below did **not** move and are IMPORTED by the new module, never copied (AR7).

**What every guard here is ultimately protecting.** Epic 13 exists to answer one question
honestly: has Argus's own finding precision been measured, and did it clear ≥80%? There
are exactly two ways to get that wrong, and both are cheap:

1. **Fold an incompletely adjudicated record and write down "the gate did not cleared".**
   True, useless, and INDISTINGUISHABLE DOWNSTREAM from an honest measured shortfall. The
   ``BLOCKED`` member of the outcome vocabulary exists to make that sentence
   unexpressible, and ``-55`` / ``-58`` are what make the vocabulary real.
2. **Publish a figure that overstates the breadth of what was measured.** ``-59`` closes
   AC3b in both directions: the disclosure must go RED when it is absent, and it must NOT
   manufacture a concentration claim over a well-distributed population. That guard now
   lives in ``tests/test_gate_decision_artifact.py``; the claim it protects is unchanged.

**GUARD-ADEQUACY (``AI-E11-1``, architecture §Enforcement) is discharged per guard**: each
names its **observable**, each moves the defect **at the real seam** (the shipped types and
the committed artifacts, never a copy), and ``-58`` **GENERATES** its adversarial
variants *from the committed record itself* with their counts, rather than hand-listing
them. Its input-side twin is honoured too — ``-54`` asserts what the artifact IS (a tracked
file with a live re-derivation), not merely what shape it has.

**Non-vacuity is not optional**: every guard that walks the record or the decision asserts
it extracted **> 0** items before asserting anything about them.

**Platform neutrality** (the local gates here are Windows-only while CI runs an ubuntu
matrix): ``pathlib`` throughout, explicit ``encoding="utf-8"``, ``.as_posix()`` at every
path→string boundary, and not one assertion on ``os.sep``, a drive letter or a
CRLF-sensitive byte count.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from argus.precision.adjudication import (
    AdjudicationRecord,
    AdjudicationRow,
    AdjudicationUnevaluable,
    Exhaustive,
    finding_row_id,
    fold_adjudicated_precision,
    load_record,
    validation_set_population_n,
)
from argus.precision.gate_breadth import assess_breadth
from argus.precision.gate_seal import sealed_member_floor
from argus.precision.gate_yield import verdict_eligible_population_floor
from argus.precision.gate_decision import (
    BREADTH_CONDITION_ID,
    CONDITION_VERDICTS,
    GATE_OUTCOMES,
    SECTION_5_CONDITIONS,
    CleanRepoEvidence,
    ConditionResult,
    CorpusReadProof,
    GateDecision,
    UnregisteredConditionVerdict,
    UnregisteredGateOutcome,
    VacuousDecisionError,
    condition_verdict_meaning,
    decide_gate,
    gate_outcome_meaning,
    section_5_condition,
)
from argus.precision.gate_disclosure import (
    VacuousDisclosureError,
    derive_concentration,
    ratified_corpus_members,
)
from argus.precision.replay_harness import (
    PRECISION_GATE_THRESHOLD,
    ratio_string,
    registry_module,
)
from argus.store.canonical import loads

# §5's dispatch MIRROR is IMPORTED, never copied (12.6 / DN-7 — a second copy is a second
# thing to keep true), and is driven to its breadth branch, in both directions, by -86 in
# the module it lives in.
from tests.test_gate_breadth import expected_section_5_outcome

# ⛔ MOVED 2026-08-20 (Story 16.2 / AC6.3), not deleted. `_spread` lived HERE and spread over
# `ratified_corpus_members()`; all five of those became `pre-seal` when the seal landed, so a
# population over them can never reach a §5 OUTCOME again. It now spreads over the SEALED
# bench rows and lives in the module that owns the partition, IMPORTED rather than copied
# (AR7) exactly as the §5 dispatch mirror above is.
from tests.test_gate_seal import sealed_corpus_members, spread_over_sealed as _spread

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_CORPUS_DIR = _ARTIFACTS / "validation-corpus"
_RECORD_PATH = _CORPUS_DIR / "adjudication-record.json"
_DECISION_PATH = _CORPUS_DIR / "gate-decision-record.json"
_PROTOCOL_PATH = _ARTIFACTS / "precision-validation-protocol.md"

#: The named human protocol §2 designates. Synthetic fixtures below attribute their
#: SYNTHETIC judgements to this string so the instrument's attribution rule is exercised;
#: not one of them is ever written to the committed record.
_ADJUDICATOR = "XAgent007 (Engineering Lead)"


def _record() -> AdjudicationRecord:
    assert _RECORD_PATH.is_file(), (
        f"the committed adjudication record is absent at "
        f"{_RECORD_PATH.relative_to(_REPO_ROOT).as_posix()}"
    )
    return load_record(_RECORD_PATH)


def _decision_payload() -> dict:
    assert _DECISION_PATH.is_file(), (
        f"the committed gate-decision record is absent at "
        f"{_DECISION_PATH.relative_to(_REPO_ROOT).as_posix()}. Run: python "
        f"scripts/build_gate_decision.py"
    )
    return loads(_DECISION_PATH.read_text(encoding="utf-8"))


def _judged(
    row: AdjudicationRow, disposition: str, *, revision: int = 9
) -> AdjudicationRow:
    """A SYNTHETIC superseding judgement over *row*'s finding — exercises the instrument only.

    ``revision=9`` keeps every synthetic row id distinct from the committed ones, and
    ``supersedes`` names the row it replaces, so the record's append-only invariant is
    honoured rather than side-stepped. Every row this helper produces lives inside one
    test's local fixture and is never written to any committed artifact.
    """
    return AdjudicationRow(
        row_id=finding_row_id(
            member_id=row.member_id,
            rule_id=row.rule_id,
            verdict_eligible=row.verdict_eligible,
            advisory=row.advisory,
            locator=row.locator,
            revision=revision,
        ),
        member_id=row.member_id,
        rule_id=row.rule_id,
        verdict_eligible=row.verdict_eligible,
        advisory=row.advisory,
        locator=row.locator,
        disposition=disposition,
        adjudicator=_ADJUDICATOR,
        adjudicated_on="2026-08-17",
        reason="synthetic fixture: exercises the instrument, adjudicates nothing real",
        supersedes=row.row_id,
    )


def _clean_evidence(*, clean_repo_fp: int = 0) -> CleanRepoEvidence:
    """Cartridge-corpus clean-repo evidence, shaped exactly as the producer supplies it."""
    return CleanRepoEvidence(
        corpus="synthetic fixture standing in for the FR20 cartridge corpus",
        applicable=True,
        clean_repo_fp=clean_repo_fp,
        clean_member_ids=("clean_control",),
        note="synthetic fixture",
    )


def _read_proof(**overrides: object) -> CorpusReadProof:
    """A POSITIVE corpus-read proof, shaped exactly as the producer supplies it (13.5).

    The defaults are the ORDER OF MAGNITUDE of the real 2026-08-18 run, so a fixture that
    accidentally proves something about an empty corpus is visible as a fixture. Every
    conjunct is overridable by keyword, which is how ``-69`` GENERATES its adversarial
    variants rather than hand-writing them.
    """
    fields: dict[str, object] = {
        "statement": "synthetic fixture standing in for a measured corpus-read proof",
        "members_audited": 5,
        "source_file_count": 1960,
        "scored_population_count": 5129,
        "flagged_file_count": 1249,
        "advisory_finding_count": 4284,
        "blocking_finding_count": 0,
        "every_member_pin_verified": True,
        "every_member_byte_reproducible": True,
    }
    fields.update(overrides)
    return CorpusReadProof(**fields)  # type: ignore[arg-type]


def _decide(
    record: AdjudicationRecord,
    *,
    expected: list[str] | None = None,
    clean_repo_fp: int = 0,
    corpus_read_proof: CorpusReadProof | None = None,
    corpus: tuple[dict[str, str], ...] | None = None,
) -> GateDecision:
    """Drive :func:`decide_gate` at the REAL seam with the live derived corpus figures.

    *corpus* defaults to the five RATIFIED members — every caller's shape before
    2026-08-20 — and is passed explicitly by the guards that generate over SEALED rows, so
    the concentration and the partitions describe the SAME population. Passing a row here
    ratifies nothing: ``ratified_members`` is an argument, and protocol §6 R2 is an
    operator act.
    """
    return decide_gate(
        record,
        corpus_read_proof=corpus_read_proof,
        expected_finding_ids=(
            [row.finding_id for row in record.rows] if expected is None else expected
        ),
        population_n=validation_set_population_n(),
        floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
        protocol_change_log_head=record.protocol_version,
        clean_repo_evidence=_clean_evidence(clean_repo_fp=clean_repo_fp),
        ratified_members=ratified_corpus_members() if corpus is None else corpus,
        record_is_tracked_in_git=True,
        commit_sha="0" * 40,
        decided_on="2026-08-17",
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — THREE terminal states, never two, in a vocabulary that RAISES
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_53_the_outcome_vocabulary_is_closed_and_raises() -> None:
    """TC-ArgusAgent-PRECISION-001-53 — AC1: three outcomes, exhaustive dispatch, RAISES.

    **Observable:** :func:`gate_outcome_meaning` and :func:`condition_verdict_meaning`.
    Checked in BOTH directions — an unregistered member raises, and every registered
    member is exercised, because a vocabulary entry nobody constructs is an entry nobody
    guards. ``BLOCKED`` is asserted present BY NAME and asserted to be a distinct claim
    from ``NOT_CLEARED``: collapsing them is the one failure this whole epic exists to
    prevent, and a two-member vocabulary would make it the only expressible answer.
    """
    assert set(GATE_OUTCOMES) == {"CLEARED", "NOT_CLEARED", "BLOCKED"}, (
        "the outcome vocabulary must hold exactly three members. A fourth terminal state "
        "is a protocol decision; a missing third is the DF-10-4-E defect."
    )
    for outcome in GATE_OUTCOMES:
        assert gate_outcome_meaning(outcome).strip(), outcome
    for unregistered in ("cleared", "PASSED", "UNKNOWN", "", "not_cleared"):
        with pytest.raises(UnregisteredGateOutcome):
            gate_outcome_meaning(unregistered)

    # BLOCKED and NOT_CLEARED are DIFFERENT CLAIMS, and the vocabulary says so in its own
    # text rather than leaving it to a reader's charity.
    blocked = gate_outcome_meaning("BLOCKED")
    assert "NOT a §5 outcome" in blocked
    assert "the gate did not clear" in blocked and "NEVER" in blocked, (
        "BLOCKED's registered meaning must forbid its own restatement as 'the gate did "
        "not clear' — that sentence is true, useless and indistinguishable downstream "
        "from an honest measured shortfall"
    )
    assert "RESULT" in gate_outcome_meaning("NOT_CLEARED")

    assert set(CONDITION_VERDICTS) == {"MET", "FAILED", "NOT_APPLICABLE", "UNEVALUABLE"}
    for verdict in CONDITION_VERDICTS:
        assert condition_verdict_meaning(verdict).strip(), verdict
    with pytest.raises(UnregisteredConditionVerdict):
        condition_verdict_meaning("SATISFIED")
    # NOT_APPLICABLE is not a synonym for MET, and the vocabulary must say so — protocol
    # §5 as amended forbids counting the clean-repo condition met by default.
    assert "never" in condition_verdict_meaning("NOT_APPLICABLE").lower()


def test_TC_ArgusAgent_PRECISION_001_54_the_decision_is_committed_derived_and_re_derivable() -> None:
    """TC-ArgusAgent-PRECISION-001-54 — AC3: the decision is IN GIT and it re-derives live.

    **Observable:** ``git ls-files`` over the artifact path, and the artifact's payload
    compared field-by-field against a decision computed from the live record and the live
    manifest. **Why ``git ls-files`` and not a path check:** a path assertion passes for an
    ignored file, ``.gitignore`` ignores ``.argus/``, and gate evidence that is not in git
    is not evidence (``TC-ArgusAgent-PRECISION-001-40``'s precedent, reused not re-invented).

    **The input-side twin of the guard-adequacy clause, honoured:** this asserts what the
    artifact IS — a tracked file whose measured fields still equal a live re-derivation —
    not merely that it has the right shape.
    """
    relative = _DECISION_PATH.relative_to(_REPO_ROOT).as_posix()
    assert not relative.startswith(".argus/"), relative
    tracked = subprocess.run(
        ["git", "ls-files", "--", relative],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.split()
    assert tracked, (
        f"{relative} is NOT tracked by git. The gate decision is the evidence the "
        f"externalization gate rests on; evidence outside git is not evidence (13.2 / DN-3)."
    )

    payload = _decision_payload()
    assert payload["schema_version"] and payload["story"].startswith("13-3"), payload["story"]
    assert len(payload["section_5_conditions"]) == len(SECTION_5_CONDITIONS) > 0
    assert payload["corpus"]["members"], "non-vacuity: the decision names ZERO corpus members"
    assert payload["concentration"]["adjudicated_population"] > 0, (
        "non-vacuity: the decision was folded over an EMPTY population"
    )

    live = _decide(_record())
    assert payload["outcome"] == live.outcome, (
        f"the committed decision says {payload['outcome']!r} and the live re-derivation "
        f"says {live.outcome!r}. Re-run: python scripts/build_gate_decision.py"
    )
    assert payload["precision"]["total_tp"] == live.fold.total_tp
    assert payload["precision"]["total_fp"] == live.fold.total_fp
    assert payload["precision"]["precision_ratio"] == live.fold.precision_ratio
    assert payload["corpus"]["n"] == live.fold.n == validation_set_population_n()
    assert [c["verdict"] for c in payload["section_5_conditions"]] == [
        c.verdict for c in live.conditions
    ]
    # PROVENANCE, not measurement: the sha and the date are carried, never re-derived —
    # re-deriving them would make the artifact stale on the next commit and a check that
    # is red for a reason nobody can fix is a check people learn to ignore.
    assert re.fullmatch(r"[0-9a-f]{40}|NO_VCS", payload["commit_sha"]), payload["commit_sha"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", payload["decided_on"]), payload["decided_on"]


def test_TC_ArgusAgent_PRECISION_001_55_the_live_outcome_is_derived_not_chosen() -> None:
    """TC-ArgusAgent-PRECISION-001-55 — AC1/AC5: the outcome equals what the preconditions dictate.

    **Observable:** the committed outcome, versus §5's three-way dispatch recomputed from
    the fold's own preconditions by the shared :func:`expected_section_5_outcome` mirror.
    This is the guard that would catch a story writing down the answer it preferred: the
    expected outcome is DERIVED from ``determinism`` / ``exhaustiveness`` / ``precision`` /
    breadth rather than pinned as a literal, so it stays correct when the adjudication moves
    and it fails the moment the recorded outcome and the measured state disagree.

    ⛔ **WHICH CLAUSE THIS FIXTURE REACHES, stated plainly** (2026-08-20 code review). The
    COMMITTED record carries 5 ``BORDERLINE`` rows, is therefore never :class:`Exhaustive`,
    and the mirror's FIRST clause always fires here. The breadth clause is **not** exercised
    by this fixture and is not claimed to be: round 2 claimed it and the review disproved it
    by execution (``holds = True``, and separately both breadth branches disabled, left this
    guard GREEN). The term is passed in so this guard cannot expect ``CLEARED`` over a narrow
    denominator should the record ever become exhaustive; the clause itself is DRIVEN both
    ways by ``tests/test_gate_breadth.py::TC-ArgusAgent-PRECISION-001-86``.
    """
    record = _record()
    assert len(record.rows) > 0, "non-vacuity: the adjudication record is EMPTY"
    ratified = [str(member["member_id"]) for member in ratified_corpus_members()]
    assert ratified, "non-vacuity: the manifest reports ZERO ratified members"
    fold = fold_adjudicated_precision(
        record,
        expected_finding_ids=[row.finding_id for row in record.rows],
        population_n=validation_set_population_n(),
        floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
    )
    # RE-AUTHORED 2026-08-20 (Story 16.1 / AC1.5), and REPAIRED the same day after the code
    # review proved the re-authoring had not been driven. The dispatch mirror is now written
    # ONCE, in tests/test_gate_breadth.py, and its breadth clause is driven in both
    # directions by -86 over GENERATED populations. Here the breadth term is DERIVED from the
    # same concentration the decision publishes — never recounted — and over THIS fixture the
    # mirror's first clause fires, because the committed record is not exhaustive. That is
    # recorded in the docstring rather than papered over.
    breadth = assess_breadth(
        derive_concentration(record, ratified_member_ids=ratified),
        validation_set_floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
        population_source=_RECORD_PATH.name,
    )
    assert not isinstance(fold.exhaustiveness, Exhaustive), (
        "the committed record became EXHAUSTIVE. This guard's fixture now reaches clauses it "
        "did not before: re-read its docstring, and check -86 still covers the breadth clause."
    )
    # The SEAL term, added 2026-08-20 (Story 16.2 / AC6.2), derived HERE from the committed
    # corpus and never read out of `assess_seal`. As with breadth, THIS FIXTURE DOES NOT
    # REACH THAT CLAUSE — the record is not exhaustive, so the mirror's first clause fires;
    # the term is passed in so this guard cannot expect CLEARED should that change, and the
    # clause is DRIVEN both ways by tests/test_gate_seal.py::-90.
    sealed_contributing = {
        str(member["member_id"])
        for member in ratified_corpus_members()
        if member["partition"] == "sealed"
    } & {row.member_id for row in record.live_rows()}
    # The YIELD term, added 2026-08-20 (Story 16.3 / AC4.4) on exactly the same terms as the
    # seal term above it: a THIRD REQUIRED keyword argument with no default, so this caller
    # had to state what it believes rather than inherit the old answer. It is COUNTED HERE
    # from the record's own live rows — the same quantity `derive_concentration` publishes as
    # `adjudicated_population` — and is never read back out of `assess_yield`; a mirror fed
    # the predicate's own answer moves in lockstep with the defect and survives exactly the
    # mutation that should kill it. As with the two terms above, THIS FIXTURE DOES NOT REACH
    # THAT CLAUSE: the record is not exhaustive, so the mirror's first clause fires. The
    # clause is DRIVEN both ways, with breadth and the seal pinned TRUE, by
    # tests/test_gate_yield.py::TC-ArgusAgent-PRECISION-001-97.
    live_population = len(record.live_rows())
    assert live_population > 0, (
        "non-vacuity: the committed record carries ZERO live rows, so the yield term below "
        "would be about an empty population and the mirror would be answering a different "
        "question than the decision"
    )
    expected = expected_section_5_outcome(
        fold,
        breadth_holds=breadth.holds,
        seal_holds=len(sealed_contributing) >= sealed_member_floor(fold.floor_n),
        yield_holds=live_population
        >= verdict_eligible_population_floor(PRECISION_GATE_THRESHOLD),
    )

    payload = _decision_payload()
    assert payload["outcome"] == expected, (
        f"the committed decision records {payload['outcome']!r} while the measured state "
        f"dictates {expected!r}. determinism={fold.determinism}; "
        f"exhaustiveness={fold.exhaustiveness}; precision={fold.precision_ratio}"
    )

    if expected == "BLOCKED":
        # A BLOCKED outcome must carry its residual AND its closure path. An unqualified
        # "blocked" is barely better than a skip, and it is the shape that reads
        # downstream as a shortfall.
        assert payload["closure_path"], "a BLOCKED decision recorded no closure path"
        # AMENDED 2026-08-18 (Story 13.5 / AC5). There is now a THIRD way to be BLOCKED and
        # it carries different evidence: the emitted blocking population is EMPTY while the
        # record still holds historical dispositions, so there is no residual to publish and
        # the denominator is not zero either. That leg is admitted only against a POSITIVE
        # corpus-read proof — strictly MORE evidence than the two legs above it, not less.
        # Without one, an empty population is still the unread-corpus case and decide_gate
        # raises before reaching here.
        proof = payload.get("corpus_read_proof")
        measured_empty_population = bool(
            proof
            and proof["proves_corpus_was_read"]
            and proof["blocking_finding_count"] == 0
            and proof["source_file_count"] > 0
            and proof["scored_population_count"] > 0
        )
        assert (
            payload["residual_completion_bound"]["residual_count"] > 0
            or (payload["precision"]["total_tp"] + payload["precision"]["total_fp"] == 0)
            or measured_empty_population
        ), (
            "a BLOCKED decision published neither a residual, nor an empty denominator, nor "
            "a positive corpus-read proof. One of the three is what makes BLOCKED a "
            "statement rather than a shrug."
        )
        # THE SENTENCE THAT MUST NOT APPEAR, in any casing, anywhere on the artifact —
        # except inside the vocabulary entry that forbids it.
        text = _DECISION_PATH.read_text(encoding="utf-8")
        forbidden = [
            match.start()
            for match in re.finditer(
                r"the gate (did not clear|was not cleared)", text, re.IGNORECASE
            )
        ]
        allowed = text.index(GATE_OUTCOMES["BLOCKED"][:60])
        for position in forbidden:
            assert allowed <= position < allowed + len(GATE_OUTCOMES["BLOCKED"]), (
                "a BLOCKED decision restates itself as 'the gate did not clear' outside "
                "the vocabulary entry that forbids exactly that. A shortfall and an "
                "absent measurement are different claims (AC1)."
            )


def test_TC_ArgusAgent_PRECISION_001_56_all_four_section_5_conditions_are_reported_individually() -> None:
    """TC-ArgusAgent-PRECISION-001-56 — AC2/DN-3: four conditions, four verdicts, no conjunction.

    **Observable:** the committed ``section_5_conditions`` list and
    :class:`GateDecision.__post_init__`. **Moved at the real seam:** a decision built with
    a condition dropped, renamed, or re-ordered RAISES, and a ``CLEARED`` decision carrying
    a condition that is anything but ``MET`` RAISES — which is protocol §5's *"it may not
    count it as met by default"* made unexpressible rather than written down.
    """
    payload = _decision_payload()
    reported = [c["condition_id"] for c in payload["section_5_conditions"]]
    assert reported == list(SECTION_5_CONDITIONS), reported
    for condition in payload["section_5_conditions"]:
        assert condition["verdict"] in CONDITION_VERDICTS, condition
        assert condition["measured"].strip(), condition["condition_id"]
        assert condition["what_would_close_it"].strip(), condition["condition_id"]
        assert condition["corpus"].strip(), condition["condition_id"]

    # §5's clean-repo condition NAMES the corpus it was measured over (protocol §5 as
    # amended 2026-08-16 binds this story by name) and is never met by default.
    clean = next(
        c
        for c in payload["section_5_conditions"]
        if c["condition_id"] == "clean-repo-blocking-false-positives-zero"
    )
    assert clean["verdict"] in ("MET", "FAILED", "NOT_APPLICABLE")
    if clean["verdict"] == "MET":
        assert payload["clean_repo_evidence"]["applicable"] is True
        assert payload["clean_repo_evidence"]["clean_member_ids"], (
            "a MET clean-repo condition folded ZERO clean members — a false-positive "
            "ceiling over an empty clean population passes forever"
        )
        assert payload["clean_repo_evidence"]["clean_repo_fp"] == 0

    live = _decide(_record())
    for dropped in range(len(SECTION_5_CONDITIONS)):
        with pytest.raises(ValueError, match="must report ALL"):
            replace(
                live,
                conditions=tuple(
                    c for i, c in enumerate(live.conditions) if i != dropped
                ),
            )
    with pytest.raises(ValueError, match="must report ALL"):
        replace(live, conditions=tuple(reversed(live.conditions)))

    # A CLEARED decision may not carry a NOT_APPLICABLE or UNEVALUABLE condition.
    not_met = tuple(c for c in live.conditions if c.verdict != "MET")
    assert not_met, (
        "non-vacuity: this branch needs >=1 non-MET condition to prove CLEARED refuses it"
    )
    with pytest.raises(ValueError, match="CLEARED requires all"):
        replace(live, outcome="CLEARED")
    with pytest.raises(UnregisteredConditionVerdict):
        ConditionResult(
            condition_id=SECTION_5_CONDITIONS[0],
            requirement="synthetic",
            corpus="synthetic",
            measured="synthetic",
            verdict="PROBABLY",
            what_would_close_it="synthetic",
        )
    with pytest.raises(ValueError, match="no 'what would close it'"):
        ConditionResult(
            condition_id=SECTION_5_CONDITIONS[0],
            requirement="synthetic",
            corpus="synthetic",
            measured="synthetic",
            verdict="MET",
            what_would_close_it="   ",
        )


def test_TC_ArgusAgent_PRECISION_001_57_the_threshold_is_an_exact_fraction_not_a_float() -> None:
    """TC-ArgusAgent-PRECISION-001-57 — AC2.1/AR4: a Fraction-vs-float divergence, DEMONSTRATED.

    **Observable:** the comparison ``precision >= PRECISION_GATE_THRESHOLD``. Not asserted
    — **demonstrated**: a denominator exists at which the float arithmetic and the exact
    ``Fraction`` arithmetic disagree about whether the gate clears, and the shipped
    threshold is the one that answers the question that was asked. The divergent case is
    SEARCHED FOR rather than hand-picked, so the guard keeps working if the threshold ever
    legitimately moves.
    """
    assert PRECISION_GATE_THRESHOLD == Fraction(4, 5), (
        "the locked ≥80% externalization-gate threshold moved. A failed measurement is "
        "not a reason to amend the threshold (protocol §5; Story 13.3 / AC5)."
    )
    assert not isinstance(PRECISION_GATE_THRESHOLD, float)

    # DIVERGENCE 1 — the FLOAT THRESHOLD, at the exact boundary. The double nearest to
    # 0.8 is strictly GREATER than 4/5, so a gate written `precision >= 0.8` REFUSES a
    # measured precision of exactly four-fifths: a false RED on the boundary the whole
    # threshold is about. Demonstrated, not asserted — the two comparisons disagree here.
    assert Fraction(4, 5) < 0.8, (
        "the double nearest 0.8 is no longer strictly greater than 4/5, so this "
        "demonstration would be asserting a property it never observed"
    )
    exact_boundary = Fraction(4, 5)
    assert (exact_boundary >= PRECISION_GATE_THRESHOLD) is True
    assert (exact_boundary >= 0.8) is False
    assert (exact_boundary >= PRECISION_GATE_THRESHOLD) != (exact_boundary >= 0.8), (
        "a float threshold and the exact Fraction threshold disagree at exactly 80%, "
        "which is the whole reason AR4 forbids the float"
    )

    # DIVERGENCE 2 — the PERCENTAGE LITERAL, the other half of AR4's ban. A gate written
    # `round(100 * tp / (tp + fp)) >= 80` CLEARS a precision of 199/250, which is 79.6%
    # and is below the threshold. A false GREEN, on the externalization gate.
    rounding_frauds = [
        (numerator, denominator)
        for denominator in range(1, 400)
        for numerator in range(denominator + 1)
        if Fraction(numerator, denominator) < PRECISION_GATE_THRESHOLD
        and round(100 * numerator / denominator) >= 80
    ]
    assert rounding_frauds, (
        "no rounded-percentage divergence was found in the searched range, so this guard "
        "would be asserting a property it never observed. Widen the search rather than "
        "deleting the assertion (non-vacuity floor, AI-E11-1)."
    )
    numerator, denominator = rounding_frauds[0]
    exact = Fraction(numerator, denominator)
    assert exact < PRECISION_GATE_THRESHOLD
    assert round(100 * numerator / denominator) >= 80
    assert ratio_string(exact) == f"{exact.numerator}/{exact.denominator}"
    assert "." not in ratio_string(exact), "a ratio rendered with a decimal point is a float"

    # The committed decision publishes the threshold in the same exact form.
    payload = _decision_payload()
    assert payload["precision"]["threshold"] == ratio_string(PRECISION_GATE_THRESHOLD)


def test_TC_ArgusAgent_PRECISION_001_58_the_dispatch_moves_at_the_real_seam() -> None:
    """TC-ArgusAgent-PRECISION-001-58 — AC1: every outcome is REACHED, from variants GENERATED.

    **Observable:** :func:`decide_gate`'s three-way dispatch. **Adversarial variants
    GENERATED from the committed record itself** (never hand-written), with their counts,
    per the guard-adequacy clause:

    * every residual resolved ``FP`` → the run becomes exhaustive → a §5 outcome, and
      because the ratio then falls short it is ``NOT_CLEARED`` — *a result*;
    * every finding resolved ``TP`` → ``CLEARED``, which proves the CLEARED branch is
      reachable at all and is not dead code guarding a state nobody can enter;
    * exactly one disposition removed → ``BLOCKED`` with residual **1**, never a pass over
      the rest;
    * exactly one made ``BORDERLINE`` → ``BLOCKED``, because §4's ladder has not terminated;
    * ``reproducibility_verified=False`` with a FULL set of judgements → ``BLOCKED``,
      proving the determinism precondition is evaluated BEFORE the arithmetic;
    * an empty expected population → ``VacuousDecisionError``, never a confident answer.
    """
    record = _record()
    rows = record.rows
    expected = [row.finding_id for row in rows]
    assert len(expected) > 2, "non-vacuity: need >2 findings to remove exactly one"

    # RE-AUTHORED 2026-08-20 (Story 16.1 / AC1.5) as an INTENDED BEHAVIOUR CHANGE, not
    # relaxed. §5's fifth condition means the committed population — 2 contributing members
    # — can no longer reach a §5 outcome at all, so the two variants below are generated
    # over a population that satisfies breadth and the narrow one is asserted BLOCKED on
    # breadth immediately after. Without this the guard would have gone red mid-round on a
    # line nobody edited, and its stated subject (the dispatch) would have quietly become
    # the breadth floor.
    # ⛔ RE-AUTHORED AGAIN 2026-08-20 (Story 16.2 / AC6.3), INTENDED BEHAVIOUR CHANGE. §5
    # gained a SIXTH condition and every RATIFIED member is `pre-seal`, so 16.1's repair
    # stopped reaching a §5 OUTCOME. `_spread` now generates over the SEALED rows and the
    # same rows are the decision's corpus, so concentration and partitions describe ONE
    # population. Nothing is relaxed: CLEARED must still be reachable at the real seam.
    broad = _spread(record)
    sealed = sealed_corpus_members()
    broad_rows = broad.rows
    all_fp = _decide(
        broad.append([_judged(row, "FP") for row in broad_rows]), corpus=sealed
    )
    assert all_fp.outcome == "NOT_CLEARED", all_fp.outcome_reason
    assert all_fp.fold.evaluable is True
    assert "RESULT" in all_fp.outcome_reason or "result" in all_fp.outcome_reason
    assert all_fp.failed_conditions, "a NOT_CLEARED decision must name a failing condition"

    all_tp = _decide(
        broad.append([_judged(row, "TP") for row in broad_rows]), corpus=sealed
    )
    assert all_tp.outcome == "CLEARED", all_tp.outcome_reason
    assert all(c.verdict == "MET" for c in all_tp.conditions)
    # ...and the SAME all-TP judgements over the NARROW committed population do NOT clear.
    # This is the amendment working, driven at the real seam, in the direction that matters.
    narrow_tp = _decide(record.append([_judged(row, "TP") for row in rows]))
    assert narrow_tp.outcome == "BLOCKED", narrow_tp.outcome_reason
    assert section_5_condition(narrow_tp.conditions, BREADTH_CONDITION_ID).verdict == "FAILED"
    assert narrow_tp.fold.meets_threshold and narrow_tp.fold.evaluable, (
        "non-vacuity: the narrow variant must be over threshold and otherwise evaluable, or "
        "the refusal could be caused by something other than breadth"
    )
    assert "ATTESTED externalization and NOTHING ELSE" in all_tp.outcome_reason, (
        "a cleared gate authorises attested externalization and nothing else, and the "
        "record must say so where it says 'cleared'"
    )

    # A finding the corpus EMITTED that carries no row at all. Generated by dropping
    # exactly one finding's rows from the record while leaving it in the expected
    # population — which is the real seam, and the reason the producer derives the
    # expected population from the adjudication SET rather than from the record itself.
    missing_one = _decide(
        replace(
            record,
            rows=rows[1:] + tuple(_judged(row, "TP") for row in rows[1:]),
        ),
        expected=expected,
    )
    assert missing_one.outcome == "BLOCKED"
    assert isinstance(missing_one.fold.exhaustiveness, AdjudicationUnevaluable)
    assert missing_one.fold.exhaustiveness.residual_count == 1, (
        "one undisposed finding must make the run BLOCKED with residual 1 — never a pass "
        "over the 30 that remain, which is the sampled measurement §4 forbids"
    )
    assert missing_one.closure_path

    one_borderline = _decide(
        record.append(
            [_judged(rows[0], "BORDERLINE")] + [_judged(row, "TP") for row in rows[1:]]
        )
    )
    assert one_borderline.outcome == "BLOCKED", (
        "BORDERLINE is a first-class outcome and still a residual: §4's ladder has not "
        "terminated, so the corpus is not exhaustively adjudicated"
    )

    non_repro = AdjudicationRecord(
        protocol_version=record.protocol_version,
        adjudication_unit=record.adjudication_unit,
        corpus_source=record.corpus_source,
        reproducibility_verified=False,
        reproducibility_source="synthetic: one member diverged between two runs",
        expert_hours=Fraction(3, 2),
        expert_hours_note="synthetic",
        rows=rows + tuple(_judged(row, "TP") for row in rows),
    )
    blocked_repro = _decide(non_repro, expected=expected)
    assert blocked_repro.outcome == "BLOCKED"
    assert blocked_repro.fold.total_tp == len(rows) > 0, (
        "the fixture must genuinely carry a full set of TP judgements, or the refusal "
        "could be caused by absent dispositions rather than by determinism"
    )
    assert "reproducib" in blocked_repro.outcome_reason.lower()

    with pytest.raises(VacuousDecisionError):
        _decide(record, expected=[])
    with pytest.raises(VacuousDecisionError):
        _decide(replace(record, rows=()), expected=expected)


# ─────────────────────────────────────────────────────────────────────────────
# Story 13.5 / AC5 — the vacuity floor NARROWED, proved in BOTH directions
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_69_the_empty_population_floor_discriminates() -> None:
    """TC-ArgusAgent-PRECISION-001-69 — Story 13.5 / AC5: narrowed, never removed.

    **Observable:** :func:`decide_gate` at the real seam, over the COMMITTED record, with an
    empty ``expected_finding_ids`` and a :class:`CorpusReadProof` that is varied one conjunct
    at a time.

    Until Story 13.5 an empty emitted population raised unconditionally, and the message
    named the confusion it could not resolve: *"the corpus could not be read, not that
    everything in it was judged"*. Epic 14 made the second case real — a corpus that WAS
    read and promoted nothing. Narrowing a floor is how a guard quietly becomes a hole, so
    both directions are proved here and the adversarial variants are GENERATED from the
    positive fixture by flipping each conjunct in turn, not hand-listed.
    """
    record = _record()
    assert len(record.rows) > 0, "non-vacuity: the committed record is EMPTY"

    # ── direction 1: NO evidence. The refusal is byte-unchanged in substance. ──────────
    with pytest.raises(VacuousDecisionError) as bare:
        _decide(record, expected=[])
    assert "the corpus could not be read" in str(bare.value)

    # ── direction 2: evidence, and it holds. The outcome becomes EXPRESSIBLE. ──────────
    decided = _decide(record, expected=[], corpus_read_proof=_read_proof())
    assert decided.outcome == "BLOCKED", decided.outcome
    assert decided.outcome in GATE_OUTCOMES, (
        "the narrowing invented a terminal state. GATE_OUTCOMES is closed at three and "
        "BLOCKED already means 'no §5 decision was taken'; a fourth member would give two "
        "names to one state."
    )
    assert len(GATE_OUTCOMES) == 3
    precision = next(
        c for c in decided.conditions if c.condition_id == "precision-at-least-80-percent"
    )
    assert precision.verdict == "UNEVALUABLE", precision.verdict
    assert precision.verdict in CONDITION_VERDICTS
    assert decided.closure_path, "a BLOCKED decision with no closure path is a shrug"
    assert any("DF-13-5-A" in step for step in decided.closure_path), (
        "the closure path must name the PRE-REGISTERED stopping rule. Without it the "
        "recorded reading is 'expand the bench until it passes', which is corpus-shopping "
        "with extra steps."
    )
    assert "was read" in decided.outcome_reason.lower()

    # ── the GENERATED adversarial variants: one conjunct at a time, each must REFUSE ───
    breaking: tuple[dict[str, object], ...] = (
        {"members_audited": 0},
        {"source_file_count": 0},
        {"scored_population_count": 0},
        {"every_member_pin_verified": False},
        {"every_member_byte_reproducible": False},
    )
    for override in breaking:
        proof = _read_proof(**override)
        assert not proof.proves_corpus_was_read, override
        with pytest.raises(VacuousDecisionError) as refusal:
            _decide(record, expected=[], corpus_read_proof=proof)
        assert "positive corpus-read proof" in str(refusal.value), override
    # ...and the positive control for the generator itself: with NO override it passes, so
    # the loop above is proving the conjunct and not the fixture.
    assert _read_proof().proves_corpus_was_read

    # A proof with no statement is not a proof — it is a flag, and a flag is what this type
    # replaces. Construction refuses it.
    with pytest.raises(VacuousDisclosureError):
        _read_proof(statement="   ")

    # A NON-EMPTY population ignores the proof entirely: the narrowing must not become a way
    # to bypass exhaustiveness when there IS something to be exhaustive over.
    with_rows = _decide(record, corpus_read_proof=_read_proof())
    assert with_rows.outcome == "BLOCKED"
    assert "NOT exhaustively adjudicated" in with_rows.outcome_reason, (
        "supplying a corpus-read proof changed the reason for a NON-empty population. The "
        "proof answers one question only: whether an EMPTY population was read."
    )


def test_TC_ArgusAgent_PRECISION_001_70_the_committed_decision_says_which_blocked_it_is() -> None:
    """TC-ArgusAgent-PRECISION-001-70 — Story 13.5 / AC4: same outcome member, different claim.

    **Observable:** the committed ``gate-decision-record.json``. Story 13.3 recorded
    ``BLOCKED`` on EXHAUSTIVENESS — five residual §4 ladders. Story 13.5 records ``BLOCKED``
    on the DENOMINATOR — the corpus was read and nothing was promoted. Same registered
    outcome member, two different facts, and a reader who cannot tell them apart will
    conclude nothing changed.

    The non-vacuity floor comes first: the artifact must carry the population it measured
    before its zero is read as a result.
    """
    payload = _decision_payload()
    assert payload["outcome"] == "BLOCKED"

    proof = payload.get("corpus_read_proof")
    assert proof is not None, (
        "the committed decision records BLOCKED over an empty emitted population with NO "
        "corpus-read proof. That combination is the unread-corpus case and decide_gate "
        "refuses it — an artifact carrying it means the artifact is stale."
    )
    assert proof["proves_corpus_was_read"] is True
    assert proof["source_file_count"] > 1000
    assert proof["scored_population_count"] > 1000
    assert proof["advisory_finding_count"] > 1000
    assert proof["blocking_finding_count"] == 0

    reason = payload["outcome_reason"]
    assert "READ" in reason and "promoted" in reason, reason
    assert "NOT an unread corpus" in reason
    assert "not a shortfall" in reason.lower(), (
        "the recorded reason must say what this outcome is NOT. A gate that did not clear "
        "because findings were judged and enough were false is a MEASUREMENT; a gate whose "
        "denominator is empty is an ABSENCE."
    )
    # The architecture's Gate-decision enforcement rule, verbatim, on the live artifact.
    assert "the gate did not clear" not in reason.lower()

    # AC9 — the provenance of the revision that did the reading is RECORDED either way, and
    # where it cannot be established the marker is the mechanically-recognised one.
    provenance = payload["commit_sha_provenance"]
    assert provenance.startswith(("ESTABLISHED", "NOT ESTABLISHED")), provenance

    # §5's precision condition carries the CONDITION verdict, not a fourth gate outcome.
    verdicts = {c["condition_id"]: c["verdict"] for c in payload["section_5_conditions"]}
    assert verdicts["precision-at-least-80-percent"] == "UNEVALUABLE"
    assert "UNEVALUABLE" not in payload["outcome_vocabulary"], (
        "UNEVALUABLE reached the OUTCOME vocabulary. It is a CONDITION verdict; recording "
        "it as a fourth outcome invents a terminal state 13.3 deliberately closed."
    )
    assert payload["outcome_vocabulary"] == sorted(GATE_OUTCOMES)
