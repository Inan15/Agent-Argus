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
- **The merge formula** — FINAL critical set = ``(heuristic_eligible ∪
  operator_designated) − operator_excluded`` (operator designation/exclusion takes
  PRECEDENCE over the content heuristic — the documented correction lever for the 2.1
  reviewer's bare-substring over-flag Low). An operator may FORCE a file critical the
  heuristic missed AND EXCLUDE a heuristic over-flag.
- **Heuristic ELIGIBILITY filter (FR4 as amended, DR-5) + its LOCKED precedence
  order (Story 8.2, boundary B5).** A file this tool can never grade ``audited_deep``
  is ineligible for the HEURISTICALLY-derived critical set — a gate no run can
  satisfy is not a gate, and an operator who learns to ignore one gate learns to
  ignore all of them. Exactly two by-construction classes qualify, and they are the
  closed :class:`CriticalIneligibility` vocabulary: a TEST FILE (``audited_shallow``
  by construction — it is the SUBJECT of the vacuous-test pass) and a CLEAN-PARSED
  ZERO-DEFINITION module (nothing in it to ground a deep claim against). A
  parse-failed / AST-ineligible file is ``skipped`` by CIRCUMSTANCE, not shallow by
  construction, and deliberately stays ELIGIBLE — quietly dropping the one
  security-relevant file the tool could not read would be a false green. The
  precedence order is::

      (i)  eligibility filter — applied to the HEURISTIC term ONLY
      (ii) union with operator designation (EXEMPT from the filter — DR-6)
      (iii) minus operator exclusion (pattern-matched; exclude still wins)

  A path that is ineligible AND excluded is recorded as eligibility-excluded (the
  FIRST rule that removed it), so the disclosure map is a function of the inputs and
  never of evaluation order.
- **The eligibility FACT is DATA, not a computation done here.** It is derived in the
  IMPURE shell (which already owns ``is_test_file`` / ``is_deep_claim_grounded``) and
  carried on :class:`CriticalCandidate`, precisely so this PURE ``ledger/`` module
  never imports a ``detectors/`` or ``audit/`` layer above it — the same ruling the
  pipeline records for the verdict gate's scope membership. The field DEFAULTS to
  ``None`` (= eligible), so a caller that forgets to supply it OVER-includes (a
  stricter gate), never under-includes.
- **A vacuously satisfied gate must be VISIBLE (boundary B3).** Every path the
  eligibility filter removed from the heuristic term is disclosed on the persisted
  result as ``heuristic_excluded_ineligible`` (path → closed reason token), so an
  EMPTY critical set is distinguishable on disk from a repository that genuinely had
  no critical subsystems. An operator-designated path is never recorded there — the
  operator's intent is honoured, not second-guessed.
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
only, the 1.4 AST-index entry) — the Story-8.2 eligibility filter added NO import,
which is exactly why the fact arrives as data. Joins the import-isolation
``_MODULES_UNDER_GUARD`` gate.
"""

from __future__ import annotations

import enum
from fnmatch import fnmatchcase
from typing import TYPE_CHECKING, Iterable

from pydantic import BaseModel, ConfigDict, Field

from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger
from argus.ledger.depth_semantics import Criticality

if TYPE_CHECKING:  # pragma: no cover - typing-only, no runtime import (keeps PURE/web-free)
    pass

__all__ = [
    "CRITICAL_SUBSYSTEMS_SCHEMA_VERSION",
    "CriticalSubsystemError",
    "CriticalIneligibility",
    "CriticalOrigin",
    "CriticalCandidate",
    "CriticalSubsystemSet",
    "identify_critical_subsystems",
    "critical_subsystems_all_deep",
    "critical_subsystems_not_deep",
]

# Single localized source for this contract's schema version (additive-only).
# "1" → "2" (Story 8.2): ``paths`` changed MEANING (the heuristic term is now
# eligibility-filtered) and the model gained an always-serialized disclosure field, so
# the persisted bytes move for every repository. NFR-M2's localized stamp is the
# sanctioned lever; leaving it at "1" would ship an artifact whose version misdescribes
# the contract that produced it.
CRITICAL_SUBSYSTEMS_SCHEMA_VERSION = "2"


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


class CriticalIneligibility(str, enum.Enum):
    """Why a heuristic-CRITICAL file can never be graded ``audited_deep`` (FR4/DR-5).

    A ``str``-valued CLOSED enum (the 1.2/1.6/2.1 precedent) naming exactly the two
    BY-CONSTRUCTION classes FR4 enumerates. It is deliberately not open-ended: every
    member is a class of file the tool stops asking about, so a third one is a
    widening of the tool's blind spot and must be argued at story level rather than
    added in passing.

    NOT a member, deliberately: a parse-failed / AST-ineligible file. That file is
    ``skipped`` by CIRCUMSTANCE (a missing grammar, a syntax error — resolvable), not
    ``audited_shallow`` by construction, and it stays in the heuristic critical set.
    """

    #: A test file — graded ``audited_shallow`` always, because it is the SUBJECT of
    #: the vacuous-test pass rather than a target of deep grounding.
    TEST_FILE = "test_file"
    #: A cleanly-parsed module with ZERO definitions (``__init__.py``, constants-only,
    #: re-export, docstring-only) — nothing in it to ground a deep claim against, and
    #: already downgraded to ``audited_shallow`` by the FR7 grounding rule.
    ZERO_DEFINITION_MODULE = "zero_definition_module"


class CriticalCandidate(BaseModel):
    """A file the identification stage considered, with its content assessment.

    The pure in-memory descriptor the IMPURE caller (the pipeline, which already
    read the source via ``_read_source``) hands to
    :func:`identify_critical_subsystems`. ``frozen=True, extra="forbid"`` (the
    1.1/1.2 precedent). NO ``float``; construction-pure.

    ``ineligibility`` carries the DR-5 eligibility FACT as data: the impure shell —
    which already owns ``is_test_file`` and ``is_deep_claim_grounded`` — derives it,
    so this PURE ``ledger/`` module never imports the ``detectors/`` / ``audit/``
    layers above it. ``None`` means ELIGIBLE, and it is the default, so a caller that
    does not supply the fact keeps the pre-8.2 behaviour and fails toward a STRICTER
    gate rather than a false green.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="Repo-root-relative POSIX path (the deterministic sort key).")
    criticality: Criticality = Field(
        ..., description="Content-derived criticality (the 2.1 assess_criticality result; closed enum)."
    )
    ineligibility: CriticalIneligibility | None = Field(
        default=None,
        description="Why this file can never be audited_deep, or None when it is ELIGIBLE (DR-5).",
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
    and conservatively withhold ``RELEASE_READY``. ``heuristic_excluded_ineligible``
    discloses every path the DR-5 eligibility filter removed from the HEURISTIC term
    and why (boundary B3 — a vacuously satisfied gate must be visible; an EMPTY
    ``paths`` with a non-empty map is a very different claim from an empty ``paths``
    with an empty one). NO ``float`` (AR4); any JSON of this model routes through the
    single 1.1 ``store/canonical.dumps``.
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
    heuristic_excluded_ineligible: dict[str, CriticalIneligibility] = Field(
        default_factory=dict,
        description="Paths the DR-5 eligibility filter removed from the heuristic term → the reason (B3).",
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


def _matches_exclusion(path: str, patterns: frozenset[str]) -> bool:
    """True iff *path* is removed by any exclusion *pattern* (PURE, deterministic).

    Exact match was the whole of the original rule, which made the documented escape
    hatch unusable at real scale: clearing an over-flagged directory required one
    ``--exclude-critical`` flag per file (62 of them on this repository). An escape
    hatch nobody can afford to use is not an escape hatch, and an unsatisfiable gate
    trains operators to ignore every gate.

    Three forms, checked in order — all deterministic, no filesystem access (AR8):

    1. **exact** — ``argus/cli.py`` (the original behaviour, unchanged).
    2. **directory prefix** — ``tests`` or ``tests/`` removes the whole subtree.
    3. **glob** — ``*_test.py``, ``argus/*/__init__.py`` via ``fnmatchcase``.

    Matching is CASE-SENSITIVE (``fnmatchcase``, never ``fnmatch``): ``fnmatch``
    normalizes case per the HOST platform, which would make the same designation
    behave differently on Windows and Linux and break the byte-identical-across-hosts
    guarantee (NFR-P1/AR4).
    """
    for pattern in patterns:
        if path == pattern:
            return True
        prefix = pattern if pattern.endswith("/") else pattern + "/"
        if path.startswith(prefix):
            return True
        if fnmatchcase(path, pattern):
            return True
    return False


def identify_critical_subsystems(
    candidates: Iterable[CriticalCandidate],
    *,
    operator_designated: Iterable[str] | None = None,
    operator_excluded: Iterable[str] | None = None,
) -> CriticalSubsystemSet:
    """Build the final critical-file set: heuristic ∪ operator − excluded (PURE, FR4).

    The heuristic critical set is every ``candidate`` whose ``criticality`` is
    :attr:`Criticality.CRITICAL` (derived upstream by the REUSED 2.1
    ``assess_criticality`` — this function does NOT re-assess) **and** whose
    ``ineligibility`` is ``None``. The DR-5 eligibility filter is applied to the
    HEURISTIC term ONLY, before the union, because operator designation is EXEMPT
    from it (DR-6) — that exemption is only expressible in this order. Each filtered
    path is disclosed in ``heuristic_excluded_ineligible`` with its reason, so an
    emptied critical set can never look like a repository that had none (B3).

    The operator channel is applied with PRECEDENCE:

    - ``operator_designated`` FORCES a path critical (even a heuristic-NORMAL or
      heuristic-absent path) — the lever for a true critical the substring matcher
      missed.
    - ``operator_excluded`` REMOVES paths from the final set — the documented
      correction for a 2.1 substring over-flag. **Exclude wins on a tie** (a path in
      both add and exclude is excluded). Each entry is PATTERN-matched by
      :func:`_matches_exclusion` (exact path, directory prefix, or glob), so
      ``--exclude-critical tests`` clears a subtree in one flag instead of one flag
      per file.

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
    excluded = frozenset(_coerce_path_tuple(operator_excluded, label="operator_excluded"))

    candidate_paths: set[str] = set()
    heuristic: set[str] = set()
    ineligible: dict[str, CriticalIneligibility] = {}
    for candidate in candidates:
        if not isinstance(candidate, CriticalCandidate):
            raise CriticalSubsystemError(
                f"identify_critical_subsystems requires CriticalCandidate items, got {type(candidate)!r}"
            )
        candidate_paths.add(candidate.file_path)
        if candidate.criticality is not Criticality.CRITICAL:
            continue
        # (i) The DR-5 eligibility filter — HEURISTIC term only. A file that can never
        # be graded audited_deep is partitioned out and DISCLOSED rather than dropped.
        if candidate.ineligibility is None:
            heuristic.add(candidate.file_path)
        else:
            ineligible[candidate.file_path] = candidate.ineligibility

    # (ii) union with operator designation (EXEMPT from the filter — DR-6), then
    # (iii) − operator_excluded — exclude still wins on a tie. Exclusion is
    # PATTERN-matched (exact / directory-prefix / glob) rather than a plain set
    # difference; the exclude-wins-on-a-tie precedence is unchanged.
    final = {
        path
        for path in (heuristic | designated)
        if not _matches_exclusion(path, excluded)
    }

    # Disclosure (B3). An operator-designated path is NEVER reported as
    # eligibility-excluded — it is in ``final`` on the operator's authority, and
    # claiming the filter removed it would be false. An ineligible-AND-excluded path
    # IS reported: eligibility is the first rule that removed it, which keeps the map a
    # function of the inputs rather than of evaluation order.
    excluded_ineligible = {
        path: reason for path, reason in sorted(ineligible.items()) if path not in designated
    }

    origins: dict[str, CriticalOrigin] = {}
    for path in final:
        # Operator intent is the visible origin when a path was explicitly designated.
        if path in designated:
            origins[path] = CriticalOrigin.OPERATOR_DESIGNATED
        else:
            origins[path] = CriticalOrigin.HEURISTIC

    unmatched = {
        path
        for path in designated
        if path not in candidate_paths and not _matches_exclusion(path, excluded)
    }

    return CriticalSubsystemSet(
        paths=tuple(sorted(final)),
        origins=origins,
        designated_but_unmatched=tuple(sorted(unmatched)),
        heuristic_excluded_ineligible=excluded_ineligible,
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
    return not critical_subsystems_not_deep(critical_paths, ledger)


def critical_subsystems_not_deep(
    critical_paths: Iterable[str],
    ledger: CoverageLedger,
) -> tuple[str, ...]:
    """Return the SORTED critical paths that are not ``audited_deep`` (PURE, FR16).

    The evidence behind :func:`critical_subsystems_all_deep`, which is defined as
    "this is empty". Kept as the single implementation so the boolean and the
    explanation can never disagree.

    Exists because a bare ``False`` is not actionable. An operator told only that
    "at least one critical subsystem is not audited deep" cannot act; told WHICH
    files, and at what depth each landed, they can. The returned paths are recorded
    on the verdict and rendered in the report.

    A designated-critical path ABSENT from the ledger is included (the conservative
    unmatched-path policy — an unexamined critical file is not a satisfied one).

    PURE (AR8): a fold over the in-memory ledger; no I/O, no clock, no LLM, no
    set-iteration-order reliance (the result is sorted). Raises
    :class:`CriticalSubsystemError` (AR10) on a non-``CoverageLedger`` ``ledger``
    argument or a non-``str`` critical path — never a silent coerce.
    """
    if not isinstance(ledger, CoverageLedger):
        raise CriticalSubsystemError(
            f"critical_subsystems_not_deep requires a CoverageLedger, got {type(ledger)!r}"
        )
    critical = _coerce_path_tuple(critical_paths, label="critical_paths")
    if not critical:
        return ()

    deep_paths = {
        entry.file_path
        for entry in ledger.entries
        if entry.depth is CoverageDepth.AUDITED_DEEP
    }
    return tuple(sorted(path for path in critical if path not in deep_paths))
