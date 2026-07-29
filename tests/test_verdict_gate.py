"""Tests for the PURE verdict gate (Story 1.6).

Verification area ArgusAgent-VERDICT (TC-ArgusAgent-VERDICT-001-NN). Covers FR15/FR16/FR8/
FR33/FR18, NFR-D2/D3, AR3/AR4/AR8, and cross-cutting #6 (the advisory-by-contract
moat). These are pure-function / model golden tests — zero LLM tokens, no temp
dirs for the module under test.
"""

from __future__ import annotations

import ast
from fractions import Fraction
from pathlib import Path

import pytest

from argus.detectors.base import FindingDraft, build_recording
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
    grade_entry,
)
from argus.ledger.recording import Recording
from argus.store import canonical
from argus.store.envelope import compute_content_hash
from argus.verdict.verdict_gate import (
    BLOCKED,
    INSUFFICIENT_COVERAGE_FLOOR,
    RELEASE_READY_DEEP_THRESHOLD,
    AuditVerdict,
    Verdict,
    blocking_finding_count,
    evaluate_verdict,
    exit_code_for_verdict,
    is_verdict_blocking,
    order_findings,
)


# ── ledger / finding builders (mirror the 1.5 locked eligibility surface) ──


def _entry(file_path: str, depth: CoverageDepth) -> CoverageLedgerEntry:
    return grade_entry(
        file_path=file_path,
        proposed_depth=depth,
        claim_present=depth is CoverageDepth.AUDITED_DEEP,
    )


def _ledger(*depths: CoverageDepth) -> CoverageLedger:
    """Build a ledger of N entries with the given depths (unique file paths)."""
    entries = [_entry(f"f{i}.py", depth) for i, depth in enumerate(depths)]
    return CoverageLedger.build(entries)


def _ledger_ratio(deep: int, total: int) -> CoverageLedger:
    """Build a ledger with exactly ``deep`` audited_deep + the rest shallow."""
    depths = [CoverageDepth.AUDITED_DEEP] * deep
    depths += [CoverageDepth.AUDITED_SHALLOW] * (total - deep)
    return _ledger(*depths)


def _heuristic_finding(file_path: str = "t.py", start: int = 1) -> Recording:
    """The 1.5 heuristic-only finding: advisory + depth_supported=None (ineligible)."""
    draft = FindingDraft(
        file_path=file_path,
        start_line=start,
        end_line=start,
        rule_id="vacuous_test_heuristic",
        advisory=True,
    )
    return build_recording(draft, depth_supported=None)


def _ast_finding(file_path: str = "t.py", start: int = 1) -> Recording:
    """The 1.5 AST-corroborated finding: advisory + depth_supported=AUDITED_SHALLOW (eligible)."""
    draft = FindingDraft(
        file_path=file_path,
        start_line=start,
        end_line=start,
        rule_id="vacuous_test_ast",
        advisory=True,
    )
    return build_recording(draft, depth_supported=CoverageDepth.AUDITED_SHALLOW)


# ── AC9 — vocabulary membership pin ──


class TestVerdictVocabulary:
    def test_TC_ArgusAgent_VERDICT_001_01_membership_is_exactly_three(self) -> None:
        assert {v.value for v in Verdict} == {
            "RELEASE_READY",
            "NOT_READY_FOR_RELEASE",
            "INSUFFICIENT_COVERAGE",
        }
        assert len(Verdict) == 3

    def test_TC_ArgusAgent_VERDICT_001_02_blocked_is_shorthand_for_not_ready(self) -> None:
        # BLOCKED is the documented demo shorthand, NOT a fourth member.
        assert BLOCKED is Verdict.NOT_READY_FOR_RELEASE
        assert "BLOCKED" not in {v.name for v in Verdict}

    def test_TC_ArgusAgent_VERDICT_001_03_no_error_verdict_member(self) -> None:
        # crash is an exit code (1), never a verdict.
        assert "ERROR" not in {v.name for v in Verdict}
        assert "CRASH" not in {v.name for v in Verdict}


# ── AC2 — three-way verdict + thresholds ──


