---
baseline_commit: 54b96d79787d58f5176367bc348cc89eeedf08fa
---

# Story 12.6: A coding agent can run the audit and read the verdict

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo.** ArgusAgent (formerly APAA) is a self-contained headless audit
> tool extracted from the Minions monorepo into its own repository (`Agent-Argus`, distribution
> `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`.
>
> 🔵 **This is the SIXTH story of Epic 12.** 12.1 (`done`) gave `argus/pipeline.py` its NFR-M1
> headroom and closed `DF-8-5-B`; 12.2 (`done`) wired the opt-in deep pass (FR36); 12.3 (`done`)
> wired the stage memoization cache (FR27/NFR-D1); 12.4 (`done`) delivered FR37 — every terminal
> outcome names its next action — plus the three-population ingestion-boundary disclosure; 12.5
> (`done`) made the default install ground all ten claimed languages (NFR-P3).
> **This story delivers the FIRST HALF of FR35: an MCP server over stdio, shipped as an entry point
> in the existing distribution.** The second half — packaged assistant command assets — is
> **Story 12.7's** and is explicitly out of scope here. **It publishes nothing: 12.9 publishes.**
>
> **Epic dependency flow (`epics.md:2167`): 12.4 → 12.6 → 12.7.** 12.4 is `done`, so this story is
> unblocked.

---

## Story

As a developer building with a coding agent,
I want the agent to run the audit and act on the result itself,
So that the loop that wrote the code contains something that checks it.

**Why this is one story.** Every clause serves **FR35's first shipped form**: *a coding agent can
invoke an audit and consume the verdict through a local agent-integration surface, without a human
relaying it* — bounded by the four §Project Classification constraints (stdio only, no HTTP stack,
no new authority, no credential handling) and by the fifth binding constraint the architecture adds
(verdict parity, pinned by test). The protocol adapter, its entry point, its parity proof and its
FR34 disclosure are one capability; splitting them would ship a surface that either cannot be
reached, cannot be trusted, or lies about the instrument that produced its verdict.

**What it is NOT.**

| Not this story | Whose it is | Authority |
|---|---|---|
| Packaged assistant command assets (`/audit …` slash commands), any registration mechanism, any wheel **data asset** | **Story 12.7** | `epics.md:2390-2411`; architecture §A calls command assets *"configuration data, not an entry point"* |
| Operator-error **diagnosis** prose on the CLI (bad path, unreadable repo, **missing grammar**, absent key), `--help` text, a first-run docs page | **Story 12.8** | `epics.md:2431` names all four causes; `argus/shared/grammar_status.py:62` and Story 12.5's Dev Agent Record both already fence this by name |
| Publishing anything — a tag, an index upload, a marketplace listing, a release | **Story 12.9** | `epics.md:2446-2473`; Epic 11 shipped five stories about publishing without publishing anything, and that discipline holds here |
| Any new **assurance** capability, verdict semantics, decision-table change, new detector or new report | Nobody — forbidden | PRD §V1.5: *"this epic adds no new assurance capability"*; `epics.md:2159` |
| An HTTP / SSE / streamable-HTTP transport, a hosted service, a bound port | **V4 at the earliest** | PRD §Project Classification excludes the hosted surface; architecture §A: *"choosing stdio is what keeps constraints 1–4 true by construction rather than by discipline"* |

---

## Acceptance Criteria

### AC1: An MCP stdio server ships as an entry point in the same distribution (FR35)

- **Given** FR35 and architecture §A *"Entry points — two, converging on one core"*
- **When** this story completes
- **Then** `argus/mcp/` exists as an **adapter layer** (impure I/O wiring; no audit logic, no verdict
  logic, no second decision path) and `pyproject.toml [project.scripts]` gains **exactly one** new
  console alias, `argus-mcp = "argus.mcp.server:main"`, in the **same distribution** — same version,
  same release workflow, same gate evidence. It is **not** a separate channel and **not** a new extra.
- **Then** the server speaks **JSON-RPC 2.0 over stdin/stdout**: one message per line, UTF-8, no
  embedded newlines, and it handles at minimum
  `initialize` + `notifications/initialized` (legacy era), `server/discover` (modern era),
  `tools/list`, `tools/call`, and `notifications/cancelled` (accepted; a notification is **never**
  answered). An unknown method returns JSON-RPC `-32601`; an unparseable line returns `-32700`; a
  malformed `tools/call` returns `-32602`.
- **Then** the set of supported protocol versions is a **CLOSED constant in one module**, rendered
  exhaustively (the `render_instrument_disclosure` / `exit_code_for_verdict` house pattern — AR10:
  raise on an unregistered member, never fall through to a default), and a request declaring a
  version outside it receives `-32022` `UnsupportedProtocolVersionError` whose `data.supported`
  names the set.
- **Then** `README.md` documents the new alias — both the literal `` `argus-mcp` `` and the literal
  target `argus.mcp.server:main` — because `TC-ArgusAgent-DOCS-001-56` closes over
  `[project.scripts]` and fails on an undocumented alias.

### AC2: The four §Project Classification constraints hold mechanically, not aspirationally

- **Given** FR35's bound and architecture §A's five *"Binding constraints"*
- **Then (2.1 — stdio only)** no network listener is opened and no port is bound. Asserted by a
  gate over `argus/mcp/**`'s static import closure (no `socket`, `socketserver`, `http.server`,
  `wsgiref`, `asyncio` server API, `ssl`) **and** by exercising the real server process end to end,
  so the observable is behaviour and not only a symbol table (AI-E11-1 clause (i)).
- **Then (2.2 — no HTTP stack)** the `argus.* ⊬ fastapi / uvicorn / starlette` import-isolation gate
  and **ADR #20 hold unchanged, asserted by the EXISTING committed gate**: every new `argus.mcp.*`
  module is **appended to `_MODULES_UNDER_GUARD` in `tests/test_no_web_imports.py`**. Extend the
  guard, never fork it (AI-E3-6 / AR7).
- **Then (2.3 — no new authority)** the MCP surface exposes **no capability the CLI lacks**: the same
  `AuditRequest → run_audit → AuditVerdict` path, the same work-manifest permission boundary
  (NFR-S4), the same filesystem containment. The adapter's dependency arrow points **inward only**
  and the pure core never imports it.
- **Then (2.4 — no credential handling)** the server accepts and stores **no** key, token or account.
  A gate asserts no credential-shaped parameter exists anywhere in the published tool input schema.
  The deep pass reads its provider credential through the **existing adapter's environment
  contract** (`argus/audit/open_llm_adapter.py`), never through this surface.

### AC3: Verdict parity — same repository, same commit, same verdict, pinned by test

