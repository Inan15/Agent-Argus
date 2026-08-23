"""Story 16.7 — derive the SILENT test class and publish it for a named human to judge.

    python scripts/build_silent_class_record.py --check
    python scripts/build_silent_class_record.py --checkout-root D:/ProjectX/XAgents/XAgents

**This script cannot adjudicate anything, and that is its main design constraint.** It
seeds one ``UNADJUDICATED`` row per member of the V2 SILENT class and writes them through
:class:`argus.precision.silent_class.SilentClassRow`, whose constructor RAISES if a row
that is not a human judgement carries an adjudicator. The only row constructor this script
can reach — :func:`~argus.precision.silent_class.seed_row` — has no parameter for a
disposition, an adjudicator or a date, so *"the producer started filling in the human's
judgements"* is not a failure mode a reviewer has to watch for; it is unreachable.

**It writes NOTHING to any corpus member, and that is proved rather than promised.** Every
byte read from a member comes out of the git OBJECT DATABASE at the member's pinned commit,
through the shipped content-addressed helpers ``pinned_tree`` (``git ls-tree -r``),
``materialize_pinned_bytes`` (``git cat-file --batch`` into a scratch directory) and
``verify_pinned_bytes``, which re-hashes every materialized file with git's own blob
identity and compares it to the id ``ls-tree`` reported. What a member's WORKING TREE holds
cannot reach the measurement. On top of that, every git invocation this script makes goes
through :func:`read_only_git`, whose verb allow-list :data:`READ_ONLY_GIT_COMMANDS` is a
named constant: ``checkout``, ``stash``, ``clean``, ``reset``, ``worktree``, ``add``,
``commit``, ``fetch`` and ``pull`` are absent from it, and ``tests/test_silent_class.py``
proves the refusal by driving it rather than by reading the list.

Deliberately NOT asserted: that a member's ``git status --porcelain`` is empty, or that it
is invariant across the run. Both were measured unsatisfiable — ``minions`` returned 13,
14, 0, 7, 1 and 0 dirty entries across six same-day readings by three different sessions,
because it is a live tree other people are editing. Neither emptiness nor invariance is
this story's business or within its control, so the porcelains are CAPTURED and REPORTED
and a difference is never a failure (``DN-16-7-4``).

**Exit contract**, the ``scripts/audit_validation_corpus.py`` one:

- **0** — the artifacts are current (``--check``) or were written.
- **2** — REFUSED: a named precondition failed and is printed on stderr.

**Append-only over human judgements.** An existing record is LOADED and every row carrying
a human disposition is carried through byte-identically. Re-running this after an
adjudication is a no-op over the judged rows: a producer that can overwrite a judgement can
erase one.

**What ``--check`` does and does not recompute, said out loud rather than implied.**
Without ``--checkout-root`` it verifies the one thing this repository can see by itself:
that the committed record round-trips through ``argus.store.canonical`` unchanged, i.e.
that it is exactly what this script's serializer produces and has not been hand-edited.
It does NOT re-derive the class and it does NOT compare the worklist's bytes, because both
need five third-party checkouts a clean CI machine does not have — and it prints that
limitation rather than letting a green line imply a measurement it never made. With
``--checkout-root`` it re-derives the class from the pinned blobs, re-renders the worklist
and compares BOTH artifacts byte-for-byte. Only the second form is a currency claim.

**Portability is a criterion here, not a hope** (``AI-E13-1``, ``DF-16-6-F``). This script
shells out to git over five repositories of third-party source on a machine whose local
suite is Windows-only while CI runs an ubuntu matrix. So: it adds no ``_git`` of its own
and reuses ``scripts/pinned_corpus_snapshot.py``'s, which captures BYTES and decodes them
explicitly rather than passing ``text=True`` and getting the locale codec; every file read
and write names ``encoding="utf-8"``; every artifact write names its newline; and every
locator is built by concatenating a POSIX path that came out of the object database, so no
platform separator constant and no path-join helper is reachable from the locator path at
all.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS = Path(__file__).resolve().parent
for _entry in (str(_REPO_ROOT), str(_SCRIPTS)):  # pragma: no cover - script bootstrap
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from argus.detectors.secret_scan import (  # noqa: E402
    RULE_HARDCODED_SECRET,
    SecretScanDetector,
)
from argus.detectors.vacuous_test import index_aligned_lines  # noqa: E402
from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.precision.adjudication import (  # noqa: E402
    ADJUDICATION_UNIT,
    DISPOSITIONS,
    PROTOCOL_ADJUDICATOR_ROLES,
    change_log_head_version,
)
from argus.precision.silent_class import (  # noqa: E402
    IDIOMS,
    SILENT_CLASS_DEFINITION,
    SILENT_CLASS_RECORD_PATH,
    SILENT_CLASS_RULE_ID,
    SILENT_CLASS_WORKLIST_PATH,
    SilentClassRecord,
    SilentClassRow,
    carry_forward,
    definitions_by_start_line,
    locator_for,
    exhaustiveness_payload,
    record_from_payload,
    rows_from_payload,
    score_span,
    seed_row,
    span_edges_of,
)
from argus.store.canonical import dumps, loads  # noqa: E402
from pinned_corpus_snapshot import (  # noqa: E402
    PinnedSnapshotError,
    _git,
    materialize_pinned_bytes,
    pinned_tree,
    verify_pinned_bytes,
)

_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_CORPUS_DIR = _ARTIFACTS / "validation-corpus"
_ADJUDICATION_SET = _CORPUS_DIR / "adjudication-set-13-5.json"
_PROTOCOL = _ARTIFACTS / "precision-validation-protocol.md"
_RECORD = _REPO_ROOT / SILENT_CLASS_RECORD_PATH
_WORKLIST = _REPO_ROOT / SILENT_CLASS_WORKLIST_PATH

#: Where each corpus member's checkout lives, RELATIVE to ``--checkout-root``. Relative on
#: purpose: no absolute host path is hardcoded in this repository and none reaches any
#: committed artifact (NFR-S1). Note ``agent-smith`` is nested one level deeper than the
#: other four, which has cost this project a cycle before.
DEFAULT_CHECKOUT_MAP: dict[str, str] = {
    "agent-markovich": "AgentMarkovich",
    "minions": "Minions",
    "xagents-webapp": "XAgents-WebApp",
    "agent-smith": "XAgents/Agent-Smith",
    "ai-body-runtime": "ai_body_runtime",
}

#: EVERY git subcommand this harness may issue, and it is a READ-ONLY vocabulary. The two
#: shipped snapshot helpers reach exactly ``ls-tree`` and ``cat-file``; this script adds
#: ``rev-parse`` (resolve the pin) and ``status`` (capture the porcelain for the report).
#: ``checkout``, ``stash``, ``clean``, ``reset``, ``worktree``, ``add``, ``commit``,
#: ``fetch`` and ``pull`` are ABSENT, and the absence is a test rather than a promise: a
#: corpus member is somebody else's repository and this story is a measurement.
READ_ONLY_GIT_COMMANDS: frozenset[str] = frozenset(
    {"cat-file", "ls-tree", "rev-parse", "status"}
)

#: The header the worklist carries, stating AC8.6's source-span carve-out and its bound.
_CARVE_OUT = (
    "SOURCE-SPAN CARVE-OUT, stated rather than assumed. NFR-S1 forbids a source byte from "
    "a corpus member appearing in a committed artifact. This worklist carries them anyway, "
    "as a BOUNDED and deliberate exception, because the judgement it asks for cannot be "
    "made without reading the test: the whole point of the artifact is that the named "
    "human does not have to clone five repositories to answer 36 questions. The bound, "
    "exactly: (1) spans appear in THIS Markdown file and nowhere else - the machine record "
    "carries no source byte at all, and no span is copied into deferred-work.md, into the "
    "story file, or into any commit message; (2) every span is read from the member's "
    "PINNED BLOB at the sha named on its row, proved against the pin by blob hash, never "
    "from a working tree; (3) each span is bounded to the flagged test function and to "
    "nothing around it; (4) any span the shipped hardcoded-secret detector flags is "
    "REDACTED to its locator and the redaction is recorded on the row."
)


def _keeper(wanted: set[str]) -> Any:
    """A ``keep`` predicate bound to ONE member's paths - a named closure, not a loop lambda."""

    def keep(path: str) -> bool:
        return path in wanted

    return keep


