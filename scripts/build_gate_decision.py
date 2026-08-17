"""Story 13.3 — compute protocol §5's four conditions and COMMIT the decision.

    python scripts/build_gate_decision.py [--check]

**This script cannot choose the answer.** It loads the committed adjudication record,
calls :func:`argus.precision.gate_decision.decide_gate` — which calls the existing
:func:`~argus.precision.adjudication.fold_adjudicated_precision` and authors no second
fold, no second threshold and no second arithmetic — and writes what comes back through
``argus.store.canonical``. Every figure on the artifact is derived: the ratio from the
shared arithmetic, the corpus from ``tests/corpus/_manifest.py``, the counts from the
record, the protocol version from the record cross-checked against the change-log head,
and the clean-repo blocking-FP count from a real fold of the cartridge corpus.

**The clean-repo condition is MEASURED here, not assumed** (Story 13.3 / AC2.2). Protocol
§5 as amended 2026-08-16 names this story: *"Story 13.3 must therefore evaluate this
condition against the cartridge corpus explicitly, or record it not-applicable — it may
not count it as met by default."* So this script stages and audits every cartridge through
the unmodified pipeline and folds the result through ``compute_precision``, which reports
``clean_repo_fp_applicable=True`` and NAMES the clean members it folded. That staging is
the impure test shell (§3.3) and is why it lives in a script rather than in ``argus/**``.

**What it refuses to do.** It never writes a disposition (only the named human may, and
``AdjudicationRow`` raises otherwise), never amends the protocol, never touches
``INSTRUMENT_STATUS`` or any disclosure surface, and never passes ``protocol_cleared=True``
anywhere. It writes exactly one file and it stages, commits, pushes, tags and publishes
nothing.

Exit codes, the ``scripts/audit_validation_corpus.py`` contract:

- **0** — the decision was written, or (``--check``) the committed artifact is current.
- **1** — ``--check`` and the committed artifact is STALE (the measurement moved).
- **2** — REFUSED: a precondition failed and is named on stderr.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:  # pragma: no cover - script bootstrap
    sys.path.insert(0, str(_REPO_ROOT))
_CARTRIDGES = _REPO_ROOT / "tests" / "cartridges"
if str(_CARTRIDGES) not in sys.path:  # pragma: no cover - script bootstrap
    sys.path.insert(0, str(_CARTRIDGES))

from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.precision.adjudication import (  # noqa: E402
    change_log_head_version,
    load_record,
    validation_set_population_n,
)
from argus.precision.gate_decision import (  # noqa: E402
    DECISION_RECORD_PATH,
    CleanRepoEvidence,
    GateDecision,
    decide_gate,
)
from argus.precision.gate_disclosure import ratified_corpus_members  # noqa: E402
from argus.precision.replay_harness import (  # noqa: E402
    compute_precision,
    finding_match_key,
    registry_module,
)
from argus.store.canonical import loads  # noqa: E402

_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_CORPUS_DIR = _ARTIFACTS / "validation-corpus"
_ADJUDICATION_SET = _CORPUS_DIR / "adjudication-set.json"
_RECORD = _CORPUS_DIR / "adjudication-record.json"
_PROTOCOL = _ARTIFACTS / "precision-validation-protocol.md"
_DECISION = _REPO_ROOT / DECISION_RECORD_PATH


class Refused(RuntimeError):
    """A named precondition failure — printed as ``REFUSED — ...`` with exit code 2."""


def _git(*args: str) -> str:
    """Run *git* in the repository root and return stdout. Never raises on a git failure."""
    completed = subprocess.run(  # noqa: S603 - fixed argv, no shell, no untrusted input
        ["git", *args],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip()


def measure_clean_repo_condition() -> CleanRepoEvidence:
    """Fold the CARTRIDGE corpus and read §5's clean-repo blocking-FP count off it.

    Uses the same staging + audit + ``compute_precision`` path the 6.6 guards use, so the
    number here is the number the suite measures rather than a second derivation of it. A
    staging or audit failure becomes a NAMED refusal (the ``AI-E5-1`` no-crash leg) — never
    a silent zero, which would read as "no false positives" when it means "nothing ran".
    """
    from _cartridge import stage_cartridge  # noqa: PLC0415 - repository-only, lazy

    registry = registry_module()
    emitted: dict[str, frozenset[tuple[str, bool, bool]]] = {}
    with tempfile.TemporaryDirectory() as scratch:
        for spec in registry.CARTRIDGE_REGISTRY:
            try:
                repo, _sha = stage_cartridge(
                    spec.cartridge_id, Path(scratch) / spec.cartridge_id
                )
                result = run_audit_detailed(
                    AuditRequest(
                        repo_path=str(repo),
                        commit="HEAD",
                        budget=100,
                        materiality_bar="default",
                    )
                )
            except Exception as exc:  # noqa: BLE001 - convert to a NAMED refusal
                raise Refused(
                    f"cartridge {spec.cartridge_id!r}: staging/audit failed "
                    f"({type(exc).__name__}: {exc}). §5's clean-repo condition cannot be "
                    f"reported met by a run that did not happen."
                ) from exc
            emitted[spec.cartridge_id] = frozenset(
                finding_match_key(finding) for finding in result.verdict.ordered_findings
            )
    if not emitted:
        raise Refused(
            "the cartridge registry folded ZERO members, so a clean-repo blocking-FP "
            "count of 0 would mean 'nothing ran', not 'nothing was falsely accused' "
            "(non-vacuity floor, AI-E11-1)."
        )
    folded = compute_precision(emitted)
    clean = tuple(sorted(row.cartridge_id for row in folded.rows if row.is_clean_repo))
    if not folded.clean_repo_fp_applicable or not clean:
        raise Refused(
            "the cartridge fold reports the clean-repo condition INAPPLICABLE — no member "
            "has an empty golden key with max_blocking == 0. §5's condition would then be "
            "unmeasurable over BOTH corpora, and it may not be counted met by default."
        )
    return CleanRepoEvidence(
        corpus=(
            f"the FR20 planted-defect cartridge corpus (tests/cartridges/_registry.py), "
            f"folded through compute_precision over {len(emitted)} member(s)"
        ),
        applicable=True,
        clean_repo_fp=int(folded.clean_repo_fp),
        clean_member_ids=clean,
        note=(
            "§5's clean-repo blocking-FP condition is evaluated HERE, over the cartridge "
            "corpus, because that is the only population where it can fail: "
            "_is_clean_repo requires an empty golden key AND max_blocking == 0, and no "
            "member of the REPOSITORY corpus that gates externalization has either — over "
            "that corpus the condition is satisfied by construction for every possible "
            "input and is recorded NOT APPLICABLE with its reason "
            "(AdjudicatedPrecision.clean_repo_fp_note), never as satisfied. A §5 condition "
            "that cannot fail is not a threshold (protocol §5 as amended 2026-08-16, "
            "Story 13.2 / AC1c, which names Story 13.3 by name)."
        ),
    )


def expected_finding_ids() -> tuple[str, ...]:
    """The EMITTED blocking-finding population, read off Story 13.1's adjudication set.

    Deliberately NOT ``[row.finding_id for row in record.rows]``. Deriving the expected
    population from the record itself makes exhaustiveness self-referential: a record can
    never be missing a row it does not contain, so the guard would report EXHAUSTIVE over
    whatever happened to be seeded and could not observe a finding the corpus emitted and
    nobody entered. The population is what the tool EMITTED; the record is what a human
    ruled on; exhaustiveness is the comparison between them, and it is only a comparison
    if the two sides come from different places.

    The identity is :attr:`~argus.precision.adjudication.AdjudicationRow.finding_id`'s,
    rebuilt from the set's own fields — the same coordinates, never a second scheme.
    """
    if not _ADJUDICATION_SET.is_file():
        raise Refused(
            f"the Story 13.1 adjudication set is absent at "
            f"{_ADJUDICATION_SET.relative_to(_REPO_ROOT).as_posix()}; without it the "
            f"emitted population is unknown and exhaustiveness would be measured against "
            f"the record itself, which cannot fail."
        )
    payload = loads(_ADJUDICATION_SET.read_text(encoding="utf-8"))
    ids: list[str] = []
    for member in payload["members"]:
        for finding in member["findings"]:
            if not finding["verdict_eligible"]:
                continue  # advisory over-emission is not a false ACCUSATION (DN-FP-DENOMINATOR)
            for locator in finding["locators"]:
                ids.append(
                    f"{member['member_id']}::{finding['rule_id']}::"
                    f"{finding['verdict_eligible']!r}::{finding['advisory']!r}::{locator}"
                )
    if not ids:
        raise Refused(
            "the adjudication set holds ZERO blocking findings, so the emitted population "
            "is empty and exhaustiveness over it would pass forever (AI-E11-1)."
        )
    return tuple(ids)


def build_decision(*, commit_sha: str, decided_on: str) -> GateDecision:
    """Load every input, measure what must be measured, and let :func:`decide_gate` decide."""
    if not _RECORD.is_file():
        raise Refused(
            f"the committed adjudication record is absent at "
            f"{_RECORD.relative_to(_REPO_ROOT).as_posix()}. Story 13.3 computes over an "
            f"adjudicated record and cannot begin without one. Re-run: python "
            f"scripts/build_adjudication_record.py"
        )
    if not _PROTOCOL.is_file():
        raise Refused(
            f"the validation protocol is absent at "
            f"{_PROTOCOL.relative_to(_REPO_ROOT).as_posix()}; its §5 IS the four "
            f"conditions this script computes."
        )
    record = load_record(_RECORD)
    head = change_log_head_version(_PROTOCOL.read_text(encoding="utf-8"))
    relative = _RECORD.relative_to(_REPO_ROOT).as_posix()
    tracked = bool(_git("ls-files", "--", relative))
    members = ratified_corpus_members()
    if not members:
        raise Refused(
            "the validation-set manifest reports ZERO eligible members, so the corpus the "
            "decision names would be empty (non-vacuity floor, AI-E11-1)."
        )
    return decide_gate(
        record,
        expected_finding_ids=expected_finding_ids(),
        population_n=validation_set_population_n(),
        floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
        protocol_change_log_head=head,
        clean_repo_evidence=measure_clean_repo_condition(),
        ratified_members=members,
        record_is_tracked_in_git=tracked,
        commit_sha=commit_sha,
        decided_on=decided_on,
        record_path=relative,
        protocol_path=_PROTOCOL.relative_to(_REPO_ROOT).as_posix(),
    )


def _provenance(check_only: bool) -> tuple[str, str]:
    """``(commit_sha, decided_on)`` — carried over from the committed artifact on ``--check``.

    ``--check`` must be able to answer *"has the MEASUREMENT moved?"* and nothing else. The
    sha and the date are provenance, not measurement: re-deriving them would make the
    committed artifact stale on the very next commit and on the following day, and a check
    that is red for a reason nobody can fix is a check people learn to ignore.
    """
    if check_only and _DECISION.is_file():
        payload = loads(_DECISION.read_text(encoding="utf-8"))
        return str(payload["commit_sha"]), str(payload["decided_on"])
    return _git("rev-parse", "HEAD") or "NO_VCS", date.today().isoformat()


def build(*, check_only: bool) -> int:
    commit_sha, decided_on = _provenance(check_only)
    decision = build_decision(commit_sha=commit_sha, decided_on=decided_on)
    text = decision.to_text()
    if check_only:
        if not _DECISION.is_file():
            print(
                f"STALE — {_DECISION.relative_to(_REPO_ROOT).as_posix()} does not exist. "
                f"Run: python scripts/build_gate_decision.py",
                file=sys.stderr,
            )
            return 1
        # NEWLINE-NORMALIZED on purpose. The canonical serializer emits LF and exactly one
        # trailing newline, but this repository has no `.gitattributes` and `core.autocrlf`
        # is true on the Windows machine the local gates run on, so a fresh checkout hands
        # back CRLF while CI's ubuntu matrix hands back LF. A staleness check that is red
        # for a checkout reason nobody can fix is a check people learn to ignore; the
        # NO-CARRIAGE-RETURN property of the produced bytes is asserted at its own seam by
        # TC-ArgusAgent-PRECISION-001-61 instead.
        if _DECISION.read_text(encoding="utf-8").replace("\r\n", "\n") != text:
            print(
                f"STALE — {_DECISION.relative_to(_REPO_ROOT).as_posix()} no longer equals "
                f"the re-derived decision. The measurement moved. Re-run: python "
                f"scripts/build_gate_decision.py",
                file=sys.stderr,
            )
            return 1
        print(f"CURRENT — {decision.outcome} ({decision.fold.precision_ratio})")
        return 0
    _DECISION.parent.mkdir(parents=True, exist_ok=True)
    _DECISION.write_text(text, encoding="utf-8", newline="\n")
    print(f"WROTE {_DECISION.relative_to(_REPO_ROOT).as_posix()}")
    print(f"  outcome        : {decision.outcome}")
    print(f"  reason         : {decision.outcome_reason}")
    for condition in decision.conditions:
        print(f"  §5 {condition.condition_id:<45} {condition.verdict}")
    print(f"  concentration  : {decision.concentration.statement}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="re-derive and compare against the committed artifact; write nothing",
    )
    args = parser.parse_args(argv)
    try:
        return build(check_only=args.check)
    except Refused as refusal:
        print(f"REFUSED — {refusal}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - script entry point
    raise SystemExit(main())
