"""Story 19.1 — the committed ratification package is complete, honest and ratifies nothing.

⛔ **EVERY ASSERTION HERE READS THE COMMITTED RECORD AND THE MANIFEST. NONE READS THE CORPUS.**
The measurement that produced the record is a LOCAL, operator-side act over checkouts that exist
only on the machine the operator fetched them onto (protocol §6 R2). CI has no ``_bench`` root, so
a guard that walked the corpus would be a guard that is red on the ubuntu matrix for a reason that
has nothing to do with correctness. ``build_silent_class_record``'s ``--check`` path is the
precedent this copies.

⛔ **NON-VACUITY IS ASSERTED BEFORE EVERY ABSENCE.** A guard over an empty record passes, and
this project has filed that defect against itself often enough to name it: the row count is
proved to be six before any per-row claim is made, and the field extractor is proved to have
parsed a non-zero number of fields before any "no such field" claim is made.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import build_ratification_record  # noqa: E402
from build_ratification_record import (  # noqa: E402
    CARRIED_MANIFEST_FIELDS,
    MEASURED_FIELDS,
    RATIFICATION_RECORD_PATH,
    RATIFICATION_WORKLIST_PATH,
    RECOMMENDATION_SUBSTRINGS,
    sealed_member_ids,
)

from tests.corpus._manifest import (  # noqa: E402
    SEALED_PARTITION_TABLE,
    VALIDATION_CORPUS,
    eligible_member_count,
)

_PRODUCER_REL_PATH = "scripts/build_ratification_record.py"

#: AC2.3 — the module names the producer may NEVER import. This is the *fetching* ban of protocol
#: §6 R2, in the shape ``TC-ArgusAgent-PRECISION-001-141`` established.
#:
#: ⛔ ``subprocess`` is deliberately NOT banned here, and the difference from ``-141`` is
#: load-bearing rather than an oversight: ``-141`` guards a PURE criterion that must spawn
#: nothing, while this producer's whole job is to read a git object database, which it does
#: through ``pinned_corpus_snapshot``'s ``ls-tree``/``cat-file`` reads. Banning the network is the
#: claim AC2.3 makes; banning the subprocess would be a claim this module cannot honour and a ban
#: nobody could keep is a ban that gets deleted.
_FORBIDDEN_IMPORTS: tuple[str, ...] = (
    "urllib",
    "requests",
    "httpx",
    "http.client",
    "socket",
    "ftplib",
    "telnetlib",
    "smtplib",
)


def _producer_source() -> str:
    return (_REPO_ROOT / _PRODUCER_REL_PATH).read_text(encoding="utf-8")


def _dotted_imports(source: str) -> set[str]:
    """Every module name *source* imports, as FULL dotted paths. PURE — no I/O (AR8)."""
    imported: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


def _forbidden_imports_seen(source: str) -> tuple[str, ...]:
    """AC2.3's predicate, isolated so it can be driven to BOTH outcomes. PURE."""
    seen = _dotted_imports(source)
    return tuple(
        sorted(
            banned
            for banned in _FORBIDDEN_IMPORTS
            for name in seen
            if name == banned or name.startswith(banned + ".")
        )
    )


