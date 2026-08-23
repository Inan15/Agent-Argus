"""Story 16.5 — WHO judged the precision figure, and whether they were independent.

``TC-ArgusAgent-PRECISION-001-105``..``-112``. A **NEW** module, per AC5.1 and §0.5's
measurement: ``tests/test_gate_seal.py`` sits at **1,145 / 1,200** with ``DF-16-3-A`` OPEN
against a trigger of 1,180, and ``tests/test_gate_decision.py`` is full at this project's
guard density. *"Do not shave a file to fit"* is the rule (``MAINT-001``'s remedy), and
landing these guards anywhere else would spend ``DF-16-3-A``'s 55 lines by accident.

**The subject.** ``GateDecision`` has carried ``adjudicators`` since Story 13.3 and
published it under ``adjudication_record.adjudicators`` ever since. Measured at HEAD
``52143eb``: **ZERO** assertions anywhere in ``tests/**`` or ``scripts/**`` closed over that
field, and **no** surface rendered it beside the precision figure. A field no guard closes
over is a field that can go wrong without anything noticing — ``AI-E11-1``'s shape applied
to a disclosure rather than to a guard. These guards are what stop that.

⛔ **THIS STORY GATES NOTHING, AND ``-109`` IS WHAT PROVES IT.** ``SECTION_5_CONDITIONS``
stays at **SEVEN**, ``precision_evaluable`` keeps exactly **four** conjuncts, and flipping
the independence status through every member a NON-EMPTY adjudicator set can produce leaves
the outcome, the outcome reason, all seven condition verdicts, ``precision_evaluable`` and
``precision.meets_threshold`` **byte-identical**, in both directions.

**Why the populations are GENERATED, and how the LOCKSTEP TRAP is avoided (§2.8).** The
committed record carries exactly ONE distinct adjudicator, so a guard built only against it
would observe one vocabulary member, never see the status flip, and never notice if the
derivation were inverted. Stories 16.1, 16.2 and 16.3 each then hit the *next* trap: a
fixture in which two terms moved together, so the guard tested neither. Here the trap is
specific — *a population whose adjudicator set changes is usually also a population whose
size or member spread changes*. :func:`_population` therefore pins the member spread, the
size, the locators, the rule ids and the dispositions and varies **the adjudicator field and
nothing else**; :func:`_assert_differs_only_in_adjudicator` asserts that mechanically,
row by row, before any guard reasons about a difference.

**GUARD-ADEQUACY (architecture.md §Enforcement) is discharged per guard, in all three
parts:** each names its **observable**, each is shown moving the defect at the **REAL SEAM**
(the shipped ``decide_gate`` / ``precision_gate_status_for`` over real
:class:`AdjudicationRow` objects carried by the real committed
:class:`AdjudicationRecord` — never against a reconstruction), and each **GENERATES** its
adversarial variants from the committed record, from
:data:`~argus.precision.adjudication.PROTOCOL_ADJUDICATOR_ROLES` or from
:data:`~argus.precision.gate_independence.INDEPENDENCE_STATUSES`, with the count stated.
Every mutation run to discharge part (ii) was executed with ``PYTHONDONTWRITEBYTECODE=1``
and a cleared ``__pycache__``, the tree restored byte-exact afterwards and
``git status --porcelain`` confirmed empty — Story 16.2 recorded a false RED from a stale
cache and had to re-run everything.

**Non-vacuity is asserted FIRST in every guard** (``AI-E11-1`` / ``DF-15-2-A`` arm (b)): the
population built is non-empty, the values compared actually differ, and every vocabulary
member is asserted to have been REACHED by a generated population rather than merely to
exist.

**Platform neutrality** — the local gates here are Windows-only while CI runs an ubuntu
matrix: ``pathlib``, explicit ``encoding="utf-8"``, ``.as_posix()`` at every path→string
boundary, and no assertion on ``os.sep``, a drive letter or a CRLF-sensitive byte count.

⛔ **Nothing below is written to any committed artifact.** Every synthetic judgement lives
inside one test's local fixture. No detector runs, no bench member is ratified, no
disposition is written, no role is filled, and ``adjudication-record.json`` is read-only
input. ``DF-13-5-A``'s one pre-registered round stays **OPEN and UNSPENT**.
"""

from __future__ import annotations

import ast
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from argus.precision.adjudication import (
    DISPOSITIONS,
    PROTOCOL_ADJUDICATOR_ROLES,
    AdjudicationRecord,
    AdjudicationRow,
    UnregisteredAdjudicator,
    load_record,
    validation_set_population_n,
)
from argus.precision.gate_breadth import effective_precision_gate_status
from argus.precision.gate_conditions import CONDITION_VERDICTS, SECTION_5_CONDITIONS
from argus.precision.gate_decision import (
    GATE_OUTCOMES,
    CleanRepoEvidence,
    GateDecision,
    decide_gate,
)
from argus.precision.gate_disclosure import ratified_corpus_members
from argus.precision.gate_independence import (
    ENGINEERING_LEAD_ROLE,
    EXTERNAL_ADJUDICATOR_ROLE,
    INDEPENDENCE_STATUSES,
    QA_LEAD_ROLE,
    IndependenceAssessment,
    UnregisteredIndependenceStatus,
    assess_independence,
    independence_note,
    independence_status_meaning,
)
from argus.precision.gate_seal import sealed_precision_gate_status
from argus.precision.gate_yield import yielded_precision_gate_status
from argus.precision.replay_harness import (
    PRECISION_GATE_THRESHOLD,
    precision_gate_status_for,
    registry_module,
)

# The SEALED-population generator is IMPORTED, never copied (AR7 — the same reason
# tests/test_gate_breadth.py imports it rather than forking it). A population that can reach
# a §5 OUTCOME at all has to be built over the SEALED bench rows, and those live in the
# module that owns the partition.
from tests.test_gate_seal import sealed_corpus_members

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_RECORD_PATH = _ARTIFACTS / "validation-corpus" / "adjudication-record.json"
_ARGUS_TREE = _REPO_ROOT / "argus"
_CONDITIONS_MODULE = _REPO_ROOT / "argus" / "precision" / "gate_conditions.py"
_NEGATIVE_ASSURANCE = _REPO_ROOT / "argus" / "verdict" / "negative_assurance.py"
_DECISION_MODULE = _REPO_ROOT / "argus" / "precision" / "gate_decision.py"

#: The three synthetic adjudicator ids, one per registered role. The ROLE half of each is
#: taken from :data:`PROTOCOL_ADJUDICATOR_ROLES` rather than typed, so a role renamed in the
#: protocol renames it here too and cannot leave a fixture quietly asserting about a role
#: that no longer exists. ⛔ The QA Lead id is the real one protocol §2's 2026-08-22 dated
#: block registers, precisely so this fixture exercises the id shape the record would
#: actually carry — it attributes NOTHING real: not one row below is ever written anywhere.
_ENGINEERING_LEAD = f"XAgent007 ({ENGINEERING_LEAD_ROLE})"
_QA_LEAD = f"Veer Pratap Singh ({QA_LEAD_ROLE})"
_EXTERNAL = f"A. N. Other ({EXTERNAL_ADJUDICATOR_ROLE})"

