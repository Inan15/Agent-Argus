"""Release NOTE and release STATUS — derived from their single sources, never transcribed.

Story 12.9 / AC2 + AC3 (epics IN-0, boundary B10). Two facts about a release used to be
typed by hand and could not track what they described:

* ``.github/workflows/release.yml:174-190`` built the GitHub Release body as a **string
  literal inside a ``run:`` script**, transcribing the AR3 exit-code contract, the install
  command and a *paraphrase* of the FR34 disclosure. Story 12.8 changed what exit ``2`` can
  mean and that literal did not move, **because nothing could see it**: ``release.yml`` is a
  registered release surface, so ``TC-ArgusAgent-DOCS-001-17`` scans it for over-*claims* —
  no guard checked whether what it said was **true**.
* the project's **release status** was written by hand wherever it appeared, which is the
  transcription class that produced ``DF-AUD-APAA-C``: ``sprint-change-proposal-2026-07-28.md``
  declared a status that no executed gate supported — the *"…FOR RELEASE"* upgrade at its
  line 63 — on a local ``pytest`` run, while the CI gate that same proposal had just created
  had never passed (run ``30774175196``, ``failure``).

So both are computed here, in ONE place, from observed facts:

* the **version** from ``pyproject.toml`` (via :mod:`release_preflight`, reused not forked);
* the **exit-code map** from ``argus/verdict/verdict_gate.py`` — the ``Verdict`` enum and
  ``_EXIT_CODE_BY_VERDICT`` — plus AR3's reserved code from ``argus/cli.py``'s
  ``_CRASH_EXIT_CODE``;
* the **FR34 disclosure** from ``argus/verdict/negative_assurance.py`` in its canonical
  single-sourced form, selected by that module's own ``INSTRUMENT_STATUS`` declaration —
  never a paraphrase;
* the **install command** from the tag under release;
* the **release status** from :func:`derive_release_status`, which returns a sha-scoped
  citation or the first-class ``NOT ESTABLISHED`` state (architecture.md §H, Story 10.1).

**Design constraint, load-bearing (Story 12.9 / DN-4).** ``scripts/release_preflight.py``
is stdlib-only because it *"must run on a bare GitHub runner before the package (or anything
else) is installed"*. This module runs in the same step-order and takes the same contract:
**stdlib only, and it never imports ``argus``.** It reads the single-source modules as TEXT
and parses them with :mod:`ast`, and a committed test — which may import ``argus`` freely —
asserts the derivation equals the live constants **in both directions**
(``tests/test_release_note_body.py``). That is exactly the shape
``TC-ArgusAgent-DOCS-001-63``/``-64`` already use for ``docs/first-run.md``.

The alternative — moving the notes step in ``release.yml`` to *after* ``pip install
dist/*.whl`` so this could ``import argus`` — was considered and REJECTED: it makes the
release note depend on a successful install of the very thing being released, and puts a
second Python-environment assumption into a job holding ``contents: write``.

**NFR-S1 containment.** Everything rendered here is a tag, a version, an exit code, a
relative path or a committed sentence. No credential, no secret, no absolute host path.

**Nothing here publishes.** This module renders text and prints it. Creating a tag, pushing
one, or creating a GitHub Release are operator acts (Story 12.9 / AC9).
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:  # pragma: no cover - import bootstrap
    sys.path.insert(0, str(_SCRIPTS_DIR))

import release_preflight as rp  # noqa: E402

__all__ = [
    "GateObservation",
    "ReleaseStatus",
    "RECORDED_GATE_OBSERVATION",
    "REPOSITORY_VISIBILITY_MEASUREMENT",
    "NOT_ESTABLISHED",
    "derive_release_status",
    "exit_code_contract",
    "instrument_disclosure",
    "install_command",
    "render_release_note",
    "render_release_status",
    "main",
]

# The literal the whole rule turns on. Story 10.1 / architecture.md §H: a status claim cites
# an executed gate, or it records THIS — which is a first-class recordable state, the
# governance twin of `AUDIT_FAILED`-is-not-a-verdict, and writing it is compliance rather
# than failure.
NOT_ESTABLISHED = "NOT ESTABLISHED"

_VERDICT_GATE = "argus/verdict/verdict_gate.py"
_NEGATIVE_ASSURANCE = "argus/verdict/negative_assurance.py"
_CLI = "argus/cli.py"

_REPOSITORY = "Inan15/Agent-Argus"
_GATE_WORKFLOW = "audit-ci.yml"


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — the release status, DERIVED
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class GateObservation:
    """What was observed about the gate, and when. The INPUT to the derivation.

    Injected rather than fetched, for the same reason
    :class:`release_preflight.PreflightContext` is: the rule must be provable offline and
    deterministically, and the impure half (a ``gh`` read) belongs at the edge. The fields
    are exactly what architecture.md §H requires a citation to carry — a run id, **the sha
    that run covers**, its conclusion and its leg count — plus the date the observation was
    taken, because an observation with no date is a claim about an unknown *time* in the
    same way a bare run id is a claim about an unknown *tree*.

    ``run_id = ""`` means *no run was observed at all*, which is a different fact from *a run
    was observed and it does not cover this commit*; the derivation states which.
    """

    run_id: str
    run_sha: str
    conclusion: str
    legs: str
    workflow: str
    measured_on: str
    behind_by: int = 0


@dataclass(frozen=True)
class ReleaseStatus:
    """A derived release status: either a sha-scoped citation, or ``NOT ESTABLISHED``.

    ``established`` is the machine answer; ``statement`` is the sentence every surface
    publishes. Surfaces render ``statement`` — they never re-type its contents, which is
    what makes AI-E9-7 hold here rather than being asserted.
    """

    established: bool
    statement: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.statement


# ─────────────────────────────────────────────────────────────────────────────
# THE RECORDED OBSERVATION — one dated measurement, one place.
#
# Taken 2026-08-15 through the GitHub API, read-only:
#
#     gh run list --workflow=audit-ci.yml --branch master --json databaseId,headSha,conclusion
#     git rev-list --left-right --count origin/master...master   ->   0   34
#
# The newest `audit-ci.yml` run on `master` is 31341363300, `success`, at sha 00c8d1b
# (2026-08-09), and `origin/master` is 34 commits BEHIND local `master` — every commit Epics
# 10, 11 and 12 produced is local only. So no executed gate covers the commit being released,
# and none CAN exist until `master` is pushed, which is an outward-facing operator act.
#
# ⚠️ Citing run 31341363300 for this release is FORBIDDEN and the prohibition is not
# stylistic: `architecture.md:614-616` uses THIS RUN ID as its worked example of a half-truth
# (*"`run 31341363300` is a half-truth; `run 31341363300 (00c8d1b, 3/3 legs green)` is the
# claim"*). The derivation below therefore names it as SUPERSEDED, with its sha, inside a
# NOT ESTABLISHED statement — which is the honest use of it and the only one.
# ─────────────────────────────────────────────────────────────────────────────
RECORDED_GATE_OBSERVATION = GateObservation(
    run_id="31341363300",
    run_sha="00c8d1b",
    conclusion="success",
    legs="3/3",
    workflow=_GATE_WORKFLOW,
    measured_on="2026-08-15",
    behind_by=34,
)


def _covers(observation: GateObservation, released_sha: str) -> bool:
    """Does *observation*'s run cover *released_sha*? Prefix-tolerant, both ways.

    Shas are published abbreviated and observed in full, so equality is the wrong test and a
    naive one would report *no run covers this* for a run that plainly does. The comparison
    is anchored at the START of both strings, so it can never accept an unrelated sha that
    merely shares a suffix.
    """
    if not observation.run_sha or not released_sha:
        return False
    shortest = min(len(observation.run_sha), len(released_sha))
    if shortest < 7:
        return False
    return observation.run_sha[:shortest] == released_sha[:shortest]


def derive_release_status(
    observation: GateObservation, released_sha: str
) -> ReleaseStatus:
    """THE derivation. Every surface that states a release status renders this value.

    A status is ESTABLISHED only when the observed run both **covers the commit being
    released** and **succeeded**. Anything else is ``NOT ESTABLISHED`` with the reason named,
    the superseded run stated as what it is — *with its sha, because a run id without its sha
    is a half-truth* — and the exact human step that would establish one.

    Pure: no clock, no network, no subprocess. The impure half is
    :func:`released_sha_of_checkout` and the ``gh`` read that produced
    :data:`RECORDED_GATE_OBSERVATION`.
    """
    if _covers(observation, released_sha) and observation.conclusion == "success":
        return ReleaseStatus(
            established=True,
            statement=(
                f"CI evidence: run {observation.run_id} "
                f"({observation.run_sha}, {observation.legs} legs green) on "
                f"`{observation.workflow}` covers the commit being released. "
                f"Observed {observation.measured_on} through the GitHub API."
            ),
        )

    if not observation.run_id:
        reason = (
            f"no `{observation.workflow}` run was observed on this repository at all"
        )
    elif not _covers(observation, released_sha):
        behind = (
            f", {observation.behind_by} commits behind the commit being released"
            if observation.behind_by
            else ""
        )
        reason = (
            f"the most recent `{observation.workflow}` run is run {observation.run_id}, "
            f"which covers sha {observation.run_sha}{behind} and therefore evidences a "
            "different tree; a run id quoted without the sha it covers is a half-truth, so "
            "it is named here as SUPERSEDED rather than cited"
        )
    else:
        reason = (
            f"run {observation.run_id} covers sha {observation.run_sha}, the commit being "
            f"released, but concluded `{observation.conclusion}` rather than `success`"
        )

    return ReleaseStatus(
        established=False,
        statement=(
            f"CI evidence: {NOT_ESTABLISHED}. No executed gate covers the commit being "
            f"released — {reason}. Observed {observation.measured_on} through the GitHub "
            "API. The human step that would establish one, and the only one: push `master` "
            f"to `origin` and let `{observation.workflow}` run to success on the released "
            "commit, then re-derive this sentence from that run. A local "
            "`pytest`/`mypy`/`bandit` run is necessary, not sufficient, and is recorded as "
            "LOCAL (architecture.md §H)."
        ),
    )


def render_release_status(released_sha: str) -> str:
    """The published status sentence for *released_sha*, from the recorded observation."""
    return derive_release_status(RECORDED_GATE_OBSERVATION, released_sha).statement


def released_sha_of_checkout(repo_root: Path) -> str:
    """``HEAD``'s sha (the impure half; AR8). Empty string when git cannot be asked."""
    return rp._git(repo_root, "rev-parse", "HEAD")


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — the repository-visibility measurement, one dated sentence, one place
# ─────────────────────────────────────────────────────────────────────────────

