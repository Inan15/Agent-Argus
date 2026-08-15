"""Story 12.6 / FR35 — a coding agent can run the audit and read the verdict.

Verification area **ArgusAgent-MCP-001** (``TC-ArgusAgent-MCP-001-01``..``-15``), OPENED by
this story. The decision to open an area rather than extend one is recorded because Story
12.5 rejected an invented area (``PACKAGING-001``) three weeks ago and this must not read
as ignoring that: 12.5's objection was that the new area *and a new file* were a **second
home for a fact that already had one** — ``test_grammar_runtime_validation.py`` already
parsed ``pyproject.toml`` for the same drift class. Here there is **no existing home**: no
test file in this repository covers a JSON-RPC surface, and folding it into ``CLI-001``
would mix a wire protocol into the area bound to ``build_parser``'s argv contract, muddying
``-35``'s corpus. Area creation is ordinary here (AUDIT, CACHE, CARTRIDGE, COST, DETECT,
DOCS, DOGFOOD, EVIDENCE, HITL, PIPELINE, REPORT-002, RELEASE, STORE all exist). Edits this
story makes to existing files continue THEIR areas from their own high-water marks.

**Every guard here is written to AI-E11-1** (Epic-11 retro §3.1): (i) its observable is
named in its docstring, (ii) the defect has been demonstrated to move that observable at
the REAL seam, and (iii) at least one adversarial variant is GENERATED from the
grammar/registry the guard closes over rather than hand-listed. The four that most needed
it, and how they get it:

* stdout purity (``-08``) — a synthetic prints to ``sys.stdout`` *during a real audit*
  through the adapter's own call site, and the channel is shown to stay clean;
* verdict parity (``-07``) — the divergence is DEMONSTRATED by building an
  ``AuditRequest`` directly, the way a hand-rolled adapter would, and observing that it
  assesses a different population (Story 10.3 / DN-8);
* the input-schema closure (``-06``) — a flag is added to a real parser and the closure is
  shown to go red with no schema entry for it;
* the no-listener gate (``-05``) — exercised against the REAL server PROCESS with a
  ``socket.bind``/``listen`` sentinel, and the sentinel itself is proven capable of firing.

Non-vacuity floors (E.3) sit on everything that passes by finding nothing: messages
parsed, tools resolved, schema properties derived and modules scanned.

Offline, deterministic, no network, no sleeps. The one subprocess (``-05``) exists because
"no port is bound" is an observable of a PROCESS and of nothing else.
"""

from __future__ import annotations

import ast
import io
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_PACKAGE_ROOT = _REPO_ROOT / "argus"
_MCP_ROOT = _PACKAGE_ROOT / "mcp"

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus import __version__, cli  # noqa: E402
from argus.mcp import protocol, server  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit  # noqa: E402
from argus.verdict.negative_assurance import (  # noqa: E402
    INSTRUMENT_STATUS,
    render_instrument_disclosure,
)

# ─────────────────────────────────────────────────────────────────────────────
# Non-vacuity floors. Each sits BELOW the figure measured on 2026-08-15 by enough slack
# that an ordinary edit does not trip it, and above zero by enough that a rename, a move
# or a parse failure cannot pass silently.
# ─────────────────────────────────────────────────────────────────────────────

#: Measured 2026-08-15: 15 accepted arguments on the `audit` sub-command.
_MIN_SCHEMA_PROPERTIES = 10
#: Measured: 6 handled methods (initialize, notifications/initialized, server/discover,
#: tools/list, tools/call, notifications/cancelled).
_MIN_HANDLED_METHODS = 6
#: Measured: 3 modules under `argus/mcp/` (`__init__`, `protocol`, `server`).
_MIN_MCP_MODULES = 3
#: Measured: 2 supported protocol revisions. A set that collapses to one has lost an era.
_MIN_SUPPORTED_VERSIONS = 2

# The stdio binding forbids a listener. These are the module-level import names that would
# be needed to open one, plus the async machinery the architecture separately forbids.
_FORBIDDEN_TOP_LEVEL_IMPORTS: tuple[str, ...] = (
    "socket",
    "socketserver",
    "http",
    "wsgiref",
    "ssl",
    "asyncio",
    "selectors",
    "fastapi",
    "uvicorn",
    "starlette",
)

