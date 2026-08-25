"""Story 17.4 — the guards over the COMMITTED RECORD of the one measurement of S1.

Verification area ``TC-ArgusAgent-PRECISION-001-148``, ``-150`` and ``-152``. Ids are minted from
``-147`` upward because ``-146`` was the highest in use at HEAD ``682b074``; no existing id is
renumbered, and an id here is a citation.

**Why this module is separate.** Every guard here reads the committed record, so they can only be
green at or after the commit that writes it — which is exactly the commit-order constraint §2.3
imposes. The guards that read the PRODUCER live in ``tests/test_successor_reach_producer.py`` and
are green before any measurement exists; ``-147``, the ordering guard, lives in
``tests/test_successor_output_ordering.py``.

⛔ **NO GUARD HERE ASSERTS A PREDICTED VALUE**, and that is ``DN-17-4-9``'s whole point. Story
17.4's acceptance criteria were written **before the number existed** — the contexting session
deliberately did not run the measurement — so a guard asserting *"S1 reaches N"*, or even
*"S1 reaches more than zero"*, would be a prediction. What is asserted is:

* **shape** — the record carries the fields a reader needs to audit it;
* **provenance** — every figure was derived by the run and every constant is imported;
* **internal consistency** — the recorded outcome and reason RE-DERIVE from the recorded counts
  through the frozen fold (``-150``), whatever that outcome turns out to be.

Non-vacuity is asserted **structurally**: ``population_walked`` equals the population re-derived
independently from ``adjudication-set-13-5.json``, ``population_skipped == 0``, and the walked
member set equals the ratified corpus. Never as a floor on the reach.

⛔ **Every guard here is green on the ubuntu CI matrix with NO third-party checkouts present.**
The corpus walk is a recorded LOCAL measurement; these guards read the committed record, the
committed adjudication set and the shipped modules, and nothing else.

⛔ **A guard here is never loosened to go green** (``DF-8-5-B``). If ``-148`` reddens because the
population moved, the answer is to report the measurement, not to adjust the literal.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

from argus.detectors.assertion_strength import (  # noqa: E402
    ASSERTION_STRENGTH_BANDS,
    UNESTABLISHED,
)
from argus.precision.silent_class import SILENT_CLASS_RULE_ID, UNADJUDICATED  # noqa: E402
from argus.store.canonical import dumps, loads  # noqa: E402

from precision_preregistration import (  # noqa: E402
    CONSEQUENCE_BELOW,
    CONSEQUENCE_MET,
    CRITERION_OUTCOMES,
    SUCCESSOR_OUTPUT_PATHS,
    evaluate,
)
from successor_reach_model import SUCCESSOR_RECORD_PATH  # noqa: E402

#: The committed adjudication set the population is re-derived from — Story 13.5's, READ.
_ADJUDICATION_SET = (
    _REPO_ROOT
    / "_bmad-output"
    / "design-artifacts"
    / "ArgusAgent"
    / "validation-corpus"
    / "adjudication-set-13-5.json"
)

# ═════════════════════════════════════════════════════════════════════════════════════════


def _record() -> dict:
    path = _REPO_ROOT / SUCCESSOR_RECORD_PATH
    if not path.is_file():
        pytest.fail(
            f"{SUCCESSOR_RECORD_PATH} is absent. The measurement is this story's deliverable; "
            f"run scripts/build_successor_reach_record.py --checkout-root <ROOT> "
            f"--snapshot-root <SHORT>."
        )
    return loads(path.read_text(encoding="utf-8"))


def _recorded_population() -> int:
    payload = json.loads(_ADJUDICATION_SET.read_text(encoding="utf-8"))
    return sum(
        1
        for member in payload["members"]
        for finding in member["findings"]
        if finding.get("rule_id") == SILENT_CLASS_RULE_ID
    )


def _recorded_members() -> set[str]:
    payload = json.loads(_ADJUDICATION_SET.read_text(encoding="utf-8"))
    return {member["member_id"] for member in payload["members"]}


def test_TC_ArgusAgent_PRECISION_001_148_the_measurement_covered_the_whole_population() -> None:
    """TC-ArgusAgent-PRECISION-001-148 — AC1.1/AC1.2/AC1.3: the walk was complete, and over WHAT.

    **Observable.** The committed record's ``population_walked`` / ``population_skipped`` /
    ``members_walked`` / ``rule_classes_walked``, re-derived independently from
    ``adjudication-set-13-5.json`` rather than compared against a literal.

    **Defect it moves.** A measurement that silently covered less than it claims. *"A skipped
    finding and a non-member are indistinguishable in the output"* — and here the difference lands
    directly on the criterion's yield-floor numerator, which decides the outcome.

    ⛔ **This is ``DN-17-4-9``'s STRUCTURAL non-vacuity**, and it is deliberately not a floor on
    the reach: ``walked == <the recorded population>`` and ``skipped == 0`` prove the measurement
    was taken over everything, without predicting what it found. *"reach > 0"* would be a
    prediction, and a prediction is the thing being refused.

    **Non-vacuity of the guard itself.** The re-derived population is asserted non-empty and the
    member set non-empty BEFORE either is compared, so a mis-parsed adjudication set cannot make
    this pass by producing zero on both sides.
    """
    expected_population = _recorded_population()
    expected_members = _recorded_members()
    assert expected_population > 0, (
        "adjudication-set-13-5.json re-derived ZERO findings of rule class "
        f"{SILENT_CLASS_RULE_ID!r}. Both sides of the comparison below would then be zero and "
        "this guard would pass over an unread corpus (AI-E11-1)."
    )
    assert len(expected_members) >= 5, (
        f"adjudication-set-13-5.json re-derived only {len(expected_members)} member(s); the "
        f"ratified corpus has five and this guard is reading the wrong thing."
    )

    record = _record()
    assert record["population_walked"] == expected_population, (
        f"the record walked {record['population_walked']} finding(s) but the committed "
        f"adjudication set carries {expected_population}."
    )
    assert record["population_skipped"] == 0, (
        f"{record['population_skipped']} finding(s) were SKIPPED. AC1.2: an unresolvable finding "
        f"is a REFUSAL, never a skip."
    )
    assert set(record["members_walked"]) == expected_members, (
        f"walked {sorted(record['members_walked'])} but the ratified corpus is "
        f"{sorted(expected_members)}. A member that contributes nothing is still a member of the "
        f"population the ratio was measured over, never one quietly dropped from the denominator."
    )

    # ⛔ AC1.3 / DN-17-4-7 — the rule-class axis has EXACTLY ONE member and is reported as one.
    assert record["rule_classes_walked"] == {SILENT_CLASS_RULE_ID: expected_population}
    assert record["rule_class_count_walked"] == 1
    assert set(record["eligible_by_rule_class"]) <= {SILENT_CLASS_RULE_ID}

    # ⛔ Contributing members are a SUBSET of the ratified five; the corpus did not grow.
    assert set(record["eligible_by_corpus_member"]) <= expected_members
    assert record["contributing_member_count"] == len(record["eligible_by_corpus_member"])
    assert record["eligible_population_count"] == len(record["rows"])
    assert sum(record["eligible_by_corpus_member"].values()) == len(record["rows"])
    assert record["corpus"]["eligible_member_count"] == 5, (
        "the shipped corpus manifest must still report FIVE eligible members after this "
        "measurement. No member was ratified, none moved between partitions, and DF-13-5-A's "
        "round is UNSPENT — AC1.6."
    )

    # ⛔ AC1.4 — the band axis is reported as COUNTS and carries no verdict weight.
    bands = set(ASSERTION_STRENGTH_BANDS) | {UNESTABLISHED}
    for key in ("assertion_band_totals_walked", "assertion_band_totals_eligible"):
        assert set(record[key]) == bands, f"{key} does not carry the shipped band vocabulary"
        assert all(isinstance(value, int) for value in record[key].values()), (
            f"{key} carries a non-integer; counts never a float (NFR-D2 / AR4)"
        )

    # ⛔ NFR-S1 — no source byte reached the machine record.
    for row in record["rows"]:
        assert set(row) >= {"locator", "member_id", "test_name", "row_id"}
        assert "source" not in row and "span" not in row, (
            "a row carries source text. NFR-S1: no corpus source byte reaches this record, and "
            "this story renders no worklist to carry one either (DN-17-4-10)."
        )


def test_TC_ArgusAgent_PRECISION_001_150_the_outcome_re_derives_from_its_own_counts() -> None:
    """TC-ArgusAgent-PRECISION-001-150 — AC2.1/AC2.3/AC3/AC9.4: the fold was CALLED, and it agrees.

    **Observable.** The recorded ``outcome`` and ``reason``, re-derived by calling the FROZEN
    ``precision_preregistration.evaluate()`` with the record's OWN recorded counts.

    **Defect it moves.** A verdict that does not follow from its own counts — the ``DF-8-5-C``
    shape applied to the one number this epic exists to protect. ``evaluate()``'s own docstring:
    *"A bare verdict is unauditable — NOT_MET with no counts cannot be told apart from NOT_MET
    measured over four findings."*

    ⛔ **THIS GUARD ASSERTS NO PARTICULAR OUTCOME** (AC9.4). It asserts INTERNAL CONSISTENCY. The
    outcome is whatever the frozen fold returns over the measured population; asserting a member
    of ``CRITERION_OUTCOMES`` here would be a prediction written after the fact, and would also
    have to be edited the first time the measurement legitimately moved — which is
    ``DF-8-5-B``'s failure mode with the arrow reversed.

    **Non-vacuity.** The re-derivation is driven RED by an EXECUTED mutation of a recorded count
    in an **in-memory copy** of the record — ⛔ nothing on disk, the tree is shared (§2.5).
    """
    record = _record()
    recorded = record["criterion"]

    # ── Non-vacuity 0: the assessment really carries the counts it claims to. ──
    for field in (
        "verdict_eligible_count",
        "contributing_member_count",
        "sealed_contributing_member_count",
        "true_positive_count",
        "false_accusation_count",
        "adjudicated_count",
        "ratio_floor",
        "exposure_ceiling",
        "floors",
        "reason",
        "outcome",
    ):
        assert field in recorded, f"the recorded assessment omits {field!r}; a bare verdict is unauditable"
    assert recorded["outcome"] in CRITERION_OUTCOMES, (
        f"{recorded['outcome']!r} is not a registered outcome. CRITERION_OUTCOMES is CLOSED at "
        f"three and this story invents no fourth terminal state (AC2.4)."
    )
    for name in (
        "verdict_eligible_population_derivation",
        "contributing_members_derivation",
        "sealed_contributing_members_derivation",
    ):
        assert recorded["floors"][name], (
            f"the resolved floors were recorded without {name}. ResolutionFloors carries its "
            f"derivations so the prose a record publishes and the arithmetic the gate runs are "
            f"ONE object rather than two statements that can disagree (DF-8-5-C)."
        )

    # ── THE CLAIM: the recorded verdict re-derives from the recorded counts. ──
    replay = evaluate(
        verdict_eligible_count=recorded["verdict_eligible_count"],
        contributing_member_count=recorded["contributing_member_count"],
        sealed_contributing_member_count=recorded["sealed_contributing_member_count"],
        true_positive_count=recorded["true_positive_count"],
        false_accusation_count=recorded["false_accusation_count"],
    )
    assert replay.outcome == recorded["outcome"], (
        f"the record says {recorded['outcome']!r} but its own counts fold to {replay.outcome!r}."
    )
    assert replay.reason == recorded["reason"], (
        "the recorded reason is not the reason the frozen fold produces for these counts. The "
        "reason is not decoration: it is what distinguishes an UNEVALUABLE on breadth from an "
        "UNEVALUABLE on an empty denominator."
    )

    # ── AC3.3 — an empty adjudicated population is recorded as such, never as 100% or 0%. ──
    if recorded["adjudicated_count"] == 0:
        assert recorded["measured_precision"] is None, (
            f"measured_precision is {recorded['measured_precision']!r} over an EMPTY adjudicated "
            f"population. It is null on purpose: an unmeasured population must not inherit a "
            f"flattering default, and bc55e36 is the measured precedent for what happens when it "
            f"does — a corpus that emitted nothing reported a CLEARED gate."
        )
        assert recorded["outcome"] != "MET", "an empty denominator can never be MET"

    # ── AC2.4 — the consequence is VERBATIM from the imported constant, or absent. ──
    consequence = recorded["consequence"]
    if recorded["outcome"] == "MET":
        assert consequence == CONSEQUENCE_MET
    elif recorded["outcome"] == "NOT_MET":
        assert consequence == CONSEQUENCE_BELOW
    else:
        assert consequence is None, (
            "UNEVALUABLE invokes NEITHER consequence. Borrowing one would convert a recorded "
            "failure to evaluate into a pass or a failure."
        )

    # ── AC3.4 — the gate stays shut at EVERY outcome, including MET. ──
    gate = record["gate_state"]
    assert gate["externalization_gate"] == "BLOCKED"
    assert gate["precision_keystone_ge_80_percent"] == "NOT CLEARED"
    assert gate["protocol_cleared"] is False
    assert record["promotes_nothing"] is True and record["gates_anything"] is False
    assert record["exhaustiveness"]["exhaustive"] is False
    assert record["exhaustiveness"]["gates_anything"] is False
    assert record["adjudication"]["external_adjudicator_ai_e16_7"] == "NOT REACHED", (
        "AI-E16-7 is a stated precondition that was NOT REACHED — never 'satisfied' and never "
        "silently omitted (AC7.2)."
    )
    assert all(row["disposition"] == UNADJUDICATED for row in record["rows"])
    assert all(
        row["adjudicator"] is None and row["adjudicated_on"] is None for row in record["rows"]
    )
    assert all(row["verdict_eligible"] is False for row in record["rows"])

    # ── AC3.1 — every short floor is NAMED with its measured count and its own derivation. ──
    for shortfall in record["criterion_shortfalls"]:
        assert shortfall["measured"] < shortfall["required"]
        assert shortfall["shortfall"] == shortfall["required"] - shortfall["measured"]
        assert shortfall["derivation"], "a shortfall without its floor's derivation is a bare number"
    if record["criterion_shortfalls"]:
        assert recorded["outcome"] == "UNEVALUABLE", (
            "a resolution floor is short, so the frozen fold must have returned UNEVALUABLE. A "
            "shortfall is REPORTED, never repaired: the floors were frozen before the number "
            "existed and -140 reds on a loosening."
        )

    # ── Non-vacuity A: the fold is watched producing MORE THAN ONE answer, so the equality
    #    above is a comparison rather than a tautology against a constant-returning function. ──
    starved = evaluate(
        verdict_eligible_count=0,
        contributing_member_count=0,
        sealed_contributing_member_count=0,
        true_positive_count=0,
        false_accusation_count=0,
    )
    floors = recorded["floors"]
    satisfied = evaluate(
        verdict_eligible_count=floors["verdict_eligible_population"],
        contributing_member_count=floors["contributing_members"],
        sealed_contributing_member_count=floors["sealed_contributing_members"],
        true_positive_count=floors["verdict_eligible_population"],
        false_accusation_count=0,
    )
    assert starved.outcome == "UNEVALUABLE" and satisfied.outcome == "MET", (
        f"the frozen fold returned {starved.outcome!r} and {satisfied.outcome!r} for a starved "
        f"and a satisfied population; it is not discriminating, so the equality asserted above "
        f"proves nothing."
    )

    # ── Non-vacuity B: an EXECUTED mutation of the record's OWN counts, GENERATED from the
    #    record's own floor table so it cannot go stale against a measurement that moved.
    #    ⛔ In memory only — the tree is shared with a peer session (§2.5). ──
    mutated = {
        "verdict_eligible_count": max(
            recorded["verdict_eligible_count"], floors["verdict_eligible_population"]
        ),
        "contributing_member_count": max(
            recorded["contributing_member_count"], floors["contributing_members"]
        ),
        "sealed_contributing_member_count": max(
            recorded["sealed_contributing_member_count"], floors["sealed_contributing_members"]
        ),
        "true_positive_count": recorded["true_positive_count"],
        "false_accusation_count": recorded["false_accusation_count"],
    }
    if record["criterion_shortfalls"]:
        assert mutated != {
            key: recorded[key] for key in mutated
        }, "the record reports a shortfall but raising every count to its floor changed nothing"
        forged = evaluate(**mutated)
        assert forged.reason != recorded["reason"], (
            "raising every short resolution count to its own recorded floor did not change what "
            "the frozen fold says, so this guard is not comparing anything and would accept any "
            "counts at all."
        )
    else:
        forged = evaluate(
            verdict_eligible_count=0,
            contributing_member_count=0,
            sealed_contributing_member_count=0,
            true_positive_count=0,
            false_accusation_count=0,
        )
        assert forged.reason != recorded["reason"], (
            "starving the population did not change what the frozen fold says about it"
        )

    # ── AC3.3, the SECOND arm — recorded whether or not the fold's check order reached it. ──
    arm = record["criterion_empty_denominator_arm"]
    assert arm["reached_by_the_fold"] == (not record["criterion_shortfalls"]), (
        "the record's claim about WHICH arm the verdict rests on disagrees with its own "
        "shortfall table"
    )
    if arm["denominator_is_empty"]:
        assert arm["precision_fraction_of_the_measured_counts"] is None, (
            "an empty adjudicated population was given a ratio. Never 100%, never 0%, and never "
            "omitted with the population implied to be fine (AC3.3)."
        )
    assert [entry["floor"] for entry in record["criterion_floor_results"]] == [
        "verdict_eligible_population",
        "contributing_members",
        "sealed_contributing_members",
    ], "the floor table must report all three resolution floors in the fold's own check order"
    assert {
        entry["floor"] for entry in record["criterion_floor_results"] if not entry["cleared"]
    } == {entry["floor"] for entry in record["criterion_shortfalls"]}


def test_TC_ArgusAgent_PRECISION_001_152_successor_output_lands_only_where_declared() -> None:
    """TC-ArgusAgent-PRECISION-001-152 — AC6.1/AC6.2/AC6.3/AC6.5: declared prefixes, and nowhere else.

    **Observable.** Every tracked path in the repository, enumerated from git, partitioned into
    *"under a declared ``SUCCESSOR_OUTPUT_PATHS`` prefix"* and *"not"*.

    **Defect it moves.** Successor output committed outside the declared prefixes makes ``-147``'s
    ordering claim unprovable against the object database: the guard walks the prefixes as git
    pathspecs, so output that landed elsewhere is output the ordering constraint never saw.
    Specification §8.2's first pointer, by name.

    **Non-vacuity — the enumeration is asserted REAL and TWO-SIDED first** (``MAINT-001-01``'s
    shape). A broken glob finds nothing and reports a clean tree, so: the enumeration is asserted
    large, the declared prefix is asserted to CONTAIN the record this story wrote (the positive
    side), and the classifier is asserted to reject a path outside it (the negative side).
    """
    listing = subprocess.run(
        ["git", "-C", str(_REPO_ROOT), "ls-files"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert listing.returncode == 0, f"git ls-files failed: {listing.stderr.strip()!r}"
    tracked = [line for line in listing.stdout.splitlines() if line.strip()]

    # ── Non-vacuity 1: the enumeration is real. ──
    assert len(tracked) > 200, (
        f"git ls-files returned only {len(tracked)} path(s); the enumeration is broken and the "
        f"absence asserted below would be an absence over nothing."
    )

    # ── Non-vacuity 2: the declared path set is non-empty and portable as a git pathspec. ──
    assert SUCCESSOR_OUTPUT_PATHS, "SUCCESSOR_OUTPUT_PATHS is empty; this guard forbids nothing"
    assert all(
        path and not path.startswith("/") and "\\" not in path
        for path in SUCCESSOR_OUTPUT_PATHS
    ), (
        f"every SUCCESSOR_OUTPUT_PATHS entry must be repository-relative and forward-slash so the "
        f"same string works as a git pathspec on the Windows local gate and the ubuntu CI "
        f"matrix; got {list(SUCCESSOR_OUTPUT_PATHS)}."
    )

    def declared(path: str) -> bool:
        return any(path.startswith(prefix + "/") for prefix in SUCCESSOR_OUTPUT_PATHS)

    # ── Non-vacuity 3: the classifier is driven to BOTH outcomes on real strings. ──
    assert declared(SUCCESSOR_RECORD_PATH), (
        f"{SUCCESSOR_RECORD_PATH} does not classify as being under a declared prefix, so the "
        f"classifier below cannot recognise successor output at all."
    )
    assert not declared("scripts/build_successor_reach_record.py"), (
        "the classifier accepted a path outside every declared prefix; it is not discriminating"
    )

    # ── THE CLAIM: successor output exists ONLY under a declared prefix. ──
    strays = sorted(
        path
        for path in tracked
        if not declared(path)
        and Path(path).name.startswith("successor-")
        and path.endswith(".json")
    )
    assert not strays, (
        f"{strays!r} look like successor-predicate output committed OUTSIDE the declared "
        f"prefixes {list(SUCCESSOR_OUTPUT_PATHS)}. Output committed elsewhere makes -147's "
        f"ordering claim unprovable against the object database (specification §8.2)."
    )

    # ── AC6.2 — the record's own prefix is the IMPORTED one, not a re-typed copy. ──
    record = _record()
    assert record["output_prefix"] == SUCCESSOR_OUTPUT_PATHS[0]
    assert SUCCESSOR_RECORD_PATH.startswith(SUCCESSOR_OUTPUT_PATHS[0] + "/")

    # ── AC6.5 — canonical, byte-stable, and NOT registered in the status-document registry. ──
    raw = (_REPO_ROOT / SUCCESSOR_RECORD_PATH).read_text(encoding="utf-8")
    assert dumps(loads(raw)) + "\n" == raw, (
        "the record does not round-trip through argus.store.canonical unchanged — it was "
        "hand-edited, or written by something other than the producer."
    )
    registry = (_REPO_ROOT / "tests" / "test_status_document_registry.py").read_text(
        encoding="utf-8"
    )
    assert SUCCESSOR_RECORD_PATH not in registry, (
        "the successor record must NOT be registered in the status-document registry: that guard "
        "globs sprint-change-proposal-*.md and epic-*-retro-*.md in the artifacts root, this "
        "record matches neither, and registering it would turn a green guard RED (DN-17-1-8's "
        "reasoning, reused)."
    )
