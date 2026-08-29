"""Base interfaces and protocols for defect remediation (PURE).

Drivers: Story 20.2 (Defect Remediation Engine).
"""

from __future__ import annotations

from argus.remediation.models import RemediationPatch, RemediationResult

__all__ = [
    "RemediationPatch",
    "RemediationResult",
]