# Credential-shaped parameter stems (AC2.4). A published input schema carrying any of
# these would mean this surface had begun handling credentials, which constraint 4 forbids
# outright — the deep pass reads its provider credential from the existing adapter's
# environment contract and from nowhere else.
_CREDENTIAL_STEMS: tuple[str, ...] = (
    "key",
    "token",
    "secret",
    "password",
    "passwd",
    "credential",
    "auth",
    "account",
    "bearer",
    "session",
    "cookie",
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _drive(messages: list[dict[str, Any]], *, trailing: str = "") -> tuple[
    list[dict[str, Any]], str, str, int
]:
    """Run the REAL loop over *messages* in-process; return (replies, stdout, stderr, code).

    In-process rather than through a subprocess on purpose: the loop takes its three
    streams by injection precisely so a guard can drive the real seam without paying for a
    process. ``-05`` is the one guard whose observable needs a process, and it spawns one.
    """
    payload = "\n".join(json.dumps(message) for message in messages)
    if payload:
        payload += "\n"
    stdin = io.StringIO(payload + trailing)
    out, err = io.StringIO(), io.StringIO()
    code = server.main([], stdin=stdin, stdout=out, stderr=err)
    replies = [json.loads(line) for line in out.getvalue().splitlines() if line.strip()]
    return replies, out.getvalue(), err.getvalue(), code


def _call(repo: Path, request_id: int = 1, **arguments: Any) -> dict[str, Any]:
    """One `tools/call` message for the one published tool."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {
            "name": protocol.TOOL_NAME,
            "arguments": {"repo": str(repo), **arguments},
        },
    }


def _mcp_sources() -> dict[str, str]:
    """Every module under ``argus/mcp/`` as {repo-relative posix path: source}."""
    return {
        path.relative_to(_REPO_ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(_MCP_ROOT.rglob("*.py"))
        if "__pycache__" not in path.parts
    }


def top_level_imports(source: str) -> frozenset[str]:
    """Every top-level package name *source* imports, by ``ast`` (PURE).

    The analyzer behind ``-04``. It reads source as TEXT and never executes it, for Story
    10.5 / DN-6's three measured reasons — a lazy import would defeat a runtime walk, an
    absent optional extra would make the answer host-dependent, and a guard that executes
    no ``argus`` line cannot perturb the coverage figure the ledger cites.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            found.add(node.module.split(".")[0])
    return frozenset(found)


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — the entry point, and the protocol surface behind it
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_MCP_001_01_the_alias_ships_in_the_same_distribution() -> None:
    """TC-ArgusAgent-MCP-001-01 — AC1: exactly one new console alias, resolving to a real callable.

    OBSERVABLE: the ``[project.scripts]`` table and the target it names. The alias is read
    off ``pyproject.toml`` rather than asserted as a literal pair, so a rename of either
    half is caught; and the target is IMPORTED and called-shape-checked, because an alias
    pointing at a name that does not exist installs cleanly and fails on first use.
    """
    text = (_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    table = text.split("[project.scripts]", 1)[1].split("\n[", 1)[0]
    aliases = {
        line.split("=", 1)[0].strip().strip('"'): line.split("=", 1)[1].strip().strip('"')
        for line in table.splitlines()
        if "=" in line and not line.lstrip().startswith("#")
    }
    assert len(aliases) == 4, (
        f"expected the three CLI aliases plus exactly one new one, measured {aliases}. "
        "This surface adds ONE entry point, in the SAME distribution — not a channel."
    )
    assert aliases["argus-mcp"] == "argus.mcp.server:main"

    module_path, _, attribute = aliases["argus-mcp"].partition(":")
    assert module_path == server.__name__
    assert callable(getattr(server, attribute))

    # The three CLI aliases are untouched: this story adds, it does not re-point.
    for alias in ("argus", "argus-agent", "repo-audit"):
        assert aliases[alias] == "argus.cli:main"


def test_TC_ArgusAgent_MCP_001_02_the_supported_version_set_is_closed_and_exhaustive() -> None:
    """TC-ArgusAgent-MCP-001-02 — AC1: a CLOSED constant with a renderer that RAISES.

    OBSERVABLE: ``protocol_era`` over the version vocabulary. AR10's house pattern —
    ``exit_code_for_verdict`` and ``render_instrument_disclosure`` both raise on an
    unregistered member — because falling through to a default would answer a revision
    nobody registered with the COMFORTABLE wrong answer.

    ADVERSARIAL VARIANT, GENERATED from the constant rather than hand-listed: every
    supported version is mutated into a neighbouring string, and each mutation must be
    rejected by the dispatcher with ``-32022`` naming the real supported set.
    """
    assert len(protocol.SUPPORTED_PROTOCOL_VERSIONS) >= _MIN_SUPPORTED_VERSIONS
    assert protocol.SUPPORTED_PROTOCOL_VERSIONS == tuple(
        member.value for member in protocol.ProtocolVersion
    ), "the published set and the enum have drifted apart; there must be one vocabulary"

    for member in protocol.ProtocolVersion:
        assert isinstance(protocol.protocol_era(member), protocol.ProtocolEra)

    with pytest.raises(protocol.McpProtocolError):
        protocol.protocol_era("2019-01-01")  # type: ignore[arg-type]

    generated = [
        version.replace("-", "_") for version in protocol.SUPPORTED_PROTOCOL_VERSIONS
    ] + [version[:-1] + "9" for version in protocol.SUPPORTED_PROTOCOL_VERSIONS]
    for candidate in generated:
        assert candidate not in protocol.SUPPORTED_PROTOCOL_VERSIONS
        outcome = protocol.dispatch(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/list",
                "_meta": {protocol.PROTOCOL_VERSION_META_KEY: candidate},
            }
        )
        assert isinstance(outcome, protocol.Reply)
        error = outcome.payload["error"]
        assert error["code"] == protocol.UNSUPPORTED_PROTOCOL_VERSION
        assert error["data"]["supported"] == list(protocol.SUPPORTED_PROTOCOL_VERSIONS)
        assert error["data"]["requested"] == candidate


def test_TC_ArgusAgent_MCP_001_03_both_eras_and_every_error_code_are_served() -> None:
    """TC-ArgusAgent-MCP-001-03 — AC1/DN-2: the whole method surface, through the REAL loop.

    OBSERVABLE: the messages the loop writes to stdout for a scripted session. Driven
    through ``server.main`` rather than through ``dispatch`` alone, so the framing, the
    notification handling and the parse-error path are exercised as a host would exercise
    them.

    A legacy client handshakes with ``initialize``; a modern one probes ``server/discover``
    and declares its version per request. Both are answered, because shipping legacy-only
    fails every modern-only client and shipping modern-only fails every host installed
    today — the specification's own compatibility matrix.
    """
    session = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": protocol.ProtocolVersion.LEGACY_2025_11_25.value,
                "capabilities": {},
                "clientInfo": {"name": "host", "version": "1"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "server/discover",
            "_meta": {
                protocol.PROTOCOL_VERSION_META_KEY: (
                    protocol.ProtocolVersion.MODERN_2026_07_28.value
                )
            },
        },
        {"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
        {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 3}},
        {"jsonrpc": "2.0", "id": 4, "method": "totally/unknown"},
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "not_a_tool", "arguments": {}},
        },
    ]
    replies, _stdout, _stderr, code = _drive(session, trailing="{ this is not json\n")
    assert code == 0, "EOF is the graceful-shutdown signal; the loop must exit 0 on it"

    by_id = {reply.get("id"): reply for reply in replies}
    # The two notifications are CONSUMED and never answered — that is the contract.
    assert len(replies) == len(by_id) == 6, (
        "a notification was answered, or a request was not: "
        f"{[reply.get('id') for reply in replies]}"
    )

    assert by_id[1]["result"]["protocolVersion"] == (
        protocol.ProtocolVersion.LEGACY_2025_11_25.value
    )
    assert by_id[1]["result"]["serverInfo"] == {"name": "argus", "version": __version__}
    assert by_id[2]["result"]["supportedVersions"] == list(
        protocol.SUPPORTED_PROTOCOL_VERSIONS
    )
    assert [tool["name"] for tool in by_id[3]["result"]["tools"]] == [protocol.TOOL_NAME]
    assert by_id[4]["error"]["code"] == protocol.METHOD_NOT_FOUND
    assert by_id[5]["error"]["code"] == protocol.INVALID_PARAMS
    assert by_id[None]["error"]["code"] == protocol.PARSE_ERROR

    handled = {
        "initialize",
        "notifications/initialized",
        "server/discover",
        "tools/list",
        "tools/call",
        "notifications/cancelled",
    }
    assert len(handled) >= _MIN_HANDLED_METHODS
    for method in sorted(handled):
        source = (_MCP_ROOT / "protocol.py").read_text(encoding="utf-8")
        assert method in source, f"{method} is not handled by the dispatcher any more"


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — the four §Project Classification constraints, mechanically
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_MCP_001_04_no_listener_symbol_reaches_the_adapter() -> None:
    """TC-ArgusAgent-MCP-001-04 — AC2.1/AC2.2: the adapter imports nothing that can listen.

    OBSERVABLE: the top-level import names in every ``argus/mcp/**`` module, by ``ast``.
    This is the SYMBOL half of constraint 1; ``-05`` supplies the behavioural half at the
    real process, because a symbol table alone is not an observation of behaviour
    (AI-E11-1 clause (i)).

    ADVERSARIAL VARIANT, GENERATED from the forbidden set: one synthetic module per member
    is fed to the same analyzer, and every one must be flagged. A guard that goes green by
    finding nothing has to be shown capable of finding something.
    """
    sources = _mcp_sources()
    assert len(sources) >= _MIN_MCP_MODULES, (
        f"only {len(sources)} module(s) resolved under {_MCP_ROOT.name}/ — the package "
        "moved or was renamed and this guard has stopped testing anything"
    )
    for rel, source in sorted(sources.items()):
        leaked = sorted(top_level_imports(source) & set(_FORBIDDEN_TOP_LEVEL_IMPORTS))
        assert not leaked, (
            f"{rel} imports {leaked}. stdio only: no network listener is opened and no "
            "port is bound, and no concurrency model of the adapter's own is introduced "
            "(architecture §Architectural Boundaries)."
        )

    for forbidden in _FORBIDDEN_TOP_LEVEL_IMPORTS:
        synthetic = f"import {forbidden}\n\n\ndef serve() -> None:\n    ...\n"
        assert forbidden in top_level_imports(synthetic), (
            f"the analyzer stopped seeing `import {forbidden}` — it would now pass the "
            "real modules vacuously"
        )
        from_form = f"from {forbidden} import something\n"
        assert forbidden in top_level_imports(from_form)


