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
)
from argus.ledger.coverage_ledger import CoverageDepth
from argus.models import AuditRequest
from argus.pipeline import run_audit_detailed
from argus.verdict.verdict_gate import Verdict

# A test whose assertions are MOCK-DOMINATED while it does reach a real SUT — the two-fact
# AST corroboration `argus/detectors/vacuous_test.py` requires. Two mock construction
# sites against one SUT call gives `mock_ratio = 2/3`, which clears the STRICT `>` ceiling
# of 1/2; a naive one-mock/one-call fixture lands exactly ON the boundary and fires
# nothing. The thresholds are imported and asserted below rather than transcribed.
_VACUOUS_TEST_SOURCE = """from unittest.mock import MagicMock

from app.service import add


def test_add_is_vacuous():
    first = MagicMock()
    second = MagicMock()
    result = add(1, 2)
    assert first is not None
    assert second is not None
    assert result is not None
"""

_APP_SOURCE = '''"""A small application module with real definitions."""


def add(a: int, b: int) -> int:
    return a + b


def subtract(a: int, b: int) -> int:
    return a - b


def multiply(a: int, b: int) -> int:
    return a * b
'''


def _corpus(root: Path) -> Path:
    (root / "app").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "app" / "service.py").write_text(_APP_SOURCE, encoding="utf-8")
    (root / "tests" / "test_service.py").write_text(_VACUOUS_TEST_SOURCE, encoding="utf-8")
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
