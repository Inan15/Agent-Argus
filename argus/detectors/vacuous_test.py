"""Heuristic vacuous-test detector + Tier-A vacuous-path AST subset (PURE).

Drivers: ArgusAgent-FR-10 (heuristic vacuous-test detector — advisory, carrying its
evidence counts), ArgusAgent-FR-7-subset (the Tier-A vacuous-path AST subset:
test→SUT reachability + assertion-target provenance, test files only — the
carved-into-Tier-A half of FR7; full multi-construct grounding is Story 6.2),
ArgusAgent-FR-13 (locator-required findings, via the Story 1.5 ``base`` builder),
ArgusAgent-FR-33-support / cross-cutting #6 (advisory-by-contract: a heuristic-only
finding can NEVER move the verdict to 🔴 — only an AST-corroborated finding is
verdict-eligible; the false-accusation moat), ArgusAgent-NFR-D2 (deterministic,
zero-LLM-token scorer over recorded inputs), ArgusAgent-NFR-R1 (parse/analysis failure
degrades to a recorded condition, never an uncaught raise), AR4 (ratios stored
fixed-precision ``Fraction``, NEVER ``float``; no clock/uuid/random/iteration-order
in any ``.argus/``-bound output), AR8 (the scorer is PURE — the only impure
boundary, the optional ``.argus/findings/`` write, lives in Story 1.7's pipeline),
AR10 (typed/recorded failure — no bare ``except: pass``, no ``print()``).

Locked contract decisions (frozen for downstream consumers — 1.6 / Epic-6)
--------------------------------------------------------------------------
- **Test-file identification (V1).** A file is a test file iff its repo-relative
  POSIX path is under a ``tests/`` segment OR its basename matches ``test_*.py``
  / ``*_test.py``. The detector runs on test files ONLY; a non-test file is
  skipped cleanly (NOT mis-flagged) — AC7.
- **Test-function identification (V1).** A ``Definition`` of kind ``function``
  whose name starts with ``test`` (``test_*`` functions / ``Test*``-class
  ``test_*`` methods). Class definitions themselves are not scored.
- **Assertion sites** — call edges whose callee is a known assertion primitive
  (the ``unittest`` family, ``unittest.mock``'s ``assert_called*`` methods and
  pytest's ``raises``/``warns``/``deprecated_call``) **or matches the
  project-helper naming convention** (``assert*``/``_assert*``), PLUS bare
  ``assert`` statements counted from the source text within the function span
  (tree-sitter ``assert_statement`` is not a ``call`` node, so the index edge set
  does not carry it — we count it from the source lines, deterministically).
- **Mock construction sites** — call edges whose callee is a known mock primitive
  (``Mock``/``MagicMock``/``patch``/``AsyncMock``/``create_autospec``/…).
- **assertion-density = assertion_sites / test_body_LOGICAL_statements** — a
  statement wrapped over several lines counts once, a ``;``-compound counts once
  per simple statement, and a docstring counts once rather than once per line of
  prose. Stored as an exact ``Fraction``. Denominator 0 (no statements) → density
  is ``Fraction(0)`` and the file degrades (un-analyzable), never flagged.
- **mock-ratio = mock_sites / call_sites** (all call edges in the function span),
  stored as an exact ``Fraction``; call_sites 0 → ratio ``Fraction(0)``.
- **Thresholds (heuristic, documented as such).** FLAG when
  ``assertion_density < 1/4`` OR ``mock_ratio > 1/2``. These are heuristic — they
  false-positive on table-driven / snapshot / parametrized tests; that is the
  KNOWN cost, and the AST subset (below) is the corroboration that protects the
  moat (a heuristic flag alone is advisory-only).
- **rule_id vocabulary.** ``"vacuous_test_heuristic"`` (advisory-only, NOT
  verdict-eligible) vs ``"vacuous_test_ast"`` (AST-corroborated, verdict-eligible).
- **Verdict-eligibility surface (read by Story 1.6).** A heuristic-only finding is
  ``advisory=True`` + ``depth_supported=None`` (no depth the verdict folds) →
  the 1.6 gate MUST NOT 🔴 on it. An AST-corroborated finding is ``advisory=True``
  (the demo line stays ``🔴 tests *appear* vacuous``) but ``depth_supported=
  AUDITED_SHALLOW`` AND ``rule_id="vacuous_test_ast"`` → the 1.6 gate MAY treat it
  as verdict-eligible. The architecture's FULL contract is "AST corroboration AND
  Prosecutor sign-off"; the Prosecutor half is Epic-6 — in V1/Epic-1 the
  AST-corroborated finding is the strongest the detector emits and the Story-1.7
  cartridge 🔴 rests on it.

The Tier-A AST subset — what it can and cannot prove (honest scope)
-------------------------------------------------------------------
The Story 1.4 index gives an UNRESOLVED edge set: ``CodeEdge(callee, line)`` is
the bare callee identifier / trailing attribute name with NO scope binding (the
locked 1.4 limitation DF-1-4-A, target ``epic-6-orphan-dead-code-detector``). The
subset therefore works on NAME-level structural facts, not a resolved call graph:

- **Reachability (fact a)** — a ``CodeEdge`` inside the flagged test's span whose
  callee is NOT an assertion primitive and NOT a mock constructor is a candidate
  SUT call. Conservative: a SUT reached only via an aliased / dynamically
  dispatched name is MISSED (a false negative — we under-claim corroboration
  rather than over-accuse).
- **Vacuity signal (fact b)** — "the asserted values do NOT derive from the SUT
  output". The V1 name-level signal is a statement about **provenance SHAPE**: the
  SUT is called and its result is **thrown away**, while what the assertions
  constrain is a value bound from a **mock**. Because there is no dataflow, when
  this cannot be established the finding stays heuristic-only/advisory — it does
  NOT fabricate corroboration. See "Why fact (b) is not ``mock_sites >= 1``" below.
- **The conservative default is the moat.** When the unresolved edge set is
  insufficient, the finding does NOT gain verdict-eligibility. A false 🔴 is the
  lethal failure; a real vacuous test left advisory is tolerable. Full
  dataflow/scope-resolved grounding is Story 6.2.

Why fact (b) is not ``mock_sites >= 1`` (Story 14.1 — a CONFORMANCE fix)
------------------------------------------------------------------------
Fact (b) used to read ``assertion_sites >= 1 and mock_sites >= 1``. That is
*"the test constructs a mock"*, not *"the asserted values do not derive from the
SUT output"* — and the difference was measured, not argued. Over the ratified
5-repository validation corpus this rule class emitted 31 blocking findings and
the named human adjudicated **0** of them true (26 FP / 5 BORDERLINE); across the
heuristically-flagged tests of the two contributing members ``ast_corroborated``
agreed with the bare ``mock_sites >= 1`` term in **2,527 of 2,529** cases
(re-measured 2026-08-17 at the pinned shas). A corroboration step that agrees with
one of its own inputs 99.9% of the time adds no evidence the heuristic did not
already have; it re-reads one input and calls the agreement confirmation. Cross-
cutting concern #6 has required real corroboration since the architecture was
written, so this is a conformance repair, not a new policy.

The replacement is a **provenance-shape** predicate over the same PURE inputs
(the source lines already passed in + the unresolved 1.4 edge set):

1. **Mock-bound names.** A name assigned from a mock primitive, or from a call
   whose receiver chain is rooted at an already-mock-bound name, is mock-bound
   (``fake = Mock()`` → ``fake``; ``pretended = fake.calculate()`` → ``pretended``).
   ``with patch(...) as m`` binds ``m`` the same way.
2. **SUT calls, for fact (b).** A span edge that is not an assertion primitive, not
   a mock primitive, not a result-observing context manager, and whose receiver
   chain is NOT rooted at a mock-bound name.
3. **Discarded vs CONSUMED.** A SUT call is DISCARDED only when the whole LOGICAL
   STATEMENT containing it is that call and nothing else. Anything else — bound to
   a name, nested in another expression, asserted on, compared, chained — is
   CONSUMED, and so is a call that cannot be located in the source text at all
   (unresolvable is not evidence). A SUT call inside a ``pytest.raises`` /
   ``assertRaises`` / ``pytest.warns`` block is CONSUMED **by construction**:
   raising IS the observation (DN-3), and treating those as vacuous would re-create
   the false-accusation class on every fail-closed test.
4. **Fact (b) holds** iff at least one SUT call is discarded, **no** SUT call is
   consumed, and at least one assertion references a mock-bound name.

Requirement 3's "no consumed SUT call" is what makes fact (b) independent of the
heuristic's own inputs, and it is deliberately asymmetric: a test that constrains
the real SUT result — however many mocks it builds, however weak the constraint —
can never be corroborated, so it can never take a build to 🔴 on this rule.

**"Logical statement", not "physical line", is load-bearing** (review iteration 2,
2026-08-17). Both of Python's continuation syntaxes put an assignment target on an
EARLIER line than the call it binds — ``result = (\\n    add(1, 2)\\n)`` (PEP 8's
preferred wrapping) and ``result = \\\\\\n    add(1, 2)`` — so judging the call from
its own physical line scored a test that genuinely constrains the SUT result as
"result thrown away" and promoted it to verdict-eligible. Both were reproduced end
to end on the default zero-token path before the fix and are pinned by
``TC-ArgusAgent-DETECT-001-109`` / ``-110`` and ``TC-ArgusAgent-VERDICT-001-116``.

The signal stays NAME-LEVEL and is a proxy, not dataflow (``DF-14-1-A``; real
assertion provenance is Story 6.2's). It reads the source text and the 1.4 index
and nothing else, so the scorer stays PURE (AR8), and it depends on **no count and
no threshold** — in particular not on ``assertion_sites``.

Why there are TWO assertion vocabularies (Story 14.2 — DN-14-2-1 / DN-14-2-4)
-----------------------------------------------------------------------------
Story 14.1 left the callee tables here and passed them into the scan, and recorded
that this made fact (b) independent of the table Story 14.2 widens. **It did not**,
and the gap was reproduced end to end rather than argued: the scan reads the table
in two places, and widening it turned an ordinary mock-interaction test — SUT result
discarded, sole assertion ``fake.calculate.assert_called_once_with()`` — from
``density=0, corroborated=False`` into ``density=1/5, corroborated=True``. Still
below the 1/4 floor, so still flagged, and now VERDICT-ELIGIBLE: a false 🔴
manufactured by the fix for the assertion table. DN-4 guarantees fact (b) does not
depend on the assertion **COUNT**; it never guaranteed independence from the
assertion **TABLE**.

So the two questions get two vocabularies. The DENSITY numerator reads
``_ASSERTION_CALLEES`` + the naming convention and wants BREADTH; facts (a) and (b)
read ``_CORROBORATION_ASSERTION_CALLEES``, FROZEN at 14.1's 23 names, and want
STABILITY. Neither is derived from the other. That is what lets Story 14.3 widen the
vocabulary across four languages without re-opening the moat, and it is what makes
14.1's promise structural instead of merely written.

The line-oriented scan that answers fact (b) lives in
``argus/detectors/provenance_scan.py`` — a separate concern from scoring, split out
for cohesion and for NFR-M1 headroom (see that module's docstring). It also owns the
ONE statement scan both the denominator and fact (b) read (AR7/§3.3).
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Iterable, Protocol, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from argus.detectors.base import (
    DegradedCondition,
    DetectorResult,
    FindingDraft,
    build_recording,
)
from argus.detectors.provenance_scan import (
    body_statement_count,
    opens_bare_assert,
    provenance_evidence,
)
from argus.index.ast_index import AstIndexEntry, CodeEdge, Definition
from argus.ledger.coverage_ledger import CoverageDepth, grade_entry

__all__ = [
    "RULE_HEURISTIC",
    "RULE_AST",
    "ASSERTION_DENSITY_FLOOR",
    "MOCK_RATIO_CEILING",
    "VacuousTestScore",
    "VacuousTestDetector",
    "is_assertion_callee",
    "is_test_file",
    "is_test_classification_content_dependent",
]

RULE_HEURISTIC = "vacuous_test_heuristic"
RULE_AST = "vacuous_test_ast"

# Heuristic thresholds (documented heuristics — see module docstring).
ASSERTION_DENSITY_FLOOR = Fraction(1, 4)
MOCK_RATIO_CEILING = Fraction(1, 2)

# ─────────────────────────────────────────────────────────────────────────────────────────
# TWO assertion vocabularies, because there are TWO QUESTIONS (Story 14.2 / DN-14-2-4).
#
# They are NOT two spellings of one table and neither is derived from the other — that is the
# whole point, and deriving either (``frozen = widened - delta``) would re-couple them the
# moment Story 14.3 lands. Read them as:
#
#   `_ASSERTION_CALLEES`                 asks "does this test ASSERT ANYTHING?" and wants
#   (the density NUMERATOR)              BREADTH. Missing a name here invents a low density
#                                        and accuses a real test. Widening it can only RAISE
#                                        `assertion_sites`, and the floor fires from BELOW, so
#                                        this half is strictly flag-REDUCING (AC7.4).
#
#   `_CORROBORATION_ASSERTION_CALLEES`   asks "which call edges are NOT SUT calls?" and wants
#   (facts (a) and (b) — the moat)       STABILITY. It is FROZEN. See its own comment.
# ─────────────────────────────────────────────────────────────────────────────────────────

# Known assertion primitives — the DENSITY NUMERATOR's vocabulary. FLAT and
# LANGUAGE-AGNOSTIC by contract (NFR-P2 keeps every language conditional inside
# ``argus/index/``): the groupings below are COMMENTS, which Story 14.3 extends by adding
# names, never structure it would have to unpick. A bare ``assert`` statement is counted
# separately from the source span (it is not a call node), and a callee matching the
# project-helper naming convention is admitted by :func:`_matches_assertion_convention`
# rather than by an entry smuggled in here (AC7.2).
#
# Story 14.2 widened this from 23 names, all ``unittest``, after measuring that an assertion
# the table could not see is present in 13 of the 31 adjudicated spans. Story 14.3 owns the
# cross-language half (``expect``/``toBe``/``assertEquals``/``Fatalf``); NONE of it is here.
_ASSERTION_CALLEES: frozenset[str] = frozenset(
    {
        # ── unittest.TestCase, the original 23 ──
        "assertEqual",
        "assertNotEqual",
        "assertTrue",
        "assertFalse",
        "assertIs",
        "assertIsNot",
        "assertIsNone",
        "assertIsNotNone",
        "assertIn",
        "assertNotIn",
        "assertRaises",
        "assertRaisesRegex",
        "assertAlmostEqual",
        "assertGreater",
        "assertLess",
        "assertGreaterEqual",
        "assertLessEqual",
        "assertListEqual",
        "assertDictEqual",
        "assertSetEqual",
        "assertCountEqual",
        "assertRegex",
        "fail",
        # ── unittest.TestCase, the gaps the 23 missed ──
        "assertIsInstance",
        "assertNotIsInstance",
        "assertNotAlmostEqual",
        "assertNotRegex",
        "assertSequenceEqual",
        "assertTupleEqual",
        "assertMultiLineEqual",
        "assertWarns",
        "assertWarnsRegex",
        "assertLogs",
        "assertNoLogs",
        "failIf",
        "failUnless",
        # ── pytest's own assertion helpers ──
        # ``raises``/``warns``/``deprecated_call`` are ASSERTIONS for the density question:
        # `with pytest.raises(ValueError): parse(bad)` constrains the SUT precisely. They are
        # also in ``provenance_scan.RESULT_OBSERVING_CONTEXT_CALLEES``, which is fact (b)'s
        # OWN table and is unaffected by their presence here (Story 14.1 / DN-3 is undisturbed
        # — that table is read by name, not by set membership in this one).
        "raises",
        "warns",
        "deprecated_call",
        # ── unittest.mock's assertion methods ──
        # Every one of these ALSO matches the naming convention below; they are enumerated
        # anyway because the convention is a fallback for names this project cannot know, and
        # the ecosystem's own vocabulary should be readable in one place.
        "assert_called",
        "assert_called_once",
        "assert_called_with",
        "assert_called_once_with",
        "assert_any_call",
        "assert_has_calls",
        "assert_not_called",
        "assert_awaited",
        "assert_awaited_once",
        "assert_awaited_with",
        "assert_awaited_once_with",
        "assert_any_await",
        "assert_has_awaits",
        "assert_not_awaited",
    }
)

#: The PROJECT-HELPER naming convention (Story 14.2 / DN-14-2-3, AC7.2). A separate, named,
#: documented PREDICATE rather than entries hidden in the frozenset, so Story 14.3 adds names
#: to a set whose contract it can read in one place.
#:
#: Every codebase grows its own assertion helpers — ``_assert_one_rejection``,
#: ``assert_corpus_holds`` — and no name table can enumerate them. Measured over the 31
#: adjudicated spans, the table ALONE reproduces neither the "4 of 31 lifted by names" nor the
#: "13 of 31 spans" figure this story is committed to; with the convention both reproduce
#: exactly. The numbers pin the design.
#:
#: ACCEPTED COLLISION COST, recorded with its error direction (AC7.4): a PRODUCTION helper
#: coincidentally named ``assert_*`` — or a name that merely begins with those letters, such
#: as ``asserted_value`` — now counts as an assertion. That can only RAISE ``assertion_sites``
#: and the floor fires from below, so the error direction is **one fewer flag** — the safe
#: direction under the locked asymmetry (a false 🔴 is the lethal failure; a real vacuous test
#: left advisory is tolerable). The corroboration half cannot be reached by it at all, because
#: that half does not read this predicate (DN-14-2-1).
#:
#: ``\w`` is a Unicode class on ``str`` patterns, so ``assert_café_vide`` matches exactly as an
#: ASCII name does (AC8.3 — the ``nonascii_unicode`` cartridge depends on this), and the
#: pattern is ``\Z``-anchored rather than ``$``-anchored so no line terminator can satisfy it
#: (AC8.1).
_ASSERTION_NAMING_CONVENTION = re.compile(r"\A_?assert\w*\Z")

# ── THE FROZEN VOCABULARY — the moat, made structural (Story 14.2 / DN-14-2-1) ────────────
#
# ⛔ THIS TABLE MUST NOT TRACK ``_ASSERTION_CALLEES``, and it is named for its PURPOSE rather
# than its contents so that stays true as the other one grows. It is pinned to the 23 names
# Story 14.1 shipped, and Story 14.3 must widen ``_ASSERTION_CALLEES`` and leave this alone.
#
# THE MEASURED REASON, not a precaution. Story 14.1's ``provenance_scan`` docstring claimed
# that passing the table in as a parameter made fact (b) independent of it. It does not: the
# scan reads the table in two places, and widening it was reproduced END TO END turning an
# ORDINARY mock-interaction test into a verdict-eligible finding —
#
#     def test_compute_calls_the_dependency():
#         compute([1, 2])                           # SUT reached, result DISCARDED
#         fake = Mock()
#         fake.calculate.return_value = 6
#         fake.calculate()
#         fake.calculate.assert_called_once_with()  # the only "assertion" in the test
#
#     23-name table : asserts=0 stmts=5 density=0   flagged=True  corroborated=False  advisory
#     widened table : asserts=1 stmts=5 density=1/5 flagged=True  corroborated=True   🔴
#
# — via ``_assertion_statement_lines``: that line becomes an assertion statement, it references
# the mock-bound name ``fake``, and ``mock_referencing_assertions`` goes 0 → 1. Density rises to
# 1/5, which is still BELOW the 1/4 floor, so the test stays flagged and is now promoted. That
# is the exact false-accusation class Epic 14 exists to close, manufactured by Epic 14's own fix.
#
# The corpus cannot adjudicate this and must not be read as reassurance: widening the table
# moved corroboration for 0 tests over both members ONLY because 0 of 4,673 are corroborated at
# all after 14.1 — an EMPTY DENOMINATOR, i.e. UNEVALUABLE, not a confirmation. The mechanism
# above is the evidence. Rejected alternative: one table everywhere, plus a guard asserting
# corroboration did not move on the corpus — a test that proves nothing (``AI-E3-1``).
#
# DN-4 (Story 14.1) still holds and is a DIFFERENT claim: fact (b) depends on no assertion
# COUNT and no threshold. This is independence from the TABLE, which DN-4 never gave.
_CORROBORATION_ASSERTION_CALLEES: frozenset[str] = frozenset(
    {
        "assertEqual",
        "assertNotEqual",
        "assertTrue",
        "assertFalse",
        "assertIs",
        "assertIsNot",
        "assertIsNone",
        "assertIsNotNone",
        "assertIn",
        "assertNotIn",
        "assertRaises",
        "assertRaisesRegex",
        "assertAlmostEqual",
        "assertGreater",
        "assertLess",
        "assertGreaterEqual",
        "assertLessEqual",
        "assertListEqual",
        "assertDictEqual",
        "assertSetEqual",
        "assertCountEqual",
        "assertRegex",
        "fail",
    }
)


def is_assertion_callee(callee: str) -> bool:
    """Whether *callee* counts as an assertion for the DENSITY NUMERATOR (Story 14.2 / AC7.2).

    The name table OR the project-helper naming convention. Declared once and read by the
    scorer, so "is this an assertion?" has a single answer in this module (AR7/§3.3).

    ⛔ **Not** the question the corroboration path asks. Facts (a) and (b) read
    :data:`_CORROBORATION_ASSERTION_CALLEES` directly and must never be routed through here —
    see that table's comment for the false accusation this separation prevents (DN-14-2-1).
    """
    return callee in _ASSERTION_CALLEES or _matches_assertion_convention(callee)


def _matches_assertion_convention(callee: str) -> bool:
    """Whether *callee* follows the project-helper assertion naming convention.

    ``assert_valid`` / ``_assert_one_rejection`` / ``assertSomethingProjectSpecific``. Named
    and documented separately from the frozenset so Story 14.3 extends a set whose contract it
    can read in one place — see :data:`_ASSERTION_NAMING_CONVENTION` for the measurement that
    required it and for the accepted collision cost.
    """
    return _ASSERTION_NAMING_CONVENTION.match(callee) is not None

# Known mock/patch construction primitives.
_MOCK_CALLEES: frozenset[str] = frozenset(
    {
        "Mock",
        "MagicMock",
        "AsyncMock",
        "NonCallableMock",
        "NonCallableMagicMock",
        "PropertyMock",
        "patch",
        "patch_object",
        "create_autospec",
        "mock_open",
    }
)

class VacuousTestScore(BaseModel):
    """Per-test fixed-precision heuristic score + evidence counts (AR4).

    Ratios are exact ``Fraction`` — NEVER ``float`` (the Story 1.1 serializer
    rejects ``float``). Counts/lines are ``int``. Frozen ``extra="forbid"`` (the
    1.1/1.2 precedent). Travels WITH the finding as evidence (FR10).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    test_name: str = Field(..., description="Test function name.")
    start_line: int = Field(..., ge=1, description="1-based start line of the test function.")
    end_line: int = Field(..., ge=1, description="1-based end line of the test function.")
    assertion_sites: int = Field(..., ge=0, description="Assertion sites (calls + bare asserts).")
    statement_count: int = Field(..., ge=0, description="Top-level statements in the test body.")
    call_sites: int = Field(..., ge=0, description="Call/reference sites in the test span.")
    mock_sites: int = Field(..., ge=0, description="Mock/patch construction sites.")
    assertion_density: Fraction = Field(
        ..., description="assertion_sites / statement_count (Fraction, NEVER float)."
    )
    mock_ratio: Fraction = Field(
        ..., description="mock_sites / call_sites (Fraction, NEVER float)."
    )
    heuristically_vacuous: bool = Field(
        ..., description="True iff below the density floor OR above the mock ceiling."
    )
    ast_corroborated: bool = Field(
        ..., description="True iff the Tier-A AST subset corroborated the vacuity (verdict-eligible)."
    )


