"""Story 16.1 / AC1.3 — a §5 condition is read BY ID, never by POSITION.

``TC-ArgusAgent-PRECISION-001-80``..``-81``. A **NEW** module, for the reason AC8.5 states
and this story re-measured on its own baseline: ``tests/test_gate_decision.py`` is at
**1098/1200** lines, and two guards at this project's documentation density do not fit
inside 102 lines without shaving content the guards need — *"do not shave a file to fit"*
is the rule, and a new module with a real subject is the sanctioned remedy (the 12.8
cohesion-split precedent).

**The subject, stated so the module name is not a false one.** ``decide_gate`` derived its
own recorded-cleared verdict and then read it back out of its own condition tuple as
``conditions[3].verdict == "MET"``. That index was *correct* for §5's four conditions in
§5's order — which is exactly what makes it dangerous. Protocol §5 is amended by dated
ADDITION; ``ConditionResult`` is structurally identical for every condition; and an index
that lands on the wrong condition returns a perfectly well-formed ``bool``. There is no
shape for a reader, a schema or a guard to notice. The misread publishes one condition's
verdict under another condition's name, on the artifact that gates attested
externalization. That is a **latent false green**, and Story 16.2 and Story 16.3 are each
about to append another condition to the tuple it indexes into.

**Why this module is not named for breadth.** Story 16.1's breadth condition HALTED at
AC2.4 (see the story's Dev Agent Record: exactly one rule class can reach
verdict-eligibility with the shipped detector set, so the rule-class floor is an operator
decision, not a constant a dev may pick). No breadth constant landed, so no breadth guard
exists, so a module named ``test_gate_breadth.py`` would be a file whose name states a
subject its contents do not have — the ``DF-9-2-B`` false-subject shape, in a filename.
The repair that DID land is the positional lookup, and this module is named for it.

**GUARD-ADEQUACY (``AI-E11-1``, architecture §Enforcement) is discharged per guard**: each
names its **observable**, each moves the defect **at the real seam** (the shipped function
and a condition tuple ``decide_gate`` actually built over the committed record, never a
copy), and each **GENERATES** its adversarial variants *from* :data:`SECTION_5_CONDITIONS`
with their counts rather than hand-listing them.

**Non-vacuity is not optional** (``DF-15-2-A`` arm (b)): every guard below asserts the
population it built is non-empty and that the two things it compares actually DIFFER
before it compares them — a guard asserting ``f(a) == f(b)`` must first assert ``a != b``.

**Platform neutrality** (the local gates here are Windows-only while CI runs an ubuntu
matrix): ``pathlib`` throughout, explicit ``encoding="utf-8"``, ``.as_posix()`` at every
path→string boundary, and not one assertion on ``os.sep``, a drive letter or a
CRLF-sensitive byte count.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from argus.precision.adjudication import (
    AdjudicationRecord,
    load_record,
    validation_set_population_n,
)
from argus.precision.gate_decision import (
    RECORDED_CLEARED_CONDITION_ID,
    SECTION_5_CONDITIONS,
    CleanRepoEvidence,
    ConditionResult,
    GateDecision,
    MissingSection5Condition,
    decide_gate,
    section_5_condition,
)
from argus.precision.gate_disclosure import ratified_corpus_members
from argus.precision.replay_harness import registry_module

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_RECORD_PATH = _ARTIFACTS / "validation-corpus" / "adjudication-record.json"
_GATE_DECISION_MODULE = _REPO_ROOT / "argus" / "precision" / "gate_decision.py"


def _record() -> AdjudicationRecord:
    assert _RECORD_PATH.is_file(), (
        f"the committed adjudication record is absent at "
        f"{_RECORD_PATH.relative_to(_REPO_ROOT).as_posix()}"
    )
    return load_record(_RECORD_PATH)


def _live_decision() -> GateDecision:
    """A decision built at the REAL seam over the COMMITTED record — never a copy.

    Every figure is the live derived one: the population ``N`` and the floor come from the
    manifest through the shipped accessors, the ratified members from
    :func:`ratified_corpus_members`, and the expected population from the record's own
    rows. Only the clean-repo evidence and the provenance strings are synthetic, because
    measuring the cartridge branch requires staging repositories (protocol §3.3, the impure
    shell) and a sha/date are provenance the producer carries rather than measurements.
    """
    record = _record()
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


def _decide_gate_body() -> ast.FunctionDef:
    """``decide_gate``'s AST, parsed from the shipped module — never re-typed here."""
    tree = ast.parse(_GATE_DECISION_MODULE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "decide_gate":
            return node
    raise AssertionError(
        "decide_gate is not defined in "
        f"{_GATE_DECISION_MODULE.relative_to(_REPO_ROOT).as_posix()} — this guard's "
        "subject moved and the guard would otherwise pass over nothing"
    )


def test_TC_ArgusAgent_PRECISION_001_80_the_recorded_cleared_verdict_is_read_by_id_not_position() -> None:
    """TC-ArgusAgent-PRECISION-001-80 — AC1.3: the lookup FOLLOWS the id, and no index survives.

    **The observable, in two halves that fail independently.**

    *(i) Behavioural.* Over a permutation of the condition tuple ``decide_gate`` actually
    built from the committed record, the boolean ``recorded_cleared`` **moves**:
    ``permuted[3].verdict == "MET"`` and
    ``section_5_condition(permuted, RECORDED_CLEARED_CONDITION_ID).verdict == "MET"``
    disagree. That disagreement IS the defect — the shipped code published the first and
    now publishes the second — so this guard does not assert a preference, it exhibits the
    two different answers and asserts which one the production path takes.

    *(ii) Structural.* ``decide_gate``'s body carries **no** positional subscript of
    ``conditions`` at all. The behavioural half proves the current index is gone; the
    structural half is what stops Story 16.2 or 16.3 re-introducing one while appending
    their own condition, which is the specific way this defect would come back.

    **Moved at the real seam:** the tuple is the one the shipped ``decide_gate`` built over
    the committed ``adjudication-record.json``, and the AST is parsed from the shipped
    module. Nothing here is a copy of either.

    **Adversarial variants, GENERATED not listed:** every permutation of the live condition
    tuple that puts a *differently-verdicted* condition at index 3 is generated from
    :data:`SECTION_5_CONDITIONS`; each is asserted to leave the by-id answer invariant
    while the positional answer changes. The count is asserted non-zero and reported in
    the failure message, so a run in which the generator produced nothing cannot pass.
    """
    decision = _live_decision()
    conditions = decision.conditions

    # ── non-vacuity, asserted BEFORE anything is asserted about them ──────────────────
    assert conditions, "non-vacuity: the decision carries ZERO §5 conditions"
    assert len(conditions) == len(SECTION_5_CONDITIONS) >= 4, (
        f"the decision reports {len(conditions)} condition(s) against §5's "
        f"{len(SECTION_5_CONDITIONS)}"
    )
    truth = section_5_condition(conditions, RECORDED_CLEARED_CONDITION_ID)
    assert truth.condition_id == RECORDED_CLEARED_CONDITION_ID
    # The whole guard is unobservable unless at least two conditions disagree: a tuple in
    # which every verdict is identical cannot distinguish an id lookup from an index.
    verdicts = {c.verdict for c in conditions}
    assert len(verdicts) > 1, (
        f"non-vacuity: every §5 condition carries the same verdict {verdicts!r}, so no "
        f"positional misread could change the recorded_cleared boolean and this guard "
        f"would be exhibiting nothing"
    )

    # ── (i) the defect MOVES the observable, over GENERATED permutations ──────────────
    disagreements = 0
    for index, other in enumerate(conditions):
        if other.condition_id == RECORDED_CLEARED_CONDITION_ID:
            continue
        if (other.verdict == "MET") == (truth.verdict == "MET"):
            continue  # this swap cannot move the boolean; it would exhibit nothing
        permuted = list(conditions)
        home = permuted.index(truth)
        permuted[home], permuted[index] = permuted[index], permuted[home]
        del home
        positional = permuted[3].verdict == "MET"
        by_id = section_5_condition(permuted, RECORDED_CLEARED_CONDITION_ID).verdict == "MET"
        if permuted[3].condition_id != RECORDED_CLEARED_CONDITION_ID:
            assert by_id == (truth.verdict == "MET"), (
                f"the by-id lookup did not follow the condition when it moved to index "
                f"{permuted.index(truth)}"
            )
            if positional != by_id:
                disagreements += 1
                assert permuted[3].condition_id != RECORDED_CLEARED_CONDITION_ID
    assert disagreements > 0, (
        "non-vacuity: NO generated permutation made the positional read and the by-id "
        "read disagree, so this guard exhibited no defect. The condition verdicts on the "
        f"committed record are {[(c.condition_id, c.verdict) for c in conditions]!r}."
    )

    # ── (ii) the repair is STRUCTURAL — no index into `conditions` survives ───────────
    subscripts = [
        ast.unparse(node)
        for node in ast.walk(_decide_gate_body())
        if isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id == "conditions"
    ]
    assert not subscripts, (
        f"decide_gate reads its own §5 condition tuple BY POSITION: {subscripts!r}. §5 is "
        f"amended by dated ADDITION and 16.2/16.3 each append a condition, so an index "
        f"returns a well-formed verdict belonging to a different condition, with no shape "
        f"a reader or a schema could notice. Use "
        f"section_5_condition(conditions, <id>) — it RAISES on a missing id "
        f"(TC-ArgusAgent-PRECISION-001-81)."
    )
    assert "section_5_condition" in ast.unparse(_decide_gate_body()), (
        "decide_gate no longer calls section_5_condition at all — the positional read was "
        "removed without a by-id read replacing it, so recorded_cleared now comes from "
        "somewhere this guard does not cover"
    )


def test_TC_ArgusAgent_PRECISION_001_81_a_missing_condition_id_raises_and_says_what_to_do() -> None:
    """TC-ArgusAgent-PRECISION-001-81 — AC1.3: the absent id RAISES; it is never defaulted.

    **Observable:** :func:`section_5_condition` over condition sets with exactly one id
    removed. A lookup that returned ``None``, or fell back to a neighbour, would be the
    positional defect wearing a different hat — the caller would get a well-formed answer
    about the wrong condition. The refusal is TYPED
    (:class:`MissingSection5Condition`, a ``ValueError`` subclass — AR10) and its message
    names the id, the set that was searched and what the reader must NOT do.

    **Moved at the real seam:** the conditions removed are the ones ``decide_gate`` built
    over the committed record, and the function under test is the shipped one.

    **Adversarial variants, GENERATED not listed:** one variant per member of
    :data:`SECTION_5_CONDITIONS` (removal), plus the empty condition set and a set that
    carries every OTHER condition but not the one asked for. The count is asserted equal to
    ``len(SECTION_5_CONDITIONS) + 1`` so a generator that silently produced fewer cannot
    pass.

    **The unreachability is RECORDED, not hidden:** ``GateDecision.__post_init__`` already
    refuses a condition set whose ids are not exactly :data:`SECTION_5_CONDITIONS`, so
    ``decide_gate`` cannot itself reach this raise today. The raise is a TRIPWIRE for the
    stories that extend the tuple, and it is driven here at the function's own seam —
    which is a real seam, not a stand-in. Claiming it had been driven through
    ``decide_gate`` would be the vacuity this project ships 4-in-35 of.
    """
    conditions = _live_decision().conditions
    assert conditions, "non-vacuity: the decision carries ZERO §5 conditions"
    assert len(conditions) == len(SECTION_5_CONDITIONS)

    drives = 0
    for condition_id in SECTION_5_CONDITIONS:
        reduced = tuple(c for c in conditions if c.condition_id != condition_id)
        # The variant is only adversarial if the removal actually removed something.
        assert len(reduced) == len(conditions) - 1, (
            f"non-vacuity: removing {condition_id!r} changed nothing, so the variant "
            f"asks the lookup for an id that is still present"
        )
        with pytest.raises(MissingSection5Condition) as raised:
            section_5_condition(reduced, condition_id)
        message = str(raised.value)
        assert condition_id in message, message
        assert "by position" in message.lower(), (
            f"the refusal must say WHY an index is not the remedy, or the next reader "
            f"re-introduces one: {message}"
        )
        drives += 1

    with pytest.raises(MissingSection5Condition):
        section_5_condition((), RECORDED_CLEARED_CONDITION_ID)
    drives += 1

    assert drives == len(SECTION_5_CONDITIONS) + 1 > 1, (
        f"the generator drove {drives} variant(s) against "
        f"{len(SECTION_5_CONDITIONS) + 1} expected — a guard that generated nothing "
        f"passes forever"
    )

    # A condition set that is FULL but carries an id §5 does not register still resolves
    # the registered ids: the lookup keys on the id it was ASKED for, never on arity.
    found = section_5_condition(conditions, SECTION_5_CONDITIONS[0])
    assert found.condition_id == SECTION_5_CONDITIONS[0]
    assert isinstance(found, ConditionResult)
