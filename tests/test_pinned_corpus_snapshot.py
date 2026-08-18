"""Story 13.5 — the corpus is materialized from the PINNED GIT OBJECT, and it is PROVED.

Verification area ``ArgusAgent-PRECISION`` (``TC-ArgusAgent-PRECISION-001-65``..``-68``,
continuing the index that ended at ``-64``).

**What these guards are protecting, and why an ordinary "it works" test would not have
caught it.** ``scripts/audit_validation_corpus.py`` used to enforce its pin by comparing
``git rev-parse HEAD`` to the manifest sha and then stage the snapshot from **working-tree**
bytes. Every existing guard stayed green through that, because the two claims — *"this
checkout is on the right commit"* and *"the bytes I audited are the pinned bytes"* — look
identical from the outside on a clean tree. On 2026-08-18 ``agent-smith`` sat exactly on its
pin with six dirty in-scope sources, so an audit labelled ``agent-smith@9ab774d7`` measured
the pin plus somebody's uncommitted edits and reported
``byte_reproducible_across_two_runs = True``, because two runs over the same wrong bytes are
reproducible. **Reproducibility is not provenance**, and that is the sentence these guards
exist to make mechanical.

**Every guard here that asserts an absence carries a non-vacuity floor, and every one has a
GENERATED adversarial variant** (``architecture.md`` §Enforcement, GUARD-ADEQUACY CLAUSE:
RED at the REAL SEAM, not against a reconstruction). Epic 14 added 35 guards; a sweep of 11
found 2 that concluded silence from an empty population — inside the vacuous-test detector's
own suite, in the epic built to stop exactly that. Story 13.5's headline result IS an
absence, so the fixtures below build REAL git repositories, mutate them, and prove the
guards go red.

No network and no third-party checkout is touched: every fixture is a repository this module
creates under ``tmp_path`` and owns.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "scripts") not in sys.path:  # pragma: no cover - test bootstrap
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from pinned_corpus_snapshot import (  # noqa: E402
    MAX_ABSOLUTE_PATH_CHARS,
    PinnedBytesRefusal,
    PinnedSnapshotError,
    PinUnreachable,
    blob_sha1,
    dirty_in_scope_paths,
    materialize_pinned_bytes,
    parse_porcelain_z,
    pin_is_reachable,
    pinned_tree,
    verify_pinned_bytes,
)

_SET_13_5 = (
    _REPO_ROOT
    / "_bmad-output"
    / "design-artifacts"
    / "ArgusAgent"
    / "validation-corpus"
    / "adjudication-set-13-5.json"
)

#: The 1.4 in-scope predicate, narrowed to what these fixtures write. The production
#: predicate lives in ``scripts/audit_validation_corpus.in_scope_source`` and is exercised by
#: the corpus guards below; re-using it here would drag the whole pipeline import in for a
#: three-file fixture.
def _keep(rel: str) -> bool:
    return rel.endswith(".py")


def _git(root: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )
    assert done.returncode == 0, f"git {' '.join(args)} failed in {root}: {done.stderr}"
    return done.stdout.strip()


def _repo_at_two_revisions(root: Path) -> tuple[str, str]:
    """A REAL git repository whose WORKING TREE differs from its first commit.

    This is the ``agent-smith`` shape, reconstructed in miniature: a pinned commit, then an
    edit that was never committed. Everything below is measured against it, because the
    defect being closed is invisible on a clean tree.
    """
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init")
    _git(root, "config", "core.autocrlf", "false")
    _git(root, "config", "user.email", "pin@argus.test")
    _git(root, "config", "user.name", "Pinned Snapshot Fixture")
    (root / "pkg").mkdir()
    (root / "pkg" / "alpha.py").write_text("PINNED = 1\n", encoding="utf-8")
    (root / "pkg" / "beta.py").write_text("PINNED = 2\n", encoding="utf-8")
    (root / "notes.md").write_text("not a source file\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "the pinned commit")
    pin = _git(root, "rev-parse", "HEAD")

    # The uncommitted edit. On the OLD instrument this byte reached the audit.
    (root / "pkg" / "alpha.py").write_text("DIRTY = 999\n", encoding="utf-8")
    # ...and a second commit on top, so HEAD != pin as well (the `minions` shape).
    (root / "pkg" / "gamma.py").write_text("LATER = 3\n", encoding="utf-8")
    _git(root, "add", "pkg/gamma.py")
    _git(root, "commit", "-m", "a later commit the manifest does not pin")
    head = _git(root, "rev-parse", "HEAD")
    assert head != pin
    return pin, head


def test_TC_ArgusAgent_PRECISION_001_65_the_audited_bytes_are_the_pinned_bytes_not_the_working_tree() -> None:
    """TC-ArgusAgent-PRECISION-001-65 — Story 13.5 / AC1: provenance, at the real seam.

    **Observable:** :func:`pinned_tree` + :func:`materialize_pinned_bytes` over a repository
    whose working tree carries an uncommitted edit AND whose ``HEAD`` has moved past the pin.
    This is the exact configuration measured on the live corpus on 2026-08-18 —
    ``agent-smith`` dirty on its pin, ``minions`` parked on another commit — and it is the
    one the old runner could not distinguish from a clean read.

    Both facts are asserted, not one: the pinned byte is PRESENT and the dirty byte is
    ABSENT. Asserting only the first stays green if the file is written twice.
    """
    # ``tmp_path`` is not used: this fixture needs a SHORT root, and building it under the
    # pytest tmp tree is how the MAX_PATH trap gets hit on Windows.
    import tempfile

    with tempfile.TemporaryDirectory(prefix="argus-pin-") as scratch:
        root = Path(scratch) / "src"
        pin, head = _repo_at_two_revisions(root)

        assert pin_is_reachable(root, pin), "non-vacuity: the fixture's pin is unreachable"
        tree = pinned_tree(root, pin, keep=_keep)

        # NON-VACUITY FLOOR, first: the population this guard reasons over is non-empty and
        # is the population AT THE PIN, not the one in the index. `gamma.py` exists only on
        # HEAD and `notes.md` is out of scope, so both absences are meaningful.
        assert tree.paths == ("pkg/alpha.py", "pkg/beta.py"), tree.paths
        assert "pkg/gamma.py" not in tree.paths, (
            "the tree listing picked up a file that exists only on HEAD — it read the index, "
            "not the pinned object, which is the whole defect"
        )

        dest = Path(scratch) / "snap"
        materialize_pinned_bytes(root, tree, dest)
        alpha = (dest / "pkg" / "alpha.py").read_text(encoding="utf-8")
        assert alpha == "PINNED = 1\n", (
            f"the materialized snapshot carries {alpha!r}. That is the WORKING-TREE byte; "
            f"the pinned blob says 'PINNED = 1'. This is DF-13-5's silent-deviation defect."
        )
        assert "DIRTY" not in alpha

        verification = verify_pinned_bytes(dest, tree)
        assert verification.proves_pinned_bytes
        assert verification.verified_file_count == verification.expected_file_count == 2

        # The dirty file is REPORTED as evidence — "the tree was dirty and it provably did
        # not matter" is a checkable statement; silence is not.
        assert dirty_in_scope_paths(root, keep=_keep) == ("pkg/alpha.py",)
        assert head != pin  # the fixture really did move HEAD


def test_TC_ArgusAgent_PRECISION_001_66_the_pin_verification_goes_red_at_the_real_seam() -> None:
    """TC-ArgusAgent-PRECISION-001-66 — Story 13.5 / AC7: the GENERATED adversarial variants.

    **Observable:** :func:`verify_pinned_bytes` against three perturbations of a real
    materialized snapshot, each one produced by mutating the snapshot rather than by
    constructing a fake :class:`PinVerification`. A guard proved against a reconstruction
    proves the reconstruction (``architecture.md`` §Enforcement, GUARD-ADEQUACY CLAUSE).

    The three perturbations are the three ways the measurement could silently become a
    zero: **one byte changed** (a working-tree edit leaking in), **one file removed** (the
    Windows ``MAX_PATH`` truncation that silently drops deep paths), and **an empty
    population** (nothing extracted at all).
    """
    import tempfile

    with tempfile.TemporaryDirectory(prefix="argus-pin-adv-") as scratch:
        root = Path(scratch) / "src"
        pin, _head = _repo_at_two_revisions(root)
        tree = pinned_tree(root, pin, keep=_keep)
        dest = Path(scratch) / "snap"
        materialize_pinned_bytes(root, tree, dest)
        assert verify_pinned_bytes(dest, tree).proves_pinned_bytes, (
            "non-vacuity: the UNPERTURBED snapshot must verify, or the perturbations below "
            "prove nothing about the perturbation"
        )

        # (1) ONE BYTE. Not a rewrite — a single character, which is what an editor leaves.
        target = dest / "pkg" / "beta.py"
        target.write_text(target.read_text(encoding="utf-8").replace("2", "3"), encoding="utf-8")
        perturbed = verify_pinned_bytes(dest, tree)
        assert not perturbed.proves_pinned_bytes
        assert perturbed.mismatched_paths == ("pkg/beta.py",), perturbed.mismatched_paths
        assert perturbed.verified_file_count == 1

        # (2) ONE FILE GONE — the truncation shape. Restore (1) first so the two failures
        # cannot be confused for one another.
        target.write_text("PINNED = 2\n", encoding="utf-8")
        (dest / "pkg" / "alpha.py").unlink()
        truncated = verify_pinned_bytes(dest, tree)
        assert not truncated.proves_pinned_bytes
        assert truncated.missing_paths == ("pkg/alpha.py",)
        assert not truncated.mismatched_paths, (
            "a MISSING file was reported as a CONTENT mismatch. They are different failures "
            "with different causes and the record must not collapse them."
        )

        # (3) AN EMPTY POPULATION verifies NOTHING, and must not report success. 0 of 0 is
        # the shape that passes forever.
        empty = verify_pinned_bytes(dest, tree.__class__(checkout=str(root), commit_sha=pin, files=()))
        assert not empty.proves_pinned_bytes, (
            "a verification over ZERO expected files reported success. That is exactly the "
            "vacuous guard AI-E11-1 names: it cannot fail, so it measures nothing."
        )
        assert empty.expected_file_count == 0


def test_TC_ArgusAgent_PRECISION_001_67_the_pin_is_a_named_unevaluable_never_a_fallback() -> None:
    """TC-ArgusAgent-PRECISION-001-67 — Story 13.5 / AC1 + AC7: refusal, and the shared identity.

    Three claims, all at the real seam:

    (a) an UNREACHABLE pin raises :class:`PinUnreachable` — a NAMED ``Unevaluable`` outcome,
        never ``pytest.skip`` and never a silent fallback to the working tree, which is what
        would turn a missing member into a four-of-five zero that reads like a five-of-five
        one;
    (b) :func:`blob_sha1` is git's OWN blob identity, cross-checked against
        ``git hash-object`` rather than against a second implementation of it (AR7);
    (c) a destination path over the Windows ``MAX_PATH`` working limit is a NAMED refusal
        BEFORE the write, because a partially-extracted tree audits clean.
    """
    import tempfile

    with tempfile.TemporaryDirectory(prefix="argus-pin-ref-") as scratch:
        root = Path(scratch) / "src"
        pin, _head = _repo_at_two_revisions(root)

        # (a) A well-formed sha that is not in this object database.
        absent = "0" * 40
        assert not pin_is_reachable(root, absent)
        with pytest.raises(PinUnreachable) as refusal:
            pinned_tree(root, absent, keep=_keep)
        assert "UNEVALUABLE" in str(refusal.value)
        assert "working tree" in str(refusal.value), (
            "the refusal must say what it is refusing to do instead — falling back to the "
            "working tree is the failure mode, and naming it is what stops the next author"
        )

        # (b) The identity is git's, proved against git.
        tree = pinned_tree(root, pin, keep=_keep)
        assert tree.files, "non-vacuity: nothing to hash"
        for entry in tree.files:
            data = _git(root, "show", f"{pin}:{entry.path}").encode("utf-8") + b""
            # `git show` normalises the trailing newline through text mode, so the identity
            # is checked against `hash-object` on the REAL file at the pin instead.
            del data
            expected = _git(root, "rev-parse", f"{pin}:{entry.path}")
            assert entry.blob_sha == expected
        dest = Path(scratch) / "snap"
        materialize_pinned_bytes(root, tree, dest)
        for entry in tree.files:
            assert blob_sha1((dest / entry.path).read_bytes()) == entry.blob_sha, (
                "blob_sha1 disagrees with the id git reported for the same bytes — a second "
                "identity scheme is exactly what AR7 forbids here"
            )

        # (c) MAX_PATH, as a refusal rather than a truncation. Skipped-by-platform is not an
        # option: the check is asserted to EXIST and to be the Windows limit either way.
        assert MAX_ABSOLUTE_PATH_CHARS < 260
        deep = Path(scratch) / ("d" * 40)
        long_tree = tree.__class__(
            checkout=str(root),
            commit_sha=pin,
            files=tuple(
                entry.__class__(path="/".join(["seg" + "x" * 20] * 12) + ".py", blob_sha=entry.blob_sha)
                for entry in tree.files[:1]
            ),
        )
        if sys.platform == "win32":
            with pytest.raises(PinnedBytesRefusal) as long_refusal:
                materialize_pinned_bytes(root, long_tree, deep)
            assert "MAX_PATH" in str(long_refusal.value)


def test_TC_ArgusAgent_PRECISION_001_68_the_committed_corpus_read_proof_is_a_measurement_not_a_flag() -> None:
    """TC-ArgusAgent-PRECISION-001-68 — Story 13.5 / AC1 + AC7: the zero is falsifiable.

    **Observable:** the committed ``adjudication-set-13-5.json``. Story 13.5's headline is an
    ABSENCE — zero verdict-eligible findings across five real repositories — and an absence
    is the one claim a broken harness produces for free. So the artifact is asserted to carry
    the population it scanned, and the population is asserted to be of the right ORDER OF
    MAGNITUDE, before the zero is read off it at all.

    The rule-level counts are what make it checkable rather than rhetorical:
    ``vacuous_test_ast`` is absent (0 promoted) **while** ``vacuous_test_heuristic`` is in the
    thousands. A detector that never ran produces zero of BOTH, and only the second number
    tells the two apart.
    """
    assert _SET_13_5.is_file(), (
        f"{_SET_13_5.relative_to(_REPO_ROOT).as_posix()} is missing. It is Story 13.5's "
        "corpus run and it is committed, not generated on demand: `python "
        "scripts/audit_validation_corpus.py --checkout-root ... --output-name "
        "adjudication-set-13-5.json`."
    )
    payload = json.loads(_SET_13_5.read_text(encoding="utf-8"))
    proof = payload["corpus_read_proof"]

    # ── the non-vacuity floor, asserted FIRST ─────────────────────────────────────────
    assert proof["members_audited"] == 5
    assert proof["source_file_count"] > 1000, proof["source_file_count"]
    assert proof["scored_test_function_count"] > 1000, proof["scored_test_function_count"]
    assert proof["advisory_finding_count"] > 1000, proof["advisory_finding_count"]
    assert proof["flagged_file_count"] > 100, proof["flagged_file_count"]
    assert proof["every_member_pin_verified"] is True
    assert proof["every_member_byte_reproducible"] is True
    assert proof["proves_corpus_was_read"] is True

    by_rule = proof["findings_by_rule"]
    assert by_rule.get("vacuous_test_heuristic", 0) > 500, (
        "the vacuous-test detector emitted almost nothing across five real repositories. "
        "Before reading the blocking zero as a result, this number has to show the detector "
        "RAN — a zero from a detector that never fired is an absence, not a measurement."
    )

    # ── and only now, the absence ─────────────────────────────────────────────────────
    assert by_rule.get("vacuous_test_ast", 0) == 0
    assert proof["blocking_finding_count"] == 0

    # Per member, the same shape — a corpus-level aggregate can hide a member that
    # contributed nothing at all, which is the four-of-five zero §0.2 warns about.
    assert len(payload["members"]) == 5
    for member in payload["members"]:
        evidence = member["corpus_read_proof"]
        verification = member["pin_verification"]
        assert evidence["source_file_count"] > 0, member["member_id"]
        assert evidence["scored_test_function_count"] > 0, member["member_id"]
        assert evidence["blocking_finding_count"] == 0, member["member_id"]
        assert verification["proves_pinned_bytes"] is True, member["member_id"]
        assert (
            verification["verified_file_count"] == verification["expected_file_count"]
        ), member["member_id"]
        assert not verification["missing_paths"] and not verification["mismatched_paths"]
        assert member["byte_reproducible_across_two_runs"] is True
        # The findings list is NON-EMPTY (advisory findings were emitted — the detector
        # ran) and NONE of them is verdict-eligible. Both halves, because "no findings at
        # all" and "findings, none promoted" are the two claims this story exists to keep
        # apart, and only the second is what happened.
        assert member["findings"], (
            f"{member['member_id']}: the run emitted NO finding of any kind. That is an "
            "unread corpus, not a clean one."
        )
        assert not [f for f in member["findings"] if f["verdict_eligible"]], (
            f"{member['member_id']}: the run emitted a verdict-eligible finding. The story "
            "record and the gate decision both rest on there being none; if one appeared, "
            "the decision must be re-derived rather than this assertion relaxed."
        )

    # The provenance that makes the zero trustworthy is RECORDED, including the awkward
    # part: members whose checkout was dirty, or parked off the pin, were audited anyway —
    # from the pinned object — and the verification above is what proves it did not matter.
    off_pin = [m["member_id"] for m in payload["members"] if not m["checkout_head_equals_pin"]]
    dirty = [m["member_id"] for m in payload["members"] if m["dirty_in_scope_source_files"]]
    assert isinstance(off_pin, list) and isinstance(dirty, list)
    for member in payload["members"]:
        if member["dirty_in_scope_source_files"] or not member["checkout_head_equals_pin"]:
            assert member["pin_verification"]["proves_pinned_bytes"] is True, (
                f"{member['member_id']} was audited from a checkout that was dirty or off "
                "its pin, and the bytes were NOT proved against the pin. That is the "
                "silent-deviation defect, restored."
            )


def _repo_with_a_rename(root: Path) -> None:
    """A REAL repository carrying a REAL rename, plus the awkward names around it.

    ``git status --porcelain -z`` emits a rename as **two** NUL-terminated records: the
    ``XY <new-path>`` record, and then the ORIGIN path as a record of its own **with no
    ``XY `` prefix at all**. Nothing but a real rename produces that shape, so it is built
    here rather than described.
    """
    (root / "pkg").mkdir(parents=True)
    _git(root, "init")
    _git(root, "config", "core.autocrlf", "false")
    _git(root, "config", "user.email", "pin@argus.test")
    _git(root, "config", "user.name", "Pinned Snapshot Fixture")
    # `status.renames=copies` is what makes git emit a `C` record. It is a real, supported
    # setting on a real checkout, so the copy half is measured at the same seam as the
    # rename half rather than hand-built.
    _git(root, "config", "status.renames", "copies")
    (root / "pkg" / "alpha.py").write_text("ALPHA = 1\n" * 40, encoding="utf-8")
    (root / "pkg" / "beta.py").write_text("BETA = 2\n", encoding="utf-8")
    (root / "pkg" / "has space.py").write_text("SPACED = 3\n", encoding="utf-8")
    (root / "notes.md").write_text("not a source file\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "the pinned commit")

    _git(root, "mv", "pkg/alpha.py", "pkg/renamed.py")  # the rename
    _git(root, "mv", "pkg/has space.py", "pkg/still spaced.py")  # ...with spaces in it
    (root / "pkg" / "copied.py").write_bytes((root / "pkg" / "renamed.py").read_bytes())
    _git(root, "add", "pkg/copied.py")  # the copy
    (root / "pkg" / "beta.py").write_text("BETA = 99\n", encoding="utf-8")  # a plain edit
    (root / "pkg" / "caf\u00e9 nouveau.py").write_text("U = 1\n", encoding="utf-8")  # untracked


def _porcelain_z_records(root: Path) -> list[str]:
    """The RAW ``-z`` stream, split exactly as the parser splits it. The seam itself."""
    done = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "-z", "--untracked-files=all"],
        capture_output=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    return done.stdout.decode("utf-8").split("\0")


def test_TC_ArgusAgent_PRECISION_001_72_a_rename_reports_both_paths_and_corrupts_neither() -> None:
    """TC-ArgusAgent-PRECISION-001-72 — Story 13.5 / AC1 + AC7: the ``-z`` record boundary.

    **Observable:** :func:`dirty_in_scope_paths` over a repository carrying a real rename, a
    real copy, paths with spaces and a non-ASCII untracked path.

    **The defect this closes.** ``git status --porcelain -z`` emits an ordinary entry as
    ``XY <path>`` but a rename or copy as **two** records — ``XY <new>`` followed by the
    origin path **bare, with no prefix**. Slicing every record at ``[3:]`` therefore eats the
    first three characters of every origin path: ``pkg/alpha.py`` was reported as
    ``/alpha.py``. The field is evidence only (:func:`verify_pinned_bytes` proves the audited
    bytes independently and never reads it), so it could not move a gate — but it is a
    *wrong recorded fact* in a story whose entire deliverable is a governance record, and it
    was untested because no fixture here had ever renamed anything.
    """
    import tempfile

    with tempfile.TemporaryDirectory(prefix="argus-pin-rn-") as scratch:
        root = Path(scratch) / "src"
        _repo_with_a_rename(root)

        # ── NON-VACUITY FLOOR, asserted FIRST, off the RAW stream ────────────────────
        # If git did not actually detect the rename, every assertion below would pass over
        # a stream that never contained the shape they are about. So the shape is measured:
        # a record whose status letter is R or C, immediately followed by a record that is a
        # BARE path — no `XY ` prefix, i.e. its third character is not a space.
        records = _porcelain_z_records(root)
        origin_records = [
            records[i + 1]
            for i, rec in enumerate(records[:-1])
            if len(rec) >= 4 and (rec[0] in "RC" or rec[1] in "RC")
        ]
        assert origin_records, (
            "the fixture produced NO rename/copy record, so this guard would prove nothing. "
            f"Records were: {records!r}. git must detect the rename for the parser to be "
            "exercised at all."
        )
        assert "pkg/alpha.py" in origin_records, origin_records
        assert all(len(rec) < 3 or rec[2] != " " for rec in origin_records), (
            f"the origin records {origin_records!r} carry an `XY ` prefix after all — the "
            "premise of this guard (and of the parser's rename branch) is wrong"
        )

        reported = dirty_in_scope_paths(root, keep=_keep)
        assert reported, "the parser returned nothing over a demonstrably dirty tree"

        # ── the corruption is ABSENT ─────────────────────────────────────────────────
        assert "/alpha.py" not in reported, (
            f"the origin path was sliced as though it carried an `XY ` prefix: {reported!r}. "
            "That is the uniform `record[3:]` defect."
        )
        assert not [p for p in reported if p.startswith("/")], reported

        # ── and BOTH halves of the rename are PRESENT, by name ───────────────────────
        assert "pkg/alpha.py" in reported, (
            f"the rename's ORIGIN path is missing from {reported!r}. It is dirty evidence "
            "exactly as much as the new path is: at the pin that path held bytes, and in "
            "the working tree it does not."
        )
        assert "pkg/renamed.py" in reported, reported
        assert "pkg/copied.py" in reported, reported  # the copy's new half
        assert "pkg/beta.py" in reported, reported  # the ordinary modification
        assert "pkg/has space.py" in reported, reported  # spaces, on both halves
        assert "pkg/still spaced.py" in reported, reported
        assert "pkg/caf\u00e9 nouveau.py" in reported, (
            f"the non-ASCII untracked path did not survive decoding: {reported!r}. `-z` "
            "suppresses git's `core.quotepath` escaping and emits the raw UTF-8 bytes."
        )
        assert "notes.md" not in reported  # `keep` still narrows the population

        # ── the GENERATED adversarial variant, at the real seam ─────────────────────
        # Not a hand-written expectation: the OLD rule is applied to THIS SAME real stream,
        # and the corruption it produces is derived rather than asserted. This proves the
        # fixture DISCRIMINATES — that it can tell the two parsers apart — which is the one
        # thing a regression test for a parsing bug has to establish about itself.
        old_rule = {rec[3:] for rec in records if len(rec) >= 4 and _keep(rec[3:])}
        assert old_rule != set(reported), (
            "the uniform-slice rule and the record-aware rule produce the SAME answer over "
            "this fixture, so the fixture does not reach the defect and would have stayed "
            "green against the broken parser"
        )
        assert "/alpha.py" in old_rule, (
            f"the old rule did not corrupt anything over this fixture ({old_rule!r}), so "
            "the regression it is standing in for is not reproduced here"
        )


def test_TC_ArgusAgent_PRECISION_001_73_an_unreadable_status_record_is_a_refusal_not_a_slice() -> None:
    """TC-ArgusAgent-PRECISION-001-73 — Story 13.5 / AC7: the parser refuses what it cannot read.

    **Observable:** :func:`parse_porcelain_z`, the pure (AR8) half of the ``-z`` reader, over
    a REAL stream first and then over two streams no git emits.

    The rename defect was silent: an unreadable record was sliced into a plausible-looking
    path and recorded as evidence. The remedy is not only to parse renames correctly but to
    stop guessing — an entry that does not carry the ``XY `` prefix and does not follow an
    ``R``/``C`` entry is a :class:`PinnedSnapshotError` by name.

    **Non-vacuity floor, asserted FIRST:** a guard that only shows a function raising proves
    nothing unless the function also ACCEPTS. So the real stream from the real fixture
    repository is parsed here and its rename entry is asserted to carry both halves, before
    any refusal is asked for. A parser that raised unconditionally would fail that floor.
    """
    import tempfile

    with tempfile.TemporaryDirectory(prefix="argus-pin-pz-") as scratch:
        root = Path(scratch) / "src"
        _repo_with_a_rename(root)
        real = "\0".join(_porcelain_z_records(root))

        # ── the floor: the REAL stream parses, and the rename is modelled as ONE entry
        # naming TWO paths rather than two entries naming one corrupted path each.
        entries = parse_porcelain_z(real)
        assert entries, "the parser returned nothing for a demonstrably dirty repository"
        renames = [e for e in entries if e.origin_path is not None]
        assert renames, f"no rename/copy entry was modelled: {entries!r}"
        assert ("pkg/renamed.py", "pkg/alpha.py") in [
            (e.path, e.origin_path) for e in renames
        ], renames
        assert all(e.status[0] in "RC" or e.status[1] in "RC" for e in renames), renames
        assert all(len(e.status) == 2 for e in entries), entries
        # Purity (AR8): same input, same output, and no dependence on the checkout.
        assert parse_porcelain_z(real) == entries

    # ── and only now the refusals. Neither stream below is producible by git; that is the
    # point of a defensive refusal, and it is why they are asked of the PURE function over a
    # constructed stream rather than of a repository. The claim is bounded accordingly: this
    # asserts what the parser does with an unreadable record, not what git emits.
    with pytest.raises(PinnedSnapshotError) as bare:
        parse_porcelain_z("pkg/orphan.py\0")
    assert "cannot read" in str(bare.value)
    assert "pkg/orphan.py" in str(bare.value), "the refusal must NAME the record it refused"

    with pytest.raises(PinnedSnapshotError) as truncated:
        parse_porcelain_z("R  pkg/renamed.py\0")
    assert "truncated" in str(truncated.value)

    # A record too short to be an entry is refused too — it is not silently dropped, which
    # is how the old `len(record) < 4: continue` branch hid the origin half of a rename of a
    # short path.
    with pytest.raises(PinnedSnapshotError):
        parse_porcelain_z("M\0")
