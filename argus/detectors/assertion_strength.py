"""What each assertion in a test span CONSTRAINS, and the successor predicate ``S1`` — PURE.

Drivers: Epic 17 (*"a test which runs the SUT and tolerates any result is distinguishable
from one that checks it"*), ``successor-vacuity-predicate-specification.md`` §2.1 (``S1``'s
three conjuncts) and §2.2 (its threshold), cross-cutting #6 (advisory by contract; the
conservative default IS the false-accusation moat), AR4/AR8 (pure, deterministic, counts
never rendered sets, no ``float``), AR7/§3.3 (one derivation, never a fork), NFR-R1 (a
resolution failure is a RECORDED condition, never an uncaught raise), NFR-M1.

⛔ THE ONE THING TO KNOW BEFORE CHANGING ANY LINE HERE
------------------------------------------------------
**Only the band-0 boundary carries verdict weight.** ``S1`` corroborates a span only when
EVERY assertion in it grades at the weakest band, so:

======================================  ==========================  =====================
grading a real constraint as…           effect on ``S1``            direction
======================================  ==========================  =====================
``none`` (weakest) when it is not       ``S1`` **ADMITS** the span   ⛔ towards an ACCUSATION
``existence``/``value`` when it is      ``S1`` **REFUSES** the span  under-claiming — SAFE
``none``
======================================  ==========================  =====================

⛔ **THE CONSERVATIVE DEFAULT, IN ONE SENTENCE: WHEN IN DOUBT, NOT THE WEAKEST BAND.** Every
judgement call below resolves that way, and the ``existence`` ↔ ``value`` boundary carries
**no** verdict weight at all — it is a reporting axis, deliberately NOT an exhaustive Python
assertion taxonomy, and widening ``S1`` to admit ``existence`` is a separate future act
requiring its own pre-registration (specification §2.2). ⛔ It is not a tuning knob.

⛔ THE FAIL-CLOSED-TEST TRAP, WHICH IS THE DEFECT THIS MODULE MOST EASILY SHIPS
-------------------------------------------------------------------------------
All **nine** members of ``provenance_scan.RESULT_OBSERVING_CONTEXT_CALLEES`` are members of
the WIDE assertion vocabulary — measured by import — so a fail-closed test::

    def test_rejects_bad_input():
        with pytest.raises(ValueError):
            parse("nonsense")          # the SUT call, and its result IS discarded

**carries an assertion** under the vocabulary this module must read. A grader that scores
that assertion by *"what do this call's arguments reference"* sees ``raises(ValueError)``,
finds no SUT-derived name, grades it at the weakest band — and ``S1`` accuses every
fail-closed test in the corpus. That is the same class ``DN-3`` refused one level down when
it made a SUT call inside such a block CONSUMED by construction.

⚠️ **Fact (b) does NOT protect this module.** ``S1`` deliberately drops ``consumed == 0``,
which is the clause that made ``DN-3``'s verdict bite, so the protection is rebuilt HERE, at
the band level: ⛔ **a result-observing context call is NEVER graded ``none``, and grades at
the STRONGEST band when a SUT call is covered by it — raising IS the observation.** The
covered line set is READ from ``provenance_scan.result_observing_lines``, never re-derived.

⛔ NO RE-PARSE, NO SECOND GRAMMAR CALL (AR8/AC3)
------------------------------------------------
Grading reads the source lines the detector already holds and the Story 1.4 edge set, and
nothing else. There is no ``import ast``, no ``tree_sitter``, no grammar entry point, no
I/O, no clock, no ``uuid4``, no ``random``, no environment read and no module-level path
resolution. The research harness's resolver (``research/investigate-per-call-scoping.py``)
is ``ast``-based and is therefore **NOT** the ancestor of anything here; the ancestor is
``provenance_scan._mock_bound_names``, which answers the identical question for mocks,
name-level, in one forward pass, and which this module's resolver mirrors.

⛔ WHAT THE SIGNAL IS, HONESTLY
-------------------------------
NAME-level structural evidence over an UNRESOLVED edge set (``DF-1-4-A``), not dataflow
(``DF-14-1-A``; real assertion provenance is Story 6.2's). Everything the resolver cannot
read is left UNBOUND, which pushes an assertion AWAY from the weakest band, i.e. away from
an accusation. ⛔ ``S1`` does not claim to be dataflow and must not be described as such.

⛔ ADVISORY, AND NOTHING FLIPS ON IT
------------------------------------
Specification §6.5: *"``S1`` landing in Story 17.3 makes nothing verdict-eligible."*
``VacuousTestDetector._ast_corroborated``'s return expression is unchanged, no finding's
``verdict_eligible`` / ``rule_id`` / ``depth_supported`` moves, nothing computed here
reaches a ``.argus/``-bound output, and this module publishes **no figure for ``S1``'s
reach** — that is Story 17.4's single measurement against a criterion frozen at
``scripts/precision_preregistration.py``'s ``PREREGISTRATION_COMMIT_SHA``.
"""

