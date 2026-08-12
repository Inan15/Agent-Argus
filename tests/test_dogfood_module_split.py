"""Story 9.2 / AC8 (ledger item ``DF-8-5-D``) — the ``proof_run.py`` split cannot rot.

Verification area ArgusAgent-DOGFOOD (``TC-ArgusAgent-DOGFOOD-001-NN``, CONTINUING the
index). ⚠️ Index correction recorded here because it matters to the next author: the
Story-9.2 context said ``-36`` was the highest id taken and that new tests start at
``-37``. Measured on this tree, ``tests/test_dogfood_proof.py`` and
``tests/test_dogfood_plan.py`` already carry ``-37`` through ``-44`` (Story 8.5's DR-10
members and its review-iteration patches). **The first free id is ``-45``**, which is
where this module starts.

What was moved and why. ``argus/dogfood/proof_run.py`` stood at 1196 lines against the
NFR-M1 1200-line ceiling and carried five responsibilities. Story 9.2 extracted the five
frozen result dataclasses to ``argus/dogfood/proof_types.py`` and the pure markdown
renderer to ``argus/dogfood/proof_render.py``, re-exporting both from ``proof_run.py``.

The reason for the timing is the LEDGER, not the ceiling, and this file records the
measured version because the inherited narrative says otherwise: the ``DF-8-5-A`` version
fix (sourcing ``DOGFOOD_ArgusAgent_VERSION`` from ``argus.__version__``) is +3 lines net
and left ``proof_run.py`` at 1199/1200 — it FIT. What forced the extraction is
``DF-8-5-D``'s ``target_story``, *"the first story that edits ``argus/dogfood/proof_run.py``
for any reason"*, combined with Story 9.2 being the last story in the plan.

What these tests protect (AI-E8-6 — enumerate the space, fail on the unenumerated):

  ``-45``  every name in ``proof_run.__all__`` still imports from ``proof_run``, AND the
           surface has not SHRUNK — a name dropped from ``__all__`` fails, so the guard
           cannot be satisfied by making it smaller.
  ``-46``  the moved names are re-exports, not forks: ``proof_run.X is proof_types.X``.
  ``-47``  all three modules are ≤1200 lines and the two PURE ones are structurally pure
           — no import of the impure shell (which would be a cycle), no I/O.
  ``-48``  ``DOGFOOD_EXTERNALIZATION_GUARD`` moved WITH its only consumer and its text is
           byte-for-byte what it was — "unchanged" verified, not asserted (Story 9.2 /
           AC12).

No network, no LLM, no ``.argus/`` write, no new dependency (NFR-D2): every assertion
here is over the import graph and the source text.
"""

from __future__ import annotations

import ast
from pathlib import Path

from argus.dogfood import proof_render, proof_run, proof_types

_REPO_ROOT = Path(__file__).resolve().parents[1]

# The public import surface as it stood BEFORE the extraction, read off
# ``proof_run.__all__`` at HEAD 7be90f7. Frozen here so the guard fails on a REMOVAL as
# well as on a broken import — a shrinking surface is the failure mode a bare
# "every name in __all__ imports" check is blind to.
_PRE_SPLIT_PUBLIC_SURFACE: frozenset[str] = frozenset(
    {
        "DOGFOOD_PROOF_SCHEMA_VERSION",
        "DOGFOOD_BUDGET_CEILING",
        "DOGFOOD_GRADE",
        "DOGFOOD_ArgusAgent_VERSION",
        "DogfoodProofError",
        "AdjudicationRow",
        "CostSummary",
        "ScopeDisclosure",
        "CriticalClauseDisclosure",
        "DogfoodProofRun",
        "enumerate_tracked_sources",
        "materialize_snapshot",
        "run_dogfood",
        "adjudication_rows",
        "cost_summary",
        "build_dogfood_proof",
        "render_proof_markdown",
    }
)

# The five frozen dataclasses that moved, and the module they moved to.
_MOVED_TO_TYPES = (
    "AdjudicationRow",
    "CostSummary",
    "ScopeDisclosure",
    "CriticalClauseDisclosure",
    "DogfoodProofRun",
)
# What moved to the renderer module.
_MOVED_TO_RENDER = ("render_proof_markdown", "DOGFOOD_EXTERNALIZATION_GUARD")

_DOGFOOD_MODULES = {
    "argus/dogfood/proof_run.py": "impure",
    "argus/dogfood/proof_render.py": "pure",
    "argus/dogfood/proof_types.py": "pure",
}

_NFR_M1_LINE_CEILING = 1200

# Names whose presence in a PURE module would mean it does I/O, reads a clock, or spawns
# a process. Enumerated so a future edit that smuggles one in fails rather than merely
# contradicting a docstring.
_IMPURE_NAMES = (
    "open",
    "subprocess",
    "shutil",
    "requests",
    "httpx",
    "socket",
    "datetime",
    "time",
    "random",
    "uuid",
    "os",
)


