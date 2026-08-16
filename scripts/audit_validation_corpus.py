"""Audit every ratified validation-set member and emit the adjudication-ready finding set.

    python scripts/audit_validation_corpus.py --checkout-root D:/ProjectX/XAgents/XAgents

**Story 13.1 / AC3b.** This is the operator-side runner the ESCALATION gates. It exists because
the corpus decided by AC1 and specified by AC3a has to actually be *run* before Story 13.2's
named human can adjudicate anything.

**What it does**

1. Reads the ratified membership from ``tests/corpus/_manifest.py`` — the one named place. It
   never takes a repository from the command line: a member that is not in the manifest is not
   in ``N``, so it cannot be audited into the corpus by an argument either.
2. Resolves each member to a local checkout and **verifies its ``git rev-parse HEAD`` equals the
   manifest's pinned sha**, refusing on mismatch. The pin is *enforced*, never assumed — DN-4
   pins by commit, and protocol §4 makes byte-reproducibility the precondition for an
   adjudication being valid at all.
3. Stages the git-**tracked** source files at that pin into a fresh committed snapshot, reusing
   the LOCKED ``materialize_snapshot`` the whole precision substrate already uses, and audits
   the snapshot through the **unmodified** ``pipeline.run_audit_detailed``. Nothing about the
   audit path is special-cased for the corpus.
4. **Runs each member TWICE and compares the canonical bytes.** A member whose two runs differ
   is reported ``REPRODUCIBLE: no`` and its findings are **withheld from the adjudication set** —
   protocol §4 again: adjudication is only valid over a byte-reproducible run, so shipping
   non-reproducible findings to a human would waste the scarcest resource in this plan.
5. Writes the adjudication-ready finding set in the shape 13.2 expects: per finding the 6.6
   ``finding_match_key`` identity ``(rule_id, verdict_eligible, advisory)`` plus ≥1 locator
   (FR13), grouped by member.

**What it refuses to do**

* **It never clones.** The operator ratified specific local checkouts; fetching is a network act
  against third-party hosts and is deliberately outside an autonomous runner (the AC3b
  escalation). Point it at checkouts that already exist.
* **It writes no source byte anywhere** (NFR-S1). The output carries rule ids, the two booleans,
  locators (path + line) and counts — exactly what ``minions-dogfood-proof.md`` already
  publishes for ``argus/``, and never a line of audited source.
* **It computes no precision number and flips no gate.** Classifying a finding TP or FP is the
  human step this whole epic exists to reach (Story 13.2), and a runner that scored its own
  output would have proven nothing.

Exit codes: ``0`` every member audited and reproducible · ``2`` a pin mismatch, a missing
checkout, or a non-reproducible member · ``3`` an audit raised.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:  # running as a script, not an installed console entry
    sys.path.insert(0, str(_REPO_ROOT))

from argus.dogfood.partition_plan import build_full_repo_plan  # noqa: E402
from argus.dogfood.proof_run import (  # noqa: E402
    DogfoodProofError,
    materialize_snapshot,
)
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.precision.replay_harness import (  # noqa: E402
    corpus_manifest_module,
    finding_match_key,
)
#: Where the adjudication set lands. 13.2 reads this.
OUTPUT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent" / "validation-corpus"

#: Source suffixes the snapshot carries — the 1.4 filter, imported rather than re-listed.
from argus.intake.repo_loader import _SOURCE_SUFFIXES  # noqa: E402

#: Directories that are never audited source even when a repository tracks them. Enumerated
#: with reasons rather than guessed: each is vendored or generated content whose defects belong
#: to somebody else, and including them would inflate the denominator with code the member's
#: authors never wrote — which would make the precision figure meaningless in the generous
#: direction rather than the strict one.
_EXCLUDED_TREES: dict[str, str] = {
    "node_modules/": "vendored third-party JavaScript; not authored by the member",
    ".venv/": "vendored Python environment; not authored by the member",
    "dist/": "build output, generated from sources already in the corpus",
    "build/": "build output, generated from sources already in the corpus",
    "_bmad/": "BMAD tooling vendored into the repository, not the member's product code",
    "_bmad-output/": "planning artifacts, not code",
    ".git/": "git internals",
}


@dataclass(frozen=True)
class MemberRun:
    """One member's audited result — counts, provenance and finding identities. No source."""

    member_id: str
    pinned_sha: str
    primary_language: str
    source_file_count: int
    verdict: str
    exit_code: int
    deep_ratio: str
    deep_count: int
    total_count: int
    blocking_finding_count: int
    total_finding_count: int
    reproducible: bool
    findings: tuple[dict[str, object], ...]


