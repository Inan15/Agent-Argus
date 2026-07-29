"""Story 4.1 — negative-assurance wrapper + critical-set persistence round-trip.

Verification area ArgusAgent-VERDICT (``TC-ArgusAgent-VERDICT-001-NN``). Drivers: ArgusAgent-FR-17 /
NFR-A3 (the persisted wrapper), ArgusAgent-FR-4 (the persisted computed
``CriticalSubsystemSet`` — DF-2-3-B), ArgusAgent-NFR-A1 (content-hashed, prev-hash-chained
envelope), ArgusAgent-NFR-D3 (the point-in-time stamp is the envelope ``created_at``,
EXCLUDED from the content hash), ArgusAgent-NFR-S5 (containment-checked write via the 1.3
shell), ArgusAgent-NFR-P1 (byte-identical round-trip), AR4/AR11.

The wrapper + the critical set persist through the EXISTING ``ApaaStoreWriter`` →
``EnvelopeWriter.build`` → the single 1.1 ``canonical`` serializer — no second
serializer / writer. Re-reading via ``ApaaStoreReader`` reconstructs an EQUAL model
+ round-trips byte-identically.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from argus.cost.exhaustion import HaltReport, build_floor_report
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
)
from argus.ledger.critical_subsystems import (
    CriticalCandidate,
    CriticalSubsystemSet,
    identify_critical_subsystems,
)
from argus.ledger.depth_semantics import Criticality
from argus.store import canonical
from argus.store.envelope import GENESIS_PREV_HASH
from argus.store.reader import ApaaStoreReader
from argus.store.writer import ApaaStoreWriter
from argus.verdict.negative_assurance import (
    NegativeAssuranceVerdict,
    build_negative_assurance_verdict,
)
from argus.verdict.verdict_gate import evaluate_verdict

_NA_PRODUCER = "argus.verdict.negative_assurance"
_CRIT_PRODUCER = "argus.pipeline.critical_subsystems"


def _entry(path: str, depth: CoverageDepth, *, claim: bool = False) -> CoverageLedgerEntry:
    return CoverageLedgerEntry(file_path=path, depth=depth, claim_present=claim)


def _fixture() -> tuple[CoverageLedger, CriticalSubsystemSet, NegativeAssuranceVerdict]:
    ledger = CoverageLedger.build(
        [
            _entry("a_deep.py", CoverageDepth.AUDITED_DEEP, claim=True),
            _entry("café/тест_auth.py", CoverageDepth.AUDITED_SHALLOW),
            _entry("c.py", CoverageDepth.SKIPPED),
        ]
    )
    critical = identify_critical_subsystems(
        [
            CriticalCandidate(file_path="a_deep.py", criticality=Criticality.CRITICAL),
            CriticalCandidate(file_path="café/тест_auth.py", criticality=Criticality.CRITICAL),
        ],
        operator_designated=("ghost.py",),
    )
    verdict = evaluate_verdict(ledger, (), critical_subsystems_all_deep=False)
    halt = HaltReport(
        halted_on_exhaustion=False,
        total_credits=10,
        ceiling_credits=None,
        assessed_count=3,
        assessed_files=(),
        skipped_on_exhaustion_count=0,
        skipped_on_exhaustion_files=(),
    )
    floor = build_floor_report(verdict, halt)
    wrapper = build_negative_assurance_verdict(
        verdict, floor, critical, ledger, materiality_bar="default"
    )
    return ledger, critical, wrapper


def test_wrapper_persist_roundtrip_equal_and_byte_identical(tmp_path: Path) -> None:
    """TC-ArgusAgent-VERDICT-001-18 — AC5: write_payload → reader reconstructs an EQUAL wrapper byte-identically."""
    _ledger, _critical, wrapper = _fixture()
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    writer.paths.ensure_tree()

    locator = writer.write_payload(
        "state",
        wrapper.to_canonical_payload(),
        schema_version=wrapper.schema_version,
        producer=_NA_PRODUCER,
    )
    # Content-addressed filename (AR11).
    assert locator.startswith("state/") and locator.endswith(".json")

    envelope = reader.read_envelope(locator)  # re-verifies content_hash (tamper guard)
    assert envelope.producer == _NA_PRODUCER
    assert envelope.prev_hash == GENESIS_PREV_HASH  # chain head

    # Reconstruct an EQUAL model (deep_ratio re-installed as a live Fraction).
    payload = envelope.payload
    num, den = payload["deep_ratio"].split("/")
    reloaded = NegativeAssuranceVerdict.model_validate(
        {**payload, "deep_ratio": Fraction(int(num), int(den))}
    )
    assert reloaded == wrapper

    # Byte-identical round-trip: re-serializing the reloaded model's payload yields
    # the same bytes as the original wrapper's payload.
    assert canonical.dumps_bytes(wrapper.to_canonical_payload()) == canonical.dumps_bytes(
        reloaded.to_canonical_payload()
    )


def test_stamp_present_in_envelope_but_absent_from_hashed_payload(tmp_path: Path) -> None:
    """TC-ArgusAgent-VERDICT-001-19 — AC1/NFR-D3: created_at lives in the envelope, never in the hashed payload."""
    _ledger, _critical, wrapper = _fixture()
    writer = ApaaStoreWriter(tmp_path)
    writer.paths.ensure_tree()
    reader = ApaaStoreReader(tmp_path)

    # The wrapper payload carries NO created_at/run_id (they are envelope-only, NFR-D3).
    payload = wrapper.to_canonical_payload()
    assert "created_at" not in payload and "run_id" not in payload

    locator = writer.write_payload(
        "state", payload, schema_version=wrapper.schema_version, producer=_NA_PRODUCER
    )
    envelope = reader.read_envelope(locator)
    # The content hash is over the payload ONLY — a different stamp would not change it.
    from argus.store.envelope import compute_content_hash

    assert envelope.content_hash == compute_content_hash(payload)


def test_critical_subsystems_persist_roundtrip(tmp_path: Path) -> None:
    """TC-ArgusAgent-VERDICT-001-20 — AC4 (DF-2-3-B): the COMPUTED CriticalSubsystemSet persists + round-trips equal."""
    _ledger, critical, _wrapper = _fixture()
    writer = ApaaStoreWriter(tmp_path)
    reader = ApaaStoreReader(tmp_path)
    writer.paths.ensure_tree()

    locator = writer.write_payload(
        "state",
        critical.model_dump(mode="json"),
        schema_version=critical.schema_version,
        producer=_CRIT_PRODUCER,
    )
    envelope = reader.read_envelope(locator)  # re-verifies content_hash
    assert envelope.producer == _CRIT_PRODUCER
    reloaded = CriticalSubsystemSet.model_validate(envelope.payload)
    assert reloaded == critical
    # The origins (heuristic vs operator) + designated_but_unmatched survive — a
    # reader can distinguish an override of a genuine heuristic hit from a no-op
    # exclude (the DF-2-3-B closure).
    assert reloaded.origins == critical.origins
    assert reloaded.designated_but_unmatched == critical.designated_but_unmatched
    # Byte-identical round-trip: the reloaded payload re-serializes to the same bytes
    # as the original (the on-disk locator holds the ENVELOPE bytes; the payload bytes
    # are what the content hash is taken over).
    assert canonical.dumps_bytes(reloaded.model_dump(mode="json")) == canonical.dumps_bytes(
        critical.model_dump(mode="json")
    )
    assert canonical.dumps_bytes(envelope.payload) == canonical.dumps_bytes(
        critical.model_dump(mode="json")
    )


def test_critical_set_persist_carries_no_abs_path_or_source_byte(tmp_path: Path) -> None:
    """TC-ArgusAgent-VERDICT-001-21 — AC5 (NFR-S1, AI-E1-1): non-ASCII path intact; no abs-path/source byte."""
    _ledger, critical, _wrapper = _fixture()
    writer = ApaaStoreWriter(tmp_path)
    writer.paths.ensure_tree()
    reader = ApaaStoreReader(tmp_path)
    locator = writer.write_payload(
        "state", critical.model_dump(mode="json"),
        schema_version=critical.schema_version, producer=_CRIT_PRODUCER,
    )
    text = reader.read_bytes(locator).decode("utf-8")
    assert "café/тест_auth.py" in text  # non-ASCII path round-trips intact
    assert "/home/" not in text and "C:\\" not in text
    assert str(tmp_path) not in text  # no absolute host path leak
