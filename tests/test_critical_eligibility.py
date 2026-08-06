"""Heuristic critical-set ELIGIBILITY filter + the operator exemption (Story 8.2).

Verification area ArgusAgent-LEDGER (``TC-ArgusAgent-LEDGER-001-NN``, continuing the
2.3 sequence). Drivers: ArgusAgent-FR-4 as amended (*"a file ArgusAgent can never grade
``audited_deep`` is ineligible for the heuristically-derived critical set — a gate no run
can satisfy is not a gate"*), DR-5 (the filter), DR-6 (operator designation is EXEMPT),
boundary B3 (a vacuously satisfied gate must be VISIBLE) and boundary B5 (one explicit,
test-pinned precedence order).

Why this file exists
--------------------
``assess_criticality`` matches security tokens over file CONTENT, which is exactly right
for anti-rename-gaming and exactly wrong for a *test* of the security module (its content
is full of the same tokens) or a package ``__init__.py`` that *re-exports* the boundary.
Both classes are ``audited_shallow`` BY CONSTRUCTION, so
``critical_subsystems_all_deep`` was ``False`` forever — a permanently unsatisfiable gate.
On this repository that was 62 of 112 flagged paths.

These are PURE-fold tests over synthetic candidates — zero LLM tokens (NFR-D2), no temp
dirs, no filesystem. The impure-shell seam that DERIVES the eligibility token from the
real ``is_test_file`` / ``is_deep_claim_grounded`` predicates is pinned in
``tests/test_critical_eligibility_pipeline.py``.
"""

from __future__ import annotations

import pytest

from argus.ledger.critical_subsystems import (
    CriticalCandidate,
    CriticalIneligibility,
    CriticalOrigin,
    CriticalSubsystemSet,
    identify_critical_subsystems,
)
from argus.ledger.depth_semantics import Criticality
from argus.store import canonical


