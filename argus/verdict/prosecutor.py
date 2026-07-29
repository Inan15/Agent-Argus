"""PURE adversarial Prosecutor — verdict challenge + advisory promotion + cut-edge pass.

Drivers: ArgusAgent-FR-19 (run an adversarial Prosecutor pass that challenges whether the
ledger justifies the verdict and downgrades an unearned verdict — Tier B), ArgusAgent-FR-13
(every emitted finding — incl. ``cross_partition`` — carries ≥1 verifiable locator or
is rejected, not emitted — via the EXISTING 1.5 ``build_recording``),
ArgusAgent-FR-33-support / cross-cutting #6 (advisory-by-contract: the Prosecutor OWNS the
advisory→verdict-eligible PROMOTION the 1.5/6.3/1.6 stories deferred to it — a 🔴
stands ONLY with AST corroboration AND Prosecutor sign-off; a heuristic-only finding
is NEVER promoted; the 1.6 gate's ``depth_supported is not None`` predicate is
UNCHANGED, refined UPSTREAM), ArgusAgent-CC4 (the V1 ``cross_partition`` cut-edge pass is the
mitigation for the deferred V2 cross-partition seam auditor — OI2), ArgusAgent-NFR-D1/D2 (the
Prosecutor is a PURE, zero-LLM-token recording-consumer — the V1 default path;
deterministic + reproducible), ArgusAgent-AR8 (PURE — no I/O, no clock, no LLM, no provider
import, no float), ArgusAgent-AR10 / NFR-R1 (a malformed / empty / None verdict / ledger /
findings / cut-edge → a recorded ``DegradedCondition`` or a NOT-prosecuted pass-through,
NEVER an uncaught raise; a typed ``ProsecutorError`` only on a genuinely malformed
argument), ArgusAgent-AR7 / §3.3 (REUSE the 1.6 ``evaluate_verdict`` / ``order_findings`` fold
+ the 2.4 ``CutEdge`` set + the 1.5 ``build_recording`` BY IMPORT — NO second verdict
math, NO finding fork, NO re-parse), ArgusAgent-AR4 (single canonical serializer;
content-derived ids; no clock/uuid/random/iteration-order; no float), ArgusAgent-NFR-S1 (no
source/secret bytes — cite file/callee names + structured reason tokens, NEVER source
excerpts).

Verification area ArgusAgent-PROSECUTOR (TC-ArgusAgent-PROSECUTOR-001-NN — index from -01).

DN-V1-DETERMINISTIC — the default Prosecutor path is PURE + deterministic + zero-token
--------------------------------------------------------------------------------------
Per the determinism-quarantine architecture (Decision E / NFR-D1/D2) and the 6.2
DN-V1-DETERMINISTIC precedent, the V1 Prosecutor is a pure recording-consumer: it folds
the candidate ``AuditVerdict`` + the ``CoverageLedger`` + the findings + the 2.4
``cut_edges`` + the explicit sign-off set into a deterministic, zero-token
``ProsecutionResult``. It dispatches NO LLM. A richer LLM-driven adversarial challenge
(an LLM prosecuting the verdict) is the documented FORWARD seam behind the 6.1
``LLMDispatchPort`` (a ``FakeDispatch`` for zero-token tests if any seam is wired) —
NEVER a direct ``minions_core.providers`` import, NEVER the V1 default. This module
imports NO providers and NO FastAPI (the no-web-imports + no-LLM gates stay green).

DN-PROMOTE — the advisory→verdict-eligible promotion authority (the central deliverable)
----------------------------------------------------------------------------------------
The 1.6 gate keys eligibility on ``depth_supported is not None`` and explicitly RESERVED
the eligible-finding-set refinement for "the Epic-6 Prosecutor." The 1.5 / 6.3 detectors
emit advisory findings (``advisory=True``, ``depth_supported=None``) and deferred
promotion to "the Prosecutor." This module implements that authority: an advisory finding
(``depth_supported is None``) is promoted to verdict-eligible — a NEW promoted
``Recording`` carrying a real ``depth_supported`` (a frozen model is immutable, so
``model_copy(update=...)``; the original is NOT mutated) — ONLY when BOTH hold:

  (a) the finding carries AST CORROBORATION — its locator carries a non-``None``
      ``ast_span`` (the 6.2 AST-grounded locator), the deterministic structural fact, AND
  (b) the Prosecutor SIGNS OFF on it — the finding's ``recording_id`` is an explicit
      member of the ``sign_offs`` set passed to :func:`prosecute`.

A heuristic-only finding (no AST corroboration) is NEVER promoted — the false-accusation
floor: a 🔴 is never served on a heuristic alone. AST corroboration WITHOUT sign-off is
NOT promoted — sign-off is required, not just corroboration. A finding already
verdict-eligible (``depth_supported is not None``) is left UNCHANGED.

The FR19 downgrade — only ever MORE conservative
-------------------------------------------------
The refined finding set (originals with promotions substituted + any ``cross_partition``
findings) is re-folded through the UNCHANGED ``evaluate_verdict`` / ``order_findings`` —
the Prosecutor performs NO second verdict math. The FINAL verdict is the MORE
conservative of (the candidate verdict, the re-folded verdict): a ``RELEASE_READY`` that
the re-fold turns blocking is DOWNGRADED; the Prosecutor NEVER upgrades a candidate (the
asymmetric-harm direction — an unearned green is the lethal failure, an over-cautious red
is recoverable). The downgrade is recorded with a structured rationale (reason tokens +
the promoted/seam finding ids — no source bytes, NFR-S1).

CC #4 — the ``cross_partition`` cut-edge pass (the V1 seam mitigation, OI2)
---------------------------------------------------------------------------
The 2.4 partitioner RECORDS the ``cut_edges`` (a caller in partition A whose callee is
defined in partition B) but analyzes none. This pass re-reads them and raises a
``cross_partition`` ADVISORY finding (``advisory=True``, ``rule_id="cross_partition"``,
``depth_supported=None``) for each cut a seam-spanning defect could hide in — built via
the EXISTING ``build_recording`` so it satisfies FR13 locator-or-reject the same way
every detector does. HONEST V1 LIMITATION: it SURFACES a cut as a place a defect COULD
hide over the UNRESOLVED-name cut-edge set (DF-1-4-A) — it does NOT PROVE a defect spans
the cut (the full resolved-seam auditor, name binding / scope resolution, is the reserved
V2 seam — OI2 / DF-6-3-A's resolved-call-graph scope; filed as DF-6-4-A). A repo with NO
cut edges raises NO ``cross_partition`` finding. A ``cross_partition`` finding is subject
to the SAME promotion rule (verdict-eligible only with corroboration + sign-off — and a
cut edge carries no AST span, so it is never promoted in V1).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from argus.detectors.base import (
    DegradedCondition,
    FindingDraft,
    build_recording,
)
from argus.index.partitioner import CutEdge
from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger
from argus.ledger.recording import Recording
from argus.verdict.verdict_gate import (
    AuditVerdict,
    Verdict,
    evaluate_verdict,
    order_findings,
)

__all__ = [
    "RULE_CROSS_PARTITION",
    "PROMOTED_DEPTH",
    "ProsecutorError",
    "ProsecutionResult",
    "prosecute",
]

# The single rule-id for the CC #4 cut-edge pass (frozen for 6.5/6.6).
RULE_CROSS_PARTITION = "cross_partition"

# The supported depth a promoted advisory finding carries — the conservative
# AUDITED_SHALLOW grade the 1.5 AST-corroborated vacuous finding already uses
# (verdict-eligible without claiming a deep grade it did not earn).
PROMOTED_DEPTH = CoverageDepth.AUDITED_SHALLOW

# Verdict conservatism rank (higher = more conservative). The Prosecutor only ever
# moves the candidate toward a higher rank, never lower (the asymmetric-harm rule).
# RELEASE_READY (least conservative) < NOT_READY_FOR_RELEASE; INSUFFICIENT_COVERAGE
# is the floor ArgusAgent reports when it has not assessed enough to claim either — it is
# the most conservative honest state and is never moved away from by the Prosecutor.
_CONSERVATISM_RANK: dict[Verdict, int] = {
    Verdict.RELEASE_READY: 0,
    Verdict.NOT_READY_FOR_RELEASE: 1,
    Verdict.INSUFFICIENT_COVERAGE: 2,
}


class ProsecutorError(ValueError):
    """Raised on a genuinely malformed argument to the Prosecutor (AR10 typed failure).

    A ``ValueError`` subclass localized to this module (mirroring
    ``OrphanCodeError`` / ``PartitionerError`` / ``RecordingValidationError``). Its
    message names the failing argument only — it carries NO source bytes (NFR-S1). A
    degraded per-element shape (a malformed cut edge / finding) is RECORDED as a
    ``DegradedCondition`` and skipped, NOT raised — only a structurally wrong
    top-level argument (a non-``AuditVerdict`` verdict, a non-``CoverageLedger``
    ledger) raises.
    """


class ProsecutionResult(BaseModel):
    """The frozen pure result of one adversarial Prosecutor pass (AR8 / NFR-M2).

    ``frozen=True, extra="forbid"`` (the Epic-1..6 contract precedent). Carries the
    FINAL prosecuted verdict (re-folded through the UNCHANGED 1.6 gate, only ever
    MORE conservative than the candidate), the refined finding set (originals with
    promotions substituted + any ``cross_partition`` findings, ordered via the
    EXISTING ``order_findings``), the structured adversarial rationale (reason tokens
    + the ids of promoted / seam-raised findings — NO source bytes, NFR-S1), the
    promoted-finding ids, the raised ``cross_partition`` finding ids, whether the
    verdict was DOWNGRADED, and the AR10 recorded degraded conditions.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    verdict: AuditVerdict = Field(..., description="The FINAL prosecuted verdict (re-folded, only-more-conservative).")
    findings: tuple[Recording, ...] = Field(
        default=(), description="The refined finding set (promotions substituted + cut-edge findings), ordered (FR33)."
    )
    rationale: tuple[str, ...] = Field(
        default=(), description="Structured adversarial reason tokens (no source bytes — NFR-S1)."
    )
    promoted_finding_ids: tuple[str, ...] = Field(
        default=(), description="recording_ids of advisory findings PROMOTED to verdict-eligible (DN-PROMOTE)."
    )
    cross_partition_finding_ids: tuple[str, ...] = Field(
        default=(), description="recording_ids of raised cross_partition seam findings (CC #4)."
    )
    downgraded: bool = Field(
        default=False, description="True iff the candidate verdict was made MORE conservative (FR19)."
    )
    degraded: tuple[DegradedCondition, ...] = Field(
        default=(), description="AR10 recorded degraded conditions (a malformed finding/cut-edge — never a crash)."
    )


