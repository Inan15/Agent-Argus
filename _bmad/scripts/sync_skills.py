"""Skill tree synchronization utility between .agent/skills and .claude/skills.

Ensures agent skill files remain byte-identical across .agent and .claude provider trees
to prevent maintenance drift (Finding 6.1).
"""

from __future__ import annotations

import filecmp
import os
import shutil
from pathlib import Path


def sync_skills(src_dir: Path, dst_dir: Path, dry_run: bool = False) -> list[str]:
    """Synchronize files from src_dir to dst_dir."""
    updated: list[str] = []
    for root, _, files in os.walk(src_dir):
        rel_root = os.path.relpath(root, src_dir)
        target_root = dst_dir / rel_root
        
        for f in files:
            src_file = Path(root) / f
            dst_file = target_root / f
            
            if not dst_file.exists() or not filecmp.cmp(src_file, dst_file, shallow=False):
                updated.append(os.path.join(rel_root, f))
                if not dry_run:
                    target_root.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dst_file)
    return updated


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    agent_skills = repo_root / ".agent" / "skills"
    claude_skills = repo_root / ".claude" / "skills"

    if not agent_skills.exists():
        print(f"Error: {agent_skills} does not exist.")
        return

    print(f"Synchronizing {agent_skills} -> {claude_skills}...")
    updated = sync_skills(agent_skills, claude_skills)
    print(f"Sync complete. {len(updated)} files updated.")


if __name__ == "__main__":
    main()
