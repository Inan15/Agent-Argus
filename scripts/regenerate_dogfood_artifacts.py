"""Regenerate the three committed dogfood artifacts THROUGH THEIR OWN RENDERERS.

    python scripts/regenerate_dogfood_artifacts.py

**This is the named regeneration entry point** that ``DF-8-5-B`` and ``DF-10-4-D`` asked for
and that Story 12.1 closed them with. Every guard that can go red because a committed dogfood
artifact no longer describes the tree it cites names this command in its failure message, so
the remedy is discoverable from the red output rather than from institutional memory. Three
stories in a row (8.5, 10.4, 12.1) had to re-derive the incantation by reading the source.

**What it does, and what it refuses to do.**

* It renders each artifact by calling the artifact's OWN renderer —
  :func:`render_partition_plan_markdown`, :func:`render_budget_plan_markdown` and
  :func:`render_proof_markdown` — and writes the returned string verbatim. **It cannot
  hand-edit an artifact**, which is the one thing the operator ruling of 2026-08-12 keeps
  forbidden: *"a regeneration is only legitimate when produced by the artifacts' own renderers
  at a truthful sha; hand-editing a dogfood artifact is still forbidden."*
* After each write it **re-reads the file and asserts it equals the renderer's return value**,
  so a partial or re-encoded write cannot pass silently (the Story 10.4 precedent).
* It **refuses to run on a dirty ``argus/`` tree**. The rendered artifacts cite
  ``git rev-parse HEAD`` as their provenance while enumerating the git index; if those two
  trees disagree over ``argus/``, the artifact would cite a commit that does not contain what
  it describes — the exact false-citation class Epic 10 exists to close, and precisely what
  ``TC-ArgusAgent-DOGFOOD-001-49``..``-52`` fail on. **Commit first, then regenerate**: that
  ordering is not a preference, it is the bootstrap ``DF-10-4-D`` named.

Exit codes: ``0`` regenerated (or already byte-identical), ``2`` refused (dirty ``argus/``
tree, or a git failure). It writes only the three artifacts and nothing else; it never stages,
commits, pushes, tags or publishes anything.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:  # running as a script, not an installed console entry
    sys.path.insert(0, str(_REPO_ROOT))

from argus.dogfood.partition_plan import (  # noqa: E402
    build_full_repo_plan,
    render_budget_plan_markdown,
    render_partition_plan_markdown,
)
from argus.dogfood.proof_render import render_proof_markdown  # noqa: E402
from argus.dogfood.proof_run import build_dogfood_proof  # noqa: E402

_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
PARTITION_PLAN = _ARTIFACT_DIR / "minions-dogfood-partition-plan.md"
BUDGET_PLAN = _ARTIFACT_DIR / "minions-dogfood-budget-plan.md"
PROOF = _ARTIFACT_DIR / "minions-dogfood-proof.md"

#: The command a human (or a dev agent reading a red) runs. Named by every guard that can go
#: red on artifact staleness; asserted to be THIS file's real invocation by
#: ``TC-ArgusAgent-DOGFOOD-001-51``.
REGENERATION_COMMAND = "python scripts/regenerate_dogfood_artifacts.py"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(_REPO_ROOT), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def _refuse_if_argus_is_dirty() -> str | None:
    """Return the reason to refuse, or ``None`` when the tree is safe to regenerate from."""
    head = _git("rev-parse", "HEAD")
    if head.returncode != 0:
        return f"`git rev-parse HEAD` failed: {head.stderr.strip() or 'no stderr'}"
    dirty = _git("status", "--porcelain", "--", "argus")
    if dirty.returncode != 0:
        return f"`git status --porcelain -- argus` failed: {dirty.stderr.strip() or 'no stderr'}"
    if dirty.stdout.strip():
        return (
            "`argus/` has uncommitted changes:\n"
            + dirty.stdout.rstrip()
            + "\n\nThe artifacts cite `git rev-parse HEAD` as their provenance while enumerating "
            "the git index. Regenerating now would produce an artifact citing a commit that does "
            "NOT contain the code it describes. COMMIT the `argus/` delta first, then re-run this "
            "script, then commit the regenerated artifacts as a separate commit."
        )
    return None


def _write_verbatim(path: Path, rendered: str) -> bool:
    """Write the renderer's output verbatim and prove the file equals it. Returns changed?"""
    before = path.read_text(encoding="utf-8") if path.exists() else None
    path.write_text(rendered, encoding="utf-8")
    written = path.read_text(encoding="utf-8")
    if written != rendered:  # pragma: no cover - a write that did not round-trip
        raise SystemExit(
            f"{path.name}: the file on disk does not equal the renderer's output after writing"
        )
    return before != rendered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--allow-dirty-argus",
        action="store_true",
        help=(
            "Regenerate even though `argus/` is dirty. The result will cite a provenance sha "
            "that does not contain the code it describes and WILL fail the currency guard. "
            "For diagnosis only."
        ),
    )
    args = parser.parse_args(argv)

    refusal = _refuse_if_argus_is_dirty()
    if refusal is not None and not args.allow_dirty_argus:
        print(f"REFUSED — {refusal}", file=sys.stderr)
        return 2
    if refusal is not None:
        print(f"WARNING (--allow-dirty-argus) — {refusal}", file=sys.stderr)

    plan = build_full_repo_plan(str(_REPO_ROOT))
    changed = {
        PARTITION_PLAN.name: _write_verbatim(PARTITION_PLAN, render_partition_plan_markdown(plan)),
        BUDGET_PLAN.name: _write_verbatim(BUDGET_PLAN, render_budget_plan_markdown(plan)),
    }
    with tempfile.TemporaryDirectory(prefix="argus-dogfood-regen-") as tmp:
        proof = build_dogfood_proof(str(_REPO_ROOT), Path(tmp) / "snapshot")
        changed[PROOF.name] = _write_verbatim(PROOF, render_proof_markdown(proof))

    if plan.commit_descriptor != proof.commit_descriptor:  # pragma: no cover - defensive
        print(
            "REFUSED — the plan and the proof resolved DIFFERENT provenance shas "
            f"({plan.commit_descriptor} vs {proof.commit_descriptor}); HEAD moved mid-run",
            file=sys.stderr,
        )
        return 2

    print(f"provenance sha cited by all three artifacts: {plan.commit_descriptor}")
    print(f"tracked source files enumerated: {plan.source_file_count}   total LOC: {plan.total_loc}")
    for name, did_change in changed.items():
        print(f"  {'REWRITTEN' if did_change else 'unchanged '}  {name}")
    print(
        "\nNow commit the regenerated artifacts as a SEPARATE commit, then re-run the gates."
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry
    raise SystemExit(main())
