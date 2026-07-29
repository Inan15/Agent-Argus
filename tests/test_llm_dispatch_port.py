"""ArgusAgent-AUDIT (TC-ArgusAgent-AUDIT-001-NN) — the LLM-dispatch PORT + DTOs + FakeDispatch.

Drivers: ArgusAgent-AR7 (the port is the single injectable LLM seam), ArgusAgent-NFR-D2 (a
``FakeDispatch`` yields a deterministic ``LLMRecording`` with ZERO LLM tokens),
ArgusAgent-AR5 / DF-5-1-A (the captured checkpoint + prompt-template version fold into
the EXISTING 5.1 cache-key slots — ADDITIVE substitution, no key-SHAPE change),
ArgusAgent-AR8 (the DTOs are PURE — no I/O/clock/float at the model layer).

Story 6.1 (Epic-6 FIRST). Test area ArgusAgent-AUDIT, index 001 (first free index for
the new ``audit/`` package). Run under PYTHONIOENCODING=utf-8.
"""

from __future__ import annotations

from fractions import Fraction

import pytest
from pydantic import ValidationError

from argus.audit.deep_audit import (
    DeepAuditSeam,
    build_closure_from_recording,
)
from argus.audit.ports import (
    CheckpointDriftError,
    LLMDispatchError,
    LLMDispatchInput,
    LLMDispatchPort,
    LLMRecording,
)
from argus.cache.key import (
    V1_MODEL_CHECKPOINT,
    V1_PROMPT_TEMPLATE_VERSION,
    RecordingProducingClosure,
    derive_cache_key,
)


# ---------------------------------------------------------------------------
# FakeDispatch — the zero-token test double (NFR-D2). Lives in the test tree.
# ---------------------------------------------------------------------------


class FakeDispatch:
    """A deterministic ``LLMDispatchPort`` that consumes ZERO LLM tokens (NFR-D2).

    Returns a fixed, fully-specified ``LLMRecording`` and makes NO network call.
    It imports no provider code. Counts ``dispatch`` calls so a test can assert
    the deep path made exactly the expected (token-free) number of dispatches.
    """

    def __init__(
        self,
        *,
        model_checkpoint: str = "fake-checkpoint-v1",
        prompt_template_version: str = "fake-template-v1",
    ) -> None:
        self.model_checkpoint = model_checkpoint
        self.prompt_template_version = prompt_template_version
        self.calls = 0

    def dispatch(self, req: LLMDispatchInput) -> LLMRecording:
        self.calls += 1
        return LLMRecording(
            model_checkpoint=self.model_checkpoint,
            prompt_template_version=self.prompt_template_version,
            provider_id="fake",
            input_tokens=0,
            output_tokens=0,
            credits_used="0",
            finish_reason="stop",
            structured_output=("claim:fake",),
        )


def _input(**overrides: object) -> LLMDispatchInput:
    base = dict(target_path="src/mod.py", prompt_template_version="deep-v1")
    base.update(overrides)
    return LLMDispatchInput(**base)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AC1 — the port is a structural Protocol; FakeDispatch satisfies it
# ---------------------------------------------------------------------------


def test_fake_dispatch_satisfies_port_protocol_runtime_checkable() -> None:
    """TC-ArgusAgent-AUDIT-001-12 — FakeDispatch structurally satisfies LLMDispatchPort."""
    assert isinstance(FakeDispatch(), LLMDispatchPort)


def test_deep_audit_seam_depends_on_port_not_adapter() -> None:
    """TC-ArgusAgent-AUDIT-001-13 — DeepAuditSeam dispatches through an injected port."""
    fake = FakeDispatch()
    seam = DeepAuditSeam(port=fake)
    recording = seam.run(_input())
    assert isinstance(recording, LLMRecording)
    assert fake.calls == 1


# ---------------------------------------------------------------------------
# AC2 — FakeDispatch yields a deterministic, zero-token recording
# ---------------------------------------------------------------------------


