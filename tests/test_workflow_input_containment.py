"""Story 11.3 — a consumer's workflow input is DATA, never shell source (``DF-9-2-D``).

Verification area ArgusAgent-SECURITY (``TC-ArgusAgent-SECURITY-001-24``..``-32``, CONTINUING the
index whose prior maximum is ``-23`` in ``tests/test_secret_containment.py``; cross-file
continuation of a namespace is established house style, as ``DOCS-001`` already spans three files).

**The defect this closes.** GitHub states the mechanism plainly: *"Before the shell script is run,
the expressions inside ``${{ }}`` are evaluated and then substituted with the resulting values,
which can make it vulnerable to shell command injection."* The value is not handed to ``bash`` as
data — it is **pasted into the script text**. ``action.yml`` interpolated five consumer-settable
action inputs into ``run:`` bodies, so a consuming repository whose workflow writes
``with: {strict: "${{ github.event.issue.title }}"}`` handed an attacker its job: the runner token,
``$GITHUB_ENV``, ``$GITHUB_OUTPUT`` and the checked-out source. The exploit was **demonstrated
through a real shell** during story design — an injected ``id -un`` ran and printed the user — and
that demonstration is recorded in the story document, deliberately NOT here (see "no shell" below).

**Why this file proves an INVARIANCE rather than running the exploit.** The security property is
not *"a shell does not execute the value"*; it is the stronger, purely textual:

    The ``run:`` script text of every step is INVARIANT under the value of every action input.

``env:``-binding buys exactly that, and it is checkable with ``str`` operations over the committed
file. That formulation is what makes the guard portable, and portability here is not a preference:

* ``bash`` is unavailable to a Windows developer, and ``pytest.skip`` is a FALSE GREEN in this
  project — ``.github/workflows/audit-ci.yml`` sets ``ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`` precisely
  so that a skip is a hard failure. A guard that silently skips has proven nothing.
* ``PyYAML`` is **not a declared dependency** (measured 2026-08-12: absent from ``pyproject.toml``'s
  ``dependencies`` and its ``[dev]`` extra; present in this venv only transitively via
  ``bandit``/``markdown-it-py``). A guard that ``import yaml`` passes here and is a coin-toss in CI.
* A committed test that spawns a shell to prove code execution is itself a liability.

So: **stdlib only — no ``bash``, no ``subprocess``, no ``PyYAML``, no network, no ``pytest.skip``,
no file writes.** Text analysis is also the *right* model, because ``${{ }}`` substitution IS a
textual operation on the script string, and a text scan can report a ``file:line`` a maintainer can
navigate to.

**Why the run-block resolver is IMPORTED and not re-implemented** (story DN-2, AR7 /
architecture §3.3 — extend, never duplicate). ``tests/test_invocation_contract.py`` already answers
*"which lines are shell source?"*. Measured 2026-08-12, its original rule keyed on
``^-?\\s*run:\\s*[|>]?[-+]?\\s*$`` and therefore saw **block scalars only**: against a synthetic
``- run: echo "${{ inputs.evil }}"`` it returned an **empty** set. A guard inheriting that blindness
would have been **vacuous against the cheapest way to reintroduce ``DF-9-2-D``** — writing the
interpolation on one line. This project has already shipped one guard whose filter swallowed the
thing it looked for (the Epic-9 ``-17b`` case), so the resolver was generalized **in place** and
made public, and ``-30`` asserts there is still exactly ONE definition of it and that this file
imports rather than copies it.

**Six ways a guard like this lies, and what stops each.** The sixth was found by review AFTER the
first five were written down, which is itself the argument for generating shapes rather than
listing them.

1. *It checks a hand-written file list, so tomorrow's workflow escapes.* Stopped by ``-30``: the
   corpus is a **glob**, and it covers **both** spellings GitHub accepts (``action.yml`` and
   ``action.yaml``, ``*.yml`` and ``*.yaml``) — the existing ``_WORKFLOW_GLOB`` is ``*.yml`` only,
   so a workflow committed as ``foo.yaml`` would have escaped it silently.
2. *Its resolver returns nothing and every assertion passes over an empty set.* Stopped by ``-30``'s
   non-vacuity half: the corpus must be non-empty, must contain ``action.yml``, and the resolver
   must find real run bodies in it.
3. *It enumerates today's five sites instead of closing the class.* Stopped by ``-24``: ``inputs.*``
   and ``github.event.*`` are forbidden OUTRIGHT with **no exemption possible**, so the guard
   protects the future rather than the past.
4. *Its exemption registry becomes a silent hole.* Stopped by ``-26``, which fails in BOTH
   directions: an unregistered survivor fails, and a registered exemption matching nothing fails.
5. *Its renderer never substitutes anything, so the invariance assertion is circular.* Stopped by
   ``-28``, the mandatory positive control: the same assertion applied to the **pre-fix** line, held
   as a literal string in this file, MUST fail.
6. *Its resolver recognises ONE spelling of the ``run:`` header and silently ignores the bodies
   under the others.* This one was live: as first shipped, a header carrying a trailing YAML
   comment (``run: | # scrub inputs before use``) or an indentation indicator (``run: |2``) was
   misread as the single-line form, so the indented script beneath it — the whole point of a block
   scalar — was never scanned. ``interpolations()`` returned ``()`` for an ``action.yml``-shaped
   document containing ``echo "${{ inputs.strict }}"``. Stopped by ``-32``, which generates YAML's
   entire block-header grammar rather than listing shapes, and by the three extra shapes added to
   ``-29``. **The general lesson, recorded because this project has now paid for it twice:** the
   fix for "a filter swallowed what it looks for" is not another enumeration of the cases somebody
   thought of — it is to key the classification on the grammar's own discriminator.

Every file is opened ``encoding="utf-8"`` explicitly: the artifact tree carries ``⚠️``/``🚩``/``❌``
and an inherited host locale is the exact defect class that turned run ``31322881580`` red.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Mapping

from tests.test_invocation_contract import executable_line_numbers

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]

_GUARD_FILE: Final[str] = "tests/test_workflow_input_containment.py"
# WHERE the single run-block resolver is DECLARED. Moved 2026-08-15 by Story 12.7 from
# `tests/test_invocation_contract.py` to its sibling when that file crossed the NFR-M1 ceiling; the
# import path below is a preserved re-export, so what changed is the declaration site and nothing
# else. `-30` now proves the "exactly one" claim over every tracked `.py`, not over this one name.
_RESOLVER_FILE: Final[str] = "tests/invocation_sources.py"

# ─────────────────────────────────────────────────────────────────────────────
# The corpus — resolved by GLOB, never by a hand-written list
# ─────────────────────────────────────────────────────────────────────────────
#
# Both spellings, deliberately. GitHub accepts `action.yml` and `action.yaml` for a composite
# action, and reads every `*.yml` AND `*.yaml` under `.github/workflows/`. Today this resolves to
# four files; a workflow added tomorrow is covered the day it is committed, with no edit here.

_CORPUS_PATTERNS: Final[tuple[str, ...]] = (
    "action.yml",
    "action.yaml",
    ".github/workflows/*.yml",
    ".github/workflows/*.yaml",
)


def corpus_paths() -> tuple[str, ...]:
    """Every committed YAML file whose `run:` bodies this guard governs (PURE-ish, reads dir)."""
    found: set[str] = set()
    for pattern in _CORPUS_PATTERNS:
        for path in _REPO_ROOT.glob(pattern):
            if path.is_file():
                found.add(str(path.relative_to(_REPO_ROOT)).replace("\\", "/"))
    return tuple(sorted(found))


# ─────────────────────────────────────────────────────────────────────────────
# Run bodies, and the expressions that survive inside them
# ─────────────────────────────────────────────────────────────────────────────
#
# AC3.7 — detection is over the JOINED run-body text, never per-line. A `${{ … }}` expression may
# be wrapped across lines inside a block scalar, so a per-line regex requiring the context name on
# the same line as `${{` is trivially escapable by pressing Enter. Each hit is attributed back to
# the line carrying its `${{` so the failure message is navigable rather than a bare boolean.

_EXPRESSION_RE: Final[re.Pattern[str]] = re.compile(r"\$\{\{(.*?)\}\}", re.DOTALL)

# The GitHub expression contexts. A dotted path is captured whole, so `github.event.issue.title`
# is one context and not three, and the `github.event.*` ban below can key on its prefix.
_CONTEXT_RE: Final[re.Pattern[str]] = re.compile(
    r"\b(?:inputs|github|env|secrets|steps|matrix|needs|vars|jobs|job|runner|strategy)"
    r"(?:\.[A-Za-z0-9_-]+)*"
)


@dataclass(frozen=True)
class RunBody:
    """One `run:` script, as committed: its file, its line numbers, and its joined text."""

    path: str
    line_numbers: tuple[int, ...]
    text: str


@dataclass(frozen=True)
class Interpolation:
    """One expression context surviving inside a `run:` body, attributed to a line."""

    path: str
    line_number: int
    context: str
    line_text: str

    def coordinate(self) -> str:
        return f"{self.path}:{self.line_number}"


def run_bodies(path: str, text: str) -> tuple[RunBody, ...]:
    """Every `run:` script in *text*, as contiguous line groups (PURE).

    Line membership comes from the SINGLE resolver in ``tests/test_invocation_contract.py``
    (DN-2). Groups are split on a real indentation return, never on a blank line: the resolver
    skips blank lines, and a block scalar routinely contains them, so treating a blank line as a
    boundary would cut one script into two and let a line-wrapped expression fall through the seam.
    """
    lines = text.splitlines()
    numbers = sorted(executable_line_numbers(text, Path(path).suffix))
    groups: list[list[int]] = []
    for number in numbers:
        previous = groups[-1][-1] if groups else None
        contiguous = previous is not None and all(
            not lines[gap - 1].strip() for gap in range(previous + 1, number)
        )
        if contiguous:
            groups[-1].append(number)
        else:
            groups.append([number])
    return tuple(
        RunBody(
            path=path,
            line_numbers=tuple(group),
            text="\n".join(lines[number - 1] for number in group),
        )
        for group in groups
    )


def interpolations(path: str, text: str) -> tuple[Interpolation, ...]:
    """Every expression context that survives inside a `run:` body of *text* (PURE).

    An expression naming no recognised context (a bare literal, say) is still reported, with the
    raw expression as its context. The closure has to be TOTAL: an unclassifiable survivor must
    reach a human, not fall out of the bottom of the classifier.
    """
    lines = text.splitlines()
    found: list[Interpolation] = []
    for body in run_bodies(path, text):
        for match in _EXPRESSION_RE.finditer(body.text):
            offset = body.text[: match.start()].count("\n")
            number = body.line_numbers[offset]
            expression = match.group(1)
            contexts = tuple(dict.fromkeys(_CONTEXT_RE.findall(expression)))
            for context in contexts or (expression.strip() or "<empty expression>",):
                found.append(
                    Interpolation(
                        path=path,
                        line_number=number,
                        context=context,
                        line_text=lines[number - 1].strip(),
                    )
                )
    return tuple(found)


def is_forbidden(context: str) -> bool:
    """Is *context* banned inside a `run:` body with NO exemption possible? (PURE)

    Two families, and the ban is outright for both (AC3.4):

    * ``inputs.*`` — the action's own consumer-settable surface. This IS ``DF-9-2-D``.
    * ``github.event.*`` — GitHub's documented untrusted-input surface. The attacker-influenced
      members end in ``body``, ``default_branch``, ``email``, ``head_ref``, ``label``, ``message``,
      ``name``, ``page_name``, ``ref``, ``title``. Enumerating them would be a list to keep in
      sync; banning the whole context is the closure.
    """
    return any(context == family or context.startswith(family + ".") for family in ("inputs", "github.event"))


# ─────────────────────────────────────────────────────────────────────────────
# THE EXEMPTION REGISTRY — reason-carrying, closed, and failing in BOTH directions
# ─────────────────────────────────────────────────────────────────────────────
#
# `inputs.*` and `github.event.*` can never appear here (`-26` asserts that). Every OTHER context
# surviving inside a `run:` body must be registered with a written reason saying WHY the context is
# trusted. Entries are keyed by anchor TEXT, not by a line number: every coordinate in this project
# drifts, and the ledger's own `DF-9-2-D` coordinate was off by one when this story re-measured it.


@dataclass(frozen=True)
class ContextExemption:
    """One trusted, non-input expression permitted to remain inside a `run:` body."""

    path: str
    context: str
    anchor: str
    reason: str


_CONTEXT_EXEMPTIONS: Final[tuple[ContextExemption, ...]] = (
    ContextExemption(
        path=".github/workflows/argus-student-audit.yml",
        context="github.sha",
        anchor="--commit",
        reason=(
            "Story 11.3 / DN-6. `github.sha` is set by the RUNNER to the 40-hex commit being "
            "built (`^[0-9a-f]{40}$`); it is not settable by a workflow author and not "
            "influenced by an attacker, so it is not the DF-9-2-D class. It is quoted, and it "
            "reaches `argus audit --commit`, which pins the FR1 determinism check. Left as-is "
            "rather than env-bound because this workflow is this repository's own, is not a "
            "published artifact, and a no-behaviour edit to it is churn a security story should "
            "not carry. The day this file gains a `workflow_dispatch` input or reads "
            "`github.event.*`, `-24` catches it with NO edit to this registry."
        ),
    ),
    ContextExemption(
        path=".github/workflows/argus-student-audit.yml",
        context="github.sha",
        anchor="has audited your commit",
        reason=(
            "Story 11.3 / DN-6, and the more interesting of the two: this one interpolates into "
            "PYTHON source inside a `python -c \"…\"` run body, so the injection target would be "
            "the Python parser rather than bash. Trusted for the same reason — `github.sha` is "
            "runner-provided 40-hex — and recorded separately BECAUSE the target language "
            "differs: a future reviewer must not read the first entry as covering this one. If "
            "this line ever carried a consumer-settable value it would be a Python-source "
            "injection, which no amount of shell quoting would fix."
        ),
    ),
)


def unregistered_survivors(
    hits: tuple[Interpolation, ...], registry: tuple[ContextExemption, ...]
) -> tuple[Interpolation, ...]:
    """Interpolations that are neither forbidden nor covered by a registry entry (PURE)."""
    return tuple(
        hit for hit in hits if not is_forbidden(hit.context) and _exemption_for(hit, registry) is None
    )


def _exemption_for(
    hit: Interpolation, registry: tuple[ContextExemption, ...]
) -> ContextExemption | None:
    for entry in registry:
        if entry.path == hit.path and entry.context == hit.context and entry.anchor in hit.line_text:
            return entry
    return None


def unmatched_exemptions(
    hits: tuple[Interpolation, ...], registry: tuple[ContextExemption, ...]
) -> tuple[ContextExemption, ...]:
    """Registry entries that no longer describe anything real (PURE) — direction two.

    E.2: a registry that cannot go red is theatre. An exemption whose site was deleted or fixed
    must fail, or the registry silently accumulates permissions nobody holds any more.
    """
    return tuple(
        entry
        for entry in registry
        if not any(_exemption_for(hit, (entry,)) is not None for hit in hits)
    )


def all_interpolations() -> tuple[Interpolation, ...]:
    """Every surviving in-`run:` interpolation across the whole committed corpus (reads files)."""
    found: list[Interpolation] = []
    for relative in corpus_paths():
        text = (_REPO_ROOT / relative).read_text(encoding="utf-8")
        found.extend(interpolations(relative, text))
    return tuple(found)


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — the renderer: the runner's textual substitution, reproduced in pure Python
# ─────────────────────────────────────────────────────────────────────────────

# Whitespace-tolerant on BOTH sides of the context path, because `${{inputs.strict}}`,
# `${{ inputs.strict }}` and `${{  inputs.strict  }}` are all the same expression to the runner.
_INPUT_EXPRESSION_RE: Final[re.Pattern[str]] = re.compile(r"\$\{\{\s*inputs\.([A-Za-z0-9_-]+)\s*\}\}")

_INPUT_NAME_RE: Final[re.Pattern[str]] = re.compile(r"^  ([A-Za-z0-9][A-Za-z0-9_-]*):\s*$")


def render_run_body(body: str, values: Mapping[str, str]) -> str:
    """Substitute ``${{ inputs.<name> }}`` with ``values[name]``, as the runner does (PURE).

    This is the runner's behaviour and nothing more: a **textual** replacement performed BEFORE
    ``bash`` ever sees the script. No quoting, no escaping — that absence is the whole defect.
    """
    return _INPUT_EXPRESSION_RE.sub(
        lambda match: values.get(match.group(1), match.group(0)), body
    )


def declared_input_names(text: str) -> tuple[str, ...]:
    """The action's declared input names, derived from the committed `inputs:` block (PURE).

    Derived rather than transcribed so the adversarial corpus in ``-27`` covers an input added
    later, and so ``-27`` cannot pass because the name list silently went empty — ``-27`` asserts
    the derivation is non-vacuous before it asserts anything about invariance.
    """
    names: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("inputs:"):
            inside = True
            continue
        if inside and line and not line.startswith(" "):
            break
        if inside:
            match = _INPUT_NAME_RE.match(line)
            if match is not None:
                names.append(match.group(1))
    return tuple(names)


# The exact value that was executed through a real `bash` during story design: rendered into the
# pre-fix `strict` comparison it closed the `if`, ran `echo PWNED_ARBITRARY_EXECUTION; id -un`, and
# exited 0. Held here as DATA for the renderer — it is never handed to a shell by this file.
_SHELL_BREAKOUT: Final[str] = 'x" = "x" ]; then echo PWNED_ARBITRARY_EXECUTION; id -un; fi; if [ "z'

_ADVERSARIAL_VALUES: Final[tuple[str, ...]] = (
    _SHELL_BREAKOUT,
    '"; id; #',
    "$(id)",
    "`id`",
    "value\nid -un\n",
    "",
)

# AC2.2 — the PRE-FIX line, held as a LITERAL here. Never read back from `action.yml`, never from
# git history: a positive control sourced from the artifact under test stops being a control the
# moment the artifact is fixed, and this one must keep firing for as long as this file exists.
_PRE_FIX_STRICT_LINE: Final[str] = (
    '        if [ "${{ inputs.strict }}" = "true" ] && [ "$EXIT_CODE" -ne 0 ]; then'
)


def _action_yml() -> str:
    return (_REPO_ROOT / "action.yml").read_text(encoding="utf-8")


def _repository_python_sources() -> dict[str, str]:
    """Every ``.py`` file in this working tree, as ``{repo-relative posix path: source}``.

    Added 2026-08-15 by Story 12.7 so ``-30``'s *"exactly ONE definition of
    `executable_line_numbers`"* claim closes over the REPOSITORY rather than over one named file. A
    file-scoped count can only ever see the file it names, so it would have gone on passing while a
    second copy grew anywhere else — which is the shape of the very defect this module exists for.

    ``pathlib`` rather than ``git ls-files``: this module is **stdlib only, no ``subprocess``** (see
    the module docstring), and that constraint is not worth spending on a convenience. Virtual
    environments, caches and the git directory are excluded because they are not this repository's
    source; every other directory is included by default, which is the direction that keeps a new
    fork visible.
    """
    skip = {".venv", "venv", "__pycache__", ".git", ".mypy_cache", ".pytest_cache", "build", "dist"}
    found: dict[str, str] = {}
    for path in sorted(_REPO_ROOT.rglob("*.py")):
        if skip & set(path.relative_to(_REPO_ROOT).parts):
            continue
        try:
            found[path.relative_to(_REPO_ROOT).as_posix()] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):  # pragma: no cover - unreadable working-tree file
            continue
    assert found, "the repository source walk found no .py file at all — `-30` would be vacuous"
    return found


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_SECURITY_001_24_no_input_expression_survives_in_any_run_body() -> None:
    """TC-ArgusAgent-SECURITY-001-24 — THE CLOSURE. Story 11.3 / AC1.5, AC3.4, AC3.7 (`DF-9-2-D`).

    ``inputs.*`` and ``github.event.*`` inside a ``run:`` body are forbidden outright, in every
    committed workflow and in the composite action, with no exemption possible. This is the
    assertion that fails on the NEXT one anybody writes — it is not a check that today's five
    sites were fixed.
    """
    forbidden = [hit for hit in all_interpolations() if is_forbidden(hit.context)]
    assert not forbidden, (
        f"{len(forbidden)} EXPRESSION(S) ARE INTERPOLATED INTO SHELL SOURCE — this is the "
        "`DF-9-2-D` defect. The runner substitutes `${{ … }}` INTO THE SCRIPT TEXT before bash "
        "parses it, so the value is code, not data. Bind it through a step-level `env:` map and "
        'reference it as a DOUBLE-QUOTED shell variable ("$VAR"), following '
        "`.github/workflows/release.yml`. Do not add an exemption: for these two contexts none "
        "exists.\n  "
        + "\n  ".join(f"{hit.coordinate()}  {hit.context}  |  {hit.line_text}" for hit in forbidden)
    )


def test_TC_ArgusAgent_SECURITY_001_25_the_published_action_carries_zero_interpolations() -> None:
    """TC-ArgusAgent-SECURITY-001-25 — Story 11.3 / AC1.4, AC1.5, DN-3.

    ``action.yml`` is the one file in this corpus that a CONSUMER's job executes, so it carries the
    stronger claim: **zero** expressions inside any ``run:`` body, of any context, with **no**
    exemption registry entry naming it. That is why ``:68``'s ``github.action_path`` was swept too
    even though it is runner-provided and was never part of the vulnerability (DN-3) — three lines
    bought an exemption-free claim on the published artifact.

    ``:135``'s ``with: path: ${{ inputs.report-dir }}`` is deliberately NOT touched and is
    deliberately NOT a violation (DN-4): it is an action input to ``actions/upload-artifact``, not
    shell source. This test asserts that distinction rather than leaving it to prose — the sweep
    must reach every shell site and stop at the boundary of one.
    """
    text = _action_yml()
    survivors = interpolations("action.yml", text)
    assert not survivors, (
        "action.yml still interpolates inside a `run:` body — the PUBLISHED artifact must carry "
        "zero, so a consumer reading it needs no exemption registry to trust it:\n  "
        + "\n  ".join(f"{hit.coordinate()}  {hit.context}  |  {hit.line_text}" for hit in survivors)
    )
    assert not [entry for entry in _CONTEXT_EXEMPTIONS if entry.path == "action.yml"], (
        "an exemption was registered against action.yml. DN-3 ruled that the published action "
        "carries NO exemption at all; if a new one is genuinely needed, that ruling has to be "
        "revisited by name rather than by adding a row here."
    )

    upload_path = [line for line in text.splitlines() if "path: ${{ inputs.report-dir }}" in line]
    assert upload_path, (
        "`with: path: ${{ inputs.report-dir }}` is gone from the upload-artifact step. DN-4 ruled "
        "it a deliberate NON-change: it is an action input, not shell source. If it was removed "
        "on purpose, amend DN-4; if it was 'fixed' as an injection site, revert — the report "
        "directory a consumer configured is where the artifacts must come from."
    )


def test_TC_ArgusAgent_SECURITY_001_26_the_exemption_registry_is_exact_in_both_directions() -> None:
    """TC-ArgusAgent-SECURITY-001-26 — Story 11.3 / AC3.5, trap E.2.

    An unregistered survivor fails, AND a registered exemption that no longer describes anything
    real fails. A registry that can only ever grow is a hole with a comment on it.
    """
    hits = all_interpolations()

    unregistered = unregistered_survivors(hits, _CONTEXT_EXEMPTIONS)
    assert not unregistered, (
        "UNREGISTERED expression(s) survive inside a `run:` body. Either bind them through `env:` "
        f"or register each in {_GUARD_FILE}::_CONTEXT_EXEMPTIONS with a written reason stating "
        "WHY the context is trusted:\n  "
        + "\n  ".join(f"{hit.coordinate()}  {hit.context}  |  {hit.line_text}" for hit in unregistered)
    )

    stale = unmatched_exemptions(hits, _CONTEXT_EXEMPTIONS)
    assert not stale, (
        "EXEMPTION(S) DESCRIBE NOTHING THAT EXISTS — the site was fixed, moved or deleted and the "
        "permission outlived it. Remove the entry:\n  "
        + "\n  ".join(f"{entry.path} :: {entry.context} :: anchor {entry.anchor!r}" for entry in stale)
    )

    assert all(entry.reason.strip() for entry in _CONTEXT_EXEMPTIONS), (
        "every exemption states its reason; a bare entry is a permission nobody argued for"
    )
    assert not [entry for entry in _CONTEXT_EXEMPTIONS if is_forbidden(entry.context)], (
        "an `inputs.*` or `github.event.*` exemption was registered. AC3.4 admits none: those two "
        "contexts are the untrusted surface this guard exists for, and an exemption on them would "
        "reopen `DF-9-2-D` with a comment attached."
    )


def test_TC_ArgusAgent_SECURITY_001_27_run_script_text_is_invariant_under_every_input() -> None:
    """TC-ArgusAgent-SECURITY-001-27 — 🔑 THE SECURITY PROPERTY. Story 11.3 / AC2.1.

    The portable formulation of "a consumer's input cannot execute code": the ``run:`` script text
    of every step in the committed ``action.yml`` is **byte-identical** no matter what any input is
    set to — because after the sweep there is nothing left to substitute. Proven over an
    adversarial corpus that includes the exact value which executed ``id -un`` through a real
    ``bash`` during story design.

    No shell is spawned here, by design (module docstring). ``-28`` is the positive control that
    stops this assertion from being circular.
    """
    text = _action_yml()

    names = declared_input_names(text)
    assert names, (
        "the input-name derivation returned NOTHING, so the renderer below would substitute "
        "nothing and this test would pass over an empty corpus. Repair the derivation."
    )
    assert set(names) == {"repo-path", "commit-sha", "report-dir", "strict"}, (
        f"action.yml's declared inputs moved to {names!r}. The consumer contract is frozen by "
        "AC1.6 — if an input was added or renamed deliberately, that is a new consumer surface "
        "and this pin is where it gets acknowledged."
    )

    bodies = run_bodies("action.yml", text)
    assert bodies, "no `run:` body was resolved in action.yml — the assertion below is vacuous"

    drifted: list[str] = []
    for body in bodies:
        for value in _ADVERSARIAL_VALUES:
            rendered = render_run_body(body.text, {name: value for name in names})
            if rendered != body.text:
                drifted.append(
                    f"action.yml:{body.line_numbers[0]}-{body.line_numbers[-1]} moved under "
                    f"input value {value!r}"
                )
    assert not drifted, (
        "A RUN SCRIPT'S TEXT DEPENDS ON AN INPUT VALUE — the consumer's value is being pasted into "
        "the script before bash parses it, which is arbitrary code execution in the consumer's "
        "job. Bind through `env:` and quote:\n  " + "\n  ".join(drifted)
    )


def test_TC_ArgusAgent_SECURITY_001_28_the_invariance_assertion_can_actually_fail() -> None:
    """TC-ArgusAgent-SECURITY-001-28 — 🔑 MANDATORY POSITIVE CONTROL. Story 11.3 / AC2.2, trap E.3.

    ``-27`` asserts that rendering changes nothing. That is exactly what a renderer which
    substitutes nothing would also produce. So the identical assertion is applied to the **pre-fix**
    ``action.yml`` line, held as a literal string in this file, and it MUST move — and it must move
    into the shape that made the original defect a defect: the adversarial value lands unquoted in
    the middle of a ``[ … ]`` test, closing it and opening a command list.

    A test that cannot demonstrate its own failure mode has not proven anything (AI-E3-1: Story
    3.4's keystone test was green over its own keystone bug).
    """
    rendered = render_run_body(_PRE_FIX_STRICT_LINE, {"strict": _SHELL_BREAKOUT})

    assert rendered != _PRE_FIX_STRICT_LINE, (
        "THE RENDERER SUBSTITUTED NOTHING. `-27`'s invariance assertion is therefore circular and "
        "proves nothing at all — repair render_run_body before trusting this file."
    )
    assert _SHELL_BREAKOUT in rendered, (
        "the adversarial value did not reach the rendered script text; the substitution is not "
        "reproducing what the runner does"
    )
    assert "PWNED_ARBITRARY_EXECUTION" in rendered and "id -un" in rendered, (
        "the rendered pre-fix line no longer contains the injected command list, so this control "
        "is not exercising the injection shape it claims to"
    )
    assert "${{" not in rendered, "the pre-fix expression should have been consumed by the render"

    # And the whole-file closure fires on the pre-fix text too, not just the renderer. The
    # scaffold reproduces action.yml's own indentation (`run: |` at 6, script at 8) so the literal
    # is exercised exactly as it sat in the committed file.
    pre_fix_document = (
        "runs:\n"
        "  using: composite\n"
        "  steps:\n"
        "    - shell: bash\n"
        "      run: |\n" + _PRE_FIX_STRICT_LINE + "\n"
    )
    hits = interpolations("synthetic-pre-fix.yml", pre_fix_document)
    assert [hit.context for hit in hits] == ["inputs.strict"], (
        f"the closure did not detect the pre-fix site it was built to detect: {hits!r}"
    )
    assert is_forbidden(hits[0].context), "`inputs.strict` must be classified forbidden"


def test_TC_ArgusAgent_SECURITY_001_29_negative_controls_in_every_run_shape_and_a_clean_corpus() -> None:
    """TC-ArgusAgent-SECURITY-001-29 — Story 11.3 / AC3.6, AC3.7, traps E.2/E.3.

    The guard is a FILTER, and a filter can swallow the thing it looks for — §A.3 measured the
    original resolver returning an empty set for a single-line ``run:``, which is the cheapest way
    to reintroduce this defect. So each reintroduction shape must drive the detection RED, a clean
    corpus must leave it GREEN, and the hit must be attributed to the right LINE.

    **Shapes four through seven are the review's finding, and they were measured RED before the
    resolver was repaired** (Story 11.3, review iteration 1). Three shapes were not the closure
    this file claimed: a block header carrying a trailing YAML comment (``run: | # scrub inputs``),
    a block header carrying an indentation indicator (``run: >-2``), and a bare ``run:`` followed
    by a comment were each classified as the SINGLE-LINE form, so the indented body — where the
    script and the injection live — was never scanned. ``interpolations()`` returned ``()`` for
    every one of them. None is adversarial; appending a comment to a ``run: |`` is unremarkable
    CI style. Shape seven is a plain scalar CONTINUED onto the next line, which YAML folds into
    one command and which the single-line branch used to stop reading at the newline.

    ``-32`` generalises this table into the whole generated YAML block-header grammar, so this
    list is the readable statement of the property and ``-32`` is the closure over it.

    Every corpus here is SYNTHETIC. No real file is mutated to produce a control.
    """
    single_line = (
        "jobs:\n"
        "  demo:\n"
        "    steps:\n"
        '      - run: echo "${{ inputs.evil }}"\n'
    )
    block_scalar = (
        "jobs:\n"
        "  demo:\n"
        "    steps:\n"
        "      - run: |\n"
        '          echo "${{ inputs.evil }}"\n'
    )
    line_wrapped = (
        "jobs:\n"
        "  demo:\n"
        "    steps:\n"
        "      - run: |\n"
        '          echo "${{\n'
        "            inputs.evil }}\"\n"
    )
    commented_block = (
        "jobs:\n"
        "  demo:\n"
        "    steps:\n"
        "      - run: | # scrub inputs before use\n"
        '          echo "${{ inputs.evil }}"\n'
    )
    indicator_block = (
        "jobs:\n"
        "  demo:\n"
        "    steps:\n"
        "      - run: >-2\n"
        '          echo "${{ inputs.evil }}"\n'
    )
    bare_key_commented = (
        "jobs:\n"
        "  demo:\n"
        "    steps:\n"
        "      - run: # the script follows\n"
        '          echo "${{ inputs.evil }}"\n'
    )
    continued_scalar = (
        "jobs:\n"
        "  demo:\n"
        "    steps:\n"
        '      - run: echo "${{\n'
        '          inputs.evil }}"\n'
    )
    clean = (
        "jobs:\n"
        "  demo:\n"
        "    steps:\n"
        "      - env:\n"
        "          EVIL: ${{ inputs.evil }}\n"
        '        run: echo "$EVIL"\n'
        "      - env:\n"
        "          EVIL: ${{ inputs.evil }}\n"
        "        run: |\n"
        '          echo "$EVIL"\n'
        # The repaired shapes must also be able to go GREEN: a commented block header over an
        # `env:`-bound body is the correct way to write this, and a guard that fired on it would
        # be teaching authors that the fix does not help them.
        "      - env:\n"
        "          EVIL: ${{ inputs.evil }}\n"
        "        run: |- # values arrive as environment variables, never as script text\n"
        '          echo "$EVIL"\n'
    )

    for label, document, expected_line in (
        ("single-line `- run: cmd`", single_line, 4),
        ("block scalar `run: |`", block_scalar, 5),
        ("line-wrapped `${{` with the context on the NEXT line", line_wrapped, 5),
        ("block scalar with a TRAILING COMMENT `run: | # …`", commented_block, 5),
        ("block scalar with an INDENTATION indicator `run: >-2`", indicator_block, 5),
        ("bare `run:` with a COMMENT, script indented beneath", bare_key_commented, 5),
        ("single-line scalar CONTINUED onto the next line", continued_scalar, 4),
    ):
        hits = interpolations("synthetic.yml", document)
        forbidden = [hit for hit in hits if is_forbidden(hit.context)]
        assert forbidden, (
            f"THE GUARD IS BLIND TO THE {label} FORM. It would pass while the vulnerability "
            "stands, which is precisely the vacuous-guard failure this file was written to avoid."
        )
        assert forbidden[0].context == "inputs.evil", forbidden
        assert forbidden[0].line_number == expected_line, (
            f"{label}: the hit was attributed to line {forbidden[0].line_number}, not to the line "
            f"carrying its `${{{{` ({expected_line}). AC3.7 requires a navigable file:line."
        )

    clean_hits = interpolations("synthetic-clean.yml", clean)
    assert clean_hits == (), (
        "the guard fired on an `env:`-bound, double-quoted corpus — the very shape it is asking "
        f"authors to write. A guard that cannot go green is deleted by the third person to hit "
        f"it: {clean_hits!r}"
    )

    # Direction two of the registry, on synthetic data, so E.2's "a registry that cannot go red is
    # theatre" is proven rather than asserted.
    phantom = ContextExemption(
        path="synthetic-clean.yml", context="github.sha", anchor="nothing here", reason="synthetic"
    )
    assert unmatched_exemptions(clean_hits, (phantom,)) == (phantom,), (
        "the stale-exemption check did not fire on an entry describing nothing"
    )
    real_hits = interpolations(
        "synthetic-trusted.yml",
        "jobs:\n  demo:\n    steps:\n      - run: echo \"${{ github.sha }}\"\n",
    )
    matching = ContextExemption(
        path="synthetic-trusted.yml", context="github.sha", anchor="echo", reason="synthetic"
    )
    assert unmatched_exemptions(real_hits, (matching,)) == ()
    assert unregistered_survivors(real_hits, (matching,)) == ()
    assert unregistered_survivors(real_hits, ()) == real_hits, (
        "an untrusted-but-unregistered survivor was not reported; direction one of the registry "
        "is not firing"
    )


def test_TC_ArgusAgent_SECURITY_001_30_the_guard_is_not_vacuous_and_owns_no_second_resolver() -> None:
    """TC-ArgusAgent-SECURITY-001-30 — Story 11.3 / AC3.1, AC3.3, AR7 / architecture §3.3.

    Two failure modes, both of which have bitten this project:

    1. *The corpus or the resolver silently returns nothing* and every assertion above passes over
       an empty set (``CLI-001-39``'s lesson, made mandatory).
    2. *The rule gets implemented twice* and the two copies drift. ``executable_line_numbers`` is
       the SINGLE definition of "which lines are shell source?" in this repository; this file
       imports it. A private re-implementation here would have re-created exactly the block-scalar
       blindness that §A.3 measured — in a second place, where the next person would not look.
    """
    paths = corpus_paths()
    assert paths, (
        "THE CORPUS GLOB RESOLVED TO NOTHING. Every assertion in this file is vacuous until this "
        "is repaired — do NOT delete a test to get green."
    )
    assert "action.yml" in paths, (
        f"the corpus no longer reaches action.yml, the one file a CONSUMER executes: {paths}"
    )
    assert ".github/workflows/argus-student-audit.yml" in paths, (
        f"the corpus no longer reaches the workflows directory: {paths}"
    )

    bodies = run_bodies("action.yml", _action_yml())
    assert len(bodies) >= 2, (
        f"the resolver found {len(bodies)} `run:` bodies in action.yml; it has at least two "
        "(install and audit), so the resolver is no longer resolving"
    )

    # CORRECTED 2026-08-15 by Story 12.7, and STRENGTHENED rather than relaxed. The resolver moved
    # from `tests/test_invocation_contract.py` to its sibling `tests/invocation_sources.py` when
    # that file crossed the NFR-M1 ceiling (a cohesion split with a re-export; every import path is
    # unchanged, which is why the import assertion below still reads the same). Simply re-pointing
    # `_RESOLVER_FILE` would have preserved the letter of this check and lost its POINT — the claim
    # is *"exactly one definition exists"*, and a file-scoped count can only ever see the file it
    # names. So the count now closes over EVERY tracked `.py` in the repository: a fork anywhere is
    # red, including in a file nobody thought to name here.
    # Matched as a DEFINITION at the start of a line, never as a substring, for the reason the
    # comment below the next assertion already gives: this module names the symbol repeatedly in
    # its own prose and assertion messages, and a bare substring count fires on itself.
    _definition = re.compile(r"^\s*def executable_line_numbers\s*\(", re.MULTILINE)
    definitions = {
        rel: len(_definition.findall(source))
        for rel, source in _repository_python_sources().items()
        if _definition.search(source)
    }
    assert definitions == {_RESOLVER_FILE: 1}, (
        "`executable_line_numbers` must be declared EXACTLY ONCE in this repository, in "
        f"{_RESOLVER_FILE}. Measured: {definitions}. AR7 / architecture §3.3 — a rule implemented "
        "twice drifts in one of the two, and this one decides which lines are shell source."
    )
    resolver_source = (_REPO_ROOT / _RESOLVER_FILE).read_text(encoding="utf-8")
    assert "def _executable_line_numbers(" not in resolver_source, (
        "the private spelling is back alongside the public one — that is two names for one rule, "
        "which is how a caller ends up on the stale copy"
    )

    own_source = (_REPO_ROOT / _GUARD_FILE).read_text(encoding="utf-8")
    # Matched as a DEFINITION at the start of a line, not as a substring: this test names the
    # symbol several times in its own assertion messages, and a bare `in` check would fail on its
    # own prose — a control that fires on itself teaches the next reader to delete it.
    assert re.search(r"^\s*def executable_line_numbers", own_source, re.MULTILINE) is None, (
        f"{_GUARD_FILE} has grown its OWN run-block resolver. AR7 / architecture §3.3 forbid a "
        f"second mechanism where one exists: import it from {_RESOLVER_FILE}."
    )
    assert "from tests.test_invocation_contract import executable_line_numbers" in own_source, (
        "the import from the single declaration was removed"
    )
    assert executable_line_numbers.__module__ == "tests.invocation_sources", (
        "the imported resolver is no longer the one declared in "
        f"{_RESOLVER_FILE}: {executable_line_numbers.__module__}. The import path above is a "
        "RE-EXPORT and is preserved on purpose; what must not change is which function it reaches."
    )

    # The generalisation itself, asserted rather than trusted: the ORIGINAL rule returned an empty
    # set for this input, and that blindness is what made the obvious guard vacuous (§A.3).
    assert executable_line_numbers('      - run: echo "${{ inputs.evil }}"\n', ".yml") == {1}, (
        "the resolver stopped recognising the SINGLE-LINE `run:` form. A guard built on it is "
        "blind to the cheapest way to reintroduce DF-9-2-D."
    )
    assert executable_line_numbers("      - run: |\n          echo hi\n", ".yml") == {2}, (
        "the resolver stopped recognising the BLOCK-SCALAR `run:` form"
    )


def test_TC_ArgusAgent_SECURITY_001_31_the_consumer_contract_of_the_action_is_frozen() -> None:
    """TC-ArgusAgent-SECURITY-001-31 — Story 11.3 / AC1.6, §C.1, §C.4.

    The sweep was required to change the SHAPE of the script and nothing a consumer can observe.
    Everything below is a published surface Story 9.2 / ``DF-8-4-A`` wrote deliberately, over which
    this story has no mandate, and each is the kind of thing an over-eager "hardening" edit takes
    with it: the input defaults, the output names, the complete exit-code map, its ``::error::``
    strings, and ``assessed``.

    ``set -euo pipefail`` is asserted ABSENT on purpose (§C.4): the audit step uses ``set +e`` /
    ``set -e`` around the audit alone so a non-zero exit is CAPTURED and MAPPED rather than
    aborting the step. Adding ``-u``/``pipefail`` would change the failure semantics of a shipped
    consumer contract for no security benefit once the values are ``env:``-bound.
    """
    text = _action_yml()

    for expected in (
        'default: "."',
        'default: "${{ github.sha }}"',
        'default: "./argus-reports"',
        'default: "false"',
        "value: ${{ steps.run_audit.outputs.verdict }}",
        "value: ${{ steps.run_audit.outputs.exit_code }}",
        "value: ${{ steps.run_audit.outputs.assessed }}",
        'echo "exit_code=$EXIT_CODE" >> $GITHUB_OUTPUT',
        'echo "verdict=RELEASE_READY" >> $GITHUB_OUTPUT',
        'echo "verdict=NOT_READY_FOR_RELEASE" >> $GITHUB_OUTPUT',
        'echo "verdict=INSUFFICIENT_COVERAGE" >> $GITHUB_OUTPUT',
        'echo "verdict=AUDIT_FAILED" >> $GITHUB_OUTPUT',
        'echo "assessed=true" >> $GITHUB_OUTPUT',
        'echo "assessed=false" >> $GITHUB_OUTPUT',
        "::error::Argus exited 1 (AR10 typed failure)",
        "::error::Argus exited with the unmapped code $EXIT_CODE",
        "❌ Argus Release Gate failed with exit code $EXIT_CODE",
        "exit $EXIT_CODE",
    ):
        assert expected in text, (
            f"action.yml lost a frozen consumer-contract element: {expected!r}. Story 11.3 was an "
            "injection sweep with NO mandate over behaviour (§C.1); if this changed on purpose it "
            "is a behavioural change to a published action and belongs to its own story."
        )

    assert "set -euo pipefail" not in text, (
        "`set -euo pipefail` was added to the audit step. §C.4: the step deliberately brackets the "
        "audit with `set +e` / `set -e` so a non-zero exit is captured and mapped to a verdict "
        "token instead of aborting. `-u`/`pipefail` change a shipped failure contract."
    )
    assert "set +e" in text and "set -e" in text, (
        "the `set +e` / `set -e` bracket around the audit call is gone — the exit-code map below "
        "it can no longer run, because a non-zero exit now aborts the step"
    )


def _block_header_spellings() -> tuple[str, ...]:
    """Every spelling YAML's `c-b-block-header` grammar gives a `run:` block scalar (PURE).

    GENERATED, not listed — that is the point of ``-32``. The grammar is: a style indicator
    (``|`` literal or ``>`` folded), then an OPTIONAL indentation indicator (a digit) and an
    OPTIONAL chomping indicator (``-`` strip or ``+`` keep) **in either order**, then optionally
    a comment. Every combination is legal YAML and every one is a block scalar, so every one must
    reach the indented body. Enumerating by hand is how the first three shipped and the other
    fifteen did not.
    """
    suffixes: list[str] = []
    for indentation in ("", "1", "2", "3"):
        for chomping in ("", "-", "+"):
            orders = {indentation + chomping, chomping + indentation}
            suffixes.extend(sorted(orders))
    return tuple(
        f"{style}{suffix}{comment}"
        for style in ("|", ">")
        for suffix in sorted(set(suffixes))
        for comment in ("", " # scrub inputs before use", " #no space after the hash")
    )


def test_TC_ArgusAgent_SECURITY_001_32_every_block_header_spelling_reaches_the_body() -> None:
    """TC-ArgusAgent-SECURITY-001-32 — 🔑 THE HEADER GRAMMAR IS CLOSED. Story 11.3 / AC3.2, §C.6.

    **Why this test exists, stated plainly so it is never deleted as redundant.** ``-29`` shipped
    with three shapes and the review found a fourth that defeated the whole guard silently:
    ``run: | # scrub inputs before use``. The remainder after the block indicator was non-empty, so
    the resolver called the line a single-line command, never set ``run_indent``, and never read
    the indented body at all — ``interpolations()`` returned ``()`` against an action.yml-shaped
    document with ``echo "${{ inputs.strict }}"`` in it. That is the story's own "-17b lesson"
    (trap E.3, a filter swallowing what it looks for) reproduced one shape further out, and the
    lesson of it is that **another hand-written list of shapes is the same mistake again**.

    So this asserts over the GENERATED cross product of YAML's block-header grammar — style x
    indentation indicator x chomping indicator x comment, both indicator orders — and for each
    spelling requires:

    1. the header line is NOT itself reported as shell source (it is a header and, at most, a
       comment — the script is what follows), and
    2. the indented body IS scanned, and
    3. the ``inputs.*`` interpolation hidden in that body is detected, forbidden, and attributed
       to the body's line number.

    Measured before the repair: **9 of these spellings returned an empty hit set**, including
    every commented one and every one carrying an indentation indicator (a digit is not ``[-+]``,
    so ``run: |2`` fell through the same hole with no comment involved at all).

    The bodies are indented deeper than the header in every case, so what is under test is the
    HEADER classification and not the indentation indicator's arithmetic — which this resolver
    deliberately does not model, because a text scan that guesses at YAML's indentation rules
    would be a second, worse YAML parser (DN-5: stdlib only, no ``PyYAML``).
    """
    spellings = _block_header_spellings()
    assert len(spellings) >= 100, (
        f"the header-grammar generator collapsed to {len(spellings)} spellings; if it can go "
        "empty or small, every assertion below is vacuous"
    )
    assert "|" in spellings and "| # scrub inputs before use" in spellings, (
        "the generated grammar no longer contains the plainest block header, or the exact shape "
        "the Story 11.3 review found the guard blind to"
    )

    blind: list[str] = []
    misattributed: list[str] = []
    header_claimed: list[str] = []
    for spelling in spellings:
        document = (
            "runs:\n"
            "  using: composite\n"
            "  steps:\n"
            "    - name: audit\n"
            "      shell: bash\n"
            f"      run: {spelling}\n"
            '        echo "${{ inputs.evil }}"\n'
        )
        if 6 in executable_line_numbers(document, ".yml"):
            header_claimed.append(spelling)
        hits = [hit for hit in interpolations("synthetic.yml", document) if is_forbidden(hit.context)]
        if not hits:
            blind.append(spelling)
        elif hits[0].line_number != 7:
            misattributed.append(f"{spelling} -> line {hits[0].line_number}")

    assert not blind, (
        f"THE GUARD IS BLIND TO {len(blind)} OF {len(spellings)} LEGAL `run:` BLOCK HEADERS. Each "
        "is ordinary YAML a contributor could write without any intent to evade, and against each "
        "one an `${{ inputs.* }}` in the script body goes UNDETECTED — `DF-9-2-D` reopens silently "
        "and this guard stays green. Classify on the PRESENCE of the `|`/`>` indicator, not on "
        "whether the remainder of the line is empty: YAML permits only a comment after a block "
        f"header, so the remainder is never the command.\n  {blind}"
    )
    assert not misattributed, (
        "the hit was attributed to the wrong line for some spellings; AC3.7 requires a navigable "
        f"file:line, and a header line is not where the script is:\n  {misattributed}"
    )
    assert not header_claimed, (
        "the block-scalar HEADER line was reported as shell source for some spellings. It is not "
        "shell source — the script is the indented body — and reporting it would make a `${{ }}` "
        f"in a YAML COMMENT a violation:\n  {header_claimed}"
    )
