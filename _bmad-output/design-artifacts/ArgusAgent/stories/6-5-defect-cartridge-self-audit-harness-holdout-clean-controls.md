# Story 6.5: Defect-cartridge self-audit harness + holdout + clean controls — [Tier B]

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/APAA/`; the tracker is `_bmad-output/design-artifacts/APAA/sprint-status.yaml`
> (NOT the Minions platform tracker at `_bmad-output/implementation-artifacts/sprint-status.yaml`). All
> CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only, §3.8 12-Factor + secret masking, §3.4
> evidence immutability). Run all gate/test commands under `PYTHONIOENCODING=utf-8`.
>
> **This is the FIFTH story of Epic 6** (Trust Substrate — Self-Audit, Prosecutor & Precision, Tier-B). It
> builds on the fully-done Epics 1+2+3+4+5 and on **done Stories 6.1** (the `LLMDispatchPort` +
> `MinionsLLMAdapter` + `FakeDispatch`), **6.2** (FR7 full Python AST-grounding `audit/grounding.py`),
> **6.3** (the FR12 orphan/dead-code detector `detectors/orphan_code.py`), and **6.4** (the FR19 adversarial
> Prosecutor `verdict/prosecutor.py` + the CC #4 `cross_partition` cut-edge pass). `epic-6` is already
> `in-progress`.
>
> **THIS STORY DELIVERS FR20 (APAA validates its own detectors against defect cartridges with golden
> expected-findings keys, asserted in CI), `[Tier B]`** — the **precision/recall measurement substrate**.
> It does NOT compute the empirical ≥80%-precision number (that is Story 6.6's replay harness + validation
> protocol). It builds: (1) a deterministic, parametrized **defect-cartridge self-audit harness** that runs
> the FULL audit pipeline against the curated cartridges and asserts each planted defect hits its **golden
> expected-findings key** (true positives); (2) **clean true-negative control** cartridges where **any 🔴 is
> an instant CI fail** (the false-accusation floor); (3) a **hidden holdout** cartridge the detector authors
> never tuned against (the overfitting defense); and (4) **false-negative traps** (citation-gaming) that a
> naive detector would miss. Per the OI1 lock, the harness is **DESIGNED for N=5 cartridges, populated
> phased 3→5**, precision is measured over **findings not repos**, and the ≥80% gate is **PROVISIONAL below
> N=5** — this story must be HONEST about that (it is the substrate, not the cleared gate).

## Story

As an **APAA maintainer** who knows that the whole externalization thesis rests on *honest, measured*
coverage — and who is therefore more harmed by a detector that **looks** validated (a green CI badge with
no holdout, tuned to its own examples) than by a harness that admits "N is only 3 today, the number is
provisional" — and who has watched every earlier Epic-6 story defer its "is this catch real?" question to
"the 6.5 cartridge harness",
I want **a CI-asserted defect-cartridge self-audit harness** (`tests/apaa/test_cartridge_selfaudit.py` over
a parametrized cartridge registry) that, for each curated defect cartridge (a minimal repo + exactly one
planted defect + a documented **golden expected-findings key**), runs the FULL deterministic audit pipeline
and asserts the planted defect is caught (the detector hits its golden key — a true positive); that, for
each **clean true-negative control** (a repo with NO planted defect), asserts **any blocking 🔴 is an instant
CI fail** (the false-accusation floor); that exercises a **hidden holdout** cartridge the detectors were
never tuned against (the overfitting defense); and that includes **false-negative traps** (e.g. a
citation-gaming repo whose findings cite real locators but describe nothing) so a naive detector is caught —
designed for **N=5** cartridges, populated **phased 3→5**, measuring precision over **findings not repos**,
with the ≥80%-precision gate reported **PROVISIONAL until N≥5**,
so that **FR20 is delivered as the measurement substrate** — what the detectors catch (and, crucially, what
they must NOT falsely flag) is asserted EMPIRICALLY and durably in CI, the holdout proves the detectors are
not overfit, the clean controls pin the false-accusation floor, and the harness is the deterministic,
zero-overfitting foundation that Story 6.6's precision number and the externalization gate stand on — while
being scrupulously honest that the cartridge count is N=3-going-on-5 and the precision claim stays
provisional until the corpus is populated.

## Story Context

This is **Story 5 of Epic 6** (Trust Substrate, Tier-B — the "proven, not asserted, depth" moat that clears
the ≥80%-precision externalization gate). It delivers **FR20 (defect-cartridge self-audit, CI-asserted,
`[Tier B]`)** as the measurement substrate over the determinism spine (Epics 1–5) and the full Epic-6
detector + Prosecutor stack (6.1 LLM port, 6.2 grounding, 6.3 orphan, 6.4 Prosecutor). It is the story EVERY
earlier story deferred its "is the catch / the no-false-accusation real and measured?" question to.

**The substrate this harness consumes already exists and is FROZEN — REUSE it, do NOT re-shape (the no-fork
keystone, §3.3 / AR7).** This story builds a TEST/HARNESS layer; it adds NO new detector, NO new pipeline
behavior, and edits NO frozen contract.
- **The cartridge staging helper (`tests/apaa/cartridges/_cartridge.py::stage_cartridge`).** The LOCKED
  cartridge-pinning approach (story 1.7 / 6.5-precursor): copies `*.py.txt` templates into a fresh temp dir,
  strips `.txt`, `git init` + single commit, returns `(repo_path, commit_sha)`. The harness REUSES this
  verbatim — it does NOT re-implement staging. The cartridges README (`tests/apaa/cartridges/README.md`)
  already states: "Story 6.5 extends this directory ADDITIVELY into the parametrized multi-cartridge
  self-audit harness (+ hidden holdout); the layout here is designed so 6.5 can drop in more cartridges with
  no refactor."
- **The full pipeline (`minions_core/apaa/pipeline.py::run_audit` / `run_audit_detailed`).** The harness
  runs the SAME deterministic, zero-token (NFR-D2) audit the signature-demo test
  (`tests/apaa/test_pipeline_signature_demo.py`) runs, and reads the verdict / ordered findings / coverage
  ledger off the result — it adds NO new pipeline entrypoint.
- **The frozen `Recording` (`ledger/recording.py`).** A finding carries `rule_id` (the golden-key match
  field), `finding_id`, `locators` (≥1 verifiable, FR13), `advisory: bool`, `depth_supported`. The golden
  key matches on `rule_id` + locator presence — NEVER on source bytes (NFR-S1).
- **The done detectors + Prosecutor — the golden keys map 1:1 to their LOCKED `rule_id`s:**
  - `vacuous_test_ast` (1.5 vacuous-path AST subset — verdict-eligible) — cartridge `vacuous_basic`.
  - the secret detector's redacted finding (2.5 `contained_secret: true`, value redacted) — cartridge
    `hardcoded_secret` (and `secret_canary` for the canary/non-ASCII surface).
  - `orphan_code` (6.3, advisory) — cartridge `orphan_basic` (planted `unused_helper`).
  - (FR33 ordering: a verdict-blocking finding sorts first — asserted on the vacuous cartridge.)
- **The existing cartridge fixtures under `tests/apaa/cartridges/` (REUSE, do not author net-new SUTs unless
  a declared-set member needs one):** `vacuous_basic`, `clean_control`, `hardcoded_secret`, `secret_canary`
  (incl. a non-ASCII `café/модуль_секрет.py` path), `evidence_sentinel` (planted source sentinel + secret —
  the canary surface), `nonascii_unicode` (non-ASCII module + test paths), `orphan_basic` (planted orphan),
  `tool_breadth` (non-ASCII breadth-tool surface). These are the populated corpus; the holdout is a NEW
  cartridge (see DN-HOLDOUT).

**THE OI1 LOCK — the central honesty constraint (read this twice).** Per the epic "Open delivery inputs —
LOCKED 2026-06-18" block and the FR Coverage Map:
- **Validation-set `N` is LOCKED at `N = 5`** (V1 gate floor). The harness ground-truth / cartridge-registry
  shape is **DESIGNED for N=5** (the registry must scale to 5 with no refactor — the README's additive
  promise).
- **Populated PHASED 3→5.** Three labeled cartridges are front-loaded in M1 for early precision signal; the
  corpus grows to 5 before the ≥80%-precision gate is declared cleared. **This story stands up the harness +
  registry designed for 5 and populates the 3 planted-defect cartridges (vacuous / secret / orphan) + clean
  controls + a holdout** — it does NOT have to physically reach 5 distinct planted-defect cartridges in this
  story (that is the phased-population plan continuing into 6.6 / M1), but the registry + the harness must be
  shaped for 5 and the gate-status reporting must be honest.
- **Precision is measured over FINDINGS, not repos.** A golden expected-findings key is a SET of expected
  findings (per cartridge), so 5 repos with sufficient findings support a defensible 80% number. The harness
  asserts the EXPECTED-FINDINGS key per cartridge (the true-positive set) AND the clean-control empty-blocking
  set (the true-negative / false-positive denominator).
- **The ≥80%-precision gate stays PROVISIONAL below N=5.** This story does NOT compute or assert an 80%
  number (that is 6.6). It MUST surface, in the harness docstring + a documented gate-status marker + Dev
  Notes + the negative-assurance-adjacent honesty note, that the precision claim is PROVISIONAL until the
  corpus reaches N=5 — **do NOT overclaim a precision number from too few cartridges (honest coverage is
  APAA's whole thesis).**

**The five members of the cartridge-self-audit declared set (the FR20 substrate, mechanizing AI-E4-2).**
The harness must cover EACH, RED-first where a naive implementation would miss it:
1. **Golden-key true positive (per planted-defect cartridge).** Each defect cartridge's planted defect is
   caught — the audit emits ≥1 finding whose `rule_id` is the cartridge's golden key, carrying ≥1 verifiable
   locator (FR13). (vacuous → `vacuous_test_ast` + verdict-eligible + sorts first; secret → the redacted
   secret finding, value absent; orphan → `orphan_code` advisory.)
2. **Clean-control true negative (the false-accusation floor).** A clean-control cartridge (`clean_control`,
   no planted defect) audits to a verdict with **ZERO blocking findings** — **any 🔴 / blocking finding is an
   instant CI fail**. This is the moat the whole tool's credibility rests on.
3. **Hidden holdout (the overfitting defense).** A holdout cartridge the detector authors never tuned against
   is exercised + gated: its planted defect is caught by the SAME detectors with NO detector change (proving
   the detectors generalize, not memorize). See DN-HOLDOUT for what "hidden" means in a single-repo V1.
4. **False-negative trap (citation-gaming).** A trap cartridge / fixture where a naive detector would either
   (a) emit a finding that cites a real locator but describes nothing real (a citation-gaming false positive
   the clean-control floor must reject), or (b) miss a genuine planted defect that resembles benign code — so
   the harness proves the detector is not gamed. Include ≥1 such trap (the `evidence_sentinel` /
   citation-gaming surface is the natural home).
5. **Determinism + secret-containment + non-ASCII over the corpus.** Every cartridge audited TWICE yields a
   byte-identical verdict envelope `content_hash` (NFR-P1 / the `_cartridge.py` HEAD-pin approach); NO
   source/secret byte from ANY cartridge (incl. the planted secrets + the canary + the non-ASCII paths) ever
   appears in the harness's read surface or any `.apaa/` artifact it inspects (NFR-S1 — this story's cartridge
   audits flow through the EXISTING 4.4 randomized-canary containment suite, extended if a NEW write path or
   a NEW cartridge is introduced); a non-ASCII cartridge (`nonascii_unicode` / `secret_canary`'s
   `café/модуль_секрет.py`) audits + grades + serializes under `PYTHONIOENCODING=utf-8` (AI-E1-1).

**The cartridge registry — designed for N=5, populated phased (DN-REGISTRY).** Build a single
parametrized registry (a frozen dataclass / tuple of `CartridgeSpec`) keyed by cartridge id, each carrying:
the cartridge id (→ `stage_cartridge`), the **golden expected-findings key** (the SET of expected `(rule_id,
verdict_eligible?, advisory?)` tuples — NOT a count, NOT source bytes), the expected verdict + exit code, a
`kind` ∈ `{planted_defect, clean_control, holdout, trap}`, and a `provisional: bool` / `gate_status` marker.
The harness parametrizes over the registry so a NEW cartridge is a registry row + a `*.py.txt` template
drop-in — NO harness-code refactor (the README's additive promise; the N=5 design). The golden keys are the
LOCKED, documented expected-findings — they live in the registry (the durable, committed, §3.4 source of
truth), not scattered in assertions.

**The gate-status honesty marker (DN-GATE-STATUS — the OI1 keystone).** The harness must EXPOSE (in a
docstring constant + a documented marker the test asserts, e.g. `PRECISION_GATE_STATUS = "provisional
(N=<populated_count> < 5; precision measured over findings; ≥80% gate cleared in Story 6.6 at N≥5)"`) that
the precision gate is PROVISIONAL. This is a COMMITTED, durable statement of the honest-coverage limitation —
not a comment that rots. It is the mechanized form of "do not overclaim a precision number from too few
cartridges." Story 6.6 flips it to non-provisional only when N≥5 with sufficient findings.

