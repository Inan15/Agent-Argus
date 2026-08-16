"""Story 13.2 — the ADJUDICATION RECORD: who judged which finding, when, and why.

Verification area ``ArgusAgent-PRECISION`` (``TC-ArgusAgent-PRECISION-001-32``..).
Drivers: ArgusAgent-FR-13 (every recorded finding carries >=1 verifiable LOCATOR — the
thing protocol §4's borderline ladder re-examines), ArgusAgent-FR-20, the PRD's
>=80%-precision externalization gate, ArgusAgent-NFR-S1 (rule-id provenance, locators and
counts ONLY — no source byte, no secret value, no absolute host path),
ArgusAgent-AR4 (precision is an exact ``Fraction`` rendered ``"num/den"`` — never a float),
ArgusAgent-AR7 (reuse, never fork), ArgusAgent-AR8 (PURE core — no clock, no LLM, no
random; this module's only I/O is :func:`load_record`, which a caller passes an explicit
``Path``), ArgusAgent-NFR-M1 (<=1200 lines).

WHAT THIS MODULE IS — and the one thing it must never become
------------------------------------------------------------
It is the **instrument**, not the **judgement**. It defines the shape of an adjudication,
enforces that a disposition can only enter the record attributed to a human role the
protocol §2 table registers, proves the record is exhaustive over the emitted finding set,
and folds the resulting TP/FP counts into the precision arithmetic.

**No function here decides whether a finding is a true positive.** A disposition enters the
record only from the named human (protocol §2 Engineering Lead; ``sprint-status.yaml``
names **XAgent007**). ``UNADJUDICATED`` is the ONLY vocabulary member an automated
producer may write, and :class:`AdjudicationRow` RAISES if such a row carries an
adjudicator id — so "an agent filled in the human's name" is a construction-time failure
rather than a review-time observation. *An autonomous story that tags its own findings TP
has measured nothing and has produced the exact artifact Epic 13 exists to make
impossible.*

THE UNIT OF ADJUDICATION IS THE **FINDING** (protocol §7 / V1.3, Story 13.2 / AC2)
---------------------------------------------------------------------------------
Protocol §7 locks *"precision is measured over FINDINGS, not repos"* and §7 says in its own
heading not to soften it. The 6.6 fold takes ``dict[str, frozenset[MatchKey]]`` and does
``tp = len(tp_keys)`` — a count of distinct ``(rule_id, verdict_eligible, advisory)``
CLASSES, which is a different quantity: on the 13.1 corpus **31** blocking findings across
two members collapse to **one** class, and a class with 24 findings would weigh exactly as
much as a class with 1.

So this record keys each row on a **finding identity** —
``(member_id, rule_id, verdict_eligible, advisory, locator)`` — which is the SHARED 6.6
:data:`~argus.precision.replay_harness.MatchKey` plus the two coordinates that distinguish
two findings of the same class (DN-MATCH-KEY-REUSE is honoured: the match key is reused
unchanged and is still derivable from any row via :attr:`AdjudicationRow.match_key`; no
second, divergent identity is introduced).

WHY THE FOLD IS NOT ROUTED THROUGH ``compute_precision`` (DN-2b — read the alternative)
--------------------------------------------------------------------------------------
The obvious reuse is to synthesise a golden key from the TP dispositions and let
``compute_precision`` diff against it through its existing ``registry=`` injection seam.
**It produces a wrong number, and it does so silently.** That fold classifies by golden-key
MEMBERSHIP: a class present in the golden key contributes its whole multiplicity as TP. On
a real repository one rule class routinely holds both real and false findings — 20 genuine
``vacuous_test_ast`` hits and 4 false ones share one match key — and a membership diff
cannot express "this class is 20 TP and 4 FP". Adding a multiplicity map to
``compute_precision`` was the rejected alternative: it would have carried the multiset
correctly and still assigned every one of the 24 to whichever side the class landed on.

What must not fork is the **arithmetic**, and it does not: precision comes from
:func:`~argus.precision.replay_harness.precision_fraction`, the gate predicate from
:func:`~argus.precision.replay_harness.gate_is_provisional`, the threshold from
:data:`~argus.precision.replay_harness.PRECISION_GATE_THRESHOLD`, and the status sentence
from :func:`~argus.precision.replay_harness.precision_gate_status_for` — all of them the
same objects ``compute_precision`` uses. One arithmetic, two populations.

THE THREE OUTCOMES (DN-5, the ``scripts/release_preflight.py`` precedent)
------------------------------------------------------------------------
A run is ADJUDICATED, or it is :class:`AdjudicationUnevaluable`, or it raises. There is no
fourth state in which a partially-adjudicated corpus quietly reports a precision figure
over the subset that happened to be judged. *A green run that silently skipped the
adjudication is worse than a red one.*
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Any

from argus.precision.replay_harness import (
    PRECISION_GATE_THRESHOLD,
    MatchKey,
    corpus_manifest_module,
    gate_is_provisional,
    precision_fraction,
    precision_gate_status_for,
)
from argus.store.canonical import dumps, dumps_bytes, loads

__all__ = [
    "ADJUDICATION_UNIT",
    "DISPOSITIONS",
    "DENOMINATOR_DISPOSITIONS",
    "EXPERT_HOURS_CEILING",
    "HUMAN_DISPOSITIONS",
    "PROTOCOL_ADJUDICATOR_ROLES",
    "PROTOCOL_PATH",
    "RECORD_PATH",
    "ROW_FIELDS",
    "AdjudicatedPrecision",
    "AdjudicationRecord",
    "AdjudicationRow",
    "AdjudicationUnevaluable",
    "Exhaustive",
    "UnregisteredAdjudicator",
    "UnregisteredDisposition",
    "adjudicator_role",
    "change_log_head_version",
    "disposition_meaning",
    "expert_hours_report",
    "finding_row_id",
    "fold_adjudicated_precision",
    "load_record",
    "validation_set_population_n",
]

#: Repository-relative paths, forward-slash, resolved by the CALLER against its own root.
#: Not `Path` objects and not absolute: this module is imported from a built distribution
#: where neither file exists (``DF-9-2-A``), and a module-level path resolution is the
#: shape ``tests/test_built_distribution.py`` exists to catch.
PROTOCOL_PATH = "_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md"
RECORD_PATH = (
    "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-record.json"
)

#: The unit precision is measured over (protocol §7, re-affirmed by V1.3 / AC2).
ADJUDICATION_UNIT = "finding"

#: §3's ceiling on a full gate-flip adjudication run, as an exact ``Fraction`` (no float).
#: RECORDED against, never enforced: §3 says the budget is *"a ceiling, not a target"* and
#: that an overrun *"is a signal the cartridge is ambiguous"*. Trimming an adjudication to
#: fit an estimate is the failure this constant must never cause.
#: ``TC-ArgusAgent-PRECISION-001-45`` cross-checks it against protocol §3's own text, so
#: this is a single source under assertion rather than a prose copy that rots (AI-E9-7).
EXPERT_HOURS_CEILING = Fraction(4, 1)


class UnregisteredDisposition(ValueError):
    """Raised on a disposition outside the closed vocabulary (the ``DF-10-4-E`` shape).

    A ``ValueError`` subclass (AR10), matching 12.5's ``_downgrade_sentence`` and 12.8's
    exhaustive dispatch: an unregistered member RAISES rather than falling through to a
    default. A default here would be a disposition nobody chose, on the record whose
    entire purpose is that every disposition was chosen by a named human.
    """


class UnregisteredAdjudicator(ValueError):
    """Raised when a disposition is attributed to a role protocol §2 does not register."""


#: The CLOSED disposition vocabulary. Checked in BOTH directions by
#: ``TC-ArgusAgent-PRECISION-001-38``: an unregistered member raises, and a member that
#: exists here but is not exercised by the guards is itself a finding.
DISPOSITIONS: dict[str, str] = {
    "TP": (
        "TRUE POSITIVE — the named human inspected the cited locator and judges this a "
        "genuinely real blocking finding a human auditor would also raise (protocol §4). "
        "Enters the precision NUMERATOR and DENOMINATOR."
    ),
    "FP": (
        "FALSE POSITIVE — the named human inspected the cited locator and judges this a "
        "false accusation (protocol §4 step 1: the locator does not point at a genuine "
        "defect). Enters the precision DENOMINATOR only."
    ),
    "BORDERLINE": (
        "LOOKED AT, COULD NOT DECIDE — protocol §4's borderline ladder is engaged and has "
        "not terminated (locator re-examination -> golden-key correction -> external "
        "tie-break). A FIRST-CLASS outcome, not an absence: it records that a human spent "
        "the time and the question is genuinely open. It enters NEITHER side of the "
        "precision ratio, and it makes the run NON-EXHAUSTIVE until it resolves."
    ),
    "UNADJUDICATED": (
        "NOT YET JUDGED — the finding is in the population and no human has ruled on it. "
        "The ONLY member an automated producer may write, and it must carry no "
        "adjudicator. 12.6 / DN-8 applied: an UNADJUDICATED row that says so beats a TP "
        "row that guessed."
    ),
}

#: The members only a HUMAN may write. Enforced at construction, not by review.
HUMAN_DISPOSITIONS: tuple[str, ...] = ("TP", "FP", "BORDERLINE")

#: The members that enter precision = TP / (TP + FP). BORDERLINE and UNADJUDICATED are
#: deliberately absent: counting an undecided finding on either side would let the
#: denominator be moved by the act of not deciding.
DENOMINATOR_DISPOSITIONS: tuple[str, ...] = ("TP", "FP")

#: The adjudicating roles protocol §2 registers. ``TC-ArgusAgent-PRECISION-001-40``
#: cross-checks this tuple against §2's own table in both directions, so a role added to
#: the protocol without being registered here — or removed from the protocol while a row
#: still cites it — fails rather than drifting.
PROTOCOL_ADJUDICATOR_ROLES: tuple[str, ...] = (
    "Engineering Lead",
    "QA Lead",
    "External adjudicator",
)

#: ``<who> (<role>)`` — e.g. ``"XAgent007 (Engineering Lead)"``. The role must be
#: registered above; the name is who is accountable. An unattributed disposition is a
#: failure, which is why this is a construction-time regex and not a review checklist.
_ADJUDICATOR_RE = re.compile(r"^(?P<who>[A-Za-z0-9][A-Za-z0-9 ._@-]*) \((?P<role>[^()]+)\)$")

#: ISO-8601 calendar date. No clock is read anywhere in this module (AR8) — the date is
#: supplied by the producer and validated for SHAPE only.
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

#: A locator is ``<repository-relative posix path>:<line>``. The character class excludes
#: the backslash and the pattern refuses a leading ``/``, a drive letter and any ``..``
#: segment. Two reasons, and both have bitten this repository: NFR-S1 forbids an absolute
#: HOST path in any artifact, and the local gates here run on Windows only while CI runs
#: an ubuntu matrix — a locator built by string concatenation on one platform is a
#: cross-platform defect a green local suite would ship.
_LOCATOR_RE = re.compile(r"^(?![A-Za-z]:)(?!/)[A-Za-z0-9._@+#$/-]+:\d+$")

#: The CLOSED row schema, mirroring 13.1's ``MANIFEST_FIELDS`` discipline. Checked in both
#: directions on parse: an unknown key raises and a missing key raises. This is also how
#: NFR-S1 is enforced STRUCTURALLY rather than by scanning — there is no field a source
#: byte could enter, because every field is a bounded identifier, a boolean, a locator, a
#: registered vocabulary member, a date, a row id, or the human's prose REASON.
ROW_FIELDS: tuple[str, ...] = (
    "row_id",
    "member_id",
    "rule_id",
    "verdict_eligible",
    "advisory",
    "locator",
    "disposition",
    "adjudicator",
    "adjudicated_on",
    "reason",
    "supersedes",
)

_RECORD_FIELDS: tuple[str, ...] = (
    "schema_version",
    "story",
    "protocol_version",
    "adjudication_unit",
    "corpus_source",
    "reproducibility_verified",
    "reproducibility_source",
    "expert_hours",
    "expert_hours_note",
    "rows",
)

_SCHEMA_VERSION = "1"
_STORY = "13-2-adjudicate-every-finding-by-a-named-human"


def disposition_meaning(disposition: str) -> str:
    """The registered meaning of *disposition* — RAISES on an unregistered member.

    The exhaustive-dispatch seam (``DF-10-4-E``). Every consumer of a disposition routes
    through here rather than through a ``dict.get(..., default)``, so adding a fifth
    vocabulary member without teaching the consumers about it fails loudly at the first
    row that uses it.
    """
    try:
        return DISPOSITIONS[disposition]
    except KeyError:
        raise UnregisteredDisposition(
            f"disposition {disposition!r} is not a registered member of the closed "
            f"adjudication vocabulary {tuple(sorted(DISPOSITIONS))!r}. A disposition "
            f"outside the vocabulary is not a judgement — it is an unrecorded one."
        ) from None


def adjudicator_role(adjudicator: str) -> str:
    """The protocol §2 role an adjudicator id claims — RAISES if §2 does not register it.

    AC3's *"the human attribution is ASSERTED, not assumed"*. The id is
    ``"<who> (<role>)"``: the name carries accountability and the role carries the
    protocol's authority to adjudicate at all.
    """
    match = _ADJUDICATOR_RE.match(adjudicator or "")
    if match is None:
        raise UnregisteredAdjudicator(
            f"adjudicator {adjudicator!r} is not of the form '<who> (<role>)' — an "
            f"unattributed disposition is a failure (protocol §2)."
        )
    role = match.group("role").strip()
    if role not in PROTOCOL_ADJUDICATOR_ROLES:
        raise UnregisteredAdjudicator(
            f"adjudicator {adjudicator!r} claims role {role!r}, which "
            f"precision-validation-protocol.md §2 does not register. Registered roles: "
            f"{PROTOCOL_ADJUDICATOR_ROLES!r}."
        )
    return role


def finding_row_id(
    *,
    member_id: str,
    rule_id: str,
    verdict_eligible: bool,
    advisory: bool,
    locator: str,
    revision: int = 0,
) -> str:
    """A DERIVED, stable row id: ``<12 hex of the finding identity>.<revision>``.

    Content-addressed through the ONE canonical serializer (AR4/``DF-4-x``: never a second
    serializer or hasher), so regenerating the record over an unchanged corpus reproduces
    byte-identical ids and a re-seed cannot silently renumber a human's rows. ``revision``
    increments only when a judgement is CORRECTED, and the correcting row must name the
    row it supersedes — §3.4's supersede-never-erase rule, mechanised.
    """
    digest = hashlib.sha256(
        dumps_bytes(
            {
                "member_id": member_id,
                "rule_id": rule_id,
                "verdict_eligible": verdict_eligible,
                "advisory": advisory,
                "locator": locator,
            }
        )
    ).hexdigest()[:12]
    return f"{digest}.{int(revision)}"


@dataclass(frozen=True)
class AdjudicationRow:
    """ONE adjudication of ONE finding — the append-only unit of the record (AC3).

    Every field the epic's §3.4 clause names is present and REQUIRED where it can be:
    the finding identity, the corpus member, >=1 locator (FR13), the disposition, the
    adjudicator id, the date, a reason, and ``supersedes`` for a correction.

    Validation happens in ``__post_init__`` — i.e. at CONSTRUCTION, not at a call site —
    so there is no path that produces an invalid row and no reviewer who has to remember
    to look. In particular an ``UNADJUDICATED`` row carrying an adjudicator name RAISES:
    that is the shape a machine would produce if it started filling in the human's
    judgements, and it is the one thing this record exists to prevent.
    """

    row_id: str
    member_id: str
    rule_id: str
    verdict_eligible: bool
    advisory: bool
    locator: str
    disposition: str
    adjudicator: str | None = None
    adjudicated_on: str | None = None
    reason: str | None = None
    supersedes: str | None = None

    def __post_init__(self) -> None:
        disposition_meaning(self.disposition)  # raises on an unregistered member
        if not self.member_id or not self.member_id.strip():
            raise ValueError(f"row {self.row_id!r}: member_id is empty")
        if not self.rule_id.isidentifier():
            raise ValueError(
                f"row {self.row_id!r}: rule_id {self.rule_id!r} is not an identifier — "
                f"the record carries RULE-ID PROVENANCE, never source bytes (NFR-S1)"
            )
        if not _LOCATOR_RE.match(self.locator) or ".." in self.locator.split("/"):
            raise ValueError(
                f"row {self.row_id!r}: locator {self.locator!r} is not a "
                f"repository-relative '<posix/path>:<line>'. An absolute or host path in "
                f"an artifact breaches NFR-S1, and a backslash-separated one is a "
                f"Windows-only locator in a repository whose CI runs an ubuntu matrix."
            )
        if self.disposition in HUMAN_DISPOSITIONS:
            adjudicator_role(self.adjudicator or "")
            if not _DATE_RE.match(self.adjudicated_on or ""):
                raise ValueError(
                    f"row {self.row_id!r}: disposition {self.disposition!r} requires an "
                    f"ISO-8601 adjudicated_on date; got {self.adjudicated_on!r}"
                )
            if not (self.reason or "").strip():
                raise ValueError(
                    f"row {self.row_id!r}: disposition {self.disposition!r} requires a "
                    f"REASON. A judgement without a reason cannot be re-examined, and "
                    f"protocol §4's borderline ladder is a re-examination procedure."
                )
        else:
            if self.adjudicator is not None or self.adjudicated_on is not None:
                raise ValueError(
                    f"row {self.row_id!r}: disposition {self.disposition!r} is NOT a "
                    f"human judgement, so it must carry no adjudicator and no date; got "
                    f"adjudicator={self.adjudicator!r}, "
                    f"adjudicated_on={self.adjudicated_on!r}. Attributing an "
                    f"unadjudicated row to a human is the fabrication this record exists "
                    f"to make impossible (DN-6)."
                )

    @property
    def match_key(self) -> MatchKey:
        """The SHARED 6.6 match key, reused unchanged (DN-MATCH-KEY-REUSE)."""
        return (self.rule_id, self.verdict_eligible, self.advisory)

    @property
    def finding_id(self) -> str:
        """The PER-FINDING identity (AC2): the match key plus member and locator.

        Two findings of the same rule class in the same member at different lines are two
        findings, and protocol §7 measures precision over findings. This is the coordinate
        that makes 31 blocking findings 31 rather than 1.
        """
        return f"{self.member_id}::{self.rule_id}::{self.verdict_eligible!r}::{self.advisory!r}::{self.locator}"

    @property
    def is_human_judgement(self) -> bool:
        """Whether this row carries a judgement only the named human could have made."""
        return self.disposition in HUMAN_DISPOSITIONS

    def to_payload(self) -> dict[str, Any]:
        """The row's canonical mapping — exactly :data:`ROW_FIELDS`, no more, no less."""
        return {field: getattr(self, field) for field in ROW_FIELDS}

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> AdjudicationRow:
        """Parse a row, enforcing the CLOSED schema in BOTH directions.

        An unknown key raises (a field nobody registered is a field nobody guards) and a
        missing key raises (a row silently defaulting its disposition is the failure mode
        with the worst blast radius here).
        """
        keys = set(payload)
        unknown = keys - set(ROW_FIELDS)
        missing = set(ROW_FIELDS) - keys
        if unknown or missing:
            raise ValueError(
                f"adjudication row schema violation: unknown={sorted(unknown)!r}, "
                f"missing={sorted(missing)!r}; the closed schema is {ROW_FIELDS!r}"
            )
        return cls(**{field: payload[field] for field in ROW_FIELDS})


