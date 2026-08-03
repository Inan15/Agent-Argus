"""PURE role-based source/non-source classification for non-git repository intake.

Drivers: ArgusAgent-FR-1 (repo intake), ArgusAgent-NFR-P2 (stack-agnostic by
construction), AR4 (deterministic; no clock/random/iteration-order), AR8 (pure —
this module takes the already-listed paths + already-read markers as ARGUMENTS and
never touches the filesystem), AR10 (degrade honestly — an exclusion is RECORDED
with its reason, never silently applied).

Why this module exists
----------------------
``git ls-files`` gives intake a deterministic, noise-free source set for free: it
lists tracked files only. Auditing a directory that is not a clean git checkout
loses that, and a naive filesystem walk pulls in ``node_modules``, ``.venv``,
``target/``, ``__pycache__`` — often orders of magnitude more files than the
application itself.

That is not cosmetic. Vendored dependencies enter the coverage ledger graded
shallow-or-less and swamp the deep-% denominator, manufacturing exactly the
false-negative class the assessment-scope seam exists to remove: a
``NOT_READY_FOR_RELEASE`` earned by having dependencies rather than by any defect.

Classification is therefore by ROLE, not by name-matching alone.

The two tiers (and why the second one exists)
---------------------------------------------
**Tier 1 — unambiguous.** Names no one gives to application code:
``node_modules``, ``__pycache__``, ``.mypy_cache``, ``.git``. These are excluded on
the name alone. Matching is on a full PATH COMPONENT, never a substring, so
``src/node_modules_helper.py`` and ``app/distributor.py`` are NOT hit.

**Tier 2 — ambiguous, requires corroboration.** ``build``, ``dist``, ``out``,
``bin``, ``obj``, ``target`` are perfectly ordinary application directory names —
a Python package may legitimately contain ``bin/``, and plenty of projects have a
hand-written ``build/`` module. Excluding those on the name alone would DELETE REAL
APPLICATION CODE from the audit, which is far worse than including some build
output: the tool would silently assure a repository it never looked at.

So a Tier-2 directory is excluded only when an ecosystem marker corroborates the
role — ``target/`` only alongside ``Cargo.toml``, ``obj/``/``bin/`` only alongside a
``.csproj``/``.sln``, and so on. This mirrors the two-fact corroboration the vacuous
detector and the promotion moat already use: a suspicious NAME plus an independent
structural FACT before acting.

When corroboration is absent the directory is KEPT. Over-including costs coverage
percentage points; over-excluding costs the truth.
"""

from __future__ import annotations

import fnmatch
import posixpath
from dataclasses import dataclass

__all__ = [
    "IgnoreReason",
    "IgnoreRule",
    "TIER1_RULES",
    "TIER2_RULES",
    "ECOSYSTEM_MARKERS",
    "IgnoreDecision",
    "GitignorePattern",
    "classify_path",
    "corroborated_tier2_components",
    "parse_gitignore",
    "gitignore_matches",
]


class IgnoreReason:
    """Closed vocabulary of WHY a path is not an application subsystem.

    A string enum by convention (mirroring the ``CoverageDepth`` value style) so the
    reason serializes verbatim and can be counted in the report. Every excluded file
    carries one — an exclusion with no reason is indistinguishable from a bug.
    """

    DEPENDENCIES = "dependencies"
    BUILD_OUTPUT = "build_output"
    CACHE = "cache"
    TOOLING_METADATA = "tooling_metadata"
    GITIGNORED = "gitignored"
    OPERATOR = "operator_ignored"


@dataclass(frozen=True)
class IgnoreRule:
    """One directory-component rule: the component name, its role, and its ecosystem.

    ``ecosystem`` is ``None`` for Tier-1 rules (no corroboration needed) and a key
    into :data:`ECOSYSTEM_MARKERS` for Tier-2 rules.
    """

    component: str
    reason: str
    ecosystem: str | None = None


