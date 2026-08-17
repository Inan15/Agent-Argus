"""ArgusAgent-VERDICT — is `NOT_READY_FOR_RELEASE` reachable on the DEFAULT invocation?

Verification area ArgusAgent-VERDICT (``TC-ArgusAgent-VERDICT-001-30``), Story 12.2 / AC6.

THE QUESTION, AND WHY IT IS COMMITTED RATHER THAN RECORDED IN PROSE
-------------------------------------------------------------------
Two statements in the planning corpus were in tension, and the epics frontmatter recorded
the tension honestly as *"both may be true if the paths supply depth differently — not
verified"*:

* ``DOGFOOD_EXTERNALIZATION_GUARD`` asserted that the AST-grounding deep-audit seam is not
  wired in, **so** every finding is advisory / verdict-ineligible (``depth_supported is
  None``) — a CAUSAL claim; while
* the vacuous-test defect cartridge was recorded as emitting a verdict-**blocking**
  finding.

Story 12.2 was required to MEASURE the answer and record it as a yes or a no. **The answer
is YES**, and the escalation branch of AC6 therefore does not fire.

The measurement lives here, as an executable test, rather than only in a story document,
because a prose answer to a question about runtime behaviour rots silently — which is
precisely how the causal claim above survived unchallenged in two committed artifacts. If
a future change makes a blocking verdict unreachable on the default path, this goes red
and somebody has to say so out loud.

WHY IT MATTERS BEYOND THE GUARD SENTENCE
-----------------------------------------
It decides whether *"every finding is advisory"* is a property of the TOOL or a property
of the ARGUS DOGFOOD CORPUS. It is the corpus. A consumer reading Argus's own proof
artifact must not conclude that Argus cannot block their release: it can, with no LLM, no
opt-in and no cartridge harness. Story 12.4 needs this answer to state plainly whether a
blocking verdict is available on the default path.

NO LLM, NO FLAGS, NO HARNESS. The run below is a bare ``argus audit <repo>``.

THE WITNESS WAS RE-AUTHORED ON 2026-08-17, AND WHY THAT IS NOT ADJUSTING A GATE
-------------------------------------------------------------------------------
Story 14.1 replaced the vacuous-test detector's AST corroboration fact (b). It used to
read *"the test constructs a mock"*; cross-cutting concern #6 requires *"the asserted
values do not derive from the SUT output"*, and the two were measured to be the same
answer in 2,527 of 2,529 heuristically-flagged tests across the validation corpus —
on which the rule class emitted 31 blocking findings and the named human adjudicated
**0** of them true.

The fixture this test used to plant did not survive that correction: it bound the SUT
result and asserted it (``result = add(1, 2)`` / ``assert result is not None``), which
is a real, if weak, constraint on the SUT output — so under the corrected predicate it
is advisory, not verdict-eligible. That raised the escalation this test's own failure
message demands, it was escalated, and the operator ruled:

**The question this test asks is about the TOOL, and the answer is still YES.** A
blocking verdict remains reachable on a default, zero-token, no-sign-off run — measured
3/3 on the planted cartridges under the corrected predicate. The default path still
blocks; it merely no longer blocks THIS witness. Recording "the default path no longer
blocks" would therefore have committed a FALSE claim to the README, ``action.yml`` and
Story 12.4.

And the fixture is not evidence. It is a CONSTRUCTED existence proof, engineered
against the old detector — the note below about landing "exactly ON the boundary" says
so in its own words. Replacing a reachability WITNESS is not adjusting a threshold or a
predicate, and no adjudicated sample is touched.

To keep that distinction checkable rather than asserted, ``-30`` now measures **both
arms on the same default path**: the new witness is promoted, and the OLD fixture is
demoted. The second arm is the point — it regression-locks the discrimination Epic 14
exists to create, and turns a fixture edit into a measurement of the intended change.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from argus.cli import main
from argus.detectors.vacuous_test import (
    ASSERTION_DENSITY_FLOOR,
    MOCK_RATIO_CEILING,
    RULE_AST,
    RULE_HEURISTIC,
)
from argus.ledger.coverage_ledger import CoverageDepth
from argus.models import AuditRequest
from argus.pipeline import run_audit_detailed
from argus.verdict.verdict_gate import Verdict

# A GENUINELY VACUOUS test, in the shape the planted cartridges carry: the SUT is
# reached and its result is THROWN AWAY, while the one assertion constrains a value
# bound from a separately configured mock. That is the two-fact AST corroboration
# `argus/detectors/vacuous_test.py` requires — reachability, plus evidence that what is
# asserted does not derive from the SUT.
#
# It is FLAGGED on the density floor: 1 assertion over 5 body statements is 1/5, below
# the 1/4 floor. (The previous fixture cleared the STRICT `>` mock ceiling instead, with
# two mock sites against one SUT call; a naive one-mock/one-call fixture lands exactly
# ON that boundary and fires nothing.) BOTH thresholds are imported and asserted below
# rather than transcribed, so a change to either still fails here loudly.
_VACUOUS_TEST_SOURCE = """from unittest.mock import MagicMock

