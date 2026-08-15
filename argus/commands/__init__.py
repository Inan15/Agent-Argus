"""The ``argus install-commands`` step: place the packaged command assets, and remove them.

Story 12.7 / FR35 (second half). :mod:`argus.assets.commands` ships the assets; this
package is the ONE mechanism that puts them where an assistant reads them, and the one
that takes them away again.

Layout, and why it is split this way (AR8 — pure/impure separation is a mandate here,
not a preference):

``argus.commands.hosts``
    A CLOSED, PURE registry. One entry per supported assistant, each naming the exact
    configuration directory it reads commands from and the exact spelling a user ends up
    typing. No I/O, no detection, no writing.

``argus.commands.installer``
    A PURE fold — assets × hosts × destination root → a fully resolved, ordered plan of
    ``(path, bytes)`` writes — plus a THIN impure shell that detects which hosts are
    present and performs the plan. Everything that can be decided without touching the
    filesystem is decided in the fold, which is what makes every containment rule and
    every rendered byte testable without a real ``$HOME``.

``argus/cli.py`` holds no logic for any of this: NFR-M1 says the entry point carries no
business logic, and 12.6 set the precedent of a thin adapter over a reused core. The entry
point declares the ``install-commands`` arguments, hands them to
:func:`argus.commands.installer.install_commands`, prints
:func:`argus.commands.installer.render_outcome`'s lines, and maps a typed failure to the
existing exit-code contract — nothing else.

**DN-8: this package does NOT write assistant host configuration for the agent-integration
transport Story 12.6 shipped.** That snippet stays documentation in ``README.md``. Naming
it here would put its token into a ``.py`` under ``argus/`` and make this module an
unregistered disclosure surface for ``TC-ArgusAgent-DOCS-001-49``, for no user benefit —
12.6's own ruling, applied: a false registry entry is worse than a coy docstring.
"""

from __future__ import annotations

__all__: list[str] = []
