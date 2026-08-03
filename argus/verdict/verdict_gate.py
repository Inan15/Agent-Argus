"""PURE release-readiness verdict gate — fold + finding ordering + exit code.

Drivers: ArgusAgent-FR-15 (release-readiness verdict as a PURE function of the coverage
ledger), ArgusAgent-FR-16 (gate+floor core: ``RELEASE_READY`` only when gates met —
≥60% deep + 0 blocking findings; ``INSUFFICIENT_COVERAGE`` below the 20% floor;
never a default block), ArgusAgent-FR-8-honored (``inferred`` evidence can never satisfy
a gate — honored by the gate's coverage math), ArgusAgent-FR-18 (deterministic exit code
+ machine-readable verdict artifact), ArgusAgent-FR-33 (order findings by verdict impact
— verdict-blocking before non-blocking, alarm-fatigue defense), ArgusAgent-NFR-D2
(deterministic, zero-LLM-token verdict — a pure fold over recorded inputs),
ArgusAgent-NFR-D3 (content hash over the canonical payload only), ArgusAgent-NFR-M1
(≤1200-line files), ArgusAgent-NFR-M2 (frozen, additive-only Pydantic v2 contracts),
AR3 (exit-code wire contract ``0``/``2``/``3``/``1``), AR4 (single canonical
serializer; ratios stored fixed-precision ``Fraction``/``Decimal``, NEVER
``float``; no clock/uuid/random/iteration-order), AR8 (pure/impure separation —
the verdict gate is PURE: imports only ledger/finding models, no I/O, no
``dispatch()``), cross-cutting #6 (advisory-by-contract: a heuristic-only finding
can never drive a release-blocking verdict — the false-accusation moat).

Why this module exists
----------------------
The entire determinism architecture exists so that the terminal stage — the
verdict — is a *pure function of a fixed-enum coverage ledger*. This module cashes
that payoff: a function that imports ONLY the 1.2 ledger/finding models, reads NO
file, calls NO ``dispatch()``, reads NO clock, and produces a verdict + ordered
findings + exit code that is byte-reproducible and provably token-free.

Contract decisions LOCKED here (frozen for every downstream consumer)
--------------------------------------------------------------------
- **Verdict vocabulary** — a ``str``-valued ``enum.Enum`` (``Verdict``, mirroring
  the 1.2 ``CoverageDepth``) with EXACTLY three members: ``RELEASE_READY`` /
  ``NOT_READY_FOR_RELEASE`` / ``INSUFFICIENT_COVERAGE``. ``BLOCKED`` is the
  documented demo SHORTHAND for ``NOT_READY_FOR_RELEASE`` (the two names denote
  ONE blocking concept) — exposed as the module constant ``BLOCKED`` aliasing the
  enum member, NOT a fourth member. There is no ``ERROR`` verdict — ``crash`` is
  the exit code ``1``, never a verdict the gate emits.
- **Gate thresholds (decision table, evaluated IN ORDER)** — with
  ``deep_ratio = Fraction(deep_count, total)`` and
  ``blocking = (# findings where depth_supported is not None)``:

  | condition (evaluated in order)                                       | verdict                | exit |
  |----------------------------------------------------------------------|------------------------|------|
  | ``total == 0`` OR ``deep_ratio < Fraction(1, 5)`` (< 20%)            | INSUFFICIENT_COVERAGE  | 3    |
  | ``deep_ratio >= Fraction(3, 5)`` (≥ 60%) AND ``blocking == 0`` AND   |                        |      |
  | ``critical_subsystems_all_deep``                                     | RELEASE_READY          | 0    |
  | otherwise (≥ 20% AND (< 60% OR ≥1 blocking OR a critical not deep))  | NOT_READY_FOR_RELEASE  | 2    |

  Boundary semantics LOCKED: ``RELEASE_READY`` at deep-% ``>= 60%`` (inclusive);
  ``INSUFFICIENT_COVERAGE`` at deep-% ``< 20%`` (strict — exactly-20% is
  assessable/blocking-eligible).
- **Floor-vs-blocking precedence = FLOOR WINS** — a below-20% ledger returns
  ``INSUFFICIENT_COVERAGE`` EVEN WITH blocking findings. Rationale: below the floor
  ArgusAgent has not assessed enough to honestly claim it saw enough to BLOCK either; low
  coverage is ArgusAgent's limitation to report, not a verdict to render. The floor row
  is evaluated FIRST. Pinned by a test.
- **``inferred`` never satisfies a gate (FR8)** — the deep-% numerator counts ONLY
  ``audited_deep`` entries (via ``CoverageLedger.deep_count()``); ``inferred`` /
  ``skipped`` / ``tool_scanned_only`` / ``audited_shallow`` are in the DENOMINATOR
  (``total()``) but NEVER the numerator. So a 100%-``inferred`` ledger is 0% deep,
  below the floor → ``INSUFFICIENT_COVERAGE``.
- **Advisory-by-contract eligibility predicate = ``depth_supported is not None``**
  (cross-cutting #6, the moat). A finding is verdict-blocking ⇔ it is
  verdict-eligible ⇔ it carries an AST-corroborated supported depth
  (``depth_supported is not None``). NOT keyed on ``advisory`` — the 1.5 detector
  keeps ``advisory=True`` on BOTH its heuristic-only AND AST-corroborated findings
  (the demo line stays ``🔴 tests *appear* vacuous``), so ``advisory`` does NOT
  distinguish them; ``depth_supported`` does. A heuristic-only finding
  (``depth_supported is None``) can NEVER move the verdict to a blocking state,
  regardless of its ``advisory`` flag — a wrong 🔴 is the lethal failure. The
  Epic-6 Prosecutor refines the eligible finding set UPSTREAM without changing this
  gate's contract.
- **Finding ordering (FR33)** — verdict-blocking (eligible) findings sort STRICTLY
  before non-blocking ones (alarm-fatigue defense), with a TOTAL deterministic
  tie-break: ``(not eligible, depth_rank, rule_id, recording_id)`` — primary
  blocking-first, then a documented supported-depth rank (deepest first), then
  ``rule_id``, final ``recording_id`` lexicographic so the order is fully
  determined with NO input/iteration-order reliance (AR4). Two runs over the same
  findings in different input orders produce the identical ordered tuple.
- **Exit-code mapping (AR3, the wire contract)** — EXACTLY ``RELEASE_READY → 0``,
  ``NOT_READY_FOR_RELEASE → 2``, ``INSUFFICIENT_COVERAGE → 3``, ``crash → 1``. The
  mapping is exhaustive over the verdict enum (a ``match`` that RAISES on an
  unmapped member — never a silent default), so adding a verdict member without a
  code is a build-time failure. The gate is a TOTAL pure function and never raises
  to produce ``1``; ``1`` is reserved for the Story-1.7 pipeline's AR10
  typed-finding/uncaught-error degradation (the gate exposes the MAPPING; the
  pipeline owns producing ``1`` on an actual crash).
- **``AuditVerdict`` result model** — frozen ``extra="forbid"`` (the 1.1/1.2
  precedent). Carries every field a machine consumer (Story 1.7 / a CI gate) reads
  at birth (FR18 / NFR-M2 additive-only): ``verdict``, ``deep_ratio: Fraction``
  (NEVER ``float``), per-depth counts, ``blocking_finding_count``,
  ``ordered_findings``, ``exit_code``, ``schema_version``. NO volatile
  ``run_id``/``created_at`` — those belong to the Story-1.7 envelope around it
  (NFR-D3 hash-over-payload-only); the gate result is the pure payload.
- **Critical-subsystem-clause seam (Story 2.3)** — the FR16 "all critical
  subsystems deep" clause is NOT built here. It inserts ADDITIVELY via the optional
  ``critical_subsystems_all_deep: bool = True`` parameter on
  :func:`evaluate_verdict`, which defaults to satisfied in V1. Story 2.3 supplies
  the real value from the (then-built) critical-subsystem designation; this story
  builds only the gate that honors it.
- **Assessment-scope seam — DISCLOSED narrowing, never a floor bypass** — the
  deep-% denominator defaults to the whole ledger. The optional ``scope_paths``
  parameter narrows the ASSESSED POPULATION (the caller supplies membership as data;
  the gate never classifies files, preserving AR8 import isolation). It exists for
  the test-heavy repository, where entries graded ``audited_shallow`` BY CONSTRUCTION
  (test files — the subject of the vacuous pass, never a deep-grounding target)
  swamp the denominator and manufacture a ``NOT_READY_FOR_RELEASE`` carrying ZERO
  blocking findings. LOCKED invariants: the floor and the RELEASE_READY threshold are
  BOTH re-applied WITHIN the narrowed population (a narrowing may change what is
  claimed, NEVER the bar for claiming it — an under-audited application is still
  ``INSUFFICIENT_COVERAGE``); ``findings`` are NOT filtered, so a blocking finding in
  a held-out file still blocks; and a :class:`CoverageScope` disclosure is attached to
  the result, so a scoped ``RELEASE_READY`` can never be read without its scope.
  ``deep_ratio``/``deep_count``/``total_count`` keep their whole-ledger meaning. An
  unscoped call is byte-identical to the pre-seam fold (``coverage_scope`` is omitted
  from the canonical payload entirely, not serialized as ``null``).

This module is PURE (AR8): no I/O, no clock, no LLM, no ``uuid4``/``random``, no
set/dict iteration-order reliance. It imports ONLY the 1.2 ledger/finding models
(and is appended to the import-isolation ``_MODULES_UNDER_GUARD`` gate).
"""

