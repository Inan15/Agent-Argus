"""PURE pattern-matched HITL STOP/PROCEED escalation gate + the frozen schema.

Drivers: ArgusAgent-FR-23 (HITL STOP/PROCEED gate — the trigger is PATTERN-MATCHED (a
deterministic rule match over the findings / coverage ledger / candidate
verdict-state), NOT an LLM judgment; the gate DEFAULTS TO STOP; on a configured
gate-timeout window with no human response it PARKS AT STOP and NEVER
auto-PROCEEDs), ArgusAgent-FR-24-support (the resolved outcome + resolution kind this
gate returns are what the append-only :mod:`decision_record` persists — incl. the
default/timeout STOP that is logged even when the full human decision is deferred),
ArgusAgent-NFR-D1/D2 (the escalation resolution is DETERMINISTIC + ZERO-LLM-token — a
pure fold; this module dispatches NO LLM and imports NO provider surface),
ArgusAgent-NFR-S1 (an escalation carries ONLY the decision, the pattern-matched trigger
provenance (rule-id / reason token), the triggering finding-id(s) / locator
provenance, and a decider-id token — NEVER source bytes / a secret value / an
absolute host path), ArgusAgent-AR4 (content-derived ids — the decision-id is the
content hash of the canonical decision payload; NO ``uuid4`` / clock / counter /
``os.getpid`` / random; NO float in any payload), ArgusAgent-AR8 (PURE — no I/O, no
clock, no LLM, no random; the byte read/write is the :mod:`decision_record` impure
shell, NOT this module), ArgusAgent-AR10 (typed failure — a genuinely malformed argument
raises a typed, NAMED :class:`EscalationError`; empty/None findings / an empty
ledger degrade to a deterministic STOP, never a bare traceback).

Verification area ArgusAgent-HITL (``TC-ArgusAgent-HITL-001-NN`` — index from -01).

DN-V1-DETERMINISTIC — the escalation trigger is PATTERN-MATCHED, never LLM-judgment
--------------------------------------------------------------------------------
Per the FR23 lock + the Epic-6 determinism quarantine (the 6.4 Prosecutor is the
exact precedent), the V1 escalation gate is a PURE recording-consumer: it folds the
frozen findings + the candidate verdict-state into a deterministic ``bool``
(fired?) via a configured :class:`EscalationRule`, and resolves the
``(fired, human_decision, timeout_elapsed)`` triple into a frozen
:class:`EscalationResolution`. It dispatches NO LLM. A richer LLM-driven escalation
adjudicator is the documented FORWARD seam behind the 6.1 ``LLMDispatchPort`` (a
``FakeDispatch`` for zero-token tests if any seam is ever wired) — NEVER a direct
provider import of any kind, NEVER the V1 default. This module imports NO
providers and NO FastAPI (the no-web-imports + no-LLM gates stay green).

DN-RESOLUTION — the FR23 fail-safe matrix (the keystone, read twice)
--------------------------------------------------------------------
The gate resolves ``(fired, human_decision, timeout_elapsed)`` deterministically:

  - NOT fired                                  → not escalated (``None``; pass-through,
                                                 no record required).
  - fired + no decision + not-timed-out        → **STOP** (``default_stop``) — silence
                                                 blocks; it never ships a verdict.
  - fired + no decision + timeout-elapsed       → **STOP** (``timeout_parked_stop``) —
                                                 NEVER auto-PROCEED (the keystone; a
                                                 slow/absent human never becomes an
                                                 auto-PROCEED).
  - fired + human decision (STOP or PROCEED)    → **that decision** (``human_decision``).

The default is STOP; the timeout parks at STOP; only an explicit human decision can
PROCEED. There is NO code path that resolves to PROCEED without a human decision.
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from argus.ledger.recording import Recording
from argus.store.envelope import compute_content_hash
from argus.verdict.verdict_gate import AuditVerdict, Verdict

__all__ = [
    "ESCALATION_SCHEMA_VERSION",
    "EscalationError",
    "EscalationOutcome",
    "ResolutionKind",
    "EscalationRule",
    "EscalationTrigger",
    "HumanDecision",
    "EscalationResolution",
    "escalation_fires",
    "resolve_escalation",
    "decision_record_payload",
]

# Single localized source for this contract's schema version (additive-only;
# part of the hashed decision payload — a bump deliberately changes the hash).
ESCALATION_SCHEMA_VERSION = "1"


class EscalationError(ValueError):
    """Raised on a genuinely malformed argument to the escalation gate (AR10).

    A ``ValueError`` subclass localized to this module (mirroring
    ``ProsecutorError`` / ``StoreIntegrityError`` / ``WorkspaceContainmentError``).
    Its message names the failing argument only — it carries NO source bytes
    (NFR-S1). A degraded per-element shape (empty/None findings, an empty ledger) is
    NOT a crash — it degrades to a deterministic STOP; only a structurally wrong
    top-level argument (a non-``AuditVerdict`` verdict, a non-``EscalationRule``
    rule, a decision whose ``outcome`` is not an :class:`EscalationOutcome`) raises.
    """


class EscalationOutcome(str, enum.Enum):
    """The closed STOP/PROCEED escalation-outcome vocabulary (FR23).

    A ``str``-valued enum (mirroring ``Verdict`` / ``CoverageDepth``) so members
    serialize verbatim as their token through ``store/canonical.dumps``. EXACTLY two
    members — the human decision is STOP or PROCEED; a resolved-but-pending state is
    represented as a STOP-parked resolution (``timeout_parked_stop``), NOT a third
    member.
    """

    STOP = "STOP"
    PROCEED = "PROCEED"


class ResolutionKind(str, enum.Enum):
    """How the escalation outcome was reached (the FR23 fail-safe provenance).

    - ``default_stop`` — fired, no human decision, not-timed-out → STOP (silence
      blocks).
    - ``timeout_parked_stop`` — fired, no human decision, timeout elapsed → STOP
      (parked; NEVER auto-PROCEED — the keystone).
    - ``human_decision`` — fired, an explicit human STOP/PROCEED decision was
      supplied.
    """

    DEFAULT_STOP = "default_stop"
    TIMEOUT_PARKED_STOP = "timeout_parked_stop"
    HUMAN_DECISION = "human_decision"


class EscalationRule(BaseModel):
    """A frozen, deterministic pattern-match rule over findings / verdict-state (FR23).

    ``frozen=True, extra="forbid"`` (the Epic-1..6 contract precedent). The rule is
    a PATTERN — a set of finding ``rule_id`` tokens to match and/or a set of
    candidate ``Verdict`` states to match — NOT an LLM prompt. The gate fires when a
    finding whose ``rule_id`` is in :attr:`match_rule_ids` is present OR the
    candidate verdict is in :attr:`match_verdicts`. A rule with BOTH sets empty
    never fires (a NO-OP rule — no escalation is configured).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str = Field(..., description="Provenance id for this escalation rule (a token, not source).")
    reason: str = Field(
        default="", description="Optional structured reason token (a provenance token, never source bytes)."
    )
    match_rule_ids: tuple[str, ...] = Field(
        default=(), description="Finding rule_ids that fire the escalation (a deterministic pattern)."
    )
    match_verdicts: tuple[Verdict, ...] = Field(
        default=(), description="Candidate verdict states that fire the escalation (a deterministic pattern)."
    )


