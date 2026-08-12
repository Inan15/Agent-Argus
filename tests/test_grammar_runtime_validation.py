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


def _audit(repo: Path) -> object:
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
