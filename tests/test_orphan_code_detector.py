"""Orphan / dead-code detector — the conservative name-reachability detector (Story 6.3).

Verification area ArgusAgent-ORPHAN (``TC-ArgusAgent-ORPHAN-001-NN``, indexed from ``-01``).
Drivers: ArgusAgent-FR-12 (detect orphan / dead code — a function/class with no
referencing requirement or caller, each with a verifiable locator), ArgusAgent-FR-13
(every finding carries ≥1 verifiable locator via the EXISTING ``build_recording``),
ArgusAgent-AR10 / NFR-R1 (a malformed / empty / None index / a None-named definition → a
recorded ``DegradedCondition`` or NOT-orphan, NEVER an uncaught raise), DF-1-4-A
(the 1.4 edge set is UNRESOLVED-NAME only → the detection rule is CONSERVATIVE: a
name-collision / ambiguity → NOT-orphan, NEVER a false dead-code accusation).

This module enumerates the COMPLETE DECLARED SET of ``(definition, edge-graph)``
shapes the detector must classify (the complete-the-declared-set discipline that
caught 3.4 / 4.2 / 5.1 / the 6.2 construct set), each demonstrated explicitly:

  (a) a referenced def (name appears as an edge callee) → NOT-orphan
  (b) an unreferenced, non-excluded def → an ADVISORY orphan finding (FR12 happy path)
  (c) a dunder / ``__init__`` / ``__all__`` / ``test_*`` / framework-hook entrypoint
      with no caller → EXCLUDED → NOT-orphan (the conservative exclusion)
  (d) a NAME-COLLISION (two defs share a name, one is referenced) → BOTH NOT-orphan
      (the DF-1-4-A unresolved-name guard — RED against a naive per-def check)
  (e) a non-Python / parse-failed / ``ast_eligible=False`` entry → no finding, no crash
  (f) a malformed / empty / None index / a None-named definition → a recorded
      ``DegradedCondition`` or NOT-orphan, NEVER an uncaught raise (the no-crash leg)
  (g) a non-ASCII ``Definition.name`` / non-ASCII path → classifies + builds a finding
      + derives a stable ``recording_id`` under ``PYTHONIOENCODING=utf-8`` (AI-E1-1)
"""

from __future__ import annotations

import pytest

from argus.detectors.base import DetectorResult
from argus.detectors.orphan_code import (
    RULE_ORPHAN_CODE,
    OrphanCodeDetector,
    OrphanCodeError,
)
from argus.index.ast_index import (
    AstIndex,
    AstIndexEntry,
    CodeEdge,
    Definition,
)
from argus.ledger.recording import Recording


def _defn(name: str, *, kind: str = "function", start: int = 1, end: int = 2) -> Definition:
    return Definition(name=name, kind=kind, start_line=start, end_line=end)


def _entry(
    file_path: str,
    *,
    definitions: tuple[Definition, ...] = (),
    edges: tuple[CodeEdge, ...] = (),
    ast_eligible: bool = True,
    parse_failed: bool = False,
    parse_failure_reason: str | None = None,
) -> AstIndexEntry:
    return AstIndexEntry(
        file_path=file_path,
        ast_eligible=ast_eligible,
        parse_failed=parse_failed,
        parse_failure_reason=parse_failure_reason,
        definitions=definitions,
        edges=edges,
    )


def _index(*entries: AstIndexEntry) -> AstIndex:
    return AstIndex(grammar_version="test", entries=tuple(entries))


def _run(index: AstIndex) -> DetectorResult:
    return OrphanCodeDetector().run(index=index)


# ── (a) referenced def → NOT-orphan ─────────────────────────────────────────


def test_referenced_definition_is_not_orphan() -> None:
    """TC-ArgusAgent-ORPHAN-001-01 — a def whose name is an edge callee is NOT an orphan."""
    index = _index(
        _entry("pkg/lib.py", definitions=(_defn("widget"),)),
        _entry("pkg/app.py", edges=(CodeEdge(callee="widget", line=3),)),
    )
    result = _run(index)
    assert result.findings == ()
    assert result.degraded == ()


# ── (b) unreferenced, non-excluded def → an advisory orphan finding ──────────


def test_unreferenced_definition_is_an_advisory_orphan_finding() -> None:
    """TC-ArgusAgent-ORPHAN-001-02 — the FR12 happy path: an orphan advisory finding w/ a locator."""
    index = _index(
        _entry("pkg/dead.py", definitions=(_defn("orphan_fn", start=10, end=14),)),
        _entry("pkg/app.py", edges=(CodeEdge(callee="something_else", line=2),)),
    )
    result = _run(index)
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert isinstance(finding, Recording)
    assert finding.rule_id == RULE_ORPHAN_CODE
    # advisory-by-contract (CC #6) — cannot alone move the verdict to 🔴.
    assert finding.advisory is True
    assert finding.depth_supported is None
    # FR13: exactly one verifiable locator built from the def's file + span + ast_span.
    assert len(finding.locators) == 1
    loc = finding.locators[0]
    assert loc.file_path == "pkg/dead.py"
    assert loc.start_line == 10
    assert loc.end_line == 14
    assert loc.ast_span == "function:orphan_fn@10-14"
    assert finding.recording_id.startswith(RULE_ORPHAN_CODE + ":")
    # finding-only detector: NO coverage entry (the 2.5 additive pattern).
    assert result.entries == ()


