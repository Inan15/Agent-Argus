"""A wrong grammar version cannot silently produce a false green (Story 11.4).

Verification areas ArgusAgent-INDEX (``TC-ArgusAgent-INDEX-001-NN``), ArgusAgent-REPORT
(``TC-ArgusAgent-REPORT-002-NN``), ArgusAgent-DOCS (``TC-ArgusAgent-DOCS-001-NN``).

What this file exists to stop
------------------------------
Argus resolved ``tree-sitter-<lang>`` versions and folded them into the Epic-5 cache key,
and it had **never once asked whether the toolchain it was about to trust actually behaves
the way it was validated against**. Measured on this tree before the fix, on a staged
repository sitting ABOVE the 60% deep gate, with the real in-bound ``tree-sitter 0.25.2``::

    IN-BOUND grammar : NOT_READY_FOR_RELEASE exit=2 deep=5/6 blocking=1
                       [('vacuous_test_ast', eligible=True), ('orphan_code', False), …]
    DRIFTED  grammar : RELEASE_READY          exit=0 deep=5/6 blocking=0
                       [('orphan_code', False), …, ('vacuous_test_heuristic', False)]

The verdict INVERTED — exit 2 to exit 0, a CI gate that blocked now passes — while the
planted defect stayed exactly where it was. ``vacuous_test_ast`` (``depth_supported is not
None``, verdict-**eligible**) silently became ``vacuous_test_heuristic`` (advisory-only),
and cross-cutting #6 guarantees an advisory finding can never move a verdict. **The moat
that protects against a false 🔴 is the carrier of this false 🟢.**

🚩 And ``deep_ratio`` is **5/6 in BOTH runs**. Every honesty surface this project built —
the coverage ledger, the negative-assurance scope statement, the plain-English report, the
FR34 disclosure — prints the SAME numbers either way. There is no figure a user could
compare, which is why this had to be closed at the loader rather than downstream.

Why this is NOT a version assertion
------------------------------------
``assert tree-sitter < 0.26`` would be **vacuous by construction** and Story 11.4 measured
why, three times over:

1. The flip above happens at an **in-bound** version. A version pin is green on the exact
   tree where the defect is live.
2. The epic's stated reason for the pin does not reproduce: ``py-tree-sitter`` 0.26.0's
   breaking changes are ``Language.version``→``abi_version``, ``Language.query()``→
   ``Query(...)``, the ``timeout_micros`` removals and ``Point`` becoming a tuple subclass.
   Argus uses **none** of them, and the minimum grammar ABI is unchanged.
3. Grammar packages drift independently of the core — this host runs ten grammars across
   four different minor lines, all in bound — and a vendored or patched grammar reports
   whatever metadata it likes.

So the mechanism is a **behavioural per-language canary at the real loader seam**, and the
declared range is recorded evidence beside it (``-125``). Every negative control here is
driven through a simulated seam inside ``monkeypatch.context()``; ⛔ nothing installs or
uninstalls a package, and nothing mutates a shared registry outside a context manager.

RED evidence (AC2.2), captured against the UNMODIFIED tree before any ``argus/`` edit — see
the story's Dev Agent Record for the raw transcript. ``-121`` keeps it permanently
reproducible by reconstructing the pre-fix loader in memory, so this file cannot go green
over its own keystone defect the way ``AI-E3-1`` did.
"""

from __future__ import annotations

import re
import subprocess
import sys
import types
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.index import ast_index  # noqa: E402
from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit  # noqa: E402
from argus.reports import generator as report_generator  # noqa: E402
from argus.shared.grammar_status import (  # noqa: E402
    CANARY_BY_ENTRY_POINT,
    CORE_VERSION_CEILING_EXCLUSIVE,
    CORE_VERSION_FLOOR,
    GRAMMAR_PACKAGE_BY_LANGUAGE,
    INSPECT_CORE_VERSION_COMMAND,
    RUNTIME_UNVALIDATED_TOKEN,
    SUPPORTED_CORE_RANGE,
    CanaryObservation,
    GrammarCanary,
    GrammarFailure,
    canary_for,
    canary_matches,
    classify_reason,
    core_version_is_supported,
    parse_version_tuple,
    registered_failures,
)
from argus.shared.source_languages import LANGUAGE_BY_SUFFIX  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[1]
_PYPROJECT = _REPO_ROOT / "pyproject.toml"
_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"

#: The four languages that load, parse cleanly and extract ZERO definitions on this tree.
#: ``DF-10-2-A``, open and filed — a *different* defect from an unvalidated toolchain, and
#: the trap that would turn this story's false-green fix into a mass false-``INSUFFICIENT_
#: COVERAGE`` if a canary asserted "≥1 definition" uniformly (§C.4 / DN-8).
_ZERO_DEFINITION_LANGUAGES: tuple[str, ...] = ("c", "cpp", "ruby", "rust")

#: The shape of the claim Story 11.4 measured as FALSE. AC5.5 asserts it does not survive
#: anywhere in the artifact set except beside its own correction.
_FALSE_CLAIM = re.compile(
    r"NOT_READY_FOR_RELEASE`?\s*(?:->|→)\s*`?RELEASE_READY", re.IGNORECASE
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers — the staged above-the-gate repository, and the two simulated drifts
# ─────────────────────────────────────────────────────────────────────────────

_CLEAN_MODULE = '''"""Clean production module {n} — lifts the repository above the 60% deep gate."""


def helper_{n}(values):
    total = 0
    for value in values:
        total = total + value
    return total


class Widget{n}:
    def render(self):
        return helper_{n}([1, 2, 3])
'''


def _repo_above_the_deep_gate(dest: Path) -> Path:
    """The real ``vacuous_basic`` cartridge plus four clean modules, committed once.

    The cartridges alone sit at deep 1/2 = 50%, BELOW the 60% row-3 gate, so they can only
    ever fall to ``INSUFFICIENT_COVERAGE`` — which is why the epic's stated flip was never
    reproducible on the corpus it cited. A real user's repository is above the gate, and so
    is this one (Argus's own self-audit measured 61/77 = 79%). Four clean modules is the
    minimum that puts the staged repo there.
    """
    repo, _sha = stage_cartridge("vacuous_basic", dest)
    for n in range(4):
        (repo / "src" / f"module_{n}.py").write_text(_CLEAN_MODULE.format(n=n), encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "above the gate"], check=True, capture_output=True
    )
    return repo


