"""ArgusAgent audit/ sub-package — the LLM-dispatch seam (Epic 6).

Bootstrapped by story 6.1 (the FIRST Epic-6 story). This package holds the ONE
injectable seam between ArgusAgent's pure determinism core and the non-deterministic
LLM substrate (architecture Decision E / cross-cutting #7):

- ``ports`` — the PURE-importable ``LLMDispatchPort`` Protocol + the frozen
  ``LLMDispatchInput`` / ``LLMRecording`` DTOs + the typed no-crash errors.
  Importing it pulls NO provider code and NO FastAPI.
- ``minions_llm_adapter`` — the IMPURE adapter that implements the port over a
  reused ``minions_core.providers.orchestrator.LLMProviderOrchestrator`` (the
  ONE module in ``argus.audit`` allowed to import ``providers``).
- ``deep_audit`` — the thin V1 seam that depends on the PORT TYPE, never the
  adapter (DIP). The deep AST-grounding logic is Story 6.2.

Drivers: ArgusAgent-AR7 (reuse-by-import, leaf modules only), ArgusAgent-NFR-D2 (zero-token
core / FakeDispatch), ArgusAgent-AR8 (pure/impure separation), ArgusAgent-AR9 (import
isolation), ArgusAgent-AR5 (model-checkpoint captured from the API response).
"""

__all__: list[str] = []