from __future__ import annotations

import enum
from fractions import Fraction

from pydantic import BaseModel, ConfigDict, Field

from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger
from argus.ledger.recording import Recording

__all__ = [
    "VERDICT_SCHEMA_VERSION",
    "RELEASE_READY_DEEP_THRESHOLD",
    "INSUFFICIENT_COVERAGE_FLOOR",
    "Verdict",
    "BLOCKED",
    "CoverageScope",
    "AuditVerdict",
    "is_verdict_blocking",
    "blocking_finding_count",
    "order_findings",
    "exit_code_for_verdict",
    "evaluate_verdict",
]

# Single localized source for this contract's schema version (additive-only;
# part of the hashed payload — a bump deliberately changes the content hash).
VERDICT_SCHEMA_VERSION = "1"

# LOCKED gate thresholds — exact fixed-precision Fractions (NEVER float, AR4).
# RELEASE_READY requires deep-% >= 60% (inclusive); INSUFFICIENT_COVERAGE is
# deep-% < 20% (strict, so exactly-20% is assessable/blocking-eligible).
RELEASE_READY_DEEP_THRESHOLD = Fraction(3, 5)  # 60%
INSUFFICIENT_COVERAGE_FLOOR = Fraction(1, 5)  # 20%


class Verdict(str, enum.Enum):
    """Closed, fixed-enum release-readiness verdict vocabulary (FR15 / Contract).

    The string VALUES are the wire contract — serialized verbatim through
    ``store/canonical.dumps``. EXACTLY three members; the membership set is pinned
    by a committed test so adding/removing/renaming a verdict fails the build. A
    genuinely new verdict is an additive ``schema_version`` bump, never an edit.

    ``BLOCKED`` is NOT a member — it is the documented demo SHORTHAND for
    ``NOT_READY_FOR_RELEASE`` (the two names denote ONE blocking concept), exposed
    as the module constant :data:`BLOCKED`. ``crash`` is the exit code ``1``, never
    a verdict the gate emits — there is deliberately no ``ERROR`` member.
    """

    RELEASE_READY = "RELEASE_READY"
    NOT_READY_FOR_RELEASE = "NOT_READY_FOR_RELEASE"
    INSUFFICIENT_COVERAGE = "INSUFFICIENT_COVERAGE"


