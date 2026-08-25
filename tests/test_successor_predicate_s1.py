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


def test_TC_ArgusAgent_PRECISION_001_146_nothing_flipped(tmp_path: Path) -> None:
    """TC-ArgusAgent-PRECISION-001-146 — AC6: the verdict line, the output paths, the diff.

    **Observable, three halves.**

    1. ``VacuousTestDetector._ast_corroborated``'s return expression, compared as a PARSED
       AST EXPRESSION to the pinned form. ⛔ Compared as an expression and not as a string on
       purpose: a string comparison goes RED on a reformat that changes nothing and GREEN on
       a semantic change that happens to keep the same text.
    2. ⛔ **RE-SCOPED 2026-08-26 BY OPERATOR DECISION** (see below): **no commit of THIS
       STORY'S OWN ARC created either** ``SUCCESSOR_OUTPUT_PATHS`` **prefix** — asked of git
       over ``_BASELINE_COMMIT..HEAD`` filtered by this story's ``(17-3)`` scope, rather than
       of the filesystem. This story commits the predicate's CODE and never its OUTPUT over a
       corpus member, which is what leaves Story 17.4's ancestry guard nothing to argue about.
    3. This story's own commits, read out of REAL history, touch none of ``argus/precision/``,
       ``scripts/`` or the specification document.

    **⛔ THE AMENDMENT TO PART (2), AND WHY.** Part (2) used to assert that both prefixes were
    ABSENT ON DISK. That form is **self-destructing**: filesystem existence is not scoped by
    commit ancestry, so it goes RED the moment Story 17.4 legitimately writes the measurement
    record it is chartered to produce under ``SUCCESSOR_OUTPUT_PATHS[0]`` (17.4 AC6.1) — and no
    descendant commit can escape it. The claim this part was always making is the one stated in
    its own original words, *"THIS STORY commits S1's CODE and never its OUTPUT"*, and that
    claim is permanent and checkable. Re-scoping preserves the guard's real intent; deleting it
    would not.

    ⛔ **This is the repair this epic has already accepted once, as ``DN-17-2-12``** — ``-144``'s
    git half was scoped to its own story's ``(17-2)``-tagged commits for exactly this reason,
    *"the literal form is guaranteed RED the moment Story 17.3 legitimately writes inside the
    shipped package, and the only response would be to delete it"*, and iteration 1's review
    judged that sound. The operator considered and **REJECTED** two alternatives: retiring part
    (2) into Story 17.4's ``-152``, and deferring 17.4's committed artifact to a follow-up.

    ⛔ **Parts (1) and (3) are untouched and no other frozen guard moved.** The amendment is
    narrow, is to ``-146`` part (2) ONLY, and was taken as an explicit operator act on
    2026-08-26 through Story 17.4's dev loop; 17.4's AC9.6 (*"``-135``..``-146`` are not
    edited"*) is amended to exactly this extent and to no other.

    ⛔ **The residual risk is the same one ``DN-17-2-12`` disclosed** and is bounded by the same
    convention ``-78`` already relies on: a future ``(17-3)``-scoped commit that writes
    successor output without carrying the tag would not be seen. It is disclosed here rather
    than hidden.

    **Non-vacuity FIRST:** a control path KNOWN to carry commits of this story's arc is
    asserted NON-empty, through the SAME function and the SAME range and tag filter the claim
    uses. A misspelled pathspec — or a scope filter that matches nothing — returns empty and
    reads exactly like a clean history: the failure mode ``-75``/``-94``/``-139`` already
    answered, reused here.

    **Executed mutations, two, and neither touches disk in this repository.** The return
    expression is altered in the parsed source text and the SAME comparison is driven over it
    — RED. And part (2)'s re-scoped claim is driven RED at its real seam against a synthetic
    ``(17-3)``-tagged commit that creates a declared prefix, built in a THROWAWAY repository
    under ``tmp_path`` (Story 17.4 ``DN-17-4-5``; ⛔ never against this object database, which
    a peer session commits to). ⛔ A guard that cannot go red is worse than the one it replaced.
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

    # ---- (2) NO COMMIT OF THIS STORY'S ARC created a successor-output prefix -----------
    # ⛔ RE-SCOPED 2026-08-26 by operator decision from a FILESYSTEM existence check to this
    # claim over this story's OWN commit range — see the docstring for the decision, the
    # DN-17-2-12 precedent it reuses, and the two alternatives that were rejected.
    from scripts.precision_preregistration import SUCCESSOR_OUTPUT_PATHS

    from tests.test_successor_output_ordering import (
        CONTROL_PATH_WITH_COMMITS,
        build_violating_history,
        commits_touching_prefixes,
    )

    assert len(SUCCESSOR_OUTPUT_PATHS) == 2, "the pre-registered output prefixes moved"
    assert all(
        prefix and not prefix.startswith("/") and "\\" not in prefix
        for prefix in SUCCESSOR_OUTPUT_PATHS
    ), (
        f"every SUCCESSOR_OUTPUT_PATHS entry must be repository-relative and forward-slash to "
        f"work as a git pathspec on both the Windows local gate and the ubuntu CI matrix; got "
        f"{list(SUCCESSOR_OUTPUT_PATHS)}."
    )

    arc = f"{_BASELINE_COMMIT}..HEAD"

    def this_arc(hits: list[tuple[str, str]] | tuple[tuple[str, str], ...]) -> dict[str, str]:
        return {sha[:7]: subject for sha, subject in hits if _STORY_TAG in subject}

    # ── Non-vacuity: the range, the scope filter and the pathspec all FIND things. ──
    arc_control = this_arc(
        commits_touching_prefixes(_REPO_ROOT, (CONTROL_PATH_WITH_COMMITS,), arc)
    )
    assert arc_control, (
        f"no {_STORY_TAG} commit in {arc} touches the control path "
        f"{CONTROL_PATH_WITH_COMMITS!r}, which this story is known to have written. The range, "
        f"the scope filter or the pathspec is broken, and an invocation that finds nothing "
        f"reports a clean history for a dirty one. Fix the invocation, never the assertion."
    )

    # ── THE CLAIM: this story's arc created no successor output. ──
    created = this_arc(commits_touching_prefixes(_REPO_ROOT, SUCCESSOR_OUTPUT_PATHS, arc))
    assert not created, (
        f"{created!r} — commit(s) of THIS story's arc touch a declared successor-output prefix "
        f"{list(SUCCESSOR_OUTPUT_PATHS)}. This story commits S1's CODE and never its OUTPUT "
        f"over a corpus member (AC6.4); committing one scored row here would make Story 17.4's "
        f"ancestry guard argue about a commit nobody planned."
    )

    # ── ⛔ EXECUTED RED DEMONSTRATION of the re-scoped claim, at its real seam. ──
    history = build_violating_history(tmp_path, story_tag=_STORY_TAG)
    rogue_arc = f"{history.rogue_base}..{history.offender}"
    assert this_arc(
        commits_touching_prefixes(history.repo, (CONTROL_PATH_WITH_COMMITS,), rogue_arc)
    ), "the throwaway control is empty, so its RED result below would be unattributable"
    demonstrated = this_arc(
        commits_touching_prefixes(history.repo, SUCCESSOR_OUTPUT_PATHS, rogue_arc)
    )
    assert demonstrated and history.offender[:7] in demonstrated, (
        f"a synthetic {_STORY_TAG} commit that CREATES {SUCCESSOR_OUTPUT_PATHS[0]!r} was not "
        f"reported by the same query the claim above is made with (got {demonstrated!r}). The "
        f"re-scoped part (2) cannot go RED, which would make it worse than the filesystem "
        f"check it replaced."
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