def test_TC_ArgusAgent_DOGFOOD_001_45_public_import_surface_survives_the_split() -> None:
    """TC-ArgusAgent-DOGFOOD-001-45 — AC8: every ``__all__`` name still imports, and none was dropped.

    ``importlib`` is not enough: the point of the shim is that a caller writing
    ``from argus.dogfood.proof_run import DogfoodProofRun`` — the literal statement that
    exists at call sites across ``tests/`` — keeps working. So the check executes that
    statement for every name, one at a time.
    """
    surface = set(proof_run.__all__)

    # (a) The surface did not SHRINK. A name removed from __all__ fails here, so the
    #     extraction cannot be "made green" by narrowing what it promises.
    missing = _PRE_SPLIT_PUBLIC_SURFACE - surface
    assert not missing, (
        f"__all__ lost names across the DF-8-5-D split: {sorted(missing)} — the shim "
        "must preserve the public import surface, not redefine it"
    )

    # (b) Every advertised name really resolves through `proof_run`.
    unresolved = [name for name in sorted(surface) if not hasattr(proof_run, name)]
    assert not unresolved, f"__all__ advertises names that do not resolve: {unresolved}"

    # (c) And through the real `from ... import <name>` statement, per name.
    for name in sorted(surface):
        namespace: dict[str, object] = {}
        exec(f"from argus.dogfood.proof_run import {name}", namespace)  # noqa: S102
        assert name in namespace, f"`from argus.dogfood.proof_run import {name}` failed"

    # Non-vacuity: the surface is the real one, not an empty set that trivially passes.
    assert len(surface) == len(_PRE_SPLIT_PUBLIC_SURFACE) == 17


def test_TC_ArgusAgent_DOGFOOD_001_46_moved_names_are_reexports_not_forks() -> None:
    """TC-ArgusAgent-DOGFOOD-001-46 — AC8/AR7: the shim re-exports; it does not re-declare.

    Object IDENTITY is the falsifiable form of "no fork". If ``proof_run`` ever grows its
    own second ``DogfoodProofRun``, every ``isinstance`` check in the suite would still
    pass while two incompatible classes circulated — the exact defect AR7 exists to
    prevent. ``is`` catches it; ``==`` would not.
    """
    for name in _MOVED_TO_TYPES:
        assert getattr(proof_run, name) is getattr(proof_types, name), (
            f"proof_run.{name} is not the same object as proof_types.{name} (a fork)"
        )
        assert getattr(proof_types, name).__module__ == "argus.dogfood.proof_types"
    for name in _MOVED_TO_RENDER:
        assert getattr(proof_run, name) is getattr(proof_render, name), (
            f"proof_run.{name} is not the same object as proof_render.{name} (a fork)"
        )
    assert proof_render.render_proof_markdown.__module__ == "argus.dogfood.proof_render"
    # The five moved dataclasses are still FROZEN (the split must not relax the contract).
    for name in _MOVED_TO_TYPES:
        cls = getattr(proof_types, name)
        assert getattr(cls, "__dataclass_params__").frozen, f"{name} is no longer frozen"


def test_TC_ArgusAgent_DOGFOOD_001_47_three_modules_fit_and_the_pure_ones_are_pure() -> None:
    """TC-ArgusAgent-DOGFOOD-001-47 — AC8/NFR-M1/AR8: sizes measured, purity structural.

    The AR8 pure/impure line used to live in a docstring paragraph. After the split it is
    a property of the import graph: ``proof_render`` and ``proof_types`` may not import
    ``proof_run``. That is not merely a rule — a violation would be an import CYCLE, and
    the assertion below states the direction explicitly so a reviewer sees which way the
    edge is allowed to run.
    """
    for rel, kind in _DOGFOOD_MODULES.items():
        path = _REPO_ROOT / rel
        source = path.read_text(encoding="utf-8")
        n_lines = len(source.splitlines())
        assert n_lines <= _NFR_M1_LINE_CEILING, (
            f"{rel} is {n_lines} lines, over the NFR-M1 ceiling of {_NFR_M1_LINE_CEILING}"
        )
        assert n_lines > 100, f"{rel} is suspiciously small ({n_lines} lines)"
        if kind != "pure":
            continue
        tree = ast.parse(source)
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module)
        assert "argus.dogfood.proof_run" not in imported, (
            f"{rel} imports the IMPURE shell — that is an import cycle and it destroys "
            "the AR8 separation the split exists to make structural"
        )
        for banned in _IMPURE_NAMES:
            assert banned not in imported, f"{rel} imports the impure module {banned!r}"
        called = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        assert "open" not in called, f"{rel} calls open() — a PURE module performs no I/O"


