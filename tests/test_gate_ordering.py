"""Story 16.4 — the ORDERING: §5's three new conditions landed BEFORE any output over a bench member.

Verification area ``TC-ArgusAgent-PRECISION-001-101``..``-102``. A NEW module, for the reason
§0.8 states in figures rather than as a preference: ``tests/test_gate_seal.py`` stands at 1,145
of NFR-M1's 1,200 lines under a FILED split-first trigger (``DF-16-3-A``, 1,180), and 55 lines of
headroom is not a place to put a story's guards.

**The claim this module makes, and why it is a claim about git rather than about intent.**
Story 16.4 spends ``DF-13-5-A``'s ONE bench-expansion round. The three conditions that make the
resulting figure mean what it says — breadth (16.1), the seal (16.2), yield (16.3) — are only
strengthenings if they were in place BEFORE anybody saw a number over a bench member. Stated in a
story file that is an intention; read out of the object database it is evidence. So this module
reads the object database.

⛔ **NOTHING HERE RUNS ARGUS OVER ANY CORPUS MEMBER, fetches anything, or ratifies anything.**
Every subprocess call is ``git cat-file`` / ``git log`` / ``git merge-base`` / ``git rev-list``
against *this* repository — pure reads. This module is the part of Story 16.4 that is permitted
while the story is HALTED on its two operator acts (AC1.4), precisely because it produces no
output over a bench member.

**The vacuity this module was built against.** An ordering guard is the easiest guard in this
repository to write vacuously: ``git log <sha> -- <pathspec>`` returns an empty list both when
the history is clean and when the pathspec is misspelled, and the two are indistinguishable from
the assertion's point of view. ``TC-ArgusAgent-PRECISION-001-75`` and ``-94`` already answer this
correctly and their answer is REUSED here rather than re-invented: a control path known to carry
commits is asserted non-empty **before** the absence it protects, every cited sha is required to
RESOLVE, and the ancestry predicate is driven to **both** outcomes on real shas.

⛔ **The constants are IMPORTED, never re-typed** (``DN-16-4-2`` / ``AI-E9-7``): ``SEAL_COMMIT_SHA``
from ``tests.test_gate_seal`` and ``CANDIDATE_OUTPUT_PATHS`` from ``tests.test_candidate_selection``.
A constant retyped is a constant that drifts, and 16.2's hand-off says so in terms.
"""

from __future__ import annotations

import ast
import dataclasses
import subprocess
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]

#: The commit in which Story 16.1 landed §5's FIFTH condition — the denominator-breadth arm
#: (``argus/precision/gate_breadth.py`` new; ``SECTION_5_CONDITIONS`` 4 -> 5). Recorded as a full
#: 40-character lowercase sha: a short sha is ambiguous and this is a load-bearing citation.
BREADTH_COMMIT_SHA = "2ac107875682def5bbe838e8ac0af2602c8cc444"

#: The commit in which Story 16.3 landed §5's SEVENTH condition — the detector-yield arm
#: (``argus/precision/gate_yield.py``; ``SECTION_5_CONDITIONS`` 6 -> 7).
YIELD_COMMIT_SHA = "48e8ea6b13cd77a0eb20603e5d9072460a751a18"

#: A path KNOWN to carry commits. Without it a misspelled pathspec returns empty and reads
#: exactly like a clean ordering — the single most likely way the absences below could pass
#: vacuously. The ``-75``/``-94`` template, reused rather than re-invented.
_CONTROL_PATH_WITH_COMMITS = "tests/corpus/_manifest.py"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    """A pure READ of this repository's history. Never mutates: no checkout, no commit, no fetch."""
    return subprocess.run(
        ["git", "-C", str(_REPO_ROOT), *args],
        capture_output=True,
        text=True,
        # ⛔ EXPLICIT, and found by execution rather than by review. `text=True` alone decodes
        # with the LOCALE codec — cp1252 on this Windows machine — and `git show` of a source
        # blob carries UTF-8 punctuation, so `-103` died on a UnicodeDecodeError here while it
        # would have passed on the ubuntu CI leg. The reverse of this repository's usual
        # Windows/POSIX asymmetry, and the same lesson: name the encoding, never inherit it.
        encoding="utf-8",
        timeout=120,
    )


