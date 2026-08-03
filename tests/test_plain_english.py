"""Verification for the PURE human-register verdict rendering (argus.reports.plain_english).

Verification area ArgusAgent-REPORT (TC-ArgusAgent-REPORT-002-NN).

What these tests actually pin
-----------------------------
The module exists to stop ONE failure mode: an operator reading a blocking word
beside a zero blocking count and being unable to tell "I found a defect" from "I did
not look at enough". So the load-bearing test is the SPLIT inside
``NOT_READY_FOR_RELEASE`` (blocking>0 vs blocking==0 must not read the same), plus
the invariant that the wording layer never contradicts or replaces the machine
verdict it describes.
"""

from __future__ import annotations

from fractions import Fraction

from argus.ledger.coverage_ledger import CoverageDepth
from argus.reports.plain_english import (
    render_depth_meaning,
    render_ship_readiness,
)
from argus.verdict.verdict_gate import AuditVerdict, CoverageScope, Verdict


def _verdict(
    state: Verdict = Verdict.NOT_READY_FOR_RELEASE,
    *,
    blocking: int = 0,
    deep: int = 11,
    total: int = 28,
    criticals_all_deep: bool = True,
    criticals_not_deep: tuple[str, ...] = (),
    scope: CoverageScope | None = None,
) -> AuditVerdict:
    exit_code = {
        Verdict.RELEASE_READY: 0,
        Verdict.NOT_READY_FOR_RELEASE: 2,
        Verdict.INSUFFICIENT_COVERAGE: 3,
    }[state]
    return AuditVerdict(
        verdict=state,
        deep_ratio=Fraction(deep, total),
        deep_count=deep,
        total_count=total,
        counts_by_depth={
            CoverageDepth.AUDITED_DEEP: deep,
            CoverageDepth.AUDITED_SHALLOW: total - deep,
        },
        blocking_finding_count=blocking,
        ordered_findings=(),
        critical_subsystems_all_deep=criticals_all_deep,
        critical_subsystems_not_deep=criticals_not_deep,
        coverage_scope=scope,
        exit_code=exit_code,
    )


def test_zero_finding_block_does_not_read_as_a_defect_claim() -> None:
    """THE keystone: NOT_READY with zero blocking findings must not say "blocked".

    This is the exact line an operator saw beside ``blocking_findings=0``. Saying
    "blocked" there asserts a defect the audit did not find — a false accusation,
    which this codebase treats as the lethal failure.
    """
    lines = render_ship_readiness(_verdict(blocking=0))
    headline = lines[0]

    assert "NOT VOUCHED" in headline
    assert "BLOCKED" not in headline
    # It must say WHY, and say it is a statement about the audit, not the code.
    assert "coverage gate" in headline
    assert "not about the code" in headline


def test_real_blocking_findings_do_read_as_a_defect_claim() -> None:
    """The other side of the split: with findings present, "blocked" is the truth."""
    headline = render_ship_readiness(_verdict(blocking=3))[0]

    assert "BLOCKED" in headline
    assert "3 verdict-blocking finding(s)" in headline
    assert "NOT VOUCHED" not in headline


def test_insufficient_coverage_reads_as_not_assessed_never_as_a_defect() -> None:
    headline = render_ship_readiness(_verdict(Verdict.INSUFFICIENT_COVERAGE))[0]

    assert "NOT ASSESSED" in headline
    assert "not about the code" in headline


def test_release_ready_reads_as_ready() -> None:
    headline = render_ship_readiness(
        _verdict(Verdict.RELEASE_READY, deep=9, total=10)
    )[0]

    assert headline.startswith("Ship-readiness: READY")


def test_counts_restate_the_verdict_and_never_invent_a_number() -> None:
    """Every rendered number must be a counter already on the verdict (no new judgement)."""
    verdict = _verdict(blocking=2, deep=11, total=28, criticals_all_deep=False,
                       criticals_not_deep=("a.py", "b.py"))
    body = "\n".join(render_ship_readiness(verdict))

    assert "Verdict-blocking findings: 2" in body
    assert "11 of 28 files (11/28)" in body
    assert "Critical files not examined deeply: 2" in body


def test_scoped_verdict_reports_the_assessed_population_and_the_holdout() -> None:
    """A narrowed assessment must never be presented as a whole-repository claim."""
    scope = CoverageScope(
        scope_id="application",
        excluded_reason="test_files",
        assessed_deep_count=55,
        assessed_total_count=71,
        assessed_deep_ratio=Fraction(55, 71),
        excluded_count=69,
    )
    body = "\n".join(render_ship_readiness(_verdict(scope=scope)))

    assert "55 of 71 assessed files (55/71)" in body
    assert "application" in body
    assert "69 held out" in body
    assert "test_files" in body


def test_scope_suggestion_appears_only_when_the_run_was_not_already_narrowed() -> None:
    """Suggesting a flag the operator already passed is noise, not help."""
    unscoped = "\n".join(render_ship_readiness(_verdict(deep=11, total=28)))
    assert "--coverage-scope application" in unscoped

    scope = CoverageScope(
        scope_id="application",
        excluded_reason="test_files",
        assessed_deep_count=1,
        assessed_total_count=10,
        assessed_deep_ratio=Fraction(1, 10),
        excluded_count=5,
    )
    scoped = "\n".join(render_ship_readiness(_verdict(scope=scope)))
    assert "--coverage-scope application" not in scoped


def test_next_step_appears_for_the_critical_clause_so_a_block_is_actionable() -> None:
    body = "\n".join(
        render_ship_readiness(
            _verdict(criticals_all_deep=False, criticals_not_deep=("argus/x.py",))
        )
    )
    assert "--exclude-critical" in body


def test_depth_meaning_refuses_to_claim_comprehension_without_an_llm_pass() -> None:
    """The over-claim this closes: `audited_deep` must not imply a model read the code."""
    text = render_depth_meaning(("coverage", "security", "orphan", "vacuous", "prosecutor"))

    assert "No language model read any source" in text
    assert "not a comprehension grade" in text


def test_depth_meaning_strengthens_automatically_when_a_deep_pass_is_enabled() -> None:
    """The disclosure is DERIVED from enabled_passes, so it cannot drift out of date."""
    text = render_depth_meaning(("coverage", "deep"))

    assert "validated against the repository AST" in text
    assert "No language model read any source" not in text


def test_depth_meaning_is_markup_free_so_it_is_correct_on_a_terminal() -> None:
    """The same string is printed to a TTY and embedded in Markdown — no leaked asterisks."""
    for passes in (("coverage",), ("coverage", "deep")):
        text = render_depth_meaning(passes)
        assert "**" not in text
        assert not text.startswith("#")


def test_rendering_is_deterministic_and_leaks_no_host_path() -> None:
    """PURE + NFR-S1: same input → identical tuple; no absolute path can appear."""
    verdict = _verdict(blocking=1, criticals_all_deep=False, criticals_not_deep=("a.py",))
    first = render_ship_readiness(verdict, enabled_passes=("coverage",))
    second = render_ship_readiness(verdict, enabled_passes=("coverage",))

    assert first == second
    body = "\n".join(first)
    assert ":\\" not in body
    assert not any(line.strip().startswith("/") for line in first)
