"""IMPURE source-state resolution — audit what is there, and say what it was.

Drivers: ArgusAgent-FR-1 (repo intake), AR4 (deterministic — sorted walks, exact
hashes, no clock/random), AR10 (degrade honestly — every exclusion is counted and
reported, never silent), NFR-S1 (repo-relative paths only; no absolute host path).

Why this module exists
----------------------
Intake previously required a git repository, a clean working tree, and an explicit
``--commit``. Those three preconditions are a locked front door: a developer with a
half-built project — no ``git init`` yet, or simply mid-edit — could not run Argus
at all.

Refusing to run does not make an audit more honest; it means no audit happened.
The rigour belongs in what the tool CLAIMS, not in whether it will start. So intake
now resolves whichever source state is actually present and RECORDS which one it
was, letting the report and evidence bundle carry the distinction.

The determinism cost of this is nil, which is the key fact: the memoization closure
in ``cache/key.py`` keys on the CONTENT hash of the audited unit (plus detectors,
grammar/tool versions, budget, materiality bar, manifest) and contains no reference
to a commit at all. Byte-reproducibility comes from content addressing, never from
git. What the commit pin uniquely provides is THIRD-PARTY retrievability — a
reviewer can ``git checkout`` a SHA — and that is precisely the property this module
labels rather than fakes.

The three modes
---------------
``commit``    — git present, tree clean, ``HEAD == pin``. Unchanged behaviour, and
                the only mode whose evidence a third party can reconstruct from a
                ref. This is what ``--strict`` demands.
``worktree``  — git present, tree dirty. Audits what is on disk; identity keeps the
                nearest committed anchor (``<sha12>-dirty+<digest12>``, the
                ``git describe --dirty`` convention) so lineage is not lost.
``directory`` — no git. Audits the directory; identity is ``dir+<digest12>``.

The digest is a content hash over the sorted ``(path, sha256(bytes))`` pairs of the
audited set. It pins exactly what was READ, which is strictly more precise than a
commit SHA (that pins what was committed, which may not be what was audited).
"""

from __future__ import annotations

import hashlib
import os
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from argus.shared.source_languages import AUDITABLE_SUFFIXES
from argus.intake.repo_loader import RepoIntakeError
from argus.intake.ignore_rules import (
    IgnoreReason,
    classify_path,
    corroborated_tier2_components,
    gitignore_matches,
    parse_gitignore,
)
from argus.store import canonical

__all__ = [
    "SourceStateKind",
    "SourceState",
    "resolve_source_state",
    "SourceStateError",
]

_SOURCE_SUFFIXES: frozenset[str] = AUDITABLE_SUFFIXES


class SourceStateError(RepoIntakeError):
    """Raised when a source state cannot be resolved (AR10 typed failure).

    Subclasses :class:`RepoIntakeError` deliberately: every existing caller and test
    that catches an intake failure keeps working unchanged, because "this source
    state cannot be loaded" IS an intake failure. Introducing a sibling type would
    have silently broken those handlers into bare crashes (exit 1 with no typed
    message) — the opposite of AR10.
    """


class SourceStateKind:
    """Closed vocabulary for what was actually audited."""

    COMMIT = "commit"
    WORKTREE = "worktree"
    DIRECTORY = "directory"


@dataclass(frozen=True)
class SourceState:
    """What was audited, how it is identified, and what was left out.

    ``reproducible`` is the honest headline: only a ``commit`` state can be
    reconstructed by someone else from the identity alone.
    """

    kind: str
    identity: str
    source_files: tuple[str, ...]
    reproducible: bool
    excluded_by_reason: dict[str, int] = field(default_factory=dict)
    base_commit: str | None = None

    @property
    def excluded_total(self) -> int:
        return sum(self.excluded_by_reason.values())


def _digest_of(root: Path, rel_paths: tuple[str, ...]) -> str:
    """Content digest over the audited set — deterministic, order-independent (AR4).

    Hashes ``path\\0sha256(bytes)\\0`` for each file in sorted order, so the digest
    changes if a path is added/removed/renamed OR if any byte changes.
    """
    outer = hashlib.sha256()
    for rel in rel_paths:  # already sorted by the caller
        inner = hashlib.sha256()
        try:
            inner.update((root / rel).read_bytes())
        except OSError as exc:
            raise SourceStateError(f"could not read {rel!r} while pinning source state: {exc}") from exc
        # See canonical.safe_utf8_bytes — a bare .encode crashes on the surrogates a
        # C-locale POSIX host produces for a non-ASCII path, and would make this
        # digest host-dependent (NFR-P1).
        outer.update(canonical.safe_utf8_bytes(rel))
        outer.update(b"\0")
        outer.update(inner.hexdigest().encode("ascii"))
        outer.update(b"\0")
    return outer.hexdigest()


