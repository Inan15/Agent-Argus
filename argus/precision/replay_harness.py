"""Story 6.6 — the PURE precision replay harness (FR20 precision MEASUREMENT).

Verification area ArgusAgent-PRECISION (``TC-ArgusAgent-PRECISION-001-NN`` — the FIRST file in
that area; the index starts at 01, locked here). Drivers: ArgusAgent-FR-20 (ArgusAgent
validates its own detectors against the FR20 defect cartridges with golden
expected-findings keys — this module computes the precision NUMBER over that
substrate), ArgusAgent-FR-13 (the TP/FP diff matches an emitted finding on its rule-id +
verdict-eligibility + advisory flag — never source bytes), ArgusAgent-NFR-D1/D2 (the
precision computation is deterministic + ZERO-LLM-token — a pure fold over the
already-recorded findings; this module makes NO LLM call and reads no clock /
random), ArgusAgent-NFR-P1 (the precision number + per-cartridge rows are
byte-reproducible across two runs over the same corpus — fixed-precision, no
float), ArgusAgent-NFR-S1 (no source/secret byte from any cartridge appears in the
precision result / rows — the result carries only counts + rule-id provenance +
the fixed-precision ratio string), ArgusAgent-AR4 (precision = TP / (TP + FP) is an
exact ``Fraction`` stored as a ``"num/den"`` string ratio — NEVER a ``float``),
ArgusAgent-AR8 (PURE core — no clock, no LLM, no random; its ONE declared impure edge is the
LAZY ``_registry_module()``, strictly LESS I/O than the module-level import it replaced —
DF-9-2-A), ArgusAgent-NFR-M1/M2 (<=1200-line files; the frozen Epic-1..6 contracts + the 6.5
``_registry.py`` shape are unchanged — this module COMPOSES them, edits none).

What this module IS (partial-reuse note, AI-E5-7)
-------------------------------------------------
It is the PURE diff/classify/roll-up CORE. It REUSES the 6.5 substrate BY VALUE:
the caller (``tests/test_precision_replay.py``) stages each registry
cartridge via the LOCKED ``stage_cartridge`` + audits it via the deterministic
zero-token ``run_audit_detailed`` + reads the emitted findings through the
``ApaaStoreReader`` (exactly as the 6.5 self-audit harness does), then feeds the
emitted findings + the ``CARTRIDGE_REGISTRY`` ground truth to ``compute_precision``
here. This module:

- REUSES the SAME 6.5 match key ``(rule_id, depth_supported is not None,
  advisory)`` — ``finding_match_key`` derives it from an emitted ``Recording`` and
  ``golden_match_key`` derives the IDENTICAL key from a registry ``GoldenFinding``
  (DN-MATCH-KEY-REUSE — no second, divergent key; the precision number and the 6.5
  self-audit agree on what "the same finding" means, §3.3).
- REUSES / EXTENDS the 6.5 ``precision_gate_status()`` marker — it does NOT fork a
  second marker; ``precision_gate_status_for`` builds the gate-status STRING that
  carries the computed number ALONGSIDE the provisional flag (DN-PROVISIONAL).
- ADDS NO parallel pipeline runner, NO second serializer, NO second hasher, NO
  second golden-key store (§3.3 / AR7).

THE OI1 LOCK (DN-PROVISIONAL — the central honesty constraint, read twice)
--------------------------------------------------------------------------
Validation-set N is LOCKED at 5; populated PHASED 3->5; precision is measured over
FINDINGS not repos; the >=80%-precision gate is PROVISIONAL below N=5. This module
COMPUTES a real precision number from whatever the corpus currently holds AND
reports it PROVISIONALLY: ``PrecisionResult.provisional`` is ``True`` unless the
corpus has genuinely reached N>=5 distinct planted-defect cartridges AND the
caller has recorded the validation protocol's per-metric pass/fail as cleared
(``protocol_cleared=True``). The harness does NOT silently flip the gate to
cleared from a thin corpus — over-claiming a cleared >=80% gate is the exact
failure mode this lock forbids. As of Story 6.6 the corpus is below N=5, so the
gate is reported PROVISIONAL and the number is an EARLY/PROVISIONAL signal.

The four DECLARED precision-replay members (AI-E5-1 complete-the-declared-set)
-----------------------------------------------------------------------------
  (1) precision computation over FINDINGS — TP/FP/FN classification (compute_precision)
  (2) the clean-repo false-positive denominator (R6) — any BLOCKING finding on a
      clean repo (empty golden key / max_blocking == 0) is an FP (DN-FP-DENOMINATOR)
  (3) the validation protocol — a committed .md deliverable (DN-PROTOCOL; not code)
  (4) the provisional-gate honesty roll-up (DN-PROVISIONAL — the OI1 keystone)
Members (1)(2)(4) live here + are asserted in the test module; member (3) is the
committed ``precision-validation-protocol.md`` referenced by the protocol field.

Precision over FINDINGS, not repos (the OI1 lock)
-------------------------------------------------
Precision = TP / (TP + FP) over the FINDING counts (NOT a repos-passed fraction).
By convention precision over an empty denominator (TP + FP == 0 — no finding
emitted across the corpus) is the exact ``Fraction(1, 1)`` ("no false positive
emitted"); the result carries the denominator so the caller can see the count is
degenerate. Recall is reported as a sibling diagnostic (TP / (TP + FN)) but the
GATE is precision (the OI1 lock).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import TYPE_CHECKING, Any

# REUSE the 6.5 cartridge registry as the labeled ground-truth source (no fork). It lives
# under tests/cartridges/ — REPOSITORY-ONLY, absent from the built distribution — so it is
# resolved ON DEMAND, never at module import time (DF-9-2-A). It carries NO source bytes
# (value-free golden key, the 6.5 NFR-S1 contract), so importing it leaks no secret byte.
_CARTRIDGES_DIR = Path(__file__).resolve().parents[2] / "tests" / "cartridges"
if TYPE_CHECKING:
    from _registry import CartridgeSpec, GoldenFinding  # type: ignore[import-not-found]


def _registry_module() -> Any:
    """Resolve ``_registry`` lazily — this function IS this module's declared impure edge."""
    if _CARTRIDGES_DIR.is_dir() and str(_CARTRIDGES_DIR) not in sys.path:
        sys.path.insert(0, str(_CARTRIDGES_DIR))
    import _registry  # type: ignore[import-not-found]

    return _registry


