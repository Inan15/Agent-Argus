"""Coverage-ledger model + determinism golden tests (story 1.2).

Verification area ArgusAgent-LEDGER (TC-ArgusAgent-LEDGER-001-xx). Covers AC1/AC2/AC3/AC4/
AC7/AC8 of story 1.2: the closed coverage-depth enum membership pin, the frozen
``extra="forbid"`` entry/aggregate models, the pure per-depth count accessor,
order-independent equality + byte-identical serialization, the claim-required
``audited_deep`` grading (silence -> shallow), the zero-``float`` invariant, and
the byte-stable golden round-trip through the Story 1.1 canonical serializer +
envelope (REUSED, never a second serializer).

These are PURE-function / model golden tests — zero LLM tokens (NFR-D2), no temp
dirs for the modules under test. The golden constants are recorded so a future
byte-drift fails loudly (NFR-P1).
"""

from __future__ import annotations

import pytest

from argus.ledger.coverage_ledger import (
    LEDGER_SCHEMA_VERSION,
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
    grade_entry,
)
from argus.store import canonical
from argus.store.envelope import compute_content_hash

# ── FROZEN GOLDEN FIXTURE (do not edit without intent — downstream stories fold
#    over these exact bytes; a change is a cross-host reproducibility break) ──
GOLDEN_LEDGER_CANONICAL = (
    '{"entries":[{"claim_present":false,"depth":"skipped","file_path":"a.py",'
    '"partition_id":"root","recording_ids":[]},{"claim_present":true,'
    '"depth":"audited_deep","file_path":"b.py","partition_id":"root",'
    '"recording_ids":["r1"]},{"claim_present":false,"depth":"inferred",'
    '"file_path":"c.py","partition_id":"root","recording_ids":[]}],'
    '"partition_id":"root","schema_version":"1"}\n'
)
GOLDEN_LEDGER_CONTENT_HASH = (
    "62f56fe738838971ed3032b32a110786c9e9ff8c693a8615e0747febb88f1a1e"
)


def _golden_entries() -> list[CoverageLedgerEntry]:
    return [
        CoverageLedgerEntry(
            file_path="b.py",
            depth=CoverageDepth.AUDITED_DEEP,
            claim_present=True,
            recording_ids=("r1",),
        ),
        CoverageLedgerEntry(
            file_path="a.py", depth=CoverageDepth.SKIPPED, claim_present=False
        ),
        CoverageLedgerEntry(
            file_path="c.py", depth=CoverageDepth.INFERRED, claim_present=False
        ),
    ]


class TestCoverageDepthEnum:
    """TC-ArgusAgent-LEDGER-001-01..04 — closed fixed-enum (AC1)."""

    def test_membership_set_pinned(self) -> None:
        # AC1: exactly these five members — adding/removing/renaming fails here.
        assert {m.name for m in CoverageDepth} == {
            "AUDITED_DEEP",
            "AUDITED_SHALLOW",
            "TOOL_SCANNED_ONLY",
            "INFERRED",
            "SKIPPED",
        }

    def test_string_values_pinned(self) -> None:
        # AC1: the snake_case value strings ARE the wire contract.
        assert {m.value for m in CoverageDepth} == {
            "audited_deep",
            "audited_shallow",
            "tool_scanned_only",
            "inferred",
            "skipped",
        }

    def test_exactly_five_members(self) -> None:
        assert len(list(CoverageDepth)) == 5

    def test_str_valued_serializes_verbatim(self) -> None:
        # str-enum: members serialize as their value through canonical.dumps.
        assert canonical.dumps({"d": CoverageDepth.AUDITED_DEEP.value}) == (
            '{"d":"audited_deep"}\n'
        )


class TestCoverageLedgerEntry:
    """TC-ArgusAgent-LEDGER-001-10..15 — frozen per-file entry (AC2)."""

    def test_minimum_fields_present(self) -> None:
        entry = CoverageLedgerEntry(
            file_path="x.py", depth=CoverageDepth.AUDITED_SHALLOW, claim_present=True
        )
        assert entry.file_path == "x.py"
        assert entry.depth is CoverageDepth.AUDITED_SHALLOW
        assert entry.claim_present is True
        assert entry.recording_ids == ()
        assert entry.partition_id == "root"

    def test_is_frozen(self) -> None:
        entry = CoverageLedgerEntry(
            file_path="x.py", depth=CoverageDepth.SKIPPED, claim_present=False
        )
        with pytest.raises(Exception):
            entry.depth = CoverageDepth.AUDITED_DEEP  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CoverageLedgerEntry(
                file_path="x.py",
                depth=CoverageDepth.SKIPPED,
                claim_present=False,
                unexpected_field="boom",  # type: ignore[call-arg]
            )

    def test_partition_id_reserved_default_root(self) -> None:
        entry = CoverageLedgerEntry(
            file_path="x.py", depth=CoverageDepth.SKIPPED, claim_present=False
        )
        assert entry.partition_id == "root"


