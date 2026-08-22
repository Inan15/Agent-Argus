"""Story 16.3 — protocol §5's YIELD condition, driven to BOTH outcomes by real populations.

``TC-ArgusAgent-PRECISION-001-95``..``-100``. A **NEW** module, per AC4.4 and this story's
own measurement: ``tests/test_gate_seal.py`` has 65 lines of NFR-M1 headroom and
``tests/test_gate_decision.py`` had **nine** before this story split it, and *"do not shave
a file to fit"* is the rule these guards exist to obey rather than to test.

**The subject, measured rather than argued.** Driven through the SHIPPED ``decide_gate`` at
HEAD ``1ecf618``, a population of exactly **three** findings — one per sealed member, all
adjudicated TP — returned ``CLEARED`` at precision ``1/1`` with all six §5 conditions ``MET``
and an outcome sentence reading *"Clearing authorises ATTESTED externalization."* So did
four. ``UNEVALUABLE`` closed the hole for an **empty** denominator and Story 13.5 made *"the
corpus was read and nothing was promoted"* expressible; neither closes the **tiny** one.
Below a denominator of five the ``>= 80%`` gate is silently a **100%** gate, and the record
publishes the figure as though the tool had faced the bar it is quoted against.

**Why every population here is GENERATED** (AC4.1/AC4.3). The committed record can only
produce one population, the live fold is already unevaluable for a reason that has nothing
to do with yield (the emitted blocking population is empty), and the committed population of
31 sits *above* the floor — so a guard built only against the committed artifact would be
green, silent and useless. Every population below is generated at an exactly-known size and
every guard asserts **where the verdict flips**, not merely that it has two values.

⛔ **THE LOCKSTEP TRAP, in its third form, and the fixture that defeats it.** 16.1 shipped a
breadth clause no fixture reached; 16.2 found that over a sealed-only population breadth and
the seal move together, so deleting the seal clause left everything green, and built
``mixed_population`` to pin breadth TRUE while the sealed count moved. **The identical trap
is here again**: over a population built from sealed members, breadth, seal *and* yield all
rise together with the fixture size. ``-97`` is the answer — it pins breadth and the seal
TRUE by fixing the member spread and moves the population SIZE alone across the floor, so a
mutation deleting the yield clause has nowhere to hide. AC4.2's mutation list is executed
against exactly that fixture and each one is observed RED.

**GUARD-ADEQUACY (architecture §Enforcement) is discharged per guard**: each names its
**observable**, each moves the defect at the **real seam** (the shipped ``decide_gate`` over
real :class:`AdjudicationRow` objects through the real :class:`AdjudicationRecord` — never a
reconstruction), and each **GENERATES** its adversarial variants from the committed record,
from ``SECTION_5_CONDITIONS``, or from the module's own AST.

**Non-vacuity is asserted FIRST in every guard** (``DF-15-2-A`` arm (b)): the population
built is non-empty, the generated range is asserted to STRADDLE the floor, and the two
observed directions are asserted to be different answers — a family that never crossed the
boundary cannot pass.

**Platform neutrality** (the local gates here are Windows-only while CI runs an ubuntu
matrix): ``pathlib``, explicit ``encoding="utf-8"``, ``.as_posix()`` at every path→string
boundary, and no assertion on ``os.sep``, a drive letter or a CRLF-sensitive byte count.

**Nothing below is written to any committed artifact.** Every synthetic judgement lives
inside one test's local fixture, no detector runs over any repository, and no bench candidate
is fetched, staged, ratified or touched.
"""

from __future__ import annotations

import ast
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

import pytest

from argus.precision.adjudication import Exhaustive
from argus.precision.gate_decision import (
    BREADTH_CONDITION_ID,
    SEAL_CONDITION_ID,
    SECTION_5_CONDITIONS,
    YIELD_CONDITION_ID,
    GateDecision,
    section_5_condition,
)
from argus.precision.gate_disclosure import derive_concentration
from argus.precision.gate_yield import (
    YIELD_FLOOR_DERIVATION,
    YIELD_PROVENANCE_DISCLOSURE,
    VacuousYieldFloor,
    assess_yield,
    verdict_eligible_population_floor,
)
from argus.precision.replay_harness import PRECISION_GATE_THRESHOLD, registry_module

# The SEALED-population generators are IMPORTED, never copied (AR7 — the same reason
# tests/test_gate_breadth.py imports them and tests/test_gate_decision.py imports the §5
# dispatch mirror). `mixed_population` is the fixture that pins breadth TRUE while another
# term moves, and it is exactly what AC3.4 needs a third time.
from tests.test_gate_seal import decide_over, mixed_population, sealed_corpus_members

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_CORPUS_DIR = _ARTIFACTS / "validation-corpus"
_YIELD_MODULE = _REPO_ROOT / "argus" / "precision" / "gate_yield.py"

#: The two committed adjudication SETS the pre-round disclosure counts out of. Named as
#: paths rather than as figures so ``-100`` re-derives every number in
#: :data:`YIELD_PROVENANCE_DISCLOSURE` from the artifact instead of comparing two literals.
_SET_13_5 = _CORPUS_DIR / "adjudication-set-13-5.json"
_RECORD_PATH = _CORPUS_DIR / "adjudication-record.json"