def _has_ast_corroboration(finding: Recording) -> bool:
    """True iff *finding* carries AST corroboration — a non-``None`` locator ``ast_span``.

    The deterministic structural fact (the 6.2 AST-grounded locator). The promotion
    floor: a heuristic-only advisory finding (no ``ast_span`` on any locator) is NEVER
    corroborated, so it can never be promoted (the false-accusation moat). PURE.
    """
    return any(
        locator.ast_span is not None and locator.ast_span != ""
        for locator in finding.locators
    )


def _is_advisory_promotable(finding: Recording) -> bool:
    """True iff *finding* is an advisory candidate the promotion rule may act on.

    Only an advisory finding that is NOT already verdict-eligible
    (``depth_supported is None``) is a promotion candidate; an already-eligible
    finding (a 1.5 AST-corroborated vacuous finding the detector already graded) is
    left UNCHANGED. PURE.
    """
    return finding.depth_supported is None


def _promote(finding: Recording) -> Recording:
    """Mint a NEW promoted ``Recording`` carrying a real ``depth_supported`` (DN-PROMOTE).

    A frozen ``Recording`` is immutable, so the promotion is a ``model_copy`` with the
    supported depth set to the conservative :data:`PROMOTED_DEPTH` — the ORIGINAL is
    NOT mutated. The promoted row keeps the SAME ``recording_id`` / ``rule_id`` /
    ``locators`` (the locating identity is unchanged; only its verdict-eligibility
    signal flips), so the gate's ``depth_supported is not None`` predicate now
    treats it as blocking. PURE.
    """
    return finding.model_copy(update={"depth_supported": PROMOTED_DEPTH})


