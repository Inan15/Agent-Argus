"""Story 16.2 — protocol §5's SEAL condition: evidence the tool was never tuned against.

Verification area ``TC-ArgusAgent-PRECISION-001-87``.. (``tests/test_gate_seal.py``).
Drivers: `precision-validation-protocol.md` §5 as amended **2026-08-20** (a second dated
block **under the existing V1.3** — the change-log head did NOT move, by operator decision,
because the committed record carries 31 human judgements made under V1.3 and re-stamping
them would re-interpret judgements nobody re-made); the 2026-08-20 sprint change proposal
§1.3 (H-2) and §4.3(2); **AR4** (exact arithmetic); **AR7** (reuse, never fork); **AR8**
(pure — no I/O, no clock, no network, no manifest resolution); **AR10** (typed failures);
**NFR-M1**; **DF-9-2-A** (no module-level repository-only path — there is not one below,
and there cannot be: every input arrives as an argument).

What this module is
-------------------
H-2, verbatim from the proposal: *"Nothing is held back. The cartridge corpus has an
author-blind holdout (``holdout_vacuous``). The repository corpus that actually gates has
none. If all 14 bench members are adjudicated and the detector is then tuned, no untouched
population remains to show the tool was not shaped to fit its own exam."*

This module is the repository corpus's answer. It holds the **partition rule** — a pure
function of a member's pinned commit sha plus a prior-output override — and the §5
condition that makes the partition binding: *the precision ratio is evaluable only over a
population that drew findings from enough distinct **SEALED** members.* Tuning happens
against the ``open`` partition; the gate is computed over the ``sealed`` one.

Nothing here recounts anything. :func:`assess_seal` reads its counts off the SAME
:class:`~argus.precision.gate_disclosure.ConcentrationDisclosure` instance the decision
publishes and the SAME partition strings the decision already carries on its corpus
members — a second count is a second thing that can drift, invisibly, from the disclosure
it contradicts.

THREE partition values, not two (DN-16-2-4)
-------------------------------------------
:data:`PARTITION_VALUES` is a CLOSED vocabulary that RAISES on an unregistered member (the
``DF-10-4-E`` shape ``PROVENANCE_VALUES`` / ``GATE_OUTCOMES`` / ``CONDITION_VERDICTS``
already use in this codebase). *Rejected:* collapsing ``pre-seal`` into ``open``. It is
arithmetically identical — only ``sealed`` is counted — and it would tell a reader that the
five ratified members were **assigned** by the bisection, when in fact they were
**excluded from sealing** because Argus output over them already existed. A measured
result and an unobservable one are different claims, and this project's dominant defect
class is exactly the surface that cannot tell them apart.

THE RULE, and why the override is load-bearing rather than decorative
----------------------------------------------------------------------
See :data:`SEAL_RULE_DERIVATION`. Stated once: a member over which Argus output already
existed when the seal was taken is ``pre-seal`` **unconditionally**; every other member is
``sealed`` iff ``int(commit_sha, 16) % 2 == 1`` and ``open`` otherwise. The override is
not a tidiness clause. Measured on the manifest this rule was frozen against, two of the
five already-audited members carry **odd** pins, and one of them supplied 7 of the
committed record's 31 judged findings: the bisection alone would have declared two
already-audited members "sealed" and manufactured a fake holdout. *A member that has
already been run over cannot be a holdout, and a rule capable of sealing one is not a seal.*

The FLOOR is the ONE 16.1 already derived, resolved not re-typed
-----------------------------------------------------------------
:func:`sealed_member_floor` **is** :func:`~argus.precision.gate_breadth.contributing_member_floor`
— ``(VALIDATION_SET_FLOOR_N + 1) // 2``, reached by CALLING it. Story 16.1 already decided
*how many distinct contributing members a denominator needs*; this condition adds *and they
must be members the tool was never tuned against*. Deriving the two from one function is
what stops them drifting apart, and it makes §0.3's closure path countable in advance:
protocol §6 R2 must ratify at least that many members from the sealed partition, or
``CLEARED`` is unreachable — which the operator must be told **before** taking the act.

Why not the obvious alternatives, each rejected with its reason:

* **every contributing member must be sealed** — a SHUTDOWN, not a strengthening, and by
  construction: the five members that already have output are permanently ``pre-seal``,
  they will keep contributing findings, and the only way to satisfy such a rule would be to
  drop them from the population — which is the NARROWING protocol §5 and Story 13.3 / AC5
  forbid. Story 16.1 HALTED rather than land an arm that could not be satisfied; this is
  that same test applied to this arm, and it is why the arm below is a COUNT;
* **at least one sealed contributing member** — that is H-1 (*a score drawn from one
  repository is not a score*) re-introduced on the sealed side, one epic after it was
  closed;
* **a majority of the CONTRIBUTING members must be sealed** — set-relative: the threshold
  would move as a side effect of how many pre-seal members happened to emit, so the same
  evidence would pass or fail depending on evidence that has nothing to do with it;
* **a second, seal-specific constant** — DN-3's one-floor rule, forked. Two floors is how
  two corpora happened in the first place.

Its OWN verdict is MET or FAILED, and no terminal state is invented
--------------------------------------------------------------------
The seal condition's own verdict is ``MET`` or ``FAILED`` — it *was* evaluated over a
named population. ``UNEVALUABLE`` would tell a reader the provenance of the evidence was
unknown, which is a different and false claim. What becomes ``UNEVALUABLE`` is protocol
§5's **precision** condition, and the gate outcome is ``BLOCKED`` with a countable closure
path. ``GATE_OUTCOMES`` stays CLOSED at three and ``CONDITION_VERDICTS`` at four.

``gate_decision`` builds the ``ConditionResult`` because ``ConditionResult`` lives in
``gate_conditions`` and this module is imported by the registry that names it — one
direction only, ``gate_decision`` -> ``gate_seal``, exactly as DN-16-1-3 has it for
``gate_breadth``.

**Direction of travel, stated once:** every change this module makes to the gate makes
clearing **HARDER**, and none of it can make clearing easier. A population that cleared
before either still clears or is now ``BLOCKED``; no population that failed before can
pass because of anything here. It touches neither the ``>= 80%`` ``Fraction``, nor
``VALIDATION_SET_FLOOR_N``, nor ``eligible_member_count()``, nor the ratified member list,
nor ``MANIFEST_FIELDS``. It PARTITIONS; it does not narrow, and every finding from every
partition stays recorded and stays disclosed.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from argus.precision.adjudication import AdjudicatedPrecision
from argus.precision.gate_breadth import contributing_member_floor
from argus.precision.gate_disclosure import ConcentrationDisclosure
from argus.precision.replay_harness import precision_gate_status_for

__all__ = [
    "DETECTOR_TUNING_PATHS",
    "PARTITION_OPEN",
    "PARTITION_PRE_SEAL",
    "PARTITION_SEALED",
    "PARTITION_VALUES",
    "SEALED_MEMBER_FLOOR_DERIVATION",
    "SEAL_CITATION_RULE",
    "SEAL_CITATION_TRAILER",
    "SEAL_CITATION_VALUES",
    "SEAL_CONDITION_ID",
    "SEAL_RULE_DERIVATION",
    "MissingMemberPartition",
    "SealAssessment",
    "UnregisteredPartition",
    "UnsealablePin",
    "VacuousSealError",
    "assess_seal",
    "cites_partition",
    "member_partitions",
    "partition_meaning",
    "partition_of",
    "seal_blocked_reason",
    "seal_closure_path",
    "sealed_member_floor",
    "sealed_precision_gate_status",
]


class UnregisteredPartition(ValueError):
    """Raised on a partition outside :data:`PARTITION_VALUES` (the ``DF-10-4-E`` shape).

    A ``ValueError`` subclass (AR10). A silent default here would let a member be counted
    into — or out of — the sealed population under a name nobody registered, on the one
    surface that exists to say which evidence the tool was never tuned against.
    """


class UnsealablePin(ValueError):
    """Raised when a partition is asked of something that is not a 40-hex commit sha.

    A ``ValueError`` subclass (AR10) whose message says what a reader must do. A sha-ordered
    rule over an UNVALIDATED sha is not mechanically reproducible: ``int(sha, 16)`` would
    raise or, worse, succeed on a shortened sha and answer a question about a different
    number. The pin is the anchor the whole seal rests on, so this refuses rather than
    guesses.
    """


class MissingMemberPartition(ValueError):
    """Raised when a corpus member reaches the seal carrying no partition.

    A ``ValueError`` subclass (AR10). Defaulting an absent partition to ``open`` — or to
    ``pre-seal`` — would publish a partition nobody derived, and it would do so on the
    conservative-looking side, which is precisely how a false subject survives review
    (``DF-9-2-B``: a true status carrying a false reason). An unknown partition is an
    ERROR, never a value.
    """


class VacuousSealError(ValueError):
    """Raised when the seal was assessed over a corpus carrying ZERO members.

    The non-vacuity floor (``AI-E11-1``) as a TYPE. *k sealed of zero* has no denominator:
    the condition would report a measured shortfall over a population that does not exist,
    and every sentence it published would be about nothing.
    """


#: The three partition values, named ONCE, as a CLOSED vocabulary that RAISES on an
#: unregistered member. ``pre-seal`` is a member and not a synonym for ``open`` — see
#: DN-16-2-4 and this module's docstring.
PARTITION_SEALED = "sealed"
PARTITION_OPEN = "open"
PARTITION_PRE_SEAL = "pre-seal"

PARTITION_VALUES: dict[str, str] = {
    PARTITION_SEALED: (
        "SEALED — no Argus output over this member existed when the seal was taken, and its "
        "pinned commit sha reads ODD as an integer. Evidence drawn from a sealed member is "
        "the only evidence protocol §5's seal condition counts, because it is the only "
        "evidence the detector cannot have been tuned against. A sealed member's findings "
        "are still recorded and still disclosed like any other's: the seal governs what may "
        "GATE, never what is REPORTED."
    ),
    PARTITION_OPEN: (
        "OPEN — no Argus output over this member existed when the seal was taken, and its "
        "pinned commit sha reads EVEN. This is the partition tuning happens against. It is "
        "a full member of the corpus with its findings recorded and disclosed; what it "
        "cannot do is satisfy §5's seal condition, because a member the detector may have "
        "been shaped around cannot also be the evidence that it was not."
    ),
    PARTITION_PRE_SEAL: (
        "PRE-SEAL — Argus output over this member ALREADY EXISTED when the seal was taken, "
        "so the bisection was never applied to it. It is EXCLUDED from sealing rather than "
        "assigned by the rule, and the distinction is load-bearing: a member that has "
        "already been run over cannot be a holdout, whatever its sha says, and a rule "
        "capable of sealing one would manufacture a fake holdout. Recorded as its own value "
        "rather than folded into 'open' so no reader can mistake an exclusion for an "
        "assignment (DN-16-2-4)."
    ),
}

#: §5's sixth condition id, named ONCE — used by ``SECTION_5_CONDITIONS``, by the builder in
#: :mod:`argus.precision.gate_decision` and by the by-id lookup, so three literals that
#: could drift apart are one constant. The ``RECORDED_CLEARED_CONDITION_ID`` /
#: ``BREADTH_CONDITION_ID`` precedent.
SEAL_CONDITION_ID = "gate-evidence-drawn-from-the-sealed-partition"

#: THE RULE AND ITS REJECTED ALTERNATIVES, recorded WITH the rule rather than in story prose
#: (AC1.2; the ``BREADTH_MEMBER_FLOOR_DERIVATION`` precedent). ⛔ The order in which this was
#: decided is part of the claim: the rule was chosen on the STRUCTURAL grounds below, and the
#: split it produces was measured AFTERWARDS and frozen as a table a guard re-derives from
#: this very function. **A rule chosen because of the split it produces is the
#: corpus-shopping failure mode with an extra step**, so no figure about the resulting split
#: appears here — it is derived, never pinned (``DF-8-5-C``).
SEAL_RULE_DERIVATION = (
    "TWO CONJUNCTS, in this order. (1) PRIOR-OUTPUT OVERRIDE: a member over which Argus "
    "output already existed when the seal was taken is 'pre-seal' UNCONDITIONALLY, whatever "
    "its sha says — a member that has already been run over cannot be a holdout, and a rule "
    "capable of sealing one would manufacture a fake one. (2) THE BISECTION: every other "
    "member is 'sealed' iff int(commit_sha, 16) % 2 == 1 — the PARITY OF THE PINNED OBJECT "
    "NAME READ AS AN INTEGER — and 'open' otherwise. "
    "CHOSEN ON STRUCTURAL GROUNDS, AND THE SPLIT MEASURED AFTERWARDS. The pin is the "
    "strongest available anchor: it was frozen before any output existed, changing it "
    "changes which bytes are audited, and the change is visible in a diff and refused by the "
    "row's own construction. REJECTED: the parity of a chosen hex DIGIT — an arbitrary "
    "position, not a property of the number (and, measured across the manifest this rule was "
    "frozen against, the last-digit reading agrees with this one on every single row, so it "
    "is not even a second rule). REJECTED: hashing member_id — a local name this project "
    "chose and can edit. REJECTED, DECISIVELY: any SET-RELATIVE rule, such as sorting by sha "
    "and alternating the index. The ratified set is not known until the protocol §6 R2 "
    "operator act, so a rank-within-set rule RE-PARTITIONS SILENTLY when the operator "
    "ratifies eleven instead of fourteen — removing one member shifts every subsequent index "
    "— which makes it re-derivable after the fact to a different answer, and that is exactly "
    "what 'pre-committed' forbids. A per-row function of the pin is stable under every "
    "ratification subset: each member's partition is already determined and publishable "
    "today, so the operator can change the partition's SIZE but never a MEMBER'S partition."
)

#: The floor's derivation, stated as a RESOLUTION of 16.1's rather than as a second rule —
#: which is what the code below does, by calling that function.
SEALED_MEMBER_FLOOR_DERIVATION = (
    "the SAME floor protocol §5's breadth arm already derives — "
    "contributing_member_floor(VALIDATION_SET_FLOOR_N) = (VALIDATION_SET_FLOOR_N + 1) // 2 — "
    "REACHED BY CALLING IT, never re-typed and never forked (AR7; DN-3's one-floor rule). "
    "Story 16.1 decided HOW MANY distinct contributing members a denominator needs; this "
    "condition adds AND THEY MUST BE MEMBERS THE TOOL WAS NEVER TUNED AGAINST. Deriving both "
    "from one function is what stops them drifting apart, and it makes the closure path "
    "countable in advance: protocol §6 R2 must ratify at least this many members from the "
    "SEALED partition, or CLEARED is unreachable — which an operator must be told BEFORE "
    "taking the act, not discover after"
)

#: AC4.4 — the trailer token a post-seal detector change must carry, and the values it may
#: take. Named as constants so the rule, the predicate and the guard's failure message are
#: one string rather than three that can drift.
SEAL_CITATION_TRAILER = "Evidence-partition"
SEAL_CITATION_VALUES: tuple[str, ...] = (PARTITION_SEALED, PARTITION_OPEN, "none")

#: The declared DETECTOR-TUNING path set (AC4.1). Repository-relative, forward-slash, and
#: resolved by the CALLER against its own root — the same treatment
#: ``gate_decision.DECISION_RECORD_PATH`` and ``adjudication.RECORD_PATH`` get, and for the
#: same reason: this module is imported from a built distribution where these files do not
#: exist (``DF-9-2-A``), so a module-level ``Path`` resolution here would ship a wheel that
#: cannot import.
DETECTOR_TUNING_PATHS: tuple[str, ...] = (
    "argus/detectors",
    "argus/precision/replay_harness.py",
)

#: AC4.4 — the rule, written down where the next author will read it (the ``SOURCING_RULE``
#: / ``_REMEDY`` precedent), and quoted verbatim in the failure message of the guard that
#: enforces it, so the remedy is discoverable from the red output.
SEAL_CITATION_RULE = (
    f"ANY COMMIT TOUCHING A DECLARED DETECTOR-TUNING PATH {list(DETECTOR_TUNING_PATHS)!r} "
    f"THAT IS NOT AN ANCESTOR OF THE SEAL COMMIT MUST SAY WHICH PARTITION ITS EVIDENCE CAME "
    f"FROM. Add a trailer line to the commit message reading exactly "
    f"'{SEAL_CITATION_TRAILER}: <value>', where <value> is one of "
    f"{list(SEAL_CITATION_VALUES)!r}: 'sealed' if the change was informed by findings from a "
    f"SEALED member — which is a disclosure, not a prohibition, and is what makes the "
    f"contamination visible later; 'open' if it was informed by findings from the OPEN "
    f"partition, which is where tuning is supposed to happen; 'none' if no corpus evidence "
    f"informed it at all. THE POINT IS THE COMPARISON. The public benchmark-contamination "
    f"literature's whole method is comparing performance across a public development split "
    f"and a held-out evaluation split, and that comparison is only possible if each change "
    f"says which side it learned from. A change that cites nothing is indistinguishable from "
    f"a change that was fitted to the exam. Amending the rule to make a red commit green is "
    f"the corpus-shopping failure mode with an extra step; the remedy is always to write the "
    f"trailer."
)

_CITATION_RE = re.compile(
    rf"^{re.escape(SEAL_CITATION_TRAILER)}:[ \t]*(?P<value>\S+)[ \t]*$",
    re.MULTILINE,
)

#: A 40-character lowercase hex sha. The same shape ``tests/corpus/_manifest.py`` validates
#: at construction — stated here too because this module may never resolve that manifest
#: (AR8 / ``DF-9-2-A``) and a rule that keys on a pin must be able to refuse a non-pin.
_SHA_LENGTH = 40
_SHA_ALPHABET = frozenset("0123456789abcdef")


def partition_meaning(partition: str) -> str:
    """The registered meaning of *partition* — RAISES on an unregistered member.

    PURE (AR8): a dict lookup. No I/O, no clock.

    Raises:
        UnregisteredPartition: *partition* is not in :data:`PARTITION_VALUES`.
    """
    try:
        return PARTITION_VALUES[partition]
    except KeyError:
        raise UnregisteredPartition(
            f"{partition!r} is not a registered corpus partition. The closed vocabulary is "
            f"{sorted(PARTITION_VALUES)!r}. Adding a fourth partition is a protocol "
            f"decision, not an implementation detail — an unregistered partition would let "
            f"a member be counted into, or out of, the sealed population under a name "
            f"nobody defined."
        ) from None


def partition_of(commit_sha: str, *, has_prior_output: bool) -> str:
    """THE partition rule (AC1.1) — a pure function of a pin and the prior-output override.

    The two conjuncts, in order, are :data:`SEAL_RULE_DERIVATION`'s and are written here
    once. Nothing recomputes them at a call site: ``CorpusMemberSpec.partition`` derives
    from this function, ``gate_disclosure`` publishes what that property returns, and the
    §5 condition reads the published value.

    PURE (AR8): integer arithmetic over two arguments. **No I/O, no clock, no network, and
    no manifest resolution** — in particular the prior-output fact arrives as an ARGUMENT
    rather than being looked up here, because looking it up would mean reading a committed
    adjudication set from disk inside a predicate the gate depends on.

    Args:
        commit_sha: the member's PINNED commit sha, full 40-character lowercase hex.
        has_prior_output: whether Argus output over this member already existed when the
            seal was taken. ``True`` short-circuits to ``pre-seal``, unconditionally.

    Returns:
        One of :data:`PARTITION_VALUES`' keys.

    Raises:
        UnsealablePin: *commit_sha* is not a full 40-character lowercase hex sha.
    """
    if len(commit_sha) != _SHA_LENGTH or not set(commit_sha) <= _SHA_ALPHABET:
        raise UnsealablePin(
            f"{commit_sha!r} is not a full {_SHA_LENGTH}-character lowercase hex commit "
            f"sha, so it has no partition. The seal is a per-row function OF THE PIN: "
            f"reading an unvalidated string as an integer either raises or, worse, succeeds "
            f"on a shortened sha and answers a question about a different number — and a "
            f"sha-ordered rule over unvalidated shas is not mechanically reproducible. Pin "
            f"the member at a full commit sha in tests/corpus/_manifest.py; do NOT relax "
            f"this check."
        )
    if has_prior_output:
        # ⛔ THE OVERRIDE, and it is not decorative. Two of the members that already carried
        # Argus output when this rule was frozen have ODD pins, and one of them supplied a
        # quarter of the committed record's judged findings. The bisection ALONE would have
        # declared two already-audited members "sealed". A holdout that has already been
        # peeked at is not a holdout.
        return PARTITION_PRE_SEAL
    return PARTITION_SEALED if int(commit_sha, 16) % 2 == 1 else PARTITION_OPEN


def sealed_member_floor(validation_set_floor_n: int) -> int:
    """The minimum number of distinct SEALED contributing members — 16.1's floor, RESOLVED.

    It **is** :func:`~argus.precision.gate_breadth.contributing_member_floor`, called rather
    than copied (AR7). See :data:`SEALED_MEMBER_FLOOR_DERIVATION` for why the two conditions
    share one floor and why a seal-specific constant was rejected.

    PURE (AR8). Raises whatever that function raises for a vacuous locked floor, unchanged —
    a floor no population could fail is refused at its own seam, once.
    """
    return contributing_member_floor(validation_set_floor_n)


def member_partitions(members: Sequence[Mapping[str, str]]) -> dict[str, str]:
    """The partition of every corpus member the decision carries — RAISES on an omission.

    *members* is the ``ratified_members`` sequence :func:`decide_gate` already receives, in
    which :func:`~argus.precision.gate_disclosure.ratified_corpus_members` has already put
    each row's derived ``partition``. This reads it; it never re-derives it, because a
    second derivation is a second answer to one question.

    PURE (AR8): a fold over mappings.

    Raises:
        MissingMemberPartition: a member carries no ``partition`` key, or carries one
            outside :data:`PARTITION_VALUES`.
    """
    resolved: dict[str, str] = {}
    for member in members:
        member_id = str(member.get("member_id", ""))
        if "partition" not in member:
            raise MissingMemberPartition(
                f"corpus member {member_id!r} reached protocol §5's seal condition carrying "
                f"no 'partition' key; it carries {sorted(member)!r}. The partition is "
                f"DERIVED from the member's own pin by gate_seal.partition_of and published "
                f"on the row by gate_disclosure.ratified_corpus_members — it is never "
                f"defaulted here, because defaulting it would publish a partition nobody "
                f"derived on the surface that decides which evidence may gate."
            )
        partition = str(member["partition"])
        partition_meaning(partition)
        resolved[member_id] = partition
    return resolved


@dataclass(frozen=True)
class SealAssessment:
    """Protocol §5's seal arm, MEASURED — with the sentences the record publishes.

    Every count is READ from the concentration disclosure the decision publishes and from
    the partitions the decision already carries, never recounted (AR7, AC3.3).
    """

    contributing_member_ids: tuple[str, ...]
    sealed_contributing_member_ids: tuple[str, ...]
    open_contributing_member_ids: tuple[str, ...]
    pre_seal_contributing_member_ids: tuple[str, ...]
    unpartitioned_contributing_member_ids: tuple[str, ...]
    corpus_partition_counts: tuple[tuple[str, int], ...]
    sealed_member_floor: int
    adjudicated_population: int
    population_source: str
    holds: bool
    requirement: str
    measured: str
    what_would_close_it: str
    unevaluable_reason: str

    @property
    def sealed_contributing_member_count(self) -> int:
        return len(self.sealed_contributing_member_ids)

    @property
    def contributing_member_count(self) -> int:
        return len(self.contributing_member_ids)

    @property
    def sealed_corpus_member_count(self) -> int:
        """How many members of the corpus this decision measured are SEALED at all.

        The number that tells a reader whether ``0 sealed contributions`` means *no sealed
        member was in the population* or *sealed members were audited and emitted nothing*
        (AC3.4). Two very different claims; one number separates them.
        """
        return dict(self.corpus_partition_counts).get(PARTITION_SEALED, 0)

    def to_payload(self) -> dict[str, object]:
        """The canonical mapping — serialized through ``argus.store.canonical`` upstream."""
        return {
            "condition_id": SEAL_CONDITION_ID,
            "contributing_member_count": self.contributing_member_count,
            "contributing_member_ids": list(self.contributing_member_ids),
            "sealed_contributing_member_count": self.sealed_contributing_member_count,
            "sealed_contributing_member_ids": list(self.sealed_contributing_member_ids),
            "open_contributing_member_ids": list(self.open_contributing_member_ids),
            "pre_seal_contributing_member_ids": list(self.pre_seal_contributing_member_ids),
            "unpartitioned_contributing_member_ids": list(
                self.unpartitioned_contributing_member_ids
            ),
            "corpus_partition_counts": [
                {"partition": partition, "members": count}
                for partition, count in self.corpus_partition_counts
            ],
            "sealed_corpus_member_count": self.sealed_corpus_member_count,
            "sealed_member_floor": self.sealed_member_floor,
            "sealed_member_floor_derivation": SEALED_MEMBER_FLOOR_DERIVATION,
            "seal_rule_derivation": SEAL_RULE_DERIVATION,
            "partition_vocabulary": sorted(PARTITION_VALUES),
            "adjudicated_population": self.adjudicated_population,
            "population_source": self.population_source,
            "holds": self.holds,
            "requirement": self.requirement,
            "measured": self.measured,
            "what_would_close_it": self.what_would_close_it,
            "unevaluable_reason": self.unevaluable_reason,
        }


def _partition_roll_call(partitions: Mapping[str, str]) -> tuple[tuple[str, int], ...]:
    """Every REGISTERED partition with its member count — a zero is STATED, never absent.

    Folded over the whole closed vocabulary rather than over the values present, because
    *"the corpus holds 0 sealed members"* and *"the corpus does not mention sealed members"*
    read identically to a human and are different claims. PURE (AR8).
    """
    return tuple(
        (partition, sum(1 for value in partitions.values() if value == partition))
        for partition in sorted(PARTITION_VALUES)
    )


def assess_seal(
    concentration: ConcentrationDisclosure,
    *,
    partitions: Mapping[str, str],
    validation_set_floor_n: int,
    population_source: str,
) -> SealAssessment:
    """Evaluate §5's seal arm over the concentration the decision ALREADY published.

    *concentration* is the very instance the decision serializes and *partitions* are the
    partitions it already carries on its corpus members, so the threshold, the disclosure
    and the published partition are one set of facts. Recounting any of them here would
    create a second answer to one question, and a disagreement between a disclosure and the
    threshold derived from it is invisible to every reader of either (AC3.3).

    *population_source* names WHICH population was counted (AC3.4), for the reason
    :func:`~argus.precision.gate_breadth.assess_breadth` records: the concentration is
    derived from the committed record's LIVE rows, while the most recent adjudication set's
    EMITTED blocking population is a different — possibly empty — set.

    PURE (AR8): reads two frozen mappings and returns a frozen dataclass.

    Raises:
        VacuousSealError: *partitions* is empty, so the corpus the seal was assessed over
            holds no members at all and every sentence below would be about nothing.
    """
    if not partitions:
        raise VacuousSealError(
            "protocol §5's seal condition was assessed over a corpus carrying ZERO "
            "members, so 'k sealed of none' has no denominator and the condition would "
            "report a measured shortfall over a population that does not exist "
            "(non-vacuity floor, AI-E11-1). Pass the ratified members the decision carries."
        )
    floor = sealed_member_floor(validation_set_floor_n)
    contributing = tuple(concentration.contributing_member_ids)

    def _in(partition: str) -> tuple[str, ...]:
        return tuple(sorted(m for m in contributing if partitions.get(m) == partition))

    sealed = _in(PARTITION_SEALED)
    open_side = _in(PARTITION_OPEN)
    pre_seal = _in(PARTITION_PRE_SEAL)
    unpartitioned = tuple(sorted(m for m in contributing if m not in partitions))
    counts = _partition_roll_call(partitions)
    corpus_size = len(partitions)
    sealed_in_corpus = dict(counts).get(PARTITION_SEALED, 0)
    holds = len(sealed) >= floor
    short_by = max(0, floor - len(sealed))

    requirement = (
        f"protocol §5 as amended 2026-08-20 (Story 16.2; sprint change proposal "
        f"2026-08-20 §4.3(2)): the precision ratio is EVALUABLE only over a population "
        f"drawn from at least {floor} DISTINCT CONTRIBUTING member(s) lying in the SEALED "
        f"partition — members over which no Argus output existed when the seal was taken, "
        f"so the detector cannot have been tuned against them. The floor is "
        f"{SEALED_MEMBER_FLOOR_DERIVATION}. The partition rule is: {SEAL_RULE_DERIVATION} "
        f"This condition makes clearing HARDER and can never make it easier: it adds a "
        f"requirement, it does not narrow the population, and every finding from every "
        f"partition stays recorded and stays disclosed."
    )

    roll_call = (
        "; ".join(f"{member}: {partitions.get(member, 'NO PARTITION')}" for member in contributing)
        or "none"
    )
    corpus_split = ", ".join(f"{count} {partition}" for partition, count in counts)
    if sealed_in_corpus == 0:
        discrimination = (
            f"⛔ READ THIS BEFORE READING THE COUNT: the corpus this condition measured holds "
            f"ZERO members in the sealed partition, so {len(sealed)} sealed contribution(s) "
            f"means NO SEALED MEMBER WAS IN THE POPULATION AT ALL — it does NOT mean sealed "
            f"members were audited and emitted nothing. Those are different claims and this "
            f"sentence exists so no reader has to guess which one happened."
        )
    elif not sealed:
        discrimination = (
            f"⛔ READ THIS BEFORE READING THE COUNT: the corpus this condition measured holds "
            f"{sealed_in_corpus} sealed member(s) and NONE of them contributed a finding to "
            f"the population. The zero is a MEASURED SILENCE over a population that was "
            f"present, not an absent population."
        )
    else:
        discrimination = (
            f"The corpus this condition measured holds {sealed_in_corpus} sealed member(s), "
            f"{len(sealed)} of which contributed at least one finding to the population."
        )
    unregistered_clause = (
        ""
        if not unpartitioned
        else (
            f" ⚠️ {len(unpartitioned)} contributing member(s) carry NO partition on this "
            f"decision's corpus and are counted as NOT sealed, named rather than folded "
            f"silently into 'open': {', '.join(unpartitioned)}."
        )
    )
    measured = (
        f"seal = {len(sealed)} SEALED contributing member(s) of "
        f"{len(contributing)} contributing, against a floor of {floor}; counted over the "
        f"{concentration.adjudicated_population} LIVE row(s) of {population_source} — NOT "
        f"over the emitted blocking population of the most recent adjudication set, which "
        f"is a different population and may be empty. Every contributing member with its "
        f"partition: [{roll_call}]. The corpus measured holds {corpus_size} member(s): "
        f"{corpus_split}. {discrimination}{unregistered_clause} "
        + (
            "The seal floor is MET."
            if holds
            else f"The seal floor is NOT met — short by {short_by} sealed member(s)."
        )
    )
    what_would_close_it = (
        (
            "already met; it re-opens the moment the sealed contributing population narrows "
            "back below the floor — by a superseding judgement, a withdrawn member, or a "
            "re-measurement that emits from fewer sealed members"
        )
        if holds
        else (
            f"{short_by} further member(s) of the SEALED partition must be ratified by the "
            f"protocol §6 R2 operator act AND must each contribute at least ONE adjudicated "
            f"finding, taking the sealed contributing count from {len(sealed)} to {floor}. "
            f"⛔ RATIFYING ONLY OPEN-PARTITION MEMBERS LEAVES THIS CONDITION PERMANENTLY "
            f"FAILED, and an operator must be told that BEFORE taking the act rather than "
            f"discover it after. NOT closable by re-partitioning a member — the partition is "
            f"DERIVED from the pin and cannot change without changing which bytes are "
            f"audited. NOT closable by narrowing the corpus, dropping a non-contributing "
            f"member or re-weighting one: protocol §5 and Story 13.3 / AC5 forbid every one "
            f"of those. NOT closable by lowering the floor, which is shared with §5's "
            f"breadth arm and derived from the ONE locked N. The honest closure is evidence "
            f"from members the tool was never tuned against"
        )
    )
    unevaluable_reason = (
        f"EVIDENCE NOT DRAWN FROM THE SEALED PARTITION — the adjudicated population draws "
        f"on {len(sealed)} sealed contributing member(s) against protocol §5's seal floor of "
        f"{floor}, so the ratio measures a population the detector may have been tuned "
        f"against and is not a statement about the tool"
    )
    return SealAssessment(
        contributing_member_ids=contributing,
        sealed_contributing_member_ids=sealed,
        open_contributing_member_ids=open_side,
        pre_seal_contributing_member_ids=pre_seal,
        unpartitioned_contributing_member_ids=unpartitioned,
        corpus_partition_counts=counts,
        sealed_member_floor=floor,
        adjudicated_population=concentration.adjudicated_population,
        population_source=population_source,
        holds=holds,
        requirement=requirement,
        measured=measured,
        what_would_close_it=what_would_close_it,
        unevaluable_reason=unevaluable_reason,
    )


def sealed_precision_gate_status(
    *,
    fold: AdjudicatedPrecision,
    seal: SealAssessment,
    protocol_path: str,
    independence_note: str | None = None,
) -> str:
    """The gate-status sentence when the SEAL is what makes precision unevaluable.

    The exact analogue of
    :func:`~argus.precision.gate_breadth.effective_precision_gate_status`, and — like it —
    it renders through the SAME
    :func:`~argus.precision.replay_harness.precision_gate_status_for` the fold used, never
    through a second status function (AR7). Publishing ``precision.evaluable = True`` beside
    a §5 precision verdict of ``UNEVALUABLE`` is the ``DF-9-2-B`` false-subject class on the
    surface that publishes the externalization gate.

    **Why this is a sibling rather than a widened breadth function (DN-16-2-8).** Story
    16.2's write set holds ``argus/precision/gate_breadth.py`` BYTE-UNCHANGED — *"read it;
    do not edit its subject"* — and that module's subject is the breadth arm. Giving its
    renderer a second reason would make it not-about-breadth. Both functions are thin
    wrappers over one shared renderer, and neither authors a status string of its own.

    When the seal does not change the answer the fold's OWN string is returned
    BYTE-FOR-BYTE rather than re-rendered, so the amendment is provably inert on a
    population it does not bind (NFR-P1 byte-stability of the precision surface).

    PURE (AR8).
    Story 16.5: ``independence_note`` is FORWARDED verbatim, never derived here (AC7.1a).
    """
    if fold.evaluable == (fold.evaluable and seal.holds):
        return fold.gate_status
    return precision_gate_status_for(
        precision=fold.precision,
        n=fold.n,
        provisional=fold.provisional,
        protocol_path=protocol_path,
        floor_n=fold.floor_n,
        population_label="eligible validation-set repositories",
        evaluable=False,
        unevaluable_reason=seal.unevaluable_reason,
        independence_note=independence_note,
    )


def seal_blocked_reason(seal: SealAssessment) -> str:
    """The ``outcome_reason`` a decision BLOCKED on the seal publishes (AC3.2).

    It lives here rather than inline in :func:`~argus.precision.gate_decision.decide_gate`
    for DN-16-1-3's reason: the constants, the predicate and the measured and closure
    SENTENCES are this module's subject, and ``gate_decision`` builds the
    ``ConditionResult``. One direction only.

    **Why BLOCKED and not NOT_CLEARED, said in the sentence itself.** ``NOT_CLEARED`` may be
    recorded only when the measurement RAN, and a ratio over evidence the detector may have
    been tuned against did not produce a measurement of the tool — it produced a measurement
    of the fit. ``GATE_OUTCOMES`` stays CLOSED at three; no terminal state is invented.

    PURE (AR8).
    """
    return (
        f"the precision ratio is NOT EVALUABLE as a statement about the tool: protocol §5's "
        f"SEAL condition, as amended 2026-08-20 (Story 16.2), does not hold. {seal.measured} "
        f"A ratio computed over evidence the detector may have been tuned against cannot "
        f"distinguish a tool that got BETTER from a tool that got FITTED, and nothing "
        f"downstream can recover the difference once the figure is quoted. This is NOT a "
        f"shortfall and NOT a failed measurement: the partition was frozen, in code and in "
        f"git, BEFORE any Argus output over any member of it existed, and it can only make "
        f"clearing harder."
    )


def seal_closure_path(seal: SealAssessment) -> tuple[str, ...]:
    """What it would take, in COUNTABLE terms — a BLOCKED decision with no closure path raises.

    The last leg is stated as a REFUSAL rather than left to a reader's restraint, because
    the tempting closure here is not lowering a threshold — it is quietly re-partitioning a
    member, which the derivation makes impossible and which this sentence makes visible.

    PURE (AR8).
    """
    return (
        seal.what_would_close_it,
        "re-run scripts/build_gate_decision.py so the record carries the sealed-partition "
        "evidence, and re-run this decision",
        "NOT closable by amending the partition rule, by re-pinning a member, or by "
        "lowering the seal floor: a partition redrawn after seeing the result it produced is "
        "corpus-shopping with extra steps (protocol §5; Story 13.3 / AC5), and the whole "
        "value of this condition is that the rule was frozen before any output existed",
    )


def cites_partition(commit_message: str) -> bool:
    """AC4.3's predicate: does *commit_message* cite the partition its evidence came from?

    Isolated as a pure function of a STRING precisely so it can be driven to BOTH outcomes
    independently of any commit population. At the moment this rule lands the post-seal
    detector-commit population is EMPTY, so a guard that only iterated it would pass forever
    over nothing — this project's signature defect. The predicate is therefore watched
    FAILING over synthetic messages, not only passing.

    The trailer must be a WHOLE LINE reading ``Evidence-partition: <value>`` with *value* in
    :data:`SEAL_CITATION_VALUES`. A mention of the word "sealed" in prose is deliberately
    NOT a citation: the point is a machine-checkable claim a later comparison can rely on,
    and prose that happens to contain a partition name is the shape that makes an
    unenforceable rule look enforced.

    PURE (AR8): a regex over a string. No I/O, no clock, no git.
    """
    return any(
        match.group("value") in SEAL_CITATION_VALUES
        for match in _CITATION_RE.finditer(commit_message)
    )
