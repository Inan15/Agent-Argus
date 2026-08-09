"""ArgusAgent-AUDIT — the ``OpenLLMAdapter`` dispatch paths that never touch a network.

Verification area ArgusAgent-AUDIT (AR7 / AR5 / AR10 / AR4 / NFR-S1).

Why this file exists
--------------------
``open_llm_adapter`` shipped at 50% line coverage, and the uncovered half was not
incidental — it was BOTH real dispatch backends:

* ``_dispatch_litellm`` (lines 102-139) is dead to the suite because ``litellm`` is an
  optional dependency that is not installed in the dev environment;
* the live-HTTP half of ``_dispatch_httpx`` (lines 165-200) is dead because the adapter
  short-circuits to a mock recording whenever no ``api_base`` is configured.

What was actually exercised was the mock fallback. That is the one path that cannot fail
in production, so the covered fraction was inversely correlated with risk: the AR10
no-crash matrix, the AR5 checkpoint capture, and the AR4 float-free credit rendering were
all asserted ONLY on a branch that fabricates its own numbers.

These tests substitute the backends rather than the network — a fake ``litellm`` module
object and a fake ``httpx.Client`` — so every branch runs with zero tokens and zero
sockets (NFR-D2), while the real adapter code under test is unmodified.
"""

from __future__ import annotations

from typing import Any

import httpx
import pytest

from argus.audit import open_llm_adapter as mod
from argus.audit.open_llm_adapter import OpenLLMAdapter, credits_to_str
from argus.audit.ports import (
    CheckpointDriftError,
    LLMDispatchError,
    LLMDispatchInput,
    LLMRecording,
)

_API_KEY = "sk-test-do-not-leak-me"


@pytest.fixture(autouse=True)
def _no_ambient_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    """Neutralise the ambient endpoint env vars the constructor reads.

    ``__init__`` falls back to ``OPENAI_BASE_URL`` / ``OLLAMA_HOST`` when no ``api_base``
    is passed. A developer with either exported would otherwise flip the mock-mode tests
    onto the live HTTP branch and attempt a real connection — an environment-dependent
    suite is not a deterministic one.
    """
    for var in ("OPENAI_BASE_URL", "OLLAMA_HOST", "OPENAI_API_KEY"):
        monkeypatch.delenv(var, raising=False)


def _req(**overrides: Any) -> LLMDispatchInput:
    """A metadata-only dispatch request (NFR-S1 — no prompt/source bytes)."""
    base: dict[str, Any] = {
        "target_path": "src/auth.py",
        "prompt_template_version": "v1.0",
        "run_id": "run-123",
    }
    base.update(overrides)
    return LLMDispatchInput(**base)


# ─────────────────────────────────────────────────────────────────────────────
# Fake LiteLLM backend
# ─────────────────────────────────────────────────────────────────────────────


class _Usage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class _Choice:
    def __init__(self, finish_reason: str) -> None:
        self.finish_reason = finish_reason


class _LiteLLMResponse:
    def __init__(
        self,
        *,
        model: str = "gpt-4o-mini",
        usage: _Usage | None = None,
        choices: list[_Choice] | None = None,
    ) -> None:
        self.model = model
        self.usage = usage
        self.choices = choices if choices is not None else []


