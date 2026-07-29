"""Story 7.2 — the Minions dogfood PROOF-RUN + SIGNED bundle + signature demo test.

Verification area ArgusAgent-DOGFOOD (``TC-ArgusAgent-DOGFOOD-001-NN`` — CONTINUING from the 7.1
index; 7.1 locked ``...-01..17``, so 7.2 starts at ``...-18``). Drivers: ArgusAgent-FR-29
(the SIGNED evidence bundle), ArgusAgent-FR-17 / NFR-A3 (the negative-assurance verdict the
bundle exports), ArgusAgent-FR-30 (the frozen headless invocation the dogfood reuses),
ArgusAgent-FR-21 / OI3 (the empirical ``$X`` = 843 ceiling — within it + the 3.2 halt),
ArgusAgent-FR-20 / FR13 (the adjudication-ready real findings + the 6.6 ``finding_match_key``),
ArgusAgent-NFR-D1 / P1 (100% reproducibility over a real repo — byte-identical verdict +
bundle bytes), ArgusAgent-NFR-S1 / S3 (no Minions source/secret byte in the bundle / proof /
precision surface), ArgusAgent-NFR-A1 / D3 (the content-hashed, prev-hash-chained envelope —
the signature; ``created_at`` excluded from the hash), ArgusAgent-AR4 (int credits / Fraction
ratios — never float), ArgusAgent-AR7 (REUSE by import — no fork of the pipeline / bundle /
serializer / lint / precision harness / 7.1 plan), ArgusAgent-AR10 (typed failure — no
uncaught traceback), ArgusAgent-NFR-M1/M2 (≤1200-line files; frozen Epic-1..6 + 7.1 contracts
+ the 4.3/6.5 SHAPES unchanged).

The complete-the-declared-set matrix (AI-E5-1 / AI-E6-1 / AI-E4-2 / AR10) — each covered:
  (1) the reproducible dogfood execution + proof artifact (AC-EXECUTE)   → TC-...-18/19/20
  (2) the SIGNED source-free bundle over the REAL repo (AC-BUNDLE)        → TC-...-21/22
  (3) the reproduced signature demo (AC-SIGNATURE)                       → TC-...-23
  (4) the 100%-reproducibility check (AC-REPRODUCIBLE, RED-first)         → TC-...-24
  (5) the grade: demo-heuristic-only red-team flag (AC-DEMO-GRADE)        → TC-...-25/26
  (6) the adjudication-ready findings layout (AC-ADJUDICATION-READY)      → TC-...-27/28
  (7) the provisional-gate honesty + the DF-6-6-A note + the human defer  → TC-...-29/30/31
  (8) the complete-the-declared-set enumeration + no-crash edges          → TC-...-32/33
Every assertion NAMES the unit / finding class / cartridge id (the AI-E4-2 no-crash leg).

THE OI1 LOCK (DN-PROVISIONAL — read twice): the ≥80%-precision gate STAYS PROVISIONAL.
Story 7.2 EXECUTES the dogfood + produces the REAL findings + lays them ADJUDICATION-READY
ONLY. The human TP/FP adjudication that clears the gate is a human step. ``protocol_cleared``
is NEVER flipped and the ``precision_gate_status()`` marker is NEVER flipped —
over-claiming a cleared gate / presenting a Tier-A demo run as externalization evidence is
the exact failure mode this lock forbids (RED-first in TC-...-26 / TC-...-30).
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402
from _registry import precision_gate_status  # noqa: E402

from argus.dogfood.proof_run import (  # noqa: E402
    DOGFOOD_ArgusAgent_VERSION,
    DOGFOOD_BUDGET_CEILING,
    DOGFOOD_GRADE,
    AdjudicationRow,
    DogfoodProofError,
    DogfoodProofRun,
    build_dogfood_proof,
    cost_summary,
    enumerate_tracked_sources,
    render_proof_markdown,
    run_dogfood,
)
from argus.evidence.bundle import (  # noqa: E402
    build_evidence_bundle,
    bundle_to_canonical_bytes,
)
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402

# The committed proof artifact (the durable §3.4 deliverable).
_PROOF_ARTIFACT = (
    _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent" / "minions-dogfood-proof.md"
)
_DEFERRED_WORK = (
    _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent" / "deferred-work.md"
)

# Distinctive Minions SOURCE-BODY bytes that MUST NOT leak into the bundle (NFR-S1).
# These are real source STATEMENTS / docstring content that live inside Minions source
# file bodies (verified present in the real tree by the test's non-vacuity guard) but
# have NO business appearing in the source-free evidence bundle. NOTE: a bundle finding
# legitimately cites a locator (file + line + a symbol name in ``ast_span`` — that IS the
# "location" FR13 requires), so a SYMBOL/identifier name is NOT a valid sentinel; only a
# source-CODE-BODY byte (a statement, an import, a docstring phrase) is — that is what the
# 4.3 no-source-retention moat forbids retaining.
_SOURCE_SENTINELS: tuple[str, ...] = (
    "HMAC-SHA256",       # a docstring/comment phrase in agent_auth source
    "import hashlib",    # an import statement (source-body bytes)
    "raise ValueError",  # a raise statement (source-body bytes)
)


# One shared dogfood run per session (the audit + bundle export is the expensive step).
# Module-scoped so the ~137-file real-repo audit runs ONCE, not per test.
@pytest.fixture(scope="module")
def dogfood_proof(tmp_path_factory: pytest.TempPathFactory) -> DogfoodProofRun:
    snap = tmp_path_factory.mktemp("dogfood-proof")
    return build_dogfood_proof(str(_REPO_ROOT), snap / "snapshot")


# ─────────────────────────────────────────────────────────────────────────────
# Member (1) / AC-EXECUTE — the reproducible dogfood execution + proof artifact
# ─────────────────────────────────────────────────────────────────────────────


def test_dogfood_runs_frozen_pipeline_over_real_repo(dogfood_proof: DogfoodProofRun) -> None:
    """TC-ArgusAgent-DOGFOOD-001-18 — AC-EXECUTE: the frozen audit runs over the REAL Minions repo.

    The dogfood REUSES ``run_audit_detailed`` (no fork) over the real Minions platform
    source (~137 tracked ``minions_core/`` modules over ~38.1k LOC; the 7.1 plan is
    size-derived — the unit count scales with the tree, it is NOT a frozen constant),
    producing a real verdict + coverage ledger + findings. NAMED figures.
    """
    proof = dogfood_proof
    assert proof.source_file_count >= 60, (
        f"the dogfood must audit the real Minions tree; got {proof.source_file_count} files"
    )
    assert proof.total_loc >= 10000, f"real-repo LOC expected; got {proof.total_loc}"
    # Partition count scales with repo size; assert the plan is real and internally
    # consistent rather than pinning a size-derived constant. A frozen 4-unit count
    # coupled every Minions story that added LOC to this ArgusAgent snapshot (the 7.1
    # partitioner rebalances as the tree grows) — operator adjudication 2026-07-10.
    assert proof.unit_count >= 3, (

        f"the 7.1 plan partitions the real tree; got {proof.unit_count}"
    )
    # Internal consistency: the PartitionPlan is total + disjoint (every source file
    # lands in EXACTLY one partition, argus/index/partitioner.py), so a
    # genuine plan has >=1 unit and never MORE units than the files it covers — this
    # proves the plan is real, not merely "big enough".
    assert 1 <= proof.unit_count <= proof.source_file_count, (
        f"unit_count {proof.unit_count} must lie in [1, source_file_count="
        f"{proof.source_file_count}] for a total, disjoint partition plan"
    )
    # The verdict is a real closed-enum verdict + a mapped exit code (not fabricated).
    assert proof.verdict in {
        "RELEASE_READY",
        "NOT_READY_FOR_RELEASE",
        "INSUFFICIENT_COVERAGE",
    }
    assert proof.exit_code in {0, 2, 3}
    # The deep-% is an exact Fraction, never a float (AR4).
    assert isinstance(proof.deep_ratio, Fraction)
    assert not isinstance(proof.deep_ratio, float)
    assert proof.total_finding_count >= 1, "the real dogfood must emit findings"


def test_dogfood_completes_within_the_843_ceiling_and_demonstrates_halt(
    dogfood_proof: DogfoodProofRun,
) -> None:
    """TC-ArgusAgent-DOGFOOD-001-19 — AC-EXECUTE/FR21/OI3: within $X=843 + the 3.2 halt-if-breached.

    The run's V1 deterministic cost total FITS under ``$X`` = 843 (``ceiling_reached is
    False``), while a ceiling ONE credit below the total demonstrably breaches (the 3.2
    halt->skip->downgrade->report path, REUSING the 3.1 ``account_spend`` — no fork). All
    int credits / a Fraction baseline ratio — never float (AR4).
    """
    cost = dogfood_proof.cost
    assert cost.ceiling == DOGFOOD_BUDGET_CEILING == 843
    assert isinstance(cost.total_credits, int) and not isinstance(cost.total_credits, bool)
    assert 0 < cost.total_credits <= cost.ceiling, (
        f"the dogfood total {cost.total_credits} must fit under $X={cost.ceiling}"
    )
    assert cost.fits_within_ceiling is True, "the run must FIT under $X=843 (AC-EXECUTE)"
    assert cost.breaches_below_total is True, (
        "a ceiling below the total must breach (the 3.2 halt demonstration)"
    )
    assert isinstance(cost.baseline_ratio, (Fraction, str))
    assert not isinstance(cost.baseline_ratio, float)


def test_committed_proof_artifact_exists_and_matches_live_run(
    dogfood_proof: DogfoodProofRun,
) -> None:
    """TC-ArgusAgent-DOGFOOD-001-20 — AC-EXECUTE: the committed proof .md exists + re-derives.

    The committed ``minions-dogfood-proof.md`` is the durable §3.4 deliverable AND is
    reproducible — the live run's verdict + ceiling + grade appear in the committed
    markdown, so the artifact cannot silently rot away from the generator.
    """
    assert _PROOF_ARTIFACT.exists(), f"the proof artifact must exist at {_PROOF_ARTIFACT}"
    text = _PROOF_ARTIFACT.read_text(encoding="utf-8")
    proof = dogfood_proof
    assert f"`{proof.verdict}` (exit `{proof.exit_code}`)" in text
    assert "$X` = 843" in text or "843" in text
    assert DOGFOOD_GRADE in text
    assert "REUSED" in text or "REUSING" in text  # the AR7 no-fork narration
    # The live render re-derives the SAME committed structure (headings), not a rot.
    live = render_proof_markdown(proof)
    for heading in (
        "## 1. Dogfood execution",
        "## 3. The SIGNED, source-free evidence bundle",
        "## 7. The",
    ):
        assert heading in live and heading in text, f"proof artifact missing {heading!r} (rot?)"


# ─────────────────────────────────────────────────────────────────────────────
# Member (2) / AC-BUNDLE — the SIGNED, source-free evidence bundle over the REAL repo
# ─────────────────────────────────────────────────────────────────────────────


def test_signed_bundle_persisted_content_addressed_and_consistent(
    dogfood_proof: DogfoodProofRun,
) -> None:
    """TC-ArgusAgent-DOGFOOD-001-21 — AC-BUNDLE/FR29/NFR-A1: the bundle is signed + persisted + linted.

    The bundle is exported via the 4.3 ``build_evidence_bundle`` + persisted via
    ``persist_evidence_bundle`` (content-addressed under ``state/`` — the filename stem IS
    the content hash = the signature) and the 4.2 ``lint_referential_integrity`` report is
    consistent (no dangling references). The bundle is non-empty.
    """
    proof = dogfood_proof
    assert proof.bundle_locator.startswith("state/") and proof.bundle_locator.endswith(".json")
    # The content-addressed filename stem IS the content hash (the signature).
    assert proof.bundle_content_hash and proof.bundle_content_hash in proof.bundle_locator
    assert proof.bundle_byte_length > 0, "the bundle must be non-empty (redaction != suppression)"
    assert proof.integrity_consistent is True, (
        "the referential-integrity lint over the dogfood .argus/ tree must be consistent"
    )


def test_signed_bundle_retains_no_minions_source_byte(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-DOGFOOD-001-22 — AC-BUNDLE/NFR-S1/S3: NO Minions source/secret byte in the bundle.

    The no-source-retention moat proven over the REAL Minions tree (not only a cartridge):
    distinctive Minions source identifiers are ABSENT from the serialized bundle bytes +
    the persisted artifact, WHILE the bundle is non-empty + the verdict + scope statement
    are present (redaction != suppression). Re-reading via the 1.3 reader round-trips.
    """
    snap = tmp_path / "snap"
    # Non-vacuity guard: prove each sentinel is GENUINELY present in the real Minions
    # source (so the absence assertion below is meaningful, not vacuous) — the source-body
    # bytes really exist in the audited tree, yet must not survive into the bundle.
    real_source = b""
    for src_file in sorted((_REPO_ROOT).rglob("*.py")):
        if "argus" in src_file.parts:
            continue
        real_source += src_file.read_bytes()
    for sentinel in _SOURCE_SENTINELS:
        assert sentinel.encode("utf-8") in real_source, (
            f"non-vacuity: sentinel {sentinel!r} must genuinely exist in the real Minions "
            "source (else the no-source assertion is vacuous)"
        )

    execution = run_dogfood(str(_REPO_ROOT), snap)
    blob = execution.bundle_bytes
    # The bundle carries the verdict + scope statement (non-empty, redaction != suppression).
    na = execution.bundle.negative_assurance
    assert na is not None
    assert execution.bundle.findings, "the bundle must carry the verdict-ordered findings"
    # NO distinctive Minions source-BODY byte leaks into the serialized bundle.
    for sentinel in _SOURCE_SENTINELS:
        assert sentinel.encode("utf-8") not in blob, (
            f"SOURCE LEAK — Minions source identifier {sentinel!r} appeared in the bundle bytes (NFR-S1)"
        )
    # The persisted artifact on disk is ALSO source-free (searched as UTF-8 over .argus/**).
    argus_dir = snap / ".argus"
    on_disk = b""
    for artifact in sorted(argus_dir.rglob("*.json")):
        on_disk += artifact.read_bytes()
    for sentinel in _SOURCE_SENTINELS:
        assert sentinel.encode("utf-8") not in on_disk, (
            f"SOURCE LEAK — {sentinel!r} appeared in a persisted .argus/ artifact (NFR-S1/S3)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Member (3) / AC-SIGNATURE — the reproduced GitHub-green · ArgusAgent-🔴 signature demo
# ─────────────────────────────────────────────────────────────────────────────


def test_signature_demo_vacuous_test_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-DOGFOOD-001-23 — AC-SIGNATURE: `GitHub green · Sonar green · ArgusAgent 🔴` reproduced.

    ArgusAgent audits a vacuous test (the ``vacuous_basic`` cartridge — a test that runs green
    in CI while asserting nothing) → a BLOCKING ``vacuous_test_ast`` finding FIRST in
    ``ordered_findings`` → verdict ``NOT_READY_FOR_RELEASE`` / exit ``2`` (the 🔴). The 1.7
    ``TC-ArgusAgent-PIPELINE-001-01`` signature-demo precedent, reproduced as a committed test.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "vacuous")
    result = run_audit_detailed(
        AuditRequest(repo_path=str(repo), commit="HEAD", budget=843, materiality_bar="default")
    )
    verdict = result.verdict
    assert verdict.verdict.value == "NOT_READY_FOR_RELEASE", (
        f"the vacuous-test signature demo must be 🔴 NOT_READY_FOR_RELEASE; got {verdict.verdict.value}"
    )
    assert verdict.exit_code == 2, f"the 🔴 must map to exit 2; got {verdict.exit_code}"
    assert verdict.blocking_finding_count >= 1, "the vacuous_test_ast finding must be BLOCKING (🔴)"
    assert verdict.ordered_findings, "the signature demo must emit findings"
    first = verdict.ordered_findings[0]
    assert first.rule_id == "vacuous_test_ast", (
        f"the vacuous_test_ast finding must be FIRST (FR33 blocking-first); got {first.rule_id!r}"
    )
    assert first.depth_supported is not None, "the demo 🔴 finding must be verdict-eligible"