from app.service import add


def test_add_is_vacuous():
    fake = MagicMock()
    fake.compute.return_value = 3
    add(1, 2)
    pretended = fake.compute()
    assert pretended == 3
"""

# ARM 2's corpus — the fixture this module planted until 2026-08-17, verbatim. It is
# mock-heavy and heuristically vacuous, but `assert result is not None` CONSTRAINS the
# real SUT output, so a correct fact (b) must not corroborate it. Committed here rather
# than deleted because the demotion is the measurable half of Story 14.1: without it,
# nothing in the suite would notice fact (b) silently reverting to "a mock exists".
_SUT_RESULT_ASSERTED_SOURCE = """from unittest.mock import MagicMock

from app.service import add


def test_add_is_vacuous():
    first = MagicMock()
    second = MagicMock()
    result = add(1, 2)
    assert first is not None
    assert second is not None
    assert result is not None
"""

# `-116`'s corpus: the SAME test as `_SUT_RESULT_ASSERTED_SOURCE`, differing ONLY in
# where the line breaks fall. Both continuation syntaxes are planted, because the review
# that found this named one of them and the other — the one PEP 8 actually prefers — was
# broken in exactly the same way. See `-116`'s docstring for the measurement.
_WRAPPED_SOURCES = {
    "parenthesised": """from unittest.mock import MagicMock

from app.service import add


def test_add_is_vacuous():
    first = MagicMock()
    second = MagicMock()
    result = (
        add(1, 2)
    )
    assert first is not None
    assert second is not None
    assert result is not None
""",
    "backslash": """from unittest.mock import MagicMock

from app.service import add


def test_add_is_vacuous():
    first = MagicMock()
    second = MagicMock()
    result = \\
        add(1, 2)
    assert first is not None
    assert second is not None
    assert result is not None