# Suffixes that identify a test file on the FILENAME alone, with no ambiguity: in
# these ecosystems the convention is reserved for tests and no production module
# adopts it. EVERY entry begins with a real WORD SEPARATOR (``_`` or ``.``), because
# a convention without one matches a letter SEQUENCE instead of a word: ``"test.java"``
# and ``"spec.rb"`` used to sit here and claimed ``latest.java`` / ``myspec.rb``, which
# removed ordinary production files from the FR4 critical set under the false reason
# ``test_file`` (DF-8-2-B). ``tests/test_classification_word_boundary.py`` closes over
# these tables and fails on any future entry that carries no boundary.
_UNAMBIGUOUS_TEST_SUFFIXES = (
    "_test.go", ".test.js", ".spec.js",
    ".test.ts", ".spec.ts", ".test.jsx", ".spec.jsx", ".test.tsx", ".spec.tsx",
    "_test.rs", "_spec.rb", "_test.cpp", "_test.cc",
)

# Java's word separator is a CASE boundary, so this table is matched CASE-SENSITIVELY
# against the ORIGINAL-CASE basename, before the lowercasing below. Maven Surefire's
# defaults are ``**/Test*.java``, ``**/*Test.java``, ``**/*Tests.java``,
# ``**/*TestCase.java`` — all CamelCase; Java has no ``_`` convention, so spelling this
# ``"_test.java"`` would delete every Java test in the world, and lowercasing first
# destroys the only boundary the name has. This is a language-specific NAMING
# convention, not a grammar/parse conditional, so it belongs here beside the other
# conventions and does NOT breach NFR-P2 ("the language conditional remains confined to
# ``argus/index/``").
_CASE_SENSITIVE_TEST_SUFFIXES = ("Test.java",)

