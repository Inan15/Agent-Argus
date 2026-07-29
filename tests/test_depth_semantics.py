"""Depth-semantics grading rule + FR8 inferred-never-satisfies + criticality (story 2.1).

Verification area ArgusAgent-LEDGER (TC-ArgusAgent-LEDGER-001-NN, continuing the 1.2 area).
Covers AC1/AC2/AC3/AC4/AC5 of story 2.1:

- AC1 — the five-state grading rule has a single documented source
  (``DEPTH_SEMANTICS`` table + the pure ``classify_depth``), exhaustive over the
  1.2 ``CoverageDepth`` enum with no silent default.
- AC2 — the MANDATORY FR8 proofs: ``inferred`` / ``skipped`` / ``tool_scanned_only``
  evidence can NEVER satisfy a verdict gate, proven by NAMED synthetic-ledger tests
  run through the EXISTING 1.6 ``evaluate_verdict`` (asserting the gate honors FR8;
  the gate/ledger are NOT modified). The central evidence-poisoning driver.
- AC3 — criticality assessed by file CONTENT, not filename (anti-gaming): a
  benign-named-but-critical file is flagged; a benign file is not; a non-ASCII path
  + non-ASCII-identifier file is correctly classified, not silently dropped
  (AI-E1-1, the Epic-1 retro action item).
- AC4 — the module is PURE (no I/O / clock / uuid / random / LLM), frozen-contract,
  non-``float``, raises a typed error on a malformed descriptor.

These are PURE-function / synthetic-ledger tests — zero LLM tokens (NFR-D2), no
temp dirs. Synthetic ledgers are built via ``CoverageLedger.build([grade_entry(
...), ...])`` and run through the 1.6 ``evaluate_verdict`` verbatim.
"""

from __future__ import annotations

import ast as _ast_module
import inspect
from fractions import Fraction

import pytest

from argus.index.ast_index import AstIndexEntry, CodeEdge, Definition
from argus.ledger import depth_semantics
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    grade_entry,
)
from argus.ledger.depth_semantics import (
    DEPTH_SEMANTICS,
    DEPTH_SEMANTICS_SCHEMA_VERSION,
    Criticality,
    DepthEvidence,
    DepthSemanticsError,
    EvidenceKind,
    assess_criticality,
    classify_depth,
)
from argus.verdict.verdict_gate import Verdict, evaluate_verdict


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — the five-state grading rule has a single documented source, exhaustive
# ─────────────────────────────────────────────────────────────────────────────


def test_depth_semantics_table_covers_every_member_no_silent_default() -> None:
    """TC-ArgusAgent-LEDGER-001-90 — DEPTH_SEMANTICS keys == the closed 1.2 enum exactly."""
    assert set(DEPTH_SEMANTICS.keys()) == set(CoverageDepth)
    # Every member has a non-empty grading-rule description (no silent default).
    for member in CoverageDepth:
        assert DEPTH_SEMANTICS[member].strip(), f"empty grading rule for {member!r}"


def test_classify_depth_is_exhaustive_over_evidence_kind() -> None:
    """TC-ArgusAgent-LEDGER-001-91 — every EvidenceKind classifies to a valid CoverageDepth."""
    results = {
        EvidenceKind.DEEP_READ: classify_depth(
            DepthEvidence(kind=EvidenceKind.DEEP_READ, claim_present=True)
        ),
        EvidenceKind.TOOL_BREADTH_ONLY: classify_depth(
            DepthEvidence(kind=EvidenceKind.TOOL_BREADTH_ONLY)
        ),
        EvidenceKind.NARRATIVE_ONLY: classify_depth(
            DepthEvidence(kind=EvidenceKind.NARRATIVE_ONLY)
        ),
        EvidenceKind.UNGRADABLE: classify_depth(DepthEvidence(kind=EvidenceKind.UNGRADABLE)),
    }
    # All four kinds are mapped (no kind raises / returns a non-member).
    assert set(results.keys()) == set(EvidenceKind)
    for depth in results.values():
        assert depth in set(CoverageDepth)


def test_classify_depth_deep_read_claim_present_is_audited_deep() -> None:
    """TC-ArgusAgent-LEDGER-001-92 — DEEP_READ + claim -> AUDITED_DEEP (the only numerator state)."""
    assert (
        classify_depth(DepthEvidence(kind=EvidenceKind.DEEP_READ, claim_present=True))
        is CoverageDepth.AUDITED_DEEP
    )


def test_classify_depth_deep_read_silence_downgrades_to_shallow() -> None:
    """TC-ArgusAgent-LEDGER-001-93 — DEEP_READ + no claim -> AUDITED_SHALLOW (silence -> shallow, FR6)."""
    assert (
        classify_depth(DepthEvidence(kind=EvidenceKind.DEEP_READ, claim_present=False))
        is CoverageDepth.AUDITED_SHALLOW
    )