@dataclass(frozen=True)
class Exhaustive:
    """Protocol §4 satisfied: EVERY emitted finding carries exactly one live judgement."""

    adjudicated_count: int

    def __str__(self) -> str:  # pragma: no cover - trivial
        return (
            f"EXHAUSTIVE — all {self.adjudicated_count} emitted finding(s) carry exactly "
            f"one live human disposition (protocol §4: full-corpus, not sampled)"
        )


@dataclass(frozen=True)
class AdjudicationUnevaluable:
    """The run could not be evaluated, RECORDED with its counts — never a pass (DN-5).

    A distinct TYPE rather than a flag, following ``scripts/release_preflight.py``'s
    ``Refusal`` / ``Unevaluable`` / ``None`` precedent, so that no call site can treat it
    as falsy by forgetting to look. The residual counts are on the object because *"the
    result is Unevaluable, recorded with the member count actually available"* is the
    requirement — an unqualified "unevaluable" is barely better than a skip.
    """

    reason: str
    residual_count: int
    adjudicated_count: int
    residual_finding_ids: tuple[str, ...] = ()

    def __str__(self) -> str:  # pragma: no cover - trivial
        return (
            f"UNEVALUABLE — {self.reason}; {self.adjudicated_count} finding(s) carry a "
            f"live human disposition and {self.residual_count} do NOT"
        )