class TestCoverageLedgerAggregate:
    """TC-ArgusAgent-LEDGER-001-20..28 — aggregate ledger + counts + determinism (AC3)."""

    def test_entries_stored_sorted_by_file_path(self) -> None:
        led = CoverageLedger.build(_golden_entries())
        assert [e.file_path for e in led.entries] == ["a.py", "b.py", "c.py"]

    def test_order_independent_equality(self) -> None:
        entries = _golden_entries()
        led_a = CoverageLedger.build(entries)
        led_b = CoverageLedger.build(list(reversed(entries)))
        assert led_a == led_b

    def test_order_independent_byte_identical_serialization(self) -> None:
        entries = _golden_entries()
        led_a = CoverageLedger.build(entries)
        led_b = CoverageLedger.build(list(reversed(entries)))
        assert canonical.dumps(led_a.model_dump()) == canonical.dumps(
            led_b.model_dump()
        )

    def test_counts_by_depth_zero_filled_for_every_member(self) -> None:
        led = CoverageLedger.build(_golden_entries())
        counts = led.counts_by_depth()
        assert set(counts.keys()) == set(CoverageDepth)
        assert counts[CoverageDepth.AUDITED_DEEP] == 1
        assert counts[CoverageDepth.SKIPPED] == 1
        assert counts[CoverageDepth.INFERRED] == 1
        assert counts[CoverageDepth.AUDITED_SHALLOW] == 0
        assert counts[CoverageDepth.TOOL_SCANNED_ONLY] == 0

    def test_deep_count_and_total(self) -> None:
        led = CoverageLedger.build(_golden_entries())
        assert led.deep_count() == 1
        assert led.total() == 3

    def test_schema_version_and_partition_defaults(self) -> None:
        led = CoverageLedger.build(_golden_entries())
        assert led.schema_version == LEDGER_SCHEMA_VERSION
        assert led.partition_id == "root"

    def test_is_frozen(self) -> None:
        led = CoverageLedger.build(_golden_entries())
        with pytest.raises(Exception):
            led.partition_id = "other"  # type: ignore[misc]

    def test_extra_forbid(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            CoverageLedger(entries=(), nope="x")  # type: ignore[call-arg]


class TestGradeEntrySilenceToShallow:
    """TC-ArgusAgent-LEDGER-001-30..34 — claim-required audited_deep (AC4)."""

    def test_deep_without_claim_downgrades_to_shallow(self) -> None:
        entry = grade_entry(
            file_path="x.py",
            proposed_depth=CoverageDepth.AUDITED_DEEP,
            claim_present=False,
        )
        assert entry.depth is CoverageDepth.AUDITED_SHALLOW
        assert entry.claim_present is False

    def test_deep_with_claim_records_deep(self) -> None:
        entry = grade_entry(
            file_path="x.py",
            proposed_depth=CoverageDepth.AUDITED_DEEP,
            claim_present=True,
        )
        assert entry.depth is CoverageDepth.AUDITED_DEEP
        assert entry.claim_present is True

    @pytest.mark.parametrize(
        "depth",
        [
            CoverageDepth.AUDITED_SHALLOW,
            CoverageDepth.TOOL_SCANNED_ONLY,
            CoverageDepth.INFERRED,
            CoverageDepth.SKIPPED,
        ],
    )
    def test_non_deep_depths_unchanged_without_claim(
        self, depth: CoverageDepth
    ) -> None:
        entry = grade_entry(
            file_path="x.py", proposed_depth=depth, claim_present=False
        )
        assert entry.depth is depth

    def test_grade_preserves_evidence_and_partition(self) -> None:
        entry = grade_entry(
            file_path="x.py",
            proposed_depth=CoverageDepth.AUDITED_DEEP,
            claim_present=True,
            recording_ids=("r1", "r2"),
            partition_id="root",
        )
        assert entry.recording_ids == ("r1", "r2")
        assert entry.partition_id == "root"


class TestNoFloatInvariant:
    """TC-ArgusAgent-LEDGER-001-40 — zero-float invariant (AC7)."""

    def test_no_float_fields_serialize(self) -> None:
        # The canonical serializer rejects float; a clean round-trip proves the
        # model carries no float leaves.
        led = CoverageLedger.build(_golden_entries())
        canonical.dumps(led.model_dump())  # must not raise

    def test_count_values_are_int(self) -> None:
        led = CoverageLedger.build(_golden_entries())
        for value in led.counts_by_depth().values():
            assert isinstance(value, int)
            assert not isinstance(value, bool)


class TestLedgerGoldenRoundTrip:
    """TC-ArgusAgent-LEDGER-001-50..53 — byte-stable golden round-trip (AC8)."""

    def test_golden_canonical_string_frozen(self) -> None:
        led = CoverageLedger.build(_golden_entries())
        assert canonical.dumps(led.model_dump()) == GOLDEN_LEDGER_CANONICAL

    def test_golden_content_hash_frozen(self) -> None:
        led = CoverageLedger.build(_golden_entries())
        assert compute_content_hash(led.model_dump()) == GOLDEN_LEDGER_CONTENT_HASH

    def test_round_trips_to_equal_model(self) -> None:
        led = CoverageLedger.build(_golden_entries())
        restored = CoverageLedger(**canonical.loads(canonical.dumps(led.model_dump())))
        assert restored == led

    def test_content_hash_reproducible(self) -> None:
        led_a = CoverageLedger.build(_golden_entries())
        led_b = CoverageLedger.build(list(reversed(_golden_entries())))
        assert compute_content_hash(led_a.model_dump()) == compute_content_hash(
            led_b.model_dump()
        )
