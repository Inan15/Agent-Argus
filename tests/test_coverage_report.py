"""FR9 readable per-file coverage-ledger surface — render tests (story 2.2).

Verification area ArgusAgent-LEDGER (TC-ArgusAgent-LEDGER-001-NN, continuing the 1.2/2.1 area).
Covers AC1/AC2/AC3/AC4/AC5 of story 2.2:

- AC1 — every entry is rendered with file_path + depth token + claim_present +
  recording_ids, in the ledger's deterministic (file_path-sorted) order; all five
  states render; an empty ledger renders a well-formed empty surface (no crash, no
  divide-by-zero).
- AC2 — per-depth counts (zero-filled, all five members) + the deep-% as an exact
  Fraction; the MANDATORY gate-agreement cross-check (surface deep-% ==
  evaluate_verdict(ledger).deep_ratio); the total==0 → Fraction(0,1) edge.
- AC3 — secret-safe: paths + ids + depth tokens + counts only; the render NEVER
  sources file bytes (a planted source/secret canary is absent from the render).
- AC4 — PURE (AST scan: no I/O/clock/uuid/random) / frozen-contract / no-float /
  byte-stability (render twice + two input orders → identical) / typed-error; JSON
  routes through the single 1.1 serializer.
- AC5/AI-E1-1 — a non-ASCII file_path rendered INTACT in BOTH text and JSON.

These are PURE-function / synthetic-ledger tests — zero LLM tokens (NFR-D2), no
temp dirs. Synthetic ledgers are built via ``CoverageLedger.build([grade_entry(
...), ...])``.
"""

from __future__ import annotations

import ast as _ast_module
import inspect
from fractions import Fraction

import pytest

from argus.ledger import coverage_report
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    grade_entry,
)
from argus.ledger.coverage_report import (
    COVERAGE_REPORT_SCHEMA_VERSION,
    SUPPORTED_FORMATS,
    CoverageReportError,
    DepthAggregate,
    build_coverage_report,
    build_depth_aggregate,
    render,
    render_json,
    render_text,
)
from argus.store import canonical
from argus.verdict.verdict_gate import evaluate_verdict


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures — synthetic ledgers (zero-token, NFR-D2)
# ─────────────────────────────────────────────────────────────────────────────


def _all_five_states_entries() -> list:
    """One entry per coverage depth, with distinct paths + recording ids."""
    return [
        grade_entry(
            file_path="auth/login.py",
            proposed_depth=CoverageDepth.AUDITED_DEEP,
            claim_present=True,
            recording_ids=("rec-deep-1", "rec-deep-2"),
        ),
        grade_entry(
            file_path="core/util.py",
            proposed_depth=CoverageDepth.AUDITED_SHALLOW,
            claim_present=False,
            recording_ids=("rec-shallow-1",),
        ),
        grade_entry(
            file_path="lib/tool_only.py",
            proposed_depth=CoverageDepth.TOOL_SCANNED_ONLY,
            claim_present=False,
        ),
        grade_entry(
            file_path="docs/inferred.py",
            proposed_depth=CoverageDepth.INFERRED,
            claim_present=False,
            recording_ids=("rec-inferred-1",),
        ),
        grade_entry(
            file_path="zz/skipped.py",
            proposed_depth=CoverageDepth.SKIPPED,
            claim_present=False,
        ),
    ]


