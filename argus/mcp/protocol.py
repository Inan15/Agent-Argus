"""PURE JSON-RPC 2.0 / MCP message layer for the FR35 stdio adapter (Story 12.6).

AR8 — this module is the PURE half of the adapter. Every function here takes a value and
returns a value: it parses no stream, opens no file, reads no clock and dispatches no
audit. The one impure act the whole surface performs — running the audit — is expressed
here as a *value* (:class:`ToolInvocation`) and performed by :mod:`argus.mcp.server`.
That is what lets the entire protocol be driven with plain dicts in a test, with no
subprocess and no I/O.

AR2 / DN-1 — the transport is hand-rolled from the standard library and the official
``mcp`` Python SDK is REFUSED. Measured 2026-08-15: that SDK declares ``starlette``,
``uvicorn`` and ``sse-starlette`` as REQUIRED dependencies, because it carries its HTTP
server transports in the base package. Installing it would put a web server into
``argus-agent``'s dependency tree and break the standing
``argus.* ⊬ fastapi/uvicorn/starlette`` import-isolation gate and ADR #20 — the very
constraints this surface exists to keep true. The cost accepted in exchange is that Argus
owns this file and must track spec revisions itself; the benefit is that constraints 1, 2
and 4 hold BY CONSTRUCTION rather than by discipline. The wire format is one
newline-delimited JSON object per line over two streams, so the whole transport is
``json.loads`` per line in and this project's ONE canonical serializer per message out
(see :func:`encode` — never a second ``json.dumps``, AR4 / cross-cutting #3).

Two protocol eras, both served (DN-2)
--------------------------------------
The specification split on 2026-07-28 and a server that speaks only one era fails half the
hosts in existence:

* **Legacy** (``2025-11-25`` and earlier) — an ``initialize`` request negotiates a version
  and capabilities and is followed by a ``notifications/initialized`` notification. This
  is what the installed host base speaks today.
* **Modern** (``2026-07-28`` and later) — stateless. There is no handshake; every request
  carries its version in ``_meta["io.modelcontextprotocol/protocolVersion"]`` and the
  server accepts or rejects each request independently. Servers MUST implement
  ``server/discover``, and an unsupported version is answered ``-32022``
  ``UnsupportedProtocolVersionError`` with ``data: {supported, requested}``.

Serving both costs almost nothing here because this server keeps **no session state** at
all: ``tools/call`` is answered identically in either era, so the eras differ only in how
a version is declared and in which discovery method exists. The supported set is ONE
CLOSED constant with an exhaustive renderer that RAISES on an unregistered member — the
``exit_code_for_verdict`` / ``render_instrument_disclosure`` house pattern (AR10), never a
fall-through to a default.

One tool, and only one (DN-3)
------------------------------
``audit_repository``. No ``get_status``, no ``explain_verdict``, no ledger reader.
Constraint 3 forbids a capability the CLI lacks, and every additional tool would be
another surface needing its own FR34 disclosure and its own parity proof.

Parity by construction, not by discipline (AC3)
------------------------------------------------
The tool's ``inputSchema`` is DERIVED from ``argus.cli.build_parser`` and the request is
built by handing an argv projection back to that same parser and then through the CLI's
own ``resolve_passes`` / ``build_request``. **The CLI's defaults therefore govern this
surface.** This is load-bearing rather than tidy: ``--coverage-scope`` defaults to
``application`` on the CLI while ``AuditRequest.coverage_scope`` defaults to
``repository`` — a deliberate, announced divergence (Story 10.3 / DN-8, pinned in both
directions by ``TC-ArgusAgent-CLI-001-37b``) — so an adapter that constructed
``AuditRequest(...)`` itself would assess a DIFFERENT POPULATION and could return a
different verdict for an unchanged repository. Nothing here re-declares a single default.
"""

from __future__ import annotations