**REUSE the signature-demo harness patterns — no second pipeline runner (§3.3).** `test_pipeline_signature_demo.py`
already proves: stage → `run_audit` / `run_audit_detailed` → assert verdict / exit / ordered findings; two
runs → byte-identical `content_hash`; clean control → `RELEASE_READY` exit 0. The 6.5 harness GENERALIZES
that into the parametrized registry over MORE cartridges + the holdout + the trap + the golden-key SET match
+ the gate-status marker. It composes `stage_cartridge` + `run_audit_detailed` + `ApaaStoreReader` exactly as
the signature-demo + 3.x e2e tests do — it does NOT add a parallel pipeline.

**THE SIZE CONSTRAINT — the harness is a TEST module; mind ≤1200 lines (NFR-M1 / §3.2).** The harness + the
registry are tests + a small fixtures/registry helper. Keep the registry data in a cohesive helper
(`tests/apaa/cartridges/_registry.py` or top-of-module) and the parametrized assertions thin. If the harness
module approaches 1200 lines, split by member (true-positive / clean-control / holdout-trap) into sibling
test modules sharing the registry helper — measure first, do not split speculatively. The cartridge
templates are `*.py.txt` (NOT collected by pytest — the `_cartridge.py` precedent).

**Scope vs the rest of Epic 6 (explicit deferrals — do NOT pull forward).**
- **6.6 precision replay harness + validation protocol (FR20 / OI1 N=5)** — the EMPIRICAL ≥80%-precision
  NUMBER, the `precision/replay_harness.py` that diffs findings against labeled ground truth, the validation
  protocol (who validates, expert-hours/repo, the precision-adjudication method, per-metric pass/fail), and
  the physical growth of the corpus to N=5 with the ground-truth schema FROZEN are 6.6. **6.5 builds the
  measurement SUBSTRATE (the cartridge harness + golden keys + holdout + clean controls + the
  provisional-gate marker); 6.6 computes the number on top of it.** 6.5 MUST NOT compute or assert an 80%
  precision figure.
- **6.7 HITL STOP/PROCEED escalation + append-only decision record (FR23/FR24)** — out of scope.
- **A new detector / a change to any 6.1–6.4 detector or the Prosecutor** — out of scope. The harness
  MEASURES the existing detectors; it does not add or tune one. If a cartridge reveals a detector gap, that
  is a FINDING (file a defer), not a 6.5 detector edit.