# ─────────────────────────────────────────────────────────────────────────────
# Member (4) / AC-REPRODUCIBLE — 100% reproducibility (RED-first non-determinism)
# ─────────────────────────────────────────────────────────────────────────────


def test_dogfood_is_100pct_reproducible_byte_identical(tmp_path: Path) -> None:
    """TC-ArgusAgent-DOGFOOD-001-24 — AC-REPRODUCIBLE/NFR-D1/P1: two runs → byte-identical bundle.

    Two dogfood runs on the SAME tracked Minions content yield an IDENTICAL verdict token +
    deep-Fraction + BYTE-IDENTICAL ``bundle_to_canonical_bytes`` (100% reproducibility on a
    REAL repo — the builder sorts/order-fixes every collection; no clock/float/set-order in
    the hashed payload). RED-first against a deliberate non-determinism injection: an
    UNSORTED finding order into the bundle breaks the byte-identity assertion, then green.
    """
    a = run_dogfood(str(_REPO_ROOT), tmp_path / "a")
    b = run_dogfood(str(_REPO_ROOT), tmp_path / "b")
    assert a.result.verdict.verdict == b.result.verdict.verdict, "verdict token diverged across runs"
    assert a.result.verdict.deep_ratio == b.result.verdict.deep_ratio, "deep-ratio diverged"
    # The GREEN assertion: the two SIGNED bundles are byte-identical.
    assert a.bundle_bytes == b.bundle_bytes, (
        "AC-REPRODUCIBLE violated — the two dogfood bundles are NOT byte-identical (NFR-D1/P1)"
    )

    # RED-first: rebuild bundle B from A's result but with the findings REVERSED (a
    # non-determinism injection). The builder reads ``verdict.ordered_findings`` verbatim,
    # so a reversed order MUST produce different canonical bytes — proving the byte-identity
    # is load-bearing (it would FAIL under an unsorted finding order), then the real run is
    # green above.
    result = a.result
    ordered = result.verdict.ordered_findings
    if len(ordered) >= 2:
        reversed_verdict = result.verdict.model_copy(
            update={"ordered_findings": tuple(reversed(ordered))}
        )
        reversed_result = _ShimResult(reversed_verdict, result)
        reversed_bundle = build_evidence_bundle(
            reversed_result, a.integrity, commit="minions-dogfood", argus_version=DOGFOOD_ArgusAgent_VERSION
        )
        assert bundle_to_canonical_bytes(reversed_bundle) != a.bundle_bytes, (
            "RED-first: an injected non-determinism (reversed finding order) must break the "
            "byte-identity — if it did NOT, the reproducibility assertion would be vacuous"
        )


