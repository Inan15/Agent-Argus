# Story 6.7: HITL STOP/PROCEED escalation + append-only decision record — [Tier B]

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/APAA/`; the tracker is `_bmad-output/design-artifacts/APAA/sprint-status.yaml`
> (NOT the Minions platform tracker at `_bmad-output/implementation-artifacts/sprint-status.yaml`). All
> CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only, §3.8 12-Factor + secret masking, §3.4
> evidence immutability). Run all gate/test commands under `PYTHONIOENCODING=utf-8` (Windows / cp1252).
>
> **This is the SEVENTH and LAST story of Epic 6** (Trust Substrate — Self-Audit, Prosecutor & Precision,
> Tier-B). It builds on the fully-done Epics 1+2+3+4+5 and on **done Stories 6.1** (the `LLMDispatchPort` +
> `MinionsLLMAdapter` + `FakeDispatch`), **6.2** (FR7 full Python AST-grounding `audit/grounding.py`),
> **6.3** (the FR12 orphan/dead-code detector), **6.4** (the FR19 adversarial Prosecutor `verdict/prosecutor.py`
> + the CC #4 `cross_partition` cut-edge pass), **6.5** (the FR20 measurement substrate — the cartridge
> registry + self-audit harness), and **6.6** (the precision replay harness + validation protocol). `epic-6`
> is already `in-progress`. After this story completes, Epic 6 has all seven stories `done` and only the
> Minions-dogfood capstone (Epic 7) remains.
>
> **THIS STORY DELIVERS THE HITL DECISION SURFACE (FR23 + FR24).** APAA can halt at a human STOP/PROCEED
> gate on a **pattern-matched** escalation condition, **default to STOP** (never LLM-judgment), **park at
> STOP on gate-timeout (never auto-PROCEED)**, and record each human decision in an **append-only decision
> record** under `.apaa/decisions/` — and log the STOP even if the full record is deferred. Per the
> architecture it lands TWO new PURE-CORE + THIN-IMPURE modules in a NEW `governance/` sub-package:
> (1) `minions_core/apaa/governance/escalation.py` — the PURE, pattern-matched STOP/PROCEED gate (rule
> matcher + default-STOP + time-boxed park-at-STOP resolution), zero-LLM-token; and (2)
> `minions_core/apaa/governance/decision_record.py` — the append-only decision-record writer that REUSES
> the Story 1.1 canonical serializer + content-hashed, prev-hash-chained envelope + the Story 1.3
> `ApaaStoreWriter` + the already-reserved `.apaa/decisions/` subdir (NO forked persistence mechanism). It
> is a **decision-RECORD contract** — a headless append-only artifact + its function seam — NOT a UI
> (§3.7): the "human" supplies the decision through the function/CLI seam, and the record is a
> deterministic `.apaa/` artifact.

## Story

As a **Delivery Orchestrator** — who is accountable for whether an ambiguous, non-deterministic, or
high-stakes audit outcome ships, and who is therefore far more harmed by an APAA that silently PROCEEDs
past a case it could not confidently adjudicate (a false green nobody signed off on) OR that auto-PROCEEDs
when a human simply did not respond in time (the exact fail-open trap FR23 forbids) than by an APAA that
STOPs by default and forces an auditable human decision — and who needs, when the audit is later
questioned, to read exactly which cases escalated, who decided STOP vs PROCEED, when, and on what
pattern-matched trigger,
I want **a PURE pattern-matched STOP/PROCEED escalation gate** (`minions_core/apaa/governance/escalation.py`)
that fires on a configured escalation condition (a deterministic rule match over the ledger/findings —
NOT an LLM judgment), **defaults to STOP**, and on a configured gate-timeout window with no human response
**parks at STOP and never auto-PROCEEDs**, plus **an append-only decision record**
(`minions_core/apaa/governance/decision_record.py`) that appends each human STOP/PROCEED decision to
`.apaa/decisions/` — reusing the Story 1.1 canonical serializer + the content-hashed, prev-hash-chained
envelope + the Story 1.3 `ApaaStoreWriter` (no forked persistence), and logging the STOP even if the full
record is deferred,
so that **a non-deterministic or high-stakes case escalates to a human, defaults safe (STOP), never
fails open on timeout, and the decision is permanently auditable** — the escalation is deterministic and
zero-token (a pattern match, testable with no LLM), the default is STOP so silence never ships a verdict,
the timeout parks at STOP so a slow human never becomes an auto-PROCEED, and the append-only record is a
content-hashed, prev-hash-chained, secret-free `.apaa/` artifact that a later auditor can replay — because
honest, human-accountable governance under pressure is exactly the trust layer this Tier-B epic exists to
deliver.

## Story Context

This is **Story 7 of Epic 6** (Trust Substrate, Tier-B — the "proven, not asserted, human-accountable
depth" moat). It delivers the **HITL escalation gate + the append-only decision record** — the FR23/FR24
governance surface every earlier Epic-6 story deferred here. It CREATES a NEW `governance/` sub-package
(no `governance/` dir exists in `minions_core/apaa/` yet); the two modules are the only new production
files.

**The persistence substrate this record REUSES already exists and is FROZEN — REUSE it, do NOT fork (the
no-fork keystone, §3.3 / AR7).** The append-only decision record is NOT a new storage mechanism; it is a
new PAYLOAD written through the existing spine:
- **The canonical serializer (`minions_core/apaa/store/canonical.py`).** THE single serializer
  (`sort_keys=True, separators=(",",":"), ensure_ascii=False`, `\n`-terminated UTF-8; `Decimal`/`Fraction`
  only, NO float — AR4). The decision record's bytes are EXACTLY `canonical.dumps_bytes(...)`; the module
  authors NO second `json.dumps`.
- **The content-hashed, prev-hash-chained envelope (`minions_core/apaa/store/envelope.py`).** `Envelope` +
  `EnvelopeWriter.build` — content-hash over the canonical payload ONLY (excludes volatile
  `run_id`/`created_at`), `prev_hash` chains to the prior artifact (genesis sentinel `"0"*64` at the head),
  `schema_version` + `producer` + `apaa_version` present (FR25/NFR-A1/NFR-D3). **The append-only chain uses
  this EXISTING prev-hash chaining** — each new decision's envelope `prev_hash` = the prior decision
  envelope's `content_hash` (tamper-evident, ordered append).
- **The `.apaa/` store writer (`minions_core/apaa/store/writer.py::ApaaStoreWriter`).** The IMPURE,
  containment-checked, content-addressed writer. `write_payload(subdir, payload, *, schema_version,
  producer, prev_hash=...)` wraps a payload in an envelope then writes `<subdir>/<content_hash>.json`
  (content-addressed, AR11) and returns the `.apaa/`-root-relative POSIX locator. **The decision record
  writes through this — `subdir="decisions"` — it does NOT open files or build JSON itself.**
- **The store paths / containment (`minions_core/apaa/store/paths.py::ApaaStorePaths`).** The `.apaa/` fixed
  tree ALREADY reserves `decisions/` in `APAA_SUBDIRS` (`state/ · assignments/ · findings/ · decisions/ ·
  cache/`). Containment (`is_relative_to`, never `str.startswith`; typed `WorkspaceContainmentError` before
  any write) is inherited via the writer — the record module adds NO second containment check (NFR-S5/AR7).
- **The store reader (`minions_core/apaa/store/reader.py::ApaaStoreReader`).** Re-verifies `content_hash`
  (tamper guard → `StoreIntegrityError`). The append-only-verification test REUSES it to read back the
  decision chain and confirm the prev-hash links + tamper-evidence.
- **The finding contract (`minions_core/apaa/ledger/recording.py::Recording` + `Locator`).** The
  escalation condition matches over the SAME frozen findings the verdict folds over (`rule_id`,
  `advisory`, `depth_supported`, `locators`) — NEVER over source bytes (NFR-S1). The gate is a PURE
  recording-consumer, exactly like the 6.4 Prosecutor.
- **The Prosecutor precedent (`minions_core/apaa/verdict/prosecutor.py`).** The pattern to MIRROR for the
  pure gate: a zero-LLM-token, deterministic recording-consumer with a typed error only on a genuinely
  malformed argument, degrading (never raising) on empty/None inputs. The escalation gate is the SAME
  pure-consumer shape (rule match over findings/ledger → a `STOP`/`PROCEED`/`ESCALATE` decision), and — per
  the FR23 lock — the trigger is PATTERN-MATCHED (a deterministic rule), NOT LLM-judgment (there is NO LLM
  dispatch anywhere in this story).

**THE FR23 LOCK — the fail-safe defaults (read twice).** Per the epic (Story 6.7 ACs) + the PRD (FR23):
- **The escalation trigger is PATTERN-MATCHED, not LLM-judgment.** The gate fires on a deterministic rule
  match (e.g. a configured rule-id / finding-shape / verdict-state pattern), a PURE zero-token function.
  It NEVER calls an LLM to decide whether to escalate.
- **The gate DEFAULTS TO STOP.** When an escalation condition fires and no human decision is present, the
  resolved outcome is STOP — never a default PROCEED. Silence blocks; it never ships.
- **On gate-timeout with no human response, APAA PARKS AT STOP — it NEVER auto-PROCEEDs.** A configured
  time-boxed window that elapses with no decision resolves to STOP (parked), the fail-CLOSED default. This
  is the keystone: a slow/absent human must never become an auto-PROCEED.
- **The STOP is logged even if the full decision record is deferred (FR24).** If, at escalation time, only
  the STOP event can be recorded (the full human decision arrives later, or the record write is deferred),
  the STOP itself is still logged — the audit trail never loses the fact that a STOP occurred.

**THE FR24 LOCK — append-only, tamper-evident, secret-free.**
- **Append-only.** The decision record is APPEND-ONLY: a new decision is a NEW content-addressed artifact
  under `.apaa/decisions/` whose envelope `prev_hash` chains to the prior decision's `content_hash`. There
  is NO in-place update / delete of a prior decision (mirrors the Minions §3.4 evidence-immutability +
  hash-chained-ledger discipline — a decision, once recorded, is permanent).
- **Tamper-evident.** The chain is verifiable through the EXISTING reader (`content_hash` re-verify →
  `StoreIntegrityError` on mutation; the `prev_hash` links form the ordered chain).
- **Secret-free (NFR-S1).** A decision record carries ONLY: the decision (STOP/PROCEED), the pattern-matched
  trigger provenance (rule-id / escalation-reason token), the finding-id(s) / locator provenance that
  triggered it, a decider-id token, and a deterministic decision-id — NEVER source bytes, a secret value, or
  an absolute host path. The decider-id is a caller-supplied opaque token (an operator/role id), not free
  text that could leak content.

**The FOUR members of the HITL declared set (the deliverable checklist, mechanizing AI-E5-1).** The gate +
record must cover EACH, RED-first where a naive implementation would miss it:
1. **Pattern-matched escalation firing + default-STOP.** A configured escalation condition (a deterministic
   rule match over findings/ledger/verdict-state) fires and, absent a human decision, resolves to STOP —
   RED-first against a gate that defaults to PROCEED or that reaches for an LLM to decide.
2. **Time-boxed park-at-STOP (never auto-PROCEED).** A configured timeout window that elapses with no human
   response resolves to STOP (parked) — RED-first against a gate that auto-PROCEEDs (fails open) on timeout.
3. **Append-only, prev-hash-chained decision record.** Each human decision appends a NEW content-addressed
   `.apaa/decisions/` artifact whose envelope `prev_hash` chains to the prior decision — RED-first against a
   writer that overwrites / mutates a prior decision, or that forks a second serializer/envelope/writer.
4. **STOP logged even if the full record is deferred.** The STOP event is logged at escalation time even
   when the full human decision record is deferred — RED-first against an implementation that only records
   the STOP once the human responds (losing the escalation fact on a deferred/abandoned decision).

**The escalation-outcome + decision-record schema (pure, frozen, deterministic — DN-SCHEMA).** Build the
PURE frozen types the gate returns and the record persists, carrying: the escalation outcome
(`STOP` / `PROCEED` — a closed enum; a resolved `ESCALATE`-pending state may be represented as
STOP-parked), the pattern-matched trigger provenance (rule-id / reason token), the triggering finding-id(s)
/ locator provenance, the decider-id token (for a human decision; absent/`None` for a default/timeout STOP),
a resolution kind (`default_stop` / `timeout_parked_stop` / `human_decision`), and a deterministic
content-derived decision-id (NEVER `uuid4`/clock/counter — AR4/AR11). The types are PURE (no I/O, no clock,
no LLM, no random — AR8); the RECORD payload is written through the existing writer/envelope. All ids are
content-derived; no float, no wall-clock in the payload.

**REUSE the existing spine — no second persistence, no LLM, no second containment (§3.3 / AR7).** The
decision record composes `ApaaStoreWriter.write_payload(subdir="decisions", ...)` + `EnvelopeWriter.build`
+ the canonical serializer + the reserved `decisions/` subdir. The escalation gate composes the frozen
`Recording`/`CoverageLedger`/`AuditVerdict` as a PURE consumer (mirroring the 6.4 Prosecutor). Neither
module imports `fastapi/uvicorn/starlette`, `minions_core.providers.*`, or any LLM dispatch surface (the
no-web-imports + no-LLM gates stay green). Neither module authors a second `json.dumps`, a second hasher,
a second containment check, or a second `.apaa/` writer.

**THE SIZE CONSTRAINT — both modules are production modules; mind ≤1200 lines (NFR-M1 / §3.2).** The gate is
pure rule-match + resolution logic; the record is thin append-only wiring over the writer. Keep each
cohesive; if either approaches 1200 lines split by responsibility (the pure gate resolution vs. the
schema types; the record writer vs. the chain-read verifier) — measure first, do not split speculatively.

**Scope vs the rest of APAA (explicit deferrals — do NOT pull forward).**
- **6.1–6.6 (the LLM port, AST-grounding, orphan detector, Prosecutor, cartridge substrate, precision
  harness)** — DONE. 6.7 COMPOSES the frozen findings/ledger/verdict as a pure consumer; it does NOT add or
  edit a detector, the Prosecutor, or the precision harness.
- **The Minions dogfood proof run (Epic 7)** — out of scope. 6.7 delivers the HITL surface + the append-only
  record; it does NOT run APAA against Minions, size a budget, or produce the proof artifact.
- **An LLM-driven escalation adjudicator** — out of scope AND forbidden by the FR23 lock: V1 escalation is
  PATTERN-MATCHED (deterministic), not LLM-judgment. A richer LLM-driven escalation is a documented FORWARD
  seam (behind the 6.1 `LLMDispatchPort`, a `FakeDispatch` for zero-token tests) — NEVER a direct
  `minions_core.providers` import, NEVER the V1 default.
- **A live async/blocking wait for a human, a notification system, a webhook, or a queue** — out of scope.
  The gate is a PURE resolution over `(escalation_condition, optional_human_decision, timeout_elapsed)` — the
  "wait" and any human-input transport is the CALLER's concern (the CLI/orchestrator seam); 6.7 delivers the
  deterministic resolution + the record contract, not a live wait loop.
- **A new HTTP route / FastAPI surface / UI (§3.7)** — out of scope. The HITL surface is a decision-RECORD
  contract + its function seam, headless.
- **A new `cli.py` flag / wiring the gate into `pipeline.py`'s straight-line run** — the story DELIVERS the
  gate + record modules + their tests. Wiring the escalation gate into the live pipeline invocation (a
  pipeline call site / a `cli.py` `--escalate`/`--decision` flag) is a FOLLOW-UP if not required to prove
  the ACs; if the AC proof needs a minimal invocation seam, add ONLY the minimal seam and record the
  decision in the Change Log (do NOT change the frozen pipeline dataflow / the `POST`-less headless contract).
- **A new `.github/workflows` CI job** — the tests ship as a `tests/apaa/` pytest module + extend the
  existing security suite if a new write path is introduced; they run under the EXISTING APAA pytest CI
  invocation (the durable backstop, AR9). NO new CI job (mirrors the 6.1–6.6 "no new CI job" fence).
- **Editing any frozen Epic-1..6 contract** (`store/*` / `ledger/*` / `verdict/*` / `detectors/*` /
  `cache/*` / `pipeline.py` / `models.py` / the 6.5 `_registry.py`) — the modules COMPOSE them as-is. The
  ONLY production-tree additions are the NEW `governance/escalation.py` + `governance/decision_record.py`
  (+ the `governance/__init__.py` package shell) — pure / FastAPI-free / LLM-free, added to the
  `tests/apaa/test_no_web_imports.py` guard's APAA-module set if that guard enumerates modules.

**Carry-forward action items (CLAUDE.md §9.1 / L1-E11 — each 6.x story cites its AI-E5-* item).**
- **AI-E5-1 (test-infra 🟠) — the COMPLETE-THE-DECLARED-SET keystone-adequacy checklist.** Applied to 6.7:
  enumerate the FULL declared set of HITL members — (1) pattern-matched firing + default-STOP; (2)
  time-boxed park-at-STOP (never auto-PROCEED); (3) append-only prev-hash-chained decision record; (4) STOP
  logged even if the record is deferred — and demonstrate EACH covered (RED-first: the default-STOP, the
  timeout-never-PROCEED, and the append-only-not-overwrite legs are the traps a naive gate falls into). The
  enumeration is explicit in the gate/record modules + the test module.
- **AI-E5-2 (test-infra 🟠) — MECHANIZE the fixture-shape coverage.** The escalation-resolution matrix
  (fired × human-decision-present × timeout-elapsed → outcome) is tested as a MECHANIZED parametrized table
  (no hand-copied per-case bodies), and the append-only chain is verified by reading it back through the
  existing reader (mechanized, not a prose promise).
- **AI-E4-2 (test-infra) — no-crash input shapes.** The gate handles empty/None findings, an empty ledger,
  a missing prior decision (genesis), and a malformed decider-id without crashing — degrading to a
  deterministic STOP or a typed, NAMED error (never a bare traceback); a NAMED assertion cites the case.
- **AI-E1-1 (test-infra 🟢) — non-ASCII / locale discipline (the Epic-1-FAIL class, standing).** A decision
  with a non-ASCII decider-id / reason token serializes byte-identically under `PYTHONIOENCODING=utf-8`
  (the single serializer is `ensure_ascii=False`) and round-trips through the reader.
- **AI-E5-4 (governance 🟢) — central defer register.** If 6.7 surfaces a follow-up (e.g. the live pipeline
  wiring, the CLI decision flag, an LLM-driven escalation seam, a notification transport, or a known
  limitation it does NOT close), file it append-only in
  `_bmad-output/design-artifacts/APAA/deferred-work.md` with the six CC-3 fields (`target_story` e.g.
  `epic-7-minions-dogfood-proof-run` for the live-run wiring, or an `epic-7-...` / future-epic key).
- **AI-E5-7 (process 🟢) — keep the structural gates green + partial-reuse docstring precision.** Both
  modules keep the no-web-imports gate, the single-serializer AST gate, and the file-size gate green (pure,
  reuse the EXISTING canonical serializer + envelope + writer, add NO new `json.dumps`/hasher/parse, import
  NO `fastapi/uvicorn/starlette` and NO LLM dispatch). Where reuse is PARTIAL (REUSE the writer + envelope
  + serializer + reader + reserved `decisions/` subdir + the frozen findings; ADD the pure gate + the
  append-only record wiring), narrate it precisely.
- **AI-E5-3 (process 🟠) — committed pre-`review` test-existence guard.** The gate module + the record
  module + the schema types + the HITL tests EXIST + pass before the `review` flip.
- **NFR-S1 secret-containment (standing CI-blocking moat).** A decision record NEVER carries source/secret
  bytes — only the decision, the pattern-matched trigger provenance, the finding-id/locator provenance, the
  decider-id token, and the deterministic decision-id. If a NEW write path (`.apaa/decisions/`) is exercised
  by the containment suite, EXTEND `tests/security/test_apaa_secret_containment.py` (the 4.4 randomized-canary
  suite) to sweep the decisions subdir (do NOT fork).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 6.7) + the PRD (FR23 HITL STOP/PROCEED, default-STOP,
> time-boxed park-at-STOP; FR24 append-only decision record, log STOP even if deferred) + the architecture
> (AR4 fixed-precision-no-float / no-clock / no-uuid / content-derived ids; AR7 reuse-by-import; AR8
> pure/impure separation; AR10 typed-failure-never-raise; AR11 content-addressed filenames; NFR-A1
> prev-hash-chained envelope; NFR-S1 no source/secret bytes; NFR-S5 containment). Drivers: **APAA-FR-23**
> (HITL STOP/PROCEED gate, pattern-matched, default-STOP, time-boxed park-at-STOP), **APAA-FR-24**
> (append-only decision record; log the STOP even if the record is deferred — Tier B), **APAA-NFR-A1**
> (schema-versioned, content-hashed, prev-hash-chained, additive-only envelope — the append-only chain),
> **APAA-NFR-D1/D2** (the escalation gate is deterministic + zero-LLM-token — a pure fold), **APAA-NFR-S1**
> (no source/secret bytes in the decision record / any read surface), **APAA-NFR-S5** (containment via the
> reused writer), **APAA-AR4** (content-derived ids; no clock/uuid/random/float in the payload),
> **APAA-NFR-M1/M2** (≤1200-line files; frozen contracts + additive-only).
>
> **SCOPE FENCE — Tier-B, single-purpose, the HITL escalation gate + the append-only decision record.**
> This story delivers ONLY: (1) the PURE pattern-matched escalation gate
> (`minions_core/apaa/governance/escalation.py`) — fires on a deterministic rule match, defaults to STOP,
> parks at STOP on timeout (never auto-PROCEED), zero-LLM-token; (2) the PURE escalation-outcome +
> decision-record schema types; (3) the append-only decision-record writer
> (`minions_core/apaa/governance/decision_record.py`) that appends each decision to `.apaa/decisions/`
> reusing the 1.1 serializer + the content-hashed prev-hash-chained envelope + the 1.3 `ApaaStoreWriter`
> (no forked persistence), and logs the STOP even if the full record is deferred; (4) the `governance/`
> package shell; (5) the HITL test module (`tests/apaa/test_hitl_escalation.py`) + any needed extension of
> the 4.4 secret-containment suite for the `decisions/` write path; (6) any NEW defer filed with the six
> CC-3 fields. It does NOT build, and MUST NOT pull forward: an **LLM-driven escalation adjudicator** (V1 is
> pattern-matched — forbidden by the FR23 lock); a **live async/blocking human wait / notification /
> webhook / queue**; the **Minions dogfood run / budget sizing** (Epic 7); a **new detector or any change to
> a 6.1–6.6 detector / the Prosecutor / any frozen Epic-1..6 contract**; a **new `.github/workflows` CI
> job**; a **new HTTP route / FastAPI surface / UI** (§3.7); a **new `cli.py` flag** (a minimal invocation
> seam only if the AC proof requires it, recorded in the Change Log).

**AC1 — A PURE pattern-matched escalation gate fires on a rule match and DEFAULTS TO STOP (FR23 / NFR-D2 / AR8)**
**Given** a configured escalation condition (a deterministic rule match over the findings / coverage ledger /
candidate verdict-state — e.g. a configured rule-id, a finding-shape, or a verdict-state pattern) and NO
human decision present
**When** `minions_core/apaa/governance/escalation.py` evaluates the gate
**Then** the escalation FIRES on the pattern match (a PURE, zero-LLM-token function — no I/O, no clock, no
LLM, no random — AR8; it imports NO `fastapi/uvicorn/starlette` and NO LLM dispatch surface, so the
no-web-imports / no-LLM gates stay green) and, absent a human decision, resolves to **STOP** — the
default-STOP fail-CLOSED outcome, RED-first against a gate that defaults to PROCEED or reaches for an LLM to
decide (FR23: "defaulting to STOP", "R1 pattern-matched, not LLM-judgment").

**AC2 — On gate-timeout with no human response, the gate PARKS AT STOP and NEVER auto-PROCEEDs (FR23 — the keystone)**
**Given** a fired escalation with a configured gate-timeout window and no human decision
**When** the timeout window has elapsed
**Then** the gate resolves to **STOP (parked)** with resolution kind `timeout_parked_stop` — it NEVER
auto-PROCEEDs (the time-boxed-gate fail-CLOSED default); this is verified RED-first against a gate that
fails open (auto-PROCEEDs) on timeout, which would be the exact FR23 violation.

**AC3 — A human STOP/PROCEED decision is recorded in an APPEND-ONLY, prev-hash-chained `.apaa/decisions/` record (FR24 / NFR-A1 / AR7 reuse)**
**Given** a fired escalation and a supplied human decision (STOP or PROCEED) with a decider-id token
**When** `minions_core/apaa/governance/decision_record.py` records it
**Then** it appends a NEW content-addressed artifact under `.apaa/decisions/` (filename from the envelope
`content_hash`, AR11) whose envelope `prev_hash` chains to the prior decision's `content_hash` (genesis
sentinel `"0"*64` for the first), by REUSING `ApaaStoreWriter.write_payload(subdir="decisions", ...)` +
`EnvelopeWriter.build` + the 1.1 canonical serializer (the bytes are EXACTLY `canonical.dumps_bytes(...)`
— NO second `json.dumps`, NO forked envelope/writer/containment — §3.3/AR7); a SECOND decision appends a
NEW artifact whose `prev_hash` = the first's `content_hash` (append-only — the prior decision is NEVER
mutated / overwritten / deleted, mirroring the §3.4 evidence-immutability + hash-chained-ledger discipline),
verified by reading the chain back through the EXISTING `ApaaStoreReader` (which re-verifies `content_hash`
→ `StoreIntegrityError` on tamper).

**AC4 — The STOP is logged even if the full decision record is deferred (FR24)**
**Given** an escalation that fires but whose full human decision is NOT yet available (deferred / the human
has not responded / the full-record write is deferred)
**When** the escalation is processed
**Then** the STOP itself is logged (a STOP decision record — or a minimal STOP log entry — is still
appended to `.apaa/decisions/` with resolution kind `default_stop` / `timeout_parked_stop`), so the audit
trail never loses the fact that a STOP occurred — RED-first against an implementation that records nothing
until the human responds (which would lose the escalation fact on a deferred/abandoned decision) (FR24:
"log the STOP even if the record is deferred").

**AC5 — The decision record carries NO source/secret bytes and NO absolute host path (NFR-S1 / AR4)**
**Given** an escalation triggered by a finding on a secret-bearing / source-bearing file (a
`hardcoded_secret` / `secret_canary` cartridge-shaped input)
**When** the decision record is serialized
**Then** it carries ONLY the decision (STOP/PROCEED), the pattern-matched trigger provenance (rule-id /
reason token), the triggering finding-id(s) / locator provenance, the decider-id token, the resolution kind,
and a deterministic content-derived decision-id — NEVER a secret value, source bytes, or an absolute host
path (the returned locator is `.apaa/`-root-relative POSIX, inherited from the writer); ALL ids are
content-derived (NO `uuid4` / clock / counter / `os.getpid` / random — AR4/AR11), and NO float appears in
the payload (the 1.1 serializer rejects float). These audits flow through the EXISTING 4.4 randomized-canary
suite (`tests/security/test_apaa_secret_containment.py`), EXTENDED to sweep the `.apaa/decisions/` write path
if it is a newly-exercised path (do NOT fork).

**AC6 — Determinism + append-only integrity + non-ASCII hold over the HITL surface (NFR-D1/D2 / NFR-P1 / NFR-A1 / AI-E1-1)**
**Given** a fixed escalation input + a fixed sequence of decisions
**When** the gate + record are run twice
**Then** (a) the escalation resolution is deterministic + ZERO-LLM-token (NFR-D2 — a pure fold, no LLM
dispatch); (b) the decision-record bytes + the `content_hash` chain are byte-reproducible across two runs
over the same inputs (NFR-P1 — content-derived ids, no clock/uuid/float in the hashed payload; the
volatile `run_id`/`created_at` are envelope-only and excluded from the hash per NFR-D3); (c) the append-only
chain's `prev_hash` links resolve correctly and the reader re-verifies each `content_hash` (NFR-A1 —
tamper-evident, ordered append); (d) a decision with a NON-ASCII decider-id / reason token serializes
byte-identically under `PYTHONIOENCODING=utf-8` (the single serializer is `ensure_ascii=False`) and
round-trips through the reader (AI-E1-1).

**AC7 — Complete-the-declared-set over the HITL members, each RED-first where applicable (AI-E5-1 / AR10)**
**Given** the full DECLARED set of HITL members
**When** the gate + record + tests are built
**Then** EACH member is explicitly covered: (1) pattern-matched firing + default-STOP (AC1 — RED-first
against default-PROCEED / an LLM trigger); (2) time-boxed park-at-STOP (AC2 — RED-first against
auto-PROCEED on timeout); (3) append-only prev-hash-chained decision record (AC3 — RED-first against an
overwrite / a forked writer); (4) STOP-logged-even-if-deferred (AC4 — RED-first against record-nothing-until-
human); AND the enumeration is EXPLICIT in the gate/record modules + the test module (the
complete-the-declared-set discipline). The modules never raise opaquely: empty/None findings, an empty
ledger, a missing prior decision (genesis), a malformed decider-id → a deterministic STOP or a typed, NAMED
error (a `ValueError` subclass mirroring `WorkspaceContainmentError` / `StoreIntegrityError`), never a bare
traceback (AR10 / the AI-E5-1 no-crash leg; a NAMED assertion cites the case).

**AC8 — No regression / no scope creep; structural gates green; ≤1200 lines; the pre-`review` test-existence precondition (AI-E5-7 / AI-E5-3 / NFR-M1/M2)**
**Given** the new `governance/escalation.py` + `governance/decision_record.py` (+ the `governance/__init__.py`
shell) + the schema types + the HITL tests
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the prior green baseline + the new 6.7 HITL tests), the no-web-imports gate (extended to include the
new `governance/` modules if it enumerates modules), the single-serializer AST gate, and the file-size gate
stay green; `mypy` is clean on any new/modified modules
**And** NO production-tree behavior changes to the frozen surfaces (the gate/record COMPOSE the existing
`store/*` writer/envelope/serializer/reader + the frozen `Recording`/`CoverageLedger`/`AuditVerdict`; NO new
detector, NO detector/Prosecutor edit, NO frozen-contract diff — `store/*` / `ledger/*` / `verdict/*` /
`detectors/*` / `cache/*` / `pipeline.py` / `models.py` / `tests/apaa/cartridges/_registry.py` show NO
behavior-changing diff), NO new `json.dumps`/hasher/containment/writer forked, NO `cli.py` flag (a minimal
invocation seam ONLY if the AC proof requires it, recorded in the Change Log), NO HTTP route, NO new CI job,
NO live LLM call
**And** each new/modified file is ≤1200 lines (NFR-M1 — split the pure gate resolution from the schema types,
or the record writer from the chain-read verifier, if either approaches the limit; measure first); the new
files cite their `APAA-FR-23` / `APAA-FR-24` / `APAA-NFR-A1` / `APAA-NFR-D2` / `APAA-NFR-S1` / `APAA-AR4`
drivers in the module docstring + the locked test area / index; the mandatory artifacts (the gate + the
record + the schema types + the new tests) EXIST + pass + any new defer is filed BEFORE the story flips to
`status: review` (AI-E5-3 / AI-E2-1 test-existence discipline). **Test area `APAA-HITL`**
(`TC-APAA-HITL-001-NN`, start at index 01; lock the area + index in the module docstring).

## Tasks / Subtasks

- [x] **Task 0 — Re-read the REAL surfaces; LOCK the escalation-resolution matrix (DN-RESOLUTION), the decision-record schema (DN-SCHEMA), the writer/envelope reuse, the FR23/FR24 fail-safe locks, and the declared member set** (AC: 1, 2, 3, 4, 7)
  - [x] Re-read `minions_core/apaa/store/writer.py` (`ApaaStoreWriter.write_payload(subdir, payload, *,
        schema_version, producer, prev_hash=...)` → `<subdir>/<content_hash>.json` + the returned
        root-relative locator) + `store/envelope.py` (`EnvelopeWriter.build`, `GENESIS_PREV_HASH = "0"*64`,
        content-hash-over-payload-only, `prev_hash` chaining) + `store/paths.py` (`APAA_SUBDIRS` already
        reserves `decisions/`; containment) + `store/reader.py` (`ApaaStoreReader.read_envelope` re-verifies
        `content_hash` → `StoreIntegrityError`). LOCK: the record REUSES `write_payload(subdir="decisions")`
        + the prev-hash chain — NO forked persistence.
  - [x] Re-read `minions_core/apaa/verdict/prosecutor.py` (the PURE zero-token recording-consumer pattern +
        the typed `ProsecutorError` / degrade-never-raise discipline) + `ledger/recording.py`
        (`Recording` fields: `rule_id`, `advisory`, `depth_supported`, `locators` ≥1, `recording_id`). LOCK:
        the escalation gate is the SAME pure-consumer shape; the trigger is PATTERN-MATCHED over these frozen
        fields, NEVER an LLM call, NEVER over source bytes.
  - [x] Re-read the FR23/FR24 ACs in `epics.md` (Story 6.7) + the PRD FR23/FR24. LOCK the fail-safe defaults:
        default-STOP; timeout parks-at-STOP (never auto-PROCEED); STOP logged even if the record is deferred;
        append-only (no mutate/overwrite).
  - [x] Enumerate + LOCK the DECLARED HITL member set (AC7 (1)–(4)) + DN-RESOLUTION (the fired ×
        human-decision × timeout → outcome matrix) + DN-SCHEMA + the append-only chain rule + the OI-free
        secret-containment constraint. Record the locked rules + the fail-safe rationale in Dev Notes.
- [x] **Task 1 — Create the `governance/` package + the PURE escalation-outcome + decision-record schema types (designed frozen/additive)** (AC: 1, 2, 5)
  - [x] `minions_core/apaa/governance/__init__.py` (package shell, no logic) + the PURE frozen types: the
        escalation outcome (`STOP`/`PROCEED` closed enum), the resolution kind
        (`default_stop`/`timeout_parked_stop`/`human_decision`), and the decision-record payload
        (decision + trigger provenance (rule-id/reason) + triggering finding-id(s)/locator provenance +
        decider-id token + resolution kind + a deterministic content-derived decision-id). PURE (no I/O /
        clock / LLM / random — AR8); NO float; content-derived ids (AR4/AR11); `frozen=True, extra="forbid"`
        (the 1.1 envelope precedent, additive-only NFR-M2).
- [x] **Task 2 — Build the PURE pattern-matched escalation gate (default-STOP + time-boxed park-at-STOP)** (AC: 1, 2, 7)
  - [x] `minions_core/apaa/governance/escalation.py`: a PURE function that takes the escalation condition (a
        deterministic rule match over findings/ledger/verdict-state), an optional human decision, and a
        timeout-elapsed flag → resolves the outcome per DN-RESOLUTION: fired + no decision → STOP
        (`default_stop`); fired + timeout-elapsed + no decision → STOP (`timeout_parked_stop`, NEVER PROCEED);
        fired + human decision → that decision (`human_decision`). Imports NO `fastapi/uvicorn/starlette`, NO
        `providers.*`, NO LLM dispatch. Degrades (empty/None findings, empty ledger) to a deterministic STOP;
        a genuinely malformed argument → a typed NAMED error (never a bare raise — AR10).
- [x] **Task 3 — Build the append-only decision-record writer (REUSE the writer/envelope/serializer)** (AC: 3, 4, 5)
  - [x] `minions_core/apaa/governance/decision_record.py`: appends a decision to `.apaa/decisions/` via
        `ApaaStoreWriter.write_payload(subdir="decisions", payload=<record>, schema_version=..., producer=...,
        prev_hash=<prior content_hash or GENESIS_PREV_HASH>)` → returns the root-relative locator. The
        prev-hash chain is the append-only ordering (a helper to resolve the current chain head from the
        prior write). NO forked serializer/envelope/writer/containment. The STOP is logged even when the full
        human decision is deferred (a `default_stop`/`timeout_parked_stop` record is still appended — AC4).
  - [x] If either module approaches 1200 lines, split by responsibility (measure first — no speculative split).
- [x] **Task 4 — Build the parametrized HITL test harness (the resolution matrix + the append-only chain)** (AC: 1, 2, 3, 4, 6, 7)
  - [x] `tests/apaa/test_hitl_escalation.py` (area `APAA-HITL`, `TC-APAA-HITL-001-NN` from index 01): a
        MECHANIZED parametrized resolution matrix (fired × human-decision-present × timeout-elapsed → expected
        outcome) asserting default-STOP (AC1, RED-first vs default-PROCEED / LLM trigger), timeout-parked-STOP
        (AC2, RED-first vs auto-PROCEED), append-only prev-hash chain (AC3 — write two decisions, read the
        chain back through `ApaaStoreReader`, assert `prev_hash` links + the prior record is unmutated),
        STOP-logged-even-if-deferred (AC4, RED-first vs record-nothing), and the determinism + non-ASCII +
        tamper-evidence properties (AC6). Each assertion failure NAMES the case (the AI-E5-1 no-crash leg).
- [x] **Task 5 — Secret-containment over the decisions write path (extend the 4.4 suite only if needed)** (AC: 5)
  - [x] Assert the decision record carries NO planted secret / canary / source byte / absolute host path —
        only counts / provenance tokens / the decider-id / the content-derived id. If the `.apaa/decisions/`
        write path is a newly-exercised path, EXTEND `tests/security/test_apaa_secret_containment.py` (the 4.4
        randomized-canary suite) to sweep it (do not fork).
- [x] **Task 6 — Run + mypy + gates + any NEW defer + the pre-`review` precondition** (AC: 8)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
        all pass (prior baseline + the new 6.7 HITL tests). `mypy` clean on any new modules.
  - [x] Confirm NO behavior-changing diff to the frozen Epic-1..6 production surfaces (use mtime — the APAA
        prod tree is currently untracked, so `git diff` is empty/N-A; the new `governance/` modules are the
        only added production files). Confirm the no-web-imports gate (extended to include the new
        `governance/` modules if it enumerates modules), single-serializer, and file-size gates green. NO
        `cli.py`/HTTP/CI-job change; NO new detector/Prosecutor edit; NO live LLM.
  - [x] **AI-E5-4:** file any follow-up (live pipeline wiring, the CLI `--decision` flag, an LLM-driven
        escalation seam, a notification transport, or a known limitation) append-only in
        `_bmad-output/design-artifacts/APAA/deferred-work.md` with the six CC-3 fields (`target_story` e.g.
        `epic-7-minions-dogfood-proof-run` or a future-epic key).
  - [x] **AI-E5-3 / AI-E2-1 GATE:** the mandatory artifacts (the gate + the record + the schema types + the
        new tests) EXIST + pass BEFORE the `review` flip; the Dev Agent Record is filled completely (no blank
        placeholders), incl. the locked DN-RESOLUTION matrix / DN-SCHEMA / the append-only chain decision /
        the FR23/FR24 fail-safe confirmations.

### Review Findings

_Code-review iteration 1 (2026-07-01) filed the blocking `[Review][Patch]` below. Fix iteration 1
resolved it; **code-review iteration 2 (2026-07-02) independently verified the fix and closed it** —
the item is checked off, no unresolved findings remain, `review → done`._

- [x] [Review][Patch] Append-only violated for identical resolutions — content-addressed
  filename collision overwrites the prior decision + corrupts the prev-hash chain
  [minions_core/apaa/governance/decision_record.py:125]. Two identical `EscalationResolution`
  payloads (e.g. re-logging the same deferred `default_stop` STOP — the exact AC4 case, or two
  audit runs of the same repo) hash to the same `content_hash` → same `decisions/<hash>.json`
  → the second `append()` OVERWRITES the first (AC3 "prior NEVER overwritten" broken) and
  yields a self-cyclic `prev_hash` so `_resolve_chain_head()` returns genesis, orphaning the
  whole chain (independently reproduced: 3 appends → 2 files, a 2-cycle, head resets to
  genesis). Fix: fold the chain position (`prev_hash` or a monotonic append-index) into the
  HASHED decision payload so each link is a distinct artifact, OR reject a duplicate filename
  with a typed `DecisionRecordError` instead of silently overwriting. Add a RED-first test:
  two identical resolutions → 2 files + an intact genesis-rooted (non-cyclic) chain.
  **RESOLVED (fix iteration 1, 2026-07-01) — reviewer's PREFERRED "fold the chain position into
  the hashed payload" approach.** `DecisionRecordWriter.append()` now folds the resolved
  `prev_hash` (the prior decision's `content_hash`, genesis sentinel at the head) INTO the
  persisted, hashed payload under a new `chain_prev_hash` key (`CHAIN_PREV_HASH_KEY`). Because
  the envelope `content_hash` (and thus the `decisions/<content_hash>.json` filename) covers the
  payload, each chain link is now a genuinely DISTINCT content-addressed artifact even for
  byte-identical resolutions — no filename collision, no overwrite, no self-cycle, no
  genesis-orphan. The value is a 64-hex content-hash / genesis token (provenance only, NEVER
  source/secret bytes — NFR-S1). NO fork of the 1.1 serializer / envelope / 1.3 writer/reader;
  NO UPDATE/DELETE path added; the envelope `prev_hash` (the read-side chain) is unchanged.
  RED-first regression `test_identical_resolutions_append_two_distinct_files_and_intact_chain`
  (TC-APAA-HITL-001-31) reproduces the reviewer's scenario (append A → B (chains A) → A' identical
  to A) and asserts 3 distinct files + an ordered genesis-rooted NON-cyclic chain (`A'.prev = B`).
  It fails RED on the old code (2 files) and passes green with the fix.
  **VERIFIED CLOSED (code-review iteration 2, 2026-07-02).** The reviewer independently reproduced
  the fix: (a) the fold of `chain_prev_hash` into the hashed payload is present at
  `decision_record.py:190`; (b) the regression test is genuinely RED on the old code (reviewer
  reverted the fold in a scratch copy → 2 files, `assert 2 == 3` fails) and green on the new
  (3 distinct files); (c) three fresh adversarial probes — the FIRST TWO byte-identical appends
  (the head-genesis edge), THREE identical in a row, and interleaved identical/different — all
  yield distinct content-addressed files with an ordered, genesis-rooted, NON-cyclic chain whose
  head never resets to genesis after the head. No residual collision path exists (append is
  synchronous, so each identical re-log resolves a distinct tail as its `chain_prev_hash`). This
  finding is fully resolved.

## Dev Notes

### Architecture / contract anchors (re-read before coding)
- **Persistence — REUSE, do not fork:** `minions_core/apaa/store/writer.py::ApaaStoreWriter.write_payload(
  subdir, payload, *, schema_version, producer, prev_hash=...)` (→ `<subdir>/<content_hash>.json`, returns
  the root-relative locator) + `store/envelope.py::EnvelopeWriter.build` (`GENESIS_PREV_HASH = "0"*64`,
  content-hash over the payload ONLY, `prev_hash` chaining) + `store/canonical.py` (THE serializer — no float,
  Decimal/Fraction only) + `store/paths.py` (`APAA_SUBDIRS` already reserves `decisions/`; containment
  inherited) + `store/reader.py::ApaaStoreReader.read_envelope` (re-verifies `content_hash` →
  `StoreIntegrityError`). The record COMPOSES these; it authors NO second serializer/envelope/writer/
  containment.
- **Pure-consumer precedent — MIRROR:** `minions_core/apaa/verdict/prosecutor.py` (a PURE, zero-token,
  deterministic recording-consumer; typed error only on a genuinely malformed arg; degrade-never-raise on
  empty/None). The escalation gate is the SAME shape. The trigger is PATTERN-MATCHED over the frozen
  `Recording` fields (`rule_id`/`advisory`/`depth_supported`/`locators`) — NEVER an LLM call (FR23 lock),
  NEVER over source bytes (NFR-S1).
- **Finding contract:** `minions_core/apaa/ledger/recording.py::Recording` (`rule_id`, `advisory`,
  `depth_supported`, `locators` ≥1 = FR13, `recording_id`) + `Locator`. The record cites finding-id / locator
  provenance ONLY — never bytes.
- **No-float / content-derived ids — AR4 (the byte-diff landmine):** the decision-id is content-derived
  (NO `uuid4`/clock/counter/`os.getpid`/random); NO float in the payload (the 1.1 serializer rejects float);
  the envelope's volatile `run_id`/`created_at` are excluded from the hash (NFR-D3).
- **Secret-containment suite (EXTEND, do not fork):** `tests/security/test_apaa_secret_containment.py` (4.4)
  — sweep the `.apaa/decisions/` write path if newly exercised.
- **Structural gates:** `tests/apaa/test_no_web_imports.py` (no-web-imports — ADD the new `governance/`
  modules to its APAA-module set if it enumerates modules), the single-serializer AST gate, the file-size gate.

### Locked decisions (resolve in dev; recorded here per §3.4)
- **DN-RESOLUTION (the FR23 fail-safe matrix — the keystone).** The gate resolves
  `(fired, human_decision, timeout_elapsed)` deterministically:
  - fired + no decision + not-timed-out → **STOP** (`default_stop`) — silence blocks.
  - fired + no decision + timeout-elapsed → **STOP** (`timeout_parked_stop`) — NEVER auto-PROCEED.
  - fired + human decision (STOP/PROCEED) → **that decision** (`human_decision`).
  - not fired → not escalated (pass-through; no record required).
  The trigger is a PATTERN MATCH (deterministic rule over findings/ledger/verdict-state), NOT an LLM
  judgment. There is NO LLM dispatch anywhere in this story.
- **DN-SCHEMA.** A PURE frozen escalation-outcome + decision-record type: outcome (`STOP`/`PROCEED` closed
  enum) + resolution kind (`default_stop`/`timeout_parked_stop`/`human_decision`) + trigger provenance
  (rule-id/reason token) + triggering finding-id(s)/locator provenance + decider-id token (None for a
  default/timeout STOP) + a deterministic content-derived decision-id. PURE (no I/O/clock/LLM/random — AR8);
  no float; `frozen=True, extra="forbid"` (additive-only, NFR-M2).
- **DN-APPEND-ONLY.** Each decision is a NEW content-addressed `.apaa/decisions/<content_hash>.json` whose
  envelope `prev_hash` chains to the prior decision's `content_hash` (genesis `"0"*64` at the head). NO
  in-place update / delete of a prior decision (§3.4 evidence-immutability + hash-chained-ledger discipline).
  The chain is verified by reading it back through the EXISTING `ApaaStoreReader` (`content_hash` re-verify).
- **DN-STOP-LOGGED-DEFERRED (FR24).** The STOP is logged even when the full human decision is deferred: a
  `default_stop` / `timeout_parked_stop` record is STILL appended at escalation time (the audit trail never
  loses the STOP fact). A later human decision is a SUBSEQUENT append (append-only, not a mutation of the STOP
  record).
- **DN-NO-PROD-CHANGE-FROZEN.** 6.7 adds a NEW `governance/` sub-package (`escalation.py` +
  `decision_record.py` + `__init__.py`) + a test module. It adds NO detector, edits NO detector/Prosecutor/
  frozen contract, forks NO serializer/envelope/writer/containment, adds NO `.apaa/` subdir (`decisions/`
  already exists in `APAA_SUBDIRS`). If a live pipeline/CLI wiring is needed only to prove an AC, add the
  MINIMAL seam and record it in the Change Log; otherwise it is an AI-E5-4 defer to Epic 7.
- **DN-NO-LLM (the FR23 lock).** V1 escalation is PATTERN-MATCHED, deterministic, zero-token. An LLM-driven
  escalation adjudicator is a documented FORWARD seam (behind the 6.1 `LLMDispatchPort`, `FakeDispatch` for
  zero-token tests) — NEVER a direct `minions_core.providers` import, NEVER the V1 default. Both new modules
  import NO providers and NO FastAPI (the no-web-imports + no-LLM gates stay green).

### FR23/FR24 fail-safe constraints (the central theme — do NOT soften)
- The trigger is a PATTERN MATCH (a deterministic rule), never LLM-judgment (FR23).
- The gate DEFAULTS TO STOP — silence never ships a verdict (FR23).
- On timeout with no response, the gate PARKS AT STOP — it NEVER auto-PROCEEDs (FR23, the keystone).
- The STOP is logged even if the full decision record is deferred (FR24).
- The decision record is APPEND-ONLY, prev-hash-chained, tamper-evident, and secret-free (FR24/NFR-A1/NFR-S1).

### Carry-forward action items addressed
- **AI-E5-1** — complete-the-declared-set over the HITL members (AC7), RED-first on default-STOP, the
  timeout-never-PROCEED, and the append-only-not-overwrite legs.
- **AI-E5-2** — MECHANIZE the resolution matrix as a parametrized table + the append-only chain verified by
  read-back (not a prose promise).
- **AI-E4-2** — empty/None findings, an empty ledger, a genesis (no prior) decision, a malformed decider-id
  handled without crashing; NAMED failures cite the case.
- **AI-E1-1** — a non-ASCII decider-id / reason token round-trips under `PYTHONIOENCODING=utf-8`.
- **AI-E5-3 / AI-E5-7** — pre-`review` test-existence + structural gates green + partial-reuse docstring
  precision.

### Previous-story intelligence (6.6 + the Epic-6 spine)
- 6.6 delivered the precision harness + validation protocol and left the ≥80% gate PROVISIONAL; it filed no
  blocker for 6.7 (the HITL surface was always Epic-6's last, explicitly-planned story).
- The `.apaa/decisions/` subdir is ALREADY reserved in `store/paths.py::APAA_SUBDIRS` (created by
  `ensure_tree`) — 6.7 writes into an existing subdir; it does NOT add a new tree branch.
- The whole APAA prod tree is currently UNTRACKED (the sub-tool is not yet git-committed), so `git diff` over
  the frozen surfaces will be empty/N-A — use mtime as the load-bearing no-change evidence, and keep the new
  `governance/` modules the only added production files.
- The FR23 "pattern-matched, not LLM-judgment" lock aligns with the whole Epic-6 determinism-quarantine: the
  V1 default path is PURE + zero-token (the 6.4 Prosecutor is the exact precedent). Do NOT introduce any LLM
  dispatch here.

## Dev Agent Record

### Context Reference

- Epic: `_bmad-output/design-artifacts/APAA/epics.md` — Epic 6 / Story 6.7 (FR23 + FR24).
- Predecessors (done): Stories 6.1–6.6 (Epic 6 spine); Epics 1–5 (the determinism/persistence/verdict spine).
- Reuse anchors: `store/writer.py`, `store/envelope.py`, `store/canonical.py`, `store/paths.py`,
  `store/reader.py`, `verdict/prosecutor.py`, `ledger/recording.py`.

### Agent Model Used

claude-opus-4-8[1m] (dev-story, implement mode), 2026-07-01.

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/test_apaa_secret_containment.py tests/test_import_paths.py` — baseline 1007 passed → **1045 passed** after 6.7 (+34 HITL, +2 secret-containment, +2 no-web-imports provider-free legs).
- `PYTHONIOENCODING=utf-8 python -m pytest tests/security/` — full security suite: 1 skipped (pre-existing), rest green.
- `PYTHONIOENCODING=utf-8 python -m mypy minions_core/apaa/governance/escalation.py governance/decision_record.py governance/__init__.py` — **Success: no issues found in 3 source files**.
- Structural gates (`test_canonical_single_serializer.py` + `test_no_web_imports.py`) green.
- Frozen Epic-1..6 surfaces mtime-verified unchanged (pipeline.py 06-29, models.py 06-24, prosecutor.py 06-29, orphan_code.py 06-29, store/writer.py 06-25, store/envelope.py 06-21) — only the new `governance/` files are dated 2026-07-01. The APAA prod tree is untracked so `git diff` is N-A; mtime is the load-bearing no-change evidence (as the story anticipated).

### Completion Notes List

- **DN-RESOLUTION (the FR23 fail-safe matrix) — implemented + proven.** `resolve_escalation(trigger, *, human_decision=None, timeout_elapsed=False)` resolves: human decision present → that decision (`human_decision`); no decision + timeout-elapsed → **STOP** (`timeout_parked_stop`); no decision + not-timed-out → **STOP** (`default_stop`). There is NO code path that resolves to PROCEED without an explicit human decision (proven mechanically by `test_no_resolution_path_proceeds_without_a_human_decision` + the parametrized `_RESOLUTION_MATRIX`). `escalation_fires(rule, *, findings, verdict)` is the PURE pattern-match: fires when a finding's `rule_id` ∈ `rule.match_rule_ids` OR the candidate verdict ∈ `rule.match_verdicts` — a deterministic rule, NEVER an LLM call (FR23 lock).
- **DN-SCHEMA — the frozen pure types.** `EscalationOutcome` (STOP/PROCEED closed enum), `ResolutionKind` (default_stop/timeout_parked_stop/human_decision), `EscalationRule` (the pattern), `EscalationTrigger` (rule-id + reason + finding-id(s) + `<file>:<start>-<end>` locator-provenance tokens — file/line only, never source bytes / ast_span), `HumanDecision` (outcome + opaque decider-id token), `EscalationResolution` (outcome + kind + trigger + decider-id + **content-derived** `decision_id`). All `frozen=True, extra="forbid"`; no float; content-derived id = `compute_content_hash(identity_payload)` (the single 1.1 hasher, NO uuid/clock/counter/random — AR4/AR11).
- **DN-APPEND-ONLY — REUSE, no fork.** `DecisionRecordWriter.append(resolution)` computes `prev_hash` by reading the current chain TAIL (the decision-record envelope whose `content_hash` is not any other decision's `prev_hash`; genesis `"0"*64` for the head) then delegates to `ApaaStoreWriter.write_payload(subdir="decisions", ..., prev_hash=...)` → `decisions/<content_hash>.json`. It authors NO second serializer/envelope/writer/containment. Chain-head resolution is **producer-scoped** (only `<64hex>.json` artifacts whose envelope `producer == "apaa.hitl.decision_record"`), so the 5.3 fixed-name `rejection_ledger.json` and any corrupt/foreign artifact are SKIPPED (never crash — AR10). Append-only proven: a prior decision's bytes are byte-identical after a later append; each decision is a distinct content-addressed file; the chain read-back through `ApaaStoreReader` links + tamper-guards.
- **DN-STOP-LOGGED-DEFERRED (FR24) — proven RED-first.** A `default_stop` / `timeout_parked_stop` resolution IS appended at escalation time (`test_stop_logged_even_when_deferred`), so the STOP is logged before/without any human decision; a later human decision is a SUBSEQUENT append (never a mutation of the STOP record).
- **DN-NO-LLM (the FR23 lock).** Both modules import NO `fastapi/uvicorn/starlette` and NO `minions_core.providers` / `apaa.audit` LLM surface. Added `escalation.py` (PURE) + `decision_record.py` (IMPURE FS shell) to `_MODULES_UNDER_GUARD` (no-web-imports) + two provider-free clean-subprocess legs (TC-APAA-HITL-001-20/-21). The escalation gate mirrors the 6.4 Prosecutor pure-consumer shape exactly.
- **NFR-S1 secret-containment — EXTENDED, not forked.** The `.apaa/decisions/` write path was already swept by the 4.4 suite (5.3 rejection records). Added TC-APAA-SECURITY-001-21/-22: a HITL decision record whose trigger cites a real `hardcoded_secret` finding over the `secret_canary` cartridge carries NO planted canary byte, and a planted raw secret in a `decisions/<64hex>.json` byte is CAUGHT by the same sweep (RED-then-green).
- **Complete-the-declared-set (AI-E5-1)** — all four HITL members covered RED-first: (1) pattern-match + default-STOP, (2) timeout-parks-at-STOP-never-PROCEED, (3) append-only prev-hash chain (never overwrite/fork), (4) STOP-logged-even-if-deferred. Mechanized resolution matrix (AI-E5-2). No-crash edges (AI-E4-2): empty/None findings, empty universe, malformed per-element finding skipped, genesis (no prior) decision, foreign/corrupt decisions artifact, malformed top-level arg → typed NAMED `EscalationError`/`DecisionRecordError`. Non-ASCII decider-id/reason round-trip byte-stable (AI-E1-1).
- **Scope fences honored (AI-E5-4 defer DF-6-7-A filed).** NO detector/Prosecutor/frozen-contract edit; NO `cli.py` flag / pipeline call site (the AC proof needed none — DN-NO-PROD-CHANGE-FROZEN); NO HTTP route / FastAPI / UI (§3.7); NO new CI job; NO live LLM; NO live async human-wait transport. The live pipeline/CLI wiring is DF-6-7-A → `epic-7-minions-dogfood-proof-run`.
- **File sizes (NFR-M1):** escalation.py 396, decision_record.py 216, __init__.py 24, test_hitl_escalation.py 574, test_apaa_secret_containment.py 791 — all ≤1200 (no split needed; measured, not speculative).
- **FIX ITERATION 1 (2026-07-01) — append-only content-address collision (the blocking `[Review][Patch]`).** ROOT CAUSE: the envelope `content_hash` (and the `decisions/<content_hash>.json` filename) covers the payload ONLY (NFR-D3), and the payload was `resolution.to_payload()` — which is chain-position-independent — so two byte-identical resolutions (the AC4 re-log-same-deferred-STOP case, or two audit runs of one repo) collided on one filename; the second `append()` overwrote the first, self-referenced its `prev_hash`, and `_resolve_chain_head()` returned genesis (orphaning the chain). FIX (reviewer's PREFERRED option): `append()` folds the resolved `prev_hash` into the persisted payload under `CHAIN_PREV_HASH_KEY = "chain_prev_hash"`, so each chain link is a genuinely distinct content-addressed artifact and the prev-hash spine stays intact + non-cyclic + reader-verifiable. The `EscalationResolution.to_payload()` 6-key resolution schema is UNCHANGED (the fold is at the RECORD layer, in the writer); the envelope `prev_hash` (the read-side chain) is unchanged; NO fork of the 1.1 serializer/envelope/1.3 writer/reader; NO UPDATE/DELETE; secret-free (the folded value is a 64-hex content-hash / genesis token — NFR-S1, swept by the 4.4 suite). RED-first `test_identical_resolutions_append_two_distinct_files_and_intact_chain` (TC-APAA-HITL-001-31): RED on old code (2 files), green with fix (3 distinct files + ordered genesis-rooted non-cyclic chain). Full suite 1220 passed / 1 skipped / 4 subtests; mypy clean; files ≤1200. decision_record.py 216 → 253 lines.

### File List

New (production):
- `minions_core/apaa/governance/__init__.py`
- `minions_core/apaa/governance/escalation.py`
- `minions_core/apaa/governance/decision_record.py`

New (tests):
- `tests/apaa/test_hitl_escalation.py`

Extended (tests — not forked):
- `tests/apaa/test_no_web_imports.py` (+2 governance modules in `_MODULES_UNDER_GUARD`; +2 provider-free legs)
- `tests/security/test_apaa_secret_containment.py` (+HITL decision-record sweep TC-APAA-SECURITY-001-21/-22)

Governance evidence:
- `_bmad-output/design-artifacts/APAA/deferred-work.md` (DF-6-7-A appended, six CC-3 fields)
- `_bmad-output/design-artifacts/APAA/sprint-status.yaml` (6-7 → review)
- this story file (Dev Agent Record + Change Log + Status)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-07-01 | 0.1 | Story created (context-filled, ready-for-dev) — HITL STOP/PROCEED escalation (FR23) + append-only decision record (FR24); reuses the 1.1 serializer + content-hashed prev-hash-chained envelope + 1.3 `ApaaStoreWriter` + the reserved `.apaa/decisions/` subdir; PURE pattern-matched gate, default-STOP, timeout-parks-at-STOP, STOP-logged-even-if-deferred; zero-LLM-token. | Scrum Master (create-story) |
| 2026-07-01 | 1.1 | **Fix iteration 1 (dev-story, fix) — resolved the blocking `[Review][Patch]` append-only collision.** `DecisionRecordWriter.append()` now folds the resolved chain position (`prev_hash`) into the HASHED persisted payload under a new `chain_prev_hash` key (`CHAIN_PREV_HASH_KEY`, exported), so each chain link is a DISTINCT content-addressed `decisions/<content_hash>.json` even for byte-identical resolutions — the second re-log of an identical `default_stop` STOP (the AC4 case) no longer collides on / overwrites the prior file, no self-cyclic `prev_hash`, no genesis-orphan. Reviewer's PREFERRED "fold chain position in" approach (not the reject-duplicate alternative). REUSE preserved: no forked serializer/envelope/1.3 writer/reader; no UPDATE/DELETE; envelope `prev_hash` read-side chain unchanged; secret-free (the folded value is a 64-hex content-hash / genesis token — NFR-S1). Added RED-first `test_identical_resolutions_append_two_distinct_files_and_intact_chain` (TC-APAA-HITL-001-31): fails RED on old code (2 files / 2-cycle / genesis-reset), green with fix (3 distinct files, ordered genesis-rooted non-cyclic chain). Suite `tests/apaa/ tests/security/ tests/test_import_paths.py` = **1220 passed, 1 skipped (pre-existing), 4 subtests**; mypy clean on the 3 governance modules; decision_record.py 253 / escalation.py 396 / __init__.py 24 / test 621 lines (all ≤1200). Status → review. | Dev (claude-opus-4-8[1m]) |
| 2026-07-01 | 1.0 | Implemented (dev-story, implement). NEW `governance/` sub-package: PURE pattern-matched `escalation.py` (`escalation_fires`/`resolve_escalation` + frozen `EscalationRule`/`EscalationTrigger`/`HumanDecision`/`EscalationResolution` + `EscalationOutcome`/`ResolutionKind`; default-STOP, timeout-parks-at-STOP, content-derived decision-id via the 1.1 hasher, zero-LLM-token) + IMPURE `decision_record.py` (`DecisionRecordWriter.append` → append-only `decisions/<content_hash>.json`, prev-hash-chained, producer-scoped chain-head resolution, REUSES the 1.3 writer/reader/paths — no fork). STOP logged even when deferred (FR24). Extended the no-web-imports gate (+2 modules, +2 provider-free legs) + the 4.4 secret-containment suite (+HITL decision-record sweep, RED-then-green). Area APAA-HITL TC-APAA-HITL-001-01..30. Tests 1045 passed (was 1007); mypy clean; files ≤1200; frozen Epic-1..6 surfaces mtime-unchanged. DF-6-7-A (live pipeline/CLI wiring) filed with six CC-3 fields → `epic-7-minions-dogfood-proof-run`. Status → review. | Dev (claude-opus-4-8[1m]) |

## Senior Developer Review (AI)

**Reviewer:** code-review worker (claude-opus-4-8[1m]), 2026-07-01, iteration 1.
**Verdict: FAIL (concerns escalated to blocking).** Status returned to `in-progress`.

### Summary

The safety keystone is genuinely enforced and independently re-verified: the PURE
pattern-matched gate DEFAULTS TO STOP, PARKS AT STOP on timeout, and has NO code path
to PROCEED without an explicit `HumanDecision` (confirmed by tracing `resolve_escalation`
and the `(human=None) × timeout` matrix — every cell is STOP). The gate is zero-LLM-token
and provider-free (importing both modules loads zero `providers`/`fastapi`/`uvicorn`/
`starlette` modules). The decision record REUSES the 1.1 serializer + 1.3 writer/reader +
envelope prev-hash with no forked persistence. STOP-logged-even-if-deferred holds.
Secret-containment is genuinely extended (RED-then-green). Frozen Epic-1..6 surfaces are
untouched (only the new `governance/` files added). Full suite is green: `tests/apaa/ +
tests/security/ + tests/test_import_paths.py` = 1220 collected, exit 0, 1 skipped (34 HITL
pass, mypy clean, structural gates green).

**However, the FR24 append-only / hash-chained keystone (AC3) is BROKEN for the
identical-resolution case** — the exact case AC4 (re-log the same deferred STOP) invites.
Because the content-addressed filename derives from the envelope `content_hash` (a hash of
the PAYLOAD ONLY, which excludes `prev_hash`), two identical resolutions collapse to the
SAME `decisions/<hash>.json` file. The second `append()` **overwrites the prior record**
(AC3's "the prior decision is NEVER overwritten/mutated" is violated — its bytes change),
and produces a self-referential / cyclic `prev_hash` link that makes `_resolve_chain_head`
return the genesis sentinel — **orphaning the entire prior chain** so the next append
silently restarts from genesis. This is a data-integrity break in the headline FR24
property, so it is escalated to blocking.

### Independently reproduced (not trusting the Dev record)

Appending `default_stop` (A) → human `PROCEED` (B, chains to A) → the SAME `default_stop`
(A') yields **2 files, not 3** (the third STOP audit fact is lost); the surviving pair
forms a 2-cycle (`A.prev = B`, `B.prev = A`); `_resolve_chain_head()` returns `00000000…`
(genesis), so a fourth append starts a new, disconnected chain. The existing tests never
catch this because every test deliberately uses DISTINCT decider tokens to force distinct
payloads.

### ISSUES (unresolved — the next dev round must address)

- [Med] `minions_core/apaa/governance/decision_record.py:125-160` (`append`) — **AC3 /
  FR24 append-only violated for identical resolutions.** Two identical `EscalationResolution`
  payloads → identical `content_hash` → identical filename → the second `append()` overwrites
  the first and corrupts the prev-hash spine (self-cycle → genesis-orphan). Rule violated:
  FR24 "append-only, prior decision NEVER overwritten"; §3.4 hash-chained-ledger discipline.
  Suggested fix: make each appended record's identity include its chain position so
  re-logging the same logical STOP is a DISTINCT artifact — e.g. fold `prev_hash` (or a
  monotonic append-index) into the hashed decision payload so the content hash differs per
  chain link, OR reject a would-be duplicate filename (`FileExistsError`/typed
  `DecisionRecordError`) instead of silently overwriting. Add a RED-first test: append two
  IDENTICAL resolutions and assert 2 files + an intact genesis-rooted chain (no cycle, no
  head reset).

### Verified keystones (PASS)

(a) STOP-default / no-auto-PROCEED — PASS; (b) PURE + zero-LLM-token + no network — PASS;
(d) STOP-logged-even-if-deferred — PASS; (e) frozen surfaces unchanged — PASS; (f) headless
— PASS; defer DF-6-7-A six CC-3 fields — PASS; secret-containment RED-then-green — PASS;
tests green + mypy clean + ≤1200 lines — PASS. Only (c) append-only/hash-chain fails for the
identical-resolution case.

### Action Items

See `### Review Findings` under Tasks/Subtasks (the next dev round reads it).

---

**Reviewer:** code-review worker (claude-opus-4-8[1m]), 2026-07-02, iteration 2 (re-review after fix).
**Verdict: PASS.** Status flipped to `done`.

### Summary (iteration 2)

The single blocking finding from iteration 1 (append-only content-address collision on identical
resolutions) is genuinely and completely fixed. `DecisionRecordWriter.append()` folds the resolved
`prev_hash` into the hashed payload under `CHAIN_PREV_HASH_KEY = "chain_prev_hash"` (decision_record.py:190),
so each chain link is a distinct content-addressed artifact even for byte-identical resolutions. All
iteration-1 keystones are re-verified as non-regressed; the suite is genuinely green.

### Independently verified (not trusting the Dev record)

- **PRIMARY — the iteration-1 finding is fixed.** Reviewer reverted the fold in a scratch copy →
  the regression test fails RED (2 files, `assert 2 == 3`); with the fold, green. Three fresh
  adversarial probes (first-two-identical head-genesis edge; three-identical-in-a-row;
  interleaved identical/different) all produce distinct files + an ordered, genesis-rooted,
  non-cyclic chain, head never resets. The residual-path hypotheses in the review brief (two
  identical resolutions sharing the same prev_hash; the very first two appends both at genesis)
  are all closed — append is synchronous so each identical re-log resolves a distinct tail.
- **Keystone regression guard — all PASS.** escalation.py PURE / zero-LLM-token / DEFAULTS-TO-STOP
  / PARKS-AT-STOP on timeout / NO PROCEED without an explicit `HumanDecision` (mechanized matrix
  re-read, every no-human cell is STOP). escalation.py + `__init__.py` untouched since iteration 1
  (mtime 07-01; only decision_record.py changed, mtime 07-02 — matches the claim). No forked
  persistence, no UPDATE/DELETE, no LLM/web imports (grep clean — only docstring prose mentions).
- **Secret-free.** `chain_prev_hash` is a 64-hex content hash / genesis sentinel — provenance only.
  The 4.4 secret-containment suite sweeps `.apaa/decisions/` and has HITL-specific RED-first
  coverage (TC-APAA-SECURITY-001-21/-22) — a planted secret in a decision byte is caught.
- **Headless** — no HTTP route / FastAPI / UI. **File sizes** ≤1200 (escalation 396, decision_record
  253, __init__ 24, test 621).
- **Tests independently re-run.** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/
  tests/test_import_paths.py` → **1220 passed, 1 skipped, 4 subtests passed** (162.85s), matching the
  fix claim.

### Verdict rationale

No unresolved `decision-needed` or `patch` findings; no High/Medium issues; tests/lint green; all
ACs (AC1–AC8) met. The append-only/hash-chain data-integrity break that blocked iteration 1 is
closed with the reviewer's preferred approach and proven RED-first. PASS → `done`.
