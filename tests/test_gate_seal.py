"""Story 16.2 — the SEAL: a partition of the bench frozen before anything is run.

Verification area ``TC-ArgusAgent-PRECISION-001-87``..``-93``. A NEW module, opened here
for the reason AC8.5 states in its own words — *"new guards go in a NEW module; do not
shave a file to fit"*. ``tests/test_gate_decision.py`` stood at 1,193 of NFR-M1's 1,200
lines when this story began and ``tests/test_gate_breadth.py`` owns the BREADTH arm; the
seal is its own subject and gets its own file.

**What this module guards, and the vacuity each guard was built against.** Three of this
story's guards are structurally at risk of passing over nothing, and each has a named
answer rather than a hope:

* ``-89``'s FROZEN PARTITION TABLE — *a guard that only read the table would be a guard
  over a hand-list.* Answer: every row is RE-DERIVED from the shipped rule and asserted in
  BOTH directions (no table row the rule contradicts, no rule output the table omits), with
  both partition classes required non-empty.
* ``-90``'s §5 SEAL CONDITION — over the committed record it can only ever read ``FAILED``,
  and the fold is *already* unevaluable for reasons that have nothing to do with the seal, so
  a guard built only against the committed artifact would be green, silent and useless.
  Answer: GENERATED populations at the real ``decide_gate`` seam, with **breadth pinned
  TRUE** so the seal is the ONLY term that can move the answer, driven to both verdicts and
  asserted at the exact count where it flips.
* ``-93``'s post-seal detector-commit rule — its population is EMPTY on the day it lands, so
  a guard that only iterated it would pass forever over nothing. Answer: the PREDICATE is
  driven to both outcomes over synthetic messages, independently of the population, behind
  three non-vacuity preconditions copied from ``TC-ArgusAgent-PRECISION-001-75``.

⛔ **THE MIRROR RULE, which cost Story 16.1 a whole review round.** Where an expectation has
to be recomputed, its inputs are derived FROM THE FIXTURE and passed IN — never read back
out of the predicate under test. A mirror fed the predicate's own answer moves in lockstep
with the defect and survives exactly the mutation that should kill it.

**This module also owns the SEALED-POPULATION GENERATORS** (:func:`sealed_corpus_members`,
:func:`spread_over_sealed`, :func:`mixed_population`) because every fixture in the tree that
needs a sealed population needs the same ones, and ``tests/test_gate_decision.py`` and
``tests/test_gate_breadth.py`` IMPORT them rather than each growing a copy — the same AR7
reuse-never-fork discipline that already has ``test_gate_decision.py`` importing
``expected_section_5_outcome`` and ``protocol_cleared_call_sites`` instead of copying them.

⛔ **NOTHING HERE RUNS ARGUS OVER ANY CORPUS MEMBER.** Every population below is synthesised
from the committed adjudication record's own shape; no repository is fetched, staged,
checked out or read; no detector is imported. The manifest is read for member ids and pins
only (NFR-S1: counts, locators and metadata, never a source byte).
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent / "corpus"))

from _manifest import (  # noqa: E402
    MANIFEST_FIELDS,
    PRE_SEAL_MEMBER_IDS,
    SEALED_PARTITION_TABLE,
    VALIDATION_CORPUS,
    CorpusMemberSpec,
    bench_candidates,
    eligible_member_count,
    validation_floor_n,
)

from argus.precision.adjudication import (  # noqa: E402
    AdjudicationRecord,
    AdjudicationRow,
    Exhaustive,
    load_record,
    validation_set_population_n,
)
from argus.precision.gate_breadth import contributing_member_floor  # noqa: E402
from argus.precision.gate_decision import (  # noqa: E402
    SEAL_CONDITION_ID,
    SECTION_5_CONDITIONS,
    CleanRepoEvidence,
    GateDecision,
    decide_gate,
    section_5_condition,
)
from argus.precision.gate_disclosure import (  # noqa: E402
    derive_concentration,
    ratified_corpus_members,
)
from argus.precision.gate_seal import (  # noqa: E402
    PARTITION_OPEN,
    PARTITION_PRE_SEAL,
    PARTITION_SEALED,
    PARTITION_VALUES,
    SEAL_CITATION_RULE,
    SEAL_CITATION_TRAILER,
    SEAL_CITATION_VALUES,
    SEAL_RULE_DERIVATION,
    MissingMemberPartition,
    UnregisteredPartition,
    UnsealablePin,
    VacuousSealError,
    assess_seal,
    cites_partition,
    member_partitions,
    partition_meaning,
    partition_of,
    sealed_member_floor,
)
from argus.precision.replay_harness import (  # noqa: E402
    PRECISION_GATE_THRESHOLD,
    registry_module,
)

_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_CORPUS_DIR = _ARTIFACTS / "validation-corpus"
_RECORD_PATH = _CORPUS_DIR / "adjudication-record.json"
_SEAL_MODULE = _REPO_ROOT / "argus" / "precision" / "gate_seal.py"

#: The committed adjudication SETS. ``-88`` derives the ``pre-seal`` population from their
#: ``members[]`` arrays rather than from the manifest, so the two have to agree.
_ADJUDICATION_SETS = (
    _CORPUS_DIR / "adjudication-set.json",
    _CORPUS_DIR / "adjudication-set-13-5.json",
)

#: The named human protocol §2 designates. Synthetic fixtures attribute their SYNTHETIC
#: judgements to this string so the instrument's attribution rule is genuinely exercised;
#: not one of them is ever written to the committed record.
_ADJUDICATOR = "XAgent007 (Engineering Lead)"


def _record() -> AdjudicationRecord:
    assert _RECORD_PATH.is_file(), (
        f"the committed adjudication record is absent at "
        f"{_RECORD_PATH.relative_to(_REPO_ROOT).as_posix()}"
    )
    return load_record(_RECORD_PATH)


def _corpus_row(spec: CorpusMemberSpec) -> dict[str, str]:
    """One manifest row in the mapping shape :func:`decide_gate` consumes.

    ⛔ **The shape is ASSERTED against the shipped producer, never assumed** — see
    :func:`sealed_corpus_members`. A fixture that quietly grew a different key set would
    drive the seam with a mapping the producer never emits, and every assertion over it
    would be about a shape that does not ship.
    """
    return {
        "member_id": str(spec.member_id),
        "commit_sha": str(spec.commit_sha),
        "primary_language": str(spec.primary_language),
        "provenance": str(spec.provenance),
        "partition": str(spec.partition),
    }


def sealed_corpus_members() -> tuple[dict[str, str], ...]:
    """The SEALED bench members, read LIVE from the manifest — real rows, real pins.

    This is Story 16.2 §2.4's recipe, and it is the only honest way to build a fixture that
    can satisfy §5's seal condition: ``decide_gate`` takes ``ratified_members`` as an
    ARGUMENT, so a fixture may be driven over the sealed bench candidates **as they actually
    exist in the manifest** rather than over fabricated rows. Nothing here ratifies
    anything: passing a row into a test fixture is not the protocol §6 R2 operator act, and
    every one of these rows still carries ``eligible_for_n=False`` in the manifest — ``-92``
    asserts exactly that.

    **Non-vacuity floor**, asserted here rather than left to each caller: there must be at
    least ``contributing_member_floor(VALIDATION_SET_FLOOR_N)`` sealed rows, or every
    generated population below would be structurally incapable of satisfying the condition
    and each assertion over it would silently become about something else.

    **The mapping shape is asserted against the shipped producer**, so this fixture cannot
    fork from ``gate_disclosure.ratified_corpus_members`` without going red.
    """
    rows = tuple(_corpus_row(spec) for spec in VALIDATION_CORPUS if spec.partition == PARTITION_SEALED)
    floor = contributing_member_floor(int(registry_module().VALIDATION_SET_FLOOR_N))
    assert len(rows) >= floor, (
        f"non-vacuity: the manifest holds {len(rows)} sealed member(s) against a floor of "
        f"{floor}, so no generated population could satisfy §5's seal condition and every "
        f"guard below would be asserting over a fixture that cannot pass"
    )
    shipped = ratified_corpus_members()
    assert shipped and set(rows[0]) == set(shipped[0]), (
        f"the fixture's corpus-member shape forked from the shipped producer's: fixture "
        f"{sorted(rows[0])!r} vs gate_disclosure.ratified_corpus_members {sorted(shipped[0])!r}"
    )
    return rows


def pre_seal_corpus_members() -> tuple[dict[str, str], ...]:
    """The PRE-SEAL members — the five already-audited rows, in the same mapping shape."""
    rows = tuple(
        _corpus_row(spec) for spec in VALIDATION_CORPUS if spec.partition == PARTITION_PRE_SEAL
    )
    assert rows, "non-vacuity: the manifest reports ZERO pre-seal members"
    return rows


def spread_over_sealed(record: AdjudicationRecord) -> AdjudicationRecord:
    """The SAME findings, RE-HOMED across the SEALED members — a §5 outcome, GENERATED.

    ⛔ **RE-AUTHORED 2026-08-20 (Story 16.2 / AC6.3) as an INTENDED BEHAVIOUR CHANGE, and
    MOVED here from ``tests/test_gate_decision.py``.** Story 16.1 introduced it spreading
    over ``ratified_corpus_members()`` — the five members that satisfy §5's N floor — because
    §5 had just gained a breadth condition the committed 2-member population could not meet.
    All five of those members became ``pre-seal`` the moment this story's seal landed, so a
    population spread over them is now 100% pre-seal and can never reach a §5 OUTCOME at all.
    Every guard whose subject is the DISPATCH would have started measuring the seal floor
    instead of the thing it names. Spreading over the SEALED members restores the subject.

    It moved modules for a second, blunter reason: ``tests/test_gate_decision.py`` had SEVEN
    lines of NFR-M1 headroom, and *"do not shave a file to fit"* cuts both ways — the
    generator's natural home is the module that owns the partition it generates over.

    The population is GENERATED from the committed record by rotating each row's
    ``member_id`` across the sealed members — never hand-written — so it keeps the real
    record's rules, locators and count. ``row_id`` is re-derived through the shipped
    ``finding_row_id``, because the id is content-addressed over the member.
    """
    from argus.precision.adjudication import finding_row_id

    members = [str(member["member_id"]) for member in sealed_corpus_members()]
    floor = contributing_member_floor(int(registry_module().VALIDATION_SET_FLOOR_N))
    rows = tuple(
        replace(
            row,
            member_id=members[index % len(members)],
            row_id=finding_row_id(
                member_id=members[index % len(members)],
                rule_id=row.rule_id,
                verdict_eligible=row.verdict_eligible,
                advisory=row.advisory,
                locator=row.locator,
            ),
        )
        for index, row in enumerate(record.rows)
    )
    spread = replace(record, rows=rows)
    assert len({row.member_id for row in spread.live_rows()}) >= floor, (
        "non-vacuity: the generated population did not actually broaden across the sealed "
        "partition, so every guard below would be asserting over the same narrow "
        "denominator it meant to replace"
    )
    return spread


def _judged_rows(members: list[str], *, size: int) -> tuple[AdjudicationRow, ...]:
    """*size* live TP judgements by the named human, rotated across *members*.

    Every row is reproducible, exhaustive and above threshold, so the ONLY thing that can
    move a §5 outcome over the result is which members it came from. The locators are
    per-index and therefore distinct, so the content-addressed ids cannot collide.
    """
    return tuple(
        AdjudicationRow(
            row_id=f"synthetic{index:04d}.0",
            member_id=members[index % len(members)],
            rule_id="vacuous_test_ast",
            verdict_eligible=True,
            advisory=False,
            locator=f"pkg/tests/test_synthetic_{index}.py:{index + 1}",
            disposition="TP",
            adjudicator=_ADJUDICATOR,
            adjudicated_on="2026-08-17",
            reason="synthetic fixture: exercises the instrument, adjudicates nothing real",
        )
        for index in range(size)
    )


def mixed_population(
    *, sealed_members: int, pre_seal_members: int, size: int
) -> tuple[AdjudicationRecord, tuple[dict[str, str], ...]]:
    """A population spread over EXACTLY *sealed_members* sealed and *pre_seal_members* pre-seal.

    ⛔ **This is the fixture that makes the seal clause DECISIVE rather than decorative, and
    the reason it exists is worth stating.** A population built only from sealed members has
    ``sealed contributing == contributing``, so its seal term and its breadth term move in
    LOCKSTEP — and a mutation that deleted the seal clause entirely would leave every
    assertion green, because the breadth clause already answered ``BLOCKED``. That is exactly
    the unreal-guard shape the 2026-08-20 review found in Story 16.1's round 2. Mixing in
    ``pre_seal_members`` pins **breadth TRUE** while the sealed count moves, so the seal is
    the only term that can change the answer.

    Returns the record AND the corpus rows to pass as ``ratified_members``, because the two
    must describe the same population or the concentration and the partitions disagree.
    """
    sealed = list(sealed_corpus_members())
    pre_seal = list(pre_seal_corpus_members())
    assert 0 <= sealed_members <= len(sealed), (sealed_members, len(sealed))
    assert 0 <= pre_seal_members <= len(pre_seal), (pre_seal_members, len(pre_seal))
    corpus = tuple(sealed[:sealed_members] + pre_seal[:pre_seal_members])
    contributing = [str(row["member_id"]) for row in corpus]
    assert contributing, "non-vacuity: a population over ZERO members is not a population"
    assert size >= len(contributing)
    record = replace(_record(), rows=_judged_rows(contributing, size=size))
    live = {row.member_id for row in record.live_rows()}
    assert live == set(contributing), (
        "non-vacuity: the generated population does not carry the members it claims, so "
        "every assertion over it would be about the wrong fixture"
    )
    return record, corpus


def decide_over(
    record: AdjudicationRecord, *, corpus: tuple[dict[str, str], ...]
) -> GateDecision:
    """Drive the SHIPPED :func:`decide_gate` at the real seam over *corpus*.

    Only the clean-repo evidence and the provenance strings are synthetic, because measuring
    the cartridge branch requires staging repositories (protocol §3.3, the impure shell) and
    a sha/date are provenance the producer carries rather than measurements.
    """
    return decide_gate(
        record,
        expected_finding_ids=[row.finding_id for row in record.rows],
        population_n=validation_set_population_n(),
        floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
        protocol_change_log_head=record.protocol_version,
        clean_repo_evidence=CleanRepoEvidence(
            corpus="synthetic fixture standing in for the FR20 cartridge corpus",
            applicable=True,
            clean_repo_fp=0,
            clean_member_ids=("clean_control",),
            note="synthetic fixture",
        ),
        ratified_members=corpus,
        record_is_tracked_in_git=True,
        commit_sha="0" * 40,
        decided_on="2026-08-17",
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC1.1 / AC1.2 — the rule is ONE pure function with a vocabulary that RAISES
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_87_the_partition_rule_is_one_pure_closed_function() -> None:
    """TC-ArgusAgent-PRECISION-001-87 — AC1.1/AC1.2: the rule, its closure, and its purity.

    **Observable, four of them, each failing independently.**

    *(i) The vocabulary is CLOSED and RAISES.* Three registered values, each with a
    substantive meaning, and an unregistered one raises rather than being tolerated
    (``DF-10-4-E``) — the ``PROVENANCE_VALUES`` / ``GATE_OUTCOMES`` / ``CONDITION_VERDICTS``
    shape this codebase already uses. ``pre-seal`` is required to be a MEMBER and its meaning
    is required to say it is an EXCLUSION rather than an assignment (DN-16-2-4): collapsing
    it into ``open`` is arithmetically identical and tells a reader something false.

    *(ii) The rule is DRIVEN TO ALL THREE OUTCOMES, over GENERATED shas rather than a
    hand-picked pair.* Every one of the sixteen hex digits is used to build a real 40-hex
    sha, so the odd/even bisection is observed both ways across the whole alphabet — and each
    of those shas is ALSO driven through the override, where it must return ``pre-seal``
    whatever its parity says. The two directions of the override are what make it a rule
    rather than a comment.

    *(iii) It REFUSES a non-pin.* A sha-ordered rule over an unvalidated sha is not
    mechanically reproducible: ``int()`` of a shortened sha succeeds and answers a question
    about a different number. Driven over the empty string, a short sha, an uppercase sha and
    a non-hex string.

    *(iv) PURITY IS STRUCTURAL, not promised (AR8 / DF-9-2-A).* The shipped module's own AST
    is walked and required to contain no import of ``subprocess``, ``pathlib``, ``datetime``,
    ``random``, ``os``, ``time`` or ``urllib``, and no call to ``open``. A predicate the gate
    depends on that could read a file or a clock is a predicate whose answer depends on when
    and where it ran.

    **The defect MOVES the observable:** flipping the bisection's parity, deleting the
    override, or relaxing the pin check each reddens a different assertion above.
    """
    # (i) the vocabulary
    assert set(PARTITION_VALUES) == {PARTITION_SEALED, PARTITION_OPEN, PARTITION_PRE_SEAL}
    assert len(PARTITION_VALUES) == 3, sorted(PARTITION_VALUES)
    for value in PARTITION_VALUES:
        assert len(partition_meaning(value).split()) >= 20, value
    with pytest.raises(UnregisteredPartition):
        partition_meaning("holdout")
    with pytest.raises(UnregisteredPartition):
        partition_meaning("")
    pre_seal_meaning = partition_meaning(PARTITION_PRE_SEAL).lower()
    assert "excluded" in pre_seal_meaning and "already existed" in pre_seal_meaning, (
        "the pre-seal meaning must say the member was EXCLUDED from sealing because output "
        "already existed — not that the bisection assigned it. A measured result and an "
        "unobservable one are different claims (DN-16-2-4)."
    )

    # (ii) all three outcomes, over GENERATED shas
    seen: dict[str, int] = {value: 0 for value in PARTITION_VALUES}
    for digit in "0123456789abcdef":
        sha = ("0" * 39) + digit
        derived = partition_of(sha, has_prior_output=False)
        expected = PARTITION_SEALED if int(digit, 16) % 2 == 1 else PARTITION_OPEN
        assert derived == expected, (sha, derived, expected)
        seen[derived] += 1
        # THE OVERRIDE, driven over the SAME sha: prior output wins, whatever the parity.
        assert partition_of(sha, has_prior_output=True) == PARTITION_PRE_SEAL, sha
        seen[PARTITION_PRE_SEAL] += 1
    assert seen[PARTITION_SEALED] == seen[PARTITION_OPEN] == 8, seen
    assert seen[PARTITION_PRE_SEAL] == 16, seen
    assert all(count > 0 for count in seen.values()), (
        f"non-vacuity: the generated family never produced {sorted(k for k, v in seen.items() if not v)}"
    )
    # The whole-sha reading is what ships, and it is not the same as reading one digit when
    # the digits disagree — asserted on a sha built to make them disagree.
    assert partition_of("f" * 39 + "0", has_prior_output=False) == PARTITION_OPEN
    assert partition_of("0" * 39 + "f", has_prior_output=False) == PARTITION_SEALED

    # (iii) it refuses a non-pin
    for bad in ("", "deadbeef", "NOT-A-SHA", "A" * 40, "0" * 39, "0" * 41, "z" * 40):
        with pytest.raises(UnsealablePin):
            partition_of(bad, has_prior_output=False)
        with pytest.raises(UnsealablePin):
            partition_of(bad, has_prior_output=True)

    # (iv) purity, STRUCTURALLY
    tree = ast.parse(_SEAL_MODULE.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    banned = imported & {
        "subprocess", "pathlib", "datetime", "random", "os", "time", "urllib", "socket", "uuid"
    }
    assert not banned, (
        f"argus/precision/gate_seal.py imports {sorted(banned)!r}. The partition rule is a "
        f"PURE predicate the externalization gate depends on (AR8): no I/O, no clock, no "
        f"network, no manifest resolution. Everything it needs arrives as an argument."
    )
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "open" not in calls, "gate_seal.py calls open() — see AR8 and DF-9-2-A"

    # AC1.2 — the derivation and its rejected alternatives live WITH the rule, in code.
    assert len(SEAL_RULE_DERIVATION.split()) >= 120, len(SEAL_RULE_DERIVATION.split())
    lowered = SEAL_RULE_DERIVATION.lower()
    for required in ("rejected", "set-relative", "structural grounds", "afterwards", "member_id"):
        assert required in lowered, required


# ─────────────────────────────────────────────────────────────────────────────
# AC1.4 / AC1.3 — the pre-seal set is DERIVED, and the table is RE-DERIVED
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_88_the_pre_seal_set_is_derived_from_committed_output() -> None:
    """TC-ArgusAgent-PRECISION-001-88 — AC1.4: *"already run over"* is READ, never typed.

    **Observable:** the ``members[]`` arrays of BOTH committed adjudication sets, versus
    ``_manifest.PRE_SEAL_MEMBER_IDS``, in **both** directions. The override is the load-bearing
    half of the seal rule — without it two already-audited members with odd pins would have
    been declared "sealed" — so the set it keys on may not be a hand-list somebody could
    extend. It is exactly the members Argus has actually been run over, read off the artifacts
    that record those runs.

    **Non-vacuity first** (both sides required non-empty, ``DF-15-2-A``): a broken extractor
    that returned an empty set would make the intersection assertions trivially true and this
    guard would pass while proving nothing.

    **The defect MOVES the observable:** adding a member to ``PRE_SEAL_MEMBER_IDS`` that no
    adjudication set names — the way somebody would quietly exclude an inconvenient member
    from the sealed side — reddens the second direction; dropping one reddens the first.
    """
    derived: set[str] = set()
    files_read = 0
    for path in _ADJUDICATION_SETS:
        assert path.is_file(), (
            f"the committed adjudication set {path.name} is absent, so the pre-seal "
            f"population could not be derived and this guard would pass over nothing"
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        members = [str(entry["member_id"]) for entry in payload["members"]]
        assert members, f"non-vacuity: {path.name} names ZERO audited members"
        derived.update(members)
        files_read += 1
    assert files_read == len(_ADJUDICATION_SETS) >= 2, files_read
    assert derived, "non-vacuity: the committed adjudication sets name ZERO members at all"
    assert PRE_SEAL_MEMBER_IDS, "non-vacuity: PRE_SEAL_MEMBER_IDS is empty"

    assert set(PRE_SEAL_MEMBER_IDS) == derived, (
        f"the frozen pre-seal set and the members Argus has ACTUALLY been run over disagree. "
        f"frozen-only={sorted(set(PRE_SEAL_MEMBER_IDS) - derived)} "
        f"run-over-only={sorted(derived - set(PRE_SEAL_MEMBER_IDS))}. A member that has been "
        f"run over cannot be a holdout, and a member that has not been run over may not be "
        f"excluded from sealing by being typed into this set."
    )
    # ...and every one of them resolves to a real manifest row that reads pre-seal.
    known = {spec.member_id: spec for spec in VALIDATION_CORPUS}
    for member_id in sorted(derived):
        assert member_id in known, member_id
        assert known[member_id].partition == PARTITION_PRE_SEAL, member_id
    # The override is LOAD-BEARING, asserted rather than remembered: at least one pre-seal
    # member carries an ODD pin, so the bisection alone WOULD have sealed an audited member.
    would_have_been_sealed = sorted(
        member_id
        for member_id in derived
        if partition_of(known[member_id].commit_sha, has_prior_output=False) == PARTITION_SEALED
    )
    assert would_have_been_sealed, (
        "no already-audited member carries an odd pin, so this corpus cannot demonstrate why "
        "the prior-output override exists. If that has genuinely become true, re-derive this "
        "guard rather than deleting it — the override is still required."
    )


def test_TC_ArgusAgent_PRECISION_001_89_the_frozen_table_is_re_derived_from_the_rule() -> None:
    """TC-ArgusAgent-PRECISION-001-89 — AC1.3: a materialization of a RULE, never a hand-list.

    **Observable:** ``_manifest.SEALED_PARTITION_TABLE`` versus
    ``gate_seal.partition_of`` re-run over every bench candidate's own pin, in **BOTH**
    directions — no table row the rule contradicts, and no rule output the table omits.

    ⛔ **Why re-deriving is the whole guard.** A guard that only read the table would be a
    guard over a hand-list: it would go green for a table somebody edited to move a member
    across the seal. Here the table is the FROZEN record and the rule is the AUTHORITY, and
    the guard is the assertion that they have not diverged. The table earns its place because
    after the protocol §6 R2 ratification act a ratified candidate is indistinguishable from a
    pre-seal member by its fields alone.

    **Non-vacuity, asserted BEFORE the equality:** the bench is non-empty, the table is
    non-empty, and BOTH partition classes are non-empty — a table that had become all-sealed
    or all-open would satisfy an equality check while describing a partition that does not
    partition anything.

    **The defect MOVES the observable:** re-pinning a member, editing a table row, adding a
    bench candidate without tabling it, or flipping the bisection's parity each reddens this.
    """
    bench = bench_candidates()
    table = dict(SEALED_PARTITION_TABLE)
    assert bench, "non-vacuity: the manifest holds ZERO bench candidates"
    assert table, "non-vacuity: the frozen partition table is empty"
    assert len(table) == len(SEALED_PARTITION_TABLE), "duplicate member id in the frozen table"
    classes = set(table.values())
    assert classes == {PARTITION_SEALED, PARTITION_OPEN}, (
        f"the frozen table records {sorted(classes)!r}. A bench candidate is never pre-seal "
        f"— no Argus output over any of them exists — and a table with only ONE class does "
        f"not partition anything, so an equality check over it would prove nothing."
    )
    for value in (PARTITION_SEALED, PARTITION_OPEN):
        assert sum(1 for v in table.values() if v == value) > 0, value

    # DIRECTION 1 — no table row the rule contradicts.
    checked = 0
    for spec in bench:
        assert spec.member_id in table, (
            f"{spec.member_id!r} is a bench candidate with no row in SEALED_PARTITION_TABLE. "
            f"The table is frozen at the seal commit and must cover the whole bench, or the "
            f"partition of the missing member survives nothing."
        )
        rederived = partition_of(spec.commit_sha, has_prior_output=False)
        assert rederived == table[spec.member_id], (
            f"{spec.member_id!r}: the frozen table says {table[spec.member_id]!r} and the "
            f"rule re-derives {rederived!r} from the pin {spec.commit_sha!r}. The table is a "
            f"MATERIALIZATION of the rule; if they disagree, one of them was edited."
        )
        # ...and the row's own derived property agrees with both, so nothing recomputes the
        # rule at a call site with a different answer.
        assert spec.partition == rederived, spec.member_id
        checked += 1
    assert checked == len(bench) >= len(table), (checked, len(bench), len(table))

    # DIRECTION 2 — no rule output the table omits.
    assert set(table) == {spec.member_id for spec in bench}, (
        f"table-only={sorted(set(table) - {s.member_id for s in bench})} "
        f"bench-only={sorted({s.member_id for s in bench} - set(table))}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC3 / AC6.2 — the condition, driven to BOTH verdicts at the real seam
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_90_the_seal_condition_is_driven_to_both_verdicts() -> None:
    """TC-ArgusAgent-PRECISION-001-90 — AC3.1/AC3.2/AC6.2: WHERE the verdict flips, at the seam.

    **Observable:** the LIVE :func:`decide_gate` outcome and §5's seal condition, over
    GENERATED populations built from real manifest rows at real pins.

    ⛔ **BREADTH IS PINNED TRUE SO THE SEAL IS THE ONLY TERM THAT CAN MOVE.** Each generated
    population contributes from ``k`` sealed members PLUS a fixed ``floor`` pre-seal members,
    so the total contributing count clears §5's breadth floor for every ``k`` while the sealed
    count sweeps ``0..len(sealed)``. Without the pre-seal ballast the two terms would move in
    lockstep and a mutation deleting the seal clause outright would leave every assertion
    green — which is precisely the unreal-guard finding the 2026-08-20 review made against
    Story 16.1's round 2.

    **Non-vacuity, asserted BEFORE anything is compared:** every clause ABOVE the seal clause
    must be false for every variant — reproducible, exhaustive, non-empty denominator, over
    threshold, breadth MET — or an assertion would be recording a refusal that has nothing to
    do with the seal.

    **Adversarial variants GENERATED with their count:** one population per sealed-member
    count in ``0..len(sealed)``, each asserted to carry exactly the partition mix it claims.
    The observed family is required to straddle the floor and to contain BOTH outcomes: a
    guard that never saw the verdict flip cannot notice a predicate that stopped flipping.

    **The defect MOVES the observable:** a seal predicate stuck at ``True`` reddens the
    below-floor half, one stuck at ``False`` reddens the above-floor half, and removing the
    dispatch branch reddens the outcome comparison while leaving the condition verdict intact.
    """
    sealed = sealed_corpus_members()
    floor = sealed_member_floor(int(registry_module().VALIDATION_SET_FLOOR_N))
    assert floor == contributing_member_floor(int(registry_module().VALIDATION_SET_FLOOR_N)), (
        "the seal floor forked from §5's breadth floor. They are ONE derived quantity "
        "reached through ONE function (AR7, DN-3) — two floors is how two corpora happened."
    )
    assert 1 < floor <= len(sealed), (
        f"non-vacuity: the derived floor {floor} does not lie strictly inside the generated "
        f"range 0..{len(sealed)}, so this guard could not observe the clause both ways"
    )
    ballast = floor  # pre-seal members, enough to satisfy breadth on their own

    observed: dict[int, str] = {}
    verdicts: dict[int, str] = {}
    for sealed_count in range(0, len(sealed) + 1):
        record, corpus = mixed_population(
            sealed_members=sealed_count,
            pre_seal_members=ballast,
            size=max((len(sealed) + ballast) * 2, 12),
        )
        decision = decide_over(record, corpus=corpus)
        fold = decision.fold
        # ── NON-VACUITY: every clause above the seal clause must be false ──────────────
        assert fold.determinism is None, fold.determinism
        assert isinstance(fold.exhaustiveness, Exhaustive), fold.exhaustiveness
        assert fold.precision is not None and fold.meets_threshold, fold.precision_ratio
        assert decision.breadth is not None and decision.breadth.holds, (
            f"{sealed_count} sealed + {ballast} pre-seal member(s) did not satisfy §5's "
            f"BREADTH floor, so this variant's refusal is not about the seal at all"
        )
        # ── the fixture carries the mix it claims, DERIVED from the fixture ────────────
        assert decision.seal is not None
        assert decision.seal.sealed_contributing_member_count == sealed_count, (
            decision.seal.sealed_contributing_member_ids
        )
        assert len(decision.seal.pre_seal_contributing_member_ids) == ballast
        assert decision.seal.contributing_member_count == sealed_count + ballast

        holds = sealed_count >= floor
        condition = section_5_condition(decision.conditions, SEAL_CONDITION_ID)
        assert condition.verdict == ("MET" if holds else "FAILED"), condition.measured
        assert condition.verdict in ("MET", "FAILED"), (
            "the seal condition's OWN verdict may never be UNEVALUABLE: the provenance of "
            "the evidence WAS established over a named population (AC3.2)"
        )
        assert decision.outcome == ("CLEARED" if holds else "BLOCKED"), decision.outcome_reason
        if not holds:
            # The SEAL is what refused it — not something above it.
            assert "SEAL condition" in decision.outcome_reason, decision.outcome_reason
            assert "BREADTH condition" not in decision.outcome_reason, decision.outcome_reason
            precision = section_5_condition(decision.conditions, "precision-at-least-80-percent")
            assert precision.verdict == "UNEVALUABLE", precision.measured
            assert decision.to_payload()["precision"]["evaluable"] is False
            assert decision.to_payload()["precision"]["fold_evaluable"] is True, (
                "the fold's OWN value must still be published beside the effective one — "
                "nothing is hidden, and a reader can see which conjunct moved"
            )
            assert decision.to_payload()["precision"]["seal_holds"] is False
            assert "EVIDENCE NOT DRAWN FROM THE SEALED PARTITION" in decision.precision_gate_status
            assert decision.closure_path, "a BLOCKED decision must carry a closure path"
        else:
            assert decision.to_payload()["precision"]["evaluable"] is True
            assert decision.to_payload()["precision"]["seal_holds"] is True
            assert decision.precision_gate_status == fold.gate_status, (
                "when the seal does not change the answer the fold's own sentence must be "
                "returned BYTE-FOR-BYTE (NFR-P1)"
            )
        observed[sealed_count] = decision.outcome
        verdicts[sealed_count] = condition.verdict

    assert set(observed.values()) == {"BLOCKED", "CLEARED"}, (
        f"the generated family observed only {sorted(set(observed.values()))} — a guard that "
        f"never saw the verdict flip cannot notice a predicate that stopped flipping"
    )
    assert set(verdicts.values()) == {"MET", "FAILED"}, sorted(set(verdicts.values()))
    assert all(observed[n] == "BLOCKED" for n in range(0, floor)), observed
    assert all(observed[n] == "CLEARED" for n in range(floor, len(sealed) + 1)), observed
    assert len(observed) == len(sealed) + 1 > floor, observed


def test_TC_ArgusAgent_PRECISION_001_91_the_measured_sentence_discriminates_and_is_inert_today() -> None:
    """TC-ArgusAgent-PRECISION-001-91 — AC3.3/AC3.4/AC3.5: what it says, and what did not move.

    **Observable, four of them.**

    *(i) AC3.3 — the counts are READ, never recounted.* :func:`assess_seal` is driven over
    the SAME ``ConcentrationDisclosure`` the decision publishes and over the partitions the
    decision carries, and its per-partition contributing sets are required to equal the ones
    derived here INDEPENDENTLY from the fixture's own rows — not read back out of the object
    under test. It is also required to RAISE over an empty corpus (the non-vacuity floor as a
    type) and over a member that carries no partition at all: defaulting an absent partition
    would publish a provenance nobody derived (``DF-9-2-B``).

    *(ii) AC3.4 — the sentence names its population, every contributing member's partition,
    and the sealed/open/pre-seal split of the corpus it measured*, including a zero. And it
    carries the DISCRIMINATION AC3.4 exists for: a reader must never have to guess whether
    ``0 sealed contributions`` means *no sealed member was in the population* or *sealed
    members were audited and emitted nothing*. Both branches of that sentence are driven.

    *(iii) The floor is the ONE derived floor*, not a second constant.

    *(iv) AC3.5 — the amendment is INERT on the live tree.* Over the committed record the
    outcome must still be ``BLOCKED`` and must still be blocked for the reason it was blocked
    for before — not for the seal — and §5 must now carry exactly six conditions. An amendment
    that binds when the measurement runs and changes nothing before it is exactly what *"made
    before the measurement it governs"* means, and it is a claim that has to be executed.
    """
    floor = sealed_member_floor(int(registry_module().VALIDATION_SET_FLOOR_N))

    # (i) the counts are read off the disclosure, and the floors are typed failures
    record, corpus = mixed_population(sealed_members=2, pre_seal_members=floor, size=12)
    partitions = member_partitions(corpus)
    concentration = derive_concentration(
        record, ratified_member_ids=[str(row["member_id"]) for row in corpus]
    )
    seal = assess_seal(
        concentration,
        partitions=partitions,
        validation_set_floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
        population_source=_RECORD_PATH.name,
    )
    # DERIVED HERE FROM THE FIXTURE — never read back out of `seal`.
    expected_sealed = tuple(
        sorted(
            str(row["member_id"])
            for row in corpus
            if row["partition"] == PARTITION_SEALED
            and str(row["member_id"]) in concentration.contributing_member_ids
        )
    )
    assert seal.sealed_contributing_member_ids == expected_sealed, (
        seal.sealed_contributing_member_ids,
        expected_sealed,
    )
    assert seal.adjudicated_population == concentration.adjudicated_population == len(
        record.live_rows()
    )
    assert seal.sealed_member_floor == floor
    with pytest.raises(VacuousSealError):
        assess_seal(
            concentration,
            partitions={},
            validation_set_floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
            population_source=_RECORD_PATH.name,
        )
    with pytest.raises(MissingMemberPartition):
        member_partitions([{"member_id": "x", "commit_sha": "0" * 40}])
    with pytest.raises(UnregisteredPartition):
        member_partitions([{"member_id": "x", "partition": "holdout"}])

    # (ii) the sentence names its population, the roll call, and the split — including zeros
    assert _RECORD_PATH.name in seal.measured
    assert "NOT over the emitted blocking population" in seal.measured
    assert str(seal.adjudicated_population) in seal.measured
    for member_id, partition in sorted(partitions.items()):
        if member_id in concentration.contributing_member_ids:
            assert f"{member_id}: {partition}" in seal.measured, member_id
    counts = dict(seal.corpus_partition_counts)
    assert set(counts) == set(PARTITION_VALUES), sorted(counts)
    assert counts[PARTITION_OPEN] == 0 and f"0 {PARTITION_OPEN}" in seal.measured, (
        "a partition with zero members must be STATED as zero, not omitted: 'the corpus "
        "holds 0 open members' and 'the corpus does not mention open members' read "
        "identically to a human and are different claims"
    )
    assert counts[PARTITION_SEALED] == 2 and counts[PARTITION_PRE_SEAL] == floor, counts
    assert "MEASURED SILENCE" in seal.measured or "measured silence" in seal.measured.lower() or (
        seal.sealed_contributing_member_ids
    ), seal.measured

    # ...and BOTH branches of AC3.4's discrimination are driven.
    empty_sealed, empty_corpus = mixed_population(
        sealed_members=0, pre_seal_members=floor, size=12
    )
    no_sealed_member = assess_seal(
        derive_concentration(
            empty_sealed, ratified_member_ids=[str(r["member_id"]) for r in empty_corpus]
        ),
        partitions=member_partitions(empty_corpus),
        validation_set_floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
        population_source=_RECORD_PATH.name,
    )
    assert "NO SEALED MEMBER WAS IN THE POPULATION AT ALL" in no_sealed_member.measured
    silent_record, silent_corpus = mixed_population(
        sealed_members=0, pre_seal_members=floor, size=12
    )
    silent = assess_seal(
        derive_concentration(
            silent_record,
            ratified_member_ids=[str(r["member_id"]) for r in silent_corpus],
        ),
        # the sealed members ARE in the corpus; none of them contributed a row.
        partitions=member_partitions(tuple(silent_corpus) + sealed_corpus_members()),
        validation_set_floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
        population_source=_RECORD_PATH.name,
    )
    assert "MEASURED SILENCE" in silent.measured, silent.measured
    assert silent.sealed_corpus_member_count > 0 and not silent.sealed_contributing_member_ids

    # (iv) AC3.5 — INERT on the committed population
    live = _record()
    decision = decide_over(live, corpus=ratified_corpus_members())
    assert decision.outcome == "BLOCKED", decision.outcome_reason
    assert "SEAL condition" not in decision.outcome_reason, (
        "the live decision is BLOCKED on the SEAL, which means the amendment changed the "
        "outcome's REASON on the committed population. It must still be BLOCKED for the "
        "reason it was blocked for before (AC3.5)."
    )
    assert section_5_condition(decision.conditions, SEAL_CONDITION_ID).verdict == "FAILED"
    assert len(decision.conditions) == len(SECTION_5_CONDITIONS) == 6, (
        "§5 must now carry exactly six conditions: the five historical ones in their "
        "historical positions, plus the appended seal condition (DN-16-1-2's rule, inherited)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC2 / AC5 — it partitions; it does not narrow, and the schema stays closed
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_92_it_partitions_and_does_not_narrow() -> None:
    """TC-ArgusAgent-PRECISION-001-92 — AC2.2/AC2.3/AC5.1/AC5.4: what this story did NOT move.

    **Observable, read LIVE rather than claimed.** ``VALIDATION_SET_FLOOR_N``,
    ``eligible_member_count()``, ``MANIFEST_FIELDS``, the ≥80% ``Fraction``, every candidate
    row's ``eligible_for_n``, and every member's ``adjudication_caveat``. A story whose whole
    direction of travel is *"clearing gets harder"* has to be able to show that it took
    nothing away, and *"it partitions; it does not narrow"* is a claim about counts.

    **AC2.3 — the constructor now validates the pin for EVERY row, driven BOTH ways.** The
    check used to live inside the ``eligible_for_n=True`` branch, after an early ``return``,
    so a candidate row accepted ``commit_sha="NOT-A-SHA"`` and ``commit_sha=""`` in silence —
    on exactly the rows the seal rule keys on. It is hoisted, and the refusal is driven over
    generated bad pins on an INELIGIBLE row (where it did not fire before) as well as on an
    eligible one, with the legal shape asserted to still construct so the guard is not simply
    refusing everything.

    ⛔ **``MANIFEST_FIELDS`` stays CLOSED at 9 (DN-16-2-3).** The partition is a DERIVED
    property and a ``@property`` is not a dataclass field, so ``-22`` stays green unedited.
    Asserted here too, in this story's own module, because a later change that added a tenth
    field would otherwise only redden a guard belonging to a different story.
    """
    manifest = registry_module()
    assert int(manifest.VALIDATION_SET_FLOOR_N) == 5, "the ONE locked floor moved"
    assert validation_floor_n() == 5
    assert eligible_member_count() == 5, "N moved — this story may not ratify or drop a member"
    assert PRECISION_GATE_THRESHOLD.numerator == 4 and PRECISION_GATE_THRESHOLD.denominator == 5
    assert len(MANIFEST_FIELDS) == 9, (
        f"MANIFEST_FIELDS is now {len(MANIFEST_FIELDS)}: {list(MANIFEST_FIELDS)}. The schema "
        f"is CLOSED at 9 and the partition is a DERIVED property, not a field (DN-16-2-3). "
        f"Extending it is an operator escalation, not a dev decision."
    )
    assert "partition" not in MANIFEST_FIELDS
    assert len(VALIDATION_CORPUS) == 21, len(VALIDATION_CORPUS)

    bench = bench_candidates()
    assert len(bench) == 14, len(bench)
    for spec in bench:
        assert spec.eligible_for_n is False, (
            f"{spec.member_id!r} became eligible for N. Ratification is the protocol §6 R2 "
            f"OPERATOR act; this story partitions the bench and ratifies nothing."
        )
        assert (spec.adjudication_caveat or "").strip(), spec.member_id
    # Every member of every partition is still a member, with its findings still disclosed.
    partitions = {spec.partition for spec in VALIDATION_CORPUS}
    assert partitions <= set(PARTITION_VALUES) and len(partitions) == 3, sorted(partitions)

    # AC2.3 — the hoisted pin check, driven BOTH ways on an INELIGIBLE row.
    candidate = dict(
        member_id="premise-probe",
        repository_url="https://example.invalid/x.git",
        licence="MIT",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
    )
    legal = CorpusMemberSpec(**candidate, commit_sha="a" * 40)  # the control: still constructs
    assert legal.partition in PARTITION_VALUES
    refused = 0
    for bad_sha in ("", "NOT-A-SHA", "deadbeef", "A" * 40, "0" * 39, "0" * 41, "z" * 40):
        with pytest.raises(ValueError, match="sha"):
            CorpusMemberSpec(**candidate, commit_sha=bad_sha)
        refused += 1
    assert refused == 7, refused
    # ...and the eligible branch, which validated before, still does.
    eligible = dict(candidate, eligible_for_n=True, ineligible_reason=None)
    CorpusMemberSpec(**eligible, commit_sha="a" * 40)
    with pytest.raises(ValueError, match="sha"):
        CorpusMemberSpec(**eligible, commit_sha="NOT-A-SHA")


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — the citation rule's PREDICATE, driven independently of any population
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_93_the_partition_citation_predicate_is_driven_both_ways() -> None:
    """TC-ArgusAgent-PRECISION-001-93 — AC4.3/AC4.4: the predicate, watched FAILING.

    ⛔ **THE VACUITY THIS GUARD EXISTS AGAINST.** At the moment this rule lands the
    post-seal detector-commit population is **EMPTY**, so a guard that only iterated real
    commits would pass forever over nothing — this project's signature defect, and the shape
    that shipped 4 of Epic 14's 35 guards unreal. AC4.3 forbids it here: the PREDICATE is
    driven to both outcomes over SYNTHETIC message strings, independently of the population.
    The ancestry half of the rule — which commits it applies to — is
    ``TC-ArgusAgent-PRECISION-001-94``'s, and it carries ``-75``'s three non-vacuity
    preconditions.

    **Adversarial variants GENERATED, with their counts:** every accepted value produces a
    citation in each of three real message shapes (trailer alone, trailer after a body,
    trailer with trailing whitespace); and a hand-built family of near-misses — an
    unregistered value, the token in prose rather than as a trailer, a missing colon, a
    lower-cased token, a trailer wrapped mid-line — each of which must be REFUSED. A
    predicate that accepted prose would make an unenforceable rule look enforced.
    """
    assert SEAL_CITATION_VALUES, "non-vacuity: no citation value is accepted at all"
    assert set(SEAL_CITATION_VALUES) == {PARTITION_SEALED, PARTITION_OPEN, "none"}
    assert len(SEAL_CITATION_RULE.split()) >= 60
    for fragment in (SEAL_CITATION_TRAILER, "sealed", "open", "none"):
        assert fragment in SEAL_CITATION_RULE, fragment

    accepted = 0
    for value in SEAL_CITATION_VALUES:
        for message in (
            f"{SEAL_CITATION_TRAILER}: {value}",
            f"fix(detector): tighten a rule\n\nbody text\n\n{SEAL_CITATION_TRAILER}: {value}\n",
            f"subject\n\n{SEAL_CITATION_TRAILER}:  {value}  \n",
        ):
            assert cites_partition(message) is True, message
            accepted += 1
    assert accepted == len(SEAL_CITATION_VALUES) * 3 > 0, accepted

    refused = 0
    for message in (
        "",
        "fix(detector): tighten a rule",
        f"{SEAL_CITATION_TRAILER}: holdout",
        f"{SEAL_CITATION_TRAILER}: SEALED",
        "this change was informed by the sealed partition",
        "the evidence came from open members only",
        f"{SEAL_CITATION_TRAILER} sealed",
        f"see the {SEAL_CITATION_TRAILER}: sealed note above and ignore it",
        f"{SEAL_CITATION_TRAILER.lower()}: sealed",
        f"{SEAL_CITATION_TRAILER}:",
    ):
        assert cites_partition(message) is False, message
        refused += 1
    assert refused == 10, refused


def test_the_seal_module_ships_no_repository_only_path() -> None:
    """``DF-9-2-A`` — the declared path sets are STRINGS the caller resolves, never ``Path``.

    Not a TC id: this is the module-level companion to ``-87``'s purity walk, kept beside it
    because ``DETECTOR_TUNING_PATHS`` is the one thing in the module that LOOKS like a path.
    A ``Path`` resolved at import time here would ship a wheel that cannot import.
    """
    from argus.precision.gate_seal import DETECTOR_TUNING_PATHS

    assert DETECTOR_TUNING_PATHS, "non-vacuity: the declared detector-tuning path set is empty"
    for declared in DETECTOR_TUNING_PATHS:
        assert isinstance(declared, str), declared
        assert not declared.startswith("/") and "\\" not in declared, declared
        assert (_REPO_ROOT / declared).exists(), (
            f"{declared!r} does not exist in this repository, so the rule that governs it "
            f"governs nothing — a misspelled pathspec reads exactly like a clean history"
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC1.5 / AC4.1 / AC4.2 — the ORDERING, checked against real git history
# ─────────────────────────────────────────────────────────────────────────────

#: AC1.5 — THE SEAL COMMIT. The commit that froze the partition rule, the frozen table and
#: the pre-seal set. Recorded as a full 40-character lowercase hex sha because a short sha is
#: ambiguous and this is the story's central citation, and recorded in a LATER commit than the
#: one it names, for the reason Story 15.1's ``CRITERIA_COMMIT_SHA`` was (``16d7100d`` froze,
#: ``4f4db78`` recorded): **a commit cannot cite itself.**
#:
#: ⛔ Story 16.4's deliverable is the ANCESTRY GUARD that ties this sha to every commit
#: carrying Argus output over a bench member. Story 16.2's obligation was to LAND FIRST and to
#: record this sha for 16.4 to cite; ``-94`` below discharges the half that is checkable
#: today — that this sha resolves, that it is an ancestor of HEAD, and that no commit
#: reachable from it touches a declared candidate-output path.
SEAL_COMMIT_SHA = "f89f028038dcd9881204f36bc404267c876b18f7"

#: A path KNOWN to carry commits. Without it a misspelled pathspec returns empty and reads
#: exactly like a clean history — the single most likely way ``-94`` could pass vacuously.
#: The ``TC-ArgusAgent-PRECISION-001-75`` template, reused rather than re-invented.
_CONTROL_PATH_WITH_COMMITS = "tests/corpus/_manifest.py"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    """A pure READ of this repository's history. Never mutates: no checkout, no commit."""
    return subprocess.run(
        ["git", "-C", str(_REPO_ROOT), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def _candidate_output_paths() -> tuple[str, ...]:
    """Story 15.1's declared candidate-output paths, IMPORTED rather than re-typed.

    A prose copy of a pinned constant is how two orderings come to disagree about what
    "candidate output" means (``AI-E9-7``). The import is function-local because
    ``tests/test_candidate_selection.py`` manipulates ``sys.path`` at import time and this
    module must not depend on the order pytest happens to collect them in.
    """
    from tests.test_candidate_selection import CANDIDATE_OUTPUT_PATHS

    return tuple(CANDIDATE_OUTPUT_PATHS)


def test_TC_ArgusAgent_PRECISION_001_94_the_seal_precedes_every_candidate_output() -> None:
    """TC-ArgusAgent-PRECISION-001-94 — AC1.5/AC4.1/AC4.2: the ordering, read from git.

    Story 16.2's central evidentiary claim is a claim about **git history**: the partition was
    frozen in a commit that precedes every commit containing Argus output over any member of
    it. An asserted intention is not evidence of it, so this reads the real object database.

    **Three non-vacuity preconditions, each asserted BEFORE the absence it protects**, copied
    from ``TC-ArgusAgent-PRECISION-001-75``, which already gets this right:

    1. the declared candidate-output path set and the declared detector-tuning path set are
       both **non-empty**, and every declared tuning path **exists** — a rule over a
       misspelled pathspec governs nothing;
    2. ``git log`` over a **control path known to carry commits** returns **non-empty** — a
       misspelled or moved pathspec returns empty and is **indistinguishable from a clean
       ordering**, which is the one way this guard could pass while seeing nothing;
    3. the seal sha **resolves** (``git cat-file -t`` -> ``commit``), is a full 40-character
       lowercase hex sha, and the ancestry predicate is driven to **BOTH** outcomes —
       ``True`` for seal->HEAD and ``False`` for HEAD->seal — so it is watched **failing**,
       not only passing.

    ⛔ **AC4.1's citation rule is enforced here over the REAL post-seal population, and that
    population is EMPTY on the day this lands.** That is stated rather than hidden: an empty
    iteration proves nothing, which is exactly why the citation PREDICATE is driven to both
    outcomes over synthetic messages by ``-93``, independently of any population. The loop
    below is the half that starts biting the moment somebody touches a detector, and it
    reports the remedy verbatim from ``SEAL_CITATION_RULE`` when it does.
    """
    from argus.precision.gate_seal import DETECTOR_TUNING_PATHS

    candidate_output_paths = _candidate_output_paths()

    # ── Precondition 1: both declared path sets are non-empty and REAL. ──
    assert candidate_output_paths, (
        "CANDIDATE_OUTPUT_PATHS is empty, so the absence asserted below is an absence over "
        "nothing. Declare where candidate output would land, or this guard forbids nothing."
    )
    assert DETECTOR_TUNING_PATHS, (
        "DETECTOR_TUNING_PATHS is empty, so the citation rule governs no path at all and the "
        "loop at the end of this guard iterates nothing by construction."
    )
    for declared in DETECTOR_TUNING_PATHS:
        assert (_REPO_ROOT / declared).exists(), (
            f"the declared detector-tuning path {declared!r} does not exist in this "
            f"repository. A rule over a path nobody has is a rule over nothing, and a "
            f"misspelled pathspec reads exactly like a clean history."
        )

    # ── Precondition 3a: the sha RESOLVES and is a full lowercase hex sha. ──
    assert len(SEAL_COMMIT_SHA) == 40 and SEAL_COMMIT_SHA.islower(), SEAL_COMMIT_SHA
    assert set(SEAL_COMMIT_SHA) <= set("0123456789abcdef"), SEAL_COMMIT_SHA
    kind = _git("cat-file", "-t", SEAL_COMMIT_SHA)
    assert kind.returncode == 0 and kind.stdout.strip() == "commit", (
        f"the recorded seal sha {SEAL_COMMIT_SHA} does not resolve to a commit in this "
        f"repository (git said {kind.stdout.strip()!r} / {kind.stderr.strip()!r}). Story "
        f"16.2's ordering claim is a claim about git history and cannot be established "
        f"against a sha that is not in it."
    )

    # ── Precondition 2: prove the invocation can FIND something. ──
    control = _git("log", "--format=%H", SEAL_COMMIT_SHA, "--", _CONTROL_PATH_WITH_COMMITS)
    assert control.returncode == 0, f"control `git log` failed: {control.stderr.strip()!r}"
    assert [line for line in control.stdout.splitlines() if line.strip()], (
        f"`git log {SEAL_COMMIT_SHA} -- {_CONTROL_PATH_WITH_COMMITS}` returned NOTHING. That "
        "path is known to carry commits, so this invocation is not capable of finding "
        "anything — and an invocation that finds nothing reports a clean ordering for a "
        "dirty one. Fix the invocation, never the assertion."
    )

    # ── THE CLAIM: no commit reachable from the seal touches candidate output. ──
    touching = _git("log", "--format=%H", SEAL_COMMIT_SHA, "--", *candidate_output_paths)
    assert touching.returncode == 0, f"`git log` failed: {touching.stderr.strip()!r}"
    offenders = [line for line in touching.stdout.splitlines() if line.strip()]
    assert not offenders, (
        f"{len(offenders)} commit(s) reachable from the seal sha touch a declared "
        f"candidate-output path {list(candidate_output_paths)}: {offenders[:5]}. The "
        f"partition would then have been frozen with Argus's verdicts over the bench already "
        f"in hand, which is the whole failure this seal exists to prevent."
    )

    # ── Precondition 3b: the ancestry predicate, driven to BOTH outcomes. ──
    forward = _git("merge-base", "--is-ancestor", SEAL_COMMIT_SHA, "HEAD")
    assert forward.returncode == 0, (
        f"the seal commit {SEAL_COMMIT_SHA} is NOT an ancestor of HEAD. It is on a detached "
        "or abandoned line of history, so it establishes no ordering on the branch that ships."
    )
    backward = _git("merge-base", "--is-ancestor", "HEAD", SEAL_COMMIT_SHA)
    assert backward.returncode != 0, (
        "HEAD reports as an ancestor of the seal commit, which cannot be true while the seal "
        "commit is also an ancestor of HEAD unless they are the same commit. The ancestry "
        "predicate is returning the same answer to both questions and discriminates nothing."
    )

    # ── AC4.1: every POST-SEAL detector-tuning commit CITES its partition. ──
    # ⛔ The population is EMPTY the day this lands, and that is recorded rather than hidden:
    # an empty iteration proves nothing, which is why -93 drives the predicate itself.
    listed = _git(
        "log", "--format=%H", f"{SEAL_COMMIT_SHA}..HEAD", "--", *DETECTOR_TUNING_PATHS
    )
    assert listed.returncode == 0, f"`git log` failed: {listed.stderr.strip()!r}"
    post_seal = [line for line in listed.stdout.splitlines() if line.strip()]
    uncited = []
    for sha in post_seal:
        message = _git("log", "-1", "--format=%B", sha)
        assert message.returncode == 0, message.stderr
        if not cites_partition(message.stdout):
            uncited.append(sha)
    assert not uncited, (
        f"{len(uncited)} post-seal commit(s) touching a declared detector-tuning path do not "
        f"cite the partition their evidence came from: {uncited[:5]}. {SEAL_CITATION_RULE}"
    )
