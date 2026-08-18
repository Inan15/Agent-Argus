"""Story 13.2 / AC2–AC6 — the adjudication record, and the guards that keep it honest.

``TC-ArgusAgent-PRECISION-001-39``..``-52``. A NEW module, for the reason 13.1 / DN-10
already recorded and this story re-measured: ``tests/test_evidence_citation.py`` is at
**1199/1200** lines and ``tests/test_instrument_disclosure.py`` at **1185/1200**, so the
sanctioned remedy is a cohesion split rather than shaving a load-bearing guard file.

**What every guard here is ultimately protecting.** The externalization gate flips on a
recorded human adjudication. If the record can be produced by a machine, be partially
filled and still report a number, be re-interpreted after the fact by amending the
protocol, or be iterated while empty — then the gate flips on evidence that does not
exist, and **every guard downstream, including Story 13.3's, would agree that it had.**

**GUARD-ADEQUACY (``AI-E11-1``) is discharged per guard**: each names its **observable**,
each moves the defect **at the real seam** (the shipped types and the committed artifact,
never a copy), and ``-46``/``-47`` **GENERATE** their adversarial variants *from the
committed record itself* rather than hand-writing a fixture.

**Non-vacuity is not optional here** (the ``-39`` argparse-internals precedent): every
guard that walks the record asserts it extracted **> 0** rows before asserting anything
about them. A guard that silently iterates an empty adjudication record passes forever,
and here that guard is the one protecting the externalization gate.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from argus.precision.adjudication import (
    ADJUDICATION_UNIT,
    DENOMINATOR_DISPOSITIONS,
    DISPOSITIONS,
    EXPERT_HOURS_CEILING,
    HUMAN_DISPOSITIONS,
    PROTOCOL_ADJUDICATOR_ROLES,
    AdjudicationRecord,
    AdjudicationRow,
    AdjudicationUnevaluable,
    Exhaustive,
    UnregisteredAdjudicator,
    UnregisteredDisposition,
    adjudicator_role,
    change_log_head_version,
    disposition_meaning,
    expert_hours_report,
    finding_row_id,
    fold_adjudicated_precision,
    load_record,
    validation_set_population_n,
)
from argus.precision.replay_harness import registry_module
from argus.store.canonical import dumps

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACTS = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_RECORD_PATH = _ARTIFACTS / "validation-corpus" / "adjudication-record.json"
_PROTOCOL_PATH = _ARTIFACTS / "precision-validation-protocol.md"

#: The named human protocol §2 designates, and `sprint-status.yaml:414`/`:416` record.
_ADJUDICATOR = "XAgent007 (Engineering Lead)"


def _record() -> AdjudicationRecord:
    assert _RECORD_PATH.is_file(), (
        f"the committed adjudication record is absent at "
        f"{_RECORD_PATH.relative_to(_REPO_ROOT).as_posix()}. Re-run: python "
        f"scripts/build_adjudication_record.py"
    )
    return load_record(_RECORD_PATH)


def _judged(row: AdjudicationRow, disposition: str, *, revision: int = 1) -> AdjudicationRow:
    """A HUMAN judgement over *row*'s finding — used only to exercise the instrument.

    Every row this helper produces lives inside a single test's local fixture and is never
    written to the committed record. What ``-39`` asserts against the artifact itself is
    the property that survives the adjudication: every judged row is attributed to a
    protocol §2 role, and every unjudged row carries no attribution at all.
    """
    return AdjudicationRow(
        row_id=finding_row_id(
            member_id=row.member_id,
            rule_id=row.rule_id,
            verdict_eligible=row.verdict_eligible,
            advisory=row.advisory,
            locator=row.locator,
            revision=revision,
        ),
        member_id=row.member_id,
        rule_id=row.rule_id,
        verdict_eligible=row.verdict_eligible,
        advisory=row.advisory,
        locator=row.locator,
        disposition=disposition,
        adjudicator=_ADJUDICATOR,
        adjudicated_on="2026-08-16",
        reason="synthetic fixture: exercises the instrument, adjudicates nothing real",
        supersedes=row.row_id,
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — the record exists, is committed, is machine-readable, and judges NOTHING
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_39_the_committed_record_exists_and_is_non_vacuous() -> None:
    """TC-ArgusAgent-PRECISION-001-39 — AC3/AC7: the record is committed, parsable and ATTRIBUTED.

    **Observable:** the row count parsed off the committed artifact, and the attribution
    on every live row. **Why the non-vacuity assertion comes first:** every other guard in
    this file walks these rows, and all of them would pass over an empty record.

    **RE-DERIVED 2026-08-17 (Story 13.3).** This guard used to assert
    ``TP == FP == BORDERLINE == 0`` and ``UNADJUDICATED == len(rows)``. Story 13.2 encoded
    *"nothing is adjudicated yet"* as a permanent invariant when it was a TRANSIENT state,
    so the guard went red the moment the named human did the work it was waiting for — and
    a guard that fails on the event it exists to enable is measuring the calendar, not the
    property. What it was ACTUALLY protecting is intact and is what it now asserts, in a
    form that cannot pass trivially: **a disposition may only enter the record attributed
    to a human role protocol §2 registers, and an unjudged row may carry no attribution at
    all.** That is the shape a machine filling in the human's judgements would break, in
    BOTH directions, and it stays able to fail whatever the tally becomes.
    """
    record = _record()
    assert len(record.rows) > 0, (
        "non-vacuity floor (AI-E11-1): the adjudication record is EMPTY, so every "
        "exhaustiveness and attribution guard below would pass without observing anything"
    )
    tally = record.counts()
    assert sum(tally.values()) == len(record.live_rows()) == len(record.rows)
    assert set(tally) == set(DISPOSITIONS), (
        "counts() must report EVERY registered vocabulary member, so a consumer reading a "
        "member cannot get a KeyError that reads like a zero"
    )

    # AC7 / DN-6, asserted against the artifact rather than trusted. A HUMAN disposition
    # carries a §2-registered adjudicator and a date; an UNADJUDICATED row carries
    # NEITHER. Both halves can fail, and the second is the one that catches an agent
    # writing judgements: `AdjudicationRow.__post_init__` refuses an attributed
    # UNADJUDICATED row, and this asserts the committed artifact against that rule rather
    # than trusting that it was constructed through the type.
    judged = [row for row in record.rows if row.is_human_judgement]
    unjudged = [row for row in record.rows if not row.is_human_judgement]
    assert len(judged) + len(unjudged) == len(record.rows)
    assert judged or unjudged, "non-vacuity: the record partitioned into nothing"
    for row in judged:
        assert row.adjudicator is not None and row.adjudicated_on is not None, (
            f"row {row.row_id!r} carries the human disposition {row.disposition!r} with "
            f"no adjudicator or no date. An unattributed judgement is exactly what an "
            f"agent filling in the human's work would leave behind (protocol §2)."
        )
        assert adjudicator_role(row.adjudicator) in PROTOCOL_ADJUDICATOR_ROLES, (
            f"row {row.row_id!r} is attributed to {row.adjudicator!r}, whose role protocol "
            f"§2 does not register. Only §2's roles adjudicate."
        )
    for row in unjudged:
        assert row.disposition == "UNADJUDICATED", row.disposition
        assert row.adjudicator is None and row.adjudicated_on is None, (
            f"row {row.row_id!r} is UNADJUDICATED yet carries an attribution — that is "
            f"the exact shape a machine filling in the human's judgements would produce"
        )
    # The tally is DERIVED from the same partition rather than pinned, so this cannot
    # silently drift out of agreement with the rows it just walked.
    assert sum(tally[name] for name in HUMAN_DISPOSITIONS) == len(judged)
    assert tally["UNADJUDICATED"] == len(unjudged)


def test_TC_ArgusAgent_PRECISION_001_40_the_record_is_tracked_in_git_and_not_under_dot_argus() -> None:
    """TC-ArgusAgent-PRECISION-001-40 — AC3: gate evidence that is not in git is not evidence.

    **Observable:** ``git ls-files`` over the record path, and the path itself. **The
    defect this closes before it happens:** the obvious reuse — the 6.7
    ``DecisionRecordWriter`` — writes under ``.argus/``, which ``.gitignore`` ignores, so
    an adjudication record filed there would be invisible to every reviewer and absent
    from every clone (DN-3).
    """
    relative = _RECORD_PATH.relative_to(_REPO_ROOT).as_posix()
    assert not relative.startswith(".argus/"), (
        f"the record is under .argus/, which .gitignore ignores — {relative}"
    )
    tracked = subprocess.run(
        ["git", "ls-files", "--", relative],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.split()
    assert tracked, (
        f"{relative} is NOT tracked by git. The adjudication record is the evidence the "
        f"externalization gate rests on; evidence outside git is not evidence (DN-3)."
    )
    gitignore = (_REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".argus/" in gitignore, (
        "the premise of this guard is that .argus/ IS ignored; if that stopped being "
        "true the guard must be re-derived rather than left asserting a dead reason"
    )


def test_TC_ArgusAgent_PRECISION_001_41_the_disposition_vocabulary_is_closed_and_raises() -> None:
    """TC-ArgusAgent-PRECISION-001-41 — AC3: an unregistered disposition RAISES (the DF-10-4-E shape).

    **Observable:** :func:`disposition_meaning` and ``AdjudicationRow.__post_init__``.
    Checked in BOTH directions: an unregistered member raises, and every registered member
    is exercised — a vocabulary entry nobody constructs is an entry nobody guards.
    ``BORDERLINE`` is asserted present by name: §4's ladder makes *"looked at, could not
    decide"* a first-class outcome, and a vocabulary without it forces a human who cannot
    decide to record a decision.
    """
    with pytest.raises(UnregisteredDisposition, match="not a registered member"):
        disposition_meaning("PROBABLY_FINE")
    assert "BORDERLINE" in DISPOSITIONS, (
        "§4's borderline ladder is a first-class outcome, not an absence"
    )
    assert set(DENOMINATOR_DISPOSITIONS) == {"TP", "FP"}, (
        "BORDERLINE and UNADJUDICATED must enter NEITHER side of the ratio, or the "
        "denominator could be moved by the act of not deciding"
    )
    assert set(HUMAN_DISPOSITIONS) == set(DISPOSITIONS) - {"UNADJUDICATED"}

    seed = _record().rows[0]
    exercised = 0
    for name in sorted(DISPOSITIONS):
        assert disposition_meaning(name)
        if name in HUMAN_DISPOSITIONS:
            assert _judged(seed, name).disposition == name
        exercised += 1
    assert exercised == len(DISPOSITIONS) >= 4, (
        f"non-vacuity: {exercised} vocabulary member(s) exercised"
    )
    with pytest.raises(UnregisteredDisposition):
        AdjudicationRow(
            row_id="x.0",
            member_id="m",
            rule_id="vacuous_test_ast",
            verdict_eligible=True,
            advisory=True,
            locator="a/b.py:1",
            disposition="LOOKS_OK",
        )


def test_TC_ArgusAgent_PRECISION_001_42_every_disposition_is_attributed_to_a_protocol_role() -> None:
    """TC-ArgusAgent-PRECISION-001-42 — AC3/§2: attribution is ASSERTED, not assumed.

    **Observable:** :func:`adjudicator_role`, and the registered role tuple cross-checked
    against protocol §2's own table **in both directions**, so the code and the document
    cannot drift apart. **The converse is the load-bearing half:** an ``UNADJUDICATED``
    row carrying an adjudicator RAISES — a machine that started signing the named human's
    name fails at construction, not at review.
    """
    protocol = _PROTOCOL_PATH.read_text(encoding="utf-8")
    for role in PROTOCOL_ADJUDICATOR_ROLES:
        assert f"**{role}**" in protocol, (
            f"role {role!r} is registered in argus/precision/adjudication.py but "
            f"precision-validation-protocol.md §2 does not name it"
        )
    documented = set(
        re.findall(r"\| \*\*(Engineering Lead|QA Lead|External adjudicator)\*\*", protocol)
    )
    assert documented == set(PROTOCOL_ADJUDICATOR_ROLES), (
        f"§2's role table names {sorted(documented)} while the code registers "
        f"{sorted(PROTOCOL_ADJUDICATOR_ROLES)} — the two have drifted"
    )
    assert "XAgent007" in protocol, (
        "§2 must name the HOLDER of the primary adjudicating role; a role with no named "
        "holder cannot make an attributable judgement (AI-E9-8)"
    )

    assert adjudicator_role(_ADJUDICATOR) == "Engineering Lead"
    for bad in ("XAgent007", "XAgent007 (Intern)", "", "(Engineering Lead)"):
        with pytest.raises(UnregisteredAdjudicator):
            adjudicator_role(bad)

    seed = _record().rows[0]
    with pytest.raises(UnregisteredAdjudicator):
        AdjudicationRow(
            row_id="x.0",
            member_id=seed.member_id,
            rule_id=seed.rule_id,
            verdict_eligible=True,
            advisory=True,
            locator=seed.locator,
            disposition="TP",
            adjudicator="some-agent (Automated Reviewer)",
            adjudicated_on="2026-08-16",
            reason="an agent adjudicated",
        )
    with pytest.raises(ValueError, match="must carry no adjudicator"):
        AdjudicationRow(
            row_id="x.0",
            member_id=seed.member_id,
            rule_id=seed.rule_id,
            verdict_eligible=True,
            advisory=True,
            locator=seed.locator,
            disposition="UNADJUDICATED",
            adjudicator=_ADJUDICATOR,
        )
    with pytest.raises(ValueError, match="requires a REASON"):
        AdjudicationRow(
            row_id="x.0",
            member_id=seed.member_id,
            rule_id=seed.rule_id,
            verdict_eligible=True,
            advisory=True,
            locator=seed.locator,
            disposition="TP",
            adjudicator=_ADJUDICATOR,
            adjudicated_on="2026-08-16",
        )


def test_TC_ArgusAgent_PRECISION_001_43_a_correction_supersedes_and_never_rewrites() -> None:
    """TC-ArgusAgent-PRECISION-001-43 — AC3/§3.4: append-only, supersede-never-erase, mechanised.

    **Observable:** what :class:`AdjudicationRecord` will and will not accept.
    **Adversarial variants GENERATED from the committed record's own first row** rather
    than a hand-written fixture: a second live judgement for one finding, a correction
    naming a row that does not exist, and a correction pointing at a DIFFERENT finding.
    The superseded row must still be **present** afterwards — struck, not erased.
    """
    record = _record()
    assert len(record.rows) > 0, "non-vacuity: nothing to generate a variant from"
    first = record.rows[0]

    corrected = record.append([_judged(first, "TP")])
    assert len(corrected.rows) == len(record.rows) + 1
    assert any(row.row_id == first.row_id for row in corrected.rows), (
        "the superseded row must remain IN the record — §3.4 is strike, never erase"
    )
    assert first.row_id in corrected.superseded_row_ids
    live = corrected.live_dispositions()[first.finding_id]
    assert live.disposition == "TP" and live.supersedes == first.row_id

    twice = corrected.append([_judged(live, "FP", revision=2)])
    assert twice.live_dispositions()[first.finding_id].disposition == "FP", (
        "a second correction supersedes the first CORRECTION, not the original"
    )
    assert len(twice.live_rows()) == len(record.rows), (
        "a chain of corrections must still leave exactly one live row per finding"
    )
    # And a second correction that re-supersedes the ORIGINAL leaves two live rows —
    # which is a rewrite of history dressed as a correction, and is refused.
    with pytest.raises(ValueError, match="TWO live rows"):
        corrected.append([_judged(first, "FP", revision=2)])

    # (a) a second row for one finding that does NOT supersede — a rewrite in disguise.
    with pytest.raises(ValueError, match="TWO live rows"):
        record.append(
            [
                AdjudicationRow(
                    row_id="rewrite.9",
                    member_id=first.member_id,
                    rule_id=first.rule_id,
                    verdict_eligible=first.verdict_eligible,
                    advisory=first.advisory,
                    locator=first.locator,
                    disposition="TP",
                    adjudicator=_ADJUDICATOR,
                    adjudicated_on="2026-08-16",
                    reason="a second opinion sitting beside the first",
                )
            ]
        )
    # (b) a correction naming a row the record does not contain.
    with pytest.raises(ValueError, match="which is not in"):
        record.append(
            [
                AdjudicationRow(
                    row_id="orphan.1",
                    member_id=first.member_id,
                    rule_id=first.rule_id,
                    verdict_eligible=first.verdict_eligible,
                    advisory=first.advisory,
                    locator=first.locator,
                    disposition="TP",
                    adjudicator=_ADJUDICATOR,
                    adjudicated_on="2026-08-16",
                    reason="supersedes a row nobody wrote",
                    supersedes="deadbeefcafe.0",
                )
            ]
        )
    # (c) a correction pointing at a DIFFERENT finding.
    other = next(r for r in record.rows if r.finding_id != first.finding_id)
    with pytest.raises(ValueError, match="DIFFERENT finding"):
        record.append(
            [
                AdjudicationRow(
                    row_id="crossed.1",
                    member_id=first.member_id,
                    rule_id=first.rule_id,
                    verdict_eligible=first.verdict_eligible,
                    advisory=first.advisory,
                    locator=first.locator,
                    disposition="TP",
                    adjudicator=_ADJUDICATOR,
                    adjudicated_on="2026-08-16",
                    reason="corrects the wrong finding",
                    supersedes=other.row_id,
                )
            ]
        )


def test_TC_ArgusAgent_PRECISION_001_44_the_row_schema_is_closed_and_nfr_s1_holds() -> None:
    """TC-ArgusAgent-PRECISION-001-44 — AC3/NFR-S1: rule-id provenance, locators and counts ONLY.

    **Observable:** the closed row schema in both directions, the locator shape, and the
    committed artifact's bytes. **Why the schema IS the NFR-S1 enforcement:** there is no
    free field a source byte could enter except the human's ``reason``, so the containment
    is structural rather than a scan that must guess what a secret looks like. The locator
    rules also close the cross-platform hole this repository has shipped before — an
    absolute or backslash-separated locator is a Windows-only artifact, and the local
    gates here are Windows-only while CI runs an ubuntu matrix.
    """
    record = _record()
    assert len(record.rows) > 0
    with pytest.raises(ValueError, match="schema violation"):
        AdjudicationRow.from_payload({**record.rows[0].to_payload(), "note": "extra"})
    with pytest.raises(ValueError, match="schema violation"):
        payload = record.rows[0].to_payload()
        payload.pop("disposition")
        AdjudicationRow.from_payload(payload)

    seed = record.rows[0]
    generated = 0
    for bad_locator in (
        "D:/repo/tests/a.py:1",
        "/etc/passwd:1",
        r"tests\a.py:1",
        "tests/../../secret.py:1",
        "tests/a.py",
    ):
        generated += 1
        with pytest.raises(ValueError, match="locator"):
            AdjudicationRow(
                row_id="x.0",
                member_id=seed.member_id,
                rule_id=seed.rule_id,
                verdict_eligible=True,
                advisory=True,
                locator=bad_locator,
                disposition="UNADJUDICATED",
            )
    assert generated == 5, f"non-vacuity: {generated} adversarial locator(s)"
    with pytest.raises(ValueError, match="not an identifier"):
        AdjudicationRow(
            row_id="x.0",
            member_id=seed.member_id,
            rule_id="api_key = 'AKIA...'",
            verdict_eligible=True,
            advisory=True,
            locator=seed.locator,
            disposition="UNADJUDICATED",
        )

    blob = _RECORD_PATH.read_text(encoding="utf-8")
    assert not re.search(r"[A-Za-z]:[/\\]", blob), (
        "the committed record carries a drive-lettered host path (NFR-S1)"
    )
    assert "\\\\" not in blob, "the committed record carries a backslash-separated path"
    for row in record.rows:
        assert row.rule_id.isidentifier()
        assert re.match(r"^[A-Za-z0-9._@+#$/-]+:\d+$", row.locator)


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — the protocol is amended BEFORE the run, and the ordering is mechanical
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_45_the_record_names_the_protocol_head_it_was_adjudicated_under() -> None:
    """TC-ArgusAgent-PRECISION-001-45 — AC2: a record adjudicated under a SUPERSEDED protocol fails.

    **Observable:** ``record.protocol_version`` against the change log's current head.
    **The defect it makes impossible:** amending the protocol *after* dispositions were
    recorded — i.e. reinterpreting a run rather than governing it. *"The protocol is
    amended BEFORE the run, never reinterpreted during it"* becomes an assertion instead
    of an instruction nobody can check. **Moved at the real seam:** the parser is driven
    over a copy of the real document with a NEW change-log row prepended, and the guard's
    own predicate must go red.
    """
    protocol = _PROTOCOL_PATH.read_text(encoding="utf-8")
    head = change_log_head_version(protocol)
    record = _record()
    assert record.protocol_version == head, (
        f"the adjudication record was recorded under protocol {record.protocol_version!r} "
        f"while the change log's head is {head!r}. Either the record predates an "
        f"amendment (re-run scripts/build_adjudication_record.py and RE-ADJUDICATE), or "
        f"the protocol was amended to reinterpret a run that already happened."
    )
    # RED, generated from the real document: a new head must invalidate this record.
    amended = protocol.replace(
        f"| 2026-08-16 | {head} |",
        "| 2026-08-17 | V9.9 | a later amendment | Someone |\n| 2026-08-16 | " + head + " |",
        1,
    )
    assert change_log_head_version(amended) == "V9.9", (
        "the parser did not follow the change log's head — the guard would be pinned to "
        "whatever version it first saw"
    )
    assert record.protocol_version != change_log_head_version(amended), (
        "with a later head in place the committed record MUST no longer match; a guard "
        "that stayed green through an amendment is the vacuous shape this closes"
    )
    for broken, why in (
        ("# no change log here", "no '## Change log' section"),
        ("## Change log\n\n| Date | Version |\n|---|---|\n", "no data rows"),
    ):
        with pytest.raises(ValueError):
            change_log_head_version(broken)


def test_TC_ArgusAgent_PRECISION_001_46_the_unit_is_the_finding_not_the_rule_class() -> None:
    """TC-ArgusAgent-PRECISION-001-46 — AC2/§7: precision is over FINDINGS, and the record proves it.

    **Observable:** the count of distinct ``finding_id``s versus the count of distinct
    ``match_key``s over the committed record. **The defect being closed:** §7 locks
    *"precision measured over FINDINGS, not repos"* while ``compute_precision`` counts
    distinct ``(rule_id, verdict_eligible, advisory)`` CLASSES. On this corpus the two
    quantities are 31 and 1 — a per-class fold would compute the externalization gate over
    a denominator of one. The 6.6 match key is nonetheless REUSED unchanged
    (DN-MATCH-KEY-REUSE): it is derivable from every row and no second identity exists.
    """
    record = _record()
    findings = {row.finding_id for row in record.rows}
    classes = {row.match_key for row in record.rows}
    assert len(findings) == len(record.rows) > 0, (
        "every row must be a DISTINCT finding; a collision means two findings were "
        "collapsed into one adjudication"
    )
    assert len(findings) > len(classes), (
        f"the record holds {len(findings)} finding(s) across {len(classes)} class(es). If "
        f"these were equal this guard could not distinguish the two quantities and would "
        f"prove nothing about the unit."
    )
    assert record.adjudication_unit == ADJUDICATION_UNIT == "finding"
    for row in record.rows:
        assert row.match_key == (row.rule_id, row.verdict_eligible, row.advisory), (
            "the 6.6 match key must stay derivable from every row — no second, divergent "
            "identity (DN-MATCH-KEY-REUSE)"
        )
    with pytest.raises(ValueError, match="Protocol §7"):
        AdjudicationRecord(
            protocol_version=record.protocol_version,
            adjudication_unit="class",
            corpus_source=record.corpus_source,
            reproducibility_verified=True,
            reproducibility_source="x",
            expert_hours=None,
            expert_hours_note="x",
            rows=record.rows[:1],
        )
    protocol = _PROTOCOL_PATH.read_text(encoding="utf-8")
    assert "**Precision is measured over FINDINGS, not repos**" in protocol, (
        "§7's invariant must still be present and unsoftened — the amendment upholds it"
    )
    assert "the unit is the FINDING" in protocol, (
        "AC2 requires the decision to be WRITTEN DOWN in the protocol before the run"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — exhaustiveness is proven, not asserted; AC6 — determinism comes first
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_47_exhaustiveness_is_proven_and_a_residual_is_unevaluable() -> None:
    """TC-ArgusAgent-PRECISION-001-47 — AC4: every emitted finding, one live disposition, or UNEVALUABLE.

    **Observable:** :meth:`AdjudicationRecord.exhaustiveness`. **Adversarial variant
    GENERATED from the committed record itself** (never hand-written), in both directions:
    every row is judged so the population is genuinely exhaustive, then **exactly one**
    disposition is removed and the result must become ``Unevaluable`` **with residual 1** —
    not a pass over the 30 that remain. A pass over the adjudicated subset is precisely
    the sampled measurement §4 forbids, and downstream it is indistinguishable from an
    honest one.
    """
    record = _record()
    expected = [row.finding_id for row in record.rows]
    assert len(expected) > 1, "non-vacuity: need >1 finding to remove exactly one"

    fully = record.append([_judged(row, "TP") for row in record.rows])
    verdict = fully.exhaustiveness(expected)
    assert isinstance(verdict, Exhaustive), verdict
    assert verdict.adjudicated_count == len(expected)

    # EXACTLY ONE finding the corpus emitted, carrying no row at all. Generated by
    # dropping that finding's rows while leaving it in the expected population — which is
    # the real seam now that every committed row carries a human disposition: a residual
    # is a finding NOBODY ENTERED, and it can only be observed when the expected
    # population comes from somewhere other than the record itself.
    partial = replace(
        record,
        rows=record.rows[1:] + tuple(_judged(row, "TP") for row in record.rows[1:]),
    )
    residual = partial.exhaustiveness(expected)
    assert isinstance(residual, AdjudicationUnevaluable), (
        "one undisposed finding must make the run UNEVALUABLE, never a pass over the rest"
    )
    assert residual.residual_count == 1
    assert residual.adjudicated_count == len(expected) - 1
    assert residual.residual_finding_ids == (record.rows[0].finding_id,)
    assert "what would close the gap" in str(residual).lower() or (
        "What would close the gap" in residual.reason
    )

    # BORDERLINE is a first-class OUTCOME and still a residual: the ladder has not
    # terminated, so the corpus is not exhaustively adjudicated.
    undecided = record.append(
        [_judged(record.rows[0], "BORDERLINE")]
        + [_judged(row, "TP") for row in record.rows[1:]]
    )
    borderline = undecided.exhaustiveness(expected)
    assert isinstance(borderline, AdjudicationUnevaluable)
    assert borderline.residual_count == 1

    # THE LIVE COMMITTED RECORD, re-derived 2026-08-17 (Story 13.3). This used to assert
    # `residual == len(expected)` and `adjudicated == 0` — true while the record held 31
    # UNADJUDICATED rows and false the moment the named human judged them. The PROPERTY
    # being protected is not the count: it is that `exhaustiveness` and the disposition
    # vocabulary agree about what a residual IS. Both sides are computed here
    # independently and compared, so the guard tracks the record instead of a date, and it
    # still fails if BORDERLINE ever stops making a run non-exhaustive.
    live_residual = sorted(
        finding_id
        for finding_id, row in record.live_dispositions().items()
        if row.disposition not in DENOMINATOR_DISPOSITIONS
    )
    live = record.exhaustiveness(expected)
    if live_residual:
        assert isinstance(live, AdjudicationUnevaluable), (
            f"{len(live_residual)} committed finding(s) carry no live TP/FP disposition "
            f"and the record still reports EXHAUSTIVE. A pass over the adjudicated subset "
            f"is the sampled measurement §4 forbids."
        )
        assert live.residual_count == len(live_residual)
        assert live.adjudicated_count == len(expected) - len(live_residual)
        assert sorted(live.residual_finding_ids) == live_residual
    else:
        assert isinstance(live, Exhaustive)
        assert live.adjudicated_count == len(expected)


def test_TC_ArgusAgent_PRECISION_001_48_an_empty_population_is_unevaluable_not_exhaustive() -> None:
    """TC-ArgusAgent-PRECISION-001-48 — AC4: the non-vacuity floor is IN the guard, not beside it.

    **Observable:** what ``exhaustiveness(())`` returns. A naive implementation returns
    "exhaustive" for an empty population — vacuously true and permanently green — and here
    that green would be the one protecting the externalization gate. It must be
    ``Unevaluable`` instead, because an empty population means the corpus could not be
    read, not that everything in it was judged.
    """
    record = _record()
    empty = record.exhaustiveness(())
    assert isinstance(empty, AdjudicationUnevaluable), (
        "an EMPTY emitted-finding population must be Unevaluable; 'exhaustive over "
        "nothing' is the guard that passes forever"
    )
    assert empty.residual_count == 0 and empty.adjudicated_count == 0
    assert "non-vacuity" in empty.reason


def test_TC_ArgusAgent_PRECISION_001_49_determinism_is_proven_before_any_disposition_counts() -> None:
    """TC-ArgusAgent-PRECISION-001-49 — AC6/§4: a non-reproducible run makes the adjudication INVALID.

    **Observable:** :meth:`AdjudicationRecord.determinism_precondition` and the fold's
    ordering. **The EXISTING check is reused, not re-authored**: byte-reproducibility is
    measured by ``scripts/audit_validation_corpus.py`` (13.1) and carried per member on the
    adjudication set; the record only records its result. **Moved at the real seam:** a
    record with ``reproducibility_verified=False`` and a FULL set of judgements must still
    refuse to produce a ratio — proving the precondition is evaluated before the
    arithmetic, not beside it.
    """
    record = _record()
    assert record.determinism_precondition() is None, (
        f"the committed record reports a non-reproducible corpus: "
        f"{record.reproducibility_source}"
    )
    assert "audit_validation_corpus.py" in record.reproducibility_source, (
        "AC6 requires the EXISTING check to be reused and NAMED on the record; a "
        "reproducibility claim that cites no instrument is a claim about nothing"
    )

    judged_rows = [_judged(row, "TP") for row in record.rows]
    non_repro = AdjudicationRecord(
        protocol_version=record.protocol_version,
        adjudication_unit=record.adjudication_unit,
        corpus_source=record.corpus_source,
        reproducibility_verified=False,
        reproducibility_source="synthetic: one member diverged between two runs",
        expert_hours=Fraction(3, 2),
        expert_hours_note="synthetic",
        rows=record.rows + tuple(judged_rows),
    )
    invalid = non_repro.determinism_precondition()
    assert isinstance(invalid, AdjudicationUnevaluable)
    folded = fold_adjudicated_precision(
        non_repro,
        expected_finding_ids=[row.finding_id for row in record.rows],
        population_n=validation_set_population_n(),
        floor_n=registry_module().VALIDATION_SET_FLOOR_N,
        protocol_cleared=True,
    )
    assert folded.total_tp == len(record.rows) > 0, (
        "the fixture must genuinely carry a full set of TP judgements, or the refusal "
        "below could be caused by the absence of dispositions rather than by determinism"
    )
    assert folded.precision is None and folded.evaluable is False, (
        "a full sweep of TP judgements over a NON-REPRODUCIBLE corpus must still produce "
        "NO number — §4: the determinism check runs before any pass/fail is recorded"
    )
    assert folded.provisional is True
    assert folded.gate_status.startswith("unevaluable")


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — expert-hours are RECORDED against §3's ceiling, never enforced by it
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_50_the_expert_hours_ceiling_is_single_sourced() -> None:
    """TC-ArgusAgent-PRECISION-001-50 — AC5/AI-E9-7: the ≤4h ceiling in code equals §3's own text.

    **Observable:** :data:`EXPERT_HOURS_CEILING` cross-checked against protocol §3. Never
    publish a prose copy of a pinned constant — so where a constant must exist in both a
    document and the code, the two are compared by a guard rather than trusted to agree.
    """
    protocol = _PROTOCOL_PATH.read_text(encoding="utf-8")
    stated = re.search(
        r"Per gate-flip adjudication run \(the full corpus at N≥5\):\*\* ≤ \*\*(\d+) expert-hours",
        protocol,
    )
    assert stated is not None, (
        "protocol §3's gate-flip budget line could not be located — the cross-check would "
        "be vacuous, which is worse than a mismatch because it never fires"
    )
    assert EXPERT_HOURS_CEILING == Fraction(int(stated.group(1)), 1), (
        f"the code's ceiling {EXPERT_HOURS_CEILING} != §3's stated {stated.group(1)}h"
    )
    assert isinstance(EXPERT_HOURS_CEILING, Fraction), "AR4: no float, ever"


def test_TC_ArgusAgent_PRECISION_001_51_an_overrun_is_reported_and_never_fails() -> None:
    """TC-ArgusAgent-PRECISION-001-51 — AC5: exceeding §3's ceiling is a REPORT, not a gate.

    **Observable:** :func:`expert_hours_report` across the whole boundary — under, exactly
    at, over, and NOT RECORDED. §3 states the budget is *"a ceiling, not a target"* and an
    overrun *"a signal the cartridge is ambiguous"*, so a guard that failed on an overrun
    would create pressure to trim the adjudication to fit the estimate — trading the
    measurement this project's externalization claim rests on for a number.
    """
    assert "NOT RECORDED" in expert_hours_report(None), (
        "a null must read as NOT RECORDED, never as zero hours — a zero claims the work "
        "took no time rather than that it has not happened"
    )
    assert "within" in expert_hours_report(Fraction(7, 2))
    assert "within" in expert_hours_report(EXPERT_HOURS_CEILING), (
        "exactly AT the ceiling is within it (≤, not <)"
    )
    over = expert_hours_report(EXPERT_HOURS_CEILING + Fraction(1, 2))
    assert "EXCEEDS" in over and "RECORDED, NOT FAILED" in over
    assert "trimming the adjudication" in over.lower()
    # The record accepts an overrun; nothing about it raises.
    record = _record()
    overrun = AdjudicationRecord(
        protocol_version=record.protocol_version,
        adjudication_unit=record.adjudication_unit,
        corpus_source=record.corpus_source,
        reproducibility_verified=True,
        reproducibility_source=record.reproducibility_source,
        expert_hours=EXPERT_HOURS_CEILING * 3,
        expert_hours_note="synthetic overrun",
        rows=record.rows,
    )
    assert "EXCEEDS" in expert_hours_report(overrun.expert_hours)
    assert record.expert_hours is None, (
        "the COMMITTED record must report NOT RECORDED: no adjudication run has happened, "
        "and a number here would be an invented measurement"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC7 / OI1 — the live state, asserted rather than described
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_52_the_live_fold_is_unevaluable_and_the_gate_is_not_flipped() -> None:
    """TC-ArgusAgent-PRECISION-001-52 — AC7/DN-5/OI1: the real corpus reports UNEVALUABLE, recorded.

    **Observable:** the fold over the COMMITTED record with the live derived N. The claim
    this guard protects is the one that must never weaken: **a caller that ASSERTS
    ``protocol_cleared=True`` cannot flip the gate over a record protocol §4's
    preconditions do not admit.** That is the whole reason ``protocol_cleared`` is passed
    by the caller rather than derived inside the harness, and it is why the flag is
    threaded into this fixture.

    **RE-DERIVED 2026-08-17 (Story 13.3).** It used to assert
    ``total_unadjudicated == residual_count == len(record.rows)`` — the state on the day
    13.2 landed, encoded as though it were an invariant. The named human then adjudicated,
    ``total_unadjudicated`` went to 0, and the guard failed on the event it existed to
    wait for. The residual is now DERIVED from the record's own live dispositions and the
    refusal is asserted against that, so the guard keeps its teeth as the adjudication
    moves and goes red if the fold ever reports a ratio over a subset.
    """
    record = _record()
    folded = fold_adjudicated_precision(
        record,
        expected_finding_ids=[row.finding_id for row in record.rows],
        population_n=validation_set_population_n(),
        floor_n=registry_module().VALIDATION_SET_FLOOR_N,
        protocol_cleared=True,  # even CLAIMED cleared, a non-exhaustive corpus cannot flip
    )
    assert folded.n == validation_set_population_n() >= 5, (
        "the repository corpus floor is met — which is exactly why the remaining three §5 "
        "conditions must not be satisfiable by default"
    )
    residual = [
        finding_id
        for finding_id, row in record.live_dispositions().items()
        if row.disposition not in DENOMINATOR_DISPOSITIONS
    ]
    assert len(record.rows) > 0, "non-vacuity: the committed record is EMPTY"
    assert residual, (
        "every committed finding now carries a live TP/FP disposition. This guard's "
        "subject — the refusal to report a ratio over an incompletely adjudicated corpus "
        "— is no longer observable on the live record. RE-DERIVE it (drive the refusal "
        "over a generated variant) rather than deleting it: a guard that passes because "
        "its subject vanished is worse than the red it replaced."
    )
    assert folded.evaluable is False
    assert folded.precision is None and folded.precision_ratio == "NOT COMPUTED BY THIS RUN"
    assert folded.meets_threshold is False
    assert folded.provisional is True, (
        "an incompletely adjudicated corpus must never report a cleared gate, even when "
        "the caller claims protocol_cleared=True"
    )
    assert isinstance(folded.exhaustiveness, AdjudicationUnevaluable)
    assert folded.exhaustiveness.residual_count == len(residual)
    assert folded.exhaustiveness.adjudicated_count == len(record.rows) - len(residual)
    assert folded.total_tp + folded.total_fp == folded.exhaustiveness.adjudicated_count, (
        "the findings that carry a live TP/FP disposition and the findings the fold "
        "counted into the denominator must be the same set, or the two halves of the "
        "measurement are describing different populations"
    )
    assert folded.clean_repo_fp_applicable is False
    assert "NOT APPLICABLE" in folded.clean_repo_fp_note
    assert "NOT RECORDED" in folded.expert_hours_report, (
        "expert_hours is null and stays null until the adjudicator states a figure; a "
        "zero would claim the work took no time rather than that it was not reported"
    )
    assert folded.gate_status.startswith("unevaluable")


# ─────────────────────────────────────────────────────────────────────────────────────
# Story 13.5 / AC3 + AC7 — the 13.1–13.3 rows are BYTE-UNCHANGED, verified by execution
# ─────────────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_71_the_prior_rows_survive_an_append_byte_for_byte() -> None:
    """TC-ArgusAgent-PRECISION-001-71 — Story 13.5 / AC3: append-only, PROVED not intended.

    **Observable:** the canonical bytes of the committed record's rows, extracted before and
    after a real :meth:`AdjudicationRecord.append`, compared as bytes.

    §3.4 evidence immutability says a correction SUPERSEDES and never erases. *"A diff of the
    file is not sufficient — it cannot distinguish a reordering from an edit"*, so this
    compares the canonical serialization of each row OBJECT, keyed by ``row_id``, which is
    invariant under reordering and sensitive to a single character.

    **Why this is the guard Story 13.5 needed.** 13.5 re-measured the same five members at
    the same pins through a corrected detector and a corrected instrument, and the corrected
    run promoted NOTHING — so there was no new finding to adjudicate and no superseding row
    to write. That is a measured fact, not a decision, and it makes the append-only property
    easy to satisfy by doing nothing. A guard that only asserted *"the rows are still there"*
    would be green for the wrong reason forever. This one drives a real append at the real
    seam and proves the prior rows come through it untouched.

    **The adversarial variant is GENERATED**: one byte of one committed row is perturbed and
    the comparison is proved to go RED. Without it, "the bytes match" is a claim about a
    comparison nobody has seen fail.
    """
    record = _record()
    assert len(record.rows) > 0, "non-vacuity: the committed record holds ZERO rows"

    def _canonical(rows: tuple[AdjudicationRow, ...]) -> dict[str, bytes]:
        return {
            row.row_id: dumps(row.to_payload()).encode("utf-8") for row in rows
        }

    before = _canonical(record.rows)
    original_ids = frozenset(before)
    assert len(before) == len(record.rows), "row ids are not unique — the key is not a key"

    # A REAL append through the shipped instrument, of a REAL superseding judgement shape.
    # It is never written to disk: the record on disk is the evidence, and this fixture
    # exists to prove the evidence survives the operation, not to perform it.
    appended = record.append([_judged(record.rows[0], "TP", revision=7)])
    assert len(appended.rows) == len(record.rows) + 1, "the append did not append"

    after = _canonical(tuple(row for row in appended.rows if row.row_id in original_ids))
    assert set(after) == original_ids, (
        f"row ids vanished across the append: {sorted(original_ids - set(after))}. "
        "Append-only means the prior rows are still THERE, under the same identity."
    )
    for row_id in sorted(original_ids):
        assert after[row_id] == before[row_id], (
            f"row {row_id!r} changed across an append. §3.4: a correction supersedes, it "
            f"never erases, and it never rewrites the row it supersedes."
        )

    # The disposition tally of the ORIGINAL rows is unchanged too — a row can keep its bytes
    # and still be re-read if the fold started counting superseded rows.
    live_before = {row.row_id for row in record.live_rows()}
    assert live_before, "non-vacuity: the committed record has no live rows"

    # ── the GENERATED adversarial variant: ONE byte, and the comparison must go RED ────
    victim = record.rows[0]
    perturbed = replace(victim, locator=victim.locator[:-1] + ("9" if not victim.locator.endswith("9") else "8"))
    tampered = _canonical((perturbed,))
    assert tampered[perturbed.row_id] != before.get(victim.row_id, b""), (
        "a one-character change to a committed row produced identical canonical bytes. The "
        "comparison above would then be blind to an edit, which is the only thing it is for."
    )
