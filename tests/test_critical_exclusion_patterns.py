"""Verification for pattern-matched critical exclusion (CR-4, 2026-08-03).

Verification area ArgusAgent-LEDGER (TC-ArgusAgent-LEDGER-002-NN).

Why this exists
---------------
``--exclude-critical`` was an exact-path set difference. On this repository that made
the documented escape hatch cost 62 separate flags, which is the same as not having
one — and a gate an operator cannot afford to satisfy trains them to ignore every
gate. Exclusion now matches by exact path, directory prefix, or glob.

The precedence rule (exclude wins on a tie) and the conservative unmatched-designation
policy are UNCHANGED and are pinned here so the widening cannot quietly relax them.
"""

from __future__ import annotations

from argus.ledger.depth_semantics import Criticality
from argus.ledger.critical_subsystems import (
    CriticalCandidate,
    CriticalOrigin,
    identify_critical_subsystems,
)


def _critical(*paths: str) -> list[CriticalCandidate]:
    return [
        CriticalCandidate(file_path=p, criticality=Criticality.CRITICAL) for p in paths
    ]


def test_directory_prefix_clears_a_subtree_in_one_flag() -> None:
    """The headline fix: one exclusion for `tests`, not one per test file."""
    candidates = _critical(
        "tests/test_a.py", "tests/nested/test_b.py", "argus/cli.py"
    )

    result = identify_critical_subsystems(candidates, operator_excluded=["tests"])

    assert result.paths == ("argus/cli.py",)


def test_trailing_slash_form_is_equivalent() -> None:
    candidates = _critical("tests/test_a.py", "argus/cli.py")

    result = identify_critical_subsystems(candidates, operator_excluded=["tests/"])

    assert result.paths == ("argus/cli.py",)


def test_glob_patterns_are_supported() -> None:
    candidates = _critical(
        "argus/cache/__init__.py", "argus/store/__init__.py", "argus/cli.py"
    )

    result = identify_critical_subsystems(
        candidates, operator_excluded=["argus/*/__init__.py"]
    )

    assert result.paths == ("argus/cli.py",)


def test_exact_path_exclusion_still_works_unchanged() -> None:
    """The original behaviour is a subset of the new one, not a replacement."""
    candidates = _critical("argus/cli.py", "argus/pipeline.py")

    result = identify_critical_subsystems(
        candidates, operator_excluded=["argus/cli.py"]
    )

    assert result.paths == ("argus/pipeline.py",)


def test_a_prefix_must_be_a_directory_boundary_not_a_string_prefix() -> None:
    """`test` must not silently swallow `testing_utils.py` — the classic prefix bug."""
    candidates = _critical("tests/a.py", "testing_utils.py")

    result = identify_critical_subsystems(candidates, operator_excluded=["tests"])

    assert "testing_utils.py" in result.paths
    assert "tests/a.py" not in result.paths


def test_exclude_still_wins_over_an_operator_designation() -> None:
    """Precedence is unchanged: a path in both add and exclude is excluded."""
    candidates = _critical("argus/cli.py")

    result = identify_critical_subsystems(
        candidates,
        operator_designated=["tests/test_secrets.py"],
        operator_excluded=["tests"],
    )

    assert result.paths == ("argus/cli.py",)
    assert result.designated_but_unmatched == ()


def test_an_unmatched_designation_still_withholds_release_ready() -> None:
    """The conservative unmatched policy survives: a typo makes the gate STRICTER."""
    result = identify_critical_subsystems(
        _critical("argus/cli.py"), operator_designated=["argus/typo.py"]
    )

    assert "argus/typo.py" in result.paths
    assert result.designated_but_unmatched == ("argus/typo.py",)
    assert result.origins["argus/typo.py"] is CriticalOrigin.OPERATOR_DESIGNATED


def test_no_exclusions_is_a_no_op() -> None:
    candidates = _critical("argus/cli.py", "tests/test_a.py")

    result = identify_critical_subsystems(candidates)

    assert result.paths == ("argus/cli.py", "tests/test_a.py")


def test_result_stays_sorted_and_deterministic_under_pattern_matching() -> None:
    """AR4/NFR-P1: no set-iteration-order reliance leaked in with the pattern filter."""
    candidates = _critical("z/a.py", "a/z.py", "m/m.py", "tests/x.py")

    first = identify_critical_subsystems(candidates, operator_excluded=["tests"])
    second = identify_critical_subsystems(
        list(reversed(candidates)), operator_excluded=["tests"]
    )

    assert first.paths == second.paths == ("a/z.py", "m/m.py", "z/a.py")
