"""Story 3.4 — the PURE resume-plan core + the resume-plan invariants.

Verification area ArgusAgent-COST (``TC-ArgusAgent-COST-001-NN``, continuing 3-1/3-2/3-3).
Covers the pure ``cost/resume.py`` deliverable:
  - AC1: carried-forward = EVERY prior-ASSESSED path (all depths — ``audited_deep``,
    ``audited_shallow``, ``tool_scanned_only``, assessed-but-``skipped`` alike, the
    prior halt report's ``assessed_files``; reused verbatim, NFR-R2 "no loss of prior
    coverage"); resume target = the remainder re-projected against the raised ceiling
    (NOT re-audited here).
  - AC4: a partial-state resume (raised budget still short) keeps a shrunken
    still-skipped remainder + ``halts_again=True``.
  - AC5/AC7: the ``ResumePlan`` is frozen / ``extra="forbid"`` / no-``float`` /
    secret-safe (no abs-path/source byte) / round-trips through the single 1.1
    serializer; a non-ASCII (café/Cyrillic) path round-trips intact.
  - AC7: PURE (AST scan — no FS/clock/uuid/random/os) / typed-error on a divergent
    tree / order-independence + byte-stability of the plan.

The e2e resume tests (halt→resume byte-identity, tamper-on-resume) live in
``test_pipeline_signature_demo.py`` (the impure pipeline shell).
"""

from __future__ import annotations

import ast
from fractions import Fraction
from pathlib import Path

import pytest
from pydantic import ValidationError

from argus.cost.budget_governor import budget_config_from_budget
from argus.cost.exhaustion import (
    CostUnit,
    HaltReport,
    build_halt_report,
    project_halt_point,
)
from argus.cost.resume import (
    RESUME_PLAN_SCHEMA_VERSION,
    ResumeError,
    ResumePlan,
    build_resume_plan,
)
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    grade_entry,
)
from argus.store import canonical


# ── helpers ──────────────────────────────────────────────────────────────────


def _units(*specs: tuple[str, int]) -> tuple[CostUnit, ...]:
    return tuple(CostUnit(path=p, cost=c) for p, c in specs)


def _prior_ledger(deep: tuple[str, ...], skipped: tuple[str, ...]) -> CoverageLedger:
    entries = [
        grade_entry(file_path=p, proposed_depth=CoverageDepth.AUDITED_DEEP, claim_present=True)
        for p in deep
    ] + [
        grade_entry(file_path=p, proposed_depth=CoverageDepth.SKIPPED, claim_present=False)
        for p in skipped
    ]
    return CoverageLedger.build(entries)


def _prior_halt(units: tuple[CostUnit, ...], budget: int) -> HaltReport:
    return build_halt_report(project_halt_point(units, config=budget_config_from_budget(budget)))


# ── AC1 — carry forward prior coverage, continue only the remainder ───────────


def test_resume_plan_carries_forward_prior_deep_and_targets_remainder() -> None:
    """TC-ArgusAgent-COST-001-116 — AC1: carried-forward = prior audited_deep; target = remainder."""
    units = _units(("a.py", 5), ("b.py", 5))
    halt_b1 = _prior_halt(units, 6)  # admits a.py (5<6), halts at b.py (10>=6)
    assert halt_b1.assessed_files == ("a.py",)
    assert halt_b1.skipped_on_exhaustion_files == ("b.py",)

    prior = _prior_ledger(deep=("a.py",), skipped=("b.py",))
    plan = build_resume_plan(prior, halt_b1, units, budget_config_from_budget(100))

    assert plan.carried_forward_paths == ("a.py",)
    assert plan.resume_target_paths == ("b.py",)
    assert plan.still_skipped_paths == ()
    assert plan.halts_again is False
    assert plan.prior_total_credits == 5
    assert plan.raised_ceiling_credits == 100