class TestThreeWayVerdict:
    def test_TC_ArgusAgent_VERDICT_001_10_release_ready(self) -> None:
        # 60% deep (3/5), 0 blocking → RELEASE_READY.
        av = evaluate_verdict(_ledger_ratio(deep=3, total=5))
        assert av.verdict is Verdict.RELEASE_READY
        assert av.exit_code == 0

    def test_TC_ArgusAgent_VERDICT_001_11_not_ready_low_deep(self) -> None:
        # 40% deep (2/5), 0 blocking → NOT_READY (enough to assess, gate unmet).
        av = evaluate_verdict(_ledger_ratio(deep=2, total=5))
        assert av.verdict is Verdict.NOT_READY_FOR_RELEASE
        assert av.exit_code == 2

    def test_TC_ArgusAgent_VERDICT_001_12_not_ready_blocking_finding(self) -> None:
        # 100% deep but ≥1 verdict-eligible finding → NOT_READY.
        av = evaluate_verdict(_ledger_ratio(deep=5, total=5), [_ast_finding()])
        assert av.verdict is Verdict.NOT_READY_FOR_RELEASE
        assert av.exit_code == 2

    def test_TC_ArgusAgent_VERDICT_001_13_insufficient_coverage(self) -> None:
        # 10% deep (1/10) → below floor → INSUFFICIENT_COVERAGE.
        av = evaluate_verdict(_ledger_ratio(deep=1, total=10))
        assert av.verdict is Verdict.INSUFFICIENT_COVERAGE
        assert av.exit_code == 3

    def test_TC_ArgusAgent_VERDICT_001_14_never_default_block_clean_ready(self) -> None:
        # A clean ledger with adequate coverage + no findings is READY, not blocked.
        av = evaluate_verdict(_ledger_ratio(deep=3, total=5), [])
        assert av.verdict is Verdict.RELEASE_READY


# ── AC2 — exact boundary semantics (19.99 / 20 / 59.99 / 60) ──


class TestBoundaries:
    def test_TC_ArgusAgent_VERDICT_001_20_just_below_floor(self) -> None:
        # 19.99% → below 20% strict → INSUFFICIENT_COVERAGE.
        av = evaluate_verdict(_ledger_ratio(deep=1999, total=10000))
        assert av.deep_ratio < INSUFFICIENT_COVERAGE_FLOOR
        assert av.verdict is Verdict.INSUFFICIENT_COVERAGE

    def test_TC_ArgusAgent_VERDICT_001_21_exactly_floor_is_assessable(self) -> None:
        # Exactly 20% → assessable (not below floor) → NOT_READY (< 60%).
        av = evaluate_verdict(_ledger_ratio(deep=1, total=5))
        assert av.deep_ratio == INSUFFICIENT_COVERAGE_FLOOR
        assert av.verdict is Verdict.NOT_READY_FOR_RELEASE

    def test_TC_ArgusAgent_VERDICT_001_22_just_below_ready(self) -> None:
        # 59.99% → below 60% → NOT_READY.
        av = evaluate_verdict(_ledger_ratio(deep=5999, total=10000))
        assert av.deep_ratio < RELEASE_READY_DEEP_THRESHOLD
        assert av.verdict is Verdict.NOT_READY_FOR_RELEASE

    def test_TC_ArgusAgent_VERDICT_001_23_exactly_ready_inclusive(self) -> None:
        # Exactly 60% → RELEASE_READY (>= inclusive).
        av = evaluate_verdict(_ledger_ratio(deep=3, total=5))
        assert av.deep_ratio == RELEASE_READY_DEEP_THRESHOLD
        assert av.verdict is Verdict.RELEASE_READY


# ── AC3 — inferred (and skipped/tool_scanned/shallow) never satisfy the gate ──


class TestInferredNeverSatisfies:
    def test_TC_ArgusAgent_VERDICT_001_30_all_inferred_is_insufficient(self) -> None:
        led = _ledger(*([CoverageDepth.INFERRED] * 10))
        av = evaluate_verdict(led)
        assert av.deep_count == 0
        assert av.deep_ratio == Fraction(0, 1)
        assert av.verdict is Verdict.INSUFFICIENT_COVERAGE

    def test_TC_ArgusAgent_VERDICT_001_31_only_deep_counts_toward_numerator(self) -> None:
        # 3 deep + a mix of every other non-deep state in the denominator.
        led = _ledger(
            CoverageDepth.AUDITED_DEEP,
            CoverageDepth.AUDITED_DEEP,
            CoverageDepth.AUDITED_DEEP,
            CoverageDepth.AUDITED_SHALLOW,
            CoverageDepth.INFERRED,
            CoverageDepth.TOOL_SCANNED_ONLY,
            CoverageDepth.SKIPPED,
        )
        av = evaluate_verdict(led)
        assert av.deep_count == 3
        assert av.total_count == 7
        assert av.deep_ratio == Fraction(3, 7)  # < 60% → NOT_READY
        assert av.verdict is Verdict.NOT_READY_FOR_RELEASE

    def test_TC_ArgusAgent_VERDICT_001_32_shallow_does_not_inflate_to_ready(self) -> None:
        # 50% deep + 50% shallow → 50% < 60% → NOT_READY (shallow not in numerator).
        led = _ledger(
            CoverageDepth.AUDITED_DEEP,
            CoverageDepth.AUDITED_SHALLOW,
        )
        av = evaluate_verdict(led)
        assert av.deep_ratio == Fraction(1, 2)
        assert av.verdict is Verdict.NOT_READY_FOR_RELEASE


