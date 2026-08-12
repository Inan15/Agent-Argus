"""Story 12.1 / AC1 — the NFR-M1 extraction did not move the PUBLIC IMPORT SURFACE.

Verification area ArgusAgent-PIPELINE (``TC-ArgusAgent-PIPELINE-002-14``..``-16``, continuing
the index Story 11.2 left at ``-13``).

**Why this file exists, and why it did not exist before.** AC1 requires that
``argus.pipeline.__all__`` still exports ``PipelineError`` / ``ResumeStateError`` /
``AuditResult`` / ``run_audit`` / ``run_audit_detailed`` / ``resume_audit_detailed`` /
``resume_audit`` and says *"Pinned by test."* The first implementation round left that clause
**unpinned**: the surface really was byte-identical (independently diffed against ``ca37283``),
but the only thing holding it there was the *indirect* coverage of other tests that happen to
``from argus.pipeline import <name>``. That coverage catches exactly one mutation — the removal
of a name some other test already imports. It cannot see

* the removal of a name **nothing** imports today (``resume_audit`` and ``run_audit`` are the
  documented entry points for *consumers*, not for this suite),
* an **addition** — the split re-exports sixteen private helpers back into ``pipeline``; one of
  them slipping into ``__all__`` would silently widen the published surface, and a published
  surface cannot be narrowed again without a breaking change,
* a **reorder**, which is invisible to every importer and visible to anyone who diffs the file
  or reads ``__all__`` as the module's stated contract.

So the claim *"the public import surface is unchanged"* was true and **unfalsifiable**, which is
this project's dominant defect class (``AI-E11-1``: *the defect exists while every observable the
guard watches is unchanged*) — the same class Story 12.1 was chartered to close, one clause away
from where it closed it. This file makes the claim falsifiable, following the named precedent:
``tests/test_dogfood_module_split.py::TC-ArgusAgent-DOGFOOD-001-45`` pins
``argus.dogfood.proof_run.__all__`` across the ``DF-8-5-D`` split — *no name dropped, and the
surface did not shrink* — and ``-46`` pins the re-exports as the SAME OBJECTS rather than forks.

**The pin is DERIVED, not transcribed** (``AI-E9-7`` / ``AI-E10-5``, *the list is never the
contract*). ``-15`` re-reads ``__all__`` out of the pre-split blob ``ca37283:argus/pipeline.py``
by ``ast`` and requires it to equal both the literal below and the live module, so the literal
cannot quietly drift away from the pre-split truth it claims to record. Editing the literal to
match a changed surface is therefore not enough to make this file green — the pre-split blob is
immutable history.

**Non-vacuity is mandatory** (five precedents: ``-39``, ``-118``, ``-51``, ``-99``, ``-122``).
``-16`` GENERATES its adversarial set from the live surface rather than hand-listing it — every
single-name deletion, every adjacent transposition, every addition and every duplication,
``4n − 1`` mutants for an ``n``-name surface (27 today), each driven through the SAME predicate
``-14`` uses, with both directions asserted: every mutant is rejected AND the unmutated surface
is accepted. A guard that rejected everything would pass a one-directional check.

**Scope.** This file pins the SURFACE, not the split's purity. The 28-of-29 byte-identity of the
moved and retained definitions is recorded in the story's AC1 Completion Notes with its
re-derivation; the one intentional exception (``_assessment_scope_paths``, rewritten by the same
story's ``DF-8-3-C`` de-duplication) is a body change behind an unchanged surface — which is
precisely the distinction this file exists to keep honest.
"""

from __future__ import annotations

import ast
import subprocess
from pathlib import Path

from argus import pipeline, pipeline_stages

_REPO_ROOT = Path(__file__).resolve().parents[1]

#: The commit this story started from — the last tree in which ``argus/pipeline.py`` was
#: un-split. Immutable history: an ancestor of ``HEAD`` (asserted by ``-15``), so it is a
#: sound anchor for "the pre-split form" for as long as this repository keeps its history.
_PRE_SPLIT_SHA = "ca37283"

#: ``argus.pipeline.__all__`` as it stood at :data:`_PRE_SPLIT_SHA`. Written out so a red here
#: says WHAT the surface was, not merely that it moved — and re-derived from the blob by ``-15``
#: so it can never become a comfortable fiction.
_PRE_SPLIT_ALL: tuple[str, ...] = (
    "PipelineError",
    "ResumeStateError",
    "AuditResult",
    "run_audit",
    "run_audit_detailed",
    "resume_audit_detailed",
    "resume_audit",
)

#: The house line every failure message here ends with.
_WORKING = (
    "A red here is the guard working. `argus.pipeline.__all__` is the PUBLISHED import surface "
    "of this package: Story 12.1 moved sixteen private helpers into `argus/pipeline_stages.py` "
    "on the explicit promise (AC1) that the surface did not move. If you MEANT to change it, "
    "that is a breaking change to a published API — take it in a story that says so, update "
    "`_PRE_SPLIT_ALL` and this docstring together, and note that `-15` will still hold the "
    f"literal against the immutable pre-split blob at {_PRE_SPLIT_SHA}."
)