# Python suffixes that are GENUINELY AMBIGUOUS. ``*_test.py`` is a real pytest
# convention (``python_files = test_*.py *_test.py``), so it cannot simply be dropped
# — but it also matches production modules whose subject happens to be testing, e.g.
# ``argus/detectors/vacuous_test.py``, the vacuous-TEST DETECTOR. Classifying that as
# a test file skipped it from deep grading and dropped it to ``tool_scanned_only``.
# These are resolved by CONTENT when an AST entry is available (see below).
_AMBIGUOUS_PYTHON_TEST_SUFFIXES = ("_test.py",)

# Whole BASENAMES resolved by the same tier-3 content rule. A bare ``"test.py"`` suffix
# used to stand in for this and matched ``contest.py`` / ``attest.py`` / ``latest.py``
# too; the fix is the whole-name rule it was really standing in for, not deleting it.
# ``conftest.py`` genuinely is ambiguous — one holding only fixtures is production and
# one holding test helpers is not — so it stays in TIER 3 and is decided by CONTENT.
_AMBIGUOUS_PYTHON_TEST_BASENAMES = ("conftest.py",)

_TEST_DIRECTORY_NAMES = ("tests", "test", "__tests__", "spec", "specs")


def _exhibits_test_definitions(ast_entry: object) -> bool:
    """True iff *ast_entry* defines something test-shaped (PURE, content-derived).

    The disambiguator for :data:`_AMBIGUOUS_PYTHON_TEST_SUFFIXES`. Mirrors the
    doctrine ``assess_criticality`` already applies — classify by CONTENT, never by
    filename alone — using the pre-built 1.4 definitions (no re-parse, AR7/§3.3).

    Returns ``True`` for any entry it cannot read (missing / parse-failed /
    AST-ineligible / wrong-shaped). That direction is deliberate: the two possible
    misclassifications are NOT symmetric. Treating a production module as a test
    under-states coverage (visibly, in the ledger); treating a TEST as production
    both inflates the deep count AND skips the vacuous-test detector on it — a hole
    in the moat and a false green. When the content cannot be read, stay a test file.
    """
    if not isinstance(ast_entry, AstIndexEntry):
        return True
    if ast_entry.parse_failed or not ast_entry.ast_eligible:
        return True
    for definition in ast_entry.definitions:
        name = definition.name
        if definition.kind == "function" and name.startswith("test"):
            return True
        # unittest style: `class TestFoo(TestCase)` holds the test_* methods.
        if definition.kind == "class" and name.lower().startswith("test"):
            return True
    return False


