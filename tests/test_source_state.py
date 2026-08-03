"""Source-state resolution + role-based ignore rules (non-git / dirty intake).

Verification area ArgusAgent-INTAKE (TC-ArgusAgent-INTAKE-002-NN).

Two things are being protected here, and the second matters more:

1. **Reach.** ``argus audit .`` must work on a directory that was never
   ``git init``-ed and on a tree that is mid-edit. Refusing to run produces no
   audit, which protects nobody.
2. **Not over-excluding.** A walk that drops real application code is far worse
   than one that includes some build output: the tool would assure a repository it
   never looked at. Hence the Tier-1/Tier-2 split — ambiguous directory names like
   ``build``/``dist``/``target`` are only excluded when an ecosystem marker
   corroborates the role, and component matching never fires on a substring.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from argus.intake.ignore_rules import (
    IgnoreReason,
    classify_path,
    corroborated_tier2_components,
    gitignore_matches,
    parse_gitignore,
)
from argus.intake.repo_loader import RepoIntakeError
from argus.intake.source_state import (
    SourceStateError,
    SourceStateKind,
    resolve_source_state,
)


def _make(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(body, encoding="utf-8")
    return root


_TYPICAL = {
    "app/main.py": "def main():\n    return 1\n",
    "app/util.py": "def helper():\n    return 2\n",
    "tests/test_main.py": "def test_main():\n    assert True\n",
    "node_modules/left-pad/index.py": "x = 1\n",
    ".venv/lib/site-packages/requests/api.py": "y = 2\n",
    "app/__pycache__/main.cpython-311.py": "z = 3\n",
}


# ─────────────────────────────────────────────────────────────────────────────
# Not over-excluding — the property that protects the audit's truthfulness
# ─────────────────────────────────────────────────────────────────────────────


def test_component_matching_never_fires_on_a_substring() -> None:
    """TC-ArgusAgent-INTAKE-002-01 — `node_modules_helper.py` is application code."""
    assert classify_path("src/node_modules_helper.py").ignored is False
    assert classify_path("app/distributor.py").ignored is False
    assert classify_path("lib/building/blocks.py").ignored is False
    # …while the real directory is caught.
    assert classify_path("web/node_modules/left-pad/index.py").ignored is True


def test_a_file_named_like_a_build_dir_is_still_source() -> None:
    """TC-ArgusAgent-INTAKE-002-02 — only DIRECTORY components are classified."""
    assert classify_path("app/build.py").ignored is False
    assert classify_path("app/dist.py").ignored is False


def test_tier2_is_inert_without_corroboration() -> None:
    """TC-ArgusAgent-INTAKE-002-03 — an ambiguous name alone is not evidence.

    A `build/` directory in a repo with no build system is far more likely to be
    someone's package than compiler output. Keeping it costs coverage percentage
    points; dropping it would hide code from the audit entirely.
    """
    assert classify_path("build/generated.py", tier2_enabled={}).ignored is False
    assert classify_path("target/x.py", tier2_enabled={}).ignored is False


def test_tier2_fires_once_an_ecosystem_marker_corroborates() -> None:
    """TC-ArgusAgent-INTAKE-002-04 — name + independent structural fact."""
    enabled = corroborated_tier2_components(frozenset({"Cargo.toml"}))
    assert "target" in enabled
    assert classify_path("target/debug/x.py", tier2_enabled=enabled).ignored is True

    none_enabled = corroborated_tier2_components(frozenset({"README.md"}))
    assert "target" not in none_enabled


def test_dotnet_markers_are_matched_by_suffix() -> None:
    """TC-ArgusAgent-INTAKE-002-05 — a .csproj has a project-specific NAME."""
    enabled = corroborated_tier2_components(frozenset({"MyApp.csproj"}))
    assert enabled.get("obj") == IgnoreReason.BUILD_OUTPUT
    assert "bin" in enabled


# ─────────────────────────────────────────────────────────────────────────────
# Tier 1 + .gitignore
# ─────────────────────────────────────────────────────────────────────────────


def test_tier1_covers_the_major_ecosystems() -> None:
    """TC-ArgusAgent-INTAKE-002-06 — dependency/cache dirs across languages."""
    for path in (
        "node_modules/x/i.py",           # javascript
        ".venv/lib/site-packages/r.py",  # python
        "vendor/bundle/g.py",            # ruby
        "Pods/lib/a.py",                 # swift/objc
        ".gradle/caches/x.py",           # jvm
        "__pycache__/m.py",
        ".mypy_cache/x.py",
        ".git/hooks/x.py",
    ):
        assert classify_path(path).ignored is True, path


def test_gitignore_subset_parses_and_matches() -> None:
    """TC-ArgusAgent-INTAKE-002-07 — comments, anchoring, dir-only, negation."""
    patterns = parse_gitignore(
        "# comment\n\n/generated/\nsecrets.py\n*.tmp.py\n!keep.tmp.py\n"
    )
    assert gitignore_matches("generated/a.py", patterns) is True
    assert gitignore_matches("app/secrets.py", patterns) is True
    assert gitignore_matches("app/x.tmp.py", patterns) is True
    assert gitignore_matches("keep.tmp.py", patterns) is False  # negation wins (last match)
    assert gitignore_matches("app/main.py", patterns) is False


# ─────────────────────────────────────────────────────────────────────────────
# The three modes
# ─────────────────────────────────────────────────────────────────────────────


def test_directory_mode_on_a_repo_with_no_git(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-002-08 — the greenfield case: it must simply work."""
    root = _make(tmp_path / "green", _TYPICAL)

    state = resolve_source_state(root)

    assert state.kind == SourceStateKind.DIRECTORY
    assert state.identity.startswith("dir+")
    assert state.reproducible is False
    assert set(state.source_files) == {"app/main.py", "app/util.py", "tests/test_main.py"}
    assert state.excluded_by_reason[IgnoreReason.DEPENDENCIES] == 2
    assert state.excluded_by_reason[IgnoreReason.CACHE] == 1


