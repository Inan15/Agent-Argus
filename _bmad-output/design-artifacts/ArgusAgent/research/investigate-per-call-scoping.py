"""PER-CALL SCOPING INVESTIGATION for fact (b).

Question: the shipped clause `consumed == 0` is evaluated over the WHOLE test
function, so one observed call anywhere withholds corroboration from the entire
test. What does a per-call formulation reach, and at what accusation risk?

Variants measured, all over the SAME shipped provenance_evidence() evidence:

  V0  shipped   disc>=1 AND cons==0 AND mref>=1          (known: 0)
  V1  drop-mref disc>=1 AND cons==0                      (known: 6)
  V2  silent    disc>=1 AND the span asserts NOTHING AT ALL
  V3  strict    V1 AND the span asserts nothing at all
  V4  per-call  disc>=1 alone                            (upper bound, too loose)
  V5  unrelated disc>=1 AND span HAS assertions AND no assertion references a
                name bound from a SUT call  ("asserts, but not about the SUT")

V2/V3 use the WIDE assertion vocabulary (`is_assertion_callee`, table + naming
convention) plus bare `assert`. Using the FROZEN corroboration table here would
manufacture false accusations -- DN-14-2-1 warns about exactly this, because a
test asserting through a widened callee would look assertion-free.

V5 additionally needs SUT-derived name binding, which no shipped helper provides;
it is computed with Python `ast` and is therefore THIS SCRIPT'S OWN reasoning,
not the shipped predicate. Flagged as such in the output.

Reads pinned blobs into a scratch tree. Writes nothing else.
"""
import ast
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

ROOT = "d:/ProjectX/XAgents/XAgents/ArgusAgent"
sys.path.insert(0, ROOT)
os.environ.setdefault("ARGUS_REQUIRE_LANGUAGE_GRAMMARS", "1")

from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.detectors.provenance_scan import (  # noqa: E402
    provenance_evidence,
    opens_bare_assert,
)
from argus.detectors.vacuous_test import (  # noqa: E402
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
    index_aligned_lines,
    is_assertion_callee,
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


def blob(repo, sha, path):
    r = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"],
                       capture_output=True)
    return None if r.returncode != 0 else r.stdout


def asserts_anything(source_lines, span_edges, start, end):
    """WIDE vocabulary: does this span assert anything at all? (breadth wanted)"""
    for line_no in range(start, end + 1):
        i = line_no - 1
        if 0 <= i < len(source_lines) and opens_bare_assert(source_lines[i].strip()):
            return True
    return any(is_assertion_callee(e.callee) for e in span_edges)


def sut_unrelated_assertions(fn):
    """V5: span has assertions, none referencing a SUT-derived name. AST-based.

    THIS SCRIPT'S OWN reasoning -- no shipped helper computes it.
    """
    body = []
    for stmt in fn.body:
        body.extend(ast.walk(stmt))

    def callee(n):
        f = n.func
        if isinstance(f, ast.Name):
            return f.id
        if isinstance(f, ast.Attribute):
            return f.attr
        return None

    def is_sut(name):
        return (name is not None
                and name not in _CORROBORATION_ASSERTION_CALLEES
                and name not in _MOCK_CALLEES)

    sut_bound = set()
    for n in body:
        tgt, val = None, None
        if isinstance(n, ast.Assign):
            tgt, val = n.targets, n.value
        elif isinstance(n, (ast.AnnAssign, ast.AugAssign)) and n.value is not None:
            tgt, val = [n.target], n.value
        if val is None:
            continue
        if any(isinstance(x, ast.Call) and is_sut(callee(x)) for x in ast.walk(val)):
            for t in tgt:
                for sub in ast.walk(t):
                    if isinstance(sub, ast.Name):
                        sut_bound.add(sub.id)

    def touches_sut(node):
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and is_sut(callee(sub)):
                return True
            if isinstance(sub, ast.Name) and sub.id in sut_bound:
                return True
        return False

    n_assert = 0
    n_sut_assert = 0
    for n in body:
        if isinstance(n, ast.Assert):
            n_assert += 1
            if touches_sut(n.test):
                n_sut_assert += 1
        elif isinstance(n, ast.Call) and is_assertion_callee(callee(n) or ""):
            n_assert += 1
            if any(touches_sut(a) for a in n.args):
                n_sut_assert += 1
    return n_assert, n_sut_assert