def test_TC_ArgusAgent_MCP_001_05_the_real_server_process_binds_no_port() -> None:
    """TC-ArgusAgent-MCP-001-05 — AC2.1: BEHAVIOUR, observed on the real process.

    OBSERVABLE: whether ``socket.socket.bind`` or ``.listen`` is ever called inside a real
    ``argus-mcp`` process that has served a real session. A sentinel replaces both before
    ``argus`` is imported and records any call to a marker file.

    NON-VACUITY, and it is mandatory here (AI-E11-1 clause (ii)): the SAME sentinel, in the
    SAME harness, is shown to fire when a process does bind. A guard that has never seen
    its observable move proves nothing.
    """
    marker = _REPO_ROOT / ".pytest-mcp-listener-marker"
    if marker.exists():  # pragma: no cover - defensive
        marker.unlink()

    preamble = (
        "import pathlib, socket, sys\n"
        "sys.path.insert(0, {root!r})\n"
        "_marker = pathlib.Path({marker!r})\n"
        "def _forbid(name):\n"
        "    def _fire(self, *args, **kwargs):\n"
        "        _marker.write_text(name, encoding='utf-8')\n"
        "        raise AssertionError('a listener was opened: ' + name)\n"
        "    return _fire\n"
        "socket.socket.bind = _forbid('bind')\n"
        "socket.socket.listen = _forbid('listen')\n"
    ).format(root=str(_REPO_ROOT), marker=str(marker))

    session = "\n".join(
        json.dumps(message)
        for message in (
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2025-11-25", "capabilities": {}},
            },
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        )
    ) + "\n"

    done = subprocess.run(
        [
            sys.executable,
            "-c",
            preamble + "from argus.mcp.server import main\nraise SystemExit(main([]))\n",
        ],
        input=session,
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
        timeout=180,
    )
    assert done.returncode == 0, (
        f"the real server process failed: {done.stdout[-800:]} {done.stderr[-800:]}"
    )
    answered = [json.loads(line) for line in done.stdout.splitlines() if line.strip()]
    assert [reply["id"] for reply in answered] == [1, 2], (
        "the real process did not serve the session, so 'it bound no port' would be true "
        "of a process that did nothing"
    )
    assert not marker.exists(), (
        f"the real argus-mcp process opened a listener ({marker.read_text('utf-8')}). "
        "stdio only is a binding constraint, not a preference."
    )

    # The sentinel fires when something DOES bind — proven in the same harness.
    control = subprocess.run(
        [
            sys.executable,
            "-c",
            preamble
            + "import socket\ntry:\n    socket.socket().bind(('127.0.0.1', 0))\n"
            "except AssertionError:\n    pass\n",
        ],
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
        timeout=60,
    )
    assert control.returncode == 0, control.stderr[-800:]
    assert marker.exists(), (
        "the sentinel did not fire on a process that really did bind — it cannot have "
        "proven anything about the process above"
    )
    marker.unlink()


