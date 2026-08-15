"""IMPURE stdio shell for the FR35 agent-integration surface (Story 12.6).

This is the ``argus-mcp`` console entry point. It is to :mod:`argus.mcp.protocol` exactly
what ``argus/cli.py`` is to the audit core: the thin impure layer that owns the streams,
the loop and the one call into ``run_audit``. All message construction, dispatch and
rendering is pure and lives next door (AR8).

The loop, and why it is the shape it is
----------------------------------------
A synchronous ``for line in stdin``. **No ``asyncio``, no thread pool, no worker.**
``architecture.md`` §Architectural Boundaries binds the adapter not to introduce a
scheduling or concurrency model of its own — the sequential-canonical execution model is
unchanged — and a single blocking loop is both the compliant shape and the correct one for
a transport whose framing is one message per line over one pipe. It exits promptly and
cleanly on stdin EOF, which the stdio binding names as the primary (and only portable)
graceful-shutdown signal.

**stdout carries JSON-RPC messages and nothing else, and that is enforced structurally.**
The binding says the server MUST NOT write anything to stdout that is not a valid MCP
message, and ``argus/cli.py`` prints its FR18/AR3 summary line **to stdout** today — so
the very code path this adapter calls is one that writes there. Reviewing for that would
be a promise; instead, for the whole duration of any audit this adapter runs, stdout is
REDIRECTED to stderr. A ``print()`` introduced later anywhere beneath ``run_audit`` lands
on stderr, which the binding explicitly permits (*"the server MAY write UTF-8 strings to
stderr for any logging purposes"*), and the protocol channel stays clean. stderr is
redirected alongside it so that the run's disclosures — including the FR36 egress
disclosure, which fires before the first byte leaves — reach the stream this server was
handed rather than the process's, which matters when the caller injected one.

Testable without a subprocess
------------------------------
``main(argv=None, *, stdin=None, stdout=None, stderr=None) -> int`` mirrors
``argus/cli.py::main(argv=None)``'s testable-without-``sys.exit`` shape: it RETURNS the
exit code and the console wrapper does ``sys.exit(main())``. Injecting the three streams
lets the real loop be driven in-process with ``io.StringIO``, so the stdout-purity guard
and the verdict-parity guard both run a REAL audit through the REAL seam cheaply. The
no-listener guard still spawns the real process, because that observable exists only
there.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import sys
from typing import Any, Mapping, TextIO

from argus.cli import (
    PROG,
    build_parser,
    build_request,
    emit_egress_disclosure,
    harden_output_streams,
    resolve_passes,
)
from argus.mcp import protocol
from argus.pipeline import run_audit
from argus.reports.plain_english import deep_pass_enabled

__all__ = ["main", "serve"]

#: Returned when the process was invoked in a way this server cannot serve. It reuses the
#: CLI's reserved crash code (AR3): no verdict reached any consumer.
_CRASH_EXIT_CODE = 1


def _write(stream: TextIO, payload: Mapping[str, Any]) -> None:
    """Write ONE JSON-RPC message, newline-framed, and flush it.

    ``protocol.encode`` already terminates the message with the single ``\\n`` this
    project's canonical serializer appends — the wire framing and the on-disk framing are
    the same newline, from the same function, which is one fewer thing to keep in step.

    The flush is load-bearing rather than defensive: a host reads this pipe line by line
    and a buffered response is an unanswered request from where it is standing.
    """
    stream.write(protocol.encode(payload))
    stream.flush()


def _tool_call_payload(
    invocation: protocol.ToolInvocation, *, stderr: TextIO
) -> dict[str, Any]:
    """Run ONE audit and render its JSON-RPC response (IMPURE — the only such function).

    Everything that can write to stdout runs inside the redirect, so the protocol channel
    cannot be corrupted by anything beneath ``run_audit`` — including ``argparse``'s own
    usage output and the CLI's stdout summary line.

    The two failure classes are kept apart because a model can act on the difference:

    * an argument the derived schema admitted but the REAL parser rejects is a PROTOCOL
      error (``-32602``). It means the schema and the parser disagree, which is a defect in
      this adapter, not in the caller's repository;
    * a TYPED pipeline failure is a TOOL-EXECUTION error (``isError: true``) carrying the
      CLI's own secret-safe wording. An agent handed *"argus: audit failed: …"* has a next
      action (FR37); one handed ``-32603`` does not.

    Nothing broader is caught. The CLI catches exactly ``ValueError`` here, and a surface
    that swallowed more would report "audit failed" for a defect that deserves to surface.
    """
    with contextlib.redirect_stdout(stderr), contextlib.redirect_stderr(stderr):
        try:
            argv = protocol.build_tool_argv(invocation.arguments)
            args = build_parser().parse_args(argv)
        except (SystemExit, argparse.ArgumentError) as exc:
            return protocol.error_payload(
                invocation.request_id,
                protocol.INVALID_PARAMS,
                f"the audit invocation was rejected by the parser: {exc}",
            )

        enabled_passes = resolve_passes(args)
        request = build_request(args, enabled_passes)
        try:
            # The egress disclosure sink is handed over ONLY when the operator opted in,
            # and it is the CLI's OWN callable — not a lookalike. Story 12.2's contract is
            # that there is one consent channel and one sentence that discloses it.
            deep_kwargs = (
                {"disclose": emit_egress_disclosure}
                if deep_pass_enabled(enabled_passes)
                else {}
            )
            verdict = run_audit(request, **deep_kwargs)  # type: ignore[arg-type]
            text = protocol.render_tool_result_text(
                verdict, enabled_passes=enabled_passes
            )
            structured = protocol.tool_structured_content(verdict)
        except ValueError as exc:
            # RepoIntakeError / WorkspaceContainmentError / CanonicalSerializationError /
            # PipelineError / ShipReadinessError are all ValueError subclasses — TYPED and
            # secret-safe (AR10). The wording is the CLI's, character for character, so the
            # two surfaces cannot describe one failure differently.
            return protocol.response_payload(
                invocation.request_id,
                protocol.tool_result(f"{PROG}: audit failed: {exc}", is_error=True),
            )

    return protocol.response_payload(
        invocation.request_id, protocol.tool_result(text, structured)
    )


def serve(stdin: TextIO, stdout: TextIO, stderr: TextIO) -> int:
    """The stdin→stdout loop. Returns the process exit code (IMPURE).

    A blank line carries no message and is skipped rather than refused: it is framing, not
    content. An unparseable line is answered ``-32700`` with a null id, which is what
    JSON-RPC prescribes when the id cannot be known. Neither ends the loop — the server
    survives a bad message and keeps serving; only EOF ends it.
    """
    for raw in stdin:
        line = raw.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError as exc:
            _write(
                stdout,
                protocol.error_payload(
                    None, protocol.PARSE_ERROR, f"could not parse JSON: {exc}"
                ),
            )
            continue

        outcome = protocol.dispatch(message)
        if isinstance(outcome, protocol.Silence):
            continue
        if isinstance(outcome, protocol.Reply):
            _write(stdout, outcome.payload)
            continue
        _write(stdout, _tool_call_payload(outcome, stderr=stderr))
    return 0


def main(
    argv: list[str] | None = None,
    *,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Serve MCP over stdio until EOF; return the process exit code.

    The server takes NO arguments — its entire input is the message stream. An argument is
    therefore refused with a one-line stderr message rather than ignored: silently
    accepting a flag that does nothing is how a caller comes to believe it configured
    something.
    """
    arguments = sys.argv[1:] if argv is None else list(argv)
    in_stream = sys.stdin if stdin is None else stdin
    out_stream = sys.stdout if stdout is None else stdout
    err_stream = sys.stderr if stderr is None else stderr

    # The stdio binding requires UTF-8 in both directions, and the process streams inherit
    # the host console's code page rather than the protocol's requirement. Setting it here
    # is what makes the transport's own contract true on a cp1252 or cp437 console; the
    # hardening beneath it is the CLI's existing defence, reused rather than re-authored,
    # for the human prose that still reaches stderr. A stream that cannot be reconfigured —
    # an injected in-memory buffer — is skipped, which is correct: it has no encoding.
    for stream in (in_stream, out_stream, err_stream):
        try:
            stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        except (AttributeError, ValueError):  # pragma: no cover - non-reconfigurable
            pass
    harden_output_streams(out_stream, err_stream)

    if arguments:
        print(
            f"{PROG}-mcp: this server takes no arguments and speaks JSON-RPC 2.0 over "
            f"stdin/stdout; received {arguments}. Configure it as an MCP stdio server, or "
            f"run `{PROG} audit <repo>` for the command line.",
            file=err_stream,
        )
        return _CRASH_EXIT_CODE

    return serve(in_stream, out_stream, err_stream)


if __name__ == "__main__":  # pragma: no cover - process entrypoint
    sys.exit(main())
