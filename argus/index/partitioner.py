"""PURE graph-derived repository partitioner + work-manifest permission boundary.

Drivers: ArgusAgent-FR-3 (partition the repository into bounded audit units within a
declared budget — in V1 the "declared budget" is the FILES+LOC scale envelope,
NOT a $-budget; FR21/FR22 cost accounting is Epic 3), ArgusAgent-NFR-SC1 (V1 audit
units ≤40 files / 15k LOC soft target; hard ceiling ≤60 / 25k; larger repos
partition; full 10k→500k LOC scaling is V2), ArgusAgent-NFR-S4 (an auditor reads ONLY
the files in its work-manifest — the work_manifest IS the read PERMISSION
BOUNDARY; an off-scope read is impossible through the manifest-scoped primitive),
ArgusAgent-NFR-S5 (manifest persistence is containment-checked via the 1.3 store shell —
``is_relative_to``, never ``str.startswith``), ArgusAgent-NFR-P1 (byte-identical
partition plan + manifests across hosts/runs for the same repo@commit; two input
orderings of the same files yield the identical plan), ArgusAgent-NFR-D2 (deterministic,
zero-LLM-token — a pure fold over the recorded 1.4 index + the in-memory LOC map),
ArgusAgent-NFR-M2 (frozen, additive-only contracts), AR4 (no ``float``; ``int``/``str``/
``bool`` only; single canonical serializer; content-derived ids — never arrival
order), AR8 (pure/impure separation — the planner + the contract + ``is_in_scope``
are PURE; the per-file LOC READ, the manifest WRITE, and the manifest-scoped READ
are the impure shell), AR10 (typed failure — ``PartitionerError`` /
``PartitionScopeError`` ValueError subclasses, never a silent coerce / bare
``except`` / ``print`` in library code), AR11 (``partition_id`` is a sha256 over
the SORTED member paths — the ``assignments/<partition_id>.json`` filename — never
``uuid4`` / a counter / arrival order).

Graph-derived, not directory-derived (architecture Decision B)
--------------------------------------------------------------
Partitioning uses the 1.4 import/call graph, NOT folder layout. Nodes are files;
cohesion edges come from ``AstIndexEntry.edges`` (call/reference) resolved to a
DEFINING file via a ``Definition.name -> file`` map built from the index. Honor
the locked V1 edge limitation (DF-1-4-A): ``CodeEdge.callee`` is an UNRESOLVED
bare name with no scope binding, so the name→file map is best-effort — a callee
name that resolves to ZERO or MORE-THAN-ONE defining file yields NO cohesion edge.
The conservative direction is to UNDER-merge (keep weakly-coupled files in
separate small units) rather than over-merge into an oversized unit. A full
resolved call graph is Epic-6 depth — NOT built here.

The work-manifest IS the permission boundary (NFR-S4)
-----------------------------------------------------
A manifest is a CLOSED ALLOW-SET. ``is_in_scope(manifest, rel_path)`` is EXACT
normalized-path membership — NEVER a ``str.startswith`` / prefix / substring check
(the 1.3 lesson: a sibling-prefix ``auth/secrets_extra.py`` vs ``auth/secrets.py``
must NOT pass; the 18-2 Minions ``is_relative_to``-not-``startswith`` precedent).
Paths are POSIX-normalized (strip a leading ``./``, reject ``..`` traversal and
absolute paths) before comparison so a normalization gap is not an off-scope-read
escape. The impure ``read_in_scope`` reads ONLY on a scope pass and raises
``PartitionScopeError`` otherwise — an off-scope read is IMPOSSIBLE through the
primitive (not a policy a caller may opt out of).

The V1 honest limitation — NO cross-partition seam analysis (OI2, cross-cutting #4)
-----------------------------------------------------------------------------------
V1 does MULTI-UNIT auditing, NOT cross-partition SEAM analysis. A defect spanning
a cut (caller in unit A, callee in unit B) is NOT analyzed by any seam auditor in
this story. The plan provenance records ``seam_analysis="v2-deferred"`` + the
cut-edge set (recorded, NOT analyzed). The Story 6.4 ``cross_partition`` Prosecutor
cut-edge pass is the V1 MITIGATION (Tier-B / Epic 6 — re-reads cut edges); the
full seam auditor is reserved V2. ``partition_id`` becomes a REAL per-unit
content-derived id here (it stops always being ``"root"``), but the frozen 1.2
ledger/recording/verdict models are NOT re-shaped — this story SUPPLIES real id
values via the plan; the ledger/verdict core stays partition-agnostic.

Pure/impure separation (master rule, AR8)
-----------------------------------------
PURE (this module's planner core): ``partition_repository`` + the frozen
``Partition``/``PartitionPlan``/``WorkManifest`` contract + ``is_in_scope`` over
in-memory inputs — it never opens a file, reads a clock, mints a uuid, or calls
the parser. IMPURE shell: ``compute_loc_by_file`` (line count over an already-read
source map), ``read_in_scope`` (the manifest-scoped read), and the manifest
``write_assignment`` persistence (the pipeline). The impure helpers live in a
clearly-marked section below.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from argus.index.ast_index import AstIndex

__all__ = [
    "PARTITION_SCHEMA_VERSION",
    "DEFAULT_SOFT_FILE_LIMIT",
    "DEFAULT_SOFT_LOC_LIMIT",
    "DEFAULT_HARD_FILE_LIMIT",
    "DEFAULT_HARD_LOC_LIMIT",
    "SEAM_ANALYSIS_MARKER",
    "PartitionerError",
    "PartitionScopeError",
    "PartitionLimits",
    "WorkManifest",
    "Partition",
    "CutEdge",
    "PartitionPlan",
    "normalize_rel_path",
    "is_in_scope",
    "partition_repository",
    "build_plan_payload",
    "compute_loc_by_file",
    "read_in_scope",
]

# Localized schema version for the partition contracts (additive-only, NFR-M2).
PARTITION_SCHEMA_VERSION = "1"

# NFR-SC1 scale envelope: soft V1 target vs hard ceiling.
DEFAULT_SOFT_FILE_LIMIT = 40
DEFAULT_SOFT_LOC_LIMIT = 15_000
DEFAULT_HARD_FILE_LIMIT = 60
DEFAULT_HARD_LOC_LIMIT = 25_000

# The honest V1 limitation marker recorded on every plan (OI2 / cross-cutting #4).
SEAM_ANALYSIS_MARKER = "v2-deferred"


class PartitionerError(ValueError):
    """A TYPED partitioner / contract failure (AR10).

    A ``ValueError`` subclass localized to this module (mirroring
    ``RepoIntakeError`` / ``DepthSemanticsError`` / ``CriticalSubsystemError`` /
    ``CoverageReportError`` / ``PipelineError``). Raised on a malformed planner
    input (a non-``AstIndex`` argument, a non-``int`` LOC value, a negative limit,
    a missing/extra LOC entry, a non-``str`` path) — never a silent coerce.
    """


class PartitionScopeError(PartitionerError):
    """An off-scope read attempt through the manifest-scoped primitive (NFR-S4).

    The typed failure that makes an off-scope read IMPOSSIBLE: ``read_in_scope``
    raises this when a requested path is not an EXACT member of the manifest's
    closed allow-set — never a silent empty read / fabricated content.
    """


class PartitionLimits(BaseModel):
    """Frozen NFR-SC1 scale-envelope limits (the planner budget; files + LOC).

    ``soft_*`` are the V1 target a unit is greedily filled to; ``hard_*`` are the
    ceiling NO produced unit may exceed (a near-ceiling fill is split + flagged
    ``context_pressure``). All ``int`` (no ``float``, AR4); each ``hard_* >=
    soft_* >= 1``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    soft_file_limit: int = Field(default=DEFAULT_SOFT_FILE_LIMIT, ge=1)
    soft_loc_limit: int = Field(default=DEFAULT_SOFT_LOC_LIMIT, ge=1)
    hard_file_limit: int = Field(default=DEFAULT_HARD_FILE_LIMIT, ge=1)
    hard_loc_limit: int = Field(default=DEFAULT_HARD_LOC_LIMIT, ge=1)

    def _validate(self) -> None:
        if self.hard_file_limit < self.soft_file_limit:
            raise PartitionerError(
                "hard_file_limit must be >= soft_file_limit "
                f"({self.hard_file_limit} < {self.soft_file_limit})"
            )
        if self.hard_loc_limit < self.soft_loc_limit:
            raise PartitionerError(
                "hard_loc_limit must be >= soft_loc_limit "
                f"({self.hard_loc_limit} < {self.soft_loc_limit})"
            )


