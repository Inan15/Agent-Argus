"""THE single injectable LLM-dispatch seam — port Protocol + frozen DTOs (PURE).

Drivers: ArgusAgent-AR7 (the LLM is reached ONLY via this ArgusAgent-owned port; never via
a host product's api / app-factory / api-server modules — ArgusAgent imports no host
package at all, RS-1/IN-2),
ArgusAgent-NFR-D2 (the deep path is zero-token-testable — a ``FakeDispatch`` yields 0
LLM tokens; importing this module pulls NO provider code, NO FastAPI),
ArgusAgent-NFR-P2 (stack-agnostic claim interface — the port is the seam the
``claim → validated?`` interface rides), ArgusAgent-AR5 (the captured model checkpoint
+ prompt-template version are the cache-key closure inputs 5.1 reserved),
ArgusAgent-AR8 (PURE module — the DTOs do NO I/O, NO clock, NO uuid/random/float at
the model layer), ArgusAgent-AR10 (a failure degrades to a typed error/finding, never
an uncaught raise out of the seam), ArgusAgent-NFR-S1 (no prompt/response/secret bytes
on the ``LLMRecording``), ArgusAgent-NFR-M1 (≤1200-line files).

Verification area ArgusAgent-AUDIT (TC-ArgusAgent-AUDIT-001-NN).

Why this module exists — the determinism-quarantine keystone
------------------------------------------------------------
Architecture Decision E / §324 / §496-497: "the ``LLMDispatchPort`` is the only
seam between the pure core and the non-deterministic LLM substrate; everything
downstream is pure folds over recordings." The port is a structural
``typing.Protocol`` (DIP): ``deep_audit`` and every later Epic-6 deep pass depend
on the PORT TYPE, never the orchestrator directly. This module is PURE-importable
— it carries the Protocol + the frozen request/response DTOs + the typed errors,
and nothing else (no ``providers`` import, no FastAPI). The IMPURE adapter that
holds an ``LLMProviderOrchestrator`` lives in ``minions_llm_adapter`` (the one
``argus.audit`` module allowed to import ``providers``).

Producer-side redaction (NFR-S1 / cross-cutting #5)
---------------------------------------------------
The ``LLMRecording`` carries METADATA (captured model checkpoint, prompt-template
version, token counts, finish_reason, credits, provider_id) + the DECLARED
structured output the deep-audit consumes — NEVER raw prompt/response bytes or
secret values. Redaction is a property of the PRODUCER (the adapter), not a
post-filter; the DTO simply has no field that could hold source bytes.

No float (AR4)
--------------
Any credit/ratio-shaped field is ``str`` (a frozen exact-numeric string), never
``float`` — the single canonical serializer raises on a float leaf, so a
credit-bearing recording must already be float-free to derive a stable key.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "LLMDispatchError",
    "CheckpointDriftError",
    "LLMDispatchInput",
    "LLMRecording",
    "LLMDispatchPort",
]


class LLMDispatchError(ValueError):
    """The typed degradation a failed dispatch routes to (AR10 / NFR-R1).

    A ``ValueError`` subclass — the named typed outcome the adapter's no-crash
    matrix maps EVERY declared failure mode to (provider-chain exhaustion,
    transport timeout, malformed/empty response, budget halt), so a failure
    NEVER propagates out of ``dispatch(...)`` as an uncaught
    ``RuntimeError``/``Exception``. The string form carries ONLY structured
    identifiers (a reason code + provider id) — NEVER prompt/response/secret
    bytes (NFR-S1).
    """


class CheckpointDriftError(LLMDispatchError):
    """A captured checkpoint drifted from the run's pinned checkpoint (AR5).

    Raised when the adapter is given a pinned checkpoint and the API response
    returns a DIFFERENT model id mid-run — the live capture of the 5.1
    ``checkpoint_drift`` detection seam. 6.1 EXPOSES the captured checkpoint on
    the ``LLMRecording`` and proves two captured values derive two cache keys;
    the live mid-run abort/re-audit loop + the ``checkpoint_drift`` finding's
    pipeline wiring are deferred to the shared deep-audit pipeline, which is
    UNSCHEDULED — ⛔ not Story 6.2's, which is ``done``. Owner XAgent007
    (Engineering Lead); ``DF-12-2-D``.
    """

    def __init__(self, *, pinned: str, captured: str) -> None:
        super().__init__(
            f"checkpoint-drift:pinned={pinned}:captured={captured}"
        )
        self.pinned = pinned
        self.captured = captured


class LLMDispatchInput(BaseModel):
    """Frozen request the deep-audit hands the port (metadata only — NFR-S1).

    ``frozen=True, extra="forbid"`` (the Epic-1..5 contract precedent), no float
    (AR4/AR8). Carries the deep-audit request SCOPE — a target file/locator
    scope, the declared ``prompt_template_version`` the deep pass dispatches
    under, a tier hint, and the work-manifest-scoped run id — never raw prompt
    or secret bytes (the prompt is assembled by the adapter from the declared
    template + the scoped, redacted inputs, not carried as source bytes here).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    target_path: str = Field(
        ..., min_length=1, description="Audited unit / locator scope the deep pass targets."
    )
    prompt_template_version: str = Field(
        ..., min_length=1, description="Declared prompt-template version the deep pass dispatches under (AR5)."
    )
    tier: str = Field(
        default="standard", min_length=1, description="WorkerTier hint (string; resolved by the adapter)."
    )
    run_id: str = Field(
        default="", description="Work-manifest-scoped run id (carried for provenance; no secret bytes)."
    )
    pinned_model_checkpoint: str | None = Field(
        default=None,
        description="The run's pinned checkpoint; a drifting captured value → CheckpointDriftError (AR5).",
    )


