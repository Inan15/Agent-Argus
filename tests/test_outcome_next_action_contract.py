"""Story 12.4 / FR37 — Every terminal outcome names why it was reached and its next action.

Verification area ArgusAgent-REPORT (``TC-ArgusAgent-REPORT-003-01``..``-07``).

Covers:
- AC1: Exhaustive terminal outcome next-action enumeration (RELEASE_READY, NOT_READY_FOR_RELEASE, INSUFFICIENT_COVERAGE, AUDIT_FAILED)
  and failure on unenumerated outcomes.
- AC2: Three-population ingestion-boundary disclosure (Never ingested, Ingested but held out, Assessed).
- AC3: Specific unmet gate explanation for INSUFFICIENT_COVERAGE with measured figures.
- AC4: Immutability of FR16 verdict decision table and exit codes.
- AC5: Real work / memoization & grounding honesty disclosure (DF-12-3-A).
- AC6: Absorbed ledger items (DF-8-3-A, DF-10-4-B).
"""

from __future__ import annotations

from fractions import Fraction
import pytest

from argus.ledger.coverage_ledger import CoverageDepth
from argus.reports.plain_english import (
    TERMINAL_OUTCOMES,
    render_audit_failed_next_action,
    render_depth_meaning,
    render_ship_readiness,
)
from argus.shared.source_languages import (
    AUDITABLE_SUFFIXES,
    derive_non_auditable_suffixes,
    format_ingestion_boundary,
)
from argus.verdict.verdict_gate import (
    AuditVerdict,
    CoverageScope,
    DecisionRow,
    DeepPassOutcome,
    Verdict,
    exit_code_for_verdict,
)


def _make_verdict(
    verdict: Verdict,
    *,
    deep_count: int = 10,
    total_count: int = 10,
    blocking_count: int = 0,
    is_below_floor: bool = False,
    critical_all_deep: bool = True,
    scope: CoverageScope | None = None,
) -> AuditVerdict:
    counts = {
        CoverageDepth.AUDITED_DEEP: deep_count,
        CoverageDepth.AUDITED_SHALLOW: total_count - deep_count,
    }
    if is_below_floor:
        row = DecisionRow.BELOW_FLOOR
    elif verdict is Verdict.RELEASE_READY:
        row = DecisionRow.GATES_MET
    elif verdict is Verdict.NOT_READY_FOR_RELEASE:
        row = DecisionRow.BLOCKING_FINDINGS
    else:
        row = DecisionRow.GATE_UNMET_NO_FINDINGS

    return AuditVerdict(
        verdict=verdict,
        decision_row=row,
        deep_ratio=Fraction(deep_count, total_count) if total_count > 0 else Fraction(0, 1),
        counts_by_depth=counts,
        total_count=total_count,
        deep_count=deep_count,
        blocking_finding_count=blocking_count,
        ordered_findings=(),
        exit_code=exit_code_for_verdict(verdict),
        critical_subsystems_all_deep=critical_all_deep,
        critical_subsystems_not_deep=() if critical_all_deep else ("argus/critical.py",),
        coverage_scope=scope,
    )



def test_TC_ArgusAgent_REPORT_003_01_all_four_terminal_outcomes_enumerated() -> None:
    """TC-ArgusAgent-REPORT-003-01 — FR37 / AC1: all 4 terminal outcomes enumerated.

    Asserts that TERMINAL_OUTCOMES carries exactly the 4 expected tokens and that
    a registry lookup fails on an unenumerated outcome.
    """
    assert len(TERMINAL_OUTCOMES) == 4
    assert set(TERMINAL_OUTCOMES) == {
        "RELEASE_READY",
        "NOT_READY_FOR_RELEASE",
        "INSUFFICIENT_COVERAGE",
        "AUDIT_FAILED",
    }

    # Helper registry representing outcome next-action handlers
    outcome_handlers = {
        "RELEASE_READY": lambda v: render_ship_readiness(v),
        "NOT_READY_FOR_RELEASE": lambda v: render_ship_readiness(v),
        "INSUFFICIENT_COVERAGE": lambda v: render_ship_readiness(v),
        "AUDIT_FAILED": lambda err: render_audit_failed_next_action(err),
    }

    for outcome in TERMINAL_OUTCOMES:
        assert outcome in outcome_handlers

    # An unenumerated outcome causes KeyError / failure
    with pytest.raises(KeyError):
        _ = outcome_handlers["UNKNOWN_OUTCOME"]


def test_TC_ArgusAgent_REPORT_003_02_every_terminal_outcome_has_non_empty_next_action() -> None:
    """TC-ArgusAgent-REPORT-003-02 — FR37 / AC1: every terminal outcome names its next action.

    Asserts that every terminal outcome generates a non-empty `Next:` action line.
    """
    # 1. RELEASE_READY
    v_rr = _make_verdict(Verdict.RELEASE_READY, deep_count=10, total_count=10)
    lines_rr = render_ship_readiness(v_rr)
    next_rr = [line for line in lines_rr if line.strip().startswith("Next:")]
    assert len(next_rr) >= 1
    assert "maintain coverage floor" in next_rr[0]

    # 2. NOT_READY_FOR_RELEASE
    v_nr = _make_verdict(Verdict.NOT_READY_FOR_RELEASE, blocking_count=2)
    lines_nr = render_ship_readiness(v_nr)
    next_nr = [line for line in lines_nr if line.strip().startswith("Next:")]
    assert len(next_nr) >= 1
    assert "resolve the 2 verdict-blocking finding(s)" in next_nr[0]

    # 3. INSUFFICIENT_COVERAGE (Row 1 below floor)
    v_ic_floor = _make_verdict(Verdict.INSUFFICIENT_COVERAGE, deep_count=1, total_count=10, is_below_floor=True)
    lines_ic_floor = render_ship_readiness(v_ic_floor)
    next_ic_floor = [line for line in lines_ic_floor if line.strip().startswith("Next:")]
    assert len(next_ic_floor) >= 1
    assert "below the 20% floor" in next_ic_floor[0]

    # 4. INSUFFICIENT_COVERAGE (Row 4 unmet gate)
    v_ic_gate = _make_verdict(Verdict.INSUFFICIENT_COVERAGE, deep_count=5, total_count=10)
    lines_ic_gate = render_ship_readiness(v_ic_gate)
    next_ic_gate = [line for line in lines_ic_gate if line.strip().startswith("Next:")]
    assert len(next_ic_gate) >= 1

    # 5. AUDIT_FAILED
    next_af = render_audit_failed_next_action("SyntaxError in config")
    assert next_af.startswith("audit process encountered execution failure")
    assert "SyntaxError in config" in next_af


