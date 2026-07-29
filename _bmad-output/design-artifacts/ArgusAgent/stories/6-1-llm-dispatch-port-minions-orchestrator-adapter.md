# Story 6.1: LLM dispatch port + Minions orchestrator adapter — [Tier B]

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/APAA/`; the tracker is `_bmad-output/design-artifacts/APAA/sprint-status.yaml`
> (NOT the Minions platform tracker at `_bmad-output/implementation-artifacts/sprint-status.yaml`). All
> CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only, §3.8 12-Factor + secret masking, §3.4
> evidence immutability).
>
> **This is the FIRST story of Epic 6** (Trust Substrate — Self-Audit, Prosecutor & Precision, Tier-B). It
> flips `epic-6` to `in-progress`. It builds on the fully-done Epics 1+2+3+4+5 (1032 passed / 1 skipped /
> 4 subtests at the Epic-5 retro, mypy clean, all files ≤1200 lines, a five-epic clean
> determinism/security-gate streak). **Epic 6 is the explicit cut-order boundary** — the Tier-B validation
> layer that earns externalization. This story lays the FOUNDATIONAL LLM SEAM the rest of Epic 6's deep
> work rides on: the single injectable `LLMDispatchPort` + a thin Minions-orchestrator adapter that
> implements it. It is the determinism-quarantine keystone at the substrate level — **all non-determinism
> is confined to this one port**, so the pure core stays pure and a `FakeDispatch` yields zero-token tests.

## Story

As an **APAA maintainer** who must keep the entire pure determinism core (ledger, verdict, cache-key,
Prosecutor, detector scorers) free of any direct LLM dependency — so that the core is reproducible,
zero-token-testable, and provably non-coupled to the non-deterministic substrate — while still giving the
Tier-B deep-audit path (6.2 AST-grounding, 6.4 Prosecutor sign-off) a REAL way to reach the Minions LLM
fleet,
I want **one narrow, APAA-owned `LLMDispatchPort` Protocol** (`apaa/audit/ports.py`) with a single
`dispatch(req) -> LLMRecording` method, a **thin Minions-orchestrator adapter** (`apaa/audit/minions_llm_adapter.py`)
that implements the port by holding a `minions_core.providers.orchestrator.LLMProviderOrchestrator`
(verified FastAPI-free, reused BY IMPORT — no fork, §3.3) and **captures the model checkpoint from the API
response** (AR5/R3), a `FakeDispatch` test double that returns a deterministic `LLMRecording` with ZERO LLM
tokens, and a deep-audit seam (`apaa/audit/deep_audit.py`) that depends on the **port**, never the
orchestrator (DIP) — **plus** the additive substitution wiring so the 5.1 cache-key placeholders
(`V1_MODEL_CHECKPOINT` / `V1_PROMPT_TEMPLATE_VERSION`) now have a REAL source: a closure built from a live
`LLMRecording` carries the captured checkpoint + the real prompt-template version in the SAME key slots 5.1
already reserved (additive value substitution, no key-SHAPE change — `CACHE_KEY_SCHEMA_VERSION` bumps only
if a real value REPLACES a placeholder in the V1 LLM path),
so that every later Epic-6 story (6.2 deep AST claims, 6.4 Prosecutor, 6.7 HITL) reaches the LLM through ONE
injectable seam, the import-isolation gate proves `apaa.*` never pulls FastAPI even WITH the adapter present,
and a future maintainer who wires a different provider chain or a real prompt template is caught by a key
that faithfully moves — rather than by a stale cache hit served under a different checkpoint.

## Story Context

This is **Story 1 of Epic 6** (Trust Substrate — Self-Audit, Prosecutor & Precision, Tier-B — the "proven,
not asserted, depth" moat that clears the ≥80%-precision externalization gate, PRD §Self-Audit & Trust). It
is the FIRST Epic-6 story (so it flips `epic-6` to `in-progress`). It builds on the fully-done Epics 1+2+3+4+5
(the Epic-5 retro recorded 1032 passed / 1 skipped / 4 subtests, mypy clean, all files ≤1200 lines, zero
hard review FAILs in Epic 5, a converged defer-inflow). It is the **LLM-dispatch port + Minions adapter**
story (FR7/FR12/FR19 enabler / AR7 / NFR-D2 injectability, `[Tier B]`).

**What this story delivers and what it explicitly does NOT.** This story delivers (1) the `LLMDispatchPort`
Protocol + the frozen `LLMRecording` DTO it returns, (2) the thin `MinionsLLMAdapter` that implements the
port over the reused `LLMProviderOrchestrator` and captures the model checkpoint from the API response, (3)
a `FakeDispatch` zero-token test double, (4) the `deep_audit.py` seam that depends on the PORT (DIP — never
the orchestrator directly), and (5) the ADDITIVE substitution wiring so the 5.1 cache-key placeholders have
a real source (a closure built from a live recording carries the captured checkpoint + prompt-template
version in the SAME slots). It does **not** build the full Python AST-grounding of deep claims (Story 6.2,
which CLOSES DF-1-7-B), the orphan/dead-code detector (Story 6.3), the adversarial Prosecutor + cut-edge
pass (Story 6.4), the defect-cartridge self-audit harness + holdout + clean controls (Story 6.5), the
precision replay harness + validation protocol (Story 6.6), or the HITL STOP/PROCEED escalation +
append-only decision record (Story 6.7). The port is the SEAM; using it to validate deep claims / prosecute
verdicts / escalate is the next six stories. Keeping 6.1 to the port-and-adapter scope is the thin-slice
discipline that held across Epics 1-5 (each story folds ONE working capability over the determinism spine).

**The determinism spine + cache-key closure this port feeds are DONE and proven.** The single canonical
serializer (`apaa/store/canonical.py::dumps_bytes`), the content-hashed envelope
(`apaa/store/envelope.py::compute_content_hash`), the fixed-enum ledger + frozen recording schema
(`apaa/ledger/`), the pure-function verdict gate (`apaa/verdict/verdict_gate.py`), and the full
recording-producing-closure cache key (`apaa/cache/key.py::RecordingProducingClosure` + `derive_cache_key`)
all shipped in Epics 1-5 and were proven byte-identical across environments. **The cache key already
RESERVES the two LLM-path slots this story makes real:** `model_checkpoint` (default
`V1_MODEL_CHECKPOINT = "v1-heuristic-no-llm"`) and `prompt_template_version` (default
`V1_PROMPT_TEMPLATE_VERSION = "v1-no-prompt-template"`), both shaped (DN-PLACEHOLDER / DF-5-1-A, closed in
5.1) for a clean ADDITIVE substitution of a real captured value into the SAME slot — `CACHE_KEY_SCHEMA_VERSION`
is `"2"` and the model is `frozen, extra="forbid"`. **6.1 changes slot VALUES via a real source, not the key
SHAPE** (the DF-5-1-A closure note: "Epic-6 Story 6.1 substitutes the real captured value into the existing
slot (no key-shape change)").

**The LLM is behind ONE injectable port — the determinism-quarantine keystone (architecture Decision E / CC
#7 / §496).** The architecture mandates: "the `LLMDispatchPort` is the only seam between the pure core and
the non-deterministic LLM substrate" (§324), "everything downstream is pure folds over recordings" (§497).
Concretely:
- `apaa/audit/ports.py` → `LLMDispatchPort(Protocol)` with a single `dispatch(req: LLMDispatchInput) ->
  LLMRecording`. PURE-IMPORTABLE: importing the port pulls NO provider code, NO FastAPI (it is a structural
  `typing.Protocol` + the frozen `LLMRecording`/`LLMDispatchInput` DTOs only).
- `apaa/audit/minions_llm_adapter.py` → the IMPURE adapter holding an `LLMProviderOrchestrator`
  (`minions_core.providers.orchestrator`, verified FastAPI-free), mapping APAA's request DTO →
  `RuntimeDispatchRequest`/`LLMRequest` and `LLMResponse`/`RuntimeDispatchResult` → APAA's frozen
  `LLMRecording`, **capturing the model checkpoint from the API response** (`LLMResponse.model` is the
  dispatch-actual model id — the captured checkpoint, NOT a config string).
- `apaa/audit/deep_audit.py` → depends on `LLMDispatchPort`, **never the orchestrator directly** (DIP). In
  V1 it is a thin seam (the full AST-grounding logic is 6.2); tests inject a `FakeDispatch` → 0 LLM tokens.
- **No fork (§3.3):** the adapter inherits the orchestrator's fallback chain + circuit breaker + cost
  attribution, which feeds APAA cost governance (3.1 `budget_governor`) + honest degradation (NFR-R1) for
  free. The adapter NEVER reimplements routing/retry/breaker logic.

**The closure inputs this story makes real (architecture §76-82, §247-250; 5.1 slots).** Two of the cache
key's enumerated closure inputs were V1 placeholders pending the live LLM:

| Closure input | 5.1 V1 placeholder | 6.1 real source |
|---|---|---|
| **model checkpoint** (captured from the API response) | `V1_MODEL_CHECKPOINT = "v1-heuristic-no-llm"` | `LLMRecording.model_checkpoint` ← `LLMResponse.model` (the dispatch-actual model id captured from the adapter's API response). A closure built from a live recording folds this captured value into the EXISTING `RecordingProducingClosure.model_checkpoint` slot. |
| **prompt-template version** | `V1_PROMPT_TEMPLATE_VERSION = "v1-no-prompt-template"` | `LLMRecording.prompt_template_version` ← the version of the deep-audit prompt template the adapter dispatched (a stable, declared version string the adapter/deep-audit owns). Folded into the EXISTING `RecordingProducingClosure.prompt_template_version` slot. |

**SCOPE NOTE on the substitution (DN-SUBST below).** This story DEFINES the real source (the
`LLMRecording` fields + the adapter capture) and proves the closure-from-recording path folds them into the
existing slots additively. Whether `CACHE_KEY_SCHEMA_VERSION` BUMPS depends on whether the V1 default-path
key VALUE changes for a no-LLM run — it MUST NOT (a Tier-A heuristic run still uses the placeholder
defaults, byte-identically); a bump is required ONLY if the live-LLM path's key value would otherwise
collide with a placeholder-path key (it cannot — distinct checkpoint values derive distinct keys, the 5.1
drift seam). The pipeline call site that drives a LIVE LLM run end-to-end is fenced to 6.2 (deep-audit
logic); 6.1 provides the seam + the closure-builder helper + its tests.

**The `checkpoint_drift` detection (AR5 / 5.1 seam → live capture here).** 5.1 defined the
`checkpoint_drift` DETECTION SEAM as a placeholder-comparison (two checkpoint values → two keys). 6.1 wires
the LIVE capture: the adapter captures the model checkpoint from EACH API response, so a mid-run checkpoint
that DIFFERS from the run's pinned checkpoint is observable. **SCOPE FENCE:** 6.1 captures the checkpoint
and EXPOSES it on the `LLMRecording`; the FULL mid-run drift comparison + the `checkpoint_drift` finding's
pipeline wiring + the abort/re-audit loop is a deep-audit-pipeline concern shared with 6.2 — 6.1 defines the
captured-checkpoint surface + a typed `CheckpointDriftError`/finding-shape seam and demonstrates that two
captured values derive two keys; it does NOT build the live abort/re-audit loop. Document the deferral.

**Carry-forward from the Epic-5 retro (2026-06-29) + the standing disciplines (CLAUDE.md §9.1 / L1-E11).**
Each item below is an Epic-6-backlog action item this story discharges or carries (per the L1-E11 operating
model: package the prior retro's action items as the next epic's backlog).
- **AI-E5-1 (test-infra 🟠) — the COMPLETE-THE-DECLARED-SET keystone checklist, now at THREE levels
  (fixture coverage-classes, no-crash input-shapes, closure/enumeration completeness).** Applied to 6.1:
  the adapter's LLM no-crash matrix is a DECLARED set — **provider-chain exhaustion, transport timeout,
  malformed/empty response, a captured checkpoint that drifts mid-run, a budget halt** — and EACH member
  must degrade to a typed APAA outcome (a typed finding or a typed `LLMDispatchError`), NEVER an uncaught
  raise out of the seam (the orchestrator raises `RuntimeError("all-providers-unavailable")` on exhaustion;
  the adapter MUST catch+map it). Each leg demonstrated RED-first. This is the retro's explicit headline:
  "6.1 in particular adds the first live LLM seam; the no-crash matrix (provider failure, timeout, malformed
  response, checkpoint drift) must each degrade to a typed finding, never raise."
- **AI-E5-7 (process 🟢) — keep the structural gates green + the L1-E11 loop + partial-reuse docstring
  precision.** The new `audit/` modules must keep the web-stack import-isolation gate
  (`tests/apaa/test_no_web_imports.py::_FORBIDDEN` = fastapi/uvicorn/starlette) green EVEN WITH the adapter
  importing `providers.orchestrator` (providers are verified FastAPI-free — the gate distinguishes the PURE
  core from the impure adapter seam: the adapter may import providers but must NOT pull FastAPI; the port +
  deep_audit + the pure core must NOT import providers AT ALL — `_LLM_FORBIDDEN_PREFIXES`). Extend (NOT
  fork) `_MODULES_UNDER_GUARD` with the new `audit/` modules (web-gate) and EXTEND `test_pipeline_is_zero_token`
  / `_assert_no_llm_import` coverage so the PURE seam (`audit/ports.py`, `audit/deep_audit.py`) is proven to
  NOT pull `providers` while the adapter is explicitly EXEMPT from the no-LLM gate (it is the one allowed
  importer). When a reuse is PARTIAL, narrate it precisely ("holds an `LLMProviderOrchestrator`, maps DTOs;
  does NOT reimplement routing/breaker"), not "reuses the orchestrator wholesale."
- **AI-E5-3 (process 🟠) — the committed pre-`review` test-existence guard is now FOUR epics slipping; Epic 6
  is CI-touching.** NOT this story's primary deliverable (6.5/6.6 harnesses + 6.1 import-isolation are the
  CI-touching moments), but 6.1 MUST honor the in-session test-existence discipline (the mandatory artifacts
  EXIST + pass before the `review` flip). Flag forward: the committed `*→review` guard is best landed in a
  CI-touching Epic-6 story (the orchestrator's call; AI-E5-3 owner = Delivery Orchestrator).
- **AI-E5-5 (process 🟠) — DF-1-7-B (interim Python deep over-grading) is owned by Story 6.2, ONE STORY
  AWAY.** NOT this story's work, but 6.1 is the seam 6.2 rides. Do NOT confuse 6.1's port/adapter (the LLM
  reach) with 6.2's AST-grounding deliverable (the deep-claim validator). Keep the port shaped so 6.2's
  validator depends on it cleanly (a `dispatch(req) -> LLMRecording` the validator consumes).
- **AI-E1-1 (test-infra 🟢) — non-ASCII / locale discipline (the Epic-1-FAIL class, standing).** An
  `LLMRecording` carrying a non-ASCII file path / content / model id must round-trip + derive a stable
  closure key (explicit UTF-8; the single serializer is `ensure_ascii=False`). Run the suite under
  `PYTHONIOENCODING=utf-8` (project memory — the cp1252 emoji crash). At least one fixture carries a
  non-ASCII value.
- **AI-E5-4 (governance 🟢) — central defer register.** If this story files a NEW defer, file it append-only
  in `_bmad-output/design-artifacts/APAA/deferred-work.md` (the single canonical APAA defer source), not
  only in the story file, with the six CC-3 fields. (DF-5-1-A, which targeted THIS story, was already closed
  in 5.1 — confirm it stays closed; 6.1 does not reopen it.)
- **NFR-S1 secret-containment (standing CI-blocking moat).** The adapter reaches the LLM — prompt/response
  bytes MUST NEVER land in an `LLMRecording`, a ledger, evidence, logs, or traces. The `LLMRecording`
  carries METADATA (model checkpoint, prompt-template version, token counts, finish_reason, credits) +
  declared structured output the deep-audit consumes — NEVER raw prompt/response source bytes or secret
  values (producer-side redaction, architecture CC #5). The 4.4 randomized-canary suite (extended in 5.2 to
  `.apaa/cache/` and 5.3 to `.apaa/decisions/`) remains the durable backstop; if 6.1 introduces any new
  `.apaa/` write path it MUST be swept (note: 6.1 is library-only — it writes NO `.apaa/` byte; the live
  pipeline write is 6.2).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 6.1) + the architecture / PRD. Drivers: **APAA-AR7**
> (reuse-by-import, leaf modules only; the LLM is reached ONLY via the APAA-owned `audit/ports.py::LLMDispatchPort`;
> never import `minions_core.api.* / services.api_app / app_factory / api_server`), **APAA-NFR-D2** (the deep
> path is zero-token-testable — `FakeDispatch` yields 0 LLM tokens; the pure core never touches the LLM),
> **APAA-NFR-P2** (stack-agnostic claim interface; the port is the seam the `claim→validated?` interface
> rides), **APAA-AR5** (model checkpoint captured from the API response — the cache-key closure input made
> real; the placeholder slots 5.1 reserved are substituted additively), **APAA-AR9** (committed/durable
> import-isolation gate: `apaa.* ⊬ fastapi/uvicorn/starlette`, EVEN WITH the adapter), **APAA-AR8**
> (pure/impure separation: `ports.py` + `deep_audit.py` PURE-of-providers; `minions_llm_adapter.py` the
> impure shell), **APAA-AR10** (a provider failure / timeout / malformed response / checkpoint drift / budget
> halt → a typed finding or typed error, NEVER an uncaught raise out of the seam), **APAA-NFR-S1** (no
> prompt/response/secret bytes in the `LLMRecording` / ledger / evidence / logs / traces), **APAA-NFR-M1**
> (≤1200-line files), **APAA-FR-7/FR-12/FR-19 enabler** (the deep-audit / orphan / Prosecutor passes ride
> this seam; their LOGIC is 6.2/6.3/6.4).
>
> **SCOPE FENCE — Tier-B, single-purpose, FIRST Epic-6 story.** This story delivers ONLY: (1) the
> `LLMDispatchPort(Protocol)` + the frozen `LLMRecording` + `LLMDispatchInput` DTOs (`apaa/audit/ports.py`);
> (2) the thin `MinionsLLMAdapter` implementing the port over a reused `LLMProviderOrchestrator`, capturing
> the model checkpoint from the API response (`apaa/audit/minions_llm_adapter.py`); (3) a `FakeDispatch`
> zero-token test double; (4) the `deep_audit.py` seam depending on the PORT (DIP), thin in V1; (5) the
> ADDITIVE substitution wiring — a closure-builder helper that folds a live `LLMRecording`'s captured
> checkpoint + prompt-template version into the EXISTING 5.1 cache-key slots (no key-SHAPE change); (6) the
> import-isolation gate extension proving `apaa.* ⊬ FastAPI` WITH the adapter, and the no-LLM gate extension
> proving the PURE seam (`ports`/`deep_audit`) ⊬ `providers`. It does NOT build, and MUST NOT pull forward:
> the **full Python AST-grounding of deep claims** (Story 6.2, which CLOSES DF-1-7-B); the **orphan/dead-code
> detector** (Story 6.3); the **adversarial Prosecutor + cut-edge pass** (Story 6.4); the **cartridge
> self-audit harness + holdout + clean controls** (Story 6.5); the **precision replay harness + validation
> protocol** (Story 6.6); the **HITL STOP/PROCEED escalation + decision record** (Story 6.7); the **live
> mid-run checkpoint-drift comparison + `checkpoint_drift` finding pipeline wiring + abort/re-audit loop**
> (the captured-checkpoint SURFACE + drift-seam is defined; the live loop is 6.2-shared); a **live
> end-to-end LLM pipeline call site** (`pipeline.py` stays byte-identical — DN-WIRING; 6.2 wires the live
> deep path); any **`.apaa/` write** (6.1 is library-only; it writes NO `.apaa/` byte); a **new
> `.github/workflows` CI job** (the gates are normal `tests/apaa/` tests); a **new HTTP route / FastAPI
> surface / UI** (§3.7); a **`cli.py` subcommand / `--llm` flag**. Build the port + adapter + FakeDispatch +
> the deep_audit seam + the substitution helper + the gate extensions, prove the no-crash matrix
> RED-then-green and the import-isolation gates green, then stop.

**AC1 — One narrow, PURE-importable `LLMDispatchPort` Protocol is the single LLM seam (AR7 / §324 / §496 — the determinism-quarantine keystone)**
**Given** `apaa/audit/ports.py` defining `LLMDispatchPort(Protocol)` with a single method
`dispatch(req: LLMDispatchInput) -> LLMRecording`, plus the frozen (`frozen=True, extra="forbid"`, no float)
`LLMRecording` DTO it returns and the frozen `LLMDispatchInput` DTO it takes
**When** `apaa/audit/deep_audit.py` (or any later Epic-6 deep pass) needs an LLM
**Then** it depends on the **port type** (`LLMDispatchPort`), NEVER the orchestrator directly (DIP) — the
dependency is injected (constructor/parameter), so the deep path is provider-agnostic
**And** importing `apaa/audit/ports.py` and `apaa/audit/deep_audit.py` pulls NO provider code and NO FastAPI
(the port is a structural `typing.Protocol` + frozen DTOs only; `deep_audit` imports the port, not the
adapter) — proven by the extended no-LLM gate (`apaa.audit.ports` / `apaa.audit.deep_audit` ⊬
`minions_core.providers`).

**AC2 — A `FakeDispatch` test double yields a deterministic `LLMRecording` with ZERO LLM tokens (NFR-D2 — the zero-token property)**
**Given** a `FakeDispatch` implementing `LLMDispatchPort` (in the test tree or a clearly-marked testing
helper, NOT the production adapter)
**When** `deep_audit.py` (or a test) dispatches through it
**Then** it returns a deterministic, fully-specified `LLMRecording` (a fixed captured `model_checkpoint`, a
fixed `prompt_template_version`, fixed token counts, declared structured output) consuming ZERO LLM tokens
and making NO network call (NFR-D2: the deep path is zero-token-testable)
**And** a closure built from the `FakeDispatch` recording derives a deterministic, stable cache key (the
fake feeds the real closure-builder, proving the substitution path is exercised token-free).

**AC3 — The Minions adapter implements the port over a REUSED `LLMProviderOrchestrator`, capturing the model checkpoint from the API response (AR5 / §3.3 no-fork / §272-278)**
**Given** `apaa/audit/minions_llm_adapter.py::MinionsLLMAdapter` holding an
`LLMProviderOrchestrator` (`minions_core.providers.orchestrator`, verified FastAPI-free)
**When** `dispatch(req)` is called
**Then** the adapter maps APAA's `LLMDispatchInput` → the orchestrator's request type
(`RuntimeDispatchRequest`/`LLMRequest`), invokes `execute_llm(...)`, maps the result
(`RuntimeDispatchResult`/`LLMResponse`) → APAA's frozen `LLMRecording`, and **captures the model checkpoint
from the API response** (`LLMResponse.model` — the dispatch-actual model id, NOT a config string — into
`LLMRecording.model_checkpoint`)
**And** the adapter REUSES the orchestrator BY IMPORT and does NOT fork/reimplement its fallback chain,
circuit breaker, or cost attribution (§3.3) — it inherits them, so the adapter is thin (DTO-mapping +
checkpoint capture only); the adapter NEVER imports `minions_core.api.* / services.api_app / app_factory /
api_server` (AR7 leaf-module rule)
**And** prompt/response/secret BYTES never enter the `LLMRecording` — it carries metadata + declared
structured output only (NFR-S1 producer-side redaction; cite locations/counts, never bytes).

**AC4 — The 5.1 cache-key placeholders now have a REAL source — additive substitution, no key-SHAPE change (AR5 / DF-5-1-A closure / DN-SUBST)**
**Given** the 5.1 cache-key closure reserving `model_checkpoint` (default `V1_MODEL_CHECKPOINT`) and
`prompt_template_version` (default `V1_PROMPT_TEMPLATE_VERSION`) slots, both shaped for a clean ADDITIVE
substitution (frozen, `extra="forbid"`, `CACHE_KEY_SCHEMA_VERSION = "2"`)
**When** a `RecordingProducingClosure` is built from a LIVE `LLMRecording` (via the new closure-builder
helper)
**Then** it folds the recording's captured `model_checkpoint` + `prompt_template_version` into the EXISTING
slots (the SAME slots 5.1 defined — additive VALUE substitution, NOT a key-SHAPE/schema change), and a
distinct captured checkpoint/prompt-template version derives a DISTINCT key (the 5.1 drift seam, now fed by
a real source — a mixed-checkpoint result can never be served as a hit)
**And** a Tier-A no-LLM (heuristic/claim-proxy) run still uses the placeholder defaults and derives a
BYTE-IDENTICAL key to before this story (no regression — the placeholder-path golden key is unchanged); a
`CACHE_KEY_SCHEMA_VERSION` bump is required ONLY if a real value would otherwise collide a placeholder-path
key (it cannot — the drift seam guarantees distinct values → distinct keys), and any deliberate bump
regenerates + documents the golden (the 5.1 intentional-invalidation lever).

**AC5 — The full LLM no-crash matrix degrades to a typed outcome, NEVER an uncaught raise (AR10 / AI-E5-1 / NFR-R1 — the headline Epic-6 risk surface)**
**Given** the adapter reaching the live orchestrator
**When** any failure mode in the DECLARED no-crash set occurs — **provider-chain exhaustion** (the
orchestrator raises `RuntimeError("all-providers-unavailable")`), a **transport timeout**, a
**malformed/empty response**, a **captured checkpoint that drifts** from the run's pinned checkpoint, or a
**budget halt** (the orchestrator's `budget_exceeded` path)
**Then** EACH member degrades to a typed APAA outcome — a typed `LLMDispatchError` (a `ValueError`/dedicated
exception subclass) OR a typed degradation `LLMRecording`/finding-shape the deep path can record — NEVER an
uncaught `RuntimeError`/`Exception` propagating out of `dispatch(...)` (AR10 / NFR-R1: failure → typed
finding/coverage downgrade, never a crash)
**And** EACH member is demonstrated RED-first (the no-crash test fixtured against an adapter that lets the
raise escape, then made green) — the AI-E5-1 complete-the-declared-set keystone-adequacy proof: the matrix
enumerates the full failure set and covers each member; no bare `except: pass`; a NAMED typed catch set.

**AC6 — Import-isolation holds WITH the adapter; the PURE seam is provider-free; ≤1200 lines; non-ASCII; mypy (AR9 / AR8 / NFR-M1 / AI-E1-1)**
**Given** the new `audit/` modules (`ports.py`, `minions_llm_adapter.py`, `deep_audit.py`) + their test
fixtures
**When** the suite runs under `PYTHONIOENCODING=utf-8`
**Then** the web-stack import-isolation gate stays green EVEN WITH the adapter: importing ANY new `audit/`
module (including `minions_llm_adapter.py`) does NOT transitively pull `fastapi`/`uvicorn`/`starlette` (the
providers leaf modules are verified FastAPI-free — extend, do NOT fork, `_MODULES_UNDER_GUARD`); the no-LLM
gate proves the PURE seam (`apaa.audit.ports`, `apaa.audit.deep_audit`, AND the unchanged `models`/`pipeline`/`cli`)
⊬ `minions_core.providers`, while the adapter (`apaa.audit.minions_llm_adapter`) is the ONE explicitly-allowed
provider importer (carve it out of the no-LLM gate, documented)
**And** an `LLMRecording` carrying a non-ASCII file path / content / model id round-trips + derives a stable
closure key (explicit UTF-8, `ensure_ascii=False` single serializer — the Epic-1-FAIL encoding class); each
new `audit/` file + its test file is ≤1200 lines (NFR-M1); `mypy` is clean on the new modules; the
`LLMRecording`/`LLMDispatchInput` DTOs are PURE (no I/O, no clock, no uuid/random/float at the model layer
— AR8).

**AC7 — No regression / no scope creep; the structural gates stay green; mypy clean (AR8, AI-E5-7, the thin-slice discipline)**
**Given** the new port + adapter + FakeDispatch + deep_audit seam + substitution helper + their tests
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the 1032-green Epic-5 baseline + the new `tests/apaa/test_llm_dispatch_port.py` /
`test_minions_llm_adapter.py` and any sibling), the import-isolation gates (web-stack + no-LLM, both
extended-not-forked), the single-serializer AST gate (`test_canonical_single_serializer.py` — the
substitution helper REUSES `derive_cache_key`/`dumps_bytes`, adds NO second `json.dumps`/hasher), and the
file-size gate (≤1200 lines) stay green; `mypy` is clean on `audit/*` + any sibling
**And** the frozen Epic-1..5 contracts show NO working-tree diff (`store/{canonical,envelope}.py`,
`cache/key.py` — the substitution helper COMPOSES `RecordingProducingClosure`/`derive_cache_key` read-only;
it does NOT edit the model; if a `CACHE_KEY_SCHEMA_VERSION` bump is genuinely required (it is NOT for the V1
no-LLM path — AC4), it is the ONLY permitted `cache/key.py` edit and is documented), `ledger/recording.py`,
`models.py`, `verdict/*`, `detectors/*`, `pipeline.py` (byte-identical — DN-WIRING). `_MODULES_UNDER_GUARD`
is EXTENDED (not forked) with the new `audit/` modules. NO `.apaa/` byte written, NO `cli.py` subcommand, NO
HTTP route, NO new CI job
**And** the new test files cite their `APAA-AR7`/`APAA-NFR-D2`/`APAA-AR5` drivers in the module docstring +
the locked test area / index; the mandatory artifacts EXIST + pass + the no-crash-matrix RED-then-green is
documented BEFORE the story flips to `status: review` (AI-E5-3 / AI-E2-1 test-existence discipline). **Test
area `APAA-AUDIT`** (`TC-APAA-AUDIT-001-NN` — the natural area for `audit/`; confirm/lock the next free index
in the module docstring).

## Tasks / Subtasks

- [x] **Task 0 — Re-read the REAL surfaces; LOCK the port shape, the DTO mapping, and the substitution path** (AC: 1, 3, 4)
  - [x] Re-read `minions_core/providers/orchestrator.py::LLMProviderOrchestrator` (`__init__` args:
        `primary_provider_id`, `fallback_chain`, …; `execute_llm(request: RuntimeDispatchRequest,
        required_capabilities=None) -> RuntimeDispatchResult`; the `RuntimeError("all-providers-unavailable")`
        exhaustion raise; the `budget_exceeded`/`_maybe_halt_on_budget` path). LOCK: the adapter HOLDS the
        orchestrator and CALLS `execute_llm`; it does NOT reimplement routing/breaker (§3.3).
  - [x] Re-read `minions_core/providers/base.py` (`LLMRequest` = `model/max_tokens/temperature/tier`;
        `LLMResponse` = `content/model/provider_id/credits_used/finish_reason/…`; `RuntimeDispatchRequest`
        @201 / `RuntimeDispatchResult` @217; `WorkerTier`; `provider_max_tokens`). LOCK: `LLMResponse.model`
        is the CAPTURED checkpoint (dispatch-actual model id) → `LLMRecording.model_checkpoint`. Confirm the
        providers package is FastAPI-free (it is — verified across Epics 1-5).
  - [x] Re-read `minions_core/apaa/cache/key.py` (`RecordingProducingClosure` with the `model_checkpoint` /
        `prompt_template_version` slots + their `V1_MODEL_CHECKPOINT` / `V1_PROMPT_TEMPLATE_VERSION` defaults,
        `CACHE_KEY_SCHEMA_VERSION = "2"`, `derive_cache_key`, `detector_set_content_hash`). LOCK DN-SUBST: the
        substitution is ADDITIVE — fold the captured checkpoint + prompt-template version into the EXISTING
        slots via a closure-builder; do NOT change the key SHAPE; the V1 no-LLM golden key is UNCHANGED.
  - [x] Re-read `minions_core/apaa/ledger/recording.py` (the frozen `Recording` row + the anticipated
        `LLMRecording` DTO note @31). LOCK: `LLMRecording` is the frozen DTO the PORT returns (metadata +
        declared output, NO source/secret bytes — NFR-S1); the ledger `Recording` row stays frozen
        (additive-only if it must reference the LLM recording — but 6.1 need not touch it).
  - [x] Re-read `tests/apaa/test_no_web_imports.py` (`_FORBIDDEN` web set, `_MODULES_UNDER_GUARD`,
        `_LLM_FORBIDDEN_PREFIXES = ("minions_core.providers", "minions_core.apaa.audit")`,
        `_assert_no_llm_import`, `test_pipeline_is_zero_token`). LOCK the gate strategy: the adapter is the
        ONE allowed providers importer (carve it out of the no-LLM gate); the PURE seam (`ports`/`deep_audit`)
        + the unchanged `models`/`pipeline`/`cli` stay no-LLM; ALL `audit/` modules stay web-stack-clean.
- [x] **Task 1 — Build the PORT + DTOs `apaa/audit/ports.py`** (AC: 1, 3, 6)
  - [x] `LLMDispatchPort(Protocol)` with `dispatch(self, req: "LLMDispatchInput") -> "LLMRecording"` (a
        structural `typing.Protocol`, `@runtime_checkable` if useful). PURE-importable: NO provider/FastAPI
        import.
  - [x] Frozen `LLMDispatchInput` (Pydantic v2 `frozen=True, extra="forbid"`, no float) carrying the
        deep-audit request: target file/locator scope, the declared `prompt_template_version`, the tier hint,
        and the work-manifest-scoped inputs the deep pass needs — METADATA only, no secret bytes.
  - [x] Frozen `LLMRecording` DTO (`frozen=True, extra="forbid"`, no float) carrying the captured
        `model_checkpoint`, `prompt_template_version`, token counts (int), `finish_reason`, `credits_used`
        (Fraction/str, NOT float — AR4), `provider_id`, and the declared structured output the deep-audit
        consumes — NO prompt/response/secret bytes (NFR-S1).
  - [x] A typed `LLMDispatchError(ValueError)` (and a `CheckpointDriftError` subclass or a finding-shape
        seam) for the AC5 no-crash matrix.
- [x] **Task 2 — Build the thin Minions adapter `apaa/audit/minions_llm_adapter.py`** (AC: 3, 5)
  - [x] `MinionsLLMAdapter` holding an injected `LLMProviderOrchestrator`; `dispatch(req)` maps
        `LLMDispatchInput` → `RuntimeDispatchRequest`/`LLMRequest` (resolve `max_tokens` via the canonical
        `providers.base.provider_max_tokens`, `temperature` from settings/default), calls `execute_llm`, maps
        the result → `LLMRecording`, CAPTURES `LLMResponse.model` → `model_checkpoint`. Thin: DTO-mapping +
        capture only (§3.3 no-fork).
  - [x] The AC5 no-crash matrix: catch the orchestrator's `RuntimeError("all-providers-unavailable")` →
        typed `LLMDispatchError`; map a timeout / malformed-empty response / budget-halt
        (`budget_exceeded`) → a typed outcome; capture a drifted checkpoint → `CheckpointDriftError`/finding
        seam. NAMED typed catch set, no bare `except`. NFR-S1: never put response bytes in the error/recording.
- [x] **Task 3 — Build the `FakeDispatch` + the deep_audit seam + the substitution helper** (AC: 2, 4)
  - [x] `FakeDispatch` (testing helper) implementing `LLMDispatchPort` → a deterministic, zero-token
        `LLMRecording` (fixed checkpoint/prompt-template/output). No network, no providers import in the fake.
  - [x] `apaa/audit/deep_audit.py` — a THIN seam depending on `LLMDispatchPort` (injected), V1-minimal (the
        AST-grounding logic is 6.2). It consumes an `LLMRecording`; it imports the PORT, never the adapter.
  - [x] The closure-builder helper (in `audit/` or a tiny sibling — REUSE `cache/key.py`, do NOT fork): build
        a `RecordingProducingClosure` from a live `LLMRecording`, folding the captured `model_checkpoint` +
        `prompt_template_version` into the EXISTING slots; `derive_cache_key` over it; prove additive (V1
        no-LLM golden unchanged; distinct captured values → distinct keys).
- [x] **Task 4 — The gates: import-isolation (web + no-LLM), no-crash matrix, non-ASCII, purity** (AC: 5, 6)
  - [x] Extend `_MODULES_UNDER_GUARD` (web-stack gate) with `apaa.audit.ports`,
        `apaa.audit.minions_llm_adapter`, `apaa.audit.deep_audit` (+ any sibling) — all stay
        fastapi/uvicorn/starlette-clean (the adapter importing providers is fine for the WEB gate).
  - [x] Extend the no-LLM gate: assert `apaa.audit.ports` + `apaa.audit.deep_audit` ⊬ `minions_core.providers`
        (PURE seam); CARVE OUT `apaa.audit.minions_llm_adapter` (the ONE allowed providers importer —
        documented). Keep `test_pipeline_is_zero_token` green (`models`/`pipeline`/`cli` unchanged).
  - [x] In NEW `tests/apaa/test_llm_dispatch_port.py` + `tests/apaa/test_minions_llm_adapter.py` (area
        `APAA-AUDIT`, `TC-APAA-AUDIT-001-NN`): the AC5 no-crash matrix (exhaustion / timeout / malformed /
        drift / budget-halt → typed, each RED-first); the AC2 FakeDispatch zero-token path; the AC4 additive
        substitution (golden-unchanged for no-LLM + distinct-values-distinct-keys); the AI-E1-1 non-ASCII
        recording; the AR8 purity (DTOs no I/O/clock/float).
- [x] **Task 5 — Run + mypy + the pre-`review` test-existence precondition** (AC: 7)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
        all pass (1032 baseline + the new audit tests). `mypy` clean on `audit/*` (+ sibling).
  - [x] Confirm NO working-tree diff to the frozen Epic-1..5 surfaces (the helper COMPOSES `cache/key.py`
        read-only; `pipeline.py` byte-identical — DN-WIRING). Confirm NO `.apaa/` byte written, NO
        `cli.py`/HTTP/CI-job change. Confirm the V1 no-LLM cache-key golden is UNCHANGED (no schema bump for
        the placeholder path).
  - [x] **AI-E5-4 / DN-DEFER:** if a NEW defer is filed, file it append-only in
        `_bmad-output/design-artifacts/APAA/deferred-work.md` with the six CC-3 fields. Confirm DF-5-1-A stays
        CLOSED (this story does not reopen it). Do NOT pull 6.2 AST-grounding / 6.3 orphan / 6.4 Prosecutor /
        6.5 cartridge / 6.6 precision / 6.7 HITL into scope.
  - [x] **AI-E5-3 / AI-E2-1 GATE:** the mandatory artifacts (`audit/ports.py` + `minions_llm_adapter.py` +
        `deep_audit.py` + `FakeDispatch` + the substitution helper + the new tests with the no-crash matrix +
        the documented RED-then-green) EXIST + pass BEFORE the `review` flip; the Dev Agent Record is filled
        completely (no blank placeholders).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **The LLM is behind ONE injectable port — determinism quarantine at the substrate (architecture Decision E
  / CC #7 / §324 / §496-497, the scope crux).** "The `LLMDispatchPort` is the only seam between the pure core
  and the non-deterministic LLM substrate; everything downstream is pure folds over recordings." The port is
  a Protocol (DIP). `deep_audit` depends on the PORT TYPE, never the orchestrator. This is NOT a speculative
  abstraction — it is REQUIRED by NFR-D2 injectability (a `FakeDispatch` gives zero-token tests) and by the
  reproducibility floor (the pure core must never touch the LLM). Do NOT collapse the port into the adapter.
- **Reuse the orchestrator BY IMPORT, NO fork (§3.3 / AR7 / §272-278).** The adapter HOLDS an
  `LLMProviderOrchestrator` and CALLS `execute_llm` — it inherits the fallback chain + circuit breaker +
  cost attribution, which feeds APAA cost governance (3.1) + honest degradation for free. The adapter is
  THIN: DTO-mapping + checkpoint capture only. It NEVER reimplements routing/retry/breaker, and NEVER imports
  `minions_core.api.* / services.api_app / app_factory / api_server` (leaf-module rule — those are the
  FastAPI-bearing modules).
- **The import-isolation gate distinguishes the PURE core from the impure adapter seam (AR9 — the load-bearing
  gate decision).** TWO orthogonal gates: (a) the WEB-stack gate (`_FORBIDDEN` = fastapi/uvicorn/starlette)
  applies to EVERY `apaa.*` module INCLUDING the adapter — providers are verified FastAPI-free, so the adapter
  importing `providers.orchestrator` keeps the web gate green; (b) the no-LLM gate (`_LLM_FORBIDDEN_PREFIXES`
  = `minions_core.providers` + `minions_core.apaa.audit`) applies to the PURE seam — `models`/`pipeline`/`cli`
  (unchanged, stay zero-token) AND the new `audit/ports.py`/`audit/deep_audit.py` (must NOT pull providers).
  The adapter (`audit/minions_llm_adapter.py`) is the ONE explicitly-allowed providers importer — CARVE IT
  OUT of the no-LLM gate (documented). Net: pure core ⊬ providers ⊬ FastAPI; adapter → providers (FastAPI-free)
  but ⊬ FastAPI.
- **Capture the model checkpoint from the API RESPONSE, not config (AR5/R3 — the closure input made real).**
  `LLMResponse.model` is the dispatch-actual model id the provider returned — that is the captured checkpoint
  → `LLMRecording.model_checkpoint`. A config string is NOT a checkpoint (the orchestrator may fall back to a
  different provider/model). The captured value flows into the 5.1 cache-key `model_checkpoint` slot, so a
  silent model rotation moves the key (the AR5 honesty property; the `checkpoint_drift` seam).
- **The 5.1 placeholders are substituted ADDITIVELY — no key-SHAPE change (DF-5-1-A closure / DN-SUBST).**
  5.1 reserved BOTH slots (`model_checkpoint`, `prompt_template_version`) precisely so 6.1 substitutes a real
  value WITHOUT a schema bump. The substitution helper builds a `RecordingProducingClosure` from a live
  `LLMRecording` and folds the captured values into the EXISTING slots. **CRITICAL:** the V1 no-LLM
  (heuristic/claim-proxy) path STILL uses the placeholder defaults and derives the SAME golden key as before
  6.1 — NO regression, NO schema bump for the placeholder path. A bump is required ONLY if a real value would
  collide a placeholder-path key, which it cannot (distinct values → distinct keys, the drift seam). Do NOT
  edit `cache/key.py` unless a genuine bump is required (it is not for V1).
- **The full LLM no-crash matrix → typed outcome, NEVER an uncaught raise (AR10 / NFR-R1 / AI-E5-1 — the
  headline Epic-6 risk surface, called out by the Epic-5 retro §6).** The orchestrator raises
  `RuntimeError("all-providers-unavailable")` on chain exhaustion — the adapter MUST catch+map it to a typed
  `LLMDispatchError`. The DECLARED failure set is: provider-chain exhaustion, transport timeout,
  malformed/empty response, captured-checkpoint drift, budget halt (`budget_exceeded`). Enumerate the FULL
  set and cover EACH member RED-first (the AI-E5-1 complete-the-declared-set keystone-adequacy discipline,
  now at the no-crash-input-shape level). NAMED typed catch set, no bare `except: pass`. This is the surface
  the retro predicted as the highest Epic-6 risk; apply the AI-E4-1/E5-1 checklist proactively.
- **No source/secret/prompt/response bytes in the `LLMRecording` (NFR-S1 / architecture CC #5 — producer-side
  redaction).** The `LLMRecording` carries METADATA (captured checkpoint, prompt-template version, token
  counts, finish_reason, credits, provider_id) + the DECLARED STRUCTURED OUTPUT the deep-audit consumes
  (claim/locator-shaped) — NEVER raw prompt/response bytes or secret values. Redaction is a property of the
  PRODUCER (the adapter), not a post-filter. The 4.4 randomized-canary suite is the durable backstop; 6.1
  writes NO `.apaa/` byte so no new write path needs sweeping (the live pipeline write is 6.2).
- **No floats / determinism — inherited (AR4/NFR-P1).** Any credit/ratio-shaped field on the DTOs is
  `Fraction`/string, never float; the single serializer raises on a float leaf. The closure-from-recording
  key is order-independent (the 5.1 sorted/canonical derivation). Run under `PYTHONIOENCODING=utf-8`; a
  non-ASCII recording derives a stable key (AI-E1-1).
- **Frozen contracts unchanged (AR8/NFR-M2).** The substitution helper COMPOSES `cache/key.py` read-only.
  Verify NO working-tree diff to `store/{canonical,envelope}.py`, `cache/key.py` (unless a genuine bump —
  not for V1), `ledger/recording.py`, `models.py`, `verdict/*`, `detectors/*`, `pipeline.py` (byte-identical
  — DN-WIRING; the live deep-path call site is 6.2). The new `audit/` modules join `_MODULES_UNDER_GUARD`
  (extend, NOT fork).

### Project Structure Notes

- **New sub-package `minions_core/apaa/audit/`** (per architecture §439-442): `ports.py` (the port +
  DTOs, PURE), `minions_llm_adapter.py` (the impure adapter — Decision E), `deep_audit.py` (depends on the
  port; thin in V1, the AST logic is 6.2). Add `audit/__init__.py`. This is the FIRST `audit/` story; it
  bootstraps the package.
- **The `FakeDispatch`** lives in the test tree (or a clearly-marked testing helper in `audit/`), NOT the
  production adapter — it is the zero-token double for NFR-D2 and every later Epic-6 deep test.
- **`pipeline.py` stays byte-identical (DN-WIRING).** 6.1 is library-only: it builds the seam + the helper +
  the gates. The LIVE end-to-end LLM run (the pipeline call site that drives `deep_audit` through the real
  adapter) is fenced to 6.2 (the AST-grounding deliverable that closes DF-1-7-B). Do NOT wire a live LLM call
  into the pipeline this story.
- **Test area `APAA-AUDIT`** (`TC-APAA-AUDIT-001-NN`) — the natural area for `audit/`. Lock the next free
  index in each new test module's docstring. New tests:
  `tests/apaa/test_llm_dispatch_port.py` (port/DTOs/FakeDispatch/substitution) +
  `tests/apaa/test_minions_llm_adapter.py` (adapter mapping + checkpoint capture + the no-crash matrix); the
  two import-isolation gate extensions live in the existing `tests/apaa/test_no_web_imports.py`.

### Forward-coupling / deferral notes (do NOT build here)

- **Story 6.2 (full Python AST-grounding, FR7) CLOSES DF-1-7-B** — the carried 🟡 interim-over-grading debt,
  now ONE STORY AWAY (AI-E5-5, the HARD Epic-6 deliverable). 6.2 rides THIS port: its deep-claim validator
  depends on `LLMDispatchPort` and consumes the `LLMRecording`. Keep the port shaped for that consumer. Do
  NOT build the AST validator here.
- **The live mid-run `checkpoint_drift` comparison + finding pipeline-wiring + abort/re-audit loop** is
  shared with the 6.2 deep-audit pipeline. 6.1 captures the checkpoint + exposes it on the `LLMRecording` +
  defines the `CheckpointDriftError`/finding seam + proves two captured values → two keys; it does NOT build
  the live loop.
- **6.4 (Prosecutor) is a PURE recording-CONSUMER that CANNOT call an LLM** (architecture §245) — it consumes
  recordings, it does NOT use this port. Do not couple the Prosecutor to the port. 6.7 (HITL) populates the
  5.3 rejection seam. Neither is 6.1's work.

### References

- Epic: `_bmad-output/design-artifacts/APAA/epics.md` §Epic 6 / Story 6.1 (lines 828-855).
- Architecture: `_bmad-output/design-artifacts/APAA/architecture.md` Decision E (§265-281, LLM dispatch via
  port), §322-325 (the port is the only pure/non-det seam), §382-386 (depend-on-the-port reuse pattern),
  §439-442 (`audit/` package), §487-499 (architectural boundaries — LLM boundary), AR5/AR7/AR8/AR9/AR10.
- PRD drivers: FR7 (deep-claim AST validation — 6.2), FR12 (orphan — 6.3), FR19 (Prosecutor — 6.4) all RIDE
  this seam; NFR-D2 (zero-token core), NFR-P2 (stack-agnostic claim interface).
- Prior story (placeholder source): `5-1-cache-key-derivation-recording-producing-closure-ci-canary.md` +
  `minions_core/apaa/cache/key.py` (`V1_MODEL_CHECKPOINT` / `V1_PROMPT_TEMPLATE_VERSION` / `CACHE_KEY_SCHEMA_VERSION`
  / `RecordingProducingClosure`).
- Reused Minions surfaces: `minions_core/providers/orchestrator.py` (`LLMProviderOrchestrator.execute_llm`),
  `minions_core/providers/base.py` (`LLMRequest`/`LLMResponse`/`RuntimeDispatchRequest`/`RuntimeDispatchResult`/`WorkerTier`/`provider_max_tokens`).
- Gate: `tests/apaa/test_no_web_imports.py` (`_FORBIDDEN`, `_MODULES_UNDER_GUARD`, `_LLM_FORBIDDEN_PREFIXES`,
  `_assert_no_llm_import`, `test_pipeline_is_zero_token`).
- Retro carry-forward: `_bmad-output/design-artifacts/APAA/epic-5-retro-2026-06-29.md` §6-7 (AI-E5-1
  complete-the-declared-set; AI-E5-3 committed test-existence guard; AI-E5-5 DF-1-7-B → 6.2; AI-E5-7 gates +
  partial-reuse docstrings); standing AI-E1-1 (non-ASCII/locale).
- Defer register: `_bmad-output/design-artifacts/APAA/deferred-work.md` (DF-5-1-A — CLOSED in 5.1, targeted
  this story; confirm it stays closed).

## Dev Agent Record

### Context Reference

- Story file (this) + `_bmad-output/design-artifacts/APAA/sprint-status.yaml` (APAA-local tracker).
- Reused Minions surfaces (BY IMPORT, no fork): `minions_core/providers/orchestrator.py::LLMProviderOrchestrator.execute_llm`, `minions_core/providers/base.py` (`LLMRequest`, `RuntimeDispatchRequest`, `RuntimeDispatchResult`, `provider_max_tokens`), `minions_core/orchestration/worker_agent_pool.py` (`WorkerAgentResult`, `LlmOutputMetadata`, `WorkerTier`, `WorkerAgentConfig`).
- 5.1 closure reused read-only: `minions_core/apaa/cache/key.py` (`RecordingProducingClosure`, `derive_cache_key`, `V1_MODEL_CHECKPOINT`, `V1_PROMPT_TEMPLATE_VERSION`, `CACHE_KEY_SCHEMA_VERSION="2"`).
- Gate extended (not forked): `tests/apaa/test_no_web_imports.py`.

### Agent Model Used

- claude-opus-4-8 (BMAD dev-story, mode=implement).

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` → **1062 passed, 1 skipped, 4 subtests** in ~60s (Epic-5 baseline 1032 + 30 new audit tests).
- New-module subset: `tests/apaa/test_llm_dispatch_port.py` + `test_minions_llm_adapter.py` + `test_no_web_imports.py` → 35 passed.
- `mypy --follow-imports=silent` on `audit/ports.py` + `deep_audit.py` + `minions_llm_adapter.py` → **Success: no issues found in 3 source files**. (The repo-wide non-silent mypy reports only PRE-EXISTING errors in unchanged files — `config/__init__.py`, `orchestration/worker_agent_pool.py`, `providers/base.py` — NOT in any new `audit/*` file; this matches the project's per-file mypy model.)

### Completion Notes List

- **Port (AC1, AR7/AR8/NFR-D2):** `apaa/audit/ports.py` defines `LLMDispatchPort(Protocol, @runtime_checkable)` with the single `dispatch(req: LLMDispatchInput) -> LLMRecording`, plus frozen (`frozen=True, extra="forbid"`, no float) `LLMDispatchInput`/`LLMRecording` DTOs and typed `LLMDispatchError(ValueError)` / `CheckpointDriftError`. PURE-importable — proven provider-free by the new `test_pure_audit_seam_is_provider_free`.
- **Adapter (AC3/AC5, AR5/§3.3):** `apaa/audit/minions_llm_adapter.py::MinionsLLMAdapter` HOLDS an injected `LLMProviderOrchestrator`, maps `LLMDispatchInput → RuntimeDispatchRequest/LLMRequest`, calls `execute_llm`, and CAPTURES the dispatch-actual model id from `result.worker_results[0].llm_metadata.model_id` (which `build_worker_result_from_llm` sets from `LLMResponse.model`) → `LLMRecording.model_checkpoint`. Thin: DTO-mapping + capture only; no routing/breaker reimplementation. Credits rendered as a frozen `Fraction` STRING (AR4, no float).
- **No-crash matrix (AC5, AR10/AI-E5-1 — the headline Epic-6 risk):** named typed catch set — `RuntimeError("all-providers-unavailable")` → `provider-chain-exhausted`; any other `RuntimeError`/`Exception` (timeout) → `transport-error`; `budget_exceeded` result → `budget-halt`; empty/no-captured-model result → `malformed-response`; captured≠pinned checkpoint → `CheckpointDriftError`. Each leg RED-first via `_RawRaisingAdapter` then green-typed. NFR-S1: error/recording carry only structured ids, never bytes.
- **FakeDispatch (AC2, NFR-D2):** zero-token deterministic double in the test tree; feeds the REAL closure-builder token-free.
- **Additive substitution (AC4, AR5/DF-5-1-A):** `deep_audit.build_closure_from_recording` folds the captured `model_checkpoint` + `prompt_template_version` into the EXISTING 5.1 closure slots — NO key-SHAPE change, NO `CACHE_KEY_SCHEMA_VERSION` bump. Proven: V1 no-LLM placeholder-default key is byte-identical (`test_v1_no_llm_golden_key_unchanged_by_substitution_path`); distinct captured checkpoint / prompt-template → distinct key.
- **Deep-audit seam (AC1, DIP):** `apaa/audit/deep_audit.py::DeepAuditSeam` depends on the PORT TYPE only; thin V1 (AST grounding is 6.2). Provider-free.
- **Gates (AC6/AC7):** web-stack gate `_MODULES_UNDER_GUARD` EXTENDED (not forked) with the three `audit/` modules; new `test_pure_audit_seam_is_provider_free` (PURE seam ⊬ providers) + `test_adapter_is_the_allowed_provider_importer` (adapter IS the carve-out, but ⊬ FastAPI api/service modules). Non-ASCII recording round-trips to a stable key. All new files ≤1200 lines.
- **Scope fences honored:** `pipeline.py`/`cli.py`/`models.py`/`cache/key.py`/`store/*`/`verdict/*`/`detectors/*`/`ledger/recording.py` BYTE-IDENTICAL (no working-tree diff); NO `.apaa/` byte written; NO new CI job / HTTP route / cli subcommand. The live mid-run drift abort/re-audit loop + live end-to-end pipeline call site remain fenced to 6.2. DF-5-1-A confirmed CLOSED (not reopened). No NEW defer filed.

### File List

- `minions_core/apaa/audit/__init__.py` (new — package shell)
- `minions_core/apaa/audit/ports.py` (new — port Protocol + frozen DTOs + typed errors)
- `minions_core/apaa/audit/minions_llm_adapter.py` (new — impure adapter + no-crash matrix)
- `minions_core/apaa/audit/deep_audit.py` (new — pure port-only seam + closure-builder)
- `tests/apaa/test_llm_dispatch_port.py` (new — port/DTOs/FakeDispatch/substitution)
- `tests/apaa/test_minions_llm_adapter.py` (new — adapter mapping + checkpoint capture + no-crash matrix)
- `tests/apaa/test_no_web_imports.py` (modified — extended `_MODULES_UNDER_GUARD` + 2 new gate tests)
- `_bmad-output/design-artifacts/APAA/stories/6-1-llm-dispatch-port-minions-orchestrator-adapter.md` (status → review, Dev Agent Record, Change Log)
- `_bmad-output/design-artifacts/APAA/sprint-status.yaml` (story → review; epic-6 → in-progress; last_updated)

## Senior Developer Review (AI)

**Reviewer:** Code-Review gate (BMAD adversarial) — claude-opus-4-8. **Date:** 2026-06-29. **Iteration:** 1. **Outcome:** PASS → `done`.

### Scope reviewed
New `minions_core/apaa/audit/{__init__,ports,minions_llm_adapter,deep_audit}.py`; new `tests/apaa/{test_llm_dispatch_port,test_minions_llm_adapter}.py`; extended `tests/apaa/test_no_web_imports.py`. Read against architecture Decision E / §324 / §496-497, the 5.1 cache-key closure (`cache/key.py`), and the Epic-5 retro carry-forwards (AI-E5-1/3/5/7, AI-E1-1, NFR-S1).

### Adversarial findings — three layers
- **Blind Hunter (correctness/security):** No correctness or security bug found. `dispatch` wraps `execute_llm` in a named typed catch set (`RuntimeError`→exhausted/transport, `Exception`→transport); `_map_result` raises only typed `LLMDispatchError`/`CheckpointDriftError` AFTER the try, so the typed outcomes are not swallowed and no raw `RuntimeError`/`Exception` escapes the seam. `_build_request`/`_map_result` are construction-only over coerced/validated values (`_resolve_tier` swallows bad tiers → STANDARD; `provider_max_tokens` falls back without raising) — no latent uncaught path in the declared matrix. NFR-S1 verified structurally: `LLMRecording` has no field that can hold prompt/response bytes; errors carry only `reason=`/`provider=` structured ids; `LLMRequest(prompt="")` carries no source bytes. `execute_llm(RuntimeDispatchRequest)` signature matches the reused orchestrator.
- **Edge Case Hunter (boundary/branch):** Matrix is complete and each branch is covered — exhaustion, transport timeout, malformed/empty result, empty-captured-model, budget halt, drift, and matching-pinned (no false drift). RED-first baselines (`_RawRaisingAdapter`) genuinely demonstrate the pre-fix failure (raw raise / IndexError / silent wrong-checkpoint), so the green tests would catch a regression that swallowed or leaked an exception. Non-ASCII checkpoint/path/output round-trips to a stable 64-hex key. `credits_used` float→`Fraction` string proven (`1.5`→`"3/2"`).
- **Acceptance Auditor (AC/spec conformance):** AC1–AC7 all met. Determinism quarantine proven by two orthogonal subprocess gates (`test_pure_audit_seam_is_provider_free`: ports/deep_audit ⊬ `minions_core.providers`, correctly narrowed to the providers prefix; `test_adapter_is_the_allowed_provider_importer`: adapter IS the carve-out AND ⊬ FastAPI api/service — sharp, exit-2 if it fails to import providers). Reuse-by-import confirmed (holds orchestrator, calls `execute_llm`, no routing/breaker fork). Additive substitution confirmed: `build_closure_from_recording` folds captured checkpoint + prompt-template into the EXISTING 5.1 slots, V1 no-LLM golden key byte-identical (`test_v1_no_llm_golden_key_unchanged_by_substitution_path`), distinct captured values → distinct keys; `CACHE_KEY_SCHEMA_VERSION` stays `"2"`, `cache/key.py` untouched. `pipeline.py`/`models.py`/`cli.py`/`store/*`/`verdict/*`/`detectors/*`/`ledger/recording.py` not edited by this story.

### Independent verification
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` → **1062 passed, 1 skipped, 4 subtests** (matches the Epic-5 1032 baseline + 30 new APAA-AUDIT tests).
- `mypy --follow-imports=silent` on the three new `audit/*` modules → **Success: no issues found in 3 source files**.
- `_MODULES_UNDER_GUARD` EXTENDED (not forked) with the three audit modules; web gate + no-LLM gate both green. No `.apaa/` write, no new CI job, no HTTP route, no `cli.py` subcommand, headless. All new files ≤1200 lines.

### Notes (non-blocking)
- The new `tests/security/test_apaa_secret_containment.py` (untracked, from earlier APAA work) drives only the Epic-1 zero-token pipeline and does not exercise the new `LLMRecording`. This is acceptable for 6.1: the recording is structurally redaction-safe (no source-byte field, pinned by TC-APAA-AUDIT-001-32) and 6.1 writes no `.apaa/` byte. When 6.2 wires the live deep path's `.apaa/` write, the randomized-canary suite should be extended to sweep the live-LLM write path — recommend tracking as a 6.2 follow-up, not a 6.1 defect.

No `decision-needed` or `patch` findings. No unresolved High/Medium issues. No new defer filed; DF-5-1-A confirmed closed (not reopened).

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-06-29 | 0.1 | Story drafted (create-story) — Epic 6 FIRST story; LLM dispatch port + Minions orchestrator adapter; additive substitution of the 5.1 cache-key placeholders; full no-crash matrix; import-isolation gate distinguishes pure core from impure adapter seam. Status set ready-for-dev. | Scrum Master (Bob) |
| 2026-06-29 | 0.2 | Implemented (dev-story) — `apaa/audit/` bootstrapped: PURE `ports.py` (`LLMDispatchPort` Protocol + frozen `LLMDispatchInput`/`LLMRecording` + typed `LLMDispatchError`/`CheckpointDriftError`), impure `minions_llm_adapter.py` (holds + calls `LLMProviderOrchestrator.execute_llm`, captures `LLMResponse.model` → `model_checkpoint`, full no-crash matrix RED-then-green: chain-exhaustion/timeout/malformed/budget-halt → `LLMDispatchError`, drift → `CheckpointDriftError`), pure `deep_audit.py` (port-only DIP seam + `build_closure_from_recording` additive substitution into the EXISTING 5.1 slots — no key-shape change, V1 no-LLM golden byte-identical). `FakeDispatch` zero-token double + 30 new `APAA-AUDIT` tests. Web gate extended (not forked) with the 3 audit modules; no-LLM gate proves pure seam ⊬ providers + carves out the adapter. 1062 passed / 1 skipped, mypy clean on new files, frozen Epic-1..5 surfaces byte-identical, no `.apaa/` write, DF-5-1-A stays closed. Status → review. | Dev (Amelia) |