def _lower_basename(file_path: str) -> str:
    parts = file_path.replace("\\", "/").split("/")
    return parts[-1].lower() if parts else file_path.lower()


def _is_unambiguous_test_path(file_path: str) -> bool:
    """Tiers 1-2 — a test LOCATION, or a filename convention reserved for tests.

    Split out so the tier structure is declared exactly ONCE and both public
    predicates below READ it rather than restate it (AR7/§3.3 no-fork). Answers here
    are properties of what the file IS: they hold whatever the parse did.
    """
    parts = file_path.replace("\\", "/").split("/")
    if any(p in _TEST_DIRECTORY_NAMES for p in parts[:-1]) or (
        parts and parts[0] in ("tests", "test", "spec")
    ):
        return True
    # Checked BEFORE the lowercasing: for these conventions the capital IS the word
    # separator, so folding case first would destroy the only boundary they have.
    raw = parts[-1] if parts else file_path
    if any(raw.endswith(s) for s in _CASE_SENSITIVE_TEST_SUFFIXES):
        return True
    name = _lower_basename(file_path)
    if name.startswith("test_") or name.startswith("test."):
        return True
    return any(name.endswith(s) for s in _UNAMBIGUOUS_TEST_SUFFIXES)


def is_test_classification_content_dependent(file_path: str) -> bool:
    """True iff :func:`is_test_file` must read the CONTENT to classify *file_path*.

    True means the path reached **tier 3** — neither the test-directory tier nor the
    unambiguous-name tier fired — so the answer is a judgement about what this file
    CONTAINS, and when the content cannot be read
    :func:`_exhibits_test_definitions` returns a deliberately conservative **guess**
    (``True``) rather than a fact. False means the answer came from the location or a
    filename convention reserved for tests, which holds however the parse went.

    Exported because that distinction is not the same question for every consumer.
    For GRADING — this module's original consumer — "assume test when unreadable" is
    the safe direction: it keeps the false-accusation moat and the vacuous-test pass
    closed over the file. For the FR4/DR-5 critical-set ELIGIBILITY filter the
    identical direction is the LOOSENING one: it would drop an unreadable,
    security-token-bearing PRODUCTION module out of the critical set and disclose a
    FALSE reason (``test_file``) for it. That consumer therefore distrusts a tier-3
    label on an unreadable entry — see ``pipeline._critical_ineligibility``.
    """
    if _is_unambiguous_test_path(file_path):
        return False
    name = _lower_basename(file_path)
    return name in _AMBIGUOUS_PYTHON_TEST_BASENAMES or any(
        name.endswith(s) for s in _AMBIGUOUS_PYTHON_TEST_SUFFIXES
    )


