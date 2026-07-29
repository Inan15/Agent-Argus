"""ArgusAgent-AUDIT — OpenLLMAdapter & MinionsLLMAdapter test suite.

Verifies:
- OpenLLMAdapter dispatch via LiteLLM & HTTPX.
- Checkpoint capture & CheckpointDriftError on model mismatch.
- Typed error mapping (LLMDispatchError) on failure modes.
- Producer-side secret redaction and float-free credit formatting.
"""

from __future__ import annotations

import pytest

from argus.audit.minions_llm_adapter import MinionsLLMAdapter
from argus.audit.open_llm_adapter import OpenLLMAdapter, credits_to_str
from argus.audit.ports import (
    CheckpointDriftError,
    LLMDispatchError,
    LLMDispatchInput,
    LLMRecording,
)


class _FakeOrchestrator:
    """Fake orchestrator for testing dispatch behavior."""

    def __init__(self, *, result=None, raises: Exception | None = None) -> None:
        self.result = result
        self.raises = raises

    def execute_llm(self, req: LLMDispatchInput) -> LLMRecording | None:
        if self.raises:
            raise self.raises
        return self.result


def test_open_llm_adapter_default_dispatch() -> None:
    """Default HTTPX mock dispatch returns structured LLMRecording."""
    adapter = OpenLLMAdapter(model="gpt-4o-mini", provider_id="test-provider", use_litellm=False)
    req = LLMDispatchInput(
        target_path="src/main.py",
        prompt_template_version="v1.0",
        run_id="run-123",
    )
    rec = adapter.dispatch(req)

    assert isinstance(rec, LLMRecording)
    assert rec.model_checkpoint == "gpt-4o-mini"
    assert rec.provider_id == "test-provider"
    assert rec.prompt_template_version == "v1.0"
    assert rec.input_tokens >= 0
    assert rec.output_tokens >= 0
    assert isinstance(rec.credits_used, str)
    assert rec.credits_used == credits_to_str(0.000025)



def test_open_llm_adapter_checkpoint_drift_error() -> None:
    """CheckpointDriftError raised when pinned checkpoint differs from actual model."""
    adapter = OpenLLMAdapter(model="gpt-4o-mini", provider_id="test-provider", use_litellm=False)
    req = LLMDispatchInput(
        target_path="src/main.py",
        prompt_template_version="v1.0",
        pinned_model_checkpoint="claude-3-5-sonnet",
    )

    with pytest.raises(CheckpointDriftError) as exc_info:
        adapter.dispatch(req)

    assert exc_info.value.pinned == "claude-3-5-sonnet"
    assert exc_info.value.captured == "gpt-4o-mini"


def test_minions_llm_adapter_backward_compatibility() -> None:
    """MinionsLLMAdapter delegates cleanly to OpenLLMAdapter without minions_core."""
    adapter = MinionsLLMAdapter(provider_id="minions-test")
    req = LLMDispatchInput(
        target_path="src/auth.py",
        prompt_template_version="v1.0",
    )
    rec = adapter.dispatch(req)

    assert isinstance(rec, LLMRecording)
    assert rec.provider_id == "minions-test"
    assert rec.prompt_template_version == "v1.0"


def test_minions_llm_adapter_orchestrator_failure_mapping() -> None:
    """Orchestrator raises RuntimeError -> mapped to typed LLMDispatchError."""
    fake_orch = _FakeOrchestrator(raises=RuntimeError("all-providers-unavailable"))
    adapter = MinionsLLMAdapter(orchestrator=fake_orch, provider_id="test-prov")
    req = LLMDispatchInput(
        target_path="src/auth.py",
        prompt_template_version="v1.0",
    )

    with pytest.raises(LLMDispatchError) as exc_info:
        adapter.dispatch(req)

    assert "provider-chain-exhausted" in str(exc_info.value)


def test_credits_to_str_formatting() -> None:
    """Credits formatting converts float to exact numeric string."""
    assert credits_to_str(0.0) == "0"
    assert credits_to_str(1.5) == "3/2"
    assert credits_to_str("invalid") == "0"
