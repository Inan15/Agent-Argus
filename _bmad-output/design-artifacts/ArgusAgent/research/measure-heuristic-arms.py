"""Which heuristic ARM selects the 1,032? And do these repos mock at all (control)?

Part 1 uses argus's OWN scorer (VacuousTestDetector._score) over the pinned blobs.
Part 2 is a repo-wide control over the live checkouts: if the corpus barely mocks
anywhere, then "the mock clause is dead" is a statement about the CORPUS, not the
resolver -- and that is a different defect with a different fix.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = "d:/ProjectX/XAgents/XAgents/ArgusAgent"
sys.path.insert(0, ROOT)
os.environ.setdefault("ARGUS_REQUIRE_LANGUAGE_GRAMMARS", "1")

from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.detectors.vacuous_test import (  # noqa: E402
    VacuousTestDetector, index_aligned_lines,
    ASSERTION_DENSITY_FLOOR, MOCK_RATIO_CEILING,
)

SET = (f"{ROOT}/_bmad-output/design-artifacts/ArgusAgent/validation-corpus/"
       "adjudication-set-13-5.json")
CHECKOUTS = {
    "agent-markovich": "D:/ProjectX/XAgents/XAgents/AgentMarkovich",
    "minions": "D:/ProjectX/XAgents/XAgents/Minions",
    "xagents-webapp": "D:/ProjectX/XAgents/XAgents/XAgents-WebApp",
    "agent-smith": "D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith",
    "ai-body-runtime": "D:/ProjectX/XAgents/XAgents/ai_body_runtime",
}
MOCK_RE = re.compile(r"\b(MagicMock|AsyncMock|Mock\(|mock\.patch|@patch|patch\(|mocker\b"
                     r"|create_autospec|monkeypatch)\b")


def blob(repo, sha, path):
    r = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"], capture_output=True)
    return None if r.returncode != 0 else r.stdout


def part1():
    data = json.load(open(SET, encoding="utf-8"))
    det = VacuousTestDetector()
    arms, dens_buckets = Counter(), Counter()
    stmt_tot = assert_tot = 0
    n = 0
    for m in data["members"]:
        mid, sha = m["member_id"], m["pinned_sha"]
        repo = CHECKOUTS[mid]
        wanted = {}
        for f in m["findings"]:
            if f.get("rule_id") != "vacuous_test_heuristic":
                continue
            path, _, line = f["locators"][0].rpartition(":")
            wanted.setdefault(path, []).append(int(line))
        if not wanted:
            continue
        tmp = tempfile.mkdtemp(prefix=f"argus-arms-{mid}-")
        got = []
        for path in wanted:
            c = blob(repo, sha, path)
            if c is None:
                continue
            dest = Path(tmp) / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(c)
            got.append(path)
        if not got:
            continue
        index = build_ast_index(tmp, tuple(sorted(got)))
        entries = {e.file_path: e for e in index.entries}
        for path in got:
            e = entries.get(path)
            if e is None or e.parse_failed or not e.ast_eligible:
                continue
            src = (Path(tmp) / path).read_bytes().decode("utf-8", errors="replace")
            lines = index_aligned_lines(src)
            by_start = {d.start_line: d for d in e.definitions}
            for line in wanted[path]:
                d = by_start.get(line)
                if d is None:
                    continue
                s = det._score(lines, e.edges, d)
                if not s.heuristically_vacuous:
                    continue
                n += 1
                lo = s.assertion_density < ASSERTION_DENSITY_FLOOR
                hi = s.mock_ratio > MOCK_RATIO_CEILING
                arms["density_only" if (lo and not hi) else
                     "mock_only" if (hi and not lo) else "both"] += 1
                stmt_tot += s.statement_count
                assert_tot += s.assertion_sites
                dens_buckets[
                    "0 assertions" if s.assertion_sites == 0 else
                    "1 assertion" if s.assertion_sites == 1 else
                    "2+ assertions"] += 1
    print("=" * 74)
    print("PART 1 -- which heuristic ARM selects the flagged population?")
    print("=" * 74)
    print(f"  scored as heuristically vacuous: {n}")
    print(f"  density floor = {ASSERTION_DENSITY_FLOOR}   mock ceiling = {MOCK_RATIO_CEILING}")
    for k in ("density_only", "mock_only", "both"):
        v = arms[k]
        print(f"  {k:14s} {v:>5}  ({100.0*v/n if n else 0:5.1f}%)")
    print(f"\n  assertion count within the flagged population:")
    for k, v in sorted(dens_buckets.items()):
        print(f"    {k:16s} {v:>5}  ({100.0*v/n if n else 0:5.1f}%)")
    print(f"\n  totals: {assert_tot} assertion sites over {stmt_tot} statements")


def part2():
    print()
    print("=" * 74)
    print("PART 2 -- CONTROL: do the corpus members use mocks anywhere at all?")
    print("=" * 74)
    for mid, repo in CHECKOUTS.items():
        r = subprocess.run(["git", "-C", repo, "ls-files"], capture_output=True, text=True,
                           errors="replace")
        files = [f for f in r.stdout.splitlines()
                 if f.endswith(".py") and ("test" in Path(f).name.lower()
                                           or "/tests/" in f or f.startswith("tests/"))]
        withmock = 0
        for f in files:
            p = Path(repo) / f
            try:
                t = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if MOCK_RE.search(t):
                withmock += 1
        pct = 100.0 * withmock / len(files) if files else 0
        print(f"  {mid:18s} test files={len(files):<5} using mocks={withmock:<5} ({pct:5.1f}%)")


if __name__ == "__main__":
    part1()
    part2()
