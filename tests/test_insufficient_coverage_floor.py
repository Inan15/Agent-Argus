"""Story 3.3 — INSUFFICIENT_COVERAGE floor SEMANTICS under exhaustion (FR16/FR22).

Verification area ArgusAgent-COST (``TC-ArgusAgent-COST-001-95..114``, continuing the 3-1/3-2
cost area). Drivers: ArgusAgent-FR-16 (emit ``INSUFFICIENT_COVERAGE`` below the 20% deep
floor — never a default block; the floor-under-exhaustion SEMANTICS), ArgusAgent-FR-22
(the halt → skip → downgrade → report honest-degradation chain whose floor verdict
this story renders), ArgusAgent-NFR-R1 (an exhaustion condition degrades to a recorded
downgrade — never an uncaught crash or a fabricated result), ArgusAgent-FR-15 (the
verdict is the pure-function gate result this READS, UNCHANGED), ArgusAgent-FR-18 / AR3
(the exit-code wire contract ``0/2/3/1`` is UNCHANGED — ``INSUFFICIENT_COVERAGE →
3``, DISTINCT from ``BLOCKED → 2`` and ``RELEASE_READY → 0``), ArgusAgent-FR-8
(``skipped``/``inferred`` in the denominator, never the deep-% numerator — honored
by the UNCHANGED gate), ArgusAgent-NFR-D2 (deterministic zero-LLM-token — the floor
report is a pure fold over the EXISTING ``AuditVerdict`` + ``HaltReport``),
ArgusAgent-NFR-P1 (byte-identical floor report + message across runs / input-orderings;
no float), ArgusAgent-NFR-S1 (no source / secret / absolute-host-path bytes in the floor
report), ArgusAgent-NFR-M2 (frozen, additive-only contract), AR4/AR8/AR10/AR11.

Zero LLM tokens — the floor report is a pure fold over two in-memory records.
"""

from __future__ import annotations

import ast
from fractions import Fraction
from pathlib import Path

import pytest
from pydantic import ValidationError

from argus.cost.exhaustion import (
    FLOOR_REPORT_SCHEMA_VERSION,
    ExhaustionError,
    HaltReport,
    InsufficientCoverageFloorReport,
    build_floor_report,
)
from argus.detectors.base import FindingDraft, build_recording
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    grade_entry,
)
from argus.ledger.recording import Recording
from argus.store import canonical
from argus.verdict.verdict_gate import (
    INSUFFICIENT_COVERAGE_FLOOR,
    DecisionRow,
    Verdict,
    evaluate_verdict,
)

_EXHAUSTION_SOURCE = (
    Path(__file__).resolve().parents[1]
    
    / "argus"
    / "cost"
    / "exhaustion.py"
)


def _ledger(deep: int, skipped: int) -> CoverageLedger:
    """A synthetic ledger with `deep` audited_deep + `skipped` skipped entries."""
    entries = [
        grade_entry(
            file_path=f"deep_{i}.py",
            proposed_depth=CoverageDepth.AUDITED_DEEP,
            claim_present=True,
        )
        for i in range(deep)
    ]
    entries += [
        grade_entry(
            file_path=f"skip_{i}.py",
            proposed_depth=CoverageDepth.SKIPPED,
            claim_present=False,
        )
        for i in range(skipped)
    ]
    return CoverageLedger.build(entries)


def _halt_report(*, halted: bool, assessed: tuple[str, ...], skipped: tuple[str, ...]) -> HaltReport:
    return HaltReport(
        halted_on_exhaustion=halted,
        total_credits=len(assessed) * 5,
        ceiling_credits=len(assessed) * 5 if halted else None,
        assessed_count=len(assessed),
        assessed_files=tuple(sorted(assessed)),
        skipped_on_exhaustion_count=len(skipped),
        skipped_on_exhaustion_files=tuple(sorted(skipped)),
    )


