"""Precision of the ``high_entropy_string`` family (Story 2.5 hardening).

Verification area ArgusAgent-SECRET (TC-ArgusAgent-SECRET-002-NN). Story 2.5 pinned
that the entropy family DETECTS; this module pins that it does not detect
EVERYTHING — the other half of a usable detector.

Measured before this hardening, the family fired on 1108 string literals across 53
files of ArgusAgent's own secret-free source (docstrings, ``__all__`` entries, help
text) — ~99% false positives, enough noise to make the report unreadable and the
exact alarm-fatigue failure FR33 exists to prevent.

The root cause is pinned by ``test_entropy_alone_cannot_separate_the_classes``:
per-char Shannon entropy does not separate credentials from prose at these lengths,
so no threshold fixes it. The two structural discriminators do.
"""

from __future__ import annotations

import pytest

from argus.detectors.secret_scan import (
    ENTROPY_BITS_PER_CHAR_FLOOR,
    MIN_ENTROPY_TOKEN_LENGTH,
    _has_letter_digit_mix,
    _has_no_whitespace,
    _is_entropy_candidate,
    _shannon_bits_per_char,
)

# Real credential shapes the family must keep catching (recall).
KNOWN_SECRET_SHAPES = (
    "PLANTEDxAbCdEfGhIjKlMnOpQrStUvWxYz012345",
    "EVIDENCE_SENTINEL_zXqW7vKpLmNrTaBcDeF1234567890ABCDEF",
    "AKIAIOSFODNN7EXAMPLE",
    "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "xoxb-123456789012-1234567890123-example",
    "0123456789abcdef0123456789abcdef01234567",
    "sk_live_4eC39HqLyjWDarjtT1zdp7dc",
    "ghp_16C7e42F292c6912E7710c838347Ae178B4a",
)

# Ordinary literals harvested from ArgusAgent's own source, every one of which the
# pre-hardening rule reported as a hardcoded secret.
ORDINARY_LITERALS = (
    "render_final_verdict_report",
    "render_security_review_report",
    "Render the `final-verdict.md` end-user summary report.",
    "Negative Assurance & Scope Disclaimer",
    "audited_shallow / tool_scanned_only",
    "Path to the repository to audit.",
    "argus/reports/generator.py",
    "NOT_READY_FOR_RELEASE",
    "critical_subsystems_all_deep",
    "Enabled end-user report types to generate.",
)


@pytest.mark.parametrize("value", KNOWN_SECRET_SHAPES)
def test_known_secret_shapes_are_still_candidates(value: str) -> None:
    """TC-ArgusAgent-SECRET-002-01 — recall: hardening must not cost a real detection."""
    assert _is_entropy_candidate(value) is True


@pytest.mark.parametrize("value", ORDINARY_LITERALS)
def test_ordinary_literals_are_rejected(value: str) -> None:
    """TC-ArgusAgent-SECRET-002-02 — precision: ordinary source text is not a secret."""
    assert _is_entropy_candidate(value) is False


def test_entropy_alone_cannot_separate_the_classes() -> None:
    """TC-ArgusAgent-SECRET-002-03 — THE root cause, pinned so it cannot be re-argued.

    An ordinary docstring measures HIGHER per-char entropy than a genuine AWS access
    key. Because the ranges overlap, no ``ENTROPY_BITS_PER_CHAR_FLOOR`` value can
    separate them — which is why the fix is structural rather than a re-tuned
    threshold. If someone later "simplifies" the discriminators away and raises the
    floor instead, this test explains why that cannot work.
    """
    docstring = "Render the `final-verdict.md` end-user summary report."
    aws_key = "AKIAIOSFODNN7EXAMPLE"

    assert _shannon_bits_per_char(docstring) > _shannon_bits_per_char(aws_key)
    # Both clear the configured floor — entropy gives no signal to discriminate on.
    assert _shannon_bits_per_char(docstring) >= ENTROPY_BITS_PER_CHAR_FLOOR
    assert _shannon_bits_per_char(aws_key) >= ENTROPY_BITS_PER_CHAR_FLOOR
    # The structural clauses are what actually separate them.
    assert _is_entropy_candidate(docstring) is False
    assert _is_entropy_candidate(aws_key) is True


def test_whitespace_discriminator() -> None:
    """TC-ArgusAgent-SECRET-002-04 — a credential is one token; prose is not."""
    assert _has_no_whitespace("sk_live_4eC39HqLyjWDarjtT1zdp7dc") is True
    assert _has_no_whitespace("a long sentence of prose text here") is False
    assert _has_no_whitespace("tab\tseparated") is False
    assert _has_no_whitespace("newline\nvalue") is False


def test_letter_digit_mix_discriminator() -> None:
    """TC-ArgusAgent-SECRET-002-05 — generated credentials mix letters and digits."""
    assert _has_letter_digit_mix("AKIAIOSFODNN7EXAMPLE") is True
    assert _has_letter_digit_mix("render_final_verdict_report") is False  # no digits
    assert _has_letter_digit_mix("1234567890123456789012") is False  # no letters
    # Unicode-aware (the AI-E1-1 precedent): a non-ASCII identifier is classified.
    assert _has_letter_digit_mix("пароль_секрет_значение_1234") is True


def test_length_floor_still_applies() -> None:
    """TC-ArgusAgent-SECRET-002-06 — the hardening is additive to the length gate."""
    short_but_mixed = "ab1"
    assert len(short_but_mixed) < MIN_ENTROPY_TOKEN_LENGTH
    assert _is_entropy_candidate(short_but_mixed) is False


def test_predicate_is_pure_and_deterministic() -> None:
    """TC-ArgusAgent-SECRET-002-07 — AR4/AR8: same input, same answer, no state."""
    value = "PLANTEDxAbCdEfGhIjKlMnOpQrStUvWxYz012345"
    results = {_is_entropy_candidate(value) for _ in range(8)}
    assert results == {True}
    entropies = {_shannon_bits_per_char(value) for _ in range(8)}
    assert len(entropies) == 1  # exact Fraction, never a drifting float
