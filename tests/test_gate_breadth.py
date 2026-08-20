"""Story 16.1 — protocol §5's BREADTH condition, driven to BOTH outcomes by real populations.

``TC-ArgusAgent-PRECISION-001-82``..``-85``. A **NEW** module, per AC8.5 and this story's
own measurement: ``tests/test_gate_decision.py`` is effectively full at this project's
guard density, and *"do not shave a file to fit"* is the rule.

**The subject.** The gate record has DERIVED the concentration of its own denominator since
2026-08-17 and said, in writing, that it was *"derived — not a threshold and not a
distribution requirement"*. That sentence was correct and it was **inert**: a gate could
clear on a ratio computed over one repository, and the record would disclose it in a
paragraph a reader is free to skip. Story 16.1 makes the member arm of that disclosure a §5
condition. These guards are what stop it being a constant somebody typed.

**Why the ``MET`` direction is the one that matters here, and is built deliberately**
(AC4.3). The committed record can only produce ``FAILED`` — its findings come from 2
ratified members — and the live fold is *already* unevaluable for a reason that has nothing
to do with breadth (the emitted blocking population is empty). A guard built only against
the committed record would therefore be green, silent and useless: it would never observe
the condition holding, never observe it binding, and never notice if the predicate were
inverted. Every population below is **GENERATED**, spread over an exactly-known number of
contributing members, and the guards assert **where the verdict flips**, not merely that it
has two possible values.

**GUARD-ADEQUACY (architecture §Enforcement) is discharged per guard**: each names its
**observable**, each moves the defect at the **real seam** (the shipped ``decide_gate`` over
real :class:`AdjudicationRow` objects through the real :class:`AdjudicationRecord` — the
``-58``/``-59`` pattern, never a reconstruction), and each **GENERATES** its adversarial
variants from the committed record or from ``SECTION_5_CONDITIONS`` with their counts.

**Non-vacuity is asserted FIRST in every guard** (``DF-15-2-A`` arm (b)): the population
built is non-empty, the counts compared actually differ, and the flip point is asserted to
lie strictly inside the generated range — a family that never crossed the floor cannot pass.

**Platform neutrality** (the local gates here are Windows-only while CI runs an ubuntu
matrix): ``pathlib``, explicit ``encoding="utf-8"``, ``.as_posix()`` at every path→string
boundary, and no assertion on ``os.sep``, a drive letter or a CRLF-sensitive byte count.

**Nothing below is written to any committed artifact.** Every synthetic judgement lives
inside one test's local fixture, and no detector, repository or bench candidate is touched.
"""

from __future__ import annotations

import ast
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from argus.precision.adjudication import (
    AdjudicatedPrecision,
    AdjudicationRecord,
    AdjudicationRow,
    Exhaustive,
    fold_adjudicated_precision,
    load_record,
    validation_set_population_n,
)
from argus.precision.gate_breadth import (
    ADJUDICATED_POPULATION_LABEL,
    BREADTH_MEMBER_FLOOR_DERIVATION,
    VacuousBreadthFloor,
    assess_breadth,
    contributing_member_floor,
    effective_precision_gate_status,
)
from argus.precision.gate_decision import (
    BREADTH_CONDITION_ID,
    SECTION_5_CONDITIONS,
    CleanRepoEvidence,
    GateDecision,
    decide_gate,
    section_5_condition,
)
from argus.precision.gate_disclosure import derive_concentration, ratified_corpus_members
from argus.precision.replay_harness import PRECISION_GATE_THRESHOLD, registry_module

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_RECORD_PATH = _ARTIFACTS / "validation-corpus" / "adjudication-record.json"
_BREADTH_MODULE = _REPO_ROOT / "argus" / "precision" / "gate_breadth.py"

#: The named human protocol §2 designates. Synthetic fixtures attribute their SYNTHETIC
#: judgements to this string so the instrument's attribution rule is genuinely exercised;
#: not one of them is ever written to the committed record.
_ADJUDICATOR = "XAgent007 (Engineering Lead)"


def _record() -> AdjudicationRecord:
    assert _RECORD_PATH.is_file(), (
        f"the committed adjudication record is absent at "
        f"{_RECORD_PATH.relative_to(_REPO_ROOT).as_posix()}"
    )
    return load_record(_RECORD_PATH)


def _ratified() -> list[str]:
    members = [str(member["member_id"]) for member in ratified_corpus_members()]
    assert members, "non-vacuity: the manifest reports ZERO ratified members"
    return members