def _blocking_finding() -> Recording:
    """A verdict-ELIGIBLE (depth_supported is not None) AST-corroborated finding."""
    draft = FindingDraft(
        file_path="deep_0.py",
        start_line=1,
        end_line=1,
        rule_id="vacuous_test_ast",
        advisory=True,
    )
    return build_recording(draft, depth_supported=CoverageDepth.AUDITED_SHALLOW)


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — below-floor-under-exhaustion → INSUFFICIENT_COVERAGE / exit 3,
#       NEVER RELEASE_READY (exit 0), NEVER BLOCKED (exit 2)
# ─────────────────────────────────────────────────────────────────────────────


def test_below_floor_partial_ledger_is_insufficient_coverage_exit_3() -> None:
    """TC-ArgusAgent-COST-001-95 — 1 deep + 9 skipped = 10% deep < 20% → INSUFFICIENT_COVERAGE/exit 3."""
    ledger = _ledger(deep=1, skipped=9)  # 1/10 = 10% < 20%
    verdict = evaluate_verdict(ledger, ())
    assert verdict.deep_ratio == Fraction(1, 10)
    assert verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert verdict.exit_code == 3
    # NEVER the lethal fabricated-ready nor the misleading block.
    assert verdict.verdict is not Verdict.RELEASE_READY
    assert verdict.verdict is not Verdict.NOT_READY_FOR_RELEASE


def test_below_floor_wins_even_with_blocking_finding() -> None:
    """TC-ArgusAgent-COST-001-96 — floor-wins precedence: <20% with a blocking finding is STILL exit 3, not 2."""
    ledger = _ledger(deep=1, skipped=9)  # 10% < 20%
    verdict = evaluate_verdict(ledger, (_blocking_finding(),))
    assert verdict.blocking_finding_count == 1
    # Floor wins: a blocking finding does NOT promote this to NOT_READY_FOR_RELEASE (exit 2).
    assert verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert verdict.exit_code == 3


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — the floor report names the assessed deep-% and distinguishes
#       exhaustion-driven from intrinsic floor
# ─────────────────────────────────────────────────────────────────────────────


def test_floor_report_names_assessed_deep_pct_and_floor() -> None:
    """TC-ArgusAgent-COST-001-97 — the report reuses deep_ratio + floor and renders the PRD J2 message."""
    ledger = _ledger(deep=9, skipped=41)  # 9/50 = 18% < 20%
    verdict = evaluate_verdict(ledger, ())
    assert verdict.deep_ratio == Fraction(9, 50)
    halt = _halt_report(
        halted=True,
        assessed=tuple(f"deep_{i}.py" for i in range(9)),
        skipped=tuple(f"skip_{i}.py" for i in range(41)),
    )
    report = build_floor_report(verdict, halt)
    assert report.deep_ratio == Fraction(9, 50)  # REUSED, exact Fraction
    assert report.floor == INSUFFICIENT_COVERAGE_FLOOR == Fraction(1, 5)
    assert report.below_floor is True
    assert report.verdict == "INSUFFICIENT_COVERAGE"
    assert report.assessed_count == 9
    assert report.skipped_on_exhaustion_count == 41
    # The PRD J2 line: whole-percent from the exact Fraction (18% deep; floor 20%).
    assert report.message == (
        "assessed 18% deep; no repo-wide verdict rendered (floor: 20%)"
    )


