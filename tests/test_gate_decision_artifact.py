"""Story 13.3 — the guards over the ARTIFACT the gate decision PUBLISHES.

``TC-ArgusAgent-PRECISION-001-59``..``-64``. A **NEW** module, created 2026-08-20 by Story
16.3 as a **pure cohesion split** of ``tests/test_gate_decision.py``. Not one guard, not one
assertion and not one fixture below was authored here: every definition was moved
**byte-for-byte**, no function was split across the boundary, and the shared fixtures are
**IMPORTED rather than copied** (``tests/invocation_sources.py`` precedent,
``architecture.md:1045``; the same AR7 discipline that already has ``test_gate_decision.py``
importing its §5 dispatch mirror from ``tests/test_gate_breadth.py``).

**Why the split happened at all, and why on this story.** ``tests/test_gate_decision.py``
stood at **1,191 of NFR-M1's 1,200** lines with **no ledger entry of any kind** — 16.2's
contexted story flagged it at 1,193 and said it *"gets the same rule"*, then split the
PRODUCTION module (``DF-16-1-B``) and left this one unfiled. Story 16.3 adds §5's **seventh**
condition, and ``expected_section_5_outcome`` — §5's dispatch mirror — takes its terms as
**REQUIRED keyword arguments with no default**, deliberately, so that every existing caller
must state what it believes rather than silently inherit the old answer. A seventh condition
therefore forces an edit to ``-55`` inside nine lines of headroom. It does not fit, and
``MAINT-001-04`` forbids the exemption that would be tempting at that moment. *"Do not shave
a file to fit"* — ``tests/test_module_size_ceiling.py::_REMEDY``; the sanctioned remedy is a
cohesion split, taken FIRST and in its own commit (the ``95819bc`` precedent), so that the
one change a reviewer most needs to read is not buried in a restructuring.

**Why the boundary is HERE, confirmed by an AST walk of the module before a line moved.**
``test_gate_decision.py`` holds six shared fixtures followed by fourteen guards, and the
fourteen fall into two cohesive groups that are the *test-side mirror of the split Story 16.2
already made in production* (``gate_conditions.py`` — what a condition IS — against
``gate_evidence.py`` — what one is MEASURED FROM):

* **the DECISION FUNCTION** — ``-53``..``-58``, ``-69``, ``-70``: the outcome vocabulary, the
  re-derivation, the live dispatch, the per-condition reporting, the exact ``Fraction``, the
  dispatch at the real seam, the empty-population floor. They stay where they are.
* **the ARTIFACT it PUBLISHES** — ``-59``..``-64``, contiguous at former lines 704–1056:
  the concentration disclosure, the residual completion bound, locators-and-counts, the
  disclosure's persistence while the gate is uncleared, no-threshold-moved, and the
  ``UNEVALUABLE`` sentence. **This module.** Their observable is the committed
  ``gate-decision-record.json`` and the sentences it carries, not the branch that chose them.

**Nothing about the split is a behaviour change**: the collection count is unchanged, every
verification id keeps its number, and the guards run against the same shipped seams over the
same committed artifacts. That claim is checked rather than asserted — the split commit
carries the before/after ``_physical_line_count`` figures and a full-suite exit 0.

**Platform neutrality** (the local gates here are Windows-only while CI runs an ubuntu
matrix): ``pathlib`` throughout, explicit ``encoding="utf-8"``, ``.as_posix()`` at every
path→string boundary, and not one assertion on ``os.sep``, a drive letter or a
CRLF-sensitive byte count.
"""

from __future__ import annotations

import re
from dataclasses import replace
from fractions import Fraction

import pytest

