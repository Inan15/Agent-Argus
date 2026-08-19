"""Vacuous-test detector cases over the REAL Story-1.4 tree-sitter substrate.

Verification area ArgusAgent-DETECT (TC-ArgusAgent-DETECT-001-NN). Split out of
``tests/test_vacuous_detector.py`` by Story 15.2 (``DN-15-2-1``), which needed room to add
the line-numbering-contract cases and found the module at **1,161 of NFR-M1's 1,200**. The
remedy for a full guard module is a COHESION SPLIT — never a shave and never an
``_EXEMPT_BY_DESIGN`` entry (``tests/test_module_size_ceiling.py::_REMEDY``;
``MAINT-001-04``, whose registry may only shrink).

What this module is about
-------------------------
Cases that stand up the **real** Story-1.4 tree-sitter substrate — the index is built from a
fixture on disk by :func:`~argus.index.ast_index.build_ast_index`, and the edge set is
whatever that index actually emits — plus the occurrence-resolution family that shares those
fixtures. The retained module keeps the cases that construct an ``AstIndexEntry`` **by
hand**.

⛔ **The boundary is not invented here.** The original module's own docstring already drew
it: *"The pure-logic cases construct an ``AstIndexEntry`` directly; the integration cases
build it from a real tiny fixture via ``build_ast_index``."* The split makes an
already-stated distinction physical, which is why it is a subject boundary and not an
arithmetic one.

Why the boundary is where it is, and the alternatives that were REJECTED
-----------------------------------------------------------------------
``_REMEDY`` requires this docstring to say why the module exists, so the rejected boundaries
are recorded here rather than in a commit message:

1. **REJECTED — splitting at the ``-111``/``-112`` pair**, so that this module would hold
   only the cases that literally call ``build_ast_index``. It splits the
   ``_REPEATED_CALLEE_SHAPES`` family across the boundary and separates ``-112`` from the
   guard it exists to pin: ``-112`` is pure logic, but it shares ``_DUP_HEAD`` with ``-111``
   and exists specifically to prove ``-111``'s order-invariance. Separating them splits one
   subject in half.
2. **REJECTED — splitting by id range** (``-85``..``-100`` here, ``-101``..``-112`` there).
   An id range is an **arithmetic** boundary, not a subject boundary — the choice ``_REMEDY``
   forbids by name. Two cases with consecutive ids routinely test unrelated things.

``_grammars_or_unevaluable()`` travels **with** these cases and is deliberately absent from
the retained module: measured at the split, no case remaining there needs tree-sitter at all.
It stays a NAMED ``UNEVALUABLE`` failure raised at **import** time, never a skip —
``audit-ci.yml`` sets ``ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`` and ``importorskip`` ignores that
variable (``DF-14-2-A``). Splitting at ``-111`` instead of here would have separated ``-111``
from that guard and reintroduced exactly the false green ``DF-14-2-A`` records.
"""

from __future__ import annotations

import importlib.util
from fractions import Fraction
from pathlib import Path

import pytest

from argus.detectors.provenance_scan import provenance_evidence
from argus.detectors.vacuous_test import (
    # The FROZEN vocabulary, because the cases below exercise the CORROBORATION path and
    # that is the table production hands it (Story 14.2 / DN-14-2-1). Passing the widened
    # `_ASSERTION_CALLEES` here would score a configuration the detector never runs.
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
    RULE_AST,
    RULE_HEURISTIC,
    VacuousTestDetector,
    VacuousTestScore,
    _edges_in_span,
    index_aligned_lines,
)
from argus.index.ast_index import AstIndexEntry, CodeEdge, Definition
from argus.ledger.coverage_ledger import CoverageDepth
from argus.pipeline_stages import _read_source


# ── Integration cases over the real 1.4 AST substrate (tree-sitter) ──


def _grammars_or_unevaluable() -> None:
    """Assert the Python grammar is present as a NAMED outcome, never a skip (`DF-14-2-B`'s twin).

    ⛔ These two lines were ``pytest.importorskip``, and that was a FALSE GREEN
    (``DF-14-2-A``, filed by Story 14.2 against this module, discharged by Story 14.3).
    ``audit-ci.yml`` sets ``ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`` so a missing grammar cannot be
    answered with a skip — and ``importorskip`` **ignores that variable**. Had either package
    gone missing in CI, roughly forty fact-(b) guards **including the moat's own
    false-accusation guard** would have reported SKIPPED and the run would have read green.

    ⚠️ **Re-derived at Story 15.2's cohesion split, because the split changed what this guard
    protects and the old wording had become false.** It named ``-88`` as the moat guard at
    risk; ``-88`` is PURE-LOGIC and stayed in ``tests/test_vacuous_detector.py``, which needs
    no grammar, so a missing grammar no longer silences it. The moat guard that IS at risk
    here is **``TC-ArgusAgent-DETECT-001-94``** — the integration false-accusation case, which
    asserts a genuine well-asserting test is not flagged **over the real index**. The hazard is
    unchanged in kind and the id had to move with it.

    These are **BASE** dependencies (``pyproject.toml`` promoted them out of the optional
    ``[languages]`` extra), so "absent" is a broken environment, not a supported one. Raised
    at import time on purpose: it fails COLLECTION, which reads RED where a skip reads green.
    """
    missing = [
        name
        for name in ("tree_sitter", "tree_sitter_python")
        if importlib.util.find_spec(name) is None
    ]
    if missing:
        pytest.fail(
            f"UNEVALUABLE: {', '.join(missing)} is not importable, so none of the "
            "integration cases below — including the integration false-accusation moat "
            "guard TC-ArgusAgent-DETECT-001-94 — measured anything. These are BASE dependencies, "
            "not the optional `[languages]` extra. Reported as a FAILURE and never a skip "
            "(Story 14.3 / AC7.6): a skip here would read as green."
        )


_grammars_or_unevaluable()

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


# ── The SAME callee called more than once on ONE physical line (review iteration 3) ──

#: A body prefix that is heuristically vacuous for a reason none of the rows below can
#: change: four setup statements against one assertion puts the density at or under 1/5,
#: beneath the 1/4 floor. Three mock constructions are deliberate — a two-mock fixture
#: never clears the STRICT `> 1/2` mock ceiling against two SUT calls, which is what makes
#: this shape family easy to probe for and conclude, wrongly, that it is already safe.
_DUP_HEAD = (
    "from unittest.mock import MagicMock\n"  # 1
    "\n"  # 2
    "\n"  # 3
    "def test_shape():\n"  # 4
    "    fake = MagicMock()\n"  # 5
    "    second = MagicMock()\n"  # 6
    "    third = MagicMock()\n"  # 7
    "    fake.other.return_value = 7\n"  # 8
)