- **Editing the frozen Epic-1..6 contracts** (`coverage_ledger.py` / `recording.py` / `verdict_gate.py` /
  `partitioner.py` / `detectors/*` / `prosecutor.py` / `pipeline.py` / `store/*` / `cache/*` / `models.py`) —
  the harness COMPOSES them as-is. The ONLY production-tree touch this story may make is appending new
  cartridge-module ids to the no-web-imports guard tuple ONLY if a new APAA library module is introduced
  (it should not be — the harness is a test).
- **A new `.github/workflows` CI job** — the harness is a `tests/apaa/` pytest module; it runs under the
  EXISTING APAA pytest CI invocation (the durable backstop, AR9). NO new CI job is authored (mirrors the
  6.1–6.4 "no new CI job" fence).
- **A new HTTP route / FastAPI surface / UI (§3.7) / a new `cli.py` flag** — out of scope.

**Carry-forward action items (CLAUDE.md §9.1 / L1-E11 — each 6.x story cites its AI-E5-* item).**
- **AI-E5-1 (test-infra 🟠) — the COMPLETE-THE-DECLARED-SET keystone-adequacy checklist.** Applied to 6.5:
  enumerate the FULL declared set of cartridge MEMBERS — (1) golden-key true positive per planted-defect
  cartridge; (2) clean-control true negative (any 🔴 = instant fail); (3) hidden holdout; (4) false-negative
  trap (citation-gaming); (5) determinism + secret-containment + non-ASCII over the corpus — and demonstrate
  EACH covered (RED-first where a naive harness would miss it, especially the clean-control floor + the
  trap). The enumeration is explicit in the harness module (the practice that caught the 6.2 construct set /
  the 6.3 input set / the 6.4 decision space).
- **AI-E5-2 (test-infra 🟠) — MECHANIZE fixture-shape coverage in the 6.5 cartridge harness.** This is the
  story the retro named for AI-E5-2: the cartridge registry IS the mechanized fixture-shape coverage. The
  registry must be parametrized so the declared cartridge set is mechanically iterated (no hand-copied
  per-cartridge test bodies), and the gate-status marker is mechanized (a committed constant the test
  asserts), not a prose promise.
- **AI-E4-2 (test-infra) — mechanize the no-crash input-shape checklist AS CARTRIDGES.** The 6.5 harness is
  the natural home: the no-crash / honest-degradation input shapes (a tool-failure repo, an
  unestablishable-traceability repo, a budget-exhausted repo, a malformed/parse-failure file) become CARTRIDGE
  rows in the registry where the GOLDEN key is "degrades to a typed finding / honest verdict, NEVER an
  uncaught crash" (AR10 / NFR-R1). Add ≥1 such no-crash cartridge row (or reuse `tool_breadth` / a
  parse-failure fixture) so the no-crash checklist is mechanized as a cartridge, not only as scattered unit
  tests.
- **AI-E5-1 no-crash leg (AR10 / NFR-R1).** The harness itself must never raise opaquely: a missing cartridge
  id, an empty/absent golden key, a `stage_cartridge` git failure → a clear, NAMED test failure (an assertion
  with the cartridge id), never a bare traceback that hides which cartridge failed.
