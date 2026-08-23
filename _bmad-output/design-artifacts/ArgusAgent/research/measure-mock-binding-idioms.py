"""INDEPENDENT probe: why does `mock_referencing_assertions >= 1` fire 0 times in 1,032?

Uses CPython's own `ast` module -- NOT argus's tree-sitter index -- so this is a
second instrument, not a re-read of the first. Materialises the same pinned blobs
as research/revalidate-fact-b-widening.py. Writes nothing outside a scratch tree.

For each flagged test function it asks two questions:
  1. HOW are mocks bound in this test?  (which idiom)
  2. Would an assertion reference a mock-bound name IF the resolver understood
     that idiom?
"""
import json
import os
import subprocess
import sys
import ast
import tempfile
from collections import Counter
from pathlib import Path

ROOT = "d:/ProjectX/XAgents/XAgents/ArgusAgent"
SET = (f"{ROOT}/_bmad-output/design-artifacts/ArgusAgent/validation-corpus/"
       "adjudication-set-13-5.json")
CHECKOUTS = {
    "agent-markovich": "D:/ProjectX/XAgents/XAgents/AgentMarkovich",
    "minions": "D:/ProjectX/XAgents/XAgents/Minions",
    "xagents-webapp": "D:/ProjectX/XAgents/XAgents/XAgents-WebApp",
    "agent-smith": "D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith",
    "ai-body-runtime": "D:/ProjectX/XAgents/XAgents/ai_body_runtime",
}

MOCK_PRIMS = {"Mock", "MagicMock", "AsyncMock", "NonCallableMock", "PropertyMock",
              "patch", "create_autospec", "mock_open", "sentinel", "seal"}
ASSERT_PREFIXES = ("assert", "_assert")


def blob(repo, sha, path):
    r = subprocess.run(["git", "-C", repo, "show", f"{sha}:{path}"], capture_output=True)
    return None if r.returncode != 0 else r.stdout


def chain_root(node):
    while isinstance(node, (ast.Attribute, ast.Call, ast.Subscript, ast.Await)):
        node = node.func if isinstance(node, ast.Call) else (
            node.value if isinstance(node, (ast.Attribute, ast.Subscript)) else node.value)
    return node.id if isinstance(node, ast.Name) else None


def expr_names(node):
    """Every Name id and every `self.<attr>` spelling referenced in the subtree."""
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name):
            out.add(f"{n.value.id}.{n.attr}")
    return out


def is_mock_expr(node, known):
    """Does this expression plausibly produce a mock?"""
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id in MOCK_PRIMS:
            return True
        if isinstance(n, ast.Attribute) and n.attr in MOCK_PRIMS:
            return True
    r = chain_root(node)
    return r in known if r else False


def decorator_patch_count(fn):
    n = 0
    for d in fn.decorator_list:
        f = d.func if isinstance(d, ast.Call) else d
        name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
        if name == "patch" or (name or "").startswith("patch"):
            n += 1
    return n


def is_assert_call(node):
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
    return bool(name) and (name.startswith(ASSERT_PREFIXES) or name in
                           {"raises", "warns", "deprecated_call", "fail"})


def analyse(fn, cls):
    """Return (idiom_set, shipped_visible_names, extended_names, assert_nodes)."""
    idioms = set()
    shipped, extended = set(), set()

    # --- idiom A: in-span local assignment from a mock primitive (THE ONLY ONE SHIPPED)
    for n in ast.walk(fn):
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            val = n.value
            if val is None:
                continue
            targets = n.targets if isinstance(n, ast.Assign) else [n.target]
            if is_mock_expr(val, shipped | extended):
                for t in targets:
                    if isinstance(t, ast.Name):
                        shipped.add(t.id)
                        extended.add(t.id)
                        idioms.add("A_local_assign")
                    elif isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name):
                        extended.add(f"{t.value.id}.{t.attr}")
                        idioms.add("D_self_attr_in_test")
        elif isinstance(n, (ast.With, ast.AsyncWith)):
            for item in n.items:
                if item.optional_vars is not None and is_mock_expr(item.context_expr,
                                                                  shipped | extended):
                    for t in ast.walk(item.optional_vars):
                        if isinstance(t, ast.Name):
                            shipped.add(t.id)
                            extended.add(t.id)
                            idioms.add("A_with_as")

    # --- idiom B: @patch decorator injection -> trailing params carry the mocks
    npatch = decorator_patch_count(fn)
    params = [a.arg for a in fn.args.args if a.arg != "self"]
    if npatch:
        idioms.add("B_patch_decorator")
        for p in params[:npatch] if not params else params[-npatch:]:
            extended.add(p)

    # --- idiom C: fixture / mocker injection via parameters
    for p in params:
        low = p.lower()
        if p == "mocker" or "mock" in low or low.startswith("fake") or low.startswith("stub"):
            extended.add(p)
            idioms.add("C_fixture_param")

    # names bound from `mocker.patch(...)`
    if "mocker" in params:
        for n in ast.walk(fn):
            if isinstance(n, ast.Assign) and chain_root(n.value) == "mocker":
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        extended.add(t.id)

    # --- idiom E: self.<attr> = Mock() bound in the enclosing class (setUp etc.)
    if cls is not None:
        seen = set()
        for meth in cls.body:
            if not isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if meth is fn:
                continue
            for n in ast.walk(meth):
                if isinstance(n, ast.Assign) and is_mock_expr(n.value, seen):
                    for t in n.targets:
                        if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) \
                                and t.value.id == "self":
                            nm = f"self.{t.attr}"
                            seen.add(nm)
                            extended.add(nm)
                            idioms.add("E_setup_self_attr")
    if not idioms:
        idioms.add("Z_no_mock_binding_found")
    return idioms, shipped, extended