def test_resume_plan_carries_forward_every_assessed_depth_not_only_deep() -> None:
    """TC-ArgusAgent-COST-001-132 — AC1/NFR-R2: carry forward ALL assessed paths, not just audited_deep.

    The keystone-bug regression at the PURE layer: a prior run that ASSESSED a file it
    graded NON-deep (a test file → ``audited_shallow``) must carry that path forward
    VERBATIM — it is in neither the still-skipped set nor the resume target, so dropping
    it (the old ``audited_deep``-only behavior) silently loses prior coverage and breaks
    the AC2 byte-identity keystone. Here ``a_test.py`` (shallow) sorts into the ASSESSED
    prefix of ``halt(6)`` alongside no deep file; it MUST be carried forward.
    """
    # a_test.py (shallow, 5) sorts before src.py (deep, 5). halt(6) admits a_test.py,
    # then halts at src.py (5+5>=6). The assessed prefix is the SHALLOW test file.
    units = _units(("a_test.py", 5), ("src.py", 5))
    halt_b1 = _prior_halt(units, 6)
    assert halt_b1.assessed_files == ("a_test.py",)  # a non-deep file in the assessed prefix
    assert halt_b1.skipped_on_exhaustion_files == ("src.py",)

    # Build a prior ledger where a_test.py is audited_SHALLOW (not deep) + src.py skipped.
    prior_entries = [
        grade_entry(file_path="a_test.py", proposed_depth=CoverageDepth.AUDITED_SHALLOW, claim_present=True),
        grade_entry(file_path="src.py", proposed_depth=CoverageDepth.SKIPPED, claim_present=False),
    ]
    prior = CoverageLedger.build(prior_entries)

    plan = build_resume_plan(prior, halt_b1, units, budget_config_from_budget(100))
    # The shallow assessed file is carried forward (NOT dropped); only src.py is the target.
    assert plan.carried_forward_paths == ("a_test.py",)
    assert plan.resume_target_paths == ("src.py",)
    assert plan.still_skipped_paths == ()


def test_resume_continues_does_not_re_spend_prior_credits() -> None:
    """TC-ArgusAgent-COST-001-117 — AC1: the raised ceiling is a TOTAL budget (prior spend seeded)."""
    units = _units(("a.py", 5), ("b.py", 5), ("c.py", 5))
    halt_b1 = _prior_halt(units, 6)  # admits a.py only
    prior = _prior_ledger(deep=("a.py",), skipped=("b.py", "c.py"))
    # B2=11: prior spend 5 + b.py 5 = 10 < 11 admits b.py; + c.py 5 = 15 >= 11 skips c.py.
    plan = build_resume_plan(prior, halt_b1, units, budget_config_from_budget(11))
    assert plan.resume_target_paths == ("b.py",)
    assert plan.still_skipped_paths == ("c.py",)
    assert plan.halts_again is True


def test_resume_plan_no_ceiling_covers_entire_remainder() -> None:
    """TC-ArgusAgent-COST-001-118 — AC1: a raised budget of 0 (no ceiling) covers the whole remainder."""
    units = _units(("a.py", 5), ("b.py", 5), ("c.py", 5))
    halt_b1 = _prior_halt(units, 6)
    prior = _prior_ledger(deep=("a.py",), skipped=("b.py", "c.py"))
    plan = build_resume_plan(prior, halt_b1, units, budget_config_from_budget(0))
    assert plan.resume_target_paths == ("b.py", "c.py")
    assert plan.still_skipped_paths == ()
    assert plan.halts_again is False


# ── AC4 — partial-state resume halts again honestly ───────────────────────────


def test_partial_resume_keeps_shrunken_skipped_set() -> None:
    """TC-ArgusAgent-COST-001-119 — AC4: a raised budget still short leaves a shrunken still-skipped set."""
    units = _units(("a.py", 5), ("b.py", 5), ("c.py", 5), ("d.py", 5))
    halt_b1 = _prior_halt(units, 6)  # admits a.py only; skips b,c,d
    prior = _prior_ledger(deep=("a.py",), skipped=("b.py", "c.py", "d.py"))
    # B2=16: prior 5 + b 5 =10 <16; +c 5=15<16; +d 5=20>=16 skips d only.
    plan = build_resume_plan(prior, halt_b1, units, budget_config_from_budget(16))
    assert plan.carried_forward_paths == ("a.py",)
    assert plan.resume_target_paths == ("b.py", "c.py")
    assert plan.still_skipped_paths == ("d.py",)
    assert plan.halts_again is True


