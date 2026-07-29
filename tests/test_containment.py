"""Containment property test for the ``.argus/`` store (the architecture-named gate).

Verification area ArgusAgent-STORE (TC-ArgusAgent-STORE-001-60..69). Drivers: ArgusAgent-NFR-S5
(every FS write containment-checked — ``Path.resolve()`` + ``is_relative_to``,
never ``str.startswith``; an escape raises BEFORE any FS mutation), AR7 (REUSE the
Minions ``WorkspaceContainmentError``), AR11 (the fixed ``.argus/`` tree).

Every escape vector in AC1 must raise ``WorkspaceContainmentError`` AND leave the
escaping path uncreated; a legitimately-confined path must write + return a
``.argus/``-root-relative POSIX locator. The sibling-prefix case (``.argus-evil`` vs
``.argus``) is the explicit ``str.startswith`` regression guard.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from argus.store.envelope import EnvelopeWriter
from argus.store.paths import ApaaStorePaths, WorkspaceContainmentError
from argus.store.writer import ApaaStoreWriter
from argus.shared.workspace_containment import (
    WorkspaceContainmentError as MinionsWorkspaceContainmentError,
)


def test_reuses_minions_containment_error_no_fork() -> None:
    """AC2 — the typed error is the Minions one (reused by import, not forked)."""
    assert WorkspaceContainmentError is MinionsWorkspaceContainmentError
    assert issubclass(WorkspaceContainmentError, ValueError)


# ── Escape vectors (AC1). Each must raise BEFORE any FS mutation. ──

_ESCAPE_VECTORS = [
    pytest.param("../escape.json", id="parent-traversal"),
    pytest.param("state/../../escape.json", id="deep-traversal"),
    pytest.param("..", id="dotdot-only"),
    pytest.param("/etc/passwd", id="absolute-posix"),
    pytest.param("C:\\Windows\\system32\\evil.json", id="drive-letter-absolute"),
    pytest.param("..\\..\\escape.json", id="windows-backslash-traversal"),
]


@pytest.mark.parametrize("relative_path", _ESCAPE_VECTORS)
def test_escape_vector_raises_before_any_write(tmp_path: Path, relative_path: str) -> None:
    """AC1 — every escape vector raises WorkspaceContainmentError, no FS mutation."""
    paths = ApaaStorePaths(tmp_path)
    before = _snapshot(tmp_path)

    with pytest.raises(WorkspaceContainmentError):
        paths.resolve(relative_path)
    with pytest.raises(WorkspaceContainmentError):
        paths.ensure_parent(relative_path)

    after = _snapshot(tmp_path)
    assert after == before, f"escape '{relative_path}' mutated the filesystem"


def test_writer_escape_vector_writes_nothing(tmp_path: Path) -> None:
    """AC1 — the writer surfaces the containment error before writing bytes."""
    writer = ApaaStoreWriter(tmp_path)
    env = EnvelopeWriter.build({"k": "v"}, schema_version="1", producer="test")
    before = _snapshot(tmp_path)
    # ``subdir`` carrying a traversal escapes via the relative path the writer builds.
    with pytest.raises(WorkspaceContainmentError):
        writer.write_envelope("../evil", env)
    assert _snapshot(tmp_path) == before


def test_sibling_prefix_is_not_contained(tmp_path: Path) -> None:
    """AC1/AC9 — ``.argus-evil`` must NOT be treated as inside ``.argus`` (startswith guard).

    A naive ``str.startswith(str(argus_root))`` check would accept the sibling dir
    ``<repo>/.argus-evil`` because its string begins with ``<repo>/.argus``. The
    ``is_relative_to`` check must reject it.
    """
    paths = ApaaStorePaths(tmp_path)
    argus_root = str(paths.argus_root)
    sibling = argus_root + "-evil"
    # Prefix-string relationship holds (the trap a startswith check would fall into)…
    assert sibling.startswith(argus_root)
    # …but real containment rejects it.
    assert not Path(sibling).is_relative_to(paths.argus_root)

    # And a relative path that resolves into the sibling escapes.
    with pytest.raises(WorkspaceContainmentError):
        paths.resolve("../.argus-evil/x.json")


def test_symlink_escape_raises_before_write(tmp_path: Path) -> None:
    """AC1 — a symlink whose target escapes the ``.argus/`` root is rejected."""
    paths = ApaaStorePaths(tmp_path)
    paths.ensure_tree()
    outside = tmp_path / "outside"
    outside.mkdir()
    link = paths.argus_root / "state" / "link"
    try:
        os.symlink(outside, link, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted on this platform/run")

    before = _snapshot(tmp_path)
    with pytest.raises(WorkspaceContainmentError):
        # state/link -> outside/, so state/link/escape.json resolves outside .argus/
        paths.ensure_parent("state/link/escape.json")
    # the escape produced no new file under outside/
    assert not (outside / "escape.json").exists()
    assert _snapshot(tmp_path) == before


# ── The confined happy path (AC1/AC3) ──

def test_confined_path_writes_and_returns_relative_locator(tmp_path: Path) -> None:
    """AC1/AC3 — a legitimately-confined path writes + returns a relative POSIX locator."""
    paths = ApaaStorePaths(tmp_path)
    paths.ensure_tree()
    target = paths.ensure_parent("state/abc.json")
    assert target.is_relative_to(paths.argus_root)
    locator = paths.to_locator("state/abc.json")
    assert locator == "state/abc.json"
    assert not Path(locator).is_absolute()


def test_ensure_tree_creates_exactly_the_fixed_subdirs(tmp_path: Path) -> None:
    """AC3 — the fixed tree is EXACTLY state/ assignments/ findings/ decisions/ cache/."""
    paths = ApaaStorePaths(tmp_path)
    paths.ensure_tree()
    children = sorted(p.name for p in paths.argus_root.iterdir() if p.is_dir())
    assert children == ["assignments", "cache", "decisions", "findings", "state"]


from argus.shared.workspace_containment import (
    WorkspaceArtifactWriter,
    WorkspaceContainmentError as MinionsWorkspaceContainmentError,
)


def test_workspace_artifact_writer_materialize_and_containment(tmp_path: Path) -> None:
    """Test WorkspaceArtifactWriter enabled property, materialization, and traversal rejection."""
    disabled_writer = WorkspaceArtifactWriter("")
    assert not disabled_writer.enabled
    with pytest.raises(WorkspaceContainmentError, match="disabled"):
        disabled_writer.materialize("run-1", "file.py", "code")

    writer = WorkspaceArtifactWriter(str(tmp_path))
    assert writer.enabled

    locator = writer.materialize("run-1", "src/mod.py", "print('hello')")
    assert locator == "run-1/src/mod.py"
    written_file = tmp_path / "run-1" / "src" / "mod.py"
    assert written_file.exists()
    assert written_file.read_text(encoding="utf-8") == "print('hello')"

    with pytest.raises(WorkspaceContainmentError, match="escapes"):
        writer.materialize("run-1", "../../../escape.txt", "evil")


def _snapshot(root: Path) -> set[str]:
    """All paths under *root* (relative POSIX) — for asserting no FS mutation."""
    if not root.exists():
        return set()
    return {p.relative_to(root).as_posix() for p in root.rglob("*")}

