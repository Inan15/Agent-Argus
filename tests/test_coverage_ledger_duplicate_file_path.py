"""Regression lock for the CoverageLedger.build() duplicate-file_path guard.

Filed by wq-634, re-filing wq-627 (which closed exit 0 without building this).
Definition source: company/argus-coverage-dedupe-2026-09-22.md section 3 — a
file audited twice is one row, not two; a repeat must raise, never silently
dedupe, since dedupe hides a wrong FR6/FR16 deep-% denominator.
"""

from __future__ import annotations

import pytest

from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
    CoverageLedgerError,
)


def test_build_raises_on_duplicate_file_path() -> None:
    entries = [
        CoverageLedgerEntry(
            file_path="a.py", depth=CoverageDepth.AUDITED_DEEP, claim_present=True
        ),
        CoverageLedgerEntry(
            file_path="a.py", depth=CoverageDepth.SKIPPED, claim_present=False
        ),
    ]
    with pytest.raises(CoverageLedgerError):
        CoverageLedger.build(entries)


def test_build_does_not_fire_on_distinct_file_paths() -> None:
    entries = [
        CoverageLedgerEntry(
            file_path="a.py", depth=CoverageDepth.AUDITED_DEEP, claim_present=True
        ),
        CoverageLedgerEntry(
            file_path="b.py", depth=CoverageDepth.SKIPPED, claim_present=False
        ),
    ]
    led = CoverageLedger.build(entries)
    assert [e.file_path for e in led.entries] == ["a.py", "b.py"]
