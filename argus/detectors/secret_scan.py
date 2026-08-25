"""Hardcoded-secret detector with PRODUCER-SIDE redaction (PURE).

Drivers: ArgusAgent-FR-11 (detect hardcoded secrets + report them with the secret value
REDACTED — the central driver), ArgusAgent-NFR-S2 (detected secrets redacted BEFORE
storage; the stored form carries ``contained_secret`` WITHOUT the value),
ArgusAgent-FR-28 (producer guarantee: no source/secret bytes in ledger/evidence/logs/
traces — the PRODUCER half; the CI-blocking randomized property suite is Story
4.4), ArgusAgent-NFR-S1 (source/secret/api-key bytes never appear in ledgers, evidence,
logs, OTLP spans, traces, or any response — enforced here at the producer,
mechanically backstopped by Story 4.4), ArgusAgent-FR-13 (every finding carries ≥1
verifiable locator or is rejected — via the Story 1.5 ``build_recording`` builder),
ArgusAgent-NFR-D2 (deterministic, zero-LLM-token detector core — a pure scorer over
recorded inputs), ArgusAgent-NFR-R1 / AR10 (a regex/scan failure on a file degrades to a
recorded condition, never an uncaught raise / false flag / silent secret leak),
AR4 (single canonical serializer; entropy stored as an exact ``Fraction``, NEVER
``float``; content-derived ids; no clock/uuid/random/iteration-order in any
``.argus/`` write path), AR8 (pure/impure separation — the scorer + redaction +
finding build are PURE; the per-file source read + finding write are the existing
impure pipeline shell), AR11 (``.argus/`` finding filenames content-derived),
ArgusAgent-NFR-M1 (≤1200-line files), ArgusAgent-NFR-M2 (frozen, additive-only contracts).

The keystone: producer-side redaction
--------------------------------------
Redaction happens AT THE PRODUCER, before any model is constructed or any byte is
written. The detector is the single point that KNOWS the secret value, so it is
the single point at which the value must be DROPPED. The LOCATION is the ONLY thing
that survives into a finding: the masked indicator is computed by
:meth:`SecretScanDetector.scan_evidence`'s in-memory carrier and NEVER enters one —
no emitted model has a field that could hold it. The secret value's bytes
NEVER enter a ``FindingDraft`` field, a ``Locator``, a ``rule_id``, a
``coverage_envelope_slice``, the :class:`SecretFindingEvidence`, a
``DegradedCondition.reason``, a log line, or a raised exception message. The
``recording_id`` is derived (by the 1.5 builder) from the LOCATION + rule, NOT the
value — so the id reveals nothing and two distinct secrets at one location do not
collide on identity beyond the location they share.

The structural safety is the ABSENCE of a value field
-----------------------------------------------------
The 1.2 ``Recording`` / ``Locator`` and the 1.5 ``FindingDraft`` carry NO
free-form value/evidence field. :class:`SecretFindingEvidence` (mirroring the 1.5
``VacuousTestScore`` precedent — detector evidence on a separate frozen
``int``/``Fraction``-only model) ALSO has no value field. A secret cannot be stored
if there is nowhere to store it.

V1 detection scope + KNOWN limits (LOCKED — frozen for Story 4.4 + Story 6.5)
----------------------------------------------------------------------------
Detection is regex pattern families + a Shannon-entropy threshold over candidate
assigned string literals. This is a V1 HEURISTIC: it false-positives on test
fixtures / example/placeholder keys and false-negatives on obfuscated / split /
base64-nested secrets. The finding is therefore ``advisory=True`` in V1 (a
verdict-blocking promotion is a deferred future story — see Dev Notes).

KNOWN LIMITS that remain after Story 18.3 / DF-AUD-DETECT-E, each MEASURED and
DISCLOSED rather than fixed. The scan is a TEXT scan and is NOT a Python tokenizer.
Every quoted-literal pattern below now closes with the delimiter it opened with, which
REALIGNS the scan; it does not tokenize it. So: (1) a literal that CONTAINS its own
delimiter is still invisible to it; (2) prose in a comment still matches — there is no
comment model, so a commented-out assignment is reported exactly as a live one is;
(3) a JSON-style mapping from a quoted key to a quoted value is still NOT matched,
because the quote between the key and its separator defeats the assignment shape the
pattern requires (measured: 0 findings before that story and 0 after); and (4) the
left anchor added there rejects a preceding LETTER OR DIGIT only — see
``generic_assigned_secret`` below for why it must admit ``_``.

The locked pattern families (each documented by its ``pattern_id``):

- ``aws_access_key_id`` — an ``AKIA``/``ASIA``-prefixed 20-char uppercase/digit id.
- ``aws_secret_access_key`` — a 40-char base64-ish value assigned to an
  ``aws``/``secret`` key.
- ``private_key_pem`` — a PEM private-key header line
  (``-----BEGIN ... PRIVATE KEY-----``).
- ``generic_assigned_secret`` — an assignment whose key matches
  ``api[_-]?key`` / ``secret`` / ``token`` / ``password`` / ``passwd`` / ``pwd``
  to a quoted string literal of sufficient length. The key word must NOT be preceded
  by a letter or a digit (so ``topsecret`` / ``mytoken`` / ``notapassword`` are
  rejected), but ``_`` IS admitted: ``_`` is the SEPARATOR in ``UPPER_SNAKE_CASE``,
  which is how credentials are really named, and excluding it was measured to drop
  ``DB_PASSWORD`` / ``_API_KEY`` / ``SMTP_PASSWORD`` to ZERO findings.
- ``high_entropy_string`` — a quoted string literal whose length ≥
  :data:`MIN_ENTROPY_TOKEN_LENGTH`, whose Shannon entropy (bits/char) ≥
  :data:`ENTROPY_BITS_PER_CHAR_FLOOR` (entropy stored as an exact ``Fraction``),
  AND which passes the two STRUCTURAL discriminators below.

Why entropy alone is not a usable rule for this family
------------------------------------------------------
Per-char Shannon entropy does NOT separate credentials from prose at these
lengths, so a threshold cannot be tuned to fix it. Measured on real values:

  ordinary docstrings / identifiers   3.49 – 4.14 bits/char
  real secrets (incl. an AWS key)     3.68 – 5.17 bits/char

The ranges OVERLAP — an ordinary docstring (4.14) scores HIGHER than a genuine
``AKIA`` access key (3.68). Any floor high enough to reject prose also rejects
real keys. Left on entropy alone this family fired on 1108 literals across 53
files of ArgusAgent's own secret-free source (docstrings, ``__all__`` entries,
help text), i.e. ~99% false positives — the alarm-fatigue failure FR33 exists to
prevent, and enough noise to make the whole report unreadable.

Two STRUCTURAL discriminators separate the classes where entropy cannot, because
they key on the SHAPE of a generated credential rather than its randomness:

- :func:`_has_no_whitespace` — a credential is a single token. Prose is not.
- :func:`_has_letter_digit_mix` — a generated credential mixes letters AND
  digits. ``render_final_verdict_report`` does not; ``AKIAIOSFODNN7EXAMPLE`` does.

Together these cut the same corpus 1108 → 12 (98.9%) while retaining 100% recall
over every known secret shape (AWS id + secret key, Slack ``xoxb``, GitHub
``ghp_``, Stripe ``sk_live_``, hex API keys, and the planted cartridge sentinels).

The residual recall cost is bounded and deliberate: an all-alphabetic credential
assigned to a non-obvious name is no longer caught by THIS family. It is still
caught by ``generic_assigned_secret`` whenever the target name looks like a
secret (``api_key`` / ``secret`` / ``token`` / ``password`` / …), and by the
dedicated ``aws_*`` / ``private_key_pem`` families regardless of naming. This
family is a supplementary net, and a supplementary net that fires on everything
catches nothing — an operator who cannot read the report is not protected by it.

File-scope rule (LOCKED): secrets live in production code, so the detector is NOT
gated to test files (contrast the vacuous detector). It scans every text source
file the pipeline hands it. It reads source TEXT + the existing 1.4
``AstIndexEntry`` (for an optional containing ``Definition.ast_span``); it does NOT
re-parse and does NOT need the call graph.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from fractions import Fraction
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field

from argus.detectors.base import (
    DegradedCondition,
    DetectorResult,
    FindingDraft,
    build_recording,
)
from argus.detectors.secret_suppression import (
    OPERATOR_ATTRIBUTABLE_REASONS,
    SecretSuppressionEngine,
)
from argus.index.ast_index import AstIndexEntry, Definition
from argus.ledger.coverage_ledger import CoverageDepth, grade_entry

__all__ = [
    "SECRET_EVIDENCE_SCHEMA_VERSION",
    "RULE_HARDCODED_SECRET",
    "RULE_OPERATOR_SUPPRESSED_SECRET",
    "MIN_ENTROPY_TOKEN_LENGTH",
    "ENTROPY_BITS_PER_CHAR_FLOOR",
    "MIN_GENERIC_SECRET_LENGTH",
    "SecretScanError",
    "SecretFindingEvidence",
    "SecretScanDetector",
    "operator_suppression_rule_id",
]

SECRET_EVIDENCE_SCHEMA_VERSION = "1"

# The single rule-id vocabulary for this detector (frozen for 4.4 / 6.5).
RULE_HARDCODED_SECRET = "hardcoded_secret"

# Story 10.3 / AC4.2 — the rule-id PREFIX for a suppression an operator's own flag caused.
# The full id is ``operator_suppressed_secret:<reason token>``; the reason travels in the
# rule id because ``Recording`` is a frozen, ``extra="forbid"`` contract with no free-text
# slot, and widening it would be a schema change this specification-correction story has no
# licence to make (``prd.md`` additive-only policy).
RULE_OPERATOR_SUPPRESSED_SECRET = "operator_suppressed_secret"


def operator_suppression_rule_id(reason: str) -> str:
    """The rule id recording a suppression the operator's own flag caused (PURE).

    Raises:
        SecretScanError: if *reason* is not an operator-attributable token. A built-in
            suppression (public sentinel, inline annotation, ``DEFAULT_TEST_PATH_PATTERNS``)
            is deliberately NOT recorded here — AC4.5 — and minting an id for one would
            silently widen the disclosure onto runs that passed no flag at all.
    """
    if reason not in OPERATOR_ATTRIBUTABLE_REASONS:
        raise SecretScanError(
            f"'{reason}' is not an operator-attributable suppression reason; "
            f"expected one of {OPERATOR_ATTRIBUTABLE_REASONS}"
        )
    return f"{RULE_OPERATOR_SUPPRESSED_SECRET}:{reason}"

# Entropy candidate thresholds (LOCKED heuristics — documented as such).
MIN_ENTROPY_TOKEN_LENGTH = 20
# 3 bits/char ≈ a meaningfully random base-charset token (a low-entropy English
# word sits well below this). Stored as a Fraction so the comparison + any
# persisted value is exact (AR4 — never float).
ENTROPY_BITS_PER_CHAR_FLOOR = Fraction(3)

# Minimum length for a generic ``key = "..."`` assignment to be flagged (so a
# short placeholder like ``password = "x"`` is not noise).
MIN_GENERIC_SECRET_LENGTH = 8

# A fixed-shape mask revealing ZERO value characters (the SAFEST default — see the
# module docstring + AC2). The evidence also carries ``value_length`` + ``kind``
# so a reader learns "a secret of kind X of length N is at file:line" WITHOUT
# learning the secret.
_MASK = "****"


class SecretScanError(ValueError):
    """Raised on a malformed argument to the detector (AR10 typed failure).

    A ``ValueError`` subclass localized to this module (mirroring
    ``RecordingValidationError`` / ``RepoIntakeError`` / ``PartitionerError``). Its
    message names the failing argument only — it NEVER contains a secret value.
    """


class SecretFindingEvidence(BaseModel):
    """Frozen, redaction-safe evidence carried WITH a secret finding (NFR-S2/M2).

    Mirrors the 1.5 ``VacuousTestScore`` precedent: detector evidence on a separate
    frozen model carrying ONLY redaction-safe metadata. ``frozen=True,
    extra="forbid"``; entropy is an exact ``Fraction`` (NEVER ``float`` — the 1.1
    serializer rejects ``float``); counts/lengths are ``int``.

    There is **NO** ``value`` / ``secret`` / raw-bytes field on this model AT ALL —
    the ABSENCE of the field is the structural redaction guarantee (a value cannot
    be stored if there is nowhere to store it). The detector computes ``masked`` +
    ``value_length`` + ``entropy_bits`` and DISCARDS the raw value in the same pure
    step.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=SECRET_EVIDENCE_SCHEMA_VERSION,
        description="SecretFindingEvidence schema version (additive-only).",
    )
    pattern_id: str = Field(..., description="Which regex/entropy family matched.")
    kind: str = Field(..., description="Category label for the matched secret.")
    contained_secret: bool = Field(
        default=True, description="Always True — a secret WAS detected (NFR-S2)."
    )
    masked: str = Field(..., description="Fixed-shape mask revealing zero value chars.")
    value_length: int = Field(..., ge=0, description="Length of the redacted value (no value).")
    entropy_bits: Fraction = Field(
        ..., description="Shannon bits/char of the value (Fraction, NEVER float)."
    )


