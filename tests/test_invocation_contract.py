"""Story 10.3 / AC6 — the invocation contract equals what the parser accepts, both ways.

Verification area ArgusAgent-CLI (``TC-ArgusAgent-CLI-001-35``..``-41``, CONTINUING the index
whose prior maximum is ``-34``) plus ``TC-ArgusAgent-DOCS-001-28`` for AC6.4 (the documented
invocations must actually run; ``-01``..``-27`` belong to the release-note, evidence-citation and
spec-claim guards).

**The defect under repair (``DF-AUD-APAA-E``).** Four CLI flags were accepted by the shipped parser
and specified nowhere. Re-measured on 2026-08-10 against the binding contract corpus
(``E-PRD/prd.md``, ``E-PRD/addendum.md``, ``architecture.md``, ``epics.md``, ``CHANGELOG.md``,
``README.md``) the number is **six**: ``--reports`` (entered in ``084c6a7``, the same 426-file
separation seed as the ledger's four, and *depended on* by
``.github/workflows/argus-student-audit.yml:48``) and ``--strict`` (entered in ``ae5f00c``; named in
``cli.py`` as the binding statement of the FR1 determinism pin) have zero occurrences in that corpus
either. The ledger's enumeration was a hand-counted list, and a hand-counted list has now been the
wrong instrument three stories running.

**Why this file exists rather than a corrected list** (story DN-2). 10.2's guard had to infer a claim
shape from prose with a tuned regex. This one does not need to: ``argus.cli.build_parser`` is
*exactly* enumerable, so the left-hand side is DERIVED at run time and the comparison is an
**equality**, not a heuristic. There is therefore no defensible route to a seventh instance — a flag
added to the parser without a registry entry and a real contract site turns this file red.

**A red test here is this guard WORKING, not a defect.** When ``--deep`` (FR36, Story 12.2) or an
MCP-era flag lands, ``-35`` fails until it is registered with the contract site that specifies it.
That is the whole point: registration is a deliberate edit, and an unregistered flag is precisely the
defect ``DF-AUD-APAA-E`` records.

**Five known ways a guard like this lies, and what stops each.**

1. *It hand-types the flags it checks* (AI-E8-6: all five Epic-8 stories shipped a guard narrower
   than their own AC). Stopped by ``-35``: the left-hand side is walked off the live parser and the
   assertion is a symmetric difference.
2. *It checks names only, so a default or a shape drifts underneath it.* Stopped by ``-37``, which
   compares default AND shape and requires every divergence to be a named exemption with a reason
   (DN-8's ``coverage_scope`` case) rather than silence — the ``_PRESERVED_RECORD`` anti-pattern
   10.1's DN-5 ruled on.
3. *It checks only that the parser is registered, never that the registration is true.* Stopped by
   ``-38``: every registry entry names contract site(s) BY ANCHOR TEXT and the anchor must be
   findable in that file. A registry is not a contract; a document is.
4. *Its own enumeration silently collapses to nothing.* ``_subparsers`` / ``_group_actions`` /
   ``_actions`` are **argparse private API** — acceptable inside a test, but a future argparse could
   turn the walk into an empty list and every set comparison above would pass vacuously. Stopped by
   ``-39``, which is not optional.
5. *It is only ever run after the fix* (AI-E3-1: Story 3.4's keystone test was green over its own
   keystone bug). Every assertion here was demonstrated RED against the unamended contract before the
   amendments landed; the run is recorded in the story's Dev Agent Record.

Plus the ``-17b`` escape (Epic 9, found by review not by the author): a comparison that swallows what
it looks for. Stopped by ``-40``, a positive control in **both** directions over **synthetic**
parsers — the real parser is never mutated.

**No network, no LLM, no subprocess, no ``.argus/`` write** — pure ``argparse`` introspection +
``pathlib``/``re``/``shlex`` over committed files, so it runs identically on all three CI legs
(10.1/10.2 precedent). Every file is opened ``encoding="utf-8"`` explicitly: the artifact tree
carries ``~~``, ``⚠️``, ``🚩`` and Cyrillic, and an inherited host locale is the exact defect class
that turned run ``31322881580`` red.
"""

from __future__ import annotations

import argparse
import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path

from argus import cli

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"

_GUARD_FILE = "tests/test_invocation_contract.py"


def _read(relative: str) -> str:
    """Read a committed file as text, ALWAYS explicitly utf-8 (never the host locale)."""
    return (_REPO_ROOT / relative).read_text(encoding="utf-8")


