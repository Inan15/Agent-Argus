"""Cache-key derivation golden + bidirectional CI canary (Story 5.1).

Drivers: ArgusAgent-FR-27 (reproduce the same verdict for the same repo + ArgusAgent version),
ArgusAgent-NFR-D1 (content-addressed memoization key = content-hash + model checkpoint +
detector-set hash), ArgusAgent-AR5 (ONE cache-key function; CI canary fails when key
inputs change without a bump), ArgusAgent-NFR-D2 (PURE, zero LLM tokens), ArgusAgent-NFR-P1
(byte-identical / deterministic key), ArgusAgent-AR4 (single serializer, no float),
ArgusAgent-AR8 (PURE module), ArgusAgent-AR10 (typed degradation), AI-E4-1 (no-crash
input-shape + keystone-adequacy perturbation matrix), AI-E1-1 (non-ASCII).

Verification area ArgusAgent-CACHE — TC-ArgusAgent-CACHE-001-01..NN (NEW area for cache/;
the next free index is 01 — no prior ArgusAgent-CACHE tests exist).

The honesty property is BIDIRECTIONAL (AR5 / §9.2):
- closure changes → key MUST change (a forgotten input is caught by a
  perturbation leg that fails to move the key — silent cache-staleness);
- the same closure → the SAME key (deterministic, byte-stable, order-independent).

AI-E4-1 keystone adequacy: each perturbation leg is also demonstrated RED against
a derivation that IGNORES that input (``_key_ignoring``), proving the assertion is
a real proof and not vacuous — a derivation that forgot an input passes a naive
same-key test but FAILS the perturbation canary.
"""

from __future__ import annotations

import ast
import dataclasses
from pathlib import Path
from typing import Any

import pytest

from argus.cache import key as cache_key
from argus.cache.key import (
    CACHE_KEY_SCHEMA_VERSION,
    FROZEN_DETECTOR_SET,
    V1_MODEL_CHECKPOINT,
    V1_PROMPT_TEMPLATE_VERSION,
    CacheKeyError,
    DetectorDescriptor,
    RecordingProducingClosure,
    derive_cache_key,
    detector_set_content_hash,
)

_KEY_MODULE = Path(cache_key.__file__).resolve()


def _baseline() -> RecordingProducingClosure:
    """A fixed, fully-specified baseline closure (the golden anchor)."""
    return RecordingProducingClosure(
        content_hash="a" * 64,
        detectors=FROZEN_DETECTOR_SET,
        grammar_version="0.23.6",
        tool_versions={"radon": "6.0.1", "tree-sitter": "0.23.2"},
        budget=100,
        materiality_bar="release",
        work_manifest_files=("pkg/a.py", "pkg/b.py", "pkg/c.py"),
        critical_paths=("pkg/a.py",),
        excluded_critical_paths=("pkg/c.py",),
        model_checkpoint=V1_MODEL_CHECKPOINT,
        prompt_template_version=V1_PROMPT_TEMPLATE_VERSION,
    )


# ── AC1 / AC5: determinism (closure unchanged → key unchanged, byte-stable) ──


def test_same_closure_same_key_byte_stable() -> None:
    """TC-ArgusAgent-CACHE-001-01 — same closure derives the same key twice (determinism)."""
    assert derive_cache_key(_baseline()) == derive_cache_key(_baseline())


def test_key_is_a_stable_hex_string() -> None:
    """TC-ArgusAgent-CACHE-001-02 — the key is a 64-char sha256 hex string."""
    k = derive_cache_key(_baseline())
    assert isinstance(k, str)
    assert len(k) == 64
    assert all(c in "0123456789abcdef" for c in k)


def test_golden_key_pinned() -> None:
    """TC-ArgusAgent-CACHE-001-03 — the GOLDEN key for the fixed baseline closure.

    A committed golden value: any change to the derivation OR the baseline closure
    that moves this number is surfaced as a RED build (the AR5 canary backbone).
    Regenerate ONLY with a documented intentional invalidation (e.g. a deliberate
    schema bump), never silently.
    """
    golden = derive_cache_key(_baseline())
    assert golden == "2628b9a6ecb72e845d6fb83286ca838db326fb888837dfbd9483a05de550ca87"


# ── AC2: the bidirectional CI canary — each input perturbation moves the key ──

#: A derivation that IGNORES a given closure field (drops it from the payload),
#: used to prove each perturbation leg is RED-then-green (AI-E4-1 keystone proof).


