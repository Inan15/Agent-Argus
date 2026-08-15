"""Story 11.5 — the BUILT artifact is complete, and the sentences describing it are true.

Verification areas ``ArgusAgent-RELEASE`` (``TC-ArgusAgent-RELEASE-001-20``..``-24``,
CONTINUING the index locked by Story 9.2 in ``tests/test_release_preflight.py``, which
ended at ``-19``) and ``ArgusAgent-DOCS`` (``TC-ArgusAgent-DOCS-001-54``..``-58``,
continuing the index that ended at ``-53``).

**Why this file exists at all: a guard that inspects the SOURCE TREE is vacuous by
construction for a claim about the DISTRIBUTION.** This is Story 11.5's headline finding
and it was demonstrated, not argued. ``tests/test_release_preflight.py``'s
``TC-ArgusAgent-RELEASE-001-11`` computes the un-shippable surface by walking the source
tree's import graph with ``ast``. Story 11.5 built the whole DF-9-2-A fix — the module-level
``sys.path.insert`` + unconditional ``from _registry import …`` in
``argus/precision/replay_harness.py`` became a lazily-resolved ``_registry_module()`` — and
measured the wheel going from *5 modules fail to import* to *0 fail*. **``-11`` stayed
GREEN across the entire fix.** ``import _registry`` inside a function body is still an
``ast.Import`` node named ``_registry``, so the walk finds it exactly as before; the walk is
structurally incapable of distinguishing a module-level import from a lazy one, which is
the *entire content* of the fix. ``DF-9-2-A``'s stated close condition — *"pinned in BOTH
directions, so a fix that leaves the record stale goes RED"* — was false as written, and
``README.md``'s *"so this list cannot drift from the code"* was false with it. Both drifted
anyway while ``-11`` was green: the denominator moved 71 → 72 and the importable count
66 → 67 during Epics 10–11 with nothing going red, because ``-11`` pins a *set of paths*
and the documents publish *numbers*.

So everything here is measured against a **freshly built wheel and sdist**, built LOCALLY
into a temporary directory. Nothing is published, pushed, tagged or uploaded, and no build
artifact is written into the repository (Story 11.5 §0.5 — the publish is Story 12.9).

**The measurement trap that cost a cycle, and why the probe asserts its own provenance.**
This repository is installed EDITABLE into its own ``.venv`` (``argus.pth`` points at the
repo root). Any probe that leaves the repository reachable on ``sys.path`` silently imports
``argus`` from the repo — where ``tests/cartridges/`` exists — and reports a triumphant
*72 of 72* while the wheel is still broken. Running the probe with ``python -I`` makes it
WORSE, not better: ``-I`` implies ``-E``, which drops ``PYTHONPATH`` but leaves the ``.pth``
in place. **A probe that cannot prove where it imported from is not a probe**, so the probe
below removes the repository root from ``sys.path`` by normalised absolute path, prepends
the extraction directory, runs from a ``cwd`` outside the repository, and REFUSES with
``PROBE-INVALID`` unless ``argus.__file__`` resolves inside the extraction directory.
``-21`` is the positive control for that refusal.

No network, no LLM, no ``.argus/`` write, no new dependency: ``build`` is already a release
dependency (``.github/workflows/release.yml`` invokes it) and ``zipfile``/``tarfile`` are
stdlib. Where a tool is missing the guard reports :class:`release_preflight.Unevaluable` and
SKIPS with that named reason — it never passes silently (AR10 / NFR-R1).
"""

from __future__ import annotations

import functools
import importlib.util
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import release_preflight as rp  # noqa: E402

# The post-fix record, and the ONE place it lives. Story 9.2 wrote it; Story 11.5 empties
# it against a freshly built wheel. It is imported rather than re-declared because a second
# copy of a pinned figure is precisely the fork class this story exists to close.
from tests.test_release_preflight import (  # noqa: E402
    _NOT_IMPORTABLE_FROM_DISTRIBUTION,
)

_README = _REPO_ROOT / "README.md"
_CHANGELOG = _REPO_ROOT / "CHANGELOG.md"

# The documents that publish a figure about the built distribution. Both are release
# surfaces already registered in tests/test_release_surface_honesty.py.
_FIGURE_DOCUMENTS: tuple[Path, ...] = (_README, _CHANGELOG)

# The build tooling this guard needs. Absent => Unevaluable + skip, never a silent pass.
_REQUIRED_BUILD_TOOLS: tuple[tuple[str, str], ...] = (
    ("build", "PEP 517 front-end (`python -m build`), the same one release.yml runs"),
    ("flit_core", "the build backend named by [build-system] in pyproject.toml"),
)


# ─────────────────────────────────────────────────────────────────────────────
# Building and probing the real artifact
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class BuiltDistribution:
    """A wheel and an sdist built from THIS tree, plus where the wheel was extracted."""

    wheel: Path
    sdist: Path
    extracted: Path
    outside_cwd: Path
    wheel_entries: tuple[str, ...]
    sdist_members: tuple[str, ...]

    @property
    def module_entries(self) -> tuple[str, ...]:
        """Every shipped ``argus/**`` module, read off the ARCHIVE — never a hand list."""
        return tuple(
            entry
            for entry in self.wheel_entries
            if entry.startswith("argus/") and entry.endswith(".py")
        )

    @property
    def non_module_entries(self) -> tuple[str, ...]:
        """Everything in the wheel that is not an ``argus/**`` module (i.e. ``dist-info``)."""
        return tuple(e for e in self.wheel_entries if e not in set(self.module_entries))

    @property
    def data_assets(self) -> tuple[str, ...]:
        """Shipped files that are neither Python modules nor distribution metadata.

        This is the closure behind AC5: a slash command, a skill file or a prompt template
        would have to appear HERE to be installed by ``pip install argus-agent``. Measured
        on this tree: empty.
        """
        return tuple(e for e in self.non_module_entries if ".dist-info/" not in e)


def unevaluable_build_tooling(
    is_available: "object | None" = None,
) -> rp.Unevaluable | None:
    """Why the built-artifact guard cannot run here, as a NAMED outcome — or ``None``.

    Injectable so ``-24`` can prove the missing-tool path produces a named refusal to
    evaluate rather than a silent pass. The vocabulary is
    :class:`release_preflight.Unevaluable`, reused rather than forked (AR7 / §3.3): E6 is
    the enumerated release case about the built artifacts, and "could not build them at
    all" is that case being unobservable, not that case clearing.
    """
    probe = is_available if is_available is not None else _module_is_installed
    missing = [
        f"{name} ({why})"
        for name, why in _REQUIRED_BUILD_TOOLS
        if not probe(name)  # type: ignore[operator]
    ]
    if not missing:
        return None
    return rp.Unevaluable(
        "E6",
        "the distribution could not be built in this environment, so nothing about the "
        f"BUILT artifact was checked. Missing: {', '.join(missing)}. Install the `dev` "
        "extra plus `build`, or run this guard where release.yml runs it.",
    )