class WorkManifest(BaseModel):
    """A closed read allow-set — the auditor's PERMISSION BOUNDARY (NFR-S4, frozen).

    ``files`` is the SORTED tuple of repo-root-relative POSIX member paths. An
    auditor working this manifest reads ONLY these files; ``is_in_scope`` is the
    EXACT-membership predicate and ``read_in_scope`` the impure scoped read.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(default=PARTITION_SCHEMA_VERSION)
    files: tuple[str, ...] = Field(
        ..., description="Sorted repo-root-relative POSIX member paths (the closed allow-set)."
    )


class Partition(BaseModel):
    """A bounded audit unit (frozen contract; AR4 — no ``float``).

    ``partition_id`` is a sha256 over the SORTED member paths (content-derived,
    AR11 — never ``uuid4`` / counter / arrival order). ``work_manifest`` is the
    closed read allow-set. ``file_count`` / ``total_loc`` are bounded-size
    provenance (``int``); ``context_pressure`` flags a unit split because it neared
    the ceiling (or a single oversized file that cannot split below one file).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(default=PARTITION_SCHEMA_VERSION)
    partition_id: str = Field(..., description="sha256 over sorted member paths (AR11).")
    work_manifest: WorkManifest = Field(..., description="The closed read allow-set (NFR-S4).")
    file_count: int = Field(..., ge=0)
    total_loc: int = Field(..., ge=0)
    context_pressure: bool = Field(
        default=False, description="True if split/flagged because it neared the NFR-SC1 ceiling."
    )