def _walk_sources(root: Path) -> tuple[tuple[str, ...], dict[str, int]]:
    """Deterministic filesystem walk → (sorted source files, excluded counts by reason).

    Ignored directories are PRUNED rather than filtered afterwards: descending into
    ``node_modules`` or ``.venv`` to then discard the results can mean walking
    hundreds of thousands of entries, and a first run that appears to hang is
    indistinguishable from one that is broken.

    Counts are per FILE (of an auditable suffix), so the reported exclusion total is
    comparable with the audited total rather than counting directories.
    """
    root_entries = frozenset(entry.name for entry in os.scandir(root))
    tier2 = corroborated_tier2_components(root_entries)

    gitignore = root / ".gitignore"
    patterns = parse_gitignore(gitignore.read_text(encoding="utf-8", errors="replace")) \
        if gitignore.is_file() else ()

    found: list[str] = []
    excluded: Counter[str] = Counter()

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root).as_posix()
        rel_dir = "" if rel_dir == "." else rel_dir

        kept_dirs: list[str] = []
        for name in sorted(dirnames):
            rel = f"{rel_dir}/{name}" if rel_dir else name
            decision = classify_path(f"{rel}/x", tier2_enabled=tier2)
            if decision.ignored:
                excluded[decision.reason or "unknown"] += _count_sources_under(root / rel)
                continue
            if patterns and gitignore_matches(rel, patterns, is_dir=True):
                excluded[IgnoreReason.GITIGNORED] += _count_sources_under(root / rel)
                continue
            kept_dirs.append(name)
        dirnames[:] = kept_dirs  # prune in place — os.walk honours this

        for name in sorted(filenames):
            if Path(name).suffix not in _SOURCE_SUFFIXES:
                continue
            rel = f"{rel_dir}/{name}" if rel_dir else name
            if patterns and gitignore_matches(rel, patterns):
                excluded[IgnoreReason.GITIGNORED] += 1
                continue
            found.append(rel)

    return tuple(sorted(found)), dict(excluded)


def _count_sources_under(directory: Path) -> int:
    """Count auditable-suffix files under *directory* (for an honest exclusion total).

    Bounded by design: this is only called for a directory already classified as
    non-source, and it does not recurse into further ignorable subtrees for counting
    purposes — an approximate-but-never-zero count is enough to tell an operator the
    magnitude of what was held out.
    """
    total = 0
    for _dirpath, _dirnames, filenames in os.walk(directory):
        total += sum(1 for n in filenames if Path(n).suffix in _SOURCE_SUFFIXES)
    return total


def _git(root: Path, *args: str) -> str | None:
    """Run git, returning stripped stdout, or ``None`` if git/repo is unavailable."""
    import subprocess

    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def resolve_source_state(
    repo_path: str | Path,
    *,
    commit: str = "HEAD",
    strict: bool = False,
) -> SourceState:
    """Resolve whichever source state is present (AR10 — never refuse by default).

    ``strict=True`` restores the original contract: a git repository, a clean tree,
    and ``HEAD == commit``, or a typed refusal. That is the release-gate mode, and it
    belongs in CI — configured once, deliberately, by whoever owns the gate — rather
    than in the path of every first run.
    """
    root = Path(repo_path).resolve()
    if not root.is_dir():
        raise SourceStateError(f"repo path is not a directory: {repo_path!r}")

    # Repo presence and commit presence are DISTINCT. A freshly `git init`-ed project
    # is a git repository with no HEAD — exactly the "new repo under development" case
    # this work exists to support — so probing HEAD alone would misclassify it as
    # "no git" and skip the explicit-commit validation below.
    is_git = _git(root, "rev-parse", "--git-dir") is not None
    head = _git(root, "rev-parse", "HEAD") if is_git else None
    has_commits = head is not None
    dirty_out = _git(root, "status", "--porcelain") if is_git else None
    is_dirty = bool(dirty_out)

    if strict:
        if not is_git or head is None:
            raise SourceStateError(
                "--strict requires a git repository (no git metadata found). "
                "Drop --strict to audit the directory as-is."
            )
        resolved = _git(root, "rev-parse", "--verify", f"{commit}^{{commit}}")
        if not resolved:
            raise SourceStateError(f"commit {commit!r} did not resolve to a SHA")
        if head != resolved:
            raise SourceStateError(
                f"working tree drift: HEAD ({head[:12]}) != pinned commit ({resolved[:12]})"
            )
        if is_dirty:
            raise SourceStateError(
                "working tree drift: uncommitted changes present "
                "(git status --porcelain is non-empty). Drop --strict to audit the "
                "working tree as-is."
            )

    # An EXPLICITLY named commit that does not resolve is an error even outside strict
    # mode. Falling back to "audit whatever is on disk" would silently audit something
    # other than what the operator asked for and report success — the precise
    # misrepresentation this relaxation must not introduce. A defaulted "HEAD" that
    # does not resolve is different: that is a git repo with no commits yet (the
    # freshly-`git init`-ed project), which is a NORMAL state to audit as a directory.
    if is_git and commit != "HEAD":
        if not _git(root, "rev-parse", "--verify", f"{commit}^{{commit}}"):
            raise SourceStateError(f"commit {commit!r} did not resolve to a SHA")

    files, excluded = _walk_sources(root)

    if is_git and head is not None and not is_dirty:
        resolved = _git(root, "rev-parse", "--verify", f"{commit}^{{commit}}") or head
        return SourceState(
            kind=SourceStateKind.COMMIT,
            identity=resolved,
            source_files=files,
            reproducible=True,
            excluded_by_reason=excluded,
            base_commit=resolved,
        )

    digest = _digest_of(root, files)[:12]
    if is_git and head is not None:
        return SourceState(
            kind=SourceStateKind.WORKTREE,
            identity=f"{head[:12]}-dirty+{digest}",
            source_files=files,
            reproducible=False,
            excluded_by_reason=excluded,
            base_commit=head,
        )
    return SourceState(
        kind=SourceStateKind.DIRECTORY,
        identity=f"dir+{digest}",
        source_files=files,
        reproducible=False,
        excluded_by_reason=excluded,
    )
