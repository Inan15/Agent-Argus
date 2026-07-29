"""PURE critical-subsystem identification + operator designation + all-deep gate.

Drivers: ArgusAgent-FR-4 (the central driver — ArgusAgent identifies critical subsystems by
file CONTENT *and* an operator can designate/override them, so coverage gates can
require them examined deeply), ArgusAgent-FR-16 (the "all critical subsystems deep"
clause of the coverage gate — ``RELEASE_READY`` is withheld when a critical
subsystem is below ``audited_deep``; this module SUPPLIES the boolean the Story-1.6
``evaluate_verdict(..., critical_subsystems_all_deep=...)`` seam already consumes,
WITHOUT forking the verdict math), ArgusAgent-FR-30 (the headless invocation contract —
the operator-designation channel is an additive ``AuditRequest`` field + CLI flag,
populated upstream and threaded in as ARGUMENTS here), ArgusAgent-NFR-D2 (deterministic,
zero-LLM-token — pure identification/predicate over recorded inputs), ArgusAgent-NFR-P1
(byte-identical critical set + verdict across hosts/runs for the same
repo+designations — sorted output, no set/dict iteration-order reliance), ArgusAgent-NFR-M2
(frozen, additive-only contracts — a localized ``schema_version``), ArgusAgent-NFR-M1
(≤1200-line files), AR4 (no ``float`` — criticality is the closed 2.1
``Criticality`` enum, the predicate returns ``bool``, counts/paths are ``int``/``str``;
any JSON routes through the single 1.1 ``store/canonical.dumps``), AR8 (PURE — the
identification + designation merge + ``critical_subsystems_all_deep`` predicate
perform NO filesystem I/O, NO clock read, NO ``uuid4``/``random``, NO LLM/network;
the file READ + pipeline wiring + CLI parse are the impure shell), AR10 (typed
failure — a malformed input raises a localized ``ValueError`` subclass, never a
silent coerce / bare ``except: pass`` / ``print()`` in library code).

Why this module exists (the FR4 + FR16 wire-the-seam story)
-----------------------------------------------------------
Story 2.1 built the content-derived criticality ASSESSMENT
(``assess_criticality`` → the closed ``Criticality`` enum). Story 1.6 built the
verdict gate with the FR16 critical-subsystem clause ALREADY present as the
additive ``critical_subsystems_all_deep: bool = True`` seam (defaulted satisfied).
This module is the missing middle: it (a) IDENTIFIES the heuristic critical-file
set by REUSING ``assess_criticality`` verbatim (NO second criticality enum / token
set / matcher), (b) merges OPERATOR designations with PRECEDENCE over the heuristic,
and (c) computes the ``critical_subsystems_all_deep`` boolean the gate consumes —
so a critical-but-shallow subsystem withholds ``RELEASE_READY`` without re-shaping
the gate (the advisory moat + locked vocabulary stay intact).

Decisions LOCKED here (frozen for downstream — recorded per the story)
----------------------------------------------------------------------
- **Module placement** — ``ledger/critical_subsystems.py`` (cohesive with the 2.1
  ``ledger/depth_semantics.assess_criticality`` it consumes). Repository
  partitioning proper is ``index/partitioner.py`` (Story 2.4) — NOT here; a critical
  subsystem is a content-derived + operator-adjusted FILE SET in V1, ``partition_id``
  stays ``"root"``.
- **The merge formula** — FINAL critical set = ``(heuristic ∪ operator_designated)
  − operator_excluded`` (operator designation/exclusion takes PRECEDENCE over the
  content heuristic — the documented correction lever for the 2.1 reviewer's
  bare-substring over-flag Low). An operator may FORCE a file critical the heuristic
  missed AND EXCLUDE a heuristic over-flag.
- **Add-vs-exclude tie policy = EXCLUDE WINS.** A path that is in BOTH the operator
  add set and the operator exclude set is EXCLUDED. An explicit ``--exclude-critical``
  is the unambiguous "this is not critical" lever; this is the safe direction for
  the correction-of-a-false-positive use case the seam exists to serve.
- **Unmatched-path policy (conservative, never a silent drop).** A force-critical
  path that matches NO analyzable file is RECORDED in the final set as a
  ``designated-but-unmatched`` member: it is part of the critical set, has no ledger
  entry, and therefore is NOT ``audited_deep`` — so it behaves conservatively toward
  WITHHOLDING ``RELEASE_READY`` (an operator typo cannot quietly WEAKEN the gate; it
  can only make it stricter, the safe direction). An exclude path matching nothing
  is a no-op (it removes what is not there). The set of designated-but-unmatched
  paths is exposed on the result for the impure caller to surface.
- **Provenance** — the frozen :class:`CriticalSubsystemSet` carries the sorted final
  ``paths`` plus a per-path :class:`CriticalOrigin` (``HEURISTIC`` /
  ``OPERATOR_DESIGNATED`` — a path that is BOTH heuristic AND operator-forced is
  recorded ``OPERATOR_DESIGNATED`` so the operator intent is visible) and the sorted
  ``designated_but_unmatched`` tuple.
- **Typed error = :class:`CriticalSubsystemError`**, a ``ValueError`` subclass
  localized to this module (mirroring ``DepthSemanticsError`` /
  ``CoverageReportError`` / ``RecordingValidationError``) — raised on a malformed
  input (a non-``str`` designation path, a non-iterable designation set, a
  non-``CoverageLedger`` predicate argument).

PURE (AR8): no filesystem I/O, no clock, no LLM, no ``uuid4``/``random``, no
set/dict iteration-order reliance. Imports ONLY the 2.1 ``depth_semantics``
(``assess_criticality`` / ``Criticality``) + the 1.2 ledger models (and, for typing
only, the 1.4 AST-index entry). Joins the import-isolation ``_MODULES_UNDER_GUARD``
gate.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Iterable

from pydantic import BaseModel, ConfigDict, Field

from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger
from argus.ledger.depth_semantics import Criticality

if TYPE_CHECKING:  # pragma: no cover - typing-only, no runtime import (keeps PURE/web-free)
    pass

__all__ = [
    "CRITICAL_SUBSYSTEMS_SCHEMA_VERSION",
    "CriticalSubsystemError",
    "CriticalOrigin",
    "CriticalCandidate",
    "CriticalSubsystemSet",
    "identify_critical_subsystems",
    "critical_subsystems_all_deep",
]

# Single localized source for this contract's schema version (additive-only).
CRITICAL_SUBSYSTEMS_SCHEMA_VERSION = "1"


class CriticalSubsystemError(ValueError):
    """Raised on a malformed critical-subsystem input (AR10).

    A ``ValueError`` subclass localized to this module (mirroring
    ``depth_semantics.DepthSemanticsError`` /
    ``coverage_report.CoverageReportError``) — the typed failure for a non-``str``
    designation path, a non-iterable designation set, or a non-``CoverageLedger``
    predicate argument. NEVER a silent coerce / bare ``except: pass`` / ``print()``
    in library code.
    """


class CriticalOrigin(str, enum.Enum):
    """Why a file is in the final critical set — per-path provenance (FR4).

    A ``str``-valued closed enum (the 1.2/1.6/2.1 closed-enum precedent). A path
    that is BOTH heuristic-critical AND operator-force-critical is recorded
    ``OPERATOR_DESIGNATED`` so the operator's explicit intent is the visible origin.
    """

    HEURISTIC = "heuristic"
    OPERATOR_DESIGNATED = "operator_designated"


class CriticalCandidate(BaseModel):
    """A file the identification stage considered, with its content assessment.

    The pure in-memory descriptor the IMPURE caller (the pipeline, which already
    read the source via ``_read_source``) hands to
    :func:`identify_critical_subsystems`. ``frozen=True, extra="forbid"`` (the
    1.1/1.2 precedent). NO ``float``; construction-pure.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="Repo-root-relative POSIX path (the deterministic sort key).")
    criticality: Criticality = Field(
        ..., description="Content-derived criticality (the 2.1 assess_criticality result; closed enum)."
    )