# A repository's visibility can change under a document that asserts it, so this is written
# as a DATED MEASUREMENT WITH ITS COMMAND rather than as a standing claim — and it is stated
# once here and rendered onto every surface that publishes it, so the three copies cannot
# drift the way `README.md` and `CHANGELOG.md` drifted while both admitted they had never
# looked. Measured 2026-08-15, read-only.
REPOSITORY_VISIBILITY_MEASUREMENT = (
    "Repository visibility, MEASURED 2026-08-15 by "
    f"`gh repo view {_REPOSITORY} --json visibility,isPrivate` -> `PRIVATE` / "
    "`isPrivate: true`. What that costs a consumer, stated plainly: while it stays private "
    "the pinned install cannot resolve for anybody — tag or no tag — without a read "
    "credential carried in the URL (`git+https://<credential>@github.com/...`), and a GitHub "
    "Release on a private repository is not publicly resolvable either. Making the "
    "repository public is an outward-facing operator act that has not been taken. This is a "
    "dated measurement, not a standing claim: re-run the command above before relying on it."
)


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — the facts in the note, each read from its single source
# ─────────────────────────────────────────────────────────────────────────────


def _module_ast(repo_root: Path, relative: str) -> ast.Module:
    return ast.parse((repo_root / relative).read_text(encoding="utf-8"))