def test_resume_with_budget_at_or_below_prior_spend_covers_nothing_new() -> None:
    """TC-ArgusAgent-COST-001-120 — AC4: a raised budget <= prior spend admits no new remainder."""
    units = _units(("a.py", 5), ("b.py", 5))
    halt_b1 = _prior_halt(units, 6)
    prior = _prior_ledger(deep=("a.py",), skipped=("b.py",))
    # B2=5: the seed (prior spend 5) already breaches a 5-ceiling (>= is a breach).
    plan = build_resume_plan(prior, halt_b1, units, budget_config_from_budget(5))
    assert plan.resume_target_paths == ()
    assert plan.still_skipped_paths == ("b.py",)
    assert plan.halts_again is True


# ── AC7 — typed error on a divergent tree / commit ────────────────────────────


def test_divergent_carried_forward_path_raises_resume_error() -> None:
    """TC-ArgusAgent-COST-001-121 — AC7: a carried-forward path absent from the current index → ResumeError."""
    units = _units(("b.py", 5))  # a.py is GONE from the current index
    halt_b1 = build_halt_report(
        project_halt_point(_units(("a.py", 5), ("b.py", 5)), config=budget_config_from_budget(6))
    )
    prior = _prior_ledger(deep=("a.py",), skipped=("b.py",))
    with pytest.raises(ResumeError) as exc:
        build_resume_plan(prior, halt_b1, units, budget_config_from_budget(100))
    assert "diverged" in str(exc.value)
    assert "a.py" in str(exc.value)


def test_divergent_skipped_path_raises_resume_error() -> None:
    """TC-ArgusAgent-COST-001-122 — AC7: a prior skipped path absent from the current index → ResumeError."""
    units = _units(("a.py", 5))  # b.py is GONE
    halt_b1 = build_halt_report(
        project_halt_point(_units(("a.py", 5), ("b.py", 5)), config=budget_config_from_budget(6))
    )
    prior = _prior_ledger(deep=("a.py",), skipped=("b.py",))
    with pytest.raises(ResumeError):
        build_resume_plan(prior, halt_b1, units, budget_config_from_budget(100))


def test_non_ledger_argument_raises_resume_error() -> None:
    """TC-ArgusAgent-COST-001-123 — AC7: a non-CoverageLedger prior_ledger → typed ResumeError."""
    units = _units(("a.py", 5))
    halt = _prior_halt(units, 0)
    with pytest.raises(ResumeError):
        build_resume_plan({"not": "a ledger"}, halt, units, budget_config_from_budget(0))  # type: ignore[arg-type]


def test_non_halt_report_argument_raises_resume_error() -> None:
    """TC-ArgusAgent-COST-001-124 — AC7: a non-HaltReport prior_halt_report → typed ResumeError."""
    prior = _prior_ledger(deep=("a.py",), skipped=())
    with pytest.raises(ResumeError):
        build_resume_plan(prior, object(), _units(("a.py", 5)), budget_config_from_budget(0))


# ── AC5/AC7 — frozen, no-float, secret-safe, round-trip ───────────────────────


def test_resume_plan_is_frozen_and_forbids_extra() -> None:
    """TC-ArgusAgent-COST-001-125 — AC5: the ResumePlan is frozen + extra='forbid'."""
    plan = build_resume_plan(
        _prior_ledger(deep=("a.py",), skipped=()),
        _prior_halt(_units(("a.py", 5)), 0),
        _units(("a.py", 5)),
        budget_config_from_budget(0),
    )
    with pytest.raises(ValidationError):
        ResumePlan(prior_total_credits=0, halts_again=False, bogus="x")  # type: ignore[call-arg]
    # frozen — assignment raises.
    with pytest.raises(ValidationError):
        plan.prior_total_credits = 99  # type: ignore[misc]


def test_resume_plan_round_trips_through_single_serializer_no_float() -> None:
    """TC-ArgusAgent-COST-001-126 — AC5: the plan round-trips through the 1.1 canonical serializer (no float)."""
    plan = build_resume_plan(
        _prior_ledger(deep=("a.py", "b.py"), skipped=("c.py",)),
        _prior_halt(_units(("a.py", 5), ("b.py", 5), ("c.py", 5)), 12),
        _units(("a.py", 5), ("b.py", 5), ("c.py", 5)),
        budget_config_from_budget(20),
    )
    payload = plan.to_canonical_payload()
    raw = canonical.dumps_bytes(payload)  # raises on a float leaf — the determinism backstop
    reloaded = canonical.loads(raw)
    again = ResumePlan.model_validate(reloaded)
    assert again == plan
    assert canonical.dumps_bytes(again.to_canonical_payload()) == raw
    # No float byte anywhere in the canonical payload.
    assert b"." not in raw.replace(b'.py"', b'PY')  # no decimal point (paths use .py)