# Documented demo shorthand: BLOCKED denotes the NOT_READY_FOR_RELEASE concept.
BLOCKED = Verdict.NOT_READY_FOR_RELEASE

# Exhaustive verdict → exit-code map (AR3 wire contract). Used by
# exit_code_for_verdict, which RAISES on a member missing here (no silent default).
_EXIT_CODE_BY_VERDICT: dict[Verdict, int] = {
    Verdict.RELEASE_READY: 0,
    Verdict.NOT_READY_FOR_RELEASE: 2,
    Verdict.INSUFFICIENT_COVERAGE: 3,
}

# Deterministic supported-depth tie-break rank (deepest first) for the FR33
# ordering. A finding's depth_supported being None means verdict-ineligible
# (sorts after every eligible finding via the primary `not eligible` key); the
# rank only differentiates eligible findings among themselves.
_DEPTH_ORDER_RANK: dict[CoverageDepth, int] = {
    CoverageDepth.AUDITED_DEEP: 0,
    CoverageDepth.AUDITED_SHALLOW: 1,
    CoverageDepth.TOOL_SCANNED_ONLY: 2,
    CoverageDepth.INFERRED: 3,
    CoverageDepth.SKIPPED: 4,
}


class CoverageScope(BaseModel):
    """Frozen DISCLOSURE record of a narrowed assessment scope (FR16 / negative assurance).

    The gate's deep-% is, by default, taken over the WHOLE ledger. A repository whose
    test files outnumber its application files drags that ratio down even when every
    application file was audited deep — the ledger grades a test file
    ``audited_shallow`` by construction (it is the SUBJECT of the vacuous-test pass,
    not a target of deep grounding). Folding those shallow-by-design entries into the
    denominator produces a FALSE NEGATIVE: ``NOT_READY_FOR_RELEASE`` with zero
    blocking findings, purely because the repo is well-tested.

    Narrowing the assessed population is the honest fix — but ONLY when the narrowing
    is DISCLOSED. That is what this model is: the machine-readable record of what was
    actually assessed and what was held out, carried on the verdict itself so no
    consumer can read a scoped ``RELEASE_READY`` without also reading its scope.

    The narrowing NEVER weakens the floor. :data:`INSUFFICIENT_COVERAGE_FLOOR` is
    re-applied WITHIN the narrowed population (see :func:`evaluate_verdict`), so an
    application whose own files are under-audited still returns
    ``INSUFFICIENT_COVERAGE``. A scope narrows WHAT is claimed; it can never lower the
    bar for claiming it.

    PURE + frozen ``extra="forbid"`` (the 1.1/1.2/1.6 precedent). ``assessed_deep_ratio``
    is an exact ``Fraction`` (NEVER ``float``, AR4).
    """

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    scope_id: str = Field(
        ..., description="Closed identifier of the narrowing that was applied (e.g. 'application')."
    )
    excluded_reason: str = Field(
        ..., description="Why the held-out entries were held out (e.g. 'test_files')."
    )
    assessed_deep_count: int = Field(
        ..., ge=0, description="audited_deep entries WITHIN the assessed scope (the gate numerator)."
    )
    assessed_total_count: int = Field(
        ..., ge=0, description="Total entries WITHIN the assessed scope (the gate denominator)."
    )
    assessed_deep_ratio: Fraction = Field(
        ..., description="assessed_deep / assessed_total as an exact Fraction (NEVER float, AR4)."
    )
    excluded_count: int = Field(
        ..., ge=0, description="Entries held out of the assessment (disclosed, never silently dropped)."
    )

    def to_canonical_payload(self) -> dict[str, object]:
        """Canonical-serializable payload with the live ``Fraction`` re-installed (AR4).

        Mirrors :meth:`AuditVerdict.to_canonical_payload` — Pydantic coerces a
        ``Fraction`` via ``str`` (``Fraction(1, 1) → "1"``), which diverges from the
        LOCKED canonical ``"num/den"`` encoding.
        """
        payload = self.model_dump()
        payload["assessed_deep_ratio"] = self.assessed_deep_ratio
        return payload


