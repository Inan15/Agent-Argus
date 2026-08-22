"""READ-ONLY characterisation of the 1,032 vacuous_test_heuristic findings (v2).

v2 corrections over v1:
  * decorator_list EXCLUDED from traversal (Python sets FunctionDef.lineno to the
    `def` line, so decorators fall outside the detector's definition span;
    counting @pytest.mark.parametrize as a consumed SUT call inflated bucket C).
  * bucket C split by WHAT consumes the SUT result, which is the question that
    actually matters.

Buckets:
  A   no SUT call at all             -> nothing to corroborate
  B   SUT result discarded only      -> the shape fact (b) CAN corroborate
  C1  SUT result reaches an ASSERTION -> fact (b) can never corroborate;
        C1-weak   constrained only by a unary tolerance check  -> DEFECT, invisible
        C1-strong constrained by an equality/containment check -> correct test
  C2  SUT result consumed elsewhere   -> fact (b) can never corroborate

Vocabularies imported from the shipped frozen tables, so bucketing uses the
detector's own notion of "assertion callee" and "mock callee".

Writes nothing. Produces no finding, verdict, disposition or adjudication set.
Reads every file from its PINNED git object; no working tree is touched.
"""
import ast
import json
import subprocess
import sys
from collections import Counter

sys.path.insert(0, "d:/ProjectX/XAgents/XAgents/ArgusAgent")
from argus.detectors.vacuous_test import (  # noqa: E402
    _CORROBORATION_ASSERTION_CALLEES,
    _MOCK_CALLEES,
)

SET = ("d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/"
       "ArgusAgent/validation-corpus/adjudication-set-13-5.json")

CHECKOUTS = {
    "agent-markovich": "D:/ProjectX/XAgents/XAgents/AgentMarkovich",
    "minions": "D:/ProjectX/XAgents/XAgents/Minions",
    "xagents-webapp": "D:/ProjectX/XAgents/XAgents/XAgents-WebApp",
    "agent-smith": "D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith",
    "ai-body-runtime": "D:/ProjectX/XAgents/XAgents/ai_body_runtime",
}

# Unary tolerance checks: execute the SUT, accept a large class of wrong values.
WEAK_ASSERTIONS = {"assertIsNotNone", "assertIsNone", "assertTrue", "assertFalse",
                   "assertIsInstance", "assertNotIsInstance", "assertRegex"}
# Also count bare `assert x` / `assert x is not None` style (ast.Assert).


def callee_name(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def is_sut(name):
    return (name is not None
            and name not in _CORROBORATION_ASSERTION_CALLEES
            and name not in _MOCK_CALLEES)


def body_nodes(fn):
    """Walk the function BODY only — decorators excluded."""
    out = []
    for stmt in fn.body:
        out.extend(ast.walk(stmt))
    return out


def contains_sut_call(node):
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and is_sut(callee_name(n)):
            return True
    return False


def classify(fn):
    nodes = body_nodes(fn)

    discarded = 0
    bare_ids = set()
    for n in nodes:
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call):
            if is_sut(callee_name(n.value)):
                discarded += 1
                bare_ids.add(id(n.value))

    consumed = [n for n in nodes
                if isinstance(n, ast.Call) and id(n) not in bare_ids
                and is_sut(callee_name(n))]

    # Which names are bound from a SUT call?
    sut_bound = set()
    for n in nodes:
        if isinstance(n, ast.Assign) and contains_sut_call(n.value):
            for t in n.targets:
                for sub in ast.walk(t):
                    if isinstance(sub, ast.Name):
                        sut_bound.add(sub.id)
        if isinstance(n, (ast.AnnAssign, ast.AugAssign)) and n.value is not None:
            if contains_sut_call(n.value):
                for sub in ast.walk(n.target):
                    if isinstance(sub, ast.Name):
                        sut_bound.add(sub.id)

    def refs_sut(node):
        if contains_sut_call(node):
            return True
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and sub.id in sut_bound:
                return True
        return False

    # Assertions that constrain a SUT-derived value
    weak_hit = strong_hit = False
    for n in nodes:
        if isinstance(n, ast.Call):
            nm = callee_name(n)
            if nm in _CORROBORATION_ASSERTION_CALLEES:
                if any(refs_sut(a) for a in n.args):
                    if nm in WEAK_ASSERTIONS:
                        weak_hit = True
                    else:
                        strong_hit = True
        elif isinstance(n, ast.Assert):
            if refs_sut(n.test):
                t = n.test
                if isinstance(t, ast.Compare) and any(
                    isinstance(o, (ast.Eq, ast.In, ast.NotEq, ast.NotIn))
                    for o in t.ops
                ):
                    strong_hit = True
                else:
                    weak_hit = True

    if not consumed:
        return ("B_discarded_only" if discarded else "A_no_sut_call")
    if weak_hit or strong_hit:
        if strong_hit:
            return "C1_strong"
        return "C1_weak"
    return "C2_elsewhere"


