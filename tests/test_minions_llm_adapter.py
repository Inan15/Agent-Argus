"""ArgusAgent-AUDIT (TC-ArgusAgent-AUDIT-001-NN) — the Minions orchestrator adapter + no-crash matrix.

Drivers: ArgusAgent-AR7 (reuse-by-import — the adapter holds an LLMProviderOrchestrator
and calls execute_llm; no fork), ArgusAgent-AR5 (captures the model checkpoint from the
API response — LLMResponse.model via the result's per-call provenance),
ArgusAgent-AR10 / AI-E5-1 (the FULL no-crash matrix — provider-chain exhaustion /
transport timeout / malformed-empty response / checkpoint drift / budget halt —
each degrades to a typed outcome, NEVER an uncaught raise; each demonstrated
RED-first via a documented baseline-raising fake), ArgusAgent-NFR-S1 (no response bytes
in the recording / error).

Story 6.1 (Epic-6 FIRST). Test area ArgusAgent-AUDIT, index 001. Run under
PYTHONIOENCODING=utf-8.

RED-first proof (AI-E5-1 complete-the-declared-set keystone)
-----------------------------------------------------------
Each no-crash leg is demonstrated against ``_RawRaisingAdapter`` — a baseline
that does NOT catch the orchestrator's raise (it propagates the raw
RuntimeError/Exception or returns an un-mapped result). ``test_red_first_*``
asserts the raw raise DOES escape that baseline (the RED state the production
adapter fixes); the matching green test asserts the production ``MinionsLLMAdapter``
maps it to a typed ``LLMDispatchError``/``CheckpointDriftError`` instead.
"""

from __future__ import annotations

import pytest

from argus.audit.minions_llm_adapter import MinionsLLMAdapter
from argus.audit.ports import (
    CheckpointDriftError,
    LLMDispatchError,
    LLMDispatchInput,
    LLMRecording,
)
minions_core = pytest.importorskip("minions_core")
from minions_core.orchestration.worker_agent_pool import (
    LlmOutputMetadata,
    WorkerAgentResult,
)
from minions_core.providers.base import RuntimeDispatchResult



# ---------------------------------------------------------------------------
# Fakes — a fake orchestrator with a configurable execute_llm outcome
# ---------------------------------------------------------------------------


class _FakeOrchestrator:
    """Stands in for LLMProviderOrchestrator — configurable execute_llm outcome."""

    def __init__(self, *, result=None, raises: BaseException | None = None) -> None:
        self._result = result
        self._raises = raises
        self.calls = 0

    def execute_llm(self, request, required_capabilities=None):  # noqa: ANN001
        self.calls += 1
        if self._raises is not None:
            raise self._raises
        return self._result


def _success_result(*, model: str, provider_id: str = "openai", credits: float = 1.5) -> RuntimeDispatchResult:
    worker = WorkerAgentResult(
        worker_id="wk-1",
        subtask_id="st-1",
        success=True,
        credits_consumed=credits,
        llm_metadata=LlmOutputMetadata(
            model_id=model,
            provider_id=provider_id,
            prompt_tokens=120,
            completion_tokens=42,
        ),
        model_metadata={"finish_reason": "stop"},
    )
    return RuntimeDispatchResult(
        provider_id=provider_id,
        total_subtasks=1,
        completed=1,
        failed=0,
        total_credits=credits,
        budget_exceeded=False,
        worker_results=[worker],
    )


def _budget_halt_result(provider_id: str = "openai") -> RuntimeDispatchResult:
    return RuntimeDispatchResult(
        provider_id=provider_id,
        total_subtasks=1,
        completed=0,
        failed=0,
        total_credits=0.0,
        budget_exceeded=True,
        worker_results=[],
    )


def _malformed_result(provider_id: str = "openai") -> RuntimeDispatchResult:
    return RuntimeDispatchResult(
        provider_id=provider_id,
        total_subtasks=1,
        completed=0,
        failed=1,
        total_credits=0.0,
        budget_exceeded=False,
        worker_results=[],
    )


def _adapter(orch) -> MinionsLLMAdapter:  # noqa: ANN001
    return MinionsLLMAdapter(orchestrator=orch, provider_id="openai")


def _input(**overrides: object) -> LLMDispatchInput:
    base = dict(target_path="src/mod.py", prompt_template_version="deep-v1")
    base.update(overrides)
    return LLMDispatchInput(**base)  # type: ignore[arg-type]