@pytest.fixture(scope="module")
def record() -> dict:
    path = _REPO_ROOT / RATIFICATION_RECORD_PATH
    if not path.exists():
        pytest.fail(
            f"no committed ratification record at {RATIFICATION_RECORD_PATH}. Story 19.1's "
            f"deliverable is the record; without it every assertion below would pass vacuously."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def test_TC_ArgusAgent_PRECISION_001_153_the_ratification_package_is_complete_and_ratifies_nothing(
    record: dict,
) -> None:
    """TC-ArgusAgent-PRECISION-001-153 — Story 19.1 AC1, AC2, AC5.

    **Observable, part one — the package is COMPLETE.** The committed record carries exactly one
    row per ``sealed`` member of :data:`SEALED_PARTITION_TABLE`, keyed by ``member_id``, and every
    row carries all eight carried manifest fields plus all five measured fields. A member that
    could not be measured carries ``UNMEASURED`` **with a reason** and is still present: a member
    that contributes nothing is a member the ratio was measured over, never a member quietly
    dropped from the denominator (``POPULATION_DERIVATION``).

    **Observable, part two — the package RATIFIES NOTHING.** ``eligible_member_count()`` is 5 by
    IMPORT, the record agrees, every row's ``eligible_for_n`` is ``False``, and the sealed ∩
    ratified intersection is empty. If any of those moved, an operator act has been performed by
    something that had no authority to perform it.

    **Observable, part three — the package RECOMMENDS NOTHING.** No row key contains any of
    :data:`RECOMMENDATION_SUBSTRINGS`. Protocol §6 R2 reserves *"choosing which repositories are
    legitimate members"* to the operator; a worksheet that ranks has already chosen.

    **Non-vacuity, asserted BEFORE the absences:** the row count is proved to be exactly six and
    the key extractor is proved to have parsed a non-zero number of keys, so *"no recommendation
    field"* below is a MEASURED absence rather than the silence of an empty record.
    """
    # ── NON-VACUITY, FIRST. Every absence claimed below is claimed over a non-empty record. ──
    expected_ids = list(sealed_member_ids())
    assert len(expected_ids) == 6, (
        f"the sealed partition holds {len(expected_ids)} members, not 6. Either the bench moved "
        f"or this guard is reading the wrong table; both make every count below meaningless."
    )
    rows = record["rows"]
    assert len(rows) == 6, (
        f"the committed record holds {len(rows)} rows, not 6. A guard over a short record "
        f"reports absences that are artifacts of the shortfall."
    )
    parsed_keys = {key for row in rows for key in row}
    assert len(parsed_keys) >= 14, (
        f"the extractor parsed only {len(parsed_keys)} distinct row keys ({sorted(parsed_keys)}). "
        f"The 'no recommendation field' assertion below would pass over a record it cannot read."
    )

    # ── AC1.1 / AC1.2 — complete, keyed, and carrying every column. ──
    assert [row["member_id"] for row in rows] == expected_ids, (
        f"rows {[row['member_id'] for row in rows]} are not the sealed partition {expected_ids}."
    )
    for row in rows:
        missing = [
            field
            for field in (*CARRIED_MANIFEST_FIELDS, *MEASURED_FIELDS)
            if field not in row
        ]
        assert not missing, f"{row['member_id']} is missing {missing} — the package is incomplete."

    # ── AC1.4 — UNMEASURED is a value WITH a reason, never a dropped member. ──
    for row in rows:
        unmeasured = [
            field for field in MEASURED_FIELDS if str(row.get(field)) == "UNMEASURED"
        ]
        if unmeasured:
            reason = row.get("unmeasured_reason") or record.get(
                "finding_count_unmeasured_reason"
            )
            assert reason and len(str(reason)) > 40, (
                f"{row['member_id']} reports {unmeasured} UNMEASURED with no usable reason. An "
                f"unexplained blank is indistinguishable from a measurement nobody took."
            )

    # ── AC1.5 — no recommendation, rank, score or ordering by desirability. ──
    offenders = sorted(
        key
        for key in parsed_keys
        for banned in RECOMMENDATION_SUBSTRINGS
        if banned in key.lower()
    )
    assert not offenders, (
        f"the record carries {offenders}. Protocol §6 R2 reserves the choice of legitimate "
        f"members to the operator, and a worksheet that ranks has made that choice for them."
    )

    # ── AC2.1 / AC2.4 — nothing was ratified, and the record says so in its own fields. ──
    assert eligible_member_count() == 5, (
        f"eligible_member_count() is {eligible_member_count()}, not 5. An eligible_for_n has "
        f"flipped: an operator act was performed (story 19.1 AC6.2)."
    )
    assert record["eligible_member_count_before"] == 5
    assert record["eligible_member_count_after"] == 5
    assert record["eligible_for_n_moved_for"] == []
    assert record["ratifies_nothing"] is True
    assert record["recommends_nothing"] is True
    assert record["sealed_ratified_intersection"] == [], (
        f"sealed ∩ ratified is {record['sealed_ratified_intersection']}, not empty. Only a §6 R2 "
        f"operator act can move that, and story 19.1 is not one."
    )
    for row in rows:
        assert row["eligible_for_n"] is False, (
            f"{row['member_id']} is recorded eligible_for_n=True in a package that ratifies "
            f"nothing."
        )

    # ── The carried fields are the manifest's, VERBATIM — not a re-derivation (AC4). ──
    specs = {spec.member_id: spec for spec in VALIDATION_CORPUS}
    for row in rows:
        spec = specs[row["member_id"]]
        for field in CARRIED_MANIFEST_FIELDS:
            assert row[field] == getattr(spec, field), (
                f"{row['member_id']}.{field} in the record does not match the manifest. The "
                f"record must CARRY manifest facts, never restate them from a second derivation."
            )


def test_TC_ArgusAgent_PRECISION_001_153_the_producer_cannot_reach_the_network() -> None:
    """TC-ArgusAgent-PRECISION-001-153 (AC2.3) — 'it never fetches' as a STRUCTURAL property.

    **Observable.** The forbidden module names reachable from ``scripts/build_ratification_record``'s
    AST: ``urllib`` / ``requests`` / ``httpx`` / ``http.client`` / ``socket`` / ``ftplib`` /
    ``telnetlib`` / ``smtplib``.

    **Why it matters.** *"This story reads checkouts the operator already fetched, and fetches
    nothing itself"* is a promise until something makes it unexpressible. Protocol §6 R2 puts
    fetching third-party source outside what an autonomous agent may do, and a producer that could
    open a socket could quietly repair the one member whose pin is unreachable — turning a
    recorded ``UNMEASURED`` into an unrecorded operator act.

    **Non-vacuity, asserted BEFORE the absence:** the walk is proved able to SEE the producer's
    own resolving imports, so the absence below is measured rather than an artifact of a walk that
    parsed nothing.

    **Adversarial, EXECUTED and GENERATED:** one mutant per forbidden name, in both import forms,
    injected into the REAL source text. Every one must be caught.
    """
    source = _producer_source()
    imported = _dotted_imports(source)

    assert "pinned_corpus_snapshot" in imported, (
        f"the walk did not see the `pinned_corpus_snapshot` import among {sorted(imported)}. That "
        f"import is REQUIRED to be visible: it proves the walk resolves this module's imports, so "
        f"the absence of every network module below is a MEASURED absence."
    )
    assert any(name.startswith("tests.corpus") for name in imported), (
        "the walk did not see the dotted `tests.corpus._manifest` import, so it cannot be trusted "
        "to resolve dotted paths such as `http.client`."
    )

    seen = _forbidden_imports_seen(source)
    assert not seen, (
        f"{_PRODUCER_REL_PATH} imports {list(seen)}. It reads checkouts an operator already "
        f"fetched and may never fetch one itself: protocol §6 R2."
    )

    # ── RED, EXECUTED and GENERATED: one mutant per banned name, both import forms. ──
    for banned in _FORBIDDEN_IMPORTS:
        for injected in (f"import {banned}\n", f"from {banned} import thing\n"):
            assert banned in _forbidden_imports_seen(injected + source), (
                f"the network ban missed an injected {injected.strip()!r}. Half the ways to "
                f"breach it are unguarded and the silence above means nothing."
            )
    assert _forbidden_imports_seen("import urllib.request\n" + source), (
        "the ban missed a SUBMODULE import of urllib, so the fetching ban is walkable."
    )


def test_TC_ArgusAgent_PRECISION_001_153_the_worklist_is_committed_beside_the_record(
    record: dict,
) -> None:
    """TC-ArgusAgent-PRECISION-001-153 (AC1.3) — the human worklist exists and names every member.

    **Observable.** The worklist file exists, is non-trivial, and mentions all six ``member_id``s.

    **⛔ Its filename matches NEITHER ``sprint-change-proposal-*.md`` NOR ``epic-*-retro-*.md``,**
    asserted here rather than assumed: ``TC-ArgusAgent-DOCS-001-22`` fires on an unregistered file
    in either family, so a worklist named into one of them would RED a guard this story never
    touched — the ``AI-E17-1`` failure of shipping a deliverable that breaks a neighbour.

    **Non-vacuity:** the file's length is asserted before its contents are searched, so "mentions
    every member" cannot pass over an empty file.
    """
    path = _REPO_ROOT / RATIFICATION_WORKLIST_PATH
    assert path.exists(), f"no worklist at {RATIFICATION_WORKLIST_PATH} (AC1.3)."
    text = path.read_text(encoding="utf-8")
    assert len(text) > 500, (
        f"the worklist is {len(text)} bytes — too short to carry six members and their caveats. "
        f"Searching it for member names below would pass vacuously."
    )

    name = path.name
    assert not name.startswith("sprint-change-proposal-"), (
        f"{name} matches the sprint-change-proposal glob and would RED TC-ArgusAgent-DOCS-001-22."
    )
    assert not (name.startswith("epic-") and "-retro-" in name), (
        f"{name} matches the epic-retro glob and would RED TC-ArgusAgent-DOCS-001-22."
    )

    for member_id, status in SEALED_PARTITION_TABLE:
        if status == "sealed":
            assert member_id in text, f"the worklist never names {member_id} (AC1.3)."

    assert record["finding_count_unmeasured_reason"] in text, (
        "the worklist does not carry the reason the finding-count column is empty. The operator "
        "would meet a blank column with no account of why it is blank."
    )


# ═════════════════════════════════════════════════════════════════════════════════════════
# The --map escape, closed. Review round 1 (2026-08-26) found this producer had copied the
# --map flag shape from `audit_validation_corpus` but only HALF its absolute-path predicate.
# ═════════════════════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize(
    "relative",
    [
        "/etc/passwd",  # POSIX-absolute: Path.is_absolute() is FALSE for this on Windows
        "/",
        "//server/share",
        "C:/Windows",
        r"C:\Windows",
        "D:/_bench",
        # ── Review round 2: DRIVE-RELATIVE, absolute to NEITHER of the first two checks. ──
        # `C:foo` names a drive and then a path relative to THAT DRIVE's working directory.
        # Measured: Path("D:/_bench") / "C:foo" -> "C:foo" — the left operand is discarded just
        # as completely as by a rooted value, so the escape opens through a form that is not
        # "absolute" in the ordinary sense at all.
        "C:foo",
        "C:",
        "D:sub/dir",
    ],
)
def test_TC_ArgusAgent_PRECISION_001_153_absolute_map_paths_are_refused(relative: str) -> None:
    r"""TC-ArgusAgent-PRECISION-001-153 (AC5.4) — an absolute ``--map`` value cannot escape the root.

    **Observable.** :func:`map_path_is_absolute` is ``True`` for every absolute value in BOTH path
    flavours, and ``main()`` refuses the run with exit 2 rather than reading the mapped tree.

    **Why it matters, measured rather than asserted.** ``--map MEMBER_ID=PATH`` promises a path
    *relative to* ``--checkout-root``, and pathlib **discards the left operand** when the right one
    is rooted. ``Path("/etc/passwd").is_absolute()`` is **False** on Windows, so the narrow
    predicate this producer shipped in review round 1 let ``/etc/passwd`` through, and
    ``Path("D:/_bench") / "/etc/passwd"`` resolves to ``D:\etc\passwd`` — already outside the
    directory the operator scoped the run to. On POSIX the root is discarded entirely, which is
    the platform this repository's CI actually runs on.

    ⛔ **ONE DERIVATION, TWO CALLERS.** The predicate lives in ``pinned_corpus_snapshot`` and
    ``audit_validation_corpus`` routes through the same function, so this defect class cannot be
    fixed in one script and left standing in the other (AR7 / ``DN-3``).
    """
    from pinned_corpus_snapshot import map_path_is_absolute

    assert map_path_is_absolute(relative), (
        f"{relative!r} was not recognised as absolute. Joined onto --checkout-root it would read "
        f"a tree outside the directory the operator scoped the run to."
    )

    exit_code = build_ratification_record.main(
        ["--checkout-root", "irrelevant", "--map", f"aws-aws-sam-cli={relative}"]
    )
    assert exit_code == 2, (
        f"--map aws-aws-sam-cli={relative} was accepted (exit {exit_code}). An absolute mapped "
        f"path must be a refusal, never a silently re-rooted read."
    )