- **Given** FR35's parity requirement and architecture §A constraint 5
- **Then** the same repository at the same commit yields the **same** `verdict`, `deep_ratio`,
  `blocking_findings`, `assessed_deep_ratio` / `scope` / `held_out` (when the assessment was
  narrowed) and `exit_code` through the MCP surface and through the CLI — driven through **both real
  entry points** (`argus.cli.main(argv)` and the MCP server's own stdin→stdout loop) over a real
  fixture repository, **never** through one shared helper called twice. A parity test whose
  observable cannot move when the two surfaces diverge is vacuous (AI-E11-1 clause (i)).
- **Then** parity is true **by construction, not by discipline**: the MCP tool builds its request by
  **reusing `argus/cli.py::build_parser` and the CLI's own request projection**, so the **CLI
  defaults govern this surface**. ⚠️ **This is load-bearing and is the single most likely way to
  ship a silently divergent verdict:** `--coverage-scope` defaults to `application` on the CLI while
  `AuditRequest.coverage_scope` defaults to `repository` — a deliberate, announced divergence
  (**Story 10.3 / DN-8**) pinned in *both* directions by `TC-ArgusAgent-CLI-001-37b`. An MCP adapter
  that constructs `AuditRequest(...)` directly would assess a **different population** and could
  return a different verdict on an unchanged repository. Do not re-declare a single default.
- **Then** the tool's `inputSchema` is **DERIVED from `build_parser`, never hand-listed**: a flag
  added to the parser without a corresponding schema entry fails a test. This is the
  `TC-ArgusAgent-CLI-001-35` closure pattern (equality, both directions) applied to the second
  invocation surface, and it is what stops the two surfaces drifting apart one flag at a time.

### AC4: stdout carries JSON-RPC messages and nothing else

- **Given** the stdio binding's *"the server **MUST NOT** write anything to its stdout that is not a
  valid MCP message"*, and given that `argus/cli.py` prints its FR18/AR3 summary line **to stdout**
  today
- **When** a real audit runs through the MCP server over a fixture repository
- **Then** **every** line the server writes to stdout parses as a single valid JSON-RPC message —
  asserted by a test that drives the real loop and parses **every** stdout line, not a sampled one.
- **Then** the channel is protected structurally, not by review: stdout is redirected to stderr for
  the duration of any audit the adapter runs, so a `print()` introduced later anywhere under
  `run_audit` cannot corrupt the protocol. **Non-vacuity is mandatory** (AI-E11-1 clause (ii)): the
  guard is proven by a synthetic that writes to `sys.stdout` mid-audit and shows the channel stays
  clean — a guard that has never seen the defect move its observable proves nothing.
- **Then** diagnostics, disclosures and the human register go to **stderr**, which the binding
  explicitly permits (*"the server MAY write UTF-8 strings to stderr for any logging purposes"*).

### AC5: FR34 — the disclosure is present on this surface, and Story 11.1's enumeration covers it

- **Given** FR34 and architecture §Instrument-status enforcement: *"no verdict surface ships without
  disclosure — every user-facing surface that emits a verdict also states how the tool's own findings
  have been validated, and the tool cannot emit a verdict on a surface that omits it"*
- **Then** every verdict-bearing tool result carries `render_instrument_disclosure(INSTRUMENT_STATUS)`
  taken from the **ONE constant** in `argus/verdict/negative_assurance.py` — never a transcribed copy
  (AI-E9-7).
- **Then** the disclosure is **also** stated in the `tools/list` tool description, so the agent reads
  it *before* it can decide to call the tool, not only after it has a verdict in hand.
- **Then** `_MCP_DISCLOSURE_SURFACES` in `tests/test_instrument_disclosure.py` is populated with
  every surface `TC-ArgusAgent-DOCS-001-49` now resolves, and `-49` goes **green because the surfaces
  emit the disclosure**. ⚠️ **`-49`'s registered-surface loop has never executed** (it carries
  `# pragma: no cover - empty until 12.6`) and, **as written, it asserts the literal short disclosure
  text is a substring of the registered module's SOURCE** — which would force a transcribed copy of
  the constant into `argus/mcp/**`, the exact AI-E9-7 drift the FR34 regime exists to prevent, and
  the exact "guard whose observable is wrong" defect class Epic 11 produced five times (retro §3.1).
  **Correct the assertion to an `ast` closure** — the `unrouted_write_text_calls` pattern from `-31`
  — proving the module **routes** its verdict result through the disclosure helper. **Do not satisfy
  it by pasting the text**, and record the correction with its reasoning rather than fixing it
  quietly.

### AC6: The gates this story falsifies are CORRECTED, never loosened, and none is left stale

- **Given** DF-8-5-B's standing rule — *"do not close it by loosening an assertion"* — and the
  Epic-11 finding that a stale committed guard publishes a false claim (retro §4.4)
- **Then** each of the following is handled, and a decision is recorded for each:
  1. **`tests/test_v1_commitment_closure.py`** — `_ENTRY_POINT = "argus.cli"` and its assertion
     *"It is the ONLY entry point — pyproject.toml ships three console aliases and all three are
     `argus.cli:main`"* become **FALSE** the moment `argus-mcp` lands. Replace the single entry point
     with the **set derived from `pyproject.toml [project.scripts]`** (a closure, per AI-E11-1 clause
     (iii) — never a hand-list), union the reachability closures, and **re-measure** the non-vacuity
     floors (`_MIN_PACKAGE_MODULES`, `_MIN_IMPORT_EDGES`, `_MIN_REACHABLE_MODULES`) against the new
     tree, updating their comments with the measured figures.
  2. **FR35's delivery disposition** in the same file is `_Delivery("FR35", "not-built", "", "", …)`
     with the reason *"`argus/mcp/**` does not exist on this tree"* — now false. Flip it to a
     disposition the closure can **prove**, naming the module and a text anchor inside it, and
     **naming the residual 12.7 half explicitly** so the entry does not over-claim FR35 as fully
     delivered. The disposition vocabulary is CLOSED (`_REVERSE_VOCABULARY`); a hit that fits none of
     its members is a HALT, never a new label invented mid-story.
  3. ⚠️ **Broadening reachability can flip a `library-seam` disposition.** `delivery_refutations`
     refutes `library-seam` over a **reachable** module, and FR23 / FR24 / FR26 / FR29 are disposed
     `library-seam` today. If the MCP adapter imports one of those seams they go red — correctly.
     Constraint 2.3 (*no capability the CLI lacks*) makes not importing them a **design rule**, not
     an accident to be discovered by a red suite.
  4. **`tests/test_invocation_contract.py`** — `_CONSOLE_SCRIPTS = ("argus", "argus-agent",
     "repo-audit")` gains `argus-mcp`.
  5. **`tests/test_built_distribution.py::TC-ArgusAgent-DOCS-001-56`** — README must name the new
     alias and its target. **The `FORTHCOMING` marker STAYS**: `-56` keys the marker's removal on
     `dist.data_assets` being non-empty, and this story ships **no data asset**. Removing the marker
     here would falsely claim Story 12.7's delivery.
  6. **Measured figures that this story moves** — re-derive and correct, do not remember:
     `README.md:154-156` (wheel entry / sdist file counts, pinned by `TC-ArgusAgent-DOCS-001-54`),
     `README.md:163` (the console-script row), `README.md:176` (*"75 of the 75 shipped modules
     import"*), `README.md:222-226` (*"Three console aliases, and nothing else"* + *"77 entries = 72
     `argus/**` modules + 5 `dist-info` files"* — ⚠️ **already rotted**: it disagrees with the pinned
     80/79 figures at `:154` **before** this story touches anything; correct it as part of this work
     and prefer one derived statement to two remembered ones), and `argus/__init__.py`'s docstring
     *"three console scripts that all resolve to `argus.cli.main`"*.
  7. **`CHANGELOG.md`** gains a section registered in `tests/test_release_surface_honesty.py`'s
     `_NOTE_SECTIONS`, whose **order** is pinned by `-16`; the placement is a **reasoned decision**
     in the registry comment, matching the register those comments already use.

### AC7: NFR-M1, determinism, secret-safety and honest degradation

- **Then** every `argus/**` and `tests/**` file stays at or under the **1200-line NFR-M1 ceiling**,
  proven by Story 12.1's repo-wide sweep (`tests/test_module_size_ceiling.py`).
- **Then** the tool result carries **no `float`** (AR4): `deep_ratio` and `assessed_deep_ratio`
  travel as exact `"num/den"` strings, exactly as the CLI's summary line renders them.
- **Then** the result is **secret-safe (NFR-S1)**: it carries the same information class the CLI's
  stdout + stderr carries — verdict token, exact ratios, counts, the ship-readiness lines, the FR34
  disclosure — and **never** raw findings, source bytes, or an absolute host path.
