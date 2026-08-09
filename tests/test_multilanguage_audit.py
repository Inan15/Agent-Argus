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
