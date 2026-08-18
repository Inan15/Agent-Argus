"""Story 13.3 — the ONE place protocol §5's four conditions become a recorded decision.

Verification area ``TC-ArgusAgent-PRECISION-001-53``.. (``tests/test_gate_decision.py``).
Drivers: `precision-validation-protocol.md` §4 (the two preconditions and the borderline
ladder) and §5 (the four pass/fail conditions); the PRD's ≥80%-precision attested-
externalization gate; **AR4** (exact ``Fraction``, never a float); **AR7** (one
arithmetic, never forked); **NFR-S1** (rule-id provenance, locators and counts only);
**NFR-M1** (≤1200-line modules); **DF-9-2-A** (no module-level repository-only path).

What this module is
-------------------
13.1 decided what the validation set is and built it. 13.2 built the adjudication
instrument and recorded the emitted blocking findings. **This module computes the four §5
conditions over the committed, human-adjudicated record and lets the arithmetic decide.**
It does not adjudicate, it does not tune, and it authors no second threshold: the ratio,
the threshold, the provisional predicate and the status sentence are all
:mod:`argus.precision.replay_harness`'s objects, reached through
:func:`~argus.precision.adjudication.fold_adjudicated_precision`, which is called and
never re-implemented.

THREE terminal states, never two (DN-1)
---------------------------------------
:data:`GATE_OUTCOMES` is a CLOSED vocabulary that RAISES on an unregistered member (the
``DF-10-4-E`` exhaustive-dispatch shape 12.5 / 12.8 / 13.2 already use), and the third
member is the point of the whole module:

* ``CLEARED`` — all four §5 conditions hold over an exhaustively adjudicated,
  byte-reproducible record.
* ``NOT_CLEARED`` — the measurement **RAN** (reproducible **and** exhaustive **and**
  non-empty denominator) and at least one §5 condition FAILED. **This is a result.**
* ``BLOCKED`` — the record is not exhaustively adjudicated, or not reproducible, or the
  denominator is empty. **Not a §5 outcome at all.** The decision HALTS and the residual
  plus the closure path are recorded.

*A gate that did not clear because findings were judged and enough of them were false is a
MEASUREMENT. A gate that did not clear because the judgement has not terminated is an
ABSENCE.* One boolean cannot tell a reader which happened, and every downstream surface
would inherit the ambiguity — so ``BLOCKED`` is never rendered, serialized or summarised
as *"the gate did not clear"*, in any artifact, in any wording.

Non-vacuity is a floor, not a nicety — and Story 13.5 NARROWED it, never removed it
-----------------------------------------------------------------------------------
:func:`decide_gate` RAISES :class:`VacuousDecisionError` before it asserts anything when
the record holds zero rows (the ``-39`` argparse-internals precedent, ``AI-E11-1``). A
decision function that silently folds an empty record returns a confident answer forever,
and here that answer is the externalization gate.

The EMPTY-EMITTED-POPULATION half of that floor used to raise unconditionally too, and its
message named the exact confusion it could not resolve: *"That means the corpus could not
be read, not that everything in it was judged."* Correct for the world 13.3 was written in
— it had no evidence with which to tell the two apart, and chose the safe refusal. Epic 14
corrected ``vacuous_test_ast`` and created a third world: a corpus that **was** read, was
scanned file by file, had 5,129 test functions scored, emitted 4,284 advisory findings and
promoted **none** of them. That outcome was inexpressible by the instrument meant to record
it. So the floor now DISCRIMINATES on measured evidence:

* an empty population with **no** :class:`CorpusReadProof`, or one that does not prove a
  read, still raises :class:`VacuousDecisionError`, with the same claim it always made;
* an empty population with a **positive** proof — members audited at their pinned shas with
  the staged bytes proved byte-for-byte against the pin, source files scanned, test
  functions scored, two runs byte-identical — returns ``BLOCKED`` with the precision
  condition ``UNEVALUABLE``, which is what the architecture already registers for an empty
  denominator.

**Both directions are guarded**, because a narrowing proven in one direction is a hole.

``protocol_cleared`` is passed ``False`` as a LITERAL, deliberately
-------------------------------------------------------------------
:func:`decide_gate` computes ``adjudication_run_recorded_cleared`` itself, from the
committed record, exactly as the architecture's *Adjudication-record enforcement* rule
requires — and then still passes the literal ``False`` into the fold rather than threading
its own derivation back in. Measured, and the reason: ``protocol_cleared_call_sites``
(``tests/test_instrument_disclosure.py``) records a production call site **only** when the
keyword value is ``ast.Constant`` ``is True``, so a derived flag is INVISIBLE to it and
``TC-ArgusAgent-DOCS-001-46`` — the one guard tying the declared instrument status to the
harness — would go vacuous at the exact moment the gate flips. Whoever performs the flip
must close that blind spot **in the same change** (Story 13.3 / AC4(d)); until then this
module refuses to open it. The decision object still carries the derived verdict on
:attr:`GateDecision.adjudication_run_recorded_cleared`, so nothing is lost but the blind
spot.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from argus.precision.adjudication import (
    PROTOCOL_ADJUDICATOR_ROLES,
    PROTOCOL_PATH,
    RECORD_PATH,
    AdjudicatedPrecision,
    AdjudicationRecord,
    Exhaustive,
    adjudicator_role,
    fold_adjudicated_precision,
)
from argus.precision.gate_disclosure import (
    ConcentrationDisclosure,
    ResidualCompletionBound,
    VacuousDisclosureError,
    derive_concentration,
    derive_residual_completion_bound,
)
from argus.precision.replay_harness import PRECISION_GATE_THRESHOLD, ratio_string
from argus.store.canonical import dumps, dumps_bytes

__all__ = [
    "CONDITION_VERDICTS",
    "DECISION_RECORD_PATH",
    "GATE_OUTCOMES",
    "SECTION_5_CONDITIONS",
    "CleanRepoEvidence",
    "ConditionResult",
    "CorpusReadProof",
    "GateDecision",
    "UnregisteredConditionVerdict",
    "UnregisteredGateOutcome",
    "VacuousDecisionError",
    "condition_verdict_meaning",
    "decide_gate",
    "gate_outcome_meaning",
]

#: Repository-relative, forward-slash, resolved by the CALLER against its own root — the
#: same treatment ``adjudication.RECORD_PATH`` gets and for the same reason: this module is
#: imported from a built distribution where the file does not exist (``DF-9-2-A``), so a
#: module-level ``Path`` resolution here would ship a wheel that cannot import.
DECISION_RECORD_PATH = (
    "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/gate-decision-record.json"
)

_SCHEMA_VERSION = "1"
_STORY = "13-3-record-the-result-and-let-it-decide"


class UnregisteredGateOutcome(ValueError):
    """Raised on an outcome outside :data:`GATE_OUTCOMES` (the ``DF-10-4-E`` shape).

    A ``ValueError`` subclass (AR10). A silent default here would publish an outcome
    nobody registered onto the externalization gate — the comfortable wrong answer, on
    the one decision this plan exists to make honestly.
    """


class UnregisteredConditionVerdict(ValueError):
    """Raised on a per-condition verdict outside :data:`CONDITION_VERDICTS`."""


class VacuousDecisionError(VacuousDisclosureError):
    """Raised when a decision was requested over an empty record or empty population.

    The non-vacuity floor (``AI-E11-1``), as a TYPE rather than a comment. An empty
    record does not mean "everything in it was judged"; it means the corpus could not be
    read. Returning ``BLOCKED`` for it would be defensible, and it was rejected: a
    producer that reached this point has already failed to load its own evidence, and a
    recorded outcome would make that indistinguishable from a real halt.
    """


#: The CLOSED three-outcome vocabulary (AC1). Checked in BOTH directions: an unregistered
#: member raises, and a registered member nobody constructs is itself a finding.
GATE_OUTCOMES: dict[str, str] = {
    "CLEARED": (
        "CLEARED — all four protocol §5 conditions hold over an exhaustively adjudicated, "
        "byte-reproducible committed record. Clearing authorises ATTESTED externalization "
        "and nothing else: it is not a publish act, and it is not plan closure."
    ),
    "NOT_CLEARED": (
        "NOT CLEARED — the measurement RAN (the record is byte-reproducible AND "
        "exhaustively adjudicated AND the precision denominator is non-empty) and at "
        "least one protocol §5 condition FAILED. This is a RESULT: a real, measured "
        "shortfall. A failed measurement is not a reason to amend the threshold — it is "
        "the measurement working."
    ),
    "BLOCKED": (
        "BLOCKED — NOT a §5 outcome. The record is not exhaustively adjudicated, or not "
        "byte-reproducible, or the precision denominator is empty, so no §5 decision was "
        "taken. Recorded with its residual count and its closure path. This must NEVER be "
        "rendered, serialized, summarised or committed as 'the gate did not clear': a "
        "shortfall and an incomplete measurement are different claims, and downstream "
        "nothing can tell them apart once the wording collapses them."
    ),
}

#: The CLOSED per-condition verdict vocabulary (DN-3). ``NOT_APPLICABLE`` is a member
#: because protocol §5's clean-repo condition genuinely is not applicable over the corpus
#: that gates externalization, and the amendment 13.2 wrote forbids counting it met by
#: default. It is deliberately NOT a synonym for ``MET``.
CONDITION_VERDICTS: dict[str, str] = {
    "MET": "the condition was evaluated over a named corpus and holds.",
    "FAILED": "the condition was evaluated over a named corpus and does NOT hold.",
    "NOT_APPLICABLE": (
        "the condition cannot fail over this corpus for any possible input, so evaluating "
        "it here measures nothing. RECORDED with its reason and its corpus — never "
        "counted as met. A §5 condition that cannot fail is not a threshold."
    ),
    "UNEVALUABLE": (
        "the condition could not be evaluated at all: a protocol §4 precondition "
        "(byte-reproducibility, exhaustive adjudication) does not hold, so any value "
        "reported here would rest on nothing. Recorded with the residual, never as a "
        "failure and never as a pass."
    ),
}

#: §5's four conditions, in §5's own order. The ids are stable and the record is keyed by
#: them, so a condition cannot be dropped from the report without the schema noticing.
SECTION_5_CONDITIONS: tuple[str, ...] = (
    "precision-at-least-80-percent",
    "clean-repo-blocking-false-positives-zero",
    "corpus-floor-n-at-least-5",
    "adjudication-run-recorded-cleared",
)


def gate_outcome_meaning(outcome: str) -> str:
    """The registered meaning of *outcome* — RAISES on an unregistered member."""
    try:
        return GATE_OUTCOMES[outcome]
    except KeyError:
        raise UnregisteredGateOutcome(
            f"{outcome!r} is not a registered gate outcome. The closed vocabulary is "
            f"{sorted(GATE_OUTCOMES)!r}. Adding a fourth terminal state is a protocol "
            f"decision, not an implementation detail — an unregistered outcome would let "
            f"the externalization gate terminate in a state nobody defined."
        ) from None


def condition_verdict_meaning(verdict: str) -> str:
    """The registered meaning of a per-condition *verdict* — RAISES on an unregistered one."""
    try:
        return CONDITION_VERDICTS[verdict]
    except KeyError:
        raise UnregisteredConditionVerdict(
            f"{verdict!r} is not a registered condition verdict. The closed vocabulary is "
            f"{sorted(CONDITION_VERDICTS)!r}."
        ) from None


@dataclass(frozen=True)
class ConditionResult:
    """ONE protocol §5 condition, with its own measured value and its own verdict (DN-3).

    Reported individually and never collapsed into a conjunction. §5's clean-repo
    condition is currently ``NOT_APPLICABLE`` over the corpus that gates externalization;
    a single boolean would swallow that into a ``False`` — or, far worse, into a vacuous
    ``True`` — and the protocol amendment 13.2 wrote forbids exactly that.
    """

    condition_id: str
    requirement: str
    corpus: str
    measured: str
    verdict: str
    what_would_close_it: str

    def __post_init__(self) -> None:
        if self.condition_id not in SECTION_5_CONDITIONS:
            raise ValueError(
                f"{self.condition_id!r} is not one of protocol §5's conditions "
                f"{SECTION_5_CONDITIONS!r}. §5 enumerates four and the record is keyed by "
                f"them, so a fifth condition — or a renamed one — is a protocol amendment."
            )
        condition_verdict_meaning(self.verdict)
        if not self.what_would_close_it.strip():
            raise ValueError(
                f"{self.condition_id!r} carries no 'what would close it' clause. AC5 "
                f"requires every condition to name, in countable terms, what would move "
                f"it — a verdict with no closure path is a status, not a result."
            )

    def to_payload(self) -> dict[str, Any]:
        return {
            "condition_id": self.condition_id,
            "requirement": self.requirement,
            "corpus": self.corpus,
            "measured": self.measured,
            "verdict": self.verdict,
            "verdict_meaning": condition_verdict_meaning(self.verdict),
            "what_would_close_it": self.what_would_close_it,
        }


@dataclass(frozen=True)
class CleanRepoEvidence:
    """§5's clean-repo blocking-FP condition, over the corpus it was MEASURED on (AC2.2).

    Protocol §5 as amended 2026-08-16 names Story 13.3 by name: *"Story 13.3 must
    therefore evaluate this condition against the cartridge corpus explicitly, or record
    it not-applicable — it may not count it as met by default."* Both branches are
    expressible here and neither of them is "assume zero":

    * ``applicable=False`` — the repository corpus. ``_is_clean_repo`` needs an empty
      golden key **AND** ``max_blocking == 0`` and no repository member has either, so the
      condition is satisfied by construction for every possible input.
    * ``applicable=True`` — the cartridge corpus, where ``compute_precision`` measures a
      real ``clean_repo_fp`` and NAMES the clean members it folded.

    The caller supplies this because measuring the cartridge branch requires STAGING and
    AUDITING repositories, which is the impure test shell (§3.3) and must not happen
    inside a pure fold.
    """

    corpus: str
    applicable: bool
    clean_repo_fp: int | None
    clean_member_ids: tuple[str, ...]
    note: str

    def __post_init__(self) -> None:
        if self.applicable and self.clean_repo_fp is None:
            raise ValueError(
                "clean-repo evidence is marked applicable but carries no measured "
                "blocking-FP count. 'Applicable' means a number was measured; a missing "
                "number is NOT_APPLICABLE with its reason, never an implied zero."
            )
        if self.applicable and not self.clean_member_ids:
            raise ValueError(
                "clean-repo evidence is marked applicable over ZERO clean members. A "
                "false-positive ceiling folded over an empty clean population passes "
                "forever (non-vacuity floor, AI-E11-1)."
            )
        if not self.applicable and self.clean_repo_fp is not None:
            raise ValueError(
                "clean-repo evidence is marked NOT applicable yet carries a count. A "
                "number beside 'not applicable' is the shape a reader counts as met."
            )

    def condition(self) -> ConditionResult:
        """This evidence as §5's second condition — MET, FAILED or NOT_APPLICABLE."""
        if not self.applicable:
            verdict = "NOT_APPLICABLE"
            measured = "NOT MEASURED over this corpus — the condition cannot fail here"
            closes = (
                "evaluate the condition over the CARTRIDGE corpus, where "
                "compute_precision reports clean_repo_fp_applicable=True and names the "
                "clean members it folded; or amend protocol §5 to define a clean member "
                "of the repository corpus. Neither is this story's act."
            )
        elif self.clean_repo_fp == 0:
            verdict = "MET"
            measured = (
                f"{self.clean_repo_fp} blocking false positive(s) over "
                f"{len(self.clean_member_ids)} clean member(s): "
                f"{', '.join(self.clean_member_ids)}"
            )
            closes = "already met; it re-opens the moment any clean member emits a blocking finding"
        else:
            verdict = "FAILED"
            measured = (
                f"{self.clean_repo_fp} blocking false positive(s) over "
                f"{len(self.clean_member_ids)} clean member(s): "
                f"{', '.join(self.clean_member_ids)}"
            )
            closes = (
                f"{self.clean_repo_fp} blocking finding(s) on a clean member would have to "
                f"stop being emitted. The ceiling is ZERO and it is not negotiable: a "
                f"blocking finding on a repository with an empty golden key is a false "
                f"ACCUSATION (R6)."
            )
        return ConditionResult(
            condition_id="clean-repo-blocking-false-positives-zero",
            requirement=(
                "protocol §5: the clean-repo blocking false-positive count is 0 "
                "(clean_repo_fp == 0 for blocking findings)"
            ),
            corpus=self.corpus,
            measured=measured,
            verdict=verdict,
            what_would_close_it=closes,
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "corpus": self.corpus,
            "applicable": self.applicable,
            "clean_repo_fp": self.clean_repo_fp,
            "clean_member_ids": list(self.clean_member_ids),
            "note": self.note,
        }


