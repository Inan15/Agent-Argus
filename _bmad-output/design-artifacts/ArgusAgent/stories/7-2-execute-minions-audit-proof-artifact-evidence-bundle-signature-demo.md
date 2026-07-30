# Story 7.2: Execute the Minions audit → proof artifact, evidence bundle & repeatable signature demo — [Tier B]

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker at `_bmad-output/implementation-artifacts/sprint-status.yaml`). All
> CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only, §3.8 12-Factor + secret masking, §3.4
> evidence immutability). Run all gate/test commands under `PYTHONIOENCODING=utf-8` (Windows / cp1252).
>
> **This is the FINAL story of Epic 7 AND the CAPSTONE of the whole APAA project** (Minions Dogfood Proof
> Run — "the last thing cut"). `epic-7` is ALREADY `in-progress` (flipped by the done Story 7.1); this story
> does NOT change the epic status. It builds directly on the **done Story 7.1** (the full-repo partition map
> + the empirically-sized `$X` = 843-credit budget ceiling + the N=5 distinct-class corpus growth — all in
> `minions-dogfood-partition-plan.md` / `minions-dogfood-budget-plan.md` / `minions_core/apaa/dogfood/`), and
> on the fully-done Epics 1–6 spine.
>
> **THIS STORY EXECUTES THE DOGFOOD — it RUNS the audit 7.1 sized; it does NOT re-plan / re-size / re-grow
> the corpus (that was 7.1).** Per the epic (Story 7.2) it does FOUR coherent "run the proof" things:
> 1. **Execute APAA end-to-end over the real Minions repo** per the 7.1 partition map + the `$X` = 843 budget
>    ceiling, REUSING the frozen `pipeline.run_audit_detailed` (no fork), producing a coverage ledger,
>    findings, and a negative-assurance verdict — within the ceiling (and demonstrating the ceiling halts +
>    downgrades if breached), and recording it as a committed **proof artifact**.
> 2. **Export a SIGNED evidence bundle** — REUSING the done Story 4.3 evidence-bundle-export seam
>    (`evidence/bundle.py::build_evidence_bundle` + `persist_evidence_bundle` + the no-source-retention
>    guarantee) + the 1.1 canonical serializer + the 1.1 hash-chained/content-addressed envelope (no fork).
> 3. **Reproduce the `GitHub green · Sonar green · APAA 🔴 tests appear vacuous` signature demo** as a real,
>    repeatable artifact over the real (or planted-in-Minions) vacuous test — the moat demo as a success
>    criterion; AND prove the dogfood run is **100% reproducible** on the same Minions commit (two runs →
>    identical verdict — NFR-D1); AND carry the honest **`grade: demo-heuristic-only`** flag (the run cuts LLM
>    AST-grounding — Tier-A only — so it is NOT presented as externalization evidence; the red-team guard).
> 4. **Lay out the REAL dogfood findings ADJUDICATION-READY** so the later human TP/FP adjudication (the
>    DF-6-6-A HUMAN half) can clear the ≥80%-precision gate on REAL data — each finding inspectable with its
>    `rule_id` / locators / verdict-eligibility. **The human adjudication itself is OUT of scope for this
>    autonomous story** (it is the human step); this story only ENABLES it.
>
> **The OI1 honesty keystone is NON-NEGOTIABLE and is the spine of this story** (operator epic-boundary
> decision, 2026-07-02): the synthetic corpus bootstrapped a PROVISIONAL ≥80%-precision gate (7.1: 5 distinct
> classes). The gate is cleared ONLY by the human TP/FP adjudication over the REAL dogfood findings this story
> produces. Therefore this story:
> - Presents the ≥80%-precision gate as **honestly PROVISIONAL** in the evidence bundle / proof artifact
>   (`protocol_cleared` NOT flipped; the `precision_gate_status()` marker NOT flipped; NO ≥80% number
>   presented as authoritative / cleared). **Do NOT fabricate a cleared gate — over-claiming is the exact
>   failure mode APAA exists to prevent.**
> - Structures the bundle so the REAL dogfood findings are laid out **ready for human TP/FP adjudication**
>   (each finding: `rule_id` + locators + advisory-vs-blocking verdict-eligibility) — the Eng-Lead + QA-Lead
>   adjudication can later clear the gate on REAL data.
> - Files the still-open human-adjudication step as a defer with the six CC-3 fields (it does NOT run the
>   adjudication or flip the gate).

## Story

As **the XAgents platform owner** answering the strategic question "does Minions have a working AI audit
agent?" with a REAL artifact — who has watched 7.1 size the full-repo partition map (4 bounded units over 135
modules / 36.7k LOC) + the empirical `$X` = 843-credit ceiling + grow the synthetic cartridge corpus to 5
distinct defect-rule classes, and who knows the whole capstone stands or falls on APAA actually RUNNING over
the real Minions repo and producing a defensible, source-free, signed evidence bundle — while never
over-claiming (the ≥80%-precision gate stays PROVISIONAL until a human adjudicates REAL findings),
I want **APAA executed end-to-end over the real Minions repo per the 7.1 plan + ceiling, producing a committed
proof artifact + a SIGNED (hash-chained, content-addressed) evidence bundle + a reproduced `GitHub green ·
Sonar green · APAA 🔴` signature demo + a 100%-reproducibility check + an honest `grade: demo-heuristic-only`
flag** — REUSING the frozen `pipeline.run_audit_detailed` + the 4.3 `build_evidence_bundle`/`persist_evidence_bundle`
export + the 1.1 canonical serializer + envelope (no forks) — with the REAL dogfood findings laid out
ADJUDICATION-READY (each finding inspectable with its `rule_id` / locators / verdict-eligibility) so the later
human TP/FP adjudication can clear the gate on REAL data,
so that **the strategic question is answered with a real artifact, the moat demo is a repeatable success
criterion, and the path to the ≥80%-precision gate is OPEN** — while the ≥80%-precision gate stays PROVISIONAL
(the OI1 honesty keystone) because only the human TP/FP adjudication over these REAL dogfood findings (the
DF-6-6-A human half, this story + a human step) may clear it, and presenting a Tier-A heuristic-only demo run
as externalization evidence — or fabricating a cleared gate from the synthetic corpus — is the exact failure
mode this story's red-team guards forbid.

## Story Context

This is **Story 2 of Epic 7** (Minions Dogfood Proof Run, Tier-B — the capstone) and the **FINAL story of the
whole APAA project**. It is the EXECUTION half of the dogfood: 7.1 produced the PLAN (partition map + budget
sizing + corpus growth); **7.2 RUNS it** — the audit, the coverage ledger, the findings, the
negative-assurance verdict, the SIGNED evidence bundle, the reproduced signature demo, the reproducibility
check, and the adjudication-ready findings layout. 7.2 does NOT re-plan, re-size, re-partition, or re-grow the
corpus (that was 7.1), and does NOT run the human adjudication or flip the gate (that is the human step).

**What already exists (REUSE verbatim, do NOT rebuild — the no-fork keystone, §3.3 / AR7).** This story is an
EXECUTION + assembly story sitting on the fully-built Epic-1..6 spine + the done 7.1 plan. Every mechanism it
needs already ships:

- **Story 7.1 (done) — the committed dogfood PLAN + sizing + the `dogfood/` sub-package.**
  `minions_core/apaa/dogfood/partition_plan.py` (`build_full_repo_plan` / `size_budget` /
  `render_partition_plan_markdown` / `render_budget_plan_markdown`) + the committed
  `minions-dogfood-partition-plan.md` (4 units, 135 files, 36712 LOC, 332 cut edges, `commit
  7f8e1478...`) + `minions-dogfood-budget-plan.md` (`$X` = **843 credits**, V1 total 675, NFR-C1
  baseline `675/36712`, the 3.2 halt demonstration). **7.2 CONSUMES this plan — it re-derives the plan (for
  the pinned commit) and RUNS the audit with `budget = 843`; it does NOT re-author a partitioner, a second
  plan, or a second budget-sizing.** The corpus already spans **5 distinct classes** (7.1's DF-6-6-A-P1
  autonomous half); 7.2 does NOT grow it further.
- **Story 1.7 / 3.x / 6.x (done) — `pipeline.py::run_audit_detailed(request, *, store_writer=None) ->
  AuditResult` (REUSE verbatim, do NOT edit).** The frozen impure pipeline shell: intake @ a pinned commit →
  AST index → per-file grade + detectors (+ the 6.2 FR7 AST-grounding, the 6.3 orphan pass, the 6.4
  Prosecutor cut-edge pass) → the 3.2 halt projection under the ceiling → `_assemble_and_persist` →
  `AuditResult(verdict, locators, floor_report, negative_assurance, coverage_report)`. It calls **NO LLM**
  (zero-token, NFR-D2 — the AST-grounding depth path via `audit/deep_audit.py::LLMDispatchPort` is a separate
  INJECTED seam NOT wired into `run_audit_detailed`), so the dogfood run is **Tier-A heuristic-only** (this is
  exactly why AC-DEMO-GRADE's `grade: demo-heuristic-only` flag is honest — see DN-GRADE). 7.2 CONSUMES this
  to run the audit over each 7.1 unit's `work_manifest`; it does NOT touch the verdict math / persist order /
  producer tokens.
- **Story 4.3 (done) — `evidence/bundle.py` (REUSE verbatim, do NOT edit / do NOT fork the Minions governance
  bundle).** `build_evidence_bundle(result: AuditResult, integrity_report: IntegrityReport, *, commit: str,
  apaa_version: str) -> EvidenceBundle` (PURE) + `bundle_to_canonical_payload` / `bundle_to_canonical_bytes`
  (single 1.1 serializer) + `persist_evidence_bundle(writer, bundle) -> str` (the impure additive persist to
  `state/` via the 1.3 writer, content-addressed, containment-checked, producer `apaa.evidence.bundle`) + the
  frozen `EvidenceBundle` model + `EVIDENCE_BUNDLE_SCHEMA_VERSION` / `EVIDENCE_BUNDLE_PRODUCER`. **The
  no-source-retention MOAT is already structural (no field holds source/secret bytes — only locations +
  redacted indicators).** 7.2 CONSUMES this to export + persist the SIGNED bundle for the dogfood run; it does
  NOT re-author a bundle model, a second serializer, or a redaction pass.
- **Story 4.2 (done) — `store/integrity.py::lint_referential_integrity(reader) -> IntegrityReport` (REUSE
  verbatim).** The referential-integrity lint over the `.apaa/` tree the bundle INCLUDES. 7.2 runs it over the
  dogfood run's persisted tree and feeds the `IntegrityReport` to `build_evidence_bundle` (the impure shell,
  NOT inside the pure builder — the 4.3 DN-WIRING precedent).
- **Story 1.1 (done) — `store/{canonical,envelope}.py` (REUSE — THE serializer + THE signing/chaining
  envelope).** `canonical.dumps_bytes` (rejects `float`; `Fraction → "num/den"`; `sort_keys`; `\n`-terminated
  UTF-8) + the content-hashed, schema-versioned, **prev-hash-chained** envelope (`EnvelopeWriter.build`). The
  bundle is "signed" in the APAA sense = the content hash + the prev-hash chain over the canonical payload
  (NFR-A1 / NFR-D3 — the point-in-time stamp is the envelope `created_at`, EXCLUDED from the hash). 7.2 does
  NOT introduce a second serializer / a new signing scheme.