class Refused(RuntimeError):
    """A named precondition failure — printed as ``REFUSED — ...`` with exit code 2."""


def read_only_git(checkout: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    """``git -C <checkout> <args>`` restricted to :data:`READ_ONLY_GIT_COMMANDS`.

    A GUARD in front of the shipped ``pinned_corpus_snapshot._git``, not a sixth copy of
    it: the subprocess call, the byte capture and the explicit decode all stay where they
    already are, correct and already tested. What this adds is the refusal, and the refusal
    is what makes ``DN-16-7-4``'s containment claim checkable by execution instead of by
    reading the diff and believing it.
    """
    if not args or args[0] not in READ_ONLY_GIT_COMMANDS:
        raise Refused(
            f"git subcommand {args[0] if args else '<none>'!r} is not in this harness's "
            f"READ-ONLY vocabulary {sorted(READ_ONLY_GIT_COMMANDS)!r}. A corpus member is "
            f"a ratified third-party repository and this story is a MEASUREMENT: it reads "
            f"the object database and writes nothing, anywhere, ever."
        )
    return _git(checkout, *args)


def _decode(raw: bytes) -> str:
    """Decode subprocess output EXPLICITLY — never through the locale codec (DF-16-6-F).

    ``subprocess.run(..., text=True)`` decodes with ``locale.getpreferredencoding()``,
    which is cp1252 on the Windows machine this suite runs on locally and utf-8 on the
    ubuntu matrix CI runs. A single non-cp1252 byte in a third-party repository's status
    output therefore crashes on one leg and passes on the other, which is exactly the
    class of bug this repository has already shipped once and has an OPEN ledger entry for.
    """
    return raw.decode("utf-8", errors="replace")


def _checkout_for(root: Path, member_id: str, overrides: dict[str, str]) -> Path:
    relative = overrides.get(member_id, DEFAULT_CHECKOUT_MAP.get(member_id, member_id))
    return root / relative


def _population(payload: dict) -> dict[str, dict[str, Any]]:
    """The recorded ``vacuous_test_heuristic`` findings, per member — READ, never re-run.

    Non-vacuity is checked by the caller and it is not optional (``AI-E11-1``): an empty
    population produces an empty class, and an empty class satisfies every "nothing was
    promoted" guard in this story forever.
    """
    out: dict[str, dict[str, Any]] = {}
    for member in payload["members"]:
        wanted: dict[str, list[int]] = {}
        for finding in member["findings"]:
            if finding.get("rule_id") != SILENT_CLASS_RULE_ID:
                continue
            locators = finding["locators"]
            if not locators:
                raise Refused(
                    f"{member['member_id']}: a {SILENT_CLASS_RULE_ID} finding carries NO "
                    f"locator. FR13 requires >= 1 verifiable locator and protocol section "
                    f"4's ladder re-examines exactly that locator; a finding without one "
                    f"cannot be adjudicated at all."
                )
            path, _, line = locators[0].rpartition(":")
            wanted.setdefault(path, []).append(int(line))
        out[member["member_id"]] = {
            "pinned_sha": member["pinned_sha"],
            "paths": wanted,
            "count": sum(len(lines) for lines in wanted.values()),
        }
    return out


class Derivation:
    """The class as derived, plus everything the report and the worklist need to say."""

    def __init__(self) -> None:
        self.rows: list[SilentClassRow] = []
        self.spans: dict[str, list[str]] = {}
        self.redacted: list[str] = []
        self.walked = 0
        self.skipped: list[str] = []
        self.commented = 0
        self.verifications: list[dict[str, Any]] = []
        self.porcelain: dict[str, int] = {}


def derive(
    payload: dict, checkout_root: Path, overrides: dict[str, str], snapshot_root: Path
) -> Derivation:
    """Derive the silent class from the PINNED blobs of every member. Reads only."""
    population = _population(payload)
    total = sum(entry["count"] for entry in population.values())
    if total == 0:
        raise Refused(
            f"the committed {_ADJUDICATION_SET.name} carries ZERO {SILENT_CLASS_RULE_ID} "
            f"findings. That is an unreadable corpus rather than a clean one, and deriving "
            f"a class over it would publish an empty worklist that passes every guard in "
            f"this story forever (non-vacuity floor, AI-E11-1)."
        )
    out = Derivation()
    detector = SecretScanDetector()
    for member_id in sorted(population):
        entry = population[member_id]
        if not entry["paths"]:
            continue
        checkout = _checkout_for(checkout_root, member_id, overrides)
        if not checkout.is_dir():
            raise Refused(
                f"{member_id}: no checkout at {checkout}. Point --checkout-root at the "
                f"directory holding the ratified checkouts, or map this member with "
                f"--map {member_id}=RELATIVE/PATH. Nothing is cloned or fetched here: a "
                f"third-party fetch is an operator act (protocol section 6 R2)."
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
                f"{member_id}: {len(missing)} recorded path(s) are absent from the pinned "
                f"tree {entry['pinned_sha']}: {sorted(missing)[:3]!r}. A finding whose file "
                f"cannot be read at the pin is UNRESOLVABLE, and skipping it silently would "
                f"shrink the class by an amount nobody can see."
            )
        dest = snapshot_root / member_id
        materialize_pinned_bytes(checkout, tree, dest)
        proof = verify_pinned_bytes(dest, tree)
        if not proof.proves_pinned_bytes:
            raise Refused(
                f"{member_id}: the materialized bytes are NOT the pinned bytes "
                f"({proof.verified_file_count}/{proof.expected_file_count} verified, "
                f"missing={proof.missing_paths!r} mismatched={proof.mismatched_paths!r}). "
                f"Deriving a class from unproven bytes measures a tree nobody pinned."
            )
        out.verifications.append({"member_id": member_id, **proof.to_payload()})
        _derive_member(out, member_id, entry, tree.paths, dest, detector)
    if out.skipped:
        raise Refused(
            f"{len(out.skipped)} finding(s) could not be resolved to a definition at the "
            f"pin: {out.skipped[:5]!r}. The class must be derived over the WHOLE recorded "
            f"population - 0 skipped, 0 unresolvable - because a skipped finding and a "
            f"non-member are indistinguishable in the output."
        )
    if out.walked != total:
        raise Refused(
            f"walked {out.walked} finding(s) but the committed set records {total}. The "
            f"derivation must cover the population exactly."
        )
    return out


def _derive_member(
    out: Derivation,
    member_id: str,
    entry: dict[str, Any],
    paths: tuple[str, ...],
    dest: Path,
    detector: SecretScanDetector,
) -> None:
    """Score every recorded finding of one member against the SHIPPED index and predicate."""
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
        source_lines = index_aligned_lines(source)
        by_start = definitions_by_start_line(indexed)
        secret_lines = _secret_lines(detector, path, source, indexed)
        for line in sorted(entry["paths"][path]):
            out.walked += 1
            definition = by_start.get(line)
            if definition is None:
                out.skipped.append(locator_for(path, line))
                continue
            edges = span_edges_of(indexed, definition)
            score = score_span(source_lines, edges, definition.start_line, definition.end_line)
            if not score.is_silent_class_member:
                continue
            locator = locator_for(path, definition.start_line)
            out.rows.append(
                seed_row(
                    member_id=member_id,
                    locator=locator,
                    test_name=definition.name,
                    pinned_sha=entry["pinned_sha"],
                    score=score,
                )
            )
            span = source_lines[definition.start_line - 1 : definition.end_line]
            if any(definition.start_line <= hit <= definition.end_line for hit in secret_lines):
                out.redacted.append(locator)
                out.spans[locator] = []
            else:
                out.spans[locator] = list(span)
            if any("#" in text for text in span):
                out.commented += 1


def _secret_lines(
    detector: SecretScanDetector, path: str, source: str, indexed: Any
) -> set[int]:
    """Lines the SHIPPED hardcoded-secret detector flags — reused, never re-implemented.

    AC8.6's redaction arm. The producer-side redaction this project already ships is the
    one that decides whether a span may be published; writing a second credential heuristic
    here would be the fork class (``AR7``) applied to the one question where a fork means a
    leaked secret rather than a wrong number.
    """
    result = detector.run(file_path=path, source=source, ast_entry=indexed)
    lines: set[int] = set()
    for finding in result.findings:
        if finding.rule_id != RULE_HARDCODED_SECRET:
            continue
        for locator in finding.locators:
            lines.update(range(locator.start_line, locator.end_line + 1))
    return lines


_EXPERT_HOURS_NOTE = (
    "NOT RECORDED - no adjudication run has taken place. Story 16.7 delivered the "
    "instrument and HALTED at the judgement, which is an OPERATOR ACT no automated "
    "producer may take (protocol section 2: UNADJUDICATED is the ONLY member an automated "
    "producer may write). The actual hours are recorded here by the adjudicator when the "
    "run happens, and are compared against protocol section 3's <= 4 expert-hour ceiling "
    "AS A REPORT, never as a gate. NOT RECORDED means exactly that and never zero."
)

_TRANSCRIPTION_NOTE = (
    "NOTHING ON THIS RECORD WAS TRANSCRIBED. Every row was SEEDED UNADJUDICATED by "
    "scripts/build_silent_class_record.py and carries no adjudicator and no date. If a "
    "named human supplies judgements they are transcribed VERBATIM, this note records that "
    "they were transcribed and from whom, and no row is ever inferred, completed or "
    "defaulted from another (DN-6)."
)


def _record_from(rows: tuple[SilentClassRow, ...], walked: int, method: str) -> SilentClassRecord:
    return SilentClassRecord(
        protocol_version=change_log_head_version(_PROTOCOL.read_text(encoding="utf-8")),
        adjudication_unit=ADJUDICATION_UNIT,
        class_definition=SILENT_CLASS_DEFINITION,
        derivation_source=(
            "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/"
            "adjudication-set-13-5.json (Story 13.5, operator-ratified 2026-08-18) - the "
            "recorded vacuous_test_heuristic findings, READ. No detector was re-run over "
            "any corpus member and DF-13-5-A's one expansion round is UNSPENT."
        ),
        derivation_method=method,
        population_walked=walked,
        population_skipped=0,
        expert_hours=None,
        expert_hours_note=_EXPERT_HOURS_NOTE,
        transcription_note=_TRANSCRIPTION_NOTE,
        rows=rows,
    )


_METHOD = (
    "Every member read from its PINNED COMMIT through the shipped content-addressed "
    "helpers: git ls-tree -r enumerates the in-scope blobs, git cat-file --batch reads them "
    "from the object database into a scratch tree, and every materialized file is re-hashed "
    "with git's own blob identity and compared to the id ls-tree reported. The span is then "
    "scored by CALLING the shipped provenance_evidence (frozen table, fact (b)'s own "
    "arithmetic), body_statement_count, opens_bare_assert and is_assertion_callee (the WIDE "
    "table, DN-14-2-1) over a real build_ast_index. No AST walk, no line scanner and no "
    "assertion vocabulary is re-implemented anywhere in this derivation."
)


def _load_existing() -> tuple[SilentClassRow, ...]:
    if not _RECORD.is_file():
        return ()
    return rows_from_payload(loads(_RECORD.read_text(encoding="utf-8")))


def _record_text(record: SilentClassRecord) -> str:
    return dumps(record.to_payload()) + "\n"


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
            f"{_ADJUDICATION_SET.relative_to(_REPO_ROOT).as_posix()}. This story measures "
            f"the corpus Story 13.5 recorded; it does not re-derive or re-ratify it."
        )
    existing = _load_existing()

    if checkout_root is None:
        if not check_only:
            raise Refused(
                "--checkout-root is required to WRITE the artifacts: the class is derived "
                "from the members' pinned blobs and nothing else. --check alone verifies "
                "what this repository can see by itself."
            )
        return _check_without_corpus(existing)

    root = snapshot_root or Path(tempfile.mkdtemp(prefix="argus-silent-"))
    root.mkdir(parents=True, exist_ok=True)
    payload = loads(_ADJUDICATION_SET.read_text(encoding="utf-8"))
    derivation = derive(payload, checkout_root, overrides, root)
    seeded = tuple(derivation.rows)
    if not seeded:
        raise Refused(
            "the derivation produced an EMPTY silent class over a non-empty population. "
            "That is a broken derivation, not a clean corpus, and it is refused rather "
            "than published (AI-E11-1)."
        )
    record = _record_from(carry_forward(seeded, existing), derivation.walked, _METHOD)
    text = _record_text(record)
    worklist = render_worklist(record, derivation)

    if check_only:
        _refuse_stale(_RECORD, text)
        _refuse_stale(_WORKLIST, worklist)
        print(
            f"OK - the silent-class artifacts are current ({len(record.rows)} row(s), "
            f"re-derived from {derivation.walked} recorded finding(s) at the pins)."
        )
        _print_report(record, derivation)
        return 0

    _CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    _RECORD.write_text(text, encoding="utf-8", newline="\n")
    _WORKLIST.write_text(worklist, encoding="utf-8", newline="\n")
    print(
        f"WROTE {_RECORD.relative_to(_REPO_ROOT).as_posix()} and "
        f"{_WORKLIST.relative_to(_REPO_ROOT).as_posix()} - {len(record.rows)} row(s)."
    )
    _print_report(record, derivation)
    return 0


