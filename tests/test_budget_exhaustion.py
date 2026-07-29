"""Story 3.2 — halt → skip → downgrade → report on budget exhaustion (FR22).

Verification area ArgusAgent-COST (``TC-ArgusAgent-COST-001-70..89``, continuing the 3-1 cost
area). Drivers: ArgusAgent-FR-22 (halt on exhaustion, mark remainder ``skipped``,
downgrade, report honestly — never fabricating / silently overrunning),
ArgusAgent-NFR-C2 (never exceed the ceiling; halt DETERMINISTICALLY — no wall-clock
interrupt), ArgusAgent-NFR-R1 (honest degradation — the skipped remainder is NEVER a
fabricated ``audited_*``), ArgusAgent-FR-8 (``skipped`` in the denominator, never the
deep-% numerator — honored by the UNCHANGED 1.6 gate), ArgusAgent-NFR-D2 (zero-token
pure fold over ``int``), ArgusAgent-NFR-P1 (byte-identical halt point + skipped set +
report across input orderings; no ``float``), ArgusAgent-NFR-S1 (no source / secret /
absolute-host-path bytes in the report), AR4/AR7/AR8/AR10/AR11.

Zero LLM tokens — the halt projection is a pure fold over ``int`` per-unit costs.
"""

from __future__ import annotations

import ast
from fractions import Fraction
from pathlib import Path

import pytest
from pydantic import ValidationError

from argus.cost.budget_governor import (
    BudgetConfig,
    _coerce_breach,
    budget_config_from_budget,
)
from argus.cost.exhaustion import (
    HALT_SCHEMA_VERSION,
    CostUnit,
    ExhaustionError,
    HaltReport,
    build_halt_report,
    project_halt_point,
    would_breach,
)
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    grade_entry,
)
from argus.store import canonical
from argus.verdict.verdict_gate import Verdict, evaluate_verdict

_EXHAUSTION_SOURCE = (
    Path(__file__).resolve().parents[1]
    
    / "argus"
    / "cost"
    / "exhaustion.py"
)


def _units(*pairs: tuple[str, int]) -> tuple[CostUnit, ...]:
    return tuple(CostUnit(path=p, cost=c) for p, c in pairs)


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — deterministic halt point (reuse of the 3-1 >=-hard-ceiling decision)
# ─────────────────────────────────────────────────────────────────────────────


def test_would_breach_reuses_3_1_coerce_breach_at_ceiling_boundary() -> None:
    """TC-ArgusAgent-COST-001-70 — would_breach == the imported _coerce_breach at every boundary.

    The at-ceiling boundary (total == ceiling) is a BREACH (the 3-1 / TC-COST-001-46
    semantic). would_breach delegates to _coerce_breach BY IMPORT — no fork.
    """
    for total in (0, 50, 99, 100, 101, 500):
        assert would_breach(total_credits=total, ceiling_credits=100) == _coerce_breach(
            total_credits=total, ceiling_credits=100
        )
    # total == ceiling is a breach.
    assert would_breach(total_credits=100, ceiling_credits=100) is True
    assert would_breach(total_credits=99, ceiling_credits=100) is False
    # No ceiling → never a breach.
    assert would_breach(total_credits=10_000, ceiling_credits=None) is False


def test_halt_point_stops_at_first_breaching_unit() -> None:
    """TC-ArgusAgent-COST-001-71 — audit stops at the first unit whose inclusion reaches the ceiling."""
    units = _units(("a.py", 5), ("b.py", 5), ("c.py", 5), ("d.py", 5))
    # ceiling 10: a(5)→5 ok, b(5)→10 reaches ceiling → BREACH at b (index 1).
    proj = project_halt_point(units, config=BudgetConfig(ceiling_credits=10))
    assert proj.halted_on_exhaustion is True
    assert proj.halt_index == 1
    assert proj.assessed_paths == ("a.py",)
    assert proj.skipped_paths == ("b.py", "c.py", "d.py")
    assert proj.total_credits == 5


