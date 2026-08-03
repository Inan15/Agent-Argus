"""The final-verdict report must state WHY it blocked, accurately and actionably.

Verification area ArgusAgent-REPORT (TC-ArgusAgent-REPORT-002-NN). The report is the
end-user surface for a decision-support tool; a block an operator cannot act on is a
block they will learn to ignore, and an ignored gate protects nothing.

Pins three properties:

1. The block message names the gate(s) that ACTUALLY failed. It previously read
   "due to blocking findings or unresolved security/correctness rules" directly
   beside "Blocking Findings: 0" — false, and unactionable.
2. A critical-subsystem block NAMES the offending files and the depth each reached.
3. A coverage block caused by test-file dilution SAYS SO, and does not over-promise.
"""

from __future__ import annotations

from fractions import Fraction

from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
)
from argus.models import AuditRequest
from argus.reports.generator import render_final_verdict_report
from argus.verdict.verdict_gate import evaluate_verdict

_DEEP = CoverageDepth.AUDITED_DEEP
_SHALLOW = CoverageDepth.AUDITED_SHALLOW


def _entry(path: str, depth: CoverageDepth) -> CoverageLedgerEntry:
    return CoverageLedgerEntry(
        file_path=path, depth=depth, claim_present=(depth is _DEEP)
    )


def _request() -> AuditRequest:
    return AuditRequest(
        repo_path="/repo", commit="HEAD", budget=100, materiality_bar="default"
    )


def _render(ledger: CoverageLedger, verdict) -> str:
    return render_final_verdict_report(_request(), verdict, ledger, 0)


# ─────────────────────────────────────────────────────────────────────────────
# 1 + 2 — the block names the gate, and names the files
# ─────────────────────────────────────────────────────────────────────────────


def test_critical_block_names_the_gate_and_the_files() -> None:
    """TC-ArgusAgent-REPORT-002-01 — a block with 0 findings must not blame findings."""
    ledger = CoverageLedger.build(
        (
            _entry("src/a.py", _DEEP),
            _entry("src/b.py", _DEEP),
            _entry("src/auth.py", _SHALLOW),
            _entry("src/crypto.py", _SHALLOW),
        )
    )
    verdict = evaluate_verdict(
        ledger,
        (),
        critical_subsystems_all_deep=False,
        critical_subsystems_not_deep=("src/auth.py", "src/crypto.py"),
    )
    text = _render(ledger, verdict)

    assert "Blocking Findings**: **0" in text
    # It must NOT claim findings caused this.
    assert "due to blocking findings" not in text
    assert "critical subsystem is not audited deep" in text
    # …and it must name them, with the depth each actually reached.
    assert "`src/auth.py`" in text
    assert "`src/crypto.py`" in text
    assert "audited_shallow" in text


def test_designated_critical_absent_from_ledger_is_labelled() -> None:
    """TC-ArgusAgent-REPORT-002-02 — 'never examined' is a distinct, honest state."""
    ledger = CoverageLedger.build((_entry("src/a.py", _DEEP), _entry("src/b.py", _DEEP)))
    verdict = evaluate_verdict(
        ledger,
        (),
        critical_subsystems_all_deep=False,
        critical_subsystems_not_deep=("src/ghost.py",),
    )
    text = _render(ledger, verdict)

    assert "`src/ghost.py`" in text
    assert "never examined" in text


def test_blocking_findings_are_named_when_they_are_the_cause() -> None:
    """TC-ArgusAgent-REPORT-002-03 — the honest message still works the other way."""
    from tests.test_verdict_gate import _ast_finding

    ledger = CoverageLedger.build(
        (_entry("src/a.py", _DEEP), _entry("src/b.py", _DEEP), _entry("src/c.py", _DEEP))
    )
    verdict = evaluate_verdict(ledger, (_ast_finding(),))
    text = _render(ledger, verdict)

    assert "1 verdict-blocking finding(s)" in text


# ─────────────────────────────────────────────────────────────────────────────
# 3 — test-file dilution is explained, without over-promising
# ─────────────────────────────────────────────────────────────────────────────


