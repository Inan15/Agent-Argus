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
ArgusAgent-AR8 (PURE core — no clock, no LLM, no random; its declared impure edges are the
LAZY ``registry_module()`` and, since Story 13.1, the LAZY ``corpus_manifest_module()`` —
each strictly LESS I/O than the module-level import it replaced, and each resolving a
DIFFERENT repository-only substrate rather than giving one substrate two doors —
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
# Story 13.1 / AC3a — the REPOSITORY corpus manifest. Same directory property, same reason,
# same treatment: repository-only, resolved on demand. See :func:`corpus_manifest_module`.
_CORPUS_DIR = Path(__file__).resolve().parents[2] / "tests" / "corpus"
if TYPE_CHECKING:
    from _registry import CartridgeSpec, GoldenFinding  # type: ignore[import-not-found]


def registry_module() -> Any:
    """Resolve ``_registry`` lazily — this function IS this module's declared impure edge.

    PUBLIC since Story 13.1 (12.6 / DN-7: *"need a helper from a ``_``-prefixed API? Promote it
    to public; never reach through"*). ``argus/dogfood/proof_run.py`` and the Story 13.1
    validation-set manifest both need the registry, and both must reach it through THIS
    function — a second path to the registry is the fork this codebase keeps refusing.
    """
    if _CARTRIDGES_DIR.is_dir() and str(_CARTRIDGES_DIR) not in sys.path:
        sys.path.insert(0, str(_CARTRIDGES_DIR))
    import _registry  # type: ignore[import-not-found]

    return _registry


#: The pre-13.1 private name, preserved so no existing caller breaks. It is an ALIAS, not a
#: second implementation — there is still exactly one way to reach the registry.
_registry_module = registry_module


def corpus_manifest_module() -> Any:
    """Resolve the Story 13.1 validation-set manifest lazily (``tests/corpus/_manifest.py``).

    This is a SECOND declared edge, and it is deliberately the same KIND as
    :func:`registry_module` rather than a second way to reach the same thing: it resolves a
    DIFFERENT repository-only substrate (the repository corpus, which measures precision)
    under the identical ``DF-9-2-A`` constraint that put the first one behind a lazy call.
    A module-level import of either would ship a wheel that cannot import, which
    ``tests/test_built_distribution.py::-20`` exists to catch.

    Raises ``ImportError`` when the manifest is absent — which is the normal state inside a
    built distribution. Callers that must survive that (the dogfood proof generator) go
    through :func:`measure_validation_corpus`, which converts absence into a RECORDED reason
    rather than a crash or, worse, a fabricated zero.
    """
    if _CORPUS_DIR.is_dir() and str(_CORPUS_DIR) not in sys.path:
        sys.path.insert(0, str(_CORPUS_DIR))
    import _manifest  # type: ignore[import-not-found]

    return _manifest


__all__ = [
    "MatchKey",
    "CartridgePrecisionRow",
    "PrecisionResult",
    "ValidationCorpusMeasurement",
    "finding_match_key",
    "gate_is_provisional",
    "golden_match_key",
    "compute_precision",
    "corpus_manifest_module",
    "measure_validation_corpus",
    "precision_fraction",
    "precision_gate_status_for",
    "ratio_string",
    "registry_module",
    "PRECISION_GATE_THRESHOLD",
    "UNEVALUABLE_EMPTY_DENOMINATOR",
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
    #: Story 13.2 / AC1b — whether the precision DENOMINATOR (TP + FP) was non-empty.
    #: ``False`` means this run measured NOTHING: no finding entered the denominator, so
    #: there is no 80% result to compare against a threshold. ``precision`` still carries
    #: the pre-13.2 ``Fraction(1, 1)`` "no false positive emitted" convention for callers
    #: that read it, but that value is NOT a measurement when this flag is ``False`` —
    #: read :attr:`precision_or_none` instead, and note that both
    #: :attr:`meets_threshold` and the gate are forced negative here.
    precision_evaluable: bool = True
    #: Story 13.2 / AC1c — whether §5's "0 blocking FP on a CLEAN repo" condition was
    #: measurable at all over the population this run folded. ``False`` means no member
    #: of the population satisfies the clean-repo predicate (empty golden key AND
    #: ``max_blocking == 0``), so ``clean_repo_fp`` is 0 BY CONSTRUCTION rather than by
    #: measurement. A condition that cannot fail is not a threshold, so it is reported
    #: NOT APPLICABLE with a reason instead of silently passing.
    clean_repo_fp_applicable: bool = True
    #: The sentence naming WHICH population the two flags above were resolved over, and
    #: — when a flag is ``False`` — why. Never hand-written at a call site.
    measurement_note: str = ""

    @property
    def precision_or_none(self) -> Fraction | None:
        """The precision as a MEASUREMENT: ``None`` when the denominator was empty.

        The honest surface (13.1 / DN-8's precedent, applied one level down): "no result"
        and "a perfect result" are different claims, and ``Fraction(1, 1)`` states the
        second. Pass this straight into :func:`precision_gate_status_for`, which already
        renders ``None`` as ``"NOT COMPUTED BY THIS RUN"`` and refuses to clear a gate on it.
        """
        return self.precision if self.precision_evaluable else None

    @property
    def meets_threshold(self) -> bool:
        """Whether the EXACT precision Fraction is >= 80% (Fraction(4, 5)) — no float.

        **Story 13.2 / AC1b:** an UNEVALUABLE run never meets the threshold. Before 13.2
        a corpus that emitted nothing at all returned ``Fraction(1, 1)`` here and passed
        — measured, on ``bc55e36``, as ``0 TP / 0 FP / 8 FN -> precision=1/1 ->
        provisional=False -> gate_status "cleared"``. An empty denominator is not an 80%
        result; it is no result.
        """
        return self.precision_evaluable and self.precision >= PRECISION_GATE_THRESHOLD


# The locked >=80%-precision externalization gate threshold, as an EXACT Fraction
# (NEVER a float). The PRD's >=80% precision gate. PUBLIC since Story 13.2 (12.6 / DN-7:
# promote, never reach through a `_`-prefixed name) because the adjudication fold in
# ``argus/precision/adjudication.py`` compares against the SAME threshold object — a
# second literal `4/5` is how two thresholds happen.
PRECISION_GATE_THRESHOLD = Fraction(4, 5)

#: The pre-13.2 private name, preserved so no existing caller breaks. An ALIAS.
_PRECISION_GATE_THRESHOLD = PRECISION_GATE_THRESHOLD


def precision_fraction(total_tp: int, total_fp: int) -> Fraction | None:
    """THE precision arithmetic — ``TP / (TP + FP)`` as an exact ``Fraction`` (AR4).

    **One implementation, two populations** (Story 13.2). The cartridge fold
    (:func:`compute_precision`) and the repository-corpus adjudication fold
    (:func:`argus.precision.adjudication.fold_adjudicated_precision`) both call this, so
    the arithmetic that gates externalization cannot drift between the corpus that
    measures recall and the corpus that measures the gate. Forking it per corpus is
    exactly what AR7 forbids and is how this project came to have two corpora.

    Returns ``None`` — **not** ``Fraction(1, 1)`` — when the denominator is empty. That
    convention (*"no false positive emitted"*) is why a corpus emitting nothing at all
    reported a cleared >=80% gate on ``bc55e36``; the caller must decide what an
    unmeasured population means rather than inheriting a flattering default.
    """
    denominator = total_tp + total_fp
    return Fraction(total_tp, denominator) if denominator else None


def gate_is_provisional(
    *,
    n: int,
    floor_n: int,
    protocol_cleared: bool,
    precision: Fraction | None,
) -> bool:
    """THE gate predicate (DN-PROVISIONAL) — one implementation, two populations.

    The gate is PROVISIONAL unless **all four** hold: the population reached the locked
    floor, the protocol's per-metric pass/fail is recorded cleared by the CALLER (never
    defaulted), a precision number was actually **computed**, and it meets the >=80%
    threshold as an exact ``Fraction``.

    The third conjunct is Story 13.2 / AC1b, and it is the one that was missing: a
    ``None`` precision — no finding in the denominator — can never clear the gate,
    because there is no measurement to clear it with.
    """
    return not (
        n >= floor_n
        and protocol_cleared
        and precision is not None
        and precision >= PRECISION_GATE_THRESHOLD
    )


def _is_clean_repo(spec: CartridgeSpec) -> bool:
    """A clean (true-negative) repo: empty golden key AND ``max_blocking == 0`` (R6).

    The ``clean_control`` row + the clean-shaped ``trap`` / ``no_crash`` rows: their
    golden key is empty and they tolerate ZERO blocking findings, so ANY blocking
    finding on them is a false positive (the FP denominator, DN-FP-DENOMINATOR).
    """
    return not spec.required_findings and spec.max_blocking == 0


def ratio_string(fraction: Fraction | None) -> str:
    """Render an exact ``Fraction`` as the committed ``"num/den"`` string (AR4, no float).

    Mirrors the LOCKED 1.1 canonical ``Fraction -> "num/den"`` encoding so the
    precision surface that crosses a byte boundary is fixed-precision + byte-stable
    (NFR-P1). ``Fraction`` is always normalized (denominator > 0, gcd-reduced).

    PUBLIC since Story 13.3 (12.6 / DN-7: *"need a helper from a ``_``-prefixed API?
    Promote it to public; never reach through"*). The gate-decision modules render the
    same ratios onto the committed decision record, and a second ``f"{num}/{den}"`` there
    is how two renderings of one number happen. ``None`` — *this run computed no number* —
    renders the SAME sentence :func:`precision_gate_status_for` already uses, so "not
    computed" and "measured zero" stay different claims on every surface.
    """
    if fraction is None:
        return "NOT COMPUTED BY THIS RUN"
    return f"{fraction.numerator}/{fraction.denominator}"


#: The pre-13.3 private name, preserved so no existing caller breaks. An ALIAS, not a
#: second implementation.
_ratio_string = ratio_string

#: The ONLY reason a run could be unevaluable when Story 13.2 wrote the sentence, kept as
#: the default of :func:`precision_gate_status_for`'s ``unevaluable_reason`` so every
#: pre-13.3 caller renders byte-identical output. It is a NAMED constant rather than an
#: inline literal because it is now one reason among several and a reader has to be able
#: to tell which one a surface is claiming.
UNEVALUABLE_EMPTY_DENOMINATOR = (
    "DENOMINATOR EMPTY — no finding entered TP+FP over this population"
)


def compute_precision(
    emitted_keys_by_cartridge: dict[str, frozenset[MatchKey]],
    *,
    registry: tuple[CartridgeSpec, ...] | None = None,
    protocol_cleared: bool = False,
    protocol_path: str = "_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md",
    population_n: int | None = None,
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

    **Story 13.2 / AC1 — three ADDITIVE corrections, every default preserving today's
    behaviour byte-for-byte** (DN-2: a contract test edited to accommodate a change has
    stopped being a contract test). All three were reproduced BY EXECUTION before they
    were fixed, and all three were independently reachable without a single adjudicated
    finding:

    - **AC1a — ``n`` counts the population that was actually folded.** ``registry=``
      injection has existed since 6.6, but ``n`` was read from the module-level
      ``populated_planted_defect_count()`` regardless: injecting a **2**-member registry
      reported ``N=7`` and a gate string saying *"cleared … N=7 labeled cartridges >=
      floor N=5"*. The count now closes over the resolved population. ``population_n``
      additionally lets a caller supply a **measured** count for a population this
      function does not itself iterate — the repository corpus, whose N is
      ``tests/corpus/_manifest.eligible_member_count()`` (13.1 / AC3a). It is for a
      MEASUREMENT, never a literal; see
      :func:`argus.precision.adjudication.validation_set_population_n`.
    - **AC1b — an empty denominator is UNEVALUABLE, never cleared.** A corpus emitting
      nothing at all (0 TP / 0 FP / 8 FN) returned ``precision=1/1``,
      ``provisional=False`` and a gate string reading *"cleared"*. It now sets
      ``precision_evaluable=False``, forces the gate provisional, and renders an
      ``"unevaluable"`` status carrying the degenerate counts.
    - **AC1c — the clean-repo blocking-FP condition names its population.**
      ``clean_repo_fp_applicable`` is ``False``, with a reason on
      ``measurement_note``, when no member of the folded population can satisfy the
      clean-repo predicate at all.
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

    # Precision = TP / (TP + FP) over FINDINGS (the OI1 lock), exact Fraction (AR4),
    # through the SINGLE arithmetic both corpora share. ``None`` means the denominator
    # was empty — AC1b: nothing was measured, so nothing can be cleared.
    measured_precision = precision_fraction(total_tp, total_fp)
    precision_evaluable = measured_precision is not None
    # The pre-13.2 "no false positive emitted" convention is PRESERVED on the
    # ``precision`` field so every existing caller reads exactly the bytes it always
    # did (NFR-P1 byte-stability), but it is now labelled: ``precision_evaluable``
    # says whether that Fraction is a measurement or a convention.
    precision = Fraction(1, 1) if measured_precision is None else measured_precision
    recall_den = total_tp + total_fn
    recall = Fraction(total_tp, recall_den) if recall_den else Fraction(1, 1)

    # AC1a — ``n`` counts the population that was ACTUALLY folded. ``registry`` is the
    # RESOLVED population by this point, so passing it explicitly yields the identical
    # number for the default (unsupplied) case and the HONEST number for an injected
    # one. Measured on ``bc55e36``: injecting a 2-member registry reported ``N=7`` and a
    # gate string reading "cleared ... N=7 labeled cartridges >= floor N=5". The count
    # is still the registry's OWN predicate — a second eligible-member count here is the
    # fork 13.1 / DN-3 refused, and would let the two disagree about N.
    n = int(population_n) if population_n is not None else (
        registry_module.populated_planted_defect_count(registry)
    )
    # DN-PROVISIONAL, through the SHARED predicate (13.2): N>=floor AND the caller
    # recorded the protocol cleared AND a precision number was COMPUTED AND it meets
    # >=80%. The harness never silently clears the gate (the OI1 over-claim ban).
    provisional = gate_is_provisional(
        n=n,
        floor_n=floor_n,
        protocol_cleared=protocol_cleared,
        precision=measured_precision,
    )

    # AC1c — §5's clean-repo blocking-FP condition must NAME the population it was
    # measured over, and say so when that population contains no clean member at all.
    # ``_is_clean_repo`` needs an empty golden key AND ``max_blocking == 0``; a
    # repository-corpus member has neither, so on that population the condition is
    # vacuously 0 for every possible input. A condition that cannot fail is not a
    # threshold, and reporting it as satisfied is the strongest kind of false green.
    clean_rows = tuple(row.cartridge_id for row in rows if row.is_clean_repo)
    clean_repo_fp_applicable = bool(clean_rows)
    notes = [
        f"clean-repo blocking-FP condition measured over {len(clean_rows)} clean member(s) "
        f"of {len(rows)} ({', '.join(clean_rows)})"
        if clean_rows
        else (
            f"clean-repo blocking-FP condition NOT APPLICABLE over this population: none "
            f"of its {len(rows)} member(s) satisfies the clean-repo predicate (empty "
            f"golden key AND max_blocking == 0), so clean_repo_fp is 0 BY CONSTRUCTION "
            f"and not by measurement"
        )
    ]
    if not precision_evaluable:
        notes.append(
            f"precision UNEVALUABLE: the denominator (TP + FP) is empty over "
            f"{len(rows)} member(s) — {total_tp} TP, {total_fp} FP, {total_fn} FN. An "
            f"empty denominator is not an 80% result; it is no result"
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
            precision=measured_precision,
            n=n,
            provisional=provisional,
            protocol_path=protocol_path,
            floor_n=floor_n,
            evaluable=precision_evaluable,
        ),
        precision_evaluable=precision_evaluable,
        clean_repo_fp_applicable=clean_repo_fp_applicable,
        measurement_note="; ".join(notes),
    )


@dataclass(frozen=True)
class ValidationCorpusMeasurement:
    """What the two corpora ACTUALLY hold, measured (Story 13.1 / AC5 — ``DF-8-5-C``).

    ``DF-8-5-C`` was filed because ``argus/dogfood/proof_run.py`` passed
    ``precision=Fraction(0, 1), n=0`` into the gate status as **literals** — arguments that
    were never a measurement of anything — and the resulting sentence was published verbatim
    into a proof artifact *about the very gate those numbers describe*. This type exists so
    that the numbers a proof artifact publishes come from the corpora rather than from a
    keyboard.

    **Two counts, because Story 13.1 decided there are two corpora (DN-1).**

    - ``validation_set_n`` — the count of ELIGIBLE members of the REPOSITORY corpus. This is
      the ``N`` the ≥80% externalization gate is measured over, because the PRD governs.
    - ``recall_cartridge_rows`` / ``recall_rule_classes`` — the planted-defect cartridge
      substrate, which measures **recall** (FR20) and does **not** gate externalization.

    Reporting the cartridge count as the gate's ``N`` would read as "floor met" (7 ≥ 5) for a
    gate the cartridges do not gate at all — a worse published statement than the ``N=0`` it
    replaced, and in the over-claiming direction rather than the understating one. So the two
    are carried separately and rendered with their roles named.

    Absence is RECORDED, never silently zeroed: inside a built distribution ``tests/`` is
    absent (``DF-9-2-A``), so the corresponding ``*_available`` flag goes ``False`` and
    ``unavailable_reasons`` says which substrate could not be consulted. A zero that means
    "not consulted" and a zero that means "measured, and it is zero" are different facts.
    """

    validation_set_n: int
    validation_set_available: bool
    recall_cartridge_rows: int
    recall_rule_classes: int
    recall_substrate_available: bool
    #: The locked OI1 floor, RESOLVED from whichever substrate answered — never restated here
    #: (DN-3: one floor, two populations). ``None`` when NEITHER substrate could be consulted,
    #: because the honest report of an unreadable floor is "unknown", not the number this
    #: module happens to remember. A caller that needs it then fails loudly rather than
    #: publishing an invented constant.
    floor_n: int | None
    unavailable_reasons: tuple[str, ...]

    @property
    def fully_measured(self) -> bool:
        """Whether BOTH corpora were consulted — i.e. every figure below is a measurement."""
        return self.validation_set_available and self.recall_substrate_available

    def corpus_note(self) -> str:
        """The rendered clause naming WHICH corpus each figure describes (never hand-written)."""
        if self.recall_substrate_available:
            recall = (
                f"the planted-defect cartridge corpus holds {self.recall_cartridge_rows} "
                f"populated rows across {self.recall_rule_classes} distinct rule classes and "
                "measures RECALL (FR20), NOT this gate"
            )
        else:
            recall = "the cartridge recall corpus was NOT CONSULTED by this run"
        if self.validation_set_available:
            corpus = (
                f"N counts ELIGIBLE members of the REPOSITORY corpus (PRD Validation Approach: "
                f"N ~ 5-10 real repositories), measured at {self.validation_set_n}"
            )
        else:
            corpus = "the repository corpus manifest was NOT CONSULTED by this run"
        return f"{corpus}; {recall}"


def measure_validation_corpus() -> ValidationCorpusMeasurement:
    """MEASURE both corpora through the declared lazy edges (Story 13.1 / AC5).

    Every field is read off the substrate; nothing here is a literal. Where a substrate is
    **absent** — the built-distribution case (``DF-9-2-A``), which raises ``ImportError`` — the
    count stays 0 AND the reason is recorded, so a downstream renderer can say "not consulted"
    instead of publishing a zero that looks like a finding. That distinction is the whole
    content of ``DF-8-5-C``.

    **Absence is not the same as breakage, and only absence is tolerated** (code-review R2). A
    substrate that exists but raises anything other than ``ImportError`` — a malformed manifest
    row, an API drift, a ``TypeError`` — is a defect in the corpus data itself, and it
    **propagates**. Reporting it as "not consulted" would convert a data-integrity failure into
    a benign note inside the very artifact this module exists to keep honest.

    **What the caller must handle:** ``floor_n`` is ``None`` when the locked floor could not be
    resolved at all. There is no honest default — the floor is the gate's own threshold — so a
    caller that needs it must fail loudly and say why. See
    :func:`argus.dogfood.proof_run.derive_gate_status`, which raises a typed error rather than
    letting a second registry lookup surface a bare ``ImportError`` from deep in the stack.
    """
    reasons: list[str] = []

    # THREE INDEPENDENT RESOLUTIONS, THREE INDEPENDENT try BLOCKS (code-review R2).
    #
    # These were originally two blocks, and the manifest block ALSO resolved the floor via
    # ``manifest.validation_floor_n()`` — which routes through ``registry_module()``. So a
    # failure of the CARTRIDGE registry was caught by the MANIFEST's handler: the result
    # reported ``validation_set_available=False`` and blamed the manifest, while
    # ``validation_set_n`` still held the real, already-measured count. ``corpus_note()`` then
    # rendered "the repository corpus manifest was NOT CONSULTED by this run" beside a number
    # that had in fact been consulted. A published figure contradicting its own provenance note
    # is precisely the ``DF-8-5-C`` failure class this module exists to close, reproduced inside
    # the fix for it. Each substrate now fails only for itself.
    #
    # ONLY ``ImportError`` means "absent". Anything else means the substrate EXISTS and is
    # BROKEN — e.g. ``CorpusMemberSpec.__post_init__`` raising ``ValueError`` on a bad manifest
    # row, which happens at import while ``VALIDATION_CORPUS`` is constructed. A bare
    # ``except Exception`` reported that as ordinary absence, silently converting a data-integrity
    # defect into a benign-looking "not consulted" note in a proof artifact. Those propagate now.
    validation_set_n = 0
    validation_set_available = True
    try:
        validation_set_n = int(corpus_manifest_module().eligible_member_count())
    except ImportError as exc:  # pragma: no cover - the built-distribution path
        validation_set_available = False
        reasons.append(f"repository-corpus manifest unavailable ({type(exc).__name__}: {exc})")

    recall_rows = 0
    recall_classes = 0
    recall_available = True
    try:
        registry = registry_module()
        recall_rows = int(registry.populated_planted_defect_count())
        recall_classes = int(registry.distinct_rule_class_count())
    except ImportError as exc:  # pragma: no cover - the built-distribution path
        recall_available = False
        reasons.append(f"cartridge registry unavailable ({type(exc).__name__}: {exc})")

    # The locked floor is resolved from the registry DIRECTLY — it is the single source (DN-3),
    # and reading it here rather than through the manifest is what removes the coupling above.
    floor_n: int | None = None
    try:
        floor_n = int(registry_module().VALIDATION_SET_FLOOR_N)
    except ImportError as exc:  # pragma: no cover - the built-distribution path
        reasons.append(f"locked floor unresolvable ({type(exc).__name__}: {exc})")

    return ValidationCorpusMeasurement(
        validation_set_n=validation_set_n,
        validation_set_available=validation_set_available,
        recall_cartridge_rows=recall_rows,
        recall_rule_classes=recall_classes,
        recall_substrate_available=recall_available,
        floor_n=floor_n,
        unavailable_reasons=tuple(reasons),
    )


def precision_gate_status_for(
    *,
    precision: Fraction | None,
    n: int,
    provisional: bool,
    protocol_path: str,
    floor_n: int | None = None,
    corpus_note: str | None = None,
    population_label: str = "labeled cartridges",
    evaluable: bool = True,
    unevaluable_reason: str | None = None,
    independence_note: str | None = None,
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

    **Story 13.1 / AC5 — two additive changes, both in the honest direction.**

    ``precision`` accepts ``None``, meaning *this run computed no precision number*. That is
    the true state of the dogfood proof generator, which audits a repository and does not run
    the replay harness at all; it previously said so by passing ``Fraction(0, 1)``, which
    renders ``precision=0/1`` — a statement that the tool's precision was measured and found to
    be zero. "Not computed" and "measured zero" are different claims and the surface now
    distinguishes them. A ``None`` precision with ``provisional=False`` RAISES: a run that
    computed no number can never report a cleared gate.

    ``corpus_note`` names WHICH corpus ``n`` counts, because after Story 13.1's DN-1 decision
    there are two and they gate different things. It is supplied already-derived (see
    :meth:`ValidationCorpusMeasurement.corpus_note`) so that no caller can hand-write it.

    **Story 13.3 — one additive change, in the honest direction, default byte-identical.**

    ``unevaluable_reason`` names WHY a run was unevaluable. The sentence used to be fixed at
    *"precision DENOMINATOR EMPTY — no finding entered TP+FP over this population"*, which was
    the only way to be unevaluable when Story 13.2 wrote it. It stopped being the only way the
    moment a human recorded a ``BORDERLINE``: the 13.3 fold over a record holding 26 TP/FP
    dispositions and 5 unterminated ``BORDERLINE`` ladders is unevaluable because it is
    **non-exhaustive**, and it rendered "DENOMINATOR EMPTY" beside a denominator of 26. That is
    the ``DF-9-2-B`` FALSE-SUBJECT class — a true status sentence carrying a false reason — on
    the surface that publishes the externalization gate. The parameter defaults to
    :data:`UNEVALUABLE_EMPTY_DENOMINATOR`, the exact prior wording, so every existing caller
    renders the bytes it always did (NFR-P1 byte-stability of the precision surface).

    ``population_label`` is the NOUN ``n`` counts. It defaults to ``"labeled cartridges"``, so
    :func:`compute_precision` — which genuinely folds the cartridge registry — renders exactly
    the bytes it always did (NFR-P1 byte-stability of the precision surface). The dogfood
    generator overrides it, because under DN-1 its ``n`` counts **repositories**, and a status
    line that reported a repository count using the word "cartridges" would be a new false
    statement introduced by the change that removed an old one.

    **Story 16.5 — one additive change, in the honest direction, default byte-identical.**

    ``independence_note`` carries WHO judged the population this figure was computed over, and
    whether they were independent of the tool's authors. It is rendered in **ALL THREE**
    branches, because the precision figure appears in all three and the whole point is that
    the two cannot be quoted apart: a note wired into the ``unevaluable`` branch alone would be
    correct today and silently wrong on the day the gate clears, which is the one day it
    matters most. The clause is **supplied already-derived and already-worded** by
    :func:`~argus.precision.gate_independence.independence_note` — this function PLACES it and
    never authors it, so there is still exactly one status renderer (AR7) and exactly one
    module that words the disclosure. It defaults to ``None``, rendering the empty string, so
    every existing caller renders the bytes it always did (NFR-P1 byte-stability of the
    precision surface) — which is what lets the same keyword be forwarded through the
    adjudication fold and §5's three arm renderers without any of them changing behaviour.

    ⛔ It is attached ONLY where the status is rendered from an adjudication record
    (DN-16-5-6). :func:`compute_precision`'s cartridge fold has golden keys rather than
    adjudicators, and ``argus/dogfood/proof_run.py`` passes ``precision=None`` and no record at
    all; a sentence about independence on either would describe a judgement that never
    happened. Both pass nothing and both are byte-identical after Story 16.5.
    """
    floor_n = registry_module().VALIDATION_SET_FLOOR_N if floor_n is None else floor_n
    if precision is None and not provisional:
        raise ValueError(
            "precision_gate_status_for(precision=None, provisional=False): this run computed "
            "NO precision number, so it cannot report a cleared gate. The >=80% gate is "
            "cleared only by the adjudication run of the validation protocol (OI1)."
        )
    if not evaluable and not provisional:
        raise ValueError(
            "precision_gate_status_for(evaluable=False, provisional=False): this run's "
            "precision denominator was EMPTY, so it measured nothing and cannot report a "
            "cleared gate. An empty denominator is not an 80% result; it is no result "
            "(Story 13.2 / AC1b)."
        )
    ratio = ratio_string(precision)
    note = "" if corpus_note is None else f" ({corpus_note})"
    # Story 16.5. ONE derivation, placed in all three branches below, so the independence
    # answer cannot be separated from the precision figure by copy-and-paste. ``None`` renders
    # the empty string and therefore the exact pre-16.5 bytes (NFR-P1).
    who = "" if independence_note is None else f"; {independence_note}"
    if not evaluable:
        return (
            f"unevaluable (Story 6.6 precision harness, Story 13.2 / AC1b; precision "
            f"{unevaluable_reason or UNEVALUABLE_EMPTY_DENOMINATOR}, so "
            f"precision={ratio} is NOT a measurement; N={n} {population_label}, floor "
            f"N={floor_n}{note}; the >=80% externalization gate is NEITHER cleared NOR "
            f"met — it is UNEVALUABLE and is recorded as such; adjudication method: "
            f"{protocol_path}{who})"
        )
    if provisional:
        return (
            f"provisional (Story 6.6 precision harness; precision={ratio} over FINDINGS "
            f"not repos; N={n} {population_label} populated, floor N={floor_n}{note}; "
            f"the >=80% externalization gate stays PROVISIONAL until N>={floor_n} "
            f"with the validation protocol applied — this number is an EARLY/PROVISIONAL "
            f"signal, NOT a cleared gate; adjudication method: {protocol_path}{who})"
        )
    return (
        f"cleared (Story 6.6 precision harness; precision={ratio} >= 4/5 over FINDINGS; "
        f"N={n} {population_label} >= floor N={floor_n}{note}; the validation "
        f"protocol's per-metric pass/fail is recorded cleared — {protocol_path}{who})"
    )