@dataclass(frozen=True)
class AdjudicationRecord:
    """The committed, machine-readable, append-only adjudication record (AC3).

    APPEND-ONLY is a PROPERTY, not a promise: :meth:`append` returns a new record with the
    rows added, ``__post_init__`` refuses a second live row for one finding, and a
    corrected judgement is admissible only as a row that NAMES the row it supersedes.
    Rewriting a prior row is not expressible through this type.
    """

    protocol_version: str
    adjudication_unit: str
    corpus_source: str
    reproducibility_verified: bool
    reproducibility_source: str
    expert_hours: Fraction | None
    expert_hours_note: str
    rows: tuple[AdjudicationRow, ...]

    def __post_init__(self) -> None:
        if self.adjudication_unit != ADJUDICATION_UNIT:
            raise ValueError(
                f"adjudication_unit {self.adjudication_unit!r} != {ADJUDICATION_UNIT!r}. "
                f"Protocol §7 locks precision over FINDINGS; a record adjudicated in a "
                f"different unit is not comparable with the threshold it is measured "
                f"against (AC2)."
            )
        ids = [row.row_id for row in self.rows]
        if len(ids) != len(set(ids)):
            duplicated = sorted({i for i in ids if ids.count(i) > 1})
            raise ValueError(f"duplicate row_id(s) in the record: {duplicated!r}")
        known = set(ids)
        superseded = set()
        by_id = {row.row_id: row for row in self.rows}
        for row in self.rows:
            if row.supersedes is None:
                continue
            if row.supersedes not in known:
                raise ValueError(
                    f"row {row.row_id!r} supersedes {row.supersedes!r}, which is not in "
                    f"the record. A correction must NAME the judgement it replaces "
                    f"(§3.4: supersede, strike, never erase)."
                )
            if by_id[row.supersedes].finding_id != row.finding_id:
                raise ValueError(
                    f"row {row.row_id!r} supersedes a row about a DIFFERENT finding "
                    f"({by_id[row.supersedes].finding_id!r})"
                )
            superseded.add(row.supersedes)
        live_by_finding: dict[str, str] = {}
        for row in self.rows:
            if row.row_id in superseded:
                continue
            previous = live_by_finding.get(row.finding_id)
            if previous is not None:
                raise ValueError(
                    f"finding {row.finding_id!r} carries TWO live rows ({previous!r} and "
                    f"{row.row_id!r}). A corrected judgement is recorded as a CORRECTION "
                    f"with its date and reason — never as a second opinion sitting beside "
                    f"the first, and never by rewriting the first (§3.4)."
                )
            live_by_finding[row.finding_id] = row.row_id
        if self.expert_hours is not None and self.expert_hours < 0:
            raise ValueError(f"expert_hours {self.expert_hours!r} is negative")

    # ── reading ───────────────────────────────────────────────────────────────────

    @property
    def superseded_row_ids(self) -> frozenset[str]:
        """The ids of rows a later correction replaced. Retained, never deleted."""
        return frozenset(
            row.supersedes for row in self.rows if row.supersedes is not None
        )

    def live_rows(self) -> tuple[AdjudicationRow, ...]:
        """The CURRENT judgement per finding — superseded rows excluded, never removed."""
        superseded = self.superseded_row_ids
        return tuple(row for row in self.rows if row.row_id not in superseded)

    def live_dispositions(self) -> dict[str, AdjudicationRow]:
        """``finding_id -> the live row``. Exactly one per finding, by construction."""
        return {row.finding_id: row for row in self.live_rows()}

    def counts(self) -> dict[str, int]:
        """Live row counts per registered vocabulary member — every member present.

        Every key of :data:`DISPOSITIONS` appears even at zero, so a consumer reading
        ``counts()["BORDERLINE"]`` cannot get a ``KeyError`` that reads like a zero.
        """
        tally = {name: 0 for name in DISPOSITIONS}
        for row in self.live_rows():
            tally[row.disposition] += 1
        return tally

    # ── writing (append-only) ─────────────────────────────────────────────────────

    def append(self, rows: Iterable[AdjudicationRow]) -> AdjudicationRecord:
        """A NEW record with *rows* appended. The only write door, and it never erases."""
        return replace(self, rows=self.rows + tuple(rows))

    # ── the two §4 preconditions ──────────────────────────────────────────────────

    def exhaustiveness(
        self, expected_finding_ids: Sequence[str]
    ) -> Exhaustive | AdjudicationUnevaluable:
        """Protocol §4: EVERY emitted finding classified, nothing sampled out (AC4).

        **Non-vacuity is mandatory and is checked FIRST** (the ``-39`` argparse-internals
        precedent, ``AI-E11-1``): a guard that silently iterates an empty record passes
        forever, and here that guard is the one protecting the externalization gate. An
        empty expected population is itself :class:`AdjudicationUnevaluable` — it means
        the corpus could not be read, not that everything in it was judged.

        A finding with no row, or whose live row is ``UNADJUDICATED`` or ``BORDERLINE``,
        is a RESIDUAL. Any residual makes the run Unevaluable **with the residual count**
        — never a pass over the adjudicated subset.
        """
        expected = tuple(expected_finding_ids)
        if not expected:
            return AdjudicationUnevaluable(
                reason=(
                    "the emitted finding population is EMPTY — nothing was extracted to "
                    "adjudicate, so exhaustiveness is unobservable rather than satisfied "
                    "(non-vacuity floor, AI-E11-1)"
                ),
                residual_count=0,
                adjudicated_count=0,
            )
        live = self.live_dispositions()
        residual = tuple(
            sorted(
                finding_id
                for finding_id in expected
                if finding_id not in live
                or live[finding_id].disposition not in DENOMINATOR_DISPOSITIONS
            )
        )
        adjudicated = len(expected) - len(residual)
        if residual:
            return AdjudicationUnevaluable(
                reason=(
                    f"{len(residual)} of {len(expected)} emitted finding(s) carry no live "
                    f"TP/FP disposition (protocol §4 requires the FULL populated corpus, "
                    f"not a sample). What would close the gap: the named human "
                    f"(protocol §2) adjudicates each residual finding at its cited locator"
                ),
                residual_count=len(residual),
                adjudicated_count=adjudicated,
                residual_finding_ids=residual,
            )
        return Exhaustive(adjudicated_count=adjudicated)

    def determinism_precondition(self) -> None | AdjudicationUnevaluable:
        """Protocol §4's last bullet: adjudication is only valid over a reproducible run.

        REUSES the existing check rather than adding a second one: byte-reproducibility
        across two runs over the same corpus is measured by
        ``scripts/audit_validation_corpus.py`` (Story 13.1) and recorded per member on the
        adjudication set as ``byte_reproducible_across_two_runs``. This method reads that
        result off the record and converts a negative into a RECORDED invalidity, so the
        record says the adjudication rests on nothing rather than carrying dispositions
        that do.
        """
        if self.reproducibility_verified:
            return None
        return AdjudicationUnevaluable(
            reason=(
                f"the NFR-P1 byte-reproducibility precondition is NOT satisfied over this "
                f"corpus ({self.reproducibility_source}). Protocol §4: adjudication is "
                f"only valid over a byte-reproducible harness run, and the check runs "
                f"BEFORE any pass/fail is recorded"
            ),
            residual_count=len(self.live_rows()),
            adjudicated_count=0,
        )

    # ── serialization (the ONE serializer, AR4) ───────────────────────────────────

    def to_payload(self) -> dict[str, Any]:
        """The record's canonical mapping — exactly :data:`_RECORD_FIELDS`."""
        return {
            "schema_version": _SCHEMA_VERSION,
            "story": _STORY,
            "protocol_version": self.protocol_version,
            "adjudication_unit": self.adjudication_unit,
            "corpus_source": self.corpus_source,
            "reproducibility_verified": self.reproducibility_verified,
            "reproducibility_source": self.reproducibility_source,
            "expert_hours": (
                None if self.expert_hours is None else str(self.expert_hours)
            ),
            "expert_hours_note": self.expert_hours_note,
            "rows": [row.to_payload() for row in self.rows],
        }

    def to_bytes(self) -> bytes:
        """The committed bytes, through ``argus.store.canonical`` — never ``json.dumps``."""
        return dumps_bytes(self.to_payload())

    def to_text(self) -> str:
        """The committed text, through ``argus.store.canonical`` — never ``json.dumps``."""
        return dumps(self.to_payload())

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> AdjudicationRecord:
        """Parse a record, enforcing the CLOSED schema in BOTH directions."""
        keys = set(payload)
        unknown = keys - set(_RECORD_FIELDS)
        missing = set(_RECORD_FIELDS) - keys
        if unknown or missing:
            raise ValueError(
                f"adjudication record schema violation: unknown={sorted(unknown)!r}, "
                f"missing={sorted(missing)!r}; the closed schema is {_RECORD_FIELDS!r}"
            )
        if payload["schema_version"] != _SCHEMA_VERSION:
            raise ValueError(
                f"adjudication record schema_version {payload['schema_version']!r} != "
                f"{_SCHEMA_VERSION!r}"
            )
        hours = payload["expert_hours"]
        return cls(
            protocol_version=payload["protocol_version"],
            adjudication_unit=payload["adjudication_unit"],
            corpus_source=payload["corpus_source"],
            reproducibility_verified=bool(payload["reproducibility_verified"]),
            reproducibility_source=payload["reproducibility_source"],
            expert_hours=None if hours is None else Fraction(hours),
            expert_hours_note=payload["expert_hours_note"],
            rows=tuple(AdjudicationRow.from_payload(row) for row in payload["rows"]),
        )


