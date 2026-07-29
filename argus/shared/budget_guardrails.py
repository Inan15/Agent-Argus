from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List


@dataclass
class BudgetPolicy:
    max_token_usage: float = 100000.0
    max_runtime_cost: float = 100.0
    max_tool_executions: float = 200.0
    # Worker agent pool budget.  Set to 0.0 to disable worker pool usage.
    max_worker_credits: float = 1000.0
    # Optional per-pod budget overrides keyed by pod_id.
    # Each value can provide token/runtime/tool limits.
    pod_budget: Dict[str, Dict[str, float]] | None = None
    # Fraction of each limit at which a throttle alert fires before the hard halt.
    alert_threshold_pct: float = 0.8


class BudgetGuardrails:
    """FR-12 budget thresholds, throttling/halts, and attribution support.

    Cache-aware spend-basis contract (story 13-5 / CC-3; MIN-FR-COST-001.01/.03)
    ----------------------------------------------------------------------------
    Append-only note (the D3 hard-ceiling comments below are NOT rewritten).
    Three budget axes coexist; exactly ONE is cache-aware, and that is by design:

      - LLM cumulative-credit halt (CACHE-AWARE). The pre-dispatch halt check
        ``LLMProviderOrchestrator._maybe_halt_on_budget`` evaluates spend via
        ``ProviderCostAttribution.total_credits()``, which sums the discounted
        ``total_credits_used`` that ``record()`` stores. Story 13-1 made each
        cloud ``_compute_credits`` bill the vendor-reported cached input portion
        at ``cache_discount_rate(provider_id)`` BEFORE recording, so the halt
        basis is the realized, cache-discounted total transitively — a
        cache-heavy run accumulates lower credits and halts later (or not at
        all); a cache-miss run accumulates at the full base rate. The D3 ``>=``
        hard-ceiling decision semantics are unchanged; only the spend BASIS is
        the discounted total.

      - Token-volume ceiling ``max_token_usage`` (deliberately CACHE-AGNOSTIC).
        ``evaluate``/``evaluate_pod`` count tokens consumed, not credits. A
        cached input token is still a token that was sent and served — caching
        changes its PRICE, not its VOLUME — so cached tokens are NOT subtracted
        here (CC-6 honesty: a cache hit reduces credits, never the token count).

      - Worker-pool credit ceiling ``max_worker_credits`` /
        ``evaluate_worker_spend`` (deliberately CACHE-AGNOSTIC). Worker-pool
        credits come from tier-based subtask dispatch (``worker_billing``), not
        from LLM prompt-cache reads. There is no vendor cache on this axis, so
        discounting it would fabricate a saving (CC-6 violation). It stays as-is.
    """

    def __init__(self, policy: BudgetPolicy | None = None) -> None:
        self.policy = policy or BudgetPolicy()
        # Per-pod accumulated usage: pod_id -> {metric: cumulative float}
        self._pod_usage: Dict[str, Dict[str, float]] = {}
        # Alert log populated by emit_alert(); inspectable by operators and tests.
        self.alert_log: List[dict] = []

    def evaluate(self, token_usage: float, runtime_cost: float, tool_executions: float) -> dict:
        # D3 (review 2026-05-10): hard-ceiling semantic — equality is a breach.
        # Aligns with the LLM orchestrator's ``_maybe_halt_on_budget`` which
        # halts on ``cumulative >= ceiling``. The pre-D3 strict ``>`` allowed
        # one in-flight call to push usage exactly to the ceiling without
        # triggering a breach, which produced inconsistent halt behaviour
        # across the two enforcement paths.
        breaches = []
        if token_usage >= self.policy.max_token_usage:
            breaches.append("token_usage")
        if runtime_cost >= self.policy.max_runtime_cost:
            breaches.append("runtime_cost")
        if tool_executions >= self.policy.max_tool_executions:
            breaches.append("tool_executions")
        if breaches:
            action = "halt"
        else:
            threshold = self.policy.alert_threshold_pct
            near_limit = (
                token_usage >= self.policy.max_token_usage * threshold
                or runtime_cost >= self.policy.max_runtime_cost * threshold
                or tool_executions >= self.policy.max_tool_executions * threshold
            )
            action = "throttle" if near_limit else "ok"
        return {
            "within_budget": len(breaches) == 0,
            "breaches": breaches,
            "token_usage": token_usage,
            "runtime_cost": runtime_cost,
            "tool_executions": tool_executions,
            "action": action,
        }

    def evaluate_pod(self, pod_id: str, token_usage: float, runtime_cost: float, tool_executions: float) -> dict:
        """Accumulate and evaluate per-pod budget usage across sequential calls.

        Each call for a given pod_id adds the supplied metrics to that pod's running
        totals, enabling continuous budget evaluation across multiple workflow
        executions within the same pod.
        """
        acc = self._pod_usage.setdefault(
            pod_id, {"token_usage": 0.0, "runtime_cost": 0.0, "tool_executions": 0.0}
        )
        acc["token_usage"] += token_usage
        acc["runtime_cost"] += runtime_cost
        acc["tool_executions"] += tool_executions

        pod_limits = (self.policy.pod_budget or {}).get(pod_id, {})
        token_limit = float(pod_limits.get("max_token_usage", self.policy.max_token_usage))
        runtime_limit = float(pod_limits.get("max_runtime_cost", self.policy.max_runtime_cost))
        tool_limit = float(pod_limits.get("max_tool_executions", self.policy.max_tool_executions))

        # D3 (review 2026-05-10): hard-ceiling semantic — equality is a breach.
        breaches = []
        if acc["token_usage"] >= token_limit:
            breaches.append("token_usage")
        if acc["runtime_cost"] >= runtime_limit:
            breaches.append("runtime_cost")
        if acc["tool_executions"] >= tool_limit:
            breaches.append("tool_executions")
        return {
            "pod_id": pod_id,
            "within_budget": len(breaches) == 0,
            "breaches": breaches,
            "accumulated_token_usage": acc["token_usage"],
            "accumulated_runtime_cost": acc["runtime_cost"],
            "accumulated_tool_executions": acc["tool_executions"],
            "pod_limits": {
                "max_token_usage": token_limit,
                "max_runtime_cost": runtime_limit,
                "max_tool_executions": tool_limit,
            },
        }

    def emit_alert(self, evaluation: dict) -> None:
        """Record a budget breach alert to the internal alert log.

        Called automatically by enforce() for throttle and halt actions.
        Can also be invoked directly for integration with the observability pipeline.
        """
        action = evaluation.get("action", "halt")
        if action not in ("throttle", "halt"):
            return
        self.alert_log.append({
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "breaches": list(evaluation.get("breaches", [])),
            "token_usage": evaluation.get("token_usage"),
            "runtime_cost": evaluation.get("runtime_cost"),
            "tool_executions": evaluation.get("tool_executions"),
        })

    def enforce(self, evaluation: dict) -> None:
        action = evaluation.get("action", "halt" if not evaluation["within_budget"] else "ok")
        if action in ("throttle", "halt"):
            self.emit_alert(evaluation)
        if action == "halt":
            raise PermissionError(f"Budget threshold exceeded: {evaluation['breaches']}")

    def evaluate_worker_spend(self, credits_consumed: float) -> dict:
        """Evaluate whether the worker pool's credit spend is within policy.

        D3 (review 2026-05-10): hard-ceiling semantic — ``credits_consumed
        >= max_worker_credits`` is a breach. Aligns with the LLM
        orchestrator's ``_maybe_halt_on_budget`` halt condition.

        MIN-FR-COST-001 (story 20-4, TC-COST-001-46): the at-ceiling boundary is
        verified correct as written — ``within = credits_consumed < max`` already
        makes the exact equality ``credits_consumed == max`` evaluate to
        ``within=False`` (a breach), which is the D3 ``>=`` semantic. The
        gap-audit "at-ceiling escape" was a FALSE POSITIVE for the equality case;
        the full boundary (just-below within, at/above breach) is regression-
        locked by ``TestWorkerSpendCeilingBoundary``.
        """
        within = credits_consumed < self.policy.max_worker_credits
        return {
            "within_budget": within,
            "credits_consumed": credits_consumed,
            "max_worker_credits": self.policy.max_worker_credits,
            "overage": max(0.0, round(credits_consumed - self.policy.max_worker_credits, 4)),
        }

    def enforce_worker_spend(self, evaluation: dict) -> None:
        if not evaluation["within_budget"]:
            raise PermissionError(
                f"Worker pool credit ceiling exceeded: consumed {evaluation['credits_consumed']:.2f} "
                f"/ limit {evaluation['max_worker_credits']:.2f} credits"
            )

    def evaluate_preflight(self, estimate_total: float, budget: float | None = None) -> dict:
        """Admit-or-reject a not-yet-run workload by its pre-flight cost estimate.

        MIN-FR-COST-001.05 (story 21-2, E21-S2; architecture.md §11 ADR #22 —
        thin admission-control slice). This is the forward-admission decision the
        21-2 pre-dispatch gate consumes: a run whose estimated cost-tree total
        (from the pure ``preflight_estimator.estimate_run`` core, story 21-1) is
        at-or-over the configured ceiling is rejected *before* any worker
        dispatch, closing the gap that today's controls only HALT mid-run.

        Reuse, NOT fork (§3.3): the breach comparison is the SAME D3
        ``>=``-is-a-breach hard-ceiling semantic ``evaluate_worker_spend`` already
        encodes (``admitted = estimate_total < ceiling`` ⇒ the exact at-ceiling
        boundary rejects, identical to TC-COST-001-46). There is no second budget
        authority and no parallel comparison. The "approved budget" is the
        configured ``BudgetPolicy`` ceiling (``max_worker_credits`` — the
        worker-pool credit axis the credit-multiplier estimate maps onto, CLAUDE.md
        clarification commit 4d9370c); an explicit ``budget`` override is honored
        when supplied (used by tests and any future per-run ceiling).
        """
        ceiling = budget if budget is not None else self.policy.max_worker_credits
        admitted = estimate_total < ceiling
        return {
            "admitted": admitted,
            "estimate_total": estimate_total,
            "budget": ceiling,
            "overage": max(0.0, round(estimate_total - ceiling, 4)),
            "action": "admit" if admitted else "reject",
        }


