"""Assemble the protocol §6 R2 ratification package for the SEALED bench partition.

**Story 19.1.** This is the *input* to an operator act, and it is emphatically not the act.
Protocol §6 R2 is verbatim: *"choosing which repositories are legitimate members, and fetching
third-party source, are not autonomous acts."* Story 19.2 is that act. This script assembles the
evidence the operator needs in order to take it, writes it down, and **stops**.

**What it does**

1. Reads the six ``sealed`` rows of :data:`tests.corpus._manifest.SEALED_PARTITION_TABLE` and
   carries their manifest fields **verbatim**. It re-derives none of them. ``repository_url``,
   ``commit_sha``, ``licence`` (with its tracked-at-the-pin evidence), ``primary_language``,
   ``provenance``, ``eligible_for_n``, ``ineligible_reason`` and ``adjudication_caveat`` are
   already recorded, for all six, and a second derivation of a recorded fact is the AR7 / ``DN-3``
   / ``DF-8-5-C`` defect this repository has filed against itself three times.
2. Measures the two columns nobody has recorded — ``files_at_pin`` and ``python_files_at_pin`` —
   through the shipped ``pinned_corpus_snapshot`` helpers (``pin_is_reachable`` +
   ``pinned_tree``), which read the git object database at the pin. ``build_silent_class_record``
   already reads its trees this way; this is the same derivation, not a new one.
3. Records ``heuristic_findings_at_pin`` as **UNMEASURED with its measured reason** — see
   :data:`FINDING_COUNT_UNMEASURED_REASON`, which is the central finding of this story.

**What it refuses to do**

* **It never reaches the network.** The six checkouts were fetched by the operator during Story
  15.1 and are already on disk; reading source an operator already fetched is not fetching. A
  member whose checkout is absent, or whose pin is unreachable, is recorded ``UNMEASURED`` with
  the reason and is **not repaired and not dropped** (``POPULATION_DERIVATION``: a member that
  contributes nothing is a member the ratio was measured over). This ban is asserted structurally
  over this module's AST by ``TC-ArgusAgent-PRECISION-001-153``, not promised in this docstring.
* **It ratifies nothing.** No ``eligible_for_n`` is written, and the record carries
  ``eligible_member_count`` before and after so that a run which moved it is visible rather than
  silent.
* **It recommends nothing.** There is no ``recommended``, ``admit``, ``score`` or ``rank`` field
  and no ordering by desirability. §6 R2 reserves *"choosing which repositories are legitimate
  members"* to the operator, and a worksheet that ranks has made the choice and left the operator
  a rubber stamp.

Exit codes: ``0`` the record was written (or, under ``--check``, matches the committed record) ·
``2`` a refusal the operator must act on.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from pinned_corpus_snapshot import (  # noqa: E402
    PinnedSnapshotError,
    pin_is_reachable,
    pinned_tree,
)

from tests.corpus._manifest import (  # noqa: E402
    MANIFEST_FIELDS,
    SEALED_PARTITION_TABLE,
    VALIDATION_CORPUS,
    eligible_member_count,
)

#: Repository-relative home of the record and its worklist.
#:
#: ⛔ **The directory is `ratification/`, and the names match NEITHER ``sprint-change-proposal-*.md``
#: NOR ``epic-*-retro-*.md``.** ``TC-ArgusAgent-DOCS-001-22`` fires on a file matching either glob
#: that is not registered in its index; a worklist named into one of those families would RED a
#: guard this story never touched. ``blocking-worklist.md`` and ``silent-class-worklist.md``
#: already sit outside both, and this follows them.
RATIFICATION_DIR = "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/ratification"
RATIFICATION_RECORD_PATH = f"{RATIFICATION_DIR}/ratification-record.json"
RATIFICATION_WORKLIST_PATH = f"{RATIFICATION_DIR}/ratification-worklist.md"

SCHEMA_VERSION = 1

#: The manifest fields carried into every row VERBATIM. Deliberately derived from
#: :data:`MANIFEST_FIELDS` minus the key rather than retyped: the manifest schema is CLOSED and
#: ``TC-ArgusAgent-DOCS-001-22`` checks it in both directions, so a field added there must either
#: appear here or be a deliberate exclusion — never a silent omission.
CARRIED_MANIFEST_FIELDS: tuple[str, ...] = tuple(
    field for field in MANIFEST_FIELDS if field != "member_id"
)

#: The columns this script MEASURES, as opposed to carries.
MEASURED_FIELDS: tuple[str, ...] = (
    "checkout_path",
    "pin_reachable",
    "files_at_pin",
    "python_files_at_pin",
    "heuristic_findings_at_pin",
)

#: ⛔ Field-name substrings that would turn this worksheet into a recommendation (AC1.5). The
#: guard asserts no row key contains any of them. Named here rather than in the test so the ban
#: travels with the producer that must not breach it.
RECOMMENDATION_SUBSTRINGS: tuple[str, ...] = (
    "recommend",
    "admit",
    "score",
    "rank",
    "prefer",
    "best",
    "star",
    "popular",
    "download",
)

#: ⛔⛔ **THE CENTRAL MEASURED FINDING OF STORY 19.1.**
#:
#: The story chartered this record on the premise that ``scripts/audit_validation_corpus.py`` is
#: the one producer of the finding count and merely needed to be invoked. **It is the one
#: producer, and it structurally refuses every sealed member.** Its ``main()`` folds over
#: ``manifest.eligible_members()``, which is ``tuple(spec for spec in VALIDATION_CORPUS if
#: spec.eligible_for_n)``; all six sealed candidates carry ``eligible_for_n = False`` with
#: ``ineligible_reason = "candidate - awaiting operator ratification (protocol section 6 R2)"``.
#: Selecting them yields an empty member list and the runner exits ``REFUSED — no eligible members
#: selected`` with code ``2``. Measured, not inferred — the command and its output are in the
#: record's ``derivation_sources``.
#:
#: ⛔ **This is a MOAT, not a defect, and it must not be "fixed".** The three ways to obtain the
#: number are (a) flip ``eligible_for_n`` — that IS the §6 R2 operator act, (b) write a second
#: walker — barred by AR7 / ``DN-3`` and by this story's own AC4.1, (c) widen the runner to audit
#: unratified repositories — which would delete the refusal that keeps corpus-shopping
#: unexpressible. All three are refused here.
FINDING_COUNT_UNMEASURED_REASON = (
    "UNMEASURABLE-BEFORE-RATIFICATION. The one producer of this column, "
    "scripts/audit_validation_corpus.py, folds over manifest.eligible_members(), which selects "
    "only members carrying eligible_for_n = True. All six sealed members carry "
    "eligible_for_n = False with ineligible_reason 'candidate - awaiting operator ratification "
    "(protocol section 6 R2)', so the runner selects none of them and exits 'REFUSED - no "
    "eligible members selected' (exit 2). Obtaining this number would require flipping "
    "eligible_for_n (which IS the R2 operator act this record exists to inform), writing a "
    "second walker (barred by AR7/DN-3 and by story 19.1 AC4.1), or widening the runner to audit "
    "unratified repositories (which would remove the refusal that makes corpus-shopping "
    "unexpressible). All three are refused. The column is therefore reported UNMEASURED with "
    "this reason rather than estimated, and the member is NOT dropped from the population."
)

#: ⛔ **WHAT ``files_at_pin`` COUNTS, because a row moved on exactly this distinction.**
#:
#: ``pinned_tree`` keeps ``blob`` entries and drops ``commit`` (submodule gitlink) and ``tree``
#: entries. Story 19.1's §0.1 recorded ``getsentry-sentry-python`` at **639** files, measured with
#: a raw ``git ls-tree -r --name-only | wc -l``; this record says **638**. Both numbers are
#: correct about different questions, and the difference is one submodule gitlink at the pin:
#: ``160000 commit 6d2c435b8ce3a67e2065f38374bb437f274d0a6c  checkouts/data-schemas``. A gitlink
#: is a POINTER to a commit in another repository, not a file, and its content is not present in
#: this checkout at all. ⛔ Counting it as a file would have overstated the auditable surface of
#: the only sealed member that has one.
FILE_COUNT_SEMANTICS = (
    "files_at_pin counts BLOB entries at the pinned commit (git ls-tree -r), via the shipped "
    "pinned_corpus_snapshot.pinned_tree helper. Submodule gitlinks (mode 160000, type commit) and "
    "tree entries are NOT counted: a gitlink is a pointer to a commit in another repository, not "
    "a file, and its bytes are not present in this checkout. This matters for exactly one sealed "
    "member: getsentry-sentry-python carries one gitlink (checkouts/data-schemas) at its pin, so "
    "a raw entry count reports 639 where the blob count reports 638. The blob count is the one "
    "recorded here."
)

#: ⛔ The sequencing consequence, stated in the record's own fields so the operator meets it
#: before the rows rather than after them. It is an OBSERVATION, not a recommendation: it does
#: not say what to do about the circularity, because that is the operator's ruling.
SEQUENCING_OBSERVATION = (
    "OBSERVATION, NOT A RECOMMENDATION. Story 19.1 was chartered to put a heuristic finding "
    "count in front of the operator BEFORE the R2 ratification of story 19.2. Measurement shows "
    "that count cannot exist before that ratification: the instrument that produces it refuses "
    "unratified members by construction (see finding_count_unmeasured_reason). The R2 judgement "
    "is therefore available on twelve of the thirteen columns and not on the thirteenth, and "
    "whether that is sufficient to rule on is the operator's decision and is NOT taken here. "
    "This record neither argues for ratification nor against it."
)

#: ⛔ What this record does NOT touch, named so that silence is not read as coverage.
SCOPE_DISCLAIMER = (
    "This record ratifies nothing, fetches nothing, adjudicates nothing and spends no round. "
    "DF-13-5-A stays OPEN and UNSPENT. The protocol §2 External adjudicator stays UNFILLED "
    "(AI-E17-8), which is what blocks story 19.4 and is not addressed here. The gate stays "
    "BLOCKED and protocol_cleared stays False. No finding is judged TP or FP: a population size "
    "is not a yield forecast."
)


@dataclass(frozen=True)
class RatificationRow:
    """One sealed member's evidence. Carried fields verbatim, measured fields measured."""

    member_id: str
    carried: dict[str, Any]
    measured: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {"member_id": self.member_id, **self.carried, **self.measured}