- **Story 1.3 (done) — `store/{writer,paths,reader}.py` (REUSE).** `ApaaStoreWriter.write_payload`
  (content-addressed, `ApaaStorePaths` `is_relative_to` containment); `ApaaStoreReader.read_envelope`
  (tamper-guarded). 7.2 writes the dogfood `.apaa/` tree + the persisted bundle through the writer, reads it
  back through the reader.
- **Story 6.6 (done) — `precision/replay_harness.py::compute_precision` + `precision_gate_status_for(...)` +
  the 6.5 `precision_gate_status()` / `PRECISION_GATE_STATUS` marker (REUSE unchanged, do NOT flip).** The
  provisional-gate marker. **7.2 REPORTS the gate PROVISIONAL (`protocol_cleared=False`, marker NOT flipped) —
  it does NOT run the human adjudication that would clear it (that is the human step). The 7.2 dogfood findings
  are the REAL-repo input the human adjudication needs; 7.2 lays them out adjudication-ready.**
- **Story 6.5 (done) — the cartridge registry + the 7.1-grown 5-distinct-class corpus.** 7.2 does NOT grow it
  further; it MAY reuse a `vacuous_test_ast` cartridge (or a planted-in-Minions vacuous test) to reproduce the
  signature demo (AC-SIGNATURE). The signature demo cartridge staging REUSES `tests/apaa/cartridges/_cartridge.py`.
