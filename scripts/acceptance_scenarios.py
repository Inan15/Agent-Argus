"""Outcome-based release evidence — N end-to-end runs of the SHIPPED CLI.

Registered in `architecture.md` §Enforcement under *Outcome-scenario enforcement*
(added 2026-08-23). Produces a one-page result sheet a human reads before a
release. It **demotes** the existing gates; it deletes and weakens none of them,
and they keep exactly the blocking power they have today.

**The problem it exists to fix, measured.** "All gates green" is not a release
decision when the gates check paperwork. Classified on 2026-08-23 this project ran
roughly **21 bookkeeping checks to 6 outcome checks** — file sizes, id uniqueness,
placeholder strings, whether documents cite each other. The proof that this is not
theoretical is committed: `_bmad-output/audit-reports/final-verdict.md` reads
`RELEASE_READY` with 0 blocking findings while the protocol §5 precision gate reads
`BLOCKED`. Both figures are true. Neither answers whether a developer who installs
Argus gets something that works.

**What a scenario asserts, and why it is not a golden file.** Each scenario runs the
real CLI as a subprocess and then cross-checks **three independently produced
surfaces** against each other:

  1. the **process exit code** the operating system saw;
  2. the **stdout machine summary** the CLI printed for a scripted consumer;
  3. the **rendered `final-verdict.md`** a human reads.

A scenario passes when all three AGREE. No expected verdict is hardcoded anywhere,
which is deliberate: a suite of pinned expected verdicts degrades into a change
detector that re-asserts whatever the tool currently does, and would have to be
edited every time a detector legitimately improves. Disagreement between the three
surfaces is a defect **in any direction** — the exact class Epic 8 spent five
stories removing from the verdict, checked here at the outermost boundary where a
user actually stands.

**Hermetic.** Every fixture repository is built in a temp directory from bytes in
this file. Nothing reads a ratified corpus member, nothing fetches, nothing writes
into the repository under audit, and no scenario depends on a checkout that may or
may not exist on the machine.

**What it does NOT cover, stated rather than implied.** The published GitHub Action
is exercised only through the flag set `argus-student-audit.yml` passes, not through
a real Actions runner; and the deep pass is exercised only in its
provider-unconfigured degradation, because a scenario that dispatched to a live
model would make release evidence depend on a paid third party. Both are real gaps
and are named here so the sheet is never read as broader than it is.

Usage::

    python scripts/acceptance_scenarios.py                   # print the sheet
    python scripts/acceptance_scenarios.py --out results.md  # write it
    python scripts/acceptance_scenarios.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# The three surfaces, and how each names the same two facts.
_STDOUT_SUMMARY = re.compile(
    r"verdict=(?P<verdict>[A-Z_]+)\s.*?\sblocking_findings=(?P<blocking>\d+)"
)
_REPORT_VERDICT = re.compile(
    r"\*\*Final Verdict\*\*:\s*\*\*`(?P<verdict>[A-Z_]+)`\*\*\s*\(Exit Code `(?P<exit>\d+)`\)"
)
_REPORT_BLOCKING = re.compile(r"\*\*Blocking Findings\*\*:\s*\*\*(?P<blocking>\d+)\*\*")

# ── Fixture sources. Small on purpose: a scenario is about the CLI's contract at
#    its boundary, not about detector recall, which the cartridges already measure.
_PY_CLEAN = '''"""A module with a real function and a real assertion over it."""


def add(left: int, right: int) -> int:
    return left + right
'''

_PY_TEST = '''from src.calc import add


def test_add_returns_the_sum() -> None:
    assert add(2, 3) == 5
'''

_JS_CLEAN = """export function add(left, right) {
  return left + right;
}
"""

_TS_CLEAN = """export function greet(name: string): string {
  return `hello ${name}`;
}
"""

_UNPARSEABLE = """def broken(:
    this is not valid python at all ][
"""


@dataclass
class Scenario:
    """One end-to-end run: what is built, what is invoked, what is checked."""

    key: str
    what_a_user_is_doing: str
    files: dict[str, str]
    args: list[str] = field(default_factory=list)
    covers: str = ""


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        key="python-only",
        what_a_user_is_doing="Audits a small pure-Python project with no flags at all — the first-run path.",
        files={"src/calc.py": _PY_CLEAN, "tests/test_calc.py": _PY_TEST},
        covers="default invocation - the configuration most first-time users hit",
    ),
    Scenario(
        key="polyglot-with-grammars",
        what_a_user_is_doing="Audits a Python + JavaScript + TypeScript project with the grammars installed.",
        files={
            "src/calc.py": _PY_CLEAN,
            "src/calc.js": _JS_CLEAN,
            "src/greet.ts": _TS_CLEAN,
            "tests/test_calc.py": _PY_TEST,
        },
        covers="the multi-language claim the installer's [languages] extra sells",
    ),
    Scenario(
        key="unparseable-source-degrades",
        what_a_user_is_doing="Audits a project containing a file the parser cannot read.",
        files={
            "src/calc.py": _PY_CLEAN,
            "src/broken.py": _UNPARSEABLE,
            "tests/test_calc.py": _PY_TEST,
        },
        covers="honest degradation - an unreadable file must never count as deeply audited",
    ),
    Scenario(
        key="deep-audit-no-provider",
        what_a_user_is_doing="Passes --deep-audit with no model provider configured.",
        files={"src/calc.py": _PY_CLEAN, "tests/test_calc.py": _PY_TEST},
        args=["--deep-audit"],
        covers="opt-in deep pass degrading rather than silently claiming deep coverage",
    ),
    Scenario(
        key="scope-application",
        what_a_user_is_doing="Restricts assessment to application code, holding tests out.",
        files={"src/calc.py": _PY_CLEAN, "tests/test_calc.py": _PY_TEST},
        args=["--coverage-scope", "application"],
        covers="the scope split - held-out files must be disclosed, never silently dropped",
    ),
    Scenario(
        key="action-flag-set",
        what_a_user_is_doing="Runs the exact flag set the published GitHub Action passes.",
        files={"src/calc.py": _PY_CLEAN, "tests/test_calc.py": _PY_TEST},
        args=[
            "--reports",
            "final-verdict,coverage-ledger,security-review,architecture-review",
            "--coverage-scope",
            "application",
        ],
        covers="argus-student-audit.yml - the published consumer path",
    ),
)


def _build(scenario: Scenario, root: Path) -> Path:
    """Materialize the fixture repository. Returns the directory to audit."""
    target = root / scenario.key
    for rel, body in scenario.files.items():
        path = target / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return target


def run_scenario(scenario: Scenario, root: Path) -> dict:
    """Run one scenario and cross-check its three surfaces. Never raises."""
    target = _build(scenario, root)
    reports = root / f"{scenario.key}-reports"
    argv = [
        sys.executable, "-m", "argus.cli", "audit", str(target),
        "--report-dir", str(reports),
    ]
    if "--reports" not in scenario.args:
        argv += ["--reports", "final-verdict"]
    argv += scenario.args

    try:
        proc = subprocess.run(argv, capture_output=True, timeout=600, cwd=str(REPO))
    except Exception as exc:  # noqa: BLE001 - a crash is a RESULT, not an abort
        return {
            "key": scenario.key, "agree": False, "unevaluable": True,
            "why": f"the CLI could not be invoked: {type(exc).__name__}",
        }

    stdout = proc.stdout.decode("utf-8", "replace")
    stderr = proc.stderr.decode("utf-8", "replace")
    combined = stdout + "\n" + stderr

    summary = _STDOUT_SUMMARY.search(combined)
    report_path = reports / "final-verdict.md"
    report = report_path.read_text(encoding="utf-8", errors="replace") if report_path.exists() else ""
    rv = _REPORT_VERDICT.search(report)
    rb = _REPORT_BLOCKING.search(report)

    # A surface that could not be OBSERVED is UNEVALUABLE, never silently "agrees".
    # Printing ok for a check that never ran is the exact defect class this
    # repository removed from the verdict; it is not reintroduced here.
    missing = [
        name for name, found in (
            ("stdout machine summary", summary),
            ("report verdict line", rv),
            ("report blocking line", rb),
        ) if found is None
    ]
    if missing:
        return {
            "key": scenario.key, "agree": False, "unevaluable": True,
            "exit_code": proc.returncode,
            "why": "could not observe: " + ", ".join(missing),
        }

    checks = {
        "exit code matches the report's stated exit code":
            proc.returncode == int(rv.group("exit")),
        "stdout verdict matches the report verdict":
            summary.group("verdict") == rv.group("verdict"),
        "stdout blocking count matches the report blocking count":
            summary.group("blocking") == rb.group("blocking"),
    }
    return {
        "key": scenario.key,
        "agree": all(checks.values()),
        "unevaluable": False,
        "exit_code": proc.returncode,
        "verdict": rv.group("verdict"),
        "blocking": int(rb.group("blocking")),
        "checks": checks,
        "why": "" if all(checks.values())
               else "; ".join(k for k, v in checks.items() if not v) + " — DISAGREE",
    }


def render(results: list[dict], sha: str) -> str:
    """The one page a human reads before deciding to release."""
    agreed = sum(1 for r in results if r["agree"])
    uneval = sum(1 for r in results if r.get("unevaluable"))
    lines = [
        "# Acceptance scenario results",
        "",
        f"Measured at `{sha}` by `scripts/acceptance_scenarios.py`.",
        "",
        f"**{agreed} of {len(results)} scenarios agree across all three surfaces"
        + (f"; {uneval} unevaluable" if uneval else "") + ".**",
        "",
        "Each scenario runs the shipped CLI end to end and checks that the process",
        "exit code, the stdout machine summary and the rendered `final-verdict.md`",
        "all describe the same outcome. No expected verdict is hardcoded, so a",
        "legitimate detector improvement does not make this sheet red — only a",
        "disagreement between what the tool did and what it said it did.",
        "",
        "| scenario | what a user is doing | verdict | exit | blocking | agree |",
        "|---|---|---|---:|---:|---|",
    ]
    for r in results:
        mark = "UNEVALUABLE" if r.get("unevaluable") else ("yes" if r["agree"] else "**NO**")
        lines.append(
            f"| `{r['key']}` | {next(s.what_a_user_is_doing for s in SCENARIOS if s.key == r['key'])} "
            f"| {r.get('verdict', '—')} | {r.get('exit_code', '—')} "
            f"| {r.get('blocking', '—')} | {mark} |"
        )
    lines += ["", "## Coverage, and what it excludes", ""]
    for s in SCENARIOS:
        lines.append(f"- `{s.key}` — {s.covers}")
    lines += [
        "",
        "**Not covered.** The published Action is exercised through its flag set, not",
        "through a real Actions runner. The deep pass is exercised only in its",
        "provider-unconfigured degradation, because release evidence must not depend",
        "on a paid third party. Both gaps are real and are named so this page is never",
        "read as broader than it is.",
        "",
        "The existing gates are unchanged and still block. This page is the release",
        "decision they inform; it does not replace one of them.",
        "",
    ]
    for r in results:
        if r["why"]:
            lines.append(f"- `{r['key']}`: {r['why']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run the acceptance scenarios.")
    ap.add_argument("--out", type=Path, default=None, help="write the sheet here")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    sha = subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True
    ).stdout.decode("utf-8", "replace").strip() or "unknown"

    root = Path(tempfile.mkdtemp(prefix="argus-acceptance-"))
    try:
        results = [run_scenario(s, root) for s in SCENARIOS]
    finally:
        shutil.rmtree(root, ignore_errors=True)

    if args.json:
        print(json.dumps({"sha": sha, "results": results}, indent=2))
    else:
        sheet = render(results, sha)
        if args.out:
            args.out.write_text(sheet + "\n", encoding="utf-8")
            print(f"wrote {args.out}")
        else:
            print(sheet)

    # Non-zero when a scenario DISAGREES with itself — this is a real outcome
    # signal, not a prose judgement, so unlike check_meta_drift.py it is allowed
    # to be actionable. It is still not wired into CI as a blocking step until
    # its population has been adjudicated.
    return 0 if all(r["agree"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
