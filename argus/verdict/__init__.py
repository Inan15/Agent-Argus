"""ArgusAgent verdict sub-package — the PURE terminal fold of the determinism spine.

Drivers: ArgusAgent-FR-15 (release-readiness verdict as a PURE function of the coverage
ledger), ArgusAgent-FR-16 (gate+floor core), ArgusAgent-FR-18 (deterministic exit code +
machine-readable verdict artifact), ArgusAgent-FR-33 (verdict-impact finding ordering),
ArgusAgent-NFR-D2 (zero-LLM-token verdict), AR8 (pure/impure separation — the verdict
gate imports only ledger/finding models and never reads a file or calls
``dispatch()``).

This package holds the verdict-stage modules from ``architecture.md`` §Project
Structure:

- ``verdict_gate.py`` — Story 1.6: the PURE verdict fold + finding ordering +
  exit-code mapping + the frozen ``AuditVerdict`` result (DELIVERED HERE).
- ``negative_assurance.py`` — Epic-4 Story 4.1 (NOT built here).
- ``prosecutor.py`` — Epic-6 (NOT built here).

Resist building ahead: this story delivers ``verdict_gate.py`` only.
"""

from __future__ import annotations

__all__: list[str] = []
