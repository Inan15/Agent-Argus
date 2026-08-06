"""Vacuous-test detector + Tier-A AST subset (Story 1.5, AC1/2/3/5/6/7/10).

Verification area ArgusAgent-DETECT (TC-ArgusAgent-DETECT-001-NN). Covers the heuristic score
(fixed-precision ratios / zero-float), advisory-only vs AST-corroborated
eligibility, the MANDATORY false-accusation guard (a genuine well-asserting test
is NOT flagged; a clean/non-test file is NOT flagged), and honest degradation
(un-parseable / no-test-functions → recorded, no flag, no crash).

The pure-logic cases construct an ``AstIndexEntry`` directly; the integration
cases build it from a real tiny fixture via ``build_ast_index`` and so
``importorskip`` tree-sitter (mirrors the 1.4 strategy). The pure heuristic logic
over given counts stays UNCONDITIONALLY tested.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from argus.detectors.vacuous_test import (
    RULE_AST,
    RULE_HEURISTIC,
    VacuousTestDetector,
    is_test_classification_content_dependent,
    is_test_file,
)
from argus.index.ast_index import AstIndexEntry, CodeEdge, Definition
from argus.ledger.coverage_ledger import CoverageDepth
from argus.store import canonical


# ── Pure-logic cases (no tree-sitter) — construct the AstIndexEntry directly ──


def _entry(definitions, edges, *, file_path="tests/test_mod.py") -> AstIndexEntry:
    return AstIndexEntry(
        file_path=file_path,
        ast_eligible=True,
        definitions=tuple(definitions),
        edges=tuple(edges),
    )


def test_is_test_file_rule() -> None:
    """TC-ArgusAgent-DETECT-001-85 — test-file identification (under tests/ or test_*/_test)."""
    assert is_test_file("tests/test_x.py")
    assert is_test_file("pkg/tests/foo.py")
    assert is_test_file("test_thing.py")
    assert is_test_file("thing_test.py")
    assert not is_test_file("argus/detectors/vacuous.py")
    assert not is_test_file("pkg/widget.py")


def test_test_classification_content_dependence_names_the_tier_that_answered() -> None:
    """TC-ArgusAgent-DETECT-001-95 — which TIER decided, exposed for the FR4/DR-5 consumer.

    ``is_test_file`` answers three ways and only ONE of them is a guess: tier 3 reads the
    file's definitions, so for an entry it cannot read it deliberately assumes "test"
    (conservative for grading — it keeps the vacuous-test moat closed). The critical-set
    eligibility filter consumes the same value in the opposite direction, where that
    assumption would drop an unreadable security module out of the gate, so it needs to
    know when the answer was content-derived. Both predicates read ONE tier structure
    (AR7/§3.3), which is why this asserts them together rather than in isolation.
    """
    # tier 1 (location) and tier 2 (reserved name) — properties of what the file IS.
    for path in ("tests/foo_test.py", "pkg/tests/thing.py", "test_thing.py", "svc/x_test.go"):
        assert is_test_file(path)
        assert not is_test_classification_content_dependent(path)

    # tier 3 — the ambiguous Python suffix, the ONE tier resolved by CONTENT.
    for path in ("app/auth_test.py", "svc/token_test.py", "pkg/conftest.py"):
        assert is_test_classification_content_dependent(path)

    # not a test path at all: no tier fired, so nothing was guessed.
    for path in ("argus/detectors/vacuous.py", "pkg/widget.py"):
        assert not is_test_file(path)
        assert not is_test_classification_content_dependent(path)

    # …and the guess itself is unchanged: tier 3 with an unreadable entry stays "test".
    unreadable = AstIndexEntry(file_path="app/auth_test.py", ast_eligible=False, parse_failed=True)
    assert is_test_file("app/auth_test.py", ast_entry=unreadable)


def test_vacuous_mock_dominated_test_flagged_and_corroborated() -> None:
    """TC-ArgusAgent-DETECT-001-86 — a mock-dominated test reaching the SUT is flagged + AST-corroborated."""
    source = (
        "def test_widget():\n"  # line 1
        "    m = Mock()\n"  # 2
        "    dep = MagicMock()\n"  # 3
        "    sut = widget_under_test(m, dep)\n"  # 4
        "    assert sut\n"  # 5 — 1 assert / 4 statements = 1/4 (not < floor),
        # but mock_ratio = 2/3 > 1/2 → flagged; reaches SUT + mock-dominated → corroborated
    )
    defs = [Definition(name="test_widget", kind="function", start_line=1, end_line=5)]
    edges = [
        CodeEdge(callee="Mock", line=2),
        CodeEdge(callee="MagicMock", line=3),
        CodeEdge(callee="widget_under_test", line=4),
    ]
    result = VacuousTestDetector().run(
        file_path="tests/test_widget.py", source=source, ast_entry=_entry(defs, edges)
    )

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.advisory is True
    assert finding.rule_id == RULE_AST  # AST-corroborated → verdict-eligible rule
    assert finding.depth_supported is CoverageDepth.AUDITED_SHALLOW
    assert finding.locators[0].ast_span == "function:test_widget@1-5"
    # graded audited_shallow, never audited_deep
    assert result.entries[0].depth is CoverageDepth.AUDITED_SHALLOW
    assert finding.recording_id in result.entries[0].recording_ids


def test_assertionless_test_flagged_advisory_only_when_no_corroboration() -> None:
    """TC-ArgusAgent-DETECT-001-87 — low-density test with no mock signal → advisory-only (heuristic)."""
    source = (
        "def test_thing():\n"  # 1
        "    do_a()\n"  # 2
        "    do_b()\n"  # 3
        "    do_c()\n"  # 4
        "    result = compute()\n"  # 5
        "    assert result\n"  # 6 — 1 assert / 5 statements = 1/5 < 1/4 → flagged
    )
    defs = [Definition(name="test_thing", kind="function", start_line=1, end_line=6)]
    edges = [
        CodeEdge(callee="do_a", line=2),
        CodeEdge(callee="do_b", line=3),
        CodeEdge(callee="do_c", line=4),
        CodeEdge(callee="compute", line=5),
    ]
    result = VacuousTestDetector().run(
        file_path="tests/test_thing.py", source=source, ast_entry=_entry(defs, edges)
    )
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.advisory is True
    assert finding.rule_id == RULE_HEURISTIC  # NOT corroborated → advisory-only
    assert finding.depth_supported is None  # the 1.6 gate must NOT 🔴 on it


def test_genuine_well_asserting_test_not_flagged_FALSE_ACCUSATION_GUARD() -> None:
    """TC-ArgusAgent-DETECT-001-88 — MANDATORY moat: a genuine test is NOT flagged."""
    source = (
        "def test_add():\n"  # 1
        "    result = add(2, 3)\n"  # 2
        "    assert result == 5\n"  # 3 — 1 assert / 2 statements = 1/2 >= 1/4
    )
    defs = [Definition(name="test_add", kind="function", start_line=1, end_line=3)]
    edges = [CodeEdge(callee="add", line=2)]
    result = VacuousTestDetector().run(
        file_path="tests/test_add.py", source=source, ast_entry=_entry(defs, edges)
    )
    assert result.findings == ()  # NOT flagged
    assert len(result.entries) == 1
    assert result.entries[0].depth is CoverageDepth.AUDITED_SHALLOW


def test_clean_non_test_file_not_flagged_FALSE_ACCUSATION_GUARD() -> None:
    """TC-ArgusAgent-DETECT-001-89 — MANDATORY moat: a non-test file is skipped, not mis-flagged."""
    source = "def widget(x):\n    return x + 1\n"
    defs = [Definition(name="widget", kind="function", start_line=1, end_line=2)]
    result = VacuousTestDetector().run(
        file_path="argus/widget.py",
        source=source,
        ast_entry=_entry(defs, [], file_path="argus/widget.py"),
    )
    assert result.findings == ()
    assert result.entries == ()
    assert len(result.degraded) == 1
    assert result.degraded[0].reason == "not_a_test_file"


def test_parse_failed_entry_degrades_no_flag_no_crash() -> None:
    """TC-ArgusAgent-DETECT-001-90 — a parse_failed entry degrades, never flagged/crashed (AR10)."""
    entry = AstIndexEntry(
        file_path="tests/test_broken.py",
        ast_eligible=False,
        parse_failed=True,
        parse_failure_reason="syntax_error",
    )
    result = VacuousTestDetector().run(
        file_path="tests/test_broken.py", source="def test_(:\n", ast_entry=entry
    )
    assert result.findings == ()
    assert result.degraded[0].reason == "syntax_error"


def test_no_test_functions_degrades() -> None:
    """TC-ArgusAgent-DETECT-001-91 — a test file with no test functions degrades cleanly."""
    source = "def helper():\n    return 1\n"
    defs = [Definition(name="helper", kind="function", start_line=1, end_line=2)]
    result = VacuousTestDetector().run(
        file_path="tests/test_empty.py", source=source, ast_entry=_entry(defs, [])
    )
    assert result.findings == ()
    assert result.degraded[0].reason == "no_test_functions"


def test_ratios_are_fraction_not_float_AR4() -> None:
    """TC-ArgusAgent-DETECT-001-92 — emitted findings serialize through the float-rejecting serializer."""
    source = (
        "def test_v():\n"
        "    m = Mock()\n"
        "    d = MagicMock()\n"
        "    out = run_sut(m, d)\n"
        "    assert out\n"
    )
    defs = [Definition(name="test_v", kind="function", start_line=1, end_line=5)]
    edges = [
        CodeEdge(callee="Mock", line=2),
        CodeEdge(callee="MagicMock", line=3),
        CodeEdge(callee="run_sut", line=4),
    ]
    result = VacuousTestDetector().run(
        file_path="tests/test_v.py", source=source, ast_entry=_entry(defs, edges)
    )
    # The finding payload serializes cleanly through the single (float-rejecting)
    # serializer — proving no float field leaked into the .argus/-bound model.
    payload = result.findings[0].model_dump(mode="json")
    assert canonical.dumps_bytes(payload)


def test_score_density_is_exact_fraction() -> None:
    """TC-ArgusAgent-DETECT-001-93 — the per-test score stores exact Fraction ratios."""
    detector = VacuousTestDetector()
    source = (
        "def test_x():\n"
        "    a()\n"
        "    b()\n"
        "    c()\n"
        "    d()\n"
        "    assert z()\n"
    )
    defn = Definition(name="test_x", kind="function", start_line=1, end_line=6)
    edges = (
        CodeEdge(callee="a", line=2),
        CodeEdge(callee="b", line=3),
        CodeEdge(callee="c", line=4),
        CodeEdge(callee="d", line=5),
        CodeEdge(callee="z", line=6),
    )
    score = detector._score(source.splitlines(), edges, defn)
    assert isinstance(score.assertion_density, Fraction)
    assert isinstance(score.mock_ratio, Fraction)
    # 1 bare assert / 5 body statements
    assert score.assertion_density == Fraction(1, 5)
    assert score.heuristically_vacuous is True


# ── Integration cases over the real 1.4 AST substrate (tree-sitter) ──

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.index.ast_index import build_ast_index  # noqa: E402

_VACUOUS_FIXTURE = """\
from unittest.mock import Mock, MagicMock


