"""Budget-ceiling config + deterministic cost-accounting tests (Story 3.1).

Verification area ArgusAgent-COST (``TC-ArgusAgent-COST-001-NN`` — a NEW area for the cost
module, continuing the per-module-area convention). Drivers: ArgusAgent-FR-21 (operator
budget ceiling), ArgusAgent-NFR-C1 (measured baseline ratio), ArgusAgent-NFR-C2 (the ceiling
the halt — Story 3.2 — enforces over; ``ceiling_reached`` exposed here),
ArgusAgent-NFR-D2 (zero-token pure fold), ArgusAgent-NFR-P1 (byte-stable + order-independent),
AR4 (no ``float``), AR7 (reuse ``BudgetGuardrails`` ``>=``-is-a-breach BY IMPORT,
no fork — the at-ceiling boundary is a breach, mirroring ``TC-COST-001-46``), AR8
(pure core), AR10 (typed ``BudgetGovernorError``), OI3 (NO hardcoded numeric
default — ``budget == 0`` → ``ceiling_credits is None``).
"""

from __future__ import annotations

import ast as _ast
import inspect
from fractions import Fraction

import pytest

from argus.cost import budget_governor
from argus.cost.budget_governor import (
    BASELINE_UNDEFINED,
    BudgetConfig,
    BudgetGovernorError,
    CostLedger,
    account_spend,
    baseline_ratio,
    budget_config_from_budget,
)
from argus.models import AuditRequest
from argus.store import canonical


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — budget-ceiling config: positive → ceiling; 0/omitted → None; NO numeric default
# ─────────────────────────────────────────────────────────────────────────────


def test_positive_budget_configures_ceiling() -> None:
    """TC-ArgusAgent-COST-001-01 — a positive budget configures an int ceiling."""
    config = budget_config_from_budget(250)
    assert config.ceiling_credits == 250
    assert isinstance(config.ceiling_credits, int)


def test_zero_budget_is_no_ceiling_first_class_none() -> None:
    """TC-ArgusAgent-COST-001-02 — budget==0 (CLI default) → ceiling_credits is None (OI3)."""
    config = budget_config_from_budget(0)
    assert config.ceiling_credits is None


def test_default_budget_config_has_no_numeric_default() -> None:
    """TC-ArgusAgent-COST-001-03 — a default BudgetConfig has NO hardcoded numeric ceiling (OI3)."""
    assert BudgetConfig().ceiling_credits is None


def test_no_magic_numeric_default_leaks_in_source() -> None:
    """TC-ArgusAgent-COST-001-04 — the module ships NO hardcoded numeric ceiling default (OI3).

    The ONLY default for ``ceiling_credits`` is ``None``. A numeric default literal
    on a ``ceiling_credits`` field (or a module-level numeric ceiling constant)
    would violate OI3 (the $X default is deferred to Story 7.1).
    """
    source = inspect.getsource(budget_governor)
    tree = _ast.parse(source)
    for node in _ast.walk(tree):
        # Pydantic field default: ceiling_credits: ... = Field(default=<numeric>)
        if isinstance(node, _ast.AnnAssign) and isinstance(node.target, _ast.Name):
            if node.target.id == "ceiling_credits" and node.value is not None:
                # The annotated assignment value is the Field(...) call; scan it for
                # a numeric default= keyword.
                for sub in _ast.walk(node.value):
                    if isinstance(sub, _ast.keyword) and sub.arg == "default":
                        assert not isinstance(
                            sub.value, _ast.Constant
                        ) or sub.value.value is None, (
                            "ceiling_credits must default to None, NOT a numeric default (OI3)"
                        )


def test_audit_request_budget_maps_through_config() -> None:
    """TC-ArgusAgent-COST-001-05 — the reserved AuditRequest.budget seam derives the config."""
    req_none = AuditRequest(repo_path="/x", commit="abc", budget=0, materiality_bar="")
    assert budget_config_from_budget(req_none.budget).ceiling_credits is None
    req_ceiling = AuditRequest(repo_path="/x", commit="abc", budget=42, materiality_bar="")
    assert budget_config_from_budget(req_ceiling.budget).ceiling_credits == 42


