"""Story 16.1 — protocol §5's BREADTH condition: a denominator drawn from one repository.

Verification area ``TC-ArgusAgent-PRECISION-001-82``.. (``tests/test_gate_breadth.py``).
Drivers: `precision-validation-protocol.md` §5 as amended **2026-08-20** (the amendment is
a dated block **under the existing V1.3** — the change-log head did NOT move, by operator
decision, because the committed record carries 31 human judgements made under V1.3 and
re-stamping them would re-interpret judgements nobody re-made); the 2026-08-20 sprint
change proposal §4.3(1); **AR4** (exact arithmetic, never a float); **AR7** (reuse, never
fork); **AR8** (pure — no I/O, no clock, no network); **AR10** (typed failures);
**NFR-M1**; **DF-9-2-A** (no module-level repository-only path — there is not one below,
and there cannot be: every input arrives as an argument).

What this module is
-------------------
:mod:`argus.precision.gate_disclosure` already DERIVES what the denominator is made of —
contributing members, per-member counts, distinct rule classes — and says so in writing:
*"derived — not a threshold and not a distribution requirement"*. That sentence was
correct and it was inert. **A gate could clear on a denominator drawn from a single
repository, and the record would disclose it in a paragraph a reader is free to skip.**

This module turns ONE arm of that disclosure into a §5 condition the gate must satisfy:
the precision ratio is evaluable only over a population that drew findings from at least a
**derived** number of distinct contributing members. Nothing here recounts anything —
:func:`assess_breadth` reads the counts off the SAME
:class:`~argus.precision.gate_disclosure.ConcentrationDisclosure` instance the decision
publishes, so the threshold and the disclosure cannot disagree. A second count would be a
second thing that can drift, and the drift would be invisible.

ONE ARM, NOT TWO — and the missing arm is a recorded measurement, not an oversight
--------------------------------------------------------------------------------
An honest breadth condition has two arms: *not one repository* and *not one rule*. **Only
the member arm lands here**, by operator decision (XAgent007, Engineering Lead,
2026-08-20), on a measurement reproduced by two independent instruments:

* ``verdict_eligible`` is ``depth_supported is not None``
  (``replay_harness.finding_match_key``). An AST walk of **all seven** ``build_recording``
  call sites in ``argus/**`` finds exactly **one** that passes a non-``None`` depth —
  ``argus/detectors/vacuous_test.py:1067`` — and there the depth and
  ``rule_id = RULE_AST`` are governed by the same ``corroborated`` boolean, so a
  verdict-eligible finding is bound to ``"vacuous_test_ast"`` by construction.
* the only other route to a depth is ``prosecutor._promote``, gated on
  ``recording_id in sign_offs``; the single production ``prosecute()`` call site
  (``argus/pipeline.py:535``) supplies no ``sign_offs`` at all, so the branch is
  unreachable on the corpus-audit path.
* counted over both committed adjudication sets: 2026-08-16, 6 rule classes emitted and
  **1** verdict-eligible; 2026-08-18, 5 emitted and **0**.

**Maximum achievable distinct verdict-eligible rule-class count = 1.** So a rule-class
floor of ``>= 2`` would not be a strengthening — it would be a **shutdown**, making
``CLEARED`` unreachable by construction with the shipped detector set; and a floor of ``1``
could not fail for any admissible input, which
:data:`~argus.precision.gate_decision.CONDITION_VERDICTS` already names in this codebase's
own words: *"A §5 condition that cannot fail is not a threshold."* Neither landed. The arm
is filed on the deferred-work ledger with that measurement, and **no rule-class threshold
is written anywhere in this module** — the count is still DISCLOSED, in
:attr:`BreadthAssessment.distinct_rule_class_count` and in the ``measured`` sentence, so
the next reader sees the number the condition deliberately does not gate.

The floor is DERIVED from the ONE locked quantity, never typed
--------------------------------------------------------------
:func:`contributing_member_floor` is ``(VALIDATION_SET_FLOOR_N + 1) // 2`` — *at least half
the members that satisfy §5's own floor, rounded up, must actually have contributed*. At the
locked floor of 5 that is **3**, a strict majority; the general form is stated as "half,
rounded up" because the two coincide only at an odd floor, and a derivation that overstates
what it computes is the ``DF-9-2-B`` false-subject shape applied to a threshold. It is
expressed as a FUNCTION of the locked floor rather than as the integer it currently
evaluates to (AR7 / Story 13.1 / DN-3: one floor, resolved, never re-typed), and the floor
arrives as an ARGUMENT — the same ``floor_n`` the decision already carries — so this module
never resolves the repository-only manifest and never ships a second ``N``.

Why not the obvious alternatives, each rejected with its reason:

* **the value the population already has** — a threshold met by the very population that
  motivated it is not a threshold, it is a description;
* **``N`` itself** (the ratified member count) — one clean member that legitimately emits
  nothing would block the gate forever, and it is a distribution requirement wearing a
  threshold's hat, which §5 and Story 13.3 / AC5 forbid;
* **a proportion of the ratified population** — unstable under a §6 R2 ratification: the
  same expression would demand 3 today and 12 after, so the constant would move as a SIDE
  EFFECT of an operator act rather than by decision;
* **``VALIDATION_SET_FLOOR_N`` itself** — identical today, and it forks the MEANING of the
  one floor: §5's ``N >= 5`` counts members that EXIST, this counts members that
  CONTRIBUTED.

Below the floor the outcome is UNEVALUABLE, and no terminal state is invented
-----------------------------------------------------------------------------
The breadth condition's OWN verdict is ``MET`` or ``FAILED`` — it *was* evaluated over a
named corpus, and ``UNEVALUABLE`` means a §4 precondition did not hold, which is a
different claim. What becomes ``UNEVALUABLE`` is protocol §5's **precision** condition,
because a ratio over a denominator this narrow is not a measurement of the tool; and the
gate outcome is ``BLOCKED`` with a countable closure path. ``GATE_OUTCOMES`` stays closed
at three and ``CONDITION_VERDICTS`` at four: the states this needs already exist.

The breadth condition's own verdict is never ``UNEVALUABLE`` and that is a distinction with
teeth: recording it so would tell a reader the breadth of the population was *unknown*,
when in fact it was counted and found wanting. A measured result and an unobservable one
are different claims, and this project's dominant defect class is exactly the surface that
cannot tell them apart. ``gate_decision._breadth_condition`` builds the ``ConditionResult``
because ``ConditionResult`` lives there and the import would otherwise be circular — one
direction only, ``gate_decision`` → ``gate_breadth`` (DN-16-1-3).

The two surfaces may not disagree (``DF-9-2-B``)
------------------------------------------------
:func:`effective_precision_gate_status` renders the status sentence through the EXISTING
:func:`~argus.precision.replay_harness.precision_gate_status_for` — the same object, never
a second one (AR7) — so a payload can never carry ``precision.evaluable = True`` beside a
§5 precision verdict of ``UNEVALUABLE``. That shape is a true status carrying a false
subject, on the surface that publishes the externalization gate.

**Direction of travel, stated once:** every change this module makes to the gate makes
clearing **HARDER**. It touches neither the ``>= 80%`` ``Fraction``, nor
``VALIDATION_SET_FLOOR_N``, nor the ratified member list, nor ``MANIFEST_FIELDS``.
"""