- **Story 6.7 (done) — the HITL escalation + decision-record LIBRARY seam (`governance/escalation.py` +
  `governance/decision_record.py`).** DF-6-7-A targets `epic-7-minions-dogfood-proof-run` (this story's epic)
  as the first live consumer. **DECISION (DN-ESCALATION): wiring the HITL escalation into the live pipeline/CLI
  is OUT of scope for 7.2** (the human adjudication is a documented human step, and the escalation-rule config
  source + a `--decision` flag are a distinct wiring task) — 7.2 does the dogfood EXECUTION + the
  adjudication-ready findings layout; DF-6-7-A stays open. See the Scope fence + AC-ADJUDICATION-READY.

**The net-new deliverable of THIS story.** The dogfood is EXECUTED + assembled + made honestly inspectable:

1. a committed, reproducible **dogfood-execution generator + proof artifact** (a `.md` deliverable under
   `_bmad-output/design-artifacts/ArgusAgent/`, e.g. `minions-dogfood-proof.md`) that runs APAA end-to-end over the
   real Minions repo @ the pinned commit under `budget = 843` (the 7.1 `$X`), REUSING `run_audit_detailed`
   (no fork), and records the proof: the verdict per unit (or over the whole repo), the coverage-ledger deep-%
   (exact `Fraction`), the finding counts by `rule_id` (advisory vs blocking / verdict-eligible), the
   within-ceiling confirmation (+ the 3.2 halt-if-breached demonstration), and the honest
   `grade: demo-heuristic-only` provenance. Byte-reproducible for the same repo@commit (a committed
   generator/test re-derives it deterministically — NOT a hand-typed report that rots).
2. a **SIGNED evidence bundle** for the dogfood run — REUSING `build_evidence_bundle` + `persist_evidence_bundle`
   (the 4.3 seam) + the 1.1 envelope: the negative-assurance verdict + scope statement + disclaimer + the
   coverage ledger + the verdict-ordered REDACTED findings + the 4.2 integrity report + metadata, serialized
   through the single 1.1 serializer, content-addressed + prev-hash-chained (the "signature"). The bundle
   retains NO Minions source byte and NO secret (the 4.3 structural moat + NFR-S1) — proven over the REAL
   Minions tree, not only a cartridge.
3. the **reproduced signature demo** — `GitHub green · Sonar green · APAA 🔴 tests appear vacuous` as a real,
   repeatable artifact over a vacuous test (a real Minions one if found, else a planted-in-Minions cartridge),
   asserted as a committed test; AND the **100%-reproducibility check** (two dogfood runs on the same commit →
   byte-identical verdict / bundle canonical payload — NFR-D1); AND the **`grade: demo-heuristic-only` flag**
   (the run cuts LLM AST-grounding → Tier-A only → NOT presented as externalization evidence — the red-team
   guard, an additive honesty field on the proof artifact / bundle metadata; see DN-GRADE).
4. the **adjudication-ready findings layout** — the REAL dogfood findings laid out so a human Eng-Lead +
   QA-Lead can later record a TP/FP judgment per the `precision-validation-protocol.md`: each finding with its
   `rule_id`, locators, and advisory-vs-blocking verdict-eligibility, mapped onto the 6.5/6.6 golden-key shape
   (`finding_match_key`) so the human judgment is a per-finding TP/FP tag over a real-repo finding set. The
   gate STAYS PROVISIONAL — 7.2 does NOT run the adjudication or flip `protocol_cleared`.
5. a committed **DF-6-6-A progress note** (append-only in `deferred-work.md`, six CC-3 fields) recording that
   the dogfood was EXECUTED + the REAL findings are adjudication-ready, and that the HUMAN adjudication step
   (the ONLY thing that may flip the ≥80% gate) is still OPEN — plus a **new defer** for the human-adjudication
   step (and, if it surfaces, the DF-6-7-A HITL wiring) with the six CC-3 fields.

**Scope vs the human adjudication (the OI1 crux — the operator epic-boundary decision, read carefully).**
The synthetic corpus (7.1: 5 distinct classes) bootstrapped a PROVISIONAL ≥80%-precision gate. **The gate is
cleared ONLY by the human TP/FP adjudication over the REAL dogfood findings this story produces** — that
adjudication is a HUMAN step (Eng-Lead + QA-Lead per `precision-validation-protocol.md` §4/§5), and it is
**OUT of scope for this autonomous story**. 7.2's job is to (a) produce the REAL dogfood findings, and (b) lay
them out ADJUDICATION-READY so the human step can run. 7.2 does NOT flip `protocol_cleared`, does NOT fabricate
a cleared gate, and does NOT present a ≥80% number as authoritative. The still-open human step is filed as a
defer (six CC-3 fields). **This is the single most important honesty invariant of the story — a reviewer's #1
adversarial check will be a quietly-flipped gate or an over-claimed externalization; both must be clean.**

**Scope vs the rest of Epic 7 / project (explicit deferrals — do NOT pull forward).**
- **The HUMAN TP/FP adjudication that CLEARS the ≥80%-precision gate** — a human step (DF-6-6-A human half).
  7.2 produces the REAL findings + lays them adjudication-ready ONLY; it does NOT run the adjudication or flip
  `protocol_cleared` / the marker. File the open step as a defer.
- **Live HITL-escalation wiring into the pipeline/CLI (DF-6-7-A)** — OUT of scope (DN-ESCALATION). The
  escalation is a pure LIBRARY seam (6.7); wiring it (the config source + a `--decision` flag + a human-wait
  transport) is a distinct task. DF-6-7-A stays open (its `target_story` is this epic; note it, do NOT close).
- **A V2 cross-partition SEAM auditor / an LLM-driven deep-audit run** — OUT of scope (V2). The dogfood is
  Tier-A heuristic-only (the honest `grade: demo-heuristic-only`); V1 has NO cross-partition seam analysis (the
  6.4 `cross_partition` pass is the V1 mitigation — 7.1's `minions-dogfood-partition-plan.md` states this).
- **A change to the 2.4 partitioner / the 3.1 budget core / the 4.3 bundle SHAPE / the 6.5 registry SHAPE /
  any detector / the Prosecutor / any frozen Epic-1..6 contract / the 7.1 `dogfood/partition_plan.py`
  contract** — out of scope. 7.2 CONSUMES `run_audit_detailed` + `build_evidence_bundle`/`persist_evidence_bundle`
  + `lint_referential_integrity` + `compute_precision` + the 7.1 plan as-is. If executing surfaces a gap in a
  frozen surface, that is a DEFER (six CC-3 fields), not a 7.2 edit. If a MINIMAL additive `grade`/provenance
  field is genuinely needed for AC-DEMO-GRADE, prefer recording it in the PROOF ARTIFACT / a dogfood-run
  wrapper (additive) over mutating the frozen 4.1 `NegativeAssuranceVerdict` / 4.3 `EvidenceBundle` model —
  lock the decision in Dev Notes (DN-GRADE); ONLY if an additive frozen-model field is unavoidable, add it as
  a default-preserving optional field (the 4.1 `floor_report`/`coverage_report` additive-field precedent) and
  narrate the byte-compat impact.
- **A new `.github/workflows` CI job / a new HTTP route / a FastAPI surface / a UI (§3.7) / a new `cli.py`
  flag** — out of scope. Any new test runs under the EXISTING APAA pytest CI invocation (the durable backstop).
  A future `apaa audit --export-bundle` CLI surface is a follow-up (the 4.3 DN-WIRING / DF-3-4-A precedent) —
  NOT this story.

**Carry-forward action items (CLAUDE.md §9.1 / L1-E11 — the Epic-6 retro's AI-E6-* items + the 7.1 handoff).**
- **AI-E6-2 (process/precision, HARD Epic-7 pre-condition) — DF-6-6-A.** 7.1 discharged the AUTONOMOUS half (5
  distinct classes). 7.2 EXECUTES the dogfood + produces the REAL findings + lays them ADJUDICATION-READY (the
  input the human half needs). The HUMAN adjudication (the ONLY gate-flipping step) stays OPEN → a defer.
- **AI-E6-1 (test-infra 🟠, the §9.2 occ-2 promotion) — payload/event-identity checklist leg.** The
  adjudication-ready finding-set maps each real finding onto the 6.6 `finding_match_key` shape so a human
  TP/FP tag is unambiguous per finding (no collision-collapsed identity — RED-first where two distinct findings
  would collapse to one key).
- **AI-E5-1 (test-infra 🟠, standing) — complete-the-declared-set.** Enumerate the FULL declared set of 7.2
  deliverables — (1) the dogfood execution + proof artifact (reproducible, within-ceiling); (2) the SIGNED
  evidence bundle (no-source over the REAL repo); (3) the reproduced signature demo; (4) the
  100%-reproducibility check; (5) the `grade: demo-heuristic-only` honesty flag; (6) the adjudication-ready
  findings layout; (7) the OI1 provisional-gate honesty report + the DF-6-6-A progress note + the
  human-adjudication defer — and demonstrate EACH covered.
- **AI-E4-2 (test-infra) — no-crash input shapes.** The dogfood generator over the REAL Minions repo (parse
  failures, non-ASCII paths, a module over the hard LOC limit, an empty/oversized unit) degrades to a typed,
  NAMED outcome — never a bare traceback. A bundle-export / persist / lint failure → a typed
  `EvidenceBundleError` / `PipelineError` / `StoreIntegrityError`, never an uncaught raise.
- **AI-E1-1 (test-infra 🟢, standing) — non-ASCII / locale discipline.** The dogfood run + the bundle + the
  proof artifact serialize + round-trip under `PYTHONIOENCODING=utf-8`; a non-ASCII path in a locator
  round-trips intact.
- **AI-E5-4 / AI-E6-6 (governance 🟢) — central defer register.** File the DF-6-6-A progress note + the
  human-adjudication defer + any newly-surfaced gap append-only in `deferred-work.md` with the six CC-3 fields.
- **AI-E5-7 (process 🟢) — structural gates green + partial-reuse docstring precision.** The dogfood generator
  + any new test keep the no-web-imports gate, the single-serializer AST gate, and the file-size gate green
  (REUSE the canonical serializer for any `.apaa`/bundle/proof bytes; add NO new `json.dumps`/hasher; import NO
  `fastapi/uvicorn/starlette`; NO live LLM). Narrate the PARTIAL reuse precisely (REUSES `run_audit_detailed` +
  `build_evidence_bundle`/`persist_evidence_bundle` + `lint_referential_integrity` + `compute_precision` + the
  7.1 plan; ADDS the dogfood-execution generator + the proof artifact + the signature-demo/reproducibility/
  adjudication-ready tests).
- **NFR-S1 secret-containment (standing CI-blocking moat).** The dogfood bundle + proof artifact route through
  the EXISTING 4.4 randomized-canary suite (`tests/security/test_apaa_secret_containment.py`) discipline — no
  Minions source byte / secret value in the bundle, the proof artifact, the precision surface, or any persisted
  `.apaa/` artifact (the 4.3 structural moat is the primary guarantee; extend the 4.4 sweep to the dogfood
  bundle if a new secret-bearing path is introduced — do NOT fork).

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 7.2) + the OI1 honesty keystone (the ≥80% gate stays
> PROVISIONAL; the human adjudication over REAL findings is the only clearing step, OUT of scope here) + the
> operator epic-boundary decision (2026-07-02: adjudication-ready findings feed a later human TP/FP
> adjudication) + the architecture (FR29 evidence bundle; FR17 negative assurance; the FR7 AST-grounding
> demo-grade guard; NFR-D1 reproducibility). Drivers: **APAA-FR-29** (export an evidence bundle — the SIGNED
> dogfood bundle), **APAA-FR-17 / NFR-A3** (the negative-assurance verdict + scope statement + disclaimer the
> bundle exports), **APAA-FR-30 / FR18** (the headless invocation contract + deterministic verdict the dogfood
> reuses), **APAA-FR-21 / OI3** (the empirically-sized `$X` = 843 ceiling from 7.1; the run completes within
> it and halts + downgrades if breached), **APAA-FR-20** (the defect-cartridge precision substrate — the
> adjudication-ready real findings feed the human gate-clearing step), **APAA-NFR-D1** (100% reproducibility on
> a real repo), **APAA-NFR-S1 / NFR-S3** (no Minions source / secret byte in the bundle / proof / precision
> surface — the no-source-retention moat over the REAL repo), **APAA-NFR-A1 / D3** (the content-hashed,
> prev-hash-chained, schema-versioned envelope — the "signature"; the point-in-time stamp is the envelope
> `created_at`, excluded from the hash), **APAA-NFR-P1** (byte-identical / order-independent bundle for the
> same audit result), **APAA-AR4** (int credits / Fraction ratios — NEVER float in any persisted figure),
> **APAA-AR7** (REUSE by import — no fork of the pipeline / bundle / serializer / lint / precision harness),
> **APAA-AR8** (pure/impure separation preserved), **APAA-AR10** (typed failure — no uncaught traceback),
> **APAA-NFR-M1/M2** (≤1200-line files; frozen Epic-1..6 + 7.1 contracts + the 4.3/6.5 SHAPES unchanged).
>
> **SCOPE FENCE — Tier-B, single-purpose "EXECUTE the dogfood": run the audit + produce the SIGNED bundle +
> reproduce the signature demo + prove reproducibility + flag demo-grade + lay findings adjudication-ready +
> keep the gate PROVISIONAL.** This story delivers ONLY: (1) the committed, reproducible dogfood EXECUTION +
> proof artifact (REUSING `run_audit_detailed` under `budget = 843`, within-ceiling + halt-if-breached); (2)
> the SIGNED evidence bundle for the dogfood run (REUSING `build_evidence_bundle`/`persist_evidence_bundle` +
> the 1.1 envelope; no Minions source/secret byte); (3) the reproduced `GitHub green · Sonar green · APAA 🔴`
> signature demo; (4) the 100%-reproducibility check (NFR-D1); (5) the honest `grade: demo-heuristic-only`
> red-team flag; (6) the adjudication-ready real-findings layout (per-finding `rule_id` + locators +
> verdict-eligibility, mapped to the 6.6 match-key shape); (7) the OI1 provisional-gate honesty report + the
> DF-6-6-A progress note + the human-adjudication defer; (8) any new defer with the six CC-3 fields. It does
> NOT build, and MUST NOT pull forward: the **HUMAN TP/FP adjudication that CLEARS the ≥80% gate** (a human
> step — 7.2 keeps the gate PROVISIONAL, `protocol_cleared=False`, marker NOT flipped); the **live HITL-escalation
> wiring** (DF-6-7-A stays open); a **V2 cross-partition SEAM auditor / an LLM-driven deep-audit run**; a
> **change to the 2.4 partitioner / 3.1 budget core / 4.3 bundle SHAPE / 6.5 registry SHAPE / any detector /
> the Prosecutor / any frozen Epic-1..6 or 7.1 contract**; a **new `.github/workflows` CI job / HTTP route /
> FastAPI surface / UI (§3.7) / new `cli.py` flag**.

**AC-EXECUTE — APAA is executed end-to-end over the real Minions repo per the 7.1 plan + `$X` = 843 ceiling, REUSING `run_audit_detailed`, producing a coverage ledger + findings + a negative-assurance verdict WITHIN the ceiling (FR30 / FR21 / OI3 / AR7)**
**Given** the real Minions repo @ the pinned commit (the 7.1 plan's `commit 7f8e1478...` or the current HEAD,
re-derived), the 7.1 partition map (4 bounded units) + the `$X` = 843-credit ceiling
(`minions-dogfood-budget-plan.md`), and the frozen `pipeline.run_audit_detailed`
**When** the dogfood is executed (a committed generator runs the audit over the repo / each 7.1 unit's
`work_manifest` under `AuditRequest(..., budget=843)`, REUSING `run_audit_detailed` — no forked pipeline)
**Then** the run produces an `AuditResult` per unit (or over the whole repo) carrying a **coverage ledger**
(per-file depth states + the exact-`Fraction` deep-%), the **findings** (the verdict-ordered `ordered_findings`),
and the **negative-assurance verdict** (the 4.1 `NegativeAssuranceVerdict` — verdict + scope statement +
disclaimer), and it records these into a committed **proof artifact** (e.g.
`_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md`); the run completes **within the `$X` = 843
ceiling** (the cost accounting under `BudgetConfig(ceiling_credits=843)` does NOT breach — `ceiling_reached is
False`), **and** the proof records the 3.2 halt demonstration (a ceiling below the V1 total demonstrably
breaches → the halt→skip→downgrade→report path fires — REUSING the 3.2 mechanism, not re-implementing it).

**AC-BUNDLE — A SIGNED, source-free evidence bundle is exported + persisted for the dogfood run, REUSING the 4.3 seam + the 1.1 envelope (FR29 / NFR-A1 / NFR-S1 / NFR-S3 / AR7)**
**Given** the dogfood `AuditResult` (with its persisted `.apaa/` tree) and the 4.2
`lint_referential_integrity` report over that tree
**When** the bundle is exported (`build_evidence_bundle(result, integrity_report, commit=..., apaa_version=...)`)
and persisted (`persist_evidence_bundle(writer, bundle)`) — REUSING the 4.3 seam (no forked bundle model /
serializer)
**Then** a frozen `EvidenceBundle` is produced carrying the FR29 sections (the negative-assurance verdict +
scope statement + disclaimer, the coverage ledger + deep-%, the verdict-ordered REDACTED findings, the 4.2
integrity report, and metadata — `schema_version`, `apaa_version`, the audited `commit`, `materiality_bar`),
serialized THROUGH the single 1.1 `canonical.dumps_bytes` and persisted via the 1.1 envelope
(`EnvelopeWriter.build` → content-addressed `<content_hash>.json`, **prev-hash chained** = the "signature",
the point-in-time stamp the envelope `created_at` EXCLUDED from the hash — NFR-A1/D3), containment-checked by
the 1.3 writer (NFR-S5); **and** the persisted bundle retains **NO Minions source byte and NO secret value**
(searched as UTF-8 over the serialized bundle bytes + any persisted artifact — the 4.3 structural moat + NFR-S1,
proven over the REAL Minions tree, not only a cartridge) WHILE the bundle is non-empty + the verdict + scope
statement are present (redaction ≠ suppression); re-reading via the 1.3 reader reconstructs an EQUAL bundle
(round-trip byte-identical).

**AC-SIGNATURE — The `GitHub green · Sonar green · APAA 🔴 tests appear vacuous` signature demo is reproduced as a real, repeatable artifact (the moat demo as a success criterion — epic 7.2 AC2)**
**Given** a vacuous test in the Minions context (a REAL Minions vacuous test if one is found by the audit, ELSE
a planted-in-Minions vacuous-test cartridge staged via `tests/apaa/cartridges/_cartridge.py`)
**When** APAA audits it
**Then** APAA emits a **BLOCKING** `vacuous_test_ast` finding → verdict `NOT_READY_FOR_RELEASE` / exit `2`
(the 🔴), reproducing the `GitHub green · Sonar green · APAA 🔴 tests appear vacuous` line as a real,
repeatable committed artifact (a committed test asserts the 🔴 verdict + the `vacuous_test_ast` finding first
in `ordered_findings` — the 1.7 signature-demo precedent, `TC-APAA-PIPELINE-001-01`), so the moat demo is a
demonstrated success criterion (the honest "green CI, still-vacuous tests" story APAA exists to tell).

**AC-REPRODUCIBLE — The dogfood run is 100% reproducible on the same Minions commit (NFR-D1 / NFR-P1 — epic 7.2 AC3)**
**Given** the dogfood run repeated on the SAME Minions commit (same repo@commit, same `$X` = 843 ceiling)
**When** the two runs' verdicts + the two exported bundles' canonical payloads are compared
**Then** they are **IDENTICAL** — the verdict token + deep-`Fraction` + ordered findings are equal across the
two runs, and the two bundles' `bundle_to_canonical_bytes(...)` are BYTE-IDENTICAL (100% reproducibility on a
REAL repo — NFR-D1; the builder sorts/order-fixes every collection, no clock/float/set-iteration-order in the
hashed payload — NFR-P1), demonstrated by a committed test; **and** this is demonstrated RED against a
deliberate non-determinism injection (e.g. an unsorted finding order into the bundle → the byte-identity
assertion FAILS), then green.

**AC-DEMO-GRADE — The dogfood verdict carries a hard `grade: demo-heuristic-only` flag and is NOT presented as externalization evidence (the red-team guard — epic 7.2 AC4)**
**Given** the dogfood run completes with **AST-grounding cut** (Tier-A only — `run_audit_detailed` calls NO
LLM; the `audit/deep_audit.py::LLMDispatchPort` deep-audit seam is NOT wired into the live pipeline, so the run
is heuristic-only)
**When** the verdict / the proof artifact / the bundle is presented
**Then** it carries a hard, explicit **`grade: demo-heuristic-only`** provenance flag (recorded on the PROOF
ARTIFACT and/or as an additive, default-preserving field per DN-GRADE — do NOT mutate a frozen 4.1/4.3 SHAPE
unless unavoidable) and the proof artifact + Dev Notes state EXPLICITLY that this run is a **demo-grade,
heuristic-only** result that is **NOT presented as externalization / assurance evidence** (the FR7 red-team
guard: a Tier-A demo run must never be dressed up as a validated deep audit); a committed test asserts the flag
is present + the externalization-guard language is present, demonstrated RED if the flag were dropped or if a
"validated / externalization-grade" over-claim phrase were injected (the 4.1/4.3 forbidden-phrase precedent).

**AC-ADJUDICATION-READY — The REAL dogfood findings are laid out ADJUDICATION-READY for the later human TP/FP judgment; the human adjudication is NOT performed here (OI1 / DF-6-6-A / the operator epic-boundary decision)**
**Given** the dogfood `AuditResult`'s findings over the REAL Minions repo and the 6.6 `finding_match_key` /
`precision-validation-protocol.md` §4/§5 human-adjudication contract
**When** the findings are laid out for adjudication
**Then** each REAL dogfood finding is recorded INSPECTABLE with its `rule_id` + locators + advisory-vs-blocking
**verdict-eligibility** (`depth_supported` present = verdict-eligible / blocking; `None` = advisory), mapped
onto the 6.6 `finding_match_key` shape so a human Eng-Lead + QA-Lead can later tag each as TP/FP over a
real-repo finding set (each finding's identity unambiguous — RED-first where two distinct findings would
collapse to one match key, AI-E6-1) — recorded in the proof artifact / a committed adjudication-input surface;
**and** the human TP/FP adjudication itself is **NOT performed in this story** (it is the human step — the ONLY
step that may clear the gate), so `protocol_cleared` STAYS `False`, the `precision_gate_status()` marker STAYS
`provisional`, and NO ≥80% number is presented as authoritative / cleared (AC-PROVISIONAL). A committed defer
(six CC-3 fields, `target_story: epic-7-minions-dogfood-precision`) records the still-open human-adjudication
step over these REAL findings.

**AC-PROVISIONAL — The ≥80%-precision gate STAYS PROVISIONAL — the OI1 honesty keystone; NO fabricated cleared gate, NO over-claimed externalization (OI1 / DF-6-6-A / the honesty NFR)**
**Given** the dogfood run + the 6.6 `precision_gate_status_for(...)` / the 6.5 `PRECISION_GATE_STATUS` marker
**When** the precision / gate status is reported in the proof artifact / bundle / Dev Notes
**Then** the gate is reported **PROVISIONAL** (`protocol_cleared=False`; the marker is NOT flipped; NO
production `protocol_cleared=True` call site is added): 7.2 EXECUTES the dogfood + produces the REAL findings +
lays them adjudication-ready ONLY, and does NOT run the human TP/FP adjudication (that is the human step); the
proof artifact + Dev Notes are scrupulously honest that (a) the run is Tier-A demo-heuristic-only
(AC-DEMO-GRADE) and (b) the ≥80% gate stays PROVISIONAL until the human adjudication over these REAL findings
runs — a REAL number (if any precision figure is shown at all) is presented ALONGSIDE the provisional flag,
NEVER as a cleared/authoritative ≥80% result; a committed test is RED against a silently-flipped
`protocol_cleared=True` or an injected "gate cleared / ≥80% achieved" over-claim, then green. The DF-6-6-A
progress note (append-only, six CC-3 fields) records the executed dogfood + the adjudication-ready findings +
the still-open human half.

**AC-COMPLETE-SET — Complete-the-declared-set over the 7.2 deliverables, each RED-first / honest where applicable; no-crash on real-repo edges (AI-E5-1 / AI-E6-1 / AI-E4-2 / AR10)**
**Given** the full DECLARED set of 7.2 deliverables
**When** the story is built
**Then** EACH member is explicitly covered: (1) the reproducible dogfood execution + proof artifact
(AC-EXECUTE); (2) the SIGNED source-free bundle over the REAL repo (AC-BUNDLE); (3) the reproduced signature
demo (AC-SIGNATURE); (4) the 100%-reproducibility check (AC-REPRODUCIBLE, RED-first non-determinism); (5) the
`grade: demo-heuristic-only` red-team flag (AC-DEMO-GRADE, RED-first dropped-flag / over-claim); (6) the
adjudication-ready findings layout (AC-ADJUDICATION-READY, RED-first collision); (7) the provisional-gate
honesty report + the DF-6-6-A progress note + the human-adjudication defer (AC-PROVISIONAL, RED-first
silently-flipped gate); AND the enumeration is EXPLICIT in the proof artifact + the test module. The dogfood
generator never raises opaquely over the real repo (a parse failure / non-ASCII path / over-hard-limit module /
empty-or-oversized unit → a typed, NAMED outcome; a bundle-export / persist / lint failure → a typed
`EvidenceBundleError` / `PipelineError` / `StoreIntegrityError` citing the stage — the AI-E4-2 no-crash leg).

**AC-NO-REGRESSION — No regression / no scope creep; structural gates green; ≤1200 lines; frozen surfaces unchanged; the pre-`review` test-existence precondition (AI-E5-7 / AI-E5-3 / NFR-M1/M2 / AR7)**
**Given** the new dogfood-execution generator/test + the proof artifact + the persisted bundle + any additive
`grade` field
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the prior green baseline — 1243 passed at 7.1 — + the new 7.2 tests + the dogfood run), the
no-web-imports gate, the single-serializer AST gate, the file-size gate, and the 4.4 secret-containment suite
stay green; `mypy` is clean on any new/modified modules
**And** NO behavior-changing diff to the frozen Epic-1..6 production surfaces, the 7.1 `dogfood/partition_plan.py`
contract, the 4.3 `EvidenceBundle` SHAPE, OR the 6.5 `_registry.py` SHAPE (the story CONSUMES
`run_audit_detailed` / `build_evidence_bundle` / `persist_evidence_bundle` / `lint_referential_integrity` /
`compute_precision`; `pipeline.py` / `evidence/bundle.py` / `store/integrity.py` / `precision/replay_harness.py`
/ `verdict/*` / `ledger/*` / `store/*` / `models.py` show NO behavior-changing diff), NO forked
pipeline/bundle/serializer/lint/harness, NO `cli.py` flag, NO HTTP route, NO new CI job, NO live LLM call,
`protocol_cleared` NOT flipped; **IF** an additive `grade` field on a frozen model is unavoidable it is a
default-preserving optional field (the 4.1 additive-field precedent) with the byte-compat impact narrated
**And** each new/modified file is ≤1200 lines (NFR-M1); the new files cite their `APAA-FR-29` / `APAA-FR-17` /
`APAA-FR-30` / `APAA-FR-21` / `APAA-NFR-D1` / `APAA-NFR-S1` / `APAA-AR4` drivers in the module/artifact
docstring + the locked test area / index; the mandatory artifacts (the proof artifact + the persisted bundle
proof + the signature-demo/reproducibility/adjudication-ready tests + the DF-6-6-A progress note + the
human-adjudication defer) EXIST + pass + any new defer is filed BEFORE the story flips to `status: review`
(AI-E5-3 test-existence discipline). **Test area `APAA-DOGFOOD`** (`TC-APAA-DOGFOOD-001-NN`, CONTINUE from the
7.1 index — 7.1 locked `TC-APAA-DOGFOOD-001-01..17`, so 7.2 starts at **18**; lock the area + start index in
the generator/test docstring) — plus any signature-demo e2e additions under `APAA-PIPELINE`.