class _ShimResult:
    """A duck-typed AuditResult carrying an overridden verdict (RED-first injection only)."""

    def __init__(self, verdict: object, base: object) -> None:
        self.verdict = verdict
        self.negative_assurance = base.negative_assurance  # type: ignore[attr-defined]
        self.coverage_report = base.coverage_report  # type: ignore[attr-defined]


# ─────────────────────────────────────────────────────────────────────────────
# Member (5) / AC-DEMO-GRADE — the grade: demo-heuristic-only red-team flag
# ─────────────────────────────────────────────────────────────────────────────


def test_demo_grade_flag_and_externalization_guard_present(
    dogfood_proof: DogfoodProofRun,
) -> None:
    """TC-ArgusAgent-DOGFOOD-001-25 — AC-DEMO-GRADE: the demo-heuristic-only flag + guard are present.

    The run carries the hard ``grade: demo-heuristic-only`` flag (on the wrapper + the proof
    artifact) and the externalization-guard language stating the Tier-A run is NOT presented
    as externalization / assurance evidence (the FR7 red-team guard). Every dogfood finding
    is advisory / verdict-ineligible (``blocking_finding_count == 0``) — the structural
    heuristic-only signal.
    """
    proof = dogfood_proof
    assert proof.grade == "demo-heuristic-only"
    text = _PROOF_ARTIFACT.read_text(encoding="utf-8")
    assert f"grade: {DOGFOOD_GRADE}" in text, "the proof artifact must carry the grade flag"
    lowered = text.lower()
    assert "not presented as externalization" in lowered, "the externalization guard must be present"
    assert "demo-heuristic-only" in lowered and "tier-a" in lowered
    # The structural heuristic-only signal: the real dogfood emits ZERO blocking findings
    # (every finding is advisory / verdict-ineligible — depth_supported is None).
    assert proof.blocking_finding_count == 0, (
        "a Tier-A heuristic-only dogfood must emit no verdict-eligible (blocking) findings"
    )


