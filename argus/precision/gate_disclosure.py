"""Story 13.3 / AC3b — what the gate result must SAY about its own denominator.

Verification area ``TC-ArgusAgent-PRECISION-001-53``.. (``tests/test_gate_decision.py``).
A cohesion split from :mod:`argus.precision.gate_decision` (the 12.8 precedent, and the
NFR-M1 rule AC8.5 states in its own words: *"new guards go in a NEW module — do not shave
a file to fit"*). The split line is a real seam, not a line count: this module holds what
the result must **say** about the population it was measured over, and
:mod:`argus.precision.gate_decision` holds what the result **is**. Neither imports the
other's decision logic.

Two derivations live here, and both exist because a bare precision figure is a true number
that misleads:

* :func:`derive_concentration` — AC3b, added 2026-08-17 by the interim Epic-13
  retrospective (``AI-E13-5``) deliberately BEFORE the figure existed, because after
  adjudication any limitation attached to the result reads as an excuse if it fails and as
  goalpost-moving if it passes. **It changes no threshold.**
* :func:`derive_residual_completion_bound` — what the ratio could become under every
  admissible completion of an unterminated protocol §4 ladder, so a reader told *"k
  findings remain undecided"* can tell whether the outcome is genuinely open.

Every figure both produce is COUNTED from the committed record and the manifest and none
is pinned as a literal: ``DF-8-5-C`` is the defect class (a hand-written number in a proof
artifact about the very gate this epic measures) and ``AI-E9-7`` applies with full force.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from argus.precision.adjudication import AdjudicationRecord
from argus.precision.replay_harness import (
    PRECISION_GATE_THRESHOLD,
    corpus_manifest_module,
    precision_fraction,
    ratio_string,
)

__all__ = [
    "ConcentrationDisclosure",
    "ResidualCompletionBound",
    "VacuousDisclosureError",
    "derive_concentration",
    "derive_residual_completion_bound",
    "ratified_corpus_members",
]


class VacuousDisclosureError(ValueError):
    """Raised when a disclosure was requested over an empty population.

    The non-vacuity floor (``AI-E11-1``) as a TYPE. The concentration of an EMPTY
    population is unobservable, not "even" — a disclosure derived from zero rows would
    state a breadth nobody measured, on the artifact that publishes the externalization
    gate. :class:`argus.precision.gate_decision.VacuousDecisionError` subclasses this, so
    a caller that guards the decision has already guarded the disclosure.
    """


@dataclass(frozen=True)
class ConcentrationDisclosure:
    """AC3b — what the denominator is actually made of, DERIVED and never typed.

    §5's ``N >= 5`` is satisfied by MEMBER COUNT while the ratio is computed over whichever
    members actually emitted a blocking finding. *The N that gates and the N that
    contributes are different numbers*, and a bare precision figure overstates the breadth
    of what was measured whichever way the gate lands.

    Recorded deliberately BEFORE the figure existed (the interim Epic-13 retrospective,
    ``AI-E13-5``), because after adjudication any limitation attached to the result reads
    as an excuse if it fails and as goalpost-moving if it passes. **It changes no
    threshold**: §5's four conditions, the ≥80% ``Fraction``, the ``N >= 5`` floor, the
    unit and the corpus definition are untouched, and this is NOT a distribution
    requirement — the concentration is DISCLOSED, not corrected. Correcting it by dropping
    or re-weighting a member would be the threshold change AC5 forbids, wearing a hat.
    """

    ratified_member_ids: tuple[str, ...]
    contributing_member_ids: tuple[str, ...]
    non_contributing_member_ids: tuple[str, ...]
    per_member_finding_counts: tuple[tuple[str, int], ...]
    rule_class_ids: tuple[str, ...]
    per_rule_class_finding_counts: tuple[tuple[str, int], ...]
    adjudicated_population: int
    statement: str

    @property
    def ratified_member_count(self) -> int:
        return len(self.ratified_member_ids)

    @property
    def contributing_member_count(self) -> int:
        return len(self.contributing_member_ids)

    @property
    def distinct_rule_class_count(self) -> int:
        return len(self.rule_class_ids)

    @property
    def is_concentrated(self) -> bool:
        """Whether the population is narrower than the corpus that satisfies the floor.

        TRUE when some ratified member contributed nothing, or when every finding came
        from a single rule class. Deliberately a PREDICATE and not a threshold: it decides
        what the record must SAY, never what the gate must reach. Driven over a
        well-distributed synthetic population it must return ``False`` — a caveat that
        cannot be absent is not an observation.
        """
        return bool(self.non_contributing_member_ids) or self.distinct_rule_class_count <= 1

    def to_payload(self) -> dict[str, Any]:
        return {
            "ratified_member_count": self.ratified_member_count,
            "ratified_member_ids": list(self.ratified_member_ids),
            "contributing_member_count": self.contributing_member_count,
            "contributing_member_ids": list(self.contributing_member_ids),
            "non_contributing_member_ids": list(self.non_contributing_member_ids),
            "per_member_finding_counts": [
                {"member_id": member, "findings": count}
                for member, count in self.per_member_finding_counts
            ],
            "distinct_rule_class_count": self.distinct_rule_class_count,
            "rule_class_ids": list(self.rule_class_ids),
            "per_rule_class_finding_counts": [
                {"rule_id": rule, "findings": count}
                for rule, count in self.per_rule_class_finding_counts
            ],
            "adjudicated_population": self.adjudicated_population,
            "is_concentrated": self.is_concentrated,
            "statement": self.statement,
        }


def ratified_corpus_members() -> tuple[dict[str, str], ...]:
    """The ELIGIBLE validation-set members with their pinned shas — from the manifest.

    Reached through :func:`~argus.precision.replay_harness.corpus_manifest_module`, the
    ONE declared lazy edge to the repository-only corpus (``DF-9-2-A``). Nothing here is
    typed: the member ids and the pinned shas the decision record publishes are the
    manifest's own, so a ratification or an exclusion moves the record rather than
    contradicting it (``AI-E9-7``).
    """
    members = corpus_manifest_module().eligible_members()
    return tuple(
        {
            "member_id": str(spec.member_id),
            "commit_sha": str(spec.commit_sha),
            "primary_language": str(spec.primary_language),
            "provenance": str(spec.provenance),
        }
        for spec in members
    )


def derive_concentration(
    record: AdjudicationRecord, *, ratified_member_ids: Sequence[str]
) -> ConcentrationDisclosure:
    """DERIVE AC3b's concentration statement from the record and the manifest.

    Every figure is counted here and none is pinned: the per-member counts, the
    contributing-vs-ratified split and the distinct rule-class count are read off the live
    rows. ``DF-8-5-C`` is the defect class this avoids — a hand-written number in a proof
    artifact about the very gate this epic measures — and ``AI-E9-7`` applies with full
    force, so the figures in the story text are the state at authoring time and are NOT
    pinned as literals anywhere in this module or its guards.
    """
    live = record.live_rows()
    if not live:
        raise VacuousDisclosureError(
            "the concentration of an EMPTY population is unobservable, not 'even'. A "
            "disclosure derived from zero rows would state a breadth nobody measured "
            "(non-vacuity floor, AI-E11-1)."
        )
    ratified = tuple(dict.fromkeys(str(member) for member in ratified_member_ids))
    if not ratified:
        raise VacuousDisclosureError(
            "the ratified corpus is EMPTY, so 'contributing members vs. ratified members' "
            "has no denominator and the disclosure would be vacuous."
        )
    per_member = Counter(row.member_id for row in live)
    per_rule = Counter(row.rule_id for row in live)
    contributing = tuple(sorted(per_member))
    non_contributing = tuple(sorted(set(ratified) - set(contributing)))
    rule_classes = tuple(sorted(per_rule))
    member_counts = tuple(sorted(per_member.items()))
    rule_counts = tuple(sorted(per_rule.items()))
    population = len(live)

    breakdown = "; ".join(
        f"{member}: {count} of {population}" for member, count in member_counts
    )
    classes = ", ".join(f"{rule} ({count})" for rule, count in rule_counts)
    absent = (
        "every ratified member contributed at least one finding"
        if not non_contributing
        else (
            f"{len(non_contributing)} ratified member(s) contributed ZERO findings: "
            f"{', '.join(non_contributing)}"
        )
    )
    statement = (
        f"CONCENTRATION OF THE DENOMINATOR (AC3b, derived — not a threshold and not a "
        f"distribution requirement): the adjudicated population is {population} "
        f"finding(s) drawn from {len(contributing)} of {len(ratified)} ratified member(s) "
        f"[{breakdown}], across {len(rule_classes)} distinct rule class(es) [{classes}]. "
        f"{absent}. Protocol §5's N >= 5 is satisfied by MEMBER COUNT, so the N that gates "
        f"and the N that contributes are different numbers and a bare precision figure "
        f"would overstate the breadth of what was measured. This is DISCLOSED, never "
        f"corrected: narrowing the corpus, dropping a member or re-weighting one to move "
        f"the ratio is the threshold change protocol §5 and Story 13.3 / AC5 forbid."
    )
    return ConcentrationDisclosure(
        ratified_member_ids=ratified,
        contributing_member_ids=contributing,
        non_contributing_member_ids=non_contributing,
        per_member_finding_counts=member_counts,
        rule_class_ids=rule_classes,
        per_rule_class_finding_counts=rule_counts,
        adjudicated_population=population,
        statement=statement,
    )


@dataclass(frozen=True)
class ResidualCompletionBound:
    """What the ratio COULD become if every residual finding resolved the best way.

    Only meaningful when the run is non-exhaustive, and it exists so a ``BLOCKED`` outcome
    can be honest in both directions at once: the measurement is genuinely incomplete
    **and** the incompleteness may or may not be able to change the answer. Both facts are
    derived, in exact ``Fraction`` arithmetic through
    :func:`~argus.precision.replay_harness.precision_fraction` — the shared arithmetic,
    never a second one — and neither is a decision.

    It is **not** a licence to decide anyway. ``threshold_reachable=False`` does not turn
    ``BLOCKED`` into ``NOT_CLEARED``: the residual findings are a human's unfinished act
    and the record says so. It is recorded because a reader who is told only *"5 findings
    remain undecided"* cannot tell whether the outcome is genuinely open.
    """

    residual_count: int
    completed_denominator: int
    best_case_precision: Fraction | None
    best_case_ratio: str
    worst_case_precision: Fraction | None
    worst_case_ratio: str
    threshold: Fraction
    threshold_reachable: bool
    statement: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "residual_count": self.residual_count,
            "completed_denominator": self.completed_denominator,
            "best_case_precision": self.best_case_precision,
            "best_case_ratio": self.best_case_ratio,
            "worst_case_precision": self.worst_case_precision,
            "worst_case_ratio": self.worst_case_ratio,
            "threshold": self.threshold,
            "threshold_reachable": self.threshold_reachable,
            "statement": self.statement,
        }


def derive_residual_completion_bound(
    *,
    total_tp: int,
    total_fp: int,
    residual_count: int,
    threshold: Fraction = PRECISION_GATE_THRESHOLD,
) -> ResidualCompletionBound:
    """Bound the ratio over EVERY admissible completion of the residual (exact ``Fraction``).

    Best case: every residual finding resolves ``TP``. Worst case: every one resolves
    ``FP``. Both denominators include the residual, because a resolved ``BORDERLINE``
    enters the ratio on one side or the other — that is what §4's ladder terminating
    means.

    ``threshold_reachable`` is the exact-``Fraction`` comparison ``best_case >=
    threshold``. No float, no rounding, no percentage literal (AR4): the whole reason this
    project holds the threshold as ``Fraction(4, 5)`` is that a float comparison at the
    boundary answers a question nobody asked.
    """
    if residual_count < 0 or total_tp < 0 or total_fp < 0:
        raise ValueError(
            f"negative counts are not a completion bound: tp={total_tp}, fp={total_fp}, "
            f"residual={residual_count}"
        )
    best = precision_fraction(total_tp + residual_count, total_fp)
    worst = precision_fraction(total_tp, total_fp + residual_count)
    reachable = best is not None and best >= threshold
    # ``Fraction`` reduces, so a best/worst case of 0/31 renders "0/1" — exact, and easy to
    # misread as a denominator of one on the artifact that publishes the externalization
    # gate. The completed denominator is therefore named beside every ratio.
    completed = total_tp + total_fp + residual_count
    if residual_count == 0:
        statement = (
            "no residual: every emitted finding carries a live TP/FP disposition, so the "
            "ratio has no admissible completion other than itself."
        )
    elif best is None:
        statement = (
            f"{residual_count} residual finding(s) and an EMPTY denominator: no completion "
            f"of the residual produces a ratio at all, because nothing has entered TP+FP."
        )
    elif reachable:
        statement = (
            f"{residual_count} residual finding(s) remain, over a completed denominator of "
            f"{completed}. The outcome is GENUINELY OPEN: resolving every residual as TP "
            f"would give {ratio_string(best)} >= the {ratio_string(threshold)} threshold, "
            f"while resolving every one as FP would give {ratio_string(worst)}. The gate's "
            f"answer therefore depends on judgements that have not been made, which is "
            f"exactly why no §5 decision is recorded here."
        )
    else:
        statement = (
            f"{residual_count} residual finding(s) remain, and NO completion of them "
            f"reaches the threshold over the completed denominator of {completed}: "
            f"resolving EVERY residual as TP — the most favourable admissible outcome — "
            f"gives {ratio_string(best)}, still below {ratio_string(threshold)} (the least "
            f"favourable gives {ratio_string(worst)}). Recorded as a derived BOUND, NOT as "
            f"a decision: the residual is a human's unfinished act under protocol §4's "
            f"ladder, and an incomplete measurement stays an incomplete measurement however "
            f"its arithmetic is trending. A shortfall and an absent judgement are different "
            f"claims, and only the shortfall is a §5 result."
        )
    return ResidualCompletionBound(
        residual_count=residual_count,
        completed_denominator=completed,
        best_case_precision=best,
        best_case_ratio=ratio_string(best),
        worst_case_precision=worst,
        worst_case_ratio=ratio_string(worst),
        threshold=threshold,
        threshold_reachable=reachable,
        statement=statement,
    )
