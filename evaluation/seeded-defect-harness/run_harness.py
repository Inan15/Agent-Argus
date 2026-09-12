#!/usr/bin/env python3
"""Run Argus over every seeded case in cases/, in both coverage scopes, and record
raw results as JSON + a Markdown table (wq-188). MEASURE ONLY -- this script never
edits argus/**; it only invokes `python -m argus.cli audit` as a subprocess against
each case's own temp git repo.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES_DIR = HERE / "cases"
REPO_ROOT = HERE.parent.parent  # D:/ProjectX/XAgents/XAgents/ArgusAgent


def run(argv, cwd) -> tuple[int, str]:
    done = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True)
    return done.returncode, (done.stdout + done.stderr)


def git_init_commit(root: Path) -> None:
    shutil.rmtree(root / ".argus", ignore_errors=True)
    if not (root / ".git").exists():
        run(["git", "init", "-q", "."], root)
        run(["git", "config", "user.email", "wq188@argus-eval.invalid"], root)
        run(["git", "config", "user.name", "wq-188 seeded-defect harness"], root)
    run(["git", "add", "-A"], root)
    run(["git", "commit", "-qm", "seed"], root)


def parse_summary(out: str) -> dict:
    info = {"verdict_line": None, "blocking_findings": None, "findings": []}
    for line in out.splitlines():
        s = line.strip()
        if s.startswith("verdict="):
            info["verdict_line"] = s
            for part in s.split():
                if part.startswith("verdict="):
                    info["verdict"] = part.split("=", 1)[1]
                if part.startswith("blocking_findings="):
                    try:
                        info["blocking_findings"] = int(part.split("=", 1)[1])
                    except ValueError:
                        pass
        if "rule_id" in s or "vacuous" in s or "orphan_code" in s:
            info["findings"].append(s)
    return info


def read_finding_rule_ids(root: Path) -> list[str]:
    findings_dir = root / ".argus" / "findings"
    if not findings_dir.exists():
        return []
    rule_ids = []
    for f in sorted(findings_dir.glob("*.json")):
        try:
            payload = json.loads(f.read_text(encoding="utf-8"))["payload"]
        except Exception:
            continue
        loc = payload.get("locators") or [{}]
        rule_ids.append(
            f"{payload.get('rule_id')} advisory={payload.get('advisory')} "
            f"depth_supported={payload.get('depth_supported')} @ "
            f"{loc[0].get('file_path')}:{loc[0].get('start_line')}"
        )
    return rule_ids


def audit_case(root: Path, scope: str) -> dict:
    code, out = run(
        [sys.executable, "-m", "argus.cli", "audit", ".", "--coverage-scope", scope],
        root,
    )
    parsed = parse_summary(out)
    parsed["exit_code"] = code
    parsed["raw_tail"] = "\n".join(out.splitlines()[-40:])
    parsed["rule_ids"] = read_finding_rule_ids(root)
    return parsed


def main() -> None:
    results = {}
    case_dirs = sorted(p for p in CASES_DIR.iterdir() if p.is_dir())
    for case_dir in case_dirs:
        name = case_dir.name
        print(f"== {name} ==", flush=True)

        pytest_code, pytest_out = run(
            [sys.executable, "-m", "pytest", "tests/", "-q"], case_dir
        )
        pytest_tail = pytest_out.strip().splitlines()[-1] if pytest_out.strip() else ""

        git_init_commit(case_dir)

        app_scope = audit_case(case_dir, "application")
        repo_scope = audit_case(case_dir, "repository")

        results[name] = {
            "pytest_exit": pytest_code,
            "pytest_tail": pytest_tail,
            "application": app_scope,
            "repository": repo_scope,
        }
        print(
            f"  pytest={pytest_code} app.verdict={app_scope.get('verdict')} "
            f"app.blocking={app_scope.get('blocking_findings')} exit={app_scope.get('exit_code')} | "
            f"repo.verdict={repo_scope.get('verdict')} repo.blocking={repo_scope.get('blocking_findings')} "
            f"exit={repo_scope.get('exit_code')}",
            flush=True,
        )

    out_path = HERE / "results.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