from __future__ import annotations

import re
from typing import NamedTuple

from argus.detectors.provenance_scan import (
    LogicalStatement,
    _AS_BINDING_RE,
    _ASSIGNMENT_RE,
    _blank_strings,
    _CHAIN_ROOT_RE,
    _IDENT,
    _OBSERVING_CALL_RE,
    _structural_colon,
    assertion_statement_lines,
    candidate_sut_edges,
    logical_statement_starts,
    logical_statements,
    provenance_evidence,
    result_observing_lines,
    sut_call_classification,
)
from argus.detectors.vacuous_vocabulary import (
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
    is_assertion_callee,
)
from argus.index.ast_index import CodeEdge

__all__ = [
    "ASSERTION_STRENGTH_BANDS",
    "AssertionStrengthCounts",
    "S1_SPECIFICATION",
    "UNESTABLISHED",
    "UnregisteredStrength",
    "grade_span_assertions",
    "s1_corroborated",
    "strength_meaning",
    "strength_ordinal",
]

#: ⛔ THE assertion-strength scale: CLOSED, ORDERED, declared exactly once in this
#: repository, ``none`` at ordinal 0. The epic requires at minimum these three bands and
#: this story commits exactly these three (Story 17.3 / ``DN-17-3-7``): a complete Python
#: assertion taxonomy is refused, because the ``existence`` ↔ ``value`` boundary carries no
#: verdict weight and building it would consume the story that has to get band 0 right.
ASSERTION_STRENGTH_BANDS: tuple[str, ...] = ("none", "existence", "value")

#: What each band MEANS, in the words a promotion proposal would have to defend. The house
#: form (``silent_class.idiom_meaning`` / ``gate_seal.partition_meaning``): a vocabulary
#: whose members carry their meaning beside them cannot acquire a member nobody can define.
_STRENGTH_MEANINGS: dict[str, str] = {
    "none": (
        "The assertion does not reference any value derived from the code under test. It "
        "constrains nothing the SUT produced, so a SUT that returned anything at all would "
        "satisfy it. This is the WEAKEST band and the ONLY one S1 admits."
    ),
    "existence": (
        "The assertion constrains only that an SUT-derived value EXISTS, is truthy/falsy, "
        "is None or is not None, or has a type. It rules out a missing or wrongly-shaped "
        "result and nothing more. S1 REFUSES a span carrying one of these."
    ),
    "value": (
        "The assertion constrains WHAT an SUT-derived value IS -- an equality, a membership, "
        "a comparison, a match, or a result-observing context whose block covers a SUT call "
        "(raising IS the observation, DN-3). S1 REFUSES a span carrying one of these."
    ),
}

#: ⛔ NOT A BAND, and deliberately so (``DN-17-3-4``). A recorded CONDITION (``NFR-R1``): the
#: assertion's statement could not be read, its extent could not be resolved, or the scale
#: cannot assign it. It is carried as its own COUNT and ``S1`` REFUSES any span holding one
#: — specification §6.3 already places this inside (c′) (*"a grading the scale cannot assign
#: … the answer is NOT corroborated"*), so it is a condition, not a fourth conjunct and not a
#: re-specification. A fourth band would make the scale's ORDER meaningless (where would
#: *unknown* sit between *none* and *value*?) and would invite a future widening to admit it.
UNESTABLISHED: str = "unestablished"

#: The contract this module implements. ⛔ CITED, never re-argued here (``AC5.4``): a prose
#: copy of a specification's argument inside a module is the ``DF-8-5-C`` / ``AI-E9-7``
#: drift defect. If the code and the document disagree, **the document wins and the code is
#: wrong**, unless the document is falsified by measurement — which is an escalation, never
#: a quiet edit on either side.
S1_SPECIFICATION: str = (
    "successor-vacuity-predicate-specification.md section 2.1 (S1's three conjuncts: "
    "(a) reachability UNCHANGED, (b') discarded_sut_calls >= 1 UNCHANGED, (c') every "
    "assertion at the weakest band, including the empty-assertion span), section 2.2 (the "
    "threshold, pre-refused from widening), section 6.3 (the NFR-R1 refusal), section 6.5 "
    "(advisory until an operator says otherwise) and section 7.3 (mock binding is not an "
    "input to S1)."
)


