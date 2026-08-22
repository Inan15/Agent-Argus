"""The TWO assertion vocabularies + the mock table — names only, no scoring.

Split out of ``argus/detectors/vacuous_test.py`` on 2026-08-22 under **``DF-15-2-D``**,
whose trigger reads: *"the next change of any size to ``argus/detectors/vacuous_test.py``
performs the cohesion split FIRST — by subject cohesion, never by arithmetic, with no
function split across the boundary."* The host stood at **1,196 of 1,200**. This module is
that split, taken **alone and before** Story 16.6's behaviour change, on the
``provenance_scan.py`` precedent.

**The subject.** *"Which callee names count as an assertion, and which as a mock?"* — and
nothing else. No threshold, no score, no finding, no I/O. ``ASSERTION_DENSITY_FLOOR`` and
``MOCK_RATIO_CEILING`` deliberately stayed behind: they are scorer configuration, not
vocabulary, and moving them would have split one subject across two modules to make a line
count work, which is the arithmetic split the ledger entry forbids by name.

⛔ **DN-14-2-1 — the load-bearing rule, restated here because this is now where the tables
live.** There are TWO vocabularies because there are TWO QUESTIONS, and they are NOT two
spellings of one table:

- :data:`_ASSERTION_CALLEES` (+ the naming convention) asks *"does this test ASSERT
  ANYTHING?"* and wants **BREADTH**. It is the density NUMERATOR. Widening it can only RAISE
  ``assertion_sites``, and the floor fires from BELOW, so a wider table moves **away** from an
  accusation.
- :data:`_CORROBORATION_ASSERTION_CALLEES` asks *"which call edges are NOT SUT calls?"*, is
  **FROZEN at Story 14.1's 23 names**, and feeds facts (a) and (b). ``provenance_scan`` reads
  it in two places and **BOTH can move TOWARD an accusation when it widens** — a measured
  false 🔴 is written out beside its declaration below.

**Neither is derived from the other.** Deriving either (``frozen = widened - delta``) would
re-couple them the moment the wide table grows. Facts (a) and (b) must read the frozen table
**directly** and must never be routed through :func:`is_assertion_callee`.

**Re-exported, not relocated, from the caller's point of view.** ``vacuous_test`` imports
every name below and continues to expose it, so ``from argus.detectors.vacuous_test import
_CORROBORATION_ASSERTION_CALLEES`` still resolves. That is deliberate: this split is a
maintainability act and may not become an API change in disguise.

Verification area ArgusAgent-DETECT (``TC-ArgusAgent-DETECT-001-NN``).
"""

from __future__ import annotations

import re