class CutEdge(BaseModel):
    """A best-effort cohesion edge that CROSSES a partition boundary (frozen).

    Recorded-NOT-analyzed (the V1 honest limitation): the set the future Story 6.4
    ``cross_partition`` Prosecutor cut-edge pass will consume. Derived from the
    unresolved 1.4 edge set (DF-1-4-A) — a caller file whose callee resolves to a
    single defining file in a DIFFERENT partition.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    caller_file: str = Field(..., description="The file containing the call site.")
    callee_file: str = Field(..., description="The file defining the resolved callee.")
    callee: str = Field(..., description="The unresolved callee name (DF-1-4-A best-effort).")


class PartitionPlan(BaseModel):
    """The whole partition of the repo + the V1 honest-limitation provenance (frozen).

    ``partitions`` is the tuple SORTED by ``partition_id``; ``seam_analysis`` is the
    fixed ``"v2-deferred"`` marker (V1 attempts NO cross-partition seam analysis);
    ``cut_edges`` is the recorded-not-analyzed cut-edge set (the 6.4 seam). Total +
    disjoint: every source file lands in EXACTLY one partition.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(default=PARTITION_SCHEMA_VERSION)
    partitions: tuple[Partition, ...] = Field(..., description="Sorted by partition_id.")
    seam_analysis: str = Field(
        default=SEAM_ANALYSIS_MARKER,
        description="V1 honest limitation: NO cross-partition seam analysis (the 6.4 pass is the mitigation).",
    )
    cut_edges: tuple[CutEdge, ...] = Field(
        default=(), description="Best-effort cut edges, recorded-NOT-analyzed (the Story 6.4 seam)."
    )