""",
}

_APP_SOURCE = '''"""A small application module with real definitions."""


def add(a: int, b: int) -> int:
    return a + b


def subtract(a: int, b: int) -> int:
    return a - b


def multiply(a: int, b: int) -> int:
    return a * b
'''


def _corpus(root: Path, test_source: str = _VACUOUS_TEST_SOURCE) -> Path:
    (root / "app").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "app" / "service.py").write_text(_APP_SOURCE, encoding="utf-8")
    (root / "tests" / "test_service.py").write_text(test_source, encoding="utf-8")
    return root


def test_TC_ArgusAgent_VERDICT_001_30_a_blocking_verdict_is_reachable_with_no_llm(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-VERDICT-001-30 — AC6.1: the answer is YES, and it is now committed.

    A DEFAULT ``run_audit_detailed`` — no flags, no deep pass, no LLM, no cartridge
    harness — must be able to reach ``NOT_READY_FOR_RELEASE`` with at least one
    verdict-blocking finding, through ``argus/detectors/vacuous_test.py``'s ``RULE_AST``
    finding carrying a non-``None`` ``depth_supported`` (the FR16 row-2 eligibility
    predicate).

    The MECHANISM is asserted, not just the outcome: it must be the AST-corroborated
    vacuous-test rule specifically, because the point of the measurement is that the
    blocking path requires NOTHING — no LLM, and no sign-offs (the Prosecutor promotion
    path is a second producer but needs explicit sign-offs, which a default run has none
    of).

    TWO ARMS, ONE PATH (Story 14.1 / the 2026-08-17 re-authoring — see the module
    docstring). Arm 1 is the reachability answer this test has always carried. Arm 2
    runs the SAME default ``run_audit_detailed`` over the SAME corpus shape with the
    OLD fixture and requires that it is **not** verdict-eligible. Without arm 2 the
    witness swap would be unfalsifiable: a fact (b) that silently reverted to "a mock
    exists" would keep arm 1 green.
    """
    repo = _corpus(tmp_path / "repo")

    result = run_audit_detailed(
        AuditRequest(repo_path=str(repo), commit="HEAD", budget=0, materiality_bar="")
    )
    verdict = result.verdict

    assert verdict.verdict is Verdict.NOT_READY_FOR_RELEASE, (
        "AC6.2 ESCALATION BRANCH: a blocking verdict was NOT reachable on the default "
        f"path (got {verdict.verdict.value}). Do NOT adjust a gate to make this pass — "
        "report it and escalate. The externalization guard's causal claim, and Story "
        "12.4's statement about the default path, both depend on this answer."
    )
    assert verdict.blocking_finding_count >= 1
    assert verdict.exit_code == 2, f"the AR3 wire contract for row 2 is exit 2, got {verdict.exit_code}"

    blocking = [f for f in verdict.ordered_findings if f.depth_supported is not None]
    assert blocking, "no finding carried the row-2 eligibility predicate"
    assert any(f.rule_id == RULE_AST for f in blocking), (
        "the blocking finding did not come from the AST-corroborated vacuous-test rule; "
        f"got {sorted({f.rule_id for f in blocking})}. The measurement is specifically "
        "that the ZERO-TOKEN, NO-SIGN-OFF path can block."
    )
    assert all(f.depth_supported is CoverageDepth.AUDITED_SHALLOW for f in blocking)

    # NO LLM was involved: the deep pass was never requested, so the verdict carries no
    # deep-pass record at all.
    assert verdict.deep_pass is None, (
        "a default run must not even record a deep pass — it did not request one"
    )

    # The thresholds the corpus was built against are IMPORTED, so a future change to
    # either one fails here loudly instead of silently making this fixture non-vacuous.
    assert ASSERTION_DENSITY_FLOOR.numerator == 1 and ASSERTION_DENSITY_FLOOR.denominator == 4
    assert MOCK_RATIO_CEILING.numerator == 1 and MOCK_RATIO_CEILING.denominator == 2

    # ── ARM 2: the same default path, the OLD fixture — the SUT result is bound and
    # asserted, so a correct fact (b) must NOT corroborate it. ────────────────────────
    old_repo = _corpus(tmp_path / "old_repo", test_source=_SUT_RESULT_ASSERTED_SOURCE)
    old = run_audit_detailed(
        AuditRequest(repo_path=str(old_repo), commit="HEAD", budget=0, materiality_bar="")
    ).verdict

    eligible_ast = [
        f
        for f in old.ordered_findings
        if f.rule_id == RULE_AST and f.depth_supported is not None
    ]
    assert not eligible_ast, (
        "a test that ASSERTS THE REAL SUT RESULT was promoted to verdict-eligible. Fact "
        "(b) is supposed to be 'the asserted values do not derive from the SUT output'; "
        "if this fires, it has reverted to 'the test constructs a mock' — the shape that "
        "measured 0 true positives over 31 blocking findings on the validation corpus. "
        "Do NOT relax this to make a witness pass; re-read Story 14.1 / AC1."
    )
    # It is DEMOTED, not made invisible: the heuristic is unchanged, so the finding is
    # still emitted — advisory, carrying no depth for the 1.6 gate to fold.
    advisory = [f for f in old.ordered_findings if f.rule_id == RULE_HEURISTIC]
    assert advisory, "the heuristic flag itself must be unchanged — only PROMOTION moved"
    assert all(f.depth_supported is None for f in advisory)


