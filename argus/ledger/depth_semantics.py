"""Documented five-state depth-grading rule + content-derived criticality (FR8).

Drivers: ArgusAgent-FR-5 (fixed-enum coverage ledger — the five depth states with
documented semantics; reuses the 1.2 ``CoverageDepth`` enum verbatim), ArgusAgent-FR-8
(the central driver: ``inferred`` (narrative/doc) evidence can never satisfy a
verdict gate — this module documents the rule as data and the FR8 regression
tests pin that the 1.6 gate honors it), ArgusAgent-FR-4-support (criticality assessed by
file CONTENT, not filename — the anti-gaming ASSESSMENT Story 2.3 consumes; this
story builds the assessment, NOT the operator designation or the gate clause),
ArgusAgent-NFR-D2 (deterministic, zero-LLM-token), ArgusAgent-NFR-M2 (frozen, additive-only
contracts), AR4 (no ``float``; no clock/uuid/random/iteration-order in any
``.argus/``-bound output — the criticality signal is a closed enum, never a float
score), AR8 (PURE — no I/O, no clock, no LLM; the file READ is the impure
caller's job, this module classifies in-memory inputs only), AR10 (typed failure —
a malformed descriptor raises a localized ``ValueError`` subclass, never a silent
coerce / bare ``except: pass`` / ``print()`` in library code).

Why this module exists
----------------------
Epic 1 delivered the determinism spine: the closed five-member ``CoverageDepth``
enum (Story 1.2) and a verdict gate whose deep-% numerator counts ONLY
``audited_deep`` (Story 1.6) — so the FR8 evidence-poisoning math already holds.
What was MISSING is the *honesty surface*: a single, documented source of truth
for what evidence earns each of the five states, a pure classifier the later
detectors (2.5/2.6) and the readable surface (2.2) can call, the content-derived
criticality ASSESSMENT that defeats coverage-gaming-by-renaming (FR4-support), and
an explicit, NAMED FR8 regression that fails loudly if a future author ever lets a
non-``audited_deep`` state into the gate numerator. This module is that surface.

The five-state grading rule (FR5 / FR8 — the canonical reference, LOCKED here)
------------------------------------------------------------------------------
Each file lands in EXACTLY ONE state. Only ``audited_deep`` is in the deep-%
numerator (the 1.6 gate's ``deep_count()``); every other state is denominator-only.
This table IS FR8 expressed as data — see :data:`DEPTH_SEMANTICS`.

- ``audited_deep`` — an emitted deep claim is present (FR6 claim-presence; V1.
  AST-truth grounding of the claim is the Epic-6 Story 6.2 deferral DF-1-7-B, the
  documented V1 honesty limitation). COUNTS toward the deep-% numerator.
- ``audited_shallow`` — read/analyzed but no qualifying deep claim was emitted
  (silence → shallow, the 1.2 ``grade_entry`` downgrade) OR a deep claim was
  emitted but is unverifiable (the 6.2 downgrade target — seam noted, NOT built
  here). Denominator-only.
- ``tool_scanned_only`` — covered ONLY by a zero-token breadth tool
  (``cloc``/``radon``/linter), never read for depth (the state Story 2.6 will
  PRODUCE; this story documents + classifies it). Denominator-only.
- ``inferred`` — the only evidence is narrative/doc (a referencing requirement /
  comment / README), NOT a direct read of the file's own structure — the
  evidence-poisoning class FR8 excludes from gates. **Never** in the numerator.
- ``skipped`` — examined-but-ungradable / not examined (parse-failed,
  budget-skipped, non-analyzable). Denominator-only, never a deep claim.

Decisions LOCKED here (frozen for downstream — Story 2.2/2.3/2.5/2.6)
--------------------------------------------------------------------
- **Grading-rule representation = BOTH.** A ``DEPTH_SEMANTICS: dict[CoverageDepth,
  str]`` description table (the rule as data, exhaustiveness-pinned) AND a pure
  ``classify_depth(evidence)`` over a small frozen :class:`DepthEvidence`
  descriptor (the rule encoded executably so later detectors call it). Reuses the
  1.2 enum; adds NO state.
- **Criticality return type = a closed enum** :class:`Criticality` (``CRITICAL`` /
  ``NORMAL``) — mirrors the 1.2 closed-enum precedent and extends additively if
  Story 2.3 wants tiers. NEVER a ``float`` score (AR4 — the obvious float trap).
- **Criticality signal set (V1, LOCKED).** Content tokens / imports / dotted
  references over the in-memory source (and the optional 1.4 AST entry's
  definition + edge names): security / auth / crypto / governance / secret /
  policy / permission. The filename is at most a WEAK hint, NEVER the decision —
  a security module renamed to ``utils_misc.py`` is still flagged from its content
  (the FR4 anti-gaming requirement: "criticality detected by content, not
  filename"). Matching is case-insensitive and Unicode-aware (so non-ASCII
  identifiers around a critical token are not silently dropped — AI-E1-1).
- **Typed error = :class:`DepthSemanticsError`**, a ``ValueError`` subclass
  localized to this module (mirroring ``RecordingValidationError`` /
  ``CanonicalSerializationError``) — raised on a malformed/empty descriptor.

V1 boundary (do NOT pull forward — Story 2.3 consumes this)
-----------------------------------------------------------
``assess_criticality`` produces the criticality ASSESSMENT only. The operator
DESIGNATION / override and the ``RELEASE_READY``-withheld-when-a-critical-
subsystem-is-below-deep GATE CLAUSE are Story 2.3 (the 1.6
``critical_subsystems_all_deep`` seam stays defaulted-True until 2.3 wires it).
This module adds NO gate clause and NO invocation flag.

PURE (AR8): no filesystem I/O, no clock read, no ``uuid4``/``random``/
``os.getpid()``, no LLM/network, no dict/set-iteration-order reliance. Imports
ONLY the 1.2 ledger enum (and, optionally for typing, the 1.4 AST-index entry).
Joins the import-isolation ``_MODULES_UNDER_GUARD`` gate.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from argus.ledger.coverage_ledger import CoverageDepth

if TYPE_CHECKING:  # pragma: no cover - typing-only, no runtime import (keeps PURE/web-free)
    from argus.index.ast_index import AstIndexEntry

__all__ = [
    "DEPTH_SEMANTICS_SCHEMA_VERSION",
    "DEPTH_SEMANTICS",
    "DepthSemanticsError",
    "EvidenceKind",
    "DepthEvidence",
    "Criticality",
    "CRITICALITY_SIGNAL_TOKENS",
    "classify_depth",
    "assess_criticality",
]

# Single localized source for this contract's schema version (additive-only).
DEPTH_SEMANTICS_SCHEMA_VERSION = "1"


class DepthSemanticsError(ValueError):
    """Raised on a malformed/empty depth-or-criticality descriptor (AR10).

    A ``ValueError`` subclass localized to this module (mirroring
    ``ledger.recording.RecordingValidationError`` /
    ``store.canonical.CanonicalSerializationError``) — the typed failure for an
    unmappable evidence descriptor or a malformed criticality input. NEVER a
    silent coerce / bare ``except: pass`` / ``print()`` in library code.
    """


# ── The canonical five-state grading rule, expressed as data (AC1 / FR5 / FR8) ──
# Exactly the five 1.2 ``CoverageDepth`` members — no new state, no enum edit. The
# AC1 exhaustiveness test pins that this table covers every member with no silent
# default. Only ``audited_deep`` counts toward the deep-% numerator (FR8).
DEPTH_SEMANTICS: dict[CoverageDepth, str] = {
    CoverageDepth.AUDITED_DEEP: (
        "an emitted deep claim is present (FR6 claim-presence; V1 — AST-truth "
        "grounding is Epic-6 Story 6.2 / DF-1-7-B); COUNTS toward the deep-% numerator"
    ),
    CoverageDepth.AUDITED_SHALLOW: (
        "read/analyzed but no qualifying deep claim (silence -> shallow, 1.2 "
        "grade_entry) OR a deep claim emitted-but-unverifiable (the 6.2 downgrade "
        "target — seam, not built here); denominator-only"
    ),
    CoverageDepth.TOOL_SCANNED_ONLY: (
        "covered ONLY by a zero-token breadth tool (cloc/radon/linter), never read "
        "for depth (Story 2.6 PRODUCES this; documented + classified here); "
        "denominator-only"
    ),
    CoverageDepth.INFERRED: (
        "the only evidence is narrative/doc (referencing requirement/comment/README), "
        "NOT a direct structural read — the FR8 evidence-poisoning class; NEVER in the "
        "deep-% numerator"
    ),
    CoverageDepth.SKIPPED: (
        "examined-but-ungradable / not examined (parse-failed, budget-skipped, "
        "non-analyzable); denominator-only, never a deep claim"
    ),
}


class EvidenceKind(str, enum.Enum):
    """The kind of evidence the audit gathered for a file — the ``classify_depth``
    input dimension that selects exactly one :class:`CoverageDepth`.

    Closed, ``str``-valued (the 1.2/1.6 closed-enum precedent). NOT a wire contract
    persisted to ``.argus/`` (the persisted contract is ``CoverageDepth``); this is
    the executable encoding of the grading rule's input.

    - ``DEEP_READ`` — the file's own structure was read for depth (the
      ``audited_deep`` / ``audited_shallow`` path; ``claim_present`` disambiguates).
    - ``TOOL_BREADTH_ONLY`` — covered ONLY by a zero-token breadth tool.
    - ``NARRATIVE_ONLY`` — the only evidence is narrative/doc (the FR8 class).
    - ``UNGRADABLE`` — examined-but-ungradable / not examined.
    """

    DEEP_READ = "deep_read"
    TOOL_BREADTH_ONLY = "tool_breadth_only"
    NARRATIVE_ONLY = "narrative_only"
    UNGRADABLE = "ungradable"


class DepthEvidence(BaseModel):
    """A small frozen evidence descriptor ``classify_depth`` maps to ONE depth.

    ``frozen=True, extra="forbid"`` (the 1.1 ``Envelope`` / 1.2 ``Recording``
    precedent): an unknown field is a typed ``ValidationError``. PURE construction —
    no I/O, no clock, no ``float``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=DEPTH_SEMANTICS_SCHEMA_VERSION,
        description="Depth-semantics schema version (additive-only).",
    )
    kind: EvidenceKind = Field(..., description="The kind of evidence gathered (selects the depth).")
    claim_present: bool = Field(
        default=False,
        description="Whether an emitted deep claim accompanies a DEEP_READ (FR6 disambiguator).",
    )


