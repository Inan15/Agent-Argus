"""Story 16.5 — WHO judged the precision figure, and whether they were independent.

Verification area ``TC-ArgusAgent-PRECISION-001-105``.. (``tests/test_gate_independence.py``).
Drivers: `precision-validation-protocol.md` §2 (the three registered adjudicating roles, the
2026-08-16 attribution amendment, and the **2026-08-22 dated block** that fills the QA Lead
and hands *"whether any given adjudication was independent"* to this story); **AR7** (reuse,
never fork — nothing here renders a gate-status sentence, it renders a CLAUSE for the one
renderer to place); **AR8** (pure — no I/O, no clock, no network, and no module-level
repository-only path, ``DF-9-2-A``: every input arrives as an argument); **AR10** (typed
failures); **NFR-M1**; **NFR-P1**.

What this module is
-------------------
:class:`~argus.precision.gate_decision.GateDecision` has carried ``adjudicators`` since
Story 13.3 and published it under ``adjudication_record.adjudicators`` ever since. Measured
at HEAD ``52143eb``: **zero** assertions anywhere in ``tests/**`` or ``scripts/**`` close
over that field, and **no** surface renders it beside the precision figure. So a reader who
wants to know whether the precision figure was judged by the people who wrote the tool has
to open a JSON artifact, find a nested list of ``"<who> (<role>)"`` strings, and know that
protocol §2 registers three roles and that one of them is the one §2 says *"SHOULD be
outside the implementing team"*.

This module turns that reconstruction into a **derived, published status** that travels on
the same sentence as the precision figure, so the two cannot be quoted apart.

⛔ **It is a DISCLOSURE, not a condition.** Protocol §5 carries **seven** conditions and this
module adds none. :attr:`~argus.precision.gate_decision.GateDecision.precision_evaluable`
keeps exactly four conjuncts and the independence arm is never one of them. The honest
answer today is *"not independent"*, and a condition would convert an honest **no** into a
blocked gate that only a hiring decision could unblock — i.e. it would hold the
externalization gate hostage to filling a role. §2 says the external sign-off *"SHOULD be
outside the implementing team"*; **SHOULD is not MUST**, and promoting it is a threshold
change no implementation story may make (protocol §6 R2).

DERIVED FROM THE RECORD, NEVER FROM §2's PROSE (DN-16-5-3)
----------------------------------------------------------
The status is derived from the ``"<who> (<role>)"`` ids on the **live rows** of the
committed adjudication record — reached through the ``adjudicators`` tuple ``decide_gate``
already computes, so nothing here recounts the record — and every id is parsed through the
**existing** :func:`~argus.precision.adjudication.adjudicator_role`. There is no second
parser, no second regex and no second role list: the three role names are **destructured**
out of :data:`~argus.precision.adjudication.PROTOCOL_ADJUDICATOR_ROLES` below, so a fourth
role added to the protocol fails at import rather than drifting into a silent mis-derivation.

*Rejected:* parsing protocol §2's markdown holder table. It is prose, it can drift from the
record, and it answers a **different question** — §2 records who **may** judge; the record
records who **did**.

*Rejected:* a third :class:`~argus.verdict.negative_assurance.InstrumentStatus` member
(DN-16-5-2). That vocabulary bounds **the instrument, per tool VERSION**, and is removed
only by the >=80% gate clearing. This one bounds **one adjudication run** and changes
whenever the record does. Merging them is exactly the run-grade/instrument-status confusion
that enum's own docstring warns against.

*Rejected:* a wrapper that appends the note to a returned status string (DN-16-5-5). String
surgery on another function's output is a second mechanism (AR7) that forks the day the
first one's wording changes, and it cannot be made byte-stable across the three branches.
:func:`independence_note` returns a **clause**; the ONE renderer,
:func:`~argus.precision.replay_harness.precision_gate_status_for`, places it.

*Rejected:* attaching the note to every ``precision_gate_status_for`` call site
(DN-16-5-6). The dogfood generator passes ``precision=None`` and reads no record at all, and
the cartridge fold has golden keys, not adjudicators. A sentence about independence on
either would describe a judgement that never happened.

A ROLE THAT DID NOT JUDGE IS NOT A ROLE NOBODY FILLED (DN-16-5-4)
-----------------------------------------------------------------
As of ``1bb7088`` (2026-08-22) the **QA Lead** role is FILLED — Veer Pratap Singh — and has
authored **zero** dispositions. *Filled* and *judged* are now different facts about
different roles, so a sentence reading "QA Lead: absent" would be read as *unfilled* and
would be **false**: a true statement whose subject a reader gets wrong, which is
``DF-9-2-B``'s class on the surface that publishes the gate. Every sentence this module
renders therefore says, in its own words, that it is a claim about **the adjudication that
was performed** and not about §2's roster — which this module does not read.

``NOT_ESTABLISHED`` AND ``NOT_INDEPENDENT`` ARE NOT SYNONYMS
------------------------------------------------------------
*Nothing was judged* and *the author judged everything* are different findings, and the
distinction is the one ``BLOCKED`` vs ``NOT_CLEARED`` already makes one level in
(``AI-E11-1``: an absent population is unobservable, not clean). They must not collapse.

PURE (AR8). Nothing here reads a file, a clock, a network or an environment variable.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from argus.precision.adjudication import PROTOCOL_ADJUDICATOR_ROLES, adjudicator_role

__all__ = [
    "ENGINEERING_LEAD_ROLE",
    "EXTERNAL_ADJUDICATOR_ROLE",
    "INDEPENDENCE_STATUSES",
    "QA_LEAD_ROLE",
    "IndependenceAssessment",
    "UnregisteredIndependenceStatus",
    "assess_independence",
    "independence_note",
    "independence_status_meaning",
]

#: The three registered roles, DESTRUCTURED out of protocol §2's own tuple rather than
#: re-typed (AC1.3 / AC1.4). A fourth role added to
#: :data:`~argus.precision.adjudication.PROTOCOL_ADJUDICATOR_ROLES` fails HERE, at import,
#: with a ``ValueError`` — which is the honest outcome, because the derivation below is a
#: closed dispatch over exactly these three and a fourth role would need a decision, not a
#: default (``DF-10-4-E``).
ENGINEERING_LEAD_ROLE, QA_LEAD_ROLE, EXTERNAL_ADJUDICATOR_ROLE = PROTOCOL_ADJUDICATOR_ROLES


class UnregisteredIndependenceStatus(ValueError):
    """Raised on a status outside :data:`INDEPENDENCE_STATUSES` (the ``DF-10-4-E`` shape).

    A ``ValueError`` subclass (AR10), the ``UnregisteredGateOutcome`` /
    ``UnregisteredDisposition`` house shape. A silent default here would publish a claim
    about who judged that nobody derived — on the one surface this project's
    externalization claim rests on.
    """


#: The CLOSED status vocabulary: member -> the REGISTERED meaning, which is also the clause
#: :meth:`IndependenceAssessment.note` renders, so the published sentence and the registered
#: meaning are ONE string and cannot drift. Checked in BOTH directions by
#: ``TC-ArgusAgent-PRECISION-001-105``: an unregistered member raises, and a member no
#: generated population reaches is itself a finding (``AI-E11-1``).
INDEPENDENCE_STATUSES: dict[str, str] = {
    "NOT_ESTABLISHED": (
        "NO live human judgement is recorded, so independence is UNOBSERVABLE rather than "
        "absent — nothing was judged, and 'nobody judged it' is not the same finding as "
        "'the author judged all of it' (AI-E11-1)"
    ),
    "NOT_INDEPENDENT": (
        "EVERY live human judgement on this record is authored by the Engineering Lead "
        "alone — the role that also implements the tool — so this precision figure was NOT "
        "judged independently of the implementing team (protocol §2: an externalization "
        "sign-off SHOULD be outside it; SHOULD is not MUST, so this is RECORDED, not gated)"
    ),
    "SECOND_REVIEWER_INTERNAL": (
        "the QA Lead second reviewer authored at least one live judgement and the External "
        "adjudicator authored none, so this adjudication carries a SECOND pair of eyes but "
        "both pairs are inside the implementing team (protocol §2 §4)"
    ),
    "EXTERNAL_ADJUDICATOR_PARTICIPATED": (
        "the External adjudicator (protocol §2's tie-break, the role §2 says SHOULD be "
        "outside the implementing team) authored at least one live judgement on this "
        "record, so at least part of this adjudication was judged from outside"
    ),
}

#: Rendered once, beside every status, and it is the whole of DN-16-5-4. A role that
#: authored nothing HERE may still be FILLED — the QA Lead has been since 2026-08-22 — and
#: this module derives from the RECORD and never reads §2's roster, so it must not be read
#: as saying which roles are filled.
ROSTER_DISCLAIMER = (
    "a claim about THIS adjudication run and NOT about protocol §2's roster, which is not "
    "read here: a registered role may be FILLED and have authored nothing on this record"
)


def independence_status_meaning(status: str) -> str:
    """The registered meaning of *status* — RAISES on an unregistered member.

    The exhaustive-dispatch seam (``DF-10-4-E``), matching
    :func:`~argus.precision.adjudication.disposition_meaning` and
    :func:`~argus.precision.gate_decision.gate_outcome_meaning`. Every consumer routes
    through here rather than through a ``dict.get(..., default)``, so a fifth member added
    without teaching the consumers about it fails loudly at the first use.
    """
    try:
        return INDEPENDENCE_STATUSES[status]
    except KeyError:
        raise UnregisteredIndependenceStatus(
            f"independence status {status!r} is not a registered member of the closed "
            f"vocabulary {tuple(sorted(INDEPENDENCE_STATUSES))!r}. An unregistered status "
            f"is not a disclosure about who judged — it is an undisclosed one."
        ) from None


@dataclass(frozen=True)
class IndependenceAssessment:
    """WHO judged this adjudication, and what that says about its independence.

    Every field is DERIVED by :func:`assess_independence` from the ``adjudicators`` tuple
    ``decide_gate`` already computes off the record's LIVE rows. Nothing here is typed and
    nothing here is recounted.
    """

    #: A member of :data:`INDEPENDENCE_STATUSES`, validated at construction.
    status: str
    #: The sorted ``"<who> (<role>)"`` ids that authored a live judgement (AC1.4).
    adjudicators: tuple[str, ...]
    #: The registered roles present on the record, in protocol §2's own order (AC1.4).
    roles_present: tuple[str, ...]
    #: The registered roles that authored NOTHING here, in protocol §2's own order. ⛔ Read
    #: it with :data:`ROSTER_DISCLAIMER`: absent from THIS record, not absent from §2.
    roles_absent: tuple[str, ...]

    def __post_init__(self) -> None:
        independence_status_meaning(self.status)
        overlap = set(self.roles_present) & set(self.roles_absent)
        if overlap:
            raise ValueError(
                f"role(s) {sorted(overlap)!r} are reported both present on and absent from "
                f"the same record. Present and absent are a PARTITION of "
                f"{PROTOCOL_ADJUDICATOR_ROLES!r}; an overlap means the derivation, not the "
                f"record, is wrong."
            )
        covered = tuple(self.roles_present) + tuple(self.roles_absent)
        if sorted(covered) != sorted(PROTOCOL_ADJUDICATOR_ROLES):
            raise ValueError(
                f"present {self.roles_present!r} + absent {self.roles_absent!r} do not "
                f"partition protocol §2's registered roles {PROTOCOL_ADJUDICATOR_ROLES!r}. "
                f"A role in neither list is a role this disclosure silently forgot."
            )

    @property
    def meaning(self) -> str:
        """The registered meaning of :attr:`status` — through the raising lookup."""
        return independence_status_meaning(self.status)

    @property
    def note(self) -> str:
        """The CLAUSE the one status renderer places — never a status sentence (AR7).

        It carries no ``precision=`` surface and no ``N=`` count, so it is not a
        gate-status sentence and ``TC-ArgusAgent-PRECISION-001-107``'s no-second-renderer
        walk correctly excludes it. What it does carry is the whole of AC1.4 and AC1.5:
        the status, its registered meaning, who judged, which registered roles authored
        nothing here, and — in its own words — that the last of those is a statement about
        the adjudication and not about the roster.
        """
        judged = (
            ", ".join(self.adjudicators)
            if self.adjudicators
            else "NOBODY — no live human judgement is recorded"
        )
        absent = (
            ", ".join(self.roles_absent)
            if self.roles_absent
            else "NONE — every registered role authored at least one"
        )
        return (
            f"adjudication independence: {self.status} — {self.meaning}; judged by "
            f"{judged}; registered protocol §2 role(s) that authored NO live judgement "
            f"here: {absent} ({ROSTER_DISCLAIMER})"
        )

    def to_payload(self) -> dict[str, object]:
        """The canonical mapping — serialized through ``argus.store.canonical`` upstream.

        The ``breadth`` / ``seal`` / ``yield`` precedent: a machine reader takes the status
        off a key and never has to parse the sentence (AC2.5).
        """
        return {
            "status": self.status,
            "status_meaning": self.meaning,
            "status_vocabulary": dict(INDEPENDENCE_STATUSES),
            "adjudicators": list(self.adjudicators),
            "registered_roles": list(PROTOCOL_ADJUDICATOR_ROLES),
            "roles_present": list(self.roles_present),
            "roles_absent": list(self.roles_absent),
            "roles_absent_meaning": ROSTER_DISCLAIMER,
            "gates_anything": False,
            "note": self.note,
        }


def _ordered_roles(roles: set[str]) -> tuple[str, ...]:
    """*roles*, in protocol §2's own order — never in insertion or hash order."""
    return tuple(role for role in PROTOCOL_ADJUDICATOR_ROLES if role in roles)


