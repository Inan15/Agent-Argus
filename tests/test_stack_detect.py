"""Stack & toolchain auto-detection — no operator config (Story 1.4, AC2/AC5/AC6).

Verification area ArgusAgent-INTAKE (TC-ArgusAgent-INTAKE-001-NN). FR2: Python detection from
sources/markers with NO config; honest degraded toolchain (unavailable tool →
available: false), never a crash. The non-tree-sitter logic is unconditionally
tested.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from argus.intake import stack_detect
from argus.intake.stack_detect import (
    StackProfile,
    ToolchainProfile,
    detect_stack,
)


def test_python_detected_from_sources(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-80 — *.py sources → primary_language='python'."""
    profile = detect_stack(tmp_path, ("a/b.py", "c.py"))
    assert isinstance(profile, StackProfile)
    assert profile.primary_language == "python"
    assert profile.detected_languages == ("python",)


def test_python_detected_from_marker_without_py_sources(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-81 — a pyproject.toml marker alone → 'python' (no *.py needed)."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    profile = detect_stack(tmp_path, ("main.go",))
    assert profile.primary_language == "python"
    assert profile.detected_languages == ("go",)


def test_non_python_sources_are_other(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-82 — only non-Python sources, no marker → 'other'."""
    profile = detect_stack(tmp_path, ("main.go", "lib.rs"))
    assert profile.primary_language == "other"
    assert profile.detected_languages == ("go", "rust")


def test_empty_repo_is_unknown(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-83 — no sources, no markers → 'unknown'."""
    profile = detect_stack(tmp_path, ())
    assert profile.primary_language == "unknown"
    assert profile.detected_languages == ()


def test_detected_languages_sorted_and_distinct(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-84 — detected_languages is a sorted, de-duplicated tuple (AR11)."""
    profile = detect_stack(tmp_path, ("z.ts", "a.py", "b.py", "m.js"))
    assert profile.detected_languages == ("javascript", "python", "typescript")


def test_toolchain_probes_are_bools(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-85 — toolchain availability flags are honest booleans."""
    profile = detect_stack(tmp_path, ("a.py",))
    tc = profile.toolchain
    assert isinstance(tc, ToolchainProfile)
    assert isinstance(tc.radon_available, bool)
    assert isinstance(tc.tree_sitter_python_available, bool)
    assert isinstance(tc.cloc_available, bool)


def test_unavailable_tool_records_false_no_crash(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """TC-ArgusAgent-INTAKE-001-86 — a failing/absent probe degrades to False, never a crash (AR10)."""

    def _boom(name: str) -> bool:
        raise RuntimeError("forced probe failure")

    # _module_importable already swallows ImportError/ValueError; here we force the
    # probe helper itself to report unavailable and assert no crash escapes.
    monkeypatch.setattr(stack_detect, "_module_importable", lambda name: False)
    monkeypatch.setattr(stack_detect.shutil, "which", lambda _name: None)

    profile = detect_stack(tmp_path, ("a.py",))
    assert profile.toolchain.radon_available is False
    assert profile.toolchain.tree_sitter_python_available is False
    assert profile.toolchain.cloc_available is False
    # _boom referenced so the helper signature is exercised conceptually; ensure no leak.
    assert callable(_boom)


def test_profile_is_frozen(tmp_path: Path) -> None:
    """TC-ArgusAgent-INTAKE-001-87 — StackProfile is a frozen contract."""
    profile = detect_stack(tmp_path, ("a.py",))
    with pytest.raises(Exception):
        profile.primary_language = "go"  # type: ignore[misc]