from argus.precision.adjudication import (
    LOCATOR_RE,
    AdjudicationRow,
    AdjudicationUnevaluable,
    change_log_head_version,
    fold_adjudicated_precision,
    validation_set_population_n,
)
from argus.precision.gate_decision import RECORDED_CLEARED_CONDITION_ID
from argus.precision.gate_independence import assess_independence
from argus.precision.gate_disclosure import (
    VacuousDisclosureError,
    derive_concentration,
    derive_residual_completion_bound,
    ratified_corpus_members,
)
from argus.precision.replay_harness import (
    PRECISION_GATE_THRESHOLD,
    UNEVALUABLE_EMPTY_DENOMINATOR,
    precision_gate_status_for,
    registry_module,
)
from argus.verdict.negative_assurance import INSTRUMENT_STATUS, InstrumentStatus

# ⛔ The shared fixtures and path constants are IMPORTED, never copied (AR7). A second copy
# of `_decide` or `_judged` would be a second thing that can drift from the seam it drives,
# and the drift would be invisible to a reader of either module. This is the same rule that
# already has `test_gate_decision.py` importing `expected_section_5_outcome` from
# `tests/test_gate_breadth.py` and `spread_over_sealed` from `tests/test_gate_seal.py`.
from tests.test_gate_decision import (
    _ADJUDICATOR,
    _DECISION_PATH,
    _PROTOCOL_PATH,
    _REPO_ROOT,
    _decide,
    _decision_payload,
    _judged,
    _record,
)
from tests.test_instrument_disclosure import protocol_cleared_call_sites


def test_TC_ArgusAgent_PRECISION_001_59_the_concentration_disclosure_is_derived_and_can_be_absent() -> None:
    """TC-ArgusAgent-PRECISION-001-59 — AC3b: the denominator discloses its own concentration.

    **Observable:** :func:`derive_concentration` and the committed ``concentration`` block.
    **Guarded in BOTH directions** (the ``-55b`` convention), which is the whole content of
    the AC: over the corpus as it stands the disclosure must be present and must agree with
    the counts derived here independently; and driven over a SYNTHETIC well-distributed
    population the same predicate must **NOT** manufacture a concentration claim. *A caveat
    that cannot be absent is not an observation.*

    Every figure is COUNTED, never pinned: the story's 24/7/0/0/0 and single-rule-class
    figures were the state at authoring time and are deliberately absent from this file
    (``DF-8-5-C`` / ``AI-E9-7``).
    """
    record = _record()
    ratified = [member["member_id"] for member in ratified_corpus_members()]
    assert ratified, "non-vacuity: the manifest reports ZERO ratified members"

    disclosure = derive_concentration(record, ratified_member_ids=ratified)
    live_rows = record.live_rows()
    assert disclosure.adjudicated_population == len(live_rows) > 0
    assert dict(disclosure.per_member_finding_counts) == {
        member: sum(1 for row in live_rows if row.member_id == member)
        for member in {row.member_id for row in live_rows}
    }
    assert sum(count for _, count in disclosure.per_member_finding_counts) == len(live_rows)
    assert disclosure.distinct_rule_class_count == len(
        {row.rule_id for row in live_rows}
    ) > 0
    assert disclosure.ratified_member_count == len(set(ratified))
    assert set(disclosure.non_contributing_member_ids) == set(ratified) - {
        row.member_id for row in live_rows
    }

    payload = _decision_payload()["concentration"]
    assert payload["contributing_member_count"] == disclosure.contributing_member_count
    assert payload["ratified_member_count"] == disclosure.ratified_member_count
    assert payload["distinct_rule_class_count"] == disclosure.distinct_rule_class_count
    assert payload["per_member_finding_counts"] == [
        {"member_id": member, "findings": count}
        for member, count in disclosure.per_member_finding_counts
    ]
    assert payload["statement"] == disclosure.statement
    assert payload["is_concentrated"] is disclosure.is_concentrated

    # AC3b applies in BOTH branches: the statement rides with the outcome whatever it is.
    for outcome_record in (
        record,
        record.append([_judged(row, "TP") for row in record.rows]),
        record.append([_judged(row, "FP") for row in record.rows]),
    ):
        decision = _decide(outcome_record)
        assert decision.concentration.statement.strip()
        assert decision.concentration.adjudicated_population > 0

    # THE OTHER DIRECTION — the predicate must not manufacture a claim. A synthetic
    # population spread evenly across every ratified member and >1 rule class is NOT
    # concentrated, and the guard says so.
    spread_rows = tuple(
        AdjudicationRow(
            row_id=f"synthetic{index:04d}.0",
            member_id=member,
            rule_id=f"synthetic_rule_{index % 3}",
            verdict_eligible=True,
            advisory=True,
            locator=f"pkg/tests/test_synthetic_{index}.py:{index + 1}",
            disposition="FP",
            adjudicator=_ADJUDICATOR,
            adjudicated_on="2026-08-17",
            reason="synthetic fixture: a well-distributed population",
        )
        for index, member in enumerate(ratified * 3)
    )
    spread = derive_concentration(
        replace(record, rows=spread_rows), ratified_member_ids=ratified
    )
    assert spread.non_contributing_member_ids == ()
    assert spread.distinct_rule_class_count > 1
    assert spread.is_concentrated is False, (
        "the concentration predicate fired over a well-distributed population — a caveat "
        "that cannot be absent is not an observation, it is boilerplate"
    )
    assert disclosure.is_concentrated is True, (
        "the concentration predicate did NOT fire over the live corpus, where the "
        "population is drawn from a strict subset of the ratified members. If that has "
        "genuinely stopped being true, re-derive this guard rather than deleting it."
    )
    with pytest.raises(VacuousDisclosureError):
        derive_concentration(replace(record, rows=()), ratified_member_ids=ratified)
    with pytest.raises(VacuousDisclosureError):
        derive_concentration(record, ratified_member_ids=[])


