"""Secret scan suppression engine and test mock filtering for ArgusAgent.

Implements industry-standard multi-layer secret suppression:
1. Public Sentinel Allowlisting (e.g. AWS documentation test keys, RFC test domains).
2. Inline Annotations (# argus:ignore, # noqa: secret-scan).
3. Test & Fixture Path Glob Scoping (e.g. tests/, fixtures/, mock_*.py).
4. Live-Key Safeguard: High-confidence live production key signatures override
   folder glob exemptions unless annotated with an explicit inline line comment.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Sequence

# `fnmatchcase`, never the module-level `fnmatch`. `fnmatch` compares through
# `os.path.normcase`, which lower-cases on Windows and is identity on POSIX. Every
# match here decides whether a detected secret is SUPPRESSED, so a host-dependent
# answer means the same repository at the same commit reports a credential on Linux
# and hides it on Windows — a security false negative produced by the operating
# system the audit happened to run on. NFR-P1 (byte-identical across hosts) forbids
# it, and `ledger/critical_subsystems._matches_exclusion` already documents the rule.
# Case-sensitive also errs toward REPORTING a secret rather than suppressing it.
from fnmatch import fnmatchcase

# Known public documentation / test sentinels (RFC 2606 & Cloud provider docs)
KNOWN_PUBLIC_SENTINELS: tuple[str, ...] = (
    "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "0123456789abcdef0123456789abcdef01234567",
    "xoxb-123456789012-1234567890123-example",
    "example.com",
    "example.org",
    "example.net",
    "127.0.0.1",
    "localhost",
)


# High-confidence live production key patterns that bypass path-glob exemptions
LIVE_KEY_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9_]{36}"),
    re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC|PGP) PRIVATE KEY-----"),
    re.compile(r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32}"),
)

# Test / fixture path patterns
DEFAULT_TEST_PATH_PATTERNS: tuple[str, ...] = (
    "tests/**",
    "**/test_*.py",
    "**/*_test.py",
    "**/fixtures/**",
    "**/cartridges/**",
    "**/mock_*.py",
)

INLINE_ANNOTATION_PATTERN = re.compile(
    r"#\s*(?:argus:ignore|noqa:\s*(?:secret-scan|hardcoded_secret|security))",
    re.IGNORECASE,
)


class SecretSuppressionEngine:
    """Evaluates candidates for secret scan suppression & mock filtering."""

    @staticmethod
    def is_public_sentinel(snippet: str) -> bool:
        """Check if *snippet* matches a known public documentation/test sentinel."""
        snippet_clean = snippet.strip()
        for sentinel in KNOWN_PUBLIC_SENTINELS:
            if sentinel in snippet_clean:
                return True
        return False

    @staticmethod
    def is_live_production_key(snippet: str) -> bool:
        """Check if *snippet* matches a high-confidence live key format.

        Excludes known public sentinels (e.g. AKIAIOSFODNN7EXAMPLE).
        """
        for sentinel in KNOWN_PUBLIC_SENTINELS:
            if sentinel in snippet:
                return False
        for pattern in LIVE_KEY_PATTERNS:
            if pattern.search(snippet):
                return True
        return False

    @staticmethod
    def has_inline_annotation(line_content: str | None) -> bool:
        """Check if the code line contains an explicit inline ignore annotation."""
        if not line_content:
            return False
        return bool(INLINE_ANNOTATION_PATTERN.search(line_content))

    @staticmethod
    def is_test_fixture_path(
        file_path: str, custom_ignore_paths: Sequence[str] = ()
    ) -> bool:
        """Check if *file_path* matches standard test fixture patterns or custom paths."""
        posix_path = file_path.replace("\\", "/")
        patterns = list(DEFAULT_TEST_PATH_PATTERNS) + list(custom_ignore_paths)
        for pat in patterns:
            pat_posix = pat.replace("\\", "/")
            if fnmatchcase(posix_path, pat_posix) or fnmatchcase(
                Path(posix_path).name, pat_posix
            ):
                return True
        return False

    @classmethod
    def evaluate_suppression(
        cls,
        file_path: str,
        snippet: str,
        line_content: str | None = None,
        ignore_paths: Sequence[str] = (),
        ignore_patterns: Sequence[str] = (),
    ) -> tuple[bool, str | None]:
        """Evaluate if a secret candidate should be suppressed.

        Returns:
            (is_suppressed, suppression_reason)
        """
        # 1. Inline annotation check (highest precedence override)
        if cls.has_inline_annotation(line_content):
            return True, "inline_annotation"

        # 2. Known public test sentinel check
        if cls.is_public_sentinel(snippet):
            return True, "known_sentinel"

        # 3. Custom pattern match check
        for pat in ignore_patterns:
            if pat in snippet or fnmatchcase(snippet, pat):
                return True, "custom_ignore_pattern"

        # 4. Live production key check (bypasses path-glob exemptions)
        if cls.is_live_production_key(snippet):
            return False, None

        # 5. Test fixture path glob check
        if cls.is_test_fixture_path(file_path, ignore_paths):
            return True, "test_fixture_glob"

        return False, None