def _wipe_memo_cache(repo: Path) -> None:
    """Empty ``.argus/cache/`` so a leg computes rather than being served a previous leg's answer.

    STORY 12.3 NOTE — why this exists, since deleting it would silently gut ``-125``.
    ``-125`` audits ONE repository THREE times to contrast three TOOLCHAIN STATES (healthy /
    drifted-with-the-fix-disabled / drifted-with-the-guard-live). Story 12.3 wired the FR27
    memoization store onto the detect/grade stage, and the three legs present the SAME
    recording-producing closure to it: the repository, the flags and the RECORDED grammar
    versions are identical in all three, because the drift is simulated by monkeypatching
    Argus's own ``_CALL_NODE_TYPES`` in-process rather than by installing a different grammar
    (see ``_drift_extraction_vocabulary`` — deliberately so). A real drifted grammar arrives
    with its own package version, which the 10.2 per-grammar provenance folds into the key; an
    in-process patch of Argus's internals cannot move that key and is not meant to.

    So without this wipe the second leg would be SERVED the first leg's recorded result and
    would report the healthy verdict, and ``-125`` would fail while asserting something true.
    Wiping is the sanctioned lever, not a workaround: ``memo_store.py``'s own invariant is that
    *the verdict is correct whether or not the cache exists, is warm, or is wiped*. Nothing
    about what ``-125`` measures changes — each leg simply computes its own answer, exactly as
    it did before the store was wired.
    """
    cache_dir = repo / ".argus" / "cache"
    if not cache_dir.is_dir():
        return
    for slot in cache_dir.iterdir():
        if slot.is_file():
            slot.unlink()


def _audit(repo: Path) -> object:
    _wipe_memo_cache(repo)
    return run_audit(
        AuditRequest(repo_path=str(repo), commit="HEAD", budget=200, materiality_bar="default")
    )


def _drift_extraction_vocabulary(patch: pytest.MonkeyPatch) -> None:
    """Rename the call/reference node vocabulary — the shape a drifted grammar has.

    Applied at the module attribute, inside a ``monkeypatch.context()``, so it is reverted
    whatever the test does. This is the EXACT perturbation that produced the measured
    exit 2 → exit 0 flip; ⛔ it is never simulated by touching an installed package.
    """
    patch.setattr(
        ast_index,
        "_CALL_NODE_TYPES",
        frozenset(f"drifted_{node_type}" for node_type in ast_index._CALL_NODE_TYPES),
    )


def _disable_the_fix(patch: pytest.MonkeyPatch) -> None:
    """Reconstruct the PRE-FIX loader: construct a parser and never validate it.

    This is what keeps ``-121`` honest. A test that only asserts the post-fix behaviour
    proves nothing about a defect that was never demonstrated (``AI-E3-1``, Story 3.4),
    and a pasted transcript rots. Disabling exactly the one predicate this story added
    reproduces the original defect on demand, for as long as the guard exists.
    """
    patch.setattr(ast_index, "_toolchain_is_validated", lambda *args, **kwargs: True)


def _grade(verdict: object) -> tuple[str, int, str, int]:
    return (
        str(getattr(verdict, "verdict")),
        int(getattr(verdict, "exit_code")),
        f"{getattr(verdict, 'deep_count')}/{getattr(verdict, 'total_count')}",
        int(getattr(verdict, "blocking_finding_count")),
    )