def test_fake_dispatch_is_deterministic_and_zero_token() -> None:
    """TC-ArgusAgent-AUDIT-001-14 — same input → byte-identical recording; 0 tokens."""
    fake = FakeDispatch()
    a = fake.dispatch(_input())
    b = fake.dispatch(_input())
    assert a == b
    assert a.input_tokens == 0 and a.output_tokens == 0
    assert a.credits_used == "0"


def test_fake_dispatch_feeds_real_closure_builder_token_free() -> None:
    """TC-ArgusAgent-AUDIT-001-15 — the fake feeds the REAL closure-builder → stable key."""
    fake = FakeDispatch()
    recording = fake.dispatch(_input())
    closure = build_closure_from_recording(
        recording=recording,
        content_hash="ch",
        grammar_version="gv",
        budget=10,
        materiality_bar="bar",
        work_manifest_files=("a.py",),
    )
    key1 = derive_cache_key(closure)
    key2 = derive_cache_key(
        build_closure_from_recording(
            recording=recording,
            content_hash="ch",
            grammar_version="gv",
            budget=10,
            materiality_bar="bar",
            work_manifest_files=("a.py",),
        )
    )
    assert key1 == key2


# ---------------------------------------------------------------------------
# AC4 — additive substitution: no-LLM golden unchanged; distinct values → distinct keys
# ---------------------------------------------------------------------------


def _base_closure_kwargs() -> dict[str, object]:
    return dict(
        content_hash="content-hash-1",
        grammar_version="ts-python-0.21",
        budget=100,
        materiality_bar="release-blocking",
        work_manifest_files=("src/a.py", "src/b.py"),
    )


def test_v1_no_llm_golden_key_unchanged_by_substitution_path() -> None:
    """TC-ArgusAgent-AUDIT-001-16 — a no-LLM closure (placeholder defaults) is byte-identical.

    The closure-builder substitutes a REAL captured value; a Tier-A no-LLM run
    that still uses the 5.1 placeholder defaults must derive the SAME key it did
    before this story. Proven by: a closure built directly with the placeholder
    defaults equals a closure built from a recording carrying those SAME default
    placeholder values (the substitution slot is additive, not shape-changing).
    """
    direct = RecordingProducingClosure(
        model_checkpoint=V1_MODEL_CHECKPOINT,
        prompt_template_version=V1_PROMPT_TEMPLATE_VERSION,
        **_base_closure_kwargs(),
    )
    placeholder_recording = LLMRecording(
        model_checkpoint=V1_MODEL_CHECKPOINT,
        prompt_template_version=V1_PROMPT_TEMPLATE_VERSION,
        provider_id="none",
    )
    via_builder = build_closure_from_recording(
        recording=placeholder_recording, **_base_closure_kwargs()
    )
    assert derive_cache_key(direct) == derive_cache_key(via_builder)


def test_distinct_captured_checkpoint_derives_distinct_key() -> None:
    """TC-ArgusAgent-AUDIT-001-17 — a drifting captured checkpoint moves the key (AR5 seam)."""
    rec_a = LLMRecording(
        model_checkpoint="gpt-4o-2026-01", prompt_template_version="deep-v1", provider_id="openai"
    )
    rec_b = LLMRecording(
        model_checkpoint="gpt-4o-2026-09", prompt_template_version="deep-v1", provider_id="openai"
    )
    key_a = derive_cache_key(build_closure_from_recording(recording=rec_a, **_base_closure_kwargs()))
    key_b = derive_cache_key(build_closure_from_recording(recording=rec_b, **_base_closure_kwargs()))
    assert key_a != key_b


def test_distinct_prompt_template_version_derives_distinct_key() -> None:
    """TC-ArgusAgent-AUDIT-001-18 — a prompt-template change moves the key (DF-5-1-A)."""
    rec_a = LLMRecording(
        model_checkpoint="m", prompt_template_version="deep-v1", provider_id="openai"
    )
    rec_b = LLMRecording(
        model_checkpoint="m", prompt_template_version="deep-v2", provider_id="openai"
    )
    key_a = derive_cache_key(build_closure_from_recording(recording=rec_a, **_base_closure_kwargs()))
    key_b = derive_cache_key(build_closure_from_recording(recording=rec_b, **_base_closure_kwargs()))
    assert key_a != key_b