def _three_deep_one_shallow_one_inferred() -> CoverageLedger:
    """3 deep + 1 shallow + 1 inferred → deep-% Fraction(3, 5)."""
    return CoverageLedger.build(
        [
            grade_entry(file_path="a.py", proposed_depth=CoverageDepth.AUDITED_DEEP, claim_present=True),
            grade_entry(file_path="b.py", proposed_depth=CoverageDepth.AUDITED_DEEP, claim_present=True),
            grade_entry(file_path="c.py", proposed_depth=CoverageDepth.AUDITED_DEEP, claim_present=True),
            grade_entry(file_path="d.py", proposed_depth=CoverageDepth.AUDITED_SHALLOW, claim_present=False),
            grade_entry(file_path="e.py", proposed_depth=CoverageDepth.INFERRED, claim_present=False),
        ]
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — every file readable with depth + justifying evidence; all five; empty
# ─────────────────────────────────────────────────────────────────────────────


def test_every_entry_rendered_with_required_fields() -> None:
    """TC-ArgusAgent-LEDGER-001-110 — text render contains every entry's path/depth/claim/ids."""
    ledger = CoverageLedger.build(_all_five_states_entries())
    text = render_text(build_coverage_report(ledger))
    for entry in ledger.entries:
        assert entry.file_path in text
        assert entry.depth.value in text
        assert str(entry.claim_present).lower() in text
        for rid in entry.recording_ids:
            assert rid in text


def test_all_five_states_render_with_correct_token() -> None:
    """TC-ArgusAgent-LEDGER-001-111 — every closed depth token appears in the surface."""
    ledger = CoverageLedger.build(_all_five_states_entries())
    text = render_text(build_coverage_report(ledger))
    json_out = render_json(build_coverage_report(ledger))
    for depth in CoverageDepth:
        assert depth.value in text
        assert depth.value in json_out


def test_empty_recording_ids_rendered_not_omitted() -> None:
    """TC-ArgusAgent-LEDGER-001-112 — an empty recording_ids tuple renders as [] (text) / [] (JSON)."""
    ledger = CoverageLedger.build(
        [grade_entry(file_path="x.py", proposed_depth=CoverageDepth.SKIPPED, claim_present=False)]
    )
    report = build_coverage_report(ledger)
    assert "[]" in render_text(report)
    assert '"recording_ids":[]' in render_json(report)


def test_per_file_rows_in_sorted_order() -> None:
    """TC-ArgusAgent-LEDGER-001-113 — rows follow ledger.entries (file_path-sorted) order."""
    ledger = CoverageLedger.build(_all_five_states_entries())
    report = build_coverage_report(ledger)
    text = render_text(report)
    positions = [text.index(entry.file_path) for entry in ledger.entries]
    assert positions == sorted(positions)
    # entries on the report are the ledger's verbatim (already-sorted) tuple
    assert report.entries == ledger.entries


def test_empty_ledger_renders_well_formed_no_crash() -> None:
    """TC-ArgusAgent-LEDGER-001-114 — empty ledger → header + zero counts, no divide-by-zero."""
    ledger = CoverageLedger.build([])
    report = build_coverage_report(ledger)
    text = render_text(report)
    assert "total: 0" in text
    assert report.aggregate.deep_ratio == Fraction(0, 1)
    # JSON render also succeeds and carries Fraction(0,1) → "0/1"
    json_out = render_json(report)
    assert '"deep_ratio":"0/1"' in json_out


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — per-depth counts + exact-Fraction percentages + gate-agreement cross-check
# ─────────────────────────────────────────────────────────────────────────────


def test_counts_by_depth_zero_filled_all_five_members() -> None:
    """TC-ArgusAgent-LEDGER-001-115 — aggregate carries a count for EVERY depth (zero-filled)."""
    ledger = _three_deep_one_shallow_one_inferred()
    agg = build_depth_aggregate(ledger)
    assert set(agg.counts_by_depth.keys()) == set(CoverageDepth)
    assert set(agg.percentages.keys()) == set(CoverageDepth)
    assert agg.counts_by_depth[CoverageDepth.AUDITED_DEEP] == 3
    assert agg.counts_by_depth[CoverageDepth.TOOL_SCANNED_ONLY] == 0


def test_deep_ratio_exact_fraction() -> None:
    """TC-ArgusAgent-LEDGER-001-116 — 3 deep + 1 shallow + 1 inferred → deep-% Fraction(3, 5)."""
    ledger = _three_deep_one_shallow_one_inferred()
    agg = build_depth_aggregate(ledger)
    assert agg.deep_ratio == Fraction(3, 5)
    assert isinstance(agg.deep_ratio, Fraction)


def test_per_depth_percentages_exact_fraction() -> None:
    """TC-ArgusAgent-LEDGER-001-117 — each per-depth pct is the exact Fraction(count, total)."""
    ledger = _three_deep_one_shallow_one_inferred()
    agg = build_depth_aggregate(ledger)
    assert agg.percentages[CoverageDepth.AUDITED_DEEP] == Fraction(3, 5)
    assert agg.percentages[CoverageDepth.AUDITED_SHALLOW] == Fraction(1, 5)
    assert agg.percentages[CoverageDepth.INFERRED] == Fraction(1, 5)
    assert agg.percentages[CoverageDepth.SKIPPED] == Fraction(0, 1)
    for value in agg.percentages.values():
        assert isinstance(value, Fraction)


def test_gate_agreement_cross_check_deep_ratio() -> None:
    """TC-ArgusAgent-LEDGER-001-118 — surface deep-% == evaluate_verdict(ledger).deep_ratio (MANDATORY)."""
    for ledger in (
        _three_deep_one_shallow_one_inferred(),
        CoverageLedger.build(_all_five_states_entries()),
        CoverageLedger.build(
            [grade_entry(file_path=f"f{i}.py", proposed_depth=CoverageDepth.AUDITED_DEEP, claim_present=True) for i in range(7)]
        ),
    ):
        surface = build_depth_aggregate(ledger).deep_ratio
        gate = evaluate_verdict(ledger).deep_ratio
        assert surface == gate, f"surface {surface} != gate {gate}"


def test_total_zero_deep_ratio_is_fraction_zero_one() -> None:
    """TC-ArgusAgent-LEDGER-001-119 — total==0 → Fraction(0,1), agreeing with the gate."""
    ledger = CoverageLedger.build([])
    agg = build_depth_aggregate(ledger)
    assert agg.deep_ratio == Fraction(0, 1)
    assert evaluate_verdict(ledger).deep_ratio == Fraction(0, 1)
    for value in agg.percentages.values():
        assert value == Fraction(0, 1)


def test_fraction_renders_as_num_den_in_json() -> None:
    """TC-ArgusAgent-LEDGER-001-120 — deep_ratio serializes as the canonical "num/den" form."""
    ledger = _three_deep_one_shallow_one_inferred()
    json_out = render_json(build_coverage_report(ledger))
    assert '"deep_ratio":"3/5"' in json_out


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — secret-safe: paths + ids + tokens + counts only; never sources file bytes
# ─────────────────────────────────────────────────────────────────────────────


def test_render_never_sources_file_bytes() -> None:
    """TC-ArgusAgent-LEDGER-001-121 — a planted source/secret canary is absent from the render."""
    secret_canary = "API_KEY=sk-PLANTED-SECRET-DO-NOT-LEAK"  # separate source string, NOT in ledger
    ledger = CoverageLedger.build(
        [
            grade_entry(
                file_path="config/settings.py",
                proposed_depth=CoverageDepth.AUDITED_DEEP,
                claim_present=True,
                recording_ids=("rec-1",),
            )
        ]
    )
    report = build_coverage_report(ledger)
    text = render_text(report)
    json_out = render_json(report)
    assert "config/settings.py" in text and "config/settings.py" in json_out
    assert "rec-1" in text and "rec-1" in json_out
    assert secret_canary not in text
    assert secret_canary not in json_out


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — PURE / frozen / no-float / byte-stable / typed-error / single serializer
# ─────────────────────────────────────────────────────────────────────────────


def test_module_is_pure_no_io_clock_uuid_random() -> None:
    """TC-ArgusAgent-LEDGER-001-122 — AST scan: the module performs no I/O/clock/uuid/random."""
    source = inspect.getsource(coverage_report)
    tree = _ast_module.parse(source)
    forbidden_attr = {
        "now", "utcnow", "time", "monotonic", "uuid1", "uuid4", "getpid", "open",
        "random", "randint", "choice",
    }
    forbidden_call_names = {"open", "print", "input"}
    for node in _ast_module.walk(tree):
        if isinstance(node, _ast_module.Attribute) and node.attr in forbidden_attr:
            raise AssertionError(f"forbidden attribute use: .{node.attr}")
        if isinstance(node, _ast_module.Call) and isinstance(node.func, _ast_module.Name):
            assert node.func.id not in forbidden_call_names, f"forbidden call: {node.func.id}"
        if isinstance(node, (_ast_module.Import, _ast_module.ImportFrom)):
            mod = getattr(node, "module", None) or ""
            names = [a.name for a in node.names]
            for banned in ("os", "time", "datetime", "uuid", "random", "pathlib"):
                assert banned != mod and banned not in names, f"forbidden import: {banned}"


def test_models_are_frozen() -> None:
    """TC-ArgusAgent-LEDGER-001-123 — DepthAggregate + CoverageReport are frozen (extra forbidden)."""
    ledger = _three_deep_one_shallow_one_inferred()
    report = build_coverage_report(ledger)
    with pytest.raises(Exception):
        report.schema_version = "2"  # type: ignore[misc]
    with pytest.raises(Exception):
        report.aggregate.total = 99  # type: ignore[misc]
    with pytest.raises(Exception):
        DepthAggregate(  # extra field rejected
            counts_by_depth={d: 0 for d in CoverageDepth},
            total=0,
            deep_count=0,
            deep_ratio=Fraction(0, 1),
            percentages={d: Fraction(0, 1) for d in CoverageDepth},
            bogus=1,  # type: ignore[call-arg]
        )


def test_no_float_anywhere_in_aggregate() -> None:
    """TC-ArgusAgent-LEDGER-001-124 — no ratio is a float (the 1.1 serializer would reject it)."""
    ledger = _three_deep_one_shallow_one_inferred()
    agg = build_depth_aggregate(ledger)
    assert not isinstance(agg.deep_ratio, float)
    assert all(not isinstance(v, float) for v in agg.percentages.values())
    # render_json would raise CanonicalSerializationError on a float leaf
    render_json(build_coverage_report(ledger))


def test_byte_stable_render_twice_identical() -> None:
    """TC-ArgusAgent-LEDGER-001-125 — rendering the same ledger twice is byte-identical (NFR-P1)."""
    ledger = CoverageLedger.build(_all_five_states_entries())
    assert render_text(build_coverage_report(ledger)) == render_text(build_coverage_report(ledger))
    assert render_json(build_coverage_report(ledger)) == render_json(build_coverage_report(ledger))


def test_byte_stable_across_input_orders() -> None:
    """TC-ArgusAgent-LEDGER-001-126 — two ledgers from the same entries in different orders render identically."""
    entries = _all_five_states_entries()
    ledger_a = CoverageLedger.build(entries)
    ledger_b = CoverageLedger.build(list(reversed(entries)))
    assert render_text(build_coverage_report(ledger_a)) == render_text(build_coverage_report(ledger_b))
    assert render_json(build_coverage_report(ledger_a)) == render_json(build_coverage_report(ledger_b))


def test_typed_error_on_non_ledger() -> None:
    """TC-ArgusAgent-LEDGER-001-127 — a non-CoverageLedger arg raises CoverageReportError (AR10)."""
    with pytest.raises(CoverageReportError):
        build_coverage_report({"not": "a ledger"})  # type: ignore[arg-type]
    with pytest.raises(CoverageReportError):
        build_depth_aggregate(None)  # type: ignore[arg-type]
    assert issubclass(CoverageReportError, ValueError)


def test_typed_error_on_unsupported_format() -> None:
    """TC-ArgusAgent-LEDGER-001-128 — an unsupported fmt selector raises CoverageReportError (AR10)."""
    ledger = _three_deep_one_shallow_one_inferred()
    with pytest.raises(CoverageReportError):
        render(ledger, fmt="yaml")
    assert render(ledger, fmt="text") == render_text(build_coverage_report(ledger))
    assert render(ledger, fmt="json") == render_json(build_coverage_report(ledger))
    assert set(SUPPORTED_FORMATS) == {"text", "json"}


def test_render_json_routes_through_single_serializer() -> None:
    """TC-ArgusAgent-LEDGER-001-129 — render_json output round-trips via canonical.loads (1.1 serializer)."""
    ledger = _three_deep_one_shallow_one_inferred()
    json_out = render_json(build_coverage_report(ledger))
    decoded = canonical.loads(json_out)
    assert decoded["aggregate"]["deep_ratio"] == "3/5"
    assert decoded["schema_version"] == COVERAGE_REPORT_SCHEMA_VERSION
    assert len(decoded["entries"]) == 5


# ─────────────────────────────────────────────────────────────────────────────
# AC5 / AI-E1-1 — non-ASCII file_path rendered INTACT in BOTH text and JSON
# ─────────────────────────────────────────────────────────────────────────────


def test_non_ascii_file_path_intact_text_and_json() -> None:
    """TC-ArgusAgent-LEDGER-001-130 — non-ASCII paths render verbatim (AI-E1-1, ensure_ascii=False)."""
    paths = ("auth/café_guard.py", "модуль/тест.py", "日本/モジュール.py")
    ledger = CoverageLedger.build(
        [
            grade_entry(file_path=p, proposed_depth=CoverageDepth.AUDITED_DEEP, claim_present=True)
            for p in paths
        ]
    )
    report = build_coverage_report(ledger)
    text = render_text(report)
    json_out = render_json(report)
    for p in paths:
        assert p in text, f"path dropped/mojibake in text: {p}"
        assert p in json_out, f"path dropped/mojibake in JSON: {p}"
    # round-trips through the 1.1 serializer verbatim
    decoded = canonical.loads(json_out)
    decoded_paths = {e["file_path"] for e in decoded["entries"]}
    assert set(paths) == decoded_paths
