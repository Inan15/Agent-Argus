"""Per-run on-disk artifact materialization with workspace-root containment.

Story 18-2 (E18-S2) — the SECOND link in the Epic 18 execution-plane chain
(18-1 live dispatch -> 18-2 on-disk artifacts -> 18-3 real merge+test). This is
the single filesystem-I/O point that turns content-bearing developer-subtask
output (the live ``WorkerAgentResult.output`` channel from 18-1) into real,
inspectable on-disk source files.

Architecture drivers:
  - MIN-FR-ART-001.04 (content-bearing on-disk artifacts — ratified by the
    approved §3.5 amendment Section 2 / ADR #20 Decision 2).
  - MIN-NFR-SEC-001 / MIN-NFR-SEC-002 (workspace path-traversal containment —
    every write is confined to a per-run subtree of a configured root).

Containment (the security keystone, DN-4): the candidate path is resolved with
``Path.resolve()`` (which normalises ``..`` and follows symlinks) and asserted
``is_relative_to`` the resolved workspace root — NOT a naive string-prefix check
(a ``str.startswith`` test lets ``/root/ws-evil`` defeat the ``/root/ws`` root).
A containment violation raises ``WorkspaceContainmentError`` BEFORE any
filesystem mutation. The ``run_id`` is part of the path and is validated too.

Opt-in (DN-2): a writer constructed with an empty root is ``enabled == False``
and is never asked to materialize by the dispatch wiring, so unconfigured
environments are byte-identical to pre-18-2.

Honest failure (DN-7): a containment violation raises before any write; an
unexpected OS error on a legitimately-confined path is allowed to propagate
(fail-loud — a run that cannot persist its source is not a successful delivery).
The writer NEVER fabricates a content-locator for a file it did not write and
NEVER returns silently on a partial write. The writer is DOWNSTREAM of the HTTP
A2A boundary (ADR #20 Boundary note): it takes no token and self-verifies
nothing.
"""

from __future__ import annotations

from pathlib import Path


class WorkspaceContainmentError(ValueError):
    """Raised when a materialization target escapes the workspace root.

    Subclasses ``ValueError`` so existing ``except ValueError`` callers still
    catch it (DN-5). The message names the offending relative path but NEVER
    echoes the file content (CC-5 spirit).
    """


class WorkspaceArtifactWriter:
    """Writes developer-subtask content to a confined per-run workspace.

    Constructed with the workspace-root path resolved from ``MinionsSettings``
    (``MINIONS_WORKSPACE_ROOT``, ADR #7 / §3.8) — never a hardcoded literal. An
    empty root disables the writer (``enabled == False``); the dispatch wiring
    skips materialization entirely in that case (opt-in, AC4).
    """

    def __init__(self, workspace_root: str) -> None:
        self._root_str = str(workspace_root or "")
        # Resolve once at construction so containment checks compare against a
        # stable, symlink-normalised absolute root.
        self._resolved_root: Path | None = (
            Path(self._root_str).resolve() if self._root_str else None
        )

    @property
    def enabled(self) -> bool:
        """True when a non-empty workspace root is configured (opt-in)."""
        return self._resolved_root is not None

    def materialize(self, run_id: str, relative_path: str, content: str) -> str:
        """Write *content* to ``<root>/<run_id>/<relative_path>`` (confined).

        Returns the **content-locator** — the workspace-root-relative POSIX path
        of the written file (DN-3), so the locator is portable across host moves
        (the absolute root is reconstructable from settings) and no absolute
        host path leaks into committed evidence.

        Raises:
            WorkspaceContainmentError: if the target resolves outside the
                workspace root (``../`` traversal, an absolute ``relative_path``
                or ``run_id``, a ``..``-only segment, a symlink escape). Raised
                BEFORE any filesystem mutation.
            OSError: if the write fails on a legitimately-confined path
                (permission denied, disk full, a blocking non-directory). The
                error propagates — no fabricated locator, no silent partial.
        """
        if self._resolved_root is None:
            raise WorkspaceContainmentError(
                "workspace materialization disabled: no workspace root configured"
            )

        root = self._resolved_root
        candidate = (root / str(run_id) / str(relative_path)).resolve()

        if not self._is_contained(candidate, root):
            raise WorkspaceContainmentError(
                f"path '{run_id}/{relative_path}' escapes workspace root"
            )

        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text(content, encoding="utf-8")

        return candidate.relative_to(root).as_posix()

    @staticmethod
    def _is_contained(candidate: Path, root: Path) -> bool:
        """True iff *candidate* is the root itself or strictly within it.

        Uses real path containment (``is_relative_to``), NOT a string-prefix
        check — the DN-CC-8 (b) guard against a sibling-prefixed escape.
        """
        try:
            c = candidate.resolve()
            r = root.resolve()
            if c.drive and r.drive:
                if c.drive.upper() == r.drive.upper():
                    c = Path(c.drive.upper() + str(c)[len(c.drive):])
                    r = Path(r.drive.upper() + str(r)[len(r.drive):])
            return c.is_relative_to(r) and c != r
        except (ValueError, RuntimeError):
            return False
