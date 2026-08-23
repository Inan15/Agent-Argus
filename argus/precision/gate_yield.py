"""Story 16.3 — protocol §5's YIELD condition: a detector that finds nothing has not passed.

Verification area ``TC-ArgusAgent-PRECISION-001-95``.. (``tests/test_gate_yield.py``).
Drivers: `precision-validation-protocol.md` §5 as amended **2026-08-20** (a THIRD dated
block **under the existing V1.3** — the change-log head did NOT move, by operator decision,
because the committed record carries 31 human judgements made under V1.3 and re-stamping
them would re-interpret judgements nobody re-made); the 2026-08-20 sprint change proposal
§4.3(3); **AR4** (exact arithmetic, never a float); **AR7** (reuse, never fork); **AR8**
(pure — no I/O, no clock, no network, no manifest resolution); **AR10** (typed failures);
**NFR-M1**; **NFR-P1**; **DF-9-2-A** (no module-level repository-only path — there is not
one below, and there cannot be: every input arrives as an argument).

What this module is
-------------------
Story 13.2's ``UNEVALUABLE`` closed the hole for an **empty** denominator and Story 13.5
made *"the corpus was read and nothing was promoted"* expressible. **Neither closes the
TINY one**, and that is a measurement rather than a worry: driven through the shipped
``decide_gate`` at HEAD ``1ecf618``, a population of **exactly three findings, one per
sealed member, all adjudicated TP** returned ``CLEARED`` at precision ``1/1`` with all six
§5 conditions ``MET`` and an outcome sentence reading *"Clearing authorises ATTESTED
externalization."* Three findings. All correct. Cleared.

This module puts a floor under the SIZE of the verdict-eligible population the precision
ratio is computed over. Nothing here recounts anything: :func:`assess_yield` reads its one
count off the SAME :class:`~argus.precision.gate_disclosure.ConcentrationDisclosure`
instance the decision publishes and the breadth and seal arms read, so the threshold and
the disclosure cannot disagree. A second count would be a second thing that can drift, and
the drift would be invisible.

The floor is DERIVED from the ONE locked threshold, and it is a property of the RATIO
------------------------------------------------------------------------------------
``PRECISION_GATE_THRESHOLD`` is ``Fraction(4, 5)``. At a denominator ``d``, the largest
number of false positives a population can carry and still clear is
``max{ k : (d − k)/d >= 4/5 }``. Executed over the shipped threshold:

===  ==========================  ==================================
``d``  FPs affordable at >= 80%    what ">= 80%" actually demands
===  ==========================  ==================================
1    0                           100%
2    0                           100%
3    0                           100%
4    0                           100%
5    **1**                       **80%**
6    1                           80%
===  ==========================  ==================================

**Below a denominator of five, the >= 80% gate is silently a 100% gate.** A detector that
emits three findings and gets all three right has not cleared an 80% bar — it has cleared a
bar it never faced, and the record publishes the figure as though it had. The floor is the
smallest denominator at which the threshold means the thing it is written as, and
:func:`verdict_eligible_population_floor` computes exactly that.

⛔ **The GENERAL form, and why it is not ``threshold.denominator``.** For a threshold
``T = p/q`` in lowest terms, ``(d−1)/d >= p/q`` iff ``d >= q/(q−p)``, so the floor is
``ceil(q / (q − p))``. It equals ``q`` **only when ``q − p == 1``**, and it DIVERGES
otherwise: verified against brute force over eight thresholds, at ``5/7`` it is 4 and at
``7/9`` it is 5 — not 7 and 9. Writing ``threshold.denominator`` would be correct by
coincidence at exactly the one threshold shipped, and would be a derivation describing
something it does not compute. That is Story 16.1's *"strict majority"* correction —
``(N+1)//2`` is a strict majority only at an ODD floor — repeated one story later, and it is
pre-applied here rather than caught in review.

⚠️ **A COINCIDENCE, DISCLOSED rather than leaned on (DN-16-3-2).**
``VALIDATION_SET_FLOOR_N`` is **also 5**. The two are independent locked quantities that
happen to be equal today: one counts members that must EXIST, this is the smallest
DENOMINATOR at which a ratio threshold is the threshold it is written as. Deriving this
floor from ``VALIDATION_SET_FLOOR_N`` is **REJECTED** — it would fork the meaning of that
floor a THIRD time (``N`` counts members that exist; ``contributing_member_floor`` counts
members that CONTRIBUTED; this counts FINDINGS) and would move a §5 threshold as a side
effect of a change to the corpus floor. DN-3's one-floor rule is about not forking one
quantity, not about collapsing three different ones into it. For the same reason this floor
is **not resolved from** ``contributing_member_floor`` / ``sealed_member_floor`` and does
not fork them: those two are one quantity resolved through one function (16.1, resolved by
16.2), and both are left byte-unchanged by this story.

THE VACUITY CHECK, executed — and it rules out the obvious numbers
------------------------------------------------------------------
*"A §5 condition that cannot fail is not a threshold"* is this codebase's own sentence, in
:data:`~argus.precision.gate_conditions.CONDITION_VERDICTS`. Two independent tests:

1. **Against any admissible population.** ``derive_concentration`` RAISES
   ``VacuousDisclosureError`` on an empty population, so ``adjudicated_population >= 1``
   for every population the decision accepts. **A yield floor of 1 could not fail** —
   16.1's rule-class arm died on exactly this.
2. **Against the populations that can REACH the branch.** Measured on this tree: the
   smallest population passing BOTH breadth and seal is **3**. So a floor of **2 or 3 can
   never fire** — every population it would block is already blocked upstream, and the
   dispatch branch would be an unreachable guard. **The floor must exceed 3.** A floor of 4
   fires on exactly one population size; the derived floor of **5 fires on sizes 3 and 4**,
   which is precisely the pair measured as wrongly ``CLEARED`` today.

The derivation and the vacuity floor agree from two directions that share no reasoning.
That agreement is why this number is defensible rather than convenient.

⛔ IS THIS RECALL BY ANOTHER NAME? — the OI1 question, answered by WHERE THE NUMBER COMES FROM
----------------------------------------------------------------------------------------------
Recall is diagnostic-only by the **OI1 lock** (protocol §5's Recall row, and §7). A floor on
a population size is adjacent to recall, so the question is not rhetorical and the answer
turns entirely on the number's SOURCE.

``recall = TP / (TP + FN)``. It requires ``FN`` — defects that exist and were missed. Over
the repository corpus ``FN`` is unknowable: protocol V1.1 records that *"a real repository
has no golden key"*, and ``replay_harness`` sources its ``FN`` term from cartridge golden
keys, so over the gating corpus recall degenerates to ``1/1`` vacuously.

**The condition this module lands has no ``FN`` term, no estimate of one, and no reference
to how many defects the bench contains.** Its two inputs are (i) the count of
verdict-eligible findings that reached adjudication, read off the disclosure the decision
already publishes, and (ii) the gate threshold. It says: *the denominator must be large
enough that the >= 80% threshold is a >= 80% threshold.* **That is a statement about the
RESOLUTION of the measurement that was taken — not a claim about what was missed.** It is
precision-side arithmetic end to end and it does not re-open OI1.

⛔ **The framing that WOULD make it recall, named so it is refused rather than stumbled
into.** *"The sealed partition holds 431 co-occurrence files, so expect at least X"*
estimates ``FN`` from a text proxy and gates on it. That IS recall by another name, it
re-opens OI1, and it is an **operator escalation** rather than a story decision.
``scripts/candidate_selection.py`` says so in its own words: co-occurrence is *"a TEXT
PROXY … a proxy for the DEFINITION, never for the VERDICT."* This floor comes from
``PRECISION_GATE_THRESHOLD`` and from nowhere else, and
``tests/test_gate_yield.py::TC-ArgusAgent-PRECISION-001-99`` makes that **mechanically
checkable** by walking this module's own AST: no recall symbol is imported, no ``FN`` term
is named, and no co-occurrence / bench-content quantity is referenced. Prose may NAME what
it refuses — that is what this docstring is doing — so the guard walks names and imports,
never string constants.

Below the floor the outcome is UNEVALUABLE, and no terminal state is invented
-----------------------------------------------------------------------------
The yield condition's OWN verdict is ``MET`` or ``FAILED`` and never ``UNEVALUABLE``
(DN-16-3-4): the population *was* counted. ``UNEVALUABLE`` would tell a reader its size was
unknown, which is a different and false claim, and this project's dominant defect class is
exactly the surface that cannot tell those apart. What becomes ``UNEVALUABLE`` is protocol
§5's **precision** condition; the gate outcome is ``BLOCKED`` with a countable closure path.
``GATE_OUTCOMES`` stays closed at three and ``CONDITION_VERDICTS`` at four.
``gate_decision._yield_condition`` builds the ``ConditionResult`` because ``ConditionResult``
lives there and the import would otherwise be circular — one direction only (DN-16-1-3).

**Direction of travel, stated once and verified by execution:** every change this module
makes to the gate makes clearing **HARDER**. A population that returns ``CLEARED`` today at
sizes 3 and 4 returns ``BLOCKED`` after it; no population that failed before can pass
because of it. It touches neither the ``>= 80%`` ``Fraction``, nor ``VALIDATION_SET_FLOOR_N``,
nor the ratified member list, nor ``MANIFEST_FIELDS``, nor the sealed partition.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from argus.precision.adjudication import AdjudicatedPrecision
from argus.precision.gate_disclosure import ConcentrationDisclosure
from argus.precision.replay_harness import precision_gate_status_for, ratio_string

__all__ = [
    "YIELD_CONDITION_ID",
    "YIELD_FLOOR_DERIVATION",
    "YIELD_PROVENANCE_DISCLOSURE",
    "VacuousYieldFloor",
    "YieldAssessment",
    "assess_yield",
    "verdict_eligible_population_floor",
    "yield_blocked_reason",
    "yield_closure_path",
    "yielded_precision_gate_status",
]


class VacuousYieldFloor(ValueError):
    """Raised when the THRESHOLD a yield floor is derived FROM makes the floor meaningless.

    AR10: the message says what a reader must do. A threshold of ``1`` (or above) admits no
    false positive at ANY denominator, so ``q − p <= 0`` and ``ceil(q / (q − p))`` is
    undefined or negative. A floor derived from such a threshold would hold for every
    admissible population — the *"condition that cannot fail"* shape protocol §5 already
    refuses in its clean-repo row, and the shape 16.1's rule-class arm died on.
    """


#: §5's SEVENTH condition id, named ONCE — used by :data:`SECTION_5_CONDITIONS`, by the
#: builder in :mod:`argus.precision.gate_decision` and by the by-id lookup, so three literals
#: that could drift apart are one constant. The ``RECORDED_CLEARED_CONDITION_ID`` /
#: ``BREADTH_CONDITION_ID`` / ``SEAL_CONDITION_ID`` precedent.
YIELD_CONDITION_ID = "detector-yield-verdict-eligible-population-floor"

#: THE DERIVATION, in one place, so the prose the record publishes and the arithmetic the
#: gate runs are the same object rather than two statements that can disagree (``DF-8-5-C``:
#: a hand-written number in an artifact about the very gate this epic measures). The
#: ``BREADTH_MEMBER_FLOOR_DERIVATION`` / ``SEAL_RULE_DERIVATION`` precedent.
YIELD_FLOOR_DERIVATION = (
    "ceil(q / (q - p)) over PRECISION_GATE_THRESHOLD = p/q in lowest terms — the SMALLEST "
    "DENOMINATOR at which the threshold admits a single false positive, i.e. at which "
    "'>= 80%' is not silently '100%'. At a denominator d the largest affordable FP count is "
    "max{k : (d-k)/d >= p/q}, and that count is ZERO for every d below this floor: a "
    "detector emitting three findings and getting all three right has not cleared an 80% "
    "bar, it has cleared a bar it never faced. It is a property of the RATIO, not of the "
    "corpus: it carries no FN term, no estimate of one, and no quantity describing what the "
    "bench contains, so it is NOT a recall floor and does not re-open the OI1 lock. It "
    "equals q ONLY when q - p == 1 and diverges otherwise (at 5/7 it is 4, at 7/9 it is 5, "
    "verified against brute force), which is why it is expressed in the general form and "
    "NEVER as threshold.denominator — that spelling would be correct by coincidence at "
    "exactly the one threshold shipped. AT THE SHIPPED THRESHOLD OF 4/5 IT IS 5. "
    "⚠ COINCIDENCE, DISCLOSED: VALIDATION_SET_FLOOR_N is also 5 and this floor is NOT "
    "derived from it (DN-16-3-2) — one counts MEMBERS THAT EXIST, this counts FINDINGS, and "
    "coupling them would move a §5 threshold as a side effect of a corpus-floor change. It "
    "is likewise not resolved from contributing_member_floor / sealed_member_floor, which "
    "are one quantity (3) resolved through one function and are left byte-unchanged. "
    "VACUITY, measured from two directions that share no reasoning: derive_concentration "
    "raises on an empty population so a floor of 1 could not fail, and the smallest "
    "population passing both breadth and seal is 3 so a floor of 2 or 3 could never fire — "
    "the derived floor of 5 fires on exactly the sizes 3 and 4 that are wrongly CLEARED "
    "without it"
)

#: ⚠️ THE PRE-ROUND DISCLOSURE, owed to the operator BEFORE ``DF-13-5-A``'s ONE round is
#: spent rather than after. It is carried on the CONDITION, not left in story prose, because
#: a reader who sees this condition report ``MET`` over the committed population of 31 must
#: not conclude *"the detector currently yields 31"*.
#:
#: Every figure below is a count of DETECTOR OUTPUT over the RATIFIED gating corpus, read
#: from committed artifacts — never a quantity describing what the bench CONTAINS, which is
#: the framing that would make this condition recall (see this module's docstring). The
#: numbers are stated here rather than resolved because this module may not read a
#: repository-only path (AR8 / ``DF-9-2-A``); ``TC-ArgusAgent-PRECISION-001-100`` RE-DERIVES
#: every one of them from the committed sets and reddens if this string drifts, which is the
#: ``SEALED_PARTITION_TABLE`` treatment rather than a typed literal.
YIELD_PROVENANCE_DISCLOSURE = (
    "A POPULATION SIZE IS NOT A YIELD FORECAST. Counted out of the committed "
    "validation-corpus/adjudication-set-13-5.json (2026-08-18, post-Epic-14): the CORRECTED "
    "detector emitted 4284 finding(s) across all 5 ratified members and promoted 0 of them "
    "to verdict-eligible — 0 blocking. The only population that ever exceeded this floor was "
    "the 2026-08-16 set of 31, produced under the PRE-Epic-14 corroboration rule that Epic "
    "14 REFUTED, and the named human adjudicated those 31 as 0 TP / 26 FP / 5 BORDERLINE. A "
    "yield above this floor has been achieved exactly ONCE and was achieved entirely by "
    "false positives. The achievable yield over the SEALED partition is UNMEASURABLE without "
    "fetching third-party source, which is a protocol §6 R2 operator act no agent may take, "
    "so this is DISCLOSED as unmeasured and is NOT presented as impossible: unmeasured is "
    "not bounded-by-construction, and a search for a structural cap on promoted findings "
    "found none (the corroboration path emits one finding per flagged test function and "
    "admits no k). On the only evidence that exists the likely outcome of the ONE "
    "pre-registered round is BLOCKED on yield — which DF-13-5-A, answered 2026-08-17 BEFORE "
    "any number existed, already routes to option (b): the FR34 disclosure stands for V1.5 "
    "and the next attempt requires a materially better detector, NOT a bigger bench. This "
    "condition is therefore not a new hurdle; it is that stopping rule made arithmetic, "
    "because without it a round yielding THREE would route to CLEARED while a round yielding "
    "ZERO routes to option (b) — two destinations for a materially identical result"
)


def verdict_eligible_population_floor(threshold: Fraction) -> int:
    """The minimum VERDICT-ELIGIBLE population the ratio may be computed over — derived.

    ``ceil(q / (q − p))`` for ``threshold = p/q`` in lowest terms: the smallest denominator
    at which the threshold admits a single false positive, i.e. at which *">= 80%"* is not
    silently *"100%"*. See :data:`YIELD_FLOOR_DERIVATION` for the full statement, the
    rejected alternatives and the disclosed coincidence.

    ⛔ **Not ``threshold.denominator``.** That spelling agrees only when ``q − p == 1`` and
    is wrong at ``5/7`` (4, not 7) and ``7/9`` (5, not 9). A derivation that describes
    something it does not compute is the ``DF-9-2-B`` false-subject shape applied to a
    threshold, and it is the exact mistake Story 16.1 made and corrected one story earlier.

    **AR4 — exact integer arithmetic, never a float.** ``-(-q // (q - p))`` is integer
    ceiling division; ``math.ceil(q / (q - p))`` would evaluate a float quotient and answer a
    different question at the boundary, which is the whole subject of this condition.

    **Why a function of the threshold and not a constant.** The floor is a property of the
    RATIO. Typing ``5`` would fork it from the threshold it derives from, and the two could
    then move apart with nothing noticing — on the record that gates attested
    externalization. The threshold arrives as an ARGUMENT and is never resolved at module
    level (``AR8`` / ``DF-9-2-A``: this module ships in a wheel).

    PURE (AR8): integer arithmetic over an argument. No I/O, no clock, no manifest.

    Args:
        threshold: protocol §5's ONE locked gate threshold, RESOLVED by the caller
            (``replay_harness.PRECISION_GATE_THRESHOLD``, reached through the decision).
            ``Fraction`` normalises to lowest terms at construction, so ``p`` and ``q`` are
            read off it directly.

    Raises:
        VacuousYieldFloor: ``q − p <= 0`` — the threshold admits no false positive at any
            denominator, so no floor derived from it could ever fail.
    """
    p, q = threshold.numerator, threshold.denominator
    if q - p <= 0:
        raise VacuousYieldFloor(
            f"a verdict-eligible population floor cannot be derived from a gate threshold "
            f"of {ratio_string(threshold)}: it admits ZERO false positives at EVERY "
            f"denominator (q - p = {q - p}), so ceil(q / (q - p)) is undefined and any "
            f"floor derived from it would hold for every admissible population — the "
            f"'condition that cannot fail' protocol §5 already refuses in its clean-repo "
            f"row. Pass the resolved replay_harness.PRECISION_GATE_THRESHOLD, which is "
            f"Fraction(4, 5); do not default it and do not amend it to make this call "
            f"succeed."
        )
    return -(-q // (q - p))


@dataclass(frozen=True)
class YieldAssessment:
    """Protocol §5's yield arm, MEASURED — with the sentences the record publishes.

    The one count is READ from the concentration disclosure the decision publishes, never
    recounted (AR7, AC1.5). It is the SAME instance the breadth and seal arms read, so the
    three conditions and the disclosure cannot disagree about how big the population was.
    """

    adjudicated_population: int
    yield_floor: int
    threshold_ratio: str
    population_source: str
    holds: bool
    requirement: str
    measured: str
    what_would_close_it: str
    unevaluable_reason: str

    @property
    def short_by(self) -> int:
        """How many further verdict-eligible findings the population is short of the floor."""
        return max(0, self.yield_floor - self.adjudicated_population)

    def to_payload(self) -> dict[str, object]:
        """The canonical mapping — serialized through ``argus.store.canonical`` upstream."""
        return {
            "condition_id": YIELD_CONDITION_ID,
            "adjudicated_population": self.adjudicated_population,
            "yield_floor": self.yield_floor,
            "yield_floor_derivation": YIELD_FLOOR_DERIVATION,
            "threshold_ratio": self.threshold_ratio,
            "short_by": self.short_by,
            "population_source": self.population_source,
            "provenance_disclosure": YIELD_PROVENANCE_DISCLOSURE,
            "holds": self.holds,
            "requirement": self.requirement,
            "measured": self.measured,
            "what_would_close_it": self.what_would_close_it,
            "unevaluable_reason": self.unevaluable_reason,
        }


def assess_yield(
    concentration: ConcentrationDisclosure,
    *,
    threshold: Fraction,
    population_source: str,
) -> YieldAssessment:
    """Evaluate §5's yield arm over the concentration the decision ALREADY published.

    *concentration* is the very instance the decision serializes and the breadth and seal
    arms read, so all three thresholds and the disclosure are computed from one set of
    counts. Recounting here would create a second answer to one question, and a
    disagreement between a disclosure and a threshold derived from it is invisible to every
    reader of either.

    ⛔ **The subject is ``adjudicated_population`` (DN-16-3-3)** — the count of live rows the
    ratio is computed over. Rejected: *the most recent adjudication set's emitted count*, a
    FOURTH population forked from the three the decision already reads, whose entirely-empty
    case Story 13.5 already closes; and *``total_tp + total_fp``*, which excludes BORDERLINE
    rows and would let this term disagree with breadth's over one population (26 against 31
    today), where the exhaustiveness branch already blocks on residuals, upstream.

    *population_source* names WHICH population was counted (AC1.5). It is not cosmetic: the
    concentration is derived from the committed record's LIVE rows, while the most recent
    adjudication set's EMITTED blocking population may be a different — even empty — set.
    That divergence predates this condition and is out of scope to fix; what is in scope is
    that the sentence never lets a reader mistake one for the other.

    PURE (AR8): reads a frozen dataclass and returns a frozen dataclass.
    """
    floor = verdict_eligible_population_floor(threshold)
    population = concentration.adjudicated_population
    holds = population >= floor
    short_by = max(0, floor - population)
    ratio = ratio_string(threshold)

    requirement = (
        f"protocol §5 as amended 2026-08-20 (Story 16.3; sprint change proposal "
        f"2026-08-20 §4.3(3)): the precision ratio is EVALUABLE only over a VERDICT-ELIGIBLE "
        f"population of at least {floor} adjudicated finding(s) — derived as "
        f"{YIELD_FLOOR_DERIVATION}. Below that floor a '>= {ratio}' threshold is silently a "
        f"100% threshold and a detector that emitted three ultra-safe findings would be "
        f"published as validated. This is a floor on the DENOMINATOR of the precision ratio "
        f"and NOT a floor on recall, on coverage, or on any estimate of FN: recall stays "
        f"ungated and diagnostic under the OI1 lock. This condition makes clearing HARDER "
        f"and can never make it easier"
    )
    measured = (
        f"yield = {population} verdict-eligible finding(s) against a floor of {floor}; "
        f"counted over the LIVE row(s) of {population_source} — NOT over the emitted "
        f"blocking population of the most recent adjudication set, which is a different "
        f"population and may be empty. At a denominator of {population} the largest number "
        f"of false positives the population could carry and still reach {ratio} is "
        f"{_affordable_false_positives(population, threshold)}. "
        + (
            f"The yield floor is MET. {YIELD_PROVENANCE_DISCLOSURE}."
            if holds
            else (
                f"The yield floor is NOT met — short by {short_by} verdict-eligible "
                f"finding(s). {YIELD_PROVENANCE_DISCLOSURE}."
            )
        )
    )
    what_would_close_it = (
        (
            f"already met; it re-opens the moment the adjudicated population falls back "
            f"below {floor} — by a superseded judgement, a withdrawn member, or a "
            f"re-measurement that promotes fewer findings"
        )
        if holds
        else (
            f"the detector must promote {short_by} further finding(s) to verdict-eligible "
            f"over a corpus chosen BEFORE anyone looks at what it contains, taking the "
            f"adjudicated population from {population} to {floor}, and the named human "
            f"(protocol §2) must adjudicate each of them TP or FP. NOT closable by lowering "
            f"the floor, by re-counting advisory findings toward it, or by admitting a "
            f"member's findings twice — protocol §5 and Story 13.3 / AC5 forbid every one of "
            f"those, and each would move the ratio rather than deepen the evidence. The "
            f"honest closure is MORE adjudicated evidence, and DF-13-5-A already names what "
            f"happens if it does not arrive"
        )
    )
    unevaluable_reason = (
        f"DENOMINATOR TOO SMALL TO RESOLVE THE THRESHOLD — the adjudicated population holds "
        f"{population} verdict-eligible finding(s), below protocol §5's yield floor of "
        f"{floor} ({YIELD_FLOOR_DERIVATION}), so a ratio computed over it faces a 100% bar "
        f"while being published against a {ratio} one"
    )
    return YieldAssessment(
        adjudicated_population=population,
        yield_floor=floor,
        threshold_ratio=ratio,
        population_source=population_source,
        holds=holds,
        requirement=requirement,
        measured=measured,
        what_would_close_it=what_would_close_it,
        unevaluable_reason=unevaluable_reason,
    )


def _affordable_false_positives(population: int, threshold: Fraction) -> int:
    """``max{ k : (population − k)/population >= threshold }`` — EXACT, and 0 below the floor.

    The number that makes the condition's subject legible in one clause: it is ZERO at every
    denominator below :func:`verdict_eligible_population_floor`, which IS the hole this
    condition closes. Computed with exact integer arithmetic (AR4) — ``floor(population *
    (q − p) / q)`` — never a float, because the boundary is the whole subject.

    PURE (AR8). Returns 0 for a non-positive *population*: a population the decision cannot
    accept anyway (``derive_concentration`` raises on it), reported as affording nothing
    rather than as a negative count.
    """
    if population <= 0:
        return 0
    p, q = threshold.numerator, threshold.denominator
    return max(0, (population * (q - p)) // q)


def yielded_precision_gate_status(
    *,
    fold: AdjudicatedPrecision,
    detector_yield: YieldAssessment,
    protocol_path: str,
    independence_note: str | None = None,
) -> str:
    """The gate-status sentence when the YIELD FLOOR is what makes precision unevaluable.

    The exact analogue of
    :func:`~argus.precision.gate_breadth.effective_precision_gate_status` and
    :func:`~argus.precision.gate_seal.sealed_precision_gate_status`, and — like both — it
    renders through the SAME
    :func:`~argus.precision.replay_harness.precision_gate_status_for` the fold used, never
    through a second status function (AR7). Publishing ``precision.evaluable = True`` beside
    a §5 precision verdict of ``UNEVALUABLE`` is the ``DF-9-2-B`` false-subject class on the
    surface that publishes the externalization gate.

    **Why a THIRD sibling rather than a widened breadth renderer (DN-16-3-8).** Story 16.2
    faced the identical choice and recorded its answer as DN-16-2-8: ``gate_breadth.py``'s
    subject is the breadth arm, and giving its renderer a second reason would make it
    not-about-breadth. This story follows that precedent rather than forking it, which is
    also why ``argus/precision/gate_breadth.py`` is left **byte-unchanged** here. All three
    functions are thin wrappers over ONE shared renderer and none authors a status string of
    its own — the fork AR7 forbids would be a second *renderer*, not a third caller.

    When the yield floor does not change the answer the fold's OWN string is returned
    BYTE-FOR-BYTE rather than re-rendered, so the amendment is provably inert on a population
    it does not bind (NFR-P1 byte-stability of the precision surface).

    PURE (AR8).
    Story 16.5: ``independence_note`` is FORWARDED verbatim, never derived here (AC7.1a).
    """
    if fold.evaluable == (fold.evaluable and detector_yield.holds):
        return fold.gate_status
    return precision_gate_status_for(
        precision=fold.precision,
        n=fold.n,
        provisional=fold.provisional,
        protocol_path=protocol_path,
        floor_n=fold.floor_n,
        population_label="eligible validation-set repositories",
        evaluable=False,
        unevaluable_reason=detector_yield.unevaluable_reason,
        independence_note=independence_note,
    )


def yield_blocked_reason(detector_yield: YieldAssessment) -> str:
    """The ``outcome_reason`` a decision BLOCKED on the yield floor publishes (AC1.6).

    It lives here rather than inline in :func:`~argus.precision.gate_decision.decide_gate`
    for DN-16-1-3's reason: the constants, the predicate and the measured and closure
    SENTENCES are this module's subject, and ``gate_decision`` builds the
    ``ConditionResult``. One direction only.

    **Why BLOCKED and not NOT_CLEARED, said in the sentence itself.** ``NOT_CLEARED`` may be
    recorded only when the measurement RAN, and a ratio over a population too small to
    resolve the threshold did not produce a measurement of the tool — it produced a figure
    against a bar the tool never faced. ``GATE_OUTCOMES`` stays CLOSED at three; no terminal
    state is invented.

    PURE (AR8).
    """
    return (
        f"the precision ratio is NOT EVALUABLE as a statement about the tool: protocol §5's "
        f"YIELD condition, as amended 2026-08-20 (Story 16.3), does not hold. "
        f"{detector_yield.measured} A ratio computed over a population this small faces a "
        f"100% bar while being published against a {detector_yield.threshold_ratio} one, so "
        f"a detector that emitted a handful of ultra-safe findings and got them all right "
        f"would be recorded as validated at >= {detector_yield.threshold_ratio} precision "
        f"against a threshold it never faced. This is NOT a shortfall and NOT a failed "
        f"measurement, and it is NOT a claim about defects the detector MISSED: the floor "
        f"was derived from the gate threshold's own arithmetic and frozen BEFORE the "
        f"measurement it governs, and it can only make clearing harder."
    )


def yield_closure_path(detector_yield: YieldAssessment) -> tuple[str, ...]:
    """What it would take, in COUNTABLE terms — a BLOCKED decision with no closure path raises.

    The last two legs are stated as REFUSALS rather than left to a reader's restraint. The
    tempting closure here is not lowering a threshold in the open — it is quietly counting
    something else toward the floor, or lowering the floor to whatever the population
    happened to be; the derivation makes the first impossible and these sentences make both
    visible.

    PURE (AR8).
    """
    return (
        detector_yield.what_would_close_it,
        "re-run scripts/build_gate_decision.py so the record carries the deepened "
        "population, and re-run this decision",
        "NOT closable by amending the floor or by widening what counts toward it: a "
        "threshold moved after seeing the population it failed is corpus-shopping with extra "
        "steps (protocol §5; Story 13.3 / AC5), and the floor is DERIVED from "
        "PRECISION_GATE_THRESHOLD rather than typed, so moving it means moving the gate "
        "threshold itself — in the open, and as an operator act",
        "NOT closable by a bigger bench either, and this is pre-registered rather than "
        "decided here: DF-13-5-A, answered 2026-08-17 before any number existed, allows "
        "exactly ONE bench-expansion round and routes a round that promotes too little to "
        "option (b) — the FR34 disclosure stands for V1.5 and the next attempt requires a "
        "materially better DETECTOR, not a bigger corpus",
    )
