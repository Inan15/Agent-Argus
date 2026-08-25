"""Story 17.1 — the PRE-REGISTRATION: what would count as precision, written before the number.

    from precision_preregistration import evaluate, CRITERION_OUTCOMES, precision_floor

**WHAT A PRE-REGISTRATION IS, AND WHY IT IS DATED.** A pre-registration is a criterion committed
to the object database **before** the measurement it will judge exists. Its whole value is the
ORDER: a threshold chosen with the result already in view is not a threshold, it is a description
of the result. The date and the commit sha are therefore not decoration — they are the evidence,
and a guard reads them out of git rather than trusting this sentence.

**THE PRECEDENT THIS COPIES.** On 2026-08-17 this project wrote down, before Story 13.5 ran and
before Epic 15's bench was chosen, that *"we pursue ONE bench-expansion round ... if precision
lands below 80% we take option (b)"*. That rule is worth something for exactly one reason: no
number existed when it was written. Epic 17 is about to move the verdict-eligible population from
**zero** to something, and this module writes down what *"good enough"* means while the answer is
still zero. Story 15.1 did the same thing one level up in ``scripts/candidate_selection.py``.

**WHAT THIS MODULE JUDGES, AND WHAT IT DOES NOT.** It judges a candidate SUCCESSOR VACUITY
PREDICATE. It does **not** judge protocol section 5's externalization gate, and meeting the
criterion moves **no** gate condition. That distinction is load-bearing rather than pedantic:
measured at this story's HEAD, the intersection of the SEALED partition and the RATIFIED members
is **EMPTY** — every ratified member is ``pre-seal`` — so section 5's
``gate-evidence-drawn-from-the-sealed-partition`` condition reads FAILED over the population
Story 17.4 is chartered to measure, and it reads FAILED today, before any successor exists. Only
a protocol section 6 R2 operator act ratifying sealed members could change that, and no story in
Epic 17 may take one. A criterion silent on this invites exactly one sentence six weeks from now
-- *"precision came out at 84%, so the gate clears"* -- and it does not. See
:data:`CONSEQUENCE_MET`.

**NOTHING HERE RATIFIES, FETCHES OR SPENDS** (AC3). No corpus member is ratified; the eligible
member count is what it was. No third-party source is fetched -- protocol section 6 R2 says
verbatim that *"choosing which repositories are legitimate members, and fetching third-party
source, are not autonomous acts"*. No bench-expansion round is spent, ``DF-13-5-A`` stays OPEN and
UNSPENT, its branch (a) is not executed and its branch (b) is not declared. No protocol row is
added: :data:`PROTOCOL_VERSION` **names** V1.3, it does not create a version, and
``precision-validation-protocol.md`` is byte-unchanged. No FR is amended, no finding becomes
verdict-eligible and nothing published changes.

**NO SUCCESSOR PREDICATE IS IMPLEMENTED HERE.** Not a clause, not a scoring rule, not a line under
``argus/detectors/``. Story 17.2 specifies the successor and Story 17.3 builds it. This module
must be able to GRADE a population; it must never be able to PRODUCE one. The ban is enforced by
an ``ast`` walk in ``TC-ArgusAgent-PRECISION-001-141``, not by this paragraph -- which is what
converts *"it cannot look"* from a promise into a property.

**WHY ``scripts/`` AND NOT ``argus/precision/``** (``DN-17-1-1``). By subject matter this belongs
beside the gate. By cost it does not, and the costs are measured rather than felt: a byte under
``argus/**`` makes every committed dogfood artifact STALE and forces a regeneration commit; it
puts this file one directory from ``gate_seal.DETECTOR_TUNING_PATHS`` and its
``Evidence-partition:`` trailer obligation; it drags ``--cov=argus --cov-fail-under=80`` and the
blocking ``mypy argus`` / ``bandit -r argus`` gates over a module that ships in the wheel and is
never imported by ``argus.cli``. ``scripts/`` is still swept by NFR-M1's ``git ls-files -- '*.py'``
population, so the size ceiling still binds. Story 15.1 made the identical placement call and it
has held for two epics.

**PURITY (AR8), AND EXACTLY WHERE THE EDGE IS.** Every function below is a fold over its
arguments. No file is opened, no clock is read, no network is reached, no subprocess is spawned,
nothing is written -- at import or in any exported function. The two facts that live outside this
module -- protocol ``V1.3``'s change-log head, and the 26 false accusations in the pinned
adjudication record -- are reached the way this codebase reaches repository-only substrate
everywhere else: a repository-relative PATH constant plus a PURE predicate the CALLER feeds
(:data:`PROTOCOL_CHANGE_LOG_PATH` / :func:`refuse_protocol_drift`, :data:`EXPOSURE_SOURCE_PATH` /
:data:`EXPOSURE_SOURCE_SHA`). ``DF-9-2-A``: a module-level path resolution ships a wheel that
cannot import, and a module-level file read makes the criterion depend on the tree it is judging.

**RATES ARE EXACT** :class:`~fractions.Fraction` (AR4) -- never ``float``, never ``0.8``, never
the string ``"80%"``. The floors are RESOLVED by calling the functions that derive them
(``DN-3``: one floor, never forked; ``AI-E9-7``: constants are imported, never re-typed).
``TC-ArgusAgent-PRECISION-001-135`` walks this module's AST and fails on any numeric literal equal
to the threshold or to any derived floor, which is what stops the resolution silently becoming a
copy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from fractions import Fraction

from argus.precision.gate_breadth import (
    BREADTH_MEMBER_FLOOR_DERIVATION,
    contributing_member_floor,
)
from argus.precision.gate_conditions import (
    CONDITION_VERDICTS,
    condition_verdict_meaning,
)
from argus.precision.gate_seal import (
    SEALED_MEMBER_FLOOR_DERIVATION,
    sealed_member_floor,
)
from argus.precision.gate_yield import (
    YIELD_FLOOR_DERIVATION,
    verdict_eligible_population_floor,
)
from argus.precision.replay_harness import (
    PRECISION_GATE_THRESHOLD,
    corpus_manifest_module,
    precision_fraction,
)

__all__ = [
    "CONSEQUENCE_BELOW",
    "CONSEQUENCE_MET",
    "CRITERION_OUTCOMES",
    "EXPOSURE_CEILING_DERIVATION",
    "EXPOSURE_SOURCE_PATH",
    "EXPOSURE_SOURCE_SHA",
    "MAX_FALSE_ACCUSATION_EXPOSURE",
    "POPULATION_DERIVATION",
    "POPULATION_ID",
    "POPULATION_SOURCE_ARTIFACTS",
    "PREREGISTERED_BY",
    "PREREGISTRATION_COMMIT_SHA",
    "PREREGISTRATION_DATE",
    "PROTOCOL_CHANGE_LOG_PATH",
    "PROTOCOL_VERSION",
    "REJECTED_EXPOSURE_CEILINGS",
    "STRENGTHENING_ONLY_ASYMMETRY",
    "SUCCESSOR_OUTPUT_PATHS",
    "CriterionAssessment",
    "ProtocolVersionDrift",
    "ResolutionFloors",
    "UnregisteredCriterionOutcome",
    "criterion_outcome_meaning",
    "evaluate",
    "precision_floor",
    "protocol_change_log_head",
    "refuse_protocol_drift",
    "resolution_floors",
]


class UnregisteredCriterionOutcome(ValueError):
    """Raised on an outcome name outside :data:`CRITERION_OUTCOMES` (the ``DF-10-4-E`` rule)."""


class ProtocolVersionDrift(ValueError):
    """Raised when :data:`PROTOCOL_VERSION` and the change-log head disagree.

    A ``ValueError`` subclass (AR10), and the same REFUSAL ``gate_decision`` already performs on
    a committed record: *"the protocol is amended BEFORE a run, never reinterpreted during it --
    a decision folded across an amendment is a re-interpretation of judgements nobody re-made."*
    A pre-registration is the same object one level down, so it refuses the same way.
    """


# ---------------------------------------------------------------------------------------------
# WHO, WHEN. The two fields the whole construction rests on.
# ---------------------------------------------------------------------------------------------

#: AC1.1 -- the date this criterion was fixed. It is a plain ISO date and it is deliberately NOT
#: derived from a clock: a criterion whose date moves when you re-run it is not pre-registered.
PREREGISTRATION_DATE = "2026-08-25"

#: AC1.6 -- the ROLE that fixed it, not a machine account. Protocol section 2 names role holders
#: because an act nobody owns is an act nobody can be held to. The absolute exposure ceiling below
#: is an Engineering Lead act of the same class as the 2026-08-17 rule (XAgent007) and is RAISED
#: for ratification in this story's record; it may afterwards only be strengthened
#: (:data:`STRENGTHENING_ONLY_ASYMMETRY`).
PREREGISTERED_BY = (
    "Engineering Lead (Epic 17 / Story 17.1), recorded by the dev-story workflow. The exposure "
    "ceiling below is RAISED for operator ratification (XAgent007) with its derivation and its "
    "rejected alternatives; it may be LOWERED thereafter and never raised."
)


# ---------------------------------------------------------------------------------------------
# THE POPULATION (AC1.4) -- the five ALREADY-RATIFIED members, and only those.
# ---------------------------------------------------------------------------------------------

#: AC1.4 -- the population, named. The already-ratified members at their pinned shas, and the ONE
#: rule class this criterion is about. NOT a new bench, NOT a sealed candidate, NOT the open
#: partition: admitting any of those takes a protocol section 6 R2 ratification, which is an
#: operator act, spends ``DF-13-5-A``, and is forbidden to this story and to Story 17.4 alike.
POPULATION_ID = (
    "the vacuous_test_heuristic findings recorded for the five ALREADY-RATIFIED repository-corpus "
    "members at their pinned shas in "
    "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-set-13-5.json: "
    "minions, agent-smith, agent-markovich, xagents-webapp, ai-body-runtime"
)

#: AC1.4 -- HOW the population is derived, and the number it comes to, stated so a reader can
#: reproduce it without running a detector. The count re-derives from TWO committed artifacts,
#: which is the point: one artifact is a claim, two that agree is a measurement.
POPULATION_DERIVATION = (
    "Parse adjudication-set-13-5.json and count the findings whose rule_id is "
    "'vacuous_test_heuristic' across all five ratified members: 648 minions + 295 agent-smith + "
    "72 agent-markovich + 17 xagents-webapp + 0 ai-body-runtime = 1032, of 4284 findings "
    "emitted in total. The same 1032 re-derives independently from silent-class-record.json, "
    "which reports population_walked 1032 and population_skipped 0 under protocol V1.3. "
    "ai-body-runtime contributes ZERO findings of this class and is still part of the "
    "population: a member that contributes nothing is a member the ratio was measured over, not "
    "a member quietly dropped from the denominator. NOTHING WAS RUN to derive this -- both "
    "artifacts are committed, and a re-measurement would be a detector run this story is "
    "forbidden."
)

#: AC1.4 -- the two committed artifacts :data:`POPULATION_DERIVATION` re-derives from.
#: Repository-relative, forward-slash, resolved BY THE CALLER (``DF-9-2-A``; the
#: ``gate_seal.DETECTOR_TUNING_PATHS`` treatment).
POPULATION_SOURCE_ARTIFACTS: tuple[str, ...] = (
    "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-set-13-5.json",
    "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/silent-class-record.json",
)


# ---------------------------------------------------------------------------------------------
# THE PROTOCOL VERSION (AC1.2) -- NAMED, never created, and CHECKED rather than asserted.
# ---------------------------------------------------------------------------------------------

#: AC1.2 -- the adjudication protocol in force when this criterion was fixed. It is NAMED here.
#: No V1.4 row is added and no section 5 condition is created: the 2026-08-20 operator decision
#: records that adding a version row re-stamps protocol_version across all 31 committed human
#: judgements, and *"a decision folded across an amendment is a re-interpretation of judgements
#: nobody re-made."* The three 2026-08-20 section 5 amendments (breadth, seal, yield) sit as dated
#: blocks UNDER V1.3 for exactly that reason.
PROTOCOL_VERSION = "V1.3"

#: The document whose change-log head :data:`PROTOCOL_VERSION` must equal. Repository-relative and
#: resolved BY THE CALLER -- this module never opens it (``DF-9-2-A``, AR8).
PROTOCOL_CHANGE_LOG_PATH = (
    "_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md"
)

#: The change-log table's row shape, as one compiled pattern rather than three string literals
#: that can drift. ``| <date> | <version> | <description> | <author> |``.
_CHANGE_LOG_ROW = re.compile(
    r"^\|\s*(?P<date>\d{4}-\d{2}-\d{2})\s*\|\s*(?P<version>V[\w.]*)\s*\|", re.MULTILINE
)


def protocol_change_log_head(markdown: str) -> str:
    """The HEAD version of the protocol's change-log table. PURE -- text in, string out.

    The caller reads :data:`PROTOCOL_CHANGE_LOG_PATH` and passes the bytes it decoded; this
    function never opens anything. That split is what keeps the criterion pure while still making
    the version claim falsifiable: ``TC-ArgusAgent-PRECISION-001-135`` performs the read and
    calls :func:`refuse_protocol_drift` with the answer.

    Head means FIRST row, which is how the table is maintained -- newest version on top, every
    historical row retained and struck rather than erased (architecture section 3.4).

    Raises:
        ProtocolVersionDrift: if the table has no parseable row at all. An unparseable table is
            a REFUSAL, never a silent pass: returning the module's own literal on a failed parse
            is how a check becomes ``f(x) == f(x)``.
    """
    match = _CHANGE_LOG_ROW.search(markdown)
    if match is None:
        raise ProtocolVersionDrift(
            "no parseable change-log row was found in the supplied protocol text. The version "
            "check cannot be performed, and a check that cannot be performed must REFUSE rather "
            "than return the value it was going to compare against -- that would make it "
            "trivially true. Supply the full text of "
            f"{PROTOCOL_CHANGE_LOG_PATH!r}."
        )
    return match.group("version")


def refuse_protocol_drift(markdown: str) -> str:
    """Refuse a criterion whose protocol version is not the change-log head. PURE.

    The shape ``gate_decision`` already uses on a committed record, applied to a criterion: the
    protocol is amended BEFORE the thing that cites it, never after. If this raises, the remedy
    is NEVER to edit :data:`PROTOCOL_VERSION` to match -- a criterion re-stamped to whatever the
    protocol says today was not pre-registered under anything.

    Returns:
        The resolved change-log head, so a caller can record what it saw.

    Raises:
        ProtocolVersionDrift: on a mismatch, or on an unparseable table.
    """
    head = protocol_change_log_head(markdown)
    if head != PROTOCOL_VERSION:
        raise ProtocolVersionDrift(
            f"this criterion was pre-registered under protocol {PROTOCOL_VERSION!r} on "
            f"{PREREGISTRATION_DATE}, while the change-log head of {PROTOCOL_CHANGE_LOG_PATH!r} "
            f"is now {head!r}. A pre-registration folded across an amendment is a criterion "
            f"nobody actually registered. Do NOT edit PROTOCOL_VERSION to agree: record the "
            f"amendment, and decide -- as an operator act -- whether the criterion survives it."
        )
    return head


# ---------------------------------------------------------------------------------------------
# THE FLOORS (AC1.3, AC2.1) -- RESOLVED by calling the code that derives them. NEVER re-typed.
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class ResolutionFloors:
    """The three RESOLUTION floors a population must clear before its ratio means anything.

    They answer AC2's DOWNWARD half -- *a ratio alone is satisfiable by a tiny denominator*. Not
    one of them is authored here: each is the value protocol section 5's own machinery already
    derives, reached by calling it. Their derivation strings are carried alongside so the prose a
    record publishes and the arithmetic the gate runs are one object rather than two statements
    that can disagree (``DF-8-5-C``).
    """

    verdict_eligible_population: int
    contributing_members: int
    sealed_contributing_members: int
    validation_set_floor_n: int
    verdict_eligible_population_derivation: str
    contributing_members_derivation: str
    sealed_contributing_members_derivation: str


def precision_floor() -> Fraction:
    """The criterion's ratio floor: protocol section 5's OWN locked threshold, RESOLVED.

    ``replay_harness.PRECISION_GATE_THRESHOLD``, returned as the exact
    :class:`~fractions.Fraction` object it already is. It is never re-typed as a decimal, never
    reconstructed from a numerator and denominator, and never rendered as ``"80%"``.

    **REJECTED: a story-local, lower "Story 17.4 acceptance threshold."** A second threshold is
    precisely how this project came to have two corpora (``DN-3``), and a threshold set below the
    gate's own is a threshold chosen to be passable. If the successor cannot reach the number the
    gate already requires, that is a result, not a calibration problem.

    PURE (AR8): returns an imported object.
    """
    return PRECISION_GATE_THRESHOLD


def resolution_floors() -> ResolutionFloors:
    """The three resolution floors, RESOLVED against the ONE locked ``N`` floor (``DN-3``).

    ``verdict_eligible_population_floor(precision_floor())`` -- the smallest denominator at which
    ">= 80%" is not silently "100%". ``contributing_member_floor(N)`` -- at least half the members
    that satisfy section 5's own ``N`` floor, rounded up, must actually have contributed a
    finding. ``sealed_member_floor(N)`` -- and that many of them must be members the tool was
    never tuned against. The last two are the SAME derived number reached two ways, deliberately:
    ``sealed_member_floor`` CALLS ``contributing_member_floor``. Story 17.1 resolves all three and
    re-types none.

    ``N`` is reached through ``replay_harness.corpus_manifest_module()`` -- the ONE declared lazy
    edge to the repository-only manifest (``DF-9-2-A``), the same edge ``gate_decision`` uses.
    Reaching ``VALIDATION_SET_FLOOR_N`` directly would be a SECOND path to a number
    ``_manifest.validation_floor_n()`` already answers, and AR7 allows exactly one derivation per
    question. The resolution happens HERE, in a function, and never at module scope: this file is
    imported in environments where ``tests/`` does not exist.
    """
    floor_n = int(corpus_manifest_module().validation_floor_n())
    return ResolutionFloors(
        verdict_eligible_population=verdict_eligible_population_floor(precision_floor()),
        contributing_members=contributing_member_floor(floor_n),
        sealed_contributing_members=sealed_member_floor(floor_n),
        validation_set_floor_n=floor_n,
        verdict_eligible_population_derivation=YIELD_FLOOR_DERIVATION,
        contributing_members_derivation=BREADTH_MEMBER_FLOOR_DERIVATION,
        sealed_contributing_members_derivation=SEALED_MEMBER_FLOOR_DERIVATION,
    )


# ---------------------------------------------------------------------------------------------
# THE EXPOSURE CEILING (AC2.2, AC2.3) -- the one genuinely NEW quantity, and it is DERIVED.
# ---------------------------------------------------------------------------------------------

#: AC2.2 -- an ABSOLUTE INTEGER cap on adjudicated false accusations, evaluated JOINTLY WITH and
#: INDEPENDENTLY OF the ratio. Eighty percent of a thousand findings is two hundred wrong
#: accusations, and a ratio cannot see that. This is the number that can.
#:
#: FROZEN AS A LITERAL, ON PURPOSE, AND THIS IS THE ONE PLACE A LITERAL IS RIGHT (``DN-17-1-4``).
#: Resolving it live from adjudication-record.json was REJECTED because THE RECORD GROWS -- Story
#: 17.4 appends to it -- so a live ceiling would move the moment the number it judges came into
#: view, which is the exact defect this whole story exists to prevent. It is frozen with the
#: pinned blob it came from (:data:`EXPOSURE_SOURCE_SHA`), and
#: ``TC-ArgusAgent-PRECISION-001-136`` RE-DERIVES it from that blob rather than trusting this
#: line.
MAX_FALSE_ACCUSATION_EXPOSURE = 26

#: The artifact the ceiling is derived from. Repository-relative, resolved by the caller.
EXPOSURE_SOURCE_PATH = (
    "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-record.json"
)

#: The FULL 40-character lowercase pin the derivation was read at. A short sha is ambiguous and
#: this is the criterion's central citation. ``git show <sha>:<path>`` reproduces the count.
EXPOSURE_SOURCE_SHA = "6c59115b2aad1e6ab9c7dd3ebba011f7d37376dd"

#: AC2.2 -- the derivation, in this module's own words, beside the number it produces (the
#: ``gate_yield.YIELD_FLOOR_DERIVATION`` / ``gate_seal.SEAL_CITATION_RULE`` house form).
EXPOSURE_CEILING_DERIVATION = (
    "THE SUCCESSOR MAY NOT, OVER THE PINNED POPULATION, PRODUCE MORE ADJUDICATED FALSE "
    "ACCUSATIONS THAN THIS INSTRUMENT'S ENTIRE RECORDED FALSE-ACCUSATION HISTORY. That history "
    "is adjudication-record.json read at its pin: 31 rows, all rule_id 'vacuous_test_ast', "
    "judged by a NAMED HUMAN under protocol V1.3 -- 26 FP, 5 BORDERLINE, and ZERO TP. The "
    "ceiling is that 26. "
    "WHY THIS DERIVATION AND NOT A PREFERENCE. (i) It is MEASURED AND COMMITTED, not invented: "
    "the project put 31 blocking findings in front of a human once and 26 came back false, and "
    "nothing about that is negotiable after the fact. (ii) It REPRODUCES FROM A PINNED BLOB, so "
    "the guard can prove the derivation instead of trusting the literal. (iii) It BITES WITHOUT "
    "BEING A SHUTDOWN: at the largest known candidate reach the ratio binds first, and above "
    "roughly 130 verdict-eligible findings the ceiling becomes the binding constraint -- which "
    "is the band protocol section 5 demands, refusing both 'a condition that cannot fail' and a "
    "floor that 'would make CLEARED unreachable by construction'."
)

#: AC2.5 -- the ceilings that were considered and REJECTED, each with the reason, recorded
#: BESIDE the number so the next author cannot re-propose one as though it were new.
REJECTED_EXPOSURE_CEILINGS: tuple[tuple[str, str], ...] = (
    (
        "floor(yield_floor * (1 - threshold)), which evaluates to 1",
        "At a target population of roughly 125 findings it demands better than 99% precision. "
        "That is a SHUTDOWN, and section 5's own rule-class reasoning refuses a floor that "
        "would make clearing unreachable by construction.",
    ),
    (
        "the verdict-eligible population floor itself",
        "The same failure, less obviously: a handful of permitted false accusations over a "
        "population two orders of magnitude larger is a shutdown wearing a derivation.",
    ),
    (
        "48, from DF-16-7-B's 'what the moat is worth here'",
        "Nearly twice the measured exposure. It could not bite at any reachable population, and "
        "a condition that cannot fail is not a threshold.",
    ),
    (
        "a percentage of the population",
        "That is the ratio again wearing a different hat. AC2 asks for an ABSOLUTE, precisely "
        "because a proportion cannot see unbounded harm behind a good ratio.",
    ),
    (
        "resolved live from adjudication-record.json",
        "THE RECORD GROWS -- Story 17.4 appends to it. A ceiling that moves once the number is "
        "in view is the exact defect this story exists to prevent.",
    ),
)

#: AC2.5 / ``DN-17-1-6`` -- pre-registered WITH the number, because an immutable criterion is one
#: nobody can strengthen and a mutable one is not a criterion.
STRENGTHENING_ONLY_ASYMMETRY = (
    "STRENGTHENING ONLY. The operator may LOWER MAX_FALSE_ACCUSATION_EXPOSURE and may RAISE the "
    "ratio floor, at any time, without reopening this pre-registration. NEITHER MAY MOVE THE "
    "OTHER WAY once PREREGISTRATION_COMMIT_SHA exists. This is the same asymmetry that lets "
    "protocol section 5 be amended by dated addition: an amendment is permitted precisely "
    "because it can only make clearing HARDER. TC-ArgusAgent-PRECISION-001-140 enforces the "
    "direction against the pinned blob, so a loosening is a RED test rather than a diff nobody "
    "reads."
)


# ---------------------------------------------------------------------------------------------
# THE CONSEQUENCE (AC1.5) -- a branch, not a discussion. Both halves.
# ---------------------------------------------------------------------------------------------

#: AC1.5 -- what happens if the criterion is not met, written in the shape of the 2026-08-17 rule
#: so there is nothing left to decide when the number arrives.
CONSEQUENCE_BELOW = (
    "IF, over the pinned population, the successor's measured precision is BELOW the resolved "
    "ratio floor, OR its adjudicated false accusations EXCEED MAX_FALSE_ACCUSATION_EXPOSURE, OR "
    "the population is UNEVALUABLE under any of the three resolution floors -- THEN THE "
    "SUCCESSOR PREDICATE IS NOT PROMOTED TO VERDICT-ELIGIBLE. It ships ADVISORY-ONLY. The "
    "consumed == 0 asymmetry and the conservative default stay exactly as they are; the FR34 "
    "disclosure stands; the externalization gate stays BLOCKED. The next attempt requires A "
    "DIFFERENT PREDICATE -- not a bigger bench, and not a loosened clause. "
    "AND: DF-13-5-A IS NOT SPENT BY THAT OUTCOME AND ITS BRANCH (b) IS NOT DECLARED BY IT. That "
    "entry's pre-registered conditions are zero blocking findings, or precision below 80%, OVER "
    "A SPENT ROUND -- and Story 17.4 spends no round, ratifies no member and fetches no source. "
    "DF-13-5-A stays OPEN and UNSPENT either way."
)

#: AC1.5 -- the CONVERSE, stated because it is the half that gets misread. Written down before
#: the number exists for the same reason as everything else here.
CONSEQUENCE_MET = (
    "MEETING THIS CRITERION PROMOTES NOTHING AND MOVES NO GATE CONDITION. It produces a "
    "recorded, evidenced PROPOSAL to promote, and promotion is an operator act. This criterion "
    "judges the SUCCESSOR PREDICATE; protocol section 5's condition set judges THE GATE, and "
    "they are different questions. Measured at pre-registration time, the intersection of the "
    "SEALED partition and the RATIFIED members is EMPTY -- all five ratified members are "
    "pre-seal -- so section 5's gate-evidence-drawn-from-the-sealed-partition condition reads "
    "FAILED over the very population the successor will be measured on, TODAY, before any "
    "successor exists. Only a protocol section 6 R2 act ratifying sealed members could change "
    "that, and no Epic 17 story may take one. THE GATE THEREFORE CANNOT REACH CLEARED FROM THIS "
    "MEASUREMENT, at any ratio. 'Precision came out at 84%, so the gate clears' is FALSE, and it "
    "is written down here before anyone has a number to say it about. "
    "STATED PRECONDITION FOR THE MEASUREMENT ITSELF: protocol section 4's EXTERNAL ADJUDICATOR "
    "tie-break role is UNFILLED (AI-E16-7). This story adjudicates nothing and does not need it. "
    "Story 17.4 does."
)


# ---------------------------------------------------------------------------------------------
# THE ORDERING SURFACE (AC4.1, AC4.2) -- the two constants Story 17.4 IMPORTS.
# ---------------------------------------------------------------------------------------------

#: AC4.1 -- where a SUCCESSOR predicate's output over a corpus member would land. Declared,
#: non-empty, repository-relative, forward-slash, resolved by the caller.
#:
#: Deliberately SUCCESSOR-SCOPED rather than "anything under validation-corpus/". The artifacts
#: already in that directory are output over the five RATIFIED members and predate this story by
#: weeks; folding them in would make the ordering guard assert something FALSE and invite
#: somebody to "fix" it by loosening the assertion. That is ``-75``'s recorded reasoning, reused
#: rather than re-derived.
SUCCESSOR_OUTPUT_PATHS: tuple[str, ...] = (
    "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/successor",
    "_bmad-output/audit-reports/successor",
)

#: AC4.2 -- the commit that FROZE this criterion, as a full 40-character lowercase hex sha.
#:
#: A COMMIT CANNOT CONTAIN ITS OWN SHA, so this is ``None`` in the commit that lands the criterion
#: and is filled by the immediately following commit -- Story 15.1 hit the same wall and solved it
#: the same way. ``TC-ArgusAgent-PRECISION-001-139`` proves, against the real object database,
#: that no commit reachable from this sha touches any :data:`SUCCESSOR_OUTPUT_PATHS` entry; that
#: is the whole ordering claim, and it is checked rather than promised.
#:
#: ⛔ Story 17.4 IMPORTS this constant and :data:`SUCCESSOR_OUTPUT_PATHS` from here and re-types
#: neither (``DN-16-4-2`` / ``AI-E9-7``). The ancestry guard over LATER commits is 17.4's to
#: write, not this story's.
# Commit A lands this as ``None``; commit B fills it. See DN-17-1-7 and section 2.2 of the
# story record for the three-commit arc that makes that ordering provable.
PREREGISTRATION_COMMIT_SHA: str | None = None


# ---------------------------------------------------------------------------------------------
# THE FOLD (AC1.1, AC2.1, AC2.4) -- resolution floors FIRST, then the ratio and the ceiling.
# ---------------------------------------------------------------------------------------------

#: AC1.1 / AC2.1 -- the CLOSED outcome vocabulary, in ``GATE_OUTCOMES``' shape: a mapping from the
#: outcome to what it MEANS, so a caller cannot render one without the sentence that qualifies it.
#:
#: ``UNEVALUABLE`` is RESOLVED from ``gate_conditions.CONDITION_VERDICTS`` rather than re-typed:
#: :func:`_verdict` looks the name up in the imported vocabulary and raises if it is absent, so
#: this module STOPS IMPORTING if section 5's terminal states are ever changed underneath it. No
#: new terminal state is invented here -- ``CONDITION_VERDICTS`` stays closed at four and
#: ``GATE_OUTCOMES`` closed at three; ``NOT_MET`` is this criterion's own name for its own
#: negative and is never written into a section 5 condition or a gate record.


def _verdict(name: str) -> str:
    """Resolve *name* against the imported section 5 verdict vocabulary. PURE.

    Returns the name, having proved it is a registered member. ``condition_verdict_meaning``
    raises ``UnregisteredConditionVerdict`` on anything else, which is what makes this a
    RESOLUTION rather than a copy of a string that happens to match today.
    """
    condition_verdict_meaning(name)
    return name


_MET = _verdict("MET")
_UNEVALUABLE = _verdict("UNEVALUABLE")
_NOT_MET = "NOT_MET"

CRITERION_OUTCOMES: dict[str, str] = {
    _MET: (
        "MET -- the population cleared every resolution floor, the measured precision is at or "
        "above the resolved ratio floor, AND the adjudicated false accusations are at or below "
        "MAX_FALSE_ACCUSATION_EXPOSURE. This is a PROPOSAL to promote the successor predicate. "
        "It promotes nothing by itself and moves no protocol section 5 condition."
    ),
    _NOT_MET: (
        "NOT MET -- the population WAS evaluable and at least one of the two joint conditions "
        "does not hold. This is a RESULT, not a calibration problem: CONSEQUENCE_BELOW applies "
        "verbatim and the remedy is a different predicate, never a lowered criterion."
    ),
    _UNEVALUABLE: (
        "UNEVALUABLE -- a resolution floor does not hold, or the denominator is empty, so any "
        "ratio reported would rest on nothing. Recorded with the count that failed. NEVER a "
        "pass and NEVER a failure, and never an invitation to argue the floor down: the two "
        "known candidate successors each draw from exactly TWO contributing members against a "
        "floor of three, and this outcome was pre-registered for them before they were measured."
    ),
}


def criterion_outcome_meaning(outcome: str) -> str:
    """The registered meaning of *outcome*. PURE.

    Raises:
        UnregisteredCriterionOutcome: on anything outside :data:`CRITERION_OUTCOMES`. An
            unregistered value RAISES rather than being tolerated (``DF-10-4-E``).
    """
    try:
        return CRITERION_OUTCOMES[outcome]
    except KeyError:
        raise UnregisteredCriterionOutcome(
            f"unregistered criterion outcome {outcome!r}; the closed vocabulary is "
            f"{sorted(CRITERION_OUTCOMES)}. A fifth outcome is not invented at a call site."
        ) from None


@dataclass(frozen=True)
class CriterionAssessment:
    """The outcome AND the counts that produced it -- never the outcome alone.

    A bare verdict is unauditable: ``NOT_MET`` with no counts cannot be told apart from
    ``NOT_MET`` measured over four findings. Counts, never rendered sets (NFR-D2 / AR4);
    ``measured_precision`` is an exact :class:`~fractions.Fraction` or ``None`` when there is no
    denominator, following ``replay_harness.precision_fraction``'s convention that an unmeasured
    population must not inherit a flattering default.
    """

    outcome: str
    reason: str
    verdict_eligible_count: int
    contributing_member_count: int
    sealed_contributing_member_count: int
    true_positive_count: int
    false_accusation_count: int
    adjudicated_count: int
    measured_precision: Fraction | None
    ratio_floor: Fraction
    exposure_ceiling: int
    floors: ResolutionFloors

    def __post_init__(self) -> None:
        criterion_outcome_meaning(self.outcome)


def evaluate(
    *,
    verdict_eligible_count: int,
    contributing_member_count: int,
    sealed_contributing_member_count: int,
    true_positive_count: int,
    false_accusation_count: int,
    floors: ResolutionFloors | None = None,
    ratio_floor: Fraction | None = None,
) -> CriterionAssessment:
    """THE fold: a candidate population in, one registered outcome plus its counts out. PURE.

    **ORDER IS THE PROTOCOL'S, NOT A CONVENIENCE.** The three RESOLUTION floors are evaluated
    BEFORE the ratio -- exactly as ``adjudication.fold_adjudicated_precision`` evaluates
    reproducibility and exhaustiveness before it will report a figure. A ratio computed over a
    population that failed a resolution floor is a number resting on nothing, and it is
    indistinguishable downstream from an honest one.

    Then the denominator: an EMPTY adjudicated population is ``UNEVALUABLE``, never ``MET``.
    ``AI-E11-1`` -- an absence is evidence only over a population proved non-empty -- and the
    measured precedent is ``bc55e36``, where a corpus that emitted nothing reported a cleared
    gate.

    Then the two JOINT conditions, and they are joint rather than nested: the ratio floor AND the
    absolute exposure ceiling, each able to produce ``NOT_MET`` on its own. That is AC2's whole
    point and ``TC-ArgusAgent-PRECISION-001-137`` drives all four corners of it.

    Args:
        verdict_eligible_count: findings the successor would make verdict-eligible over the
            pinned population -- the yield floor's subject.
        contributing_member_count: DISTINCT corpus members contributing at least one such
            finding.
        sealed_contributing_member_count: how many of those are drawn from the SEALED partition.
        true_positive_count: adjudicated TP.
        false_accusation_count: adjudicated FP -- the exposure ceiling's subject.
        floors: resolved floors, injected for a caller that already resolved them; defaults to
            :func:`resolution_floors`.
        ratio_floor: the resolved ratio floor, injected likewise; defaults to
            :func:`precision_floor`.

    Raises:
        ValueError: on a negative count, or on an adjudicated population larger than the
            verdict-eligible one. Refusing a malformed input at construction is correct (NFR-R1's
            stated exception); folding it would produce a confident answer to an impossible
            question.
    """
    counts = {
        "verdict_eligible_count": verdict_eligible_count,
        "contributing_member_count": contributing_member_count,
        "sealed_contributing_member_count": sealed_contributing_member_count,
        "true_positive_count": true_positive_count,
        "false_accusation_count": false_accusation_count,
    }
    negative = sorted(name for name, value in counts.items() if value < 0)
    if negative:
        raise ValueError(
            f"negative count(s) {negative} supplied to evaluate(). A count is a cardinality; a "
            f"negative one is a caller defect, and folding it would return a registered outcome "
            f"for a population that cannot exist."
        )
    adjudicated = true_positive_count + false_accusation_count
    if adjudicated > verdict_eligible_count:
        raise ValueError(
            f"{adjudicated} adjudicated finding(s) were reported over a verdict-eligible "
            f"population of {verdict_eligible_count}. The adjudicated rows are a SUBSET of the "
            f"population the ratio is measured over; a superset means the two were counted over "
            f"different things, which is the DF-8-5-C shape."
        )
    if sealed_contributing_member_count > contributing_member_count:
        raise ValueError(
            f"{sealed_contributing_member_count} sealed contributing member(s) were reported "
            f"among {contributing_member_count} contributing member(s). The sealed contributors "
            f"are a SUBSET of the contributors."
        )

    resolved_floors = resolution_floors() if floors is None else floors
    resolved_ratio = precision_floor() if ratio_floor is None else ratio_floor
    measured = precision_fraction(true_positive_count, false_accusation_count)

    def assess(outcome: str, reason: str) -> CriterionAssessment:
        return CriterionAssessment(
            outcome=outcome,
            reason=reason,
            verdict_eligible_count=verdict_eligible_count,
            contributing_member_count=contributing_member_count,
            sealed_contributing_member_count=sealed_contributing_member_count,
            true_positive_count=true_positive_count,
            false_accusation_count=false_accusation_count,
            adjudicated_count=adjudicated,
            measured_precision=measured,
            ratio_floor=resolved_ratio,
            exposure_ceiling=MAX_FALSE_ACCUSATION_EXPOSURE,
            floors=resolved_floors,
        )

    # ---- (1) RESOLUTION FLOORS, before any ratio is looked at. AC2.1's downward half. ----
    shortfalls = (
        (
            verdict_eligible_count,
            resolved_floors.verdict_eligible_population,
            "verdict-eligible population",
            resolved_floors.verdict_eligible_population_derivation,
        ),
        (
            contributing_member_count,
            resolved_floors.contributing_members,
            "distinct contributing members",
            resolved_floors.contributing_members_derivation,
        ),
        (
            sealed_contributing_member_count,
            resolved_floors.sealed_contributing_members,
            "sealed contributing members",
            resolved_floors.sealed_contributing_members_derivation,
        ),
    )
    for measured_count, floor, subject, derivation in shortfalls:
        if measured_count < floor:
            return assess(
                _UNEVALUABLE,
                f"{subject}: {measured_count}, below the resolved floor of {floor}. The "
                f"criterion is UNEVALUABLE over this population -- a recorded failure to "
                f"evaluate, which is neither a pass nor a fail and is not an invitation to "
                f"argue the floor down. Floor derivation: {derivation}",
            )

    # ---- (2) THE DENOMINATOR. An empty one is UNEVALUABLE, never a flattering 100%. ----
    if measured is None:
        return assess(
            _UNEVALUABLE,
            "the adjudicated population is EMPTY, so there is no denominator and no ratio to "
            "compare against the floor. Exhaustiveness over nothing is the guard that passes "
            "forever (AI-E11-1).",
        )

    # ---- (3) THE TWO JOINT CONDITIONS. Each can produce NOT_MET on its own. AC2.4. ----
    ratio_holds = measured >= resolved_ratio
    exposure_holds = false_accusation_count <= MAX_FALSE_ACCUSATION_EXPOSURE
    if ratio_holds and exposure_holds:
        return assess(
            _MET,
            f"precision {measured} is at or above the resolved floor {resolved_ratio}, and "
            f"{false_accusation_count} adjudicated false accusation(s) are at or below the "
            f"ceiling of {MAX_FALSE_ACCUSATION_EXPOSURE}. This is a PROPOSAL to promote; it "
            f"promotes nothing and moves no section 5 condition.",
        )
    failed = []
    if not ratio_holds:
        failed.append(
            f"precision {measured} is BELOW the resolved floor {resolved_ratio}"
        )
    if not exposure_holds:
        failed.append(
            f"{false_accusation_count} adjudicated false accusation(s) EXCEED the ceiling of "
            f"{MAX_FALSE_ACCUSATION_EXPOSURE}, which is this instrument's entire recorded "
            f"false-accusation history"
        )
    return assess(_NOT_MET, "; ".join(failed) + ". " + CONSEQUENCE_BELOW)