def sealed_member_ids() -> tuple[str, ...]:
    """The ``sealed`` partition, in table order. A fold over the table, never a transcription."""
    return tuple(mid for mid, status in SEALED_PARTITION_TABLE if status == "sealed")


def _spec_by_id() -> dict[str, Any]:
    return {spec.member_id: spec for spec in VALIDATION_CORPUS}


def _carried_fields(spec: Any) -> dict[str, Any]:
    """Every manifest field except the key, read off the spec. No lookup, no re-derivation."""
    return {field: getattr(spec, field) for field in CARRIED_MANIFEST_FIELDS}


def _measure(checkout: Path, commit_sha: str) -> dict[str, Any]:
    """The two measurable columns, through the shipped pinned-tree helpers.

    Every failure is a NAMED ``UNMEASURED`` with its reason. ⛔ Nothing here clones, pulls or
    fetches to repair a missing checkout or an unreachable pin: that is the AC6.1 escalation and
    the answer to it is to record the member, not to go and get it.
    """
    if not (checkout / ".git").exists():
        return {
            "checkout_path": checkout.as_posix(),
            "pin_reachable": False,
            "files_at_pin": "UNMEASURED",
            "python_files_at_pin": "UNMEASURED",
            "unmeasured_reason": (
                f"no git checkout at {checkout}. This script never clones (protocol §6 R2): "
                f"the member is recorded UNMEASURED and kept in the population."
            ),
        }
    if not pin_is_reachable(checkout, commit_sha):
        return {
            "checkout_path": checkout.as_posix(),
            "pin_reachable": False,
            "files_at_pin": "UNMEASURED",
            "python_files_at_pin": "UNMEASURED",
            "unmeasured_reason": (
                f"the pinned commit {commit_sha} is not in this checkout's object database. "
                f"NOT repaired by fetching: that is an operator act."
            ),
        }
    try:
        tree = pinned_tree(checkout, commit_sha, keep=lambda _path: True)
    except PinnedSnapshotError as exc:  # a NAMED refusal, never a degraded pass
        return {
            "checkout_path": checkout.as_posix(),
            "pin_reachable": True,
            "files_at_pin": "UNMEASURED",
            "python_files_at_pin": "UNMEASURED",
            "unmeasured_reason": f"{type(exc).__name__}: {exc}",
        }
    paths = tree.paths
    return {
        "checkout_path": checkout.as_posix(),
        "pin_reachable": True,
        "files_at_pin": len(paths),
        "python_files_at_pin": sum(1 for path in paths if path.endswith(".py")),
    }