@dataclass(frozen=True)
class CorpusReadProof:
    """PROOF that the corpus was READ — the evidence an EMPTY finding population needs (13.5).

    **Why this type exists.** :func:`decide_gate`'s non-vacuity floor refused an empty emitted
    population outright, with the message *"That means the corpus could not be read, not that
    everything in it was judged"*. That was correct for the world it was written in: Story
    13.3 could not distinguish the two cases, so it chose the safe refusal. Epic 14 corrected
    ``vacuous_test_ast`` and created a third world — a corpus that **was** read, was scanned
    file by file, had its test functions scored, emitted thousands of advisory findings, and
    promoted **none** of them to verdict-eligible. As shipped, that outcome was
    **inexpressible by the instrument that is supposed to record it**.

    The floor is therefore NARROWED, never removed. This object is the evidence that
    discriminates, and every field on it is measured by
    ``scripts/audit_validation_corpus.py`` on the run being decided:

    * ``members_audited`` / ``source_file_count`` — something was enumerated;
    * ``scored_population_count`` — the DETECTOR's own scored population was non-empty. This
      is the field that separates *"read and clean"* from *"unparsed"*: an unparsed file and
      a well-asserted file both emit nothing, and only a scored count tells them apart;
    * ``every_member_pin_verified`` — each staged file was proved, by git's own blob hash, to
      be the byte the manifest pins. Reproducibility is not provenance: two runs over the
      same WRONG bytes are reproducible;
    * ``every_member_byte_reproducible`` — protocol §4's determinism precondition.

    ``flagged_file_count`` and ``advisory_finding_count`` are RECORDED but deliberately NOT
    part of :attr:`proves_corpus_was_read`: requiring a flag would make a genuinely clean
    corpus unprovable, which is the opposite failure and would reward a noisier detector.

    PURE (AR8): a frozen value object with no I/O and no clock. The producer measures; this
    only says what the measurement has to contain before an absence may be called a result.
    """

    statement: str
    members_audited: int
    source_file_count: int
    scored_population_count: int
    flagged_file_count: int
    advisory_finding_count: int
    blocking_finding_count: int
    every_member_pin_verified: bool
    every_member_byte_reproducible: bool

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise VacuousDisclosureError(
                "a corpus-read proof carries no statement. The statement is what a stranger "
                "reads to tell a measured absence from an unread corpus; a proof nobody can "
                "read is a flag, and a flag is what this type exists to replace."
            )

    @property
    def proves_corpus_was_read(self) -> bool:
        """Every conjunct, measured — never a caller's assertion, never a default."""
        return (
            self.members_audited > 0
            and self.source_file_count > 0
            and self.scored_population_count > 0
            and self.every_member_pin_verified
            and self.every_member_byte_reproducible
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "statement": self.statement,
            "members_audited": self.members_audited,
            "source_file_count": self.source_file_count,
            "scored_population_count": self.scored_population_count,
            "flagged_file_count": self.flagged_file_count,
            "advisory_finding_count": self.advisory_finding_count,
            "blocking_finding_count": self.blocking_finding_count,
            "every_member_pin_verified": self.every_member_pin_verified,
            "every_member_byte_reproducible": self.every_member_byte_reproducible,
            "proves_corpus_was_read": self.proves_corpus_was_read,
        }