- **AI-E1-1 (test-infra 🟢) — non-ASCII / locale discipline (the Epic-1-FAIL class, standing).** ≥1 cartridge
  in the registry carries a non-ASCII path / module / planted value (`nonascii_unicode` /
  `secret_canary`'s `café/модуль_секрет.py`); it audits + grades + serializes + matches its golden key under
  `PYTHONIOENCODING=utf-8` (the single serializer is `ensure_ascii=False`).
- **AI-E5-4 (governance 🟢) — central defer register.** If 6.5 surfaces a detector gap, a missing-cartridge
  need, or a known overfitting risk it does NOT close, file it append-only in
  `_bmad-output/design-artifacts/APAA/deferred-work.md` with the six CC-3 fields (`target_story` e.g.
  `6-6-precision-replay-harness-validation-protocol` for "grow corpus to N=5" or an Epic-6/V2 key).
- **AI-E5-7 (process 🟢) — keep the structural gates green + partial-reuse docstring precision.** The harness
  keeps the no-web-imports gate, the single-serializer AST gate, and the file-size gate green (it adds NO
  `json.dumps`/hasher/parse — it READS through the EXISTING `ApaaStoreReader` + asserts on `Recording`
  fields). When reuse is PARTIAL (reuses `stage_cartridge` + `run_audit_detailed` + `ApaaStoreReader`,
  composes a NEW registry + golden keys), narrate it precisely ("reuses the 1.7 staging + pipeline + reader;
  adds a parametrized cartridge registry + golden expected-findings keys", not "reuses the signature-demo
  test wholesale").
- **AI-E5-3 (process 🟠) — committed pre-`review` test-existence guard.** The harness + the registry + the
  holdout cartridge + the trap + the gate-status marker EXIST + pass before the `review` flip.
- **NFR-S1 secret-containment (standing CI-blocking moat).** The harness audits secret-bearing cartridges
  (`hardcoded_secret`, `secret_canary`, `evidence_sentinel`); it MUST assert the planted secret + the canary
  + any source sentinel are ABSENT from the findings / verdict / ledger it reads (the redaction guarantee),
  and these audits flow through the EXISTING 4.4 randomized-canary suite (extend the suite if a NEW cartridge
  or write path is introduced).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 6.5) + the architecture (FR20 defect-cartridge self-audit,
> CI-asserted; AR9 committed/durable CI gates; the cartridges README additive-extension promise) + the PRD
> (FR20 + FR13 locator-or-reject + the ≥80%-precision externalization gate) + the OI1 LOCK (N=5, phased 3→5,
> precision over findings, provisional below N=5). Drivers: **APAA-FR-20** (APAA validates its own detectors
> against defect cartridges with golden expected-findings keys, asserted in CI), **APAA-FR-13** (every
> finding carries ≥1 verifiable locator or is rejected — asserted in each golden key), **APAA-NFR-D1/D2**
> (the cartridge audits are deterministic + zero-LLM-token — the V1 pipeline), **APAA-NFR-P1** (each
> cartridge audited twice → byte-identical verdict envelope `content_hash`), **APAA-NFR-S1** (no
> source/secret bytes from any cartridge — incl. the planted secrets + canary + non-ASCII paths — in any
> read surface or `.apaa/` artifact; flows through the 4.4 suite), **APAA-AR9** (the harness is a committed,
> durable CI gate under the existing APAA pytest invocation), **APAA-AR10 / NFR-R1** (the no-crash cartridge
> rows: an honest-degradation input degrades to a typed finding / honest verdict, never an uncaught crash —
> AI-E4-2 mechanized as cartridges), **APAA-NFR-M1/M2** (≤1200-line files; frozen Epic-1..6 contracts
> unchanged), **APAA-AR4** (golden keys + counts are `int`/`str`/sets, never float; content-derived).
>
> **SCOPE FENCE — Tier-B, single-purpose, the FR20 cartridge self-audit harness + holdout + clean controls +
> the provisional-gate marker.** This story delivers ONLY: (1) the parametrized cartridge **registry**
> (designed for N=5) with per-cartridge **golden expected-findings keys** + a `kind` +
> provisional/gate-status marker; (2) the **harness** (`tests/apaa/test_cartridge_selfaudit.py`) that runs
> the FULL deterministic pipeline over the registry and asserts each member — golden-key true positive,
> clean-control true-negative (any 🔴 = instant fail), hidden holdout, false-negative trap, determinism +
> secret-containment + non-ASCII; (3) the **hidden holdout** cartridge (a NEW `*.py.txt` cartridge); (4) ≥1
> **no-crash cartridge row** (AI-E4-2 mechanization); (5) the **gate-status honesty marker** (PROVISIONAL
> until N≥5, mechanized); (6) any NEW defer (a detector gap / "grow corpus to N=5") filed with the six CC-3
> fields. It does NOT build, and MUST NOT pull forward: the **precision replay harness / the empirical ≥80%
> precision NUMBER / the validation protocol / the FROZEN ground-truth schema** (6.6 — 6.5 stops at the
> golden-key substrate + the provisional marker); the **HITL STOP/PROCEED + decision record** (6.7); a **new
> detector or any change to a 6.1–6.4 detector / the Prosecutor**; an **edit to any frozen Epic-1..6
> contract** (compose them as-is); a **new `.github/workflows` CI job**; a **new HTTP route / FastAPI surface
> / UI** (§3.7); a **new `cli.py` flag**.

**AC1 — A parametrized cartridge registry (designed for N=5) carries a golden expected-findings key per cartridge (FR20 / AR9 / AI-E5-2 mechanization)**
**Given** a single committed cartridge **registry** (a frozen `CartridgeSpec` tuple/dataclass set, in a
cohesive helper such as `tests/apaa/cartridges/_registry.py`) keyed by cartridge id, each row carrying the
cartridge id, a **golden expected-findings key** (the SET of expected `(rule_id, verdict_eligible?,
advisory?)` tuples — NOT a count, NOT source bytes), the expected verdict + exit code, a `kind` ∈
`{planted_defect, clean_control, holdout, trap}`, and a `provisional`/gate-status marker
**When** the harness `tests/apaa/test_cartridge_selfaudit.py` parametrizes over the registry
**Then** the declared cartridge set is iterated MECHANICALLY (no hand-copied per-cartridge bodies — AI-E5-2),
the registry is SHAPED for N=5 (a NEW cartridge is a registry row + a `*.py.txt` template drop-in with NO
harness-code refactor — the README additive promise), and the golden keys live in the committed registry
(the durable §3.4 source of truth), not scattered in inline assertions.

**AC2 — Each planted-defect cartridge's planted defect is caught — the golden-key true positive, CI-asserted (FR20 / FR13)**
**Given** the planted-defect cartridges — `vacuous_basic` (planted vacuous test → golden key
`vacuous_test_ast`, verdict-eligible), `hardcoded_secret` (planted secret → the redacted-secret golden key,
value ABSENT), `orphan_basic` (planted `unused_helper` → golden key `orphan_code`, advisory)
**When** the harness runs the FULL pipeline (`run_audit_detailed`) over each
**Then** the audit emits ≥1 finding whose `rule_id` matches the cartridge's golden key, carrying ≥1
verifiable locator (FR13 — a locator-less finding would have been rejected, not emitted), and the
verdict/exit match the golden expectation (vacuous → `NOT_READY_FOR_RELEASE`/exit 2, the blocking finding
sorts FIRST per FR33; orphan advisory does NOT alone move the verdict to 🔴 — the 1.5/6.3/6.4
advisory-by-contract floor), and the assertion failure names the cartridge id (the AI-E5-1 no-crash leg — a
clear NAMED failure, never an opaque traceback).

**AC3 — A clean-control cartridge produces ZERO blocking findings — any 🔴 is an instant CI fail (the false-accusation floor / FR20)**
**Given** a clean-control cartridge (`clean_control`, two clean SUTs + a genuine well-asserting test, NO
planted defect)
**When** the harness audits it
**Then** the verdict is `RELEASE_READY` / exit 0 with **ZERO blocking findings**, and the harness asserts
that **any blocking 🔴 is an instant CI fail** (the false-accusation floor — the moat the tool's credibility
rests on); a clean-control row with `blocking_finding_count > 0` FAILS the harness with a NAMED assertion
citing the offending finding's `rule_id` + locator (never source bytes).

**AC4 — A hidden holdout cartridge is exercised + gated with NO detector change (the overfitting defense / FR20)**
**Given** a hidden holdout cartridge (a NEW `*.py.txt` cartridge — see DN-HOLDOUT — the detector authors did
NOT tune the detectors against it)
**When** the harness audits it through the SAME detectors with NO detector-code change
**Then** its planted defect is caught by its golden key (proving the detectors GENERALIZE, not memorize), the
holdout is marked `kind=holdout` in the registry, and a clean-holdout variant (if the holdout is a
clean-control-style holdout) produces zero blocking findings — the harness gates the holdout exactly like a
labeled cartridge so an overfit detector that only catches the tuned examples would FAIL here.

**AC5 — A false-negative / citation-gaming trap is included so a naive detector is caught (the gaming defense / FR20)**
**Given** a false-negative trap cartridge / fixture (citation-gaming — e.g. a repo whose code would tempt a
naive detector into a finding that cites a real locator but describes nothing real, OR a genuine defect that
resembles benign code; the `evidence_sentinel` surface is the natural home)
**When** the harness audits it
**Then** the harness asserts the trap's golden expectation — a citation-gaming false positive is REJECTED
(the clean-control floor catches it), or a benign-looking genuine defect is still caught — so a naive /
gamed detector FAILS the harness (the trap is RED-first against a naive implementation), and the trap row is
marked `kind=trap` in the registry.

**AC6 — Determinism + secret-containment + non-ASCII hold over the WHOLE corpus (NFR-D1/D2 / NFR-P1 / NFR-S1 / AI-E1-1)**
**Given** every cartridge in the registry
**When** each is audited
**Then** (a) the audit is deterministic + ZERO-LLM-token (NFR-D2 — the V1 pipeline calls no LLM); (b) each
cartridge audited TWICE yields a byte-identical verdict envelope `content_hash` (NFR-P1 — the `_cartridge.py`
HEAD-pin approach, the signature-demo determinism precedent); (c) NO source/secret byte from ANY cartridge
(the planted secrets in `hardcoded_secret`/`secret_canary`/`evidence_sentinel`, the canary, the source
sentinel, the non-ASCII paths) appears in the findings / verdict / ledger the harness reads (NFR-S1 — these
audits flow through the EXISTING 4.4 randomized-canary suite; extend the suite if a NEW cartridge or write
path is introduced); (d) ≥1 non-ASCII cartridge (`nonascii_unicode` / `secret_canary`'s
`café/модуль_секрет.py`) audits + grades + serializes + matches its golden key under `PYTHONIOENCODING=utf-8`
(AI-E1-1).

**AC7 — The precision gate is mechanically reported PROVISIONAL until N≥5 — the OI1 honesty keystone (FR20 / OI1)**
**Given** the OI1 LOCK — `N=5` V1 gate floor, populated phased 3→5, precision measured over findings, the
≥80%-precision gate PROVISIONAL below N=5
**When** the harness reports its gate status
**Then** a COMMITTED, mechanized marker (a docstring/module constant the harness ASSERTS — e.g.
`PRECISION_GATE_STATUS = "provisional (N=<populated_planted_defect_count> < 5; precision measured over
findings; ≥80% gate cleared in Story 6.6 at N≥5)"`) states the gate is PROVISIONAL, the harness does NOT
compute or assert any ≥80% precision NUMBER (that is 6.6 — scope fence), and the Dev Notes + the harness
docstring are scrupulously honest that the cartridge count is N=3-going-on-5 and the precision claim is
provisional (do NOT overclaim a precision number from too few cartridges — honest coverage is APAA's whole
thesis). Story 6.6 flips the marker to non-provisional only at N≥5 with sufficient findings.

**AC8 — Complete-the-declared-set + no-crash matrix over the cartridge members, each RED-first where applicable (AI-E5-1 / AI-E4-2 / AR10)**
**Given** the full DECLARED set of cartridge members
**When** the harness is built
**Then** EACH member is explicitly covered: (1) golden-key true positive per planted-defect cartridge (AC2);
(2) clean-control true negative — any 🔴 = instant fail (AC3 — RED-first against a detector that false-flags
clean code); (3) hidden holdout (AC4 — RED-first against an overfit detector); (4) false-negative /
citation-gaming trap (AC5 — RED-first against a gamed detector); (5) determinism + secret-containment +
non-ASCII (AC6); AND (6) ≥1 **no-crash cartridge row** mechanizing the AI-E4-2 input-shape checklist — an
honest-degradation input (a tool-failure / parse-failure / budget-exhausted shape; reuse `tool_breadth` or a
parse-failure fixture) whose golden expectation is "degrades to a typed finding / honest verdict, NEVER an
uncaught crash" (AR10/NFR-R1) — and the enumeration is EXPLICIT in the harness module (the
complete-the-declared-set discipline). The harness itself never raises opaquely (a missing cartridge id /
empty golden key / staging failure → a NAMED assertion citing the cartridge id, never a bare traceback).

