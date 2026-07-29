"""ArgusAgent governance sub-package — the HITL STOP/PROCEED escalation surface.

Story 6.7 (Epic 6, Tier-B). This package is the FR23/FR24 human-in-the-loop
governance surface: a PURE, pattern-matched STOP/PROCEED escalation gate and an
append-only, prev-hash-chained decision record. It is a RESERVED package shell —
the two production modules (:mod:`escalation` and :mod:`decision_record`) hold the
logic; this ``__init__`` carries no logic (mirroring the other ArgusAgent sub-package
shells).

Drivers: ArgusAgent-FR-23 (HITL STOP/PROCEED gate — pattern-matched, default-STOP,
time-boxed park-at-STOP), ArgusAgent-FR-24 (append-only decision record; the STOP is
logged even if the full record is deferred).

The escalation gate is a PURE zero-LLM-token recording-consumer (it imports NO
``fastapi``/``uvicorn``/``starlette`` and NO LLM dispatch surface — the FR23 lock:
the trigger is a deterministic pattern match, NEVER an LLM judgment). The decision
record REUSES the Story 1.1 canonical serializer + the content-hashed,
prev-hash-chained envelope + the Story 1.3 ``ApaaStoreWriter`` (no forked
persistence).
"""

from __future__ import annotations

__all__: list[str] = []
