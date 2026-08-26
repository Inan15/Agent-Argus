"""Story 13.5 — materialize a validation-corpus member from its PINNED GIT OBJECT.

    from pinned_corpus_snapshot import pinned_tree, materialize_pinned_bytes, verify_pinned_bytes

**Why this module exists, measured rather than argued.** ``scripts/audit_validation_corpus.py``
enforced its pin by comparing ``git rev-parse HEAD`` to the manifest sha, and then staged the
snapshot with ``argus.dogfood.proof_run.materialize_snapshot``, which copies **WORKING-TREE
bytes**. Those are two different claims. On 2026-08-18, over the five ratified checkouts:

* ``minions`` was OFF its pin (``HEAD 8b7be40f`` vs pinned ``ec63b729``) and the runner
  REFUSED it — a LOUD failure, the runner working;
* ``agent-smith`` was ON its pin and carried **16 dirty entries, several of them in-scope
  sources under ``agentsmith-core/``** — a SILENT failure. An audit labelled
  ``agent-smith@9ab774d7`` measured the pin PLUS somebody's uncommitted edits, and
  ``byte_reproducible_across_two_runs`` still reported ``True``, because two runs over the
  same wrong bytes are reproducible.

**Reproducibility is not provenance.** This module closes that by construction: the audited
bytes are read from the object database at the pinned commit (``git ls-tree`` +
``git cat-file --batch``), never from the working tree, and then **every materialized file is
proved to be the pinned blob** by recomputing git's own blob hash over the bytes on disk and
comparing it to the blob id ``ls-tree`` reported. The pin stops being assumed and becomes
structurally enforced, and a deviation stops being silent.

**It is a pure READ of the source repository.** ``ls-tree`` and ``cat-file`` write nothing —
no checkout, no stash, no clean, no worktree metadata, no branch change. The ratified
checkouts belong to other projects and are treated as strictly read-only. ``git worktree add``
was considered and rejected: it writes into the target repository's ``.git/worktrees``.

**Windows ``MAX_PATH`` is a NAMED refusal, not a mystery.** An extraction under a deep
scratch root silently loses files whose absolute path exceeds ~260 characters, and a
measurement over a truncated corpus reports 0 findings — indistinguishable from a real 0,
which is exactly the claim Story 13.5 makes. So the destination path length is checked BEFORE
the write, the extracted file COUNT is compared against ``git ls-tree``'s count, and every
byte is hashed. Three independent ways for a truncated corpus to be caught, because the
headline result is an absence.

Exceptions are typed (AR10) and none of them is recoverable by guessing:
:class:`PinUnreachable` is a NAMED ``Unevaluable`` outcome for a member (never a silent
fallback to the working tree), and :class:`PinnedBytesRefusal` means the bytes on disk could
not be shown to be the pinned bytes.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

__all__ = [
    "MAX_ABSOLUTE_PATH_CHARS",
    "map_path_is_absolute",
    "PinUnreachable",
    "PinVerification",
    "PinnedBytesRefusal",
    "PinnedFile",
    "PinnedSnapshotError",
    "PinnedTree",
    "PorcelainEntry",
    "blob_sha1",
    "dirty_in_scope_paths",
    "materialize_pinned_bytes",
    "parse_porcelain_z",
    "pin_is_reachable",
    "pinned_tree",
    "verify_pinned_bytes",
]

#: git subprocess ceiling. Generous: ``cat-file --batch`` over a 900-file tree is fast, but a
#: cold object database on a slow disk is not, and a timeout that fires on a slow machine
#: would look exactly like an unreachable pin.
_GIT_TIMEOUT_SECONDS = 900

#: How many blob ids go into one ``cat-file --batch`` invocation. Bounded so a 10k-file member
#: cannot buffer its whole tree in memory at once.
_BATCH = 256

#: The Windows ``MAX_PATH`` boundary, as a REFUSAL rather than a truncation. 260 is the OS
#: limit including the NUL; 250 leaves room for the ``.git`` machinery a snapshot commit adds.
MAX_ABSOLUTE_PATH_CHARS = 250


class PinnedSnapshotError(RuntimeError):
    """Base class — a refusal the operator must act on, never a degraded pass."""


class PinUnreachable(PinnedSnapshotError):
    """The pinned commit is not in this checkout's object database.

    A NAMED ``Unevaluable`` outcome for that member. Deliberately NOT a fallback to the
    working tree: reading the working tree because the pin is missing is precisely the
    silent-deviation defect this module exists to remove, and it would report a number for
    a tree nobody named.
    """


class PinnedBytesRefusal(PinnedSnapshotError):
    """The materialized bytes could NOT be shown to be the pinned bytes.

    Raised on a count mismatch, a missing file or a blob-hash mismatch. This is the loud
    half of the fix: before it, a snapshot that silently lost or altered files still produced
    a byte-reproducible run and a confident zero.
    """


def blob_sha1(data: bytes) -> str:
    """git's own blob object id over *data* — PURE, no subprocess, no I/O (AR8).

    ``sha1(b"blob <len>\\0" + data)``. This is the SAME identity ``git ls-tree`` reports, so
    comparing it against the tree listing proves the bytes on disk are the pinned bytes
    rather than merely that a file of that name exists. It is computed in-process because a
    per-file ``git hash-object`` would be 1,960 subprocesses and would additionally apply the
    repository's ``core.autocrlf`` / ``.gitattributes`` filters — which is the one thing a
    byte-provenance check must not do.
    """
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


@dataclass(frozen=True)
class PinnedFile:
    """One in-scope source file AT the pin: its repository-relative path and its blob id."""

    path: str
    blob_sha: str


@dataclass(frozen=True)
class PinnedTree:
    """The in-scope source tree AT a pinned commit, read from the object database."""

    checkout: str
    commit_sha: str
    files: tuple[PinnedFile, ...]

    @property
    def paths(self) -> tuple[str, ...]:
        """Repository-relative POSIX paths, SORTED (NFR-P1 determinism)."""
        return tuple(entry.path for entry in self.files)

    @property
    def blob_by_path(self) -> dict[str, str]:
        return {entry.path: entry.blob_sha for entry in self.files}


@dataclass(frozen=True)
class PinVerification:
    """The PROOF that what is on disk is what the pin names — or the named reason it is not."""

    method: str
    commit_sha: str
    expected_file_count: int
    verified_file_count: int
    missing_paths: tuple[str, ...]
    mismatched_paths: tuple[str, ...]

    @property
    def proves_pinned_bytes(self) -> bool:
        """True only when EVERY expected file is present and hashes to its pinned blob.

        Non-vacuity is part of the predicate: a verification over ZERO expected files proves
        nothing and must not report success, because an empty corpus and a clean corpus
        produce the same downstream zero.
        """
        return (
            self.expected_file_count > 0
            and self.verified_file_count == self.expected_file_count
            and not self.missing_paths
            and not self.mismatched_paths
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "commit_sha": self.commit_sha,
            "expected_file_count": self.expected_file_count,
            "verified_file_count": self.verified_file_count,
            "missing_paths": list(self.missing_paths),
            "mismatched_paths": list(self.mismatched_paths),
            "proves_pinned_bytes": self.proves_pinned_bytes,
        }


def _git(
    checkout: Path, *args: str, stdin: bytes | None = None
) -> subprocess.CompletedProcess[bytes]:
    """``git -C <checkout> <args>`` — a pure READ; nothing here mutates the repository.

    The WINDOWS path form is passed (``str(Path)``), never a Git-Bash ``/d/...`` form: git
    on Windows exits 128 on the latter, and that failure has already been paid for twice.
    """
    return subprocess.run(  # noqa: S603 - fixed argv, no shell, no untrusted input
        ["git", "-C", str(checkout), *args],
        input=stdin,
        capture_output=True,
        timeout=_GIT_TIMEOUT_SECONDS,
    )


def map_path_is_absolute(relative: str) -> bool:
    r"""Whether *relative* is absolute in EITHER path flavour. PURE — no I/O (AR8).

    ⛔ **BOTH flavours, and the second one is the whole point.** A ``--map MEMBER_ID=PATH`` value
    is promised to be relative to ``--checkout-root``, and pathlib discards the left operand when
    the right one is rooted — so an absolute value silently reads a tree outside the directory
    the operator scoped the run to. ``Path.is_absolute()`` alone does NOT catch this on Windows:
    ``Path("/etc/passwd").is_absolute()`` is **False** there (no drive letter), and
    ``Path("D:/_bench") / "/etc/passwd"`` resolves to ``D:\etc\passwd`` — already outside the
    scoped root. On POSIX the same value discards the root entirely.

    ⛔ **ONE DERIVATION, TWO CALLERS (AR7 / DN-3).** :mod:`audit_validation_corpus` shipped this
    predicate inline first; :mod:`build_ratification_record` copied the ``--map`` flag shape and,
    in its first round, copied only the ``Path.is_absolute()`` half — reintroducing exactly the
    defect the original comment records as already-shipped-and-fixed. It lives here, in the
    module both already import, so the class cannot be half-fixed again.
    """
    return PurePosixPath(relative.replace("\\", "/")).is_absolute() or Path(relative).is_absolute()


def pin_is_reachable(checkout: Path, commit_sha: str) -> bool:
    """Whether *commit_sha* resolves to a COMMIT object in this checkout (never HEAD)."""
    done = _git(checkout, "cat-file", "-t", commit_sha)
    return done.returncode == 0 and done.stdout.decode("utf-8", "replace").strip() == "commit"


def pinned_tree(checkout: Path, commit_sha: str, *, keep: Callable[[str], bool]) -> PinnedTree:
    """The in-scope source tree at *commit_sha*, from ``git ls-tree -r`` — NOT the index.

    ``git ls-files`` reads the INDEX, i.e. the working tree's idea of what is tracked NOW.
    Measured on 2026-08-18 the two disagree materially: ``minions`` has **583** in-scope
    source files at its pin and **479** in its current index. Auditing the index would have
    measured a different repository under the pin's name.
    """
    if not pin_is_reachable(checkout, commit_sha):
        raise PinUnreachable(
            f"{checkout}: the pinned commit {commit_sha} is NOT in this checkout's object "
            f"database (`git cat-file -t` did not report 'commit'). This member is "
            f"UNEVALUABLE for this run and is recorded as such by name. It is NOT audited "
            f"from the working tree: reading whatever happens to be checked out would "
            f"report a number for a tree nobody pinned."
        )
    done = _git(checkout, "ls-tree", "-r", "-z", commit_sha)
    if done.returncode != 0:
        raise PinnedSnapshotError(
            f"{checkout}: `git ls-tree -r {commit_sha}` failed "
            f"({done.stderr.decode('utf-8', 'replace').strip()!r})"
        )
    files: list[PinnedFile] = []
    for record in done.stdout.decode("utf-8", errors="replace").split("\0"):
        if not record:
            continue
        meta, _, path = record.partition("\t")
        parts = meta.split()
        if len(parts) != 3 or parts[1] != "blob":
            continue  # a submodule (commit) or tree entry — not an auditable source file
        if keep(path):
            files.append(PinnedFile(path=path, blob_sha=parts[2]))
    return PinnedTree(
        checkout=str(checkout),
        commit_sha=commit_sha,
        files=tuple(sorted(files, key=lambda entry: entry.path)),
    )


def _read_blobs(checkout: Path, shas: Sequence[str]) -> dict[str, bytes]:
    """Raw object bytes for *shas* via ``git cat-file --batch`` — NO filters, NO checkout."""
    wanted = sorted(set(shas))
    blobs: dict[str, bytes] = {}
    for start in range(0, len(wanted), _BATCH):
        chunk = wanted[start : start + _BATCH]
        done = _git(
            checkout, "cat-file", "--batch", stdin=("\n".join(chunk) + "\n").encode("ascii")
        )
        if done.returncode != 0:
            raise PinnedSnapshotError(
                f"{checkout}: `git cat-file --batch` failed "
                f"({done.stderr.decode('utf-8', 'replace').strip()!r})"
            )
        out = done.stdout
        pos = 0
        for sha in chunk:
            end = out.find(b"\n", pos)
            if end < 0:
                raise PinnedSnapshotError(
                    f"{checkout}: `git cat-file --batch` output ended before object {sha}"
                )
            header = out[pos:end].decode("ascii", "replace").split()
            pos = end + 1
            if len(header) != 3 or header[1] != "blob":
                raise PinUnreachable(
                    f"{checkout}: object {sha} is not a readable blob at the pin "
                    f"(git said {' '.join(header)!r})"
                )
            size = int(header[2])
            blobs[header[0]] = out[pos : pos + size]
            pos += size + 1  # the trailing LF git appends after every object
    return blobs


def _refuse_long_path(target: Path) -> None:
    if os.name == "nt" and len(str(target)) > MAX_ABSOLUTE_PATH_CHARS:
        raise PinnedBytesRefusal(
            f"the destination path is {len(str(target))} characters, over the "
            f"{MAX_ABSOLUTE_PATH_CHARS}-character Windows MAX_PATH working limit: {target}. "
            f"Refused rather than written, because a partially-extracted tree audits clean "
            f"and a clean audit over a truncated corpus is indistinguishable from a real "
            f"zero. Materialize to a SHORT root (e.g. D:/_argus_snap)."
        )


def materialize_pinned_bytes(checkout: Path, tree: PinnedTree, dest: Path) -> Path:
    """Write every file of *tree* into *dest* from the PINNED BLOB — never the working tree.

    Returns *dest*. Nothing is written into *checkout*: this is ``ls-tree`` + ``cat-file``,
    both pure reads of the object database.
    """
    if not tree.files:
        raise PinnedBytesRefusal(
            f"{checkout}: the pinned tree {tree.commit_sha} holds ZERO in-scope source "
            f"files. An empty corpus reports zero findings and looks exactly like a clean "
            f"one, so it is refused rather than audited (non-vacuity floor, AI-E11-1)."
        )
    dest.mkdir(parents=True, exist_ok=True)
    blobs = _read_blobs(checkout, [entry.blob_sha for entry in tree.files])
    for entry in tree.files:
        target = dest / entry.path
        _refuse_long_path(target)
        data = blobs.get(entry.blob_sha)
        if data is None:
            raise PinnedBytesRefusal(
                f"{checkout}: blob {entry.blob_sha} for {entry.path!r} was not returned by "
                f"`git cat-file --batch` at pin {tree.commit_sha}"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return dest


def verify_pinned_bytes(root: Path, tree: PinnedTree) -> PinVerification:
    """PROVE the bytes under *root* are the pinned bytes — by count AND by blob hash.

    This is the loud half of the fix. It answers the question the old runner never asked:
    not *"is this checkout on the right commit"* but *"are the bytes I am about to audit the
    bytes the manifest pins"*. A file that is missing (the ``MAX_PATH`` truncation) or whose
    content differs by one byte (a working-tree edit that leaked in) is NAMED.
    """
    missing: list[str] = []
    mismatched: list[str] = []
    verified = 0
    for entry in tree.files:
        target = root / entry.path
        try:
            data = target.read_bytes()
        except OSError:
            missing.append(entry.path)
            continue
        if blob_sha1(data) != entry.blob_sha:
            mismatched.append(entry.path)
            continue
        verified += 1
    return PinVerification(
        method=(
            "git ls-tree -r <pin> enumerates the in-scope blobs; git cat-file --batch reads "
            "them from the object database; every materialized file is re-hashed with git's "
            "own blob identity and compared to the id ls-tree reported"
        ),
        commit_sha=tree.commit_sha,
        expected_file_count=len(tree.files),
        verified_file_count=verified,
        missing_paths=tuple(sorted(missing)),
        mismatched_paths=tuple(sorted(mismatched)),
    )


#: Porcelain-v1 status letters whose entry is followed by a SECOND, BARE record carrying the
#: ORIGIN path. ``R`` (rename) is emitted by default; ``C`` (copy) wherever a checkout sets
#: ``status.renames=copies``. Both are ordinary configurations of an ordinary repository, and
#: both break any parser that assumes every record starts with ``XY ``.
_ORIGIN_FOLLOWS = frozenset({"C", "R"})


@dataclass(frozen=True)
class PorcelainEntry:
    """One ``git status --porcelain -z`` entry: its ``XY`` status and the path(s) it names."""

    status: str
    path: str
    origin_path: str | None = None

    @property
    def paths(self) -> tuple[str, ...]:
        """Every path this entry names — two of them for a rename or a copy."""
        if self.origin_path is None:
            return (self.path,)
        return (self.path, self.origin_path)


def parse_porcelain_z(stream: str) -> tuple[PorcelainEntry, ...]:
    """Parse a decoded ``git status --porcelain -z`` *stream*. Pure (AR8): no I/O, no clock.

    **The record boundary is not uniform, and assuming it is corrupts paths.** An ordinary
    entry is ``XY <path>`` — two status letters, a space, then the path, NUL-terminated. A
    RENAME or COPY is **two** records: ``XY <new-path>`` and then the origin path **bare,
    with no ``XY `` prefix at all**. Slicing every record at ``[3:]`` therefore removes the
    first three characters of every origin path, rendering ``pkg/alpha.py`` as ``/alpha.py``.

    Splitting on NUL is what makes the rest safe: ``-z`` suppresses ``core.quotepath``
    escaping, so a path containing spaces, quotes or non-ASCII bytes is emitted literally and
    needs no unquoting — but only because the separator can never occur inside a path.

    A record that is neither a well-formed entry nor an expected origin is a REFUSAL
    (:class:`PinnedSnapshotError`), never a silent slice: this function's failure mode was a
    quietly wrong path, and a wrong recorded fact is worse than a loud one.
    """
    records = stream.split("\0")
    entries: list[PorcelainEntry] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue  # the trailing field after the final NUL terminator
        if len(record) < 4 or record[2] != " ":
            raise PinnedSnapshotError(
                f"`git status --porcelain -z` emitted a record this parser cannot read: "
                f"{record!r}. A porcelain-v1 entry is `XY <path>`; the only record without "
                f"that prefix is the origin half of a rename or a copy, and this one does "
                f"not follow an R/C entry."
            )
        status, path = record[:2], record[3:]
        origin: str | None = None
        if status[0] in _ORIGIN_FOLLOWS or status[1] in _ORIGIN_FOLLOWS:
            # An EMPTY next field is the truncated case too, not a nameless origin: the
            # split leaves one empty trailing field after the final NUL, so a stream cut
            # short after the rename entry lands here rather than at the end of `records`.
            origin = records[index] if index < len(records) else ""
            index += 1
            if not origin:
                raise PinnedSnapshotError(
                    f"`git status --porcelain -z` ended after the rename/copy entry "
                    f"{record!r} without the origin-path record that must follow it. The "
                    f"stream is truncated, and a partial parse would under-report."
                )
        entries.append(PorcelainEntry(status=status, path=path, origin_path=origin))
    return tuple(entries)


def dirty_in_scope_paths(checkout: Path, *, keep: Callable[[str], bool]) -> tuple[str, ...]:
    """In-scope source paths that are dirty in *checkout* — recorded as EVIDENCE, not a gate.

    Under working-tree materialization these were a silent corruption of the measurement.
    Under pinned-object materialization they cannot enter the snapshot at all, and
    :func:`verify_pinned_bytes` proves it file by file. They are still recorded, because
    *"the tree was dirty and it provably did not matter"* is a stronger statement than
    *"the tree was clean"*, and it is the one a reader can check.
    """
    done = _git(checkout, "status", "--porcelain", "-z", "--untracked-files=all")
    if done.returncode != 0:
        raise PinnedSnapshotError(
            f"{checkout}: `git status --porcelain` failed "
            f"({done.stderr.decode('utf-8', 'replace').strip()!r})"
        )
    entries = parse_porcelain_z(done.stdout.decode("utf-8", errors="replace"))
    paths = {path for entry in entries for path in entry.paths if keep(path)}
    return tuple(sorted(paths))
