"""Seam aggregation + the corroboration moat for the cut-edge pass (Story 6.4 hardening).

Verification area ArgusAgent-PROSECUTOR (TC-ArgusAgent-PROSECUTOR-002-NN). Story 6.4
pinned that a cut edge SURFACES a seam; this module pins the two properties that make
the pass usable and safe:

1. **Granularity.** The claim ("a defect could hide at this boundary") is a property
   of the SEAM, shared by every call that crosses it. Measured on a 132-file repo:
   495 cut edges over 5 partition-pair seams — 495 findings carrying 5 facts, and
   which edges get flagged is decided by the planner's ≤40-file packing rather than
   by the code.
2. **The moat.** A pass that analysed nothing must not be able to corroborate itself
   into a verdict-blocking promotion.
"""

from __future__ import annotations

from argus.index.partitioner import CutEdge
from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger, CoverageLedgerEntry
from argus.verdict.prosecutor import (
    RULE_CROSS_PARTITION,
    _cross_partition_findings,
    _has_ast_corroboration,
    _is_advisory_promotable,
    prosecute,
)
from argus.verdict.verdict_gate import evaluate_verdict


def _ledger() -> CoverageLedger:
    return CoverageLedger.build(
        tuple(
            CoverageLedgerEntry(
                file_path=p, depth=CoverageDepth.AUDITED_DEEP, claim_present=True
            )
            for p in ("a.py", "b.py", "c.py", "d.py", "e.py")
        )
    )


def _edges(*triples: tuple[str, str, str]) -> tuple[CutEdge, ...]:
    return tuple(
        CutEdge(caller_file=c, callee_file=t, callee=n) for c, t, n in triples
    )


# ─────────────────────────────────────────────────────────────────────────────
# Granularity
# ─────────────────────────────────────────────────────────────────────────────


def test_many_edges_across_one_seam_produce_one_finding() -> None:
    """TC-ArgusAgent-PROSECUTOR-002-01 — the motivating defect: N edges, 1 boundary."""
    edges = _edges(
        ("p1/a.py", "p2/x.py", "alpha"),
        ("p1/b.py", "p2/y.py", "beta"),
        ("p1/c.py", "p2/z.py", "gamma"),
        ("p1/d.py", "p2/x.py", "delta"),
    )
    mapping = {
        "p1/a.py": "P1", "p1/b.py": "P1", "p1/c.py": "P1", "p1/d.py": "P1",
        "p2/x.py": "P2", "p2/y.py": "P2", "p2/z.py": "P2",
    }

    findings, degraded = _cross_partition_findings(edges, mapping)

    assert len(findings) == 1
    assert degraded == []
    span = findings[0].locators[0].ast_span or ""
    assert "edges=4" in span
    # The locator is a real crossing caller, deterministically the first.
    assert findings[0].locators[0].file_path == "p1/a.py"


def test_distinct_seams_stay_distinct() -> None:
    """TC-ArgusAgent-PROSECUTOR-002-02 — aggregation must not collapse real boundaries."""
    edges = _edges(
        ("p1/a.py", "p2/x.py", "alpha"),
        ("p1/b.py", "p3/q.py", "beta"),
    )
    mapping = {"p1/a.py": "P1", "p1/b.py": "P1", "p2/x.py": "P2", "p3/q.py": "P3"}

    findings, _ = _cross_partition_findings(edges, mapping)

    assert len(findings) == 2


def test_edges_inside_one_unit_are_not_a_seam() -> None:
    """TC-ArgusAgent-PROSECUTOR-002-03 — same audit unit ⇒ nothing crossed ⇒ no claim."""
    edges = _edges(("p1/a.py", "p1/b.py", "alpha"))
    findings, _ = _cross_partition_findings(edges, {"p1/a.py": "P1", "p1/b.py": "P1"})

    assert findings == []


