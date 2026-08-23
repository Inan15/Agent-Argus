"""Story 16.7 — guards over the SILENT test class RECORD: its vocabularies and its figures.

WHY THIS FILE EXISTS, and why it is separate from ``tests/test_silent_class.py``. That file
guards the PREDICATE — what makes a span a member of the class, and the structural fact that
the predicate cannot reach the detector path. This one guards the RECORD the predicate feeds:
the two CLOSED vocabularies it borrows and adds, the derived figures it publishes, the
containment its builder claims, and the fence around the four committed corpus artifacts the
externalization gate reads. The split is NFR-M1's own remedy — split, never shave, never
exempt — applied along ``AR8``'s seam, and the fixture plumbing is IMPORTED from the predicate
half rather than copied: a second copy of a fixture is the fork class ``AR7`` exists to
prevent, and this repository has rotted from it twice.

⛔ THE ONE MISTAKE THAT MATTERS MOST IN THIS STORY IS FENCED HERE, by ``-131``. The obvious
move — *"it is an adjudication, so it goes on the adjudication record"* — silently moves the
externalization gate. Measured in memory before a line of this story was written: appending 36
advisory ``TP`` rows to ``validation-corpus/adjudication-record.json`` takes ``total_tp``
0 → 36, ``adjudicated_population`` 31 → 67, ``distinct_rule_class_count`` 1 → 2 and
``independence.status`` ``NOT_INDEPENDENT`` → ``SECOND_REVIEWER_INTERNAL``. Two of those the
epic forbids outright, and the move is wrong on the protocol's own terms besides — every one of
the 1,032 findings is ADVISORY, and protocol section 4,
``scripts/build_adjudication_record.py`` and ``validation-corpus/blocking-worklist-13-5.md``
each say independently that an advisory finding is not a false ACCUSATION and is not in the
precision denominator.

⛔ AND THE SECOND MISTAKE: A MACHINE ANSWERING THE HUMAN'S QUESTION. ``-125`` asserts that the
only row factory the builder can reach has no parameter for a disposition, an adjudicator or a
date, so protocol section 2's rule — ``UNADJUDICATED`` is *the ONLY member an automated
producer may write* — is enforced by the SHAPE OF THE CODE rather than by a reviewer
remembering it.

⛔ NON-VACUITY IS CHECKED FIRST, EVERY TIME (``AI-E11-1``). Every case asserts its population is
non-empty before asserting anything about it. An empty record satisfies *"nothing was
promoted"*, *"no row carries an adjudicator"* and *"no proportion was reported"* all at once,
forever, while measuring nothing at all — and that is the precise shape of the artifact Epic 13
exists to make impossible.

⛔ WHAT THIS FILE DELIBERATELY DOES NOT ASSERT. Nothing here says anything about
``argus/precision/gate_*.py`` and nothing here imports ``gate_decision``. That the gate did not
move is discharged by the NINE EXISTING ``tests/test_gate_*.py`` files staying green and by
both existing builders exiting 0 under ``--check``; forking a guard that already exists is the
``AR7`` defect. And nothing here asserts a corpus member's working tree is clean or unchanged:
``minions`` returned seven different dirty-entry counts in one day under three sessions,
because it is a live tree other people are editing, and a check nobody can satisfy is the
Story 16.5 defect class (``DN-16-7-4``).

Verification area: precision validation — the silent-class RECORD
(``TC-ArgusAgent-PRECISION-001-119`` .. ``-125``, ``-129`` .. ``-134``).
"""

from __future__ import annotations

import ast
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from argus.precision import adjudication, silent_class
from argus.precision.adjudication import (
    DISPOSITIONS,
    LOCATOR_RE,
    PROTOCOL_ADJUDICATOR_ROLES,
    UnregisteredAdjudicator,
    UnregisteredDisposition,
)
from argus.precision.gate_independence import assess_independence
from argus.precision.silent_class import (
    ASSESSED_IDIOMS,
    IDIOMS,
    SILENT_CLASS_ROW_FIELDS,
    SILENT_CLASS_RULE_ID,
    UNADJUDICATED,
    UNASSESSED_IDIOM,
    SilentClassRow,
    SpanScore,
    UnregisteredIdiom,
    carry_forward,
    idiom_meaning,
    locator_for,
    rows_from_payload,
    seed_row,
)
from argus.store.canonical import loads

# The fixture plumbing and the committed-record readers are IMPORTED from the predicate half,
# never copied: ONE fixture, ONE set of readers, ONE definition of "the seam is reachable".
from tests.test_silent_class import (
    _MODULE_SOURCE_PATH,
    _RECORD_PATH,
    _WORKLIST_PATH,
    _assert_seam_is_reachable,
    _committed_record_payload,
    _committed_rows,
    _judged,
    _record_of,
    _score_fixture,
    _tmp,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "scripts") not in sys.path:  # pragma: no cover - test bootstrap
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import build_silent_class_record as builder  # noqa: E402

_BUILDER_SOURCE_PATH = _REPO_ROOT / "scripts" / "build_silent_class_record.py"
_SNAPSHOT_SOURCE_PATH = _REPO_ROOT / "scripts" / "pinned_corpus_snapshot.py"