def _coerce_cut_edge(cut_edge: object) -> CutEdge | None:
    """Return *cut_edge* if it is a well-formed ``CutEdge``, else ``None`` (AR10).

    A non-``CutEdge`` or a ``CutEdge`` with a ``None``/empty required field is NOT a
    crash — it is a recorded degraded condition (handled by the caller) and skipped.
    PURE.
    """
    if not isinstance(cut_edge, CutEdge):
        return None
    if not (cut_edge.caller_file and cut_edge.callee_file and cut_edge.callee):
        return None
    return cut_edge


def _cross_partition_findings(
    cut_edges: tuple[CutEdge, ...] | list[CutEdge],
) -> tuple[list[Recording], list[DegradedCondition]]:
    """The CC #4 cut-edge pass — raise an advisory ``cross_partition`` finding per cut.

    For each well-formed cut edge a seam-spanning defect could hide in, mint an
    ``advisory=True`` ``cross_partition`` ``Recording`` via the EXISTING
    ``build_recording`` (the locator is the caller file; the callee file + callee
    name are carried in the ``ast_span`` token so the finding is self-describing
    WITHOUT a source excerpt — NFR-S1). A malformed cut edge is recorded as a
    degraded condition and skipped (AR10). Findings are SORTED deterministically
    (caller / callee_file / callee). NO cut edges → NO findings. PURE.
    """
    findings: list[Recording] = []
    degraded: list[DegradedCondition] = []
    seen: set[tuple[str, str, str]] = set()
    for raw in cut_edges:
        edge = _coerce_cut_edge(raw)
        if edge is None:
            degraded.append(
                DegradedCondition(file_path="<unknown>", reason="cross_partition_malformed_cut_edge")
            )
            continue
        key = (edge.caller_file, edge.callee_file, edge.callee)
        if key in seen:
            continue
        seen.add(key)
        # The ast_span token carries the structured seam description (callee_file +
        # callee name) — file/symbol identifiers only, never source bytes (NFR-S1).
        seam_token = f"cross_partition:{edge.callee_file}::{edge.callee}"
        draft = FindingDraft(
            file_path=edge.caller_file,
            start_line=1,
            end_line=1,
            ast_span=seam_token,
            rule_id=RULE_CROSS_PARTITION,
            advisory=True,
        )
        findings.append(build_recording(draft, depth_supported=None, claim_present=False))
    findings.sort(
        key=lambda f: (f.locators[0].file_path, f.locators[0].ast_span or "", f.recording_id)
    )
    return findings, degraded


