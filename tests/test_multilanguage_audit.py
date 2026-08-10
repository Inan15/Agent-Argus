"""Multi-language auditing is reachable end-to-end, not just component-by-component.

Verification area ArgusAgent-INTAKE (TC-ArgusAgent-INTAKE-003-NN).

The 2026-07-28 change proposal recorded multi-language support as delivered, and
each component genuinely had it: ``stack_detect`` knew 10 languages, ``ast_index``
probed 10 grammars, ``is_test_file`` knew 10 test conventions. It was still false
end-to-end, because the two stages that GATE everything upstream were Python-only:

* intake enumerated ``{.py, .pyi, .pyx}``, so no other language reached the index;
* the per-file loop dropped every non-Python file to ``SKIPPED`` before any pass ran.

A JavaScript repository therefore ran to completion, emitted
``INSUFFICIENT_COVERAGE``, and never said it had been unable to read a single file.
These tests pin the whole chain so a narrow copy upstream cannot silently disable
the breadth downstream again.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")

# The two end-to-end JavaScript tests below assert that source files reach
# `audited_deep`, which is only reachable with the `tree-sitter-javascript` grammar from
# the OPTIONAL `[languages]` extra. Under a bare `pip install .[dev]` they fail with
# `deep_count == 0`, which is an ENVIRONMENT statement, not a defect statement — the
# graceful-degradation contract for that same state is pinned separately by
# `test_missing_grammar_is_named_not_reported_as_unsupported`.
#
# Skipping is only defensible because it cannot hide a regression: audit-ci.yml installs
# `.[dev,languages]` and sets ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1, which converts the skip
# back into a hard failure. A silently-skipped multi-language claim would be exactly the
# false green this suite exists to prevent.
_REQUIRE_GRAMMARS = os.getenv("ARGUS_REQUIRE_LANGUAGE_GRAMMARS") == "1"


def _grammar_installed(module_name: str) -> bool:
    """True when a tree-sitter grammar package is importable in this environment.

    Total by construction. ``find_spec`` returns ``None`` for a simply-absent package but
    RAISES for a broken one — a finder that itself errors, a missing parent package
    (``ModuleNotFoundError``), or a ``None`` entry left in ``sys.modules``
    (``ValueError``). Every one of those means the same thing here: the grammar is not
    usable. Letting one escape would abort COLLECTION of this whole module, taking the
    grammar-independent tests down with it.
    """
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ValueError):
        return False


requires_js_grammar = pytest.mark.skipif(
    not _grammar_installed("tree_sitter_javascript") and not _REQUIRE_GRAMMARS,
    reason=(
        "tree-sitter-javascript is not installed (optional `[languages]` extra). "
        "Install it with `pip install .[languages]`, or set "
        "ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 to fail instead of skip."
    ),
)

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.intake.source_state import resolve_source_state  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit  # noqa: E402
from argus.shared.source_languages import (  # noqa: E402
    AUDITABLE_SUFFIXES,
    LANGUAGE_BY_SUFFIX,
    language_for_suffix,
)

_JS_PROJECT = {
    "package.json": '{"name":"jsapp"}\n',
    "src/index.js": "function main(){ return 1; }\nmodule.exports={main};\n",
    "src/auth.js": 'function login(pw){ return pw === "x"; }\nmodule.exports={login};\n',
    "test/index.test.js": 'test("x", () => { expect(1).toBe(1); });\n',
    "node_modules/dep/index.js": "var x = 1;\n",
}

_GO_PROJECT = {
    "go.mod": "module example.com/app\n\ngo 1.21\n",
    "main.go": "package main\n\nfunc main() { greet() }\n",
    "greet.go": 'package main\n\nimport "fmt"\n\nfunc greet() { fmt.Println("hi") }\n',
    "greet_test.go": 'package main\n\nimport "testing"\n\nfunc TestGreet(t *testing.T) { greet() }\n',
    "vendor/dep/x.go": "package dep\n",
}


def _make(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
    return root


# ─────────────────────────────────────────────────────────────────────────────
# One definition, not four
# ─────────────────────────────────────────────────────────────────────────────


def test_every_stage_shares_one_suffix_map() -> None:
    """TC-ArgusAgent-INTAKE-003-01 — the divergence that caused this cannot recur.

    intake, source-state resolution, and the AST index must agree on what counts as
    source. They previously held three different copies, and the narrowest one — being
    upstream — silently won.
    """
    from argus.index import ast_index
    from argus.intake import repo_loader, source_state

    assert repo_loader._SOURCE_SUFFIXES is AUDITABLE_SUFFIXES
    assert source_state._SOURCE_SUFFIXES is AUDITABLE_SUFFIXES
    assert ast_index._LANGUAGE_BY_SUFFIX is LANGUAGE_BY_SUFFIX
    # Anything enumerable must be classifiable, or it would enumerate into a void.
    for suffix in AUDITABLE_SUFFIXES:
        assert language_for_suffix(suffix) is not None


def test_the_ten_claimed_languages_are_enumerable() -> None:
    """TC-ArgusAgent-INTAKE-003-02 — the claim in the change proposal, pinned."""
    claimed = {
        "python", "javascript", "typescript", "go", "rust",
        "java", "c", "cpp", "ruby", "php",
    }
    assert claimed <= set(LANGUAGE_BY_SUFFIX.values())


# ─────────────────────────────────────────────────────────────────────────────
# End-to-end reach
# ─────────────────────────────────────────────────────────────────────────────


@requires_js_grammar
def test_javascript_project_enumerates_and_grades(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-003-03 — a JS repo audits; it used to enumerate ZERO files."""
    root = _make(tmp_path / "jsapp", _JS_PROJECT)

    state = resolve_source_state(root)

    assert set(state.source_files) == {
        "src/index.js", "src/auth.js", "test/index.test.js",
    }
    assert "node_modules/dep/index.js" not in state.source_files

    verdict = run_audit(
        AuditRequest(
            repo_path=str(root), commit="HEAD", budget=100, materiality_bar="default"
        )
    )
    assert verdict.total_count == 3
    # The two source files can reach deep; the test file is graded shallow.
    assert verdict.deep_count == 2