@pytest.mark.parametrize(
    "relative",
    [
        "samcli",
        "sub/dir",
        "a/b/c",
        "sentrypy",
        "agent-smith/nested",
        # ⛔ A colon that is NOT a drive. Round 2 added a drive check, and this is the
        # value that proves the check did not simply start refusing every colon.
        "weird:name",
    ],
)
def test_TC_ArgusAgent_PRECISION_001_153_relative_map_paths_are_not_refused(relative: str) -> None:
    """TC-ArgusAgent-PRECISION-001-153 (AC5.4) — the ban's OTHER outcome, so it is not vacuous.

    A predicate that answered ``True`` to everything would pass the refusal test above while
    making the flag unusable. These are the real values the operator passes (``samcli``,
    ``sentrypy``, ``gauth`` …) and every one must be accepted as relative.
    """
    from pinned_corpus_snapshot import map_path_is_absolute

    assert not map_path_is_absolute(relative), (
        f"{relative!r} was refused as absolute. The ban has swallowed the legitimate values and "
        f"the refusal test above proves nothing."
    )


def test_TC_ArgusAgent_PRECISION_001_153_malformed_map_pairs_are_refused() -> None:
    """TC-ArgusAgent-PRECISION-001-153 (AC5.4) — a ``--map`` without ``=`` is a named refusal."""
    for pair in ("no-equals-sign", "=empty-id", "empty-path="):
        assert (
            build_ratification_record.main(["--checkout-root", "irrelevant", "--map", pair])
            == 2
        ), f"--map {pair!r} was accepted; a malformed pair must be a refusal, not a silent skip."
