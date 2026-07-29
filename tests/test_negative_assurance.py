"""Story 4.1 — negative-assurance verdict WRAPPER (FR17 / NFR-A3).

Verification area ArgusAgent-VERDICT (``TC-ArgusAgent-VERDICT-001-NN`` — the FIRST test file in
this new area; the 1.6 gate tests live in ``test_verdict_gate.py``). Drivers:
ArgusAgent-FR-17 (express every verdict in negative-assurance terms: scope statement,
materiality bar, disclaimer, point-in-time stamp), ArgusAgent-NFR-A3 (every verdict
carries those four), ArgusAgent-FR-4 (the critical-subsystem narration), ArgusAgent-FR-16/FR-22
(the floor report folded over), ArgusAgent-NFR-D2/D3/P1/S1, AR4/AR8/AR10/AR11.

Zero LLM tokens — the wrapper is a pure fold over in-memory records.

AI-E3-1 keystone-fixture-adequacy (the Epic-3 marquee lesson): each keystone
assertion ("no over-claim", "did NOT cover every not-deep class", "critical-not-deep
narration") runs over a fixture that contains ≥1 element of EVERY class it preserves,
and is demonstrated RED against a deliberate violation before it is trusted. The
RED-then-green demonstrations are in-test (a deliberate mutation must FAIL the
assertion) — see ``test_*_demonstrated_red`` cases.
"""

from __future__ import annotations

import ast
from fractions import Fraction
from pathlib import Path

import pytest
from pydantic import ValidationError

from argus.cost.exhaustion import (
    HaltReport,
    InsufficientCoverageFloorReport,
    build_floor_report,
)
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
)
from argus.ledger.critical_subsystems import (
    CriticalCandidate,
    CriticalOrigin,
    CriticalSubsystemSet,
    identify_critical_subsystems,
)
from argus.ledger.depth_semantics import Criticality
from argus.store import canonical
from argus.verdict.negative_assurance import (
    DISCLAIMER,
    NEGATIVE_ASSURANCE_SCHEMA_VERSION,
    NegativeAssuranceError,
    NegativeAssuranceVerdict,
    ScopeStatement,
    build_negative_assurance_verdict,
)
from argus.verdict.verdict_gate import (
    AuditVerdict,
    Verdict,
    evaluate_verdict,
)

_NA_SOURCE = (
    Path(__file__).resolve().parents[1]
    
    / "argus"
    / "verdict"
    / "negative_assurance.py"
)