#: The committed corpus artifacts this story must leave BYTE-UNCHANGED.
_FENCED_CORPUS_ARTIFACTS = (
    "adjudication-record.json",
    "adjudication-set.json",
    "adjudication-set-13-5.json",
    "gate-decision-record.json",
)


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC3 / AC4 / AC5 / AC6 — the record, its vocabularies and its derived figures.
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_119_the_shared_vocabulary_is_the_SAME_OBJECT() -> None:
    """TC-ArgusAgent-PRECISION-001-119 — AC3.3: borrowed, not copied.

    **Observable:** object identity (``is``, never ``==``) of the vocabulary this module
    imports against ``argus.precision.adjudication``'s, plus three construction-time raises.

    **Defect it moves:** a re-declared local copy of ``DISPOSITIONS`` or ``LOCATOR_RE``.
    An ``==`` comparison would pass over a copy, and every other guard in this file would
    stay green while the two records slowly disagreed about what a disposition is. Identity
    is the only comparison that catches it.
    """
    assert len(DISPOSITIONS) == 4, "DISPOSITIONS is not four members; the fence moved"
    assert silent_class.DISPOSITIONS is adjudication.DISPOSITIONS
    assert silent_class.HUMAN_DISPOSITIONS is adjudication.HUMAN_DISPOSITIONS
    assert silent_class.LOCATOR_RE is adjudication.LOCATOR_RE
    assert silent_class.PROTOCOL_ADJUDICATOR_ROLES is adjudication.PROTOCOL_ADJUDICATOR_ROLES
    assert silent_class.adjudicator_role is adjudication.adjudicator_role
    assert silent_class.disposition_meaning is adjudication.disposition_meaning
    assert silent_class.finding_row_id is adjudication.finding_row_id
    assert silent_class.expert_hours_report is adjudication.expert_hours_report

    row = _committed_rows()[0]
    with pytest.raises(UnregisteredDisposition):
        _judged(row, "PROBABLY_FINE", "NOT_A_SMOKE_TEST", "XAgent007 (Engineering Lead)")
    with pytest.raises(UnregisteredAdjudicator):
        _judged(row, "FP", "NOT_A_SMOKE_TEST", "Somebody (Chief Vibes Officer)")
    with pytest.raises(ValueError, match="must carry NO adjudicator"):
        SilentClassRow(
            row_id=row.row_id,
            member_id=row.member_id,
            rule_id=row.rule_id,
            verdict_eligible=False,
            advisory=True,
            locator=row.locator,
            test_name=row.test_name,
            discarded_sut_calls=row.discarded_sut_calls,
            consumed_sut_calls=row.consumed_sut_calls,
            pinned_sha=row.pinned_sha,
            disposition=UNADJUDICATED,
            adjudicator="XAgent007 (Engineering Lead)",
        )


def test_TC_ArgusAgent_PRECISION_001_120_the_idiom_vocabulary_is_closed_both_ways() -> None:
    """TC-ArgusAgent-PRECISION-001-120 — AC5.1/AC5.2: closed, and ORTHOGONAL.

    **Observable:** every registered idiom is exercised by this case, an unregistered one
    RAISES, and a row that is ``FP`` *and* ``DELIBERATE_SMOKE_TEST`` is constructible and
    round-trips through the payload.

    **Defect it moves:** the ``TC-ArgusAgent-PRECISION-001-38`` shape — a vocabulary checked
    in one direction only. A registered member no case exercises is itself a finding,
    because a member nobody can produce is a member nobody can rely on. And an idiom folded
    into ``DISPOSITIONS`` as a fifth member would make *"is this a false accusation?"* and
    *"is this idiom deliberate?"* one axis when they are two — the combination FP AND
    deliberate smoke test IS the measurement (``DN-16-7-2``).
    """
    assert set(ASSESSED_IDIOMS) | {UNASSESSED_IDIOM} == set(IDIOMS), (
        "the assessed/unassessed partition does not cover the idiom vocabulary"
    )
    assert UNASSESSED_IDIOM not in ASSESSED_IDIOMS
    assert not set(IDIOMS) & set(DISPOSITIONS), (
        "an idiom member collides with a disposition member; the axes are not orthogonal"
    )
    assert len(DISPOSITIONS) == 4, "DISPOSITIONS gained a member — DN-16-7-2 forbids it"
    for name in IDIOMS:
        assert idiom_meaning(name).strip(), f"idiom {name} has no registered meaning"
    with pytest.raises(UnregisteredIdiom):
        idiom_meaning("PROBABLY_A_SMOKE_TEST")

    row = _committed_rows()[0]
    exercised: set[str] = {UNASSESSED_IDIOM}
    assert row.idiom == UNASSESSED_IDIOM
    for idiom in ASSESSED_IDIOMS:
        judged = _judged(row, "FP", idiom, "Veer Pratap Singh (QA Lead)")
        exercised.add(judged.idiom)
        assert judged.to_payload()["idiom"] == idiom
        assert judged.to_payload()["disposition"] == "FP"
    assert exercised == set(IDIOMS), (
        f"registered idiom(s) {sorted(set(IDIOMS) - exercised)!r} are exercised by no case. "
        f"An unexercised member of a closed vocabulary is itself a finding."
    )
    with pytest.raises(UnregisteredIdiom):
        _judged(row, "FP", "SMOKE", "Veer Pratap Singh (QA Lead)")


