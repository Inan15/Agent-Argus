"""Line-oriented provenance scanning for the vacuous-test detector's fact (b) — PURE.

Drivers: ArgusAgent-FR-7-subset (the Tier-A vacuous-path AST subset — assertion-target
provenance), cross-cutting #6 (a heuristic finding is verdict-eligible only when the AST
corroborates it — the false-accusation moat), AR4/AR8 (pure, deterministic, no ``float``,
no clock/uuid/random/iteration-order in anything reaching a ``.argus/``-bound output),
NFR-M1 (≤1200-line modules), AR7/§3.3 (one derivation, never a fork).

Why this module exists (Story 14.1, review iteration 2)
-------------------------------------------------------
``argus/detectors/vacuous_test.py``'s job is *scoring a test function*: the heuristic
ratios, the two-fact corroboration and the finding it emits. Answering fact (b) — *"do
the asserted values derive from the SUT output?"* — needs something different in kind: a
small, line-oriented reader of Python source text that knows about comments, string
literals, brackets, line continuations and ``with``-block extents. That is a **separate
concern** with its own failure modes (CRLF, non-ASCII identifiers, continuation syntax),
and bolting ~15 of its functions onto the scorer took that module from 623 to 1072 lines
— 128 from the NFR-M1 ceiling, with Stories 14.2 and 14.3 still to land in it. The split
follows the ``argus/pipeline_stages.py`` / ``argus/pipeline_persist.py`` precedent:
a cohesion boundary, no function split across it, and the scorer imports back.

**The callee vocabularies are deliberately NOT here.** ``_ASSERTION_CALLEES`` and
``_MOCK_CALLEES`` stay in ``vacuous_test.py`` and are PASSED IN.
``RESULT_OBSERVING_CONTEXT_CALLEES`` is fact (b)'s OWN table (DN-3) and therefore does live
here.

⚠️ **What the parameter does and does not guarantee — CORRECTED 2026-08-18 (Story 14.2 /
AC6.5).** This paragraph used to end *"nothing in this module can grow a dependency on a
table it cannot see"*, and read as a guarantee that fact (b) could not move when Story 14.2
widened the assertion table. **That was false as written.** The table is a parameter, so this
module *does* see it, and reads it in TWO places: the SUT loop in :func:`provenance_evidence`
(a widened callee stops being a candidate SUT call, which can drop ``consumed_sut_calls`` to
zero and flip ``sut_result_is_discarded`` TRUE) and :func:`_assertion_statement_lines` (a
widened callee makes another line an assertion statement, which can raise
``mock_referencing_assertions`` from zero). Both directions were reproduced end to end: an
ordinary mock-interaction test whose sole assertion is ``fake.calculate.assert_called_once_with()``
scores ``asserts=0 density=0 corroborated=False`` on the 23-name table and
``asserts=1 density=1/5 corroborated=True`` on a widened one — still under the density floor,
so still flagged, and now VERDICT-ELIGIBLE. A false 🔴 manufactured by the fix for the
assertion table.

What Story 14.1's DN-4 actually guarantees is that fact (b) does not depend on the assertion
**COUNT** — no clause here reads ``assertion_sites`` or compares it to a threshold. It never
guaranteed independence from the assertion **TABLE**, and the two are different things. What
enforces the rest is **DN-14-2-1**, in the caller: ``vacuous_test.py`` passes the corroboration
path a FROZEN vocabulary (``_CORROBORATION_ASSERTION_CALLEES``) pinned to 14.1's 23 names,
while only the density numerator reads the widened ``_ASSERTION_CALLEES``. So this module is
independent of the widening because of what it is HANDED, not because of what it can see —
and Story 14.3 can widen the table across four languages without re-opening the moat.

What the scan can and cannot prove (honest scope)
--------------------------------------------------
The Story 1.4 index gives an UNRESOLVED edge set (``DF-1-4-A``): a callee NAME and a
1-based line, with no scope binding. Everything below is therefore NAME-level structural
evidence, not dataflow — real assertion provenance is Story 6.2's (``DF-14-1-A``). The
asymmetry that governs every judgement call here is stated in ``vacuous_test.py``'s
docstring: **a false 🔴 is the lethal failure; a real vacuous test left advisory is
tolerable.** So wherever the source text cannot be read confidently, the answer is
"consumed" — unresolvable is not evidence, and no corroboration can rest on it.

Platform neutrality is a property of the inputs, not a hope
------------------------------------------------------------
Every function takes the line list the detector already receives, so no line TERMINATOR is
ever observed.

**Re-derived by Story 15.2, because the list changed.** That list is no longer
``source.splitlines()``; it is
:func:`~argus.detectors.vacuous_test.index_aligned_lines`, the newline-only decomposition the
Story 1.4 index numbers by. ``\\r`` and ``\\r\\n`` still cannot appear in it -- the read path
at ``argus/pipeline_stages.py:124`` normalises them long before -- so the neutrality claim
holds for line terminators. What CHANGED is that a line may now legitimately **contain** one
of ``\\x0b``, ``\\x0c``, ``\\x1c``, ``\\x1d``, ``\\x1e``, ``\\x85``, ``\\u2028``, ``\\u2029``,
where ``splitlines()`` used to cut the line in two at them. Python's ``\\s`` and
``str.strip()`` treat all of those as whitespace, so this module's ``\\A\\s*`` anchors and its
statement stripping now see characters they never saw before. ⛔ **That was MEASURED, not
reasoned about**: with each of the eight inserted at the leading and at the trailing edge of a
body line, ``body_statement_count`` and ``logical_statement_starts`` return values IDENTICAL
to the separator-free control in all sixteen cases, and ``TC-ArgusAgent-DETECT-001-134``
pins the whole ``VacuousTestScore`` against a separator-free control end to end. The claim
survives; its WORDING did not, and is corrected here rather than left to go quietly stale. No pattern below is anchored with ``^`` or ``$`` — every one uses ``\\A``
and ``\\Z``, which cannot be satisfied by a line terminator — none relies on ``\\s`` spanning
a terminator, and every identifier pattern is Unicode-aware by construction. Local gates run
on Windows and CI runs an ubuntu matrix; this module has to score both identically.

⚠️ **That sentence was FALSE when it was first written, and it is corrected here rather than
quietly re-worded.** ``_ASSIGNMENT_RE`` was ``^``/``$``-anchored from the day the claim was
made (``DF-14-2-B``, filed by Story 14.2 against its own module and discharged by Story
14.3). It was never exploitable — every call site passes a ``splitlines()``-derived line —
but an unexploitable false claim in a docstring is still a false claim, and this module's
whole contract is that platform neutrality is a property of the inputs rather than a hope.
``tests/test_vacuous_cross_language.py`` now enforces the claim by SWEEPING the module's own
source for ``^``/``$`` anchors, so it cannot silently become false a second time.
"""