class AuditVerdict(BaseModel):
    """Frozen pure verdict result the Story-1.7 pipeline consumes (FR15/FR18/M2).

    ``frozen=True, extra="forbid"`` (the 1.1 ``Envelope`` / 1.2 ``Recording``
    precedent): an unknown field on read-back is a typed ``ValidationError``.
    Reserves every field a downstream machine consumer reads at birth (NFR-M2
    additive-only). The ``deep_ratio`` is an exact ``Fraction`` (NEVER ``float``)
    so it serializes byte-identically through the 1.1 canonical encoding
    (``Fraction`` → ``"num/den"``). NO volatile ``run_id``/``created_at`` — those
    belong to the Story-1.7 envelope around this payload (NFR-D3).
    """

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    schema_version: str = Field(
        default=VERDICT_SCHEMA_VERSION, description="Verdict schema version (part of the hash)."
    )
    verdict: Verdict = Field(..., description="The closed-enum release-readiness verdict.")
    deep_ratio: Fraction = Field(
        ..., description="audited_deep / total as an exact Fraction (NEVER float, AR4)."
    )
    deep_count: int = Field(..., ge=0, description="Number of audited_deep entries (the numerator).")
    total_count: int = Field(..., ge=0, description="Total ledger entries (the denominator).")
    counts_by_depth: dict[CoverageDepth, int] = Field(
        ..., description="Per-depth entry counts (reuse of CoverageLedger.counts_by_depth())."
    )
    blocking_finding_count: int = Field(
        ..., ge=0, description="Number of verdict-eligible (depth_supported is not None) findings."
    )
    ordered_findings: tuple[Recording, ...] = Field(
        default=(), description="Findings ordered blocking-first, fully tie-broken (FR33)."
    )
    critical_subsystems_all_deep: bool = Field(
        default=True,
        description="FR16 critical-subsystem clause input (Story 2.3 seam; True in V1).",
    )
    coverage_scope: CoverageScope | None = Field(
        default=None,
        description=(
            "Disclosed assessment-scope narrowing, or None for a whole-repository "
            "assessment (the default). Present ⇔ the gate keyed on a narrowed population."
        ),
    )
    critical_subsystems_not_deep: tuple[str, ...] = Field(
        default=(),
        description=(
            "Sorted critical paths that are not audited_deep — the EVIDENCE behind a "
            "False critical_subsystems_all_deep. Empty when the clause is satisfied."
        ),
    )
    exit_code: int = Field(..., description="Mapped process exit code (AR3 wire contract).")

    def to_canonical_payload(self) -> dict[str, object]:
        """Return a canonical-serializable payload dict for the 1.1 serializer.

        Pydantic v2's ``model_dump()`` coerces a ``Fraction`` via ``str`` (so
        ``Fraction(1, 1) → "1"``), which DIVERGES from the LOCKED canonical
        ``Fraction → "num/den"`` encoding (``"1/1"``). This method dumps the model
        and then re-installs the live ``Fraction`` object for ``deep_ratio`` so the
        single 1.1 ``canonical.dumps`` applies its frozen exact encoding (AR4 /
        NFR-P1) — keeping ONE serializer and one ratio form across hosts. Every
        other leaf (enum values, ints, the ``Recording`` finding rows) already
        ``model_dump()``s to canonical-safe JSON primitives.

        ``coverage_scope`` is OMITTED from the payload entirely when no narrowing was
        applied, rather than serialized as ``null``. This keeps an unscoped run
        BYTE-IDENTICAL to a pre-scope run (the Story-6.3/6.4 additive precedent: only
        an actually-engaged feature may change a byte), so the whole-repository
        default needs no ``schema_version`` bump and every persisted V1 verdict still
        round-trips. A scoped run carries the nested disclosure with its live
        ``Fraction`` re-installed by the same AR4 rule.
        """
        payload = self.model_dump()
        payload["deep_ratio"] = self.deep_ratio
        if self.coverage_scope is None:
            payload.pop("coverage_scope", None)
        else:
            payload["coverage_scope"] = self.coverage_scope.to_canonical_payload()
        # Same omit-when-unengaged rule: a satisfied critical clause adds no key, so a
        # repo with no non-deep criticals stays byte-identical to a pre-seam run.
        if not self.critical_subsystems_not_deep:
            payload.pop("critical_subsystems_not_deep", None)
        return payload


