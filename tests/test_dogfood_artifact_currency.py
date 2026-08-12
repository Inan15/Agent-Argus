"""Story 12.1 / AC3 — a committed dogfood artifact cannot describe a tree that no longer exists.

Verification area ArgusAgent-DOGFOOD (``TC-ArgusAgent-DOGFOOD-001-49``..``-52``, CONTINUING the
index Story 7.1 opened; ``-01``..``-48`` were taken). Closes ``DF-8-5-B`` and ``DF-10-4-D``
**together**, which is ``DF-10-4-D``'s own instruction: *"supersede or close them together, never
separately."*

**The defect, measured — and it is the opposite of the one both entries describe.** Both were
filed about guards that *break too often*: `TC-ArgusAgent-DOGFOOD-001-03`, `-06`, `-41` and the two
proof assertions re-break on any `argus/**` composition change, and `DF-10-4-D` sharpened the
trigger to *"the moment you `git add`"*, because ``enumerate_minions_source_files`` reads the git
INDEX. True. But measured on this tree at ``ca37283`` on 2026-08-12, the **silent** direction was
also live and worse: all three committed artifacts were **already stale** —

===========================================  =====================  ====================
field                                        committed              live at ``ca37283``
===========================================  =====================  ====================
provenance sha                               ``a9cc933``            ``ca37283``
total physical LOC                           19783                  20454
recorded cut edges                           57                     64
unit-2 LOC / unit-3 LOC                      14793 / 3660           14997 / 4127
NFR-C1 baseline ratio                        ``360/19783``          ``60/3409``
===========================================  =====================  ====================

— **while all five of those assertions were GREEN**. They are green because of what they actually
assert, which is far less than their own docstrings claim: ``-03``'s docstring says *"the artifact
cannot silently rot away from the generator"* and it checks the literal ``Unit count: 3``, three
12-character ``partition_id`` prefixes and the phrase ``Reused planner``. It cannot see a single
figure in that table. That is this project's dominant defect class (``AI-E11-1``) sitting in the
exact surface Story 12.1 was chartered to fix: *the defect exists while every observable the guard
watches is unchanged.*

**So the remedy both entries named — "name a regeneration entry point in the failure message" — is
necessary and NOT sufficient**: it improves a red that never appeared. It is delivered anyway
(:data:`REGENERATION_COMMAND` now appears in every one of those five failure messages, and
``scripts/regenerate_dogfood_artifacts.py`` is a real committed entry point rather than an
incantation), and this file adds the half that makes the red appear.

**The property, as a closure over the real structure rather than over a list of tokens.**

    An artifact is CURRENT iff (a) the provenance sha it cites is a real commit **and an ancestor
    of ``HEAD``**, and (b) ``git diff --quiet <cited-sha> HEAD -- argus/`` is empty — nothing in
    ``argus/**`` has changed since the tree the artifact says it describes.

Why this shape and not byte-equality against a fresh render: byte-equality would go red on the
provenance sha alone, on **every** commit, making the two-step tax permanent — which is the
complaint ``DF-8-5-B`` filed. This goes red exactly when ``argus/**`` moved, which is exactly when
the figures are wrong. Validated against real history before it was written: it is RED at
``ca37283`` on the real defect with no reconstruction (``git diff a9cc933 HEAD -- argus/`` = 7
files, +749/−78), and it would have been GREEN at the last honest regeneration (``git diff a9cc933
93adc94 -- argus/`` is empty, and ``a9cc933`` IS an ancestor of ``HEAD``). It distinguishes the
honest state from the rotten one; it does not merely fail always. ``-52`` re-proves both halves
from live history on every run rather than trusting that paragraph.

It also **mechanises the operator ruling of 2026-08-12** — *"every regenerated artifact must cite a
truthful provenance sha that is an ancestor of HEAD"* — turning a promise into an assertion, and it
reconciles the ``DF-10-4-D`` provenance/enumeration split: the artifacts enumerate the INDEX while
citing ``HEAD``, and this guard fails unless those two trees agree over ``argus/``.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from argus.dogfood.partition_plan import (
    render_budget_plan_markdown,
    render_partition_plan_markdown,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"

#: The named regeneration entry point (``DF-8-5-B``'s close condition). Imported from the script
#: itself rather than retyped, so the string in every failure message and the command that
#: actually exists cannot drift apart.
REGENERATION_COMMAND = "python scripts/regenerate_dogfood_artifacts.py"
_REGENERATION_SCRIPT = _REPO_ROOT / "scripts" / "regenerate_dogfood_artifacts.py"

#: Every committed artifact that CITES a provenance sha and DESCRIBES the ``argus/`` tree, with
#: the renderer that produces it. The registry is closed by ``-51``: a fourth artifact added to
#: the directory without being registered here (or exempted with a reason) FAILS.
_CURRENT_ARTIFACTS: dict[str, str] = {
    "minions-dogfood-partition-plan.md": "argus.dogfood.partition_plan.render_partition_plan_markdown",
    "minions-dogfood-budget-plan.md": "argus.dogfood.partition_plan.render_budget_plan_markdown",
    "minions-dogfood-proof.md": "argus.dogfood.proof_render.render_proof_markdown",
}

#: Exempt BY NAME WITH THE REASON, never by narrowing the glob. Story 8.5 / AC15 fences this file:
#: it is the PRESERVED, FROZEN Story-7.2 independent Minions run — the record being SUPERSEDED and
#: the only surviving copy of the independent evidence. It is *supposed* to cite a tree that no
#: longer exists; that is what a historical record is. Re-deriving it is impossible (the Minions
#: population cannot be reconstructed in this repository) and rewriting it would destroy the
#: evidence. The same ``_PRESERVED_RECORD`` precedent as ``tests/test_release_surface_honesty.py``.
_PRESERVED_RECORDS: dict[str, str] = {
    "minions-dogfood-proof-story-7-2-superseded.md": (
        "The frozen Story-7.2 independent Minions run, preserved by Story 8.5 / AC15 under RS-3 "
        "('supersede, don't erase'). It is the only surviving copy of the independent evidence, "
        "its population cannot be re-derived in this repository, and it cites a provenance sha "
        "from a history this repository does not contain. A historical record that still "
        "described the current tree would not be a historical record."
    ),
}

_PROVENANCE = re.compile(r"^- Commit descriptor[^:]*:\s*`(?P<sha>[0-9a-f]{7,40})`\s*$", re.MULTILINE)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(_REPO_ROOT), *args], capture_output=True, text=True, timeout=120
    )


def _remedy(artifact: str) -> str:
    renderer = _CURRENT_ARTIFACTS.get(artifact, "its own renderer")
    return (
        f"\n\nHOW TO FIX THIS: commit the `argus/` delta first, then run\n\n    "
        f"{REGENERATION_COMMAND}\n\nwhich re-renders {artifact} through {renderer} and writes the "
        "output VERBATIM, then commit the regenerated artifacts as a SEPARATE commit. Do NOT edit "
        "the .md by hand — a regeneration is legitimate only through the artifact's own renderer "
        "at a truthful sha (operator ruling, 2026-08-12). Do NOT loosen or delete an assertion "
        "(DF-8-5-B: 'Do not close it by loosening an assertion')."
    )


def _cited_sha(artifact: str) -> str:
    path = _ARTIFACT_DIR / artifact
    assert path.exists(), f"the committed artifact {artifact} is missing from {_ARTIFACT_DIR}"
    text = path.read_text(encoding="utf-8")
    match = _PROVENANCE.search(text)
    assert match is not None, (
        f"{artifact} carries no parseable `- Commit descriptor …: \\`<sha>\\`` provenance line, so "
        "nothing can be said about which tree it describes. Every renderer emits one."
        + _remedy(artifact)
    )
    return match.group("sha")


def _argus_unchanged_since(sha: str) -> bool:
    """(b) of the currency property: has ``argus/**`` moved since *sha*?"""
    return _git("diff", "--quiet", sha, "HEAD", "--", "argus/").returncode == 0


def _is_ancestor_of_head(sha: str) -> bool:
    """(a) of the currency property: is *sha* a real commit on ``HEAD``'s history?"""
    return _git("merge-base", "--is-ancestor", sha, "HEAD").returncode == 0


def test_TC_ArgusAgent_DOGFOOD_001_49_every_artifact_cites_a_real_ancestor_of_head() -> None:
    """TC-ArgusAgent-DOGFOOD-001-49 — AC3: the cited provenance is a real commit, on this history.

    Half (a) of the currency property, and the mechanised form of the operator ruling of
    2026-08-12 (*"every regenerated artifact must cite a truthful provenance sha that is an
    ancestor of HEAD"*). This is not hypothetical: the artifact Story 10.4 replaced cited
    ``7be90f77``, which is NOT an ancestor of this history — it survives only on a branch
    literally named ``backup/pre-rebase-fix``. The orphaned-provenance failure this assertion
    exists to prevent has already happened here once, by rebase.
    """
    assert _CURRENT_ARTIFACTS, "the artifact registry is empty — this guard would check nothing"
    for artifact in sorted(_CURRENT_ARTIFACTS):
        sha = _cited_sha(artifact)
        assert _git("cat-file", "-e", f"{sha}^{{commit}}").returncode == 0, (
            f"{artifact} cites provenance sha {sha!r}, which is not a commit in this repository. "
            "The artifact describes a tree nobody can check out." + _remedy(artifact)
        )
        assert _is_ancestor_of_head(sha), (
            f"{artifact} cites provenance sha {sha!r}, which is a real commit but NOT an ancestor "
            "of HEAD — it is on an abandoned or rebased history, so the tree it describes is not "
            "on the line of development this repository is on." + _remedy(artifact)
        )


def test_TC_ArgusAgent_DOGFOOD_001_50_no_artifact_describes_a_superseded_argus_tree() -> None:
    """TC-ArgusAgent-DOGFOOD-001-50 — AC3: THE currency assertion. Closes DF-8-5-B + DF-10-4-D.

    Half (b): ``argus/**`` has not moved since the tree each artifact says it describes. Every
    figure these artifacts publish — the population, the total LOC, the cut edges, each
    ``partition_id``, the sized ceiling ``$X``, the NFR-C1 baseline ratio, the critical-set size —
    is derived from the content of ``argus/**``, so this is the exact condition under which those
    figures are still true. A guard that instead re-asserted three tokens the artifact happens to
    contain is what let all three rot across two epics with every gate green.
    """
    stale: dict[str, str] = {}
    for artifact in sorted(_CURRENT_ARTIFACTS):
        sha = _cited_sha(artifact)
        if not _argus_unchanged_since(sha):
            stat = _git("diff", "--shortstat", sha, "HEAD", "--", "argus/").stdout.strip()
            stale[artifact] = f"cites {sha[:7]}; argus/ has moved since ({stat or 'changed'})"

    assert not stale, (
        "STALE committed dogfood artifact(s) — each describes an `argus/` tree that no longer "
        "exists, so every figure it publishes (population, total LOC, cut edges, partition_ids, "
        "the sized ceiling $X, the NFR-C1 baseline ratio) is a claim about a tree nobody is "
        "running:\n  "
        + "\n  ".join(f"{name}: {why}" for name, why in stale.items())
        + _remedy(sorted(stale)[0])
    )


def test_TC_ArgusAgent_DOGFOOD_001_51_the_registry_is_closed_and_the_remedy_is_real() -> None:
    """TC-ArgusAgent-DOGFOOD-001-51 — AC3: a fourth artifact cannot escape by being new, and the
    named remedy exists.

    Two closures that a guard of this kind needs and that this repository has shipped without
    before. **(1) The registry is closed over the tree**: the artifacts are resolved by GLOB and
    anything found that is neither registered nor a named preserved record FAILS — so a future
    story cannot add a fourth committed artifact that silently escapes the currency rule (the
    ``_REPORT_POINTERS`` fail-on-unregistered shape Story 8.3 established, ``AI-E8-6``).
    **(2) The remedy is not a sentence**: ``DF-8-5-B``'s close condition is *"a documented
    regeneration entry point named in the failure message"*, and a named command that does not
    exist is worse than none — so the script is asserted to exist, to be the command the message
    names, and to call all three renderers.
    """
    found = {
        path.name
        for path in _ARTIFACT_DIR.glob("minions-dogfood-*.md")
        if path.is_file()
    }
    assert found, (
        "the `minions-dogfood-*.md` glob resolved to NOTHING under "
        f"{_ARTIFACT_DIR} — the artifacts are gone or the path is wrong, and every assertion in "
        "this file is vacuous"
    )
    unregistered = sorted(found - set(_CURRENT_ARTIFACTS) - set(_PRESERVED_RECORDS))
    assert not unregistered, (
        f"committed dogfood artifact(s) exist but are not registered: {unregistered}. Add each to "
        "_CURRENT_ARTIFACTS (with its renderer) so the currency rule covers it, or to "
        "_PRESERVED_RECORDS WITH A WRITTEN REASON if it is a frozen historical record. Never "
        "leave one unregistered — that is how the rule ends up covering less than it claims."
    )
    missing = sorted(set(_CURRENT_ARTIFACTS) - found)
    assert not missing, f"registered artifact(s) absent from the tree: {missing}"

    for name, reason in _PRESERVED_RECORDS.items():
        assert len(reason) >= 80, f"preserved record {name!r} carries no substantive reason"
        assert name in found, (
            f"preserved record {name!r} is registered but no longer present; delete the entry "
            "rather than leaving a reason for a file that is gone"
        )

    assert _REGENERATION_SCRIPT.is_file(), (
        f"the failure messages in this file name `{REGENERATION_COMMAND}` as the remedy, and the "
        f"script does not exist at {_REGENERATION_SCRIPT}. A named remedy that cannot be run is "
        "worse than no remedy: it costs the reader the time to find out."
    )
    script = _REGENERATION_SCRIPT.read_text(encoding="utf-8")
    for renderer in ("render_partition_plan_markdown", "render_budget_plan_markdown", "render_proof_markdown"):
        assert renderer in script, (
            f"the regeneration entry point does not call {renderer!r}, so running it would leave "
            "at least one artifact stale — and the failure message would have sent the reader to "
            "a command that does not fix their problem"
        )
    assert REGENERATION_COMMAND in _remedy("minions-dogfood-proof.md"), (
        "the failure-message remedy no longer names the regeneration command (DF-8-5-B's stated "
        "close condition)"
    )
    # The rendered artifacts really do carry the provenance line this guard parses — proven by
    # rendering live rather than by trusting the committed bytes.
    from argus.dogfood.partition_plan import build_full_repo_plan

    plan = build_full_repo_plan(str(_REPO_ROOT))
    for rendered in (render_partition_plan_markdown(plan), render_budget_plan_markdown(plan)):
        assert _PROVENANCE.search(rendered) is not None, (
            "a renderer no longer emits a `- Commit descriptor …: `<sha>`` line, so this guard "
            "would stop being able to read any provenance at all and would fail for the wrong "
            "reason. Update the _PROVENANCE pattern deliberately, do not delete the assertion."
        )


def test_TC_ArgusAgent_DOGFOOD_001_52_the_currency_predicate_bites_on_real_history() -> None:
    """TC-ArgusAgent-DOGFOOD-001-52 — AC3 non-vacuity: the predicate separates honest from rotten.

    A currency guard that answered *"current"* for every sha would be green forever, and one that
    answered *"stale"* for every sha would be the permanent two-step tax ``DF-8-5-B`` was filed
    about. Both failure modes are refuted here, and the adversarial set is **GENERATED from the
    repository's own commit history** rather than hand-listed: every commit reachable from ``HEAD``
    is classified by the same :func:`_argus_unchanged_since` the assertion above uses, and BOTH
    classes must be non-empty, with their counts asserted.

    The counts are deliberately not pinned to specific numbers — they grow with the repository —
    but their non-emptiness is the whole property: there exist real shas this guard calls stale
    (so it can fire) and real shas it calls current (so it is not a permanent red).
    """
    revs = _git("rev-list", "--max-count=400", "HEAD").stdout.split()
    assert len(revs) >= 10, (
        f"only {len(revs)} commits reachable from HEAD; the generated adversarial set is too small "
        "to prove anything about this predicate"
    )

    current = [sha for sha in revs if _argus_unchanged_since(sha)]
    stale = [sha for sha in revs if sha not in set(current)]

    assert current, (
        f"NOT ONE of the {len(revs)} commits in this history is 'current' by this predicate — it "
        "answers 'stale' for everything, which would make it a permanent red and exactly the "
        "two-step tax DF-8-5-B was filed about"
    )
    assert stale, (
        f"ALL {len(revs)} commits in this history are 'current' by this predicate — it can never "
        "fire, and this whole file would be a vacuous guard of the class it exists to close. "
        "argus/** has demonstrably changed across this history"
    )
    assert len(current) + len(stale) == len(revs)

    # HEAD itself must be current (the trivially true end of the range), and the OLDEST reachable
    # commit must be stale — both derived, not assumed.
    head = _git("rev-parse", "HEAD").stdout.strip()
    assert _argus_unchanged_since(head), (
        "the predicate says argus/ has changed since HEAD itself, which is impossible — it is "
        "comparing the wrong trees and every result above is meaningless"
    )
    assert not _argus_unchanged_since(revs[-1]), (
        f"the predicate says argus/ has NOT changed since the oldest reachable commit "
        f"({revs[-1][:7]}), across {len(revs)} commits of development — it is structurally "
        "incapable of seeing a change and cannot guard anything"
    )
    assert all(_is_ancestor_of_head(sha) for sha in revs[:20]), (
        "a commit reachable from HEAD is not an ancestor of HEAD — the ancestry probe used by "
        "-49 is broken, so its assertion would pass vacuously"
    )