def test_TC_ArgusAgent_PRECISION_001_121_the_proportion_refuses_an_unassessed_denominator() -> None:
    """TC-ArgusAgent-PRECISION-001-121 — AC5.3: no measurement over rows nobody read.

    **Observable:** ``SmokeTestProportion.measured`` and ``.proportion`` over a record whose
    rows are all ``NOT_ASSESSED``, and over one where some have been assessed.

    **Defect it moves:** reporting ``0/36``. That reads as *"none of them are smoke tests"*
    — a measurement — when the truth is *"nobody looked"*. It is the same class of defect as
    an empty adjudication record reporting 100% precision, and it is the one this whole
    story exists to avoid producing.
    """
    rows = _committed_rows()
    seeded = _record_of(rows)
    assert len(seeded.live_rows()) == 36, "non-vacuity: the seeded record must carry 36 rows"
    proportion = seeded.smoke_test_proportion()
    assert proportion.population == 36
    assert proportion.assessed == 0
    assert proportion.measured is False
    assert proportion.proportion is None, "a proportion was reported over 0 assessed rows"
    assert "NOT MEASURED" in proportion.note

    judged = (
        _judged(rows[0], "FP", "DELIBERATE_SMOKE_TEST", "XAgent007 (Engineering Lead)"),
        _judged(rows[1], "TP", "NOT_A_SMOKE_TEST", "XAgent007 (Engineering Lead)"),
        _judged(rows[2], "BORDERLINE", "DELIBERATE_SMOKE_TEST", "Veer Pratap Singh (QA Lead)"),
    )
    partial = _record_of(judged + rows[3:])
    measured = partial.smoke_test_proportion()
    assert measured.assessed == 3, "the assessed denominator did not move"
    assert measured.smoke_tests == 2
    assert measured.measured is True
    assert measured.proportion == Fraction(2, 3), "the proportion is not an exact Fraction 2/3"
    assert isinstance(measured.proportion, Fraction), "AR4: never a float"
    assert measured.population == 36


def test_TC_ArgusAgent_PRECISION_001_122_expert_hours_are_a_report_and_never_a_gate() -> None:
    """TC-ArgusAgent-PRECISION-001-122 — AC6.1: a sentence, and nothing branches on it.

    **Observable:** the sentence :func:`argus.precision.adjudication.expert_hours_report`
    returns for ``None``, for an exact ``Fraction`` under the ceiling, and for one over it.

    **Defect it moves:** an hours OVERRUN turned into a failure. Protocol section 3's four
    expert-hours is a CEILING and not a target, and a producer that failed on an overrun
    would create a standing incentive to trim the adjudication to fit the estimate — which
    is how an estimate stops measuring the thing it estimates. ``None`` reading as zero is
    the second defect: *not recorded* and *took no time* are different claims.
    """
    rows = _committed_rows()
    assert rows, "non-vacuity: no rows to build a record from"
    record = _record_of(rows)
    assert record.expert_hours is None
    sentence = record.expert_hours_sentence()
    assert "NOT RECORDED" in sentence
    assert "0" not in sentence.split("NOT RECORDED")[0], "None must never render as zero"

    under = adjudication.expert_hours_report(Fraction(7, 2))
    over = adjudication.expert_hours_report(Fraction(9, 2))
    assert isinstance(under, str) and isinstance(over, str), "a report is a SENTENCE"
    assert under != over, "the report does not distinguish an overrun from an underrun"
    # It is a report: the module exposes no pass/fail derived from it, and nothing here
    # branches on it. Asserted structurally rather than promised.
    source = _MODULE_SOURCE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    branching = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.If, ast.While, ast.Assert))
        and "expert_hours_report" in ast.dump(node)
    ]
    assert not branching, (
        f"{len(branching)} control-flow node(s) branch on expert_hours_report. It is a "
        f"REPORT: the moment something branches on it, protocol section 3's ceiling has "
        f"quietly become a gate."
    )


def test_TC_ArgusAgent_PRECISION_001_123_independence_is_derived_and_gates_nothing() -> None:
    """TC-ArgusAgent-PRECISION-001-123 — AC6.2: derived through the EXISTING assessor.

    **Observable:** ``SilentClassRecord.independence().status`` over records with zero, one
    and two distinct adjudicator roles, and the ``gates_anything`` key on its payload.

    **Defect it moves:** a TYPED independence status, or one derived by a second
    implementation. The status here is computed by calling the shipped
    ``assess_independence`` over the ids that actually authored live rows, and the case
    asserts the two agree over every reachable member — so a fork would show up as a
    disagreement rather than as two quietly different numbers.

    ``NOT_ESTABLISHED`` over an unjudged record is the honest output and NOT a failure:
    *nobody judged it* is a different finding from *the author judged all of it*.
    """
    rows = _committed_rows()
    seeded = _record_of(rows)
    assert seeded.adjudicator_ids() == (), "a seeded record must name NO adjudicator"
    assert seeded.independence().status == "NOT_ESTABLISHED"

    lead = _judged(rows[0], "FP", "NOT_A_SMOKE_TEST", "XAgent007 (Engineering Lead)")
    qa = _judged(rows[1], "TP", "DELIBERATE_SMOKE_TEST", "Veer Pratap Singh (QA Lead)")
    one_role = _record_of((lead,) + rows[1:])
    two_roles = _record_of((lead, qa) + rows[2:])
    assert one_role.independence().status == "NOT_INDEPENDENT"
    assert two_roles.independence().status == "SECOND_REVIEWER_INTERNAL"
    for record in (seeded, one_role, two_roles):
        assert record.independence() == assess_independence(record.adjudicator_ids()), (
            "the record's status disagrees with the shipped assessor over its own ids"
        )
        payload = record.independence().to_payload()
        assert payload["gates_anything"] is False
        assert sorted(payload["roles_present"] + payload["roles_absent"]) == sorted(
            PROTOCOL_ADJUDICATOR_ROLES
        )
    assert "External adjudicator" in two_roles.independence().roles_absent, (
        "the External adjudicator is UNFILLED and must author nothing here"
    )


