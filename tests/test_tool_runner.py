"""Zero-token breadth tool-runner + tool-failure-AS-FINDING tests (Story 2.6).

Verification area ArgusAgent-TOOL (``TC-ArgusAgent-TOOL-001-NN``). Covers the AC1–AC8 surface
of ``argus.detectors.tool_runner``:

- AC1 — zero-token breadth + the ``tool_scanned_only`` PRODUCER (denominator-only
  proven via the REAL 1.6 ``evaluate_verdict`` over a synthetic ledger, NOT a fork).
- AC2 — tool-failure-AS-FINDING: each injected failure mode (crash / timeout /
  unavailable / unparseable) → a ``tool_failure`` finding + a coverage downgrade,
  NEVER a crash / fabricated pass / silent skip / leaked output (sanitized token).
- AC3 — unestablishable-traceability-AS-FINDING (clean-but-signal-less file).
- AC4 — the frozen redaction-safe ``ToolRunOutcome`` (no raw-output field; no
  ``float``; metrics ``int``; round-trips through the single 1.1 serializer).
- AC5 — the grade + the fold + the no-double-count rule + the regression-safe
  clean-run path (no NEW ``tool_scanned_only`` → ledger+verdict byte-identical).
- AC6 — the MANDATORY adversarial non-ASCII + locale + FAILURE-INJECTION suite
  (AI-E1-1 — 2.6 is the named first application).
- AC7 — purity-of-classification / typed error (no leak) / single serializer.

The CLASSIFIER tests are pure-function over a captured-outcome fixture (zero LLM
tokens, NFR-D2). The FAILURE-INJECTION tests inject a fake ``tool_invoker`` (the
AR8 seam) so crash/timeout/unavailable/unparseable are forced WITHOUT spawning a
real subprocess — fast + deterministic.
"""

from __future__ import annotations

from fractions import Fraction

import pytest
from pydantic import ValidationError

from argus.detectors.base import DetectorResult
from argus.detectors.tool_runner import (
    RULE_TOOL_FAILURE,
    RULE_TRACEABILITY_NOT_ESTABLISHABLE,
    TOOL_RUN_SCHEMA_VERSION,
    V1_BREADTH_TOOL_ID,
    ToolInvocation,
    ToolOutcome,
    ToolRunnerDetector,
    ToolRunnerError,
    ToolRunOutcome,
    radon_invoker,
)
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
)
from argus.ledger.recording import Recording
from argus.store import canonical
from argus.verdict.verdict_gate import Verdict, evaluate_verdict

# A planted source/secret-shaped sentinel for the leak search. A hostile tool can
# echo bytes like this in its stderr/stdout; none of them may reach an emitted or
# persisted field (NFR-S1).
_SENTINEL_ASCII = "PLANTEDxLEAKSENTINEL_0123456789"
_SENTINEL_NON_ASCII = "пароль_секрет_PLANTED_значение_42"


def _ok(file_path: str, *, loc: int = 4, cx: int = 2) -> ToolInvocation:
    return ToolInvocation(
        file_path=file_path, outcome=ToolOutcome.OK, total_loc=loc, total_complexity=cx
    )


def _failing_invoker(outcome: ToolOutcome):
    """A fake invoker that always returns *outcome* (the AR8 failure-injection seam)."""

    def _invoke(file_path: str, source: str) -> ToolInvocation:
        return ToolInvocation(file_path=file_path, outcome=outcome)

    return _invoke


def _leaky_raising_invoker(file_path: str, source: str) -> ToolInvocation:
    """A fake invoker that RAISES with a sentinel-bearing message (a hostile tool)."""
    raise RuntimeError(f"radon blew up on {_SENTINEL_ASCII} / {_SENTINEL_NON_ASCII}")


# ── AC1 — zero-token breadth + the tool_scanned_only producer ──────────────────