def is_test_file(file_path: str, *, ast_entry: "AstIndexEntry | None" = None) -> bool:
    """True iff *file_path* is a test file under multi-language conventions.

    Recognizes test paths across Python, JavaScript, TypeScript, Go, Rust, Java,
    C/C++, Ruby. Three tiers, evaluated in order:

    1. **Location** — anything under a test directory is a test file.
    2. **Unambiguous filename** — a ``test_``/``test.`` prefix, a suffix from
       :data:`_UNAMBIGUOUS_TEST_SUFFIXES`, or a CASE-SENSITIVE suffix from
       :data:`_CASE_SENSITIVE_TEST_SUFFIXES` (``*Test.java``, whose separator is the
       capital). Every one of them carries a real word boundary, so a production file
       whose name merely ENDS with those letters — ``latest.java``, ``myspec.rb`` — is
       not claimed here.
    3. **Ambiguous Python name** (``*_test.py``, ``conftest.py``) — resolved by CONTENT
       when *ast_entry* is supplied, and by the filename alone when it is not.

    ``ast_entry`` is OPTIONAL and keyword-only, so every existing call site keeps its
    exact behaviour (tier 3 without an entry answers ``True``, as before). A caller
    that HAS the pre-built AST entry — the pipeline does — passes it and gets the
    content-derived answer, which is what stops a production module named
    ``*_test.py`` from being mistaken for a test suite.

    A caller that needs to know WHICH tier answered (because the tier-3 guess is not
    a fact) asks :func:`is_test_classification_content_dependent`.
    """
    if _is_unambiguous_test_path(file_path):
        return True
    if is_test_classification_content_dependent(file_path):
        if ast_entry is None:
            return True
        return _exhibits_test_definitions(ast_entry)
    return False