def _locator_strings(finding: object) -> list[str]:
    """FR13 locators as sorted ``path:line`` strings — the SAME rendering the dogfood uses.

    ``Locator`` is not orderable, so it is rendered before sorting rather than sorted as an
    object. Carries a path and a line number and never a byte of audited source (NFR-S1).
    """
    return sorted(
        {f"{loc.file_path}:{loc.start_line}" for loc in finding.locators}  # type: ignore[attr-defined]
    )


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, timeout=300
    )


def _tracked_sources(root: Path) -> tuple[str, ...]:
    """Git-tracked source files, excluding the vendored/generated trees enumerated above."""
    done = _git(root, "ls-files", "-z")
    if done.returncode != 0:
        raise DogfoodProofError(
            f"`git ls-files` failed in {root}: "
            f"{done.stderr.decode('utf-8', 'replace').strip()!r}"
        )
    records = done.stdout.decode("utf-8", errors="replace").split("\0")
    return tuple(
        sorted(
            rec
            for rec in records
            if rec
            and Path(rec).suffix in _SOURCE_SUFFIXES
            and not any(rec.startswith(p) or f"/{p}" in rec for p in _EXCLUDED_TREES)
        )
    )


def _audit_once(root: Path, sources: tuple[str, ...], workdir: Path) -> tuple[object, bytes]:
    """Stage a clean on-pin snapshot and run the UNMODIFIED audit over it.

    The budget is **sized empirically per member** by reusing Story 7.1's ``size_budget``
    recipe through ``build_full_repo_plan`` over the staged snapshot — not a constant. The
    dogfood's ``$X`` = 843 was sized for ``argus/`` (83 files); reusing it for a 591-file member
    would exhaust the budget mid-run and report a coverage shortfall that is an artefact of the
    number rather than a property of the repository. Sizing per member is the same accountant
    (AR7 — no forked cost model), applied to each member's own measured content.
    """
    snapshot_repo, sha = materialize_snapshot(root, sources, workdir / "snapshot")
    plan = build_full_repo_plan(str(snapshot_repo), scope_prefix=".", exclude_prefixes=())
    result = run_audit_detailed(
        AuditRequest(
            repo_path=str(snapshot_repo),
            commit=sha,
            budget=plan.budget.sized_ceiling,
            materiality_bar="default",
        )
    )
    # The reproducibility signature is built from the SAME surface the adjudication set
    # publishes — finding identity plus locators — so "byte-reproducible" means reproducible
    # in exactly the thing 13.2 will read, not in some adjacent artifact.
    findings = sorted(
        (list(finding_match_key(f)), _locator_strings(f)) for f in result.verdict.ordered_findings
    )
    signature = json.dumps(findings, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return result, signature


def _run_member(spec: object, checkout: Path) -> MemberRun:
    member_id = spec.member_id  # type: ignore[attr-defined]
    pinned = spec.commit_sha  # type: ignore[attr-defined]

    head = _git(checkout, "rev-parse", "HEAD")
    actual = head.stdout.decode().strip()
    if head.returncode != 0 or actual != pinned:
        raise SystemExit(
            f"REFUSED — {member_id}: checkout {checkout} is at {actual or '<unresolvable>'}, "
            f"but the manifest pins {pinned}. The pin is the precondition for the run being "
            "byte-reproducible and therefore adjudicable (protocol §4). Check out the pinned "
            "sha, or amend the manifest DELIBERATELY in a story that records why it moved."
        )

    sources = _tracked_sources(checkout)
    if not sources:
        raise SystemExit(f"REFUSED — {member_id}: no tracked source files enumerated")

    print(f"  {member_id}: {len(sources)} tracked source files at {pinned[:8]} — run 1/2", flush=True)
    with tempfile.TemporaryDirectory(prefix=f"argus-corpus-{member_id}-a-") as tmp_a:
        result_a, sig_a = _audit_once(checkout, sources, Path(tmp_a))
    print(f"  {member_id}: run 2/2 (byte-reproducibility check)", flush=True)
    with tempfile.TemporaryDirectory(prefix=f"argus-corpus-{member_id}-b-") as tmp_b:
        _result_b, sig_b = _audit_once(checkout, sources, Path(tmp_b))

    reproducible = sig_a == sig_b
    verdict = result_a.verdict  # type: ignore[attr-defined]

    findings: list[dict[str, object]] = []
    if reproducible:
        for finding in sorted(
            verdict.ordered_findings, key=lambda f: (f.rule_id, tuple(_locator_strings(f)))
        ):
            rule_id, verdict_eligible, advisory = finding_match_key(finding)
            findings.append(
                {
                    # The 6.6 finding_match_key identity — the SAME shape the cartridge
                    # substrate uses, so an adjudicated real-repository finding and a
                    # cartridge finding mean the same thing by "the same finding".
                    "rule_id": rule_id,
                    "verdict_eligible": verdict_eligible,
                    "advisory": advisory,
                    # FR13 — every finding carries >=1 verifiable locator. Path + line only.
                    "locators": _locator_strings(finding),
                    # Left for the human. 13.2 fills these in; nothing here guesses.
                    "adjudication": None,
                    "adjudicator": None,
                    "rationale": None,
                }
            )

    return MemberRun(
        member_id=member_id,
        pinned_sha=pinned,
        primary_language=spec.primary_language,  # type: ignore[attr-defined]
        source_file_count=len(sources),
        verdict=verdict.verdict.value,
        exit_code=verdict.exit_code,
        deep_ratio=f"{verdict.deep_ratio.numerator}/{verdict.deep_ratio.denominator}",
        deep_count=verdict.deep_count,
        total_count=verdict.total_count,
        blocking_finding_count=verdict.blocking_finding_count,
        total_finding_count=len(verdict.ordered_findings),
        reproducible=reproducible,
        findings=tuple(findings),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--checkout-root",
        required=True,
        help="Directory containing the ratified checkouts (resolved per member by --map).",
    )
    parser.add_argument(
        "--map",
        action="append",
        default=[],
        metavar="MEMBER_ID=RELATIVE_PATH",
        help="Where a member's checkout lives under --checkout-root. Repeatable.",
    )
    parser.add_argument("--only", action="append", default=[], help="Audit only these members.")
    args = parser.parse_args(argv)

    root = Path(args.checkout_root)
    overrides = dict(pair.split("=", 1) for pair in args.map)

    manifest = corpus_manifest_module()
    members = [s for s in manifest.eligible_members() if not args.only or s.member_id in args.only]
    if not members:
        print("REFUSED — no eligible members selected", file=sys.stderr)
        return 2

    print(f"auditing {len(members)} ratified member(s) from {root}")
    runs: list[MemberRun] = []
    for spec in members:
        checkout = root / overrides.get(spec.member_id, spec.member_id)
        if not (checkout / ".git").is_dir():
            print(
                f"REFUSED — {spec.member_id}: no git checkout at {checkout}. This runner never "
                "clones (the AC3b escalation): point --map at an existing checkout.",
                file=sys.stderr,
            )
            return 2
        try:
            runs.append(_run_member(spec, checkout))
        except (DogfoodProofError, Exception) as exc:  # noqa: BLE001 - reported, never swallowed
            if isinstance(exc, SystemExit):
                raise
            print(f"AUDIT FAILED — {spec.member_id}: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 3

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1",
        "story": "13-1-decide-what-validation-set-is-then-build-it",
        "purpose": (
            "Adjudication-ready finding set for Story 13.2. Every finding carries the 6.6 "
            "finding_match_key identity and >=1 locator, and NO audited source byte (NFR-S1). "
            "The adjudication/adjudicator/rationale fields are NULL by design: classifying a "
            "finding TP or FP is the named human's act, and nothing here guesses at it."
        ),
        "members": [
            {
                "member_id": r.member_id,
                "pinned_sha": r.pinned_sha,
                "primary_language": r.primary_language,
                "source_file_count": r.source_file_count,
                "verdict": r.verdict,
                "exit_code": r.exit_code,
                "deep_ratio": r.deep_ratio,
                "deep_count": r.deep_count,
                "total_count": r.total_count,
                "blocking_finding_count": r.blocking_finding_count,
                "total_finding_count": r.total_finding_count,
                "byte_reproducible_across_two_runs": r.reproducible,
                "findings": list(r.findings),
            }
            for r in runs
        ],
    }
    out = OUTPUT_DIR / "adjudication-set.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    # The BLOCKING worklist. The full set is ~2 MB and is overwhelmingly advisory findings,
    # which are recorded but are NOT false accusations and do NOT enter the precision
    # denominator (protocol §4, as amended by Story 13.1). What Story 13.2's named human
    # actually has to judge is the blocking subset — so it gets its own small, readable file,
    # DERIVED from the same run rather than transcribed. A 2 MB JSON is a machine artifact;
    # a human adjudication list that nobody can read is an adjudication that does not happen.
    worklist = OUTPUT_DIR / "blocking-worklist.md"
    lines = [
        "# Blocking-finding adjudication worklist — Story 13.2",
        "",
        "> DERIVED by `scripts/audit_validation_corpus.py`. Do not hand-edit: re-run the",
        "> script. Every row is a **blocking** (verdict-eligible) finding — the population the",
        "> ≥80% precision gate is measured over. Advisory findings are in",
        "> `adjudication-set.json` and are deliberately absent here: an advisory finding does",
        "> not move a verdict and is not a false accusation, so it is not in the denominator.",
        "",
        "**Nothing below is adjudicated.** TP/FP is the named human's call (protocol §2/§4).",
        "",
    ]
    grand_total = 0
    for r in runs:
        blocking = [f for f in r.findings if f["verdict_eligible"]]
        grand_total += len(blocking)
        lines += [
            f"## {r.member_id} — {len(blocking)} blocking",
            "",
            f"Pin `{r.pinned_sha}` · {r.primary_language} · {r.source_file_count} source files "
            f"· verdict `{r.verdict}` (exit {r.exit_code}) · deep {r.deep_ratio}",
            "",
        ]
        if not blocking:
            lines += ["_No blocking finding. Nothing to adjudicate for this member._", ""]
            continue
        lines += ["| # | rule_id | locator | TP/FP | adjudicator | rationale |", "|---|---|---|---|---|---|"]
        for i, f in enumerate(blocking, 1):
            locs = "; ".join(str(x) for x in f["locators"][:3]) or "_none_"
            lines.append(f"| {i} | `{f['rule_id']}` | `{locs}` | | | |")
        lines.append("")
    lines += [
        "---",
        "",
        f"**Total blocking findings to adjudicate: {grand_total}.** Precision = TP / (TP + FP) "
        "over this population, as an exact `Fraction` (AR4). The gate additionally requires "
        "0 blocking false positives on a clean repository, N ≥ 5, and the adjudication run "
        "recorded cleared — all four, or the gate stays PROVISIONAL (protocol §5).",
    ]
    worklist.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nwrote {out.relative_to(_REPO_ROOT).as_posix()}")
    print(f"wrote {worklist.relative_to(_REPO_ROOT).as_posix()} ({grand_total} to adjudicate)")
    print(f"{'member':18} {'verdict':26} {'blocking':>8} {'total':>6} {'deep':>10}  repro")
    for r in runs:
        print(
            f"{r.member_id:18} {r.verdict:26} {r.blocking_finding_count:8} "
            f"{r.total_finding_count:6} {r.deep_ratio:>10}  {'yes' if r.reproducible else 'NO'}"
        )
    non_repro = [r.member_id for r in runs if not r.reproducible]
    if non_repro:
        print(
            f"\nREFUSED — not byte-reproducible across two runs: {non_repro}. Their findings "
            "are WITHHELD from the adjudication set: protocol §4 makes reproducibility the "
            "precondition for an adjudication being valid.",
            file=sys.stderr,
        )
        return 2
    print("\nAll members byte-reproducible. NOTHING here is adjudicated — that is Story 13.2.")
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry
    raise SystemExit(main())