def _floor() -> int:
    return contributing_member_floor(int(registry_module().VALIDATION_SET_FLOOR_N))


def _population(*, contributing_members: int, size: int) -> AdjudicationRecord:
    """A judged population spread over EXACTLY *contributing_members* ratified members.

    Built at the real seam — real :class:`AdjudicationRow` objects carried by the real,
    committed :class:`AdjudicationRecord` (its protocol version, its reproducibility flag,
    its expert-hours), with only the ROWS replaced. Every row is a live ``TP`` judgement by
    the named human, so the fold is reproducible, exhaustive and above threshold and
    **breadth is the only thing moving** (AC4.3).

    The locators are per-index and therefore distinct, so the content-addressed row ids
    cannot collide and the population's size is exactly *size*.
    """
    members = _ratified()
    assert 1 <= contributing_members <= len(members)
    assert size >= contributing_members
    rows = tuple(
        AdjudicationRow(
            row_id=f"synthetic{index:04d}.0",
            member_id=members[index % contributing_members],
            rule_id="vacuous_test_ast",
            verdict_eligible=True,
            advisory=False,
            locator=f"pkg/tests/test_synthetic_{index}.py:{index + 1}",
            disposition="TP",
            adjudicator=_ADJUDICATOR,
            adjudicated_on="2026-08-17",
            reason="synthetic fixture: exercises the instrument, adjudicates nothing real",
        )
        for index in range(size)
    )
    record = replace(_record(), rows=rows)
    live = record.live_rows()
    assert len({row.member_id for row in live}) == contributing_members, (
        "non-vacuity: the generated population does not carry the number of contributing "
        "members it claims, so every assertion over it would be about the wrong fixture"
    )
    return record


def _decide(record: AdjudicationRecord) -> GateDecision:
    """Drive the shipped :func:`decide_gate` with the live derived corpus figures."""
    return decide_gate(
        record,
        expected_finding_ids=[row.finding_id for row in record.rows],
        population_n=validation_set_population_n(),
        floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
        protocol_change_log_head=record.protocol_version,
        clean_repo_evidence=CleanRepoEvidence(
            corpus="synthetic fixture standing in for the FR20 cartridge corpus",
            applicable=True,
            clean_repo_fp=0,
            clean_member_ids=("clean_control",),
            note="synthetic fixture",
        ),
        ratified_members=ratified_corpus_members(),
        record_is_tracked_in_git=True,
        commit_sha="0" * 40,
        decided_on="2026-08-17",
    )


def expected_section_5_outcome(fold: AdjudicatedPrecision, *, breadth_holds: bool) -> str:
    """Protocol §5's three-way dispatch, RECOMPUTED from its preconditions — ONE mirror.

    Shared by ``TC-ArgusAgent-PRECISION-001-55``, which drives it over the COMMITTED
    artifact, and by ``-86``, which drives it over GENERATED populations in BOTH directions.
    A second copy would be a second thing that can drift from the dispatch it mirrors, and
    the drift would be invisible to a reader of either (AR7 — reuse, never fork; the same
    reason ``tests/test_gate_decision.py`` already IMPORTS its analyzer rather than copying
    it).

    **It lives in the breadth module deliberately**, and the reason is recorded rather than
    left to be guessed: ``breadth_holds`` is the only term in this dispatch whose truth this
    project had to CONSTRUCT a population to observe, every such population lives here, and
    ``tests/test_gate_decision.py`` is full at this project's guard density — AC8.5's rule is
    *"do not shave a file to fit"*.

    *breadth_holds* is an ARGUMENT rather than something derived inside, so one caller can
    drive the clause both ways over the SAME fold. That is what makes the clause a guard
    instead of a comment: see ``-86``, and the 2026-08-20 review finding that made it
    necessary.

    PURE (AR8): a frozen fold and a bool in, a registered outcome name out. No I/O, no clock.
    """
    if fold.determinism is not None or not isinstance(fold.exhaustiveness, Exhaustive):
        return "BLOCKED"
    if fold.precision is None:
        return "BLOCKED"
    if not breadth_holds:
        return "BLOCKED"
    return "CLEARED" if fold.meets_threshold else "NOT_CLEARED"