def _derive_status(roles_present: tuple[str, ...], *, any_adjudicator: bool) -> str:
    """THE predicate. One derivation, driven by every guard — no second copy.

    The order is protocol §2's ladder read from the outside in, and it is deliberate: the
    External adjudicator is the only role §2 says SHOULD be outside the implementing team,
    so its participation is the strongest available claim and is reported first. A record
    carrying BOTH a QA Lead and an External judgement is
    ``EXTERNAL_ADJUDICATOR_PARTICIPATED``, because the weaker finding would understate what
    actually happened.
    """
    if not any_adjudicator:
        return "NOT_ESTABLISHED"
    if EXTERNAL_ADJUDICATOR_ROLE in roles_present:
        return "EXTERNAL_ADJUDICATOR_PARTICIPATED"
    if QA_LEAD_ROLE in roles_present:
        return "SECOND_REVIEWER_INTERNAL"
    return "NOT_INDEPENDENT"


def assess_independence(adjudicators: Sequence[str]) -> IndependenceAssessment:
    """DERIVE who judged and whether they were independent — PURE (AR8).

    *adjudicators* is the tuple :func:`~argus.precision.gate_decision.decide_gate` already
    computes off ``record.live_rows()``: the distinct ``"<who> (<role>)"`` ids that authored
    a live judgement. It is READ, never recounted (AC1.3) — a second count over the record
    would be a second thing that can drift, and the drift would be invisible.

    Every id is parsed through the EXISTING
    :func:`~argus.precision.adjudication.adjudicator_role`, so a malformed id or a role §2
    does not register RAISES :exc:`~argus.precision.adjudication.UnregisteredAdjudicator`
    here exactly as it does at row construction. Defaulting it to "not independent" would
    publish a judgement about a role nobody registered.

    An EMPTY set yields ``NOT_ESTABLISHED``, never ``NOT_INDEPENDENT`` (``AI-E11-1``).
    """
    ids = tuple(sorted(set(adjudicators)))
    present = _ordered_roles({adjudicator_role(who) for who in ids})
    return IndependenceAssessment(
        status=_derive_status(present, any_adjudicator=bool(ids)),
        adjudicators=ids,
        roles_present=present,
        roles_absent=tuple(r for r in PROTOCOL_ADJUDICATOR_ROLES if r not in present),
    )


def independence_note(assessment: IndependenceAssessment | None) -> str | None:
    """The clause for :func:`precision_gate_status_for`, or ``None`` for the PRE-STORY shape.

    ``None`` in, ``None`` out, and a ``None`` note renders the exact bytes every surface
    rendered before Story 16.5 (NFR-P1). That is what lets one optional keyword be threaded
    through the fold and the three §5 arm renderers without any of them changing behaviour
    for any caller that does not pass it.
    """
    return None if assessment is None else assessment.note