#: Every adjudicator configuration a guard drives, keyed by the status it MUST derive to.
#: This mapping is the fixture half of ``-105``'s coverage claim: the keys are asserted
#: equal to ``set(INDEPENDENCE_STATUSES)``, so a fifth vocabulary member added without a
#: population that reaches it fails HERE rather than shipping unobserved (``AI-E11-1``).
_CONFIGURATIONS: dict[str, tuple[str, ...]] = {
    "NOT_ESTABLISHED": (),
    "NOT_INDEPENDENT": (_ENGINEERING_LEAD,),
    "SECOND_REVIEWER_INTERNAL": (_ENGINEERING_LEAD, _QA_LEAD),
    "EXTERNAL_ADJUDICATOR_PARTICIPATED": (_ENGINEERING_LEAD, _QA_LEAD, _EXTERNAL),
}

#: The NON-EMPTY members — AC4.3's inertness sweep, and its scope. ``NOT_ESTABLISHED`` is
#: EXCLUDED and the reason is a FOUND, PRE-EXISTING fact rather than a concession; see
#: :func:`test_TC_ArgusAgent_PRECISION_001_109_the_status_moves_no_gate_outcome`.
_NON_EMPTY_STATUSES: tuple[str, ...] = (
    "NOT_INDEPENDENT",
    "SECOND_REVIEWER_INTERNAL",
    "EXTERNAL_ADJUDICATOR_PARTICIPATED",
)


def _record() -> AdjudicationRecord:
    assert _RECORD_PATH.is_file(), (
        f"the committed adjudication record is absent at "
        f"{_RECORD_PATH.relative_to(_REPO_ROOT).as_posix()}"
    )
    return load_record(_RECORD_PATH)


def _sealed() -> list[str]:
    members = [str(member["member_id"]) for member in sealed_corpus_members()]
    assert members, "non-vacuity: the manifest reports ZERO sealed members"
    return members


def _population(
    adjudicators: tuple[str, ...],
    *,
    contributing_members: int,
    size: int,
    members: list[str] | None = None,
) -> AdjudicationRecord:
    """A judged population that varies ONLY in WHO judged it (§2.8, the lockstep trap).

    Built at the real seam — real :class:`AdjudicationRow` objects carried by the real
    committed :class:`AdjudicationRecord` (its protocol version, its reproducibility flag,
    its expert-hours), with only the ROWS replaced. The member spread, the size, the
    locators, the rule ids and the dispositions are functions of *contributing_members* and
    *size* ALONE, so two populations built with the same pair and different *adjudicators*
    differ in the adjudicator field and in nothing else — which
    :func:`_assert_differs_only_in_adjudicator` then asserts mechanically rather than
    trusting this docstring.

    Every row is a live ``TP`` judgement, so the fold is reproducible, exhaustive and above
    threshold, and breadth / seal / yield are moved only by the two size arguments.

    An EMPTY *adjudicators* tuple yields an all-``UNADJUDICATED`` population, which is the
    only shape an empty adjudicator set is constructible from: ``AdjudicationRow`` refuses a
    TP/FP/BORDERLINE row without a registered adjudicator. That population is necessarily
    NON-EXHAUSTIVE — see ``-109``.
    """
    pool = _sealed() if members is None else members
    assert 1 <= contributing_members <= len(pool)
    assert size >= contributing_members
    human = bool(adjudicators)
    rows = tuple(
        AdjudicationRow(
            row_id=f"synthetic{index:04d}.0",
            member_id=pool[index % contributing_members],
            rule_id="vacuous_test_ast",
            verdict_eligible=True,
            advisory=False,
            locator=f"pkg/tests/test_synthetic_{index}.py:{index + 1}",
            disposition="TP" if human else "UNADJUDICATED",
            adjudicator=adjudicators[index % len(adjudicators)] if human else None,
            adjudicated_on="2026-08-17" if human else None,
            reason=(
                "synthetic fixture: exercises the instrument, adjudicates nothing real"
                if human
                else None
            ),
        )
        for index in range(size)
    )
    record = replace(_record(), rows=rows)
    live = record.live_rows()
    assert len(live) == size, "non-vacuity: the generated population lost rows"
    assert len({row.member_id for row in live}) == contributing_members, (
        "non-vacuity: the generated population does not carry the number of contributing "
        "members it claims, so every assertion over it would be about the wrong fixture"
    )
    return record


def _assert_differs_only_in_adjudicator(
    left: AdjudicationRecord, right: AdjudicationRecord
) -> None:
    """⛔ THE LOCKSTEP ASSERTION (§2.8). Two populations, one moving term.

    Everything except ``adjudicator`` (and the ``adjudicated_on`` / ``reason`` fields the
    row's own construction rule binds to it) is compared field by field and must be
    identical, and the adjudicator sets must actually DIFFER. A fixture in which the size or
    the member spread moved alongside the adjudicator would let a guard credit the wrong
    term with the flip — which is the trap 16.1, 16.2 and 16.3 each fell into once.
    """
    assert len(left.rows) == len(right.rows) > 0, "non-vacuity: empty or mismatched rows"
    pinned = ("row_id", "member_id", "rule_id", "verdict_eligible", "advisory", "locator")
    for a, b in zip(left.rows, right.rows):
        for field in pinned:
            assert getattr(a, field) == getattr(b, field), (
                f"lockstep: {field} moved alongside the adjudicator, so no guard over "
                f"these two populations can attribute a difference to independence"
            )
    lefts = {row.adjudicator for row in left.live_rows()} - {None}
    rights = {row.adjudicator for row in right.live_rows()} - {None}
    assert lefts != rights, (
        "non-vacuity: the two populations carry the SAME adjudicator set, so the term "
        "this comparison is about never moved"
    )


def _decide(
    record: AdjudicationRecord,
    *,
    corpus: tuple[dict[str, str], ...],
    per_finding: bool = False,
) -> GateDecision:
    """Drive the shipped :func:`decide_gate` — the REAL seam, never a reconstruction.

    Passing *corpus* ratifies nothing: ``decide_gate`` takes ``ratified_members`` as an
    argument, and protocol §6 R2 ratification is an operator act no agent performs.

    *per_finding* de-duplicates the expected population by ``finding_id``, preserving
    order. It defaults to ``False``, so every pre-existing caller passes byte-identical
    arguments and this parameter cannot move any guard that already existed. It exists for
    the ONE fixture that carries a SUPERSEDED row (``-114``): a correction and the row it
    strikes share a ``finding_id`` by construction, and the emitted finding population a
    real caller passes is per FINDING, never per ROW — so passing the row list there would
    hand ``exhaustiveness`` a duplicate no real record can produce.
    """
    expected = [row.finding_id for row in record.rows]
    if per_finding:
        expected = list(dict.fromkeys(expected))
    return decide_gate(
        record,
        expected_finding_ids=expected,
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
        ratified_members=corpus,
        record_is_tracked_in_git=True,
        commit_sha="0" * 40,
        decided_on="2026-08-17",
    )


def _cleared(adjudicators: tuple[str, ...]) -> GateDecision:
    """An otherwise-``CLEARED`` decision, parameterised ONLY by who judged it.

    5 contributing SEALED members against a breadth floor of 3 and a seal floor of 3, over 6
    live ``TP`` rows against a yield floor of 5. The outcome is asserted by the callers, not
    assumed here.
    """
    return _decide(_population(adjudicators, contributing_members=5, size=6),
                   corpus=sealed_corpus_members())


def _fixed_gate_kwargs(**overrides: object) -> dict[str, object]:
    """The one set of ``precision_gate_status_for`` inputs every branch guard shares."""
    kwargs: dict[str, object] = {
        "precision": Fraction(4, 5),
        "n": 5,
        "provisional": False,
        "protocol_path": "precision-validation-protocol.md",
        "floor_n": 5,
        "population_label": "eligible validation-set repositories",
        "evaluable": True,
        "unevaluable_reason": None,
    }
    kwargs.update(overrides)
    return kwargs