## Tasks / Subtasks

- [x] **Task 0 — Re-read the REAL reuse surfaces; LOCK the dogfood-execution design, the bundle-export/persist call, the demo-grade flag placement, and the OI1 provisional constraint** (AC: EXECUTE, BUNDLE, DEMO-GRADE, PROVISIONAL)
  - [x] Re-read `minions_core/apaa/pipeline.py::run_audit_detailed` (signature `(request, *, store_writer=None)
        -> AuditResult`; the `AuditResult` slots `verdict`/`locators`/`floor_report`/`negative_assurance`/
        `coverage_report`; NO LLM — Tier-A / zero-token) + `models.py::AuditRequest` (`repo_path`/`commit`/
        `budget`/`materiality_bar`/`critical_paths`). LOCK: REUSE the pipeline; run per 7.1 unit or over the
        repo under `budget=843`; do NOT fork a pipeline.
  - [x] Re-read `minions_core/apaa/dogfood/partition_plan.py` (7.1: `build_full_repo_plan` / `size_budget` /
        `compute_loc_by_file` / the git-`ls-files` enumeration over `minions_core/` excluding `apaa/`; the
        pinned-commit handling for a dirty/untracked tree) + `minions-dogfood-partition-plan.md` /
        `minions-dogfood-budget-plan.md`. LOCK: CONSUME the 7.1 plan (the `$X`=843 ceiling, the 4-unit map);
        do NOT re-author the partitioner / a second budget-sizing.
  - [x] Re-read `minions_core/apaa/evidence/bundle.py` (`build_evidence_bundle` / `bundle_to_canonical_payload`
        / `bundle_to_canonical_bytes` / `persist_evidence_bundle` / `EvidenceBundle` SHAPE /
        `EVIDENCE_BUNDLE_PRODUCER` / the structural no-source moat) + `store/integrity.py::
        lint_referential_integrity(reader) -> IntegrityReport` + `store/{writer,reader,canonical,envelope}.py`
        (the content-addressed, prev-hash-chained "signature"; `created_at` excluded from the hash). LOCK:
        REUSE the 4.3 export + the 1.1 envelope; run the lint at the impure call site (NOT inside the builder);
        do NOT fork a bundle model / serializer.
  - [x] Re-read `precision/replay_harness.py::compute_precision` / `precision_gate_status_for` (`protocol_cleared`
        default `False`) + `_registry.py::precision_gate_status()` / `PRECISION_GATE_STATUS` + the 6.6
        `finding_match_key` + `precision-validation-protocol.md` §4/§5 (the human-adjudication contract). LOCK:
        REPORT the gate PROVISIONAL; do NOT flip `protocol_cleared` / the marker; lay findings adjudication-ready
        via the `finding_match_key` shape; do NOT run the adjudication.
  - [x] Confirm the dogfood run is Tier-A / zero-token (verify `run_audit_detailed` wires NO `LLMDispatchPort`)
        → LOCK the `grade: demo-heuristic-only` flag placement (DN-GRADE: prefer the PROOF ARTIFACT / a dogfood
        wrapper; a frozen-model additive field ONLY if unavoidable, default-preserving). Record the OI1
        no-overclaim + no-flip constraint in Dev Notes.
