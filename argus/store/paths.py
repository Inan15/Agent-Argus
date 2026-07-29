""".argus/ fixed runtime tree + containment-checked path resolver (IMPURE shell).

Drivers: ArgusAgent-NFR-S5 (every filesystem write is containment-checked —
``Path.resolve()`` + ``is_relative_to``, never ``str.startswith``; an escape
raises a typed error BEFORE any FS mutation), ArgusAgent-NFR-P1 (the fixed ``.argus/``
tree + content-addressed filenames make two hosts produce identically-named
files), AR7 (REUSE Minions' canonical containment authority by import — no fork),
AR10 (typed failure at the impure shell — no bare ``except: pass``, no ``print()``),
AR11 (the fixed ``.argus/`` runtime tree; filenames from content-sha256 / a stable
assignment-id, never arrival order).

Containment is the security keystone (architecture cross-cutting #5)
-------------------------------------------------------------------
ArgusAgent writes into ``.argus/`` rooted INSIDE a repository it does not control
(including, on the operated-service path, a customer's repo). A path-traversal /
symlink-escape / absolute-path / sibling-prefix bug at this exact seam would let
an audit write outside its sandbox. The architecture mandates reuse of Minions'
``lifecycle/workspace_artifact_writer`` containment pattern.

Reuse decision (architecture Decision F — recorded here per the story)
----------------------------------------------------------------------
``WorkspaceArtifactWriter.materialize`` is hard-wired to a
``<root>/<run_id>/<relative_path>`` shape and always writes UTF-8 *text*. The
``.argus/`` store is content-addressed (``<sha>.json``), writes canonical *bytes*
(``canonical.dumps_bytes`` — the single serializer, AR4), and is rooted at a
``.argus/`` dir inside an arbitrary audited repo. Injecting the ``.argus/`` root and
mapping ``run_id``/``relative_path`` onto a content-addressed byte write is a poor
fit. Per Decision F ("thin-wrap if root injection is unsupported") we therefore
**thin-wrap**: we REUSE the canonical :class:`WorkspaceContainmentError` typed
error AND mirror its EXACT containment LOGIC (resolve-once root,
``candidate.resolve()``, ``is_relative_to`` + ``!= root``, ``except ValueError:
return False``) — with NO second/divergent containment implementation and NO fork
of the helper (§3.3 reuse-canonical). The shared invariant (``is_relative_to``,
never ``str.startswith``) is the property the import-isolation + containment gates
pin.
"""

from __future__ import annotations

from pathlib import Path

from argus.shared.workspace_containment import WorkspaceContainmentError

__all__ = [
    "ArgusAgent_DIR_NAME",
    "ArgusAgent_SUBDIRS",
    "WorkspaceContainmentError",
    "ApaaStorePaths",
]

# The fixed ``.argus/`` directory name, rooted inside the audited repo (AR11).
ArgusAgent_DIR_NAME = ".argus"

# The EXACT architecture-fixed sub-directory set (architecture §Runtime artifact
# tree). ``cache/`` is a directory only in V1 — the memoization LOGIC is Epic 5.
ArgusAgent_SUBDIRS: tuple[str, ...] = (
    "state",
    "assignments",
    "findings",
    "decisions",
    "cache",
)


def _is_contained(candidate: Path, root: Path) -> bool:
    """True iff *candidate* is strictly within *root* (mirror of the Minions helper).

    Real path containment via ``is_relative_to`` — NEVER a ``str.startswith``
    prefix check (which a sibling-prefixed dir ``.argus-evil`` vs ``.argus``
    defeats). Identical logic to
    ``WorkspaceArtifactWriter._is_contained`` (AR7 reuse-canonical, no fork).
    """
    try:
        return candidate.is_relative_to(root) and candidate != root
    except ValueError:
        return False


class ApaaStorePaths:
    """Containment-checked resolver for the ``.argus/`` tree under an audited repo.

    Constructed with the audited-repo root; resolves the ``.argus/`` root ONCE
    (symlink-normalised, absolute) so every sub-path is checked against a stable
    root (NFR-S5). The resolver itself performs no payload write — directory
    creation (``ensure_tree`` / ``ensure_parent``) happens ONLY after the
    containment check passes; the byte write lives in :mod:`store.writer`.
    """

    def __init__(self, repo_root: str | Path) -> None:
        self._repo_root = Path(repo_root)
        # Resolve the ``.argus/`` root once. ``strict=False`` so the root need not
        # pre-exist (we may create it); ``..`` is normalised and symlinks on the
        # existing prefix are followed.
        self._argus_root: Path = (self._repo_root / ArgusAgent_DIR_NAME).resolve()

    @property
    def argus_root(self) -> Path:
        """The resolved absolute ``.argus/`` root (containment reference)."""
        return self._argus_root

    def resolve(self, relative_path: str | Path) -> Path:
        """Resolve a ``.argus/``-relative sub-path, containment-checked (NFR-S5).

        Returns the resolved absolute target. Raises
        :class:`WorkspaceContainmentError` BEFORE any filesystem mutation when the
        candidate escapes the ``.argus/`` root via ``../`` traversal, an absolute
        sub-path, a ``..``-only segment, a symlink whose target escapes the root,
        a sibling-prefixed sibling dir (``.argus-evil`` vs ``.argus``), a
        Windows-backslash traversal, or a drive-letter absolute. The message names
        the offending RELATIVE path only — never file content / an absolute host
        path (NFR-S1 spirit, AR10).
        """
        rel = Path(relative_path)
        if rel.is_absolute():
            raise WorkspaceContainmentError(
                f"path '{relative_path}' escapes .argus root (absolute sub-path)"
            )
        candidate = (self._argus_root / rel).resolve()
        if not _is_contained(candidate, self._argus_root):
            raise WorkspaceContainmentError(
                f"path '{relative_path}' escapes .argus root"
            )
        return candidate

    def ensure_tree(self) -> Path:
        """Idempotently create the ``.argus/`` root + the fixed sub-dirs (AR11).

        Creates ``.argus/`` and EXACTLY ``state/ assignments/ findings/ decisions/
        cache/`` with ``mkdir(parents=True, exist_ok=True)``. Returns the
        ``.argus/`` root. Pure-of-payload (no artifact bytes written here).
        """
        self._argus_root.mkdir(parents=True, exist_ok=True)
        for sub in ArgusAgent_SUBDIRS:
            (self._argus_root / sub).mkdir(parents=True, exist_ok=True)
        return self._argus_root

    def ensure_parent(self, relative_path: str | Path) -> Path:
        """Containment-check ``relative_path`` then create its parent dir.

        Returns the resolved absolute target. Directory creation happens ONLY
        after the containment check passes (no dir creation on an escaping path).
        """
        target = self.resolve(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def to_locator(self, relative_path: str | Path) -> str:
        """Return the ``.argus/``-root-relative POSIX locator (never absolute).

        Containment-checked first (a non-contained path cannot produce a
        locator). Mirrors the ``WorkspaceArtifactWriter`` DN-3 decision: persisted
        / returned locators are root-relative POSIX, so no absolute host path
        leaks into evidence (NFR-S1 spirit).
        """
        target = self.resolve(relative_path)
        return target.relative_to(self._argus_root).as_posix()