def assertion_refs(fn):
    """Names referenced by the test's assertion statements."""
    refs = set()
    found = False
    for n in ast.walk(fn):
        if isinstance(n, ast.Assert):
            found = True
            refs |= expr_names(n)
        elif isinstance(n, ast.Expr) and is_assert_call(n.value):
            found = True
            refs |= expr_names(n.value)
        elif isinstance(n, ast.Call) and is_assert_call(n):
            refs |= expr_names(n)
    return refs, found


def main():
    data = json.load(open(SET, encoding="utf-8"))
    idiom_tally, per_member = Counter(), {}
    tot = shipped_hit = extended_hit = no_assert = 0
    unmatched = 0
    examples = []

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
        pm = Counter()
        tmp = tempfile.mkdtemp(prefix=f"argus-idiom-{mid}-")
        for path, lines in wanted.items():
            content = blob(repo, sha, path)
            if content is None:
                unmatched += len(lines)
                continue
            src = content.decode("utf-8", errors="replace")
            try:
                tree = ast.parse(src)
            except SyntaxError:
                unmatched += len(lines)
                continue
            # map every function to (node, enclosing class)
            fns = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for b in node.body:
                        if isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            fns[b.lineno] = (b, node)
                            for d in b.decorator_list:
                                fns[d.lineno] = (b, node)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    fns.setdefault(node.lineno, (node, None))
                    for d in node.decorator_list:
                        fns.setdefault(d.lineno, (node, None))
            for line in lines:
                hit = fns.get(line)
                if hit is None:
                    cands = [v for k, v in fns.items() if k <= line <= v[0].end_lineno]
                    hit = cands[0] if cands else None
                if hit is None:
                    unmatched += 1
                    continue
                fn, cls = hit
                idioms, shipped_names, ext_names = analyse(fn, cls)
                refs, has_assert = assertion_refs(fn)
                tot += 1
                pm["n"] += 1
                for i in idioms:
                    idiom_tally[i] += 1
                if not has_assert:
                    no_assert += 1
                s_hit = bool(refs & shipped_names)
                e_hit = bool(refs & ext_names)
                shipped_hit += int(s_hit)
                extended_hit += int(e_hit)
                pm["ext"] += int(e_hit)
                if e_hit and not s_hit and len(examples) < 6:
                    examples.append((mid, path, line, sorted(idioms),
                                     sorted(refs & ext_names)[:3]))
        per_member[mid] = pm

    print("=" * 74)
    print("INDEPENDENT PROBE (CPython ast) -- how are mocks bound in the flagged tests?")
    print("=" * 74)
    print(f"flagged tests matched: {tot}    unmatched: {unmatched}\n")
    print("MOCK-BINDING IDIOM (a test may use more than one)")
    for k, v in sorted(idiom_tally.items()):
        pct = 100.0 * v / tot if tot else 0
        star = "  <- the ONLY idiom the shipped resolver recognises" if k.startswith("A_") else ""
        print(f"  {k:26s} {v:>5}  ({pct:5.1f}%){star}")
    print()
    print("ASSERTION REFERENCES A MOCK-BOUND NAME")
    print(f"  tests with no assertion at all       : {no_assert:>5}")
    print(f"  shipped resolver (in-span binds only): {shipped_hit:>5}"
          f"   <- reproduces the shipped 0 if 0")
    print(f"  extended resolver (all idioms)       : {extended_hit:>5}")
    print(f"  findings the RESOLVER GAP hides      : {extended_hit - shipped_hit:>5}")
    print()
    print("per member (extended):")
    for mid, pm in per_member.items():
        print(f"  {mid:18s} n={pm['n']:<5} extended_mock_ref={pm['ext']}")
    print()
    print("examples the shipped resolver misses:")
    for mid, path, line, idioms, names in examples:
        print(f"  {mid}: {path}:{line}  idioms={idioms}  names={names}")


if __name__ == "__main__":
    main()