# ── Tier 1 — excluded on the name alone (no application code is named these) ──
TIER1_RULES: tuple[IgnoreRule, ...] = (
    # Dependencies / vendored third-party code
    IgnoreRule("node_modules", IgnoreReason.DEPENDENCIES),
    IgnoreRule("bower_components", IgnoreReason.DEPENDENCIES),
    IgnoreRule("jspm_packages", IgnoreReason.DEPENDENCIES),
    IgnoreRule("site-packages", IgnoreReason.DEPENDENCIES),
    IgnoreRule("Pods", IgnoreReason.DEPENDENCIES),
    IgnoreRule("Carthage", IgnoreReason.DEPENDENCIES),
    IgnoreRule("bundle", IgnoreReason.DEPENDENCIES),  # ruby vendor/bundle
    IgnoreRule(".bundle", IgnoreReason.DEPENDENCIES),
    IgnoreRule(".yarn", IgnoreReason.DEPENDENCIES),
    IgnoreRule(".pnpm-store", IgnoreReason.DEPENDENCIES),
    IgnoreRule(".cargo", IgnoreReason.DEPENDENCIES),
    IgnoreRule(".gradle", IgnoreReason.DEPENDENCIES),
    IgnoreRule(".m2", IgnoreReason.DEPENDENCIES),
    IgnoreRule(".nuget", IgnoreReason.DEPENDENCIES),
    IgnoreRule(".stack-work", IgnoreReason.DEPENDENCIES),
    IgnoreRule("Godeps", IgnoreReason.DEPENDENCIES),
    # Virtualenvs — a Python env is dependencies, never application code
    IgnoreRule(".venv", IgnoreReason.DEPENDENCIES),
    IgnoreRule("venv", IgnoreReason.DEPENDENCIES),
    IgnoreRule("virtualenv", IgnoreReason.DEPENDENCIES),
    IgnoreRule(".tox", IgnoreReason.DEPENDENCIES),
    IgnoreRule(".nox", IgnoreReason.DEPENDENCIES),
    IgnoreRule(".conda", IgnoreReason.DEPENDENCIES),
    # Caches
    IgnoreRule("__pycache__", IgnoreReason.CACHE),
    IgnoreRule(".mypy_cache", IgnoreReason.CACHE),
    IgnoreRule(".pytest_cache", IgnoreReason.CACHE),
    IgnoreRule(".ruff_cache", IgnoreReason.CACHE),
    IgnoreRule(".pytype", IgnoreReason.CACHE),
    IgnoreRule(".dmypy.json", IgnoreReason.CACHE),
    IgnoreRule(".sass-cache", IgnoreReason.CACHE),
    IgnoreRule(".parcel-cache", IgnoreReason.CACHE),
    IgnoreRule(".turbo", IgnoreReason.CACHE),
    IgnoreRule(".nx", IgnoreReason.CACHE),
    IgnoreRule("__snapshots__", IgnoreReason.CACHE),
    # Generated / build output whose names are unambiguous
    IgnoreRule(".next", IgnoreReason.BUILD_OUTPUT),
    IgnoreRule(".nuxt", IgnoreReason.BUILD_OUTPUT),
    IgnoreRule(".svelte-kit", IgnoreReason.BUILD_OUTPUT),
    IgnoreRule(".angular", IgnoreReason.BUILD_OUTPUT),
    IgnoreRule(".output", IgnoreReason.BUILD_OUTPUT),
    IgnoreRule("__generated__", IgnoreReason.BUILD_OUTPUT),
    IgnoreRule(".terraform", IgnoreReason.BUILD_OUTPUT),
    IgnoreRule("DerivedData", IgnoreReason.BUILD_OUTPUT),
    # VCS / editor / CI tooling metadata
    IgnoreRule(".git", IgnoreReason.TOOLING_METADATA),
    IgnoreRule(".hg", IgnoreReason.TOOLING_METADATA),
    IgnoreRule(".svn", IgnoreReason.TOOLING_METADATA),
    IgnoreRule(".idea", IgnoreReason.TOOLING_METADATA),
    IgnoreRule(".vscode", IgnoreReason.TOOLING_METADATA),
    IgnoreRule(".vs", IgnoreReason.TOOLING_METADATA),
    IgnoreRule(".argus", IgnoreReason.TOOLING_METADATA),  # our own store
)

