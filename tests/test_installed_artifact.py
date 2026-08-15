"""Story 12.9 / AC1 — the artifact is PROVEN by USING it, from an INSTALLED distribution.

Verification area ``ArgusAgent-RELEASE`` (``TC-ArgusAgent-RELEASE-001-25``..``-28``,
CONTINUING the index that ended at ``-24`` in ``tests/test_built_distribution.py``).

**Why this file exists, and why it is a separate file.** ``CHANGELOG.md`` already PUBLISHED
this claim — *"the wheel was installed into a fresh virtualenv with the repository absent
from ``sys.path``, and ``argus --help`` and ``argus audit <fixture-repo>`` both ran to
completion there"* — and **no committed guard held it**. It was true by hand on 2026-08-08.
Since then the distribution gained ``argus-mcp`` (12.6), three packaged command assets
(12.7), nine grammar dependencies (12.5) and a changed exit-code contract (12.8). *A
published claim with no test is what this repository files as a defect*, and this one is the
front-door claim of the release. It is a separate module rather than an extension of
``tests/test_built_distribution.py`` because that file is at **992** of NFR-M1's 1200 lines
and this is a different seam — that one measures the ARCHIVE, this one measures an
INSTALLED ENVIRONMENT — so the split is by cohesion, which is 12.7/12.8's recorded remedy.
It **reuses** that module's build (one build per session, ``functools.lru_cache``) and its
``[project.scripts]`` closure rather than repeating either.

**What ``-20`` cannot see, which is the whole reason for this file.** ``-20`` EXTRACTS the
wheel and prepends the extraction directory to ``sys.path``. That never generates a
console-script shim, never unpacks packaged data through an installer, and never runs an
entry point — so it is structurally blind to a broken/renamed entry point, a missing asset
and a packaging error. Story 11.5's own headline finding is that a guard one level away
from the claim is vacuous about it.

**How the fresh environment is built, and what it does and does NOT test.** The test
contract is *offline, deterministic, no network*, so a plain ``pip install dist/*.whl`` —
which would resolve fourteen dependencies from the network — is not available, and this
repository's ``.venv`` has **no ``pip``** at all (it is ``uv``-managed). So:

1. ``python -m venv --without-pip`` creates an EMPTY environment;
2. ``uv pip install --no-deps <wheel>`` installs the DISTRIBUTION into it, which is what
   generates the console-script shims and unpacks the packaged assets;
3. one ``.pth`` file adds THIS interpreter's ``site-packages`` so the fourteen dependencies
   resolve from what is already on the machine.

**It therefore does not test dependency resolution**, and that is stated here rather than
implied. It tests exactly what AC1 asserts: entry points, packaged data, module layout, and
the artifact answering real invocations. ``--system-site-packages`` was tried first and
REJECTED by measurement: a venv created from ``.venv`` inherits the BASE installation's
``site-packages``, not ``.venv``'s, so the dependencies were absent — and the option also
drags in whatever ``.pth`` files that installation carries. One explicit path entry is the
narrower, more honest instrument.

**The provenance assertion is non-negotiable, and it is not theoretical here.** This
repository is installed EDITABLE into its own ``.venv`` (``argus.pth`` points at the repo
root), and while building this guard the naive route was measured resolving ``argus`` **from
the repository** while reporting success. So every probe asserts ``argus.__file__`` lives
inside the fresh environment and REFUSES with ``PROBE-INVALID`` otherwise — the refusal
``TC-ArgusAgent-RELEASE-001-21`` established, reused rather than re-invented (AR7).
``-28`` is the positive control for it.

Where the environment cannot be built the guard reports :class:`release_preflight.Unevaluable`
with a NAMED reason and skips — it never passes silently (AR10 / NFR-R1).

**Nothing here publishes, pushes, tags or uploads.** Everything is built into a temporary
directory outside the repository (Story 12.9 / AC8).
"""

from __future__ import annotations

import functools
import json
import os
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import release_preflight as rp  # noqa: E402

from argus.verdict.verdict_gate import Verdict, exit_code_for_verdict  # noqa: E402
from tests.cartridges._cartridge import stage_cartridge  # noqa: E402
from tests.test_built_distribution import (  # noqa: E402
    _build_distribution,
    console_script_aliases,
    unevaluable_build_tooling,
)

