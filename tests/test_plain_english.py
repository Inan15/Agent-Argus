"""Verification for the PURE human-register verdict rendering (argus.reports.plain_english).

Verification area ArgusAgent-REPORT (TC-ArgusAgent-REPORT-002-NN).

What these tests actually pin
-----------------------------
The module exists to stop ONE failure mode: an operator reading a headline that
describes a state the gate did not produce. Since the FR16 amendment (Story 8.1) that
splits three ways:

1. ``NOT_READY_FOR_RELEASE`` means "I found something" — ALWAYS, with ``N >= 1``,
   proven by the exhaustive fold sweep (``-002-10``) rather than asserted.
2. ``INSUFFICIENT_COVERAGE`` covers TWO genuinely different situations — row 1 ("too
   little was assessed to say anything") and row 4 ("plenty was assessed, nothing was
   found, a gate was not met") — which must not read the same (``-002-12``…``-002-15``).
3. A state the gate cannot produce is a TYPED failure, never a rendered falsehood
   (``-002-16``).

Every case that claims to describe what the tool can produce folds a REAL
``evaluate_verdict``; a hand-constructed :class:`AuditVerdict` is used ONLY where the
subject IS the contract-violating input.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction

import pytest

from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
)
from argus.reports.plain_english import (
    ShipReadinessError,
    render_depth_meaning,
    render_ship_readiness,
)
from argus.verdict.verdict_gate import (
    AuditVerdict,
    CoverageScope,
    DecisionRow,
    DeepPassOutcome,
    Verdict,
    evaluate_verdict,
)


def _delivered_outcome(*, delivered: int) -> DeepPassOutcome:
    """A deep-pass outcome that DELIVERED — the only input the strong claim may rest on.

    Story 12.2 / §A.4. Built through the real frozen model so a field rename cannot
    leave these disclosure tests asserting over a shape that no longer exists.
    """
    return DeepPassOutcome(
        requested_count=delivered,
        delivered_count=delivered,
        degraded_count=0,
        credits_used="0",
    )


# The row-1 headline is BYTE-IDENTICAL to its pre-Story-8.3 text (AC4): only row 4
# moved. Pinned as a literal so a reword of row 4 cannot silently drag row 1 with it.
_ROW_1_HEADLINE = (
    "NOT ASSESSED — too little of the code was examined deeply to make any call. "
    "This is a statement about the audit, not about the code."
)


def _ledger(total: int, deep: int) -> CoverageLedger:
    """A ledger of *total* application files of which *deep* are ``audited_deep``."""
    return CoverageLedger.build(
        tuple(
            CoverageLedgerEntry(
                file_path=f"src/m{i}.py",
                depth=(
                    CoverageDepth.AUDITED_DEEP if i < deep else CoverageDepth.AUDITED_SHALLOW
                ),
                claim_present=i < deep,
            )
            for i in range(total)
        )
    )


def _fold(
    total: int,
    deep: int,
    n_findings: int = 0,
    criticals_all_deep: bool = True,
) -> AuditVerdict:
    """A REAL ``evaluate_verdict`` fold — the only producer of any renderable verdict.

    Reuses ``tests.test_verdict_gate._ast_finding`` rather than growing a third
    finding builder (§3.3 / AR7 no-fork).
    """
    from tests.test_verdict_gate import _ast_finding

    return evaluate_verdict(
        _ledger(total, deep),
        tuple(_ast_finding(file_path=f"t{i}.py", start=i + 1) for i in range(n_findings)),
        critical_subsystems_all_deep=criticals_all_deep,
        critical_subsystems_not_deep=() if criticals_all_deep else ("src/m0.py",),
    )


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


def test_TC_ArgusAgent_REPORT_002_10_no_fold_ever_blocks_with_zero_findings() -> None:
    """TC-ArgusAgent-REPORT-002-10 — AC1/AC2: the ``N >= 1`` invariant is PROVEN.

    Sweeps every ``(total 0..8) x (deep 0..total) x (findings 0,1,2) x (criticals
    True/False)`` combination — 270 REAL ``evaluate_verdict`` folds — and pins the
    exact ``(verdict, row, has-blocking)`` population it produces. ``NOT_READY_FOR_
    RELEASE`` with ``blocking_finding_count == 0`` occurs ZERO times, which is what
    makes ``_headline``'s former trailing else-branch unreachable (DR-11) and what
    guarantees every rendered ``BLOCKED`` headline names a count of at least one.
    """
    seen: Counter[tuple[str, str, bool]] = Counter()
    for total in range(0, 9):
        for deep in range(0, total + 1):
            for n_findings in (0, 1, 2):
                for criticals_all_deep in (True, False):
                    verdict = _fold(total, deep, n_findings, criticals_all_deep)
                    assert verdict.decision_row is not None
                    seen[
                        (
                            verdict.verdict.value,
                            verdict.decision_row.value,
                            verdict.blocking_finding_count > 0,
                        )
                    ] += 1
                    if verdict.verdict is Verdict.NOT_READY_FOR_RELEASE:
                        assert verdict.blocking_finding_count >= 1
                        assert render_ship_readiness(verdict)[0] == (
                            f"Ship-readiness: BLOCKED — "
                            f"{verdict.blocking_finding_count} verdict-blocking "
                            f"finding(s) must be resolved."
                        )

    assert sum(seen.values()) == 270
    assert seen == Counter(
        {
            ("INSUFFICIENT_COVERAGE", "row_1_below_floor", False): 24,
            ("INSUFFICIENT_COVERAGE", "row_1_below_floor", True): 48,
            ("INSUFFICIENT_COVERAGE", "row_4_gate_unmet_no_findings", False): 47,
            ("NOT_READY_FOR_RELEASE", "row_2_blocking_findings", True): 132,
            ("RELEASE_READY", "row_3_gates_met", False): 19,
        }
    )
    assert not [
        key for key in seen if key[0] == "NOT_READY_FOR_RELEASE" and key[2] is False
    ], "NOT_READY_FOR_RELEASE with zero blocking findings is unreachable"


def test_TC_ArgusAgent_REPORT_002_11_every_headline_branch_is_reachable_and_distinct() -> None:
    """TC-ArgusAgent-REPORT-002-11 — AC2: ``_headline`` is TOTAL, with no dead branch.

    One REAL fold per FR16 row. Each row must reach the renderer and produce its own
    wording; four rows collapsing into three headlines would mean a branch nobody can
    observe — the defect DR-11 exists to remove.
    """
    headlines = {
        DecisionRow.BELOW_FLOOR: render_ship_readiness(_fold(10, 1))[0],
        DecisionRow.BLOCKING_FINDINGS: render_ship_readiness(_fold(5, 3, 1))[0],
        DecisionRow.GATES_MET: render_ship_readiness(_fold(5, 3))[0],
        DecisionRow.GATE_UNMET_NO_FINDINGS: render_ship_readiness(_fold(5, 2))[0],
    }
    # Each fold really did fire the row it is filed under.
    assert _fold(10, 1).decision_row is DecisionRow.BELOW_FLOOR
    assert _fold(5, 3, 1).decision_row is DecisionRow.BLOCKING_FINDINGS
    assert _fold(5, 3).decision_row is DecisionRow.GATES_MET
    assert _fold(5, 2).decision_row is DecisionRow.GATE_UNMET_NO_FINDINGS

    assert len(set(headlines.values())) == 4, "each FR16 row needs its own words"
    assert headlines[DecisionRow.BELOW_FLOOR].endswith(_ROW_1_HEADLINE)
    assert "BLOCKED" in headlines[DecisionRow.BLOCKING_FINDINGS]
    assert "READY —" in headlines[DecisionRow.GATES_MET]
    assert "NOT VOUCHED" in headlines[DecisionRow.GATE_UNMET_NO_FINDINGS]


def test_zero_finding_block_does_not_read_as_a_defect_claim() -> None:
    """TC-ArgusAgent-REPORT-002-12 — a zero-finding outcome must not read as a defect.

    RE-POINTED (Story 8.3 / AC3). The subject is unchanged and it is still the
    keystone; only the verdict it is asserted against moved. It used to hand-build
    ``NOT_READY_FOR_RELEASE`` + ``blocking=0`` — a state the amended gate cannot
    produce (``-002-10``) — so it pinned the wording of an impossible input. It now
    folds the REAL zero-finding outcome an operator actually meets: FR16 row 4,
    ``INSUFFICIENT_COVERAGE``, 2/5 deep, nothing found, the coverage gate unmet.
    """
    verdict = _fold(5, 2)
    assert verdict.decision_row is DecisionRow.GATE_UNMET_NO_FINDINGS
    assert verdict.blocking_finding_count == 0

    headline = render_ship_readiness(verdict)[0]

    assert "NOT VOUCHED" in headline
    assert "BLOCKED" not in headline
    assert "nothing broken was found" in headline
    # It must say WHY, and say it is a statement about the audit, not the code.
    assert "coverage or critical-subsystem gate was not met" in headline
    assert "not about the code" in headline
    # …and it must NOT claim the floor stopped the audit — that is row 1's message.
    assert "too little of the code was examined" not in headline


def test_real_blocking_findings_do_read_as_a_defect_claim() -> None:
    """The other side of the split: with findings present, "blocked" is the truth."""
    headline = render_ship_readiness(_verdict(blocking=3))[0]

    assert "BLOCKED" in headline
    assert "3 verdict-blocking finding(s)" in headline
    assert "NOT VOUCHED" not in headline
    # The row-2 string is UNCHANGED by Story 8.3 (AC1) — pinned byte-for-byte.
    assert headline == (
        "Ship-readiness: BLOCKED — 3 verdict-blocking finding(s) must be resolved."
    )


def test_TC_ArgusAgent_REPORT_002_13_full_deep_coverage_row_4_never_claims_too_little() -> None:
    """TC-ArgusAgent-REPORT-002-13 — AC4: the absurd case, measured at 100 % deep.

    Row 4 also fires on the CRITICAL-SUBSYSTEM clause alone, with every single file
    at ``audited_deep``. Telling that operator "too little of the code was examined
    deeply" is not merely imprecise, it is contradicted by the very next line of the
    same block ("Deeply examined: 5 of 5"). This is why the row-4 wording may not
    mention coverage alone.
    """
    verdict = _fold(5, 5, 0, criticals_all_deep=False)
    assert verdict.decision_row is DecisionRow.GATE_UNMET_NO_FINDINGS
    assert verdict.deep_ratio == Fraction(1, 1)  # 100 % of files reached audited_deep

    lines = render_ship_readiness(verdict)
    headline = lines[0]

    assert "too little of the code was examined" not in headline
    assert "NOT VOUCHED" in headline
    assert "critical-subsystem gate" in headline
    assert "Deeply examined: 5 of 5 files" in "\n".join(lines)


def test_TC_ArgusAgent_REPORT_002_14_below_floor_and_gate_unmet_read_differently() -> None:
    """TC-ArgusAgent-REPORT-002-14 — AC4/boundary B4: one enum, two actions.

    Rows 1 and 4 carry the SAME verdict token and the SAME exit code, so the human
    register is the only surface on which an operator can tell "give me more to look
    at" from "I looked, found nothing, and a gate is unmet". The split is driven by
    ``AuditVerdict.is_below_floor`` — never by ``decision_row`` directly and never by
    a re-derived ratio comparison (§3.3 no-fork).
    """
    row_1 = _fold(10, 1)
    row_4 = _fold(5, 2)

    assert row_1.verdict is row_4.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert row_1.exit_code == row_4.exit_code == 3
    assert row_1.is_below_floor is True
    assert row_4.is_below_floor is False

    row_1_headline = render_ship_readiness(row_1)[0]
    row_4_headline = render_ship_readiness(row_4)[0]

    assert row_1_headline != row_4_headline
    # Row 1 is BYTE-IDENTICAL to its pre-Story-8.3 text.
    assert row_1_headline == f"Ship-readiness: {_ROW_1_HEADLINE}"
    assert "nothing broken was found" in row_4_headline
    assert "NOT VOUCHED" not in row_1_headline


def test_TC_ArgusAgent_REPORT_002_15_pre_amendment_payload_still_reads_as_row_1() -> None:
    """TC-ArgusAgent-REPORT-002-15 — AC4/D1: the ``decision_row is None`` fallback.

    A pre-amendment (``schema_version "1"``) payload carries no row. Branching on
    ``decision_row`` directly would send it down the row-4 arm and describe it in
    words that were never true of it; ``is_below_floor`` carries the enum fallback
    that keeps it on the row-1 text it was written under.
    """
    legacy = _verdict(Verdict.INSUFFICIENT_COVERAGE)

    assert legacy.decision_row is None
    assert legacy.is_below_floor is True
    assert render_ship_readiness(legacy)[0] == f"Ship-readiness: {_ROW_1_HEADLINE}"


def test_TC_ArgusAgent_REPORT_002_16_impossible_verdict_is_a_typed_failure() -> None:
    """TC-ArgusAgent-REPORT-002-16 — AC2: never a silent default, never the bug string.

    The one input ``_headline`` must refuse is the state ``-002-10`` proves the gate
    cannot produce. Letting it fall into the row-2 arm would print
    ``BLOCKED — 0 verdict-blocking finding(s)`` — the exact false accusation this epic
    exists to delete — so it is a TYPED ``ValueError`` subclass (the
    ``exit_code_for_verdict`` / ``NegativeAssuranceError`` house pattern), which the
    CLI already degrades to a secret-safe exit 1 (AR10).
    """
    impossible = _verdict(Verdict.NOT_READY_FOR_RELEASE, blocking=0)

    assert issubclass(ShipReadinessError, ValueError)
    with pytest.raises(ShipReadinessError) as excinfo:
        render_ship_readiness(impossible)

    message = str(excinfo.value)
    assert "NOT_READY_FOR_RELEASE" in message
    assert "blocking_finding_count=0" in message
    # NFR-S1: the message names the typed reason only — no source, no host path.
    assert ":\\" not in message
    assert not message.startswith("/")


def test_TC_ArgusAgent_REPORT_002_17_row_1_and_row_4_both_read_as_not_a_defect() -> None:
    """TC-ArgusAgent-REPORT-002-17 — AC4: SPLIT of the old single-case pin.

    The original ``…insufficient_coverage_reads_as_not_assessed_never_as_a_defect``
    asserted one property over one hand-built verdict. Both real rows must hold it:
    neither may read as a defect claim, and both must say they describe the AUDIT.
    """
    for verdict in (_fold(10, 1), _fold(5, 2), _fold(5, 5, 0, criticals_all_deep=False)):
        headline = render_ship_readiness(verdict)[0]
        assert verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
        assert "not about the code" in headline
        assert "BLOCKED" not in headline
        assert "verdict-blocking finding(s) must be resolved" not in headline


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
    """A narrowed assessment must never be presented as a whole-repository claim.

    ``blocking=1`` is now passed EXPLICITLY (Story 8.3): the helper's zero-finding
    ``NOT_READY_FOR_RELEASE`` default is a state the amended gate cannot produce
    (``-002-10``) and the renderer now refuses it. The subject — the scope disclosure
    body lines, which are identical on every row — and every assertion are unchanged;
    only the fixture moved to a verdict the tool can actually emit.
    """
    scope = CoverageScope(
        scope_id="application",
        excluded_reason="test_files",
        assessed_deep_count=55,
        assessed_total_count=71,
        assessed_deep_ratio=Fraction(55, 71),
        excluded_count=69,
    )
    body = "\n".join(render_ship_readiness(_verdict(blocking=1, scope=scope)))

    assert "55 of 71 assessed files (55/71)" in body
    assert "application" in body
    assert "69 held out" in body
    assert "test_files" in body


def test_scope_suggestion_appears_only_when_the_run_was_not_already_narrowed() -> None:
    """Suggesting a flag the operator already passed is noise, not help.

    ``blocking=1`` is passed EXPLICITLY for the reason given in
    ``test_scoped_verdict_reports_the_assessed_population_and_the_holdout``; the
    ``Next:`` advice under test is unaffected by the finding count.
    """
    unscoped = "\n".join(render_ship_readiness(_verdict(blocking=1, deep=11, total=28)))
    assert "--coverage-scope application" in unscoped

    scope = CoverageScope(
        scope_id="application",
        excluded_reason="test_files",
        assessed_deep_count=1,
        assessed_total_count=10,
        assessed_deep_ratio=Fraction(1, 10),
        excluded_count=5,
    )
    scoped = "\n".join(render_ship_readiness(_verdict(blocking=1, scope=scope)))
    assert "--coverage-scope application" not in scoped


def test_next_step_appears_for_the_critical_clause_so_a_block_is_actionable() -> None:
    """``blocking=1`` is explicit for the same fixture reason; the advice is unchanged."""
    body = "\n".join(
        render_ship_readiness(
            _verdict(
                blocking=1, criticals_all_deep=False, criticals_not_deep=("argus/x.py",)
            )
        )
    )
    assert "--exclude-critical" in body


def test_depth_meaning_refuses_to_claim_comprehension_without_an_llm_pass() -> None:
    """The over-claim this closes: `audited_deep` must not imply a model read the code."""
    text = render_depth_meaning(("coverage", "security", "orphan", "vacuous", "prosecutor"))

    assert "No language model read any source" in text
    assert "not a comprehension grade" in text


def test_depth_meaning_strengthens_automatically_when_a_deep_pass_is_enabled() -> None:
    """The disclosure is DERIVED from the deep pass's OUTCOME, so it cannot drift out of date.

    Story 12.2 / AC6.3 STRENGTHENED this test rather than narrowing it. It previously
    passed ``("coverage", "deep")`` and asserted the strengthened sentence — which was
    true of the FUNCTION and false of the RUN: the token alone flipped the wording while
    nothing dispatched (Story 12.2 §0.5). The property the test was reaching for — *the
    disclosure tracks what actually ran* — is unchanged and is now asserted against a
    DELIVERED outcome, which is the only input that makes the sentence true.
    """
    text = render_depth_meaning(
        ("coverage", "deep"), deep_pass=_delivered_outcome(delivered=3)
    )

    assert "validated against the repository AST" in text
    assert "No language model read any source" not in text


def test_TC_ArgusAgent_REPORT_002_20_a_requested_deep_pass_that_delivered_nothing_never_claims_one() -> None:
    """TC-ArgusAgent-REPORT-002-20 — FR36: the tool NEVER produces a false deep claim.

    Story 12.2 / AC6.3, Task 1 — landed RED on ``2bea92f`` BEFORE any wiring existed.

    THE DEFECT THIS CLOSES, measured on the shipped tree: ``render_depth_meaning`` keyed
    the strengthened sentence on the mere PRESENCE of the token ``deep`` in
    ``enabled_passes``. ``--passes`` is not validated against ``_ALL_PASSES`` (that tuple
    is the DEFAULT, not a whitelist), so ``argus audit <repo> --passes coverage,deep``
    printed *"a deep read was dispatched for the file and its claim was validated against
    the repository AST"* on a tree where ``DeepAuditSeam`` had ZERO production callers.

    THE OBSERVABLE is the returned sentence. THE DEFECT MOVES IT: with the pre-story
    predicate (``any(name in LLM_DEEP_PASSES ...)``) this assertion fails, because that
    predicate cannot see the difference between *requested* and *delivered* — the
    distinction the sentence is a statement about.

    There are THREE honest states, not two, and the third is the one FR36 and NFR-R1
    care about most: requested-and-not-delivered must say so out loud rather than
    silently falling back to the no-deep-pass wording (which would be a DIFFERENT lie —
    it would claim no deep pass was enabled when one was).
    """
    text = render_depth_meaning(("coverage", "deep"))

    assert "a deep read was dispatched" not in text, (
        "the strengthened claim was produced by the presence of a CSV token, with "
        "nothing dispatched — FR36's 'never produces a false deep claim', violated"
    )
    assert "no deep read was completed" in text, (
        "a requested-but-undelivered deep pass must be NAMED, not silently downgraded "
        "to the wording of a run where no deep pass was requested at all"
    )


def test_TC_ArgusAgent_REPORT_002_21_the_three_disclosure_states_are_mutually_exclusive() -> None:
    """TC-ArgusAgent-REPORT-002-21 — the disclosure is TOTAL and its states are distinct.

    Story 12.2 / AC6.3. A three-state disclosure whose states are not distinguishable is
    a two-state disclosure with extra words. Each state is generated from the real
    predicate inputs and asserted to differ from BOTH others.
    """
    not_requested = render_depth_meaning(("coverage", "security"))
    requested_undelivered = render_depth_meaning(("coverage", "deep"))
    requested_delivered = render_depth_meaning(
        ("coverage", "deep"), deep_pass=_delivered_outcome(delivered=1)
    )

    states = (not_requested, requested_undelivered, requested_delivered)
    assert len(set(states)) == 3, f"the three states are not distinct: {states}"
    # A delivered outcome attached to a run that never REQUESTED the pass cannot
    # manufacture the claim either — the request is necessary, not merely sufficient.
    assert (
        render_depth_meaning(("coverage",), deep_pass=_delivered_outcome(delivered=1))
        == not_requested
    )


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
