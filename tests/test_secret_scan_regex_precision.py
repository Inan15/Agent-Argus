"""Story 18.3 / DF-AUD-DETECT-E - the two regex precision defects in ``secret_scan``.

Verification area ArgusAgent-SECRET (``TC-ArgusAgent-SECRET-002-08``..``-12``, CONTINUING the
``SECRET-002`` index whose prior maximum is ``-07``; nothing is renumbered). ``SECRET-002``'s
charter is the PRECISION of this detector: ``tests/test_secret_scan_precision.py`` pins the three
PREDICATES (``_is_entropy_candidate`` / ``_has_no_whitespace`` / ``_has_letter_digit_mix``) and says
nothing at all about the REGEXES. This module pins the regexes, which is the half
``DF-AUD-DETECT-E`` found unguarded.

**DEFECT 1 - no left anchor.** ``_GENERIC_ASSIGN_RE`` anchored nothing to the left of
``api[_-]?key|secret|token|password|passwd|pwd``, so an innocent identifier whose tail happens to
contain a key word matched the alternation. Driven through the shipped ``SecretScanDetector.run()``
on the NON-TEST path ``argus/prod/settings.py``, one line each, on 2026-08-25 at HEAD ``62fd1b9``::

    topsecret    = "correct-horse-battery-staple"   -> 1 finding  [generic_assigned_secret]
    mytoken      = "correct-horse-battery-staple"   -> 1 finding  [generic_assigned_secret]
    notapassword = "correct-horse-battery-staple"   -> 1 finding  [generic_assigned_secret]

Over ``argus/**`` (95 files) the shipped pattern produced **3** matches with a word character
immediately left of the key, **1** of them inside a comment line - the entry's own census,
re-derived rather than cited, reproducing at the same paths.

**THE OBVIOUS REPAIR IS A MEASURED FALSE GREEN, WHICH IS WHY ``-09`` EXISTS.** ``DF-AUD-DETECT-E``
proposes *"a negative lookbehind before the alternation"*. Its ordinary spelling is the word-
boundary one, ``(?<![A-Za-z0-9_])`` - and every one of this repository's own word-char-left matches
is preceded by ``_``, not by a letter. Executed, one line each, on the same non-test path::

    source                                  shipped   (?<![A-Za-z0-9_])   (?<![A-Za-z0-9])
    DB_PASSWORD   = "Tr0ub4dor3xKqmZw91"       1            0                   1
    _API_KEY      = "sk-test-do-not-leak-me"   1            0                   1
    SMTP_PASSWORD = "aBcD1234EfGh5678"         1            0                   1
    topsecret     = "correct-horse-..."        1            0                   0

The ``_``-including spelling turns a precision defect into a RECALL defect on ``UPPER_SNAKE_CASE``,
the single most common real-world credential-naming convention there is, where ``_`` is a SEPARATOR
and not a word character that could make ``PASSWORD`` part of a larger innocent word. The whole
1,724-test suite under that spelling goes RED at exactly one case -
``TC-ArgusAgent-SECRET-001-26``, Story 18.1's live-key safeguard. The repair taken here therefore
excludes LETTERS AND DIGITS ONLY and ADMITS ``_`` (``DN-18-3-1``).

**DEFECT 2 - unpaired delimiters, at THREE sites and not the one the entry names.** Every
quoted-literal pattern in the module opened with a bare two-member delimiter class and closed with
an INDEPENDENT copy of it, so a span opened with ``'`` and closed with ``"`` was accepted as one
literal. The entry names only ``_ANY_LITERAL_RE``; ``_AWS_SECRET_KEY_RE`` and
``_GENERIC_ASSIGN_RE`` carry the identical shape. Over ``argus/**``: **462** spans whose opening
and closing delimiters DIFFER, **3** of them surviving ``_is_entropy_candidate`` and therefore
reportable - one of which was ``secret_scan.py``'s own regex source line. Measured: pairing all
three sites is OUTPUT-IDENTICAL to pairing only ``_ANY_LITERAL_RE`` over all 252 tracked files, so
the wider repair costs nothing measurable and removes the class rather than one instance
(``DN-18-3-2``).

**DEFECT 2 ALSO UNDER-REPORTS, AND THAT FALSIFIES THE ENTRY'S SEVERITY RATIONALE.**
``DF-AUD-DETECT-E`` files itself green on *"the error direction is OVER-reporting, never a false
green"*. Measured false. The scanner is left-to-right and non-overlapping: an outer ``'`` opens a
span, the negated class eats the assignment prefix, the INNER OPENING ``"`` is accepted as the
closing delimiter, ``finditer`` resumes INSIDE the credential, and the real literal is never
offered to ``_is_entropy_candidate`` at all. Through the shipped ``run()`` on the non-test path::

    src = 'blob = "aZ9kPqW3mX7vL2cR8tY4nB6h"'   shipped -> 0 findings
                                                paired  -> 1 finding  [high_entropy_string]

At the raw ``_scan`` level over 252 tracked files the paired engine finds 13 matches the shipped
engine does not, at 12 distinct sites, ten of them canonical credential shapes (``AKIA...``, an AWS
secret key, a ``ghp_`` token, two ``postgres://`` URLs with an inline password). ``-11`` is the
guard that pins this direction.

**WHAT THE REPAIR MOVES, so no reader mistakes this module for an output-neutral one.**
Engine-vs-engine over one identical 252-file population, comparing the FULL ``DetectorResult`` per
file: **91 -> 90** ``hardcoded_secret`` findings over **38 -> 37** files, five spans moving. The
three removals are an f-string fragment in ``argus/audit/open_llm_adapter.py``, this module's
subject's own regex source line, and an f-string fragment in ``argus/precision/gate_decision.py`` -
not one of them a credential. Nothing that was a real secret stops being reported.

**RED evidence (AI-E14-1).** Every case here was run against the SHIPPED module body before the
repair existed, by monkeypatching the shipped regexes from a copy held OUTSIDE the repository.
``-08``, ``-10``, ``-11`` and ``-12`` go RED. ``-09`` stays GREEN **by design** and must hold
BEFORE and AFTER: it is a CONTRACT PIN fencing out the mis-repair the ledger entry recommends, not
a defect witness, and its non-vacuity is proven separately by executing it against the naive
lookbehind, where it goes RED (``DN-18-3-8``). The raw failure text is in the story's Dev Agent
Record. Per the guard-fire rule this author-driven RED is **vacuity evidence** - proof the cases
can fail - not "these guards caught a defect".

**Every case runs on the NON-TEST path** ``argus/prod/settings.py``: a case built on a ``tests/**``
path would be suppressed by ``DEFAULT_TEST_PATH_PATTERNS`` for an entirely unrelated reason and
would assert nothing at all. That path is never opened - ``run()`` is pure (AR8) and uses
``file_path`` only for glob matching and locators - and it does not exist on disk and must not be
created.

**Key material here is synthetic and built in this module**, never planted in a committed fixture
file (NFR-S1 / NFR-S2), and no chosen value is a member of the Story 18.1 public-sentinel table -
a value carrying ``example.com`` or ``localhost`` is SUPPRESSED and would say nothing about any
regex. Every assertion is on a count, a ``pattern_id``, a ``rule_id`` or an absence, never on a
secret value. Every case asserts its population is non-empty BEFORE asserting an absence
(AI-E11-1).

Counts are asserted as ``>= 1`` or by pattern-id membership, never as an exact total: ``run()``
de-duplicates on ``(start_line, end_line, pattern_id)``, so one source line legitimately yields more
than one finding.

**What this module does NOT claim.** The scan is still not a Python tokenizer; pairing the
delimiters realigns it, it does not make it token-accurate, and a literal containing its own
delimiter stays invisible to it (``DN-18-3-5``). Prose in a comment still matches - the detector has
no comment model. A JSON-style mapping from a quoted key to a quoted value is still not matched.
All three are DISCLOSED in the docstring of the module under repair and in the story record; none
is fixed here.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import argus.detectors.secret_scan as secret_scan
from argus.detectors.secret_scan import RULE_HARDCODED_SECRET, SecretScanDetector
from argus.index.ast_index import AstIndexEntry

#: The non-test path every case runs on. Never opened; ``run()`` is pure (AR8) and uses
#: ``file_path`` only for glob matching and locators. It does not exist on disk and must not
#: be created.
_NON_TEST_PATH = "argus/prod/settings.py"

#: The module under guard, resolved from THIS file rather than from a hard-coded absolute path,
#: so the source-level guard travels with the repository (AI-E13-1: CI runs an ubuntu matrix).
_SECRET_SCAN_PATH = (
    Path(__file__).resolve().parent.parent / "argus" / "detectors" / "secret_scan.py"
)

#: Synthetic key material, built here (NFR-S1 / NFR-S2). None of these values is a member of the
#: Story 18.1 public-sentinel table, and none is a live credential.
#:
#: ``_INNOCENT_VALUE`` is deliberately DIGIT-FREE so ``_has_letter_digit_mix`` rejects it: a value
#: that is ALSO a legitimate ``high_entropy_string`` would let ``-08`` pass for a reason that has
#: nothing to do with the left anchor (the guard-vacuity trap).
_INNOCENT_VALUE = "correct-horse-battery-staple"
#: A credential-shaped value: a single token mixing letters AND digits.
_SECRET_VALUE = "Tr0ub4dor3xKqmZw91"
#: The same, extended past ``MIN_ENTROPY_TOKEN_LENGTH`` so the entropy family reaches it too.
_ENTROPY_VALUE = "Tr0ub4dor3xKqmZw91abcd"
#: A 40-character base64-ish value, the shape ``_AWS_SECRET_KEY_RE`` requires.
_AWS_SECRET_VALUE = "wZ9kPqW3mX7vL2cR8tY4nB6hJ5sD1fG2hK3lM4nP"
#: The credential nested inside a single-quoted wrapper - the entry's falsified severity claim.
_NESTED_VALUE = "aZ9kPqW3mX7vL2cR8tY4nB6h"

#: The ``pattern_id`` the left anchor and the generic delimiter repair govern.
_GENERIC = "generic_assigned_secret"
#: The ``pattern_id`` the AWS delimiter repair governs.
_AWS_SECRET = "aws_secret_access_key"
#: The ``pattern_id`` the ``_ANY_LITERAL_RE`` delimiter repair governs.
_ENTROPY = "high_entropy_string"

#: The module's LOCKED regex constants. ``-12`` asserts all of them still compile, so it cannot
#: pass by a pattern having vanished rather than by the class having been repaired.
_LOCKED_PATTERN_CONSTANTS = (
    "_AWS_ACCESS_KEY_RE",
    "_AWS_SECRET_KEY_RE",
    "_PEM_PRIVATE_KEY_RE",
    "_GENERIC_ASSIGN_RE",
    "_ANY_LITERAL_RE",
)

#: The bare two-member character class both defects are spelled with, built rather than typed so
#: this module's own source does not carry the very shape ``-12`` forbids (it reads
#: ``secret_scan.py`` only, but a literal copy here is a trap for the next grep).
_DELIMITER_CLASS = "[" + chr(39) + chr(92) + chr(34) + "]"

#: A named-group opener immediately before a delimiter class is what PAIRING looks like:
#: ``(?P<q>...)`` captures the opening delimiter so ``(?P=q)`` can require the same one to close.
_NAMED_GROUP_OPEN = re.compile(r"\(\?P<\w+>$")


def _entry(file_path: str = _NON_TEST_PATH) -> AstIndexEntry:
    """The 1.4 entry, constructed directly - no tree-sitter (``test_secret_scan``'s precedent)."""
    return AstIndexEntry(file_path=file_path, ast_eligible=True, definitions=(), edges=())


def _findings(source: str, *, file_path: str = _NON_TEST_PATH) -> list:
    """Every ``hardcoded_secret`` finding the detector reports for *source*."""
    result = SecretScanDetector().run(
        file_path=file_path, source=source, ast_entry=_entry(file_path)
    )
    return [f for f in result.findings if f.rule_id == RULE_HARDCODED_SECRET]


def _pattern_ids(source: str) -> tuple[str, ...]:
    """The ``pattern_id`` of every raw match, sorted.

    Read off ``_scan`` rather than counted off ``findings``: ``run()`` de-duplicates on
    ``(start_line, end_line, pattern_id)``, so a case about ONE family must name that family
    rather than assert a total.
    """
    return tuple(sorted(m.pattern_id for m in SecretScanDetector()._scan(source)))


def _module_pattern_sources() -> dict[str, str]:
    """Every module-level ``_*_RE = re.compile(<literal>)`` pattern STRING, by constant name.

    A source-level read, not a read of the compiled objects: the defect is a property of the
    pattern TEXT a future editor would type. Adjacent string literals are folded by the parser,
    so a pattern split across source lines arrives here as one string.
    """
    tree = ast.parse(_SECRET_SCAN_PATH.read_text(encoding="utf-8"))
    found: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or not target.id.endswith("_RE"):
            continue
        call = node.value
        if not isinstance(call, ast.Call) or not call.args:
            continue
        literal = call.args[0]
        if isinstance(literal, ast.Constant) and isinstance(literal.value, str):
            found[target.id] = literal.value
    return found


def _unpaired_delimiter_classes(pattern: str) -> tuple[int, ...]:
    """Offsets of every delimiter class in *pattern* that is NOT captured into a named group.

    A PAIRED pattern spells the delimiter class ONCE, captures it, and closes the literal with a
    backreference to that group. An UNPAIRED pattern spells it TWICE, uncaptured - and two
    independent copies of a two-member class accept four delimiter combinations where only two
    are a real literal. The predicate is therefore "is this class captured", not "how many are
    there": counting would forbid the repaired spelling too.
    """
    offsets: list[int] = []
    start = 0
    while True:
        index = pattern.find(_DELIMITER_CLASS, start)
        if index == -1:
            return tuple(offsets)
        if _NAMED_GROUP_OPEN.search(pattern[:index]) is None:
            offsets.append(index)
        start = index + 1


# ---------------------------------------------------------------------------------------------
# TC-ArgusAgent-SECRET-002-08 - THE LEFT ANCHOR
# ---------------------------------------------------------------------------------------------


def test_TC_ArgusAgent_SECRET_002_08_an_identifier_ending_in_a_key_word_is_not_a_secret() -> None:
    """TC-ArgusAgent-SECRET-002-08 - AC1.1/AC4.2: the key alternation is anchored on its left.

    **Observable:** whether ``topsecret``, ``mytoken`` and ``notapassword`` - three identifiers
    whose only relation to a credential is that a key word is a SUFFIX of them - still produce a
    ``generic_assigned_secret`` match. **Measured RED against the shipped body:** each produced
    exactly one, which is ``DF-AUD-DETECT-E``'s defect 1 verbatim.

    The value is deliberately digit-free so ``_has_letter_digit_mix`` rejects it. A value that is
    ALSO a legitimate ``high_entropy_string`` would make the absence assertion pass for a reason
    that has nothing to do with the left anchor - the guard-vacuity trap this repository keeps
    catching (AI-E14-1).
    """
    control = 'password = "' + _INNOCENT_VALUE + '"\n'

    # AI-E11-1: the population is proven non-empty BEFORE anything is asserted absent. A real key
    # word in the SAME position with the SAME value must still be reported, or the three absences
    # below would be evidence of nothing but a broken fixture.
    assert _GENERIC in _pattern_ids(control), (
        "the positive control reports no generic_assigned_secret: the absences asserted below "
        "would be vacuous"
    )
    assert len(_findings(control)) >= 1

    for identifier in ("topsecret", "mytoken", "notapassword"):
        source = identifier + ' = "' + _INNOCENT_VALUE + '"\n'
        assert _GENERIC not in _pattern_ids(source), (
            f"{identifier!r} still matches the key alternation: the alternation is not anchored "
            f"on its left (DF-AUD-DETECT-E defect 1)"
        )
        assert _findings(source) == [], (
            f"{identifier!r} is still reported as a hardcoded secret"
        )


# ---------------------------------------------------------------------------------------------
# TC-ArgusAgent-SECRET-002-09 - THE FALSE-GREEN FENCE (a contract pin, NOT a defect witness)
# ---------------------------------------------------------------------------------------------


def test_TC_ArgusAgent_SECRET_002_09_the_left_anchor_admits_underscore_so_snake_names_survive() -> None:
    """TC-ArgusAgent-SECRET-002-09 - AC1.1/AC3.4/AC4.3: the FENCE around the mis-repair.

    **THIS CASE IS GREEN BEFORE AND AFTER THE STORY, BY DESIGN.** It is a CONTRACT PIN, not a
    defect witness, and calling it "a guard that caught a defect" would be the over-claim the
    guard-fire rule exists to prevent (``DN-18-3-8`` / AI-E14-1). What it fences is the repair
    ``DF-AUD-DETECT-E`` itself recommends, taken in its ordinary spelling.

    **The mis-repair it fences out.** ``(?<![A-Za-z0-9_])`` - the textbook word boundary - reads
    like the correct anchor and is a measured SECURITY REGRESSION: executed, it drops the first
    four rows below to ZERO findings, because ``_`` in ``DB_PASSWORD`` is a SEPARATOR, not a word
    character that could make ``PASSWORD`` part of a larger innocent word. The anchor taken
    instead excludes LETTERS AND DIGITS ONLY.

    **Non-vacuity, proven rather than asserted:** this case was EXECUTED against the naive
    lookbehind and goes RED there. ``TC-ArgusAgent-SECRET-001-26`` (Story 18.1's live-key
    safeguard) is the corroborating END-TO-END witness: it is the ONLY case in the whole
    1,724-test suite that the naive spelling reddens, and if it ever goes RED alongside this one
    the fault is the lookbehind, never the guard.
    """
    # AC3.4's naming matrix in full: every shape a credential is really named with.
    naming_matrix = (
        ("DB_PASSWORD", 'DB_PASSWORD = "' + _SECRET_VALUE + '"\n'),
        ("_API_KEY", '_API_KEY = "' + _SECRET_VALUE + '"\n'),
        ("SMTP_PASSWORD", 'SMTP_PASSWORD = "' + _SECRET_VALUE + '"\n'),
        ("API_TOKEN", 'API_TOKEN = "' + _SECRET_VALUE + '"\n'),
        ("self.token", 'self.token = "' + _SECRET_VALUE + '"\n'),
        ("password", 'password = "' + _SECRET_VALUE + '"\n'),
        ("api-key", 'api-key = "' + _SECRET_VALUE + '"\n'),
        ("api_key", 'api_key = "' + _SECRET_VALUE + '"\n'),
    )
    for label, source in naming_matrix:
        assert _GENERIC in _pattern_ids(source), (
            f"the ordinary credential assignment {label!r} stopped matching the key alternation: "
            f"the left anchor excludes '_' and has inverted a precision fix into a recall "
            f"regression (DN-18-3-1)"
        )
        assert len(_findings(source)) >= 1, (
            f"{label!r} is no longer reported as a hardcoded secret at all"
        )


# ---------------------------------------------------------------------------------------------
# TC-ArgusAgent-SECRET-002-10 - PAIRED DELIMITERS, ALL THREE SITES
# ---------------------------------------------------------------------------------------------


def test_TC_ArgusAgent_SECRET_002_10_a_literal_must_close_with_the_delimiter_it_opened_with() -> None:
    """TC-ArgusAgent-SECRET-002-10 - AC1.2/AC4.4: no span opened with one quote closes with the other.

    **Observable:** whether a span whose opening and closing delimiters DIFFER is still accepted
    as one quoted literal, at EACH of the three sites that carried the shape - ``_ANY_LITERAL_RE``
    (``high_entropy_string``), ``_GENERIC_ASSIGN_RE`` (``generic_assigned_secret``) and
    ``_AWS_SECRET_KEY_RE`` (``aws_secret_access_key``). **Measured RED against the shipped body:**
    all three accepted it.

    Repairing only the site ``DF-AUD-DETECT-E`` names would leave ``_AWS_SECRET_KEY_RE`` carrying
    the defect - and that very line is ITSELF one of the three surviving over-reports this story
    is chartered to remove (``DN-18-3-2``).

    Each mismatched case is paired with BOTH matched-delimiter controls at the same site, asserted
    FIRST (AI-E11-1), so an absence can never be evidence of a fixture that matches nothing.
    """
    single = chr(39)
    double = chr(34)
    cases = (
        (
            _ENTROPY,
            "x = " + single + _ENTROPY_VALUE + double + "\n",
            (
                "x = " + single + _ENTROPY_VALUE + single + "\n",
                "x = " + double + _ENTROPY_VALUE + double + "\n",
            ),
        ),
        (
            _GENERIC,
            "password = " + single + _ENTROPY_VALUE + double + "\n",
            (
                "password = " + single + _ENTROPY_VALUE + single + "\n",
                "password = " + double + _ENTROPY_VALUE + double + "\n",
            ),
        ),
        (
            _AWS_SECRET,
            "aws_secret_access_key = " + single + _AWS_SECRET_VALUE + double + "\n",
            (
                "aws_secret_access_key = " + single + _AWS_SECRET_VALUE + single + "\n",
                "aws_secret_access_key = " + double + _AWS_SECRET_VALUE + double + "\n",
            ),
        ),
    )
    for pattern_id, mismatched, controls in cases:
        for control in controls:
            assert pattern_id in _pattern_ids(control), (
                f"the matched-delimiter control for {pattern_id} reports nothing: the mismatch "
                f"assertion below would be vacuous"
            )
            assert len(_findings(control)) >= 1
        assert pattern_id not in _pattern_ids(mismatched), (
            f"a span opened with one quote and closed with the other is still accepted by the "
            f"{pattern_id} pattern: its open and close delimiters are independent character "
            f"classes (DF-AUD-DETECT-E defect 2)"
        )


# ---------------------------------------------------------------------------------------------
# TC-ArgusAgent-SECRET-002-11 - THE REALIGNMENT RECALL
# ---------------------------------------------------------------------------------------------


def test_TC_ArgusAgent_SECRET_002_11_an_unpaired_span_no_longer_eats_an_opening_quote() -> None:
    """TC-ArgusAgent-SECRET-002-11 - AC4.5: defect 2 UNDER-reports, which the entry denied.

    **Observable:** whether a real, entropy-qualifying credential nested inside a single-quoted
    wrapper is reported at all. **Measured RED against the shipped body: ZERO findings.**

    **The mechanism, and why this is a false green and not noise.** ``finditer`` is left-to-right
    and non-overlapping. The outer quote opens a span, the negated class eats the assignment
    prefix, the INNER OPENING quote is accepted as the closing delimiter, the span is consumed,
    and the scan resumes INSIDE the credential - where the remaining text can no longer form a
    literal. The real value is never offered to ``_is_entropy_candidate``. The defect does not
    merely add noise; it eats a credential's opening quote and takes the credential with it.

    This is the case that falsifies ``DF-AUD-DETECT-E``'s own severity rationale - *"the error
    direction is OVER-reporting, never a false green"* - and it is why that severity is corrected
    in the entry's dated disposition note rather than left standing.
    """
    single = chr(39)
    double = chr(34)
    source = "src = " + single + "blob = " + double + _NESTED_VALUE + double + single + "\n"

    # AI-E11-1 in its recall direction: the same value in an ordinary matched-delimiter literal
    # MUST be reported, or the assertion below would be pinning the entropy predicate's opinion of
    # the value rather than the scanner's alignment.
    control = "blob = " + double + _NESTED_VALUE + double + "\n"
    assert _ENTROPY in _pattern_ids(control), (
        "the un-nested control is not an entropy candidate: this case would assert nothing about "
        "delimiter pairing"
    )

    assert _ENTROPY in _pattern_ids(source), (
        "a credential nested inside a single-quoted wrapper is invisible to the scan: the "
        "unpaired delimiters consumed its opening quote (DF-AUD-DETECT-E, severity rationale "
        "falsified)"
    )
    assert len(_findings(source)) >= 1


# ---------------------------------------------------------------------------------------------
# TC-ArgusAgent-SECRET-002-12 - THE CLASS GUARD
# ---------------------------------------------------------------------------------------------


def test_TC_ArgusAgent_SECRET_002_12_no_pattern_pairs_two_independent_delimiter_classes() -> None:
    """TC-ArgusAgent-SECRET-002-12 - AC1.2/AC4.6: the CLASS, not one instance of it.

    **Observable:** whether any module-level pattern constant in ``argus/detectors/secret_scan.py``
    still spells a quoted literal with two INDEPENDENT delimiter character classes. **Measured RED
    against the shipped body:** three did - ``_AWS_SECRET_KEY_RE``, ``_GENERIC_ASSIGN_RE`` and
    ``_ANY_LITERAL_RE`` - while ``DF-AUD-DETECT-E`` names only the third.

    Repairing one of three occurrences of a defect class inside one module is the half-repair this
    repository keeps catching. This case makes the class unable to come back by any route, because
    it reads the module's SOURCE rather than a list of names some future edit could grow past.

    **Scope:** the pattern constants of THIS module. It is deliberately NOT a blanket rule over
    the repository - a regex elsewhere with independent delimiter classes may be entirely correct
    for its own job, and asserting otherwise would be a rule nobody agreed to.

    **Non-vacuity is asserted first and twice:** every LOCKED pattern constant must still compile,
    and the delimiter class must still be PRESENT in at least three of them. A guard that passed
    because the regexes had vanished would be worse than no guard at all.
    """
    patterns = _module_pattern_sources()

    # Non-vacuity (i): the guard cannot pass by a pattern family having disappeared.
    for name in _LOCKED_PATTERN_CONSTANTS:
        assert name in patterns, (
            f"{name} is no longer a module-level re.compile of a string literal: this guard "
            f"would pass by the pattern having vanished rather than by the class being repaired"
        )
        assert isinstance(getattr(secret_scan, name), re.Pattern), f"{name} does not compile"

    # Non-vacuity (ii): the delimiter class must still be spelled in the three quoted-literal
    # patterns, or the assertion below is satisfied by a module that no longer scans literals.
    carriers = sorted(n for n, p in patterns.items() if _DELIMITER_CLASS in p)
    assert len(carriers) >= 3, (
        f"only {len(carriers)} pattern constant(s) still spell a delimiter class ({carriers!r}): "
        f"the module has stopped matching quoted literals and this guard asserts nothing"
    )

    offenders = {
        name: _unpaired_delimiter_classes(pattern)
        for name, pattern in patterns.items()
        if _unpaired_delimiter_classes(pattern)
    }
    assert offenders == {}, (
        f"pattern constant(s) still open and close a literal with two INDEPENDENT delimiter "
        f"classes, so a span opened with one quote can close with the other: {sorted(offenders)} "
        f"(DF-AUD-DETECT-E defect 2 - the class, not one instance)"
    )