def load_record(path: Path) -> AdjudicationRecord:
    """Read + parse the committed record. The module's ONLY I/O, and the caller owns the path.

    ``encoding="utf-8"`` is explicit: this repository's local gates run on Windows, whose
    default encoding is not UTF-8, while CI runs an ubuntu matrix — an implicit encoding
    is a cross-platform divergence a green local suite would ship.
    """
    return AdjudicationRecord.from_payload(loads(path.read_text(encoding="utf-8")))


def change_log_head_version(markdown: str) -> str:
    """The CURRENT head version of a protocol change log — the first data row's version.

    A PURE analyzer over the document text (no path, no I/O), so the guard and the record
    producer read the head the same way. The change log is newest-first, so the head is
    the first ``| <date> | <version> | ...`` row after the header separator.

    AC2's *"ordering is mechanical, not a promise"*: the record carries the protocol
    version it was adjudicated under, and a committed guard asserts that version equals
    this head. A record adjudicated under a superseded protocol fails — which is what
    makes *"the protocol is amended BEFORE the run, never reinterpreted during it"* an
    enforced ordering rather than an instruction nobody can check.
    """
    lines = markdown.splitlines()
    try:
        start = next(
            i for i, line in enumerate(lines) if line.strip().lower() == "## change log"
        )
    except StopIteration:
        raise ValueError(
            "the protocol document carries no '## Change log' section, so its head "
            "version is unreadable — the version guard would be vacuous"
        ) from None
    for line in lines[start + 1 :]:
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("|") or set(stripped) <= set("|- "):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() in ("date",):
            continue
        return cells[1]
    raise ValueError(
        "the protocol change log has no data rows — a version guard over an empty change "
        "log passes forever (non-vacuity floor, AI-E11-1)"
    )