def _seal_commit_sha() -> str:
    """Story 16.2's ``SEAL_COMMIT_SHA``, IMPORTED rather than re-typed (``DN-16-4-2``).

    Function-local because ``tests/test_gate_seal.py`` and ``tests/test_candidate_selection.py``
    both manipulate ``sys.path`` at import time, and this module must not depend on the order
    pytest happens to collect them in — the same reason ``-94`` imports its paths locally.
    """
    from tests.test_gate_seal import SEAL_COMMIT_SHA

    return str(SEAL_COMMIT_SHA)


def _candidate_output_paths() -> tuple[str, ...]:
    """Story 15.1's declared candidate-output paths, IMPORTED rather than re-listed."""
    from tests.test_candidate_selection import CANDIDATE_OUTPUT_PATHS

    return tuple(CANDIDATE_OUTPUT_PATHS)


def _condition_landing_shas() -> tuple[tuple[str, str, str], ...]:
    """``(story, condition_id, sha)`` for §5's three NEW conditions, in landing order."""
    return (
        ("16.1", "denominator-breadth-contributing-members", BREADTH_COMMIT_SHA),
        ("16.2", "gate-evidence-drawn-from-the-sealed-partition", _seal_commit_sha()),
        ("16.3", "detector-yield-verdict-eligible-population-floor", YIELD_COMMIT_SHA),
    )


def _assert_sha_resolves(story: str, sha: str) -> None:
    """Precondition: the citation is a real, full, lowercase sha in THIS object database."""
    assert len(sha) == 40 and sha.islower(), (
        f"story {story}'s condition-landing sha {sha!r} is not a full 40-character lowercase "
        f"hex sha. A short sha is ambiguous and this is the citation the ordering rests on."
    )
    assert set(sha) <= set("0123456789abcdef"), sha
    kind = _git("cat-file", "-t", sha)
    assert kind.returncode == 0 and kind.stdout.strip() == "commit", (
        f"story {story}'s condition-landing sha {sha} does not resolve to a commit in this "
        f"repository (git said {kind.stdout.strip()!r} / {kind.stderr.strip()!r}). Story 16.4's "
        f"ordering claim is a claim about git history and cannot be established against a sha "
        f"that is not in it."
    )