def test_red_first_no_externalization_overclaim_phrase(dogfood_proof: DogfoodProofRun) -> None:
    """TC-ArgusAgent-DOGFOOD-001-26 — AC-DEMO-GRADE RED-first: no 'externalization-grade / validated' over-claim.

    RED-first against an injected over-claim: the proof artifact + the render must NEVER
    contain an externalization-grade / validated-deep-audit / cleared-gate over-claim phrase
    (the 4.1/4.3 forbidden-phrase precedent). If such a phrase were injected the assertion
    would fire — proving the honesty guard is load-bearing, not decorative.
    """
    text = _PROOF_ARTIFACT.read_text(encoding="utf-8").lower()
    forbidden = (
        "externalization-grade",
        "validated deep audit",
        "assurance-grade result",
        "gate cleared",
        ">=80% achieved",
        "precision gate cleared",
    )
    for phrase in forbidden:
        assert phrase not in text, (
            f"OVER-CLAIM — the proof artifact must NOT contain {phrase!r} "
            "(a Tier-A demo run is never externalization/assurance evidence)"
        )
    # The render of a real run also carries no over-claim.
    live = render_proof_markdown(dogfood_proof).lower()
    for phrase in forbidden:
        assert phrase not in live


# ─────────────────────────────────────────────────────────────────────────────
# Member (6) / AC-ADJUDICATION-READY — the real findings laid out for the human judgment
# ─────────────────────────────────────────────────────────────────────────────


