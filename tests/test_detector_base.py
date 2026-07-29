"""Detector base — finding builder + Protocol (Story 1.5, AC3/AC4/AC6).

Verification area ArgusAgent-DETECT (TC-ArgusAgent-DETECT-001-NN). The locator-required
``Recording`` finding builder (FR13): a valid draft mints a valid 1.2 ``Recording``
reusing the 1.2 models verbatim; a malformed locator is rejected (not minted).
Pure — no tree-sitter dependency here.
"""

from __future__ import annotations

import pytest

from argus.detectors.base import (
    DegradedCondition,
    Detector,
    DetectorResult,
    FindingDraft,
    build_recording,
)
from argus.ledger.coverage_ledger import CoverageDepth
from argus.ledger.recording import Recording, RecordingValidationError
from argus.detectors.vacuous_test import VacuousTestDetector


def test_build_recording_mints_valid_recording() -> None:
    """TC-ArgusAgent-DETECT-001-80 — a valid draft mints a 1.2 Recording with one locator."""
    draft = FindingDraft(
        file_path="tests/test_widget.py",
        start_line=4,
        end_line=9,
        ast_span="function:test_widget@4-9",
        rule_id="vacuous_test_ast",
        advisory=True,
        coverage_envelope_slice="root",
    )
    rec = build_recording(
        draft, depth_supported=CoverageDepth.AUDITED_SHALLOW, claim_present=False
    )

    assert isinstance(rec, Recording)
    assert rec.rule_id == "vacuous_test_ast"
    assert rec.advisory is True
    assert rec.depth_supported is CoverageDepth.AUDITED_SHALLOW
    assert len(rec.locators) == 1
    loc = rec.locators[0]
    assert loc.file_path == "tests/test_widget.py"
    assert loc.start_line == 4
    assert loc.end_line == 9
    assert loc.ast_span == "function:test_widget@4-9"
    # recording_id is content-derived + stable (AR4/AR11), never uuid/arrival order.
    assert rec.recording_id == rec.finding_id
    assert rec.recording_id.startswith("vacuous_test_ast:")
    assert build_recording(draft).recording_id == rec.recording_id


def test_recording_id_distinct_per_finding() -> None:
    """TC-ArgusAgent-DETECT-001-81 — distinct findings get distinct content-derived ids."""
    base = dict(start_line=1, end_line=2, rule_id="vacuous_test_heuristic", advisory=True)
    a = build_recording(FindingDraft(file_path="tests/test_a.py", **base))
    b = build_recording(FindingDraft(file_path="tests/test_b.py", **base))
    assert a.recording_id != b.recording_id


def test_build_recording_rejects_malformed_locator() -> None:
    """TC-ArgusAgent-DETECT-001-82 — a malformed span is rejected (FR13 locator-or-reject)."""
    with pytest.raises(RecordingValidationError):
        build_recording(
            FindingDraft(
                file_path="tests/test_x.py",
                start_line=9,
                end_line=4,  # end < start → no verifiable locator
                rule_id="vacuous_test_heuristic",
                advisory=True,
            )
        )


def test_detector_result_is_frozen_and_extra_forbid() -> None:
    """TC-ArgusAgent-DETECT-001-83 — DetectorResult / DegradedCondition are frozen extra=forbid."""
    result = DetectorResult(degraded=(DegradedCondition(file_path="a.py", reason="x"),))
    with pytest.raises(Exception):
        result.findings = ()  # type: ignore[misc]
    with pytest.raises(Exception):
        DetectorResult(bogus=1)  # type: ignore[call-arg]


def test_vacuous_detector_satisfies_protocol() -> None:
    """TC-ArgusAgent-DETECT-001-84 — the concrete detector satisfies the Detector Protocol."""
    assert isinstance(VacuousTestDetector(), Detector)