def test_TC_ArgusAgent_VERDICT_001_116_line_wrapping_alone_cannot_reach_a_blocking_verdict(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-VERDICT-001-116 — Story 14.1 / AC1.3: a 🔴 must not depend on where Enter was pressed.

    WHAT WAS MEASURED, AND WHY THIS ARM IS THE ONE THAT WOULD HAVE CAUGHT IT
    -------------------------------------------------------------------------
    Fact (b) decided whether a SUT call's result was thrown away by reading the text
    preceding the call **on the call's own physical line**. Both of Python's continuation
    syntaxes put the assignment target on an earlier line, so on a default, zero-token,
    no-sign-off run over this very corpus::

        result = add(1, 2)      -> INSUFFICIENT_COVERAGE   RULE_AST=0   (correct)
        result = (
            add(1, 2)           -> NOT_READY_FOR_RELEASE   RULE_AST=1   FALSE ACCUSATION
        )
        result = \\
            add(1, 2)           -> NOT_READY_FOR_RELEASE   RULE_AST=1   FALSE ACCUSATION

    Three spellings of one test, one of them blocking a release. ``-30``'s arm 2 could not
    see it: it plants only the unwrapped spelling, and the predicate-level tests in
    ``tests/test_vacuous_detector.py`` could not prove the *product* consequence. This arm
    is deliberately at the same altitude as ``-30`` — the real ``run_audit_detailed``, no
    flags, no LLM, no harness — because the claim being defended is about what an operator
    experiences, not about a helper's return value.

    The assertion is therefore an EQUIVALENCE, not a threshold: every wrapping of the same
    test must reach the same verdict as the unwrapped one. Writing it that way means a
    future predicate cannot satisfy this by being uniformly stricter or uniformly looser —
    it has to be indifferent to layout, which is the actual requirement.
    """
    baseline = run_audit_detailed(
        AuditRequest(
            repo_path=str(_corpus(tmp_path / "unwrapped", test_source=_SUT_RESULT_ASSERTED_SOURCE)),
            commit="HEAD",
            budget=0,
            materiality_bar="",
        )
    ).verdict
    baseline_eligible = [
        f for f in baseline.ordered_findings if f.rule_id == RULE_AST and f.depth_supported is not None
    ]
    assert not baseline_eligible, (
        "the UNWRAPPED control is already verdict-eligible, so this test cannot measure "
        "anything about wrapping — see -30 arm 2, which owns that regression"
    )

    for label, source in sorted(_WRAPPED_SOURCES.items()):
        wrapped = run_audit_detailed(
            AuditRequest(
                repo_path=str(_corpus(tmp_path / label, test_source=source)),
                commit="HEAD",
                budget=0,
                materiality_bar="",
            )
        ).verdict

        eligible_ast = [
            f
            for f in wrapped.ordered_findings
            if f.rule_id == RULE_AST and f.depth_supported is not None
        ]
        assert not eligible_ast, (
            f"a test that ASSERTS THE REAL SUT RESULT was promoted to verdict-eligible "
            f"purely because the assignment was wrapped with {label} continuation. The "
            "unwrapped spelling of the SAME test is advisory, so this 🔴 is a property of "
            "the source layout, not of the test — the lethal failure class (a false 🔴) "
            "Story 14.1 exists to close, and a violation of AC1.3. Fact (b) must judge the "
            "whole LOGICAL statement containing the call, never the call's physical line; "
            "do NOT special-case one continuation syntax."
        )
        assert wrapped.verdict is baseline.verdict and wrapped.exit_code == baseline.exit_code, (
            f"{label} wrapping changed the VERDICT of an otherwise identical test: "
            f"{baseline.verdict.value} (exit {baseline.exit_code}) -> "
            f"{wrapped.verdict.value} (exit {wrapped.exit_code})"
        )

        # …and it is still SEEN: the heuristic is layout-independent too, so the advisory
        # finding must be present in both. A predicate that went quiet would pass the
        # assertion above by no longer detecting anything at all.
        assert [f for f in wrapped.ordered_findings if f.rule_id == RULE_HEURISTIC], (
            f"the {label}-wrapped test emitted no advisory finding at all — the heuristic "
            "flag itself must not depend on line wrapping either"
        )


def test_TC_ArgusAgent_VERDICT_001_31_the_bare_cli_exits_2_on_that_corpus(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-VERDICT-001-31 — AC6.1: the same answer through the real CLI, end to end.

    Story 12.2. The in-process fold above proves the verdict; this proves an OPERATOR
    experiences it — a bare ``argus audit <repo>`` with no arguments beyond the path.

    ⚠️ The exit code is read from ``main()``'s return value and, in the subprocess leg,
    from ``proc.returncode`` — NEVER through a pipe. Measuring it as ``... | tail`` reports
    the PIPE's status (``0``), not the audit's; that trap cost this measurement a wrong
    answer once already and is recorded so it is not paid for twice.
    """
    repo = _corpus(tmp_path / "repo")

    assert main(["audit", str(repo)]) == 2

    proc = subprocess.run(
        [sys.executable, "-m", "argus.cli", "audit", str(repo)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2, (
        f"a bare CLI invocation must exit 2 on a blocking verdict; got {proc.returncode}"
    )
    assert "verdict=NOT_READY_FOR_RELEASE" in proc.stdout
    assert "blocking_findings=1" in proc.stdout
    # And the run must not claim any deep read, because none was requested.
    assert "a deep read was dispatched" not in proc.stderr
