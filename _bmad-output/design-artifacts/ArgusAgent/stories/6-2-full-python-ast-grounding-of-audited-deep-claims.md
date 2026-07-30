# Story 6.2: Full Python AST-grounding of `audited_deep` claims — [Tier B]

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker at `_bmad-output/implementation-artifacts/sprint-status.yaml`). All
> CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only, §3.8 12-Factor + secret masking, §3.4
> evidence immutability).
>
> **This is the SECOND story of Epic 6** (Trust Substrate — Self-Audit, Prosecutor & Precision, Tier-B). It
> builds on the fully-done Epics 1+2+3+4+5 (the Epic-5 retro recorded 1032 passed / 1 skipped / 4 subtests,
> mypy clean, all files ≤1200 lines, zero hard review FAILs in Epic 5, a converged net-≈0 defer-inflow) and
> on **done Story 6.1** (the `LLMDispatchPort` + `MinionsLLMAdapter` + `FakeDispatch` + the thin
> `DeepAuditSeam` + the closure-from-recording substitution helper). `epic-6` is already `in-progress`.
>
> **THIS STORY IS THE HARD DELIVERABLE that CLOSES the long-carried 🟡 `DF-1-7-B` (interim Python deep
> over-grading) — AI-E5-5.** The runway has collapsed to one epic: 6.2 is the LAST opportunity to close
> DF-1-7-B BEFORE the Epic-7 dogfood presents a verdict. Story 1.7 (and the pipeline since Epic 1) grades
> EVERY cleanly-parsed non-test Python file `audited_deep` purely on claim-PRESENCE (`grade_entry(
> proposed_depth=AUDITED_DEEP, claim_present=True)` — FR6). This story implements **FR7 full Python AST
> GROUNDING**: a non-test Python file is `audited_deep` only when its deep claim is actually
> **AST-grounded/verified** against the file's own multi-construct AST, NOT merely present. An unverifiable
> claim downgrades to `audited_shallow` (silence/insufficiency → downgrade).

## Story

As an **Engineering Lead** who must trust that an `audited_deep` grade means a file's structure was actually
examined — not that a presence flag was set — so that the negative-assurance verdict and the deep-% the
20%/60% gate reads are *earned*, not asserted (the difference between a demo-grade and a validation-grade
audit, and the whole reason Epic 6 exists),
I want **the V1 claim-PRESENCE deep-grading path for non-test Python files (`_grade_non_test_python`,
FR6/Epic-1) replaced by an FR7 AST-GROUNDING gate**: a pure validator (`audit/deep_audit.py`, the seam 6.1
built) that, given a non-test Python file's 1.4 AST-index entry (its `definitions` + `edges` — the same
structural substrate the 1.5 vacuous-path subset reads for test files), decides whether the deep claim is
**AST-grounded** — i.e. the file actually exhibits the auditable structure a deep read claims (≥1 real
definition the audit could ground a claim against, not an empty/trivial/constants-only module) — and grades
`audited_deep` ONLY when grounded, downgrading an ungroundable claim to `audited_shallow` through the
EXISTING 1.2 `grade_entry` honesty keystone (extended, not forked); routing a non-Python file (and any
AST-ineligible/parse-failed file) through the stack-agnostic `claim→validated?` interface to the
`claim_emitted` proxy so V2 multi-language is purely additive (NFR-P2),
so that **DF-1-7-B is CLOSED** — the over-grading is removed, a shallow read mis-graded as deep is caught and
downgraded, the deep-% the gate reads reflects grounded depth, and the migration is HONEST: the verdict on
real repos (and on the signature-demo cartridge + every existing fixture) is re-graded under the new rule and
its expectations are updated deliberately and documented, not silently broken.

## Story Context

This is **Story 2 of Epic 6** (Trust Substrate, Tier-B — the "proven, not asserted, depth" moat). It is the
**owning story of the long-carried 🟡 DF-1-7-B** (origin: story 1-7; target_story:
`6-2-full-python-ast-grounding-of-audited-deep-claims`; the Epic-1/4/5 retros flagged it through AI-E2-2 →
AI-E3-4 → AI-E4-5 → **AI-E5-5**). It delivers **FR7 (full Python AST-grounding of `audited_deep` claims,
`[Tier B]`)** over the determinism spine (Epics 1–5) and the LLM seam (6.1).

**What 6.1 left for 6.2 (explicit handoff).** 6.1 built the SEAM and explicitly fenced the GROUNDING LOGIC
to 6.2: its scope note reads "It does NOT build the **full Python AST-grounding of deep claims** (Story 6.2,
which CLOSES DF-1-7-B)"; its `deep_audit.py` is a thin `DeepAuditSeam` (dispatch one request, return the
recording) + the `build_closure_from_recording` substitution helper; and its Dev Notes say "the LIVE
end-to-end LLM run (the pipeline call site that drives `deep_audit` through the real adapter) is fenced to
6.2 (the AST-grounding deliverable that closes DF-1-7-B). Do NOT wire a live LLM call into the pipeline this
story." **6.2 is where the deep-claim VALIDATOR is built and wired into the pipeline grading site.**

**The over-grading site this story replaces (the exact DF-1-7-B locator).** The flagged line is
`minions_core/apaa/pipeline.py:149` (the locator recorded in 1.7's defer entry; the function has since moved
but the LOGIC is unchanged). It is `pipeline.py::_grade_non_test_python`:

```python
def _grade_non_test_python(entry: AstIndexEntry) -> CoverageLedgerEntry:
    if entry.parse_failed or not entry.ast_eligible:
        return grade_entry(file_path=entry.file_path, proposed_depth=CoverageDepth.SKIPPED, claim_present=False)
    return grade_entry(
        file_path=entry.file_path,
        proposed_depth=CoverageDepth.AUDITED_DEEP,
        claim_present=True,   # ← FR6 presence proxy: EVERY clean-parsed non-test .py is deep. This is DF-1-7-B.
    )
```

