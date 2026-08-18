"""Audit every ratified validation-set member and emit the adjudication-ready finding set.

    python scripts/audit_validation_corpus.py --checkout-root D:/ProjectX/XAgents/XAgents

**Story 13.1 / AC3b.** This is the operator-side runner the ESCALATION gates. It exists because
the corpus decided by AC1 and specified by AC3a has to actually be *run* before Story 13.2's
named human can adjudicate anything.

**What it does**

1. Reads the ratified membership from ``tests/corpus/_manifest.py`` — the one named place. It
   never takes a repository from the command line: a member that is not in the manifest is not
   in ``N``, so it cannot be audited into the corpus by an argument either.
2. Resolves each member to a local checkout and reads its tree **from the pinned git object**
   (``git ls-tree -r <pin>`` + ``git cat-file --batch``), never from the working tree. The pin
   is *structurally enforced*, not assumed — DN-4 pins by commit, and protocol §4 makes
   byte-reproducibility the precondition for an adjudication being valid at all. A pin that is
   not in the checkout's object database is a NAMED ``Unevaluable`` outcome for that member
   (:class:`pinned_corpus_snapshot.PinUnreachable`), never a silent fallback.
3. Stages those pinned bytes into a fresh committed snapshot through the LOCKED
   ``materialize_snapshot``, **PROVES every staged file hashes to its pinned blob**
   (Story 13.5 / AC1), and audits the snapshot through the **unmodified**
   ``pipeline.run_audit_detailed``. Nothing about the audit path is special-cased for the
   corpus.

   **Story 13.5 changed (2) and (3), and the reason is measured.** Until then the runner
   compared ``git rev-parse HEAD`` to the pin and then staged **working-tree** bytes. Those
   are two different claims: a member sitting on the right commit with a dirty working tree
   was audited as its DIRTY bytes while the record said *"at the pin"*, and
   ``byte_reproducible_across_two_runs`` still reported ``True`` because two runs over the
   same wrong bytes are reproducible. Reproducibility is not provenance. See
   ``scripts/pinned_corpus_snapshot.py`` for the measurement that found it.
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

Exit codes: ``0`` every member audited, pin-verified and reproducible · ``2`` a refusal the
operator must act on (a malformed ``--map``, an absolute mapped path, a missing checkout, an
unreachable pin, no sources at the pin, bytes that could not be proved to be the pinned bytes,
or a non-reproducible member) · ``3`` an audit raised an unexpected error. Refusals are
:class:`CorpusRefusal`, never ``SystemExit`` — see that class for why.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:  # running as a script, not an installed console entry
    sys.path.insert(0, str(_REPO_ROOT))

if str(Path(__file__).resolve().parent) not in sys.path:  # sibling script modules
    sys.path.insert(0, str(Path(__file__).resolve().parent))

# ``_is_test_function`` is IMPORTED rather than re-derived (AR7): the corpus-read proof must
# count the population the SHIPPED detector actually scores, and a second "looks like a test"
# predicate here would drift from it silently — which would make the proof a decoration. The
# ``_SOURCE_SUFFIXES`` import below sets the same precedent.
from argus.detectors.vacuous_test import (  # noqa: E402
    _is_test_function,
    is_test_file,
)
from argus.dogfood.partition_plan import build_full_repo_plan  # noqa: E402
from argus.dogfood.proof_run import materialize_snapshot  # noqa: E402
from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.precision.replay_harness import (  # noqa: E402
    corpus_manifest_module,
    finding_match_key,
)
from pinned_corpus_snapshot import (  # noqa: E402
    PinnedBytesRefusal,
    PinnedSnapshotError,
    PinnedTree,
    PinVerification,
    dirty_in_scope_paths,
    materialize_pinned_bytes,
    pinned_tree,
    verify_pinned_bytes,
)

#: Where the adjudication set lands. 13.2 reads this.
OUTPUT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent" / "validation-corpus"

#: The story this runner was written for. Overridable, because Story 13.5 re-runs the SAME
#: instrument over the SAME corpus at the SAME pins and must not claim to be 13.1's run.
_DEFAULT_STORY = "13-1-decide-what-validation-set-is-then-build-it"

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


def in_scope_source(rel: str) -> bool:
    """The ONE in-scope predicate: a 1.4 source suffix outside the vendored/generated trees.

    Named and shared (AR7) because Story 13.5 needs the SAME filter in three places — the
    pinned tree listing, the dirty-tree evidence and the corpus-read proof — and three
    copies of a filter is three chances for the population to differ from the one measured.
    """
    return bool(
        rel
        and Path(rel).suffix in _SOURCE_SUFFIXES
        and not any(rel.startswith(p) or f"/{p}" in rel for p in _EXCLUDED_TREES)
    )


@dataclass(frozen=True)
class CorpusReadEvidence:
    """PROOF that the corpus was READ — Story 13.5 / AC1, the non-vacuity floor of a zero.

    Story 13.5's central result is an **absence**: zero verdict-eligible findings. An absence
    is the one claim a broken harness produces for free, so the run records, per member, the
    population it actually scanned and scored. *"We read 1,960 files, scored 6,000 test
    functions, flagged 269 files and promoted none"* is a measurement; *"we found nothing"*
    over an unread tree is the same bytes downstream. These fields are what make the two
    distinguishable.
    """

    source_file_count: int
    test_file_count: int
    scored_test_function_count: int
    flagged_file_count: int
    blocking_finding_count: int
    advisory_finding_count: int
    #: Emitted findings per rule id, SORTED. This is what makes the headline zero CHECKABLE
    #: at the rule level rather than in aggregate: `vacuous_test_ast: 0` beside
    #: `vacuous_test_heuristic: 648` says the detector RAN and promoted nothing, which is a
    #: different claim from a pipeline that emitted nothing at all.
    findings_by_rule: tuple[tuple[str, int], ...] = ()

    @property
    def proves_corpus_was_read(self) -> bool:
        """A read is proved by a non-empty SCANNED and a non-empty SCORED population.

        Both, not either: a tree of 900 non-test files reads fine and scores nothing, and a
        detector that never ran also scores nothing. The flagged and advisory counts are
        recorded but deliberately NOT part of the predicate — requiring a flag would make a
        genuinely clean corpus unprovable, which is the opposite failure.
        """
        return self.source_file_count > 0 and self.scored_test_function_count > 0

    def to_payload(self) -> dict[str, object]:
        return {
            "source_file_count": self.source_file_count,
            "test_file_count": self.test_file_count,
            "scored_test_function_count": self.scored_test_function_count,
            "flagged_file_count": self.flagged_file_count,
            "blocking_finding_count": self.blocking_finding_count,
            "advisory_finding_count": self.advisory_finding_count,
            "findings_by_rule": {rule: count for rule, count in self.findings_by_rule},
            "proves_corpus_was_read": self.proves_corpus_was_read,
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
    checkout_head_sha: str
    checkout_head_equals_pin: bool
    dirty_in_scope_source_files: tuple[str, ...]
    pin_verification: PinVerification
    read_evidence: CorpusReadEvidence


class CorpusRefusal(Exception):
    """A refusal the operator must act on — reported cleanly, and mapped to exit code 2.

    Code-review R5. These were ``raise SystemExit(<str>)``, which looked like it produced the
    documented exit code 2 and did not: ``SystemExit`` carrying a string makes Python print the
    string and exit **1**. Worse, ``SystemExit`` derives from ``BaseException``, so the
    ``except (DogfoodProofError, Exception)`` handler in :func:`main` never caught it and the
    ``isinstance(exc, SystemExit): raise`` line inside that handler was unreachable code that
    read as though it were doing something. A refusal is now an ordinary exception with one
    handler and one documented exit code.
    """


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


def _scored_population(repo: Path, sources: tuple[str, ...]) -> tuple[int, int]:
    """``(test_file_count, scored_test_function_count)`` over the STAGED snapshot (AC1).

    Built through the SHIPPED ``build_ast_index`` + the SHIPPED ``is_test_file`` +
    ``_is_test_function``, so the population counted here is the population the detector
    scores — not an approximation of it. A file the index marked ``parse_failed`` or
    ``ast_eligible=False`` contributes nothing, which is the point: an unparsed file and a
    well-asserted file both emit no finding, and only this count tells them apart.
    """
    index = build_ast_index(repo, sources, partition_id="root")
    test_files = 0
    scored = 0
    for entry in index.entries:
        if not is_test_file(entry.file_path, ast_entry=entry):
            continue
        test_files += 1
        if entry.parse_failed or not entry.ast_eligible:
            continue
        scored += sum(1 for d in entry.definitions if _is_test_function(d))
    return test_files, scored


def _audit_once(
    checkout: Path, tree: PinnedTree, workdir: Path, *, measure_scored: bool = False
) -> tuple[object, bytes, PinVerification, tuple[int, int]]:
    """Stage the PINNED bytes as a clean snapshot, PROVE them, and run the UNMODIFIED audit.

    The budget is **sized empirically per member** by reusing Story 7.1's ``size_budget``
    recipe through ``build_full_repo_plan`` over the staged snapshot — not a constant. The
    dogfood's ``$X`` = 843 was sized for ``argus/`` (83 files); reusing it for a 591-file member
    would exhaust the budget mid-run and report a coverage shortfall that is an artefact of the
    number rather than a property of the repository. Sizing per member is the same accountant
    (AR7 — no forked cost model), applied to each member's own measured content.
    """
    pinned_bytes = materialize_pinned_bytes(checkout, tree, workdir / "pinned")
    snapshot_repo, sha = materialize_snapshot(pinned_bytes, tree.paths, workdir / "snapshot")
    # The PROOF, taken on the tree the audit is about to read — not on the intermediate one.
    # It covers both writes at once and it is the reason a MAX_PATH truncation, a dropped
    # file or a byte that is not the pinned byte cannot reach the measurement silently.
    verification = verify_pinned_bytes(snapshot_repo, tree)
    if not verification.proves_pinned_bytes:
        raise PinnedBytesRefusal(
            f"the staged snapshot could NOT be proved to be the pinned bytes of "
            f"{tree.commit_sha}: {verification.verified_file_count} of "
            f"{verification.expected_file_count} file(s) verified; "
            f"{len(verification.missing_paths)} missing, "
            f"{len(verification.mismatched_paths)} content mismatch(es). First few — "
            f"missing: {list(verification.missing_paths[:3])}, "
            f"mismatched: {list(verification.mismatched_paths[:3])}."
        )
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
    # Measured on the FIRST run only: the population is a property of the pinned tree, and
    # the second run exists to compare signatures, not to re-count what cannot have moved.
    scored = _scored_population(snapshot_repo, tree.paths) if measure_scored else (0, 0)
    return result, signature, verification, scored


def _run_member(spec: object, checkout: Path, snapshot_root: Path | None = None) -> MemberRun:
    member_id = spec.member_id  # type: ignore[attr-defined]
    pinned = spec.commit_sha  # type: ignore[attr-defined]

    # HEAD is RECORDED, not enforced (Story 13.5). The audited bytes come from the pinned
    # object, so a checkout parked on another branch no longer changes what is measured —
    # and that is the point: the pin became structurally enforced instead of assumed. HEAD
    # stays on the record because "the checkout was elsewhere and it provably did not
    # matter" is a stronger, checkable statement than silence.
    head = _git(checkout, "rev-parse", "HEAD")
    # errors="replace" matches every other git decode in this file (code-review R9). A
    # corrupted git state should surface as recorded provenance, not as an uncaught
    # UnicodeDecodeError.
    actual = head.stdout.decode("utf-8", "replace").strip()

    # The pin itself is NOT optional. An unreachable pin is a named Unevaluable outcome for
    # this member and it propagates as a refusal — never a fallback to the working tree.
    tree = pinned_tree(checkout, pinned, keep=in_scope_source)
    if not tree.files:
        raise CorpusRefusal(
            f"{member_id}: ZERO in-scope source files at pin {pinned}. A measurement over an "
            f"empty corpus reports zero findings and is byte-identical to a clean one."
        )
    dirty = dirty_in_scope_paths(checkout, keep=in_scope_source)

    print(
        f"  {member_id}: {len(tree.files)} in-scope source files AT PIN {pinned[:8]} "
        f"(HEAD {actual[:8] or '<unresolvable>'}, {len(dirty)} dirty in-scope) — run 1/2",
        flush=True,
    )
    with tempfile.TemporaryDirectory(
        prefix=f"ac-{member_id}-a-", dir=str(snapshot_root) if snapshot_root else None
    ) as tmp_a:
        result_a, sig_a, verification, scored = _audit_once(
            checkout, tree, Path(tmp_a), measure_scored=True
        )
    print(f"  {member_id}: run 2/2 (byte-reproducibility check)", flush=True)
    with tempfile.TemporaryDirectory(
        prefix=f"ac-{member_id}-b-", dir=str(snapshot_root) if snapshot_root else None
    ) as tmp_b:
        _result_b, sig_b, _verification_b, _ = _audit_once(checkout, tree, Path(tmp_b))

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

    flagged_files = {
        locator.rsplit(":", 1)[0]
        for finding in verdict.ordered_findings
        for locator in _locator_strings(finding)
    }
    blocking = sum(1 for f in verdict.ordered_findings if finding_match_key(f)[1])
    test_file_count, scored_test_functions = scored
    return MemberRun(
        member_id=member_id,
        pinned_sha=pinned,
        primary_language=spec.primary_language,  # type: ignore[attr-defined]
        source_file_count=len(tree.files),
        verdict=verdict.verdict.value,
        exit_code=verdict.exit_code,
        deep_ratio=f"{verdict.deep_ratio.numerator}/{verdict.deep_ratio.denominator}",
        deep_count=verdict.deep_count,
        total_count=verdict.total_count,
        blocking_finding_count=verdict.blocking_finding_count,
        total_finding_count=len(verdict.ordered_findings),
        reproducible=reproducible,
        findings=tuple(findings),
        checkout_head_sha=actual or "<unresolvable>",
        checkout_head_equals_pin=actual == pinned,
        dirty_in_scope_source_files=dirty,
        pin_verification=verification,
        read_evidence=CorpusReadEvidence(
            source_file_count=len(tree.files),
            test_file_count=test_file_count,
            scored_test_function_count=scored_test_functions,
            flagged_file_count=len(flagged_files),
            blocking_finding_count=blocking,
            advisory_finding_count=len(verdict.ordered_findings) - blocking,
            findings_by_rule=tuple(
                sorted(Counter(f.rule_id for f in verdict.ordered_findings).items())
            ),
        ),
    )


def corpus_read_proof(runs: Sequence[MemberRun]) -> dict[str, object]:
    """The corpus-level read proof — the ONE object a downstream zero may rest on (AC1).

    Every clause is a conjunct and every conjunct is measured on this run:

    * ``members_audited > 0`` — a fold over zero members proves nothing;
    * every member's bytes were **proved to be the pinned bytes** (hash per file);
    * every member was **byte-reproducible across two runs** (protocol §4);
    * every member has a non-empty **scanned** and non-empty **scored** population.

    ``proves_corpus_was_read`` is what :func:`argus.precision.gate_decision.decide_gate`'s
    narrowed vacuity floor consults. Where it is False, an empty finding population still
    means *"the corpus could not be read"* and the floor still refuses — unchanged.
    """
    return {
        "statement": (
            f"{len(runs)} member(s) audited at their pinned shas, read from the git object "
            f"database and proved byte-for-byte against it; "
            f"{sum(r.read_evidence.source_file_count for r in runs)} in-scope source file(s) "
            f"scanned, {sum(r.read_evidence.test_file_count for r in runs)} test file(s) "
            f"identified, "
            f"{sum(r.read_evidence.scored_test_function_count for r in runs)} test "
            f"function(s) scored, "
            f"{sum(r.read_evidence.flagged_file_count for r in runs)} file(s) flagged, "
            f"{sum(r.read_evidence.advisory_finding_count for r in runs)} advisory and "
            f"{sum(r.read_evidence.blocking_finding_count for r in runs)} blocking finding(s) "
            f"emitted. A zero blocking count over THIS population is a measurement; a zero "
            f"over an unread corpus is an absence, and these figures are what tell them apart."
        ),
        "members_audited": len(runs),
        "member_ids": sorted(r.member_id for r in runs),
        "source_file_count": sum(r.read_evidence.source_file_count for r in runs),
        "test_file_count": sum(r.read_evidence.test_file_count for r in runs),
        "scored_test_function_count": sum(
            r.read_evidence.scored_test_function_count for r in runs
        ),
        "flagged_file_count": sum(r.read_evidence.flagged_file_count for r in runs),
        "advisory_finding_count": sum(r.read_evidence.advisory_finding_count for r in runs),
        "blocking_finding_count": sum(r.read_evidence.blocking_finding_count for r in runs),
        "findings_by_rule": dict(
            sorted(
                sum(
                    (Counter(dict(r.read_evidence.findings_by_rule)) for r in runs),
                    Counter(),
                ).items()
            )
        ),
        "every_member_pin_verified": bool(runs)
        and all(r.pin_verification.proves_pinned_bytes for r in runs),
        "every_member_byte_reproducible": bool(runs) and all(r.reproducible for r in runs),
        "every_member_scored_population_non_empty": bool(runs)
        and all(r.read_evidence.proves_corpus_was_read for r in runs),
        "proves_corpus_was_read": bool(runs)
        and all(
            r.pin_verification.proves_pinned_bytes
            and r.reproducible
            and r.read_evidence.proves_corpus_was_read
            for r in runs
        ),
    }


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
    parser.add_argument(
        "--snapshot-root",
        default=None,
        help=(
            "Directory the pinned snapshots are materialized under. Use a SHORT path on "
            "Windows (e.g. D:/_argus_snap): a member's deepest in-scope path is ~104 "
            "characters and the default temp root can push the absolute path past MAX_PATH."
        ),
    )
    parser.add_argument(
        "--output-name",
        default="adjudication-set.json",
        help=(
            "Artifact filename under validation-corpus/. Story 13.5 writes a SUPERSEDING "
            "set under its own name rather than overwriting 13.1's: §3.4 evidence "
            "immutability — a correction supersedes, it never erases."
        ),
    )
    parser.add_argument(
        "--supersedes",
        default=None,
        help="The artifact this run supersedes, recorded ON the artifact (§3.4).",
    )
    parser.add_argument("--story", default=_DEFAULT_STORY, help="Story id recorded on the artifact.")
    args = parser.parse_args(argv)

    root = Path(args.checkout_root)
    snapshot_root = Path(args.snapshot_root) if args.snapshot_root else None
    if snapshot_root is not None:
        snapshot_root.mkdir(parents=True, exist_ok=True)

    # Code-review R8/R6. `dict(pair.split("=", 1) for pair in args.map)` raised a raw
    # `ValueError: dictionary update sequence element #0 has length 1` on `--map foo`, dumping a
    # traceback at an operator in a script where every other failure prints a clean REFUSED.
    # And an ABSOLUTE mapped value silently escaped --checkout-root entirely, because
    # `Path("C:/root") / "D:/elsewhere"` is `D:/elsewhere` — pathlib discards the left operand.
    # The metavar promised RELATIVE_PATH; nothing enforced it. Both are refusals now.
    overrides: dict[str, str] = {}
    for pair in args.map:
        if "=" not in pair:
            print(
                f"REFUSED — --map {pair!r} is not MEMBER_ID=RELATIVE_PATH (no '=' found)",
                file=sys.stderr,
            )
            return 2
        member_id, _, rel = pair.partition("=")
        if not member_id.strip() or not rel.strip():
            print(f"REFUSED — --map {pair!r} has an empty member id or path", file=sys.stderr)
            return 2
        if PurePosixPath(rel.replace("\\", "/")).is_absolute() or Path(rel).is_absolute():
            print(
                f"REFUSED — --map {pair!r} names an ABSOLUTE path. It must be relative to "
                "--checkout-root: pathlib discards the root when the right operand is "
                "absolute, so an absolute value would silently audit a tree outside the "
                "directory the operator scoped this run to.",
                file=sys.stderr,
            )
            return 2
        overrides[member_id.strip()] = rel.strip()

    manifest = corpus_manifest_module()
    members = [s for s in manifest.eligible_members() if not args.only or s.member_id in args.only]
    if not members:
        print("REFUSED — no eligible members selected", file=sys.stderr)
        return 2

    print(f"auditing {len(members)} ratified member(s) from {root}")
    runs: list[MemberRun] = []
    for spec in members:
        checkout = root / overrides.get(spec.member_id, spec.member_id)
        # `.exists()`, not `.is_dir()` (code-review R7): in a git WORKTREE or a SUBMODULE, `.git`
        # is a plain FILE containing a `gitdir:` pointer. Both are fully valid repositories, and
        # `is_dir()` refused them as "no git checkout" — which would have blocked an operator
        # who staged the corpus with `git worktree add`, for no real reason.
        if not (checkout / ".git").exists():
            print(
                f"REFUSED — {spec.member_id}: no git checkout at {checkout}. This runner never "
                "clones (the AC3b escalation): point --map at an existing checkout.",
                file=sys.stderr,
            )
            return 2
        try:
            runs.append(_run_member(spec, checkout, snapshot_root))
        except (CorpusRefusal, PinnedSnapshotError) as exc:
            # PinUnreachable and PinnedBytesRefusal are refusals of exactly the same kind as
            # CorpusRefusal: a NAMED precondition the operator must act on. They are reported
            # with their type so "the pin is not in this checkout" and "the staged bytes are
            # not the pinned bytes" never collapse into one message.
            print(f"REFUSED — {type(exc).__name__}: {exc}", file=sys.stderr)
            return 2
        except Exception as exc:  # noqa: BLE001 - reported with its type, never swallowed
            print(f"AUDIT FAILED — {spec.member_id}: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 3

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1",
        "story": args.story,
        "supersedes": args.supersedes,
        "purpose": (
            "Adjudication-ready finding set for Story 13.2. Every finding carries the 6.6 "
            "finding_match_key identity and >=1 locator, and NO audited source byte (NFR-S1). "
            "The adjudication/adjudicator/rationale fields are NULL by design: classifying a "
            "finding TP or FP is the named human's act, and nothing here guesses at it."
        ),
        # Story 13.5 / AC1. The CORPUS-READ PROOF, at corpus level and per member. It exists
        # because this run's headline result is an ABSENCE, and an unread corpus reports the
        # same absence. Nothing downstream may treat a zero here as a measurement unless
        # `proves_corpus_was_read` holds for every member.
        "corpus_read_proof": corpus_read_proof(runs),
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
                # PROVENANCE (13.5): what the audited bytes were, proved rather than assumed.
                "checkout_head_sha": r.checkout_head_sha,
                "checkout_head_equals_pin": r.checkout_head_equals_pin,
                "dirty_in_scope_source_files": list(r.dirty_in_scope_source_files),
                "pin_verification": r.pin_verification.to_payload(),
                "corpus_read_proof": r.read_evidence.to_payload(),
                "findings": list(r.findings),
            }
            for r in runs
        ],
    }
    out = OUTPUT_DIR / args.output_name
    out.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    # The BLOCKING worklist. The full set is ~2 MB and is overwhelmingly advisory findings,
    # which are recorded but are NOT false accusations and do NOT enter the precision
    # denominator (protocol §4, as amended by Story 13.1). What Story 13.2's named human
    # actually has to judge is the blocking subset — so it gets its own small, readable file,
    # DERIVED from the same run rather than transcribed. A 2 MB JSON is a machine artifact;
    # a human adjudication list that nobody can read is an adjudication that does not happen.
    worklist = OUTPUT_DIR / (Path(args.output_name).stem.replace("adjudication-set", "blocking-worklist") + ".md")
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
            f"## {r.member_id} — {len(blocking)} blocking" + ("" if r.reproducible else "  ⛔ WITHHELD"),
            "",
            f"Pin `{r.pinned_sha}` · {r.primary_language} · {r.source_file_count} source files "
            f"· verdict `{r.verdict}` (exit {r.exit_code}) · deep {r.deep_ratio}",
            "",
        ]
        if not r.reproducible:
            # Code-review R3. Findings are WITHHELD for a non-reproducible member (correct —
            # protocol §4 makes reproducibility the precondition for adjudication). But the
            # empty list then rendered as "0 blocking / nothing to adjudicate", byte-identical
            # to a genuinely clean member, and was written to disk BEFORE the exit-2 fired. A
            # human reading the artifact rather than the process exit code was told the member
            # was clean. "Withheld" and "clean" are opposite facts and must never render alike.
            lines += [
                f"> ⛔ **FINDINGS WITHHELD — this member is NOT byte-reproducible.** Its two "
                f"runs disagreed, so protocol §4's determinism precondition is unmet and its "
                f"findings cannot be validly adjudicated. It reported "
                f"{r.blocking_finding_count} blocking / {r.total_finding_count} total findings "
                f"on the first run; those identities are deliberately ABSENT from this worklist "
                f"and from `adjudication-set.json`. **This is not a clean member.** Do not "
                f"adjudicate it and do not count it toward N until the run is reproducible.",
                "",
            ]
            continue
        if not blocking:
            lines += [
                "_No blocking finding, and this member IS byte-reproducible — genuinely nothing "
                "to adjudicate._",
                "",
            ]
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
    proof = corpus_read_proof(runs)
    print()
    print("corpus-read proof: " + str(proof["statement"]))
    if not proof["proves_corpus_was_read"]:
        print(
            "REFUSED — the corpus-read proof does NOT hold: pin_verified="
            f"{proof['every_member_pin_verified']}, "
            f"reproducible={proof['every_member_byte_reproducible']}, "
            f"scored_population_non_empty="
            f"{proof['every_member_scored_population_non_empty']}. This run's finding counts "
            "may NOT be read as a measurement — an unread corpus reports the same zero.",
            file=sys.stderr,
        )
        return 2

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