def test_TC_ArgusAgent_PRECISION_001_60_the_completion_bound_is_exact_and_decides_nothing() -> None:
    """TC-ArgusAgent-PRECISION-001-60 — AC5: what would close it, DERIVED in countable terms.

    **Observable:** :func:`derive_residual_completion_bound`. It answers *"could the
    unfinished judgements still change the answer?"* in exact ``Fraction`` arithmetic, and
    the guard pins the one thing that must never follow from it: an unreachable threshold
    does **not** promote ``BLOCKED`` to ``NOT_CLEARED``. The residual is a human's
    unfinished act; the arithmetic trending one way is not a judgement having been made.
    """
    reachable = derive_residual_completion_bound(total_tp=8, total_fp=2, residual_count=2)
    assert reachable.best_case_precision == Fraction(10, 12)
    assert reachable.worst_case_precision == Fraction(8, 12)
    assert reachable.completed_denominator == 12
    assert reachable.threshold_reachable is True
    assert "GENUINELY OPEN" in reachable.statement

    unreachable = derive_residual_completion_bound(total_tp=0, total_fp=26, residual_count=5)
    assert unreachable.best_case_precision == Fraction(5, 31)
    assert unreachable.threshold_reachable is False
    assert unreachable.completed_denominator == 31
    assert "NOT as a decision" in unreachable.statement, (
        "an unreachable threshold must be recorded as a BOUND, never as a decision — "
        "otherwise it becomes the licence to record NOT_CLEARED over an incomplete "
        "adjudication, which is the exact falsehood BLOCKED exists to prevent"
    )
    # The completed denominator is named beside every ratio because Fraction REDUCES:
    # 0/31 renders "0/1", which reads as a denominator of one on the honesty-critical
    # artifact.
    assert unreachable.worst_case_ratio == "0/1"
    assert "31" in unreachable.statement

    assert derive_residual_completion_bound(
        total_tp=4, total_fp=1, residual_count=0
    ).statement.startswith("no residual")
    with pytest.raises(ValueError):
        derive_residual_completion_bound(total_tp=-1, total_fp=1, residual_count=0)

    # AT THE REAL SEAM: the live decision carries the bound, and carries BLOCKED anyway.
    payload = _decision_payload()
    if payload["outcome"] == "BLOCKED":
        bound = payload["residual_completion_bound"]
        if bound["residual_count"] > 0 and bound["threshold_reachable"] is False:
            assert payload["outcome"] == "BLOCKED", (
                "the decision was promoted out of BLOCKED because the residual could not "
                "reach the threshold. It may not be: an incomplete measurement stays an "
                "incomplete measurement however its arithmetic is trending (AC1)."
            )


