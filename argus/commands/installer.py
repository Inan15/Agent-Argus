"""The ``argus install-commands`` mechanism: resolve a plan (PURE), then write it (IMPURE).

Story 12.7 / FR35 (second half). :mod:`argus.assets.commands` ships the assets; this module
is the ONE mechanism that places them where an assistant reads them, and the one that takes
them away again (AR7 / architecture §3.3 — a second placement mechanism is the fork this
story exists to close, and there were two of them: ``install.sh`` and ``install.ps1`` each
created ``~/.claude/commands/`` and then copied the adapter files BESIDE it).

AR8, and it is a MANDATE here rather than a preference
------------------------------------------------------
Everything that can be decided without touching a filesystem is decided in the PURE fold —
which assets exist, which hosts they go to, what each written file's exact bytes are, and
whether any of it would escape the destination root. The IMPURE shell is three narrow
functions: read the packaged assets, detect which hosts are present, and perform the plan.
That split is what makes every containment rule and every rendered byte testable against a
``tmp_path`` and never against a real ``$HOME``.

Reading the assets goes through :mod:`importlib.resources` over a real package, never
``Path(__file__).parent`` arithmetic: the latter happens to work from a source checkout and
breaks the moment the distribution is zip-imported, relocated or vendored.

FR34, and why the disclosure is RENDERED rather than committed (DN-7 / AI-E9-7)
-------------------------------------------------------------------------------
A command asset emits no verdict — the CLI it invokes carries its own disclosure — but the
description is what an agent reads BEFORE it decides to run anything, which is exactly the
reason Story 12.6 put the same disclosure in the ``tools/list`` description one story
earlier. So every asset this module writes carries it, rendered at write time from the ONE
constant in :mod:`argus.verdict.negative_assurance`. No committed file under
``argus/assets/**`` contains that text at all: a committed transcription of a pinned
constant is the AI-E9-7 drift class, and it would go stale the day Epic 13's Story 13.3
flips the status. Re-running the step then produces the new text (and a stale installed
asset is detectable, because a written asset is byte-identical for identical inputs).

Containment (NFR-S4/NFR-S5), split across the two halves for the reason above
-----------------------------------------------------------------------------
This is the only place Argus writes outside the audited repository at all, so the write set
is closed twice. The PURE half refuses an asset name that is absolute, carries a path
separator or a ``..`` segment — a name is a NAME, never a path. The IMPURE half re-checks
the real filesystem: every write's parent directory must resolve INSIDE the resolved
destination root, so a symlinked ``commands/`` directory pointing somewhere else is refused
rather than followed. Both raise :class:`CommandInstallError`, which is a ``ValueError``
subclass, so ``argus/cli.py``'s existing typed arm maps it to a secret-safe stderr line and
the reserved exit code ``1`` with no new handling and no traceback (AR3/AR10/NFR-R1).

Determinism and containment of AUTHORITY (NFR-P1, architecture §A constraint 2.3): the
rendered bytes are a pure function of the packaged asset and the pinned constant — no clock,
no ``uuid``/``random``, no ``float``, no network — and the assets grant nothing the CLI
lacks, because their entire executable content is an ``argus audit …`` invocation the real
parser accepts (asserted by ``TC-ArgusAgent-DOCS-001-28`` and ``-ASSETS-001-02``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from argus.assets.commands import ASSET_MARKER, ASSET_SUFFIX, DISCLOSURE_PLACEHOLDER
from argus.commands.hosts import AssistantHost, resolve_hosts
from argus.verdict.negative_assurance import (
    INSTRUMENT_STATUS,
    render_instrument_disclosure,
)

__all__ = [
    "ASSET_PACKAGE",
    "CommandAsset",
    "CommandInstallError",
    "ContainmentError",
    "InstallOutcome",
    "PlannedWrite",
    "default_destination_root",
    "detect_hosts",
    "install_commands",
    "load_command_assets",
    "plan_writes",
    "render_asset",
    "render_outcome",
]

#: The importable package the assets live in. Named once; every read resolves through it.
ASSET_PACKAGE = "argus.assets.commands"


class CommandInstallError(ValueError):
    """A TYPED failure of the install step (AR10 — never a bare exception, never a traceback).

    A ``ValueError`` subclass so ``argus/cli.py``'s single existing typed arm maps it to a
    secret-safe stderr line and the reserved exit code ``1``. Every message names the
    reason and a DESTINATION-RELATIVE path only — never an absolute host path (NFR-S1).
    """


class ContainmentError(CommandInstallError):
    """A planned write that would land outside the resolved destination root (NFR-S4/S5).

    Separate from the base class because it is the one failure that means *the step tried
    to write somewhere it was never allowed to*, and a reader of a refusal should be able
    to tell that from "your config directory is read-only".
    """


@dataclass(frozen=True)
class CommandAsset:
    """One packaged command asset, as read from the distribution (immutable, inert data)."""

    #: The file name as it ships, e.g. ``argus-audit.md``. A NAME, never a path.
    name: str
    #: The committed text, placeholder included and disclosure NOT included.
    text: str

    @property
    def stem(self) -> str:
        """The name without its suffix — the token a host turns into a command spelling."""
        return self.name[: -len(ASSET_SUFFIX)]


@dataclass(frozen=True)
class PlannedWrite:
    """One fully resolved write: which host, which destination-relative path, which bytes.

    ``relative_parts`` is kept as SEGMENTS rather than a joined string because joining is
    where an absolute path or a ``..`` sneaks in, and the join happens in exactly one place
    (:func:`_resolve_target`) so there is a single site to audit.
    """

    host_id: str
    relative_parts: tuple[str, ...]
    content: str

    @property
    def relative_path(self) -> str:
        """The destination-relative POSIX path, for messages and for tests (never absolute)."""
        return "/".join(self.relative_parts)


@dataclass(frozen=True)
class InstallOutcome:
    """What the step did, as data — so the CLI only has to print it (AR8).

    ``written`` / ``removed`` / ``unchanged`` hold DESTINATION-RELATIVE paths, which is what
    makes every line this produces secret-safe by construction (NFR-S1): there is no
    absolute host path in the structure at all, so none can reach a message.
    """

    action: str  # "install" | "dry-run" | "remove"
    host_ids: tuple[str, ...]
    written: tuple[str, ...]
    removed: tuple[str, ...]
    unchanged: tuple[str, ...]


# ─────────────────────────────────────────────────────────────────────────────
# PURE — the fold. No filesystem, no environment, no clock, no network.
# ─────────────────────────────────────────────────────────────────────────────


def _validate_asset_name(name: str) -> None:
    """Refuse an asset name that is a PATH rather than a name (PURE, containment half one).

    An asset ships as ``<stem>.md`` and is written into one directory. Anything with a
    separator, a ``..`` segment, a drive letter or a leading root is not that, and it is the
    cheapest way to make a write land outside the destination root. Refused before anything
    is joined, because a check performed after the join is a check performed on the escape.
    """
    if not name.endswith(ASSET_SUFFIX) or len(name) <= len(ASSET_SUFFIX):
        raise ContainmentError(
            f"command asset {name!r} is not a `<stem>{ASSET_SUFFIX}` file name"
        )
    if "/" in name or "\\" in name or os.sep in name or (os.altsep or "") in name:
        raise ContainmentError(
            f"command asset {name!r} carries a path separator; an asset name is a NAME, "
            "never a path, and a path here is how a write escapes the destination root"
        )
    if name in (".", "..") or ".." in Path(name).parts or Path(name).is_absolute():
        raise ContainmentError(
            f"command asset {name!r} is absolute or carries a `..` segment; refused before "
            "it is joined to any destination"
        )


def render_asset(asset: CommandAsset, disclosure: str) -> str:
    """Return the exact text to write for *asset*, with the FR34 disclosure in place (PURE).

    The ONLY transformation: the committed placeholder becomes a markdown block quote
    carrying *disclosure*. Deterministic — same asset plus same constant gives byte-identical
    output forever (NFR-P1), which is what makes a STALE installed asset detectable after
    Story 13.3 flips the instrument status: the bytes on disk stop equalling the bytes this
    function now produces.

    An asset that does not carry the placeholder is REFUSED rather than written without the
    disclosure. Writing it silently would produce exactly the surface FR34 exists to prevent
    — one an agent reads before it acts, with no statement of how the tool's own findings
    have been validated.
    """
    if DISCLOSURE_PLACEHOLDER not in asset.text:
        raise CommandInstallError(
            f"command asset {asset.name!r} carries no {DISCLOSURE_PLACEHOLDER!r} "
            "placeholder, so the FR34 instrument-status disclosure has nowhere to be "
            "rendered; the asset is refused rather than written without it"
        )
    if ASSET_MARKER not in asset.text:
        raise CommandInstallError(
            f"command asset {asset.name!r} carries no {ASSET_MARKER!r} marker, so neither "
            "`--remove` nor the one-tree guard can recognise it as ours"
        )
    return asset.text.replace(DISCLOSURE_PLACEHOLDER, f"> {disclosure}")


def plan_writes(
    assets: tuple[CommandAsset, ...],
    hosts: tuple[AssistantHost, ...],
    disclosure: str,
) -> tuple[PlannedWrite, ...]:
    """Fold assets x hosts into the complete, ORDERED set of writes (PURE).

    Ordered by ``(host_id, asset name)`` so the plan — and therefore ``--dry-run``'s output
    and the written set — is identical on every host and every run (NFR-P1). Every name is
    validated before it is joined to anything.
    """
    if not assets:
        raise CommandInstallError(
            "no command assets were resolved from "
            f"{ASSET_PACKAGE!r}; the distribution ships none, so there is nothing to place"
        )
    if not hosts:
        raise CommandInstallError(
            "no assistant host was resolved, so this step would place nothing while "
            "reporting success; name one with --host, or run it where a supported "
            "assistant's configuration directory exists"
        )
    planned: list[PlannedWrite] = []
    for host in sorted(hosts, key=lambda h: h.host_id):
        for asset in sorted(assets, key=lambda a: a.name):
            _validate_asset_name(asset.name)
            planned.append(
                PlannedWrite(
                    host_id=host.host_id,
                    relative_parts=(
                        *host.config_root_parts,
                        *host.commands_parts,
                        asset.name,
                    ),
                    content=render_asset(asset, disclosure),
                )
            )
    return tuple(planned)


def render_outcome(outcome: InstallOutcome) -> tuple[str, ...]:
    """Render the human-readable report for *outcome* (PURE).

    Kept out of ``argus/cli.py`` so the entry point only has to print what it is given
    (NFR-M1 — no business logic in the entry point) and so every line is assertable without
    capturing a stream. SECRET-SAFE BY CONSTRUCTION: :class:`InstallOutcome` holds only
    destination-relative paths, so no absolute host path can reach a line here (NFR-S1).
    """
    verb = {
        "install": "wrote",
        "dry-run": "would write",
        "remove": "removed",
    }[outcome.action]
    touched = outcome.removed if outcome.action == "remove" else outcome.written
    lines = [
        f"argus: install-commands {outcome.action}: {verb} {len(touched)} command "
        f"file(s) for host(s) {list(outcome.host_ids)}"
    ]
    lines.extend(f"  {verb}: {path}" for path in touched)
    lines.extend(f"  unchanged (not ours, left alone): {path}" for path in outcome.unchanged)
    return tuple(lines)


# ─────────────────────────────────────────────────────────────────────────────
# IMPURE — three narrow functions: read the package, look at the disk, write.
# ─────────────────────────────────────────────────────────────────────────────


def load_command_assets() -> tuple[CommandAsset, ...]:
    """Read every packaged command asset through :mod:`importlib.resources` (IMPURE read).

    Never ``Path(__file__)`` arithmetic — see the module docstring. Sorted, so the caller
    inherits a deterministic order rather than the filesystem's.
    """
    found: list[CommandAsset] = []
    for entry in resources.files(ASSET_PACKAGE).iterdir():
        if not entry.name.endswith(ASSET_SUFFIX):
            continue
        found.append(
            CommandAsset(name=entry.name, text=entry.read_text(encoding="utf-8"))
        )
    return tuple(sorted(found, key=lambda asset: asset.name))


def default_destination_root() -> Path:
    """The destination root when ``--dest`` is not given: the user's home directory (IMPURE).

    Isolated in its own function so that every guard in the suite can drive the whole step
    against a ``tmp_path`` without ever reading — let alone writing — a real ``$HOME``.
    """
    return Path.home()


def detect_hosts(
    root: Path, hosts: tuple[AssistantHost, ...]
) -> tuple[AssistantHost, ...]:
    """Narrow *hosts* to the ones whose configuration root exists under *root* (IMPURE read).

    Detection is a PRESENCE question and nothing more: the directory an assistant keeps its
    configuration in either exists or it does not. It reads; it creates nothing. An
    explicitly named ``--host`` skips this narrowing on purpose (see
    :func:`install_commands`) — an operator naming a host is making the statement detection
    would otherwise infer.
    """
    return tuple(
        host for host in hosts if (root.joinpath(*host.config_root_parts)).is_dir()
    )


def _resolve_target(root: Path, write: PlannedWrite) -> Path:
    """Join *write* onto *root* and re-check containment against the REAL filesystem (IMPURE).

    Containment half two, and the half a pure check cannot do: ``..`` and absolute names are
    already gone, but a symlink is a property of the disk. The parent directory's REAL path
    must sit inside the destination root's REAL path, so a ``commands/`` directory that is a
    symlink to somewhere else is refused instead of followed — and an existing target that
    is itself a symlink is refused rather than written through.
    """
    root_real = Path(os.path.realpath(root))
    target = root.joinpath(*write.relative_parts)
    parent_real = Path(os.path.realpath(target.parent))
    if parent_real != root_real and root_real not in parent_real.parents:
        raise ContainmentError(
            f"refusing to write {write.relative_path!r}: it resolves outside the "
            "destination root (a `..` segment, an absolute name, or a symlinked "
            "configuration directory pointing elsewhere)"
        )
    if target.is_symlink():
        raise ContainmentError(
            f"refusing to write {write.relative_path!r}: the target is a symlink, and "
            "writing through it would place the file wherever it points"
        )
    return target


def _is_ours(path: Path) -> bool:
    """Does *path* carry the command-asset marker? (IMPURE read; refuses on unreadable.)

    The predicate ``--remove`` and the overwrite rule both stand on: this step removes and
    replaces exactly what it wrote, and leaves a user's own file of the same name entirely
    alone. An unreadable or non-UTF-8 file is NOT ours, which is the safe answer.
    """
    try:
        return ASSET_MARKER in path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False


def install_commands(
    *,
    dest: str = "",
    requested_hosts: tuple[str, ...] = (),
    dry_run: bool = False,
    remove: bool = False,
) -> InstallOutcome:
    """Place (or remove) the packaged command assets. The whole impure shell (AR8).

    ``dest`` overrides the host-configuration ROOT — the directory the registry's
    ``config_root_parts`` are relative to — which is the seam every guard in this suite
    drives so no test ever touches a real ``$HOME``. An empty ``dest`` means
    :func:`default_destination_root`.

    ``requested_hosts`` empty means *every registered host that is DETECTED*; naming hosts
    explicitly skips detection, because an operator naming one has already made the
    statement detection would infer. An unregistered name raises
    :class:`~argus.commands.hosts.UnknownHostError` rather than being skipped: silently
    ignoring a misspelled ``--host`` reports success for a step that placed nothing, which
    is precisely the shape ``install.sh``'s Cline branch had — it incremented its counter
    and copied no file at all.

    Every failure is TYPED and secret-safe (NFR-R1): an undetected host, an unwritable
    destination, a missing asset, an escaping path and a pre-existing file that is not ours
    are each a named outcome, never a traceback.
    """
    root = Path(dest) if dest else default_destination_root()
    hosts = resolve_hosts(requested_hosts or None)
    if not requested_hosts:
        hosts = detect_hosts(root, hosts)
    disclosure = render_instrument_disclosure(INSTRUMENT_STATUS, short=True)
    plan = plan_writes(load_command_assets(), hosts, disclosure)
    host_ids = tuple(sorted({write.host_id for write in plan}))

    if remove:
        return _apply_removals(root, plan, host_ids)
    return _apply_writes(root, plan, host_ids, dry_run=dry_run)


def _apply_writes(
    root: Path, plan: tuple[PlannedWrite, ...], host_ids: tuple[str, ...], *, dry_run: bool
) -> InstallOutcome:
    """Perform (or, for ``--dry-run``, decline to perform) every planned write (IMPURE).

    ``--dry-run`` resolves containment for every target exactly as a real run does and then
    writes nothing at all — a dry run that skipped the checks would report a plan the real
    run refuses.

    A pre-existing file that is NOT ours is left untouched and reported, rather than
    overwritten: this step owns the files it wrote and nothing else. One that IS ours is
    rewritten, which is what makes re-running the step after Story 13.3 flips the instrument
    status the documented way to refresh a stale disclosure.
    """
    written: list[str] = []
    unchanged: list[str] = []
    for write in plan:
        target = _resolve_target(root, write)
        if target.exists() and not _is_ours(target):
            unchanged.append(write.relative_path)
            continue
        if dry_run:
            written.append(write.relative_path)
            continue
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(write.content)
        except OSError as exc:
            raise CommandInstallError(
                f"could not write {write.relative_path!r} under the destination root: "
                f"{exc.strerror or exc.__class__.__name__}"
            ) from exc
        written.append(write.relative_path)
    return InstallOutcome(
        action="dry-run" if dry_run else "install",
        host_ids=host_ids,
        written=tuple(written),
        removed=(),
        unchanged=tuple(unchanged),
    )


def _apply_removals(
    root: Path, plan: tuple[PlannedWrite, ...], host_ids: tuple[str, ...]
) -> InstallOutcome:
    """Delete exactly what this step wrote, and nothing else (IMPURE).

    This is the asymmetry ``uninstall.sh`` carried: it ran ``pip uninstall`` only, so every
    file the two installers copied stayed in the user's home directory forever. Removal is
    closed over the SAME plan the install is closed over and gated on the marker, so a file
    the user wrote themselves under one of our names survives.
    """
    removed: list[str] = []
    unchanged: list[str] = []
    for write in plan:
        target = _resolve_target(root, write)
        if not target.exists():
            continue
        if not _is_ours(target):
            unchanged.append(write.relative_path)
            continue
        try:
            target.unlink()
        except OSError as exc:
            raise CommandInstallError(
                f"could not remove {write.relative_path!r} under the destination root: "
                f"{exc.strerror or exc.__class__.__name__}"
            ) from exc
        removed.append(write.relative_path)
    return InstallOutcome(
        action="remove",
        host_ids=host_ids,
        written=(),
        removed=tuple(removed),
        unchanged=tuple(unchanged),
    )