class _HasFilePath(Protocol):
    """Structural row type: anything carrying a repo-relative ``file_path``.

    Declared structurally so :func:`partition_application_files` can serve both call sites
    without this leaf detector module importing the ledger (the import-isolation gate keeps
    ``argus.detectors.*`` a leaf), and so each caller gets its OWN element type back.
    """

    @property
    def file_path(self) -> str: ...  # pragma: no cover - structural declaration


_EntryT = TypeVar("_EntryT", bound=_HasFilePath)


def partition_application_files(
    entries: Iterable[_EntryT],
    ast_index: object | None = None,
) -> tuple[list[_EntryT], int]:
    """Split ledger entries into (APPLICATION entries, held-out count) — ONE derivation.

    Closes ``DF-8-3-C``. Story 8.3's AC8 correctly REUSED :func:`is_test_file` rather than
    forking a second classifier, but the *plumbing* around it was written twice, verbatim, in
    two modules: ``pipeline._assessment_scope_paths`` (which narrows the ASSESSED population
    the verdict gate folds over) and ``reports.generator._coverage_scope_suggestion`` (which
    derives the report's APPLICATION denominator). Two spellings of one derivation, whose
    agreement the verdict depends on — precisely the disagreement class AC8 removed one level
    down. This is the single derivation both now call; it is a DE-DUPLICATION, not a second
    parallel derivation (AR7 / §3.3: reuse, never fork).

    *ast_index* is the pre-built 1.4 AST index when the caller has one (both production
    callers do), and ``None`` for callers that do not. It is read defensively via ``getattr``
    — the same spelling ``generator.py`` already used — so an index-less caller keeps the
    name-only tier-3 behaviour byte-for-byte. The AST entry is what lets an ambiguously-named
    ``*_test.py`` module be classified BY CONTENT, which is the mechanism that stops the
    report's denominator and the verdict's assessed population from disagreeing inside a
    single run.

    Typed structurally rather than against ``CoverageLedgerEntry`` so this leaf detector
    module gains no new import edge, and so the returned list keeps the caller's own element
    type. The held-out count is returned beside the list because both call sites need it and
    ``len(entries) - len(application)`` is the third place the same subtraction would be
    written.
    """
    entry_list = list(entries)
    entry_by_path = {
        entry.file_path: entry for entry in (getattr(ast_index, "entries", ()) or ())
    }
    application = [
        e
        for e in entry_list
        if not is_test_file(e.file_path, ast_entry=entry_by_path.get(e.file_path))
    ]
    return application, len(entry_list) - len(application)


