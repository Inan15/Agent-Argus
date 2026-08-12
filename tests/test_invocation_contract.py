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


def derive_arguments(parser: argparse.ArgumentParser, subcommand: str) -> dict[str, DerivedArgument]:
    """Walk *parser*'s *subcommand* and return every accepted argument, keyed by spelling (PURE).

    Uses argparse private API (``_subparsers`` / ``_group_actions`` / ``_actions``) — see the module
    docstring's failure mode 4 and ``-39``, which is the countermeasure. ``-h/--help`` is excluded:
    it is argparse's own, is not part of the product's invocation contract, and its prose is Story
    12.8's. A positional is keyed by its ``dest``.
    """
    subparsers_actions = [
        action
        for action in parser._actions  # noqa: SLF001 - argparse exposes no public walk
        if isinstance(action, argparse._SubParsersAction)  # noqa: SLF001 - same
    ]
    derived: dict[str, DerivedArgument] = {}
    for subparsers_action in subparsers_actions:
        sub = subparsers_action.choices.get(subcommand)
        if sub is None:
            continue
        for action in sub._actions:  # noqa: SLF001 - same
            if isinstance(action, argparse._HelpAction):  # noqa: SLF001 - same
                continue
            spelling = action.option_strings[0] if action.option_strings else action.dest
            derived[spelling] = DerivedArgument(
                spelling=spelling,
                dest=action.dest,
                default=action.default,
                shape=describe_shape(action),
                choices=tuple(str(c) for c in (action.choices or ())),
            )
    return derived


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
# Scoped to README.md, action.yml and .github/workflows/*.yml, and MEASURED against the corpus
# before the pattern was written (10.2's D2 lesson). `epics.md` and this repository's story files
# also contain `argus audit ...` strings, but they are the project's meta-discussion of the command
# rather than a command a CONSUMER is told to run; a guard that fires on those cries wolf and gets
# deleted by the third person to hit it.
#
# A command line counts when it is inside an executable block — a fenced ```bash/```sh block in
# README, or a YAML `run:` script — AND its first token is a console script this distribution ships.
# Measured consequences of that rule on the real corpus: `pip install "argus-agent @ ..."`,
# `mypy argus`, `bandit -r argus`, `--title "argus-agent $TAG"` and the `/audit ...` slash-command
# block (README:178-190, Story 12.7's, DN-9) are all correctly OUT; README's terminal invocation,
# action.yml's and argus-student-audit.yml's are all correctly IN.

_CONSOLE_SCRIPTS = ("argus", "argus-agent", "repo-audit")

_INVOCATION_SOURCES = ("README.md", "action.yml")
_WORKFLOW_GLOB = ".github/workflows/*.yml"

# `${{ github.sha }}`, `$TAG`, `<repo>` — a documented placeholder is a value, not a parse error.
_PLACEHOLDER_RE = re.compile(r"\$\{\{[^}]*\}\}|\$\{[^}]*\}|\$[A-Za-z_][A-Za-z0-9_]*|<[^>\s]+>")
_PLACEHOLDER = "PLACEHOLDER"


@dataclass(frozen=True)
class DocumentedInvocation:
    """A console-script command line committed in a consumer-facing file."""

    source: str
    line_number: int
    command: str


# The YAML `run:` header, in BOTH shapes GitHub accepts, and in EVERY spelling YAML gives each
# shape. Group `block` is the block-scalar header if one is present, group `rest` is whatever
# else follows the key on the same line.
#
# `block` deliberately matches the whole YAML block header — the style indicator `|` or `>`
# followed by its OPTIONAL indentation indicator (a digit) and chomping indicator (`-`/`+`), in
# EITHER order, which is what the YAML spec allows (`c-b-block-header`). So `|`, `>`, `|-`, `|+`,
# `>-`, `>+`, `|2`, `|2-`, `|-2`, `>-2` are all recognised as block headers. The previous rule
# `(?:[|>][-+]?\s*)?(.*)` did not, and the miss was not academic: a digit is not `[-+]`, so
# `run: |2` fell into group 1 non-empty and was classified as the SINGLE-LINE form.
#
# 🚩 THE CLASSIFICATION KEYS ON THE PRESENCE OF `block`, NOT ON WHETHER SOMETHING FOLLOWS IT.
# That is the whole correction (Story 11.3 review iteration 1). YAML permits exactly one thing
# after a block header on the same line — a comment — so `run: | # scrub inputs first` IS a block
# scalar, and the old "is the remainder non-empty?" test read the comment text as the command and
# never scanned the indented body where the real script lives. Nine header spellings were
# measured VACUOUS on 2026-08-12 before this fix (`| #`, `> #`, `|- #`, `|+ #`, `|2`, `|2- #`,
# `>-2`, `run: # …`, and a single-line scalar continued onto the next line); each is ordinary,
# non-adversarial CI YAML. Keying on the indicator makes the set of recognised block spellings
# the YAML grammar itself rather than a list of the ones somebody thought of (§C.6).
_RUN_HEADER_RE = re.compile(r"^-?\s*run:\s*(?P<block>[|>][0-9+\-]*)?\s*(?P<rest>.*)$")


