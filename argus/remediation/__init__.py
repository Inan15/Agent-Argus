"""Defect remediation package (`argus.remediation`).

Drivers: Story 20.2 (Defect Remediation Engine).
"""

from __future__ import annotations

from argus.remediation.engine import (
    RemediationEngine,
    apply_patch,
    apply_unified_diff,
    verify_patch_dry_run,
)
from argus.remediation.models import RemediationPatch, RemediationResult

__all__ = [
    "RemediationEngine",
    "RemediationPatch",
    "RemediationResult",
    "apply_patch",
    "apply_unified_diff",
    "verify_patch_dry_run",
]