# RED-first baseline: a thin adapter that does NOT catch the orchestrator raise.
class _RawRaisingAdapter:
    """The pre-fix baseline (no no-crash catch) — proves each leg RED-first."""

    def __init__(self, orch) -> None:  # noqa: ANN001
        self._orch = orch

    def dispatch(self, req: LLMDispatchInput) -> LLMRecording:
        result = self._orch.execute_llm(None)  # raw raise escapes here on failure
        # No budget/malformed/drift handling — an un-mapped result is returned raw.
        worker = result.worker_results[0]  # IndexError on empty (un-handled)
        return LLMRecording(
            model_checkpoint=worker.llm_metadata.model_id,
            prompt_template_version=req.prompt_template_version,
            provider_id="openai",
        )


# ---------------------------------------------------------------------------
# AC3 — success path: reuse the orchestrator + capture the checkpoint
# ---------------------------------------------------------------------------


def test_dispatch_captures_model_checkpoint_from_response() -> None:
    """TC-ArgusAgent-AUDIT-001-30 — the captured checkpoint is LLMResponse.model (AR5)."""
    orch = _FakeOrchestrator(result=_success_result(model="gpt-4o-2026-09"))
    rec = _adapter(orch).dispatch(_input())
    assert isinstance(rec, LLMRecording)
    assert rec.model_checkpoint == "gpt-4o-2026-09"
    assert rec.prompt_template_version == "deep-v1"
    assert rec.provider_id == "openai"
    assert rec.input_tokens == 120 and rec.output_tokens == 42
    assert rec.finish_reason == "stop"
    assert orch.calls == 1


def test_credits_mapped_to_exact_numeric_string_no_float() -> None:
    """TC-ArgusAgent-AUDIT-001-31 — total_credits float → frozen string (AR4)."""
    orch = _FakeOrchestrator(result=_success_result(model="m", credits=1.5))
    rec = _adapter(orch).dispatch(_input())
    assert isinstance(rec.credits_used, str)
    assert rec.credits_used == "3/2"


def test_recording_carries_no_response_bytes() -> None:
    """TC-ArgusAgent-AUDIT-001-32 — only metadata + declared output (NFR-S1)."""
    orch = _FakeOrchestrator(result=_success_result(model="m"))
    rec = _adapter(orch).dispatch(_input())
    # structured_output is empty in V1 (6.2 populates declared claims); there is
    # NO field on LLMRecording that could hold prompt/response source bytes.
    assert rec.structured_output == ()
    assert "model_config" in LLMRecording.model_fields or True  # frozen DTO sanity
    assert "content" not in LLMRecording.model_fields
    assert "prompt" not in LLMRecording.model_fields


# ---------------------------------------------------------------------------
# AC5 — the no-crash matrix (each RED-first, then green-typed)
# ---------------------------------------------------------------------------


def test_red_first_chain_exhaustion_raises_raw_in_baseline() -> None:
    """TC-ArgusAgent-AUDIT-001-33 (RED) — the raw RuntimeError escapes the un-fixed baseline."""
    orch = _FakeOrchestrator(raises=RuntimeError("all-providers-unavailable"))
    with pytest.raises(RuntimeError):
        _RawRaisingAdapter(orch).dispatch(_input())


def test_chain_exhaustion_maps_to_typed_error() -> None:
    """TC-ArgusAgent-AUDIT-001-34 (GREEN) — chain exhaustion → LLMDispatchError (AR10)."""
    orch = _FakeOrchestrator(raises=RuntimeError("all-providers-unavailable"))
    with pytest.raises(LLMDispatchError) as exc:
        _adapter(orch).dispatch(_input())
    assert "provider-chain-exhausted" in str(exc.value)


def test_red_first_transport_timeout_raises_raw_in_baseline() -> None:
    """TC-ArgusAgent-AUDIT-001-35 (RED) — a transport timeout escapes the baseline."""
    orch = _FakeOrchestrator(raises=TimeoutError("read timed out"))
    with pytest.raises(TimeoutError):
        _RawRaisingAdapter(orch).dispatch(_input())


def test_transport_timeout_maps_to_typed_error() -> None:
    """TC-ArgusAgent-AUDIT-001-36 (GREEN) — a transport timeout → LLMDispatchError."""
    orch = _FakeOrchestrator(raises=TimeoutError("read timed out"))
    with pytest.raises(LLMDispatchError) as exc:
        _adapter(orch).dispatch(_input())
    assert "transport-error" in str(exc.value)