#: The three branch selectors of ``precision_gate_status_for``, keyed by the marker word the
#: branch opens with. DERIVED into the guards rather than restated in each one.
_BRANCHES: dict[str, dict[str, object]] = {
    "unevaluable": {"evaluable": False, "provisional": True},
    "provisional": {"provisional": True},
    "cleared": {},
}


def test_TC_ArgusAgent_PRECISION_001_105_the_status_vocabulary_is_closed_and_reached() -> None:
    """TC-ArgusAgent-PRECISION-001-105 — AC1.2 / AC5.3: a CLOSED vocabulary, every member reached.

    **Observable:** the member :func:`assess_independence` derives for a given adjudicator
    configuration, and whether :func:`independence_status_meaning` raises on a member the
    vocabulary does not register.

    **The defect MOVES it, at the real seam.** Mutation executed 2026-08-23 with
    ``PYTHONDONTWRITEBYTECODE=1`` and a cleared ``__pycache__``, on the shipped
    ``argus/precision/gate_independence.py``: collapsing ``_derive_status``'s empty-set arm
    into the Engineering-Lead arm — i.e. returning ``NOT_INDEPENDENT`` for an empty
    adjudicator set, the single most tempting simplification in this module — turns this
    guard **RED** on the ``NOT_ESTABLISHED`` assertion below. Replacing the raising lookup
    with ``INDEPENDENCE_STATUSES.get(status, "")`` turns it **RED** on the
    :func:`pytest.raises` block. The tree was restored byte-exact after each and
    ``git status --porcelain`` confirmed empty.

    **Adversarial variants, GENERATED rather than hand-written:** every registered member is
    perturbed into an id the vocabulary does not carry — lower-cased, suffixed, and prefixed
    — and the lookup must reject **all 12** (4 members x 3 perturbations), plus the empty
    string and a member of the NEIGHBOURING closed vocabulary
    (:data:`~argus.precision.gate_decision.GATE_OUTCOMES`), whose members are the ones a
    reader is likeliest to confuse this vocabulary with.
    """
    assert len(INDEPENDENCE_STATUSES) == 4, INDEPENDENCE_STATUSES
    assert set(_CONFIGURATIONS) == set(INDEPENDENCE_STATUSES), (
        "AI-E11-1: a vocabulary member no generated population reaches is itself a "
        "finding. Add the population, or remove the member."
    )
    for member, meaning in INDEPENDENCE_STATUSES.items():
        assert meaning.strip(), f"{member} carries no registered meaning"
        assert independence_status_meaning(member) == meaning

    reached: dict[str, IndependenceAssessment] = {}
    for expected, configuration in _CONFIGURATIONS.items():
        assessment = assess_independence(configuration)
        assert assessment.status == expected, (
            f"{configuration!r} derived {assessment.status!r}, expected {expected!r}"
        )
        reached[expected] = assessment
    assert set(reached) == set(INDEPENDENCE_STATUSES)

    # ⛔ AC1.2's non-collapse, asserted rather than assumed: *nothing was judged* and *the
    # author judged everything* are different findings and must not be the same member.
    assert reached["NOT_ESTABLISHED"].status != reached["NOT_INDEPENDENT"].status
    assert reached["NOT_ESTABLISHED"].adjudicators == ()
    assert reached["NOT_INDEPENDENT"].adjudicators == (_ENGINEERING_LEAD,)
    assert reached["NOT_ESTABLISHED"].roles_present == ()
    assert tuple(reached["NOT_ESTABLISHED"].roles_absent) == PROTOCOL_ADJUDICATOR_ROLES

    # AC1.4 — roles present and absent are a PARTITION of §2's own tuple, never re-typed.
    for assessment in reached.values():
        assert set(assessment.roles_present) | set(assessment.roles_absent) == set(
            PROTOCOL_ADJUDICATOR_ROLES
        )
        assert not set(assessment.roles_present) & set(assessment.roles_absent)

    variants = tuple(
        perturbed
        for member in INDEPENDENCE_STATUSES
        for perturbed in (member.lower(), f"{member}_", f"X{member}")
    )
    assert len(variants) == 12, len(variants)
    for perturbed in (*variants, "", *GATE_OUTCOMES):
        with pytest.raises(UnregisteredIndependenceStatus):
            independence_status_meaning(perturbed)

    # DF-10-4-E, one level down: an id §2 does not register RAISES rather than defaulting.
    for bogus in ("XAgent007", "XAgent007 (Chief Adjudicator)", "(Engineering Lead)", ""):
        with pytest.raises(UnregisteredAdjudicator):
            assess_independence((bogus,))


def test_TC_ArgusAgent_PRECISION_001_106_the_figure_and_the_note_cannot_be_separated() -> None:
    """TC-ArgusAgent-PRECISION-001-106 — AC2.1 / AC2.2 / AC2.4: all three branches, both directions.

    **Observable:** the bytes ``precision_gate_status_for`` returns — specifically whether
    the ``precision=`` surface and the independence clause appear TOGETHER, in each of its
    three return branches, including the ``cleared`` branch no production call site in this
    repository currently reaches.

    **The defect MOVES it, at the real seam** — the shipped
    ``argus/precision/replay_harness.py``, not a reconstruction. Two mutations, executed
    2026-08-23 with ``PYTHONDONTWRITEBYTECODE=1`` and a cleared ``__pycache__``, one per
    direction of AC2.4:

    * *figure without the note* — drop ``{who}`` from the ``cleared`` branch's f-string (the
      branch a dev is likeliest to forget, because nothing here reaches it): **RED** on the
      ``cleared`` assertion below.
    * *note without the figure* — replace ``precision={ratio}`` with ``precision=<withheld>``
      in the ``unevaluable`` branch: **RED** on the ``precision=4/5`` assertion below.

    The tree was restored byte-exact after each and ``git status --porcelain`` confirmed
    empty.

    **Adversarial variants, GENERATED from the vocabulary rather than hand-written:** the
    note for **every one of the 4** registered statuses is driven through **every one of the
    3** branches — **12** renders — and every one must carry both halves. A guard that
    checked one status on one branch would be green against a renderer that placed the note
    in the branch this repository happens to reach and nowhere else.
    """
    assert set(_BRANCHES) == {"unevaluable", "provisional", "cleared"}, _BRANCHES
    notes = {
        status: assess_independence(configuration).note
        for status, configuration in _CONFIGURATIONS.items()
    }
    assert len(notes) == 4 and all(notes.values()), "non-vacuity: a status rendered no note"

    rendered = 0
    for branch, overrides in _BRANCHES.items():
        bare = precision_gate_status_for(**_fixed_gate_kwargs(**overrides))  # type: ignore[arg-type]
        assert bare.startswith(branch), (branch, bare[:40])
        assert "precision=" in bare and "N=" in bare, bare
        # NFR-P1: the keyword OMITTED and the keyword passed as None are the same bytes, and
        # neither carries a clause. This is the inert default, asserted by rendering.
        assert bare == precision_gate_status_for(
            **_fixed_gate_kwargs(**overrides), independence_note=None  # type: ignore[arg-type]
        )
        assert "adjudication independence:" not in bare

        for status, note in notes.items():
            got = precision_gate_status_for(
                **_fixed_gate_kwargs(**overrides), independence_note=note  # type: ignore[arg-type]
            )
            rendered += 1
            assert got.startswith(branch), (branch, status, got[:40])
            # ⛔ BOTH HALVES, ON ONE STRING. This is the whole acceptance criterion: the two
            # facts must not be separable by copy-and-paste.
            assert "precision=" in got, (branch, status)
            assert f"precision={PRECISION_GATE_THRESHOLD.numerator}/" in got, (branch, status)
            assert note in got, (branch, status)
            assert status in got, (branch, status)
            # The note is ADDED to the bytes that were already there, never substituted
            # for them: the pre-16.5 sentence survives verbatim as a prefix.
            assert len(got) > len(bare), (branch, status)
            assert got.startswith(bare[:-1]), (branch, status)
    assert rendered == 12, rendered