__all__ = [
    "MatchKey",
    "CartridgePrecisionRow",
    "PrecisionResult",
    "finding_match_key",
    "golden_match_key",
    "compute_precision",
    "precision_gate_status_for",
]

# The shared 6.5 match key: (rule_id, verdict_eligible, advisory). ``verdict_eligible``
# is ``depth_supported is not None`` for an emitted Recording (the 6.5 convention).
MatchKey = tuple[str, bool, bool]


def finding_match_key(finding: object) -> MatchKey:
    """Derive the SHARED 6.5 match key from an emitted ``Recording`` (DN-MATCH-KEY-REUSE).

    ``(rule_id, depth_supported is not None, advisory)`` — IDENTICAL to the key the
    6.5 self-audit harness uses (``test_cartridge_selfaudit._emitted_keys``). Reads
    only the rule-id provenance + the two booleans — NEVER source bytes (NFR-S1).
    """
    return (
        finding.rule_id,  # type: ignore[attr-defined]
        finding.depth_supported is not None,  # type: ignore[attr-defined]
        finding.advisory,  # type: ignore[attr-defined]
    )


def golden_match_key(golden: GoldenFinding) -> MatchKey:
    """Derive the IDENTICAL match key from a registry ``GoldenFinding`` (no divergent key).

    ``GoldenFinding.verdict_eligible`` is the 6.5 ``depth_supported is not None``
    convention, so this key is byte-comparable with ``finding_match_key``.
    """
    return (golden.rule_id, golden.verdict_eligible, golden.advisory)


