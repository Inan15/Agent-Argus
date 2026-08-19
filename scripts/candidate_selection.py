"""Story 15.1 — the SELECTION harness: every criterion decided WITHOUT the detector.

    from candidate_selection import measure_candidate, CRITERIA, candidate_row_defects

**What this module is for.** Epic 15 exists because Story 13.5 re-measured the >=80% precision
gate through the corrected instrument and the pin-verified reader and returned
``outcome = BLOCKED``, ``precision = UNEVALUABLE`` — **0 blocking findings over 1,960
pin-verified files**. An empty precision denominator is ``UNEVALUABLE`` by construction. Clearing
the gate needs findings that are REAL, which needs a bench that **contains the defect class**.

This module selects that bench's *candidates*. It does **not** ratify them: protocol section 6 R2
says, verbatim, *"Choosing which repositories are legitimate members, and fetching third-party
source, are not autonomous acts"*. Selection is prepared here; the decision stays the operator's.

**THE LINE THIS MODULE IS BUILT AROUND**

    A criterion may reference the defect's DEFINITION.
    A criterion may never reference the tool's VERDICT.

Selecting repositories likely to contain the defect is ordinary benchmark design — a bench for a
null-pointer analyser is chosen from code that dereferences pointers. Selecting repositories the
detector already flagged is criterion-shopping wearing public repositories as a disguise, and it
is the same fallacy the Story 13.1 amendment already rejected by name when it refused *"an
externalization gate clearable by a corpus the team authored, planted, and wrote the answers
for."*

**THE IMPORT BAN, AND WHY IT IS DRAWN WHERE IT IS.** This module may import ``argus.index.*`` and
must **NEVER** import ``argus.detectors.*``. The index measures whether a test is **visible** —
the instrument's *reach*. The detector measures whether a test is **guilty** — the instrument's
*output*. Sizing a candidate's scorable population is measuring reach; reading a verdict is
looking. The ban is enforced by an ``ast`` walk in
``TC-ArgusAgent-PRECISION-001-74``, not by this paragraph — which is what converts *"we did not
look"* from a promise into a property.

One visible consequence of the ban: :func:`is_scorable_test_definition` **restates** the
detector's test-function rule instead of importing ``_is_test_function`` from
``argus/detectors/vacuous_test.py``. That duplication is deliberate and is the price of the ban.
It is not a fork of behaviour — the rule is three lines of predicate, it is quoted from the
detector's own contract, and the guard that matters (the ban) is worth more than the de-dup.

**READS ARE FROM THE PINNED OBJECT DATABASE, NEVER THE WORKING TREE.** Story 13.5 established
that ``git rev-parse HEAD == pin`` and *"the audited bytes are the pinned bytes"* are two
different claims: ``agent-smith`` was ON its pin with 16 dirty entries and still reported
``byte_reproducible_across_two_runs = True``, because two runs over the same wrong bytes are
reproducible. Every read here goes through :mod:`pinned_corpus_snapshot`'s ``ls-tree`` +
``cat-file`` path. ``minions`` drifted off its pin three times in one session; a working-tree
read would have measured a tree nobody named.

**NOTHING HERE FETCHES.** ``DN-5`` and ``TC-ArgusAgent-PRECISION-001-28``: staging a corpus is an
operator act behind the R2 escalation, never something a selection run performs. A candidate that
is not already on this machine cannot be measured by this module, and that is a REFUSAL rather
than a gap — see :class:`CandidateUnreachable`.

**A MEASUREMENT OVER AN EMPTY OR DECOY TREE REPORTS 0 AND LOOKS IDENTICAL TO A REAL 0.** Three
decoy checkouts exist beside the real ones carrying the SAME ``origin`` URL and the WRONG bytes
(``Minions - Copy``, ``XAgents-WebApp - Temp (Bulild & run Working)``, ``AgentMarkovich-old``).
Matching the remote is not matching the tree. A checkout is resolved by ``cat-file -t <pin>``
returning ``commit`` — never by name, and never by remote. Relatedly, ``DF-13-3-A``'s premise was
withdrawn: that pin was never unreachable, the scan that filed the entry stopped one directory
level short. **A path scanned at the wrong depth is indistinguishable from an unreachable pin**,
and it cost this project a ledger entry and seven findings' worth of doubt.

Purity (AR8): every ``*_PATTERN`` fold and every predicate below is pure — no I/O, no clock, no
network. The impure shell is the git subprocess edge in :func:`measure_candidate`, at the bottom.
Rates are exact :class:`~fractions.Fraction` (AR4) — never ``float``. Sets render ``sorted()``.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pinned_corpus_snapshot import (  # noqa: E402  (path shim above must run first)
    PinUnreachable,
    PinnedTree,
    _git,
    _read_blobs,
    pin_is_reachable,
    pinned_tree,
)

__all__ = [
    "COOCCURRENCE_FILE_FLOOR",
    "CRITERIA",
    "HISTORY_SPAN_DAYS_FLOOR",
    "IN_SCOPE_LANGUAGES",
    "MOCK_ASSERTION_PATTERN",
    "MOCK_ASSERTION_PATTERN_LOOSE",
    "MOCK_BINDING_PATTERN",
    "TEST_FILE_FLOOR",
    "TYPESCRIPT_SCORABLE_FLOOR",
    "CandidateMeasurement",
    "CandidateUnreachable",
    "CriterionOutcome",
    "binds_mock",
    "candidate_row_defects",
    "asserts_on_mock",
    "cooccurs",
    "is_scorable_test_definition",
    "is_test_path",
    "measure_candidate",
    "test_file_paths",
]


# ─────────────────────────────────────────────────────────────────────────────────────────────
# DN-15-1-1 — CRITERION 3 IS MOCK-ASSERTION CO-OCCURRENCE, NOT "USES MOCKING".
#
# The predicates live HERE, as named code constants, and are never retyped into prose (AI-E9-7).
# The sensitivity below is exactly why: the same corpus reads 1 or 6 depending on which
# assertion pattern you pick, and an unnamed predicate is how a figure becomes folklore.
#
# WHY NOT "uses mocking". That is the REFUTED definition. Over the ratified corpus it measured
# **0 true positives / 26 false positives**, and `ast_corroborated` was equivalent to
# `mock_sites >= 1` in 1,835 of 1,836 flagged tests. Since Epic 14 the architecture's
# vacuity-corroboration rule states it directly: *"a vacuous_test_ast finding is verdict-eligible
# ONLY on evidence that the asserted values do not derive from the SUT — NEVER on the mere
# presence of a mock."* A criterion built on "uses mocking" is a criterion built on the refuted
# definition, so it would select the population that already measured 0 TP.
#
# WHAT CO-OCCURRENCE IS, STATED AS THE LIMITATION IT IS. It is a TEXT PROXY for the detector's
# facts (a)+(b). It cannot see whether the SUT result is DISCARDED versus CONSUMED, which is what
# actually decides eligibility. It is deliberately BROADER than the detector: a bench must be
# able to contain true negatives, or precision is unmeasurable. It is a proxy for the
# DEFINITION, never for the VERDICT.
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: A mock PRIMITIVE being bound — the first half of the co-occurrence.
MOCK_BINDING_PATTERN = re.compile(
    r"\b(?:MagicMock|AsyncMock|Mock|patch|mocker\.patch|create_autospec|NonCallableMock)\s*\("
)

#: An assertion made ON a mock-derived value — the second half, and the half that carries the
#: defect class. STRICT: anchored on the attribute dot, so `assert_called` as a bare word in a
#: comment or a docstring does not count.
MOCK_ASSERTION_PATTERN = re.compile(
    r"\.(?:assert_called(?:_once|_with|_once_with)?|assert_any_call|assert_has_calls"
    r"|assert_not_called|assert_awaited\w*)\s*\(|\.call_count\b|\.called\b"
)

#: The LOOSE variant, reported beside the strict one rather than instead of it. Measured
#: 2026-08-19 over `minions` @ ec63b729: strict yields 1 co-occurrence file of 286, loose yields
#: 6 (2.1%). BOTH figures are reported and the conclusion is invariant to the choice — which is
#: the only reason a proxy this coarse is admissible at all.
MOCK_ASSERTION_PATTERN_LOOSE = re.compile(
    r"assert_called|assert_any_call|assert_has_calls|assert_not_called|assert_awaited"
    r"|call_count|\.called\b|\.call_args"
)

#: DN-15-1-2, first number: a suite-size floor by the language's own naming convention.
TEST_FILE_FLOOR = 50

#: DN-15-1-2, second number — and THIS is the real floor. Rationale, stated as an
#: order-of-magnitude argument and explicitly NOT as a prediction of yield: the current
#: five-member corpus carries ONE co-occurrence file across 315 Python test files and returned
#: ZERO blocking findings. Twelve to twenty candidates at >=10 each puts the bench between 120
#: and 200 such files against today's 1. It CANNOT be a prediction that the detector will flag
#: any of them — predicting the yield would be looking.
#:
#: REJECTED — a raw test-count floor ("a large suite"): measured uninformative. `minions` has 286
#: Python test files, the largest in the corpus, and contributes ONE co-occurrence file. Suite
#: size does not carry the defect class.
#: REJECTED — deriving the floor from the >=80% gate arithmetic: that reasons backwards from the
#: number the round is supposed to measure, which is corpus-shopping in a spreadsheet.
COOCCURRENCE_FILE_FLOOR = 10

#: Criterion 4: >= 2 years of commit history. Tests need time to rot; a new repository's tests
#: have not had it.
#:
#: MEASURED AS FIRST-COMMIT-TO-LAST-COMMIT, NOT FIRST-COMMIT-TO-NOW, and the difference is not
#: pedantry: NFR-P1/D1 forbid a wall-clock read, and a criterion whose value changes every day it
#: is re-run is not a frozen criterion. The span is a property of the repository at its pin.
HISTORY_SPAN_DAYS_FLOOR = 730

#: AC3.2 — the TypeScript EXTRACTOR-VISIBILITY floor, in scorable test functions at the pin.
#:
#: Why TypeScript needs a floor that Python does not. Measured 2026-08-19 through the real index
#: at the pins: **367 TypeScript test files across both ratified TypeScript members yield ONE
#: scorable test function** (xagents-webapp 279 files -> 1, agent-smith 88 -> 0). Every idiomatic
#: Jest / Vitest / Mocha suite yields zero, because a test declared as a callback passed to a
#: call extracts no definitions at all (`DF-14-3-C`, open, and its own entry states that it
#: bounds Epic 15).
#:
#: So TypeScript is in the same position as Go and Java, not a different one — which is the
#: premise this story re-measured and found FALSE as originally written. This floor is the
#: answer, and it deliberately neither widens nor narrows the scope: collapsing the bench to
#: Python-only is the operator's call at R2, where the protocol already puts it, and a candidate
#: TypeScript repository that clears this floor genuinely does contribute to the N that gates.
TYPESCRIPT_SCORABLE_FLOOR = 25

#: Criterion 1's scope. Go, Java, PHP and the four AST_INELIGIBLE_LANGUAGES (c, cpp, ruby, rust)
#: are OUT: `DF-14-3-A`/`-B` leave Go and Java unscored and are ⛔ COUPLED — fixing `-A` alone
#: would convert Go's silence into a language-wide false accusation. Admitting an unscorable
#: language would inflate the N that satisfies the floor while contributing nothing to the N that
#: gates. Neither entry is reopened here.
IN_SCOPE_LANGUAGES = frozenset({"python", "typescript"})

#: The seven criteria, in the order they are reported to the operator at R2. Each row is
#: (id, statement, what decides it). Every one is decidable from the repository ALONE, before
#: Argus's detector is run over it — that ordering is the whole point of this story.
CRITERIA: tuple[tuple[int, str, str], ...] = (
    (1, "primary language python, or typescript clearing the AC3.2 visibility floor",
     "file-suffix fold through argus.shared.source_languages.LANGUAGE_BY_SUFFIX"),
    (2, f">= {TEST_FILE_FLOOR} test files by naming convention, AND "
        f">= {COOCCURRENCE_FILE_FLOOR} co-occurrence files",
     "text patterns over the pinned tree"),
    (3, "mock-assertion CO-OCCURRENCE (DN-15-1-1), never 'uses mocking'",
     "MOCK_BINDING_PATTERN and MOCK_ASSERTION_PATTERN over the pinned tree"),
    (4, f">= {HISTORY_SPAN_DAYS_FLOOR} days of commit history",
     "git log --reverse --format=%cI, first entry to last"),
    (5, "permissive licence, recorded VERBATIM from the tracked licence file",
     "tracked LICENSE/COPYING blob at the pin"),
    (6, "independent provenance — nothing Argus was developed against, AND third-party",
     "operator-verifiable metadata"),
    (7, "resolvable pin — 40-char lowercase hex, reachable at an INDIVIDUALLY resolved path",
     "git -C <windows-path> cat-file -t <sha> returns 'commit'"),
)

_SHA_LENGTH = 40
_SHA_ALPHABET = frozenset("0123456789abcdef")

_PYTHON_TEST_SUFFIXES = (".py",)
_TYPESCRIPT_TEST_SUFFIXES = (".ts", ".tsx")

#: Tracked licence filenames, checked at the pin. `.md`/`.txt` variants included because a
#: licence recorded from an untracked file is a licence nobody can verify at the pin.
_LICENCE_NAMES = frozenset(
    {"license", "license.md", "license.txt", "licence", "licence.md", "licence.txt",
     "copying", "copying.md", "copying.txt", "license-mit", "license-apache"}
)


class CandidateUnreachable(RuntimeError):
    """A named ``Unevaluable`` outcome for a candidate — never a silent zero.

    Raised when the candidate's pin does not resolve at the given path. Deliberately NOT a
    fallback to the working tree and deliberately NOT a zero measurement: a measurement over an
    unreachable or decoy tree reports 0 and is indistinguishable from a real 0, which is the
    single most likely way this story's numbers could be false.

    It is also NOT an invitation to fetch. ``DN-5``: nothing here fetches, and protocol section 6
    R2 makes fetching third-party source an operator act.
    """


# ─────────────────────────────────────────────────────────────────────────────────────────────
# PURE ANALYZERS (AR8). No I/O, no clock, no network, no subprocess below this line.
# ─────────────────────────────────────────────────────────────────────────────────────────────


def is_test_path(path: str, language: str) -> bool:
    """Whether *path* is a test file by *language*'s own naming convention (criterion 2).

    Python is ``test_*.py`` / ``*_test.py``. TypeScript is ``*.test.ts(x)`` / ``*.spec.ts(x)``
    or anything under a ``__tests__/`` directory — the three conventions Jest, Vitest and Mocha
    projects actually use.

    Deliberately a NAMING rule rather than a content rule: criterion 2 must be decidable from the
    tree listing alone, and a content rule would start to shade into reading the tests.
    """
    posix = path.replace("\\", "/").lower()
    name = posix.rsplit("/", 1)[-1]
    if language == "python":
        if not name.endswith(_PYTHON_TEST_SUFFIXES):
            return False
        return name.startswith("test_") or name.endswith("_test.py")
    if language == "typescript":
        if not name.endswith(_TYPESCRIPT_TEST_SUFFIXES):
            return False
        if "/__tests__/" in posix or posix.startswith("__tests__/"):
            return True
        stem = name.rsplit(".", 1)[0]
        return stem.endswith(".test") or stem.endswith(".spec")
    return False


def test_file_paths(paths: Iterable[str], language: str) -> tuple[str, ...]:
    """The test files among *paths*, ``sorted()`` for determinism (NFR-D1)."""
    return tuple(sorted(p for p in paths if is_test_path(p, language)))


def binds_mock(text: str) -> bool:
    """Whether *text* binds a mock primitive — the FIRST half of the co-occurrence."""
    return MOCK_BINDING_PATTERN.search(text) is not None


def asserts_on_mock(text: str, *, loose: bool = False) -> bool:
    """Whether *text* asserts on a mock-derived value — the SECOND half, and the load-bearing one.

    *loose* selects :data:`MOCK_ASSERTION_PATTERN_LOOSE`. Both are reported rather than one being
    chosen silently, because the strict/loose choice moves the headline count by 6x on the one
    member where it is non-zero.
    """
    pattern = MOCK_ASSERTION_PATTERN_LOOSE if loose else MOCK_ASSERTION_PATTERN
    return pattern.search(text) is not None


def cooccurs(text: str, *, loose: bool = False) -> bool:
    """DN-15-1-1: *text* binds a mock **AND** asserts on one. Criterion 3, exactly.

    The conjunction is the whole decision. Either half alone is the refuted "uses mocking"
    definition: 21 of `minions`' 286 test files bind a mock, and **1** carries both.
    """
    return binds_mock(text) and asserts_on_mock(text, loose=loose)


def is_scorable_test_definition(name: str, kind: str) -> bool:
    """AC3.2's predicate: would the detector be able to SCORE this definition as a test?

    RESTATED, NOT IMPORTED. ``argus/detectors/vacuous_test.py::_is_test_function`` is the
    original; importing it would breach the AC2.2 ban that is the strongest guard in this story,
    so the rule is quoted here instead: a ``function`` definition whose name starts with a
    lowercase ``test``. The lowercase requirement is the detector's own and is deliberately
    mirrored including its sharp edge — Go's ``func TestX`` fails it, which is one of the two
    independent causes behind the measured TypeScript floor.

    Class methods of that shape are extracted by the index as ``function`` definitions in their
    own right, so they are covered by the same predicate rather than by a second branch.
    """
    return kind == "function" and name.startswith("test")


def candidate_row_defects(
    *,
    member_id: str,
    commit_sha: str,
    primary_language: str,
    licence: str,
    ast_ineligible_languages: frozenset[str],
) -> tuple[str, ...]:
    """AC4.3 — the three checks ``CorpusMemberSpec.__post_init__`` does NOT perform on a candidate.

    ⛔ THE MEASURED REASON THIS FUNCTION EXISTS. ``__post_init__`` **returns early** immediately
    after the ineligible-reason check, so for a row with ``eligible_for_n=False`` the sha,
    provenance and AST-eligibility validations **never run**. Measured by construction
    2026-08-19: on a candidate row, ``commit_sha='deadbeef'`` (8 chars) CONSTRUCTS, a non-hex
    ``commit_sha='zzzz'`` CONSTRUCTS, and ``primary_language='go'`` or ``'ruby'`` CONSTRUCTS —
    all three silently. *"The guard is structural"* is TRUE of the promotion path and FALSE of
    these three, and a reader will assume otherwise.

    It is a **pure fold returning defects**, not a raising validator, and not a new
    ``__post_init__`` branch — a new branch would change behaviour for the five RATIFIED rows,
    which is outside this story's scope and would move ``N``.

    Returns a ``sorted()`` tuple of defect strings; empty means the row is well-formed.
    """
    defects: list[str] = []
    if len(commit_sha) != _SHA_LENGTH or not set(commit_sha) <= _SHA_ALPHABET:
        defects.append(
            f"{member_id!r}: commit_sha {commit_sha!r} is not a full {_SHA_LENGTH}-character "
            "lowercase hex sha. A candidate with an unpinned or malformed sha is not "
            "byte-reproducible, and protocol section 4 makes reproducibility the precondition "
            "for any adjudication being valid — so it could never be ratified at R2 anyway."
        )
    if primary_language in ast_ineligible_languages:
        defects.append(
            f"{member_id!r}: primary_language {primary_language!r} is AST-INELIGIBLE, so it "
            "cannot support an audited_deep claim and cannot contribute to the N that gates "
            "(DN-6). Admitting it would inflate the N that satisfies the floor while "
            "contributing nothing."
        )
    elif primary_language not in IN_SCOPE_LANGUAGES:
        defects.append(
            f"{member_id!r}: primary_language {primary_language!r} is outside this round's "
            f"scope {sorted(IN_SCOPE_LANGUAGES)} (AC3.1). Go and Java are excluded because "
            "DF-14-3-A/-B leave them unscored and are COUPLED; neither is reopened here."
        )
    if not licence.strip():
        defects.append(
            f"{member_id!r}: no licence recorded. The schema requires it and R2 ratification "
            "must be an INFORMED act — an operator cannot ratify a repository whose terms "
            "nobody wrote down."
        )
    return tuple(sorted(defects))


@dataclass(frozen=True)
class CriterionOutcome:
    """One criterion's verdict for one candidate — the measured value, never an impression."""

    criterion: int
    passed: bool
    measured: str

    def render(self) -> str:
        return f"  criterion {self.criterion}: {'PASS' if self.passed else 'FAIL'} — {self.measured}"


