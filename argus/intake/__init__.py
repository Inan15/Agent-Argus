"""ArgusAgent repository-intake sub-package (IMPURE shell).

Drivers: ArgusAgent-FR-1 (headless repo intake @ pinned commit), ArgusAgent-FR-2 (stack /
toolchain auto-detection, no operator config), AR8 (pure/impure separation —
``intake/`` is the impure shell; its RESULT models are frozen pure contracts),
AR10 (typed failure at the impure shell — never an uncaught raise).

Modules:
- :mod:`argus.intake.repo_loader` — load a repo @ a pinned commit,
  refusing a drifted working tree (FR1); frozen ``RepoIntake`` result.
- :mod:`argus.intake.stack_detect` — no-config stack / toolchain
  auto-detection (FR2); frozen ``StackProfile`` result.

The architecture classifies ``intake/`` as the impure shell: it reads files and
invokes ``git`` / ``radon``. All filesystem and subprocess I/O is confined here;
the result DATA models are frozen, construction-pure Pydantic v2 contracts.
"""

from __future__ import annotations

__all__: list[str] = []