def test_TC_ArgusAgent_MCP_001_13_the_dependency_arrow_points_inward_only() -> None:
    """TC-ArgusAgent-MCP-001-13 — AC2.3: the core never imports the adapter.

    OBSERVABLE: every ``argus/**`` module OUTSIDE ``argus/mcp/``, walked with ``ast`` for an
    import of ``argus.mcp``. "No new authority" is an architectural statement about
    direction: the adapter composes the core, and the day the core reaches back the layer
    boundary has stopped existing — which is how a second decision path gets in.
    """
    scanned = 0
    offenders: list[str] = []
    for path in sorted(_PACKAGE_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts or _MCP_ROOT in path.parents or path == _MCP_ROOT:
            continue
        rel = path.relative_to(_REPO_ROOT).as_posix()
        if rel.startswith("argus/mcp/"):
            continue
        scanned += 1
        source = path.read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
                "argus.mcp"
            ):
                offenders.append(rel)
            elif isinstance(node, ast.Import) and any(
                alias.name.startswith("argus.mcp") for alias in node.names
            ):
                offenders.append(rel)
    assert scanned >= 50, (
        f"only {scanned} core module(s) scanned (75 at 2026-08-15) — the walk collapsed"
    )
    assert not offenders, (
        f"the pure core imports the adapter: {sorted(set(offenders))}. The arrow points "
        "inward only."
    )