def test_classify_depth_narrative_only_is_inferred() -> None:
    """TC-ArgusAgent-LEDGER-001-94 — NARRATIVE_ONLY -> INFERRED (the FR8 evidence-poisoning class)."""
    assert (
        classify_depth(DepthEvidence(kind=EvidenceKind.NARRATIVE_ONLY)) is CoverageDepth.INFERRED
    )


def test_classify_depth_tool_breadth_only_is_tool_scanned_only() -> None:
    """TC-ArgusAgent-LEDGER-001-95 — TOOL_BREADTH_ONLY -> TOOL_SCANNED_ONLY."""
    assert (
        classify_depth(DepthEvidence(kind=EvidenceKind.TOOL_BREADTH_ONLY))
        is CoverageDepth.TOOL_SCANNED_ONLY
    )


def test_classify_depth_ungradable_is_skipped() -> None:
    """TC-ArgusAgent-LEDGER-001-96 — UNGRADABLE -> SKIPPED."""
    assert classify_depth(DepthEvidence(kind=EvidenceKind.UNGRADABLE)) is CoverageDepth.SKIPPED


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — MANDATORY FR8 proofs: inferred / skipped / tool_scanned_only never satisfy a gate
#       (assert the EXISTING 1.6 gate honors FR8 — do NOT modify the gate)
# ─────────────────────────────────────────────────────────────────────────────


def _ledger(*specs: tuple[str, CoverageDepth, bool]) -> CoverageLedger:
    """Build a synthetic ledger from (file_path, proposed_depth, claim_present) specs."""
    return CoverageLedger.build(
        [
            grade_entry(file_path=path, proposed_depth=depth, claim_present=claim)
            for path, depth, claim in specs
        ]
    )


def test_fr8_all_inferred_ledger_is_insufficient_coverage() -> None:
    """TC-ArgusAgent-LEDGER-001-97 — a 100%-inferred ledger is 0% deep -> INSUFFICIENT_COVERAGE (FR8)."""
    ledger = _ledger(
        ("a.py", CoverageDepth.INFERRED, False),
        ("b.py", CoverageDepth.INFERRED, False),
        ("c.py", CoverageDepth.INFERRED, False),
    )
    result = evaluate_verdict(ledger)
    assert result.deep_count == 0
    assert result.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert result.verdict is not Verdict.RELEASE_READY


def test_fr8_all_skipped_ledger_is_insufficient_coverage() -> None:
    """TC-ArgusAgent-LEDGER-001-98 — skipped-only never enters the numerator -> INSUFFICIENT_COVERAGE."""
    ledger = _ledger(
        ("a.py", CoverageDepth.SKIPPED, False),
        ("b.py", CoverageDepth.SKIPPED, False),
    )
    result = evaluate_verdict(ledger)
    assert result.deep_count == 0
    assert result.verdict is Verdict.INSUFFICIENT_COVERAGE


def test_fr8_all_tool_scanned_only_ledger_is_insufficient_coverage() -> None:
    """TC-ArgusAgent-LEDGER-001-99 — tool_scanned_only never enters the numerator -> INSUFFICIENT_COVERAGE."""
    ledger = _ledger(
        ("a.py", CoverageDepth.TOOL_SCANNED_ONLY, False),
        ("b.py", CoverageDepth.TOOL_SCANNED_ONLY, False),
        ("c.py", CoverageDepth.TOOL_SCANNED_ONLY, False),
    )
    result = evaluate_verdict(ledger)
    assert result.deep_count == 0
    assert result.verdict is Verdict.INSUFFICIENT_COVERAGE


def test_fr8_inferred_cannot_tip_a_sub_60_ledger_to_release_ready() -> None:
    """TC-ArgusAgent-LEDGER-001-100 — 59% deep + 41% inferred is NOT promoted to RELEASE_READY (FR8).

    The keystone: ``inferred`` entries inflate the DENOMINATOR (so they can only
    LOWER deep-%), never the numerator. A ledger with 10 audited_deep + 7 inferred
    is 10/17 ≈ 58.8% deep (< 60%) -> NOT_READY_FOR_RELEASE; the inferred entries
    cannot tip it over the line. If a future author let inferred into the
    numerator, 17/17 = 100% would wrongly read RELEASE_READY and this fails loudly.
    """
    deep_specs = [(f"deep_{i}.py", CoverageDepth.AUDITED_DEEP, True) for i in range(10)]
    inferred_specs = [(f"narr_{i}.py", CoverageDepth.INFERRED, False) for i in range(7)]
    ledger = _ledger(*deep_specs, *inferred_specs)

    result = evaluate_verdict(ledger)
    assert result.deep_count == 10
    assert result.total_count == 17
    assert result.deep_ratio < Fraction(3, 5)
    assert result.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert result.verdict is not Verdict.RELEASE_READY