#: One callee, called TWICE, with the two calls placed relative to each other in every way
#: that matters. The 1.4 index gives `(callee, line)` and NO column, so each of these emits
#: two `CodeEdge`s that are INDISTINGUISHABLE — which is exactly why the classification has
#: to consume a distinct textual occurrence per edge instead of re-reading the first one.
#: Both directions are present: two rows must STAY corroborated, so a predicate that bought
#: safety by demoting every repeated callee would fail here rather than pass.
_REPEATED_CALLEE_SHAPES: tuple[tuple[str, bool, str], ...] = (
    (
        # THE DEFECT. `captured` is bound to the real `sut(3, 4)` result and the assertion
        # constrains it against a mock — a genuine test, and a false 🔴 before the fix.
        "semicolon-compound-bound",
        False,
        "    sut(1, 2); captured = sut(3, 4)\n    assert captured == fake.other()\n",
    ),
    (
        # The same two statements in the other order, so the fix cannot be an artefact of
        # which occurrence happens to come first.
        "semicolon-compound-bound-first",
        False,
        "    captured = sut(3, 4); sut(1, 2)\n    assert captured == fake.other()\n",
    ),
    (
        # The control: byte-identical semantics, one newline more. It was already advisory,
        # and it is what makes the row above a LAYOUT-dependent verdict rather than a
        # difference of opinion about the test.
        "two-line-bound-control",
        False,
        "    sut(1, 2)\n    captured = sut(3, 4)\n    assert captured == fake.other()\n",
    ),
    (
        # RECALL, on the same shape: both results really are thrown away, so the semicolon
        # must not cost the detector the finding.
        "semicolon-compound-discarded",
        True,
        "    sut(1, 2); sut(3, 4)\n    assert fake.other() == 7\n",
    ),
    (
        "two-line-discarded-control",
        True,
        "    sut(1, 2)\n    sut(3, 4)\n    assert fake.other() == 7\n",
    ),
    (
        # Neighbouring shapes that put the callee twice on one line by other means.
        "comprehension-repeated-callee",
        False,
        "    xs = [sut(1), sut(2)]\n    assert xs[0] == fake.other()\n",
    ),
    (
        "nested-call-bound",
        False,
        "    captured = sut(sut(1, 2), 3)\n    assert captured == fake.other()\n",
    ),
    (
        # CONSERVATIVE BY CONSTRUCTION, and it moved with this fix: the inner call's result
        # is consumed — by the outer call — so fact (b)'s "no SUT result is consumed"
        # clause genuinely fails once the two occurrences are told apart. Before the fix
        # both edges read the OUTER occurrence and this corroborated. Recorded as a row
        # rather than left implicit, because it is a recall change and it is in the safe
        # direction (a real vacuous test left advisory is tolerable; a false 🔴 is not).
        "nested-call-discarded",
        False,
        "    sut(sut(1, 2), 3)\n    assert fake.other() == 7\n",
    ),
    (
        "chained-then-bound",
        False,
        "    sut(1, 2).thing(); captured = sut(3, 4)\n    assert captured == fake.other()\n",
    ),
)


def _corroborated_over_real_index(root: Path, source: str, name: str) -> bool:
    """Score *source* through the REAL tree-sitter index — the edges are not hand-built.

    This family cannot be honestly tested from a hand-written edge list: the whole claim
    is about what the 1.4 index actually emits for two calls to one name on one line, and
    a hand-built list is the tester asserting their own belief about that.
    """
    relative = f"test_{name.replace('-', '_')}.py"
    (root / relative).write_text(source, encoding="utf-8")
    index = build_ast_index(root, (relative,))
    entry = {e.file_path: e for e in index.entries}[relative]
    result = VacuousTestDetector().run(file_path=relative, source=source, ast_entry=entry)
    assert len(result.findings) == 1, (
        f"{name!r} was not flagged by the (unchanged) heuristic at all, so it cannot "
        "measure anything about PROMOTION — repair the fixture, not the predicate"
    )
    return result.findings[0].rule_id == RULE_AST


