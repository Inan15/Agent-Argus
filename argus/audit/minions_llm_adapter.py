"""The thin IMPURE Minions-orchestrator adapter implementing ``LLMDispatchPort``.

Drivers: ArgusAgent-AR7 (reuse-by-import — the adapter HOLDS an
``LLMProviderOrchestrator`` and CALLS ``execute_llm``; it NEVER imports
``minions_core.api.* / services.api_app / app_factory / api_server``),
ArgusAgent-AR5 (captures the model checkpoint from the API response — ``LLMResponse.model``,
the dispatch-actual id, NOT a config string), ArgusAgent-AR10 (the full no-crash matrix
→ a typed outcome, NEVER an uncaught raise out of ``dispatch(...)``),
ArgusAgent-NFR-S1 (no prompt/response/secret bytes enter the ``LLMRecording`` or the
error — metadata + declared structured output only), ArgusAgent-AR8 (the impure shell;
the PURE seam is ``ports`` + ``deep_audit``), ArgusAgent-NFR-M1 (≤1200-line files).

Verification area ArgusAgent-AUDIT (TC-ArgusAgent-AUDIT-001-NN).

No fork (§3.3 / AR7) — PARTIAL reuse, narrated precisely
--------------------------------------------------------
This adapter HOLDS an injected ``LLMProviderOrchestrator`` and CALLS its
``execute_llm`` — it INHERITS the fallback chain, the circuit breaker, and the
cost attribution (which feeds ArgusAgent cost governance + honest degradation for
free). It does NOT reimplement routing/retry/breaker. The adapter is THIN: it
maps ArgusAgent's ``LLMDispatchInput`` → the orchestrator's
``RuntimeDispatchRequest``/``LLMRequest``, invokes ``execute_llm``, maps the
``RuntimeDispatchResult`` → ArgusAgent's frozen ``LLMRecording``, and CAPTURES the
dispatch-actual model id from the result's per-call provenance.

The no-crash matrix (AR10 — the headline Epic-6 risk surface)
-------------------------------------------------------------
``execute_llm`` raises ``RuntimeError("all-providers-unavailable")`` on
chain-exhaustion → caught + mapped to ``LLMDispatchError``. A budget halt returns
``RuntimeDispatchResult(budget_exceeded=True, ...)`` → mapped to
``LLMDispatchError``. A transport timeout / any other ``Exception`` out of
``execute_llm`` → mapped to ``LLMDispatchError``. A malformed/empty result (no
worker results, or no captured model id) → ``LLMDispatchError``. A captured
checkpoint that DRIFTS from ``req.pinned_model_checkpoint`` →
``CheckpointDriftError``. There is a NAMED typed catch set — no bare
``except: pass`` — and no response byte ever enters the error message.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from argus.audit.ports import (
    CheckpointDriftError,
    LLMDispatchError,
    LLMDispatchInput,
    LLMRecording,
)
try:
    from minions_core.providers.base import (
        LLMRequest,
        RuntimeDispatchRequest,
        RuntimeDispatchResult,
        provider_max_tokens,
    )
    from minions_core.orchestration.worker_agent_pool import WorkerAgentResult, WorkerTier
    MINIONS_CORE_AVAILABLE = True
except ImportError:
    MINIONS_CORE_AVAILABLE = False
    LLMRequest = Any  # type: ignore
    RuntimeDispatchRequest = Any  # type: ignore
    RuntimeDispatchResult = Any  # type: ignore
    WorkerAgentResult = Any  # type: ignore
    WorkerTier = Any  # type: ignore


__all__ = ["MinionsLLMAdapter"]

_EXHAUSTION_MESSAGE = "all-providers-unavailable"


def _resolve_tier(tier_hint: str) -> WorkerTier:
    """Resolve a string tier hint to a ``WorkerTier`` (STANDARD fallback)."""
    try:
        return WorkerTier(str(tier_hint).lower())
    except ValueError:
        return WorkerTier.STANDARD


def _credits_to_str(credits: Any) -> str:
    """Render a credits value as a frozen exact-numeric string (AR4 — no float).

    ``execute_llm`` reports ``total_credits`` as a float; ArgusAgent's recording is
    float-free so the single serializer can derive a stable key. The float is
    rounded to a fixed 4-place ``Fraction`` (the same 4-place precision the
    Minions cost path rounds to) so the rendered string is byte-stable.
    """
    try:
        as_fraction = Fraction(round(float(credits or 0.0), 4)).limit_denominator(10_000)
    except (TypeError, ValueError):
        return "0"
    return str(as_fraction)


class MinionsLLMAdapter:
    """``LLMDispatchPort`` over a reused ``LLMProviderOrchestrator`` (AR7/AR5).

    Holds the injected orchestrator and the dispatching provider id + tier model.
    Thin: DTO-mapping + checkpoint capture only (§3.3 no-fork).
    """

    def __init__(
        self,
        *,
        orchestrator: Any,
        provider_id: str,
        temperature: float = 0.2,
    ) -> None:
        self._orchestrator = orchestrator
        self._provider_id = provider_id
        self._temperature = temperature

    def dispatch(self, req: LLMDispatchInput) -> LLMRecording:
        """Dispatch one request → a frozen ``LLMRecording`` (never raises uncaught).

        Maps ``req`` → ``RuntimeDispatchRequest``/``LLMRequest``, calls
        ``execute_llm``, maps the result → ``LLMRecording``, captures the
        dispatch-actual model id. Every declared failure mode degrades to a
        typed ``LLMDispatchError`` / ``CheckpointDriftError`` (AR10).
        """
        tier = _resolve_tier(req.tier)
        dispatch_request = self._build_request(req, tier)

        try:
            result = self._orchestrator.execute_llm(dispatch_request)
        except RuntimeError as exc:
            # Chain exhaustion (the documented terminal raise) + any other
            # RuntimeError out of the orchestrator (transport failure surfaced
            # as RuntimeError). NFR-S1: only the structured message, no bytes.
            message = str(exc)
            reason = "provider-chain-exhausted" if _EXHAUSTION_MESSAGE in message else "transport-error"
            raise LLMDispatchError(
                f"llm-dispatch-failed:reason={reason}:provider={self._provider_id}"
            ) from exc
        except Exception as exc:  # noqa: BLE001 — the AR10 no-crash floor.
            # A transport timeout / any unexpected provider-side exception →
            # typed outcome, never propagated raw out of the seam.
            raise LLMDispatchError(
                f"llm-dispatch-failed:reason=transport-error:provider={self._provider_id}"
            ) from exc

        return self._map_result(req, result)

    def _build_request(self, req: LLMDispatchInput, tier: WorkerTier) -> RuntimeDispatchRequest:
        """Map ArgusAgent's ``LLMDispatchInput`` → the orchestrator's request type."""
        llm_request = LLMRequest(
            prompt="",  # NFR-S1: the deep prompt is assembled downstream; no source bytes carried here.
            model="",
            max_tokens=provider_max_tokens(self._provider_id, tier),
            temperature=self._temperature,
            tier=tier,
            run_id=req.run_id,
        )

        def _execute_subtask(_subtask: Any, _tier: WorkerTier) -> WorkerAgentResult:  # pragma: no cover - 6.2 wires the live path
            raise RuntimeError("argus-deep-execute-subtask-not-wired (6.2)")

        return RuntimeDispatchRequest(
            provider_id=self._provider_id,
            subtasks=[],
            worker_config=self._orchestrator_worker_config(tier),
            execute_subtask=_execute_subtask,
            llm_request=llm_request,
        )

    @staticmethod
    def _orchestrator_worker_config(tier: WorkerTier) -> Any:
        from minions_core.orchestration.worker_agent_pool import WorkerAgentConfig

        return WorkerAgentConfig(tier=tier)

    def _map_result(self, req: LLMDispatchInput, result: RuntimeDispatchResult) -> LLMRecording:
        """Map a ``RuntimeDispatchResult`` → a frozen ``LLMRecording`` (AR5)."""
        if getattr(result, "budget_exceeded", False):
            raise LLMDispatchError(
                f"llm-dispatch-failed:reason=budget-halt:provider={self._provider_id}"
            )

        worker_results = list(getattr(result, "worker_results", []) or [])
        if not worker_results:
            raise LLMDispatchError(
                f"llm-dispatch-failed:reason=malformed-response:provider={self._provider_id}"
            )

        first = worker_results[0]
        metadata = getattr(first, "llm_metadata", None)
        captured_model = str(getattr(metadata, "model_id", "") or "")
        if not captured_model:
            raise LLMDispatchError(
                f"llm-dispatch-failed:reason=malformed-response:provider={self._provider_id}"
            )

        if req.pinned_model_checkpoint and captured_model != req.pinned_model_checkpoint:
            raise CheckpointDriftError(
                pinned=req.pinned_model_checkpoint, captured=captured_model
            )

        provider_id = str(getattr(metadata, "provider_id", "") or getattr(result, "provider_id", "") or self._provider_id)
        finish_reason = str((getattr(first, "model_metadata", {}) or {}).get("finish_reason", ""))

        return LLMRecording(
            model_checkpoint=captured_model,
            prompt_template_version=req.prompt_template_version,
            provider_id=provider_id,
            input_tokens=max(0, int(getattr(metadata, "prompt_tokens", 0) or 0)),
            output_tokens=max(0, int(getattr(metadata, "completion_tokens", 0) or 0)),
            credits_used=_credits_to_str(getattr(result, "total_credits", 0.0)),
            finish_reason=finish_reason,
            structured_output=(),
        )
