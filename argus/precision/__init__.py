"""ArgusAgent precision-measurement package (Story 6.6).

Verification area ArgusAgent-PRECISION. Drivers: ArgusAgent-FR-20 (precision MEASUREMENT over
the FR20 defect-cartridge substrate), ArgusAgent-FR-13 (TP/FP diff matches on
rule-id + locator-bearing findings, never source bytes), ArgusAgent-NFR-D1/D2
(deterministic + zero-LLM-token pure fold), ArgusAgent-NFR-P1 (byte-reproducible),
ArgusAgent-NFR-S1 (no source/secret bytes in any precision surface), ArgusAgent-AR4
(fixed-precision ratio — Fraction/Decimal as a string, NEVER float).

This package holds the PURE precision replay harness (``replay_harness``) that
diffs emitted findings against the 6.5 cartridge-registry golden keys into
TP/FP/FN counts → a fixed-precision precision number, plus the false-positive
denominator drawn from the clean-control / trap / no-crash repos (R6).

OI1 honesty keystone: the >=80%-precision gate stays PROVISIONAL until the
corpus reaches the locked N=5 floor with the validation protocol applied — the
harness computes a number but reports it ALONGSIDE the provisional flag and
NEVER silently flips the gate to cleared.
"""

from __future__ import annotations

from argus.precision.replay_harness import (
    CartridgePrecisionRow,
    PrecisionResult,
    compute_precision,
    finding_match_key,
    golden_match_key,
    precision_gate_status_for,
)

__all__ = [
    "CartridgePrecisionRow",
    "PrecisionResult",
    "compute_precision",
    "finding_match_key",
    "golden_match_key",
    "precision_gate_status_for",
]