@dataclass(frozen=True)
class CartridgePrecisionRow:
    """One cartridge's precision contribution — counts + rule-id provenance only (NFR-S1).

    Carries NO source/secret bytes: ``fp_rule_ids`` / ``fn_rule_ids`` are the
    detector RULE-ID provenance (e.g. ``"vacuous_test_ast"``), never the planted
    secret/source value. ``is_clean_repo`` flags a true-negative repo (empty golden
    key / ``max_blocking == 0``) whose blocking findings populate the FP denominator.
    """

    cartridge_id: str
    kind: str
    is_clean_repo: bool
    tp: int
    fp: int
    fn: int
    fp_rule_ids: tuple[str, ...]
    fn_rule_ids: tuple[str, ...]


@dataclass(frozen=True)
class PrecisionResult:
    """The PURE precision roll-up the harness returns (DN-RESULT-SCHEMA).

    Carries per-cartridge rows + the corpus TP/FP/FN totals + the precision number
    as a fixed-precision STRING ratio (``Fraction`` rendered ``"num/den"`` — NEVER a
    float, AR4) + the labeled-cartridge count ``n`` + the locked floor + the
    ``provisional`` flag + the gate-status string. PURE DATA — no clock, LLM or random
    (AR8; the producer's ONE I/O edge is ``_registry_module()``). REUSES the 6.5 marker.

    ``precision`` is the exact ``Fraction`` (the in-memory truth); ``precision_ratio``
    is its committed STRING form (``f"{num}/{den}"``) — the only precision surface
    that crosses a byte boundary, so it is fixed-precision by construction. The
    threshold check (>=80%) compares the exact ``Fraction`` against
    ``Fraction(4, 5)`` — no float rounding.
    """

    rows: tuple[CartridgePrecisionRow, ...]
    total_tp: int
    total_fp: int
    total_fn: int
    clean_repo_fp: int
    precision: Fraction
    precision_ratio: str
    recall: Fraction
    recall_ratio: str
    n: int
    floor_n: int
    provisional: bool
    gate_status: str

    @property
    def meets_threshold(self) -> bool:
        """Whether the EXACT precision Fraction is >= 80% (Fraction(4, 5)) — no float."""
        return self.precision >= Fraction(4, 5)


# The locked >=80%-precision externalization gate threshold, as an EXACT Fraction
# (NEVER a float). The PRD's >=80% precision gate.
_PRECISION_GATE_THRESHOLD = Fraction(4, 5)


def _is_clean_repo(spec: CartridgeSpec) -> bool:
    """A clean (true-negative) repo: empty golden key AND ``max_blocking == 0`` (R6).

    The ``clean_control`` row + the clean-shaped ``trap`` / ``no_crash`` rows: their
    golden key is empty and they tolerate ZERO blocking findings, so ANY blocking
    finding on them is a false positive (the FP denominator, DN-FP-DENOMINATOR).
    """
    return not spec.required_findings and spec.max_blocking == 0


def _ratio_string(fraction: Fraction) -> str:
    """Render an exact ``Fraction`` as the committed ``"num/den"`` string (AR4, no float).

    Mirrors the LOCKED 1.1 canonical ``Fraction -> "num/den"`` encoding so the
    precision surface that crosses a byte boundary is fixed-precision + byte-stable
    (NFR-P1). ``Fraction`` is always normalized (denominator > 0, gcd-reduced).
    """
    return f"{fraction.numerator}/{fraction.denominator}"