def _expression_is_open(text: str) -> bool:
    """Does *text* carry a `${{` that has not been closed by a `}}` yet? (PURE)"""
    return text.count("${{") > text.count("}}")


def executable_line_numbers(text: str, suffix: str) -> set[int]:
    """1-based line numbers that sit inside an executable block (PURE).

    PUBLIC on purpose (Story 11.3 / DN-2): this is the SINGLE definition of "which lines are
    shell source?" in this repository, and `tests/test_workflow_input_containment.py` imports
    it rather than carrying a second copy (AR7 / architecture §3.3 — extend, never duplicate).
    A private spelling would have forced the injection guard to reach through `_`-prefixed
    API or to re-implement the rule, and a rule implemented twice drifts in one of the two.

    **Both YAML `run:` shapes are recognised, and that generalisation is load-bearing.** The
    original rule keyed on ``^-?\\s*run:\\s*[|>]?[-+]?\\s*$`` — the ``\\s*$`` requires
    end-of-line after the key, so it saw block scalars ONLY. Measured on 2026-08-12 against a
    synthetic ``- run: echo "${{ inputs.evil }}"`` it returned an **empty** set, and against
    `.github/workflows/release.yml` it missed four real single-line `run:` steps. A guard
    inheriting that blindness would have been vacuous against the cheapest way to reintroduce
    `DF-9-2-D`: writing the interpolation on one line. Re-measured after the generalisation,
    `extract_documented_invocations()` returns the same five invocations element-by-element —
    every single-line `run:` in the corpus starts with `python`, which is not a console script
    this distribution ships.

    **Story 11.3, review iteration 1 — the same lesson, one shape further out.** The first
    generalisation asked *"is anything left on the line after the key?"* and called a non-empty
    remainder the command. That re-created the identical blindness for a header carrying a
    trailing YAML comment (``run: | # scrub inputs before use``) and for a header carrying an
    indentation indicator (``run: |2``): the remainder is non-empty in both, so the line was
    classified single-line, ``run_indent`` was never set, and **the indented body — where the
    script and any interpolation live — was never scanned at all**. Measured before the fix,
    nine such headers each yielded an EMPTY hit set from the containment guard. The rule now
    keys on the PRESENCE of the block indicator (YAML allows only a comment after it), which
    makes the recognised set the YAML grammar rather than an enumeration. ``-32`` in
    ``tests/test_workflow_input_containment.py`` drives the whole generated cross product of
    style x indentation x chomping x comment through this function and fails on any spelling
    that collapses back to the single-line branch.

    **A single-line ``run:`` whose value carries an unclosed ``${{`` absorbs its continuation
    lines**, because a YAML plain or quoted scalar may span lines and ``run: echo "${{`` /
    ``  inputs.evil }}"`` is legal YAML that the runner folds into one command. The continuation
    is bounded by the closing ``}}`` and by the indentation returning, deliberately narrowly: a
    single-line ``run:`` is normally followed by a SIBLING key (``env:``, ``with:``) whose body is
    more indented, and absorbing that would report `env:`-bound values — the very shape this
    project asks authors to write — as shell source.
    """
    inside: set[int] = set()
    if suffix == ".md":
        fenced = False
        for number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                fenced = not fenced and stripped[3:].strip().lower() in ("bash", "sh", "shell", "console")
                continue
            if fenced:
                inside.add(number)
        return inside
    # YAML: everything under a `run:` block scalar, until the indentation returns — PLUS the
    # single-line `run: cmd …` form, which is shell source on the key's own line.
    run_indent: int | None = None
    open_indent: int | None = None  # single-line `run:` whose value has an unclosed `${{`
    open_text = ""
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        indent = len(line) - len(line.lstrip())
        if run_indent is not None and indent > run_indent:
            inside.add(number)
            continue
        if open_indent is not None and indent > open_indent:
            inside.add(number)  # continuation of a multi-line single-line-form scalar
            open_text += "\n" + stripped
            if not _expression_is_open(open_text):
                open_indent = None
            continue
        run_indent = None
        open_indent = None
        header = _RUN_HEADER_RE.match(stripped)
        if header is not None:
            rest = header.group("rest").strip()
            if header.group("block") is not None or not rest or rest.startswith("#"):
                # Block scalar (`run: |`, `run: >-2`, `run: |+ # note`) or a bare `run:` key:
                # the script is what follows, indented. Only a COMMENT may legally follow a
                # block header, so its remainder is never the command.
                run_indent = indent
            else:
                inside.add(number)  # single-line `run: cmd …` — the line itself is the script
                if _expression_is_open(rest):
                    open_indent, open_text = indent, rest
    return inside