# Exhaustive evidence-kind -> depth map for ``classify_depth``. A DEEP_READ
# disambiguates on ``claim_present`` (the 1.2 grade_entry rule: claim -> deep,
# silence -> shallow). RAISES on an unmapped kind (no silent default).
_DEPTH_BY_EVIDENCE_KIND: dict[EvidenceKind, CoverageDepth] = {
    EvidenceKind.TOOL_BREADTH_ONLY: CoverageDepth.TOOL_SCANNED_ONLY,
    EvidenceKind.NARRATIVE_ONLY: CoverageDepth.INFERRED,
    EvidenceKind.UNGRADABLE: CoverageDepth.SKIPPED,
}


def classify_depth(evidence: DepthEvidence) -> CoverageDepth:
    """Map an evidence descriptor to EXACTLY ONE :class:`CoverageDepth` (PURE, FR5/FR8).

    Encodes the :data:`DEPTH_SEMANTICS` rule executably so later detectors
    (Story 2.5/2.6) and the readable surface (Story 2.2) consume ONE classifier.
    Reuses the 1.2 enum verbatim and the 1.2 ``grade_entry`` rule (claim -> deep,
    silence -> shallow) for a ``DEEP_READ``; it does NOT re-implement
    ``grade_entry`` (a file-level classifier, not the entry constructor) and does
    NOT add a state. Exhaustive over :class:`EvidenceKind` — raises
    :class:`DepthSemanticsError` on an unmappable descriptor (AR10, no silent
    default).

    The FR8 keystone holds by construction: only ``DEEP_READ`` + ``claim_present``
    yields ``AUDITED_DEEP`` (the only state the 1.6 gate numerator counts);
    ``NARRATIVE_ONLY`` -> ``INFERRED``, ``TOOL_BREADTH_ONLY`` -> ``TOOL_SCANNED_ONLY``,
    ``UNGRADABLE`` -> ``SKIPPED`` are all denominator-only.
    """
    if not isinstance(evidence, DepthEvidence):  # AR10 — typed failure, never a coerce
        raise DepthSemanticsError(
            f"classify_depth requires a DepthEvidence descriptor, got {type(evidence)!r}"
        )
    if evidence.kind is EvidenceKind.DEEP_READ:
        return CoverageDepth.AUDITED_DEEP if evidence.claim_present else CoverageDepth.AUDITED_SHALLOW
    try:
        return _DEPTH_BY_EVIDENCE_KIND[evidence.kind]
    except KeyError as exc:  # pragma: no cover - guarded by the exhaustiveness test
        raise DepthSemanticsError(
            f"no depth mapped for evidence kind {evidence.kind!r}; the grading rule "
            f"must be exhaustive over EvidenceKind (FR5)"
        ) from exc