- [x] **Task 1 — Execute the dogfood + produce the reproducible proof artifact** (AC: EXECUTE, DEMO-GRADE, COMPLETE-SET)
  - [x] A committed generator/test (e.g. `minions_core/apaa/dogfood/proof_run.py` or an extension of the 7.1
        `dogfood/` package — keep files ≤1200 lines) that runs `run_audit_detailed` over the real Minions repo
        @ the pinned commit under `AuditRequest(..., budget=843)`, REUSING the 7.1 plan; records the verdict +
        coverage deep-% (`Fraction`) + finding counts by `rule_id` (advisory vs blocking) + the within-ceiling
        confirmation + the 3.2 halt-if-breached demonstration + the `grade: demo-heuristic-only` provenance
        into a committed `minions-dogfood-proof.md`. Deterministic / byte-stable for the same repo@commit.
  - [x] No-crash over the real repo (AI-E4-2): parse failures / non-ASCII paths / an over-hard-limit module /
        an empty-or-oversized unit → a typed NAMED outcome, never a bare traceback.
- [x] **Task 2 — Export + persist the SIGNED, source-free evidence bundle for the dogfood run** (AC: BUNDLE, COMPLETE-SET)
  - [x] Run `lint_referential_integrity` over the dogfood `.apaa/` tree → `IntegrityReport`; call
        `build_evidence_bundle(result, integrity_report, commit=..., apaa_version=...)`; persist via
        `persist_evidence_bundle(writer, bundle)` (content-addressed, prev-hash-chained, containment-checked).
        Record the bundle locator + content-hash + envelope provenance in the proof artifact.
  - [x] Assert NO Minions source byte / secret value in the serialized bundle bytes + the persisted artifact
        (searched as UTF-8 over the REAL Minions tree — the 4.3 moat proven over the real repo) WHILE the
        bundle is non-empty + the verdict + scope statement present; re-read via the 1.3 reader → EQUAL bundle
        (round-trip byte-identical).
- [x] **Task 3 — Reproduce the signature demo + prove reproducibility + flag demo-grade** (AC: SIGNATURE, REPRODUCIBLE, DEMO-GRADE)
  - [x] Reproduce `GitHub green · Sonar green · APAA 🔴 tests appear vacuous` — audit a real Minions vacuous
        test (if found) ELSE a planted-in-Minions vacuous cartridge (via `_cartridge.py::stage_cartridge`) →
        assert `NOT_READY_FOR_RELEASE` / exit 2 / `vacuous_test_ast` first in `ordered_findings` (the 1.7
        precedent). Commit the assertion as a test.
  - [x] Two dogfood runs on the same commit → identical verdict + BYTE-IDENTICAL `bundle_to_canonical_bytes`
        (NFR-D1/P1). RED-first against an injected non-determinism (unsorted findings) → byte-identity FAILS,
        then green.
  - [x] Assert the `grade: demo-heuristic-only` flag + the externalization-guard language present in the proof
        artifact / bundle metadata (per DN-GRADE); RED-first if the flag is dropped or an
        "externalization-grade / validated" over-claim phrase is injected.
- [x] **Task 4 — Lay the REAL dogfood findings ADJUDICATION-READY (do NOT run the adjudication / flip the gate)** (AC: ADJUDICATION-READY, PROVISIONAL)
  - [x] Record each REAL dogfood finding INSPECTABLE (`rule_id` + locators + advisory-vs-blocking
        verdict-eligibility via `depth_supported`), mapped onto the 6.6 `finding_match_key` shape, into the
        proof artifact / a committed adjudication-input surface — so a human Eng-Lead + QA-Lead can later tag
        each TP/FP per `precision-validation-protocol.md` §4/§5. RED-first where two distinct findings would
        collapse to one match key (AI-E6-1).
  - [x] Confirm the gate STAYS PROVISIONAL: `protocol_cleared` NOT flipped, the `precision_gate_status()`
        marker NOT flipped, NO ≥80% number presented as authoritative. RED-first against a silently-flipped
        `protocol_cleared=True` / an injected "gate cleared" over-claim.
- [x] **Task 5 — The parametrized 7.2 test module** (AC: all)
  - [x] `tests/apaa/test_dogfood_proof.py` (area `APAA-DOGFOOD`, `TC-APAA-DOGFOOD-001-NN` continuing from **18**):
        assert the dogfood run completes within `$X`=843 (AC-EXECUTE) + the 3.2 halt-if-breached; the bundle is
        signed + source-free + round-trips (AC-BUNDLE); the signature demo 🔴 (AC-SIGNATURE); two-run
        byte-identity (AC-REPRODUCIBLE, RED-first non-determinism); the demo-grade flag + externalization guard
        (AC-DEMO-GRADE, RED-first); the adjudication-ready finding layout (AC-ADJUDICATION-READY, RED-first
        collision); the gate stays PROVISIONAL (AC-PROVISIONAL, RED-first silently-flipped); the
        complete-the-declared-set enumeration + no-crash edges (AC-COMPLETE-SET). Each assertion failure NAMES
        the unit / finding / cartridge id.
- [x] **Task 6 — Run + mypy + gates + the DF-6-6-A progress note + the human-adjudication defer + the pre-`review` precondition** (AC: PROVISIONAL, NO-REGRESSION)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` → all
        pass (prior baseline + the new 7.2 tests + the dogfood run). `mypy` clean on any new modules. Confirm
        NO behavior-changing diff to the frozen Epic-1..6 / 7.1 surfaces + the 4.3/6.5 SHAPES. Confirm the
        no-web-imports / single-serializer / file-size / 4.4 gates green. NO `cli.py`/HTTP/CI-job change; NO
        detector/Prosecutor/partitioner/budget-core/bundle-core edit; NO live LLM; `protocol_cleared` NOT
        flipped.
  - [x] **AI-E5-4 / AI-E6-6:** file the DF-6-6-A progress note append-only in
        `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (six CC-3 fields; dogfood EXECUTED + real
        findings adjudication-ready; human-adjudication half still open, `target_story:
        epic-7-minions-dogfood-precision`) AND a NEW defer for the human-adjudication step (six CC-3 fields).
        Note DF-6-7-A (HITL wiring) stays open — do NOT close it. File any newly-surfaced frozen-surface gap the
        same way.
  - [x] **AI-E5-3 / AI-E2-1 GATE:** the mandatory artifacts (the proof artifact + the persisted-bundle proof +
        the test module + the DF-6-6-A progress note + the human-adjudication defer) EXIST + pass BEFORE the
        `review` flip; the Dev Agent Record is filled completely (no blank placeholders), incl. the locked
        dogfood-execution design + the bundle-export call + the demo-grade flag placement + the
        adjudication-ready layout + the OI1 no-overclaim statement.

## Dev Notes

### Architecture / contract anchors (re-read before coding)
- **Pipeline — REUSE, do not fork:** `minions_core/apaa/pipeline.py::run_audit_detailed(request, *,
  store_writer=None) -> AuditResult`. The `AuditResult` carries `verdict` (the 1.6 `AuditVerdict` with
  `ordered_findings` / `deep_ratio: Fraction` / `exit_code` / `blocking_finding_count`), `locators`,
  `floor_report`, `negative_assurance` (the 4.1 wrapper), `coverage_report` (the 2.2 surface). It calls **NO
  LLM** — Tier-A / zero-token (NFR-D2). The 3.2 halt fires under `AuditRequest.budget` → `budget_config_from_budget`.
- **7.1 plan — CONSUME, do not re-author:** `minions_core/apaa/dogfood/partition_plan.py` +
  `minions-dogfood-partition-plan.md` (4 units, 135 files, 36712 LOC, 332 cut edges) +
  `minions-dogfood-budget-plan.md` (`$X` = **843** = V1 total 675 × 5/4 int-floored; NFR-C1 baseline
  `675/36712`). The dogfood runs under `budget=843`.
- **Evidence bundle — REUSE, do not fork:** `minions_core/apaa/evidence/bundle.py::build_evidence_bundle(result,
  integrity_report, *, commit, apaa_version) -> EvidenceBundle` (PURE) + `bundle_to_canonical_bytes` (single
  1.1 serializer) + `persist_evidence_bundle(writer, bundle) -> str` (impure, content-addressed,
  prev-hash-chained, producer `apaa.evidence.bundle`). The no-source moat is STRUCTURAL (no source/secret
  field). Feed the 4.2 `lint_referential_integrity(reader) -> IntegrityReport` at the impure call site.
- **The "signature" = the 1.1 envelope:** `store/{canonical,envelope}.py` — content hash over the canonical
  payload + the prev-hash chain (NFR-A1); the point-in-time stamp is the envelope `created_at`, EXCLUDED from
  the hash (NFR-D3). No new signing scheme.
- **Precision / provisional gate — REUSE, do NOT flip:** `precision/replay_harness.py::compute_precision` /
  `precision_gate_status_for(..., protocol_cleared=False)` + `_registry.py::precision_gate_status()` /
  `PRECISION_GATE_STATUS`. The 6.6 `finding_match_key` is the adjudication-ready identity shape.
  `protocol_cleared` STAYS `False`.
- **Fixed-precision — AR4 (the byte-diff landmine):** every persisted cost/ratio figure is `int` credits / a
  `Fraction` — NO float (the 1.1 serializer rejects float; NFR-P1 byte-identity).
- **Secret-containment suite (EXTEND, do not fork):** `tests/security/test_apaa_secret_containment.py` (4.4).
- **Structural gates:** the no-web-imports gate (`test_no_web_imports.py` — append any new module to
  `_MODULES_UNDER_GUARD`), the single-serializer AST gate, the file-size gate — all stay green (the dogfood
  generator is pure/FastAPI-free/LLM-free; REUSE the canonical serializer for any bytes).

### Locked decisions (resolve in dev; recorded here per §3.4)
- **DN-DOGFOOD-REUSE.** The dogfood is EXECUTED by REUSING `run_audit_detailed` over the real Minions repo @
  the pinned commit under `budget=843` (the 7.1 `$X`), per the 7.1 4-unit plan — a committed generator/test
  records the proof deterministically. NO forked pipeline, NO hand-typed proof that rots, NO re-partitioning.
  (Follow the 7.1 `dogfood/partition_plan.py` pattern for the dirty/untracked-tree pinned-commit handling — the
  APAA sub-tree is git-untracked; the 7.1 generator sidestepped `load_repo_at_commit`'s clean-tree requirement
  via `git ls-files -z` over committed content scoped to `minions_core/` excluding `apaa/`.)
- **DN-BUNDLE-REUSE.** The SIGNED bundle is exported via `build_evidence_bundle` + persisted via
  `persist_evidence_bundle` (content-addressed, prev-hash-chained — the 4.3 seam + the 1.1 envelope). The 4.2
  lint runs at the impure call site (NOT inside the pure builder — the 4.3 DN-WIRING precedent). NO forked
  bundle model / serializer / signing scheme.