def _floor() -> int:
    """§5's yield floor, resolved through the SHIPPED derivation over the shipped threshold."""
    return verdict_eligible_population_floor(PRECISION_GATE_THRESHOLD)


def _brute_force_floor(threshold: Fraction) -> int:
    """The floor found by SEARCH: the smallest ``d`` with ``(d-1)/d >= threshold``.

    Deliberately NOT the closed form under test — it shares no arithmetic with it. Two
    derivations that agree from different directions is the whole reason the number is
    defensible rather than convenient, and a mirror computing ``ceil(q/(q-p))`` a second time
    would agree with the shipped function even when both are wrong.

    Searches to a bound well above every threshold exercised; raises rather than returning a
    silent sentinel if it never crosses, because a mirror that quietly gives up would make
    the comparison below vacuous.
    """
    for d in range(1, 10_001):
        if Fraction(d - 1, d) >= threshold:
            return d
    raise AssertionError(f"no denominator below 10001 satisfies (d-1)/d >= {threshold}")


def _affordable_false_positives_by_search(population: int, threshold: Fraction) -> int:
    """``max{k : (population-k)/population >= threshold}``, found by ENUMERATION.

    The mirror for the sentence the condition publishes, computed by walking every possible
    ``k`` rather than by the closed form the module uses.
    """
    return max(
        k for k in range(0, population + 1) if Fraction(population - k, population) >= threshold
    )


def _sealed_only(*, size: int, members: int) -> tuple[GateDecision, int]:
    """A decision over *size* live TP findings spread across exactly *members* SEALED rows.

    Returns the decision and the population size it was actually built over, re-counted from
    the record rather than taken from the argument — a fixture that did not build what it
    claims would make every assertion over it about the wrong thing.
    """
    record, corpus = mixed_population(sealed_members=members, pre_seal_members=0, size=size)
    live = len(record.live_rows())
    assert live == size, (live, size)
    return decide_over(record, corpus=corpus), live


# ─────────────────────────────────────────────────────────────────────────────
# AC1.2 / AC1.3 — the floor is DERIVED from the threshold, and it RAISES
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_95_the_yield_floor_is_derived_from_the_locked_threshold() -> None:
    """TC-ArgusAgent-PRECISION-001-95 — AC1.2/AC1.3: derived, general, and not ``.denominator``.

    **Observable:** :func:`verdict_eligible_population_floor` and
    :data:`YIELD_FLOOR_DERIVATION`.

    **Four things fail independently.**

    *(i) It agrees with BRUTE FORCE over a family of thresholds*, not just the shipped one.
    The mirror SEARCHES for the smallest denominator at which one false positive is
    affordable; the module computes it closed-form. Two derivations sharing no arithmetic.

    *(ii) It DIVERGES from ``threshold.denominator``*, and the guard asserts the divergence
    rather than trusting the docstring: at ``5/7`` the floor is 4 and at ``7/9`` it is 5. The
    family is asserted to CONTAIN at least one divergent case, so writing
    ``return threshold.denominator`` cannot pass — which is the exact mutation AC4.2 lists and
    the exact shape of 16.1's *"strict majority"* error, one story later.

    *(iii) At the SHIPPED threshold it is 5, and the reason is measured:* the largest number
    of false positives affordable at ``>= 4/5`` is ZERO at every denominator below it and ONE
    at the floor. That transition IS the condition's subject, and it is enumerated rather
    than asserted.

    *(iv) A threshold that admits no false positive at any denominator RAISES* — ``AR10``,
    with a message that says what to do. A floor derived from such a threshold could never
    fail, which this codebase's own vocabulary calls *"not a threshold"*.

    **The defect MOVES the observable:** typing the floor, spelling it ``.denominator``,
    shifting it by one in either direction, or swallowing the vacuous case each reddens a
    different assertion above.
    """
    # (i) + (ii) — brute force, over a family, including thresholds where q diverges
    family = (
        Fraction(4, 5),
        Fraction(5, 7),
        Fraction(7, 9),
        Fraction(1, 2),
        Fraction(2, 3),
        Fraction(3, 4),
        Fraction(9, 10),
        Fraction(99, 100),
    )
    divergent = 0
    for threshold in family:
        derived = verdict_eligible_population_floor(threshold)
        assert derived == _brute_force_floor(threshold), (threshold, derived)
        assert derived >= 1, (threshold, derived)
        if derived != threshold.denominator:
            divergent += 1
    assert divergent >= 2, (
        f"non-vacuity: only {divergent} of {len(family)} thresholds distinguish the derived "
        f"floor from threshold.denominator, so this guard could not see that spelling as a "
        f"defect — which is precisely the mutation AC4.2 requires it to catch"
    )
    assert verdict_eligible_population_floor(Fraction(5, 7)) == 4
    assert verdict_eligible_population_floor(Fraction(7, 9)) == 5

    # (iii) the shipped threshold, and WHY the number is what it is
    floor = _floor()
    assert floor == 5, floor
    assert PRECISION_GATE_THRESHOLD == Fraction(4, 5), PRECISION_GATE_THRESHOLD
    affordable = {
        d: _affordable_false_positives_by_search(d, PRECISION_GATE_THRESHOLD)
        for d in range(1, floor + 3)
    }
    assert all(affordable[d] == 0 for d in range(1, floor)), affordable
    assert affordable[floor] == 1, affordable
    assert set(affordable.values()) == {0, 1}, (
        "non-vacuity: the enumerated range never crossed the point where a false positive "
        "becomes affordable, so it cannot show what the floor is for"
    )

    # (iv) the vacuous threshold RAISES
    for vacuous in (Fraction(1, 1), Fraction(3, 2), Fraction(5, 1)):
        with pytest.raises(VacuousYieldFloor) as raised:
            verdict_eligible_population_floor(vacuous)
        assert "PRECISION_GATE_THRESHOLD" in str(raised.value), str(raised.value)

    # The derivation lives WITH the rule, states the general form, and DISCLOSES the
    # coincidence rather than leaning on it (AC1.2).
    lowered = YIELD_FLOOR_DERIVATION.lower()
    for required in (
        "ceil(q / (q - p))",
        "q - p == 1",
        "threshold.denominator",
        "validation_set_floor_n",
        "coincidence",
        "5/7",
        "7/9",
        "vacuity",
    ):
        assert required in lowered, required
    assert len(YIELD_FLOOR_DERIVATION.split()) >= 120, len(YIELD_FLOOR_DERIVATION.split())


