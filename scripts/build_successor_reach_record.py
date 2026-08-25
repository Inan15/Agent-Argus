"""Story 17.4 — measure S1 over the pinned corpus ONCE, and fold it through the frozen criterion.

    python scripts/build_successor_reach_record.py --check
    python scripts/build_successor_reach_record.py \\
        --checkout-root d:/ProjectX/XAgents/XAgents --snapshot-root c:/t/ar174

**This script measures a number that did not exist when the standard it is judged against was
written, and that ORDER is the whole point.** Story 17.1 froze
``scripts/precision_preregistration.py`` in commit ``f906d04`` while the verdict-eligible
population of every candidate successor was still zero. Story 17.2 specified ``S1`` and refused to
publish its reach. Story 17.3 built ``S1`` and still refused. This script runs the measurement
once, hands the counts to ``precision_preregistration.evaluate()`` **unmodified**, and records
whatever comes back — including ``UNEVALUABLE``, which is a RESULT and not a thing to repair.

**It cannot move the bar, and that is structural rather than promised.** It imports the criterion
and never writes to it. There is no story-local threshold, no ``--floor`` option, no fourth
terminal state, and no code path that reaches a different outcome by supplying different floors:
:func:`successor_reach_model.fold` passes neither ``floors=`` nor ``ratio_floor=``.

**It re-derives no conjunct of ``S1``.** The predicate comes from the ONE shipped public entry
point Story 17.3 made public for exactly this consumer —
:meth:`argus.detectors.vacuous_test.VacuousTestDetector.successor_evidence`, itself
composition-only over ``assertion_strength.s1_corroborated`` and ``grade_span_assertions``. Neither
this module nor ``scripts/successor_reach_model.py`` imports ``ast``, re-parses a source, calls a
second grammar, or re-implements fact (a), fact (b′), the band grading, the statement boundary or
the SUT-derived-name resolution; the research resolver ``research/investigate-per-call-scoping.py``
is NOT ported. ``TC-ArgusAgent-PRECISION-001-151`` walks both modules and reds on a second
derivation.

**It adjudicates NOTHING, and is structurally incapable of doing so.** Protocol §2 registers
``UNADJUDICATED`` as the ONLY disposition an automated producer may write, and protocol §4's
borderline ladder has no third rung — ``AI-E16-7`` is UNFILLED. The only reachable row constructor,
``successor_reach_model.seed_successor_row``, has no parameter for a disposition, an adjudicator, a
date or a reason. So the fold sees ``true_positive_count=0`` and ``false_accusation_count=0``, and
its own step (2) answers the empty denominator. ⛔ That answer is recorded VERBATIM with its
reason: never rewritten as a flattering ``100%``, never as ``0%``, and never omitted with the
population implied to be fine. The measured precedent for that failure is ``bc55e36``, where a
corpus that emitted nothing reported a CLEARED gate.

**It writes NOTHING to any corpus member, and that is proved rather than promised.** Every byte
read from a member comes out of the git OBJECT DATABASE at the member's pinned commit through the
shipped content-addressed helpers ``pinned_tree`` / ``materialize_pinned_bytes`` /
``verify_pinned_bytes``, and every git invocation goes through
``build_silent_class_record.read_only_git``, whose verb allow-list
:data:`~build_silent_class_record.READ_ONLY_GIT_COMMANDS` Story 16.7's suite proves by DRIVING it.
No member is ratified, no member moves between partitions, no third-party source is fetched,
``DF-13-5-A``'s one expansion round is UNSPENT, and no seal value is amended. **Reaching a gate by
changing the corpus after seeing the number is this epic's named anti-pattern**, and no amount of
local justification makes it permissible.

**Where the output may land is imported, not chosen.** The record is written under
``precision_preregistration.SUCCESSOR_OUTPUT_PATHS[0]`` and nowhere else, because
``TC-ArgusAgent-PRECISION-001-139`` and ``-147`` between them assert the ordering constraint
against those prefixes as git pathspecs — output committed anywhere else makes the ordering claim
unprovable against the object database.

**No human worklist is rendered, and that is a decision rather than an omission** (``DN-17-4-10``,
recorded in the story). Story 16.7 rendered one because it was asking a named human for 36
judgements and the spans WERE the question. This story asks for no judgement (``DN-17-4-2``), so a
worklist would spend ``NFR-S1``'s source-span carve-out to support a judgement nobody requested.
The machine record carries locators and counts and no source byte at all.

**Determinism is a requirement, not a hope.** No clock, no ``uuid4``, no ``random``, no environment
read and no network reach any derivation path, so ``--check --checkout-root`` is a genuine
byte-comparison rather than a re-render. The record carries no date for the same reason — the
commit and the story record carry it, exactly as ``silent-class-record.json`` does.

**Portability is a criterion** (``AI-E13-1``). The local gate is Windows-only while CI runs an
ubuntu matrix, so: every read and write names ``encoding="utf-8"``, the artifact write names its
newline, the record goes through ``argus.store.canonical`` so it is byte-stable across platforms,
every locator is a POSIX path that came out of the object database with no separator constant
reachable from it, spans are split by ``index_aligned_lines`` and never ``str.splitlines()``, and
``--snapshot-root`` is REQUIRED and should be SHORT on Windows because the deepest in-scope path
can push the absolute path past ``MAX_PATH`` — and a partially extracted tree measures CLEAN, which
is failing silently in the dangerous direction.

**Exit contract**, ``scripts/audit_validation_corpus.py``'s:

- **0** — the record is current (``--check``) or was written.
- **2** — REFUSED: a named precondition failed and is printed on stderr.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
for _entry in (str(_REPO_ROOT), str(_SCRIPTS)):  # pragma: no cover - script bootstrap
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

# ⛔ ``-151``'s non-vacuity anchor over THIS module: a known-present outbound edge to the shipped
# grader. A walk that cannot resolve it would report *"no second derivation of S1"* forever.
from argus.detectors.assertion_strength import UNESTABLISHED  # noqa: E402,F401
from argus.detectors.vacuous_test import (  # noqa: E402
    VacuousTestDetector,
    index_aligned_lines,
)
from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.precision.silent_class import (  # noqa: E402
    SILENT_CLASS_RULE_ID,
    ProvenanceEvidence,
    definitions_by_start_line,
    locator_for,
    score_span,
    span_edges_of,
)
from argus.store.canonical import dumps, loads  # noqa: E402

# ⛔ ONE walk, ONE read-only git vocabulary, ONE checkout map, ONE population derivation and ONE
# refusal type — Story 16.7's, IMPORTED. Re-typing any of them here would be the AR7 fork this
# epic exists to close, applied to the harness rather than to the predicate. The underscore names
# are imported deliberately and the reason is load-bearing: a private second copy of
# ``_population`` would let this record and ``silent-class-record.json`` disagree about what the
# recorded population IS, which is precisely the ``DF-8-5-C`` shape.
from build_silent_class_record import (  # noqa: E402
    DEFAULT_CHECKOUT_MAP,
    READ_ONLY_GIT_COMMANDS,
    Refused,
    _checkout_for,
    _decode,
    _discards_the_root,
    _keeper,
    _population,
    read_only_git,
)
from pinned_corpus_snapshot import (  # noqa: E402
    PinnedSnapshotError,
    materialize_pinned_bytes,
    pinned_tree,
    verify_pinned_bytes,
)
from precision_preregistration import evaluate  # noqa: E402
from successor_reach_model import (  # noqa: E402
    RECORD_ABSOLUTE_PATH,
    SUCCESSOR_RECORD_PATH,
    Reach,
    fold,
    record_text,
    seed_successor_row,
    shortfalls,
)

_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_CORPUS_DIR = _ARTIFACTS / "validation-corpus"
_ADJUDICATION_SET = _CORPUS_DIR / "adjudication-set-13-5.json"

# The READ-ONLY vocabulary and the checkout map this harness runs under, re-exported so a reader
# auditing what this script may do to somebody else's repository does not have to open a second
# file to find out. Bound, never re-typed.
HARNESS_GIT_VOCABULARY = READ_ONLY_GIT_COMMANDS
HARNESS_CHECKOUT_MAP = DEFAULT_CHECKOUT_MAP


# ═════════════════════════════════════════════════════════════════════════════════════════
# The walk
# ═════════════════════════════════════════════════════════════════════════════════════════


def derive(
    payload: dict, checkout_root: Path, overrides: dict[str, str], snapshot_root: Path
) -> Reach:
    """Walk the WHOLE recorded population at the pins and score every span. Reads only.

    ⛔ A finding that cannot be resolved at the pin is a REFUSAL, never a skip (AC1.2). *"A
    skipped finding and a non-member are indistinguishable in the output"* — and here the
    difference lands directly on the criterion's yield-floor numerator, which is the one number
    this whole story exists to measure honestly.
    """
    population = _population(payload)
    total = sum(entry["count"] for entry in population.values())
    if total == 0:
        raise Refused(
            f"the committed {_ADJUDICATION_SET.name} carries ZERO {SILENT_CLASS_RULE_ID} "
            f"findings. That is an unreadable corpus rather than a clean one, and measuring S1 "
            f"over it would publish a reach of zero that satisfies every 'nothing was promoted' "
            f"guard forever (non-vacuity floor, AI-E11-1)."
        )
    out = Reach()
    for member_id in sorted(population):
        entry = population[member_id]
        out.members_walked.append(member_id)
        if not entry["paths"]:
            # ⛔ A member that contributes NOTHING is still a member of the population the ratio
            # was measured over, never a member quietly dropped from the denominator
            # (POPULATION_DERIVATION, verbatim). It is walked, recorded, and contributes 0.
            continue
        checkout = _checkout_for(checkout_root, member_id, overrides)
        if not checkout.is_dir():
            raise Refused(
                f"{member_id}: no checkout at {checkout}. Point --checkout-root at the directory "
                f"holding the ratified checkouts, or map this member with "
                f"--map {member_id}=RELATIVE/PATH. Nothing is cloned or fetched here: a "
                f"third-party fetch is an operator act (protocol section 6 R2) and no Epic 17 "
                f"story may take one."
            )
        status = read_only_git(checkout, "status", "--porcelain")
        out.porcelain[member_id] = len(
            [line for line in _decode(status.stdout).splitlines() if line.strip()]
        )
        wanted = set(entry["paths"])
        try:
            tree = pinned_tree(checkout, entry["pinned_sha"], keep=_keeper(wanted))
        except PinnedSnapshotError as exc:
            raise Refused(f"{member_id}: {exc}") from exc
        missing = wanted - set(tree.paths)
        if missing:
            raise Refused(
                f"{member_id}: {len(missing)} recorded path(s) are absent from the pinned tree "
                f"{entry['pinned_sha']}: {sorted(missing)[:3]!r}. A finding whose file cannot be "
                f"read at the pin is UNRESOLVABLE, and skipping it silently would shrink the "
                f"population by an amount nobody can see (AC10.6)."
            )
        dest = snapshot_root / member_id
        materialize_pinned_bytes(checkout, tree, dest)
        proof = verify_pinned_bytes(dest, tree)
        if not proof.proves_pinned_bytes:
            raise Refused(
                f"{member_id}: the materialized bytes are NOT the pinned bytes "
                f"({proof.verified_file_count}/{proof.expected_file_count} verified, "
                f"missing={proof.missing_paths!r} mismatched={proof.mismatched_paths!r}). "
                f"Measuring a tree nobody pinned is AC10.6's REFUSAL, not a warning."
            )
        out.verifications.append({"member_id": member_id, **proof.to_payload()})
        _derive_member(out, member_id, entry, tree.paths, dest)
    if out.skipped:
        raise Refused(
            f"{len(out.skipped)} finding(s) could not be resolved to a definition at the pin: "
            f"{out.skipped[:5]!r}. The measurement must cover the WHOLE recorded population - 0 "
            f"skipped, 0 unresolvable - because a skipped finding and a non-member are "
            f"indistinguishable in the output."
        )
    if out.walked != total:
        raise Refused(
            f"walked {out.walked} finding(s) but the committed set records {total}. The "
            f"measurement must cover the population EXACTLY; a partial walk publishes a reach "
            f"measured over a population nobody declared."
        )
    return out


def _derive_member(
    out: Reach,
    member_id: str,
    entry: dict[str, Any],
    paths: tuple[str, ...],
    dest: Path,
) -> None:
    """Score every recorded finding of one member with the SHIPPED S1 and the SHIPPED fact (b).

    ⛔ ONE span resolution, TWO readings of it. ``successor_evidence`` and ``score_span`` are
    called on the SAME ``(source_lines, span_edges, start, end)`` tuple, side by side, exactly as
    Story 17.3 §0.7 requires — ``silent_class.SpanScore`` is NOT widened to carry
    ``s1_corroborated`` and ``VacuousTestScore``'s field set is NOT touched
    (``TC-ArgusAgent-DETECT-001-119``, ``-143``). Widening a model to fit new code and then
    editing the green guard that pinned it is ``DF-8-5-B`` by name.
    """
    index = build_ast_index(str(dest), tuple(sorted(paths)))
    entries = {item.file_path: item for item in index.entries}
    for path in sorted(entry["paths"]):
        indexed = entries.get(path)
        if indexed is None or indexed.parse_failed or not indexed.ast_eligible:
            out.skipped.extend(
                locator_for(path, line) for line in sorted(entry["paths"][path])
            )
            continue
        source = (dest / path).read_bytes().decode("utf-8", errors="replace")
        # ⛔ `index_aligned_lines`, never `str.splitlines()`: the line-numbering contract.
        # `splitlines()` splits on eleven things where the index counts one.
        source_lines = index_aligned_lines(source)
        by_start = definitions_by_start_line(indexed)
        for line in sorted(entry["paths"][path]):
            out.walked += 1
            out.rule_ids_walked[SILENT_CLASS_RULE_ID] = (
                out.rule_ids_walked.get(SILENT_CLASS_RULE_ID, 0) + 1
            )
            definition = by_start.get(line)
            if definition is None:
                out.skipped.append(locator_for(path, line))
                continue
            edges = span_edges_of(indexed, definition)
            start, end = definition.start_line, definition.end_line
            evidence = VacuousTestDetector.successor_evidence(source_lines, edges, start, end)
            score = score_span(source_lines, edges, start, end)
            out.tally(out.band_totals_walked, evidence)
            # ⛔ The SHIPPED discard half, read off the SHIPPED property rather than re-typed as
            # `disc >= 1 and cons == 0` — so this record and `_ast_corroborated` cannot disagree.
            provenance = ProvenanceEvidence(
                discarded_sut_calls=score.discarded_sut_calls,
                consumed_sut_calls=score.consumed_sut_calls,
                mock_referencing_assertions=score.mock_referencing_assertions,
            )
            shipped = (
                provenance.sut_result_is_discarded
                and provenance.mock_referencing_assertions >= 1
            )
            locator = locator_for(path, start)
            if shipped:
                out.shipped_promoted.append((member_id, locator))
            if not evidence.s1_corroborated:
                continue
            out.tally(out.band_totals_eligible, evidence)
            out.rows.append(
                seed_successor_row(
                    member_id=member_id,
                    rule_id=SILENT_CLASS_RULE_ID,
                    locator=locator,
                    test_name=definition.name,
                    pinned_sha=entry["pinned_sha"],
                    evidence=evidence,
                    score=score,
                    shipped_verdict_eligible=shipped,
                )
            )


# ═════════════════════════════════════════════════════════════════════════════════════════
# CLI
# ═════════════════════════════════════════════════════════════════════════════════════════


def build(
    *,
    check_only: bool,
    checkout_root: Path | None,
    overrides: dict[str, str],
    snapshot_root: Path | None,
) -> int:
    if not _ADJUDICATION_SET.is_file():
        raise Refused(
            f"the ratified adjudication set is absent at "
            f"{_ADJUDICATION_SET.relative_to(_REPO_ROOT).as_posix()}. This story measures the "
            f"corpus Story 13.5 recorded; it does not re-derive or re-ratify it."
        )
    if checkout_root is None:
        if not check_only:
            raise Refused(
                "--checkout-root is required to WRITE the record: S1 is measured from the "
                "members' pinned blobs and nothing else. --check alone verifies what this "
                "repository can see by itself, and says so."
            )
        return _check_without_corpus()

    if snapshot_root is None:
        raise Refused(
            "--snapshot-root is required alongside --checkout-root. The default temp root can "
            "push the deepest in-scope absolute path past MAX_PATH on Windows, and a partially "
            "extracted tree measures CLEAN - it fails silently in the dangerous direction. Pass "
            "a SHORT path, e.g. --snapshot-root c:/t/ar174."
        )
    snapshot_root.mkdir(parents=True, exist_ok=True)
    payload = loads(_ADJUDICATION_SET.read_text(encoding="utf-8"))
    reach = derive(payload, checkout_root, overrides, snapshot_root)
    assessment = fold(reach)
    text = record_text(reach, assessment)

    if check_only:
        current = (
            RECORD_ABSOLUTE_PATH.read_text(encoding="utf-8")
            if RECORD_ABSOLUTE_PATH.is_file()
            else ""
        )
        if current != text:
            raise Refused(
                f"{SUCCESSOR_RECORD_PATH} is NOT current against a fresh measurement at the "
                f"pins. Do not quietly rewrite it: the whole value of this artifact is that the "
                f"measurement was taken ONCE, against a criterion frozen beforehand. Report the "
                f"difference LOUDLY in the story record first."
            )
        print(f"OK - {SUCCESSOR_RECORD_PATH} is current against a re-measurement at the pins.")
        _print_report(reach, assessment)
        return 0

    RECORD_ABSOLUTE_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECORD_ABSOLUTE_PATH.write_text(text, encoding="utf-8", newline="\n")
    print(f"WROTE {SUCCESSOR_RECORD_PATH}")
    _print_report(reach, assessment)
    return 0


def _check_without_corpus() -> int:
    """Verify what this repository can see BY ITSELF, and print what it did NOT check.

    Two things are checkable without the five third-party checkouts, and both matter: the record
    round-trips through ``argus.store.canonical`` unchanged (so it was not hand-edited), and the
    recorded outcome RE-DERIVES from the recorded counts through the frozen fold (so the verdict
    and the counts cannot have drifted apart). What is NOT checked is the measurement itself, and
    that limitation is PRINTED rather than left implied by a green line.
    """
    if not RECORD_ABSOLUTE_PATH.is_file():
        raise Refused(
            f"{SUCCESSOR_RECORD_PATH} is absent. Run this script with --checkout-root and "
            f"--snapshot-root to take the measurement and write it."
        )
    raw = RECORD_ABSOLUTE_PATH.read_text(encoding="utf-8")
    payload = loads(raw)
    if dumps(payload) + "\n" != raw:
        raise Refused(
            f"{SUCCESSOR_RECORD_PATH} does not round-trip through argus.store.canonical "
            f"unchanged - it has been hand-edited or written by something other than this script."
        )
    recorded = payload["criterion"]
    replay = evaluate(
        verdict_eligible_count=recorded["verdict_eligible_count"],
        contributing_member_count=recorded["contributing_member_count"],
        sealed_contributing_member_count=recorded["sealed_contributing_member_count"],
        true_positive_count=recorded["true_positive_count"],
        false_accusation_count=recorded["false_accusation_count"],
    )
    if replay.outcome != recorded["outcome"] or replay.reason != recorded["reason"]:
        raise Refused(
            f"the recorded outcome {recorded['outcome']!r} does NOT re-derive from the recorded "
            f"counts through the frozen fold, which returns {replay.outcome!r}. Either the counts "
            f"or the verdict was edited after the measurement, and a verdict that does not follow "
            f"from its own counts is exactly what this record exists to make impossible."
        )
    print(
        f"OK - {SUCCESSOR_RECORD_PATH} round-trips through argus.store.canonical unchanged "
        f"({len(payload['rows'])} row(s)), and its recorded outcome {recorded['outcome']} "
        f"re-derives from its recorded counts through the frozen fold."
    )
    print(
        "NOT RE-MEASURED BY THIS RUN, and NOT a claim that the record is current - S1's reach is "
        "measured from five third-party checkouts this run was not given. Pass --checkout-root "
        "and --snapshot-root to re-measure, which is the check that compares bytes."
    )
    return 0


def _print_report(reach: Reach, assessment: Any) -> None:
    print(
        f"walked={reach.walked} skipped={len(reach.skipped)} "
        f"rule_classes={sorted(reach.rule_ids_walked)} members={sorted(reach.members_walked)}"
    )
    print(
        f"S1 eligible={len(reach.rows)} by member={reach.eligible_by_member()} "
        f"bands(eligible)={reach.band_totals_eligible} bands(walked)={reach.band_totals_walked}"
    )
    print(
        f"SHIPPED verdict-eligible predicate promotes {len(reach.shipped_promoted)} of "
        f"{reach.walked} (DF-13-5-A condition 1, measured)"
    )
    print(f"OUTCOME: {assessment.outcome}")
    print(f"REASON: {assessment.reason}")
    for shortfall in shortfalls(assessment):
        print(
            f"  SHORTFALL {shortfall['floor']}: measured {shortfall['measured']}, "
            f"required {shortfall['required']}"
        )
    print(
        "NOTHING IS ADJUDICATED AND NOTHING IS PROMOTED. Every row is UNADJUDICATED and stays "
        "verdict_eligible=false; the externalization gate stays BLOCKED and the >=80% keystone "
        "stays NOT CLEARED at EVERY outcome, including MET."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed record; write nothing.",
    )
    parser.add_argument(
        "--checkout-root",
        default=None,
        help=(
            "Directory containing the ratified checkouts, resolved per member by --map. "
            "Required to WRITE. Omitted with --check, the run verifies only what this "
            "repository can see by itself and says so."
        ),
    )
    parser.add_argument(
        "--map",
        action="append",
        default=[],
        metavar="MEMBER_ID=RELATIVE_PATH",
        help="Where a member's checkout lives under --checkout-root. Repeatable.",
    )
    parser.add_argument(
        "--snapshot-root",
        default=None,
        help=(
            "Directory the pinned blobs are materialized under. REQUIRED with --checkout-root, "
            "and SHORT on Windows: the deepest in-scope path here is long enough that a default "
            "temp root can push the absolute path past MAX_PATH, and a partially-extracted tree "
            "measures clean."
        ),
    )
    args = parser.parse_args(argv)
    try:
        overrides: dict[str, str] = {}
        for pair in args.map:
            if "=" not in pair:
                raise Refused(f"--map {pair!r} is not MEMBER_ID=RELATIVE_PATH (no '=' found)")
            member_id, _, relative = pair.partition("=")
            if not member_id.strip() or not relative.strip():
                raise Refused(f"--map {pair!r} has an empty member id or path")
            if _discards_the_root(relative):
                raise Refused(
                    f"--map {pair!r} names an ANCHORED path - absolute, root-anchored or "
                    f"drive-relative. It must be relative to --checkout-root, because pathlib "
                    f"discards the left operand when the right one is anchored - which silently "
                    f"escapes the root entirely."
                )
            overrides[member_id] = relative
        return build(
            check_only=args.check,
            checkout_root=Path(args.checkout_root) if args.checkout_root else None,
            overrides=overrides,
            snapshot_root=Path(args.snapshot_root) if args.snapshot_root else None,
        )
    except Refused as exc:
        print(f"REFUSED - {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
