"""Story 3.5 — cross-ENVIRONMENT byte-identical determinism + no-parallelism lock.

Verification areas:
  - ArgusAgent-PIPELINE (TC-ArgusAgent-PIPELINE-001-31..) — the e2e cross-environment proofs.
  - ArgusAgent-PORT (TC-ArgusAgent-PORT-001-NN, NEW area) — the no-parallelism / sequential-only
    lock, the order-independent-merge forward-compat lock, the stack-agnostic-core
    lock, and the cross-CWD no-leak determinism guard.

Drivers: ArgusAgent-FR-32 (run-to-completion on a sequential least-capable host →
byte-identical on-disk state — the central driver), ArgusAgent-NFR-P1 (least-capable-host
byte-identity; parallel = pure speedup), ArgusAgent-NFR-P2 (stack-agnostic core),
ArgusAgent-NFR-D2 (deterministic, zero-LLM-token), ArgusAgent-NFR-S1 (no source/secret/abs-host
path bytes), ArgusAgent-NFR-S5 (containment-checked relative locators), AR4 (no float /
single canonical serializer / no clock-uuid-random-iteration-order reliance), AR8
(pure/impure separation — the determinism comes from the pure cores; the subprocess
+ env mutation here is the documented impure shell of the TEST harness), AR11
(content-derived filenames; sorted discovery), AR7 (reuse the spine BY IMPORT).

THE PARALLEL-RUN REFRAMING (the load-bearing scope decision)
------------------------------------------------------------
The epic AC + PRD/NFR-P1 phrase the guarantee as "byte-identical to a *parallel*
run". V1 ships NO parallel scheduler — ``pipeline.py`` is sequential-canonical only
and "parallel = pure speedup" is the architecture's forward-looking statement (arch
§230 Decision A), NOT a second code path. Building a parallel scheduler solely to
diff it would be speculative scope (CLAUDE.md §5). Per the project's
conflict-resolution authority (project context wins over literal epic wording) the
guarantee is REFRAMED to the equivalent, in-scope form: **cross-ENVIRONMENT
byte-identity of the single sequential-canonical path** (varying PYTHONHASHSEED /
locale-encoding / CWD), PLUS the **order-independent-merge lock** (the precise
invariant that makes a FUTURE parallel decomposition a pure speedup: if the
sequential answer is environment-independent and the merges are order-independent,
any future parallel decomposition re-using the same pure folds + sorted merges
provably returns the same bytes). The literal sequential-vs-parallel diff is
deferred to whenever a parallel scheduler is actually built (V2+).

HOW THE ENV LEGS ARE VARIED (the AC2 mechanism — locked)
--------------------------------------------------------
``PYTHONHASHSEED`` is read once at interpreter startup, so a fresh process is
required to exercise a different seed. The robust mechanism (used for ALL three
legs so the harness is uniform) is a ``subprocess`` child of ``sys.executable``
running ``tests/argus/portability_runner.py`` with a differing ``env`` (PYTHONHASHSEED
+ LC_ALL/LANG/LC_CTYPE + PYTHONIOENCODING/PYTHONUTF8) and ``cwd``. The child writes
its ``.argus/`` tree to an out-dir the parent then byte-reads. The subprocess + env
mutation is the documented impure shell of the SUITE; the product code stays pure.
The ``C``/``POSIX``-vs-default leg is the portable minimum and always runs; a UTF-8
leg is skip-guarded ONLY if the host genuinely lacks that locale (never a silent
no-op of the byte-identity assertion).
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.ledger.coverage_ledger import (  # noqa: E402
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
)
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit, run_audit_detailed  # noqa: E402
from argus.store import canonical  # noqa: E402
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.verdict.verdict_gate import Verdict  # noqa: E402

_RUNNER = Path(__file__).resolve().parent / "portability_runner.py"
_ArgusAgent_PKG = Path("argus").resolve()

# The threads/process/async fan-out surfaces a least-capable (Cline-class)
# sequential host must NOT need (FR32 / NFR-P2). asyncio is intentionally included:
# the V1 write path is purely synchronous.
_PARALLEL_MODULES = ("threading", "multiprocessing", "concurrent", "asyncio")


def _request(repo: Path, budget: int = 100) -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo), commit="HEAD", budget=budget, materiality_bar="default"
    )


def _read_tree(out_dir: Path) -> dict[str, bytes]:
    """Read the full sorted ``.argus/`` tree under *out_dir* as a {locator: bytes} map."""
    return {
        p.relative_to(out_dir).as_posix(): p.read_bytes()
        for p in sorted(out_dir.rglob("*.json"))
    }


def _run_leg(
    tmp_path: Path,
    *,
    name: str,
    cartridge: str = "nonascii_unicode",
    mode: str = "clean",
    pythonhashseed: str = "0",
    locale: str = "C",
    pythonutf8: str | None = None,
    cwd: Path | None = None,
    budget: int = 100,
    halt_budget: int = 6,
) -> dict[str, bytes]:
    """Run one audit leg in a FRESH subprocess under a deliberately-varied environment.

    Returns the resulting ``.argus/`` tree as a {locator: bytes} map.
    """
    out_dir = tmp_path / f"{name}_out"
    work_dir = tmp_path / f"{name}_work"
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = pythonhashseed
    env["LC_ALL"] = locale
    env["LANG"] = locale
    env["LC_CTYPE"] = locale
    env.pop("PYTHONIOENCODING", None)
    env.pop("PYTHONUTF8", None)
    if pythonutf8 is not None:
        env["PYTHONUTF8"] = pythonutf8
    proc = subprocess.run(
        [
            sys.executable,
            str(_RUNNER),
            "--cartridge",
            cartridge,
            "--work-dir",
            str(work_dir),
            "--out-dir",
            str(out_dir),
            "--mode",
            mode,
            "--budget",
            str(budget),
            "--halt-budget",
            str(halt_budget),
        ],
        env=env,
        cwd=str(cwd) if cwd is not None else None,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"portability leg {name!r} failed (rc={proc.returncode}): "
        f"{proc.stdout.strip()} {proc.stderr.strip()}"
    )
    return _read_tree(out_dir)


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — sequential-only completion + the no-parallelism / sequential-only lock
# ─────────────────────────────────────────────────────────────────────────────


def _iter_argus_source_files() -> list[Path]:
    return sorted(p for p in _ArgusAgent_PKG.rglob("*.py") if p.is_file())


def test_argus_write_path_imports_no_parallelism_primitive() -> None:
    """TC-ArgusAgent-PORT-001-01 — AC1/NFR-P2: NO threading/multiprocessing/concurrent/asyncio import.

    A least-capable sequential (Cline-class) host has no concurrency primitives. An
    AST scan over EVERY ``argus/*.py`` source file proves no module
    ``import``s (or ``from ... import``s) a parallelism primitive on a write path —
    the no-web-imports-gate enforcement style, applied to FR32's least-capable-host
    guarantee. (A future parallel scheduler is V2+ and would land in a clearly-marked
    NEW module outside this gate's scope — the gate is the regression backstop.)
    """
    offenders: list[str] = []
    for src in _iter_argus_source_files():
        tree = ast.parse(src.read_text(encoding="utf-8"), filename=str(src))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in _PARALLEL_MODULES:
                        offenders.append(f"{src.name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root = node.module.split(".")[0]
                if root in _PARALLEL_MODULES:
                    offenders.append(f"{src.name}: from {node.module} import ...")
    assert not offenders, (
        "ArgusAgent write path imported a parallelism primitive (FR32 least-capable host): "
        + "; ".join(offenders)
    )


def test_argus_write_path_invokes_no_fan_out_construct() -> None:
    """TC-ArgusAgent-PORT-001-02 — AC1: NO fan-out construct used / no async def on a write path.

    Complements the import scan (TC-01): even setting aside imports, the ArgusAgent source
    must INVOKE no concurrency fan-out construct and define no coroutine on a write
    path. An AST scan over every ``argus/*.py`` finds no ``async def`` /
    ``await`` / ``async for`` / ``async with``, and no call to a fan-out factory
    (``Thread``/``Process``/``Pool``/``ThreadPoolExecutor``/``ProcessPoolExecutor`` /
    ``asyncio.*`` / ``threading.*`` / ``multiprocessing.*``).

    NOTE — the deliberate choice of an AST source scan over a ``sys.modules`` runtime
    absence check (the no-web-imports gate's mechanism). ``threading``/``concurrent``/
    ``asyncio`` are pulled into ``sys.modules`` TRANSITIVELY by third-party deps the
    impure shell imports (pydantic, tree-sitter, the lifecycle writer) — NOT by ArgusAgent's
    own code — so a ``sys.modules`` absence assertion would be a false positive that
    cannot distinguish ArgusAgent intent from a dependency's incidental import. The AST scan
    over ArgusAgent's OWN source is the honest, precise FR32 lock.
    """
    fan_out_names = {
        "Thread",
        "Process",
        "Pool",
        "ThreadPool",
        "ThreadPoolExecutor",
        "ProcessPoolExecutor",
    }
    parallel_attr_roots = set(_PARALLEL_MODULES)
    offenders: list[str] = []
    for src in _iter_argus_source_files():
        tree = ast.parse(src.read_text(encoding="utf-8"), filename=str(src))
        for node in ast.walk(tree):
            if isinstance(node, (ast.AsyncFunctionDef, ast.Await, ast.AsyncFor, ast.AsyncWith)):
                offenders.append(f"{src.name}: {type(node).__name__}")
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in fan_out_names:
                    offenders.append(f"{src.name}: call {func.id}(...)")
                elif isinstance(func, ast.Attribute):
                    if func.attr in fan_out_names:
                        offenders.append(f"{src.name}: call .{func.attr}(...)")
                    # ``asyncio.gather(...)`` / ``threading.Thread(...)`` etc.
                    value = func.value
                    if isinstance(value, ast.Name) and value.id in parallel_attr_roots:
                        offenders.append(f"{src.name}: call {value.id}.{func.attr}(...)")
    assert not offenders, (
        "the ArgusAgent write path invoked a concurrency fan-out construct (FR32 "
        "sequential-only): " + "; ".join(offenders)
    )


def test_sequential_path_completes_to_full_verdict_block_and_clean(tmp_path: Path) -> None:
    """TC-ArgusAgent-PORT-001-03 — AC1: the sequential path reaches a full verdict (BLOCK + clean).

    The audit completes to a full ``AuditVerdict`` + persisted ``.argus/`` state using
    ONLY the sequential-canonical path: the signature-demo cartridge BLOCKS (exit 2),
    a clean control is RELEASE_READY (exit 0). Sequential-only execution does not
    change the answer.
    """
    repo_block, _ = stage_cartridge("nonascii_unicode", tmp_path / "block")
    block = run_audit_detailed(_request(repo_block))
    assert block.verdict.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert block.verdict.exit_code == 2
    assert block.locators  # a full persisted .argus/ state

    repo_clean, _ = stage_cartridge("clean_control", tmp_path / "clean")
    clean = run_audit(_request(repo_clean))
    assert clean.verdict is Verdict.RELEASE_READY
    assert clean.exit_code == 0


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — cross-environment byte-identity (PYTHONHASHSEED / locale-encoding / CWD)
# ─────────────────────────────────────────────────────────────────────────────


def _assert_tree_byte_identical(tree_a: dict[str, bytes], tree_b: dict[str, bytes]) -> None:
    assert sorted(tree_a) == sorted(tree_b), "the two .argus/ trees have different locators"
    assert tree_a.keys()  # non-trivial — a real audit wrote artifacts
    for loc in sorted(tree_a):
        assert tree_a[loc] == tree_b[loc], f"byte divergence at locator {loc!r}"


def test_cross_environment_byte_identical_state(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-31 — AC2 KEYSTONE: same cartridge under differing env → byte-identical.

    Leg A: PYTHONHASHSEED=0, LC_ALL=C (non-UTF-8), PYTHONUTF8=0, cwd=home. Leg B:
    PYTHONHASHSEED=987654321, LC_ALL=en_US.utf8, cwd=tmp. The two ``.argus/`` trees are
    BYTE-IDENTICAL — the same sorted locators AND the same bytes for every locator —
    the reframed "byte-identical to a parallel run". A divergence is a HARD failure.
    """
    home = Path(os.path.expanduser("~"))
    tree_a = _run_leg(
        tmp_path,
        name="envA",
        pythonhashseed="0",
        locale="C",
        pythonutf8="0",
        cwd=home if home.is_dir() else None,
    )
    tree_b = _run_leg(
        tmp_path,
        name="envB",
        pythonhashseed="987654321",
        locale="en_US.utf8",
        pythonutf8=None,
        cwd=tmp_path,
    )
    _assert_tree_byte_identical(tree_a, tree_b)


def test_cross_environment_content_hash_identical(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-32 — AC2: every persisted envelope's content_hash is env-independent.

    Beyond raw bytes, assert the content-addressed ``content_hash`` of every envelope
    matches across the two environment legs (the NFR-D3 property — the hash covers the
    canonical payload only, excluding volatile run_id/created_at).
    """
    tree_a = _run_leg(tmp_path, name="hA", pythonhashseed="0", locale="C", pythonutf8="0")
    tree_b = _run_leg(
        tmp_path, name="hB", pythonhashseed="424242", locale="en_US.utf8", cwd=tmp_path
    )

    def _hashes(tree: dict[str, bytes]) -> dict[str, str]:
        out: dict[str, str] = {}
        for loc, raw in tree.items():
            obj = canonical.loads(raw)
            out[loc] = obj["content_hash"]
        return out

    assert _hashes(tree_a) == _hashes(tree_b)


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — cross-locale impure-shell + non-ASCII round-trip (AI-E1-1)
# ─────────────────────────────────────────────────────────────────────────────


def test_cross_locale_byte_identical_clean(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-33 — AC3/AI-E1-1: C/POSIX leg == UTF-8 leg, non-ASCII intact (clean).

    A cartridge with non-ASCII paths (``café``/Cyrillic ``тесты``) audited under a
    ``C``/``POSIX``-locale leg (PYTHONUTF8=0 forcing a non-UTF-8 default) AND a UTF-8
    leg yields BYTE-IDENTICAL ``.argus/`` trees, and the non-ASCII paths appear intact
    (correct UTF-8 bytes, NOT mojibake/octal-escaped/dropped) — proving the 1.4
    ``git ls-files -z`` + explicit-UTF-8-decode boundary is host-locale-independent
    (the Epic-1-FAIL class does not recur).
    """
    tree_c = _run_leg(tmp_path, name="locC", locale="C", pythonutf8="0", mode="clean")
    tree_u = _run_leg(tmp_path, name="locU", locale="en_US.utf8", mode="clean")
    _assert_tree_byte_identical(tree_c, tree_u)

    blob = b"".join(tree_u.values())
    assert "café".encode("utf-8") in blob  # non-ASCII path intact as UTF-8
    assert "тесты".encode("utf-8") in blob
    # NOT octal-escaped (git's default would emit "caf\303\251") and NOT dropped.
    assert b"caf\\303" not in blob
    assert b'"src/' in blob  # the file_path key is present (path not dropped)


def test_cross_locale_non_ascii_round_trips_through_reader(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-34 — AC3: the non-ASCII path round-trips intact via the 1-3 reader.

    The persisted ledger entry for the non-ASCII source file is re-read via the
    ``ApaaStoreReader`` and the path is the exact UTF-8 string (round-trip stable). The
    reader re-verifies the content_hash (tamper guard), so a successful read also proves
    canonical round-trip stability of the non-ASCII payload.
    """
    repo, _ = stage_cartridge("nonascii_unicode", tmp_path / "repo")
    result = run_audit_detailed(_request(repo))
    reader = ApaaStoreReader(repo)

    ledger_entries: dict[str, str] | None = None
    for loc in result.locators:
        if not loc.startswith("state/"):
            continue
        payload = reader.read_envelope(loc).payload  # re-verifies content_hash
        if isinstance(payload.get("ledger"), dict):
            ledger_entries = {
                e["file_path"]: e["depth"] for e in payload["ledger"]["entries"]
            }
    assert ledger_entries is not None
    assert ledger_entries.get("src/café_calc.py") == "audited_deep"
    assert ledger_entries.get("тесты/test_café_calc.py") == "audited_shallow"


def test_cross_locale_byte_identical_halted(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-35 — AC3: the cross-locale proof holds for a HALTED cartridge.

    A tiny budget halts the audit (the 3-2 halt → skip → downgrade surface). The
    halted ``.argus/`` tree (carrying the SKIPPED remainder + the halt report) is
    BYTE-IDENTICAL across the ``C``/``POSIX`` and UTF-8 legs — the degraded surface is
    host-independent.
    """
    tree_c = _run_leg(tmp_path, name="haltC", locale="C", pythonutf8="0", mode="halt")
    tree_u = _run_leg(tmp_path, name="haltU", locale="en_US.utf8", mode="halt")
    _assert_tree_byte_identical(tree_c, tree_u)


def test_cross_locale_byte_identical_resumed(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-36 — AC3: the cross-locale proof holds for a RESUMED cartridge.

    A halt-then-resume (the 3-4 resume loop) over the non-ASCII cartridge produces a
    final ``.argus/`` tree BYTE-IDENTICAL across the ``C``/``POSIX`` and UTF-8 legs — the
    whole degraded/resume surface is host-locale-independent.
    """
    tree_c = _run_leg(tmp_path, name="resC", locale="C", pythonutf8="0", mode="resume")
    tree_u = _run_leg(tmp_path, name="resU", locale="en_US.utf8", mode="resume")
    _assert_tree_byte_identical(tree_c, tree_u)


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — order-independent merges (the forward-compat "parallel = pure speedup" lock)
# ─────────────────────────────────────────────────────────────────────────────


def _entry(path: str, depth: CoverageDepth, claim: bool = True) -> CoverageLedgerEntry:
    return CoverageLedgerEntry(file_path=path, depth=depth, claim_present=claim)


def test_coverage_ledger_build_is_order_independent(tmp_path: Path) -> None:
    """TC-ArgusAgent-PORT-001-04 — AC4: CoverageLedger.build(shuffled) == build(sorted), byte-identical.

    The pure merge primitive the pipeline (and a FUTURE parallel decomposition) folds:
    feeding the SAME members in different input orders (sorted / reversed / a rotated
    order) produces the SAME sorted ledger — equal AND byte-identical through the single
    1.1 canonical serializer. This is WHY a future parallel decomposition is a pure
    speedup (the reframing of the epic's "byte-identical to a parallel run").
    """
    entries = [
        _entry("zeta.py", CoverageDepth.AUDITED_DEEP),
        _entry("alpha.py", CoverageDepth.AUDITED_SHALLOW),
        _entry("mid.py", CoverageDepth.SKIPPED, claim=False),
        _entry("café/δ.py", CoverageDepth.AUDITED_DEEP),
    ]
    sorted_ledger = CoverageLedger.build(list(entries))
    reversed_ledger = CoverageLedger.build(list(reversed(entries)))
    rotated_ledger = CoverageLedger.build(entries[2:] + entries[:2])

    assert sorted_ledger == reversed_ledger == rotated_ledger
    # Byte-identical through the single canonical serializer.
    a = canonical.dumps_bytes(sorted_ledger.model_dump(mode="json"))
    b = canonical.dumps_bytes(reversed_ledger.model_dump(mode="json"))
    c = canonical.dumps_bytes(rotated_ledger.model_dump(mode="json"))
    assert a == b == c
    # The entries are file_path-sorted regardless of input order.
    assert [e.file_path for e in sorted_ledger.entries] == sorted(
        e.file_path for e in entries
    )


def test_resume_merge_is_order_independent(tmp_path: Path) -> None:
    """TC-ArgusAgent-PORT-001-05 — AC4: the 3-4 resume merge is order-independent (byte-identical).

    The resume merge re-folds carried-forward + newly-audited + still-skipped entries
    through ``CoverageLedger.build``, which re-sorts — so the merged ledger is the SAME
    sorted ledger regardless of carried-forward-vs-newly-audited ordering. Modelled
    directly on the merge primitive: two disjoint partitions concatenated in either
    order build the same ledger.
    """
    carried = [
        _entry("src/café_calc.py", CoverageDepth.AUDITED_DEEP),
        _entry("aaa_test.py", CoverageDepth.AUDITED_SHALLOW),
    ]
    newly = [_entry("тесты/test_café_calc.py", CoverageDepth.AUDITED_SHALLOW)]

    forward = CoverageLedger.build(carried + newly)
    backward = CoverageLedger.build(newly + carried)
    assert forward == backward
    assert canonical.dumps_bytes(forward.model_dump(mode="json")) == canonical.dumps_bytes(
        backward.model_dump(mode="json")
    )


def test_locator_discovery_is_sorted(tmp_path: Path) -> None:
    """TC-ArgusAgent-PORT-001-06 — AC4/AR11: the pipeline's locator enumeration is sorted.

    The resume's ``_list_locators`` enumerates the resolved sub-dir via ``sorted(...)``
    so discovery order is content-derived (arrival-order-independent — AR11). Asserted
    directly against the real helper over a populated store.
    """
    from argus import pipeline as pipeline_mod

    repo, _ = stage_cartridge("nonascii_unicode", tmp_path / "repo")
    run_audit_detailed(_request(repo))
    reader = ApaaStoreReader(repo)

    for subdir in ("state", "findings", "assignments"):
        locs = pipeline_mod._list_locators(reader, subdir)
        assert list(locs) == sorted(locs), f"{subdir} discovery is not sorted"


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — no absolute host path / source / secret byte across the cross-CWD leg
# ─────────────────────────────────────────────────────────────────────────────


def test_cross_cwd_no_absolute_host_path_in_persisted_state(tmp_path: Path) -> None:
    """TC-ArgusAgent-PORT-001-07 — AC5/NFR-S1: a foreign-CWD run leaks no absolute host path.

    The audit run from a foreign CWD with the repo passed as an absolute path persists
    artifacts whose stored locators are repo-RELATIVE POSIX paths — the foreign-CWD
    absolute prefix is ABSENT from every persisted byte (no ``os.getcwd()`` leak into a
    hashed payload). REUSES the established no-abs-path determinism assertion (the full
    randomized-canary containment suite is Story 4.4 — NOT built here).
    """
    foreign_cwd = tmp_path / "foreign"
    foreign_cwd.mkdir()
    tree = _run_leg(tmp_path, name="cwd", locale="C", cwd=foreign_cwd, mode="clean")

    abs_prefix = str(foreign_cwd).encode("utf-8")
    abs_posix = foreign_cwd.as_posix().encode("utf-8")
    work_prefix = str(tmp_path).encode("utf-8")
    for loc, raw in tree.items():
        assert abs_prefix not in raw, f"absolute foreign CWD leaked into {loc!r}"
        assert abs_posix not in raw, f"absolute foreign CWD (posix) leaked into {loc!r}"
        assert work_prefix not in raw, f"absolute host work path leaked into {loc!r}"
        # No drive-letter / unix absolute file_path in the persisted bytes.
        assert b'"/' not in raw, f"a unix-absolute path leaked into {loc!r}"


def test_cross_cwd_byte_identical_to_repo_root_run(tmp_path: Path) -> None:
    """TC-ArgusAgent-PORT-001-08 — AC5/AC2(c): a foreign-CWD run is byte-identical to a root-CWD run.

    The cross-CWD byte-identity independently proves no ``os.getcwd()`` / relative-path
    reliance leaks into a hashed payload (the same answer regardless of where the
    process is launched, as long as the repo is passed absolutely).
    """
    foreign_cwd = tmp_path / "foreign"
    foreign_cwd.mkdir()
    tree_foreign = _run_leg(tmp_path, name="cwdF", locale="C", cwd=foreign_cwd)
    tree_root = _run_leg(tmp_path, name="cwdR", locale="C", cwd=tmp_path)
    _assert_tree_byte_identical(tree_foreign, tree_root)


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — a no-portability-suite run is byte-identical (frozen contracts unchanged)
# ─────────────────────────────────────────────────────────────────────────────


def test_normal_run_byte_identical_across_two_runs(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-37 — AC6: a normal audit is byte-identical across two runs.

    This story adds NO new invocation surface / AuditRequest field / CLI flag. A plain
    ``run_audit_detailed`` over the non-ASCII cartridge produces verdict + findings +
    ledger artifacts byte-identical across two independent runs (the regression-safe
    keystone — the spine is unchanged).
    """
    repo_a, _ = stage_cartridge("nonascii_unicode", tmp_path / "a")
    repo_b, _ = stage_cartridge("nonascii_unicode", tmp_path / "b")
    res_a = run_audit_detailed(_request(repo_a))
    res_b = run_audit_detailed(_request(repo_b))

    reader_a = ApaaStoreReader(repo_a)
    reader_b = ApaaStoreReader(repo_b)
    assert res_a.locators[0] == res_b.locators[0]
    assert reader_a.read_bytes(res_a.locators[0]) == reader_b.read_bytes(res_b.locators[0])
    findings_a = {
        loc: reader_a.read_bytes(loc) for loc in res_a.locators if loc.startswith("findings/")
    }
    findings_b = {
        loc: reader_b.read_bytes(loc) for loc in res_b.locators if loc.startswith("findings/")
    }
    assert findings_a == findings_b


def test_no_new_audit_request_field_or_cli_flag() -> None:
    """TC-ArgusAgent-PORT-001-09 — AC6: this story added NO AuditRequest field / CLI flag.

    The AuditRequest model fields are exactly the pre-3.5 set (no portability/parallel
    field), and the CLI exposes no new flag (the ``--resume`` flag stays deferred —
    DF-3-4-A / Story 7.1). A guard against accidental scope creep.

    The set below is a DELIBERATE INVENTORY, not a freeze: a field lands here only
    with an explicit reason. ``coverage_scope`` selects the population the deep-%
    gate assesses ('repository' default = the V1 fold, byte-identical; 'application'
    holds out shallow-by-construction test files and DISCLOSES the narrowing on the
    verdict). It cannot weaken a gate — the coverage floor is re-applied within the
    scope — so it does not reopen the portability/parallel surface this guard closed.
    """
    fields = set(AuditRequest.model_fields)
    assert fields == {
        "schema_version",
        "repo_path",
        "commit",
        "budget",
        "materiality_bar",
        "critical_paths",
        "excluded_critical_paths",
        "enabled_passes",
        "enabled_reports",
        "report_dir",
        "ignore_paths",
        "ignore_patterns",
        "coverage_scope",
        # Release-gate mode. Default False so a first run works on any directory;
        # True restores the original refuse-on-drift intake contract for CI.
        "strict",
    }




# ─────────────────────────────────────────────────────────────────────────────
# AC7 — stack-agnostic-core lock (NFR-P2)
# ─────────────────────────────────────────────────────────────────────────────


def test_ledger_verdict_core_has_no_host_or_stack_specific_branch() -> None:
    """TC-ArgusAgent-PORT-001-10 — AC7/NFR-P2: the ledger/verdict core is stack-agnostic.

    A verify-and-lock assertion (NOT the V2 multi-language implementation): the
    ledger/verdict CORE (``ledger/coverage_ledger.py``, ``verdict/verdict_gate.py``)
    carries NO host-/stack-/platform-/language-specific branch — it folds the
    stack-agnostic ``claim→validated?`` interface the 1.4 routing established. An AST
    scan over the two core modules finds no reference to host/platform/OS/language
    tokens, and no ``import`` of ``os``/``sys``/``platform``/``locale``.
    """
    core_files = (
        _ArgusAgent_PKG / "ledger" / "coverage_ledger.py",
        _ArgusAgent_PKG / "verdict" / "verdict_gate.py",
    )
    host_tokens = {
        "platform",
        "getcwd",
        "uname",
        "win32",
        "linux",
        "darwin",
        "posix",
        "java",
        "javascript",
        "typescript",
        "golang",
        "rust",
    }
    forbidden_imports = {"os", "sys", "platform", "locale", "socket", "subprocess"}
    offenders: list[str] = []
    for src in core_files:
        text = src.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(src))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in forbidden_imports:
                        offenders.append(f"{src.name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in forbidden_imports:
                    offenders.append(f"{src.name}: from {node.module} import ...")
            elif isinstance(node, ast.Name) and node.id.lower() in host_tokens:
                offenders.append(f"{src.name}: name {node.id!r}")
            elif isinstance(node, ast.Attribute) and node.attr.lower() in host_tokens:
                offenders.append(f"{src.name}: attribute {node.attr!r}")
    assert not offenders, (
        "the ledger/verdict core carries a host-/stack-specific branch (NFR-P2): "
        + "; ".join(offenders)
    )


# ─────────────────────────────────────────────────────────────────────────────
# NFR-P1 — path matching must not depend on the HOST's filename case rules
# ─────────────────────────────────────────────────────────────────────────────
#
# `fnmatch.fnmatch` compares through `os.path.normcase`: identity on POSIX,
# lower-casing on Windows. Two modules used it on repo-relative paths, so the same
# repository at the same commit answered differently by operating system:
#
#   * `intake/ignore_rules` decides which files are ENUMERATED, moving the coverage
#     ledger's denominator, the deep-%, the verdict and the exit code;
#   * `detectors/secret_suppression` decides whether a DETECTED SECRET is suppressed,
#     so a credential reported on Linux was hidden on Windows.
#
# The suite already pinned byte-identity across environment and locale, but nothing
# pinned it across filename-case semantics — which is exactly why the divergence
# survived. These tests assert the property directly (a case-varied path must not
# match a lower-case pattern) and structurally (no module may reach for the
# host-normalizing spelling again).


def test_gitignore_matching_is_case_sensitive_on_every_host() -> None:
    """A case-varied path must NOT match a lower-case gitignore pattern (NFR-P1)."""
    from argus.intake.ignore_rules import gitignore_matches, parse_gitignore

    patterns = parse_gitignore("build/\nvendor\n*.log\n")

    # Exact case matches on every host.
    assert gitignore_matches("build/out.py", patterns)
    assert gitignore_matches("vendor/lib.py", patterns)
    assert gitignore_matches("debug.log", patterns)

    # Case-varied paths must NOT match — on Windows `fnmatch` would say they do,
    # silently removing these files from the audited population.
    assert not gitignore_matches("Build/out.py", patterns)
    assert not gitignore_matches("Vendor/lib.py", patterns)
    assert not gitignore_matches("debug.LOG", patterns)


def test_secret_suppression_path_globs_are_case_sensitive_on_every_host() -> None:
    """A case-varied path must NOT be treated as a test fixture (NFR-P1 + security)."""
    from argus.detectors.secret_suppression import SecretSuppressionEngine as Engine

    # Exact case is a fixture path on every host.
    assert Engine.is_test_fixture_path("tests/conftest.py")
    assert Engine.is_test_fixture_path("pkg/test_auth.py")

    # Case-varied paths must NOT be — on Windows `fnmatch` would suppress a real
    # secret found in any of these files.
    assert not Engine.is_test_fixture_path("Tests/Config.py")
    assert not Engine.is_test_fixture_path("SRC/Test_Auth.py")
    assert not Engine.is_test_fixture_path("Lib/Fixtures/keys.py")
    assert not Engine.is_test_fixture_path("app/Mock_Db.py")


def test_a_real_secret_in_a_case_varied_path_is_not_suppressed() -> None:
    """The end-to-end consequence: the credential is reported, on any host."""
    from argus.detectors.secret_suppression import SecretSuppressionEngine as Engine

    suppressed, reason = Engine.evaluate_suppression(
        file_path="Tests/Config.py",
        snippet="ghp_aB3dEfGh1JkLmN0pQrStUvWxYz456789012",
        line_content='API_TOKEN = "ghp_aB3dEfGh1JkLmN0pQrStUvWxYz456789012"',
    )
    assert suppressed is False, f"a live token was suppressed by host case rules ({reason})"


def test_no_argus_module_uses_the_host_normalizing_fnmatch() -> None:
    """Structural guard: `fnmatch.fnmatch` / `os.path.normcase` are banned (NFR-P1).

    `fnmatchcase` is the only permitted spelling. This fails on reintroduction rather
    than waiting for a cross-host verdict divergence to be noticed in the field.
    """
    root = Path(__file__).resolve().parents[1] / "argus"
    offenders: list[str] = []
    for src in sorted(root.rglob("*.py")):
        tree = ast.parse(src.read_text(encoding="utf-8"), str(src))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            attr = node.func.attr
            base = getattr(node.func.value, "id", "")
            if attr == "fnmatch" and base == "fnmatch":
                offenders.append(f"{src.relative_to(root).as_posix()}:{node.lineno} fnmatch.fnmatch")
            elif attr == "normcase":
                offenders.append(f"{src.relative_to(root).as_posix()}:{node.lineno} normcase")
    assert not offenders, (
        "host-case-normalizing path matching reintroduced (NFR-P1) — use "
        "fnmatch.fnmatchcase: " + "; ".join(offenders)
    )


# ─────────────────────────────────────────────────────────────────────────────
# NFR-P1 — a non-UTF-8 host locale must not change the recorded bytes (F-21)
# ─────────────────────────────────────────────────────────────────────────────
#
# On POSIX under LC_ALL=C with PYTHONUTF8=0, Python decodes filenames with the ASCII
# codec plus surrogateescape, so `café` arrives as 'caf\udcc3\udca9'. Those strings reach
# every Recording locator, and `str.encode("utf-8")` refuses lone surrogates — so the
# audit CRASHED (PipelineError -> exit 1 -> AUDIT_FAILED) on any repository containing a
# non-ASCII filename, on exactly those hosts. AR10 forbids a crash; NFR-P1 requires the
# same bytes everywhere.
#
# The cross-locale legs above already catch this end-to-end, but only on a POSIX runner —
# Windows takes filenames from the wide APIs and never produces surrogates, so a
# developer machine stays green while CI is red. That asymmetry is why this went unseen.
# These tests assert the property directly from simulated inputs, so the guard fires on
# EVERY host.


def _as_c_locale(text: str) -> str:
    """The str a C-locale POSIX host yields for *text*'s UTF-8 bytes on disk."""
    return text.encode("utf-8").decode("ascii", "surrogateescape")


def test_surrogate_path_serializes_identically_to_utf8_host() -> None:
    """The two host views of one filename must produce identical canonical bytes."""
    from argus.store import canonical

    for name in ("café/x.py", "тесты/test_a.py", "ünïcode/mixed_日本.py"):
        native = _as_c_locale(name)
        assert native != name, "precondition: the C-locale view must carry surrogates"
        assert canonical.dumps_bytes({"file_path": native}) == canonical.dumps_bytes(
            {"file_path": name}
        ), f"host locale changed the recorded bytes for {name!r} (NFR-P1)"


def test_surrogate_path_does_not_raise_on_encode() -> None:
    """A surrogate-bearing path must serialize, not crash (AR10)."""
    from argus.store import canonical

    payload = {"locators": [{"file_path": _as_c_locale("café/x.py"), "start_line": 1}]}
    canonical.dumps_bytes(payload)  # must not raise UnicodeEncodeError


def test_undecodable_byte_degrades_deterministically() -> None:
    """A byte that is not valid UTF-8 becomes U+FFFD, not an exception (errors=replace)."""
    from argus.store import canonical

    undecodable = b"x\xff.py".decode("ascii", "surrogateescape")
    assert canonical.dumps_bytes({"p": undecodable}) == b'{"p":"x\xef\xbf\xbd.py"}\n'


def test_payloads_without_surrogates_are_untouched() -> None:
    """The repair must be a no-op for every string without surrogates (byte-identity)."""
    import json

    from argus.store import canonical

    for value in ("plain.py", "café/x.py", "тесты/y.py", ""):
        assert canonical.dumps({"v": value}) == (
            '{"v":' + json.dumps(value, ensure_ascii=False) + "}\n"
        )


# ── The OTHER half of the same boundary: a recorded path must stay OPENABLE ──
#
# `_repair_surrogates` makes the RECORDED form host-independent. Its inverse,
# `repo_loader.to_native_fs_path`, makes the I/O form host-openable. They are needed
# together because the two intake producers start from opposite ends: `source_state`
# walks the filesystem (native, surrogate-bearing), while `repo_loader` decodes git's
# UTF-8 bytes (true text). Without the inverse, the resume path — the remaining
# `load_repo_at_commit` caller — handed true-text paths to `open()` and a C-locale host
# raised "'ascii' codec can't encode character", a DIFFERENT crash from the surrogate
# one above and invisible to every other test.


def test_git_path_round_trips_through_the_host_filename_rule() -> None:
    """to_native_fs_path -> _repair_surrogates is the identity, on EVERY host (NFR-P1).

    The composition is what guarantees the persisted bytes match across locales: I/O
    uses the native form, the serializer restores the recorded form. On a UTF-8 host
    both halves are identities; on a C-locale host they are exact inverses.
    """
    from argus.intake.repo_loader import to_native_fs_path
    from argus.store.canonical import _repair_surrogates

    for name in ("café/x.py", "тесты/test_a.py", "ünïcode/mixed_日本.py", "plain.py"):
        assert _repair_surrogates(to_native_fs_path(name)) == name


def test_c_locale_native_form_repairs_back_to_the_git_form() -> None:
    """The inverse holds for the exact host view the cross-locale CI leg exercises.

    Asserted from a SIMULATED C-locale string so the guard fires on Windows too, where
    ``os.fsdecode`` never produces a surrogate and the real defect is unobservable.
    """
    from argus.store.canonical import _repair_surrogates

    for name in ("café/x.py", "тесты/test_a.py", "ünïcode/mixed_日本.py"):
        native = _as_c_locale(name)
        assert native != name, "precondition: the C-locale view must carry surrogates"
        assert _repair_surrogates(native) == name