# ─────────────────────────────────────────────────────────────────────────────
# AC1.5 / AC3.5 — ONE count, from the published disclosure; the other floors untouched
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_96_the_count_is_read_from_the_published_disclosure() -> None:
    """TC-ArgusAgent-PRECISION-001-96 — AC1.5/AC3.5: one population, counted once.

    **Observable:** the decision's ``concentration.adjudicated_population`` against the
    ``yield`` block's own ``adjudicated_population``, over GENERATED populations of several
    sizes, plus the two existing floors it must neither resolve from nor fork.

    *(i) The yield arm's count IS the disclosure's count*, over every generated size — not a
    recount that happens to agree today. A second count is a second thing that can drift, and
    a disagreement between a disclosure and the threshold derived from it is invisible to
    every reader of either.

    *(ii) It is the SAME instance the breadth and seal arms read*, asserted by comparing all
    three published populations rather than by inspecting call sites.

    *(iii) The ``measured`` sentence NAMES which population it counted* and carries breadth's
    divergence caveat in substance — LIVE rows, not the most recent adjudication set's
    emitted blocking population, which is a different and possibly empty set.

    *(iv) It is NOT resolved from the breadth/seal floor and does not fork it* (DN-16-3-2):
    those two are 3, this is 5, they come from different sources, and the guard asserts the
    two existing floors still resolve through ONE function and still answer 3.

    **The defect MOVES the observable:** reading the count from a second source, or resolving
    the floor from ``contributing_member_floor`` / ``VALIDATION_SET_FLOOR_N``, reddens a
    different assertion above.
    """
    from argus.precision.gate_breadth import contributing_member_floor
    from argus.precision.gate_seal import sealed_member_floor

    floor = _floor()
    sizes = (3, 4, 5, 7, 11)
    assert min(sizes) < floor <= max(sizes), (
        f"non-vacuity: the generated sizes {sizes} do not straddle the floor of {floor}"
    )
    seen: set[bool] = set()
    for size in sizes:
        decision, live = _sealed_only(size=size, members=3)
        assert decision.yield_ is not None and decision.breadth is not None
        assert decision.seal is not None
        # (i) + (ii) — one population, read by all three arms and the disclosure
        assert decision.yield_.adjudicated_population == live == size
        assert (
            decision.concentration.adjudicated_population
            == decision.breadth.adjudicated_population
            == decision.seal.adjudicated_population
            == decision.yield_.adjudicated_population
        ), (
            "the yield arm counted a population the disclosure, the breadth arm and the seal "
            "arm do not agree with — a second count is a second thing that can drift"
        )
        assert decision.yield_.yield_floor == floor
        assert decision.yield_.holds is (size >= floor)
        seen.add(decision.yield_.holds)
        # (iii) — the sentence names its population and keeps the divergence caveat
        measured = decision.yield_.measured
        assert "LIVE row(s)" in measured, measured
        assert "most recent adjudication set" in measured, measured
        assert "may be empty" in measured, measured
        assert str(size) in measured and str(floor) in measured, measured
    assert seen == {True, False}, (
        f"non-vacuity: the generated family only ever observed holds={seen}"
    )

    # (iv) — a DIFFERENT quantity from a DIFFERENT source, and the other two are untouched
    floor_n = int(registry_module().VALIDATION_SET_FLOOR_N)
    assert contributing_member_floor(floor_n) == sealed_member_floor(floor_n) == 3, floor_n
    assert sealed_member_floor(floor_n) == contributing_member_floor(floor_n), (
        "the seal floor stopped resolving through 16.1's function — one quantity, one source"
    )
    assert floor != contributing_member_floor(floor_n), (
        "the yield floor collapsed onto the breadth/seal floor. They are different "
        "quantities: one counts CONTRIBUTING MEMBERS, this counts FINDINGS (DN-16-3-2)."
    )
    assert floor == floor_n, (
        "the disclosed coincidence stopped holding, which does not make the derivation "
        "wrong but does mean YIELD_FLOOR_DERIVATION's disclosure needs re-reading"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC3.3 / AC3.4 / AC4.1 — DECISIVE: breadth and the seal pinned TRUE, yield alone moves
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_97_the_yield_term_is_decisive_and_flips_at_the_floor() -> None:
    """TC-ArgusAgent-PRECISION-001-97 — AC3.3/AC3.4/AC4.1: the guard that would have caught it.

    **Observable:** the SHIPPED ``decide_gate``'s outcome, swept across the yield boundary
    over populations whose breadth and seal terms are **pinned TRUE**.

    ⛔ **Why the pinning is the whole point.** Over a population built from sealed members,
    breadth, seal and yield all rise together with the fixture size, so a sweep that grew all
    three would stay green with the yield clause deleted — the unreal-guard shape found in
    16.1's round 2 and defeated in 16.2 by ``mixed_population``. Here the member spread is
    HELD at three sealed members for every size, so breadth and the seal are constant TRUE
    and the population SIZE is the only thing that moves.

    **Both directions, and WHERE it flips.** Sizes 3 and 4 — the two measured as wrongly
    ``CLEARED`` before this condition — must be ``BLOCKED`` with the yield condition
    ``FAILED``, breadth ``MET`` and the seal ``MET``; sizes at and above the floor must be
    ``CLEARED`` with all seven ``MET``. The flip point is asserted to be the derived floor
    itself, not merely asserted to exist.

    **Every precondition ABOVE the yield clause is asserted false first**, so a ``BLOCKED``
    cannot be credited to the yield term when something upstream refused the population —
    which is exactly how a clause becomes decorative.

    **The defect MOVES the observable:** deleting the dispatch branch, deleting the yield
    term from ``_precision_condition``, sticking ``holds`` at either value, or shifting the
    floor by one reddens this guard. Each was EXECUTED and observed RED; the evidence is in
    the story's Dev Agent Record.
    """
    floor = _floor()
    sealed = sealed_corpus_members()
    members = 3
    assert members <= len(sealed), (members, len(sealed))
    sizes = tuple(range(members, floor + 3))
    assert min(sizes) < floor <= max(sizes), (
        f"non-vacuity: sizes {sizes} do not straddle the floor of {floor}, so the flip point "
        f"could not be observed"
    )

    outcomes: dict[int, str] = {}
    for size in sizes:
        decision, live = _sealed_only(size=size, members=members)
        fold = decision.fold
        # NON-VACUITY, asserted BEFORE anything is concluded: every clause ABOVE the yield
        # clause must be false, or a BLOCKED would be about something else entirely.
        assert fold.determinism is None, fold.determinism
        assert isinstance(fold.exhaustiveness, Exhaustive), fold.exhaustiveness
        assert fold.precision is not None and fold.meets_threshold, fold.precision_ratio
        assert decision.breadth is not None and decision.breadth.holds, (
            "breadth is not pinned TRUE over this fixture, so yield is not the only term "
            "moving and this guard has become a guard about breadth"
        )
        assert decision.seal is not None and decision.seal.holds, (
            "the seal is not pinned TRUE over this fixture, so yield is not the only term "
            "moving and this guard has become a guard about the seal"
        )
        assert decision.yield_ is not None and live == size

        expected = "CLEARED" if size >= floor else "BLOCKED"
        assert decision.outcome == expected, (
            f"a population of {size} against a yield floor of {floor}: expected {expected!r}, "
            f"got {decision.outcome!r}. yield={decision.yield_.holds} "
            f"breadth={decision.breadth.holds} seal={decision.seal.holds}"
        )
        outcomes[size] = decision.outcome

        yield_condition = section_5_condition(decision.conditions, YIELD_CONDITION_ID)
        assert yield_condition.verdict == ("MET" if size >= floor else "FAILED")
        # DN-16-3-4 — its OWN verdict is never UNEVALUABLE: the population WAS counted.
        assert yield_condition.verdict != "UNEVALUABLE", yield_condition
        assert section_5_condition(decision.conditions, BREADTH_CONDITION_ID).verdict == "MET"
        assert section_5_condition(decision.conditions, SEAL_CONDITION_ID).verdict == "MET"

        precision = section_5_condition(decision.conditions, "precision-at-least-80-percent")
        if size < floor:
            # AC1.6 — §5's PRECISION condition goes UNEVALUABLE with the counts that made it
            # so, the outcome is BLOCKED, and the closure path is countable.
            assert precision.verdict == "UNEVALUABLE", precision
            assert "YIELD condition" in precision.measured, precision.measured
            assert decision.closure_path, "a BLOCKED decision recorded no closure path"
            assert any("NOT closable by amending the floor" in leg for leg in decision.closure_path)
            assert "YIELD condition" in decision.outcome_reason, decision.outcome_reason
            assert not decision.precision_evaluable
            assert "eligible validation-set repositories" in decision.precision_gate_status
        else:
            assert precision.verdict == "MET", precision
            assert decision.precision_evaluable
            assert all(c.verdict == "MET" for c in decision.conditions), decision.conditions
            assert "yield floor" in decision.outcome_reason, decision.outcome_reason

    # THE FLIP POINT IS THE DERIVED FLOOR — asserted, not merely straddled.
    blocked = {size for size, outcome in outcomes.items() if outcome == "BLOCKED"}
    cleared = {size for size, outcome in outcomes.items() if outcome == "CLEARED"}
    assert blocked and cleared, outcomes
    assert max(blocked) + 1 == min(cleared) == floor, (outcomes, floor)
    assert {3, 4} <= blocked, (
        "sizes 3 and 4 are the two populations MEASURED as wrongly CLEARED at HEAD 1ecf618. "
        "If they are no longer blocked, the condition this story exists for is not binding."
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC3.1 / AC3.2 / AC5 — composition, not replacement; harder, never easier
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_98_quantity_without_breadth_still_fails() -> None:
    """TC-ArgusAgent-PRECISION-001-98 — AC3.1/AC3.2/AC5.1: two terms, not one wearing the other's name.

    **Observable:** the outcome and the per-condition verdicts over a population with **yield
    well above the floor** and **contributing members below the breadth floor**.

    *(i) Quantity without breadth still fails.* 40 findings from ONE sealed member is
    ``BLOCKED``, with breadth ``FAILED`` **and** yield ``MET`` — which is only expressible if
    the two are independent terms. If the yield floor had quietly replaced the breadth one,
    this population would clear.

    *(ii) And the converse* (``-97``'s subject, restated here as the other half of the pair):
    breadth and seal ``MET`` with yield below the floor is ``BLOCKED`` on yield. Both
    directions in one guard, because *"they compose"* is a claim about the PAIR.

    *(iii) Neither short-circuits the other.* Over a population failing BOTH, each condition
    still reports its own verdict — no condition is folded into another or skipped.

    *(iv) HARDER, never easier (AC5.1).* Across a swept family, every population that clears
    after the amendment is asserted to have yield ``MET``; and the two sizes that cleared
    before it are asserted ``BLOCKED`` now. The condition can only remove clearances, never
    create one.

    **The defect MOVES the observable:** folding yield into breadth, or letting a yield
    ``MET`` short-circuit the breadth branch, reddens a different assertion above.
    """
    floor = _floor()

    # (i) quantity without breadth — 40 findings, ONE contributing member
    decision, live = _sealed_only(size=40, members=1)
    assert live == 40 > floor, (live, floor)
    assert decision.breadth is not None and decision.yield_ is not None
    assert decision.yield_.holds is True, decision.yield_.measured
    assert decision.breadth.holds is False, decision.breadth.measured
    assert decision.outcome == "BLOCKED", decision.outcome_reason
    assert section_5_condition(decision.conditions, YIELD_CONDITION_ID).verdict == "MET"
    assert section_5_condition(decision.conditions, BREADTH_CONDITION_ID).verdict == "FAILED"
    assert "BREADTH condition" in decision.outcome_reason, decision.outcome_reason
    assert "YIELD condition" not in decision.outcome_reason, (
        "a population that fails BREADTH is told about the yield floor. §5's own condition "
        "order decides which reason a reader is told, and provenance is prior to quantity."
    )

    # (ii) the converse — breadth and seal MET, yield below the floor
    converse, live = _sealed_only(size=floor - 1, members=3)
    assert live == floor - 1
    assert converse.breadth is not None and converse.seal is not None
    assert converse.yield_ is not None
    assert converse.breadth.holds and converse.seal.holds and not converse.yield_.holds
    assert converse.outcome == "BLOCKED", converse.outcome_reason
    assert section_5_condition(converse.conditions, BREADTH_CONDITION_ID).verdict == "MET"
    assert section_5_condition(converse.conditions, YIELD_CONDITION_ID).verdict == "FAILED"

    # (iii) BOTH failing — each still reports its own verdict, nothing short-circuits
    both, live = _sealed_only(size=2, members=1)
    assert live == 2 < floor
    assert both.breadth is not None and both.yield_ is not None
    assert not both.breadth.holds and not both.yield_.holds
    assert len(both.conditions) == len(SECTION_5_CONDITIONS) == 7, both.conditions
    assert section_5_condition(both.conditions, BREADTH_CONDITION_ID).verdict == "FAILED"
    assert section_5_condition(both.conditions, YIELD_CONDITION_ID).verdict == "FAILED"
    assert both.outcome == "BLOCKED"

    # (iv) HARDER, never easier — swept, and asserted over the whole family
    cleared_sizes: set[int] = set()
    for size in range(3, floor + 4):
        swept, _ = _sealed_only(size=size, members=3)
        assert swept.yield_ is not None
        if swept.outcome == "CLEARED":
            assert swept.yield_.holds, (
                "a decision CLEARED with the yield floor unmet — the condition made clearing "
                "EASIER somewhere, which protocol §5 and Story 13.3 / AC5 forbid outright"
            )
            cleared_sizes.add(size)
        else:
            assert not swept.precision_evaluable or swept.outcome != "CLEARED"
    assert cleared_sizes, "non-vacuity: no population in the swept family cleared at all"
    assert min(cleared_sizes) == floor, (cleared_sizes, floor)
    assert 3 not in cleared_sizes and 4 not in cleared_sizes, cleared_sizes


# ─────────────────────────────────────────────────────────────────────────────
# AC2.4 — the OI1 lock, made MECHANICALLY CHECKABLE by an AST walk
# ─────────────────────────────────────────────────────────────────────────────

#: The names that would make this condition a RECALL gate. ``recall`` needs ``FN``; ``FN`` is
#: unknowable over a repository corpus (*"a real repository has no golden key"*, protocol
#: V1.1); and a co-occurrence / bench-content quantity is an ESTIMATE of ``FN`` from a text
#: proxy, which ``scripts/candidate_selection.py`` refuses in its own words. Any of them
#: appearing among this module's imports or names would mean the floor came from somewhere
#: other than the threshold's own arithmetic.
_FORBIDDEN_NAMES = frozenset(
    {
        "recall",
        "recall_ratio",
        "recall_den",
        "recall_num",
        "total_fn",
        "fn",
        "false_negative",
        "false_negatives",
        "golden_key",
        "golden_findings",
        "PrecisionResult",
        "co_occurrence",
        "cooccurrence",
        "co_occurrence_files",
        "bench_content",
        "planted_defects",
        "VALIDATION_CORPUS",
        "candidate_selection",
    }
)


def _structural_names(source: str) -> set[str]:
    """Every NAME and IMPORT the module binds or reads — string constants deliberately excluded.

    ⛔ **String constants are out of scope ON PURPOSE, and saying so is part of the guard.**
    The module must be able to NAME what it refuses: its docstring explains at length why a
    floor on the ratio's denominator is not recall, and the sentences it publishes say in
    terms that this is *"NOT a floor on recall, on coverage, or on any estimate of FN"*. A
    textual grep would forbid exactly the disclosure AC2.1 requires. What must stay absent is
    a structural DEPENDENCE — an import, an attribute, a parameter, a variable — because that
    is what it would take for such a quantity to reach the arithmetic.
    """
    tree = ast.parse(source)
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.update(alias.name.split("."))
                if alias.asname:
                    names.add(alias.asname)
        elif isinstance(node, ast.ImportFrom):
            names.update((node.module or "").split("."))
            for alias in node.names:
                names.add(alias.name)
                if alias.asname:
                    names.add(alias.asname)
        elif isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def test_TC_ArgusAgent_PRECISION_001_99_the_yield_floor_is_structurally_not_recall() -> None:
    """TC-ArgusAgent-PRECISION-001-99 — AC2.4: the OI1 answer, made checkable rather than promised.

    **Observable:** the shipped ``argus/precision/gate_yield.py``'s own AST — its imports,
    its bound and read names, its parameters — walked on the ``gate_seal.py`` purity-assertion
    precedent (``-87`` (iv)).

    **The question this answers.** Recall is diagnostic-only by the OI1 lock, and a floor on a
    population size is adjacent to recall. The answer turns entirely on WHERE THE NUMBER COMES
    FROM: a floor derived from the THRESHOLD's own arithmetic contains no ``FN`` term and
    makes no claim about undetected defects; a floor derived from HOW MUCH OF THE DEFECT CLASS
    THE BENCH CARRIES is recall with an estimated denominator, and is an operator escalation
    rather than something to land. This guard makes the first structurally true instead of
    promised.

    **Three legs, each failing independently.**

    *(i) No forbidden name appears* among the module's imports, names, attributes or
    parameters.

    *(ii) The guard is DRIVEN TO RED* by adversarial variants that add exactly such a
    reference — an import of the recall symbol and a use of an ``FN`` term. A structural
    assertion nobody has watched fail is a comment with an ``assert`` in front of it.

    *(iii) The floor's only inputs are the THRESHOLD and the published population*, asserted
    by evaluating the same floor twice over the same threshold and by driving the assessment
    over two populations that differ only in size — no bench quantity can be reaching it,
    because nothing about the bench changed between the calls.

    **The defect MOVES the observable:** adding any recall or bench-content reference to the
    module reddens (i); removing the forbidden-name check reddens (ii).
    """
    source = _YIELD_MODULE.read_text(encoding="utf-8")
    assert source.strip(), f"non-vacuity: {_YIELD_MODULE.name} is empty"
    names = _structural_names(source)
    assert names, "non-vacuity: the AST walk bound ZERO names"
    assert "assess_yield" in names and "verdict_eligible_population_floor" in names, (
        "non-vacuity: the AST walk did not see the module's own public functions, so it is "
        "walking something other than what ships"
    )

    # (i) — nothing forbidden, case-insensitively, and the check is exact-name rather than
    # substring so a legitimate identifier is never caught by accident.
    lowered = {name.lower() for name in names}
    found = sorted(name for name in _FORBIDDEN_NAMES if name.lower() in lowered)
    assert not found, (
        f"argus/precision/gate_yield.py structurally references {found!r}. The yield floor "
        f"is derived from PRECISION_GATE_THRESHOLD and from NOTHING ELSE. A floor that "
        f"depends on an FN term, on a golden key, or on how much of the defect class the "
        f"bench carries is RECALL with an estimated denominator — it re-opens the OI1 lock, "
        f"and re-opening OI1 is an OPERATOR ACT (AC2.5), not an implementation choice. If "
        f"the floor genuinely cannot be stated without one of these, HALT and escalate."
    )

    # (ii) — DRIVEN TO RED. Generated from the shipped source, never hand-written.
    adversaries = {
        "an imported recall symbol": (
            "from argus.precision.replay_harness import recall_ratio\n" + source
        ),
        "an FN term in the arithmetic": source.replace(
            "    p, q = threshold.numerator, threshold.denominator\n"
            "    if q - p <= 0:",
            "    total_fn = 431\n"
            "    p, q = threshold.numerator, threshold.denominator\n"
            "    if q - p <= 0:",
            1,
        ),
        "a bench-content quantity": source.replace(
            "    floor = verdict_eligible_population_floor(threshold)",
            "    co_occurrence_files = 431\n"
            "    floor = verdict_eligible_population_floor(threshold)",
            1,
        ),
    }
    for label, variant in adversaries.items():
        assert variant != source, (
            f"the adversarial variant {label!r} is byte-identical to the shipped source, so "
            f"it proves nothing — the anchor it patches has moved"
        )
        variant_names = {name.lower() for name in _structural_names(variant)}
        assert any(name.lower() in variant_names for name in _FORBIDDEN_NAMES), (
            f"the guard did NOT go red on {label!r} — it is structurally incapable of seeing "
            f"the defect it claims to prevent, which is the unreal-guard shape this project "
            f"has shipped four times"
        )

    # (iii) — the floor's only inputs
    floor = _floor()
    assert floor == verdict_eligible_population_floor(PRECISION_GATE_THRESHOLD)
    concentrations = []
    for size in (floor - 2, floor + 2):
        record, corpus = mixed_population(sealed_members=3, pre_seal_members=0, size=size)
        concentration = derive_concentration(
            record,
            ratified_member_ids=[str(member["member_id"]) for member in corpus],
        )
        concentrations.append(
            assess_yield(
                concentration,
                threshold=PRECISION_GATE_THRESHOLD,
                population_source="synthetic fixture",
            )
        )
    below, above = concentrations
    assert below.yield_floor == above.yield_floor == floor, (below.yield_floor, above.yield_floor)
    assert below.holds is False and above.holds is True, (below.holds, above.holds)
    # The published sentence says what the condition is NOT, so no reader can read a recall
    # gate into it (AC2.1's other half, carried on the condition rather than only in the doc).
    assert "NOT a floor on recall" in below.requirement, below.requirement
    assert "estimate of FN" in below.requirement, below.requirement


# ─────────────────────────────────────────────────────────────────────────────
# AC5.5 — the pre-round disclosure, RE-DERIVED from the committed artifacts
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_100_the_pre_round_disclosure_is_re_derived_not_typed() -> None:
    """TC-ArgusAgent-PRECISION-001-100 — AC5.5: ``MET`` today must not read as *"it yields 31"*.

    **Observable:** :data:`YIELD_PROVENANCE_DISCLOSURE` against the committed adjudication
    SETS it describes, plus the committed gate decision's own yield verdict.

    **Why the disclosure exists.** Over the committed population of 31 the yield condition
    reads ``MET`` — 31 is above the floor of 5. A reader could take that as *"the detector
    currently yields 31."* It does not: those 31 were produced by the PRE-Epic-14
    corroboration rule that Epic 14 refuted, and were adjudicated 0 TP / 26 FP / 5 BORDERLINE.
    The CORRECTED detector's verdict-eligible yield over the same five ratified members is
    **zero**. That is the pre-round disclosure owed to the operator BEFORE ``DF-13-5-A``'s ONE
    round is spent, and it is carried on the condition rather than left in story prose.

    **Every figure in it is RE-DERIVED here from the committed artifacts** — the
    ``SEALED_PARTITION_TABLE`` treatment rather than a typed literal — so the string cannot
    drift from the sets it describes. The module cannot read those artifacts itself (AR8 /
    ``DF-9-2-A``: it ships in a wheel), which is exactly why this guard must.

    **AC5.5's other half: the amendment is INERT ON THE LIVE TREE, verified at the producing
    seam.** The committed decision must still be ``BLOCKED`` for the Story 13.5 reason — the
    corpus was read and nothing was promoted — and NOT for a yield reason.

    **The defect MOVES the observable:** changing a figure in the disclosure, or letting the
    committed decision become blocked on yield, reddens a different assertion above.
    """
    payload = json.loads(_SET_13_5.read_text(encoding="utf-8"))
    members = payload["members"]
    assert members, "non-vacuity: adjudication-set-13-5.json names ZERO members"
    findings = [finding for member in members for finding in member.get("findings", [])]
    assert findings, "non-vacuity: the 2026-08-18 set carries ZERO findings"
    verdict_eligible = sum(1 for f in findings if f.get("verdict_eligible"))
    blocking = sum(1 for f in findings if f.get("blocking"))
    rule_classes = Counter(f.get("rule_id") for f in findings)

    # The CORRECTED detector's yield over the gating corpus, counted rather than quoted.
    assert f"{len(findings)} finding(s)" in YIELD_PROVENANCE_DISCLOSURE, len(findings)
    assert f"across all {len(members)} ratified members" in YIELD_PROVENANCE_DISCLOSURE
    assert f"promoted {verdict_eligible} of them" in YIELD_PROVENANCE_DISCLOSURE
    assert f"{blocking} blocking" in YIELD_PROVENANCE_DISCLOSURE
    assert verdict_eligible == blocking == 0, (verdict_eligible, blocking)
    assert len(rule_classes) > 1, rule_classes

    # The 2026-08-16 population of 31 and its dispositions, counted out of the committed
    # record rather than quoted from story prose.
    record = json.loads(_RECORD_PATH.read_text(encoding="utf-8"))
    rows = record["rows"]
    assert rows, "non-vacuity: the committed adjudication record carries ZERO rows"
    superseded = {str(row["supersedes"]) for row in rows if row.get("supersedes")}
    live = [row for row in rows if str(row["row_id"]) not in superseded]
    dispositions = Counter(str(row["disposition"]) for row in live)
    assert f"set of {len(live)}" in YIELD_PROVENANCE_DISCLOSURE, len(live)
    assert (
        f"{dispositions['TP']} TP / {dispositions['FP']} FP / "
        f"{dispositions['BORDERLINE']} BORDERLINE" in YIELD_PROVENANCE_DISCLOSURE
    ), dispositions
    assert dispositions["TP"] == 0 and dispositions["FP"] > 0, dispositions
    assert len(live) > _floor(), (
        "non-vacuity: the committed population no longer sits ABOVE the yield floor, so the "
        "'MET today' reading this disclosure exists to qualify is no longer what happens"
    )

    # ⛔ THE LIVE LEG, added after an EXECUTED MUTATION found this guard UNREAL. Deleting
    # `YIELD_PROVENANCE_DISCLOSURE` from the MET branch of `assess_yield`'s measured sentence
    # left every assertion above GREEN, because they all read the COMMITTED artifact — which
    # a mutation run does not regenerate. A guard that can only see a stale JSON file is a
    # guard about a file, not about the code that writes it. Both branches are driven at the
    # LIVE seam, because the MET branch is the one that most needs the qualifier: it is the
    # branch a reader would otherwise take as "the detector currently yields 31".
    live_legs = {}
    for size in (_floor() - 2, _floor() + 2):
        generated, corpus = mixed_population(
            sealed_members=3, pre_seal_members=0, size=size
        )
        assessment = assess_yield(
            derive_concentration(
                generated,
                ratified_member_ids=[str(member["member_id"]) for member in corpus],
            ),
            threshold=PRECISION_GATE_THRESHOLD,
            population_source="synthetic fixture",
        )
        live_legs[assessment.holds] = assessment
        assert YIELD_PROVENANCE_DISCLOSURE in assessment.measured, (
            f"the LIVE measured sentence for a population of {size} (holds="
            f"{assessment.holds}) does not carry the pre-round disclosure. A reader of a MET "
            f"yield condition would see a population size with nothing qualifying it, and "
            f"the committed artifact would not notice until it was next regenerated."
        )
    assert set(live_legs) == {True, False}, (
        f"non-vacuity: the live legs only observed holds={sorted(live_legs)}, so one branch "
        f"of the measured sentence was never exercised"
    )

    # The disclosure says the unmeasured part is UNMEASURED and not impossible (§0.3 / AC7.4).
    for required in (
        "UNMEASURABLE",
        "R2 operator act",
        "not bounded-by-construction",
        "found none",
        "option (b)",
        "NOT a bigger bench",
    ):
        assert required in YIELD_PROVENANCE_DISCLOSURE, required

    # AC5.5 — INERT at the producing seam: still BLOCKED, still for the 13.5 reason.
    committed = json.loads(
        (_CORPUS_DIR / "gate-decision-record.json").read_text(encoding="utf-8")
    )
    assert committed["outcome"] == "BLOCKED", committed["outcome"]
    yield_block = committed["yield"]
    assert yield_block is not None and yield_block["holds"] is True, yield_block
    assert yield_block["adjudicated_population"] == len(live) >= yield_block["yield_floor"]
    reported = [c["condition_id"] for c in committed["section_5_conditions"]]
    assert reported == list(SECTION_5_CONDITIONS), reported
    yield_condition = next(
        c for c in committed["section_5_conditions"] if c["condition_id"] == YIELD_CONDITION_ID
    )
    assert yield_condition["verdict"] == "MET", yield_condition
    assert "YIELD condition" not in committed["outcome_reason"], (
        "the committed decision is BLOCKED on the YIELD floor, which means the amendment "
        "changed the outcome's REASON on the live population. It must still be BLOCKED for "
        "the reason it was blocked for before (AC5.5)."
    )
    assert "NOTHING was promoted" in committed["outcome_reason"], committed["outcome_reason"]
    assert YIELD_PROVENANCE_DISCLOSURE in yield_condition["measured"], (
        "the committed condition's measured sentence does not carry the pre-round "
        "disclosure, so a reader sees MET with nothing qualifying it"
    )
