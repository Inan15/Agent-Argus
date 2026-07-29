"""ArgusAgent coverage-ledger + recording sub-package (the determinism core's 2nd link).

Story 1.2 lands the PURE data substrate every later module folds over: the
fixed-enum coverage ledger (``coverage_ledger.py``) and the first-class frozen
recording schema (``recording.py``). Both are pure Pydantic v2 models + pure
functions over in-memory inputs — no I/O, no clock, no LLM, no ``uuid4`` /
``random`` (AR8). The impure ``.argus/`` write/read shell is Story 1.3; the
verdict gate that folds the ledger is Story 1.6.

Drivers: ArgusAgent-FR-5, ArgusAgent-FR-6, ArgusAgent-FR-13 (model-layer support), ArgusAgent-NFR-D2,
ArgusAgent-NFR-M2, AR8, AR10.
"""

__all__: list[str] = []