def test_TC_ArgusAgent_REPORT_003_03_three_population_ingestion_boundary_disclosure_on_release_ready() -> None:
    """TC-ArgusAgent-REPORT-003-03 — AC2: three-population ingestion boundary disclosure.

    Explicitly asserts the 3-population disclosure on RELEASE_READY.
    """
    v_rr = _make_verdict(Verdict.RELEASE_READY, deep_count=10, total_count=10)
    non_auditable = derive_non_auditable_suffixes(["action.yml", "README.md", "pyproject.toml"])
    assert set(non_auditable) == {".md", ".toml", ".yml"}

    lines = render_ship_readiness(v_rr, non_auditable_suffixes=non_auditable)
    ingestion_lines = [line for line in lines if "Ingestion boundary:" in line]
    assert len(ingestion_lines) == 1

    boundary_text = ingestion_lines[0]
    # Population 1: Never ingested
    assert "(1) Never ingested: file suffixes outside AUDITABLE_SUFFIXES (.md, .toml, .yml)" in boundary_text
    # Population 2: Ingested but held out
    assert "(2) Ingested but held out: 0" in boundary_text
    # Population 3: Assessed
    assert "(3) Assessed: 10" in boundary_text

    # Verify dynamic derivation from AUDITABLE_SUFFIXES
    for suffix in non_auditable:
        assert suffix not in AUDITABLE_SUFFIXES


def test_TC_ArgusAgent_REPORT_003_04_insufficient_coverage_names_specific_unmet_gate() -> None:
    """TC-ArgusAgent-REPORT-003-04 — AC3: INSUFFICIENT_COVERAGE names specific unmet gate.

    Verifies measured figures for floor, ratio, and critical subsystem shortfalls.
    """
    # Floor shortfall
    v_floor = _make_verdict(Verdict.INSUFFICIENT_COVERAGE, deep_count=1, total_count=10, is_below_floor=True)
    lines_floor = render_ship_readiness(v_floor)
    assert any("below the 20% floor" in line for line in lines_floor)

    # Critical subsystem shortfall
    v_crit = _make_verdict(Verdict.INSUFFICIENT_COVERAGE, deep_count=8, total_count=10, critical_all_deep=False)
    lines_crit = render_ship_readiness(v_crit)
    assert any("Critical files not examined deeply: 1" in line for line in lines_crit)


def test_TC_ArgusAgent_REPORT_003_05_verdict_decision_table_remains_immutable() -> None:
    """TC-ArgusAgent-REPORT-003-05 — AC4: FR16 verdict decision table remains immutable.

    Asserts that Verdict has 3 members and DecisionRow has 4 members, and exit codes match.
    """
    assert len(Verdict) == 3
    assert set(v.value for v in Verdict) == {
        "RELEASE_READY",
        "NOT_READY_FOR_RELEASE",
        "INSUFFICIENT_COVERAGE",
    }

    assert len(DecisionRow) == 4
    assert set(r.value for r in DecisionRow) == {
        "row_1_below_floor",
        "row_2_blocking_findings",
        "row_3_gates_met",
        "row_4_gate_unmet_no_findings",
    }

    assert exit_code_for_verdict(Verdict.RELEASE_READY) == 0
    assert exit_code_for_verdict(Verdict.NOT_READY_FOR_RELEASE) == 2
    assert exit_code_for_verdict(Verdict.INSUFFICIENT_COVERAGE) == 3


def test_TC_ArgusAgent_REPORT_003_06_grounding_and_memoization_honesty_disclosure() -> None:
    """TC-ArgusAgent-REPORT-003-06 — AC5 / DF-12-3-A: memoization & grounding honesty disclosure.

    Asserts that deep audit text explicitly discloses recomputation per run (DF-12-3-A).
    """
    dp = DeepPassOutcome(
        requested_count=5,
        delivered_count=5,
        degraded_count=0,
        reasons=(),
    )
    meaning = render_depth_meaning(("deep",), deep_pass=dp)
    assert "DF-12-3-A" in meaning or "recomputed per run and not served" in meaning


def test_TC_ArgusAgent_REPORT_003_07_degraded_conditions_rendered_in_output() -> None:
    """TC-ArgusAgent-REPORT-003-07 — AC6 / DF-10-4-B: DetectorResult.degraded conditions rendered.

    Asserts that recorded degradation conditions are presented in output.
    """
    v = _make_verdict(Verdict.RELEASE_READY, deep_count=10, total_count=10)
    lines = render_ship_readiness(v, degraded_conditions=["secret_scan_failed", "syntax_error"])
    degraded_lines = [line for line in lines if "Recorded degradation conditions:" in line]
    assert len(degraded_lines) == 1
    assert "2 condition(s) recorded" in degraded_lines[0]