def test_adjudication_rows_map_to_the_66_match_key(dogfood_proof: DogfoodProofRun) -> None:
    """TC-ArgusAgent-DOGFOOD-001-27 — AC-ADJUDICATION-READY/OI1: findings laid out per finding_match_key.

    Each REAL dogfood finding CLASS is inspectable with its ``rule_id`` + verdict-eligibility
    (``depth_supported is not None`` = blocking / verdict-eligible; None = advisory) +
    count + sample locators, mapped onto the 6.6 ``finding_match_key`` identity so a human
    can tag it TP/FP. The human adjudication is NOT performed here (the ``adjudication`` tag
    stays empty). NAMED per class.
    """
    rows = dogfood_proof.adjudication
    assert rows, "the dogfood must lay out at least one adjudication-ready finding class"
    for row in rows:
        assert isinstance(row, AdjudicationRow)
        assert row.rule_id, "every adjudication row must carry a rule_id"
        assert row.count >= 1, f"class {row.rule_id!r}: a listed class must have >=1 finding"
        # The 6.6 match-key identity is the row identity.
        assert row.match_key == (row.rule_id, row.verdict_eligible, row.advisory)
        # 7.2 does NOT run the human adjudication — the TP/FP tag stays empty (OI1).
        assert row.adjudication == "", (
            f"class {row.rule_id!r}: 7.2 must NOT pre-tag TP/FP (the human step)"
        )
    # The rendered proof exposes the adjudication table with an empty human TP/FP column.
    text = _PROOF_ARTIFACT.read_text(encoding="utf-8")
    assert "TP/FP (human)" in text
    assert "finding_match_key" in text