def test_TC_ArgusAgent_PRECISION_001_107_there_is_still_exactly_one_status_renderer() -> None:
    """TC-ArgusAgent-PRECISION-001-107 — AC3.1: AR7's one renderer, walked over the tree.

    **Observable:** how many functions in ``argus/**`` emit the **``precision=`` surface** —
    the ``precision={ratio}`` / ``N=`` shape ``precision_gate_status_for`` emits in all three
    of its branches. That surface IS the guard predicate, and naming it is what keeps this
    walk from being either red on master or vacuous: shipped code renders several sentences
    *about* the gate which are not gate-status sentences.

    ⛔ **The exclusion set is NAMED, and each excluded sentence is ASSERTED TO STILL EXIST**,
    so the exclusion cannot silently swallow a real fork:

    * ``ConditionResult.measured`` on any of the SEVEN §5 conditions — including §5(4)'s
      attributed sentence at ``gate_decision.py``, which NAMES the adjudicators and carries
      no precision figure. It is pre-existing, it is correct, and this story neither routes
      through it nor weakens it;
    * ``breadth_blocked_reason`` / ``seal_blocked_reason`` / ``yield_blocked_reason``, which
      render **outcome reasons**, not status;
    * this story's own note renderer in ``gate_independence.py``, which renders a CLAUSE for
      ``precision_gate_status_for`` to place and never a status sentence of its own.

    **The defect MOVES it, at the real seam.** Mutation executed 2026-08-23 with
    ``PYTHONDONTWRITEBYTECODE=1`` and a cleared ``__pycache__``: a second function emitting
    the ``precision=`` surface was added to the shipped
    ``argus/precision/gate_independence.py`` — the module this story adds, i.e. the module a
    fork would most plausibly appear in — and this guard went **RED** naming it. The tree was
    restored byte-exact and ``git status --porcelain`` confirmed empty.

    **Adversarial variant, GENERATED from the live tree:** the walk is re-run over every
    ``argus/**`` module with the predicate INVERTED, and the count of functions that emit
    ``precision=`` without ``N=`` (and vice versa) is asserted to be zero — proving the
    conjunction is not silently carrying the walk.
    """
    modules = sorted(_ARGUS_TREE.rglob("*.py"))
    assert len(modules) >= 50, (
        f"non-vacuity: the tree walk enumerated only {len(modules)} module(s); a truncated "
        f"population makes this guard silent rather than green"
    )

    def _literals(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        body = node.body
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            body = body[1:]
        return "".join(
            literal.value
            for statement in body
            for literal in ast.walk(statement)
            if isinstance(literal, ast.Constant) and isinstance(literal.value, str)
        )

    renderers: list[str] = []
    half: list[str] = []
    functions = 0
    for path in modules:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            functions += 1
            text = _literals(node)
            where = f"{path.relative_to(_REPO_ROOT).as_posix()}::{node.name}"
            if "precision=" in text and "N=" in text:
                renderers.append(where)
            elif "precision=" in text or ("N=" in text and "precision" in text):
                half.append(where)
    assert functions >= 200, f"non-vacuity: only {functions} function(s) walked"
    assert renderers == ["argus/precision/replay_harness.py::precision_gate_status_for"], (
        "AR7: a SECOND function in argus/** renders the precision= gate-status surface. "
        "One arithmetic, one renderer, never forked — a second one silently diverges the "
        f"day the first one's wording changes. Found: {renderers!r}"
    )
    assert not half, (
        f"a function emits half the precision= surface, which the conjunction above would "
        f"miss: {half!r}"
    )

    # ⛔ The exclusion set, each member ASSERTED TO STILL EXIST and to carry NO precision
    # figure — so "excluded" can never quietly mean "deleted, and nobody noticed".
    decision_source = _DECISION_MODULE.read_text(encoding="utf-8")
    attributed = "recorded cleared: run attributed to "
    assert attributed in decision_source, (
        "§5(4)'s attributed sentence is GONE. It pre-dates Story 16.5, it is correct, and "
        "16.5 neither routes through it nor removes it (§0.7)."
    )
    for reason in ("breadth_blocked_reason", "seal_blocked_reason", "yield_blocked_reason"):
        assert f"def {reason}(" in "".join(
            p.read_text(encoding="utf-8") for p in modules
        ), f"{reason} is gone — the exclusion set names a sentence that no longer exists"

    # This story's own clause renderer: a clause, not a status sentence. Asserted by
    # RENDERING it, not by reading the source.
    clause = assess_independence((_ENGINEERING_LEAD,)).note
    assert "precision=" not in clause and "N=" not in clause, clause


def test_TC_ArgusAgent_PRECISION_001_108_the_note_rides_on_every_renderer_branch() -> None:
    """TC-ArgusAgent-PRECISION-001-108 — AC2.3: all FOUR renderers, selected by construction.

    **Observable:** whether ``GateDecision.precision_gate_status`` carries the independence
    clause on each of the four renderers its branch set can return — ``fold.gate_status``,
    ``effective_precision_gate_status``, ``sealed_precision_gate_status`` and
    ``yielded_precision_gate_status``. ⛔ **None of the four renders in ``gate_decision.py``**:
    each is a ``precision_gate_status_for`` call inside another module, and all three arm
    renderers SHORT-CIRCUIT on ``return fold.gate_status``. A keyword added to
    ``precision_gate_status_for`` alone reaches none of them.

    **Selected by CONSTRUCTION, never by whichever branch the committed record happens to
    reach.** Today ``breadth_holds`` is ``false``, so the live path is
    ``effective_precision_gate_status`` and a guard built against the committed record would
    observe exactly one of the four. Each population below is generated to fail exactly the
    arm that selects its branch, with the floors (breadth 3, seal 3, yield 5) read from the
    shipped derivations rather than typed.

    **The defect MOVES it, at the real seam.** Mutation executed 2026-08-23 with
    ``PYTHONDONTWRITEBYTECODE=1`` and a cleared ``__pycache__``: dropping
    ``independence_note=who`` from the ``sealed_precision_gate_status`` call in the shipped
    ``GateDecision.precision_gate_status`` — one of the three forwards, and the one no
    production path exercises — turns this guard **RED** on the ``seal`` branch and on
    NOTHING else, which is what proves the four branches are genuinely being distinguished.
    Tree restored byte-exact; ``git status --porcelain`` empty.

    **Adversarial variant, GENERATED:** every one of the **4** branches is driven for **each
    of the 3** non-empty vocabulary members — **12** decisions — and each is asserted to
    carry that member's own clause, not merely some clause.
    """
    ratified = ratified_corpus_members()
    observed: dict[str, str] = {}
    for status in _NON_EMPTY_STATUSES:
        configuration = _CONFIGURATIONS[status]
        note = assess_independence(configuration).note
        # fold.gate_status — breadth, seal and yield ALL hold, so all three short-circuit.
        fold_branch = _cleared(configuration)
        # effective_precision_gate_status — 2 contributing members against a floor of 3.
        breadth_branch = _decide(
            _population(configuration, contributing_members=2, size=6),
            corpus=sealed_corpus_members(),
        )
        # sealed_precision_gate_status — 3 RATIFIED (all pre-seal) members: breadth holds,
        # the seal does not.
        seal_branch = _decide(
            _population(configuration, contributing_members=3, size=6, members=[
                str(member["member_id"]) for member in ratified
            ]),
            corpus=ratified,
        )
        # yielded_precision_gate_status — 3 sealed members but only 4 rows against a yield
        # floor of 5: breadth and the seal hold, the yield floor does not.
        yield_branch = _decide(
            _population(configuration, contributing_members=3, size=4),
            corpus=sealed_corpus_members(),
        )

        assert fold_branch.outcome == "CLEARED", fold_branch.outcome_reason
        assert fold_branch.precision_gate_status == fold_branch.fold.gate_status
        assert breadth_branch.breadth is not None and not breadth_branch.breadth.holds
        assert seal_branch.seal is not None and not seal_branch.seal.holds
        assert seal_branch.breadth is not None and seal_branch.breadth.holds
        assert yield_branch.yield_ is not None and not yield_branch.yield_.holds
        assert yield_branch.breadth is not None and yield_branch.breadth.holds
        assert yield_branch.seal is not None and yield_branch.seal.holds

        branches = {
            "fold": fold_branch,
            "breadth": breadth_branch,
            "seal": seal_branch,
            "yield": yield_branch,
        }
        # Each re-render is asserted to BE the arm renderer's own output, so this guard is
        # about the four renderers rather than about four decisions that happen to differ.
        assert breadth_branch.precision_gate_status == effective_precision_gate_status(
            fold=breadth_branch.fold,
            breadth=breadth_branch.breadth,
            protocol_path=breadth_branch.protocol_path,
            independence_note=note,
        )
        assert seal_branch.precision_gate_status == sealed_precision_gate_status(
            fold=seal_branch.fold,
            seal=seal_branch.seal,
            protocol_path=seal_branch.protocol_path,
            independence_note=note,
        )
        assert yield_branch.precision_gate_status == yielded_precision_gate_status(
            fold=yield_branch.fold,
            detector_yield=yield_branch.yield_,
            protocol_path=yield_branch.protocol_path,
            independence_note=note,
        )
        for name, decision in branches.items():
            status_line = decision.precision_gate_status
            assert note in status_line, (status, name)
            assert "precision=" in status_line and "N=" in status_line, (status, name)
            observed[f"{status}/{name}"] = status_line
        # the four are genuinely four: no two branches rendered the same sentence
        assert len({d.precision_gate_status for d in branches.values()}) == 4, status
    assert len(observed) == 12, len(observed)


def test_TC_ArgusAgent_PRECISION_001_109_the_status_moves_no_gate_outcome() -> None:
    """TC-ArgusAgent-PRECISION-001-109 — AC4.3: the inertness proof, DRIVEN rather than argued.

    **Observable:** ``outcome``, ``outcome_reason``, all SEVEN condition verdicts,
    ``precision_evaluable`` and ``precision.meets_threshold``, over two populations — one
    constructed to be otherwise ``CLEARED`` and one ``BLOCKED`` — as the independence status
    is flipped through every member a NON-EMPTY adjudicator set can produce. All of them must
    be **byte-identical**. Both directions.

    ⛔ **``NOT_ESTABLISHED`` IS EXCLUDED FROM THIS SWEEP, AND THE REASON IS A FOUND,
    PRE-EXISTING FACT — not a concession and not something this story added.** Reaching
    ``NOT_ESTABLISHED`` means an EMPTY adjudicator set, which is only CONSTRUCTIBLE when every
    live row is ``UNADJUDICATED``: ``AdjudicationRow.__post_init__`` calls
    ``adjudicator_role(self.adjudicator or "")`` for every disposition in
    ``HUMAN_DISPOSITIONS`` and RAISES on an empty or unregistered id, so a human-judged row
    cannot exist without a registered adjudicator. An all-``UNADJUDICATED`` record is
    NON-EXHAUSTIVE, so ``decide_gate`` BLOCKS on **exhaustiveness** — which PRECEDES both the
    empty-denominator branch and §5(4). The ``outcome_reason`` and closure path observed on
    that population are therefore the EXHAUSTIVENESS ones. Separately, §5(4)
    ``_recorded_cleared_condition`` has taken ``adjudicators`` and failed on an empty set
    since Story 13.3; that coupling PRE-DATES this story, and 16.5 neither adds, removes nor
    strengthens it. ``-110`` asserts the ``NOT_ESTABLISHED`` population's derived STATUS,
    which is what this story owns; asserting gate inertness there would go red for a reason
    with nothing to do with independence.

    **The defect MOVES it, at the real seam.** Mutation executed 2026-08-23 with
    ``PYTHONDONTWRITEBYTECODE=1`` and a cleared ``__pycache__``: adding
    ``and (self.independence is None or self.independence.status != "NOT_INDEPENDENT")`` as a
    FIFTH conjunct of the shipped ``GateDecision.precision_evaluable`` — the exact one-line
    edit a dev could make while "being consistent" with the three §5 arms that landed
    immediately before this story — turns this guard **RED** on the ``CLEARED`` population.
    Tree restored byte-exact; ``git status --porcelain`` empty.

    **Adversarial variants, GENERATED from the vocabulary:** the sweep is driven over **3**
    non-empty members x **2** populations = **6** decisions, and the invariants are compared
    pairwise across all 3 members of each population — **and the fixtures are first asserted
    to differ ONLY in the adjudicator field**, so a lockstep fixture cannot make this pass.
    """
    def _invariants(decision: GateDecision) -> tuple[object, ...]:
        return (
            decision.outcome,
            decision.outcome_reason,
            tuple((c.condition_id, c.verdict) for c in decision.conditions),
            decision.precision_evaluable,
            decision.fold.meets_threshold,
            decision.closure_path,
        )

    populations: dict[str, dict[str, GateDecision]] = {"CLEARED": {}, "BLOCKED": {}}
    fixtures: dict[str, AdjudicationRecord] = {}
    for status in _NON_EMPTY_STATUSES:
        configuration = _CONFIGURATIONS[status]
        cleared = _cleared(configuration)
        assert cleared.outcome == "CLEARED", cleared.outcome_reason
        populations["CLEARED"][status] = cleared
        fixtures[status] = _population(configuration, contributing_members=5, size=6)

        # The BLOCKED population: the REAL committed rows, re-attributed. Dispositions,
        # locators, members and counts are the committed ones; only WHO judged moves.
        live_record = _record()
        assert len(live_record.rows) == 31, len(live_record.rows)
        rows = tuple(
            replace(row, adjudicator=configuration[index % len(configuration)])
            if row.is_human_judgement
            else row
            for index, row in enumerate(live_record.rows)
        )
        blocked = _decide(replace(live_record, rows=rows), corpus=ratified_corpus_members())
        assert blocked.outcome == "BLOCKED", blocked.outcome_reason
        populations["BLOCKED"][status] = blocked

    # ⛔ The lockstep assertion FIRST: the three CLEARED fixtures differ in the adjudicator
    # field and in nothing else, so any difference below is attributable to independence.
    _assert_differs_only_in_adjudicator(
        fixtures["NOT_INDEPENDENT"], fixtures["SECOND_REVIEWER_INTERNAL"]
    )
    _assert_differs_only_in_adjudicator(
        fixtures["SECOND_REVIEWER_INTERNAL"], fixtures["EXTERNAL_ADJUDICATOR_PARTICIPATED"]
    )

    for label, byStatus in populations.items():
        assert len(byStatus) == 3, (label, len(byStatus))
        # Non-vacuity, the direction that matters: the term this guard is about DID move.
        derived = {d.independence.status for d in byStatus.values() if d.independence}
        assert derived == set(_NON_EMPTY_STATUSES), (label, derived)
        # ...and the published SENTENCE moved with it, so the fixtures are not inert overall.
        assert len({d.precision_gate_status for d in byStatus.values()}) == 3, label
        # ...while every gate-bearing invariant did NOT.
        invariants = {status: _invariants(d) for status, d in byStatus.items()}
        assert len(set(invariants.values())) == 1, (
            f"{label}: the independence status MOVED a gate-bearing value. This story is a "
            f"DISCLOSURE and gates nothing, in either direction, for any population. "
            f"Observed: {invariants!r}"
        )
        for decision in byStatus.values():
            assert len(decision.conditions) == len(SECTION_5_CONDITIONS) == 7


def test_TC_ArgusAgent_PRECISION_001_110_not_established_is_reached_and_does_not_collapse() -> None:
    """TC-ArgusAgent-PRECISION-001-110 — AC5.3: the empty-set member, reached over a real decision.

    **Observable:** the status ``decide_gate`` derives over a population whose live rows are
    all ``UNADJUDICATED`` — the ONLY shape an empty adjudicator set is constructible from —
    and whether it collapses into ``NOT_INDEPENDENT``.

    ⛔ **This population is NECESSARILY ``BLOCKED``, for a reason that PRE-DATES this story**,
    and the guard asserts the DERIVED STATUS here, never gate inertness (that is ``-109``'s
    excluded case). ``AdjudicationRow`` refuses a TP/FP/BORDERLINE row without a registered
    adjudicator, so an empty set implies every live row is ``UNADJUDICATED``, which makes the
    record NON-EXHAUSTIVE, so ``decide_gate`` blocks on **exhaustiveness** — AHEAD of both the
    empty-denominator branch and §5(4). ⛔ The ``outcome_reason`` asserted below is therefore
    the EXHAUSTIVENESS one, measured rather than assumed.

    **The defect MOVES it, at the real seam.** The ``_derive_status`` collapse mutation
    described in ``-105`` also turns THIS guard **RED**, on the live ``decide_gate`` path
    rather than on the pure function — which is the point of asserting it twice at two
    different seams. Executed 2026-08-23 with ``PYTHONDONTWRITEBYTECODE=1``; tree restored
    byte-exact; ``git status --porcelain`` empty.

    **Adversarial variant, GENERATED:** the same population is rebuilt at **3** sizes
    (4, 6 and 8 rows), and every one must derive ``NOT_ESTABLISHED`` — so the member cannot
    be an artefact of one row count.
    """
    seen = set()
    for size in (4, 6, 8):
        record = _population((), contributing_members=3, size=size)
        live = record.live_rows()
        assert len(live) == size, "non-vacuity: the population lost rows"
        assert all(row.disposition == "UNADJUDICATED" for row in live)
        assert all(row.adjudicator is None for row in live)

        decision = _decide(record, corpus=sealed_corpus_members())
        assert decision.independence is not None
        assert decision.independence.status == "NOT_ESTABLISHED", decision.independence
        # ⛔ AC5.3's non-collapse: *nothing was judged* is not *the author judged everything*.
        assert decision.independence.status != "NOT_INDEPENDENT"
        assert decision.adjudicators == ()
        assert decision.independence.adjudicators == ()

        # The BLOCKED reason is the pre-existing EXHAUSTIVENESS one, measured not assumed.
        assert decision.outcome == "BLOCKED"
        assert "NOT exhaustively adjudicated" in decision.outcome_reason, decision.outcome_reason
        assert "denominator is empty" not in decision.outcome_reason
        assert decision.independence.note in decision.precision_gate_status
        seen.add(decision.independence.status)
    assert seen == {"NOT_ESTABLISHED"}, seen


def test_TC_ArgusAgent_PRECISION_001_111_the_fenced_vocabularies_are_byte_unchanged() -> None:
    """TC-ArgusAgent-PRECISION-001-111 — AC3.2 / AC4.1 / AC4.2 / AC4.4: the constants, BY VALUE.

    **Observable:** every threshold, floor and closed vocabulary §2.1 fences, asserted **by
    value in one place** and against **the module it actually lives in** — because two of
    them are not where a reader would guess (``VALIDATION_SET_FLOOR_N`` lives in
    ``tests/cartridges/_registry.py``, and ``PROTOCOL_ADJUDICATOR_ROLES`` / ``DISPOSITIONS``
    live in ``adjudication.py``, which Story 16.5 WIDENED and therefore no longer
    whole-module fences).

    **The defect MOVES it, at the real seam.** Mutation executed 2026-08-23 with
    ``PYTHONDONTWRITEBYTECODE=1`` and a cleared ``__pycache__``: appending an EIGHTH member
    to the shipped ``SECTION_5_CONDITIONS`` — the single most consequential thing a dev
    could do in this story, because the three stories immediately before it each appended a
    §5 condition and the pattern-match is strong — turns this guard **RED** on the count and
    on the ``__post_init__`` order assertion. Adding a fifth conjunct to
    ``precision_evaluable`` turns it **RED** on the ``ast`` count. Tree restored byte-exact;
    ``git status --porcelain`` empty.

    **Adversarial variant, GENERATED from the AST rather than from a literal:** the conjunct
    count is COUNTED out of the shipped ``precision_evaluable`` body by walking its
    ``ast.BoolOp``, not compared against a number someone typed — so a fifth conjunct written
    in any spelling is caught.
    """
    assert len(SECTION_5_CONDITIONS) == 7, SECTION_5_CONDITIONS
    assert len(set(SECTION_5_CONDITIONS)) == 7, "the §5 condition ids are not distinct"
    assert len(CONDITION_VERDICTS) == 4, CONDITION_VERDICTS
    assert len(GATE_OUTCOMES) == 3, GATE_OUTCOMES
    assert PROTOCOL_ADJUDICATOR_ROLES == (
        "Engineering Lead",
        "QA Lead",
        "External adjudicator",
    ), PROTOCOL_ADJUDICATOR_ROLES
    assert len(DISPOSITIONS) == 4, DISPOSITIONS
    assert PRECISION_GATE_THRESHOLD == Fraction(4, 5), PRECISION_GATE_THRESHOLD
    assert int(registry_module().VALIDATION_SET_FLOOR_N) == 5
    manifest = registry_module.__module__  # resolved lazily; the manifest is its sibling
    assert manifest, "non-vacuity: the lazy registry indirection did not resolve"
    from tests.corpus._manifest import MANIFEST_FIELDS  # noqa: PLC0415 - repository-only

    assert len(MANIFEST_FIELDS) == 9, MANIFEST_FIELDS

    # AC4.1 — gate_conditions.py owns the §5 vocabulary and Story 16.5 does not touch it.
    conditions_source = _CONDITIONS_MODULE.read_text(encoding="utf-8")
    assert "independence" not in conditions_source.lower(), (
        "argus/precision/gate_conditions.py names independence. This story adds NO eighth "
        "§5 condition; that module is byte-unchanged by it (AC4.1)."
    )

    # AC3.2 — FR34's InstrumentStatus stays a closed TWO-member vocabulary, un-merged.
    from argus.verdict.negative_assurance import INSTRUMENT_STATUS, InstrumentStatus

    assert len(tuple(InstrumentStatus)) == 2, tuple(InstrumentStatus)
    assert INSTRUMENT_STATUS is InstrumentStatus.NOT_INDEPENDENTLY_VALIDATED
    assurance_source = _NEGATIVE_ASSURANCE.read_text(encoding="utf-8")
    assert "gate_independence" not in assurance_source, (
        "argus/verdict/negative_assurance.py reaches this story's module. That vocabulary "
        "bounds the INSTRUMENT per tool VERSION; this one bounds ONE adjudication run "
        "(DN-16-5-2). Merging them repeats the confusion the enum's own docstring warns of."
    )

    # AC4.2 — exactly FOUR conjuncts, COUNTED out of the shipped source.
    tree = ast.parse(_DECISION_MODULE.read_text(encoding="utf-8"))
    evaluable = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "precision_evaluable"
    ]
    assert len(evaluable) == 1, "precision_evaluable is not a single function"
    boolops = [n for n in ast.walk(evaluable[0]) if isinstance(n, ast.BoolOp)]
    assert boolops, "non-vacuity: precision_evaluable carries no boolean expression"
    assert len(boolops[0].values) == 4, (
        f"GateDecision.precision_evaluable has {len(boolops[0].values)} conjuncts, not 4. "
        f"The independence arm is NEVER a conjunct of precision_evaluable and never a "
        f"branch of _precision_condition (§2.2). This story gates nothing."
    )
    # ...and no §5 condition builder mentions it either.
    assert "_precision_condition" in _DECISION_MODULE.read_text(encoding="utf-8")
    precision_condition = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_precision_condition"
    ]
    assert len(precision_condition) == 1
    assert "independence" not in ast.dump(precision_condition[0]), (
        "_precision_condition gained an independence branch (§2.2 / AC4.2)"
    )