def test_unreferenced_class_is_an_orphan() -> None:
    """TC-ArgusAgent-ORPHAN-001-03 — a class def with no name-match caller is an orphan."""
    index = _index(
        _entry("pkg/dead.py", definitions=(_defn("DeadClass", kind="class", start=1, end=8),)),
    )
    result = _run(index)
    assert len(result.findings) == 1
    assert result.findings[0].locators[0].ast_span == "class:DeadClass@1-8"


# ── (c) excluded entrypoints → NOT-orphan even with no caller ────────────────


@pytest.mark.parametrize(
    "name,kind",
    [
        ("__init__", "function"),
        ("__call__", "function"),
        ("__enter__", "function"),
        ("test_widget", "function"),
        ("test", "function"),
        ("setUp", "function"),
        ("tearDown", "function"),
        ("main", "function"),
        ("lambda_handler", "function"),
        ("pytest_configure", "function"),
    ],
)
def test_excluded_entrypoints_are_never_orphans(name: str, kind: str) -> None:
    """TC-ArgusAgent-ORPHAN-001-04 — dunder / test / framework hooks are NOT-orphan (conservative)."""
    index = _index(_entry("pkg/m.py", definitions=(_defn(name, kind=kind),)))
    result = _run(index)
    assert result.findings == (), f"{name} should be excluded, not flagged"


# ── (d) name-collision → BOTH NOT-orphan (the DF-1-4-A unresolved-name guard) ─


def test_name_collision_makes_both_definitions_not_orphan() -> None:
    """TC-ArgusAgent-ORPHAN-001-05 — two defs share a name, one is referenced → BOTH NOT-orphan.

    RED against a naive per-def check that would false-flag the uncalled twin: the
    UNRESOLVED-name graph cannot tell which def a callee resolves to, so neither may
    be accused (the conservative ambiguity rule / DF-1-4-A). This is the keystone
    no-false-accusation guard.
    """
    index = _index(
        _entry("pkg/a.py", definitions=(_defn("process", start=1, end=3),)),
        _entry("pkg/b.py", definitions=(_defn("process", start=5, end=9),)),
        # Only ONE call site; the unresolved graph can't say which 'process' it hits.
        _entry("pkg/app.py", edges=(CodeEdge(callee="process", line=2),)),
    )
    result = _run(index)
    assert result.findings == (), "a referenced name-collision twin must not be flagged"


def test_unreferenced_name_collision_is_still_not_orphan() -> None:
    """TC-ArgusAgent-ORPHAN-001-06 — two same-named defs, NEITHER referenced → BOTH NOT-orphan.

    Even with no caller, a shared name is ambiguous on the unresolved substrate, so
    the conservative rule stays silent (when in doubt → NOT-orphan). A resolved graph
    might flag one; V1 does not (low recall, high precision — the documented limit).
    """
    index = _index(
        _entry("pkg/a.py", definitions=(_defn("shared", start=1, end=2),)),
        _entry("pkg/b.py", definitions=(_defn("shared", start=4, end=6),)),
    )
    result = _run(index)
    assert result.findings == ()


# ── (e) non-Python / parse-failed entries → no finding, no crash ─────────────


def test_non_python_and_parse_failed_entries_yield_no_finding() -> None:
    """TC-ArgusAgent-ORPHAN-001-07 — ineligible entries carry no defs → no finding, no crash."""
    index = _index(
        _entry("README.md", ast_eligible=False, parse_failure_reason="non_python"),
        _entry(
            "pkg/broken.py",
            ast_eligible=False,
            parse_failed=True,
            parse_failure_reason="syntax_error",
        ),
    )
    result = _run(index)
    assert result.findings == ()
    assert result.degraded == ()


def test_empty_index_yields_empty_result() -> None:
    """TC-ArgusAgent-ORPHAN-001-08 — an empty index (no entries) → an empty result, no crash."""
    result = _run(_index())
    assert result == DetectorResult()


def test_entry_with_empty_definitions_and_edges() -> None:
    """TC-ArgusAgent-ORPHAN-001-09 — an eligible entry with no defs/edges → no finding."""
    result = _run(_index(_entry("pkg/empty.py")))
    assert result.findings == ()


# ── (f) no-crash leg: a None-named definition / malformed index ──────────────