- **DN-GRADE (the AC-DEMO-GRADE placement decision — the design crux).** The dogfood is Tier-A / heuristic-only
  (`run_audit_detailed` wires no LLM). The `grade: demo-heuristic-only` flag + the externalization-guard
  language are recorded on the **PROOF ARTIFACT** (`minions-dogfood-proof.md`) and/or a dogfood-run wrapper
  object — PREFER this over mutating the frozen 4.1 `NegativeAssuranceVerdict` / 4.3 `EvidenceBundle` SHAPE.
  **ONLY IF** an additive frozen-model field is genuinely required for the bundle to self-carry the grade, add
  it as a default-preserving OPTIONAL field (the 4.1 `floor_report`/`coverage_report` additive-field precedent
  — a default-`None`/default-preserving field keeps existing bundle bytes byte-identical) and narrate the
  byte-compat impact + the SHAPE-additive-not-changed argument. Do NOT introduce a `float`. Lock the final
  placement in Completion Notes.
- **DN-PROVISIONAL (the OI1 keystone — do NOT soften — the operator epic-boundary decision).** 7.2 EXECUTES the
  dogfood + produces the REAL findings + lays them ADJUDICATION-READY. The ≥80%-precision gate STAYS PROVISIONAL
  (`protocol_cleared=False`; the `precision_gate_status()` marker NOT flipped; NO production
  `protocol_cleared=True`). The human TP/FP adjudication over these REAL findings (the DF-6-6-A human half) is a
  HUMAN step + a follow-up defer — the ONLY step that may clear the gate. Do NOT fabricate or softclaim a
  cleared gate, and do NOT present the Tier-A demo run as externalization evidence — honest coverage is APAA's
  whole thesis and over-claiming is the exact failure mode this lock forbids.
- **DN-ADJUDICATION-READY.** Lay each REAL finding out with its `rule_id` + locators + verdict-eligibility,
  mapped to the 6.6 `finding_match_key` shape, so the human adjudication is a per-finding TP/FP tag over a
  real-repo finding set. Each finding's identity is unambiguous (RED-first collision — AI-E6-1). The
  adjudication itself is NOT performed here.
- **DN-ESCALATION (DF-6-7-A stays open).** Wiring the 6.7 HITL escalation + decision-record into the live
  pipeline/CLI (the config source + a `--decision` flag + a human-wait transport) is OUT of scope for 7.2 (the
  dogfood is the first live consumer, but the wiring is a distinct task). DF-6-7-A stays open; note it, do NOT
  close it.
- **DN-NO-PROD-CHANGE-FROZEN.** 7.2 adds a committed proof artifact + a dogfood-execution generator + a test
  module + a DF-6-6-A progress note + a human-adjudication defer (+ at most one default-preserving additive
  grade field per DN-GRADE). It CONSUMES `run_audit_detailed` / `build_evidence_bundle` /
  `persist_evidence_bundle` / `lint_referential_integrity` / `compute_precision` / the 7.1 plan as-is; it edits
  NO detector/Prosecutor/partitioner/budget-core/bundle-core/frozen-contract, does NOT change the 4.3
  `EvidenceBundle` SHAPE (beyond a default-preserving additive field IF unavoidable) or the 6.5 `_registry.py`
  SHAPE, adds NO `cli.py`/HTTP/CI-job. If executing surfaces a gap, that is a DEFER (six CC-3 fields), not a
  7.2 edit.

### OI1 honesty constraints (the central theme — do NOT soften)
- **OI1 LOCKED — the ≥80%-precision gate is PROVISIONAL below the cleared human adjudication.** The synthetic
  corpus (7.1: 5 distinct classes) bootstrapped the PROVISIONAL gate. 7.2 produces the REAL dogfood findings +
  lays them adjudication-ready, but keeps the gate PROVISIONAL; only the human adjudication over these REAL
  findings clears it (a human step + a follow-up defer). NEVER a fabricated cleared gate; NEVER a Tier-A demo
  run presented as externalization evidence (the `grade: demo-heuristic-only` red-team guard is the mechanism).
- **OI2 / OI3 (inherited from 7.1).** The dogfood covers all 4 units (OI2 full-repo multi-partition; V1 does
  MULTI-UNIT, NOT cross-partition SEAM — the 6.4 `cross_partition` pass is the V1 mitigation). `$X` = 843 is
  the empirically-sized ceiling (OI3 resolved in the plan artifact; `budget_governor.py` keeps no hardcoded
  default).

### Carry-forward action items addressed
- **AI-E6-2** — DF-6-6-A: 7.2 EXECUTES the dogfood + produces the REAL findings + lays them adjudication-ready;
  the human adjudication half stays open (a defer).
- **AI-E6-1** — payload/event-identity: each real finding's adjudication identity is unambiguous (RED-first
  collision on the `finding_match_key`).
- **AI-E5-1** — complete-the-declared-set over the 7.2 deliverables (AC-COMPLETE-SET).
- **AI-E4-2** — no-crash over the real repo + the bundle export/persist/lint (typed NAMED outcomes).
- **AI-E1-1** — non-ASCII discipline under `PYTHONIOENCODING=utf-8`.
- **AI-E5-3 / AI-E5-7 / AI-E6-6** — pre-`review` test-existence + structural gates green + partial-reuse
  docstring precision + defer back-fill.

### Previous-story intelligence (7.1 — the immediate predecessor + the plan this story executes)
- 7.1 (done, code-review PASS) produced the FULL-REPO partition map (4 bounded units: 40/34/40/21 files;
  12577/13998/9438/699 LOC — all ≤ the 60/25k hard ceiling; 332 cut edges) + the empirically-sized `$X` = 843
  credits (V1 total 675 × 5/4; NFR-C1 baseline `675/36712`) + grew the corpus 3→**5 distinct classes**
  (`vacuous_heuristic_basic`→`vacuous_test_heuristic` planted, `cross_partition_seam`→`cross_partition`
  holdout — both CONFIRMED-emitted by the real detectors). It locked `TC-APAA-DOGFOOD-001-01..17`, so **7.2
  continues at 18**. `dogfood/partition_plan.py` is 611 lines (budget any additions ≤1200).
- **OI1 KEYSTONE HELD by 7.1** — the gate stayed PROVISIONAL (`protocol_cleared` default `False`, marker
  unflipped). 7.2 must HOLD the same keystone: EXECUTE + produce REAL findings + lay them adjudication-ready,
  but do NOT flip the gate.
- The whole APAA prod tree is currently git-UNTRACKED (the sub-tool is not yet git-committed), so `git diff`
  over the frozen surfaces is empty/N-A — use mtime (as the 6.5/6.6/7.1 reviewers did) as the load-bearing
  no-change evidence, and keep the dogfood generator/test + the proof artifact + the persisted-bundle proof the
  only added files.
- The Epic-6 retro AI-E6-4 flagged `pipeline.py` at 1090/1200 for a proactive split BEFORE live-wiring. 7.2
  RUNS the pipeline (`run_audit_detailed`) but does NOT EDIT it — no split is forced by 7.2 (the dogfood
  generator is a NEW module that CALLS the pipeline). If any 7.2 touch approaches the limit, note it / defer a
  split (do NOT edit `pipeline.py` for 7.2).
- `pipeline.py` is 1090 lines; `evidence/bundle.py` and `dogfood/partition_plan.py` (611) are the reuse seams —
  do NOT edit them; the dogfood-execution generator is a NEW module (or an additive extension of the
  `dogfood/` package) that imports them.

### Project structure notes
- New generator (production): `minions_core/apaa/dogfood/proof_run.py` (or an additive extension of
  `dogfood/partition_plan.py` if it stays ≤1200 — PREFER a new sibling module for cohesion). Append it to
  `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py`.
- New test: `tests/apaa/test_dogfood_proof.py` (area `APAA-DOGFOOD`, `TC-APAA-DOGFOOD-001-NN` from **18**); +
  any signature-demo e2e under `APAA-PIPELINE`.
- New committed artifact: `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` (the proof artifact +
  the adjudication-ready findings layout + the `grade: demo-heuristic-only` flag + the provisional-gate report).
- DF-6-6-A progress note + the human-adjudication defer: append-only in
  `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`.
- All files ≤1200 lines; run everything under `PYTHONIOENCODING=utf-8`.

### References
- Epic source: `_bmad-output/design-artifacts/ArgusAgent/epics.md` §Epic 7 / Story 7.2 (lines 996–1018) + the "Open
  delivery inputs — LOCKED 2026-06-18" block (OI1/OI2/OI3).
- The plan this story executes: `_bmad-output/design-artifacts/ArgusAgent/stories/7-1-minions-full-repo-partition-budget-sizing-plan.md`
  + `minions-dogfood-partition-plan.md` + `minions-dogfood-budget-plan.md`.
- Reuse seams: `pipeline.py::run_audit_detailed` (1.7/3.x/6.x); `evidence/bundle.py::build_evidence_bundle`/
  `persist_evidence_bundle` (4.3); `store/integrity.py::lint_referential_integrity` (4.2);
  `store/{canonical,envelope,writer,reader}.py` (1.1/1.3); `precision/replay_harness.py::compute_precision` +
  `_registry.py::precision_gate_status()` (6.6/6.5); `dogfood/partition_plan.py` (7.1);
  `tests/apaa/cartridges/_cartridge.py::stage_cartridge` (6.5).
- Drivers: DF-6-6-A / DF-6-6-A-P1 / DF-6-7-A (`deferred-work.md`); the Epic-6 retro AI-E6-2
  (`epic-6-retro-2026-07-02.md`); `precision-validation-protocol.md` §4/§5 (the human-adjudication contract).
- Operator epic-boundary decision (2026-07-02): synthetic corpus bootstrapped a PROVISIONAL gate; the REAL
  dogfood findings feed a later human TP/FP adjudication that clears the ≥80% gate. 7.2 ENABLES it (findings
  adjudication-ready) but does NOT run it or flip the gate.

## Dev Agent Record

### Context Reference
- Epic source: `_bmad-output/design-artifacts/ArgusAgent/epics.md` §Epic 7 / Story 7.2.
- Reuse seams: `pipeline.py` (1.7/3.x/6.x), `evidence/bundle.py` (4.3), `store/integrity.py` (4.2),
  `store/{canonical,envelope,writer,reader}.py` (1.1/1.3), `precision/replay_harness.py` + `_registry.py`
  (6.6/6.5), `dogfood/partition_plan.py` (7.1), `tests/apaa/cartridges/_cartridge.py` (6.5).
- Driver: DF-6-6-A / DF-6-6-A-P1 (`deferred-work.md`); Epic-6 retro AI-E6-2 (`epic-6-retro-2026-07-02.md`);
  the operator epic-boundary decision (2026-07-02).

### Agent Model Used

claude-opus-4-8[1m] (Claude Opus 4.8, 1M context) — BMAD dev-story worker, implement mode.

### Debug Log References