class UnregisteredStrength(ValueError):
    """An assertion-strength band that is not on the scale.

    The ``DF-10-4-E`` shape already used by ``silent_class.UnregisteredIdiom`` and
    ``gate_seal.UnregisteredPartition``: ⛔ an unregistered member RAISES. It is never
    defaulted and never tolerated, because a vocabulary that silently accepts an unknown
    member is a vocabulary that is not closed.
    """


def strength_ordinal(band: str) -> int:
    """Position of *band* on the scale — ``none`` is 0 and is the weakest.

    Raises :class:`UnregisteredStrength` for anything not on the scale.
    """
    try:
        return ASSERTION_STRENGTH_BANDS.index(band)
    except ValueError:
        raise UnregisteredStrength(
            f"{band!r} is not an assertion-strength band. The scale is closed and ORDERED: "
            f"{list(ASSERTION_STRENGTH_BANDS)!r}. {UNESTABLISHED!r} is a recorded CONDITION, "
            f"not a fourth band (NFR-R1)."
        ) from None


def strength_meaning(band: str) -> str:
    """What *band* means, in the words a promotion proposal would have to defend.

    Raises :class:`UnregisteredStrength` for anything not on the scale.
    """
    strength_ordinal(band)  # the ONE membership decision, reused rather than restated
    return _STRENGTH_MEANINGS[band]


class AssertionStrengthCounts(NamedTuple):
    """How the span's assertions graded — COUNTS ONLY (``NFR-D2`` / ``AR4``).

    One count per band plus the ``unestablished`` count. ⛔ No rendered set, no
    iteration-order-dependent value and no ``float`` — the Story 1.1 serializer rejects
    ``float`` and a rendered set leaks iteration order into anything it reaches.
    """

    none: int = 0
    existence: int = 0
    value: int = 0
    unestablished: int = 0

    @property
    def graded(self) -> int:
        """Assertions the scale COULD assign a band to."""
        return self.none + self.existence + self.value

    @property
    def every_assertion_at_the_weakest_band(self) -> bool:
        """(c′): every assertion graded ``none``, and none of them unestablished.

        ⛔ TRUE for the span with NO assertions at all — the degenerate case the
        specification names explicitly, and what makes ``S1`` a superset of the V2 silent
        band exactly. ⛔ FALSE the moment one assertion could not be graded (§6.3).
        """
        return self.unestablished == 0 and self.existence == 0 and self.value == 0


#: Assertion primitives that constrain only EXISTENCE, truthiness or type. ⛔ A small,
#: STATED, closed list and deliberately not exhaustive (``DN-17-3-7``): this boundary
#: carries NO verdict weight in Epic 17, so a name missing from it grades ``value``, which
#: is the SAFE direction. Never a reason to grade something ``none``.
_EXISTENCE_ONLY_CALLEES: frozenset[str] = frozenset(
    {
        "assertTrue",
        "assertFalse",
        "assertIsNone",
        "assertIsNotNone",
        "assertIsInstance",
        "assertNotIsInstance",
        "isinstance",
    }
)

#: ``assert <chain>`` / ``assert not <chain>`` / ``assert <chain> is [not] None``, with an
#: optional ``, "message"``. Anything richer — an ``==``, an ``in``, a comparison, a call
#: with arguments — is a VALUE constraint. ⛔ ``\A``/``\Z`` and never ``^``/``$`` (the
#: platform-neutrality contract, ``DF-14-2-B``); ``_IDENT`` is Unicode-aware by construction.
_EXISTENCE_ONLY_BARE_ASSERT_RE = re.compile(
    rf"\A\s*assert\s+(?:not\s+)?{_IDENT}(?:\s*\.\s*{_IDENT})*"
    rf"(?:\s+is(?:\s+not)?\s+None)?\s*(?:,.*)?\Z"
)


def _references_any(expression: str, names: frozenset[str]) -> bool:
    """Whether *expression* mentions any of *names* as a CHAIN ROOT.

    String literals are blanked first, so a name occurring inside a message or a regex is
    text and not a reference. Deliberately more generous than
    ``provenance_scan._is_mock_derived``'s leading-chain rule: ``2 * result`` references
    ``result`` here where a leading-chain test would miss it, and being generous about *"is
    this SUT-derived"* pushes AWAY from the weakest band (``DN-17-3-6``).
    """
    return any(root in names for root in _CHAIN_ROOT_RE.findall(_blank_strings(expression)))