def test_clean_run_grades_tool_scanned_only() -> None:
    """TC-ArgusAgent-TOOL-001-01 — an OK file not otherwise graded → tool_scanned_only."""
    detector = ToolRunnerDetector(tool_invoker=lambda fp, src: _ok(fp))
    result = detector.run(targets=[("pkg/mod.py", "x = 1\n")], already_graded_paths=())
    assert isinstance(result, DetectorResult)
    assert len(result.entries) == 1
    assert result.entries[0].depth is CoverageDepth.TOOL_SCANNED_ONLY
    assert result.entries[0].file_path == "pkg/mod.py"
    assert result.entries[0].claim_present is False
    assert result.findings == ()
    assert result.degraded == ()


def test_tool_scanned_only_is_denominator_only_via_real_verdict_gate() -> None:
    """TC-ArgusAgent-TOOL-001-02 — FR8: a tool_scanned_only-only ledger never RELEASE_READY.

    Proven through the REAL 1.6 ``evaluate_verdict`` (import-verified, NOT a fork):
    the deep-% numerator counts ONLY ``audited_deep``, so breadth grades land in the
    denominator and can never satisfy a deep gate (the NFR-C3 cost split).
    """
    detector = ToolRunnerDetector(tool_invoker=lambda fp, src: _ok(fp))
    result = detector.run(
        targets=[("a.py", "x=1\n"), ("b.py", "y=2\n"), ("c.py", "z=3\n")]
    )
    ledger = CoverageLedger.build(result.entries)
    assert all(e.depth is CoverageDepth.TOOL_SCANNED_ONLY for e in ledger.entries)

    verdict = evaluate_verdict(ledger, ())
    # 0 deep / 3 total → below the 20% floor → INSUFFICIENT_COVERAGE, never READY.
    assert verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert verdict.verdict is not Verdict.RELEASE_READY
    assert verdict.deep_ratio == Fraction(0, 3)


def test_radon_invoker_is_the_locked_v1_tool() -> None:
    """TC-ArgusAgent-TOOL-001-03 — V1 tool id is radon; the default invoker is radon."""
    assert V1_BREADTH_TOOL_ID == "radon"
    inv = radon_invoker("m.py", "def f(x):\n    if x:\n        return 1\n    return 2\n")
    assert inv.outcome is ToolOutcome.OK
    assert inv.total_loc > 0
    assert inv.total_complexity > 0


# ── AC2 — tool-failure-AS-FINDING (each injected failure mode) ──────────────────


@pytest.mark.parametrize(
    "outcome,token",
    [
        (ToolOutcome.UNAVAILABLE, "radon_unavailable"),
        (ToolOutcome.CRASHED, "radon_crashed"),
        (ToolOutcome.TIMED_OUT, "radon_timed_out"),
        (ToolOutcome.UNPARSEABLE, "radon_unparseable"),
    ],
)
def test_each_failure_mode_becomes_a_finding_plus_downgrade(
    outcome: ToolOutcome, token: str
) -> None:
    """TC-ArgusAgent-TOOL-001-04 — crash/timeout/unavailable/unparseable → tool_failure + skipped."""
    detector = ToolRunnerDetector(tool_invoker=_failing_invoker(outcome))
    result = detector.run(targets=[("pkg/mod.py", "x = 1\n")])

    # A recorded tool_failure finding (advisory, depth_supported=None, ≥1 locator).
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.rule_id == RULE_TOOL_FAILURE
    assert finding.advisory is True
    assert finding.depth_supported is None
    assert len(finding.locators) == 1
    assert finding.locators[0].file_path == "pkg/mod.py"
    assert finding.locators[0].start_line == 1

    # A coverage DOWNGRADE: the file is recorded skipped, never fabricated as covered.
    assert len(result.entries) == 1
    assert result.entries[0].depth is CoverageDepth.SKIPPED

    # A degraded condition carrying ONLY the sanitized reason TOKEN (NFR-S1).
    assert len(result.degraded) == 1
    assert result.degraded[0].reason == token
    assert result.degraded[0].file_path == "pkg/mod.py"