def test_resume_plan_carries_no_absolute_path_or_source_byte() -> None:
    """TC-ArgusAgent-COST-001-127 — AC5/NFR-S1: the plan carries only repo-relative paths + int/bool."""
    plan = build_resume_plan(
        _prior_ledger(deep=("src/a.py",), skipped=("src/b.py",)),
        _prior_halt(_units(("src/a.py", 5), ("src/b.py", 5)), 6),
        _units(("src/a.py", 5), ("src/b.py", 5)),
        budget_config_from_budget(100),
    )
    raw = canonical.dumps_bytes(plan.to_canonical_payload())
    text = raw.decode("utf-8")
    assert "/home/" not in text and "C:\\" not in text and ":\\" not in text
    for p in plan.carried_forward_paths + plan.resume_target_paths:
        assert not p.startswith("/")


def test_non_ascii_paths_round_trip_intact() -> None:
    """TC-ArgusAgent-COST-001-128 — AC5/AI-E1-1: a café/Cyrillic path round-trips intact through the plan."""
    cafe = "src/café_guard.py"
    cyr = "src/модуль.py"
    units = _units((cafe, 5), (cyr, 5))
    halt_b1 = _prior_halt(units, 6)  # admits café (sorts first), skips Cyrillic
    prior = _prior_ledger(deep=(cafe,), skipped=(cyr,))
    plan = build_resume_plan(prior, halt_b1, units, budget_config_from_budget(100))
    assert cafe in plan.carried_forward_paths
    assert cyr in plan.resume_target_paths
    raw = canonical.dumps_bytes(plan.to_canonical_payload())
    again = ResumePlan.model_validate(canonical.loads(raw))
    assert cafe in again.carried_forward_paths
    assert cyr in again.resume_target_paths
    assert again == plan


# ── AC7 — purity (AST scan) + determinism (order-independence + byte-stability) ──


def test_resume_module_is_pure_ast_scan() -> None:
    """TC-ArgusAgent-COST-001-129 — AC7: cost/resume.py reads no clock/uuid/random/os, does no I/O."""
    src = Path("argus/cost/resume.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned = {"datetime", "time", "uuid", "random", "os", "open", "subprocess", "socket"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in banned, alias.name
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in banned, node.module
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open"


def test_resume_plan_is_order_independent_and_byte_stable() -> None:
    """TC-ArgusAgent-COST-001-130 — AC7/NFR-P1: two input orderings → the identical plan + identical bytes."""
    spec = (("a.py", 5), ("b.py", 5), ("c.py", 5))
    halt_b1 = _prior_halt(_units(*spec), 6)
    prior = _prior_ledger(deep=("a.py",), skipped=("b.py", "c.py"))
    forward = build_resume_plan(prior, halt_b1, _units(*spec), budget_config_from_budget(13))
    reverse = build_resume_plan(
        prior, halt_b1, _units(*reversed(spec)), budget_config_from_budget(13)
    )
    assert forward == reverse
    assert canonical.dumps_bytes(forward.to_canonical_payload()) == canonical.dumps_bytes(
        reverse.to_canonical_payload()
    )
    # Built twice → byte-identical (no clock/uuid leak).
    again = build_resume_plan(prior, halt_b1, _units(*spec), budget_config_from_budget(13))
    assert canonical.dumps_bytes(again.to_canonical_payload()) == canonical.dumps_bytes(
        forward.to_canonical_payload()
    )


def test_schema_version_is_localized_constant() -> None:
    """TC-ArgusAgent-COST-001-131 — AC5: the schema_version is the localized constant (never env/clock)."""
    assert RESUME_PLAN_SCHEMA_VERSION == "1"
    plan = build_resume_plan(
        _prior_ledger(deep=("a.py",), skipped=()),
        _prior_halt(_units(("a.py", 5)), 0),
        _units(("a.py", 5)),
        budget_config_from_budget(0),
    )
    assert plan.schema_version == RESUME_PLAN_SCHEMA_VERSION
    # deep_ratio-style Fraction is NOT on this model (counts only) — pin no-float.
    for value in plan.model_dump().values():
        assert not isinstance(value, (float, Fraction))