def test_TC_ArgusAgent_PRECISION_001_124_borderline_is_first_class_and_in_neither_ratio() -> None:
    """TC-ArgusAgent-PRECISION-001-124 — AC4.3: *looked at, could not decide*, recorded.

    **Observable:** ``counts()``, ``exhaustiveness()`` and the smoke-test denominator over a
    record carrying a ``BORDERLINE`` row.

    **Defect it moves:** collapsing ``BORDERLINE`` into ``FP`` (or into ``UNADJUDICATED``).
    A borderline records that a human SPENT THE TIME and the question is genuinely open. It
    must make the run non-exhaustive — otherwise an unresolved question is silently reported
    as a completed adjudication — and it must enter NEITHER side of any ratio.

    The semantics are the committed record's own: ``exhaustiveness()`` here DELEGATES to
    ``AdjudicationRecord.exhaustiveness()`` rather than restating the rule.
    """
    rows = _committed_rows()
    assert len(rows) == 36, "non-vacuity: the population must be the real one"
    borderline = _judged(rows[0], "BORDERLINE", "NOT_ASSESSED", "Veer Pratap Singh (QA Lead)")
    decided = tuple(
        _judged(row, "FP", "NOT_A_SMOKE_TEST", "XAgent007 (Engineering Lead)")
        for row in rows[1:]
    )
    record = _record_of((borderline,) + decided)
    tally = record.counts()
    assert tally["BORDERLINE"] == 1 and tally["FP"] == 35 and tally["TP"] == 0
    assert set(tally) == set(DISPOSITIONS), "counts() must carry EVERY registered member"

    result = record.exhaustiveness()
    assert isinstance(result, adjudication.AdjudicationUnevaluable), (
        "one BORDERLINE row must make the run NON-EXHAUSTIVE; reporting it exhaustive "
        "reports an open question as a closed one"
    )
    assert result.residual_count == 1
    assert result.adjudicated_count == 35
    payload = silent_class.exhaustiveness_payload(result)
    assert payload["exhaustive"] is False and payload["gates_anything"] is False

    proportion = record.smoke_test_proportion()
    assert proportion.assessed == 35, (
        "the BORDERLINE row carries NOT_ASSESSED and must be outside the denominator"
    )
    assert proportion.smoke_tests == 0


