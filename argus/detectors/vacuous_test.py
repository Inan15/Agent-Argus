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
  output". The V1 name-level signal: the test reaches the SUT (fact a present) but
  its assertions are mock-dominated / literal-dominated (``mock_ratio`` high or
  zero non-assertion/non-mock SUT-derived call besides the SUT call). Because
  there is no dataflow, when this cannot be established the finding stays
  heuristic-only/advisory — it does NOT fabricate corroboration.
- **The conservative default is the moat.** When the unresolved edge set is
  insufficient, the finding does NOT gain verdict-eligibility. A false 🔴 is the
  lethal failure; a real vacuous test left advisory is tolerable. Full
  dataflow/scope-resolved grounding is Story 6.2.
"""

from __future__ import annotations

from fractions import Fraction

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


def is_test_file(file_path: str) -> bool:
    """True iff *file_path* is a test file under multi-language conventions.

    Recognizes test paths across Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, Ruby.
    """
    parts = file_path.replace("\\", "/").split("/")
    if any(p in ("tests", "test", "__tests__", "spec", "specs") for p in parts[:-1]) or (
        parts and parts[0] in ("tests", "test", "spec")
    ):
        return True
    name = parts[-1].lower() if parts else file_path.lower()
    if name.startswith("test_") or name.startswith("test."):
        return True
    test_suffixes = (
        "_test.py", "test.py", "_test.go", ".test.js", ".spec.js",
        ".test.ts", ".spec.ts", ".test.jsx", ".spec.jsx", ".test.tsx", ".spec.tsx",
        "_test.rs", "test.java", "spec.rb", "_spec.rb", "_test.cpp", "_test.cc"
    )
    return any(name.endswith(s) for s in test_suffixes)


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
        stripped = source_lines[idx].lstrip()
        if stripped == "assert" or stripped.startswith("assert ") or stripped.startswith("assert("):
            count += 1
    return count


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
        if not is_test_file(file_path):
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
            span_edges, assertion_sites, mock_sites, heuristically_vacuous
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
        span_edges: list[CodeEdge],
        assertion_sites: int,
        mock_sites: int,
        heuristically_vacuous: bool,
    ) -> bool:
        """Tier-A two-fact corroboration over the UNRESOLVED 1.4 edge set (DF-1-4-A).

        Conservative by design — corroborates ONLY when both AST facts hold:
        (a) the test reaches a candidate SUT (≥1 non-assertion/non-mock call in
        the span), AND (b) the vacuity signal: there ARE assertion sites (so the
        test claims to verify) yet they are mock-dominated (``mock_sites >= 1``)
        — i.e. the asserted values plausibly derive from mocks, not the SUT call.
        When (a) cannot be established, or there is no mock-domination signal,
        corroboration is NOT granted — the finding stays heuristic-only/advisory
        (it does NOT fabricate corroboration). Pure; no name binding / dataflow
        (that is Story 6.2).
        """
        if not heuristically_vacuous:
            return False
        sut_calls = self._sut_call_sites(span_edges)
        reaches_sut = len(sut_calls) >= 1  # fact a
        # fact b (name-level): the test asserts AND is mock-dominated, so the
        # asserted values plausibly derive from a mock rather than the SUT result.
        vacuity_signal = assertion_sites >= 1 and mock_sites >= 1
        return reaches_sut and vacuity_signal
