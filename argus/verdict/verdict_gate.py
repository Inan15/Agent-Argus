"""PURE release-readiness verdict gate — fold + finding ordering + exit code.

Drivers: ArgusAgent-FR-15 (release-readiness verdict as a PURE function of the coverage
ledger), ArgusAgent-FR-16 as amended 2026-08-03 (the binding FOUR-row decision table:
findings are evaluated BEFORE the coverage gates, so a blocking verdict is emitted only
on the strength of a finding Argus actually made; ``INSUFFICIENT_COVERAGE`` below the
20% floor AND for a zero-findings unmet gate; never a default block), ArgusAgent-DR-3
(the fired decision row is DISCLOSED on the artifact), ArgusAgent-DR-4 (the
``schema_version`` bump that pays for it), ArgusAgent-FR-8-honored (``inferred`` evidence can never satisfy
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
- **Gate thresholds (the binding FR16 decision table, evaluated IN ORDER)** — with
  ``assessed_ratio`` the deep-% over the assessed population and
  ``blocking = (# findings where depth_supported is not None)``:

  | # | condition (evaluated in order)                                   | verdict                | exit |
  |---|------------------------------------------------------------------|------------------------|------|
  | 1 | ``assessed_total == 0`` OR ``assessed_ratio < Fraction(1, 5)``   | INSUFFICIENT_COVERAGE  | 3    |
  | 2 | ``blocking >= 1``                                                | NOT_READY_FOR_RELEASE  | 2    |
  | 3 | ``assessed_ratio >= Fraction(3, 5)`` AND all criticals deep       | RELEASE_READY          | 0    |
  | 4 | otherwise — zero findings, a coverage/critical gate unmet         | INSUFFICIENT_COVERAGE  | 3    |

  Boundary semantics LOCKED: ``RELEASE_READY`` at deep-% ``>= 60%`` (inclusive);
  the floor is deep-% ``< 20%`` (strict — exactly-20% is assessable/blocking-eligible).
- **FINDINGS ARE EVALUATED BEFORE THE COVERAGE GATES (FR16 amended 2026-08-03)** — the
  pre-amendment table had a THREE-row shape whose ``else`` was a DEFAULT BLOCK: any run
  above the floor that missed the 60% gate or the critical-subsystem clause returned
  ``NOT_READY_FOR_RELEASE`` — a verdict whose canonical meaning is "**Argus found
  something**" — while carrying ZERO blocking findings. That is a false accusation
  emitted by the tool whose product thesis is that it does not cry wolf, and it is the
  last asymmetry in cross-cutting #6 (the advisory-by-contract / false-accusation moat),
  which was enforced on FINDINGS but not on the VERDICT itself. Row 4 replaces it: a
  coverage shortfall is reported as the honest NOT-ASSESSED state, never as a defect.
  ``INSUFFICIENT_COVERAGE`` is therefore reached TWO ways — below the floor (row 1) or a
  zero-findings unmet gate (row 4) — which is precisely why the fired row is DISCLOSED.
- **Floor-vs-blocking precedence = FLOOR WINS** — a below-20% ledger returns
  ``INSUFFICIENT_COVERAGE`` EVEN WITH blocking findings. Rationale: below the floor
  ArgusAgent has not assessed enough to honestly claim it saw enough to BLOCK either; low
  coverage is ArgusAgent's limitation to report, not a verdict to render. The floor row
  is evaluated FIRST — row 1 keeps precedence over row 2, so "findings before coverage"
  means before the 60% / critical-subsystem GATES (row 3), NEVER before the FLOOR.
  Pinned by a test.
- **Decision-row disclosure vocabulary** — :class:`DecisionRow`, a ``str``-valued closed
  enum with EXACTLY four members, one per FR16 row. It is a SEPARATE disclosure
  vocabulary: the addendum's "the verdict enum MUST NOT grow" constrains
  :class:`Verdict` (still exactly three members — adding ``COVERAGE_GATE_UNMET`` was
  considered and REJECTED), not the introduction of a field that records WHICH row
  fired. Rows 1 and 4 are indistinguishable by verdict and exit code, so without the
  row every downstream consumer would have to re-derive the gate's reasoning from the
  counters — a forked second decision table, the exact failure mode §3.3 forbids.
  Consumers that need to know "was this the floor?" read
  :attr:`AuditVerdict.is_below_floor`.
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
  swamp the denominator and withhold ``RELEASE_READY`` from a repository carrying ZERO
  blocking findings (a row-4 ``INSUFFICIENT_COVERAGE``; before the FR16 amendment this
  was the far worse ``NOT_READY_FOR_RELEASE``). LOCKED invariants: the floor and the
  RELEASE_READY threshold are
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
    "DecisionRow",
    "BLOCKED",
    "CoverageScope",
    "DeepPassOutcome",
    "AuditVerdict",
    "is_verdict_blocking",
    "blocking_finding_count",
    "order_findings",
    "exit_code_for_verdict",
    "evaluate_verdict",
]

# Single localized source for this contract's schema version (additive-only;
# part of the hashed payload — a bump deliberately changes the content hash).
# "1" → "2" (Story 8.1 / DR-4): the FR16 reorder + the additive ``decision_row``
# disclosure. NFR-M2 sanctions the bump as the lever for an INTENTIONAL content-hash
# change; there is deliberately NO migration code and NO rewrite pass — verdicts already
# persisted under ``.apaa/`` / ``.argus/`` keep their "1" stamp and still round-trip,
# because every field added since has carried a default.
VERDICT_SCHEMA_VERSION = "2"

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


class DecisionRow(str, enum.Enum):
    """Closed, fixed-enum disclosure of WHICH FR16 row produced the verdict (DR-3).

    A ``str``-valued closed enum with EXACTLY four members — one per row of the binding
    FR16 decision table — mirroring the :class:`Verdict` / ``CoverageDepth`` pattern; the
    membership set is pinned by a committed test. The string VALUES carry the row number
    so "which row fired" is LITERAL on the artifact rather than inferred.

    This does NOT grow :class:`Verdict`, which still has exactly three members. One
    verdict value carries one meaning; the row records the REASONING that produced it.
    The distinction matters because rows 1 and 4 both render ``INSUFFICIENT_COVERAGE`` /
    exit ``3`` and are otherwise indistinguishable:

    - ``BELOW_FLOOR`` — too little was assessed to claim anything at all.
    - ``GATE_UNMET_NO_FINDINGS`` — plenty was assessed and NOTHING was found; a coverage
      or critical-subsystem gate simply was not met.

    A consumer that reports the second as the first (or as a block) states a falsehood.
    """

    BELOW_FLOOR = "row_1_below_floor"
    BLOCKING_FINDINGS = "row_2_blocking_findings"
    GATES_MET = "row_3_gates_met"
    GATE_UNMET_NO_FINDINGS = "row_4_gate_unmet_no_findings"


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
    denominator produces a FALSE NEGATIVE: ``RELEASE_READY`` withheld (row 4,
    ``INSUFFICIENT_COVERAGE``) with zero blocking findings, purely because the repo is
    well-tested.

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


class DeepPassOutcome(BaseModel):
    """What the OPT-IN LLM-backed deep pass actually did — the FR36 honesty record.

    ``frozen=True, extra="forbid"``, no ``float`` (AR4/AR8). Story 12.2.

    Why this exists at all
    ----------------------
    Before Story 12.2 the depth disclosure was derived from ``enabled_passes`` — i.e.
    from what was REQUESTED. The sentence it printed was a statement about what was
    DELIVERED. Those differ, and the gap was an operator-visible false claim: the token
    ``deep`` in a ``--passes`` CSV made the tool report that a deep read had been
    dispatched and AST-validated on a tree where the seam had ZERO production callers
    (FR36's *"it never produces a false deep claim"*, violated by the shipped tool).

    This record is the OUTCOME the disclosure is now derived from. It carries counts, a
    typed reason set and the spend — never prompt/response bytes, a provider endpoint or
    a key (NFR-S1: there is no field that could hold them).

    ``credits_used`` is a frozen exact-numeric STRING and never a ``float`` (AR4): the
    single canonical serializer raises on a float leaf, and this is the one new path in
    the product that carries a cost number.

    THE OMIT-WHEN-UNENGAGED RULE (the byte-identity keystone — AC2.4)
    ----------------------------------------------------------------
    ``AuditVerdict.deep_pass`` is ``None`` unless the pass was actually requested, and
    :meth:`AuditVerdict.to_canonical_payload` then omits the key ENTIRELY rather than
    serializing ``null``. This is the Story-6.3/6.4 additive precedent ``coverage_scope``
    and ``critical_subsystems_not_deep`` already follow — *only an actually-engaged
    feature may change a byte* — so a default run's ``.argus/`` tree is BYTE-IDENTICAL to
    a pre-12.2 run and needs no ``schema_version`` bump.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    requested_count: int = Field(
        ..., ge=0, description="Files the deep pass targeted (the denominator of the attempt)."
    )
    delivered_count: int = Field(
        ...,
        ge=0,
        description=(
            "Targets for which a recording came back AND its claim was AST-grounded. "
            "The ONLY input that may license the strengthened depth disclosure."
        ),
    )
    degraded_count: int = Field(
        ..., ge=0, description="Targets that failed, were skipped on exhaustion, or came back ungrounded."
    )
    reasons: tuple[str, ...] = Field(
        default=(),
        description=(
            "SORTED distinct typed degradation reason codes (structured identifiers only "
            "— never prompt/response/secret bytes or an endpoint, NFR-S1)."
        ),
    )
    halted_on_exhaustion: bool = Field(
        default=False,
        description="The FR22 ceiling halted the pass mid-run (the remainder is `skipped`).",
    )
    credits_used: str = Field(
        default="0",
        min_length=1,
        description="Deep-pass spend as a frozen exact-numeric string (AR4 — NEVER float).",
    )

    @property
    def delivered(self) -> bool:
        """Whether the pass delivered at least one AST-grounded deep read.

        A property, not a field: it is derived, so it adds no key to the canonical
        payload and cannot become a second source of truth on disk (the
        ``is_below_floor`` precedent).
        """
        return self.delivered_count > 0


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
    decision_row: DecisionRow | None = Field(
        default=None,
        description=(
            "Which row of the binding FR16 decision table produced this verdict (DR-3). "
            "None ONLY for a pre-amendment (schema_version '1') payload read back from "
            "disk, where the row was never disclosed; evaluate_verdict always sets it."
        ),
    )
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
    deep_pass: DeepPassOutcome | None = Field(
        default=None,
        description=(
            "What the opt-in LLM-backed deep pass DID (FR36), or None when it was never "
            "requested — which is every default run. Present ⇔ the operator opted in."
        ),
    )
    exit_code: int = Field(..., description="Mapped process exit code (AR3 wire contract).")

    @property
    def is_below_floor(self) -> bool:
        """Whether the FLOOR (row 1) — not a gate — withheld the verdict.

        THE single source of truth for every consumer that has to distinguish "too
        little was assessed to claim anything" (row 1) from "nothing was found and a
        gate was not met" (row 4). Both render ``INSUFFICIENT_COVERAGE`` / exit ``3``,
        so keying on the verdict enum states a falsehood for row 4 — which is exactly
        what ``exhaustion.build_floor_report`` and the negative-assurance statement did
        before Story 8.1.

        Re-deriving this from the counters in each consumer would fork the decision
        table (§3.3). It reads the DISCLOSED row instead. A pre-amendment payload
        (``decision_row is None``, ``schema_version "1"``) falls back to the enum, which
        for a ``"1"``-stamped verdict is exactly the old — and then still correct —
        equivalence, so read-back of persisted state is unchanged.

        A property, not a field: it is derived, so it adds no key to the canonical
        payload and cannot become a second source of truth on disk.
        """
        if self.decision_row is not None:
            return self.decision_row is DecisionRow.BELOW_FLOOR
        return self.verdict is Verdict.INSUFFICIENT_COVERAGE

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
        # …and again for the row: every LIVE verdict discloses one, so this only ever
        # fires for a pre-amendment payload read back from disk, which then re-serializes
        # BYTE-IDENTICALLY to how it was written (NFR-D3: a "1"-stamped verdict keeps its
        # hash). A `"decision_row":null` key is never emitted.
        if self.decision_row is None:
            payload.pop("decision_row", None)
        # Story 12.2 / AC2.4 — the SAME omit-when-unengaged rule, for the same reason:
        # the opt-in deep pass is absent from every default run, so a default run's
        # persisted bytes are identical to a pre-12.2 run's and no schema bump is owed.
        if self.deep_pass is None:
            payload.pop("deep_pass", None)
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
    deep_pass: DeepPassOutcome | None = None,
) -> AuditVerdict:
    """Fold a coverage ledger + findings into an :class:`AuditVerdict` (PURE).

    The terminal pure fold (FR15 / AR8): imports only the 1.2 ledger/finding
    models, performs no I/O, reads no clock, calls no ``dispatch()``, uses zero LLM
    tokens (NFR-D2). The binding FR16 decision table (evaluated IN ORDER, floor first),
    each row also DISCLOSED on the result as :attr:`AuditVerdict.decision_row`:

    1. ``assessed_total == 0`` OR ``assessed_ratio < 20%`` → ``INSUFFICIENT_COVERAGE``
       (``DecisionRow.BELOW_FLOOR``; the floor, which WINS over blocking findings — and
       guards the deep-% denominator so a divide-by-zero is structurally impossible).
    2. ``blocking >= 1`` → ``NOT_READY_FOR_RELEASE`` (``DecisionRow.BLOCKING_FINDINGS``).
    3. ``assessed_ratio >= 60%`` AND ``critical_subsystems_all_deep`` →
       ``RELEASE_READY`` (``DecisionRow.GATES_MET``).
    4. otherwise → ``INSUFFICIENT_COVERAGE``
       (``DecisionRow.GATE_UNMET_NO_FINDINGS``): zero blocking findings with a coverage
       or critical-subsystem gate unmet.

    **Findings are evaluated BEFORE the coverage GATES, never before the FLOOR.** Row 1
    keeps precedence over row 2 (the LOCKED floor-vs-blocking precedence): below the
    floor ArgusAgent has not assessed enough to honestly claim it saw enough to BLOCK
    either. Row 3 deliberately carries NO ``blocking == 0`` clause — that is GUARANTEED
    by row-2 precedence, and restating it would be a second, silently divergable copy of
    the same condition.

    Never a default block (FR16 as amended): the ONLY blocking verdict is row 2, which
    requires ≥1 verdict-eligible finding. A coverage shortfall or an unmet
    critical-subsystem clause with nothing found is reported as the honest NOT-ASSESSED
    state, not as a defect the tool never detected. A clean ledger with adequate
    coverage and no blocking findings returns ``RELEASE_READY``. The same fold runs over
    a partial ledger with no special mode (the Epic-3 Story-3.3 reuse seam).

    Disclosure (DR-3): the result carries the fired row PLUS the assessed population it
    was computed over — ``coverage_scope`` when the assessment was narrowed, otherwise
    ``deep_count`` / ``total_count``. Together with ``blocking_finding_count`` and
    ``critical_subsystems_all_deep`` that is sufficient to RE-DERIVE the verdict and the
    exit code without re-reading the ledger (pinned by a test), so no consumer ever needs
    a second copy of this table.

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
    entries dominate the denominator and manufacture a FALSE NEGATIVE — ``RELEASE_READY``
    withheld (row 4) from a repository carrying zero blocking findings, earned solely by
    being well-tested. Narrowing to the application files reports what was actually
    assessed.

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

    # ── The binding FR16 decision table, VERBATIM and IN ORDER, over the ASSESSED
    # population. Each branch sets both the verdict and the row it fired.
    if assessed_total == 0 or assessed_ratio < INSUFFICIENT_COVERAGE_FLOOR:
        # Row 1 — the FLOOR, first and above the findings row (LOCKED precedence). An
        # empty assessed population is `total == 0`-equivalent: nothing was examined, so
        # nothing can be claimed (guards the divide-by-zero structurally).
        verdict = Verdict.INSUFFICIENT_COVERAGE
        row = DecisionRow.BELOW_FLOOR
    elif blocking >= 1:
        # Row 2 — findings BEFORE the coverage gates. The only blocking verdict, and it
        # is earned by a finding Argus actually made.
        verdict = Verdict.NOT_READY_FOR_RELEASE
        row = DecisionRow.BLOCKING_FINDINGS
    elif assessed_ratio >= RELEASE_READY_DEEP_THRESHOLD and critical_subsystems_all_deep:
        # Row 3 — the gates. NO `blocking == 0` clause: row-2 precedence already
        # guarantees it here, and a redundant copy of that condition could silently
        # diverge from the one that is actually load-bearing.
        verdict = Verdict.RELEASE_READY
        row = DecisionRow.GATES_MET
    else:
        # Row 4 — zero blocking findings, a coverage or critical-subsystem gate unmet.
        # The honest NOT-ASSESSED state. This row replaces the pre-amendment default
        # block, which reported a coverage shortfall as a defect.
        verdict = Verdict.INSUFFICIENT_COVERAGE
        row = DecisionRow.GATE_UNMET_NO_FINDINGS

    return AuditVerdict(
        verdict=verdict,
        decision_row=row,
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
        # Story 12.2 / FR36 — carried, never DECIDED ON. The deep pass's effect on the
        # verdict is already fully expressed in its INPUTS (a degraded target is graded
        # by the existing `grade_entry` downgrade, so it moves the ratio the table
        # already reads). No FR16 row, threshold, boundary or exit-code mapping moves.
        deep_pass=deep_pass,
        exit_code=exit_code_for_verdict(verdict),
    )