def test_TC_ArgusAgent_PRECISION_001_101_the_conditions_precede_every_candidate_output() -> None:
    """TC-ArgusAgent-PRECISION-001-101 — AC2.1/AC2.2/AC2.3: §5's three new arms landed FIRST.

    **Observable (guard-adequacy (i)):** for each of §5's three new conditions, the pair *(is the
    landing commit an ancestor of HEAD, does any commit reachable from it touch a declared
    candidate-output path)*. Story 16.4's evidentiary position is that the answer is
    ``(True, no)`` for all three — the conditions that make this round's number mean something
    were in place before any output over a bench member could exist.

    **The defect that moves it (guard-adequacy (ii)):** a cited sha that is not actually an
    ancestor, or a story that landed its condition *after* touching candidate output, each flips
    a conjunct here — at the real seam, the object database, never against a reconstruction of
    it. ``AC2.4``'s mutation run drives exactly those two and observes RED.

    **Three non-vacuity preconditions, each asserted BEFORE the absence it protects** (AC2.3,
    the ``-75``/``-94`` template):

    1. the declared candidate-output path set is **non-empty** — an empty pathspec makes
       ``git log`` report everything or nothing depending on invocation, and either way the
       assertion below would mean nothing;
    2. ``git log`` over a **control path known to carry commits** returns **non-empty**, per
       cited sha — a misspelled or moved pathspec returns empty and is **indistinguishable from
       a clean ordering**. This is the precondition that makes the absence real;
    3. every cited sha **resolves** to a commit, and the ancestry predicate is driven to **BOTH**
       outcomes — ``True`` for landing->HEAD and ``False`` for HEAD->landing — so it is watched
       failing, not only passing.
    """
    shas = _condition_landing_shas()
    candidate_output_paths = _candidate_output_paths()

    # ── Non-vacuity: this guard is about a real, non-empty, non-degenerate set of citations. ──
    assert len(shas) == 3, f"expected §5's three NEW conditions, got {len(shas)}"
    assert len({sha for _story, _condition, sha in shas}) == 3, (
        f"two of §5's three new conditions cite the SAME landing commit: {shas}. Either a "
        f"constant drifted onto its neighbour or two conditions landed together — in both cases "
        f"the per-story ordering claim below is weaker than it reads."
    )

    # ── Precondition 1: the declared output-path set is non-empty. ──
    assert candidate_output_paths, (
        "CANDIDATE_OUTPUT_PATHS is empty, so the absence asserted below is an absence over "
        "nothing. Declare where candidate output would land, or this guard forbids nothing."
    )

    for story, condition, sha in shas:
        # ── Precondition 3a: the sha RESOLVES. ──
        _assert_sha_resolves(story, sha)

        # ── Precondition 2: prove THIS invocation is capable of finding something. ──
        control = _git("log", "--format=%H", sha, "--", _CONTROL_PATH_WITH_COMMITS)
        assert control.returncode == 0, f"control `git log` failed: {control.stderr.strip()!r}"
        assert [line for line in control.stdout.splitlines() if line.strip()], (
            f"`git log {sha} -- {_CONTROL_PATH_WITH_COMMITS}` returned NOTHING. That path is "
            f"known to carry commits, so this invocation is not capable of finding anything — "
            f"and an invocation that finds nothing reports a clean ordering for a dirty one. "
            f"Fix the invocation, never the assertion."
        )

        # ── THE ABSENCE (AC2.2): nothing reachable from the landing sha touches candidate output. ──
        touching = _git("log", "--format=%H", sha, "--", *candidate_output_paths)
        assert touching.returncode == 0, f"`git log` failed: {touching.stderr.strip()!r}"
        offenders = [line for line in touching.stdout.splitlines() if line.strip()]
        assert not offenders, (
            f"{len(offenders)} commit(s) reachable from story {story}'s condition-landing sha "
            f"{sha} touch a declared candidate-output path {list(candidate_output_paths)}: "
            f"{offenders[:5]}. Condition {condition!r} would then have been written with Argus's "
            f"output over the bench already in hand, which is the ordering Story 16.4's round "
            f"exists to rule out."
        )

        # ── Precondition 3b: the ancestry predicate, driven to BOTH outcomes on real shas. ──
        forward = _git("merge-base", "--is-ancestor", sha, "HEAD")
        assert forward.returncode == 0, (
            f"story {story}'s condition-landing commit {sha} is NOT an ancestor of HEAD. It is "
            f"on a detached or abandoned line of history, so condition {condition!r} establishes "
            f"no ordering on the branch that ships this round's result."
        )
        backward = _git("merge-base", "--is-ancestor", "HEAD", sha)
        assert backward.returncode != 0, (
            f"HEAD reports as an ancestor of {sha}, which cannot be true while {sha} is also an "
            f"ancestor of HEAD unless they are the same commit. The ancestry predicate is "
            f"returning the same answer to both questions and discriminates NOTHING — every "
            f"ordering assertion in this module would pass over it."
        )