**AC9 — No regression / no scope creep; structural gates green; ≤1200 lines; the pre-`review` test-existence precondition (AI-E5-7 / AI-E5-3 / NFR-M1/M2)**
**Given** the new harness + registry + holdout cartridge + trap + gate-status marker + their tests
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the prior green baseline + the new 6.5 cartridge-harness tests), the no-web-imports gate, the
single-serializer AST gate, and the file-size gate stay green; `mypy` is clean on any new/modified modules
**And** NO production-tree behavior changes (the harness COMPOSES the existing pipeline/detectors/Prosecutor;
NO new detector, NO detector/Prosecutor edit, NO frozen-contract diff — `coverage_ledger.py` / `recording.py`
/ `verdict_gate.py` / `partitioner.py` / `detectors/*` / `prosecutor.py` / `pipeline.py` / `store/*` /
`cache/*` / `models.py` show NO working-tree diff), NO new `.apaa/` write path (the harness READS through the
EXISTING `ApaaStoreReader`), NO `cli.py` flag, NO HTTP route, NO new CI job, NO live LLM call
**And** each new/modified file is ≤1200 lines (NFR-M1 — split the harness by member into sibling modules
sharing the registry helper ONLY if it approaches the limit; measure first); the new test files cite their
`APAA-FR-20` / `APAA-FR-13` / `APAA-NFR-S1` / `APAA-AR10` drivers in the module docstring + the locked test
area / index; the mandatory artifacts EXIST + pass + any new defer is filed BEFORE the story flips to
`status: review` (AI-E5-3 / AI-E2-1 test-existence discipline). **Test area `APAA-CARTRIDGE`** (the existing
`_cartridge.py` area — `TC-APAA-CARTRIDGE-001-NN`, start at the next free index; lock the area + index in the
module docstring). The cartridge templates are `*.py.txt` (NOT collected by pytest — the `_cartridge.py`
precedent).

## Tasks / Subtasks

- [x] **Task 0 — Re-read the REAL surfaces; LOCK the registry shape (DN-REGISTRY), the golden keys, the holdout approach (DN-HOLDOUT), the gate-status marker (DN-GATE-STATUS), and the declared cartridge set** (AC: 1, 2, 7, 8)
  - [x] Re-read `tests/apaa/cartridges/_cartridge.py::stage_cartridge` + `tests/apaa/cartridges/README.md`
        (the LOCKED cartridge-pinning approach + the additive-extension promise). LOCK: REUSE `stage_cartridge`
        verbatim; cartridges are `*.py.txt` templates.
  - [x] Re-read `tests/apaa/test_pipeline_signature_demo.py` (the stage → `run_audit_detailed` → assert
        verdict/exit/ordered-findings + two-run byte-identical `content_hash` + clean-control floor patterns).
        LOCK: GENERALIZE these into the parametrized registry; do NOT add a parallel pipeline runner (§3.3).
  - [x] Re-read `minions_core/apaa/ledger/recording.py` (`rule_id` / `finding_id` / `locators` ≥1 /
        `advisory` / `depth_supported`) + the done detectors' LOCKED `rule_id`s (`vacuous_test_ast`,
        `orphan_code`, the secret detector's redacted-finding rule). LOCK the golden-key match field set
        (`(rule_id, verdict_eligible?, advisory?)` tuples; NEVER source bytes).
  - [x] Inventory the populated cartridges (`vacuous_basic`, `clean_control`, `hardcoded_secret`,
        `secret_canary`, `evidence_sentinel`, `nonascii_unicode`, `orphan_basic`, `tool_breadth`) + their
        planted conditions; map each to a registry `kind` + golden key. Identify which serve as
        planted-defect / clean-control / trap / non-crash, and what the NEW holdout cartridge must be.
  - [x] Enumerate + LOCK the DECLARED cartridge member set (AC8 (1)–(6)) + DN-REGISTRY + DN-HOLDOUT +
        DN-GATE-STATUS + the OI1 honesty constraints (N=5 design, phased 3→5, precision over findings,
        provisional below N=5). Record the locked rules + the honest-coverage rationale in Dev Notes.
- [x] **Task 1 — Build the parametrized cartridge registry (designed for N=5)** (AC: 1, 7)
  - [x] `tests/apaa/cartridges/_registry.py` (or a top-of-harness helper): a frozen `CartridgeSpec`
        tuple/dataclass set keyed by cartridge id, each row = id + golden expected-findings key (SET of
        `(rule_id, verdict_eligible?, advisory?)`) + expected verdict/exit + `kind` ∈ `{planted_defect,
        clean_control, holdout, trap}` + provisional/gate-status. Shaped so a NEW cartridge = a row + a
        `*.py.txt` drop-in (NO harness refactor). The `PRECISION_GATE_STATUS` marker constant lives here
        (DN-GATE-STATUS), mechanically derived from the populated planted-defect count.
- [x] **Task 2 — Author the NEW hidden holdout cartridge + (if needed) the no-crash cartridge row** (AC: 4, 8)
  - [x] A NEW `tests/apaa/cartridges/<holdout-id>/...py.txt` cartridge the detectors were not tuned against
        (DN-HOLDOUT — document precisely what "hidden" means in a single-repo V1: a cartridge added in THIS
        story whose planted defect was NOT used to shape any detector's heuristics, gated like a labeled
        cartridge). Register it `kind=holdout` with its golden key.
  - [x] A no-crash cartridge ROW (reuse `tool_breadth` / add a parse-failure fixture) whose golden
        expectation is "degrades to a typed finding / honest verdict, NEVER an uncaught crash" (AI-E4-2
        mechanization / AR10).
- [x] **Task 3 — Build the parametrized harness over the registry** (AC: 2, 3, 4, 5, 6, 8)
  - [x] `tests/apaa/test_cartridge_selfaudit.py` (area `APAA-CARTRIDGE`, `TC-APAA-CARTRIDGE-001-NN` from the
        next free index): parametrize over the registry; per `kind` assert — planted_defect → golden-key true
        positive + locator + verdict/exit + FR33 ordering (AC2); clean_control → zero blocking findings, any
        🔴 = NAMED instant fail (AC3); holdout → caught with no detector change (AC4); trap → naive/gamed
        detector fails (AC5, RED-first). Each assertion failure NAMES the cartridge id (no opaque traceback).
  - [x] Determinism: each cartridge audited twice → byte-identical verdict envelope `content_hash` (AC6 /
        NFR-P1). Non-ASCII cartridge audits + matches its golden key under `PYTHONIOENCODING=utf-8` (AI-E1-1).
  - [x] Assert the `PRECISION_GATE_STATUS` marker is PROVISIONAL + the harness asserts NO ≥80% number is
        computed (AC7 — the OI1 honesty keystone).
- [x] **Task 4 — Secret-containment over the secret-bearing cartridges (extend the 4.4 suite if needed)** (AC: 6)
  - [x] Assert the planted secrets (`hardcoded_secret`/`secret_canary`), the canary, and the
        `evidence_sentinel` source sentinel are ABSENT from the findings/verdict/ledger the harness reads
        (NFR-S1 producer guarantee). If a NEW cartridge or write path is introduced, EXTEND
        `tests/security/test_apaa_secret_containment.py` (the 4.4 randomized-canary suite) to sweep it (do not
        fork).