def is_verdict_blocking(finding: Recording) -> bool:
    """Return whether ``finding`` is verdict-blocking — the advisory-by-contract moat.

    A finding is verdict-blocking ⇔ verdict-eligible ⇔ ``depth_supported is not
    None`` (cross-cutting #6). NOT keyed on ``advisory`` — both 1.5 finding kinds
    carry ``advisory=True``; only ``depth_supported`` (an AST-corroborated supported
    depth) distinguishes a verdict-eligible AST-corroborated finding from an
    advisory heuristic-only one. A heuristic-only finding can never block.
    """
    return finding.depth_supported is not None


def blocking_finding_count(findings: tuple[Recording, ...] | list[Recording]) -> int:
    """Count verdict-eligible (blocking) findings — PURE (the AC4 moat)."""
    return sum(1 for finding in findings if is_verdict_blocking(finding))


def _finding_sort_key(finding: Recording) -> tuple[bool, int, str, str]:
    """Total deterministic sort key: blocking-first, fully tie-broken (FR33/AR4).

    ``(not eligible, depth_rank, rule_id, recording_id)`` — primary blocking-first
    (eligible before advisory-only), secondary supported-depth rank (deepest
    first), then ``rule_id``, final ``recording_id`` lexicographic so the order is
    fully determined with NO reliance on input/iteration order. An ineligible
    finding (``depth_supported is None``) gets the max depth rank so it can never
    sort ahead of an eligible one even within its (non-blocking) partition.
    """
    eligible = is_verdict_blocking(finding)
    depth = finding.depth_supported
    depth_rank = _DEPTH_ORDER_RANK[depth] if depth is not None else len(_DEPTH_ORDER_RANK)
    return (not eligible, depth_rank, finding.rule_id, finding.recording_id)