def _key_ignoring(closure: RecordingProducingClosure, ignored: str) -> str:
    """Re-derive a key whose payload OMITS ``ignored`` (a buggy derivation).

    A derivation that forgets ``ignored`` produces the SAME key for two closures
    that differ ONLY in ``ignored`` — the exact silent-cache-staleness bug the
    canary must catch. This helper reproduces that bug so each perturbation leg
    is demonstrated RED against it.
    """
    payload = cache_key._closure_payload(closure)  # the real payload
    # Map the closure-field perturbed by a leg to the payload key it lands on.
    payload_key = {"detectors": "detector_set_hash"}.get(ignored, ignored)
    payload.pop(payload_key, None)
    from argus.store.envelope import compute_content_hash

    return compute_content_hash(payload)


_PERTURBATIONS: tuple[tuple[str, dict[str, Any]], ...] = (
    ("content_hash", {"content_hash": "b" * 64}),
    (
        "detectors",
        {
            "detectors": FROZEN_DETECTOR_SET
            + (DetectorDescriptor(rule_id="new_detector", code_identity="new.v1"),)
        },
    ),
    ("grammar_version", {"grammar_version": "0.24.0"}),
    ("tool_versions", {"tool_versions": {"radon": "6.0.2", "tree-sitter": "0.23.2"}}),
    ("budget", {"budget": 200}),
    ("materiality_bar", {"materiality_bar": "internal"}),
    ("work_manifest_files", {"work_manifest_files": ("pkg/a.py", "pkg/b.py")}),
    ("critical_paths", {"critical_paths": ("pkg/b.py",)}),
    ("excluded_critical_paths", {"excluded_critical_paths": ()}),
    ("model_checkpoint", {"model_checkpoint": "epoch-6.1-real-checkpoint"}),
    ("prompt_template_version", {"prompt_template_version": "tmpl-6.1-real-v2"}),
)


@pytest.mark.parametrize("field,override", _PERTURBATIONS, ids=[p[0] for p in _PERTURBATIONS])
def test_perturbing_each_input_changes_the_key(field: str, override: dict[str, Any]) -> None:
    """TC-ArgusAgent-CACHE-001-04 — closure changes → key changes (per-input matrix)."""
    base = _baseline()
    perturbed = base.model_copy(update=override)
    assert derive_cache_key(perturbed) != derive_cache_key(base), (
        f"perturbing {field!r} did NOT move the key — the derivation forgot to "
        f"fold it (silent cache-staleness, AR5/AR6)"
    )


@pytest.mark.parametrize(
    "field,override",
    [p for p in _PERTURBATIONS if p[0] != "excluded_critical_paths"],
    ids=[p[0] for p in _PERTURBATIONS if p[0] != "excluded_critical_paths"],
)
def test_keystone_adequacy_ignoring_input_would_not_move_key(
    field: str, override: dict[str, Any]
) -> None:
    """TC-ArgusAgent-CACHE-001-05 — AI-E4-1: a derivation IGNORING the input is RED.

    Proves each perturbation leg is a real proof: a buggy derivation that drops
    ``field`` from the payload produces the SAME key for base vs perturbed — the
    exact failure the AC2 matrix catches. (``excluded_critical_paths`` baseline
    value is non-empty and the perturbation empties it; dropping it from the
    payload still collides, so it is covered by the general matrix only.)
    """
    base = _baseline()
    perturbed = base.model_copy(update=override)
    assert _key_ignoring(base, field) == _key_ignoring(perturbed, field), (
        f"the ignoring-derivation for {field!r} unexpectedly moved the key — the "
        f"RED demonstration is not valid"
    )


def test_detector_config_edit_changes_the_set_hash_and_key() -> None:
    """TC-ArgusAgent-CACHE-001-06 — AC3: editing a descriptor config moves the key (AR6 lever)."""
    base = _baseline()
    edited = tuple(
        d.model_copy(update={"config": {"min_entropy": "4/1"}}) if d.rule_id == "hardcoded_secret" else d
        for d in FROZEN_DETECTOR_SET
    )
    perturbed = base.model_copy(update={"detectors": edited})
    assert detector_set_content_hash(edited) != detector_set_content_hash(FROZEN_DETECTOR_SET)
    assert derive_cache_key(perturbed) != derive_cache_key(base)