# ── Tier 2 — ONLY excluded when an ecosystem marker corroborates the role ──
TIER2_RULES: tuple[IgnoreRule, ...] = (
    IgnoreRule("target", IgnoreReason.BUILD_OUTPUT, "rust_or_jvm"),
    IgnoreRule("build", IgnoreReason.BUILD_OUTPUT, "jvm_or_native_or_python"),
    IgnoreRule("dist", IgnoreReason.BUILD_OUTPUT, "js_or_python"),
    IgnoreRule("out", IgnoreReason.BUILD_OUTPUT, "js_or_jvm"),
    IgnoreRule("bin", IgnoreReason.BUILD_OUTPUT, "dotnet_or_go"),
    IgnoreRule("obj", IgnoreReason.BUILD_OUTPUT, "dotnet"),
    IgnoreRule("Debug", IgnoreReason.BUILD_OUTPUT, "dotnet"),
    IgnoreRule("Release", IgnoreReason.BUILD_OUTPUT, "dotnet"),
    IgnoreRule("coverage", IgnoreReason.BUILD_OUTPUT, "js_or_python"),
    IgnoreRule("vendor", IgnoreReason.DEPENDENCIES, "go_or_php"),
)

# Ecosystem key -> the repo-root marker files that corroborate it. A Tier-2 rule
# fires only when at least one of its ecosystem's markers is present at the root.
ECOSYSTEM_MARKERS: dict[str, tuple[str, ...]] = {
    "rust_or_jvm": ("Cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts", "build.sbt"),
    "jvm_or_native_or_python": (
        "pom.xml", "build.gradle", "build.gradle.kts", "CMakeLists.txt",
        "Makefile", "meson.build", "setup.py", "pyproject.toml",
    ),
    "js_or_python": ("package.json", "pyproject.toml", "setup.py", "setup.cfg"),
    "js_or_jvm": ("package.json", "pom.xml", "build.gradle", "build.gradle.kts", "tsconfig.json"),
    "dotnet_or_go": ("go.mod", "Directory.Build.props"),
    "dotnet": ("Directory.Build.props",),
    "go_or_php": ("go.mod", "composer.json"),
}

# Suffix-based markers (a .csproj/.sln has a project-specific name, so the marker is
# the SUFFIX rather than a fixed filename).
ECOSYSTEM_MARKER_SUFFIXES: dict[str, tuple[str, ...]] = {
    "dotnet": (".csproj", ".sln", ".fsproj", ".vbproj"),
    "dotnet_or_go": (".csproj", ".sln"),
}

_TIER1_BY_COMPONENT: dict[str, IgnoreRule] = {rule.component: rule for rule in TIER1_RULES}
_TIER2_BY_COMPONENT: dict[str, IgnoreRule] = {rule.component: rule for rule in TIER2_RULES}


@dataclass(frozen=True)
class IgnoreDecision:
    """Whether a path is application source, and — when not — the recorded reason."""

    ignored: bool
    reason: str | None = None


def corroborated_tier2_components(root_entries: frozenset[str]) -> dict[str, str]:
    """Return the Tier-2 components that *root_entries* corroborate → their reason (PURE).

    ``root_entries`` is the set of entry NAMES directly under the repository root
    (files and directories), supplied by the impure caller — this module never reads
    the filesystem (AR8).

    A Tier-2 component is enabled only when its ecosystem has a marker present. With
    no marker the component stays AUDITABLE: a ``build/`` directory in a repo with no
    build system is far more likely to be someone's package than compiler output, and
    including it costs coverage percentage points while excluding it would hide code.
    """
    enabled: dict[str, str] = {}
    for rule in TIER2_RULES:
        ecosystem = rule.ecosystem
        if ecosystem is None:  # pragma: no cover - defensive; Tier-2 always has one
            continue
        names = ECOSYSTEM_MARKERS.get(ecosystem, ())
        if any(marker in root_entries for marker in names):
            enabled[rule.component] = rule.reason
            continue
        suffixes = ECOSYSTEM_MARKER_SUFFIXES.get(ecosystem, ())
        if suffixes and any(
            entry.endswith(suffix) for entry in root_entries for suffix in suffixes
        ):
            enabled[rule.component] = rule.reason
    return enabled