def test_go_project_enumerates_and_excludes_vendor(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-003-04 — Go, with `vendor/` corroborated by go.mod."""
    root = _make(tmp_path / "goapp", _GO_PROJECT)

    state = resolve_source_state(root)

    assert set(state.source_files) == {"main.go", "greet.go", "greet_test.go"}
    assert not any(f.startswith("vendor/") for f in state.source_files)


@requires_js_grammar
def test_non_python_test_file_is_not_run_through_the_python_vacuous_detector(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-INTAKE-003-05 — no false accusations on idioms it cannot read.

    The vacuous detector counts bare ``assert`` statements, a Python idiom. A JS suite
    uses ``expect().toBe()``, so running it there would emit vacuous accusations from
    evidence the detector cannot actually interpret — and a wrong 🔴 is the lethal
    failure this codebase is built to avoid. The file is still graded (examined), just
    never accused.
    """
    root = _make(tmp_path / "jsapp", _JS_PROJECT)

    verdict = run_audit(
        AuditRequest(
            repo_path=str(root), commit="HEAD", budget=100, materiality_bar="default"
        )
    )

    vacuous = [
        f for f in verdict.ordered_findings if f.rule_id.startswith("vacuous_test")
    ]
    assert vacuous == []
    # …but the JS test file WAS examined, not dropped: all three files are in the
    # ledger, and exactly one of them (the test) is below deep.
    assert verdict.total_count == 3
    assert verdict.deep_count == 2


def test_missing_grammar_is_named_not_reported_as_unsupported(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-003-06 — 'grammar not installed' ≠ 'language unsupported'.

    Two states, two remedies (one pip install vs nothing). Reporting the second for
    the first leaves an operator with a zero-coverage verdict and no way to act.
    """
    root = tmp_path / "exotic"
    root.mkdir()
    (root / "a.rb").write_text("def hi\n  1\nend\n", encoding="utf-8")

    index = build_ast_index(root, ("a.rb",))
    entry = index.entries[0]

    if not entry.ast_eligible:
        assert entry.parse_failure_reason == "grammar_missing_ruby"
        assert entry.parse_failure_reason != "non_python"


# ─────────────────────────────────────────────────────────────────────────────
# Story 10.2 / AC3 — the grounding MATRIX: enumerable is not groundable
# ─────────────────────────────────────────────────────────────────────────────
#
# `-02` above asserts `claimed <= set(LANGUAGE_BY_SUFFIX.values())` — that the ten languages can be
# ENUMERATED. That is the weaker property, asserted where the stronger one was assumed, and it is
# exactly how the following survived a full epic green:
#
#   measured 2026-08-10 on this tree — a.ts → ast_eligible=False, `grammar_missing_typescript`
#                                      a.php → ast_eligible=False, `grammar_missing_php`
#
# …while BOTH grammar packages were installed and BOTH were declared in the `[languages]` extra.
# `tree_sitter_typescript` exports `language_typescript`/`language_tsx` and `tree_sitter_php`
# exports `language_php`/`language_php_only`; neither exports the bare `language()` the loader
# looked for, so `getattr(mod, "language", None)` returned `None`, nothing raised, and the file was
# reported with a token that tells an operator to install a package they already have.
#
# Story 10.2 amends FR7 — the BINDING capability contract — to record multi-language AST grounding
# as delivered in V1. These tests are the reason that amendment is TRUE at the moment it is
# written, rather than one false spec claim replacing another in the oversell direction.

#: A minimal, valid, one-definition fixture per language. Keyed by FILENAME, because the suffix is
#: what selects the grammar dialect: `.ts` and `.tsx` are both `typescript` in LANGUAGE_BY_SUFFIX,
#: and TSX needs the JSX-aware entry point or every `<div/>` is a syntax error.
_GROUNDING_FIXTURES: dict[str, str] = {
    "sample.c": "int add(int a, int b) { return a + b; }\n",
    "sample.cpp": "int add(int a, int b) { return a + b; }\n",
    "sample.go": "package main\n\nfunc Add(a int, b int) int { return a + b }\n",
    "sample.java": "class Sample { int add(int a, int b) { return a + b; } }\n",
    "sample.js": "function add(a, b) { return a + b; }\n",
    "sample.php": "<?php\nfunction add($a, $b) { return $a + $b; }\n",
    "sample.py": "def add(a, b):\n    return a + b\n",
    "sample.rb": "def add(a, b)\n  a + b\nend\n",
    "sample.rs": "fn add(a: i32, b: i32) -> i32 { a + b }\n",
    "sample.ts": "function add(a: number, b: number): number { return a + b; }\n",
    # The TSX dialect (AC3.2). JSX syntax is a hard parse error under the plain `typescript`
    # grammar, so this fixture is a real discriminator between the two entry points and not a
    # decorative eleventh case.
    "sample.tsx": (
        "function Greeting(props: { name: string }) {\n"
        "  return <div className=\"hi\">{props.name}</div>;\n"
        "}\n"
    ),
}

_FIXTURE_LANGUAGES: frozenset[str] = frozenset(
    language_for_suffix(Path(name).suffix) or "" for name in _GROUNDING_FIXTURES
)


def _grounding_skip_reason(language: str) -> str | None:
    """Why *language* may legitimately be skipped here, or ``None`` if it must ground.

    An absent optional grammar is an ENVIRONMENT statement, not a defect statement — the same
    judgement `requires_js_grammar` above already makes. It is only defensible because it cannot
    hide a regression: `audit-ci.yml` installs `.[dev,languages]` and sets
    ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1, which turns every skip below into a hard failure. A skip
    that could hide THIS regression would be the false green this file exists to prevent.
    """
    if _REQUIRE_GRAMMARS:
        return None
    if _grammar_installed(f"tree_sitter_{language}"):
        return None
    return (
        f"tree-sitter-{language} is not installed (optional `[languages]` extra). Install it with "
        "`pip install .[languages]`, or set ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 to fail instead of "
        "skip."
    )


def test_every_enumerable_language_has_a_grounding_fixture() -> None:
    """TC-ArgusAgent-INTAKE-003-07 — Story 10.2/AC3.3: language #11 cannot be added unpinned.

    The matrix below is only a proof if it covers the whole enumerated space. A language added to
    `LANGUAGE_BY_SUFFIX` with no fixture here would silently widen what Argus claims to enumerate
    without widening what it is shown to ground — which is the precise gap between `-02` and this
    section, and the gap TypeScript and PHP lived in for an entire epic.
    """
    enumerable = set(LANGUAGE_BY_SUFFIX.values())
    unpinned = sorted(enumerable - _FIXTURE_LANGUAGES)
    assert not unpinned, (
        f"language(s) are enumerable but have NO grounding fixture: {unpinned}. Add a minimal "
        "valid fixture to _GROUNDING_FIXTURES so the matrix proves the language actually reaches "
        "`ast_eligible=True`. Enumerable is not groundable (argus/shared/source_languages.py:27-32)."
    )

    stray = sorted(_FIXTURE_LANGUAGES - enumerable)
    assert not stray, (
        f"fixture(s) claim language(s) absent from LANGUAGE_BY_SUFFIX: {stray}. The matrix must "
        "test the real enumerated space, not a hand-kept parallel list."
    )

    # `.tsx` is named explicitly (AC3.2): it is a SUFFIX-level dialect inside an already-covered
    # language, so the set comparison above cannot see whether it is present.
    assert "sample.tsx" in _GROUNDING_FIXTURES, (
        "the `.tsx` dialect fixture was removed. `.ts` and `.tsx` are both `typescript`, but TSX "
        "needs the JSX-aware grammar entry point; without this fixture `.tsx` can silently regress "
        "to a syntax error while `.ts` stays green."
    )


@pytest.mark.parametrize("filename", sorted(_GROUNDING_FIXTURES))
def test_every_claimed_language_actually_grounds(filename: str, tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-003-08 — Story 10.2/AC3: the ten claimed languages reach ast_eligible.

    The STRONGER property `-02` assumed. FR7 now records multi-language AST grounding as delivered
    in V1; this is what makes that sentence true. A failure here means the specification is
    overselling the binding capability contract — the defect class Story 10.5 files, manufactured
    inside the story whose job is closing its inverse.
    """
    language = language_for_suffix(Path(filename).suffix)
    assert language is not None, f"{filename} has no language mapping — fixture and map disagree"

    skip_reason = _grounding_skip_reason(language)
    if skip_reason is not None:
        pytest.skip(skip_reason)

    root = tmp_path / "matrix"
    root.mkdir()
    (root / filename).write_text(_GROUNDING_FIXTURES[filename], encoding="utf-8")

    index = build_ast_index(root, (filename,))
    entry = index.entries[0]

    assert entry.ast_eligible, (
        f"{language} ({filename}) did NOT ground: ast_eligible=False, "
        f"parse_failure_reason={entry.parse_failure_reason!r}. The grammar package "
        f"`tree_sitter_{language}` IS importable in this environment, so a "
        f"`grammar_missing_{language}` token here is a MISDIAGNOSIS: it tells an operator to "
        "install a package they already have (the DF-AUD-APAA-F harm, third cause). Check the "
        "per-language entry point in argus/index/ast_index.py — not every grammar package exports "
        "a bare `language()`."
    )
    assert entry.parse_failure_reason is None and not entry.parse_failed, (
        f"{language} ({filename}) is ast_eligible yet carries a degradation record "
        f"(parse_failed={entry.parse_failed}, reason={entry.parse_failure_reason!r}) — eligibility "
        "and honest degradation must not both be true (AR10)."
    )


#: MEASURED on this tree 2026-08-10, AFTER the story-10.2 grammar-resolution fix. Grounding
#: (`ast_eligible`) and STRUCTURE EXTRACTION are two different capabilities, and they do not yet
#: coincide: four languages parse cleanly and yield no `Definition` at all, because
#: `ast_index._DEF_KIND_BY_NODE` / `_node_name` were written against Python's node vocabulary.
#:
#:   c, cpp  — `function_definition` carries its name under the `declarator` field, not `name`
#:   ruby    — a method is the node type `method`, which is not in the kind map at all
#:   rust    — the node type is `function_item`, while the map lists `fn_item`
#:
#: Consequence, stated rather than left to be discovered: a file in one of those four grounds, but
#: has no function or class for the depth gate to stand on, so it cannot reach `audited_deep`. That
#: is a real limit on what "multi-language grounding" buys a consumer today.
#:
#: Filed as **DF-10-2-A**, NOT fixed here: story 10.2/AC3 is fenced to a *grammar-resolution* fix,
#: and widening the definition vocabulary changes which files reach `audited_deep` in any polyglot
#: repository — a capability change that needs its own ACs and its own cartridges. Measured blast
#: radius on THIS repository is zero (`git ls-files` matches 0 `.c/.h/.cpp/.hpp/.cc/.cxx/.hh/.rb/.rs`
#: files). Pinned in BOTH directions below so it can neither silently regress nor silently improve
#: while the specification and the README keep claiming the version of it that was measured.
_YIELDS_DEFINITIONS: dict[str, bool] = {
    "sample.c": False,
    "sample.cpp": False,
    "sample.go": True,
    "sample.java": True,
    "sample.js": True,
    "sample.php": True,
    "sample.py": True,
    "sample.rb": False,
    "sample.rs": False,
    "sample.ts": True,
    "sample.tsx": True,
}


@pytest.mark.parametrize("filename", sorted(_GROUNDING_FIXTURES))
def test_structure_extraction_breadth_is_pinned_not_assumed(filename: str, tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-003-09 — Story 10.2/AC3 + DF-10-2-A: grounding ≠ structure, measured.

    `-08` proves every claimed language GROUNDS. This proves what that does and does not buy, in
    both directions, so the honest boundary the README and FR7 state is a measured fact rather than
    a hopeful one. The near-miss this file already documents (`-02` asserting the weaker property
    where the stronger was assumed) is exactly what an unpinned gap looks like on the way in.

    A language moving from False to True here is GOOD NEWS that must still be deliberate: it widens
    what reaches `audited_deep`, which moves verdicts, and it makes DF-10-2-A partly closable.
    """
    language = language_for_suffix(Path(filename).suffix)
    assert language is not None
    skip_reason = _grounding_skip_reason(language)
    if skip_reason is not None:
        pytest.skip(skip_reason)

    assert set(_YIELDS_DEFINITIONS) == set(_GROUNDING_FIXTURES), (
        "the structure-extraction pin and the grounding matrix have drifted apart; every fixture "
        "must be pinned in this table or the enumeration proves nothing"
    )

    root = tmp_path / "structure"
    root.mkdir()
    (root / filename).write_text(_GROUNDING_FIXTURES[filename], encoding="utf-8")
    entry = build_ast_index(root, (filename,)).entries[0]

    expected = _YIELDS_DEFINITIONS[filename]
    actual = bool(entry.definitions)
    if expected:
        assert actual, (
            f"{language} ({filename}) REGRESSED: it parsed cleanly but extracted no definition, so "
            "no file in this language can reach `audited_deep` any more. Check "
            "ast_index._DEF_KIND_BY_NODE and _node_name against this grammar's node vocabulary."
        )
    else:
        assert not actual, (
            f"{language} ({filename}) now extracts definitions {[d.name for d in entry.definitions]} "
            "where DF-10-2-A recorded none. This is an IMPROVEMENT and must be adopted "
            "deliberately: flip this entry to True, re-measure the dogfood verdict (more files can "
            "now reach `audited_deep`), and close or narrow DF-10-2-A in deferred-work.md."
        )
