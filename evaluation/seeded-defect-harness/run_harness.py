#!/usr/bin/env python3
"""Run Argus over every seeded case in cases/, in both coverage scopes, and record
raw results as JSON + a Markdown table (wq-188). MEASURE ONLY -- this script never
edits argus/** or cases/**; it copies each case to a temp dir, makes that copy its
own git repo, and invokes `python -m argus.cli audit` there as a subprocess.

Why the copy: the case dirs used to be git-init'ed in place, so a later `git add -A`
in this repo recorded 14 of them as gitlinks (empty in a clone or `git archive`),
and a loop auditing those empty dirs read 4 of 20 where the cases score 17.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES_DIR = HERE / "cases"
REPO_ROOT = HERE.parent.parent  # the checkout this script lives in
# Audit with THIS checkout's argus package, not whatever an editable install points at.
ENV = dict(os.environ, PYTHONPATH=os.pathsep.join(
    p for p in (str(REPO_ROOT), os.environ.get("PYTHONPATH", "")) if p))


def run(argv, cwd) -> tuple[int, str]:
    done = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, env=ENV)
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
    empty = [p.name for p in case_dirs if not any(f.is_file() for f in p.rglob("*"))]
    if empty:
        sys.exit(f"refusing to measure: {len(empty)} case dirs are empty ({', '.join(empty)}); "
                 "run generate_cases.py first")
    work_root = Path(tempfile.mkdtemp(prefix="argus-seeded-"))
    for src_dir in case_dirs:
        name = src_dir.name
        print(f"== {name} ==", flush=True)
        case_dir = work_root / name
        shutil.copytree(src_dir, case_dir, ignore=shutil.ignore_patterns(".git", ".argus", "__pycache__"))

        pytest_code, pytest_out = run(
            [sys.executable, "-m", "pytest", "tests/", "-q", "-p", "no:cacheprovider"], case_dir
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
