"""The EVIDENCE protocol §5's conditions are measured from — supplied, never assumed.

Verification area ``TC-ArgusAgent-PRECISION-001-53``.. (``tests/test_gate_decision.py``).
A cohesion split from :mod:`argus.precision.gate_decision`, taken 2026-08-20 under Story
16.2 to discharge ``DF-16-1-B``'s SPLIT-FIRST trigger (that module stood at 1,197 of
NFR-M1's 1,200 lines and a sixth §5 condition does not fit in three). The boundary is the
one Story 16.2 §2.1 measured by AST: :class:`CleanRepoEvidence` and
:class:`CorpusReadProof`, moved unchanged, and re-exported from
:mod:`argus.precision.gate_decision` so **not one import line anywhere moved**.

**Why the boundary is HERE and is a real seam rather than a line count.** Both types are
things the CALLER MEASURES and hands in — staging and auditing repositories is the impure
test shell (protocol §3.3) and may not happen inside a pure fold — while
:mod:`argus.precision.gate_decision` is what the result IS. Neither type decides anything:
one says what was measured over the clean corpus, the other says what has to have been
measured before an ABSENCE of findings may be read as a result rather than as an unread
corpus.

One direction only: ``gate_decision`` -> ``gate_evidence`` -> ``gate_conditions``. Every
condition object built here is a :class:`~argus.precision.gate_conditions.ConditionResult`
from the layer below, which is why that layer is a separate module — see its docstring.

PURE (AR8): frozen value objects, no I/O, no clock, no repository-only path (``DF-9-2-A``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from argus.precision.gate_conditions import ConditionResult
from argus.precision.gate_disclosure import VacuousDisclosureError

__all__ = [
    "CleanRepoEvidence",
    "CorpusReadProof",
]


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