from __future__ import annotations

import re
from typing import NamedTuple

from argus.index.ast_index import CodeEdge

__all__ = [
    "RESULT_OBSERVING_CONTEXT_CALLEES",
    "ProvenanceEvidence",
    "body_statement_count",
    "logical_statement_count",
    "logical_statement_starts",
    "opens_bare_assert",
    "provenance_evidence",
]

# Context managers whose BODY observes the SUT's behaviour, so a SUT call inside one
# is CONSUMED rather than discarded (Story 14.1 / DN-3, AC1.4). ``with
# pytest.raises(ValueError): parse(bad)`` constrains the SUT precisely — raising IS
# the observation — and scoring it as "the result was thrown away" would re-create the
# false-accusation class on every fail-closed test, a shape the validation corpus is
# full of. This is fact (b)'s OWN table and not an addition to ``_ASSERTION_CALLEES``:
# that one is Story 14.2's to widen, and fact (b) must not move when it does (DN-4).
RESULT_OBSERVING_CONTEXT_CALLEES: frozenset[str] = frozenset(
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
#:
#: ⚠️ RE-ANCHORED ``\A``/``\Z`` 2026-08-18 (Story 14.3, ``DF-14-2-B``). It was ``^``/``$``,
#: which contradicted this module's own platform-neutrality claim above — a claim that was
#: not true as written. ``$`` also matches immediately BEFORE a trailing ``\n``, so on an
#: input that ever carried its terminator the ``value`` group would silently differ between
#: a CRLF and an LF source. Not exploitable at any current call site (every one of them
#: passes an ``index_aligned_lines()``-derived line -- ``splitlines()`` until Story 15.2 --
#: neither of which can carry a terminator), and the
#: **equivalence was DEMONSTRATED rather than asserted**: both patterns were run over every
#: line of every staged test file of all three pinned corpus members — **218,017 lines, of
#: which 25,649 matched as assignments — with 0 disagreements** on the match/no-match verdict
#: and on both named groups, and the flagged set of all three members byte-identical
#: afterwards. The anchors are now correct by construction rather than by the call sites'
#: continued good behaviour.
_ASSIGNMENT_RE = re.compile(
    rf"\A\s*(?P<targets>{_IDENT}(?:\s*\.\s*{_IDENT})*"
    rf"(?:\s*,\s*{_IDENT}(?:\s*\.\s*{_IDENT})*)*)"
    rf"\s*(?::[^=]*?)?=(?!=)\s*(?P<value>.+)\Z"
)

#: The leading attribute chain of an expression: ``fake.calculate(…)`` → ``fake``,
#: ``calculate``.
#: ⚠️ Also re-anchored ``\A`` 2026-08-18 (Story 14.3). ``DF-14-2-B`` named only
#: ``_ASSIGNMENT_RE``; this SECOND ``^`` was found by the sweep ``-130`` now runs over this
#: module, not by reading the ledger entry. ``^`` without ``re.MULTILINE`` is exactly ``\A``,
#: so the behaviour delta is provably nil — but the docstring's claim is about the ANCHORS,
#: and one that is true only because a flag happens not to be set is the kind of claim this
#: module exists to stop making.
_LEADING_CHAIN_RE = re.compile(rf"\A({_IDENT})((?:\s*\.\s*{_IDENT})*)")

#: ``with cm() as name`` / ``… as a, … as b``.
_AS_BINDING_RE = re.compile(rf"\bas\s+({_IDENT})")

#: An identifier that ROOTS a chain — i.e. is not itself an attribute of something
#: else. ``fake.tally`` yields ``fake`` and not ``tally``.
_CHAIN_ROOT_RE = re.compile(rf"(?<![\w.]){_IDENT}")

#: ``pytest.raises(``/``assertRaises(`` — any result-observing context call, however
#: it is qualified. Built from the table (sorted, so the pattern is deterministic).
_OBSERVING_CALL_RE = re.compile(
    r"(?<!\w)(?:" + r"|".join(sorted(map(re.escape, RESULT_OBSERVING_CONTEXT_CALLEES))) + r")\s*\("
)

_OPEN_BRACKETS = "([{"
_CLOSE_BRACKETS = ")]}"

#: A CONTINUATION-CLAUSE header carrying no code of its own past the colon — ``except:`` /
#: ``except V as e:`` / ``except* V:`` / ``else:`` / ``finally:`` / ``case P:``. These are
#: CLAUSES of a compound statement, not statements: CPython builds ONE ``ast.Try`` however
#: many handlers it carries, ONE ``ast.If`` however its ``orelse`` is spelled and ONE
#: ``ast.Match`` however many arms it has, and neither ``ast.ExceptHandler`` nor
#: ``ast.match_case`` is an ``ast.stmt`` at all. See
#: :func:`_is_continuation_clause_header` for the measurement that put this here.
#:
#: ⛔ ``elif`` is deliberately absent: ``if/elif`` is a NESTED ``ast.If``, i.e. a genuine
#: extra statement, and sweeping it in here would under-count.
#:
#: ``case`` is a SOFT keyword, so the test is shape-based — "opens with ``case`` and ends at
#: a colon" — and is applied to the STRING-BLANKED text so a colon inside a literal cannot
#: end it. An annotated assignment to a name called ``case`` (``case: int = f()``) does not
#: end at a colon and is not matched. Anchored ``\A``/``\Z`` and never ``^``/``$``, per the
#: platform-neutrality contract in this module's docstring (AC8.1).
_CONTINUATION_CLAUSE_RE = re.compile(r"\A(?:except|else|finally|case)\b.*:\Z")


def opens_bare_assert(stripped: str) -> bool:
    """Whether *stripped* (a left-stripped source line) opens a bare ``assert``.

    Declared ONCE and read by both consumers — the heuristic's assertion count in
    ``vacuous_test.py`` and the fact-(b) provenance scan below (AR7/§3.3: reuse, never
    fork). Two spellings of "is this an assert line" is exactly the disagreement class
    this detector keeps closing elsewhere.
    """
    return stripped == "assert" or stripped.startswith("assert ") or stripped.startswith("assert(")


def _consume_string(text: str, index: int) -> tuple[int, str | None]:
    """``(index just past the literal at *index*, delimiter still open at end of *text*)``.

    Single- and triple-quoted, backslash-aware. The second element is the TRIPLE
    delimiter when the literal is still open when the line runs out — that is the
    cross-line state :func:`logical_statement_count` needs, and the reason this
    returns a pair rather than an index (Story 14.2 / DN-14-2-2). A single-quoted
    literal cannot legally span a line without a backslash continuation, so it is
    reported CLOSED at end of line, which is exactly what this module did before the
    state existed — the conservative direction, and one the "unresolvable is not
    evidence" default already absorbs.
    """
    quote = text[index]
    delimiter = quote * 3 if text.startswith(quote * 3, index) else quote
    cursor = index + len(delimiter)
    while cursor < len(text):
        if text[cursor] == "\\":
            cursor += 2
            continue
        if text.startswith(delimiter, cursor):
            return cursor + len(delimiter), None
        cursor += 1
    return len(text), (delimiter if len(delimiter) == 3 else None)


def _skip_string(text: str, index: int) -> int:
    """Index just past the string literal opening at *index* (or end of *text*)."""
    return _consume_string(text, index)[0]


def _code_prefix(line: str) -> str:
    """*line* with any trailing comment removed, string literals PRESERVED.

    Column indices into the result are valid indices into *line*, which is what lets
    a call site located by regex be split into "what precedes it" and "what follows".
    """
    return _continued_code_prefix(line, None)[0]


def _continued_code_prefix(line: str, pending: str | None) -> tuple[str, str | None]:
    """:func:`_code_prefix` of *line*, resumed inside a string left open by an earlier line.

    *pending* is the triple-quote delimiter the PREVIOUS line left open, or ``None``.
    Returns the comment-stripped code text and the delimiter still open after this line.

    Characters belonging to a literal opened on an earlier line are blanked to spaces
    rather than dropped, so every column index into the result is still a valid index
    into *line* — the invariant :func:`_locate_call` and the ``preceding``/``statement``
    split in :func:`provenance_evidence` rest on. A ``#`` inside such a literal is text,
    not a comment, which is precisely the confusion that made a ``;`` in docstring prose
    look like a statement separator (§0.2 of Story 14.2: two flags GAINED on the corpus,
    on a change advertised as flag-reducing).
    """
    out: list[str] = []
    cursor = 0
    if pending is not None:
        while cursor < len(line):
            if line[cursor] == "\\":
                out.append(" " * min(2, len(line) - cursor))
                cursor += 2
                continue
            if line.startswith(pending, cursor):
                out.append(" " * len(pending))
                cursor += len(pending)
                pending = None
                break
            out.append(" ")
            cursor += 1
        if pending is not None:
            return "".join(out), pending
    while cursor < len(line):
        char = line[cursor]
        if char == "#":
            break
        if char in "\"'":
            end, still_open = _consume_string(line, cursor)
            out.append(line[cursor:end])
            cursor = end
            if still_open is not None:
                return "".join(out), still_open
            continue
        out.append(char)
        cursor += 1
    return "".join(out), None


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


def _continues_onto_next_line(code: str) -> bool:
    """Whether *code* (comment-stripped) ends in an explicit backslash continuation.

    Python requires the backslash to be the last character on the physical line, so
    this is exact rather than heuristic — and it is checked on the COMMENT-STRIPPED,
    string-preserving text, so a literal ending in an escaped backslash
    (``path = "c:\\\\"``) is not mistaken for one.
    """
    return code.rstrip().endswith("\\")


def _logical_statement_end(source_lines: list[str], start_line: int, span_end: int) -> int:
    """Last 1-based line of the logical statement opening at *start_line*.

    Bracket-balanced AND backslash-aware, so both of Python's continuation syntaxes end
    the statement in the same place. Bounded by *span_end* so a malformed span can never
    walk out of the test function.
    """
    depth = 0
    for line_no in range(start_line, span_end + 1):
        index = line_no - 1
        if index < 0 or index >= len(source_lines):
            return line_no
        code = _code_prefix(source_lines[index])
        depth = max(depth + _bracket_delta(code), 0)
        if depth <= 0 and not _continues_onto_next_line(code):
            return line_no
    return span_end


class _SpanLine(NamedTuple):
    """One physical line of a span, as the ONE scan below reads it.

    ``opens`` is the 1-based first line of the logical statement this line belongs to,
    or ``None`` when the line opens nothing and belongs to nothing (blank, comment-only,
    at bracket depth 0 and outside any string).
    """

    line_no: int
    code: str
    opens: int | None


def _scan_span(source_lines: list[str], start: int, end: int) -> list[_SpanLine]:
    """THE statement scan of the 1-based inclusive span — declared once, read by both consumers.

    A line continues the previous logical statement when the bracket depth before it is
    positive, OR the previous code line ended in a backslash, OR a triple-quoted string
    literal opened earlier is still open. All three are handled by one rule rather than
    special-cased, because the two Python continuation syntaxes were already broken
    separately once (see :func:`logical_statement_starts`) and the string state was the
    third member of the same family.

    **Why the string state is here and not in the caller (AR7/§3.3, AC1.2).**
    ``logical_statement_starts`` — fact (b)'s statement boundaries — and
    :func:`logical_statement_count` — the heuristic's density DENOMINATOR — are two
    consumers of one question: *"where does a statement start?"*. Story 14.2 measured what
    happens when the second one is written separately: reusing the pre-14.2 line scan put
    the denominator at 1.134× of CPython's own statement count and **GAINED two flags** on
    the pinned corpora, both from a ``;`` inside DOCSTRING PROSE being read as a statement
    separator (``test_sim_real_boundary.py:405``, ``test_plugin_fail_closed.py:376``). With
    the state added HERE, once, both consumers see it: 1.005× of ground truth and **0** flags
    gained. Two spellings of "where does a statement start" is the disagreement class this
    detector keeps closing elsewhere.
    """
    scanned: list[_SpanLine] = []
    current: int | None = None
    depth = 0
    continued = False
    pending: str | None = None
    for line_no in range(start, end + 1):
        index = line_no - 1
        if index < 0 or index >= len(source_lines):
            continue
        inside_string = pending is not None
        code, pending = _continued_code_prefix(source_lines[index], pending)
        if depth <= 0 and not continued and not inside_string:
            if not code.strip():
                current = None  # a blank / comment-only line opens no statement
                scanned.append(_SpanLine(line_no, code, None))
                continue
            current = line_no
        scanned.append(_SpanLine(line_no, code, current if current is not None else line_no))
        depth = max(depth + _bracket_delta(code), 0)
        continued = _continues_onto_next_line(code)
    return scanned


def logical_statement_count(source_lines: list[str], start: int, end: int) -> int:
    """How many SIMPLE statements the 1-based inclusive span contains (PURE, deterministic).

    The heuristic's assertion-density DENOMINATOR (Story 14.2 / AC1). It counts what
    Python executes rather than what the author typed:

    - a statement wrapped over several lines — bracketed or backslash-continued — counts
      **once**, however many lines it occupies;
    - a ``;``-compound counts once per simple statement, which is the same unit fact (b)
      already reasons about (:func:`_simple_statement_breaks`, reused here rather than
      re-derived);
    - a docstring, or any other multi-line string literal, counts **once** — not once per
      line of prose;
    - a bare continuation-clause header (``except`` / ``else`` / ``finally`` / ``case``) and
      a decorator count for **nothing**, because CPython builds no ``ast.stmt`` for either
      (:func:`_is_continuation_clause_header`, :func:`_is_decorator`);
    - blank lines, comment-only lines and bare closing brackets count for nothing.

    Measured against CPython's own ``ast`` module (every ``ast.stmt`` in the body,
    recursively) over the 1,848 flagged minions tests, the LINE count this replaced ran at
    **1.9071×** ground truth (29,093 ÷ 15,255); this runs at **1.0000×** — 15,255 ÷ 15,255,
    exact on **1,848 of 1,848** spans. Over agent-smith's 681: **0.9997×**, exact on 680.
    Over the whole 4,673-function pinned population: **4,672 exact, 0 over-counts, 1
    under-count**.

    **The residual, and its DIRECTION — corrected 2026-08-18 after it was measured wrong**
    ----------------------------------------------------------------------------------------
    This paragraph used to claim the residual was *"a bounded, deterministic under-count in
    the direction that RAISES density, i.e. away from a flag"*. ⛔ **At the time it was
    written that was the wrong direction**, and a claim about a SAFETY direction is the last
    thing that may be asserted rather than measured in this detector. Re-measured over the
    non-exact spans of the first implementation: **64 of 64** (minions) and **27 of 28**
    (agent-smith) were OVER-counts, which LOWER density and bias TOWARDS a flag — the very
    failure mode Story 14.2 exists to remove, reintroduced smaller and differently shaped. The
    dominant mechanism was a continuation-clause header opening a statement of its own
    (``try/except/else/finally`` scored 8 against CPython's 5); the rest was decorators.

    Both were then FIXED rather than documented, and the direction re-measured: **0
    over-counts remain in either member**. What is left is one span in 4,673 — the inline
    compound header, ``def f(): return 0`` or ``with x(): y()``, which is two statements to
    CPython and one line here. That IS a bounded under-count, so the original claim is now
    true of the code as it stands, having been made true instead of merely asserted. Flags
    GAINED by the correction: **0** on both members (structurally so — the denominator can
    only shrink, density can only rise, the floor fires from below, and ``mock_ratio`` is
    taken over ``call_sites``, never over this count).

    Line-terminator-agnostic by construction: it reads the line list the detector already
    holds -- since Story 15.2 that is
    :func:`~argus.detectors.vacuous_test.index_aligned_lines`, not ``source.splitlines()`` --
    and ``\\r`` / ``\\r\\n`` cannot reach it at all, because the read path normalises them
    (``argus/pipeline_stages.py:124``). Under the corrected decomposition a line MAY now carry
    an exotic separator that ``splitlines()`` would have split on; measured, that changes
    neither this count nor the statement starts (see the module docstring).
    """
    return sum(
        _simple_statement_segments(text)
        for text in _counted_statement_texts(source_lines, start, end).values()
    )


def body_statement_count(source_lines: list[str], start: int, end: int) -> int:
    """:func:`logical_statement_count` of the BODY of the function whose ``def`` opens at *start*.

    The ``def`` header is the span's FIRST logical statement — however many lines its
    signature is wrapped over — so the body is everything else. Deriving it that way rather
    than "skip line *start*" is what makes a wrapped signature count zero body statements
    for its own continuation lines::

        def test_wrapped(          # ← the header opens here…
            a,
            b,
        ):                         # ← …and ends here; NONE of this is a body statement
            assert a               # ← 1

    A degenerate one-line ``def test_x(): assert 1`` therefore reports **0** body
    statements, which the caller reads as "no denominator" and does NOT flag — the safe
    direction, and byte-identical to what the line count it replaced did with it.
    """
    texts = _counted_statement_texts(source_lines, start, end)
    if not texts:
        return 0
    header = min(texts)
    return sum(
        _simple_statement_segments(text) for line, text in texts.items() if line != header
    )


def _statement_texts(source_lines: list[str], start: int, end: int) -> dict[int, str]:
    """1-based opening line → that whole logical statement's comment-free code text."""
    parts: dict[int, list[str]] = {}
    for line in _scan_span(source_lines, start, end):
        if line.opens is None:
            continue
        parts.setdefault(line.opens, []).append(line.code.strip())
    return {
        opens: " ".join(part for part in fragments if part)
        for opens, fragments in parts.items()
    }


def _is_continuation_clause_header(code: str) -> bool:
    """Whether *code* — ONE whole logical statement — is a bare continuation-clause header.

    ADDED 2026-08-18 (Story 14.2, review iteration 1), and the reason is a measurement that
    contradicted a claim rather than a preference. :func:`logical_statement_count`'s docstring
    asserted that its residual against CPython was *"a bounded under-count in the direction
    that RAISES density, i.e. away from a flag"*. Re-measured over the non-exact spans of the
    pinned corpora, **64 of 64** (minions) and **27 of 28** (agent-smith) were OVER-counts —
    the opposite direction, which LOWERS density and biases TOWARDS a flag. A claim about a
    SAFETY direction, stated backwards, in a detector whose method is "measured, not
    asserted".

    The dominant mechanism was this: :func:`_scan_span` opens a logical statement on every
    line that starts one, and an ``except`` / ``else`` / ``finally`` / ``case`` header starts
    a CLAUSE rather than a statement. ``try/except/else/finally`` scored **8** against
    CPython's **5**; two real corpus instances ran 15-vs-11 and 39-vs-35.

    Applied at the COUNT and deliberately not in :func:`_scan_span`, so that
    :func:`logical_statement_starts` — fact (b)'s boundary map, and Story 14.1's moat rests on
    it — is byte-identical: a call on a clause-header line is still attributed to that line.
    Fixing the denominator must not reach into the corroboration path (DN-14-2-1's coupling
    class, arriving through a different door).

    Error direction of the exclusion itself is the SAFE one, structurally rather than by
    hope: the denominator can only shrink, ``assertion_density`` can only rise, the ``1/4``
    floor fires from BELOW, and ``mock_ratio`` is taken over ``call_sites`` and never over the
    statement count — so nothing can GAIN a flag from it. Measured: **0** gained on both
    pinned corpora.
    """
    return _CONTINUATION_CLAUSE_RE.match(_blank_strings(code).strip()) is not None


def _is_decorator(code: str) -> bool:
    """Whether *code* — ONE whole logical statement — is a DECORATOR.

    A decorator is an expression CPython hangs off the ``FunctionDef``/``ClassDef`` it
    decorates (``decorator_list``); it is not an ``ast.stmt`` and adds none. ``@`` cannot
    BEGIN a Python expression — its only other uses, ``a @ b`` and ``a @= b``, both start at
    the left operand — so at a statement-start position this test is exact rather than
    heuristic. A decorator wrapped over several lines is assembled into one logical statement
    by :func:`_statement_texts` and is therefore excluded once, not once per line.

    Measured (Story 14.2, review iteration 1): after the clause-header rule above, this was
    the ONLY remaining over-count in the whole 4,673-function pinned population — one span,
    ``test_quality_gate_default_on.py::test_unevaluable_toggle_resolves_to_enforcing``, whose
    body defines a nested class carrying an ``@property``. Fixing it is what makes the
    residual's direction UNAMBIGUOUS, which is the point of the correction this pair of rules
    belongs to: what is left over-counts nothing and under-counts only the inline compound
    header, i.e. it can only RAISE density and only move AWAY from a flag.
    """
    return code.lstrip().startswith("@")


def _counted_statement_texts(
    source_lines: list[str], start: int, end: int
) -> dict[int, str]:
    """:func:`_statement_texts` minus the syntax CPython counts as no statement of its own.

    Two rules, each with its own predicate and its own measurement: a bare continuation-clause
    header (:func:`_is_continuation_clause_header`) and a decorator (:func:`_is_decorator`).
    Both are applied HERE, at the count, and never in :func:`_scan_span`, so
    :func:`logical_statement_starts` — fact (b)'s boundary map — is untouched.
    """
    return {
        opens: text
        for opens, text in _statement_texts(source_lines, start, end).items()
        if not _is_continuation_clause_header(text) and not _is_decorator(text)
    }


def _simple_statement_segments(code: str) -> int:
    """How many non-empty SIMPLE statements *code* — one whole logical statement — holds.

    ``sut(1, 2); result = sut(3, 4)`` is two; ``x = 1;`` is one (a trailing separator ends
    nothing new); ``pass`` is one. Reuses :func:`_simple_statement_breaks` so the ``;``
    rule has exactly one definition in this module.
    """
    breaks = _simple_statement_breaks(code)
    if not breaks:
        return 1 if code.strip() else 0
    bounds = (-1, *breaks, len(code))
    return sum(1 for lo, hi in zip(bounds, bounds[1:]) if code[lo + 1 : hi].strip())


def logical_statement_starts(
    source_lines: list[str], start: int, end: int
) -> dict[int, int]:
    """Map each 1-based line of the span to the FIRST line of its logical statement.

    The mirror image of :func:`_logical_statement_end`, and the reason it exists: a call
    site's own physical line is not the unit Python binds results in. Both continuation
    syntaxes put the assignment target on an EARLIER line than the call::

        result = (          # ← the statement starts here (PEP 8's preferred wrapping)
            add(1, 2)       # ← but this is where the 1.4 edge lands
        )

        result = \\          # ← and here
            add(1, 2)

    Reading only the call's own line makes both look like a bare expression statement
    whose result is thrown away, which promotes a test that genuinely constrains the SUT
    result to verdict-eligible — the exact false-accusation class Story 14.1 exists to
    close. Both syntaxes are handled by the SAME rule (a line is a continuation iff the
    bracket depth before it is positive OR the previous code line ended in a backslash OR a
    triple-quoted literal opened earlier is still open), because special-casing one of them
    leaves the other broken — and the third was added by Story 14.2 for exactly that reason.

    A line that is blank or comment-only at depth 0 opens nothing and is absent from the
    result. A caller that finds its line absent must treat the statement as unreadable —
    unresolvable is not evidence.

    A PROJECTION of :func:`_scan_span`, never a second walk of the same source (AR7/§3.3).
    """
    return {
        line.line_no: line.opens
        for line in _scan_span(source_lines, start, end)
        if line.opens is not None
    }


def _statement_code(source_lines: list[str], start_line: int, end_line: int) -> str:
    """The comment-free code text of lines *start_line*..*end_line*, joined by a space."""
    parts = [
        _code_prefix(source_lines[line_no - 1]).strip()
        for line_no in range(start_line, end_line + 1)
        if 0 <= line_no - 1 < len(source_lines)
    ]
    return " ".join(part for part in parts if part)


def _locate_call(line: str, callee: str, from_column: int = 0) -> tuple[str | None, int, int] | None:
    """Locate ``callee(`` on *line* at or after *from_column*.

    Returns ``(receiver-chain root, chain start column, match end column)``. The root is
    ``None`` for an unqualified call (``add(1, 2)``) and the leading identifier for a
    qualified one (``fake.calculate()`` → ``"fake"``).

    *from_column* is what lets one callee be called MORE THAN ONCE on one line. The Story
    1.4 ``CodeEdge`` carries a callee NAME and a line and **no column** (``DF-1-4-A``), so
    the two edges emitted for ``sut(1, 2); captured = sut(3, 4)`` are indistinguishable;
    searching from column 0 for each of them classified BOTH from the first occurrence,
    and the second — genuinely bound to ``captured`` — inherited the first one's "nothing
    precedes it" verdict. The caller therefore resumes each search past the END of the
    previous match for the same ``(line, callee)`` pair, so every edge consumes a DISTINCT
    occurrence. See :func:`provenance_evidence` for why distinctness is all that is needed
    and the index's edge ORDER is not.

    ``None`` is returned when the callee cannot be found at or after *from_column* — a call
    whose function expression spans lines or is computed, or an edge for which the line
    holds no further occurrence. That is NOT treated as an unqualified SUT call:
    unresolvable is not evidence, and the caller reads it as CONSUMED so no corroboration
    can rest on it.
    """
    pattern = re.compile(
        rf"(?<![\w.])(?P<prefix>(?:{_IDENT}\s*\.\s*)*){re.escape(callee)}\s*\("
    )
    match = pattern.search(_blank_strings(_code_prefix(line)), from_column)
    if match is None:
        return None
    prefix = match.group("prefix")
    root_match = re.match(rf"\s*({_IDENT})", prefix) if prefix else None
    return (root_match.group(1) if root_match else None), match.start(), match.end()


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


def _is_mock_derived(
    expression: str, mock_names: frozenset[str], mock_callees: frozenset[str]
) -> bool:
    """Whether *expression*'s value plausibly comes from a mock rather than the SUT.

    Two ways, both name-level: the chain is rooted at an already-mock-bound name
    (``fake.calculate()``), or some component of the leading chain is a mock
    construction primitive (``Mock()``, ``unittest.mock.patch(...)``).
    """
    chain = _leading_chain(expression)
    if not chain:
        return False
    return chain[0] in mock_names or any(part in mock_callees for part in chain)


def _simple_statement_breaks(code: str) -> tuple[int, ...]:
    """Columns of *code*'s depth-0 ``;`` — where one SIMPLE statement ends and the next begins.

    A ``;`` is the only thing in Python that puts two simple statements on one logical
    line, and it is the unit fact (b) actually reasons about: ``sut(1, 2); result =
    sut(3, 4)`` is *two* statements, one of which binds the SUT result. Depth- and
    string-aware, so a ``;`` inside a call's arguments, a literal or a slice is not a
    separator. On text that starts mid-statement the depth can only be understated, so
    the count is clamped at zero — the same convention
    :func:`_logical_statement_end` uses.
    """
    masked = _blank_strings(code)
    depth = 0
    breaks: list[int] = []
    for column, char in enumerate(masked):
        if char in _OPEN_BRACKETS:
            depth += 1
        elif char in _CLOSE_BRACKETS:
            depth = max(depth - 1, 0)
        elif char == ";" and depth == 0:
            breaks.append(column)
    return tuple(breaks)


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


def _mock_bound_names(
    source_lines: list[str], start: int, end: int, mock_callees: frozenset[str]
) -> frozenset[str]:
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
            if _is_mock_derived(header, frozenset(bound), mock_callees):
                bound.update(_AS_BINDING_RE.findall(_blank_strings(header)))
            continue
        assignment = _ASSIGNMENT_RE.match(code)
        if assignment is None:
            continue
        if not _is_mock_derived(assignment.group("value"), frozenset(bound), mock_callees):
            continue
        for target in assignment.group("targets").split(","):
            name = target.strip()
            if name and "." not in name:
                bound.add(name)
    return frozenset(bound)


class ProvenanceEvidence(NamedTuple):
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
    source_lines: list[str],
    span_edges: list[CodeEdge],
    start: int,
    end: int,
    assertion_callees: frozenset[str],
) -> tuple[int, ...]:
    """1-based first lines of the span's assertion statements, SORTED (AR11).

    Both spellings the heuristic already counts: a bare ``assert`` (read from the
    source, since it is not a call node) and a call to an assertion primitive.
    """
    lines: set[int] = set()
    for line_no in range(start, end + 1):
        index = line_no - 1
        if 0 <= index < len(source_lines) and opens_bare_assert(
            _code_prefix(source_lines[index]).lstrip()
        ):
            lines.add(line_no)
    lines.update(edge.line for edge in span_edges if edge.callee in assertion_callees)
    return tuple(sorted(lines))