def test_none_index_raises_typed_error_not_uncaught() -> None:
    """TC-ArgusAgent-ORPHAN-001-10 — a non-AstIndex argument raises a TYPED OrphanCodeError (AR10)."""
    with pytest.raises(OrphanCodeError):
        OrphanCodeDetector().run(index=None)  # type: ignore[arg-type]
    with pytest.raises(OrphanCodeError):
        OrphanCodeDetector().run(index="not-an-index")  # type: ignore[arg-type]


def test_definition_with_empty_name_is_degraded_not_crashed() -> None:
    """TC-ArgusAgent-ORPHAN-001-11 — a None/empty-named definition → recorded degraded, NOT-orphan, no crash.

    A ``Definition`` constructed via ``model_construct`` to bypass validation (the
    1.4 builder never mints an empty name, but the detector must NEVER raise on a
    degraded shape — AR10). The unnameable def is recorded + treated as NOT-orphan.
    """
    bad_def = Definition.model_construct(name="", kind="function", start_line=1, end_line=2)
    entry = AstIndexEntry.model_construct(
        file_path="pkg/weird.py",
        ast_eligible=True,
        parse_failed=False,
        parse_failure_reason=None,
        definitions=(bad_def,),
        edges=(),
    )
    index = AstIndex.model_construct(
        schema_version="1", partition_id="root", grammar_version="test", entries=(entry,)
    )
    result = OrphanCodeDetector().run(index=index)
    # No false orphan accusation on the unnameable def; the condition is recorded.
    assert result.findings == ()
    assert any(d.reason == "orphan_unnamed_definition" for d in result.degraded)


def test_malformed_entry_shape_is_degraded_not_crashed() -> None:
    """TC-ArgusAgent-ORPHAN-001-12 — a non-AstIndexEntry in entries → recorded degraded, no crash."""
    index = AstIndex.model_construct(
        schema_version="1",
        partition_id="root",
        grammar_version="test",
        entries=("not-an-entry",),  # type: ignore[arg-type]
    )
    result = OrphanCodeDetector().run(index=index)
    assert result.findings == ()
    assert any(d.reason == "orphan_malformed_entry" for d in result.degraded)


# ── (g) non-ASCII identifier / path → classifies, builds finding, stable id ──


def test_non_ascii_definition_name_is_classified_and_serialized() -> None:
    """TC-ArgusAgent-ORPHAN-001-13 — a non-ASCII def name + path → orphan finding + stable id (AI-E1-1)."""
    index = _index(
        _entry(
            "paquete/módulo.py",
            definitions=(_defn("función_huérfana", start=2, end=4),),
        ),
    )
    result = _run(index)
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.locators[0].file_path == "paquete/módulo.py"
    assert finding.locators[0].ast_span == "function:función_huérfana@2-4"
    # Stable content-derived id (AR4) — recompute is byte-identical.
    again = _run(index)
    assert again.findings[0].recording_id == finding.recording_id


def test_non_ascii_name_referenced_is_not_orphan() -> None:
    """TC-ArgusAgent-ORPHAN-001-14 — a referenced non-ASCII name is NOT-orphan (name-match over unicode)."""
    index = _index(
        _entry("paquete/m.py", definitions=(_defn("función_ñ"),)),
        _entry("paquete/app.py", edges=(CodeEdge(callee="función_ñ", line=1),)),
    )
    assert _run(index).findings == ()


# ── determinism / purity / ordering (AC6) ────────────────────────────────────


def test_findings_are_sorted_deterministically() -> None:
    """TC-ArgusAgent-ORPHAN-001-15 — findings sorted by (file_path, start_line, ...) — AR11."""
    index = _index(
        _entry(
            "pkg/z.py",
            definitions=(_defn("z_two", start=20, end=21), _defn("z_one", start=1, end=2)),
        ),
        _entry("pkg/a.py", definitions=(_defn("a_fn", start=5, end=6),)),
    )
    result = _run(index)
    keys = [(f.locators[0].file_path, f.locators[0].start_line) for f in result.findings]
    assert keys == sorted(keys)
    assert keys[0][0] == "pkg/a.py"


def test_repeated_runs_are_byte_identical() -> None:
    """TC-ArgusAgent-ORPHAN-001-16 — the detector is a pure deterministic fold (NFR-D2)."""
    index = _index(
        _entry("pkg/a.py", definitions=(_defn("dead_a"),)),
        _entry("pkg/b.py", definitions=(_defn("dead_b"),)),
    )
    first = _run(index)
    second = _run(index)
    assert [f.recording_id for f in first.findings] == [f.recording_id for f in second.findings]


def test_detector_satisfies_protocol_rule_id() -> None:
    """TC-ArgusAgent-ORPHAN-001-17 — the detector exposes the rule_id the Protocol requires."""
    assert OrphanCodeDetector.rule_id == RULE_ORPHAN_CODE == "orphan_code"