@dataclass(frozen=True)
class GateDecision:
    """The committed, DERIVED, machine-readable gate decision (AC3).

    No figure on it is hand-written: the ratio comes from the shared arithmetic, the
    corpus from the manifest, the counts from the committed adjudication record, the
    protocol version from the record cross-checked against the change-log head, and the
    commit sha and date from the producer's caller. It goes through
    ``argus.store.canonical`` and never ``json.dumps``.
    """

    outcome: str
    outcome_reason: str
    conditions: tuple[ConditionResult, ...]
    concentration: ConcentrationDisclosure
    completion_bound: ResidualCompletionBound
    clean_repo_evidence: CleanRepoEvidence
    fold: AdjudicatedPrecision
    corpus_members: tuple[dict[str, str], ...]
    record_path: str
    record_row_count: int
    record_live_row_count: int
    protocol_version: str
    protocol_change_log_head: str
    protocol_path: str
    adjudicators: tuple[str, ...]
    expert_hours: Fraction | None
    adjudication_run_recorded_cleared: bool
    closure_path: tuple[str, ...]
    commit_sha: str
    decided_on: str
    #: Story 13.5. Present when the run carried a positive corpus-read proof; ``None`` is the
    #: pre-13.5 shape and stays valid, because a decision over a NON-empty emitted population
    #: never needed one. Defaulted last so every existing construction site is unchanged.
    corpus_read_proof: CorpusReadProof | None = None
    #: Story 13.5 / AC9. Whether ``commit_sha`` describes the tree the measurement ran over.
    #: ``build_gate_decision.py`` stamped ``git rev-parse HEAD`` with NO dirty check, so on a
    #: dirty tree the recorded sha named a tree that was not the one measured. The state is
    #: now RECORDED — with the mechanically-recognised ``NOT ESTABLISHED`` marker when it
    #: cannot be established — rather than left to the reader to assume.
    commit_sha_provenance: str = "NOT RECORDED BY THIS RUN"

    def __post_init__(self) -> None:
        gate_outcome_meaning(self.outcome)
        if tuple(c.condition_id for c in self.conditions) != SECTION_5_CONDITIONS:
            raise ValueError(
                f"the decision must report ALL FOUR §5 conditions, in §5's order "
                f"{SECTION_5_CONDITIONS!r}; got "
                f"{tuple(c.condition_id for c in self.conditions)!r}. Reporting three and "
                f"a conjunction is how a condition that cannot fail gets counted as met."
            )
        if self.protocol_version != self.protocol_change_log_head:
            raise ValueError(
                f"the adjudication record was judged under protocol "
                f"{self.protocol_version!r} while the change-log head is "
                f"{self.protocol_change_log_head!r}. The protocol is amended BEFORE a run, "
                f"never reinterpreted during it — a decision folded across an amendment is "
                f"a re-interpretation of judgements nobody re-made."
            )
        if self.outcome == "CLEARED" and not all(c.verdict == "MET" for c in self.conditions):
            raise ValueError(
                "CLEARED requires all four §5 conditions MET. A NOT_APPLICABLE or "
                "UNEVALUABLE condition is not met — protocol §5 as amended 2026-08-16 "
                "forbids counting the clean-repo condition met by default, and this is "
                "that rule made unexpressible rather than written down."
            )
        if self.outcome == "BLOCKED" and not self.closure_path:
            raise ValueError(
                "a BLOCKED decision must record its CLOSURE PATH. An unqualified 'blocked' "
                "is barely better than a skip, and it is the shape that reads downstream "
                "as a shortfall."
            )
        if self.outcome != "BLOCKED" and not self.fold.evaluable:
            raise ValueError(
                f"outcome {self.outcome!r} was recorded over a fold that is NOT evaluable "
                f"({self.fold.exhaustiveness}). A §5 outcome may only be recorded when the "
                f"measurement RAN: reproducible AND exhaustive AND a non-empty denominator."
            )

    @property
    def failed_conditions(self) -> tuple[ConditionResult, ...]:
        """The conditions that did NOT hold — each with what would close it."""
        return tuple(c for c in self.conditions if c.verdict != "MET")

    def to_payload(self) -> dict[str, Any]:
        """The canonical mapping. Fractions are encoded by the canonical serializer."""
        return {
            "schema_version": _SCHEMA_VERSION,
            "story": _STORY,
            "decided_on": self.decided_on,
            "commit_sha": self.commit_sha,
            "commit_sha_provenance": self.commit_sha_provenance,
            "corpus_read_proof": (
                None if self.corpus_read_proof is None else self.corpus_read_proof.to_payload()
            ),
            "outcome": self.outcome,
            "outcome_meaning": gate_outcome_meaning(self.outcome),
            "outcome_reason": self.outcome_reason,
            "outcome_vocabulary": sorted(GATE_OUTCOMES),
            "section_5_conditions": [c.to_payload() for c in self.conditions],
            "concentration": self.concentration.to_payload(),
            "residual_completion_bound": self.completion_bound.to_payload(),
            "clean_repo_evidence": self.clean_repo_evidence.to_payload(),
            "precision": {
                "total_tp": self.fold.total_tp,
                "total_fp": self.fold.total_fp,
                "total_borderline": self.fold.total_borderline,
                "total_unadjudicated": self.fold.total_unadjudicated,
                "precision": self.fold.precision,
                "precision_ratio": self.fold.precision_ratio,
                "threshold": PRECISION_GATE_THRESHOLD,
                "meets_threshold": self.fold.meets_threshold,
                "evaluable": self.fold.evaluable,
                "provisional": self.fold.provisional,
                "gate_status": self.fold.gate_status,
            },
            "preconditions": {
                "determinism": (
                    "SATISFIED" if self.fold.determinism is None else str(self.fold.determinism)
                ),
                "exhaustiveness": str(self.fold.exhaustiveness),
                "residual_finding_ids": (
                    []
                    if isinstance(self.fold.exhaustiveness, Exhaustive)
                    else list(self.fold.exhaustiveness.residual_finding_ids)
                ),
            },
            "corpus": {
                "n": self.fold.n,
                "floor_n": self.fold.floor_n,
                "members": [dict(member) for member in self.corpus_members],
            },
            "adjudication_record": {
                "path": self.record_path,
                "row_count": self.record_row_count,
                "live_row_count": self.record_live_row_count,
                "protocol_version": self.protocol_version,
                "protocol_change_log_head": self.protocol_change_log_head,
                "protocol_path": self.protocol_path,
                "adjudicators": list(self.adjudicators),
                "adjudication_run_recorded_cleared": self.adjudication_run_recorded_cleared,
            },
            "expert_hours": self.expert_hours,
            "expert_hours_report": self.fold.expert_hours_report,
            "closure_path": list(self.closure_path),
        }

    def to_bytes(self) -> bytes:
        """The committed bytes, through ``argus.store.canonical`` — never ``json.dumps``."""
        return dumps_bytes(self.to_payload())

    def to_text(self) -> str:
        """The committed text, through ``argus.store.canonical`` — never ``json.dumps``."""
        return dumps(self.to_payload())