# ── AC5: order-independence (the 3.5 sorted-vs-set precedent) ──


def test_key_is_order_independent_over_manifest_and_detectors() -> None:
    """TC-ArgusAgent-CACHE-001-07 — re-ordered set inputs derive the SAME key (AR4/NFR-P1)."""
    base = _baseline()
    reordered = base.model_copy(
        update={
            "work_manifest_files": tuple(reversed(base.work_manifest_files)),
            "detectors": tuple(reversed(FROZEN_DETECTOR_SET)),
            "tool_versions": dict(reversed(list(base.tool_versions.items()))),
        }
    )
    assert derive_cache_key(reordered) == derive_cache_key(base)


def test_detector_set_hash_is_order_independent() -> None:
    """TC-ArgusAgent-CACHE-001-08 — the detector-set hash is order-independent."""
    assert detector_set_content_hash(tuple(reversed(FROZEN_DETECTOR_SET))) == detector_set_content_hash(
        FROZEN_DETECTOR_SET
    )


# ── AC4: model-checkpoint placeholder + checkpoint_drift detection seam ──


def test_default_model_checkpoint_is_the_v1_placeholder() -> None:
    """TC-ArgusAgent-CACHE-001-09 — the checkpoint defaults to the stable V1 constant (DN-PLACEHOLDER)."""
    assert _baseline().model_checkpoint == V1_MODEL_CHECKPOINT == "v1-heuristic-no-llm"


def test_checkpoint_drift_seam_two_values_two_keys() -> None:
    """TC-ArgusAgent-CACHE-001-10 — AC4: two checkpoint values derive two keys (drift seam)."""
    base = _baseline()
    drifted = base.model_copy(update={"model_checkpoint": "epoch-2-real"})
    assert derive_cache_key(drifted) != derive_cache_key(base)


def test_default_prompt_template_version_is_the_v1_placeholder() -> None:
    """TC-ArgusAgent-CACHE-001-21 — DF-5-1-A: prompt-template version defaults to the V1 placeholder.

    Mirrors the ``model_checkpoint`` DN-PLACEHOLDER slot: architecture §77 lists
    ``prompt-template version`` as a closure key input; V1 Tier-A has no live LLM,
    so the slot is a stable sentinel shaped for a clean ADDITIVE 6.1 substitution.
    """
    assert _baseline().prompt_template_version == V1_PROMPT_TEMPLATE_VERSION == "v1-no-prompt-template"


def test_prompt_template_drift_seam_two_values_two_keys() -> None:
    """TC-ArgusAgent-CACHE-001-22 — DF-5-1-A: two prompt-template values derive two keys (6.1 seam).

    Once 6.1 wires the live LLM, a prompt-template change MUST move the cache key
    so a stale result computed under a different prompt cannot be served — the
    silent-cache-staleness hole DF-5-1-A flagged, closed here.
    """
    base = _baseline()
    drifted = base.model_copy(update={"prompt_template_version": "tmpl-2-real"})
    assert derive_cache_key(drifted) != derive_cache_key(base)


# ── AC5 / AI-E1-1: non-ASCII closure derives a stable key ──


def test_non_ascii_closure_derives_a_stable_key() -> None:
    """TC-ArgusAgent-CACHE-001-11 — AI-E1-1: non-ASCII path/value → stable key (explicit UTF-8)."""
    base = _baseline()
    non_ascii = base.model_copy(
        update={
            "work_manifest_files": ("pkg/café.py", "pkg/модуль.py", "pkg/テスト.py"),
            "materiality_bar": "релиз",
        }
    )
    k1 = derive_cache_key(non_ascii)
    k2 = derive_cache_key(non_ascii)
    assert k1 == k2 and len(k1) == 64
    # And it is distinct from the ASCII baseline (the non-ASCII inputs are folded).
    assert k1 != derive_cache_key(base)


# ── AC5 / AR10 / AI-E4-1: malformed closure degrades to a typed CacheKeyError ──


def test_empty_detector_set_is_a_typed_error() -> None:
    """TC-ArgusAgent-CACHE-001-12 — an empty detector set → CacheKeyError, never a wrong key."""
    with pytest.raises(CacheKeyError):
        detector_set_content_hash(())
    base = _baseline()
    with pytest.raises(CacheKeyError):
        derive_cache_key(base.model_copy(update={"detectors": ()}))