def _check_without_corpus(existing: tuple[SilentClassRow, ...]) -> int:
    if not existing:
        raise Refused(
            f"{_RECORD.relative_to(_REPO_ROOT).as_posix()} is absent or carries no rows. "
            f"Run this script with --checkout-root to derive and write it."
        )
    # Provenance is read back; every DERIVED figure is RECOMPUTED from the rows and then
    # compared byte-for-byte. That is what makes this a check rather than a tautology: a
    # hand-edited count, independence status or smoke-test proportion does not survive it.
    record = record_from_payload(loads(_RECORD.read_text(encoding="utf-8")))
    text = _record_text(record)
    current = _RECORD.read_text(encoding="utf-8")
    if current != text:
        raise Refused(
            f"{_RECORD.relative_to(_REPO_ROOT).as_posix()} does not round-trip through "
            f"argus.store.canonical unchanged - it has been hand-edited or written by "
            f"something other than this script. Re-run: python "
            f"scripts/build_silent_class_record.py --checkout-root <ROOT>"
        )
    if not _WORKLIST.is_file():
        raise Refused(
            f"{_WORKLIST.relative_to(_REPO_ROOT).as_posix()} is absent. The record without "
            f"the worklist is a question nobody can answer."
        )
    print(
        f"OK - the committed silent-class record round-trips through argus.store.canonical "
        f"unchanged ({len(record.rows)} row(s)) and the worklist is present."
    )
    print(
        "NOT RE-DERIVED BY THIS RUN, and NOT a claim that the worklist is current - the "
        "class and every source span in the worklist are read from five third-party "
        "checkouts this run was not given. Pass --checkout-root to re-derive the "
        "membership and re-render the worklist, which is the check that compares bytes."
    )
    return 0


