"""Critical-subsystem identification + operator designation + the FR16 gate clause (story 2.3).

Verification area ArgusAgent-LEDGER (TC-ArgusAgent-LEDGER-001-NN, continuing the 1.2/2.1/2.2
area). Covers AC1–AC6 of story 2.3:

- AC1 — critical subsystems IDENTIFIED by content, REUSING the REAL 2.1
  ``assess_criticality`` (import-verified — a benign-named-but-critical file is
  identified; a benign file is not; anti-rename-gaming at the identification layer).
- AC2 — an operator can ADD / EXCLUDE designations with PRECEDENCE over the
  heuristic (force-critical adds a heuristic-NORMAL file; exclude removes a
  heuristic-CRITICAL file; the add-vs-exclude tie = exclude wins; the unmatched-path
  conservative policy).
- AC3 — the MANDATORY FR16 proofs over the REAL 1.6 ``evaluate_verdict``
  (import-verified, NOT a fork): a clean ≥60%-deep ledger with a critical-shallow
  file → RELEASE_READY WITHHELD (Story 8.1: with zero blocking findings that is
  ``INSUFFICIENT_COVERAGE`` / exit 3, FR16 row 4 — it was a block before the
  amendment); the SAME ledger with that file deep → RELEASE_READY; a no-critical
  ledger → byte-identical to the 1.6 default.
- AC5 — the module is PURE (AST scan: no I/O / clock / uuid / random / LLM),
  frozen-contract, non-``float``, raises a typed error on malformed input; the
  single 1.1 serializer is honored (no second json.dumps).
- AI-E1-1 — a non-ASCII path + identifier fixture identified critical by content
  AND designable + excludable by an operator path round-tripped intact.

These are PURE-function / synthetic-ledger tests — zero LLM tokens (NFR-D2), no temp
dirs. Synthetic ledgers are built via ``CoverageLedger.build([grade_entry(...)])``
and run through the 1.6 ``evaluate_verdict`` verbatim.
"""

from __future__ import annotations

import ast as _ast_module
import inspect

import pytest

from argus.index.ast_index import AstIndexEntry, CodeEdge, Definition
from argus.ledger import critical_subsystems as cs
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    grade_entry,
)
from argus.ledger.critical_subsystems import (
    CRITICAL_SUBSYSTEMS_SCHEMA_VERSION,
    CriticalCandidate,
    CriticalIneligibility,
    CriticalOrigin,
    CriticalSubsystemError,
    CriticalSubsystemSet,
    critical_subsystems_all_deep,
    identify_critical_subsystems,
)
from argus.ledger.depth_semantics import Criticality, assess_criticality
from argus.store import canonical
from argus.verdict.verdict_gate import DecisionRow, Verdict, evaluate_verdict


def _candidate(file_path: str, source: str = "", ast_entry: AstIndexEntry | None = None) -> CriticalCandidate:
    """Build a candidate by REUSING the real 2.1 assess_criticality (import-verified)."""
    return CriticalCandidate(
        file_path=file_path,
        criticality=assess_criticality(file_path=file_path, source=source, ast_entry=ast_entry),
    )


