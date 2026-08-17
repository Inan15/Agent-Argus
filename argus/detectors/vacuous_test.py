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
  (``assertEqual``/``assertTrue``/… unittest family) PLUS bare ``assert``
  statements counted from the source text within the function span (tree-sitter
  ``assert_statement`` is not a ``call`` node, so the index edge set does not
  carry it — we count it from the source lines, deterministically).
- **Mock construction sites** — call edges whose callee is a known mock primitive
  (``Mock``/``MagicMock``/``patch``/``AsyncMock``/``create_autospec``/…).
- **assertion-density = assertion_sites / test_body_statements** (statements, not
  lines — robust to multi-line statements), stored as an exact ``Fraction``.
  Denominator 0 (no statements) → density is ``Fraction(0)`` and the file
  degrades (un-analyzable), never flagged.
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
3. **Discarded vs CONSUMED.** A SUT call is DISCARDED only when its whole logical
   statement is that call and nothing else. Anything else — bound to a name, nested
   in another expression, asserted on, compared, chained — is CONSUMED, and so is a
   call this module cannot locate in the source text at all (unresolvable is not
   evidence). A SUT call inside a ``pytest.raises`` / ``assertRaises`` /
   ``pytest.warns`` block is CONSUMED **by construction**: raising IS the
   observation (DN-3), and treating those as vacuous would re-create the
   false-accusation class on every fail-closed test.
4. **Fact (b) holds** iff at least one SUT call is discarded, **no** SUT call is
   consumed, and at least one assertion references a mock-bound name.

Requirement 3's "no consumed SUT call" is what makes fact (b) independent of the
heuristic's own inputs, and it is deliberately asymmetric: a test that constrains
the real SUT result — however many mocks it builds, however weak the constraint —
can never be corroborated, so it can never take a build to 🔴 on this rule.