__all__ = [
    "is_assertion_callee",
]

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
# the table could not see is present in 13 of the 31 adjudicated spans. Story 14.3 then added
# the cross-language half, and the reason it is HERE and nowhere else is DN-14-2-1: this table
# answers the density question, and the corroboration table below does not track it.
#
# ── STORY 14.3, THE CROSS-LANGUAGE HALF: what it closed, and what it did NOT ───────────────
#
# THE FALSE ACCUSATION, reproduced through the real tree-sitter index and the real scorer
# before it was closed (14.3 / AC1, ``tests/test_vacuous_cross_language.py``)::
#
#     function testAllman()          // brace on its OWN line
#     {
#         const r = add(2, 3);
#         expect(r).toBe(5);         // a REAL assertion, in the edge set the whole time
#     }
#
#     53-name table : asserts=0 stmts=1 density=0 FLAGGED  <- a real test, falsely accused
#     widened table : asserts=2 stmts=1 density=2 clean    <- and its assertion-free twin
#                                                             STAYS flagged (the control)
#
# ⚠️ **BRACE STYLE IS THE VARIABLE, and it is why the story's original fixture proves
# nothing.** With the brace on the ``function`` line (K&R), 14.2's logical-statement scanner
# reads the header as one unclosed continued statement, the body counts **0**, and
# ``heuristically_vacuous`` requires ``> 0`` — so that shape is unflagged for a reason that
# has nothing to do with this table. The ALLMAN shape is where the accusation actually lived.
#
# ⛔ **MEASURED INCIDENCE ON THE RATIFIED CORPUS: ZERO, and that is recorded rather than
# smoothed.** Over all three pinned members this widening moves 0 flags gained and 0 lost:
# agent-smith scores **0** TypeScript test functions out of 169 extracted and xagents-webapp
# exactly **1** of 410, because ``_is_test_function``'s case-sensitive ``startswith("test")``
# and the invisibility of ``describe``/``it`` callback bodies keep essentially every real
# TypeScript test out of the scorer (``DF-14-3-A`` / ``DF-14-3-C``, cited and NOT fixed here).
# The justification for this table is therefore the MECHANISM and the FIXTURE, never a corpus
# benefit — and the same measurement is what makes it zero-risk.
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
        # ══ Story 14.3 — the cross-language vocabulary ══════════════════════════════════
        # Counts below are MEASURED call-edge frequencies over the TS/JS test files of the
        # two ratified TypeScript members at their pinned shas (agent-smith @ 9ab774d7,
        # xagents-webapp @ 33a86525), not tastes. Names with no count are named by
        # `epics.md`'s minimum or complete a family whose other members ARE measured; each
        # says which. The groupings are COMMENTS — see the flat/language-agnostic contract
        # above (NFR-P2 / AC2.5).
        #
        # ── JavaScript / TypeScript: Jest + Vitest matchers ──
        "expect",  # measured 6876 — the dominant idiom of xagents-webapp
        "toBe",  # measured 2560
        "toHaveBeenCalledWith",  # measured 696
        "toHaveBeenCalled",  # measured 569
        "toEqual",  # measured 344
        "toHaveBeenCalledTimes",  # measured 306
        "toBeVisible",  # measured 298 — Playwright's async matcher, an assertion
        "toContain",  # measured 278
        "toThrow",  # measured 277
        "toMatchObject",  # measured 226
        # …completing the two families above. `epics.md` names `toEqual`/`toThrow`; these
        # are their documented siblings in the same matcher API, added so the table does not
        # recognise half of one family (Jest `expect` API reference).
        "toStrictEqual",
        "toHaveBeenLastCalledWith",
        "toHaveBeenNthCalledWith",
        # ── JavaScript / TypeScript: the `node:assert` core ──
        # agent-smith's whole harness. `deepStrictEqual` is `epics.md`'s; the rest are the
        # documented members of the same module, and the top three are measured.
        "equal",  # measured 1548
        "ok",  # measured 758
        "deepEqual",  # measured 506
        "notEqual",  # measured 50
        "strictEqual",
        "notStrictEqual",
        "deepStrictEqual",
        "notDeepEqual",
        "notDeepStrictEqual",
        "throws",
        "rejects",
        "doesNotThrow",
        "doesNotReject",
        "ifError",
        "assert",  # `node:assert`'s callable default export
        #
        # ⛔ `match` (469) and `doesNotMatch` (76) are DELIBERATELY EXCLUDED despite being
        # measured, and this is a DECISION rather than an omission (14.3 / DN-14-3-2).
        # `re.match` in Python and `String.prototype.match` in JavaScript are pervasive
        # NON-assertions. The error direction is flag-REDUCING, so they could not accuse
        # anyone falsely — but they would silently suppress REAL flags on Python code, which
        # is a recall regression wearing a precision fix's clothes. The accepted-collision
        # argument that carries `expect` does not carry these: `expect` has no common
        # non-assertion meaning and `match` has one in BOTH languages that matter.
        #
        # ⛔ `objectContaining` (376) is likewise excluded: it builds an ARGUMENT to a
        # matcher (`expect(x).toEqual(expect.objectContaining({…}))`), so it is never itself
        # the assertion, and admitting it would count one assertion twice.
        #
        # ── Java / JUnit ──
        # ⚠️ ZERO BEHAVIOUR DELTA, and it is stated as zero rather than claimed as a fix:
        # both already match `_ASSERTION_NAMING_CONVENTION` below and were therefore already
        # admitted by `is_assertion_callee`. They are enumerated for the same reason 14.2
        # enumerated the `unittest.mock` methods that also match it — the convention is a
        # fallback for names this project cannot know, and an ecosystem's own vocabulary
        # should be readable in one place. (`assertTrue` and `fail`, the other two names in
        # `epics.md`'s Java minimum, were ALREADY here and are not added twice.)
        "assertEquals",
        "assertThat",
        # ── Go: `testing.T` + `testify` ──
        # ⚠️ MEASURABLY INERT TODAY, and recorded as inert so no future reader believes Go
        # was made to work here (14.3 / DN-14-3-3): NO Go test is scored at all, because
        # `_is_test_function` requires a lowercase `test` prefix (`func TestX` fails it) and
        # Go selector-expression calls never reach the edge set — `DF-14-3-A` / `DF-14-3-B`,
        # which are COUPLED and must move together or not at all. They ship because
        # `epics.md` names them, they cost nothing, and having them present removes one
        # reason to re-open this table on the day A and B do move.
        #
        # ⛔ `Error` IS NOT HERE, and its absence is the one asymmetry inside this family.
        # It is a DECISION under DN-14-3-5 below, not an oversight, and it must not be
        # "tidied" back in for symmetry. `TC-ArgusAgent-DETECT-001-133` holds it out.
        "Fatal",
        "Fatalf",
        "Errorf",
        "NoError",
        "Equal",
    }
)

