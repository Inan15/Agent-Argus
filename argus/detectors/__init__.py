"""ArgusAgent defect detectors — pure scorers emitting 1.2 ``Recording`` findings.

Drivers: ArgusAgent-FR-10 (heuristic vacuous-test detector, advisory, evidence-carrying),
ArgusAgent-FR-7-subset (Tier-A vacuous-path AST subset), ArgusAgent-FR-13 (locator-or-reject),
AR8 (pure scorers; the only impure boundary is the optional ``.argus/`` persistence
routed through the Story 1.3 shell), AR10 (typed/recorded failure — no bare
``except: pass``, no ``print()`` in library code).

Sub-package shell. The detector scorers are PURE functions over (test source text
+ the Story 1.4 ``AstIndexEntry``) → flags + fixed-precision counts + 1.2
``Recording`` findings. They import NO web stack and NO LLM (zero-token, NFR-D2).

V1 members: ``base`` (the detector ``Protocol`` + the locator-required finding
builder) and ``vacuous_test`` (the heuristic assertion-density + mock-ratio scorer
AND the Tier-A vacuous-path AST subset). ``secret_scan`` is Story 2.5,
``tool_runner`` Story 2.6, ``orphan_code`` Epic 6 — do NOT add them here.
"""

from __future__ import annotations

__all__: list[str] = []