def _assigned_value(tree: ast.Module, name: str) -> ast.expr:
    """The value expression assigned to module-level *name*. Raises when absent.

    Raises rather than returning ``None``: a single source that has been renamed or moved is
    the recognizer-that-stopped-recognizing defect this project has recorded four times, and
    the only safe answer is to fail loudly at render time (``DF-10-4-E``'s lesson).
    """
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and target.id == name and node.value:
                return node.value
    raise ValueError(
        f"the single source no longer declares {name!r}; the release note cannot be "
        "rendered from a fact it can no longer read. Fix the derivation, never the note."
    )


def _verdict_tokens(repo_root: Path) -> dict[str, str]:
    """``{member name: published token}`` for every ``Verdict`` member.

    The published token is the enum's VALUE, read from the class body — not its member name.
    They happen to coincide today, and assuming that is exactly how a transcription gets in.
    """
    tree = _module_ast(repo_root, _VERDICT_GATE)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Verdict":
            tokens: dict[str, str] = {}
            for item in node.body:
                if (
                    isinstance(item, ast.Assign)
                    and len(item.targets) == 1
                    and isinstance(item.targets[0], ast.Name)
                    and isinstance(item.value, ast.Constant)
                    and isinstance(item.value.value, str)
                ):
                    tokens[item.targets[0].id] = item.value.value
            if not tokens:
                raise ValueError("the Verdict enum parsed to no members")
            return tokens
    raise ValueError(f"{_VERDICT_GATE} no longer declares `class Verdict`")


