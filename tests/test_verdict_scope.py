"""Tests for the DISCLOSED assessment-scope seam on the PURE verdict gate.

Verification area ArgusAgent-VERDICT (TC-ArgusAgent-VERDICT-002-NN). Covers the
``scope_paths`` narrowing added to :func:`evaluate_verdict`: the false-negative it
removes (a test-heavy repository graded ``NOT_READY_FOR_RELEASE`` with ZERO blocking
findings), and — the load-bearing half — the invariants that keep the narrowing from
becoming a loophole.

The rejected design (a ``core_app_ready`` flag that let a healthy-looking application
BYPASS ``INSUFFICIENT_COVERAGE_FLOOR``) is pinned as forbidden by
``test_scope_never_bypasses_the_floor``: narrowing may change WHAT is claimed, never
the bar for claiming it. Pure-function tests — zero LLM tokens, no temp dirs.
"""

from __future__ import annotations

from fractions import Fraction

from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
)
from argus.store import canonical
from argus.verdict.verdict_gate import (
    CoverageScope,
    Verdict,
    evaluate_verdict,
)

from tests.test_verdict_gate import _ast_finding  # reuse the 1.6 blocking-finding builder

_DEEP = CoverageDepth.AUDITED_DEEP
_SHALLOW = CoverageDepth.AUDITED_SHALLOW


def _entry(file_path: str, depth: CoverageDepth) -> CoverageLedgerEntry:
    return CoverageLedgerEntry(
        file_path=file_path, depth=depth, claim_present=(depth is _DEEP)
    )


def _repo(*, app_deep: int, app_shallow: int, tests: int) -> CoverageLedger:
    """A ledger shaped like a real repository: app files + shallow-by-design tests."""
    entries = [_entry(f"src/deep_{i}.py", _DEEP) for i in range(app_deep)]
    entries += [_entry(f"src/shallow_{i}.py", _SHALLOW) for i in range(app_shallow)]
    entries += [_entry(f"tests/test_{i}.py", _SHALLOW) for i in range(tests)]
    return CoverageLedger.build(tuple(entries))


def _application_paths(ledger: CoverageLedger) -> frozenset[str]:
    return frozenset(
        e.file_path for e in ledger.entries if not e.file_path.startswith("tests/")
    )


# ─────────────────────────────────────────────────────────────────────────────
# The false negative the seam exists to remove
# ─────────────────────────────────────────────────────────────────────────────


def test_test_heavy_repo_is_a_false_negative_without_scope() -> None:
    """TC-ArgusAgent-VERDICT-002-01 — the motivating defect, pinned.

    Every application file audited deep, zero blocking findings, and the whole-ledger
    fold STILL returns NOT_READY_FOR_RELEASE — earned purely by being well-tested.
    """
    ledger = _repo(app_deep=40, app_shallow=0, tests=86)
    verdict = evaluate_verdict(ledger)

    assert verdict.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert verdict.blocking_finding_count == 0  # nothing is actually wrong
    assert verdict.deep_ratio == Fraction(40, 126)
    assert verdict.coverage_scope is None


def test_application_scope_resolves_the_false_negative() -> None:
    """TC-ArgusAgent-VERDICT-002-02 — same ledger, assessed over application files."""
    ledger = _repo(app_deep=40, app_shallow=0, tests=86)
    verdict = evaluate_verdict(ledger, scope_paths=_application_paths(ledger))

    assert verdict.verdict is Verdict.RELEASE_READY
    assert verdict.exit_code == 0
    assert verdict.coverage_scope is not None
    assert verdict.coverage_scope.assessed_deep_ratio == Fraction(1, 1)
    assert verdict.coverage_scope.assessed_total_count == 40
    assert verdict.coverage_scope.excluded_count == 86


# ─────────────────────────────────────────────────────────────────────────────
# The invariants that keep the narrowing honest
# ─────────────────────────────────────────────────────────────────────────────