def test_floor_report_distinguishes_exhaustion_driven_from_intrinsic() -> None:
    """TC-ArgusAgent-COST-001-98 — driven_by_exhaustion reflects HaltReport.halted_on_exhaustion exactly.

    Two below-floor runs, both INSUFFICIENT_COVERAGE, distinct driven_by_exhaustion:
    one halted (budget ran out), one not (a sparse repo that never cleared 20%).
    """
    ledger = _ledger(deep=1, skipped=9)  # 10% < 20% in both
    verdict = evaluate_verdict(ledger, ())

    halted = _halt_report(
        halted=True, assessed=("deep_0.py",), skipped=tuple(f"skip_{i}.py" for i in range(9))
    )
    intrinsic = _halt_report(
        halted=False,
        assessed=tuple(["deep_0.py"] + [f"skip_{i}.py" for i in range(9)]),
        skipped=(),
    )

    driven = build_floor_report(verdict, halted)
    intrinsic_report = build_floor_report(verdict, intrinsic)

    assert driven.below_floor is True and intrinsic_report.below_floor is True
    assert driven.verdict == intrinsic_report.verdict == "INSUFFICIENT_COVERAGE"
    # The FR22↔FR16 join: distinguishable for a downstream consumer (4.1 / a CI gate).
    assert driven.driven_by_exhaustion is True
    assert intrinsic_report.driven_by_exhaustion is False


def test_floor_report_message_zero_deep_below_floor() -> None:
    """TC-ArgusAgent-COST-001-99 — a 0%-deep below-floor run renders 0% in the message."""
    ledger = _ledger(deep=0, skipped=10)  # 0/10 → total>0, 0% < 20%
    verdict = evaluate_verdict(ledger, ())
    halt = _halt_report(halted=True, assessed=(), skipped=tuple(f"skip_{i}.py" for i in range(10)))
    report = build_floor_report(verdict, halt)
    assert report.deep_ratio == Fraction(0, 1)
    assert report.message == "assessed 0% deep; no repo-wide verdict rendered (floor: 20%)"


def test_floor_report_total_zero_below_floor() -> None:
    """TC-ArgusAgent-COST-001-100 — an empty ledger (total==0) is INSUFFICIENT_COVERAGE, below_floor=True."""
    ledger = CoverageLedger.build([])
    verdict = evaluate_verdict(ledger, ())
    assert verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert verdict.deep_ratio == Fraction(0, 1)
    halt = _halt_report(halted=False, assessed=(), skipped=())
    report = build_floor_report(verdict, halt)
    assert report.below_floor is True
    assert report.message == "assessed 0% deep; no repo-wide verdict rendered (floor: 20%)"


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — INSUFFICIENT_COVERAGE routes to exit 3, DISTINCT from BLOCKED (exit 2)
# ─────────────────────────────────────────────────────────────────────────────


def test_exit_3_distinct_from_exit_2_over_comparable_ledgers() -> None:
    """TC-ArgusAgent-COST-001-101 — a <20% run is exit 3; a 20-60%+blocking run is exit 2 (never conflated)."""
    below = evaluate_verdict(_ledger(deep=1, skipped=9), ())  # 10% < 20% → INSUFFICIENT
    # 5 deep + 5 skipped = 50% (>=20%, <60%) with a blocking finding → NOT_READY (exit 2).
    blocking = evaluate_verdict(_ledger(deep=5, skipped=5), (_blocking_finding(),))

    assert below.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert below.exit_code == 3
    assert blocking.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert blocking.exit_code == 2
    # The three routes are distinct — a low-coverage run is never conflated with a block.
    assert below.exit_code != blocking.exit_code


def test_release_ready_exit_0_distinct() -> None:
    """TC-ArgusAgent-COST-001-102 — RELEASE_READY is exit 0, distinct from both 2 and 3."""
    ready = evaluate_verdict(_ledger(deep=9, skipped=1), ())  # 90% >= 60%, 0 blocking
    assert ready.verdict is Verdict.RELEASE_READY
    assert ready.exit_code == 0
    floor = evaluate_verdict(_ledger(deep=1, skipped=9), ())
    assert {ready.exit_code, floor.exit_code} == {0, 3}


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — above-floor-under-exhaustion → the gate's normal decision (no over-fire)
# ─────────────────────────────────────────────────────────────────────────────