def test_TC_ArgusAgent_PRECISION_001_82_the_breadth_floor_is_derived_from_the_one_locked_floor() -> None:
    """TC-ArgusAgent-PRECISION-001-82 — AC2.1/AC2.2(iv): the floor is a FUNCTION, never typed.

    **Observable:** :func:`contributing_member_floor` and the shipped module's own source.
    A floor typed as ``3`` would be indistinguishable from a derived one at every call site
    and would silently stop tracking ``VALIDATION_SET_FLOOR_N`` the moment that moved —
    which is the ``DF-8-5-C`` defect class (a hand-written number in an artifact about the
    very gate this epic measures) with the number moved into code.

    **The defect MOVES the observable:** the strict-majority property is asserted over a
    GENERATED range of locked floors, so a floor re-typed as any constant fails for every
    input but one, and a floor changed to a different function fails at a boundary.

    **Adversarial variants GENERATED, with their count:** every locked floor in ``1..24``
    — 24 of them — is required to equal *half, rounded up* exactly: at least half, and no
    more than necessary. The property is stated as ``ceil(n/2)`` and NOT as *"a strict
    majority"*, because the two coincide only at an ODD floor and asserting the stronger
    one would be a guard enforcing something the code does not compute. At the LOCKED floor
    of 5 the strict-majority reading does hold, and that is asserted separately. Plus the
    vacuous inputs, which must RAISE rather than return a floor no population could fail.

    **It changes nothing else** (AC2.2(iv)), asserted by execution rather than by claim:
    the ≥80% ``Fraction``, the ONE locked floor and ``MANIFEST_FIELDS`` are read live and
    required to be exactly what they were.
    """
    manifest = registry_module()
    locked = int(manifest.VALIDATION_SET_FLOOR_N)
    assert locked == 5, (
        "protocol §5's ONE locked floor moved. This story may not touch it — every change "
        "here makes clearing HARDER and touches no existing threshold."
    )
    assert PRECISION_GATE_THRESHOLD == Fraction(4, 5), "the ≥80% threshold moved"
    manifest_module = registry_module.__module__ and __import__(
        "argus.precision.replay_harness", fromlist=["corpus_manifest_module"]
    ).corpus_manifest_module()
    assert len(manifest_module.MANIFEST_FIELDS) == 9, "MANIFEST_FIELDS is closed at 9"
    assert manifest_module.eligible_member_count() == 5, "the five ratified members moved"

    # ── the strict-majority property, over a GENERATED range of locked floors ──────────
    drives = 0
    for candidate in range(1, 25):
        derived = contributing_member_floor(candidate)
        assert derived * 2 >= candidate, (
            f"a floor of {derived} over a locked N of {candidate} is below half — more "
            f"than half the corpus could contribute nothing and the gate would still clear"
        )
        assert (derived - 1) * 2 < candidate, (
            f"a floor of {derived} over a locked N of {candidate} demands more than half "
            f"rounded up; the derivation is {BREADTH_MEMBER_FLOOR_DERIVATION}"
        )
        assert derived <= candidate, (
            "the breadth floor exceeded the member count it is derived from, so it could "
            "never be met and would be a shutdown rather than a strengthening"
        )
        drives += 1
    assert drives == 24 > 1, f"the generator produced {drives} variants, 24 expected"
    # At the LOCKED floor specifically, "half rounded up" IS a strict majority, and that is
    # the property the §5 amendment claims. Asserted here so the claim is checked where it
    # is actually made, rather than generalised into a property the derivation lacks.
    assert contributing_member_floor(locked) * 2 > locked, (
        f"at the locked floor of {locked} the derived breadth floor "
        f"{contributing_member_floor(locked)} is not a strict majority, which is what "
        f"protocol §5's 2026-08-20 amendment states it is"
    )
    assert contributing_member_floor(locked) == 3

    # The floor a CONSTANT would have to be, shown not to work: no single integer satisfies
    # the property across the generated range, which is why it is a function.
    assert len({contributing_member_floor(n) for n in range(1, 25)}) > 1, (
        "non-vacuity: the derivation returned one value for every locked floor, so it is a "
        "constant wearing a function's hat"
    )

    # ── the vacuous direction RAISES; it never returns a floor that cannot fail ────────
    for vacuous in (0, -1, -5):
        with pytest.raises(VacuousBreadthFloor):
            contributing_member_floor(vacuous)

    # ── STRUCTURAL: the derivation is written ONCE, and not as a bare literal ──────────
    source = _BREADTH_MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    derivations = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "contributing_member_floor"
    ]
    assert len(derivations) == 1, "the derivation is written more than once, or not at all"
    body = ast.unparse(derivations[0])
    assert "validation_set_floor_n + 1" in body and "// 2" in body, body[-200:]
    assert "return 3" not in body, (
        "the derived floor was replaced by the integer it currently evaluates to; it would "
        "stop tracking VALIDATION_SET_FLOOR_N and nothing would notice"
    )