# ── AC4 — advisory-by-contract moat (THE keystone) ──


class TestAdvisoryByContractMoat:
    def test_TC_ArgusAgent_VERDICT_001_40_heuristic_only_never_blocks(self) -> None:
        # ≥60% deep + ONLY heuristic-only advisory findings → RELEASE_READY.
        led = _ledger_ratio(deep=3, total=5)
        findings = [_heuristic_finding("a.py"), _heuristic_finding("b.py")]
        av = evaluate_verdict(led, findings)
        assert av.blocking_finding_count == 0
        assert av.verdict is Verdict.RELEASE_READY

    def test_TC_ArgusAgent_VERDICT_001_41_ast_corroborated_blocks(self) -> None:
        # SAME ledger + ≥1 AST-corroborated eligible finding → NOT_READY.
        led = _ledger_ratio(deep=3, total=5)
        findings = [_heuristic_finding("a.py"), _ast_finding("b.py")]
        av = evaluate_verdict(led, findings)
        assert av.blocking_finding_count == 1
        assert av.verdict is Verdict.NOT_READY_FOR_RELEASE

    def test_TC_ArgusAgent_VERDICT_001_42_eligibility_keyed_on_depth_not_advisory(self) -> None:
        # Both 1.5 kinds carry advisory=True; only depth_supported distinguishes.
        heuristic = _heuristic_finding()
        ast_corroborated = _ast_finding()
        assert heuristic.advisory is True
        assert ast_corroborated.advisory is True
        assert is_verdict_blocking(heuristic) is False
        assert is_verdict_blocking(ast_corroborated) is True

    def test_TC_ArgusAgent_VERDICT_001_43_advisory_true_with_depth_still_blocks(self) -> None:
        # A finding carrying a supported depth blocks regardless of advisory flag.
        draft = FindingDraft(
            file_path="x.py", start_line=1, end_line=1, rule_id="r", advisory=True
        )
        finding = build_recording(draft, depth_supported=CoverageDepth.AUDITED_DEEP)
        assert is_verdict_blocking(finding) is True
        assert blocking_finding_count([finding]) == 1


# ── AC5 — deterministic finding ordering (blocking-first, fully tie-broken) ──


class TestFindingOrdering:
    def test_TC_ArgusAgent_VERDICT_001_50_blocking_sorts_before_non_blocking(self) -> None:
        findings = [
            _heuristic_finding("a.py"),
            _ast_finding("b.py"),
            _heuristic_finding("c.py"),
            _ast_finding("d.py"),
        ]
        ordered = order_findings(findings)
        eligibility = [is_verdict_blocking(f) for f in ordered]
        # All eligible (blocking) findings come first.
        assert eligibility == sorted(eligibility, reverse=True)
        assert eligibility[:2] == [True, True]
        assert eligibility[2:] == [False, False]

    def test_TC_ArgusAgent_VERDICT_001_51_order_independent_of_input_order(self) -> None:
        a = _ast_finding("a.py")
        b = _ast_finding("b.py", start=2)
        c = _heuristic_finding("c.py")
        d = _heuristic_finding("d.py", start=2)
        order1 = order_findings([a, b, c, d])
        order2 = order_findings([d, c, b, a])
        order3 = order_findings([c, a, d, b])
        assert order1 == order2 == order3

    def test_TC_ArgusAgent_VERDICT_001_52_total_order_tiebreak_recording_id(self) -> None:
        # Two eligible findings, same rule + depth, differ only by recording_id.
        f1 = _ast_finding("a.py", start=1)
        f2 = _ast_finding("a.py", start=2)
        ordered = order_findings([f2, f1])
        ids = [f.recording_id for f in ordered]
        assert ids == sorted(ids)

    def test_TC_ArgusAgent_VERDICT_001_53_ordered_findings_travel_with_verdict(self) -> None:
        findings = [_heuristic_finding("a.py"), _ast_finding("b.py")]
        av = evaluate_verdict(_ledger_ratio(deep=3, total=5), findings)
        assert av.ordered_findings == order_findings(findings)
        assert is_verdict_blocking(av.ordered_findings[0]) is True