class CostAttributionEngine:
    """FR-12 per-workflow and per-release cost attribution reports.

    Records cost metrics for each workflow run and generates aggregated reports
    scoped to a workflow or a release.
    """

    def __init__(self) -> None:
        self._records: List[Dict] = []

    def record_workflow_cost(
        self,
        run_id: str,
        workflow_id: str,
        release_id: str,
        metrics: Dict[str, float],
    ) -> None:
        """Record cost metrics for a single workflow run."""
        self._records.append({
            "run_id": run_id,
            "workflow_id": workflow_id,
            "release_id": release_id,
            "token_usage": float(metrics.get("token_usage", 0.0)),
            "runtime_cost": float(metrics.get("runtime_cost", 0.0)),
            "tool_executions": float(metrics.get("tool_executions", 0.0)),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        })

    def generate_workflow_report(self, workflow_id: str) -> Dict:
        """Return aggregated cost totals for all runs of a given workflow."""
        runs = [r for r in self._records if r["workflow_id"] == workflow_id]
        return {
            "workflow_id": workflow_id,
            "run_count": len(runs),
            "total_token_usage": sum(r["token_usage"] for r in runs),
            "total_runtime_cost": sum(r["runtime_cost"] for r in runs),
            "total_tool_executions": sum(r["tool_executions"] for r in runs),
        }

    def generate_release_report(self, release_id: str) -> Dict:
        """Return per-workflow breakdown and totals for all workflows in a release."""
        runs = [r for r in self._records if r["release_id"] == release_id]
        by_workflow: Dict[str, Dict] = {}
        for record in runs:
            wid = record["workflow_id"]
            entry = by_workflow.setdefault(
                wid,
                {
                    "workflow_id": wid,
                    "run_count": 0,
                    "total_token_usage": 0.0,
                    "total_runtime_cost": 0.0,
                    "total_tool_executions": 0.0,
                },
            )
            entry["run_count"] += 1
            entry["total_token_usage"] += record["token_usage"]
            entry["total_runtime_cost"] += record["runtime_cost"]
            entry["total_tool_executions"] += record["tool_executions"]
        workflows = list(by_workflow.values())
        return {
            "release_id": release_id,
            "workflows": workflows,
            "total_token_usage": sum(w["total_token_usage"] for w in workflows),
            "total_runtime_cost": sum(w["total_runtime_cost"] for w in workflows),
            "total_tool_executions": sum(w["total_tool_executions"] for w in workflows),
        }
