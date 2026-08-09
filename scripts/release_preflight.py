"""Release preflight — the ENUMERATED release edge cases, and the refusal for each.

Story 9.2 / AC5 (epics boundary **B10**). ``argus-agent`` had no release path at all
before this story: ``.github/workflows/`` held two audit workflows, neither of which
built, tagged or published anything, and ``git tag -l`` was empty. A release path added
without an explicit refusal for each failure mode is a path that produces artifacts whose
provenance cannot be established — the same defect class Epic 8 spent five stories
removing from the verdict, moved into the packaging.

**The enumeration is the contract.** :data:`RELEASE_EDGE_CASE_IDS` is the single named
place the space is declared, and :data:`_HANDLERS` maps each id to the check that refuses
it. The two are asserted equal by a committed test
(``TC-ArgusAgent-RELEASE-001-01``), so adding a member to the enumeration WITHOUT writing
its handler fails the build — which is what makes this an enumerated space rather than a
list of the cases someone happened to think of. Per **AI-E8-6**, a test that exercises
one case and passes would be a breach of AC5, not a satisfaction of it, so every handler
has both a refusing and a non-refusing case in the suite.

Design notes:

* **stdlib only.** This module must run on a bare GitHub runner before the package (or
  anything else) is installed, so it imports nothing outside the standard library and is
  not part of the ``argus`` distribution — ``[tool.flit.module] name = "argus"`` packages
  the ``argus`` module only, and this is release machinery, not audit engine.
* **NFR-D2 does not apply.** That rule constrains the *audit* (zero-token, no network).
  A release workflow legitimately talks to git and to the GitHub API.
* **NFR-S1 still applies.** Refusal messages name relative paths, tags and versions —
  never a token, a secret, or an absolute host path.
* Every check returns ``None`` for "no objection", a :class:`Refusal`, or an
  :class:`Unevaluable` for "this check could not observe what it needs to". Nothing here
  repairs, retries or overwrites: the outcomes are *proceed*, *refuse*, and *say so*.
  **A guard that cannot observe is not a guard**, and printing ``ok`` for it would be an
  unsupported clearance — the exact defect class Epic 8 exists to remove. So "could not
  ask" is a THIRD outcome with its own printed token (``UNKNOWN``), never folded into
  ``ok``.
* **Reachability is disclosed, not implied.** A member can be enumerated, handled, and
  phase-assigned yet still be unreachable from the committed workflow;
  :data:`CI_UNREACHABLE` names every such member and why, and the printed report repeats it
  next to that member, so the enumeration never reads as more active than it is.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

__all__ = [
    "RELEASE_EDGE_CASE_IDS",
    "EDGE_CASE_DESCRIPTIONS",
    "CI_UNREACHABLE",
    "PreflightContext",
    "Refusal",
    "Unevaluable",
    "check_e1_dirty_worktree",
    "check_e2_tag_already_exists",
    "check_e3_tag_moved",
    "check_e4_release_already_published",
    "check_e5_tag_version_mismatch",
    "check_e6_incomplete_build",
    "run_checks",
    "run_preflight",
    "handler_for",
]

# ─────────────────────────────────────────────────────────────────────────────
# THE ENUMERATED SPACE (boundary B10). One named place. Add a member here and the
# committed test goes RED until its handler exists.
# ─────────────────────────────────────────────────────────────────────────────

RELEASE_EDGE_CASE_IDS: tuple[str, ...] = ("E1", "E2", "E3", "E4", "E5", "E6")

EDGE_CASE_DESCRIPTIONS: dict[str, str] = {
    "E1": "working tree dirty at build time",
    "E2": "the tag already exists",
    "E3": "a re-tag / tag move is attempted",
    "E4": "the version already has a published artifact for that target",
    "E5": "the tag does not match the pyproject.toml version",
    "E6": "the build produced no artifact, or only one of sdist/wheel",
}

# Which phase of the workflow each check belongs to. E6 can only be evaluated after the
# build; every other member must be evaluated BEFORE it, so a refusal costs nothing.
_PRE_BUILD = ("E1", "E2", "E3", "E4", "E5")
_POST_BUILD = ("E6",)

# Members that are enumerated, handled and phase-assigned but that the COMMITTED workflow
# cannot actually reach — with the reason. Phase assignment says *when* a case would run;
# it does not say that any committed trigger reaches it, and conflating the two is how an
# enumeration comes to read as more active than it is. Every entry here is printed next to
# its member in the report, and a committed test pins the workflow fact that makes it true,
# so removing the cause without removing the disclosure (or vice versa) goes RED.
CI_UNREACHABLE: dict[str, str] = {
    "E2": (
        "local-tooling guard only: neither committed trigger creates a tag (the tag-push "
        "path is started BY the tag, and the workflow_dispatch input requires a tag that "
        "already exists), so .github/workflows/release.yml never passes --creating-tag "
        "and this check cannot fire in CI. It still fires for an operator running the "
        "preflight locally before creating a tag by hand."
    ),
}


@dataclass(frozen=True)
class PreflightContext:
    """Everything the checks are allowed to look at. Frozen; no check mutates state.

    ``existing_tags`` / ``head_sha`` / ``tag_sha`` / ``dirty_paths`` /
    ``published_release_tags`` are INJECTED rather than read inside each check, so every
    edge case is reachable in a test without a GitHub API, a remote, or a second git
    repository. :func:`gather_context` is the impure collector that fills them in on a
    real runner.

    ``published_release_tags`` is deliberately THREE-VALUED. ``()`` means *asked, and the
    target has no releases*; ``None`` means *could not ask* (no ``gh``, no credential, API
    refusal). Collapsing the second into the first is what let E4 print ``ok`` for a
    question it never got to put, so the distinction is carried in the type.
    """

    repo_root: Path
    tag: str
    pyproject_version: str
    dirty_paths: tuple[str, ...] = ()
    existing_tags: tuple[str, ...] = ()
    head_sha: str = ""
    tag_sha: str = ""
    published_release_tags: tuple[str, ...] | None = ()
    dist_files: tuple[str, ...] = ()
    # True on the workflow_dispatch path, where the run is being asked to CREATE the tag.
    # On the tag-push path the tag necessarily exists already — that is why the run
    # started — so E2 must not fire there, and saying so explicitly is the difference
    # between a guard and a superstition.
    creating_tag: bool = False


@dataclass(frozen=True)
class Refusal:
    """A refusal: which enumerated case fired, and the sentence a human will read."""

    edge_case: str
    reason: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"[{self.edge_case}] {EDGE_CASE_DESCRIPTIONS[self.edge_case]}: {self.reason}"


@dataclass(frozen=True)
class Unevaluable:
    """The check could not observe what it needs to. NOT a clearance, and not a refusal.

    A guard that cannot observe is not a guard. Reporting this state as ``ok`` would
    publish a clearance the run was structurally unable to establish — an unsupported
    claim of exactly the class this repository spent Epic 8 removing from its verdict. It
    is a distinct type rather than a flag so that no call site can treat it as ``None`` by
    forgetting to look.
    """

    edge_case: str
    reason: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return (
            f"[{self.edge_case}] {EDGE_CASE_DESCRIPTIONS[self.edge_case]}: "
            f"NOT EVALUATED — {self.reason}"
        )


Check = Callable[[PreflightContext], "Refusal | Unevaluable | None"]


# ─────────────────────────────────────────────────────────────────────────────
# The handlers — one per enumerated member
# ─────────────────────────────────────────────────────────────────────────────


def check_e1_dirty_worktree(ctx: PreflightContext) -> Refusal | None:
    """E1 — refuse to build from a dirty tree.

    An artifact built from uncommitted bytes cannot be reproduced from the tag it claims
    to be, which makes its provenance unfalsifiable. This is the packaging analogue of
    the ``load_repo_at_commit`` clean-tree precondition the audit engine already refuses
    to run without.
    """
    if ctx.dirty_paths:
        listed = ", ".join(sorted(ctx.dirty_paths)[:10])
        return Refusal(
            "E1",
            f"{len(ctx.dirty_paths)} uncommitted path(s) in the working tree ({listed}). "
            "Commit or stash them; the artifact must be reproducible from the tag.",
        )
    return None


def check_e2_tag_already_exists(ctx: PreflightContext) -> Refusal | None:
    """E2 — refuse to create a tag that already exists. No silent overwrite.

    Only meaningful when the run is being asked to CREATE the tag
    (``creating_tag=True``). On the tag-push path the tag exists by definition and E3 is
    the check that matters instead.

    ⚠️ **Not reachable from the committed workflow** — see :data:`CI_UNREACHABLE`. Neither
    trigger creates a tag, so ``.github/workflows/release.yml`` never passes
    ``--creating-tag`` and this check is a LOCAL-TOOLING guard for an operator creating a
    tag by hand. Passing ``--creating-tag`` on the ``workflow_dispatch`` path was
    considered and rejected: that input is documented as a tag that *must already exist*,
    so the flag would be a false statement about what the run is doing, and E2 would then
    refuse every legitimate dispatch. Disclosing the gap is the honest option; hiding it
    behind a flag that lies is not.
    """
    if ctx.creating_tag and ctx.tag in ctx.existing_tags:
        return Refusal(
            "E2",
            f"tag {ctx.tag!r} already exists in this repository. Creating it again would "
            "either fail or move it; neither is a release. Choose a new version.",
        )
    return None


def check_e3_tag_moved(ctx: PreflightContext) -> Refusal | None:
    """E3 — refuse a re-tag / tag move.

    If the tag no longer points at the commit being built, then whatever was published
    under that tag before was built from different bytes, and the tag has stopped being
    an identifier. Refuse rather than publish a second, different artifact under a name
    that already means something else.
    """
    if ctx.creating_tag:
        return None
    if ctx.tag_sha and ctx.head_sha and ctx.tag_sha != ctx.head_sha:
        return Refusal(
            "E3",
            f"tag {ctx.tag!r} points at {ctx.tag_sha[:12]} but the checkout is at "
            f"{ctx.head_sha[:12]}. A moved tag makes every artifact previously published "
            "under it unattributable.",
        )
    return None


def check_e4_release_already_published(
    ctx: PreflightContext,
) -> Refusal | Unevaluable | None:
    """E4 — refuse when the target already has a published artifact for this version.

    The measured target is a GitHub Release for the tag (Story 9.2 / D2). Overwriting one
    replaces bytes a consumer may already have resolved and pinned, which is the same
    irreversibility argument that kept PyPI out of this story.

    When the release list could not be obtained at all
    (``published_release_tags is None``) this returns :class:`Unevaluable` rather than a
    clearance. The earlier shape swallowed the failure into an empty tuple and the report
    printed ``ok`` — a clearance for a question that was never asked. ``gh release create
    --verify-tag`` still refuses to clobber an existing release, so no artifact was ever at
    risk; the defect was the false clearance, and that is what this removes.
    """
    if ctx.published_release_tags is None:
        return Unevaluable(
            "E4",
            "the published-release list could not be obtained (no `gh`, no credential, or "
            "the API refused), so this run cannot say whether the tag already has a "
            "release. `gh release create --verify-tag` still refuses to overwrite one.",
        )
    if ctx.tag in ctx.published_release_tags:
        return Refusal(
            "E4",
            f"a release already exists for tag {ctx.tag!r}. Publishing again would "
            "replace artifacts a consumer may already have resolved.",
        )
    return None


def check_e5_tag_version_mismatch(ctx: PreflightContext) -> Refusal | None:
    """E5 — refuse when the tag and the packaged version disagree.

    A ``v0.2.0`` tag on a ``0.1.0`` tree is a provenance failure, not a rounding error:
    the resolvable name and the metadata inside the artifact would state different
    versions of the same package — precisely the class of contradiction DF-8-5-A removed
    from the signed evidence bundle in this same story.
    """
    expected = normalize_tag(ctx.tag)
    if expected is None:
        return Refusal(
            "E5",
            f"tag {ctx.tag!r} is not a version tag; the expected shape is "
            "``v<major>.<minor>.<patch>`` (e.g. ``v0.1.0``).",
        )
    if expected != ctx.pyproject_version:
        return Refusal(
            "E5",
            f"tag {ctx.tag!r} declares version {expected!r} but pyproject.toml states "
            f"{ctx.pyproject_version!r}. The resolvable name and the artifact metadata "
            "must state the same version.",
        )
    return None


def check_e6_incomplete_build(ctx: PreflightContext) -> Refusal | None:
    """E6 — refuse a partial release: BOTH an sdist and a wheel, or nothing.

    A release carrying only a wheel silently drops every consumer that must build from
    source; one carrying only an sdist drops every consumer that cannot. Publishing half
    is worse than publishing none, because the gap is invisible until it bites.
    """
    sdists = [f for f in ctx.dist_files if f.endswith(".tar.gz")]
    wheels = [f for f in ctx.dist_files if f.endswith(".whl")]
    if not ctx.dist_files:
        return Refusal("E6", "the build produced no artifact at all in the dist directory.")
    if not sdists or not wheels:
        return Refusal(
            "E6",
            f"the build is incomplete: {len(sdists)} sdist(s) and {len(wheels)} wheel(s) "
            f"in {sorted(ctx.dist_files)}. A release carries both or neither.",
        )
    return None


_HANDLERS: dict[str, Check] = {
    "E1": check_e1_dirty_worktree,
    "E2": check_e2_tag_already_exists,
    "E3": check_e3_tag_moved,
    "E4": check_e4_release_already_published,
    "E5": check_e5_tag_version_mismatch,
    "E6": check_e6_incomplete_build,
}


def handler_for(edge_case: str) -> Check:
    """The handler registered for *edge_case*.

    Raises ``KeyError`` — loudly — when an enumerated member has no handler. The
    committed test asserts ``set(RELEASE_EDGE_CASE_IDS) == set(_HANDLERS)``, so this
    cannot be reached in a healthy tree; it exists so a partial edit fails at the first
    call rather than skipping a case in silence.
    """
    return _HANDLERS[edge_case]


def phase_members(phase: str) -> Sequence[str]:
    """The enumerated members belonging to *phase*. One place, so the report and the run
    can never disagree about what was actually evaluated."""
    if phase == "pre-build":
        return _PRE_BUILD
    if phase == "post-build":
        return _POST_BUILD
    if phase == "all":
        return RELEASE_EDGE_CASE_IDS
    raise ValueError(f"unknown preflight phase {phase!r}")


def run_checks(
    ctx: PreflightContext, *, phase: str
) -> list[tuple[str, Refusal | Unevaluable | None]]:
    """Every member of *phase* with its OUTCOME, in enumeration order.

    This is the full-fidelity result: refused, not-evaluated, and cleared are three
    different answers and the reporting layer needs all three. :func:`run_preflight`
    narrows it to refusals for callers that only decide go/no-go.
    """
    return [(case, handler_for(case)(ctx)) for case in phase_members(phase)]


def run_preflight(ctx: PreflightContext, *, phase: str) -> list[Refusal]:
    """Run every enumerated check for *phase* and return ALL refusals, not just the first.

    Returning all of them is deliberate: an operator fixing a release should see every
    reason it was refused in one run rather than discovering them one CI round at a time.
    An :class:`Unevaluable` outcome is NOT a refusal and is not returned here — it is
    surfaced by the report, which is the surface that would otherwise have claimed ``ok``.
    """
    return [
        outcome
        for _, outcome in run_checks(ctx, phase=phase)
        if isinstance(outcome, Refusal)
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Impure helpers — used on a runner, injected in tests
# ─────────────────────────────────────────────────────────────────────────────

_VERSION_TAG = re.compile(r"^v(\d+\.\d+\.\d+)$")


def normalize_tag(tag: str) -> str | None:
    """``"v0.1.0"`` -> ``"0.1.0"``; ``None`` when *tag* is not a version tag."""
    match = _VERSION_TAG.match(tag.strip())
    return match.group(1) if match else None


def read_pyproject_version(repo_root: Path) -> str:
    """The ``[project] version`` literal, read without a TOML dependency.

    ``tomllib`` is 3.11+ and this must run on the ``requires-python = ">=3.10"`` floor,
    so the value is read with an anchored regex over the first ``version =`` assignment.
    """
    text = (repo_root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"^version\s*=\s*\"([^\"]+)\"", text, flags=re.MULTILINE)
    if match is None:
        raise ValueError("pyproject.toml declares no `version = ` for the distribution")
    return match.group(1)


def _git(repo_root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout.strip()


def _published_release_tags(repo_root: Path) -> tuple[str, ...] | None:
    """Tags that already have a GitHub Release, via ``gh`` when it is available.

    Returns ``None`` for **"could not ask"** — ``gh`` missing, unauthenticated, or the API
    refusing — as distinct from ``()`` for **"asked, and there are none"**. The previous
    shape returned ``()`` for both, so an unauthenticated runner produced an E4 clearance
    indistinguishable from a real one. ``[]`` on stdout is a genuine empty answer and stays
    ``()``.
    """
    try:
        proc = subprocess.run(
            ["gh", "release", "list", "--limit", "200", "--json", "tagName"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        # `gh` is not installed on this machine: the question could not be put.
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        entries = json.loads(proc.stdout)
    except json.JSONDecodeError:  # pragma: no cover - defensive
        return None
    return tuple(str(e.get("tagName", "")) for e in entries if e.get("tagName"))


def gather_context(
    repo_root: Path, tag: str, *, dist_dir: Path | None, creating_tag: bool
) -> PreflightContext:
    """Collect the real state of the checkout (the impure half; AR8)."""
    dirty = tuple(
        line[3:] for line in _git(repo_root, "status", "--porcelain").splitlines() if line
    )
    tags = tuple(t for t in _git(repo_root, "tag", "-l").splitlines() if t)
    dist_files: tuple[str, ...] = ()
    if dist_dir is not None and dist_dir.is_dir():
        dist_files = tuple(sorted(p.name for p in dist_dir.iterdir() if p.is_file()))
    return PreflightContext(
        repo_root=repo_root,
        tag=tag,
        pyproject_version=read_pyproject_version(repo_root),
        dirty_paths=dirty,
        existing_tags=tags,
        head_sha=_git(repo_root, "rev-parse", "HEAD"),
        tag_sha=_git(repo_root, "rev-list", "-n", "1", tag) if tag in tags else "",
        published_release_tags=_published_release_tags(repo_root),
        dist_files=dist_files,
        creating_tag=creating_tag,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="the version tag, e.g. v0.1.0")
    parser.add_argument(
        "--phase",
        choices=("validate-tag", "pre-build", "post-build", "all"),
        default="pre-build",
        help=(
            "validate-tag checks ONLY the shape of --tag and exits; it exists so the "
            "workflow can reject an untrusted dispatch input before that value reaches "
            "any other command"
        ),
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--dist-dir", default="dist")
    parser.add_argument(
        "--creating-tag",
        action="store_true",
        help="the run is being asked to CREATE the tag (workflow_dispatch path)",
    )
    args = parser.parse_args(argv)

    # FIRST, before anything else touches the value: the tag must have the one shape this
    # project releases under. `--tag` carries an UNTRUSTED workflow_dispatch input, and the
    # workflow binds it through `env:` and hands it here before it reaches any other
    # command, so this is the point at which a crafted value stops. `_VERSION_TAG` is the
    # single pattern; E5 reuses it rather than restating it (AR7 reuse-not-fork).
    if normalize_tag(args.tag) is None:
        print(
            f"RELEASE REFUSED: tag {args.tag!r} is not a version tag. The expected shape "
            "is v<major>.<minor>.<patch> (e.g. v0.1.0)."
        )
        return 1
    if args.phase == "validate-tag":
        print(f"tag {args.tag} has the expected v<major>.<minor>.<patch> shape.")
        return 0

    repo_root = Path(args.repo_root).resolve()
    ctx = gather_context(
        repo_root,
        args.tag,
        dist_dir=Path(args.dist_dir) if args.phase != "pre-build" else None,
        creating_tag=args.creating_tag,
    )
    outcomes = run_checks(ctx, phase=args.phase)
    print(f"release preflight [{args.phase}] for tag {ctx.tag} "
          f"(pyproject version {ctx.pyproject_version})")
    for edge_case, outcome in outcomes:
        if isinstance(outcome, Refusal):
            status = "REFUSE"
        elif isinstance(outcome, Unevaluable):
            status = "UNKNOWN"
        else:
            status = "ok"
        note = " (not reachable from this workflow)" if edge_case in CI_UNREACHABLE else ""
        print(f"  {edge_case} {EDGE_CASE_DESCRIPTIONS[edge_case]:<58} {status}{note}")

    refusals = [o for _, o in outcomes if isinstance(o, Refusal)]
    unevaluated = [o for _, o in outcomes if isinstance(o, Unevaluable)]
    unreachable = [case for case, _ in outcomes if case in CI_UNREACHABLE]

    for case in unreachable:
        print(f"\nNOT REACHABLE HERE [{case}]: {CI_UNREACHABLE[case]}")
    if unevaluated:
        print("\nNOT EVALUATED (this run could not observe these; they are NOT cleared):")
        for item in unevaluated:
            print(f"  {item}")
    if refusals:
        print("\nRELEASE REFUSED:")
        for refusal in refusals:
            print(f"  {refusal}")
        return 1
    if unevaluated:
        # Deliberately NOT a failure: `gh` is legitimately absent when an operator runs
        # this locally, and `gh release create --verify-tag` still refuses to overwrite a
        # published release. What is not acceptable is calling this a clearance, so the
        # closing sentence names exactly what was and was not established.
        names = ", ".join(item.edge_case for item in unevaluated)
        print(
            f"\nno enumerated release edge case refused, but {names} could NOT be "
            "evaluated by this run — this is not a clearance of those cases."
        )
        return 0
    print("\nall enumerated release edge cases cleared.")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