def test_vacuous():
    m = Mock()
    dep = MagicMock()
    result = service_call(m, dep)
    assert result
"""

_GENUINE_FIXTURE = """\
def test_genuine():
    total = add(2, 3)
    assert total == 5
"""


def test_integration_vacuous_flagged_genuine_not(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-94 — over real 1.4 index: vacuous flagged, genuine not (moat)."""
    (tmp_path / "test_vacuous.py").write_text(_VACUOUS_FIXTURE, encoding="utf-8")
    (tmp_path / "test_genuine.py").write_text(_GENUINE_FIXTURE, encoding="utf-8")
    index = build_ast_index(tmp_path, ("test_vacuous.py", "test_genuine.py"))
    by_path = {e.file_path: e for e in index.entries}

    detector = VacuousTestDetector()

    vac = detector.run(
        file_path="test_vacuous.py",
        source=_VACUOUS_FIXTURE,
        ast_entry=by_path["test_vacuous.py"],
    )
    assert len(vac.findings) == 1
    assert vac.findings[0].rule_id == RULE_AST  # corroborated over the real edge set

    gen = detector.run(
        file_path="test_genuine.py",
        source=_GENUINE_FIXTURE,
        ast_entry=by_path["test_genuine.py"],
    )
    assert gen.findings == ()  # genuine test NOT flagged