def test_negative_budget_rejected_by_model_ge0() -> None:
    """TC-ArgusAgent-COST-001-06 — a negative budget is a typed ValidationError (existing ge=0)."""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        AuditRequest(repo_path="/x", commit="abc", budget=-1, materiality_bar="")


def test_negative_budget_direct_call_typed_error() -> None:
    """TC-ArgusAgent-COST-001-07 — a direct negative-budget config call raises a typed error (AR10)."""
    with pytest.raises(BudgetGovernorError):
        budget_config_from_budget(-5)


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — the fold: running int total, order-independence, byte-stability,
#       the REUSED >=-is-a-breach decision (incl. the at-ceiling boundary)
# ─────────────────────────────────────────────────────────────────────────────


def test_fold_running_int_total() -> None:
    """TC-ArgusAgent-COST-001-10 — account_spend folds contributions into a running int total."""
    ledger = account_spend(
        {"files_indexed": 12, "tool_invocations": 3, "detector_passes": 9},
        config=budget_config_from_budget(0),
        build_cost_proxy=100,
    )
    assert ledger.total_credits == 24
    assert isinstance(ledger.total_credits, int)
    assert ledger.breakdown == {"files_indexed": 12, "tool_invocations": 3, "detector_passes": 9}


def test_fold_is_order_independent_and_byte_stable() -> None:
    """TC-ArgusAgent-COST-001-11 — two input orderings yield an equal model + identical bytes (NFR-P1)."""
    config = budget_config_from_budget(100)
    a = account_spend({"a": 3, "b": 7, "c": 2}, config=config, build_cost_proxy=50)
    b = account_spend({"c": 2, "a": 3, "b": 7}, config=config, build_cost_proxy=50)
    assert a == b
    assert canonical.dumps_bytes(a.to_canonical_payload()) == canonical.dumps_bytes(
        b.to_canonical_payload()
    )


def test_at_ceiling_boundary_is_a_breach_reused_from_guardrails() -> None:
    """TC-ArgusAgent-COST-001-12 — the exact at-ceiling boundary breaches (TC-COST-001-46 reuse)."""
    config = budget_config_from_budget(10)
    assert account_spend({"a": 9}, config=config, build_cost_proxy=100).ceiling_reached is False
    assert account_spend({"a": 10}, config=config, build_cost_proxy=100).ceiling_reached is True
    assert account_spend({"a": 11}, config=config, build_cost_proxy=100).ceiling_reached is True


def test_breach_decision_matches_guardrails_by_import() -> None:
    """TC-ArgusAgent-COST-001-13 — the breach matches the imported BudgetGuardrails directly (no fork)."""
    from argus.shared.budget_guardrails import BudgetGuardrails, BudgetPolicy

    ceiling = 100
    for total in (0, 50, 99, 100, 101, 500):
        guardrails = BudgetGuardrails(BudgetPolicy(max_worker_credits=ceiling))
        expected_reached = not guardrails.evaluate_worker_spend(total)["within_budget"]
        actual = account_spend(
            {"a": total}, config=budget_config_from_budget(ceiling), build_cost_proxy=1000
        ).ceiling_reached
        assert actual is expected_reached


def test_no_ceiling_admits_everything() -> None:
    """TC-ArgusAgent-COST-001-14 — no ceiling → ceiling_reached deterministically False (admit all)."""
    ledger = account_spend(
        {"a": 10**9}, config=budget_config_from_budget(0), build_cost_proxy=10
    )
    assert ledger.ceiling_credits is None
    assert ledger.ceiling_reached is False
    assert ledger.total_credits == 10**9


def test_empty_contributions_is_zero_total() -> None:
    """TC-ArgusAgent-COST-001-15 — an empty contributions map folds to total 0 (total-safe)."""
    ledger = account_spend({}, config=budget_config_from_budget(5), build_cost_proxy=10)
    assert ledger.total_credits == 0
    assert ledger.ceiling_reached is False
    assert ledger.breakdown == {}


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — the frozen CostLedger contract: no-float, ceiling_reached exposed
# ─────────────────────────────────────────────────────────────────────────────