def _shannon_bits_per_char(value: str) -> Fraction:
    """Shannon entropy in bits/char of *value*, as an EXACT ``Fraction`` (AR4).

    ``H = -Σ p·log2(p)``. ``log2`` is irrational, so each per-symbol contribution
    is rounded to a fixed-precision ``Fraction`` (a 1e-6 grid) — deterministic and
    byte-stable across hosts (never a binary ``float`` in a persisted field). The
    raw value is consumed here and never returned.
    """
    if not value:
        return Fraction(0)
    counts = Counter(value)
    length = len(value)
    total = Fraction(0)
    for symbol_count in counts.values():
        probability = Fraction(symbol_count, length)
        # -p * log2(p); quantize log2 to a deterministic rational grid.
        log2_p = Fraction(round(math.log2(symbol_count / length) * 1_000_000), 1_000_000)
        total += -probability * log2_p
    return total


class _Match:
    """An internal, transient per-match descriptor — NEVER persisted/serialized.

    Holds the raw value ONLY long enough to compute the masked evidence; it is a
    plain object (not a Pydantic model) so it can never accidentally be
    ``model_dump``-ed into a persisted payload. Discarded after evidence is built.
    """

    __slots__ = ("pattern_id", "kind", "value", "start_line", "end_line")

    def __init__(
        self, *, pattern_id: str, kind: str, value: str, start_line: int, end_line: int
    ) -> None:
        self.pattern_id = pattern_id
        self.kind = kind
        self.value = value
        self.start_line = start_line
        self.end_line = end_line


