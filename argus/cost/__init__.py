"""ArgusAgent cost-governance sub-package (Epic 3 — FR21/FR22/NFR-C1/NFR-C2).

Home of the deterministic, pure cost-accounting MECHANISM: the budget-ceiling
configuration contract, the ``account_spend`` fold (reusing the Minions
``cost.budget_guardrails`` ``>=``-is-a-breach hard-ceiling decision BY IMPORT —
no fork, §3.3 / AR7), the frozen ``CostLedger`` cost-report contract, and the
NFR-C1 baseline-cost ratio. See :mod:`argus.cost.budget_governor`.
"""

from __future__ import annotations

__all__: list[str] = []
