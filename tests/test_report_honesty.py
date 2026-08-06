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
    # The row-2 callout is UNCHANGED by Story 8.3 — pinned verbatim.
    assert "Repository is NOT ready for release — 1 verdict-blocking finding(s)." in text


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
    # RE-POINTED (Story 8.3 / AC6). The caveat used to say the clause "would still
    # block". Under the amended FR16 table an unmet critical clause with zero findings
    # is row 4 — it WITHHOLDS `RELEASE_READY`, it does not block — so the old wording
    # was itself the over-promise's mirror image. Same subject, stricter claim: the
    # hint must name the surviving gate AND the effect it actually has.
    assert (
        "Note that the critical-subsystem clause would still withhold `RELEASE_READY`."
        in text
    )
    assert "would still block" not in text


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


# ─────────────────────────────────────────────────────────────────────────────
# 4 — Story 8.3 / DR-11: a row-2 report names the FINDING and nothing else
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_REPORT_002_24_row_2_names_only_the_findings() -> None:
    """TC-ArgusAgent-REPORT-002-24 — AC6: no reason the table never evaluated.

    (Renumbered from ``-002-17`` at review finding R2: ``test_plain_english.py`` already
    owned ``-002-17`` in the same ``TC-ArgusAgent-REPORT-002-NN`` area, and a duplicate
    id breaks the ``TC-<AREA>-<SEQ>-<SUBSEQ>`` uniqueness convention and makes the AC
    map ambiguous. Subject and every assertion are unchanged by the renumber.)

    The amended FR16 table is evaluated IN ORDER and SHORT-CIRCUITS: when row 2 fires,
    rows 3 and 4 were never reached, so the coverage threshold and the critical-
    subsystem clause are not causes of anything. Measured before the fix, a diluted
    row-2 run printed ``1 verdict-blocking finding(s); deep coverage `20/63` is below
    the `3/5` release threshold`` and a NOTE claiming "this coverage result is driven
    by test-file dilution" — a coverage story told about a FINDINGS result. That is
    the mirror image of DF-8-1-A and equally false.

    The work LIST is a different thing from a reason CLAUSE, and review finding R1 is
    what happens when the two are conflated: suppressing the clause also dropped the
    named critical files, while ``render_ship_readiness`` kept counting them and
    pointing here. So this case now pins both halves — no false reason, and the list
    still present under an explicitly NON-causal lead.
    """
    from tests.test_verdict_gate import _ast_finding

    ledger = _diluted_ledger()
    verdict = evaluate_verdict(
        ledger,
        (_ast_finding(),),
        critical_subsystems_all_deep=False,
        critical_subsystems_not_deep=("src/m0.py",),
    )
    text = _render(ledger, verdict)

    assert verdict.verdict.value == "NOT_READY_FOR_RELEASE"
    assert verdict.blocking_finding_count == 1
    # The one true reason survives, unchanged.
    assert "Repository is NOT ready for release — 1 verdict-blocking finding(s)." in text
    # …and nothing the short-circuited table never evaluated is presented as a reason.
    assert "release threshold" not in text
    assert "critical subsystem is not audited deep" not in text
    assert "test-file dilution" not in text
    # R1: the work list IS rendered, and says outright that it caused nothing here.
    assert "### Critical subsystems below `audited_deep` (1)" in text
    assert "| `src/m0.py` |" in text
    assert "Not the reason for this verdict" in text
    assert "These withheld `RELEASE_READY` (FR16)." not in text


# ─────────────────────────────────────────────────────────────────────────────
# 5 — Story 8.3 / AC7: the critical-blocker section and its guidance
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_REPORT_002_18_empty_critical_set_makes_no_critical_claim() -> None:
    """TC-ArgusAgent-REPORT-002-18 — AC7: an empty set renders NOTHING, either way.

    Story 8.2's eligibility filter can empty the critical set entirely, so a row-4 run
    blocked on coverage ALONE must carry no critical-subsystem sentence — neither a
    block naming a gate that is satisfied, nor a positive claim that criticals were
    examined (which would be true only vacuously).
    """
    coverage_only = CoverageLedger.build(
        (
            _entry("src/a.py", _DEEP),
            _entry("src/b.py", _DEEP),
            _entry("src/c.py", _SHALLOW),
            _entry("src/d.py", _SHALLOW),
            _entry("src/e.py", _SHALLOW),
        )
    )
    row_4 = evaluate_verdict(coverage_only)  # 2/5 deep, nothing found → row 4
    assert row_4.critical_subsystems_not_deep == ()
    assert row_4.critical_subsystems_all_deep is True

    text = _render(coverage_only, row_4)

    assert "Critical subsystems below" not in text
    assert "critical subsystem is not audited deep" not in text
    for phrase in (
        "all critical",
        "every critical",
        "all criticals",
        "criticals examined",
        "critical subsystems examined deeply",
        "critical subsystems were examined",
    ):
        assert phrase not in text.lower()


def test_TC_ArgusAgent_REPORT_002_19_critical_blocker_table_is_non_ascii_safe() -> None:
    """TC-ArgusAgent-REPORT-002-19 — AI-E1-1 + AC7: the corrected guidance, on a real path.

    Standing requirement since Epic 1's only review FAIL: adversarial non-ASCII
    coverage is discharged with an actual non-ASCII path, not a sentence. This story
    renders critical paths into a Markdown table, so the pin puts a Cyrillic/accented
    path through it and checks the AC7 guidance rewrite in the same breath.
    """
    non_ascii = "src/расчёт/café_auth.py"
    ledger = CoverageLedger.build(
        (
            _entry("src/a.py", _DEEP),
            _entry("src/b.py", _DEEP),
            _entry("src/c.py", _DEEP),
            _entry(non_ascii, _SHALLOW),
        )
    )
    verdict = evaluate_verdict(
        ledger,
        (),
        critical_subsystems_all_deep=False,
        critical_subsystems_not_deep=(non_ascii,),
    )
    text = _render(ledger, verdict)

    assert f"| `{non_ascii}` | `audited_shallow` |" in text
    # AC7 — the guidance no longer implies an ungradable file could be listed by
    # accident: FR4/DR-5 already removes those automatically…
    assert "already dropped from the heuristic critical set" in text
    # …and it states the ONE exception, the DR-6 operator designation.
    assert "--critical-subsystem" in text
    assert "exempt" in text
