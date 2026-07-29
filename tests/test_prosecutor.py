"""The PURE adversarial Prosecutor — the complete declared decision set (Story 6.4).

Verification area ArgusAgent-PROSECUTOR (``TC-ArgusAgent-PROSECUTOR-001-NN`` — index from -01).
Drivers: ArgusAgent-FR-19 (challenge the candidate verdict + downgrade an unearned
``RELEASE_READY``), ArgusAgent-FR-13 (every emitted finding — incl. ``cross_partition`` —
carries a verifiable locator via the EXISTING ``build_recording``), ArgusAgent-CC4 (the V1
``cross_partition`` cut-edge pass surfaces a seam a defect could hide in — the V1
mitigation for the deferred V2 seam auditor), ArgusAgent-FR-33-support / CC #6 (the
advisory→verdict-eligible promotion: promote IFF AST corroboration AND sign-off; a
heuristic-only finding is NEVER promoted — the false-accusation floor),
ArgusAgent-AR10 / NFR-R1 (a malformed / empty / None verdict / ledger / findings / cut-edge →
a recorded ``DegradedCondition`` or pass-through, NEVER an uncaught raise),
ArgusAgent-AI-E1-1 (non-ASCII path / callee classifies + serializes under
``PYTHONIOENCODING=utf-8``).

The complete-the-declared-set discipline (AI-E5-1) — every member is enumerated and
covered, RED-first where applicable (the (c) heuristic-never-promoted + (h)
never-upgrade members are the false-accusation + asymmetric-harm guards):

  (a) an EARNED RELEASE_READY                       → UNCHANGED (byte-identical)
  (b) an UNEARNED RELEASE_READY                      → downgraded to NOT_READY_FOR_RELEASE
  (c) a heuristic-only advisory (no AST corrobor.)   → NEVER promoted (false-accusation floor)
  (d) an AST-corroborated advisory WITH sign-off     → PROMOTED to verdict-eligible
  (e) an AST-corroborated advisory WITHOUT sign-off  → NOT promoted (sign-off required)
  (f) a hiding cut edge                              → a cross_partition advisory finding
  (g) NO cut edges                                   → NO cross_partition finding
  (h) an INSUFFICIENT_COVERAGE / NOT_READY candidate → never UPGRADED (only more conservative)
  (i) malformed / empty / None inputs                → recorded DegradedCondition / pass-through
  (j) a non-ASCII path / callee                      → classifies + serializes (AI-E1-1)
"""

from __future__ import annotations

from argus.detectors.base import FindingDraft, build_recording
from argus.index.partitioner import CutEdge
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    grade_entry,
)
from argus.verdict.prosecutor import (
    PROMOTED_DEPTH,
    RULE_CROSS_PARTITION,
    ProsecutionResult,
    ProsecutorError,
    prosecute,
)
from argus.verdict.verdict_gate import (
    AuditVerdict,
    Verdict,
    evaluate_verdict,
)


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures — earned-green and below-gate ledgers built only from the closed enum
# ──────────────────────────────────────────────────────────────────────────────


def _release_ready_ledger() -> CoverageLedger:
    """A 100%-deep ledger the 1.6 gate folds to RELEASE_READY (deep-% >= 60%)."""
    entries = [
        grade_entry(file_path=f"f{i}.py", proposed_depth=CoverageDepth.AUDITED_DEEP, claim_present=True)
        for i in range(3)
    ]
    return CoverageLedger.build(entries)


def _not_ready_ledger() -> CoverageLedger:
    """A ledger between the 20% floor and the 60% gate → NOT_READY_FOR_RELEASE."""
    entries = [
        grade_entry(
            file_path=f"g{i}.py",
            proposed_depth=CoverageDepth.AUDITED_DEEP,
            claim_present=(i < 2),  # 2/5 deep = 40% (>=20% floor, <60% gate)
        )
        for i in range(5)
    ]
    return CoverageLedger.build(entries)


def _insufficient_ledger() -> CoverageLedger:
    """A below-20%-floor ledger → INSUFFICIENT_COVERAGE."""
    entries = [
        grade_entry(
            file_path=f"h{i}.py",
            proposed_depth=CoverageDepth.AUDITED_DEEP,
            claim_present=(i == 0),  # 1/10 deep = 10% (<20% floor)
        )
        for i in range(10)
    ]
    return CoverageLedger.build(entries)


def _advisory(
    *, file_path: str = "f0.py", line: int = 2, ast_span: str | None = None, rule_id: str = "vacuous_test_heuristic"
):
    return build_recording(
        FindingDraft(
            file_path=file_path,
            start_line=line,
            end_line=line,
            ast_span=ast_span,
            rule_id=rule_id,
            advisory=True,
        ),
        depth_supported=None,
    )


