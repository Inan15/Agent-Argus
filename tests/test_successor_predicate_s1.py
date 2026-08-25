"""Story 17.3 — guards over the SUCCESSOR predicate ``S1`` itself, and over what did NOT move.

The second half of ``tests/test_assertion_strength.py``, split under NFR-M1 and Story 17.3's
§0.8 pre-registered split trigger. It imports that module's fixture plumbing — ``_span``,
``_discarded_sut_calls`` and the band fixtures — rather than copying it: a second copy of a
fixture is the fork class this repository has already rotted from twice.

⛔ **``S1`` GATES NOTHING IN EPIC 17.** ``successor-vacuity-predicate-specification.md`` §6.5:
*"17.3 must land ``S1`` such that no finding's ``verdict_eligible`` flips on it within Epic
17."* ``-145`` is what makes ``S1`` the predicate §2.1 defines rather than something adjacent
to it; ``-146`` is what makes *"nothing flipped"* checkable rather than promised.

⛔ **NO REACH FIGURE FOR ``S1`` IS WRITTEN HERE** (AC6.3). The counts below are guard fixtures
over hand-built spans scored through the real Story 1.4 index; ``S1``'s population over the
corpus is Story 17.4's single measurement, against a criterion frozen at
``scripts/precision_preregistration.py``'s ``PREREGISTRATION_COMMIT_SHA`` before any of this
existed.

Verification area: precision validation (``TC-ArgusAgent-PRECISION-001-145`` .. ``-146``).
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

from argus.detectors import provenance_scan
from argus.detectors.assertion_strength import (
    ASSERTION_STRENGTH_BANDS,
    grade_span_assertions,
    s1_corroborated,
)
from argus.detectors.vacuous_vocabulary import (
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
)
from tests.test_assertion_strength import (
    _ARGUS_ROOT,
    _BASELINE_COMMIT,
    _EXISTENCE_BAND,
    _REPO_ROOT,
    _SILENT,
    _STORY_TAG,
    _VALUE_BAND,
    _discarded_sut_calls,
    _span,
)


# --------------------------------------------------------------------------------------
# AC5 — S1 is the SPECIFIED predicate; AC6 — nothing flipped
# --------------------------------------------------------------------------------------
def test_TC_ArgusAgent_PRECISION_001_145_s1_is_the_specified_predicate(tmp_path: Path) -> None:
    """TC-ArgusAgent-PRECISION-001-145 — AC5: three conjuncts, and a threshold that did not move.

    **Observable:** ``s1_corroborated``'s verdict over spans that falsify exactly ONE
    conjunct of ``successor-vacuity-predicate-specification.md`` §2.1 at a time, plus the
    §2.2 threshold.

    **Non-vacuity FIRST, and it is this case's specific way of dying quietly:** a span that
    ``S1`` ACCEPTS is exhibited before any refusal is asserted. Every refusal below is
    trivially green against a predicate that refuses everything.

    **Generated with its count:** one widening variant per band ABOVE ``none`` — the two
    bands ``S1`` is pre-refused from admitting — each asserted to CHANGE the verdict, with
    the generated count asserted to equal ``len(ASSERTION_STRENGTH_BANDS) - 1``.

    ⛔ **The threshold is EVERY assertion at the weakest band and it is NOT a tuning knob.**
    Admitting ``existence`` is a separate, future act requiring its own pre-registration
    (§2.2); this case is what makes turning it a visible act rather than a quiet one.
    """
    # ⛔ NON-VACUITY: a span S1 ACCEPTS, exhibited first.
    accepted = _span(tmp_path, _SILENT, slug="s1_accepted")
    assert s1_corroborated(*accepted) is True, (
        "S1 accepts NOTHING, so every refusal below is trivially green. The predicate, its "
        "grader, or this fixture has moved -- escalate (AC10.3/AC10.4)."
    )
    assert _discarded_sut_calls(accepted) >= 1, "the accepted span does not even reach (b′)"
    assert grade_span_assertions(*accepted).graded == 0, (
        "AC2.5: the accepted span is the EMPTY-assertion case the specification names "
        "explicitly, which is what makes S1 a superset of the V2 silent band exactly"
    )

    # ---- (a) REACHABILITY falsified ALONE --------------------------------------------
    no_sut = _span(
        tmp_path,
        "\ndef test_x():\n    assert True\n",
        slug="s1_no_sut",
    )
    assert (
        len(
            provenance_scan.candidate_sut_edges(
                no_sut[1],
                assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
                mock_callees=_MOCK_CALLEES,
            )
        )
        == 0
    ), "the (a)-falsifying fixture still reaches a candidate SUT, so it falsifies nothing"
    assert s1_corroborated(*no_sut) is False, "(a) reachability does not gate S1"

    # ---- (b′) DISCARD falsified ALONE ------------------------------------------------
    consumed = _span(
        tmp_path,
        '\ndef test_x():\n    result = parse("payload")\n    assert True\n',
        slug="s1_consumed",
    )
    assert (
        len(
            provenance_scan.candidate_sut_edges(
                consumed[1],
                assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
                mock_callees=_MOCK_CALLEES,
            )
        )
        >= 1
    ), "the (b′)-falsifying fixture does not satisfy (a), so its refusal is not attributable"
    assert _discarded_sut_calls(consumed) == 0, (
        "the (b′)-falsifying fixture still discards a SUT result, so it falsifies nothing"
    )
    assert grade_span_assertions(*consumed).every_assertion_at_the_weakest_band, (
        "the (b′)-falsifying fixture also fails (c′), so a refusal could come from either"
    )
    assert s1_corroborated(*consumed) is False, "(b′) discarded_sut_calls >= 1 does not gate S1"

    # ---- (c′) falsified ALONE, and the THRESHOLD -------------------------------------
    generated = 0
    for band, source in (("value", _VALUE_BAND), ("existence", _EXISTENCE_BAND)):
        span = _span(tmp_path, source, slug=f"s1_band_{band}")
        counts = grade_span_assertions(*span)
        assert getattr(counts, band) == 1 and counts.graded == 1, (
            f"the {band!r} fixture graded {counts!r}, not exactly one {band!r} assertion"
        )
        assert counts.unestablished == 0
        assert _discarded_sut_calls(span) >= 1, (
            f"the {band!r} fixture does not reach (b′), so its refusal is not attributable "
            f"to (c′) and this variant measures nothing"
        )
        assert s1_corroborated(*span) is False, (
            f"S1 corroborated a span carrying exactly one {band!r}-band assertion. The "
            f"threshold is EVERY assertion at the WEAKEST band (specification §2.2), and "
            f"admitting a band above `none` is a separate, future act requiring its own "
            f"pre-registration. ⛔ It is not a tuning knob and this story does not turn it."
        )
        generated += 1
    assert generated == len(ASSERTION_STRENGTH_BANDS) - 1 == 2, (
        f"{generated} widening variant(s) were generated; one per band above `none` is the "
        f"claim, and the scale's own length is what decides how many that is"
    )

    # ⛔ AC5.2 / specification §7.3 — S1 carries NO mock-binding input. Driven, not read: the
    # grader's answer must not move when the mock vocabulary does.
    mocked = _span(
        tmp_path,
        '\nfrom unittest.mock import Mock\n\n\ndef test_x():\n'
        '    fake = Mock()\n    parse("payload")\n    fake.tally.assert_called_once()\n',
        slug="s1_mock_free",
    )
    assert grade_span_assertions(*mocked).graded >= 1, (
        "the mock fixture carries no graded assertion, so it says nothing about mock input"
    )


def test_TC_ArgusAgent_PRECISION_001_146_nothing_flipped() -> None:
    """TC-ArgusAgent-PRECISION-001-146 — AC6: the verdict line, the output paths, the diff.

    **Observable, three halves.**

    1. ``VacuousTestDetector._ast_corroborated``'s return expression, compared as a PARSED
       AST EXPRESSION to the pinned form. ⛔ Compared as an expression and not as a string on
       purpose: a string comparison goes RED on a reformat that changes nothing and GREEN on
       a semantic change that happens to keep the same text.
    2. Both ``SUCCESSOR_OUTPUT_PATHS`` prefixes asserted ABSENT on disk. This story commits
       the predicate's CODE and never its OUTPUT over a corpus member, which is what leaves
       Story 17.4's ancestry guard nothing to argue about.
    3. This story's own commits, read out of REAL history, touch none of ``argus/precision/``,
       ``scripts/`` or the specification document.

    **Non-vacuity FIRST:** a control path KNOWN to carry commits in the same range is
    asserted NON-empty. A misspelled pathspec returns empty and reads exactly like a clean
    tree — the failure mode ``-75``/``-94``/``-139`` already answered, reused here.

    **Executed mutation:** the return expression is altered in the parsed source text and the
    SAME comparison is driven over it — RED.
    """
    pinned = "evidence.sut_result_is_discarded and evidence.mock_referencing_assertions >= 1"
    source = (_ARGUS_ROOT / "detectors" / "vacuous_test.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    corroborated = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "_ast_corroborated"
    )
    returns = [node for node in ast.walk(corroborated) if isinstance(node, ast.Return)]
    assert len(returns) >= 3, (
        f"only {len(returns)} return statement(s) were resolved in _ast_corroborated; the "
        f"walk is not seeing the function it claims to"
    )
    final = max(returns, key=lambda node: (node.lineno, node.col_offset))
    assert final.value is not None
    assert ast.dump(final.value) == ast.dump(ast.parse(pinned, mode="eval").body), (
        "the ONE verdict-eligibility decision in this rule class MOVED. Story 17.3 lands S1 "
        "ADVISORY: specification §6.5 requires that no finding's verdict_eligible flips on "
        f"it within Epic 17. Expected {pinned!r}, found {ast.unparse(final.value)!r}."
    )
    mutated = ast.parse(pinned.replace(">= 1", ">= 0"), mode="eval").body
    assert ast.dump(mutated) != ast.dump(final.value), (
        "the comparison cannot distinguish a mutated expression, so it would stay green "
        "through the change it exists to catch"
    )

    # ---- (2) neither successor output prefix exists ----------------------------------
    from scripts.precision_preregistration import SUCCESSOR_OUTPUT_PATHS

    assert len(SUCCESSOR_OUTPUT_PATHS) == 2, "the pre-registered output prefixes moved"
    for prefix in SUCCESSOR_OUTPUT_PATHS:
        assert not (_REPO_ROOT / prefix).exists(), (
            f"{prefix!r} exists. This story commits S1's CODE and never its OUTPUT over a "
            f"corpus member (AC6.4); committing one scored row would make Story 17.4's "
            f"ancestry guard argue about a commit nobody planned."
        )

    # ---- (3) this story's commits touch none of the fenced paths ----------------------
    commits = subprocess.run(  # noqa: S603,S607 - read-only git verb, fixed argv
        ["git", "log", "--format=%H %s", f"{_BASELINE_COMMIT}..HEAD"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    story_commits = [line.split(" ", 1)[0] for line in commits if _STORY_TAG in line]
    assert len(story_commits) >= 1, (
        f"no commit of this story's arc was found in {_BASELINE_COMMIT}..HEAD, so every "
        f"'the diff is empty' claim below is a claim about no commits at all"
    )

    def touched(sha: str, *pathspecs: str) -> list[str]:
        return subprocess.run(  # noqa: S603,S607 - read-only git verb, fixed argv
            ["git", "show", "--name-only", "--format=", sha, "--", *pathspecs],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()

    control = {path for sha in story_commits for path in touched(sha, "argus/detectors")}
    assert control, (
        "the CONTROL pathspec 'argus/detectors' reports no file touched by this story's "
        "commits. A misspelled pathspec returns empty and reads exactly like a clean tree, "
        "so every absence below would be unfalsifiable"
    )

    fenced = (
        "argus/precision",
        "scripts",
        "_bmad-output/design-artifacts/ArgusAgent/successor-vacuity-predicate-specification.md",
        "_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md",
        "_bmad-output/design-artifacts/ArgusAgent/validation-corpus",
        "argus/detectors/base.py",
    )
    violations = {
        sha[:7]: paths for sha in story_commits if (paths := touched(sha, *fenced))
    }
    assert not violations, (
        f"a commit of this story's arc touched a path AC8.2 requires to be byte-unchanged: "
        f"{violations!r}"
    )