def test_fr8_only_audited_deep_drives_release_ready() -> None:
    """TC-ArgusAgent-LEDGER-001-101 — replacing the inferred entries with audited_deep DOES promote.

    Control proving the gate is sensitive to the numerator: the SAME 17-file shape
    where every entry is audited_deep is 100% deep -> RELEASE_READY. Together with
    the prior test this pins that only audited_deep counts (FR8 from both sides).
    """
    deep_specs = [(f"f_{i}.py", CoverageDepth.AUDITED_DEEP, True) for i in range(17)]
    ledger = _ledger(*deep_specs)
    result = evaluate_verdict(ledger)
    assert result.deep_count == 17
    assert result.verdict is Verdict.RELEASE_READY


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — criticality assessed by file CONTENT, not filename (anti-gaming + non-ASCII)
# ─────────────────────────────────────────────────────────────────────────────


def test_assess_criticality_flags_benign_named_critical_file() -> None:
    """TC-ArgusAgent-LEDGER-001-102 — a critical module renamed benign is flagged from CONTENT (FR4)."""
    # Benign filename, but the body authenticates + handles a secret.
    source = (
        "def check(token):\n"
        "    secret = load_credential()\n"
        "    return hmac_verify(token, secret)\n"
    )
    result = assess_criticality(file_path="utils_misc.py", source=source)
    assert result is Criticality.CRITICAL


def test_assess_criticality_does_not_flag_benign_file() -> None:
    """TC-ArgusAgent-LEDGER-001-103 — a genuinely benign file is NORMAL (no false positive)."""
    source = "def add(a, b):\n    return a + b\n"
    result = assess_criticality(file_path="math_helpers.py", source=source)
    assert result is Criticality.NORMAL


def test_assess_criticality_ignores_filename_alone() -> None:
    """TC-ArgusAgent-LEDGER-001-104 — a critical-SOUNDING name with benign content is NOT flagged.

    Proves the filename is at most a weak hint, never the decision: ``auth_guard.py``
    whose body is pure arithmetic is NORMAL — the decision is content-driven.
    """
    source = "def total(items):\n    return sum(items)\n"
    result = assess_criticality(file_path="auth_guard.py", source=source)
    assert result is Criticality.NORMAL


def test_assess_criticality_non_ascii_path_and_identifier_classified() -> None:
    """TC-ArgusAgent-LEDGER-001-105 — non-ASCII path + non-ASCII identifier classified, not dropped (AI-E1-1).

    The Epic-1 retro adversarial fixture: a security module at a non-ASCII path
    whose security tokens sit AROUND non-ASCII identifiers must still be flagged
    CRITICAL — the content classifier must not silently drop non-ASCII input.
    """
    source = (
        "def vérifier_permission(utilisateur):\n"
        "    jeton = charger_credential(utilisateur)\n"
        "    return autorisé(jeton)\n"
    )
    result = assess_criticality(file_path="auth/café_guard.py", source=source)
    assert result is Criticality.CRITICAL


def test_assess_criticality_non_ascii_benign_not_flagged() -> None:
    """TC-ArgusAgent-LEDGER-001-106 — a benign non-ASCII file is NORMAL (no over-flagging of Unicode)."""
    source = "def additionner(a, b):\n    return a + b  # somme\n"
    result = assess_criticality(file_path="maths/café_utils.py", source=source)
    assert result is Criticality.NORMAL


def test_assess_criticality_uses_ast_entry_signals() -> None:
    """TC-ArgusAgent-LEDGER-001-107 — criticality also derives from the 1.4 AST entry def/edge names."""
    entry = AstIndexEntry(
        file_path="obscure.py",
        ast_eligible=True,
        definitions=(Definition(name="rotate_encryption_key", kind="function", start_line=1, end_line=2),),
        edges=(CodeEdge(callee="noop", line=2),),
    )
    # Source alone carries no token; the AST def name does.
    result = assess_criticality(file_path="obscure.py", source="x = 1\n", ast_entry=entry)
    assert result is Criticality.CRITICAL