def test_TC_ArgusAgent_DOGFOOD_001_48_externalization_guard_moved_unchanged() -> None:
    """TC-ArgusAgent-DOGFOOD-001-48 — AC8/AC12: the guard sentence is byte-for-byte the same.

    ``DOGFOOD_EXTERNALIZATION_GUARD`` moved from ``proof_run.py`` to ``proof_render.py``
    because the renderer is its ONLY consumer and leaving it behind would have forced
    ``proof_render -> proof_run``, i.e. the cycle. Story 9.2 / AC12 requires the guard to
    be *verified* unchanged rather than assumed, so its text is pinned here in full. If a
    future edit softens the honesty language, this fails — which is the whole point of a
    red-team guard: it must be harder to weaken than to leave alone.

    🔴 AMENDED 2026-08-13 by Story 12.2 (AC6.3). THE SENTENCE WAS FALSE IN TWO WAYS and
    both are repaired by making it TRUE, never by deleting the honesty language:

    * Its FACTUAL first clause — *"the AST-grounding deep-audit seam is NOT wired in"* —
      became false the moment 12.2 wired FR36. This test going red at that moment is the
      guard WORKING.
    * Its CAUSAL claim — *seam not wired in, **so** every finding is advisory* — was
      ALREADY false, before 12.2 changed anything, and no test had ever checked it.
      Measured on ``2bea92f`` by execution: a DEFAULT ``python -m argus.cli audit`` over a
      synthetic repository — no flags, no LLM, no cartridge harness — returned
      ``verdict=NOT_READY_FOR_RELEASE blocking_findings=1`` and EXIT CODE 2, via
      ``argus/detectors/vacuous_test.py``'s two-fact AST corroboration emitting a
      ``RULE_AST`` finding with a non-``None`` ``depth_supported``. So advisory-ness was
      never a consequence of the seam being unwired — it is a contingent property of the
      Argus dogfood corpus. That measurement is committed as
      ``TC-ArgusAgent-VERDICT-001-30`` so the answer cannot rot back into a guess.

    The replacement says all of that, and the two honesty clauses (*"NOT presented as
    externalization or assurance evidence"*, *"does NOT clear the >=80%-precision gate"*)
    survive verbatim and are asserted separately below so a future rewrite cannot drop
    them while still matching some new pinned string.
    """
    expected = (
        "This dogfood run is a demo-heuristic-only (Tier-A) result: the frozen pipeline "
        "run_audit_detailed calls NO LLM (zero-token). Since 2026-08-13 (Story 12.2) the "
        "AST-grounding deep-audit seam IS wired, but it is OFF BY DEFAULT and was NOT "
        "engaged by this run — no --deep-audit, no dispatch, no provider contacted — so no "
        "finding here rests on a deep read. Every finding in this run is in fact advisory / "
        "verdict-ineligible (depth_supported is None), and that is a MEASURED property of "
        "the Argus dogfood corpus, NOT a consequence of the seam: a verdict-BLOCKING finding "
        "is reachable on the default zero-LLM path (argus/detectors/vacuous_test.py emits "
        "RULE_AST with a non-None depth_supported), so this run being advisory throughout is "
        "a fact about this repository and must never be read as a guarantee about any other. "
        "It is NOT presented as externalization or assurance evidence, and it does NOT clear "
        "the >=80%-precision gate — that requires the human TP/FP adjudication over these "
        "REAL findings (a documented human step, still open)."
    )
    assert proof_render.DOGFOOD_EXTERNALIZATION_GUARD == expected, (
        "the externalization guard text changed; it is the red-team honesty flag and "
        "Story 9.2 / AC12 requires it intact"
    )
    assert proof_run.DOGFOOD_EXTERNALIZATION_GUARD is expected or (
        proof_run.DOGFOOD_EXTERNALIZATION_GUARD
        is proof_render.DOGFOOD_EXTERNALIZATION_GUARD
    )
    # And no over-claim phrase was introduced alongside it.
    lowered = proof_render.DOGFOOD_EXTERNALIZATION_GUARD.lower()
    for overclaim in (
        "externalization-grade",
        "validated deep audit",
        "gate cleared",
        "externally validated",
        "independently validated",
    ):
        assert overclaim not in lowered, f"the guard now contains the over-claim {overclaim!r}"

    # Story 12.2 / AC6.3 — the honesty language is asserted SEPARATELY from the byte pin,
    # so a future amendment can change the wording around it but can never drop it while
    # quietly updating the pinned string to match. These clauses are the guard's payload.
    for load_bearing in (
        "NOT presented as externalization or assurance evidence",
        "does NOT clear the >=80%-precision gate",
        "a documented human step, still open",
    ):
        assert load_bearing in proof_render.DOGFOOD_EXTERNALIZATION_GUARD, (
            f"the guard lost its load-bearing honesty clause {load_bearing!r}. AC6.3: the "
            "honesty language must survive intact or be STRENGTHENED, never softened."
        )
    # And the repaired sentence must not re-assert either falsehood it was amended to fix.
    assert "seam is NOT wired in" not in proof_render.DOGFOOD_EXTERNALIZATION_GUARD, (
        "the factual clause Story 12.2 falsified was re-introduced"
    )
    assert "OFF BY DEFAULT" in proof_render.DOGFOOD_EXTERNALIZATION_GUARD, (
        "a wired egress seam must be disclosed as off-by-default, not merely as wired"
    )
