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

Story 8.2 / DR-7 is VERIFY-ONLY — no new matcher, ``_matches_exclusion`` ends that story
byte-identical. The nine tests below were re-verified rather than rewritten, and exactly
two things they did not yet assert were ADDED at the end of this file: that the matcher
is ``fnmatchcase`` and not ``fnmatch`` (a host case-folding regression would break the
byte-identical-across-hosts guarantee, NFR-P1/AR4, and is invisible on Linux where the
two are the same function), and that every DR-7 behaviour survives IN THE PRESENCE OF the
new DR-5 eligibility filter.
"""

from __future__ import annotations

import ast as _ast_module
import inspect

from argus.ledger import critical_subsystems as cs
from argus.ledger.depth_semantics import Criticality
from argus.ledger.critical_subsystems import (
    CriticalCandidate,
    CriticalIneligibility,
    CriticalOrigin,
    identify_critical_subsystems,
)


def _critical(*paths: str) -> list[CriticalCandidate]:
    return [
        CriticalCandidate(file_path=p, criticality=Criticality.CRITICAL) for p in paths
    ]


def _ineligible_test_files(*paths: str) -> list[CriticalCandidate]:
    """Heuristic-CRITICAL candidates the DR-5 filter would remove on its own."""
    return [
        CriticalCandidate(
            file_path=p,
            criticality=Criticality.CRITICAL,
            ineligibility=CriticalIneligibility.TEST_FILE,
        )
        for p in paths
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


# ─────────────────────────────────────────────────────────────────────────────
# Story 8.2 / DR-7 — the two things the nine tests above did not yet assert
# ─────────────────────────────────────────────────────────────────────────────


def test_the_matcher_is_fnmatchcase_and_never_the_host_folding_fnmatch() -> None:
    """TC-ArgusAgent-LEDGER-002-10 — NFR-P1: matching must be CASE-SENSITIVE on every host.

    ``fnmatch`` normalizes case per the HOST platform, so the same
    ``--exclude-critical`` would behave differently on Windows and Linux and break the
    byte-identical-across-hosts guarantee. Asserted two ways deliberately: the source
    check catches the regression on every platform, and the behavioural check proves the
    source check is testing the thing that actually matters.
    """
    source = inspect.getsource(cs)
    assert "from fnmatch import fnmatchcase" in source
    called = {
        node.func.id
        for node in _ast_module.walk(_ast_module.parse(source))
        if isinstance(node, _ast_module.Call) and isinstance(node.func, _ast_module.Name)
    }
    assert "fnmatch" not in called, "host-case-folding fnmatch must never be called"
    assert "fnmatchcase" in called

    # Behavioural: a differently-cased glob must NOT match (on Windows, plain fnmatch
    # would have matched here).
    result = identify_critical_subsystems(
        _critical("tests/a.py"), operator_excluded=["TESTS/*.py"]
    )
    assert result.paths == ("tests/a.py",)


def test_dr7_behaviours_are_unchanged_in_the_presence_of_the_eligibility_filter() -> None:
    """TC-ArgusAgent-LEDGER-002-11 — DR-7 survives DR-5 intact, on all three forms.

    The eligibility filter narrows the HEURISTIC term only, so every exclusion form,
    the exclude-wins tie, the conservative unmatched policy and the no-op must behave
    exactly as the nine tests above pin them even when the candidates carry an
    ineligibility token — including the case where exclusion and eligibility would
    remove the SAME path.
    """
    candidates = [
        *_ineligible_test_files("tests/test_auth.py"),
        *_critical("argus/cli.py", "argus/cache/__init__.py"),
    ]

    # Directory prefix + glob still remove eligible paths; the ineligible one was
    # already gone and is DISCLOSED rather than double-counted as an exclusion.
    result = identify_critical_subsystems(
        candidates, operator_excluded=["tests", "argus/*/__init__.py"]
    )
    assert result.paths == ("argus/cli.py",)
    assert result.heuristic_excluded_ineligible == {
        "tests/test_auth.py": CriticalIneligibility.TEST_FILE
    }

    # Exclude still wins over a designation, even one that exercises the DR-6 exemption.
    tie = identify_critical_subsystems(
        candidates,
        operator_designated=["tests/test_auth.py"],
        operator_excluded=["tests/"],
    )
    assert tie.paths == ("argus/cache/__init__.py", "argus/cli.py")
    assert tie.designated_but_unmatched == ()
    # Designated ⇒ never reported as eligibility-excluded, even when exclusion won.
    assert tie.heuristic_excluded_ineligible == {}

    # An exclude matching nothing is still a harmless no-op, and an unmatched
    # designation is still recorded conservatively.
    noop = identify_critical_subsystems(
        candidates, operator_designated=["argus/typo.py"], operator_excluded=["nope.py"]
    )
    assert noop.paths == ("argus/cache/__init__.py", "argus/cli.py", "argus/typo.py")
    assert noop.designated_but_unmatched == ("argus/typo.py",)
    assert noop.origins["argus/typo.py"] is CriticalOrigin.OPERATOR_DESIGNATED