def exit_code_contract(repo_root: Path) -> tuple[tuple[str, int], ...]:
    """The AR3 wire contract as ``((token, code), ...)``, derived from the code.

    ``_EXIT_CODE_BY_VERDICT`` is the exhaustive verdict half; ``argus/cli.py``'s
    ``_CRASH_EXIT_CODE`` is the reserved *no verdict was produced* code, which is NOT a
    verdict and is stated as such. Ordering is by code, so the rendered sentence is
    deterministic (AR4) and a re-render never produces a diff for no reason.
    """
    tokens = _verdict_tokens(repo_root)
    mapping = _assigned_value(_module_ast(repo_root, _VERDICT_GATE), "_EXIT_CODE_BY_VERDICT")
    if not isinstance(mapping, ast.Dict):
        raise ValueError("_EXIT_CODE_BY_VERDICT is no longer a dict literal")

    contract: list[tuple[str, int]] = []
    for key, value in zip(mapping.keys, mapping.values):
        if (
            isinstance(key, ast.Attribute)
            and isinstance(key.value, ast.Name)
            and key.value.id == "Verdict"
            and isinstance(value, ast.Constant)
            and isinstance(value.value, int)
        ):
            contract.append((tokens[key.attr], value.value))
    if len(contract) != len(tokens):
        raise ValueError(
            f"the AR3 map covers {len(contract)} of {len(tokens)} Verdict members; it is "
            "declared exhaustive and a partial read would publish a partial contract"
        )

    crash = _assigned_value(_module_ast(repo_root, _CLI), "_CRASH_EXIT_CODE")
    if not isinstance(crash, ast.Constant) or not isinstance(crash.value, int):
        raise ValueError("argus/cli.py's _CRASH_EXIT_CODE is no longer an int literal")
    contract.append(("no verdict produced", crash.value))
    return tuple(sorted(contract, key=lambda pair: pair[1]))


def instrument_disclosure(repo_root: Path) -> str:
    """The FR34 disclosure in its CANONICAL single-sourced form — never a paraphrase.

    Which of the two texts applies is itself derived: ``negative_assurance.INSTRUMENT_STATUS``
    names the declared status, and the matching ``INSTRUMENT_DISCLOSURE_<STATUS>`` constant is
    the text. So the day Epic 13's adjudication flips that declaration, the release note
    changes with it instead of publishing a stale disclosure — or, if the constant is renamed,
    this raises rather than quietly emitting nothing.
    """
    tree = _module_ast(repo_root, _NEGATIVE_ASSURANCE)
    declared = _assigned_value(tree, "INSTRUMENT_STATUS")
    if not isinstance(declared, ast.Attribute):
        raise ValueError("INSTRUMENT_STATUS is no longer a single enum-member reference")
    text = _assigned_value(tree, f"INSTRUMENT_DISCLOSURE_{declared.attr}")
    if not isinstance(text, ast.Constant) or not isinstance(text.value, str):
        raise ValueError(
            f"INSTRUMENT_DISCLOSURE_{declared.attr} is no longer a plain string constant"
        )
    return text.value