def test_identity_is_deterministic_and_content_sensitive(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-002-09 — AR4: same bytes ⇒ same identity; a byte changes it."""
    root = _make(tmp_path / "d", _TYPICAL)

    first = resolve_source_state(root).identity
    assert resolve_source_state(root).identity == first

    (root / "app/main.py").write_text("def main():\n    return 99\n", encoding="utf-8")
    assert resolve_source_state(root).identity != first


def test_exclusions_are_counted_never_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-002-10 — an unreported exclusion is a misrepresentation."""
    root = _make(tmp_path / "d", _TYPICAL)

    state = resolve_source_state(root)

    assert state.excluded_total == 3
    assert all(reason for reason in state.excluded_by_reason)


def test_strict_refuses_without_git_and_explains_the_way_forward(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-002-11 — the release gate still exists, and is actionable."""
    root = _make(tmp_path / "d", _TYPICAL)

    with pytest.raises(SourceStateError) as exc:
        resolve_source_state(root, strict=True)

    assert "--strict" in str(exc.value)
    assert "Drop --strict" in str(exc.value)  # tells the operator how to proceed


def test_source_state_error_is_an_intake_error(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-002-12 — existing typed-error handlers keep working."""
    assert issubclass(SourceStateError, RepoIntakeError)
    with pytest.raises(RepoIntakeError):
        resolve_source_state(tmp_path / "does_not_exist")


def test_explicit_unresolvable_commit_still_raises(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-002-13 — never silently audit something else.

    Relaxing the precondition must not mean substituting a different source state
    for the one the operator named. A defaulted HEAD that does not resolve is a
    different, NORMAL case (a git repo with no commits yet).
    """
    import subprocess

    root = _make(tmp_path / "repo", _TYPICAL)
    subprocess.run(["git", "init", "-q", str(root)], check=False, capture_output=True)

    with pytest.raises(SourceStateError):
        resolve_source_state(root, commit="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")


def test_freshly_initialised_repo_with_no_commits_is_auditable(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-002-14 — `git init` with nothing committed yet is NORMAL."""
    import subprocess

    root = _make(tmp_path / "repo", _TYPICAL)
    subprocess.run(["git", "init", "-q", str(root)], check=False, capture_output=True)

    state = resolve_source_state(root)

    assert state.kind == SourceStateKind.DIRECTORY
    assert "app/main.py" in state.source_files