def _cand(
    file_path: str,
    *,
    criticality: Criticality = Criticality.CRITICAL,
    ineligibility: CriticalIneligibility | None = None,
) -> CriticalCandidate:
    return CriticalCandidate(
        file_path=file_path, criticality=criticality, ineligibility=ineligibility
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC1 / AC2 / AC3 — what the filter removes, and what it deliberately KEEPS
# ─────────────────────────────────────────────────────────────────────────────


def test_heuristic_critical_test_file_is_filtered_out() -> None:
    """TC-ArgusAgent-LEDGER-001-156 — AC1: a heuristic-CRITICAL TEST file leaves the set.

    A test file is ``audited_shallow`` by construction — it is the SUBJECT of the
    vacuous-test pass, never a target of deep grounding — so it can never satisfy the
    all-deep clause it is placed under.
    """
    result = identify_critical_subsystems(
        [
            _cand("tests/test_auth.py", ineligibility=CriticalIneligibility.TEST_FILE),
            _cand("argus/auth.py"),
        ]
    )

    assert result.paths == ("argus/auth.py",)
    assert "tests/test_auth.py" not in result.origins


def test_heuristic_critical_zero_definition_module_is_filtered_out() -> None:
    """TC-ArgusAgent-LEDGER-001-157 — AC2: a clean-parse ZERO-definition module leaves the set.

    There is nothing in it to ground a deep claim against; the pipeline already
    downgrades exactly this class to ``audited_shallow`` via ``is_deep_claim_grounded``.
    """
    result = identify_critical_subsystems(
        [
            _cand(
                "argus/auth/__init__.py",
                ineligibility=CriticalIneligibility.ZERO_DEFINITION_MODULE,
            ),
            _cand("argus/auth/guard.py"),
        ]
    )

    assert result.paths == ("argus/auth/guard.py",)


def test_an_eligible_critical_candidate_survives_and_is_not_disclosed() -> None:
    """TC-ArgusAgent-LEDGER-001-158 — the FOLD contract: ``ineligibility is None`` ⇒ survives.

    Scope, stated honestly: this pins one half of the fold's own rule — an eligible
    CRITICAL candidate stays in ``paths`` with origin ``HEURISTIC`` and is recorded in
    NO disclosure entry (the map is not a log of everything the fold saw). Its sibling
    ``-156``/``-157`` pin the other half.

    It deliberately does **NOT** pin AC3 / LOCKED decision D3 (*a parse-failed file is
    shallow by CIRCUMSTANCE and must stay ELIGIBLE*). D3 is a property of the SHELL —
    of which entries get ``ineligibility=None`` in the first place — and a fold test
    that hands the answer in as its own input restates the rule instead of testing it.
    Iteration 1 of this story's review proved the cost of that confusion: a genuine D3
    false green survived here untouched. D3 is therefore pinned where it lives, over
    real AST entries, at ``tests/test_critical_eligibility_pipeline.py`` —
    ``TC-ArgusAgent-PIPELINE-002-01`` (both filename shapes) and ``-002-09``.
    """
    result = identify_critical_subsystems([_cand("argus/broken_auth.py")])

    assert result.paths == ("argus/broken_auth.py",)
    assert result.origins["argus/broken_auth.py"] is CriticalOrigin.HEURISTIC
    assert result.heuristic_excluded_ineligible == {}


def test_a_non_critical_ineligible_candidate_is_not_recorded_anywhere() -> None:
    """TC-ArgusAgent-LEDGER-001-159 — the filter narrows the CRITICAL term only.

    An ordinary test file was never in the heuristic set to begin with; disclosing it
    would turn the map into "every ineligible file in the repo" (AC8's explicit bound).
    """
    result = identify_critical_subsystems(
        [
            _cand(
                "tests/test_adder.py",
                criticality=Criticality.NORMAL,
                ineligibility=CriticalIneligibility.TEST_FILE,
            )
        ]
    )

    assert result.paths == ()
    assert result.heuristic_excluded_ineligible == {}


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — DR-6: operator designation is EXEMPT from the eligibility filter
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "path, ineligibility",
    [
        ("tests/test_auth.py", CriticalIneligibility.TEST_FILE),
        ("argus/auth/__init__.py", CriticalIneligibility.ZERO_DEFINITION_MODULE),
    ],
)
def test_operator_designation_overrides_ineligibility(
    path: str, ineligibility: CriticalIneligibility
) -> None:
    """TC-ArgusAgent-LEDGER-001-160 — AC4(a)(b): a designated ineligible path is HONOURED.

    The filter is a correction to a HEURISTIC over-reach, never a veto over the operator.
    A designated path that can never be ``audited_deep`` still withholds ``RELEASE_READY``
    — that is the operator's stated intent and the lever that makes DR-5's residual
    exposure acceptable.
    """
    result = identify_critical_subsystems(
        [_cand(path, ineligibility=ineligibility)], operator_designated=[path]
    )

    assert result.paths == (path,)
    assert result.origins[path] is CriticalOrigin.OPERATOR_DESIGNATED
    # AC4 — an operator-designated path is NEVER recorded as eligibility-excluded.
    assert path not in result.heuristic_excluded_ineligible


def test_operator_designation_of_an_unmatched_path_is_unchanged_by_the_filter() -> None:
    """TC-ArgusAgent-LEDGER-001-161 — AC4(c): the conservative unmatched policy survives.

    A designation matching no candidate is still IN ``paths`` and still recorded in
    ``designated_but_unmatched``, so an operator typo can only make the gate STRICTER.
    """
    result = identify_critical_subsystems(
        [_cand("tests/test_auth.py", ineligibility=CriticalIneligibility.TEST_FILE)],
        operator_designated=["argus/typo.py"],
    )

    assert result.paths == ("argus/typo.py",)
    assert result.designated_but_unmatched == ("argus/typo.py",)
    assert result.origins["argus/typo.py"] is CriticalOrigin.OPERATOR_DESIGNATED
    assert result.heuristic_excluded_ineligible == {
        "tests/test_auth.py": CriticalIneligibility.TEST_FILE
    }