# ── Regex pattern families (LOCKED V1 set) ──────────────────────────────────
# Each pattern captures the SECRET VALUE in a named group ``secret`` (or the whole
# match where the header itself is the indicator). The value is used ONLY to
# compute the mask; it is never emitted.

_AWS_ACCESS_KEY_RE = re.compile(r"(?P<secret>(?:AKIA|ASIA)[0-9A-Z]{16})")
# The opening delimiter is CAPTURED and the close is a BACKREFERENCE to it (Story 18.3
# / DF-AUD-DETECT-E). Spelling the delimiter as two INDEPENDENT one-of-two classes
# accepted a span opened with one quote and closed with the other: measured 462 such
# spans over ``argus/**`` (95 files), 3 of them reportable — one of which was THIS
# pattern's own source line.
_AWS_SECRET_KEY_RE = re.compile(
    r"(?i)aws[_-]?(?:secret[_-]?access[_-]?key|secret)\s*[:=]\s*"
    r"(?P<q>['\"])(?P<secret>[A-Za-z0-9/+=]{40})(?P=q)"
)
_PEM_PRIVATE_KEY_RE = re.compile(
    r"(?P<secret>-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----)"
)
# TWO repairs, both measured (Story 18.3 / DF-AUD-DETECT-E). The LEFT ANCHOR rejects a
# preceding letter or digit: without it ``topsecret`` / ``mytoken`` / ``notapassword``
# each reported 1 finding. It deliberately does NOT exclude ``_``: the word-boundary
# spelling ``(?<![A-Za-z0-9_])`` was executed and drops ``DB_PASSWORD``, ``_API_KEY``
# and ``SMTP_PASSWORD`` to ZERO, and reddens ``TC-ArgusAgent-SECRET-001-26``, the
# live-key safeguard — a recall regression wearing a precision fix's clothes. The
# DELIMITER is captured and back-referenced, as above.
_GENERIC_ASSIGN_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:api[_-]?key|secret|token|password|passwd|pwd)\s*[:=]\s*"
    r"(?P<q>['\"])(?P<secret>[^'\"\n]+)(?P=q)"
)
# NOTE: this matches ANY quoted literal — docstrings, ``__all__`` entries, help
# text, log messages — NOT only assigned ones. It was previously named
# ``_ASSIGNED_LITERAL_RE``, and that name is precisely why an unbounded match was
# mistaken for a narrow one. The narrowing now lives in the explicit structural
# predicates applied at the call site, where it is visible.
# The delimiter is captured and back-referenced here too (Story 18.3 /
# DF-AUD-DETECT-E). This is the site the entry names, and the direction of its error
# was BOTH ways rather than over-reporting only: the unpaired form consumed a real
# credential's opening quote and ``finditer`` then resumed INSIDE the value, so
# a credential nested inside a single-quoted wrapper reported 0 findings before this
# repair and 1 after. Over 252 tracked files the paired form finds 13 raw matches the unpaired form
# does not, ten of them canonical credential shapes.
_ANY_LITERAL_RE = re.compile(r"(?P<q>['\"])(?P<secret>[^'\"\n]+)(?P=q)")


