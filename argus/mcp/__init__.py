"""ArgusAgent's MCP (Model Context Protocol) stdio adapter — FR35, first half.

What this package is, and what it deliberately is not
-----------------------------------------------------
This is an **adapter layer** in the ``architecture.md`` §A sense — the same kind of thing
``argus/cli.py`` is, one transport over. ``cli.py`` adapts process ``argv`` + exit codes
onto the audit core; this package adapts **JSON-RPC 2.0 over stdin/stdout** onto the same
core. It contains **no audit logic, no verdict logic and no second decision path**. A
behaviour reachable here and not through the CLI is an architecture violation, not a
feature.

The five binding constraints (``architecture.md`` §A, mirroring PRD §Project
Classification). Each is mechanical here rather than aspirational:

1. **stdio only** — no listener is opened and no port is bound. Nothing under this package
   imports ``socket``, ``socketserver``, ``http.server``, ``wsgiref``, ``ssl`` or an
   ``asyncio`` server API, and the guard exercises the real process to observe the
   behaviour rather than only the symbol table.
2. **No HTTP stack** — every module here is registered in
   ``tests/test_no_web_imports.py::_MODULES_UNDER_GUARD``, so the standing
   ``argus.* ⊬ fastapi/uvicorn/starlette`` isolation gate and ADR #20 cover it unchanged.
   This is also why the official ``mcp`` Python SDK is refused: it declares ``starlette``,
   ``uvicorn`` and ``sse-starlette`` as REQUIRED dependencies (its HTTP transports live in
   the base package), so adopting it would put a web server in this distribution's
   dependency tree and break the very gate this constraint names. The JSON-RPC layer is
   hand-rolled from the standard library instead — see :mod:`argus.mcp.protocol`.
3. **No new authority** — the same ``AuditRequest → run_audit → AuditVerdict`` path, the
   same work-manifest permission boundary (NFR-S4), the same filesystem containment. The
   dependency arrow points INWARD only: this package imports the core, and no core module
   imports this package.
4. **No credential handling** — no key, token or account is accepted or stored. The
   published tool input schema is derived from ``argus.cli.build_parser`` and carries no
   credential-shaped parameter; the opt-in deep pass reads its provider credential through
   the existing adapter's environment contract (``argus/audit/open_llm_adapter.py``).
5. **Verdict parity** — the same repository at the same commit yields the same verdict
   through this surface and through the CLI, and it holds BY CONSTRUCTION rather than by
   discipline: the tool reuses ``argus.cli``'s own request projection, so the CLI's
   defaults govern here too.

Layout (AR8 — the pure/impure split is structural, not narrated)
-----------------------------------------------------------------
* :mod:`argus.mcp.protocol` — PURE. Message parsing, method dispatch, the closed
  supported-version vocabulary, the tool descriptor, the input-schema derivation, the
  argv projection and the result rendering. Every function takes a value and returns a
  value; nothing here reads a stream, a clock or the filesystem.
* :mod:`argus.mcp.server` — IMPURE. ``main()``, the synchronous stdin→stdout loop, the
  stdout-purity guard and the one call into ``run_audit``.

Ships as the console alias ``argus-mcp`` in the SAME distribution as ``argus`` — same
version, same release workflow, same gate evidence. It is not a separate channel and not
a new extra.
"""

from __future__ import annotations

__all__: list[str] = []