class Criticality(str, enum.Enum):
    """Closed criticality-assessment vocabulary (FR4-support; NEVER a float, AR4).

    A ``str``-valued closed enum (the 1.2 ``CoverageDepth`` / 1.6 ``Verdict``
    precedent) — extends additively if Story 2.3 wants tiers. The ASSESSMENT only:
    the operator DESIGNATION/override and the gate clause are Story 2.3.
    """

    CRITICAL = "critical"
    NORMAL = "normal"


# V1 content criticality signal tokens (LOCKED). Lower-cased, matched
# case-insensitively as substrings over the source text + the AST entry's
# definition/edge/callee names. The filename is at most a WEAK hint (never the
# decision) — a critical module renamed to a benign name is still flagged from its
# CONTENT (the FR4 anti-gaming requirement). Matching is Unicode-aware via
# ``str.casefold`` so a non-ASCII identifier around a token is not dropped
# (AI-E1-1). Extending the set is additive (NFR-M2) — bump the schema version.
CRITICALITY_SIGNAL_TOKENS: tuple[str, ...] = (
    "auth",
    "crypto",
    "encrypt",
    "decrypt",
    "secret",
    "credential",
    "password",
    "token",
    "signature",
    "hmac",
    "governance",
    "policy",
    "permission",
    "authoriz",
    "privilege",
)


