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
  (9) Story 8.5 / DR-10 — the artifact matches the SHIPPED verdict contract → TC-...-35..44
Every assertion NAMES the unit / finding class / cartridge id (the AI-E4-2 no-crash leg).

STORY 8.5 (DR-10) — why members (9) exist. Epic 8 amended what a verdict MEANS, and this
repository was publishing proof/verdict artifacts that contradicted the shipped contract
(a blocking verdict beside zero blocking findings) AND that named a repository the
generator never audits (``enumerate_tracked_sources`` defaults to ``scope_prefix="argus"``
— the dogfood is a SELF-audit of this package). Members (9) pin the DISCLOSURES that make
the artifact falsifiable rather than trustworthy: the LITERAL decision row, the honest
subject + resolvable citations, the impossible-state end-to-end guard, the ceiling honesty
pair, the preserved supersession record, and the vacuous-vs-real critical-gate split.

THE OI1 LOCK (DN-PROVISIONAL — read twice): the ≥80%-precision gate STAYS PROVISIONAL.
Story 7.2 EXECUTES the dogfood + produces the REAL findings + lays them ADJUDICATION-READY
ONLY. The human TP/FP adjudication that clears the gate is a human step. ``protocol_cleared``
is NEVER flipped and the ``precision_gate_status()`` marker is NEVER flipped —
over-claiming a cleared gate / presenting a Tier-A demo run as externalization evidence is
the exact failure mode this lock forbids (RED-first in TC-...-26 / TC-...-30).
"""

from __future__ import annotations

import re
import sys
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402
from _registry import precision_gate_status  # noqa: E402

import argus  # noqa: E402
from argus.dogfood import proof_run as proof_run_module  # noqa: E402
from argus.dogfood.partition_plan import build_full_repo_plan  # noqa: E402
from argus.dogfood.proof_run import (  # noqa: E402
    DOGFOOD_ArgusAgent_VERSION,
    DOGFOOD_BUDGET_CEILING,
    DOGFOOD_GRADE,
    AdjudicationRow,
    CriticalClauseDisclosure,
    DogfoodProofError,
    DogfoodProofRun,
    build_dogfood_proof,
    cost_summary,
    enumerate_tracked_sources,
    render_proof_markdown,
    run_dogfood,
)
from argus.pipeline_persist import CRITICAL_SUBSYSTEMS_PRODUCER  # noqa: E402
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.store.writer import ApaaStoreWriter  # noqa: E402
from argus.verdict.verdict_gate import DecisionRow  # noqa: E402
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
# Story 8.5 / AC5 — the RS-3 "supersede, don't erase" preservation of the Story-7.2
# Minions run whose bytes the re-derivation would otherwise have destroyed.
_SUPERSEDED_PROOF = (
    _REPO_ROOT
    / "_bmad-output"
    / "design-artifacts"
    / "ArgusAgent"
    / "minions-dogfood-proof-story-7-2-superseded.md"
)
# The two sibling plan artifacts, re-derived by the same story and subject to the SAME
# citation-resolution guard (Story 8.5 / AC2 last clause, AC6).
_PARTITION_PLAN_8_5 = (
    _REPO_ROOT
    / "_bmad-output"
    / "design-artifacts"
    / "ArgusAgent"
    / "minions-dogfood-partition-plan.md"
)
_BUDGET_PLAN_8_5 = (
    _REPO_ROOT
    / "_bmad-output"
    / "design-artifacts"
    / "ArgusAgent"
    / "minions-dogfood-budget-plan.md"
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
    # No source module in the dogfood generator ever passes protocol_cleared=True (a
    # grep-style guard). Story 9.2 / DF-8-5-D split the generator into three modules;
    # scanning only proof_run.py would have left the renderer and the type contract
    # outside the guard the moment the split landed — the blind-spot class AI-E8-2
    # names. The enumeration is the whole dogfood package, so a NEW module is covered
    # the moment it is added rather than when someone remembers to register it.
    dogfood_modules = sorted(
        p for p in (_REPO_ROOT / "argus" / "dogfood").glob("*.py")
    )
    assert len(dogfood_modules) >= 4, f"only {len(dogfood_modules)} dogfood modules found"
    for module in dogfood_modules:
        src = module.read_text(encoding="utf-8")
        assert "protocol_cleared=True" not in src, (
            f"OI1: {module.name} must NEVER pass protocol_cleared=True "
            "(no fabricated cleared gate)"
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
    # Story 9.2 / DF-8-5-D: the generator is now three modules. Check EVERY module in
    # the package against the ceiling, not just the one this test was written around —
    # otherwise an extraction that relieves one file silently removes its siblings from
    # the NFR-M1 guard.
    for module in sorted((_REPO_ROOT / "argus" / "dogfood").glob("*.py")):
        n_lines = len(module.read_text(encoding="utf-8").splitlines())
        assert n_lines <= 1200, f"{module.name} is {n_lines} lines, over the 1200 limit"
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
    # argus_version provenance is the SINGLE ArgusAgent-owned constant `argus.__version__`
    # (Story 9.2 / DF-8-5-A) — never a module literal. The pre-9.2 wording of this comment
    # claimed "the pyproject version token" while the assertion pinned "1.43.0" against a
    # pyproject that reads 0.1.0, so the comment documented a provenance the code did not
    # have. Assert AGREEMENT with the constant rather than a second copy of its value: a
    # literal here would re-introduce exactly the drift the fix removed.
    assert DOGFOOD_ArgusAgent_VERSION == argus.__version__


# ─────────────────────────────────────────────────────────────────────────────
# Member (9) / Story 8.5 (DR-10) — the artifact matches the SHIPPED verdict contract
# ─────────────────────────────────────────────────────────────────────────────

# Claim substrings (lowercased) that assert a tree the dogfood does NOT audit, or cite a
# path that does not exist. Each was GENUINELY rendered by the pre-8.5 generator into the
# committed artifact; the RED-first demonstration is the pre-fix artifact itself.
_FALSE_SUBJECT_CLAIMS: tuple[str, ...] = (
    "the real minions repo",
    "real minions platform source",
    "the audited bytes are the real minions source",
    "tracked `minions_core/`",
    "minions_core/",
    "tests/argus/",
    "tests/security/",
)

# A backticked token that LOOKS like a repo file path: optional dirs, a known source /
# document suffix, optionally followed by a ``:line`` locator.
_PATH_TOKEN = re.compile(r"`([A-Za-z0-9_.\-/]+\.(?:py|md|yaml|toml))(?::\d+)?`")
# A backticked token that LOOKS like a repo DIRECTORY: path segments ending in ``/``.
# AC11b demands that every path an artifact CITES resolves — not every path that happens
# to carry a file suffix. A suffix-only guard is structurally blind to the exact defect
# the 8.5 review found: all three artifacts rendered "excluding `argus/tests/`" while the
# tests are flat under `tests/`, so the clause asserted a held-out sub-tree that does not
# exist. This pattern is generic; nothing about `argus/tests/` is special-cased.
_DIR_TOKEN = re.compile(r"`([A-Za-z0-9_.\-]+(?:/[A-Za-z0-9_.\-]+)*/)`")


def _cited_paths_resolve(artifact: Path) -> list[str]:
    """Return every backticked path token in *artifact* that resolves to NOTHING on disk.

    Covers BOTH file-shaped and directory-shaped citations. A citation is resolved against
    the repository root first, then against the artifact's own directory (sibling
    artifacts are cited by bare filename); a directory token must resolve to a directory,
    so a stale prefix cannot be excused by a same-named file. Anything left over is a
    dangling citation — the defect class Story 8.5 / AC2 exists to delete.
    """
    text = artifact.read_text(encoding="utf-8")
    dangling: list[str] = []
    for token in sorted(set(_PATH_TOKEN.findall(text))):
        if (_REPO_ROOT / token).exists() or (artifact.parent / token).exists():
            continue
        dangling.append(token)
    for token in sorted(set(_DIR_TOKEN.findall(text))):
        if (_REPO_ROOT / token).is_dir() or (artifact.parent / token).is_dir():
            continue
        dangling.append(token)
    return sorted(dangling)


def test_artifact_discloses_the_live_decision_row(dogfood_proof: DogfoodProofRun) -> None:
    """TC-ArgusAgent-DOGFOOD-001-35 — Story 8.5/AC1/AC11a: the artifact discloses the LIVE DecisionRow.

    DR-3: the artifact must record WHICH row of the binding FR16 table fired, by its
    literal ``DecisionRow`` value — not a paraphrase and not a re-derivation from the
    verdict token (rows 1 and 4 both render ``INSUFFICIENT_COVERAGE`` / exit ``3``, so
    inferring the row from the token states a falsehood for one of them). The value the
    run carries must be a real closed-enum member, must appear verbatim in the committed
    markdown, and must be CONSISTENT with the verdict token it was disclosed beside.
    """
    proof = dogfood_proof
    valid = {row.value for row in DecisionRow}
    assert proof.decision_row in valid, (
        f"the run must carry a literal DecisionRow value; got {proof.decision_row!r}"
    )
    text = _PROOF_ARTIFACT.read_text(encoding="utf-8")
    assert f"`{proof.decision_row}`" in text, (
        f"the committed proof must disclose the live decision row {proof.decision_row!r} "
        "(rot? re-run the generator)"
    )
    # The row and the verdict token cannot disagree — the row IS the reasoning behind it.
    row_to_verdicts = {
        DecisionRow.BELOW_FLOOR.value: {"INSUFFICIENT_COVERAGE"},
        DecisionRow.BLOCKING_FINDINGS.value: {"NOT_READY_FOR_RELEASE"},
        DecisionRow.GATES_MET.value: {"RELEASE_READY"},
        DecisionRow.GATE_UNMET_NO_FINDINGS.value: {"INSUFFICIENT_COVERAGE"},
    }
    assert proof.verdict in row_to_verdicts[proof.decision_row], (
        f"row {proof.decision_row!r} cannot produce verdict {proof.verdict!r}"
    )


def test_artifact_names_its_real_subject_and_every_citation_resolves() -> None:
    """TC-ArgusAgent-DOGFOOD-001-36 — Story 8.5/AC2/AC11b: honest subject + resolvable citations.

    ``enumerate_tracked_sources`` defaults to ``scope_prefix="argus"``: the dogfood audits
    THIS repository's own package and never the Minions platform. The committed artifact
    must therefore make NO Minions-source-audited claim, must state plainly that it is a
    SELF-audit, and EVERY file path it cites must resolve on disk (the pre-8.5 artifact
    cited three paths that do not exist). NAMED per offending claim / citation.
    """
    text = _PROOF_ARTIFACT.read_text(encoding="utf-8")
    lowered = text.lower()
    for claim in _FALSE_SUBJECT_CLAIMS:
        assert claim not in lowered, (
            f"FALSE SUBJECT — the proof artifact claims {claim!r}, but the dogfood "
            "enumerates scope_prefix='argus' (it audits THIS repository's own package)"
        )
    # The self-audit weakness is STATED, not left to the reader to infer.
    assert "self-audit" in lowered
    assert "argus auditing argus" in lowered
    assert "never independent corroboration" in lowered
    # Every cited path resolves (repo-root or artifact-sibling).
    for artifact in (_PROOF_ARTIFACT, _PARTITION_PLAN_8_5, _BUDGET_PLAN_8_5):
        dangling = _cited_paths_resolve(artifact)
        assert not dangling, (
            f"DANGLING CITATION in {artifact.name}: {dangling} — an artifact that cites a "
            "path which does not exist is asserting a falsehood"
        )


def test_real_dogfood_never_blocks_without_a_finding(dogfood_proof: DogfoodProofRun) -> None:
    """TC-ArgusAgent-DOGFOOD-001-37 — Story 8.5/AC11c: the end-to-end impossible-state guard.

    THE symptom this whole epic exists to delete: a blocking verdict carrying ZERO
    blocking findings. Under the amended FR16 table only row 2 renders
    ``NOT_READY_FOR_RELEASE``, and row 2 requires ``blocking_finding_count >= 1``. Asserted
    end-to-end on the REAL dogfood run (the module-scoped fixture, so it costs no extra
    runtime) and on the committed artifact, because a unit-level table test cannot prove
    the wiring produces it.
    """
    proof = dogfood_proof
    assert not (proof.verdict == "NOT_READY_FOR_RELEASE" and proof.blocking_finding_count == 0), (
        "IMPOSSIBLE STATE — the real dogfood returned NOT_READY_FOR_RELEASE with "
        f"blocking_finding_count=0 (row {proof.decision_row!r}); under the amended FR16 "
        "table only row 2 blocks and row 2 requires >=1 blocking finding"
    )
    if proof.verdict == "NOT_READY_FOR_RELEASE":
        assert proof.decision_row == DecisionRow.BLOCKING_FINDINGS.value
    text = _PROOF_ARTIFACT.read_text(encoding="utf-8")
    blocks = "`NOT_READY_FOR_RELEASE` (exit `2`)" in text
    zero_blocking = "Blocking (verdict-eligible) findings: **0**" in text
    assert not (blocks and zero_blocking), (
        "the committed proof artifact pairs a blocking verdict with zero blocking "
        "findings — the exact published contradiction DR-10 deletes"
    )


def test_artifact_states_the_ceiling_honesty_pair(dogfood_proof: DogfoodProofRun) -> None:
    """TC-ArgusAgent-DOGFOOD-001-38 — Story 8.5/AC1/AC11d/D7: BOTH ceilings, with a fit for each.

    ``$X`` = ``DOGFOOD_BUDGET_CEILING`` is a FROZEN historical execution parameter; the 7.1
    generator re-sizes its ceiling from the live tree on every derivation. Publishing only
    one of the two lets the proof artifact and the budget artifact — regenerated together —
    disagree about what "the 7.1 empirical ceiling" is. The run must carry BOTH, the live
    figure must be the one ``build_full_repo_plan`` actually derives (no second
    accountant, AR7), and both must be rendered with an explicit fit verdict.
    """
    cost = dogfood_proof.cost
    assert cost.ceiling == DOGFOOD_BUDGET_CEILING == 843, "the frozen $X must not float"
    live = build_full_repo_plan(str(_REPO_ROOT)).budget.sized_ceiling
    assert cost.live_sized_ceiling == live, (
        f"the proof's live ceiling {cost.live_sized_ceiling} must be the SAME sizing the "
        f"7.1 generator derives ({live}) — a divergence means a forked accountant"
    )
    assert isinstance(cost.fits_within_live_sized_ceiling, bool)
    text = _PROOF_ARTIFACT.read_text(encoding="utf-8")
    assert str(cost.ceiling) in text and str(cost.live_sized_ceiling) in text, (
        "the artifact must state BOTH the frozen $X and the live 7.1 sizing"
    )
    assert "ceiling honesty pair" in text.lower()
    assert f"Fits under the frozen `$X` = {cost.ceiling}: **{cost.fits_within_ceiling}**" in text
    assert (
        f"Fits under the live 7.1 sizing = {cost.live_sized_ceiling}: "
        f"**{cost.fits_within_live_sized_ceiling}**"
    ) in text


def test_superseded_story_7_2_record_is_preserved_verbatim() -> None:
    """TC-ArgusAgent-DOGFOOD-001-39 — Story 8.5/AC5/AC11e: the Minions record survives regeneration.

    Regenerating ``minions-dogfood-proof.md`` OVERWRITES the only surviving on-disk record
    of the real Story-7.2 Minions run — the 135-file / 36712-LOC execution whose three
    finding classes (332 / 2289 / 285) are the substrate ``DF-7-2-A``'s human TP/FP
    adjudication is DEFINED over, and which can never be re-derived here because Minions
    source is not in this repository. §3.4 evidence immutability / RS-3 say supersede,
    don't erase: the original bytes must be preserved at a sibling path, beneath a header
    that says so, with pointers in both directions.
    """
    assert _SUPERSEDED_PROOF.exists(), (
        f"the preserved Story-7.2 record must exist at {_SUPERSEDED_PROOF}"
    )
    preserved = _SUPERSEDED_PROOF.read_text(encoding="utf-8")
    # The DISTINCTIVE bytes of the original run — provenance, scale and the three
    # adjudication classes at their recorded counts.
    for token in (
        "7f8e1478573d3208c1df16aaaaa4f6f0bb0afea0",   # the 7.2 commit descriptor
        "c0c4c35e1d32b5d435064bfdbf01550f2fb8acd16abde3413fc595dd7c72341b",  # bundle hash
        "**135**",                                     # source files audited
        "**36712**",                                   # total LOC
        "| 332 |",                                     # cross_partition class count
        "| 2289 |",                                    # hardcoded_secret class count
        "| 285 |",                                     # orphan_code class count
    ):
        assert token in preserved, (
            f"the preserved record lost the distinctive Story-7.2 byte {token!r} — the "
            "supersession must keep the original body VERBATIM"
        )
    # The header states the method honestly and refuses to pick a row it cannot know.
    lowered = preserved.lower()
    assert "no new audit was executed over minions" in lowered
    assert "cannot** produce `not_ready_for_release`" in lowered or (
        "cannot produce `not_ready_for_release`" in lowered
    )
    assert "does not assert" in lowered, "the header must refuse to pick row 3 vs row 4"
    # Pointers in BOTH directions.
    assert "minions-dogfood-proof.md" in preserved, "forward pointer missing"
    assert _SUPERSEDED_PROOF.name in _PROOF_ARTIFACT.read_text(encoding="utf-8"), (
        "the re-derived artifact must carry a back pointer to the preserved record"
    )


def test_red_first_vacuously_satisfied_critical_gate_is_named(
    dogfood_proof: DogfoodProofRun,
) -> None:
    """TC-ArgusAgent-DOGFOOD-001-40 — Story 8.5/AC1 (boundary B3 / inversion F1): vacuous gate visible.

    Epic 8 LOOSENS the critical gate twice and nothing guards the PRD-fatal
    false-``RELEASE_READY`` direction. A green verdict whose critical clause held because
    the critical set was EMPTY is a vacuously satisfied gate and MUST be visible. RED-first
    against a rendered proof whose retrieved set is empty: the artifact must say VACUOUSLY
    for that input and must NOT say it for the live run's real, non-empty set.
    """
    proof = dogfood_proof
    assert proof.critical is not None, "the run must disclose the critical-clause state"
    live_text = render_proof_markdown(proof)
    # The live disclosure names the set size, the DR-5 exclusions and the unmatched paths.
    assert f"Critical-set size (`CriticalSubsystemSet.paths`): **{proof.critical.set_size}**" in live_text
    assert "DR-5 eligibility filter removed" in live_text
    assert "designated_but_unmatched" in live_text
    # RED-first injection: the SAME renderer over an EMPTY-but-retrieved set must name the
    # gate vacuous. If it did not, the non-vacuity assertion below would be decorative.
    empty = CriticalClauseDisclosure(all_deep=True, set_retrieved=True, set_size=0)
    vacuous_text = render_proof_markdown(replace(proof, critical=empty))
    assert "VACUOUSLY satisfied" in vacuous_text, (
        "B3 violated — an EMPTY critical set must be reported as a VACUOUSLY satisfied "
        "gate, never as a satisfied one"
    )
    # An unretrieved set is reported as unread, never as empty (no fabricated vacuity).
    unread = CriticalClauseDisclosure(all_deep=True, set_retrieved=False)
    unread_text = render_proof_markdown(replace(proof, critical=unread))
    assert "could NOT be read back" in unread_text
    assert "VACUOUSLY" not in unread_text
    # The committed artifact carries whichever case the live run actually produced.
    committed = _PROOF_ARTIFACT.read_text(encoding="utf-8")
    if proof.critical.vacuously_satisfied:
        assert "VACUOUSLY satisfied" in committed
    else:
        assert "VACUOUSLY satisfied" not in committed
        assert f"Critical-set size (`CriticalSubsystemSet.paths`): **{proof.critical.set_size}**" in committed


# ─────────────────────────────────────────────────────────────────────────────
# Story 8.5 code review, iteration 1 — the four behavioural patches, pinned
# ─────────────────────────────────────────────────────────────────────────────


def test_citation_guard_covers_directories_and_exclusions_are_measured(
    dogfood_proof: DogfoodProofRun, tmp_path: Path
) -> None:
    """TC-ArgusAgent-DOGFOOD-001-42 — Story 8.5/AC2/AC11b (review it.1): a directory IS a citation.

    Two halves of one defect. (a) The AC11b guard only matched tokens ending in a file
    suffix, so a backticked DIRECTORY citation was structurally outside it — which is how
    all three artifacts came to render "excluding ``argus/tests/``" when no such directory
    exists (tests are flat under ``tests/``), telling a reader a sub-tree was held out of
    the 69-file population when nothing was held out at all. (b) The generator now renders
    only the exclusions the enumerator MEASURABLY applied, so a stale or renamed prefix
    can never be published as a held-out sub-tree. RED-first on a deliberately-stale
    artifact, because an assertion never shown to fail is not a rot check.
    """
    stale = tmp_path / "deliberately-stale-artifact.md"
    stale.write_text(
        "Source files (tracked `argus/`, excluding `argus/tests/`) — generated by "
        "`argus/dogfood/proof_run.py`.\n",
        encoding="utf-8",
    )
    assert _cited_paths_resolve(stale) == ["argus/tests/"], (
        "the citation guard must flag a backticked DIRECTORY that resolves to nothing; "
        "AC11b says EVERY path an artifact cites must resolve, not every file path"
    )
    # (b) Whatever the run rendered as excluded, it measurably held >=1 tracked file out.
    tracked_unfiltered = enumerate_tracked_sources(_REPO_ROOT, exclude_prefixes=())
    assert tracked_unfiltered, "the un-excluded enumeration is the measurement baseline"
    for prefix in dogfood_proof.effective_exclude_prefixes:
        assert any(f.startswith(prefix) for f in tracked_unfiltered), (
            f"{prefix!r} is rendered as an exclusion but held NO tracked file out"
        )
    rendered = render_proof_markdown(dogfood_proof)
    for prefix in dogfood_proof.exclude_prefixes:
        if prefix not in dogfood_proof.effective_exclude_prefixes:
            assert f"excluding `{prefix}`" not in rendered, (
                f"{prefix!r} matched nothing and must not be rendered as an exclusion"
            )
    # The configured set is still recorded on the run — measured, not silently dropped.
    assert dogfood_proof.exclude_prefixes == proof_run_module._DEFAULT_EXCLUDE_PREFIXES


def test_optional_critical_set_read_degrades_and_refuses_ambiguity(
    dogfood_proof: DogfoodProofRun, tmp_path: Path
) -> None:
    """TC-ArgusAgent-DOGFOOD-001-43 — Story 8.5 review it.1: an OPTIONAL disclosure never aborts.

    The critical-set read-back is an OPTIONAL disclosure on an artifact whose §3 REPORTS
    store integrity. Re-raising ANY ``state/`` read failure as fatal meant a store the 4.2
    lint would have reported as ``integrity_consistent: False`` could no longer produce
    the artifact that reports it. It now degrades to ``set_retrieved=False`` plus a
    MEASURED reason, which the renderer prints. Separately: filenames are
    content-addressed, so ``sorted`` is lexicographic and NOT recency — two envelopes
    claiming the producer is an ambiguity that must raise, never a coin flip disclosed as
    fact.
    """
    writer = ApaaStoreWriter(tmp_path)
    writer.paths.ensure_tree()
    reader = ApaaStoreReader(tmp_path)

    # (a) An UNRELATED, unreadable envelope degrades — it does not abort.
    unrelated = writer.write_payload(
        "state",
        {"note": "unrelated"},
        schema_version="1",
        producer="argus.pipeline.some_other_producer",
    )
    on_disk = writer.paths.resolve(unrelated)
    on_disk.write_bytes(on_disk.read_bytes().replace(b"unrelated", b"tampered!"))
    with pytest.raises(Exception):
        reader.read_envelope(unrelated)  # the tamper guard genuinely fires
    found, note = proof_run_module._read_critical_subsystem_set(reader)
    assert found is None, "no producer-matching envelope was written yet"
    assert unrelated in note and "unreadable" in note, (
        f"the degraded reason must NAME the unreadable locator; got {note!r}"
    )
    # The renderer states that measured reason instead of asserting an empty set.
    unread_text = render_proof_markdown(
        replace(
            dogfood_proof,
            critical=CriticalClauseDisclosure(
                all_deep=True, set_retrieved=False, retrieval_note=note
            ),
        )
    )
    assert "could NOT be read back" in unread_text and "MEASURED reason" in unread_text
    assert "VACUOUSLY" not in unread_text

    # (b) The real set is still found DESPITE the unreadable sibling.
    writer.write_payload(
        "state", {"paths": ["a.py"]}, schema_version="1", producer=CRITICAL_SUBSYSTEMS_PRODUCER
    )
    retrieved, clean_note = proof_run_module._read_critical_subsystem_set(reader)
    assert retrieved is not None and retrieved.paths == ("a.py",)
    assert clean_note == "", "a successful read reports no degradation reason"

    # (c) A SECOND producer-matching envelope is ambiguous and raises the typed error.
    writer.write_payload(
        "state", {"paths": ["b.py"]}, schema_version="1", producer=CRITICAL_SUBSYSTEMS_PRODUCER
    )
    with pytest.raises(DogfoodProofError) as ambiguous:
        proof_run_module._read_critical_subsystem_set(reader)
    message = str(ambiguous.value)
    assert "ambiguous" in message and str(tmp_path) not in message, (
        "the typed error must name the ambiguity with RELATIVE locators only (NFR-S1)"
    )


def test_live_sizing_sentinel_separates_absent_from_zero(
    dogfood_proof: DogfoodProofRun,
) -> None:
    """TC-ArgusAgent-DOGFOOD-001-44 — Story 8.5 review it.1: ``0`` is a sizing, not an absence.

    ``live_sized_ceiling`` once used ``0`` as its "absent" sentinel, so a genuinely-zero
    live sizing (an empty tree is a legitimate derivation — the 7.1 generator has an
    explicit no-crash empty-repo leg) would have been PUBLISHED as "not supplied to this
    derivation": a false statement about what the generator was actually given. The
    sentinel is now ``None``, matching :class:`CriticalClauseDisclosure.set_retrieved`,
    which exists to refuse exactly this ambiguity.
    """
    absent = cost_summary(("a.py",), total_loc=10)
    zero = cost_summary(("a.py",), total_loc=10, live_sized_ceiling=0)
    assert absent.live_sized_ceiling is None
    assert zero.live_sized_ceiling == 0, "a supplied 0 must survive as 0, never as absent"

    absent_text = render_proof_markdown(replace(dogfood_proof, cost=absent))
    zero_text = render_proof_markdown(replace(dogfood_proof, cost=zero))
    assert "not supplied to this derivation" in absent_text
    assert "not supplied to this derivation" not in zero_text, (
        "a derivation that WAS given a zero ceiling must not be reported as un-supplied"
    )
    assert (
        f"Fits under the live 7.1 sizing = 0: **{zero.fits_within_live_sized_ceiling}**"
    ) in zero_text
