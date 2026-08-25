"""Story 17.4 — the ORDERING GUARD, and the pure git-history seams two guards share.

Verification area ``TC-ArgusAgent-PRECISION-001-147``.

⛔ **THIS MODULE IS THE INVERSION OF ``-139``.** ``-139``
(``tests/test_precision_preregistration.py``) asserts an **absence**: no commit reachable from
``PREREGISTRATION_COMMIT_SHA`` touches successor output. ``-147`` asserts a **universal over a
population Story 17.4 CREATES**: for *every* commit that touches a declared
``SUCCESSOR_OUTPUT_PATHS`` entry, the pre-registration commit is an **ancestor** of it.

⛔ **THE SAME "git log found nothing" STATE IS A LEGITIMATE PASS FOR ``-139`` AND A DEAD GUARD
HERE.** So ``-147`` asserts, as a first-class precondition, that the offender-candidate population
is **NON-EMPTY** — which is satisfiable only at or after the commit that writes this story's
record (``DN-17-4-4`` / AC4.7). This module therefore may not land in a commit earlier than the
first successor-output commit.

**Why the seams below are pure, exported functions.** ``commits_touching_prefixes`` and
``ancestry_offenders`` take a repository root and return data. That is what lets the RED
demonstration drive **the real seam** in a throwaway repository rather than a re-implementation of
it (``tests/test_vacuous_cross_language.py:169``'s shape, reused) — and ⛔ **nothing is ever
written to this repository's object database**: a peer session commits to this branch, and a
rewritten object graph is not recoverable by ``git checkout`` (``DN-17-4-5``).

**These same seams carry the AMENDED half of ``TC-ArgusAgent-PRECISION-001-146``.** On 2026-08-26
the operator amended AC9.6 narrowly, for ``-146`` part (2) ONLY, to permit RE-SCOPING that part
from a **filesystem existence** check to a claim over **Story 17.3's own commit range** — see that
guard's docstring for the decision and its rationale. Both guards ask git the same question
through the same function, so there is ONE derivation of *"which commits touched a declared
prefix"* rather than two that can disagree (``DF-8-5-C``).

⛔ **Green on the ubuntu CI matrix with NO third-party checkouts present.** Everything here reads
the object database, or a repository this module builds under ``tmp_path``.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from precision_preregistration import (  # noqa: E402
    PREREGISTRATION_COMMIT_SHA,
    SUCCESSOR_OUTPUT_PATHS,
)

#: A path known to carry commits in this repository, used as the non-vacuity control: a
#: misspelled or moved pathspec returns empty and is indistinguishable from a clean history.
CONTROL_PATH_WITH_COMMITS = "argus/detectors"


# ═════════════════════════════════════════════════════════════════════════════════════════
# The pure seams. Commits in, offenders out — so a demonstration can drive them anywhere.
# ═════════════════════════════════════════════════════════════════════════════════════════


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603,S607 - fixed argv, no shell, repository-relative
        ["git", "-C", str(repo_root), *args],
        capture_output=True,
        text=True,
        timeout=180,
    )


def commits_touching_prefixes(
    repo_root: Path,
    prefixes: Sequence[str],
    revision: str,
) -> tuple[tuple[str, str], ...]:
    """Every commit in ``revision`` that touches any of ``prefixes``, as ``(sha, subject)``.

    ⛔ **Pure with respect to this process**: it reads a repository and returns data. ``log`` is
    a read-only verb and nothing here writes to the repository it is pointed at.

    ``prefixes`` are used as git pathspecs **verbatim** — repository-relative, forward-slash —
    which is why ``SUCCESSOR_OUTPUT_PATHS`` entries are asserted to have that shape before this
    is called. ``os.path.join`` or a backslash would silently match nothing on the ubuntu matrix.
    """
    assert prefixes, "an empty pathspec makes `git log` report everything or nothing"
    done = _run_git(repo_root, "log", "--format=%H %s", revision, "--", *prefixes)
    if done.returncode != 0:
        raise RuntimeError(f"git log failed in {repo_root}: {done.stderr.strip()!r}")
    resolved: list[tuple[str, str]] = []
    for line in done.stdout.splitlines():
        if not line.strip():
            continue
        sha, _, subject = line.partition(" ")
        resolved.append((sha, subject))
    return tuple(resolved)


def ancestry_offenders(
    repo_root: Path,
    commits: Sequence[str],
    ancestor: str,
) -> tuple[str, ...]:
    """The commits of ``commits`` that ``ancestor`` is **NOT** an ancestor of.

    An empty result is the claim ``-147`` makes. ⛔ It is only meaningful when ``commits`` is
    non-empty, which is why every caller asserts that first.
    """
    offenders: list[str] = []
    for sha in commits:
        done = _run_git(repo_root, "merge-base", "--is-ancestor", ancestor, sha)
        if done.returncode == 0:
            continue
        if done.returncode == 1:
            offenders.append(sha)
            continue
        raise RuntimeError(
            f"`git merge-base --is-ancestor {ancestor} {sha}` failed in {repo_root} with "
            f"{done.returncode}: {done.stderr.strip()!r}. A guard that cannot ask the question "
            f"must not answer it."
        )
    return tuple(offenders)


# ═════════════════════════════════════════════════════════════════════════════════════════
# The throwaway repository — the ONLY place a violating arrangement is ever built
# ═════════════════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ViolatingHistory:
    """A synthetic history carrying both a compliant and a violating successor-output commit."""

    repo: Path
    #: A stand-in for the pre-registration commit, on its own root.
    criterion: str
    #: A DESCENDANT of ``criterion`` that writes successor output — the compliant arrangement.
    compliant: str
    #: The base of the rogue line, used as a revision range base.
    rogue_base: str
    #: A commit on an UNRELATED root that writes successor output — the violating arrangement.
    #: Its subject carries Story 17.3's tag, so it also falsifies ``-146`` part (2).
    offender: str
    #: A commit on the rogue line that touches no declared prefix — the range control.
    rogue_control: str


def build_violating_history(root: Path, story_tag: str = "(17-3)") -> ViolatingHistory:
    """Build a THROWAWAY repository whose history violates both ordering claims.

    ⛔ **Never run against this repository.** ``root`` is a pytest ``tmp_path``; the repository
    is created there, used, and discarded. Nothing is written to the shared object database and
    no ``git replace`` / ``graft`` / ``commit-tree`` / history rewrite is used anywhere.

    Two unrelated roots are created on purpose:

    * the **criterion line** — a stand-in pre-registration commit and a DESCENDANT of it that
      writes successor output. That is the compliant arrangement, and it is what proves
      ``ancestry_offenders`` can return **empty** for a reason rather than by accident;
    * the **rogue line** — an unrelated root, a control commit that touches no declared prefix,
      and a commit that writes successor output while carrying ``story_tag`` in its subject.
      The pre-registration stand-in is **not** an ancestor of it, and it is inside a commit range
      the ``-146`` claim quantifies over. One commit, both violations.
    """
    repo = root / "throwaway-ordering-repo"
    repo.mkdir(parents=True, exist_ok=True)

    def git(*args: str) -> None:
        done = _run_git(repo, *args)
        if done.returncode != 0:
            raise RuntimeError(f"throwaway git {args}: {done.stderr.strip()!r}")

    def head() -> str:
        done = _run_git(repo, "rev-parse", "HEAD")
        assert done.returncode == 0, done.stderr
        return done.stdout.strip()

    def commit(relative: str, body: str, subject: str) -> str:
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        git("add", "--", relative)
        git(
            "-c",
            "user.name=ArgusAgent Ordering Fixture",
            "-c",
            "user.email=ordering@argus.test",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--no-gpg-sign",
            "-m",
            subject,
        )
        return head()

    git("-c", "init.defaultBranch=main", "init")

    # ── The rogue line: an unrelated root, and a successor-output commit on it. ──
    rogue_base = commit("seed.txt", "rogue root\n", "chore: rogue root")
    rogue_control = commit(
        "argus/detectors/placeholder.py",
        "PLACEHOLDER = 1\n",
        f"chore{story_tag}: rogue control, touching no declared prefix",
    )
    offender = commit(
        f"{SUCCESSOR_OUTPUT_PATHS[0]}/successor-reach-record.json",
        '{"rogue": true}\n',
        f"chore{story_tag}: commit successor output with no pre-registration ancestor",
    )

    # ── The criterion line: a separate root, so the stand-in is NOT an ancestor of the rogue. ──
    git("checkout", "--orphan", "criterion-line")
    git("rm", "-rf", "--quiet", ".")
    criterion = commit(
        "criterion.txt", "pre-registration stand-in\n", "docs: pre-registration stand-in"
    )
    compliant = commit(
        f"{SUCCESSOR_OUTPUT_PATHS[0]}/successor-reach-record.json",
        '{"compliant": true}\n',
        "chore: commit successor output AFTER the pre-registration",
    )

    return ViolatingHistory(
        repo=repo,
        criterion=criterion,
        compliant=compliant,
        rogue_base=rogue_base,
        offender=offender,
        rogue_control=rogue_control,
    )


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC4 — the binding ordering constraint, asserted against the real object database
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_147_every_successor_output_commit_descends_from_the_criterion(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-PRECISION-001-147 — AC4: the criterion PRECEDES every successor output.

    **Observable.** Every commit reachable from ``HEAD`` that touches any declared
    ``SUCCESSOR_OUTPUT_PATHS`` entry, and for each of them the answer git gives to
    ``merge-base --is-ancestor PREREGISTRATION_COMMIT_SHA <commit>``. The claim is that the
    offender set is **EMPTY over a NON-EMPTY population**.

    **The defect it moves.** Story 17.1's entire value is the ORDER: the criterion was frozen
    while the verdict-eligible population was still zero. ``-139`` proves the criterion carried no
    successor output *behind* it. Without this guard, nothing stops a later successor measurement
    from being committed on a line of history the criterion never preceded — which would make the
    pre-registration a claim about intent rather than a fact about git.

    **⛔ Non-vacuity, three ways, each asserted BEFORE the claim** (AC4.3), and the second is the
    INVERSION of ``-139``:

    1. the pre-registration sha resolves to a real commit, and the declared path set is non-empty
       and portable as a git pathspec on both the Windows local gate and the ubuntu matrix;
    2. ⛔ **the offender-candidate population is asserted NON-EMPTY** — at least one commit really
       does touch a declared prefix. ``-139`` may legitimately find nothing; a universal that
       finds nothing is a **dead guard**, and this is the one precondition that separates them;
    3. the ancestry predicate is driven to **BOTH** outcomes on real, resolvable shas in this
       repository, neither fabricated.

    **⛔ Executed RED demonstration, at the real seam.** ``build_violating_history`` builds a
    THROWAWAY repository under ``tmp_path`` carrying a successor-output commit on a line the
    criterion stand-in does not precede, and ``ancestry_offenders`` — the same function the claim
    below is made with — is driven over it and returns that commit. ⛔ Nothing is written to this
    repository's object database and no history is rewritten: the tree is shared (``DN-17-4-5``).

    **CI-safe.** No third-party checkout is read; ``git`` and this repository are the only inputs.
    """
    # ── Precondition 0: the pre-registration sha RESOLVES. ────────────────────────────────
    assert PREREGISTRATION_COMMIT_SHA is not None, (
        "PREREGISTRATION_COMMIT_SHA is still None; the ordering claim has no subject."
    )
    assert len(PREREGISTRATION_COMMIT_SHA) == 40 and PREREGISTRATION_COMMIT_SHA.islower(), (
        "the pre-registration sha must be a full 40-character lowercase hex sha — a short sha is "
        "ambiguous, and this is the story's central citation."
    )
    kind = _run_git(_REPO_ROOT, "cat-file", "-t", PREREGISTRATION_COMMIT_SHA)
    assert kind.returncode == 0 and kind.stdout.strip() == "commit", (
        f"{PREREGISTRATION_COMMIT_SHA} does not resolve to a commit in this repository "
        f"({kind.stdout.strip()!r} / {kind.stderr.strip()!r}); an ordering claim cannot be "
        f"established against a sha that is not in the history."
    )

    # ── Precondition 1: the declared path set is non-empty and portable. ──────────────────
    assert SUCCESSOR_OUTPUT_PATHS, (
        "SUCCESSOR_OUTPUT_PATHS is empty, so the universal below quantifies over nothing."
    )
    assert all(
        path and not path.startswith("/") and "\\" not in path
        for path in SUCCESSOR_OUTPUT_PATHS
    ), (
        f"every SUCCESSOR_OUTPUT_PATHS entry must be repository-relative and forward-slash so the "
        f"same string works as a git pathspec on the Windows local gate and the ubuntu CI matrix; "
        f"got {list(SUCCESSOR_OUTPUT_PATHS)}."
    )

    # ── Precondition 1b: the invocation is CAPABLE of finding commits at all. ─────────────
    control = commits_touching_prefixes(_REPO_ROOT, (CONTROL_PATH_WITH_COMMITS,), "HEAD")
    assert control, (
        f"`git log HEAD -- {CONTROL_PATH_WITH_COMMITS}` returned NOTHING. That path is known to "
        f"carry commits, so this invocation cannot find anything, and an invocation that finds "
        f"nothing satisfies a universal for free. Fix the invocation, never the assertion."
    )

    # ── ⛔ Precondition 2: THE INVERSION OF -139 — the population must be NON-EMPTY. ──────
    population = commits_touching_prefixes(_REPO_ROOT, SUCCESSOR_OUTPUT_PATHS, "HEAD")
    assert population, (
        f"no commit reachable from HEAD touches any of {list(SUCCESSOR_OUTPUT_PATHS)}, so this "
        f"universal is VACUOUSLY TRUE and this guard is dead. That state is a legitimate PASS for "
        f"-139 and a dead guard here (DN-17-4-4): -147 may not land in a commit earlier than the "
        f"first commit touching a declared successor-output prefix (AC4.7)."
    )

    # ── Precondition 3: the ancestry predicate, driven to BOTH outcomes on real shas. ─────
    head = _run_git(_REPO_ROOT, "rev-parse", "HEAD")
    assert head.returncode == 0, f"`git rev-parse HEAD` failed: {head.stderr.strip()!r}"
    head_sha = head.stdout.strip()
    assert not ancestry_offenders(_REPO_ROOT, (head_sha,), PREREGISTRATION_COMMIT_SHA), (
        f"the pre-registration commit {PREREGISTRATION_COMMIT_SHA} is NOT an ancestor of HEAD, so "
        f"it is on a detached or abandoned line of history and establishes nothing about the "
        f"branch that shipped."
    )
    assert ancestry_offenders(_REPO_ROOT, (PREREGISTRATION_COMMIT_SHA,), head_sha) == (
        PREREGISTRATION_COMMIT_SHA,
    ), (
        "HEAD reports as an ancestor of the pre-registration commit as well as the reverse, so "
        "the ancestry predicate is returning the same answer to both questions and is not "
        "discriminating anything — the assertion above would prove nothing."
    )

    # ── ⛔ THE CLAIM: the criterion precedes EVERY successor-output commit. ───────────────
    offenders = ancestry_offenders(
        _REPO_ROOT, [sha for sha, _ in population], PREREGISTRATION_COMMIT_SHA
    )
    assert not offenders, (
        f"{len(offenders)} commit(s) touching a declared successor-output path do NOT descend "
        f"from the pre-registration commit {PREREGISTRATION_COMMIT_SHA}: {offenders[:5]}. The "
        f"criterion would then not have preceded the measurement it judges, which is the ONE "
        f"thing Story 17.1 exists to establish. ⛔ The repair is to the history, never to this "
        f"assertion."
    )

    # ── ⛔ EXECUTED RED DEMONSTRATION, at the real seam, in a THROWAWAY repository. ───────
    history = build_violating_history(tmp_path)
    assert not ancestry_offenders(history.repo, (history.compliant,), history.criterion), (
        "the compliant arrangement — successor output committed as a DESCENDANT of the criterion "
        "stand-in — is reported as an offender, so the predicate rejects everything and its "
        "empty answer above would mean nothing."
    )
    demonstrated = ancestry_offenders(history.repo, (history.offender,), history.criterion)
    assert demonstrated == (history.offender,), (
        f"the violating arrangement — successor output committed on a line the criterion stand-in "
        f"does NOT precede — was not reported by ancestry_offenders (got {demonstrated!r}). A "
        f"guard that cannot go RED is not a guard."
    )

