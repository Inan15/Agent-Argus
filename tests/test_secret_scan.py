"""Hardcoded-secret detector + producer-side redaction (Story 2.5, AC1-5/7/8).

Verification area ArgusAgent-SECRET (TC-ArgusAgent-SECRET-001-NN). Covers AC1 detection (each
regex family hits its planted pattern; the entropy threshold flags a high-entropy
literal + does NOT flag a short / low-entropy token; deterministic finding set +
stable value-independent ids), AC2/AC3 producer-side redaction (the value is
absent from every emitted field; ``SecretFindingEvidence`` has no value field; the
masked indicator + length + kind are present; the ``recording_id`` is
value-independent), AC4 the locator-or-reject finding via the 1.5 builder
(``ast_span`` populated in a definition), AC5 the grade/fold, AC7 purity / frozen /
no-``float`` / typed-error (no secret in message) / single serializer, and the
AI-E1-1 non-ASCII file path + non-ASCII secret value.

The pure-logic cases construct an ``AstIndexEntry`` directly (no tree-sitter); the
detector core is a pure function over (source text + the 1.4 entry).
"""

from __future__ import annotations

from fractions import Fraction

import pytest
from pydantic import ValidationError

from argus.detectors.secret_scan import (
    MIN_ENTROPY_TOKEN_LENGTH,
    RULE_HARDCODED_SECRET,
    SecretFindingEvidence,
    SecretScanDetector,
    SecretScanError,
)
from argus.index.ast_index import AstIndexEntry, Definition
from argus.ledger.coverage_ledger import CoverageDepth
from argus.store import canonical


def _entry(*, file_path="src/config.py", definitions=()) -> AstIndexEntry:
    return AstIndexEntry(
        file_path=file_path,
        ast_eligible=True,
        definitions=tuple(definitions),
        edges=(),
    )


def _run(source: str, *, file_path="src/config.py", definitions=()):
    return SecretScanDetector().run(
        file_path=file_path,
        source=source,
        ast_entry=_entry(file_path=file_path, definitions=definitions),
    )


# ── AC1 — detection (regex families + entropy) ──────────────────────────────


def test_aws_access_key_detected() -> None:
    """TC-ArgusAgent-SECRET-001-01 — an AWS access-key id is flagged (>=1; may also match entropy)."""
    result = _run('aws_key = "AKIAIOSFODNN7EXAMPLE"\n')
    assert result.findings
    assert all(f.rule_id == RULE_HARDCODED_SECRET for f in result.findings)


def test_pem_private_key_header_detected() -> None:
    """TC-ArgusAgent-SECRET-001-02 — a PEM private-key header is flagged."""
    result = _run("KEY = '''-----BEGIN RSA PRIVATE KEY-----\nabc\n'''\n")
    assert any(f.rule_id == RULE_HARDCODED_SECRET for f in result.findings)


def test_generic_assigned_secret_detected() -> None:
    """TC-ArgusAgent-SECRET-001-03 — a generic api_key assignment is flagged."""
    result = _run('api_key = "supersecretvalue123"\n')
    assert len(result.findings) == 1


def test_high_entropy_literal_flagged_short_low_entropy_not() -> None:
    """TC-ArgusAgent-SECRET-001-04 — entropy flags a long random literal, not a short/low-entropy one."""
    high = 'blob = "aZ9kPqW3mX7vL2cR8tY4nB6h"\n'  # 24 chars, high entropy
    result_high = _run(high)
    assert any(f.rule_id == RULE_HARDCODED_SECRET for f in result_high.findings)

    # A short literal (below the length floor) → no finding.
    assert _run('x = "abc"\n').findings == ()
    # A long but low-entropy literal (all one char) → no finding.
    low = 'x = "' + "a" * (MIN_ENTROPY_TOKEN_LENGTH + 5) + '"\n'
    assert _run(low).findings == ()


def test_no_secret_repo_is_clean() -> None:
    """TC-ArgusAgent-SECRET-001-05 — a file with no secret yields zero findings (regression-safe)."""
    result = _run("def add(a, b):\n    return a + b\n")
    assert result.findings == ()
    assert result.entries[0].depth is CoverageDepth.AUDITED_SHALLOW


def test_deterministic_finding_set_and_stable_ids() -> None:
    """TC-ArgusAgent-SECRET-001-06 — same source → same findings + same value-independent ids."""
    source = 'api_key = "supersecretvalue123"\n'
    a = _run(source)
    b = _run(source)
    assert [f.recording_id for f in a.findings] == [f.recording_id for f in b.findings]


# ── AC2 / AC3 — producer-side redaction + the evidence contract ─────────────


def test_secret_value_absent_from_every_finding_field() -> None:
    """TC-ArgusAgent-SECRET-001-07 — the secret value bytes appear in no emitted field."""
    secret = "supersecretvalue123"
    result = _run(f'api_key = "{secret}"\n')
    blob = canonical.dumps(result.findings[0].model_dump(mode="json"))
    assert secret not in blob
    # nor in the recording id (value-independent identity).
    assert secret not in result.findings[0].recording_id


