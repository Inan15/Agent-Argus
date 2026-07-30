# Story 1.6: Pure-function verdict gate, finding ordering & exit-code mapping

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).

## Story

As an integrator,
I want a pure-function verdict gate that folds the coverage ledger + findings into a release-readiness
verdict, deterministically orders the findings by verdict impact, and maps the verdict to a process exit
code,
so that the release decision is reproducible, machine-consumable, and provably token-free — the SIXTH link
in the Epic-1 spine and the `C + A` half of the architecture's locked implementation sequence, consumed by
the CLI/pipeline (Story 1.7) that produces the signature 🔴 on the cartridge.

## Story Context

This is **Story 6 of Epic 1** (Signature-Demo Vertical Slice). It is the `C + A` half of the architecture's
locked implementation sequence — *"envelope + canonical serializer + fixed-enum ledger (C-core) → AST index
+ a single vacuous-path rule (B + D) → **pure-function verdict + exit code (C + A)** → 🔴 on the cartridge"*
(architecture §Decision Impact Analysis). Stories 1.1–1.3 delivered **C-core** (serializer + envelope +
fixed-enum ledger + frozen recording schema + `.apaa/` store shell); Story 1.4 delivered the **B** half
(repo intake + stack detection + tree-sitter AST index); Story 1.5 delivered the detector **D**
(heuristic vacuous-test detector + Tier-A vacuous-path AST subset, advisory-by-contract). **This story
delivers the verdict gate `C` + the exit-code mapping `A`** — the PURE function that folds the 1.2
`CoverageLedger` + the 1.5 `Recording` findings into a verdict, orders the findings by verdict impact
(FR33), and maps the verdict to a deterministic process exit code (FR18/AR3). **It computes a verdict but
runs no CLI and no pipeline** — the CLI invocation contract + the sequential pipeline that wires the whole
slice and produces the signature 🔴 on the vacuous-test cartridge is **Story 1.7** (the LAST Epic-1 story).

It builds directly on the five done stories of the spine:

- **Story 1.1 (done)** — the PURE determinism keystone (`store/canonical.py` single serializer:
  `dumps`/`dumps_bytes`/`loads` + `CanonicalSerializationError`; `store/envelope.py`: `Envelope`,
  `EnvelopeWriter.build`, `compute_content_hash`, `GENESIS_PREV_HASH`; `Decimal`/`Fraction` encoding frozen;
  `_MODULES_UNDER_GUARD` import-isolation gate seed + the `test_canonical_single_serializer.py` AST gate).
- **Story 1.2 (done)** — the PURE fixed-enum coverage ledger (`ledger/coverage_ledger.py`: `CoverageDepth`
  with EXACTLY five members `AUDITED_DEEP / AUDITED_SHALLOW / TOOL_SCANNED_ONLY / INFERRED / SKIPPED`;
  `CoverageLedgerEntry`; `CoverageLedger` with `build(...)`, `counts_by_depth() -> dict[CoverageDepth, int]`,
  `deep_count() -> int`, `total() -> int`; `grade_entry`) and the frozen recording schema
  (`ledger/recording.py`: `Locator`, `Recording`, `RecordingValidationError`, `RECORDING_SCHEMA_VERSION`).
  **`CoverageLedger` is THE ledger this gate folds; `Recording` is THE finding row this gate orders.**
  `Recording` already reserves `recording_id`/`finding_id`, `rule_id`, `cartridge_id`, `advisory: bool`,
  `locators` (≥1), `depth_supported: CoverageDepth | None`, `claim_present`, `coverage_envelope_slice`.
- **Story 1.3 (done)** — the IMPURE `.apaa/` write/read shell (`store/paths.py` `ApaaStorePaths` containment
  resolver; `store/writer.py`; `store/reader.py` + `StoreIntegrityError`). **This story does NOT write to
  `.apaa/` — it is PURE — but the verdict artifact it produces is the thing Story 1.7 will persist through
  this shell.**
- **Story 1.4 (done)** — the tree-sitter Python AST index (`index/ast_index.py`). Not directly imported by
  the verdict gate (the gate is downstream of the detectors); listed for spine completeness.
- **Story 1.5 (done)** — the heuristic vacuous-test detector + Tier-A vacuous-path AST subset
  (`detectors/base.py`: `Detector` Protocol, `FindingDraft`, `DegradedCondition`, `DetectorResult`,
  `build_recording`; `detectors/vacuous_test.py`). **This is the source of the `Recording` findings the
  verdict gate consumes** — and it LOCKED the advisory-by-contract eligibility surface this gate MUST
  honor (see "The advisory-by-contract moat" below).