def test_no_ceiling_admits_everything_no_halt() -> None:
    """TC-ArgusAgent-COST-001-72 — no ceiling configured → no halt, every unit assessed (AC6)."""
    units = _units(("a.py", 5), ("b.py", 5), ("c.py", 5))
    proj = project_halt_point(units, config=BudgetConfig(ceiling_credits=None))
    assert proj.halted_on_exhaustion is False
    assert proj.halt_index is None
    assert proj.assessed_paths == ("a.py", "b.py", "c.py")
    assert proj.skipped_paths == ()
    assert proj.total_credits == 15


def test_ceiling_never_reached_no_halt() -> None:
    """TC-ArgusAgent-COST-001-73 — a ceiling the cumulative total never reaches → no halt (AC6)."""
    units = _units(("a.py", 5), ("b.py", 5))
    proj = project_halt_point(units, config=BudgetConfig(ceiling_credits=1000))
    assert proj.halted_on_exhaustion is False
    assert proj.assessed_paths == ("a.py", "b.py")
    assert proj.skipped_paths == ()


def test_halt_point_is_order_independent() -> None:
    """TC-ArgusAgent-COST-001-74 — two input orderings yield the IDENTICAL halt outcome (NFR-P1)."""
    forward = _units(("a.py", 5), ("b.py", 5), ("c.py", 5), ("d.py", 5))
    reversed_units = tuple(reversed(forward))
    cfg = BudgetConfig(ceiling_credits=10)
    p1 = project_halt_point(forward, config=cfg)
    p2 = project_halt_point(reversed_units, config=cfg)
    assert p1 == p2
    assert p1.assessed_paths == ("a.py",)
    assert p1.skipped_paths == ("b.py", "c.py", "d.py")


def test_halt_projection_byte_stable() -> None:
    """TC-ArgusAgent-COST-001-75 — the projection serializes byte-identically twice (NFR-P1)."""
    units = _units(("z.py", 5), ("a.py", 5), ("m.py", 5))
    cfg = BudgetConfig(ceiling_credits=10)
    p1 = project_halt_point(units, config=cfg)
    p2 = project_halt_point(units, config=cfg)
    assert canonical.dumps_bytes(p1.model_dump(mode="json")) == canonical.dumps_bytes(
        p2.model_dump(mode="json")
    )


def test_first_unit_alone_breaches_skips_everything() -> None:
    """TC-ArgusAgent-COST-001-76 — a ceiling smaller than the first unit skips ALL units."""
    units = _units(("a.py", 5), ("b.py", 5))
    proj = project_halt_point(units, config=BudgetConfig(ceiling_credits=3))
    assert proj.halt_index == 0
    assert proj.assessed_paths == ()
    assert proj.skipped_paths == ("a.py", "b.py")
    assert proj.total_credits == 0


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — the skip + downgrade: SKIPPED, never fabricated audited_*; denominator-only
# ─────────────────────────────────────────────────────────────────────────────


def test_skipped_remainder_is_exactly_skipped_never_audited() -> None:
    """TC-ArgusAgent-COST-001-77 — unreached files graded SKIPPED, NEVER audited_* (the keystone)."""
    proj = project_halt_point(
        _units(("a.py", 5), ("b.py", 5), ("c.py", 5)),
        config=BudgetConfig(ceiling_credits=8),
    )
    # a admitted (5<8); b would reach 10 → breach at b → b,c skipped.
    skipped_entries = [
        grade_entry(file_path=p, proposed_depth=CoverageDepth.SKIPPED, claim_present=False)
        for p in proj.skipped_paths
    ]
    assert {e.file_path for e in skipped_entries} == {"b.py", "c.py"}
    for entry in skipped_entries:
        assert entry.depth is CoverageDepth.SKIPPED
        # The honest-degradation keystone: NEVER fabricated as an audited grade.
        assert entry.depth not in (
            CoverageDepth.AUDITED_DEEP,
            CoverageDepth.AUDITED_SHALLOW,
            CoverageDepth.TOOL_SCANNED_ONLY,
            CoverageDepth.INFERRED,
        )
        assert entry.claim_present is False