def _has_no_whitespace(value: str) -> bool:
    """Whether *value* is a single unbroken token (PURE).

    A generated credential is one token. Prose is not. This alone rejects every
    docstring and help string, which entropy cannot (a 52-char docstring measures
    4.14 bits/char — above a real AWS key's 3.68).
    """
    return not any(char.isspace() for char in value)


def _has_letter_digit_mix(value: str) -> bool:
    """Whether *value* mixes letters AND digits — the shape of a generated key (PURE).

    ``render_final_verdict_report`` (letters only) is rejected;
    ``AKIAIOSFODNN7EXAMPLE`` and ``sk_live_4eC39HqLyjWDarjtT1zdp7dc`` are kept.
    Unicode-aware via ``str.isalpha``/``str.isdigit`` so a non-ASCII identifier is
    classified, not silently dropped (the AI-E1-1 precedent).
    """
    return any(c.isalpha() for c in value) and any(c.isdigit() for c in value)


def _is_entropy_candidate(value: str) -> bool:
    """The full ``high_entropy_string`` predicate (PURE, deterministic).

    Length ∧ entropy ∧ single-token ∧ letter-digit mix. See the module docstring
    for why the two structural clauses are load-bearing rather than cosmetic.
    """
    return (
        len(value) >= MIN_ENTROPY_TOKEN_LENGTH
        and _shannon_bits_per_char(value) >= ENTROPY_BITS_PER_CHAR_FLOOR
        and _has_no_whitespace(value)
        and _has_letter_digit_mix(value)
    )