def _refuse_stale(path: Path, expected: str) -> None:
    current = path.read_text(encoding="utf-8") if path.is_file() else ""
    if current != expected:
        raise Refused(
            f"{path.relative_to(_REPO_ROOT).as_posix()} is NOT current. Re-run: python "
            f"scripts/build_silent_class_record.py --checkout-root <ROOT>"
        )


def _print_report(record: SilentClassRecord, derivation: Derivation | None) -> None:
    tally = record.counts()
    print(
        f"class={len(record.live_rows())} by member={record.members_by_id()} "
        f"files={record.files_by_member_id()} live: "
        + ", ".join(f"{name}={tally[name]}" for name in sorted(tally))
    )
    print(f"independence (THIS record, gates nothing): {record.independence().status}")
    print(f"smoke-test proportion: {record.smoke_test_proportion().note}")
    print(f"expert hours: {record.expert_hours_sentence()}")
    if derivation is not None:
        print(
            "corpus member porcelain, CAPTURED AND REPORTED, asserted nowhere "
            f"(DN-16-7-4): {derivation.porcelain}"
        )
        print(f"pin verifications: {len(derivation.verifications)} member(s), all proved")
        print(
            f"triage colour only (DN-16-7-5): {derivation.commented} of "
            f"{len(record.rows)} span(s) contain a comment character somewhere. That is a "
            f"fact about punctuation, not about intent; it seeds nothing and orders nothing."
        )
        if derivation.redacted:
            print(f"REDACTED span(s) (AC8.6): {derivation.redacted}")
    print(
        "NOTHING IS ADJUDICATED AND NOTHING IS PROMOTED. Every row is UNADJUDICATED, "
        "carries no adjudicator, and stays verdict_eligible=false. The TP/FP/BORDERLINE "
        "judgement is the named human's act (protocol section 2/4)."
    )