# ── AC7 — exit-code mapping (0/2/3/1 wire contract) ──


class TestExitCodeMapping:
    def test_TC_ArgusAgent_VERDICT_001_60_pins(self) -> None:
        assert exit_code_for_verdict(Verdict.RELEASE_READY) == 0
        assert exit_code_for_verdict(Verdict.NOT_READY_FOR_RELEASE) == 2
        assert exit_code_for_verdict(Verdict.INSUFFICIENT_COVERAGE) == 3

    def test_TC_ArgusAgent_VERDICT_001_61_exhaustive_over_enum(self) -> None:
        # Every verdict member maps to a code (no silent default).
        for verdict in Verdict:
            assert exit_code_for_verdict(verdict) in (0, 2, 3)

    def test_TC_ArgusAgent_VERDICT_001_62_crash_code_reserved_not_emitted(self) -> None:
        # 1 (crash) is reserved for the pipeline; the gate never produces it.
        codes = {exit_code_for_verdict(v) for v in Verdict}
        assert 1 not in codes

    def test_TC_ArgusAgent_VERDICT_001_63_unmapped_member_raises(self) -> None:
        # Guard the guard: a fabricated unmapped member raises (no silent default).
        class FakeVerdict(str):
            pass

        with pytest.raises((ValueError, KeyError, TypeError)):
            exit_code_for_verdict(FakeVerdict("WAT"))  # type: ignore[arg-type]


# ── AC8 — honest degradation: empty/partial ledger never crashes ──


class TestHonestDegradation:
    def test_TC_ArgusAgent_VERDICT_001_70_empty_ledger_is_insufficient(self) -> None:
        av = evaluate_verdict(CoverageLedger.build([]))
        assert av.total_count == 0
        assert av.deep_ratio == Fraction(0, 1)  # divide-by-zero structurally impossible
        assert av.verdict is Verdict.INSUFFICIENT_COVERAGE
        assert av.exit_code == 3

    def test_TC_ArgusAgent_VERDICT_001_71_empty_ledger_with_findings_no_crash(self) -> None:
        # Floor wins even with eligible findings present (precedence pin).
        av = evaluate_verdict(CoverageLedger.build([]), [_ast_finding()])
        assert av.verdict is Verdict.INSUFFICIENT_COVERAGE

    def test_TC_ArgusAgent_VERDICT_001_72_partial_ledger_same_fold(self) -> None:
        # A partial ledger is the SAME pure fold (Epic-3 reuse seam).
        led = _ledger_ratio(deep=2, total=3)  # 66% deep
        av = evaluate_verdict(led)
        assert av.verdict is Verdict.RELEASE_READY


# ── floor-vs-blocking precedence pin (LOCKED: floor wins) ──


class TestFloorVsBlockingPrecedence:
    def test_TC_ArgusAgent_VERDICT_001_80_floor_wins_over_blocking(self) -> None:
        # 10% deep (below floor) + an eligible blocking finding → INSUFFICIENT,
        # NOT NOT_READY. Floor is evaluated first.
        led = _ledger_ratio(deep=1, total=10)
        av = evaluate_verdict(led, [_ast_finding()])
        assert av.blocking_finding_count == 1
        assert av.verdict is Verdict.INSUFFICIENT_COVERAGE


# ── critical-subsystem clause seam (Story 2.3) ──


class TestCriticalSubsystemSeam:
    def test_TC_ArgusAgent_VERDICT_001_85_defaults_satisfied_v1(self) -> None:
        av = evaluate_verdict(_ledger_ratio(deep=3, total=5))
        assert av.critical_subsystems_all_deep is True
        assert av.verdict is Verdict.RELEASE_READY

    def test_TC_ArgusAgent_VERDICT_001_86_critical_not_deep_withholds_ready(self) -> None:
        # ≥60% deep + 0 blocking but a critical subsystem not deep → NOT_READY.
        av = evaluate_verdict(
            _ledger_ratio(deep=3, total=5), critical_subsystems_all_deep=False
        )
        assert av.verdict is Verdict.NOT_READY_FOR_RELEASE