def test_TC_ArgusAgent_MCP_001_09_no_credential_shaped_parameter_is_published() -> None:
    """TC-ArgusAgent-MCP-001-09 — AC2.4: this surface accepts and stores no credential.

    OBSERVABLE: the property names of the published ``inputSchema``, tested against a
    credential-stem vocabulary. The deep pass still reads its provider credential through
    the EXISTING adapter's environment contract; nothing about that path runs through here.

    ADVERSARIAL VARIANT, GENERATED from the vocabulary: each stem is spelled as a plausible
    property name and the detector must flag every one, so the scan cannot go green by
    having stopped working.
    """
    schema = protocol.derive_input_schema()
    properties = schema["properties"]
    assert len(properties) >= _MIN_SCHEMA_PROPERTIES, (
        f"only {len(properties)} schema properties derived (15 at 2026-08-15) — the "
        "derivation collapsed and this scan would pass over nothing"
    )

    def _credential_shaped(names: list[str]) -> list[str]:
        return sorted(
            name
            for name in names
            if any(stem in name.lower() for stem in _CREDENTIAL_STEMS)
        )

    assert not _credential_shaped(list(properties)), (
        f"the published tool schema exposes credential-shaped parameter(s): "
        f"{_credential_shaped(list(properties))}. Constraint 4 is absolute: no key, token "
        "or account is accepted or stored by this surface."
    )
    for stem in _CREDENTIAL_STEMS:
        assert _credential_shaped([f"provider_{stem}"]) == [f"provider_{stem}"], (
            f"the credential detector stopped recognising {stem!r}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — verdict parity, by construction
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_MCP_001_06_the_input_schema_is_derived_from_the_parser() -> None:
    """TC-ArgusAgent-MCP-001-06 — AC3.3: schema ≡ parser, BOTH directions.

    OBSERVABLE: the symmetric difference between the schema's property set and the ``dest``
    set the real parser accepts. This is ``TC-ArgusAgent-CLI-001-35``'s closure pattern
    applied to the second invocation surface, and it is what stops the two surfaces
    drifting apart one flag at a time.

    ADVERSARIAL VARIANT, GENERATED from the parser itself: a flag is added to a REAL
    parser and the derivation is shown to pick it up, so a flag added to ``build_parser``
    without a schema entry cannot exist — the schema is not a place a flag can be
    forgotten. The DEFECT is then shown to move the observable: a schema derived from the
    unmodified parser is missing that flag, and the comparison goes red.

    It also asserts the schema declares NO default. Publishing one would re-declare a value
    that already has a source, and the one place that would hide is ``coverage_scope``,
    where the CLI's default deliberately is not the model's (Story 10.3 / DN-8).
    """
    parser = cli.build_parser()
    derived = protocol.derive_input_schema(parser)
    accepted = {spec.dest for spec in protocol.audit_argument_specs(parser)}

    assert set(derived["properties"]) == accepted, (
        "the published schema and the accepted argv surface disagree: "
        f"schema-only={sorted(set(derived['properties']) - accepted)}, "
        f"parser-only={sorted(accepted - set(derived['properties']))}"
    )
    assert derived["required"] == ["repo"]
    assert derived["additionalProperties"] is False
    for name, prop in sorted(derived["properties"].items()):
        assert "default" not in prop, (
            f"{name} publishes a default in the tool schema. The value that governs is the "
            "one `build_parser` gives `parse_args`; a copy here is a second thing to keep "
            "true, and on `coverage_scope` the two answers deliberately differ (DN-8)."
        )
    assert derived["properties"]["coverage_scope"]["enum"] == [
        "repository",
        "application",
    ]

    # The generated variant: a flag the real parser gained but no schema entry names.
    widened = cli.build_parser()
    for action in widened._actions:  # noqa: SLF001 - argparse exposes no public walk
        sub = getattr(action, "choices", None)
        if isinstance(sub, dict) and "audit" in sub:
            sub["audit"].add_argument("--newly-added-flag", dest="newly_added_flag")
            break
    else:  # pragma: no cover - the parser always has the audit sub-command
        pytest.fail("could not reach the audit sub-parser to generate the variant")

    widened_props = set(protocol.derive_input_schema(widened)["properties"])
    assert "newly_added_flag" in widened_props, (
        "the derivation did not pick up a flag added to the real parser, so it is not a "
        "derivation — it is a list that happens to agree today"
    )
    assert widened_props - set(derived["properties"]) == {"newly_added_flag"}, (
        "the closure cannot see a flag that was added on one side only; that is exactly "
        "the drift this guard exists to make impossible"
    )


def test_TC_ArgusAgent_MCP_001_07_the_two_surfaces_return_the_same_verdict(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """TC-ArgusAgent-MCP-001-07 — AC3.1/AC3.2: same repo, same commit, same verdict.

    OBSERVABLE: the verdict token, the exact ratios, the blocking count, the assessed scope
    and the exit code, produced through BOTH REAL ENTRY POINTS over one real fixture
    repository — ``cli.main(argv)`` on one side and the MCP server's own stdin→stdout loop
    on the other. Never one shared helper called twice: a parity test whose observable
    cannot move when the two surfaces diverge is vacuous.

    THE DEFECT IS DEMONSTRATED MOVING IT. The third block below is the adapter this story
    was most likely to ship: one that constructs ``AuditRequest`` directly. It inherits
    ``coverage_scope="repository"`` from the model instead of ``"application"`` from the
    parser (Story 10.3 / DN-8, an announced divergence pinned both ways by
    ``TC-ArgusAgent-CLI-001-37b``), assesses a DIFFERENT POPULATION, and its answer differs
    from the CLI's on an unchanged repository. That is why the real adapter reuses the
    CLI's own projection rather than building a request.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")

    cli_code = cli.main(["audit", str(repo)])
    cli_summary = [
        line
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("verdict=")
    ]
    assert len(cli_summary) == 1

    replies, _stdout, _stderr, _code = _drive([_call(repo, request_id=11)])
    result = replies[0]["result"]
    assert result["isError"] is False
    structured = result["structuredContent"]
    text_lines = result["content"][0]["text"].splitlines()

    assert text_lines[0] == cli_summary[0], (
        "the two surfaces describe one run differently:\n"
        f"  CLI: {cli_summary[0]}\n  MCP: {text_lines[0]}"
    )
    assert structured["exit_code"] == cli_code
    parsed = dict(
        field.split("=", 1) for field in cli_summary[0].split(" ") if "=" in field
    )
    assert structured["verdict"] == parsed["verdict"]
    assert structured["deep_ratio"] == parsed["deep_ratio"]
    assert structured["blocking_findings"] == int(parsed["blocking_findings"])
    assert structured["assessed_deep_ratio"] == parsed["assessed_deep_ratio"]
    assert structured["scope"] == parsed["scope"]
    assert structured["held_out"] == int(parsed["held_out"])

    # The divergence, demonstrated at the real seam rather than described.
    divergent = run_audit(
        AuditRequest(
            repo_path=str(repo), commit="HEAD", budget=0, materiality_bar=""
        )
    )
    assert divergent.coverage_scope is None, (
        "AuditRequest's own `coverage_scope` default no longer narrows differently from "
        "the CLI's, so this demonstration has stopped demonstrating anything — re-derive "
        "it against DN-8 rather than deleting it"
    )
    assert structured["scope"] == "application", (
        "the MCP surface stopped inheriting the CLI's `--coverage-scope` default, which "
        "means it is no longer building its request through the CLI's projection"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — stdout carries JSON-RPC messages and nothing else
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_MCP_001_08_stdout_stays_pure_across_a_real_audit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-MCP-001-08 — AC4: EVERY stdout line is one valid JSON-RPC message.

    OBSERVABLE: every line the loop writes to stdout while a REAL audit runs — parsed, all
    of them, not a sample. The audit path this adapter calls is one that prints its FR18
    summary line to stdout today, so the channel is protected structurally: stdout is
    redirected to stderr for the duration of the audit.

    NON-VACUITY, mandatory (AI-E11-1 clause (ii)): the second half injects a synthetic that
    writes to ``sys.stdout`` MID-AUDIT, at the adapter's own call site, and shows the
    channel stays clean and the noise lands on stderr. A guard that has never seen the
    defect move its observable proves nothing — so the defect is introduced on purpose.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")

    replies, stdout, stderr, _code = _drive(
        [
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            _call(repo, request_id=2),
        ]
    )
    lines = stdout.splitlines()
    assert len(lines) == 2, f"expected one line per request, measured {len(lines)}"
    for line in lines:
        message = json.loads(line)
        assert message["jsonrpc"] == "2.0"
        assert ("result" in message) ^ ("error" in message)
        assert "\n" not in line

    # The CLI's own stdout summary line ran during that audit and did NOT reach stdout as
    # a bare line. It is present INSIDE the tool result, where it belongs.
    assert not any(line.startswith("verdict=") for line in lines)
    assert replies[1]["result"]["content"][0]["text"].startswith("verdict=")

    # ── the injected defect, at the real seam ──
    noise = "PRINTED-BY-A-LATER-EDIT"
    real_run_audit = server.run_audit

    def _noisy(*args: Any, **kwargs: Any) -> Any:
        print(noise)
        sys.stdout.write(noise + "-direct\n")
        return real_run_audit(*args, **kwargs)

    monkeypatch.setattr(server, "run_audit", _noisy)
    replies, stdout, stderr, _code = _drive([_call(repo, request_id=3)])

    assert noise not in stdout, (
        "a `print()` beneath run_audit reached the protocol channel — the stdout guard is "
        "not holding, and a host would see a parse error instead of a verdict"
    )
    assert noise in stderr, (
        "the injected write vanished entirely, so this control proved nothing about where "
        "it went; the guard must be shown to REDIRECT, not to swallow"
    )
    for line in stdout.splitlines():
        json.loads(line)
    assert replies[0]["result"]["isError"] is False


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — the FR34 disclosure is on this surface, from the ONE constant
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_MCP_001_10_every_verdict_bearing_result_carries_the_disclosure(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-MCP-001-10 — AC5: the disclosure reaches the tool listing AND the result.

    OBSERVABLE: the rendered disclosure text inside the ``tools/list`` description and
    inside a real verdict-bearing result. It is compared against
    ``render_instrument_disclosure(INSTRUMENT_STATUS)`` — the ONE constant — and never
    against a literal typed here, so flipping the declared status turns this red rather
    than leaving a surface publishing a retired notice (the ``-51`` device).

    The listing half is the point of the pair: an agent reads the description BEFORE it can
    decide to call the tool, which is when a statement about the instrument is worth
    something. The result half is what FR34 requires of every verdict surface.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    disclosure = render_instrument_disclosure(INSTRUMENT_STATUS)

    replies, _stdout, _stderr, _code = _drive(
        [
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            _call(repo, request_id=2),
        ]
    )
    tool = replies[0]["result"]["tools"][0]
    assert disclosure in tool["description"]
    assert "deep_audit" in tool["description"] and "egress" in tool["description"].lower()
    assert "cancel" in tool["description"].lower(), (
        "DN-6: the inability to interrupt an in-flight audit is stated on the surface, not "
        "left for a user to discover"
    )

    text = replies[1]["result"]["content"][0]["text"]
    assert disclosure in text
    assert text.splitlines()[0].startswith("verdict=")

    # The flipped status must NOT already be satisfied, or the presence check is vacuous.
    from argus.verdict.negative_assurance import InstrumentStatus

    flipped = render_instrument_disclosure(InstrumentStatus.VALIDATED)
    assert flipped not in text and flipped not in tool["description"]


# ─────────────────────────────────────────────────────────────────────────────
# AC7 — NFR-M1, determinism, secret-safety, honest degradation
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_MCP_001_11_the_result_carries_no_float_and_no_secret(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-MCP-001-11 — AC7: AR4 (no ``float``) and NFR-S1 (secret-safe), together.

    OBSERVABLE: every scalar in the tool result, walked recursively, and the result text
    scanned for the audited repository's absolute path and for source bytes from the
    cartridge. Ratios travel as exact ``"num/den"`` strings because ``Fraction`` has no JSON
    form and a ``float`` would be a lie about an exact quantity.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    replies, _stdout, _stderr, _code = _drive([_call(repo, request_id=1)])
    result = replies[0]["result"]

    floats: list[str] = []

    def _walk(node: Any, path: str) -> None:
        if isinstance(node, float):
            floats.append(path)
        elif isinstance(node, dict):
            for key, value in node.items():
                _walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                _walk(value, f"{path}[{index}]")

    _walk(result, "result")
    assert not floats, f"AR4: a float reached the wire at {floats}"

    structured = result["structuredContent"]
    assert structured["deep_ratio"] == "1/2"
    assert isinstance(structured["assessed_deep_ratio"], str)

    text = result["content"][0]["text"]
    assert str(repo) not in text, "NFR-S1: an absolute host path reached the result"
    assert "compute_total" not in text, "NFR-S1: source bytes reached the result"
    assert "ordered_findings" not in json.dumps(result), (
        "DN-5: the result carries the CLI's information set, never the verdict object"
    )


def test_TC_ArgusAgent_MCP_001_12_a_typed_failure_is_a_tool_error_and_the_server_survives(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-MCP-001-12 — AC7/NFR-R1: no crash, no traceback, and it keeps serving.

    OBSERVABLE: the response to a ``tools/call`` naming a path that cannot be audited, and
    the response to the NEXT request on the same connection. A typed pipeline failure is a
    TOOL-EXECUTION error (``isError: true``) carrying the CLI's own secret-safe wording,
    because a model handed *"argus: audit failed: …"* has a next action and one handed
    ``-32603`` does not (FR37). A malformed request is a protocol error. The loop survives
    both, and EOF — the binding's graceful-shutdown signal — exits promptly and cleanly.
    """
    missing = tmp_path / "no-such-repository"
    replies, _stdout, _stderr, code = _drive(
        [
            _call(missing, request_id=1),
            {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": 5}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
        ]
    )
    assert code == 0

    failure = replies[0]["result"]
    assert failure["isError"] is True
    text = failure["content"][0]["text"]
    assert text.startswith(f"{cli.PROG}: audit failed: "), text
    assert "Traceback" not in text
    assert "structuredContent" not in failure, (
        "no verdict exists, so there is nothing structured to report about one"
    )

    assert replies[1]["error"]["code"] == protocol.INVALID_PARAMS
    assert replies[2]["result"]["tools"], (
        "the server stopped serving after a failure — NFR-R1 requires it to survive both "
        "classes and keep going"
    )

    # An argument the schema rejects never reaches the audit at all.
    replies, _stdout, _stderr, _code = _drive(
        [_call(tmp_path, request_id=4, budget="not-an-int")]
    )
    assert replies[0]["error"]["code"] == protocol.INVALID_PARAMS
    assert "budget" in json.dumps(replies[0]["error"]["data"])


def test_TC_ArgusAgent_MCP_001_14_the_adapter_is_under_the_nfr_m1_ceiling() -> None:
    """TC-ArgusAgent-MCP-001-14 — AC7: every file this story adds is ≤1200 lines.

    OBSERVABLE: the physical line count of each new module and of this file. The repo-wide
    sweep in ``tests/test_module_size_ceiling.py`` (Story 12.1) is the binding one and it
    covers ``tests/**`` as well as ``argus/**``; this is the local statement of the same
    fact, in the register this repository's per-module assertions already use.
    """
    for path in (*sorted(_MCP_ROOT.rglob("*.py")), Path(__file__)):
        if "__pycache__" in path.parts:
            continue
        count = len(path.read_text(encoding="utf-8").splitlines())
        assert count <= 1200, f"{path.name} is {count} lines, over the NFR-M1 ceiling"


def test_TC_ArgusAgent_MCP_001_15_the_dispatcher_is_pure_and_notifications_are_never_answered() -> None:
    """TC-ArgusAgent-MCP-001-15 — AR8: the message layer is driven with plain dicts, no I/O.

    OBSERVABLE: the outcome type ``dispatch`` returns for each message shape. That the whole
    protocol can be exercised with dicts IS the pure/impure split being structural rather
    than narrated — the one impure act is expressed as a value (``ToolInvocation``) and
    performed by the loop.

    ADVERSARIAL VARIANT, GENERATED from the handled-method set: every method is re-sent with
    its ``id`` removed, and every one must fall to ``Silence``. A notification is never
    answered, however wrong it is — including an unknown one, which is the case a
    hand-written table forgets.
    """
    requests = {
        "initialize": {"params": {"protocolVersion": "2025-11-25"}},
        "server/discover": {},
        "tools/list": {},
        "notifications/initialized": {},
        "notifications/cancelled": {"params": {"requestId": 1}},
        "totally/unknown": {},
    }
    for method, extra in sorted(requests.items()):
        notification = {"jsonrpc": "2.0", "method": method, **extra}
        assert isinstance(protocol.dispatch(notification), protocol.Silence), (
            f"{method!r} was ANSWERED as a notification; notifications are never answered"
        )

    call = protocol.dispatch(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": protocol.TOOL_NAME, "arguments": {"repo": "."}},
        }
    )
    assert isinstance(call, protocol.ToolInvocation)
    assert call.arguments == {"repo": "."}

    # A batch, and a message with the wrong envelope, are both refused as Invalid Request.
    for bad in ([{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}], "nope", 7):
        outcome = protocol.dispatch(bad)
        assert isinstance(outcome, protocol.Reply)
        assert outcome.payload["error"]["code"] == protocol.INVALID_REQUEST
    outcome = protocol.dispatch({"jsonrpc": "1.0", "id": 1, "method": "tools/list"})
    assert isinstance(outcome, protocol.Reply)
    assert outcome.payload["error"]["code"] == protocol.INVALID_REQUEST

    # `encode` renders exactly ONE line, always — a single trailing newline and no embedded
    # one, whatever the payload contains. The newline framing depends on that, and the
    # payload here is prose full of newlines, which is what a verdict result actually is.
    rendered = protocol.encode(
        protocol.response_payload(1, protocol.tool_result("a\nb\nc"))
    )
    assert rendered.endswith("\n") and "\n" not in rendered[:-1]
    assert json.loads(rendered)["result"]["content"][0]["text"] == "a\nb\nc"

    # AR4 becomes structural on the wire by routing through the ONE serializer: a float
    # cannot be rendered at all, it is REFUSED. Demonstrated rather than asserted in prose.
    from argus.store.canonical import CanonicalSerializationError

    with pytest.raises(CanonicalSerializationError):
        protocol.encode(protocol.response_payload(1, {"deep_ratio": 0.5}))

    # A fractional request id is refused rather than echoed — echoing it would put a float
    # on the wire, which the serializer would then refuse, taking the loop down (NFR-R1).
    outcome = protocol.dispatch({"jsonrpc": "2.0", "id": 1.5, "method": "tools/list"})
    assert isinstance(outcome, protocol.Reply)
    assert outcome.payload["id"] is None
    assert outcome.payload["error"]["code"] == protocol.INVALID_REQUEST
