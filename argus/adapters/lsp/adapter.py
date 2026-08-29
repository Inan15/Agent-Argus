"""Finding to LSP Diagnostic Mapper for ArgusAgent findings (Story 20.3).

Drivers: ArgusAgent-FR-39 (IDE & LSP diagnostic surface), ArgusAgent-FR-13
(locator-or-reject mapping), AR8 (PURE mapping, zero I/O).

Why this module exists
----------------------
Converts ArgusAgent findings (such as ``Recording`` rows and ``FindingDraft`` objects)
into LSP 3.17 ``LSPDiagnostic`` instances, mapping 1-based line spans into 0-based
LSP range positions and translating Argus finding severity grades into LSP diagnostic
severities.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from argus.adapters.lsp.models import (
    LSPDiagnostic,
    LSPDiagnosticSeverity,
    LSPPosition,
    LSPRange,
)

if TYPE_CHECKING:
    from argus.detectors.base import FindingDraft
    from argus.ledger.coverage_ledger import CoverageDepth
    from argus.ledger.recording import Recording

__all__ = [
    "file_path_to_uri",
    "map_severity",
    "LSPDiagnosticAdapter",
]


def file_path_to_uri(file_path: str, workspace_root: str = ".") -> str:
    """Convert a file path to a standard ``file:///`` URI format.

    Handles absolute paths, relative paths (resolved against ``workspace_root``),
    and already-formatted ``file://`` URIs. Normalizes Windows path separators.
    """
    if file_path.startswith("file://"):
        return file_path
    path = Path(file_path)
    if not path.is_absolute():
        path = (Path(workspace_root) / path).resolve()
    return path.as_uri()


def map_severity(
    advisory: bool,
    depth_supported: CoverageDepth | str | None = None,
) -> LSPDiagnosticSeverity:
    """Map Argus advisory/blocking flags and coverage depth to LSPDiagnosticSeverity.

    - Non-advisory blocking findings (advisory == False) -> ERROR (1)
    - Advisory findings with supported coverage depth -> WARNING (2)
    - Advisory shallow/heuristic findings -> INFORMATION (3)
    """
    if not advisory:
        return LSPDiagnosticSeverity.ERROR
    if depth_supported is not None:
        return LSPDiagnosticSeverity.WARNING
    return LSPDiagnosticSeverity.INFORMATION


class LSPDiagnosticAdapter:
    """Mapper translating ArgusAgent ledger/detector findings into LSP diagnostics."""

    @staticmethod
    def map_recording(
        recording: Recording,
        workspace_root: str = ".",
        message: str | None = None,
    ) -> LSPDiagnostic:
        """Map a ``Recording`` to an ``LSPDiagnostic`` instance.

        Uses the primary locator's 1-based line span to compute 0-based LSP positions.
        """
        locator = recording.locators[0]
        start_line_0 = max(0, locator.start_line - 1)
        end_line_0 = max(0, locator.end_line - 1)

        diag_range = LSPRange(
            start=LSPPosition(line=start_line_0, character=0),
            end=LSPPosition(line=end_line_0, character=0),
        )
        severity = map_severity(recording.advisory, recording.depth_supported)
        diag_message = (
            message
            if message is not None
            else f"[{recording.rule_id}] Finding {recording.recording_id} (advisory={recording.advisory})"
        )

        return LSPDiagnostic(
            range=diag_range,
            severity=severity,
            code=recording.rule_id,
            source="ArgusAgent",
            message=diag_message,
        )

    @staticmethod
    def map_draft(
        draft: FindingDraft,
        workspace_root: str = ".",
        depth_supported: CoverageDepth | str | None = None,
        message: str | None = None,
    ) -> LSPDiagnostic:
        """Map a ``FindingDraft`` to an ``LSPDiagnostic`` instance."""
        start_line_0 = max(0, draft.start_line - 1)
        end_line_0 = max(0, draft.end_line - 1)

        diag_range = LSPRange(
            start=LSPPosition(line=start_line_0, character=0),
            end=LSPPosition(line=end_line_0, character=0),
        )
        severity = map_severity(draft.advisory, depth_supported)
        diag_message = (
            message
            if message is not None
            else f"[{draft.rule_id}] Finding in {draft.file_path} (advisory={draft.advisory})"
        )

        return LSPDiagnostic(
            range=diag_range,
            severity=severity,
            code=draft.rule_id,
            source="ArgusAgent",
            message=diag_message,
        )

    @classmethod
    def map_recordings_by_uri(
        cls,
        recordings: Sequence[Recording],
        workspace_root: str = ".",
    ) -> dict[str, list[LSPDiagnostic]]:
        """Map a sequence of recordings into a dict of URI -> list[LSPDiagnostic]."""
        by_uri: dict[str, list[LSPDiagnostic]] = defaultdict(list)
        for rec in recordings:
            locator = rec.locators[0]
            uri = file_path_to_uri(locator.file_path, workspace_root)
            diag = cls.map_recording(rec, workspace_root)
            by_uri[uri].append(diag)
        return dict(by_uri)