def test_skipped_in_denominator_not_numerator_through_real_gate() -> None:
    """TC-ArgusAgent-COST-001-78 — skipped lands in total(), never deep_count(); the UNCHANGED gate downgrades (FR8)."""
    # 1 deep audited + 4 skipped-on-exhaustion → deep-% = 1/5 = 20% (at the floor).
    audited = [
        grade_entry(file_path="a.py", proposed_depth=CoverageDepth.AUDITED_DEEP, claim_present=True)
    ]
    skipped = [
        grade_entry(file_path=p, proposed_depth=CoverageDepth.SKIPPED, claim_present=False)
        for p in ("b.py", "c.py", "d.py", "e.py")
    ]
    ledger = CoverageLedger.build(audited + skipped)
    assert ledger.total() == 5
    assert ledger.deep_count() == 1
    verdict = evaluate_verdict(ledger, ())
    # The REAL frozen 1.6 gate (import-verified, NOT forked) folds the partial ledger.
    assert verdict.deep_ratio == Fraction(1, 5)
    # 1/5 = exactly the 20% floor → INSUFFICIENT_COVERAGE is below the floor; the gate
    # decides per its existing thresholds (the floor semantics are Story 3.3).
    assert verdict.verdict in (
        Verdict.INSUFFICIENT_COVERAGE,
        Verdict.NOT_READY_FOR_RELEASE,
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — the partial-ledger verdict over the UNCHANGED gate, degraded, no crash
# ─────────────────────────────────────────────────────────────────────────────


def test_partial_ledger_verdict_degrades_no_crash() -> None:
    """TC-ArgusAgent-COST-001-79 — a heavily-skipped partial ledger folds to a verdict, never crashes."""
    skipped = [
        grade_entry(file_path=f"f{i}.py", proposed_depth=CoverageDepth.SKIPPED, claim_present=False)
        for i in range(10)
    ]
    ledger = CoverageLedger.build(skipped)
    verdict = evaluate_verdict(ledger, ())  # must not raise
    assert verdict.deep_ratio == Fraction(0, 1)
    assert verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert verdict.exit_code == 3


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — the frozen, no-float, secret-safe HaltReport
# ─────────────────────────────────────────────────────────────────────────────


def test_halt_report_built_from_halted_projection() -> None:
    """TC-ArgusAgent-COST-001-80 — the report records assessed vs skipped + halted flag."""
    proj = project_halt_point(
        _units(("a.py", 5), ("b.py", 5), ("c.py", 5)),
        config=BudgetConfig(ceiling_credits=8),
    )
    report = build_halt_report(proj)
    assert report.halted_on_exhaustion is True
    assert report.assessed_files == ("a.py",)
    assert report.assessed_count == 1
    assert report.skipped_on_exhaustion_files == ("b.py", "c.py")
    assert report.skipped_on_exhaustion_count == 2
    assert report.total_credits == 5
    assert report.ceiling_credits == 8
    assert report.schema_version == HALT_SCHEMA_VERSION


def test_non_halted_report_is_populated_and_honest() -> None:
    """TC-ArgusAgent-COST-001-81 — a no-halt run → halted=False, empty skipped, full assessed (AC4)."""
    proj = project_halt_point(
        _units(("a.py", 5), ("b.py", 5)),
        config=BudgetConfig(ceiling_credits=None),
    )
    report = build_halt_report(proj)
    assert report.halted_on_exhaustion is False
    assert report.skipped_on_exhaustion_files == ()
    assert report.skipped_on_exhaustion_count == 0
    assert report.assessed_files == ("a.py", "b.py")
    assert report.assessed_count == 2


def test_halt_report_is_frozen_and_forbids_extra() -> None:
    """TC-ArgusAgent-COST-001-82 — HaltReport is frozen=True, extra=forbid (NFR-M2)."""
    report = HaltReport(
        halted_on_exhaustion=False,
        total_credits=0,
        assessed_count=0,
        skipped_on_exhaustion_count=0,
    )
    with pytest.raises(ValidationError):
        report.halted_on_exhaustion = True  # type: ignore[misc]
    with pytest.raises(ValidationError):
        HaltReport(
            halted_on_exhaustion=False,
            total_credits=0,
            assessed_count=0,
            skipped_on_exhaustion_count=0,
            unknown_field="x",  # type: ignore[call-arg]
        )


def test_halt_report_has_no_float_leaf() -> None:
    """TC-ArgusAgent-COST-001-83 — no float anywhere; the canonical serializer accepts the payload (AR4)."""
    proj = project_halt_point(
        _units(("a.py", 5), ("b.py", 5)), config=BudgetConfig(ceiling_credits=8)
    )
    report = build_halt_report(proj)
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
    # The canonical serializer (the determinism backstop) accepts it without raising.
    canonical.dumps_bytes(payload)


def test_halt_report_no_abs_path_or_source_byte() -> None:
    """TC-ArgusAgent-COST-001-84 — the report payload carries no absolute path / source byte (NFR-S1)."""
    proj = project_halt_point(
        _units(("src/a.py", 5), ("src/b.py", 5)),
        config=BudgetConfig(ceiling_credits=8),
    )
    report = build_halt_report(proj)
    raw = canonical.dumps_bytes(report.to_canonical_payload())
    for sentinel in (b"/home/", b"/Users/", b"C:\\", b"\\\\"):
        assert sentinel not in raw


def test_halt_report_non_ascii_path_round_trips_intact() -> None:
    """TC-ArgusAgent-COST-001-85 — a café/Cyrillic path in the skipped set survives intact (AI-E1-1)."""
    units = _units(("src/café_metrics.py", 5), ("src/модуль.py", 5), ("src/a.py", 5))
    proj = project_halt_point(units, config=BudgetConfig(ceiling_credits=8))
    report = build_halt_report(proj)
    raw = canonical.dumps_bytes(report.to_canonical_payload())
    reloaded = canonical.loads(raw)
    # The non-ASCII paths survive into the skipped set intact.
    all_paths = set(reloaded["assessed_files"]) | set(reloaded["skipped_on_exhaustion_files"])
    assert "src/café_metrics.py" in all_paths
    assert "src/модуль.py" in all_paths
    re_report = HaltReport.model_validate(reloaded)
    assert re_report == report


# ─────────────────────────────────────────────────────────────────────────────
# AC7 — purity (AST scan) / typed-error / FastAPI-free reuse
# ─────────────────────────────────────────────────────────────────────────────


def test_exhaustion_module_is_pure_no_io_clock_random() -> None:
    """TC-ArgusAgent-COST-001-86 — AST scan: no datetime/time/uuid/random/os.getpid/open in exhaustion.py."""
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


def test_malformed_unit_cost_raises_typed_error() -> None:
    """TC-ArgusAgent-COST-001-87 — a float / negative / non-int cost raises ExhaustionError (AR10)."""
    # A float cost is rejected at CostUnit construction (Pydantic int field) OR at
    # projection; assert the typed path through would_breach + projection inputs.
    with pytest.raises(ExhaustionError):
        would_breach(total_credits=1.5, ceiling_credits=10)  # type: ignore[arg-type]
    with pytest.raises(ExhaustionError):
        would_breach(total_credits=10, ceiling_credits=-1)
    with pytest.raises(ExhaustionError):
        would_breach(total_credits=True, ceiling_credits=10)  # type: ignore[arg-type]


def test_project_halt_rejects_non_cost_unit() -> None:
    """TC-ArgusAgent-COST-001-88 — a non-CostUnit element raises ExhaustionError (AR10)."""
    with pytest.raises(ExhaustionError):
        project_halt_point(["a.py"], config=BudgetConfig(ceiling_credits=10))  # type: ignore[list-item]


def test_budget_config_from_budget_zero_is_no_ceiling() -> None:
    """TC-ArgusAgent-COST-001-89 — budget 0 → no ceiling → no halt (the OI3 first-class state)."""
    cfg = budget_config_from_budget(0)
    assert cfg.ceiling_credits is None
    proj = project_halt_point(_units(("a.py", 5), ("b.py", 5)), config=cfg)
    assert proj.halted_on_exhaustion is False