# The CLI entry target. Every alias pointing HERE is exercised with `--help`; an alias
# pointing anywhere else must have a registered exerciser below, and an unregistered target
# RAISES rather than being skipped (DF-10-4-E: an exhaustive dispatch raises on an
# unregistered member). That is what makes a FIFTH alias covered with no edit when it reuses
# a known target, and RED — not invisible — when it introduces a new one.
_CLI_TARGET = "argus.cli:main"
_MCP_TARGET = "argus.mcp.server:main"

# AC1's non-vacuity floor, stated as a number rather than implied: `[project.scripts]` held
# FOUR aliases when this was written and a fifth must be covered with no edit. The floor
# stops the closure from passing over an empty or mis-parsed table.
_MINIMUM_ALIASES = 4

_FIXTURE_CARTRIDGE = "vacuous_basic"

# `verdict=<TOKEN> deep_ratio=<num>/<den> blocking_findings=<n>` — the FR18 machine contract
# a consumer parses. Asserted as a SHAPE, with the token checked against the live `Verdict`
# enum, so a renamed verdict turns this red rather than leaving a published parser stale.
_SUMMARY_LINE = re.compile(
    r"^verdict=(?P<verdict>\S+) deep_ratio=(?P<num>\d+)/(?P<den>\d+) "
    r"blocking_findings=(?P<blocking>\d+)\b"
)

_PROVENANCE_PROBE = """
import os, sys
import argus
_where = os.path.normcase(os.path.abspath(argus.__file__))
_env = os.path.normcase(os.path.abspath({env_root!r}))
if not _where.startswith(_env):
    raise SystemExit(
        "PROBE-INVALID: argus resolved from " + _where + ", which is NOT inside the fresh "
        "environment at " + _env
    )
print(_where)
"""


@dataclass(frozen=True)
class InstalledArtifact:
    """A fresh environment with the freshly built wheel really installed into it."""

    root: Path
    python: Path
    script_dir: Path
    outside_cwd: Path

    def script(self, alias: str) -> Path | None:
        """The shim *alias* resolves to inside this environment, or ``None``.

        Resolved by looking in the environment's OWN script directory rather than by
        consulting ``PATH``: a shim found on ``PATH`` could be the repository's editable
        install, which is the exact false pass this whole module is written against.
        """
        for suffix in (".exe", ".cmd", ""):
            candidate = self.script_dir / f"{alias}{suffix}"
            if candidate.is_file():
                return candidate
        return None


def unevaluable_install_tooling(
    is_available: "object | None" = None,
) -> rp.Unevaluable | None:
    """Why the installed-artifact guard cannot run here, as a NAMED outcome — or ``None``.

    Injectable so ``-28`` can prove the missing-tool path produces a named refusal to
    evaluate rather than a silent pass. The vocabulary is
    :class:`release_preflight.Unevaluable` reused rather than forked (AR7): E6 is the
    enumerated release case about the built artifacts, and "could not install them at all"
    is that case being unobservable, not that case clearing.
    """
    probe = is_available if is_available is not None else shutil.which
    if probe("uv") is None:  # type: ignore[operator]
        return rp.Unevaluable(
            "E6",
            "`uv` is not on PATH, so the wheel could NOT be installed into a fresh "
            "environment and nothing about the INSTALLED distribution was checked. This "
            "repository's own .venv carries no `pip` (it is uv-managed, uv.lock is "
            "committed), so `uv pip install --no-deps` is the offline install route. "
            "Install uv, or run this guard where the release workflow runs it.",
        )
    return None


