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

import ast
from fractions import Fraction
from pathlib import Path

import pytest

from argus.ledger.coverage_ledger import CoverageDepth
from argus.reports.plain_english import (
    INTERNAL_DEFECT_MARKER,
    TERMINAL_OUTCOMES,
    TYPED_FAILURE_CLASSES,
    _INTERNAL_DEFECT_NEXT_ACTION,
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


# ─────────────────────────────────────────────────────────────────────────────────────
# Story 12.8 / AC4 — FR37's next action reaches the CLI, per CAUSE, by TYPED CLASS
#
# 12.4 shipped `render_audit_failed_next_action` and this file was its ONLY caller: measured
# on `2f84a0b`, a grep over `argus/**` returned its own `__all__` and nothing else, while both
# CLI failure arms printed `f"{PROG}: audit failed: {exc}"` and stopped. FR37 says *"the next
# action is present in the tool's own output"*; it was present in a test.
#
# These guards EXTEND 12.4's `TERMINAL_OUTCOMES` device to the failure seam rather than fork
# it: a closed vocabulary, enumerated in the pure module, closed over the REAL classes by
# `ast`, and failing on an unenumerated member instead of rendering a neighbour's remedy
# (`DF-10-4-E`'s lesson, the shape `_downgrade_sentence` already uses).
# ─────────────────────────────────────────────────────────────────────────────────────

_ARGUS_ROOT = Path(__file__).resolve().parents[1] / "argus"

#: Floor for the measured population (E.3). 36 typed `ValueError` subclasses were measured in
#: `argus/**` on 2026-08-15; a walk that collapses to nothing must be RED, not green.
_MIN_TYPED_CLASSES = 25


def _typed_value_error_classes() -> dict[str, str]:
    """Every `ValueError` subclass declared in `argus/**`, by `ast` — `{name: module path}`.

    STATIC on purpose. The obvious alternative — importing every module and walking
    `ValueError.__subclasses__()` — would pull `argus.audit.deep_audit` into `sys.modules`,
    and `TC-ArgusAgent-PIPELINE-001-10`'s NFR-S6 zero-token quarantine asserts precisely that
    it is absent. A guard that breaks a security invariant to measure a diagnosis vocabulary
    is not a guard worth having.

    The base chain is resolved WITHIN the tree, so `SourceStateError -> RepoIntakeError ->
    ValueError` and `UnexpectedStageError -> PipelineError -> ValueError` are both included.
    """
    declared: dict[str, tuple[list[str], str]] = {}
    for path in sorted(_ARGUS_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = [
                    base.id if isinstance(base, ast.Name)
                    else base.attr if isinstance(base, ast.Attribute)
                    else ""
                    for base in node.bases
                ]
                declared[node.name] = (bases, str(path))

    def roots_at_value_error(name: str, seen: tuple[str, ...] = ()) -> bool:
        if name in seen:
            return False  # a cycle cannot exist in Python, but never loop on malformed input
        bases, _module = declared.get(name, ([], ""))
        return any(
            base == "ValueError" or roots_at_value_error(base, seen + (name,))
            for base in bases
        )

    return {
        name: module
        for name, (_bases, module) in declared.items()
        if roots_at_value_error(name)
    }


def test_TC_ArgusAgent_REPORT_003_08_the_typed_failure_vocabulary_is_enumerated() -> None:
    """TC-ArgusAgent-REPORT-003-08 — FR37 / AC4: every enumerated failure class is REAL.

    `TERMINAL_OUTCOMES` is a closed vocabulary held against the `Verdict` enum. This is the
    same device at the FAILURE seam: `TYPED_FAILURE_CLASSES` is held against the classes that
    actually exist in `argus/**`, so an entry cannot be a phantom (a renamed or deleted class
    would leave a remedy nothing can ever select) and every entry must drive a real message.

    Dispatch is by class NAME rather than by class object, because `plain_english` is PURE and
    is imported BY `pipeline.py` — importing the pipeline's exception classes into it would
    invert that arrow (AR8). This guard is what makes the name-keyed registry honest.
    """
    population = _typed_value_error_classes()
    assert len(population) >= _MIN_TYPED_CLASSES, (
        f"the `ast` walk found only {len(population)} typed ValueError subclasses in argus/** "
        f"— below the measured floor of {_MIN_TYPED_CLASSES}. Either the walk broke or the "
        "tree moved; every assertion below is vacuous until it is repaired."
    )

    # `ValueError` itself is the deliberate TOTALITY arm — it is Python's, not ours, so it is
    # the one member with no declaration in `argus/**`.
    phantom = sorted(
        name for name in TYPED_FAILURE_CLASSES
        if name != "ValueError" and name not in population
    )
    assert not phantom, (
        f"TYPED_FAILURE_CLASSES names class(es) that do not exist in argus/**: {phantom}. A "
        "remedy keyed to a class nobody can raise is a remedy that never renders, and the "
        "real class it was renamed from now falls to the base arm silently."
    )
    assert "ValueError" in TYPED_FAILURE_CLASSES, (
        "the base `ValueError` arm was removed, so the dispatch is no longer TOTAL over what "
        "cli.py's `except ValueError` can catch — an unregistered subclass would RAISE inside "
        "an exception handler and put a traceback in front of the user (NFR-R1)"
    )
    assert len(TYPED_FAILURE_CLASSES) == len(set(TYPED_FAILURE_CLASSES)) > 1


def test_TC_ArgusAgent_REPORT_003_09_every_typed_failure_drives_a_real_next_action() -> None:
    """TC-ArgusAgent-REPORT-003-09 — FR37 / AC4: no cause is answered with the generic string.

    Today's single string — *"inspect logs/stderr, verify environment setup, or report
    unhandled exception if persistent"* — is the AUDIT_FAILED FALLBACK for an outcome token
    with no exception behind it. It must NOT be the answer to a `RepoIntakeError` for a missing
    path: telling someone to report an unhandled exception because they mistyped a directory is
    a remedy that cannot work.

    Asserted over the WHOLE measured population, not only the enumerated members: any class the
    CLI can catch must produce a non-empty, actionable sentence, because a dispatch that raises
    inside an `except` block would hand the user the traceback NFR-R1 forbids.
    """
    fallback = render_audit_failed_next_action()
    population = _typed_value_error_classes()

    for name in sorted(population):
        synthetic = type(name, (ValueError,), {})
        # An UNENUMERATED class is deliberately answered by the base `ValueError` arm — the
        # INTERNAL DEFECT remedy — because a typed failure nobody registered is, by
        # construction, one nobody has decided how a user could act on.
        action = render_audit_failed_next_action(cause=synthetic("synthetic"))
        assert action.strip(), f"{name} produced an empty next action"
        assert action != fallback, (
            f"{name} was answered with the generic AUDIT_FAILED fallback rather than a "
            "cause-specific remedy"
        )
        if name not in TYPED_FAILURE_CLASSES:
            assert INTERNAL_DEFECT_MARKER in action, (
                f"{name} is not enumerated and did not fall to the INTERNAL DEFECT arm — it "
                "has silently inherited some other cause's remedy"
            )

    # The expected-vs-defect SPLIT, asserted in both directions so the two cannot re-merge.
    for expected_name in ("RepoIntakeError", "SourceStateError", "UnknownHostError"):
        action = render_audit_failed_next_action(
            cause=type(expected_name, (ValueError,), {})("x")
        )
        assert INTERNAL_DEFECT_MARKER not in action, (
            f"{expected_name} is an OPERATOR error and was reported as a bug in Argus"
        )
    for defect_name in ("UnexpectedStageError", "ShipReadinessError"):
        action = render_audit_failed_next_action(
            cause=type(defect_name, (ValueError,), {})("x")
        )
        assert INTERNAL_DEFECT_MARKER in action, (
            f"{defect_name} is an INTERNAL defect and was reported as a normal degradation"
        )


def test_TC_ArgusAgent_REPORT_003_10_the_dispatch_raises_on_an_unregistered_type() -> None:
    """TC-ArgusAgent-REPORT-003-10 — FR37 / AC4: exhaustive means it RAISES, not falls through.

    `DF-10-4-E`'s lesson, which 12.5 applied to `_downgrade_sentence` the day it was written: a
    fallthrough hands the operator a remedy that cannot work, and it does so silently. So the
    dispatch has no default arm — a cause outside the registered hierarchy is LOUD.

    That is reachable only from a caller handing over something that is not a `ValueError` at
    all, because the base `ValueError` arm makes the dispatch total over everything the CLI's
    own `except` clauses can catch. Both facts are asserted here: the raise exists, and it
    cannot fire on the CLI's real path.
    """
    with pytest.raises(ValueError, match="no operator next action is registered"):
        render_audit_failed_next_action(cause=KeyError("not a ValueError"))

    # …and the CLI's real path cannot reach it: every ValueError, however exotic, resolves.
    for exotic in (
        UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte"),
        ValueError("bare"),
        type("NeverSeenBefore", (ValueError,), {})("x"),
    ):
        assert render_audit_failed_next_action(cause=exotic).strip()

    # The MODE split survives: with no cause, 12.4's fallback string is byte-identical.
    assert render_audit_failed_next_action("SyntaxError in config") == (
        "audit process encountered execution failure: SyntaxError in config — inspect "
        "logs/stderr, verify environment setup, or report unhandled exception if persistent"
    )


def test_TC_ArgusAgent_REPORT_003_11_one_vocabulary_reaches_all_three_surfaces() -> None:
    """TC-ArgusAgent-REPORT-003-11 — Story 12.8 / DN-7: three surfaces, one set of words.

    12.6 made it the contract that the CLI and the second invocation surface describe one
    failure identically — *"the wording is the CLI's, character for character"* — and this
    story does not weaken it. Three arms print an audit failure: `cli.py`'s audit arm,
    `cli.py`'s ship-readiness arm, and the second surface's failure arm. A next-action sentence
    added on one and not the others is a fork.

    Asserted STATICALLY over the committed sources, because the observable is *"do all three
    call the one renderer?"* — driving the stdio surface here would prove one instance and say
    nothing about the class.
    """
    cli_source = (_ARGUS_ROOT / "cli.py").read_text(encoding="utf-8")
    second_surface = (_ARGUS_ROOT / "mcp" / "server.py").read_text(encoding="utf-8")

    assert cli_source.count("render_audit_failed_next_action(cause=") >= 2, (
        "the CLI has fewer than two call sites for the shared next-action renderer, so one of "
        "its failure arms prints a cause and stops — which is the state FR37 was violated in"
    )
    assert "render_audit_failed_next_action(cause=" in second_surface, (
        "the second invocation surface no longer renders FR37's next action, so an agent is "
        "handed a cause it cannot act on while a human is handed a remedy (DN-7: a message on "
        "one surface and not the other is a fork)"
    )
    # And neither surface carries a TRANSCRIBED copy of the remedy PROSE (AI-E9-7). Naming
    # the token in a docstring is documentation; re-typing the sentence is a second source of
    # truth, and the sentence is the thing that drifts.
    signature = "this is a bug in Argus, not a problem with your repository"
    assert signature in _INTERNAL_DEFECT_NEXT_ACTION, (
        "the probe phrase no longer appears in the constant, so the transcription check below "
        "is testing nothing"
    )
    for name, source in (("cli.py", cli_source), ("the second surface", second_surface)):
        assert signature not in source, (
            f"{name} contains a transcribed copy of the internal-defect sentence instead of "
            "rendering it from the single constant in plain_english.py"
        )