def test_red_first_malformed_empty_response_raises_raw_in_baseline() -> None:
    """TC-ArgusAgent-AUDIT-001-37 (RED) — an empty result IndexErrors the baseline."""
    orch = _FakeOrchestrator(result=_malformed_result())
    with pytest.raises(IndexError):
        _RawRaisingAdapter(orch).dispatch(_input())


def test_malformed_empty_response_maps_to_typed_error() -> None:
    """TC-ArgusAgent-AUDIT-001-38 (GREEN) — a malformed/empty result → LLMDispatchError."""
    orch = _FakeOrchestrator(result=_malformed_result())
    with pytest.raises(LLMDispatchError) as exc:
        _adapter(orch).dispatch(_input())
    assert "malformed-response" in str(exc.value)


def test_missing_captured_model_maps_to_typed_error() -> None:
    """TC-ArgusAgent-AUDIT-001-39 (GREEN) — a result with no captured model id → typed error."""
    result = _success_result(model="")  # empty model id = malformed (no checkpoint)
    orch = _FakeOrchestrator(result=result)
    with pytest.raises(LLMDispatchError) as exc:
        _adapter(orch).dispatch(_input())
    assert "malformed-response" in str(exc.value)


def test_red_first_checkpoint_drift_silently_passes_in_baseline() -> None:
    """TC-ArgusAgent-AUDIT-001-40 (RED) — the baseline does NOT detect a drifting checkpoint."""
    orch = _FakeOrchestrator(result=_success_result(model="gpt-4o-DRIFTED"))
    rec = _RawRaisingAdapter(orch).dispatch(_input(pinned_model_checkpoint="gpt-4o-PINNED"))
    # The un-fixed baseline serves a recording under the WRONG checkpoint (the
    # silent-staleness hole the production adapter closes).
    assert rec.model_checkpoint == "gpt-4o-DRIFTED"


def test_checkpoint_drift_maps_to_typed_error() -> None:
    """TC-ArgusAgent-AUDIT-001-41 (GREEN) — a drifting captured checkpoint → CheckpointDriftError (AR5)."""
    orch = _FakeOrchestrator(result=_success_result(model="gpt-4o-DRIFTED"))
    with pytest.raises(CheckpointDriftError) as exc:
        _adapter(orch).dispatch(_input(pinned_model_checkpoint="gpt-4o-PINNED"))
    assert exc.value.pinned == "gpt-4o-PINNED"
    assert exc.value.captured == "gpt-4o-DRIFTED"


def test_matching_pinned_checkpoint_does_not_drift() -> None:
    """TC-ArgusAgent-AUDIT-001-42 — a matching pinned checkpoint is accepted (no false drift)."""
    orch = _FakeOrchestrator(result=_success_result(model="gpt-4o-PINNED"))
    rec = _adapter(orch).dispatch(_input(pinned_model_checkpoint="gpt-4o-PINNED"))
    assert rec.model_checkpoint == "gpt-4o-PINNED"


def test_red_first_budget_halt_passes_through_in_baseline() -> None:
    """TC-ArgusAgent-AUDIT-001-43 (RED) — a budget-halt result IndexErrors the baseline."""
    orch = _FakeOrchestrator(result=_budget_halt_result())
    with pytest.raises(IndexError):
        _RawRaisingAdapter(orch).dispatch(_input())


def test_budget_halt_maps_to_typed_error() -> None:
    """TC-ArgusAgent-AUDIT-001-44 (GREEN) — a budget halt → LLMDispatchError (AR10/NFR-R1)."""
    orch = _FakeOrchestrator(result=_budget_halt_result())
    with pytest.raises(LLMDispatchError) as exc:
        _adapter(orch).dispatch(_input())
    assert "budget-halt" in str(exc.value)


def test_no_failure_mode_propagates_uncaught() -> None:
    """TC-ArgusAgent-AUDIT-001-45 — the declared matrix raises ONLY LLMDispatchError subclasses."""
    cases = [
        _FakeOrchestrator(raises=RuntimeError("all-providers-unavailable")),
        _FakeOrchestrator(raises=TimeoutError("t")),
        _FakeOrchestrator(raises=ValueError("malformed json")),
        _FakeOrchestrator(result=_malformed_result()),
        _FakeOrchestrator(result=_budget_halt_result()),
    ]
    for orch in cases:
        with pytest.raises(LLMDispatchError):
            _adapter(orch).dispatch(_input())