def test_TC_ArgusAgent_PRECISION_001_112_the_disclosure_travels_as_structure_too() -> None:
    """TC-ArgusAgent-PRECISION-001-112 — AC2.5 / AC3.4 / AC4.5: the payload block and the fences.

    **Observable:** whether the independence status also appears as its OWN structured block
    on the payload (so a machine reader never parses the sentence), whether that block AGREES
    with the sentence, and whether the two surfaces this story deliberately does not touch —
    the dogfood generator and the cartridge fold — render byte-identically.

    **The defect MOVES it, at the real seam.** Mutation executed 2026-08-23 with
    ``PYTHONDONTWRITEBYTECODE=1`` and a cleared ``__pycache__``: dropping the
    ``"independence"`` key from the shipped ``GateDecision.to_payload`` turns this guard
    **RED** on the key assertion; passing ``independence_note=...`` into
    ``argus/dogfood/proof_run.py::derive_gate_status``'s ``precision_gate_status_for`` call —
    the DN-16-5-6 violation, i.e. publishing a sentence about a judgement that never happened
    — turns it **RED** on the dogfood assertion. Tree restored byte-exact;
    ``git status --porcelain`` empty.

    **Adversarial variant, GENERATED:** the payload block is re-derived for **each of the 4**
    vocabulary members and compared field by field against the assessment it came from, so a
    block that published a constant would fail on three of the four.
    """
    for status, configuration in _CONFIGURATIONS.items():
        assessment = assess_independence(configuration)
        payload = assessment.to_payload()
        assert payload["status"] == status
        assert payload["status_meaning"] == INDEPENDENCE_STATUSES[status]
        assert payload["adjudicators"] == list(assessment.adjudicators)
        assert payload["roles_present"] == list(assessment.roles_present)
        assert payload["roles_absent"] == list(assessment.roles_absent)
        assert payload["registered_roles"] == list(PROTOCOL_ADJUDICATOR_ROLES)
        assert payload["gates_anything"] is False, (
            "the payload must SAY it gates nothing — a reader should not have to take it "
            "on trust from a story file they will never see"
        )
        assert payload["note"] == assessment.note
        # AC1.5 / DN-16-5-4 — the roster/record distinction is in the PUBLISHED sentence,
        # not only in a comment. The QA Lead has been FILLED since 2026-08-22 and has judged
        # nothing; a sentence reading "QA Lead: absent" would be read as *unfilled*.
        assert "roster" in assessment.note, assessment.note
        assert "FILLED" in assessment.note, assessment.note

    decision = _cleared(_CONFIGURATIONS["NOT_INDEPENDENT"])
    block = decision.to_payload()["independence"]
    assert isinstance(block, dict) and block["status"] == "NOT_INDEPENDENT", block
    assert block["note"] in decision.precision_gate_status, (
        "the structured block and the sentence disagree, so a machine reader and a human "
        "reader of the same artifact would be told different things"
    )
    assert decision.to_payload()["adjudication_record"]["adjudicators"] == list(
        decision.adjudicators
    )

    # AC3.4 / DN-16-5-6 — the dogfood surface reads NO adjudication record, and must stay
    # byte-identical. Asserted by RENDERING and comparing strings, not by reading the diff.
    from argus.dogfood.proof_run import derive_gate_status  # noqa: PLC0415

    dogfood = derive_gate_status()
    assert "precision=" in dogfood, "non-vacuity: the dogfood status rendered no figure"
    assert "adjudication independence:" not in dogfood, (
        "the dogfood generator passes precision=None and reads NO record; a sentence about "
        "independence there would describe a judgement that never happened (DN-16-5-6)."
    )
    assert dogfood == derive_gate_status(), "the dogfood status is not deterministic"

    # AC4.5 — this story writes NOTHING. The committed record is read-only input, and its
    # 31 rows and single adjudicator are exactly what they were.
    committed = _record()
    assert len(committed.rows) == 31, len(committed.rows)
    assert {row.adjudicator for row in committed.live_rows()} == {
        "XAgent007 (Engineering Lead)"
    }
    assert committed.protocol_version == "V1.3", committed.protocol_version
    assert assess_independence(
        tuple(sorted({r.adjudicator for r in committed.live_rows() if r.adjudicator}))
    ).status == "NOT_INDEPENDENT"
    assert independence_note(None) is None, "the pre-16.5 shape must stay renderable"