class EscalationTrigger(BaseModel):
    """The pattern-matched trigger provenance for a fired escalation (NFR-S1).

    ``frozen=True, extra="forbid"``. Carries ONLY provenance tokens: the escalation
    rule-id, its reason token, and the triggering finding-id(s) + locator
    provenance (file path + line span tokens) — NEVER source bytes / a secret value
    / an absolute host path. This is the ``trigger`` slice of the decision-record
    payload.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str = Field(..., description="The EscalationRule rule_id that fired (a provenance token).")
    reason: str = Field(default="", description="Structured reason token (no source bytes — NFR-S1).")
    finding_ids: tuple[str, ...] = Field(
        default=(), description="recording_id(s) of the finding(s) that matched the pattern (provenance)."
    )
    locator_provenance: tuple[str, ...] = Field(
        default=(),
        description="Locator provenance tokens '<file_path>:<start>-<end>' — file/line only, never source (NFR-S1).",
    )


class HumanDecision(BaseModel):
    """A supplied human STOP/PROCEED decision (FR23 / FR24).

    ``frozen=True, extra="forbid"``. Carries the decision outcome + an opaque
    decider-id token (an operator/role id supplied by the caller — NOT free text
    that could leak content, NFR-S1). Absent (``None``) for a default/timeout STOP.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    outcome: EscalationOutcome = Field(..., description="The human decision: STOP or PROCEED.")
    decider_id: str = Field(..., description="Opaque decider-id token (operator/role id — NFR-S1, never source).")


