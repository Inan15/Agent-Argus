"""A name-based test convention matches a WORD, never a letter sequence (Story 11.2).

Verification areas ArgusAgent-DETECT (``TC-ArgusAgent-DETECT-001-96``..``-99``),
ArgusAgent-PIPELINE (``TC-ArgusAgent-PIPELINE-002-10``..``-13``) and ArgusAgent-DOCS
(``TC-ArgusAgent-DOCS-001-53``). Closes ``DF-8-2-B``.

What was actually wrong, and why it was release-blocking
--------------------------------------------------------
Three entries in the two classification tables of ``argus/detectors/vacuous_test.py``
were written without a word separator — ``"test.java"``, ``"spec.rb"`` and a bare
``"test.py"`` — so tier 2 / tier 3 claimed any basename whose letters merely *ended*
that way. Measured on a polyglot fixture at ``93adc94`` with the defect live::

    svc/latest.java   is_test=True  depth=audited_shallow  crit=CRITICAL  inelig=test_file
    critical set: ()

``svc/latest.java`` is ordinary production Java carrying a credential-shaped token.
Argus assessed it CRITICAL, then removed it from the FR4 critical set under the reason
``test_file`` — a statement that is simply false — leaving the set EMPTY, so FR16's
*"all critical subsystems deep"* clause was satisfied **vacuously** and
``RELEASE_READY`` was reachable on a repository whose one critical production file was
never deep-graded. That is a false green in the PRD-fatal direction (inversion F1).

Why this file is a CLOSURE and not a list of three fixes
--------------------------------------------------------
Six hand-counted enumerations in this project have been re-measured and all six were
wrong — this defect itself was documented as "two entries" by four planning documents
and is three. A list closes today's instances; a closure closes the class. So:

* ``-97`` reads the tables **out of the module** (never transcribes them, AI-E9-7) and
  requires every entry to carry a REGISTERED boundary — a leading ``_``/``.``, an
  uppercase-initial case-sensitive convention, or a whole basename. A separator-less
  entry added tomorrow fails here, naming itself.
* ``-98`` **synthesizes** the adversarial near-misses from those same tables rather
  than hand-listing them, and asserts both directions (the boundary-less form is NOT a
  test AND the boundary-carrying form IS) — a fix that simply made everything ``False``
  would pass a one-directional check.
* ``-99`` closes over the GROUNDED LANGUAGE SET: every language in
  ``argus/shared/source_languages.py::LANGUAGE_BY_SUFFIX`` either has a registered
  convention or is a registered exemption carrying its reason. It **forces a decision**
  and deliberately does not authorise adding a convention — the missing conventions are
  false NEGATIVES, a different defect class, filed by Story 11.2 AC6.2 and not fixed
  here, because adding one moves classification on real repositories.

Because all three closures go green by finding nothing, non-vacuity is mandatory
(E.3): every table must resolve, entries read per table, near-miss pairs generated and
languages enumerated all carry ``> 0`` floors, so a rename or a move of the constants —
or an ``ast.parse`` failure in ``-11`` — turns this **RED** rather than silently green.

Scope fence recorded rather than assumed
-----------------------------------------
This story only REMOVES false positives. Java's ``Test*.java`` prefix form, Ruby's
minitest ``_test.rb``, Surefire's ``*Tests.java`` / ``*TestCase.java``, PHPUnit's
``*Test.php`` and C's ``_test.c`` are all unrecognised, are all false NEGATIVES, and
are all FILED (``deferred-work.md``, Story 11.2 AC6.2) rather than fixed.
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path
from typing import NamedTuple

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.detectors import vacuous_test  # noqa: E402
from argus.detectors.vacuous_test import (  # noqa: E402
    is_test_classification_content_dependent,
    is_test_file,
)
from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger  # noqa: E402
from argus.ledger.critical_subsystems import (  # noqa: E402
    CriticalIneligibility,
    identify_critical_subsystems,
)
from argus.ledger.depth_semantics import Criticality  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import _detect_per_file  # noqa: E402
from argus.shared.source_languages import LANGUAGE_BY_SUFFIX, language_for_suffix  # noqa: E402
from argus.verdict.verdict_gate import (  # noqa: E402
    DecisionRow,
    Verdict,
    exit_code_for_verdict,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_ARCHITECTURE = _ARTIFACT_DIR / "architecture.md"
_PIPELINE_SOURCE = _REPO_ROOT / "argus" / "pipeline.py"


def _pipeline_family_sources() -> tuple[Path, ...]:
    """Every ``argus/pipeline*.py`` module, globbed from the FILESYSTEM — never a hand list.

    Story 12.1 moved ``_detect_per_file`` and ``_critical_candidate`` out of
    ``argus/pipeline.py`` into the sibling ``argus/pipeline_stages.py`` (the NFR-M1
    extraction). ``-11`` went RED, which is the guard working: it reads a file BY NAME and
    the code it reads moved. The fix is to widen the guard's REACH, never to narrow its
    CLAIM — the claim has always been *"in the pipeline, every ``_critical_ineligibility``
    call receives an ``is_test`` value bound from a single ``is_test_file`` evaluation in
    its own function"*, and the pipeline is now more than one file.

    Globbed so a THIRD sibling (12.2's deep-audit wiring is the next candidate) is swept
    the moment it exists. Pinning the names that exist today would re-acquire exactly the
    defect this repository keeps re-finding: a guard that names the files that existed when
    it was written. The FILESYSTEM is the population rather than ``git ls-files`` — the
    index would let an unstaged new sibling escape the walk mid-implementation, which is
    the ``DF-10-4-D`` property, desirable for a currency guard and a hole in a purity one.
    """
    found = tuple(
        sorted(
            path
            for path in (_REPO_ROOT / "argus").glob("pipeline*.py")
            if path.is_file() and "__pycache__" not in path.parts
        )
    )
    assert found, (
        "no `argus/pipeline*.py` module was enumerated — the walk below would be vacuous. "
        f"{_WORKING}"
    )
    assert _PIPELINE_SOURCE in found, (
        f"argus/pipeline.py is not in the enumerated pipeline family {found} — the pathspec "
        f"is broken. {_WORKING}"
    )
    return found

_GUARD = "tests/test_classification_word_boundary.py"
_OWNING_MODULE = "argus/detectors/vacuous_test.py"

#: The house line every failure message here ends with. A red in this file is almost
#: always the guard doing its job on a deliberate change, not a mystery.
_WORKING = (
    f"A red here is the guard working: register the change in {_OWNING_MODULE} and in "
    f"{_GUARD}, or revert it."
)


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — the near-miss corpus, declared ONCE and imported by every consumer (E.6)
# ─────────────────────────────────────────────────────────────────────────────


class Case(NamedTuple):
    """One pinned classification answer, in BOTH of its dimensions.

    ``content_dependent`` is pinned beside ``is_test`` because WHICH TIER answered is a
    separate contract with a second consumer: grading wants "assume test when
    unreadable", while the FR4/DR-5 eligibility filter wants the opposite, so a path
    that moves between tier 2 and tier 3 changes both consumers even when ``is_test``
    is unmoved.
    """

    path: str
    is_test: bool
    content_dependent: bool
    why: str


#: Declared ONCE (AC2.4) and imported by ``tests/test_vacuous_detector.py`` beside
#: ``TC-ArgusAgent-DETECT-001-85``/``-95`` — never restated (AI-E9-7).
#:
#: The corpus is the UNION of the two source documents' lists, recorded as such because
#: neither is the contract (``-97``/``-98`` are): ``DF-8-2-B`` named ``attest.py`` and
#: ``greatest.py``; ``epics.md`` named ``contest.py`` and ``respec.rb``. Covering both
#: means neither reviewer finds a gap, and the closures above cover the ones nobody
#: thought to name.
NEAR_MISS_CORPUS: tuple[Case, ...] = (
    # ── false positives the defect produced: production files claimed as tests ──
    Case("svc/latest.java", False, False, "DF-8-2-B headline; CamelCase boundary absent"),
    Case("svc/myspec.rb", False, False, "DF-8-2-B headline; RSpec's boundary is `_`"),
    Case("svc/respec.rb", False, False, "named by epics.md"),
    Case("svc/spec.rb", False, False, "the bare literal itself, outside a spec/ dir"),
    Case("svc/contest.py", False, False, "named by epics.md; tier-3 bare `test.py`"),
    Case("svc/attest.py", False, False, "named by DF-8-2-B"),
    Case("svc/greatest.py", False, False, "named by DF-8-2-B"),
    Case("svc/latest.py", False, False, "the Python twin of the headline Java case"),
    Case("svc/mytest.py", False, False, "pytest's python_files does NOT match this"),
    # ── the true positives that MUST survive: the conventions really in use ──
    Case("svc/UserServiceTest.java", True, False, "Surefire `**/*Test.java` (tier 2)"),
    Case("svc/Test.java", True, False, "the bare case-sensitive convention (tier 2)"),
    Case("svc/test.java", True, False, "kept by the unchanged `test.` prefix rule"),
    Case("svc/user_spec.rb", True, False, "RSpec `*_spec.rb` (tier 2)"),
    Case("pkg/conftest.py", True, True, "DN-2 — whole-basename rule, still TIER 3"),
    Case("app/auth_test.py", True, True, "pytest `*_test.py` (tier 3, by content)"),
    Case("svc/x_test.go", True, False, "Go `*_test.go` (tier 2)"),
    Case("web/button.test.tsx", True, False, "Jest `*.test.tsx` (tier 2)"),
    Case("crate/parser_test.rs", True, False, "Rust `*_test.rs` (tier 2)"),
    Case("tests/test_x.py", True, False, "tier 1 — location, not name"),
)


def assert_corpus_holds() -> None:
    """Assert every corpus row in BOTH directions (E.4), or raise ``AssertionError``.

    Factored out of the test so ``tests/test_vacuous_detector.py`` reuses the ONE
    declaration and the ONE assertion rather than restating either.
    """
    assert NEAR_MISS_CORPUS, "the near-miss corpus is empty; every assertion over it is vacuous"
    for case in NEAR_MISS_CORPUS:
        assert is_test_file(case.path) is case.is_test, (
            f"is_test_file({case.path!r}) should be {case.is_test} — {case.why}. A name-based "
            f"convention must match a WORD, never a letter sequence. {_WORKING}"
        )
        assert is_test_classification_content_dependent(case.path) is case.content_dependent, (
            f"is_test_classification_content_dependent({case.path!r}) should be "
            f"{case.content_dependent} — {case.why}. WHICH TIER answered is its own contract: "
            f"the FR4/DR-5 eligibility consumer reads it in the opposite direction from the "
            f"grading consumer. {_WORKING}"
        )


def test_TC_ArgusAgent_DETECT_001_96_the_near_miss_corpus_holds_in_both_directions() -> None:
    """TC-ArgusAgent-DETECT-001-96 — Story 11.2 / AC2: false positives gone, true positives kept.

    Both directions, because a "fix" that classified nothing as a test would satisfy a
    one-directional check while deleting every real convention (E.4). The union of both
    source documents' near-miss lists is covered, and ``content_dependent`` is asserted
    beside ``is_test`` for every row (AC2.3).
    """
    assert_corpus_holds()

    # Non-vacuity: the corpus must exercise BOTH answers, or "both directions" is a claim
    # about an empty set.
    assert sum(1 for c in NEAR_MISS_CORPUS if not c.is_test) >= 9
    assert sum(1 for c in NEAR_MISS_CORPUS if c.is_test) >= 10
    assert any(c.content_dependent for c in NEAR_MISS_CORPUS), (
        "no corpus row reaches tier 3, so the tier-3 half of the contract is untested"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — THE CLOSURE: a separator-less entry fails CI
# ─────────────────────────────────────────────────────────────────────────────

#: The registered word separators for a SUFFIX convention. A suffix entry must begin
#: with one of these, because that character is the whole reason the match is a word
#: boundary rather than an accident of spelling.
_WORD_SEPARATORS = ("_", ".")

#: The registration kinds, by the module attribute that holds each. Read by name so a
#: RENAME or a MOVE of a constant turns ``-99`` red (E.3) instead of silently reducing
#: the closure to whatever still resolves.
_SUFFIX_TABLES = ("_UNAMBIGUOUS_TEST_SUFFIXES", "_AMBIGUOUS_PYTHON_TEST_SUFFIXES")
_CASE_SENSITIVE_TABLE = "_CASE_SENSITIVE_TEST_SUFFIXES"
_BASENAME_TABLE = "_AMBIGUOUS_PYTHON_TEST_BASENAMES"
_REGISTERED_TABLES = (*_SUFFIX_TABLES, _CASE_SENSITIVE_TABLE, _BASENAME_TABLE)

#: Grounded languages with NO recognised test-name convention. Each carries its reason
#: and its filing, so the gap is REGISTERED rather than invisible. ⛔ Removing an entry
#: here by ADDING the convention is out of scope for Story 11.2 (§D) — these are false
#: NEGATIVES, and adding a convention moves classification on real repositories.
_NO_CONVENTION_EXEMPTIONS: dict[str, str] = {
    "c": (
        "C has no convention Argus recognises; the common form is `*_test.c` (Check/Unity). "
        "False negative, FILED by Story 11.2 AC6.2 — owner Delivery Orchestrator, target 12.5."
    ),
    "php": (
        "PHPUnit's convention is `*Test.php`, unrecognised here. False negative, FILED by "
        "Story 11.2 AC6.2 — owner Delivery Orchestrator, target 12.5."
    ),
}


def _table(name: str) -> tuple[str, ...]:
    """Read one registration table out of the module (never transcribe it, AI-E9-7)."""
    entries = getattr(vacuous_test, name, None)
    if entries is None:
        return ()
    assert isinstance(entries, tuple), (
        f"{_OWNING_MODULE}::{name} is no longer a tuple; the closure reads it as data. {_WORKING}"
    )
    return entries


def _all_registrations() -> dict[str, tuple[str, ...]]:
    return {name: _table(name) for name in _REGISTERED_TABLES}


def _boundary_failure(entry: str, table: str) -> str | None:
    """Why *entry* carries no word boundary, or ``None`` when it does (PURE)."""
    if table in _SUFFIX_TABLES:
        if entry.startswith(_WORD_SEPARATORS):
            return None
        return (
            f"{table} entry {entry!r} begins with no registered word separator "
            f"{_WORD_SEPARATORS}, so it matches a LETTER SEQUENCE: every basename merely "
            f"ending in {entry!r} is claimed as a test"
        )
    if table == _CASE_SENSITIVE_TABLE:
        if entry[:1].isupper():
            return None
        return (
            f"{table} entry {entry!r} does not begin with an uppercase letter, so it carries "
            f"no CASE boundary — and this table is matched against the original-case basename "
            f"precisely because the capital IS the separator"
        )
    if entry and "/" not in entry and "\\" not in entry and language_for_suffix(_suffix_of(entry)):
        return None
    return (
        f"{table} entry {entry!r} is not a whole basename with an auditable suffix; this table "
        f"is matched by WHOLE-NAME equality, which is the boundary"
    )


def _suffix_of(entry: str) -> str:
    dot = entry.rfind(".")
    return entry[dot:] if dot != -1 else ""


def test_TC_ArgusAgent_DETECT_001_97_every_registered_convention_carries_a_word_boundary() -> None:
    """TC-ArgusAgent-DETECT-001-97 — Story 11.2 / AC3.1: the load-bearing closure.

    Every entry in every classification table must be one of exactly three registered
    shapes: a suffix beginning with a word separator, a case-sensitive convention whose
    first character is an uppercase letter, or a whole basename. Anything else fails
    **naming itself** — which is what makes this a closure over the class rather than a
    list of the three instances known on 2026-08-11.

    Demonstrated RED against the unfixed tables, where it named exactly three offenders:
    ``test.java``, ``spec.rb`` and ``test.py``.
    """
    registrations = _all_registrations()

    offenders = [
        message
        for table, entries in registrations.items()
        for entry in entries
        if (message := _boundary_failure(entry, table)) is not None
    ]
    assert not offenders, (
        "a name-based test convention must match a WORD, never a letter sequence — "
        + str(len(offenders))
        + " entry/entries do not:\n  - "
        + "\n  - ".join(offenders)
        + f"\nAdd the real separator the convention actually uses (`_`, `.`, a CamelCase "
        f"capital, or the whole basename), or register the entry in the table whose boundary "
        f"rule it satisfies. {_WORKING}"
    )

    # Non-vacuity (E.3): a closure that read nothing would pass by finding nothing.
    assert sum(len(v) for v in registrations.values()) >= 15, (
        f"fewer registrations resolved than {_OWNING_MODULE} carries — the constants moved or "
        f"were renamed and this closure went green by finding nothing. {_WORKING}"
    )


def test_TC_ArgusAgent_DETECT_001_98_synthesized_near_misses_fail_and_their_twins_pass() -> None:
    """TC-ArgusAgent-DETECT-001-98 — Story 11.2 / AC3.2: adversarial cases derived, not listed.

    For every registered convention the guard DERIVES its boundary-less form — strip the
    separator, lowercase the CamelCase capital, or prefix the whole basename — glues an
    alphanumeric character in front, and asserts the result is NOT a test. The
    boundary-CARRYING twin is asserted to still BE one in the same loop, so a change that
    passed by classifying nothing as a test would fail here (E.4).

    This is the half that closes the class: an entry added tomorrow gets its own
    adversarial pair for free, with nobody having to think of it.
    """
    pairs = 0
    for table, entries in _all_registrations().items():
        for entry in entries:
            for prefix in ("a", "9"):
                if table == _CASE_SENSITIVE_TABLE:
                    near_miss = f"svc/{prefix}{entry[:1].lower()}{entry[1:]}"
                    twin = f"svc/{prefix}{entry}"
                elif table == _BASENAME_TABLE:
                    near_miss = f"svc/{prefix}{entry}"
                    twin = f"svc/{entry}"
                else:
                    near_miss = f"svc/{prefix}{entry.lstrip(''.join(_WORD_SEPARATORS))}"
                    twin = f"svc/{prefix}{entry}"
                pairs += 1
                assert not is_test_file(near_miss), (
                    f"{near_miss!r} is production code: it merely ENDS with the letters of the "
                    f"{table} convention {entry!r} and carries none of its boundary. Classifying "
                    f"it as a test removes it from the FR4 critical set under the false reason "
                    f"`test_file`. {_WORKING}"
                )
                assert is_test_file(twin), (
                    f"{twin!r} carries the {table} convention {entry!r} in full and must still be "
                    f"a test — a fix that removed the false positives by deleting the convention "
                    f"would silently stop recognising a whole ecosystem's test suites. {_WORKING}"
                )

    # Non-vacuity (E.3): pairs are SYNTHESIZED, so an empty table would assert nothing.
    assert pairs >= 30, (
        f"only {pairs} adversarial pairs were synthesized; the registration tables in "
        f"{_OWNING_MODULE} moved and this guard went green by generating nothing. {_WORKING}"
    )


def test_TC_ArgusAgent_DETECT_001_99_every_grounded_language_is_decided_not_forgotten() -> None:
    """TC-ArgusAgent-DETECT-001-99 — Story 11.2 / AC3.4-AC3.5: the language closure + non-vacuity.

    ``argus/shared/source_languages.py`` is the single source of truth for what Argus
    grounds (FR7/NFR-P2), deliberately not a hand-typed list — so the set of languages
    that need a test-name convention is DERIVED from it. Every grounded language either
    has at least one registered convention or is a registered exemption carrying its
    reason. Both directions fail: a newly grounded language with no convention, and an
    exemption that has quietly acquired one.

    The tier-2 ``test_``/``test.`` PREFIX rules are deliberately excluded from "has a
    convention" — they are language-agnostic, so counting them would make every language
    covered and the closure vacuous.

    ⛔ A red here forces a DECISION; it does not authorise adding a convention. The
    missing conventions are false NEGATIVES (a different defect class), they move
    classification on real repositories, and Story 11.2 files them rather than fixing
    them.
    """
    registrations = _all_registrations()
    missing_tables = [name for name in _REGISTERED_TABLES if not registrations[name]]
    assert not missing_tables, (
        f"registration table(s) {missing_tables} did not resolve in {_OWNING_MODULE} — renamed, "
        f"moved or emptied. Every closure in this file reads them by name, so this must be RED "
        f"rather than silently green. {_WORKING}"
    )

    covered: dict[str, list[str]] = {}
    for entries in registrations.values():
        for entry in entries:
            language = language_for_suffix(_suffix_of(entry))
            if language is not None:
                covered.setdefault(language, []).append(entry)

    grounded = set(LANGUAGE_BY_SUFFIX.values())
    undecided = sorted(grounded - set(covered) - set(_NO_CONVENTION_EXEMPTIONS))
    assert not undecided, (
        f"grounded language(s) {undecided} have no registered test-name convention and no "
        f"registered exemption. Argus reads their files, so it will classify them — decide "
        f"which: register the convention in {_OWNING_MODULE}, or register the gap here WITH ITS "
        f"REASON and its filing. {_WORKING}"
    )

    stale = sorted(set(_NO_CONVENTION_EXEMPTIONS) & set(covered))
    assert not stale, (
        f"language(s) {stale} are registered as having NO convention but now have one "
        f"({ {k: covered[k] for k in stale} }). Adding a convention is a widening that moves "
        f"classification on real repositories — remove the exemption deliberately, and say so in "
        f"the ledger. {_WORKING}"
    )
    for language, reason in _NO_CONVENTION_EXEMPTIONS.items():
        assert language in grounded, f"exemption {language!r} is not a grounded language any more"
        assert "FILED" in reason and len(reason) > 40, (
            f"the {language!r} exemption carries no filing; an exemption without a reason and an "
            f"owner is just a silence with a name. {_WORKING}"
        )

    # Non-vacuity (E.3) — floors on both derived populations.
    assert len(grounded) >= 10, f"only {len(grounded)} languages enumerated; LANGUAGE_BY_SUFFIX moved"
    assert len(covered) >= 8, f"only {len(covered)} languages carry a convention; the tables moved"


# ─────────────────────────────────────────────────────────────────────────────
# AC4/AC5 — the two-stage invariant RE-PROVEN over both constants, end to end
# ─────────────────────────────────────────────────────────────────────────────

#: Ordinary production Java: a credential-shaped token (heuristic CRITICAL by CONTENT)
#: and two definitions, so it is deep-GRADABLE. It is the whole point of the story —
#: under the defect this file was excluded from the critical set as a `test_file`.
_LATEST_JAVA = (
    "package svc;\n"
    "\n"
    "public class LatestConfig {\n"
    '    private static final String CREDENTIAL_PREFIX = "svc-prod";\n'
    "\n"
    "    public String resolveCredential(String user) {\n"
    '        return CREDENTIAL_PREFIX + ":" + user;\n'
    "    }\n"
    "}\n"
)

_USER_SERVICE_TEST_JAVA = (
    "package svc;\n"
    "\n"
    "public class UserServiceTest {\n"
    "    public void testResolvesCredentialForUser() {\n"
    '        assert new LatestConfig().resolveCredential("u") != null;\n'
    "    }\n"
    "}\n"
)

#: Ruby grounds but extracts ZERO definitions (`DF-10-2-A`, Story 11.5's) — which is
#: exactly why its TRUE exclusion reason is `zero_definition_module`, not `test_file`.
_MYSPEC_RB = 'def render_credential(user)\n  "#{user}:token"\nend\n'
_USER_SPEC_RB = 'describe "user" do\n  it "resolves" do\n    expect(1).to eq(1)\n  end\nend\n'

#: A `conftest.py` holding only FIXTURES resolves to production BY CONTENT — the tier-3
#: answer DN-2 preserved by replacing the bare `test.py` letter-match with a
#: whole-basename rule instead of deleting it.
_CONFTEST_PY = (
    '"""Shared fixtures for the service suite."""\n'
    "\n"
    "\n"
    "def build_permission_token(user: str) -> str:\n"
    '    return f"{user}:token"\n'
)

_POLYGLOT_FIXTURE: dict[str, str] = {
    # tier 2, the two constants this story changed
    "svc/latest.java": _LATEST_JAVA,
    "svc/UserServiceTest.java": _USER_SERVICE_TEST_JAVA,
    "svc/myspec.rb": _MYSPEC_RB,
    "svc/user_spec.rb": _USER_SPEC_RB,
    # tier 3, and its interaction with the above
    "svc/contest.py": (
        '"""Bidding contest scoring."""\n'
        "\n"
        "\n"
        "def score_contest(bids: list[int]) -> int:\n"
        "    return max(bids) if bids else 0\n"
    ),
    "app/auth_test.py": (
        '"""Production helpers for exercising the authorization boundary."""\n'
        "\n"
        "\n"
        "def build_permission_token(user: str) -> str:\n"
        '    return f"{user}:token"\n'
    ),
    "pkg/conftest.py": _CONFTEST_PY,
    # tier 3 + UNREADABLE — the carve-out `TC-ArgusAgent-PIPELINE-002-09` pins
    "svc/token_test.py": "def issue_permission_token(secret:\n",
}


def _stage(files: dict[str, str], dest: Path) -> Path:
    """Materialize *files* into *dest* as a fresh single-commit git repo.

    The shape ``tests/test_critical_eligibility_pipeline.py::_stage`` uses, kept local
    for the same reason: ``CARTRIDGE_REGISTRY`` is the ground truth of the 6.6 precision
    replay harness and its size is read by a gate, so these fixtures stay out of it.
    """
    dest.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    (dest / ".gitignore").write_text(".argus/\n", encoding="utf-8")
    for args in (
        ["init"],
        ["config", "core.autocrlf", "false"],
        ["config", "user.email", "boundary@argus.test"],
        ["config", "user.name", "ArgusAgent Word Boundary Fixture"],
        ["add", "-A"],
        ["commit", "-m", "polyglot word-boundary fixture"],
    ):
        subprocess.run(["git", "-C", str(dest), *args], check=True, capture_output=True)
    return dest


def _request(repo: Path) -> AuditRequest:
    return AuditRequest(repo_path=str(repo), commit="HEAD", budget=100, materiality_bar="default")


def _drive_polyglot(tmp_path: Path):
    """Run the REAL pipeline over the polyglot fixture and return what both stages said."""
    repo = _stage(_POLYGLOT_FIXTURE, tmp_path / "repo")
    sources = tuple(sorted(_POLYGLOT_FIXTURE))
    index = build_ast_index(repo, sources, partition_id="root")
    entries, _findings, candidates = _detect_per_file(repo, index.entries, _request(repo))
    depth_by_path = {e.file_path: e.depth for e in CoverageLedger.build(entries).entries}
    return candidates, depth_by_path


def assert_two_stages_agree(candidates, depth_by_path: dict[str, CoverageDepth]) -> None:
    """The AC7 invariant, as an executable assertion (raises ``AssertionError``).

    Factored out so the positive control can prove it actually FIRES on a synthetic
    disagreement — a re-proof that cannot fail is not a proof.
    """
    for candidate in candidates:
        path = candidate.file_path
        depth = depth_by_path.get(path)
        if depth is CoverageDepth.AUDITED_DEEP:
            assert candidate.ineligibility is not CriticalIneligibility.TEST_FILE, (
                f"{path} was graded audited_deep by the GRADING stage and excluded from the FR4 "
                f"critical set as a `test_file` by the ELIGIBILITY stage. The two stages disagree "
                f"inside one run — the inconsistency this tool exists to surface in other "
                f"people's repositories. {_WORKING}"
            )
        if is_test_file(path) and not is_test_classification_content_dependent(path):
            assert depth is not CoverageDepth.AUDITED_DEEP, (
                f"{path} is a test file by NAME (tier 1 or tier 2, a property of what the file IS) "
                f"yet reached audited_deep — a test file is audited_shallow BY CONSTRUCTION, so "
                f"this inflates the deep count. {_WORKING}"
            )


def test_TC_ArgusAgent_PIPELINE_002_10_the_two_stages_still_cannot_disagree(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-002-10 — Story 11.2 / AC4.1+AC4.3: the AC7 invariant, RE-PROVEN.

    The invariant was never violated by the defect — both stages called the same predicate
    and reached the same WRONG answer, which is why this story re-PROVES it rather than
    repairing it. The re-proof is load-bearing because this change is the first thing to
    alter that predicate since a second classification stage existed.

    Driven end-to-end over a polyglot fixture exercising BOTH constants and their
    interaction: tier-2 Java and Ruby, tier-3 Python, and the unreadable tier-3 case whose
    carve-out (``-002-09``) must survive untouched.
    """
    candidates, depth_by_path = _drive_polyglot(tmp_path)
    by_path = {c.file_path: c for c in candidates}

    assert len(candidates) == len(_POLYGLOT_FIXTURE), (
        "the fixture did not reach the detect/grade stage; every assertion below would be vacuous"
    )
    assert_two_stages_agree(candidates, depth_by_path)

    # The tier-3 unreadable carve-out — `-002-09`'s rule, restated as a live expectation
    # because this story moved the tier-3 table it depends on.
    assert by_path["svc/token_test.py"].ineligibility is None, (
        "the 'test' label on an UNREADABLE tier-3 name is a guess forced by the content the tool "
        "could not read; the file stays in the critical set and is never disclosed under the "
        "false reason `test_file`"
    )
    assert depth_by_path["svc/token_test.py"] is CoverageDepth.SKIPPED

    # Positive control (AC4.3): the invariant assertion must actually FIRE.
    disagreeing = [
        c.model_copy(update={"ineligibility": CriticalIneligibility.TEST_FILE})
        if c.file_path == "svc/latest.java"
        else c
        for c in candidates
    ]
    assert depth_by_path["svc/latest.java"] is CoverageDepth.AUDITED_DEEP
    with pytest.raises(AssertionError, match="two stages disagree"):
        assert_two_stages_agree(disagreeing, depth_by_path)


def test_TC_ArgusAgent_PIPELINE_002_11_is_test_is_derived_once_and_shared_by_both_paths() -> None:
    """TC-ArgusAgent-PIPELINE-002-11 — Story 11.2 / AC4.2: the structural half, by `ast` walk.

    The BEHAVIOURAL half above proves the two stages agree on today's fixture. This proves
    the MECHANISM by which they could ever come to disagree does not exist: across the
    ``argus/pipeline*.py`` family (read-only) every ``_critical_ineligibility`` call receives
    an ``is_test`` value bound from a SINGLE ``is_test_file`` evaluation in its own function.
    A third derivation, or a call passing a separately-computed value, turns this red.

    Measured 2026-08-11: exactly two such construction sites — the fresh path
    (``_detect_per_file``) and the resume path (``_critical_candidate``). Both were in
    ``pipeline.py``; Story 12.1's NFR-M1 extraction moved both into
    ``argus/pipeline_stages.py``, so the population is now the whole ``pipeline*.py``
    family, ENUMERATED FROM GIT (see :func:`_pipeline_family_sources`) rather than named —
    the guard's reach was widened, its claim was not narrowed. Static walk over the sources
    read as TEXT (the 10.5 DN-6 rule); it imports nothing from ``argus``.
    """
    sources = _pipeline_family_sources()
    functions: list[ast.FunctionDef] = []
    for source in sources:
        tree = ast.parse(source.read_text(encoding="utf-8"))
        functions.extend(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
    assert len(functions) >= 20, (
        f"only {len(functions)} functions parsed out of {[s.name for s in sources]}; the walk "
        f"found nothing and every assertion below is vacuous. {_WORKING}"
    )

    def _calls_to(node: ast.AST, name: str) -> list[ast.Call]:
        return [
            c
            for c in ast.walk(node)
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == name
        ]

    sites = {f.name: f for f in functions if _calls_to(f, "_critical_ineligibility")}
    assert set(sites) == {"_detect_per_file", "_critical_candidate"}, (
        f"the FR4 candidate construction sites are {sorted(sites)}, not the two measured on "
        f"2026-08-11 (`_detect_per_file` — the fresh path — and `_critical_candidate` — the "
        f"resume path). A THIRD site is the one mechanism by which the grading and eligibility "
        f"stages could come to disagree. {_WORKING}"
    )

    for name, function in sorted(sites.items()):
        derivations = _calls_to(function, "is_test_file")
        assert len(derivations) == 1, (
            f"{name} evaluates is_test_file {len(derivations)} times; it must be evaluated ONCE "
            f"per file and the SAME value handed to both stages. {_WORKING}"
        )
        bound = {
            target.id
            for assign in ast.walk(function)
            if isinstance(assign, ast.Assign) and assign.value in derivations
            for target in assign.targets
            if isinstance(target, ast.Name)
        }
        assert len(bound) == 1, (
            f"{name} does not bind its single is_test_file result to one name, so what reaches "
            f"_critical_ineligibility cannot be shown to be that value. {_WORKING}"
        )
        (bound_name,) = bound
        for call in _calls_to(function, "_critical_ineligibility"):
            passed = [k for k in call.keywords if k.arg == "is_test"]
            assert len(passed) == 1 and isinstance(passed[0].value, ast.Name), (
                f"{name} calls _critical_ineligibility without passing `is_test=` as the bound "
                f"name; the eligibility stage would be re-deriving the fact. {_WORKING}"
            )
            assert passed[0].value.id == bound_name, (
                f"{name} passes is_test={passed[0].value.id!r} but derived {bound_name!r} — the "
                f"eligibility stage is reading a SEPARATELY computed classification, which is "
                f"exactly how the two stages come to disagree. {_WORKING}"
            )


def test_TC_ArgusAgent_PIPELINE_002_12_the_vacuous_critical_set_is_closed(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-002-12 — Story 11.2 / AC5.1-AC5.2: the measured consequence, pinned.

    The §A.3 result, in its CORRECTED form. Before this story, on this exact fixture,
    ``svc/latest.java`` was ``is_test=True depth=audited_shallow crit=CRITICAL
    inelig=test_file``, the critical set came out ``()`` and FR16's "all critical
    subsystems deep" clause was satisfied vacuously. After it: the file is CRITICAL,
    ELIGIBLE, deep-graded, and the critical set is NON-EMPTY, so the clause has something
    to be true of.

    ``svc/myspec.rb`` stays excluded — Ruby grounds but extracts zero definitions
    (``DF-10-2-A``, NOT fixed here) — but under the reason that is TRUE.
    """
    candidates, depth_by_path = _drive_polyglot(tmp_path)
    by_path = {c.file_path: c for c in candidates}

    java = by_path["svc/latest.java"]
    assert java.criticality is Criticality.CRITICAL, (
        "the fixture no longer carries a criticality signal, so the false green it reproduces "
        "cannot be observed and this pin is vacuous"
    )
    assert java.ineligibility is None, (
        "ordinary production Java is excluded from the FR4 critical set under the reason "
        "`test_file` — the false statement that made FR16's critical clause vacuous"
    )
    assert depth_by_path["svc/latest.java"] is CoverageDepth.AUDITED_DEEP

    critical = identify_critical_subsystems(candidates)
    assert "svc/latest.java" in critical.paths, (
        "the critical set is empty of the one critical production file in the repository; FR16's "
        "'all critical subsystems deep' clause would be satisfied VACUOUSLY and RELEASE_READY "
        "reachable on a repository nothing critical was examined in (inversion F1)"
    )

    assert (
        critical.heuristic_excluded_ineligible.get("svc/myspec.rb")
        is CriticalIneligibility.ZERO_DEFINITION_MODULE
    ), (
        "Ruby grounds but extracts zero definitions (DF-10-2-A), so `svc/myspec.rb` is genuinely "
        "ineligible — but calling it a `test_file` is a false reason disclosed to the operator"
    )
    assert (
        by_path["svc/user_spec.rb"].ineligibility is CriticalIneligibility.TEST_FILE
    ), "the real RSpec convention `*_spec.rb` must still be recognised"


def test_TC_ArgusAgent_PIPELINE_002_13_the_verdict_machinery_is_untouched() -> None:
    """TC-ArgusAgent-PIPELINE-002-13 — Story 11.2 / AC5.3: FR16 asserted unchanged, not claimed.

    FR37 governs explanation; FR16 governs classification. This story changes neither, and
    the epic's binding note is explicit that no verdict is reworded, upgraded or hedged —
    so the vocabulary, the four-row decision table and every exit code are ASSERTED here
    rather than described as unchanged in prose.
    """
    assert [v.value for v in Verdict] == [
        "RELEASE_READY",
        "NOT_READY_FOR_RELEASE",
        "INSUFFICIENT_COVERAGE",
    ]
    assert [r.value for r in DecisionRow] == [
        "row_1_below_floor",
        "row_2_blocking_findings",
        "row_3_gates_met",
        "row_4_gate_unmet_no_findings",
    ]
    assert {v: exit_code_for_verdict(v) for v in Verdict} == {
        Verdict.RELEASE_READY: 0,
        Verdict.NOT_READY_FOR_RELEASE: 2,
        Verdict.INSUFFICIENT_COVERAGE: 3,
    }


# ─────────────────────────────────────────────────────────────────────────────
# AC6.3 — a rule that lives only in a test is not a rule
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_DOCS_001_53_the_word_boundary_rule_is_registered_in_the_architecture() -> None:
    """TC-ArgusAgent-DOCS-001-53 — Story 11.2 / AC6.3: the enforcement is registered.

    The ``-23``/``-29``/``-41``/``-52`` pattern: §Enforcement must carry the rule text and
    name this module and its ids, so the enforcement cannot be deleted from the
    architecture while the tests quietly survive, or vice versa.
    """
    architecture = _ARCHITECTURE.read_text(encoding="utf-8")
    assert "### Enforcement" in architecture
    for anchor in (
        "Name-classification enforcement",
        _GUARD,
        "TC-ArgusAgent-DETECT-001-96",
        "TC-ArgusAgent-DOCS-001-53",
        "matches a WORD, never a letter sequence",
    ):
        assert anchor in architecture, (
            f"architecture.md §Enforcement is missing the Story 11.2 registration anchor {anchor!r}"
        )
