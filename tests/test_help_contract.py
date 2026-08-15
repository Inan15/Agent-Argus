"""Story 12.8 / AC2 — ``--help`` states what each argument does AND its default.

Verification area ArgusAgent-CLI (``TC-ArgusAgent-CLI-001-52``..``-54``, CONTINUING the index
``tests/test_cli_flag_contract.py`` left at ``-51``).

**Split out of ``tests/test_invocation_contract.py`` on 2026-08-15, along a COHESION boundary,
because that file crossed the NFR-M1 1200-line ceiling when these guards joined it.** It follows
the ``tests/invocation_sources.py`` (Story 12.7), ``argus/pipeline_persist.py`` (Story 6.3) and
``argus/pipeline_stages.py`` (Story 12.1) precedent exactly: a module docstring naming why the
module exists, no function split across the boundary, and no import path broken —
``live_actions`` stays in ``test_invocation_contract`` beside the walk it is a projection of, and
is IMPORTED here rather than re-implemented. **Lines were NOT shaved to fit, and the population
was NOT narrowed**; the size guard's own remedy text bans both, and rightly.

**The boundary is real, not arithmetic.** The file this was split from asks *"does the CONTRACT
REGISTRY equal what ``build_parser`` accepts?"* and closes over a registry of contract sites. This
one asks a different question about the same parser — *"does ``--help`` DESCRIBE what
``build_parser`` accepts?"* — and closes over the argparse FORMATTER, which the other file never
touches. The two share exactly one thing, the walk over accepted arguments, and that walk is
imported rather than copied.

**Why the question needed asking.** Measured on ``2f84a0b`` by rendering the real ``--help``: the
parser accepted **19** arguments and **8 value-bearing flags stated no default at all**
(``--materiality-bar``, ``--critical-subsystem``, ``--exclude-critical``, ``--skip-pass``,
``--reports``, ``--report-dir``, ``--ignore-path``, ``--ignore-pattern``). A user had to read the
source to find out what omitting a flag does — which is the *"sent elsewhere to interpret the
tool"* failure FR37 is written against, one layer out from the verdict.

**DN-2 binds the mechanism, not just the outcome:** the default is DERIVED from the parser and
never hand-typed into prose, because a hand-typed default is a transcription of a pinned value —
the class AI-E9-7 forbids — and it would re-create one layer out the exact drift ``-35``/``-37``
exist to close. ``build_parser`` installs ``ArgumentDefaultsHelpFormatter``; these guards compare
the RENDERED text against the LIVE ``action.default``. Rejected: a registry of expected default
sentences, which is a second hand-list — the instrument this project has now found wrong four
times.

⚠️ ``tests/test_cli_flag_contract.py`` forbids help-text assertions in that file BY NAME and
points here. No network, no LLM, no subprocess, no ``.argus/`` write.
"""

from __future__ import annotations

import argparse

from argus import cli

from tests.test_invocation_contract import live_actions


def subparsers_by_name(
    parser: argparse.ArgumentParser,
) -> dict[str, argparse.ArgumentParser]:
    """``{sub-command: its parser}`` — the same closure :func:`subcommands` walks (PURE).

    Story 12.8. ``-52`` needs the SUB-PARSER, not just its name, because rendering an
    argument's help is the formatter's job and the formatter belongs to the parser that owns
    the argument. Derived from the live parser, so a third sub-command enters the help
    contract with no edit here — which is the property AC2 asks for by name.
    """
    found: dict[str, argparse.ArgumentParser] = {}
    for action in parser._actions:  # noqa: SLF001 - argparse exposes no public walk
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001 - same
            for name, sub in action.choices.items():
                if isinstance(sub, argparse.ArgumentParser):
                    found[name] = sub
    return found


def rendered_help(
    sub: argparse.ArgumentParser, action: argparse.Action
) -> str:
    """The help text ``--help`` actually prints for ONE argument, whitespace-normalised (PURE).

    Story 12.8 / AC2. Rendered through the sub-parser's OWN formatter — the same object
    ``format_help()`` uses — so what this returns is what a user sees, including anything
    ``ArgumentDefaultsHelpFormatter`` appends. Reading ``action.help`` instead would compare
    the SOURCE string and would therefore be blind to the entire mechanism under test.

    **The width is PINNED, and that is not cosmetic.** ``sub._get_formatter()`` sizes itself
    from ``shutil.get_terminal_size()``, so the rendered text depends on the console the suite
    happens to run in — and ``textwrap`` breaks on HYPHENS, which measurably turned
    ``HIGH-CONFIDENCE`` into ``HIGH- CONFIDENCE`` and ``--report-dir`` into ``--report- dir``
    at the default 80 columns. A guard whose result moves with ``COLUMNS`` is red on one CI leg
    and green on another for no reason in the code (the ``LC_ALL`` class of defect that turned
    run ``31322881580`` red). Rendering at an effectively unbounded width removes wrapping
    entirely, so what is asserted is the AUTHORED text plus whatever the formatter appends.

    Whitespace is still collapsed, so a future multi-line help string is compared by content
    rather than by layout.
    """
    formatter = sub.formatter_class(prog=sub.prog, width=10_000)
    formatter.add_argument(action)
    return " ".join(formatter.format_help().split())
