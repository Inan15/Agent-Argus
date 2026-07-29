"""Pure partition planner + work-manifest permission-boundary tests (Story 2.4).

Verification area ArgusAgent-INDEX (TC-ArgusAgent-INDEX-001-NN — continuing the 1.4 index
area). Drivers: ArgusAgent-FR-3 (bounded-unit graph-derived partitioning), ArgusAgent-NFR-SC1
(≤40 files/15k LOC soft; ≤60/25k hard; context_pressure auto-downgrade),
ArgusAgent-NFR-S4 (the work-manifest IS the read permission boundary — off-scope read
impossible), ArgusAgent-NFR-P1 (byte-identical plan; order-independent), ArgusAgent-NFR-D2
(pure / zero-token), AR4 (no float; content-derived ids), AR8 (pure/impure), AR10
(typed errors), AR11 (content-derived partition_id), AI-E1-1 (non-ASCII paths).

The pure planner / contract / is_in_scope tests build a SYNTHETIC AstIndex (no
parse, no FS) + an in-memory loc_by_file map; the read_in_scope test uses tmp_path.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from argus.index.ast_index import (
    AstIndex,
    AstIndexEntry,
    CodeEdge,
    Definition,
)
from argus.index.partitioner import (
    PARTITION_SCHEMA_VERSION,
    SEAM_ANALYSIS_MARKER,
    PartitionLimits,
    PartitionerError,
    PartitionScopeError,
    WorkManifest,
    build_plan_payload,
    compute_loc_by_file,
    is_in_scope,
    normalize_rel_path,
    partition_repository,
    read_in_scope,
)
from argus.store import canonical

_PARTITIONER_PY = (
    Path(__file__).resolve().parents[1]
    
    / "argus"
    / "index"
    / "partitioner.py"
)


# ── fixtures ────────────────────────────────────────────────────────────────


def _entry(
    file_path: str,
    *,
    defs: tuple[str, ...] = (),
    edges: tuple[str, ...] = (),
    ast_eligible: bool = True,
) -> AstIndexEntry:
    definitions = tuple(
        Definition(name=n, kind="function", start_line=1, end_line=2) for n in defs
    )
    code_edges = tuple(CodeEdge(callee=c, line=1) for c in edges)
    return AstIndexEntry(
        file_path=file_path,
        ast_eligible=ast_eligible,
        parse_failed=not ast_eligible,
        definitions=definitions,
        edges=code_edges,
    )


def _index(entries: tuple[AstIndexEntry, ...]) -> AstIndex:
    sorted_entries = tuple(sorted(entries, key=lambda e: e.file_path))
    return AstIndex(grammar_version="test", entries=sorted_entries)


def _uniform_loc(files: tuple[str, ...], loc: int) -> dict[str, int]:
    return {f: loc for f in files}


def _all_files(index: AstIndex) -> tuple[str, ...]:
    return tuple(sorted(e.file_path for e in index.entries))


# ── AC1 — bounded-unit graph-derived partitioning ────────────────────────────


def test_small_repo_stays_one_unit() -> None:
    """TC-ArgusAgent-INDEX-001-80 — a repo at/under one unit yields a single partition."""
    index = _index((_entry("a.py"), _entry("b.py"), _entry("c.py")))
    loc = _uniform_loc(_all_files(index), 100)
    plan = partition_repository(index, loc_by_file=loc)
    assert len(plan.partitions) == 1
    assert plan.partitions[0].work_manifest.files == ("a.py", "b.py", "c.py")
    assert plan.partitions[0].context_pressure is False


def test_oversized_by_file_count_splits_into_multiple_units() -> None:
    """TC-ArgusAgent-INDEX-001-81 — >40 files (no cohesion) split into >=2 bounded units."""
    entries = tuple(_entry(f"mod_{i:03d}.py") for i in range(95))
    index = _index(entries)
    loc = _uniform_loc(_all_files(index), 10)
    limits = PartitionLimits()
    plan = partition_repository(index, loc_by_file=loc, limits=limits)
    assert len(plan.partitions) >= 2
    for p in plan.partitions:
        assert p.file_count <= limits.hard_file_limit
        assert p.total_loc <= limits.hard_loc_limit


def test_oversized_by_loc_splits_into_multiple_units() -> None:
    """TC-ArgusAgent-INDEX-001-82 — total LOC over the soft target splits by LOC."""
    entries = tuple(_entry(f"big_{i:02d}.py") for i in range(10))
    index = _index(entries)
    loc = _uniform_loc(_all_files(index), 3_000)  # 30k total > 15k soft
    limits = PartitionLimits()
    plan = partition_repository(index, loc_by_file=loc, limits=limits)
    assert len(plan.partitions) >= 2
    for p in plan.partitions:
        assert p.total_loc <= limits.hard_loc_limit


def test_no_unit_exceeds_hard_ceiling() -> None:
    """TC-ArgusAgent-INDEX-001-83 — NO produced unit exceeds the hard ceiling."""
    entries = tuple(_entry(f"f_{i:03d}.py") for i in range(200))
    index = _index(entries)
    loc = _uniform_loc(_all_files(index), 500)
    limits = PartitionLimits()
    plan = partition_repository(index, loc_by_file=loc, limits=limits)
    for p in plan.partitions:
        assert p.file_count <= limits.hard_file_limit
        assert p.total_loc <= limits.hard_loc_limit


def test_context_pressure_flagged_on_near_ceiling_split() -> None:
    """TC-ArgusAgent-INDEX-001-84 — a split forced by nearing the ceiling is flagged."""
    entries = tuple(_entry(f"f_{i:03d}.py") for i in range(90))
    index = _index(entries)
    loc = _uniform_loc(_all_files(index), 10)
    plan = partition_repository(index, loc_by_file=loc)
    assert any(p.context_pressure for p in plan.partitions)


def test_single_oversized_file_is_its_own_pressured_unit() -> None:
    """TC-ArgusAgent-INDEX-001-85 — a single file > hard LOC limit is its own pressured unit."""
    index = _index((_entry("huge.py"), _entry("small.py")))
    loc = {"huge.py": 30_000, "small.py": 50}
    plan = partition_repository(index, loc_by_file=loc)
    huge = next(p for p in plan.partitions if "huge.py" in p.work_manifest.files)
    assert huge.work_manifest.files == ("huge.py",)
    assert huge.context_pressure is True
    assert huge.total_loc == 30_000


def test_graph_cohesion_groups_related_files() -> None:
    """TC-ArgusAgent-INDEX-001-86 — cohesion via edges (a calls helper defined in b)."""
    entries = (
        _entry("a.py", edges=("helper",)),
        _entry("b.py", defs=("helper",)),
        _entry("z.py"),  # unrelated, isolated
    )
    index = _index(entries)
    loc = {"a.py": 5_000, "b.py": 5_000, "z.py": 14_000}
    limits = PartitionLimits()
    plan = partition_repository(index, loc_by_file=loc, limits=limits)
    # a + b cohere (10k) and stay together; z (14k) cannot join without exceeding
    # 15k soft, so it lands in its own unit.
    a_unit = next(p for p in plan.partitions if "a.py" in p.work_manifest.files)
    assert "b.py" in a_unit.work_manifest.files


def test_ambiguous_callee_does_not_merge_under_merge_rule() -> None:
    """TC-ArgusAgent-INDEX-001-87 — DF-1-4-A: an ambiguous callee yields no cohesion edge."""
    entries = (
        _entry("caller.py", edges=("dup",)),
        _entry("one.py", defs=("dup",)),
        _entry("two.py", defs=("dup",)),
    )
    index = _index(entries)
    # Force a small soft limit so a spurious merge would be observable.
    loc = _uniform_loc(_all_files(index), 100)
    limits = PartitionLimits(soft_file_limit=1, soft_loc_limit=200)
    plan = partition_repository(index, loc_by_file=loc, limits=limits)
    # 'dup' defined in two files → ambiguous → dropped → no merge edge. Each file
    # is its own component → with soft_file_limit=1 each is its own unit.
    assert len(plan.partitions) == 3


def test_non_eligible_file_is_still_placed() -> None:
    """TC-ArgusAgent-INDEX-001-88 — a parse_failed/non-eligible file is still in a partition."""
    entries = (_entry("ok.py"), _entry("broken.py", ast_eligible=False))
    index = _index(entries)
    loc = _uniform_loc(_all_files(index), 10)
    plan = partition_repository(index, loc_by_file=loc)
    placed = {f for p in plan.partitions for f in p.work_manifest.files}
    assert placed == {"ok.py", "broken.py"}


def test_empty_index_yields_empty_plan() -> None:
    index = _index(())
    plan = partition_repository(index, loc_by_file={})
    assert plan.partitions == ()
    assert plan.seam_analysis == SEAM_ANALYSIS_MARKER


# ── AC2 — content-derived stable id + determinism + total-and-disjoint ────────


def test_partition_id_is_sha256_over_sorted_members() -> None:
    """TC-ArgusAgent-INDEX-001-89 — partition_id is a deterministic sha256 (never a counter)."""
    import hashlib

    index = _index((_entry("b.py"), _entry("a.py")))
    loc = _uniform_loc(_all_files(index), 10)
    plan = partition_repository(index, loc_by_file=loc)
    pid = plan.partitions[0].partition_id
    expected = hashlib.sha256("a.py\nb.py".encode("utf-8")).hexdigest()
    assert pid == expected
    assert len(pid) == 64


def test_plan_is_byte_stable_and_order_independent() -> None:
    """TC-ArgusAgent-INDEX-001-90 — two input orderings → byte-identical PartitionPlan."""
    entries = tuple(
        _entry(f"m_{i:02d}.py", edges=("shared",) if i % 2 == 0 else ())
        for i in range(50)
    ) + (_entry("shared_mod.py", defs=("shared",)),)
    files = tuple(sorted(e.file_path for e in entries))
    loc = _uniform_loc(files, 200)

    idx1 = _index(entries)
    idx2 = _index(tuple(reversed(entries)))
    p1 = partition_repository(idx1, loc_by_file=loc)
    p2 = partition_repository(idx2, loc_by_file=loc)

    b1 = canonical.dumps_bytes(build_plan_payload(p1))
    b2 = canonical.dumps_bytes(build_plan_payload(p2))
    assert b1 == b2
    assert p1 == p2


def test_partition_of_the_set_is_total_and_disjoint() -> None:
    """TC-ArgusAgent-INDEX-001-91 — every file in EXACTLY one partition (no drop/dup)."""
    entries = tuple(_entry(f"file_{i:03d}.py") for i in range(120))
    index = _index(entries)
    expected = set(_all_files(index))
    loc = _uniform_loc(tuple(expected), 100)
    plan = partition_repository(index, loc_by_file=loc)

    seen: list[str] = []
    for p in plan.partitions:
        seen.extend(p.work_manifest.files)
    assert sorted(seen) == sorted(expected)  # total
    assert len(seen) == len(set(seen))  # disjoint


def test_partitions_sorted_by_partition_id() -> None:
    entries = tuple(_entry(f"f_{i:03d}.py") for i in range(90))
    index = _index(entries)
    loc = _uniform_loc(_all_files(index), 10)
    plan = partition_repository(index, loc_by_file=loc)
    ids = [p.partition_id for p in plan.partitions]
    assert ids == sorted(ids)


# ── AC3 — the permission boundary (off-scope read impossible) ─────────────────


def _manifest(*files: str) -> WorkManifest:
    return WorkManifest(files=tuple(sorted(files)))


def test_is_in_scope_exact_membership_pass() -> None:
    """TC-ArgusAgent-INDEX-001-92 — an exact member is in scope."""
    m = _manifest("auth/secrets.py", "core/util.py")
    assert is_in_scope(m, "auth/secrets.py") is True


def test_is_in_scope_sibling_prefix_rejected() -> None:
    """TC-ArgusAgent-INDEX-001-93 — a sibling-prefix path is NOT a prefix match (the 1.3 rigor)."""
    m = _manifest("auth/secrets.py")
    assert is_in_scope(m, "auth/secrets_extra.py") is False
    assert is_in_scope(m, "auth/secrets") is False
    assert is_in_scope(m, "auth") is False


def test_is_in_scope_traversal_rejected() -> None:
    """TC-ArgusAgent-INDEX-001-94 — a ../ traversal is out of scope."""
    m = _manifest("auth/secrets.py")
    assert is_in_scope(m, "../other_unit/x.py") is False


def test_is_in_scope_normalizes_dot_slash_and_backslash() -> None:
    """TC-ArgusAgent-INDEX-001-95 — ./ and backslash variants normalize to the member."""
    m = _manifest("auth/secrets.py")
    assert is_in_scope(m, "./auth/secrets.py") is True
    assert is_in_scope(m, "auth\\secrets.py") is True


def test_read_in_scope_reads_member_and_refuses_off_scope(tmp_path: Path) -> None:
    """TC-ArgusAgent-INDEX-001-96 — read_in_scope reads in-scope; off-scope raises (NFR-S4)."""
    (tmp_path / "auth").mkdir()
    (tmp_path / "auth" / "secrets.py").write_text("SECRET = 1\n", encoding="utf-8")
    (tmp_path / "auth" / "secrets_extra.py").write_text("LEAK = 2\n", encoding="utf-8")
    m = _manifest("auth/secrets.py")

    assert read_in_scope(tmp_path, m, "auth/secrets.py") == "SECRET = 1\n"
    with pytest.raises(PartitionScopeError):
        read_in_scope(tmp_path, m, "auth/secrets_extra.py")
    with pytest.raises(PartitionScopeError):
        read_in_scope(tmp_path, m, "../escape.py")


def test_is_in_scope_rejects_non_manifest() -> None:
    with pytest.raises(PartitionerError):
        is_in_scope("not-a-manifest", "a.py")  # type: ignore[arg-type]


# ── AC5 — V1 no-seam-analysis provenance + recorded-not-analyzed cut edges ────


def test_plan_records_seam_analysis_v2_deferred() -> None:
    """TC-ArgusAgent-INDEX-001-97 — the plan carries the honest V1 limitation marker."""
    index = _index((_entry("a.py"),))
    plan = partition_repository(index, loc_by_file={"a.py": 10})
    assert plan.seam_analysis == "v2-deferred"


def test_cut_edges_recorded_not_analyzed() -> None:
    """TC-ArgusAgent-INDEX-001-98 — a cohesion edge crossing a cut is recorded as a CutEdge."""
    # caller calls helper defined in callee; force them into separate units via a
    # soft_file_limit of 1 so the cohesion edge becomes a CUT edge.
    entries = (
        _entry("caller.py", edges=("helper",)),
        _entry("callee.py", defs=("helper",)),
    )
    index = _index(entries)
    loc = _uniform_loc(_all_files(index), 100)
    limits = PartitionLimits(soft_file_limit=1, soft_loc_limit=200)
    plan = partition_repository(index, loc_by_file=loc, limits=limits)
    # With soft_file_limit=1 the cohering pair is packed one-file-per-unit, so the
    # edge crosses a partition boundary and is recorded.
    assert len(plan.partitions) == 2
    assert any(
        ce.caller_file == "caller.py" and ce.callee_file == "callee.py" and ce.callee == "helper"
        for ce in plan.cut_edges
    )


# ── AC6 — purity / frozen / no-float / typed-error / single serializer ────────


def test_models_are_frozen_and_forbid_extra() -> None:
    """TC-ArgusAgent-INDEX-001-99 — frozen + extra='forbid' (NFR-M2)."""
    m = _manifest("a.py")
    with pytest.raises(Exception):
        m.files = ("b.py",)  # type: ignore[misc]
    with pytest.raises(Exception):
        WorkManifest(files=("a.py",), unexpected="x")  # type: ignore[call-arg]
    with pytest.raises(Exception):
        PartitionLimits(unexpected=1)  # type: ignore[call-arg]


def test_schema_version_localized() -> None:
    m = _manifest("a.py")
    assert m.schema_version == PARTITION_SCHEMA_VERSION


def test_no_float_in_plan_payload() -> None:
    """TC-ArgusAgent-INDEX-001-100 — the plan payload carries no float (canonical rejects it)."""
    index = _index((_entry("a.py", edges=("g",)), _entry("b.py", defs=("g",))))
    loc = {"a.py": 100, "b.py": 200}
    plan = partition_repository(index, loc_by_file=loc)
    # build_plan_payload routes through the single canonical serializer, which
    # raises on any float leaf — so a clean dumps proves no-float.
    canonical.dumps_bytes(build_plan_payload(plan))
    payload = build_plan_payload(plan)
    for p in payload["partitions"]:
        assert isinstance(p["file_count"], int)
        assert isinstance(p["total_loc"], int)
        assert isinstance(p["context_pressure"], bool)


def test_malformed_inputs_raise_partitioner_error() -> None:
    """TC-ArgusAgent-INDEX-001-101 — typed errors on malformed input (AR10)."""
    index = _index((_entry("a.py"),))
    with pytest.raises(PartitionerError):
        partition_repository("not-an-index", loc_by_file={})  # type: ignore[arg-type]
    with pytest.raises(PartitionerError):
        partition_repository(index, loc_by_file={})  # missing a.py
    with pytest.raises(PartitionerError):
        partition_repository(index, loc_by_file={"a.py": -1})  # negative LOC
    with pytest.raises(PartitionerError):
        partition_repository(index, loc_by_file={"a.py": True})  # bool not int
    with pytest.raises(PartitionerError):
        partition_repository(index, loc_by_file={"a.py": "10"})  # type: ignore[dict-item]


def test_invalid_limits_raise() -> None:
    index = _index((_entry("a.py"),))
    bad = PartitionLimits(soft_file_limit=50, hard_file_limit=40)
    with pytest.raises(PartitionerError):
        partition_repository(index, loc_by_file={"a.py": 10}, limits=bad)


def test_compute_loc_by_file_counts_lines() -> None:
    out = compute_loc_by_file({"a.py": "x\ny\nz\n", "b.py": "one line", "c.py": ""})
    assert out == {"a.py": 3, "b.py": 1, "c.py": 0}
    with pytest.raises(PartitionerError):
        compute_loc_by_file({"a.py": 5})  # type: ignore[dict-item]


def test_normalize_rel_path_rejects_absolute_and_traversal() -> None:
    assert normalize_rel_path("./a/b.py") == "a/b.py"
    assert normalize_rel_path("a\\b.py") == "a/b.py"
    with pytest.raises(PartitionScopeError):
        normalize_rel_path("/abs/x.py")
    with pytest.raises(PartitionScopeError):
        normalize_rel_path("a/../b.py")
    with pytest.raises(PartitionScopeError):
        normalize_rel_path("C:/win/x.py")
    with pytest.raises(PartitionerError):
        normalize_rel_path(123)  # type: ignore[arg-type]


def test_partitioner_module_is_pure_no_io_clock_uuid() -> None:
    """TC-ArgusAgent-INDEX-001-102 — AST scan: the pure module has no I/O/clock/uuid/random.

    Scans the PURE planner functions (not the clearly-marked impure shell
    read_in_scope, which legitimately reads a file). The whole module must not
    import datetime/time/uuid/random or call open().
    """
    src = _PARTITIONER_PY.read_text(encoding="utf-8")
    tree = ast.parse(src)
    forbidden_modules = {"datetime", "time", "uuid", "random", "os"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden_modules, alias.name
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_modules, node.module
    # The pure planner functions must not call open() or read a clock. read_in_scope
    # is the documented impure shell that reads a file via Path.read_text — allowed.
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id != "open", "open() forbidden in the partitioner"


# ── AI-E1-1 — non-ASCII path fixtures (Epic-1 retro carry-forward) ────────────


def test_non_ascii_path_placed_intact_and_scoped() -> None:
    """TC-ArgusAgent-INDEX-001-103 — a non-ASCII path is placed intact + scope-correct."""
    entries = (
        _entry("auth/café_guard.py"),
        _entry("модуль/безопасность.py"),
        _entry("core/util.py"),
    )
    index = _index(entries)
    files = _all_files(index)
    loc = _uniform_loc(files, 50)
    plan = partition_repository(index, loc_by_file=loc)

    placed = {f for p in plan.partitions for f in p.work_manifest.files}
    assert "auth/café_guard.py" in placed
    assert "модуль/безопасность.py" in placed

    # Round-trips intact through the canonical serializer (no mojibake / drop).
    payload = build_plan_payload(plan)
    reloaded = canonical.loads(canonical.dumps_bytes(payload))
    reloaded_files = {
        f for part in reloaded["partitions"] for f in part["work_manifest"]["files"]
    }
    assert "auth/café_guard.py" in reloaded_files
    assert "модуль/безопасность.py" in reloaded_files


def test_non_ascii_in_scope_and_cross_manifest_rejected() -> None:
    """TC-ArgusAgent-INDEX-001-104 — a non-ASCII path is in-scope for its own manifest only."""
    own = _manifest("auth/café_guard.py")
    other = _manifest("core/util.py")
    assert is_in_scope(own, "auth/café_guard.py") is True
    assert is_in_scope(other, "auth/café_guard.py") is False
    # a different non-ASCII sibling-prefix is still rejected.
    assert is_in_scope(own, "auth/café_guard_extra.py") is False