def _ledger(*specs: tuple[str, CoverageDepth, bool]) -> CoverageLedger:
    """Build a synthetic ledger from (file_path, proposed_depth, claim_present) specs."""
    return CoverageLedger.build(
        [
            grade_entry(file_path=fp, proposed_depth=depth, claim_present=claim)
            for (fp, depth, claim) in specs
        ]
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — content identification reusing the REAL 2.1 assess_criticality
# ─────────────────────────────────────────────────────────────────────────────


def test_identify_uses_real_assess_criticality_benign_name_critical_content() -> None:
    """TC-ArgusAgent-LEDGER-001-131 — a benign-named file with auth content IS identified critical."""
    result = identify_critical_subsystems(
        [
            _candidate("utils_misc.py", "def check_hmac_signature(tok): return tok"),
            _candidate("adder.py", "def add(a, b): return a + b"),
        ]
    )
    assert result.paths == ("utils_misc.py",)
    assert result.origins["utils_misc.py"] is CriticalOrigin.HEURISTIC


def test_identify_benign_file_is_not_critical() -> None:
    """TC-ArgusAgent-LEDGER-001-132 — a benign file (no signal) is NOT in the critical set."""
    result = identify_critical_subsystems([_candidate("adder.py", "def add(a, b): return a + b")])
    assert result.paths == ()


def test_identify_result_is_sorted_and_provenance_carried() -> None:
    """TC-ArgusAgent-LEDGER-001-133 — AC1 sorted output + provenance distinguishes heuristic vs operator."""
    result = identify_critical_subsystems(
        [
            _candidate("z_auth.py", "password = 'x'"),
            _candidate("a_crypto.py", "def encrypt(): ..."),
        ],
        operator_designated=("m_forced.py",),
    )
    assert result.paths == ("a_crypto.py", "m_forced.py", "z_auth.py")
    assert result.origins["a_crypto.py"] is CriticalOrigin.HEURISTIC
    assert result.origins["m_forced.py"] is CriticalOrigin.OPERATOR_DESIGNATED


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — operator precedence: ADD / EXCLUDE / tie / unmatched
# ─────────────────────────────────────────────────────────────────────────────


def test_operator_force_adds_a_heuristic_normal_file() -> None:
    """TC-ArgusAgent-LEDGER-001-134 — force-critical adds a file the heuristic graded NORMAL."""
    result = identify_critical_subsystems(
        [_candidate("plain.py", "def add(a, b): return a + b")],
        operator_designated=("plain.py",),
    )
    assert result.paths == ("plain.py",)
    assert result.origins["plain.py"] is CriticalOrigin.OPERATOR_DESIGNATED
    assert result.designated_but_unmatched == ()  # it matched an analyzable candidate


def test_operator_exclude_removes_a_heuristic_critical_file() -> None:
    """TC-ArgusAgent-LEDGER-001-135 — exclude removes a heuristic-CRITICAL file (the 2.1 Low correction)."""
    result = identify_critical_subsystems(
        [_candidate("tokenize_helper.py", "import tokenize  # benign, over-flagged by substring")],
        operator_excluded=("tokenize_helper.py",),
    )
    assert result.paths == ()


def test_add_vs_exclude_tie_exclude_wins() -> None:
    """TC-ArgusAgent-LEDGER-001-136 — a path in BOTH add and exclude is EXCLUDED (exclude wins)."""
    result = identify_critical_subsystems(
        [_candidate("auth.py", "def authorize(): ...")],
        operator_designated=("auth.py",),
        operator_excluded=("auth.py",),
    )
    assert result.paths == ()
    assert result.designated_but_unmatched == ()  # excluded ⇒ not unmatched-recorded


def test_unmatched_force_critical_recorded_conservatively() -> None:
    """TC-ArgusAgent-LEDGER-001-137 — a force-critical path matching no candidate is recorded unmatched."""
    result = identify_critical_subsystems(
        [_candidate("adder.py", "def add(a, b): return a + b")],
        operator_designated=("does/not/exist.py",),
    )
    # It IS in the critical set (conservative — cannot be deep ⇒ withholds RELEASE_READY).
    assert result.paths == ("does/not/exist.py",)
    assert result.designated_but_unmatched == ("does/not/exist.py",)
    assert result.origins["does/not/exist.py"] is CriticalOrigin.OPERATOR_DESIGNATED


def test_unmatched_exclude_path_is_a_noop() -> None:
    """TC-ArgusAgent-LEDGER-001-138 — an exclude path matching nothing is a harmless no-op."""
    result = identify_critical_subsystems(
        [_candidate("auth.py", "def authorize(): ...")],
        operator_excluded=("nope.py",),
    )
    assert result.paths == ("auth.py",)


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — critical_subsystems_all_deep predicate + the MANDATORY FR16 gate proofs
#       over the REAL 1.6 evaluate_verdict (import-verified, NOT a fork)
# ─────────────────────────────────────────────────────────────────────────────


def test_predicate_empty_set_is_vacuously_true() -> None:
    """TC-ArgusAgent-LEDGER-001-139 — empty critical set → True (the regression-safe default)."""
    ledger = _ledger(("a.py", CoverageDepth.AUDITED_SHALLOW, False))
    assert critical_subsystems_all_deep((), ledger) is True


def test_predicate_all_deep_true_one_shallow_false() -> None:
    """TC-ArgusAgent-LEDGER-001-140 — True iff EVERY critical path is audited_deep."""
    ledger = _ledger(
        ("crit.py", CoverageDepth.AUDITED_DEEP, True),
        ("other.py", CoverageDepth.AUDITED_SHALLOW, False),
    )
    assert critical_subsystems_all_deep(("crit.py",), ledger) is True

    shallow = _ledger(("crit.py", CoverageDepth.AUDITED_SHALLOW, False))
    assert critical_subsystems_all_deep(("crit.py",), shallow) is False


@pytest.mark.parametrize(
    "depth",
    [
        CoverageDepth.AUDITED_SHALLOW,
        CoverageDepth.TOOL_SCANNED_ONLY,
        CoverageDepth.INFERRED,
        CoverageDepth.SKIPPED,
    ],
)
def test_predicate_any_non_deep_critical_is_false(depth: CoverageDepth) -> None:
    """TC-ArgusAgent-LEDGER-001-141 — a critical file in any non-deep state → False."""
    ledger = _ledger(("crit.py", depth, False))
    assert critical_subsystems_all_deep(("crit.py",), ledger) is False


def test_predicate_critical_absent_from_ledger_is_false() -> None:
    """TC-ArgusAgent-LEDGER-001-142 — a designated-but-unmatched critical (no ledger entry) → False."""
    ledger = _ledger(("a.py", CoverageDepth.AUDITED_DEEP, True))
    assert critical_subsystems_all_deep(("ghost.py",), ledger) is False


def test_fr16_critical_shallow_withholds_release_ready() -> None:
    """TC-ArgusAgent-LEDGER-001-143 — MANDATORY: ≥60% deep, 0 blocking, BUT a critical shallow
    → RELEASE_READY WITHHELD.

    Story 8.1: the clause still gates, which is this test's subject. With ZERO blocking
    findings the amended FR16 table renders the withholding as row 4 /
    ``INSUFFICIENT_COVERAGE`` / exit 3 — the honest "not assessed enough of what matters"
    state — instead of a block that would blame a defect nobody found.
    """
    # 4 deep + 1 shallow = 80% deep ≥ 60%, 0 blocking findings. The shallow file is critical.
    ledger = _ledger(
        ("a.py", CoverageDepth.AUDITED_DEEP, True),
        ("b.py", CoverageDepth.AUDITED_DEEP, True),
        ("c.py", CoverageDepth.AUDITED_DEEP, True),
        ("d.py", CoverageDepth.AUDITED_DEEP, True),
        ("crit.py", CoverageDepth.AUDITED_SHALLOW, False),
    )
    all_deep = critical_subsystems_all_deep(("crit.py",), ledger)
    assert all_deep is False
    verdict = evaluate_verdict(ledger, (), critical_subsystems_all_deep=all_deep)
    assert verdict.verdict is not Verdict.RELEASE_READY
    assert verdict.decision_row is DecisionRow.GATE_UNMET_NO_FINDINGS
    assert verdict.exit_code == 3


def test_fr16_same_ledger_critical_deep_is_release_ready() -> None:
    """TC-ArgusAgent-LEDGER-001-144 — MANDATORY: the SAME ledger with that file deep → RELEASE_READY/exit 0."""
    ledger = _ledger(
        ("a.py", CoverageDepth.AUDITED_DEEP, True),
        ("b.py", CoverageDepth.AUDITED_DEEP, True),
        ("c.py", CoverageDepth.AUDITED_DEEP, True),
        ("d.py", CoverageDepth.AUDITED_DEEP, True),
        ("crit.py", CoverageDepth.AUDITED_DEEP, True),
    )
    all_deep = critical_subsystems_all_deep(("crit.py",), ledger)
    assert all_deep is True
    verdict = evaluate_verdict(ledger, (), critical_subsystems_all_deep=all_deep)
    assert verdict.verdict is Verdict.RELEASE_READY
    assert verdict.exit_code == 0


def test_fr16_no_critical_is_byte_identical_to_1_6_default() -> None:
    """TC-ArgusAgent-LEDGER-001-145 — MANDATORY: a no-critical ledger → identical to the 1.6 default-True."""
    ledger = _ledger(
        ("a.py", CoverageDepth.AUDITED_DEEP, True),
        ("b.py", CoverageDepth.AUDITED_DEEP, True),
        ("c.py", CoverageDepth.AUDITED_SHALLOW, False),
    )
    all_deep = critical_subsystems_all_deep((), ledger)
    wired = evaluate_verdict(ledger, (), critical_subsystems_all_deep=all_deep)
    default = evaluate_verdict(ledger, ())  # the pre-2.3 default-True call
    # Byte-identical verdict payload (NFR-P1) — the wired empty-set path is a no-op.
    assert canonical.dumps(wired.to_canonical_payload()) == canonical.dumps(
        default.to_canonical_payload()
    )
    assert wired.verdict is default.verdict


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — PURE / frozen / no-float / typed-error / single serializer / determinism
# ─────────────────────────────────────────────────────────────────────────────


def test_module_is_pure_no_io_clock_random_via_ast_scan() -> None:
    """TC-ArgusAgent-LEDGER-001-146 — AC5: no I/O / clock / uuid / random / LLM call in the module source."""
    source = inspect.getsource(cs)
    tree = _ast_module.parse(source)
    forbidden_attrs = {"now", "today", "time", "uuid4", "getpid", "monotonic"}
    forbidden_calls = {"open", "read_text", "write_text"}
    for node in _ast_module.walk(tree):
        if isinstance(node, _ast_module.Attribute) and node.attr in forbidden_attrs:
            raise AssertionError(f"forbidden impure attribute access: {node.attr}")
        if isinstance(node, _ast_module.Call) and isinstance(node.func, _ast_module.Name):
            assert node.func.id not in forbidden_calls, f"forbidden impure call: {node.func.id}"
    # No import of the impure store writer / providers / web stack.
    for forbidden in ("import random", "import uuid", "import time", "datetime", "open("):
        assert forbidden not in source, f"impure token present: {forbidden}"


def test_critical_subsystem_set_is_frozen() -> None:
    """TC-ArgusAgent-LEDGER-001-147 — AC5: CriticalSubsystemSet is frozen (extra=forbid; immutable)."""
    result = CriticalSubsystemSet(paths=("a.py",), origins={"a.py": CriticalOrigin.HEURISTIC})
    with pytest.raises(Exception):
        result.paths = ("b.py",)  # type: ignore[misc]
    with pytest.raises(Exception):
        CriticalSubsystemSet(paths=("a.py",), unknown_field=1)  # type: ignore[call-arg]


def test_schema_version_is_localized_constant() -> None:
    """TC-ArgusAgent-LEDGER-001-148 — AC5: schema_version is a localized constant (additive-only).

    Story 8.2 moved the stamp "1" → "2": ``paths`` changed MEANING (the heuristic term
    is now eligibility-filtered, DR-5) and the model gained an always-serialized
    disclosure field, so the persisted bytes move for every repository. The subject of
    this test is unchanged — the version is ONE localized constant that the model's
    default tracks, never a literal duplicated at a write site.
    """
    assert CRITICAL_SUBSYSTEMS_SCHEMA_VERSION == "2"
    assert CriticalSubsystemSet().schema_version == CRITICAL_SUBSYSTEMS_SCHEMA_VERSION


def test_typed_error_on_malformed_designation_path() -> None:
    """TC-ArgusAgent-LEDGER-001-149 — AC5/AR10: a non-str designation entry raises a typed error."""
    with pytest.raises(CriticalSubsystemError):
        identify_critical_subsystems([], operator_designated=[123])  # type: ignore[list-item]
    with pytest.raises(CriticalSubsystemError):
        identify_critical_subsystems([], operator_designated="not-an-iterable-of-paths")  # bare str
    assert issubclass(CriticalSubsystemError, ValueError)


def test_typed_error_on_non_ledger_predicate_arg() -> None:
    """TC-ArgusAgent-LEDGER-001-150 — AC5/AR10: a non-CoverageLedger predicate arg raises a typed error."""
    with pytest.raises(CriticalSubsystemError):
        critical_subsystems_all_deep(("a.py",), {"not": "a ledger"})  # type: ignore[arg-type]


def test_no_float_anywhere_in_serialized_set() -> None:
    """TC-ArgusAgent-LEDGER-001-151 — AC5/AR4: the set serializes through the single 1.1 serializer (no float)."""
    result = identify_critical_subsystems(
        [_candidate("auth.py", "def authorize(): ...")], operator_designated=("forced.py",)
    )
    payload = result.model_dump(mode="json")
    encoded = canonical.dumps(payload)  # rejects float — proves no float leaf
    assert "auth.py" in encoded
    assert "forced.py" in encoded


def test_order_independence_same_designations_two_input_orders() -> None:
    """TC-ArgusAgent-LEDGER-001-152 — NFR-P1: same designations in two input orders → identical result.

    Story 8.2 extends the subject onto the DR-5 disclosure map: an ELIGIBILITY-filtered
    path enters through a dict rather than a sorted tuple, so its order-independence is
    asserted here rather than inherited on trust.
    """
    cands_1 = [
        _candidate("auth.py", "password=1"),
        _candidate("crypto.py", "def encrypt(): ..."),
        _candidate("adder.py", "def add(a, b): return a"),
        CriticalCandidate(
            file_path="tests/test_token.py",
            criticality=Criticality.CRITICAL,
            ineligibility=CriticalIneligibility.TEST_FILE,
        ),
        CriticalCandidate(
            file_path="auth/__init__.py",
            criticality=Criticality.CRITICAL,
            ineligibility=CriticalIneligibility.ZERO_DEFINITION_MODULE,
        ),
    ]
    cands_2 = list(reversed(cands_1))
    r1 = identify_critical_subsystems(cands_1, operator_designated=("z.py", "a.py"))
    r2 = identify_critical_subsystems(cands_2, operator_designated=("a.py", "z.py"))
    assert r1.paths == r2.paths
    assert r1.designated_but_unmatched == r2.designated_but_unmatched
    assert r1.heuristic_excluded_ineligible == r2.heuristic_excluded_ineligible
    assert list(r1.heuristic_excluded_ineligible) == list(
        r2.heuristic_excluded_ineligible
    ), "the disclosure map's own key ORDER must not depend on candidate order"
    assert canonical.dumps(r1.model_dump(mode="json")) == canonical.dumps(r2.model_dump(mode="json"))


# ─────────────────────────────────────────────────────────────────────────────
# AI-E1-1 — non-ASCII path + identifier: identified critical + designable + excludable intact
# ─────────────────────────────────────────────────────────────────────────────


def test_non_ascii_path_identified_critical_by_content() -> None:
    """TC-ArgusAgent-LEDGER-001-153 — AI-E1-1: a non-ASCII path with critical content IS identified."""
    # café_guard.py with a non-ASCII identifier around a critical token (the 2.1 precedent).
    result = identify_critical_subsystems(
        [_candidate("auth/café_guard.py", "def vérifier_permission(): pass")]
    )
    assert result.paths == ("auth/café_guard.py",)


def test_non_ascii_path_designable_and_excludable_intact() -> None:
    """TC-ArgusAgent-LEDGER-001-154 — AI-E1-1: a Cyrillic path round-trips through designation + exclusion intact."""
    cyrillic = "модуль/безопасность.py"
    # Force-critical a benign-content non-ASCII path; the path round-trips intact (not mojibake).
    forced = identify_critical_subsystems(
        [_candidate(cyrillic, "def add(): pass")], operator_designated=(cyrillic,)
    )
    assert forced.paths == (cyrillic,)
    assert forced.origins[cyrillic] is CriticalOrigin.OPERATOR_DESIGNATED
    # Excludable intact — the same non-ASCII path drops a heuristic-critical match.
    excluded = identify_critical_subsystems(
        [_candidate(cyrillic, "password = 'x'")], operator_excluded=(cyrillic,)
    )
    assert excluded.paths == ()
    # The path survives the single 1.1 serializer (ensure_ascii=False) byte-intact.
    encoded = canonical.dumps(forced.model_dump(mode="json"))
    assert cyrillic in encoded


def test_non_ascii_critical_via_ast_entry_names() -> None:
    """TC-ArgusAgent-LEDGER-001-155 — AI-E1-1: a critical AST definition/edge name identifies a benign-source file."""
    entry = AstIndexEntry(
        file_path="módulo/seguro.py",
        ast_eligible=True,
        definitions=(Definition(name="authorize_açõ", kind="function", start_line=1, end_line=2),),
        edges=(CodeEdge(callee="check_token", line=2),),
    )
    cand = _candidate("módulo/seguro.py", source="x = 1", ast_entry=entry)
    assert cand.criticality is Criticality.CRITICAL
    result = identify_critical_subsystems([cand])
    assert result.paths == ("módulo/seguro.py",)