def _superseded_population(
    *, struck_by: str, live_author: str, contributing_members: int = 5, size: int = 6
) -> AdjudicationRecord:
    """A population carrying ONE row struck by a ``supersedes`` correction (AC1.3, ``-114``).

    Built from :func:`_population` so every pinned term (member spread, size, locators, rule
    ids, dispositions) is inherited rather than re-typed — the lockstep discipline of §2.8
    applies here too, and the ONLY thing this helper varies is WHO authored the struck row
    versus WHO authored the live one that replaces it.

    The correction is expressed the one way the type admits: a NEW row that NAMES the row it
    replaces. ``AdjudicationRecord.__post_init__`` requires the two to share a
    ``finding_id`` — so only ``row_id``, ``adjudicator``, ``reason`` and ``supersedes``
    move, and the five fields ``finding_id`` is derived from are carried over untouched.
    §3.4's supersede-never-erase rule means the struck row STAYS on ``record.rows`` and
    disappears only from ``record.live_rows()``. That difference is the whole observable.
    """
    base = _population((live_author,), contributing_members=contributing_members, size=size)
    first, *rest = base.rows
    struck = replace(
        first,
        adjudicator=struck_by,
        reason="synthetic fixture: the SUPERSEDED judgement, retained and never erased",
    )
    revision = first.row_id.rsplit(".", 1)[0]
    correction = replace(
        first,
        row_id=f"{revision}.1",
        adjudicator=live_author,
        supersedes=first.row_id,
        reason="synthetic fixture: the CORRECTION that strikes the row above (§3.4)",
    )
    record = replace(base, rows=(struck, correction, *rest))
    assert record.superseded_row_ids == frozenset({first.row_id}), (
        "non-vacuity: the fixture did not actually strike a row, so the live/all "
        "distinction this guard is about never arises"
    )
    assert len(record.live_rows()) == len(record.rows) - 1 == size, (
        "non-vacuity: the struck row is still live, or the correction did not land"
    )
    return record


