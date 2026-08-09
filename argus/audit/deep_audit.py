"""The PURE deep-audit seam — depends on the PORT TYPE, never the adapter (DIP).

STATUS: **EXPERIMENTAL** (story 22-15, M9 decision). This deep-audit seam is NOT
wired into the Minions product run path — nothing in Minions orchestration
dispatches through it. The wire-or-graduate decision is tracked as DF-22-15-A.

Drivers: ArgusAgent-AR7 (the deep pass reaches the LLM ONLY via the injected
``LLMDispatchPort``), ArgusAgent-NFR-D2 (zero-token-testable — a ``FakeDispatch`` gives
the deep path zero LLM tokens; importing this module pulls NO provider code),
ArgusAgent-AR5 / DF-5-1-A (the closure-builder folds the captured checkpoint +
prompt-template version into the EXISTING 5.1 cache-key slots — ADDITIVE
substitution, no key-SHAPE change), ArgusAgent-AR8 (PURE — no I/O, no clock, no LLM,
no provider import), ArgusAgent-NFR-M1 (≤1200-line files).

Verification area ArgusAgent-AUDIT (TC-ArgusAgent-AUDIT-001-NN).

Why this module is PURE of providers
------------------------------------
``deep_audit`` is the consumer side of the determinism quarantine. It depends on
the PORT TYPE (``LLMDispatchPort``), which is injected (constructor/parameter),
so it is provider-agnostic and never imports ANY provider package or the
concrete adapter (RS-1/IN-2: ArgusAgent imports nothing from a host product; the
provider-package reference this sentence used to name no longer exists here). The full Python AST-grounding of deep claims is Story 6.2; in
V1 this module is a THIN seam: it dispatches through the injected port and folds
the returned ``LLMRecording`` into a cache key via the closure-builder below.

The ADDITIVE substitution (AR5 / DF-5-1-A / DN-SUBST)
-----------------------------------------------------
``build_closure_from_recording`` builds a ``RecordingProducingClosure`` whose
``model_checkpoint`` + ``prompt_template_version`` slots carry the LIVE
recording's CAPTURED values — folded into the SAME slots 5.1 reserved (no
key-shape / ``CACHE_KEY_SCHEMA_VERSION`` change). A distinct captured checkpoint
derives a distinct key (the 5.1 drift seam fed by a real source); a Tier-A
no-LLM run that omits a recording still uses the 5.1 placeholder defaults and
derives a BYTE-IDENTICAL key. The builder REUSES ``cache/key.py`` read-only — it
introduces NO second serializer / hasher (the 1.1 single-serializer AST gate
stays green).
"""

from __future__ import annotations

from typing import Any

from argus.audit.ports import (
    LLMDispatchInput,
    LLMDispatchPort,
    LLMRecording,
)
from argus.cache.key import RecordingProducingClosure

__all__ = ["build_closure_from_recording", "DeepAuditSeam"]


def build_closure_from_recording(
    *,
    recording: LLMRecording,
    content_hash: str,
    grammar_version: str,
    budget: int,
    materiality_bar: str,
    work_manifest_files: tuple[str, ...],
    tool_versions: dict[str, str] | None = None,
    critical_paths: tuple[str, ...] = (),
    excluded_critical_paths: tuple[str, ...] = (),
    detectors: Any = None,
) -> RecordingProducingClosure:
    """Fold a live ``LLMRecording`` into a ``RecordingProducingClosure`` (AR5).

    Substitutes the captured ``model_checkpoint`` + ``prompt_template_version``
    into the EXISTING 5.1 slots (ADDITIVE — no key-shape change). All other
    closure inputs are passed through unchanged. REUSES the 5.1 closure model
    read-only; derives no key here (the caller composes ``derive_cache_key``).
    """
    kwargs: dict[str, Any] = {
        "content_hash": content_hash,
        "grammar_version": grammar_version,
        "tool_versions": dict(tool_versions or {}),
        "budget": budget,
        "materiality_bar": materiality_bar,
        "work_manifest_files": work_manifest_files,
        "critical_paths": critical_paths,
        "excluded_critical_paths": excluded_critical_paths,
        "model_checkpoint": recording.model_checkpoint,
        "prompt_template_version": recording.prompt_template_version,
    }
    if detectors is not None:
        kwargs["detectors"] = detectors
    return RecordingProducingClosure(**kwargs)


class DeepAuditSeam:
    """Thin V1 deep-audit seam over an injected ``LLMDispatchPort`` (DIP).

    Holds the port TYPE (injected), never the concrete adapter. ``run`` is the
    minimal V1 surface: it dispatches one request and returns the recording the
    later (6.2) AST-grounding validator will consume. The AST logic is NOT built
    here.
    """

    def __init__(self, *, port: LLMDispatchPort) -> None:
        self._port = port

    def run(self, req: LLMDispatchInput) -> LLMRecording:
        """Dispatch one deep-audit request through the injected port."""
        return self._port.dispatch(req)