def validation_set_population_n() -> int:
    """N for the REPOSITORY corpus — MEASURED through 13.1's derived count, never typed.

    Calls ``tests/corpus/_manifest.eligible_member_count()`` through the harness's declared
    lazy edge (``DF-9-2-A``). AC1a's warning, honoured: *"AC1a's N comes from 13.1, not
    from a new count … authoring a second eligible-member count here is the fork 13.1's
    DN-3 already refused, and it would let the two disagree about N."*
    """
    return int(corpus_manifest_module().eligible_member_count())


def expert_hours_report(
    hours: Fraction | None, *, ceiling: Fraction = EXPERT_HOURS_CEILING
) -> str:
    """§3's budget compared to the actual, AS A REPORT — never as a gate (AC5).

    §3 states the budget is *"a ceiling, not a target"* and that an overrun *"is a signal
    the cartridge is ambiguous"*. So exceeding it is recorded, never failed: this function
    returns a sentence and no caller may branch a pass/fail on it. **Never trim an
    adjudication to fit the estimate** — that trades a measurement for a number.
    """
    if hours is None:
        return (
            f"expert-hours NOT RECORDED: no adjudication run has taken place, so there "
            f"are no actual hours to compare against §3's <= {ceiling} expert-hour "
            f"ceiling. A zero here would claim the work took no time rather than that it "
            f"has not happened."
        )
    if hours > ceiling:
        return (
            f"expert-hours {hours} EXCEEDS §3's <= {ceiling} ceiling by "
            f"{hours - ceiling}. RECORDED, NOT FAILED: §3 calls the budget 'a ceiling, "
            f"not a target' and an overrun 'a signal the cartridge is ambiguous'. The "
            f"overrun and what made it expensive belong in the record; trimming the "
            f"adjudication to fit the estimate does not."
        )
    return (
        f"expert-hours {hours} is within §3's <= {ceiling} ceiling "
        f"({ceiling - hours} unused). Recorded so the next run can be scheduled on "
        f"evidence rather than on the estimate."
    )


