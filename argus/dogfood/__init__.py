"""ArgusAgent dogfood-preparation tooling (Story 7.1 — Epic-7 capstone PLAN/sizing).

This sub-package holds the REPRODUCIBLE generators that PREPARE the Minions dogfood
proof run (Story 7.2 EXECUTES it). Story 7.1 delivers the PLAN + the sizing only —
it does NOT run the whole-repo audit, build the evidence bundle, or reproduce the
signature demo (those are 7.2).

Drivers: ArgusAgent-FR-3 (partition the repo into bounded audit units — the full-repo
Minions map), ArgusAgent-FR-21 (operator budget ceiling — the empirically-sized ``$X``),
ArgusAgent-NFR-SC1 (≤40-file/15k-LOC scale envelope), ArgusAgent-NFR-C1 (baseline-cost report),
ArgusAgent-NFR-D1/P1 (the plan is deterministic + byte-reproducible), ArgusAgent-NFR-S1 (no
source/secret bytes in the plan — only paths + counts + credits), ArgusAgent-AR4 (int
credits / Fraction ratios — never float), ArgusAgent-AR7 (REUSE by import — no fork of the
2.4 partitioner or the 3.1 accountant).

Reuse BY IMPORT, never fork (AR7 / §3.3): the plan is PRODUCED by REUSING the 2.4
``partition_repository`` planner + the 1.4 ``build_ast_index`` index + the 3.1
``account_spend`` accountant — this sub-package adds NO second partitioner, NO second
cost model, NO forked serializer.
"""

from __future__ import annotations

__all__: tuple[str, ...] = ()