# ─────────────────────────────────────────────────────────────────────────────
# Story 12.8 / AC2 — `--help` states what each argument does AND its default
# ─────────────────────────────────────────────────────────────────────────────
#
# The population is `derive_arguments`' closure (`live_actions` is the same walk projected
# onto the live Action object), so a THIRD sub-command's flags enter the help contract with
# NO edit here. Writing a second walk for this file would be the `_CONSOLE_SCRIPTS` defect
# class Story 12.6 found twice and 12.7 found again.

#: The positional `repo` is the ONE argument whose rendered help states no default, and the
#: exemption is a DECISION rather than an omission (Story 12.8 / AC2). It is REQUIRED: there
#: is no value the parser falls back to, so "the default of `repo`" is not a fact that exists
#: and printing `(default: None)` would state a falsehood. `--dry-run` and `--remove` were
#: weighed in the same breath and are NOT exempt — a `store_true` has a real default (`False`)
#: and stating it is what tells an operator that omitting the flag is a live choice.
_HELP_DEFAULT_EXEMPT: dict[str, str] = {
    "repo": (
        "required positional — the parser has no fallback value for it, so there is no "
        "default to state and argparse correctly appends none"
    ),
}

#: The operator-consequence facts three help strings must carry, pinned by EXACT substring
#: with the reason each one exists. Every phrase is already recorded in `cli.py`'s own
#: contract block; omitting it from `--help` is what costs a user a run, which is why these
#: three and not others (Story 12.8 / AC2, §0.1 §A).
_HELP_MUST_STATE: dict[str, tuple[tuple[str, str], ...]] = {
    "--reports": (
        (
            "INERT WITHOUT --report-dir",
            "measured: `--reports final-verdict` alone renders nothing and says nothing, "
            "and cli.py already records this while the help did not",
        ),
    ),
    "--ignore-pattern": (
        (
            "MATCHED BY BARE SUBSTRING",
            "a short pattern is a wide net; an operator who thinks it is a glob suppresses "
            "far more than they meant to",
        ),
        (
            "CANNOT SUPPRESS A HIGH-CONFIDENCE LIVE PRODUCTION KEY",
            "Story 10.3's Live-Key Safeguard was the CONDITION of this flag's bless; a user "
            "who does not know the bound cannot rely on it",
        ),
    ),
    "--ignore-path": (
        (
            "CANNOT SUPPRESS A HIGH-CONFIDENCE LIVE PRODUCTION KEY",
            "the same safeguard clause — the two flags share the bound and must share the "
            "statement of it",
        ),
    ),
}


def test_TC_ArgusAgent_CLI_001_52_help_states_every_arguments_live_default() -> None:
    """TC-ArgusAgent-CLI-001-52 — parser/help parity: the default in `--help` is DERIVED.

    Story 12.8 / AC2 / DN-2, alongside `-35`'s parser-vs-contract equality exactly as
    `epics.md:2427-2429` asks. Measured on `2f84a0b`: the parser accepted **19** arguments and
    **8 value-bearing flags stated no default at all** (`--materiality-bar`,
    `--critical-subsystem`, `--exclude-critical`, `--skip-pass`, `--reports`, `--report-dir`,
    `--ignore-path`, `--ignore-pattern`), so a user had to read the source to learn what
    omitting a flag does.

    **Observable:** the text `--help` actually PRINTS for each argument (rendered through the
    sub-parser's own formatter — see :func:`rendered_help`), compared against
    `action.default` READ OFF THE LIVE PARSER. Never against a registry of expected default
    sentences: that is a second hand-list, the instrument this project has now found wrong
    four times, and it would re-create one layer out the very drift `-35`/`-37` close.

    **The defect moves it, at the real seam:** an argument declared on a sub-parser that lost
    its `formatter_class` keeps its `action.default` and loses the rendered `(default: …)`,
    which turns this RED. `-53` is the positive control that proves exactly that.
    """
    parser = cli.build_parser()
    subs = subparsers_by_name(parser)
    walked = 0
    reached: set[str] = set()
    problems: list[str] = []

    for name, sub in sorted(subs.items()):
        for spelling, action in sorted(live_actions(parser, name).items()):
            walked += 1
            reached.add(name)
            if spelling in _HELP_DEFAULT_EXEMPT:
                continue
            text = rendered_help(sub, action)
            expected = f"(default: {action.default})"
            if expected not in text:
                problems.append(
                    f"{name} {spelling}: rendered help does not state the live default "
                    f"{action.default!r} — expected {expected!r} in {text!r}"
                )

    assert not problems, (
        "HELP/PARSER DIVERGENCE — an argument's `--help` does not state the default the "
        "parser actually holds:\n  " + "\n  ".join(problems)
    )

    # Non-vacuity (AC2, E.3): a rename, a move, or an argparse change must turn this RED
    # rather than pass over an empty set.
    assert walked > 0, "the help-parity walk reached NO arguments; every assertion is vacuous"
    assert len(reached) >= 2, (
        f"the walk reached {sorted(reached)} — it must be a closure over EVERY sub-command, "
        "not the single hand-named one 12.7 removed"
    )
    # The exemption registry can only SHRINK, and only over arguments that still exist.
    stale = sorted(set(_HELP_DEFAULT_EXEMPT) - set(live_actions(parser)))
    assert not stale, (
        f"_HELP_DEFAULT_EXEMPT exempts argument(s) the parser no longer has: {stale}. An "
        "exemption for something that is gone is a hole, not a decision."
    )
    for spelling, reason in _HELP_DEFAULT_EXEMPT.items():
        assert reason.strip(), f"the exemption for {spelling} carries no reason"