from __future__ import annotations

from dataclasses import dataclass

from argus.precision.adjudication import AdjudicatedPrecision
from argus.precision.gate_disclosure import ConcentrationDisclosure
from argus.precision.replay_harness import precision_gate_status_for

__all__ = [
    "ADJUDICATED_POPULATION_LABEL",
    "BREADTH_CONDITION_ID",
    "BREADTH_MEMBER_FLOOR_DERIVATION",
    "BreadthAssessment",
    "VacuousBreadthFloor",
    "assess_breadth",
    "breadth_blocked_reason",
    "breadth_closure_path",
    "contributing_member_floor",
    "effective_precision_gate_status",
]


class VacuousBreadthFloor(ValueError):
    """Raised when the locked floor a breadth floor is derived FROM is itself meaningless.

    AR10: the message says what a reader must do. A floor derived from a non-positive
    ``VALIDATION_SET_FLOOR_N`` would evaluate to ``0`` or less and the condition would hold
    for every admissible population — the ``NOT_APPLICABLE`` shape this codebase already
    refuses in §5's clean-repo row (*"a condition that cannot fail is not a threshold"*).
    """


#: §5's new condition id, named ONCE. Used by :data:`SECTION_5_CONDITIONS`, by the builder
#: in :mod:`argus.precision.gate_decision`, and by the by-id lookup — so three literals that
#: could drift apart are one constant, exactly as ``RECORDED_CLEARED_CONDITION_ID`` is.
BREADTH_CONDITION_ID = "denominator-breadth-contributing-members"

