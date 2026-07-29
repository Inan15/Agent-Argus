"""Frozen recording-schema model tests (story 1.2).

Verification area ArgusAgent-LEDGER (TC-ArgusAgent-LEDGER-002-xx). Covers AC5/AC6/AC7/AC8 of
story 1.2: the frozen first-class ``Recording`` contract (``frozen=True,
extra="forbid"``, every downstream-read field reserved), locator-or-reject as a
typed failure at the data layer (FR13 support / AR10), the ``Locator`` span
validation, the zero-``float`` invariant, the additive-optional-field hash
invariance (NFR-M2), and the byte-stable golden round-trip through the Story 1.1
canonical serializer + envelope (REUSED, never a second serializer).

PURE-function / model golden tests — zero LLM tokens (NFR-D2). Golden constants
are recorded so a future byte-drift fails loudly (NFR-P1).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from argus.ledger.coverage_ledger import CoverageDepth
from argus.ledger.recording import (
    RECORDING_SCHEMA_VERSION,
    Locator,
    Recording,
    RecordingValidationError,
)
from argus.store import canonical
from argus.store.envelope import compute_content_hash

# ── FROZEN GOLDEN FIXTURE — a change is a cross-host reproducibility break ──
GOLDEN_RECORDING_CANONICAL = (
    '{"advisory":false,"cartridge_id":null,"claim_present":true,'
    '"coverage_envelope_slice":null,"depth_supported":"audited_deep",'
    '"locators":[{"ast_span":null,"end_line":12,"file_path":"a.py",'
    '"start_line":10}],"partition_id":"root","recording_id":"rec-1",'
    '"rule_id":"R-001","schema_version":"1"}\n'
)
GOLDEN_RECORDING_CONTENT_HASH = (
    "62441c4171f83d9681b5cb9365571a4f7c1ab9a4beb36cc9a6dc90ad14c72ca5"
)


def _golden_recording() -> Recording:
    return Recording(
        recording_id="rec-1",
        rule_id="R-001",
        advisory=False,
        depth_supported=CoverageDepth.AUDITED_DEEP,
        claim_present=True,
        locators=(Locator(file_path="a.py", start_line=10, end_line=12),),
    )


class TestLocator:
    """TC-ArgusAgent-LEDGER-002-01..05 — verifiable locator (AC6)."""

    def test_well_formed_span_builds(self) -> None:
        loc = Locator(file_path="a.py", start_line=1, end_line=1)
        assert loc.start_line == 1
        assert loc.end_line == 1

    def test_end_before_start_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Locator(file_path="a.py", start_line=10, end_line=5)

    def test_line_below_one_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Locator(file_path="a.py", start_line=0, end_line=1)

    def test_is_frozen(self) -> None:
        loc = Locator(file_path="a.py", start_line=1, end_line=2)
        with pytest.raises(Exception):
            loc.start_line = 5  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        with pytest.raises(ValidationError):
            Locator(
                file_path="a.py",
                start_line=1,
                end_line=2,
                nope="x",  # type: ignore[call-arg]
            )


class TestRecordingBuild:
    """TC-ArgusAgent-LEDGER-002-10..16 — frozen first-class recording (AC5)."""

    def test_reserves_downstream_fields(self) -> None:
        rec = _golden_recording()
        assert rec.recording_id == "rec-1"
        assert rec.finding_id == "rec-1"
        assert rec.partition_id == "root"
        assert rec.rule_id == "R-001"
        assert rec.cartridge_id is None
        assert rec.advisory is False
        assert rec.depth_supported is CoverageDepth.AUDITED_DEEP
        assert rec.claim_present is True
        assert rec.coverage_envelope_slice is None
        assert rec.schema_version == RECORDING_SCHEMA_VERSION
        assert len(rec.locators) == 1

    def test_is_frozen(self) -> None:
        rec = _golden_recording()
        with pytest.raises(Exception):
            rec.advisory = True  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        with pytest.raises(ValidationError):
            Recording(
                recording_id="r",
                rule_id="R",
                advisory=False,
                locators=(Locator(file_path="a.py", start_line=1, end_line=1),),
                nope="x",  # type: ignore[call-arg]
            )


class TestLocatorOrReject:
    """TC-ArgusAgent-LEDGER-002-20..23 — locator-or-reject typed failure (AC6/AR10)."""

    def test_empty_locators_raises_typed_error(self) -> None:
        with pytest.raises(ValidationError) as ei:
            Recording(
                recording_id="r",
                rule_id="R",
                advisory=False,
                locators=(),
            )
        # The model_validator wraps the typed ArgusAgent error inside Pydantic's
        # ValidationError; assert the rejection message surfaces.
        assert "locator" in str(ei.value).lower()

    def test_recording_validation_error_is_valueerror_subclass(self) -> None:
        assert issubclass(RecordingValidationError, ValueError)

    def test_with_one_locator_validates(self) -> None:
        rec = Recording(
            recording_id="r",
            rule_id="R",
            advisory=False,
            locators=(Locator(file_path="a.py", start_line=1, end_line=1),),
        )
        assert len(rec.locators) == 1

    def test_no_silent_empty_default(self) -> None:
        # locators has no default — omitting it is a required-field error, never a
        # silent empty locator.
        with pytest.raises(ValidationError):
            Recording(recording_id="r", rule_id="R", advisory=False)  # type: ignore[call-arg]


class TestNoFloatInvariant:
    """TC-ArgusAgent-LEDGER-002-30 — zero-float invariant (AC7)."""

    def test_recording_serializes_clean(self) -> None:
        # canonical.dumps rejects float; a clean serialize proves no float leaves.
        canonical.dumps(_golden_recording().model_dump())  # must not raise


class TestAdditiveFieldHashInvariance:
    """TC-ArgusAgent-LEDGER-002-40..41 — additive-only hash semantics (NFR-M2 / AC5)."""

    def test_optional_default_absent_vs_explicit_same_hash(self) -> None:
        # An OPTIONAL field left at its default vs explicitly set to that same
        # default must not change the content hash (additive-only).
        rec_implicit = _golden_recording()
        rec_explicit = Recording(
            recording_id="rec-1",
            rule_id="R-001",
            advisory=False,
            depth_supported=CoverageDepth.AUDITED_DEEP,
            claim_present=True,
            cartridge_id=None,
            coverage_envelope_slice=None,
            locators=(Locator(file_path="a.py", start_line=10, end_line=12),),
        )
        assert compute_content_hash(rec_implicit.model_dump()) == compute_content_hash(
            rec_explicit.model_dump()
        )

    def test_schema_version_bump_changes_hash(self) -> None:
        rec_v1 = _golden_recording()
        rec_v2 = Recording(
            schema_version="2",
            recording_id="rec-1",
            rule_id="R-001",
            advisory=False,
            depth_supported=CoverageDepth.AUDITED_DEEP,
            claim_present=True,
            locators=(Locator(file_path="a.py", start_line=10, end_line=12),),
        )
        assert compute_content_hash(rec_v1.model_dump()) != compute_content_hash(
            rec_v2.model_dump()
        )


class TestRecordingGoldenRoundTrip:
    """TC-ArgusAgent-LEDGER-002-50..53 — byte-stable golden round-trip (AC8)."""

    def test_golden_canonical_string_frozen(self) -> None:
        assert canonical.dumps(_golden_recording().model_dump()) == (
            GOLDEN_RECORDING_CANONICAL
        )

    def test_golden_content_hash_frozen(self) -> None:
        assert compute_content_hash(_golden_recording().model_dump()) == (
            GOLDEN_RECORDING_CONTENT_HASH
        )

    def test_round_trips_to_equal_model(self) -> None:
        rec = _golden_recording()
        restored = Recording(**canonical.loads(canonical.dumps(rec.model_dump())))
        assert restored == rec

    def test_content_hash_reproducible(self) -> None:
        assert compute_content_hash(_golden_recording().model_dump()) == (
            compute_content_hash(_golden_recording().model_dump())
        )