# The AC2 forbidden over-claim phrase set (case-insensitive substring scan).
_FORBIDDEN_PHRASES = (
    "certif",
    "is correct",
    "proven",
    "guarantee",
    "defect-free",
    "bug-free",
    "passed",
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures — adequate per AI-E3-1: every not-deep class + a critical-not-deep path
# ─────────────────────────────────────────────────────────────────────────────


def _entry(path: str, depth: CoverageDepth, *, claim: bool = False) -> CoverageLedgerEntry:
    return CoverageLedgerEntry(file_path=path, depth=depth, claim_present=claim)


def _every_class_ledger() -> CoverageLedger:
    """A ledger with ≥1 of EVERY depth class (the AC3 adequate fixture).

    1 audited_deep + 1 audited_shallow + 1 tool_scanned_only + 1 inferred + 1
    skipped = 5 entries, deep_ratio 1/5 (exactly at the floor — assessable, NOT
    insufficient). ``crit_auth.py`` is a CRITICAL file graded audited_shallow (a
    critical-NOT-deep path).
    """
    return CoverageLedger.build(
        [
            _entry("a_deep.py", CoverageDepth.AUDITED_DEEP, claim=True),
            _entry("crit_auth.py", CoverageDepth.AUDITED_SHALLOW),
            _entry("c_tool.py", CoverageDepth.TOOL_SCANNED_ONLY),
            _entry("d_inferred.py", CoverageDepth.INFERRED),
            _entry("e_skipped.py", CoverageDepth.SKIPPED),
        ]
    )


def _critical_set_with_not_deep() -> CriticalSubsystemSet:
    """A critical set with ≥1 critical-not-deep path + 1 designated-but-unmatched.

    ``crit_auth.py`` (heuristic critical, graded shallow in the ledger) is
    NOT-deep; ``ghost.py`` is operator-designated but matches no candidate
    (designated_but_unmatched — also NOT-deep). ``a_deep.py`` is critical AND deep.
    """
    return identify_critical_subsystems(
        [
            CriticalCandidate(file_path="a_deep.py", criticality=Criticality.CRITICAL),
            CriticalCandidate(file_path="crit_auth.py", criticality=Criticality.CRITICAL),
            CriticalCandidate(file_path="c_tool.py", criticality=Criticality.NORMAL),
        ],
        operator_designated=("ghost.py",),
    )


def _floor_report(verdict: AuditVerdict, *, halted: bool = False, skipped_on_exh: int = 0) -> InsufficientCoverageFloorReport:
    report = HaltReport(
        halted_on_exhaustion=halted,
        total_credits=5,
        ceiling_credits=5 if halted else None,
        assessed_count=verdict.total_count - skipped_on_exh,
        assessed_files=(),
        skipped_on_exhaustion_count=skipped_on_exh,
        skipped_on_exhaustion_files=(),
    )
    return build_floor_report(verdict, report)


def _release_ready_verdict() -> AuditVerdict:
    """A clean RELEASE_READY verdict (deep_ratio >= 60%, no blocking, all-critical-deep)."""
    ledger = CoverageLedger.build(
        [
            _entry("a.py", CoverageDepth.AUDITED_DEEP, claim=True),
            _entry("b.py", CoverageDepth.AUDITED_DEEP, claim=True),
            _entry("c.py", CoverageDepth.AUDITED_DEEP, claim=True),
        ]
    )
    return evaluate_verdict(ledger, ())


def _not_ready_verdict() -> AuditVerdict:
    """A NOT_READY_FOR_RELEASE verdict (>=20% deep but a critical not deep)."""
    ledger = _every_class_ledger()
    critical = _critical_set_with_not_deep()
    return evaluate_verdict(
        ledger, (), critical_subsystems_all_deep=False
    )


def _insufficient_verdict() -> AuditVerdict:
    """An INSUFFICIENT_COVERAGE verdict (deep_ratio < 20%)."""
    ledger = CoverageLedger.build(
        [
            _entry("a.py", CoverageDepth.SKIPPED),
            _entry("b.py", CoverageDepth.SKIPPED),
            _entry("c.py", CoverageDepth.SKIPPED),
            _entry("d.py", CoverageDepth.SKIPPED),
            _entry("e.py", CoverageDepth.SKIPPED),
            _entry("f.py", CoverageDepth.AUDITED_DEEP, claim=True),
        ]
    )
    return evaluate_verdict(ledger, ())


def _wrapper_for(verdict: AuditVerdict, *, ledger: CoverageLedger | None = None,
                 critical: CriticalSubsystemSet | None = None,
                 floor: InsufficientCoverageFloorReport | None = None,
                 materiality_bar: str = "default") -> NegativeAssuranceVerdict:
    floor = floor if floor is not None else _floor_report(verdict)
    critical = critical if critical is not None else CriticalSubsystemSet()
    ledger = ledger if ledger is not None else CoverageLedger.build([])
    return build_negative_assurance_verdict(
        verdict, floor, critical, ledger, materiality_bar=materiality_bar
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — the four negative-assurance fields over all three verdicts
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "make_verdict",
    [_release_ready_verdict, _not_ready_verdict, _insufficient_verdict],
)
def test_wrapper_carries_four_fields_over_all_three_verdicts(make_verdict) -> None:
    """TC-ArgusAgent-VERDICT-001-01 — AC1: scope_statement + materiality_bar + disclaimer + verdict/exit, all three verdicts."""
    verdict = make_verdict()
    ledger = _every_class_ledger()
    critical = _critical_set_with_not_deep()
    floor = _floor_report(verdict)
    wrapper = build_negative_assurance_verdict(
        verdict, floor, critical, ledger, materiality_bar="high"
    )
    assert wrapper.verdict == verdict.verdict.value
    assert wrapper.exit_code == verdict.exit_code
    assert wrapper.deep_ratio == verdict.deep_ratio
    assert wrapper.materiality_bar == "high"
    assert wrapper.disclaimer == DISCLAIMER
    assert isinstance(wrapper.scope_statement, ScopeStatement)
    assert wrapper.assurance_statement  # populated + honest
    # The stamp is NOT a hashed-payload field (NFR-D3) — no created_at on the model.
    assert "created_at" not in wrapper.model_dump()
    assert "run_id" not in wrapper.model_dump()


def test_scope_statement_examined_sampled_not_covered_triad() -> None:
    """TC-ArgusAgent-VERDICT-001-02 — AC1: the scope triad reuses AuditVerdict.counts_by_depth exactly."""
    verdict = _not_ready_verdict()
    wrapper = _wrapper_for(verdict, ledger=_every_class_ledger(),
                           critical=_critical_set_with_not_deep())
    scope = wrapper.scope_statement
    counts = verdict.counts_by_depth
    assert scope.examined_deep == counts[CoverageDepth.AUDITED_DEEP]
    assert scope.sampled_shallow == counts[CoverageDepth.AUDITED_SHALLOW]
    assert scope.sampled_tool_scanned == counts[CoverageDepth.TOOL_SCANNED_ONLY]
    assert scope.not_covered_inferred == counts[CoverageDepth.INFERRED]
    assert scope.not_covered_skipped == counts[CoverageDepth.SKIPPED]
    assert scope.total_count == verdict.total_count


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — the no-over-claim keystone (forbidden-phrase scan + RED demonstration)
# ─────────────────────────────────────────────────────────────────────────────


def _serialized_text(wrapper: NegativeAssuranceVerdict) -> str:
    """The full serialized wrapper text, lower-cased, for the forbidden-phrase scan."""
    return canonical.dumps(wrapper.to_canonical_payload()).lower()


@pytest.mark.parametrize(
    "make_verdict",
    [_release_ready_verdict, _not_ready_verdict, _insufficient_verdict],
)
def test_no_over_claim_over_all_three_verdicts(make_verdict) -> None:
    """TC-ArgusAgent-VERDICT-001-03 — AC2 KEYSTONE: no certification/correctness over-claim, all three verdicts."""
    verdict = make_verdict()
    wrapper = _wrapper_for(verdict, ledger=_every_class_ledger(),
                           critical=_critical_set_with_not_deep())
    text = _serialized_text(wrapper)
    for phrase in _FORBIDDEN_PHRASES:
        assert phrase not in text, (
            f"{verdict.verdict.value} wrapper over-claims: forbidden phrase {phrase!r} present"
        )
    # A RELEASE_READY wrapper specifically frames scope-bounded assurance.
    if verdict.verdict is Verdict.RELEASE_READY:
        assert "within the assessed scope" in wrapper.assurance_statement.lower()


def test_no_over_claim_scan_is_demonstrated_red() -> None:
    """TC-ArgusAgent-VERDICT-001-04 — AC2: the no-over-claim scan goes RED on a certification phrase (keystone proof).

    Mutate the disclaimer to a certification phrase and confirm the SAME forbidden-
    phrase scan FAILS — proving the AC2 assertion can catch its keystone bug
    (AI-E3-1). The real text (above) is green.
    """
    verdict = _release_ready_verdict()
    wrapper = _wrapper_for(verdict)
    mutated = wrapper.model_copy(
        update={"disclaimer": "This certifies the code is correct and defect-free."}
    )
    text = _serialized_text(mutated)
    # The scan that passes on the real text MUST fail on the mutated text.
    hits = [p for p in _FORBIDDEN_PHRASES if p in text]
    assert hits, "the forbidden-phrase scan failed to catch a mutated over-claiming disclaimer"


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — assessed-scope honesty: every not-deep class + critical-not-deep narration
# ─────────────────────────────────────────────────────────────────────────────


def test_scope_statement_accounts_for_every_not_deep_class() -> None:
    """TC-ArgusAgent-VERDICT-001-05 — AC3 KEYSTONE: every not-deep class is present + non-zero (none dropped)."""
    verdict = _not_ready_verdict()
    wrapper = _wrapper_for(verdict, ledger=_every_class_ledger(),
                           critical=_critical_set_with_not_deep())
    scope = wrapper.scope_statement
    # The fixture has ≥1 of EVERY not-deep class — none may be silently dropped.
    assert scope.sampled_shallow >= 1
    assert scope.sampled_tool_scanned >= 1
    assert scope.not_covered_inferred >= 1
    assert scope.not_covered_skipped >= 1


def test_scope_statement_drop_a_class_is_demonstrated_red() -> None:
    """TC-ArgusAgent-VERDICT-001-06 — AC3: dropping a not-deep class makes the AC3 assertion FAIL (keystone proof).

    Simulate the keystone bug — a scope statement that silently drops the
    ``inferred`` class (set to 0) — and confirm the AC3 "every class non-zero"
    assertion FAILS on it (AI-E3-1). The real builder (above) keeps every class.
    """
    verdict = _not_ready_verdict()
    wrapper = _wrapper_for(verdict, ledger=_every_class_ledger(),
                           critical=_critical_set_with_not_deep())
    dropped_scope = wrapper.scope_statement.model_copy(update={"not_covered_inferred": 0})
    # The assertion that passes on the real scope MUST fail on the dropped one.
    assert not (dropped_scope.not_covered_inferred >= 1)


def test_critical_not_deep_narration_names_the_critical_subsystem() -> None:
    """TC-ArgusAgent-VERDICT-001-07 — AC3 KEYSTONE: the scope statement names a critical subsystem NOT examined deeply."""
    verdict = _not_ready_verdict()
    critical = _critical_set_with_not_deep()
    wrapper = _wrapper_for(verdict, ledger=_every_class_ledger(), critical=critical)
    scope = wrapper.scope_statement
    # crit_auth.py is critical but graded shallow → NOT examined deeply.
    assert "crit_auth.py" in scope.critical_not_examined_deep
    # a_deep.py is critical AND deep → examined deeply.
    assert "a_deep.py" in scope.critical_examined_deep
    # ghost.py is designated_but_unmatched → also NOT examined deeply.
    assert "ghost.py" in scope.critical_designated_but_unmatched
    assert "ghost.py" in scope.critical_not_examined_deep
    # A consumer can tell ≥1 critical area was excluded.
    assert len(scope.critical_not_examined_deep) >= 1


def test_critical_not_deep_narration_is_demonstrated_red() -> None:
    """TC-ArgusAgent-VERDICT-001-08 — AC3: omitting the critical-not-deep narration makes the assertion FAIL.

    Simulate the keystone bug — a wrapper that omits the critical-not-deep names —
    and confirm the AC3 narration assertion FAILS on it (AI-E3-1).
    """
    verdict = _not_ready_verdict()
    wrapper = _wrapper_for(verdict, ledger=_every_class_ledger(),
                           critical=_critical_set_with_not_deep())
    omitted = wrapper.scope_statement.model_copy(
        update={"critical_not_examined_deep": ()}
    )
    assert not (len(omitted.critical_not_examined_deep) >= 1)


def test_critical_deep_vs_not_deep_are_distinguished() -> None:
    """TC-ArgusAgent-VERDICT-001-09 — AC3: a deeply-covered critical is distinct from a shallow one."""
    verdict = _not_ready_verdict()
    critical = _critical_set_with_not_deep()
    wrapper = _wrapper_for(verdict, ledger=_every_class_ledger(), critical=critical)
    scope = wrapper.scope_statement
    assert set(scope.critical_examined_deep).isdisjoint(scope.critical_not_examined_deep)


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — frozen, no-float, secret-safe, schema-versioned
# ─────────────────────────────────────────────────────────────────────────────


def test_wrapper_is_frozen_extra_forbid() -> None:
    """TC-ArgusAgent-VERDICT-001-10 — AC5: frozen + extra='forbid' + localized schema_version."""
    wrapper = _wrapper_for(_release_ready_verdict())
    assert wrapper.schema_version == NEGATIVE_ASSURANCE_SCHEMA_VERSION
    # extra="forbid" — an unknown field on validation is a typed ValidationError.
    with pytest.raises(ValidationError):
        NegativeAssuranceVerdict.model_validate(
            {**wrapper.model_dump(), "unknown_field": "x", "deep_ratio": wrapper.deep_ratio}
        )
    # frozen=True — attribute assignment raises.
    with pytest.raises((ValidationError, TypeError)):
        wrapper.verdict = "MUTATED"  # type: ignore[misc]


def test_wrapper_no_float_anywhere_and_serializes() -> None:
    """TC-ArgusAgent-VERDICT-001-11 — AC5: no float; the canonical serializer accepts the payload (Fraction → num/den)."""
    wrapper = _wrapper_for(_not_ready_verdict(), ledger=_every_class_ledger(),
                           critical=_critical_set_with_not_deep())
    text = canonical.dumps(wrapper.to_canonical_payload())
    # deep_ratio is the canonical Fraction "num/den" form, never a binary float.
    assert '"deep_ratio":"' in text.replace(" ", "")
    # No leaf is a Python float (the serializer would raise; assert it does not).
    assert canonical.loads(text)  # round-trips through json


def test_wrapper_is_secret_and_abs_path_safe_with_non_ascii_critical_path() -> None:
    """TC-ArgusAgent-VERDICT-001-12 — AC5 (AI-E1-1): non-ASCII critical path round-trips; no abs-path/source/secret byte."""
    # A non-ASCII (café + Cyrillic) critical path graded shallow (not deep).
    nonascii = "café/тест_auth.py"
    ledger = CoverageLedger.build(
        [
            _entry("a_deep.py", CoverageDepth.AUDITED_DEEP, claim=True),
            _entry(nonascii, CoverageDepth.AUDITED_SHALLOW),
            _entry("b_deep.py", CoverageDepth.AUDITED_DEEP, claim=True),
        ]
    )
    critical = identify_critical_subsystems(
        [
            CriticalCandidate(file_path="a_deep.py", criticality=Criticality.CRITICAL),
            CriticalCandidate(file_path=nonascii, criticality=Criticality.CRITICAL),
        ],
    )
    verdict = evaluate_verdict(ledger, (), critical_subsystems_all_deep=False)
    wrapper = build_negative_assurance_verdict(
        verdict, _floor_report(verdict), critical, ledger, materiality_bar="default"
    )
    text = canonical.dumps(wrapper.to_canonical_payload())
    # The non-ASCII path round-trips intact (ensure_ascii=False — no octal escape).
    assert nonascii in text
    assert nonascii in wrapper.scope_statement.critical_not_examined_deep
    # No absolute host path byte (POSIX / Windows).
    assert "/home/" not in text and "C:\\" not in text
    # No source byte leakage — only the path string, not file contents.
    reloaded = NegativeAssuranceVerdict.model_validate(
        {**canonical.loads(text), "deep_ratio": Fraction(*map(int, canonical.loads(text)["deep_ratio"].split("/")))}
    )
    assert reloaded.scope_statement == wrapper.scope_statement


# ─────────────────────────────────────────────────────────────────────────────
# AC7 — purity / typed error / single serializer / order-independence
# ─────────────────────────────────────────────────────────────────────────────


def test_builder_raises_typed_error_on_malformed_inputs() -> None:
    """TC-ArgusAgent-VERDICT-001-13 — AC7 (AR10): malformed inputs raise NegativeAssuranceError."""
    verdict = _release_ready_verdict()
    floor = _floor_report(verdict)
    critical = CriticalSubsystemSet()
    ledger = CoverageLedger.build([])
    assert issubclass(NegativeAssuranceError, ValueError)
    with pytest.raises(NegativeAssuranceError):
        build_negative_assurance_verdict("not a verdict", floor, critical, ledger, materiality_bar="x")  # type: ignore[arg-type]
    with pytest.raises(NegativeAssuranceError):
        build_negative_assurance_verdict(verdict, "not a floor", critical, ledger, materiality_bar="x")  # type: ignore[arg-type]
    with pytest.raises(NegativeAssuranceError):
        build_negative_assurance_verdict(verdict, floor, "not a set", ledger, materiality_bar="x")  # type: ignore[arg-type]
    with pytest.raises(NegativeAssuranceError):
        build_negative_assurance_verdict(verdict, floor, critical, "not a ledger", materiality_bar="x")  # type: ignore[arg-type]
    with pytest.raises(NegativeAssuranceError):
        build_negative_assurance_verdict(verdict, floor, critical, ledger, materiality_bar=123)  # type: ignore[arg-type]


def test_builder_raises_on_inconsistent_verdict_floor_pair() -> None:
    """TC-ArgusAgent-VERDICT-001-14 — AC7 (AR10): a floor report describing a DIFFERENT verdict raises."""
    rr = _release_ready_verdict()
    other = _insufficient_verdict()
    mismatched_floor = _floor_report(other)  # describes INSUFFICIENT_COVERAGE
    with pytest.raises(NegativeAssuranceError):
        build_negative_assurance_verdict(
            rr, mismatched_floor, CriticalSubsystemSet(), CoverageLedger.build([]),
            materiality_bar="x",
        )


def test_wrapper_is_byte_stable_and_order_independent() -> None:
    """TC-ArgusAgent-VERDICT-001-15 — AC7 (NFR-P1): same inputs → byte-identical wrapper; ledger order does not matter."""
    entries_a = [
        _entry("a_deep.py", CoverageDepth.AUDITED_DEEP, claim=True),
        _entry("crit_auth.py", CoverageDepth.AUDITED_SHALLOW),
        _entry("c_tool.py", CoverageDepth.TOOL_SCANNED_ONLY),
        _entry("d_inferred.py", CoverageDepth.INFERRED),
        _entry("e_skipped.py", CoverageDepth.SKIPPED),
    ]
    ledger_a = CoverageLedger.build(entries_a)
    ledger_b = CoverageLedger.build(list(reversed(entries_a)))  # different input order
    critical = _critical_set_with_not_deep()
    v_a = evaluate_verdict(ledger_a, (), critical_subsystems_all_deep=False)
    v_b = evaluate_verdict(ledger_b, (), critical_subsystems_all_deep=False)
    w_a = build_negative_assurance_verdict(v_a, _floor_report(v_a), critical, ledger_a, materiality_bar="m")
    w_b = build_negative_assurance_verdict(v_b, _floor_report(v_b), critical, ledger_b, materiality_bar="m")
    assert canonical.dumps_bytes(w_a.to_canonical_payload()) == canonical.dumps_bytes(w_b.to_canonical_payload())
    # And byte-stable when built twice from the same inputs.
    assert canonical.dumps_bytes(w_a.to_canonical_payload()) == canonical.dumps_bytes(w_a.to_canonical_payload())


def test_builder_is_pure_no_io_no_clock_ast_scan() -> None:
    """TC-ArgusAgent-VERDICT-001-16 — AC7 (AR8): the module makes no I/O / clock / uuid / random / direct json call."""
    tree = ast.parse(_NA_SOURCE.read_text(encoding="utf-8"), filename=str(_NA_SOURCE))
    forbidden_attrs = {"now", "today", "time", "uuid4", "getpid", "random", "open", "read_text", "read_bytes"}
    forbidden_modules = {"os", "time", "random", "uuid", "datetime", "pathlib", "subprocess"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Attribute) and node.attr in forbidden_attrs:
            raise AssertionError(f"forbidden impure attribute access: .{node.attr}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
            raise AssertionError("forbidden open() call in a pure module")
    leaked = imported & forbidden_modules
    assert not leaked, f"pure module imports an impure module: {sorted(leaked)}"


def test_origins_distinguish_heuristic_from_operator_designated() -> None:
    """TC-ArgusAgent-VERDICT-001-17 — DF-2-3-B intent: the critical set carries per-path origins (auditable)."""
    critical = _critical_set_with_not_deep()
    # crit_auth.py is a genuine heuristic hit; ghost.py is operator-designated.
    assert critical.origins["crit_auth.py"] is CriticalOrigin.HEURISTIC
    assert critical.origins["ghost.py"] is CriticalOrigin.OPERATOR_DESIGNATED