- [x] **Task 5 — Run + mypy + gates + any NEW defer + the pre-`review` precondition** (AC: 9)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
        all pass (prior baseline + the new 6.5 cartridge-harness tests). `mypy` clean on any new modules.
  - [x] Confirm NO working-tree diff to the frozen Epic-1..6 production surfaces (the harness is a test +
        cartridge templates + a registry helper). Confirm the no-web-imports + single-serializer + file-size
        gates green. NO `cli.py`/HTTP/CI-job change; NO new detector/Prosecutor edit; NO live LLM.
  - [x] **AI-E5-4:** if 6.5 surfaces a detector gap, an overfitting risk, or a "grow corpus to N=5" item it
        does NOT close, file it append-only in `_bmad-output/design-artifacts/APAA/deferred-work.md` with the
        six CC-3 fields (`target_story` e.g. `6-6-precision-replay-harness-validation-protocol`).
  - [x] **AI-E5-3 / AI-E2-1 GATE:** the mandatory artifacts (the registry + the harness + the holdout
        cartridge + the trap + the no-crash row + the gate-status marker + the new tests) EXIST + pass BEFORE
        the `review` flip; the Dev Agent Record is filled completely (no blank placeholders), incl. the locked
        DN-REGISTRY / DN-HOLDOUT / DN-GATE-STATUS rules + the populated-vs-N=5 honesty statement.

## Dev Notes

### Architecture / contract anchors (re-read before coding)
- **Cartridge staging — REUSE, do not re-implement:** `tests/apaa/cartridges/_cartridge.py::stage_cartridge`
  (the LOCKED HEAD-pin / fresh-single-commit approach) + `tests/apaa/cartridges/README.md` (the additive
  extension promise — 6.5 drops in cartridges with no refactor).
- **Pipeline — REUSE:** `minions_core/apaa/pipeline.py::run_audit` / `run_audit_detailed` (deterministic,
  zero-token V1 path). `tests/apaa/test_pipeline_signature_demo.py` is the pattern to GENERALIZE.
- **Finding contract:** `minions_core/apaa/ledger/recording.py::Recording` (`rule_id` golden-key match field;
  `locators` ≥1 = FR13; `advisory` / `depth_supported` = the verdict-eligibility / advisory-by-contract
  flags). Reader: `minions_core/apaa/store/reader.py::ApaaStoreReader` (re-verifies `content_hash`).
- **Golden-key `rule_id`s (LOCKED by the done detectors):** `vacuous_test_ast` (1.5, verdict-eligible);
  the secret detector's redacted-secret rule (2.5, `contained_secret`); `orphan_code` (6.3, advisory);
  `cross_partition` (6.4, advisory — only if a multi-partition cartridge is added, optional).
- **Secret-containment suite (EXTEND, do not fork):** `tests/security/test_apaa_secret_containment.py` (4.4).
- **Structural gates:** `tests/apaa/test_no_web_imports.py` (no-web-imports), the single-serializer AST gate,
  the file-size gate.

### Locked decisions (resolve in dev; recorded here per §3.4)
- **DN-REGISTRY.** A single committed, frozen `CartridgeSpec` registry (helper module / top-of-harness),
  parametrized so the declared set iterates mechanically (AI-E5-2) and a NEW cartridge is a row + a `*.py.txt`
  drop-in (the N=5 design / README promise). Golden keys are SETS of `(rule_id, verdict_eligible?,
  advisory?)` tuples — NOT counts, NEVER source bytes. The registry is the durable §3.4 source of truth for
  the golden expected-findings.
- **DN-HOLDOUT.** "Hidden holdout" in a single-repo V1 means: a cartridge ADDED in this story whose planted
  defect was NOT used to shape/tune any detector's heuristics (the detectors are frozen from 6.1–6.4), gated
  exactly like a labeled cartridge — so an overfit detector that only catches the tuned examples fails. Document
  this precise V1 meaning in the harness docstring + Dev Notes (a true author-blind holdout corpus is a 6.6 /
  validation-protocol concern). The holdout is a NEW `*.py.txt` cartridge, marked `kind=holdout`.
- **DN-GATE-STATUS (the OI1 keystone).** A committed, mechanized `PRECISION_GATE_STATUS` marker (a constant
  the harness ASSERTS) states the precision gate is PROVISIONAL (N populated < 5; precision measured over
  findings; ≥80% gate cleared in Story 6.6 at N≥5). 6.5 computes NO ≥80% number. Story 6.6 flips the marker.
  This mechanizes "do not overclaim a precision number from too few cartridges."
- **DN-NO-PROD-CHANGE.** 6.5 is a TEST/HARNESS + cartridge-template + registry-helper story. It adds NO
  detector, edits NO detector/Prosecutor/frozen contract, adds NO `.apaa/` write path. The ONLY conceivable
  production-tree touch is appending a module id to the no-web-imports guard tuple — and only if a new APAA
  *library* module is introduced (it should not be). If a cartridge reveals a detector gap, that is a DEFER
  (AI-E5-4), not a 6.5 detector edit.

### OI1 honesty constraints (the central theme — do NOT soften)
- `N` is LOCKED at 5 (V1 gate floor). The harness/registry are DESIGNED for 5.
- Population is PHASED 3→5: this story stands up the harness + the 3 planted-defect cartridges (vacuous /
  secret / orphan) + clean controls + a holdout + a trap. Physically reaching 5 distinct planted-defect
  cartridges may continue into 6.6 / M1 — but the registry + harness MUST be shaped for 5 and the gate-status
  honest.
- Precision is measured over FINDINGS, not repos (the golden key is a finding SET).
- The ≥80%-precision gate is PROVISIONAL below N=5 — surfaced via the mechanized DN-GATE-STATUS marker.

### Carry-forward action items addressed
- **AI-E5-1** — complete-the-declared-set over the cartridge members (AC8), RED-first on the clean-control
  floor + the trap + the holdout.
- **AI-E5-2** — MECHANIZE fixture-shape coverage via the parametrized registry + the mechanized gate marker
  (this is the retro-named home for AI-E5-2).
- **AI-E4-2** — mechanize the no-crash input-shape checklist AS a cartridge row (AC8 (6)).
- **AI-E1-1** — non-ASCII cartridge (`nonascii_unicode` / `secret_canary`) under `PYTHONIOENCODING=utf-8`.
- **AI-E5-3 / AI-E5-7** — pre-`review` test-existence + structural gates green + partial-reuse docstring
  precision.

## Dev Agent Record

### Context Reference

- Story: `_bmad-output/design-artifacts/APAA/stories/6-5-defect-cartridge-self-audit-harness-holdout-clean-controls.md` (FR20 defect-cartridge self-audit harness, Tier-B).
- Reused substrate (by import, no fork — §3.3 / AR7): `tests/apaa/cartridges/_cartridge.py::stage_cartridge` (the 1.7 fresh-single-commit cartridge-pinning helper), `minions_core/apaa/pipeline.py::run_audit_detailed` (the deterministic zero-token V1 pipeline), `minions_core/apaa/store/reader.py::ApaaStoreReader` (the tamper-guard reader), `minions_core/apaa/ledger/recording.py::Recording` (`rule_id`/`locators`/`advisory`/`depth_supported` — the golden-key match fields).
- Pattern generalized: `tests/apaa/test_pipeline_signature_demo.py` (stage → audit → assert verdict/exit/ordered-findings + two-run byte-identical `content_hash` + clean-control floor).
- Project rules: `CLAUDE.md` §3.2 (≤1200 lines), §3.4 (evidence immutability), §3.7 (headless), §3.8 (12-Factor + secret masking); APAA `_bmad-output/design-artifacts/APAA/` planning + own sprint tracker.

### Agent Model Used

