"""THE single PURE cache-key derivation over the full recording-producing closure.

Drivers: ArgusAgent-FR-27 (reproduce the same verdict for the same repo + ArgusAgent version
— the cache key is the reproducibility FINGERPRINT the 5.2 store rests on),
ArgusAgent-NFR-D1 (content-addressed memoization key = content-hash + model checkpoint
+ detector-set hash — the central driver), ArgusAgent-AR5 (ONE cache-key function;
the key is the full recording-producing closure; a mid-run checkpoint drift →
``checkpoint_drift`` → abort/re-audit; the CI canary fails when key inputs change
without a bump), ArgusAgent-NFR-D2 (PURE derivation, zero LLM tokens), ArgusAgent-NFR-D3
(content hashes cover the canonical payload only), ArgusAgent-NFR-P1 (byte-identical /
deterministic key across environments), ArgusAgent-AR4 (single serializer, no float,
clock-free / uuid-free / random-free), ArgusAgent-AR8 (PURE module — no I/O, clock,
LLM), ArgusAgent-NFR-M1 (≤1200-line files), ArgusAgent-AR10 (a malformed closure input
degrades to a typed error, never an uncaught raise that yields a wrong key).

Why this module exists (the determinism keystone — architecture CC #1)
----------------------------------------------------------------------
The KEY is the determinism keystone, NOT the verdict math. A memoization cache
hit may ONLY ever return a result produced by an IDENTICAL recording-producing
closure — so reproducibility never silently serves a result computed under a
different detector, grammar, config, or model. This module folds EVERY
determinism-relevant input that determines a recording's output into one
deterministic key:

- the **content-hash** of the audited unit (REUSE the 1.1 ``compute_content_hash``);
- the **detector-set content-hash** — a CONTENT hash of the enabled detector SET
  (code + config), NOT a human ``argus_version`` string (DN-DETECTORSET / AR5/R3);
- the **tree-sitter grammar version** (REAL, recorded by 1.4) + **tool versions**;
- the **budget / materiality** config (recorded by 1.7 / 3.1);
- the **work-manifest scope** (the 2.4 manifest membership + 2.3 critical
  designation);
- the **model checkpoint** — a STABLE, TESTABLE V1 placeholder shaped for a clean
  ADDITIVE Epic-6 Story 6.1 substitution of a real captured value (DN-PLACEHOLDER);
- the **prompt-template version** — a STABLE, TESTABLE V1 placeholder for the SAME
  reason as the model checkpoint (architecture §77 enumerates ``prompt-template
  version`` among the closure key inputs). In V1 Tier-A there is NO live LLM, so
  there is no prompt template to fold today; the slot is a fixed sentinel shaped
  for a clean ADDITIVE Epic-6 Story 6.1 substitution of the real captured
  prompt-template version. Carrying the slot NOW (rather than adding it at 6.1)
  closes the forward-coupling silent-staleness hole DF-5-1-A flagged: when 6.1
  wires the live LLM, a prompt-template change moves the cache key (no stale
  result computed under a different prompt can be served). Do NOT build 6.1 here.

ONE serializer, ONE content-hash (AR4/AR5)
------------------------------------------
NFR-P1 (byte-identical) dies the day a second ``json.dumps`` or second hasher
appears. This module COMPOSES the single canonical serializer
(``store/canonical.py::dumps_bytes``) and the single content-hash
(``store/envelope.py::compute_content_hash`` = sha256 over ``dumps_bytes``). It
introduces NO second serializer and NO second hasher.

PURE (AR8) — no I/O, no clock, no LLM, no float, no uuid/random/os.getpid. The
tool/grammar-version PROBING (an impure ``importlib.metadata`` read) is done by
the impure caller and passed IN as recorded strings; this module never probes.

The ``checkpoint_drift`` detection SEAM (AR5 / AC4)
---------------------------------------------------
Two DIFFERENT ``model_checkpoint`` values derive DIFFERENT keys — so a
mixed-checkpoint result can never be served as a hit. The LIVE mid-run drift
capture + the ``checkpoint_drift`` finding's pipeline wiring + abort/re-audit
loop are DEFERRED to Epic-6 Story 6.1 (do NOT build here).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from argus.store import canonical
from argus.store.envelope import compute_content_hash

__all__ = [
    "CACHE_KEY_SCHEMA_VERSION",
    "V1_MODEL_CHECKPOINT",
    "V1_PROMPT_TEMPLATE_VERSION",
    "CacheKeyError",
    "DetectorDescriptor",
    "FROZEN_DETECTOR_SET",
    "RecordingProducingClosure",
    "detector_set_content_hash",
    "derive_cache_key",
]

# Cache-key payload schema version (additive-only; a bump deliberately moves the
# key — the documented intentional-invalidation lever for a key-shape change).
# Bumped 1 → 2 (story 5.1 fix iter-1, DF-5-1-A): the prompt_template_version slot
# was added to the closure payload, which deliberately moves every derived key
# (the golden was regenerated accordingly).
CACHE_KEY_SCHEMA_VERSION = "2"

# DN-PLACEHOLDER — the stable, testable V1 model-checkpoint constant. V1 Tier-A's
# deep path is heuristic/claim-proxy with NO live LLM, so the checkpoint input is
# this fixed sentinel occupying a key slot shaped for a clean ADDITIVE Epic-6
# Story 6.1 substitution of a real captured API-response checkpoint value. Two
# different checkpoint values derive two different keys (the checkpoint_drift
# detection seam). Do NOT build 6.1 here; do NOT block on it.
V1_MODEL_CHECKPOINT = "v1-heuristic-no-llm"

# DN-PLACEHOLDER (prompt-template, DF-5-1-A) — the stable, testable V1
# prompt-template-version constant. Architecture §77 enumerates ``prompt-template
# version`` among the recording-producing-closure key inputs. V1 Tier-A's deep
# path is heuristic/claim-proxy with NO live LLM, so there is no prompt template
# to fold today; this fixed sentinel occupies a key slot shaped for a clean
# ADDITIVE Epic-6 Story 6.1 substitution of the real captured prompt-template
# version. Two different prompt-template values derive two different keys, so once
# 6.1 wires the live LLM a prompt-template change cannot serve a stale hit. Do NOT
# build 6.1 here; do NOT block on it.
V1_PROMPT_TEMPLATE_VERSION = "v1-no-prompt-template"


class CacheKeyError(ValueError):
    """Raised when a closure cannot be turned into a faithful cache key (AR10).

    A ``ValueError`` subclass — the typed degradation a malformed closure
    (a missing grammar version, an empty detector set, an absent required field)
    routes to, NEVER an uncaught raise that would yield a silently-wrong key.
    """


class DetectorDescriptor(BaseModel):
    """One enabled detector's identity for the detector-set content hash (DN-DETECTORSET).

    The detector-set hash is taken over a DECLARED, frozen, enumerated set of
    these descriptors — NOT a hand-written ``argus_version`` string. Each descriptor
    carries its ``rule_id`` (the producer token), a ``code_identity`` token (a
    stable identifier for the detector's code path — bumped when its logic
    materially changes), and its ``config`` (a JSON-object of the detector's
    determinism-relevant settings). Editing any field CHANGES the set hash →
    CHANGES the derived key (the AR6 invalidation lever Story 5.3 rides).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str = Field(..., min_length=1, description="Detector producer/rule token.")
    code_identity: str = Field(
        ..., min_length=1, description="Stable code-path identity token (bumped on logic change)."
    )
    config: dict[str, Any] = Field(
        default_factory=dict, description="Determinism-relevant detector config (canonical leaves only)."
    )