def blob(repo, sha, path):
    r = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"],
                       capture_output=True)
    return None if r.returncode != 0 else r.stdout.decode("utf-8", errors="replace")


def main():
    data = json.load(open(SET, encoding="utf-8"))
    buckets, per_member, unresolved = Counter(), {}, 0

    for m in data["members"]:
        mid, repo, sha = m["member_id"], CHECKOUTS[m["member_id"]], m["pinned_sha"]
        pm, cache = Counter(), {}
        for f in m["findings"]:
            if f.get("rule_id") != "vacuous_test_heuristic":
                continue
            path, _, line = f["locators"][0].rpartition(":")
            try:
                line = int(line)
            except ValueError:
                unresolved += 1
                continue
            if path not in cache:
                cache[path] = blob(repo, sha, path)
            if cache[path] is None:
                unresolved += 1
                continue
            try:
                tree = ast.parse(cache[path])
            except SyntaxError:
                unresolved += 1
                continue
            target = None
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and node.lineno == line:
                    target = node
                    break
            if target is None:
                unresolved += 1
                continue
            b = classify(target)
            buckets[b] += 1
            pm[b] += 1
        if pm:
            per_member[mid] = pm

    total = sum(buckets.values())
    order = ["C1_weak", "C1_strong", "C2_elsewhere", "B_discarded_only", "A_no_sut_call"]
    labels = {
        "C1_weak":  "C1-weak   SUT result constrained ONLY by a tolerance check",
        "C1_strong": "C1-strong SUT result constrained by equality/containment",
        "C2_elsewhere": "C2       SUT result consumed, never reaches an assertion",
        "B_discarded_only": "B        SUT result DISCARDED  <- corroborable shape",
        "A_no_sut_call": "A        no SUT call at all",
    }
    print("=" * 74)
    print("VACUOUS_TEST_HEURISTIC POPULATION -- WHY CORROBORATION FAILED  (v2)")
    print("=" * 74)
    print(f"classified: {total}    unresolved: {unresolved}\n")
    for k in order:
        n = buckets[k]
        print(f"{labels[k]:<62}{n:>5} {100.0*n/total:5.1f}%")

    invisible = buckets["C1_weak"] + buckets["C2_elsewhere"]
    print()
    print(f"INVISIBLE-BUT-SUSPECT (C1-weak + C2)      : {invisible:>5} "
          f"({100.0*invisible/total:.1f}%)")
    print(f"CORROBORABLE CEILING  (B)                 : {buckets['B_discarded_only']:>5} "
          f"({100.0*buckets['B_discarded_only']/total:.1f}%)")
    b = buckets["B_discarded_only"]
    print(f"BLINDNESS RATIO       invisible : B       = {invisible}:{b}"
          + (f"  ({invisible/b:.0f}x)" if b else "  (B is ZERO)"))
    print()
    print("per member:")
    for mid, pm in per_member.items():
        print(f"  {mid:18s} n={sum(pm.values()):<5} "
              f"C1w={pm['C1_weak']:<4} C1s={pm['C1_strong']:<4} "
              f"C2={pm['C2_elsewhere']:<4} B={pm['B_discarded_only']:<3} "
              f"A={pm['A_no_sut_call']}")


if __name__ == "__main__":
    main()
