"""Defect-cartridge registry — the committed golden expected-findings source of truth.

Verification area ArgusAgent-CARTRIDGE. Drivers: ArgusAgent-FR-20 (ArgusAgent validates its own
detectors against defect cartridges with golden expected-findings keys, asserted
in CI), ArgusAgent-FR-13 (every emitted finding carries >=1 verifiable locator), ArgusAgent-AR9
(committed / durable CI gate), ArgusAgent-AR4 (golden keys are str/bool/int sets, never
float; content-derived), ArgusAgent-NFR-M1 (<=1200-line files), ArgusAgent-NFR-M2 (frozen
Epic-1..6 contracts unchanged — this module COMPOSES them, edits none).

Why this module exists (DN-REGISTRY)
------------------------------------
Story 6.5 delivers FR20 as the precision/recall MEASUREMENT SUBSTRATE. The harness
(``test_cartridge_selfaudit.py``) must iterate the declared cartridge set
MECHANICALLY (AI-E5-2) — no hand-copied per-cartridge test bodies — and the golden
expected-findings keys must live in ONE committed, frozen place (the durable
CLAUDE.md s3.4 source of truth), not scattered across inline assertions. This module
is that place: a frozen ``CartridgeSpec`` tuple keyed by cartridge id, each row
carrying the golden key, the expected verdict/exit, a ``kind``, and the
provisional/gate-status marker. A NEW cartridge is a registry row + a ``*.py.txt``
template drop-in with NO harness-code refactor (the README additive promise; the
N=5 design).

The golden key is a SET, never source bytes (NFR-S1) and never a count (AR4 / the
OI1 "precision over findings" lock). Each member is a ``GoldenFinding`` describing
a finding the audit MUST emit (``rule_id`` + verdict-eligibility + advisory flag),
NEVER the planted secret/source value.

THE OI1 LOCK (DN-GATE-STATUS — the central honesty constraint)
--------------------------------------------------------------
Validation-set N is LOCKED at 5; the corpus is populated PHASED 3->5; precision is
measured over FINDINGS not repos; the >=80%-precision gate is PROVISIONAL below
N=5. This module computes NO precision number (that is Story 6.6). It exposes a
COMMITTED, mechanically-derived ``PRECISION_GATE_STATUS`` marker that the harness
ASSERTS — the mechanized form of "do not overclaim a precision number from too few
cartridges (honest coverage is ArgusAgent's whole thesis)." Story 6.6 flips the marker to
non-provisional only at N>=5 with sufficient findings.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "GoldenFinding",
    "CartridgeSpec",
    "CARTRIDGE_REGISTRY",
    "VALIDATION_SET_FLOOR_N",
    "populated_planted_defect_count",
    "distinct_rule_class_count",
    "distinct_rule_classes",
    "PRECISION_GATE_STATUS",
    "precision_gate_status",
]

# The locked V1 validation-set floor (OI1): the >=80%-precision gate is PROVISIONAL
# until the corpus reaches this many distinct planted-defect cartridges.
VALIDATION_SET_FLOOR_N = 5


@dataclass(frozen=True)
class GoldenFinding:
    """One expected finding in a cartridge's golden key (a SET member, never bytes).

    Matches on ``rule_id`` + the verdict-eligibility flag (``verdict_eligible`` =
    ``depth_supported is not None``) + the advisory-by-contract flag. NEVER carries a
    source/secret byte (NFR-S1) — only the detector-rule provenance the verdict folds.
    """

    rule_id: str
    verdict_eligible: bool
    advisory: bool


@dataclass(frozen=True)
class CartridgeSpec:
    """A single registry row — a cartridge's locked golden expectation.

    - ``cartridge_id`` -> ``stage_cartridge`` (a directory of ``*.py.txt`` templates).
    - ``kind`` in {planted_defect, clean_control, holdout, trap, no_crash}.
    - ``required_findings`` — the golden key: findings the audit MUST emit (a SET; the
      true-positive set). For ``clean_control`` this is empty AND ``max_blocking == 0``
      is the asserted floor.
    - ``expected_verdict`` / ``expected_exit`` — the locked verdict/exit-code outcome.
    - ``max_blocking`` — the maximum blocking-finding count tolerated (the
      false-accusation floor; ``0`` for clean controls).
    - ``first_finding_rule_id`` — when set, the FR33 ordering assertion (the blocking
      finding sorts strictly first).
    - ``non_ascii`` — the AI-E1-1 non-ASCII-path/module/value cartridge flag.
    - ``provisional`` — whether this cartridge's precision contribution is provisional
      (always True in 6.5 below N=5; 6.6 flips it).
    """

    cartridge_id: str
    kind: str
    required_findings: tuple[GoldenFinding, ...]
    expected_verdict: str
    expected_exit: int
    max_blocking: int
    first_finding_rule_id: str | None = None
    non_ascii: bool = False
    provisional: bool = True


_VACUOUS = GoldenFinding(rule_id="vacuous_test_ast", verdict_eligible=True, advisory=True)
_SECRET = GoldenFinding(rule_id="hardcoded_secret", verdict_eligible=False, advisory=True)
_ORPHAN = GoldenFinding(rule_id="orphan_code", verdict_eligible=False, advisory=True)
# ── Story 7.1 — two NEW distinct defect-rule CLASSES (DF-6-6-A autonomous half).
# Both rule_ids are CONFIRMED-emitted by the REAL detectors over a staged cartridge
# (verified by running run_audit_detailed, NOT assumed) — never a synthetic rule_id.
# Both are advisory / verdict-ineligible (depth_supported is None), so each key is
# (rule_id, verdict_eligible=False, advisory=True).
_VACUOUS_HEURISTIC = GoldenFinding(
    rule_id="vacuous_test_heuristic", verdict_eligible=False, advisory=True
)
_CROSS_PARTITION = GoldenFinding(
    rule_id="cross_partition", verdict_eligible=False, advisory=True
)


# The committed cartridge registry — DESIGNED for N=5, populated phased 3->5 (OI1).
# A NEW cartridge is appended here + a *.py.txt template directory dropped in; the
# harness needs NO code change (the README additive promise / DN-REGISTRY).
CARTRIDGE_REGISTRY: tuple[CartridgeSpec, ...] = (
    # ── (1) Golden-key true positives — the three phased planted-defect cartridges.
    CartridgeSpec(
        cartridge_id="vacuous_basic",
        kind="planted_defect",
        required_findings=(_VACUOUS,),
        expected_verdict="NOT_READY_FOR_RELEASE",
        expected_exit=2,
        max_blocking=1,
        first_finding_rule_id="vacuous_test_ast",
    ),
    CartridgeSpec(
        cartridge_id="hardcoded_secret",
        kind="planted_defect",
        # The planted secret surfaces as a REDACTED advisory finding (value absent,
        # NFR-S1). Advisory does NOT alone move the verdict to blocking.
        required_findings=(_SECRET,),
        expected_verdict="RELEASE_READY",
        expected_exit=0,
        max_blocking=0,
    ),
    CartridgeSpec(
        cartridge_id="orphan_basic",
        kind="planted_defect",
        # The planted ``unused_helper`` surfaces as the advisory ``orphan_code``
        # finding. It does NOT alone block (advisory-by-contract); the cartridge is
        # NOT_READY here purely on the deep-% gate (1 deep / 2 = 50% < 60%), with
        # zero blocking findings (the 6.3 advisory floor).
        required_findings=(_ORPHAN,),
        expected_verdict="NOT_READY_FOR_RELEASE",
        expected_exit=2,
        max_blocking=0,
    ),
    # ── (2) Clean-control true negative — the false-accusation floor (any 🔴 = fail).
    CartridgeSpec(
        cartridge_id="clean_control",
        kind="clean_control",
        required_findings=(),
        expected_verdict="RELEASE_READY",
        expected_exit=0,
        max_blocking=0,
    ),
    # ── (3) Hidden holdout — the overfitting defense (a NEW, never-tuned cartridge).
    CartridgeSpec(
        cartridge_id="holdout_vacuous",
        kind="holdout",
        required_findings=(_VACUOUS,),
        expected_verdict="NOT_READY_FOR_RELEASE",
        expected_exit=2,
        max_blocking=1,
        first_finding_rule_id="vacuous_test_ast",
    ),
    # ── (4) Citation-gaming trap — a clean-control-shaped source-sentinel surface.
    #   evidence_sentinel plants a distinctive SOURCE sentinel + a secret. A naive
    #   detector that citation-games (emits a BLOCKING finding citing a real locator
    #   while describing nothing real) would be caught by max_blocking==0; the real
    #   detectors emit only an advisory redacted-secret finding and DO NOT block.
    CartridgeSpec(
        cartridge_id="evidence_sentinel",
        kind="trap",
        required_findings=(_SECRET,),
        expected_verdict="RELEASE_READY",
        expected_exit=0,
        max_blocking=0,
    ),
    # ── (5) Non-ASCII over the corpus — AI-E1-1 (planted vacuous defect on a
    #   Cyrillic/café path). Caught by its golden key + blocks.
    CartridgeSpec(
        cartridge_id="nonascii_unicode",
        kind="planted_defect",
        required_findings=(_VACUOUS,),
        expected_verdict="NOT_READY_FOR_RELEASE",
        expected_exit=2,
        max_blocking=1,
        first_finding_rule_id="vacuous_test_ast",
        non_ascii=True,
    ),
    # ── (6) No-crash row — AI-E4-2 mechanized. tool_breadth is a breadth-tool surface
    #   with non-ASCII module paths and NO test files; its golden expectation is
    #   "degrades to a typed verdict, NEVER an uncaught crash" (AR10/NFR-R1).
    CartridgeSpec(
        cartridge_id="tool_breadth",
        kind="no_crash",
        required_findings=(),
        expected_verdict="RELEASE_READY",
        expected_exit=0,
        max_blocking=0,
        non_ascii=True,
    ),
    # ── (7) Story 7.1 — NEW distinct class #1: vacuous_test_heuristic (planted_defect).
    #   A heuristically-vacuous test that REACHES the SUT but makes NO assertion and
    #   uses NO mock, so the Tier-A AST corroboration is withheld and the finding stays
    #   HEURISTIC-ONLY / advisory (rule_id="vacuous_test_heuristic", depth_supported is
    #   None → verdict-ineligible). A DISTINCT class from the AST-corroborated
    #   vacuous_test_ast. Verified CONFIRMED-emitted over the staged cartridge via
    #   run_audit_detailed (NOT assumed). The advisory finding does NOT alone block; the
    #   cartridge is NOT_READY here on the deep-% floor gate with ZERO blocking findings.
    CartridgeSpec(
        cartridge_id="vacuous_heuristic_basic",
        kind="planted_defect",
        required_findings=(_VACUOUS_HEURISTIC,),
        expected_verdict="NOT_READY_FOR_RELEASE",
        expected_exit=2,
        max_blocking=0,
    ),
    # ── (8) Story 7.1 — NEW distinct class #2: cross_partition (holdout — the
    #   overfitting defense, a never-tuned class). A single 45-file COHESION CHAIN whose
    #   oversized component the REAL 2.4 partition_repository splits under the DEFAULT
    #   NFR-SC1 limits, producing a REAL CutEdge that the REAL 6.4 Prosecutor cut-edge
    #   pass emits as an advisory rule_id="cross_partition" finding through the
    #   UNMODIFIED run_audit_detailed pipeline (no harness change). Verified
    #   CONFIRMED-emitted over the staged cartridge (NOT assumed). Advisory /
    #   verdict-ineligible → ZERO blocking findings (the seam is recorded-not-analyzed,
    #   the honest V1 limitation). Under the harness budget (100) the 45-file chain
    #   EXHAUSTS the budget mid-run (26/45 files skipped-on-exhaustion), so the verdict
    #   is exhaustion-driven NOT_READY_FOR_RELEASE / exit 2 — the ``cross_partition``
    #   golden finding is still DETERMINISTICALLY emitted (the Prosecutor cut-edge pass
    #   folds the full partition plan's cut edges regardless of exhaustion). Verified
    #   over two clean stagings.
    CartridgeSpec(
        cartridge_id="cross_partition_seam",
        kind="holdout",
        required_findings=(_CROSS_PARTITION,),
        expected_verdict="NOT_READY_FOR_RELEASE",
        expected_exit=2,
        max_blocking=0,
    ),
)


def populated_planted_defect_count() -> int:
    """The count of labeled true-positive cartridges populated (OI1 precision-over-findings).

    Counts ``planted_defect`` + ``holdout`` rows (the labeled cartridges whose findings
    contribute to a future precision number). Clean controls, the trap, and the
    no-crash row are the true-negative / robustness denominator, not the
    planted-defect numerator. Reported (not gated-on) in ``PRECISION_GATE_STATUS``.
    """
    return sum(
        1 for spec in CARTRIDGE_REGISTRY if spec.kind in ("planted_defect", "holdout")
    )


def distinct_rule_classes() -> tuple[str, ...]:
    """The SORTED set of DISTINCT defect-rule CLASSES the labeled corpus carries (DF-6-6-A).

    Story 7.1 / DF-6-6-A honesty crux: N=5 "distinct classes" counts DISTINCT
    defect-rule CLASSES, NOT cartridge ROWS. The 6.6 corpus had 5 populated
    planted-defect ROWS but only THREE distinct classes (vacuous_test_ast ×3,
    hardcoded_secret ×1, orphan_code ×1). This helper derives the honest distinct-class
    set from the labeled (planted_defect + holdout) rows' golden-key ``rule_id``s — a
    mechanically-derived count, never a prose promise that rots. Additive-only (the
    frozen 6.5 CartridgeSpec / GoldenFinding SHAPE is unchanged).
    """
    classes: set[str] = set()
    for spec in CARTRIDGE_REGISTRY:
        if spec.kind in ("planted_defect", "holdout"):
            for gf in spec.required_findings:
                classes.add(gf.rule_id)
    return tuple(sorted(classes))


def distinct_rule_class_count() -> int:
    """The count of DISTINCT defect-rule CLASSES in the labeled corpus (DF-6-6-A / AC5).

    See :func:`distinct_rule_classes`. Story 7.1 grows this from 3 toward N=5 by adding
    the ``vacuous_test_heuristic`` + ``cross_partition`` classes (each a NOT-already-
    labeled, CONFIRMED-emitted rule class).
    """
    return len(distinct_rule_classes())


def precision_gate_status() -> str:
    """The mechanically-derived precision-gate honesty marker (DN-GATE-STATUS / OI1).

    PROVISIONAL in Story 6.5 — UNCONDITIONALLY. The OI1 honesty constraint is NOT
    merely "reached N=5 cartridges"; it is that the empirical >=80%-precision NUMBER
    has not been COMPUTED or VALIDATED. Story 6.5 builds the measurement substrate (the
    cartridge harness + golden keys + holdout + clean controls) and computes NO number;
    the precision-adjudication validation protocol + the actual figure are Story 6.6.
    So the marker stays "provisional" here regardless of the cartridge count (the count
    is reported for transparency, never used to silently flip the gate to cleared —
    that would be the over-claim this lock forbids). Story 6.6 flips it to
    non-provisional only after running the validation protocol at N>=5 with sufficient
    findings.
    """
    n = populated_planted_defect_count()
    return (
        f"provisional (Story 6.5 substrate; N={n} labeled cartridges populated, floor "
        f"N={VALIDATION_SET_FLOOR_N}; precision measured over findings not repos; NO "
        f"precision number computed here — the precision gate is computed + cleared in "
        f"Story 6.6 at N>={VALIDATION_SET_FLOOR_N})"
    )


# The committed marker constant the harness ASSERTS (DN-GATE-STATUS). Mechanically
# derived from the populated planted-defect count — not a prose promise that rots.
PRECISION_GATE_STATUS = precision_gate_status()