def test_TC_ArgusAgent_PRECISION_001_83_breadth_is_driven_to_both_outcomes_at_the_real_seam() -> None:
    """TC-ArgusAgent-PRECISION-001-83 — AC4.2/AC4.3: MET and FAILED, and WHERE it flips.

    **Observable:** §5's breadth condition verdict and the gate outcome, over populations
    that differ in exactly one property — how many distinct ratified members contributed.

    **The defect MOVES the observable at the real seam:** the shipped :func:`decide_gate`
    is driven over real rows through the real record. A population one member SHORT of the
    floor makes breadth ``FAILED``, §5's precision condition ``UNEVALUABLE`` and the outcome
    ``BLOCKED``; the SAME findings spread across one more member clear. Nothing else about
    the two populations differs — same size, same rule, same judgements, same header.

    **Adversarial variants GENERATED with their count:** one population per contributing
    member count in ``1..len(ratified)``, generated from the committed record's own header.
    The guard asserts the verdicts flip **exactly once** and **exactly at the derived
    floor** — a predicate that always answered ``MET``, always answered ``FAILED``, or was
    off by one anywhere in the range fails.

    **Non-vacuity first:** the range is asserted to STRADDLE the floor, so a corpus too
    small to exhibit both directions goes RED rather than passing silently.
    """
    members = _ratified()
    floor = _floor()
    assert 1 < floor <= len(members), (
        f"non-vacuity: the derived floor {floor} does not lie strictly inside the "
        f"generated range 1..{len(members)}, so this guard cannot observe a flip"
    )
    size = max(len(members) * 3, 6)

    verdicts: dict[int, str] = {}
    outcomes: dict[int, str] = {}
    for contributing in range(1, len(members) + 1):
        decision = _decide(_population(contributing_members=contributing, size=size))
        breadth = section_5_condition(decision.conditions, BREADTH_CONDITION_ID)
        precision = section_5_condition(decision.conditions, "precision-at-least-80-percent")
        verdicts[contributing] = breadth.verdict
        outcomes[contributing] = decision.outcome
        # The breadth condition's OWN verdict is a measured result, never UNEVALUABLE (AC3.2).
        assert breadth.verdict in ("MET", "FAILED"), breadth.verdict
        assert breadth.what_would_close_it.strip()
        if contributing < floor:
            assert precision.verdict == "UNEVALUABLE", (
                f"{contributing} contributing member(s) is below the floor of {floor}, so "
                f"§5's PRECISION condition must be UNEVALUABLE — a ratio over a denominator "
                f"this narrow is not a measurement of the tool"
            )
            assert decision.outcome == "BLOCKED", decision.outcome_reason
            assert decision.closure_path, "a BLOCKED decision recorded no closure path"
            assert str(floor) in breadth.measured and str(contributing) in breadth.measured
        else:
            assert precision.verdict == "MET", precision.measured
            assert decision.outcome == "CLEARED", decision.outcome_reason

    assert len(verdicts) == len(members) > 2, f"{len(verdicts)} variants generated"
    assert set(verdicts.values()) == {"MET", "FAILED"}, (
        f"the breadth predicate never took both values over {len(verdicts)} generated "
        f"populations: {verdicts!r}. A condition that cannot fail is not a threshold, and "
        f"a condition that cannot hold is a shutdown."
    )
    assert set(outcomes.values()) == {"BLOCKED", "CLEARED"}, outcomes
    flips = [
        n for n in range(2, len(members) + 1) if verdicts[n] != verdicts[n - 1]
    ]
    assert flips == [floor], (
        f"the breadth verdict flipped at {flips!r} and the derived floor is {floor}. It "
        f"must flip exactly once, exactly there: an off-by-one here is a §5 threshold that "
        f"admits one repository fewer, or demands one more, than the derivation says."
    )

    # The fold is NOT forked (DN-16-1-1): the same fold, over the sub-floor population, is
    # itself perfectly evaluable — so the refusal is genuinely breadth and nothing else.
    narrow = _population(contributing_members=floor - 1, size=size)
    fold = fold_adjudicated_precision(
        narrow,
        expected_finding_ids=[row.finding_id for row in narrow.rows],
        population_n=validation_set_population_n(),
        floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
    )
    assert fold.evaluable is True and isinstance(fold.exhaustiveness, Exhaustive)
    assert fold.meets_threshold is True, (
        "non-vacuity: the sub-floor population must be reproducible, exhaustive AND over "
        "threshold, or the BLOCKED outcome could be caused by something other than breadth"
    )