def test_a_repeated_callee_on_one_line_is_resolved_per_occurrence(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-111 — AC1.3: a semicolon must not manufacture a 🔴.

    THE DEFECT THIS PINS, reproduced before it was fixed (review iteration 3, 2026-08-17)
    ---------------------------------------------------------------------------------
    ``provenance_scan._locate_call`` found the call site with an unconditional
    ``pattern.search()``, which always returns the FIRST ``callee(`` on the physical line.
    ``CodeEdge`` carries ``(callee, line)`` and no column, so when one callee is called
    twice on ONE line, BOTH edges were classified from the FIRST occurrence's text — and a
    later, genuinely BOUND call inherited the first one's "nothing precedes it, so the
    result was thrown away" verdict::

        sut(1, 2); captured = sut(3, 4)
        assert captured == fake.other()

    Measured through the shipped detector over the REAL tree-sitter index, that scored
    ``discarded=2, consumed=0`` → ``vacuous_test_ast`` / ``AUDITED_SHALLOW``, while the
    byte-equivalent two-line spelling stayed advisory. A genuine test, taken to 🔴 by a
    semicolon. This is the same lethal class as ``-109``'s continuation defect reached by a
    different mechanism — column-blind OCCURRENCE resolution, not statement boundaries —
    and none of ``-101``..``-110`` or ``-116`` repeated a callee name on one line.

    The fix gives each edge for a ``(line, callee)`` pair its OWN occurrence, by resuming
    the search past the end of the previous match for that pair, and judges the SIMPLE
    statement (``;``-delimited) containing it. No column was added to the 1.4 ``CodeEdge``:
    that index is read by the orphan/dead-code detector too, and this story does not own it.
    """
    promoted, demoted = [], []
    for name, expect_corroborated, body in _REPEATED_CALLEE_SHAPES:
        actual = _corroborated_over_real_index(tmp_path, _DUP_HEAD + body, name)
        (promoted if actual else demoted).append(name)
        assert actual is expect_corroborated, (
            f"{name!r}: expected ast_corroborated={expect_corroborated}, got {actual}. "
            "If a BOUND result was corroborated, every edge for a (line, callee) pair is "
            "again reading the FIRST occurrence's text and a false 🔴 is reachable by "
            "writing two calls on one line (AC1.3). If a DISCARDED row was demoted, the "
            "predicate was weakened instead of corrected — cartridge recall is what pays."
        )

    # Non-vacuity: the table must have exercised both answers, not one.
    assert len(promoted) == 2 and len(demoted) == 7, (
        f"the shape table degenerated to one direction (promoted={promoted}, demoted={demoted})"
    )


def test_repeated_callee_evidence_does_not_depend_on_edge_order() -> None:
    """TC-ArgusAgent-DETECT-001-112 — the fix must NOT rest on the index's edge order.

    WHY THIS EXISTS AS ITS OWN GUARD
    ---------------------------------
    The suggested fix came with a premise: *"tree-sitter emits call edges in traversal
    (left-to-right, source) order, so resuming the search past the previous match recovers
    the correct occurrence."* **That premise is FALSE for this index, and was measured so
    rather than assumed.** ``ast_index._extract`` walks with ``stack.pop()`` /
    ``stack.extend(children)``, which visits siblings RIGHT to LEFT, and the AR11 sort key
    ``(line, callee)`` is stable — so two edges for one ``(callee, line)`` pair arrive in
    REVERSE source order::

        alpha(1); beta(2); gamma(3)   ->  raw traversal: gamma, beta, alpha

    The fix does not need the premise, and this pins WHY: ``ProvenanceEvidence`` aggregates
    COUNTS, and each edge's classification is a pure function of the occurrence assigned to
    it. Any one-to-one assignment of k edges to the k occurrences therefore yields the same
    multiset of classifications and the same counts. What the fix must guarantee is that the
    occurrences are DISTINCT — not that they are in order. Asserting the invariance directly
    is the difference between a fix that works and a fix that happens to work.
    """
    source = _DUP_HEAD + "    sut(1, 2); captured = sut(3, 4)\n    assert captured == fake.other()\n"
    lines = source.splitlines()
    forward = [CodeEdge(callee="MagicMock", line=n) for n in (5, 6, 7)] + [
        CodeEdge(callee="sut", line=9),
        CodeEdge(callee="sut", line=9),
        CodeEdge(callee="other", line=10),
    ]
    reverse = list(reversed(forward))

    evidence = [
        provenance_evidence(
            lines,
            edges,
            4,
            10,
            assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
            mock_callees=_MOCK_CALLEES,
        )
        for edges in (forward, reverse)
    ]

    assert evidence[0] == evidence[1], (
        f"the evidence changed with the order of two indistinguishable edges: "
        f"{evidence[0]} vs {evidence[1]}. Occurrence resolution has become order-DEPENDENT, "
        "and the index does not emit these in source order (see the docstring) — so this is "
        "a real misclassification, not a theoretical one."
    )
    # …and it is the RIGHT pair of counts, not merely a stable one: one call's result is
    # thrown away, the other's is bound. A fix that scored both the same way would be
    # order-invariant too, and wrong.
    assert (evidence[0].discarded_sut_calls, evidence[0].consumed_sut_calls) == (1, 1)
    assert evidence[0].sut_result_is_discarded is False


# -- Story 15.2: the LINE-NUMBERING CONTRACT between the detector and the 1.4 index --

#: The eight characters ``str.splitlines()`` treats as line breaks, the Story 1.4 index does
#: **not** count as line breaks, and the production read path does **not** normalise away.
#: Each occurrence shifts the detector's view of the source and silently drops the LAST line
#: off the scored span -- which, in a conventionally written test, is where the assertions are.
#: Declared as DATA and not as eight hand-written functions, on the ``_CONTINUATION_SHAPES`` /
#: ``_REPEATED_CALLEE_SHAPES`` precedent: the defect is a CLASS, and a hand-picked pair would
#: have missed the half nobody thought of.
#:
#: (X) This tuple is a MEASUREMENT, never the contract. The fix is newline-based *by
#: construction* (:func:`~argus.detectors.vacuous_test.index_aligned_lines`), so a ninth exotic
#: separator is handled by a mechanism nobody has to remember. If this list were the mechanism,
#: the ninth separator would be a fresh false accusation waiting for someone to notice it.
_INDEX_DESYNC_SEPARATORS: tuple[tuple[str, str], ...] = (
    ("VT", "\x0b"),
    ("FF", "\x0c"),
    ("FS", "\x1c"),
    ("GS", "\x1d"),
    ("RS", "\x1e"),
    ("NEL", "\x85"),
    ("LS", "\u2028"),
    ("PS", "\u2029"),
)

#: The two that CANNOT reach the detector, because ``read_text``'s universal-newline decoding
#: at ``argus/pipeline_stages.py:124`` collapses them to ``\n`` BEFORE the detector exists.
#: They are measured too (AC3.2) -- to establish the NORMALISATION, not a desync. That property
#: belongs to ``pipeline_stages``, so a guard asserting it must go through the read path; a
#: guard that normalises its own input asserts nothing, which was exactly ``-118``'s defect.
_READ_PATH_NORMALISED_TERMINATORS: tuple[tuple[str, str], ...] = (("CR", "\r"), ("CRLF", "\r\n"))

#: A genuine, MOCK-FREE, fully-asserted ten-line test: nine body statements, three bare
#: asserts, density 1/3 -- comfortably clear of the 1/4 floor. Separators go in a TRAILING
#: COMMENT on line 1, so the file's meaning is byte-identical however many are inserted and the
#: only variable is the decomposition. This rides the DENSITY floor rather than the mock ratio
#: (Story 15.2 / 0.14): the two shapes reach a flag by different routes and BOTH matter.
_CONTRACT_FIXTURE = (
    "def test_addition():  # trailing comment{separators}\n"
    "    a = 1\n"
    "    b = 2\n"
    "    c = a + b\n"
    "    d = c * 2\n"
    "    e = d - 1\n"
    "    f = e + 0\n"
    "    assert c == 3\n"
    "    assert d == 6\n"
    "    assert e == 5\n"
)

#: The same shape with the assertions removed: genuinely vacuous, and it must STAY flagged.
#: Without it, a "fix" that simply stopped flagging anything would pass every row above.
_CONTRACT_FIXTURE_VACUOUS = (
    "def test_addition():  # trailing comment{separators}\n"
    "    a = 1\n"
    "    b = 2\n"
    "    c = a + b\n"
    "    d = c * 2\n"
    "    e = d - 1\n"
    "    f = e + 0\n"
    "    g = f + 1\n"
    "    h = g + 1\n"
    "    i = h + 1\n"
)


def _score_through_the_read_path(
    root: Path, source: str, slug: str
) -> tuple[VacuousTestScore, str, AstIndexEntry, Definition]:
    """Score *source* the way PRODUCTION does: bytes on disk -> read path -> real index -> score.

    Every step of the production path is used and none is simulated. (X) The bytes are written
    with an explicit ``encoding="utf-8"`` and ``newline=""`` and are then ASSERTED (AC11.3):
    ``\\x85`` is one byte in latin-1 and two in UTF-8, ``\\u2028`` / ``\\u2029`` are three, and
    ``write_text(newline=None)`` rewrites ``\\n`` -> ``\\r\\n`` on Windows and not on Linux --
    the exact defect that made ``-118`` weak. A fixture that does not assert its own bytes means
    something different on the two platforms this repository ships to.
    """
    relative = f"tests/test_{slug}.py"
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8", newline="")
    assert target.read_bytes() == source.encode("utf-8"), (
        f"{slug!r} was not written as the bytes it claims -- the platform rewrote something, "
        f"which is how a terminator guard comes to measure nothing: {ascii(source)[:120]}"
    )
    read_back = _read_source(root, relative)
    index = build_ast_index(root, (relative,))
    entry = {e.file_path: e for e in index.entries}[relative]
    assert not entry.parse_failed and entry.ast_eligible, f"{slug!r} did not parse"
    definitions = [d for d in entry.definitions if d.name.startswith("test")]
    assert len(definitions) == 1, f"{slug!r} must hold exactly one test function"
    definition = definitions[0]
    score = VacuousTestDetector()._score(
        index_aligned_lines(read_back), entry.edges, definition
    )
    return score, read_back, entry, definition


def test_an_exotic_separator_cannot_shift_the_scored_span(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-134 -- AC2/AC3: the detector's lines ARE the index's lines.

    THE DEFECT THIS PINS, reproduced RED before the fix (Story 15.2, 2026-08-19)
    --------------------------------------------------------------------------
    ``run()`` scored ``source.splitlines()`` while the Story 1.4 index numbers lines by
    NEWLINE. ``splitlines()`` splits on eleven things. Eight of them survive the production
    read path, so every occurrence made the detector's list one element longer than the index's
    -- and because the detector recovers a span's TEXT by ``source_lines[n - 1]``, its view slid
    backwards and the span lost its LAST line. Measured on this exact fixture through the real
    index, varying only the number of form feeds in a line-1 comment::

        form feeds | assertion_sites | statements | density | heuristically_vacuous
        -----------+-----------------+------------+---------+----------------------
             0     |        3        |     9      |   1/3   | False  -- correct
             1     |        2        |     8      |   1/4   | False  -- ON the floor
             2     |        1        |     7      |   1/7   | True   -- FALSE ACCUSATION
             3     |        0        |     6      |    0    | True   -- FALSE ACCUSATION

    A fully-asserted, mock-free, genuine test accused of asserting nothing because of an
    invisible character in a comment. **The RED was OBSERVED for all eight separators before
    the fix landed** (Story 15.2 Debug Log), not predicted.

    Why this asserts the whole score and not the flag
    -------------------------------------------------
    ``VacuousTestScore`` is compared field by field against the CONTROL's, so a scorer that
    agreed on the verdict while disagreeing on the arithmetic that produced it still fails --
    and the arithmetic is what moves first (at one separator the density lands exactly ON the
    floor and the flag does NOT move, while three assertion sites have already become two).
    The control's own values are pinned too, so the comparison cannot degenerate into two equal
    wrong answers.

    AC9.3 -- the preconditions that make this meaningful, each ASSERTED rather than assumed:
    the separator really did survive to the detector; the two decompositions really do disagree
    on this input; the index really did NOT treat it as a line break; the parse really
    succeeded. AC3.3 -- BOTH directions: the genuine fixture must stay unflagged and the
    vacuous one must stay flagged, so a "fix" that bought safety by flagging nothing fails here
    rather than passing.

    MUTATION OBSERVED TO REDDEN IT (AC9.1): reverting ``run()``'s decomposition to
    ``source.splitlines()`` -- i.e. the shipped code at HEAD ``72a95ef`` -- reddens 24 of the
    24 separator rows.
    """
    control, control_text, _, control_definition = _score_through_the_read_path(
        tmp_path, _CONTRACT_FIXTURE.format(separators=""), "contract_control"
    )
    # The control is the INTERESTING case, not a degenerate one: a genuine test, comfortably
    # clear of the floor, which the detector must leave alone.
    assert control.heuristically_vacuous is False
    assert (control.assertion_sites, control.statement_count) == (3, 9)
    assert control.assertion_density == Fraction(1, 3)
    assert (control_definition.start_line, control_definition.end_line) == (1, 10)
    assert "\x0c" not in control_text  # the control really is separator-free

    for name, separator in _INDEX_DESYNC_SEPARATORS:
        for count in (1, 2, 3):
            slug = f"contract_{name.lower()}_{count}"
            score, text, _entry, definition = _score_through_the_read_path(
                tmp_path, _CONTRACT_FIXTURE.format(separators=separator * count), slug
            )
            # PRECONDITION 1 -- the separator really did survive the read path. Without this
            # the row could pass by the character having been normalised away, which is
            # precisely how `-107` and `-118` came to assert nothing.
            assert text.count(separator) == count, (
                f"{name} ({ascii(separator)}) did not survive the read path intact, so this "
                f"row measured nothing: found {text.count(separator)}, expected {count}"
            )
            # PRECONDITION 2 -- the two decompositions really DO disagree on this input. This
            # is the `a != b` that `-107` never asserted at the seam it varied.
            assert len(text.splitlines()) == text.count("\n") + count, (
                f"{name} ({ascii(separator)}) does not desynchronise splitlines() from the "
                f"newline count on this fixture ({len(text.splitlines())} vs "
                f"{text.count(chr(10))}), so this row is not exercising the contract"
            )
            # PRECONDITION 3 -- the INDEX did not treat it as a line break. The span being the
            # control's span is what makes a differing score the DETECTOR's fault.
            assert (definition.start_line, definition.end_line) == (1, 10), (
                f"{name} ({ascii(separator)}) moved the INDEX's span to "
                f"({definition.start_line}, {definition.end_line}); this guard is about the "
                "detector disagreeing with the index, not about the index moving"
            )
            # THE CONTRACT.
            assert score == control, (
                f"{count}x {name} ({ascii(separator)}) changed the score of a byte-equivalent "
                f"genuine test: {score} vs control {control}. The detector's line "
                "decomposition must BE the index's line decomposition."
            )

    # The OTHER direction: a genuinely vacuous test stays flagged, with and without the
    # separators. A fix that stopped flagging would satisfy every assertion above.
    vacuous_control, _, _, _ = _score_through_the_read_path(
        tmp_path, _CONTRACT_FIXTURE_VACUOUS.format(separators=""), "contract_vacuous_control"
    )
    assert vacuous_control.heuristically_vacuous is True
    assert vacuous_control.assertion_sites == 0
    for name, separator in _INDEX_DESYNC_SEPARATORS:
        vacuous, _, _, _ = _score_through_the_read_path(
            tmp_path,
            _CONTRACT_FIXTURE_VACUOUS.format(separators=separator * 2),
            f"contract_vacuous_{name.lower()}",
        )
        assert vacuous == vacuous_control, (
            f"2x {name} ({ascii(separator)}) changed the score of a genuinely vacuous test: "
            f"{vacuous} vs {vacuous_control}"
        )
        assert vacuous.heuristically_vacuous is True, (
            f"the detector stopped flagging a genuinely vacuous test under {name} "
            f"({ascii(separator)}) -- safety bought by blindness is not safety"
        )


def test_cr_and_crlf_are_normalised_by_the_read_path_not_the_detector(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-135 -- AC3.2: WHY CR and CRLF are not part of the problem.

    ``-107`` and ``-118`` were both named for line terminators and neither could fail, for one
    shared reason: **the CRLF property they assert is true by construction.**
    ``read_text(encoding="utf-8", errors="replace")`` at ``argus/pipeline_stages.py:124`` uses
    universal-newline decoding, so ``\\r`` and ``\\r\\n`` become ``\\n`` before the detector
    exists -- after which any two decompositions of them agree trivially.

    That normalisation is a property of ``pipeline_stages``, **not** of the detector. So this
    guard writes the terminators as BYTES, asserts the bytes it wrote, and reads them back
    through the production read path -- the thing ``-107`` (which called ``splitlines()`` on its
    own fixture, erasing the variable it was varying) and ``-118`` (which scored the in-memory
    string it never wrote) both failed to do. Establishing this BY EXECUTION is what licenses
    Story 15.2's scope decision that the eight, and not the ten, are the problem.

    A MEASURED ASYMMETRY, recorded rather than stepped around
    ---------------------------------------------------------
    The two arms are not symmetric at the INDEX, and finding that out is part of what this
    guard is for. ``build_ast_index`` reads the file itself rather than through
    ``_read_source``, and tree-sitter's Python grammar does not accept a lone ``\r`` as a line
    break -- so a **CR-only** file is numbered as ONE line by the index while ``_read_source``
    reads the very same bytes as ten. The contract still HOLDS (the detector scores the line
    the index numbered) and the outcome is the safe one: that single line holds no statements,
    so the file degrades to no flag rather than to an accusation. Both facts are asserted
    below. The divergence itself lives in ``argus/index/`` and belongs to the index's own
    reader, not to this contract; CR-only source is classic-Mac-era and occurs nowhere in the
    audited population. Out of scope for Story 15.2, written down so the next reader meets it
    as a recorded measurement instead of a mystery.

    MUTATION OBSERVED TO REDDEN IT (AC9.1): replacing ``_read_source``'s
    ``read_text(encoding="utf-8", errors="replace")`` with
    ``read_bytes().decode("utf-8", "replace")`` -- which does NOT do universal newlines -- leaves
    ``\\r`` in ``read_back`` and reddens the normalisation assertion below.
    """
    lf_source = _CONTRACT_FIXTURE.format(separators="")
    lf_score, lf_text, _, _ = _score_through_the_read_path(tmp_path, lf_source, "terminator_lf")
    assert "\r" not in lf_text

    for name, terminator in _READ_PATH_NORMALISED_TERMINATORS:
        source = lf_source.replace("\n", terminator)
        relative = f"tests/test_terminator_{name.lower()}.py"
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        # (X) write_bytes, never write_text(newline=None): on Windows the latter writes the
        # "LF" arm as CRLF and the "CRLF" arm as `\r\r\n`, which is exactly how `-118` came to
        # have an arm that could not fail. The bytes are then ASSERTED, on both platforms.
        target.write_bytes(source.encode("utf-8"))
        written = target.read_bytes()
        assert written.count(b"\r") == source.count("\r") > 0, (
            f"the {name} arm was not written with the terminator it claims: "
            f"{written.count(bytes([13]))} CR bytes on disk, expected {source.count(chr(13))}"
        )
        assert terminator.encode("utf-8") in written, (
            f"the {name} arm does not contain {ascii(terminator)} on disk, so it measures nothing"
        )

        read_back = _read_source(tmp_path, relative)
        # THE NORMALISATION, asserted DIRECTLY rather than inferred from an equality that
        # would also hold if nothing had happened.
        assert "\r" not in read_back, (
            f"{ascii(terminator)} reached the detector as-is; the read path at "
            "argus/pipeline_stages.py:124 is supposed to normalise it to a newline, and the "
            "scope of Story 15.2 rests on exactly that"
        )
        assert read_back == lf_text, (
            f"the {name} arm did not normalise to the same text as the LF arm: "
            f"{ascii(read_back[:80])} vs {ascii(lf_text[:80])}"
        )
        # ...and only THEN the consequence for the score -- against the span the INDEX
        # actually returned for these bytes, which is the whole point of the contract.
        index = build_ast_index(tmp_path, (relative,))
        entry = {e.file_path: e for e in index.entries}[relative]
        definition = [d for d in entry.definitions if d.name.startswith("test")][0]
        score = VacuousTestDetector()._score(
            index_aligned_lines(read_back), entry.edges, definition
        )
        if name == "CR":
            # THE MEASURED ASYMMETRY (see the docstring): tree-sitter reads the file itself
            # and does not accept a lone CR as a line break, so the INDEX numbers a CR-only
            # file as ONE line while the read path reads ten. Pinned as the precondition that
            # makes the next two assertions meaningful, rather than stepped around.
            assert (definition.start_line, definition.end_line) == (1, 1), (
                "a CR-only file is expected to come back from the 1.4 index as a SINGLE line; "
                f"it now spans ({definition.start_line}, {definition.end_line}), so this arm "
                "must be re-derived rather than left asserting the old shape"
            )
            # The detector still honours the contract -- it scores the one line the index
            # numbered -- and the outcome is the SAFE one: no statements, so no flag.
            assert score.statement_count == 0 and score.heuristically_vacuous is False, (
                f"the CR-only arm produced {score}; a span the index could not resolve into "
                "lines must degrade to no flag, never to an accusation"
            )
            continue
        assert (definition.start_line, definition.end_line) == (1, 10)
        assert score == lf_score, f"the {name} arm scored differently: {score} vs {lf_score}"


def test_the_contract_decomposition_is_inert_on_newline_only_source() -> None:
    """TC-ArgusAgent-DETECT-001-136 -- AC4.1: the fix changes NOTHING on ordinary source.

    The corrected decomposition changes what ``_score`` reads for **every** file, not only
    pathological ones, so the burden is to show it is byte-identical to ``splitlines()``
    wherever no exotic separator occurs -- which, per Story 15.2's corpus scan, is the entire
    audited population. Demonstrated over **every tracked ``.py`` file in this repository**
    rather than over a sample: 219 at the time of writing. The count is re-derived each run and
    only floored, never pinned, because pinning it would make this guard fail for the wrong
    reason every time a module is added.

    (X) THE TRAP, asserted rather than left unmentioned: ``"a\\nb\\n".split("\\n")`` is
    ``['a', 'b', '']`` -- a phantom trailing element ``splitlines()`` does not produce, which
    would have added a spurious final line to every span in the repository. The guard pins that
    difference, so an implementation "simplified" to a bare ``split`` reddens here.

    MUTATION OBSERVED TO REDDEN IT (AC9.1): deleting the trailing-empty pop from
    :func:`~argus.detectors.vacuous_test.index_aligned_lines` reddens both the edge-case table
    and the tracked-tree sweep on the first file that ends with a newline.
    """
    edge_cases = ("", "\n", "a", "a\n", "a\nb", "a\nb\n", "\n\n", "a\n\n", "\na")
    for text in edge_cases:
        assert index_aligned_lines(text) == text.splitlines(), (
            f"the contract decomposition disagrees with splitlines() on {ascii(text)}: "
            f"{index_aligned_lines(text)} vs {text.splitlines()}"
        )
    # The naive spelling really IS different -- otherwise the pop would be dead code and this
    # guard would be pinning nothing.
    assert "a\nb\n".split("\n") == ["a", "b", ""]
    assert index_aligned_lines("a\nb\n") != "a\nb\n".split("\n")

    repository_root = Path(__file__).resolve().parent.parent
    scanned = 0
    for path in sorted(repository_root.rglob("*.py")):
        if any(part in {".git", "node_modules", "__pycache__", ".venv"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        scanned += 1
        assert index_aligned_lines(text) == text.splitlines(), (
            f"{path.name} decomposes differently under the contract than under splitlines(), "
            "so the change is NOT inert on ordinary source and must not ship"
        )
    assert scanned > 200, (
        f"only {scanned} Python files were swept, so this guard did not cover the population "
        "it claims to -- a sweep that passes over nothing is the failure mode it exists to avoid"
    )


#: A fixture that reaches the CORROBORATION path, which the density-floor fixtures above
#: cannot: fact (a) needs at least one candidate SUT call, and a mock-free body has none, so
#: `_ast_corroborated` returns before fact (b) is ever evaluated. Three mock constructions are
#: deliberate and load-bearing -- a two-mock fixture sits exactly ON the strict `> 1/2` mock
#: ceiling against two SUT calls and fires nothing, which is what makes this shape family easy
#: to probe and conclude, wrongly, that it is already safe. Both SUT results are discarded and
#: the assertion constrains a mock-bound name, so this is corroborated (verdict-eligible) at
#: HEAD; the separator is what must not change that.
_CORROBORATED_FIXTURE = (
    "from unittest.mock import MagicMock  # trailing comment{separators}\n"
    "\n"
    "\n"
    "def test_shape():\n"
    "    fake = MagicMock()\n"
    "    second = MagicMock()\n"
    "    third = MagicMock()\n"
    "    fake.other.return_value = 7\n"
    "    sut(1, 2)\n"
    "    sut(3, 4)\n"
    "    assert fake.other() == 7\n"
)


def test_corroboration_is_identical_across_the_line_decomposition_seam(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-107 -- fact (b) must not depend on how lines were cut.

    RE-AUTHORED 2026-08-19 by Story 15.2, `-86`-style: an INTENDED behaviour change with the
    reason recorded, never an assertion adjusted until it matched output.

    WHAT THE OLD GUARD CLAIMED, AND WHY IT COULD NOT FAIL
    ----------------------------------------------------
    It was called ``test_score_is_identical_on_CRLF_and_LF_source`` and claimed *"the predicate
    reads SOURCE LINES, so line endings must not matter."* It built a CRLF fixture, asserted
    ``"\r\n" in crlf`` -- and then did this::

        lf_score   = detector._score(lf.splitlines(),   edges, defn)
        crlf_score = detector._score(crlf.splitlines(), edges, defn)
        assert lf_score == crlf_score

    ``"a\r\nb".splitlines() == "a\nb".splitlines()`` is ``True``. The guard threw the CRLF away
    in the very expression that fed the code under test, so both calls received the same list,
    the same edges and the same definition. ``_score`` is pure. The headline assertion was
    ``f(x) == f(x)`` and **no line-ending defect could ever have falsified it.** Its only other
    live assertion, ``ast_corroborated is True``, duplicated ``-104`` verbatim -- byte-identical
    fixture, identical three-element edge list, identical expectation -- so the whole guard was
    a strict subset of ``-104``.

    THE STRUCTURAL CAUSE, which is why the rebuild moved modules (Story 15.2 / AC2.3)
    --------------------------------------------------------------------------------
    It was not carelessness. ``_score`` takes ``list[str]``, so **the caller owns the
    decomposition** -- and this guard's caller was the guard. It re-implemented the
    decomposition with the same function, on input it had normalised itself. Every case in
    ``tests/test_vacuous_detector.py`` does the same, and none of them could observe a
    regression at the real seam. So the rebuilt guard lives HERE, drives the REAL index and the
    PRODUCTION read path, and varies the decomposition across a seam that actually survives to
    the detector.

    WHAT IT ASSERTS NOW, AND HOW THAT DIFFERS FROM `-104` (`DN-15-2-3`)
    ------------------------------------------------------------------
    ``-104`` pins a *classification* rule on a hand-built edge list: a call on a mock-bound name
    is not a SUT call. This pins something ``-104`` cannot see -- that the corroboration verdict
    is **invariant under the line decomposition**, measured through the real index on source
    that genuinely desynchronises the two views. The duplication is resolved by ``-107`` no
    longer asserting ``-104``'s subject at all.

    ``-134`` does not cover this either: its fixture is mock-free, so fact (a) short-circuits and
    the corroboration path is never entered. This is the guard for the branch that can move a
    finding to VERDICT-ELIGIBLE.

    MUTATION OBSERVED TO MAKE IT RED (AC5.3 / AC9.1)
    ------------------------------------------------
    Reverting ``run()``/the scorer's decomposition to ``source.splitlines()`` -- the shipped code
    at HEAD ``72a95ef`` -- makes every separator row fail: corroboration flips ``True`` ->
    ``False``, because the shifted window drops the span's last line and the mock-referencing
    assertion falls off the end. **Observed RED before the fix, in both the flag and the
    evidence.** The old form of this guard passes under that same mutation, which is the whole
    point.
    """
    control_score, control_text, control_entry, control_definition = _score_through_the_read_path(
        tmp_path, _CORROBORATED_FIXTURE.format(separators=""), "corroborated_control"
    )
    # PRECONDITION -- the control really is on the INTERESTING branch. Without this the rows
    # below could agree on an uninteresting `False` and assert nothing (`AI-E14-1`).
    assert control_score.heuristically_vacuous is True
    assert control_score.ast_corroborated is True, (
        "the control must be CORROBORATED, or this guard is comparing two advisory findings "
        "and measuring nothing about the branch it exists for"
    )
    # The ROUTE to the flag, asserted rather than assumed. It is the DENSITY floor, not
    # the mock ceiling: three MagicMock constructions against two SUT calls AND the
    # `fake.other()` assertion call is 3/6 = exactly 1/2, which does NOT clear the STRICT
    # `> 1/2` ceiling. (Story 15.2 / 0.14 offers "three mocks against two SUT calls" as the
    # mock-ratio shape; measured here, the mock-bound assertion call is a SIXTH call site
    # and lands the ratio exactly ON the boundary. Recorded because a fixture that fires
    # for a different reason than its author believes is how this family gets probed and
    # then wrongly declared safe.)
    assert control_score.mock_ratio == Fraction(1, 2)
    assert control_score.assertion_density < Fraction(1, 4)
    # ...and fact (a) really is satisfied, which the mock-free fixtures above cannot do.
    assert control_score.call_sites == 6 and control_score.mock_sites == 3
    control_evidence = provenance_evidence(
        index_aligned_lines(control_text),
        _edges_in_span(control_entry.edges, control_definition.start_line, control_definition.end_line),
        control_definition.start_line,
        control_definition.end_line,
        assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
        mock_callees=_MOCK_CALLEES,
    )
    assert control_evidence.sut_result_is_discarded is True
    assert control_evidence.mock_referencing_assertions >= 1

    for name, separator in _INDEX_DESYNC_SEPARATORS:
        for count in (1, 2):
            score, text, entry, definition = _score_through_the_read_path(
                tmp_path,
                _CORROBORATED_FIXTURE.format(separators=separator * count),
                f"corroborated_{name.lower()}_{count}",
            )
            # The variable really IS varying, at the seam it is varied across -- the assertion
            # the old guard never made, and the reason it was vacuous (`DF-15-2-A`'s arm (a)).
            assert text.count(separator) == count
            assert len(text.splitlines()) != text.count("\n"), (
                f"{name} ({ascii(separator)}) does not desynchronise the two decompositions on "
                "this fixture, so the row varies nothing"
            )
            assert (definition.start_line, definition.end_line) == (
                control_definition.start_line,
                control_definition.end_line,
            ), f"{name} ({ascii(separator)}) moved the INDEX's span, not just the detector's view"

            assert score == control_score, (
                f"{count}x {name} ({ascii(separator)}) changed the score across the line "
                f"decomposition seam: {score} vs {control_score}"
            )
            assert score.ast_corroborated is True, (
                f"{count}x {name} ({ascii(separator)}) withheld corroboration from a genuinely "
                "vacuous test -- fact (b) must not depend on how the lines were cut"
            )
            evidence = provenance_evidence(
                index_aligned_lines(text),
                _edges_in_span(entry.edges, definition.start_line, definition.end_line),
                definition.start_line,
                definition.end_line,
                assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
                mock_callees=_MOCK_CALLEES,
            )
            assert evidence == control_evidence, (
                f"{count}x {name} ({ascii(separator)}) changed fact (b)'s EVIDENCE even where "
                f"the verdict agreed: {evidence} vs {control_evidence}"
            )


#: The head every AC1 layout shares: `_DUP_HEAD`'s established shape (three mock constructions
#: against two SUT calls, so the STRICT `> 1/2` ceiling is cleared) carried through the real
#: index instead of a hand-built edge list. Reused rather than re-invented -- two spellings of
#: one question is the disagreement class this detector keeps closing elsewhere (AR7).
_DUP_HEAD_CONTRACT = (
    "from unittest.mock import MagicMock  # trailing comment{separators}\n"
    "\n"
    "\n"
    "def test_shape():\n"
    "    fake = MagicMock()\n"
    "    second = MagicMock()\n"
    "    third = MagicMock()\n"
    "    fake.other.return_value = 7\n"
    # Filler, so every layout below clears the DENSITY floor and is actually FLAGGED: an
    # unflagged fixture measures nothing about PROMOTION, which is all this family is for.
    "    filler_a = 1\n"
    "    filler_b = 2\n"
    "    filler_c = 3\n"
    "    filler_d = 4\n"
)

#: The six layouts AC1.3 required to be ATTEMPTED, in both directions. Each places a consumed
#: and a discarded SUT call, and the assertions, so that a one-line shift lands somewhere that
#: could plausibly invert fact (b). Declared as data so the search is re-runnable and visible
#: rather than described in a commit message.
_VERDICT_ELIGIBILITY_LAYOUTS: tuple[tuple[str, str], ...] = (
    # Genuinely vacuous and CORROBORATED at rest: the direction that CAN move (withholding).
    ("all-discarded", "    sut(1, 2)\n    sut(3, 4)\n    assert fake.other() == 7\n"),
    # Genuine: the consumed call sits BELOW the discarded one, so a backwards shift would
    # classify it against the discarded one's text. The named hypothesis of Story 15.2 / 0.10.
    ("consumed-below-discarded",
     "    sut(1, 2)\n    captured = sut(3, 4)\n    assert captured == fake.other()\n"),
    # The same two statements the other way up, so nothing rides on ordering.
    ("consumed-above-discarded",
     "    captured = sut(3, 4)\n    sut(1, 2)\n    assert captured == fake.other()\n"),
    # A COMMENT decoy: `sut(` is locatable on the shifted line but opens no statement.
    ("comment-decoy",
     "    # sut(9, 9)\n    captured = sut(3, 4)\n    assert fake.other() == 7\n"
     "    assert fake.other() == 7\n"),
    # A STRING decoy: locatable text that is not a call at all.
    ("string-decoy",
     '    doc = "sut(9, 9)"\n    captured = sut(3, 4)\n    assert fake.other() == 7\n'
     "    assert fake.other() == 7\n"),
    # Duplicated assertions AND trailing padding, so the mock-referencing assertion survives a
    # backwards shift instead of falling off the end -- the strongest granting candidate.
    ("duplicated-assertions-padded",
     "    # sut(9, 9)\n    sut(1, 2)\n    captured = sut(3, 4)\n"
     "    assert fake.other() == 7\n    assert fake.other() == 7\n"
     "    trailing_a = 1\n    trailing_b = 2\n    trailing_c = 3\n"),
)


def test_a_shifted_span_cannot_manufacture_verdict_eligibility(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-137 -- AC1: the measured answer, in both directions.

    THE QUESTION Story 15.2 was required to settle BY EXECUTION
    -----------------------------------------------------------
    A heuristic-only flag is ADVISORY: ``depth_supported`` is ``None`` and the Story 1.6 gate
    must not turn it red. An AST-CORROBORATED flag is a different animal -- ``rule_id`` becomes
    ``RULE_AST``, ``depth_supported`` becomes ``AUDITED_SHALLOW``, and through
    ``argus/verdict/verdict_gate.py:86-96`` (*verdict-blocking <=> verdict-eligible <=>
    ``depth_supported is not None``*) it reaches ``TC-ArgusAgent-VERDICT-001-30`` arm 1:
    ``NOT_READY_FOR_RELEASE`` on a **default** ``run_audit_detailed`` -- no flags, no deep pass,
    no LLM, no cartridge harness. So: could the shifted line view carry a finding all the way
    THERE? Every reproduction that existed when the story was written returned
    ``ast_corroborated=False``, but only because its fixture was mock-free and call-free, which
    short-circuits fact (a) -- the corroboration path had never once been exercised.

    THE ANSWER, MEASURED IN BOTH DIRECTIONS
    ---------------------------------------
    - **Corroboration wrongly WITHHELD (``True`` -> ``False``): REPRODUCES.** A genuinely
      vacuous, corroborated fixture loses its corroboration when a single separator is inserted
      above it. An accusation is downgraded to advisory -- the safe direction. Guarded by
      ``-107``.
    - **Corroboration wrongly GRANTED (``False`` -> ``True``): NO REPRODUCTION FOUND against
      the shipped code**, across the six structurally distinct layouts below.

    (X) **"No reproduction found" is recorded as exactly that, and NEVER as "cannot happen"** --
    and here that distinction has teeth, because the absence was measured to be CONTINGENT, not
    structural.

    WHY IT DOES NOT REPRODUCE, AND THE ONE LINE THAT IS HOLDING IT SHUT
    -------------------------------------------------------------------
    Two effects push the same way. First, the shift moves the window BACKWARDS, so a span loses
    its TRAILING lines -- where the mock-referencing assertion lives -- driving
    ``mock_referencing_assertions`` toward zero. Second, and decisively, **every failure to read
    in ``provenance_evidence`` counts CONSUMED**: an edge whose shifted line holds no locatable
    ``callee(`` (``provenance_scan.py:907``), one whose line opens no statement, one off-span.
    "No SUT result is consumed" is a clause fact (b) requires, so each unreadable edge withholds
    corroboration. Both of fact (b)'s clauses therefore degrade in the same, safe direction.

    ⛔ **That was not left as an argument.** Removing ONLY the conservative default -- changing
    ``provenance_scan``'s ``located is None`` branch from ``consumed += 1`` to ``continue``,
    leaving the pre-fix ``splitlines()`` decomposition otherwise intact -- **makes the granting
    direction reproduce immediately**: the ``duplicated-assertions-padded`` layout below goes
    ``False`` -> ``True`` under **all eight** separators at one occurrence. Executed and
    observed, 2026-08-19.

    So the honest severity statement is: **as shipped, the measured reach of this defect was a
    false ADVISORY flag and not a false blocking verdict** -- the source proposal's assumption
    survives -- **but the margin was a single line of defensive coding in a different module,
    and nothing had pinned it.** This guard, and the layout table it drives, is that pin.

    THE PREDICTION WAS WRONG, and is recorded as wrong (AC1.1)
    ----------------------------------------------------------
    Story 15.2's Dev Agent Record predicted **YES, in both directions**, reasoning that an edge
    on index line *N* whose real text is ``captured = sut(3, 4)`` would be classified against
    line *N-1*'s ``sut(1, 2)`` and flip ``sut_result_is_discarded``. The withholding direction
    reproduced. **The granting direction did not, and the prediction was WRONG**, because it did
    not account for the conservative CONSUMED default on an unlocatable edge. Recorded as a
    wrong prediction rather than quietly re-scoped -- and the mechanism it missed turned out to
    be the load-bearing one.

    MUTATION OBSERVED TO MAKE IT RED (AC9.1): reverting the decomposition to
    ``source.splitlines()`` -- the shipped code at HEAD ``72a95ef`` -- reddens this guard, via
    the ``all-discarded`` layout losing its corroboration. Executed and observed. (The
    ``consumed += 1`` mutation above is what makes the GRANTING direction reachable; it does
    **not** redden this guard on its own, and is named here as a measured mechanism rather than
    as this guard's reddening mutation.)
    """
    for layout, body in _VERDICT_ELIGIBILITY_LAYOUTS:
        control_source = _DUP_HEAD_CONTRACT.format(separators="") + body
        control, _, _, _ = _score_through_the_read_path(
            tmp_path, control_source, f"eligibility_{layout}_control"
        )
        # PRECONDITION -- the layout is flagged at all, or promotion cannot be measured on it.
        assert control.heuristically_vacuous is True, (
            f"{layout!r} is not flagged by the heuristic, so it can say nothing about "
            "promotion -- repair the fixture, never the predicate"
        )
        for name, separator in _INDEX_DESYNC_SEPARATORS:
            for count in (1, 2):
                shifted, text, _, _ = _score_through_the_read_path(
                    tmp_path,
                    _DUP_HEAD_CONTRACT.format(separators=separator * count) + body,
                    f"eligibility_{layout}_{name.lower()}_{count}",
                )
                assert text.count(separator) == count  # the variable really varies
                # THE CONTRACT makes this an equality. Before the fix the un-corroborated
                # layouts stayed un-corroborated and the corroborated one FLIPPED; after it,
                # nothing moves in either direction.
                assert shifted.ast_corroborated == control.ast_corroborated, (
                    f"{layout!r} with {count}x {name} ({ascii(separator)}) changed "
                    f"verdict-eligibility: {shifted.ast_corroborated} vs "
                    f"{control.ast_corroborated}"
                )
                assert shifted == control, (
                    f"{layout!r} with {count}x {name} ({ascii(separator)}): {shifted} vs "
                    f"{control}"
                )