The pipeline module docstring (§40-52, "V1 deep-coverage grading (LOCKED + documented)") states the
interim contract verbatim: "the pipeline grades each cleanly-parsed Python NON-test (source-under-test) file
`audited_deep` via `grade_entry(proposed_depth=AUDITED_DEEP, claim_present=True)` — the 1.2 claim-emitted
deep path (V1 records claim *presence*; AST-validating the claim's *truth* is Epic-6 FR7)." **6.2 makes the
truth-validation real and rewrites this docstring to the FR7 grounded contract.**

**The structural substrate already exists — REUSE it, do NOT re-parse (the no-fork keystone, §3.3 / AR7).**
The 1.4 tree-sitter AST index (`index/ast_index.py`) already produces, per file, an `AstIndexEntry` carrying
`definitions: tuple[Definition, ...]` (function/class defs with `kind`/`name`/`start_line`/`end_line` + an
`ast_span` token) and `edges: tuple[CodeEdge, ...]` (call/reference edges with `callee`/`line`). The 1.5
vacuous-path subset (`detectors/vacuous_test.py`) ALREADY reads these for TEST files to derive its two AST
facts (test→SUT reachability + assertion-target provenance). **6.2's validator consumes the SAME pre-built
`definitions`/`edges` for NON-TEST files — it does NOT re-parse source, does NOT add a second tree-sitter
call, does NOT add a `radon`/`ast`-stdlib parse.** This keeps determinism (one grammar version folded into
the cache key) and the single-serializer / no-fork discipline intact.

**The grading gate is the 1.2 `grade_entry` honesty keystone — EXTEND it, do not fork it.** `grade_entry`
already downgrades a claimless `AUDITED_DEEP → AUDITED_SHALLOW` (silence → shallow, FR6). FR7 adds the
SECOND, orthogonal downgrade condition: a present-but-UNGROUNDED claim also downgrades. **Decision (locked
below, DN-GROUNDED):** the cleanest, lowest-blast-radius form is to compute a pure `claim_grounded: bool`
in the validator and pass `claim_present = (claim_emitted AND claim_grounded)` into the EXISTING
`grade_entry` — so the existing "present → deep / absent → shallow" semantics carry the grounding result with
ZERO change to `coverage_ledger.py` (the frozen Epic-1 contract stays byte-identical). The validator is the
new pure module; the ledger is untouched. (An alternative — adding a `claim_grounded` parameter to
`grade_entry` — is rejected: it edits a frozen Epic-1 contract and a schema for marginal benefit; record the
rejection in Dev Notes.)

**The stack-agnostic `claim→validated?` interface (NFR-P2 — Python = impl #1).** The architecture mandates
(§84, §238): "AST = Python in V1 (`claim_emitted` proxy elsewhere), via a stack-agnostic `claim → validated?`
interface." The validator MUST expose this interface so a non-Python file (or an AST-ineligible/parse-failed
Python file — `ast_eligible=False`) routes to the `claim_emitted` PROXY (the V1 fallback: presence stands in
for grounding where AST grounding is unavailable), while a clean-parsed Python file routes to the REAL
Python AST-grounding impl (#1). V2 multi-language is then purely additive (a second impl behind the same
interface) — no re-architecture. The `ast_eligible` flag on `AstIndexEntry` is exactly this seam (1.4
docstring: "the stack-agnostic `claim → validated?` seam (NFR-P2)").

**The migration is the point — and it MUST be honest (the DF-1-7-B closure crux).** Removing the
over-grading WILL change `audited_deep` counts on real repos, hence the deep-% the 1.6 verdict gate reads
(`RELEASE_READY` ≥60% deep; `INSUFFICIENT_COVERAGE` <20% deep; `NOT_READY_FOR_RELEASE` between). A file that
was deep on presence-proxy and is NOT AST-groundable under FR7 now lands `audited_shallow`, lowering deep-%.
This is CORRECT (that is the over-grading being removed), but it means existing expectations change:
- **The signature-demo cartridge (`vacuous_basic`, 1.7 AC4).** SUT `calculator.py` is expected `audited_deep`
  (deep-% = 1/2 ≥ 20% floor → `NOT_READY_FOR_RELEASE` / BLOCKED 🔴, exit 2, blocking finding sorted first).
  Under FR7, `calculator.py` must be GENUINELY AST-groundable (it has a real `add`/`Calculator` definition →
  it IS groundable, so it STAYS `audited_deep` and the demo verdict is PRESERVED). **The dev MUST re-run the
  signature demo end-to-end and CONFIRM the cartridge verdict is unchanged (or, if a fixture's SUT is a
  trivial/constants-only module that is no longer groundable, update its expectation deliberately and
  document WHY).** The signature-demo moat (`GitHub green · Sonar green · APAA 🔴 tests appear vacuous`) must
  still reproduce.
- **Every existing `tests/apaa/` fixture/golden** whose ledger or verdict depends on a non-test Python file
  being `audited_deep` must be re-graded under FR7 and its expectation updated WITH a documented rationale
  (the AC4-honesty requirement below). A golden cache key / verdict that changes is an INTENTIONAL
  invalidation (the 5.1/5.3 documented-golden-regeneration lever), not a regression.

**The grounding rule MUST be a credible, conservative AST fact — not cry-wolf (R1 / CC #6 advisory-by-contract).**
The architecture's FR7 split (§141-151) is first-principles: a *credible* deep grade needs an AST fact, but
the bar must not over-downgrade (false `audited_shallow` is less harmful than a false 🔴, but a too-aggressive
downgrade tanks deep-% and lands spurious `INSUFFICIENT_COVERAGE`). **Decision (DN-GROUND-RULE, locked
below):** the V1 grounding fact is **structural-presence-of-auditable-definitions**: a non-test Python file's
deep claim is GROUNDED iff its AST entry exhibits ≥1 real `Definition` (a `function`/`class` the audit could
ground a claim against). A clean-parsed file with ZERO definitions (a pure-constants / re-export / `__all__`-
only / docstring-only / dunder-glue module) has nothing for a deep read to substantively examine → its deep
claim is UNGROUNDED → `audited_shallow`. This is conservative (it does not attempt to prove a SPECIFIC claim's
truth — that is the LLM-grounded deep pass + 6.4 Prosecutor; V1 grounds the STRUCTURE the claim is *about*),
deterministic (pure over pre-built `definitions`), zero-token, and stack-agnostic-ready. Record the rule + its
honest-limitation statement in the validator docstring and Dev Notes; it is the SAME honesty register the 1.5
subset uses ("what it can and cannot prove").

**Scope vs the rest of Epic 6 (explicit deferrals — do NOT pull forward).**
- **6.3 orphan/dead-code detector (FR12)** — flagging defs with no caller / no referencing requirement is a
  DETECTOR over the code graph; 6.2 only GRADES grounding, it does not emit orphan findings. The `edges`
  substrate 6.3 needs already exists (1.4); 6.2 must not build the orphan detector.
- **6.4 adversarial Prosecutor + cut-edge pass (FR19)** — challenging whether the ledger justifies the
  verdict + the `cross_partition` re-read + the verdict-moving-🔴 AST-corroboration-AND-Prosecutor-sign-off
  gate is 6.4. 6.2 grounds the COVERAGE grade; the Prosecutor consumes the resulting ledger. Do not build it.
- **6.5 defect-cartridge self-audit harness + holdout + clean controls (FR20)** — CI-asserted cartridges +
  AI-E5-2's mechanized fixture-shape-coverage check is 6.5. 6.2 updates the EXISTING signature-demo cartridge
  expectation; it does not build the harness.
- **6.6 precision replay harness + validation protocol (FR20/OI1 N=5)** — not 6.2.
- **6.7 HITL STOP/PROCEED + decision record (FR23/FR24)** — not 6.2.
- **The LIVE LLM-grounded deep pass.** V1's FR7 grounding is the DETERMINISTIC structural-AST fact above; it
  does NOT dispatch an LLM to verify each claim's specific truth (that richer grounding rides the 6.1 port +
  6.4 Prosecutor). 6.2 MAY exercise the 6.1 `DeepAuditSeam`/`FakeDispatch` to record a deep-audit
  `LLMRecording` (zero-token in tests) IF it cleanly feeds the grade, but it MUST NOT wire a real
  provider-backed LLM call into the pipeline default path (the pipeline must stay zero-token + deterministic;
  a live LLM run is gated/optional, never the default). **Decision (DN-V1-DETERMINISTIC):** keep the V1
  grading path PURE + zero-token (structural AST fact only); the LLM-recording-fed grounding is a documented
  forward seam, not a 6.2 default. This preserves NFR-D1/D2 (reproducible, zero-token-testable) for the
  Epic-7 dogfood.

**Carry-forward action items (CLAUDE.md §9.1 / L1-E11 — each 6.x story cites its AI-E5-* item).**
- **AI-E5-5 (process 🟠) — THE hard deliverable: close DF-1-7-B in 6.2.** This story IS that closure. The
  closure MUST be demonstrated RED against the interim over-grading shape (a test that, against the OLD
  `claim_present=True`-always path, grades an ungroundable file `audited_deep` — RED — then GREEN under the
  new validator that downgrades it). File the DF-1-7-B closure note append-only in `deferred-work.md`
  (AI-E5-4) — the entry currently lives ONLY in the 1-7 story line; 6.2 should back-fill it into the central
  register AND append the closure note (per AI-E5-4's "keep story-file copies as evidence; back-fill +
  close in the central register").
- **AI-E5-1 (test-infra 🟠) — the COMPLETE-THE-DECLARED-SET keystone-adequacy checklist (now at three
  levels).** Applied to 6.2's AST CONSTRUCT/grading-input set: enumerate the full set of AstIndexEntry shapes
  the validator must classify — **clean-parsed Python with ≥1 def (grounded→deep), clean-parsed Python with
  ZERO defs (ungrounded→shallow), parse_failed Python (skipped), ast_eligible=False non-Python (claim_emitted
  proxy), and a non-ASCII-bearing entry** — and demonstrate EACH member covered (RED-first where applicable).
  The retro names this explicitly: "apply … to 6.1's LLM no-crash matrix + **6.2's AST construct set** +
  6.4's Prosecutor."
- **AI-E5-1 no-crash leg (AR10 / NFR-R1).** The validator must NEVER raise out of the grading site: a
  malformed/empty/None entry, an entry with `parse_failed=True`, a `definitions`/`edges` tuple in any shape →
  a typed grade (SKIPPED / shallow / proxy), never an uncaught raise. NAMED handling, no bare `except`.
- **AI-E1-1 (test-infra 🟢) — non-ASCII / locale discipline (the Epic-1-FAIL class, standing).** A non-test
  Python file with a non-ASCII path / non-ASCII identifier in a `Definition.name` must grade + serialize +
  derive a stable key under `PYTHONIOENCODING=utf-8` (the single serializer is `ensure_ascii=False`). ≥1
  fixture carries a non-ASCII value.
- **AI-E5-4 (governance 🟢) — central defer register.** Back-fill DF-1-7-B into `deferred-work.md` (it is one
  of the un-back-filled story-line-only defers) AND append its closure note there; if 6.2 files a NEW defer,
  file it append-only with the six CC-3 fields.
- **AI-E5-7 (process 🟢) — keep the structural gates green + partial-reuse docstring precision.** The new
  validator must keep the no-web-imports gate (`apaa.* ⊬ fastapi/uvicorn/starlette`) and the no-LLM gate
  (the PURE seam `apaa.audit.deep_audit` ⊬ `minions_core.providers`) green — the validator is PURE (no
  provider import). When reuse is PARTIAL (consumes `definitions`/`edges`, composes `grade_entry`), narrate
  it precisely ("consumes the 1.4 pre-built AST entry; computes a pure grounding fact; composes the EXISTING
  `grade_entry`", not "reuses the AST index wholesale").
- **AI-E5-3 (process 🟠) — committed pre-`review` test-existence guard (now FOUR+ epics slipping).** NOT
  6.2's primary deliverable (6.5/6.6 + 6.1's import-isolation are the CI-touching moments), but 6.2 MUST
  honor the in-session test-existence discipline (the validator + its tests + the RED-then-green DF-1-7-B
  closure demo EXIST + pass before the `review` flip). Flag forward.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 6.2) + the architecture (FR7 split §141-151, §84/§238 NFR-P2,
> CC #6 advisory-by-contract) + the PRD (FR6/FR7 + the coverage-honesty mandate) + DF-1-7-B. Drivers:
> **APAA-FR-7** (validate a deep claim against source structure — Python AST in V1 — and downgrade an
> unverifiable claim), **APAA-FR-6** (the EXISTING claim-required `audited_deep` / silence→shallow keystone,
> extended-not-forked), **APAA-NFR-P2** (stack-agnostic `claim→validated?` interface; Python = impl #1;
> non-Python → `claim_emitted` proxy; V2 additive), **APAA-AR10** (a malformed/empty/parse-failed grading
> input → a typed grade, NEVER an uncaught raise), **APAA-NFR-D1/D2** (the grading path stays PURE +
> deterministic + zero-token — no LLM in the default path), **APAA-AR7/§3.3** (REUSE the 1.4
> `definitions`/`edges` BY IMPORT — no re-parse, no second tree-sitter/ast call; compose the EXISTING
> `grade_entry` — no ledger fork), **APAA-NFR-M1** (≤1200-line files), **APAA-NFR-M2** (frozen Epic-1..5
> contracts unchanged unless a documented intentional invalidation), **APAA-AR8** (the validator is PURE — no
> I/O, no clock, no LLM, no provider import, no float), **APAA-NFR-S1** (no source/secret bytes — cite
> `Definition` names/spans/counts, never source excerpts).
>
> **SCOPE FENCE — Tier-B, single-purpose, the DF-1-7-B closure.** This story delivers ONLY: (1) the pure FR7
> Python AST-grounding validator (a `claim→validated?` interface in `audit/deep_audit.py`, or a tightly-
> coupled pure sibling it owns) computing `claim_grounded: bool` over a non-test file's pre-built 1.4
> `AstIndexEntry`; (2) the stack-agnostic routing (Python clean-parse → real impl; non-Python /
> ast-ineligible / parse-failed → `claim_emitted` proxy / SKIPPED); (3) the pipeline `_grade_non_test_python`
> rewrite to call the validator and grade `audited_deep` ONLY when grounded (composing the EXISTING
> `grade_entry`), downgrading an ungrounded claim to `audited_shallow`; (4) the pipeline-docstring rewrite
> from the interim FR6-presence contract to the FR7 grounded contract; (5) the migration: re-grade + update
> the signature-demo cartridge + every affected `tests/apaa/` fixture/golden expectation WITH documented
> rationale, and re-run the signature demo end-to-end; (6) the DF-1-7-B closure (RED against the over-grading
> shape, then green) + the central-register back-fill + closure note. It does NOT build, and MUST NOT pull
> forward: the **orphan/dead-code detector** (6.3); the **adversarial Prosecutor + cut-edge pass** (6.4); the
> **cartridge self-audit harness + holdout + clean controls** (6.5); the **precision replay harness +
> validation protocol** (6.6); the **HITL STOP/PROCEED + decision record** (6.7); a **live provider-backed
> LLM call in the pipeline default path** (the V1 grounding is the deterministic structural AST fact; LLM-fed
> grounding is a documented forward seam — DN-V1-DETERMINISTIC); a **second tree-sitter / `ast` / `radon`
> parse** (REUSE the 1.4 entry); an **edit to the frozen `coverage_ledger.py` / `grade_entry` signature**
> (compose it as-is — DN-GROUNDED); a **new `.github/workflows` CI job**; a **new HTTP route / FastAPI
> surface / UI** (§3.7); a **new `cli.py` flag**.

**AC1 — A pure FR7 Python AST-grounding validator decides `claim_grounded` over a non-test file's pre-built 1.4 AST entry (FR7 / AR8 / §3.3 no re-parse)**
**Given** the validator (in `apaa/audit/deep_audit.py` or a pure sibling it owns) exposing a stack-agnostic
`claim→validated?` interface — e.g. `is_deep_claim_grounded(entry: AstIndexEntry) -> bool` (or a small frozen
result the interface returns)
**When** it evaluates a cleanly-parsed (`ast_eligible=True`, `parse_failed=False`) NON-test Python file's
1.4 `AstIndexEntry`
**Then** it returns `claim_grounded=True` iff the entry exhibits the V1 grounding fact —
**≥1 real `Definition` (function/class) the audit can ground a deep claim against** (DN-GROUND-RULE) — and
`False` for a clean-parsed module with ZERO definitions (constants-only / re-export / `__all__`-only /
docstring-only / dunder-glue)
**And** it consumes the PRE-BUILT `entry.definitions` / `entry.edges` (the 1.4 substrate the 1.5 subset
already reads for test files) — it does NOT re-parse source, add a second tree-sitter call, or import
`ast`/`radon` for a second parse (AR7 / §3.3 no-fork); it is PURE (no I/O, no clock, no LLM, no provider
import, no float — AR8) and NEVER raises on a malformed/empty/None/parse-failed entry (AR10 — a degraded
entry routes to a typed non-deep grade).

**AC2 — The pipeline grades `audited_deep` ONLY when grounded; an ungrounded claim downgrades to `audited_shallow` (FR7 / FR6 extend-not-fork / DF-1-7-B closure)**
**Given** `pipeline.py::_grade_non_test_python` (the DF-1-7-B over-grading site at the 1.7-recorded
`pipeline.py:149`)
**When** it grades a cleanly-parsed non-test Python file
**Then** it calls the AC1 validator and grades `audited_deep` ONLY when the claim is **grounded** — concretely
by passing `claim_present = (claim_emitted AND claim_grounded)` into the EXISTING 1.2 `grade_entry` (so the
existing `present→deep / absent→shallow` semantics carry the grounding result with ZERO change to
`coverage_ledger.py` — DN-GROUNDED); an UNGROUNDED claim (clean-parse, zero defs) is recorded
`audited_shallow` (silence/insufficiency → downgrade, FR7), and a `parse_failed` / `ast_eligible=False`
file stays `skipped` exactly as today
**And** a test demonstrates the closure RED-then-green: against the INTERIM shape (`claim_present=True`
always), an ungroundable file is graded `audited_deep` (RED — the over-grading); under the new validator it
downgrades to `audited_shallow` (GREEN) — the AI-E5-5 / DF-1-7-B closure proof.

**AC3 — The stack-agnostic `claim→validated?` interface routes non-Python (and AST-ineligible) files to the `claim_emitted` proxy; V2 is additive (NFR-P2 / §84 / §238)**
**Given** the validator interface
**When** a NON-Python file (`ast_eligible=False`, `parse_failure_reason="non_python"`) or an AST-ineligible /
parse-failed Python file is encountered
**Then** it routes to the `claim_emitted` PROXY (presence stands in for grounding where Python AST grounding
is unavailable) — Python clean-parse is impl #1 of the interface, and a future language impl is purely
additive behind the SAME interface (no re-architecture) — and a non-Python file's grade is UNCHANGED from
today (it is still `skipped` in the denominator per the existing `_detect_per_file` non-Python path; the
proxy governs the deep-claim-bearing path, not the skipped-non-Python path)
**And** the interface + its impl-selection seam is the `ast_eligible` flag (1.4), documented as the NFR-P2
seam — no new flag invented.

**AC4 — The migration is HONEST: re-grade + update the signature-demo cartridge + affected fixtures/goldens with documented rationale; re-run the signature demo (the DF-1-7-B closure crux)**
**Given** removing the over-grading changes `audited_deep` counts → deep-% → potentially verdicts on real
repos AND on existing fixtures
**When** the new grading lands
**Then** the dev re-runs the signature-demo cartridge (`vacuous_basic`, 1.7 AC4) end-to-end and CONFIRMS its
verdict: `calculator.py` has real definitions → it STAYS `audited_deep` → deep-% = 1/2 ≥ 20% →
`NOT_READY_FOR_RELEASE` (BLOCKED 🔴, exit 2, blocking finding sorted first) is PRESERVED, and the signature
moat line (`GitHub green · Sonar green · APAA 🔴 tests appear vacuous`) still reproduces; if any
fixture's SUT is a trivial/constants-only module that is no longer groundable, its expectation is updated
DELIBERATELY with a documented rationale (not silently broken)
**And** EVERY `tests/apaa/` fixture / golden whose ledger / verdict / cache-key depends on a non-test Python
file being `audited_deep` is re-graded under FR7 and its expectation updated WITH a documented rationale in
the Dev Agent Record (an intentional-invalidation note for any changed golden — the 5.1/5.3 documented-golden
lever); the change is NEVER a silent expectation edit.

**AC5 — Complete-the-declared-set + no-crash matrix over the AST construct/grading-input set, each RED-first where applicable (AI-E5-1 / AR10)**
**Given** the full DECLARED set of grading-input shapes the validator must classify
**When** the validator is tested
**Then** EACH member is covered: (a) clean-parsed Python, ≥1 def → grounded → `audited_deep`; (b) clean-parsed
Python, ZERO defs → ungrounded → `audited_shallow` (the DF-1-7-B closure member, RED-first vs the over-grading
shape); (c) `parse_failed=True` Python → `skipped`; (d) `ast_eligible=False` non-Python → `claim_emitted`
proxy (non-deep, unchanged grade); (e) a malformed / empty-`definitions` / empty-`edges` / None-ish entry →
a typed non-deep grade, NEVER an uncaught raise (the no-crash leg — NAMED handling, no bare `except`); (f) a
non-ASCII path / non-ASCII `Definition.name` entry → grades + serializes + derives a stable key under
`PYTHONIOENCODING=utf-8` (AI-E1-1)
**And** the enumeration is explicit in the test module (the complete-the-declared-set discipline — the
practice that caught 3.4 / 4.2 / 5.1).

**AC6 — Determinism, purity, secret-containment, and the frozen contracts hold; ≤1200 lines; mypy (NFR-D1/D2 / AR8 / NFR-S1 / NFR-M1/M2)**
**Given** the new validator + the rewritten grading site + the migrated fixtures
**When** the suite runs under `PYTHONIOENCODING=utf-8`
**Then** the grading path stays PURE + deterministic + ZERO-token (no LLM in the pipeline default path —
DN-V1-DETERMINISTIC; NFR-D1/D2); the validator imports NO provider code and NO FastAPI (the no-LLM gate
`apaa.audit.deep_audit ⊬ minions_core.providers` and the web-stack gate stay green — extend, do not fork,
`_MODULES_UNDER_GUARD`); no source/secret bytes enter any grade/finding (cite `Definition` names / `ast_span`
/ counts, NEVER source excerpts — NFR-S1); the frozen Epic-1..5 contracts show NO working-tree diff
(`coverage_ledger.py` / `grade_entry` byte-identical — DN-GROUNDED; `store/{canonical,envelope}.py`,
`cache/key.py`, `ledger/recording.py`, `index/ast_index.py`, `verdict/*`, `models.py` unchanged), EXCEPT the
documented intentional fixture/golden re-grades from AC4
**And** each new/modified file is ≤1200 lines (NFR-M1); `mypy` is clean on the new/modified modules; any
credit/ratio-shaped value is `Fraction`/str, never float (AR4 — though 6.2's grounding fact is a boolean
count, no ratio).

**AC7 — No regression / no scope creep; structural gates green; mypy clean; the pre-`review` test-existence precondition (AI-E5-7 / AI-E5-3 / the thin-slice discipline)**
**Given** the new validator + the rewritten grading site + the migrated fixtures/goldens + their tests
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the 1032-green Epic-5 baseline + the 6.1 audit tests + the new 6.2 grounding tests, with ONLY the
AC4-documented fixture/golden re-grades changed), and the import-isolation gates (web-stack + no-LLM, both
extended-not-forked), the single-serializer AST gate (the validator adds NO `json.dumps`/hasher/second
parse), and the file-size gate stay green; `mypy` is clean
**And** the frozen Epic-1..5 contracts show NO working-tree diff beyond the documented AC4 re-grades; NO new
`.apaa/` write path is introduced (the grade flows through the EXISTING `_detect_per_file` →
`CoverageLedger.build` → persist fold — the persisted ledger simply reflects the new grades), NO `cli.py`
flag, NO HTTP route, NO new CI job
**And** the new test files cite their `APAA-FR-7` / `APAA-FR-6` / `APAA-NFR-P2` / `APAA-AR10` drivers in the
module docstring + the locked test area / index; the mandatory artifacts EXIST + pass + the DF-1-7-B
RED-then-green closure is documented BEFORE the story flips to `status: review` (AI-E5-3 / AI-E2-1
test-existence discipline). **Test area `APAA-AUDIT`** (`TC-APAA-AUDIT-001-NN` — confirm/lock the next free
index after 6.1's tests in the module docstring); the pipeline-level migration assertions may use the
existing `APAA-PIPELINE` area.

## Tasks / Subtasks

- [x] **Task 0 — Re-read the REAL surfaces; LOCK the grounding rule, the grade-gate composition, and the migration set** (AC: 1, 2, 4)
  - [x] Re-read `minions_core/apaa/pipeline.py::_grade_non_test_python` (the DF-1-7-B site) + the module
        docstring §40-52 ("V1 deep-coverage grading"). LOCK: the rewrite calls the validator and grades
        `audited_deep` ONLY when grounded; it composes the EXISTING `grade_entry` (DN-GROUNDED — no ledger edit).
  - [x] Re-read `minions_core/apaa/index/ast_index.py` (`Definition` = `name/kind/start_line/end_line` +
        `ast_span`; `CodeEdge` = `callee/line`; `AstIndexEntry` = `file_path/ast_eligible/parse_failed/
        parse_failure_reason/definitions/edges`). LOCK: the validator CONSUMES the pre-built `definitions`/
        `edges` — NO re-parse, NO second tree-sitter/`ast`/`radon` call (§3.3 / AR7).
  - [x] Re-read `minions_core/apaa/ledger/coverage_ledger.py::grade_entry` (the `proposed_depth=AUDITED_DEEP,
        claim_present=...` → silence-downgrade keystone). LOCK DN-GROUNDED: pass `claim_present =
        (claim_emitted AND claim_grounded)`; do NOT add a parameter; `coverage_ledger.py` stays byte-identical.
  - [x] Re-read `minions_core/apaa/detectors/vacuous_test.py` (the 1.5 vacuous-path AST subset: how it derives
        test→SUT reachability + assertion-target provenance over `definitions`/`edges`, the honest
        "what it can/cannot prove" register). REUSE the same substrate + register style; do NOT fork the
        detector (6.2 grades NON-test files; the vacuous detector scores TEST files — distinct concerns).
  - [x] Re-read `minions_core/apaa/audit/deep_audit.py` (6.1's thin `DeepAuditSeam` + `build_closure_from_
        recording`). LOCK: 6.2 adds the PURE validator here (or a tightly-owned pure sibling); it stays
        provider-free (the no-LLM gate); the LLM-fed grounding is a documented forward seam, NOT the default
        (DN-V1-DETERMINISTIC).
  - [x] Re-read `minions_core/apaa/verdict/verdict_gate.py` (the deep-% gate: `RELEASE_READY` ≥60%,
        `INSUFFICIENT_COVERAGE` <20%, `NOT_READY_FOR_RELEASE` between). Understand the migration impact on
        deep-% so AC4's re-grading is principled.
  - [x] Enumerate the MIGRATION SET: grep `tests/apaa/` for fixtures/goldens that assert a non-test Python
        file `audited_deep` / a specific deep-% / a verdict / a cache-key golden that depends on the grading.
        Start from the signature-demo cartridge (`vacuous_basic`, 1.7 AC4). Record the set in Dev Notes.
- [x] **Task 1 — Build the pure FR7 AST-grounding validator (the `claim→validated?` interface)** (AC: 1, 3, 6)
  - [x] In `audit/deep_audit.py` (or a pure sibling): `is_deep_claim_grounded(entry: AstIndexEntry) -> bool`
        (or a small frozen result) — the stack-agnostic interface. Python clean-parse = impl #1: GROUNDED iff
        `len(entry.definitions) >= 1` (DN-GROUND-RULE — the V1 structural-presence fact). PURE, no I/O / clock /
        LLM / provider import / float; NEVER raises on a degraded entry (AR10).
  - [x] The stack-agnostic routing: non-Python (`ast_eligible=False`) / parse-failed → `claim_emitted` proxy /
        non-deep (no grounding attempted; presence governs). Document Python = impl #1, V2 additive (NFR-P2).
  - [x] Docstring: the grounding rule + its HONEST limitation ("grounds the STRUCTURE a claim is about, not a
        specific claim's truth — that is the LLM-grounded deep pass + 6.4 Prosecutor"), the `APAA-FR-7` /
        `APAA-NFR-P2` drivers, the `APAA-AUDIT` area + next free index.
- [x] **Task 2 — Rewrite the pipeline grading site + the module docstring** (AC: 2, 7)
  - [x] Rewrite `_grade_non_test_python`: keep the `parse_failed or not ast_eligible → SKIPPED` leg; for a
        clean-parsed file, compute `claim_grounded = is_deep_claim_grounded(entry)` and call `grade_entry(
        proposed_depth=AUDITED_DEEP, claim_present=(claim_emitted AND claim_grounded))` so an ungrounded claim
        downgrades to `audited_shallow` (DN-GROUNDED). NO edit to `coverage_ledger.py`.
  - [x] Rewrite the pipeline module docstring §40-52 from the interim FR6-presence contract to the FR7
        grounded contract (the V1 deep numerator is GROUNDED non-test Python, not every clean-parsed file);
        note DF-1-7-B CLOSED here.
- [x] **Task 3 — The migration: re-grade fixtures/goldens + re-run the signature demo** (AC: 4)
  - [x] Re-run the signature-demo cartridge end-to-end; CONFIRM `calculator.py` stays `audited_deep` (real
        defs) → verdict PRESERVED (`NOT_READY_FOR_RELEASE`, exit 2, blocking 🔴 first); the moat line
        reproduces. Document the confirmation.
  - [x] Walk the Task-0 migration set; re-grade each under FR7; update each changed expectation DELIBERATELY
        with a documented rationale (an intentional-invalidation note for any changed golden cache-key/verdict).
        NEVER a silent expectation edit.
- [x] **Task 4 — Tests: complete-the-declared-set + no-crash + non-ASCII + the DF-1-7-B RED-then-green closure** (AC: 2, 5)
  - [x] New `tests/apaa/test_deep_audit_grounding.py` (area `APAA-AUDIT`): the full declared set (grounded /
        ungrounded-zero-def / parse-failed / non-Python-proxy / malformed-no-crash / non-ASCII) — each member,
        RED-first where applicable. The (b) ungrounded-zero-def member is the DF-1-7-B closure: RED against the
        `claim_present=True`-always shape, GREEN under the validator.
  - [x] A pipeline-level assertion (area `APAA-PIPELINE`): a repo whose only non-test Python file is a
        zero-def constants module no longer clears the 20% floor the way the over-grading did (the verdict
        migration is observable), demonstrated against the interim shape.
- [x] **Task 5 — Run + mypy + gates + the central-register defer back-fill + the pre-`review` precondition** (AC: 6, 7)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
        all pass (1032 baseline + 6.1 + the new 6.2 tests; ONLY the AC4-documented re-grades changed). `mypy`
        clean on the new/modified modules.
  - [x] Confirm NO working-tree diff to the frozen Epic-1..5 surfaces beyond the documented AC4 re-grades
        (`coverage_ledger.py`/`grade_entry`/`ast_index.py`/`cache/key.py`/`verdict/*` byte-identical). Confirm
        the no-LLM + web-stack + single-serializer + file-size gates green (extend `_MODULES_UNDER_GUARD` only
        if a new module was added). NO `cli.py`/HTTP/CI-job change.
  - [x] **AI-E5-4 / AI-E5-5 / DN-DEFER:** back-fill DF-1-7-B into `_bmad-output/design-artifacts/ArgusAgent/
        deferred-work.md` (the central register — it currently lives only in the 1-7 story line; keep the
        story-file copy as evidence) AND append the closure note (CLOSED 2026-… by story 6.2; the RED-then-
        green proof, the migration confirmation). If a NEW defer is filed, the six CC-3 fields.
  - [x] **AI-E5-3 / AI-E2-1 GATE:** the mandatory artifacts (the validator + the rewritten grading site + the
        new tests with the DF-1-7-B RED-then-green closure + the migration confirmation) EXIST + pass BEFORE
        the `review` flip; the Dev Agent Record is filled completely (no blank placeholders), incl. the AC4
        migration rationale.

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **FR7 = validate a deep claim against source STRUCTURE and downgrade an unverifiable one (FR7, epic Story
  6.2 AC, §141-151).** "It checks the claim against the multi-construct AST; an unverifiable claim downgrades
  to `audited_shallow` (silence/insufficiency → downgrade)." V1's grounding fact is DETERMINISTIC and
  STRUCTURAL: a non-test Python file's deep claim is grounded iff its 1.4 AST entry has ≥1 real `Definition`
  (DN-GROUND-RULE). This is the *credible, conservative* bar the FR7-split first-principles demands — it does
  not over-downgrade (it grounds the structure a claim is *about*) and it is not cry-wolf (a real module with
  real defs stays deep). The richer "prove THIS claim's truth" grounding rides the 6.1 LLM port + the 6.4
  Prosecutor; it is NOT 6.2 (DN-V1-DETERMINISTIC).
- **Extend `grade_entry`, do NOT fork the ledger (DN-GROUNDED — the lowest-blast-radius decision).** The 1.2
  `grade_entry` already downgrades a claimless `AUDITED_DEEP → AUDITED_SHALLOW`. FR7's second downgrade
  (present-but-ungrounded) is carried by passing `claim_present = (claim_emitted AND claim_grounded)` — so
  `coverage_ledger.py` stays BYTE-IDENTICAL (frozen Epic-1 contract, NFR-M2). REJECTED alternative: adding a
  `claim_grounded` parameter to `grade_entry` (edits a frozen contract + schema for marginal benefit). The
  validator is the new pure surface; the ledger is untouched.
- **REUSE the 1.4 AST entry — NO re-parse (§3.3 / AR7 / the no-fork keystone).** The validator consumes the
  pre-built `entry.definitions` / `entry.edges` (the SAME substrate the 1.5 vacuous subset reads for test
  files). It does NOT call tree-sitter again, NOT import `ast`/`radon` for a second parse. One grammar
  version, one parse, folded once into the cache key — determinism + the single-serializer discipline intact.
- **Stack-agnostic `claim→validated?` interface — Python = impl #1, V2 additive (NFR-P2 / §84 / §238).** The
  `ast_eligible` flag (1.4) is the impl-selection seam: clean-parsed Python → the real Python AST-grounding
  impl; everything else → the `claim_emitted` proxy. A future language is a second impl behind the same
  interface — no re-architecture. Do NOT invent a new flag.
- **The migration must be HONEST (the DF-1-7-B closure crux / AC4).** Removing the over-grading lowers
  `audited_deep` counts → deep-% → can flip verdicts. This is CORRECT. But every changed expectation
  (signature-demo cartridge, fixtures, goldens, cache keys, verdicts) is re-graded and updated DELIBERATELY
  with a documented rationale (the 5.1/5.3 intentional-invalidation lever) — never a silent edit. The
  signature-demo moat must still reproduce (`calculator.py` has real defs → stays deep → BLOCKED 🔴 preserved).
- **No-crash matrix → typed grade, NEVER an uncaught raise (AR10 / NFR-R1 / AI-E5-1).** A malformed / empty /
  None / parse-failed grading input degrades to a typed non-deep grade (SKIPPED / shallow / proxy). NAMED
  handling, no bare `except: pass`. Demonstrate each member RED-first where applicable (the complete-the-
  declared-set discipline that caught 3.4 / 4.2 / 5.1).
- **No source/secret bytes (NFR-S1 / CC #5 producer-side redaction).** A grade/finding cites `Definition`
  names / `ast_span` tokens / counts — NEVER source excerpts or secret values. The grounding fact is a count
  over already-redacted AST metadata; no new `.apaa/` write path is introduced (the grade flows through the
  EXISTING persist fold).
- **PURE + deterministic + zero-token (NFR-D1/D2 / AR8).** The validator is a pure fold over the AST entry —
  no I/O, no clock, no LLM, no provider import, no float. The pipeline default grading path stays zero-token
  (DN-V1-DETERMINISTIC) so the Epic-7 dogfood verdict is reproducible. A non-ASCII entry derives a stable key
  under `PYTHONIOENCODING=utf-8` (`ensure_ascii=False` single serializer — AI-E1-1).
- **Frozen contracts unchanged (AR8 / NFR-M2).** Verify NO working-tree diff to `store/{canonical,envelope}.py`,
  `cache/key.py`, `ledger/recording.py`, `ledger/coverage_ledger.py` (+ `grade_entry`), `index/ast_index.py`,
  `verdict/*`, `models.py` — EXCEPT the documented AC4 fixture/golden re-grades. `_MODULES_UNDER_GUARD` is
  EXTENDED (not forked) only if a new module is added.

### Project Structure Notes

- **The validator lives in `minions_core/apaa/audit/deep_audit.py`** (6.1's module — the natural home for the
  deep-claim validator) OR a tightly-owned pure sibling (`audit/grounding.py`) if `deep_audit.py` would
  exceed clean cohesion / the line limit. Either way it is PURE-of-providers (the no-LLM gate) and consumes
  the 1.4 `AstIndexEntry`.
- **The pipeline grading site is `pipeline.py::_grade_non_test_python`** (the DF-1-7-B locator). The rewrite
  is surgical: call the validator, compose `grade_entry`, rewrite the docstring. The persist/verdict fold is
  unchanged (the ledger simply carries the new grades).
- **Test area `APAA-AUDIT`** (`TC-APAA-AUDIT-001-NN`) for the validator (confirm the next free index after
  6.1's `test_llm_dispatch_port.py` / `test_minions_llm_adapter.py`); the pipeline migration assertions may
  use `APAA-PIPELINE`. New test: `tests/apaa/test_deep_audit_grounding.py`. Lock the index in the module
  docstring.
- **DO NOT** add a `cli.py` flag, an HTTP route, a `.github/workflows` CI job, a second parser, or any
  `.apaa/` write path. DO NOT build 6.3 orphan / 6.4 Prosecutor / 6.5 cartridge-harness / 6.6 precision /
  6.7 HITL. DO NOT wire a live provider-backed LLM call into the pipeline default path.

### Migration & verdict-impact notes (AC4 — read before changing any fixture)

- The 1.6 verdict gate reads deep-% from `CoverageLedger.deep_count() / total()`: `RELEASE_READY` at ≥60%
  (inclusive), `INSUFFICIENT_COVERAGE` at <20% (strict), `NOT_READY_FOR_RELEASE` between. Lowering deep-% by
  downgrading ungrounded files can move a repo toward `NOT_READY_FOR_RELEASE` or `INSUFFICIENT_COVERAGE`.
- The signature-demo cartridge `vacuous_basic`: SUT `calculator.py` (real `add` / `Calculator` defs →
  GROUNDED → stays `audited_deep`) + the planted vacuous test (`audited_shallow`) → deep-% = 1/2 ≥ 20% →
  `NOT_READY_FOR_RELEASE` (BLOCKED 🔴), exit 2 — **PRESERVED under FR7**. Confirm empirically; do not assume.
- For any fixture whose SUT is a trivial/empty/constants-only module, the new grade is `audited_shallow` and
  the verdict may change — update the expectation with a one-line documented rationale (an intentional
  invalidation), and regenerate any dependent golden cache-key/verdict deterministically.

### References

- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Story-6.2] — the FR7 grounding AC (multi-construct AST; unverifiable claim downgrades) + the NFR-P2 stack-agnostic proxy AC.
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md] — §141-151 the FR7 split (R1, first-principles: a credible deep grade needs an AST fact; the vacuous-path subset is Tier-A, general multi-construct AST-grounding is Tier-B); §84/§238 the stack-agnostic `claim→validated?` interface (Python impl #1, `claim_emitted` proxy elsewhere); CC #6 advisory-by-contract (no over-downgrade / no cry-wolf); §442 `deep_audit.py` "AST-grounded `audited_deep` claims."
- [Source: minions_core/apaa/pipeline.py] — `_grade_non_test_python` (the DF-1-7-B over-grading site, recorded `pipeline.py:149`) + the module docstring §40-52 (the interim FR6-presence contract to rewrite).
- [Source: minions_core/apaa/index/ast_index.py] — `Definition` / `CodeEdge` / `AstIndexEntry` (`ast_eligible`/`parse_failed`/`definitions`/`edges`) — the pre-built substrate the validator REUSES (no re-parse).
- [Source: minions_core/apaa/ledger/coverage_ledger.py] — `grade_entry` (the silence→shallow keystone to compose, DN-GROUNDED; do NOT edit) + `CoverageDepth` + `deep_count`.
- [Source: minions_core/apaa/detectors/vacuous_test.py] — the 1.5 vacuous-path AST subset (test→SUT reachability + assertion-target provenance over `definitions`/`edges`; the honest "what it can/cannot prove" register to mirror).
- [Source: minions_core/apaa/audit/deep_audit.py] — 6.1's thin `DeepAuditSeam` + `build_closure_from_recording` (the seam this story's validator joins; stays provider-free).
- [Source: minions_core/apaa/verdict/verdict_gate.py] — the deep-% gate thresholds (the migration-impact surface for AC4).
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/1-7-cli-invocation-contract-pipeline-signature-demo-vacuous-test-cartridge.md] — the interim deep-grading decision (LOCKED) + DF-1-7-B's filing + the signature-demo cartridge (AC4).
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/6-1-llm-dispatch-port-minions-orchestrator-adapter.md] — the 6.1 handoff (deep-audit seam built; AST-grounding logic explicitly fenced to 6.2 / DF-1-7-B).
- [Source: _bmad-output/design-artifacts/ArgusAgent/epic-5-retro-2026-06-29.md] — §6/§7/§9 AI-E5-5 (close DF-1-7-B in 6.2 as a HARD deliverable, RED against the over-grading shape) + AI-E5-1 (complete-the-declared-set over the AST construct set) + AI-E5-4 (central defer back-fill) + AI-E5-7 (structural gates / partial-reuse precision).
- [Source: _bmad-output/design-artifacts/ArgusAgent/deferred-work.md] — the central APAA defer register (back-fill DF-1-7-B here + append the closure note — AI-E5-4 / AI-E5-5).

## Dev Agent Record

### Context Reference

- Story spec: this file. Builds on done Stories 1.1–1.7 + 2.x–5.x + 6.1 (REUSE by import, no fork — §3.3).

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, mode=implement).

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/test_deep_audit_grounding.py tests/apaa/test_no_web_imports.py -q` → 26 passed.
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/test_pipeline_signature_demo.py -q` → 40 passed.
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` → 1083 passed, 1 skipped, 4 subtests passed (135s). (Epic-5 baseline 1032 + 6.1 + the new 6.2 grounding tests; ONLY the AC4-documented re-grades, which net to ZERO cartridge verdict changes.)
- `python -m mypy minions_core/apaa/audit/grounding.py` → Success: no issues found. (`mypy` on `pipeline.py` surfaces only the 2 PRE-EXISTING `radon.*` missing-stub import-untyped notes in the transitively-imported `tool_runner.py` — NOT in 6.2's new/modified code.)

### Completion Notes List

- **FR7 validator (AC1/AC3/AC6).** Added the PURE `minions_core/apaa/audit/grounding.py::is_deep_claim_grounded(entry)` — the stack-agnostic `claim → validated?` interface. Python clean-parse = impl #1: GROUNDED iff `len(entry.definitions) >= 1` (DN-GROUND-RULE). A non-Python / AST-ineligible / parse-failed / malformed / `None` entry returns `False` (the `claim_emitted` proxy / typed non-deep — AR10, NAMED `isinstance` guard, no bare `except`). PURE: no I/O / clock / LLM / provider import / float; consumes the pre-built 1.4 `definitions` — no re-parse (AR7/§3.3). The honest-limitation register ("grounds the STRUCTURE a claim is about, not a specific claim's truth — that is the 6.1 LLM port + 6.4 Prosecutor") is in the module docstring.
- **Pipeline rewrite (AC2/AC7).** `pipeline.py::_grade_non_test_python` keeps the `parse_failed or not ast_eligible → SKIPPED` leg; for a clean-parsed file it computes `claim_grounded = is_deep_claim_grounded(entry)` and calls `grade_entry(proposed_depth=AUDITED_DEEP, claim_present=(claim_emitted AND claim_grounded))` (DN-GROUNDED). `coverage_ledger.py`/`grade_entry` UNCHANGED (verified byte-identical). The module docstring §40-52 was rewritten from the interim FR6-presence contract to the FR7 grounded contract (DF-1-7-B noted CLOSED); the NFR-D2 driver note now records the ONE allowed `apaa.audit` import (the pure provider-free validator).
- **REJECTED alternative (DN-GROUNDED).** Adding a `claim_grounded` parameter to `grade_entry` was rejected — it edits a frozen Epic-1 contract + schema for marginal benefit; the `claim_present=(claim_emitted AND claim_grounded)` composition carries the grounding result with ZERO ledger change.
- **Migration HONEST (AC4) — net-zero cartridge verdict change, deliberate.** Walked the migration set: the cartridge SUTs (`vacuous_basic/src/calculator.py`, `clean_control/src/{adder,multiplier}.py`, `evidence_sentinel`/`hardcoded_secret`/`secret_canary` `config.py` + `auth/guard.py` + `café/модуль_секрет.py`, `nonascii_unicode/src/café_calc.py`, `tool_breadth/...`) ALL carry ≥1 real `def`/`class` → ALL stay GROUNDED → `audited_deep`. So NO cartridge verdict / golden / cache-key changed (the signature-demo moat is PRESERVED — `calculator.py` stays deep → deep-% 1/2 → NOT_READY_FOR_RELEASE/exit 2; confirmed empirically by the new TC-APAA-PIPELINE-001-40, not assumed). The ledger unit tests (`test_coverage_ledger.py` / `test_coverage_report.py` / `test_critical_subsystems.py`) call `grade_entry` directly with synthetic paths — they do NOT route through `_grade_non_test_python`, so they are unaffected. Conclusion: NO fixture/golden re-grade was needed; the honest re-grade confirms zero affected expectations. (The migration would change verdicts only for a clean-parse zero-def module, which no cartridge contains — exercised synthetically by the new TC-APAA-PIPELINE-001-41.)
- **DF-1-7-B closure RED-then-green (AC2/AC5).** TC-APAA-AUDIT-001-50 demonstrates the closure: the interim `claim_present=True`-always shape grades a zero-def module `audited_deep` (RED — the over-grading) → the validator finds it ungrounded → `audited_shallow` (GREEN). Complete-the-declared-set + no-crash matrix + non-ASCII covered (TC-APAA-AUDIT-001-46..58); the pipeline-level migration is observable (TC-APAA-PIPELINE-001-41).
- **Gates (AC6/AC7).** Web-stack + no-LLM import gates EXTENDED-not-forked: `grounding` added to `_MODULES_UNDER_GUARD` + a provider-free assertion (TC-APAA-AUDIT-001-47); `test_pipeline_is_zero_token` now uses a pipeline-scoped forbidden set (providers + the LLM-dispatch audit modules ports/deep_audit/minions_llm_adapter) that ALLOWS the pure grounding validator — the strict `_LLM_FORBIDDEN_PREFIXES` is preserved for any caller. Frozen Epic-1..5 contracts show NO working-tree diff (verified via `git diff` on coverage_ledger/ast_index/cache-key/store/verdict/models). `grounding.py` 90 lines, `pipeline.py` 1190 lines (≤1200, NFR-M1). NO `cli.py`/HTTP/CI-job/second-parser/`.apaa/`-write change. The grounding fact is a `bool`, no float (AR4).
- **AI-E5-4 central-register back-fill.** DF-1-7-B back-filled into `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (it previously lived only in the 1-7 story line) AND the closure note appended (append-only; the story-file copy retained as evidence). No NEW defer filed by 6.2.

### File List

- `minions_core/apaa/audit/grounding.py` (NEW — the PURE FR7 AST-grounding validator)
- `minions_core/apaa/pipeline.py` (MODIFIED — `_grade_non_test_python` rewrite + docstring §40-52 + NFR-D2 note + import)
- `tests/apaa/test_deep_audit_grounding.py` (NEW — TC-APAA-AUDIT-001-46..58: declared set + no-crash + non-ASCII + DF-1-7-B RED-then-green)
- `tests/apaa/test_pipeline_signature_demo.py` (MODIFIED — TC-APAA-PIPELINE-001-40 moat-preserved + -41 verdict-migration observable)
- `tests/apaa/test_no_web_imports.py` (MODIFIED — `_MODULES_UNDER_GUARD` + pipeline-scoped no-LLM carve-out + TC-APAA-AUDIT-001-47)
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (APPENDED — DF-1-7-B back-fill + closure note, AI-E5-4)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (status flip)

## Senior Developer Review (AI)

**Reviewer:** Code-review gate (claude-opus-4-8, adversarial). **Date:** 2026-06-29. **Iteration:** 1.
**Outcome:** APPROVE — VERDICT **pass** → status `done`.

### Summary

Story 6.2 delivers FR7 Python AST-grounding and genuinely CLOSES the long-carried 🟡 DF-1-7-B
(flagged across 4 retros). The new PURE `audit/grounding.py::is_deep_claim_grounded` is the
stack-agnostic `claim → validated?` interface (Python impl #1); the pipeline grades `audited_deep`
ONLY when grounded via `claim_present=(claim_emitted AND claim_grounded)` into the UNCHANGED
`grade_entry`. The over-grading is genuinely removed (not relabelled), the ledger is byte-identical,
the migration is honest, and the implementation is clean, pure, zero-token, and well-tested.

### Adversarial findings (the four high-stakes vectors)

- **DF-1-7-B ACTUALLY CLOSED (PASS).** The grounding fact is a REAL behavioral improvement over the
  1-7 claim-presence proxy, not a relabel. TC-APAA-AUDIT-001-50 is a genuine RED-then-green closure:
  the interim `claim_present=True`-always shape grades a zero-def module `audited_deep` (RED — the
  bug), the FR7 validator downgrades it to `audited_shallow` (GREEN). The observable population that
  now downgrades is proven end-to-end through the REAL pipeline by TC-APAA-PIPELINE-001-41: a
  zero-def-only repo flips from clearing the floor to `INSUFFICIENT_COVERAGE`/exit 3. Confirmed: a
  clean-parse Python file with no real definitions now downgrades to `audited_shallow`.
- **LEDGER BYTE-IDENTICAL (DN-GROUNDED) (PASS).** `coverage_ledger.py::grade_entry` signature is
  UNCHANGED (`file_path, proposed_depth, claim_present, recording_ids, partition_id`); the grounding
  is folded via the `claim_present` boolean composition. No frozen-surface edit; no new parameter.
- **HONEST VERDICT MIGRATION (AC4) (PASS).** The signature-demo moat is preserved for the RIGHT
  reason: TC-APAA-PIPELINE-001-40 asserts EMPIRICALLY (not assumed) that `calculator.py` has real
  defs → stays `audited_deep` → `counts[AUDITED_DEEP] == 1`, `deep_ratio == 1/2`,
  `NOT_READY_FOR_RELEASE`/exit 2 — the moat reproduces because the file is genuinely groundable, not
  by gaming. No test/golden was silently weakened; the dev's net-zero-cartridge-change claim is
  honest (all cartridge SUTs carry real defs). Adversarial check on leniency FAILED to find a
  problem: the grounding is NOT so weak it reproduces over-grading — the zero-def case genuinely
  flips the verdict (TC-APAA-PIPELINE-001-41).
- **PURE + ZERO-TOKEN DEFAULT (DN-V1-DETERMINISTIC) (PASS).** The validator is a pure, deterministic,
  zero-token isinstance-guarded fold over the PRE-BUILT 1.4 AST entry (no re-parse, no second
  tree-sitter/ast/radon call — AR7/§3.3). It never raises (AR10 parametrized no-crash matrix over
  None/object/str/int/dict/tuple/list). The no-LLM gate carve-out is a correct extend-not-fork:
  `_PIPELINE_LLM_FORBIDDEN_PREFIXES` bans providers.* + the three LLM-dispatch audit modules while
  allowing the pure grounding validator; the strict `_LLM_FORBIDDEN_PREFIXES` is preserved for the
  pure-seam tests. `grounding` added to `_MODULES_UNDER_GUARD`; provider-free assertion green
  (TC-APAA-AUDIT-001-47).

### Other checks

- Single serializer / 1.1 AST gate green; `extra="forbid"` frozen on all AST models; `grounding.py`
  90 lines, `pipeline.py` 1190 lines (≤1200); headless (no HTTP/UI/cli flag). Non-ASCII discipline
  covered (TC-APAA-AUDIT-001-56). No float (AR4 — returns `bool`).
- DF-1-7-B back-filled into the central `deferred-work.md` with the six CC-3 fields + an append-only
  closure note (original entry preserved, §3.4).

### Tests

`PYTHONIOENCODING=utf-8 pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
**1083 passed, 1 skipped, 4 subtests passed**. `mypy` clean on `grounding.py`. One transient failure
during the first run (`test_store_integrity_lint.py::test_lint_writes_nothing_to_apaa` —
`git ls-files -z timed out`) was confirmed to be environment flakiness in a story-4.2 git-subprocess
path UNRELATED to 6.2; it passes cleanly on isolated re-run and on the full re-run.

### Action items

None blocking. Low / advisory (forward note, not a 6.2 finding): `pipeline.py` is at 1190/1200 lines;
the next story that touches `pipeline.py` should plan a cohesion split before the hard limit
(NFR-M1 / CLAUDE.md §3.2) rather than after.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-06-29 | 0.1.1 | Code-review gate (iter-1): VERDICT pass → done. DF-1-7-B genuinely closed (RED-then-green TC-APAA-AUDIT-001-50 + observable end-to-end verdict migration TC-APAA-PIPELINE-001-41); ledger byte-identical (grade_entry signature unchanged, DN-GROUNDED); honest migration (signature-demo moat preserved empirically for the right reason — calculator.py has real defs; no test silently weakened); validator pure/zero-token/never-raises; no-LLM gate extend-not-fork correct. 1083 passed/1 skipped (one transient git-timeout flake, unrelated, passes on re-run); mypy clean; ≤1200 lines; headless. Advisory only: pipeline.py at 1190/1200 lines. | Code-review (claude-opus-4-8) |
| 2026-06-29 | 0.1.0 | FR7 full Python AST-grounding of `audited_deep` claims — CLOSES DF-1-7-B (AI-E5-5). New PURE `audit/grounding.py::is_deep_claim_grounded` (stack-agnostic `claim→validated?` interface, Python impl #1, ≥1-Definition grounding fact, no re-parse — AR7); `pipeline._grade_non_test_python` grades `audited_deep` ONLY when grounded via `claim_present=(claim_emitted AND claim_grounded)` into the UNCHANGED `grade_entry` (DN-GROUNDED), downgrading a clean-parse zero-def module to `audited_shallow`. Honest migration: all cartridge SUTs have real defs → stay deep → signature-demo moat preserved (net-zero cartridge verdict change); DF-1-7-B RED-then-green closure (TC-APAA-AUDIT-001-50) + observable verdict migration (TC-APAA-PIPELINE-001-41). Web+no-LLM gates extended-not-forked; frozen Epic-1..5 contracts byte-identical; 1083 passed/1 skipped, mypy clean, ≤1200 lines, headless, zero-token. DF-1-7-B back-filled + closed in deferred-work.md (AI-E5-4). | Dev (claude-opus-4-8) |
