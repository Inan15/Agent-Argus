"""Advisory meta-work drift report — PRINTS AND PROCEEDS. It is not a gate.

Proposed home: ``scripts/check_meta_drift.py``.
Proposed baseline: ``_bmad-output/design-artifacts/ArgusAgent/meta-drift-baseline.md``.

WHY ADVISORY, NOT BLOCKING. Every predicate below reads PROSE and makes a
judgement about provenance. A blocking prose-parser produces false failures that
abort legitimate work, and this repository already carries the scar
(``TC-ArgusAgent-DOCS-001-78`` went RED three times from prose in one day —
`epic-14-retro-2026-08-18.md` §3.4). So: this script always exits 0 on a clean
parse. A non-zero exit means the script could not READ its inputs — never that a
finding was made.

FORWARD-ONLY. Nothing authored before :data:`CUTOFF_EPIC` is classified. Epics 1
through 16 predate the rule and print as ``(pre-rule)`` with no verdict. An
item's age is evidence, not noise (§3.4 evidence immutability).

WHAT IT REFUSES TO DO. It never edits an artifact and never returns a "retire
this guard" verdict — §GS-3 reports only whether the project can yet ANSWER that
question. On the 2026-08-23 baseline it cannot.

Usage::

    python scripts/check_meta_drift.py            # report
    python scripts/check_meta_drift.py --json     # machine-readable
    python scripts/check_meta_drift.py --since 13 # diagnostic: classify earlier
                                                  # epics WITHOUT moving the cutoff
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# ── Forward-only cutoff. Epics below this number are never classified. Raise it
#    only with a recorded operator ruling; never lower it. Epic 17 is the first
#    epic authored after this rule, so it is the first epic the rule governs.
CUTOFF_EPIC = 17

# ── §RD-1 advisory budget: process-derived stories as a share of an epic's
#    backlog. NOT a threshold that blocks; a number a human reads.
RETRO_DERIVED_BUDGET = 0.20

REPO = Path(__file__).resolve().parents[1]
ARTIFACTS = REPO / "_bmad-output" / "design-artifacts" / "ArgusAgent"
EPICS = ARTIFACTS / "epics.md"
BASELINE = ARTIFACTS / "meta-drift-baseline.md"

# Provenance is classified from `epics.md` — the document where this project
# already records why a story exists — never from the story file, whose §0
# research legitimately cites every driver it re-measured.
#
# PRODUCT-GOAL-TRACED: the story block names a requirement driver.
DRIVER = re.compile(r"\b(?:ArgusAgent-)?(?:FR|NFR)-?\d+\b|\bNFR-[A-Z]\d+\b")
# PROCESS-TRACED: the block names only retrospective / ledger provenance.
PROCESS = re.compile(r"\bAI-E\d+-\d+\b|\bSD-\d+\b|\bDF-[\dA-Z]+-\d+-[A-Z]\b")

EPIC_HEAD = re.compile(r"^## Epic (\d+):\s*(.+?)\s*$", re.MULTILINE)
STORY_HEAD = re.compile(r"^### Story ([\d.]+):", re.MULTILINE)
COVERS = re.compile(r"^\*\*Covers:\*\*(.*)$", re.MULTILINE)
CAPABILITY = re.compile(r"^\*\*Capability delivered:\*\*\s*(.+)$", re.MULTILINE)

# `git grep -E` is POSIX ERE: `\d` is NOT a digit class there. Use [0-9].
GUARD_ERE = "TC-ArgusAgent-[A-Z0-9]+-[0-9]+-[0-9]+"
GUARD_ID = re.compile(GUARD_ERE)
RULING = re.compile(r"\bDN-[A-Z0-9-]+\b|\bAI-E\d+-\d+\b|\bDF-[\dA-Z]+-\d+-[A-Z]\b")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True
    ).stdout.decode("utf-8", "replace")


# ──────────────────────────────────────────────────────────────────────────────
# §RD-1 retro-derived work budget · §CD-2 capability-delivered field
# ──────────────────────────────────────────────────────────────────────────────
def classify(cutoff: int) -> list[dict]:
    text = _read(EPICS)
    heads = list(EPIC_HEAD.finditer(text))
    rows: list[dict] = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body, epic = text[m.start() : end], int(m.group(1))
        if any(r["epic"] == epic for r in rows):
            continue  # a delta run re-opens an epic; the first full block wins
        stories = list(STORY_HEAD.finditer(body))
        product, process, flagged = 0, 0, []
        for j, s in enumerate(stories):
            se = stories[j + 1].start() if j + 1 < len(stories) else len(body)
            block = body[s.start() : se]
            if DRIVER.search(block):
                product += 1
            else:
                process += 1
                flagged.append(s.group(1))
        cov = COVERS.search(body)
        cap = CAPABILITY.search(body)
        rows.append(
            {
                "epic": epic,
                "title": m.group(2)[:52],
                "pre_rule": epic < cutoff,
                "stories": product + process,
                "product": product,
                "process": process,
                "process_ids": flagged,
                "covers_names_driver": bool(cov and DRIVER.search(cov.group(1))),
                "covers_present": bool(cov),
                "capability": cap.group(1).strip() if cap else None,
            }
        )
    return rows


def report_epics(rows: list[dict]) -> None:
    print("§RD-1  Process-derived work budget    §CD-2  Capability delivered")
    print("-" * 78)
    for r in rows:
        if r["pre_rule"]:
            continue
        n = r["stories"]
        share = (r["process"] / n) if n else 0.0
        mark = "  " if share <= RETRO_DERIVED_BUDGET else "!!"
        print(
            f"{mark}Epic {r['epic']:<3} stories={n:<3} product-traced={r['product']:<3} "
            f"process-traced={r['process']:<3} ({share:.0%}, budget {RETRO_DERIVED_BUDGET:.0%})"
        )
        if r["process_ids"]:
            print(f"      process-traced stories: {', '.join(r['process_ids'])}")
        if not r["covers_names_driver"]:
            print("    !!**Covers:** names no FR/NFR driver — the epic seed traces")
            print("      to process provenance only")
        cap = r["capability"]
        if cap is None:
            print("    !!epic seed carries no **Capability delivered:** field")
        elif cap.lower().startswith(("nothing", "none")):
            ok = re.search(r"ruling|approved by|operator", cap, re.I)
            print(f'    {"  " if ok else "!!"}capability = "Nothing"'
                  f'{" (ruling cited)" if ok else " — NO RULING CITED"}')
        else:
            print(f"      capability: {cap[:64]}")
    n_classified = sum(1 for r in rows if not r["pre_rule"])
    if not n_classified:
        print(f"      no epic at or above the cutoff ({CUTOFF_EPIC}) yet — nothing to")
        print("      classify. This is the expected state on the day the rule lands.")
    print(f"      ({sum(1 for r in rows if r['pre_rule'])} epics below the cutoff, not classified)")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# §GS-3 guard sunset — CAN the project answer "has this guard caught anything?"
# ──────────────────────────────────────────────────────────────────────────────
def guard_evidence() -> dict:
    in_tests = set(GUARD_ID.findall(_git("grep", "-hoE", GUARD_ERE, "--", "tests/")))
    in_prose = set(GUARD_ID.findall(_git("grep", "-hoE", GUARD_ERE, "--", "_bmad-output/")))
    in_log = set(GUARD_ID.findall(_git("log", "--format=%s%n%b")))
    return {
        "total": len(in_tests),
        "cited_in_commits": len(in_tests & in_log),
        "cited_in_prose": len(in_tests & in_prose),
        "orphans": len(in_tests - in_prose - in_log),
    }


def report_guards(g: dict) -> None:
    print("§GS-3  Guard sunset — the instrumentation it needs first")
    print("-" * 78)
    print(f"      guard ids in tests/                   : {g['total']}")
    print(f"      ever named in a commit message        : {g['cited_in_commits']}")
    print(f"      named in governance prose             : {g['cited_in_prose']}")
    print(f"      named NOWHERE outside their own file  : {g['orphans']}")
    pct = g["orphans"] / g["total"] if g["total"] else 0
    print()
    print(f"    !!{pct:.0%} of guards have no recorded history of catching anything.")
    print("      'Never mentioned' is NOT 'never fired'. A sunset rule cannot")
    print("      retire a guard on this evidence, so this section proposes NOTHING")
    print("      for deletion. The prerequisite is a fire ledger: a guard id gets a")
    print("      dated row the first time it goes RED against a defect that reached")
    print("      the tree. Retirement becomes discussable only for guards with an")
    print("      empty ledger AND a review date reached.")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# §RB-4 ruling duplication — one home per ruling
# ──────────────────────────────────────────────────────────────────────────────
def duplication(top: int = 10) -> list[tuple[str, int]]:
    where: dict[str, set[str]] = {}
    for path in ARTIFACTS.rglob("*.md"):
        rel = str(path.relative_to(ARTIFACTS))
        for rid in set(RULING.findall(_read(path))):
            where.setdefault(rid, set()).add(rel)
    return sorted(((r, len(f)) for r, f in where.items()), key=lambda x: -x[1])[:top]


def report_duplication(worst: list[tuple[str, int]]) -> None:
    print("§RB-4  Ruling duplication — documents each ruling id is restated in")
    print("-" * 78)
    for rid, n in worst:
        print(f"{'!!' if n > 3 else '  '}    {rid:<18} restated in {n} documents")
    print()
    print("      Restatement is not free: every copy must be kept consistent with")
    print("      every other, and that reconciliation is itself work. The remedy is")
    print("      an INDEX plus pointers, never a deletion — §3.4 forbids erasing")
    print("      the originating text.")
    print()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Advisory meta-work drift report.")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument(
        "--since",
        type=int,
        default=None,
        metavar="N",
        help="DIAGNOSTIC ONLY: classify from epic N. Does not change the "
        "committed cutoff and never produces a verdict on pre-rule work.",
    )
    args = ap.parse_args(argv)

    if not EPICS.exists():
        print(f"error: cannot read {EPICS}", file=sys.stderr)
        return 2

    cutoff = args.since if args.since is not None else CUTOFF_EPIC
    rows = classify(cutoff)
    g = guard_evidence()
    dup = duplication()

    if args.json:
        print(json.dumps({"cutoff": cutoff, "epics": rows, "guards": g,
                          "duplication": dup}, indent=2))
        return 0

    print()
    print("=" * 78)
    print(" ADVISORY meta-work drift report — prints and proceeds, never blocks")
    print(f" forward-only: epics below {cutoff} are not classified"
          + ("   [DIAGNOSTIC --since]" if args.since is not None else ""))
    print("=" * 78)
    print()
    report_epics(rows)
    report_guards(g)
    report_duplication(dup)
    print("Lines marked !! are findings for a human, NOT build failures.")
    print(f"Baseline: {'committed' if BASELINE.exists() else '(not yet committed)'}")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