def test_TC_ArgusAgent_PRECISION_001_84_the_two_precision_surfaces_cannot_disagree() -> None:
    """TC-ArgusAgent-PRECISION-001-84 — AC3.3/`DF-9-2-B`: one evaluability, published once.

    **Observable:** the committed payload's ``precision.evaluable`` and ``precision.
    gate_status`` beside §5's precision verdict. A payload carrying ``evaluable = True``
    next to a §5 precision verdict of ``UNEVALUABLE`` is a **true status carrying a false
    subject**, on the surface that publishes the externalization gate — the same class this
    repository has already shipped twice and filed as ``DF-9-2-B``.

    **The defect MOVES the observable:** over the generated family, the payload's
    ``evaluable`` is asserted to be ``False`` **exactly** when §5's precision verdict is
    ``UNEVALUABLE``, in both directions. A decision that reported the fold's own value
    instead would pass the sub-floor cases as ``True`` and fail here.

    **Adversarial variants GENERATED with their count:** the same one-per-contributing-count
    family, each asserted in both directions, with both classes required non-empty.
    """
    members = _ratified()
    floor = _floor()
    disagreements = 0
    unevaluable_seen = 0
    evaluable_seen = 0
    for contributing in range(1, len(members) + 1):
        decision = _decide(
            _population(contributing_members=contributing, size=max(len(members) * 3, 6))
        )
        payload = decision.to_payload()
        verdict = section_5_condition(
            decision.conditions, "precision-at-least-80-percent"
        ).verdict
        evaluable = payload["precision"]["evaluable"]
        assert isinstance(evaluable, bool)
        if evaluable is (verdict == "UNEVALUABLE"):
            disagreements += 1
        if verdict == "UNEVALUABLE":
            unevaluable_seen += 1
            # The status SENTENCE agrees too, and it is the existing renderer's (AR7).
            assert payload["precision"]["gate_status"].startswith("unevaluable"), (
                payload["precision"]["gate_status"][:160]
            )
            assert "NEITHER cleared NOR met" in payload["precision"]["gate_status"]
            assert "DENOMINATOR TOO NARROW" in payload["precision"]["gate_status"], (
                "the unevaluable sentence does not name BREADTH as its reason, so it is a "
                "true status carrying the wrong reason (DF-9-2-B)"
            )
            # The fold's OWN value is still published beside it — nothing is hidden.
            assert payload["precision"]["fold_evaluable"] is True
            assert payload["precision"]["breadth_holds"] is False
        else:
            evaluable_seen += 1
            assert evaluable is True
            assert payload["precision"]["breadth_holds"] is True
    assert disagreements == 0, (
        f"{disagreements} generated population(s) published a precision.evaluable that "
        f"contradicted §5's own precision verdict"
    )
    assert unevaluable_seen > 0 and evaluable_seen > 0, (
        f"non-vacuity: the family produced {unevaluable_seen} unevaluable and "
        f"{evaluable_seen} evaluable case(s); both classes must be non-empty or this guard "
        f"checked an agreement it never saw broken"
    )
    assert floor > 1