#: The two leaks ``-114`` drives, GENERATED as (struck author, role that would leak, status
#: the leak would forge). Both are the failure the review named in terms: a struck row whose
#: author differs IN ROLE from the live one quietly UPGRADING an honest ``NOT_INDEPENDENT``
#: record. One per registered role that is not the Engineering Lead.
_SUPERSEDED_LEAKS: tuple[tuple[str, str, str], ...] = (
    (_QA_LEAD, QA_LEAD_ROLE, "SECOND_REVIEWER_INTERNAL"),
    (_EXTERNAL, EXTERNAL_ADJUDICATOR_ROLE, "EXTERNAL_ADJUDICATOR_PARTICIPATED"),
)


@pytest.mark.parametrize(("struck_by", "leaked_role", "forged"), _SUPERSEDED_LEAKS)
def test_TC_ArgusAgent_PRECISION_001_114_the_status_is_derived_from_LIVE_rows_only(
    struck_by: str, leaked_role: str, forged: str
) -> None:
    """TC-ArgusAgent-PRECISION-001-114 — AC1.3 / AC5.4: SUPERSEDED rows do not judge.

    **Observable:** the ``status`` and ``adjudicators`` of the
    :class:`IndependenceAssessment` ``decide_gate`` derives for a record in which one row
    has been STRUCK by a ``supersedes`` correction whose author differs IN ROLE from the
    live row that replaces it. Concretely: does the derivation read ``record.live_rows()``
    or ``record.rows``?

    **Why this guard exists, stated as the gap it closes.** AC1.3 claims the status is
    derived from the LIVE rows, and the review of this story mutation-tested that claim:
    replacing ``live = record.live_rows()`` with ``live = record.rows`` in ``decide_gate``
    produced **ZERO** failures across ``test_gate_independence.py``,
    ``test_gate_decision.py``, ``test_adjudication_record.py`` and
    ``test_gate_decision_artifact.py`` — because no generated population anywhere carried a
    superseded row. Nothing was mis-derived on the committed record (it carries **0**
    superseded rows), so this is a REGRESSION path rather than a live defect; but a
    disclosure a reader is asked to trust, whose central claim no guard closes over, is the
    ``AI-E11-1`` shape this whole module was written to stop. It is also exactly what AC5.4
    means by *"an adversarial variant GENERATED from the record the guard closes over"*.

    **RED at the REAL SEAM (GUARD-ADEQUACY (ii)).** The mutation is the review's own, made
    in the shipped module and not against a reconstruction:
    ``argus/precision/gate_decision.py``, ``live = record.live_rows()`` ->
    ``live = record.rows``. Under it the struck author re-enters the derived set and the
    status is FORGED upward, so BOTH parametrised cases go RED on the ``status`` assertion
    below. Verified by execution with ``PYTHONDONTWRITEBYTECODE=1`` and a cleared
    ``__pycache__``, the tree restored byte-exact afterwards and ``git status --porcelain``
    confirmed empty.

    **Adversarial variants, GENERATED with their count: 2** — one per registered role that
    is NOT the Engineering Lead, with the role half taken from the protocol's own role
    constants rather than typed. Each drives a DIFFERENT forged status, so a derivation
    that leaked superseded rows could not satisfy even one of them by accident.

    **Non-vacuity is asserted FIRST**, and in the form that matters: the two views of the
    SAME record are asserted to derive DIFFERENT statuses. If they ever agreed, every
    assertion below would pass without observing anything at all.
    """
    record = _superseded_population(struck_by=struck_by, live_author=_ENGINEERING_LEAD)

    # ── non-vacuity, before any claim about the derivation ────────────────────────────
    struck_ids = record.superseded_row_ids
    struck_row = next(row for row in record.rows if row.row_id in struck_ids)
    assert struck_row.adjudicator == struck_by, struck_row.adjudicator
    assert leaked_role != ENGINEERING_LEAD_ROLE, (
        "non-vacuity: the struck row must differ IN ROLE from the live one, or the two "
        "views of this record could not disagree and the guard would observe nothing"
    )
    assert struck_by not in {row.adjudicator for row in record.live_rows()}, (
        "non-vacuity: the struck author is still LIVE, so this fixture cannot distinguish "
        "record.live_rows() from record.rows"
    )

    # THE observable, stated as the two views of one record. `all_set` is what the mutation
    # would see; `live_set` is what AC1.3 says the derivation must see.
    live_set = tuple(sorted({r.adjudicator for r in record.live_rows() if r.adjudicator}))
    all_set = tuple(sorted({r.adjudicator for r in record.rows if r.adjudicator}))
    assert live_set == (_ENGINEERING_LEAD,), live_set
    assert set(all_set) == {_ENGINEERING_LEAD, struck_by}, all_set
    forged_assessment = assess_independence(all_set)
    assert forged_assessment.status == forged, forged_assessment.status
    assert forged_assessment.status != "NOT_INDEPENDENT", (
        "non-vacuity: the leaked view derives the SAME status as the live view, so this "
        "population cannot witness the difference it was generated to witness"
    )

    # ── the claim: decide_gate derives from the LIVE rows ─────────────────────────────
    decision = _decide(record, corpus=sealed_corpus_members(), per_finding=True)
    assessment = decision.independence
    assert isinstance(assessment, IndependenceAssessment)
    assert assessment.adjudicators == (_ENGINEERING_LEAD,), (
        f"the struck row's author leaked into the derived adjudicator set: "
        f"{assessment.adjudicators!r}. §3.4 retains a superseded row so the correction can "
        f"be audited — it does not restore its author's vote."
    )
    assert assessment.status == "NOT_INDEPENDENT", (
        f"the derived status is {assessment.status!r}, not 'NOT_INDEPENDENT'. A superseded "
        f"row authored by the {leaked_role!r} has been counted as a judgement, forging "
        f"{forged!r} — a disclosure claiming MORE independence than the record supports."
    )
    assert leaked_role not in assessment.roles_present, assessment.roles_present
    assert leaked_role in assessment.roles_absent, assessment.roles_absent

    # ── and the struck author reaches NO published surface (AC2.3 / AC2.5) ────────────
    assert struck_by not in decision.precision_gate_status, (
        "the struck author is named on the gate-status sentence a reader quotes"
    )
    assert struck_by not in repr(decision.to_payload()["independence"]), (
        "the struck author is named in the machine-readable independence block"
    )