def render_worklist(record: SilentClassRecord, derivation: Derivation | None) -> str:
    """Render the human worklist FROM THE RECORD — never hand-written, never hand-edited.

    ``blocking-worklist-13-5.md``'s own precedent, including its *"do not hand-edit: re-run
    the script"* header. The record is the single source; this function adds only the
    source spans, which by AC8.6 live here and nowhere else.
    """
    live = record.live_rows()
    lines: list[str] = []
    lines.append("# Silent-test-class adjudication worklist - Story 16.7")
    lines.append("")
    lines.append(
        "> DERIVED by `scripts/build_silent_class_record.py` from "
        "`silent-class-record.json`. Do not hand-edit: re-run the script. Every row below "
        "is an **advisory** finding and stays one - this worklist promotes nothing, moves "
        "no threshold, and does not touch `adjudication-record.json` or "
        "`gate-decision-record.json`."
    )
    lines.append("")
    lines.append("## THE JUDGEMENT THIS FILE ASKS FOR, AND WHO MAY MAKE IT")
    lines.append("")
    lines.append(
        f"**{len(live)} row(s) await a named human.** No automated producer may supply the "
        "answer: protocol section 2 registers `UNADJUDICATED` as *the ONLY member an "
        "automated producer may write*, and *an autonomous story that tags its own findings "
        "TP has measured nothing*. Story 16.7 therefore built the instrument, seeded the "
        "rows, published this file, and STOPPED."
    )
    lines.append("")
    lines.append("Registered adjudicators (protocol section 2), for the `adjudicator` field:")
    lines.append("")
    lines.append("- `XAgent007 (Engineering Lead)` - primary adjudicator.")
    lines.append(
        "- `Veer Pratap Singh (QA Lead)` - second reviewer, role FILLED 2026-08-22 by "
        "operator act."
    )
    lines.append(
        "- **External adjudicator - UNFILLED.** Protocol section 4's ladder is three steps: "
        "(1) re-examine the locator, (2) correct the golden key and re-run, (3) external "
        "tie-break. Only PERSISTENT DISAGREEMENT between the two filled roles reaches step "
        "3, and a run that reaches it must STOP and report the rows rather than resolve "
        "them by default. A `BORDERLINE` on its own is NOT step 3 - it is a first-class "
        "recorded outcome meaning *looked at, could not decide*."
    )
    lines.append("")
    lines.append("Each row needs FOUR things, and the row's constructor refuses anything less:")
    lines.append("")
    lines.append(
        "1. a `disposition` from " + ", ".join(f"`{name}`" for name in sorted(DISPOSITIONS)) + ";"
    )
    lines.append(
        "2. an `idiom` from " + ", ".join(f"`{name}`" for name in sorted(IDIOMS)) + " - a "
        "SEPARATE axis from the disposition, so a row may be `FP` **and** "
        "`DELIBERATE_SMOKE_TEST` at once, and that combination is the measurement;"
    )
    lines.append("3. an `adjudicator` id of the exact form `<who> (<role>)`; and")
    lines.append("4. an `adjudicated_on` date and a `reason` - a judgement with no reason cannot")
    lines.append("   be re-examined, and section 4's ladder IS a re-examination procedure.")
    lines.append("")
    lines.append("## THE CLASS")
    lines.append("")
    lines.append(f"`{record.class_definition}`")
    lines.append("")
    lines.append(
        "By corpus member: "
        + ", ".join(f"**{name}** {count}" for name, count in record.members_by_id().items())
        + " - across "
        + ", ".join(f"{count} file(s) in {name}" for name, count in record.files_by_member_id().items())
        + "."
    )
    lines.append("")
    lines.append(f"Exhaustiveness: {record.exhaustiveness()}")
    lines.append("")
    lines.append(f"Smoke-test proportion: {record.smoke_test_proportion().note}")
    lines.append("")
    lines.append(f"Expert hours: {record.expert_hours_sentence()}")
    lines.append("")
    lines.append(f"Independence of THIS record: {record.independence().note}")
    lines.append("")
    if derivation is not None:
        lines.append(
            f"Triage colour, and it is NOT a judgement: {derivation.commented} of "
            f"{len(live)} span(s) contain a comment character somewhere in the span. That "
            "is a fact about punctuation and has no established relationship to intent. It "
            "does not seed the `idiom` field, it does not default it, and it does not order "
            "this worklist - the rows below are sorted by member and locator only "
            "(`DN-16-7-5`)."
        )
        lines.append("")
    lines.append(f"> {_CARVE_OUT}")
    lines.append("")
    for member_id in sorted({row.member_id for row in live}):
        rows = [row for row in live if row.member_id == member_id]
        lines.append(f"## {member_id} - {len(rows)} member(s) of the silent class")
        lines.append("")
        lines.append(f"Pin `{rows[0].pinned_sha}`")
        lines.append("")
        for row in sorted(rows, key=lambda item: item.locator):
            lines.extend(_render_row(row, derivation))
    lines.append("")
    lines.append(
        "_Nothing above is adjudicated. Every row is `UNADJUDICATED` and carries no "
        "adjudicator - which is the honest state, and the state protocol section 2 says an "
        "automated producer must leave it in._"
    )
    lines.append("")
    return "\n".join(lines)