def test_TC_ArgusAgent_PRECISION_001_102_the_landing_order_is_derived_from_history() -> None:
    """TC-ArgusAgent-PRECISION-001-102 — AC2.3/AC2.4: the ordering, and an ADVERSARIAL population.

    **Observable (guard-adequacy (i)):** the pairwise ancestry relation over §5's three landing
    commits — 16.1 before 16.2 before 16.3 — and the discrimination of the ancestry predicate
    itself over a population this module does not choose.

    **The defect that moves it (guard-adequacy (ii)):** a landing sha edited to a commit from the
    wrong story, or an ancestry predicate that has stopped discriminating (the failure mode that
    would make every assertion in ``-101`` pass silently), flips a conjunct here.

    **The adversarial variant, GENERATED rather than hand-listed (guard-adequacy (iii)):** the
    population is every commit STRICTLY between ``SEAL`` and ``HEAD``, read out of this
    repository's history at run time, with its count asserted non-zero. Each generated commit is
    required to be an ancestor of HEAD and to have HEAD *not* be an ancestor of it — a generated
    both-directions drive of the exact predicate ``-101`` depends on, over a population that
    grows with the branch, so it cannot silently decay into a drive over nothing. ⛔ The count is
    asserted rather than assumed: a generated population of size zero is the vacuity this clause
    exists to close. ⛔ *Strictly* is load-bearing and was found BY EXECUTION, not by reading:
    ``--is-ancestor`` is reflexive and ``rev-list A..HEAD`` includes HEAD, so the first cut of
    this drive went RED on HEAD itself. The reflexive case is now asserted on its own line
    instead of being papered over.
    """
    shas = _condition_landing_shas()
    seal = _seal_commit_sha()

    for story, _condition, sha in shas:
        _assert_sha_resolves(story, sha)

    # ── THE ORDER, pairwise, derived from the object database rather than asserted in prose. ──
    ordered = [sha for _story, _condition, sha in shas]
    for earlier, later in zip(ordered, ordered[1:]):
        forward = _git("merge-base", "--is-ancestor", earlier, later)
        assert forward.returncode == 0, (
            f"{earlier} is NOT an ancestor of {later}, so §5's conditions did not land in the "
            f"order 16.1 -> 16.2 -> 16.3 that every artifact in this epic reports."
        )
        backward = _git("merge-base", "--is-ancestor", later, earlier)
        assert backward.returncode != 0, (
            f"{later} also reports as an ancestor of {earlier}. The ancestry predicate is not "
            f"discriminating, and the order above is therefore unverified."
        )

    # ── The GENERATED adversarial population: every commit from the seal to HEAD. ──
    #
    # ⛔ ``merge-base --is-ancestor`` is REFLEXIVE — a commit is its own ancestor — and
    # ``rev-list A..HEAD`` INCLUDES HEAD. A first cut of this guard drove the backward
    # direction over the whole range and went RED on HEAD itself, correctly. The answer is to
    # state the reflexive case explicitly and drive the asymmetry over the STRICT ancestors,
    # rather than to soften the assertion into one that would also accept a predicate that had
    # stopped discriminating.
    head = _git("rev-parse", "HEAD")
    assert head.returncode == 0, f"`git rev-parse HEAD` failed: {head.stderr.strip()!r}"
    head_sha = head.stdout.strip()
    assert len(head_sha) == 40, head_sha
    assert _git("merge-base", "--is-ancestor", head_sha, head_sha).returncode == 0, (
        "`merge-base --is-ancestor` is not reflexive in this git, so the strict/non-strict "
        "distinction this guard draws below does not hold and its reasoning is unsound."
    )

    listed = _git("rev-list", f"{seal}..HEAD")
    assert listed.returncode == 0, f"`git rev-list` failed: {listed.stderr.strip()!r}"
    population = [line.strip() for line in listed.stdout.splitlines() if line.strip()]
    strict = [commit for commit in population if commit != head_sha]
    assert strict, (
        f"`git rev-list {seal}..HEAD` generated no commit STRICTLY between the seal and HEAD "
        f"(population={len(population)}), so the both-directions drive below would run over "
        f"nothing and guard-adequacy (iii) would be discharged vacuously. The seal commit is an "
        f"ancestor of HEAD with commits between them; an empty answer means the invocation is "
        f"broken, not that the branch is."
    )
    for commit in strict:
        assert _git("merge-base", "--is-ancestor", commit, "HEAD").returncode == 0, (
            f"generated commit {commit} from {seal}..HEAD is not an ancestor of HEAD, which is a "
            f"contradiction in terms — the predicate is returning noise."
        )
        assert _git("merge-base", "--is-ancestor", "HEAD", commit).returncode != 0, (
            f"HEAD reports as an ancestor of the STRICTLY earlier generated commit {commit}. The "
            f"predicate answers the same way in both directions and discriminates nothing."
        )


# ─────────────────────────────────────────────────────────────────────────────
# HALT-3 — bench membership is HISTORICAL, and does not dissolve at ratification
# ─────────────────────────────────────────────────────────────────────────────

#: The ORIGINAL live predicate ``bench_candidates()`` folded on before Story 16.4. It is
#: correct AS OF ``BENCH_COMMIT_SHA`` — nothing had been ratified then, so the two fields it
#: reads still carried the bench. It is retained HERE, in the re-derivation, rather than in the
#: manifest, because that historical blob is the only place it is still true.
_CANDIDATE_MARKER = "candidate"


def _bench_ids_at(commit_sha: str) -> frozenset[str]:
    """Re-derive the bench from ``_manifest.py`` AS READ OUT OF GIT at *commit_sha*.

    Parsed with :mod:`ast` rather than by regex: the manifest is Python, and a substring search
    over it would match a member id inside a prose ``adjudication_caveat`` as readily as a real
    row. The ORIGINAL predicate is applied, which is what makes this an independent derivation
    rather than a restatement of the constant it checks.
    """
    blob = _git("show", f"{commit_sha}:tests/corpus/_manifest.py")
    assert blob.returncode == 0, f"`git show` failed: {blob.stderr.strip()!r}"
    tree = ast.parse(blob.stdout)
    found: set[str] = set()
    rows = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, "attr", "")
        if name != "CorpusMemberSpec":
            continue
        rows += 1
        fields = {
            kw.arg: kw.value
            for kw in node.keywords
            if kw.arg and isinstance(kw.value, ast.Constant)
        }
        member_id = fields.get("member_id")
        eligible = fields.get("eligible_for_n")
        reason = fields.get("ineligible_reason")
        if member_id is None or eligible is None:
            continue
        reason_text = reason.value if reason is not None and isinstance(reason.value, str) else ""
        if eligible.value is False and _CANDIDATE_MARKER in reason_text.lower():
            found.add(str(member_id.value))
    assert rows, (
        f"the AST walk over _manifest.py at {commit_sha} found ZERO CorpusMemberSpec rows, so "
        f"the set below is empty for a reason that has nothing to do with the bench. A parser "
        f"that finds nothing reports an empty bench for a full one."
    )
    return frozenset(found)