# ─────────────────────────────────────────────────────────────────────────────
# AC6 / boundary B5 — ONE explicit precedence order, pinned as a truth table
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "ineligible, designated, excluded, in_final, origin, in_map",
    [
        (False, False, False, True, CriticalOrigin.HEURISTIC, False),
        (False, False, True, False, None, False),
        (False, True, False, True, CriticalOrigin.OPERATOR_DESIGNATED, False),
        (False, True, True, False, None, False),
        (True, False, False, False, None, True),
        # Ineligible AND excluded: recorded as eligibility-excluded — the FIRST rule
        # that removed it — so the map is a function of the inputs, not of evaluation
        # order.
        (True, False, True, False, None, True),
        (True, True, False, True, CriticalOrigin.OPERATOR_DESIGNATED, False),
        (True, True, True, False, None, False),
    ],
)
def test_precedence_truth_table_eligibility_then_designation_then_exclusion(
    ineligible: bool,
    designated: bool,
    excluded: bool,
    in_final: bool,
    origin: CriticalOrigin | None,
    in_map: bool,
) -> None:
    """TC-ArgusAgent-LEDGER-001-162 — AC6 / B5: the LOCKED order is pinned, not implied.

    ``(i) eligibility filter — heuristic term ONLY → (ii) union with operator designation
    (EXEMPT) → (iii) minus operator exclusion (pattern-matched; exclude wins).``
    Every combination of the three levers over one heuristic-CRITICAL path is asserted so
    the order can never drift into an implementation detail.
    """
    path = "argus/auth.py"
    result = identify_critical_subsystems(
        [
            _cand(
                path,
                ineligibility=(
                    CriticalIneligibility.TEST_FILE if ineligible else None
                ),
            )
        ],
        operator_designated=[path] if designated else None,
        operator_excluded=[path] if excluded else None,
    )

    assert (path in result.paths) is in_final
    if origin is not None:
        assert result.origins[path] is origin
    else:
        assert path not in result.origins
    assert (path in result.heuristic_excluded_ineligible) is in_map


# ─────────────────────────────────────────────────────────────────────────────
# AC8 / boundary B3 — a vacuously satisfied gate is VISIBLE on disk
# ─────────────────────────────────────────────────────────────────────────────


def test_disclosure_map_records_every_filtered_path_and_its_reason() -> None:
    """TC-ArgusAgent-LEDGER-001-163 — AC8: path → CLOSED reason token, for every removal."""
    result = identify_critical_subsystems(
        [
            _cand("tests/test_auth.py", ineligibility=CriticalIneligibility.TEST_FILE),
            _cand(
                "argus/auth/__init__.py",
                ineligibility=CriticalIneligibility.ZERO_DEFINITION_MODULE,
            ),
            _cand("argus/auth/guard.py"),
        ]
    )

    assert result.paths == ("argus/auth/guard.py",)
    assert result.heuristic_excluded_ineligible == {
        "tests/test_auth.py": CriticalIneligibility.TEST_FILE,
        "argus/auth/__init__.py": CriticalIneligibility.ZERO_DEFINITION_MODULE,
    }