def _precision_condition(fold: AdjudicatedPrecision, bound: ResidualCompletionBound) -> ConditionResult:
    """§5(1) — precision >= 80%, as the EXACT ``Fraction`` comparison and nothing else."""
    if not fold.evaluable:
        verdict = "UNEVALUABLE"
        measured = (
            f"NOT COMPUTED BY THIS RUN — {fold.total_tp} TP / {fold.total_fp} FP / "
            f"{fold.total_borderline} BORDERLINE / {fold.total_unadjudicated} "
            f"UNADJUDICATED; {fold.exhaustiveness}"
        )
        closes = (
            f"protocol §4's ladder must terminate for every residual finding, after which "
            f"the ratio is computable. {bound.statement}"
        )
    elif fold.meets_threshold:
        verdict = "MET"
        measured = (
            f"precision = {fold.precision_ratio} over {fold.total_tp + fold.total_fp} "
            f"adjudicated finding(s) ({fold.total_tp} TP / {fold.total_fp} FP), compared "
            f"as the exact Fraction {fold.precision_ratio} >= {ratio_string(PRECISION_GATE_THRESHOLD)}"
        )
        closes = (
            "already met; it re-opens the moment a further finding is adjudicated FP or a "
            "judgement is superseded"
        )
    else:
        denominator = fold.total_tp + fold.total_fp
        # DERIVED, never estimated in prose (AC5): the smallest number of currently-FP
        # findings that would have to have been TP instead for the EXACT Fraction to reach
        # the threshold at this denominator. ``math.ceil`` over a ``Fraction`` is exact —
        # a float here would answer a different question at the boundary (AR4).
        needed = max(
            0, math.ceil(PRECISION_GATE_THRESHOLD * denominator) - fold.total_tp
        )
        verdict = "FAILED"
        measured = (
            f"precision = {fold.precision_ratio} over {denominator} adjudicated finding(s) "
            f"({fold.total_tp} TP / {fold.total_fp} FP), compared as the exact Fraction "
            f"{fold.precision_ratio} < {ratio_string(PRECISION_GATE_THRESHOLD)}"
        )
        closes = (
            f"at the current denominator of {denominator}, {needed} further finding(s) "
            f"would have to be TP rather than FP for the exact Fraction to reach "
            f"{ratio_string(PRECISION_GATE_THRESHOLD)}. Re-classifying a judged finding to reach "
            f"it is forbidden (protocol §5; Story 13.3 / AC5): a failed measurement is not "
            f"a reason to amend the threshold, and the honest closure is more adjudicated "
            f"evidence, not a different reading of this evidence."
        )
    return ConditionResult(
        condition_id="precision-at-least-80-percent",
        requirement=(
            f"protocol §5: precision (TP / (TP + FP) over FINDINGS) >= "
            f"{ratio_string(PRECISION_GATE_THRESHOLD)}, checked as the EXACT Fraction — no "
            f"float, no rounding, no percentage literal (AR4)"
        ),
        corpus="the ratified repository validation set, via the committed adjudication record",
        measured=measured,
        verdict=verdict,
        what_would_close_it=closes,
    )