class _FakeLiteLLM:
    """Stands in for the optional ``litellm`` module object."""

    def __init__(self, *, response: Any = None, raises: Exception | None = None) -> None:
        self._response = response
        self._raises = raises
        self.calls: list[dict[str, Any]] = []

    def completion(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if self._raises:
            raise self._raises
        return self._response


def _install_litellm(monkeypatch: pytest.MonkeyPatch, fake: _FakeLiteLLM) -> None:
    """Make the adapter believe the optional LiteLLM engine is installed."""
    monkeypatch.setattr(mod, "LITELLM_AVAILABLE", True)
    monkeypatch.setattr(mod, "litellm", fake, raising=False)


# ─────────────────────────────────────────────────────────────────────────────
# Fake HTTPX transport
# ─────────────────────────────────────────────────────────────────────────────


class _FakeHTTPResponse:
    def __init__(
        self,
        payload: dict[str, Any] | None = None,
        *,
        status_error: Exception | None = None,
        json_error: Exception | None = None,
    ) -> None:
        self._payload = payload or {}
        self._status_error = status_error
        self._json_error = json_error

    def raise_for_status(self) -> None:
        if self._status_error:
            raise self._status_error

    def json(self) -> dict[str, Any]:
        if self._json_error:
            raise self._json_error
        return self._payload


class _FakeHTTPClient:
    """A context-manager stand-in for ``httpx.Client`` that records the request."""

    last_request: dict[str, Any] = {}

    def __init__(self, response: _FakeHTTPResponse, *, post_error: Exception | None = None) -> None:
        self._response = response
        self._post_error = post_error

    def __call__(self, *args: Any, **kwargs: Any) -> _FakeHTTPClient:
        # `httpx.Client(timeout=10.0)` — the instance is reused as its own factory so a
        # single object can be patched in as the class.
        return self

    def __enter__(self) -> _FakeHTTPClient:
        return self

    def __exit__(self, *exc: Any) -> bool:
        return False

    def post(self, url: str, *, json: Any = None, headers: Any = None) -> _FakeHTTPResponse:
        type(self).last_request = {"url": url, "json": json, "headers": headers}
        if self._post_error:
            raise self._post_error
        return self._response


def _install_httpx(monkeypatch: pytest.MonkeyPatch, client: _FakeHTTPClient) -> None:
    monkeypatch.setattr(httpx, "Client", client)


# ─────────────────────────────────────────────────────────────────────────────
# LiteLLM backend — AR5 capture, AR4 credits, AR10 error mapping
# ─────────────────────────────────────────────────────────────────────────────


def test_litellm_dispatch_captures_checkpoint_and_renders_float_free_credits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The captured model is the RESPONSE's, not the config string (AR5), and credits
    are an exact numeric string (AR4)."""
    fake = _FakeLiteLLM(
        response=_LiteLLMResponse(
            model="gpt-4o-mini-2024-07-18",  # the provider resolved the alias
            usage=_Usage(prompt_tokens=100, completion_tokens=50),
            choices=[_Choice("stop")],
        )
    )
    _install_litellm(monkeypatch, fake)

    adapter = OpenLLMAdapter(model="gpt-4o-mini", provider_id="lite", api_key=_API_KEY)
    rec = adapter.dispatch(_req())

    assert isinstance(rec, LLMRecording)
    # AR5 — the dispatch-actual id, which is what closes the cache key.
    assert rec.model_checkpoint == "gpt-4o-mini-2024-07-18"
    assert rec.input_tokens == 100
    assert rec.output_tokens == 50
    assert rec.finish_reason == "stop"
    # AR4 — 100*0.0000015 + 50*0.000002, as a Fraction string with no float spelling.
    assert rec.credits_used == credits_to_str(0.00025)
    assert "." not in rec.credits_used
    # NFR-S1 — the recording carries metadata only; no prompt/response bytes anywhere.
    assert rec.structured_output == ()


def test_litellm_dispatch_sends_the_declared_template_version_and_no_source_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The assembled prompt carries the locator + declared template version only."""
    fake = _FakeLiteLLM(response=_LiteLLMResponse(usage=_Usage(1, 1), choices=[_Choice("stop")]))
    _install_litellm(monkeypatch, fake)

    adapter = OpenLLMAdapter(model="gpt-4o-mini", provider_id="lite", temperature=0.7)
    adapter.dispatch(_req(target_path="src/auth.py", prompt_template_version="v2.1"))

    (call,) = fake.calls
    assert call["model"] == "gpt-4o-mini"
    assert call["temperature"] == 0.7
    system, user = call["messages"]
    assert system["role"] == "system" and "v2.1" in system["content"]
    assert user["role"] == "user"
    assert "src/auth.py" in user["content"]
    assert "run-123" in user["content"]


def test_litellm_dispatch_tolerates_a_response_missing_usage_and_choices(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A sparse provider response degrades to zeros, never an AttributeError (AR10).

    Providers differ on whether `usage` and `choices` are populated. The adapter reads
    both defensively; this pins that the defence works rather than merely exists.
    """
    fake = _FakeLiteLLM(response=_LiteLLMResponse(usage=None, choices=[]))
    _install_litellm(monkeypatch, fake)

    rec = OpenLLMAdapter(model="m", provider_id="lite").dispatch(_req())

    assert rec.input_tokens == 0
    assert rec.output_tokens == 0
    assert rec.finish_reason == ""
    assert rec.credits_used == "0"


def test_litellm_checkpoint_drift_is_raised_not_flattened_to_a_transport_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Drift must survive BOTH except-chains as its own type (AR5).

    `_dispatch_litellm` and `dispatch` each wrap broad `except Exception` handlers that
    remap to `LLMDispatchError`. Since `CheckpointDriftError` IS an `LLMDispatchError`
    subclass, an ordering slip in either handler would silently downgrade a drift into a
    generic transport error — and the run would cache a mixed-checkpoint result instead
    of aborting.
    """
    fake = _FakeLiteLLM(
        response=_LiteLLMResponse(model="gpt-4o-mini-2024-07-18", usage=_Usage(1, 1))
    )
    _install_litellm(monkeypatch, fake)

    adapter = OpenLLMAdapter(model="gpt-4o-mini", provider_id="lite")

    with pytest.raises(CheckpointDriftError) as exc_info:
        adapter.dispatch(_req(pinned_model_checkpoint="gpt-4o-mini-2024-05-13"))

    assert exc_info.value.pinned == "gpt-4o-mini-2024-05-13"
    assert exc_info.value.captured == "gpt-4o-mini-2024-07-18"
    assert "transport-error" not in str(exc_info.value)


def test_litellm_provider_exception_maps_to_typed_error_without_leaking_the_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A raising provider degrades to LLMDispatchError (AR10), secret-free (NFR-S1)."""
    fake = _FakeLiteLLM(raises=RuntimeError(f"auth failed for key {_API_KEY}"))
    _install_litellm(monkeypatch, fake)

    adapter = OpenLLMAdapter(model="m", provider_id="lite", api_key=_API_KEY)

    with pytest.raises(LLMDispatchError) as exc_info:
        adapter.dispatch(_req())

    message = str(exc_info.value)
    assert "llm-dispatch-failed:reason=transport-error:provider=lite" == message
    # The upstream text carried the key; the typed error must not re-emit it.
    assert _API_KEY not in message


# ─────────────────────────────────────────────────────────────────────────────
# Native HTTPX backend — the live endpoint branch
# ─────────────────────────────────────────────────────────────────────────────


def test_httpx_live_dispatch_reads_the_response_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The OpenAI-compatible branch parses model, usage and finish_reason from the body."""
    client = _FakeHTTPClient(
        _FakeHTTPResponse(
            {
                "model": "llama3.1:8b",
                "usage": {"prompt_tokens": 200, "completion_tokens": 100},
                "choices": [{"finish_reason": "length"}],
            }
        )
    )
    _install_httpx(monkeypatch, client)

    adapter = OpenLLMAdapter(
        model="llama3.1:8b",
        provider_id="ollama",
        api_base="http://localhost:11434/",  # trailing slash must not double up
        api_key=_API_KEY,
        use_litellm=False,
    )
    rec = adapter.dispatch(_req())

    assert _FakeHTTPClient.last_request["url"] == "http://localhost:11434/v1/chat/completions"
    assert _FakeHTTPClient.last_request["headers"] == {"Authorization": f"Bearer {_API_KEY}"}
    assert _FakeHTTPClient.last_request["json"]["model"] == "llama3.1:8b"
    assert rec.model_checkpoint == "llama3.1:8b"
    assert rec.input_tokens == 200
    assert rec.output_tokens == 100
    assert rec.finish_reason == "length"
    assert rec.credits_used == credits_to_str(0.0005)


def test_httpx_live_dispatch_defaults_a_body_with_no_usage_or_choices(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An empty-but-valid JSON body yields zeros and the configured model, not a crash."""
    _install_httpx(monkeypatch, _FakeHTTPClient(_FakeHTTPResponse({})))

    adapter = OpenLLMAdapter(
        model="cfg-model", provider_id="p", api_base="http://x", use_litellm=False
    )
    rec = adapter.dispatch(_req())

    assert rec.model_checkpoint == "cfg-model"
    assert rec.input_tokens == 0
    assert rec.finish_reason == "stop"


def test_httpx_transport_failure_maps_to_typed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """`httpx.HTTPError` is caught at the seam and never escapes as itself (AR10)."""
    _install_httpx(
        monkeypatch,
        _FakeHTTPClient(_FakeHTTPResponse({}), post_error=httpx.ConnectError("refused")),
    )

    adapter = OpenLLMAdapter(
        model="m", provider_id="ollama", api_base="http://x", use_litellm=False
    )

    with pytest.raises(LLMDispatchError) as exc_info:
        adapter.dispatch(_req())

    assert str(exc_info.value) == "llm-dispatch-failed:reason=transport-error:provider=ollama"


def test_httpx_status_error_maps_to_typed_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A non-2xx surfaced by `raise_for_status` degrades the same way."""
    request = httpx.Request("POST", "http://x/v1/chat/completions")
    response = httpx.Response(500, request=request)
    _install_httpx(
        monkeypatch,
        _FakeHTTPClient(
            _FakeHTTPResponse(
                {}, status_error=httpx.HTTPStatusError("500", request=request, response=response)
            )
        ),
    )

    adapter = OpenLLMAdapter(
        model="m", provider_id="ollama", api_base="http://x", use_litellm=False
    )

    with pytest.raises(LLMDispatchError):
        adapter.dispatch(_req())


def test_httpx_checkpoint_drift_precedes_the_network_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Drift is detected before any request is issued — no tokens spent on a doomed run."""
    client = _FakeHTTPClient(_FakeHTTPResponse({}), post_error=AssertionError("must not POST"))
    _install_httpx(monkeypatch, client)

    adapter = OpenLLMAdapter(
        model="m", provider_id="p", api_base="http://x", use_litellm=False
    )

    with pytest.raises(CheckpointDriftError):
        adapter.dispatch(_req(pinned_model_checkpoint="other-model"))


# ─────────────────────────────────────────────────────────────────────────────
# The outer `dispatch` no-crash matrix (AR10)
# ─────────────────────────────────────────────────────────────────────────────


def test_unavailable_upstream_maps_to_provider_chain_exhausted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A non-HTTP failure escaping the backend is classified by the outer handler.

    `res.json()` raising is not an `httpx.HTTPError`, so it passes through
    `_dispatch_httpx` untouched and lands in `dispatch`'s catch-all — the branch that
    distinguishes an exhausted provider chain from a plain transport fault.
    """
    _install_httpx(
        monkeypatch,
        _FakeHTTPClient(
            _FakeHTTPResponse({}, json_error=RuntimeError("all backends unavailable"))
        ),
    )

    adapter = OpenLLMAdapter(
        model="m", provider_id="chain", api_base="http://x", use_litellm=False
    )

    with pytest.raises(LLMDispatchError) as exc_info:
        adapter.dispatch(_req())

    assert str(exc_info.value) == (
        "llm-dispatch-failed:reason=provider-chain-exhausted:provider=chain"
    )


def test_other_upstream_failures_map_to_transport_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Anything not naming unavailability is the generic transport degradation."""
    _install_httpx(
        monkeypatch,
        _FakeHTTPClient(_FakeHTTPResponse({}, json_error=ValueError("malformed body"))),
    )

    adapter = OpenLLMAdapter(
        model="m", provider_id="chain", api_base="http://x", use_litellm=False
    )

    with pytest.raises(LLMDispatchError) as exc_info:
        adapter.dispatch(_req())

    assert str(exc_info.value) == "llm-dispatch-failed:reason=transport-error:provider=chain"


def test_mock_mode_is_only_entered_when_no_endpoint_is_configured() -> None:
    """With no api_base the adapter self-reports fabricated counts — and only then.

    This is the ONE branch the pre-existing suite covered. It is pinned here alongside
    the real ones so the boundary is explicit: the fabricated 10/5 token counts must
    never be reachable once an operator has configured an endpoint.
    """
    adapter = OpenLLMAdapter(model="m", provider_id="p", use_litellm=False)
    rec = adapter.dispatch(_req())

    assert (rec.input_tokens, rec.output_tokens) == (10, 5)
    assert rec.credits_used == credits_to_str(0.000025)


# ─────────────────────────────────────────────────────────────────────────────
# AR4 — credit rendering never produces a float leaf
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "0"),
        (None, "0"),
        (0.5, "1/2"),
        (0.00025, "1/4000"),
        ("not-a-number", "0"),
        ([], "0"),
    ],
)
def test_credits_to_str_is_total_and_float_free(value: object, expected: str) -> None:
    """Every input yields an exact numeric string; a bad one yields "0", never a raise.

    The canonical serializer rejects a float leaf, so a credit value that rendered as
    `1.5e-05` would fail the run at key-derivation time rather than here.
    """
    rendered = credits_to_str(value)

    assert rendered == expected
    assert "." not in rendered
    assert "e" not in rendered.lower()