def _surface_is_intact(candidate: object) -> bool:
    """The guard's ONE predicate: is ``candidate`` the pre-split surface, exactly?

    Exact LIST equality, never set equality: order and multiplicity are part of a published
    ``__all__``, and set equality would wave through both a reorder and a duplication. ``-14``
    drives the live module through this; ``-16`` drives 27 generated mutants through the same
    function, so the adversarial evidence cannot drift from the assertion it is evidence for.
    """
    if not isinstance(candidate, (list, tuple)):
        return False
    return list(candidate) == list(_PRE_SPLIT_ALL)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(_REPO_ROOT), *args], capture_output=True, text=True, timeout=120
    )


def _all_from_blob(sha: str) -> list[str]:
    """Read ``__all__`` OUT OF a committed ``argus/pipeline.py`` blob, by ``ast``.

    Never imports it and never transcribes it. A missing blob or a missing ``__all__`` is a
    FAILURE, never a skip: a guard that quietly stops checking when its evidence is unavailable
    is the vacuous guard this repository keeps filing as a defect.
    """
    shown = _git("show", f"{sha}:argus/pipeline.py")
    assert shown.returncode == 0, (
        f"cannot read the pre-split blob {sha}:argus/pipeline.py — this guard holds the live "
        f"surface against IMMUTABLE HISTORY and cannot be evaluated without it "
        f"(git said: {shown.stderr.strip()!r}). {_WORKING}"
    )
    for node in ast.parse(shown.stdout).body:
        targets = getattr(node, "targets", [])
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "__all__" for t in targets
        ):
            derived = ast.literal_eval(node.value)
            assert isinstance(derived, list) and all(isinstance(n, str) for n in derived)
            return list(derived)
    raise AssertionError(
        f"{sha}:argus/pipeline.py declares no module-level `__all__`, so the pre-split surface "
        f"cannot be re-derived. {_WORKING}"
    )


def test_TC_ArgusAgent_PIPELINE_002_14_public_surface_unchanged_across_the_split() -> None:
    """TC-ArgusAgent-PIPELINE-002-14 — Story 12.1 / AC1: ``__all__`` is byte-identical.

    Observable: the exact ordered list ``argus.pipeline.__all__``. Three checks, in the shape of
    the ``DOGFOOD-001-45`` precedent — the surface is EXACTLY the pre-split one (so it neither
    shrank nor grew nor reordered), every advertised name resolves on the module, and the literal
    ``from argus.pipeline import <name>`` statement that real call sites write still executes for
    each one.
    """
    live = list(pipeline.__all__)

    # (a) The surface did not move: no name dropped, none added, none reordered.
    assert _surface_is_intact(live), (
        f"argus.pipeline.__all__ is {live}, not the pre-split surface "
        f"{list(_PRE_SPLIT_ALL)}. {_WORKING}"
    )

    # (b) Every advertised name really resolves through `pipeline` after the split.
    unresolved = [name for name in live if not hasattr(pipeline, name)]
    assert not unresolved, (
        f"argus.pipeline.__all__ advertises names that do not resolve: {unresolved} — the "
        f"re-export is incomplete. {_WORKING}"
    )

    # (c) And through the real statement a consumer writes, one name at a time.
    for name in live:
        namespace: dict[str, object] = {}
        exec(f"from argus.pipeline import {name}", namespace)  # noqa: S102
        assert name in namespace, f"`from argus.pipeline import {name}` failed. {_WORKING}"

    # Non-vacuity: the surface is the real seven-name one, not an empty list that trivially
    # satisfies every check above.
    assert len(live) == len(_PRE_SPLIT_ALL) == 7, (
        f"the pinned surface has {len(live)} names, not the seven AC1 enumerates. {_WORKING}"
    )