def _render_row(row: SilentClassRow, derivation: Derivation | None) -> list[str]:
    out: list[str] = []
    out.append(f"### `{row.locator}` - `{row.test_name}`")
    out.append("")
    out.append(
        f"- disposition: `{row.disposition}` · idiom: `{row.idiom}` · adjudicator: "
        f"`{row.adjudicator or 'NONE'}` · date: `{row.adjudicated_on or 'NONE'}`"
    )
    out.append(
        f"- measured: `discarded_sut_calls={row.discarded_sut_calls}` "
        f"`consumed_sut_calls={row.consumed_sut_calls}` · row id `{row.row_id}`"
    )
    out.append("")
    span = None if derivation is None else derivation.spans.get(row.locator)
    if span is None:
        out.append(
            "_Span not rendered by this run: re-run with `--checkout-root` to read it from "
            "the pinned blob._"
        )
        out.append("")
        return out
    if not span:
        out.append(
            "_**REDACTED (AC8.6).** The shipped hardcoded-secret detector flagged a line "
            "inside this span, so the span is withheld and only its locator is published. "
            "Read it at the pin named above._"
        )
        out.append("")
        return out
    out.append("```python")
    out.extend(text.rstrip() for text in span)
    out.append("```")
    out.append("")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed artifacts are current; write nothing.",
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
            "Directory the pinned blobs are materialized under. Use a SHORT path on "
            "Windows: the deepest in-scope path here is long enough that the default temp "
            "root can push the absolute path past MAX_PATH, and a partially-extracted tree "
            "derives clean."
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
            if Path(relative).is_absolute():
                raise Refused(
                    f"--map {pair!r} names an ABSOLUTE path. It must be relative to "
                    f"--checkout-root, because pathlib discards the left operand when the "
                    f"right one is absolute - which silently escapes the root entirely."
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