- Live dogfood over the REAL Minions tree (135 tracked `minions_core/` modules, 36712 LOC, 7.1 4-unit plan):
  verdict `NOT_READY_FOR_RELEASE` / exit `2`, deep-% `13/15`, `blocking_finding_count == 0` (all findings
  advisory / verdict-ineligible = the structural Tier-A heuristic-only signal), 2906 total findings across
  3 classes (`cross_partition` ×332, `hardcoded_secret` ×2289, `orphan_code` ×285).
- Within-ceiling cost: V1 deterministic total **675 credits**, `$X` = **843** → `fits_within_ceiling is True`;
  a ceiling one credit below the total breaches (`breaches_below_total is True` — the 3.2 halt demo). All int /
  Fraction (`675/36712` baseline) — no float.
- SIGNED bundle: content-addressed `state/<content_hash>.json`, 4.2 integrity lint `consistent is True`,
  two runs → byte-identical `bundle_to_canonical_bytes` (100% reproducible — NFR-D1/P1). RED-first: a reversed
  finding order into the bundle breaks byte-identity (proving the assertion is load-bearing), then green.
- Signature demo: `vacuous_basic` cartridge → `vacuous_test_ast` FIRST in `ordered_findings`, blocking,
  `NOT_READY_FOR_RELEASE` / exit 2 (the 🔴).
- Full required suite `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`:
  **1262 collected, all pass / 1 skipped**, exit 0 (baseline was 1243 at 7.1 + the new 7.2 tests). `mypy` clean on
  `dogfood/proof_run.py` (the only two errors are the pre-existing `radon` missing-stub notes pulled transitively
  from the FROZEN `detectors/tool_runner.py`, NOT my module). Single-serializer AST gate + no-web-imports gate +
  file-size gate green.
- **Review-surfaced correction during dev (guard-the-guard):** the first draft of the no-source bundle test used
  SYMBOL-name sentinels (`AgentAuthMiddleware`, a class name). That FAILED — because a bundle finding legitimately
  cites a symbol in a locator's `ast_span` (`cross_partition:minions_core/agent_auth.py::AgentAuthMiddleware`),
  which IS the FR13 "location", NOT a source-code-body byte. Corrected the sentinels to real source-CODE-BODY bytes
  (`import hashlib` / `raise ValueError` / `HMAC-SHA256` docstring phrase) + added a non-vacuity guard asserting each
  is genuinely present in the real source first. This is the correct 4.3 no-source-retention property (no source
  BYTES / secret VALUES; symbol locators are in-scope), and it now proves the moat over the REAL Minions tree.

### Completion Notes List

- **AC-EXECUTE — DELIVERED.** New generator `minions_core/apaa/dogfood/proof_run.py` runs the FROZEN
  `pipeline.run_audit_detailed` (REUSED — no fork) over the real Minions source under `budget = $X = 843`. Locked
  DN-DOGFOOD-REUSE: because `load_repo_at_commit` refuses a drifted/untracked tree (the live APAA sub-tree is
  git-untracked), the generator MIRRORS the 6.5 `stage_cartridge` pattern — enumerates git-TRACKED `minions_core/`
  (excluding `apaa/`, the SAME 7.1 scope), copies into a fresh temp repo, `git init` + commit ONCE, and audits that
  clean on-pin snapshot. The audited BYTES are the real Minions source at the tracked commit
  (`7f8e1478...`, recorded as `commit_descriptor`). Within-ceiling + the 3.2 halt-if-breached demonstrated via the
  3.1 `account_spend` (no fork). Committed proof artifact `minions-dogfood-proof.md` (reproducible — a committed
  generator re-derives it, NOT a hand-typed report). TC-APAA-DOGFOOD-001-18/19/20/34.
- **AC-BUNDLE — DELIVERED.** SIGNED bundle via the 4.3 `build_evidence_bundle` + `persist_evidence_bundle` +
  the 4.2 `lint_referential_integrity` at the impure call site (the 4.3 DN-WIRING precedent) + the 1.1
  prev-hash-chained envelope (content-addressed `<content_hash>.json` = the signature; `created_at` excluded from
  the hash). No forked bundle model / serializer. No-source moat proven over the REAL tree (source-body sentinels
  absent from the bundle bytes + every persisted `.apaa/` artifact) WHILE the bundle is non-empty + verdict +
  findings present (redaction ≠ suppression). TC-APAA-DOGFOOD-001-21/22 + the extended 4.4 suite
  TC-APAA-SECURITY-001-23.
- **AC-SIGNATURE — DELIVERED.** `vacuous_basic` cartridge → blocking `vacuous_test_ast` FIRST in `ordered_findings`
  → `NOT_READY_FOR_RELEASE` / exit 2 (the 🔴 `GitHub green · Sonar green · APAA 🔴`). Committed test
  TC-APAA-DOGFOOD-001-23 (the 1.7 `TC-APAA-PIPELINE-001-01` precedent).
- **AC-REPRODUCIBLE — DELIVERED.** Two dogfood runs → byte-identical verdict + `bundle_to_canonical_bytes`
  (NFR-D1/P1). RED-first against an injected non-determinism (reversed finding order) → byte-identity fails, then
  green. TC-APAA-DOGFOOD-001-24.
- **AC-DEMO-GRADE — DELIVERED (DN-GRADE decision LOCKED).** The `grade: demo-heuristic-only` flag + the
  externalization-guard language are carried on the PROOF ARTIFACT + the pure `DogfoodProofRun` wrapper — the
  frozen 4.1 `NegativeAssuranceVerdict` / 4.3 `EvidenceBundle` SHAPE was NOT mutated (no additive frozen-model field
  was needed: the wrapper + artifact carry the grade, and every finding already carries `depth_supported=None` =
  advisory / verdict-ineligible, which IS the structural heuristic-only signal). RED-first against a dropped flag /
  an injected "externalization-grade / validated / gate cleared" over-claim phrase. TC-APAA-DOGFOOD-001-25/26.
- **AC-ADJUDICATION-READY — DELIVERED.** `adjudication_rows` lays each REAL finding CLASS out by the 6.6
  `finding_match_key` identity `(rule_id, verdict_eligible, advisory)` with count + sample locators (advisory-vs-
  blocking via `depth_supported`), rendered in proof §6 with an EMPTY human `TP/FP` column. Two DISTINCT classes
  never collapse to one row (AI-E6-1 — RED-first collision guard; row identity IS the match key; rows partition ALL
  findings). The human adjudication is NOT performed (`adjudication` tag stays empty). TC-APAA-DOGFOOD-001-27/28.
- **AC-PROVISIONAL — DELIVERED (OI1 KEYSTONE HELD).** The gate STAYS PROVISIONAL: `proof_run.py` NEVER passes
  `protocol_cleared=True` (grep-guarded by TC-APAA-DOGFOOD-001-30), the `DogfoodProofRun` carries no
  cleared-gate field, the gate status is the harness's `provisional (...)` string (NO ≥80% number presented as
  authoritative), and the 6.5 `precision_gate_status()` marker is NOT flipped. DF-6-6-A-P2 progress note + the NEW
  DF-7-2-A human-adjudication defer filed append-only (six CC-3 fields, `target_story:
  epic-7-minions-dogfood-precision`); DF-6-7-A (HITL wiring, DN-ESCALATION) stays OPEN, not closed.
  TC-APAA-DOGFOOD-001-29/30/31.
- **AC-COMPLETE-SET — DELIVERED.** The 8 declared members are enumerated EXPLICITLY in the test module docstring
  and each is covered. No-crash edges: an empty source set → typed `DogfoodProofError`; a non-existent repo
  enumeration → typed `DogfoodProofError`; the pure cost accounting over an empty file set is total-safe (no
  divide-by-zero). A pipeline / bundle / lint failure surfaces as the typed `PipelineError` / `EvidenceBundleError`
  / `StoreIntegrityError` (AR10). TC-APAA-DOGFOOD-001-32/33.
- **AC-NO-REGRESSION — HELD.** Suite 1262 pass / 1 skip; frozen Epic-1..6 + 7.1 surfaces + the 4.3/6.5 SHAPES
  mtime-unchanged (consumed by import, edited none); no forked pipeline/bundle/serializer/lint/harness; no
  `cli.py`/HTTP/CI-job change; no live LLM; `protocol_cleared` NOT flipped; files ≤1200 (proof_run 750, test 592,
  security 856). Structural gates (no-web-imports + single-serializer AST + file-size + 4.4 secret-containment)
  green; `proof_run` added to the no-web-imports import-isolation coverage as an IMPURE shell (the
  `pipeline`/`decision_record` precedent).
- **Locked decisions recorded (§3.4):** DN-DOGFOOD-REUSE (snapshot-materialize + REUSE run_audit_detailed);
  DN-BUNDLE-REUSE (4.3 seam + 1.1 envelope, lint at the impure call site); DN-GRADE (grade on the artifact +
  wrapper, NO frozen-model mutation); DN-PROVISIONAL / OI1 (gate stays provisional, never flipped);
  DN-ADJUDICATION-READY (6.6 match-key layout, human step not run); DN-ESCALATION (DF-6-7-A stays open).
- **OI1 no-overclaim statement (mandatory):** this run is Tier-A demo-heuristic-only and is NOT presented as
  externalization / assurance evidence; the ≥80%-precision gate STAYS PROVISIONAL; the human TP/FP adjudication
  over these REAL findings (DF-7-2-A) is the ONLY step that may clear it and is OUT of scope here.

### File List

- `minions_core/apaa/dogfood/proof_run.py` — NEW: the dogfood proof-run generator (impure orchestration +
  pure derivation/render; 750 lines).
- `tests/apaa/test_dogfood_proof.py` — NEW: the 7.2 test module (area APAA-DOGFOOD, TC-APAA-DOGFOOD-001-18..34).
- `tests/apaa/test_no_web_imports.py` — MODIFIED: appended `minions_core.apaa.dogfood.proof_run` to the
  import-isolation coverage (IMPURE-shell entry — FastAPI/LLM-free).
- `tests/security/test_apaa_secret_containment.py` — MODIFIED: appended TC-APAA-SECURITY-001-23 (the dogfood bundle
  over the REAL Minions repo is source-free, with a non-vacuity guard).
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` — NEW: the committed, reproducible proof artifact
  (verdict + within-ceiling + SIGNED bundle + signature demo + demo-grade flag + adjudication-ready findings +
  provisional-gate report).
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — MODIFIED (append-only): DF-6-6-A-P2 progress note + the
  NEW DF-7-2-A human-adjudication defer (six CC-3 fields).
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — MODIFIED: `7-2-...` in-progress → review.
- `_bmad-output/design-artifacts/ArgusAgent/stories/7-2-...md` — MODIFIED: tasks checked, Dev Agent Record, File List,
  Change Log, Status.

## Senior Developer Review (AI)

**Reviewer:** code-review gate (claude-opus-4-8[1m], BMAD QA gate — adversarial, stateless).
**Date:** 2026-07-03. **Iteration:** 1. **Outcome:** PASS → `done`.

This is the CAPSTONE of the whole APAA project and its externalization claim, so it was reviewed
as the highest-stakes gate: every headline figure was re-derived independently (not trusted from
the Dev record), the two hard keystones (no-source-retention of the SIGNED bundle + the OI1
provisional-gate honesty) were attacked directly, and the full required suite was re-run.

### Independent verification (not trusting the Dev record)
- **Full suite re-run:** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/
  tests/test_import_paths.py` → **1262 passed / 1 skipped**, exit 0 (matches the claimed baseline).