def test_TC_ArgusAgent_PRECISION_001_125_no_producer_path_can_author_a_judgement() -> None:
    """TC-ArgusAgent-PRECISION-001-125 — AC4.5/``DN-6``: the halt, made structural.

    **Observable:** the signature of :func:`~argus.precision.silent_class.seed_row` — the
    ONLY row factory the builder can reach — and the disposition of every row it can
    produce, plus every row on the committed artifact.

    **Defect it moves:** the exact artifact Epic 13 exists to make impossible — an
    autonomous producer tagging its own findings ``TP``. Protocol section 2 registers
    ``UNADJUDICATED`` as *the ONLY member an automated producer may write*. This case
    asserts the producer has no parameter through which another could arrive, so the rule is
    enforced by the shape of the code rather than by a reviewer remembering it.
    """
    import inspect

    parameters = set(inspect.signature(seed_row).parameters)
    for forbidden in ("disposition", "idiom", "adjudicator", "adjudicated_on", "reason"):
        assert forbidden not in parameters, (
            f"seed_row accepts {forbidden!r}. A producer that can be handed a disposition "
            f"is a producer that can write one, and protocol section 2 forbids exactly that."
        )
    scored = _score_fixture(_tmp())["test_silent_member"]
    _assert_seam_is_reachable(scored)
    seeded = seed_row(
        member_id="minions",
        locator="tests/example/test_thing.py:12",
        test_name="test_thing",
        pinned_sha="ec63b7293b7036bf910a0d1b5e61aba7dc551526",
        score=scored.score,
    )
    assert seeded.disposition == UNADJUDICATED
    assert seeded.idiom == UNASSESSED_IDIOM
    assert seeded.adjudicator is None and seeded.adjudicated_on is None

    with pytest.raises(ValueError, match="NOT a member"):
        seed_row(
            member_id="minions",
            locator="tests/example/test_thing.py:12",
            test_name="test_thing",
            pinned_sha="ec63b7293b7036bf910a0d1b5e61aba7dc551526",
            score=SpanScore(
                discarded_sut_calls=0,
                consumed_sut_calls=0,
                mock_referencing_assertions=0,
                statement_count=1,
                asserts_anything=False,
            ),
        )

    rows = _committed_rows()
    assert all(row.disposition == UNADJUDICATED for row in rows), (
        "a committed row carries a human disposition. Story 16.7 HALTED at the judgement "
        "by design; a judged row here means a machine answered the human's question."
    )
    assert all(row.adjudicator is None and row.adjudicated_on is None for row in rows)
    assert set(_committed_record_payload()["counts"]) == set(DISPOSITIONS)
    assert _committed_record_payload()["counts"]["UNADJUDICATED"] == 36


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC8 — portability, containment, and the builder's contract.
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_129_the_new_code_is_posix_portable() -> None:
    """TC-ArgusAgent-PRECISION-001-129 — AC8.4: portability as a criterion, not a hope.

    **Observable:** every locator on the committed record against ``LOCATOR_RE``; and a
    source scan of both new modules for a platform separator constant, a platform path-join
    helper, a backslash inside any string constant, an unnamed encoding, and a bare
    ``text=True`` on a subprocess call.

    **Defect it moves:** ``AI-E13-1`` and ``DF-16-6-F``. The local suite is Windows-only and
    CI runs an ubuntu matrix, so a Windows-shaped path or a locale-codec decode is invisible
    here and RED there. ``DF-16-6-F`` is an OPEN entry for exactly the ``text=True`` bug in
    a sibling guard; this case exists so this story does not file a second one.
    """
    rows = _committed_rows()
    assert len(rows) == 36, "non-vacuity: the locator population must be the real 36"
    for row in rows:
        assert LOCATOR_RE.match(row.locator), f"{row.locator!r} is not a repo-relative POSIX"
        assert ".." not in row.locator.split("/")
        assert chr(92) not in row.locator, f"{row.locator!r} carries a backslash"
        assert not row.locator[1:2] == ":", f"{row.locator!r} looks like a drive-letter path"
    assert locator_for("tests/a/b.py", 7) == "tests/a/b.py:7"

    for path in (_MODULE_SOURCE_PATH, _BUILDER_SOURCE_PATH):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert len(source.splitlines()) < 1200, f"{path.name} is over NFR-M1's ceiling"
        for banned in ("os.sep", "os.path.join", "os.path.sep", "ntpath"):
            assert banned not in source, f"{path.name} names {banned}, a platform path form"
        offenders = [
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and chr(92) in node.value
        ]
        assert not offenders, (
            f"{path.name} holds {len(offenders)} string constant(s) containing a backslash. "
            f"A backslash in this code is either a Windows path separator or a hand-rolled "
            f"regex, and neither belongs on a locator-building path."
        )
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            keywords = {keyword.arg for keyword in node.keywords}
            if name in {"read_text", "write_text", "open"}:
                assert "encoding" in keywords, (
                    f"{path.name}: {name}() does not name its encoding, so it decodes with "
                    f"the LOCALE codec - cp1252 here, utf-8 on CI"
                )
            if name == "write_text":
                assert "newline" in keywords, (
                    f"{path.name}: write_text() does not name its newline, so the artifact "
                    f"gets CRLF on Windows and LF on CI for the same input"
                )
            if name == "run":
                assert "text" not in keywords, (
                    f"{path.name}: a subprocess call passes text=; that is DF-16-6-F's bug"
                )
    assert "text=True" not in _SNAPSHOT_SOURCE_PATH.read_text(encoding="utf-8"), (
        "the shipped _git this story reuses grew a text=True; it must capture BYTES and "
        "decode them explicitly (DF-16-6-F)"
    )


def test_TC_ArgusAgent_PRECISION_001_130_the_git_vocabulary_is_read_only() -> None:
    """TC-ArgusAgent-PRECISION-001-130 — AC8.3/``DN-16-7-4``: containment, proved by driving it.

    **Observable:** the refusal :func:`build_silent_class_record.read_only_git` raises for a
    mutating verb, and every git subcommand literal reachable from either script.

    **Defect it moves:** a corpus member being written to. A member is a ratified
    third-party repository and this story is a MEASUREMENT; ``checkout``, ``stash``,
    ``clean``, ``reset``, ``worktree``, ``add``, ``commit``, ``fetch`` and ``pull`` would
    each mutate one. The absence is asserted BY EXECUTION rather than by reading the
    constant, because a constant nothing enforces is a comment.

    Deliberately NOT asserted anywhere: that a member's working tree is clean, or that it is
    unchanged across the run. Both were measured unsatisfiable — ``minions`` returned six
    different dirty-entry counts in one day under three sessions — and a check nobody can
    satisfy is the Story 16.5 defect class (``DN-16-7-4``).
    """
    allowed = builder.READ_ONLY_GIT_COMMANDS
    assert allowed, "the allow-list is empty; every call would be refused and nothing tested"
    forbidden = (
        "checkout", "stash", "clean", "reset", "worktree",
        "add", "commit", "fetch", "pull", "push", "rm", "mv",
    )
    for verb in forbidden:
        assert verb not in allowed, f"{verb!r} is a MUTATING verb and is in the allow-list"

    here = Path(_REPO_ROOT)
    for verb in forbidden:
        with pytest.raises(builder.Refused, match="READ-ONLY vocabulary"):
            builder.read_only_git(here, verb, "--porcelain")
    with pytest.raises(builder.Refused):
        builder.read_only_git(here)
    done = builder.read_only_git(here, "rev-parse", "--abbrev-ref", "HEAD")
    assert done.returncode == 0, "a permitted read-only verb was refused or failed"
    assert isinstance(done.stdout, bytes), (
        "the shipped _git must return BYTES; a str here means text= crept in (DF-16-6-F)"
    )

    literals: list[str] = []
    for path in (_BUILDER_SOURCE_PATH, _SNAPSHOT_SOURCE_PATH):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "id", None)
            if name not in {"_git", "read_only_git"}:
                continue
            positional = [
                arg.value
                for arg in node.args[1:]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
            ]
            if positional:
                literals.append(positional[0])
    assert len(literals) >= 4, (
        f"the scan found only {len(literals)} git call site(s); it is not resolving them, "
        f"so 'every subcommand is read-only' would pass vacuously"
    )
    outside = sorted({verb for verb in literals if verb not in allowed})
    assert not outside, (
        f"git subcommand(s) {outside!r} are issued but are not in the READ-ONLY allow-list "
        f"{sorted(allowed)!r}. Every read of a corpus member goes through ls-tree and "
        f"cat-file, which are pure reads of the object database."
    )


