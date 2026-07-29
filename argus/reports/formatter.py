"""PURE markdown formatting & secret masking utilities for Argus reports (AR8 / NFR-S1).

Provides pure helper functions to format markdown summary tables, sanitize secret
findings, generate locator links, and render metric indicators without side-effects.
"""

from __future__ import annotations

import re

__all__ = [
    "mask_secret",
    "format_locator_link",
    "render_markdown_table",
    "render_callout",
]


def mask_secret(value: str) -> str:
    """Mask sensitive string bytes to prevent credential leakage in reports (NFR-S1).

    Leaves up to the first 4 characters visible if string length >= 8, otherwise
    masks the entire value with asterisks.
    """
    if not value:
        return ""
    val = value.strip()
    if len(val) <= 6:
        return "*" * len(val)
    visible_prefix = val[:4]
    return f"{visible_prefix}{'*' * (len(val) - 4)}"


def format_locator_link(file_path: str, line: int | None = None) -> str:
    """Format a secret-safe, POSIX repo-relative locator code snippet/link."""
    posix_path = file_path.replace("\\", "/")
    if line is not None and line > 0:
        return f"`{posix_path}:{line}`"
    return f"`{posix_path}`"


def render_markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    """Render a GitHub-flavored Markdown table from headers and row data."""
    if not headers:
        return ""

    lines: list[str] = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")

    for row in rows:
        # Fill missing cells if row is shorter than headers
        padded_row = row + [""] * (len(headers) - len(row))
        sanitized_cells = [cell.replace("\n", " ").replace("|", "\\|") for cell in padded_row[:len(headers)]]
        lines.append("| " + " | ".join(sanitized_cells) + " |")

    return "\n".join(lines)


def render_callout(kind: str, message: str) -> str:
    """Render a GitHub-style alert callout block (NOTE, TIP, IMPORTANT, WARNING, CAUTION)."""
    valid_kind = kind.upper() if kind.upper() in ("NOTE", "TIP", "IMPORTANT", "WARNING", "CAUTION") else "NOTE"
    bullet_lines = [f"> {line}" for line in message.strip().splitlines()]
    return f"> [!{valid_kind}]\n" + "\n".join(bullet_lines)