@dataclass(frozen=True)
class GitignorePattern:
    """One parsed ``.gitignore`` line."""

    pattern: str      # normalised, no leading '!' or '/', no trailing '/'
    negated: bool     # a '!' rule re-includes a previously excluded path
    dir_only: bool    # a trailing '/' matches directories only
    anchored: bool    # a leading (or embedded) '/' anchors to the repo root


def parse_gitignore(text: str) -> tuple[GitignorePattern, ...]:
    """Parse ``.gitignore`` *text* into ordered patterns (PURE).

    A repository's own ``.gitignore`` is the most reliable statement of what is not
    source, and it is usually present even in a directory that was never
    ``git init``-ed — so it is honoured regardless of whether git is available.

    SUPPORTED SUBSET (documented rather than implied, because a silently partial
    implementation of a matching language is a trap): comments, blank lines, ``!``
    negation, trailing-``/`` directory-only rules, leading-``/`` root anchoring,
    and ``*`` / ``?`` / ``**`` globs. NOT supported: character classes with ranges
    beyond ``fnmatch``'s, and per-directory nested ``.gitignore`` files (only the
    root one is read). Anything unsupported simply fails to match — it can leave a
    file IN the audit, never silently remove one, which is the safe direction.
    """
    patterns: list[GitignorePattern] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        negated = line.startswith("!")
        if negated:
            line = line[1:]
        dir_only = line.endswith("/")
        line = line.rstrip("/")
        # A '/' anywhere but the trailing position anchors the pattern to the root.
        anchored = line.startswith("/") or "/" in line
        line = line.lstrip("/")
        if not line:
            continue
        patterns.append(GitignorePattern(line, negated, dir_only, anchored))
    return tuple(patterns)


def _pattern_hits(pattern: GitignorePattern, rel_path: str, is_dir: bool) -> bool:
    if pattern.dir_only and not is_dir:
        # A dir-only rule still covers everything BENEATH the directory; the walker
        # applies it by pruning, and here we accept a path under a matching prefix.
        pass
    if pattern.anchored:
        if fnmatch.fnmatch(rel_path, pattern.pattern):
            return True
        # `build/` should also match `build/x/y.py`
        return fnmatch.fnmatch(rel_path, pattern.pattern.rstrip("/") + "/*")
    # Unanchored: match against any single component, or any trailing sub-path.
    components = rel_path.split("/")
    if any(fnmatch.fnmatch(component, pattern.pattern) for component in components):
        return True
    return fnmatch.fnmatch(rel_path, "*/" + pattern.pattern)


def gitignore_matches(
    rel_path: str, patterns: tuple[GitignorePattern, ...], *, is_dir: bool = False
) -> bool:
    """Whether *rel_path* is ignored by *patterns* (PURE, last-match-wins like git).

    Later patterns override earlier ones, so a ``!`` re-include placed after a broad
    exclusion works the way an author expects.
    """
    ignored = False
    for pattern in patterns:
        if _pattern_hits(pattern, rel_path, is_dir):
            ignored = not pattern.negated
    return ignored


def classify_path(
    rel_path: str,
    *,
    tier2_enabled: dict[str, str] | None = None,
) -> IgnoreDecision:
    """Classify a repo-relative POSIX path as application source or ignorable (PURE).

    Matching is on whole path COMPONENTS. ``src/node_modules_helper.py`` is source
    (``node_modules_helper`` != ``node_modules``); ``web/node_modules/x/index.js`` is
    not. Substring matching here would silently drop real files, so it is never used.

    ``tier2_enabled`` comes from :func:`corroborated_tier2_components`; when omitted,
    NO Tier-2 rule fires — the conservative default, since an uncorroborated
    ambiguous name is not evidence of build output.
    """
    enabled = tier2_enabled or {}
    # Directory components only — the final segment is the filename, and a FILE named
    # `build` or `dist` is ordinary source, not a build directory.
    components = posixpath.normpath(rel_path).split("/")[:-1]
    for component in components:
        rule = _TIER1_BY_COMPONENT.get(component)
        if rule is not None:
            return IgnoreDecision(True, rule.reason)
        reason = enabled.get(component)
        if reason is not None and component in _TIER2_BY_COMPONENT:
            return IgnoreDecision(True, reason)
    return IgnoreDecision(False)