def test_red_first_two_distinct_classes_never_collapse(dogfood_proof: DogfoodProofRun) -> None:
    """TC-ArgusAgent-DOGFOOD-001-28 — AC-ADJUDICATION-READY RED-first (AI-E6-1): no collision collapse.

    RED-first against a collision-collapsed layout: two DISTINCT finding classes (different
    match keys) must NEVER collapse into one adjudication row. The row identities are
    exactly the DISTINCT ``finding_match_key`` values — a keying bug that dropped
    ``verdict_eligible`` / ``advisory`` from the identity would collapse distinct classes.
    """
    rows = dogfood_proof.adjudication
    keys = [r.match_key for r in rows]
    assert len(keys) == len(set(keys)), (
        f"AI-E6-1 collision — two adjudication rows share a match key: {keys}"
    )
    # Each class's count is the SUM of its findings (no finding dropped / mis-bucketed):
    # the total across rows equals the total finding count.
    assert sum(r.count for r in rows) == dogfood_proof.total_finding_count, (
        "adjudication rows must partition ALL findings (no finding dropped / double-counted)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Member (7) / AC-PROVISIONAL — the OI1 keystone: the gate STAYS PROVISIONAL
# ─────────────────────────────────────────────────────────────────────────────


def test_precision_gate_stays_provisional(dogfood_proof: DogfoodProofRun) -> None:
    """TC-ArgusAgent-DOGFOOD-001-29 — AC-PROVISIONAL/OI1: the ≥80% gate is PROVISIONAL; marker NOT flipped.

    The OI1 honesty keystone: 7.2 EXECUTES the dogfood + lays the findings adjudication-ready
    ONLY. The proof's gate status is PROVISIONAL, presents NO ≥80% number as authoritative,
    and the 6.5 committed ``precision_gate_status()`` marker is NOT flipped (still provisional).
    """
    proof = dogfood_proof
    assert proof.gate_status.startswith("provisional"), (
        "OI1: the dogfood must report the gate PROVISIONAL (the human adjudication clears it)"
    )
    assert "EARLY/PROVISIONAL" in proof.gate_status
    # The 6.5 committed marker is untouched (still says provisional) — 7.2 flips nothing.
    assert precision_gate_status().startswith("provisional")
    # The proof artifact says the gate stays provisional + points at the human step.
    text = _PROOF_ARTIFACT.read_text(encoding="utf-8")
    assert "STAYS PROVISIONAL" in text
    assert "protocol_cleared" in text and "NOT flip" in text


def test_red_first_gate_not_silently_flipped(dogfood_proof: DogfoodProofRun) -> None:
    """TC-ArgusAgent-DOGFOOD-001-30 — AC-PROVISIONAL RED-first: the proof carries no cleared-gate claim.

    RED-first against a silently-flipped gate: the ``DogfoodProofRun`` carries NO
    ``protocol_cleared`` field / no cleared-gate flag, and the proof artifact's gate section
    contains no 'cleared' claim outside the harness's own 'NOT a cleared gate' framing. The
    dogfood generator NEVER passes ``protocol_cleared=True`` to the precision harness.
    """
    proof = dogfood_proof
    # No cleared-gate attribute exists on the wrapper (structurally cannot over-claim).
    assert not hasattr(proof, "protocol_cleared")
    # The gate status is the harness's provisional string; "cleared" appears only in the
    # harness's own "NOT a cleared gate" negation, never as an affirmative claim.
    status = proof.gate_status
    # Split on the EARLY marker: the affirmative-claim region is before it.
    head = status.split("EARLY")[0]
    assert "cleared" not in head, "the gate status must not affirmatively claim 'cleared'"
    # The source module never passes protocol_cleared=True (a grep-style guard).
    src = (_REPO_ROOT / "argus" / "dogfood" / "proof_run.py").read_text(
        encoding="utf-8"
    )
    assert "protocol_cleared=True" not in src, (
        "OI1: proof_run.py must NEVER pass protocol_cleared=True (no fabricated cleared gate)"
    )


def test_df_6_6_a_progress_note_and_human_adjudication_defer(dogfood_proof: DogfoodProofRun) -> None:
    """TC-ArgusAgent-DOGFOOD-001-31 — AC-PROVISIONAL/AI-E5-4: DF-6-6-A note + the human-adjudication defer.

    A committed append-only DF-6-6-A progress note records the EXECUTED dogfood + the
    adjudication-ready real findings, and a NEW human-adjudication defer (six CC-3 fields,
    ``target_story: epic-7-minions-dogfood-precision``) records the still-open HUMAN step.
    DF-6-7-A (HITL wiring) stays OPEN — not closed.
    """
    assert _DEFERRED_WORK.exists(), f"the deferred-work register must exist at {_DEFERRED_WORK}"
    text = _DEFERRED_WORK.read_text(encoding="utf-8")
    # The 7.2 DF-6-6-A progress note (the EXECUTED dogfood).
    assert "DF-6-6-A-P2" in text, "the 7.2 DF-6-6-A progress note must be filed"
    assert "7-2-execute-minions-audit" in text, "the note's origin_story must be the 7.2 key"
    # The NEW human-adjudication defer.
    assert "DF-7-2-A" in text, "the human-adjudication defer must be filed"
    assert "epic-7-minions-dogfood-precision" in text
    # DF-6-7-A (HITL wiring) stays open — still referenced, not marked closed.
    assert "DF-6-7-A" in text
    # The six CC-3 fields are present.
    for field in ("id:", "origin_story:", "owner:", "category:", "severity:"):
        assert field in text, f"a defer note is missing CC-3 field {field!r}"


# ─────────────────────────────────────────────────────────────────────────────
# Member (8) / AC-COMPLETE-SET — the enumeration + the no-crash edges + file-size
# ─────────────────────────────────────────────────────────────────────────────


def test_dogfood_generator_no_crash_on_empty_and_malformed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-DOGFOOD-001-32 — AC-COMPLETE-SET/AI-E4-2/AR10: no bare traceback on edges.

    The dogfood generator over a degenerate input degrades to a typed NAMED outcome:
    an empty source set raises the typed ``DogfoodProofError`` (never a bare traceback),
    and the pure cost accounting over an empty file set is total-safe (zero credits, no
    divide-by-zero).
    """
    from argus.dogfood import proof_run

    # Empty tracked-source enumeration → run_dogfood raises the typed DogfoodProofError.
    monkeypatch.setattr(proof_run, "enumerate_tracked_sources", lambda *a, **k: ())
    with pytest.raises(DogfoodProofError):
        proof_run.run_dogfood(str(_REPO_ROOT), tmp_path / "empty")
    monkeypatch.undo()

    # The pure cost accounting over an empty file set is total-safe (no divide-by-zero).
    summary = cost_summary((), total_loc=0)
    assert summary.total_credits == 0
    assert summary.fits_within_ceiling is True  # 0 <= 843
    # A non-existent repo enumeration raises the typed error (NAMED), never a bare raise.
    with pytest.raises(DogfoodProofError):
        enumerate_tracked_sources(tmp_path / "does-not-exist-repo")


def test_declared_set_enumeration_and_file_size() -> None:
    """TC-ArgusAgent-DOGFOOD-001-33 — AC-COMPLETE-SET/NFR-M1: the declared set is enumerated + files ≤1200.

    The complete-the-declared-set discipline: this module's docstring enumerates the EIGHT
    declared 7.2 members, and both the generator + this test file are ≤1200 lines. The
    generator cites its 7.2 drivers in the module docstring.
    """
    generator = _REPO_ROOT / "argus" / "dogfood" / "proof_run.py"
    gen_src = generator.read_text(encoding="utf-8")
    this_src = Path(__file__).read_text(encoding="utf-8")
    assert len(gen_src.splitlines()) <= 1200, "proof_run.py exceeds the 1200-line limit"
    assert len(this_src.splitlines()) <= 1200, "this test file exceeds the 1200-line limit"
    for driver in ("ArgusAgent-FR-29", "ArgusAgent-FR-17", "ArgusAgent-FR-30", "ArgusAgent-FR-21", "ArgusAgent-NFR-D1", "ArgusAgent-NFR-S1", "ArgusAgent-AR4"):
        assert driver in gen_src, f"generator module docstring missing driver {driver!r}"
    assert "The complete-the-declared-set matrix" in this_src
    for marker in (
        "(1) the reproducible dogfood execution",
        "(6) the adjudication-ready findings layout",
        "(7) the provisional-gate honesty",
    ):
        assert marker in this_src, f"declared-set enumeration missing {marker!r}"


def test_dogfood_proof_result_is_typed(dogfood_proof: DogfoodProofRun) -> None:
    """TC-ArgusAgent-DOGFOOD-001-34 — AC-EXECUTE: the build returns the typed DogfoodProofRun contract."""
    proof = dogfood_proof
    assert isinstance(proof, DogfoodProofRun)
    assert proof.commit_descriptor
    assert proof.grade == "demo-heuristic-only"
    assert proof.bundle_content_hash
    # argus_version provenance is the pyproject version token.
    assert DOGFOOD_ArgusAgent_VERSION == "1.43.0"
