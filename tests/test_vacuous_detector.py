"""Vacuous-test detector + Tier-A AST subset (Story 1.5, AC1/2/3/5/6/7/10).

Verification area ArgusAgent-DETECT (TC-ArgusAgent-DETECT-001-NN). Covers the heuristic score
(fixed-precision ratios / zero-float), advisory-only vs AST-corroborated
eligibility, the MANDATORY false-accusation guard (a genuine well-asserting test
is NOT flagged; a clean/non-test file is NOT flagged), and honest degradation
(un-parseable / no-test-functions → recorded, no flag, no crash).

The pure-logic cases construct an ``AstIndexEntry`` directly; the integration
cases build it from a real tiny fixture via ``build_ast_index`` and so
``importorskip`` tree-sitter (mirrors the 1.4 strategy). The pure heuristic logic
over given counts stays UNCONDITIONALLY tested.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import pytest

from argus.detectors.vacuous_test import (
    RULE_AST,
    RULE_HEURISTIC,
    VacuousTestDetector,
    is_test_classification_content_dependent,
    is_test_file,
)
from argus.index.ast_index import AstIndexEntry, CodeEdge, Definition
from argus.ledger.coverage_ledger import CoverageDepth
from argus.store import canonical
from tests.test_classification_word_boundary import NEAR_MISS_CORPUS, assert_corpus_holds


# ── Pure-logic cases (no tree-sitter) — construct the AstIndexEntry directly ──


def _entry(definitions, edges, *, file_path="tests/test_mod.py") -> AstIndexEntry:
    return AstIndexEntry(
        file_path=file_path,
        ast_eligible=True,
        definitions=tuple(definitions),
        edges=tuple(edges),
    )


def test_is_test_file_rule() -> None:
    """TC-ArgusAgent-DETECT-001-85 — test-file identification (under tests/ or test_*/_test)."""
    assert is_test_file("tests/test_x.py")
    assert is_test_file("pkg/tests/foo.py")
    assert is_test_file("test_thing.py")
    assert is_test_file("thing_test.py")
    assert not is_test_file("argus/detectors/vacuous.py")
    assert not is_test_file("pkg/widget.py")


def test_test_classification_content_dependence_names_the_tier_that_answered() -> None:
    """TC-ArgusAgent-DETECT-001-95 — which TIER decided, exposed for the FR4/DR-5 consumer.

    ``is_test_file`` answers three ways and only ONE of them is a guess: tier 3 reads the
    file's definitions, so for an entry it cannot read it deliberately assumes "test"
    (conservative for grading — it keeps the vacuous-test moat closed). The critical-set
    eligibility filter consumes the same value in the opposite direction, where that
    assumption would drop an unreadable security module out of the gate, so it needs to
    know when the answer was content-derived. Both predicates read ONE tier structure
    (AR7/§3.3), which is why this asserts them together rather than in isolation.
    """
    # tier 1 (location) and tier 2 (reserved name) — properties of what the file IS.
    for path in ("tests/foo_test.py", "pkg/tests/thing.py", "test_thing.py", "svc/x_test.go"):
        assert is_test_file(path)
        assert not is_test_classification_content_dependent(path)

    # tier 3 — the ambiguous Python suffix, the ONE tier resolved by CONTENT.
    for path in ("app/auth_test.py", "svc/token_test.py", "pkg/conftest.py"):
        assert is_test_classification_content_dependent(path)

    # not a test path at all: no tier fired, so nothing was guessed.
    for path in ("argus/detectors/vacuous.py", "pkg/widget.py"):
        assert not is_test_file(path)
        assert not is_test_classification_content_dependent(path)

    # …and the guess itself is unchanged: tier 3 with an unreadable entry stays "test".
    unreadable = AstIndexEntry(file_path="app/auth_test.py", ast_eligible=False, parse_failed=True)
    assert is_test_file("app/auth_test.py", ast_entry=unreadable)


def test_a_name_convention_matches_a_word_not_a_letter_sequence() -> None:
    """TC-ArgusAgent-DETECT-001-100 — Story 11.2 / AC2.5: the near-miss corpus, pinned HERE.

    ``DF-8-2-B``'s close condition names THIS file explicitly, so the two headline
    near-misses are pinned beside ``-85``/``-95`` where a reviewer will look for them:
    ``svc/latest.java`` and ``svc/myspec.rb`` are ordinary production files that the
    tier-2 table used to claim as tests, which removed them from the FR4 critical set
    under the false reason ``test_file``.

    The corpus itself is declared ONCE, in
    ``tests/test_classification_word_boundary.py``, and IMPORTED here — never restated
    (AI-E9-7: an enumerable fact gets one home). The closure that makes the class stay
    closed lives there too (``-97``/``-98``/``-99``); this case is the signpost.
    """
    assert ("svc/latest.java", False, False) in {
        (c.path, c.is_test, c.content_dependent) for c in NEAR_MISS_CORPUS
    }
    assert ("svc/myspec.rb", False, False) in {
        (c.path, c.is_test, c.content_dependent) for c in NEAR_MISS_CORPUS
    }
    assert_corpus_holds()


def test_vacuous_mock_dominated_test_flagged_and_corroborated() -> None:
    """TC-ArgusAgent-DETECT-001-86 — RE-AUTHORED 2026-08-17 (Story 14.1 / AC4): what corroboration MEANS.

    WHY THIS TEST CHANGED, RECORDED RATHER THAN ADJUSTED
    ----------------------------------------------------
    Until 2026-08-17 this pinned corroboration on a test that binds the real SUT
    result and asserts it (``sut = widget_under_test(m, dep)`` / ``assert sut``),
    because fact (b) read ``assertion_sites >= 1 and mock_sites >= 1`` — *"the test
    constructs a mock"*. That is not what cross-cutting concern #6 requires and it was
    measured to be indistinguishable from its own input: over the two contributing
    validation-corpus members, ``ast_corroborated`` agreed with the bare
    ``mock_sites >= 1`` term in 2,527 of 2,529 heuristically-flagged tests, the rule
    class emitted 31 blocking findings on that corpus, and the named human adjudicated
    **0** of them true.

    So this is an INTENDED BEHAVIOUR CHANGE with its reason written down, not a test
    nudged until it matched new output. It now pins the new contract in **both
    directions**, because only the pair states it:

    * a mock-heavy test that ASSERTS THE REAL SUT RESULT is **advisory** — however
      many mocks it builds, and however weak the assertion; and
    * a test that DISCARDS the SUT result and asserts a mock-derived value is
      **corroborated** — the shape the planted cartridges carry.

    ``-88``, the false-accusation guard, is unchanged and is not this story's to
    weaken.
    """
    # ── ARM 1: SUT result thrown away, assertion on a mock-derived value → CORROBORATED ──
    corroborating = (
        "def test_widget():\n"  # line 1
        "    widget_under_test()\n"  # 2 — SUT reached, result THROWN AWAY
        "    m = Mock()\n"  # 3
        "    m.render.return_value = 7\n"  # 4
        "    pretended = m.render()\n"  # 5 — value bound from a MOCK
        "    assert pretended == 7\n"  # 6 — …and that is what is asserted
        # 1 assert / 5 statements = 1/5 < 1/4 → flagged; SUT discarded + mock-derived
        # assertion → fact (b) holds → corroborated.
    )
    defs = [Definition(name="test_widget", kind="function", start_line=1, end_line=6)]
    edges = [
        CodeEdge(callee="widget_under_test", line=2),
        CodeEdge(callee="Mock", line=3),
        CodeEdge(callee="render", line=5),
    ]
    result = VacuousTestDetector().run(
        file_path="tests/test_widget.py", source=corroborating, ast_entry=_entry(defs, edges)
    )

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.advisory is True
    assert finding.rule_id == RULE_AST  # AST-corroborated → verdict-eligible rule
    assert finding.depth_supported is CoverageDepth.AUDITED_SHALLOW
    assert finding.locators[0].ast_span == "function:test_widget@1-6"
    # graded audited_shallow, never audited_deep
    assert result.entries[0].depth is CoverageDepth.AUDITED_SHALLOW
    assert finding.recording_id in result.entries[0].recording_ids

    # ── ARM 2: the PREVIOUS fixture, verbatim — mock-heavy, but it asserts the SUT
    # result. Still flagged (mock_ratio 2/3 > 1/2); no longer verdict-eligible. ──
    sut_asserting = (
        "def test_widget():\n"  # 1
        "    m = Mock()\n"  # 2
        "    dep = MagicMock()\n"  # 3
        "    sut = widget_under_test(m, dep)\n"  # 4 — SUT result BOUND…
        "    assert sut\n"  # 5 — …and CONSTRAINED
    )
    defs = [Definition(name="test_widget", kind="function", start_line=1, end_line=5)]
    edges = [
        CodeEdge(callee="Mock", line=2),
        CodeEdge(callee="MagicMock", line=3),
        CodeEdge(callee="widget_under_test", line=4),
    ]
    demoted = VacuousTestDetector().run(
        file_path="tests/test_widget.py", source=sut_asserting, ast_entry=_entry(defs, edges)
    )
    assert len(demoted.findings) == 1  # still FLAGGED — the heuristic is unchanged
    assert demoted.findings[0].rule_id == RULE_HEURISTIC  # …but never verdict-eligible
    assert demoted.findings[0].depth_supported is None


def test_assertionless_test_flagged_advisory_only_when_no_corroboration() -> None:
    """TC-ArgusAgent-DETECT-001-87 — low-density test with no mock signal → advisory-only (heuristic)."""
    source = (
        "def test_thing():\n"  # 1
        "    do_a()\n"  # 2
        "    do_b()\n"  # 3
        "    do_c()\n"  # 4
        "    result = compute()\n"  # 5
        "    assert result\n"  # 6 — 1 assert / 5 statements = 1/5 < 1/4 → flagged
    )
    defs = [Definition(name="test_thing", kind="function", start_line=1, end_line=6)]
    edges = [
        CodeEdge(callee="do_a", line=2),
        CodeEdge(callee="do_b", line=3),
        CodeEdge(callee="do_c", line=4),
        CodeEdge(callee="compute", line=5),
    ]
    result = VacuousTestDetector().run(
        file_path="tests/test_thing.py", source=source, ast_entry=_entry(defs, edges)
    )
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.advisory is True
    assert finding.rule_id == RULE_HEURISTIC  # NOT corroborated → advisory-only
    assert finding.depth_supported is None  # the 1.6 gate must NOT 🔴 on it


def test_genuine_well_asserting_test_not_flagged_FALSE_ACCUSATION_GUARD() -> None:
    """TC-ArgusAgent-DETECT-001-88 — MANDATORY moat: a genuine test is NOT flagged."""
    source = (
        "def test_add():\n"  # 1
        "    result = add(2, 3)\n"  # 2
        "    assert result == 5\n"  # 3 — 1 assert / 2 statements = 1/2 >= 1/4
    )
    defs = [Definition(name="test_add", kind="function", start_line=1, end_line=3)]
    edges = [CodeEdge(callee="add", line=2)]
    result = VacuousTestDetector().run(
        file_path="tests/test_add.py", source=source, ast_entry=_entry(defs, edges)
    )
    assert result.findings == ()  # NOT flagged
    assert len(result.entries) == 1
    assert result.entries[0].depth is CoverageDepth.AUDITED_SHALLOW


def test_clean_non_test_file_not_flagged_FALSE_ACCUSATION_GUARD() -> None:
    """TC-ArgusAgent-DETECT-001-89 — MANDATORY moat: a non-test file is skipped, not mis-flagged."""
    source = "def widget(x):\n    return x + 1\n"
    defs = [Definition(name="widget", kind="function", start_line=1, end_line=2)]
    result = VacuousTestDetector().run(
        file_path="argus/widget.py",
        source=source,
        ast_entry=_entry(defs, [], file_path="argus/widget.py"),
    )
    assert result.findings == ()
    assert result.entries == ()
    assert len(result.degraded) == 1
    assert result.degraded[0].reason == "not_a_test_file"


def test_parse_failed_entry_degrades_no_flag_no_crash() -> None:
    """TC-ArgusAgent-DETECT-001-90 — a parse_failed entry degrades, never flagged/crashed (AR10)."""
    entry = AstIndexEntry(
        file_path="tests/test_broken.py",
        ast_eligible=False,
        parse_failed=True,
        parse_failure_reason="syntax_error",
    )
    result = VacuousTestDetector().run(
        file_path="tests/test_broken.py", source="def test_(:\n", ast_entry=entry
    )
    assert result.findings == ()
    assert result.degraded[0].reason == "syntax_error"


def test_no_test_functions_degrades() -> None:
    """TC-ArgusAgent-DETECT-001-91 — a test file with no test functions degrades cleanly."""
    source = "def helper():\n    return 1\n"
    defs = [Definition(name="helper", kind="function", start_line=1, end_line=2)]
    result = VacuousTestDetector().run(
        file_path="tests/test_empty.py", source=source, ast_entry=_entry(defs, [])
    )
    assert result.findings == ()
    assert result.degraded[0].reason == "no_test_functions"


def test_ratios_are_fraction_not_float_AR4() -> None:
    """TC-ArgusAgent-DETECT-001-92 — emitted findings serialize through the float-rejecting serializer."""
    source = (
        "def test_v():\n"
        "    m = Mock()\n"
        "    d = MagicMock()\n"
        "    out = run_sut(m, d)\n"
        "    assert out\n"
    )
    defs = [Definition(name="test_v", kind="function", start_line=1, end_line=5)]
    edges = [
        CodeEdge(callee="Mock", line=2),
        CodeEdge(callee="MagicMock", line=3),
        CodeEdge(callee="run_sut", line=4),
    ]
    result = VacuousTestDetector().run(
        file_path="tests/test_v.py", source=source, ast_entry=_entry(defs, edges)
    )
    # The finding payload serializes cleanly through the single (float-rejecting)
    # serializer — proving no float field leaked into the .argus/-bound model.
    payload = result.findings[0].model_dump(mode="json")
    assert canonical.dumps_bytes(payload)


def test_score_density_is_exact_fraction() -> None:
    """TC-ArgusAgent-DETECT-001-93 — the per-test score stores exact Fraction ratios."""
    detector = VacuousTestDetector()
    source = (
        "def test_x():\n"
        "    a()\n"
        "    b()\n"
        "    c()\n"
        "    d()\n"
        "    assert z()\n"
    )
    defn = Definition(name="test_x", kind="function", start_line=1, end_line=6)
    edges = (
        CodeEdge(callee="a", line=2),
        CodeEdge(callee="b", line=3),
        CodeEdge(callee="c", line=4),
        CodeEdge(callee="d", line=5),
        CodeEdge(callee="z", line=6),
    )
    score = detector._score(source.splitlines(), edges, defn)
    assert isinstance(score.assertion_density, Fraction)
    assert isinstance(score.mock_ratio, Fraction)
    # 1 bare assert / 5 body statements
    assert score.assertion_density == Fraction(1, 5)
    assert score.heuristically_vacuous is True


# ── Story 14.1: every branch of the NEW fact (b), reached deliberately ──
#
# "Non-vacuity travels with the assertions": a helper that can answer "not
# corroborated" for a reason that never occurs is decoration, so each clause below has
# a case that reaches it. All of them are FLAGGED by the (unchanged) heuristic — what
# is under test is only whether the finding is PROMOTED.


def _corroborated(source: str, defs: list[Definition], edges: list[CodeEdge]) -> bool:
    """Run the real detector and report whether the single finding is verdict-eligible."""
    result = VacuousTestDetector().run(
        file_path="tests/test_case.py", source=source, ast_entry=_entry(defs, edges)
    )
    assert len(result.findings) == 1, "the heuristic must still FLAG — only promotion is under test"
    return result.findings[0].rule_id == RULE_AST


def test_a_raises_context_sut_call_is_consumed_not_discarded() -> None:
    """TC-ArgusAgent-DETECT-001-101 — DN-3 / AC1.4: raising IS the observation.

    ``with pytest.raises(X): parse(bad)`` constrains the SUT precisely. Scoring the
    call as "result thrown away" would re-accuse every fail-closed test in the corpus
    — the exact false-accusation class this story exists to close — so a SUT call
    inside a result-observing context is CONSUMED by construction. This is the one
    known defect of the out-of-tree feasibility probe, designed in rather than
    inherited.
    """
    source = (
        "def test_parse_rejects_bad():\n"  # 1
        "    m = Mock()\n"  # 2
        "    m.reason.return_value = 'x'\n"  # 3
        "    with pytest.raises(ValueError):\n"  # 4
        "        parse('bad')\n"  # 5 — SUT, but its RAISING is the observation
        "    pretended = m.reason()\n"  # 6
        "    assert pretended == 'x'\n"  # 7
    )
    defs = [Definition(name="test_parse_rejects_bad", kind="function", start_line=1, end_line=7)]
    edges = [
        CodeEdge(callee="Mock", line=2),
        CodeEdge(callee="raises", line=4),
        CodeEdge(callee="parse", line=5),
        CodeEdge(callee="reason", line=6),
    ]
    assert _corroborated(source, defs, edges) is False

    # …and the SAME test with the raises context removed IS corroborated, which is what
    # proves the context is doing the work rather than some other clause.
    without_context = (
        "def test_parse_rejects_bad():\n"  # 1
        "    m = Mock()\n"  # 2
        "    m.reason.return_value = 'x'\n"  # 3
        "    parse('bad')\n"  # 4 — now genuinely discarded
        "    pretended = m.reason()\n"  # 5
        "    assert pretended == 'x'\n"  # 6
    )
    assert (
        _corroborated(
            without_context,
            [Definition(name="test_parse_rejects_bad", kind="function", start_line=1, end_line=6)],
            [
                CodeEdge(callee="Mock", line=2),
                CodeEdge(callee="parse", line=4),
                CodeEdge(callee="reason", line=5),
            ],
        )
        is True
    )


def test_one_consumed_sut_call_withholds_corroboration() -> None:
    """TC-ArgusAgent-DETECT-001-102 — the ``no consumed SUT call`` clause, reached alone.

    A test may throw one SUT result away and still constrain another. Fact (b) is a
    statement about the WHOLE test, so a single consumed result is enough to withhold
    promotion — the asymmetry the moat rests on (a false 🔴 is the lethal failure).
    """
    source = (
        "def test_mixed():\n"  # 1
        "    warm_up()\n"  # 2 — a discarded SUT call
        "    m = Mock()\n"  # 3
        "    m.value.return_value = 4\n"  # 4
        "    pretended = m.value()\n"  # 5
        "    real = compute()\n"  # 6 — …but THIS SUT result is bound…
        "    m.value.assert_called()\n"  # 7
        "    m.reset_mock()\n"  # 8
        "    assert pretended == 4\n"  # 9
        "    assert real is not None\n"  # 10 — …and CONSTRAINED
    )
    defs = [Definition(name="test_mixed", kind="function", start_line=1, end_line=10)]
    edges = [
        CodeEdge(callee="warm_up", line=2),
        CodeEdge(callee="Mock", line=3),
        CodeEdge(callee="value", line=5),
        CodeEdge(callee="compute", line=6),
        # `assert_called` / `reset_mock` are NOT in `_ASSERTION_CALLEES` (Story 14.2
        # widens that table). They are excluded from the SUT set here on their RECEIVER
        # chain instead, which is why fact (b) does not move when 14.2 lands — DN-4.
        CodeEdge(callee="assert_called", line=7),
        CodeEdge(callee="reset_mock", line=8),
    ]
    assert _corroborated(source, defs, edges) is False


def test_discarded_sut_but_no_mock_derived_assertion_is_not_corroborated() -> None:
    """TC-ArgusAgent-DETECT-001-103 — the ``assertion references a mock-bound name`` clause.

    The SUT result really is thrown away here, so the first two clauses hold. Nothing
    asserted derives from a mock, so there is no evidence about WHERE the asserted
    value came from — and "cannot establish" is never promoted to "established".
    """
    source = (
        "def test_no_mock_assertion():\n"  # 1
        "    warm_up()\n"  # 2 — SUT reached, result discarded
        "    m = Mock()\n"  # 3
        "    m.configure(1)\n"  # 4
        "    m.configure(2)\n"  # 5
        "    assert 1 + 1 == 2\n"  # 6 — a literal tautology, nothing mock-derived
    )
    defs = [Definition(name="test_no_mock_assertion", kind="function", start_line=1, end_line=6)]
    edges = [
        CodeEdge(callee="warm_up", line=2),
        CodeEdge(callee="Mock", line=3),
        CodeEdge(callee="configure", line=4),
        CodeEdge(callee="configure", line=5),
    ]
    assert _corroborated(source, defs, edges) is False


def test_a_call_on_a_mock_bound_name_is_not_a_sut_call() -> None:
    """TC-ArgusAgent-DETECT-001-104 — mock-derived calls are excluded from the SUT set.

    ``pretended = fake.calculate()`` binds a result, so if it counted as a SUT call it
    would count as a CONSUMED one and no planted cartridge could ever be promoted. The
    receiver chain is what distinguishes it, and this is the clause that keeps
    ``vacuous_basic`` / ``holdout_vacuous`` / ``nonascii_unicode`` corroborated.
    """
    source = (
        "def test_cartridge_shape():\n"  # 1
        "    compute_total([1, 2, 3])\n"  # 2
        "    fake = Mock()\n"  # 3
        "    fake.calculate.return_value = 6\n"  # 4
        "    pretended = fake.calculate()\n"  # 5 — mock-DERIVED, not a SUT call
        "    assert pretended == 6\n"  # 6
    )
    defs = [Definition(name="test_cartridge_shape", kind="function", start_line=1, end_line=6)]
    edges = [
        CodeEdge(callee="compute_total", line=2),
        CodeEdge(callee="Mock", line=3),
        CodeEdge(callee="calculate", line=5),
    ]
    assert _corroborated(source, defs, edges) is True


def test_a_patch_context_binds_its_as_name_as_mock_derived() -> None:
    """TC-ArgusAgent-DETECT-001-105 — ``with patch(...) as m`` is a mock binding too.

    Without this the whole ``patch``-style dialect would be invisible to fact (b) and
    an entire family of genuinely vacuous tests would silently stay advisory.
    """
    source = (
        "def test_patched():\n"  # 1
        "    with patch('svc.client') as fake:\n"  # 2
        "        fake.ping.return_value = 'pong'\n"  # 3
        "        boot()\n"  # 4 — SUT reached, result discarded
        "        echoed = fake.ping()\n"  # 5
        "        assert echoed == 'pong'\n"  # 6
    )
    defs = [Definition(name="test_patched", kind="function", start_line=1, end_line=6)]
    edges = [
        CodeEdge(callee="patch", line=2),
        CodeEdge(callee="boot", line=4),
        CodeEdge(callee="ping", line=5),
    ]
    assert _corroborated(source, defs, edges) is True


def test_an_unlocatable_call_is_conservative_not_corroborating() -> None:
    """TC-ArgusAgent-DETECT-001-106 — unresolvable is not evidence (the conservative default).

    The 1.4 edge set is UNRESOLVED (``DF-1-4-A``): an edge records a callee name and a
    line, and a call whose function expression spans lines cannot be located in the
    source text at that line. That is a gap in what can be READ, and a gap is never
    read as "the result was thrown away" — it is read as consumed, so no corroboration
    can rest on it.
    """
    source = (
        "def test_split_call():\n"  # 1
        "    m = Mock()\n"  # 2
        "    m.value.return_value = 9\n"  # 3
        "    (service\n"  # 4 — the edge lands HERE…
        "     .dispatch())\n"  # 5 — …but `dispatch(` is on the next line
        "    pretended = m.value()\n"  # 6
        "    assert pretended == 9\n"  # 7
    )
    defs = [Definition(name="test_split_call", kind="function", start_line=1, end_line=7)]
    edges = [
        CodeEdge(callee="Mock", line=2),
        CodeEdge(callee="dispatch", line=4),
        CodeEdge(callee="value", line=6),
    ]
    assert _corroborated(source, defs, edges) is False


def test_score_is_identical_on_CRLF_and_LF_source() -> None:
    """TC-ArgusAgent-DETECT-001-107 — the predicate reads SOURCE LINES, so line endings must not matter.

    Local gates here run on Windows and CI runs an ubuntu matrix, and this repository
    has already shipped a POSIX-only bug out of a green Windows run (``AI-E13-1``).
    Fact (b) is the most source-text-dependent thing the detector does, so the two
    encodings of the same file are scored and compared FIELD BY FIELD — not merely
    checked for the same verdict.
    """
    lf = (
        "def test_cartridge_shape():\n"
        "    compute_total([1, 2, 3])\n"
        "    fake = Mock()\n"
        "    fake.calculate.return_value = 6\n"
        "    pretended = fake.calculate()\n"
        "    assert pretended == 6\n"
    )
    crlf = lf.replace("\n", "\r\n")
    assert "\r\n" in crlf  # the fixture really is CRLF

    defn = Definition(name="test_cartridge_shape", kind="function", start_line=1, end_line=6)
    edges = (
        CodeEdge(callee="compute_total", line=2),
        CodeEdge(callee="Mock", line=3),
        CodeEdge(callee="calculate", line=5),
    )
    detector = VacuousTestDetector()
    lf_score = detector._score(lf.splitlines(), edges, defn)
    crlf_score = detector._score(crlf.splitlines(), edges, defn)

    assert lf_score == crlf_score
    assert lf_score.ast_corroborated is True  # …and it is the INTERESTING branch


#: The five ways one semantically identical test can be written. Four of them BIND the SUT
#: result (so a correct fact (b) must never corroborate them, however they are wrapped) and
#: the fifth genuinely throws it away (so it must stay corroborated, or the guard below would
#: pass by making everything advisory). Declared as data because the defect was a *shape*
#: family, and a hand-picked pair would have missed the half the reviewer did not think of —
#: the recorded finding named backslash continuation, and PEP 8's PREFERRED wrapping
#: (parentheses) was broken in exactly the same way. AI-E10-5: the list is never the contract,
#: so the closure below asserts both directions over every member.
_CONTINUATION_SHAPES: tuple[tuple[str, bool, str, list[CodeEdge], int], ...] = (
    (
        "plain-assign",
        False,
        "def test_shape():\n"  # 1
        "    fake = Mock()\n"  # 2
        "    fake.other.return_value = 1\n"  # 3
        "    fake.extra.return_value = 2\n"  # 4
        "    result = sut(1, 2)\n"  # 5 — bound on ONE physical line
        "    assert result == fake.other()\n",  # 6
        [CodeEdge(callee="Mock", line=2), CodeEdge(callee="sut", line=5),
         CodeEdge(callee="other", line=6)],
        6,
    ),
    (
        "backslash-continuation",
        False,
        "def test_shape():\n"  # 1
        "    fake = Mock()\n"  # 2
        "    fake.other.return_value = 1\n"  # 3
        "    fake.extra.return_value = 2\n"  # 4
        "    result = \\\n"  # 5 — the target and `=` are HERE…
        "        sut(1, 2)\n"  # 6 — …and the 1.4 edge lands HERE
        "    assert result == fake.other()\n",  # 7
        [CodeEdge(callee="Mock", line=2), CodeEdge(callee="sut", line=6),
         CodeEdge(callee="other", line=7)],
        7,
    ),
    (
        "parenthesised-continuation",
        False,
        "def test_shape():\n"  # 1
        "    fake = Mock()\n"  # 2
        "    fake.other.return_value = 1\n"  # 3
        "    fake.extra.return_value = 2\n"  # 4
        "    result = (\n"  # 5 — PEP 8 PREFERS this over the backslash above
        "        sut(1, 2)\n"  # 6
        "    )\n"  # 7
        "    assert result == fake.other()\n",  # 8
        [CodeEdge(callee="Mock", line=2), CodeEdge(callee="sut", line=6),
         CodeEdge(callee="other", line=8)],
        8,
    ),
    (
        "bracket-continuation",
        False,
        "def test_shape():\n"  # 1
        "    fake = Mock()\n"  # 2
        "    fake.other.return_value = 1\n"  # 3
        "    fake.extra.return_value = 2\n"  # 4
        "    results = [\n"  # 5
        "        sut(1, 2)\n"  # 6 — last element, so no trailing comma to give it away
        "    ]\n"  # 7
        "    assert results[0] == fake.other()\n",  # 8
        [CodeEdge(callee="Mock", line=2), CodeEdge(callee="sut", line=6),
         CodeEdge(callee="other", line=8)],
        8,
    ),
    (
        "genuinely-discarded-control",
        True,
        "def test_shape():\n"  # 1
        "    fake = Mock()\n"  # 2
        "    fake.other.return_value = 1\n"  # 3
        "    fake.extra.return_value = 2\n"  # 4
        "    sut(\n"  # 5 — the STATEMENT is the call and nothing else…
        "        1, 2\n"  # 6
        "    )\n"  # 7 — …merely wrapped over three lines
        "    pretended = fake.other()\n"  # 8
        "    assert pretended == 1\n",  # 9
        [CodeEdge(callee="Mock", line=2), CodeEdge(callee="sut", line=5),
         CodeEdge(callee="other", line=8)],
        9,
    ),
)


def test_a_bound_sut_result_is_consumed_however_the_line_is_wrapped() -> None:
    """TC-ArgusAgent-DETECT-001-109 — AC1.3: line wrapping must not manufacture a 🔴.

    THE DEFECT THIS PINS, reproduced before it was fixed (review iteration 2, 2026-08-17)
    ---------------------------------------------------------------------------------
    Fact (b) asked whether the SUT call's result is thrown away by reading the text that
    precedes the call **on the call's own physical line**. That is not the unit Python
    binds a result in. Both of Python's continuation syntaxes put the assignment target on
    an EARLIER line::

        result = (            result = \\
            add(1, 2)             add(1, 2)
        )

    so nothing preceded the call on its own line, the call was scored "result discarded",
    and a test that genuinely CONSTRAINS the real SUT result was promoted to
    verdict-eligible. Measured through the shipped detector, both shapes emitted
    ``vacuous_test_ast`` / ``AUDITED_SHALLOW`` while the byte-for-byte equivalent
    single-line spelling emitted ``vacuous_test_heuristic`` — a build taken to 🔴 by where
    the author pressed Enter. That is the lethal failure class (a false 🔴), it violates
    AC1.3, and the shape is not exotic: PEP 8 explicitly prefers the parenthesised form.

    The fix is the LOGICAL STATEMENT, computed the same way for both syntaxes rather than
    special-casing either — see ``provenance_scan.logical_statement_starts``. This closure
    asserts BOTH directions over ``_CONTINUATION_SHAPES``: the four bound spellings are
    advisory, and the genuinely discarded control (also wrapped, so wrapping alone is not
    what demotes) stays corroborated. Without that fifth row the guard would pass if fact
    (b) were disabled altogether.
    """
    promoted, demoted = [], []
    for name, expect_corroborated, source, edges, end_line in _CONTINUATION_SHAPES:
        defs = [Definition(name="test_shape", kind="function", start_line=1, end_line=end_line)]
        actual = _corroborated(source, defs, edges)
        (promoted if actual else demoted).append(name)
        assert actual is expect_corroborated, (
            f"{name!r}: expected ast_corroborated={expect_corroborated}, got {actual}. "
            "If a BOUND result was corroborated, fact (b) has gone back to reading the "
            "call's own physical line and a false 🔴 is reachable by line-wrapping alone "
            "(AC1.3). If the DISCARDED control was demoted, the predicate was weakened "
            "instead of corrected — recall on the planted cartridges is next."
        )

    # Non-vacuity: the closure must have exercised both directions, not one.
    assert len(demoted) == 4 and len(promoted) == 1, (
        f"the shape table degenerated to one direction (promoted={promoted}, demoted={demoted})"
    )


def test_a_discarded_sut_call_stays_corroborated_across_its_own_wrapping() -> None:
    """TC-ArgusAgent-DETECT-001-110 — the fix does not buy safety by giving up recall.

    The cheap way to close ``-109`` is to score every multi-line statement as consumed.
    That would keep the moat and silently cost the detector every genuinely vacuous test
    whose SUT call happens to be wrapped — a real defect, just an invisible one. So the
    same discarded call is asserted corroborated in three spellings, including one with a
    comment and a blank line inside the call's own parentheses (both of which the scan has
    to skip without losing the statement it is inside).
    """
    for label, source, edges, end_line in (
        (
            "one line",
            "def test_shape():\n"  # 1
            "    sut(1, 2)\n"  # 2
            "    fake = Mock()\n"  # 3
            "    fake.other.return_value = 1\n"  # 4
            "    pretended = fake.other()\n"  # 5
            "    assert pretended == 1\n",  # 6
            [CodeEdge(callee="sut", line=2), CodeEdge(callee="Mock", line=3),
             CodeEdge(callee="other", line=5)],
            6,
        ),
        (
            "wrapped arguments",
            "def test_shape():\n"  # 1
            "    sut(\n"  # 2
            "        1,\n"  # 3
            "        2,\n"  # 4
            "    )\n"  # 5
            "    fake = Mock()\n"  # 6
            "    fake.other.return_value = 1\n"  # 7
            "    pretended = fake.other()\n"  # 8
            "    assert pretended == 1\n",  # 9
            [CodeEdge(callee="sut", line=2), CodeEdge(callee="Mock", line=6),
             CodeEdge(callee="other", line=8)],
            9,
        ),
        (
            "wrapped with a comment and a blank line inside the call",
            "def test_shape():\n"  # 1
            "    sut(\n"  # 2
            "        1,  # the first operand\n"  # 3
            "\n"  # 4
            "        2,\n"  # 5
            "    )\n"  # 6
            "    fake = Mock()\n"  # 7
            "    fake.other.return_value = 1\n"  # 8
            "    pretended = fake.other()\n"  # 9
            "    assert pretended == 1\n",  # 10
            [CodeEdge(callee="sut", line=2), CodeEdge(callee="Mock", line=7),
             CodeEdge(callee="other", line=9)],
            10,
        ),
    ):
        defs = [Definition(name="test_shape", kind="function", start_line=1, end_line=end_line)]
        assert _corroborated(source, defs, edges) is True, (
            f"a genuinely discarded SUT call stopped being corroborated when written as "
            f"{label!r} — the predicate was weakened rather than corrected, and recall on "
            "the planted cartridges is what pays for it"
        )


def test_non_ascii_identifiers_bind_and_corroborate() -> None:
    """TC-ArgusAgent-DETECT-001-108 — name matching is Unicode-safe (the ``nonascii_unicode`` class).

    The ``nonascii_unicode`` cartridge carries a Cyrillic ``тесты/`` directory and a
    ``café_calc.py``; nothing stops a repository from carrying non-ASCII IDENTIFIERS
    too. Any name-level predicate that quietly assumed ASCII would fail closed here —
    silently, and only for those repositories.
    """
    source = (
        "def test_somme_totale_est_vide():\n"  # 1
        "    somme_totale([1, 2, 3])\n"  # 2
        "    поддельный = Mock()\n"  # 3
        "    поддельный.calculer.return_value = 6\n"  # 4
        "    prétendu = поддельный.calculer()\n"  # 5
        "    assert prétendu == 6\n"  # 6
    )
    defs = [
        Definition(name="test_somme_totale_est_vide", kind="function", start_line=1, end_line=6)
    ]
    edges = [
        CodeEdge(callee="somme_totale", line=2),
        CodeEdge(callee="Mock", line=3),
        CodeEdge(callee="calculer", line=5),
    ]
    assert _corroborated(source, defs, edges) is True


# ── Integration cases over the real 1.4 AST substrate (tree-sitter) ──

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.index.ast_index import build_ast_index  # noqa: E402

# RE-AUTHORED 2026-08-17 with `-86` and for the same reason (Story 14.1 / AC4): the
# previous fixture bound the real SUT result (`result = service_call(m, dep)`) and
# asserted it, which under the corrected fact (b) is ADVISORY, not corroborated. This
# is now the shape the planted cartridges carry — the SUT is reached and its result is
# thrown away, while the assertion constrains a value bound from a mock.
_VACUOUS_FIXTURE = """\
from unittest.mock import Mock