def console_script_aliases() -> dict[str, str]:
    """Every ``[project.scripts]`` alias -> its target, DERIVED from ``pyproject.toml``.

    PROMOTED to a public helper 2026-08-15 by Story 12.9 / AC1 (12.6 / DN-7: *need a helper?
    promote it; never reach through a ``_``-prefixed API, and never copy it*). ``-56`` had
    this derivation inline and ``tests/test_installed_artifact.py`` needs the identical
    closure to exercise every alias from a fresh environment. Two copies of *what the
    distribution's entry points are* is the ``_CONSOLE_SCRIPTS`` recognizer-that-stopped-
    recognizing class this project has now recorded four times, so there is one.

    A closure, not a list: a FIFTH alias is covered by every caller with no edit here.
    """
    scripts = re.search(
        r"^\[project\.scripts\]\n((?:.+\n)+?)\n",
        (_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    assert scripts, "pyproject.toml declares no [project.scripts] table"
    aliases = dict(re.findall(r'^(\S+)\s*=\s*"([^"]+)"', scripts.group(1), re.MULTILINE))
    assert aliases, "no console alias parsed out of [project.scripts]"
    return aliases


def _module_is_installed(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):  # pragma: no cover - defensive
        return False


@functools.lru_cache(maxsize=1)
def _build_distribution() -> BuiltDistribution:
    """Build the wheel + sdist ONCE per session, outside the repository, and extract them.

    ``--no-isolation`` deliberately: the backend is already installed (asserted by
    :func:`unevaluable_build_tooling`), and isolation would make this guard reach the
    network, which no test in this suite is allowed to do.
    """
    outdir = Path(tempfile.mkdtemp(prefix="argus-dist-"))
    completed = subprocess.run(
        [sys.executable, "-m", "build", "--no-isolation", "--outdir", str(outdir), "."],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, (
        "`python -m build` failed, so NOTHING about the built artifact was verified. "
        f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
    )

    wheels = sorted(outdir.glob("*.whl"))
    sdists = sorted(outdir.glob("*.tar.gz"))
    # E6's vocabulary, reused: both artifacts or none. Asserted here so every later
    # measurement in this file is known to be over a COMPLETE build.
    refusal = rp.check_e6_incomplete_build(
        rp.PreflightContext(
            repo_root=_REPO_ROOT,
            tag="v0.1.0",
            pyproject_version="0.1.0",
            dist_files=tuple(sorted(p.name for p in outdir.iterdir() if p.is_file())),
        )
    )
    assert refusal is None, f"the local build is incomplete: {refusal}"

    extracted = Path(tempfile.mkdtemp(prefix="argus-wheel-"))
    with zipfile.ZipFile(wheels[0]) as archive:
        archive.extractall(extracted)
        wheel_entries = tuple(sorted(archive.namelist()))
    with tarfile.open(sdists[0]) as archive:
        sdist_members = tuple(sorted(archive.getnames()))

    return BuiltDistribution(
        wheel=wheels[0],
        sdist=sdists[0],
        extracted=extracted,
        outside_cwd=Path(tempfile.mkdtemp(prefix="argus-cwd-")),
        wheel_entries=wheel_entries,
        sdist_members=sdist_members,
    )


def _distribution() -> BuiltDistribution:
    """The built distribution, or a SKIP carrying the named reason it is unavailable."""
    unevaluable = unevaluable_build_tooling()
    if unevaluable is not None:
        pytest.skip(str(unevaluable))
    return _build_distribution()


# The probe prelude. It runs in a subprocess with a clean environment and asserts its own
# provenance BEFORE importing anything under test — see the module docstring.
_PROBE_PRELUDE = """
import os, sys
_repo = os.path.normcase(os.path.abspath({repo!r}))
sys.path[:] = [p for p in sys.path
               if os.path.normcase(os.path.abspath(p or os.getcwd())) != _repo]
sys.path.insert(0, os.path.abspath({path_head!r}))
import argus
_where = os.path.normcase(os.path.abspath(argus.__file__))
if not _where.startswith(os.path.normcase(os.path.abspath({expected_root!r}))):
    raise SystemExit("PROBE-INVALID: argus resolved from " + _where)
import {module}
"""


def _module_name(entry: str) -> str:
    """``argus/precision/replay_harness.py`` -> ``argus.precision.replay_harness``."""
    dotted = entry[: -len(".py")].replace("/", ".")
    return dotted[: -len(".__init__")] if dotted.endswith(".__init__") else dotted


def _probe_import(
    dist: BuiltDistribution, entry: str, *, path_head: str | None = None
) -> subprocess.CompletedProcess[str]:
    """Import ONE shipped module in a CLEAN subprocess, from outside the repository."""
    environ = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    environ["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [
            sys.executable,
            "-c",
            _PROBE_PRELUDE.format(
                repo=str(_REPO_ROOT),
                path_head=path_head if path_head is not None else str(dist.extracted),
                expected_root=str(dist.extracted),
                module=_module_name(entry),
            ),
        ],
        cwd=str(dist.outside_cwd),
        env=environ,
        capture_output=True,
        text=True,
    )


def _last_line(text: str) -> str:
    lines = [line for line in text.strip().splitlines() if line.strip()]
    return lines[-1] if lines else ""


@functools.lru_cache(maxsize=1)
def _import_failures() -> tuple[tuple[str, str], ...]:
    """``(entry, last stderr line)`` for every shipped module that does NOT import."""
    dist = _build_distribution()
    entries = dist.module_entries
    with ThreadPoolExecutor(max_workers=min(8, (os.cpu_count() or 2))) as pool:
        results = list(pool.map(lambda e: (e, _probe_import(dist, e)), entries))
    return tuple(
        (entry, _last_line(done.stderr))
        for entry, done in results
        if done.returncode != 0
    )


def _importable_module_count() -> int:
    return len(_build_distribution().module_entries) - len(_import_failures())


# ─────────────────────────────────────────────────────────────────────────────
# AC1 / AC2 — the artifact
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_RELEASE_001_20_every_shipped_module_imports_from_the_built_wheel() -> None:
    """TC-ArgusAgent-RELEASE-001-20 — AC1/AC2: the wheel is complete, measured not assumed.

    This is the guard ``-11`` could never be. It builds the real wheel, walks the ARCHIVE
    (never a hand-written module list — AI-E10-5), and imports every shipped module in a
    clean subprocess with this repository off ``sys.path``. It pins the broken set in BOTH
    directions: a REGROWTH fails, and a shrink fails too so the record cannot go stale
    behind a fix.
    """
    dist = _distribution()
    entries = dist.module_entries
    assert entries, "the built wheel contains no argus/** module — the walk is broken"

    # Closure both ways: the wheel ships exactly the modules the tree has, so a module
    # silently dropped from (or smuggled into) the distribution fails here.
    on_disk = {
        path.relative_to(_REPO_ROOT).as_posix()
        for path in (_REPO_ROOT / "argus").rglob("*.py")
        if "__pycache__" not in path.parts
    }
    assert set(entries) == on_disk, (
        "the wheel's module set and the source tree's disagree; "
        f"wheel-only={sorted(set(entries) - on_disk)} tree-only={sorted(on_disk - set(entries))}"
    )

    failures = _import_failures()
    assert {entry for entry, _ in failures} == set(_NOT_IMPORTABLE_FROM_DISTRIBUTION), (
        "the set of argus/** modules that cannot be imported from the BUILT distribution "
        "changed. If it GREW, a module was made unshippable — a consumer sees "
        "ModuleNotFoundError on the first line they type. If it SHRANK, the record in "
        "tests/test_release_preflight.py._NOT_IMPORTABLE_FROM_DISTRIBUTION and the figures "
        "in README.md / CHANGELOG.md must be updated to match rather than left stale. "
        f"expected {sorted(_NOT_IMPORTABLE_FROM_DISTRIBUTION)}, measured {sorted(failures)}"
    )


def test_TC_ArgusAgent_RELEASE_001_21_the_probe_refuses_when_it_cannot_prove_provenance() -> None:
    """TC-ArgusAgent-RELEASE-001-21 — AC1.2: positive control for the §A.5 measurement trap.

    ``.venv`` carries an EDITABLE install of this repository. If the repo stays reachable
    ahead of the extracted wheel, every module imports — from the repo, where
    ``tests/cartridges/`` exists — and the probe would report a false clean bill of health.
    Here the repository root is prepended deliberately while provenance is still expected
    to be the extraction directory: the probe must REFUSE, not report success.
    """
    dist = _distribution()
    entry = "argus/precision/replay_harness.py"
    assert entry in dist.module_entries

    honest = _probe_import(dist, entry)
    assert honest.returncode == 0, (
        f"the shipped precision harness does not import from the wheel: {honest.stderr}"
    )

    spoofed = _probe_import(dist, entry, path_head=str(_REPO_ROOT))
    assert spoofed.returncode != 0, (
        "the probe accepted a module resolved from the REPOSITORY instead of the built "
        "wheel. That is exactly the false 72-of-72 this control exists to make impossible."
    )
    assert "PROBE-INVALID" in spoofed.stderr, spoofed.stderr


def test_TC_ArgusAgent_RELEASE_001_22_the_sdist_ships_no_test_tree_and_the_build_is_complete() -> None:
    """TC-ArgusAgent-RELEASE-001-22 — AC2.1b: ``tests/`` is repository-only, and stays so.

    The fix makes the cartridge registry resolve lazily; it must NOT be "fixed" by shipping
    ``tests/`` instead. The labelled golden-key store is the ground truth the precision
    number is measured against — publishing it to every consumer is the wrong direction,
    and it would also make the wheel-import measurement meaningless.
    """
    dist = _distribution()
    root = f"{dist.sdist.name[: -len('.tar.gz')]}/"
    inside = [m[len(root) :] for m in dist.sdist_members if m.startswith(root)]
    assert inside, f"the sdist has no member under {root!r}: {dist.sdist_members[:5]}"
    leaked = [m for m in inside if m == "tests" or m.startswith("tests/")]
    assert not leaked, f"the sdist ships the repository-only test tree: {leaked}"
    assert not [m for m in dist.wheel_entries if m.startswith("tests/")], (
        "the wheel ships the repository-only test tree"
    )

    # E6 in both directions, over the REAL file names, using the shipped vocabulary.
    def _e6(*files: str) -> rp.Refusal | None:
        return rp.check_e6_incomplete_build(
            rp.PreflightContext(
                repo_root=_REPO_ROOT,
                tag="v0.1.0",
                pyproject_version="0.1.0",
                dist_files=files,
            )
        )

    assert _e6(dist.wheel.name, dist.sdist.name) is None
    assert _e6(dist.wheel.name) is not None, "a wheel-only build must be refused"
    assert _e6(dist.sdist.name) is not None, "an sdist-only build must be refused"


def test_TC_ArgusAgent_RELEASE_001_23_the_guard_fails_when_the_artifact_is_wrong() -> None:
    """TC-ArgusAgent-RELEASE-001-23 — AC2.4: the guard BITES, demonstrated on demand.

    A guard that has never been observed failing is not evidence. This injects into the
    EXTRACTED distribution the exact defect DF-9-2-A was — a module-level
    ``import _registry`` — probes it with the SAME code ``-20`` uses, observes RED with the
    real ``ModuleNotFoundError``, removes it, and re-measures the same module green.

    It is injected into the extracted tree rather than into ``argus/`` on disk on purpose:
    a committed test must never rewrite the source tree to prove a point.
    """
    dist = _distribution()
    canary = dist.extracted / "argus" / "_story_11_5_canary.py"
    canary_entry = "argus/_story_11_5_canary.py"
    canary.write_text(
        "# Injected by TC-ArgusAgent-RELEASE-001-23; never committed, never shipped.\n"
        "import _registry  # noqa: F401\n",
        encoding="utf-8",
    )
    try:
        broken = _probe_import(dist, canary_entry)
        assert broken.returncode != 0, (
            "a module importing `_registry` at module level imported fine from the "
            "distribution — the probe is not measuring the distribution."
        )
        assert "No module named '_registry'" in broken.stderr, broken.stderr
        assert "PROBE-INVALID" not in broken.stderr, (
            "the failure came from the provenance check, not from the injected defect"
        )
    finally:
        canary.unlink()

    restored = _probe_import(dist, canary_entry)
    assert restored.returncode != 0 and "No module named 'argus._story_11_5_canary'" in (
        restored.stderr
    ), f"the canary survived removal: {restored.stderr}"
    assert _probe_import(dist, "argus/precision/replay_harness.py").returncode == 0


def test_TC_ArgusAgent_RELEASE_001_24_missing_build_tooling_is_named_never_silent() -> None:
    """TC-ArgusAgent-RELEASE-001-24 — AC2.5: no tool, no claim — and the reason is spoken.

    AR10 / NFR-R1: a failure is a typed, named outcome. The one thing this guard must never
    do is pass because it could not look, which is the ``E4`` defect Story 9.2's review
    found on the release workflow — reported ``ok`` for a question it never got to put.
    """
    assert unevaluable_build_tooling(lambda name: True) is None

    missing = unevaluable_build_tooling(lambda name: name != "build")
    assert isinstance(missing, rp.Unevaluable), "a missing front-end must be Unevaluable"
    assert missing.edge_case == "E6"
    assert "build" in missing.reason and "nothing about the BUILT artifact" in missing.reason
    assert "NOT EVALUATED" in str(missing)

    backend = unevaluable_build_tooling(lambda name: name != "flit_core")
    assert isinstance(backend, rp.Unevaluable) and "flit_core" in backend.reason

    # And in THIS environment it is evaluable, so the skip cannot become the normal path.
    assert unevaluable_build_tooling() is None, (
        "the built-artifact guard is skipping in the dev environment; a permanently "
        "skipped guard is a guard nobody runs"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — the published figures are ASSERTED against the live measurement
# ─────────────────────────────────────────────────────────────────────────────

# Every sentence in a published document that states a figure about the built artifact,
# with the live value it must equal. Epic-9's retrospective rule: *where a document states
# a number that a test also pins, either the document cites the pin or a test asserts the
# document.* This is the second half. `README.md:151` and `CHANGELOG.md:397,402` published
# "66 of the 71" for two whole epics while the truth moved to 67 of 72 and nothing was red.
_FIGURE_CLAIMS: tuple[tuple[str, str], ...] = (
    (r"\*\*(?P<value>\d+) of the \d+ shipped modules import", "importable_modules"),
    (r"\*\*\d+ of the (?P<value>\d+) shipped modules import", "shipped_modules"),
    (r"the wheel holds (?P<value>\d+) modules", "shipped_modules"),
    (r"py3-none-any\.whl`, (?P<value>\d+) entries", "wheel_entries"),
    (r"argus_agent-0\.1\.0\.tar\.gz`, (?P<value>\d+) files", "sdist_members"),
)

# The guard that actually holds the distribution claim, named in the documents so a reader
# can go and read it. Asserted to EXIST, so the documents cannot cite a guard that does not.
_DISTRIBUTION_GUARD_ID = "TC-ArgusAgent-RELEASE-001-20"


def _live_figures() -> dict[str, int]:
    dist = _build_distribution()
    return {
        "shipped_modules": len(dist.module_entries),
        "importable_modules": _importable_module_count(),
        "wheel_entries": len(dist.wheel_entries),
        "sdist_members": len(dist.sdist_members),
    }


def test_TC_ArgusAgent_DOCS_001_54_published_module_figures_match_the_built_artifact() -> None:
    """TC-ArgusAgent-DOCS-001-54 — AC3.3/AC3.4: the documents are asserted, not re-typed.

    Both directions, which is the whole point: if the wheel's module count changes and a
    document is not updated this fails, and if a document states a number the artifact does
    not it fails too. Each registered claim must also be PRESENT somewhere, so the way to
    make this test pass can never be to delete the sentence.
    """
    _distribution()
    live = _live_figures()
    texts = {path.name: path.read_text(encoding="utf-8") for path in _FIGURE_DOCUMENTS}

    for pattern, key in _FIGURE_CLAIMS:
        found = 0
        for name, text in texts.items():
            for match in re.finditer(pattern, text):
                found += 1
                assert int(match.group("value")) == live[key], (
                    f"{name} publishes a stale figure for {key!r}: it says "
                    f"{match.group('value')}, the freshly built artifact measures "
                    f"{live[key]}. Fix the document — the artifact is the fact."
                )
        assert found, (
            f"no registered document states the {key!r} figure any more (pattern "
            f"{pattern!r}). A published measurement was deleted rather than corrected."
        )

    # AC3.2 — README named `-11` as what pins the list "in both directions", which was
    # measurably false. It must now name the guard that actually holds it, and that guard
    # must exist.
    readme = texts["README.md"]
    assert _DISTRIBUTION_GUARD_ID in readme, (
        "README.md does not name the guard that holds the distribution claim"
    )
    # The retracted sentence, not the mere mention of `-11`: naming `-11` while explaining
    # what it CANNOT see is the correction, and banning the name would ban the retraction.
    flat = " ".join(readme.split())
    for retracted in (
        "pinned in both directions by `TC-ArgusAgent-RELEASE-001-11`",
        "so this list cannot drift from the code",
    ):
        assert retracted not in flat, (
            f"README.md still publishes the retracted claim {retracted!r}. The source-tree "
            "walk `-11` cannot see whether the BUILT distribution imports — it stayed green "
            "across the entire fix, which is this story's headline finding."
        )
    this_file = Path(__file__).read_text(encoding="utf-8")
    assert f"def test_{_DISTRIBUTION_GUARD_ID.replace('-', '_')}_" in this_file, (
        f"the documents cite {_DISTRIBUTION_GUARD_ID}, which does not exist here"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — the interim-install caveat tracks the real tag state, in both directions
# ─────────────────────────────────────────────────────────────────────────────

_VERSION_PIN = re.compile(r"git\+https://github\.com/[^\s\"']+@v\d+\.\d+\.\d+")
# Three spellings, because the first draft of this guard enumerated two and the closure
# immediately found the third — `README.md`'s pyproject example is caveated with
# "⚠️ Unresolvable until `v0.1.0` exists", which says the same thing in a different word.
# Story 11.3's review learned this the expensive way: assume your first guard is narrower
# than you think.
_CAVEAT_MARKERS: tuple[str, ...] = (
    "does not resolve",
    "tag does not exist",
    "unresolvable",
)
# How far below a pin the caveat may sit and still be read as attached to it. The
# committed caveats sit 1–4 lines below their pin's closing fence.
_CAVEAT_WINDOW = 12


def _released_versions() -> tuple[str, ...] | None:
    """Tags of the form ``vN.N.N``. ``None`` means *could not ask*, never *there are none*."""
    try:
        done = subprocess.run(
            ["git", "tag", "--list", "v*"],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
        )
    except OSError:  # pragma: no cover - git absent
        return None
    if done.returncode != 0:  # pragma: no cover - not a work tree
        return None
    return tuple(
        tag for tag in done.stdout.split() if re.fullmatch(r"v\d+\.\d+\.\d+", tag)
    )


# How the tag state was established, stated ON the surface that leans on it. A caveat that
# says only *that* it holds cannot be checked by the reader it is written for.
_TAG_STATE_EVIDENCE = "`git tag -l` is empty at this commit"

# The workflow's own tag-state claim (Story 12.9 / AC6.2). `release.yml`'s header states it
# is *"COMMITTED AND HAS NEVER EXECUTED"*, which is TRUE at this commit and becomes false the
# moment a tag is pushed — the same rot, in the same two directions, on a surface that is not
# a pin. AC6.2 asked for it to be MECHANISED rather than hand-fixed a second time, so it is
# folded into the one tag-state rule instead of getting a second guard (AR7).
_NEVER_EXECUTED_SURFACE = ".github/workflows/release.yml"
_NEVER_EXECUTED_CLAIM = "COMMITTED AND HAS NEVER EXECUTED"


@dataclass(frozen=True)
class TagStateReport:
    """What the tag-state rule found, plus the two figures that stop it passing over nothing."""

    violations: tuple[str, ...]
    surfaces_with_pins: int
    pins_found: int


def tag_state_violations(texts: dict[str, str], tags: tuple[str, ...]) -> TagStateReport:
    """The tag-state rule, as a PURE function of the surfaces and the tag list.

    WIDENED 2026-08-15 by Story 12.9 / AC4 + DN-6. Both directions are retained VERBATIM from
    Story 11.5's ``-55``; only the population changed, and it became a closure. Pure so the
    tag-present direction can be exercised through this seam — **a guard is never tested by
    creating a real tag** (Story 12.9 / AC9 fences that act).

    The rule, unchanged: while no ``v*.*.*`` tag exists every pinned VCS install command must
    carry a caveat saying it does not resolve, and the surface must say HOW that was
    established; the moment a tag exists every such caveat is the NEW falsehood and must be
    removed deliberately rather than shipped stale.
    """
    violations: list[str] = []
    surfaces_with_pins = 0
    pins_found = 0

    for rel, text in sorted(texts.items()):
        lines = text.splitlines()
        pins = [i for i, line in enumerate(lines) if _VERSION_PIN.search(line)]
        if not pins:
            continue
        surfaces_with_pins += 1
        pins_found += len(pins)

        for index in pins:
            window = " ".join(lines[index : index + _CAVEAT_WINDOW]).lower()
            caveated = any(marker in window for marker in _CAVEAT_MARKERS)
            if tags and caveated:
                violations.append(
                    f"{rel}:{index + 1} still says the pinned install does not resolve, but "
                    f"{sorted(tags)} exist(s). The caveat is now the falsehood — remove it."
                )
            elif not tags and not caveated:
                violations.append(
                    f"{rel}:{index + 1} publishes `{lines[index].strip()}` with no caveat "
                    f"within {_CAVEAT_WINDOW} lines, and `git tag -l` lists no v*.*.* tag, "
                    "so that command cannot resolve for any reader."
                )
        if not tags and _TAG_STATE_EVIDENCE not in text:
            violations.append(
                f"{rel} carries {len(pins)} tag-pinned install command(s) but never states "
                f"HOW the tag state was established ({_TAG_STATE_EVIDENCE!r}). A caveat that "
                "says only THAT it holds cannot be checked by the reader it is written for."
            )

    workflow = texts.get(_NEVER_EXECUTED_SURFACE)
    if workflow is not None:
        claimed = _NEVER_EXECUTED_CLAIM in workflow
        if tags and claimed:
            violations.append(
                f"{_NEVER_EXECUTED_SURFACE} still states it is {_NEVER_EXECUTED_CLAIM!r} "
                f"while {sorted(tags)} exist(s) — the tag triggers this workflow, so that "
                "sentence is now the falsehood. Correct it in the same change that "
                "falsified it (Story 12.9 / AC6.2)."
            )
        elif not tags and not claimed:
            violations.append(
                f"{_NEVER_EXECUTED_SURFACE} no longer states that it is "
                f"{_NEVER_EXECUTED_CLAIM!r} while `git tag -l` is still empty. A workflow "
                "that has never run and does not say so reads as one that has."
            )

    return TagStateReport(tuple(violations), surfaces_with_pins, pins_found)


def _release_surface_texts() -> dict[str, str]:
    """Every registered release surface's text — the CLOSURE the rule runs over.

    Imported from the registry that owns it rather than hard-coded, which is the entire
    correction: a FIFTH pin on a FOURTH surface is covered here with no edit.
    """
    from tests.test_release_surface_honesty import _RELEASE_SURFACES

    return {
        rel: (_REPO_ROOT / rel).read_text(encoding="utf-8")
        for rel in _RELEASE_SURFACES
        if (_REPO_ROOT / rel).is_file()
    }


def test_TC_ArgusAgent_DOCS_001_55_the_interim_install_caveat_tracks_the_real_tag_state() -> None:
    """TC-ArgusAgent-DOCS-001-55 — AC4.2 / Story 12.9 AC4: mechanised, and now over ALL of them.

    Story 10.x corrected this sentence by hand. A hand correction is true for exactly as
    long as nobody changes the world it describes — and the day an operator pushes
    ``v0.1.0`` the caveat becomes a NEW falsehood, published by the fix that made the old
    one true. So: while no ``v*.*.*`` tag exists every pinned VCS install command must
    carry the caveat; the moment one exists this goes RED so the caveat is removed
    deliberately rather than shipped stale.

    ⚠️ **WIDENED 2026-08-15 by Story 12.9 / AC4, and recorded here rather than fixed
    quietly.** As written this test read ``_README`` **and nothing else** — while the pin
    appears on THREE tracked consumer surfaces: ``README.md`` (3 pins), ``CHANGELOG.md`` (2)
    and ``docs/first-run.md`` (1, added by **Story 12.8, after this guard was written**).
    So the transition it was built to make safe would have turned it RED for README's pins —
    correct and intended — while three further caveats on two other surfaces silently became
    published falsehoods. That is 11.5's own stated failure mode, reopened by a file it could
    not have known about, and it is exactly what 12.8 left pointed at Story 12.9.

    The population is now a CLOSURE over the registered release surfaces with both
    non-vacuity floors, so a fifth pin on a fourth surface is covered with **no edit** here.
    ``-55b`` exercises both directions through the pure seam, without creating a tag.
    """
    tags = _released_versions()
    if tags is None:  # pragma: no cover - environment without git
        pytest.skip(
            str(
                rp.Unevaluable(
                    "E2",
                    "`git tag --list` could not be run, so the tag state is unknown and "
                    "the interim-install caveats were NOT checked.",
                )
            )
        )

    report = tag_state_violations(_release_surface_texts(), tags)

    # NON-VACUITY, both floors (E.3). Without these the rule is satisfied by a corpus that
    # shows no install command at all — which is how a guard stops guarding by attrition.
    assert report.surfaces_with_pins > 0, (
        "no registered release surface shows a tag-pinned VCS install command any more. "
        "Either the documented install route was deleted rather than corrected, or the pin "
        "pattern stopped matching it — and either way this guard is holding nothing."
    )
    assert report.pins_found > 0, "the pin closure found zero pins"

    assert not report.violations, "\n".join(report.violations)


def test_TC_ArgusAgent_DOCS_001_55b_the_tag_state_rule_bites_in_both_directions() -> None:
    """TC-ArgusAgent-DOCS-001-55b — Story 12.9 / AC4: the positive control, through the seam.

    OBSERVABLE: what :func:`tag_state_violations` reports for the REAL surface texts under a
    simulated tag state.

    Both directions are exercised on the committed corpus, because both are branches that
    only run "once the tag exists" — the never-executed-branch class this project has now
    recorded FOUR times. The tag state is simulated through the function's own parameter;
    **no real tag is created**, which is Story 12.9 / AC9's fence and also the only honest
    way to test a guard about tags.
    """
    texts = _release_surface_texts()

    # Direction 1 — no tag, a caveat DELETED. Today that deletion is invisible on
    # CHANGELOG.md and docs/first-run.md; that invisibility is the defect this widening
    # closes, so it is demonstrated on those two files specifically.
    for rel in ("CHANGELOG.md", "docs/first-run.md"):
        assert rel in texts, f"{rel} is not a registered release surface any more"
        stripped = dict(texts)
        text = stripped[rel]
        for marker in ("does not resolve", "Unresolvable", "does not resolve yet"):
            text = re.sub(marker, "resolves", text, flags=re.IGNORECASE)
        stripped[rel] = text
        report = tag_state_violations(stripped, ())
        assert any(rel in violation for violation in report.violations), (
            f"deleting the interim caveat from {rel} was INVISIBLE to the tag-state rule. "
            "That is precisely the hole Story 12.9 / AC4 closes: `-55` read README.md only, "
            f"and {rel} carries a pin it could not see."
        )

    # Direction 2 — the tag EXISTS. Every caveat now on disk is the falsehood, and the
    # workflow's "HAS NEVER EXECUTED" header is one too. The transition must be reported for
    # EVERY pin-carrying surface, not just the first.
    released = tag_state_violations(texts, ("v0.1.0",))
    assert released.violations, (
        "with `v0.1.0` present, not one of the caveats on disk was reported as a falsehood. "
        "The tag that makes the documented install command true makes every 'does not "
        "resolve' sentence false, and a guard that misses that ships the lie."
    )
    flagged = {violation.split(":")[0].split(" ")[0] for violation in released.violations}
    for rel in ("README.md", "CHANGELOG.md", "docs/first-run.md"):
        assert any(rel in violation for violation in released.violations), (
            f"{rel} carries a pin with a caveat and was NOT reported when the tag exists; "
            f"reported surfaces were {sorted(flagged)}"
        )
    assert any(_NEVER_EXECUTED_SURFACE in v for v in released.violations), (
        f"{_NEVER_EXECUTED_SURFACE} still claims it has never executed while a tag exists, "
        "and the rule did not say so. AC6.2 requires that header to be corrected in the same "
        "change that falsifies it."
    )

    # And the honest states are NOT flagged, in both directions — otherwise this rule could
    # never be satisfied and would be deleted by the third person to hit it.
    assert not tag_state_violations(texts, ()).violations
    no_caveats = {
        rel: re.sub(
            r"does not resolve|unresolvable|tag does not exist",
            "resolves",
            text,
            flags=re.IGNORECASE,
        ).replace(_NEVER_EXECUTED_CLAIM, "has now executed")
        for rel, text in texts.items()
    }
    assert not tag_state_violations(no_caveats, ("v0.1.0",)).violations, (
        "with the tag present and every caveat removed the rule still objects, so the "
        "post-release state it demands is unreachable: "
        f"{tag_state_violations(no_caveats, ('v0.1.0',)).violations}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — a documented command the distribution does not ship is MARKED, never implied
# ─────────────────────────────────────────────────────────────────────────────

_SLASH_COMMAND = re.compile(r"^/audit\b", re.MULTILINE)
_FORTHCOMING_MARKER = "FORTHCOMING"
_FORTHCOMING_OWNER = "Story 12.7"


def test_TC_ArgusAgent_DOCS_001_56_documented_commands_are_marked_until_they_ship() -> None:
    """TC-ArgusAgent-DOCS-001-56 — AC5.2: the docs never describe a capability the wheel lacks.

    README said *"When installed, `ArgusAgent` registers slash commands in your AI coding
    assistant"* and then listed seven of them. Measured: ``pyproject.toml`` ships three
    console aliases, all three pointing at ``argus.cli:main``, and the wheel carries ZERO
    data assets — there is no registration mechanism and no command asset in the
    distribution at all.

    Both directions, and the second one is the point: when Story 12.7 / FR35 actually ships
    a mechanism, this test goes RED until the marker is REMOVED. The marker cannot outlive
    the gap it describes.

    ⚠️ **CORRECTED 2026-08-15 by Story 12.7, and recorded here rather than fixed quietly.**
    The ``mechanism_ships`` branch below had **NEVER EXECUTED** — it carried
    ``# pragma: no cover - true only once 12.7 delivers`` — and as written it asserted one
    thing (*"the marker is gone"*) and then ``return``ed, **skipping every remaining
    assertion in the test**. So the moment this story shipped its first asset, the guard
    that exists to hold the documented set to the shipped set would have stopped holding
    anything at all: a reader could have satisfied it by DELETING the ``/audit`` lines from
    the README, which is the opposite of a delivery. That is precisely the never-executed
    branch class Epic 12 has now recorded three times — ``-49``'s registered-surface loop,
    ``_ENTRY_POINT``'s prose, and this. It was written in good faith for a delivery nobody
    could see yet, and it was wrong about the one thing that mattered.

    The corrected delivered branch is a REPLACEMENT, never a relaxation. It asserts:

    1. the FORTHCOMING marker is gone (the original assertion, kept);
    2. **set equality (AC4)** between the shipped asset tree and what README publishes,
       in BOTH directions — derived, in ONE place, by importing
       ``tests/test_command_assets.py``'s helpers rather than re-implementing the
       derivation here, because a rule implemented twice drifts in one of the two (AR7);
    3. a **non-vacuity floor**: the shipped set and the published set must each be
       non-empty, so this can never pass over nothing;

    and it does **not** return early — the alias closure above it and the assertions below
    run in both states.
    """
    dist = _distribution()
    readme = _README.read_text(encoding="utf-8")

    aliases = console_script_aliases()

    # What README claims it installs must be what pyproject declares — a closure, so a
    # fourth alias (or a renamed one) fails here rather than drifting quietly.
    for alias, target in aliases.items():
        assert f"`{alias}`" in readme, f"console alias {alias!r} is undocumented in README"
        assert target in readme, f"README does not state that {alias!r} runs {target!r}"

    mechanism_ships = bool(dist.data_assets)
    if mechanism_ships:
        # DELIVERED (Story 12.7 / FR35). The marker is gone AND the sets are equal.
        from tests.test_command_assets import published_commands, shipped_command_spellings

        assert _FORTHCOMING_MARKER not in readme, (
            f"the distribution now ships command assets {sorted(dist.data_assets)}, so the "
            "FORTHCOMING marker is stale — remove it (Story 12.7 / FR35 delivered)."
        )
        shipped = shipped_command_spellings()
        published = published_commands(readme)
        # NON-VACUITY FLOOR (E.3). Without these two lines the equality below is satisfied by
        # a README that documents nothing and a distribution that ships nothing — which is
        # exactly how the uncorrected branch could have been "passed".
        assert shipped, (
            "the distribution ships data assets but NO command spelling could be derived from "
            "the asset tree and the host registry. The equality below would be vacuous."
        )
        assert published, (
            "README publishes no command at all while the wheel ships command assets. Deleting "
            "the documented commands is NOT how this guard is satisfied — that would ship a "
            "capability no reader can find."
        )
        assert published == shipped, (
            "README and the shipped command-asset tree disagree.\n"
            f"  published but NOT shipped: {sorted(published - shipped)}\n"
            f"  shipped but NOT published: {sorted(shipped - published)}\n"
            "A documented command that is not delivered is removed in the same change (AC4); "
            "a shipped command nobody documents is one a reader can never find. "
            "tests/test_command_assets.py::TC-ArgusAgent-ASSETS-001-06 holds the same equality "
            "over EVERY publishing surface — this is the README half, kept here because this "
            "is the guard that was measuring the gap."
        )
        return

    commands = _SLASH_COMMAND.findall(readme)  # pragma: no cover - the pre-12.7 state
    assert commands, "README documents no /audit command; the guard has nothing to hold"

    # Every documented command must sit under the marker, in its own section.
    lines = readme.splitlines()
    headings = [i for i, line in enumerate(lines) if line.startswith("#")]
    for i, line in enumerate(lines):
        if not _SLASH_COMMAND.match(line):
            continue
        start = max((h for h in headings if h < i), default=0)
        section = "\n".join(lines[start:i])
        assert _FORTHCOMING_MARKER in section and _FORTHCOMING_OWNER in section, (
            f"README line {i + 1} documents `{line.strip()}` with no {_FORTHCOMING_MARKER} "
            f"marker and no {_FORTHCOMING_OWNER} reference above it in its section, while "
            "the built wheel ships no command asset and pyproject.toml ships no "
            "registration mechanism. A reader would install this and find nothing."
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — the bare-word "Minions" subject claims, classified one by one
# ─────────────────────────────────────────────────────────────────────────────

_BARE_MINIONS = re.compile(r"(?<![A-Za-z_])Minions(?![A-Za-z_])")

# AC6.1 — all 21 measured occurrences, classified with a reason. NINETEEN are
# TRUE-HISTORICAL and stay: each records where a design, a constant or a containment rule
# came FROM, and deleting that provenance would make the module less true, not more. TWO
# were FALSE-SUBJECT claims about what Argus does TODAY and were rewritten (below).
# No blanket find-and-replace: this table is why.
_TRUE_HISTORICAL_SITES: dict[str, tuple[tuple[str, str], ...]] = {
    "argus/__init__.py": (
        (
            "with no Minions package present",
            "KEEP — a NEGATIVE claim about the dependency graph, and it is true.",
        ),
    ),
    "argus/audit/deep_audit.py": (
        (
            "wired into the Minions product run path",
            "KEEP — states where the module is NOT wired; historical boundary.",
        ),
        (
            "nothing in Minions orchestration",
            "KEEP — the other half of the same negative boundary claim.",
        ),
    ),
    "argus/audit/minions_llm_adapter.py": (
        (
            "Backward-compatible Minions LLM Adapter wrapper",
            "KEEP — names the upstream interface this shim is compatible WITH.",
        ),
    ),
    "argus/cost/__init__.py": (
        (
            "reusing the Minions",
            "KEEP — AR7 reuse provenance for the account_spend fold.",
        ),
    ),
    "argus/cost/budget_governor.py": (
        (
            "UPSTREAM Minions cost-guardrails module ACROSS a product boundary",
            "KEEP — the reuse target this module wraps; unit 2, zero lines spent.",
        ),
        (
            "Story 3.1 required wrapping the UPSTREAM Minions cost-guardrails module",
            "KEEP — dated historical requirement, true as written.",
        ),
        (
            "Minions stayed the ONE hard-ceiling authority",
            "KEEP — past tense, describes the Story-3.1 arrangement.",
        ),
    ),
    "argus/dogfood/proof_render.py": (
        (
            "The independent Story-7.2 run over the Minions",
            "KEEP — the run really was over Minions; that is what makes it independent.",
        ),
    ),
    "argus/dogfood/proof_run.py": (
        (
            "Story 7.2 originally ran it over the Minions platform",
            "KEEP — explicitly past tense and explicitly superseded. Also byte-fenced "
            "by AC1.5 and in unit 2, so a rewrite would spend budget to make it worse.",
        ),
    ),
    "argus/evidence/__init__.py": (
        (
            "SEPARATE from the Minions",
            "KEEP — a separation claim; the subject is the separation, not the corpus.",
        ),
    ),
    "argus/evidence/bundle.py": (
        (
            "Separateness from the Minions governance bundle",
            "KEEP — names the artifact this one is deliberately NOT; unit 2, free.",
        ),
        (
            "a DIFFERENT artifact from Minions'",
            "KEEP — same separation claim, restated for the reader of the class.",
        ),
    ),
    "argus/index/partitioner.py": (
        (
            "the 18-2 Minions ``is_relative_to``-not-``startswith`` precedent",
            "KEEP — a citation of where the rule came from; unit 2, free.",
        ),
    ),
    "argus/store/__init__.py": (
        (
            "the Minions ``WorkspaceContainmentError`` containment logic",
            "KEEP — names the imported authority, which is the AR7 point.",
        ),
    ),
    "argus/store/paths.py": (
        (
            "REUSE Minions' canonical containment authority by import",
            "KEEP — AR7 reuse provenance for a SECURITY control.",
        ),
        (
            "The architecture mandates reuse of Minions'",
            "KEEP — restates the architectural mandate this module obeys.",
        ),
        (
            "mirror of the Minions helper",
            "KEEP — tells a maintainer which upstream helper to diff against.",
        ),
    ),
    "argus/store/writer.py": (
        (
            "the Minions ``WorkspaceContainmentError``",
            "KEEP — same imported containment authority.",
        ),
    ),
    # The two occurrences that survive in this file are NOT the disclosure any more. They
    # are the correction record itself: it cites the two modules whose true-historical
    # claims make the old subject false. Deleting them would delete the evidence.
    "argus/verdict/negative_assurance.py": (
        (
            "`argus/dogfood/proof_run.py` records that the Minions",
            "KEEP — cites the superseded Story-7.2 run that the old subject leaned on.",
        ),
        (
            'Minions package present". A false SUBJECT',
            "KEEP — cites argus/__init__.py's negative dependency claim.",
        ),
    ),
}

# The TWO false-subject claims, and what replaced them. Both are printed on a user's
# terminal by `argus audit .` today via the FR34 instrument disclosure, which makes them
# the highest-visibility sentences Argus has. "the Minions dogfood corpus" was false and
# the sentence contradicted itself four words later ("a self-audit of THIS repository");
# argus/dogfood/proof_run.py records that the Minions run was Story 7.2's and superseded,
# and argus/__init__.py states Argus runs "with no Minions package present". The SUBJECT is
# corrected; the claim, the status vocabulary and the removal condition are untouched.
_REWRITTEN_FALSE_SUBJECT_SITES: dict[str, tuple[tuple[str, str], ...]] = {
    "argus/verdict/negative_assurance.py": (
        (
            "rest on the Minions dogfood corpus, a self-audit of this ",
            "rest on the Argus dogfood corpus, a self-audit of this ",
        ),
        (
            "Minions dogfood corpus. The corpus and the adjudication",
            "Argus dogfood corpus. The corpus and the adjudication",
        ),
    ),
}


def _tracked_argus_modules() -> tuple[str, ...]:
    done = subprocess.run(
        ["git", "ls-files", "--", "argus"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, f"`git ls-files -- argus` failed: {done.stderr}"
    return tuple(p for p in done.stdout.split() if p.endswith(".py"))


def test_TC_ArgusAgent_DOCS_001_57_every_minions_claim_in_the_package_is_classified() -> None:
    """TC-ArgusAgent-DOCS-001-57 — AC6.1/AC6.3: a closure over the tree, not a list.

    The epic's premise said 22 occurrences across 14 modules and the ledger said 25; the
    measured truth was 21 across 14. This project has hand-counted wrong six times, so the
    contract is the regex over ``git ls-files -- argus``, never the table. A NEW bare-word
    occurrence fails until somebody reads it and classifies it, which is the only step that
    can tell a historical provenance note from a false claim about what Argus is.
    """
    measured: dict[str, int] = {}
    for rel in _tracked_argus_modules():
        hits = len(_BARE_MINIONS.findall((_REPO_ROOT / rel).read_text(encoding="utf-8")))
        if hits:
            measured[rel] = hits

    unclassified = sorted(set(measured) - set(_TRUE_HISTORICAL_SITES))
    assert not unclassified, (
        f"module(s) carry an unclassified bare-word 'Minions' subject claim: {unclassified}. "
        "Read each occurrence and record it as true-historical or false-subject in "
        "_TRUE_HISTORICAL_SITES — a blanket replace is banned precisely because the two "
        "classes read identically to a regex."
    )
    vanished = sorted(set(_TRUE_HISTORICAL_SITES) - set(measured))
    assert not vanished, (
        f"classified provenance disappeared from {vanished}. If it was removed on purpose, "
        "remove it from the table too, so the table never describes a tree that is gone."
    )
    for rel, entries in _TRUE_HISTORICAL_SITES.items():
        assert measured[rel] == len(entries), (
            f"{rel} carries {measured[rel]} bare-word occurrence(s) but "
            f"{len(entries)} are classified"
        )
        text = (_REPO_ROOT / rel).read_text(encoding="utf-8")
        for snippet, reason in entries:
            assert snippet in text, f"{rel}: classified snippet is not in the file: {snippet!r}"
            assert reason.startswith("KEEP — "), f"{rel}: {snippet!r} has no recorded reason"

    for rel, corrections in _REWRITTEN_FALSE_SUBJECT_SITES.items():
        text = (_REPO_ROOT / rel).read_text(encoding="utf-8")
        for was, now in corrections:
            assert was not in text, f"{rel}: the FALSE SUBJECT came back: {was!r}"
            assert now in text, f"{rel}: the corrected text is missing: {now!r}"


def test_TC_ArgusAgent_DOCS_001_58_the_instrument_disclosure_names_the_corpus_it_rests_on() -> None:
    """TC-ArgusAgent-DOCS-001-58 — AC6.2: a SUBJECT was corrected; no claim was changed.

    The disclosure is Story 11.1's FR34 surface and is single-sourced — README.md,
    CHANGELOG.md, pyproject.toml and action.yml are compared against these constants by
    tests/test_instrument_disclosure.py. This asserts the part that guard cannot: that the
    corpus is named correctly, and that correcting the name did not quietly weaken the
    status vocabulary, the negation, or what removes the notice.
    """
    from argus.verdict.negative_assurance import (
        INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED,
        INSTRUMENT_DISCLOSURE_SHORT_NOT_INDEPENDENTLY_VALIDATED,
        INSTRUMENT_DISCLOSURE_VALIDATED,
        InstrumentStatus,
    )

    for text in (
        INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED,
        INSTRUMENT_DISCLOSURE_VALIDATED,
    ):
        assert not _BARE_MINIONS.findall(text), f"false subject restored: {text}"
        assert "Argus dogfood corpus" in text

    # The claim, unchanged: the negation still precedes the banned phrase, the self-audit
    # framing survives, and Epic 13 is still the only thing that removes the notice.
    current = INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED
    assert "has not been independently validated" in current
    assert "a self-audit of this repository" in current
    assert "no human true-positive/false-positive adjudication" in current
    assert "removed only when Epic 13's human adjudication" in current
    assert "nothing else removes it" in current
    assert INSTRUMENT_DISCLOSURE_SHORT_NOT_INDEPENDENTLY_VALIDATED in current
    assert [status.value for status in InstrumentStatus] == [
        "not-independently-validated",
        "validated",
    ], "the two-member InstrumentStatus vocabulary is Epic 13's, not this story's"