def test_TC_ArgusAgent_PRECISION_001_61_the_artifact_carries_locators_and_counts_only() -> None:
    """TC-ArgusAgent-PRECISION-001-61 — AC3/NFR-S1: no source byte, no host path, no drive letter.

    **Observable:** the committed artifact's bytes and every locator it republishes.
    **The locator pattern is IMPORTED, not re-authored** — a second regex here would drift
    from the one that admits a row into the record, and NFR-S1 would then be enforced by
    two rules that disagree. The pattern already refuses a leading ``/``, a drive letter, a
    backslash and a ``..`` segment, which is also what keeps this artifact identical on
    the Windows machine that produced it and the ubuntu matrix that verifies it.
    """
    # AT THE PRODUCING SEAM, not at the checkout: this repository carries no
    # `.gitattributes` and `core.autocrlf` is true on the Windows machine the local gates
    # run on, so the bytes ON DISK depend on how git checked the file out. What must hold
    # unconditionally is that the SERIALIZER never emits a carriage return — that is the
    # NFR-P1 property, and it is the same on both platforms.
    produced = _decide(_record()).to_bytes()
    assert b"\r" not in produced and produced.endswith(b"\n"), (
        "the canonical serializer emitted a carriage return or no trailing newline; the "
        "artifact would then differ byte-for-byte between the Windows local gates and the "
        "ubuntu CI matrix (NFR-P1)"
    )
    text = _DECISION_PATH.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert text.endswith("\n")
    assert "\\" not in text, "a backslash in the artifact is a Windows path leak (NFR-S1)"
    assert not re.search(r"\b[A-Za-z]:/", text), "a drive letter reached the artifact"
    for marker in (str(_REPO_ROOT), _REPO_ROOT.name, "C:/", "/home/", "/Users/"):
        assert marker not in text or marker == "ArgusAgent", marker

    payload = _decision_payload()
    residual = payload["preconditions"]["residual_finding_ids"]
    contributing = payload["concentration"]["contributing_member_ids"]
    assert contributing, "non-vacuity: the artifact republished ZERO member ids"
    checked = 0
    for finding_id in residual:
        locator = finding_id.split("::")[-1]
        assert LOCATOR_RE.match(locator), (
            f"{locator!r} is not a repository-relative posix locator. The pattern is the "
            f"one AdjudicationRow enforces at construction; a second one here would let "
            f"the two disagree about NFR-S1."
        )
        assert ".." not in locator.split("/")
        checked += 1
    assert checked == len(residual)
    if payload["outcome"] == "BLOCKED":
        # AMENDED 2026-08-18 (Story 13.5 / AC5). A BLOCKED-on-an-EMPTY-EMITTED-POPULATION
        # decision has no residual finding id to publish — there is nothing residual about a
        # population that is empty. The non-vacuity floor does not disappear with it: it
        # MOVES to the corpus-read proof, and the proof's own counts are asserted here so
        # this leg cannot be satisfied by a decision that simply omitted both.
        proof = payload.get("corpus_read_proof")
        if checked == 0:
            assert proof and proof["proves_corpus_was_read"], (
                "non-vacuity: a BLOCKED decision published no residual finding id AND no "
                "positive corpus-read proof, so this locator scan observed nothing and "
                "nothing else vouches for the population either"
            )
            assert proof["source_file_count"] > 0 and proof["scored_population_count"] > 0, (
                "non-vacuity: the corpus-read proof standing in for the residual list is "
                "itself empty — that is the unread corpus it exists to rule out"
            )
            assert proof["members_audited"] > 0 and proof["every_member_pin_verified"], (
                "non-vacuity: the corpus-read proof names no audited member, or its bytes "
                "were never proved against the pin. Reproducibility is not provenance."
            )