def test_TC_ArgusAgent_PIPELINE_002_15_the_pin_is_derived_from_the_pre_split_blob() -> None:
    """TC-ArgusAgent-PIPELINE-002-15 — Story 12.1 / AC1: the pin is grounded, and re-exports are not forks.

    Observable: ``__all__`` as parsed out of ``ca37283:argus/pipeline.py``, and the object
    identity of every name ``pipeline`` re-exports from ``pipeline_stages``.

    Half one closes the loop ``-14`` alone would leave open: a literal that someone edited to
    match a changed surface would make ``-14`` green again. It cannot make this green, because
    the pre-split blob is immutable history rather than a line in this file.

    Half two is the ``DOGFOOD-001-46`` property: the split re-EXPORTS, it does not re-DECLARE.
    Object identity is the falsifiable form of *"no fork"* — if ``pipeline`` ever grew its own
    second ``_detect_per_file``, every call in the suite would still pass while two derivations
    circulated, and ``monkeypatch.setattr(pipeline, "_detect_per_file", ...)`` — which
    ``tests/test_pipeline_signature_demo.py`` relies on — would stop intercepting the real call.
    """
    ancestry = _git("merge-base", "--is-ancestor", _PRE_SPLIT_SHA, "HEAD")
    assert ancestry.returncode == 0, (
        f"{_PRE_SPLIT_SHA} is not an ancestor of HEAD, so it is not this tree's pre-split form "
        f"and the pin below is anchored to nothing. {_WORKING}"
    )

    derived = _all_from_blob(_PRE_SPLIT_SHA)
    assert derived == list(_PRE_SPLIT_ALL), (
        f"the literal _PRE_SPLIT_ALL in this file says {list(_PRE_SPLIT_ALL)} but "
        f"{_PRE_SPLIT_SHA}:argus/pipeline.py actually declared {derived} — the pin has drifted "
        f"from the history it claims to record. {_WORKING}"
    )
    # And the live module is held against HISTORY DIRECTLY, not only against the literal above,
    # so editing `_PRE_SPLIT_ALL` to match a changed surface cannot make this file green.
    assert list(pipeline.__all__) == derived, (
        f"the live argus.pipeline.__all__ is {list(pipeline.__all__)}, which is not what "
        f"{_PRE_SPLIT_SHA}:argus/pipeline.py published: {derived}. {_WORKING}"
    )

    # The moved family is DERIVED from the sibling module, never hand-listed here.
    moved = sorted(
        node.name
        for node in ast.parse(
            (_REPO_ROOT / "argus" / "pipeline_stages.py").read_text(encoding="utf-8")
        ).body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    )
    assert len(moved) >= 16, (
        f"only {len(moved)} definitions were parsed out of argus/pipeline_stages.py; the "
        f"identity check below would be vacuous. {_WORKING}"
    )
    forks = [
        name
        for name in moved
        if getattr(pipeline, name, None) is not getattr(pipeline_stages, name)
    ]
    assert not forks, (
        f"argus.pipeline re-declares rather than re-exports {forks} — two derivations of the "
        f"same helper would circulate, and monkeypatching argus.pipeline.<name> would stop "
        f"intercepting the real call. {_WORKING}"
    )

    # And none of the sixteen private helpers leaked INTO the published surface.
    leaked = [name for name in moved if name in pipeline.__all__]
    assert not leaked, (
        f"private helpers {leaked} appear in argus.pipeline.__all__ — the split widened the "
        f"published surface, which cannot be narrowed again without a breaking change. "
        f"{_WORKING}"
    )


def test_TC_ArgusAgent_PIPELINE_002_16_generated_mutants_all_fail_the_same_predicate() -> None:
    """TC-ArgusAgent-PIPELINE-002-16 — Story 12.1 / AC1: the guard bites, proven by generation.

    Observable: :func:`_surface_is_intact` — the predicate ``-14`` asserts with — evaluated over
    an adversarial set GENERATED from the live surface, never hand-listed.

    Four mutation families, each a real way a published ``__all__`` rots, and each invisible to
    the indirect coverage that existed before this file: deletion (n), adjacent transposition
    (n−1), addition (n) and duplication (n) — ``4n − 1`` mutants, 27 for today's seven names.
    Both directions are asserted: the unmutated surface is ACCEPTED (first, so that a red here
    is never misattributed — mutating an already-wrong surface generates a "mutant" that is the
    RIGHT surface and proves nothing) and every mutant is then REJECTED, so a predicate that
    simply said "no" to everything is refuted on every run.
    """
    surface = list(pipeline.__all__)
    assert surface, f"the live surface is empty; every mutant below would be vacuous. {_WORKING}"

    # Direction one, asserted FIRST: the predicate accepts the real surface. If the live surface
    # is itself wrong, `-14` is the test that says so and the mutants below are meaningless.
    assert _surface_is_intact(surface), (
        f"the live argus.pipeline.__all__ is {surface}, which is not the pinned surface "
        f"{list(_PRE_SPLIT_ALL)} — see `-14`. Mutating an already-wrong surface proves nothing "
        f"about the predicate, so this test stops here rather than reporting a misleading "
        f"'the guard does not bite'. {_WORKING}"
    )

    mutants: list[tuple[str, list[str]]] = []
    for i, name in enumerate(surface):
        mutants.append((f"deletion of {name!r}", surface[:i] + surface[i + 1 :]))
    for i in range(len(surface) - 1):
        swapped = list(surface)
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        mutants.append((f"reorder of {surface[i]!r}/{surface[i + 1]!r}", swapped))
    for name in surface:
        mutants.append((f"addition of {name}_internal", [*surface, f"{name}_internal"]))
    for name in surface:
        mutants.append((f"duplication of {name!r}", [*surface, name]))

    expected = 4 * len(surface) - 1
    assert len(mutants) == expected >= 20, (
        f"generated {len(mutants)} mutants, expected {expected} (4n−1 over n={len(surface)}); "
        f"the generator stopped closing over the surface. {_WORKING}"
    )

    # Direction two: every mutant is rejected by the SAME predicate `-14` asserts with.
    survivors = [label for label, mutant in mutants if _surface_is_intact(mutant)]
    assert not survivors, (
        f"{len(survivors)} of {len(mutants)} adversarial surfaces PASSED the pin: {survivors} — "
        f"the guard does not bite on that mutation family. {_WORKING}"
    )