@dataclass(frozen=True)
class CandidateMeasurement:
    """Everything the operator needs for the R2 act, per candidate (AC7.5).

    Rates are exact :class:`~fractions.Fraction` (AR4). ``scorable_test_functions`` is ``None``
    for a Python candidate — the AC3.2 floor is a TypeScript-only gate, and ``0`` would read as
    a measured zero rather than as "not applicable".
    """

    member_id: str
    checkout: str
    commit_sha: str
    repository_url: str
    primary_language: str
    source_files: int
    test_files: int
    mock_binding_files: int
    mock_assertion_files: int
    cooccurrence_files: int
    cooccurrence_files_loose: int
    history_span_days: int
    licence_path: str | None
    licence_first_line: str
    scorable_test_functions: int | None = None

    @property
    def cooccurrence_rate(self) -> Fraction:
        """Co-occurrence files over test files — EXACT, never a float (AR4)."""
        if self.test_files == 0:
            return Fraction(0, 1)
        return Fraction(self.cooccurrence_files, self.test_files)

    def outcomes(self) -> tuple[CriterionOutcome, ...]:
        """Every criterion's verdict, in :data:`CRITERIA` order. Pure."""
        language_ok = self.primary_language in IN_SCOPE_LANGUAGES
        if language_ok and self.primary_language == "typescript":
            language_ok = (self.scorable_test_functions or 0) >= TYPESCRIPT_SCORABLE_FLOOR
        return (
            CriterionOutcome(
                1, language_ok,
                f"primary_language={self.primary_language!r}"
                + (
                    f", scorable test functions={self.scorable_test_functions} "
                    f"(AC3.2 floor {TYPESCRIPT_SCORABLE_FLOOR})"
                    if self.primary_language == "typescript" else ""
                ),
            ),
            CriterionOutcome(
                2,
                self.test_files >= TEST_FILE_FLOOR
                and self.cooccurrence_files >= COOCCURRENCE_FILE_FLOOR,
                f"{self.test_files} test files (floor {TEST_FILE_FLOOR}), "
                f"{self.cooccurrence_files} co-occurrence files "
                f"(floor {COOCCURRENCE_FILE_FLOOR})",
            ),
            CriterionOutcome(
                3, self.cooccurrence_files > 0,
                f"strict={self.cooccurrence_files}, loose={self.cooccurrence_files_loose}, "
                f"binding-only={self.mock_binding_files}, "
                f"assertion-only={self.mock_assertion_files}",
            ),
            CriterionOutcome(
                4, self.history_span_days >= HISTORY_SPAN_DAYS_FLOOR,
                f"{self.history_span_days} days of history "
                f"(floor {HISTORY_SPAN_DAYS_FLOOR})",
            ),
            CriterionOutcome(
                5, bool(self.licence_path),
                f"licence file {self.licence_path!r}: {self.licence_first_line!r}"
                if self.licence_path else "NO tracked licence file at the pin",
            ),
            CriterionOutcome(
                6, False,
                "third-party status is NOT machine-decidable — operator-verifiable metadata, "
                "and stricter than the closed `provenance` vocabulary can express (AC2.3)",
            ),
            CriterionOutcome(
                7, True,
                f"pin {self.commit_sha} resolved to a commit at {self.checkout}",
            ),
        )


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE IMPURE EDGE (AR8). git subprocess reads only — ls-tree, cat-file, log. No checkout, no
# stash, no clean, no reset, no commit, no worktree. Both corpus checkouts and every candidate
# tree belong to other projects and are treated as STRICTLY READ-ONLY.
# ─────────────────────────────────────────────────────────────────────────────────────────────