# ---------------------------------------------------------------------------
# AC6 — DTO purity (no float / extra=forbid / frozen) + non-ASCII round-trip
# ---------------------------------------------------------------------------


def test_recording_is_frozen_and_forbids_extra() -> None:
    """TC-ArgusAgent-AUDIT-001-19 — LLMRecording is frozen + extra=forbid (AR8)."""
    rec = LLMRecording(model_checkpoint="m", prompt_template_version="t", provider_id="p")
    with pytest.raises(ValidationError):
        LLMRecording(model_checkpoint="m", prompt_template_version="t", provider_id="p", surprise=1)  # type: ignore[call-arg]
    with pytest.raises(ValidationError):
        rec.model_checkpoint = "other"  # type: ignore[misc]


def test_input_is_frozen_and_forbids_extra() -> None:
    """TC-ArgusAgent-AUDIT-001-20 — LLMDispatchInput is frozen + extra=forbid (AR8)."""
    with pytest.raises(ValidationError):
        LLMDispatchInput(target_path="a", prompt_template_version="t", surprise=1)  # type: ignore[call-arg]


def test_credits_used_is_string_not_float() -> None:
    """TC-ArgusAgent-AUDIT-001-21 — credits is a frozen exact-numeric string, never float (AR4)."""
    rec = LLMRecording(
        model_checkpoint="m", prompt_template_version="t", provider_id="p", credits_used=str(Fraction(3, 2))
    )
    assert isinstance(rec.credits_used, str)
    assert rec.credits_used == "3/2"


def test_non_ascii_recording_round_trips_and_derives_stable_key() -> None:
    """TC-ArgusAgent-AUDIT-001-22 — a non-ASCII checkpoint/path derives a stable key (AI-E1-1)."""
    rec = LLMRecording(
        model_checkpoint="modèle-café-2026",
        prompt_template_version="gabarit-déyuan-v1",
        provider_id="provider-ünïcode",
        structured_output=("réclamation:über",),
    )
    kwargs = dict(
        content_hash="ch",
        grammar_version="gv",
        budget=5,
        materiality_bar="барьер",
        work_manifest_files=("src/café.py", "src/déjà.py"),
    )
    key1 = derive_cache_key(build_closure_from_recording(recording=rec, **kwargs))
    key2 = derive_cache_key(build_closure_from_recording(recording=rec, **kwargs))
    assert key1 == key2
    assert isinstance(key1, str) and len(key1) == 64


def test_dispatch_error_message_carries_no_response_bytes() -> None:
    """TC-ArgusAgent-AUDIT-001-23 — typed errors carry only structured ids (NFR-S1)."""
    err = LLMDispatchError("llm-dispatch-failed:reason=transport-error:provider=openai")
    drift = CheckpointDriftError(pinned="a", captured="b")
    assert "reason=" in str(err)
    assert isinstance(drift, LLMDispatchError)
    assert drift.pinned == "a" and drift.captured == "b"


def test_open_llm_adapter_builds_messages_and_calculates_credits() -> None:
    """Verify OpenLLMAdapter builds prompt messages from input and computes non-zero credits."""
    from argus.audit.open_llm_adapter import OpenLLMAdapter, credits_to_str

    adapter = OpenLLMAdapter(model="mock-model", provider_id="test-provider", api_base=None)
    req = LLMDispatchInput(
        target_path="argus/pipeline.py",
        prompt_template_version="deep-v1",
        tier="high",
        run_id="run-123",
    )
    messages = adapter._build_messages(req)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "deep-v1" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert "argus/pipeline.py" in messages[1]["content"]
    assert "run-123" in messages[1]["content"]

    rec = adapter.dispatch(req)
    assert rec.model_checkpoint == "mock-model"
    assert rec.input_tokens > 0
    assert rec.credits_used != "0"
    assert rec.credits_used == credits_to_str(0.000025)