def _line_span(source: str, match_start: int, match_end: int) -> tuple[int, int]:
    """1-based inclusive line span of the match (deterministic, no clock)."""
    start_line = source.count("\n", 0, match_start) + 1
    end_line = source.count("\n", 0, max(match_start, match_end - 1)) + 1
    return start_line, end_line


def _ast_span_for_line(definitions: tuple[Definition, ...], line: int) -> str | None:
    """The smallest containing ``Definition.ast_span`` for *line* (deterministic)."""
    containing = [d for d in definitions if d.start_line <= line <= d.end_line]
    if not containing:
        return None
    best = min(containing, key=lambda d: (d.end_line - d.start_line, d.start_line, d.name))
    return best.ast_span


class SecretScanDetector:
    """PURE regex + entropy hardcoded-secret scorer with producer-side redaction.

    Satisfies the ``detectors.base.Detector`` protocol structurally. ``run`` is a
    pure function over (source text + the 1.4 ``AstIndexEntry``): NO I/O, NO clock,
    NO LLM (zero-token), NO ``uuid4``/``random``, NO ``float`` field, NO
    set/dict-iteration-order reliance. Un-scannable input degrades to a recorded
    condition; a malformed argument raises :class:`SecretScanError` — neither path
    leaks the secret value.
    """

    rule_id = RULE_HARDCODED_SECRET

    def scan_evidence(
        self, *, file_path: str, source: str
    ) -> tuple[SecretFindingEvidence, ...]:
        """The redaction-safe evidence for each match (in-memory carrier; AC3).

        Mirrors the 1.5 ``VacuousTestScore`` precedent: detector evidence travels on
        a separate frozen model (NOT folded into the frozen 1.5 ``DetectorResult``,
        which has no evidence slot). Each :class:`SecretFindingEvidence` carries the
        masked indicator + length + kind + entropy — never the value. Useful for an
        in-memory consumer (and the AC6 containment proof) without persisting a
        value field. PURE.
        """
        if not isinstance(source, str):
            raise SecretScanError("source must be a str")
        return tuple(
            self._evidence_for(match)
            for match in sorted(
                self._scan(source), key=lambda m: (m.start_line, m.end_line, m.pattern_id)
            )
        )

    @staticmethod
    def _evidence_for(match: _Match) -> SecretFindingEvidence:
        """Compute the redaction-safe evidence and DISCARD the raw value (keystone).

        The masked indicator + ``value_length`` + ``entropy_bits`` are computed from
        the value here; the value is not returned and never enters a serialized
        field. This is the single producer-side redaction step.
        """
        return SecretFindingEvidence(
            pattern_id=match.pattern_id,
            kind=match.kind,
            contained_secret=True,
            masked=_MASK,
            value_length=len(match.value),
            entropy_bits=_shannon_bits_per_char(match.value),
        )

    def run(
        self,
        *,
        file_path: str,
        source: str,
        ast_entry: AstIndexEntry,
        coverage_envelope_slice: str | None = None,
        ignore_paths: Sequence[str] = (),
        ignore_patterns: Sequence[str] = (),
    ) -> DetectorResult:
        """Scan *file_path* for hardcoded secrets and emit REDACTED findings (AR8).

        Returns a frozen :class:`DetectorResult` the pipeline folds: one
        ``audited_shallow`` coverage entry for the scanned file plus one REDACTED
        1.2 ``Recording`` per distinct (location, pattern) match. Producer-side
        redaction: the secret value is dropped in the same pure step that computes
        the mask; it never enters any emitted field.
        """
        if not isinstance(file_path, str) or not file_path:
            raise SecretScanError("file_path must be a non-empty str")
        if not isinstance(source, str):
            raise SecretScanError("source must be a str")
        if not isinstance(ast_entry, AstIndexEntry):
            raise SecretScanError("ast_entry must be an AstIndexEntry")

        try:
            matches = self._scan(source)
        except SecretScanError:
            raise
        except Exception:  # noqa: BLE001 — degrade, never leak / crash (AR10)
            # The reason token carries NO secret value (NFR-S1).
            return DetectorResult(
                degraded=(DegradedCondition(file_path=file_path, reason="secret_scan_failed"),)
            )

        source_lines = source.splitlines()
        findings = []
        seen: set[tuple[int, int, str]] = set()
        suppressed_ids: set[str] = set()
        for match in sorted(
            matches, key=lambda m: (m.start_line, m.end_line, m.pattern_id)
        ):
            identity = (match.start_line, match.end_line, match.pattern_id)
            if identity in seen:
                continue
            seen.add(identity)

            line_text = (
                source_lines[match.start_line - 1]
                if 1 <= match.start_line <= len(source_lines)
                else None
            )
            is_suppressed, reason = SecretSuppressionEngine.evaluate_suppression(
                file_path=file_path,
                snippet=match.value,
                line_content=line_text,
                ignore_paths=ignore_paths,
                ignore_patterns=ignore_patterns,
            )
            if is_suppressed:
                # Story 10.3 / AC4.2. The reason token used to be bound to `_reason` and
                # thrown away: the operator's INPUTS were persisted by
                # `AuditRequest.to_provenance_payload()` while the EFFECT — that a secret
                # was found and suppressed — left no trace anywhere. A suppression an
                # operator's own flag caused is now RECORDED, so it can be disclosed.
                #
                # Design (a) of the story's AC4.4: the record travels on the `Recording`
                # fold the pipeline already consumes, NOT on a new `DetectorResult` field.
                # `argus/pipeline.py` is byte-fenced to Story 12.1 (1331 lines against the
                # NFR-M1 cap of 1200) and already does `findings.extend(secret_result
                # .findings)`, so this needs no line there; a new result field would have.
                #
                # It carries the REASON TOKEN and the LOCATOR and nothing else
                # (NFR-S1/NFR-S2/AR8): not the secret, not the source line, and NOT the
                # operator's `--ignore-pattern` text — that pattern is operator-supplied and
                # may itself be secret bytes.
                #
                # `depth_supported=None` makes it NON-BLOCKING by construction
                # (`verdict_gate.is_verdict_blocking`), so a disclosure can never move a
                # verdict on its own. Built-in suppressions emit nothing (AC4.5).
                #
                # De-duplicated by content id: a single literal can match several scan
                # patterns at the same span (a `TOKEN = "..."` line is both an assigned
                # secret and a high-entropy string), and emitting the identical disclosure
                # row twice would overstate how many suppressions the operator caused.
                if reason is not None and reason in OPERATOR_ATTRIBUTABLE_REASONS:
                    suppression_draft = FindingDraft(
                        file_path=file_path,
                        start_line=match.start_line,
                        end_line=match.end_line,
                        ast_span=_ast_span_for_line(
                            ast_entry.definitions, match.start_line
                        ),
                        rule_id=operator_suppression_rule_id(reason),
                        advisory=True,
                        coverage_envelope_slice=coverage_envelope_slice,
                    )
                    suppression_record = build_recording(
                        suppression_draft, depth_supported=None, claim_present=False
                    )
                    if suppression_record.recording_id not in suppressed_ids:
                        suppressed_ids.add(suppression_record.recording_id)
                        findings.append(suppression_record)
                continue

            ast_span = _ast_span_for_line(ast_entry.definitions, match.start_line)
            # ── PRODUCER-SIDE REDACTION IS STRUCTURAL — THERE IS NO STEP TO PERFORM HERE ──
            # The value is dropped by never being CARRIED, not by a call made here. No emitted
            # model has a field that could hold it: `FindingDraft` (below), `Recording` /
            # `Locator` (built by the 1.5 `build_recording`) and `DetectorResult` (returned
            # below) are all `frozen=True, extra="forbid"`, so there is nowhere to put a value
            # and no way to add one at runtime. `match.value` never reaches a constructor —
            # only the LOCATION does. `scan_evidence()` remains the IN-MEMORY evidence carrier
            # (masked indicator + length + kind + entropy, never the value); the pipeline does
            # not call it, and Story 2.5 locked it that way — evidence is NOT folded into
            # `DetectorResult` and is NOT persisted.
            #
            # This banner read "PRODUCER-SIDE REDACTION (the keystone)" over a
            # `self._evidence_for(match)` expression statement whose return value was bound to
            # nothing (Story 18.2 / `DF-AUD-DETECT-B`): it computed the mask, the length, the
            # kind, the pattern id and an exact-`Fraction` entropy and discarded all five,
            # while reading as the load-bearing guarantee. Deleting it changed 0 of 251 tracked
            # files' `DetectorResult`s. ⛔ Do not reinstate it — `TC-ArgusAgent-SECRET-001-29`
            # asserts by AST that no `_evidence_for` call site discards its return, and `-28`
            # asserts `run()`'s output does not depend on that computation at all.
            draft = FindingDraft(
                file_path=file_path,
                start_line=match.start_line,
                end_line=match.end_line,
                ast_span=ast_span,
                rule_id=RULE_HARDCODED_SECRET,
                advisory=True,
                coverage_envelope_slice=coverage_envelope_slice,
            )
            findings.append(
                build_recording(draft, depth_supported=None, claim_present=False)
            )


        recording_ids = tuple(f.recording_id for f in findings)
        entry = grade_entry(
            file_path=file_path,
            proposed_depth=CoverageDepth.AUDITED_SHALLOW,
            claim_present=False,
            recording_ids=recording_ids,
        )
        return DetectorResult(entries=(entry,), findings=tuple(findings))

    def _scan(self, source: str) -> list[_Match]:
        """Pure regex + entropy scan over *source*. Returns transient matches.

        Each :class:`_Match` holds the raw value ONLY transiently (to compute the
        mask); none of these objects is ever serialized. Deterministic: matches are
        de-duplicated + sorted by the caller.
        """
        matches: list[_Match] = []

        for regex, pattern_id, kind in (
            (_AWS_ACCESS_KEY_RE, "aws_access_key_id", "aws_access_key"),
            (_AWS_SECRET_KEY_RE, "aws_secret_access_key", "aws_secret_key"),
            (_PEM_PRIVATE_KEY_RE, "private_key_pem", "private_key"),
            (_GENERIC_ASSIGN_RE, "generic_assigned_secret", "generic_secret"),
        ):
            for m in regex.finditer(source):
                value = m.group("secret")
                if pattern_id == "generic_assigned_secret" and len(value) < MIN_GENERIC_SECRET_LENGTH:
                    continue
                start_line, end_line = _line_span(source, m.start("secret"), m.end("secret"))
                matches.append(
                    _Match(
                        pattern_id=pattern_id,
                        kind=kind,
                        value=value,
                        start_line=start_line,
                        end_line=end_line,
                    )
                )

        for m in _ANY_LITERAL_RE.finditer(source):
            value = m.group("secret")
            if not _is_entropy_candidate(value):
                continue
            start_line, end_line = _line_span(source, m.start("secret"), m.end("secret"))
            matches.append(
                _Match(
                    pattern_id="high_entropy_string",
                    kind="high_entropy",
                    value=value,
                    start_line=start_line,
                    end_line=end_line,
                )
            )

        return matches
