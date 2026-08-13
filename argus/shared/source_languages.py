"""Single source of truth for "which file suffixes are auditable source, and in what language".

Drivers: ArgusAgent-NFR-P2 (stack-agnostic by construction), AR4 (deterministic —
a frozen mapping, no iteration-order reliance), AR8 (pure data; no I/O, no imports
beyond the stdlib).

Why this module exists
----------------------
This mapping previously existed THREE times, with three different contents:

* ``intake/repo_loader.py`` enumerated ``{.py, .pyi, .pyx}`` — Python only.
* ``intake/source_state.py`` copied that same Python-only set.
* ``index/ast_index.py`` carried the full 10-language, 20-suffix map, and
  ``intake/stack_detect.py`` carried a fourth, shorter variant.

The divergence was not cosmetic. Because ENUMERATION is upstream of everything
else, the narrowest copy won: a JavaScript or Go repository enumerated ZERO files,
so the multi-language grammars, the multi-language test-file conventions, and the
multi-language stack detection downstream were all unreachable. Argus would run to
completion on such a repository, emit ``INSUFFICIENT_COVERAGE``, and never say that
it had been unable to read a single file — a component-by-component "multi-language
support" claim that was false end-to-end.

One definition, imported everywhere, is the fix. A language is added HERE and every
stage sees it at once.

Note the boundary this module does NOT cross: being enumerable is not the same as
being deeply auditable. A suffix listed here is a file Argus will READ and grade; it
reaches ``audited_deep`` only if a tree-sitter grammar for its language is installed
and it parses. Absent that, ``ast_index`` degrades it honestly to
``ast_eligible=False`` — recorded as shallow coverage rather than silently dropped,
which is the whole point of enumerating it in the first place.
"""

from __future__ import annotations

from typing import Iterable, Sequence
from pathlib import Path

__all__ = [
    "LANGUAGE_BY_SUFFIX",
    "AUDITABLE_SUFFIXES",
    "PYTHON_SUFFIXES",
    "language_for_suffix",
    "derive_non_auditable_suffixes",
    "format_ingestion_boundary",
]

# Suffix → language token. Lower-case suffixes including the leading dot.
LANGUAGE_BY_SUFFIX: dict[str, str] = {
    # Python
    ".py": "python",
    ".pyi": "python",
    ".pyx": "python",
    # JavaScript / TypeScript
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    # Go
    ".go": "go",
    # Rust
    ".rs": "rust",
    # JVM
    ".java": "java",
    # C / C++
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hh": "cpp",
    # Ruby
    ".rb": "ruby",
    # PHP
    ".php": "php",
}

# The enumerable set — what intake will pick up off disk or out of `git ls-files`.
AUDITABLE_SUFFIXES: frozenset[str] = frozenset(LANGUAGE_BY_SUFFIX)

# Python retains a distinguished role: it is the language with full AST grounding
# (FR7), so several stages still branch on it explicitly.
PYTHON_SUFFIXES: frozenset[str] = frozenset(
    suffix for suffix, language in LANGUAGE_BY_SUFFIX.items() if language == "python"
)


def language_for_suffix(suffix: str) -> str | None:
    """Return the language token for *suffix*, or ``None`` if not auditable (PURE)."""
    return LANGUAGE_BY_SUFFIX.get(suffix.lower())


def derive_non_auditable_suffixes(
    file_paths: Iterable[str | Path] | None = None,
) -> tuple[str, ...]:
    """Derive non-auditable file extension classes present in a file collection (PURE).

    Compares suffixes against AUDITABLE_SUFFIXES. Suffixes not in AUDITABLE_SUFFIXES
    and with a non-empty extension (e.g. '.yml', '.md', '.toml') are collected and sorted.
    If *file_paths* is None or empty, returns a default representative set of non-auditable
    file classes present in project repositories: ('.md', '.toml', '.yml').
    """
    if not file_paths:
        return (".md", ".toml", ".yml")

    found: set[str] = set()
    for p in file_paths:
        s = Path(p).suffix.lower()
        if s and s not in AUDITABLE_SUFFIXES:
            found.add(s)

    if not found:
        return (".md", ".toml", ".yml")
    return tuple(sorted(found))


def format_ingestion_boundary(
    non_auditable_suffixes: Iterable[str] | None = None,
    *,
    held_out_count: int = 0,
    assessed_count: int = 0,
) -> str:
    """Format the 3-population ingestion boundary disclosure line (PURE).

    Explicitly distinguishes three populations by construction (AC2 / FR37):
    1. Never ingested: File suffixes outside AUDITABLE_SUFFIXES (e.g. .yml, .md, .toml).
    2. Ingested but held out: Source files with auditable suffixes that were held out.
    3. Assessed: Source files evaluated for coverage and defects.
    """
    suffixes = tuple(sorted(set(non_auditable_suffixes))) if non_auditable_suffixes else (".md", ".toml", ".yml")
    suffixes_str = ", ".join(suffixes)
    return (
        f"Ingestion boundary: 3 populations — "
        f"(1) Never ingested: file suffixes outside AUDITABLE_SUFFIXES ({suffixes_str}); "
        f"(2) Ingested but held out: {held_out_count}; "
        f"(3) Assessed: {assessed_count}"
    )

