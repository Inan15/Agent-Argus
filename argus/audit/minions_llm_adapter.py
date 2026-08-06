"""Backward-compatible Minions LLM Adapter wrapper implementing ``LLMDispatchPort``.

Delegates to ``OpenLLMAdapter`` using open-source multi-provider dispatch (LiteLLM + HTTPX).
Provides 100% backward compatibility for existing MinionsLLMAdapter invocations without
requiring the unpackaged ``minions_core`` library.
"""

from __future__ import annotations

from typing import Any

from argus.audit.open_llm_adapter import OpenLLMAdapter, credits_to_str
from argus.audit.ports import (
    CheckpointDriftError,
    LLMDispatchError,
    LLMDispatchInput,
    LLMRecording,
)

__all__ = ["MinionsLLMAdapter", "_credits_to_str"]

_credits_to_str = credits_to_str


class MinionsLLMAdapter:
    """``LLMDispatchPort`` adapter delegating to open-source multi-provider dispatch.

    Retained as a backward-compatible wrapper around ``OpenLLMAdapter``. Carries
    zero dependency on ``minions_core``.
    """

    def __init__(
        self,
        *,
        orchestrator: Any = None,
        provider_id: str = "minions-provider",
        temperature: float = 0.2,
    ) -> None:
        self._orchestrator = orchestrator
        self._provider_id = provider_id
        self._temperature = temperature
        self._delegate = OpenLLMAdapter(
            provider_id=provider_id,
            temperature=temperature,
        )

    def dispatch(self, req: LLMDispatchInput) -> LLMRecording:
        """Dispatch request via the open-source LLM adapter."""
        if self._orchestrator and hasattr(self._orchestrator, "execute_llm"):
            try:
                res = self._orchestrator.execute_llm(req)
                if isinstance(res, LLMRecording):
                    return res
            except Exception as exc:
                message = str(exc)
                reason = "provider-chain-exhausted" if "unavailable" in message else "transport-error"
                raise LLMDispatchError(
                    f"llm-dispatch-failed:reason={reason}:provider={self._provider_id}"
                ) from exc

        return self._delegate.dispatch(req)