# The DECLARED, FROZEN, ENUMERATED detector-descriptor set (DN-DETECTORSET / AR5 /
# AR6). There is NO central detector registry today (rule_ids are scattered
# constants); this tuple is the canonical single source of "which detectors are
# enabled" for the key. Adding/removing a descriptor, or editing one's config /
# code_identity, MOVES the detector-set content hash → MOVES the key (the 5.3
# invalidation lever). The rule_ids mirror the live detector constants:
#   detectors/secret_scan.py::RULE_HARDCODED_SECRET = "hardcoded_secret"
#   detectors/tool_runner.py::RULE_TOOL_FAILURE = "tool_failure"
#   detectors/tool_runner.py::RULE_TRACEABILITY_NOT_ESTABLISHABLE = "traceability_not_establishable"
#   detectors/vacuous_test.py::RULE_HEURISTIC = "vacuous_test_heuristic"
#   detectors/vacuous_test.py::RULE_AST = "vacuous_test_ast"
FROZEN_DETECTOR_SET: tuple[DetectorDescriptor, ...] = (
    DetectorDescriptor(rule_id="hardcoded_secret", code_identity="secret_scan.v1"),
    DetectorDescriptor(rule_id="tool_failure", code_identity="tool_runner.v1"),
    DetectorDescriptor(rule_id="traceability_not_establishable", code_identity="tool_runner.v1"),
    DetectorDescriptor(rule_id="vacuous_test_heuristic", code_identity="vacuous_test.heuristic.v1"),
    DetectorDescriptor(rule_id="vacuous_test_ast", code_identity="vacuous_test.ast.v1"),
)