def _floor_condition(fold: AdjudicatedPrecision) -> ConditionResult:
    """§5(3) — N >= the ONE locked floor, derived through 13.1's eligible-member count."""
    met = fold.n >= fold.floor_n
    return ConditionResult(
        condition_id="corpus-floor-n-at-least-5",
        requirement=(
            f"protocol §5 as amended 2026-08-16 (Story 13.1 / DN-1): N >= {fold.floor_n} "
            f"ELIGIBLE members of the repository validation set "
            f"(_manifest.eligible_member_count() >= VALIDATION_SET_FLOOR_N). One floor, "
            f"two populations — never forked"
        ),
        corpus="tests/corpus/_manifest.py — the one named place a corpus member exists",
        measured=f"N = {fold.n} eligible member(s); floor N = {fold.floor_n}",
        verdict="MET" if met else "FAILED",
        what_would_close_it=(
            "already met by member COUNT. Note the AC3b concentration disclosure: the "
            "members that satisfy this floor and the members that contributed to the ratio "
            "are different sets, and this condition measures the former."
            if met
            else f"{fold.floor_n - fold.n} further eligible member(s) must be ratified "
            f"into tests/corpus/_manifest.py under Story 13.1 / AC3b"
        ),
    )


def _recorded_cleared_condition(
    *,
    fold: AdjudicatedPrecision,
    adjudicators: Sequence[str],
    unattributed_row_ids: Sequence[str],
    record_is_tracked_in_git: bool,
    record_path: str,
) -> ConditionResult:
    """§5(4) — the adjudication RUN is recorded cleared, DERIVED from the record (AC2.4).

    Never from a caller's assertion. The architecture's *Adjudication-record enforcement*
    rule: *"the >=80%-precision externalization gate may be cleared only from a COMMITTED,
    append-only, machine-readable adjudication record in which every emitted blocking
    finding carries exactly ONE LIVE disposition attributed to a human role §2
    registers."* Every clause of that sentence is a conjunct below, and each is measured.
    """
    problems: list[str] = []
    if not record_is_tracked_in_git:
        problems.append(
            f"the record at {record_path} is NOT tracked by git — gate evidence that is "
            f"not in git is not evidence"
        )
    if fold.determinism is not None:
        problems.append(str(fold.determinism))
    if not isinstance(fold.exhaustiveness, Exhaustive):
        problems.append(str(fold.exhaustiveness))
    if unattributed_row_ids:
        problems.append(
            f"{len(unattributed_row_ids)} live row(s) carry a human disposition with no "
            f"adjudicator registered by protocol §2 "
            f"{PROTOCOL_ADJUDICATOR_ROLES!r}: {', '.join(sorted(unattributed_row_ids)[:5])}"
        )
    if not adjudicators:
        problems.append(
            "NO adjudicator is named on any live row — an unattributed adjudication run "
            "is not a recorded one (non-vacuity floor, AI-E11-1)"
        )
    verdict = "MET" if not problems else "FAILED"
    measured = (
        f"recorded cleared: run attributed to {', '.join(adjudicators)} over "
        f"{fold.total_tp + fold.total_fp} adjudicated finding(s)"
        if verdict == "MET"
        else "NOT recorded cleared — " + "; ".join(problems)
    )
    return ConditionResult(
        condition_id="adjudication-run-recorded-cleared",
        requirement=(
            "protocol §5 + architecture §Enforcement (Adjudication-record enforcement, "
            "2026-08-16): the gate may be cleared ONLY from a COMMITTED, append-only, "
            "machine-readable adjudication record in which every emitted blocking finding "
            "carries exactly ONE LIVE disposition attributed to a human role §2 registers. "
            "NEVER from a caller's assertion"
        ),
        corpus=record_path,
        measured=measured,
        verdict=verdict,
        what_would_close_it=(
            "already met; it re-opens if the record leaves git, a judgement is withdrawn, "
            "or the corpus grows a finding nobody has judged"
            if verdict == "MET"
            else "; ".join(problems)
        ),
    )