#: The DERIVATION, in one place, so the prose the record publishes and the arithmetic the
#: gate runs are the same object rather than two statements that can disagree (``DF-8-5-C``:
#: a hand-written number in an artifact about the very gate this epic measures).
BREADTH_MEMBER_FLOOR_DERIVATION = (
    "(VALIDATION_SET_FLOOR_N + 1) // 2 — i.e. ceil(N_floor / 2): at least HALF the members "
    "that satisfy protocol §5's own N floor, ROUNDED UP, must actually have CONTRIBUTED a "
    "finding to the ratio. At the locked floor of 5 that is 3, which is a strict majority; "
    "the general form is 'half, rounded up', and it is stated that way rather than as "
    "'a strict majority' because the two coincide only at an ODD floor. Expressed as a "
    "function of the ONE locked floor (Story 13.1 / DN-3), never re-typed as the integer it "
    "currently evaluates to, so it cannot fork from the floor it derives from and cannot "
    "move as a side effect of a §6 R2 ratification"
)

#: The NOUN ``n`` is counted in on the adjudicated-precision surface. It MUST be the same
#: noun :func:`~argus.precision.adjudication.fold_adjudicated_precision` renders, because
#: :func:`effective_precision_gate_status` re-renders the SAME population's status through
#: the SAME function and a second noun would be a second claim about one number.
#: ``TC-ArgusAgent-PRECISION-001-85`` asserts the two agree over the live fold, so this is a
#: mechanically-checked agreement rather than a copied literal.
ADJUDICATED_POPULATION_LABEL = "eligible validation-set repositories"


def contributing_member_floor(validation_set_floor_n: int) -> int:
    """The minimum number of DISTINCT CONTRIBUTING members — derived, never typed.

    ``(validation_set_floor_n + 1) // 2``, i.e. ``ceil(n / 2)``: at least half the members
    that satisfy protocol §5's own ``N >= VALIDATION_SET_FLOOR_N`` floor, rounded up, must
    actually have contributed at least one finding to the ratio. At the locked floor of 5
    that is **3** — a strict majority — but the general form is *"half, rounded up"*, and
    saying so is not pedantry: the two coincide only at an odd floor, and a docstring that
    claimed strict majority would be a derivation describing something it does not compute.
    Integer arithmetic throughout (AR4 — a float would answer a different question at the
    boundary).

    **Why a function of the floor and not a constant.** §5's ``N`` counts members that
    EXIST; this counts members that CONTRIBUTED. *The N that gates and the N that
    contributes are different numbers* — that sentence is already on the committed gate
    record — and this is the first thing in the tree that makes the second number binding.
    Deriving it from the locked floor rather than from the ratified population is what
    keeps it stable under a §6 R2 ratification: a proportion of the population would demand
    3 today and 12 after ratifying the 14 bench candidates, moving a §5 threshold as a side
    effect of an operator act nobody intended as a threshold change.

    PURE (AR8): integer arithmetic over an argument. No I/O, no clock, no manifest.

    Args:
        validation_set_floor_n: protocol §5's ONE locked floor, RESOLVED by the caller
            (``registry_module().VALIDATION_SET_FLOOR_N``, reached through the decision's
            own ``floor_n``). It is never resolved here — ``DF-9-2-A``.

    Raises:
        VacuousBreadthFloor: *validation_set_floor_n* is below 1, which would derive a
            floor no population could fail.
    """
    if validation_set_floor_n < 1:
        raise VacuousBreadthFloor(
            f"a contributing-member floor cannot be derived from "
            f"VALIDATION_SET_FLOOR_N = {validation_set_floor_n}: the derived floor would be "
            f"at or below zero and the breadth condition would hold for every admissible "
            f"population, which is the 'condition that cannot fail' protocol §5 already "
            f"refuses in its clean-repo row. Pass the resolved "
            f"registry_module().VALIDATION_SET_FLOOR_N; do not default it."
        )
    return (validation_set_floor_n + 1) // 2


@dataclass(frozen=True)
class BreadthAssessment:
    """Protocol §5's breadth arm, MEASURED — with the sentences the record publishes.

    Every count here is READ from the concentration disclosure the decision publishes, not
    recounted (AR7). :attr:`distinct_rule_class_count` is carried and DISCLOSED and is
    deliberately **not** gated — see this module's docstring for the measurement that
    decided that, and the ledger entry that keeps it visible.
    """

    contributing_member_count: int
    contributing_member_floor: int
    ratified_member_count: int
    distinct_rule_class_count: int
    adjudicated_population: int
    population_source: str
    holds: bool
    requirement: str
    measured: str
    what_would_close_it: str
    unevaluable_reason: str

    def to_payload(self) -> dict[str, object]:
        """The canonical mapping — serialized through ``argus.store.canonical`` upstream."""
        return {
            "condition_id": BREADTH_CONDITION_ID,
            "contributing_member_count": self.contributing_member_count,
            "contributing_member_floor": self.contributing_member_floor,
            "contributing_member_floor_derivation": BREADTH_MEMBER_FLOOR_DERIVATION,
            "ratified_member_count": self.ratified_member_count,
            "distinct_rule_class_count": self.distinct_rule_class_count,
            "rule_class_arm_landed": False,
            "adjudicated_population": self.adjudicated_population,
            "population_source": self.population_source,
            "holds": self.holds,
            "requirement": self.requirement,
            "measured": self.measured,
            "what_would_close_it": self.what_would_close_it,
            "unevaluable_reason": self.unevaluable_reason,
        }


