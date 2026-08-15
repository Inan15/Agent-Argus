"""PURE, CLOSED registry of the assistant hosts ``argus install-commands`` can write to.

Story 12.7 / FR35, decision DN-2. The story did not hand this module a host list to
trust, and that was deliberate: ``README.md`` named **seven** hosts while the repository
held **six** stub directories under ``adapters/``, one of the seven (RooCode) had no
adapter at all, and every one of the six was a two-to-three-line placeholder that
registered nothing. Six stubs are not a delivery, and a registry entry for a host whose
file-drop convention nobody verified is a promise the tool cannot keep.

So the rule this module enforces structurally is: **an entry exists only if its exact
configuration directory and its exact resulting spelling were verified.** Adding a host
is one entry here, one line in the README table that is DERIVED from this registry (never
hand-typed — ``tests/test_command_assets.py``), and nothing else: no new asset, no new
code path, no second placement mechanism.

Today the registry has exactly one member, ``claude-code``, whose convention this
repository itself demonstrates in-tree: a markdown file dropped in the personal
``~/.claude/commands/`` directory becomes the slash command ``/<file stem>``. The five
hosts removed from the README under AC4 are removed because no verified convention
existed for them here, not because they are unsupportable — each is one reviewed entry
away.

PURE (AR8): no filesystem access, no environment read, no clock, no network. Detection
and writing are the installer's thin impure shell.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "HOST_REGISTRY",
    "AssistantHost",
    "UnknownHostError",
    "host_ids",
    "resolve_hosts",
]


class UnknownHostError(ValueError):
    """A ``--host`` name that is not in this CLOSED registry (AR10 — typed, never silent).

    A ``ValueError`` subclass, like every other typed failure in this package, so the CLI's
    existing single ``except ValueError`` arm maps it to a secret-safe stderr line and the
    reserved exit code ``1`` with no new handling and no traceback.
    """


@dataclass(frozen=True)
class AssistantHost:
    """One assistant whose command directory this tool is allowed to write into.

    ``config_root_parts`` and ``commands_parts`` are POSIX-ish path SEGMENTS rather than a
    joined string on purpose: they are joined against a destination root by the installer,
    which is the single place containment is enforced. Storing a joined literal would
    invite an absolute path or a ``..`` segment to be smuggled in as data.
    """

    #: Stable machine name; the value ``--host`` accepts.
    host_id: str
    #: Human name, used only in messages.
    label: str
    #: Segments of the host's configuration root, relative to the user's home directory.
    config_root_parts: tuple[str, ...]
    #: Segments, relative to ``config_root_parts``, of the directory commands are read from.
    commands_parts: tuple[str, ...]
    #: How the verified convention was established, recorded so an entry cannot be added
    #: on a guess. ``tests/test_command_assets.py`` asserts every entry carries one.
    convention: str

    def command_spelling(self, asset_stem: str) -> str:
        """The EXACT text a user types once *asset_stem* has been placed for this host.

        Derived from the shipped asset's own filename, which is what makes the README's
        published spelling a derivation rather than a hand-typed claim (DN-4). The
        published ``/audit repo`` *space-separated argument* form was never produced by
        anything and is not preserved: what a reader is told is what the host gives them.
        """
        return f"/{asset_stem}"


#: The CLOSED registry. Adding a member is a deliberate, reviewed edit — never a fallback,
#: never inferred from the filesystem. ``resolve_hosts`` refuses anything not in here.
HOST_REGISTRY: tuple[AssistantHost, ...] = (
    AssistantHost(
        host_id="claude-code",
        label="Claude Code",
        config_root_parts=(".claude",),
        commands_parts=("commands",),
        convention=(
            "VERIFIED 2026-08-15 against the convention this repository itself carries "
            "in-tree: personal commands are markdown files under `~/.claude/commands/`, "
            "and a file `<stem>.md` there is invoked as `/<stem>`. The two committed "
            "installer scripts BOTH got this wrong in the same way — each created "
            "`~/.claude/commands/` and then copied the adapter files BESIDE it, into "
            "`~/.claude/` — which is the measured defect this story repairs, and the "
            "reason the destination is now resolved in one pure fold instead of twice in "
            "shell."
        ),
    ),
)


def host_ids() -> tuple[str, ...]:
    """Every registered ``--host`` value, sorted (PURE)."""
    return tuple(sorted(host.host_id for host in HOST_REGISTRY))


def resolve_hosts(requested: tuple[str, ...] | None) -> tuple[AssistantHost, ...]:
    """Resolve requested host ids against the registry, in registry order (PURE).

    ``None`` / empty means *every registered host* — the caller then narrows that to the
    ones actually detected. An unregistered name raises :class:`UnknownHostError` rather
    than being ignored: silently skipping a misspelled ``--host`` would report success for
    a step that placed nothing, which is the exact shape ``install.sh``'s Cline branch had
    (it incremented its counter and copied no file at all).
    """
    if not requested:
        return HOST_REGISTRY
    known = {host.host_id: host for host in HOST_REGISTRY}
    unknown = sorted({name for name in requested if name not in known})
    if unknown:
        raise UnknownHostError(
            f"unknown --host value(s) {unknown}; this build supports {list(host_ids())}"
        )
    wanted = set(requested)
    return tuple(host for host in HOST_REGISTRY if host.host_id in wanted)