# ── DN-14-3-5 — THE COLLISION RULE, stated once and applied to EVERY name ─────────────────
#
# ⚠️ FILED BY REVIEW ITERATION 1 OF STORY 14.3, WHICH FOUND THE REAL DEFECT: DN-14-3-2's
# collision test was applied to `match`/`doesNotMatch` and to nothing else. Six of the names
# above were shipped without it — `ok`, `equal`, `Error`, `Equal`, `throws`, `rejects` — and
# an exclusion principle applied to one name and not to its neighbours is not a principle.
# This block is that principle, MADE EXPLICIT AND MADE UNIFORM.
#
# THE RULE. A name is admitted when its MEASURED non-assertion collision as a Python callee
# is materially smaller than its MEASURED assertion benefit as a JS/TS call edge; it is
# excluded when the collision is comparable to or greater than the benefit.
#
# WHY THAT RULE AND NOT "EXCLUDE ANYTHING THAT COULD COLLIDE". Every error here is
# flag-REDUCING — a colliding name raises `assertion_sites`, and the floor fires from below —
# so nothing in this table can manufacture a false 🔴 (the corroboration path reads the FROZEN
# table by name, DN-14-2-1). Both failure directions are therefore ADVISORY-level, and the
# project's locked asymmetry does not settle it. What settles it is magnitude, because the
# realized populations are wildly unequal: of the 4,746 test functions scored across the three
# ratified corpus members, 4,745 are PYTHON and 1 is TypeScript (§0.4). A Python collision is
# paid against the whole corpus; a JS/TS benefit is, today, prospective.
#
# THE MEASUREMENT. Python collisions are call sites counted with the STDLIB `ast` module —
# deliberately NOT with Argus's own index, because deriving a collision argument from the
# thing under test would be circular — over 4,046 independent Python files: the three pinned
# corpus members, Argus itself, this environment's `site-packages`, and the CPython 3.11
# standard library. JS/TS benefits are call edges emitted by the SHIPPED index over the staged
# test files of the two ratified TypeScript members at their pinned shas.
#
#     name        py collisions   js/ts benefit   benefit/cost   decision
#     ---------   -------------   -------------   ------------   -------------------------
#     match                 706             476   0.7x           ⛔ EXCLUDED (was DN-14-3-2)
#     Error                 164               0   0x             ⛔ EXCLUDED (new, iter. 1)
#     equal                  34           1,548   45x            ✅ admitted, cost recorded
#     expect                 29           6,876   237x           ✅ admitted (was AC2.6)
#     ok                     10             764   76x            ✅ admitted, cost recorded
#     throws                  0              19   —              ✅ admitted, no collision
#     rejects                 0               1   —              ✅ admitted, no collision
#     Equal                   0               0   —              ✅ admitted, inert (DN-14-3-3)
#
# ⛔ THE RULE REPRODUCES THE TWO DECISIONS THAT WERE ALREADY RATIFIED, which is the only
# reason to trust it: `match` is excluded and `expect` is admitted by the SAME arithmetic that
# decides the six, so it is not a rationalisation fitted to a conclusion.
#
# ⚠️ AND IT DISAGREES WITH THE PROJECT ON EXACTLY ONE NAME, WHICH IS RECORDED RATHER THAN
# HIDDEN. `doesNotMatch` measures 0 Python collisions against 76 JS/TS edges, so the rule
# would ADMIT it; Story 14.3's AC2.3 excludes it by name and permits its inclusion only with a
# measured argument. The project standard wins and it stays out — it is `match`'s negation and
# would be read as `match` being half-admitted — and the tradeoff is written here so the next
# reader sees a conflict resolved rather than a rule quietly bent.
#
# `Error` IS DROPPED, and it is the clearest case in the table: 164 measured Python call sites
# — CPython's own `wave`/`aifc`/`sunau` each define `class Error(Exception)` and call it, and
# mypy's `stubtest` yields `Error(...)` records — against a benefit measured at exactly ZERO.
# Its intended source is Go's `t.Error`, which is unreachable by TWO independent barriers
# (`DF-14-3-A` never scores a Go test; `DF-14-3-B` never emits a selector-expression call), and
# in JS/TS `throw new Error(...)` is the standard NON-assertion idiom. It costs the most of any
# candidate and buys nothing.
#
# `ok` AND `equal` ARE KEPT WITH THEIR COST RECORDED AND MADE EXECUTABLE (AC2.6). The cost is
# real and is not hand-waved: `env.ok(...)` is a result constructor in agent-smith's production
# surface (9 sites) and `jsonschema._utils.equal(a, b)` is a BOOLEAN-RETURNING comparison
# predicate (33 sites) — and a Python test whose body is `equal(compute(x), 5)` with no
# `assert` is exactly the vacuous shape this detector exists to flag, so admitting the name
# un-flags it. It is accepted anyway because they carry `node:assert`, the ENTIRE harness of a
# ratified corpus member (2,312 measured edges), and dropping them would knowingly re-open the
# false accusation this story exists to close for that member's dominant idiom. ⛔ Recording it
# in prose was the previous round's mistake: `-133` asserts the cost BY EXECUTION, so removing
# `ok`/`equal` later cannot happen silently and re-adding `Error` cannot happen at all.

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