def order_findings(
    findings: tuple[Recording, ...] | list[Recording],
) -> tuple[Recording, ...]:
    """Order findings blocking-first with a total deterministic tie-break (FR33).

    PURE — no input/iteration-order reliance (AR4). Two calls over the same finding
    set in different input orders produce the identical tuple.
    """
    return tuple(sorted(findings, key=_finding_sort_key))


def exit_code_for_verdict(verdict: Verdict) -> int:
    """Map a verdict to its locked process exit code (AR3 ``0``/``2``/``3``).

    Exhaustive over the :class:`Verdict` enum — RAISES ``ValueError`` on an
    unmapped member rather than returning a silent default, so adding a verdict
    member without an exit code is a build-time failure. ``crash → 1`` is the
    reserved code the Story-1.7 pipeline produces on an uncaught error (AR10); the
    gate is a total pure function and never raises to produce it.
    """
    try:
        return _EXIT_CODE_BY_VERDICT[verdict]
    except KeyError as exc:  # pragma: no cover - guarded by the exhaustiveness test
        raise ValueError(
            f"no exit code mapped for verdict {verdict!r}; the AR3 exit-code map "
            f"must be exhaustive over the Verdict enum"
        ) from exc


def evaluate_verdict(
    ledger: CoverageLedger,
    findings: tuple[Recording, ...] | list[Recording] = (),
    *,
    critical_subsystems_all_deep: bool = True,
    critical_subsystems_not_deep: tuple[str, ...] | list[str] = (),
    scope_paths: frozenset[str] | tuple[str, ...] | None = None,
    scope_id: str = "application",
    scope_excluded_reason: str = "test_files",
) -> AuditVerdict:
    """Fold a coverage ledger + findings into an :class:`AuditVerdict` (PURE).

    The terminal pure fold (FR15 / AR8): imports only the 1.2 ledger/finding
    models, performs no I/O, reads no clock, calls no ``dispatch()``, uses zero LLM
    tokens (NFR-D2). The decision table (evaluated IN ORDER, floor first):

    1. ``total == 0`` OR ``deep_ratio < 20%`` → ``INSUFFICIENT_COVERAGE`` (the
       floor; wins over blocking findings — guards the deep-% denominator so a
       divide-by-zero is structurally impossible, AC8).
    2. ``deep_ratio >= 60%`` AND ``blocking == 0`` AND
       ``critical_subsystems_all_deep`` → ``RELEASE_READY``.
    3. otherwise → ``NOT_READY_FOR_RELEASE`` (≥20% with a gate unmet).

    Never a default block (FR16): the only blocking verdict requires either
    insufficient deep coverage (≥20% but <60%), ≥1 verdict-eligible finding, or a
    critical subsystem below deep (the Story-2.3 seam). A clean ledger with adequate
    coverage and no blocking findings returns ``RELEASE_READY``; a below-floor
    ledger returns ``INSUFFICIENT_COVERAGE``. The same fold runs over a partial
    ledger with no special mode (the Epic-3 Story-3.3 reuse seam, AC8).

    ``critical_subsystems_all_deep`` defaults to satisfied in V1; Story 2.3 supplies
    the real value additively (the FR16 critical-subsystem clause).

    Assessment scope (``scope_paths``) — DISCLOSED narrowing, never a bypass
    ---------------------------------------------------------------------
    ``scope_paths=None`` (the default) assesses the WHOLE ledger and is exactly the
    V1 fold, byte-identical in and out. Passing an explicit set of repo-relative
    paths narrows the ASSESSED POPULATION to the ledger entries in that set; the
    decision table above is then evaluated over the narrowed deep-% instead of the
    whole-ledger deep-%.

    This exists because a test file is graded ``audited_shallow`` BY CONSTRUCTION (it
    is the subject of the vacuous-test pass, not a target of deep grounding). In a
    repository with more test files than application files those shallow-by-design
    entries dominate the denominator and manufacture a FALSE NEGATIVE — a
    ``NOT_READY_FOR_RELEASE`` carrying zero blocking findings, earned solely by being
    well-tested. Narrowing to the application files reports what was actually assessed.

    Three invariants make the narrowing honest rather than a loophole:

    1. **The floor is re-applied WITHIN the scope, never skipped.** An application
       whose own files are below :data:`INSUFFICIENT_COVERAGE_FLOOR` still returns
       ``INSUFFICIENT_COVERAGE``. Narrowing changes WHAT is claimed, never the bar for
       claiming it. (The rejected alternative — treating "the core looks fine" as a
       reason to skip the floor — lets ArgusAgent assert release-readiness over a
       population it never adequately examined, which is the exact false assurance
       the floor exists to prevent.)
    2. **Every gate keeps its full force.** Blocking findings and the FR16
       critical-subsystem clause are unchanged and unscoped: a blocking finding in a
       held-out file still blocks, because ``findings`` are not filtered here.
    3. **The narrowing is recorded on the verdict.** A :class:`CoverageScope` is
       attached, so a scoped ``RELEASE_READY`` cannot be read without also reading
       what was assessed and what was held out. ``deep_ratio`` / ``deep_count`` /
       ``total_count`` retain their LOCKED whole-ledger meaning, so both the honest
       repository-wide number and the assessed number are always available.

    The gate stays PURE: it does not classify files. The caller (the impure pipeline
    shell, which already owns the multi-language ``is_test_file``) decides membership
    and passes it in as data — keeping the AR8 import isolation intact.
    """
    total = ledger.total()
    deep = ledger.deep_count()
    deep_ratio = Fraction(deep, total) if total > 0 else Fraction(0, 1)
    blocking = blocking_finding_count(findings)

    # The assessed population: the whole ledger by default, else the disclosed subset.
    # Derived by filtering ledger.entries (already file_path-sorted, AR4) rather than
    # by iterating the caller's collection, so the fold never depends on the caller's
    # iteration order.
    coverage_scope: CoverageScope | None = None
    if scope_paths is None:
        assessed_total = total
        assessed_deep = deep
        assessed_ratio = deep_ratio
    else:
        in_scope = frozenset(scope_paths)
        scoped = [entry for entry in ledger.entries if entry.file_path in in_scope]
        assessed_total = len(scoped)
        assessed_deep = sum(1 for e in scoped if e.depth is CoverageDepth.AUDITED_DEEP)
        assessed_ratio = (
            Fraction(assessed_deep, assessed_total) if assessed_total > 0 else Fraction(0, 1)
        )
        coverage_scope = CoverageScope(
            scope_id=scope_id,
            excluded_reason=scope_excluded_reason,
            assessed_deep_count=assessed_deep,
            assessed_total_count=assessed_total,
            assessed_deep_ratio=assessed_ratio,
            excluded_count=total - assessed_total,
        )

    # Decision table, floor first — evaluated over the ASSESSED population. An empty
    # assessed population is `total == 0`-equivalent: nothing was examined, so nothing
    # can be claimed (guards the divide-by-zero structurally, AC8).
    if assessed_total == 0 or assessed_ratio < INSUFFICIENT_COVERAGE_FLOOR:
        verdict = Verdict.INSUFFICIENT_COVERAGE
    elif (
        assessed_ratio >= RELEASE_READY_DEEP_THRESHOLD
        and blocking == 0
        and critical_subsystems_all_deep
    ):
        verdict = Verdict.RELEASE_READY
    else:
        verdict = Verdict.NOT_READY_FOR_RELEASE

    return AuditVerdict(
        verdict=verdict,
        deep_ratio=deep_ratio,
        deep_count=deep,
        total_count=total,
        counts_by_depth=ledger.counts_by_depth(),
        blocking_finding_count=blocking,
        ordered_findings=order_findings(findings),
        critical_subsystems_all_deep=critical_subsystems_all_deep,
        # Recorded only when the clause is UNSATISFIED — the paths are the evidence
        # behind the False, and carrying them on a satisfied clause would be noise.
        critical_subsystems_not_deep=(
            tuple(critical_subsystems_not_deep) if not critical_subsystems_all_deep else ()
        ),
        coverage_scope=coverage_scope,
        exit_code=exit_code_for_verdict(verdict),
    )