def normalize_rel_path(rel_path: str) -> str:
    """POSIX-normalize a repo-root-relative path for EXACT membership (NFR-S4).

    Strips a single leading ``./``, collapses backslashes to POSIX slashes, and
    REJECTS an absolute path or any ``..`` traversal segment with
    :class:`PartitionScopeError` (a normalization gap must NOT become an
    off-scope-read escape). A non-``str`` input raises :class:`PartitionerError`.
    """
    if not isinstance(rel_path, str):
        raise PartitionerError(
            f"path must be str, got {type(rel_path).__name__!r}"
        )
    if not rel_path:
        raise PartitionScopeError("empty path is out of scope")
    posix = rel_path.replace("\\", "/")
    pure = Path(posix)
    # Reject absolute paths regardless of host OS: a POSIX leading slash, a
    # PureWindowsPath-absolute (drive/UNC), or a ``C:`` drive-letter prefix.
    if posix.startswith("/") or pure.is_absolute() or (len(posix) >= 2 and posix[1] == ":"):
        raise PartitionScopeError(f"absolute path '{rel_path}' is out of scope")
    parts = [p for p in posix.split("/") if p not in ("", ".")]
    if any(p == ".." for p in parts):
        raise PartitionScopeError(f"traversal path '{rel_path}' is out of scope")
    if not parts:
        raise PartitionScopeError(f"path '{rel_path}' normalizes to empty (out of scope)")
    return "/".join(parts)


def is_in_scope(manifest: WorkManifest, rel_path: str) -> bool:
    """True iff *rel_path* is an EXACT normalized member of *manifest* (NFR-S4).

    EXACT set membership over the closed allow-set — NEVER a ``str.startswith`` /
    prefix / substring check (a sibling-prefix ``auth/secrets_extra.py`` vs an
    in-scope ``auth/secrets.py`` MUST NOT pass). A malformed / absolute / traversal
    path is out of scope (``False``); a non-``WorkManifest`` raises
    :class:`PartitionerError`.
    """
    if not isinstance(manifest, WorkManifest):
        raise PartitionerError(
            f"manifest must be a WorkManifest, got {type(manifest).__name__!r}"
        )
    try:
        normalized = normalize_rel_path(rel_path)
    except PartitionScopeError:
        return False
    return normalized in frozenset(manifest.files)


# ──────────────────────────────────────────────────────────────────────────────
# PURE planner core
# ──────────────────────────────────────────────────────────────────────────────


def _coerce_index(index: AstIndex) -> AstIndex:
    if not isinstance(index, AstIndex):
        raise PartitionerError(
            f"index must be an AstIndex, got {type(index).__name__!r}"
        )
    return index


def _validate_loc_map(files: tuple[str, ...], loc_by_file: dict[str, int]) -> None:
    if not isinstance(loc_by_file, dict):
        raise PartitionerError(
            f"loc_by_file must be a dict, got {type(loc_by_file).__name__!r}"
        )
    file_set = frozenset(files)
    for path, loc in loc_by_file.items():
        if not isinstance(path, str):
            raise PartitionerError(f"loc_by_file key must be str, got {type(path).__name__!r}")
        # bool is an int subclass — reject it explicitly (a LOC count is not a flag).
        if isinstance(loc, bool) or not isinstance(loc, int):
            raise PartitionerError(
                f"loc_by_file[{path!r}] must be a non-bool int, got {type(loc).__name__!r}"
            )
        if loc < 0:
            raise PartitionerError(f"loc_by_file[{path!r}] must be >= 0, got {loc}")
    missing = sorted(f for f in file_set if f not in loc_by_file)
    if missing:
        raise PartitionerError(f"loc_by_file is missing {len(missing)} index file(s): {missing[:3]}")


def _name_to_file(index: AstIndex) -> dict[str, str]:
    """Best-effort ``Definition.name -> file`` map (DF-1-4-A under-merge rule).

    A name defined in EXACTLY ONE file maps to that file; a name defined in zero
    or MORE-THAN-ONE file is dropped (ambiguous → no cohesion edge → under-merge,
    the conservative V1 direction). Deterministic — iterates the SORTED entries.
    """
    by_name: dict[str, set[str]] = {}
    for entry in index.entries:
        for definition in entry.definitions:
            by_name.setdefault(definition.name, set()).add(entry.file_path)
    resolved: dict[str, str] = {}
    for name in sorted(by_name):
        files = by_name[name]
        if len(files) == 1:
            resolved[name] = next(iter(files))
    return resolved


