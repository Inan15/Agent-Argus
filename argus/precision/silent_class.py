"""Story 16.7 — the SILENT test class, and the record a named human judges it on.

WHY THIS MODULE EXISTS, in one paragraph. The shipped fact-(b) predicate
(``disc >= 1 AND cons == 0 AND mref >= 1``) reaches ZERO of the 1,032
``vacuous_test_heuristic`` findings the ratified corpus recorded, so the externalization
gate is BLOCKED on an empty denominator rather than on a shortfall. Three relaxations were
measured. The one that reaches something is *"the span reaches the SUT, discards the
result, and asserts NOTHING AT ALL"* — the V2 SILENT variant — which reaches **36**. Its
true-positive proportion has never been measured, and the class is known to contain at
least one DELIBERATE SMOKE TEST, where *"does not raise"* IS the assertion and is stated in
a comment no analyser can read. So this module derives and publishes the class, and it
publishes it as a QUESTION FOR A HUMAN. It promotes nothing.

WHAT THIS MODULE IS NOT, because both are one careless import away:

* It is **not a detector and cannot become one.** Nothing under ``argus/detectors/`` and no
  ``argus/precision/gate_*.py`` imports this module; the edge runs one way, and
  ``tests/test_silent_class.py`` asserts that by walking the whole package's import graph.
  A scoring predicate sitting inside the detector package is a shipped promotion waiting
  for someone to wire it up.
* It is **not the gate's adjudication record.** Every one of the 1,032 is
  ``verdict_eligible: false, advisory: true``. Appending these dispositions to
  ``validation-corpus/adjudication-record.json`` was MEASURED to move ``total_tp`` 0 -> 36,
  ``adjudicated_population`` 31 -> 67, ``distinct_rule_class_count`` 1 -> 2 and
  ``independence.status`` NOT_INDEPENDENT -> SECOND_REVIEWER_INTERNAL. Two of those the
  epic forbids outright, and the whole move is wrong on the protocol's own terms besides:
  protocol section 4, ``scripts/build_adjudication_record.py`` and
  ``validation-corpus/blocking-worklist-13-5.md`` each say independently that an advisory
  finding is not a false ACCUSATION and is not in the precision denominator. Hence
  ``DN-16-7-1``: this record lives at its own address and the committed one is
  byte-unchanged.

THE VOCABULARY IS BORROWED, NEVER FORKED (AR7 / section 3.3). ``DISPOSITIONS``,
``HUMAN_DISPOSITIONS``, ``PROTOCOL_ADJUDICATOR_ROLES``, ``LOCATOR_RE``,
``adjudicator_role``, ``disposition_meaning`` and ``finding_row_id`` are IMPORTED from
:mod:`argus.precision.adjudication` and used as the same objects, not re-declared. The
counting, the live-row rule and the exhaustiveness rule are DELEGATED to
:class:`~argus.precision.adjudication.AdjudicationRecord` through
:meth:`SilentClassRecord.as_adjudication_record`, so there is exactly one definition of
each in the repository. What this module adds is the ONE thing the shared schema cannot
carry: ``idiom``, on a NEW row type. It is emphatically NOT a fifth disposition
(``DN-16-7-2``) — a row can be a genuine FP *and* a deliberate smoke test, and that
combination is the measurement this story exists to produce. Widening ``ROW_FIELDS``
instead was measured to make ``load_record()`` on the committed record RAISE outright.

PURE (AR8). No I/O, no clock, no randomness, no network, and NO repository path resolved at
module level — :data:`SILENT_CLASS_RECORD_PATH` and :data:`SILENT_CLASS_WORKLIST_PATH` are
repository-relative forward-slash STRINGS the caller resolves against its own root, the
same treatment ``adjudication.RECORD_PATH`` gets and for the same ``DF-9-2-A`` reason: the
wheel-import guard imports every shipped module out of a real built distribution with this
repository off ``sys.path``. All I/O lives in ``scripts/build_silent_class_record.py``.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from argus.detectors.provenance_scan import (
    ProvenanceEvidence,
    body_statement_count,
    opens_bare_assert,
    provenance_evidence,
)
from argus.detectors.vacuous_vocabulary import (
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
    is_assertion_callee,
)
from argus.index.ast_index import AstIndexEntry, CodeEdge, Definition
from argus.precision.adjudication import (
    ADJUDICATION_UNIT,
    DISPOSITIONS,
    HUMAN_DISPOSITIONS,
    LOCATOR_RE,
    PROTOCOL_ADJUDICATOR_ROLES,
    AdjudicationRecord,
    AdjudicationRow,
    Exhaustive,
    AdjudicationUnevaluable,
    adjudicator_role,
    disposition_meaning,
    expert_hours_report,
    finding_row_id,
)
from argus.precision.gate_independence import IndependenceAssessment, assess_independence

#: The rule class the silent class is drawn from. The population is the recorded findings
#: of THIS rule in ``validation-corpus/adjudication-set-13-5.json`` — 1,032 of them — and
#: not a re-run of the detector over anything.
SILENT_CLASS_RULE_ID = "vacuous_test_heuristic"

#: Where the machine record and the human worklist land, as repository-relative POSIX
#: STRINGS. Deliberately not ``Path`` objects and deliberately not resolved here: see the
#: module docstring's ``DF-9-2-A`` paragraph.
SILENT_CLASS_RECORD_PATH = (
    "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/silent-class-record.json"
)
SILENT_CLASS_WORKLIST_PATH = (
    "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/silent-class-worklist.md"
)

#: The predicate, in the words a promotion proposal would have to defend.
SILENT_CLASS_DEFINITION = (
    "V2 SILENT: the flagged test span reaches the system under test and DISCARDS at least "
    "one result (discarded_sut_calls >= 1, fact (b)'s own arithmetic, frozen table), AND "
    "the span asserts NOTHING AT ALL under the WIDE assertion vocabulary (no bare assert "
    "opens any line of the span, and no callee on any edge of the span is a registered "
    "assertion name). Measured at HEAD over the 1,032 recorded vacuous_test_heuristic "
    "findings: 36 members. NOTE for anyone who later proposes promoting this predicate: "
    "V2 is NOT a relaxation of shipped fact (b). V1 (drop the provably-dead "
    "mock-referencing clause) reaches 6, V3 (V1 AND silent) also reaches 6, so V1 is a "
    "SUBSET of V2 and 30 of the 36 lie outside V1 entirely — 30 members have at least one "
    "CONSUMED SUT call, one of them thirteen, which no clause removal from fact (b) can "
    "ever reach. Promoting V2 would be a genuinely DIFFERENT predicate, not a loosening."
)

#: ``UNADJUDICATED`` — spelled out here so the seeding path can name it without a literal
#: floating in three files. It is the ONLY disposition an automated producer may write
#: (protocol section 2), and the whole reason this story stops where it does.
UNADJUDICATED = "UNADJUDICATED"


class UnregisteredIdiom(ValueError):
    """An ``idiom`` outside :data:`IDIOMS` — never defaulted, never tolerated (DF-10-4-E)."""


#: The CLOSED idiom vocabulary, on an axis ORTHOGONAL to the disposition (``DN-16-7-2``).
#: The disposition answers *"is this a false accusation?"*. The idiom answers *"is the
#: silence deliberate?"*. They are two questions and a row answers both independently: a
#: row may be FP and DELIBERATE_SMOKE_TEST at once, and that combination is precisely the
#: measurement Story 16.7 exists to produce. Checked in BOTH directions by
#: ``tests/test_silent_class.py`` — an unregistered member raises, and a registered member
#: that no case exercises is itself a finding.
IDIOMS: Mapping[str, str] = {
    "DELIBERATE_SMOKE_TEST": (
        "DELIBERATE SMOKE TEST — the named human read the span and judges that NOT RAISING "
        "is the assertion. The test is doing what its author meant it to do; the silence "
        "is the point, and it is typically stated in a comment (the archetype is minions "
        "tests/apaa/test_coverage_ledger.py:239, whose entire assertion is the comment "
        "'# must not raise'). DN-3 already carves out the EXPLICIT spelling of this idiom, "
        "pytest.raises; this is the IMPLICIT one, and its proportion in the class is the "
        "number that decides whether the predicate could ever be promoted."
    ),
    "NOT_A_SMOKE_TEST": (
        "NOT A SMOKE TEST — the named human read the span and judges that the silence is "
        "NOT deliberate: nothing about the test says 'not raising is the assertion'. This "
        "says nothing on its own about TP or FP, which is the disposition's job."
    ),
    "NOT_ASSESSED": (
        "NOT ASSESSED — nobody has looked at the idiom question for this row yet. The ONLY "
        "member an automated producer may write, and the seeded default. It is NOT a "
        "judgement that the row is not a smoke test: it is the absence of one, and it is "
        "EXCLUDED from the smoke-test proportion's denominator rather than counted as a "
        "negative (AI-E11-1 — an unassessed row folded in as a 'no' manufactures a "
        "measurement out of the rows nobody read)."
    ),
}

#: The seeded member, and the one that keeps a row out of the proportion's denominator.
UNASSESSED_IDIOM = "NOT_ASSESSED"

#: The members that represent an actual human assessment of the idiom question.
ASSESSED_IDIOMS: tuple[str, ...] = ("DELIBERATE_SMOKE_TEST", "NOT_A_SMOKE_TEST")

#: The row schema of THIS record. Its own tuple, deliberately: ``ROW_FIELDS`` on the
#: committed record is CLOSED at eleven and was measured to make ``load_record()`` RAISE
#: the moment a twelfth is added (``DN-16-7-2``).
SILENT_CLASS_ROW_FIELDS: tuple[str, ...] = (
    "row_id",
    "member_id",
    "rule_id",
    "verdict_eligible",
    "advisory",
    "locator",
    "test_name",
    "discarded_sut_calls",
    "consumed_sut_calls",
    "pinned_sha",
    "disposition",
    "idiom",
    "adjudicator",
    "adjudicated_on",
    "reason",
    "supersedes",
)


def idiom_meaning(idiom: str) -> str:
    """The registered meaning of *idiom* — RAISES on an unregistered member (DF-10-4-E).

    The raising lookup is the vocabulary's enforcement, exactly as ``disposition_meaning``
    is for ``DISPOSITIONS``: a value that is not in the table has no meaning, and giving it
    one by default is how a closed vocabulary quietly stops being closed.
    """
    try:
        return IDIOMS[idiom]
    except KeyError:
        raise UnregisteredIdiom(
            f"idiom {idiom!r} is not registered. The vocabulary is CLOSED at "
            f"{sorted(IDIOMS)!r} and an unregistered member is refused rather than "
            f"defaulted: the idiom axis exists to make the smoke-test question visible, "
            f"and an unnameable member makes it invisible again."
        ) from None


# ---------------------------------------------------------------------------------------
# The predicate. COMPOSED from shipped components — there is no second AST walk and no
# second line scanner anywhere below, and tests/test_silent_class.py asserts that
# structurally over this module's own source.
# ---------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SpanScore:
    """What the SHIPPED components say about one flagged test span.

    Every field is READ off a shipped helper. Nothing here re-derives anything, and the
    three non-``bool`` fields are carried precisely so a guard can state its non-vacuity
    preamble (``AI-E11-1``) before asserting anything: a case that cannot show
    ``statement_count > 0`` and ``discarded_sut_calls >= 1`` is measuring an empty span.
    """

    #: ``provenance_evidence().discarded_sut_calls`` — fact (b)'s own arithmetic.
    discarded_sut_calls: int
    #: ``provenance_evidence().consumed_sut_calls``.
    consumed_sut_calls: int
    #: ``provenance_evidence().mock_referencing_assertions`` — the clause that is dead over
    #: this corpus (0 of 1,032, ``DF-16-6-A``). Carried so a promotion proposal can see it.
    mock_referencing_assertions: int
    #: ``body_statement_count()`` — the span is non-empty. The non-vacuity observable.
    statement_count: int
    #: Whether the span asserts ANYTHING at all, under the WIDE vocabulary.
    asserts_anything: bool

    @property
    def is_silent_class_member(self) -> bool:
        """The V2 SILENT predicate itself, and it is two conjuncts and no threshold.

        ``disc >= 1`` is fact (a)+(b)'s reach-and-discard evidence; ``not
        asserts_anything`` is the silence. There is deliberately no ``cons == 0`` conjunct:
        that is V1/V3, it reaches 6, and 30 of this class's 36 members would be lost to it.
        """
        return self.discarded_sut_calls >= 1 and not self.asserts_anything


def span_asserts_anything(
    source_lines: Sequence[str],
    span_edges: Sequence[CodeEdge],
    start: int,
    end: int,
) -> bool:
    """Does this span assert ANYTHING AT ALL? — the WIDE vocabulary, and only the wide one.

    ``DN-14-2-1`` IS THE LOAD-BEARING CONSTRAINT HERE, and it points the opposite way from
    the way it points inside the detector. The detector asks *"does this span CORROBORATE
    the SUT result?"* and must ask it through the FROZEN 23-name table, because widening
    that table moves a test TOWARDS an accusation. This module asks a different question —
    *"does this span assert anything at all?"* — and the direction of harm is REVERSED: a
    test that asserts through a name the frozen table has never heard of would be scored
    assertion-free, and would enter a class published for a human to judge as *silent* when
    it is nothing of the kind. That is the false accusation the two-table split exists to
    prevent, arrived at from the other side. So the breadth is wanted here, and the WIDE
    table (89 names plus the naming convention, through the shipped
    :func:`~argus.detectors.vacuous_vocabulary.is_assertion_callee`) is the correct
    vocabulary for this question and the frozen one is not.

    Both spellings the detector already recognises, and read through the SAME two shipped
    helpers it reads them through: a bare ``assert`` statement (which is not a call node,
    so it is read off the source line by
    :func:`~argus.detectors.provenance_scan.opens_bare_assert`) and a call to an assertion
    primitive (read off the index's own edges). There is no third spelling invented here.
    """
    for line_no in range(start, end + 1):
        index = line_no - 1
        if 0 <= index < len(source_lines) and opens_bare_assert(source_lines[index].strip()):
            return True
    return any(is_assertion_callee(edge.callee) for edge in span_edges)


def span_provenance(
    source_lines: Sequence[str],
    span_edges: Sequence[CodeEdge],
    start: int,
    end: int,
) -> ProvenanceEvidence:
    """The discarded/consumed/mock-referencing counts — the SHIPPED scan, unmodified.

    ``assertion_callees`` here is the FROZEN corroboration table, and that is correct and
    is NOT in tension with :func:`span_asserts_anything` above. This call is fact (b)'s OWN
    arithmetic: ``provenance_evidence`` uses the table to decide which statements are
    assertion statements for the purpose of deciding whether a SUT result was CONSUMED, and
    that is the question the frozen table is frozen for. Passing the wide table here would
    fork fact (b)'s arithmetic, which is the ``AR7`` defect. The two questions use the two
    tables, each for the question it was built for, and that is the whole of ``DN-14-2-1``.
    """
    return provenance_evidence(
        list(source_lines),
        list(span_edges),
        start,
        end,
        assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
        mock_callees=_MOCK_CALLEES,
    )


def score_span(
    source_lines: Sequence[str],
    span_edges: Sequence[CodeEdge],
    start: int,
    end: int,
) -> SpanScore:
    """Score ONE flagged test span with the shipped components — the whole predicate.

    Four shipped things are CALLED and nothing is re-implemented:
    :func:`~argus.detectors.provenance_scan.provenance_evidence` for the discard/consume
    counts, :func:`~argus.detectors.provenance_scan.body_statement_count` for the
    non-vacuity observable, :func:`~argus.detectors.provenance_scan.opens_bare_assert` for
    the bare-assert spelling and
    :func:`~argus.detectors.vacuous_vocabulary.is_assertion_callee` for the call spelling.
    """
    evidence = span_provenance(source_lines, span_edges, start, end)
    return SpanScore(
        discarded_sut_calls=evidence.discarded_sut_calls,
        consumed_sut_calls=evidence.consumed_sut_calls,
        mock_referencing_assertions=evidence.mock_referencing_assertions,
        statement_count=body_statement_count(list(source_lines), start, end),
        asserts_anything=span_asserts_anything(source_lines, span_edges, start, end),
    )


def span_edges_of(entry: AstIndexEntry, definition: Definition) -> tuple[CodeEdge, ...]:
    """The index's OWN edges falling inside *definition* — read, never recomputed.

    The index already carries the call edges and their line numbers; selecting the ones
    inside a definition's span is a filter over shipped data, not a second AST walk.
    """
    return tuple(
        edge for edge in entry.edges if definition.start_line <= edge.line <= definition.end_line
    )


def definitions_by_start_line(entry: AstIndexEntry) -> dict[int, Definition]:
    """The index's definitions keyed by their 1-based start line — the locator's own key.

    A ``vacuous_test_heuristic`` locator is ``<path>:<start line of the test function>``,
    so this is the join between a recorded finding and the definition it was raised about.
    The definition also carries ``name``, which is why nothing here needs to re-parse the
    file to learn the test's name.
    """
    return {definition.start_line: definition for definition in entry.definitions}


def locator_for(path: str, start_line: int) -> str:
    """The repository-relative POSIX locator ``<path>:<line>``, and nothing else.

    Built by CONCATENATION from the path the pinned tree reported, which is already POSIX
    because it came out of the object database rather than off a filesystem walk. Neither
    the platform separator constant nor the platform path-join helper is reachable from
    this module at all, and no backslash occurs in any string it holds — a
    Windows-shaped locator in a committed artifact is a Windows-only locator in a
    repository whose CI runs an ubuntu matrix, and ``LOCATOR_RE`` refuses one outright.
    That absence is asserted by a source scan in ``tests/test_silent_class.py``, which is
    also why this sentence names those two helpers by description rather than by spelling.
    """
    return f"{path}:{start_line}"


# ---------------------------------------------------------------------------------------
# The record.
# ---------------------------------------------------------------------------------------


@dataclass(frozen=True)
class SilentClassRow:
    """ONE member of the silent class, and the question a named human must answer about it.

    Validation happens in ``__post_init__`` — at CONSTRUCTION, not at a call site — so
    there is no path that produces an invalid row and no reviewer who has to remember to
    look. In particular an ``UNADJUDICATED`` row carrying an adjudicator RAISES: that is
    the shape a machine would produce if it started filling in the human's judgements
    (``DN-6``), and it is the one thing this record exists to prevent.

    The vocabulary checks are the SAME objects the committed record uses —
    ``disposition_meaning``, ``adjudicator_role`` and ``LOCATOR_RE`` are imported from
    :mod:`argus.precision.adjudication` rather than re-declared, so a row that would be
    illegal there is illegal here for the identical reason and by the identical code.
    """

    row_id: str
    member_id: str
    rule_id: str
    verdict_eligible: bool
    advisory: bool
    locator: str
    test_name: str
    discarded_sut_calls: int
    consumed_sut_calls: int
    pinned_sha: str
    disposition: str
    idiom: str = UNASSESSED_IDIOM
    adjudicator: str | None = None
    adjudicated_on: str | None = None
    reason: str | None = None
    supersedes: str | None = None

    def __post_init__(self) -> None:
        disposition_meaning(self.disposition)  # raises on an unregistered member
        idiom_meaning(self.idiom)  # raises on an unregistered member
        if self.verdict_eligible:
            raise ValueError(
                f"row {self.row_id!r}: verdict_eligible is True. Every member of the "
                f"silent class is an ADVISORY finding — all 1,032 of the population are "
                f"advisory, measured — and this story promotes nothing. A verdict-eligible "
                f"row here would be a promotion smuggled in through the record."
            )
        if not self.advisory:
            raise ValueError(
                f"row {self.row_id!r}: advisory is False. The population is the advisory "
                f"vacuous_test_heuristic findings and nothing else."
            )
        if not self.test_name.strip():
            raise ValueError(
                f"row {self.row_id!r}: test_name is empty. The human judges a NAMED test; "
                f"a locator with no name makes them open the file to learn what they are "
                f"looking at, which is the cost this record exists to remove."
            )
        if self.discarded_sut_calls < 1:
            raise ValueError(
                f"row {self.row_id!r}: discarded_sut_calls is {self.discarded_sut_calls}, "
                f"but the V2 SILENT predicate requires >= 1. A row that does not satisfy "
                f"the predicate is not a member of the class it is published under."
            )
        if self.consumed_sut_calls < 0:
            raise ValueError(f"row {self.row_id!r}: consumed_sut_calls is negative")
        if not LOCATOR_RE.match(self.locator) or ".." in self.locator.split("/"):
            raise ValueError(
                f"row {self.row_id!r}: locator {self.locator!r} is not a "
                f"repository-relative POSIX '<path>:<line>'. An absolute or host path in a "
                f"committed artifact breaches NFR-S1, and a backslash-separated one is a "
                f"Windows-only locator in a repository whose CI runs an ubuntu matrix."
            )
        if not self.pinned_sha.strip():
            raise ValueError(
                f"row {self.row_id!r}: pinned_sha is empty. The locator means nothing "
                f"without the commit it was read at — the member's working tree moves, and "
                f"section 0.7 measured it moving three times in one day."
            )
        if self.disposition in HUMAN_DISPOSITIONS:
            adjudicator_role(self.adjudicator or "")
            if not (self.adjudicated_on or "").strip():
                raise ValueError(
                    f"row {self.row_id!r}: disposition {self.disposition!r} requires an "
                    f"adjudicated_on date."
                )
            if not (self.reason or "").strip():
                raise ValueError(
                    f"row {self.row_id!r}: disposition {self.disposition!r} requires a "
                    f"REASON. A judgement without a reason cannot be re-examined, and "
                    f"protocol section 4's borderline ladder IS a re-examination procedure."
                )
        elif self.adjudicator is not None or self.adjudicated_on is not None:
            raise ValueError(
                f"row {self.row_id!r}: disposition {self.disposition!r} is not a human "
                f"judgement, so it must carry NO adjudicator and NO date; got "
                f"adjudicator={self.adjudicator!r} adjudicated_on={self.adjudicated_on!r}. "
                f"Attributing an unjudged row to a human is the fabrication this record "
                f"exists to make impossible (DN-6)."
            )

    @property
    def finding_id(self) -> str:
        """The PER-FINDING identity — DELEGATED to the committed record's own coordinate.

        ``DN-2a`` / ``DN-MATCH-KEY-REUSE``: the unit is the FINDING, and its identity is
        ``(member_id, rule_id, verdict_eligible, advisory, locator)``. Reused rather than
        respelled so the two records answer *"is this the same finding?"* identically.
        """
        return self.to_adjudication_row().finding_id

    @property
    def is_assessed_idiom(self) -> bool:
        """Whether a human has actually answered the idiom question for this row."""
        return self.idiom in ASSESSED_IDIOMS

    def to_adjudication_row(self) -> AdjudicationRow:
        """PROJECT this row onto the shared row type, dropping the orthogonal ``idiom``.

        This is how the counting, the live-row rule and the exhaustiveness rule get reused
        instead of respelled (``AR7``). It is a projection in memory and it never travels:
        nothing here is ever serialized to, appended to, or compared against
        ``validation-corpus/adjudication-record.json``, whose bytes this story does not
        move (``DN-16-7-1``).
        """
        return AdjudicationRow(
            row_id=self.row_id,
            member_id=self.member_id,
            rule_id=self.rule_id,
            verdict_eligible=self.verdict_eligible,
            advisory=self.advisory,
            locator=self.locator,
            disposition=self.disposition,
            adjudicator=self.adjudicator,
            adjudicated_on=self.adjudicated_on,
            reason=self.reason,
            supersedes=self.supersedes,
        )

    def to_payload(self) -> dict[str, Any]:
        """The canonical mapping — serialized through ``argus.store.canonical`` upstream."""
        return {
            "row_id": self.row_id,
            "member_id": self.member_id,
            "rule_id": self.rule_id,
            "verdict_eligible": self.verdict_eligible,
            "advisory": self.advisory,
            "locator": self.locator,
            "test_name": self.test_name,
            "discarded_sut_calls": self.discarded_sut_calls,
            "consumed_sut_calls": self.consumed_sut_calls,
            "pinned_sha": self.pinned_sha,
            "disposition": self.disposition,
            "idiom": self.idiom,
            "adjudicator": self.adjudicator,
            "adjudicated_on": self.adjudicated_on,
            "reason": self.reason,
            "supersedes": self.supersedes,
        }


def seed_row(
    *,
    member_id: str,
    locator: str,
    test_name: str,
    pinned_sha: str,
    score: SpanScore,
) -> SilentClassRow:
    """The ONLY row constructor a producer may reach, and it can only make one shape.

    It is structurally incapable of writing a ``TP``, an ``FP`` or a ``BORDERLINE``: the
    disposition is the module constant :data:`UNADJUDICATED`, there is no parameter that
    could carry another, and there is no parameter for an adjudicator or a date either. A
    caller that wants a human judgement on this record has to construct
    :class:`SilentClassRow` itself and supply a registered adjudicator, a date and a
    reason — which is exactly the friction protocol section 2 asks for.
    """
    if not score.is_silent_class_member:
        raise ValueError(
            f"{locator}: the span is NOT a member of the silent class "
            f"(discarded_sut_calls={score.discarded_sut_calls}, "
            f"asserts_anything={score.asserts_anything}). Seeding a non-member would "
            f"publish a question about a test that does not raise it."
        )
    return SilentClassRow(
        row_id=finding_row_id(
            member_id=member_id,
            rule_id=SILENT_CLASS_RULE_ID,
            verdict_eligible=False,
            advisory=True,
            locator=locator,
        ),
        member_id=member_id,
        rule_id=SILENT_CLASS_RULE_ID,
        verdict_eligible=False,
        advisory=True,
        locator=locator,
        test_name=test_name,
        discarded_sut_calls=score.discarded_sut_calls,
        consumed_sut_calls=score.consumed_sut_calls,
        pinned_sha=pinned_sha,
        disposition=UNADJUDICATED,
        idiom=UNASSESSED_IDIOM,
    )


@dataclass(frozen=True)
class SmokeTestProportion:
    """The measurement, or the NAMED REASON there is not one yet — never a bare number.

    ``AR4``: an exact :class:`~fractions.Fraction`, never a float. And ``AI-E11-1`` applied
    to a ratio: with nothing assessed, :attr:`proportion` is ``None`` and :attr:`measured`
    is ``False``. Reporting ``0/36`` there would publish a measurement over the rows
    nobody read, which is the exact artifact this story exists to avoid producing.
    """

    assessed: int
    smoke_tests: int
    population: int

    def __post_init__(self) -> None:
        if self.assessed > self.population or self.smoke_tests > self.assessed:
            raise ValueError(
                f"impossible tally: {self.smoke_tests} smoke test(s) of {self.assessed} "
                f"assessed of {self.population} member(s)"
            )

    @property
    def measured(self) -> bool:
        """Whether any human has assessed the idiom question at all."""
        return self.assessed > 0

    @property
    def proportion(self) -> Fraction | None:
        """The exact proportion of ASSESSED rows that are deliberate smoke tests."""
        if not self.measured:
            return None
        return Fraction(self.smoke_tests, self.assessed)

    @property
    def note(self) -> str:
        """The one sentence that renders this, whether or not there is a number."""
        if not self.measured:
            return (
                f"NOT MEASURED — 0 of {self.population} member(s) have had the idiom "
                f"question assessed, so there is no denominator. This is refused rather "
                f"than reported as 0/{self.population}: a proportion over rows nobody read "
                f"is not a measurement (AI-E11-1), and measuring this proportion is the "
                f"whole purpose of Story 16.7."
            )
        fraction = self.proportion
        assert fraction is not None  # noqa: S101 - narrowing; measured is True here
        return (
            f"{self.smoke_tests}/{self.assessed} of the ASSESSED member(s) are deliberate "
            f"smoke tests (exact Fraction {fraction.numerator}/{fraction.denominator}); "
            f"{self.population - self.assessed} of {self.population} member(s) remain "
            f"unassessed and are EXCLUDED from the denominator rather than counted as a "
            f"negative."
        )

    def to_payload(self) -> dict[str, Any]:
        fraction = self.proportion
        return {
            "measured": self.measured,
            "population": self.population,
            "assessed": self.assessed,
            "deliberate_smoke_tests": self.smoke_tests,
            "proportion_numerator": None if fraction is None else fraction.numerator,
            "proportion_denominator": None if fraction is None else fraction.denominator,
            "gates_anything": False,
            "note": self.note,
        }


@dataclass(frozen=True)
class SilentClassRecord:
    """The silent class, its 36 questions, and every derived figure published beside it.

    Nothing on this record gates anything. It is a MEASUREMENT INSTRUMENT: the gate's
    outcome, its seven section-5 conditions, its threshold, its floor and its published
    independence status are all untouched by every field below, and
    ``tests/test_gate_*.py`` staying green is what says so.
    """

    protocol_version: str
    adjudication_unit: str
    class_definition: str
    derivation_source: str
    derivation_method: str
    population_walked: int
    population_skipped: int
    expert_hours: Fraction | None
    expert_hours_note: str
    transcription_note: str
    rows: tuple[SilentClassRow, ...]

    def __post_init__(self) -> None:
        if self.adjudication_unit != ADJUDICATION_UNIT:
            raise ValueError(
                f"adjudication_unit {self.adjudication_unit!r} != {ADJUDICATION_UNIT!r}. "
                f"Protocol section 7 locks the unit to the FINDING; a record adjudicated "
                f"in another unit is not comparable with anything."
            )
        if self.population_skipped:
            raise ValueError(
                f"{self.population_skipped} finding(s) were SKIPPED during the derivation. "
                f"A class derived over a partially-read population is a class whose "
                f"membership nobody can defend, and the missing rows look exactly like "
                f"non-members (AI-E11-1)."
            )
        if not self.rows:
            raise ValueError(
                "the silent class is EMPTY. An empty class satisfies every 'nothing was "
                "promoted' guard forever and would publish a worklist with no questions on "
                "it, so it is refused rather than written (AI-E11-1)."
            )
        if self.population_walked < len(self.rows):
            raise ValueError(
                f"the derivation walked {self.population_walked} finding(s) but produced "
                f"{len(self.rows)} class member(s); a class cannot be larger than the "
                f"population it was drawn from."
            )
        # Delegated: duplicate row_ids, supersede integrity and the disposition vocabulary
        # are the committed record's rules, and they are enforced by ITS constructor rather
        # than re-stated here (AR7).
        self.as_adjudication_record()

    def as_adjudication_record(self) -> AdjudicationRecord:
        """This record's rows PROJECTED onto the shared container — in memory, never written.

        The single place the shared arithmetic is borrowed from. It exists so that
        :meth:`counts`, :meth:`live_rows` and :meth:`exhaustiveness` are the committed
        record's definitions rather than second copies of them. The header fields it needs
        are filled with this record's own provenance, and the result is never serialized —
        ``AdjudicationRecord.to_payload()`` hardcodes Story 13.2 as its subject, so an
        artifact rendered through it would publish a false subject (the ``DF-9-2-B`` class),
        which is one of the reasons ``DN-16-7-1`` gave this story its own row type.
        """
        return AdjudicationRecord(
            protocol_version=self.protocol_version,
            adjudication_unit=self.adjudication_unit,
            corpus_source=self.derivation_source,
            reproducibility_verified=True,
            reproducibility_source=self.derivation_method,
            expert_hours=self.expert_hours,
            expert_hours_note=self.expert_hours_note,
            rows=tuple(row.to_adjudication_row() for row in self.rows),
        )

    def live_rows(self) -> tuple[SilentClassRow, ...]:
        """The CURRENT judgement per finding — superseded rows excluded, never removed."""
        superseded = self.as_adjudication_record().superseded_row_ids
        return tuple(row for row in self.rows if row.row_id not in superseded)

    def counts(self) -> dict[str, int]:
        """Live row counts per registered DISPOSITION — the committed record's own tally."""
        return self.as_adjudication_record().counts()

    def idiom_counts(self) -> dict[str, int]:
        """Live row counts per registered IDIOM — every member present, even at zero."""
        tally = {name: 0 for name in IDIOMS}
        for row in self.live_rows():
            tally[row.idiom] += 1
        return tally

    def exhaustiveness(self) -> Exhaustive | AdjudicationUnevaluable:
        """Protocol section 4 exhaustiveness over THIS class — the shared definition.

        A ``BORDERLINE`` or an ``UNADJUDICATED`` row is a RESIDUAL and makes the run
        Unevaluable with the residual count, exactly as it does for the committed record.
        Seeded, this returns Unevaluable with 36 residuals, and that is the honest reading:
        nothing has been judged yet.
        """
        record = self.as_adjudication_record()
        return record.exhaustiveness([row.finding_id for row in self.rows])

    def adjudicator_ids(self) -> tuple[str, ...]:
        """The distinct ``'<who> (<role>)'`` ids that authored a LIVE judgement here."""
        return tuple(sorted({row.adjudicator for row in self.live_rows() if row.adjudicator}))

    def independence(self) -> IndependenceAssessment:
        """Independence for THIS population — DERIVED through the EXISTING assessor.

        ``assess_independence`` is CALLED, not copied and not wrapped-and-modified, over
        the ids that actually authored live rows here. This EXTENDS FR34's existing
        disclosure mechanism rather than forking a second one, and it GATES NOTHING: it
        claims no independence, fills no role, and is emphatically NOT written to
        ``gate-decision-record.json``, whose ``independence`` block is a claim about the
        GATE'S adjudication and stays ``NOT_INDEPENDENT``. With zero live human rows this
        returns ``NOT_ESTABLISHED``, which is the honest output and not a failure.
        """
        return assess_independence(self.adjudicator_ids())

    def smoke_test_proportion(self) -> SmokeTestProportion:
        """The smoke-test proportion over the ASSESSED rows — or the reason there is none."""
        live = self.live_rows()
        assessed = tuple(row for row in live if row.is_assessed_idiom)
        return SmokeTestProportion(
            assessed=len(assessed),
            smoke_tests=sum(1 for row in assessed if row.idiom == "DELIBERATE_SMOKE_TEST"),
            population=len(live),
        )

    def expert_hours_sentence(self) -> str:
        """Protocol section 3's <= 4 expert-hour budget — through the EXISTING reporter.

        ``expert_hours_report`` is a REPORT and nothing branches on it. ``None`` reads as
        NOT RECORDED and never as zero, and an overrun is reported rather than failed:
        trimming an adjudication to fit an estimate is how the estimate stops measuring the
        adjudication.
        """
        return expert_hours_report(self.expert_hours)

    def members_by_id(self) -> dict[str, int]:
        """Live class members per corpus member id — sorted, deterministic (NFR-P1)."""
        tally: dict[str, int] = {}
        for row in self.live_rows():
            tally[row.member_id] = tally.get(row.member_id, 0) + 1
        return dict(sorted(tally.items()))

    def files_by_member_id(self) -> dict[str, int]:
        """Distinct source files per corpus member id — sorted, deterministic (NFR-P1)."""
        seen: dict[str, set[str]] = {}
        for row in self.live_rows():
            seen.setdefault(row.member_id, set()).add(row.locator.rpartition(":")[0])
        return {member: len(paths) for member, paths in sorted(seen.items())}

    def to_payload(self) -> dict[str, Any]:
        """The canonical mapping — serialized through ``argus.store.canonical`` upstream.

        Note what is NOT here: no source byte from any corpus member (NFR-S1), no absolute
        host path, and no per-row comment flag. The source spans live in the Markdown
        worklist under AC8.6's stated carve-out and nowhere else, and the comment tally is
        published as an aggregate in the worklist's header as triage colour, never per row
        — ``DN-16-7-5`` forbids a fact about punctuation from seeding, defaulting or
        ordering a judgement.
        """
        exhaustive = self.exhaustiveness()
        return {
            "schema_version": 1,
            "story": "16-7-adjudicate-the-silent-test-class-before-proposing-promotion",
            "protocol_version": self.protocol_version,
            "adjudication_unit": self.adjudication_unit,
            "rule_id": SILENT_CLASS_RULE_ID,
            "class_definition": self.class_definition,
            "derivation_source": self.derivation_source,
            "derivation_method": self.derivation_method,
            "population_walked": self.population_walked,
            "population_skipped": self.population_skipped,
            "class_size": len(self.live_rows()),
            "class_by_corpus_member": self.members_by_id(),
            "files_by_corpus_member": self.files_by_member_id(),
            "promotes_nothing": True,
            "gates_anything": False,
            "disposition_vocabulary": dict(DISPOSITIONS),
            "idiom_vocabulary": dict(IDIOMS),
            "idiom_is_not_a_disposition": (
                "The idiom axis is ORTHOGONAL to the disposition (DN-16-7-2). A row may be "
                "FP and DELIBERATE_SMOKE_TEST at once, and that combination is the "
                "measurement. DISPOSITIONS is CLOSED at four members and this record does "
                "not widen it."
            ),
            "registered_adjudicator_roles": list(PROTOCOL_ADJUDICATOR_ROLES),
            "counts": self.counts(),
            "idiom_counts": self.idiom_counts(),
            "exhaustiveness": exhaustiveness_payload(exhaustive),
            "independence": self.independence().to_payload(),
            "smoke_test_proportion": self.smoke_test_proportion().to_payload(),
            "expert_hours_numerator": (
                None if self.expert_hours is None else self.expert_hours.numerator
            ),
            "expert_hours_denominator": (
                None if self.expert_hours is None else self.expert_hours.denominator
            ),
            "expert_hours_note": self.expert_hours_note,
            "expert_hours_report": self.expert_hours_sentence(),
            "transcription_note": self.transcription_note,
            "rows": [row.to_payload() for row in self.rows],
        }


def exhaustiveness_payload(result: Exhaustive | AdjudicationUnevaluable) -> dict[str, Any]:
    """Render the SHARED exhaustiveness result for an artifact — its own sentence, reused.

    ``Exhaustive`` and ``AdjudicationUnevaluable`` are two TYPES rather than a flag,
    precisely so that no call site can treat one as falsy by forgetting to look, and both
    already render themselves. This adds the machine-readable keys an artifact needs and
    takes the sentence from the object's own ``__str__`` rather than writing a second one
    (``AR7``): a consumer reads the status off a key and never has to parse prose.
    """
    if isinstance(result, Exhaustive):
        residual = 0
    else:
        residual = result.residual_count
    return {
        "exhaustive": isinstance(result, Exhaustive),
        "adjudicated_count": result.adjudicated_count,
        "residual_count": residual,
        "gates_anything": False,
        "note": str(result),
    }


def rows_from_payload(payload: Mapping[str, Any]) -> tuple[SilentClassRow, ...]:
    """Re-hydrate rows from a previously written record — the APPEND-ONLY read path.

    Every row goes back through :class:`SilentClassRow`'s constructor, so a hand-edited
    artifact carrying an unregistered disposition, an unregistered idiom, an unregistered
    adjudicator role or a human judgement with no reason is refused on READ as well as on
    write. The schema is checked in both directions: an unknown field and a missing field
    are both a violation, because a silently-dropped field is how a human's judgement
    disappears between two runs of a builder.
    """
    rows: list[SilentClassRow] = []
    for raw in payload.get("rows", ()):
        unknown = sorted(set(raw) - set(SILENT_CLASS_ROW_FIELDS))
        missing = sorted(set(SILENT_CLASS_ROW_FIELDS) - set(raw))
        if unknown or missing:
            raise ValueError(
                f"silent-class row schema violation: unknown={unknown!r} "
                f"missing={missing!r}; the closed schema is {SILENT_CLASS_ROW_FIELDS!r}"
            )
        rows.append(SilentClassRow(**raw))
    return tuple(rows)


def record_from_payload(payload: Mapping[str, Any]) -> SilentClassRecord:
    """The exact INVERSE of :meth:`SilentClassRecord.to_payload` — the currency check's half.

    Only the PROVENANCE fields are read back: the protocol version, the class definition,
    the derivation's source and method, the walked/skipped counts, the hours and the two
    notes. Every DERIVED field on the artifact — the counts, the idiom counts, the class
    split by corpus member, the file spread, the exhaustiveness result, the independence
    assessment and the smoke-test proportion — is deliberately NOT read back and is
    RECOMPUTED from the rows. That asymmetry is the point: re-serializing the result and
    comparing it to the committed bytes is what catches a hand-edited derived figure, which
    is the way a record starts telling a story its own rows do not support.

    ``expert_hours`` round-trips as an exact numerator/denominator pair rather than a float
    (``AR4``), and ``None`` round-trips as ``None`` rather than as zero.
    """
    numerator = payload.get("expert_hours_numerator")
    denominator = payload.get("expert_hours_denominator")
    hours = None if numerator is None or denominator is None else Fraction(numerator, denominator)
    return SilentClassRecord(
        protocol_version=payload["protocol_version"],
        adjudication_unit=payload["adjudication_unit"],
        class_definition=payload["class_definition"],
        derivation_source=payload["derivation_source"],
        derivation_method=payload["derivation_method"],
        population_walked=payload["population_walked"],
        population_skipped=payload["population_skipped"],
        expert_hours=hours,
        expert_hours_note=payload["expert_hours_note"],
        transcription_note=payload["transcription_note"],
        rows=rows_from_payload(payload),
    )


def carry_forward(
    seeded: Iterable[SilentClassRow], existing: Iterable[SilentClassRow]
) -> tuple[SilentClassRow, ...]:
    """APPEND-ONLY over human judgements: an existing row WINS over a freshly seeded one.

    Re-running the builder after an adjudication is a no-op over every row a human has
    touched. A judged row is carried through unchanged — disposition, idiom, adjudicator,
    date and reason — and only findings with no row at all are seeded. This is
    ``scripts/build_adjudication_record.py``'s rule, applied to this record for the same
    reason: a producer that can overwrite a judgement can erase one.
    """
    by_finding = {row.finding_id: row for row in existing}
    return tuple(by_finding.get(row.finding_id, row) for row in seeded)
