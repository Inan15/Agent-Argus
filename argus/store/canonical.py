"""THE single canonical JSON serializer for every ``.argus/`` artifact.

Drivers: ArgusAgent-NFR-P1 (byte-identical on-disk state across hosts), ArgusAgent-NFR-D3
(hashes cover the canonical payload only), AR4 (single canonical serializer),
AR10 (typed failure, never an uncaught raise / silent coercion).

Why this module exists
----------------------
NFR-P1 (sequential output byte-identical to parallel, across hosts) dies the
day a second ``json.dumps`` appears anywhere in an ``.argus/`` write path with
different kwargs. This module is the ONE choke point: every artifact's JSON is
produced by exactly::

    json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

plus a single trailing ``\\n``, encoded UTF-8. The no-second-serializer test
(``tests/argus/test_canonical_single_serializer.py``) is the durable enforcement
that keeps it the only entry point.

Determinism contract (the byte-diff landmine defenses)
------------------------------------------------------
The following are FORBIDDEN as leaf values anywhere in a payload routed toward
a write, because they are non-reproducible across hosts/runs and would silently
break NFR-P1/D1:

- ``float`` — binary floats are not byte-stable across platforms; ratios/scores
  MUST be supplied as fixed-precision ``Decimal`` or exact ``Fraction``.
- ``datetime`` / ``date`` / ``time`` — wall-clock leakage.
- ``uuid.UUID`` — random/clock-derived identity.
- ``set`` / ``frozenset`` — iteration order is not deterministic.

A payload containing any of these (or any other non-JSON-primitive leaf) raises
``CanonicalSerializationError`` (a ``ValueError`` subclass) naming the offending
path/type BEFORE any bytes are produced. The serializer never silently coerces.

Decimal / Fraction encoding (FROZEN — golden-tested, do not change)
------------------------------------------------------------------
``Decimal`` and ``Fraction`` are the ONLY accepted numeric forms for
ratios/scores. They are encoded to a deterministic STRING form (never a binary
float) so the same value serializes byte-identically on every host:

- ``Decimal``  → ``format(value.normalize(), 'f')`` (plain decimal notation,
  no exponent, trailing-zero-normalized). NaN / Infinity are rejected.
- ``Fraction`` → ``f"{value.numerator}/{value.denominator}"`` (always reduced
  by ``Fraction`` itself; sign carried on the numerator).

The validator rewrites these leaves to their string form and then the standard
``json.dumps`` runs over a tree of JSON primitives only.
"""

from __future__ import annotations

import datetime as _datetime
import json
import uuid as _uuid
from decimal import Decimal
from fractions import Fraction
from typing import Any

__all__ = [
    "CanonicalSerializationError",
    "dumps",
    "dumps_bytes",
    "loads",
    "canonicalize",
]


class CanonicalSerializationError(ValueError):
    """Raised when a payload cannot be canonically/deterministically serialized.

    A ``ValueError`` subclass (AR10) — the typed failure a write path catches
    instead of emitting non-canonical bytes or silently coercing a value.
    """


def _encode_decimal(value: Decimal, path: str) -> str:
    if not value.is_finite():
        raise CanonicalSerializationError(
            f"non-finite Decimal at {path}: {value!r} (NaN/Infinity forbidden)"
        )
    return format(value.normalize(), "f")


def _encode_fraction(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def _reject(value: Any, path: str) -> None:
    raise CanonicalSerializationError(
        f"forbidden non-deterministic value at {path}: type "
        f"{type(value).__name__!r} is not canonically serializable"
    )


def canonicalize(payload: Any, _path: str = "$") -> Any:
    """Return a JSON-primitive-only mirror of ``payload``.

    Walks the payload depth-first. Rejects every forbidden non-deterministic
    leaf (``float``/``datetime``/``date``/``time``/``UUID``/``set``/
    ``frozenset`` and any non-JSON-primitive object) and rewrites the accepted
    ``Decimal``/``Fraction`` leaves to their frozen string form. Pure — no I/O,
    no clock, no mutation of the input.
    """
    if payload is None:
        return None
    # bool MUST be checked before int (bool is an int subclass); both are allowed.
    if isinstance(payload, bool):
        return payload
    if isinstance(payload, str):
        return payload
    if isinstance(payload, int):  # bool already returned above
        return payload

    # ── Accepted exact-numeric forms → deterministic string ──
    if isinstance(payload, Decimal):
        return _encode_decimal(payload, _path)
    if isinstance(payload, Fraction):
        return _encode_fraction(payload)

    # ── Explicitly forbidden leaves (named for the error message) ──
    if isinstance(payload, float):
        raise CanonicalSerializationError(
            f"forbidden float at {_path}: {payload!r} — supply ratios/scores as "
            f"Decimal or Fraction (floats are an NFR-P1 byte-diff landmine)"
        )
    if isinstance(payload, (_datetime.datetime, _datetime.date, _datetime.time)):
        raise CanonicalSerializationError(
            f"forbidden wall-clock value at {_path}: type "
            f"{type(payload).__name__!r} — clocks are non-deterministic"
        )
    if isinstance(payload, _uuid.UUID):
        raise CanonicalSerializationError(
            f"forbidden uuid.UUID at {_path}: {payload!s} — uuids are "
            f"non-deterministic; use a content-derived identifier"
        )
    if isinstance(payload, (set, frozenset)):
        raise CanonicalSerializationError(
            f"forbidden {type(payload).__name__} at {_path}: set iteration order "
            f"is non-deterministic — use a sorted list"
        )

    # ── Containers (recurse) ──
    if isinstance(payload, dict):
        out: dict[str, Any] = {}
        for key, val in payload.items():
            if not isinstance(key, str):
                raise CanonicalSerializationError(
                    f"non-string dict key at {_path}: {key!r} "
                    f"(type {type(key).__name__!r}) — JSON object keys must be str"
                )
            out[key] = canonicalize(val, f"{_path}.{key}")
        return out
    if isinstance(payload, (list, tuple)):
        return [canonicalize(item, f"{_path}[{i}]") for i, item in enumerate(payload)]

    # ── Anything else is a non-JSON-primitive leaf ──
    _reject(payload, _path)
    return None  # unreachable; keeps type-checkers happy


def dumps(payload: Any) -> str:
    """Canonically serialize ``payload`` to a ``\\n``-terminated JSON string.

    Validates + rewrites via :func:`canonicalize`, then emits exactly
    ``json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False)``
    with a single trailing newline. Raises :class:`CanonicalSerializationError`
    on any forbidden value (never silently coerces).
    """
    safe = canonicalize(payload)
    return json.dumps(safe, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def dumps_bytes(payload: Any) -> bytes:
    """UTF-8 bytes of :func:`dumps` — the single encode point.

    Hashing and writing share these exact bytes so a ``content_hash`` is taken
    over the very bytes that hit disk (single source of truth, NFR-D3).
    """
    return dumps(payload).encode("utf-8")


def loads(text: str | bytes) -> Any:
    """Thin ``json.loads`` wrapper for round-trip + reader reuse.

    Decoding is symmetric with :func:`dumps` for all supported inputs
    (``loads(dumps(x)) == x``). Note: ``Decimal``/``Fraction`` inputs round-trip
    back as their canonical STRING form by design (they are stored as strings).
    """
    if isinstance(text, bytes):
        text = text.decode("utf-8")
    return json.loads(text)