def test_TC_ArgusAgent_CLI_001_53_the_help_parity_guard_actually_bites() -> None:
    """TC-ArgusAgent-CLI-001-53 — the positive control, generated from the live surface.

    Story 12.8 / AC2 + AI-E11-1 clause (iii). A guard that never fails on a bad input proves
    nothing (AI-E3-1). Both directions, over a SYNTHETIC parser — the real parser is never
    mutated (`-40`'s rule).

    The adversarial variant is GENERATED from the live parser rather than hand-written: every
    argument the real `audit` sub-parser accepts is re-rendered through a parser WITHOUT the
    defaults formatter, which is the single most likely way this parity is lost (someone adds
    a third sub-command and forgets `formatter_class`). Every one of them must be caught.
    """
    real = cli.build_parser()
    real_audit = subparsers_by_name(real)["audit"]
    population = [
        (spelling, action)
        for spelling, action in live_actions(real, "audit").items()
        if spelling not in _HELP_DEFAULT_EXEMPT
    ]
    assert population, "the generated adversarial set would be empty"

    # ACCEPTED: the real sub-parser's arguments all state their live default.
    for _spelling, action in population:
        assert f"(default: {action.default})" in rendered_help(real_audit, action)

    # REJECTED: the same arguments rendered by a parser that lost the formatter.
    bare = argparse.ArgumentParser(prog="synthetic")
    missed = [
        spelling
        for spelling, action in population
        if f"(default: {action.default})" not in rendered_help(bare, action)
    ]
    assert missed, (
        "dropping ArgumentDefaultsHelpFormatter changed NOTHING about the rendered help, so "
        "`-52` is not measuring the mechanism it claims to measure"
    )
    # And the loss is TOTAL, which is what makes the real green meaningful rather than
    # incidental to one flag whose prose happens to spell its default out.
    assert len(missed) == len(population), (
        f"only {len(missed)} of {len(population)} arguments lost their stated default when "
        "the formatter was removed — expected every one"
    )


def test_TC_ArgusAgent_CLI_001_54_help_states_the_three_operator_consequences() -> None:
    """TC-ArgusAgent-CLI-001-54 — a default is not the whole of "what this flag does".

    Story 12.8 / AC2. Three flags carry a fact whose omission costs a user a run, each already
    recorded in `cli.py`'s own contract block and none of them in `--help` before this story.
    They are pinned by EXACT substring, with the reason in `_HELP_MUST_STATE` beside each, so a
    reword that drops the fact is red and a reword that keeps it is free.

    This is deliberately NOT in `tests/test_cli_flag_contract.py`: that file's docstring
    forbids help-text assertions there BY NAME and points here instead.
    """
    parser = cli.build_parser()
    subs = subparsers_by_name(parser)
    checked = 0
    problems: list[str] = []

    for name, sub in sorted(subs.items()):
        for spelling, action in live_actions(parser, name).items():
            for phrase, reason in _HELP_MUST_STATE.get(spelling, ()):
                checked += 1
                if phrase not in rendered_help(sub, action):
                    problems.append(f"{spelling} no longer states {phrase!r} — {reason}")

    assert not problems, (
        "A HELP STRING DROPPED AN OPERATOR-CONSEQUENCE FACT:\n  " + "\n  ".join(problems)
    )
    expected_total = sum(len(v) for v in _HELP_MUST_STATE.values())
    assert expected_total > 0 and checked == expected_total, (
        f"only {checked} of {expected_total} registered phrases were reached — a flag in "
        "_HELP_MUST_STATE was renamed or removed and the guard went partly vacuous"
    )