def _is_test_function(definition: Definition) -> bool:
    return definition.kind == "function" and definition.name.startswith("test")


def _edges_in_span(edges: tuple[CodeEdge, ...], start: int, end: int) -> list[CodeEdge]:
    return [e for e in edges if start <= e.line <= end]


def _count_bare_asserts(source_lines: list[str], start: int, end: int) -> int:
    """Count bare ``assert`` statements in the 1-based inclusive span (deterministic).

    A bare ``assert`` is not a ``call`` node, so it is absent from the 1.4 edge
    set; we count it from the source text. Heuristic-but-deterministic: a line
    whose first non-whitespace token is ``assert`` followed by whitespace / EOL.
    """
    count = 0
    for line_no in range(start, end + 1):
        idx = line_no - 1
        if idx < 0 or idx >= len(source_lines):
            continue
        if opens_bare_assert(source_lines[idx].lstrip()):
            count += 1
    return count


def _count_statements(source_lines: list[str], start: int, end: int) -> int:
    """LOGICAL statements in the test body — the density denominator (Story 14.2 / AC1).

    RE-AUTHORED 2026-08-18, and the reason is measured rather than stylistic. This counted
    every non-blank, non-comment **LINE** of the span. A multi-line call, a dict literal, a
    closing bracket and **every line of a docstring** each scored as a statement, so the
    denominator ran at **1.9071×** CPython's own statement count over the 1,848 flagged
    minions tests (ground truth: every ``ast.stmt`` in the body, recursively). An inflated
    denominator depresses ``assertion_density`` arithmetically, and the 1/4 floor fires from
    below — so half of every test suite was being flagged for a reason that was arithmetic
    rather than evidence. The replacement measures **1.0000×** of ground truth, exact on all
    1,848 spans (agent-smith: 0.9997×, exact on 680 of 681).

    ⚠️ **The residual's DIRECTION was itself measured wrong first, and that is recorded
    rather than quietly fixed** (review iteration 1). The first implementation claimed a
    bounded under-count "away from a flag"; of its non-exact spans, 64/64 (minions) and 27/28
    (agent-smith) were OVER-counts, biasing TOWARDS a flag — a continuation-clause header
    (``except``/``else``/``finally``/``case``) or a decorator opening a statement CPython does
    not build. Both are now excluded at the count; **0** over-counts remain in either member,
    and **0** flags were gained by the correction. See
    :func:`~argus.detectors.provenance_scan.logical_statement_count`.

    It is a REUSE, not a second scanner (AR7/§3.3, AC1.2): ``provenance_scan`` already had to
    answer *"where does a statement start?"* for fact (b), and two spellings of that question
    is the disagreement class this detector keeps closing elsewhere. The cross-line string
    state the docstring case needs was added THERE, once, and both consumers read it.

    Still PURE, still deterministic, still line-terminator-agnostic: it reads the
    ``source.splitlines()`` list the detector already holds.
    """
    return body_statement_count(source_lines, start, end)