def _cohesion_pairs(index: AstIndex, name_to_file: dict[str, str]) -> list[tuple[str, str]]:
    """Deterministic, sorted, de-duplicated undirected cohesion edges (caller, callee_file)."""
    pairs: set[tuple[str, str]] = set()
    for entry in index.entries:
        caller = entry.file_path
        for edge in entry.edges:
            target = name_to_file.get(edge.callee)
            if target is None or target == caller:
                continue
            a, b = sorted((caller, target))
            pairs.add((a, b))
    return sorted(pairs)


class _UnionFind:
    """Deterministic union-find over a fixed, sorted node order."""

    def __init__(self, nodes: tuple[str, ...]) -> None:
        self._parent: dict[str, str] = {n: n for n in nodes}

    def find(self, node: str) -> str:
        root = node
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[node] != root:
            self._parent[node], node = root, self._parent[node]
        return root

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        # Deterministic merge: the lexicographically smaller root wins.
        lo, hi = sorted((ra, rb))
        self._parent[hi] = lo


def _connected_components(
    files: tuple[str, ...], pairs: list[tuple[str, str]]
) -> list[list[str]]:
    """Sorted connected components (each member-sorted; components sorted by first member)."""
    uf = _UnionFind(files)
    for a, b in pairs:
        uf.union(a, b)
    groups: dict[str, list[str]] = {}
    for f in files:
        groups.setdefault(uf.find(f), []).append(f)
    components = [sorted(members) for members in groups.values()]
    components.sort(key=lambda members: members[0])
    return components


def _partition_id(files: tuple[str, ...]) -> str:
    """sha256 over the sorted member paths (AR11 — the ``assignments/<id>.json`` name)."""
    joined = "\n".join(sorted(files)).encode("utf-8")
    return hashlib.sha256(joined).hexdigest()


def _split_oversized_component(
    members: list[str],
    loc_by_file: dict[str, int],
    limits: PartitionLimits,
) -> list[tuple[list[str], bool]]:
    """Split a cohering component that itself exceeds the soft target.

    A component is an ATOMIC cohesion blob (files that call each other). When the
    blob alone exceeds the soft target it cannot stay one unit — it is split into
    sub-units (each ≤ the soft target) and every sub-unit is flagged
    ``context_pressure`` (the auto-downgrade: a cohering group was forced apart to
    stay bounded). A single file whose LOC exceeds the hard LOC limit is its own
    context-pressured unit (cannot split below one file — the AC1 boundary case).
    Returns ``[(files, pressured)]``.
    """
    units: list[tuple[list[str], bool]] = []
    current: list[str] = []
    current_loc = 0

    def flush(pressured: bool) -> None:
        nonlocal current, current_loc
        if current:
            units.append((current, pressured))
            current = []
            current_loc = 0

    for f in members:
        loc = loc_by_file[f]
        if loc > limits.hard_loc_limit:
            flush(True)
            units.append(([f], True))
            continue
        would_files = len(current) + 1
        would_loc = current_loc + loc
        if current and (would_files > limits.soft_file_limit or would_loc > limits.soft_loc_limit):
            flush(True)
        current.append(f)
        current_loc += loc
    flush(True)
    return units


def _component_loc(members: list[str], loc_by_file: dict[str, int]) -> int:
    return sum(loc_by_file[f] for f in members)