def test_evidence_model_has_no_value_field() -> None:
    """TC-ArgusAgent-SECRET-001-08 — SecretFindingEvidence has no value/secret field at all."""
    fields = set(SecretFindingEvidence.model_fields)
    assert "value" not in fields and "secret" not in fields and "raw" not in fields
    ev = SecretFindingEvidence(
        pattern_id="generic_assigned_secret",
        kind="generic_secret",
        masked="****",
        value_length=19,
        entropy_bits=Fraction(7, 2),
    )
    assert ev.contained_secret is True
    assert ev.masked == "****"
    assert ev.value_length == 19
    # The whole serialized evidence carries no secret.
    assert "supersecret" not in canonical.dumps(ev.model_dump(mode="json"))


def test_scan_evidence_carrier_masks_value() -> None:
    """TC-ArgusAgent-SECRET-001-14 — the in-memory evidence carrier masks the value (AC3)."""
    secret = "supersecretvalue123"
    evidence = SecretScanDetector().scan_evidence(
        file_path="src/config.py", source=f'api_key = "{secret}"\n'
    )
    assert evidence
    ev = evidence[0]
    assert ev.contained_secret is True
    assert ev.masked == "****"
    assert ev.value_length == len(secret)
    assert isinstance(ev.entropy_bits, Fraction)
    assert secret not in canonical.dumps(ev.model_dump(mode="json"))


def test_evidence_rejects_unknown_field_and_float() -> None:
    """TC-ArgusAgent-SECRET-001-09 — frozen extra=forbid; entropy is Fraction, not float."""
    with pytest.raises(ValidationError):
        SecretFindingEvidence(
            pattern_id="x", kind="y", masked="****", value_length=1,
            entropy_bits=Fraction(1), value="leak",  # type: ignore[call-arg]
        )
    ev = SecretFindingEvidence(
        pattern_id="x", kind="y", masked="****", value_length=1, entropy_bits=Fraction(7, 2)
    )
    # entropy serializes as a string (Fraction form), never a float (the 1.1 serializer rejects float).
    dumped = ev.model_dump(mode="json")
    assert isinstance(dumped["entropy_bits"], str)
    assert dumped["entropy_bits"] == "7/2"
    # the canonical serializer accepts the payload (no forbidden float leaf).
    canonical.dumps(dumped)


# ── AC4 — locator via the 1.5 builder + ast_span ────────────────────────────


def test_finding_carries_locator_and_ast_span_in_definition() -> None:
    """TC-ArgusAgent-SECRET-001-10 — the finding cites the file/line + the containing ast_span."""
    source = (
        "def load_creds():\n"  # 1
        '    api_key = "supersecretvalue123"\n'  # 2
        "    return api_key\n"  # 3
    )
    defs = [Definition(name="load_creds", kind="function", start_line=1, end_line=3)]
    result = _run(source, definitions=defs)
    assert len(result.findings) == 1
    loc = result.findings[0].locators[0]
    assert loc.file_path == "src/config.py"
    assert loc.start_line == 2
    assert loc.ast_span == "function:load_creds@1-3"


# ── AC5 — grade + fold ──────────────────────────────────────────────────────


def test_scanned_file_graded_shallow_with_recording_ids() -> None:
    """TC-ArgusAgent-SECRET-001-11 — the scanned file is graded audited_shallow."""
    result = _run('token = "supersecretvalue123"\n')
    assert result.entries[0].depth is CoverageDepth.AUDITED_SHALLOW
    assert result.findings[0].recording_id in result.entries[0].recording_ids


# ── AC7 — typed error + degradation, no secret leak ─────────────────────────


def test_malformed_argument_raises_typed_error_without_secret() -> None:
    """TC-ArgusAgent-SECRET-001-12 — a bad arg raises SecretScanError with no secret in the message."""
    detector = SecretScanDetector()
    with pytest.raises(SecretScanError) as exc:
        detector.run(file_path="", source="x", ast_entry=_entry())
    assert "AKIA" not in str(exc.value)
    with pytest.raises(SecretScanError):
        detector.run(file_path="a.py", source=123, ast_entry=_entry())  # type: ignore[arg-type]


# ── AI-E1-1 — non-ASCII path + non-ASCII secret value ───────────────────────


def test_non_ascii_path_secret_detected_and_redacted() -> None:
    """TC-ArgusAgent-SECRET-001-13 — a non-ASCII path's secret is detected, located, redacted."""
    secret = "пароль_секрет_значение_1234"  # Cyrillic secret value
    path = "модуль/café_secrets.py"
    result = _run(f'token = "{secret}"\n', file_path=path)
    assert result.findings  # detected (may match both generic + entropy families)
    loc = result.findings[0].locators[0]
    assert loc.file_path == path  # path intact, not mojibake / dropped
    blob = canonical.dumps_bytes(result.findings[0].model_dump(mode="json"))
    assert secret.encode("utf-8") not in blob  # the non-ASCII value's bytes are absent