def prosecute(
    *,
    verdict: AuditVerdict,
    ledger: CoverageLedger,
    findings: tuple[Recording, ...] | list[Recording] = (),
    cut_edges: tuple[CutEdge, ...] | list[CutEdge] = (),
    sign_offs: frozenset[str] | set[str] | tuple[str, ...] = (),
) -> ProsecutionResult:
    """Run one PURE adversarial Prosecutor pass → a :class:`ProsecutionResult` (FR19).

    Consumes the candidate verdict + the ledger + the findings + the 2.4 ``cut_edges``
    + the explicit ``sign_offs`` set (recording_ids the Prosecutor signs off on) BY
    IMPORT — NO re-parse, NO second gate. It:

    1. runs the CC #4 ``cross_partition`` cut-edge pass over ``cut_edges`` (advisory
       findings via the EXISTING ``build_recording``; no cut edges → none);
    2. PROMOTES each advisory candidate (``depth_supported is None``) to
       verdict-eligible ONLY with AST corroboration (a non-``None`` locator
       ``ast_span``) AND sign-off (``recording_id in sign_offs``) — a heuristic-only
       finding is NEVER promoted, corroboration-without-sign-off is NOT promoted
       (DN-PROMOTE);
    3. re-folds the refined finding set (originals with promotions substituted + the
       ``cross_partition`` findings) through the UNCHANGED ``evaluate_verdict`` /
       ``order_findings`` — NO second verdict math (§3.3);
    4. returns the MORE conservative of (the candidate verdict, the re-folded verdict)
       — the Prosecutor NEVER upgrades a candidate (FR19 asymmetric-harm direction).

    PURE — no I/O, no clock, no LLM, no provider import, no float. NEVER raises on a
    degraded element (a malformed finding / cut edge → a recorded ``DegradedCondition``
    or pass-through); a typed :class:`ProsecutorError` is raised ONLY on a genuinely
    malformed top-level argument.

    Raises:
        ProsecutorError: a non-``AuditVerdict`` ``verdict`` or a non-``CoverageLedger``
            ``ledger`` — a typed failure, never a leak (AR10).
    """
    if not isinstance(verdict, AuditVerdict):
        raise ProsecutorError(
            f"verdict must be an AuditVerdict, got {type(verdict).__name__!r}"
        )
    if not isinstance(ledger, CoverageLedger):
        raise ProsecutorError(
            f"ledger must be a CoverageLedger, got {type(ledger).__name__!r}"
        )

    sign_off_set = frozenset(sign_offs)
    degraded: list[DegradedCondition] = []

    # ── CC #4 — the cross_partition cut-edge pass (advisory findings) ──
    cross_findings, cross_degraded = _cross_partition_findings(cut_edges)
    degraded.extend(cross_degraded)

    # The full finding universe the promotion rule + the re-fold see: the inbound
    # findings PLUS the raised cross_partition findings (each subject to the SAME rule).
    universe: list[Recording] = []
    for raw in findings:
        if not isinstance(raw, Recording):
            degraded.append(
                DegradedCondition(file_path="<unknown>", reason="prosecutor_malformed_finding")
            )
            continue
        universe.append(raw)
    universe.extend(cross_findings)

    # ── DN-PROMOTE — the advisory→verdict-eligible promotion (corroboration AND sign-off) ──
    refined: list[Recording] = []
    promoted_ids: list[str] = []
    rationale: list[str] = []
    for finding in universe:
        if (
            _is_advisory_promotable(finding)
            and _has_ast_corroboration(finding)
            and finding.recording_id in sign_off_set
        ):
            promoted = _promote(finding)
            refined.append(promoted)
            promoted_ids.append(promoted.recording_id)
            rationale.append(f"promoted:{promoted.rule_id}:{promoted.recording_id}")
        else:
            refined.append(finding)

    # ── §3.3 — re-fold the refined set through the UNCHANGED 1.6 gate (NO second math) ──
    refolded = evaluate_verdict(
        ledger,
        tuple(refined),
        critical_subsystems_all_deep=verdict.critical_subsystems_all_deep,
    )

    # ── FR19 — only ever MORE conservative: pick the higher conservatism rank ──
    candidate_rank = _CONSERVATISM_RANK[verdict.verdict]
    refolded_rank = _CONSERVATISM_RANK[refolded.verdict]
    if refolded_rank >= candidate_rank:
        final_verdict = refolded
    else:
        # The re-fold is LESS conservative than the candidate (an impossible
        # upgrade — promotions/seam findings only ever add blocking weight). Keep
        # the candidate verdict but carry the refined ordered finding set so the
        # cross_partition findings are still surfaced (never an upgrade — FR19).
        final_verdict = verdict.model_copy(
            update={"ordered_findings": order_findings(tuple(refined))}
        )

    downgraded = _CONSERVATISM_RANK[final_verdict.verdict] > candidate_rank
    if downgraded:
        rationale.append(
            f"downgrade:{verdict.verdict.value}->{final_verdict.verdict.value}"
        )

    cross_ids = tuple(f.recording_id for f in cross_findings)
    if cross_ids:
        rationale.extend(f"cross_partition:{rid}" for rid in cross_ids)

    return ProsecutionResult(
        verdict=final_verdict,
        findings=final_verdict.ordered_findings,
        rationale=tuple(rationale),
        promoted_finding_ids=tuple(promoted_ids),
        cross_partition_finding_ids=cross_ids,
        downgraded=downgraded,
        degraded=tuple(degraded),
    )