def test_TC_ArgusAgent_PRECISION_001_131_the_builder_check_writes_nothing() -> None:
    """TC-ArgusAgent-PRECISION-001-131 — AC3.1/AC3.2: ``--check`` is a read, and the fence holds.

    **Observable:** the exit code of ``build_silent_class_record.main(["--check"])`` and the
    bytes of six artifacts before and after it — this story's two, and the four the gate
    reads.

    **Defect it moves:** the single most consequential mistake available in this story.
    Appending these 36 advisory dispositions to ``adjudication-record.json`` was MEASURED to
    move ``total_tp`` 0 -> 36, ``adjudicated_population`` 31 -> 67 and ``independence.status``
    ``NOT_INDEPENDENT`` -> ``SECOND_REVIEWER_INTERNAL``, two of which the epic forbids
    outright. ``DN-16-7-1`` sends them to their own artifacts instead, and this case is the
    fence made executable.
    """
    corpus = _RECORD_PATH.parent
    watched = {name: (corpus / name) for name in _FENCED_CORPUS_ARTIFACTS}
    watched["silent-class-record.json"] = _RECORD_PATH
    watched["silent-class-worklist.md"] = _WORKLIST_PATH
    for name, path in watched.items():
        assert path.is_file(), f"{name} is absent; this case would watch nothing"
    before = {name: path.read_bytes() for name, path in watched.items()}
    assert all(before.values()), "an artifact is empty; the comparison would be vacuous"

    exit_code = builder.main(["--check"])
    assert exit_code == 0, f"--check exited {exit_code}; the artifacts are not current"

    after = {name: path.read_bytes() for name, path in watched.items()}
    moved = sorted(name for name in watched if before[name] != after[name])
    assert not moved, f"--check WROTE to {moved!r}; it is supposed to be a pure read"

    record = loads(before["silent-class-record.json"].decode("utf-8"))
    assert record["promotes_nothing"] is True
    assert record["gates_anything"] is False
    assert record["rule_id"] == SILENT_CLASS_RULE_ID
    gate = loads(before["gate-decision-record.json"].decode("utf-8"))
    assert "silent" not in loads(before["adjudication-record.json"].decode("utf-8")).get(
        "story", ""
    ), "this story's subject appears on the GATE's adjudication record"
    assert gate, "the gate decision record is empty"


def test_TC_ArgusAgent_PRECISION_001_132_a_human_judgement_is_carried_forward() -> None:
    """TC-ArgusAgent-PRECISION-001-132 — AC3.1: append-only over the human's work.

    **Observable:** :func:`~argus.precision.silent_class.carry_forward` over a freshly
    seeded row set and an existing set in which one row has been judged.

    **Defect it moves:** a producer that RE-SEEDS. Re-running the builder after the
    adjudication must be a no-op over every row a human touched; a producer that can
    overwrite a judgement can erase one, and the erasure would look exactly like a row that
    was never judged. The row schema is checked in BOTH directions on read for the same
    reason — a silently dropped field is how a judgement disappears between two runs.
    """
    rows = _committed_rows()
    assert len(rows) == 36, "non-vacuity: nothing to carry forward from an empty set"
    judged = _judged(rows[0], "TP", "DELIBERATE_SMOKE_TEST", "Veer Pratap Singh (QA Lead)")
    carried = carry_forward(rows, (judged,))
    assert len(carried) == 36, "carry_forward changed the population size"
    assert carried[0] == judged, "the human's judgement was RE-SEEDED away"
    assert carried[0].reason, "the carried judgement lost its reason"
    assert all(row.disposition == UNADJUDICATED for row in carried[1:])
    assert carry_forward(rows, ()) == rows, "a no-op carry-forward changed the rows"

    payload = _committed_record_payload()
    assert set(payload["rows"][0]) == set(SILENT_CLASS_ROW_FIELDS), (
        "the committed row schema does not match the closed schema this module enforces"
    )
    broken = dict(payload)
    broken["rows"] = [{key: value for key, value in payload["rows"][0].items() if key != "idiom"}]
    with pytest.raises(ValueError, match="schema violation"):
        rows_from_payload(broken)
    widened = dict(payload)
    widened["rows"] = [{**payload["rows"][0], "confidence": 0.9}]
    with pytest.raises(ValueError, match="schema violation"):
        rows_from_payload(widened)


