"""Story 13.2 / AC1 — the flip path cannot certify a corpus it never measured.

``TC-ArgusAgent-PRECISION-001-32``..``-37``. A NEW module by necessity and by design:
``tests/test_evidence_citation.py`` measured **1199/1200** lines and
``tests/test_instrument_disclosure.py`` **1179/1200** at the start of this story, so the
sanctioned remedy is a cohesion split, never shaving (12.8's precedent, 13.1 / DN-10).
Cohesion here is real and not merely convenient: every guard below closes over the
**gate-flip predicate** — the three inputs to ``provisional is False`` — and nothing else.

**Why this file exists at all.** Measured by execution on ``bc55e36`` and re-measured on
``1816524``, all three inputs to the flip were independently reachable **without a single
adjudicated finding**:

1. ``compute_precision`` accepted a ``registry=`` injection and still read ``n`` from the
   module-level cartridge count — a **2**-member corpus reported ``N=7``;
2. an empty precision denominator returned ``Fraction(1, 1)`` by convention, which
   ``meets_threshold`` compared against ``4/5`` and passed — a corpus emitting **nothing**
   reported ``provisional=False`` and a gate string reading *"cleared"*;
3. §5's clean-repo blocking-FP condition is defined over a member with an empty golden key
   AND ``max_blocking == 0``, which no repository-corpus member has — so on the population
   that actually gates externalization it was vacuously satisfied for every possible input.

Read (1) and (2) together: a corpus of **two** members that emitted **zero** findings
reported ``N=7``, ``precision=1/1`` and **cleared**, the moment a caller passed
``protocol_cleared=True``. The only thing standing between this repository and a false
cleared claim was a human's decision not to pass that flag.

**GUARD-ADEQUACY (``AI-E11-1``), discharged per guard below:** each names its
**observable**, each is shown moving **at the real seam** (the shipped
``compute_precision``, not a copy), and ``-33``/``-35``/``-37`` **generate** their
adversarial variants from the live registry rather than hand-writing one.

**This file does NOT flip the gate.** It passes ``protocol_cleared=True`` in order to prove
the flip is *refused*, which is why it is registered by name in
``_PROTOCOL_CLEARED_TEST_EXEMPTIONS`` (``tests/test_instrument_disclosure.py``). No
``argus/**`` module passes it, ``TC-ArgusAgent-DOCS-001-46`` stays green, and computing the
four §5 conditions is Story 13.3's.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CARTRIDGES = _REPO_ROOT / "tests" / "cartridges"
if str(_CARTRIDGES) not in sys.path:
    sys.path.insert(0, str(_CARTRIDGES))

from _registry import (  # noqa: E402  # type: ignore[import-not-found]
    CARTRIDGE_REGISTRY,
    VALIDATION_SET_FLOOR_N,
    populated_planted_defect_count,
)

from argus.precision.replay_harness import (  # noqa: E402
    PRECISION_GATE_THRESHOLD,
    compute_precision,
    gate_is_provisional,
    golden_match_key,
    precision_fraction,
    precision_gate_status_for,
)


def _perfect_emission() -> dict[str, frozenset[tuple[str, bool, bool]]]:
    """Every cartridge emits exactly its golden key — the 1/1, non-degenerate baseline."""
    return {
        spec.cartridge_id: frozenset(
            golden_match_key(gf) for gf in spec.required_findings
        )
        for spec in CARTRIDGE_REGISTRY
    }


def _silent_emission(
    registry: tuple[object, ...] = CARTRIDGE_REGISTRY,
) -> dict[str, frozenset[tuple[str, bool, bool]]]:
    """Nothing is emitted anywhere — the degenerate denominator, reproduced exactly."""
    return {spec.cartridge_id: frozenset() for spec in registry}  # type: ignore[attr-defined]


# ─────────────────────────────────────────────────────────────────────────────
# AC1a — ``n`` counts the population that was ACTUALLY folded
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_32_n_counts_the_injected_population() -> None:
    """TC-ArgusAgent-PRECISION-001-32 — AC1a: an injected population's N is ITS count, not the registry's.

    **Observable:** ``PrecisionResult.n`` and the ``N=`` figure in ``gate_status``.
    **The defect, at the real seam:** ``compute_precision`` accepted ``registry=`` and read
    ``n = populated_planted_defect_count()`` off the module-level registry regardless.
    Injecting two cartridges reported ``N=7 labeled cartridges >= floor N=5``.
    """
    injected = CARTRIDGE_REGISTRY[:2]
    result = compute_precision(
        _silent_emission(injected), registry=injected, protocol_cleared=True
    )
    assert len(result.rows) == 2, "the fold must have iterated exactly the injected rows"
    assert result.n == populated_planted_defect_count(injected), (
        f"N={result.n} does not count the population that was folded "
        f"({populated_planted_defect_count(injected)} labeled row(s) of "
        f"{len(injected)} injected). Before Story 13.2 this reported "
        f"{populated_planted_defect_count()} — the WHOLE registry — and the gate string "
        f"said 'cleared ... N=7 labeled cartridges >= floor N=5' for a 2-member corpus."
    )
    assert result.n < populated_planted_defect_count(), (
        "the reproduction requires the injected population to be SMALLER than the "
        "registry, or this guard proves nothing"
    )
    assert f"N={result.n} " in result.gate_status
    assert result.provisional is True, (
        "a 2-member corpus is below the N=5 floor and must never report a cleared gate, "
        "even with protocol_cleared=True"
    )


def test_TC_ArgusAgent_PRECISION_001_33_default_n_is_byte_unchanged_and_the_count_is_not_forked() -> None:
    """TC-ArgusAgent-PRECISION-001-33 — AC1a/DN-2: additive, with the default preserving today's N.

    **Observable:** ``n`` for the DEFAULT (unsupplied) registry, and the identity of the
    predicate used. **Adversarial variant, GENERATED from the live registry** rather than
    hand-written: every prefix of ``CARTRIDGE_REGISTRY`` is folded and its ``n`` compared
    against the registry's OWN predicate applied to that prefix. A second eligible-member
    count implemented here would diverge on at least one prefix — which is the fork
    13.1 / DN-3 refused, and the way two populations came to disagree about N in the first
    place.
    """
    default = compute_precision(_perfect_emission())
    assert default.n == populated_planted_defect_count(), (
        "the DEFAULT call must return exactly the pre-13.2 number (NFR-P1 byte-stability)"
    )
    assert populated_planted_defect_count(CARTRIDGE_REGISTRY) == (
        populated_planted_defect_count()
    ), "passing the registry explicitly must equal the no-argument call"

    checked = 0
    for size in range(1, len(CARTRIDGE_REGISTRY) + 1):
        population = CARTRIDGE_REGISTRY[:size]
        folded = compute_precision(_silent_emission(population), registry=population)
        assert folded.n == populated_planted_defect_count(population), (
            f"prefix of {size}: the harness reported N={folded.n} while the registry's "
            f"own predicate says {populated_planted_defect_count(population)} — the two "
            f"counts have forked"
        )
        checked += 1
    assert checked == len(CARTRIDGE_REGISTRY) >= 5, (
        f"non-vacuity: only {checked} population(s) were generated; a guard that "
        f"iterates an empty enumeration passes forever (AI-E11-1)"
    )


def test_TC_ArgusAgent_PRECISION_001_34_population_n_is_an_explicit_override_for_a_measured_count() -> None:
    """TC-ArgusAgent-PRECISION-001-34 — AC1a: ``population_n`` carries a MEASURED count for another corpus.

    **Observable:** ``n`` when the caller supplies the count of a population this function
    does not iterate — the repository corpus, whose N is 13.1's derived
    ``eligible_member_count()``. The parameter exists so 13.3 never has to type a number;
    ``adjudication.validation_set_population_n()`` is the only intended source.
    """
    result = compute_precision(_perfect_emission(), population_n=3)
    assert result.n == 3
    assert result.n != populated_planted_defect_count(), (
        "the override must actually override, or the guard is vacuous"
    )
    assert result.provisional is True, (
        "N=3 is below the floor, so the gate stays provisional regardless"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC1b — an empty denominator is UNEVALUABLE, never cleared
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_35_empty_denominator_is_unevaluable_not_cleared() -> None:
    """TC-ArgusAgent-PRECISION-001-35 — AC1b: a corpus that emitted NOTHING cannot clear the gate.

    **Observable:** ``provisional``, ``meets_threshold``, ``precision_evaluable`` and the
    first word of ``gate_status``. **The defect, reproduced verbatim at the real seam:**
    ``0 TP / 0 FP / 8 FN`` returned ``precision=1/1`` (the *"no false positive emitted"*
    convention), ``provisional=False`` and ``gate_status`` starting with **"cleared"**,
    while the corpus is at N=7 ≥ 5 and the caller passed ``protocol_cleared=True``.
    """
    result = compute_precision(_silent_emission(), protocol_cleared=True)
    assert (result.total_tp, result.total_fp) == (0, 0), (
        "the reproduction requires an EMPTY denominator; this corpus emitted findings"
    )
    assert result.n >= result.floor_n, (
        "the reproduction requires the floor to be MET, so that the only thing standing "
        "between this input and a cleared gate is the degenerate denominator"
    )
    assert result.precision_evaluable is False
    assert result.meets_threshold is False, (
        "Fraction(1, 1) >= 4/5 is arithmetically true and measurement-wise meaningless: "
        "an empty denominator is not an 80% result, it is no result"
    )
    assert result.provisional is True, (
        "0 TP / 0 FP with protocol_cleared=True previously returned provisional=False"
    )
    assert result.gate_status.startswith("unevaluable"), result.gate_status[:120]
    assert "NEITHER cleared NOR met" in result.gate_status, (
        "the status must state the negative explicitly: a reader scanning for the word "
        "'cleared' must find it only inside a sentence that denies it"
    )
    assert not result.gate_status.startswith("cleared")
    assert "0 TP, 0 FP" in result.measurement_note, (
        "the degenerate counts must be RECORDED on the result, not merely flagged"
    )
    assert precision_fraction(0, 0) is None, (
        "the shared arithmetic must return None (no result), never a flattering 1/1"
    )


def test_TC_ArgusAgent_PRECISION_001_36_unevaluable_cannot_be_rendered_as_cleared() -> None:
    """TC-ArgusAgent-PRECISION-001-36 — AC1b: the status renderer REFUSES to clear an unmeasured run.

    **Observable:** whether ``precision_gate_status_for`` can be made to emit the word
    *cleared* for a run that measured nothing. **Adversarial variants, GENERATED** by
    driving the renderer over the full cross-product of its two honesty flags and the
    shared predicate over a generated grid of inputs — a hand-written case would have
    covered the combination someone thought of.
    """
    with pytest.raises(ValueError, match="denominator was EMPTY"):
        # The degenerate corpus renders a Fraction (the preserved 1/1 convention) while
        # declaring itself unevaluable — the renderer must refuse on the FLAG, not merely
        # on a None it could have been handed instead.
        precision_gate_status_for(
            precision=Fraction(1, 1),
            n=9,
            provisional=False,
            protocol_path="p.md",
            evaluable=False,
        )
    with pytest.raises(ValueError, match="NO precision number"):
        precision_gate_status_for(
            precision=None, n=9, provisional=False, protocol_path="p.md"
        )

    generated = 0
    for tp in range(0, 4):
        for fp in range(0, 4):
            measured = precision_fraction(tp, fp)
            provisional = gate_is_provisional(
                n=9, floor_n=5, protocol_cleared=True, precision=measured
            )
            status = precision_gate_status_for(
                precision=measured,
                n=9,
                provisional=provisional,
                protocol_path="p.md",
                floor_n=5,
                evaluable=measured is not None,
            )
            generated += 1
            if measured is None:
                assert provisional is True and status.startswith("unevaluable")
            elif measured >= PRECISION_GATE_THRESHOLD:
                assert provisional is False and status.startswith("cleared"), (
                    f"tp={tp} fp={fp}: the flip path must still WORK when a real "
                    f"measurement clears it — a guard that made the gate unflippable "
                    f"would be as wrong as one that let it flip for free"
                )
            else:
                assert provisional is True and status.startswith("provisional")
    assert generated == 16, f"non-vacuity: {generated} generated case(s), expected 16"


# ─────────────────────────────────────────────────────────────────────────────
# AC1c — §5's clean-repo condition NAMES the corpus it is measured over
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_37_clean_repo_condition_names_its_population() -> None:
    """TC-ArgusAgent-PRECISION-001-37 — AC1c: a §5 condition that cannot fail is reported NOT APPLICABLE.

    **Observable:** ``clean_repo_fp_applicable`` and ``measurement_note``. **The defect:**
    ``_is_clean_repo`` needs an empty golden key AND ``max_blocking == 0``; a
    repository-corpus member has neither, so ``clean_repo_fp`` was 0 by construction on the
    population that gates externalization — and 0 is what §5 requires. **Adversarial
    variant, GENERATED from the live registry:** the population of cartridges that carry a
    golden key is folded on its own, which is structurally the shape of the repository
    corpus, and the condition must declare itself inapplicable over it.
    """
    full = compute_precision(_perfect_emission())
    assert full.clean_repo_fp_applicable is True, (
        "the CARTRIDGE corpus does contain clean members, so the condition IS measurable "
        "there and must keep saying so — this is not a licence to disable it"
    )
    assert "clean member(s)" in full.measurement_note

    labelled_only = tuple(spec for spec in CARTRIDGE_REGISTRY if spec.required_findings)
    assert len(labelled_only) >= 3, (
        f"non-vacuity: the generated golden-key-bearing population holds "
        f"{len(labelled_only)} member(s)"
    )
    shaped_like_a_repo_corpus = compute_precision(
        {
            spec.cartridge_id: frozenset(
                golden_match_key(gf) for gf in spec.required_findings
            )
            for spec in labelled_only
        },
        registry=labelled_only,
    )
    assert shaped_like_a_repo_corpus.clean_repo_fp == 0, (
        "the reproduction requires the count to be zero — the point is WHY it is zero"
    )
    assert shaped_like_a_repo_corpus.clean_repo_fp_applicable is False, (
        "a population with no clean member cannot fail this condition, so reporting it "
        "as satisfied is a false green: it must be NOT APPLICABLE with a reason"
    )
    assert "NOT APPLICABLE" in shaped_like_a_repo_corpus.measurement_note
    assert "BY CONSTRUCTION" in shaped_like_a_repo_corpus.measurement_note


def test_TC_ArgusAgent_PRECISION_001_38_the_flip_still_requires_all_four_conditions() -> None:
    """TC-ArgusAgent-PRECISION-001-38 — AC1/OI1: the repairs did not make the gate unflippable.

    **Observable:** the shared ``gate_is_provisional`` predicate over every combination of
    its four inputs. A repair that simply pinned ``provisional`` to ``True`` would satisfy
    every guard above and destroy the instrument, so the flip path is proven REACHABLE —
    and proven to need all four: floor met, protocol recorded cleared by the caller, a
    precision number actually COMPUTED, and that number ≥ 4/5.
    """
    combos = 0
    flipped = 0
    for n in (4, 5):
        for cleared in (False, True):
            for precision in (None, Fraction(3, 4), Fraction(4, 5)):
                provisional = gate_is_provisional(
                    n=n,
                    floor_n=VALIDATION_SET_FLOOR_N,
                    protocol_cleared=cleared,
                    precision=precision,
                )
                combos += 1
                expected = not (
                    n >= VALIDATION_SET_FLOOR_N
                    and cleared
                    and precision is not None
                    and precision >= PRECISION_GATE_THRESHOLD
                )
                assert provisional is expected, (n, cleared, precision)
                flipped += 0 if provisional else 1
    assert combos == 12, f"non-vacuity: {combos} combinations exercised"
    assert flipped == 1, (
        f"exactly ONE of the 12 combinations may flip the gate (N>=floor + cleared + a "
        f"computed precision >= 4/5); {flipped} did"
    )
