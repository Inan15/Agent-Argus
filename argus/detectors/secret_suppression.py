"""Secret scan suppression engine and test mock filtering for ArgusAgent.

Implements industry-standard multi-layer secret suppression:
1. Public Sentinel Allowlisting (e.g. AWS documentation test keys, RFC test domains).
2. Inline Annotations (# argus:ignore, # noqa: secret-scan).
3. Test & Fixture Path Glob Scoping (e.g. tests/, fixtures/, mock_*.py).
4. Live-Key Safeguard: High-confidence live production key signatures override
   folder glob exemptions unless annotated with an explicit inline line comment.

THE EVALUATION ORDER IS THE SECURITY PROPERTY (Story 10.3 / AC4.1, 2026-08-10)
------------------------------------------------------------------------------
``evaluate_suppression`` used to run the CLI-supplied ``ignore_patterns`` arm
*above* the Live-Key Safeguard, and its match test is a bare substring. Measured
on 2026-08-10: ``--ignore-pattern "A"`` — one character — suppressed every live
AWS key, GitHub PAT, Slack token and ``BEGIN RSA PRIVATE KEY`` block in the
repository, while ``--ignore-path 'argus/**'`` suppressed none of them. The
docstring above promised the safeguard; the code ranked a command-line flag over
it, so the two flags were never the same risk. The order is now:

1. **inline annotation** — DELIBERATELY still on top. It is the documented,
   in-diff, reviewable override: it lands in a pull request beside the line it
   exempts, where a reviewer sees it. That is a different accountability class
   from an argv flag nobody reads afterwards.
2. **known public sentinel** — a published, non-secret value.
3. **Live-Key Safeguard** — a high-confidence live key is REPORTED. Nothing below
   this line can suppress it.
4. **operator ``--ignore-pattern``** — bounded by (3).
5. **path globs** — the built-in ``DEFAULT_TEST_PATH_PATTERNS`` and the operator's
   ``--ignore-path``, also bounded by (3).

Steps 4 and 5 return **operator-attributable** reason tokens when, and only when,
an operator-supplied rule is what caused the suppression (see
``OPERATOR_ATTRIBUTABLE_REASONS``); ``secret_scan`` turns those into a redacted,
non-blocking record so a suppression is disclosed instead of vanishing.

⛔ The bare-substring MATCHING SEMANTICS of ``--ignore-pattern`` are unchanged and
out of scope here: a short pattern is still a wide net over everything the
safeguard does not cover. That residual risk is stated in the architecture §G
threat model and filed as ``DF-10-3-C`` rather than silently redesigned.

PURE (AR8): no I/O, no clock, no logging side effect, no network.
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

# Reason tokens for a suppression an OPERATOR caused by passing a flag, as opposed to
# pre-existing blessed behaviour nobody chose per-run (Story 10.3 / AC4.2). Only these are
# recorded and disclosed: the public sentinels, the inline annotation and
# DEFAULT_TEST_PATH_PATTERNS are deliberately OUT (AC4.5) — disclosing them is a reporting
# enhancement (filed as DF-10-3-B), and folding them in here would move the finding count
# on a run that passed no flags at all.
REASON_CUSTOM_IGNORE_PATTERN = "custom_ignore_pattern"
REASON_CUSTOM_IGNORE_PATH = "custom_ignore_path"
REASON_TEST_FIXTURE_GLOB = "test_fixture_glob"

OPERATOR_ATTRIBUTABLE_REASONS: tuple[str, ...] = (
    REASON_CUSTOM_IGNORE_PATTERN,
    REASON_CUSTOM_IGNORE_PATH,
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
    def _matches_any_path_pattern(file_path: str, patterns: Sequence[str]) -> bool:
        """Whether *file_path* matches any of *patterns* (host-invariant, NFR-P1)."""
        posix_path = file_path.replace("\\", "/")
        for pat in patterns:
            pat_posix = pat.replace("\\", "/")
            if fnmatchcase(posix_path, pat_posix) or fnmatchcase(
                Path(posix_path).name, pat_posix
            ):
                return True
        return False

    @classmethod
    def is_test_fixture_path(
        cls, file_path: str, custom_ignore_paths: Sequence[str] = ()
    ) -> bool:
        """Check if *file_path* matches standard test fixture patterns or custom paths."""
        return cls._matches_any_path_pattern(
            file_path, list(DEFAULT_TEST_PATH_PATTERNS) + list(custom_ignore_paths)
        )

    @classmethod
    def path_glob_reason(
        cls, file_path: str, custom_ignore_paths: Sequence[str] = ()
    ) -> str | None:
        """Which path rule exempts *file_path* — a BUILT-IN default or the OPERATOR's own?

        Returns ``"test_fixture_glob"``, ``"custom_ignore_path"`` or ``None``.
        ``is_test_fixture_path`` merged the two sets into one undifferentiated answer, so a
        suppression could not be attributed to the operator who caused it (Story 10.3 / AC4.2).

        Attribution is CONSERVATIVE: the built-in defaults are tested FIRST, so an
        ``--ignore-path`` that merely restates a default (``--ignore-path 'tests/**'``) is not
        credited with a suppression that would have happened without it. Over-attributing a
        suppression to an operator is as dishonest as recording none.
        """
        if cls._matches_any_path_pattern(file_path, DEFAULT_TEST_PATH_PATTERNS):
            return REASON_TEST_FIXTURE_GLOB
        if cls._matches_any_path_pattern(file_path, custom_ignore_paths):
            return REASON_CUSTOM_IGNORE_PATH
        return None

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

        The ORDER below is the security property, not an implementation detail — see the
        module docstring. Nothing an operator can pass on the command line outranks the
        Live-Key Safeguard; only an inline annotation, which is reviewable in the diff, does.

        Returns:
            (is_suppressed, suppression_reason)
        """
        # 1. Inline annotation — the one deliberately preserved override (reviewable in-diff).
        if cls.has_inline_annotation(line_content):
            return True, "inline_annotation"

        # 2. Known public test sentinel — a published, non-secret value.
        if cls.is_public_sentinel(snippet):
            return True, "known_sentinel"

        # 3. LIVE-KEY SAFEGUARD. Moved ABOVE the two operator-supplied arms by Story 10.3 /
        #    AC4.1: `--ignore-pattern` matches by bare substring, so at step 3 a one-character
        #    pattern silently suppressed every live credential in the repository. A high-
        #    confidence live key is now REPORTED regardless of any flag the operator passed.
        if cls.is_live_production_key(snippet):
            return False, None

        # 4. Operator-supplied value patterns (`--ignore-pattern`), bounded by step 3.
        for pat in ignore_patterns:
            if pat in snippet or fnmatchcase(snippet, pat):
                return True, REASON_CUSTOM_IGNORE_PATTERN

        # 5. Path globs — built-in fixtures first, then the operator's `--ignore-path`, so the
        #    returned token attributes the suppression to whichever rule ACTUALLY caused it.
        path_reason = cls.path_glob_reason(file_path, ignore_paths)
        if path_reason is not None:
            return True, path_reason

        return False, None