The signal stays NAME-LEVEL and is a proxy, not dataflow (``DF-14-1-A``; real
assertion provenance is Story 6.2's). It reads the source text and the 1.4 index
and nothing else, so the scorer stays PURE (AR8), and it depends on **no count and
no threshold** — in particular not on ``assertion_sites``, whose callee table
Story 14.2 widens.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Iterable, NamedTuple, Protocol, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from argus.detectors.base import (
    DegradedCondition,
    DetectorResult,
    FindingDraft,
    build_recording,
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
    "is_test_file",
    "is_test_classification_content_dependent",
]

RULE_HEURISTIC = "vacuous_test_heuristic"
RULE_AST = "vacuous_test_ast"

# Heuristic thresholds (documented heuristics — see module docstring).
ASSERTION_DENSITY_FLOOR = Fraction(1, 4)
MOCK_RATIO_CEILING = Fraction(1, 2)

# Known assertion primitives (unittest family + pytest helpers). A bare ``assert``
# statement is counted separately from the source span (it is not a call node).
_ASSERTION_CALLEES: frozenset[str] = frozenset(
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

# Context managers whose BODY observes the SUT's behaviour, so a SUT call inside one
# is CONSUMED rather than discarded (Story 14.1 / DN-3, AC1.4). ``with
# pytest.raises(ValueError): parse(bad)`` constrains the SUT precisely — raising IS
# the observation — and scoring it as "the result was thrown away" would re-create the
# false-accusation class on every fail-closed test, a shape the validation corpus is
# full of. This is its OWN table and not an addition to ``_ASSERTION_CALLEES``: that
# one is Story 14.2's to widen, and fact (b) must not move when it does (DN-4).
_RESULT_OBSERVING_CONTEXT_CALLEES: frozenset[str] = frozenset(
    {
        "raises",
        "warns",
        "deprecated_call",
        "assertRaises",
        "assertRaisesRegex",
        "assertWarns",
        "assertWarnsRegex",
        "assertLogs",
        "assertNoLogs",
    }
)

# A Python identifier, Unicode-aware by construction: ``\w`` and ``[^\W\d]`` are
# Unicode classes on ``str`` patterns, so ``тесты``/``café`` names match exactly as
# ASCII ones do (the ``nonascii_unicode`` cartridge depends on this).
_IDENT = r"[^\W\d]\w*"

#: ``name = ...`` / ``a, b = ...`` / ``name: T = ...``. The negative lookahead is what
#: keeps ``==`` out; ``!=``/``+=``/``<=`` cannot reach the ``=`` at all because the
#: target group admits only identifiers and dots.
_ASSIGNMENT_RE = re.compile(
    rf"^\s*(?P<targets>{_IDENT}(?:\s*\.\s*{_IDENT})*"
    rf"(?:\s*,\s*{_IDENT}(?:\s*\.\s*{_IDENT})*)*)"
    rf"\s*(?::[^=]*?)?=(?!=)\s*(?P<value>.+)$"
)

#: The leading attribute chain of an expression: ``fake.calculate(…)`` → ``fake``,
#: ``calculate``.
_LEADING_CHAIN_RE = re.compile(rf"^({_IDENT})((?:\s*\.\s*{_IDENT})*)")

#: ``with cm() as name`` / ``… as a, … as b``.
_AS_BINDING_RE = re.compile(rf"\bas\s+({_IDENT})")

#: An identifier that ROOTS a chain — i.e. is not itself an attribute of something
#: else. ``fake.tally`` yields ``fake`` and not ``tally``.
_CHAIN_ROOT_RE = re.compile(rf"(?<![\w.]){_IDENT}")

#: ``pytest.raises(``/``assertRaises(`` — any result-observing context call, however
#: it is qualified. Built from the table (sorted, so the pattern is deterministic).
_OBSERVING_CALL_RE = re.compile(
    r"(?<!\w)(?:" + r"|".join(sorted(map(re.escape, _RESULT_OBSERVING_CONTEXT_CALLEES))) + r")\s*\("
)

_OPEN_BRACKETS = "([{"
_CLOSE_BRACKETS = ")]}"


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


def _opens_bare_assert(stripped: str) -> bool:
    """Whether *stripped* (a left-stripped source line) opens a bare ``assert``.

    Declared ONCE and read by both consumers — the heuristic's assertion count and
    the fact-(b) provenance scan (AR7/§3.3: reuse, never fork). Two spellings of
    "is this an assert line" is exactly the disagreement class this module keeps
    closing elsewhere.
    """
    return stripped == "assert" or stripped.startswith("assert ") or stripped.startswith("assert(")


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
        if _opens_bare_assert(source_lines[idx].lstrip()):
            count += 1
    return count


# ── Source-text scanning primitives for fact (b) — PURE, line-oriented, CRLF-safe ──
#
# Every one of these takes the ``source.splitlines()`` list the detector already
# receives, so no line terminator is ever observed: ``"a\r\nb".splitlines()`` and
# ``"a\nb".splitlines()`` are the same list, and no pattern below is anchored with
# ``$`` or relies on ``\s`` spanning a terminator. Local gates run on Windows and CI
# runs an ubuntu matrix; this module has to score both identically.


def _skip_string(text: str, index: int) -> int:
    """Index just past the string literal opening at *index* (or end of *text*).

    Single- and triple-quoted, backslash-aware. An unterminated literal (a
    triple-quoted string continuing onto the next line) consumes the rest of the
    line — a bounded, deterministic degradation, and one the conservative default
    absorbs: an unreadable statement produces no corroboration.
    """
    quote = text[index]
    delimiter = quote * 3 if text.startswith(quote * 3, index) else quote
    cursor = index + len(delimiter)
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
            continue
        if text.startswith(delimiter, cursor):
            return cursor + len(delimiter)
        cursor += 1
    return len(text)


def _code_prefix(line: str) -> str:
    """*line* with any trailing comment removed, string literals PRESERVED.

    Column indices into the result are valid indices into *line*, which is what lets
    a call site located by regex be split into "what precedes it" and "what follows".
    """
    cursor = 0
    while cursor < len(line):
        char = line[cursor]
        if char == "#":
            return line[:cursor]
        if char in "\"'":
            cursor = _skip_string(line, cursor)
            continue
        cursor += 1
    return line


def _blank_strings(code: str) -> str:
    """*code* with every string literal's characters replaced by spaces (length-preserving).

    Brackets, colons and identifiers inside a literal must not be read as syntax —
    ``with pytest.raises(ValueError, match="a:b"):`` has exactly one structural colon
    — and blanking rather than deleting keeps every column index aligned with *code*.
    """
    out: list[str] = []
    cursor = 0
    while cursor < len(code):
        char = code[cursor]
        if char in "\"'":
            end = _skip_string(code, cursor)
            out.append(" " * (end - cursor))
            cursor = end
            continue
        out.append(char)
        cursor += 1
    return "".join(out)


def _bracket_delta(code: str) -> int:
    """Net bracket depth change across *code* (strings blanked, comment already gone)."""
    masked = _blank_strings(code)
    return sum(
        1 if char in _OPEN_BRACKETS else -1
        for char in masked
        if char in _OPEN_BRACKETS or char in _CLOSE_BRACKETS
    )


def _logical_statement_end(source_lines: list[str], start_line: int, span_end: int) -> int:
    """Last 1-based line of the logical statement opening at *start_line* (bracket-balanced).

    Bounded by *span_end* so a malformed span can never walk out of the test function.
    """
    depth = 0
    for line_no in range(start_line, span_end + 1):
        index = line_no - 1
        if index < 0 or index >= len(source_lines):
            return line_no
        depth += _bracket_delta(_code_prefix(source_lines[index]))
        if depth <= 0:
            return line_no
    return span_end


def _statement_code(source_lines: list[str], start_line: int, end_line: int) -> str:
    """The comment-free code text of lines *start_line*..*end_line*, joined by a space."""
    parts = [
        _code_prefix(source_lines[line_no - 1]).strip()
        for line_no in range(start_line, end_line + 1)
        if 0 <= line_no - 1 < len(source_lines)
    ]
    return " ".join(part for part in parts if part)


def _locate_call(line: str, callee: str) -> tuple[str | None, int] | None:
    """Locate ``callee(`` on *line*; return (receiver-chain root, chain start column).

    The root is ``None`` for an unqualified call (``add(1, 2)``) and the leading
    identifier for a qualified one (``fake.calculate()`` → ``"fake"``). ``None`` is
    returned when the callee cannot be found on that line at all — a call whose
    function expression spans lines, or is computed. That is NOT treated as an
    unqualified SUT call: unresolvable is not evidence, and the caller reads it as
    CONSUMED so no corroboration can rest on it.
    """
    pattern = re.compile(
        rf"(?<![\w.])(?P<prefix>(?:{_IDENT}\s*\.\s*)*){re.escape(callee)}\s*\("
    )
    match = pattern.search(_blank_strings(_code_prefix(line)))
    if match is None:
        return None
    prefix = match.group("prefix")
    root_match = re.match(rf"\s*({_IDENT})", prefix) if prefix else None
    return (root_match.group(1) if root_match else None), match.start()


def _leading_chain(expression: str) -> tuple[str, ...]:
    """The leading attribute chain of *expression* — ``fake.calculate(…)`` → ``("fake", "calculate")``.

    Empty when the expression does not begin with an identifier (a literal, a list
    display, a parenthesised expression). Empty means "cannot establish", which the
    caller reads as NOT mock-derived.
    """
    text = expression.strip()
    if text.startswith("await "):
        text = text[len("await ") :].lstrip()
    match = _LEADING_CHAIN_RE.match(text)
    if match is None:
        return ()
    return (match.group(1), *re.findall(_IDENT, match.group(2)))


def _is_mock_derived(expression: str, mock_names: frozenset[str]) -> bool:
    """Whether *expression*'s value plausibly comes from a mock rather than the SUT.

    Two ways, both name-level: the chain is rooted at an already-mock-bound name
    (``fake.calculate()``), or some component of the leading chain is a mock
    construction primitive (``Mock()``, ``unittest.mock.patch(...)``).
    """
    chain = _leading_chain(expression)
    if not chain:
        return False
    return chain[0] in mock_names or any(part in _MOCK_CALLEES for part in chain)


def _structural_colon(code: str) -> int:
    """Column of the statement-terminating ``:`` in *code*, or ``-1``.

    Depth- and string-aware, so a dict display, a slice, an annotation inside a call
    and a ``match=":"`` regex are all skipped.
    """
    masked = _blank_strings(code)
    depth = 0
    for column, char in enumerate(masked):
        if char in _OPEN_BRACKETS:
            depth += 1
        elif char in _CLOSE_BRACKETS:
            depth -= 1
        elif char == ":" and depth == 0:
            return column
    return -1


def _result_observing_lines(source_lines: list[str], start: int, end: int) -> frozenset[int]:
    """1-based lines of the span that sit inside a result-observing context (DN-3).

    Indentation-scoped, because that is what a ``with`` block actually is. The inline
    single-line form (``with pytest.raises(X): parse(bad)``) is covered too — it is
    the same statement, written on one line.
    """
    covered: set[int] = set()
    open_indents: list[int] = []
    for line_no in range(start, end + 1):
        index = line_no - 1
        if index < 0 or index >= len(source_lines):
            continue
        code = _code_prefix(source_lines[index])
        stripped = code.strip()
        if not stripped:
            continue
        indent = len(code) - len(code.lstrip())
        while open_indents and indent <= open_indents[-1]:
            open_indents.pop()
        if open_indents:
            covered.add(line_no)
        if not (stripped.startswith("with ") or stripped.startswith("with(")):
            continue
        if not _OBSERVING_CALL_RE.search(_blank_strings(code)):
            continue
        colon = _structural_colon(code)
        if colon >= 0 and code[colon + 1 :].strip():
            covered.add(line_no)  # inline body — one statement, one line
        else:
            open_indents.append(indent)
    return frozenset(covered)


def _mock_bound_names(source_lines: list[str], start: int, end: int) -> frozenset[str]:
    """Names bound to mock-derived values within the span (forward pass, PURE).

    One pass in source order, which is the order Python binds them in. A name bound
    from an expression rooted at an earlier mock-bound name becomes mock-bound in
    turn, so ``fake = Mock(); pretended = fake.calculate()`` binds both.
    """
    bound: set[str] = set()
    for line_no in range(start, end + 1):
        index = line_no - 1
        if index < 0 or index >= len(source_lines):
            continue
        code = _code_prefix(source_lines[index])
        stripped = code.strip()
        if not stripped:
            continue
        if stripped.startswith("with ") or stripped.startswith("with("):
            header = stripped[len("with") :].lstrip()
            colon = _structural_colon(header)
            if colon >= 0:
                header = header[:colon]
            if _is_mock_derived(header, frozenset(bound)):
                bound.update(_AS_BINDING_RE.findall(_blank_strings(header)))
            continue
        assignment = _ASSIGNMENT_RE.match(code)
        if assignment is None:
            continue
        if not _is_mock_derived(assignment.group("value"), frozenset(bound)):
            continue
        for target in assignment.group("targets").split(","):
            name = target.strip()
            if name and "." not in name:
                bound.add(name)
    return frozenset(bound)


class _ProvenanceEvidence(NamedTuple):
    """What the span's source text says about where the asserted values came from.

    Counts only — no set is ever rendered into a message, so nothing here can leak
    iteration order into a ``.argus/``-bound output (NFR-D2 / AR4).
    """

    discarded_sut_calls: int
    consumed_sut_calls: int
    mock_referencing_assertions: int

    @property
    def sut_result_is_discarded(self) -> bool:
        """The SUT was reached and NOTHING the test does looks at what it returned."""
        return self.discarded_sut_calls >= 1 and self.consumed_sut_calls == 0


def _assertion_statement_lines(
    source_lines: list[str], span_edges: list[CodeEdge], start: int, end: int
) -> tuple[int, ...]:
    """1-based first lines of the span's assertion statements, SORTED (AR11).

    Both spellings the heuristic already counts: a bare ``assert`` (read from the
    source, since it is not a call node) and a call to an assertion primitive.
    """
    lines: set[int] = set()
    for line_no in range(start, end + 1):
        index = line_no - 1
        if 0 <= index < len(source_lines) and _opens_bare_assert(
            _code_prefix(source_lines[index]).lstrip()
        ):
            lines.add(line_no)
    lines.update(edge.line for edge in span_edges if edge.callee in _ASSERTION_CALLEES)
    return tuple(sorted(lines))


def _provenance_evidence(
    source_lines: list[str], span_edges: list[CodeEdge], start: int, end: int
) -> _ProvenanceEvidence:
    """Fact (b)'s evidence over the span: is the SUT result thrown away, and are the
    assertions looking at a mock instead? PURE — source text and the 1.4 edge set only.
    """
    mock_names = _mock_bound_names(source_lines, start, end)
    observed_lines = _result_observing_lines(source_lines, start, end)

    discarded = 0
    consumed = 0
    for edge in span_edges:
        if (
            edge.callee in _ASSERTION_CALLEES
            or edge.callee in _MOCK_CALLEES
            or edge.callee in _RESULT_OBSERVING_CONTEXT_CALLEES
        ):
            continue
        index = edge.line - 1
        if index < 0 or index >= len(source_lines):
            consumed += 1  # off-span edge: cannot be read, so it cannot corroborate
            continue
        located = _locate_call(source_lines[index], edge.callee)
        if located is None:
            consumed += 1  # unresolvable is not evidence (see _locate_call)
            continue
        receiver_root, chain_start = located
        if receiver_root is not None and receiver_root in mock_names:
            continue  # a mock-derived call, not a SUT call
        if edge.line in observed_lines:
            consumed += 1  # DN-3: raising IS the observation
            continue
        preceding = _code_prefix(source_lines[index])[:chain_start].strip()
        statement_end = _logical_statement_end(source_lines, edge.line, end)
        statement = _statement_code(source_lines, edge.line, statement_end)
        if preceding in ("", "await") and statement.endswith(")"):
            discarded += 1
        else:
            consumed += 1

    mock_referencing = 0
    for line_no in _assertion_statement_lines(source_lines, span_edges, start, end):
        statement_end = _logical_statement_end(source_lines, line_no, end)
        statement = _blank_strings(_statement_code(source_lines, line_no, statement_end))
        if any(name in mock_names for name in _CHAIN_ROOT_RE.findall(statement)):
            mock_referencing += 1

    return _ProvenanceEvidence(discarded, consumed, mock_referencing)



def _count_statements(source_lines: list[str], start: int, end: int) -> int:
    """Best-effort statement count in the body span (non-blank, non-comment lines).

    Deterministic heuristic over source lines (no dataflow). Excludes the ``def``
    header line, blank lines, and full-line comments. Multi-line statements
    undercount slightly — acceptable for a ratio denominator; the AST subset is
    the corroboration that gates verdict-eligibility.
    """
    count = 0
    for line_no in range(start + 1, end + 1):  # skip the def header line
        idx = line_no - 1
        if idx < 0 or idx >= len(source_lines):
            continue
        stripped = source_lines[idx].strip()
        if not stripped or stripped.startswith("#"):
            continue
        count += 1
    return count


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

        assertion_call_sites = sum(1 for e in span_edges if e.callee in _ASSERTION_CALLEES)
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
        """Candidate SUT calls: non-assertion, non-mock callees in the test span (fact a)."""
        return [
            e
            for e in span_edges
            if e.callee not in _ASSERTION_CALLEES and e.callee not in _MOCK_CALLEES
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
        evidence = _provenance_evidence(source_lines, span_edges, start, end)
        return evidence.sut_result_is_discarded and evidence.mock_referencing_assertions >= 1