def _history_span_days(checkout: Path, commit_sha: str) -> int:
    """Days from the FIRST commit reachable from *commit_sha* to the pin itself.

    Not first-commit-to-now: NFR-P1/D1 forbid a wall-clock read, and a criterion whose value
    drifts every day it is re-run is not a frozen criterion.
    """
    from datetime import datetime

    done = _git(checkout, "log", "--reverse", "--format=%cI", commit_sha)
    if done.returncode != 0:
        raise CandidateUnreachable(f"{checkout}: `git log {commit_sha}` failed")
    stamps = [line for line in done.stdout.decode("utf-8", "replace").splitlines() if line.strip()]
    if not stamps:
        raise CandidateUnreachable(f"{checkout}: no commits reachable from {commit_sha}")
    first = datetime.fromisoformat(stamps[0])
    last = datetime.fromisoformat(stamps[-1])
    return (last - first).days


def measure_candidate(
    checkout: Path,
    commit_sha: str,
    *,
    member_id: str,
    repository_url: str,
    primary_language: str,
) -> CandidateMeasurement:
    """Measure one candidate against every criterion, reading ONLY from the pinned object database.

    RAISES :class:`CandidateUnreachable` when the pin does not resolve at *checkout* — never a
    zero, never a working-tree fallback, and never a fetch.
    """
    checkout = Path(checkout)
    if not pin_is_reachable(checkout, commit_sha):
        raise CandidateUnreachable(
            f"{checkout}: pin {commit_sha} is NOT in this checkout's object database "
            f"(`git cat-file -t` did not report 'commit'). This candidate is UNEVALUABLE and is "
            f"recorded as such by name. It is NOT measured from the working tree: three decoy "
            f"trees on this machine carry the right origin URL and the wrong bytes, so matching "
            f"the remote is not matching the tree."
        )

    tree: PinnedTree = pinned_tree(checkout, commit_sha, keep=lambda _p: True)
    all_paths = tuple(entry.path for entry in tree.files)
    tests = test_file_paths(all_paths, primary_language)

    by_path = {entry.path: entry.blob_sha for entry in tree.files}
    blobs = _read_blobs(checkout, [by_path[p] for p in tests]) if tests else {}

    binding = assertion = both = both_loose = 0
    for path in tests:
        text = blobs.get(by_path[path], b"").decode("utf-8", "replace")
        has_bind = binds_mock(text)
        has_assert = asserts_on_mock(text)
        binding += int(has_bind)
        assertion += int(has_assert)
        both += int(has_bind and has_assert)
        both_loose += int(has_bind and asserts_on_mock(text, loose=True))

    licence_path = next(
        (p for p in sorted(all_paths) if p.replace("\\", "/").lower() in _LICENCE_NAMES), None
    )
    licence_first_line = ""
    if licence_path is not None:
        licence_blob = _read_blobs(checkout, [by_path[licence_path]])
        raw = licence_blob.get(by_path[licence_path], b"").decode("utf-8", "replace")
        licence_first_line = next(
            (line.strip() for line in raw.splitlines() if line.strip()), ""
        )

    return CandidateMeasurement(
        member_id=member_id,
        checkout=str(checkout),
        commit_sha=commit_sha,
        repository_url=repository_url,
        primary_language=primary_language,
        source_files=len(all_paths),
        test_files=len(tests),
        mock_binding_files=binding,
        mock_assertion_files=assertion,
        cooccurrence_files=both,
        cooccurrence_files_loose=both_loose,
        history_span_days=_history_span_days(checkout, commit_sha),
        licence_path=licence_path,
        licence_first_line=licence_first_line,
    )