# ──────────────────────────────────────────────────────────────────────────────
# (a) EARNED RELEASE_READY → UNCHANGED
# ──────────────────────────────────────────────────────────────────────────────


def test_earned_release_ready_is_unchanged() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-01 — an earned green is left UNCHANGED (no downgrade/seam)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    assert candidate.verdict is Verdict.RELEASE_READY

    result = prosecute(verdict=candidate, ledger=ledger, findings=(), cut_edges=())

    assert isinstance(result, ProsecutionResult)
    assert result.verdict.verdict is Verdict.RELEASE_READY
    assert result.downgraded is False
    assert result.promoted_finding_ids == ()
    assert result.cross_partition_finding_ids == ()
    assert result.findings == ()


# ──────────────────────────────────────────────────────────────────────────────
# (b) UNEARNED RELEASE_READY → downgraded
# ──────────────────────────────────────────────────────────────────────────────


def test_unearned_release_ready_is_downgraded_with_rationale() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-02 — a corroborated+signed-off advisory downgrades the green (FR19)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    assert candidate.verdict is Verdict.RELEASE_READY

    finding = _advisory(ast_span="func:foo")  # AST corroboration present
    result = prosecute(
        verdict=candidate,
        ledger=ledger,
        findings=(finding,),
        cut_edges=(),
        sign_offs={finding.recording_id},
    )

    assert result.verdict.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert result.downgraded is True
    assert finding.recording_id in result.promoted_finding_ids
    # The rationale is structured tokens only — never a source excerpt (NFR-S1).
    assert any(tok.startswith("downgrade:") for tok in result.rationale)
    assert any(tok.startswith("promoted:") for tok in result.rationale)


def test_downgrade_only_ever_more_conservative_never_upgrade() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-03 — the verdict only ever moves MORE conservative (FR19)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    finding = _advisory(ast_span="func:foo")
    result = prosecute(
        verdict=candidate,
        ledger=ledger,
        findings=(finding,),
        cut_edges=(),
        sign_offs={finding.recording_id},
    )
    # RELEASE_READY -> NOT_READY_FOR_RELEASE is a downgrade; the inverse never happens.
    assert result.verdict.verdict is not Verdict.RELEASE_READY


# ──────────────────────────────────────────────────────────────────────────────
# (c) heuristic-only advisory → NEVER promoted (the false-accusation floor, RED-first)
# ──────────────────────────────────────────────────────────────────────────────