def test_vacuously_empty_set_is_distinguishable_from_genuinely_no_criticals() -> None:
    """TC-ArgusAgent-LEDGER-001-164 — AC8 / B3: the two empty sets differ ON DISK.

    "No critical subsystems" and "every critical subsystem was structurally ungradable"
    are very different claims. Before the disclosure map they serialized identically,
    which is how a vacuously satisfied gate becomes invisible.
    """
    vacuous = identify_critical_subsystems(
        [_cand("tests/test_auth.py", ineligibility=CriticalIneligibility.TEST_FILE)]
    )
    genuinely_none = identify_critical_subsystems(
        [_cand("argus/adder.py", criticality=Criticality.NORMAL)]
    )

    assert vacuous.paths == genuinely_none.paths == ()
    assert vacuous.heuristic_excluded_ineligible != {}
    assert genuinely_none.heuristic_excluded_ineligible == {}
    assert canonical.dumps(vacuous.model_dump(mode="json")) != canonical.dumps(
        genuinely_none.model_dump(mode="json")
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC7 / AC9 / AC13 — contract shape: defaults, closed vocabulary, determinism
# ─────────────────────────────────────────────────────────────────────────────


def test_ineligibility_vocabulary_is_closed_to_the_two_by_construction_classes() -> None:
    """TC-ArgusAgent-LEDGER-001-165 — D4: exactly the two classes FR4 enumerates.

    A third member would be a widening of what the tool is allowed to stop asking about,
    and must be argued at story level rather than added in passing.
    """
    assert {m.value for m in CriticalIneligibility} == {
        "test_file",
        "zero_definition_module",
    }
    assert CriticalIneligibility.TEST_FILE.value == "test_file"
    assert CriticalIneligibility.ZERO_DEFINITION_MODULE.value == "zero_definition_module"


def test_candidate_default_means_ELIGIBLE_so_a_forgetful_caller_over_includes() -> None:
    """TC-ArgusAgent-LEDGER-001-166 — AC7: the default is the SAFE direction.

    A ``CriticalCandidate`` built without the new field keeps its exact pre-8.2
    behaviour, and the failure mode of a caller that forgets to supply the fact is
    OVER-inclusion (a stricter gate) — never a false green.
    """
    bare = CriticalCandidate(file_path="argus/auth.py", criticality=Criticality.CRITICAL)
    assert bare.ineligibility is None
    assert identify_critical_subsystems([bare]).paths == ("argus/auth.py",)


def test_new_fields_round_trip_through_a_payload_that_omits_them() -> None:
    """TC-ArgusAgent-LEDGER-001-167 — AC9/NFR-M2: additive-only, read-back safe.

    ``extra="forbid"`` makes a defaultless field a ``ValidationError`` on every persisted
    read-back; both new fields therefore carry defaults, and this asserts the read-back
    rather than assuming it.
    """
    legacy_payload = {
        "schema_version": "1",
        "paths": ["argus/auth.py"],
        "origins": {"argus/auth.py": "heuristic"},
        "designated_but_unmatched": [],
    }
    restored = CriticalSubsystemSet.model_validate(legacy_payload)
    assert restored.heuristic_excluded_ineligible == {}
    assert restored.schema_version == "1"

    # …and a payload carrying the new key round-trips to the closed enum member.
    modern = CriticalSubsystemSet.model_validate(
        {
            **legacy_payload,
            "schema_version": "2",
            "heuristic_excluded_ineligible": {"tests/test_auth.py": "test_file"},
        }
    )
    assert modern.heuristic_excluded_ineligible == {
        "tests/test_auth.py": CriticalIneligibility.TEST_FILE
    }


def test_disclosure_map_is_order_independent_and_float_free() -> None:
    """TC-ArgusAgent-LEDGER-001-168 — AC13 / AR4 / NFR-P1: deterministic bytes.

    Two candidate orderings must serialize byte-identically through the single 1.1
    canonical serializer, which also rejects a float leaf — so a green here is the
    no-float proof as well.
    """
    candidates = [
        _cand("z/test_z.py", ineligibility=CriticalIneligibility.TEST_FILE),
        _cand("a/__init__.py", ineligibility=CriticalIneligibility.ZERO_DEFINITION_MODULE),
        _cand("m/test_m.py", ineligibility=CriticalIneligibility.TEST_FILE),
        _cand("k/guard.py"),
    ]

    first = identify_critical_subsystems(candidates)
    second = identify_critical_subsystems(list(reversed(candidates)))

    assert first.heuristic_excluded_ineligible == second.heuristic_excluded_ineligible
    assert canonical.dumps(first.model_dump(mode="json")) == canonical.dumps(
        second.model_dump(mode="json")
    )


def test_non_ascii_ineligible_path_round_trips_through_the_map_intact() -> None:
    """TC-ArgusAgent-LEDGER-001-169 — AI-E1-1: the standing non-ASCII adversarial pin.

    Extends the -153/-154/-155 non-ASCII coverage onto the new path-keyed structure: a
    Cyrillic test file must survive the map and the serializer byte-intact, not as
    mojibake or an escape sequence.
    """
    cyrillic = "тесты/test_безопасность.py"
    result = identify_critical_subsystems(
        [_cand(cyrillic, ineligibility=CriticalIneligibility.TEST_FILE)]
    )

    assert result.paths == ()
    assert result.heuristic_excluded_ineligible == {
        cyrillic: CriticalIneligibility.TEST_FILE
    }
    encoded = canonical.dumps(result.model_dump(mode="json"))
    assert cyrillic in encoded
    # NFR-S1 — repo-relative POSIX paths + closed enum tokens only.
    assert "test_file" in encoded