def test_TC_ArgusAgent_PRECISION_001_133_every_refusal_this_record_makes_is_reachable() -> None:
    """TC-ArgusAgent-PRECISION-001-133 — AC3.3/AC5.3/``DF-10-4-E``: a raise nobody can
    trigger protects nothing.

    **Observable:** one distinct malformed input per refusal branch on
    :class:`~argus.precision.silent_class.SilentClassRow` and
    :class:`~argus.precision.silent_class.SilentClassRecord`, and the ``Exhaustive`` arm of
    :func:`~argus.precision.silent_class.exhaustiveness_payload`.

    **Defect it moves:** an unreachable guard. Construction-time validation is this record's
    entire enforcement mechanism — it is why *"the producer started writing judgements"* and
    *"a promotion was smuggled in through a row"* are construction errors rather than things a
    reviewer must notice. A branch no input can reach is a branch that has never been shown to
    work, and ``AI-E11-1``'s lesson is that it will read as protection anyway. Each refusal
    below is driven by ONE input that differs from a KNOWN-VALID row in exactly one field, so
    a failure names the field rather than the fixture.

    ``DF-10-4-E`` is the standing rule these discharge: an unregistered or impossible value
    RAISES; it is never defaulted and never tolerated.
    """
    rows = _committed_rows()
    assert len(rows) == 36, "non-vacuity: the valid baseline row must come from the real class"
    valid = rows[0].to_payload()
    assert valid["disposition"] == UNADJUDICATED, "the baseline row is not the seeded shape"

    def row(**overrides: object) -> SilentClassRow:
        return SilentClassRow(**{**valid, **overrides})

    assert row() == rows[0], "the unmodified baseline must round-trip; else every case below lies"

    refusals: tuple[tuple[str, dict[str, object], str], ...] = (
        ("verdict_eligible", {"verdict_eligible": True}, "promotion smuggled in"),
        ("advisory", {"advisory": False}, "advisory is False"),
        ("test_name", {"test_name": "   "}, "test_name is empty"),
        ("discarded_sut_calls", {"discarded_sut_calls": 0}, "requires >= 1"),
        ("consumed_sut_calls", {"consumed_sut_calls": -1}, "negative"),
        ("locator (absolute)", {"locator": "D:/x/tests/t.py:1"}, "repository-relative"),
        ("locator (escaping)", {"locator": "tests/../etc/t.py:1"}, "repository-relative"),
        ("locator (backslash)", {"locator": "tests" + chr(92) + "t.py:1"}, "repository-relative"),
        ("pinned_sha", {"pinned_sha": ""}, "pinned_sha is empty"),
    )
    for label, override, _hint in refusals:
        with pytest.raises(ValueError):
            row(**override)
    assert len(refusals) == 9, "the refusal population shrank; a branch stopped being exercised"

    human = {
        "disposition": "FP",
        "adjudicator": "XAgent007 (Engineering Lead)",
        "adjudicated_on": "2026-08-23",
        "reason": "a reason",
    }
    assert row(**human).disposition == "FP", "the valid human row must construct"
    with pytest.raises(ValueError, match="adjudicated_on"):
        row(**{**human, "adjudicated_on": None})
    with pytest.raises(ValueError, match="REASON"):
        row(**{**human, "reason": "   "})
    with pytest.raises(UnregisteredAdjudicator):
        row(**{**human, "adjudicator": "Nobody (Vibes Lead)"})

    # The record's own refusals, each one field away from a record that constructs.
    assert _record_of(rows).population_walked >= len(rows), "the baseline record must be valid"
    with pytest.raises(ValueError, match="SKIPPED"):
        silent_class.SilentClassRecord(
            protocol_version="V1.3",
            adjudication_unit=adjudication.ADJUDICATION_UNIT,
            class_definition="x",
            derivation_source="x",
            derivation_method="x",
            population_walked=1032,
            population_skipped=1,
            expert_hours=None,
            expert_hours_note="x",
            transcription_note="x",
            rows=rows,
        )
    with pytest.raises(ValueError, match="EMPTY"):
        _record_of(())
    with pytest.raises(ValueError, match="cannot be larger"):
        silent_class.SilentClassRecord(
            protocol_version="V1.3",
            adjudication_unit=adjudication.ADJUDICATION_UNIT,
            class_definition="x",
            derivation_source="x",
            derivation_method="x",
            population_walked=1,
            population_skipped=0,
            expert_hours=None,
            expert_hours_note="x",
            transcription_note="x",
            rows=rows,
        )
    with pytest.raises(ValueError, match="adjudication_unit"):
        silent_class.SilentClassRecord(
            protocol_version="V1.3",
            adjudication_unit="file",
            class_definition="x",
            derivation_source="x",
            derivation_method="x",
            population_walked=1032,
            population_skipped=0,
            expert_hours=None,
            expert_hours_note="x",
            transcription_note="x",
            rows=rows,
        )
    with pytest.raises(ValueError, match="impossible tally"):
        silent_class.SmokeTestProportion(assessed=3, smoke_tests=4, population=36)
    with pytest.raises(ValueError, match="impossible tally"):
        silent_class.SmokeTestProportion(assessed=40, smoke_tests=0, population=36)

    # The EXHAUSTIVE arm, which a seeded record can never reach: a fully judged population.
    judged = tuple(
        _judged(entry, "FP", "NOT_A_SMOKE_TEST", "XAgent007 (Engineering Lead)")
        for entry in rows
    )
    complete = _record_of(judged)
    result = complete.exhaustiveness()
    assert isinstance(result, adjudication.Exhaustive), (
        "a fully adjudicated record must read EXHAUSTIVE; if it cannot, the residual arm is "
        "the only arm this guard has ever exercised"
    )
    payload = silent_class.exhaustiveness_payload(result)
    assert payload["exhaustive"] is True
    assert payload["residual_count"] == 0
    assert payload["adjudicated_count"] == 36
    assert payload["gates_anything"] is False
    proportion = complete.smoke_test_proportion()
    assert proportion.measured is True and proportion.proportion == Fraction(0, 36)
    assert "0/36 of the ASSESSED" in proportion.note, proportion.note
    assert complete.independence().status == "NOT_INDEPENDENT"