def test_above_floor_under_exhaustion_does_not_over_fire() -> None:
    """TC-ArgusAgent-COST-001-103 — a halt that left >=20% deep does NOT fire the floor.

    Story 8.1: the SUBJECT — the floor must not over-fire on the mere fact of exhaustion —
    is unchanged and is asserted on the FLOOR ROW, which is what "the floor fired" actually
    means. The verdict VALUE moved by design: 30% deep with ZERO blocking findings is FR16
    row 4 (a coverage gate unmet, nothing found), no longer a default block.
    """
    # 3 deep + 7 skipped = 30% (>=20%, <60%), zero findings → row 4, NOT the floor.
    ledger = _ledger(deep=3, skipped=7)
    verdict = evaluate_verdict(ledger, ())
    assert verdict.deep_ratio == Fraction(3, 10)
    assert verdict.decision_row is DecisionRow.GATE_UNMET_NO_FINDINGS
    assert verdict.decision_row is not DecisionRow.BELOW_FLOOR
    halt = _halt_report(
        halted=True,
        assessed=tuple(f"deep_{i}.py" for i in range(3)),
        skipped=tuple(f"skip_{i}.py" for i in range(7)),
    )
    report = build_floor_report(verdict, halt)
    # The floor report reflects a non-floor verdict honestly.
    assert report.below_floor is False
    assert report.driven_by_exhaustion is True
    assert report.message == "assessed 30% deep; verdict rendered: INSUFFICIENT_COVERAGE"


def test_above_floor_exactly_20pct_is_not_below_floor() -> None:
    """TC-ArgusAgent-COST-001-104 — exactly 20% deep is at/above the floor (strict <), not INSUFFICIENT."""
    ledger = _ledger(deep=2, skipped=8)  # 2/10 = 20% — NOT below the strict floor
    verdict = evaluate_verdict(ledger, ())
    assert verdict.deep_ratio == Fraction(1, 5)
    # Story 8.1 / boundary B4: exactly-20% is ASSESSABLE, so the floor row cannot fire
    # here. (It is row 4 — a gate unmet with nothing found — which renders the same
    # verdict value and exit code, which is exactly why the row is what we assert.)
    assert verdict.decision_row is not DecisionRow.BELOW_FLOOR
    assert verdict.is_below_floor is False
    halt = _halt_report(
        halted=True,
        assessed=tuple(f"deep_{i}.py" for i in range(2)),
        skipped=tuple(f"skip_{i}.py" for i in range(8)),
    )
    report = build_floor_report(verdict, halt)
    assert report.below_floor is False


def test_release_ready_floor_report_is_populated_and_honest() -> None:
    """TC-ArgusAgent-COST-001-105 — a RELEASE_READY run still builds a below_floor=False report."""
    ledger = _ledger(deep=9, skipped=1)  # 90% → RELEASE_READY
    verdict = evaluate_verdict(ledger, ())
    halt = _halt_report(halted=False, assessed=tuple(f"deep_{i}.py" for i in range(9)), skipped=())
    report = build_floor_report(verdict, halt)
    assert report.below_floor is False
    assert report.driven_by_exhaustion is False
    assert report.message == "assessed 90% deep; verdict rendered: RELEASE_READY"


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — frozen, no-float, secret-safe report
# ─────────────────────────────────────────────────────────────────────────────


def test_floor_report_is_frozen_and_forbids_extra() -> None:
    """TC-ArgusAgent-COST-001-106 — the report is frozen=True, extra=forbid (NFR-M2)."""
    ledger = _ledger(deep=1, skipped=9)
    verdict = evaluate_verdict(ledger, ())
    halt = _halt_report(halted=True, assessed=("deep_0.py",), skipped=tuple(f"skip_{i}.py" for i in range(9)))
    report = build_floor_report(verdict, halt)
    assert report.schema_version == FLOOR_REPORT_SCHEMA_VERSION
    with pytest.raises(ValidationError):
        report.below_floor = False  # type: ignore[misc]
    with pytest.raises(ValidationError):
        InsufficientCoverageFloorReport(
            verdict="INSUFFICIENT_COVERAGE",
            deep_ratio=Fraction(1, 10),
            floor=INSUFFICIENT_COVERAGE_FLOOR,
            below_floor=True,
            driven_by_exhaustion=True,
            assessed_count=1,
            skipped_on_exhaustion_count=9,
            message="x",
            unknown_field="y",  # type: ignore[call-arg]
        )