@functools.lru_cache(maxsize=1)
def _install_distribution() -> InstalledArtifact:
    """Install the freshly built wheel into a NEW environment. Once per session.

    Deliberately reuses ``tests/test_built_distribution._build_distribution`` — one build per
    session, and the artifact this proves is the artifact that module measures. Building a
    second time would be a second artifact, which is a fork of the thing under test.
    """
    dist = _build_distribution()
    root = Path(tempfile.mkdtemp(prefix="argus-env-"))

    # `--without-pip` skips `ensurepip`, which FAILS outright on this uv-managed
    # interpreter. Measured, not assumed: the default invocation errors while still leaving
    # a half-built environment behind, which is a worse starting point than an explicit one.
    created = subprocess.run(
        [sys.executable, "-m", "venv", "--without-pip", str(root)],
        capture_output=True,
        text=True,
    )
    assert created.returncode == 0, (
        f"could not create a fresh environment, so NOTHING about the installed "
        f"distribution was verified. stderr:\n{created.stderr}"
    )

    script_dir = root / ("Scripts" if os.name == "nt" else "bin")
    python = script_dir / ("python.exe" if os.name == "nt" else "python")
    assert python.is_file(), f"the fresh environment has no interpreter at {python}"

    installed = subprocess.run(
        ["uv", "pip", "install", "--no-deps", "--python", str(python), str(dist.wheel)],
        capture_output=True,
        text=True,
    )
    assert installed.returncode == 0, (
        "`uv pip install --no-deps` failed, so the distribution is NOT installed and "
        f"nothing was verified. stdout:\n{installed.stdout}\nstderr:\n{installed.stderr}"
    )

    # The dependencies, from what is already on this machine. NOT a network resolve, and
    # NOT the repository: `purelib` is this interpreter's site-packages, which carries the
    # fourteen runtime dependencies. A `.pth` path entry is NOT recursively site-processed,
    # so the editable `argus.pth` living there is NOT executed and the repository never
    # reaches `sys.path` — which the provenance probe then proves rather than assumes.
    site_packages = _environment_site_packages(root)
    (site_packages / "_argus_release_probe_deps.pth").write_text(
        sysconfig.get_paths()["purelib"] + "\n", encoding="utf-8"
    )

    return InstalledArtifact(
        root=root,
        python=python,
        script_dir=script_dir,
        outside_cwd=Path(tempfile.mkdtemp(prefix="argus-env-cwd-")),
    )


def _environment_site_packages(root: Path) -> Path:
    candidates = sorted(root.glob("**/site-packages"))
    assert candidates, f"the fresh environment at {root} has no site-packages directory"
    return candidates[0]


def _artifact() -> InstalledArtifact:
    """The installed artifact, or a SKIP carrying the named reason it is unavailable."""
    for unevaluable in (unevaluable_build_tooling(), unevaluable_install_tooling()):
        if unevaluable is not None:
            pytest.skip(str(unevaluable))
    return _install_distribution()


def _clean_env(**extra: str) -> dict[str, str]:
    environ = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    environ["PYTHONDONTWRITEBYTECODE"] = "1"
    environ["PYTHONIOENCODING"] = "utf-8"
    environ.update(extra)
    return environ


