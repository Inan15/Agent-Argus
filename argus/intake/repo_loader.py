"""IMPURE repo intake — load a repository @ a pinned commit, refuse on drift.

Drivers: ArgusAgent-FR-1 (headless repo intake @ pinned commit; refuse a drifted
working tree), ArgusAgent-NFR-S1 (no absolute host path persisted into an artifact —
source paths are repo-root-relative POSIX), AR8 (pure/impure separation — this
is the impure shell; ``RepoIntake`` is a frozen pure contract), AR10 (typed
failure — a missing repo / bad commit / dirty-vs-pin mismatch raises
``RepoIntakeError``, never a bare crash or a silent empty tree), AR11 (the
discovered source-file set is sorted, never arrival/iteration order).

Repo-load mechanism (locked decision)
-------------------------------------
This loader reads the WORKING TREE and asserts it corresponds to the requested
pin, rather than reconstructing the committed tree via ``git show``. Concretely:

1. The requested commit is resolved to a full SHA with ``git rev-parse <commit>``
   (a short SHA / ref / tag all resolve). An unresolvable commit raises
   :class:`RepoIntakeError`.
2. ``git rev-parse HEAD`` must equal the resolved pin — HEAD must BE the pin
   (no silent audit of a different checkout).
3. The working tree must be CLEAN relative to that commit: ``git status
   --porcelain`` must be empty (no staged/unstaged/untracked drift). Any drift
   raises :class:`RepoIntakeError` — an audit can never silently audit
   uncommitted drift (FR1).

"Drift" is therefore defined as: ``HEAD != pin`` OR a non-empty
``git status --porcelain``. On a clean, on-pin tree the discovered source-file
set is enumerated from ``git ls-files`` (tracked files only — committed state),
which is deterministic and ignores untracked/ignored noise.

All ``git`` invocation, subprocess error handling, and filesystem reads live in
this impure module; the returned :class:`RepoIntake` is frozen and
construction-pure (no clock / uuid / random / float).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from argus.shared.source_languages import AUDITABLE_SUFFIXES

__all__ = [
    "RepoIntakeError",
    "RepoIntake",
    "load_repo_at_commit",
    "to_native_fs_path",
]

# Source-file extensions enumerated into the intake (V1 cares about Python; the
# full set is kept small and additive — stack detection consumes the same tree).
# The auditable set is defined ONCE in argus.shared.source_languages. It used to be
# a Python-only literal here, and because enumeration gates every later stage, that
# narrow copy silently made the multi-language support downstream unreachable.
_SOURCE_SUFFIXES: frozenset[str] = AUDITABLE_SUFFIXES

_GIT_TIMEOUT_SECONDS = 30


class RepoIntakeError(ValueError):
    """Raised when a repo cannot be loaded at the requested pin (AR10 typed failure).

    A ``ValueError`` subclass (mirroring ``store.canonical.CanonicalSerializationError``
    / ``ledger.recording.RecordingValidationError``) — the typed failure for a
    missing repo / non-existent path / unresolvable commit / dirty-tree-vs-pin
    mismatch. The message names the relative offending condition only — never an
    absolute host path (NFR-S1 spirit).
    """


class RepoIntake(BaseModel):
    """Frozen result of loading a repo @ a pinned commit (FR1 / AR8 pure contract).

    ``frozen=True, extra="forbid"`` (Story 1.1 ``Envelope`` / Story 1.2
    ``Recording`` precedent): an unknown field on read-back is a typed
    ``ValidationError``. The audited-repo ABSOLUTE root is held only transiently
    by the impure loader and is NOT a field here — only the resolved commit SHA
    and the repo-root-relative POSIX source-file set are carried (NFR-S1: no
    absolute host path is ever persisted into an artifact). Construction-pure
    (no clock / uuid / random / float).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(default="1", description="RepoIntake schema version (additive-only).")
    commit_sha: str = Field(..., description="The resolved full commit SHA the tree corresponds to.")
    source_files: tuple[str, ...] = Field(
        ..., description="Sorted repo-root-relative POSIX source-file paths (AR11)."
    )