def test_TC_ArgusAgent_PRECISION_001_103_the_bench_is_what_was_frozen_at_the_bench_commit() -> None:
    """TC-ArgusAgent-PRECISION-001-103 — HALT-3: ``BENCH_MEMBER_IDS`` re-derived from history.

    **Observable (guard-adequacy (i)):** ``_manifest.BENCH_MEMBER_IDS`` versus the bench read
    out of ``tests/corpus/_manifest.py`` **at** ``BENCH_COMMIT_SHA``, under the ORIGINAL
    ``not eligible_for_n and "candidate" in ineligible_reason`` predicate — in **both**
    directions. Plus the ordering that makes the bench mean anything:
    **criteria → bench → seal**, each an ancestor of the next, read from the object database.

    **The defect that moves it (guard-adequacy (ii)):** a member added to or removed from
    ``BENCH_MEMBER_IDS`` today reddens this, because the frozen set no longer matches what was
    frozen. So does re-pointing ``BENCH_COMMIT_SHA`` at a commit where the bench was different.
    That is the whole value of the constant: it is checkable against something nobody can edit
    without rewriting history.

    **The adversarial variant, GENERATED (guard-adequacy (iii)):** the comparison set is
    *parsed out of a historical blob* rather than listed here, so it is regenerated from git on
    every run and its row count is asserted non-zero. A parser that silently matched nothing
    would report an empty bench for a full one, which is the vacuity this closes.

    ⛔ **Non-vacuity is `DF-13-5-A`'s own number.** The bench is asserted to sit inside the
    pre-registered **12–20** band — the same band ``-76``/``-78`` enforce — so this guard cannot
    pass over a bench that has quietly emptied.
    """
    from tests.corpus._manifest import BENCH_COMMIT_SHA, BENCH_MEMBER_IDS
    from tests.test_candidate_selection import CRITERIA_COMMIT_SHA

    _assert_sha_resolves("15.1 (bench)", BENCH_COMMIT_SHA)
    _assert_sha_resolves("15.1 (criteria)", CRITERIA_COMMIT_SHA)

    # ── Non-vacuity FIRST: a bench outside DF-13-5-A's pre-registered band is not a bench. ──
    assert 12 <= len(BENCH_MEMBER_IDS) <= 20, (
        f"BENCH_MEMBER_IDS holds {len(BENCH_MEMBER_IDS)} members, outside `DF-13-5-A`'s "
        f"pre-registered 12-20 band. Every equality below would still 'hold' over a bench that "
        f"had quietly emptied."
    )

    # ── THE RE-DERIVATION, in both directions. ──
    frozen = _bench_ids_at(BENCH_COMMIT_SHA)
    assert frozen == BENCH_MEMBER_IDS, (
        f"BENCH_MEMBER_IDS does not match the bench frozen at {BENCH_COMMIT_SHA}. "
        f"constant-only={sorted(BENCH_MEMBER_IDS - frozen)} "
        f"history-only={sorted(frozen - BENCH_MEMBER_IDS)}. The bench is a HISTORICAL set: it "
        f"is what was admitted at that commit, and it is not editable after the fact."
    )

    # ── THE ORDERING: criteria -> bench -> seal, and NOT the other way. ──
    for earlier, later, why in (
        (CRITERIA_COMMIT_SHA, BENCH_COMMIT_SHA, "the criteria were frozen BEFORE the selection"),
        (BENCH_COMMIT_SHA, _seal_commit_sha(), "the bench was frozen BEFORE the seal"),
    ):
        assert _git("merge-base", "--is-ancestor", earlier, later).returncode == 0, (
            f"{earlier} is not an ancestor of {later}, so it is NOT true that {why}."
        )
        assert _git("merge-base", "--is-ancestor", later, earlier).returncode != 0, (
            f"{later} also reports as an ancestor of {earlier}; the predicate discriminates "
            f"nothing and the ordering above is unverified."
        )

    # ── The bench commit is NOT the criteria commit, and the distinction is load-bearing. ──
    assert BENCH_COMMIT_SHA != CRITERIA_COMMIT_SHA, (
        "the bench and the criteria are recorded as the same commit. The criteria were frozen "
        "three commits before the bench landed, and collapsing them would let a bench chosen "
        "AFTER the criteria were seen claim it had been chosen before."
    )


