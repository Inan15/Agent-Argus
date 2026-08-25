"""Story 17.4 — the successor-reach RECORD MODEL and the fold, split out at the pre-registered line.

**Why this module exists at all, said plainly.** Story 17.4 §0.11 PRE-REGISTERED a split trigger
before a line of the producer was written: *"if the new producer projects > 1,000 lines, split the
record model out first"*. It projected 1,152 against ``NFR-M1``'s 1,200-line ceiling
(``TC-ArgusAgent-MAINT-001-02``, which sweeps ``scripts/`` too), so the split happened at that
point rather than being discovered at review. This is Story 17.3's precedent, reused.

**The seam is the honest one:** this module knows what a measurement RECORD is and how the frozen
criterion folds it; ``scripts/build_successor_reach_record.py`` knows how to WALK five third-party
checkouts at their pins. Neither needs the other's knowledge, and only the walk needs a corpus,
which is why every guard over this module is green on the ubuntu CI matrix with no checkouts
present.

**Nothing here can move the bar.** Every floor, the ratio floor, the exposure ceiling, the outcome
vocabulary, the population id and the output prefix are IMPORTED from
``scripts/precision_preregistration.py`` and not one is re-typed (``AI-E9-7`` / ``DF-8-5-C``).
:func:`fold` calls ``evaluate()`` with the measured counts UNMODIFIED and passes neither ``floors=``
nor ``ratio_floor=``: those injection points exist for a caller that already resolved them, not for
a caller that would like different ones.

**Nothing here can write a judgement.** :class:`SuccessorReachRow` RAISES on any disposition other
than ``UNADJUDICATED`` and on any adjudicator or date at all, and :func:`seed_successor_row` — the
only constructor a producer reaches — has no parameter that could carry one. Protocol §2 makes the
TP/FP judgement a named human's act; here writing one is unreachable rather than merely discouraged.

**No source byte lives on this record** (``NFR-S1``). A row carries a LOCATOR — a
repository-relative POSIX path and a line — and counts. Counts, never rendered sets, never a
``float`` (``NFR-D2`` / ``AR4``).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
for _entry in (str(_REPO_ROOT), str(_SCRIPTS)):  # pragma: no cover - script bootstrap
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

# ⛔ The band vocabulary and S1's specification pointer are IMPORTED from the shipped grader,
# never re-typed. This edge is also ``-151``'s non-vacuity anchor over this module: a walk that
# cannot resolve a KNOWN-PRESENT outbound edge to ``assertion_strength`` would report *"no second
# derivation of S1"* forever.
from argus.detectors.assertion_strength import (  # noqa: E402
    ASSERTION_STRENGTH_BANDS,
    S1_SPECIFICATION,
    UNESTABLISHED,
)
from argus.precision.adjudication import (  # noqa: E402
    ADJUDICATION_UNIT,
    AdjudicationUnevaluable,
    change_log_head_version,
    finding_row_id,
)
from argus.precision.silent_class import (  # noqa: E402
    LOCATOR_RE,
    SILENT_CLASS_RULE_ID,
    UNADJUDICATED,
    exhaustiveness_payload,
)
from argus.store.canonical import dumps  # noqa: E402
from precision_preregistration import (  # noqa: E402
    CONSEQUENCE_BELOW,
    CONSEQUENCE_MET,
    CRITERION_OUTCOMES,
    POPULATION_DERIVATION,
    POPULATION_ID,
    PREREGISTRATION_COMMIT_SHA,
    SUCCESSOR_OUTPUT_PATHS,
    CriterionAssessment,
    corpus_manifest_module,
    evaluate,
    precision_fraction,
)

_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_PROTOCOL = _ARTIFACTS / "precision-validation-protocol.md"

#: The record's file name. Its DIRECTORY is imported below and never written down here.
RECORD_FILENAME = "successor-reach-record.json"

#: ⛔ IMPORTED from the criterion module. ``SUCCESSOR_OUTPUT_PATHS[0]`` is the committed-output
#: prefix ``-139`` and ``-147`` use as a git pathspec; a re-typed copy that drifted by one
#: character would put this story's output outside the population the ordering guard walks, and
#: the guard would then go green by finding nothing.
SUCCESSOR_RECORD_PATH = f"{SUCCESSOR_OUTPUT_PATHS[0]}/{RECORD_FILENAME}"

RECORD_ABSOLUTE_PATH = _REPO_ROOT / SUCCESSOR_RECORD_PATH

#: The predicate this story measures, named by its ONE public entry point. Story 17.3's own
#: docstring: *"Story 17.4 must be able to MEASURE the shipped predicate without re-deriving it."*
S1_ENTRY_POINT = (
    "argus.detectors.vacuous_test.VacuousTestDetector.successor_evidence -> "
    "SuccessorVacuityEvidence, COMPOSITION-ONLY over the public "
    "argus.detectors.assertion_strength.s1_corroborated and grade_span_assertions"
)

#: ``S1`` is ADVISORY and this record says so on its face (specification §6.5; Story 17.3 AC6).
S1_STATUS = (
    "ADVISORY. S1 moves no verdict_eligible, no rule_id and no depth_supported; "
    "VacuousTestDetector._ast_corroborated's return expression is byte-unchanged "
    "(TC-ArgusAgent-PRECISION-001-146). S1's reach, whatever it is, is therefore NOT a shipped "
    "promotion, and this record is not a proposal to make it one."
)

#: ⛔ AC8.1 — ``DF-13-5-A``'s condition 1 was SHARPENED on 2026-08-24 and its subject is the
#: SHIPPED verdict-eligible predicate, *"whatever that predicate is at the time of measurement"*.
#: The discard half is read off the SHIPPED ``ProvenanceEvidence.sut_result_is_discarded`` property
#: rather than re-typed here, so this record and ``_ast_corroborated`` cannot disagree about it.
SHIPPED_VERDICT_ELIGIBLE_DEFINITION = (
    "The SHIPPED verdict-eligible predicate in force at the measured HEAD: "
    "VacuousTestDetector._ast_corroborated, i.e. the finding is heuristically vacuous (TRUE by "
    "construction for every row of this population - all of them are RECORDED "
    "vacuous_test_heuristic findings) AND fact (a), the span reaches a candidate SUT (entailed by "
    "discarded_sut_calls >= 1) AND fact (b), ProvenanceEvidence.sut_result_is_discarded "
    "(discarded_sut_calls >= 1 and consumed_sut_calls == 0, read off the SHIPPED property) AND "
    "mock_referencing_assertions >= 1. Counted from the shipped "
    "argus.precision.silent_class.score_span over the same (source_lines, span_edges, start, end) "
    "tuple S1 was scored on - one span resolution, two readings, no second derivation."
)

DERIVATION_SOURCE = (
    "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-set-13-5.json "
    "(Story 13.5, operator-ratified 2026-08-18) - the recorded vacuous_test_heuristic findings, "
    "READ through build_silent_class_record._population, the SAME derivation "
    "silent-class-record.json used. No detector was re-run over any corpus member, no member was "
    "ratified, no third-party source was fetched, and DF-13-5-A's one expansion round is UNSPENT."
)

DERIVATION_METHOD = (
    "Every member read from its PINNED COMMIT through the shipped content-addressed helpers: git "
    "ls-tree -r enumerates the in-scope blobs, git cat-file --batch reads them from the object "
    "database into a scratch tree, and every materialized file is re-hashed with git's own blob "
    "identity and compared to the id ls-tree reported. Each recorded finding is resolved to its "
    "definition at the pin, the span edges are taken from the shipped index, and the SAME "
    "(source_lines, span_edges, start, end) tuple is handed to TWO shipped readers side by side: "
    "VacuousTestDetector.successor_evidence for S1 and its assertion-strength bands, and "
    "argus.precision.silent_class.score_span for the shipped predicate's fact (b) arithmetic. "
    "NOTHING is re-parsed, re-graded or re-implemented: neither module carries an ast import, an "
    "assertion vocabulary, a statement-boundary rule or a SUT-name resolution."
)

TRANSCRIPTION_NOTE = (
    "NOTHING ON THIS RECORD WAS TRANSCRIBED. Every row was SEEDED UNADJUDICATED by "
    "scripts/build_successor_reach_record.py and carries no adjudicator, no date and no reason. "
    "Protocol section 2 registers UNADJUDICATED as the ONLY disposition an automated producer may "
    "write; the TP/FP/BORDERLINE judgement is a named human's act. If judgements are ever "
    "supplied they are transcribed VERBATIM, this note records that they were and from whom, and "
    "no row is ever inferred, completed or defaulted from another (DN-6)."
)

#: ⛔ AC7.2 — recorded as a stated precondition that was NOT REACHED. Never "satisfied", and never
#: silently omitted.
EXTERNAL_ADJUDICATOR_NOTE = (
    "AI-E16-7 (protocol section 4's EXTERNAL adjudicator, the ladder's third rung) is UNFILLED, "
    "and this story did NOT REACH that precondition - because it adjudicated nothing at all. NOT "
    "REACHED is not the same as satisfied and it is not the same as waived: it means the ladder "
    "was never engaged, so no row could persist in disagreement and none had to be resolved by "
    "default. The already-adjudicated record carries 5 BORDERLINE rows of 31, so the base rate of "
    "reaching the third rung is not low, which is why this is recorded rather than assumed away."
)

EXHAUSTIVENESS_GAP = (
    "no row of the S1 population carries a live TP/FP disposition, because this story adjudicates "
    "nothing (DN-17-4-2; protocol section 2). What would close the gap: a named human (protocol "
    "section 2) adjudicates each row at its cited locator, with AI-E16-7 FILLED first so that a "
    "persistent disagreement has a third rung to reach"
)

#: ⛔ Recorded VERBATIM from the imported constants, and ONLY where the outcome invokes one.
CONSEQUENCE_BY_OUTCOME: dict[str, str] = {
    "MET": CONSEQUENCE_MET,
    "NOT_MET": CONSEQUENCE_BELOW,
}

#: ⛔ True at EVERY outcome, including ``MET``. ``CONSEQUENCE_MET`` is explicit that meeting the
#: criterion *"promotes nothing and moves no protocol section 5 condition"*.
GATE_STATE: dict[str, Any] = {
    "externalization_gate": "BLOCKED",
    "precision_keystone_ge_80_percent": "NOT CLEARED",
    "protocol_cleared": False,
    "promotes_nothing": True,
    "gates_anything": False,
    "note": (
        "This record moves nothing at ANY outcome. It flips no verdict_eligible, no rule_id and "
        "no depth_supported; it adds no protocol row; it ratifies no member; it is a MEASUREMENT "
        "and, at most, a proposal. FR34's disclosure stands."
    ),
}


# ═════════════════════════════════════════════════════════════════════════════════════════
# The row, and the reason a producer cannot write a judgement into one
# ═════════════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class SuccessorReachRow:
    """One span ``S1`` corroborates, seeded UNADJUDICATED — and unable to be anything else.

    The constructor REFUSES any disposition other than :data:`UNADJUDICATED` and refuses an
    adjudicator or a date outright. That is not defensive programming: protocol §2 makes the
    TP/FP judgement a named human's act, and a producer that CAN write one has already made
    *"the automation tagged its own findings"* a failure mode a reviewer has to watch for. Here
    it is unreachable.
    """

    row_id: str
    member_id: str
    rule_id: str
    locator: str
    test_name: str
    pinned_sha: str
    #: ⛔ Counts, never rendered sets and never a ``float`` (``NFR-D2`` / ``AR4``).
    assertions_none: int
    assertions_existence: int
    assertions_value: int
    assertions_unestablished: int
    discarded_sut_calls: int
    consumed_sut_calls: int
    mock_referencing_assertions: int
    shipped_verdict_eligible: bool
    verdict_eligible: bool = False
    advisory: bool = True
    disposition: str = UNADJUDICATED
    adjudicator: None = None
    adjudicated_on: None = None
    reason: None = None

    def __post_init__(self) -> None:
        if self.disposition != UNADJUDICATED:
            raise ValueError(
                f"{self.locator}: a successor-reach row may only carry {UNADJUDICATED!r}, not "
                f"{self.disposition!r}. Protocol section 2 registers UNADJUDICATED as the ONLY "
                f"disposition an automated producer may write, and an autonomous story that tags "
                f"its own findings TP has measured nothing."
            )
        if self.adjudicator is not None or self.adjudicated_on is not None:
            raise ValueError(
                f"{self.locator}: a seeded row carries no adjudicator and no date. A judgement "
                f"needs a registered human, a date and a reason, and none of the three is "
                f"reachable from this producer."
            )
        if self.verdict_eligible:
            raise ValueError(
                f"{self.locator}: S1 is ADVISORY (specification section 6.5). A verdict-eligible "
                f"successor row would be a promotion taken by a measurement."
            )
        if not LOCATOR_RE.match(self.locator):
            raise ValueError(
                f"{self.locator!r} is not a repository-relative POSIX locator of the form "
                f"path/to/file.py:LINE. A drive-anchored or backslash locator is not portable "
                f"between the Windows local gate and the ubuntu CI matrix (AI-E13-1)."
            )

    def to_payload(self) -> dict[str, Any]:
        return {
            "row_id": self.row_id,
            "member_id": self.member_id,
            "rule_id": self.rule_id,
            "locator": self.locator,
            "test_name": self.test_name,
            "pinned_sha": self.pinned_sha,
            "assertions_none": self.assertions_none,
            "assertions_existence": self.assertions_existence,
            "assertions_value": self.assertions_value,
            "assertions_unestablished": self.assertions_unestablished,
            "discarded_sut_calls": self.discarded_sut_calls,
            "consumed_sut_calls": self.consumed_sut_calls,
            "mock_referencing_assertions": self.mock_referencing_assertions,
            "shipped_verdict_eligible": self.shipped_verdict_eligible,
            "verdict_eligible": self.verdict_eligible,
            "advisory": self.advisory,
            "disposition": self.disposition,
            "adjudicator": self.adjudicator,
            "adjudicated_on": self.adjudicated_on,
            "reason": self.reason,
        }


def seed_successor_row(
    *,
    member_id: str,
    rule_id: str,
    locator: str,
    test_name: str,
    pinned_sha: str,
    evidence: Any,
    score: Any,
    shipped_verdict_eligible: bool,
) -> SuccessorReachRow:
    """The ONLY row constructor the producer reaches, and it can make exactly one shape.

    ``evidence`` is a ``SuccessorVacuityEvidence`` off
    ``VacuousTestDetector.successor_evidence`` and ``score`` is a ``silent_class.SpanScore``;
    both are READ, and neither is recomputed. Seeding a span ``S1`` does NOT corroborate is
    refused — publishing a row about a test that does not raise the question is how a population
    quietly grows past what was measured, and here it would inflate the very count the criterion's
    yield floor is measured over.
    """
    if not evidence.s1_corroborated:
        raise ValueError(
            f"{locator}: S1 does not corroborate this span "
            f"(none={evidence.assertions_none} existence={evidence.assertions_existence} "
            f"value={evidence.assertions_value} "
            f"unestablished={evidence.assertions_unestablished})."
        )
    return SuccessorReachRow(
        row_id=finding_row_id(
            member_id=member_id,
            rule_id=rule_id,
            verdict_eligible=False,
            advisory=True,
            locator=locator,
        ),
        member_id=member_id,
        rule_id=rule_id,
        locator=locator,
        test_name=test_name,
        pinned_sha=pinned_sha,
        assertions_none=evidence.assertions_none,
        assertions_existence=evidence.assertions_existence,
        assertions_value=evidence.assertions_value,
        assertions_unestablished=evidence.assertions_unestablished,
        discarded_sut_calls=score.discarded_sut_calls,
        consumed_sut_calls=score.consumed_sut_calls,
        mock_referencing_assertions=score.mock_referencing_assertions,
        shipped_verdict_eligible=shipped_verdict_eligible,
    )


# ═════════════════════════════════════════════════════════════════════════════════════════
# The measurement as taken
# ═════════════════════════════════════════════════════════════════════════════════════════


class Reach:
    """The measurement as taken, plus everything the record has to be able to say.

    Every published distribution is a VIEW computed from the rows rather than a counter kept
    alongside them, so a distribution and a total cannot drift apart (``DF-8-5-C``).
    """

    def __init__(self) -> None:
        self.rows: list[SuccessorReachRow] = []
        self.walked = 0
        self.skipped: list[str] = []
        self.band_totals_walked: dict[str, int] = _empty_bands()
        self.band_totals_eligible: dict[str, int] = _empty_bands()
        self.shipped_promoted: list[tuple[str, str]] = []
        self.rule_ids_walked: dict[str, int] = {}
        self.verifications: list[dict[str, Any]] = []
        self.porcelain: dict[str, int] = {}
        self.members_walked: list[str] = []

    def tally(self, totals: dict[str, int], evidence: Any) -> None:
        """Accumulate the band counts a span reported — counts only, no set, no ``float``."""
        totals["none"] += evidence.assertions_none
        totals["existence"] += evidence.assertions_existence
        totals["value"] += evidence.assertions_value
        totals[UNESTABLISHED] += evidence.assertions_unestablished

    def eligible_by_member(self) -> dict[str, int]:
        return _tally_by(row.member_id for row in self.rows)

    def eligible_by_rule_class(self) -> dict[str, int]:
        return _tally_by(row.rule_id for row in self.rows)

    def shipped_promoted_by_member(self) -> dict[str, int]:
        return _tally_by(member_id for member_id, _ in self.shipped_promoted)

    def ordered_rows(self) -> list[SuccessorReachRow]:
        """Rows in a stable, platform-independent order: member, then path, then line.

        The line is sorted as an INTEGER: sorting the locator string alone would order
        ``foo.py:10`` before ``foo.py:9`` and make the record's bytes depend on how the walk
        happened to enumerate, which is exactly what ``--check``'s byte comparison must not.
        """

        def key(row: SuccessorReachRow) -> tuple[str, str, int]:
            path, _, line = row.locator.rpartition(":")
            return (row.member_id, path, int(line))

        return sorted(self.rows, key=key)


def _empty_bands() -> dict[str, int]:
    return {name: 0 for name in (*ASSERTION_STRENGTH_BANDS, UNESTABLISHED)}


def _tally_by(values: Any) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        out[value] = out.get(value, 0) + 1
    return {name: out[name] for name in sorted(out)}


# ═════════════════════════════════════════════════════════════════════════════════════════
# The fold — CALLED, never re-implemented
# ═════════════════════════════════════════════════════════════════════════════════════════


def sealed_contributing_members(member_ids: tuple[str, ...]) -> tuple[str, ...]:
    """Which contributing members are drawn from the SEALED partition — RESOLVED, not assumed.

    ⛔ Read from the shipped corpus manifest through the criterion module's own
    ``corpus_manifest_module()``, so the answer this record publishes and the answer the gate
    would compute are one lookup rather than two statements that can disagree. ⛔ Whatever this
    returns is REPORTED, never repaired: no member is ratified, no member moves between
    partitions, ``SEAL_CITATION_VALUES`` is not amended and ``SEAL_CONDITION_ID`` is not touched
    (AC3.2). Amending the seal to make the sealed arm clear is this epic's named anti-pattern,
    and no amount of local justification makes it permissible.
    """
    manifest = corpus_manifest_module()
    sealed = {
        member_id
        for member_id, partition in manifest.SEALED_PARTITION_TABLE
        if partition == "sealed"
    }
    return tuple(sorted(set(member_ids) & sealed))


def fold(reach: Reach) -> CriterionAssessment:
    """Hand the measured counts to the FROZEN criterion, unmodified, and return what it says.

    ⛔ ``floors=`` and ``ratio_floor=`` are NOT passed. Their injection points exist for a caller
    that has already resolved them, not for a caller that would like different ones, so this call
    takes ``resolution_floors()`` and ``precision_floor()`` as resolved defaults and cannot reach
    a different outcome by supplying a different floor.

    ⛔ ``true_positive_count`` and ``false_accusation_count`` are ZERO because this story
    adjudicates nothing (``DN-17-4-2``). They are not a placeholder and not an approximation:
    they are the true adjudicated counts for this population, and step (2) of the fold is the
    pre-registered answer to an empty denominator — recorded, never repaired into a flattering
    ``100%`` or a punitive ``0%``.
    """
    contributing = tuple(reach.eligible_by_member())
    return evaluate(
        verdict_eligible_count=len(reach.rows),
        contributing_member_count=len(contributing),
        sealed_contributing_member_count=len(sealed_contributing_members(contributing)),
        true_positive_count=0,
        false_accusation_count=0,
    )


def assessment_payload(assessment: CriterionAssessment) -> dict[str, Any]:
    """The whole ``CriterionAssessment`` — outcome, reason, counts, floors AND derivations.

    ⛔ A bare verdict is unauditable: ``evaluate()``'s own docstring notes that ``NOT_MET`` with
    no counts cannot be told apart from ``NOT_MET`` measured over four findings. And
    ``ResolutionFloors`` carries its derivation strings precisely *"so the prose a record
    publishes and the arithmetic the gate runs are one object rather than two statements that can
    disagree"*.
    """
    floors = assessment.floors
    consequence = CONSEQUENCE_BY_OUTCOME.get(assessment.outcome)
    return {
        "outcome": assessment.outcome,
        "outcome_meaning": CRITERION_OUTCOMES[assessment.outcome],
        "reason": assessment.reason,
        "verdict_eligible_count": assessment.verdict_eligible_count,
        "contributing_member_count": assessment.contributing_member_count,
        "sealed_contributing_member_count": assessment.sealed_contributing_member_count,
        "true_positive_count": assessment.true_positive_count,
        "false_accusation_count": assessment.false_accusation_count,
        "adjudicated_count": assessment.adjudicated_count,
        "measured_precision": assessment.measured_precision,
        "measured_precision_note": (
            "null means there is NO DENOMINATOR - the adjudicated population is empty - and it "
            "is recorded as null on purpose. It is NEVER 1 and never 0: an unmeasured population "
            "must not inherit a flattering default, and the measured precedent for that failure "
            "is bc55e36, where a corpus that emitted nothing reported a CLEARED gate."
        ),
        "ratio_floor": assessment.ratio_floor,
        "exposure_ceiling": assessment.exposure_ceiling,
        "floors": {
            "verdict_eligible_population": floors.verdict_eligible_population,
            "contributing_members": floors.contributing_members,
            "sealed_contributing_members": floors.sealed_contributing_members,
            "validation_set_floor_n": floors.validation_set_floor_n,
            "verdict_eligible_population_derivation": (
                floors.verdict_eligible_population_derivation
            ),
            "contributing_members_derivation": floors.contributing_members_derivation,
            "sealed_contributing_members_derivation": (
                floors.sealed_contributing_members_derivation
            ),
        },
        # ⛔ VERBATIM from the imported constant where the outcome invokes it, never paraphrased
        # (AI-E9-7). UNEVALUABLE invokes neither, and the record says so rather than borrowing one.
        "consequence": consequence,
        "consequence_note": (
            "Recorded VERBATIM from the imported constant this outcome invokes."
            if consequence is not None
            else (
                "This outcome invokes NEITHER CONSEQUENCE_MET nor CONSEQUENCE_BELOW. UNEVALUABLE "
                "is neither a pass nor a failure: it is a recorded failure to evaluate, and "
                "borrowing one of the other two consequences would convert it into one of them."
            )
        ),
    }


def shortfalls(assessment: CriterionAssessment) -> list[dict[str, Any]]:
    """Every resolution floor the measured population is short of, with its own derivation.

    AC3.1. ⛔ Reported for EVERY short floor rather than only the one the fold happened to return
    on: *"which floor stopped it first"* is an artefact of check order, and *"which floors are
    short"* is the measurement. ⛔ A shortfall is REPORTED, never repaired — the floors are
    ``precision_preregistration``'s, they were frozen before the number existed, and
    ``TC-ArgusAgent-PRECISION-001-140`` reds on a loosening.
    """
    floors = assessment.floors
    triples = (
        (
            "verdict_eligible_population",
            assessment.verdict_eligible_count,
            floors.verdict_eligible_population,
            floors.verdict_eligible_population_derivation,
        ),
        (
            "contributing_members",
            assessment.contributing_member_count,
            floors.contributing_members,
            floors.contributing_members_derivation,
        ),
        (
            "sealed_contributing_members",
            assessment.sealed_contributing_member_count,
            floors.sealed_contributing_members,
            floors.sealed_contributing_members_derivation,
        ),
    )
    return [
        {
            "floor": name,
            "measured": measured,
            "required": floor,
            "shortfall": floor - measured,
            "derivation": derivation,
        }
        for name, measured, floor, derivation in triples
        if measured < floor
    ]


# ═════════════════════════════════════════════════════════════════════════════════════════
# The record
# ═════════════════════════════════════════════════════════════════════════════════════════


def floor_results(assessment: CriterionAssessment) -> list[dict[str, Any]]:
    """ALL THREE resolution floors — the ones that cleared as well as the ones that did not.

    ``shortfalls()`` answers *"what was short"*; this answers *"what was checked"*. Publishing
    only the shortfalls would leave a reader unable to tell a floor that CLEARED from a floor the
    fold never got to, and ``evaluate()`` returns on the FIRST short floor by design.
    """
    floors = assessment.floors
    return [
        {
            "floor": name,
            "measured": measured,
            "required": required,
            "cleared": measured >= required,
        }
        for name, measured, required in (
            (
                "verdict_eligible_population",
                assessment.verdict_eligible_count,
                floors.verdict_eligible_population,
            ),
            (
                "contributing_members",
                assessment.contributing_member_count,
                floors.contributing_members,
            ),
            (
                "sealed_contributing_members",
                assessment.sealed_contributing_member_count,
                floors.sealed_contributing_members,
            ),
        )
    ]


def empty_denominator_arm(assessment: CriterionAssessment) -> dict[str, Any]:
    """⛔ AC3.3 — the SECOND ``UNEVALUABLE`` arm, recorded whether or not the fold reached it.

    Story 17.4 §0.3 and §0.4 named **two independent arms** that both read failed before any
    number existed: ``sealed ∩ ratified`` is empty, and the adjudicated population of any
    successor class is empty. ``evaluate()`` evaluates the three RESOLUTION floors **before** it
    looks at any ratio and returns on the first shortfall, so at most ONE of the two can appear in
    the verdict's reason — and which one is an artefact of check order, not a fact about the
    population.

    ⛔ So the other arm is recorded HERE rather than omitted. AC3.3's forbidden outcomes are
    reporting an empty denominator as a flattering ``100%``, as a punitive ``0%``, or omitting it
    with the population implied to be fine; the measured precedent is ``bc55e36``, where a corpus
    that emitted nothing reported a CLEARED gate. ``reached_by_the_fold`` says plainly whether the
    verdict above rests on this arm or on a resolution floor.
    """
    return {
        "true_positive_count": assessment.true_positive_count,
        "false_accusation_count": assessment.false_accusation_count,
        "adjudicated_count": assessment.adjudicated_count,
        "precision_fraction_of_the_measured_counts": precision_fraction(
            assessment.true_positive_count, assessment.false_accusation_count
        ),
        "denominator_is_empty": assessment.adjudicated_count == 0,
        "reached_by_the_fold": not shortfalls(assessment),
        "note": (
            "The adjudicated population is EMPTY - 0 TP and 0 FP - because this story adjudicates "
            "NOTHING (DN-17-4-2; protocol section 2 registers UNADJUDICATED as the only "
            "disposition an automated producer may write, and protocol section 4's ladder has no "
            "third rung while AI-E16-7 is UNFILLED). The shipped precision_fraction over these "
            "counts returns null: there is no denominator and no ratio to compare against the "
            "floor. This is an INDEPENDENT UNEVALUABLE arm. If reached_by_the_fold is false, the "
            "verdict above was returned on a RESOLUTION floor instead - evaluate() checks the "
            "three resolution floors before any ratio - and this arm is recorded here rather than "
            "omitted, because both arms are true and only the check order decides which reason "
            "the verdict carries. AI-E11-1: an absence is evidence only over a population proved "
            "non-empty, and exhaustiveness over nothing is the guard that passes forever. What is "
            "NOT done here, and is forbidden: reporting this as 100%, as 0%, or leaving it out "
            "with the population implied to be fine (AC3.3). The measured precedent is bc55e36, "
            "where a corpus that emitted nothing reported a CLEARED gate."
        ),
    }


def record_payload(reach: Reach, assessment: CriterionAssessment) -> dict[str, Any]:
    """Everything the measurement found, and every figure DERIVED BY THIS RUN.

    ⛔ Nothing here is copied from ``epics.md``, from ``V2 = 36``, from ``V5 = 125`` or from their
    sum, and the record does NOT describe ``S1``'s reach as confirming, missing or approaching any
    prior figure: specification §4 measured those two by two different instruments at two
    different HEADs, so they are not comparable priors and their sum is not a prediction. This is
    the FIRST measurement of ``S1`` that has ever been taken.
    """
    manifest = corpus_manifest_module()
    contributing = tuple(reach.eligible_by_member())
    sealed = sealed_contributing_members(contributing)
    exhaustiveness = AdjudicationUnevaluable(
        reason=EXHAUSTIVENESS_GAP,
        residual_count=len(reach.rows),
        adjudicated_count=0,
    )
    return {
        "schema_version": 1,
        "story": "17.4 - run it once, and let the pre-registered criterion decide",
        "purpose": (
            "The ONE measurement of the successor predicate S1 over the five already-ratified "
            "corpus members at their pinned shas, folded through the criterion Story 17.1 froze "
            "in commit " + PREREGISTRATION_COMMIT_SHA + " while the answer was still zero."
        ),
        "predicate_id": "S1",
        "predicate_entry_point": S1_ENTRY_POINT,
        "predicate_specification": S1_SPECIFICATION,
        "predicate_status": S1_STATUS,
        "protocol_version": change_log_head_version(_PROTOCOL.read_text(encoding="utf-8")),
        "adjudication_unit": ADJUDICATION_UNIT,
        "population_id": POPULATION_ID,
        "population_derivation": POPULATION_DERIVATION,
        "derivation_source": DERIVATION_SOURCE,
        "derivation_method": DERIVATION_METHOD,
        "population_walked": reach.walked,
        "population_skipped": len(reach.skipped),
        "members_walked": sorted(reach.members_walked),
        "rule_classes_walked": {
            name: reach.rule_ids_walked[name] for name in sorted(reach.rule_ids_walked)
        },
        "rule_class_count_walked": len(reach.rule_ids_walked),
        "eligible_population_count": len(reach.rows),
        "eligible_by_corpus_member": reach.eligible_by_member(),
        "eligible_by_rule_class": reach.eligible_by_rule_class(),
        "eligible_rule_class_count": len(reach.eligible_by_rule_class()),
        "rule_class_axis_note": (
            "The rule-class axis of this population has EXACTLY ONE member, "
            + SILENT_CLASS_RULE_ID
            + ", and is reported as one. Every row of adjudication-set-13-5.json this "
            "measurement walks carries that rule_id; manufacturing a second axis to make the "
            "distribution look richer would be a second source of truth about one population "
            "(DF-8-5-C)."
        ),
        "contributing_member_count": len(contributing),
        "sealed_contributing_members": list(sealed),
        "sealed_contributing_member_count": len(sealed),
        "sealed_partition_note": (
            "REPORTED AS MEASURED AND NOT REPAIRED (AC3.2). The sealed partition and the "
            "ratified corpus are resolved from the shipped manifest through the criterion "
            "module's own corpus_manifest_module(); no member was ratified, no member moved "
            "between partitions, SEAL_CITATION_VALUES was not amended and SEAL_CONDITION_ID was "
            "not touched. Ratifying a sealed member is a protocol section 6 R2 OPERATOR ACT and "
            "no Epic 17 story may take one."
        ),
        "assertion_strength_bands": list(ASSERTION_STRENGTH_BANDS) + [UNESTABLISHED],
        "assertion_band_totals_walked": dict(reach.band_totals_walked),
        "assertion_band_totals_eligible": dict(reach.band_totals_eligible),
        "assertion_band_note": (
            "Story 17.3's reporting axis, carrying NO verdict weight in Epic 17. Counts of "
            "ASSERTIONS per band, summed over spans - never a rendered set and never a float "
            "(NFR-D2 / AR4). 'unestablished' is not a band on the scale: it is the count of "
            "assertions the scale could not grade, and one of them is enough to make (c') FALSE "
            "(specification section 6.3)."
        ),
        "shipped_verdict_eligible": {
            "definition_in_force": SHIPPED_VERDICT_ELIGIBLE_DEFINITION,
            "promoted_count": len(reach.shipped_promoted),
            "promoted_by_corpus_member": reach.shipped_promoted_by_member(),
            "df_13_5_a_condition_1_note": (
                "DF-13-5-A's condition 1, as SHARPENED 2026-08-24, fires when the count of "
                "findings the SHIPPED verdict-eligible predicate promotes over the five "
                "ALREADY-RATIFIED members rises above ZERO. This is that count, MEASURED rather "
                "than assumed. S1's own reach is NOT this number: S1 is ADVISORY (specification "
                "section 6.5) and an advisory predicate promotes nothing, so S1 is not the "
                "trigger's subject."
            ),
        },
        "corpus": {
            "eligible_member_count": manifest.eligible_member_count(),
            "eligible_member_count_note": (
                "Read from the shipped corpus manifest and UNCHANGED by this measurement. No "
                "member was ratified, no member moved between partitions, no third-party source "
                "was fetched and DF-13-5-A's one expansion round is UNSPENT."
            ),
            "pin_verifications": reach.verifications,
            "porcelain_captured_asserted_nowhere": dict(reach.porcelain),
            "porcelain_note": (
                "A corpus member is a live tree other people edit; its porcelain is CAPTURED and "
                "REPORTED and a difference is never a failure (DN-16-7-4). Nothing this "
                "measurement read came from a working tree: every byte came out of the object "
                "database at the pin and was re-hashed against the id ls-tree reported."
            ),
        },
        "criterion": assessment_payload(assessment),
        "criterion_floor_results": floor_results(assessment),
        "criterion_shortfalls": shortfalls(assessment),
        "criterion_empty_denominator_arm": empty_denominator_arm(assessment),
        "criterion_module": {
            "path": "scripts/precision_preregistration.py",
            "preregistration_commit_sha": PREREGISTRATION_COMMIT_SHA,
            "note": (
                "IMPORTED and BYTE-UNCHANGED. Every floor, the ratio floor, the exposure "
                "ceiling, the outcome vocabulary, the population id and the output prefix are "
                "resolved by CALLING the module; not one is re-typed in this record. The fold "
                "was called with the measured counts UNMODIFIED and with the RESOLVED DEFAULT "
                "floors - no floors= and no ratio_floor= were injected."
            ),
        },
        "output_prefix": SUCCESSOR_OUTPUT_PATHS[0],
        "output_prefix_note": (
            "IMPORTED from precision_preregistration.SUCCESSOR_OUTPUT_PATHS[0]. Successor output "
            "is committed under a declared prefix and NOWHERE ELSE: output committed elsewhere "
            "makes the ordering guard unprovable against the object database."
        ),
        "adjudication": {
            "external_adjudicator_ai_e16_7": "NOT REACHED",
            "external_adjudicator_note": EXTERNAL_ADJUDICATOR_NOTE,
            "adjudication_record_untouched": True,
            "adjudication_record_note": (
                "validation-corpus/adjudication-record.json is BYTE-UNCHANGED by this story. Its "
                "31 rows are vacuous_test_ast - the SHIPPED rule class - and there are ZERO "
                "adjudicated rows of any successor class. This story creates none."
            ),
        },
        "exhaustiveness": exhaustiveness_payload(exhaustiveness),
        "expert_hours": None,
        "expert_hours_note": (
            "NOT RECORDED - no adjudication run has taken place, and NOT RECORDED means exactly "
            "that and never zero. Protocol section 3's <= 4 expert-hour ceiling is a REPORT, "
            "never a gate."
        ),
        "transcription_note": TRANSCRIPTION_NOTE,
        "gate_state": dict(GATE_STATE),
        "promotes_nothing": True,
        "gates_anything": False,
        "rows": [row.to_payload() for row in reach.ordered_rows()],
    }


def record_text(reach: Reach, assessment: CriterionAssessment) -> str:
    """The record's committed bytes: canonical JSON plus one trailing newline."""
    return dumps(record_payload(reach, assessment)) + "\n"