def _content_signal_hit(text: str) -> bool:
    """Whether ``text`` (casefolded) contains any locked criticality token (Unicode-aware)."""
    folded = text.casefold()
    return any(token in folded for token in CRITICALITY_SIGNAL_TOKENS)


def assess_criticality(
    *,
    file_path: str,
    source: str,
    ast_entry: "AstIndexEntry | None" = None,
) -> Criticality:
    """Assess a file's criticality from its CONTENT, not its filename (PURE, FR4).

    Anti-gaming (the FR4 ``hostile-repo`` requirement: "criticality detected by
    content, not filename"): a security-critical module renamed to ``utils_misc.py``
    is still flagged ``CRITICAL`` from its CONTENT signals, so coverage-gaming-by-
    renaming is defeated. The filename is at most a WEAK hint and NEVER the
    decision — only ``source`` (and, when supplied, the 1.4 ``ast_entry``'s
    definition + edge/callee names) carry the signal.

    PURE (AR8): takes the already-read source text and the optional in-memory AST
    entry as ARGUMENTS — it never opens a file. Deterministic; returns the closed
    :class:`Criticality` enum, NEVER a ``float`` score (AR4). Matching is
    case-insensitive and Unicode-aware (``str.casefold``) so a non-ASCII identifier
    around a critical token is correctly classified, not silently dropped (AI-E1-1).

    Raises :class:`DepthSemanticsError` (AR10 typed failure) on a malformed
    descriptor: a non-``str`` ``file_path``/``source``, or an empty ``file_path``.
    An empty ``source`` with no AST signal is a valid, well-formed NORMAL input
    (an empty file is not critical) — not an error.

    V1 boundary: this produces the criticality ASSESSMENT only. The operator
    designation/override and the ``RELEASE_READY``-withheld-when-critical-shallow
    gate clause are Story 2.3 (which consumes this function); the 1.6
    ``critical_subsystems_all_deep`` seam stays defaulted-True until 2.3 wires it.
    """
    if not isinstance(file_path, str) or not isinstance(source, str):
        raise DepthSemanticsError(
            "assess_criticality requires str file_path and str source "
            f"(got {type(file_path)!r}, {type(source)!r})"
        )
    if file_path == "":
        raise DepthSemanticsError(
            "assess_criticality requires a non-empty file_path (AR10 locator-or-reject spirit)"
        )

    if _content_signal_hit(source):
        return Criticality.CRITICAL

    if ast_entry is not None:
        names: list[str] = []
        names.extend(d.name for d in ast_entry.definitions)
        names.extend(e.callee for e in ast_entry.edges)
        if any(_content_signal_hit(name) for name in names):
            return Criticality.CRITICAL

    return Criticality.NORMAL