def _eligible_rule_ids(verdict: object) -> tuple[str, ...]:
    """Rule ids of the findings that can actually MOVE a verdict (``depth_supported`` set).

    Cross-cutting #6: an advisory-only finding never moves a verdict. The false 🟢 is a
    finding sliding out of this tuple while the coverage numbers stand still.
    """
    return tuple(
        sorted(
            finding.rule_id
            for finding in getattr(verdict, "ordered_findings")
            if getattr(finding, "depth_supported", None) is not None
        )
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC3.1 / AC3.2 — the canary is behavioural, per-language, and MEASURED
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("seam", sorted(CANARY_BY_ENTRY_POINT))
def test_every_pinned_canary_passes_on_this_host(seam: tuple[str, str]) -> None:
    """TC-ArgusAgent-INDEX-001-120 — every pinned expectation was measured, not assumed (AC3.1).

    Driven through the REAL loader seam — ``_get_parser_for_lang``, the same one every audit
    uses — never a stand-in. If a row here fails, the toolchain on this host has drifted from
    what Argus was validated against, or an expectation was hand-edited to make a canary pass.
    ⛔ Investigate; do not relax the expectation (§B.5 row 5).
    """
    language, entry_point = seam
    load = ast_index._get_parser_for_lang(language, entry_point)

    assert load.failure is None, (
        f"{language}/{entry_point} did not validate on this host: {load.failure}. Either this "
        "grammar genuinely drifted from the pinned expectation, or the expectation is wrong. "
        "Re-measure with the story's T2 procedure before changing anything."
    )
    assert load.parser is not None

    canary = canary_for(language, entry_point)
    assert canary is not None, f"{seam} is loadable but has no pinned canary — see -123"
    observation = ast_index._observe_canary(load.parser, canary.source)

    assert observation == CanaryObservation(
        parse_error=False,
        vocabulary=canary.vocabulary,
        definitions=canary.definitions,
        edges=canary.edges,
    ), f"{seam}: observed {observation}, pinned {canary}"

    # AR4 / NFR-D2 — the same canary parsed twice yields the same observation. A canary that
    # is not deterministic would make the whole check a coin flip on a real audit.
    assert ast_index._observe_canary(load.parser, canary.source) == observation


def test_no_canary_expectation_can_be_satisfied_by_nothing() -> None:
    """TC-ArgusAgent-INDEX-001-121 — the corpus cannot go vacuous (§C.3 / E.4).

    🔑 The load-bearing property of this story. ``DF-10-2-A`` means four languages honestly
    extract zero definitions, so ``definitions``/``edges`` alone would give Ruby the
    expectation ``((), ())`` — an assertion a **totally broken** Ruby grammar also satisfies.
    ``vocabulary`` is what keeps every row falsifiable: it is the set of node types Argus's
    own extraction tables match, and it is non-empty for all eleven seams including Ruby's.
    """
    assert len(CANARY_BY_ENTRY_POINT) >= 10, (
        f"only {len(CANARY_BY_ENTRY_POINT)} canaries pinned — Argus grounds ten languages "
        "(eleven load seams, counting both TypeScript dialects). A shrunken corpus is a "
        "check that silently stopped covering most of what it claims to."
    )
    for seam, canary in CANARY_BY_ENTRY_POINT.items():
        assert canary.vocabulary, (
            f"{seam}'s canary pins an EMPTY vocabulary, so a grammar that extracts nothing at "
            "all satisfies it. Every canary must assert non-zero observable work (§C.3)."
        )
        assert canary.source.strip(), f"{seam}'s canary source is empty"
        assert tuple(sorted(canary.vocabulary)) == canary.vocabulary, (
            f"{seam}'s vocabulary is not sorted; the probe emits it sorted, so this row could "
            "never match (AR11)."
        )

    # Both-direction control on the pure comparison itself — a matcher that always returns
    # True would make every row above meaningless.
    canary = CANARY_BY_ENTRY_POINT[("python", "language")]
    good = CanaryObservation(False, canary.vocabulary, canary.definitions, canary.edges)
    assert canary_matches(canary, good), "canary_matches rejects a correct observation"
    assert not canary_matches(canary, good._replace(parse_error=True)), "a parse error passed"
    assert not canary_matches(canary, good._replace(vocabulary=())), "a lost vocabulary passed"
    assert not canary_matches(canary, good._replace(definitions=())), "lost definitions passed"
    assert not canary_matches(canary, good._replace(edges=())), "lost edges passed"


def test_the_canary_actually_runs_inside_a_real_index_build(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-122 — the check is REACHED by a real audit (AC3.3).

    A guard that goes green by never executing is the failure Story 10.3's ``-39`` and
    Story 11.3's review iteration 1 both paid for. This counts canary observations during an
    ordinary ``build_ast_index`` call over a real polyglot tree and asserts the count is
    non-zero — and that the existing per-``(lang, entry point)`` load cache still bounds it,
    so the check cannot become a per-file cost on a large repository.
    """
    files = {
        "a.py": "def f():\n    return g()\n",
        "b.py": "def h():\n    return 1\n",
        "c.py": "def i():\n    return 2\n",
        "main.go": "package main\n\nfunc Add(a int) int { return a }\n",
        "app.rb": "def r\n  1\nend\n",
    }
    for name, text in files.items():
        (tmp_path / name).write_text(text, encoding="utf-8")

    observed: list[str] = []
    real = ast_index._observe_canary

    def counting(parser: object, source: str) -> CanaryObservation:
        observed.append(source)
        return real(parser, source)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(ast_index, "_observe_canary", counting)
        index = build_ast_index(tmp_path, tuple(sorted(files)))

    assert observed, (
        "ZERO canaries ran during a real build_ast_index over five source files in three "
        "languages. The check is unreachable from the production path, so every other "
        "assertion in this file is about code no audit executes (§C.3)."
    )
    assert len(observed) == 3, (
        f"{len(observed)} canary parses for 3 distinct languages over 5 files. The check must "
        "run at most once per (language, entry point) per run — the existing load cache. A "
        "per-file cost here would be a real performance regression on a large repository."
    )
    assert len(set(observed)) == 3, "two languages shared a canary source"
    assert sum(1 for entry in index.entries if entry.ast_eligible) == len(files), (
        "the healthy toolchain stopped grounding every file — the positive control is broken, "
        "so the negative controls elsewhere in this file prove nothing. All five files are "
        "well-formed in a language with an installed grammar (Ruby included: DF-10-2-A means "
        "it yields no definitions, not that it fails to parse)."
    )


def test_the_four_zero_definition_languages_still_pass(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-123 — ⛔ DF-10-2-A must NOT fire this check (AC3.4 / DN-8).

    C, C++, Ruby and Rust load, parse cleanly and extract **zero definitions** on this tree.
    That is a filed, open, *different* defect about node-type coverage — not a toolchain
    validation failure. A canary asserting "≥1 definition" uniformly would fire on four
    HEALTHY grammars and take every polyglot audit to ``INSUFFICIENT_COVERAGE``: a
    false-green fix that ships a mass false red is not a fix. Asserted BY NAME so that a
    future change making them fire is caught as a regression rather than shipped.
    """
    for language in _ZERO_DEFINITION_LANGUAGES:
        canary = canary_for(language, "language")
        assert canary is not None, f"{language} lost its pinned canary"
        assert canary.definitions == (), (
            f"{language}'s canary now expects definitions. If DF-10-2-A was fixed, that is "
            "good news — re-measure and update this list deliberately. If it was not, this "
            "expectation is wrong and will downgrade every polyglot audit."
        )
        load = ast_index._get_parser_for_lang(language, "language")
        assert load.failure is None, (
            f"{language} was ruled UNVALIDATED. It parses cleanly on this host and extracts "
            "zero definitions for structural reasons (DF-10-2-A). The canary must not "
            "conflate 'Argus does not cover this grammar's node names' with 'this toolchain "
            "is untrustworthy' — they have opposite remedies."
        )

    # …and it grounds through the real builder, not just the loader.
    (tmp_path / "app.rb").write_text("def r\n  1\nend\n", encoding="utf-8")
    index = build_ast_index(tmp_path, ("app.rb",))
    assert index.entries[0].ast_eligible is True, (
        "a healthy Ruby file lost ast_eligible. DF-10-2-A means Ruby yields no definitions; "
        "it does NOT mean Ruby is unparseable, and downgrading it here would move coverage "
        "denominators on every Ruby repository."
    )


def test_the_canary_corpus_covers_every_reachable_load_seam() -> None:
    """TC-ArgusAgent-INDEX-001-124 — the corpus closes over the enumerable languages (AC3.1).

    Both directions, because either alone is a false green: a seam with no canary is a
    language that escapes the check entirely (and, because the probe fails closed, would
    downgrade every audit of it), and a canary for a seam nothing can reach is dead data
    that hides the gap. Derived from ``LANGUAGE_BY_SUFFIX`` and ``_entry_point_for``, never
    hand-typed — 10.2's hand-list was wrong three times (E.2).
    """
    reachable = {
        (language, ast_index._entry_point_for(language, suffix))
        for suffix, language in LANGUAGE_BY_SUFFIX.items()
    }
    assert reachable, "no load seam was derived at all — this closure is vacuous"

    uncovered = sorted(reachable - set(CANARY_BY_ENTRY_POINT))
    assert not uncovered, (
        f"load seam(s) {uncovered} are reachable from LANGUAGE_BY_SUFFIX but have no pinned "
        "canary. ``canary_for`` fails CLOSED, so every file in those languages would be "
        "recorded UNVALIDATED. Measure the expectation on this host (story T2) and pin it — "
        "do NOT make canary_for fail open."
    )
    unreachable = sorted(set(CANARY_BY_ENTRY_POINT) - reachable)
    assert not unreachable, (
        f"canary/canaries {unreachable} are pinned for seams no suffix routes to. Dead data "
        "in this table is how a real gap goes unnoticed behind a full-looking corpus."
    )
    assert len({language for language, _ in reachable}) == 10, (
        "Argus no longer grounds exactly ten languages. Update source_languages.py, this "
        "corpus and this count together — deliberately."
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — 🔑 the false green: demonstrated, then proven closed
# ─────────────────────────────────────────────────────────────────────────────


def test_a_drifted_grammar_cannot_produce_a_green_verdict(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-125 — 🔑 the whole story, in one run (AC2.1–2.5).

    Three audits of the SAME commit of a repository above the 60% deep gate:

    ==========================  ==============================================================
    Run                         What it pins
    ==========================  ==============================================================
    healthy toolchain           the honest verdict: ``NOT_READY_FOR_RELEASE`` / exit 2, with
                                the planted vacuous test as a **verdict-eligible** finding
    drifted, guard DISABLED     the DEMONSTRATED DEFECT: ``RELEASE_READY`` / exit 0 — and
                                ``deep_ratio`` UNCHANGED, which is why no surface could see it
    drifted, guard LIVE         the FIX: not green, and not exit 0
    ==========================  ==============================================================

    The middle row is what makes this test non-vacuous. It reconstructs the pre-fix loader
    in memory (``_disable_the_fix``) so the defect stays reproducible rather than resting on
    a pasted transcript — ``AI-E3-1``: this project has shipped a keystone test that was
    green over its own keystone bug.

    AC2.3 asserts the **property** — "no green under an unvalidated toolchain" — and not a
    specific replacement verdict, so a later legitimate change to the FR16 decision table
    cannot silently void it.
    """
    repo = _repo_above_the_deep_gate(tmp_path / "above_gate")

    healthy = _audit(repo)
    healthy_grade = _grade(healthy)
    assert str(healthy.verdict).endswith("NOT_READY_FOR_RELEASE"), (
        f"the healthy baseline graded {healthy_grade}, expected NOT_READY_FOR_RELEASE. The "
        "staged repository must reproduce the measured starting state or the flip below "
        "proves nothing (positive control, E.3)."
    )
    assert healthy.exit_code == 2, f"healthy baseline exit {healthy.exit_code}, expected 2"
    assert healthy.deep_count / healthy.total_count > 0.6, (
        f"the staged repository is at deep {healthy_grade[2]}, BELOW the 60% row-3 gate. "
        "Below the gate only INSUFFICIENT_COVERAGE is reachable and the flip is structurally "
        "impossible — which is exactly why the epic's stated flip never reproduced on the "
        "cartridge corpus it cited. Add clean modules until it is above."
    )
    assert "vacuous_test_ast" in _eligible_rule_ids(healthy), (
        "the planted vacuous test is not a VERDICT-ELIGIBLE finding in the healthy run. The "
        "defect is the loss of that eligibility; if it was never there, nothing can be lost."
    )

    # ── the DEFECT, reproduced against the pre-fix loader ────────────────────────────
    with pytest.MonkeyPatch.context() as patch:
        _drift_extraction_vocabulary(patch)
        _disable_the_fix(patch)
        pre_fix = _audit(repo)
    pre_fix_grade = _grade(pre_fix)

    assert str(pre_fix.verdict).endswith("RELEASE_READY"), (
        f"the pre-fix drifted run graded {pre_fix_grade}, expected the measured false green "
        "RELEASE_READY. This row IS the defect; if it no longer reproduces, the premise has "
        "expired the way Story 11.2's silently did — re-measure before weakening anything."
    )
    assert pre_fix.exit_code == 0, "the pre-fix false green did not reach exit 0"
    assert "vacuous_test_ast" not in _eligible_rule_ids(pre_fix), (
        "the verdict-eligible finding survived the drift, so this is not the measured defect."
    )

    # AC2.4 — pin WHY it was undetectable: the one number a user could compare did not move.
    assert pre_fix_grade[2] == healthy_grade[2], (
        f"deep_ratio moved ({healthy_grade[2]} → {pre_fix_grade[2]}). The story's premise is "
        "that the false green is invisible on every surface Argus prints; if the ratio now "
        "distinguishes the two states, that premise has changed and the story's reasoning "
        "must be re-derived rather than assumed (Story 11.2's lesson, AC2.4)."
    )

    # ── the FIX ──────────────────────────────────────────────────────────────────────
    with pytest.MonkeyPatch.context() as patch:
        _drift_extraction_vocabulary(patch)
        fixed = _audit(repo)
    fixed_grade = _grade(fixed)

    assert not str(fixed.verdict).endswith("RELEASE_READY"), (
        f"a drifted extraction vocabulary still produced RELEASE_READY ({fixed_grade}). An "
        "assurance tool must withhold a verdict rather than compute one on a toolchain it "
        "has not validated."
    )
    assert fixed.exit_code != 0, (
        f"a drifted toolchain still exited 0 ({fixed_grade}). Exit 0 is what a CI gate reads; "
        "a verdict that is not green but exits 0 closes nothing."
    )
    assert tuple(
        entry.parse_failure_reason
        for entry in getattr(_audit_index(repo, drift=True), "entries")
        if entry.parse_failure_reason
    ), "no entry recorded a reason token under drift — the degradation is unnamed"


def _audit_index(repo: Path, *, drift: bool) -> object:
    """The AST index the loader produces for *repo*, optionally under the drift."""
    files = tuple(
        sorted(
            str(path.relative_to(repo)).replace("\\", "/")
            for path in repo.rglob("*.py")
            if ".git" not in path.parts
        )
    )
    if not drift:
        return build_ast_index(repo, files)
    with pytest.MonkeyPatch.context() as patch:
        _drift_extraction_vocabulary(patch)
        return build_ast_index(repo, files)


def test_the_drifted_toolchain_records_its_own_named_cause(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-126 — the degradation is a NAMED outcome, never a crash (AC1.3).

    ``NFR-R1`` / ``architecture.md`` §Error-Degradation: a failure becomes a typed finding and
    the run still produces a verdict. The fifth cause must round-trip through the shared
    contract in both directions — a token the classifier does not recognise reaches the
    operator as complete silence, which is the ``DF-AUD-APAA-F`` harm pointed at this story.
    """
    (tmp_path / "a.py").write_text("def f():\n    return g()\n", encoding="utf-8")

    with pytest.MonkeyPatch.context() as patch:
        _drift_extraction_vocabulary(patch)
        index = build_ast_index(tmp_path, ("a.py",))

    entry = index.entries[0]
    assert entry.parse_failure_reason == RUNTIME_UNVALIDATED_TOKEN
    assert entry.ast_eligible is False
    assert entry.parse_failed is False, (
        "parse_failed flipped to True. No parse was ATTEMPTED on the file — the parser was "
        "withheld — and the flag means 'a parse was attempted and failed'. Flipping it moves "
        "the coverage denominator, which is a verdict change by a different route."
    )
    assert entry.definitions == () and entry.edges == ()
    assert index.grammar_versions == (), (
        "an unvalidated grammar recorded a provenance row. It never parsed anything the "
        "index kept, so it cannot vouch for this index (Story 10.2 / DN-6)."
    )

    diagnosis = classify_reason(entry.parse_failure_reason)
    assert diagnosis is not None and diagnosis.failure is GrammarFailure.RUNTIME_UNVALIDATED
    assert diagnosis.language is None, (
        "the fifth cause's diagnosis names a language. It is a fact about the RUNTIME; a "
        "language would invite a per-language remedy that cannot help (AC1.1)."
    )
    assert not RUNTIME_UNVALIDATED_TOKEN.endswith("_python")

    # NFR-S1 — no version string, exception message or host path is persisted.
    serialized = index.model_dump_json()
    for fragment in (str(tmp_path), "0.25.2", "Traceback", "Exception"):
        assert fragment not in serialized, f"{fragment!r} leaked into the persisted index"


# ─────────────────────────────────────────────────────────────────────────────
# AC3.5 — the declared range, as a SECOND and independent signal
# ─────────────────────────────────────────────────────────────────────────────


def test_an_out_of_bound_core_version_also_yields_the_fifth_cause(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-127 — the version bound fires, and is not the mechanism (AC3.5).

    Simulated at the metadata seam inside a ``monkeypatch.context()``. ⛔ Never by installing
    or uninstalling ``tree-sitter``: mutating this venv would invalidate every other figure
    in this story and in the three before it (§0.1.4).

    The pairing is the point. ``-125`` proves the behavioural check fires on its own at an
    IN-BOUND version; this proves the bound fires on its own with a perfectly healthy
    grammar. Neither is sufficient alone, which is why the story refused to ship the version
    assertion the epic asked for.
    """
    (tmp_path / "a.py").write_text("def f():\n    return g()\n", encoding="utf-8")
    real = ast_index._distribution_version

    def at_version(version: str | None):
        def resolve(distribution: str) -> str | None:
            return version if distribution == "tree-sitter" else real(distribution)

        return resolve

    # Positive control FIRST — an in-bound version with a healthy grammar must ground.
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(ast_index, "_distribution_version", at_version("0.25.2"))
        assert build_ast_index(tmp_path, ("a.py",)).entries[0].ast_eligible is True, (
            "an IN-BOUND version was rejected — the control is inverted, so every negative "
            "result below is meaningless."
        )

    for version, why in (
        ("0.26.0", "above the exclusive ceiling"),
        ("0.24.9", "below the floor"),
        ("1.0.0", "far above the ceiling"),
        (None, "not installed / unresolvable metadata"),
        ("not-a-version", "unparseable metadata"),
    ):
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(ast_index, "_distribution_version", at_version(version))
            entry = build_ast_index(tmp_path, ("a.py",)).entries[0]
        assert entry.parse_failure_reason == RUNTIME_UNVALIDATED_TOKEN, (
            f"core version {version!r} ({why}) was accepted. Fail CLOSED: 'I could not tell' "
            "is not 'I checked', and the whole story is that Argus must not vouch on top of "
            "a toolchain it has not examined."
        )


def test_the_declared_range_has_exactly_one_source_of_truth() -> None:
    """TC-ArgusAgent-DOCS-001-54 — the bound in code and in pyproject.toml cannot drift (§C.5).

    This project has paid at least four times for a duplicated enumerable fact
    (``source_languages.py``'s docstring lists the tally). Parsed with ``re`` over the file
    text rather than ``tomllib``: ``requires-python`` is ``>=3.10`` and ``tomllib`` is 3.11+,
    so a ``tomllib`` import here would be a guard that cannot run on the declared floor.
    ⛔ It fails LOUDLY when it cannot parse, never skips — an unreadable pyproject is exactly
    when a drift would go unnoticed.
    """
    assert _PYPROJECT.is_file(), f"pyproject.toml not found at {_PYPROJECT}"
    text = _PYPROJECT.read_text(encoding="utf-8")

    declared = re.findall(r'"tree-sitter(>=[^"]+)"', text)
    assert declared, (
        "no `tree-sitter<specifier>` dependency line could be parsed out of pyproject.toml. "
        "This guard must not pass by finding nothing — fix the pattern, do not delete it."
    )
    assert len(set(declared)) == 1, f"the core is pinned to several different ranges: {declared}"

    assert declared[0] == SUPPORTED_CORE_RANGE, (
        f"pyproject.toml declares `tree-sitter{declared[0]}` but the runtime contract checks "
        f"`{SUPPORTED_CORE_RANGE}`. One of them is a lie to somebody. The specifier is owned "
        "by packaging (12.5 / operator, Story 11.4 DN-7); the runtime constant follows it."
    )
    # …and the other direction: the integer tuples the check actually uses must render the
    # same range, so a hand-edited tuple cannot pass while the string still matches.
    floor = ".".join(str(part) for part in CORE_VERSION_FLOOR)
    ceiling = ".".join(str(part) for part in CORE_VERSION_CEILING_EXCLUSIVE[:2])
    assert SUPPORTED_CORE_RANGE == f">={floor},<{ceiling}", (
        f"SUPPORTED_CORE_RANGE ({SUPPORTED_CORE_RANGE}) does not render "
        f"CORE_VERSION_FLOOR/{CORE_VERSION_CEILING_EXCLUSIVE}. The string is what an operator "
        "reads and the tuples are what the code compares; they must be the same fact."
    )

    # Pure-function controls, both directions, on the comparison the bound actually uses.
    assert core_version_is_supported(parse_version_tuple("0.25.0"))
    assert core_version_is_supported(parse_version_tuple("0.25"))  # 0.25 == 0.25.0
    assert core_version_is_supported(parse_version_tuple("0.25.99"))
    assert not core_version_is_supported(parse_version_tuple("0.26.0"))
    assert not core_version_is_supported(parse_version_tuple("0.26"))
    assert not core_version_is_supported(parse_version_tuple("0.24.99"))
    assert not core_version_is_supported(None)
    assert parse_version_tuple("0.26.0rc1") == (0, 26, 0), "a pre-release suffix broke parsing"
    assert parse_version_tuple("garbage") is None and parse_version_tuple("") is None


# ─────────────────────────────────────────────────────────────────────────────
# AC4.3 / AC4.4 — DF-10-4-E is closed: every cause renders ITS OWN remedy
# ─────────────────────────────────────────────────────────────────────────────


def test_all_five_causes_render_their_own_remedy_and_a_sixth_raises() -> None:
    """TC-ArgusAgent-REPORT-002-33 — DF-10-4-E closed (AC4.3 / AC4.4).

    ``_render_grammar_remedy``'s per-cause branching ended in an **unconditional
    fallthrough**, so Story 11.4's own fifth cause would have silently rendered the
    core-runtime remedy — telling an operator to ``pip install tree-sitter`` when the core is
    installed and fine. That would have reintroduced, inside 10.4's own fix, the exact
    "named reason whose remedy cannot work" defect 10.4 existed to close. The fallthrough is
    now an explicit final arm plus a ``raise``.

    The negative control is the half that matters: an unregistered member must RAISE, not
    render plausible-looking prose for a different cause.
    """
    from collections import Counter

    rendered = {
        failure: report_generator._render_grammar_remedy(failure, Counter({"go": 1}))
        for failure in registered_failures()
    }
    assert len(rendered) == 5, f"{len(rendered)} causes rendered, expected five"
    assert all(text.strip() for text in rendered.values()), "a cause rendered an empty remedy"
    assert len(set(rendered.values())) == 5, (
        "two causes rendered the IDENTICAL remedy line:\n"
        + "\n".join(f"  {f.value}: {t}" for f, t in rendered.items())
        + "\nThat is DF-10-4-E's harm — one operator is being told to run a command that "
        "cannot help them."
    )

    unvalidated = rendered[GrammarFailure.RUNTIME_UNVALIDATED]
    assert SUPPORTED_CORE_RANGE in unvalidated, "the remedy does not name the supported range"
    assert INSPECT_CORE_VERSION_COMMAND in unvalidated, (
        "the remedy does not name the command an operator runs to inspect what they have"
    )
    assert "tree-sitter-go" not in unvalidated, (
        "the fifth cause named a per-language package. The parser CONSTRUCTED — there is "
        "nothing visibly broken to reinstall — and every language is affected."
    )
    # NFR-S1 / 10.4 DN-5 — no observed version, message or host path is rendered.
    assert "0.25.2" not in unvalidated and "Traceback" not in unvalidated

    # Negative control — an unregistered member must be LOUD, not silently mis-rendered.
    fake = types.SimpleNamespace(name="INVENTED_CAUSE", value="invented_cause")
    with pytest.raises(ValueError, match="no operator remedy is registered"):
        report_generator._render_grammar_remedy(fake, Counter({"go": 1}))  # type: ignore[arg-type]


def test_the_fifth_cause_reaches_the_operator_surface() -> None:
    """TC-ArgusAgent-REPORT-002-34 — the callout is not silent for the new cause (AC4.4).

    Reusing ``test_grammar_diagnosis.py``'s stub rather than building a second one: AR7 / §3.3
    forbid a parallel mechanism where one exists, and a second stub is how two surfaces come
    to disagree about the same facts.
    """
    from tests.test_grammar_diagnosis import _callout

    text = _callout({RUNTIME_UNVALIDATED_TOKEN: 4})
    assert text, (
        "the fifth cause produced NO callout at all. An unclassifiable or unhandled token is "
        "invisible to the report — the operator sees NOTHING, which is worse than the wrong "
        "remedy DF-10-4-E would have given."
    )
    assert SUPPORTED_CORE_RANGE in text
    assert "runtime_unvalidated" not in text, (
        "the raw token leaked into operator prose — a prefix slice is being used somewhere "
        "instead of the shared classifier."
    )
    # Mixed with a load cause, each keeps its own remedy (10.4's -27 invariant, extended).
    mixed = _callout({RUNTIME_UNVALIDATED_TOKEN: 1, "grammar_missing_go": 1})
    assert "pip install tree-sitter-go" in mixed, "the installable cause lost its remedy"
    assert SUPPORTED_CORE_RANGE in mixed, "the unvalidated cause lost its remedy in the mix"


# ─────────────────────────────────────────────────────────────────────────────
# AC5.5 — the corrected claim does not survive anywhere uncorrected
# ─────────────────────────────────────────────────────────────────────────────


def test_the_disproved_flip_claim_survives_nowhere_uncorrected() -> None:
    """TC-ArgusAgent-DOCS-001-55 — the false premise is corrected everywhere it was written (AC5.5).

    Story 11.4 re-measured the epic's headline premise — *"on 0.26.0 the cartridge self-audit
    flips NOT_READY_FOR_RELEASE → RELEASE_READY"* — and found it FALSE in the direction it
    names, in two independent ways (upstream 0.26.0 touches nothing Argus uses; and total AST
    loss lands on ``INSUFFICIENT_COVERAGE``/exit 3 because the floor row fires first). Every
    place that stated it must now carry its correction beside it.

    The claim is STRUCK, not deleted (§3.4 evidence immutability), so this asserts
    co-location rather than absence — and the positive control proves the search would find
    an uncorrected instance if one existed (E.4: a grep that matches nothing is not a pass).
    """
    surfaces = [
        _PYPROJECT,
        _ARTIFACTS / "architecture.md",
        _ARTIFACTS / "epics.md",
    ]
    for path in surfaces:
        assert path.is_file(), f"{path} not found — this guard would pass by never reading it"
        text = path.read_text(encoding="utf-8")
        matches = list(_FALSE_CLAIM.finditer(text))
        # Non-vacuity, PER SURFACE rather than in total: the claim was measured in all three
        # of these files, so a regex that stopped matching one of them would otherwise hide
        # behind the other two and this guard would pass over an uncorrected instance.
        assert matches, (
            f"{path.name} contains no instance of the claim shape at all. It was measured "
            "there on 2026-08-12, and the correction STRIKES the sentence rather than "
            "deleting it (§3.4), so it must still be findable. Either the text was deleted "
            "instead of struck, or the pattern rotted — fix it, do not delete this guard."
        )
        for match in matches:
            window = text[max(0, match.start() - 1200) : match.end() + 1600]
            assert re.search(r"11\.4|not reproducible|unverified|NOT REPRODUCIBLE", window, re.I), (
                f"{path.name} states the flip claim at offset {match.start()} with no "
                "correction beside it. Story 11.4 measured that claim FALSE as written; "
                "leaving it standing ships unverified folklore as specification."
            )

    # Positive control — the pattern DOES match the original sentence.
    assert _FALSE_CLAIM.search(
        "On 0.26.0 the cartridge self-audit flips NOT_READY_FOR_RELEASE -> RELEASE_READY"
    ), "the claim pattern no longer matches the sentence it was written for"
    assert not _FALSE_CLAIM.search("the verdict moved from RELEASE_READY to BLOCKED"), (
        "the pattern matches an unrelated sentence — it would fire on correct prose and get "
        "weakened away."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Story 12.5 / NFR-P3 — the default install grounds the languages it claims,
# and a grammar that is nonetheless missing states its reason WHERE IT BITES
# ─────────────────────────────────────────────────────────────────────────────
#
# This file is NFR-P3's home for the same reason it is `-54`'s: the packaging metadata and
# the runtime behaviour it promises are one fact, and splitting them into two files is how a
# `pyproject.toml` that no longer matches the toolchain contract goes unnoticed. The
# `dependencies`/`languages` blocks are parsed with `re` for `-54`'s stated reason —
# `requires-python` is `>=3.10` and `tomllib` is 3.11+, so a `tomllib` import would be a
# guard that cannot run on the declared floor.

#: The `[project] dependencies` array. Anchored at column 0 so the `[project.
#: optional-dependencies]` arrays (`dev`/`llm`/`languages`, all indented-name keys of their
#: own) can never be mistaken for it.
_CORE_DEPS_RE = re.compile(r"^dependencies\s*=\s*\[(.*?)^\]", re.DOTALL | re.MULTILINE)

#: The backward-compatibility alias `pip install "argus-agent[languages]"` resolves through.
_LANGUAGES_EXTRA_RE = re.compile(r"^languages\s*=\s*\[(.*?)^\]", re.DOTALL | re.MULTILINE)


def _requirements(block: str) -> set[str]:
    """Every quoted requirement string in a pyproject dependency array (comments excluded)."""
    return {
        match.strip()
        for match in re.findall(r'"([^"]+)"', block)
    }


def _distribution(requirement: str) -> str:
    """The distribution name of a PEP 508 requirement — everything before its specifier."""
    return re.split(r"[<>=!~;\[\s]", requirement, maxsplit=1)[0].strip()


def test_the_default_install_grounds_every_language_it_claims() -> None:
    """TC-ArgusAgent-DOCS-001-61 — Story 12.5 / NFR-P3 (AC1 + AC3): packaging matches the claim.

    NFR-P3 classifies coverage degraded by a grammar absent from the DEFAULT install as a
    **packaging defect**, so the assertion is over `[project] dependencies` — the array a bare
    ``pip install argus-agent`` resolves — and never over the ``[languages]`` extra, which by
    definition requires a user to discover it.

    The expected set is DERIVED from ``GRAMMAR_PACKAGE_BY_LANGUAGE``, never hand-typed: that
    table is already pinned equal to the enumerable language set by
    ``TC-ArgusAgent-REPORT-002-25``, so an eleventh language added to the tool but not to the
    default install turns this red at edit time. A hand-typed list of ten is trap E.5 — the
    prose copy of a pinned figure that drifts (``AI-E9-7/R1``).
    """
    assert _PYPROJECT.is_file(), f"pyproject.toml not found at {_PYPROJECT}"
    text = _PYPROJECT.read_text(encoding="utf-8")

    core = _CORE_DEPS_RE.search(text)
    assert core, (
        "no `dependencies = [...]` array could be parsed out of pyproject.toml. This guard "
        "must not pass by finding nothing — fix the pattern, do not delete it."
    )
    core_requirements = _requirements(core.group(1))
    core_distributions = {_distribution(req) for req in core_requirements}
    assert core_distributions, "the core dependency array parsed to nothing — the pattern rotted"

    # Non-vacuity: the expectation is the shared table, and the shared table is the language set.
    assert set(GRAMMAR_PACKAGE_BY_LANGUAGE) == set(LANGUAGE_BY_SUFFIX.values()), (
        "the grammar-package table and the enumerable language set have diverged; this guard "
        "would then assert the default install grounds a set Argus does not claim to support"
    )
    missing = sorted(set(GRAMMAR_PACKAGE_BY_LANGUAGE.values()) - core_distributions)
    assert not missing, (
        f"the DEFAULT install does not ground every language Argus claims: {missing} are not in "
        "`[project] dependencies`. NFR-P3 classifies exactly this as a packaging defect — a user "
        "on that stack is silently given a worse result and would have to discover an optional "
        "extra to fix it. Promote them into `dependencies`, do not document a workaround."
    )

    # AC3 — `pip install "argus-agent[languages]"` must keep working, and the alias may not
    # become a SECOND source of truth: every requirement it names is one the default already
    # carries, specifier included. An alias with its own bound is a divergence waiting to be
    # measured (`argus/shared/source_languages.py`'s docstring lists what that has cost here).
    extra = _LANGUAGES_EXTRA_RE.search(text)
    assert extra, (
        "the `[project.optional-dependencies] languages` extra was REMOVED. Story 10.2 "
        "documented it publicly, so `pip install \"argus-agent[languages]\"` is a command "
        "someone has in a script; removing it breaks that install with a resolver error."
    )
    extra_requirements = _requirements(extra.group(1))
    assert extra_requirements, "the `languages` extra parsed to nothing — the pattern rotted"
    drifted = sorted(extra_requirements - core_requirements)
    assert not drifted, (
        f"the `[languages]` extra names requirement(s) the default install does not: {drifted}. "
        "The extra is a backward-compatibility ALIAS as of Story 12.5; if the two lists can "
        "differ, one of them is a lie about what a user gets."
    )

    # AC3 — the documentation and the metadata describe the SAME product. Struck spans are
    # RETRACTED text (§3.4: superseded, never deleted), so they are removed before the live
    # README is read — otherwise the mandated amendment form would look identical to the defect.
    readme = (_REPO_ROOT / "README.md").read_text(encoding="utf-8")
    live_readme = re.sub(r"~~(?:[^\n]|\n(?!\s*\n))+?~~", " ", readme)
    assert "default install grounds **Python only**" not in live_readme, (
        "README.md still tells the reader, in live text, that the default install grounds "
        "Python only. That was true until Story 12.5 promoted the nine grammars; it is now a "
        "false statement about the package this repository builds."
    )
    assert "default install grounds **Python only**" in readme, (
        "the superseded sentence was DELETED from README.md rather than struck. §3.4: the "
        "record of what the product used to promise is what makes the change auditable, and "
        "this project keeps it (README.md already strikes a superseded CLI invocation)."
    )
    assert "The default install grounds every language Argus claims to support" in live_readme, (
        "README.md does not state the new behaviour positively. `-17`'s lesson applies here: a "
        "surface can satisfy 'says nothing false' by saying nothing at all, and silence leaves "
        "the reader with the optional-extra instructions they already have in their notes."
    )
    assert "[languages]" in readme, (
        "README.md no longer mentions the `[languages]` extra at all. It is RETAINED for "
        "backward compatibility (AC3), and a retained public command that no document "
        "mentions is one nobody can tell is still supported."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Story 12.5 / AC2 — the reason is stated AT THE POINT OF DOWNGRADE (DF-10-4-A)
# ─────────────────────────────────────────────────────────────────────────────
#
# `_render_readability_warning` fires only when NOTHING parsed (`if eligible: return []`), so a
# polyglot repository whose Python parses learned nothing about its failed Go grammar. That
# blind spot was measured and filed as `DF-10-4-A`, fenced by
# `test_grammar_diagnosis.py::TC-ArgusAgent-REPORT-002-29`, and handed to THIS story by name.
# It is closed by a SEPARATE surface rather than by widening 10.4's trigger — the two answer
# different questions ("this verdict reflects tooling, not code quality" vs. "these specific
# files were downgraded, and here is what to install"), and 10.4's fence stays green.


def _partial_index(reasons: dict[str, int]) -> object:
    """A duck-typed index where SOME file parsed — the DF-10-4-A shape, per the 10.4 stub."""
    from tests.test_grammar_diagnosis import _index_stub

    index = _index_stub(reasons)
    eligible = types.SimpleNamespace(
        file_path="src/app.py",
        ast_eligible=True,
        parse_failed=False,
        parse_failure_reason=None,
        definitions=(),
        edges=(),
    )
    index.entries = tuple(index.entries) + (eligible,)  # type: ignore[attr-defined]
    return index


def _ledger_for(index: object) -> object:
    """A real ledger grading every parse-failed entry `audited_shallow` — the downgrade point."""
    from argus.ledger.coverage_ledger import (
        CoverageDepth,
        CoverageLedger,
        CoverageLedgerEntry,
    )

    return CoverageLedger.build(
        tuple(
            CoverageLedgerEntry(
                file_path=entry.file_path,
                depth=(
                    CoverageDepth.AUDITED_DEEP
                    if entry.ast_eligible
                    else CoverageDepth.AUDITED_SHALLOW
                ),
                claim_present=entry.ast_eligible,
            )
            for entry in getattr(index, "entries", ())
        )
    )


def _downgrade_section(reasons: dict[str, int]) -> str:
    index = _partial_index(reasons)
    return "\n".join(
        report_generator._render_grammar_downgrade_section(_ledger_for(index), index)
    )


def test_a_missing_grammar_names_itself_at_the_point_of_downgrade() -> None:
    """TC-ArgusAgent-REPORT-002-35 — Story 12.5 / AC2 (closes DF-10-4-A).

    RED-first against the shipped tree: before this story the whole surface returned nothing
    for a partially-parsed repository, so every assertion below failed on the "no callout at
    all" clause.

    The load-bearing half is the LAST assertion: 10.4's all-or-nothing callout must STILL be
    silent for this input. If closing DF-10-4-A had been done by widening
    ``_render_readability_warning``, a partially-parsed repository would be told *"No file
    could be parsed"* — a false statement about the run, and the sentence 10.4's own guard
    exists to keep truthful.
    """
    from argus.ledger.coverage_ledger import CoverageLedger

    text = _downgrade_section({"grammar_missing_go": 2})
    assert text, (
        "a repository whose Python parsed and whose Go did NOT was told nothing at all about "
        "its missing Go grammar — DF-10-4-A, the blind spot this story owns by name"
    )
    assert "tree-sitter-go" in text, "the missing grammar PACKAGE is not named"
    assert "pip install tree-sitter-go" in text, (
        "no runnable remedy at the point of downgrade — NFR-P3 requires the reason AND the fix"
    )
    assert "audited_shallow" in text, (
        "the section does not state the depth the affected files actually reached, so a reader "
        "cannot connect it to the coverage number that withheld their verdict"
    )
    assert "grammar_missing_go_0.src" in text, (
        "no file is NAMED. 'some Go files were downgraded' is not a point-of-downgrade "
        "disclosure — it is the same aggregate the coverage ratio already gave them."
    )
    # Scoped to the PROSE half: the stub's synthetic paths are named after their reason
    # token, so a whole-document scan would flag the file-listing column it exists to require.
    prose = text.split("### Files downgraded")[0]
    assert "grammar_missing_" not in prose, (
        "the raw reason token leaked into operator prose — classify through the shared "
        "contract, never by slicing the token at a call site"
    )
    assert "src/app.py" not in text, (
        "a file that parsed FINE is listed as downgraded by a grammar failure — the section "
        "must name only what the failure actually cost"
    )

    # 10.4's fence, from the other side: the all-or-nothing callout stays silent here.
    index = _partial_index({"grammar_missing_go": 2})
    assert report_generator._render_readability_warning(_ledger_for(index), index) == [], (  # type: ignore[arg-type]
        "the 'No file could be parsed' callout now fires on a repository where a file DID "
        "parse. That sentence would be false, and TC-ArgusAgent-REPORT-002-29 fences it."
    )
    assert report_generator._render_grammar_downgrade_section(CoverageLedger(entries=()), None) == []


def test_the_downgrade_section_does_not_double_report_or_misfire() -> None:
    """TC-ArgusAgent-REPORT-002-36 — Story 12.5 / AC2: one surface per run, each with its own remedy.

    Three negative controls and one mixed-class control. The double-report control is the one
    that matters: when NOTHING parsed, 10.4's callout already says it in the loudest register
    the report has, and a second block repeating the same remedies would train a reader to
    skim both.
    """
    from tests.test_grammar_diagnosis import _index_stub

    total_failure = _index_stub({"grammar_missing_go": 2})
    ledger = _ledger_for(total_failure)
    assert report_generator._render_grammar_downgrade_section(ledger, total_failure) == [], (
        "the point-of-downgrade section fired on a run where NOTHING parsed. That run is "
        "already covered by `_render_readability_warning`, in a louder register, with the same "
        "remedies — two blocks saying one thing is how a reader learns to skip both."
    )
    assert report_generator._render_readability_warning(ledger, total_failure), (
        "…and the control is not vacuous: 10.4's callout DOES fire for that same input"
    )

    assert _downgrade_section({"syntax_error": 3}) == "", (
        "a syntax error was given a grammar remedy. Only grammar-LOAD failures may claim one — "
        "telling someone to `pip install` a grammar they already have, over a typo in their "
        "own file, is the DF-AUD-APAA-F harm in a new place."
    )
    assert _downgrade_section({}) == ""

    # Mixed classes: each keeps ITS OWN remedy, never a blended `pip install` line.
    mixed = _downgrade_section(
        {
            "grammar_missing_go": 2,
            "grammar_entrypoint_missing_php": 1,
            "grammar_load_failed_rust": 1,
        }
    )
    assert "pip install tree-sitter-go" in mixed, "the installable cause lost its remedy in the mix"
    assert "pip install tree-sitter-php" not in mixed, (
        "cause 2's grammar IS installed — this line tells the operator to install what they "
        "already have, which is exactly the defect the shared contract exists to prevent"
    )
    assert "pip install tree-sitter-rust" not in mixed, (
        "cause 3's grammar is installed and broken; `pip install` re-fetches the same wheel"
    )
    assert "tree-sitter-php" in mixed and "tree-sitter-rust" in mixed, (
        "a language present in the index went unmentioned entirely"
    )


def test_the_plain_english_summary_names_the_package_per_language_class() -> None:
    """TC-ArgusAgent-REPORT-002-37 — Story 12.5 / AC2, second clause: the human register too.

    The report renders a table; the human register renders sentences. Both must name the
    SPECIFIC package per missing language class, and both must read off the shared
    classification rather than each parsing the token their own way.

    The exhaustiveness control is 11.4's ``DF-10-4-E`` lesson applied to the new surface: a
    sixth cause added without a sentence here must RAISE, never fall through to another
    cause's remedy — which is how an operator is handed a command that cannot help them.
    """
    from argus.reports import plain_english

    lines = plain_english.render_grammar_downgrade_summary(
        ("grammar_missing_go", "grammar_missing_go", "syntax_error", None)
    )
    assert len(lines) == 1, f"expected exactly one class line, got {lines}"
    line = lines[0]
    assert "tree-sitter-go" in line and "pip install tree-sitter-go" in line
    assert "2 go" in line, "the affected file count per language is not stated"
    assert "audited_shallow" in line, "the human register does not say what the files became"
    assert "grammar_missing_" not in line, "the raw token leaked into human prose"
    # The module's own contract: MARKUP-FREE, so the same string is correct on a terminal
    # and inside a Markdown callout (see `render_depth_meaning`'s docstring).
    assert "*" not in line and "#" not in line and "|" not in line

    assert plain_english.render_grammar_downgrade_summary(()) == ()
    assert plain_english.render_grammar_downgrade_summary(("syntax_error",)) == ()

    # Every registered cause renders its OWN sentence; a sixth is LOUD.
    from collections import Counter

    rendered = {
        failure: plain_english._downgrade_sentence(failure, Counter({"go": 1}))
        for failure in registered_failures()
    }
    assert len(set(rendered.values())) == len(registered_failures()) == 5, (
        "two causes rendered the identical sentence — one operator is being told to run a "
        f"command that cannot help them:\n{rendered}"
    )
    core_only = rendered[GrammarFailure.CORE_RUNTIME_MISSING]
    assert "tree-sitter-go" not in core_only, (
        "the core-runtime cause named a per-language package. Every language is down; naming "
        "one grammar is the maximally wrong remedy."
    )
    unvalidated = rendered[GrammarFailure.RUNTIME_UNVALIDATED]
    assert SUPPORTED_CORE_RANGE in unvalidated and INSPECT_CORE_VERSION_COMMAND in unvalidated
    assert "tree-sitter-go" not in unvalidated

    fake = types.SimpleNamespace(name="INVENTED_CAUSE", value="invented_cause")
    with pytest.raises(ValueError, match="no operator remedy is registered"):
        plain_english._downgrade_sentence(fake, Counter({"go": 1}))  # type: ignore[arg-type]