def build_rows(checkout_root: Path, overrides: dict[str, str]) -> tuple[RatificationRow, ...]:
    """One row per sealed member, in table order. ⛔ No member is ever dropped (§1.3)."""
    specs = _spec_by_id()
    rows: list[RatificationRow] = []
    for member_id in sealed_member_ids():
        spec = specs.get(member_id)
        if spec is None:
            rows.append(
                RatificationRow(
                    member_id=member_id,
                    carried={field: "UNMEASURED" for field in CARRIED_MANIFEST_FIELDS},
                    measured={
                        "checkout_path": "UNMEASURED",
                        "pin_reachable": False,
                        "files_at_pin": "UNMEASURED",
                        "python_files_at_pin": "UNMEASURED",
                        "heuristic_findings_at_pin": "UNMEASURED",
                        "unmeasured_reason": (
                            f"{member_id} is in SEALED_PARTITION_TABLE but not in "
                            f"VALIDATION_CORPUS. Recorded, not dropped."
                        ),
                    },
                )
            )
            continue
        checkout = checkout_root / overrides.get(member_id, member_id)
        measured = _measure(checkout, spec.commit_sha)
        measured["heuristic_findings_at_pin"] = "UNMEASURED"
        rows.append(
            RatificationRow(
                member_id=member_id,
                carried=_carried_fields(spec),
                measured=measured,
            )
        )
    return tuple(rows)