def _diluted_ledger() -> CoverageLedger:
    """40 application files all deep; 86 test files shallow by construction."""
    entries = [_entry(f"src/m{i}.py", _DEEP) for i in range(40)]
    entries += [_entry(f"tests/test_{i}.py", _SHALLOW) for i in range(86)]
    return CoverageLedger.build(tuple(entries))


def test_dilution_hint_appears_and_quantifies_the_gap() -> None:
    """TC-ArgusAgent-REPORT-002-04 — the discoverability fix for an opt-in flag."""
    ledger = _diluted_ledger()
    verdict = evaluate_verdict(ledger)  # default whole-repository scope
    text = _render(ledger, verdict)

    assert "test-file dilution" in text
    assert "40/40" in text  # the application-scope reality
    assert "86 test file(s)" in text
    assert "--coverage-scope application" in text
    # No other gate is unmet here, and the report may say exactly that.
    assert "No other gate is currently unmet." in text


def test_dilution_hint_does_not_over_promise_when_another_gate_blocks() -> None:
    """TC-ArgusAgent-REPORT-002-05 — narrowing clears COVERAGE only; say so.

    Promising RELEASE_READY when the critical clause would still block is the same
    class of dishonesty as the generic block message this work replaced.
    """
    ledger = _diluted_ledger()
    verdict = evaluate_verdict(
        ledger,
        (),
        critical_subsystems_all_deep=False,
        critical_subsystems_not_deep=("src/m0.py",),
    )
    text = _render(ledger, verdict)

    assert "test-file dilution" in text
    assert "Note that the critical-subsystem clause would still block" in text


def test_no_dilution_hint_when_narrowing_would_not_help() -> None:
    """TC-ArgusAgent-REPORT-002-06 — never suggest a flag that changes nothing."""
    # Application files are themselves under-audited: 4/40 deep.
    entries = [_entry(f"src/m{i}.py", _DEEP) for i in range(4)]
    entries += [_entry(f"src/n{i}.py", _SHALLOW) for i in range(36)]
    entries += [_entry(f"tests/test_{i}.py", _SHALLOW) for i in range(86)]
    ledger = CoverageLedger.build(tuple(entries))
    verdict = evaluate_verdict(ledger)
    text = _render(ledger, verdict)

    assert "test-file dilution" not in text


def test_no_dilution_hint_once_already_scoped() -> None:
    """TC-ArgusAgent-REPORT-002-07 — do not suggest what the operator already did."""
    ledger = _diluted_ledger()
    application = frozenset(
        e.file_path for e in ledger.entries if not e.file_path.startswith("tests/")
    )
    verdict = evaluate_verdict(
        ledger,
        (),
        critical_subsystems_all_deep=False,
        critical_subsystems_not_deep=("src/m0.py",),
        scope_paths=application,
    )
    text = _render(ledger, verdict)

    assert "test-file dilution" not in text
    # The dual-ratio disclosure is what a scoped run shows instead.
    assert "assessed scope" in text
    assert "whole repository" in text


def test_release_ready_report_has_no_block_explanation() -> None:
    """TC-ArgusAgent-REPORT-002-08 — a green report stays clean."""
    ledger = CoverageLedger.build(
        (_entry("src/a.py", _DEEP), _entry("src/b.py", _DEEP), _entry("src/c.py", _DEEP))
    )
    verdict = evaluate_verdict(ledger)
    text = _render(ledger, verdict)

    assert verdict.verdict.value == "RELEASE_READY"
    assert "test-file dilution" not in text
    assert "Critical subsystems below" not in text
    assert "NOT ready for release" not in text


def test_ratio_shown_is_the_one_the_gate_used() -> None:
    """TC-ArgusAgent-REPORT-002-09 — a scoped verdict shows BOTH ratios, unambiguously."""
    ledger = _diluted_ledger()
    application = frozenset(
        e.file_path for e in ledger.entries if not e.file_path.startswith("tests/")
    )
    verdict = evaluate_verdict(ledger, (), scope_paths=application)
    text = _render(ledger, verdict)

    assert verdict.coverage_scope is not None
    assert str(verdict.coverage_scope.assessed_deep_ratio) in text
    assert str(verdict.deep_ratio) in text
    assert Fraction(40, 126) == verdict.deep_ratio  # whole-ledger meaning preserved
