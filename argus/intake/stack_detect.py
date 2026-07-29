"""IMPURE stack / toolchain auto-detection — no operator configuration (FR2).

Drivers: ArgusAgent-FR-2 (stack & toolchain auto-detection, NO operator config),
ArgusAgent-NFR-P2 (stack-agnostic by construction — V1 deep AST is Python; the
language conditional lives ONLY in ``intake``/``index``, never in
``ledger``/``verdict``), AR1 (the sanctioned toolchain — ``radon`` /
``tree-sitter-python`` availability probed here; ``cloc`` is OPTIONAL/best-effort),
AR8 (impure shell; ``StackProfile`` is a frozen pure contract), AR10 (a tool
that is unavailable / errors during probing is recorded ``available: false`` —
a degraded but honest profile, never an uncaught crash).

Detection contract
------------------
Auto-detection only — no config file, no operator flag. Python is detected from
two independent signals, EITHER of which is sufficient:

- ``*.py`` / ``*.pyi`` / ``*.pyx`` source files in the discovered set, and/or
- packaging markers at the repo root (``pyproject.toml`` / ``setup.py`` /
  ``setup.cfg`` / ``requirements.txt``).

``primary_language`` is ``"python"`` when any Python signal is present, ``"other"``
when source files exist but none are Python, and ``"unknown"`` when no source
files / markers are found at all.

Toolchain probing
-----------------
- ``radon_available`` — importability of the ``radon`` package (zero-token metric
  availability, AR1). A probe failure → ``False`` (degraded, honest).
- ``tree_sitter_python_available`` — importability of ``tree_sitter`` +
  ``tree_sitter_python`` (the AST-index grammar, AR1).
- ``cloc_available`` — OPTIONAL system binary probed via ``shutil.which``; its
  absence is recorded, never fatal (AR10). The full tool-failure-AS-FINDING is
  Story 2.6 — this story produces the honest availability DATA only.
"""

from __future__ import annotations

import importlib.util
import shutil
from collections.abc import Iterable, Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "ToolchainProfile",
    "StackProfile",
    "detect_stack",
]

_PYTHON_SUFFIXES: frozenset[str] = frozenset({".py", ".pyi", ".pyx"})

_PYTHON_MARKERS: tuple[str, ...] = (
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
)

# file suffix -> language token, for the detected-languages set (additive).
_SUFFIX_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".pyx": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
}


class ToolchainProfile(BaseModel):
    """Frozen availability map for the probed toolchain (FR2 / AR1 / AR10).

    Each flag is an honest probe outcome: a tool that is unavailable / errors
    during probing is ``False`` (degraded but honest), never a crash. ``cloc`` is
    OPTIONAL/best-effort — its absence is recorded, not fatal.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    radon_available: bool = Field(..., description="`radon` import probe succeeded (zero-token metrics).")
    tree_sitter_python_available: bool = Field(
        ..., description="`tree_sitter` + `tree_sitter_python` import probe succeeded (AST grammar)."
    )
    cloc_available: bool = Field(
        default=False, description="OPTIONAL `cloc` binary present on PATH (best-effort; absence non-fatal)."
    )


class StackProfile(BaseModel):
    """Frozen stack/toolchain detection result (FR2 / AR8 pure contract).

    ``frozen=True, extra="forbid"`` (Story 1.1/1.2 precedent). Construction-pure
    (no clock / uuid / random / float). ``detected_languages`` is a SORTED tuple
    (not a ``set`` — set iteration order is non-deterministic, AR4/AR11).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(default="1", description="StackProfile schema version (additive-only).")
    primary_language: str = Field(
        ..., description="'python' | 'other' | 'unknown' — V1 cares whether this is a Python codebase."
    )
    detected_languages: tuple[str, ...] = Field(
        ..., description="Sorted distinct language tokens inferred from source suffixes (AR11)."
    )
    toolchain: ToolchainProfile = Field(..., description="Honest toolchain availability map.")


def _module_importable(name: str) -> bool:
    """True iff *name* can be located by the import system (no actual import / side effect).

    Uses ``importlib.util.find_spec`` so probing never runs module top-level code
    and any probe failure degrades to ``False`` (AR10) — never raises.
    """
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def _probe_toolchain() -> ToolchainProfile:
    radon_available = _module_importable("radon")
    tree_sitter_python_available = _module_importable("tree_sitter") and _module_importable(
        "tree_sitter_python"
    )
    cloc_available = shutil.which("cloc") is not None
    return ToolchainProfile(
        radon_available=radon_available,
        tree_sitter_python_available=tree_sitter_python_available,
        cloc_available=cloc_available,
    )


def _languages_for(source_files: Iterable[str]) -> tuple[str, ...]:
    langs: set[str] = set()
    for rel in source_files:
        lang = _SUFFIX_LANGUAGE.get(Path(rel).suffix)
        if lang is not None:
            langs.add(lang)
    return tuple(sorted(langs))


def _has_python_marker(repo_root: Path) -> bool:
    return any((repo_root / marker).is_file() for marker in _PYTHON_MARKERS)


def detect_stack(repo_root: str | Path, source_files: Sequence[str]) -> StackProfile:
    """Auto-detect the stack + toolchain for a loaded repo (FR2 — no operator config).

    *source_files* is the repo-root-relative POSIX set from
    :class:`~argus.intake.repo_loader.RepoIntake`. *repo_root* is read
    ONLY to probe packaging markers (the impure shell); nothing absolute is
    persisted (NFR-S1). Returns a frozen :class:`StackProfile`; a tool probe that
    fails degrades to ``available: false`` (AR10), never an uncaught crash.
    """
    root = Path(repo_root)
    detected_languages = _languages_for(source_files)
    has_python_source = any(Path(rel).suffix in _PYTHON_SUFFIXES for rel in source_files)
    has_python_marker = _has_python_marker(root)

    if has_python_source or has_python_marker:
        primary_language = "python"
    elif source_files:
        primary_language = "other"
    else:
        primary_language = "unknown"

    return StackProfile(
        primary_language=primary_language,
        detected_languages=detected_languages,
        toolchain=_probe_toolchain(),
    )