def test_raising_invoker_is_caught_as_crash_never_propagates() -> None:
    """TC-ArgusAgent-TOOL-001-05 — a raising invoker is CAUGHT → CRASHED finding, no leak."""
    detector = ToolRunnerDetector(tool_invoker=_leaky_raising_invoker)
    result = detector.run(targets=[("pkg/mod.py", "x = 1\n")])  # must NOT raise

    assert len(result.findings) == 1
    assert result.findings[0].rule_id == RULE_TOOL_FAILURE
    assert result.degraded[0].reason == "radon_crashed"

    # The sentinel from the raised message leaks into NO emitted byte.
    blob = canonical.dumps_bytes(
        {
            "findings": [f.model_dump(mode="json") for f in result.findings],
            "degraded": [
                {"file_path": d.file_path, "reason": d.reason} for d in result.degraded
            ],
        }
    )
    assert _SENTINEL_ASCII.encode("utf-8") not in blob
    assert _SENTINEL_NON_ASCII.encode("utf-8") not in blob
    assert b"PLANTED" not in blob


def test_malformed_argument_raises_typed_error_with_no_leak() -> None:
    """TC-ArgusAgent-TOOL-001-06 — a malformed argument raises ToolRunnerError (no raw output)."""
    detector = ToolRunnerDetector()
    with pytest.raises(ToolRunnerError):
        detector.run(targets="not-a-sequence-of-pairs")  # type: ignore[arg-type]
    with pytest.raises(ToolRunnerError):
        detector.run(targets=[("only-one-element",)])  # type: ignore[list-item]
    with pytest.raises(ToolRunnerError):
        detector.run(targets=[("", "source")])  # empty file_path
    assert issubclass(ToolRunnerError, ValueError)


def test_misbehaving_invoker_returning_non_invocation_is_a_crash() -> None:
    """TC-ArgusAgent-TOOL-001-07 — an invoker returning a non-ToolInvocation degrades to CRASHED."""
    detector = ToolRunnerDetector(tool_invoker=lambda fp, src: "garbage")  # type: ignore[return-value]
    result = detector.run(targets=[("pkg/mod.py", "x = 1\n")])
    assert result.findings[0].rule_id == RULE_TOOL_FAILURE
    assert result.degraded[0].reason == "radon_crashed"


# ── AC3 — unestablishable-traceability-AS-FINDING ───────────────────────────────


def test_clean_but_signal_less_file_is_traceability_not_establishable() -> None:
    """TC-ArgusAgent-TOOL-001-08 — OK with zero LOC and zero complexity → traceability finding."""
    detector = ToolRunnerDetector(
        tool_invoker=lambda fp, src: _ok(fp, loc=0, cx=0)
    )
    result = detector.run(targets=[("pkg/empty.py", "\n")])

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.rule_id == RULE_TRACEABILITY_NOT_ESTABLISHABLE
    assert finding.advisory is True
    assert finding.depth_supported is None
    assert finding.locators[0].file_path == "pkg/empty.py"

    # Recorded skipped (examined-but-ungradable), never fabricated as covered.
    assert len(result.entries) == 1
    assert result.entries[0].depth is CoverageDepth.SKIPPED
    # No tool_failure / no degraded condition for a clean-but-signal-less file.
    assert result.degraded == ()


# ── AC4 — the frozen redaction-safe ToolRunOutcome ──────────────────────────────


def test_tool_run_outcome_is_frozen_extra_forbid() -> None:
    """TC-ArgusAgent-TOOL-001-09 — ToolRunOutcome is frozen + extra=forbid + localized version."""
    out = ToolRunOutcome(tool_id="radon", file_path="a.py", outcome=ToolOutcome.OK)
    assert out.schema_version == TOOL_RUN_SCHEMA_VERSION
    with pytest.raises(ValidationError):
        ToolRunOutcome(  # extra field rejected
            tool_id="radon", file_path="a.py", outcome=ToolOutcome.OK, raw_stdout="x"
        )
    with pytest.raises(ValidationError):
        out.tool_id = "other"  # type: ignore[misc]  # frozen


def test_tool_run_outcome_has_no_raw_output_field() -> None:
    """TC-ArgusAgent-TOOL-001-10 — the structural redaction guarantee: no raw-output field exists."""
    fields = set(ToolRunOutcome.model_fields)
    forbidden = {"stdout", "stderr", "raw_stdout", "raw_stderr", "output", "source", "value"}
    assert fields & forbidden == set(), f"a raw-output field leaked onto the model: {fields}"
    # failure_reason is a sanitized TOKEN slot only (None when OK).
    assert "failure_reason" in fields