class VacuousTestDetector:
    """PURE heuristic vacuous-test scorer + Tier-A vacuous-path AST subset.

    Satisfies the ``detectors.base.Detector`` protocol structurally. ``run`` is a
    pure function over (test source text + the Story 1.4 ``AstIndexEntry``); it
    performs NO I/O, NO clock, NO LLM (zero-token), NO ``uuid4``/``random``, and
    emits NO ``float`` field (ratios are ``Fraction``). Un-parseable / non-test /
    un-analyzable input degrades to a recorded condition, never a false flag.
    """

    rule_id = RULE_HEURISTIC

    def run(
        self,
        *,
        file_path: str,
        source: str,
        ast_entry: AstIndexEntry,
        coverage_envelope_slice: str | None = None,
    ) -> DetectorResult:
        """Score *file_path* and emit findings + a coverage entry (AR8 pure).

        Degrades (records, does not flag) when the file is not a test file, the
        1.4 index marked it ``parse_failed`` / ``ast_eligible=False``, or it has no
        resolvable test functions. Otherwise scores each test function, FLAGS the
        heuristically-vacuous ones (advisory), corroborates via the Tier-A AST
        subset (verdict-eligible when both AST facts hold), grades the file
        ``audited_shallow`` via ``grade_entry`` (REUSE), and carries the counts as
        finding evidence (FR10).
        """
        if not is_test_file(file_path, ast_entry=ast_entry):
            return DetectorResult(
                degraded=(DegradedCondition(file_path=file_path, reason="not_a_test_file"),)
            )
        if ast_entry.parse_failed or not ast_entry.ast_eligible:
            reason = ast_entry.parse_failure_reason or "not_ast_eligible"
            return DetectorResult(
                degraded=(DegradedCondition(file_path=file_path, reason=reason),)
            )

        source_lines = source.splitlines()
        test_defs = [d for d in ast_entry.definitions if _is_test_function(d)]
        if not test_defs:
            return DetectorResult(
                degraded=(DegradedCondition(file_path=file_path, reason="no_test_functions"),)
            )

        findings = []
        any_flagged = False
        for definition in sorted(test_defs, key=lambda d: (d.start_line, d.end_line, d.name)):
            score = self._score(source_lines, ast_entry.edges, definition)
            if not score.heuristically_vacuous:
                continue
            any_flagged = True
            corroborated = score.ast_corroborated
            draft = FindingDraft(
                file_path=file_path,
                start_line=definition.start_line,
                end_line=definition.end_line,
                ast_span=definition.ast_span,
                rule_id=RULE_AST if corroborated else RULE_HEURISTIC,
                advisory=True,
                coverage_envelope_slice=coverage_envelope_slice,
            )
            depth = CoverageDepth.AUDITED_SHALLOW if corroborated else None
            findings.append(
                build_recording(draft, depth_supported=depth, claim_present=False)
            )

        if not any_flagged:
            # A genuine, well-asserting test file: examined, graded shallow, NOT
            # flagged (the false-accusation moat). No findings emitted.
            entry = grade_entry(
                file_path=file_path,
                proposed_depth=CoverageDepth.AUDITED_SHALLOW,
                claim_present=False,
            )
            return DetectorResult(entries=(entry,))

        recording_ids = tuple(f.recording_id for f in findings)
        entry = grade_entry(
            file_path=file_path,
            proposed_depth=CoverageDepth.AUDITED_SHALLOW,
            claim_present=False,
            recording_ids=recording_ids,
        )
        return DetectorResult(entries=(entry,), findings=tuple(findings))

    def _score(
        self,
        source_lines: list[str],
        edges: tuple[CodeEdge, ...],
        definition: Definition,
    ) -> VacuousTestScore:
        start, end = definition.start_line, definition.end_line
        span_edges = _edges_in_span(edges, start, end)

        # The DENSITY numerator reads the WIDE vocabulary (table + naming convention); the
        # corroboration path below reads the FROZEN one. Two questions, not two spellings of
        # one — DN-14-2-1 / DN-14-2-4.
        assertion_call_sites = sum(1 for e in span_edges if is_assertion_callee(e.callee))
        bare_asserts = _count_bare_asserts(source_lines, start, end)
        assertion_sites = assertion_call_sites + bare_asserts

        mock_sites = sum(1 for e in span_edges if e.callee in _MOCK_CALLEES)
        call_sites = len(span_edges)
        statement_count = _count_statements(source_lines, start, end)

        assertion_density = (
            Fraction(assertion_sites, statement_count) if statement_count else Fraction(0)
        )
        mock_ratio = Fraction(mock_sites, call_sites) if call_sites else Fraction(0)

        heuristically_vacuous = (
            statement_count > 0
            and (assertion_density < ASSERTION_DENSITY_FLOOR or mock_ratio > MOCK_RATIO_CEILING)
        )

        ast_corroborated = self._ast_corroborated(
            source_lines, span_edges, start, end, heuristically_vacuous
        )

        return VacuousTestScore(
            test_name=definition.name,
            start_line=start,
            end_line=end,
            assertion_sites=assertion_sites,
            statement_count=statement_count,
            call_sites=call_sites,
            mock_sites=mock_sites,
            assertion_density=assertion_density,
            mock_ratio=mock_ratio,
            heuristically_vacuous=heuristically_vacuous,
            ast_corroborated=ast_corroborated,
        )

    @staticmethod
    def _sut_call_sites(span_edges: list[CodeEdge]) -> list[CodeEdge]:
        """Candidate SUT calls: non-assertion, non-mock callees in the test span (fact a).

        Reads :data:`_CORROBORATION_ASSERTION_CALLEES`, NEVER the widened table and never
        :func:`is_assertion_callee` — this is the corroboration path (DN-14-2-1). Widening
        the vocabulary here can only SHRINK the candidate SUT set, which is a direction that
        moves fact (a) and fact (b) towards an accusation; the frozen table is what stops
        Story 14.3's four-language widening from reaching the moat.
        """
        return [
            e
            for e in span_edges
            if e.callee not in _CORROBORATION_ASSERTION_CALLEES
            and e.callee not in _MOCK_CALLEES
        ]

    def _ast_corroborated(
        self,
        source_lines: list[str],
        span_edges: list[CodeEdge],
        start: int,
        end: int,
        heuristically_vacuous: bool,
    ) -> bool:
        """Tier-A two-fact corroboration over the UNRESOLVED 1.4 edge set (DF-1-4-A).

        Conservative by design — corroborates ONLY when both AST facts hold:

        - **fact (a), reachability (UNCHANGED)** — the test reaches a candidate SUT
          (≥1 non-assertion/non-mock call in the span).
        - **fact (b), vacuity** — the asserted values do not derive from the SUT
          output: some SUT call's result is thrown away, **no** SUT call's result is
          consumed, and at least one assertion references a mock-bound name. See
          "Why fact (b) is not ``mock_sites >= 1``" in the module docstring for the
          measurement that replaced the old term and for what each clause means.

        When either fact cannot be established, corroboration is NOT granted — the
        finding stays heuristic-only/advisory and never reaches the verdict (it does
        NOT fabricate corroboration; the conservative default IS the moat). Pure; the
        provenance signal is NAME-level, not dataflow (``DF-14-1-A``; Story 6.2 owns
        real assertion provenance).
        """
        if not heuristically_vacuous:
            return False
        reaches_sut = len(self._sut_call_sites(span_edges)) >= 1  # fact a — unchanged
        if not reaches_sut:
            return False
        evidence = provenance_evidence(
            source_lines,
            span_edges,
            start,
            end,
            # ⛔ FROZEN, never `_ASSERTION_CALLEES` (DN-14-2-1). `provenance_scan` reads this
            # table in two places and BOTH can move towards an accusation when it widens; the
            # measured false 🔴 is written out beside the table's declaration above.
            assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
            mock_callees=_MOCK_CALLEES,
        )
        return evidence.sut_result_is_discarded and evidence.mock_referencing_assertions >= 1