def test_vacuous():
    service_call()
    m = Mock()
    m.reply.return_value = 7
    pretended = m.reply()
    assert pretended == 7
"""

# The counterpart the moat is really about, and the reason this pair is asserted
# together: the same mock-heavy setup, but the assertion CONSTRAINS the SUT result.
# It is still flagged by the heuristic; it must never be verdict-eligible.
_SUT_ASSERTING_FIXTURE = """\
from unittest.mock import Mock, MagicMock


def test_asserts_the_sut():
    m = Mock()
    dep = MagicMock()
    result = service_call(m, dep)
    assert result
"""

_GENUINE_FIXTURE = """\
def test_genuine():
    total = add(2, 3)
    assert total == 5
"""


def test_integration_vacuous_flagged_genuine_not(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-94 — over real 1.4 index: vacuous promoted, SUT-asserting demoted, genuine not flagged.

    The three-way discrimination, over the REAL tree-sitter edge set rather than a
    hand-built one — because the whole point of Story 14.1 is that the middle case
    exists at all. Before it, the first two were the same answer.
    """
    (tmp_path / "test_vacuous.py").write_text(_VACUOUS_FIXTURE, encoding="utf-8")
    (tmp_path / "test_sut_asserting.py").write_text(_SUT_ASSERTING_FIXTURE, encoding="utf-8")
    (tmp_path / "test_genuine.py").write_text(_GENUINE_FIXTURE, encoding="utf-8")
    index = build_ast_index(
        tmp_path, ("test_vacuous.py", "test_sut_asserting.py", "test_genuine.py")
    )
    by_path = {e.file_path: e for e in index.entries}

    detector = VacuousTestDetector()

    vac = detector.run(
        file_path="test_vacuous.py",
        source=_VACUOUS_FIXTURE,
        ast_entry=by_path["test_vacuous.py"],
    )
    assert len(vac.findings) == 1
    assert vac.findings[0].rule_id == RULE_AST  # corroborated over the real edge set
    assert vac.findings[0].depth_supported is CoverageDepth.AUDITED_SHALLOW

    demoted = detector.run(
        file_path="test_sut_asserting.py",
        source=_SUT_ASSERTING_FIXTURE,
        ast_entry=by_path["test_sut_asserting.py"],
    )
    assert len(demoted.findings) == 1  # flagged by the (unchanged) heuristic…
    assert demoted.findings[0].rule_id == RULE_HEURISTIC  # …and NOT verdict-eligible
    assert demoted.findings[0].depth_supported is None

    gen = detector.run(
        file_path="test_genuine.py",
        source=_GENUINE_FIXTURE,
        ast_entry=by_path["test_genuine.py"],
    )
    assert gen.findings == ()  # genuine test NOT flagged