def _run_git(repo_root: Path, *args: str, strip_output: bool = True) -> str:
    """Run ``git -C <repo_root> <args>`` and return its stdout (typed failure).

    Raises :class:`RepoIntakeError` on a non-zero exit, a missing ``git`` binary,
    a timeout, or a non-repo path — never a bare ``CalledProcessError`` /
    ``FileNotFoundError`` out of this shell (AR10).

    ``strip_output=False`` returns raw stdout — required for the NUL-separated
    ``git ls-files -z`` stream, where trailing/embedded whitespace is meaningful
    and ``str.strip()`` would corrupt the final record (the path-quoting fix).

    stdout is captured as bytes and decoded as UTF-8 (not the platform default
    that ``text=True`` would use), so a non-ASCII path round-trips faithfully on
    Windows (cp1252) as well as POSIX — git emits paths as UTF-8 bytes.
    """
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            capture_output=True,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as exc:  # git binary unavailable
        raise RepoIntakeError("git executable not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise RepoIntakeError(f"git {' '.join(args)} timed out") from exc
    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RepoIntakeError(
            f"git {' '.join(args)} failed (exit {proc.returncode}): "
            f"{stderr or 'no stderr'}"
        )
    stdout = proc.stdout.decode("utf-8", errors="replace")
    return stdout if not strip_output else stdout.strip()


def to_native_fs_path(path: str) -> str:
    """Convert a UTF-8-decoded relative path into the host's OPENABLE form (NFR-P1).

    THE INVERSE of ``store.canonical._repair_surrogates``, and the second half of the
    same host-locale boundary.

    ``_run_git`` decodes git's output as explicit UTF-8, so a file named ``café``
    arrives here as the true text ``'caf\\xe9'``. That is the right form to RECORD, but
    on POSIX under a non-UTF-8 locale (``LC_ALL=C`` with ``PYTHONUTF8=0``) it is NOT the
    form the host can open: ``sys.getfilesystemencoding()`` is ASCII there, so any
    filesystem call re-encodes the argument with the ASCII codec and raises::

        UnicodeEncodeError: 'ascii' codec can't encode character '\\xe9'

    Every downstream consumer of ``RepoIntake.source_files`` opens the file it names
    (``detect_stack``, ``build_ast_index``, the per-file detector reads), so on such a
    host the RESUME path — the one caller still routed through this loader — crashed on
    any repository holding a non-ASCII filename.

    ``os.fsdecode(text.encode("utf-8"))`` re-reads git's real on-disk bytes through the
    host's own filename rule, yielding the surrogate-bearing native str that host can
    actually open (``'caf\\udcc3\\udca9'``). On a UTF-8 host it is an exact identity, so
    nothing changes there.

    This makes both intake producers agree on ONE contract — ``source_files`` holds
    OS-NATIVE strings — which is what the fresh-run producer (``intake.source_state``,
    walking via ``os.walk``) has always returned. Recording stays host-independent
    because the serializer repairs the surrogates back to ``'caf\\xe9'`` on the way to
    disk, and that round trip is exact: the two functions are inverses over every path
    git emits, so the persisted bytes are identical on both hosts.

    A path whose bytes were NOT valid UTF-8 was already lossy before this call
    (``_run_git`` decodes with ``errors="replace"``), and it stays lossy in the same
    deterministic way — U+FFFD, never an exception.
    """
    return os.fsdecode(path.encode("utf-8"))


def load_repo_at_commit(repo_path: str | Path, commit: str) -> RepoIntake:
    """Load *repo_path* @ *commit*, refusing a drifted working tree (FR1).

    Verifies the checked-out HEAD equals the resolved pin AND the working tree is
    clean, then enumerates the tracked source-file set. Returns a frozen
    :class:`RepoIntake`.

    Raises:
        RepoIntakeError: missing path / non-git repo / unresolvable commit /
            ``HEAD != pin`` / a non-empty ``git status --porcelain`` (drift).
    """
    root = Path(repo_path)
    if not root.exists():
        raise RepoIntakeError(f"repo path does not exist: {root.name!r}")
    if not root.is_dir():
        raise RepoIntakeError(f"repo path is not a directory: {root.name!r}")

    # 1. Resolve the requested pin to a full SHA (short SHA / ref / tag all work).
    resolved = _run_git(root, "rev-parse", "--verify", f"{commit}^{{commit}}")
    if not resolved:
        raise RepoIntakeError(f"commit {commit!r} did not resolve to a SHA")

    # 2. HEAD must BE the pin.
    head = _run_git(root, "rev-parse", "HEAD")
    if head != resolved:
        raise RepoIntakeError(
            f"working tree drift: HEAD ({head[:12]}) != pinned commit ({resolved[:12]})"
        )

    # 3. The working tree must be clean relative to that commit.
    porcelain = _run_git(root, "status", "--porcelain")
    if porcelain:
        raise RepoIntakeError(
            "working tree drift: uncommitted changes present "
            "(git status --porcelain is non-empty)"
        )

    # 4. Enumerate tracked source files (committed state), sorted (AR11).
    #    ``-z`` emits NUL-separated, UNQUOTED paths (bypassing git's default
    #    ``core.quotepath=true``), so a non-ASCII-named source file is enumerated
    #    with its real relative POSIX path instead of being silently dropped /
    #    octal-escaped (AC1 audit-input completeness). The stream must NOT be
    #    ``.strip()``-ed / ``splitlines()``-ed — split on the NUL byte directly.
    tracked = _run_git(root, "ls-files", "-z", strip_output=False)
    source_files = tuple(
        sorted(
            to_native_fs_path(line)
            for line in tracked.split("\0")
            if line and Path(line).suffix in _SOURCE_SUFFIXES
        )
    )

    return RepoIntake(commit_sha=resolved, source_files=source_files)