def test_TC_ArgusAgent_PRECISION_001_85_the_measured_sentence_names_its_population_and_is_inert_today() -> None:
    """TC-ArgusAgent-PRECISION-001-85 — AC3.4/AC3.5/AR7: which population, and no outcome moved.

    **Observable, three of them.**

    *(i) AC3.4 — the sentence names WHICH population it counted.* The concentration is
    derived from the record's LIVE rows while the most recent adjudication set's EMITTED
    blocking population is a different, possibly empty set. That divergence predates this
    story and is out of scope to fix; what is in scope is that no reader can mistake one
    for the other, so the sentence is required to name its source and to disclose the rule
    class count it deliberately does **not** gate.

    *(ii) AR7 — the population NOUN is not forked.* :func:`effective_precision_gate_status`
    re-renders through the SAME ``precision_gate_status_for`` the fold used, and it must use
    the same noun for the same number. Asserted against the LIVE fold's own rendered string
    rather than against a copy of the literal, so a drift in either place goes red.

    *(iii) AC3.5 — the amendment is INERT on the live tree.* The committed record's dispatch
    reaches the empty-emitted-population branch before anything breadth-dependent, so the
    outcome must still be ``BLOCKED`` for the Story 13.5 reason and must NOT be the breadth
    reason. An amendment that is inert today and binds when the measurement runs is exactly
    what *"made before the measurement it governs"* means — and it is a claim that has to be
    executed, not asserted.
    """
    record = _record()
    ratified = _ratified()
    live = record.live_rows()
    assert live, "non-vacuity: the committed record has no live rows"

    concentration = derive_concentration(record, ratified_member_ids=ratified)
    breadth = assess_breadth(
        concentration,
        validation_set_floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
        population_source=_RECORD_PATH.name,
    )

    # (i) the sentence names its population, its counts and the arm it does NOT gate.
    assert _RECORD_PATH.name in breadth.measured
    assert "NOT over the emitted blocking population" in breadth.measured
    assert str(concentration.adjudicated_population) in breadth.measured
    assert str(concentration.distinct_rule_class_count) in breadth.measured
    assert "NOT gated" in breadth.measured, (
        "the rule-class arm is disclosed and deliberately not gated; a sentence that omits "
        "it lets a reader believe both arms landed"
    )
    assert breadth.holds is False, (
        "non-vacuity: the committed population is expected to be BELOW the floor, and if it "
        "is not, every 'this is what failing looks like' assertion above is unobserved"
    )

    # (ii) the noun is not forked — the live fold's own status string carries it.
    fold = fold_adjudicated_precision(
        record,
        expected_finding_ids=[row.finding_id for row in record.rows],
        population_n=validation_set_population_n(),
        floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
    )
    assert f"N={fold.n} {ADJUDICATED_POPULATION_LABEL}" in fold.gate_status, (
        f"the adjudicated-population NOUN forked: gate_breadth renders "
        f"{ADJUDICATED_POPULATION_LABEL!r} while the fold's own status reads "
        f"{fold.gate_status[:160]!r}. One number, two nouns, is two claims."
    )
    rendered = effective_precision_gate_status(
        fold=fold, breadth=breadth, protocol_path=record.protocol_version
    )
    assert rendered == fold.gate_status, (
        "the fold is already unevaluable for a §4 reason, so breadth cannot change the "
        "answer and the sentence must be returned BYTE-FOR-BYTE (NFR-P1)"
    )

    # (iii) the live outcome did not move, and it moved for the RIGHT reason.
    decision = _decide(record)
    assert decision.outcome == "BLOCKED", decision.outcome_reason
    assert "corpus WAS READ" not in decision.outcome_reason
    assert "BREADTH condition" not in decision.outcome_reason, (
        "the live decision is BLOCKED on BREADTH, which means the amendment changed the "
        "outcome's REASON on the committed population. It must still be BLOCKED for the "
        "reason it was blocked for before (AC3.5)."
    )
    assert section_5_condition(decision.conditions, BREADTH_CONDITION_ID).verdict == "FAILED"
    assert len(decision.conditions) == len(SECTION_5_CONDITIONS) == 5, (
        "§5 must now carry exactly five conditions: the four historical ones in their "
        "historical positions, plus the appended breadth condition (DN-16-1-2)"
    )