import argparse
import enum
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from argus import __version__
from argus.cli import PROG, build_parser, summary_line
from argus.reports.plain_english import render_ship_readiness
from argus.store.canonical import dumps as canonical_dumps
from argus.verdict.negative_assurance import (
    INSTRUMENT_STATUS,
    render_instrument_disclosure,
)
from argus.verdict.verdict_gate import AuditVerdict

__all__ = [
    "ArgumentKind",
    "ArgumentSpec",
    "JSONRPC_VERSION",
    "McpProtocolError",
    "ProtocolEra",
    "ProtocolVersion",
    "Reply",
    "SUPPORTED_PROTOCOL_VERSIONS",
    "Silence",
    "TOOL_NAME",
    "ToolInvocation",
    "argument_errors",
    "audit_argument_specs",
    "build_tool_argv",
    "build_tool_descriptor",
    "derive_input_schema",
    "dispatch",
    "encode",
    "error_payload",
    "protocol_era",
    "render_tool_result_text",
    "response_payload",
    "tool_result",
    "tool_structured_content",
]

JSONRPC_VERSION = "2.0"

#: The MCP tool this server publishes. Exactly one (DN-3). The name matches the
#: specification's ``[A-Za-z0-9_.-]{1,128}`` rule.
TOOL_NAME = "audit_repository"

#: The ``audit`` sub-command is the CLI's only V1 sub-command and therefore the only
#: surface this adapter can project onto. Named once, here.
AUDIT_SUBCOMMAND = "audit"


# ─────────────────────────────────────────────────────────────────────────────
# The CLOSED protocol-version vocabulary, rendered exhaustively (AC1, AR10)
# ─────────────────────────────────────────────────────────────────────────────


class ProtocolVersion(str, enum.Enum):
    """Every MCP revision this server speaks. A CLOSED set — adding one is an edit here."""

    LEGACY_2025_11_25 = "2025-11-25"
    MODERN_2026_07_28 = "2026-07-28"


class ProtocolEra(str, enum.Enum):
    """Which handshake shape a revision uses. Closed, and exhaustive over the versions."""

    LEGACY = "legacy"
    MODERN = "modern"


SUPPORTED_PROTOCOL_VERSIONS: tuple[str, ...] = tuple(
    member.value for member in ProtocolVersion
)

#: What ``initialize`` answers when a legacy client names no version at all. The LEGACY
#: revision, deliberately: a client that omits the field is by definition not speaking the
#: stateless modern revision, which carries its version on every request.
DEFAULT_PROTOCOL_VERSION: str = ProtocolVersion.LEGACY_2025_11_25.value

#: Where a modern (stateless) request declares its protocol version.
PROTOCOL_VERSION_META_KEY = "io.modelcontextprotocol/protocolVersion"

_ERA_BY_VERSION: dict[ProtocolVersion, ProtocolEra] = {
    ProtocolVersion.LEGACY_2025_11_25: ProtocolEra.LEGACY,
    ProtocolVersion.MODERN_2026_07_28: ProtocolEra.MODERN,
}


class McpProtocolError(ValueError):
    """A TYPED failure in the protocol layer (AR10).

    A ``ValueError`` subclass, matching every other typed failure in this package
    (``NegativeAssuranceError``, ``ShipReadinessError``, ``PipelineError``) — so the one
    place that must never crash, the stdin loop, already degrades it to a secret-safe
    message rather than a traceback.
    """


def protocol_era(version: ProtocolVersion) -> ProtocolEra:
    """Which handshake era *version* belongs to (PURE, exhaustive over the enum).

    RAISES :class:`McpProtocolError` on an unregistered member rather than returning a
    silent default. A fall-through would answer a revision nobody registered with the
    COMFORTABLE wrong answer — the exact defect class ``exit_code_for_verdict`` and
    ``render_instrument_disclosure`` already refuse (AR10).
    """
    try:
        return _ERA_BY_VERSION[version]
    except (KeyError, TypeError) as exc:
        raise McpProtocolError(
            f"no protocol era registered for {version!r}; the era map must be exhaustive "
            f"over ProtocolVersion (supported: {list(SUPPORTED_PROTOCOL_VERSIONS)})"
        ) from exc


