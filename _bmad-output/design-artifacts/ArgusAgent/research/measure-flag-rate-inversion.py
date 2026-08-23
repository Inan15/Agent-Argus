"""Does the heuristic SELECT AWAY from the very tests fact (b) is written to judge?

Hypothesis: `assert_called_once_with(...)` counts toward assertion_density (the WIDE
vocabulary), so a mock-heavy test has HIGH density and is never flagged; meanwhile the
mock arm needs mock CONSTRUCTION calls > half of ALL calls, which almost never happens.
If so, the population fact (b) can judge and the population the heuristic selects are
close to disjoint -- by construction, not by tuning.

Scored over the LIVE checkouts at HEAD (not the pinned shas): this is a structural
question about the instrument, not a corpus measurement, and HEAD is the larger sample.
"""
import ast
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
    VacuousTestDetector, index_aligned_lines, is_test_file,
    ASSERTION_DENSITY_FLOOR, MOCK_RATIO_CEILING,
)

CHECKOUTS = {
    "agent-markovich": "D:/ProjectX/XAgents/XAgents/AgentMarkovich",
    "minions": "D:/ProjectX/XAgents/XAgents/Minions",
    "agent-smith": "D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith",
}
MOCK_RE = re.compile(r"(MagicMock|AsyncMock|Mock\(|mock\.patch|@patch|patch\(|mocker\b"
                     r"|create_autospec)")
MOCK_PRIMS = {"Mock", "MagicMock", "AsyncMock", "patch", "create_autospec", "mock_open",
              "NonCallableMock", "PropertyMock"}


def binds_mock(fn_node):
    """Does this test function use a mock, by ANY idiom (decorator, param, local, self)?"""
    for d in fn_node.decorator_list:
        f = d.func if isinstance(d, ast.Call) else d
        nm = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
        if nm and "patch" in nm:
            return True
    for a in fn_node.args.args:
        low = a.arg.lower()
        if a.arg == "mocker" or "mock" in low or low.startswith(("fake", "stub")):
            return True
    for n in ast.walk(fn_node):
        if isinstance(n, ast.Name) and n.id in MOCK_PRIMS:
            return True
        if isinstance(n, ast.Attribute) and n.attr in MOCK_PRIMS:
            return True
    return False


def main():
    det = VacuousTestDetector()
    tally = Counter()
    dens = {"mock": [], "nomock": []}
    for mid, repo in CHECKOUTS.items():
        r = subprocess.run(["git", "-C", repo, "ls-files"], capture_output=True,
                           text=True, errors="replace")
        cands = []
        for f in r.stdout.splitlines():
            if not f.endswith(".py") or not is_test_file(f):
                continue
            try:
                t = (Path(repo) / f).read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if MOCK_RE.search(t):
                cands.append(f)
        if not cands:
            continue
        # materialise into a scratch tree so build_ast_index sees only test files
        tmp = tempfile.mkdtemp(prefix=f"argus-inv-{mid}-")
        got = []
        for f in cands:
            try:
                data = (Path(repo) / f).read_bytes()
            except OSError:
                continue
            dest = Path(tmp) / f
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            got.append(f)
        index = build_ast_index(tmp, tuple(sorted(got)))
        entries = {e.file_path: e for e in index.entries}
        for f in got:
            e = entries.get(f)
            if e is None or e.parse_failed or not e.ast_eligible:
                continue
            raw = (Path(tmp) / f).read_bytes().decode("utf-8", errors="replace")
            lines = index_aligned_lines(raw)
            try:
                tree = ast.parse(raw)
            except SyntaxError:
                continue
            fns = {}
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    fns[node.lineno] = node
                    for d in node.decorator_list:
                        fns.setdefault(d.lineno, node)
            for d in e.definitions:
                if d.kind != "function" or not d.name.startswith("test"):
                    continue
                node = fns.get(d.start_line)
                if node is None:
                    cand = [v for k, v in fns.items()
                            if k <= d.start_line <= (v.end_lineno or k)]
                    node = cand[0] if cand else None
                if node is None:
                    continue
                s = det._score(lines, e.edges, d)
                key = "mock" if binds_mock(node) else "nomock"
                tally[f"{key}_total"] += 1
                tally[f"{key}_flagged"] += int(s.heuristically_vacuous)
                tally[f"{key}_corroborated"] += int(s.ast_corroborated)
                if s.statement_count:
                    dens[key].append(float(s.assertion_density))

    print("=" * 74)
    print("INVERSION CHECK -- flag rate among mock-USING vs mock-FREE test functions")
    print("=" * 74)
    print("  (mock-using test FILES only, live checkouts at HEAD)\n")
    for key, label in (("mock", "test BINDS a mock"), ("nomock", "test binds NO mock")):
        tot = tally[f"{key}_total"]
        fl = tally[f"{key}_flagged"]
        co = tally[f"{key}_corroborated"]
        d = dens[key]
        mean = sum(d) / len(d) if d else 0.0
        below = sum(1 for x in d if x < 0.25)
        print(f"  {label:22s} n={tot:<6} flagged={fl:<5} ({100.0*fl/tot if tot else 0:5.1f}%)"
              f"  corroborated={co}")
        print(f"  {'':22s} mean assertion_density={mean:.3f}   "
              f"below the 1/4 floor: {below}/{len(d)}")
    print()
    print(f"  density floor={ASSERTION_DENSITY_FLOOR}  mock ceiling={MOCK_RATIO_CEILING}")
    print(f"  TOTAL corroborated anywhere in this sample: "
          f"{tally['mock_corroborated'] + tally['nomock_corroborated']}")


if __name__ == "__main__":
    main()