def _descriptor_payload(descriptor: DetectorDescriptor) -> dict[str, Any]:
    return {
        "rule_id": descriptor.rule_id,
        "code_identity": descriptor.code_identity,
        "config": descriptor.config,
    }


def detector_set_content_hash(descriptors: tuple[DetectorDescriptor, ...]) -> str:
    """sha256 hex over the canonical bytes of the enabled detector SET (DN-DETECTORSET).

    Order-independent: the descriptors are SORTED by ``(rule_id, code_identity)``
    before serialization so a re-ordered set yields the SAME hash (AR4/NFR-P1).
    Composes the SINGLE canonical serializer + content-hash (no second hasher).
    An empty set is a malformed closure (a key over zero detectors is a lie) →
    ``CacheKeyError`` (AR10).
    """
    if not descriptors:
        raise CacheKeyError(
            "detector set is empty — a cache key over zero detectors is not a "
            "faithful closure fingerprint (DN-DETECTORSET / AR5)"
        )
    ordered = sorted(
        (_descriptor_payload(d) for d in descriptors),
        key=lambda p: (p["rule_id"], p["code_identity"]),
    )
    try:
        return compute_content_hash({"detectors": ordered})
    except canonical.CanonicalSerializationError as exc:
        raise CacheKeyError(f"detector set is not canonically serializable: {exc}") from exc