def provenance_evidence(
    source_lines: list[str],
    span_edges: list[CodeEdge],
    start: int,
    end: int,
    *,
    assertion_callees: frozenset[str],
    mock_callees: frozenset[str],
) -> ProvenanceEvidence:
    """Fact (b)'s evidence over the span: is the SUT result thrown away, and are the
    assertions looking at a mock instead? PURE — source text and the 1.4 edge set only.

    The classification is made about the SIMPLE STATEMENT containing the call — the
    ``;``-delimited unit, spanning however many physical lines it was wrapped over — never
    about the call's own physical line: a SUT call is DISCARDED only when its statement is
    that call and nothing else. Every other outcome — bound to a name on a wrapped or
    backslash-continued line, nested in another expression, asserted on, compared, chained,
    unreadable — is CONSUMED, which withholds corroboration.

    Occurrence resolution, and why edge ORDER does not matter
    ---------------------------------------------------------
    An edge is ``(callee, line)`` with no column, so k calls to one name on one line emit k
    indistinguishable edges. Each is given its OWN occurrence by resuming the search past
    the previous match for that pair (``_locate_call``'s ``from_column``). It is worth being
    precise about what that does and does not assume: the index does **not** emit these in
    source order — ``ast_index._extract`` walks with ``stack.pop()``/``stack.extend``, which
    visits siblings right to left, and the AR11 ``(line, callee)`` sort is stable. It does
    not need to. Every count below is a pure function of the occurrence an edge is assigned,
    so any one-to-one assignment of the k edges to the k occurrences produces the same
    counts. What must hold is DISTINCTNESS, which the cursor guarantees; ordering is free.
    And when a line holds fewer occurrences than edges, the surplus resolve to ``None`` and
    count CONSUMED — the failure direction is always away from an accusation.
    """
    mock_names = _mock_bound_names(source_lines, start, end, mock_callees)
    observed_lines = _result_observing_lines(source_lines, start, end)
    statement_starts = logical_statement_starts(source_lines, start, end)

    discarded = 0
    consumed = 0
    next_occurrence: dict[tuple[int, str], int] = {}
    for edge in span_edges:
        if (
            edge.callee in assertion_callees
            or edge.callee in mock_callees
            or edge.callee in RESULT_OBSERVING_CONTEXT_CALLEES
        ):
            continue
        index = edge.line - 1
        if index < 0 or index >= len(source_lines):
            consumed += 1  # off-span edge: cannot be read, so it cannot corroborate
            continue
        occurrence_key = (edge.line, edge.callee)
        located = _locate_call(
            source_lines[index], edge.callee, next_occurrence.get(occurrence_key, 0)
        )
        if located is None:
            consumed += 1  # unresolvable is not evidence (see _locate_call)
            continue
        receiver_root, chain_start, match_end = located
        next_occurrence[occurrence_key] = match_end  # this edge has claimed this occurrence
        if receiver_root is not None and receiver_root in mock_names:
            continue  # a mock-derived call, not a SUT call
        if edge.line in observed_lines:
            consumed += 1  # DN-3: raising IS the observation
            continue
        statement_start = statement_starts.get(edge.line)
        if statement_start is None:
            consumed += 1  # the line opens no readable statement — not evidence
            continue
        statement_end = _logical_statement_end(source_lines, statement_start, end)
        line_code = _code_prefix(source_lines[index])
        # Everything of the LOGICAL statement that precedes the call, across however
        # many physical lines it was wrapped over, trimmed to the SIMPLE statement the
        # call is in — text before a depth-0 ``;`` belongs to an earlier statement and
        # says nothing about where THIS call's result goes. Empty (or a bare ``await``)
        # is what makes this an expression statement whose value nothing receives.
        before = (
            _statement_code(source_lines, statement_start, edge.line - 1)
            + line_code[:chain_start]
        )
        breaks_before = _simple_statement_breaks(before)
        preceding = (before[breaks_before[-1] + 1 :] if breaks_before else before).strip()
        # …and the same statement, forwards: from the call to the next depth-0 ``;`` or
        # the end of the logical statement. Ending in ``)`` is what says the statement
        # IS the call rather than the call plus something that reads its value.
        after = line_code[chain_start:] + " " + _statement_code(
            source_lines, edge.line + 1, statement_end
        )
        breaks_after = _simple_statement_breaks(after)
        statement = (after[: breaks_after[0]] if breaks_after else after).strip()
        if preceding in ("", "await") and statement.endswith(")"):
            discarded += 1
        else:
            consumed += 1

    mock_referencing = 0
    for line_no in _assertion_statement_lines(
        source_lines, span_edges, start, end, assertion_callees
    ):
        statement_end = _logical_statement_end(source_lines, line_no, end)
        statement = _blank_strings(_statement_code(source_lines, line_no, statement_end))
        if any(name in mock_names for name in _CHAIN_ROOT_RE.findall(statement)):
            mock_referencing += 1

    return ProvenanceEvidence(discarded, consumed, mock_referencing)