def test_heuristic_only_advisory_is_never_promoted() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-04 — a heuristic-only finding is NEVER promoted (RED-first).

    A finding with NO AST corroboration (no locator ``ast_span``) is not promoted even
    when explicitly signed off — the false-accusation floor: a 🔴 is never served on a
    heuristic alone (RED against a naive "promote every signed-off advisory").
    """
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    finding = _advisory(ast_span=None)  # heuristic-only — NO corroboration

    result = prosecute(
        verdict=candidate,
        ledger=ledger,
        findings=(finding,),
        cut_edges=(),
        sign_offs={finding.recording_id},  # signed off, but no corroboration
    )

    assert result.promoted_finding_ids == ()
    assert result.downgraded is False
    assert result.verdict.verdict is Verdict.RELEASE_READY


# ──────────────────────────────────────────────────────────────────────────────
# (d) AST-corroborated advisory WITH sign-off → PROMOTED
# ──────────────────────────────────────────────────────────────────────────────


def test_corroborated_and_signed_off_advisory_is_promoted() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-05 — corroboration AND sign-off → a NEW promoted Recording (DN-PROMOTE)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    finding = _advisory(ast_span="func:foo")
    assert finding.depth_supported is None  # the original is advisory-only

    result = prosecute(
        verdict=candidate,
        ledger=ledger,
        findings=(finding,),
        cut_edges=(),
        sign_offs={finding.recording_id},
    )

    assert finding.recording_id in result.promoted_finding_ids
    # The promoted finding carries a real depth_supported; the ORIGINAL is not mutated.
    assert finding.depth_supported is None
    promoted = next(f for f in result.findings if f.recording_id == finding.recording_id)
    assert promoted.depth_supported is PROMOTED_DEPTH
    assert promoted.recording_id == finding.recording_id  # same locating identity


# ──────────────────────────────────────────────────────────────────────────────
# (e) AST-corroborated advisory WITHOUT sign-off → NOT promoted
# ──────────────────────────────────────────────────────────────────────────────


def test_corroborated_without_sign_off_is_not_promoted() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-06 — corroboration WITHOUT sign-off is NOT promoted (sign-off required)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    finding = _advisory(ast_span="func:foo")

    result = prosecute(
        verdict=candidate,
        ledger=ledger,
        findings=(finding,),
        cut_edges=(),
        sign_offs=set(),  # corroborated, but NOT signed off
    )

    assert result.promoted_finding_ids == ()
    assert result.downgraded is False
    assert result.verdict.verdict is Verdict.RELEASE_READY


# ──────────────────────────────────────────────────────────────────────────────
# (f) a hiding cut edge → a cross_partition advisory finding
# ──────────────────────────────────────────────────────────────────────────────


def test_hiding_cut_edge_raises_cross_partition_finding() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-07 — a cut edge surfaces a cross_partition advisory finding (CC #4/FR13)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    edge = CutEdge(caller_file="a/caller.py", callee_file="b/callee.py", callee="do_work")

    result = prosecute(verdict=candidate, ledger=ledger, findings=(), cut_edges=(edge,))

    cross = [f for f in result.findings if f.rule_id == RULE_CROSS_PARTITION]
    assert len(cross) == 1
    finding = cross[0]
    assert finding.advisory is True
    assert finding.depth_supported is None  # advisory — not verdict-eligible alone
    # FR13 locator-or-reject: the caller file is the locator; the seam is self-describing.
    assert finding.locators[0].file_path == "a/caller.py"
    assert "b/callee.py" in (finding.locators[0].ast_span or "")
    assert "do_work" in (finding.locators[0].ast_span or "")
    # An advisory cross_partition finding does NOT downgrade an earned green on its own.
    assert result.downgraded is False
    assert finding.recording_id in result.cross_partition_finding_ids


def test_cross_partition_findings_are_deterministically_ordered_and_deduped() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-08 — cut edges produce a SORTED, deduped finding set (AR11)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    edges = (
        CutEdge(caller_file="z.py", callee_file="b.py", callee="bar"),
        CutEdge(caller_file="a.py", callee_file="c.py", callee="foo"),
        CutEdge(caller_file="a.py", callee_file="c.py", callee="foo"),  # duplicate
    )
    r1 = prosecute(verdict=candidate, ledger=ledger, findings=(), cut_edges=edges)
    r2 = prosecute(verdict=candidate, ledger=ledger, findings=(), cut_edges=tuple(reversed(edges)))
    cross1 = [f.recording_id for f in r1.findings if f.rule_id == RULE_CROSS_PARTITION]
    cross2 = [f.recording_id for f in r2.findings if f.rule_id == RULE_CROSS_PARTITION]
    assert len(cross1) == 2  # the duplicate is collapsed
    assert cross1 == cross2  # input order does not change the output (AR11)


# ──────────────────────────────────────────────────────────────────────────────
# (g) NO cut edges → NO cross_partition finding (byte-identical)
# ──────────────────────────────────────────────────────────────────────────────


def test_no_cut_edges_raises_no_cross_partition_finding() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-09 — a repo with NO cut edges raises NO cross_partition finding."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    result = prosecute(verdict=candidate, ledger=ledger, findings=(), cut_edges=())
    assert not any(f.rule_id == RULE_CROSS_PARTITION for f in result.findings)
    assert result.cross_partition_finding_ids == ()
    assert result.verdict.verdict is Verdict.RELEASE_READY


# ──────────────────────────────────────────────────────────────────────────────
# (h) an INSUFFICIENT_COVERAGE / NOT_READY candidate → never UPGRADED (RED-first)
# ──────────────────────────────────────────────────────────────────────────────


def test_not_ready_candidate_is_never_upgraded() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-10 — a NOT_READY candidate is never upgraded (asymmetric harm, RED-first)."""
    ledger = _not_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    assert candidate.verdict is Verdict.NOT_READY_FOR_RELEASE
    result = prosecute(verdict=candidate, ledger=ledger, findings=(), cut_edges=())
    assert result.verdict.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert result.downgraded is False