def _bin_pack(
    blobs: list[list[str]],
    loc_by_file: dict[str, int],
    limits: PartitionLimits,
) -> list[tuple[list[str], bool]]:
    """Pack atomic cohesion blobs into bounded units (greedy, deterministic).

    Each blob is a connected component that fits within the soft target (oversized
    blobs are pre-split by :func:`_split_oversized_component`). Blobs are packed in
    sorted order; a blob that would push the current unit over the soft target
    opens a new unit. Units never exceed the soft target (so always within the hard
    ceiling). A unit that was FLUSHED because the next blob did not fit is flagged
    ``context_pressure`` (the auto-downgrade: the repo exceeded one unit so the
    planner capped and opened another). The final, never-capped unit is not
    pressured (it had room to spare). Returns ``[(files, pressured)]``.
    """
    units: list[tuple[list[str], bool]] = []
    current: list[str] = []
    current_loc = 0

    def flush(pressured: bool) -> None:
        nonlocal current, current_loc
        if current:
            units.append((current, pressured))
            current = []
            current_loc = 0

    for blob in blobs:
        blob_loc = _component_loc(blob, loc_by_file)
        would_files = len(current) + len(blob)
        would_loc = current_loc + blob_loc
        if current and (would_files > limits.soft_file_limit or would_loc > limits.soft_loc_limit):
            # The current unit is capped (the next blob does not fit) — it was split
            # because it neared the ceiling, so flag it context-pressured.
            flush(True)
        current.extend(blob)
        current_loc += blob_loc
    flush(False)
    return units


def partition_repository(
    index: AstIndex,
    *,
    loc_by_file: dict[str, int],
    limits: PartitionLimits | None = None,
) -> PartitionPlan:
    """Pure graph-derived partition planner → a deterministic :class:`PartitionPlan` (FR3).

    Bounds units by FILES + LOC (NFR-SC1): each unit ≤ the soft target (≤40 files /
    15k LOC) and NEVER over the hard ceiling (≤60 / 25k). Graph-derived (Decision
    B): cohesion via the 1.4 ``edges`` resolved through a best-effort
    ``Definition.name -> file`` map (DF-1-4-A: ambiguous/unresolved callee → no
    edge → under-merge, the conservative direction). A repo at-or-under one unit
    yields a SINGLE partition (the regression-safe degenerate case). ``context_
    pressure`` auto-downgrade flags a unit split because it neared the ceiling (or
    a single file over the hard LOC limit — its own unit). Pure: takes the already
    built ``index`` + the in-memory ``loc_by_file`` as ARGUMENTS; never opens a
    file, reads a clock, or re-parses. Deterministic + order-independent (the
    plan is byte-stable for the same repo@commit).

    Raises:
        PartitionerError: a non-``AstIndex`` index, a bad ``loc_by_file`` (missing
            entry, non-``int`` value, negative LOC), or invalid limits (AR10).
    """
    index = _coerce_index(index)
    limits = limits or PartitionLimits()
    limits._validate()

    files = tuple(sorted(entry.file_path for entry in index.entries))
    _validate_loc_map(files, loc_by_file)

    if not files:
        return PartitionPlan(partitions=(), cut_edges=())

    name_to_file = _name_to_file(index)
    pairs = _cohesion_pairs(index, name_to_file)
    components = _connected_components(files, pairs)

    # A component is an atomic cohesion blob. A blob that fits within the soft
    # target is bin-packed alongside other blobs; a blob that itself exceeds the
    # soft target is split into context-pressured sub-units (auto-downgrade).
    raw_units: list[tuple[list[str], bool]] = []
    fitting_blobs: list[list[str]] = []
    for members in components:
        if (
            len(members) > limits.soft_file_limit
            or _component_loc(members, loc_by_file) > limits.soft_loc_limit
        ):
            raw_units.extend(_split_oversized_component(members, loc_by_file, limits))
        else:
            fitting_blobs.append(members)
    raw_units.extend(_bin_pack(fitting_blobs, loc_by_file, limits))

    partitions: list[Partition] = []
    file_to_partition: dict[str, str] = {}
    for unit_files, pressured in raw_units:
        sorted_files = tuple(sorted(unit_files))
        pid = _partition_id(sorted_files)
        total_loc = sum(loc_by_file[f] for f in sorted_files)
        for f in sorted_files:
            file_to_partition[f] = pid
        partitions.append(
            Partition(
                partition_id=pid,
                work_manifest=WorkManifest(files=sorted_files),
                file_count=len(sorted_files),
                total_loc=total_loc,
                context_pressure=pressured,
            )
        )

    partitions.sort(key=lambda p: p.partition_id)
    cut_edges = _cut_edges(index, name_to_file, file_to_partition)
    return PartitionPlan(partitions=tuple(partitions), cut_edges=cut_edges)