def scorable_test_function_count(checkout: Path, commit_sha: str, test_paths: tuple[str, ...]) -> int:
    """AC3.2 — scorable test functions at the pin, measured THROUGH THE INDEX ONLY.

    ``argus.index`` is the permitted import (reach); ``argus.detectors`` is banned (output).
    Sizing a candidate's scorable population is measuring the instrument's REACH, not reading
    its VERDICT — which is the line AC2.2 draws and enforces mechanically.
    """
    from argus.index.ast_index import build_ast_index

    tree = pinned_tree(checkout, commit_sha, keep=lambda p: p in set(test_paths))
    blobs = _read_blobs(checkout, [entry.blob_sha for entry in tree.files])

    import tempfile

    scorable = 0
    with tempfile.TemporaryDirectory(prefix="cand", dir="D:/t" if Path("D:/t").exists() else None) as tmp:
        root = Path(tmp)
        written: list[str] = []
        for entry in tree.files:
            target = root / entry.path
            if len(str(target)) > 250:  # Windows MAX_PATH: refuse rather than truncate silently
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(blobs.get(entry.blob_sha, b""))
            written.append(entry.path)
        index = build_ast_index(root, tuple(sorted(written)))
        for entry in index.entries:
            for definition in entry.definitions:
                if is_scorable_test_definition(definition.name, definition.kind):
                    scorable += 1
    return scorable


def _render(measurement: CandidateMeasurement) -> str:
    lines = [
        f"{measurement.member_id} @ {measurement.commit_sha}",
        f"  path: {measurement.checkout}",
        f"  url:  {measurement.repository_url}",
        f"  source files at pin: {measurement.source_files}",
        f"  co-occurrence rate: {measurement.cooccurrence_rate} (exact Fraction, AR4)",
    ]
    lines.extend(outcome.render() for outcome in measurement.outcomes())
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover - operator entry point
    if len(sys.argv) < 5:
        print(
            "usage: candidate_selection.py <checkout> <sha> <member_id> <language> [url]",
            file=sys.stderr,
        )
        raise SystemExit(2)
    print(
        _render(
            measure_candidate(
                Path(sys.argv[1]),
                sys.argv[2],
                member_id=sys.argv[3],
                primary_language=sys.argv[4],
                repository_url=sys.argv[5] if len(sys.argv) > 5 else "",
            )
        )
    )