class LLMRecording(BaseModel):
    """Frozen metadata record the port returns — the closure input source (AR5).

    ``frozen=True, extra="forbid"``, no float (AR4/AR8). Carries the captured
    ``model_checkpoint`` (← the dispatch-actual ``LLMResponse.model``, NOT a
    config string), the ``prompt_template_version`` the dispatch ran under, token
    counts (int), ``finish_reason``, ``credits_used`` (a frozen exact-numeric
    STRING, never float — AR4), ``provider_id``, and the DECLARED structured
    output the deep-audit consumes (claim/locator-shaped strings) — NEVER raw
    prompt/response/secret bytes (NFR-S1 producer-side redaction).

    The captured ``model_checkpoint`` + ``prompt_template_version`` are the two
    cache-key closure inputs 5.1 reserved as placeholders; the closure-builder in
    ``deep_audit`` folds them into the EXISTING slots additively (no key-shape
    change). A distinct captured checkpoint derives a distinct key (the 5.1 drift
    seam), so a mixed-checkpoint result can never be served as a hit.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model_checkpoint: str = Field(
        ..., min_length=1, description="Captured dispatch-actual model id (← LLMResponse.model, AR5)."
    )
    prompt_template_version: str = Field(
        ..., min_length=1, description="Prompt-template version this dispatch ran under (AR5)."
    )
    provider_id: str = Field(..., min_length=1, description="The provider that produced the response.")
    input_tokens: int = Field(default=0, ge=0, description="Prompt token count (metadata only — NFR-S1).")
    output_tokens: int = Field(default=0, ge=0, description="Completion token count (metadata only).")
    credits_used: str = Field(
        default="0", min_length=1, description="Credits consumed as a frozen exact-numeric string (AR4 — no float)."
    )
    finish_reason: str = Field(default="", description="Structured finish/stop reason (no response bytes).")
    structured_output: tuple[str, ...] = Field(
        default=(),
        description="Declared structured output the deep-audit consumes (claim/locator-shaped — no source bytes).",
    )


@runtime_checkable
class LLMDispatchPort(Protocol):
    """The ONE injectable LLM seam (DIP — architecture Decision E / §324).

    A structural ``typing.Protocol`` with a single method. ``deep_audit`` and
    every later Epic-6 deep pass depend on THIS type (injected via
    constructor/parameter), never the concrete adapter — so the deep path is
    provider-agnostic and a ``FakeDispatch`` gives zero-token tests (NFR-D2).

    Implementations MUST NEVER raise an uncaught ``RuntimeError``/``Exception``
    out of ``dispatch(...)``: every failure degrades to an ``LLMDispatchError``
    (or a subclass) or a typed degradation ``LLMRecording`` (AR10).
    """

    def dispatch(self, req: LLMDispatchInput) -> LLMRecording:
        """Dispatch one deep-audit request, returning a frozen ``LLMRecording``."""
        ...