def test_TC_ArgusAgent_PRECISION_001_134_a_map_override_cannot_escape_the_checkout_root(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """TC-ArgusAgent-PRECISION-001-134 — AC8.4/``DF-10-4-E``: the containment guard on
    ``--map`` is driven, and it is driven with the input that used to walk through it.

    **Observable:** :func:`build_silent_class_record._discards_the_root` over anchored and
    legitimate overrides — including every shipped ``DEFAULT_CHECKOUT_MAP`` value — and the
    exit code and stderr of ``build_silent_class_record.main(["--map", ...])`` at the real
    CLI seam.

    **Defect it moves:** a guard that could not fail, found by the iteration-1 review of this
    story. The refusal read ``if Path(relative).is_absolute()`` and its message promised to
    stop *"pathlib discards the left operand ... which silently escapes the root entirely"*.
    On this repository's LOCAL platform it did not: ``Path("/etc/x").is_absolute()`` is
    ``False`` on Windows — no drive — so a POSIX-style override was accepted and
    ``root / "/etc/x"`` resolved to ``<root's drive>:/etc/x``, outside ``--checkout-root``,
    which is the exact escape the message named. It was also entirely UNTESTED, so the suite
    could not see it. That pairing — a Windows-only local gate, an ubuntu matrix CI leg, and
    a portability check nobody drives — is ``AI-E13-1``, in one of ``AC8.4``'s own corners.

    Deliberately NOT asserted here: that ``..`` is refused. ``root / "../x"`` leaves the root
    too, but it leaves it visibly, and widening this guard to path traversal is a different
    story than the one the review filed.
    """
    root = tmp_path / "checkouts"
    root.mkdir()

    # NON-VACUITY FIRST (``AI-E11-1``): the escape this guard exists to stop is REAL on this
    # interpreter and this platform. If the join below did not discard the root, every
    # assertion after it would be theatre.
    escaped = builder._checkout_for(root, "minions", {"minions": "/etc/passwd"})
    assert root not in escaped.parents, (
        f"{escaped!r} is still under {root!r}: this platform does not discard the left "
        f"operand, so this case would be guarding a failure mode it cannot reproduce"
    )

    # TWO-SIDED. Every anchored form pathlib honours - POSIX root, Windows root, drive
    # absolute, drive RELATIVE, UNC - and the root itself.
    anchored = (
        "/etc/passwd",
        "/",
        chr(92) + "etc" + chr(92) + "passwd",
        "C:/etc",
        "C:etc",
        "//server/share",
    )
    for relative in anchored:
        assert builder._discards_the_root(relative), (
            f"{relative!r} is anchored and would discard --checkout-root, and the guard "
            f"let it through"
        )
    assert not Path("/etc/passwd").is_absolute() or sys.platform != "win32", (
        "sanity: on win32 a leading-slash override must NOT read as absolute, which is why "
        "the is_absolute() form of this guard was vacuous here"
    )

    # ... and it fires on NOTHING legitimate, including every checkout this tool ships with.
    legitimate = (*builder.DEFAULT_CHECKOUT_MAP.values(), "minions", "a/b/c")
    assert len(legitimate) == 7, "the legitimate population shrank; the negative side thins"
    for relative in legitimate:
        assert not builder._discards_the_root(relative), (
            f"{relative!r} is a legitimate relative checkout and the guard refused it; a "
            f"guard that refuses the tool's own defaults is worse than none"
        )
        contained = builder._checkout_for(root, "minions", {"minions": relative})
        assert root in contained.parents, f"{contained!r} escaped {root!r}"

    # THE REAL CLI SEAM. Note the exit code alone proves nothing - every refusal exits 2,
    # including the one an unfixed guard would reach later - so the MESSAGE is the assertion.
    exit_code = builder.main(["--map", "minions=/etc/passwd", "--checkout-root", str(root)])
    assert exit_code == 2, f"an escaping --map exited {exit_code}; it must be REFUSED"
    refusal = capsys.readouterr().err
    assert "REFUSED" in refusal and "--map" in refusal, refusal
    assert "ANCHORED" in refusal, (
        f"the run was refused, but not BY THIS GUARD: {refusal!r}. An unfixed guard also "
        f"exits 2 - one step later, on the missing checkout - so this case would pass "
        f"while the escape stayed open"
    )

    # The two sibling --map refusals, equally undriven until now.
    for malformed, expected in (("minions", "no '='"), ("minions=   ", "empty member id")):
        assert builder.main(["--map", malformed]) == 2, f"{malformed!r} was accepted"
        assert expected in capsys.readouterr().err, f"{malformed!r} refused for the wrong reason"

    # And the guard does not fire on a well-formed relative override: main() gets PAST it and
    # fails on something else entirely, which is what keeps the CLI arm two-sided too.
    assert builder.main(["--map", "minions=Minions"]) == 2, "the write path needs a root"
    passed_the_guard = capsys.readouterr().err
    assert "ANCHORED" not in passed_the_guard, passed_the_guard
    assert "--checkout-root is required" in passed_the_guard, passed_the_guard
