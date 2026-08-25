"""Detector base — finding builder + Protocol (Story 1.5, AC3/AC4/AC6).

Verification area ArgusAgent-DETECT (TC-ArgusAgent-DETECT-001-NN). The locator-required
``Recording`` finding builder (FR13): a valid draft mints a valid 1.2 ``Recording``
reusing the 1.2 models verbatim; a malformed locator is rejected (not minted).
Pure — no tree-sitter dependency here.
"""

from __future__ import annotations

import ast
import pathlib
from typing import TYPE_CHECKING

import pytest

import argus.detectors
import argus.detectors.base

from argus.detectors.base import (
    DegradedCondition,
    Detector,
    DetectorResult,
    FindingDraft,
    build_recording,
)
from argus.ledger.coverage_ledger import CoverageDepth
from argus.ledger.recording import Recording, RecordingValidationError
from argus.detectors.orphan_code import OrphanCodeDetector
from argus.detectors.secret_scan import SecretScanDetector
from argus.detectors.tool_runner import ToolRunnerDetector
from argus.detectors.vacuous_test import VacuousTestDetector


def test_build_recording_mints_valid_recording() -> None:
    """TC-ArgusAgent-DETECT-001-80 — a valid draft mints a 1.2 Recording with one locator."""
    draft = FindingDraft(
        file_path="tests/test_widget.py",
        start_line=4,
        end_line=9,
        ast_span="function:test_widget@4-9",
        rule_id="vacuous_test_ast",
        advisory=True,
        coverage_envelope_slice="root",
    )
    rec = build_recording(
        draft, depth_supported=CoverageDepth.AUDITED_SHALLOW, claim_present=False
    )

    assert isinstance(rec, Recording)
    assert rec.rule_id == "vacuous_test_ast"
    assert rec.advisory is True
    assert rec.depth_supported is CoverageDepth.AUDITED_SHALLOW
    assert len(rec.locators) == 1
    loc = rec.locators[0]
    assert loc.file_path == "tests/test_widget.py"
    assert loc.start_line == 4
    assert loc.end_line == 9
    assert loc.ast_span == "function:test_widget@4-9"
    # recording_id is content-derived + stable (AR4/AR11), never uuid/arrival order.
    assert rec.recording_id == rec.finding_id
    assert rec.recording_id.startswith("vacuous_test_ast:")
    assert build_recording(draft).recording_id == rec.recording_id


def test_recording_id_distinct_per_finding() -> None:
    """TC-ArgusAgent-DETECT-001-81 — distinct findings get distinct content-derived ids."""
    base = dict(start_line=1, end_line=2, rule_id="vacuous_test_heuristic", advisory=True)
    a = build_recording(FindingDraft(file_path="tests/test_a.py", **base))
    b = build_recording(FindingDraft(file_path="tests/test_b.py", **base))
    assert a.recording_id != b.recording_id


def test_build_recording_rejects_malformed_locator() -> None:
    """TC-ArgusAgent-DETECT-001-82 — a malformed span is rejected (FR13 locator-or-reject)."""
    with pytest.raises(RecordingValidationError):
        build_recording(
            FindingDraft(
                file_path="tests/test_x.py",
                start_line=9,
                end_line=4,  # end < start → no verifiable locator
                rule_id="vacuous_test_heuristic",
                advisory=True,
            )
        )


def test_detector_result_is_frozen_and_extra_forbid() -> None:
    """TC-ArgusAgent-DETECT-001-83 — DetectorResult / DegradedCondition are frozen extra=forbid."""
    result = DetectorResult(degraded=(DegradedCondition(file_path="a.py", reason="x"),))
    with pytest.raises(Exception):
        result.findings = ()  # type: ignore[misc]
    with pytest.raises(Exception):
        DetectorResult(bogus=1)  # type: ignore[call-arg]