def _read_artifact(relative: str) -> str:
    """Read a planning artifact as text, ALWAYS explicitly utf-8."""
    return (_ARTIFACT_DIR / relative).read_text(encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Shapes — the vocabulary the registry uses to describe an accepted flag
# ─────────────────────────────────────────────────────────────────────────────

SHAPE_POSITIONAL = "positional"
SHAPE_VALUE = "value"
SHAPE_STORE_TRUE = "store_true"
SHAPE_APPEND = "append"
SHAPE_INT = "int"
SHAPE_CHOICE = "choice"


def describe_shape(action: argparse.Action) -> str:
    """Classify an argparse action into the registry's shape vocabulary (PURE).

    Derived from the action itself, never from its spelling, so a flag that changes from
    ``store_true`` to a value flag (or gains ``choices``, or loses ``type=int``) moves shape and
    ``-37`` fails until the registry is edited deliberately.
    """
    if not action.option_strings:
        return SHAPE_POSITIONAL
    if isinstance(action, argparse._StoreTrueAction):  # noqa: SLF001 - argparse has no public probe
        return SHAPE_STORE_TRUE
    if isinstance(action, argparse._AppendAction):  # noqa: SLF001 - same
        return SHAPE_APPEND
    if action.choices:
        return SHAPE_CHOICE
    if action.type is int:
        return SHAPE_INT
    return SHAPE_VALUE


@dataclass(frozen=True)
class DerivedArgument:
    """One argument as the LIVE parser accepts it — derived, never transcribed."""

    spelling: str
    dest: str
    default: object
    shape: str
    choices: tuple[str, ...] = ()
    #: Which sub-command(s) accept it. Recorded from 2026-08-15 (Story 12.7) so the walk can be a
    #: closure over EVERY sub-command without losing which one an argument came from — `-39` uses
    #: it to prove the closure really reached more than one, and `conflicting_arguments` uses the
    #: same information to refuse a spelling that would mean two different things.
    subcommands: tuple[str, ...] = ()


def subcommands(parser: argparse.ArgumentParser) -> tuple[str, ...]:
    """Every sub-command *parser* declares, read off ``_SubParsersAction.choices`` (PURE).

    CORRECTED 2026-08-15 by Story 12.7, and the correction is the point rather than a tidy-up.
    ``derive_arguments`` used to take a hand-named ``subcommand`` and **every one of its five call
    sites passed the literal ``"audit"``**. A second sub-command's flags were therefore invisible to
    ``-35`` (parser↔contract equality), ``-37`` (defaults and shapes) and ``-38`` (every flag names
    a findable contract site) — so the day ``install-commands`` landed, four accepted flags would
    have been specified nowhere and *nothing in this file would have gone red*. That is
    ``DF-AUD-APAA-E`` itself, reconstructed by the guard written to close it, and it is verbatim the
    ``_CONSOLE_SCRIPTS`` / ``_ENTRY_POINT`` defect class Story 12.6 found twice: a derivation narrow
    enough to miss the next surface. The population is now a CLOSURE over the parser.
    """
    found: list[str] = []
    for action in parser._actions:  # noqa: SLF001 - argparse exposes no public walk
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001 - same
            found.extend(
                name
                for name, sub in action.choices.items()
                if isinstance(sub, argparse.ArgumentParser)
            )
    return tuple(sorted(set(found)))


def derive_arguments(
    parser: argparse.ArgumentParser, subcommand: str | None = None
) -> dict[str, DerivedArgument]:
    """Every accepted argument, keyed by spelling (PURE). ``None`` = EVERY sub-command.

    Uses argparse private API (``_subparsers`` / ``_group_actions`` / ``_actions``) — see the module
    docstring's failure mode 4 and ``-39``, which is the countermeasure. ``-h/--help`` is excluded:
    it is argparse's own, is not part of the product's invocation contract, and its prose is Story
    12.8's. A positional is keyed by its ``dest``.

    The default is the CLOSURE (see :func:`subcommands`): a sub-command added to ``build_parser``
    brings its flags into ``-35``/``-37``/``-38`` with no edit here, which is the only arrangement
    under which "an unregistered flag is red" stays true of the whole tool rather than of one
    sub-command. An explicit *subcommand* is still accepted, because ``-40``'s positive controls
    exercise these helpers over SYNTHETIC parsers and want to name the one they built.

    Each entry records which sub-command(s) accept it. A spelling defined DIFFERENTLY by two
    sub-commands cannot be represented by one registry entry, so it is not silently merged —
    :func:`conflicting_arguments` finds it and ``-39`` fails on it.
    """
    subparsers_actions = [
        action
        for action in parser._actions  # noqa: SLF001 - argparse exposes no public walk
        if isinstance(action, argparse._SubParsersAction)  # noqa: SLF001 - same
    ]
    derived: dict[str, DerivedArgument] = {}
    for subparsers_action in subparsers_actions:
        for name, sub in subparsers_action.choices.items():
            if subcommand is not None and name != subcommand:
                continue
            if not isinstance(sub, argparse.ArgumentParser):
                continue
            for action in sub._actions:  # noqa: SLF001 - same
                if isinstance(action, argparse._HelpAction):  # noqa: SLF001 - same
                    continue
                spelling = action.option_strings[0] if action.option_strings else action.dest
                seen = derived.get(spelling)
                derived[spelling] = DerivedArgument(
                    spelling=spelling,
                    dest=action.dest,
                    default=action.default,
                    shape=describe_shape(action),
                    choices=tuple(str(c) for c in (action.choices or ())),
                    subcommands=(*(seen.subcommands if seen else ()), name),
                )
    return derived


def conflicting_arguments(parser: argparse.ArgumentParser) -> tuple[str, ...]:
    """Spellings two sub-commands accept with DIFFERENT defaults/shapes/choices (PURE).

    The closure in :func:`derive_arguments` keys by spelling, because the contract registry — and
    ``cli.py``'s own contract block — talk about spellings. That is honest only while a spelling
    means one thing across the whole tool. If it ever does not, one of the two definitions would be
    silently dropped from the comparison and the registry would describe a flag some invocation does
    not have. So the collision is DETECTED rather than assumed away, before it can happen.
    """
    problems: list[str] = []
    for name in subcommands(parser):
        for spelling, argument in derive_arguments(parser, name).items():
            for other in subcommands(parser):
                if other <= name:
                    continue
                rival = derive_arguments(parser, other).get(spelling)
                if rival is None:
                    continue
                if (argument.default, argument.shape, argument.choices) != (
                    rival.default,
                    rival.shape,
                    rival.choices,
                ):
                    problems.append(
                        f"{spelling}: {name} accepts it as "
                        f"({argument.default!r}, {argument.shape}, {argument.choices}) while "
                        f"{other} accepts it as ({rival.default!r}, {rival.shape}, {rival.choices})"
                    )
    return tuple(sorted(problems))


# ─────────────────────────────────────────────────────────────────────────────
# THE CONTRACT REGISTRY — edited deliberately, never generated
# ─────────────────────────────────────────────────────────────────────────────
#
# `sites` names the document(s) that SPECIFY the flag, each as "<path>::<anchor text>". The anchor
# is matched as a substring, never as a line number: every number in this project drifts under the
# amendment cascade (the epic's own citation of "architecture L226" had moved to :303 by the time
# this story ran). `-38` fails if an anchor cannot be found, so a registry entry cannot claim a
# specification that does not exist.
#
# Paths are resolved relative to the REPO ROOT, except those prefixed `artifact:`, which resolve
# under _bmad-output/design-artifacts/ArgusAgent/.


@dataclass(frozen=True)
class ContractEntry:
    """One argument as the CONTRACT specifies it, with the site(s) that specify it."""

    spelling: str
    dest: str
    default: object
    shape: str
    sites: tuple[str, ...]
    choices: tuple[str, ...] = ()
    exemption: str = ""
    notes: str = field(default="")


# The in-code contract statement closest to the code (AC5.4). Every accepted flag must appear in
# `cli.py`'s own "LOCKED CLI contract" docstring block: it is the statement a maintainer reads
# first, and commit `230bf5c` repaired one paragraph of it while leaving six flags out entirely.
_CLI_BLOCK = "argus/cli.py::LOCKED-CLI-CONTRACT-BLOCK"

# FR30 — the binding capability contract. Its ORIGINAL four-parameter wording is struck rather than
# deleted (PRD §3.4 evidence immutability), so this anchor survives the amendment by design.
_FR30 = "artifact:E-PRD/prd.md::repo + commit + budget + materiality_bar"

# The release-note section that SPECIFIES the `install-commands` sub-command and its four
# arguments (Story 12.7 / FR35). Registered in `_NOTE_SECTIONS` where `-16` pins ORDER, not just
# membership, so this anchor cannot be satisfied by an unreviewed heading.
_INSTALL_SECTION = "CHANGELOG.md::### Added — `argus install-commands`"

CONTRACT_REGISTRY: tuple[ContractEntry, ...] = (
    ContractEntry(
        spelling="repo",
        dest="repo",
        default=None,
        shape=SHAPE_POSITIONAL,
        sites=(_FR30, _CLI_BLOCK),
        notes="FR30's `repo` parameter; Story 1.7 LOCKED the positional shape.",
    ),
    ContractEntry(
        spelling="--commit",
        dest="commit",
        default="HEAD",
        shape=SHAPE_VALUE,
        sites=(_FR30, _CLI_BLOCK),
        notes="FR30's `commit` parameter; the FR1 determinism pin, ENFORCED by --strict.",
    ),
    ContractEntry(
        spelling="--strict",
        dest="strict",
        default=False,
        shape=SHAPE_STORE_TRUE,
        sites=("CHANGELOG.md::### Specified: `--strict`", _CLI_BLOCK),
        notes="Story 10.3 / DN-5. The FR1 determinism lever; entered in `ae5f00c` unspecified.",
    ),
    ContractEntry(
        spelling="--budget",
        dest="budget",
        default=0,
        shape=SHAPE_INT,
        sites=(_FR30, _CLI_BLOCK),
        notes="FR30's `budget` parameter; OI3 — 0/omitted is a first-class NO ceiling.",
    ),
    ContractEntry(
        spelling="--materiality-bar",
        dest="materiality_bar",
        default="",
        shape=SHAPE_VALUE,
        sites=(_FR30, _CLI_BLOCK),
        notes="FR30's `materiality_bar` parameter; recorded, not applied in V1.",
    ),
    ContractEntry(
        spelling="--critical-subsystem",
        dest="critical_subsystem",
        default=None,
        shape=SHAPE_APPEND,
        sites=(
            "artifact:E-PRD/prd.md::`--critical-subsystem` designation",
            _CLI_BLOCK,
        ),
        notes="FR4 operator designation (Story 2.3).",
    ),
    ContractEntry(
        spelling="--exclude-critical",
        dest="exclude_critical",
        default=None,
        shape=SHAPE_APPEND,
        sites=(
            "artifact:epics.md::`--exclude-critical` matches **by prefix**",
            _CLI_BLOCK,
        ),
        notes="FR4 operator exclusion (Story 2.3); exclude wins on a tie.",
    ),
    ContractEntry(
        spelling="--passes",
        dest="passes",
        default=None,
        shape=SHAPE_VALUE,
        sites=("CHANGELOG.md::### Specified: `--passes` and `--skip-pass`", _CLI_BLOCK),
        notes="Story 10.3 / DN-3. Entered in `084c6a7` unspecified; blessed, behaviour unchanged.",
    ),
    ContractEntry(
        spelling="--skip-pass",
        dest="skip_pass",
        default=None,
        shape=SHAPE_APPEND,
        sites=("CHANGELOG.md::### Specified: `--passes` and `--skip-pass`", _CLI_BLOCK),
        notes="Story 10.3 / DN-3. Composes one-way: a skip cannot re-add an excluded pass.",
    ),
    ContractEntry(
        spelling="--reports",
        dest="reports",
        default=None,
        shape=SHAPE_VALUE,
        sites=("CHANGELOG.md::### Specified: `--reports` and `--report-dir`", _CLI_BLOCK),
        notes="Story 10.3 / DN-4. CONDITIONALLY INERT: renders nothing without --report-dir.",
    ),
    ContractEntry(
        spelling="--report-dir",
        dest="report_dir",
        default="",
        shape=SHAPE_VALUE,
        sites=(
            "README.md::Report generation (`--report-dir`)",
            "CHANGELOG.md::### Specified: `--reports` and `--report-dir`",
            _CLI_BLOCK,
        ),
        notes="AC7.3 — thin-but-present in README/action.yml, thickened by Story 10.3.",
    ),
    ContractEntry(
        spelling="--ignore-path",
        dest="ignore_paths",
        default=[],
        shape=SHAPE_APPEND,
        sites=(
            "CHANGELOG.md::### Specified: `--ignore-path` and `--ignore-pattern`",
            "artifact:architecture.md::Suppression threat model",
            _CLI_BLOCK,
        ),
        notes="Story 10.3 / DN-5. Bounded by the Live-Key Safeguard; bless conditional on AC4.",
    ),
    ContractEntry(
        spelling="--ignore-pattern",
        dest="ignore_patterns",
        default=[],
        shape=SHAPE_APPEND,
        sites=(
            "CHANGELOG.md::### Specified: `--ignore-path` and `--ignore-pattern`",
            "artifact:architecture.md::Suppression threat model",
            _CLI_BLOCK,
        ),
        notes="Story 10.3 / DN-6. Blessed because AC4 landed: it now sits BELOW the safeguard "
        "and an operator-attributable suppression is recorded and disclosed.",
    ),
    ContractEntry(
        spelling="--deep-audit",
        dest="deep_audit",
        default=False,
        shape=SHAPE_STORE_TRUE,
        sites=("CHANGELOG.md::### Specified: `--deep-audit`", _CLI_BLOCK),
        notes="Story 12.2 / FR36. THE ONLY OPT-IN TO EGRESS, and the reason it is a registered "
        "FLAG rather than a `--passes` token, an environment variable or a packaging extra is "
        "measured, not stylistic: `--passes …,deep` was already accepted and already produced a "
        "FALSE DEEP CLAIM; `--passes` is an exact selection, so `--passes deep` alone would "
        "silently disable every deterministic safety pass; the `[llm]` extra gates only litellm "
        "while httpx is a BASE dependency; and OpenLLMAdapter absorbs six environment variables. "
        "Off by default, always (FR36). An unspecified accepted flag is `DF-AUD-APAA-E` itself.",
    ),
    ContractEntry(
        spelling="--coverage-scope",
        dest="coverage_scope",
        default="application",
        shape=SHAPE_CHOICE,
        choices=("repository", "application"),
        sites=("CHANGELOG.md::### Defaults: `--coverage-scope`", _CLI_BLOCK),
        exemption=(
            "DN-8 — DELIBERATE, DOCUMENTED DIVERGENCE, ruled on by name and pinned in BOTH "
            "directions rather than silently exempted. The CLI default is 'application' "
            "(CHANGELOG '### Defaults: `--coverage-scope`'); AuditRequest.coverage_scope's "
            "default is 'repository' (models.py, 'the V1 fold'). Both are shipped, ANNOUNCED "
            "surfaces, so changing either is a behavioural change to a published default and is "
            "beyond a specification-correction story. `-37b` pins the divergence itself, so it "
            "cannot drift silently in either direction and cannot be closed by accident."
        ),
        notes="A library consumer and a CLI consumer get different assessed populations by default.",
    ),
    # ── The `install-commands` sub-command (Story 12.7 / FR35, 2026-08-15) ──────────────────
    # These four entered with the SECOND sub-command, and they are the reason `derive_arguments`
    # had to stop being scoped to one hand-named sub-command: under the old walk all four would
    # have been accepted by the shipped parser and specified in no document, with this file green
    # — `DF-AUD-APAA-E` reconstructed by the guard that closes it. Each names the CHANGELOG
    # section that specifies it PLUS `cli.py`'s own contract block, the same two-site shape every
    # Story-10.3 entry uses.
    ContractEntry(
        spelling="--host",
        dest="host",
        default=None,
        shape=SHAPE_APPEND,
        sites=(_INSTALL_SECTION, _CLI_BLOCK),
        notes="Restricts the step to named hosts from the CLOSED registry in "
        "argus/commands/hosts.py. Omitted means every registered host that is DETECTED; naming "
        "one skips detection, because an operator naming a host has already made the statement "
        "detection would infer. An unregistered name is a typed refusal, never a silent skip — "
        "silently ignoring a misspelling would report success for a step that placed nothing, "
        "which is exactly the shape install.sh's Cline branch had.",
    ),
    ContractEntry(
        spelling="--dest",
        dest="dest",
        default="",
        shape=SHAPE_VALUE,
        sites=(_INSTALL_SECTION, _CLI_BLOCK),
        notes="Overrides the host-configuration ROOT the registry's paths are relative to; "
        "defaults to the user's home directory. THE TESTABILITY SEAM: every guard drives the real "
        "step against a tmp_path through this flag, so no test in this suite touches a real $HOME. "
        "Writes never leave the resolved root (`..`, an absolute asset name and a symlinked "
        "configuration directory are each a typed refusal).",
    ),
    ContractEntry(
        spelling="--dry-run",
        dest="dry_run",
        default=False,
        shape=SHAPE_STORE_TRUE,
        sites=(_INSTALL_SECTION, _CLI_BLOCK),
        notes="Resolves and containment-checks the whole plan, prints exactly what would be "
        "written, and writes nothing. It runs the SAME checks a real run runs — a dry run that "
        "skipped them would report a plan the real run refuses.",
    ),
    ContractEntry(
        spelling="--remove",
        dest="remove",
        default=False,
        shape=SHAPE_STORE_TRUE,
        sites=(_INSTALL_SECTION, _CLI_BLOCK),
        notes="Deletes exactly the files this step wrote — recognised by the marker each asset "
        "carries — and nothing else. It closes the asymmetry uninstall.sh had: it ran `pip "
        "uninstall` only, leaving every copied file in the user's home directory forever.",
    ),
)


def _registry_by_spelling() -> dict[str, ContractEntry]:
    return {entry.spelling: entry for entry in CONTRACT_REGISTRY}


# ─────────────────────────────────────────────────────────────────────────────
# Pure comparison helpers — the positive controls in `-40` exercise THESE, over
# synthetic parsers, so the control can never be satisfied by mutating the real one.
# ─────────────────────────────────────────────────────────────────────────────


def unregistered_and_unaccepted(
    derived: dict[str, DerivedArgument], registered: dict[str, ContractEntry]
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return ``(accepted-but-unregistered, registered-but-unaccepted)`` (PURE).

    Direction one is the ``DF-AUD-APAA-E`` defect itself (six flags the parser accepted and no
    document specified). Direction two is the defect the ledger never looked for and ``README:195``
    was carrying: a contract naming a flag the parser rejects.
    """
    return (
        tuple(sorted(set(derived) - set(registered))),
        tuple(sorted(set(registered) - set(derived))),
    )


def shape_divergences(
    derived: dict[str, DerivedArgument], registered: dict[str, ContractEntry]
) -> tuple[str, ...]:
    """Return a human-readable divergence per flag whose default/shape/choices moved (PURE)."""
    problems: list[str] = []
    for spelling, actual in sorted(derived.items()):
        entry = registered.get(spelling)
        if entry is None:
            continue
        if actual.default != entry.default:
            problems.append(
                f"{spelling}: parser default {actual.default!r} != contract default "
                f"{entry.default!r} (registry entry must be edited deliberately)"
            )
        if actual.shape != entry.shape:
            problems.append(
                f"{spelling}: parser shape {actual.shape!r} != contract shape {entry.shape!r}"
            )
        if actual.choices != entry.choices:
            problems.append(
                f"{spelling}: parser choices {actual.choices!r} != contract choices "
                f"{entry.choices!r}"
            )
    return tuple(problems)


def missing_sites(registered: dict[str, ContractEntry]) -> tuple[str, ...]:
    """Return one message per registry entry whose contract site cannot be found (PURE-ish I/O read).

    This is the assertion that makes the registry a *claim about documents* rather than a second
    hand-typed list. It reads committed files; it writes nothing.
    """
    problems: list[str] = []
    cli_block = locked_contract_block()
    for spelling, entry in sorted(registered.items()):
        if not entry.sites:
            problems.append(f"{spelling}: NO contract site named (AC6.2 requires at least one)")
            continue
        for site in entry.sites:
            path, _, anchor = site.partition("::")
            if site == _CLI_BLOCK:
                if spelling not in cli_block:
                    problems.append(
                        f"{spelling}: absent from cli.py's own 'LOCKED CLI contract' docstring "
                        f"block — the contract statement closest to the code (AC5.4)"
                    )
                continue
            if path.startswith("artifact:"):
                text = _read_artifact(path[len("artifact:") :])
            else:
                text = _read(path)
            if anchor not in text:
                problems.append(
                    f"{spelling}: contract site not found — anchor {anchor!r} is absent from "
                    f"{path} (the flag is accepted by the parser and specified nowhere)"
                )
    return tuple(problems)


def locked_contract_block() -> str:
    """Return `cli.py`'s own 'LOCKED CLI contract' docstring block (PURE over committed source).

    Scoped to the DOCSTRING, never the whole module: every flag spelling trivially appears in the
    ``add_argument`` calls below, so matching the file would assert nothing at all. Located by
    anchor text, not by line number.
    """
    source = _read("argus/cli.py")
    start_anchor = "The LOCKED CLI contract"
    start = source.find(start_anchor)
    assert start != -1, (
        "argus/cli.py no longer contains its 'The LOCKED CLI contract' docstring heading — "
        "the in-code contract statement this guard reads has been removed or renamed"
    )
    end = source.find('"""', start)
    assert end != -1, "cli.py's module docstring is unterminated after the LOCKED contract heading"
    return source[start:end]



# ─────────────────────────────────────────────────────────────────────────────
# AC6.4 — the documented invocations must actually run
# ─────────────────────────────────────────────────────────────────────────────
#
# MOVED 2026-08-15 by Story 12.7 to `tests/invocation_sources.py`, along the cohesion boundary this
# file already had, because adding the shipped command-asset tree to the corpus pushed this module
# past the NFR-M1 1200-line ceiling. The remedy the ceiling guard itself prescribes is a split into
# a sibling module with a re-export and EVERY IMPORT PATH UNCHANGED — not shaved lines and not a
# narrowed population — so every name below is re-exported here and
# `from tests.test_invocation_contract import executable_line_numbers` resolves exactly as before.
# The tests that USE them stay in this file: `-28` is a Story-10.3 assertion and belongs beside the
# rest of the contract, and `-39`'s non-vacuity floor spans both halves by design.
from tests.invocation_sources import (  # noqa: E402,F401 - re-export, import path preserved
    _ASSET_GLOB,
    _CLI_ENTRY_TARGET,
    _CONSOLE_SCRIPT_TARGETS,
    _CONSOLE_SCRIPTS,
    _INVOCATION_SOURCES,
    _MCP_ENTRY_TARGET,
    _PLACEHOLDER,
    _PLACEHOLDER_RE,
    _RUN_HEADER_RE,
    _WORKFLOW_GLOB,
    DocumentedInvocation,
    console_script_targets,
    executable_line_numbers,
    extract_documented_invocations,
    parse_failure,
)

# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_CLI_001_35_every_accepted_flag_is_registered_and_vice_versa() -> None:
    """TC-ArgusAgent-CLI-001-35 — parser-vs-contract equality, in both directions.

    Story 10.3 / AC6.1, AC6.2, AC6.3 (`DF-AUD-APAA-E`).
    """
    derived = derive_arguments(cli.build_parser())
    registered = _registry_by_spelling()
    unregistered, unaccepted = unregistered_and_unaccepted(derived, registered)

    assert not unregistered, (
        "ACCEPTED BUT UNSPECIFIED — the parser accepts "
        f"{list(unregistered)} with no entry in CONTRACT_REGISTRY. This is the "
        "`DF-AUD-APAA-E` defect exactly: a flag reached users that no document specifies. "
        "Rule on it (bless with a behavioural AC + a CHANGELOG entry, or remove it) and register "
        f"it with the contract site that specifies it in {_GUARD_FILE}."
    )
    assert not unaccepted, (
        "SPECIFIED BUT UNACCEPTED — the contract registry claims "
        f"{list(unaccepted)}, which the live parser does not accept. This is the direction "
        "`README.md`'s `--materiality` carried into a consumer's terminal; fix the contract or "
        "the parser, do not delete the assertion."
    )


def test_TC_ArgusAgent_CLI_001_36_every_registered_spelling_actually_parses() -> None:
    """TC-ArgusAgent-CLI-001-36 — direction two, proven by parsing rather than by set membership.

    Story 10.3 / AC6.3. A spelling can be present in the argparse walk and still be unusable; the
    only honest proof that the contract names a REAL flag is to hand it to the real parser.
    """
    sample_for_shape = {
        SHAPE_VALUE: ["x"],
        SHAPE_INT: ["1"],
        SHAPE_APPEND: ["x"],
        SHAPE_CHOICE: None,  # filled from the registry's own choices
        SHAPE_STORE_TRUE: [],
    }
    # The sub-command a flag belongs to, and that sub-command's required positionals, are DERIVED
    # from the live parser rather than hand-typed (Story 12.7). The prefix used to be the literal
    # `"argus audit . "`, which was correct only while there was exactly one sub-command — the
    # same single-surface assumption `derive_arguments` carried, in a second place.
    parser = cli.build_parser()
    derived = derive_arguments(parser)
    positionals_by_subcommand = {
        name: [
            argument.dest
            for argument in derive_arguments(parser, name).values()
            if argument.shape == SHAPE_POSITIONAL
        ]
        for name in subcommands(parser)
    }
    failures: list[str] = []
    for entry in CONTRACT_REGISTRY:
        if entry.shape == SHAPE_POSITIONAL:
            continue
        if entry.shape == SHAPE_CHOICE:
            value = [entry.choices[0]] if entry.choices else ["x"]
        else:
            value = list(sample_for_shape[entry.shape] or [])
        accepting = derived[entry.spelling].subcommands
        for name in accepting:
            prefix = ["argus", name, *(["."] * len(positionals_by_subcommand[name]))]
            failure = parse_failure(shlex.join([*prefix, entry.spelling, *value]))
            if failure is not None:
                failures.append(f"{name} {entry.spelling}: {failure}")
    assert not failures, (
        "A CONTRACT SITE NAMES A FLAG THE PARSER REJECTS — " + "; ".join(failures)
    )


def test_TC_ArgusAgent_CLI_001_37_defaults_and_shapes_match_the_contract() -> None:
    """TC-ArgusAgent-CLI-001-37 — names are not enough: default and shape are compared too.

    Story 10.3 / AC6.7. A silent default change is a behavioural change to a published surface; it
    must cost a deliberate registry edit.
    """
    derived = derive_arguments(cli.build_parser())
    problems = shape_divergences(derived, _registry_by_spelling())
    assert not problems, "PARSER/CONTRACT DIVERGENCE:\n  " + "\n  ".join(problems)


def test_TC_ArgusAgent_CLI_001_37b_the_coverage_scope_divergence_is_pinned_both_ways() -> None:
    """TC-ArgusAgent-CLI-001-37b — DN-8's exemption is a PIN, not a hole.

    Story 10.3 / AC7.1. `--coverage-scope` defaults to `application` at the CLI and
    `AuditRequest.coverage_scope` defaults to `repository` in the library. Both are announced
    surfaces, so neither is changed here — but an exemption that merely suppresses an assertion is
    the `_PRESERVED_RECORD` anti-pattern 10.1's DN-5 ruled on. This asserts the divergence itself,
    so it can drift in NEITHER direction and cannot be closed by accident.
    """
    from argus.models import AuditRequest

    entry = _registry_by_spelling()["--coverage-scope"]
    assert entry.exemption, "DN-8's exemption must carry its reason, never bare silence"

    cli_default = derive_arguments(cli.build_parser())["--coverage-scope"].default
    library_default = AuditRequest.model_fields["coverage_scope"].default

    assert cli_default == "application", (
        f"the CLI default for --coverage-scope moved to {cli_default!r}; CHANGELOG "
        "'### Defaults: `--coverage-scope`' announces 'application' to CLI consumers"
    )
    assert library_default == "repository", (
        f"AuditRequest.coverage_scope's default moved to {library_default!r}; models.py describes "
        "'repository' as the V1 fold and test_sequential_portability.py repeats that wording"
    )
    assert cli_default != library_default, (
        "the CLI and library defaults now AGREE. That may well be an improvement, but it is a "
        "behavioural change to two published defaults (DN-8 fenced it to its own story with a "
        "migration note). If it was deliberate, amend the contract, DN-8 and this pin together."
    )


def test_TC_ArgusAgent_CLI_001_38_every_registered_flag_names_a_findable_contract_site() -> None:
    """TC-ArgusAgent-CLI-001-38 — a registry is not a contract; a document is.

    Story 10.3 / AC6.2, AC5.4. Every entry names its specifying site(s) by ANCHOR TEXT, and each
    anchor must be findable in that file. Run RED against the unamended contract this failed for
    exactly the six flags of the story's §A.1 — `--passes`, `--skip-pass`, `--reports`, `--strict`,
    `--ignore-path`, `--ignore-pattern`.
    """
    problems = missing_sites(_registry_by_spelling())
    assert not problems, (
        f"{len(problems)} FLAG(S) ARE ACCEPTED AND SPECIFIED NOWHERE (`DF-AUD-APAA-E`):\n  "
        + "\n  ".join(problems)
    )


def test_TC_ArgusAgent_CLI_001_39_the_guard_is_not_vacuous() -> None:
    """TC-ArgusAgent-CLI-001-39 — MANDATORY non-vacuity (module docstring, failure mode 4).

    Story 10.3 / AC6.5. `_subparsers`/`_group_actions`/`_actions` are argparse private API. If a
    future argparse changes them, a naive walk returns an empty list and every set comparison above
    passes over nothing. This test must go RED in that case, not silently green.
    """
    parser = cli.build_parser()
    derived = derive_arguments(parser)
    assert derived, (
        "THE PARSER WALK RETURNED NOTHING. Either the sub-commands are gone or argparse's "
        "private structure changed. Every equality assertion in this file is vacuous until this "
        "is repaired — do NOT delete this test to get green."
    )
    assert "--commit" in derived and "repo" in derived, (
        "the walk did not find FR30's own `repo`/`--commit` parameters, so it is not walking the "
        f"real audit parser: {sorted(derived)}"
    )
    assert CONTRACT_REGISTRY, "CONTRACT_REGISTRY is empty — the comparison would be vacuous"

    # Story 12.7 — the closure really is a closure. Until 2026-08-15 the walk was scoped to the
    # hand-named `audit` sub-command at every one of its call sites, so a second sub-command's
    # flags were invisible to `-35`/`-37`/`-38`. These three assertions are what stop that
    # narrowing from reappearing: the parser must declare more than one sub-command, the walk must
    # reach every one it declares, and no spelling may mean two different things.
    names = subcommands(parser)
    assert len(names) >= 2, (
        f"the parser declares {list(names)} — the closure over sub-commands cannot be shown to be "
        "wider than the single hand-named one it replaced. If a sub-command was removed, say so "
        "deliberately; do not let this assertion decay into a tautology."
    )
    reached = {name for argument in derived.values() for name in argument.subcommands}
    assert reached == set(names), (
        f"the argument walk reached {sorted(reached)} but the parser declares {list(names)} — a "
        "sub-command's flags are accepted and invisible to every comparison in this file, which "
        "is `DF-AUD-APAA-E` exactly."
    )
    assert conflicting_arguments(parser) == (), (
        "two sub-commands accept the SAME spelling with different defaults/shapes/choices, so one "
        "registry entry cannot describe both and the comparison would silently drop one: "
        f"{conflicting_arguments(parser)}"
    )

    invocations = extract_documented_invocations()
    assert invocations, (
        "THE DOCUMENTED-INVOCATION EXTRACTOR FOUND NOTHING. Either the consumer-facing corpus "
        "moved or the extraction rule stopped matching; AC6.4 is vacuous until it is repaired."
    )
    sources = {invocation.source for invocation in invocations}
    assert "README.md" in sources and "action.yml" in sources, (
        f"the extractor no longer reaches both README.md and action.yml — found {sorted(sources)}"
    )
    # Story 12.7 / AC3 — the `> 0` floor on the corpus's newest member. A rename or a move of the
    # asset tree turns this RED instead of silently shrinking `-28` back to the corpus it had
    # before, which is the `_CONSOLE_SCRIPTS` failure mode: a recognizer that stops recognizing.
    from_assets = [s for s in sources if s.startswith("argus/assets/commands/")]
    assert from_assets, (
        "NO documented invocation was extracted from the shipped command-asset tree "
        f"({_ASSET_GLOB!r}). Either the tree moved, the assets stopped carrying a fenced `argus "
        "…` invocation, or the glob stopped matching — in every case `-28` has quietly stopped "
        "checking the one surface Story 12.7 added it for."
    )


def test_TC_ArgusAgent_CLI_001_40_positive_control_in_both_directions() -> None:
    """TC-ArgusAgent-CLI-001-40 — the comparison fires when it should, and only then.

    Story 10.3 / AC6.6, trap E.3 (the Epic-9 `-17b` denial filter that swallowed what it looked
    for). Exercised over SYNTHETIC parsers and a SYNTHETIC registry — the real parser is never
    mutated, so this control cannot be satisfied by weakening the thing under test.
    """

    def synthetic(flags: tuple[tuple[str, str], ...]) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog="synthetic")
        subparsers = parser.add_subparsers(dest="command", required=True)
        sub = subparsers.add_parser("audit")
        sub.add_argument("repo")
        for spelling, _dest in flags:
            sub.add_argument(spelling, default=None)
        return parser

    def registry(spellings: tuple[str, ...]) -> dict[str, ContractEntry]:
        return {
            spelling: ContractEntry(
                spelling=spelling,
                dest=spelling.lstrip("-").replace("-", "_"),
                default=None,
                shape=SHAPE_VALUE if spelling.startswith("-") else SHAPE_POSITIONAL,
                sites=("synthetic",),
            )
            for spelling in spellings
        }

    # FIRES: the parser accepts a flag nobody registered — the DF-AUD-APAA-E shape.
    derived = derive_arguments(synthetic((("--registered", "registered"), ("--rogue", "rogue"))), "audit")
    unregistered, unaccepted = unregistered_and_unaccepted(
        derived, registry(("repo", "--registered"))
    )
    assert unregistered == ("--rogue",), (
        f"the direction-one comparison did NOT fire on an unregistered flag: {unregistered}"
    )
    assert unaccepted == ()

    # FIRES: the contract claims a flag the parser rejects — the README:195 shape.
    derived = derive_arguments(synthetic((("--registered", "registered"),)), "audit")
    unregistered, unaccepted = unregistered_and_unaccepted(
        derived, registry(("repo", "--registered", "--phantom"))
    )
    assert unaccepted == ("--phantom",), (
        f"the direction-two comparison did NOT fire on a phantom flag: {unaccepted}"
    )
    assert unregistered == ()

    # DOES NOT FIRE: a parser that matches its registry exactly.
    derived = derive_arguments(synthetic((("--registered", "registered"),)), "audit")
    assert unregistered_and_unaccepted(derived, registry(("repo", "--registered"))) == ((), ())

    # FIRES / DOES NOT FIRE: the shape comparison, same two directions.
    moved = {
        "--registered": ContractEntry(
            spelling="--registered",
            dest="registered",
            default="MOVED",
            shape=SHAPE_VALUE,
            sites=("synthetic",),
        )
    }
    assert shape_divergences(derived, moved), "the default comparison did not fire on a moved default"
    assert shape_divergences(derived, registry(("--registered",))) == ()

    # FIRES: an entry whose contract site does not exist. DOES NOT FIRE: one whose site does.
    phantom_site = {
        "--registered": ContractEntry(
            spelling="--registered",
            dest="registered",
            default=None,
            shape=SHAPE_VALUE,
            sites=("README.md::a sentence no committed document contains, 7f3a91c0",),
        )
    }
    assert missing_sites(phantom_site), "the contract-site check did not fire on a phantom anchor"
    real_site = {
        "--report-dir": ContractEntry(
            spelling="--report-dir",
            dest="report_dir",
            default="",
            shape=SHAPE_VALUE,
            sites=("README.md::Report generation (`--report-dir`)",),
        )
    }
    assert missing_sites(real_site) == (), "the contract-site check fired on a REAL anchor"

    # FIRES: an entry that names no site at all.
    assert missing_sites(
        {
            "--siteless": ContractEntry(
                spelling="--siteless", dest="siteless", default=None, shape=SHAPE_VALUE, sites=()
            )
        }
    ), "an entry naming no contract site at all was accepted"


def test_TC_ArgusAgent_CLI_001_41_the_rule_is_registered_in_architecture_enforcement() -> None:
    """TC-ArgusAgent-CLI-001-41 — a rule that lives only in a test is not a rule.

    Story 10.3 / AC6.9, the `-23` precedent from Story 10.1. Asserts BOTH halves are still present:
    the §Enforcement registration of this guard, and the §A invocation-contract text it enforces.
    """
    architecture = _read_artifact("architecture.md")

    assert _GUARD_FILE in architecture, (
        f"architecture.md §Enforcement no longer names {_GUARD_FILE}. A rule that lives only in a "
        "test is not a rule and a rule that lives only in prose is not enforced (10.1's -23)."
    )
    assert "Invocation-contract enforcement" in architecture, (
        "architecture.md §Enforcement no longer carries the Story 10.3 invocation-contract "
        "paragraph that registers this guard"
    )
    assert "argus/cli.py::build_parser" in architecture, (
        "architecture.md §A no longer names `argus/cli.py::build_parser` as the source of truth "
        "for the accepted invocation surface (AC5.2). A hand-typed flag list in its place is the "
        "AI-E9-7 drift class this amendment exists to avoid."
    )

    prd = _read_artifact("E-PRD/prd.md")
    assert "argus/cli.py::build_parser" in prd, (
        "FR30 no longer names `argus/cli.py::build_parser` as the source of truth for the accepted "
        "invocation surface (AC5.1)"
    )


def test_TC_ArgusAgent_DOCS_001_28_every_documented_invocation_actually_parses() -> None:
    """TC-ArgusAgent-DOCS-001-28 — the command lines we ship must run.

    Story 10.3 / AC6.4 (§A.3). `README.md:195` documented `argus --budget 500 --materiality
    critical`, which exits `SystemExit 2` on an argparse error: the `audit` sub-command is missing
    and `--materiality` is not a flag this parser has ever accepted. The first command a new user
    copied failed. Extracted by RULE, not by a fixed list, so a newly documented command line is
    covered the day it is committed.
    """
    failures: list[str] = []
    for invocation in extract_documented_invocations():
        failure = parse_failure(invocation.command)
        if failure is not None:
            failures.append(
                f"{invocation.source}:{invocation.line_number}: {invocation.command!r} -> {failure}"
            )
    assert not failures, (
        "DOCUMENTED INVOCATION(S) THE PARSER REJECTS — a consumer copying these gets an argparse "
        "usage error, and argparse's usage exit code is `2`, which collides with the BLOCKED "
        "verdict code (filed as `DF-10-3-A`):\n  " + "\n  ".join(failures)
    )
