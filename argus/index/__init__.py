"""ArgusAgent AST / code-graph index sub-package (IMPURE shell).

Drivers: ArgusAgent-FR-7 (Python AST grounding — this story builds the substrate),
AR1 (the sanctioned ``tree-sitter`` / ``tree-sitter-python`` toolchain; the
resolved grammar version is recorded for the Epic-5 / AR5 determinism cache key),
AR8 (pure/impure separation — ``index/`` is the impure shell that runs the
parser; the index DATA models are frozen pure contracts), ArgusAgent-NFR-P2
(stack-agnostic by construction — non-Python / unparseable files route to the
``claim_emitted`` proxy via the ``ast_eligible`` seam, with NO language
conditional in ``ledger``/``verdict``).

Modules:
- :mod:`argus.index.ast_index` — the tree-sitter Python code-graph
  index (Decision B): per-file definitions + line spans + a call/reference edge
  set, the AST-eligibility routing seam, and the recorded ``grammar_version``.

``index/partitioner.py`` (repository partitioning into bounded units) is
**Story 2.4** — deliberately NOT created here (V1 operates on the single
``partition_id="root"``).
"""

from __future__ import annotations

__all__: list[str] = []