class CriticalSubsystemSet(BaseModel):
    """Frozen final critical-file set + per-path provenance (FR4 / NFR-M2).

    ``frozen=True, extra="forbid"`` (the 1.1 ``Envelope`` / 1.2 ``Recording`` / 1.6
    ``AuditVerdict`` precedent): an unknown field on read-back is a typed
    ``ValidationError``. ``paths`` are SORTED by ``file_path`` (AR4 / NFR-P1 — no
    set-iteration-order reliance). ``origins`` maps each final path to its
    :class:`CriticalOrigin`. ``designated_but_unmatched`` holds operator-forced paths
    that match no analyzable candidate (the conservative unmatched-path policy): they
    ARE in ``paths`` but have no ledger entry, so they can never be ``audited_deep``
    and conservatively withhold ``RELEASE_READY``. NO ``float`` (AR4); any JSON of
    this model routes through the single 1.1 ``store/canonical.dumps``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=CRITICAL_SUBSYSTEMS_SCHEMA_VERSION,
        description="Critical-subsystem schema version (localized constant; additive-only).",
    )
    paths: tuple[str, ...] = Field(
        default=(), description="The final critical-file set, sorted by file_path (AR4/NFR-P1)."
    )
    origins: dict[str, CriticalOrigin] = Field(
        default_factory=dict, description="Per-path provenance (heuristic vs operator-designated)."
    )
    designated_but_unmatched: tuple[str, ...] = Field(
        default=(),
        description="Operator-forced critical paths matching no analyzable candidate (conservative; sorted).",
    )


def _coerce_path_tuple(paths: Iterable[str] | None, *, label: str) -> tuple[str, ...]:
    """Validate an operator designation set → a tuple of paths (AR10 typed failure).

    ``None`` is treated as the empty set (the default-unused channel). A non-iterable
    set, or any non-``str`` member, raises :class:`CriticalSubsystemError` — never a
    silent coerce. Order is NOT relied upon (the merge sorts); duplicates are
    tolerated (set semantics apply downstream).
    """
    if paths is None:
        return ()
    if isinstance(paths, (str, bytes)):
        raise CriticalSubsystemError(
            f"{label} must be an iterable of str paths, not a bare {type(paths).__name__}"
        )
    try:
        members = tuple(paths)
    except TypeError as exc:  # not iterable
        raise CriticalSubsystemError(
            f"{label} must be an iterable of str paths (got {type(paths)!r})"
        ) from exc
    for member in members:
        if not isinstance(member, str):
            raise CriticalSubsystemError(
                f"{label} entries must be str paths; got {type(member)!r}"
            )
    return members


def identify_critical_subsystems(
    candidates: Iterable[CriticalCandidate],
    *,
    operator_designated: Iterable[str] | None = None,
    operator_excluded: Iterable[str] | None = None,
) -> CriticalSubsystemSet:
    """Build the final critical-file set: heuristic ∪ operator − excluded (PURE, FR4).

    The heuristic critical set is every ``candidate`` whose ``criticality`` is
    :attr:`Criticality.CRITICAL` (derived upstream by the REUSED 2.1
    ``assess_criticality`` — this function does NOT re-assess). The operator channel
    is applied with PRECEDENCE:

    - ``operator_designated`` FORCES a path critical (even a heuristic-NORMAL or
      heuristic-absent path) — the lever for a true critical the substring matcher
      missed.
    - ``operator_excluded`` REMOVES a path from the final set — the documented
      correction for a 2.1 substring over-flag. **Exclude wins on a tie** (a path in
      both add and exclude is excluded).

    Unmatched policy (conservative): a force-critical path that matches no candidate
    is recorded in ``paths`` AND in ``designated_but_unmatched`` — it has no ledger
    entry, so it can never be ``audited_deep`` and withholds ``RELEASE_READY`` (an
    operator typo can only make the gate stricter, never weaker). An exclude path
    matching nothing is a no-op.

    PURE (AR8): operates over the in-memory ``candidates`` (the impure caller did the
    read). Deterministic: ``paths`` + ``designated_but_unmatched`` are sorted; NO
    set/dict-iteration-order reliance (NFR-P1). Raises
    :class:`CriticalSubsystemError` on a malformed input (AR10).
    """
    designated = set(_coerce_path_tuple(operator_designated, label="operator_designated"))
    excluded = set(_coerce_path_tuple(operator_excluded, label="operator_excluded"))

    candidate_paths: set[str] = set()
    heuristic: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, CriticalCandidate):
            raise CriticalSubsystemError(
                f"identify_critical_subsystems requires CriticalCandidate items, got {type(candidate)!r}"
            )
        candidate_paths.add(candidate.file_path)
        if candidate.criticality is Criticality.CRITICAL:
            heuristic.add(candidate.file_path)

    # (heuristic ∪ operator_designated) − operator_excluded — exclude wins on a tie.
    final = (heuristic | designated) - excluded

    origins: dict[str, CriticalOrigin] = {}
    for path in final:
        # Operator intent is the visible origin when a path was explicitly designated.
        if path in designated:
            origins[path] = CriticalOrigin.OPERATOR_DESIGNATED
        else:
            origins[path] = CriticalOrigin.HEURISTIC

    unmatched = (designated - excluded) - candidate_paths

    return CriticalSubsystemSet(
        paths=tuple(sorted(final)),
        origins=origins,
        designated_but_unmatched=tuple(sorted(unmatched)),
    )


def critical_subsystems_all_deep(
    critical_paths: Iterable[str],
    ledger: CoverageLedger,
) -> bool:
    """Return ``True`` iff EVERY critical path is graded ``audited_deep`` (PURE, FR16).

    The boolean the Story-1.6 ``evaluate_verdict(..., critical_subsystems_all_deep=...)``
    seam consumes. An EMPTY critical set returns ``True`` (vacuously all-deep — the
    regression-safe default that keeps a no-critical repo byte-identical to the
    pre-2.3 pipeline). A critical file graded ``audited_shallow`` /
    ``tool_scanned_only`` / ``inferred`` / ``skipped`` — or a designated-critical
    file ABSENT from the ledger (the conservative unmatched-path policy) — returns
    ``False`` (withholds ``RELEASE_READY``).

    PURE (AR8): a fold over the in-memory ledger; no I/O, no clock, no LLM, no
    set-iteration-order reliance. Raises :class:`CriticalSubsystemError` (AR10) on a
    non-``CoverageLedger`` ``ledger`` argument or a non-``str`` critical path — never
    a silent coerce.
    """
    if not isinstance(ledger, CoverageLedger):
        raise CriticalSubsystemError(
            f"critical_subsystems_all_deep requires a CoverageLedger, got {type(ledger)!r}"
        )
    critical = _coerce_path_tuple(critical_paths, label="critical_paths")
    if not critical:
        return True

    deep_paths = {
        entry.file_path
        for entry in ledger.entries
        if entry.depth is CoverageDepth.AUDITED_DEEP
    }
    return all(path in deep_paths for path in critical)