def compute_precision(
    emitted_keys_by_cartridge: dict[str, frozenset[MatchKey]],
    *,
    registry: tuple[CartridgeSpec, ...] | None = None,
    protocol_cleared: bool = False,
    protocol_path: str = "_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md",
) -> PrecisionResult:
    """Diff emitted findings against the registry ground truth → a PURE PrecisionResult.

    AC1/AC2/AC3/AC5. Pure apart from ONE declared edge — ``_registry_module()`` resolves
    the cartridge registry LAZILY (DF-9-2-A; strictly less I/O than the module-level import
    it replaced) — and otherwise no clock, no LLM, no random (AR8). The caller supplies
    ``emitted_keys_by_cartridge`` — a map of ``cartridge_id -> frozenset`` of emitted match
    keys (each ``(rule_id, verdict_eligible, advisory)``, derived via ``finding_match_key``);
    this module never stages/audits a repo (the impure staging is the test shell, §3.3).

    Classification, per the 6.5 match key (DN-MATCH-KEY-REUSE):
    - an emitted key IN the cartridge's golden key -> **TP**;
    - an emitted **BLOCKING** key (``key[1]`` verdict-eligible is True) NOT in the
      golden key -> **FP** — a false ACCUSATION (especially on a clean repo, the R6
      denominator, DN-FP-DENOMINATOR). An ADVISORY over-emission (``key[1]`` False)
      is NOT a false positive: advisory-by-contract findings (cross-cutting #6) do
      not move the verdict and are not false accusations — the precision moat is
      "no false BLOCKING accusation", matching the 6.5 ``max_blocking == 0`` floor
      (a clean repo legitimately emits advisory findings, e.g. a redacted-secret
      advisory, while staying RELEASE_READY);
    - a golden-key member NOT emitted -> **FN**.

    Precision = TP / (TP + FP) as an exact ``Fraction`` (AR4). The gate stays
    PROVISIONAL below N=5 (OR with the protocol pass/fail not recorded cleared) —
    DN-PROVISIONAL; the harness never silently flips the gate to cleared.

    A registry cartridge with NO emitted-keys entry (a staging/audit failure the
    caller did not record) raises ``KeyError`` with the cartridge id — a NAMED
    failure, never a silent skip (the AI-E5-1 no-crash leg; the caller converts a
    staging raise into a NAMED assertion before reaching here).
    """
    registry_module = _registry_module()
    registry = registry_module.CARTRIDGE_REGISTRY if registry is None else registry
    floor_n = registry_module.VALIDATION_SET_FLOOR_N
    rows: list[CartridgePrecisionRow] = []
    total_tp = total_fp = total_fn = clean_repo_fp = 0

    for spec in registry:
        if spec.cartridge_id not in emitted_keys_by_cartridge:
            raise KeyError(
                f"cartridge {spec.cartridge_id!r}: no emitted-findings entry supplied "
                f"to compute_precision (a staging/audit failure must be a NAMED "
                f"assertion upstream, never a silent skip — AI-E5-1)"
            )
        emitted = emitted_keys_by_cartridge[spec.cartridge_id]
        golden = {golden_match_key(gf) for gf in spec.required_findings}
        is_clean = _is_clean_repo(spec)

        tp_keys = emitted & golden
        # An FP is an emitted key NOT in the golden key that is a BLOCKING (verdict-
        # eligible, key[1] is True) finding — a false ACCUSATION. An advisory
        # over-emission (key[1] False) is advisory-by-contract (cross-cutting #6): it
        # does not move the verdict and is not a false positive. This matches the 6.5
        # ``max_blocking == 0`` clean floor (a clean repo legitimately emits a
        # redacted-secret advisory while staying RELEASE_READY).
        fp_keys = {k for k in (emitted - golden) if k[1]}
        fn_keys = golden - emitted

        tp = len(tp_keys)
        fp = len(fp_keys)
        fn = len(fn_keys)

        # The clean-repo FP contribution (R6): a BLOCKING finding on a clean repo
        # (empty golden key) is the credibility-critical false accusation. Track the
        # clean-repo FP total so the denominator's clean contribution is EXPLICIT in
        # the result (AC3 — RED-first against a harness that ignores clean-repo FPs).
        if is_clean:
            clean_repo_fp += fp

        total_tp += tp
        total_fp += fp
        total_fn += fn

        rows.append(
            CartridgePrecisionRow(
                cartridge_id=spec.cartridge_id,
                kind=spec.kind,
                is_clean_repo=is_clean,
                tp=tp,
                fp=fp,
                fn=fn,
                fp_rule_ids=tuple(sorted(k[0] for k in fp_keys)),
                fn_rule_ids=tuple(sorted(k[0] for k in fn_keys)),
            )
        )

    # Precision = TP / (TP + FP) over FINDINGS (the OI1 lock), exact Fraction (AR4).
    # An empty denominator (no finding emitted) is Fraction(1, 1) — "no FP emitted";
    # the degenerate count is visible via total_fp/total_tp on the result.
    precision_den = total_tp + total_fp
    precision = Fraction(total_tp, precision_den) if precision_den else Fraction(1, 1)
    recall_den = total_tp + total_fn
    recall = Fraction(total_tp, recall_den) if recall_den else Fraction(1, 1)

    n = registry_module.populated_planted_defect_count()
    # DN-PROVISIONAL: the gate is provisional UNLESS the corpus genuinely reached
    # N>=5 distinct planted-defect cartridges AND the protocol pass/fail is recorded
    # cleared AND the exact precision Fraction meets the >=80% threshold. The harness
    # never silently clears the gate from a thin corpus (the OI1 over-claim ban).
    provisional = not (
        n >= floor_n
        and protocol_cleared
        and precision >= _PRECISION_GATE_THRESHOLD
    )

    return PrecisionResult(
        rows=tuple(rows),
        total_tp=total_tp,
        total_fp=total_fp,
        total_fn=total_fn,
        clean_repo_fp=clean_repo_fp,
        precision=precision,
        precision_ratio=_ratio_string(precision),
        recall=recall,
        recall_ratio=_ratio_string(recall),
        n=n,
        floor_n=floor_n,
        provisional=provisional,
        gate_status=precision_gate_status_for(
            precision=precision,
            n=n,
            provisional=provisional,
            protocol_path=protocol_path,
            floor_n=floor_n,
        ),
    )


