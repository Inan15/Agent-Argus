"""Subprocess child-runner for the Story 3.5 cross-environment determinism suite.

Drivers: ArgusAgent-FR-32 (run-to-completion on a sequential least-capable host →
byte-identical on-disk state), ArgusAgent-NFR-P1 (least-capable-host byte-identity;
parallel = pure speedup — reframed in V1 as cross-ENVIRONMENT byte-identity of
the single sequential path), ArgusAgent-NFR-P2 (stack-agnostic core), AR8 (the
subprocess + env mutation is the documented impure shell of the TEST harness; the
product code stays pure).

This module is executed as ``python -m`` / ``-c`` import target in a FRESH
interpreter so a deliberately-varied ``PYTHONHASHSEED`` (read once at startup)
actually takes effect — the AC2 mechanism the story locks. It stages a cartridge
into the given working dir, runs ``run_audit_detailed`` (or a halt then resume)
against it, and copies the resulting ``.argus/`` tree to an output dir the parent
process byte-reads. It is NOT a pytest module (no ``test_`` functions); it never
runs under collection.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# When launched as a subprocess neither the repo root nor the cartridges dir is on
# sys.path (the parent pytest run gets them from pytest.ini / conftest).
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent.parent
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_HERE / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import (  # noqa: E402
    resume_audit_detailed,
    run_audit_detailed,
)
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.store.writer import ApaaStoreWriter  # noqa: E402


def _request(repo: Path, budget: int) -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo), commit="HEAD", budget=budget, materiality_bar="default"
    )


def _copy_argus_tree(src_root: Path, dest: Path) -> None:
    """Copy the ``.argus/`` tree from *src_root* to *dest* for the parent to read."""
    argus = src_root / ".argus"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(argus, dest)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ArgusAgent 3.5 portability child-runner")
    parser.add_argument("--cartridge", required=True)
    parser.add_argument("--work-dir", required=True, help="dir to stage the cartridge into")
    parser.add_argument("--out-dir", required=True, help="dir to copy the .argus tree into")
    parser.add_argument("--budget", type=int, default=100)
    parser.add_argument(
        "--mode",
        choices=("clean", "halt", "resume"),
        default="clean",
        help="clean: one run; halt: a single small-budget run; resume: halt then resume",
    )
    parser.add_argument("--halt-budget", type=int, default=6)
    args = parser.parse_args(argv)

    work_dir = Path(args.work_dir)
    out_dir = Path(args.out_dir)

    repo, _sha = stage_cartridge(args.cartridge, work_dir / "repo")

    # The .argus/ store lives OUTSIDE the audited tree (an injected writer rooted in a
    # separate dir) so a resume re-load does not trip the loader's clean-tree drift
    # check on the prior in-tree .argus/ (the Story 3.4 resume seam).
    store_root = work_dir / "store"
    store_root.mkdir(parents=True, exist_ok=True)
    writer = ApaaStoreWriter(store_root)
    reader = ApaaStoreReader(store_root)

    if args.mode == "clean":
        run_audit_detailed(_request(repo, args.budget), store_writer=writer)
    elif args.mode == "halt":
        run_audit_detailed(_request(repo, args.halt_budget), store_writer=writer)
    elif args.mode == "resume":
        run_audit_detailed(_request(repo, args.halt_budget), store_writer=writer)
        resume_audit_detailed(
            _request(repo, args.budget), store_reader=reader, store_writer=writer
        )

    _copy_argus_tree(store_root, out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