- **Live dogfood re-run** (`build_dogfood_proof('.')`) reproduces EVERY claimed figure byte-for-byte:
  verdict `NOT_READY_FOR_RELEASE` / exit `2`; 135 files / 36712 LOC / 4 units; deep-% `13/15`;
  **blocking = 0** (all findings advisory / `depth_supported=None` — the honest structural Tier-A
  signal); cost 675 credits WITHIN the `$X`=843 ceiling with `breaches_below_total=True` (the 3.2
  halt demo); grade `demo-heuristic-only`; integrity consistent; gate status starts `provisional`.
  Adjudication classes: `cross_partition ×332`, `hardcoded_secret ×2289`, `orphan_code ×285`.
- **mypy** clean on `proof_run.py` (the only 2 errors are the pre-existing `radon` missing-stub
  notes transitively pulled from the FROZEN `detectors/tool_runner.py`, NOT this module — as claimed).

### Keystone 1 — no-source-retention of the SIGNED bundle: CLEAN (no leak found)
The moat is **structural**: `EvidenceBundle` and `Recording` (`ledger/recording.py`) carry NO
source-body / secret-value field — only repo-relative locators (`file_path` + int lines), an
`ast_span` symbol/node REFERENCE, `rule_id`, a content-derived `recording_id`, and booleans. There
is no field a finding's locator or snippet could drag source text through. The Dev's guard-the-guard
correction (a symbol name in `ast_span` is the FR13 "location", not a source-body byte) is correct;
the test sentinels are genuine source-CODE-BODY bytes (`import hashlib` / `raise ValueError` /
`HMAC-SHA256`) with a non-vacuity guard asserting each is really present in the audited tree. TC-22/23
+ the 4.4 randomized-canary suite prove absence over the REAL Minions tree (not only a cartridge)
while the bundle stays non-empty (redaction ≠ suppression). The `hardcoded_secret ×2289` findings are
advisory LOCATOR records, not retained secret VALUES. **BUNDLE_LEAK: none.**

### Keystone 2 — OI1 provisional-gate honesty: HELD
`grep` confirms `protocol_cleared=True` appears NOWHERE in `proof_run.py` (also grep-guarded by
TC-30). `precision_gate_status_for(provisional=True)` returns the honest string that explicitly says
"the >=80% externalization gate stays PROVISIONAL ... an EARLY/PROVISIONAL signal, NOT a cleared
gate". The 6.5 `precision_gate_status()` marker is NOT flipped. The `grade: demo-heuristic-only` flag
+ the externalization guard are present on the wrapper AND the committed proof artifact; NO forbidden
over-claim phrase (`externalization-grade` / `validated deep audit` / `gate cleared` / `>=80%
achieved`, …) appears in the artifact or the live render. The Tier-A run is not dressed up as
externalization evidence. **GATE_STATUS: provisional (correct).**

### Reuse / no-fork / frozen-surface: CLEAN
`proof_run.py` REUSES `run_audit_detailed`, `build_evidence_bundle`/`persist_evidence_bundle`,
`lint_referential_integrity`, `finding_match_key`, and the 1.1 canonical serializer/envelope BY
IMPORT — no reimplementation. All frozen reuse seams are mtime-unchanged (2026-06-27..30, strictly
before the 2026-07-03 proof_run.py write); the git-untracked APAA tree makes `git diff` empty, so
mtime is the load-bearing no-change evidence (the 6.5/6.6/7.1 reviewer precedent). No `float`, no
second `json.dumps`, no new hasher in the new module (int credits / `Fraction` ratios only — AR4).
The `AdjudicationRow.match_key` shape `(rule_id, verdict_eligible, advisory)` is identical to the 6.6
`finding_match_key`. The RED-first non-determinism test (reversed finding order → byte-identity fails)
is non-vacuous (2906 findings > 2). Files ≤1200 (proof_run 750, test 592). Headless — no UI / CLI flag
/ HTTP route / CI job. Both CC-3 defers (DF-6-6-A-P2, DF-7-2-A) carry all six fields; DF-6-7-A stays open.

### Findings
- **[Low] `minions_core/apaa/dogfood/proof_run.py:166` — provenance consistency (not a blocker).**
  `DOGFOOD_APAA_VERSION = "1.43.0"` diverges from `minions_core/apaa/__init__.__version__ = "0.1.0"`
  (the documented single source for the envelope `apaa_version`). Cosmetic only: the bundle records a
  byte-stable, test-pinned string, so reproducibility/no-source/gate properties are all unaffected.
  Suggested (future, non-gating): source the version from `apaa.__version__` or reconcile the two so a
  reader of the bundle sees one canonical APAA version. Left as a Low note — does not warrant blocking
  the capstone.

### Verdict
No unresolved decision-needed or patch findings; no High/Medium issues; tests/lint/build green; every
AC independently re-verified; both hard keystones held. **PASS → `done`.**

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-07-03 | 1.1 | code-review gate (claude-opus-4-8[1m], adversarial, iter 1) — **VERDICT: PASS → done.** Re-verified INDEPENDENTLY (not trusting the Dev record): full suite re-run **1262 passed / 1 skipped**; live dogfood re-run reproduces every headline figure byte-for-byte (verdict NOT_READY_FOR_RELEASE/exit 2, 135 files/36712 LOC/4 units, deep-% 13/15, **0 blocking**, 675 credits within $X=843 + 3.2 halt, grade demo-heuristic-only, integrity consistent, 3 finding classes cross_partition×332/hardcoded_secret×2289/orphan_code×285); mypy clean on proof_run.py (only pre-existing radon-stub notes from the FROZEN tool_runner.py). **Keystone 1 (no-source bundle): CLEAN — structural moat confirmed (EvidenceBundle/Recording carry no source-body/secret-value field; ast_span is a symbol REFERENCE = FR13 location, not source bytes); TC-22/23 + 4.4 canary suite prove absence over the REAL tree; hardcoded_secret findings are advisory locators, not retained secret values. BUNDLE_LEAK: none.** **Keystone 2 (OI1): HELD — protocol_cleared=True nowhere (grep-guarded); precision_gate_status_for(provisional=True) returns the honest 'NOT a cleared gate' string; 6.5 marker unflipped; grade flag + externalization guard present; no over-claim phrase in artifact/render.** Reuse-by-import (no fork); frozen seams mtime-unchanged (2026-06-27..30 < proof_run 2026-07-03); no float/json.dumps/new hasher; RED-first non-determinism non-vacuous (2906 findings); files ≤1200; headless; both CC-3 defers 6-field-complete, DF-6-7-A open. 1 Low note (DOGFOOD_APAA_VERSION 1.43.0 vs __init__ 0.1.0 — cosmetic, non-gating). Senior Developer Review (AI) written into story file. Status → done. **APAA project CAPSTONE COMPLETE.** | code-review (AI) |
| 2026-07-02 | 1.0 | dev-story (implement, claude-opus-4-8[1m]) — all 8 ACs DELIVERED. EXECUTED the Minions dogfood: `run_audit_detailed` (REUSED, no fork) over the REAL Minions source (135 modules / 36712 LOC, 7.1 4-unit plan, materialized into a clean on-pin snapshot via the 6.5 `stage_cartridge` pattern) under `$X`=843 → verdict `NOT_READY_FOR_RELEASE`/exit 2, deep-% `13/15`, 0 blocking, 675 credits within-ceiling + the 3.2 halt demo → committed `minions-dogfood-proof.md` (AC-EXECUTE). SIGNED source-free bundle via the 4.3 `build_evidence_bundle`/`persist_evidence_bundle` + the 4.2 lint + the 1.1 prev-hash-chained envelope; no-source moat proven over the REAL tree (AC-BUNDLE). Reproduced the `GitHub green · Sonar green · APAA 🔴` signature demo (AC-SIGNATURE). 100% reproducibility — byte-identical verdict + bundle bytes, RED-first non-determinism (AC-REPRODUCIBLE). `grade: demo-heuristic-only` flag + externalization guard on the artifact + wrapper — NO frozen-model mutation (DN-GRADE); RED-first over-claim (AC-DEMO-GRADE). REAL findings laid ADJUDICATION-READY by the 6.6 `finding_match_key` shape, RED-first collision (AC-ADJUDICATION-READY). **OI1 KEYSTONE HELD: gate STAYS PROVISIONAL — `protocol_cleared` NOT flipped, marker NOT flipped, no fabricated cleared gate, no externalization over-claim; DF-6-6-A-P2 note + the NEW DF-7-2-A human-adjudication defer filed (6 CC-3 fields); DF-6-7-A stays open (AC-PROVISIONAL).** New `dogfood/proof_run.py` (750) + `test_dogfood_proof.py` (TC-APAA-DOGFOOD-001-18..34) + `minions-dogfood-proof.md`; extended the 4.4 secret-containment suite (TC-APAA-SECURITY-001-23) + the no-web-imports coverage. Suite 1262 pass / 1 skip; mypy clean; frozen Epic-1..6 + 7.1 + 4.3/6.5 SHAPES unchanged; ≤1200 lines; no cli/HTTP/CI-job/live-LLM. Status → review. | Amelia (Dev) |
| 2026-07-02 | 0.1 | Story created (create-story) — CAPSTONE / FINAL story of Epic 7 + the whole APAA project. EXECUTES the 7.1-planned Minions dogfood: run `run_audit_detailed` over the real repo under `$X`=843 → proof artifact (AC-EXECUTE); export + persist a SIGNED, source-free evidence bundle REUSING the 4.3 `build_evidence_bundle`/`persist_evidence_bundle` + the 1.1 envelope (AC-BUNDLE); reproduce the `GitHub green · Sonar green · APAA 🔴` signature demo (AC-SIGNATURE); prove 100% reproducibility (AC-REPRODUCIBLE); carry the honest `grade: demo-heuristic-only` red-team flag (AC-DEMO-GRADE); lay the REAL findings ADJUDICATION-READY for the later human TP/FP judgment (AC-ADJUDICATION-READY). **OI1 KEYSTONE (operator epic-boundary decision): the ≥80%-precision gate STAYS PROVISIONAL — `protocol_cleared` NOT flipped, no fabricated cleared gate, no externalization over-claim; the human adjudication is a HUMAN step + a follow-up defer (AC-PROVISIONAL).** 8 ACs. REUSE-only over frozen Epic-1..6 + 7.1; NO detector/Prosecutor/partitioner/budget-core/bundle-core/registry-SHAPE edit, NO cli/HTTP/CI-job/LLM. Area APAA-DOGFOOD (TC-APAA-DOGFOOD-001-18..NN, continuing from 7.1's ..17). | Scrum Master |