@dataclass(frozen=True)
class AdjudicatedPrecision:
    """The precision MEASUREMENT folded from human dispositions (13.2's deliverable).

    It is deliberately NOT a decision. ``protocol_cleared`` is threaded through
    unchanged and is never defaulted ``True`` here or anywhere in ``argus/**``; computing
    the four §5 conditions and flipping the gate is **Story 13.3**. A story that both
    repaired the instrument and flipped the gate with it would be measuring its own
    homework.
    """

    total_tp: int
    total_fp: int
    total_borderline: int
    total_unadjudicated: int
    precision: Fraction | None
    precision_ratio: str
    n: int
    floor_n: int
    provisional: bool
    meets_threshold: bool
    clean_repo_fp_applicable: bool
    clean_repo_fp_note: str
    exhaustiveness: Exhaustive | AdjudicationUnevaluable
    determinism: None | AdjudicationUnevaluable
    expert_hours_report: str
    gate_status: str

    @property
    def evaluable(self) -> bool:
        """Whether this fold produced a precision MEASUREMENT at all (DN-5).

        All three must hold: the run was byte-reproducible, the corpus was exhaustively
        adjudicated, and the denominator is non-empty. Any one of them false means the
        answer is ``Unevaluable``, recorded — not a number.
        """
        return (
            self.determinism is None
            and isinstance(self.exhaustiveness, Exhaustive)
            and self.precision is not None
        )


