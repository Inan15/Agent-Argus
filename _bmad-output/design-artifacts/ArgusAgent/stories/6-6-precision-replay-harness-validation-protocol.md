# Story 6.6: Precision replay harness + validation protocol (OI1 LOCKED: N = 5, phased) — [Tier B]

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
> **This is the SIXTH story of Epic 6** (Trust Substrate — Self-Audit, Prosecutor & Precision, Tier-B). It
> builds on the fully-done Epics 1+2+3+4+5 and on **done Stories 6.1** (the `LLMDispatchPort` +
> `MinionsLLMAdapter` + `FakeDispatch`), **6.2** (FR7 full Python AST-grounding `audit/grounding.py`),
> **6.3** (the FR12 orphan/dead-code detector `detectors/orphan_code.py`), **6.4** (the FR19 adversarial
> Prosecutor `verdict/prosecutor.py` + the CC #4 `cross_partition` cut-edge pass), and **6.5** (the FR20
> **measurement SUBSTRATE** — the parametrized cartridge registry `tests/apaa/cartridges/_registry.py`, the
> self-audit harness `tests/apaa/test_cartridge_selfaudit.py`, the `holdout_vacuous` cartridge, the
> citation-gaming trap, the no-crash row, AND the mechanized `PRECISION_GATE_STATUS` provisional marker).
> `epic-6` is already `in-progress`.
>
> **THIS STORY DELIVERS THE PRECISION REPLAY HARNESS + THE VALIDATION PROTOCOL** — the layer that turns the
> 6.5 golden-key substrate into a measurable, empirical **precision NUMBER**. Per the **OI1 LOCK** it does
> THREE things: (1) builds `minions_core/apaa/precision/replay_harness.py` — a PURE, zero-LLM-token function
> that **diffs emitted findings against a labeled ground-truth set** and emits precision (+ the false-positive
> denominator from clean repos) as a fixed-precision number (NOT a float — AR4); (2) authors the **validation
> protocol** (a committed `_bmad-output/design-artifacts/APAA/precision-validation-protocol.md` deliverable)
> that fixes WHO validates, expert-hours/repo, the precision-adjudication method (sample size, who judges a
> 🔴 "genuinely real"), and the per-metric pass/fail; and (3) honours the **phased-population plan** —
> the ground-truth schema is **designed for N=5** and the ≥80%-precision gate is reported **PROVISIONAL
> until N≥5** (the 6.5 marker stays provisional until the protocol is run at N≥5 with sufficient findings).
> **Precision is measured over FINDINGS, not repos.** OI1 honesty is non-negotiable: this story builds the
> harness + protocol and reports the provisional status — it MUST NOT softclaim a cleared ≥80% gate from a
> thin corpus.

## Story

