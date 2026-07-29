"""Repo intake @ pinned commit — drift refusal + typed errors (Story 1.4, AC1/AC6).

Verification area ArgusAgent-INTAKE (TC-ArgusAgent-INTAKE-001-NN). FR1: load @ pin, refuse a
drifted working tree; a missing path / bad commit / dirty-vs-pin → typed
``RepoIntakeError``. Uses a throwaway git repo under ``tmp_path``.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from argus.intake.repo_loader import (
    RepoIntake,
    RepoIntakeError,
    load_repo_at_commit,
)

_GIT = shutil.which("git")
pytestmark = pytest.mark.skipif(_GIT is None, reason="git binary not available")


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def _init_repo(repo: Path) -> str:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "Tester")
    (repo / "mod.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    (repo / "pkg.py").write_text("x = 2\n", encoding="utf-8")
    (repo / "README.md").write_text("docs\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "initial")
    return _git(repo, "rev-parse", "HEAD")


def test_load_at_pin_returns_frozen_intake_with_relative_python_sources(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-70 — clean on-pin load returns relative Python sources."""
    repo = tmp_path / "repo"
    sha = _init_repo(repo)

    intake = load_repo_at_commit(repo, sha)

    assert isinstance(intake, RepoIntake)
    assert intake.commit_sha == sha
    # Only Python sources, repo-root-relative POSIX, sorted; no README, no absolute path.
    assert intake.source_files == ("mod.py", "pkg.py")
    assert all("\\" not in p and not Path(p).is_absolute() for p in intake.source_files)
    # frozen
    with pytest.raises(Exception):
        intake.commit_sha = "x"  # type: ignore[misc]


def test_short_sha_and_head_resolve(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-71 — a short SHA and the ref 'HEAD' both resolve to the pin."""
    repo = tmp_path / "repo"
    sha = _init_repo(repo)

    by_short = load_repo_at_commit(repo, sha[:8])
    by_ref = load_repo_at_commit(repo, "HEAD")

    assert by_short.commit_sha == sha
    assert by_ref.commit_sha == sha


def test_dirty_working_tree_refuses(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-72 — uncommitted drift is refused with RepoIntakeError (FR1)."""
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    (repo / "mod.py").write_text("def f():\n    return 999\n", encoding="utf-8")

    with pytest.raises(RepoIntakeError, match="drift"):
        load_repo_at_commit(repo, sha)


def test_untracked_file_is_drift(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-73 — an untracked file counts as drift (porcelain non-empty)."""
    repo = tmp_path / "repo"
    sha = _init_repo(repo)
    (repo / "new.py").write_text("y = 3\n", encoding="utf-8")

    with pytest.raises(RepoIntakeError, match="drift"):
        load_repo_at_commit(repo, sha)


def test_head_not_at_pin_refuses(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-74 — HEAD pointing at a different commit than the pin is drift."""
    repo = tmp_path / "repo"
    first = _init_repo(repo)
    (repo / "mod.py").write_text("def f():\n    return 2\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "second")

    # HEAD is now the second commit; pinning the FIRST must refuse (HEAD != pin).
    with pytest.raises(RepoIntakeError, match="drift"):
        load_repo_at_commit(repo, first)


def test_missing_path_raises_typed(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-75 — a non-existent repo path → typed RepoIntakeError."""
    with pytest.raises(RepoIntakeError, match="does not exist"):
        load_repo_at_commit(tmp_path / "nope", "HEAD")


def test_unresolvable_commit_raises_typed(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-76 — a bogus commit ref → typed RepoIntakeError (not a bare crash)."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    with pytest.raises(RepoIntakeError):
        load_repo_at_commit(repo, "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef")


def test_non_git_directory_raises_typed(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-77 — a plain directory (not a git repo) → typed RepoIntakeError."""
    plain = tmp_path / "plain"
    plain.mkdir()
    (plain / "a.py").write_text("z = 1\n", encoding="utf-8")
    with pytest.raises(RepoIntakeError):
        load_repo_at_commit(plain, "HEAD")


def test_unicode_named_python_source_is_included_unmangled(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-78 — a non-ASCII-named .py file is enumerated with its real path.

    Regression for the review-iteration-1 Medium defect: git's default
    ``core.quotepath=true`` makes ``git ls-files`` emit a non-ASCII path as a
    double-quoted, octal-escaped token (e.g. ``"caf\\303\\251.py"``), whose
    ``Path(...).suffix`` is ``.py"`` — silently dropping the file from
    ``source_files`` (AC1 audit-input completeness / AR11). The enumeration must
    return the real relative POSIX path ``café.py`` unmangled and present.
    """
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "Tester")
    (repo / "café.py").write_text("def g():\n    return 1\n", encoding="utf-8")
    (repo / "naïve_dir").mkdir()
    (repo / "naïve_dir" / "résumé.py").write_text("h = 2\n", encoding="utf-8")
    (repo / "plain.py").write_text("x = 0\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "initial")
    sha = _git(repo, "rev-parse", "HEAD")

    intake = load_repo_at_commit(repo, sha)

    assert intake.source_files == ("café.py", "naïve_dir/résumé.py", "plain.py")
    # No double-quote / octal-escape mangling leaked into any path.
    assert all('"' not in p and "\\" not in p for p in intake.source_files)