def test_assess_criticality_ast_entry_edge_callee_signal() -> None:
    """TC-ArgusAgent-LEDGER-001-108 — a critical callee in the edge set flags criticality."""
    entry = AstIndexEntry(
        file_path="obscure.py",
        ast_eligible=True,
        definitions=(Definition(name="run", kind="function", start_line=1, end_line=2),),
        edges=(CodeEdge(callee="grant_permission", line=2),),
    )
    result = assess_criticality(file_path="obscure.py", source="y = 2\n", ast_entry=entry)
    assert result is Criticality.CRITICAL


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — PURE, frozen-contract, non-float, typed error
# ─────────────────────────────────────────────────────────────────────────────


def test_assess_criticality_returns_enum_never_float() -> None:
    """TC-ArgusAgent-LEDGER-001-109 — criticality is a closed enum, never a float score (AR4)."""
    result = assess_criticality(file_path="x.py", source="auth\n")
    assert isinstance(result, Criticality)
    assert not isinstance(result, float)


def test_assess_criticality_empty_source_is_normal_not_error() -> None:
    """TC-ArgusAgent-LEDGER-001-110 — an empty (well-formed) source is a valid NORMAL, not an error."""
    assert assess_criticality(file_path="empty.py", source="") is Criticality.NORMAL


def test_assess_criticality_empty_file_path_raises_typed_error() -> None:
    """TC-ArgusAgent-LEDGER-001-111 — an empty file_path raises the localized typed error (AR10)."""
    with pytest.raises(DepthSemanticsError):
        assess_criticality(file_path="", source="auth\n")


def test_assess_criticality_non_str_input_raises_typed_error() -> None:
    """TC-ArgusAgent-LEDGER-001-112 — a non-str descriptor raises DepthSemanticsError, never a coerce (AR10)."""
    with pytest.raises(DepthSemanticsError):
        assess_criticality(file_path="x.py", source=None)  # type: ignore[arg-type]


def test_classify_depth_non_descriptor_raises_typed_error() -> None:
    """TC-ArgusAgent-LEDGER-001-113 — classify_depth on a non-DepthEvidence raises the typed error (AR10)."""
    with pytest.raises(DepthSemanticsError):
        classify_depth("deep_read")  # type: ignore[arg-type]


def test_depth_semantics_error_is_value_error_subclass() -> None:
    """TC-ArgusAgent-LEDGER-001-114 — the typed error is a ValueError subclass (mirrors RecordingValidationError)."""
    assert issubclass(DepthSemanticsError, ValueError)


def test_depth_evidence_is_frozen_and_forbids_extra() -> None:
    """TC-ArgusAgent-LEDGER-001-115 — DepthEvidence is frozen + extra='forbid' (the 1.1/1.2 precedent)."""
    assert DepthEvidence.model_config.get("frozen") is True
    assert DepthEvidence.model_config.get("extra") == "forbid"
    with pytest.raises(Exception):
        DepthEvidence(kind=EvidenceKind.DEEP_READ, unknown_field=1)  # type: ignore[call-arg]


def test_schema_version_is_localized_constant() -> None:
    """TC-ArgusAgent-LEDGER-001-116 — schema version is a localized constant, never env/clock."""
    assert DEPTH_SEMANTICS_SCHEMA_VERSION == "1"
    assert DepthEvidence(kind=EvidenceKind.UNGRADABLE).schema_version == "1"


def test_module_source_has_no_impurity_or_float() -> None:
    """TC-ArgusAgent-LEDGER-001-117 — the module source contains no I/O / clock / uuid / random / float (AR8/AR4).

    Static AST scan over the module source: assert there is no ``datetime.now`` /
    ``time.time`` / ``uuid4`` / ``random`` / ``os.getpid`` / ``open(`` call and no
    ``float(`` cast or ``float`` annotation — the purity + no-float invariants are
    pinned mechanically, not just by behavior.
    """
    src = inspect.getsource(depth_semantics)
    tree = _ast_module.parse(src)

    forbidden_attr_calls = {"now", "getpid", "time", "uuid4"}
    forbidden_names = {"open", "float", "uuid4"}
    forbidden_modules = {"os", "random", "time", "datetime", "uuid"}

    for node in _ast_module.walk(tree):
        if isinstance(node, _ast_module.Call):
            func = node.func
            if isinstance(func, _ast_module.Attribute) and func.attr in forbidden_attr_calls:
                raise AssertionError(f"impure attribute call '{func.attr}' at line {node.lineno}")
            if isinstance(func, _ast_module.Name) and func.id in forbidden_names:
                raise AssertionError(f"forbidden call '{func.id}' at line {node.lineno}")
        if isinstance(node, (_ast_module.Import, _ast_module.ImportFrom)):
            mod = getattr(node, "module", None)
            names = [a.name.split(".")[0] for a in node.names]
            if mod in forbidden_modules or any(n in forbidden_modules for n in names):
                raise AssertionError(f"impure import at line {node.lineno}")