def decide_gate(
    record: AdjudicationRecord,
    *,
    expected_finding_ids: Sequence[str],
    population_n: int,
    floor_n: int,
    protocol_change_log_head: str,
    clean_repo_evidence: CleanRepoEvidence,
    ratified_members: Sequence[Mapping[str, str]],
    record_is_tracked_in_git: bool,
    commit_sha: str,
    decided_on: str,
    record_path: str = RECORD_PATH,
    protocol_path: str = PROTOCOL_PATH,
    corpus_read_proof: CorpusReadProof | None = None,
    commit_sha_provenance: str = "NOT RECORDED BY THIS RUN",
) -> GateDecision:
    """THE decision. Calls the existing fold; authors no second one (AC1, AC2, AC3).

    Order is protocol §4's and is not a convenience:
    :meth:`~argus.precision.adjudication.AdjudicationRecord.determinism_precondition`
    first (§4's last bullet, *"before any pass/fail is recorded"*), then
    :meth:`~argus.precision.adjudication.AdjudicationRecord.exhaustiveness`, then the
    ratio. :func:`~argus.precision.adjudication.fold_adjudicated_precision` already
    evaluates them in exactly that order, so it is CALLED rather than re-implemented.

    ``protocol_cleared`` is passed the literal ``False`` — see this module's docstring.
    The derived verdict lives on :attr:`GateDecision.adjudication_run_recorded_cleared`
    and on §5's fourth condition, where a reader can see it; threading it back into the
    fold would blind ``TC-ArgusAgent-DOCS-001-46`` and buy nothing.
    """
    # ── the non-vacuity floor, asserted FIRST, before anything is asserted about them ──
    if not record.rows:
        raise VacuousDecisionError(
            "the adjudication record holds ZERO rows. Every condition below would be "
            "computed over nothing and the decision would be confident and empty — and "
            "here that decision is the externalization gate (AI-E11-1)."
        )
    expected = tuple(expected_finding_ids)
    # ── the floor, NARROWED (Story 13.5 / AC5) and deliberately not removed ────────────
    # Before: an empty emitted population raised, unconditionally. The message named the
    # exact confusion — "the corpus could not be read, not that everything in it was
    # judged" — and could not resolve it, because 13.3 had no evidence with which to.
    # Now the two cases are separated by MEASURED evidence, and only the second is
    # admitted. Without a positive corpus-read proof the refusal is byte-unchanged, which
    # is what keeps TC-ArgusAgent-PRECISION-001-58 green at the same seam.
    corpus_was_read = corpus_read_proof is not None and corpus_read_proof.proves_corpus_was_read
    if not expected and not corpus_was_read:
        raise VacuousDecisionError(
            "the emitted-finding population is EMPTY. That means the corpus could not be "
            "read, not that everything in it was judged; exhaustiveness over nothing is "
            "the guard that passes forever (AI-E11-1). An empty population is admissible "
            "ONLY with a positive corpus-read proof (members audited at their pinned shas "
            "with the staged bytes proved against the pin, source files scanned, test "
            "functions scored, two runs byte-identical) — and none was supplied."
        )
    if record.protocol_version != protocol_change_log_head:
        raise ValueError(
            f"the record was judged under protocol {record.protocol_version!r} while the "
            f"change-log head is {protocol_change_log_head!r}. Amend the protocol BEFORE a "
            f"run, never during it (TC-ArgusAgent-PRECISION-001-45)."
        )

    fold = fold_adjudicated_precision(
        record,
        expected_finding_ids=expected,
        population_n=population_n,
        floor_n=floor_n,
        protocol_cleared=False,
        protocol_path=protocol_path,
    )

    live = record.live_rows()
    adjudicators = tuple(
        sorted({row.adjudicator for row in live if row.adjudicator is not None})
    )
    unattributed = tuple(
        row.row_id
        for row in live
        if row.is_human_judgement
        and (
            row.adjudicator is None
            or adjudicator_role(row.adjudicator) not in PROTOCOL_ADJUDICATOR_ROLES
        )
    )
    residual_count = (
        0
        if isinstance(fold.exhaustiveness, Exhaustive)
        else fold.exhaustiveness.residual_count
    )
    bound = derive_residual_completion_bound(
        total_tp=fold.total_tp,
        total_fp=fold.total_fp,
        residual_count=residual_count,
    )
    conditions = (
        _precision_condition(fold, bound),
        clean_repo_evidence.condition(),
        _floor_condition(fold),
        _recorded_cleared_condition(
            fold=fold,
            adjudicators=adjudicators,
            unattributed_row_ids=unattributed,
            record_is_tracked_in_git=record_is_tracked_in_git,
            record_path=record_path,
        ),
    )
    recorded_cleared = conditions[3].verdict == "MET"

    # ── the three-outcome dispatch, in protocol §4's order ────────────────────────────
    closure: tuple[str, ...] = ()
    if fold.determinism is not None:
        outcome = "BLOCKED"
        reason = (
            f"protocol §4's byte-reproducibility precondition does NOT hold, and it is "
            f"evaluated before any pass/fail is recorded. {fold.determinism}"
        )
        closure = (
            "re-run scripts/audit_validation_corpus.py over every member at its pinned "
            "sha and establish byte-reproducibility across two runs",
            "re-build the adjudication record so it carries the re-measured result",
            "re-run this decision",
        )
    elif not expected:
        # Story 13.5. Reachable ONLY with a positive corpus-read proof — the floor above
        # raises otherwise. This is the branch that makes "we read 1,960 files, scored
        # 5,129 test functions, emitted 4,284 advisory findings and promoted NONE of them"
        # expressible, and distinguishable from "we read nothing". It sits BEFORE the
        # exhaustiveness branch because exhaustiveness over an empty population is
        # unobservable rather than incomplete, and reporting it as incomplete would tell a
        # reader a judgement had not finished when there is nothing to judge.
        #
        # The outcome is BLOCKED — the SAME registered member 13.3 recorded, and NOT a
        # fourth one. GATE_OUTCOMES is closed at three and BLOCKED already means exactly
        # "no §5 decision was taken". What differs is the REASON, and the reason is the
        # whole content of this story: 13.3 was BLOCKED on EXHAUSTIVENESS (five residual
        # ladders); this is BLOCKED on the DENOMINATOR. Same outcome member, different
        # claims, and the record must let a stranger tell which happened.
        proof = corpus_read_proof
        assert proof is not None  # noqa: S101 - unreachable otherwise; the floor above raised
        outcome = "BLOCKED"
        reason = (
            f"the corpus WAS READ and NOTHING was promoted to a verdict-eligible finding, "
            f"so the emitted blocking population is empty and the precision denominator "
            f"with it. This is NOT an unread corpus and it is NOT a shortfall: "
            f"{proof.statement} An empty denominator is not an 80% result and it is not a "
            f"failed measurement; it is no result, recorded as such with the evidence that "
            f"the measurement ran."
        )
        closure = (
            "the detector emits at least one verdict-eligible finding over this corpus, or "
            "over a corpus chosen BEFORE anyone looks at what it contains — a corpus "
            "chosen to make the gate clear is the corpus-shopping failure mode itself",
            "the named human (protocol §2) adjudicates that population TP or FP",
            "re-run this decision, and let the arithmetic decide",
            "the pre-registered stopping rule governs which of those is attempted and how "
            "many times: DF-13-5-A, ANSWERED 2026-08-17 BEFORE any number existed, allows "
            "exactly ONE bench-expansion round and names the fallback if it returns zero. "
            "Executing that rule is the OWNER'S act after this outcome is recorded, and is "
            "not taken here",
        )
    elif not isinstance(fold.exhaustiveness, Exhaustive):
        outcome = "BLOCKED"
        reason = (
            f"the record is NOT exhaustively adjudicated: {fold.exhaustiveness}. Protocol "
            f"§4 requires the FULL populated corpus, never a sample, and a ratio over the "
            f"subset that happens to carry a TP/FP disposition is precisely the sampled "
            f"measurement §4 forbids — downstream it is indistinguishable from an honest "
            f"one. {bound.statement}"
        )
        closure = (
            f"protocol §4's borderline ladder terminates for each of the "
            f"{residual_count} residual finding(s): locator re-examination -> golden-key "
            f"correction -> external tie-break",
            "the QA-Lead second reviewer and, on persistent disagreement, the external "
            "tie-break adjudicator are FILLED — protocol §2 records both roles as "
            "*unfilled*, and filling them is itself an operator act no agent may perform",
            "the resolving judgements are appended to the record as SUPERSEDING rows "
            "(append-only; a correction supersedes, never rewrites) by re-running "
            "scripts/build_adjudication_record.py and recording the actual expert-hours",
            "re-run this decision, and let the arithmetic decide",
        )
    elif fold.precision is None:
        outcome = "BLOCKED"
        reason = (
            "the precision DENOMINATOR is empty — no finding entered TP+FP over this "
            "population, so there is no measurement to compare against the threshold. An "
            "empty denominator is not an 80% result; it is no result."
        )
        closure = (
            "adjudicate at least one emitted blocking finding TP or FP under protocol §4",
            "re-run this decision",
        )
    elif all(condition.verdict == "MET" for condition in conditions):
        outcome = "CLEARED"
        reason = (
            f"all four protocol §5 conditions hold over an exhaustively adjudicated, "
            f"byte-reproducible committed record: precision {fold.precision_ratio} >= "
            f"{ratio_string(PRECISION_GATE_THRESHOLD)}, the clean-repo blocking-FP condition is "
            f"met over {clean_repo_evidence.corpus}, N = {fold.n} >= {fold.floor_n}, and "
            f"the adjudication run is recorded cleared. Clearing authorises ATTESTED "
            f"externalization and NOTHING ELSE."
        )
    else:
        outcome = "NOT_CLEARED"
        failed = ", ".join(
            f"{c.condition_id} ({c.verdict})" for c in conditions if c.verdict != "MET"
        )
        reason = (
            f"the measurement RAN — the record is byte-reproducible, exhaustively "
            f"adjudicated, and the denominator holds "
            f"{fold.total_tp + fold.total_fp} finding(s) — and "
            f"{len(tuple(c for c in conditions if c.verdict != 'MET'))} of protocol §5's "
            f"four conditions did not hold: {failed}. This is a RESULT, not an absence. A "
            f"failed measurement is not a reason to amend the threshold; it is the "
            f"measurement working."
        )

    return GateDecision(
        outcome=outcome,
        outcome_reason=reason,
        conditions=conditions,
        concentration=derive_concentration(
            record,
            ratified_member_ids=[str(member["member_id"]) for member in ratified_members],
        ),
        completion_bound=bound,
        clean_repo_evidence=clean_repo_evidence,
        fold=fold,
        corpus_members=tuple(dict(member) for member in ratified_members),
        record_path=record_path,
        record_row_count=len(record.rows),
        record_live_row_count=len(live),
        protocol_version=record.protocol_version,
        protocol_change_log_head=protocol_change_log_head,
        protocol_path=protocol_path,
        adjudicators=adjudicators,
        expert_hours=record.expert_hours,
        adjudication_run_recorded_cleared=recorded_cleared,
        closure_path=closure,
        commit_sha=commit_sha,
        decided_on=decided_on,
        corpus_read_proof=corpus_read_proof,
        commit_sha_provenance=commit_sha_provenance,
    )