# ── AC6 — frozen result model + golden canonical round-trip ──


GOLDEN_VERDICT_CANONICAL = (
    '{"blocking_finding_count":1,'
    '"counts_by_depth":{"audited_deep":3,"audited_shallow":2,"inferred":0,'
    '"skipped":0,"tool_scanned_only":0},'
    '"critical_subsystems_all_deep":true,"deep_count":3,"deep_ratio":"3/5",'
    '"exit_code":2,'
    '"ordered_findings":[{"advisory":true,"cartridge_id":null,'
    '"claim_present":false,"coverage_envelope_slice":null,'
    '"depth_supported":"audited_shallow",'
    '"locators":[{"ast_span":null,"end_line":1,"file_path":"b.py",'
    '"start_line":1}],"partition_id":"root",'
    '"recording_id":"vacuous_test_ast:'
    'b4c46d6774c2e9b63c115d209eb8faac181115dc36b87dedb6c4a7872486eb56",'
    '"rule_id":"vacuous_test_ast","schema_version":"1"}],'
    '"schema_version":"1","total_count":5,'
    '"verdict":"NOT_READY_FOR_RELEASE"}\n'
)


def _golden_verdict() -> AuditVerdict:
    led = _ledger_ratio(deep=3, total=5)
    return evaluate_verdict(led, [_ast_finding("b.py")])


class TestResultModelGolden:
    def test_TC_ArgusAgent_VERDICT_001_90_frozen_extra_forbid(self) -> None:
        av = _golden_verdict()
        with pytest.raises(Exception):
            av.verdict = Verdict.RELEASE_READY  # type: ignore[misc]
        with pytest.raises(Exception):
            AuditVerdict(  # type: ignore[call-arg]
                verdict=Verdict.RELEASE_READY,
                deep_ratio=Fraction(3, 5),
                deep_count=3,
                total_count=5,
                counts_by_depth={},
                blocking_finding_count=0,
                exit_code=0,
                bogus_field="x",
            )

    def test_TC_ArgusAgent_VERDICT_001_91_deep_ratio_is_fraction_not_float(self) -> None:
        av = _golden_verdict()
        assert isinstance(av.deep_ratio, Fraction)
        assert not isinstance(av.deep_ratio, float)

    def test_TC_ArgusAgent_VERDICT_001_92_canonical_round_trip_no_float(self) -> None:
        av = _golden_verdict()
        payload = av.to_canonical_payload()
        # Serializes through the SINGLE 1.1 serializer with the Fraction → "num/den"
        # encoding, and contains no raw float anywhere.
        text = canonical.dumps(payload)
        assert '"deep_ratio":"3/5"' in text
        restored = canonical.loads(text)
        assert restored["verdict"] == "NOT_READY_FOR_RELEASE"
        assert restored["deep_ratio"] == "3/5"

    def test_TC_ArgusAgent_VERDICT_001_93_content_hash_reproducible(self) -> None:
        h1 = compute_content_hash(_golden_verdict().to_canonical_payload())
        h2 = compute_content_hash(_golden_verdict().to_canonical_payload())
        assert h1 == h2

    def test_TC_ArgusAgent_VERDICT_001_94_golden_canonical_bytes_stable(self) -> None:
        av = _golden_verdict()
        assert canonical.dumps(av.to_canonical_payload()) == GOLDEN_VERDICT_CANONICAL


# ── AC1 — purity: no I/O / clock / uuid / random imports in the module ──


class TestPurity:
    def test_TC_ArgusAgent_VERDICT_001_95_no_forbidden_imports(self) -> None:
        src = Path(
            "argus/verdict/verdict_gate.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(src)
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        forbidden = {"os", "time", "datetime", "uuid", "random", "subprocess", "socket"}
        assert not (imported & forbidden), f"forbidden import(s): {imported & forbidden}"

    def test_TC_ArgusAgent_VERDICT_001_96_imports_only_ledger_models(self) -> None:
        src = Path(
            "argus/verdict/verdict_gate.py"
        ).read_text(encoding="utf-8")
        tree = ast.parse(src)
        argus_modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module.startswith("argus"):
                    argus_modules.add(node.module)
        # The pure terminal fold imports only the 1.2 ledger/finding models.
        assert argus_modules == {
            "argus.ledger.coverage_ledger",
            "argus.ledger.recording",
        }