# ─────────────────────────────────────────────────────────────────────────────
# JSON-RPC error codes. -32700..-32600 are the JSON-RPC 2.0 reserved range; -32022 is
# MCP's own UnsupportedProtocolVersionError.
# ─────────────────────────────────────────────────────────────────────────────

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
UNSUPPORTED_PROTOCOL_VERSION = -32022


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch outcomes — a closed three-member algebra, so the loop has no default branch
# ─────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Reply:
    """A complete JSON-RPC payload the loop should write to stdout verbatim."""

    payload: dict[str, Any]


@dataclass(frozen=True)
class Silence:
    """A notification. It is CONSUMED and never answered — answering one is a protocol bug."""

    reason: str


@dataclass(frozen=True)
class ToolInvocation:
    """A validated ``tools/call``: the ONE outcome that needs the impure world.

    Carrying it as a value is what keeps this module pure. The loop performs the audit
    and hands the verdict back to :func:`render_tool_result_text` /
    :func:`tool_structured_content`, which are pure again.
    """

    request_id: Any
    arguments: dict[str, Any]


Outcome = Reply | Silence | ToolInvocation


# ─────────────────────────────────────────────────────────────────────────────
# Rendering
# ─────────────────────────────────────────────────────────────────────────────


def encode(payload: Mapping[str, Any]) -> str:
    """Render one JSON-RPC message as ONE line, newline-terminated (PURE).

    **This routes through ``argus.store.canonical.dumps`` rather than calling
    ``json.dumps`` itself, and that is a correctness decision, not a style one.** This
    project has exactly ONE serializer (AR4 / cross-cutting #3), pinned by
    ``TC-ArgusAgent-STORE-001-40``, and a second one with its own kwargs is how NFR-P1 dies.
    Three things come free by reusing it:

    * ``sort_keys=True`` + compact separators, so a message renders byte-identically on
      every host — determinism on the wire, matching determinism on disk;
    * **``float`` is REFUSED at the serializer**, raising ``CanonicalSerializationError``
      rather than emitting one. AR4's "no float on any surface this project emits" becomes
      structural on this transport instead of merely tested;
    * ``set`` / ``datetime`` / ``UUID`` are refused for the same reason they are on disk.

    The trailing ``\\n`` ``dumps`` already appends IS the stdio framing, so the wire format
    and the on-disk format agree down to the line terminator. ``json.dumps`` escapes every
    control character inside a string, so a message can never contain an embedded newline —
    which is what makes newline framing safe.

    ``canonical.dumps`` emits ``ensure_ascii=False``, so the message stream is real UTF-8
    rather than ASCII escapes; the MCP stdio binding requires UTF-8, and
    :func:`argus.mcp.server.main` configures its output stream accordingly.
    """
    return canonical_dumps(dict(payload))


def response_payload(request_id: Any, result: Mapping[str, Any]) -> dict[str, Any]:
    """A JSON-RPC success response (PURE)."""
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": dict(result)}