- **Then** **NFR-R1 holds: no crash.** A typed pipeline failure (`RepoIntakeError`,
  `WorkspaceContainmentError`, `CanonicalSerializationError`, `PipelineError`, any `ValueError`)
  becomes a **tool execution error** (`isError: true`) carrying the CLI's own secret-safe message —
  never a traceback, never a protocol-level crash. A malformed request becomes a JSON-RPC protocol
  error. The server survives both and keeps serving. It exits **promptly and cleanly on stdin EOF**
  (the binding's primary graceful-shutdown signal, and the only portable one).
- **Then** the operator-error **diagnosis wording** is left to **Story 12.8** by name
  (`epics.md:2431`): reuse today's message text; do not author new diagnosis prose here.

---

## Developer Context & Guardrails

### §0 — Premise re-measurement (the project's create-story control, five-for-five across Epic 11)

Measured **2026-08-15 on `54b96d7`**, before this story was written. Per the Epic-11 retro §3.2
refinement, divergences **and** confirmations are both recorded.

| Premise, as the epic/tests state it | Re-measured | Consequence for this story |
|---|---|---|
| `mcp\|model.context.protocol` has **zero** hits across `argus/`, `pyproject.toml`, `action.yml` (measured 2026-08-11 by Story 11.1) | ✅ **HOLDS** — still zero | `-49` is genuinely dormant; this story is the first thing that fires it |
| `argus/mcp/**` does not exist | ✅ **HOLDS** — no such directory | Greenfield module; nothing to preserve inside it |
| `_MCP_DISCLOSURE_SURFACES` is empty | ✅ **HOLDS** — `= ()` | See AC5: its registered-surface loop has **never executed** and is wrong as written |
| `pyproject.toml` ships three console aliases, all `argus.cli:main` | ✅ **HOLDS** — `argus`, `argus-agent`, `repo-audit` | A fourth alias is what this story adds, and what four committed guards notice |
| `test_v1_commitment_closure.py` treats `argus.cli` as **the only** entry point | ✅ **HOLDS** — `_ENTRY_POINT = "argus.cli"`, asserted in prose at the file's non-vacuity floor | **This story makes that statement false.** AC6.1 |
| FR35 disposed `not-built`, reason *"`argus/mcp/**` does not exist on this tree"* | ✅ **HOLDS** today | **Falsified by this story.** AC6.2. Note the entry names **no `seam_modules`**, so `not_built_refutations` will **not** fire automatically — nothing mechanical will tell you; AC6.2 is the reason it is written down |
| README states the shipped facts about the distribution | ❌ **DIVERGES — a live rot, found by this re-measurement.** `README.md:154` says the wheel has **80 entries** / sdist **79 files** (pinned by `-54`); `README.md:224` says **77 entries = 72 modules + 5 `dist-info`**. **The two paragraphs in one README contradict each other today**, and only the first is pinned | Correct both under AC6.6. This is the Epic-9/11 published-figure rot class recurring; it is **not** caused by this story and must not be left for the next one |
| NFR-M1 headroom | ✅ Measured: `cli.py` 600, `pipeline.py` 1044, `negative_assurance.py` 579, `test_v1_commitment_closure.py` **1581** ⚠️ | `tests/**` is **not** under the 1200 ceiling in the same way `argus/**` is (`test_v1_commitment_closure.py` is already 1581) — check what `tests/test_module_size_ceiling.py` actually sweeps **before** assuming a test file has no cap, and record the answer |
| Test-case id high-water marks | Measured: `DOCS-001-61`, `CLI-001-51`, `RELEASE-001-24`, `PIPELINE-001-61` | New ids continue from these; see §Testing for the verification-area decision |

### Technical stack, and the one dependency decision that is not negotiable

- **Python 3.10+**, stdlib only for the protocol: `json`, `sys`, `io`, `contextlib`, `dataclasses`,
  `typing`. Pydantic v2 is already a base dependency and may be used for message models if it earns
  its place; `jsonschema` is also already a base dependency.
- 🚫 **The official `mcp` Python SDK is REFUSED, and this is a hard architectural constraint rather
  than a preference.** Verified 2026-08-15 against the SDK's published requirements: `mcp` declares
  **`starlette`, `uvicorn`, `sse-starlette`** (plus `python-multipart`, `pyjwt`, `httpx`/`httpx2`,
  `anyio`, `pydantic-settings`) as **required** dependencies — they are not behind an extra, because
  the SDK carries its HTTP server transports in the base package. Installing it would put `starlette`
  and `uvicorn` in `argus-agent`'s dependency tree and **break the `argus.* ⊬ fastapi/uvicorn/starlette`
  import-isolation gate that this story's own AC2.2 requires to still pass**, as well as ADR #20 and
  AR2 (*stdlib `argparse` only — zero new dependency*). **Hand-roll the JSON-RPC layer.** The wire
  format is one newline-delimited JSON object per line over two streams; the whole transport is
  `json.loads` per line and `json.dumps(...) + "\n"` out. It is small, it is pure, and it is testable
  without a subprocess.
- **No `asyncio`.** Architecture §Architectural Boundaries: the adapter *"must not introduce a
  scheduling or concurrency model of its own (the sequential-canonical execution model at §A is
  unchanged)"*. A synchronous `for line in sys.stdin` loop is both correct and the only compliant
  shape.

### MCP protocol facts you need (verified against the specification, 2026-08-15)

The protocol split into two **eras** on 2026-07-28 and this materially affects the design.

- **Modern** (`2026-07-28` and later): **stateless — there is no `initialize` handshake.** Every
  request carries its protocol version in `_meta["io.modelcontextprotocol/protocolVersion"]`, and the
  server accepts or rejects each request independently. Servers **MUST** implement `server/discover`.
  An unsupported version returns `-32022` `UnsupportedProtocolVersionError` with
  `data: {supported: [...], requested: "..."}`.
  ([versioning](https://modelcontextprotocol.io/specification/2026-07-28/basic/versioning))
- **Legacy** (`2025-11-25` and earlier — this is what the shipped host base speaks today): an
  `initialize` request negotiates a version and capabilities, answered with `protocolVersion`,
  `capabilities` and `serverInfo`, followed by a `notifications/initialized` notification from the
  client.
- **Detection.** A dual-era client probes with `server/discover` first: a `DiscoverResult` or a
  recognized modern error means modern; **any other error (commonly `-32601`) or a timeout means
  legacy**, and the client falls back to `initialize`.
  ([stdio backward compatibility](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio))
- **stdio framing.** Newline-delimited JSON-RPC, UTF-8, **no embedded newlines**; the server **MUST
  NOT** write non-MCP bytes to stdout; the server **MAY** write anything to stderr and clients
  **SHOULD NOT** treat stderr output as an error; the server **SHOULD** exit promptly on stdin EOF;
  the server **MUST NOT** write JSON-RPC *requests* to stdout.
- **Tools.** `tools/list` → `{tools: [{name, title?, description, inputSchema, outputSchema?}], …}`;
  `tools/call` → `{name, arguments}` → a result with `content: [{type: "text", text: …}]`,
  optional `structuredContent`, and `isError`. Modern results additionally carry
  `resultType: "complete"` (additive; legacy clients ignore an unknown field). Servers **SHOULD**
  return tools in a **deterministic order** — which suits this project exactly.
  Tool names: `[A-Za-z0-9_.-]`, 1–128 chars.
  ([tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools))
- **Two error mechanisms, and the distinction matters here.** *Protocol errors* (unknown tool,
  malformed request) are JSON-RPC errors. *Tool execution errors* (the audit failed) are results with
  `isError: true`, because a model can act on those. Map Argus's typed pipeline failures to the
  second — an agent that receives `isError: true` with *"argus: audit failed: …"* has a next action;
  one that receives `-32603` does not (and FR37 forbids an outcome with no next action).

### Wire shapes, concretely (so the surface is not invented twice)

Illustrative, not a schema to transcribe — the tool's `inputSchema` is **derived** from
`build_parser` (AC3) and the version list is the closed constant (AC1).

```jsonc
// ← legacy client
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-11-25",
  "capabilities":{},"clientInfo":{"name":"…","version":"…"}}}
// → server  (serverInfo.version comes from argus.__version__ — the ONE version source)
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-11-25",
  "capabilities":{"tools":{"listChanged":false}},
  "serverInfo":{"name":"argus","version":"0.1.0"}}}

// ← modern client
{"jsonrpc":"2.0","id":1,"method":"server/discover",
  "_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28"}}
// → server: a DiscoverResult naming supportedVersions (the closed constant)

// ← unsupported version, either era
// → {"jsonrpc":"2.0","id":1,"error":{"code":-32022,"message":"Unsupported protocol version",
//     "data":{"supported":[…the constant…],"requested":"1900-01-01"}}}

// ← {"jsonrpc":"2.0","id":2,"method":"tools/call",
//     "params":{"name":"audit_repository","arguments":{"repo":".","strict":true}}}
// → result
{"jsonrpc":"2.0","id":2,"result":{"resultType":"complete","isError":false,
  "content":[{"type":"text","text":"verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 …\n<ship-readiness lines>\n<FR34 instrument disclosure>"}],
  "structuredContent":{"verdict":"RELEASE_READY","exit_code":0,"deep_ratio":"57/149",
    "blocking_findings":0,"assessed_deep_ratio":"…","scope":"…","held_out":76}}}
```

`deep_ratio` values are **strings** (`"57/149"`), never numbers — AR4 forbids `float` on any surface
this project emits, and `Fraction` has no JSON form.

### Make it testable without a subprocess

Give the loop injectable streams — `main(argv=None, *, stdin=None, stdout=None, stderr=None) -> int`,
defaulting to `sys.*`, mirroring `argus/cli.py::main(argv=None)`'s testable-without-`sys.exit` shape
(the console wrapper does `sys.exit(main())`). Then:

- the **pure** dispatcher is driven with plain dicts — no I/O at all;
- the **loop** is driven with `io.StringIO` in-process, which is how the stdout-purity guard (AC4) and
  the parity guard (AC3) run a real audit through the real seam cheaply;
- the **no-listener** guard (AC2.1) still spawns the real process, because that observable exists only
  there.

**Reuse the suite's existing repository builder, do not mint one:** `tests/test_cli.py` stages a real
auditable repo with `stage_cartridge("vacuous_basic", tmp_path / "repo")` (also `"orphan_basic"`,
`"clean_control"`) and drives `cli.main([...])` with `capsys` — that is the exact harness the parity
guard needs on the CLI side, so the MCP side is the only new thing under test.
The audit's `.argus/` writes land in the **audited** repo through the unchanged containment helper —
the MCP surface introduces no new write path and no new filesystem authority (constraint 2.3).

### Files to touch

**NEW**

| Path | Purpose |
|---|---|
| `argus/mcp/__init__.py` | Package marker; the adapter's public surface |
| `argus/mcp/protocol.py` (suggested) | PURE JSON-RPC + MCP message layer: parse a line, dispatch a method name, render a response/error. **Pure** ⇒ testable without a process, and it is where the closed protocol-version constant lives |
| `argus/mcp/server.py` | IMPURE shell: `main()`, the stdin→stdout loop, the stdout guard, the call into `run_audit` |
| `tests/test_mcp_server.py` | The story's guards (see §Testing) |

Split across two modules rather than one is a suggestion, not a mandate — but the **pure/impure
split is a mandate** (AR8): message construction and dispatch are pure folds; only the loop, the
stream handling and the `run_audit` call are impure.

**UPDATE** — read each of these completely before editing; what they currently do, and what must be
preserved, is stated so the change is a modification and not a rewrite.

| Path | What it does today | What must be preserved |
|---|---|---|
| `pyproject.toml` | Three `[project.scripts]`, all `argus.cli:main`; ten grammars in base deps (12.5); `description` carries the FR34 short disclosure | **Add exactly one alias.** Add **no** dependency and **no** extra. Do not touch the `tree-sitter<0.26` bound — Story 12.5 decided it stays, with reasons recorded in the file itself |
| `argus/cli.py` (600 lines) | `build_parser()` is the **source of truth** for the accepted surface, checked against the module docstring by `TC-ArgusAgent-CLI-001-35`/`-37`. `_resolve_passes` / `_build_request` / `_summary_line` are private. `main()` prints stdout + stderr and returns an exit code | Do **not** change the accepted flag surface. If a private helper must be reused, **promote it to a documented public name** rather than copying it or reaching through `_`-prefixed API; a rule implemented twice drifts in one of the two (Story 11.3 / DN-2's stated reason for `executable_line_numbers` being public). Adding a `# MCP` mention to this file makes it a `-49` hit — see AC5 |
| `argus/__init__.py` | Docstring states *"three console scripts that all resolve to `argus.cli.main`"* and `__version__ = "0.1.0"` | `__version__` is the single source for `serverInfo.version`; do not add a second version constant |
| `tests/test_no_web_imports.py` (1018) | `_MODULES_UNDER_GUARD` — an append-only registry, each entry commented with the story that added it and why | Append in that register. Do not fork the gate |
| `tests/test_v1_commitment_closure.py` (1581) | `_ENTRY_POINT`, `_FORWARD_REGISTRY`/`_REVERSE_REGISTRY`, the reachability refutations and their non-vacuity floors | The **closed** disposition vocabularies. A disposition that fits none is a HALT |
| `tests/test_instrument_disclosure.py` (935) | `_MCP_DISCLOSURE_SURFACES`, `mcp_surface_tokens`, `-49` | The two-closure design and the imported `_affirmative_over_claims`. See AC5 for the assertion that must be corrected |
| `tests/test_invocation_contract.py` (965) | `_CONSOLE_SCRIPTS`; documented-invocation extraction | The derived-not-transcribed principle |
| `tests/test_built_distribution.py` (940) | `-56` (README↔`[project.scripts]` closure, FORTHCOMING marker), `-54` (measured wheel/sdist figures) | The FORTHCOMING marker and its 12.7 ownership |
| `README.md` (299) / `CHANGELOG.md` (863) | Consumer-facing surfaces, both in `_RELEASE_SURFACES` and scanned for over-claims by `-17` | The struck-not-deleted amendment form (§3.4) where a shipped sentence becomes false |
| `_bmad-output/design-artifacts/ArgusAgent/architecture.md` | §A entry-point table; the FR35 row in *Post-amendment additions*; the §Instrument-status paragraph's *"The MCP surface does not exist and this story does not build it"* | **§3.4 evidence immutability: strike, never delete.** 12.5's review specifically confirmed both NFR-P3 sites were struck-and-resolved rather than replaced — do the same for every FR35 site this story resolves |

### Locked decisions this story must cite rather than reopen

| Locked | Where | Consequence here |
|---|---|---|
| **DN-8 (Story 10.3)** — `--coverage-scope` CLI default `application` vs `AuditRequest` default `repository`, both shipped and announced, pinned both ways by `TC-ArgusAgent-CLI-001-37b` | `argus/cli.py:115-121` | Reuse the CLI's projection; do **not** "fix" the divergence here. AC3 |
| **DN-9 (Story 10.4)** — verdict-adjacent changes to what the dogfood enumerates are fenced to Epic 11/12 stories that own them | `deferred-work.md` DF-10-4-D | Do not change dogfood composition logic; only regenerate artifacts. Tasks §5 |
| **Story 12.5's CLI fence** — *"`epics.md:2431` gives Story 12.8 the operator-error diagnosis surface explicitly naming 'missing grammar'"* | 12-5 Dev Agent Record; `argus/shared/grammar_status.py:62` | 12.6 does not author diagnosis prose. AC7 |
| **Story 12.2's egress contract** — `--deep-audit` is *"THE ONLY OPT-IN TO EGRESS"*; packaging and environment cannot constitute an operator act; the disclosure fires **before** the first byte and is unconditional within an opted-in run | `argus/cli.py:99-114`, `_emit_egress_disclosure` | The MCP surface reuses that mechanism verbatim; it does not build a second consent channel. DN-4 below |
| **`tree-sitter<0.26` stays** (Story 12.5, 2026-08-15) | `pyproject.toml:34-45` | Do not widen a bound under cover of an unrelated story |
| **DF-8-5-B / DF-10-4-D bootstrap** — commit the `argus/` delta **first**, then regenerate dogfood artifacts, then commit those separately; the regeneration script **refuses by design** otherwise | `scripts/regenerate_dogfood_artifacts.py`; 12-5 Debug Log §5 | This story adds modules, so it **will** trip the artifact-currency guards. Tasks §5 |
| **AI-E11-1** (Epic-11 retro §3.1) — a guard is adequate only if (i) its observable is named, (ii) the defect has been demonstrated to move that observable at the **real seam**, (iii) at least one adversarial variant is **generated** from the grammar/registry it closes over, not hand-listed | Epic-11 retro | Every new guard in this story is written to that standard, and AC4/AC5/AC6 name the observables explicitly |
| **AI-E9-7 / single-source rule** — never publish a prose copy of a pinned constant | architecture §Enforcement | The reason AC5 forbids satisfying `-49` by transcription |

### Decisions taken by this story (record these in the Dev Agent Record; do not re-litigate silently)

- **DN-1 — Hand-rolled stdlib JSON-RPC; the `mcp` SDK is refused.** Measured: the SDK requires
  `starlette`/`uvicorn`/`sse-starlette`. Adopting it breaks the very gate AC2.2 requires to pass, and
  AR2's zero-new-dependency rule. Cost accepted: Argus owns ~a few hundred lines of protocol code and
  must track spec revisions itself. Benefit: constraints 1, 2 and 4 become true *by construction*.
- **DN-2 — Dual-era support: legacy `initialize` **and** modern `server/discover` + per-request
  `_meta` version checking.** Rationale: the `2026-07-28` revision is ~3 weeks old, so shipping
  legacy-only would work with today's hosts and fail modern-only clients ("Modern client + Legacy
  server = **Fails**" in the spec's own compatibility matrix); shipping modern-only would fail every
  host installed today. The cost is small because the dispatcher is stateless either way — Argus
  keeps no session state, so `tools/call` is served identically in both eras. The supported set is
  ONE closed constant (AC1).
- **DN-3 — Exactly ONE tool: `audit_repository`.** No `get_status`, no `explain_verdict`, no
  ledger-reader tool. Constraint 2.3 forbids a capability the CLI lacks, every additional tool is
  another surface needing an FR34 disclosure and a parity proof, and this story's user need is
  satisfied by one. A second tool is a later story's decision, made with a reason.
- **DN-4 — `deep_audit` IS exposed on the MCP surface, with the egress disclosure stated in the tool
  DESCRIPTION as well as on stderr.** Withholding it was considered and rejected: it would make MCP a
  systematically shallower answer than the CLI for identical intent, with the agent unable to tell
  why — a second decision path in effect if not in code. Exposing it is safe because the credential
  still comes only from the existing adapter's environment contract (constraint 2.4), the pass is
  still off by default, and NFR-S6's *"disclosed before the first byte leaves"* is honoured on this
  transport by the tool description, which the model reads **before** it can choose `deep_audit:
  true` — plus the unchanged stderr disclosure at dispatch time.
- **DN-5 — The tool result carries the CLI's information set, not the verdict object.** No
  `verdict.model_dump()`, no `ordered_findings` array. Reuse `_summary_line`'s content and
  `render_ship_readiness(verdict, enabled_passes=…)` exactly as `argus/cli.py` calls them today (note
  its `non_auditable_suffixes` / `degraded_conditions` parameters have **no** production caller —
  `DF-10-4-B` — so calling it the way the CLI does is also what keeps parity true). Rationale:
  NFR-S1 secret-safety is inherited rather than re-argued, and the two surfaces cannot describe one
  run differently.
- **DN-6 — Cancellation is accepted and not acted upon, and that limitation is STATED.** The server
  is single-threaded by architectural mandate (no concurrency model of its own), so a
  `notifications/cancelled` arriving during an audit is read only after the audit completes. The
  notification is consumed and never answered (correct: notifications are never answered); the
  inability to interrupt an in-flight audit is documented on the surface itself rather than left for
  a user to discover. A silent limitation is the thing this project consistently refuses.

### Testing requirements

- **Framework:** `pytest`, offline, deterministic, no network, no sleeps. Every test names its
  `TC-ArgusAgent-<AREA>-001-<n>` id in the docstring alongside the AC it serves — the house style
  across the suite.
- **Verification area — DECIDED: open `ArgusAgent-MCP-001`, ids `-01` onward, homed in
  `tests/test_mcp_server.py`.** Reasoning, recorded because Story 12.5 rejected an invented area
  (`PACKAGING-001`) and this decision must not read as ignoring that: 12.5's objection was that the
  new area **and a new file** were a *second home for a fact that already had one*
  (`test_grammar_runtime_validation.py` already parsed `pyproject.toml` for the same drift class).
  Here there is **no existing home** — no test file covers a JSON-RPC surface — and folding it into
  `CLI-001` would mix a JSON-RPC transport into the area bound to `build_parser`'s argv contract,
  muddying `-35`'s corpus. Area creation is ordinary in this suite (AUDIT, CACHE, CARTRIDGE, COST,
  DETECT, DOCS, DOGFOOD, EVIDENCE, HITL, PIPELINE, REPORT-002, RELEASE, STORE all exist).
  Edits to existing files continue their own areas from the measured high-water marks in §0.
- **Every guard meets AI-E11-1.** For each new test, state the **observable**, demonstrate the defect
  **moving** it (a RED at the real seam, not against a reconstruction), and **generate** at least one
  adversarial variant from the grammar/registry the guard closes over. Concretely, the ones this
  story most needs:
  - the stdout-purity guard must be shown red by a synthetic that prints during an audit (AC4);
  - the parity guard must be shown red by a deliberate default divergence — e.g. an adapter that
    builds `AuditRequest` directly and therefore inherits `coverage_scope="repository"` (AC3);
  - the input-schema closure must be shown red by adding a parser flag with no schema entry (AC3);
  - the no-listener guard must be exercised against the **real server process**, not only its import
    graph (AC2.1).
- **Non-vacuity floors** on anything that passes by finding nothing (E.3 — 10.3's `-39`, 10.4's
  `-118`, 10.5's `-39` all could pass vacuously): a `> 0` floor on messages parsed, tools resolved,
  schema properties derived and modules scanned, so a rename or a module move turns the guard **RED**
  rather than silently green.
- **Full suite + static gates:** `python -m pytest -q`, `python -m mypy argus`, `python -m bandit -r
  argus -q` (re-measure with `argus/` stashed to prove no **new** finding — the raw count alone does
  not show that; 12.5's Debug Log §4 is the pattern).

---

## Tasks & Subtasks

- [x] **Task 1: Re-measure §0 before writing code, and record every divergence (AC6)**
  - [x] Re-run the §0 measurements on the implementation baseline commit and record the figures in
        the Dev Agent Record — including confirmations, not only divergences (Epic-11 retro §3.2.2).
  - [x] Capture the **RED evidence** for every guard this story adds, **before** any `argus/` edit.
  - [x] Confirm what `tests/test_module_size_ceiling.py` actually sweeps (`argus/**` only, or
        `tests/**` too) and record the answer — `test_v1_commitment_closure.py` is already 1581 lines.

- [x] **Task 2: Build the MCP adapter (AC1, AC2, AC4, AC7)**
  - [x] `argus/mcp/protocol.py` — PURE: line → message, method dispatch table, response/error
        rendering, the **closed** supported-version constant with an exhaustive renderer that
        **raises** on an unregistered member.
  - [x] Implement `initialize` + `notifications/initialized`, `server/discover`, `tools/list`,
        `tools/call`, `notifications/cancelled`; `-32601` unknown method, `-32700` parse error,
        `-32602` malformed call, `-32022` unsupported version with `data.supported`.
  - [x] `argus/mcp/server.py` — IMPURE: `main()`, the synchronous stdin→stdout loop, UTF-8 + newline
        framing, clean prompt exit on EOF, **stdout redirected to stderr for the duration of any
        audit**, no `asyncio`, no socket, no thread pool.
  - [x] Wire `pyproject.toml [project.scripts] argus-mcp = "argus.mcp.server:main"`. No new
        dependency, no new extra.

- [x] **Task 3: One tool, parity by construction (AC3, AC5, DN-3/4/5)**
  - [x] `audit_repository` — `inputSchema` **derived from `argus/cli.py::build_parser`**, not
        hand-listed; deterministic tool ordering; description carries the FR34 disclosure and the
        FR36 egress statement.
  - [x] Build the request by **reusing the CLI's own projection** so the CLI defaults govern
        (promote a private helper to a public name if needed — never copy it).
  - [x] Result: `content[0].text` = the CLI's summary line + `render_ship_readiness(...)` lines +
        `render_instrument_disclosure(INSTRUMENT_STATUS)`; `structuredContent` = verdict token,
        `deep_ratio` / `assessed_deep_ratio` as `"num/den"` **strings** (AR4 — no float), counts,
        scope, `held_out`, `exit_code`. No raw findings, no absolute path.
  - [x] Typed pipeline failure → `isError: true` with the CLI's own secret-safe message.

- [x] **Task 4: Correct every gate this story falsifies — none loosened (AC6)**
  - [x] `tests/test_no_web_imports.py::_MODULES_UNDER_GUARD` += every `argus.mcp.*` module, in the
        registry's commented register.
  - [x] `tests/test_v1_commitment_closure.py`: entry points **derived from `[project.scripts]`**;
        reachability unioned; floors re-measured with updated comments; FR35's `_Delivery` flipped to
        a provable disposition from the CLOSED vocabulary, naming the module, an anchor, and the
        residual 12.7 half. Verify **no `library-seam` disposition flips** (FR23/24/26/29).
  - [x] `tests/test_invocation_contract.py::_CONSOLE_SCRIPTS` += `argus-mcp`.
  - [x] `tests/test_instrument_disclosure.py`: populate `_MCP_DISCLOSURE_SURFACES`; **correct `-49`'s
        never-executed registered-surface assertion** from a source-text substring check to an `ast`
        routing closure, with the reasoning recorded (AC5).
  - [x] README + `argus/__init__.py` + CHANGELOG: new alias documented with its target; **FORTHCOMING
        marker left intact**; all measured figures re-derived (including the pre-existing 80-vs-77
        contradiction); superseded sentences **struck, not deleted**.
  - [x] `architecture.md`: strike-and-resolve the FR35 sites — the *"post-amendment additions"* row,
        and §Instrument-status's *"The MCP surface does not exist and this story does not build it"*.
  - [x] `CHANGELOG.md` section registered in `_NOTE_SECTIONS` with a **reasoned** placement comment.

- [x] **Task 5: Verification gates and the dogfood two-step (AC7)**
  - [x] `python -m pytest -q` — full suite green, or every non-green named with its reason.
  - [x] `python -m mypy argus` clean; `python -m bandit -r argus -q` with a stashed-`argus/` control
        run proving **no new** finding.
  - [x] Re-measure every file against the NFR-M1 1200 ceiling and record the counts.
  - [x] ⚠️ **This story adds modules, so the three committed-artifact currency guards WILL go red.**
        Follow the `DF-10-4-D` bootstrap in order: (1) commit the `argus/` delta, (2) run
        `python scripts/regenerate_dogfood_artifacts.py`, (3) commit the regenerated artifacts as a
        **separate** commit. The script **refuses by design** if run before (1). Do not loosen an
        assertion to make them green.

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (Claude Opus 5, 1M context) via the `bmad-dev-story` workflow, 2026-08-15.
Baseline commit `54b96d7` (recorded in the frontmatter).

### Debug Log

**§1 — §0 premises, RE-MEASURED on the implementation baseline `54b96d7` before any edit.**
Confirmations are recorded as well as divergences (Epic-11 retro §3.2.2).

| Premise | Re-measured on `54b96d7` | Consequence |
|---|---|---|
| `mcp\|model.context.protocol` has zero hits across `argus/`, `pyproject.toml`, `action.yml` | ✅ **HOLDS** — zero | `-49` was genuinely dormant |
| `argus/mcp/**` does not exist | ✅ **HOLDS** | Greenfield |
| `_MCP_DISCLOSURE_SURFACES` is empty | ✅ **HOLDS** — `= ()` | Its loop had never executed |
| Three console aliases, all `argus.cli:main` | ✅ **HOLDS** | A fourth is what this story adds |
| `_ENTRY_POINT = "argus.cli"` treated as the only entry point | ✅ **HOLDS** | Falsified by this story — AC6.1 |
| FR35 disposed `not-built`, reason *"`argus/mcp/**` does not exist on this tree"* | ✅ **HOLDS** | Falsified — AC6.2 |
| README's 80/79 vs 77 contradiction | ❌ **DIVERGES, confirmed live.** `README:154` said wheel **80** entries / sdist **79**; `README:224` said **77 = 72 modules + 5 dist-info`. The `:224` arithmetic was internally consistent but used a **stale module count** (72 when the tree carried 75), so one README contradicted itself and only the first was pinned | Corrected under AC6.6, and the second paragraph now states **no** entry count at all — one measurement, one place, one pin |
| Module/edge/reachability figures | ❌ **DIVERGE from the 2026-08-11 comments.** Measured: **75** modules (comment said 72), **376** edges (318), **60** reachable from `argus.cli` (53) | Floors re-derived — see §5 |
| NFR-M1 headroom | `cli.py` 600 · `pipeline.py` 1044 · `negative_assurance.py` 579 · `test_v1_commitment_closure.py` **1581** | See §1.3 |
| Test-case id high-water marks | `DOCS-001-61`, `CLI-001-51`, `RELEASE-001-24`, `PIPELINE-001-61` | New area `MCP-001` opened; existing files continue their own areas |

**§1.3 — what `tests/test_module_size_ceiling.py` actually sweeps (Task 1, asked explicitly).**
**It sweeps BOTH trees.** The population is `git ls-files -z -- '*.py'` — every tracked Python
file — and `-01` asserts that population is *two-sided*, with independent `>= 50` floors on
`argus/**` **and** on `tests/**`, carrying the comment *"Test files are unambiguously in scope"*.
So a test file has exactly the same 1200-line cap as a product module. `test_v1_commitment_closure.py`
is not an exception to the cap; it is a **named, dated, filed exemption** in `_EXEMPT_BY_DESIGN`
(`DF-12-1-B`), and `-04` keeps that registry shrinking by failing if an exemption's file drops
back under the ceiling. Measured population on the baseline: 182 tracked `.py` (75 `argus/**`,
101 `tests/**`); three files over the cap, all three exempted.

**§2 — RED evidence, captured before the implementation existed** (AI-E11-1 clause (ii): a
guard nobody has watched fail is a guard nobody has tested).

1. Committing only `argus/mcp/__init__.py` — a docstring and nothing else — turned
   `TC-ArgusAgent-DOCS-001-49` **RED**: *"an MCP surface appeared and is not a registered
   disclosure surface: ['argus/mcp/__init__.py']"*. The dormant pin fired on the first byte,
   exactly as Story 11.1 designed it.
2. Adding the `argus-mcp` alias to `[project.scripts]` turned `TC-ArgusAgent-DOCS-001-56`
   **RED** (*"console alias 'argus-mcp' is undocumented in README"*) and
   `TC-ArgusAgent-DOCS-001-54` **RED** (*"README.md publishes a stale figure for
   'importable_modules': it says 75, the freshly built artifact measures 76"*).
3. ⚠️ **`tests/test_v1_commitment_closure.py` stayed GREEN through both**, and that is the
   finding of this story's §2 rather than a footnote. Two committed statements became FALSE
   with nothing red: `_ENTRY_POINT`'s prose (*"It is the ONLY entry point — pyproject.toml
   ships three console aliases and all three are argus.cli:main"*) and FR35's `_Delivery`
   reason (*"`argus/mcp/**` does not exist on this tree"*). §0 predicted the second — the
   entry names no `seam_modules`, so `not_built_refutations` structurally could not fire — and
   the first was not predicted by anything. **Nothing mechanical would ever have reported
   either.** Both are corrected in AC6.1/AC6.2 by making the file able to notice: the entry
   point is now a closure over `[project.scripts]`, so the fifth alias is covered on the day
   it is declared.
4. `tests/test_invocation_contract.py` also stayed green, for the same class of reason:
   `_CONSOLE_SCRIPTS` is the *recognizer* for "is this a documented invocation of something we
   ship", so a shipped script missing from it makes that script's documented command lines
   **invisible** to `-28`. Corrected by derivation, and proven non-vacuous — the extractor now
   finds `README.md:261 'argus-mcp'`, and a documented `argus-mcp --port 8080` is refused.

**§3 — the four guards AI-E11-1 says most needed a demonstrated defect, and how each got one.**

| Guard | Observable | Defect demonstrated moving it |
|---|---|---|
| `-08` stdout purity | every stdout line, parsed | a synthetic `print()` + `sys.stdout.write()` injected at the adapter's own `run_audit` call site during a REAL audit; stdout stays parseable and the noise is asserted **present on stderr** (so the guard is shown to REDIRECT, not to swallow) |
| `-07` verdict parity | verdict/ratios/scope/exit code from **both real entry points** | `run_audit(AuditRequest(...))` built directly, as a hand-rolled adapter would: it yields `coverage_scope is None` where the CLI narrows to `scope=application, held_out=1` — DN-8, live |
| `-06` schema closure | symmetric difference schema ↔ parser | a flag added to a REAL parser instance; the derivation picks it up and the unmodified schema is shown to lack it |
| `-05` no listener | `socket.bind`/`listen` inside the REAL process | the SAME sentinel in the SAME harness is shown to fire on a process that really binds |

**§4 — verification.** `python -m pytest -q`: **1490 passed, 2 failed**, and both failures are
the committed-artifact currency guards named in §5 below. `python -m mypy argus`: **clean, 78
source files**. `python -m bandit -r argus -q`: **19 Low / 0 Medium / 0 High** — and the raw
count is not the evidence, so the 12.5 control was repeated: `git archive HEAD argus` was
extracted to a scratch tree and scanned, giving **19 findings, identical set**. A direct scan of
only the files this story writes (`argus/cli.py`, `argus/__init__.py`, `argus/mcp/*.py`) reports
**zero**. **No new finding.**

NFR-M1, re-measured on the delivered tree: `argus/mcp/protocol.py` 836 · `argus/mcp/server.py`
223 · `argus/mcp/__init__.py` 56 · `argus/cli.py` 652 (was 600) · `tests/test_mcp_server.py` 960
· `tests/test_instrument_disclosure.py` 1131 · `tests/test_no_web_imports.py` 1036 ·
`tests/test_invocation_contract.py` 1014 · `tests/test_built_distribution.py` 940. All under
1200. `tests/test_v1_commitment_closure.py` is **1685** (from 1581) and remains the filed
`DF-12-1-B` exemption; its registry entry's measured figure was **updated in place** rather than
left reading 1308, with the growth explained.

**§5 — the dogfood two-step is NOT done, deliberately, and this is the honest statement of it.**
This story adds three `argus/**` modules, which moves the physical-LOC and file-count figures the
committed dogfood artifacts record, so
`test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`
and `test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run` are **RED**
(the proof records the old total against a live **22548**). That is the `DF-8-5-B`/`DF-10-4-D`
bootstrap working as designed: `scripts/regenerate_dogfood_artifacts.py` **refuses by design**
while `argus/` is dirty, so the sequence is (1) commit the `argus/` delta, (2) regenerate, (3)
commit the artifacts separately. **Nothing was loosened, skipped, xfailed or hand-edited to make
them green**, and the remaining two-step is handed to the caller rather than closed by weakening
an assertion.

### Completion Notes

**Delivered.** `argus/mcp/` — a JSON-RPC 2.0 stdio adapter shipping as the fourth console alias
`argus-mcp = argus.mcp.server:main` in the same distribution, with exactly one tool
(`audit_repository`), dual-era protocol support, verdict parity by construction, the FR34
disclosure on both the tool listing and every verdict-bearing result, and a new verification area
`ArgusAgent-MCP-001` (`-01`..`-15`) in `tests/test_mcp_server.py`. Zero new dependencies.

**Decisions taken, beyond the six the story pre-recorded (DN-1..DN-6, all implemented as
written).** Each conflicted with a plausible alternative and each is resolved in favour of an
explicit project standard.

- **DN-7 — five CLI helpers were PROMOTED to public names rather than copied or reached through
  `_`-prefixed API**: `PROG`, `summary_line`, `resolve_passes`, `build_request`,
  `emit_egress_disclosure`, plus `harden_output_streams` (whose signature became
  `(*streams)`, defaulting to the process streams, so the CLI's own call is unchanged). The story
  named the rule (Story 11.3 / DN-2's `executable_line_numbers` precedent); this records which
  names it produced and why each earns its place. `build_request` is the load-bearing one — it is
  where the parser's defaults become the request's values, and it is the single reason parity is
  structural rather than careful. `emit_egress_disclosure` is handed to `run_audit` as **the same
  object the CLI passes**, so DN-4's "reuses that mechanism verbatim; does not build a second
  consent channel" is literally true rather than approximately. Two existing test call sites
  (`test_cli_flag_contract.py`, `test_deep_pass_wiring.py`) were updated mechanically; no
  behaviour, no accepted flag and no rendered string changed.
- **DN-8 — the adapter does NOT name itself in `argus/cli.py`, and that is a correctness choice
  rather than an evasion.** The story flagged that an MCP mention in `cli.py` makes it a `-49`
  hit. Registering `cli.py` in `_MCP_DISCLOSURE_SURFACES` would be satisfiable (it routes through
  `render_instrument_disclosure` already) but it would make the registry assert that `argus/cli.py`
  **is an MCP surface**, which is false. The promotion docstrings therefore cite *Story 12.6* and
  *"a second invocation surface"* — discoverable, accurate, and not a false registry entry.
- **DN-9 — the wire is serialized by `argus.store.canonical.dumps`, NOT by a second
  `json.dumps`.** Found by a guard this story had not anticipated:
  `TC-ArgusAgent-STORE-001-40` went red on `protocol.py`'s hand-rolled encoder. The available
  answers were an allow-list entry (the guard's designed escape) or reuse. Reuse won, and it is
  strictly better than the code it replaced: `sort_keys` + compact separators give byte-identical
  messages across hosts (NFR-P1 on the wire, matching NFR-P1 on disk); **`float` is REFUSED by the
  serializer**, so AR4 becomes structural on this transport instead of merely tested; and the
  single trailing `\n` it already appends IS the stdio framing. Consequences handled: output is
  now `ensure_ascii=False`, so `server.main` reconfigures its streams to UTF-8 — which the stdio
  binding requires anyway and the process streams do not provide on a cp437/cp1252 console; and a
  fractional JSON-RPC `id` is refused with `-32600` rather than echoed, because echoing it would
  hand the serializer a `float` and take the loop down (NFR-R1).
- **DN-10 — `-49`'s never-executed assertion was corrected to a DERIVED `ast` closure, and the
  correction is recorded in three places** (here, in the test's own docstring, and in
  `architecture.md` §Instrument-status, struck-not-deleted). As written it asserted the literal
  disclosure text was a substring of the registered module's **source**, which would have required
  pasting a transcribed copy of the constant into `argus/mcp/**` — the exact AI-E9-7 drift the FR34
  regime exists to prevent, demanded by the guard that exists to prevent it. It now asserts (a) no
  registered Python module contains the constant's text **at all**, (b) every function on a
  registered surface that renders a verdict — **derived** as *calls `summary_line` or
  `render_ship_readiness`*, never declared per file — also calls `render_instrument_disclosure`,
  which is `-31`'s `unrouted_write_text_calls` device at this seam, and (c) a listing surface
  discharges by carrying the text. A `> 0` floor on routed functions stops it returning to the
  state it spent its first four days in. Positive controls over synthetic source cover both
  directions, including a *second* verdict renderer added without the disclosure.
- **DN-11 — the entry-point closure was propagated to two consumers the story did not name**, both
  of which would otherwise have silently narrowed:
  `test_stage_memo_contract.py::CACHE-001-95` (whose 5.3-out-of-scope ruling rests on
  unreachability, and would have measured the wrong graph) and
  `test_instrument_disclosure.py::DOCS-001-45` (whose hand-written entry-point list would have gone
  on checking `argus.cli` while the **new** start-up path an agent host launches sat outside the
  guard — the replay-harness hazard is per-entry-point, not per-package).

**Verified, not assumed.** AC6.3's warning was checked directly rather than trusted: unioning the
reachability closure adds **exactly** `argus.mcp`, `argus.mcp.protocol`, `argus.mcp.server` and
**no** existing seam, so FR23/FR24/FR26/FR29 remain `library-seam` and no disposition flipped. That
is the constraint-2.3 design rule holding, not luck: the adapter imports only `argus.cli`,
`argus.pipeline`, `argus.reports.plain_english`, `argus.store.canonical` and
`argus.verdict.*`.

**Deliberate divergences from the story text, both minor, both recorded rather than silent.**
(1) The story's illustrative wire sketch shows a result whose text is built from `_summary_line`;
the delivered `render_tool_result_text` lives in the PURE `protocol.py` rather than in `server.py`,
because it is a fold over an `AuditVerdict` and AR8 puts folds on the pure side — `server.py` then
touches the disclosure not at all, which is why the `-49` closure is derived from *what a function
does* rather than from a per-file declaration. (2) A `ShipReadinessError` raised by the renderer is
reported as `isError: true` **without** the FR34 disclosure, where `cli.py` prints the disclosure
before returning `1`. The state has no producer (`TC-ArgusAgent-REPORT-002-10` proves it
exhaustively), and collapsing the two failure classes into one `except ValueError` with the CLI's
exact wording was preferred to branching for an unreachable case.

**Scope fences held.** No command asset, no registration mechanism, no wheel data asset (12.7). No
operator-error diagnosis prose — today's message text is reused verbatim (12.8). Nothing published:
no tag, no index upload, no marketplace listing (12.9). No new assurance capability, no verdict
semantics change, no decision-table change, no new detector, no new report. The FORTHCOMING marker
stays, because removing it would claim 12.7's delivery.

### File List

**NEW**

- `argus/mcp/__init__.py`
- `argus/mcp/protocol.py`
- `argus/mcp/server.py`
- `tests/test_mcp_server.py`

**MODIFIED**

- `pyproject.toml` — one new `[project.scripts]` alias; no dependency, no extra
- `argus/cli.py` — six helpers promoted to public names (no behaviour, flag or string change)
- `argus/__init__.py` — docstring: four console scripts across two entry points, struck-not-deleted
- `README.md` — the alias and its target documented; the 80-vs-77 self-contradiction corrected; the
  wheel/sdist and importable-module figures re-derived (83 / 82 / 78)
- `CHANGELOG.md` — new `### Added — argus-mcp …` section; the packaging figures re-derived
- `tests/test_no_web_imports.py` — `_MODULES_UNDER_GUARD` += the three `argus.mcp.*` modules
- `tests/test_v1_commitment_closure.py` — entry points derived from `[project.scripts]`;
  `reachable_from_any`; floors re-measured (58 / 290 / 47); FR35 flipped to `wired` with its
  residual named
- `tests/test_instrument_disclosure.py` — `_MCP_DISCLOSURE_SURFACES` populated; `-49`'s assertion
  corrected to an `ast` routing closure with a non-vacuity floor and positive controls; `-45`'s
  entry-point list derived
- `tests/test_invocation_contract.py` — `_CONSOLE_SCRIPTS` derived from `[project.scripts]`;
  `parse_failure` dispatches on the alias's target
- `tests/test_release_surface_honesty.py` — the new `_NOTE_SECTIONS` entry with its reasoned
  placement
- `tests/test_module_size_ceiling.py` — the `DF-12-1-B` exemption's measured figure re-derived
- `tests/test_stage_memo_contract.py` — uses the derived entry-point set
- `tests/test_cli_flag_contract.py`, `tests/test_deep_pass_wiring.py` — promoted helper names
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — the two FR35 sites struck-and-resolved
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — `12-6 → review`

### Review Findings

**code-review 12-6 iteration 1 (Sonnet 5): review → done. VERDICT: PASS.**

Scope reviewed: `git diff 54b96d7..HEAD` across both commits — `87cdea4` (the implementation:
new `argus/mcp/__init__.py` / `protocol.py` / `server.py`, new `tests/test_mcp_server.py`,
modified `argus/cli.py`, `argus/__init__.py`, `pyproject.toml`, `README.md`, `CHANGELOG.md`,
`architecture.md`, and nine existing test files) and `ddeb30d` (the DF-10-4-D dogfood
artifact-regeneration commit).

Independently re-derived on disk, not transcribed:
- `python -m pytest -q` → **1492 passed, 0 failed, 0 error, 0 skipped** (confirmed via a
  junit-xml run: `tests="1492" errors="0" failures="0" skipped="0"`), exit 0.
- `python -m mypy argus` → `Success: no issues found in 78 source files`.
- `python -m bandit -r argus -q` → **19 Low / 0 Medium / 0 High**, matching the claimed baseline
  exactly.
- `python -m build` on a clean checkout → wheel **83 entries**, sdist **82 files** — matches
  README's re-derived figures exactly. `find argus -name '*.py' | wc -l` → **78**, matching the
  "78 of the 78 shipped modules import" claim.
- The official `mcp` PyPI wheel's `METADATA` was downloaded and inspected directly:
  `Requires-Dist` includes `starlette`, `uvicorn` and `sse-starlette` **unconditioned on any
  extra** — DN-1's stated reason for refusing the SDK is factually correct, not merely
  asserted.
- Re-ran `test_v1_commitment_closure.py`'s own `build_import_graph` / `reachable_from_any`
  functions directly: **78 modules, 392 edges, 63 reachable from the `[project.scripts]`
  union (60 from `argus.cli` alone)** — all comfortably above the new floors (58/290/47, up
  from 55/150/35) and above the old floors too, so no floor was loosened. The union adds
  **exactly** `argus.mcp`, `argus.mcp.protocol`, `argus.mcp.server` and **no** existing
  `library-seam` module — FR23/24/26/29 confirmed still disposed `library-seam` with the live
  graph.
- Grepped `argus/mcp/**` for the FR34 disclosure constant's rendered text and for
  `INSTRUMENT_STATUS` — no transcribed copy exists; every render routes through
  `render_instrument_disclosure(INSTRUMENT_STATUS)` imported from
  `argus/verdict/negative_assurance.py` (AI-E9-7 held).

AC-by-AC, verified against the diff and the story's own decision markers rather than assumed:
- **AC1** — exactly one new `[project.scripts]` alias (`argus-mcp = argus.mcp.server:main`),
  no new dependency; both protocol eras served through one dispatcher; closed
  `ProtocolVersion` enum with an exhaustive `protocol_era()` that raises on an unregistered
  member (the `render_instrument_disclosure`/`exit_code_for_verdict` house pattern); `-32601`
  / `-32700` / `-32602` / `-32022` all independently exercised via `test_mcp_server.py`'s
  driven-loop tests and read as correct.
- **AC2** — `-04`/`-05` cover the symbol table and the real process (a `socket.bind`/`listen`
  sentinel proven capable of firing); `argus.mcp.*` appended to
  `test_no_web_imports.py::_MODULES_UNDER_GUARD` (pure extension, not a fork); the dependency
  arrow points inward only (`-13` scans 75+ core modules for a reach into `argus.mcp`, finds
  none); no credential-shaped property in the derived `inputSchema` (`-09`, with a generated
  adversarial variant per credential stem).
- **AC3** — parity is structural: `build_tool_argv` projects validated arguments back onto a
  real argv and hands it to `cli.build_parser().parse_args`, then `cli.resolve_passes` /
  `cli.build_request` — the CLI's own functions — do the rest, so the DN-8 `coverage_scope`
  divergence (CLI `application` vs `AuditRequest` `repository`) governs correctly. `-07`
  drives **both real entry points** over one fixture repo and additionally demonstrates the
  defect directly: a hand-built `AuditRequest(...)` yields `coverage_scope is None` where the
  real MCP path narrows to `scope=application, held_out=1`. `-06` derives the schema from the
  parser and shows a flag added to a live parser instance is picked up automatically.
- **AC4** — `_tool_call_payload` wraps the entire `run_audit` call (and its own
  `build_parser().parse_args` failure path) in
  `contextlib.redirect_stdout(stderr), contextlib.redirect_stderr(stderr)`. `-08`'s
  non-vacuity half is real: a synthetic `print()` + `sys.stdout.write()` is injected at the
  adapter's own `server.run_audit` call site during a live audit, and the test shows the noise
  lands on stderr while every stdout line stays parseable JSON-RPC.
- **AC5** — the disclosure is in both the `tools/list` description and every verdict-bearing
  result (`-10`); `_MCP_DISCLOSURE_SURFACES` populated; `-49`'s previously-never-executed,
  transcription-demanding assertion corrected to a derived `ast` routing closure
  (`functions_calling` over `_VERDICT_RENDER_CALLS` / `_DISCLOSURE_RENDERER`) with a `> 0`
  non-vacuity floor and both-direction positive controls (an honest renderer that routes, and
  a smuggled second renderer that does not) — read and re-derived independently above.
- **AC6** — every gate this story falsifies is corrected, not loosened, confirmed file by
  file: `test_v1_commitment_closure.py` (entry points derived from `[project.scripts]`, FR35
  flipped `not-built → wired` naming the 12.7 residual, floors raised), `test_no_web_imports.py`
  (pure append), `test_invocation_contract.py` (derived `_CONSOLE_SCRIPTS`, target-aware
  `parse_failure`), `test_instrument_disclosure.py` (see AC5), README/CHANGELOG/`__init__.py`
  (all measured figures re-derived and independently confirmed above; the pre-existing
  80-vs-77 self-contradiction fixed by removing the second remembered number rather than
  patching it), `architecture.md` (both FR35 sites struck-not-deleted per §3.4),
  `CHANGELOG.md` (`_NOTE_SECTIONS` extended with a reasoned placement, order matches the live
  document).
- **AC7** — `deep_ratio`/`assessed_deep_ratio` travel as `"num/den"` strings via
  `argus.store.canonical.dumps`, which **refuses `float` at the serializer** (demonstrated in
  `-15` by asserting `CanonicalSerializationError` on an injected float) — AR4 is structural on
  this transport, not merely tested, and the CLI's own stdout output is unchanged (only
  `_PROG` → `PROG` and `_build_request`/`_resolve_passes`/etc. → public names, confirmed
  byte-identical behaviour by diff). NFR-M1: every new/touched file re-measured under the 1200
  cap; `test_v1_commitment_closure.py`'s `DF-12-1-B` exemption entry updated in place to 1685
  (confirmed via `wc -l`). NFR-R1: a typed pipeline failure becomes `isError: true` with the
  CLI's own secret-safe wording (`-12`), never a traceback, and the server keeps serving the
  next request on the same connection (also `-12`).

No unresolved `decision-needed` or `patch` item. No unresolved High or Medium issue. All seven
ACs independently verified met against the real diff and the real tree. Nothing loosened: every
re-measured floor was checked against a live re-computation and found to sit strictly above both
the old and the new floor. Nothing dismissed as noise — no noise was found.

## Change Log

| Date | Change |
|---|---|
| 2026-08-15 | Story 12.6 created (`bmad-create-story`). Scope: FR35 half one — an MCP stdio server as a fourth console entry point in the same distribution, one `audit_repository` tool, verdict parity by reuse of the CLI's request projection, FR34 disclosure on the surface, and correction of the five committed gates this story falsifies. Premises re-measured on `54b96d7`; one live README figure rot found (80 entries vs 77) and assigned here. Status → `ready-for-dev`. |
| 2026-08-15 | Story 12.6 implemented (`bmad-dev-story`, baseline `54b96d7`). **Delivered:** `argus/mcp/` (pure `protocol.py` + impure `server.py`) behind the new `argus-mcp = argus.mcp.server:main` console alias — JSON-RPC 2.0 over stdio, both protocol eras, one `audit_repository` tool whose `inputSchema` is derived from `build_parser` and whose request is built through the CLI's own projection, so the verdict is the CLI's by construction. Zero new dependencies (the `mcp` SDK refused per DN-1). New verification area `ArgusAgent-MCP-001` (`-01`..`-15`). **Gates corrected, none loosened:** entry points in `test_v1_commitment_closure.py` derived from `[project.scripts]` with the closure unioned and floors re-measured (58/290/47); FR35 flipped `not-built` → `wired` with the residual 12.7 half named; `_MODULES_UNDER_GUARD` extended; `_CONSOLE_SCRIPTS` derived and `parse_failure` dispatched on the alias target; `_MCP_DISCLOSURE_SURFACES` populated and **`-49`'s never-executed assertion corrected** from a source-text substring check (which would have forced a transcribed copy of the FR34 constant — AI-E9-7) to a derived `ast` routing closure; README's pre-existing 80-vs-77 self-contradiction repaired by removing the second remembered figure entirely; all measured figures re-derived (wheel 83 / sdist 82 / 78 of 78 importable). **Decisions recorded:** DN-7 (five CLI helpers promoted, not copied), DN-8 (the adapter does not name itself in `cli.py` — a false registry entry is worse than a coy docstring), DN-9 (the wire routes through the ONE canonical serializer, making AR4 structural on this transport), DN-10 (`-49`'s correction), DN-11 (the entry-point closure propagated to two further consumers). **Verification:** pytest 1490 passed / 2 failed — both the DF-10-4-D dogfood artifact-currency guards, which are red BY DESIGN until the `argus/` delta is committed and the artifacts regenerated, and were not loosened; mypy clean (78 files); bandit 19L/0M/0H with a `git archive HEAD` control proving **no new finding**. Status → `review`. |
