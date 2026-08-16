"""Story 13.2 — seed / re-seed the committed adjudication record from the 13.1 corpus.

    python scripts/build_adjudication_record.py [--check]

**This script cannot adjudicate anything, and that is its main design constraint.** It
seeds one ``UNADJUDICATED`` row per emitted BLOCKING finding in
``validation-corpus/adjudication-set.json`` (Story 13.1 / AC3b) and writes them through
:class:`argus.precision.adjudication.AdjudicationRecord`, which RAISES if a row that is not
a human judgement carries an adjudicator id. So the failure mode where an automated
producer starts filling in the named human's judgements is a construction-time error, not
something a reviewer has to notice.

**Append-only, mechanically.** An existing record is LOADED, and only findings that carry
no row at all are appended. A human's disposition is never read back, rewritten, or
re-seeded — re-running this after an adjudication is a no-op over the judged rows. The
exit contract is the ``scripts/audit_validation_corpus.py`` one:

- **0** — the record is current (``--check``) or was written.
- **2** — REFUSED: a precondition failed and is named on stderr.

Blocking vs advisory: only ``verdict_eligible`` findings enter the record, because only a
blocking finding is a false ACCUSATION and only those are in the precision denominator
(protocol §4 as amended by 13.1; ``compute_precision`` counts an FP only when
``key[1]`` is True). The 5987 advisory findings stay in the adjudication set, recorded and
out of the denominator.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:  # pragma: no cover - script bootstrap
    sys.path.insert(0, str(_REPO_ROOT))

from argus.precision.adjudication import (  # noqa: E402
    ADJUDICATION_UNIT,
    AdjudicationRecord,
    AdjudicationRow,
    change_log_head_version,
    finding_row_id,
    load_record,
)
from argus.store.canonical import loads  # noqa: E402

_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_CORPUS_DIR = _ARTIFACTS / "validation-corpus"
_ADJUDICATION_SET = _CORPUS_DIR / "adjudication-set.json"
_RECORD = _CORPUS_DIR / "adjudication-record.json"
_PROTOCOL = _ARTIFACTS / "precision-validation-protocol.md"

_EXPERT_HOURS_NOTE = (
    "NOT RECORDED — no adjudication run has taken place. Story 13.2 delivered the "
    "instrument (AC1-AC6, AC8) and escalated AC7: the TP/FP judgement is the named "
    "human's act (protocol §2 Engineering Lead, XAgent007) and no agent may supply it. "
    "The actual hours are recorded here by the adjudicator when the run happens, and are "
    "compared against protocol §3's <= 4 expert-hour ceiling AS A REPORT, never as a gate."
)


class Refused(RuntimeError):
    """A named precondition failure — printed as ``REFUSED — ...`` with exit code 2."""


def _blocking_findings(payload: dict) -> tuple[tuple[str, dict], ...]:
    """Every BLOCKING finding in the adjudication set, as ``(member_id, finding)``.

    Non-vacuity is the caller's job and it is not optional: an empty return here means the
    corpus could not be read, and seeding an empty record would make every downstream
    exhaustiveness guard pass forever.
    """
    out: list[tuple[str, dict]] = []
    for member in payload["members"]:
        for finding in member["findings"]:
            if finding["verdict_eligible"]:
                out.append((member["member_id"], finding))
    return tuple(out)


def _seed_rows(pairs: tuple[tuple[str, dict], ...]) -> tuple[AdjudicationRow, ...]:
    rows: list[AdjudicationRow] = []
    for member_id, finding in pairs:
        locators = finding["locators"]
        if not locators:
            raise Refused(
                f"{member_id}: a blocking finding for rule {finding['rule_id']!r} carries "
                f"NO locator. FR13 requires >=1 verifiable locator, and protocol §4's "
                f"borderline ladder re-examines exactly that locator — a finding without "
                f"one cannot be adjudicated at all."
            )
        # ONE row per (finding, locator): the unit is the FINDING (protocol §7 / AC2), and
        # a finding reported at two locators is two things a human must look at.
        for locator in locators:
            rows.append(
                AdjudicationRow(
                    row_id=finding_row_id(
                        member_id=member_id,
                        rule_id=finding["rule_id"],
                        verdict_eligible=finding["verdict_eligible"],
                        advisory=finding["advisory"],
                        locator=locator,
                    ),
                    member_id=member_id,
                    rule_id=finding["rule_id"],
                    verdict_eligible=finding["verdict_eligible"],
                    advisory=finding["advisory"],
                    locator=locator,
                    disposition="UNADJUDICATED",
                )
            )
    return tuple(rows)


def build(*, check_only: bool) -> int:
    if not _ADJUDICATION_SET.is_file():
        raise Refused(
            f"the Story 13.1 adjudication set is absent at "
            f"{_ADJUDICATION_SET.relative_to(_REPO_ROOT).as_posix()}. 13.2 measures the "
            f"corpus 13.1 built; it does not re-derive or re-ratify it."
        )
    payload = loads(_ADJUDICATION_SET.read_text(encoding="utf-8"))
    pairs = _blocking_findings(payload)
    if not pairs:
        raise Refused(
            "the adjudication set carries ZERO blocking findings. That is either an "
            "empty corpus or an unreadable one, and seeding an empty adjudication record "
            "would make every exhaustiveness guard downstream pass forever (AI-E11-1)."
        )
    reproducible = all(
        bool(member["byte_reproducible_across_two_runs"]) for member in payload["members"]
    )
    non_repro = tuple(
        member["member_id"]
        for member in payload["members"]
        if not member["byte_reproducible_across_two_runs"]
    )
    protocol_version = change_log_head_version(_PROTOCOL.read_text(encoding="utf-8"))

    seeded = _seed_rows(pairs)
    if _RECORD.is_file():
        existing = load_record(_RECORD)
        known = {row.finding_id for row in existing.rows}
        new_rows = tuple(row for row in seeded if row.finding_id not in known)
        # APPEND-ONLY: existing rows — including every human judgement — are carried
        # through byte-identically. Only the derived header fields track the substrate.
        record = AdjudicationRecord(
            protocol_version=protocol_version,
            adjudication_unit=ADJUDICATION_UNIT,
            corpus_source=existing.corpus_source,
            reproducibility_verified=reproducible,
            reproducibility_source=_reproducibility_sentence(payload, non_repro),
            expert_hours=existing.expert_hours,
            expert_hours_note=existing.expert_hours_note,
            rows=existing.rows,
        ).append(new_rows)
    else:
        record = AdjudicationRecord(
            protocol_version=protocol_version,
            adjudication_unit=ADJUDICATION_UNIT,
            corpus_source=(
                "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/"
                "adjudication-set.json (Story 13.1 / AC3b, operator-ratified 2026-08-16)"
            ),
            reproducibility_verified=reproducible,
            reproducibility_source=_reproducibility_sentence(payload, non_repro),
            expert_hours=None,
            expert_hours_note=_EXPERT_HOURS_NOTE,
            rows=seeded,
        )

    text = record.to_text()
    if check_only:
        current = _RECORD.read_text(encoding="utf-8") if _RECORD.is_file() else ""
        if current != text:
            raise Refused(
                f"{_RECORD.relative_to(_REPO_ROOT).as_posix()} is NOT current against "
                f"{_ADJUDICATION_SET.name}. Re-run: python "
                f"scripts/build_adjudication_record.py"
            )
        print(f"OK — the adjudication record is current ({len(record.rows)} row(s)).")
        return 0
    _RECORD.write_text(text, encoding="utf-8", newline="\n")
    tally = record.counts()
    print(
        f"WROTE {_RECORD.relative_to(_REPO_ROOT).as_posix()} — {len(record.rows)} row(s); "
        f"live: " + ", ".join(f"{k}={v}" for k, v in sorted(tally.items()))
    )
    print(f"protocol_version={record.protocol_version} reproducible={reproducible}")
    print(
        "NOTHING IS ADJUDICATED. Every row is UNADJUDICATED and carries no adjudicator — "
        "the TP/FP judgement is the named human's act (protocol §2)."
    )
    return 0


def _reproducibility_sentence(payload: dict, non_repro: tuple[str, ...]) -> str:
    """Name the EXISTING check whose result this is — never a second check (AC6)."""
    members = len(payload["members"])
    base = (
        f"scripts/audit_validation_corpus.py (Story 13.1) audited each member twice at its "
        f"pinned sha and compared the runs byte-for-byte; the per-member result is carried "
        f"on adjudication-set.json as byte_reproducible_across_two_runs. Measured: "
        f"{members - len(non_repro)}/{members} member(s) byte-reproducible"
    )
    if non_repro:
        return f"{base}. NOT reproducible: {', '.join(sorted(non_repro))}"
    return f"{base} — the NFR-P1 precondition of protocol §4 holds over the whole corpus"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed record is current; write nothing",
    )
    args = parser.parse_args(argv)
    try:
        return build(check_only=args.check)
    except Refused as exc:
        print(f"REFUSED — {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