def test_cost_ledger_is_frozen() -> None:
    """TC-ArgusAgent-COST-001-20 — CostLedger is frozen (extra forbidden)."""
    ledger = account_spend({"a": 1}, config=budget_config_from_budget(0), build_cost_proxy=1)
    with pytest.raises(Exception):
        ledger.total_credits = 99  # type: ignore[misc]
    with pytest.raises(Exception):
        CostLedger(
            total_credits=1,
            ceiling_reached=False,
            baseline_ratio=Fraction(1, 1),
            unknown="x",  # type: ignore[call-arg]
        )


def test_ceiling_reached_exposed_true_at_over_false_below_and_none() -> None:
    """TC-ArgusAgent-COST-001-21 — ceiling_reached True at/over, False below + False when no ceiling."""
    cfg = budget_config_from_budget(10)
    assert account_spend({"a": 5}, config=cfg, build_cost_proxy=10).ceiling_reached is False
    assert account_spend({"a": 10}, config=cfg, build_cost_proxy=10).ceiling_reached is True
    assert account_spend({"a": 15}, config=cfg, build_cost_proxy=10).ceiling_reached is True
    no_ceiling = budget_config_from_budget(0)
    assert account_spend({"a": 15}, config=no_ceiling, build_cost_proxy=10).ceiling_reached is False


def test_cost_ledger_no_float_anywhere() -> None:
    """TC-ArgusAgent-COST-001-22 — no field is a float; the payload serializes (no float, AR4)."""
    ledger = account_spend({"a": 3}, config=budget_config_from_budget(10), build_cost_proxy=7)
    for value in ledger.model_dump().values():
        assert not isinstance(value, float)
    # The canonical serializer rejects float — a clean serialize proves no float leaf.
    canonical.dumps_bytes(ledger.to_canonical_payload())


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — the NFR-C1 baseline Fraction: measured, deterministic, proxy-0 total-safe
# ─────────────────────────────────────────────────────────────────────────────


def test_baseline_ratio_is_exact_reduced_fraction() -> None:
    """TC-ArgusAgent-COST-001-30 — the baseline is an exact reduced Fraction (never float)."""
    ledger = account_spend({"a": 15}, config=budget_config_from_budget(0), build_cost_proxy=200)
    assert ledger.baseline_ratio == Fraction(3, 40)
    assert isinstance(ledger.baseline_ratio, Fraction)


def test_baseline_ratio_helper_reduced() -> None:
    """TC-ArgusAgent-COST-001-31 — baseline_ratio reduces (10/100 → 1/10) and is exact."""
    assert baseline_ratio(10, 100) == Fraction(1, 10)


def test_baseline_ratio_proxy_zero_is_total_safe_marker() -> None:
    """TC-ArgusAgent-COST-001-32 — proxy==0 returns the undefined marker, NO divide-by-zero."""
    assert baseline_ratio(5, 0) == BASELINE_UNDEFINED
    ledger = account_spend({"a": 5}, config=budget_config_from_budget(0), build_cost_proxy=0)
    assert ledger.baseline_ratio == BASELINE_UNDEFINED


def test_baseline_ratio_deterministic_same_inputs() -> None:
    """TC-ArgusAgent-COST-001-33 — identical inputs → identical baseline (NFR-P1)."""
    a = account_spend({"a": 7}, config=budget_config_from_budget(0), build_cost_proxy=11)
    b = account_spend({"a": 7}, config=budget_config_from_budget(0), build_cost_proxy=11)
    assert a.baseline_ratio == b.baseline_ratio == Fraction(7, 11)


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — purity / typed-error / single serializer / FastAPI-free import
# ─────────────────────────────────────────────────────────────────────────────


