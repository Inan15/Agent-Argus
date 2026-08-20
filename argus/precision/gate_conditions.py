"""Protocol §5's CONDITIONS — what one is, how one is looked up, and the closed vocabulary.

Verification area ``TC-ArgusAgent-PRECISION-001-53``.. (``tests/test_gate_decision.py``,
``tests/test_gate_condition_lookup.py``). A cohesion split from
:mod:`argus.precision.gate_decision`, taken 2026-08-20 under Story 16.2 because
``DF-16-1-B`` filed that module as a **SPLIT-FIRST trigger** at 1,197 of NFR-M1's 1,200
lines and named 16.2's sixth §5 condition as the change that must perform the split first.
``tests/test_module_size_ceiling.py::_REMEDY`` states the shape: a cohesion boundary, a
module docstring naming why the module exists, no function split across the boundary, and
every import path unchanged — *"do NOT shave lines"*.

**Why the boundary is HERE.** Three layers were tangled in one file, and they are strictly
ordered:

1. **what a §5 condition IS** — this module: the closed verdict vocabulary, the registry of
   §5's condition ids, the by-id lookup, and the :class:`ConditionResult` value object;
2. **what a condition is MEASURED FROM** — :mod:`argus.precision.gate_evidence`: the two
   evidence objects a caller supplies to the decision;
3. **what the result IS** — :mod:`argus.precision.gate_decision`: the fold, the three-way
   dispatch and the committed record.

Each layer imports only downward, and every symbol below is re-exported from
:mod:`argus.precision.gate_decision`, so **not one import line anywhere in the repository
moved**. That is deliberate: it keeps the split reviewable as a pure move.

**Why not a single sibling holding both (1) and (2), as Story 16.2 §2.1 measured it.**
:meth:`gate_evidence.CleanRepoEvidence.condition` CONSTRUCTS a :class:`ConditionResult`,
whose ``__post_init__`` validates against :data:`SECTION_5_CONDITIONS`. Moving the two
evidence dataclasses alone leaves ``gate_evidence`` importing ``gate_decision`` while
``gate_decision`` imports ``gate_evidence`` — a cycle. The vocabulary layer is therefore
extracted as its own module rather than the method being relocated away from its class or
an import being deferred inside a method body to dodge the cycle. The alternative shape —
``gate_decision`` building the clean-repo ``ConditionResult`` the way it already builds the
breadth one (DN-16-1-3) — was rejected here because it would make the split a behaviour
change rather than a move, on the one commit whose whole value is that it is not one.

PURE (AR8) throughout: no I/O, no clock, no network, no repository-only path (``DF-9-2-A``).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from argus.precision.gate_breadth import BREADTH_CONDITION_ID
from argus.precision.gate_seal import SEAL_CONDITION_ID
from argus.precision.gate_yield import YIELD_CONDITION_ID

__all__ = [
    "CONDITION_VERDICTS",
    "RECORDED_CLEARED_CONDITION_ID",
    "SECTION_5_CONDITIONS",
    "ConditionResult",
    "MissingSection5Condition",
    "UnregisteredConditionVerdict",
    "condition_verdict_meaning",
    "section_5_condition",
]


class UnregisteredConditionVerdict(ValueError):
    """Raised on a per-condition verdict outside :data:`CONDITION_VERDICTS`."""


class MissingSection5Condition(ValueError):
    """Raised when a §5 condition is looked up BY ID and the decision does not carry it.

    A ``ValueError`` subclass (AR10) whose message says what a reader must do. This is the
    typed replacement for a POSITIONAL index into
    :attr:`GateDecision.conditions` — see :func:`section_5_condition` for why an index was
    a latent false green rather than a style preference.
    """


#: The CLOSED per-condition verdict vocabulary (DN-3). ``NOT_APPLICABLE`` is a member
#: because protocol §5's clean-repo condition genuinely is not applicable over the corpus
#: that gates externalization, and the amendment 13.2 wrote forbids counting it met by
#: default. It is deliberately NOT a synonym for ``MET``.
CONDITION_VERDICTS: dict[str, str] = {
    "MET": "the condition was evaluated over a named corpus and holds.",
    "FAILED": "the condition was evaluated over a named corpus and does NOT hold.",
    "NOT_APPLICABLE": (
        "the condition cannot fail over this corpus for any possible input, so evaluating "
        "it here measures nothing. RECORDED with its reason and its corpus — never "
        "counted as met. A §5 condition that cannot fail is not a threshold."
    ),
    "UNEVALUABLE": (
        "the condition could not be evaluated at all: a protocol §4 precondition "
        "(byte-reproducibility, exhaustive adjudication) does not hold, so any value "
        "reported here would rest on nothing. Recorded with the residual, never as a "
        "failure and never as a pass."
    ),
}

#: §5(4)'s id, named ONCE. :func:`decide_gate` reads this condition's verdict back out to
#: populate :attr:`GateDecision.adjudication_run_recorded_cleared`, and
#: :func:`_recorded_cleared_condition` writes it — so the id is a constant rather than two
#: string literals that can drift apart without anything noticing.
RECORDED_CLEARED_CONDITION_ID = "adjudication-run-recorded-cleared"

#: §5's four conditions, in §5's own order. The ids are stable and the record is keyed by
#: them, so a condition cannot be dropped from the report without the schema noticing.
#: §5 is amended by dated ADDITION, so a future condition is APPENDED and the historical
#: ids keep their historical positions — which is exactly why nothing may read this tuple
#: by POSITION (:func:`section_5_condition`).
SECTION_5_CONDITIONS: tuple[str, ...] = (
    "precision-at-least-80-percent",
    "clean-repo-blocking-false-positives-zero",
    "corpus-floor-n-at-least-5",
    RECORDED_CLEARED_CONDITION_ID,
    # AMENDED 2026-08-20 (Story 16.1; protocol §5's dated block of the same date). APPENDED,
    # never inserted next to precision: §5 is amended by dated ADDITION, the four historical
    # ids keep their historical positions, and the regenerated record's condition list is a
    # clean prefix-plus-one diff a reviewer can actually read. Nothing reads this tuple by
    # POSITION (:func:`section_5_condition`), which is what makes appending safe at all.
    BREADTH_CONDITION_ID,
    # AMENDED 2026-08-20 (Story 16.2; protocol §5's SECOND dated block of the same date).
    # APPENDED under the same rule DN-16-1-2 set: the five historical ids keep their
    # historical positions and the regenerated record's condition list is a clean
    # prefix-plus-one diff. §5 is amended by dated ADDITION and by nothing else — there is
    # no V1.4 row and there was no re-version, because the committed record carries 31 human
    # judgements made under V1.3 and re-stamping them would re-interpret judgements nobody
    # re-made (locked operator decision, XAgent007, 2026-08-20).
    SEAL_CONDITION_ID,
    # AMENDED 2026-08-20 (Story 16.3; protocol §5's THIRD dated block of the same date).
    # APPENDED under the rule DN-16-1-2 set and DN-16-2-2 reused: the six historical ids keep
    # their historical positions and the regenerated record's condition list is a clean
    # prefix-plus-one diff a reviewer can actually read. Still no V1.4 row and still no
    # re-version — the committed record's 31 human judgements were made under V1.3 and this
    # amendment touches no §4 rule, no golden-key semantics and no TP/FP definition, so not
    # one judgement's meaning moves (locked operator decision, XAgent007, 2026-08-20).
    #
    # ⛔ It is the SEVENTH and it is a floor on the DENOMINATOR of the precision ratio, not on
    # recall: `argus/precision/gate_yield.py` derives it from PRECISION_GATE_THRESHOLD alone,
    # carries no FN term, and a guard walks that module's own AST to keep it that way. Recall
    # stays ungated and diagnostic under the OI1 lock.
    YIELD_CONDITION_ID,
)


def condition_verdict_meaning(verdict: str) -> str:
    """The registered meaning of a per-condition *verdict* — RAISES on an unregistered one."""
    try:
        return CONDITION_VERDICTS[verdict]
    except KeyError:
        raise UnregisteredConditionVerdict(
            f"{verdict!r} is not a registered condition verdict. The closed vocabulary is "
            f"{sorted(CONDITION_VERDICTS)!r}."
        ) from None


def section_5_condition(
    conditions: Sequence["ConditionResult"], condition_id: str
) -> "ConditionResult":
    """The §5 condition with *condition_id* — BY ID, and RAISES when it is absent.

    **Why this exists at all.** :func:`decide_gate` used to read its own derived
    recorded-cleared verdict back out as ``conditions[3].verdict == "MET"``. That index was
    correct for §5's four conditions in §5's order and it is a LATENT FALSE GREEN, not a
    style question: §5 is amended by dated addition, the ``ConditionResult`` type is
    structurally identical for every condition, and an index that lands on the wrong
    condition returns a perfectly well-formed ``bool``. There is no shape for a reader —
    or a guard — to notice. Reading position 3 of a re-ordered tuple would publish one
    condition's verdict under another condition's name, on the record that gates attested
    externalization.

    Looking up by id converts that silent misread into a typed failure
    (:class:`MissingSection5Condition`), and the failure is DRIVEN rather than asserted:
    the lookup is exercised over a condition set with the id removed, which is the only
    way to know the raise is real.

    PURE (AR8): a lookup over a sequence, with no I/O and no clock.

    Raises:
        MissingSection5Condition: *condition_id* is carried by none of *conditions*.
    """
    for condition in conditions:
        if condition.condition_id == condition_id:
            return condition
    raise MissingSection5Condition(
        f"no §5 condition carries the id {condition_id!r}. The decision reported "
        f"{tuple(c.condition_id for c in conditions)!r} and §5 registers "
        f"{SECTION_5_CONDITIONS!r}. This lookup is BY ID and never by position, because a "
        f"positional index into a condition set that §5 amends by ADDITION silently "
        f"returns another condition's verdict under this condition's name. Re-check the "
        f"condition set the decision was built from; do NOT re-introduce an index."
    )


@dataclass(frozen=True)
class ConditionResult:
    """ONE protocol §5 condition, with its own measured value and its own verdict (DN-3).

    Reported individually and never collapsed into a conjunction. §5's clean-repo
    condition is currently ``NOT_APPLICABLE`` over the corpus that gates externalization;
    a single boolean would swallow that into a ``False`` — or, far worse, into a vacuous
    ``True`` — and the protocol amendment 13.2 wrote forbids exactly that.
    """

    condition_id: str
    requirement: str
    corpus: str
    measured: str
    verdict: str
    what_would_close_it: str

    def __post_init__(self) -> None:
        if self.condition_id not in SECTION_5_CONDITIONS:
            raise ValueError(
                f"{self.condition_id!r} is not one of protocol §5's conditions "
                f"{SECTION_5_CONDITIONS!r}. §5 enumerates {len(SECTION_5_CONDITIONS)} and "
                f"the record is keyed by them, so a further condition — or a renamed one — "
                f"is a protocol amendment, taken by a dated addition to §5 and never by an "
                f"edit here alone."
            )
        condition_verdict_meaning(self.verdict)
        if not self.what_would_close_it.strip():
            raise ValueError(
                f"{self.condition_id!r} carries no 'what would close it' clause. AC5 "
                f"requires every condition to name, in countable terms, what would move "
                f"it — a verdict with no closure path is a status, not a result."
            )

    def to_payload(self) -> dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "requirement": self.requirement,
            "corpus": self.corpus,
            "measured": self.measured,
            "verdict": self.verdict,
            "verdict_meaning": condition_verdict_meaning(self.verdict),
            "what_would_close_it": self.what_would_close_it,
        }
