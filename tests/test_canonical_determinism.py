"""Determinism golden tests for the ArgusAgent canonical serializer + envelope.

Verification area ArgusAgent-STORE. Covers AC1/AC3/AC4/AC5/AC6 of story 1.1:
round-trip, key-order independence, the FROZEN golden canonical string + golden
content_hash (cross-host byte-identical invariant, NFR-P1), forbidden-input
rejection (NFR-P1 / AR4), Decimal/Fraction stable encoding, the NFR-D3 hash
exclusion of volatile fields, prev-hash chaining (NFR-A1) and additive-only
schema invariance (NFR-M2).

These are PURE-function golden tests — zero tokens (NFR-D2), no temp files, no
clock for the modules under test. The golden constants are recorded so a future
byte-drift fails loudly.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction

import pytest

from argus.store import canonical
from argus.store.envelope import (
    GENESIS_PREV_HASH,
    Envelope,
    EnvelopeWriter,
    compute_content_hash,
)

# ── FROZEN GOLDEN FIXTURE (do not edit without intent — downstream stories
#    fold over these exact bytes; a change is a cross-host reproducibility break)
GOLDEN_FIXTURE: dict = {
    "b": True,
    "n": None,
    "nums": [1, 2, 3],
    "nested": {"z": "last", "a": "first"},
    "ratio": Decimal("0.50"),
    "text": "héllo",
}
GOLDEN_CANONICAL = (
    '{"b":true,"n":null,"nested":{"a":"first","z":"last"},'
    '"nums":[1,2,3],"ratio":"0.5","text":"héllo"}\n'
)
GOLDEN_CONTENT_HASH = "e92e7a08d90c60a840baf8e3e1de2870138db158df0095e2269cb734d1c1352b"


class TestCanonicalSerializer:
    """TC-ArgusAgent-STORE-001-01..09 — the single serializer (AC1/AC3)."""

    def test_round_trip_primitives(self) -> None:
        payload = {"a": 1, "b": "x", "c": True, "d": None, "e": [1, 2], "f": {"g": 3}}
        assert canonical.loads(canonical.dumps(payload)) == payload

    def test_exact_kwargs_compact_and_sorted_and_newline_terminated(self) -> None:
        out = canonical.dumps({"b": 1, "a": 2})
        assert out == '{"a":2,"b":1}\n'  # sorted keys, compact separators, trailing \n

    def test_non_ascii_not_escaped(self) -> None:
        assert canonical.dumps({"k": "café"}) == '{"k":"café"}\n'

    def test_key_order_independent(self) -> None:
        d1 = {"a": 1, "b": 2, "c": 3}
        d2 = {"c": 3, "b": 2, "a": 1}
        assert canonical.dumps(d1) == canonical.dumps(d2)

    def test_dumps_bytes_is_utf8_of_dumps(self) -> None:
        payload = {"k": "héllo"}
        assert canonical.dumps_bytes(payload) == canonical.dumps(payload).encode("utf-8")

    def test_golden_canonical_string_frozen(self) -> None:
        assert canonical.dumps(GOLDEN_FIXTURE) == GOLDEN_CANONICAL

    def test_loads_accepts_bytes(self) -> None:
        assert canonical.loads(canonical.dumps_bytes({"a": 1})) == {"a": 1}


class TestForbiddenInputs:
    """TC-ArgusAgent-STORE-001-10..16 — forbidden non-deterministic inputs (AC3)."""

    def test_reject_float(self) -> None:
        with pytest.raises(canonical.CanonicalSerializationError) as ei:
            canonical.dumps({"score": 0.5})
        assert "float" in str(ei.value)
        assert "$.score" in str(ei.value)

    def test_reject_float_nested_in_list(self) -> None:
        with pytest.raises(canonical.CanonicalSerializationError) as ei:
            canonical.dumps({"xs": [1, 2, 3.0]})
        assert "$.xs[2]" in str(ei.value)

    def test_reject_datetime(self) -> None:
        import datetime

        with pytest.raises(canonical.CanonicalSerializationError) as ei:
            canonical.dumps({"t": datetime.datetime(2026, 1, 1)})
        assert "wall-clock" in str(ei.value)

    def test_reject_date(self) -> None:
        import datetime

        with pytest.raises(canonical.CanonicalSerializationError):
            canonical.dumps({"d": datetime.date(2026, 1, 1)})

    def test_reject_uuid(self) -> None:
        import uuid

        with pytest.raises(canonical.CanonicalSerializationError) as ei:
            canonical.dumps({"id": uuid.uuid4()})
        assert "uuid" in str(ei.value).lower()

    def test_reject_set(self) -> None:
        with pytest.raises(canonical.CanonicalSerializationError) as ei:
            canonical.dumps({"s": {1, 2, 3}})
        assert "set" in str(ei.value).lower()

    def test_reject_frozenset(self) -> None:
        with pytest.raises(canonical.CanonicalSerializationError):
            canonical.dumps({"s": frozenset({1, 2})})

    def test_reject_non_string_dict_key(self) -> None:
        with pytest.raises(canonical.CanonicalSerializationError) as ei:
            canonical.dumps({1: "a"})
        assert "key" in str(ei.value).lower()

    def test_reject_arbitrary_object(self) -> None:
        class Foo:
            pass

        with pytest.raises(canonical.CanonicalSerializationError):
            canonical.dumps({"x": Foo()})

    def test_error_is_valueerror_subclass(self) -> None:
        assert issubclass(canonical.CanonicalSerializationError, ValueError)


class TestExactNumericEncoding:
    """TC-ArgusAgent-STORE-001-20..26 — Decimal/Fraction stable string encoding (AC3)."""

    def test_decimal_normalized_string(self) -> None:
        assert canonical.dumps({"r": Decimal("0.50")}) == '{"r":"0.5"}\n'

    def test_decimal_integer_value(self) -> None:
        assert canonical.dumps({"r": Decimal("3")}) == '{"r":"3"}\n'

    def test_decimal_no_scientific_notation(self) -> None:
        # A value that Decimal.normalize() would otherwise render with an exponent.
        out = canonical.dumps({"r": Decimal("1E+2")})
        assert out == '{"r":"100"}\n'

    def test_decimal_high_precision_stable(self) -> None:
        assert canonical.dumps({"r": Decimal("0.333333333333")}) == '{"r":"0.333333333333"}\n'

    def test_reject_non_finite_decimal(self) -> None:
        with pytest.raises(canonical.CanonicalSerializationError):
            canonical.dumps({"r": Decimal("NaN")})
        with pytest.raises(canonical.CanonicalSerializationError):
            canonical.dumps({"r": Decimal("Infinity")})

    def test_fraction_numerator_denominator_form(self) -> None:
        assert canonical.dumps({"r": Fraction(1, 3)}) == '{"r":"1/3"}\n'

    def test_fraction_reduced(self) -> None:
        assert canonical.dumps({"r": Fraction(2, 4)}) == '{"r":"1/2"}\n'


class TestEnvelope:
    """TC-ArgusAgent-STORE-001-30..39 — content-hashed envelope (AC4/AC5)."""

    def test_content_hash_golden_frozen(self) -> None:
        assert compute_content_hash(GOLDEN_FIXTURE) == GOLDEN_CONTENT_HASH

    def test_build_sets_content_hash_over_payload(self) -> None:
        payload = {"a": 1}
        env = EnvelopeWriter.build(
            payload, schema_version="1", producer="test", run_id="r1", created_at="t1"
        )
        assert env.content_hash == compute_content_hash(payload)

    def test_genesis_prev_hash_default(self) -> None:
        env = EnvelopeWriter.build({"a": 1}, schema_version="1", producer="test")
        assert env.prev_hash == GENESIS_PREV_HASH
        assert GENESIS_PREV_HASH == "0" * 64

    def test_argus_version_sourced_from_constant(self) -> None:
        from argus import __version__

        env = EnvelopeWriter.build({"a": 1}, schema_version="1", producer="test")
        assert env.argus_version == __version__

    def test_content_hash_excludes_volatile_fields(self) -> None:
        # AC5 / NFR-D3: same payload, different run_id/created_at → identical hash.
        env_a = EnvelopeWriter.build(
            {"x": 1}, schema_version="1", producer="p", run_id="run-A", created_at="2026-01-01"
        )
        env_b = EnvelopeWriter.build(
            {"x": 1}, schema_version="1", producer="p", run_id="run-B", created_at="2099-12-31"
        )
        assert env_a.content_hash == env_b.content_hash
        assert (env_a.run_id, env_a.created_at) != (env_b.run_id, env_b.created_at)

    def test_prev_hash_chains(self) -> None:
        # NFR-A1: B chains to A.
        env_a = EnvelopeWriter.build({"a": 1}, schema_version="1", producer="p")
        env_b = EnvelopeWriter.build(
            {"b": 2}, schema_version="1", producer="p", prev_hash=env_a.content_hash
        )
        assert env_b.prev_hash == env_a.content_hash

    def test_envelope_is_frozen(self) -> None:
        env = EnvelopeWriter.build({"a": 1}, schema_version="1", producer="p")
        with pytest.raises(Exception):
            env.content_hash = "tampered"  # type: ignore[misc]

    def test_two_independent_invocations_byte_identical(self) -> None:
        # AC5: simulated cross-host — two independent serializer invocations.
        assert canonical.dumps_bytes(GOLDEN_FIXTURE) == canonical.dumps_bytes(dict(GOLDEN_FIXTURE))
        assert compute_content_hash(GOLDEN_FIXTURE) == GOLDEN_CONTENT_HASH

    def test_additive_optional_field_does_not_change_hash(self) -> None:
        # NFR-M2: the hash is over the payload only, so an envelope-level optional
        # field (run_id/created_at present vs absent) never changes content_hash.
        env_bare = EnvelopeWriter.build({"x": 1}, schema_version="1", producer="p")
        env_rich = EnvelopeWriter.build(
            {"x": 1}, schema_version="2", producer="p", run_id="r", created_at="t"
        )
        assert env_bare.content_hash == env_rich.content_hash

    def test_envelope_round_trips_through_canonical_serializer(self) -> None:
        env = EnvelopeWriter.build({"x": 1}, schema_version="1", producer="p", run_id="r")
        as_json = canonical.dumps(env.model_dump())
        restored = canonical.loads(as_json)
        assert Envelope(**restored) == env