def assess_breadth(
    concentration: ConcentrationDisclosure,
    *,
    validation_set_floor_n: int,
    population_source: str,
) -> BreadthAssessment:
    """Evaluate §5's breadth arm over the concentration the decision ALREADY published.

    *concentration* is the very instance the decision serializes, so the threshold and the
    disclosure are computed from one set of counts. Recounting them here would create a
    second answer to one question, and a disagreement between a disclosure and the
    threshold derived from it is invisible to every reader of either.

    *population_source* names WHICH population was counted (AC3.4). It matters and it is
    not cosmetic: the concentration is derived from the committed adjudication record's
    LIVE rows, while the most recent adjudication set's EMITTED blocking population may be
    a different — even empty — set. That divergence predates this condition and is out of
    scope to fix; what is in scope is that the sentence never lets a reader mistake one for
    the other.

    PURE (AR8): reads a frozen dataclass and returns a frozen dataclass.
    """
    floor = contributing_member_floor(validation_set_floor_n)
    contributing = concentration.contributing_member_count
    holds = contributing >= floor
    short_by = max(0, floor - contributing)

    requirement = (
        f"protocol §5 as amended 2026-08-20 (Story 16.1; sprint change proposal "
        f"2026-08-20 §4.3(1)): the precision ratio is EVALUABLE only over a population "
        f"drawn from at least {floor} DISTINCT CONTRIBUTING member(s) of the ratified "
        f"repository validation set — derived as {BREADTH_MEMBER_FLOOR_DERIVATION}. A "
        f"score drawn from one repository is not a score. This condition makes clearing "
        f"HARDER and can never make it easier"
    )
    measured = (
        f"breadth = {contributing} distinct CONTRIBUTING member(s) of "
        f"{concentration.ratified_member_count} ratified, against a floor of {floor}; "
        f"counted over the {concentration.adjudicated_population} LIVE row(s) of "
        f"{population_source} — NOT over the emitted blocking population of the most "
        f"recent adjudication set, which is a different population and may be empty. The "
        f"same population spans {concentration.distinct_rule_class_count} distinct rule "
        f"class(es), which is DISCLOSED and deliberately NOT gated: exactly one rule class "
        f"can reach verdict-eligibility with the shipped detector set, so a rule-class "
        f"floor of >= 2 would be a shutdown rather than a strengthening and a floor of 1 "
        f"could not fail. "
        + (
            "The member floor is MET."
            if holds
            else f"The member floor is NOT met — short by {short_by} member(s)."
        )
    )
    what_would_close_it = (
        (
            "already met; it re-opens the moment the adjudicated population narrows back "
            "below the floor — by a superseding judgement, a withdrawn member, or a "
            "re-measurement that emits from fewer members"
        )
        if holds
        else (
            f"{short_by} further ratified member(s) must each contribute at least ONE "
            f"adjudicated finding to the population, taking the contributing count from "
            f"{contributing} to {floor}. NOT closable by narrowing the corpus, by dropping "
            f"a non-contributing member, or by re-weighting one — protocol §5 and Story "
            f"13.3 / AC5 forbid every one of those, and each would move the ratio rather "
            f"than broaden the evidence. The honest closure is MORE members contributing "
            f"evidence, never fewer members counted"
        )
    )
    unevaluable_reason = (
        f"DENOMINATOR TOO NARROW — the adjudicated population is drawn from "
        f"{contributing} of {concentration.ratified_member_count} ratified member(s), "
        f"below protocol §5's breadth floor of {floor} ({BREADTH_MEMBER_FLOOR_DERIVATION}), "
        f"so the ratio measures those {contributing} repositor(y/ies) and not the tool"
    )
    return BreadthAssessment(
        contributing_member_count=contributing,
        contributing_member_floor=floor,
        ratified_member_count=concentration.ratified_member_count,
        distinct_rule_class_count=concentration.distinct_rule_class_count,
        adjudicated_population=concentration.adjudicated_population,
        population_source=population_source,
        holds=holds,
        requirement=requirement,
        measured=measured,
        what_would_close_it=what_would_close_it,
        unevaluable_reason=unevaluable_reason,
    )