def _cut_edges(
    index: AstIndex,
    name_to_file: dict[str, str],
    file_to_partition: dict[str, str],
) -> tuple[CutEdge, ...]:
    """Recorded-NOT-analyzed cut-edge set (the Story 6.4 seam; AC5)."""
    out: set[tuple[str, str, str]] = set()
    for entry in index.entries:
        caller = entry.file_path
        caller_part = file_to_partition.get(caller)
        for edge in entry.edges:
            target = name_to_file.get(edge.callee)
            if target is None or target == caller:
                continue
            if file_to_partition.get(target) != caller_part:
                out.add((caller, target, edge.callee))
    return tuple(
        CutEdge(caller_file=c, callee_file=t, callee=name)
        for c, t, name in sorted(out)
    )


def build_plan_payload(plan: PartitionPlan) -> dict[str, object]:
    """JSON-primitive payload for a plan snapshot (routes through the single serializer).

    A thin ``model_dump(mode="json")`` — kept here so a caller never builds JSON by
    hand. Carries ONLY repo-relative paths + provenance (no absolute host path /
    source bytes, NFR-S1 spirit).
    """
    if not isinstance(plan, PartitionPlan):
        raise PartitionerError(
            f"plan must be a PartitionPlan, got {type(plan).__name__!r}"
        )
    return plan.model_dump(mode="json")


# ──────────────────────────────────────────────────────────────────────────────
# IMPURE shell — per-file LOC, manifest-scoped read (AR8; the planner stays pure)
# ──────────────────────────────────────────────────────────────────────────────


def compute_loc_by_file(source_by_file: dict[str, str]) -> dict[str, int]:
    """Per-file LOC map from an ALREADY-READ source map (the impure caller's read).

    LOC = the number of physical lines (``str.count("\\n")`` + a trailing-line
    adjustment) — an ``int`` per file fed into the pure planner, which never opens
    a file. A non-``str`` source value raises :class:`PartitionerError` (AR10).
    """
    if not isinstance(source_by_file, dict):
        raise PartitionerError(
            f"source_by_file must be a dict, got {type(source_by_file).__name__!r}"
        )
    out: dict[str, int] = {}
    for path, source in source_by_file.items():
        if not isinstance(path, str):
            raise PartitionerError(f"source key must be str, got {type(path).__name__!r}")
        if not isinstance(source, str):
            raise PartitionerError(
                f"source for {path!r} must be str, got {type(source).__name__!r}"
            )
        if source == "":
            out[path] = 0
        else:
            count = source.count("\n")
            out[path] = count if source.endswith("\n") else count + 1
    return out


def read_in_scope(repo_root: str | Path, manifest: WorkManifest, rel_path: str) -> str:
    """Read *rel_path* ONLY when it is in scope for *manifest* — else raise (NFR-S4).

    The manifest-scoped read primitive: an off-scope read is IMPOSSIBLE through it.
    Reads the file (UTF-8, ``errors="replace"`` — mirrors ``pipeline._read_source``)
    ONLY when :func:`is_in_scope` passes; otherwise raises
    :class:`PartitionScopeError` (never a silent empty read / fabricated content).
    The manifest scope is the ADDITIONAL allow-set on top of the read confinement.
    """
    if not is_in_scope(manifest, rel_path):
        raise PartitionScopeError(
            f"path '{rel_path}' is not in the work-manifest scope (off-scope read refused)"
        )
    normalized = normalize_rel_path(rel_path)
    return (Path(repo_root) / normalized).read_text(encoding="utf-8", errors="replace")