def test_TC_ArgusAgent_PRECISION_001_86_the_outcome_recomputation_carries_a_live_breadth_term() -> None:
    """TC-ArgusAgent-PRECISION-001-86 — AC1.5/AC4.1: ``-55``'s breadth clause, actually DRIVEN.

    **Why this guard exists, recorded rather than glossed.** Story 16.1's round 2 taught the
    §5 dispatch mirror a breadth term and marked AC1.5 discharged for
    ``TC-ArgusAgent-PRECISION-001-55``. The 2026-08-20 code review proved by EXECUTION that
    the claim was not supported: ``-55`` recomputes over the COMMITTED adjudication record,
    which carries 5 ``BORDERLINE`` rows and is therefore never :class:`Exhaustive`, so the
    first clause always fires and the breadth clause is unreachable for that fixture. Forcing
    ``holds = True`` in the shipped :func:`assess_breadth` left ``-55`` GREEN; disabling both
    breadth branches in ``gate_decision`` left it GREEN. **A clause no executed mutation can
    redden is the ``DF-15-2-A`` unreal-guard class** — here on the guard whose entire subject
    is *"the outcome is DERIVED, not chosen."* This guard is the repair, and it is the
    generated-fixture half of it; ``-55``'s docstring now states plainly which clause its own
    fixture reaches.

    **Observable:** the LIVE :func:`decide_gate` outcome over generated populations, compared
    against the SAME :func:`expected_section_5_outcome` recomputation ``-55`` uses.

    **The recomputation's breadth term is derived HERE from the fixture's own contributing
    member count and the derived floor — never from :func:`assess_breadth`.** That is the
    load-bearing detail: a guard that fed the shipped predicate's own answer back into its
    expectation would move in lockstep with the defect it hunts and would stay green through
    exactly the mutation the review ran.

    **The defect MOVES the observable at the real seam, in BOTH directions:** below the floor
    the recomputation says ``BLOCKED`` while a decision that ignored breadth says ``CLEARED``;
    at or above the floor it says ``CLEARED`` while a predicate stuck at ``FAILED`` says
    ``BLOCKED``. Both are asserted to have actually been observed.

    **Adversarial variants GENERATED with their count:** one population per contributing
    member count in ``1..len(ratified)``, each one asserted reproducible, exhaustive, over
    threshold and carrying exactly the member count it claims — so breadth is the ONLY term
    that can move the answer. On every below-floor population the clause is additionally
    asserted **decisive**, by flipping its argument over the identical fold.

    **Non-vacuity first** (``DF-15-2-A`` arm (b)): the generated range is asserted to straddle
    the floor, and the two observed directions are asserted to be different answers.
    """
    members = _ratified()
    floor = _floor()
    assert 1 < floor <= len(members), (
        f"non-vacuity: the derived floor {floor} does not lie strictly inside the generated "
        f"range 1..{len(members)}, so this guard could not observe the clause both ways"
    )
    size = max(len(members) * 3, 6)

    observed: dict[int, str] = {}
    decisive = 0
    for contributing in range(1, len(members) + 1):
        record = _population(contributing_members=contributing, size=size)
        decision = _decide(record)
        fold = decision.fold
        # NON-VACUITY, asserted BEFORE anything is compared: every clause ABOVE the breadth
        # clause must be false, or the recomputation would answer BLOCKED for a reason that
        # has nothing to do with breadth — which is precisely the defect this repairs.
        assert fold.determinism is None, fold.determinism
        assert isinstance(fold.exhaustiveness, Exhaustive), fold.exhaustiveness
        assert fold.precision is not None and fold.meets_threshold, (
            f"the generated population must be over threshold before breadth is asked "
            f"anything; got precision={fold.precision_ratio!r}"
        )
        # The breadth term, derived from the FIXTURE and the derived floor — never read back
        # out of the predicate under test.
        holds = contributing >= floor
        expected = expected_section_5_outcome(fold, breadth_holds=holds)
        assert expected == ("CLEARED" if holds else "BLOCKED"), expected
        assert decision.outcome == expected, (
            f"{contributing} contributing member(s) against a floor of {floor}: the "
            f"preconditions dictate {expected!r} and the live decision recorded "
            f"{decision.outcome!r}. §5's breadth condition is "
            f"{section_5_condition(decision.conditions, BREADTH_CONDITION_ID).verdict!r}"
        )
        observed[contributing] = decision.outcome
        if not holds:
            # THE CLAUSE IS DECISIVE over this identical fold: flip the one argument and the
            # recomputation answers the opposite. This is what "unreachable branch" looked
            # like before, and what makes it a driven branch now.
            assert expected_section_5_outcome(fold, breadth_holds=True) == "CLEARED", (
                "the breadth clause is not what refused this population — some other "
                "precondition is, so the clause is still undriven"
            )
            decisive += 1

    assert decisive >= 1, "no below-floor population was generated; the clause was never taken"
    assert len(observed) == len(members) > 1, observed
    assert set(observed.values()) == {"BLOCKED", "CLEARED"}, (
        f"the generated family observed only {sorted(set(observed.values()))} — a guard that "
        f"never saw the verdict flip cannot notice a predicate that stopped flipping"
    )
    assert all(observed[n] == "BLOCKED" for n in range(1, floor)), observed
    assert all(observed[n] == "CLEARED" for n in range(floor, len(members) + 1)), observed
