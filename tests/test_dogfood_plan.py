"""Story 7.1 — the full-repo partition + budget-sizing plan + N=5-toward corpus test.

Verification area ArgusAgent-DOGFOOD (``TC-ArgusAgent-DOGFOOD-001-NN`` — this is the FIRST file in
that area; the index starts at 01, LOCKED here). Drivers: ArgusAgent-FR-3 (partition the repo
into bounded audit units — the full-repo Minions map, OI2), ArgusAgent-FR-21 (operator budget
ceiling — the empirically-sized ``$X``, OI3), ArgusAgent-FR-20 (defect-cartridge precision
substrate — the N=5-toward corpus growth, DF-6-6-A autonomous half), ArgusAgent-NFR-SC1
(≤40-file/15k-LOC scale envelope), ArgusAgent-NFR-C1 (baseline-cost report), ArgusAgent-NFR-D1/P1
(the plan + corpus roll-up are deterministic + byte-reproducible), ArgusAgent-NFR-S1 (no
source/secret byte in the plan / golden keys / precision result), ArgusAgent-AR4 (int credits
/ Fraction ratios — never float), ArgusAgent-AR7 (REUSE by import — no fork of the planner /
accountant / registry), ArgusAgent-NFR-M1/M2 (≤1200-line files; frozen Epic-1..6 contracts +
the 6.5 registry SHAPE unchanged — only rows appended).

The complete-the-declared-set matrix (AI-E5-1 / AI-E6-1 / AR10), each covered below:
  (1) the reproducible full-repo partition map (AC1)                → TC-...-01/02/03
  (2) the per-unit-clears-the-20%-floor scoping (AC2)               → TC-...-04
  (3) the empirically-sized ``$X`` budget plan (AC3)                → TC-...-05/06
  (4) the honest V1-no-cross-partition-seam-analysis limitation     → TC-...-07
  (5) the ≥2 new distinct-class cartridges incl. ≥1 holdout (AC5)   → TC-...-08/09/10
  (6) the provisional-gate honesty + DF-6-6-A progress note (AC6)   → TC-...-11/12
  (7) the no-crash edges + the enumeration + file-size (AC7/AC8)    → TC-...-13/14/15
Every assertion NAMES the unit / cartridge id (the AI-E4-2 no-crash leg).

THE OI1 LOCK (DN-PROVISIONAL — read twice): the ≥80%-precision gate STAYS PROVISIONAL.
Story 7.1 does the AUTONOMOUS corpus-growth half of DF-6-6-A ONLY. The human TP/FP
adjudication that clears the gate is 7.2 + a human step. ``protocol_cleared`` is NOT
flipped and the ``precision_gate_status()`` marker is NOT flipped — over-claiming a
cleared gate from a synthetic corpus is the exact failure mode this lock forbids.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402
from _registry import (  # noqa: E402
    CARTRIDGE_REGISTRY,
    VALIDATION_SET_FLOOR_N,
    distinct_rule_class_count,
    distinct_rule_classes,
    populated_planted_defect_count,
    precision_gate_status,
)

from argus.cost.budget_governor import BudgetConfig, account_spend  # noqa: E402
from argus.dogfood.partition_plan import (  # noqa: E402
    COVERAGE_FLOOR,
    DEFAULT_HARD_FILE_LIMIT,
    DEFAULT_HARD_LOC_LIMIT,
    DogfoodPlanError,
    FullRepoPlan,
    build_full_repo_plan,
    render_budget_plan_markdown,
    render_partition_plan_markdown,
    size_budget,
)
from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.precision.replay_harness import (  # noqa: E402
    compute_precision,
    finding_match_key,
)

# The committed plan artifacts (AC1/AC3 — the durable §3.4 deliverables).
_PARTITION_PLAN = (
    _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent" / "minions-dogfood-partition-plan.md"
)
_BUDGET_PLAN = (
    _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent" / "minions-dogfood-budget-plan.md"
)
_DEFERRED_WORK = (
    _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent" / "deferred-work.md"
)

# The two NEW distinct classes Story 7.1 adds (CONFIRMED-emitted by real detectors).
_NEW_CARTRIDGES = ("vacuous_heuristic_basic", "cross_partition_seam")
_NEW_CLASSES = frozenset({"vacuous_test_heuristic", "cross_partition"})

# Planted secret/source bytes that MUST NOT leak into the plan / precision surface.
_PLANTED_SECRET_BYTES: tuple[str, ...] = (
    "PLANTEDxAbCdEfGhIjKlMnOpQrStUvWxYz012345",
    "пароль_секрет_значение_PLANTED_1234567",
    "EVIDENCE_SENTINEL_zXqW7vKpLmNrTaBcDeF1234567890ABCDEF",
    "marker-only-distinctive-source-byte",
)


def _request(repo: Path) -> AuditRequest:
    return AuditRequest(repo_path=str(repo), commit="HEAD", budget=100, materiality_bar="default")


def _emitted_keys_for_corpus(tmp_path: Path) -> dict[str, frozenset[tuple[str, bool, bool]]]:
    """Stage + audit EVERY registry cartridge → its emitted-match-key set (NAMED on failure)."""
    out: dict[str, frozenset[tuple[str, bool, bool]]] = {}
    for spec in CARTRIDGE_REGISTRY:
        try:
            repo, _sha = stage_cartridge(spec.cartridge_id, tmp_path / spec.cartridge_id)
        except Exception as exc:  # noqa: BLE001 — convert to a NAMED failure (AI-E4-2)
            raise AssertionError(
                f"cartridge {spec.cartridge_id!r}: staging failed ({type(exc).__name__}: {exc})"
            ) from exc
        try:
            result = run_audit_detailed(_request(repo))
        except Exception as exc:  # noqa: BLE001 — NAMED failure, never a bare traceback
            raise AssertionError(
                f"cartridge {spec.cartridge_id!r}: audit raised {type(exc).__name__}: {exc}"
            ) from exc
        out[spec.cartridge_id] = frozenset(finding_match_key(f) for f in result.verdict.ordered_findings)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Member (1) / AC1 — the reproducible full-repo partition map
# ─────────────────────────────────────────────────────────────────────────────


def test_full_repo_plan_is_multi_partition_and_within_hard_ceiling() -> None:
    """TC-ArgusAgent-DOGFOOD-001-01 — AC1/OI2/NFR-SC1: full-repo map = MULTIPLE bounded units.

    The real Minions platform tree (~135 tracked modules) partitions into MULTIPLE
    bounded units (OI2 — NOT a single unit), each within the ≤60-file/≤25k-LOC hard
    ceiling. Produced by REUSING ``partition_repository`` (no fork). NAMED per unit.
    """
    result = build_full_repo_plan(str(_REPO_ROOT))
    partitions = result.partition_plan.partitions
    assert len(partitions) >= 2, (
        f"OI2 full-repo multi-partition expected (~70+ modules); got {len(partitions)} unit(s)"
    )
    assert result.source_file_count >= 60, (
        f"the full Minions tree should enumerate the platform modules; got {result.source_file_count}"
    )
    for partition in partitions:
        assert partition.file_count <= DEFAULT_HARD_FILE_LIMIT, (
            f"unit {partition.partition_id[:12]!r}: {partition.file_count} files > hard ceiling"
        )
        assert partition.total_loc <= DEFAULT_HARD_LOC_LIMIT, (
            f"unit {partition.partition_id[:12]!r}: {partition.total_loc} LOC > hard ceiling"
        )
    # Total + disjoint: every enumerated file lands in EXACTLY one unit.
    all_files = [f for p in partitions for f in p.work_manifest.files]
    assert len(all_files) == len(set(all_files)), "a file landed in >1 partition (not disjoint)"
    assert len(all_files) == result.source_file_count, "the partition is not total (files dropped)"


def test_full_repo_plan_is_deterministic_and_byte_reproducible() -> None:
    """TC-ArgusAgent-DOGFOOD-001-02 — AC1/NFR-D1/P1: the plan re-derives byte-identically.

    Two independent derivations over the SAME tracked content yield an identical
    partition map (same unit ids, files, LOC) AND identical rendered markdown — a
    committed generator that re-derives deterministically, NOT a hand-typed map that
    rots.
    """
    a = build_full_repo_plan(str(_REPO_ROOT))
    b = build_full_repo_plan(str(_REPO_ROOT))
    assert [p.partition_id for p in a.partition_plan.partitions] == [
        p.partition_id for p in b.partition_plan.partitions
    ]
    assert render_partition_plan_markdown(a) == render_partition_plan_markdown(b)
    assert render_budget_plan_markdown(a) == render_budget_plan_markdown(b)


def test_committed_partition_plan_artifact_exists_and_matches_live_derivation() -> None:
    """TC-ArgusAgent-DOGFOOD-001-03 — AC1: the committed partition-plan .md exists + re-derives.

    The committed artifact is the durable §3.4 deliverable AND is reproducible — the
    live derivation's map (unit count + per-unit file/LOC rows) must appear in the
    committed markdown, so the artifact cannot silently rot away from the generator.
    """
    assert _PARTITION_PLAN.exists(), f"the partition plan must exist at {_PARTITION_PLAN}"
    text = _PARTITION_PLAN.read_text(encoding="utf-8")
    result = build_full_repo_plan(str(_REPO_ROOT))
    assert f"Unit count: {len(result.partition_plan.partitions)}" in text
    for partition in result.partition_plan.partitions:
        assert partition.partition_id[:12] in text, (
            f"unit {partition.partition_id[:12]!r} missing from the committed plan (rot?)"
        )
    assert "REUSING" in text or "Reused planner" in text  # the AR7 no-fork narration


# ─────────────────────────────────────────────────────────────────────────────
# Member (2) / AC2 — every TARGETED unit clears the 20%-deep coverage floor
# ─────────────────────────────────────────────────────────────────────────────


def test_every_targeted_unit_clears_the_20pct_floor() -> None:
    """TC-ArgusAgent-DOGFOOD-001-04 — AC2/FR16: no unit lands INSUFFICIENT_COVERAGE on scale.

    Each TARGETED unit is bounded within the NFR-SC1 envelope so the V1 deterministic
    pass (which grades every file in the unit) audits 100% of the unit — clearing the
    20%-deep floor (1/5). The budget sizing records ``clears_floor`` per unit; every
    unit is targeted (none dropped), so the coverage claim is honest.
    """
    result = build_full_repo_plan(str(_REPO_ROOT))
    assert COVERAGE_FLOOR == Fraction(1, 5)
    for row in result.budget.per_unit:
        assert row.clears_floor, (
            f"unit {row.partition_id[:12]!r}: does NOT clear the 20% floor (AC2 violated)"
        )
    # Every partition has a budget row (none un-targeted / dropped).
    assert len(result.budget.per_unit) == len(result.partition_plan.partitions)


# ─────────────────────────────────────────────────────────────────────────────
# Member (3) / AC3 — the empirically-sized $X budget plan (REUSE the 3.1 accountant)
# ─────────────────────────────────────────────────────────────────────────────


def test_budget_is_sized_empirically_int_credits_never_float() -> None:
    """TC-ArgusAgent-DOGFOOD-001-05 — AC3/AR4: $X is an int-credit value covering the plan, no float.

    ``$X`` = the V1 deterministic total (folded via ``account_spend`` across all units) ×
    headroom, floored to ``int``. No float reaches the ceiling / the baseline ratio; the
    NFR-C1 baseline is a ``Fraction`` (or the total-safe marker); the run FITS under
    ``$X`` while a ceiling below the total demonstrably breaches (the 3.2 halt).
    """
    result = build_full_repo_plan(str(_REPO_ROOT))
    b = result.budget
    assert isinstance(b.total_credits, int) and not isinstance(b.total_credits, bool)
    assert isinstance(b.sized_ceiling, int) and not isinstance(b.sized_ceiling, bool)
    assert b.sized_ceiling >= b.total_credits > 0, "$X must cover the full-repo total"
    assert not isinstance(b.sized_ceiling, float)
    # The baseline ratio is a Fraction (never a float) — the audit is a bounded fraction.
    assert isinstance(b.baseline_ratio, (Fraction, str))
    assert not isinstance(b.baseline_ratio, float)
    if isinstance(b.baseline_ratio, Fraction):
        assert b.baseline_ratio < Fraction(1, 1), "the audit cost must be a bounded fraction of build cost"
    # The per-unit credits reconcile with the whole-repo total (no silent drop).
    assert sum(r.unit_credits for r in b.per_unit) == b.total_credits
    # The 3.2 halt demonstration: fits under $X, breaches below the total.
    assert b.fits_within_ceiling is True
    assert b.breaches_when_ceiling_below_total is True


def test_budget_reuses_the_31_accountant_no_fork() -> None:
    """TC-ArgusAgent-DOGFOOD-001-06 — AC3/AR7: the sizing REUSES account_spend (no forked cost model).

    Re-fold the same whole-repo total through the 3.1 ``account_spend`` under the sized
    ceiling and assert the SAME ≥-is-a-breach decision — proving the plan uses the single
    3.1 accountant, not a parallel re-derived comparison. OI3 invariant: the number lives
    in the plan artifact, and ``budget_governor.py`` keeps no hardcoded numeric default
    (``BudgetConfig()`` defaults to ``ceiling_credits is None``).
    """
    result = build_full_repo_plan(str(_REPO_ROOT))
    total = result.budget.total_credits
    sized = result.budget.sized_ceiling
    ledger_fits = account_spend(
        {"total": total},
        config=BudgetConfig(ceiling_credits=sized),
        build_cost_proxy=result.budget.build_cost_proxy,
    )
    assert ledger_fits.ceiling_reached is False
    # OI3: the module default carries NO numeric ceiling (no hardcoded $X in code).
    assert BudgetConfig().ceiling_credits is None
    # The committed budget artifact records the sized ceiling + the OI3 resolution.
    assert _BUDGET_PLAN.exists(), f"the budget plan must exist at {_BUDGET_PLAN}"
    text = _BUDGET_PLAN.read_text(encoding="utf-8")
    assert str(sized) in text
    assert "no numeric" in text.lower() or "no hardcoded" in text.lower()


# ─────────────────────────────────────────────────────────────────────────────
# Member (4) / AC4 — the honest V1-no-cross-partition-seam-analysis limitation
# ─────────────────────────────────────────────────────────────────────────────


def test_plan_states_no_cross_partition_seam_analysis() -> None:
    """TC-ArgusAgent-DOGFOOD-001-07 — AC4/OI2: the plan STATES V1 has NO seam analysis (honest scope).

    The committed partition plan must explicitly state that V1 performs NO cross-partition
    seam analysis, that the ONLY V1 mitigation is the 6.4 ``cross_partition`` Prosecutor
    cut-edge pass, and that the full seam auditor is V2 — the honest-scope keystone.
    """
    text = _PARTITION_PLAN.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "no cross-partition" in lowered and "seam analysis" in lowered
    assert "cross_partition" in text  # the 6.4 Prosecutor pass named as the V1 mitigation
    assert "v2" in lowered  # the full seam auditor is reserved V2
    # The 2.4 plan-provenance marker is the mechanized anchor (not a prose-only claim).
    assert result_seam_marker() == "v2-deferred"


def result_seam_marker() -> str:
    return build_full_repo_plan(str(_REPO_ROOT)).partition_plan.seam_analysis


# ─────────────────────────────────────────────────────────────────────────────
# Member (5) / AC5 — ≥2 new distinct-class cartridges incl. ≥1 holdout (DF-6-6-A)
# ─────────────────────────────────────────────────────────────────────────────


def test_two_new_distinct_classes_added_incl_holdout() -> None:
    """TC-ArgusAgent-DOGFOOD-001-08 — AC5/DF-6-6-A: ≥2 NEW distinct classes appended, ≥1 holdout.

    The corpus grows from 3 distinct classes toward 5: the NEW classes
    ``vacuous_test_heuristic`` + ``cross_partition`` are appended as registry ROWS
    (REUSE the frozen ``CartridgeSpec`` shape — no fork), taking the DISTINCT-class count
    to 5. At least one new cartridge is a HOLDOUT (never-tuned — the overfitting defense).
    """
    ids = {s.cartridge_id for s in CARTRIDGE_REGISTRY}
    for cid in _NEW_CARTRIDGES:
        assert cid in ids, f"new cartridge {cid!r} not appended to CARTRIDGE_REGISTRY"
    # The new classes are genuinely NOT-already-labeled (distinct from the 6.6 three).
    assert _NEW_CLASSES <= set(distinct_rule_classes())
    assert distinct_rule_class_count() == 5, (
        f"expected 5 distinct classes after growth; got {distinct_rule_class_count()} "
        f"({distinct_rule_classes()})"
    )
    # ≥1 of the new cartridges is a holdout.
    new_specs = [s for s in CARTRIDGE_REGISTRY if s.cartridge_id in _NEW_CARTRIDGES]
    assert any(s.kind == "holdout" for s in new_specs), "≥1 NEW cartridge must be a holdout (AC5)"


def test_each_new_class_produces_its_own_tp(tmp_path: Path) -> None:
    """TC-ArgusAgent-DOGFOOD-001-09 — AC5/AI-E6-1: each new class produces its OWN TP (not collapsed).

    The 6.6 ``compute_precision`` roll-up runs over the grown corpus UNCHANGED (REUSE, no
    harness edit). Each NEW distinct-class cartridge produces its OWN true positive
    (``row.tp >= 1``) — proving the class is genuinely distinct, not a duplicate collapsed
    into an existing class's count. NAMED per cartridge.
    """
    emitted = _emitted_keys_for_corpus(tmp_path)
    result = compute_precision(emitted)
    for cid in _NEW_CARTRIDGES:
        row = next(r for r in result.rows if r.cartridge_id == cid)
        assert row.tp >= 1, (
            f"cartridge {cid!r}: new-class golden key not caught (tp={row.tp}, "
            f"fn_rule_ids={row.fn_rule_ids}) — a permanent FN would mean the rule_id "
            f"is not actually emitted"
        )
        assert row.fp == 0, f"cartridge {cid!r}: unexpected false positive {row.fp_rule_ids}"


def test_red_first_collapsed_count_would_be_caught(tmp_path: Path) -> None:
    """TC-ArgusAgent-DOGFOOD-001-10 — AC5 RED-first (AI-E6-1): a collision-collapsed count is detectable.

    RED-first against a naive registry append whose new golden key DUPLICATES an existing
    class (so its TP collapses into the existing class's count, adding no distinct
    coverage). We assert the new classes are keyed on rule_ids the existing corpus did NOT
    already label, so each contributes a genuinely NEW distinct-class TP — a duplicate key
    would have left ``distinct_rule_class_count()`` unchanged.
    """
    # The 6.6 baseline had exactly THREE distinct classes; the growth adds exactly the two
    # NEW classes (no accidental duplicate that would collapse the count).
    pre_growth_classes = {"vacuous_test_ast", "hardcoded_secret", "orphan_code"}
    grown = set(distinct_rule_classes())
    assert grown == pre_growth_classes | _NEW_CLASSES, (
        f"the distinct-class set must be exactly the 3 pre-growth + the 2 NEW classes; "
        f"got {sorted(grown)}"
    )
    # Each new class is a DISTINCT key (a collision would collapse the set back to <5).
    assert len(grown) == 5


# ─────────────────────────────────────────────────────────────────────────────
# Member (6) / AC6 — the OI1 keystone: the gate STAYS PROVISIONAL + the DF-6-6-A note
# ─────────────────────────────────────────────────────────────────────────────


def test_precision_gate_stays_provisional_after_growth(tmp_path: Path) -> None:
    """TC-ArgusAgent-DOGFOOD-001-11 — AC6/OI1: the gate is PROVISIONAL; protocol_cleared NOT flipped.

    The OI1 honesty keystone: 7.1 does the AUTONOMOUS corpus-growth half of DF-6-6-A ONLY.
    ``compute_precision`` (default ``protocol_cleared=False``) reports the gate PROVISIONAL
    even though the corpus now has ≥5 populated planted-defect ROWS — the human TP/FP
    adjudication (7.2 + a human step) is what clears it. The 6.5 marker is NOT flipped.
    """
    result = compute_precision(_emitted_keys_for_corpus(tmp_path))
    assert result.provisional is True, (
        "OI1: the ≥80%-precision gate must STAY PROVISIONAL after the autonomous growth "
        "(protocol_cleared defaults False; the human adjudication is 7.2 + a human step)"
    )
    assert result.gate_status.startswith("provisional")
    assert "cleared" not in result.gate_status.split("EARLY")[0]
    # The 6.5 committed marker is untouched (still says provisional).
    assert precision_gate_status().startswith("provisional")


def test_red_first_gate_is_not_silently_flipped(tmp_path: Path) -> None:
    """TC-ArgusAgent-DOGFOOD-001-12 — AC6 RED-first: even at N>=5 the gate needs protocol_cleared.

    RED-first against a silently-flipped gate: even though ``populated_planted_defect_count``
    is now ≥5 and precision is high, the gate flips ONLY when ``protocol_cleared=True`` is
    ALSO passed (the human adjudication) AND precision ≥ 4/5. 7.1 never passes
    ``protocol_cleared=True``, so the gate stays provisional — the OI1 no-overclaim ban.
    """
    assert populated_planted_defect_count() >= VALIDATION_SET_FLOOR_N, (
        "the corpus now has ≥5 populated planted-defect rows"
    )
    emitted = _emitted_keys_for_corpus(tmp_path)
    # With protocol_cleared=False (the 7.1 default) → provisional even at N>=5 + high precision.
    stays = compute_precision(emitted, protocol_cleared=False)
    assert stays.provisional is True
    # The flip path EXISTS (protocol_cleared=True + N>=5 + precision>=4/5) — proving the
    # gate is not permanently stuck, only NOT flipped here (7.1 keeps it honest).
    flipped = compute_precision(emitted, protocol_cleared=True)
    if flipped.precision >= Fraction(4, 5):
        assert flipped.provisional is False, "the flip path must work when the human clears it"
    # But 7.1 itself does NOT flip it — the committed marker stays provisional.
    assert precision_gate_status().startswith("provisional")


def test_df_6_6_a_progress_note_recorded() -> None:
    """TC-ArgusAgent-DOGFOOD-001-13 — AC6/AI-E5-4: the DF-6-6-A progress note is filed (six CC-3 fields).

    A committed append-only DF-6-6-A progress note records the advanced AUTONOMOUS half,
    the CURRENT distinct-class count, and the still-open HUMAN adjudication half — with the
    six CC-3 fields (id / origin_story / owner / target_story|sunset_date / category /
    severity).
    """
    assert _DEFERRED_WORK.exists(), f"the deferred-work register must exist at {_DEFERRED_WORK}"
    text = _DEFERRED_WORK.read_text(encoding="utf-8")
    assert "DF-6-6-A" in text
    assert "7-1-minions-full-repo-partition-budget-sizing-plan" in text  # origin_story
    assert "epic-7-minions-dogfood-precision" in text  # target_story (human half still open)
    # The current distinct-class count is recorded honestly.
    assert "distinct" in text.lower() and "5" in text
    # The six CC-3 fields are present in the note block.
    for field in ("id:", "origin_story:", "owner:", "category:", "severity:"):
        assert field in text, f"DF-6-6-A note missing CC-3 field {field!r}"


# ─────────────────────────────────────────────────────────────────────────────
# Member (7) / AC7 / AC8 — no-crash edges + secret-containment + file-size + enumeration
# ─────────────────────────────────────────────────────────────────────────────


def test_plan_generator_no_crash_on_empty_repo(tmp_path: Path) -> None:
    """TC-ArgusAgent-DOGFOOD-001-14 — AC7/AI-E4-2: an empty repo degrades to a typed NAMED outcome.

    The plan generator over a degenerate input (a repo with no source files) degrades to a
    total-safe plan (zero partitions + a total-safe baseline) — NEVER a bare traceback /
    divide-by-zero. A malformed contribution raises the TYPED ``DogfoodPlanError``.
    """
    # Empty index + empty LOC map → zero partitions, total 0, total-safe baseline.
    from argus.index.partitioner import partition_repository

    empty_index = build_ast_index(tmp_path, (), partition_id="root")
    empty_plan = partition_repository(empty_index, loc_by_file={})
    sizing = size_budget(empty_plan, {})
    assert sizing.total_credits == 0
    assert sizing.sized_ceiling == 0
    # A malformed contribution recipe raises the typed error (NAMED), never a bare raise.
    from argus.dogfood.partition_plan import unit_contributions

    with pytest.raises(DogfoodPlanError):
        unit_contributions(python_files=5, total_files=2)  # python > total (malformed)


def test_no_secret_or_source_bytes_in_plan_or_precision(tmp_path: Path) -> None:
    """TC-ArgusAgent-DOGFOOD-001-15 — AC8/NFR-S1: no secret/source byte in the plan or precision result.

    The plan artifacts + the precision result carry ONLY repo-relative paths + counts +
    credits + rule-id provenance — NEVER a planted secret / source value. Asserts every
    planted secret byte is ABSENT from the rendered plans + the precision result repr.
    """
    result = build_full_repo_plan(str(_REPO_ROOT))
    blob = render_partition_plan_markdown(result).encode("utf-8")
    blob += render_budget_plan_markdown(result).encode("utf-8")
    precision = compute_precision(_emitted_keys_for_corpus(tmp_path))
    blob += repr(precision).encode("utf-8")
    for row in precision.rows:
        blob += repr(row).encode("utf-8")
    for secret in _PLANTED_SECRET_BYTES:
        assert secret.encode("utf-8") not in blob, (
            f"SECRET/SOURCE LEAK — {secret!r} appeared in a plan / precision surface (NFR-S1)"
        )


def test_declared_set_enumeration_and_file_size() -> None:
    """TC-ArgusAgent-DOGFOOD-001-16 — AC7/AC8/NFR-M1: the declared set is enumerated + files ≤1200 lines.

    The complete-the-declared-set discipline: this test module's docstring enumerates the
    seven declared 7.1 members, and both the generator module + this test file are ≤1200
    lines (NFR-M1). The generator module cites its drivers in the module docstring.
    """
    generator = _REPO_ROOT / "argus" / "dogfood" / "partition_plan.py"
    gen_src = generator.read_text(encoding="utf-8")
    this_src = Path(__file__).read_text(encoding="utf-8")
    assert len(gen_src.splitlines()) <= 1200
    assert len(this_src.splitlines()) <= 1200
    # The generator cites its 7.1 drivers (AC8 docstring precision — the partition +
    # budget half; the FR-20 corpus-growth driver lives in the registry + THIS module).
    for driver in ("ArgusAgent-FR-3", "ArgusAgent-FR-21", "ArgusAgent-NFR-SC1", "ArgusAgent-NFR-C1", "ArgusAgent-AR4"):
        assert driver in gen_src, f"generator module docstring missing driver {driver!r}"
    assert "ArgusAgent-FR-20" in this_src, "the corpus-growth driver ArgusAgent-FR-20 must be cited in the 7.1 test area"
    # This test module enumerates the declared members (not a prose promise that rots).
    assert "The complete-the-declared-set matrix" in this_src
    for marker in ("(1) the reproducible full-repo partition map", "(5) the ≥2 new distinct-class cartridges"):
        assert marker in this_src


def test_full_repo_plan_result_is_typed() -> None:
    """TC-ArgusAgent-DOGFOOD-001-17 — AC1: the build returns the typed FullRepoPlan contract."""
    result = build_full_repo_plan(str(_REPO_ROOT))
    assert isinstance(result, FullRepoPlan)
    assert result.commit_descriptor
    assert result.partition_plan.seam_analysis == "v2-deferred"