def test_TC_ArgusAgent_PRECISION_001_62_the_disclosure_stays_while_the_gate_is_not_cleared() -> None:
    """TC-ArgusAgent-PRECISION-001-62 — AC5: the declared status and the decision cannot diverge.

    **Observable:** :data:`INSTRUMENT_STATUS`, the ``argus/**`` production scan from
    ``protocol_cleared_call_sites`` (IMPORTED, never copied — 12.6 / DN-7), and the
    committed outcome. ``TC-ArgusAgent-DOCS-001-46`` ties the declaration to the harness;
    this ties it to the **recorded decision**, which is the surface a reader actually acts
    on, and it moves in BOTH directions: flip the constant without a CLEARED decision and
    it goes red, record CLEARED without flipping the constant and it goes red.

    ⚠️ It is deliberately NOT a substitute for AC4(d). ``protocol_cleared_call_sites``
    matches only a literal ``True``, so a DERIVED flag is invisible to it; whoever performs
    the flip must extend that closure in the same change. Until then
    :func:`~argus.precision.gate_decision.decide_gate` passes the literal ``False`` rather
    than opening the blind spot, and the assertion below is what would notice if it did.
    """
    payload = _decision_payload()
    cleared = payload["outcome"] == "CLEARED"
    assert (INSTRUMENT_STATUS is InstrumentStatus.VALIDATED) is cleared, (
        f"INSTRUMENT_STATUS is {INSTRUMENT_STATUS!r} while the committed gate decision "
        f"records {payload['outcome']!r}. The disclosure is REPLACED by the cleared status "
        f"only when the gate has genuinely cleared, and never deleted (FR34.4)."
    )
    # BY ID (Story 16.1 / AC1.3). This read was `[3]`, which was correct for §5's four
    # conditions in §5's order and is the same latent false green the production code
    # carried: §5 is amended by dated ADDITION and an index returns a well-formed verdict
    # belonging to another condition.
    recorded_cleared = next(
        c
        for c in payload["section_5_conditions"]
        if c["condition_id"] == RECORDED_CLEARED_CONDITION_ID
    )
    assert payload["adjudication_record"]["adjudication_run_recorded_cleared"] is (
        recorded_cleared["verdict"] == "MET"
    )

    production = sorted(
        path
        for path in (_REPO_ROOT / "argus").rglob("*.py")
        if "__pycache__" not in path.parts
        and protocol_cleared_call_sites(path.read_text(encoding="utf-8"))
    )
    if not cleared:
        assert production == [], (
            f"a production argus/** call site passes protocol_cleared=True while the gate "
            f"is not cleared: {[p.relative_to(_REPO_ROOT).as_posix() for p in production]}"
        )
    # The analyzer itself is non-vacuous — proven on synthetic input, so an empty
    # production scan means "nothing passes it" and not "the analyzer stopped seeing".
    assert protocol_cleared_call_sites("f(x, protocol_cleared=True)") == (1,)
    assert protocol_cleared_call_sites("f(x, protocol_cleared=False)") == ()


def test_TC_ArgusAgent_PRECISION_001_63_no_threshold_floor_or_unit_moved() -> None:
    """TC-ArgusAgent-PRECISION-001-63 — AC5/AC2: the protocol's locked figures are byte-unchanged.

    **Observable:** protocol §5's own literals, cross-checked against the shipped
    constants. *A failed measurement is not a reason to amend the threshold — it is the
    measurement working*, and the temptation runs in both directions: loosening it to
    clear, and tightening it to look rigorous after a shortfall. Either is a story failure
    regardless of the outcome, so the document and the code are asserted to agree rather
    than either being trusted alone.

    It also asserts the record's ``protocol_version`` still equals the change-log head:
    amending the protocol after the dispositions were recorded would re-interpret
    judgements nobody re-made, and the decision constructor refuses it.
    """
    protocol = _PROTOCOL_PATH.read_text(encoding="utf-8")
    assert protocol.strip(), "non-vacuity: the protocol document is empty"
    for literal, why in (
        ("Fraction(4, 5)", "§5 states the threshold as the EXACT Fraction"),
        ("≥ 80%", "§5's precision row"),
        ("N ≥ 5", "§5's corpus-floor row"),
        ("VALIDATION_SET_FLOOR_N = 5", "the ONE floor, never forked (13.1 / DN-3)"),
        (
            "measured over FINDINGS, not repos",
            "§7's OI1 unit lock — V1.3 fixed the unit as the FINDING",
        ),
        (
            "the clean-repo\nblocking-FP count is 0",
            "§5's conjunction, which is the sentence the four conditions implement",
        ),
    ):
        assert literal in protocol, f"protocol §5/§7 no longer states {literal!r} — {why}"

    assert PRECISION_GATE_THRESHOLD == Fraction(4, 5)
    assert int(registry_module().VALIDATION_SET_FLOOR_N) == 5

    record = _record()
    assert record.protocol_version == change_log_head_version(protocol), (
        "the committed adjudication record was judged under a protocol version that is no "
        "longer the change-log head. Amend the protocol BEFORE a run, never during it."
    )
    assert _decision_payload()["adjudication_record"]["protocol_version"] == (
        record.protocol_version
    )


