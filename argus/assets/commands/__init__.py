"""THE one command-asset tree: the ``*.md`` files a host reads to offer an Argus command.

Story 12.7 / FR35. Each sibling ``.md`` here is a single assistant command: a description
plus the literal ``argus audit …`` invocation it instructs the host to run, and nothing
else. They are DATA (see :mod:`argus.assets`) — no shell beyond that one invocation, no
network call, no credential, and no interpolation construct that could splice
consumer-controlled text onto a command line (Story 11.3 shipped a whole story about that
class on ``action.yml``; here it is a gate rather than a review note).

The tree is the SOURCE OF TRUTH for the published command set. ``tests/test_command_assets.py``
derives the shipped set from these filenames and asserts every surface that publishes a
command list equals it, in both directions; ``TC-ArgusAgent-DOCS-001-28`` hands every
``argus …`` line inside these files to the REAL ``build_parser().parse_args``, so a command
that would fail for a reader fails the build first.

Each asset carries two inert markers, and both are load-bearing:

``<!-- argus-command-asset: v1 -->``
    Identifies the file as a command asset. Exactly one directory in this repository may
    contain marker-bearing files (asserted), which is what stops a second, drifting copy
    of the command set from being introduced anywhere else.

``<!-- argus:instrument-status -->``
    Where the installer RENDERS the FR34 instrument-status disclosure at write time. The
    text is never committed here: a committed transcription of a pinned constant is the
    AI-E9-7 drift class, and it would go stale the day Epic 13 clears the precision gate.
    An asset without the placeholder is refused by the installer with a typed error.
"""

from __future__ import annotations

__all__ = [
    "ASSET_MARKER",
    "ASSET_SUFFIX",
    "DISCLOSURE_PLACEHOLDER",
]

#: Identifies a file as an Argus command asset. Declared HERE, beside the files that carry
#: it, so the format has one owner: the installer imports this name rather than spelling
#: the literal a second time, and `tests/test_command_assets.py` closes over it to assert
#: that exactly one directory in the repository holds marker-bearing files.
ASSET_MARKER = "<!-- argus-command-asset: v1 -->"

#: Where the installer RENDERS the FR34 instrument-status disclosure at write time. The
#: text itself is never committed here (AI-E9-7); an asset missing this placeholder is
#: refused by the installer with a typed error rather than written without the disclosure.
DISCLOSURE_PLACEHOLDER = "<!-- argus:instrument-status -->"

#: The only file extension this tree ships. A name that is not `<stem>.md` is not an asset.
ASSET_SUFFIX = ".md"