class EscalationResolution(BaseModel):
    """The frozen, pure result of resolving one fired escalation (FR23 / AR8 / NFR-M2).

    ``frozen=True, extra="forbid"`` (the Epic-1..6 contract precedent). Carries the
    resolved outcome (STOP/PROCEED), the resolution kind (the FR23 fail-safe
    provenance), the pattern-matched trigger, the decider-id token (``None`` for a
    default/timeout STOP), and a deterministic CONTENT-DERIVED decision-id (the
    content hash of the canonical decision payload — NO ``uuid4``/clock/counter/
    random, AR4/AR11). PURE — no I/O, no clock, no LLM, no random, no float.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=ESCALATION_SCHEMA_VERSION, description="Escalation schema version (part of the hashed payload)."
    )
    outcome: EscalationOutcome = Field(..., description="The resolved escalation outcome (STOP/PROCEED).")
    resolution_kind: ResolutionKind = Field(..., description="How the outcome was reached (FR23 fail-safe provenance).")
    trigger: EscalationTrigger = Field(..., description="The pattern-matched trigger provenance (NFR-S1).")
    decider_id: str | None = Field(
        default=None, description="The decider-id token for a human decision; None for a default/timeout STOP."
    )
    decision_id: str = Field(
        ..., description="Deterministic CONTENT-DERIVED decision-id (hash of the canonical payload — AR4/AR11)."
    )

    def to_payload(self) -> dict[str, Any]:
        """Return the canonical decision-record payload (the bytes the record persists).

        A JSON-primitive dict (enums → their ``str`` value) — exactly what the
        :mod:`decision_record` writer wraps in the content-hashed envelope. PURE.
        """
        return self.model_dump(mode="json")


def _locator_provenance(finding: Recording) -> tuple[str, ...]:
    """Return '<file_path>:<start>-<end>' provenance tokens for a finding's locators.

    File path + line span ONLY — never source bytes (NFR-S1). The ``ast_span`` (a
    structured seam token) is NOT included here because a detector MAY carry a
    self-describing seam token there; the trigger provenance is deliberately the
    minimal file/line locator. PURE.
    """
    return tuple(
        f"{loc.file_path}:{loc.start_line}-{loc.end_line}" for loc in finding.locators
    )


def escalation_fires(
    rule: EscalationRule,
    *,
    findings: tuple[Recording, ...] | list[Recording] | None = (),
    verdict: AuditVerdict | None = None,
) -> EscalationTrigger | None:
    """Evaluate the PURE pattern match — return the trigger if it fires, else ``None`` (FR23).

    The escalation FIRES when either pattern matches deterministically:
      (a) a finding whose ``rule_id`` is in ``rule.match_rule_ids`` is present, OR
      (b) the candidate ``verdict.verdict`` is in ``rule.match_verdicts``.

    Zero-LLM-token: no LLM is dispatched, no clock/random is read (AR8). Degrades
    (never raises) on empty/None findings and an absent verdict — an empty universe
    simply does not fire. A genuinely malformed argument (a non-``EscalationRule``
    rule, a non-``AuditVerdict`` verdict) raises a typed :class:`EscalationError`
    (AR10). A malformed per-element finding is SKIPPED (never a crash).

    Returns:
        An :class:`EscalationTrigger` carrying the rule-id / reason + the matched
        finding-id(s) + their locator provenance when the escalation fires; ``None``
        when it does not (pass-through — no record required).

    Raises:
        EscalationError: a non-``EscalationRule`` ``rule`` or a non-``AuditVerdict``
            (and non-``None``) ``verdict`` — a typed failure, never a leak (AR10).
    """
    if not isinstance(rule, EscalationRule):
        raise EscalationError(
            f"rule must be an EscalationRule, got {type(rule).__name__!r}"
        )
    if verdict is not None and not isinstance(verdict, AuditVerdict):
        raise EscalationError(
            f"verdict must be an AuditVerdict or None, got {type(verdict).__name__!r}"
        )

    match_rule_ids = frozenset(rule.match_rule_ids)
    match_verdicts = frozenset(rule.match_verdicts)

    matched_finding_ids: list[str] = []
    locator_tokens: list[str] = []
    for raw in findings or ():
        if not isinstance(raw, Recording):
            # A malformed per-element finding is skipped, never a crash (AR10).
            continue
        if raw.rule_id in match_rule_ids:
            matched_finding_ids.append(raw.recording_id)
            locator_tokens.extend(_locator_provenance(raw))

    verdict_matches = verdict is not None and verdict.verdict in match_verdicts

    if not matched_finding_ids and not verdict_matches:
        return None

    # Sort the provenance deterministically (AR4 — no input/iteration-order reliance).
    return EscalationTrigger(
        rule_id=rule.rule_id,
        reason=rule.reason,
        finding_ids=tuple(sorted(matched_finding_ids)),
        locator_provenance=tuple(sorted(set(locator_tokens))),
    )


def _content_derived_decision_id(payload: dict[str, Any]) -> str:
    """The deterministic decision-id = content hash of the canonical payload (AR4/AR11).

    REUSES the 1.1 ``compute_content_hash`` (the single hasher over the single
    canonical serializer) — NO ``uuid4`` / clock / counter / random. Two runs over
    the same decision produce the same id. PURE.
    """
    return compute_content_hash(payload)


def resolve_escalation(
    trigger: EscalationTrigger,
    *,
    human_decision: HumanDecision | None = None,
    timeout_elapsed: bool = False,
) -> EscalationResolution:
    """Resolve a FIRED escalation into a frozen :class:`EscalationResolution` (DN-RESOLUTION).

    The FR23 fail-safe matrix (the keystone):

      - human decision present → that decision (``human_decision``).
      - no decision + timeout-elapsed → **STOP** (``timeout_parked_stop``) — NEVER
        auto-PROCEED.
      - no decision + not-timed-out → **STOP** (``default_stop``) — silence blocks.

    There is NO code path that resolves to PROCEED without an explicit human
    decision. The decision-id is CONTENT-DERIVED (the hash of the canonical payload,
    AR4/AR11) — computed AFTER the outcome/kind/decider are fixed, so it is stable
    across two runs over the same inputs.

    PURE — no I/O, no clock, no LLM, no random, no float. A genuinely malformed
    argument raises a typed :class:`EscalationError` (AR10).

    Raises:
        EscalationError: a non-``EscalationTrigger`` ``trigger`` or a
            non-``HumanDecision`` (and non-``None``) ``human_decision`` — a typed
            failure, never a leak (AR10).
    """
    if not isinstance(trigger, EscalationTrigger):
        raise EscalationError(
            f"trigger must be an EscalationTrigger, got {type(trigger).__name__!r}"
        )
    if human_decision is not None and not isinstance(human_decision, HumanDecision):
        raise EscalationError(
            f"human_decision must be a HumanDecision or None, got "
            f"{type(human_decision).__name__!r}"
        )

    if human_decision is not None:
        outcome = human_decision.outcome
        kind = ResolutionKind.HUMAN_DECISION
        decider_id: str | None = human_decision.decider_id
    elif timeout_elapsed:
        # The keystone: a timed-out gate with no human response PARKS at STOP.
        outcome = EscalationOutcome.STOP
        kind = ResolutionKind.TIMEOUT_PARKED_STOP
        decider_id = None
    else:
        # Silence blocks — the default-STOP fail-CLOSED outcome.
        outcome = EscalationOutcome.STOP
        kind = ResolutionKind.DEFAULT_STOP
        decider_id = None

    # Build the identity-bearing payload FIRST (everything but the id), hash it, then
    # stamp the content-derived decision-id onto the frozen resolution (AR4/AR11).
    identity_payload: dict[str, Any] = {
        "schema_version": ESCALATION_SCHEMA_VERSION,
        "outcome": outcome.value,
        "resolution_kind": kind.value,
        "trigger": trigger.model_dump(mode="json"),
        "decider_id": decider_id,
    }
    decision_id = _content_derived_decision_id(identity_payload)

    return EscalationResolution(
        outcome=outcome,
        resolution_kind=kind,
        trigger=trigger,
        decider_id=decider_id,
        decision_id=decision_id,
    )


def decision_record_payload(resolution: EscalationResolution) -> dict[str, Any]:
    """Return the canonical decision-record payload for a resolution (the record body).

    A thin, PURE accessor mirroring :meth:`EscalationResolution.to_payload` at the
    module level (the shape the :mod:`decision_record` writer persists). Raises a
    typed :class:`EscalationError` on a non-resolution argument (AR10).
    """
    if not isinstance(resolution, EscalationResolution):
        raise EscalationError(
            f"resolution must be an EscalationResolution, got {type(resolution).__name__!r}"
        )
    return resolution.to_payload()