def build_record(rows: tuple[RatificationRow, ...], count_before: int, count_after: int) -> dict:
    """The closed record. Provenance and boundary statements are FIELDS, never prose only."""
    ratified = set(sealed_member_ids()) & {
        spec.member_id for spec in VALIDATION_CORPUS if spec.eligible_for_n
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "story": "19.1",
        "record_kind": "ratification-evidence-package",
        "ratifies_nothing": True,
        "recommends_nothing": True,
        "adjudicates_nothing": True,
        "scope_disclaimer": SCOPE_DISCLAIMER,
        "sequencing_observation": SEQUENCING_OBSERVATION,
        "eligible_member_count_before": count_before,
        "eligible_member_count_after": count_after,
        "eligible_for_n_moved_for": [],
        "sealed_ratified_intersection": sorted(ratified),
        "row_count": len(rows),
        "carried_fields": list(CARRIED_MANIFEST_FIELDS),
        "measured_fields": list(MEASURED_FIELDS),
        "finding_count_status": "UNMEASURED",
        "finding_count_unmeasured_reason": FINDING_COUNT_UNMEASURED_REASON,
        "file_count_semantics": FILE_COUNT_SEMANTICS,
        "derivation_sources": {
            "carried_fields": "tests/corpus/_manifest.py::VALIDATION_CORPUS (read verbatim)",
            "pin_reachable": "scripts/pinned_corpus_snapshot.py::pin_is_reachable",
            "files_at_pin": "scripts/pinned_corpus_snapshot.py::pinned_tree (git ls-tree -r)",
            "python_files_at_pin": "scripts/pinned_corpus_snapshot.py::pinned_tree",
            "heuristic_findings_at_pin": (
                "scripts/audit_validation_corpus.py — REFUSED for every sealed member; see "
                "finding_count_unmeasured_reason"
            ),
        },
        "rows": [row.as_dict() for row in rows],
    }


