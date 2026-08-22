"""REVALIDATION of the proposed fact (b) widening, using the SHIPPED predicate.

Runs argus.detectors.provenance_scan.provenance_evidence -- the real function the
detector calls -- over every flagged test function, read from its member's PINNED
git object and materialised into a scratch tree (no checkout is touched).

HARNESS VALIDATION: the full shipped fact (b) must reproduce ZERO promotions over
this population, because the 2026-08-18 run recorded 0 blocking findings. If it
does not reproduce zero, every number this script prints is untrustworthy.

Writes nothing outside the scratch tree.
"""
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
from argus.detectors.provenance_scan import provenance_evidence  # noqa: E402
from argus.detectors.vacuous_test import (  # noqa: E402
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
    index_aligned_lines,
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


def main():
    data = json.load(open(SET, encoding="utf-8"))
    tally = Counter()
    shapes = Counter()
    per_member = {}
    skipped = 0

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

        tmp = tempfile.mkdtemp(prefix=f"argus-reval-{mid}-")
        materialised = []
        for path in wanted:
            content = blob(repo, sha, path)
            if content is None:
                skipped += len(wanted[path])
                continue
            dest = Path(tmp) / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
            materialised.append(path)
        if not materialised:
            continue

        index = build_ast_index(tmp, tuple(sorted(materialised)))
        entries = {e.file_path: e for e in index.entries}

        pm = Counter()
        for path in materialised:
            entry = entries.get(path)
            if entry is None or entry.parse_failed or not entry.ast_eligible:
                skipped += len(wanted[path])
                continue
            src = (Path(tmp) / path).read_bytes().decode("utf-8", errors="replace")
            source_lines = index_aligned_lines(src)
            by_start = {d.start_line: d for d in entry.definitions}
            for line in wanted[path]:
                d = by_start.get(line)
                if d is None:
                    skipped += 1
                    continue
                span_edges = [e for e in entry.edges
                              if d.start_line <= e.line <= d.end_line]
                ev = provenance_evidence(
                    source_lines, span_edges, d.start_line, d.end_line,
                    assertion_callees=_CORROBORATION_ASSERTION_CALLEES,
                    mock_callees=_MOCK_CALLEES,
                )
                disc = ev.discarded_sut_calls
                cons = ev.consumed_sut_calls
                mref = ev.mock_referencing_assertions

                shipped = ev.sut_result_is_discarded and mref >= 1
                w1 = ev.sut_result_is_discarded          # drop the mock clause
                tally["n"] += 1
                tally["shipped_fact_b"] += int(shipped)
                tally["W1_discarded_no_mock_clause"] += int(w1)
                tally["consumed_zero"] += int(cons == 0)
                tally["discarded_ge1"] += int(disc >= 1)
                tally["mock_ref_ge1"] += int(mref >= 1)
                tally["no_sut_call_at_all"] += int(disc == 0 and cons == 0)
                shapes[(min(disc, 3), min(cons, 3), min(mref, 3))] += 1
                pm["n"] += 1
                pm["W1"] += int(w1)
                pm["shipped"] += int(shipped)
        per_member[mid] = pm

    n = tally["n"]
    print("=" * 72)
    print("REVALIDATION -- shipped provenance_evidence() over the flagged population")
    print("=" * 72)
    print(f"evaluated: {n}    skipped (unresolvable): {skipped}\n")
    print("HARNESS VALIDATION")
    print(f"  shipped fact (b) promotions          : {tally['shipped_fact_b']}"
          f"   <- MUST be 0 (run recorded 0 blocking)")
    ok = tally["shipped_fact_b"] == 0
    print(f"  harness trustworthy                  : {'YES' if ok else 'NO -- STOP'}\n")
    print("CLAUSE-BY-CLAUSE")
    print(f"  no SUT call at all (disc=0, cons=0)  : {tally['no_sut_call_at_all']:>5}")
    print(f"  at least one DISCARDED SUT call      : {tally['discarded_ge1']:>5}")
    print(f"  ZERO consumed SUT calls              : {tally['consumed_zero']:>5}")
    print(f"  at least one mock-referencing assert : {tally['mock_ref_ge1']:>5}")
    print()
    print("CANDIDATE WIDENING")
    print(f"  W1 = discarded>=1 AND consumed==0    : "
          f"{tally['W1_discarded_no_mock_clause']:>5}   (drops the mock-ref clause)")
    print(f"  shipped (W1 AND mock_ref>=1)         : {tally['shipped_fact_b']:>5}")
    delta = tally["W1_discarded_no_mock_clause"] - tally["shipped_fact_b"]
    print(f"  findings the mock-ref clause BLOCKS  : {delta:>5}")
    print()
    print("top (discarded, consumed, mock_ref) shapes, capped at 3:")
    for k, v in shapes.most_common(8):
        print(f"  disc={k[0]} cons={k[1]} mref={k[2]} -> {v}")
    print()
    print("per member:")
    for mid, pm in per_member.items():
        print(f"  {mid:18s} n={pm['n']:<5} W1={pm['W1']:<4} shipped={pm['shipped']}")


if __name__ == "__main__":
    main()
