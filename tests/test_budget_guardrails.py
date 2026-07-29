"""Unit tests for BudgetGuardrails and CostAttributionEngine (argus/shared/budget_guardrails.py)."""

from __future__ import annotations

import pytest

from argus.shared.budget_guardrails import (
    BudgetGuardrails,
    BudgetPolicy,
    CostAttributionEngine,
)


def test_budget_policy_defaults() -> None:
    policy = BudgetPolicy()
    assert policy.max_token_usage == 100000.0
    assert policy.max_runtime_cost == 100.0
    assert policy.max_tool_executions == 200.0
    assert policy.max_worker_credits == 1000.0
    assert policy.alert_threshold_pct == 0.8


def test_budget_guardrails_evaluate_ok_and_throttle() -> None:
    guard = BudgetGuardrails()
    
    # OK state
    res_ok = guard.evaluate(token_usage=1000.0, runtime_cost=1.0, tool_executions=5.0)
    assert res_ok["within_budget"]
    assert res_ok["action"] == "ok"
    assert res_ok["breaches"] == []

    # Throttle state (token usage at 85% threshold)
    res_throttle = guard.evaluate(token_usage=85000.0, runtime_cost=1.0, tool_executions=5.0)
    assert res_throttle["within_budget"]
    assert res_throttle["action"] == "throttle"

    # Halt state (exceeds max_token_usage)
    res_halt = guard.evaluate(token_usage=100000.0, runtime_cost=1.0, tool_executions=5.0)
    assert not res_halt["within_budget"]
    assert res_halt["action"] == "halt"
    assert "token_usage" in res_halt["breaches"]


def test_budget_guardrails_evaluate_pod() -> None:
    policy = BudgetPolicy(pod_budget={"pod-1": {"max_token_usage": 50.0}})
    guard = BudgetGuardrails(policy)

    res1 = guard.evaluate_pod("pod-1", token_usage=30.0, runtime_cost=1.0, tool_executions=2.0)
    assert res1["within_budget"]
    assert res1["accumulated_token_usage"] == 30.0

    res2 = guard.evaluate_pod("pod-1", token_usage=25.0, runtime_cost=1.0, tool_executions=2.0)
    assert not res2["within_budget"]
    assert "token_usage" in res2["breaches"]
    assert res2["accumulated_token_usage"] == 55.0


def test_budget_guardrails_enforce_and_alerts() -> None:
    guard = BudgetGuardrails()
    eval_ok = guard.evaluate(10.0, 1.0, 1.0)
    guard.enforce(eval_ok)
    assert len(guard.alert_log) == 0

    eval_throttle = guard.evaluate(85000.0, 1.0, 1.0)
    guard.enforce(eval_throttle)
    assert len(guard.alert_log) == 1
    assert guard.alert_log[0]["action"] == "throttle"

    eval_halt = guard.evaluate(100000.0, 1.0, 1.0)
    with pytest.raises(PermissionError, match="Budget threshold exceeded"):
        guard.enforce(eval_halt)
    assert len(guard.alert_log) == 2


def test_budget_guardrails_worker_spend() -> None:
    guard = BudgetGuardrails(BudgetPolicy(max_worker_credits=100.0))
    res_ok = guard.evaluate_worker_spend(50.0)
    assert res_ok["within_budget"]
    assert res_ok["overage"] == 0.0
    guard.enforce_worker_spend(res_ok)

    res_breach = guard.evaluate_worker_spend(100.0)
    assert not res_breach["within_budget"]
    with pytest.raises(PermissionError, match="Worker pool credit ceiling exceeded"):
        guard.enforce_worker_spend(res_breach)


def test_budget_guardrails_evaluate_preflight() -> None:
    guard = BudgetGuardrails(BudgetPolicy(max_worker_credits=100.0))
    admit_res = guard.evaluate_preflight(estimate_total=80.0)
    assert admit_res["admitted"]
    assert admit_res["action"] == "admit"

    reject_res = guard.evaluate_preflight(estimate_total=120.0)
    assert not reject_res["admitted"]
    assert reject_res["action"] == "reject"
    assert reject_res["overage"] == 20.0


def test_cost_attribution_engine() -> None:
    engine = CostAttributionEngine()
    engine.record_workflow_cost(
        run_id="run-1",
        workflow_id="wf-audit",
        release_id="rel-1.0",
        metrics={"token_usage": 1000.0, "runtime_cost": 0.5, "tool_executions": 10.0},
    )
    engine.record_workflow_cost(
        run_id="run-2",
        workflow_id="wf-audit",
        release_id="rel-1.0",
        metrics={"token_usage": 1500.0, "runtime_cost": 0.8, "tool_executions": 15.0},
    )

    wf_report = engine.generate_workflow_report("wf-audit")
    assert wf_report["workflow_id"] == "wf-audit"
    assert wf_report["run_count"] == 2
    assert wf_report["total_token_usage"] == 2500.0
    assert wf_report["total_runtime_cost"] == 1.3
    assert wf_report["total_tool_executions"] == 25.0

    rel_report = engine.generate_release_report("rel-1.0")
    assert rel_report["release_id"] == "rel-1.0"
    assert len(rel_report["workflows"]) == 1
    assert rel_report["total_token_usage"] == 2500.0