def test_module_is_pure_no_io_clock_uuid_random() -> None:
    """TC-ArgusAgent-COST-001-40 — AST scan: the module performs no I/O/clock/uuid/random (AR8)."""
    source = inspect.getsource(budget_governor)
    tree = _ast.parse(source)
    forbidden_attr = {
        "now", "utcnow", "time", "monotonic", "uuid1", "uuid4", "getpid", "open",
        "random", "randint", "choice", "read_text", "write_bytes", "read_bytes",
    }
    forbidden_call_names = {"open", "print", "input"}
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Attribute) and node.attr in forbidden_attr:
            raise AssertionError(f"forbidden attribute use: .{node.attr}")
        if isinstance(node, _ast.Call) and isinstance(node.func, _ast.Name):
            assert node.func.id not in forbidden_call_names, f"forbidden call: {node.func.id}"
        if isinstance(node, (_ast.Import, _ast.ImportFrom)):
            mod = getattr(node, "module", None) or ""
            names = [a.name for a in node.names]
            for banned in ("os", "time", "datetime", "uuid", "random", "pathlib"):
                assert banned != mod and banned not in names, f"forbidden import: {banned}"


def test_float_contribution_raises_typed_error() -> None:
    """TC-ArgusAgent-COST-001-41 — a float contribution raises BudgetGovernorError (AR4/AR10)."""
    with pytest.raises(BudgetGovernorError):
        account_spend({"a": 1.5}, config=budget_config_from_budget(0), build_cost_proxy=10)  # type: ignore[dict-item]


def test_negative_contribution_raises_typed_error() -> None:
    """TC-ArgusAgent-COST-001-42 — a negative credit raises BudgetGovernorError (AR10)."""
    with pytest.raises(BudgetGovernorError):
        account_spend({"a": -3}, config=budget_config_from_budget(0), build_cost_proxy=10)


def test_bool_contribution_rejected() -> None:
    """TC-ArgusAgent-COST-001-43 — a bool credit is rejected (a flag is not a credit, AR4)."""
    with pytest.raises(BudgetGovernorError):
        account_spend({"a": True}, config=budget_config_from_budget(0), build_cost_proxy=10)  # type: ignore[dict-item]


def test_non_mapping_contributions_rejected() -> None:
    """TC-ArgusAgent-COST-001-44 — a non-mapping contributions arg raises a typed error (AR10)."""
    with pytest.raises(BudgetGovernorError):
        account_spend([("a", 1)], config=budget_config_from_budget(0), build_cost_proxy=10)  # type: ignore[arg-type]


def test_non_str_axis_rejected() -> None:
    """TC-ArgusAgent-COST-001-45 — a non-str contribution axis raises a typed error (AR10)."""
    with pytest.raises(BudgetGovernorError):
        account_spend({1: 5}, config=budget_config_from_budget(0), build_cost_proxy=10)  # type: ignore[dict-item]


def test_float_build_cost_proxy_rejected() -> None:
    """TC-ArgusAgent-COST-001-46 — a float build-cost proxy is rejected (AR4)."""
    with pytest.raises(BudgetGovernorError):
        baseline_ratio(5, 10.0)  # type: ignore[arg-type]


# ─────────────────────────────────────────────────────────────────────────────
# AI-E1-1 — no source / secret / absolute-host-path byte in the persisted snapshot
# ─────────────────────────────────────────────────────────────────────────────


def test_snapshot_payload_carries_no_secret_or_abs_path() -> None:
    """TC-ArgusAgent-COST-001-50 — the cost payload carries only int/Fraction/bool/str provenance.

    The persisted snapshot must NEVER carry an absolute host path, source bytes, or
    a secret (NFR-S1). The payload keys are a closed, audited set; their values are
    all int/str/bool/Fraction-string. A planted secret/abs-path sentinel must be
    ABSENT from the serialized bytes.
    """
    ledger = account_spend(
        {"files_indexed": 3, "detector_passes": 9},
        config=budget_config_from_budget(100),
        build_cost_proxy=120,
    )
    payload = ledger.to_canonical_payload()
    assert set(payload.keys()) == {
        "schema_version",
        "total_credits",
        "ceiling_credits",
        "ceiling_reached",
        "breakdown",
        "baseline_ratio",
    }
    raw = canonical.dumps_bytes(payload)
    for sentinel in (b"/home/", b"/Users/", b"C:\\", b"PLANTED_SECRET", b".py"):
        assert sentinel not in raw, f"sentinel {sentinel!r} leaked into the cost snapshot"