def precision_gate_status_for(
    *,
    precision: Fraction,
    n: int,
    provisional: bool,
    protocol_path: str,
    floor_n: int | None = None,
) -> str:
    """The 6.6 gate-status string — REUSES the 6.5 marker convention (no forked marker).

    DN-PROVISIONAL (AC5): the computed precision number is reported ALONGSIDE the
    provisional flag. The 6.5 ``precision_gate_status()`` marker was a STATUS string
    that carried NO number (6.5 computed none); 6.6 EXTENDS that convention into a
    status string that DOES carry the number but stays scrupulously honest about the
    provisional state. The precision is rendered as the EXACT ``"num/den"`` ratio
    (AR4 — no float / no rounded percentage that could over-claim).

    Below the N=5 floor the string says "provisional ... EARLY/PROVISIONAL signal"
    and points at the validation protocol; it NEVER says "cleared" unless the gate
    has genuinely flipped (``provisional is False``).
    """
    floor_n = _registry_module().VALIDATION_SET_FLOOR_N if floor_n is None else floor_n
    ratio = _ratio_string(precision)
    if provisional:
        return (
            f"provisional (Story 6.6 precision harness; precision={ratio} over FINDINGS "
            f"not repos; N={n} labeled cartridges populated, floor N={floor_n}; "
            f"the >=80% externalization gate stays PROVISIONAL until N>={floor_n} "
            f"with the validation protocol applied — this number is an EARLY/PROVISIONAL "
            f"signal, NOT a cleared gate; adjudication method: {protocol_path})"
        )
    return (
        f"cleared (Story 6.6 precision harness; precision={ratio} >= 4/5 over FINDINGS; "
        f"N={n} labeled cartridges >= floor N={floor_n}; the validation "
        f"protocol's per-metric pass/fail is recorded cleared — {protocol_path})"
    )