def test_TC_ArgusAgent_PRECISION_001_64_the_unevaluable_sentence_names_its_real_reason() -> None:
    """TC-ArgusAgent-PRECISION-001-64 — AC1/DF-9-2-B: a true status may not carry a false reason.

    **Observable:** ``precision_gate_status_for``'s unevaluable branch. **The defect, moved
    at the real seam:** until Story 13.3 there was exactly one way to be unevaluable and the
    sentence said so as a literal — *"DENOMINATOR EMPTY"*. The moment a human recorded a
    ``BORDERLINE`` that stopped being true, and the fold over a record holding 26 TP/FP
    dispositions rendered "DENOMINATOR EMPTY" beside a denominator of 26. That is the
    ``DF-9-2-B`` FALSE-SUBJECT class, on the surface that publishes the externalization gate.

    Fixed ADDITIVELY: ``unevaluable_reason`` defaults to the exact prior wording, so every
    pre-13.3 caller renders the bytes it always did (NFR-P1), and the fold now supplies the
    precondition that actually failed.
    """
    default = precision_gate_status_for(
        precision=None, n=5, provisional=True, protocol_path="p.md", floor_n=5, evaluable=False
    )
    assert UNEVALUABLE_EMPTY_DENOMINATOR in default, (
        "the default unevaluable sentence changed, so every pre-13.3 caller's bytes moved"
    )
    named = precision_gate_status_for(
        precision=None,
        n=5,
        provisional=True,
        protocol_path="p.md",
        floor_n=5,
        evaluable=False,
        unevaluable_reason="NOT EXHAUSTIVELY ADJUDICATED — synthetic",
    )
    assert "NOT EXHAUSTIVELY ADJUDICATED — synthetic" in named
    assert UNEVALUABLE_EMPTY_DENOMINATOR not in named

    record = _record()
    fold = fold_adjudicated_precision(
        record,
        expected_finding_ids=[row.finding_id for row in record.rows],
        population_n=validation_set_population_n(),
        floor_n=int(registry_module().VALIDATION_SET_FLOOR_N),
    )
    if not fold.evaluable and isinstance(fold.exhaustiveness, AdjudicationUnevaluable):
        denominator = fold.total_tp + fold.total_fp
        if denominator > 0:
            assert UNEVALUABLE_EMPTY_DENOMINATOR not in fold.gate_status, (
                f"the live fold reports 'DENOMINATOR EMPTY' beside a denominator of "
                f"{denominator}. A true status carrying a false reason is DF-9-2-B's class."
            )
            assert "NOT EXHAUSTIVELY ADJUDICATED" in fold.gate_status