class RecordingProducingClosure(BaseModel):
    """The full recording-producing closure the cache key fingerprints (AR5 / NFR-D1).

    Frozen + ``extra="forbid"`` — every determinism-relevant input that determines
    a recording's output, and ONLY those. The model carries no float (AR4); ratio-
    shaped inputs would be string/``Fraction``. The detector set is carried as the
    enumerated descriptors (the detector-set content hash is derived from them in
    :func:`derive_cache_key`, so the key is a faithful function of the actual
    descriptors, not a pre-computed string the caller could desync).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    content_hash: str = Field(
        ..., min_length=1, description="Content-hash of the audited unit (REUSE the 1.1 hash)."
    )
    detectors: tuple[DetectorDescriptor, ...] = Field(
        default=FROZEN_DETECTOR_SET,
        description="Enabled detector descriptor set (DN-DETECTORSET); hashed in derive_cache_key.",
    )
    grammar_version: str = Field(
        ..., min_length=1, description="Recorded tree-sitter-python grammar version (1.4)."
    )
    tool_versions: dict[str, str] = Field(
        default_factory=dict, description="Recorded pinned-tool versions (radon, etc.) — 'unknown' fallback ok."
    )
    budget: int = Field(..., ge=0, description="Recorded budget ceiling config (int credits — AR4).")
    materiality_bar: str = Field(..., min_length=1, description="Recorded materiality bar (3.1).")
    work_manifest_files: tuple[str, ...] = Field(
        ..., description="Work-manifest membership scope (2.4) — folded SORTED, order-independent."
    )
    critical_paths: tuple[str, ...] = Field(
        default=(), description="Operator-forced critical designation (2.3) — folded SORTED."
    )
    excluded_critical_paths: tuple[str, ...] = Field(
        default=(), description="Operator-excluded critical designation (2.3) — folded SORTED."
    )
    model_checkpoint: str = Field(
        default=V1_MODEL_CHECKPOINT,
        min_length=1,
        description="Model checkpoint (V1 placeholder; 6.1 substitutes a real captured value — DN-PLACEHOLDER).",
    )
    prompt_template_version: str = Field(
        default=V1_PROMPT_TEMPLATE_VERSION,
        min_length=1,
        description="Prompt-template version (V1 placeholder; 6.1 substitutes the real value — DF-5-1-A / §77).",
    )

    @field_validator(
        "grammar_version",
        "materiality_bar",
        "content_hash",
        "model_checkpoint",
        "prompt_template_version",
    )
    @classmethod
    def _non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must be a non-blank string")
        return value


def _closure_payload(closure: RecordingProducingClosure) -> dict[str, Any]:
    """Canonical, order-independent payload the cache key is taken over.

    Every set/list-shaped input is SORTED so the key is order-independent
    (AR4/NFR-P1, the 3.5 sorted-vs-set precedent). The detector set is folded as
    its CONTENT HASH (DN-DETECTORSET), not the raw descriptors, so the closure
    payload composes the single content-hash rather than re-embedding mutable
    structure.
    """
    return {
        "schema_version": CACHE_KEY_SCHEMA_VERSION,
        "content_hash": closure.content_hash,
        "detector_set_hash": detector_set_content_hash(closure.detectors),
        "grammar_version": closure.grammar_version,
        "tool_versions": {k: closure.tool_versions[k] for k in sorted(closure.tool_versions)},
        "budget": closure.budget,
        "materiality_bar": closure.materiality_bar,
        "work_manifest_files": sorted(closure.work_manifest_files),
        "critical_paths": sorted(closure.critical_paths),
        "excluded_critical_paths": sorted(closure.excluded_critical_paths),
        "model_checkpoint": closure.model_checkpoint,
        "prompt_template_version": closure.prompt_template_version,
    }


def derive_cache_key(closure: RecordingProducingClosure) -> str:
    """Derive the deterministic cache key for a fully-specified closure (AR5 / NFR-D1).

    Folds ALL closure inputs — content-hash + detector-set content-hash +
    grammar/tool versions + budget/materiality + work-manifest scope + model
    checkpoint + prompt-template version — into a single sha256 hex key by
    composing the SINGLE canonical
    serializer + content-hash (NO second ``json.dumps``, NO second hasher). PURE:
    no I/O, no clock, no uuid/random, no float (AR4/AR8/NFR-D2). The SAME closure
    ALWAYS yields the SAME key (byte-stable + order-independent); ANY input change
    moves the key (the CI-canary honesty property). A malformed closure degrades
    to :class:`CacheKeyError` (AR10).
    """
    if not isinstance(closure, RecordingProducingClosure):
        raise CacheKeyError(
            f"closure must be a RecordingProducingClosure, got {type(closure).__name__!r}"
        )
    try:
        payload = _closure_payload(closure)
        return compute_content_hash(payload)
    except canonical.CanonicalSerializationError as exc:
        raise CacheKeyError(f"closure is not canonically serializable: {exc}") from exc