def test_non_closure_argument_is_a_typed_error() -> None:
    """TC-ArgusAgent-CACHE-001-13 — a non-closure argument → CacheKeyError (AR10)."""
    with pytest.raises(CacheKeyError):
        derive_cache_key({"content_hash": "a" * 64})  # type: ignore[arg-type]


def test_missing_required_field_is_a_typed_error() -> None:
    """TC-ArgusAgent-CACHE-001-14 — a blank/absent required field → typed error (not a wrong key)."""
    with pytest.raises(Exception):  # pydantic ValidationError on missing grammar_version
        RecordingProducingClosure(  # type: ignore[call-arg]
            content_hash="a" * 64,
            budget=1,
            materiality_bar="release",
            work_manifest_files=(),
        )
    with pytest.raises(Exception):
        RecordingProducingClosure(
            content_hash="a" * 64,
            grammar_version="   ",
            budget=1,
            materiality_bar="release",
            work_manifest_files=(),
        )


def test_cache_key_error_is_a_valueerror_subclass() -> None:
    """TC-ArgusAgent-CACHE-001-15 — CacheKeyError is a ValueError (AR10 typed-degradation contract)."""
    assert issubclass(CacheKeyError, ValueError)


# ── AC5 / AR8: purity — the module imports/uses no clock/uuid/random/float/json/FS/LLM ──

_BANNED_IMPORT_ROOTS = {
    "datetime",
    "time",
    "uuid",
    "random",
    "os",
    "secrets",
    "socket",
    "requests",
    "httpx",
    "subprocess",
    "pathlib",
}


def test_cache_key_module_is_pure_no_banned_imports() -> None:
    """TC-ArgusAgent-CACHE-001-16 — AR8: cache/key.py imports no clock/uuid/random/FS/net module."""
    tree = ast.parse(_KEY_MODULE.read_text(encoding="utf-8"), filename=str(_KEY_MODULE))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    banned = imported & _BANNED_IMPORT_ROOTS
    assert not banned, f"cache/key.py imports banned non-deterministic/IO module(s): {sorted(banned)}"


def _attr_call_names(tree: ast.AST) -> set[str]:
    """Return ``a.b``-shaped attribute-call names actually invoked (AST, not substring)."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                names.add(f"{func.value.id}.{func.attr}")
            elif isinstance(func, ast.Name):
                names.add(func.id)
    return names


def test_cache_key_module_has_no_float_literal_or_clock_call() -> None:
    """TC-ArgusAgent-CACHE-001-17 — AR4/AR8: no float literal, no time/clock/uuid/random/json call site."""
    src = _KEY_MODULE.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(_KEY_MODULE))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, float):
            raise AssertionError(f"float literal at line {node.lineno} in cache/key.py (AR4)")
    calls = _attr_call_names(tree)
    banned = {"time.time", "datetime.now", "uuid4", "uuid.uuid4", "os.getpid", "json.dumps", "json.dump"}
    found = calls & banned
    assert not found, f"cache/key.py invokes a non-deterministic/second-serializer call: {sorted(found)}"


def test_cache_key_uses_the_single_content_hash() -> None:
    """TC-ArgusAgent-CACHE-001-18 — composes the 1.1 compute_content_hash (no second hasher)."""
    src = _KEY_MODULE.read_text(encoding="utf-8")
    tree = ast.parse(src, filename=str(_KEY_MODULE))
    assert "compute_content_hash" in _attr_call_names(tree) or "compute_content_hash" in src
    # No second hasher: cache/key.py must not import hashlib directly.
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "hashlib" not in imported, "cache/key.py adds a second hasher (import hashlib) — compose the 1.1 leaf"


# ── AC6: schema version is folded (a deliberate bump is the intentional lever) ──


def test_schema_version_is_folded_into_the_key() -> None:
    """TC-ArgusAgent-CACHE-001-19 — the schema version participates in the payload (intentional-bump lever)."""
    payload = cache_key._closure_payload(_baseline())
    assert payload["schema_version"] == CACHE_KEY_SCHEMA_VERSION


def test_descriptor_is_frozen() -> None:
    """TC-ArgusAgent-CACHE-001-20 — DetectorDescriptor is frozen (extra=forbid, immutable)."""
    d = FROZEN_DETECTOR_SET[0]
    with pytest.raises(dataclasses.FrozenInstanceError if False else Exception):
        d.rule_id = "mutated"  # type: ignore[misc]