def _run(
    artifact: InstalledArtifact,
    command: list[str],
    *,
    stdin: str | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 300,
) -> subprocess.CompletedProcess[str]:
    """Run *command* from OUTSIDE the repository, with a clean environment."""
    return subprocess.run(
        command,
        cwd=str(artifact.outside_cwd),
        env=env if env is not None else _clean_env(),
        input=stdin,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def _resolved_argus(
    artifact: InstalledArtifact, *, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Where the fresh environment's own interpreter resolves ``argus`` from."""
    return _run(
        artifact,
        [str(artifact.python), "-c", _PROVENANCE_PROBE.format(env_root=str(artifact.root))],
        env=env,
    )


def _assert_provenance(artifact: InstalledArtifact) -> None:
    """REFUSE unless ``argus`` resolves inside the fresh environment. Never assume it."""
    probe = _resolved_argus(artifact)
    assert probe.returncode == 0, (
        "the fresh environment does not resolve `argus` from inside itself, so every "
        f"measurement below would be about the wrong tree:\n{probe.stderr}"
    )


def _inside(root: Path, candidate: str) -> bool:
    """Is *candidate* a path inside *root*? Case-folded the way the probe reports them.

    The probe prints ``os.path.normcase(os.path.abspath(...))``, which lower-cases on
    Windows. A raw substring test against ``str(root)`` therefore fails on a correct answer
    — measured, not imagined: it failed here first — and "the provenance assertion is
    failing for a spelling reason" is indistinguishable from "the artifact is wrong" unless
    both sides are normalised the same way.
    """
    return os.path.normcase(os.path.abspath(candidate.strip())).startswith(
        os.path.normcase(os.path.abspath(str(root)))
    )


def _jsonrpc(*messages: dict[str, object]) -> str:
    """Line-delimited JSON-RPC, the framing ``argus-mcp`` speaks over stdio."""
    return "".join(json.dumps(message) + "\n" for message in messages)


# ─────────────────────────────────────────────────────────────────────────────
# AC1.1 / AC1.2 — every console script, by closure, from the installed environment
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_RELEASE_001_25_every_console_script_resolves_and_runs() -> None:
    """TC-ArgusAgent-RELEASE-001-25 — Story 12.9 / AC1.1: the entry points are EXERCISED.

    OBSERVABLE: whether each ``[project.scripts]`` alias exists as a shim in the fresh
    environment and answers a real invocation there.

    The population is a CLOSURE over the ``[project.scripts]`` table — never a hand list.
    ``_CONSOLE_SCRIPTS`` / ``_ENTRY_POINT`` is the recognizer-that-stopped-recognizing defect
    class this project has recorded FOUR times (12.6 twice, 12.7, and ``-56``'s
    never-executed branch), so a fifth alias is covered here with no edit, and a fifth alias
    with a NEW target raises rather than being skipped.
    """
    artifact = _artifact()
    _assert_provenance(artifact)

    aliases = console_script_aliases()
    assert len(aliases) >= _MINIMUM_ALIASES, (
        f"the [project.scripts] closure parsed {len(aliases)} alias(es) and the table held "
        f"at least {_MINIMUM_ALIASES} when this guard was written. Either an entry point "
        "was removed — which is a consumer-visible break — or the parse stopped working, "
        "and a closure that parses nothing passes over nothing."
    )

    exercised = 0
    for alias, target in sorted(aliases.items()):
        shim = artifact.script(alias)
        assert shim is not None, (
            f"console alias {alias!r} is declared in [project.scripts] but no shim for it "
            f"exists in the installed environment at {artifact.script_dir}. A consumer "
            "typing it gets 'command not found' on the first line they type."
        )
        # The shim lives INSIDE the fresh environment, not in the repository's own .venv.
        assert _inside(artifact.root, str(shim.resolve())), (
            f"PROBE-INVALID: the shim for {alias!r} resolved to {shim}, outside the fresh "
            "environment. That is the editable install answering for the artifact."
        )

        if target == _CLI_TARGET:
            done = _run(artifact, [str(shim), "--help"])
            assert done.returncode == 0, (
                f"`{alias} --help` failed from the installed distribution "
                f"(exit {done.returncode}):\n{done.stderr}"
            )
            assert "usage:" in done.stdout, (
                f"`{alias} --help` rendered no usage block: {done.stdout[:400]!r}"
            )
        elif target == _MCP_TARGET:
            done = _run(
                artifact,
                [str(shim)],
                stdin=_jsonrpc({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}),
            )
            assert done.returncode == 0 and done.stdout.strip(), (
                f"`{alias}` answered nothing over stdio (exit {done.returncode}): "
                f"{done.stderr[:400]!r}"
            )
        else:
            raise AssertionError(
                f"console alias {alias!r} points at {target!r}, for which this guard has no "
                "registered exerciser. Register one — an alias nobody exercises is an entry "
                "point that ships untested, which is what AC1 exists to end. Skipping it "
                "silently is the AI-E8-6 breach (a guard narrower than its own AC)."
            )
        exercised += 1

    assert exercised == len(aliases) >= _MINIMUM_ALIASES

    # AC1.2 — both sub-command help surfaces render from the ARTIFACT, not from the tree.
    argus = artifact.script("argus")
    assert argus is not None
    for arguments in (["--help"], ["audit", "--help"]):
        done = _run(artifact, [str(argus), *arguments])
        assert done.returncode == 0 and "usage:" in done.stdout, (
            f"`argus {' '.join(arguments)}` did not render from the installed "
            f"distribution: exit {done.returncode}\n{done.stderr}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC1.3 — a fixture audit, to a real verdict, from the installed distribution
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_RELEASE_001_26_a_fixture_audit_reaches_a_real_verdict(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-RELEASE-001-26 — Story 12.9 / AC1.3: the artifact AUDITS, not merely imports.

    OBSERVABLE: the stdout summary line and the process exit code of a real audit run by the
    INSTALLED ``argus``, over a committed fixture repository staged by this project's own
    cartridge helper.

    The verdict token is checked against the live :class:`Verdict` enum and the exit code
    against ``exit_code_for_verdict``, so this is the AR3 wire contract measured end to end
    through the artifact a consumer installs — not a re-statement of it.
    """
    artifact = _artifact()
    _assert_provenance(artifact)

    repo, _sha = stage_cartridge(_FIXTURE_CARTRIDGE, tmp_path / "fixture-repo")
    argus = artifact.script("argus")
    assert argus is not None

    done = _run(artifact, [str(argus), "audit", str(repo)])

    summary = [
        line for line in done.stdout.splitlines() if _SUMMARY_LINE.match(line.strip())
    ]
    assert len(summary) == 1, (
        "the installed `argus audit` did not print exactly one parseable FR18 summary line. "
        f"exit={done.returncode}\nstdout:\n{done.stdout}\nstderr:\n{done.stderr[-2000:]}"
    )
    match = _SUMMARY_LINE.match(summary[0].strip())
    assert match is not None

    token = match.group("verdict")
    verdicts = {member.value: member for member in Verdict}
    assert token in verdicts, (
        f"the installed distribution printed verdict token {token!r}, which the live "
        f"Verdict enum cannot produce ({sorted(verdicts)}). A consumer parsing this line "
        "would be reading an outcome the gate does not define."
    )
    assert done.returncode == exit_code_for_verdict(verdicts[token]), (
        f"the artifact returned exit {done.returncode} for verdict {token!r}, but the AR3 "
        f"map returns {exit_code_for_verdict(verdicts[token])}. The exit code is the one "
        "fact a CI consumer acts on without reading anything else."
    )
    assert int(match.group("den")) > 0, (
        "the audit graded no files at all, so it reached a verdict over nothing and this "
        "measurement is vacuous"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC1.4 — a real MCP JSON-RPC exchange, through the INSTALLED shim
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_RELEASE_001_27_the_mcp_shim_completes_a_jsonrpc_exchange(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-RELEASE-001-27 — Story 12.9 / AC1.4: the agent entry point, as shipped.

    OBSERVABLE: the JSON-RPC replies the INSTALLED ``argus-mcp`` shim writes to stdout for a
    real ``initialize`` / ``tools/list`` / ``tools/call`` exchange over stdio.

    ``tests/test_mcp_server.py`` drives the server IN PROCESS, which cannot see a broken
    entry point, a missing packaged asset or a packaging error — the three things that can
    only fail in an installed distribution. This is registered in ``ArgusAgent-RELEASE``
    rather than opening a second MCP id because it is one artifact probe among four, not a
    protocol test: the protocol is 12.6's and is covered there (12.9 / §Testing, decided).
    """
    artifact = _artifact()
    _assert_provenance(artifact)

    repo, _sha = stage_cartridge(_FIXTURE_CARTRIDGE, tmp_path / "mcp-repo")
    shim = artifact.script("argus-mcp")
    assert shim is not None, "the installed distribution has no `argus-mcp` shim"

    handshake = _jsonrpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-11-25"},
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    )
    advertised = _run(artifact, [str(shim)], stdin=handshake)
    assert advertised.returncode == 0, (
        f"the installed `argus-mcp` shim exited {advertised.returncode} on the handshake:"
        f"\n{advertised.stderr[-2000:]}"
    )
    listing = [
        json.loads(line) for line in advertised.stdout.splitlines() if line.strip()
    ]
    assert len(listing) == 2, (
        "expected one reply per REQUEST and none for the notification; measured "
        f"{len(listing)}: {advertised.stdout[:1000]!r}"
    )
    tools = {reply["id"]: reply for reply in listing}[2]["result"]["tools"]
    assert tools, "the installed shim advertises no tool at all"

    # The call is DERIVED from what the artifact itself advertises — the tool's name and its
    # schema's single required property — never hand-typed. A renamed tool or a renamed
    # argument is then answered correctly by this probe instead of turning it into a test of
    # a name somebody remembered, which is the transcription class AI-E9-7 forbids. (The
    # first draft of this test DID hand-type `argus_audit`/`repo_path`; the artifact
    # answered `unknown tool`, and that red is what produced this closure.)
    tool = tools[0]
    required = list(tool["inputSchema"].get("required", ()))
    assert len(required) == 1, (
        f"tool {tool['name']!r} declares required properties {required}; this probe supplies "
        "the repository under audit for exactly one, so a second required argument needs a "
        "deliberate decision here rather than a guess."
    )

    done = _run(
        artifact,
        [str(shim)],
        stdin=handshake
        + _jsonrpc(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": tool["name"], "arguments": {required[0]: str(repo)}},
            }
        ),
    )
    assert done.returncode == 0, (
        f"the installed `argus-mcp` shim exited {done.returncode}:\n{done.stderr[-2000:]}"
    )

    replies = [json.loads(line) for line in done.stdout.splitlines() if line.strip()]
    assert len(replies) == 3, (
        "expected exactly one reply per REQUEST and none for the notification; measured "
        f"{len(replies)}: {done.stdout[:1000]!r}"
    )
    by_id = {reply["id"]: reply for reply in replies}
    assert sorted(by_id) == [1, 2, 3]
    for reply in replies:
        assert reply["jsonrpc"] == "2.0"
        assert ("result" in reply) ^ ("error" in reply), (
            f"a JSON-RPC reply carried both or neither of result/error: {reply}"
        )

    assert by_id[1]["result"]["serverInfo"]["name"], "initialize named no server"

    audit_reply = by_id[3]
    assert "result" in audit_reply, (
        "the installed shim could not run an audit through `tools/call`: "
        f"{audit_reply.get('error')}"
    )
    text = audit_reply["result"]["content"][0]["text"]
    assert _SUMMARY_LINE.match(text.strip().splitlines()[0]), (
        f"the tool result does not open with the FR18 summary line: {text[:300]!r}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC1.5 — the probe refuses rather than lying, and a missing tool is NAMED
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_RELEASE_001_28_the_probe_refuses_and_never_skips_silently() -> None:
    """TC-ArgusAgent-RELEASE-001-28 — Story 12.9 / AC1.5: positive control + named Unevaluable.

    OBSERVABLE (i): whether the provenance probe accepts an ``argus`` resolved from the
    REPOSITORY instead of the fresh environment. This is not hypothetical — while this guard
    was being built the naive route was MEASURED resolving ``argus`` from
    ``<repo>/argus/__init__.py`` while every other assertion passed, which is the false
    clean bill of health ``-21`` exists to make impossible. Here the repository is forced
    onto the path deliberately and the probe must REFUSE.

    OBSERVABLE (ii): whether a missing install tool produces a named
    :class:`release_preflight.Unevaluable` rather than a silent pass (AR10 / NFR-R1).
    """
    artifact = _artifact()

    honest = _resolved_argus(artifact)
    assert honest.returncode == 0, honest.stderr
    assert _inside(artifact.root, honest.stdout), (
        f"the honest probe resolved argus from {honest.stdout.strip()!r}, which is not "
        "inside the fresh environment"
    )

    spoofed = _resolved_argus(
        artifact, env=_clean_env(PYTHONPATH=str(_REPO_ROOT))
    )
    assert spoofed.returncode != 0, (
        "the probe ACCEPTED an `argus` resolved from the repository instead of the "
        "installed distribution. Every AC1 measurement would then be a triumphant pass "
        "over the wrong tree — the trap that cost Story 11.5 a cycle."
    )
    assert "PROBE-INVALID" in spoofed.stderr, spoofed.stderr

    # (ii) — no tool, no claim, and the reason is spoken.
    assert unevaluable_install_tooling(lambda name: "/somewhere/uv") is None

    missing = unevaluable_install_tooling(lambda name: None)
    assert isinstance(missing, rp.Unevaluable), "a missing installer must be Unevaluable"
    assert missing.edge_case == "E6"
    assert "uv" in missing.reason and "INSTALLED distribution" in missing.reason
    assert "NOT EVALUATED" in str(missing)

    # And in THIS environment it is evaluable, so the skip cannot become the normal path.
    assert unevaluable_install_tooling() is None, (
        "the installed-artifact guard is skipping in the dev environment; a permanently "
        "skipped guard is a guard nobody runs"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC6.1 — the architecture's own statement of WHAT THE RELEASE CONTAINS
#
# Verification area ``ArgusAgent-DOCS`` (``-72``), homed in this RELEASE-area module and the
# choice recorded rather than defaulted: the claim is about the SHIPPED PACKAGE, which is
# this file's subject, and its natural neighbour `tests/test_built_distribution.py` sits at
# 1181 of NFR-M1's 1200 lines. Mixed areas in one module already have precedent — that file
# carries both RELEASE and DOCS ids for the same reason.
# ─────────────────────────────────────────────────────────────────────────────

_ARCHITECTURE = (
    _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent" / "architecture.md"
)

# The struck cells, verbatim. Each must survive on the page wearing `~~` — §3.4 says a
# superseded measurement is struck, never erased, and this project's whole method depends on
# a later reader being able to see that the figure moved and when.
_SUPERSEDED_PACKAGE_CELLS: tuple[str, ...] = (
    "~~`argus`, `argus-agent`, `repo-audit` — all → `argus.cli:main`~~",
    "~~**10** — Python (base) + 9 via `[languages]`~~",
)


def _architecture_package_section() -> str:
    text = _ARCHITECTURE.read_text(encoding="utf-8")
    start = text.index("**Shipped package, measured in place 2026-08-15")
    end = text.index("**Index channel, exit condition RE-AFFIRMED", start)
    return text[start:end]


def test_TC_ArgusAgent_DOCS_001_72_the_architecture_package_table_matches_the_distribution() -> None:
    """TC-ArgusAgent-DOCS-001-72 — Story 12.9 / AC6.1: the shipped-package table is DERIVED.

    OBSERVABLE: `architecture.md` §I's *"Shipped package"* table, cell by cell, against
    `pyproject.toml` and the live grammar registry.

    MEASURED STALE in FOUR cells on `de05dec`: console scripts said three and there were four
    (12.6); base deps omitted the nine grammars 12.5 promoted; `[languages]` was described as
    a feature when 12.5 made it a backward-compatibility alias; and grounded languages said
    *"Python (base) + 9 via `[languages]`"*, false in both halves. This is the architecture's
    own statement of what the release contains, so it is now held rather than remembered —
    both directions, so an eleventh grammar or a fifth alias turns this RED instead of leaving
    the page quietly wrong for another two epics.
    """
    from argus.shared.grammar_status import GRAMMAR_PACKAGE_BY_LANGUAGE

    section = _architecture_package_section()
    pyproject = (_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    checked = 0

    # (1) Console scripts: the count and every alias, derived by closure.
    aliases = console_script_aliases()
    assert f"**{len(aliases)}**" in section, (
        f"the table does not state the live console-script count ({len(aliases)}). It said "
        "three while the distribution shipped four for a whole epic."
    )
    for alias, target in aliases.items():
        assert f"`{alias}`" in section, f"console alias {alias!r} is missing from the table"
        assert f"`{target}`" in section, f"the table does not state that {alias!r} runs {target!r}"
        checked += 1

    # (2) Base deps: every grammar the tool grounds is an ORDINARY dependency, and the table
    # says so. Derived from the registry, so an eleventh language fails here at edit time.
    packages = sorted(set(GRAMMAR_PACKAGE_BY_LANGUAGE.values()))
    assert packages, "the grammar registry is empty; this comparison would be vacuous"
    base_deps = pyproject[
        pyproject.index("dependencies = [") : pyproject.index("[tool.flit.module]")
    ]
    for package in packages:
        assert package in base_deps, (
            f"{package} is no longer a base dependency; NFR-P3 classifies coverage lost to a "
            "grammar missing from the default install as a PACKAGING DEFECT"
        )
        suffix = package[len("tree-sitter") :] or "-python"
        assert f"`{suffix}`" in section or package in section, (
            f"the table does not list {package} among the base dependencies"
        )
        checked += 1
    assert "**all ten**" in section, "the table no longer states that all ten grammars ship"

    # (3) The extra is an ALIAS, and the table says which.
    assert "backward-compatibility ALIAS, not a feature" in section, (
        "the table still describes `[languages]` as a feature. Story 12.5 made it an alias "
        "that adds nothing to an install; calling it a feature tells a reader to install it."
    )
    checked += 1

    # (4) Grounded languages: the count, and that they are in the DEFAULT install.
    assert f"**{len(GRAMMAR_PACKAGE_BY_LANGUAGE)}**, all in the DEFAULT install" in section, (
        f"the table does not state that all {len(GRAMMAR_PACKAGE_BY_LANGUAGE)} grounded "
        "languages are in the default install"
    )
    checked += 1

    assert checked >= 15, f"only {checked} cells were checked; the table is barely covered"

    # §3.4 — the superseded cells are struck, not erased.
    page = _ARCHITECTURE.read_text(encoding="utf-8")
    for cell in _SUPERSEDED_PACKAGE_CELLS:
        assert cell in page, (
            f"the superseded package cell was DELETED rather than struck: {cell!r}. A reader "
            "must be able to see that the figure moved, and when (§3.4)."
        )