def effective_precision_gate_status(
    *,
    fold: AdjudicatedPrecision,
    breadth: BreadthAssessment,
    protocol_path: str,
) -> str:
    """The gate-status sentence for the EFFECTIVE evaluability — one object, never two.

    The fold's own ``gate_status`` answers *"was a ratio computable?"*. After this
    amendment the gate additionally requires the ratio to have been computed over a
    population broad enough to mean something, so the surface that PUBLISHES the gate must
    report ``fold.evaluable AND breadth.holds`` — anything else lets
    ``precision.evaluable = True`` sit beside a §5 precision verdict of ``UNEVALUABLE``,
    which is the ``DF-9-2-B`` false-subject class on the externalization gate itself.

    **The fold is NOT forked** (DN-16-1-1). ``fold_adjudicated_precision`` and
    ``AdjudicatedPrecision`` are byte-untouched: threading a breadth argument into the fold
    would widen a signature shared with the cartridge path, where breadth is meaningless.
    The sentence is re-rendered through the SAME
    :func:`~argus.precision.replay_harness.precision_gate_status_for` the fold used, with
    the breadth reason supplied — never through a second status function (AR7).

    When breadth does not change the answer the fold's OWN string is returned BYTE-FOR-BYTE
    rather than re-rendered, so this amendment is provably inert on a population it does not
    bind (NFR-P1 byte-stability of the precision surface).

    PURE (AR8).
    """
    if fold.evaluable == (fold.evaluable and breadth.holds):
        return fold.gate_status
    return precision_gate_status_for(
        precision=fold.precision,
        n=fold.n,
        provisional=fold.provisional,
        protocol_path=protocol_path,
        floor_n=fold.floor_n,
        population_label=ADJUDICATED_POPULATION_LABEL,
        evaluable=False,
        unevaluable_reason=breadth.unevaluable_reason,
    )


def breadth_blocked_reason(breadth: BreadthAssessment) -> str:
    """The ``outcome_reason`` a decision BLOCKED on breadth publishes (Story 16.1 / AC3.1).

    It lives here rather than inline in :func:`~argus.precision.gate_decision.decide_gate`
    for the reason DN-16-1-3 gives: the constants, the predicate and **the measured and
    closure sentences** are this module's subject, and ``gate_decision.py`` builds the
    ``ConditionResult`` because ``ConditionResult`` lives there. One direction only.

    **Why BLOCKED and not NOT_CLEARED, said once in the sentence itself.** ``NOT_CLEARED``
    may be recorded only when the measurement RAN, and §5's precision condition here did not
    produce a measurement of the tool — it produced a ratio over a handful of repositories.
    ``GATE_OUTCOMES`` stays CLOSED at three; no terminal state is invented.

    PURE (AR8).
    """
    return (
        f"the precision ratio is NOT EVALUABLE as a statement about the tool: protocol "
        f"§5's BREADTH condition, as amended 2026-08-20 (Story 16.1), does not hold. "
        f"{breadth.measured} A ratio computed over a denominator this narrow measures those "
        f"repositories, not Argus — and a bare precision figure would overstate the breadth "
        f"of what was measured, which the concentration disclosure has said in writing since "
        f"2026-08-17 without being able to stop it. This is NOT a shortfall and NOT a failed "
        f"measurement: the amendment was made BEFORE the measurement it governs, and it can "
        f"only make clearing harder."
    )


def breadth_closure_path(breadth: BreadthAssessment) -> tuple[str, ...]:
    """What it would take, in COUNTABLE terms — a BLOCKED decision with no closure path raises.

    The third leg is the one that matters and is stated as a refusal rather than left to a
    reader's restraint: the floor may not be lowered to fit the population that failed it.
    A threshold moved after seeing the population it failed is corpus-shopping with extra
    steps, which protocol §5 and Story 13.3 / AC5 forbid in exactly those terms.

    PURE (AR8).
    """
    return (
        breadth.what_would_close_it,
        "re-run scripts/build_gate_decision.py so the record carries the broadened "
        "population, and re-run this decision",
        "NOT closable by amending the floor: a threshold moved after seeing the population "
        "it failed is corpus-shopping with extra steps (protocol §5; Story 13.3 / AC5)",
    )