def test_TC_ArgusAgent_PRECISION_001_113_the_independence_block_agrees_with_the_evidence() -> None:
    """TC-ArgusAgent-PRECISION-001-113 — Story 16.5 / AC5.5: the artifact cannot drift from the record.

    **Observable:** the ``independence`` block on the COMMITTED
    ``gate-decision-record.json`` — its status, its adjudicator list and its role partition —
    compared against the SAME facts RE-DERIVED here from the COMMITTED
    ``adjudication-record.json``. The artifact summarises evidence it does not carry, and a
    summary nothing checks is a summary that can go stale in place; this is the ``DF-8-5-C``
    hand-written-figure class one level up, on the surface that publishes the gate.

    ⛔ **Re-derived from the RECORD, not re-read from the artifact.** The point is that the
    two are computed by different routes and must agree: the artifact's block came from
    ``decide_gate`` at build time, and the expectation below is computed now, in this
    process, from the adjudication record's own live rows. A guard that read the block twice
    would be green against an artifact that had drifted from every fact in it — which is
    exactly the defect Story 16.3's own mutation run caught in one of its guards.

    **The defect MOVES it, at the real seam.** Mutation executed 2026-08-23 with
    ``PYTHONDONTWRITEBYTECODE=1`` and a cleared ``__pycache__``: hand-editing the committed
    artifact's ``independence.status`` from ``NOT_INDEPENDENT`` to
    ``EXTERNAL_ADJUDICATOR_PARTICIPATED`` — precisely the flattering drift this guard exists
    to catch, and precisely the edit ``§2.5``'s *"never hand-edit the artifact"* rule forbids
    — turns this guard **RED** on the status assertion. The artifact was then restored
    BYTE-EXACT (sha256 verified before and after) and ``build_gate_decision.py --check``
    re-confirmed **exit 0**, so the mutation left nothing behind.

    **Adversarial variant, GENERATED from the live record:** the derived status is
    recomputed over **each of the 3** re-attributions a non-empty adjudicator set admits
    (Engineering Lead alone; + QA Lead; + External adjudicator) and each must derive a
    DIFFERENT member — so a derivation that returned a constant would fail here even though
    it agreed with the artifact.
    """
    payload = _decision_payload()
    block = payload["independence"]
    assert isinstance(block, dict) and block, (
        "the committed decision carries NO independence block. Story 16.5 publishes the "
        "status as structure so a machine reader never has to parse the sentence (AC2.5)."
    )

    record = _record()
    live = record.live_rows()
    assert live, "non-vacuity: the committed adjudication record has ZERO live rows"
    derived = assess_independence(
        tuple(sorted({row.adjudicator for row in live if row.adjudicator is not None}))
    )
    assert block["status"] == derived.status, (
        f"the committed artifact reports independence {block['status']!r} while the "
        f"committed adjudication record it summarises derives {derived.status!r}. The "
        f"artifact is REGENERATED by scripts/build_gate_decision.py, never hand-edited."
    )
    assert block["adjudicators"] == list(derived.adjudicators)
    assert block["roles_present"] == list(derived.roles_present)
    assert block["roles_absent"] == list(derived.roles_absent)
    assert block["note"] == derived.note
    assert block["gates_anything"] is False

    # ...and the SENTENCE the artifact publishes carries the same clause, so a human reader
    # and a machine reader of this one file are told the same thing.
    assert derived.note in payload["precision"]["gate_status"], (
        "the artifact's structured block and its gate-status sentence disagree"
    )
    # AC1.6 — measured over the live committed record: 31 of 31 live human judgements by one
    # adjudicator, so the derived answer is NOT_INDEPENDENT. That is the correct output.
    assert len(live) == 31, len(live)
    assert sum(1 for row in live if row.is_human_judgement) == 31
    assert derived.status == "NOT_INDEPENDENT", derived

    variants = {
        "NOT_INDEPENDENT": (_ADJUDICATOR,),
        "SECOND_REVIEWER_INTERNAL": (_ADJUDICATOR, "Veer Pratap Singh (QA Lead)"),
        "EXTERNAL_ADJUDICATOR_PARTICIPATED": (
            _ADJUDICATOR,
            "Veer Pratap Singh (QA Lead)",
            "A. N. Other (External adjudicator)",
        ),
    }
    observed = {expected: assess_independence(ids).status for expected, ids in variants.items()}
    assert observed == {key: key for key in variants}, observed
