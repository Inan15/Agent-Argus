"""Cartridge staging helper — copy a cartridge template into a fresh git repo.

Verification area ArgusAgent-CARTRIDGE. The cartridge files live as ``*.py.txt``
templates (so the main pytest run never collects them); this helper materializes
a cartridge into a fresh temp directory, strips the ``.txt`` suffix, ``git
init``s + commits once, and returns ``(repo_path, commit_sha)``.

Why a fresh staged git repo per run (the LOCKED cartridge-pinning approach)
--------------------------------------------------------------------------
``load_repo_at_commit`` (story 1.4) requires a clean working tree whose HEAD IS
the resolved pin (it audits committed state, refusing drift). A fresh
single-commit repo satisfies that deterministically and keeps the audited byte
content fixed by the committed templates — so the same cartridge audited twice
yields byte-identical ``.argus/`` verdict output (AC5 / NFR-P1). The commit SHA
itself varies per run (author/commit timestamps), but the SHA is NOT part of the
hashed verdict payload (NFR-D3 excludes volatile fields), so AC5 byte-identity
holds when callers pass a stable commit ref (``"HEAD"``) and compare the verdict
envelope ``content_hash``.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

_CARTRIDGES_ROOT = Path(__file__).resolve().parent
_TEMPLATE_SUFFIX = ".txt"


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
    )


def _materialize_templates(cartridge_id: str, dest: Path) -> None:
    source_root = _CARTRIDGES_ROOT / cartridge_id
    if not source_root.is_dir():
        raise FileNotFoundError(f"unknown cartridge id: {cartridge_id!r}")
    for template in sorted(source_root.rglob(f"*{_TEMPLATE_SUFFIX}")):
        rel = template.relative_to(source_root)
        # Strip the trailing ``.txt`` so ``calculator.py.txt`` → ``calculator.py``.
        target_rel = rel.with_suffix("")
        target = dest / target_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(template, target)


def stage_cartridge(cartridge_id: str, dest: Path) -> tuple[Path, str]:
    """Stage *cartridge_id* into *dest* as a fresh committed git repo.

    Returns ``(repo_path, commit_sha)`` — the resolved full HEAD SHA after the
    single commit. *dest* must be empty/new (typically a pytest ``tmp_path``
    subdir). Uses a deterministic author/committer identity so the staging itself
    is reproducible across hosts (the SHA still varies by timestamp, which is fine
    — see the module docstring).
    """
    dest.mkdir(parents=True, exist_ok=True)
    _materialize_templates(cartridge_id, dest)

    _run_git(dest, "init")
    _run_git(dest, "config", "core.autocrlf", "false")
    _run_git(dest, "config", "user.email", "cartridge@argus.test")
    _run_git(dest, "config", "user.name", "ArgusAgent Cartridge")
    (dest / ".gitignore").write_text(".argus/\n", encoding="utf-8")
    _run_git(dest, "add", "-A")
    _run_git(dest, "commit", "-m", f"cartridge {cartridge_id}")



    sha = subprocess.run(
        ["git", "-C", str(dest), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return dest, sha