**Why this is the determinism payoff (architecture Decision C / NFR-D2 / cross-cutting #1/#6).** The entire
determinism architecture exists so that the terminal stage — the verdict — is a **pure function of a
fixed-enum coverage ledger** (architecture §Project Context: *"one deterministic dataflow whose terminal
stage (the verdict) is a pure function of a fixed-enum coverage ledger"*). This story is where that payoff
is cashed: a function that imports ONLY the 1.2 ledger/finding models, reads NO file, calls NO `dispatch()`,
reads NO clock, and produces a verdict + ordered findings + exit code that is **byte-reproducible and
provably token-free** (NFR-D2: *"verdict gate + ledger mechanics are deterministic and testable with zero
LLM tokens"*). The verdict math is trivially pure; the work is getting the GATE THRESHOLDS, the
ADVISORY-BY-CONTRACT moat, the FINDING ORDERING, and the EXIT-CODE wire contract exactly right and frozen
for every downstream consumer (Story 1.7 CLI, Epic-3 degraded-verdict reuse, Epic-4 negative-assurance
wrapping, Epic-5 memoization, Epic-6 Prosecutor).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 1.6) and the architecture (Decision A §Execution & Invocation /
> exit-code wire contract, Decision C §Coverage Ledger/Recording/Verdict, §Contract/Format Patterns verdict
> vocabulary, §Pure/Impure Separation, AR3/AR4/AR8). Drivers: **APAA-FR-15** (release-readiness verdict as a
> PURE function of the coverage ledger), **APAA-FR-16** (gate+floor core: `RELEASE_READY` only when gates met
> — ≥60% deep + 0 blocking findings; `INSUFFICIENT_COVERAGE` below the 20% floor; never a default block),
> **APAA-FR-8-honored** (`inferred` evidence can never satisfy a gate — honored by the gate's coverage math),
> **APAA-FR-33** (order findings by verdict impact — verdict-blocking before non-blocking, alarm-fatigue
> defense), **APAA-FR-18** (deterministic exit code + machine-readable verdict artifact), **APAA-NFR-D2**
> (deterministic, zero-LLM-token verdict — a pure fold over recorded inputs), **APAA-NFR-D3** (content hash
> over the canonical payload only, excludes volatile fields — for the verdict artifact's reproducibility),
> **AR3** (exit-code wire contract `0`=RELEASE_READY / `2`=NOT_READY(BLOCKED) / `3`=INSUFFICIENT_COVERAGE /
> `1`=crash), **AR4** (single canonical serializer; ratios stored fixed-precision `Decimal`/`Fraction`, NEVER
> `float`; no clock/uuid/random/iteration-order in any `.apaa/`-bound output), **AR8** (pure/impure
> separation — the verdict gate is PURE: imports only ledger/finding models, no I/O, no `dispatch()`),
> **APAA-NFR-M1** (≤1200-line files), **APAA-NFR-M2** (frozen, additive-only Pydantic v2 contracts).
>
> **SCOPE FENCE.** This story delivers ONLY: `verdict/verdict_gate.py` (the PURE verdict function over the
> 1.2 `CoverageLedger` + the 1.5 `Recording` findings: gate evaluation, the deterministic finding ordering,
> the verdict + a frozen `AuditVerdict`-shaped result model carrying the ordered findings), and the
> exit-code mapping (`RELEASE_READY→0 · NOT_READY_FOR_RELEASE/BLOCKED→2 · INSUFFICIENT_COVERAGE→3 ·
> crash→1`). It does NOT build: the **CLI / pipeline wiring** + the cartridge run + the signature 🔴
> (`cli.py`/`pipeline.py`/`tests/apaa/cartridges/`, Story 1.7); the **critical-subsystem clause** of FR16
> (`RELEASE_READY` withheld when a designated critical subsystem is below deep — Story 2.3 completes that
> half; this story implements the ≥60%-deep + 0-blocking + 20%-floor core ONLY); the **`INSUFFICIENT_COVERAGE`
> floor under budget exhaustion** as a degradation BEHAVIOR (Epic-3 Story 3.3 reuses THIS gate over a partial
> ledger — the gate's floor LOGIC is delivered here, the budget-halt wiring is Epic 3); the **negative-assurance
> verdict semantics** — scope statement / materiality bar / disclaimer / point-in-time stamp (`verdict/
> negative_assurance.py`, Epic-4 Story 4.1; this story produces the verdict CONCEPT + vocabulary, NOT the
> negative-assurance wrapper); the **adversarial Prosecutor** + sign-off (`verdict/prosecutor.py`, Epic-6 —
> the second half of the "🔴 needs AST corroboration AND Prosecutor sign-off" rule); the **cache / memo
> store** (`cache/*`, Epic-5); the **LLM dispatch port / deep-audit** (`audit/*`, Epic-6). Build the verdict
> gate + ordering + exit-code mapping complete-and-contained, then stop.

**AC1 — Verdict is a PURE function: zero LLM tokens, no I/O, ledger/finding models only (FR15, NFR-D2, AR8)**
**Given** a `CoverageLedger` (1.2) + a tuple of `Recording` findings (1.5)
**When** the verdict gate function in `verdict/verdict_gate.py` runs
**Then** it computes the verdict as a **PURE function** — NO LLM/network call (zero tokens — NFR-D2), NO
filesystem I/O, NO `dispatch()`, NO clock read (`datetime.now`/`time.time`), NO `uuid4`/`os.getpid()`/
`random`, NO dict/`set`-iteration-order reliance — importing ONLY the 1.2 ledger/finding models (and the 1.1
serializer for any golden/hash test, not for the verdict math itself)
**And** the `verdict/` modules do NOT import `minions_core.api.* / services.api_app / app_factory /
api_server / providers.* / minions_core.apaa.audit.* / minions_core.apaa.store.writer` (the verdict gate is
the pure terminal fold — it never touches the impure write shell or the LLM seam); `verdict/verdict_gate.py`
is appended to `_MODULES_UNDER_GUARD` and the import-isolation gate stays green.

**AC2 — Gate evaluation: ≥60% deep + 0 blocking → RELEASE_READY; below 20% → INSUFFICIENT_COVERAGE (FR16)**
**Given** a coverage ledger
**When** the gate evaluates coverage thresholds
**Then** the gate computes the **deep-%** as `deep_count / total` using the 1.2 `CoverageLedger.deep_count()`
/ `total()` accessors, stored/compared as a **fixed-precision `Fraction`/`Decimal`, NEVER `float`** (the
NFR-P1 / AR4 byte-diff landmine — a `float` percentage field would explode at serialize time), and applies
the LOCKED thresholds:
- **`RELEASE_READY`** ⇔ deep-% **≥ 60%** AND **0 blocking findings** (see AC3 for "blocking").
- **`INSUFFICIENT_COVERAGE`** ⇔ deep-% **< 20%** — the not-assessed floor, returned EVEN IF blocking
  findings exist (the floor is *"low coverage is APAA's limitation to report, not the repo's failure to
  bear"* — a below-floor audit has not assessed enough to render a release verdict; **the dev locks +
  documents this floor-vs-blocking precedence and pins it with a test** — recommended: floor wins, because
  below-floor APAA cannot honestly claim it saw enough to block either; see Dev Notes).
- **`NOT_READY_FOR_RELEASE`** (BLOCKED) ⇔ deep-% **≥ 20%** AND (deep-% **< 60%** OR **≥1 blocking
  finding**) — i.e. enough coverage to render a verdict, but a gate is unmet.
**And** the verdict is **NEVER a default block**: a clean ledger with adequate coverage and no blocking
findings returns `RELEASE_READY`, and a below-20% ledger returns `INSUFFICIENT_COVERAGE` — there is no code
path that returns `NOT_READY_FOR_RELEASE` purely for absence of evidence (FR16 *"never a default block"*).
**And** the exact boundary semantics (`>= 60%` vs `> 60%`; `< 20%` vs `<= 20%`) are LOCKED and documented
(recommended: `RELEASE_READY` at deep-% **≥ 60%** inclusive; `INSUFFICIENT_COVERAGE` at deep-% **< 20%**
strict, so exactly-20% is assessable/blocking-eligible) and pinned by explicit boundary tests at 19.99% /
20% / 59.99% / 60%.

**AC3 — `inferred` (and `skipped`/`tool_scanned_only`) can never satisfy a coverage gate (FR8-honored, FR16)**
**Given** a ledger where some files' only evidence is `inferred` (narrative/doc), `skipped`, or
`tool_scanned_only`
**When** the gate computes the deep-% numerator
**Then** ONLY `audited_deep` entries count toward the ≥60% gate numerator — `inferred`, `skipped`,
`tool_scanned_only`, and `audited_shallow` entries are in the DENOMINATOR (`total`) but NEVER the numerator,
so `inferred` evidence can never inflate coverage toward `RELEASE_READY` (FR8 honored by the gate's math)
**And** a synthetic ledger that is e.g. 100% `inferred` returns `INSUFFICIENT_COVERAGE` (0% deep, below
floor), NOT `RELEASE_READY` — proven by a unit test (the evidence-poisoning defense). **What "blocking"
means** is LOCKED here (see AC4): a finding is blocking ONLY if it is verdict-eligible (advisory-by-contract).

**AC4 — Advisory-by-contract: a heuristic/advisory finding can NEVER drive a release-blocking verdict (cross-cutting #6, FR33-support, the moat)**
**Given** the 1.5 finding set carrying the LOCKED eligibility surface — a **heuristic-only / advisory**
finding is `advisory=True` + `depth_supported=None` + `rule_id="vacuous_test_heuristic"`; an
**AST-corroborated / verdict-eligible** finding is `advisory=True` + `depth_supported=AUDITED_SHALLOW` +
`rule_id="vacuous_test_ast"` (per the 1.5 Completion Notes — surfaced entirely within the 1.2 `Recording`
fields; the schema is NOT modified)
**When** the gate decides whether a finding is **blocking** (contributes to "≥1 blocking finding" in AC2)
**Then** the gate classifies a finding as **verdict-blocking ONLY** when it is **verdict-eligible** — the
dev LOCKS + documents the eligibility predicate the gate reads (recommended, matching the 1.5 locked
surface: a finding is verdict-eligible ⇔ `depth_supported is not None` — i.e. it carries an AST-corroborated
supported depth; a heuristic-only finding with `depth_supported is None` is NEVER blocking, regardless of
its `advisory` flag) — so a heuristic-only finding can **never** move the verdict to `NOT_READY_FOR_RELEASE`
on its own (architecture cross-cutting #6, the false-accusation moat; a wrong 🔴 is the lethal failure)
**And** the V1 boundary is documented: in Epic-1 the AST-corroborated finding IS the strongest blocking
signal the gate honors; the architecture's full rule ("AST corroboration AND Prosecutor sign-off") has its
Prosecutor half delivered in Epic-6 (`verdict/prosecutor.py`), which will further downgrade an unearned
verdict — the gate is written so the Prosecutor pass can be inserted additively without changing this
contract (the gate consumes a verdict-eligible finding set; the Prosecutor refines eligibility upstream)
**And** a unit test proves: a ledger with ≥60% deep + ONLY heuristic-only advisory findings returns
`RELEASE_READY` (the moat — advisory noise does not block); the SAME ledger with ≥1 AST-corroborated
verdict-eligible finding returns `NOT_READY_FOR_RELEASE` (the eligible finding blocks).

**AC5 — Deterministic finding ordering: verdict-blocking before non-blocking, fully tie-broken (FR33)**
**Given** a mix of blocking and non-blocking findings in arbitrary input order
**When** the gate orders them for the verdict result
**Then** **verdict-blocking findings sort strictly before non-blocking ones** so a blocking 🔴 is never
buried beneath advisory noise (FR33 alarm-fatigue defense), and the sort is **TOTAL and DETERMINISTIC** —
the dev LOCKS + documents a stable tie-break key (recommended: primary = blocking-first (eligible before
advisory-only), secondary = a documented severity/`rule_id` order, final = `recording_id` lexicographic so
the order is fully determined with NO reliance on input/iteration order — AR4); two runs over the same
findings in different input orders produce the **identical** ordered tuple, proven by a unit test
**And** the ordered findings travel WITH the verdict result (AC6) so a downstream consumer (Story 1.7 CLI /
Epic-4 evidence bundle) renders blocking findings first without re-sorting.

**AC6 — Frozen `AuditVerdict`-shaped result model carrying verdict + ordered findings + machine-readable fields (FR15, FR18, NFR-M2)**
**Given** a completed gate evaluation
**When** the verdict result is constructed
**Then** it is a **frozen Pydantic v2 model** (`frozen=True, extra="forbid"` — the 1.1/1.2 precedent)
carrying at minimum: the `verdict` (a closed enum / `Literal` over the LOCKED vocabulary), the **deep-%**
as a fixed-precision `Fraction`/`Decimal` (NEVER `float`), the per-depth counts (reuse
`counts_by_depth()`-derived ints), the count of verdict-blocking findings, the `ordered_findings: tuple[
Recording, ...]` (AC5), the **exit_code** (AC7), and `schema_version` — every field a machine consumer
(Story 1.7 / a CI gate) reads is reserved at birth (FR18 machine-readable; NFR-M2 additive-only)
**And** the result is canonical-serializable through the 1.1 `store/canonical.dumps` (no `float`; enum
serializes verbatim) and round-trips byte-identically (NFR-P1 / NFR-D3), proven by a golden round-trip test
REUSING the 1.1 serializer — NO second serializer (the `test_canonical_single_serializer.py` AST gate stays
green); a `compute_content_hash` over its canonical payload is reproducible
**And** the verdict result does NOT carry volatile fields (`run_id`/`created_at`) — those belong to the
Story-1.7 envelope around it (NFR-D3 hash-over-payload-only); the gate result is the pure payload.

**AC7 — Exit-code mapping is the locked wire contract `0/2/3/1` (FR18, AR3)**
**Given** a computed verdict
**When** it is mapped to a process exit code by a PURE mapping function in `verdict/verdict_gate.py`
**Then** the mapping is EXACTLY: **`RELEASE_READY → 0`**, **`NOT_READY_FOR_RELEASE` (BLOCKED) → 2**,
**`INSUFFICIENT_COVERAGE → 3`**, **crash → 1** (AR3 / mirrors Minions house style `0/1/2`, `3`=not-assessed)
— machine-consumable by a CI gate (FR18); the mapping is exhaustive over the verdict enum (a `match`/dict
that raises on an unmapped member, never a silent default) so adding a verdict member without a code is a
build-time failure
**And** the `crash → 1` code is the CONTRACT this story defines but the GATE itself never raises to produce
it (the gate is a total pure function over a valid ledger/finding set); `1` is reserved for the Story-1.7
pipeline's `AR10` typed-finding/uncaught-error degradation — document that the gate exposes the exit-code
MAPPING (including the reserved `1`) while the pipeline owns producing `1` on an actual crash
**And** a unit test pins each verdict→code pair and that the mapping is exhaustive/total.

**AC8 — Honest degradation: a partial/empty ledger produces a verdict, never a crash (NFR-R1, AR10, FR16)**
**Given** an empty ledger (`total == 0`) or a partial ledger (the Epic-3 budget-halt seam)
**When** the gate runs
**Then** it returns a verdict deterministically and NEVER raises an uncaught error — an empty ledger
(0% deep, below the 20% floor) returns `INSUFFICIENT_COVERAGE` (the dev locks + documents the `total == 0`
→ `INSUFFICIENT_COVERAGE` precedence so a divide-by-zero is structurally impossible — guard the deep-%
denominator), NOT a crash and NOT a default block (FR16)
**And** the gate's behavior over a partial ledger is the SAME pure fold as over a full one (no special
"partial" mode) so Epic-3 Story 3.3 reuses this gate VERBATIM over a budget-halted partial ledger (the
degradation BEHAVIOR is Epic-3; the floor LOGIC that makes it correct is delivered here) — documented as the
reuse seam.

**AC9 — Verdict vocabulary is the locked canonical set, frozen for downstream (Contract/Format Patterns)**
**Given** the verdict enum/`Literal`
**When** it is defined
**Then** it uses EXACTLY the LOCKED canonical vocabulary — `RELEASE_READY` / `NOT_READY_FOR_RELEASE`
(with `BLOCKED` as the documented demo SHORTHAND for the `NOT_READY_FOR_RELEASE` concept — the two names
denote ONE blocking concept; the dev locks whether the enum member is `NOT_READY_FOR_RELEASE` with `BLOCKED`
as a documented alias/string, OR carries both — recommended: enum member `NOT_READY_FOR_RELEASE`, exit-code
table + docstring note that `BLOCKED` is its shorthand) / `INSUFFICIENT_COVERAGE` (a distinct *not-assessed*
state, NOT a blocking verdict) — and a committed test pins the membership so a future author cannot silently
add/rename a verdict (closed vocabulary; additive evolution is a `schema_version` bump per NFR-M2)
**And** the string values are the wire contract serialized verbatim through `canonical.dumps`; downstream
artifacts (Story 1.7 verdict artifact, Epic-4 evidence bundle) consume this vocabulary verbatim.

**AC10 — The whole APAA suite green; tests cover the gate honestly; mypy clean; ≤1200 lines (NFR-M1)**
**Given** the modules + tests added by this story
**When** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` runs
**Then** all pass, including new tests in `tests/apaa/test_verdict_gate.py`: the three-way verdict over
synthetic ledgers (RELEASE_READY / NOT_READY / INSUFFICIENT_COVERAGE); the AC2 boundary tests
(19.99/20/59.99/60%); the AC3 `inferred`-never-satisfies test (100%-inferred → INSUFFICIENT_COVERAGE); the
**MANDATORY advisory-by-contract moat tests** (AC4 — heuristic-only advisory findings do NOT block;
AST-corroborated eligible findings DO block); the AC5 deterministic-ordering test (same findings in
different input orders → identical ordered tuple; blocking-first); the AC7 exit-code-mapping pins
(0/2/3/1, exhaustive); the AC8 empty/partial-ledger no-crash test; the AC9 vocabulary-membership pin; and
the AC6 golden canonical round-trip + reproducible `content_hash` via the 1.1 serializer (zero-`float`
invariant proven by serializing the result through `canonical.dumps_bytes`)
**And** `verdict/verdict_gate.py` is appended to `_MODULES_UNDER_GUARD` and the import-isolation gate stays
green; the 1.1 single-serializer AST gate (`test_canonical_single_serializer.py`) still passes with the new
modules present (no direct `json.dumps(` in any new module); every new source file is ≤1200 lines (NFR-M1)
and cites its `APAA-FR-*`/`APAA-NFR-*`/`AR*` drivers in the module docstring; `mypy` is clean on the new
modules.

## Tasks / Subtasks

- [x] **Task 0 — Confirm the spine + extra are present** (AC: all)
  - [x] Confirm the done spine is present and the gate's inputs exist: `ledger/coverage_ledger.py`
        (`CoverageDepth`, `CoverageLedger.deep_count()`/`total()`/`counts_by_depth()`), `ledger/recording.py`
        (`Recording` with `advisory`/`depth_supported`/`rule_id`/`recording_id`), `detectors/base.py`
        (`DetectorResult` — the finding source shape), `store/canonical.py` + `store/envelope.py`
        (the serializer/hash spine for the golden round-trip).
  - [x] Re-read the 1.5 LOCKED eligibility surface (1.5 Completion Notes): heuristic-only → `advisory=True`
        + `depth_supported=None` + `rule_id="vacuous_test_heuristic"`; AST-corroborated → `advisory=True` +
        `depth_supported=AUDITED_SHALLOW` + `rule_id="vacuous_test_ast"`. The gate's verdict-eligibility
        predicate MUST be consistent with this surface (recommended predicate: `depth_supported is not None`).
- [x] **Task 1 — `verdict/` sub-package + the verdict vocabulary + result model** (AC: 6, 9)
  - [x] Create `minions_core/apaa/verdict/__init__.py` (sub-package shell, docstring) + `verdict/verdict_gate.py`
        (docstring cites `APAA-FR-15`, `APAA-FR-16`, `APAA-FR-18`, `APAA-FR-33`, `APAA-NFR-D2`, `APAA-NFR-D3`,
        `AR3`, `AR4`, `AR8`, cross-cutting #6).
  - [x] Define the closed verdict vocabulary (a `str`-valued `enum.Enum` like `CoverageDepth`, OR a
        `Literal` + module constants) with EXACTLY `RELEASE_READY` / `NOT_READY_FOR_RELEASE` /
        `INSUFFICIENT_COVERAGE`; document `BLOCKED` as the `NOT_READY_FOR_RELEASE` shorthand. Pin membership
        with a test (AC9).
  - [x] Define the frozen `AuditVerdict` result model (`frozen=True, extra="forbid"`): `verdict`,
        `deep_ratio: Fraction` (NEVER `float`), per-depth counts, `blocking_finding_count: int`,
        `ordered_findings: tuple[Recording, ...]`, `exit_code: int`, `schema_version: str` (a localized
        `VERDICT_SCHEMA_VERSION` constant). No volatile `run_id`/`created_at` (those are 1.7's envelope).
- [x] **Task 2 — Gate evaluation: thresholds + inferred-never-satisfies + advisory-by-contract** (AC: 2, 3, 4, 8)
  - [x] Compute deep-% as `Fraction(deep_count, total)` guarding `total == 0` → `INSUFFICIENT_COVERAGE`
        (no divide-by-zero — AC8). Numerator = `audited_deep` ONLY (AC3 / FR8); denominator = `total`.
  - [x] LOCK + document the eligibility predicate (`depth_supported is not None`) and classify findings:
        verdict-blocking ⇔ verdict-eligible (AC4 moat); count `blocking_finding_count` over eligible findings.
  - [x] Apply the LOCKED thresholds + precedence (AC2): `total==0`/deep-% `< 20%` → `INSUFFICIENT_COVERAGE`
        (floor wins over blocking — document); deep-% `≥ 60%` AND `0` blocking → `RELEASE_READY`; else
        (`≥ 20%` AND (`< 60%` OR ≥1 blocking)) → `NOT_READY_FOR_RELEASE`. Pin boundary tests at
        19.99/20/59.99/60%. PURE — no I/O, no clock, no LLM (AC1).
- [x] **Task 3 — Deterministic finding ordering (blocking-first, fully tie-broken)** (AC: 5)
  - [x] LOCK + document the total sort key (recommended: `(not eligible, <severity/rule order>,
        recording_id)`) so blocking-first and the order is fully determined with NO input/iteration-order
        reliance (AR4). Produce `ordered_findings` for the result; prove order-independence in a test.
- [x] **Task 4 — Exit-code mapping (the `0/2/3/1` wire contract)** (AC: 7)
  - [x] A PURE exhaustive mapping (`match`/dict that RAISES on an unmapped verdict — never a silent default):
        `RELEASE_READY→0`, `NOT_READY_FOR_RELEASE→2`, `INSUFFICIENT_COVERAGE→3`. Document `crash→1` as the
        reserved code the 1.7 pipeline produces (the gate is total and does not crash). Store `exit_code` on
        the `AuditVerdict` result (AC6).
- [x] **Task 5 — Tests** (AC: 1–10)
  - [x] `tests/apaa/test_verdict_gate.py` — three-way verdict over synthetic ledgers; AC2 boundary cases;
        AC3 `inferred`/`skipped`/`tool_scanned_only`/`shallow` never count toward deep-% (100%-inferred →
        INSUFFICIENT_COVERAGE); **MANDATORY moat tests** (AC4 — heuristic-only advisory does NOT block;
        AST-corroborated eligible DOES block); AC5 order-independence + blocking-first; AC7 exit-code pins
        (0/2/3/1, exhaustive); AC8 empty + partial ledger → verdict, no crash; AC9 vocabulary pin; AC6
        golden canonical round-trip + reproducible `content_hash` + zero-`float` (serialize through
        `canonical.dumps_bytes`). Build `Recording` findings via the 1.5 `build_recording` (REUSE) or
        directly, mirroring the 1.5 locked eligibility surface.
- [x] **Task 6 — Extend the import-isolation gate** (AC: 1, 10)
  - [x] Append `minions_core.apaa.verdict.verdict_gate` (+ any new sibling) to `_MODULES_UNDER_GUARD` in
        `tests/apaa/test_no_web_imports.py` (do NOT fork the gate). Confirm no web/LLM/api/writer leak.
- [x] **Task 7 — Run + mypy** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass (the 1.1
        single-serializer AST gate + the extended no-web-imports gate re-run with the new modules present).
  - [x] `mypy` clean on the new modules (`python run_mypy_per_file.py` or scoped).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **Pure/impure separation (master rule, AR8).** The verdict gate is the canonical PURE terminal fold — the
  architecture lists `verdict` among the pure modules and gives the exact rule: *"✅ verdict gate imports only
  ledger models · ❌ verdict gate reads a file or calls `dispatch()`"*. Import ONLY the 1.2
  `coverage_ledger`/`recording` models (+ the 1.5 `Recording` it consumes). The gate takes its inputs as
  in-memory arguments; the pipeline (1.7) is what reads `.apaa/` and passes them in. NO I/O, NO clock, NO LLM.
- **The verdict vocabulary is LOCKED (architecture §Contract/Format Patterns, PRD §Verdict vocabulary).**
  `RELEASE_READY` / `NOT_READY_FOR_RELEASE` (`BLOCKED` = demo shorthand for the blocking `NOT_READY` concept —
  the two names denote ONE concept) / `INSUFFICIENT_COVERAGE` (a distinct *not-assessed* state, NOT a blocking
  verdict). Exit codes `0/2/3/1`. Downstream artifacts use this vocabulary verbatim. Do NOT invent a fourth
  verdict (e.g. a separate `ERROR` verdict — `crash` is an exit code `1`, not a verdict the gate emits).
- **The gate thresholds are LOCKED (PRD FR16, architecture Decision A/C).** `RELEASE_READY` requires
  **≥60% `audited_deep` + 0 blocking findings** (+ all critical subsystems deep — that clause is Story 2.3,
  NOT this story); **below the 20% floor → `INSUFFICIENT_COVERAGE`** (never a default block). The
  critical-subsystem clause is the ONLY FR16 piece deferred — this story delivers the deep-% + blocking +
  floor core. Write the gate so the critical-subsystem clause inserts additively in Story 2.3 (e.g. an
  optional `critical_subsystems_all_deep: bool = True` gate input that defaults to satisfied in V1 — document
  the seam; do NOT build the identification/designation, that is Story 2.3).
- **Advisory-by-contract is THE keystone moat (cross-cutting #6, the 1.5 contract).** A heuristic/advisory
  finding can NEVER drive the verdict to a release-blocking state. ONLY a verdict-eligible (AST-corroborated)
  finding can. The 1.5 detector LOCKED the surface the gate reads: heuristic-only → `depth_supported=None` +
  `rule_id="vacuous_test_heuristic"`; AST-corroborated → `depth_supported=AUDITED_SHALLOW` +
  `rule_id="vacuous_test_ast"`. **Recommended gate predicate: a finding is verdict-blocking ⇔
  `depth_supported is not None`** (the AST-corroborated supported depth is the eligibility signal). Do NOT key
  blocking on `advisory` alone — BOTH heuristic-only AND AST-corroborated 1.5 findings carry `advisory=True`
  (the demo line stays `🔴 tests *appear* vacuous`), so `advisory` does NOT distinguish them; `depth_supported`
  does. Lock + document the predicate and pin it with the mandatory moat test (a wrong 🔴 is the lethal
  failure). The architecture's full rule is "AST corroboration AND Prosecutor sign-off"; the Prosecutor half
  is Epic-6 — write the gate so the Prosecutor pass refines the eligible finding set upstream without
  changing this gate's contract.
- **No floats — ever — in a `.apaa/`-bound model (AR4 / Determinism / R4 red-team).** The deep-% is a RATIO —
  the obvious `float` trap. Store/compare it as a `Fraction` (exact: `Fraction(deep_count, total)`) or a
  `Decimal`. The 60% / 20% thresholds compare as `Fraction(3, 5)` / `Fraction(1, 5)`. The 1.1 serializer
  REJECTS `float` with `CanonicalSerializationError`; a `float` field on `AuditVerdict` would explode at
  serialize time. `Fraction` → `"num/den"` and `Decimal` → `format(d.normalize(),'f')` are already frozen by
  1.1 — inherited automatically through `canonical.dumps`.
- **One serializer / one finding model (AR4, reuse-canonical, §3.3).** The finding row is the 1.2 `Recording`
  — the gate consumes and re-orders it; it does NOT define a parallel finding model and does NOT modify
  `ledger/recording.py`. Any `.apaa/`-bound golden bytes go through `store/canonical.dumps_bytes`; the
  committed `test_canonical_single_serializer.py` AST gate fails the build on a direct `json.dumps(`.
- **Deterministic ordering / no iteration-order reliance (AR4, FR33).** The ordered findings must be a TOTAL
  order with a documented tie-break ending in `recording_id` lexicographic, so two runs over the same finding
  set in different input orders produce the identical tuple (the NFR-P1 byte-identical property). Never rely
  on input order or `set`/dict iteration order.
- **Error/degradation → recorded, never crash (AR10, NFR-R1).** The gate is a TOTAL pure function: an empty
  ledger → `INSUFFICIENT_COVERAGE` (guard `total == 0` BEFORE the deep-% division), a partial ledger → the
  same fold (Epic-3 reuse seam). The gate itself never produces exit code `1` — `1` is the reserved
  pipeline-crash code (Story 1.7 / AR10). NO bare `except: pass`, NO `print()` in library code.
- **Headless / import boundary (§Architectural Boundaries, AR7/AR9).** APAA is downstream of the HTTP/A2A
  boundary — `verdict/` takes no token, registers no FastAPI route, imports no web stack, and imports NO LLM
  (the verdict is zero-token). Never import `minions_core.api.* / services.api_app / app_factory /
  api_server / providers.* / apaa.audit.* / apaa.store.writer`. The new module joins `_MODULES_UNDER_GUARD`.

### The gate's exact decision table (recommended — dev locks + documents)

Given `deep_ratio = Fraction(deep_count, total)` (with `total == 0` short-circuiting to
`INSUFFICIENT_COVERAGE`) and `blocking = (count of findings where depth_supported is not None)`:

| condition (evaluated in order) | verdict | exit code |
|---|---|---|
| `total == 0` OR `deep_ratio < Fraction(1, 5)` (< 20%) | `INSUFFICIENT_COVERAGE` | 3 |
| `deep_ratio >= Fraction(3, 5)` (≥ 60%) AND `blocking == 0` | `RELEASE_READY` | 0 |
| otherwise (`>= 20%` AND (`< 60%` OR `blocking >= 1`)) | `NOT_READY_FOR_RELEASE` | 2 |

**Precedence note (lock + document + test):** the floor is evaluated FIRST, so a below-20% ledger returns
`INSUFFICIENT_COVERAGE` EVEN WITH blocking findings — rationale: below the floor APAA has not assessed enough
to honestly claim it saw enough to BLOCK either; low coverage is APAA's limitation to report, not a verdict
to render. This is the recommended precedence; if the dev chooses otherwise, document the rationale and pin
it with a test (decision recorded in the Change Log per §3.4).

### Why `depth_supported is not None` is the eligibility predicate (not `advisory`)

The 1.5 detector deliberately keeps `advisory=True` on BOTH the heuristic-only AND the AST-corroborated
finding (the signature demo line is `🔴 tests *appear* vacuous` — advisory framing preserved even for the
corroborated 🔴). So `advisory` does NOT separate "can block" from "cannot block". The separator the 1.5
detector LOCKED is `depth_supported`: `None` for heuristic-only (verdict-ineligible), `AUDITED_SHALLOW` for
AST-corroborated (verdict-eligible) — see 1.5 Completion Notes ("Verdict-eligibility surface (read by 1.6)").
The gate therefore reads `depth_supported is not None` as "verdict-eligible / can be blocking". Lock this in
the gate docstring so a future detector author knows the contract: to make a finding verdict-eligible it must
carry a non-`None` `depth_supported` (and pass whatever future Prosecutor sign-off Epic-6 adds). This keeps
the moat: a detector that emits only `advisory=True, depth_supported=None` findings can never block.

### Precedent inherited from Stories 1.1–1.5 (done) — honor these decisions

- **No second serializer / reuse the 1.1 spine.** `store/canonical.py` + `store/envelope.py` are the only
  serializer + envelope; reuse for the `AuditVerdict` golden round-trip + `content_hash`. The AST gate
  enforces it.
- **The finding row IS the 1.2 `Recording`.** The gate consumes/re-orders it; do NOT define a parallel
  finding model; do NOT modify `ledger/recording.py`.
- **The ledger IS the 1.2 `CoverageLedger`.** Use its `deep_count()`/`total()`/`counts_by_depth()` accessors;
  do NOT re-derive coverage math. Do NOT modify `ledger/coverage_ledger.py`.
- **Closed enum + membership pin (1.2 `CoverageDepth` precedent).** The verdict vocabulary is a closed
  `str`-valued enum (or `Literal`) with a committed membership pin — mirror the 1.2 `CoverageDepth` test.
- **Frozen `extra="forbid"` models** (1.1 `Envelope`, 1.2 `Recording`/`CoverageLedger`, 1.5 `DetectorResult`):
  the new `AuditVerdict` follows the SAME pattern (`frozen=True, extra="forbid"`).
- **`Fraction`/`Decimal` over `float`** — the 1.5 detector already proved fixed-precision ratios serialize
  through the 1.1 encoding (TC-APAA-DETECT-001-92). The deep-% follows the same rule.
- **`partition_id` is always `"root"` in V1.** The gate folds the single `"root"` partition; do NOT build
  partition-aware aggregation (Story 2.4).
- **`apaa_version`/`schema_version` single source** — `minions_core/apaa/__init__.py::__version__` (`"0.1.0"`);
  per-model `schema_version` is a localized module constant (`VERDICT_SCHEMA_VERSION`), never env/clock.
- **Test-area precedent** — use area `APAA-VERDICT` for this story's test ids (`TC-APAA-VERDICT-001-NN`),
  consistent with the 1.x convention (`APAA-STORE`, `APAA-LEDGER`, `APAA-INTAKE`, `APAA-INDEX`,
  `APAA-DETECT`).
- **Import-isolation gate is seeded, extend it** — append the new module(s) to `_MODULES_UNDER_GUARD`; do not
  fork.

### Source tree — files to create (all NEW; the only UPDATE is the import-isolation gate)

| Path | Status | Purpose |
|---|---|---|
| `minions_core/apaa/verdict/__init__.py` | NEW | `verdict/` sub-package shell (docstring) |
| `minions_core/apaa/verdict/verdict_gate.py` | NEW | FR15/FR16/FR33/FR18 — PURE verdict fold + finding ordering + exit-code mapping + frozen `AuditVerdict` result (PURE) |
| `tests/apaa/test_verdict_gate.py` | NEW | three-way verdict; boundaries; inferred-never-satisfies; advisory-by-contract moat; deterministic ordering; exit-code pins; empty/partial no-crash; vocabulary pin; golden round-trip |
| `tests/apaa/test_no_web_imports.py` | UPDATE | extend `_MODULES_UNDER_GUARD` with the new module(s) |

The architecture's package tree (`architecture.md` §Project Structure) places EXACTLY `verdict/verdict_gate.py`,
`verdict/prosecutor.py`, and `verdict/negative_assurance.py` in this sub-package. **`prosecutor.py` is Epic-6
and `negative_assurance.py` is Epic-4 Story 4.1** — do NOT build them here. Do not invent additional modules;
the CLI/pipeline are `cli.py`/`pipeline.py` (1.7). Resist building ahead.

### Determinism / contract decisions the dev must lock (record the choice in the docstring + Change Log)

- **Verdict vocabulary representation** — `str`-valued `enum.Enum` (recommended, mirrors `CoverageDepth`)
  vs `Literal` + constants. Whether `BLOCKED` is a documented shorthand alias or only a docstring note.
- **Threshold boundary semantics** — `RELEASE_READY` at deep-% `>= 60%` (recommended inclusive);
  `INSUFFICIENT_COVERAGE` at deep-% `< 20%` (recommended strict, so exactly-20% is assessable). Lock + test
  the boundaries.
- **Floor-vs-blocking precedence** — floor wins (recommended; below-floor → `INSUFFICIENT_COVERAGE` even with
  blocking findings) vs blocking wins. Lock + document the rationale + pin a test.
- **Verdict-eligibility predicate** — `depth_supported is not None` (recommended, matches the 1.5 locked
  surface) vs `rule_id == "vacuous_test_ast"` (more brittle — couples the gate to a detector's rule-id
  vocabulary). Lock + document.
- **Finding sort key** — the total tie-broken order (recommended: `(not eligible, <severity/rule order>,
  recording_id)`). Lock + document; the final tie-break must be deterministic (recording_id lexicographic).
- **Deep-% ratio type** — `Fraction` (recommended, exact `Fraction(deep_count, total)`) vs `Decimal`. NEVER
  `float`.
- **`AuditVerdict` field set** — the frozen result the 1.7 pipeline consumes (verdict, deep_ratio, per-depth
  counts, blocking_finding_count, ordered_findings, exit_code, schema_version). Lock + document; no volatile
  `run_id`/`created_at` (1.7's envelope owns those).
- **Critical-subsystem-clause seam** — how Story 2.3 inserts the "all critical subsystems deep" clause
  additively (recommended: an optional `critical_subsystems_all_deep: bool = True` gate parameter defaulting
  to satisfied in V1). Document the seam; do NOT build the clause.

### Scope fences (do NOT pull forward)

- ❌ The **CLI / pipeline wiring** + the cartridge run + the signature 🔴 (`cli.py`/`pipeline.py`/
  `tests/apaa/cartridges/`) — Story 1.7. This story computes a verdict + exit code; it runs no CLI/pipeline.
- ❌ The **critical-subsystem clause** of FR16 (`RELEASE_READY` withheld when a designated critical subsystem
  is below deep) — Story 2.3. This story delivers the ≥60%-deep + 0-blocking + 20%-floor core ONLY (leave the
  additive seam).
- ❌ The **negative-assurance verdict semantics** — scope statement / materiality bar / disclaimer /
  point-in-time stamp (`verdict/negative_assurance.py`) — Epic-4 Story 4.1. This story produces the verdict
  CONCEPT + vocabulary, NOT the negative-assurance wrapper.
- ❌ The **adversarial Prosecutor** + sign-off (`verdict/prosecutor.py`) — Epic-6. V1 stops at the gate
  honoring AST-corroborated eligibility; Prosecutor sign-off is the Epic-6 second half of the "🔴 needs AST +
  Prosecutor" rule (write the gate so it inserts additively upstream).
- ❌ The **`INSUFFICIENT_COVERAGE` floor under budget exhaustion** as a degradation BEHAVIOR — Epic-3 Story
  3.3 reuses THIS gate over a partial ledger. The floor LOGIC is delivered here; the budget-halt wiring is
  Epic-3.
- ❌ The **cache / memo store** (`cache/key.py`, `cache/memo_store.py`) — Epic-5. The verdict's
  reproducibility here is sequential-determinism (pure fold), not memoization.
- ❌ The **LLM dispatch port / adapter / deep-audit** (`audit/*`) — Epic-6. The verdict is zero-token; no LLM
  import.
- ❌ Writing the verdict to `.apaa/` — the gate is PURE. Persisting the verdict artifact (envelope-wrapped via
  the 1.3 shell) is Story 1.7's pipeline.

### Testing standards

- pytest under `tests/apaa/`; test ids follow `TC-<AREA>-<SEQ>-<SUBSEQ>` — use area `APAA-VERDICT` (e.g.
  `TC-APAA-VERDICT-001-01`), consistent with the 1.x convention.
- These are **pure-function / model golden tests** — zero LLM tokens (NFR-D2), no temp dirs for the module
  under test. Build synthetic `CoverageLedger`s via `CoverageLedger.build([grade_entry(...), ...])` and
  `Recording` findings via the 1.5 `build_recording` (REUSE) or direct construction mirroring the 1.5 locked
  eligibility surface. Freeze a golden canonical string + `content_hash` for a populated `AuditVerdict` so
  byte-drift fails loudly (NFR-P1).
- **The advisory-by-contract moat test is MANDATORY** (cross-cutting #6 / the lethal-failure moat): an
  explicit test that a ledger with ≥60% deep + ONLY heuristic-only advisory findings returns `RELEASE_READY`
  (advisory noise does not block), and that the SAME ledger with ≥1 AST-corroborated verdict-eligible finding
  returns `NOT_READY_FOR_RELEASE`.
- **The `inferred`-never-satisfies test is MANDATORY** (FR8): a 100%-`inferred` ledger → `INSUFFICIENT_COVERAGE`.
- On Windows, prefix runs with `PYTHONIOENCODING=utf-8` (project memory: emoji/gate scripts crash on cp1252).
- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` (the WHOLE
  `tests/apaa/` suite, so the 1.1 single-serializer AST gate + the extended no-web-imports gate re-run with
  the new modules present). All must pass before moving to `review`.
- `mypy` clean on the new modules (`python run_mypy_per_file.py` or a scoped invocation).

### CLAUDE.md §4a follow-up

The §4a APAA Component→Driver row was added by Story 1.1. This story does NOT need a new §4a row; if a
one-line additive note is added it must note `verdict/verdict_gate.py` as the pure-function verdict gate +
finding ordering + exit-code mapping (FR15/FR16/FR18/FR33) and must NOT rewrite the existing row. Keep it
minimal — a new row is not required.

### Project Structure Notes

- Alignment: file paths exactly match `architecture.md` §Project Structure package tree
  (`verdict/verdict_gate.py`). `prosecutor.py` (Epic-6) / `negative_assurance.py` (Epic-4) are deferred.
  Naming `snake_case.py`, ≤1200 lines (NFR-M1). JSON/enum values `snake_case` (verdict tokens are
  `UPPER_SNAKE` per the LOCKED vocabulary — the wire contract; documented).
- No conflicts/variances. Judgment calls — all decided above and to be documented so they freeze for
  downstream: the verdict-vocabulary representation, the threshold boundary semantics, the floor-vs-blocking
  precedence, the verdict-eligibility predicate, the finding sort key, the ratio type, the `AuditVerdict`
  field set, and the critical-subsystem-clause seam.
- Scope fence: this story delivers the PURE verdict gate + finding ordering + exit-code mapping ONLY. The
  CLI/pipeline + cartridge (1.7), the critical-subsystem clause (2.3), negative-assurance (4.1), Prosecutor
  (Epic-6), budget-halt degradation (3.3), cache (Epic-5), and any LLM wiring are explicitly NOT in scope.
  Build the gate complete-and-contained, then stop.

### References

- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Story-1.6 Pure-function verdict gate, finding ordering & exit-code mapping]
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#A. Execution & Invocation] (exit-code wire contract `0`=RELEASE_READY / `2`=BLOCKED / `3`=INSUFFICIENT_COVERAGE / `1`=crash; pure `AuditRequest → AuditVerdict`)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#C. Coverage Ledger, Recording Schema & Verdict (determinism core)] (pure-function verdict gate, 0 LLM tokens; Prosecutor = distinct pure-consumer pass)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Contract / Format Patterns] (verdict vocabulary canonical: RELEASE_READY / NOT_READY_FOR_RELEASE (BLOCKED shorthand) / INSUFFICIENT_COVERAGE; exit codes 0/2/3/1)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Cross-Cutting Concerns #6 advisory-by-contract] (no verdict-moving 🔴 without AST corroboration AND Prosecutor sign-off; false-accusation moat)
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Pure/Impure Separation (master rule)] (verdict gate imports only ledger models; never reads a file or calls dispatch())
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md#Determinism Patterns (NFR-P1/D1)] (one serializer; no floats — ratios fixed-precision; no iteration-order reliance)
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#FR15 pure-function verdict / FR16 gates+floor (≥60% deep + 0 blocking; <20% → INSUFFICIENT_COVERAGE; never a default block) / FR18 exit code + machine-readable artifact / FR33 verdict-impact finding ordering / FR8 inferred-never-satisfies]
- [Source: _bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#Verdict vocabulary (canonical)] (RELEASE_READY → NOT_READY_FOR_RELEASE; BLOCKED = demo shorthand; INSUFFICIENT_COVERAGE = not-assessed floor)
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-2-fixed-enum-coverage-ledger-frozen-recording-schema.md] (DONE — `CoverageLedger`/`CoverageDepth`/`deep_count`/`total`/`counts_by_depth`/`grade_entry`; `Recording` = the finding row the gate folds; closed-enum membership-pin precedent; golden round-trip + `extra="forbid"`)
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-5-heuristic-vacuous-test-detector-tier-a-vacuous-path-ast-subset.md] (DONE — the LOCKED eligibility surface the gate reads: heuristic-only → advisory + depth_supported=None + rule_id=vacuous_test_heuristic; AST-corroborated → advisory + depth_supported=AUDITED_SHALLOW + rule_id=vacuous_test_ast; `DetectorResult`/`build_recording`)
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-1-canonical-serializer-content-hashed-envelope.md] (DONE — serializer + envelope spine for the golden round-trip; `_MODULES_UNDER_GUARD` seed + single-serializer AST gate; Decimal/Fraction encoding)
- [Source: minions_core/apaa/ledger/coverage_ledger.py] (`CoverageLedger.deep_count()`/`total()`/`counts_by_depth()` + `CoverageDepth` — the ledger the gate folds)
- [Source: minions_core/apaa/ledger/recording.py] (`Recording` with `advisory`/`depth_supported`/`rule_id`/`recording_id` — the finding row the gate orders/classifies)
- [Source: minions_core/apaa/detectors/base.py] (`DetectorResult`/`build_recording` — the finding source shape + the recording-id/eligibility precedent)
- [Source: minions_core/apaa/store/canonical.py + store/envelope.py] (the single serializer/envelope/`compute_content_hash` to reuse for the `AuditVerdict` golden round-trip)
- [Source: minions_core/apaa/__init__.py] (`__version__ = "0.1.0"` — single apaa_version source)
- [Source: tests/apaa/test_no_web_imports.py] (`_MODULES_UNDER_GUARD` — the import-isolation gate to extend, not fork)
- [Source: CLAUDE.md §3.2 file-size / §3.7 headless-only / §3.8 12-Factor + secret masking / §4a APAA row]

## Dev Agent Record

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, mode=implement)

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/test_verdict_gate.py -q` → 40 passed.
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → 347 passed.
- `python -m mypy minions_core/apaa/verdict/verdict_gate.py` → Success: no issues.

### Completion Notes List

LOCKED decisions (frozen for downstream):

- **Verdict vocabulary** — `str`-valued `enum.Enum` `Verdict` with EXACTLY
  `RELEASE_READY` / `NOT_READY_FOR_RELEASE` / `INSUFFICIENT_COVERAGE` (mirrors the
  1.2 `CoverageDepth` precedent). `BLOCKED` is a module CONSTANT aliasing
  `Verdict.NOT_READY_FOR_RELEASE` (the documented demo shorthand), NOT a fourth
  member. No `ERROR`/`CRASH` verdict — `crash` is exit code `1`. Membership pinned
  by `TC-APAA-VERDICT-001-01/02/03`.
- **Thresholds + boundaries** — `RELEASE_READY` at deep-% `>= Fraction(3,5)` (60%,
  inclusive); `INSUFFICIENT_COVERAGE` at deep-% `< Fraction(1,5)` (20%, strict, so
  exactly-20% is assessable). Pinned by 19.99/20/59.99/60% boundary tests.
- **Floor-vs-blocking precedence = FLOOR WINS** (recommended option taken). The
  floor row is evaluated FIRST, so a below-20% ledger returns
  `INSUFFICIENT_COVERAGE` even with eligible blocking findings present
  (`TC-APAA-VERDICT-001-80`). Rationale: below the floor APAA has not assessed
  enough to honestly claim it saw enough to block either.
- **`total == 0` short-circuits to `INSUFFICIENT_COVERAGE`** BEFORE the deep-%
  division, so a divide-by-zero is structurally impossible (AC8). `deep_ratio`
  for an empty ledger is the exact `Fraction(0, 1)`.
- **Eligibility predicate = `depth_supported is not None`** (the advisory-by-contract
  moat, cross-cutting #6) — NOT `advisory`. `is_verdict_blocking(finding)` returns
  `finding.depth_supported is not None`. Both 1.5 finding kinds carry
  `advisory=True`; only `depth_supported` distinguishes the AST-corroborated
  (verdict-eligible) finding from the heuristic-only one. Mandatory moat tests:
  `TC-APAA-VERDICT-001-40` (heuristic-only ⇒ RELEASE_READY) and `-41`
  (AST-corroborated ⇒ NOT_READY).
- **Finding sort key** — `(not eligible, depth_rank, rule_id, recording_id)`:
  blocking-first, then a documented supported-depth rank (deepest first), then
  `rule_id`, final `recording_id` lexicographic. Total + deterministic — proven
  order-independent (`TC-APAA-VERDICT-001-51`).
- **Exit-code mapping** — exhaustive dict `{RELEASE_READY:0, NOT_READY:2,
  INSUFFICIENT_COVERAGE:3}`; `exit_code_for_verdict` RAISES `ValueError` on an
  unmapped member (no silent default). `1` (crash) is reserved for the 1.7
  pipeline and is never produced by the gate.
- **`AuditVerdict`** — frozen `extra="forbid"` (+ `arbitrary_types_allowed=True`
  for the `Fraction` field). Carries `verdict`, `deep_ratio: Fraction` (NEVER
  float), `deep_count`, `total_count`, `counts_by_depth`, `blocking_finding_count`,
  `ordered_findings`, `critical_subsystems_all_deep`, `exit_code`,
  `schema_version`. No volatile `run_id`/`created_at` (1.7's envelope owns those).
- **Canonical-serialization seam** — `AuditVerdict.to_canonical_payload()`
  re-installs the live `Fraction` object for `deep_ratio` after `model_dump()`,
  because pydantic v2's `model_dump()` coerces a `Fraction` via `str`
  (`Fraction(1,1) → "1"`), which DIVERGES from the LOCKED canonical
  `Fraction → "num/den"` encoding (`"1/1"`). The single 1.1 `canonical.dumps` then
  applies its frozen exact encoding. Golden bytes + reproducible `content_hash`
  pinned by `TC-APAA-VERDICT-001-92/93/94`. NO second serializer — the 1.1
  single-serializer AST gate stays green.
- **Critical-subsystem seam (Story 2.3)** — optional
  `critical_subsystems_all_deep: bool = True` parameter on `evaluate_verdict`
  (defaults satisfied in V1); a `False` withholds `RELEASE_READY` even at ≥60%
  deep + 0 blocking (`TC-APAA-VERDICT-001-86`). The identification/designation is
  NOT built here.

PURE (AR8): the module imports ONLY the 1.2 ledger/finding models (pinned by
`TC-APAA-VERDICT-001-96`); no os/time/datetime/uuid/random/subprocess/socket
imports (`-95`). Appended to `_MODULES_UNDER_GUARD`. Scope fences honored — no
CLI/pipeline (1.7), no negative-assurance (4.1), no Prosecutor (Epic-6), no
cache (Epic-5), no LLM (Epic-6), no `.apaa/` write.

### File List

- `minions_core/apaa/verdict/__init__.py` (NEW — verdict sub-package shell)
- `minions_core/apaa/verdict/verdict_gate.py` (NEW — PURE verdict fold + finding
  ordering + exit-code mapping + frozen `AuditVerdict`)
- `tests/apaa/test_verdict_gate.py` (NEW — 40 tests, area APAA-VERDICT)
- `tests/apaa/test_no_web_imports.py` (UPDATE — appended
  `minions_core.apaa.verdict.verdict_gate` to `_MODULES_UNDER_GUARD`)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (status → review)

## Senior Developer Review (AI)

**Reviewer:** XAgentsLabs007 (BMAD adversarial code-review gate, claude-opus-4-8)
**Date:** 2026-06-21
**Iteration:** 1
**Outcome:** PASS → `done`

### Summary

Story 1.6 delivers the PURE terminal verdict fold (`verdict/verdict_gate.py` + `verdict/__init__.py`)
complete-and-contained. All 10 ACs are met and adversarially verified. The whole APAA suite is green
(`tests/apaa/ tests/test_import_paths.py` → 347 passed), mypy is clean on the new modules, the
single-serializer AST gate (`test_canonical_single_serializer.py`) stays green, and
`verdict.verdict_gate` is correctly appended to `_MODULES_UNDER_GUARD` (import-isolation gate passes).
No High or Medium findings. One Low documentation-precision note (non-blocking).

### Adversarial verification performed (beyond re-running the suite)

- **Advisory-by-contract moat (cross-cutting #6 — the lethal-failure surface).** Verified non-bypassable:
  `is_verdict_blocking` is keyed strictly on `depth_supported is not None`, NOT `advisory`. A heuristic-only
  finding (`advisory=True, depth_supported=None`) returns `False` and `blocking_finding_count == 0` even at
  ≥60% deep → `RELEASE_READY` (TC-001-40); the same ledger with one AST-corroborated finding
  (`depth_supported=AUDITED_SHALLOW`) blocks (TC-001-41). A wrong 🔴 cannot be forced from heuristic noise.
- **Determinism / byte-reproducibility.** Independently fuzzed 24 distinct ledger-build orders over a 5-depth
  entry set: ALL produced ONE distinct canonical byte string and ONE content hash. Finding ordering verified
  total + input-order-independent (sort key `(not eligible, depth_rank, rule_id, recording_id)` ends in
  `recording_id` lexicographic — no input/iteration/object-id reliance).
- **Fraction canonical-encoding workaround (the flagged risk).** Independently exercised `to_canonical_payload`
  across `1/1, 0/1, 7/11, 1/2, 1/7, 13/17, 100/100`: in every case `deep_ratio` is re-installed as a live
  `Fraction` (never coerced to `"1"` by `model_dump()`), and the single 1.1 `canonical.dumps` applies the frozen
  `"num/den"` form. No Fraction slips through as a non-canonical leaf. The `counts_by_depth` enum keys survive
  `model_dump()` as `CoverageDepth` objects but serialize correctly because `CoverageDepth` is a `str` subclass
  (the `isinstance(key, str)` path in `canonicalize`). Single-serializer contract preserved — no second
  `json.dumps`, AST gate green.
- **total==0 / divide-by-zero guard.** Floor evaluated FIRST; `Fraction(0,1)` short-circuit before any division.
  Empty ledger → `INSUFFICIENT_COVERAGE` (exit 3); floor wins over an eligible blocking finding (TC-001-71/80).
- **FR8 inferred-never-satisfies.** Numerator = `deep_count()` (audited_deep only); 100%-inferred → 0% deep →
  `INSUFFICIENT_COVERAGE` (TC-001-30). Shallow/tool/skipped in denominator only (TC-001-31/32).
- **Exit-code map exhaustive.** `0/2/3` dict; `exit_code_for_verdict` raises `ValueError` on an unmapped member
  (TC-001-63); `1` (crash) reserved, never produced by the gate (TC-001-62).
- **Purity / scope.** No os/time/datetime/uuid/random/subprocess/socket imports; imports ONLY the 1.2
  ledger/finding models (TC-001-95/96). No web/LLM/writer leak. Critical-subsystem clause correctly left as the
  additive `critical_subsystems_all_deep: bool = True` seam (2.3). ≤1200 lines; headless.

### Acceptance Criteria coverage

AC1 (pure, zero-token) ✅ · AC2 (≥60%/<20% thresholds + boundaries) ✅ · AC3 (inferred-never-satisfies) ✅ ·
AC4 (advisory-by-contract moat) ✅ · AC5 (deterministic blocking-first ordering) ✅ · AC6 (frozen `AuditVerdict`
+ golden canonical round-trip + reproducible content_hash) ✅ · AC7 (`0/2/3/1` exhaustive map) ✅ · AC8
(empty/partial no-crash) ✅ · AC9 (locked vocabulary pin) ✅ · AC10 (suite green, mypy clean, ≤1200, gate
extended) ✅.

### Action Items

- [ ] [Low][Doc] `verdict_gate.py` `to_canonical_payload` docstring [verdict_gate.py:222-233] — the line
  "Every other leaf (enum values … the Recording finding rows) already model_dump()s to canonical-safe JSON
  primitives" is slightly imprecise: `counts_by_depth` keys remain `CoverageDepth` enum objects after
  `model_dump()` and are canonical-safe only because `CoverageDepth` is a `str` subclass (the str-key path in
  `canonicalize`), not because `model_dump()` coerces them. Behaviour is correct and tested; consider a
  one-line clarification for a future maintainer. Non-blocking; no code change required for this story.
- [ ] [Low][Doc] `exit_code_for_verdict` docstring [verdict_gate.py:283-298] says "a `match` that RAISES",
  but the implementation uses a dict lookup + `try/except KeyError → ValueError`. Behaviour (exhaustive, raises
  on unmapped) matches the AC7 contract; wording could say "an exhaustive dict that raises". Cosmetic.

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-06-21 | 0.2.0 | Implemented (dev-story) — `verdict/__init__.py` + PURE `verdict/verdict_gate.py`: closed `Verdict` enum (RELEASE_READY/NOT_READY_FOR_RELEASE/INSUFFICIENT_COVERAGE; `BLOCKED` constant = NOT_READY shorthand), frozen `AuditVerdict` (deep_ratio as exact `Fraction`, never float), `evaluate_verdict` decision table (floor-first precedence — LOCKED floor-wins; `total==0` short-circuit guarding divide-by-zero), `is_verdict_blocking` advisory-by-contract moat keyed on `depth_supported is not None` (NOT `advisory`), `order_findings` total tie-broken blocking-first sort (FR33), exhaustive `exit_code_for_verdict` `0/2/3/1` (raises on unmapped), `to_canonical_payload` re-installing the live `Fraction` so the single 1.1 serializer applies the canonical `num/den` encoding (golden bytes + reproducible content_hash pinned). Critical-subsystem clause left as the additive `critical_subsystems_all_deep=True` seam (Story 2.3). 40 new APAA-VERDICT tests; `_MODULES_UNDER_GUARD` extended. `tests/apaa/ tests/test_import_paths.py` 347 passed; mypy clean. Status → review. | claude-opus-4-8 (Dev) |
| 2026-06-21 | 0.1.0 | Story drafted (create-story) — pure-function verdict gate (`verdict/verdict_gate.py`) folding the 1.2 `CoverageLedger` + the 1.5 `Recording` findings into the LOCKED verdict vocabulary (RELEASE_READY / NOT_READY_FOR_RELEASE(BLOCKED) / INSUFFICIENT_COVERAGE), with the ≥60%-deep + 0-blocking gate + the 20% floor (FR16 core; critical-subsystem clause deferred to 2.3), `inferred`-never-satisfies coverage math (FR8), the advisory-by-contract moat (only `depth_supported is not None` findings can block — heuristic-only advisory never blocks), deterministic blocking-first finding ordering (FR33), a frozen `AuditVerdict` result, and the `0/2/3/1` exit-code wire contract (FR18/AR3). PURE (zero tokens, no I/O, no clock); reuses the 1.1 serializer + 1.2 ledger/finding models verbatim. Status → ready-for-dev. | claude-opus-4-8 (Scrum Master) |