def test_vacuous_detector_satisfies_protocol() -> None:
    """TC-ArgusAgent-DETECT-001-84 — all FOUR concrete detectors satisfy the Detector Protocol.

    Story 1.5 wrote this as ``assert isinstance(VacuousTestDetector(), Detector)``. Story
    18.4 kept the id and STRENGTHENED the assertion from one detector to four, and moved it
    off ``isinstance``: a ``runtime_checkable`` protocol's ``isinstance`` checks member
    PRESENCE only — never callability, never signature, never return type — so the shipped
    assertion answered ``True`` for a class whose ``run`` is the integer ``42``. It is now
    structural (§2.3: no ``isinstance``/``issubclass`` against a Protocol anywhere in this
    module), and the STATIC half of the same claim is the four ``if TYPE_CHECKING:``
    conformance pins inside ``argus/`` that ``mypy argus`` checks and ``-145`` requires.
    """
    detectors = (
        VacuousTestDetector,
        SecretScanDetector,
        ToolRunnerDetector,
        OrphanCodeDetector,
    )
    for cls in detectors:
        rule_id = getattr(cls, "rule_id", None)
        assert isinstance(rule_id, str) and rule_id, (
            f"{cls.__name__} must carry a non-empty `str` class-level `rule_id`; found "
            f"{rule_id!r}."
        )
        run = getattr(cls, "run", None)
        assert callable(run), f"{cls.__name__}.run must be callable; found {run!r}."
        # `from __future__ import annotations` is in force in every detector module, so the
        # DECLARED return type is readable as a string without evaluating it — version-stable
        # on 3.10/3.11/3.12 alike, unlike the `isinstance` check this replaced.
        declared = getattr(run, "__annotations__", {}).get("return")
        assert declared == "DetectorResult", (
            f"{cls.__name__}.run must be declared `-> DetectorResult`; found `-> {declared}`."
        )

    assert len({cls.rule_id for cls in detectors}) == len(detectors), (
        "the four detectors must carry four DISTINCT rule_ids: "
        f"{sorted(cls.rule_id for cls in detectors)}."
    )

    # AC1.5 — the symbol stays exported under its own name. This story makes `Detector`
    # MEAN something; it does not remove, rename or move it. That the Protocol is no longer
    # `@runtime_checkable` is asserted STRUCTURALLY by `-146`: per AC5.4 no guard in this
    # module decides anything by `isinstance`/`issubclass` against a Protocol, not even to
    # assert the TypeError, because that is the exact spelling §0.3 measured vacuous and
    # version-unstable and the one this epic exists to stop coming back.
    assert Detector.__name__ == "Detector"
    assert "Detector" in argus.detectors.base.__all__


# ---------------------------------------------------------------------------
# Story 18.4 — the Protocol is load-bearing (DF-AUD-DETECT-F item A).
#
# Both guards below decide by STRUCTURE (`ast`) or by static typing, never by
# `isinstance`/`issubclass` against a Protocol. That is not style: a
# `runtime_checkable` `isinstance` check was measured to answer `True` for a class
# whose `run` is the integer `42` on CPython 3.11, 3.12 AND 3.13, and to answer
# DIFFERENTLY between 3.11 and 3.12+ for a `__getattr__`-provided member (3.12
# switched from `hasattr` to `inspect.getattr_static`). CI runs 3.10/3.11/3.12, so a
# guard whose verdict is such an `isinstance` is not a guard (story 18.4 §0.3/§2.3).
# ---------------------------------------------------------------------------

_DETECTORS_DIR = pathlib.Path(argus.detectors.__file__).resolve().parent


def _module_trees() -> dict[str, ast.Module]:
    """Parse every module in ``argus/detectors/`` — the population both guards walk."""
    return {
        path.name: ast.parse(path.read_text(encoding="utf-8"))
        for path in sorted(_DETECTORS_DIR.glob("*.py"))
    }


def _is_protocol(node: ast.ClassDef) -> bool:
    """True when *node* declares ``Protocol`` among its bases (the contract, not a detector)."""
    return any(
        (isinstance(base, ast.Name) and base.id == "Protocol")
        or (isinstance(base, ast.Attribute) and base.attr == "Protocol")
        for base in node.bases
    )


def _detector_classes(trees: dict[str, ast.Module]) -> list[tuple[str, str]]:
    """Every NON-Protocol class defining ``run`` annotated ``-> DetectorResult``."""
    out: list[tuple[str, str]] = []
    for module_name, tree in trees.items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef) or _is_protocol(node):
                continue
            for member in node.body:
                if (
                    isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and member.name == "run"
                    and member.returns is not None
                    and ast.unparse(member.returns) == "DetectorResult"
                ):
                    out.append((module_name, node.name))
    return sorted(out)


def _pinned_classes(trees: dict[str, ast.Module]) -> set[tuple[str, str]]:
    """Every class bound to ``Detector`` by an annotated assignment under ``if TYPE_CHECKING:``.

    Only a pin inside an ``if TYPE_CHECKING:`` block counts: it must be checked by
    ``mypy argus`` (the blocking CI gate) and must cost nothing at import time.
    """
    pinned: set[tuple[str, str]] = set()
    for module_name, tree in trees.items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.If):
                continue
            test = node.test
            guarded = (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
                isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
            )
            if not guarded:
                continue
            for stmt in ast.walk(node):
                if (
                    isinstance(stmt, ast.AnnAssign)
                    and ast.unparse(stmt.annotation) == "Detector"
                    and isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Name)
                ):
                    pinned.add((module_name, stmt.value.func.id))
    return pinned