Claude Opus 4.8 (1M context) — `claude-opus-4-8[1m]`. BMAD `dev-story` (RESUME pass).

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/test_cartridge_selfaudit.py -v` → 33 passed in 7.56s.
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` → 1165 passed, 1 skipped, 4 subtests passed in 70.88s.
- Structural gates: `tests/apaa/test_no_web_imports.py` + `tests/apaa/test_canonical_single_serializer.py` + `tests/apaa/test_store_integrity_lint.py` → 38 passed.
- 4.4 randomized-canary suite: `tests/security/test_apaa_secret_containment.py` → 22 passed.
- `python -m mypy tests/apaa/cartridges/_registry.py` → Success: no issues found.
- `git diff --stat` over the frozen Epic-1..6 production surfaces (`coverage_ledger.py`, `recording.py`, `verdict_gate.py`, `detectors/*`, `prosecutor.py`, `pipeline.py`, `store/*`, `cache/*`, `models.py`) → EMPTY (no working-tree diff; the only tracked-file diff in `minions_core/apaa/` is `__init__.py`'s story-1.1 `__version__` constant, NOT a 6.5 change).

### Completion Notes List

This was a RESUME pass: a prior dev-story session had authored the harness, registry, and holdout cartridge on disk (untracked) but left the Dev Agent Record empty and the status at `in-progress`. I VERIFIED the existing artifacts against every AC by running the real suites (per the "verify before reporting" discipline) rather than re-authoring, then completed the record and flipped to `review`. All artifacts exist and pass.

Complete-the-declared-set matrix (AC8) — each member covered + verified green:
- (1) Golden-key true positive per planted-defect cartridge (AC2) — `vacuous_basic` → `vacuous_test_ast` (verdict-eligible, sorts first / FR33, NOT_READY/exit 2); `hardcoded_secret` → redacted advisory secret finding (value ABSENT, RELEASE_READY/exit 0, advisory does not block); `orphan_basic` → advisory `orphan_code` (NOT_READY/exit 2 on the deep-% gate, zero blocking — the 6.3 advisory floor). Each finding carries ≥1 verifiable locator (FR13). TC-APAA-CARTRIDGE-001-02.
- (2) Clean-control true negative (AC3) — `clean_control` → RELEASE_READY/exit 0, ZERO blocking; any 🔴 = NAMED instant fail. TC-APAA-CARTRIDGE-001-03/-04.
- (3) Hidden holdout (AC4) — `holdout_vacuous` (a NEW `*.py.txt` cartridge: differently-named/-structured vacuous defect — `total_stock`/`Mock.tally` vs `compute_total`/`Mock.calculate` — authored after the 6.1–6.4 detectors were frozen, never used to tune any heuristic) caught by the SAME `vacuous_test_ast` rule with NO detector change. TC-APAA-CARTRIDGE-001-05.
- (4) Citation-gaming trap (AC5) — `evidence_sentinel` (planted source sentinel + secret) emits only the advisory redacted-secret finding; a naive detector that citation-games a blocking finding would breach `max_blocking==0` and FAIL. TC-APAA-CARTRIDGE-001-06.
- (5) Determinism + secret-containment + non-ASCII (AC6) — every cartridge audited TWICE → byte-identical verdict envelope `content_hash`; `nonascii_unicode` (Cyrillic/café path) + `tool_breadth` audit/grade/serialize under `PYTHONIOENCODING=utf-8`; planted secrets/source sentinels ABSENT from the `.apaa/` blob + finding/verdict reprs; the secret finding is structurally value-free. TC-APAA-CARTRIDGE-001-07/-08/-09/-10.
- (6) No-crash row (AC8(6) / AI-E4-2 / AR10) — `tool_breadth` (breadth-tool surface, non-ASCII module paths, no test files) degrades to a typed `Verdict` with a valid exit code, never an uncaught crash. The `_audit` helper converts ANY staging/audit raise into a NAMED assertion citing the cartridge id (the AI-E5-1 no-crash leg). TC-APAA-CARTRIDGE-001-11.

OI1 honesty keystone (AC7) — `PRECISION_GATE_STATUS` (a committed, mechanically-derived constant the harness ASSERTS) reports the precision gate PROVISIONAL UNCONDITIONALLY in 6.5: it states N=labeled-cartridge-count populated, floor N=5, "precision measured over findings not repos", and "NO precision number computed here — … computed + cleared in Story 6.6 at N>=5". The harness computes NO ≥80% figure (scope fence; verified `%` and `PRECISION_VALUE`/`MEASURED_PRECISION` are absent). TC-APAA-CARTRIDGE-001-13/-14.

Locked decisions (per §3.4):
- DN-REGISTRY — `tests/apaa/cartridges/_registry.py` holds a frozen `CartridgeSpec` tuple keyed by cartridge id; golden keys are SETS of `GoldenFinding(rule_id, verdict_eligible, advisory)` (never counts, never source bytes — AR4/NFR-S1). The harness parametrizes over `CARTRIDGE_REGISTRY` so a NEW cartridge = a row + a `*.py.txt` drop-in with NO harness refactor (the README additive promise; the N=5 design). `kind ∈ {planted_defect, clean_control, holdout, trap, no_crash}`.
- DN-HOLDOUT — in a single-repo V1, "hidden holdout" = a cartridge ADDED in this story whose planted defect was NOT used to shape any 6.1–6.4 detector heuristic, gated exactly like a labeled cartridge so an overfit detector that only memorized `vacuous_basic` fails. `holdout_vacuous` is that cartridge (`kind=holdout`). A true author-blind holdout corpus is a 6.6/validation-protocol concern.
- DN-GATE-STATUS — the mechanized `PRECISION_GATE_STATUS` marker (above); 6.5 computes no number, 6.6 flips it.
- DN-NO-PROD-CHANGE — 6.5 is TEST/HARNESS + cartridge-templates + registry-helper only. NO detector added/edited, NO Prosecutor edit, NO frozen-contract diff (verified empty `git diff` over all frozen surfaces), NO `.apaa/` write path, NO `cli.py` flag, NO HTTP route, NO new CI job, NO live LLM. The harness READS through the existing `ApaaStoreReader` and asserts on `Recording` fields; it adds no `json.dumps`/hasher/parse, so the single-serializer + no-web-imports + file-size gates stay green.

Populated-vs-N=5 honesty statement: the corpus front-loads the 3 phased planted-defect cartridges (vacuous/secret/orphan) + the holdout (4 labeled true-positive cartridges) + the clean control + the citation-gaming trap + the no-crash row. The registry + harness are SHAPED for the locked N=5 floor; physically reaching 5 distinct planted-defect cartridges with the computed ≥80% precision number continues in Story 6.6. The gate-status marker is honest about this (PROVISIONAL).

Secret-containment (Task 4): the harness co-locates a fixed-canary containment check on `hardcoded_secret` + `evidence_sentinel` (TC-APAA-CARTRIDGE-001-09/-10, green). The 4.4 randomized-canary suite (`tests/security/test_apaa_secret_containment.py`) remains the CI-blocking property gate and already sweeps `secret_canary`. No 4.4 extension was needed: the only NEW cartridge introduced by 6.5 (`holdout_vacuous`) contains NO secret, and `evidence_sentinel` is a pre-existing cartridge; no new write path was introduced. No fork.

Defer decision (AI-E5-4): NO new defer filed. 6.5 surfaced no detector gap and no unplanned overfitting risk — the only open item ("grow the corpus to N=5 + compute the empirical ≥80% precision number + the validation protocol") is the explicitly-planned scope of Story 6.6 (already captured in the epic plan and mechanized in the `PRECISION_GATE_STATUS` marker), not an unplanned gap requiring a deferred-work row.

### File List

- `tests/apaa/cartridges/_registry.py` — the parametrized cartridge registry (frozen `CartridgeSpec`/`GoldenFinding`, `CARTRIDGE_REGISTRY`, `VALIDATION_SET_FLOOR_N`, `populated_planted_defect_count()`, `PRECISION_GATE_STATUS`). [new]
- `tests/apaa/test_cartridge_selfaudit.py` — the parametrized self-audit harness (15 test functions, 33 parametrized cases; area `APAA-CARTRIDGE`, `TC-APAA-CARTRIDGE-001-01..15`). [new]
- `tests/apaa/cartridges/holdout_vacuous/src/inventory.py.txt` — the holdout SUT (clean `audited_deep` module). [new]
- `tests/apaa/cartridges/holdout_vacuous/tests/test_inventory.py.txt` — the holdout planted vacuous test (`kind=holdout`). [new]
- `_bmad-output/design-artifacts/APAA/stories/6-5-defect-cartridge-self-audit-harness-holdout-clean-controls.md` — Tasks checked off, Dev Agent Record completed, Status → `review`, Change Log appended.
- `_bmad-output/design-artifacts/APAA/sprint-status.yaml` — `6-5-...: review`, `last_updated` date-only bump.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-06-30 | 0.1 | Story drafted (create-story) — FR20 defect-cartridge self-audit harness + holdout + clean controls; N=5 design, phased 3→5, precision-over-findings, provisional-gate marker (OI1); scope-fenced vs 6.6 (precision number/replay) + 6.7 (HITL). | Scrum Master (Bob) |
| 2026-06-30 | 1.0 | dev-story COMPLETE → review. Delivered the parametrized cartridge registry (`_registry.py`, frozen `CartridgeSpec`/`GoldenFinding`, N=5-shaped) + the self-audit harness (`test_cartridge_selfaudit.py`, 33 cases, area APAA-CARTRIDGE TC-...-001-01..15) + the NEW `holdout_vacuous` cartridge (overfitting defense) + the citation-gaming trap (`evidence_sentinel`) + the no-crash row (`tool_breadth`, AI-E4-2) + the mechanized `PRECISION_GATE_STATUS` provisional marker (OI1 keystone — NO ≥80% number computed; 6.6 owns it). REUSE-only (stage_cartridge + run_audit_detailed + ApaaStoreReader, no fork); NO detector/Prosecutor edit, NO frozen-contract diff (verified empty git diff), NO cli/HTTP/CI-job/LLM. 1165 passed/1 skipped/4 subtests; structural gates + 4.4 secret-containment suite green; mypy clean; files ≤1200 (475 + 240 lines). No new defer (corpus→N=5 + precision number is planned 6.6 scope). | Dev Agent (Amelia) |

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.8 (1M) — `/bmad-code-review` adversarial gate (iteration 1).
**Date:** 2026-06-30. **Verdict: PASS → `done`.**

### Outcome

FR20 is delivered as the measurement SUBSTRATE, scrupulously honest about the OI1 lock. Every keystone
claim was independently verified adversarially (not trusted from the Dev record). REUSE-only, no
frozen-contract edit, no scope creep, full suite green.

### Keystone verifications (each re-run / re-read, not trusted)

1. **Golden keys are SETS, never byte/count comparisons (NFR-S1 / AR4).** CONFIRMED. `_registry.py`
   models each golden key as a `tuple[GoldenFinding, ...]` where `GoldenFinding = (rule_id: str,
   verdict_eligible: bool, advisory: bool)`. The harness matches via set membership (`_emitted_keys`
   → `{(rule_id, depth_supported is not None, advisory)}`). No source-byte comparison and no count
   equality anywhere; the secret golden key carries no value (value-free contract asserted in
   TC-...-001-10 via `"value" not in model_fields`).

2. **Holdout is genuinely un-tuned AND caught with NO detector change (overfitting defense, AC4).**
   CONFIRMED. `holdout_vacuous` plants a differently-named/-structured vacuous test
   (`total_stock` / `Mock.tally`) vs the tuned `vacuous_basic` shape — the generalization is real, not
   a renamed clone. The frozen detector surfaces (`detectors/*`, `pipeline.py`, `verdict_gate.py`,
   `prosecutor.py`) all carry mtimes 2026-06-21..06-29, strictly BEFORE the 6-5 artifacts (2026-06-30)
   — so the holdout is caught by the SAME `vacuous_test_ast` rule with zero detector edit. Live test
   TC-...-001-05 passes (blocks, exit 2).

3. **PRECISION_GATE_STATUS computes NO ≥80% number (OI1 honesty keystone, AC7 — NOT softened).**
   CONFIRMED. `precision_gate_status()` is UNCONDITIONALLY provisional, mechanically derived from the
   labeled count, asserts `%` absent and `PRECISION_VALUE`/`MEASURED_PRECISION` unbound
   (TC-...-001-13/-14). The marker explicitly states "NO precision number computed here … computed +
   cleared in Story 6.6 at N>=5". The honesty constraint is mechanized as a committed constant, not a
   rotting comment. The count is reported-for-transparency, never used to silently flip the gate.

4. **NO working-tree diff to the frozen Epic-1..6 production surfaces (AC9 keystone).** CONFIRMED.
   The only tracked diff in `minions_core/apaa/` is `__init__.py`'s story-1.1 `__version__ = "0.1.0"`
   constant — NOT a 6-5 change. All frozen surfaces (`recording.py`, `verdict_gate.py`, `detectors/*`,
   `prosecutor.py`, `pipeline.py`, `store/reader.py`) predate the 6-5 work by mtime; the entire APAA
   prod tree is untracked (sub-tool not yet committed), so mtime — not `git diff` — is the load-bearing
   evidence, and it is clean.

5. **Determinism — 2-run byte-identical verdict envelope `content_hash` (NFR-P1, AC6).** CONFIRMED.
   TC-...-001-07 stages each cartridge twice and asserts identical verdict locator, identical read-back
   bytes, and identical `content_hash` over the WHOLE corpus. Passes.

6. **Secret-containment is NOT vacuous (NFR-S1, AC6).** CONFIRMED. The `_PLANTED_SECRET_BYTES` tokens
   were grep-verified to actually exist in `hardcoded_secret`/`evidence_sentinel`/`secret_canary`
   cartridge files — so the `secret not in blob` assertion (over `.apaa/` bytes + finding/verdict reprs)
   is a real redaction test, and it passes. The 4.4 randomized-canary suite (22 passed) remains the
   CI-blocking property gate; no fork.

### Independent test execution (re-run by the reviewer, not trusted from the record)

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/test_cartridge_selfaudit.py` → **33 passed**.
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
  **1165 passed, 1 skipped, 4 subtests passed** (matches the Dev record exactly).
- File sizes: `pipeline.py` 1090, `_registry.py` 240, `test_cartridge_selfaudit.py` 475 — all ≤1200
  (NFR-M1).

### Engineering-principle adherence

- **No-fork / DRY (§3.3 / AR7):** harness composes `stage_cartridge` + `run_audit_detailed` +
  `ApaaStoreReader` by import; no parallel pipeline runner, no second serializer/hasher/parse.
- **Mechanized fixture-shape coverage (AI-E5-2):** the parametrized registry iterates the declared set
  mechanically — no hand-copied per-cartridge bodies (TC-...-001-12 guards every kind is covered).
- **Complete-the-declared-set (AI-E5-1) + no-crash leg (AR10):** all six members enumerated and covered;
  `_audit` converts any staging/audit raise into a NAMED assertion citing the cartridge id.
- **Headless / 12-Factor:** no UI, no HTTP route, no `cli.py` flag, no env/clock in the pure registry.

### Findings

None blocking; no Low-severity cleanups warranted. The defer decision (no new defer — corpus→N=5 +
the precision number is explicitly planned 6.6 scope, already mechanized in the marker) is correct and
honest; filing a defer for in-plan next-story scope would be noise.

### Status decision

All ACs (AC1–AC9) met and empirically verified; tests green; OI1 honesty constraint mechanized and
not softened; no frozen-contract diff; ≤1200 lines; REUSE-only. **PASS → `done`.**