def test_scope_never_bypasses_the_floor() -> None:
    """TC-ArgusAgent-VERDICT-002-03 — THE guardrail. Narrowing is not a floor bypass.

    An application whose OWN files are under-audited (4/40 deep = 10%, below the 20%
    floor) must still return INSUFFICIENT_COVERAGE under an application scope. The
    rejected ``core_app_ready`` design returned RELEASE_READY here — asserting
    release-readiness over a population it never adequately examined.
    """
    ledger = _repo(app_deep=4, app_shallow=36, tests=86)
    verdict = evaluate_verdict(ledger, scope_paths=_application_paths(ledger))

    assert verdict.coverage_scope is not None
    assert verdict.coverage_scope.assessed_deep_ratio == Fraction(1, 10)
    assert verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert verdict.exit_code == 3


def test_scope_still_applies_the_release_ready_threshold() -> None:
    """TC-ArgusAgent-VERDICT-002-04 — between floor and threshold stays blocking."""
    ledger = _repo(app_deep=10, app_shallow=30, tests=86)  # 25%: over floor, under 60%
    verdict = evaluate_verdict(ledger, scope_paths=_application_paths(ledger))

    assert verdict.coverage_scope is not None
    assert verdict.coverage_scope.assessed_deep_ratio == Fraction(1, 4)
    assert verdict.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert verdict.exit_code == 2


def test_blocking_finding_in_a_held_out_file_still_blocks() -> None:
    """TC-ArgusAgent-VERDICT-002-05 — findings are NOT filtered by the scope.

    Narrowing the COVERAGE denominator must not narrow the finding set: a verdict-
    eligible finding located in a held-out test file still blocks the release.
    """
    ledger = _repo(app_deep=40, app_shallow=0, tests=86)
    finding = _ast_finding(file_path="tests/test_0.py")

    verdict = evaluate_verdict(
        ledger, (finding,), scope_paths=_application_paths(ledger)
    )

    assert verdict.blocking_finding_count == 1
    assert verdict.verdict is Verdict.NOT_READY_FOR_RELEASE


def test_critical_subsystem_clause_still_in_force_under_scope() -> None:
    """TC-ArgusAgent-VERDICT-002-06 — the FR16 clause is unscoped and still gates."""
    ledger = _repo(app_deep=40, app_shallow=0, tests=86)
    verdict = evaluate_verdict(
        ledger,
        scope_paths=_application_paths(ledger),
        critical_subsystems_all_deep=False,
    )

    assert verdict.verdict is Verdict.NOT_READY_FOR_RELEASE


def test_empty_assessed_population_is_insufficient_coverage() -> None:
    """TC-ArgusAgent-VERDICT-002-07 — nothing assessed ⇒ nothing claimed (no ZeroDivision)."""
    ledger = _repo(app_deep=0, app_shallow=0, tests=20)
    verdict = evaluate_verdict(ledger, scope_paths=frozenset())

    assert verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert verdict.exit_code == 3
    assert verdict.coverage_scope is not None
    assert verdict.coverage_scope.assessed_total_count == 0
    assert verdict.coverage_scope.assessed_deep_ratio == Fraction(0, 1)


def test_whole_ledger_numbers_survive_the_narrowing() -> None:
    """TC-ArgusAgent-VERDICT-002-08 — deep_ratio keeps its LOCKED whole-ledger meaning.

    A scoped verdict must still carry the honest repository-wide number, so a reader
    can never mistake a scoped claim for a repository-wide one.
    """
    ledger = _repo(app_deep=40, app_shallow=0, tests=86)
    verdict = evaluate_verdict(ledger, scope_paths=_application_paths(ledger))

    assert verdict.deep_ratio == Fraction(40, 126)
    assert verdict.deep_count == 40
    assert verdict.total_count == 126


# ─────────────────────────────────────────────────────────────────────────────
# Determinism + byte-identity (AR4 / the 6.3-6.4 additive precedent)
# ─────────────────────────────────────────────────────────────────────────────