def main():
    data = json.load(open(SET, encoding="utf-8"))
    t = Counter()
    per_member = Counter()
    skipped = 0

    for m in data["members"]:
        mid, sha = m["member_id"], m["pinned_sha"]
        repo = CHECKOUTS[mid]
        wanted = {}
        for f in m["findings"]:
            if f.get("rule_id") != "vacuous_test_heuristic":
                continue
            p, _, ln = f["locators"][0].rpartition(":")
            wanted.setdefault(p, []).append(int(ln))
        if not wanted:
            continue

        tmp = tempfile.mkdtemp(prefix=f"argus-percall-{mid}-")
        mat = []
        for p in wanted:
            c = blob(repo, sha, p)
            if c is None:
                skipped += len(wanted[p])
                continue
            d = Path(tmp) / p
            d.parent.mkdir(parents=True, exist_ok=True)
            d.write_bytes(c)
            mat.append(p)
        if not mat:
            continue
        index = build_ast_index(tmp, tuple(sorted(mat)))
        entries = {e.file_path: e for e in index.entries}

        for p in mat:
            entry = entries.get(p)
            if entry is None or entry.parse_failed or not entry.ast_eligible:
                skipped += len(wanted[p])
                continue
            raw = (Path(tmp) / p).read_bytes().decode("utf-8", errors="replace")
            source_lines = index_aligned_lines(raw)
            try:
                pytree = ast.parse(raw)
            except SyntaxError:
                pytree = None
            pyfns = {}
            if pytree is not None:
                for n in ast.walk(pytree):
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        pyfns[n.lineno] = n
            by_start = {d.start_line: d for d in entry.definitions}

            for line in wanted[p]:
                d = by_start.get(line)
                if d is None:
                    skipped += 1
                    continue
                se = [e for e in entry.edges if d.start_line <= e.line <= d.end_line]
                ev = provenance_evidence(
                    source_lines, se, d.start_line, d.end_line,
                    assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
                    mock_callees=_MOCK_CALLEES,
                )
                disc, cons, mref = (ev.discarded_sut_calls,
                                    ev.consumed_sut_calls,
                                    ev.mock_referencing_assertions)
                silent = not asserts_anything(source_lines, se, d.start_line, d.end_line)

                t["n"] += 1
                t["V0"] += int(disc >= 1 and cons == 0 and mref >= 1)
                t["V1"] += int(disc >= 1 and cons == 0)
                t["V2"] += int(disc >= 1 and silent)
                t["V3"] += int(disc >= 1 and cons == 0 and silent)
                t["V4"] += int(disc >= 1)
                t["silent_any"] += int(silent)

                fn = pyfns.get(line)
                if fn is not None:
                    na, nsa = sut_unrelated_assertions(fn)
                    if disc >= 1 and na >= 1 and nsa == 0:
                        t["V5"] += 1
                        per_member[f"V5:{mid}"] += 1
                else:
                    t["V5_unavailable"] += 1
                if disc >= 1 and silent:
                    per_member[f"V2:{mid}"] += 1

    n = t["n"]
    print("=" * 74)
    print("PER-CALL SCOPING INVESTIGATION -- reachable population per variant")
    print("=" * 74)
    print(f"evaluated: {n}   skipped: {skipped}   "
          f"V5 unavailable (non-Python fn): {t['V5_unavailable']}\n")
    rows = [
        ("V0 shipped   disc>=1 AND cons==0 AND mref>=1", t["V0"], "known 0"),
        ("V1 drop-mref disc>=1 AND cons==0", t["V1"], "known 6"),
        ("V2 silent    disc>=1 AND span asserts NOTHING", t["V2"], "wide vocab"),
        ("V3 strict    V1 AND span asserts nothing", t["V3"], "subset of V1"),
        ("V5 unrelated disc>=1 AND asserts, none about SUT", t["V5"], "script's own"),
        ("V4 per-call  disc>=1 alone", t["V4"], "UPPER BOUND, too loose"),
    ]
    for label, v, note in rows:
        pct = 100.0 * v / n if n else 0
        print(f"  {label:<50}{v:>5} {pct:5.1f}%   {note}")
    print(f"\n  spans asserting nothing at all (any disc): {t['silent_any']}")
    print("\nper-member for the two live candidates:")
    for k in sorted(per_member):
        print(f"  {k:28s} {per_member[k]}")


if __name__ == "__main__":
    main()