def test_insufficient_coverage_candidate_is_never_upgraded() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-11 — an INSUFFICIENT_COVERAGE candidate is never upgraded."""
    ledger = _insufficient_ledger()
    candidate = evaluate_verdict(ledger, ())
    assert candidate.verdict is Verdict.INSUFFICIENT_COVERAGE
    # Even a cut edge (advisory) cannot move INSUFFICIENT_COVERAGE to a less-conservative state.
    edge = CutEdge(caller_file="a.py", callee_file="b.py", callee="bar")
    result = prosecute(verdict=candidate, ledger=ledger, findings=(), cut_edges=(edge,))
    assert result.verdict.verdict is Verdict.INSUFFICIENT_COVERAGE


# ──────────────────────────────────────────────────────────────────────────────
# (i) malformed / empty / None → recorded DegradedCondition / pass-through (AR10)
# ──────────────────────────────────────────────────────────────────────────────


def test_malformed_top_level_arguments_raise_typed_error() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-12 — a non-AuditVerdict / non-CoverageLedger raises ProsecutorError (AR10)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    try:
        prosecute(verdict="not-a-verdict", ledger=ledger)  # type: ignore[arg-type]
    except ProsecutorError:
        pass
    else:
        raise AssertionError("a non-AuditVerdict verdict must raise ProsecutorError")
    try:
        prosecute(verdict=candidate, ledger="not-a-ledger")  # type: ignore[arg-type]
    except ProsecutorError:
        pass
    else:
        raise AssertionError("a non-CoverageLedger ledger must raise ProsecutorError")


def test_malformed_findings_and_cut_edges_are_recorded_not_raised() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-13 — a malformed finding / cut edge is recorded degraded, never a crash (AR10)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    # A None finding, a non-Recording finding, a None cut edge, and a CutEdge with an
    # empty required field — all degrade, none crash.
    bad_edge = CutEdge.model_construct(caller_file="", callee_file="b.py", callee="bar")
    result = prosecute(
        verdict=candidate,
        ledger=ledger,
        findings=(None, "x"),  # type: ignore[arg-type]
        cut_edges=(None, bad_edge),  # type: ignore[arg-type]
    )
    assert isinstance(result, ProsecutionResult)
    assert len(result.degraded) == 4
    reasons = {d.reason for d in result.degraded}
    assert "prosecutor_malformed_finding" in reasons
    assert "cross_partition_malformed_cut_edge" in reasons
    # An earned green with only degraded junk inputs stays RELEASE_READY (pass-through).
    assert result.verdict.verdict is Verdict.RELEASE_READY


def test_empty_inputs_pass_through_unchanged() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-14 — empty findings + empty cut edges → pass-through (AR10)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    result = prosecute(verdict=candidate, ledger=ledger)
    assert result.verdict.verdict is candidate.verdict
    assert result.findings == ()
    assert result.degraded == ()


# ──────────────────────────────────────────────────────────────────────────────
# (j) non-ASCII path / callee → classifies + serializes (AI-E1-1)
# ──────────────────────────────────────────────────────────────────────────────


def test_non_ascii_cut_edge_classifies_and_derives_stable_id() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-15 — a non-ASCII path/callee classifies + derives a stable id (AI-E1-1)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    edge = CutEdge(caller_file="módulo/llamador.py", callee_file="b/callee.py", callee="函数名")

    r1 = prosecute(verdict=candidate, ledger=ledger, findings=(), cut_edges=(edge,))
    r2 = prosecute(verdict=candidate, ledger=ledger, findings=(), cut_edges=(edge,))

    cross1 = [f for f in r1.findings if f.rule_id == RULE_CROSS_PARTITION]
    assert len(cross1) == 1
    finding = cross1[0]
    assert finding.locators[0].file_path == "módulo/llamador.py"
    assert "函数名" in (finding.locators[0].ast_span or "")
    # The content-derived id is stable across runs (the single ensure_ascii=False serializer).
    cross2 = [f for f in r2.findings if f.rule_id == RULE_CROSS_PARTITION]
    assert finding.recording_id == cross2[0].recording_id


def test_non_ascii_advisory_promotion_is_stable() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-16 — a non-ASCII finding promotes + derives a stable id (AI-E1-1)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    finding = _advisory(file_path="café/módulo.py", ast_span="función:añadir")
    result = prosecute(
        verdict=candidate,
        ledger=ledger,
        findings=(finding,),
        cut_edges=(),
        sign_offs={finding.recording_id},
    )
    assert finding.recording_id in result.promoted_finding_ids
    assert result.verdict.verdict is Verdict.NOT_READY_FOR_RELEASE


# ──────────────────────────────────────────────────────────────────────────────
# Purity / determinism — the result is byte-stable across runs (NFR-D1/D2/AR8)
# ──────────────────────────────────────────────────────────────────────────────


def test_result_is_deterministic_across_runs() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-17 — two runs over the same inputs produce the identical result (NFR-D2)."""
    ledger = _release_ready_ledger()
    candidate = evaluate_verdict(ledger, ())
    edges = (CutEdge(caller_file="a.py", callee_file="b.py", callee="bar"),)
    finding = _advisory(ast_span="func:foo")
    r1 = prosecute(verdict=candidate, ledger=ledger, findings=(finding,), cut_edges=edges, sign_offs={finding.recording_id})
    r2 = prosecute(verdict=candidate, ledger=ledger, findings=(finding,), cut_edges=edges, sign_offs={finding.recording_id})
    assert r1.model_dump() == r2.model_dump()
    assert isinstance(r1.verdict, AuditVerdict)