def test_unscoped_payload_is_byte_identical_to_the_pre_seam_fold() -> None:
    """TC-ArgusAgent-VERDICT-002-09 — an unengaged feature changes no byte.

    ``coverage_scope`` is OMITTED from the canonical payload when no narrowing was
    applied — not serialized as ``null`` — so every persisted V1 verdict still
    round-trips and no schema_version bump is owed for the default path.
    """
    ledger = _repo(app_deep=3, app_shallow=2, tests=0)
    payload = canonical.dumps(evaluate_verdict(ledger).to_canonical_payload())

    # Absent entirely — not `"coverage_scope":null`, which would change the hash of
    # every pre-existing verdict. The exact pre-seam byte string is pinned by
    # test_verdict_gate.GOLDEN_VERDICT_CANONICAL, which still passes unmodified.
    assert "coverage_scope" not in payload


def test_scoped_payload_discloses_with_exact_fraction_encoding() -> None:
    """TC-ArgusAgent-VERDICT-002-10 — disclosure present; ratio is num/den, never float."""
    ledger = _repo(app_deep=40, app_shallow=0, tests=86)
    verdict = evaluate_verdict(ledger, scope_paths=_application_paths(ledger))
    payload = canonical.dumps(verdict.to_canonical_payload())

    assert '"coverage_scope"' in payload
    assert '"assessed_deep_ratio":"1/1"' in payload  # AR4 num/den, not 1.0
    assert '"excluded_reason":"test_files"' in payload
    assert '"scope_id":"application"' in payload


def test_scope_membership_order_and_type_do_not_change_the_result() -> None:
    """TC-ArgusAgent-VERDICT-002-11 — PURE: no reliance on caller iteration order (AR4)."""
    ledger = _repo(app_deep=40, app_shallow=0, tests=86)
    paths = sorted(_application_paths(ledger))

    as_frozenset = evaluate_verdict(ledger, scope_paths=frozenset(paths))
    as_forward_tuple = evaluate_verdict(ledger, scope_paths=tuple(paths))
    as_reversed_tuple = evaluate_verdict(ledger, scope_paths=tuple(reversed(paths)))

    reference = canonical.dumps(as_frozenset.to_canonical_payload())
    assert canonical.dumps(as_forward_tuple.to_canonical_payload()) == reference
    assert canonical.dumps(as_reversed_tuple.to_canonical_payload()) == reference


def test_paths_outside_the_ledger_are_ignored_not_counted() -> None:
    """TC-ArgusAgent-VERDICT-002-12 — the scope filters the ledger, never invents entries."""
    ledger = _repo(app_deep=3, app_shallow=1, tests=5)
    padded = _application_paths(ledger) | {"src/does_not_exist.py", "vendor/x.py"}

    verdict = evaluate_verdict(ledger, scope_paths=padded)

    assert verdict.coverage_scope is not None
    assert verdict.coverage_scope.assessed_total_count == 4  # not 6
    assert verdict.coverage_scope.excluded_count == 5


def test_coverage_scope_model_is_frozen_and_forbids_extras() -> None:
    """TC-ArgusAgent-VERDICT-002-13 — the 1.1/1.2/1.6 frozen extra=forbid precedent."""
    import pytest
    from pydantic import ValidationError

    scope = CoverageScope(
        scope_id="application",
        excluded_reason="test_files",
        assessed_deep_count=1,
        assessed_total_count=2,
        assessed_deep_ratio=Fraction(1, 2),
        excluded_count=3,
    )
    with pytest.raises(ValidationError):
        scope.scope_id = "other"  # type: ignore[misc]
    with pytest.raises(ValidationError):
        CoverageScope(
            scope_id="application",
            excluded_reason="test_files",
            assessed_deep_count=1,
            assessed_total_count=2,
            assessed_deep_ratio=Fraction(1, 2),
            excluded_count=3,
            unknown_field="nope",  # type: ignore[call-arg]
        )