def _sut_bound_names(
    statements: tuple[LogicalStatement, ...], sut_lines: frozenset[int]
) -> frozenset[str]:
    """Names bound, transitively, to an SUT-derived value within the span (forward pass, PURE).

    ⛔ **The mirror image of ``provenance_scan._mock_bound_names``, built in its idiom** and
    NOT a port of the research harness's ``ast.walk`` resolver, which the epic's own
    acceptance forbids here (no re-parse, no second grammar call). One pass in source order,
    which is the order Python binds names in, over the ONE statement projection:

    - a statement that CONTAINS a SUT call and binds a name binds that name
      (``result = sut(1, 2)``), including across however many physical lines it was wrapped
      over — the extent comes from the scan, so a wrapped or docstring-spanning statement is
      one unit;
    - a name bound from an expression that references an already-SUT-bound name becomes
      SUT-bound in turn (``doubled = result * 2``) — transitivity, one pass, no fixpoint;
    - ``with sut_ctx() as handle:`` binds ``handle`` the same way.

    ⛔ Everything it cannot read is left UNBOUND, and unbound pushes an assertion away from
    the weakest band — i.e. away from an accusation. That asymmetry is the only reason a
    NAME-level proxy is admissible at all (cross-cutting #6, ``DN-17-3-6``).
    """
    bound: set[str] = set()
    for statement in statements:
        code = statement.code
        stripped = code.strip()
        if not stripped:
            continue
        covers_sut = any(
            line in sut_lines for line in range(statement.start_line, statement.end_line + 1)
        )
        if stripped.startswith("with ") or stripped.startswith("with("):
            header = stripped[len("with") :].lstrip()
            colon = _structural_colon(header)
            if colon >= 0:
                header = header[:colon]
            if covers_sut or _references_any(header, frozenset(bound)):
                bound.update(_AS_BINDING_RE.findall(_blank_strings(header)))
            continue
        assignment = _ASSIGNMENT_RE.match(code)
        if assignment is None:
            continue
        if not (covers_sut or _references_any(assignment.group("value"), frozenset(bound))):
            continue
        for target in assignment.group("targets").split(","):
            name = target.strip()
            if name and "." not in name:
                bound.add(name)
    return frozenset(bound)


def _grade_statement(
    statement: LogicalStatement,
    *,
    sut_bound: frozenset[str],
    sut_lines: frozenset[int],
    observed_lines: frozenset[int],
) -> str:
    """The band of the assertion whose logical statement is *statement*.

    ⛔ Reads only the statement's own comment-free code, the names the forward pass bound,
    the ONE SUT-call classification and the ONE result-observing line set. It re-derives
    none of them (AR7/§3.3, AC2.4).
    """
    code = statement.code
    masked = _blank_strings(code)
    covered = frozenset(range(statement.start_line, statement.end_line + 1))

    # ⛔ THE FAIL-CLOSED RULE (AC2.4, DN-3 one level up): raising IS the observation, so a
    # result-observing context call is NEVER the weakest band. It is the STRONGEST band when
    # a SUT call is covered by an observing context; otherwise it still constrains that
    # something was raised/warned/logged, which is an EXISTENCE constraint at least.
    if _OBSERVING_CALL_RE.search(masked) is not None:
        if (covered | observed_lines) & sut_lines:
            return "value"
        return "existence"

    references_sut = bool(covered & sut_lines) or _references_any(code, sut_bound)
    if not references_sut:
        return "none"
    if _EXISTENCE_ONLY_BARE_ASSERT_RE.match(masked) is not None:
        return "existence"
    leading = _CHAIN_ROOT_RE.findall(masked)
    if any(name in _EXISTENCE_ONLY_CALLEES for name in leading):
        return "existence"
    return "value"