def test_TC_ArgusAgent_PRECISION_001_104_ratification_does_not_remove_a_member_from_the_bench() -> None:
    """TC-ArgusAgent-PRECISION-001-104 — HALT-3: the invariance that had to be measured to be found.

    **Observable (guard-adequacy (i)):** ``bench_candidates()`` evaluated over a manifest in
    which bench members carry the POST-RATIFICATION field values — ``eligible_for_n=True`` and
    ``ineligible_reason=None``, the exact two edits protocol §6 R2 makes. The bench must be
    **unchanged**.

    **The defect that moves it (guard-adequacy (ii)):** this is not hypothetical and it is not a
    style preference. Against the pre-16.4 implementation — which folded on those two very
    fields — ratifying three members dropped the bench 14 → 11 and reddened four shipped guards
    (``-76``, ``-78``, ``-79``, ``-89``), one of them by breaching ``DF-13-5-A``'s own
    pre-registered band. This guard is that measurement, made permanent and cheap.

    **The adversarial variant, GENERATED (guard-adequacy (iii)):** the ratified manifest is
    constructed at run time from the live rows via :func:`dataclasses.replace`, so it covers
    whatever the bench happens to hold rather than a fixture that would drift away from it, and
    the drive is asserted to have TAKEN before its effect is read.

    ⛔ It also holds the line the old predicate held: a row marked as an unratified candidate
    that is NOT in ``BENCH_MEMBER_IDS`` fails here, so a new candidate still cannot be added
    without being registered.
    """
    from tests.corpus import _manifest
    from tests.corpus._manifest import BENCH_MEMBER_IDS, bench_candidates

    before = bench_candidates()
    assert before, "non-vacuity: the manifest holds ZERO bench candidates"
    assert {spec.member_id for spec in before} == set(BENCH_MEMBER_IDS)

    # ── An unratified candidate row that nobody registered is still caught. ──
    unregistered = sorted(
        spec.member_id
        for spec in _manifest.VALIDATION_CORPUS
        if not spec.eligible_for_n
        and _CANDIDATE_MARKER in (spec.ineligible_reason or "").lower()
        and spec.member_id not in BENCH_MEMBER_IDS
    )
    assert not unregistered, (
        f"{unregistered} carry the candidate marker but are absent from BENCH_MEMBER_IDS. The "
        f"bench is a frozen historical set; a row cannot join it by describing itself as a "
        f"candidate, and a genuinely new bench needs a new dated set with its own commit."
    )

    # ── THE INVARIANCE: apply R2's two edits to every bench row and re-fold. ──
    ratified = tuple(
        dataclasses.replace(spec, eligible_for_n=True, ineligible_reason=None)
        if spec.member_id in BENCH_MEMBER_IDS
        else spec
        for spec in _manifest.VALIDATION_CORPUS
    )
    inert = [
        spec.member_id
        for spec in ratified
        if spec.member_id in BENCH_MEMBER_IDS and not spec.eligible_for_n
    ]
    assert not inert, f"the synthetic ratification did not take on {inert} — the drive is inert"

    original = _manifest.VALIDATION_CORPUS
    try:
        _manifest.VALIDATION_CORPUS = ratified
        after = bench_candidates()
    finally:
        _manifest.VALIDATION_CORPUS = original

    assert _manifest.VALIDATION_CORPUS is original, "the manifest was not restored"
    assert {spec.member_id for spec in after} == {spec.member_id for spec in before}, (
        f"ratifying the bench CHANGED it: {len(before)} -> {len(after)}. Membership in a set "
        f"frozen in the past cannot depend on a field edited in the future. This is the HALT-3 "
        f"defect: it breaches `DF-13-5-A`'s pre-registered 12-20 band and breaks "
        f"SEALED_PARTITION_TABLE's both-directions equality with the bench."
    )
    assert len(after) == len(before) == len(BENCH_MEMBER_IDS)