def test_floor_report_has_no_float_leaf() -> None:
    """TC-ArgusAgent-COST-001-107 — no float anywhere; the canonical serializer accepts the payload (AR4)."""
    ledger = _ledger(deep=9, skipped=41)
    verdict = evaluate_verdict(ledger, ())
    halt = _halt_report(
        halted=True,
        assessed=tuple(f"deep_{i}.py" for i in range(9)),
        skipped=tuple(f"skip_{i}.py" for i in range(41)),
    )
    report = build_floor_report(verdict, halt)
    payload = report.to_canonical_payload()

    def _assert_no_float(value: object) -> None:
        assert not isinstance(value, float)
        if isinstance(value, dict):
            for v in value.values():
                _assert_no_float(v)
        elif isinstance(value, (list, tuple)):
            for v in value:
                _assert_no_float(v)

    _assert_no_float(payload)
    # The Fraction leaves serialize through the single 1.1 serializer as "num/den".
    raw = canonical.dumps_bytes(payload)
    assert b'"9/50"' in raw  # deep_ratio
    assert b'"1/5"' in raw  # floor


def test_floor_report_no_abs_path_or_source_byte() -> None:
    """TC-ArgusAgent-COST-001-108 — the report payload carries no absolute path / source byte (NFR-S1)."""
    ledger = _ledger(deep=1, skipped=9)
    verdict = evaluate_verdict(ledger, ())
    halt = _halt_report(
        halted=True, assessed=("src/deep_0.py",), skipped=tuple(f"src/skip_{i}.py" for i in range(9))
    )
    report = build_floor_report(verdict, halt)
    raw = canonical.dumps_bytes(report.to_canonical_payload())
    for sentinel in (b"/home/", b"/Users/", b"C:\\", b"\\\\"):
        assert sentinel not in raw


def test_floor_report_round_trips_byte_identically() -> None:
    """TC-ArgusAgent-COST-001-109 — the report re-validates to an EQUAL model + byte-identical (NFR-P1)."""
    ledger = _ledger(deep=9, skipped=41)
    verdict = evaluate_verdict(ledger, ())
    halt = _halt_report(
        halted=True,
        assessed=tuple(f"src/café_{i}.py" for i in range(9)),
        skipped=tuple(f"src/модуль_{i}.py" for i in range(41)),
    )
    report = build_floor_report(verdict, halt)
    raw = canonical.dumps_bytes(report.to_canonical_payload())
    reloaded = canonical.loads(raw)
    re_report = InsufficientCoverageFloorReport.model_validate(reloaded)
    assert re_report == report
    assert canonical.dumps_bytes(re_report.to_canonical_payload()) == raw


# ─────────────────────────────────────────────────────────────────────────────
# AC7 — purity (AST scan) / typed-error / determinism / byte-stability
# ─────────────────────────────────────────────────────────────────────────────


def test_floor_report_is_byte_stable() -> None:
    """TC-ArgusAgent-COST-001-110 — the same inputs → byte-identical report twice (NFR-P1)."""
    ledger = _ledger(deep=9, skipped=41)
    verdict = evaluate_verdict(ledger, ())
    halt = _halt_report(
        halted=True,
        assessed=tuple(f"deep_{i}.py" for i in range(9)),
        skipped=tuple(f"skip_{i}.py" for i in range(41)),
    )
    r1 = build_floor_report(verdict, halt)
    r2 = build_floor_report(verdict, halt)
    assert canonical.dumps_bytes(r1.to_canonical_payload()) == canonical.dumps_bytes(
        r2.to_canonical_payload()
    )