def test_TC_ArgusAgent_DETECT_001_145_every_detector_class_carries_a_static_conformance_pin() -> None:
    """TC-ArgusAgent-DETECT-001-145 — a detector class without a static pin fails the build.

    THE WITNESS of story 18.4: against the shipped tree this is RED at 4 classes / 0
    pins. It is what makes a FIFTH, unpinned detector impossible — the pin lives inside
    ``argus/`` so the blocking ``mypy argus`` gate checks it, and this guard is what
    stops the pin being omitted in the first place.
    """
    trees = _module_trees()
    classes = _detector_classes(trees)

    # AI-E11-1 — assert the population is non-empty BEFORE asserting an absence.
    # An empty walk would pass this guard forever.
    assert len(classes) >= 4, (
        f"the AST walk over {_DETECTORS_DIR.name}/ found only {len(classes)} class(es) defining "
        f"`run() -> DetectorResult` ({classes}); expected at least the four shipped detectors. "
        "A guard that asserts an absence over an empty population is vacuous."
    )

    pinned = _pinned_classes(trees)
    unpinned = [entry for entry in classes if entry not in pinned]
    assert not unpinned, (
        f"{len(classes)} detector class(es) define `run() -> DetectorResult` but "
        f"{len(unpinned)} carry NO static conformance pin against `Detector` in their own "
        f"module: {unpinned}. Add, at the end of the module:\n"
        "    if TYPE_CHECKING:\n"
        "        from argus.detectors.base import Detector\n"
        "        _CONFORMANCE_PIN: Detector = TheDetector()\n"
        "A pin written under `tests/` is enforced by NOTHING - there is no [tool.mypy] "
        "section in this repository and CI runs `mypy argus` only."
    )


def test_TC_ArgusAgent_DETECT_001_146_the_detector_protocol_keeps_its_measured_shape() -> None:
    """TC-ArgusAgent-DETECT-001-146 — FENCE (green before and after the behaviour it protects).

    DN-18-4-5: this is a CONTRACT PIN, not a caught defect. It is RED only against the
    SHIPPED Protocol *text*, and its job is to stop ``@runtime_checkable`` and the
    ``*args: object, **kwargs: object`` signature being reinstated by a future
    well-meaning edit. ``mypy`` REJECTS all four shipped detectors against that
    signature, so reinstating it would break the four pins ``-145`` requires.
    """
    # TYPE_CHECKING is False at runtime — the four pins therefore execute nothing and
    # construct no detector at import time (AC2.2). Asserted, never assumed.
    assert TYPE_CHECKING is False

    tree = ast.parse((_DETECTORS_DIR / "base.py").read_text(encoding="utf-8"))
    protocol = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name == "Detector"
    )

    decorators = [ast.unparse(d) for d in protocol.decorator_list]
    assert "runtime_checkable" not in decorators, (
        "`Detector` is decorated @runtime_checkable, which offers an `isinstance` check "
        "measured VACUOUS (a class whose `run` is the integer 42 passes it) and whose verdict "
        f"DIFFERS between CPython 3.11 and 3.12+. Decorators found: {decorators}."
    )

    methods = {
        member.name: member
        for member in protocol.body
        if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    data_members = sorted(
        member.target.id
        for member in protocol.body
        if isinstance(member, ast.AnnAssign) and isinstance(member.target, ast.Name)
    )
    assert data_members == [], (
        f"`Detector` declares data member(s) {data_members}. A non-method member makes "
        "`issubclass` raise TypeError and makes the member invariant; both members must be "
        "read-only properties (DN-18-4-2 — measured: the property spelling is the ONLY one "
        "all four shipped detectors satisfy)."
    )
    assert sorted(methods) == ["rule_id", "run"], (
        f"`Detector`'s members are {sorted(methods)}; expected exactly ['rule_id', 'run'] — "
        "the contract all four shipped detectors actually have."
    )

    for name, expected in (("rule_id", "str"), ("run", "Callable[..., DetectorResult]")):
        member = methods[name]
        found_decorators = [ast.unparse(d) for d in member.decorator_list]
        assert found_decorators == ["property"], (
            f"`Detector.{name}` must be a read-only @property (DN-18-4-2); found decorators "
            f"{found_decorators}."
        )
        declared = ast.unparse(member.returns) if member.returns is not None else None
        assert declared == expected, (
            f"`Detector.{name}` must be declared `-> {expected}`; found `-> {declared}`. The "
            "Protocol MUST NOT describe `run`'s parameters: `*args: object, **kwargs: object`, "
            "`**kwargs: Any` and a settable `run: Callable[...]` attribute were each measured to "
            "reject ALL FOUR shipped detectors under `mypy`."
        )

    # The purity sentence is CITED from another shipped module (`tool_runner.py` builds
    # Story 2.6's whole pure/impure argument on it). Dropping it would create a seventh
    # dangling reference (DF-INV-REFS-A).
    assert "MUST be pure" in (ast.get_docstring(protocol) or ""), (
        "the Protocol docstring's AR8 purity sentence is cited by "
        "`argus/detectors/tool_runner.py` and must survive (AC1.4)."
    )