def render_worklist(record: dict) -> str:
    """The human worklist, in the ``blocking-worklist.md`` house form (AC1.3)."""
    lines: list[str] = [
        "# Ratification worklist — the SEALED bench partition (protocol §6 R2)",
        "",
        "> ⛔ **THIS DOCUMENT RATIFIES NOTHING AND RECOMMENDS NOTHING.** It is the evidence",
        "> package for the operator act filed as Story 19.2. Produced by",
        "> `scripts/build_ratification_record.py` from",
        f"> `{RATIFICATION_RECORD_PATH}`.",
        "",
        f"**Rows:** {record['row_count']} · "
        f"**`eligible_member_count()`:** {record['eligible_member_count_before']} before, "
        f"{record['eligible_member_count_after']} after · "
        f"**sealed ∩ ratified:** `{record['sealed_ratified_intersection'] or '[]'}`",
        "",
        "## ⛔ Read this before the table",
        "",
        record["sequencing_observation"],
        "",
        "**Why the finding-count column is empty:**",
        "",
        record["finding_count_unmeasured_reason"],
        "",
        "## The members",
        "",
        "| member | pin | licence | files @ pin | `.py` @ pin | findings @ pin |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in record["rows"]:
        lines.append(
            f"| `{row['member_id']}` "
            f"| `{str(row['commit_sha'])[:12]}` "
            f"| {row['licence']} "
            f"| {row['files_at_pin']} "
            f"| {row['python_files_at_pin']} "
            f"| {row['heuristic_findings_at_pin']} |"
        )
    lines += [
        "",
        "## What each member says about itself",
        "",
        "⛔ Read verbatim from the manifest's `adjudication_caveat`. Not re-derived, not summarised.",
        "",
    ]
    for row in record["rows"]:
        lines += [
            f"### `{row['member_id']}`",
            "",
            f"- **Repository:** {row['repository_url']}",
            f"- **Pin:** `{row['commit_sha']}`",
            f"- **Provenance:** {row['provenance']} · **Language:** {row['primary_language']}",
            f"- **`eligible_for_n`:** `{row['eligible_for_n']}` — {row['ineligible_reason']}",
            f"- **Caveat:** {row['adjudication_caveat']}",
            "",
        ]
    lines += ["## Scope", "", record["scope_disclaimer"], ""]
    return "\n".join(lines)


def _write(path: Path, text: str) -> None:
    """UTF-8, LF, trailing newline — the house invariant for generated artifacts.

    ⛔ ``newline=""`` so Python's universal-newline translation cannot silently rewrite every
    line ending on Windows. ``deferred-work.md`` is LF-uniform with ONE deliberate lone CR, and
    an artifact writer that "normalised" endings would be indistinguishable from a real edit.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assemble the protocol §6 R2 ratification evidence package (story 19.1).",
    )
    parser.add_argument(
        "--checkout-root",
        help=(
            "Directory containing the sealed checkouts, resolved per member by --map. "
            "⛔ A command-line argument, never a constant: committed code carries no drive "
            "letter and no machine-specific path (AC5.4)."
        ),
    )
    parser.add_argument(
        "--map",
        action="append",
        default=[],
        metavar="MEMBER_ID=RELATIVE_PATH",
        help="Checkout directory for a member whose name differs from its member_id.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Verify the COMMITTED record against the manifest and exit. Reads no corpus, so it "
            "is green on a fresh clone with no checkouts present."
        ),
    )
    args = parser.parse_args(argv)

    record_path = _REPO_ROOT / RATIFICATION_RECORD_PATH

    if args.check:
        if not record_path.exists():
            print(f"REFUSED — no committed record at {RATIFICATION_RECORD_PATH}", file=sys.stderr)
            return 2
        record = json.loads(record_path.read_text(encoding="utf-8"))
        expected = list(sealed_member_ids())
        actual = [row["member_id"] for row in record["rows"]]
        if actual != expected:
            print(f"REFUSED — rows {actual} != sealed partition {expected}", file=sys.stderr)
            return 2
        if record["eligible_member_count_after"] != eligible_member_count():
            print(
                f"REFUSED — record says eligible_member_count "
                f"{record['eligible_member_count_after']}, manifest says "
                f"{eligible_member_count()}. An operator act may have been performed.",
                file=sys.stderr,
            )
            return 2
        print(f"OK — {len(actual)} rows, eligible_member_count {eligible_member_count()}")
        return 0

    if not args.checkout_root:
        print("REFUSED — --checkout-root is required unless --check is given", file=sys.stderr)
        return 2

    overrides: dict[str, str] = {}
    for pair in args.map:
        member_id, sep, rel = pair.partition("=")
        if not sep or not member_id.strip() or not rel.strip():
            print(f"REFUSED — --map {pair!r} is not MEMBER_ID=RELATIVE_PATH", file=sys.stderr)
            return 2
        if Path(rel.strip()).is_absolute():
            print(f"REFUSED — --map {pair!r} names an ABSOLUTE path", file=sys.stderr)
            return 2
        overrides[member_id.strip()] = rel.strip()

    count_before = eligible_member_count()
    rows = build_rows(Path(args.checkout_root), overrides)
    count_after = eligible_member_count()

    if count_after != count_before:
        print(
            f"REFUSED — eligible_member_count moved {count_before} -> {count_after} during the "
            f"run. An operator act has been performed by accident (story 19.1 AC6.2).",
            file=sys.stderr,
        )
        return 2

    record = build_record(rows, count_before, count_after)
    _write(record_path, json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    _write(_REPO_ROOT / RATIFICATION_WORKLIST_PATH, render_worklist(record))
    print(f"wrote {RATIFICATION_RECORD_PATH} ({record['row_count']} rows)")
    print(f"wrote {RATIFICATION_WORKLIST_PATH}")
    print(f"eligible_member_count: {count_before} before, {count_after} after — unmoved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