def test_absent_mapping_treats_each_file_as_its_own_unit() -> None:
    """TC-ArgusAgent-PROSECUTOR-002-04 — the conservative degenerate reading.

    Without unit information every cross-file call is a potential seam, so the
    pre-aggregation behaviour is preserved exactly.
    """
    edges = _edges(("a/caller.py", "b/callee.py", "do_work"))

    findings, _ = _cross_partition_findings(edges, None)

    assert len(findings) == 1
    span = findings[0].locators[0].ast_span or ""
    assert "b/callee.py" in span and "do_work" in span
    assert "edges=" not in span  # a single crossing needs no count


def test_named_callees_are_capped_with_an_explicit_overflow() -> None:
    """TC-ArgusAgent-PROSECUTOR-002-05 — bounded token; a wide seam cannot blow it up."""
    edges = _edges(*[(f"p1/f{i}.py", "p2/x.py", f"sym{i:02d}") for i in range(30)])
    mapping = {f"p1/f{i}.py": "P1" for i in range(30)} | {"p2/x.py": "P2"}

    findings, _ = _cross_partition_findings(edges, mapping)

    span = findings[0].locators[0].ast_span or ""
    assert "sym00,sym01,sym02" in span
    assert "+27_more" in span
    assert "edges=30" in span


def test_aggregation_is_order_independent() -> None:
    """TC-ArgusAgent-PROSECUTOR-002-06 — AR11: input order does not change the output."""
    triples = [
        ("p1/a.py", "p2/x.py", "alpha"),
        ("p1/b.py", "p2/y.py", "beta"),
        ("p1/c.py", "p3/z.py", "gamma"),
    ]
    mapping = {
        "p1/a.py": "P1", "p1/b.py": "P1", "p1/c.py": "P1",
        "p2/x.py": "P2", "p2/y.py": "P2", "p3/z.py": "P3",
    }

    forward, _ = _cross_partition_findings(_edges(*triples), mapping)
    reverse, _ = _cross_partition_findings(_edges(*reversed(triples)), mapping)

    assert [f.recording_id for f in forward] == [f.recording_id for f in reverse]


# ─────────────────────────────────────────────────────────────────────────────
# The corroboration moat
# ─────────────────────────────────────────────────────────────────────────────


def test_cross_partition_can_never_self_corroborate() -> None:
    """TC-ArgusAgent-PROSECUTOR-002-07 — THE guardrail.

    The pass borrows the reserved ``ast_span`` field to carry a self-describing seam
    descriptor (NFR-S1). Reading that descriptor as AST grounding would let EVERY cut
    edge clear the promotion floor and become verdict-blocking on sign-off — a false
    accusation manufactured by a pass that analysed nothing.
    """
    findings, _ = _cross_partition_findings(_edges(("a.py", "b.py", "do_work")), None)
    finding = findings[0]

    assert finding.rule_id == RULE_CROSS_PARTITION
    assert finding.locators[0].ast_span is not None  # the descriptor IS present …
    assert _is_advisory_promotable(finding) is True  # … and it is an advisory candidate …
    assert _has_ast_corroboration(finding) is False  # … but it corroborates nothing.


def test_signed_off_cross_partition_is_not_promoted_to_blocking() -> None:
    """TC-ArgusAgent-PROSECUTOR-002-08 — end-to-end: sign-off alone cannot promote it."""
    ledger = _ledger()
    candidate = evaluate_verdict(ledger, ())
    findings, _ = _cross_partition_findings(_edges(("a.py", "b.py", "do_work")), None)
    seam_id = findings[0].recording_id

    result = prosecute(
        verdict=candidate,
        ledger=ledger,
        findings=(),
        cut_edges=_edges(("a.py", "b.py", "do_work")),
        sign_offs=frozenset({seam_id}),  # an operator signs off on the seam
    )

    promoted = [f for f in result.findings if f.rule_id == RULE_CROSS_PARTITION]
    assert all(f.depth_supported is None for f in promoted)
    assert result.verdict.blocking_finding_count == 0
    assert result.verdict.verdict is candidate.verdict  # no downgrade earned