def error_payload(
    request_id: Any, code: int, message: str, data: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """A JSON-RPC error response (PURE). ``data`` is omitted entirely when absent."""
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = dict(data)
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": error}


# ─────────────────────────────────────────────────────────────────────────────
# The accepted surface, DERIVED from `build_parser` and never hand-listed (AC3)
# ─────────────────────────────────────────────────────────────────────────────


class ArgumentKind(str, enum.Enum):
    """The four argparse shapes the ``audit`` sub-command uses. Closed."""

    POSITIONAL = "positional"
    FLAG = "flag"  # store_true
    VALUE = "value"  # a single value
    REPEATABLE = "repeatable"  # action="append"


@dataclass(frozen=True)
class ArgumentSpec:
    """One accepted argument, read off the REAL parser (PURE data).

    ``dest`` is the JSON property name, deliberately: it is argparse's own normalised
    identifier, so the schema cannot drift from the namespace ``build_request`` projects.
    """

    dest: str
    option: str  # the long option spelling; "" for the positional
    kind: ArgumentKind
    json_type: str
    choices: tuple[str, ...]
    description: str
    required: bool


def _audit_subparser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Locate the ``audit`` sub-parser inside *parser*.

    Uses argparse private API (``_actions`` / ``_SubParsersAction``), which is the only
    way to walk a parser — argparse exposes no public introspection. The risk that a
    future argparse changes it is answered by RAISING rather than returning nothing: a
    silently empty walk would publish an empty tool schema, which is the failure mode that
    matters. The walk is confined to this one function so there is a single site to fix.
    """
    for action in parser._actions:  # noqa: SLF001 - argparse exposes no public walk
        if not isinstance(action, argparse._SubParsersAction):  # noqa: SLF001 - same
            continue
        sub = action.choices.get(AUDIT_SUBCOMMAND)
        if isinstance(sub, argparse.ArgumentParser):
            return sub
    raise McpProtocolError(
        f"the {AUDIT_SUBCOMMAND!r} sub-command could not be located on the parser, so the "
        "tool schema would be derived from nothing. Fix the derivation; never publish an "
        "empty schema."
    )


def audit_argument_specs(
    parser: argparse.ArgumentParser | None = None,
) -> tuple[ArgumentSpec, ...]:
    """Every argument the ``audit`` sub-command accepts, derived from the parser (PURE).

    THE single source for both the published ``inputSchema`` and the argv projection, so
    the two cannot describe different surfaces. A flag added to ``build_parser`` appears
    in both with no edit here — and ``TC-ArgusAgent-MCP-001-06`` fails if it ever does not.
    """
    sub = _audit_subparser(parser if parser is not None else build_parser())
    specs: list[ArgumentSpec] = []
    for action in sub._actions:  # noqa: SLF001 - argparse exposes no public walk
        if isinstance(action, argparse._HelpAction):  # noqa: SLF001 - same
            continue
        description = " ".join((action.help or "").split())
        choices = tuple(str(choice) for choice in (action.choices or ()))
        if not action.option_strings:
            specs.append(
                ArgumentSpec(
                    dest=action.dest,
                    option="",
                    kind=ArgumentKind.POSITIONAL,
                    json_type="string",
                    choices=choices,
                    description=description,
                    required=True,
                )
            )
            continue
        option = action.option_strings[-1]
        if action.nargs == 0:
            kind, json_type = ArgumentKind.FLAG, "boolean"
        elif isinstance(action, argparse._AppendAction):  # noqa: SLF001 - same
            kind, json_type = ArgumentKind.REPEATABLE, "array"
        elif action.type is int:
            kind, json_type = ArgumentKind.VALUE, "integer"
        else:
            kind, json_type = ArgumentKind.VALUE, "string"
        specs.append(
            ArgumentSpec(
                dest=action.dest,
                option=option,
                kind=kind,
                json_type=json_type,
                choices=choices,
                description=description,
                required=False,
            )
        )
    if not specs:
        raise McpProtocolError(
            "no arguments were derived from the parser, so the published tool schema would "
            "be empty. A surface that accepts nothing is not the honest answer here."
        )
    return tuple(specs)


def derive_input_schema(
    parser: argparse.ArgumentParser | None = None,
) -> dict[str, Any]:
    """The tool's JSON-Schema ``inputSchema``, DERIVED from the parser (PURE).

    **No property carries a ``default``, and that omission is the design.** Publishing a
    default here would be re-declaring it: the value that governs is whatever
    ``build_parser`` gives ``parse_args`` when the property is absent, and a second copy in
    the schema is a second thing to keep true. It is also precisely where a divergence
    would hide, because ``--coverage-scope``'s CLI default (``application``) is
    deliberately not the model's (``repository``) — Story 10.3 / DN-8.

    ``additionalProperties`` is ``False`` so an unknown argument is refused rather than
    silently dropped, which is the difference between an agent being told its call was
    wrong and an agent believing it audited something it did not.
    """
    properties: dict[str, Any] = {}
    required: list[str] = []
    for spec in audit_argument_specs(parser):
        prop: dict[str, Any] = {"type": spec.json_type}
        if spec.kind is ArgumentKind.REPEATABLE:
            prop["items"] = {"type": "string"}
        if spec.choices:
            prop["enum"] = list(spec.choices)
        if spec.description:
            prop["description"] = spec.description
        properties[spec.dest] = prop
        if spec.required:
            required.append(spec.dest)
    return {
        "type": "object",
        "properties": properties,
        "required": sorted(required),
        "additionalProperties": False,
    }


def argument_errors(
    arguments: Any, parser: argparse.ArgumentParser | None = None
) -> tuple[str, ...]:
    """Every way *arguments* fails the derived schema, as human-readable strings (PURE).

    Deliberately returns ALL of them rather than the first: an agent that is told about one
    mistake at a time takes one round trip per mistake.
    """
    if not isinstance(arguments, Mapping):
        return ("`arguments` must be a JSON object",)
    specs = {spec.dest: spec for spec in audit_argument_specs(parser)}
    problems: list[str] = []
    for name in sorted(set(arguments) - set(specs)):
        problems.append(
            f"unknown argument {name!r}; accepted: {sorted(specs)}"
        )
    for dest, spec in sorted(specs.items()):
        if dest not in arguments:
            if spec.required:
                problems.append(f"missing required argument {dest!r}")
            continue
        value = arguments[dest]
        problems.extend(_value_errors(spec, value))
    return tuple(problems)


def _value_errors(spec: ArgumentSpec, value: Any) -> tuple[str, ...]:
    """Type/enum problems for one argument value (PURE).

    ``bool`` is rejected for an integer property on purpose: in Python ``True`` IS an
    ``int``, so a naive check would let ``{"budget": true}`` through and silently configure
    a ceiling of 1.
    """
    if spec.json_type == "boolean":
        if not isinstance(value, bool):
            return (f"{spec.dest!r} must be a boolean",)
        return ()
    if spec.json_type == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            return (f"{spec.dest!r} must be an integer",)
        return ()
    if spec.json_type == "array":
        if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
            return (f"{spec.dest!r} must be an array of strings",)
        if not all(isinstance(item, str) for item in value):
            return (f"{spec.dest!r} must be an array of strings",)
        return ()
    if not isinstance(value, str):
        return (f"{spec.dest!r} must be a string",)
    if spec.choices and value not in spec.choices:
        return (f"{spec.dest!r} must be one of {list(spec.choices)}",)
    return ()


def build_tool_argv(
    arguments: Mapping[str, Any], parser: argparse.ArgumentParser | None = None
) -> list[str]:
    """Project validated tool *arguments* back onto an argv the REAL parser accepts (PURE).

    This is the mechanism that makes parity structural. The adapter never builds an
    ``AuditRequest``; it builds an argv and hands it to ``build_parser().parse_args``,
    after which ``resolve_passes`` and ``build_request`` — the CLI's own functions — do
    exactly what they do for a terminal user. Every default that governs a CLI run
    therefore governs this one, including the announced ``--coverage-scope`` divergence
    (DN-8) that a hand-built request would silently get wrong.

    An argument that is ABSENT contributes nothing to the argv, which is how the parser's
    default gets to apply. A ``False`` boolean is likewise absent from the argv: a
    ``store_true`` flag has no negative spelling, and its absence IS the ``False``.
    """
    positionals: list[str] = []
    options: list[str] = []
    for spec in audit_argument_specs(parser):
        if spec.dest not in arguments:
            continue
        value = arguments[spec.dest]
        if spec.kind is ArgumentKind.POSITIONAL:
            positionals.append(str(value))
        elif spec.kind is ArgumentKind.FLAG:
            if value:
                options.append(spec.option)
        elif spec.kind is ArgumentKind.REPEATABLE:
            for item in value:
                options.extend((spec.option, str(item)))
        else:
            options.extend((spec.option, str(value)))
    return [AUDIT_SUBCOMMAND, *positionals, *options]


# ─────────────────────────────────────────────────────────────────────────────
# The tool descriptor, and the results it produces (AC5, DN-4, DN-5, DN-6)
# ─────────────────────────────────────────────────────────────────────────────

TOOL_TITLE = "Audit a repository and return the release-readiness verdict"

_TOOL_PURPOSE = (
    "Runs the ArgusAgent deterministic release-readiness audit over a local repository "
    "and returns the same verdict, exit code and coverage figures the `argus audit` "
    "command line returns for the same arguments. It reports whether the audited "
    "coverage envelope contains a release-blocking finding; it never claims the code is "
    "correct."
)

# DN-4 / NFR-S6 — the egress statement lives in the tool DESCRIPTION because on this
# transport that is what an agent reads BEFORE it can choose `deep_audit: true`. The
# unchanged stderr disclosure still fires at dispatch time, before the first byte leaves;
# this is the earlier of the two, not a replacement for it.
_EGRESS_STATEMENT = (
    "`deep_audit` is the ONLY opt-in to egress and is off by default, always. Setting it "
    "true SENDS REPOSITORY METADATA TO A THIRD-PARTY PROVIDER, and the run states what "
    "will be transmitted and to which provider on stderr before the first byte leaves. "
    "No credential is accepted, stored or read by this surface: the provider credential "
    "is read only from the existing adapter's environment contract."
)

# DN-6 — a limitation that is stated is a limitation; one that is left to be discovered is
# a defect. This server has no concurrency model of its own (architecture §Architectural
# Boundaries), so a cancellation cannot interrupt work already in flight.
_CANCELLATION_STATEMENT = (
    "Cancellation: `notifications/cancelled` is accepted and consumed, and — correctly — "
    "never answered. It cannot interrupt an audit already running: this server is "
    "single-threaded by architectural mandate and reads the next message only after the "
    "current audit completes."
)


def build_tool_descriptor(
    parser: argparse.ArgumentParser | None = None,
) -> dict[str, Any]:
    """The one published tool, with its derived schema and its FR34 disclosure (PURE).

    The disclosure is in the DESCRIPTION as well as on every verdict-bearing result,
    because an agent reads the description BEFORE it can decide to call the tool — which
    is when a statement about how far the instrument itself has been validated is worth
    something. It is rendered from the ONE constant in
    ``argus/verdict/negative_assurance.py`` and never transcribed (AI-E9-7): a prose copy
    would go stale the day Epic 13 clears the precision gate, and the surface would then
    publish a disclosure the tool has retired.
    """
    description = " ".join(
        (
            _TOOL_PURPOSE,
            _EGRESS_STATEMENT,
            _CANCELLATION_STATEMENT,
            render_instrument_disclosure(INSTRUMENT_STATUS),
        )
    )
    return {
        "name": TOOL_NAME,
        "title": TOOL_TITLE,
        "description": description,
        "inputSchema": derive_input_schema(parser),
    }


def render_tool_result_text(
    verdict: AuditVerdict, *, enabled_passes: tuple[str, ...] | list[str] = ()
) -> str:
    """The human-and-machine-readable body of a verdict-bearing result (PURE).

    DN-5 — this carries the CLI's INFORMATION SET, not the verdict object. No
    ``model_dump()``, no ``ordered_findings``: the three renderers below are exactly the
    three the CLI calls, in the order it calls them, so NFR-S1 secret-safety is INHERITED
    rather than re-argued and the two surfaces cannot describe one run differently.

    The FR34 instrument disclosure is appended unconditionally, including on a clean
    ``RELEASE_READY`` run — a disclosure that appears only when something is wrong is one a
    reader learns nothing from.
    """
    lines = [
        summary_line(
            verdict.verdict.value,
            verdict.deep_ratio,
            verdict.blocking_finding_count,
            verdict.coverage_scope,
        )
    ]
    lines.extend(render_ship_readiness(verdict, enabled_passes=enabled_passes))
    lines.append(render_instrument_disclosure(INSTRUMENT_STATUS))
    return "\n".join(lines)


def tool_structured_content(verdict: AuditVerdict) -> dict[str, Any]:
    """The machine-readable half of a verdict-bearing result (PURE, AR4 — no ``float``).

    Every ratio travels as the exact ``"num/den"`` string the CLI's summary line prints.
    ``Fraction`` has no JSON form and a ``float`` would be a lie about an exact quantity,
    which AR4 forbids on every surface this project emits.

    Secret-safe by construction (NFR-S1): a verdict token, exact ratios, counts, a scope
    id and an exit code. No finding, no source byte, no absolute host path.
    """
    payload: dict[str, Any] = {
        "verdict": verdict.verdict.value,
        "exit_code": verdict.exit_code,
        "deep_ratio": str(verdict.deep_ratio),
        "blocking_findings": verdict.blocking_finding_count,
    }
    scope = verdict.coverage_scope
    if scope is not None:
        payload["assessed_deep_ratio"] = str(scope.assessed_deep_ratio)
        payload["scope"] = scope.scope_id
        payload["held_out"] = scope.excluded_count
    return payload


def tool_result(
    text: str,
    structured: Mapping[str, Any] | None = None,
    *,
    is_error: bool = False,
) -> dict[str, Any]:
    """Wrap *text* as an MCP tool result (PURE).

    ``resultType: "complete"`` is the modern revision's additive field; a legacy client
    ignores a field it does not know, so ONE result shape serves both eras (DN-2).

    ``isError`` is the TOOL-EXECUTION error channel and is deliberately not a JSON-RPC
    error: a model that receives ``isError: true`` with *"argus: audit failed: …"* has a
    next action, and one that receives ``-32603`` does not. FR37 forbids a terminal
    outcome with no next action.
    """
    result: dict[str, Any] = {
        "resultType": "complete",
        "isError": is_error,
        "content": [{"type": "text", "text": text}],
    }
    if structured is not None:
        result["structuredContent"] = dict(structured)
    return result


def server_info() -> dict[str, Any]:
    """``serverInfo`` for both handshakes (PURE).

    The version is ``argus.__version__`` — the ONE version source. A second constant here
    would be a second thing to bump, and the day it was not bumped a host would be told
    the wrong version of the tool that produced its verdict.
    """
    return {"name": PROG, "version": __version__}


def _capabilities() -> dict[str, Any]:
    """This server offers tools and nothing else: no resources, no prompts, no sampling."""
    return {"tools": {"listChanged": False}}


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch
# ─────────────────────────────────────────────────────────────────────────────


def declared_protocol_version(message: Mapping[str, Any]) -> str | None:
    """The protocol version *message* declares, in EITHER era, or ``None`` (PURE).

    Modern requests carry it in ``_meta``; a legacy ``initialize`` carries it in its
    params. Nothing else declares one, and a request that declares nothing is served
    rather than refused — the legacy era's whole point is that the handshake carries it
    once.
    """
    meta = message.get("_meta")
    if isinstance(meta, Mapping):
        declared = meta.get(PROTOCOL_VERSION_META_KEY)
        if isinstance(declared, str):
            return declared
    if message.get("method") == "initialize":
        params = message.get("params")
        if isinstance(params, Mapping):
            requested = params.get("protocolVersion")
            if isinstance(requested, str):
                return requested
    return None


def dispatch(message: Any) -> Outcome:
    """Turn one parsed JSON-RPC message into an :data:`Outcome` (PURE).

    The whole method surface, and the whole error surface, in one fold. A notification —
    a message with no ``id`` — always yields :class:`Silence`, including when its method is
    unknown: answering a notification is a protocol violation regardless of how wrong the
    notification was.
    """
    if not isinstance(message, Mapping):
        return Reply(
            error_payload(
                None,
                INVALID_REQUEST,
                "a JSON-RPC message must be a single JSON object; this server does not "
                "accept batches (they were removed from MCP in 2025-11-25)",
            )
        )

    is_notification = "id" not in message
    request_id = message.get("id")
    method = message.get("method")

    # JSON-RPC 2.0: an id is a String, a Number without a fractional part, or Null. A
    # fractional id is refused with a NULL id rather than echoed, because echoing it would
    # put a `float` on a surface AR4 forbids one on — and the canonical serializer would
    # refuse to render the message at all, taking the loop down with it (NFR-R1).
    if not is_notification and (
        isinstance(request_id, bool)
        or not isinstance(request_id, (str, int, type(None)))
    ):
        return Reply(
            error_payload(
                None,
                INVALID_REQUEST,
                "a request id must be a string, an integer or null",
            )
        )

    if message.get("jsonrpc") != JSONRPC_VERSION or not isinstance(method, str):
        if is_notification:
            return Silence("a malformed notification is consumed, never answered")
        return Reply(
            error_payload(
                request_id,
                INVALID_REQUEST,
                f"every message must carry jsonrpc={JSONRPC_VERSION!r} and a string method",
            )
        )

    declared = declared_protocol_version(message)
    if declared is not None and declared not in SUPPORTED_PROTOCOL_VERSIONS:
        if is_notification:
            return Silence("an unsupported-version notification is consumed, never answered")
        return Reply(
            error_payload(
                request_id,
                UNSUPPORTED_PROTOCOL_VERSION,
                "Unsupported protocol version",
                {
                    "supported": list(SUPPORTED_PROTOCOL_VERSIONS),
                    "requested": declared,
                },
            )
        )

    if is_notification:
        return Silence(f"notification {method!r} consumed")

    if method == "initialize":
        return Reply(
            response_payload(
                request_id,
                {
                    "protocolVersion": declared or DEFAULT_PROTOCOL_VERSION,
                    "capabilities": _capabilities(),
                    "serverInfo": server_info(),
                },
            )
        )

    if method == "server/discover":
        return Reply(
            response_payload(
                request_id,
                {
                    "serverInfo": server_info(),
                    "capabilities": _capabilities(),
                    "supportedVersions": list(SUPPORTED_PROTOCOL_VERSIONS),
                },
            )
        )

    if method == "tools/list":
        # Deterministic order, which this project would want even if the specification
        # did not merely recommend it.
        return Reply(response_payload(request_id, {"tools": [build_tool_descriptor()]}))

    if method == "tools/call":
        return _dispatch_tool_call(request_id, message.get("params"))

    return Reply(
        error_payload(
            request_id,
            METHOD_NOT_FOUND,
            f"unknown method {method!r}",
            {"supportedVersions": list(SUPPORTED_PROTOCOL_VERSIONS)},
        )
    )


def _dispatch_tool_call(request_id: Any, params: Any) -> Outcome:
    """Validate a ``tools/call`` into a :class:`ToolInvocation` or a ``-32602`` (PURE)."""
    if not isinstance(params, Mapping):
        return Reply(
            error_payload(request_id, INVALID_PARAMS, "`params` must be a JSON object")
        )
    name = params.get("name")
    if name != TOOL_NAME:
        return Reply(
            error_payload(
                request_id,
                INVALID_PARAMS,
                f"unknown tool {name!r}",
                {"tools": [TOOL_NAME]},
            )
        )
    arguments = params.get("arguments", {})
    problems = argument_errors(arguments)
    if problems:
        return Reply(
            error_payload(
                request_id,
                INVALID_PARAMS,
                f"invalid arguments for {TOOL_NAME!r}",
                {"errors": list(problems)},
            )
        )
    return ToolInvocation(request_id=request_id, arguments=dict(arguments))
