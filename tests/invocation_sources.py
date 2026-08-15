"""The DOCUMENTED-INVOCATION half of the Story-10.3 invocation contract (AC6.4).

Split out of ``tests/test_invocation_contract.py`` on 2026-08-15 by Story 12.7, along the COHESION
boundary the file already had, because that file crossed the NFR-M1 1200-line ceiling when the
command-asset tree joined the corpus. It follows the ``argus/pipeline_persist.py`` (Story 6.3) and
``argus/pipeline_stages.py`` (Story 12.1) precedent exactly: a module docstring naming why the
module exists, **no function split across the boundary**, and **every import path unchanged** —
``test_invocation_contract`` re-exports every name below, so
``from tests.test_invocation_contract import executable_line_numbers`` still resolves and
``tests/test_workflow_input_containment.py``'s assertion about that very import line still holds.
Lines were NOT shaved to fit; the guard's remedy text bans that, and rightly.

**The boundary is real, not arithmetic.** Two questions live in that file and they close over
different things. The half that stayed asks *"does the CONTRACT REGISTRY equal what
``build_parser`` accepts?"* and closes over argparse introspection. This half asks *"does every
command line this project SHIPS actually run?"* and closes over committed documents plus the
distribution's own ``[project.scripts]`` table. This half is also the half OTHER modules import:
``executable_line_numbers`` is the SINGLE definition of "which lines are shell source?" in this
repository (Story 11.3 / DN-2 made it public for that reason) and is used by
``tests/test_workflow_input_containment.py`` and ``tests/test_command_assets.py``. A shared
definition that lives inside a 1200-line test module is one nobody can find.

It is deliberately NOT named ``test_*``: it declares no test, and a second collection of the same
assertions would report every guard twice.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import shlex
from dataclasses import dataclass
from pathlib import Path

from argus import cli

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    """Read a committed file as text, ALWAYS explicitly utf-8 (never the host locale)."""
    return (_REPO_ROOT / relative).read_text(encoding="utf-8")


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
# `mypy argus`, `bandit -r argus` and `--title "argus-agent $TAG"` are all correctly OUT; README's
# terminal invocations, action.yml's and argus-student-audit.yml's are all correctly IN.
#
# UPDATED 2026-08-15 by Story 12.7. The comment here used to record the README slash-command block
# as *"correctly OUT … Story 12.7's"*, and that exclusion is now spent in the only way it could
# honestly be spent: the block no longer documents a capability that does not exist, and the
# COMMANDS THEMSELVES are shipped files whose `argus …` lines this guard now parses. The corpus
# gains `argus/assets/commands/*.md` BY GLOB, never by a hand-list, so an asset added, renamed or
# moved is covered the day it is committed rather than the day somebody remembers this file. The
# README's slash-command block stays out for the reason it always should have: `/argus-audit` is
# not a console script this distribution ships, so the recogniser never sees it — while the
# `argus install-commands` lines beside it ARE console-script invocations and are now checked.
# `-39` carries a floor requiring at least one extracted invocation to come FROM the asset tree, so
# this widening cannot rot into a glob that matches nothing.

# DERIVED from `[project.scripts]`, never hand-listed — corrected 2026-08-15 by Story 12.6.
# It was the three-tuple `("argus", "argus-agent", "repo-audit")` until this story added a
# FOURTH alias, and nothing here would have noticed: `_CONSOLE_SCRIPTS` is the recognizer
# for "is this line a documented invocation of something we ship", so a shipped script
# missing from it makes every command line a consumer copies for that script INVISIBLE to
# `-28`. That is a guard narrowing itself silently, which is the class AI-E11-1 clause (iii)
# names — the population is closed over the distribution metadata, so the next alias is
# covered the day it is declared and not the day somebody remembers this file.
#
# The TARGET matters as well as the name: the three CLI aliases all resolve to
# `argus.cli:main` and their command lines are parsed by `build_parser`, while `argus-mcp`
# resolves to `argus.mcp.server:main`, whose entire input is a JSON-RPC stream on stdin and
# which accepts NO arguments. Handing an `argus-mcp` line to the CLI parser would report a
# usage error for a command that is correct, so `parse_failure` dispatches on the target
# (below) rather than assuming one parser for every script this distribution ships.
_CLI_ENTRY_TARGET = "argus.cli:main"
_MCP_ENTRY_TARGET = "argus.mcp.server:main"


def console_script_targets() -> dict[str, str]:
    """``{alias: target}`` read off ``pyproject.toml [project.scripts]`` (PURE).

    Raises rather than returning an empty mapping if the table cannot be located: an empty
    recognizer makes every documented invocation invisible and `-28` would pass over
    nothing at all.
    """
    text = _read("pyproject.toml")
    match = re.search(r"^\[project\.scripts\]\n(.*?)(?=\n\[|\Z)", text, re.S | re.M)
    assert match, "pyproject.toml declares no [project.scripts] table"
    found = dict(re.findall(r'^([\w.-]+)\s*=\s*"([^"]+)"', match.group(1), re.M))
    assert found, "no console alias parsed out of [project.scripts]"
    return found


_CONSOLE_SCRIPT_TARGETS = console_script_targets()
_CONSOLE_SCRIPTS = tuple(sorted(_CONSOLE_SCRIPT_TARGETS))

_INVOCATION_SOURCES = ("README.md", "action.yml")
_WORKFLOW_GLOB = ".github/workflows/*.yml"
# The shipped command-asset tree (Story 12.7 / FR35). BY GLOB — the whole point of AC3 is that a
# rename or a move must turn `-39` RED rather than silently shrinking `-28`'s corpus to nothing.
_ASSET_GLOB = "argus/assets/commands/*.md"
# The consumer-facing documentation directory (Story 12.8 / AC1 / AC9.3). BY GLOB, for the reason
# stated one line up and because it is the whole delivery of the first-run page: `docs/first-run.md`
# is where a reader with no prior exposure copies their FIRST `argus …` command line from, so a
# command that does not parse costs exactly the user this project's persona is written about
# (PRD Journey 6). `-39` carries a `> 0` floor requiring at least one extracted invocation to come
# from this glob, so a rename, a move, or a page that stops carrying a fenced invocation turns RED
# rather than quietly shrinking the corpus back to what it was.
_DOCS_GLOB = "docs/*.md"

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
    files.extend(sorted(_REPO_ROOT.glob(_ASSET_GLOB)))
    files.extend(sorted(_REPO_ROOT.glob(_DOCS_GLOB)))
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

    # Which parser judges the line is decided by the alias's TARGET, not assumed (Story
    # 12.6). `argus-mcp` takes no arguments at all — its input is the message stream — so
    # for it the contract is "the documented line is the bare command", and a documented
    # `argus-mcp --something` is a failure here rather than a false green.
    target = _CONSOLE_SCRIPT_TARGETS.get(argv[0] if argv else "", _CLI_ENTRY_TARGET)
    if target == _MCP_ENTRY_TARGET:
        if len(argv) > 1:
            return (
                f"`{argv[0]}` accepts no arguments (its input is a JSON-RPC stream on "
                f"stdin) and this line passes {argv[1:]}"
            )
        return None

    parser = cli.build_parser()
    parser.exit_on_error = False
    # `--help` writes the whole help block to stdout; a guard is not a place for that, and
    # swallowing it is what lets a documented `argus audit --help` be checked like any other
    # line rather than excluded from the corpus.
    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink):
            parser.parse_args(argv[1:])
    except SystemExit as exc:
        # CORRECTED 2026-08-15 by Story 12.8 / AC1. `SystemExit(0)` is argparse ACCEPTING the
        # line and printing help — the exact opposite of what the old message asserted
        # ("argparse rejected the documented command line"). Reading it as a rejection made
        # this guard structurally unable to admit a documented `--help` invocation, and
        # `docs/first-run.md` documents two of them: the whole point of that page is to show a
        # reader how to ask the tool what it accepts. The check is NOT loosened — a usage error
        # still exits `2`, and `2` is still a failure here.
        if exc.code in (0, None):
            return None
        return f"SystemExit {exc.code} — argparse rejected the documented command line"
    except argparse.ArgumentError as exc:
        return f"ArgumentError: {exc}"
    return None