def grade_span_assertions(
    source_lines: list[str], span_edges: list[CodeEdge], start: int, end: int
) -> AssertionStrengthCounts:
    """Grade every assertion of the 1-based inclusive span (PURE, deterministic, AC1–AC3).

    The assertion POPULATION is the **WIDE** vocabulary — a bare ``assert`` plus any callee
    ``is_assertion_callee`` accepts — read through the shipped
    ``provenance_scan.assertion_statement_lines`` rather than a second scan. ⛔ **Never the
    FROZEN corroboration table** (``DN-14-2-1``): an assertion made through a name the frozen
    table never heard of would be INVISIBLE, the span would grade *"all assertions at the
    weakest band"* vacuously, and ``S1`` would accuse a well-asserting test.

    ⛔ **NO MOCK-BINDING INPUT** (specification §7.3, AC5.2). The ONE SUT-call classification
    is asked for its answer with an EMPTY mock-name set, which is both what the specification
    requires and the conservative direction: a call that could be mock-derived OR SUT-derived
    is treated as SUT-derived, which pushes its assertions AWAY from the weakest band
    (``DN-17-3-6``). ``mock_referencing_assertions`` is not read here, and its one decision
    site in ``argus/**`` stays where it is.

    ⛔ **NFR-R1:** a span that cannot be read degrades to ``unestablished`` — a recorded
    condition on which ``S1`` REFUSES — and never to a raise and never to ``none``.
    """
    if start < 1 or start > end or end > len(source_lines):
        return AssertionStrengthCounts(unestablished=1)

    statements = logical_statements(source_lines, start, end)
    observed_lines = result_observing_lines(source_lines, start, end)
    starts = logical_statement_starts(source_lines, start, end)
    extents = {statement.start_line: statement.end_line for statement in statements}
    sites = sut_call_classification(
        source_lines,
        span_edges,
        assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
        mock_callees=_MOCK_CALLEES,
        mock_names=frozenset(),  # ⛔ §7.3: S1 takes NO mock-binding input
        observed_lines=observed_lines,
        statement_starts=starts,
        statement_extents=extents,
    )
    sut_lines = frozenset(site.line for site in sites)
    sut_bound = _sut_bound_names(statements, sut_lines)

    wide = frozenset(edge.callee for edge in span_edges if is_assertion_callee(edge.callee))
    by_start = {statement.start_line: statement for statement in statements}

    counts = {band: 0 for band in ASSERTION_STRENGTH_BANDS}
    unestablished = 0
    for line_no in assertion_statement_lines(source_lines, span_edges, start, end, wide):
        statement = by_start.get(line_no)
        if statement is None:
            statement = next(
                (s for s in statements if s.start_line <= line_no <= s.end_line), None
            )
        if statement is None or statement.unterminated or not statement.code.strip():
            unestablished += 1
            continue
        counts[
            _grade_statement(
                statement,
                sut_bound=sut_bound,
                sut_lines=sut_lines,
                observed_lines=observed_lines,
            )
        ] += 1
    return AssertionStrengthCounts(
        none=counts["none"],
        existence=counts["existence"],
        value=counts["value"],
        unestablished=unestablished,
    )


def s1_corroborated(
    source_lines: list[str], span_edges: list[CodeEdge], start: int, end: int
) -> bool:
    """``S1`` over the span — the predicate :data:`S1_SPECIFICATION` defines, and nothing else.

    Three conjuncts, in the specification's own order:

    1. **(a) REACHABILITY — UNCHANGED.** The shipped fact (a): at least one candidate SUT
       call on the span's edges, read through the **FROZEN** corroboration vocabulary.
    2. **(b′) DISCARD — UNCHANGED.** ``discarded_sut_calls >= 1``, fact (b)'s own arithmetic
       through ``provenance_evidence`` with the same FROZEN table the shipped detector
       passes it. ⛔ ``consumed == 0`` is NOT deleted, weakened, widened or re-scoped
       anywhere: fact (b) keeps its own arithmetic and ``S1`` is computed BESIDE it.
    3. **(c′) NO ASSERTION CONSTRAINS AN SUT-DERIVED VALUE — NEW.** Every assertion at the
       weakest band, INCLUDING the span with no assertions at all, and REFUSED outright when
       any assertion could not be graded (§6.3).

    ⛔ **ADVISORY.** Nothing in Epic 17 reads this to decide verdict-eligibility, a
    ``rule_id`` or a coverage depth (specification §6.5), and this function's value is
    carried as EVIDENCE beside fact (b), never instead of it.

    ⛔ **PUBLIC on purpose** (AC5.6): Story 17.4 must be able to MEASURE the shipped
    predicate without re-deriving it. A private copy buried in the detector would force 17.4
    to fork the predicate, which is the ``AR7`` defect this epic exists to close.
    """
    reaches_sut = (
        len(
            candidate_sut_edges(
                span_edges,
                assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
                mock_callees=_MOCK_CALLEES,
            )
        )
        >= 1
    )
    if not reaches_sut:
        return False
    evidence = provenance_evidence(
        source_lines,
        span_edges,
        start,
        end,
        assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
        mock_callees=_MOCK_CALLEES,
    )
    if evidence.discarded_sut_calls < 1:
        return False
    return grade_span_assertions(
        source_lines, span_edges, start, end
    ).every_assertion_at_the_weakest_band