As a **Business owner gating externalization** — who knows the entire externalization thesis stands or falls
on a *measured, defensible* precision number, and who is therefore far more harmed by a harness that *looks*
like it cleared the ≥80% gate (a precision figure computed over too few findings, with no validation protocol
defining how a 🔴 was adjudicated "genuinely real") than by an honest harness that reports "precision is X%
over N=4 labeled cartridges; the gate stays PROVISIONAL until N=5 with the validation protocol run" — and who
has watched every earlier Epic-6 story defer its "is this a real number?" question to "the 6.6 replay
harness + validation protocol",
I want **a PURE, zero-LLM-token precision replay harness** (`minions_core/apaa/precision/replay_harness.py`)
that **diffs the findings the audit emits against a labeled ground-truth set** (built over the 6.5 cartridge
registry's golden expected-findings keys + the clean-control true-negative repos), classifies each emitted
finding as a true positive / false positive (and each missed ground-truth finding as a false negative),
and **emits precision as a fixed-precision number** (true positives ÷ (true positives + false positives),
with the false-positive denominator drawn from the clean repos), with a **committed validation protocol**
(`precision-validation-protocol.md`) that fixes who validates, expert-hours/repo, the precision-adjudication
method, and the per-metric pass/fail — the ground-truth schema **designed for N=5**, populated **phased 3→5**,
precision measured over **FINDINGS not repos**, with the ≥80%-precision gate reported **PROVISIONAL until
N≥5**,
so that **the ≥80%-precision externalization gate is EMPIRICAL, not aspirational** — the harness produces a
real number from the labeled corpus, the validation protocol makes the number defensible (a documented
adjudication method, not an ad-hoc count), the clean-control repos give precision a false-positive
denominator, and the whole thing is scrupulously honest that the gate stays PROVISIONAL until the corpus
reaches the locked N=5 floor with the protocol applied — because honest, measured coverage is APAA's whole
thesis and over-claiming a cleared gate from a thin corpus would be the exact failure mode this lock forbids.

## Story Context

This is **Story 6 of Epic 6** (Trust Substrate, Tier-B — the "proven, not asserted, depth" moat that clears
the ≥80%-precision externalization gate). It delivers the **precision replay harness + the validation
protocol** over the 6.5 measurement substrate. It is the story EVERY earlier Epic-6 story (and 6.5 itself)
deferred its "is the precision number real and defensible?" question to. Story 6.5 built the golden-key
SUBSTRATE and the provisional marker; **6.6 computes the number on top of it and authors the protocol that
makes the number defensible.**

**The substrate this harness consumes already exists and is FROZEN — REUSE it, do NOT re-shape (the no-fork
keystone, §3.3 / AR7).** This story builds a NEW pure `precision/` module + a NEW protocol document + a
test harness; it adds NO new detector, NO new pipeline behavior, and edits NO frozen contract.
- **The 6.5 cartridge registry (`tests/apaa/cartridges/_registry.py`).** The LOCKED, committed golden
  expected-findings source of truth: a frozen `CartridgeSpec` tuple (`CARTRIDGE_REGISTRY`) keyed by cartridge
  id, each row carrying `required_findings: tuple[GoldenFinding, ...]` (the golden key — `GoldenFinding =
  (rule_id, verdict_eligible, advisory)`, NEVER source bytes), `kind ∈ {planted_defect, clean_control,
  holdout, trap, no_crash}`, `expected_verdict`/`expected_exit`/`max_blocking`, `non_ascii`, `provisional`.
  Also exposes `VALIDATION_SET_FLOOR_N = 5`, `populated_planted_defect_count()`, and the
  `PRECISION_GATE_STATUS` / `precision_gate_status()` marker. **6.6 REUSES this registry as the labeled
  ground-truth source — it does NOT re-author golden keys.** The registry's `required_findings` ARE the
  ground-truth positives per cartridge; the `clean_control` (and clean-shaped `trap`/`no_crash`) rows are
  the true-negative / false-positive denominator.
- **The cartridge staging helper (`tests/apaa/cartridges/_cartridge.py::stage_cartridge`).** The LOCKED
  cartridge-pinning approach (story 1.7 / 6.5): copies `*.py.txt` templates into a fresh temp dir, strips
  `.txt`, `git init` + single commit, returns `(repo_path, commit_sha)`. The replay-harness test REUSES this
  verbatim to stage each registry cartridge before auditing it.
- **The full pipeline (`minions_core/apaa/pipeline.py::run_audit_detailed`).** Returns an `AuditResult`
  (`verdict` = the pure 1.6 `AuditVerdict` carrying the ordered findings + exit code, `locators` =
  `.apaa/`-root-relative POSIX write paths, plus additive `floor_report` / `negative_assurance` /
  `coverage_report`). The harness runs the SAME deterministic, zero-token (NFR-D2) audit the 6.5
  self-audit harness + the signature-demo test run, and reads the emitted findings off the result. It adds
  NO new pipeline entrypoint.
- **The frozen `Recording` (`ledger/recording.py`).** An emitted finding carries `recording_id`
  (a.k.a. `finding_id`), `rule_id` (the golden-key match field), `cartridge_id`, `advisory: bool`,
  `depth_supported: CoverageDepth | None` (the verdict-eligibility flag — `verdict_eligible ==
  depth_supported is not None`, the 6.5 convention), `claim_present`, `locators: tuple[Locator, ...]` (≥1,
  FR13), `coverage_envelope_slice`. The replay-harness diff matches an emitted finding to a ground-truth
  `GoldenFinding` on `(rule_id, depth_supported is not None, advisory)` — the SAME 6.5 match key — NEVER on
  source bytes (NFR-S1).
- **The store reader (`minions_core/apaa/store/reader.py::ApaaStoreReader`).** Re-verifies `content_hash`;
  the harness reads emitted findings through it exactly as the 6.5 harness does.
- **The 6.5 self-audit harness (`tests/apaa/test_cartridge_selfaudit.py`).** The pattern to GENERALIZE: it
  already proves stage → `run_audit_detailed` → assert golden-key true positives / clean-control floor /
  determinism / secret-containment. **6.6 GENERALIZES the per-cartridge golden-key assertion into a
  corpus-wide PRECISION ROLL-UP** (a pure diff → TP/FP/FN counts → a precision number) — it does NOT add a
  parallel pipeline runner (§3.3).

**THE OI1 LOCK — the central honesty constraint (read this twice).** Per the epic "Open delivery inputs —
LOCKED 2026-06-18" block, the FR Coverage Map, and the 6.5 `PRECISION_GATE_STATUS` marker:
- **Validation-set `N` is LOCKED at `N = 5`** (V1 gate floor). The ground-truth schema + the precision
  harness are **DESIGNED for N=5** (the registry already scales to 5 with no refactor — the README's additive
  promise; 6.6 must not regress that).
- **Populated PHASED 3→5.** Three labeled cartridges were front-loaded in M1 (6.5 populated vacuous / secret
  / orphan + the holdout); the corpus grows to 5 before the ≥80%-precision gate is declared cleared. **6.6
  stands up the precision harness + the validation protocol over whatever the corpus currently holds and
  reports the number PROVISIONALLY** — it does NOT have to physically reach 5 distinct planted-defect
  cartridges in this story (continuing the phased plan), but the harness + ground-truth schema MUST be
  shaped for 5 and the gate-status reporting must be honest.
- **Precision is measured over FINDINGS, not repos.** The ground-truth is a SET of expected findings (per
  cartridge), so 5 repos with sufficient findings support a defensible 80% number. The harness computes
  precision over the FINDING counts (TP / (TP + FP)), NOT over a repos-passed fraction.
- **The ≥80%-precision gate stays PROVISIONAL below N=5.** This story COMPUTES a precision number from the
  labeled corpus AND authors the validation protocol — but it MUST report the gate PROVISIONAL until N≥5 with
  the protocol applied (it does NOT flip `PRECISION_GATE_STATUS` to non-provisional unless the corpus has
  genuinely reached N≥5 distinct planted-defect cartridges AND the validation protocol's per-metric pass/fail
  has been recorded as cleared — if the corpus is still below 5, the marker STAYS provisional and the
  computed number is reported as an EARLY/PROVISIONAL signal). **Do NOT overclaim a cleared ≥80% gate from
  too few findings — honest coverage is APAA's whole thesis.**

**The four members of the precision-replay declared set (the harness substrate, mechanizing AI-E5-1).**
The harness + protocol must cover EACH, RED-first where a naive implementation would miss it:
1. **Precision computation over FINDINGS (TP/FP/FN classification).** For each cartridge, diff the emitted
   findings against the registry's `required_findings` golden key: an emitted finding whose match key is in
   the golden key is a **true positive (TP)**; an emitted finding whose match key is NOT expected (especially
   a BLOCKING finding on a clean-control / trap / no-crash repo) is a **false positive (FP)**; a golden-key
   member NOT emitted is a **false negative (FN)**. Precision = TP / (TP + FP), computed as fixed-precision
   (a `Decimal` or an exact `Fraction`, stored as a string ratio — NEVER a `float`, AR4 / the NFR-P1
   byte-diff landmine). The harness must surface the TP/FP/FN counts + the precision number + the clean-repo
   false-positive count.
2. **The false-positive denominator from clean repos (R6).** Precision needs clean (true-negative) repos so
   a citation-gaming / over-eager detector that false-flags clean code is PENALIZED in the denominator. The
   `clean_control` row (and the clean-shaped `trap` / `no_crash` rows) are that denominator: ANY blocking
   finding on a clean repo is an FP. The harness asserts the clean-repo FP contribution is computed (RED-first
   against a harness that only counts planted-defect TPs and ignores clean-repo FPs — that would inflate
   precision to a meaningless 100%).
3. **The validation protocol (a committed V1 deliverable).** A committed
   `_bmad-output/design-artifacts/APAA/precision-validation-protocol.md` that fixes: WHO validates (the
   role — e.g. Engineering Lead / QA Lead / an external adjudicator), expert-hours/repo budget, the
   **precision-adjudication method** (sample size, who judges whether a 🔴 is "genuinely real", how a
   borderline finding is resolved), the per-metric pass/fail thresholds (≥80% precision, the false-positive
   ceiling, the N=5 corpus floor), and the phased-population plan (3→5, who labels each new cartridge, when
   the gate flips). Recorded BEFORE the ground-truth schema is frozen (OI1) — the protocol is the durable
   §3.4 source of truth for HOW the number is judged, not just WHAT it is.
4. **The provisional-gate honesty roll-up (the OI1 keystone).** The harness EXPOSES (and a test ASSERTS) that
   the precision gate is reported PROVISIONAL until N≥5 with the protocol applied. It REUSES the 6.5
   `PRECISION_GATE_STATUS` marker convention (or a 6.6 precision-result type that carries a `provisional:
   bool` + the gate-status string) — the computed number is reported alongside the provisional flag, and the
   harness does NOT silently flip the gate to cleared. If the corpus is below N=5, the result is explicitly
   `provisional=True` and the number is an early signal.

**The precision-result schema — pure, fixed-precision, designed for N=5 (DN-RESULT-SCHEMA).** Build a
single PURE result type (a frozen dataclass / Pydantic model) the harness returns, carrying: per-cartridge
`(cartridge_id, kind, tp, fp, fn)` rows, the corpus-wide TP/FP/FN totals, the precision number as a
fixed-precision STRING ratio (NEVER a float), the labeled-cartridge count `n`, the floor `VALIDATION_SET_FLOOR_N`,
a `provisional: bool`, and the gate-status string (REUSE / extend the 6.5 `precision_gate_status()` marker —
do NOT fork a second marker). The type is PURE (no I/O, no clock, no LLM, no random — AR8); it is computed
from the emitted-findings sets + the registry ground-truth. The ground-truth shape is designed so a NEW
labeled cartridge is a registry row + a `*.py.txt` drop-in with NO harness refactor (the N=5 design — 6.5's
DN-REGISTRY promise, which 6.6 must not regress).

**REUSE the 6.5 harness patterns — no second pipeline runner, no second match key (§3.3).** The 6.5
self-audit harness already proves stage → `run_audit_detailed` → emitted-findings-set → golden-key match on
`(rule_id, depth_supported is not None, advisory)`. The 6.6 replay harness GENERALIZES that into the
corpus-wide precision roll-up: it composes `stage_cartridge` + `run_audit_detailed` + `ApaaStoreReader` and
REUSES the SAME match-key derivation (factor the shared match-key helper if it is not already importable — do
NOT re-derive a second, divergent match key). It does NOT add a parallel pipeline, a second serializer, a
second hasher, or a second golden-key store.

**THE SIZE CONSTRAINT — `precision/replay_harness.py` is a production module; mind ≤1200 lines (NFR-M1 /
§3.2).** The harness module is PURE diff/count/precision logic. Keep it cohesive; the cartridge templates +
the registry stay in `tests/apaa/cartridges/`. The protocol is a `.md` document, not code. If the module
approaches 1200 lines, split by responsibility (the pure diff/classify core vs. the result-schema /
gate-status roll-up) into sibling modules — measure first, do not split speculatively.

**Scope vs the rest of Epic 6 + the dogfood (explicit deferrals — do NOT pull forward).**
- **6.5 measurement substrate (the cartridge registry + golden keys + holdout + clean controls + the
  provisional marker)** — DONE. 6.6 CONSUMES it; it does NOT re-author golden keys, re-author the holdout, or
  edit the 6.5 registry shape (it may ADDITIVELY consume `CARTRIDGE_REGISTRY` and REUSE / extend the
  `precision_gate_status()` marker — it must not fork a second registry or a second marker).
- **6.7 HITL STOP/PROCEED escalation + append-only decision record (FR23/FR24)** — out of scope. 6.6 does NOT
  build the escalation gate or the decision record.
- **Physically growing the corpus to 5 distinct planted-defect cartridges with a fully author-blind holdout
  corpus** — if the corpus is still below 5 after 6.6, the remaining cartridge population continues per the
  phased plan; 6.6's job is the HARNESS + PROTOCOL + the honest provisional report, not necessarily reaching
  N=5 in this story. (If the corpus is already at/over 5 labeled planted-defect cartridges, 6.6 MAY flip the
  marker to non-provisional ONLY after the validation protocol's per-metric pass/fail is recorded as cleared —
  but it must not manufacture cartridges merely to flip the gate.)
- **The Minions dogfood proof run (Epic 7 — running APAA against Minions itself, the empirical precision over
  a REAL repo, the budget sizing)** — out of scope. 6.6's precision is measured over the CARTRIDGE corpus
  (labeled ground truth); the real-repo proof is Epic 7.
- **A new detector / a change to any 6.1–6.5 detector or the Prosecutor** — out of scope. The harness
  MEASURES the existing detectors; it does not add or tune one. If the precision diff reveals a detector gap,
  that is a FINDING (file a defer), not a 6.6 detector edit.
- **Editing the frozen Epic-1..6 contracts** (`coverage_ledger.py` / `recording.py` / `verdict_gate.py` /
  `partitioner.py` / `detectors/*` / `prosecutor.py` / `pipeline.py` / `store/*` / `cache/*` / `models.py` /
  the 6.5 `_registry.py` shape) — the harness COMPOSES them as-is. The ONLY production-tree additions are the
  NEW `precision/` module (a new APAA library module → it MUST be added to the `tests/apaa/test_no_web_imports.py`
  guard's APAA-module set if that guard enumerates modules, and it MUST be pure / FastAPI-free / LLM-free).
- **A new `.github/workflows` CI job** — the harness ships a `tests/apaa/` pytest module; it runs under the
  EXISTING APAA pytest CI invocation (the durable backstop, AR9). NO new CI job is authored (mirrors the
  6.1–6.5 "no new CI job" fence).
- **A new HTTP route / FastAPI surface / UI (§3.7) / a new `cli.py` flag** — out of scope. (A future
  `apaa precision`/`--precision` CLI surface is a follow-up; 6.6 is the library harness + protocol.)

**Carry-forward action items (CLAUDE.md §9.1 / L1-E11 — each 6.x story cites its AI-E5-* item).**
- **AI-E5-1 (test-infra 🟠) — the COMPLETE-THE-DECLARED-SET keystone-adequacy checklist.** Applied to 6.6:
  enumerate the FULL declared set of precision-replay MEMBERS — (1) precision computation over findings
  (TP/FP/FN); (2) the clean-repo false-positive denominator (R6); (3) the validation protocol; (4) the
  provisional-gate honesty roll-up — and demonstrate EACH covered (RED-first where a naive harness would miss
  it, especially the clean-repo FP denominator + the no-overclaim provisional report). The enumeration is
  explicit in the harness module + the test module.
- **AI-E5-2 (test-infra 🟠) — MECHANIZE fixture-shape coverage.** 6.6 REUSES the 6.5 parametrized registry as
  the mechanized ground-truth source — the precision roll-up iterates `CARTRIDGE_REGISTRY` mechanically (no
  hand-copied per-cartridge bodies), and the gate-status is mechanized (a committed constant / a derived
  result field the test asserts), not a prose promise.
- **AI-E4-2 (test-infra) — no-crash input shapes.** The precision harness must handle the no-crash / clean
  cartridge rows without crashing (a `no_crash` / `clean_control` row contributes to the FP denominator, not
  a TP); a missing registry row, an empty golden key, or a `stage_cartridge` failure → a clear, NAMED test
  failure (an assertion with the cartridge id), never a bare traceback.
- **AI-E1-1 (test-infra 🟢) — non-ASCII / locale discipline (the Epic-1-FAIL class, standing).** The
  non-ASCII cartridge (`nonascii_unicode`) participates in the precision corpus + matches its golden key +
  serializes under `PYTHONIOENCODING=utf-8` (the single serializer is `ensure_ascii=False`).
- **AI-E5-4 (governance 🟢) — central defer register.** If 6.6 surfaces a detector gap (a finding the diff
  classifies FP/FN that reveals a real detector weakness), a missing-cartridge need, or a known precision
  limitation it does NOT close, file it append-only in `_bmad-output/design-artifacts/APAA/deferred-work.md`
  with the six CC-3 fields (`target_story` e.g. `6-7-hitl-stop-proceed-escalation-append-only-decision-record`
  or `epic-7-...` for "grow corpus to N=5 / dogfood precision").
- **AI-E5-7 (process 🟢) — keep the structural gates green + partial-reuse docstring precision.** The harness
  keeps the no-web-imports gate, the single-serializer AST gate, and the file-size gate green (the new
  `precision/` module is pure, uses the EXISTING canonical serializer if it serializes anything, adds NO new
  `json.dumps`/hasher/parse, imports NO `fastapi/uvicorn/starlette` and NO LLM dispatch). When reuse is
  PARTIAL (REUSES the 6.5 registry + `stage_cartridge` + `run_audit_detailed` + `ApaaStoreReader` + the
  match-key derivation + the `precision_gate_status()` marker; ADDS a pure precision-diff/roll-up + a
  validation-protocol doc), narrate it precisely.
- **AI-E5-3 (process 🟠) — committed pre-`review` test-existence guard.** The harness module + the result
  schema + the precision tests + the validation-protocol doc + the gate-status reporting EXIST + pass before
  the `review` flip.
- **NFR-S1 secret-containment (standing CI-blocking moat).** The precision corpus includes secret-bearing
  cartridges (`hardcoded_secret`, `secret_canary`, `evidence_sentinel`). The harness MUST assert no planted
  secret / canary / source sentinel byte appears in the precision result, the per-cartridge rows, or any
  artifact it reads — the precision result carries only counts + rule-id provenance + the fixed-precision
  ratio, NEVER source bytes (the golden key is value-free by the 6.5 contract). These audits flow through the
  EXISTING 4.4 randomized-canary suite (extend it only if a NEW write path or NEW cartridge is introduced).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 6.6) + the architecture (FR20 defect-cartridge self-audit /
> precision substrate; AR9 committed/durable CI gates; AR4 fixed-precision-no-float) + the PRD (the
> ≥80%-precision externalization gate; FR13 locator-or-reject) + the OI1 LOCK (N=5, phased 3→5, precision
> over findings, provisional below N=5). Drivers: **APAA-FR-20** (APAA validates its own detectors against
> defect cartridges with golden expected-findings keys — the precision MEASUREMENT over that substrate),
> **APAA-FR-13** (every finding carries ≥1 verifiable locator — the TP/FP diff matches on rule-id +
> locator-bearing findings, never bytes), **APAA-NFR-D1/D2** (the precision computation is deterministic +
> zero-LLM-token — a pure fold over recorded findings), **APAA-NFR-P1** (the precision number + per-cartridge
> rows are byte-reproducible across two runs over the same corpus), **APAA-NFR-S1** (no source/secret bytes
> from any cartridge in the precision result / rows / any read surface), **APAA-AR9** (the harness is a
> committed, durable CI gate under the existing APAA pytest invocation), **APAA-AR4** (precision is
> fixed-precision `Decimal`/`Fraction` stored as a string ratio — NEVER a float), **APAA-NFR-M1/M2**
> (≤1200-line files; frozen Epic-1..6 contracts + the 6.5 registry shape unchanged).
>
> **SCOPE FENCE — Tier-B, single-purpose, the precision replay harness + the validation protocol + the
> honest provisional report.** This story delivers ONLY: (1) the PURE precision replay harness
> (`minions_core/apaa/precision/replay_harness.py`) that diffs emitted findings against the 6.5 registry
> ground truth → TP/FP/FN → a fixed-precision precision number (+ the clean-repo FP denominator); (2) a PURE
> precision-result schema (per-cartridge rows + corpus totals + the precision ratio-string + `n` + floor +
> `provisional` + gate-status); (3) the committed validation protocol
> (`_bmad-output/design-artifacts/APAA/precision-validation-protocol.md`); (4) the honest provisional
> gate-status report (REUSE/extend the 6.5 `precision_gate_status()` marker — the gate stays PROVISIONAL
> until N≥5 with the protocol applied); (5) the precision-harness test module
> (`tests/apaa/test_precision_replay.py`); (6) any NEW defer filed with the six CC-3 fields. It does NOT
> build, and MUST NOT pull forward: the **HITL STOP/PROCEED + decision record** (6.7); the **Minions dogfood
> real-repo precision / budget sizing** (Epic 7); a **new detector or any change to a 6.1–6.5 detector / the
> Prosecutor**; an **edit to any frozen Epic-1..6 contract OR the 6.5 `_registry.py` shape** (compose them
> as-is); a **new `.github/workflows` CI job**; a **new HTTP route / FastAPI surface / UI** (§3.7); a **new
> `cli.py` flag**.

**AC1 — A PURE precision replay harness diffs emitted findings against the 6.5 ground truth → TP/FP/FN (FR20 / NFR-D2 / AR7 reuse)**
**Given** the 6.5 cartridge registry (`tests/apaa/cartridges/_registry.py::CARTRIDGE_REGISTRY`, each row's
`required_findings` = the golden key) and the emitted findings from `run_audit_detailed` over each staged
cartridge
**When** `minions_core/apaa/precision/replay_harness.py` diffs the emitted findings against the ground truth
**Then** it classifies each emitted finding as a **TP** (its match key `(rule_id, depth_supported is not None,
advisory)` is in the cartridge's golden key) or a **FP** (its match key is NOT expected — especially a
blocking finding on a clean repo), and each golden-key member NOT emitted as a **FN**; the diff is a PURE
function (no I/O, no clock, no LLM, no random — AR8), it REUSES the SAME 6.5 match-key derivation (no second,
divergent match key — §3.3), and it imports NO `fastapi/uvicorn/starlette` and NO LLM dispatch surface
(the no-web-imports / no-LLM gates stay green).

**AC2 — Precision is computed as a fixed-precision number over FINDINGS, not repos (OI1 / AR4)**
**Given** the corpus-wide TP / FP / FN counts
**When** precision is computed
**Then** precision = TP / (TP + FP) is a **fixed-precision** value (a `Decimal` or an exact `Fraction`)
stored / reported as a **string ratio** — NEVER a `float` (AR4 / the NFR-P1 byte-diff landmine; the 1.1
serializer rejects float); it is measured over FINDING counts (NOT a repos-passed fraction — the OI1
precision-over-findings lock); and the result surfaces the TP/FP/FN totals + the precision string + the
labeled-cartridge count `n` + `VALIDATION_SET_FLOOR_N`.

**AC3 — Clean (true-negative) repos supply the false-positive denominator — a citation-gaming detector is penalized (R6 / FR20)**
**Given** the clean repos in the corpus (`clean_control`, and the clean-shaped `trap` / `no_crash` rows whose
golden key is empty / `max_blocking == 0`)
**When** the precision diff runs over them
**Then** ANY emitted BLOCKING finding on a clean repo is counted as a **false positive** (it inflates the FP
denominator and DEPRESSES precision), so a citation-gaming / over-eager detector that false-flags clean code
is mechanically PENALIZED — the harness is RED-first against a naive precision harness that counts only
planted-defect TPs and ignores clean-repo FPs (which would report a meaningless 100%); the false-positive
contribution from clean repos is explicit in the result.

**AC4 — A committed validation protocol fixes who validates, the adjudication method, and per-metric pass/fail (OI1 / FR20)**
**Given** the OI1 LOCK (N=5, phased 3→5, precision over findings, ≥80% gate provisional below N=5)
**When** the validation protocol is authored
**Then** a committed `_bmad-output/design-artifacts/APAA/precision-validation-protocol.md` exists and fixes:
WHO validates (the role), the expert-hours/repo budget, the **precision-adjudication method** (sample size,
who judges a 🔴 "genuinely real", how a borderline finding is resolved), the **per-metric pass/fail**
thresholds (≥80% precision, the false-positive ceiling, the N=5 corpus floor), and the **phased-population
plan** (3→5, who labels each new cartridge, when the gate flips to non-provisional) — recorded BEFORE the
ground-truth schema is frozen (it is the durable §3.4 source of truth for HOW the number is judged). The
protocol references the harness + the registry as the mechanized substrate.

**AC5 — The ≥80%-precision gate is reported PROVISIONAL until N≥5 with the protocol applied — the OI1 honesty keystone (OI1 / FR20)**
**Given** the OI1 LOCK and the 6.5 `PRECISION_GATE_STATUS` / `precision_gate_status()` marker
**When** the harness reports its gate status
**Then** the precision result carries a `provisional: bool` + a gate-status string that REUSES / EXTENDS the
6.5 marker (NO forked second marker), the result reports the computed precision number ALONGSIDE the
provisional flag, and the harness does NOT silently flip the gate to cleared: if the corpus is below N=5
distinct planted-defect cartridges (OR the validation protocol's per-metric pass/fail has not been recorded
as cleared), `provisional` is `True` and the number is reported as an EARLY/PROVISIONAL signal. The Dev Notes
+ the harness docstring are scrupulously honest that the count is N-going-on-5 and the gate stays provisional
(do NOT overclaim a cleared ≥80% gate from too few findings — honest coverage is APAA's whole thesis). If and
ONLY IF the corpus has genuinely reached N≥5 labeled planted-defect cartridges AND the protocol pass/fail is
recorded cleared may the marker flip — and that decision is recorded in the Change Log + Dev Notes.

**AC6 — Determinism + secret-containment + non-ASCII hold over the precision computation (NFR-D1/D2 / NFR-P1 / NFR-S1 / AI-E1-1)**
**Given** the precision corpus (every labeled + clean + non-ASCII cartridge)
**When** the precision is computed
**Then** (a) the computation is deterministic + ZERO-LLM-token (NFR-D2 — the V1 pipeline calls no LLM, the
diff is a pure fold); (b) the precision number + the per-cartridge rows are byte-reproducible across two runs
over the same corpus (NFR-P1 — fixed-precision, no float, the `_cartridge.py` HEAD-pin determinism precedent);
(c) NO source/secret byte from ANY cartridge (the planted secrets in `hardcoded_secret`/`secret_canary`/
`evidence_sentinel`, the canary, the source sentinel, the non-ASCII paths) appears in the precision result /
rows / any read surface (NFR-S1 — the result carries only counts + rule-id provenance + the ratio string;
these audits flow through the EXISTING 4.4 randomized-canary suite, extended only if a NEW cartridge or write
path is introduced); (d) the non-ASCII cartridge (`nonascii_unicode`) participates in the corpus + matches
its golden key + serializes under `PYTHONIOENCODING=utf-8` (AI-E1-1).

**AC7 — Complete-the-declared-set over the precision-replay members, each RED-first where applicable (AI-E5-1 / AR10)**
**Given** the full DECLARED set of precision-replay members
**When** the harness + protocol are built
**Then** EACH member is explicitly covered: (1) precision computation over findings — TP/FP/FN classification
(AC1/AC2); (2) the clean-repo false-positive denominator (AC3 — RED-first against a harness that ignores
clean-repo FPs); (3) the committed validation protocol (AC4); (4) the provisional-gate honesty roll-up (AC5 —
RED-first against a harness that silently flips the gate to cleared); AND the enumeration is EXPLICIT in the
harness module + the test module (the complete-the-declared-set discipline). The harness itself never raises
opaquely (a missing registry row / empty golden key / staging failure → a NAMED assertion citing the
cartridge id, never a bare traceback — the AI-E5-1 no-crash leg).

**AC8 — No regression / no scope creep; structural gates green; ≤1200 lines; the pre-`review` test-existence precondition (AI-E5-7 / AI-E5-3 / NFR-M1/M2)**
**Given** the new `precision/replay_harness.py` + the result schema + the validation-protocol doc + the
precision tests
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the prior green baseline + the new 6.6 precision tests), the no-web-imports gate (extended to include
the new `precision/` module if it enumerates modules), the single-serializer AST gate, and the file-size gate
stay green; `mypy` is clean on any new/modified modules
**And** NO production-tree behavior changes to the frozen surfaces (the harness COMPOSES the existing
pipeline/detectors/Prosecutor + the 6.5 registry; NO new detector, NO detector/Prosecutor edit, NO
frozen-contract diff, NO 6.5 `_registry.py` shape change — `coverage_ledger.py` / `recording.py` /
`verdict_gate.py` / `partitioner.py` / `detectors/*` / `prosecutor.py` / `pipeline.py` / `store/*` /
`cache/*` / `models.py` / `tests/apaa/cartridges/_registry.py` show NO behavior-changing diff), NO new
`.apaa/` write path that the harness mandates (the harness READS through the EXISTING `ApaaStoreReader`), NO
`cli.py` flag, NO HTTP route, NO new CI job, NO live LLM call
**And** each new/modified file is ≤1200 lines (NFR-M1 — split the pure diff core from the result/roll-up if it
approaches the limit; measure first); the new files cite their `APAA-FR-20` / `APAA-FR-13` / `APAA-NFR-D2` /
`APAA-NFR-S1` / `APAA-AR4` drivers in the module docstring + the locked test area / index; the mandatory
artifacts (the harness + the result schema + the protocol doc + the new tests) EXIST + pass + any new defer is
filed BEFORE the story flips to `status: review` (AI-E5-3 / AI-E2-1 test-existence discipline). **Test area
`APAA-PRECISION`** (`TC-APAA-PRECISION-001-NN`, start at index 01; lock the area + index in the module
docstring).

## Tasks / Subtasks

- [ ] **Task 0 — Re-read the REAL surfaces; LOCK the precision-result schema (DN-RESULT-SCHEMA), the diff/match-key reuse, the validation-protocol outline, the provisional-gate reuse, and the declared member set** (AC: 1, 2, 4, 5, 7)
  - [ ] Re-read `tests/apaa/cartridges/_registry.py` (`CARTRIDGE_REGISTRY`, `GoldenFinding`, `CartridgeSpec`,
        `kind` set, `required_findings`, `max_blocking`, `VALIDATION_SET_FLOOR_N`,
        `populated_planted_defect_count()`, `precision_gate_status()`, `PRECISION_GATE_STATUS`). LOCK: REUSE
        this as the labeled ground-truth source; do NOT re-author golden keys or fork a second registry.
  - [ ] Re-read `tests/apaa/test_cartridge_selfaudit.py` (the stage → `run_audit_detailed` → emitted-findings
        → `(rule_id, depth_supported is not None, advisory)` match-key pattern + the clean-control floor +
        the two-run determinism). LOCK: GENERALIZE the per-cartridge golden-key assertion into a corpus-wide
        TP/FP/FN roll-up; REUSE the SAME match-key derivation (factor a shared helper if not importable — no
        divergent second key); do NOT add a parallel pipeline runner (§3.3).
  - [ ] Re-read `minions_core/apaa/ledger/recording.py` (`rule_id` / `recording_id`/`finding_id` /
        `depth_supported` / `advisory` / `locators` ≥1) + `minions_core/apaa/pipeline.py::run_audit_detailed`
        / `AuditResult` (where the ordered findings live) + `minions_core/apaa/store/reader.py::ApaaStoreReader`.
        LOCK the emitted-findings read path + the match-key fields (NEVER source bytes — NFR-S1).
  - [ ] Re-read the OI1 LOCK block in `epics.md` (N=5, phased 3→5, precision over findings, provisional below
        N=5) + the 6.5 Senior Developer Review's `PRECISION_GATE_STATUS` keystone. LOCK: 6.6 computes the
        number + authors the protocol + reports PROVISIONAL; it does NOT manufacture cartridges to flip the
        gate, and it must not overclaim.
  - [ ] Enumerate + LOCK the DECLARED precision-replay member set (AC7 (1)–(4)) + DN-RESULT-SCHEMA + the
        protocol outline + the provisional-gate reuse + the OI1 honesty constraints. Record the locked rules +
        the honest-coverage rationale in Dev Notes.
- [ ] **Task 1 — Build the PURE precision-result schema (designed for N=5)** (AC: 2, 5)
  - [ ] A PURE frozen result type (dataclass / Pydantic model) carrying per-cartridge `(cartridge_id, kind,
        tp, fp, fn)` rows + corpus TP/FP/FN totals + the precision number as a fixed-precision STRING ratio
        (Decimal/Fraction, NEVER float — AR4) + `n` (labeled count) + `VALIDATION_SET_FLOOR_N` + `provisional:
        bool` + the gate-status string. PURE (no I/O / clock / LLM / random — AR8). REUSE / extend the 6.5
        `precision_gate_status()` marker for the gate-status string (no forked second marker).
- [ ] **Task 2 — Build the PURE precision diff/classify core** (AC: 1, 2, 3)
  - [ ] `minions_core/apaa/precision/replay_harness.py`: a PURE function that takes the emitted findings
        (per cartridge) + the registry ground truth → classifies TP/FP/FN per the 6.5 match key → computes
        the corpus precision (TP / (TP + FP)) as fixed-precision → returns the result schema. Clean repos
        (empty golden key / `max_blocking == 0`) contribute blocking findings as FPs (the R6 denominator).
        Imports NO `fastapi/uvicorn/starlette`, NO LLM dispatch; uses the EXISTING canonical serializer if it
        serializes anything (no second `json.dumps`/hasher).
  - [ ] If the module approaches 1200 lines, split the pure diff/classify core from the result/roll-up into
        sibling modules (measure first — do not split speculatively).
- [ ] **Task 3 — Author the validation protocol document** (AC: 4)
  - [ ] `_bmad-output/design-artifacts/APAA/precision-validation-protocol.md`: fixes WHO validates, the
        expert-hours/repo budget, the precision-adjudication method (sample size, who judges a 🔴 "genuinely
        real", borderline resolution), the per-metric pass/fail (≥80% precision, FP ceiling, N=5 floor), and
        the phased-population plan (3→5, who labels new cartridges, when the gate flips). References the
        harness + registry as the mechanized substrate. Recorded BEFORE the ground-truth schema is frozen.
- [ ] **Task 4 — Build the parametrized precision test harness over the corpus** (AC: 1, 2, 3, 5, 6, 7)
  - [ ] `tests/apaa/test_precision_replay.py` (area `APAA-PRECISION`, `TC-APAA-PRECISION-001-NN` from index
        01): stage each registry cartridge → `run_audit_detailed` → feed emitted findings to the harness →
        assert TP/FP/FN classification (AC1), the fixed-precision number (no float — AC2), the clean-repo FP
        denominator (AC3, RED-first against a TP-only harness), the provisional gate-status (AC5, RED-first
        against a silently-cleared gate), and the determinism + secret-containment + non-ASCII corpus
        properties (AC6). Each assertion failure NAMES the cartridge id (the AI-E5-1 no-crash leg).
  - [ ] Assert the gate-status marker is PROVISIONAL (unless the corpus has genuinely reached N≥5 with the
        protocol cleared) + the harness computes a real number (not a hardcoded 80%).
- [ ] **Task 5 — Secret-containment over the secret-bearing cartridges (extend the 4.4 suite only if needed)** (AC: 6)
  - [ ] Assert the planted secrets (`hardcoded_secret`/`secret_canary`), the canary, and the
        `evidence_sentinel` source sentinel are ABSENT from the precision result / per-cartridge rows / any
        read surface (NFR-S1 — the result carries only counts + rule-id provenance + the ratio string). If a
        NEW cartridge or write path is introduced, EXTEND `tests/security/test_apaa_secret_containment.py`
        (the 4.4 randomized-canary suite) to sweep it (do not fork).
- [ ] **Task 6 — Run + mypy + gates + any NEW defer + the pre-`review` precondition** (AC: 8)
  - [ ] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
        all pass (prior baseline + the new 6.6 precision tests). `mypy` clean on any new modules.
  - [ ] Confirm NO behavior-changing diff to the frozen Epic-1..6 production surfaces + the 6.5 `_registry.py`
        shape. Confirm the no-web-imports gate (extended to include the new `precision/` module if it
        enumerates modules), single-serializer, and file-size gates green. NO `cli.py`/HTTP/CI-job change; NO
        new detector/Prosecutor edit; NO live LLM.
  - [ ] **AI-E5-4:** if 6.6 surfaces a detector gap (an FP/FN the diff reveals as a real detector weakness),
        a missing-cartridge need, or a known precision limitation it does NOT close, file it append-only in
        `_bmad-output/design-artifacts/APAA/deferred-work.md` with the six CC-3 fields (`target_story` e.g.
        `6-7-hitl-stop-proceed-escalation-append-only-decision-record` or an `epic-7-...` key for "grow corpus
        to N=5 / dogfood precision").
  - [ ] **AI-E5-3 / AI-E2-1 GATE:** the mandatory artifacts (the harness + the result schema + the protocol
        doc + the new tests) EXIST + pass BEFORE the `review` flip; the Dev Agent Record is filled completely
        (no blank placeholders), incl. the locked DN-RESULT-SCHEMA / the protocol outline / the
        provisional-gate decision + the populated-vs-N=5 honesty statement.

## Dev Notes

### Architecture / contract anchors (re-read before coding)
- **Ground-truth source — REUSE, do not re-author:** `tests/apaa/cartridges/_registry.py` (the 6.5
  `CARTRIDGE_REGISTRY` — `CartridgeSpec.required_findings` = the golden key; `kind ∈ {planted_defect,
  clean_control, holdout, trap, no_crash}`; `max_blocking`; `VALIDATION_SET_FLOOR_N = 5`;
  `populated_planted_defect_count()`; `precision_gate_status()` / `PRECISION_GATE_STATUS`). 6.6 CONSUMES this;
  it does NOT fork a second registry or re-author golden keys.
- **Match key — REUSE the 6.5 derivation (no divergent second key):** an emitted `Recording` → its golden
  match key is `(rule_id, depth_supported is not None, advisory)` (the `verdict_eligible == depth_supported is
  not None` convention from `_registry.py::GoldenFinding`). Factor a shared match-key helper if it is not
  already importable; do NOT re-derive a second key in `precision/`.
- **Pipeline — REUSE:** `minions_core/apaa/pipeline.py::run_audit_detailed` → `AuditResult` (`verdict` = the
  1.6 `AuditVerdict` carrying ordered findings + exit code; additive `floor_report`/`negative_assurance`/
  `coverage_report`). `tests/apaa/test_cartridge_selfaudit.py` is the pattern to GENERALIZE (per-cartridge
  golden-key assertion → corpus precision roll-up). Stage via `tests/apaa/cartridges/_cartridge.py::stage_cartridge`.
- **Finding contract:** `minions_core/apaa/ledger/recording.py::Recording` (`rule_id` golden-key match field;
  `recording_id`/`finding_id`; `depth_supported` = verdict-eligibility; `advisory`; `locators` ≥1 = FR13).
  Reader: `minions_core/apaa/store/reader.py::ApaaStoreReader` (re-verifies `content_hash`). The precision
  result carries ONLY counts + rule-id provenance + the fixed-precision ratio string — NEVER source bytes
  (NFR-S1).
- **Fixed-precision — AR4 (the byte-diff landmine):** precision = TP / (TP + FP) must be `Decimal`/`Fraction`
  stored as a string ratio; NO float (the 1.1 serializer rejects float; NFR-P1 byte-identity).
- **Secret-containment suite (EXTEND, do not fork):** `tests/security/test_apaa_secret_containment.py` (4.4).
- **Structural gates:** `tests/apaa/test_no_web_imports.py` (no-web-imports — ADD the new `precision/` module
  to its APAA-module set if it enumerates modules), the single-serializer AST gate, the file-size gate.

### Locked decisions (resolve in dev; recorded here per §3.4)
- **DN-RESULT-SCHEMA.** A single PURE frozen result type the harness returns: per-cartridge `(cartridge_id,
  kind, tp, fp, fn)` rows + corpus TP/FP/FN totals + the precision number as a fixed-precision STRING ratio
  (Decimal/Fraction, NEVER float — AR4) + `n` (labeled count) + `VALIDATION_SET_FLOOR_N` + `provisional: bool`
  + the gate-status string. PURE (no I/O / clock / LLM / random — AR8). The gate-status string REUSES /
  extends the 6.5 `precision_gate_status()` marker (no forked second marker).
- **DN-MATCH-KEY-REUSE.** The TP/FP/FN diff matches on the SAME 6.5 key `(rule_id, depth_supported is not
  None, advisory)`. Factor a shared importable helper if needed; do NOT introduce a second, divergent match
  key (the precision number and the 6.5 self-audit must agree on what "the same finding" means — §3.3).
- **DN-FP-DENOMINATOR.** Clean repos (`clean_control` + clean-shaped `trap`/`no_crash`, golden key empty /
  `max_blocking == 0`) supply the false-positive denominator: any BLOCKING finding on a clean repo is an FP.
  RED-first against a harness that counts only planted-defect TPs (which would report a meaningless 100%).
- **DN-PROVISIONAL (the OI1 keystone).** The harness REPORTS the computed precision number ALONGSIDE a
  `provisional: bool` + the gate-status string. It does NOT silently flip the gate to cleared: below N=5
  distinct planted-defect cartridges (OR with the protocol pass/fail not recorded cleared), `provisional` is
  `True`. The marker flips to non-provisional ONLY if the corpus has genuinely reached N≥5 AND the validation
  protocol's per-metric pass/fail is recorded cleared — and that decision is recorded in the Change Log + Dev
  Notes. 6.6 must not manufacture cartridges merely to flip the gate, and must not overclaim a cleared gate
  from too few findings.
- **DN-PROTOCOL.** The validation protocol is a committed `.md` deliverable
  (`_bmad-output/design-artifacts/APAA/precision-validation-protocol.md`), not code. It fixes who validates,
  expert-hours/repo, the precision-adjudication method, the per-metric pass/fail, and the phased-population
  plan — recorded BEFORE the ground-truth schema is frozen (it is the durable §3.4 source of truth for HOW
  the number is judged).
- **DN-NO-PROD-CHANGE-FROZEN.** 6.6 adds a NEW pure `precision/` library module + a NEW protocol doc + a test
  module. It adds NO detector, edits NO detector/Prosecutor/frozen contract, does NOT change the 6.5
  `_registry.py` SHAPE (it may CONSUME `CARTRIDGE_REGISTRY` + REUSE/extend `precision_gate_status()`), adds
  NO `.apaa/` write path it mandates. The ONLY production-tree additions are the `precision/` module (pure /
  FastAPI-free / LLM-free) + its registration in the no-web-imports guard. If the diff reveals a detector
  gap, that is a DEFER (AI-E5-4), not a 6.6 detector edit.

### OI1 honesty constraints (the central theme — do NOT soften)
- `N` is LOCKED at 5 (V1 gate floor). The ground-truth schema / harness are DESIGNED for 5 (the 6.5 registry
  already scales to 5 — do not regress that).
- Population is PHASED 3→5: 6.6 computes the number over whatever the corpus holds + authors the protocol +
  reports PROVISIONAL. Physically reaching 5 distinct planted-defect cartridges may continue into the dogfood
  / a follow-up — but the harness + schema MUST be shaped for 5 and the gate-status honest.
- Precision is measured over FINDINGS, not repos (TP / (TP + FP) over finding counts).
- The ≥80%-precision gate is PROVISIONAL below N=5 — surfaced via the reused/extended gate-status marker. Do
  NOT overclaim a cleared gate from a thin corpus (the failure mode this lock forbids).

### Carry-forward action items addressed
- **AI-E5-1** — complete-the-declared-set over the precision-replay members (AC7), RED-first on the clean-repo
  FP denominator + the no-overclaim provisional report.
- **AI-E5-2** — MECHANIZE fixture-shape coverage via the REUSED 6.5 parametrized registry + the mechanized
  gate-status marker.
- **AI-E4-2** — the clean / no-crash cartridge rows handled without crashing; NAMED failures cite the
  cartridge id.
- **AI-E1-1** — the non-ASCII cartridge (`nonascii_unicode`) in the corpus under `PYTHONIOENCODING=utf-8`.
- **AI-E5-3 / AI-E5-7** — pre-`review` test-existence + structural gates green + partial-reuse docstring
  precision.

### Previous-story intelligence (6.5 — the immediate predecessor)
- 6.5 left the ≥80% gate **PROVISIONAL with NO precision number computed** and scope-fenced "grow the corpus
  to N=5 + compute the precision number + the validation protocol" to **this story (6.6)** — the 6.5 Senior
  Developer Review confirms `precision_gate_status()` is UNCONDITIONALLY provisional and computes NO number,
  and that the only open item ("corpus→N=5 + precision number + protocol") is 6.6's explicitly-planned scope
  (so 6.5 filed NO defer for it — it is in-plan, not a gap).
- 6.5's `_registry.py` carries 8 cartridge rows, of which `populated_planted_defect_count()` counts the
  labeled `planted_defect` + `holdout` rows (vacuous_basic, hardcoded_secret, orphan_basic, holdout_vacuous,
  nonascii_unicode → currently below the N=5 floor for *distinct* planted-defect classes depending on how
  vacuous variants are counted — the harness must REPORT the count honestly, not assume N≥5). The clean
  denominator rows are `clean_control` (clean), `evidence_sentinel` (trap, clean-shaped), `tool_breadth`
  (no_crash, clean-shaped).
- 6.5 confirmed every frozen Epic-1..6 production surface is unchanged by mtime; 6.6 must preserve that (NO
  behavior-changing diff to those surfaces or to the `_registry.py` shape).
- The whole APAA prod tree is currently UNTRACKED (the sub-tool is not yet git-committed), so `git diff` over
  the frozen surfaces will be empty/N-A — use mtime (as 6.5's reviewer did) as the load-bearing
  no-change evidence, and keep the new `precision/` module the only added production file.

## Dev Agent Record

### Context Reference

- Story: `_bmad-output/design-artifacts/APAA/stories/6-6-precision-replay-harness-validation-protocol.md`
  (the precision replay harness + the validation protocol, Tier-B).
- Reused substrate (by import, no fork — §3.3 / AR7): `tests/apaa/cartridges/_registry.py::CARTRIDGE_REGISTRY`
  (+ `GoldenFinding` / `CartridgeSpec` / `VALIDATION_SET_FLOOR_N` / `populated_planted_defect_count()` /
  `precision_gate_status()`), `tests/apaa/cartridges/_cartridge.py::stage_cartridge`,
  `minions_core/apaa/pipeline.py::run_audit_detailed`, `minions_core/apaa/store/reader.py::ApaaStoreReader`,
  `minions_core/apaa/ledger/recording.py::Recording` (`rule_id`/`depth_supported`/`advisory`/`locators` —
  the golden-key match fields).
- Pattern generalized: `tests/apaa/test_cartridge_selfaudit.py` (per-cartridge golden-key true positive →
  corpus-wide precision roll-up).
- Project rules: `CLAUDE.md` §3.2 (≤1200 lines), §3.4 (evidence immutability), §3.7 (headless), §3.8
  (12-Factor + secret masking); APAA `_bmad-output/design-artifacts/APAA/` planning + own sprint tracker.

### Agent Model Used

claude-opus-4-8[1m] (BMAD dev-story worker, 2026-06-30).

### Debug Log References

- One RED-then-green iteration on the FP-classification semantics: the first cut counted ANY
  emitted-not-golden key as an FP, which mis-classified the `clean_control` cartridge's two
  legitimate **advisory** `hardcoded_secret` findings as false positives. Corrected per AC3's
  explicit wording ("ANY emitted **BLOCKING** finding on a clean repo is a false positive") +
  the cross-cutting #6 advisory-by-contract rule: an FP is an emitted-not-golden key that is
  **verdict-eligible** (`key[1]` is True). An advisory over-emission is NOT a false accusation
  (it does not move the verdict; a clean repo legitimately stays RELEASE_READY while emitting a
  redacted-secret advisory). This matches the 6.5 `max_blocking == 0` clean floor exactly.
- Empirical computed precision over the current corpus: `precision=1/1` (6 TP / 0 FP / 0 FN),
  `recall=1/1`, `clean_repo_fp=0`, `n=5`, `provisional=True`. Reproducible across two runs.

### Completion Notes List

- **Delivered** (all REUSE-only over the 6.5 substrate, no fork — §3.3 / AR7):
  1. `minions_core/apaa/precision/replay_harness.py` (381 lines) — the PURE diff/classify/roll-up
     core: `finding_match_key` / `golden_match_key` (the SHARED 6.5 key, DN-MATCH-KEY-REUSE),
     `compute_precision` (TP/FP/FN → exact `Fraction` precision, AR4), the frozen
     `PrecisionResult` + `CartridgePrecisionRow` schema (DN-RESULT-SCHEMA), and
     `precision_gate_status_for` (REUSES/extends the 6.5 marker convention, no forked marker).
  2. `minions_core/apaa/precision/__init__.py` (39 lines) — the package surface.
  3. `_bmad-output/design-artifacts/APAA/precision-validation-protocol.md` — the committed V1
     validation protocol (DN-PROTOCOL): WHO validates (Engineering Lead / QA Lead / external
     tie-break), expert-hours/repo budget, the precision-adjudication method (full-corpus
     exhaustive + borderline resolution), the per-metric pass/fail (≥80% exact-Fraction, 0
     clean-repo blocking FP, N≥5 floor, recall diagnostic), the phased-population plan (3→5).
  4. `tests/apaa/test_precision_replay.py` (514 lines, area `APAA-PRECISION`,
     `TC-APAA-PRECISION-001-01..15`) — the corpus-wide precision roll-up test, RED-first on the
     clean-repo FP denominator (-05) + the no-overclaim provisional gate (-08).
  5. `tests/apaa/test_no_web_imports.py` — additive registration of the new `precision/` module
     in `_MODULES_UNDER_GUARD` + a dedicated provider-free / zero-token test (`TC-APAA-PRECISION-001-20`).
  6. `DF-6-6-A` filed (six CC-3 fields) — the honest N=5 / human-adjudication gate-flip limitation.
- **DN-RESULT-SCHEMA (locked).** `PrecisionResult` is a frozen dataclass carrying per-cartridge
  `(cartridge_id, kind, is_clean_repo, tp, fp, fn, fp_rule_ids, fn_rule_ids)` rows + corpus
  TP/FP/FN totals + `clean_repo_fp` + the precision as an exact `Fraction` AND its `"num/den"`
  string ratio (the only precision surface crossing a byte boundary — AR4, never a float) +
  `recall` + `n` + `floor_n` + `provisional` + `gate_status`. PURE (no I/O / clock / LLM /
  random — AR8). The threshold check compares the exact `Fraction` against `Fraction(4, 5)`.
- **DN-MATCH-KEY-REUSE (locked).** The diff matches on the SAME 6.5 key
  `(rule_id, depth_supported is not None, advisory)`. `golden_match_key` over a registry
  `GoldenFinding` equals the 6.5 self-audit's key byte-for-byte (asserted, `TC-...-01`) — no
  second, divergent key.
- **DN-FP-DENOMINATOR (locked).** An FP is an emitted-not-golden key that is BLOCKING
  (verdict-eligible). Clean repos (empty golden key + `max_blocking == 0`) supply the
  false-accusation denominator; `clean_repo_fp` is explicit on the result. RED-first proven by
  `TC-...-05` (a synthetic clean-repo blocking finding mechanically depresses precision below 1/1).
- **DN-PROVISIONAL (the OI1 keystone — NOT softened).** The harness computes a real number AND
  reports it PROVISIONALLY. `provisional` is `True` unless `n >= 5` AND `protocol_cleared=True`
  AND `precision >= 4/5`. **6.6 did NOT flip the gate.** Although
  `populated_planted_defect_count()` returns `5` cartridge ROWS, those span only THREE distinct
  defect-rule CLASSES (vacuous ×3, secret ×1, orphan ×1), and — decisively — NO human
  Engineering-Lead/QA-Lead adjudication run has been performed (`protocol_cleared` defaults
  `False`). Per OI1/AC5 the marker stays PROVISIONAL and the computed `1/1` is reported as an
  EARLY/PROVISIONAL signal. Manufacturing cartridges or fabricating a cleared adjudication to
  flip the gate is the exact failure mode this lock forbids; both are deferred (DF-6-6-A).
  The flip PATH is exercised over a synthetic 5-cartridge registry (`TC-...-09`) + the
  `precision_gate_status_for` "cleared" branch, so the logic is proven without over-claiming.
- **Complete-the-declared-set (AI-E5-1, AC7).** All four members enumerated in the harness
  docstring + covered: (1) TP/FP/FN computation (`-02`/`-03`); (2) clean-repo FP denominator
  RED-first (`-04`/`-05`); (3) the committed protocol (`-06`); (4) the provisional-gate roll-up
  RED-first (`-07`/`-08`/`-09`). No-crash leg: a missing emitted entry → a NAMED `KeyError`
  citing the cartridge id (`-13`).
- **AC6.** Determinism + zero-token (the V1 pipeline calls no LLM) byte-reproducible across two
  runs (`-10`); non-ASCII cartridge participates + matches its golden key under UTF-8 (`-11`);
  NFR-S1 secret-containment — no planted secret/source byte in the result/rows (`-12`, the
  result carries only counts + rule-id provenance + the ratio string; the 4.4 randomized-canary
  suite stays the CI-blocking property gate; 6.6 adds NO new cartridge / write path so it
  co-locates a fixed-canary check rather than extending 4.4).
- **AC8 / no regression.** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/
  tests/test_import_paths.py` → **1181 passed, 1 skipped, 4 subtests** (6.5 baseline was 1165
  passed; +16 = 15 precision tests + 1 provider-free test). `mypy` clean on both new modules.
  no-web-imports / single-serializer / file-size gates green. ALL files ≤1200 lines (harness
  381, init 39, test 514). Frozen Epic-1..6 surfaces + the 6.5 `_registry.py` shape UNCHANGED
  (mtime evidence: pipeline/prosecutor 06-29, recording/verdict_gate/reader 06-21,
  `_registry.py` 06-30 from 6.5 — none touched by 6.6; the APAA tree is untracked so mtime is
  the load-bearing no-change evidence, per the 6.5 reviewer's method). NO detector/Prosecutor
  edit, NO new `.apaa/` write path, NO `cli.py` flag, NO HTTP route, NO new CI job, NO live LLM.
- **Partial-reuse narration (AI-E5-7).** REUSES: the 6.5 `CARTRIDGE_REGISTRY` golden keys +
  `populated_planted_defect_count()` + `VALIDATION_SET_FLOOR_N`, `stage_cartridge`,
  `run_audit_detailed`, `ApaaStoreReader`, the 6.5 match-key derivation, and the
  `precision_gate_status()` marker CONVENTION. ADDS: a pure precision-diff/roll-up core + the
  result schema + the validation-protocol doc. The new `precision/` module imports the 6.5
  value-free registry from `tests/apaa/cartridges/` (the committed golden-key store) — value-free
  by the 6.5 NFR-S1 contract, so no source/secret byte enters the production module.

### File List

- `minions_core/apaa/precision/replay_harness.py` (new — the PURE diff/classify/roll-up core).
- `minions_core/apaa/precision/__init__.py` (new — the package surface).
- `tests/apaa/test_precision_replay.py` (new — the `APAA-PRECISION` corpus roll-up test).
- `_bmad-output/design-artifacts/APAA/precision-validation-protocol.md` (new — the V1 protocol).
- `tests/apaa/test_no_web_imports.py` (modified — additive registration + provider-free test).
- `_bmad-output/design-artifacts/APAA/deferred-work.md` (modified — DF-6-6-A appended).
- `_bmad-output/design-artifacts/APAA/stories/6-6-precision-replay-harness-validation-protocol.md`
  (this story file — status + Dev Agent Record + Change Log).
- `_bmad-output/design-artifacts/APAA/sprint-status.yaml` (modified — 6-6 → review).

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-06-30 | 0.1 | Story drafted (create-story) — the precision replay harness (`precision/replay_harness.py`, pure TP/FP/FN diff over the 6.5 registry ground truth → fixed-precision precision number, clean-repo FP denominator) + the validation protocol (`precision-validation-protocol.md`) + the honest PROVISIONAL gate-status report (REUSE/extend the 6.5 `precision_gate_status()` marker — OI1: N=5, phased 3→5, precision over findings, provisional below N=5, no over-claim). REUSE-only over the 6.5 substrate; scope-fenced vs 6.7 (HITL) + Epic 7 (Minions dogfood real-repo precision). Status → ready-for-dev. | Scrum Master (Bob) |
| 2026-06-30 | 1.0 | dev-story — DELIVERED. PURE `precision/replay_harness.py` (`compute_precision` → TP/FP/FN over the 6.5 golden keys → exact-`Fraction` precision string, AR4) + frozen `PrecisionResult`/`CartridgePrecisionRow` (DN-RESULT-SCHEMA) + `finding_match_key`/`golden_match_key` (the SHARED 6.5 key, DN-MATCH-KEY-REUSE) + `precision_gate_status_for` (REUSES the 6.5 marker convention, no fork). Committed `precision-validation-protocol.md` (DN-PROTOCOL: who validates / expert-hours / adjudication method / per-metric pass-fail / phased 3→5). Test `tests/apaa/test_precision_replay.py` (area APAA-PRECISION, TC-APAA-PRECISION-001-01..15) RED-first on the clean-repo FP denominator (DN-FP-DENOMINATOR: an FP is an emitted-not-golden BLOCKING key; advisory over-emissions are advisory-by-contract, NOT false accusations — matches the 6.5 max_blocking==0 floor) + RED-first on the no-overclaim provisional gate. **OI1 KEYSTONE — gate NOT flipped:** computed precision `1/1` over the corpus is reported PROVISIONAL (`protocol_cleared=False` default; no human adjudication run; only 3 distinct defect-rule classes across 5 cartridge rows) — over-claim refused. DF-6-6-A filed (grow corpus to N=5 distinct classes + run adjudication → flip gate). REUSE-only; frozen Epic-1..6 surfaces + `_registry.py` shape unchanged (mtime-verified); no detector/Prosecutor edit, no cli/HTTP/CI-job/LLM. 1181 passed/1 skipped/4 subtests, mypy clean, no-web/single-serializer/file-size gates green, files ≤1200. Status → review. | Developer (Amelia) |

## Senior Developer Review (AI)

**Reviewer:** Claude (BMAD adversarial code-review gate). **Date:** 2026-07-01. **Model:** claude-opus-4-8[1m].

**Outcome:** **PASS** (clean — 0 decision-needed / 0 patch / 0 defer-from-review / 0 dismissed). Story flipped `review → done`.

**What was reviewed.** Three adversarial layers (Blind Hunter correctness/security, Edge Case Hunter
boundary/branch, Acceptance Auditor AC/OI1 conformance) over the full 6.6 delivery: the PURE
`minions_core/apaa/precision/replay_harness.py` (381 lines) + its `__init__.py`, the
`tests/apaa/test_precision_replay.py` corpus roll-up (15 tests), the additive no-web-imports guard
registration, the committed `precision-validation-protocol.md`, and the DF-6-6-A defer entry. Every
keystone claim was verified INDEPENDENTLY (not trusted from the Dev record), including a live
harness run over the real staged cartridge corpus.

**Independent verification (evidence).**
- **Tests genuinely green** — re-ran `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/
  tests/test_import_paths.py` → **1181 passed, 1 skipped, 4 subtests** (118s), matching the Dev claim exactly.
  All 15 `TC-APAA-PRECISION-001-01..15` + the provider-free `-20` pass. `mypy` clean on both new modules.
- **AR4 fixed-precision, never float** — a live `compute_precision` run returned `precision_ratio='1/1'`,
  `isinstance(precision, float) is False` (exact `Fraction`); the ≥80% threshold compares against
  `Fraction(4, 5)`. Confirmed.
- **FP-definition keystone (the RED-first crux)** — verified empirically that the `clean_control` /
  `evidence_sentinel` / `tool_breadth` clean repos emit ONLY advisory `('hardcoded_secret'/'orphan_code',
  False, True)` keys, and because the FP filter is `if k[1]` (verdict-eligible/BLOCKING only), those
  advisory over-emissions are correctly NOT counted as false positives → `clean_repo_fp == 0`. A naive
  harness would have wrongly reported 3 FPs; `TC-...-05` proves a SYNTHETIC blocking clean-repo finding
  DOES depress precision below 1/1. The R6 denominator is real.
- **OI1 honesty keystone (the central constraint) — HELD, not softened** — computed precision is `1/1`
  (6 TP / 0 FP / 0 FN) yet `provisional=True`: the gate is NOT flipped. Independently confirmed
  `populated_planted_defect_count() == 5` ROWS but only **3 distinct defect-rule classes**
  (`vacuous_test_ast`, `hardcoded_secret`, `orphan_code`) — exactly as DF-6-6-A states. The gate is held
  provisional by `protocol_cleared=False` (no human adjudication run). No over-claim; the flip PATH is
  exercised in `-09` without manufacturing cartridges.
- **Zero-token / no-network** — the `TC-APAA-PRECISION-001-20` provider-free guard passes; the pure fold
  transitively imports no LLM/provider surface.
- **No-fork reuse (§3.3 / AR7)** — the 6.6 `finding_match_key` triple `(rule_id, depth_supported is not
  None, advisory)` is byte-identical to the 6.5 `test_cartridge_selfaudit._emitted_keys` derivation
  (verified by grep + the `-01` parity test). No second registry, serializer, hasher, or match key.
- **No frozen-surface regression** — the whole APAA tree is git-untracked, so `git diff` is N/A; mtime is
  the load-bearing evidence (`pipeline.py` 06-29, `_registry.py` 06-30 from 6.5, both pre-dating 6.6's
  precision work). `_registry.py` contents inspected: pure 6.5 registry, no 6.6 additions. No
  detector/Prosecutor/contract edit, no new `.apaa/` write path, no cli/HTTP/CI-job/LLM change. Files
  ≤1200 (harness 381).
- **Defer-schema** — DF-6-6-A carries all six CC-3 fields (id / origin_story / owner / target_story
  `epic-7-minions-dogfood-precision` / category `process` / severity 🟠); `scripts/check_defer_schema.py`
  exits 0.

**Triage:** all layers clean — zero actionable findings. No `### Review Findings` block was written
(nothing to persist). See the Dev Agent Record for the per-member complete-the-declared-set matrix.

**Verdict rationale.** Every AC (AC1–AC8) is met and independently reproduced; tests are genuinely green;
the OI1 no-over-claim keystone is honestly held (the single most important property of this story), with
the honest limitation correctly deferred rather than papered over. This is a genuine, defensible
precision harness that refuses to fabricate a cleared gate from a thin corpus.