def extract_documented_invocations() -> tuple[DocumentedInvocation, ...]:
    """Extract every console-script command line committed in the consumer-facing corpus (PURE)."""
    files = [_REPO_ROOT / name for name in _INVOCATION_SOURCES]
    files.extend(sorted(_REPO_ROOT.glob(_WORKFLOW_GLOB)))
    found: list[DocumentedInvocation] = []
    for path in files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        executable = executable_line_numbers(text, path.suffix)
        lines = text.splitlines()
        number = 0
        while number < len(lines):
            number += 1
            if number not in executable:
                continue
            stripped = lines[number - 1].strip()
            first = stripped.split(" ", 1)[0]
            if first not in _CONSOLE_SCRIPTS:
                continue
            start = number
            parts = [stripped]
            while parts[-1].endswith("\\") and number < len(lines):
                parts[-1] = parts[-1][:-1]
                number += 1
                parts.append(lines[number - 1].strip())
            found.append(
                DocumentedInvocation(
                    source=str(path.relative_to(_REPO_ROOT)).replace("\\", "/"),
                    line_number=start,
                    command=" ".join(part.strip() for part in parts).strip(),
                )
            )
    return tuple(found)


def parse_failure(command: str) -> str | None:
    """Return the parse failure for *command*, or ``None`` when it parses (PURE).

    ``build_parser().parse_args`` is called directly rather than through a subprocess: the failure
    mode under test is the ARGUMENT CONTRACT, not process spawning, and a subprocess would make this
    guard host-dependent on all three CI legs.
    """
    substituted = _PLACEHOLDER_RE.sub(_PLACEHOLDER, command)
    try:
        argv = shlex.split(substituted, posix=True)
    except ValueError as exc:  # unbalanced quotes in the documented line
        return f"could not tokenise: {exc}"
    parser = cli.build_parser()
    parser.exit_on_error = False
    try:
        parser.parse_args(argv[1:])
    except SystemExit as exc:
        return f"SystemExit {exc.code} — argparse rejected the documented command line"
    except argparse.ArgumentError as exc:
        return f"ArgumentError: {exc}"
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_CLI_001_35_every_accepted_flag_is_registered_and_vice_versa() -> None:
    """TC-ArgusAgent-CLI-001-35 — parser-vs-contract equality, in both directions.

    Story 10.3 / AC6.1, AC6.2, AC6.3 (`DF-AUD-APAA-E`).
    """
    derived = derive_arguments(cli.build_parser(), "audit")
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
    failures: list[str] = []
    for entry in CONTRACT_REGISTRY:
        if entry.shape == SHAPE_POSITIONAL:
            continue
        if entry.shape == SHAPE_CHOICE:
            value = [entry.choices[0]] if entry.choices else ["x"]
        else:
            value = list(sample_for_shape[entry.shape] or [])
        failure = parse_failure("argus audit . " + shlex.join([entry.spelling, *value]))
        if failure is not None:
            failures.append(f"{entry.spelling}: {failure}")
    assert not failures, (
        "A CONTRACT SITE NAMES A FLAG THE PARSER REJECTS — " + "; ".join(failures)
    )


def test_TC_ArgusAgent_CLI_001_37_defaults_and_shapes_match_the_contract() -> None:
    """TC-ArgusAgent-CLI-001-37 — names are not enough: default and shape are compared too.

    Story 10.3 / AC6.7. A silent default change is a behavioural change to a published surface; it
    must cost a deliberate registry edit.
    """
    derived = derive_arguments(cli.build_parser(), "audit")
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

    cli_default = derive_arguments(cli.build_parser(), "audit")["--coverage-scope"].default
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
    derived = derive_arguments(cli.build_parser(), "audit")
    assert derived, (
        "THE PARSER WALK RETURNED NOTHING. Either the `audit` sub-command is gone or argparse's "
        "private structure changed. Every equality assertion in this file is vacuous until this "
        "is repaired — do NOT delete this test to get green."
    )
    assert "--commit" in derived and "repo" in derived, (
        "the walk did not find FR30's own `repo`/`--commit` parameters, so it is not walking the "
        f"real audit parser: {sorted(derived)}"
    )
    assert CONTRACT_REGISTRY, "CONTRACT_REGISTRY is empty — the comparison would be vacuous"

    invocations = extract_documented_invocations()
    assert invocations, (
        "THE DOCUMENTED-INVOCATION EXTRACTOR FOUND NOTHING. Either the consumer-facing corpus "
        "moved or the extraction rule stopped matching; AC6.4 is vacuous until it is repaired."
    )
    sources = {invocation.source for invocation in invocations}
    assert "README.md" in sources and "action.yml" in sources, (
        f"the extractor no longer reaches both README.md and action.yml — found {sorted(sources)}"
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