def test_tool_run_outcome_has_no_float_and_round_trips() -> None:
    """TC-ArgusAgent-TOOL-001-11 — metrics are int (no float); round-trips through 1.1 serializer."""
    out = ToolRunOutcome(
        tool_id="radon",
        file_path="pkg/mod.py",
        outcome=ToolOutcome.OK,
        total_loc=42,
        total_complexity=7,
    )
    assert isinstance(out.total_loc, int)
    assert isinstance(out.total_complexity, int)
    payload = out.model_dump(mode="json")
    blob = canonical.dumps_bytes(payload)  # the single 1.1 serializer (rejects float)
    assert canonical.loads(blob.decode("utf-8")) == payload


# ── AC5 — grade + fold + no-double-count + regression-safe ──────────────────────


def test_already_graded_files_are_not_double_counted() -> None:
    """TC-ArgusAgent-TOOL-001-12 — a file the depth path already graded is skipped by breadth."""
    detector = ToolRunnerDetector(tool_invoker=lambda fp, src: _ok(fp))
    result = detector.run(
        targets=[("graded.py", "x=1\n"), ("ungraded.py", "y=2\n")],
        already_graded_paths=("graded.py",),
    )
    paths = {e.file_path for e in result.entries}
    assert paths == {"ungraded.py"}  # the already-graded file gets NO breadth entry
    assert result.entries[0].depth is CoverageDepth.TOOL_SCANNED_ONLY


def test_clean_run_all_already_graded_is_ledger_byte_identical_no_new_grade() -> None:
    """TC-ArgusAgent-TOOL-001-13 — every file already graded → no NEW entry/finding (regression-safe)."""
    detector = ToolRunnerDetector(tool_invoker=lambda fp, src: _ok(fp))
    targets = [("a.py", "x=1\n"), ("b.py", "y=2\n")]
    result = detector.run(targets=targets, already_graded_paths=("a.py", "b.py"))
    assert result.entries == ()
    assert result.findings == ()
    assert result.degraded == ()


def test_classification_is_deterministic_regardless_of_input_order() -> None:
    """TC-ArgusAgent-TOOL-001-14 — same invocations in different orders → identical result bytes."""
    detector = ToolRunnerDetector()
    invs_a = [_ok("c.py"), _ok("a.py"), _ok("b.py")]
    invs_b = [_ok("b.py"), _ok("c.py"), _ok("a.py")]
    res_a = detector.classify_outcomes(invs_a)
    res_b = detector.classify_outcomes(invs_b)
    assert canonical.dumps_bytes(res_a.model_dump(mode="json")) == canonical.dumps_bytes(
        res_b.model_dump(mode="json")
    )


# ── AC7 — purity-of-classification / single serializer / typed error ────────────


def test_classify_outcomes_is_pure_and_typed() -> None:
    """TC-ArgusAgent-TOOL-001-15 — classify_outcomes is a pure function; rejects a bad element."""
    detector = ToolRunnerDetector()
    # Pure: same input twice → identical output.
    invs = [_ok("a.py"), ToolInvocation(file_path="b.py", outcome=ToolOutcome.CRASHED)]
    first = detector.classify_outcomes(invs)
    second = detector.classify_outcomes(invs)
    assert canonical.dumps_bytes(first.model_dump(mode="json")) == canonical.dumps_bytes(
        second.model_dump(mode="json")
    )
    # Typed failure on a non-invocation element.
    with pytest.raises(ToolRunnerError):
        detector.classify_outcomes(["not-an-invocation"])  # type: ignore[list-item]


def test_findings_are_recordings_with_verifiable_locators() -> None:
    """TC-ArgusAgent-TOOL-001-16 — every emitted finding is a 1.2 Recording with ≥1 locator (FR13)."""
    detector = ToolRunnerDetector(tool_invoker=_failing_invoker(ToolOutcome.CRASHED))
    result = detector.run(targets=[("pkg/mod.py", "x=1\n")])
    for finding in result.findings:
        assert isinstance(finding, Recording)
        assert len(finding.locators) >= 1