def test_below_floor_predicate_agrees_with_deep_ratio_comparison() -> None:
    """TC-ArgusAgent-COST-001-111 — below_floor AGREES with deep_ratio < floor.

    Pins the locked predicate against the alternative comparison across the boundary
    (including the total==0 short-circuit where deep_ratio is 0/1 < 1/5). THIS is the
    real invariant, and it is unchanged.

    Story 8.1: the second assertion previously read
    ``below_floor == (verdict is INSUFFICIENT_COVERAGE)``. The FR16 amendment FALSIFIES
    that equivalence — ``INSUFFICIENT_COVERAGE`` is now also row 4, above the floor — so
    it is re-pointed to the DISCLOSED row, which is the thing ``below_floor`` is supposed
    to mean. The 30%-deep case below is precisely the one that used to agree by accident
    and would now assert a falsehood.
    """
    cases = [
        _ledger(deep=0, skipped=10),  # 0% < 20%
        _ledger(deep=1, skipped=9),  # 10% < 20%
        _ledger(deep=2, skipped=8),  # 20% — at floor (not below)
        _ledger(deep=3, skipped=7),  # 30% — above
        CoverageLedger.build([]),  # total==0
    ]
    halt = _halt_report(halted=False, assessed=(), skipped=())
    for ledger in cases:
        verdict = evaluate_verdict(ledger, ())
        report = build_floor_report(verdict, halt)
        ratio_below = verdict.deep_ratio < INSUFFICIENT_COVERAGE_FLOOR
        assert report.below_floor == ratio_below
        assert report.below_floor == (verdict.decision_row is DecisionRow.BELOW_FLOOR)


def test_build_floor_report_rejects_non_verdict() -> None:
    """TC-ArgusAgent-COST-001-112 — a non-AuditVerdict argument raises ExhaustionError (AR10)."""
    halt = _halt_report(halted=False, assessed=(), skipped=())
    with pytest.raises(ExhaustionError):
        build_floor_report("not a verdict", halt)  # type: ignore[arg-type]


def test_build_floor_report_rejects_non_halt_report() -> None:
    """TC-ArgusAgent-COST-001-113 — a non-HaltReport argument raises ExhaustionError (AR10)."""
    verdict = evaluate_verdict(_ledger(deep=1, skipped=9), ())
    with pytest.raises(ExhaustionError):
        build_floor_report(verdict, {"halted_on_exhaustion": True})  # type: ignore[arg-type]


def test_exhaustion_module_floor_logic_is_pure() -> None:
    """TC-ArgusAgent-COST-001-114 — AST scan: still no datetime/time/uuid/random/os/open after the 3.3 additions."""
    tree = ast.parse(_EXHAUSTION_SOURCE.read_text(encoding="utf-8"))
    forbidden_attr = {"now", "time", "uuid4", "getpid"}
    forbidden_name = {"open", "random"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in forbidden_attr:
            raise AssertionError(f"impure call .{node.attr} at line {node.lineno}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in forbidden_name, f"impure {node.func.id}() call"
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in {"random", "uuid", "os", "time", "datetime"}, (
                    f"impure import {alias.name}"
                )


def test_message_whole_percent_is_truncation_not_rounding() -> None:
    """TC-ArgusAgent-COST-001-115 — the whole-percent render is exact-Fraction truncation (no float)."""
    # 1/3 → 33.33...% → truncates to 33% deterministically (Fraction arithmetic, never float).
    ledger = _ledger(deep=1, skipped=2)  # 1/3 = 33.3% — above floor
    verdict = evaluate_verdict(ledger, ())
    assert verdict.deep_ratio == Fraction(1, 3)
    halt = _halt_report(halted=True, assessed=("deep_0.py",), skipped=("skip_0.py", "skip_1.py"))
    report = build_floor_report(verdict, halt)
    assert "33% deep" in report.message