def install_command(tag: str) -> str:
    """The VCS pin for *tag*. The one place the release channel's install line is built."""
    return (
        f'pip install "argus-agent @ git+https://github.com/{_REPOSITORY}.git@{tag}"'
    )


# ─────────────────────────────────────────────────────────────────────────────
# The generator
# ─────────────────────────────────────────────────────────────────────────────


def render_release_note(
    tag: str,
    *,
    repo_root: Path,
    released_sha: str,
    observation: GateObservation = RECORDED_GATE_OBSERVATION,
) -> str:
    """The GitHub Release body. Every factual claim in it is derived above.

    The tag/version agreement is checked by **E5's own handler** rather than by a second
    comparison written here (AR7 reuse-not-fork): if the two disagree the note refuses to
    render at all, because a release note is the last place a version should be discovered
    to be wrong.
    """
    version = rp.read_pyproject_version(repo_root)
    mismatch = rp.check_e5_tag_version_mismatch(
        rp.PreflightContext(repo_root=repo_root, tag=tag, pyproject_version=version)
    )
    if mismatch is not None:
        raise ValueError(f"refusing to render a release note: {mismatch}")

    codes = ", ".join(f"{code}={token}" for token, code in exit_code_contract(repo_root))
    status = derive_release_status(observation, released_sha)

    return "\n".join(
        (
            f"Source distribution and wheel for `argus-agent` {tag}.",
            "",
            "Install directly from this repository at this tag:",
            "",
            f"    {install_command(tag)}",
            "",
            f"{REPOSITORY_VISIBILITY_MEASUREMENT}",
            "",
            f"The exit-code wire contract is UNCHANGED by this release: {codes}. "
            "Exit 1 is reserved and is never a verdict — a run that produced no verdict "
            "made no statement about your code. See CHANGELOG.md for the full consumer "
            "contract.",
            "",
            f"{status.statement}",
            "",
            "This release makes no assurance claim about Argus itself. Argus's dogfood run "
            "is a self-audit and is not independent corroboration.",
            "",
            f"{instrument_disclosure(repo_root)}",
        )
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render the GitHub Release note body.")
    parser.add_argument("--tag", required=True, help="the version tag, e.g. v0.1.0")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--released-sha",
        default="",
        help="the commit being released; defaults to HEAD of --repo-root",
    )
    parser.add_argument(
        "--out",
        default="",
        help=(
            "write the body to this path with an EXPLICIT utf-8 encoding instead of "
            "printing it. The workflow uses this: the note carries non-ASCII, and an "
            "inherited host locale on the writing end is the exact defect class that "
            "turned run 31322881580 red"
        ),
    )
    args = parser.parse_args(argv)

    # The SAME shape check release_preflight applies, in the FIRST step that touches the
    # value: `--tag` carries an untrusted workflow_dispatch input, bound through `env:` and
    # quoted by the caller. A crafted value stops here as well as there.
    if rp.normalize_tag(args.tag) is None:
        print(
            f"REFUSING to render a release note: tag {args.tag!r} is not a version tag. "
            "The expected shape is v<major>.<minor>.<patch> (e.g. v0.1.0)."
        )
        return 1

    repo_root = Path(args.repo_root).resolve()
    released_sha = args.released_sha or released_sha_of_checkout(repo_root)
    body = render_release_note(args.tag, repo_root=repo_root, released_sha=released_sha)
    if args.out:
        Path(args.out).write_text(body + "\n", encoding="utf-8")
        print(f"release note body written to {args.out} ({len(body)} characters)")
    else:
        print(body)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