def fold_adjudicated_precision(
    record: AdjudicationRecord,
    *,
    expected_finding_ids: Sequence[str],
    population_n: int,
    floor_n: int,
    protocol_cleared: bool = False,
    protocol_path: str = PROTOCOL_PATH,
) -> AdjudicatedPrecision:
    """Fold the human dispositions into the SHARED precision arithmetic (DN-1).

    Protocol §2 already settles the semantics: *"A finding's classification (TP/FP/FN) is
    mechanically derived by the harness from the golden key; the human roles above
    adjudicate the golden key itself."* On a real repository there is no golden key, so —
    per §4 as amended by 13.1 — **the human dispositions ARE the ground truth**, and this
    function is the mechanical derivation over them.

    Order matters and is the protocol's, not a convenience: the **determinism**
    precondition is evaluated first (§4's last bullet: *"before any pass/fail is
    recorded"*), then **exhaustiveness** (§4: full corpus, not sampled), and only then the
    ratio. A precision figure produced ahead of either would be a number resting on
    nothing.
    """
    determinism = record.determinism_precondition()
    exhaustive = record.exhaustiveness(expected_finding_ids)
    tally = record.counts()
    total_tp = tally["TP"]
    total_fp = tally["FP"]

    measured = precision_fraction(total_tp, total_fp)
    # Only a run that is reproducible AND exhaustive may report a ratio at all. A ratio
    # over the subset that happened to be adjudicated is exactly the sampled measurement
    # §4 forbids, and it would be indistinguishable from an honest one downstream.
    valid = determinism is None and isinstance(exhaustive, Exhaustive)
    precision = measured if valid else None
    provisional = gate_is_provisional(
        n=population_n,
        floor_n=floor_n,
        protocol_cleared=protocol_cleared,
        precision=precision,
    )
    # AC1c over the REPOSITORY corpus: §5's clean-repo blocking-FP condition is defined
    # over cartridge members with an empty golden key AND ``max_blocking == 0``. No
    # repository-corpus member has either, so the condition is vacuously satisfied for
    # every possible input here. It is recorded NOT APPLICABLE with that reason rather
    # than reported as one of the four §5 conditions having been met.
    clean_note = (
        "NOT APPLICABLE over the repository corpus: protocol §5's clean-repo blocking-FP "
        "condition is defined over a member with an EMPTY GOLDEN KEY and max_blocking == "
        "0 (replay_harness._is_clean_repo), and no repository-corpus member has either — "
        "so the condition is satisfied by construction for every possible input and "
        "cannot fail. A condition that cannot fail is not a threshold. It remains a real "
        "threshold over the CARTRIDGE corpus, where compute_precision measures it and "
        "reports clean_repo_fp_applicable=True."
    )
    return AdjudicatedPrecision(
        total_tp=total_tp,
        total_fp=total_fp,
        total_borderline=tally["BORDERLINE"],
        total_unadjudicated=tally["UNADJUDICATED"],
        precision=precision,
        precision_ratio=(
            "NOT COMPUTED BY THIS RUN"
            if precision is None
            else f"{precision.numerator}/{precision.denominator}"
        ),
        n=population_n,
        floor_n=floor_n,
        provisional=provisional,
        meets_threshold=precision is not None and precision >= PRECISION_GATE_THRESHOLD,
        clean_repo_fp_applicable=False,
        clean_repo_fp_note=clean_note,
        exhaustiveness=exhaustive,
        determinism=determinism,
        expert_hours_report=expert_hours_report(record.expert_hours),
        gate_status=precision_gate_status_for(
            precision=precision,
            n=population_n,
            provisional=provisional,
            protocol_path=protocol_path,
            floor_n=floor_n,
            population_label="eligible validation-set repositories",
            evaluable=precision is not None,
        ),
    )
