# Story 4.3: Evidence-bundle export with no source retention — [Tier B]

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **APAA sub-project story.** APAA (AI Project Assurance Audit) is a SEPARATE headless audit sub-tool
> placed at `minions_core/apaa/` (placement decision 2026-06-18). It reuses Minions infra BY IMPORT but
> ships its own `APAA-FR-*` / `APAA-NFR-*` driver namespace. Planning lives under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
> (NOT the Minions platform tracker). All CLAUDE.md rules apply (§3.2 ≤1200-line files, §3.7 headless-only,
> §3.8 12-Factor + secret masking, §3.4 evidence immutability).
>
> **APAA's evidence bundle is SEPARATE from Minions' governance evidence bundle.** Minions has its own
> `minions_core/governance/evidence.py` (decision-ledger / policy-trace / A2A-audit export for Minions
> stories). APAA's `evidence/bundle.py` is a SELF-CONTAINED, different artifact for an APAA *audit* (verdict
> + coverage ledger + findings + scope statement + integrity-lint report). **Do NOT fork, import, or couple
> to `governance/evidence.py`** — APAA "consumes-not-owns" shared *leaf* layers (the 1.1 serializer / 1.3
> store) but owns its own audit-evidence bundle. The two are unrelated by design.

## Story

As an XAgents engineer on the **operated-service path** exporting an APAA audit result for a regulated
customer,
I want to export a portable **evidence bundle** — the negative-assurance verdict + disclaimer +
point-in-time stamp, the coverage ledger (per-file depth states + deep-%), the findings (redacted
excerpts / locators only), the scope statement, and the 4.2 referential-integrity-lint report — assembled
through the single 1.1 canonical serializer into a deterministic, byte-stable bundle, **with the KEYSTONE
constraint that the bundle retains NO source** — it contains NO audited source-code bytes and NO secret
values, only **locations + redacted indicators** (mirroring the 2.5 producer-side redaction discipline +
the 2.4/2.5/2.6 containment) —
so that a regulated customer gets defensible, audit-grade evidence of what APAA examined and found **without
their source code (or any secret) ever being kept in the exported bundle or the operated-service working
state** — the THIRD story of Epic 4 (Negative-Assurance Verdict & Evidence Bundle, Tier-B), building on the
done Story 4.1 (negative-assurance verdict + persisted `CriticalSubsystemSet`) + the done Story 4.2
(referential-integrity lint), and the per-story producer guarantee that the dedicated CI-blocking
randomized-canary secret-containment property suite (Story 4.4) will mechanically enforce across a fresh
clone.

## Story Context

This is **Story 3 of Epic 4** (Negative-Assurance Verdict & Evidence Bundle, Tier-B — the "evidence you can
show a regulator" layer, PRD Journey 4). epic-4 is ALREADY `in-progress` (flipped by Story 4.1). It builds on
the fully-done Epics 1+2+3 (661 passed at the Epic-3 retro) + the done Stories 4.1 (694 passed; the
negative-assurance wrapper + the persisted computed `CriticalSubsystemSet`) and 4.2 (721 passed; the
referential-integrity lint). It is the **evidence-bundle export** story (FR29 / NFR-S3, `[Tier B]`).

**Every input the bundle assembles ALREADY ships and is frozen — this story is an ADDITIVE export that
READS the existing surfaces and assembles them into ONE portable, source-free bundle.** The honesty surface
the bundle exports already exists; the net-new is the assembly + the NO-SOURCE-RETENTION guarantee:

- **Story 4.1 (done) — `verdict/negative_assurance.py::NegativeAssuranceVerdict` + `build_negative_assurance_verdict`
  (REUSE verbatim, do NOT edit).** The frozen wrapper carries `verdict`, `exit_code`, `deep_ratio:
  Fraction`, `materiality_bar`, `scope_statement` (the structured "examined X, sampled Y, did NOT cover Z"
  triad + critical-subsystem narration), `assurance_statement`, and the fixed `DISCLAIMER` constant. The
  **point-in-time stamp** is the envelope `created_at` on the persisted wrapper (NFR-D3, excluded from the
  hashed payload). The bundle EXPORTS this wrapper (the FR29 "scope statement" + "verdict" + "disclaimer").
  The pipeline already exposes it on `AuditResult.negative_assurance` and persists it at `state/` (producer
  `apaa.verdict.negative_assurance`).
- **Story 4.2 (done) — `store/integrity.py::lint_referential_integrity` + `IntegrityReport` (REUSE
  verbatim, do NOT edit).** The PURE-core lint over the `.apaa/` tree returns a frozen `IntegrityReport`
  (sorted `IntegrityFinding`s + `consistent: bool` + per-kind counts). The bundle INCLUDES this report (so a
  consumer can see "the on-disk state this bundle was assembled from is internally consistent") — and the
  bundle export uses `consistent` as a precondition signal (the 4.2 Story Context explicitly fenced "is this
  store consistent before I export it" to THIS story as its natural consumer). REUSE the lint; do NOT re-walk
  or re-resolve references.
- **Story 1.6 (done) — `verdict/verdict_gate.py::AuditVerdict` (REUSE verbatim, do NOT edit).** The frozen
  verdict carries `verdict`, `deep_ratio: Fraction`, `deep_count`, `total_count`, `counts_by_depth`,
  `blocking_finding_count`, `ordered_findings`, `exit_code`. `ordered_findings` is the verdict-impact-ordered
  finding list (FR33) the bundle exports — each a `Recording` carrying `recording_id`, `rule_id`, `locators`,
  `advisory`, and (for the secret detector) `contained_secret: true` + the masked indicator. **These findings
  ALREADY carry locations + redacted indicators only — they NEVER carry source/secret bytes (2.5 producer-
  side redaction is structural).** The bundle exports them verbatim; it does NOT re-read source.
- **Story 2.2 (done) — `ledger/coverage_report.py::build_coverage_report` + `CoverageReport`/`DepthAggregate`
  (REUSE if it fits).** The PURE per-file depth states + per-depth counts + exact-`Fraction` deep-% — the
  FR29 "coverage ledger" surface the bundle exports. Prefer REUSING this readable surface over forking a
  parallel per-depth render. It is already proven secret-safe (TC-121: never sources file bytes).
- **Story 1.2 (done) — `ledger/coverage_ledger.py::CoverageLedger`/`CoverageLedgerEntry` + `ledger/recording.py::Recording`
  (REUSE verbatim, do NOT edit).** The fixed-enum coverage ledger (per-file depth) + the frozen recording
  (the finding payload). The bundle reads the ledger entries (file path + depth + the evidence/claim that
  justified it) + the recordings — all already source-free.
- **Story 1.1 (done) — `store/{canonical,envelope}.py` (REUSE).** The single serializer
  (`canonical.dumps_bytes` — rejects `float`, `Fraction → "num/den"`, `sort_keys=True`, `ensure_ascii=False`,
  `\n`-terminated UTF-8); the content-hashed, schema-versioned, prev-hash-chained envelope. **The bundle is
  assembled THROUGH this single serializer — NO second `json.dumps`, NO new serializer** (the AST gate
  enforces it). If the bundle is persisted, the point-in-time stamp is the envelope `created_at` (NFR-D3).
- **Story 1.3 (done) — `store/{writer,paths,reader}.py` (REUSE).** `ApaaStoreReader.read_envelope`
  (tamper-guarded read, `StoreIntegrityError`); `ApaaStorePaths` (containment-checked `is_relative_to`
  resolver); `ApaaStoreWriter.write_payload` (content-addressed, containment-checked). The bundle READS the
  persisted surfaces through the 1.3 reader OR consumes the in-memory `AuditResult` (lock the source-of-truth
  in Dev Notes); any persistence WRITE goes through the 1.3 writer (NFR-S5).
- **Story 3.3 (done) — `cost/exhaustion.py::InsufficientCoverageFloorReport` (REUSE).** The floor report the
  4.1 wrapper already folds over (exhaustion-driven vs intrinsic). The bundle exports the wrapper, which
  already carries the floor narration; do NOT re-derive it.
- **Story 1.7 / 3.x (done) — `pipeline.py::run_audit_detailed` / `AuditResult` (the in-memory source).** The
  pipeline already returns an `AuditResult(verdict, locators, floor_report, negative_assurance)`. The bundle
  builder folds over THESE in-memory records (the cleanest, most deterministic source — no re-read drift),
  with the 4.2 lint run over the persisted tree for the integrity-report section.

**The net-new deliverable of THIS story.** A scope-thin, PURE-CORE evidence-bundle export + the
no-source-retention guarantee + its e2e proof:

1. a new module **`minions_core/apaa/evidence/bundle.py`** (the architecture-locked home,
   `architecture.md:448-449` — the `evidence/` sub-package, FR29). It carries:
   - a frozen **`EvidenceBundle`** Pydantic v2 model (`frozen=True, extra="forbid"`, localized
     `EVIDENCE_BUNDLE_SCHEMA_VERSION`) that aggregates (by REFERENCE, not by re-deriving) the FR29 sections:
     - **the negative-assurance verdict** (the 4.1 `NegativeAssuranceVerdict` — verdict + scope statement +
       materiality bar + disclaimer; the exit code; the deep-% as exact `Fraction`);
     - **the coverage ledger** — per-file depth states + per-depth counts + deep-% (the 2.2 `CoverageReport`
       surface, or a structured per-entry `(file_path, depth, justification)` list reusing the 1.2 ledger);
     - **the findings** — the verdict-ordered `ordered_findings`, each REDACTED-only (locators +
       `rule_id`/`recording_id` + `advisory` + `contained_secret` indicator + masked excerpt — NEVER a source
       byte / secret value); a finding that somehow carried a raw byte would be a 2.5 producer bug, but the
       bundle MUST also be structurally incapable of emitting one (no field on the bundle holds raw source);
     - **the scope statement** (already inside the 4.1 wrapper — do NOT duplicate; expose it as the wrapper's
       `scope_statement`);
     - **the referential-integrity-lint report** (the 4.2 `IntegrityReport` — `consistent` + the sorted
       findings + per-kind counts), so the bundle is self-attesting about the internal consistency of the
       state it was assembled from;
     - **bundle metadata** — `schema_version`, the `apaa_version`, the audited `commit` (the pin), the
       `materiality_bar`, and (via the envelope, if persisted) the point-in-time `created_at` stamp. NO
       `repo_path` / absolute host path / source / secret byte (NFR-S1/S3);
   - a PURE **builder** `build_evidence_bundle(result: AuditResult, integrity_report: IntegrityReport, *, commit:
     str, apaa_version: str) -> EvidenceBundle` (lock the exact signature in Dev Notes against the real
     `AuditResult` shape) that folds the EXISTING records into the bundle — over in-memory inputs, NO source
     re-read, NO clock, NO LLM (AR8). It is honest + populated for ALL THREE verdicts;
   - a thin **export/serialize surface** — `bundle_to_canonical_payload(...)` / a persist helper — that
     serializes the bundle THROUGH the single 1.1 `canonical.dumps_bytes` (and, if persisted, wraps it in the
     1.1 envelope via the 1.3 writer at `state/` with a `apaa.evidence.bundle` producer token; the
     point-in-time stamp is the envelope `created_at`);
2. **the NO-SOURCE-RETENTION guarantee (the security keystone, FR29 / NFR-S3 — AC2/AC3):**
   - the bundle is STRUCTURALLY incapable of carrying source: every leaf is `str` (repo-relative POSIX
     locators / ids / kinds / the fixed disclaimer / the deterministic statement) / `int` / `bool` /
     `Fraction` — there is NO field that holds a file's source bytes / a raw excerpt / a secret value (mirror
     the 2.5 structural argument: the absence of a value field is the moat, not a redaction pass);
   - **the MANDATORY no-source-retention test (AI-E3-1 keystone-fixture-adequacy)** PLANTS a sentinel source
     byte AND a sentinel secret value in a fixture/cartridge repo, runs the full audit + bundle export, and
     asserts the sentinel source byte AND the sentinel secret value are ABSENT from the serialized bundle
     bytes (and from any persisted bundle artifact + the operated-service working state) — while the bundle IS
     non-empty and the secret finding IS present (redaction ≠ suppression; the 2.5 precedent). The test plants
     a DISTINCTIVE sentinel (not a generic token) so its absence is a real proof, and is demonstrated RED
     against a deliberate violation (a builder variant that copies a source excerpt into the bundle → the test
     FAILS);
   - the operated-service-path "no source retained after completion" (NFR-S3) is the broader guarantee Story
     7.x exercises end-to-end; THIS story's per-story producer discipline is: the EXPORTED bundle retains no
     source, and the bundle export itself reads no source into a retained field;
3. **NO mandatory pipeline auto-wiring REQUIRED (lock the decision, the 4.2 DN-WIRING precedent).** The bundle
   export is a standalone library over an `AuditResult` + an `IntegrityReport`, exercised by tests. The
   DEFAULT decision (DN-WIRING): the export is a library + a thin invocation surface — it does NOT add a
   mandatory pipeline persistence stage, a NEW HTTP route, or a `cli.py` subcommand in THIS story (DF-3-4-A
   `--resume` / a `--export` CLI flag stay deferred; the 7.x dogfood is the natural place a CLI export lands).
   If a thin opt-in persist into `state/` (additive, default-preserving) is genuinely warranted to make the
   bundle inspectable on disk, it is permitted as an ADDITIVE artifact (the 4.1 `_persist_negative_assurance`
   precedent) — but the testable deliverable is the BUNDLE + its no-source guarantee, not a wiring;
4. **byte-identity / determinism discipline** — the bundle is a pure deterministic function of its in-memory
   inputs (sorted collections, no clock/uuid/random in the hashed payload, no float, no set/dict
   iteration-order reliance), so the same audit result always exports to the same bundle bytes (NFR-P1);
5. **the no-over-claim inheritance** — the bundle exports the 4.1 disclaimer + assurance statement verbatim
   (it does NOT re-author verdict language), so the FR17 negative-assurance framing is preserved into the
   export (a `RELEASE_READY` bundle states "no blocking findings within the assessed scope", never "certified"
   / "correct"); a forbidden-phrase scan over the serialized bundle is the cheap regression guard.

The `EvidenceBundle` model + the `build_evidence_bundle` builder + the canonical-payload render are PURE (AR8)
and join the import-isolation gate. Any persistence WRITE is the impure shell (the 1.3 writer).

**Carry-forward from the Epic-3 retro (2026-06-27) + the 4.1/4.2 discharge (CLAUDE.md §9.1 / L1-E11).** Each
item below is an Epic-4-backlog action item this story discharges (per the L1-E11 operating model: package the
prior retro's action items as the next epic's backlog).
- **AI-E3-1 (test-infra 🟠) — keystone-fixture-adequacy practice (the marquee Epic-3 lesson; apply FIRST to
  4.3, and it is the SAME class as this story's security keystone).** The 3.4 review FAIL was a green keystone
  test that structurally COULD NOT catch its keystone bug. **For this story's no-source-retention keystone, the
  fixture MUST plant a REAL sentinel source byte AND a REAL sentinel secret value (a DISTINCTIVE token, not a
  generic word), run the FULL audit + bundle export, and prove the sentinel's ABSENCE from the serialized
  bundle (+ any persisted artifact) — AND the test MUST be demonstrated RED against a deliberate violation (a
  builder that leaks a source excerpt / secret into the bundle → the test FAILS) before it is trusted.**
  Concretely: (a) the no-source-retention assertion plants a unique `EVIDENCE_SENTINEL_<...>` source byte in a
  source file AND a `PLANTED...`-style secret value, and asserts BOTH are absent from the bundle bytes while
  the bundle is non-empty AND the secret finding is present (redaction ≠ suppression — the 2.5 precedent);
  (b) the no-over-claim assertion runs over all three verdicts and goes RED on a certification phrase; (c) the
  bundle-completeness assertion fixtures a run with ≥1 of every section (verdict + ≥1 ledger entry of multiple
  depths + ≥1 finding + the scope statement + the integrity report) so a silently-dropped section is caught,
  and goes RED if a section is omitted. Document the RED-then-green demonstration in Completion Notes.
- **AI-E3-3 (governance 🟢) — central defer register.** If this story files a NEW defer, file it append-only in
  `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (the single canonical APAA defer source), not only in
  the story file. No existing defer names THIS story as its `target_story` (DF-1-3-A targets 4.4; DF-1-3-B was
  left-open with a non-4.3 home; DF-2-3-B is CLOSED; DF-3-4-A targets 7.1), so there is no carry-forward
  closure obligation here — do NOT expand scope to chase another defer.
- **AI-E3-6 (process 🟢) — keep the three structural gates + the standing cross-env determinism suite.** Append
  the new `evidence/bundle.py` to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py` (extend, NOT
  fork); keep the single-serializer AST gate (`test_canonical_single_serializer.py`) green (any JSON the bundle
  emits goes through `store/canonical.dumps`, never a direct `json.dumps`); apply byte-stability +
  order-independence fixtures to the bundle surface; apply the 3.5 cross-env discipline (sorted, float-free,
  clock-free payload) to the export.
- **AI-E3-2 / AI-E2-1 (process 🟠) — pre-`review` mandatory-test-existence guard.** This story does NOT flip
  `status: review` until ALL mandatory test files (`tests/apaa/test_evidence_bundle.py`, the
  no-source-retention sentinel test [a dedicated `tests/apaa/test_evidence_bundle_no_source_retention.py` OR an
  asserted section within `test_evidence_bundle.py`], the round-trip if persisted, the import-isolation
  extension, the e2e assertion in `test_pipeline_signature_demo.py` if an e2e is added) EXIST and pass; the Dev
  Agent Record is filled completely (no blank placeholders). Treat the test-existence precondition as a hard
  gate on the `review` flip.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 4.3) + the architecture / PRD. Drivers: **APAA-FR-29** (an
> operator can export an evidence bundle [coverage ledger, scope statement, findings, verdict]; the
> operated-service path retains no source — the CENTRAL driver), **APAA-NFR-S3** (on the operated-service
> path, customer source is never retained after an audit completes — the no-source-retention keystone),
> **APAA-NFR-S1** (source / prompt / response / API-key bytes never appear in ledgers, evidence, logs, OTLP
> spans, traces, or any response — the bundle is "evidence", squarely in scope), **APAA-FR-28** (producer-side
> redaction — findings cite locations, never source/secret bytes; the bundle exports the already-redacted
> findings verbatim; the durable CI-blocking property suite that enforces it is Story 4.4), **APAA-FR-17 /
> NFR-A3** (the negative-assurance verdict + scope statement + disclaimer + point-in-time stamp the bundle
> exports — REUSED from 4.1, framing preserved), **APAA-FR-26 / NFR-A2** (the referential-integrity-lint
> report the bundle includes — REUSED from 4.2), **APAA-FR-33** (the verdict-impact-ordered findings the bundle
> exports — REUSED unchanged), **APAA-FR-25 / NFR-A1** (if persisted, the content-hashed, schema-versioned,
> prev-hash-chained envelope), **APAA-NFR-D2** (deterministic, zero-LLM-token — a pure fold over the EXISTING
> records, no source re-read), **APAA-NFR-D3** (the content hash covers the canonical payload ONLY — the
> point-in-time stamp is the envelope `created_at`, EXCLUDED from the hash), **APAA-NFR-P1** (byte-identical /
> order-independent bundle for the same audit result; no float; sorted collections), **APAA-NFR-S5** (any FS
> write containment-checked via the 1.3 shell), **APAA-NFR-M1** (≤1200-line files), **APAA-NFR-M2** (frozen,
> schema-versioned, additive-only contracts), **AR4** (no `float`; ratios are exact `Fraction` REUSED from the
> verdict; single canonical serializer; no clock/uuid/random/iteration-order — content-derived, AR11), **AR8**
> (pure/impure separation — the bundle model + builder + render are PURE; the WRITE is the impure shell),
> **AR10** (typed failure — a localized `EvidenceBundleError`, never an uncaught raise).
>
> **SCOPE FENCE — Tier-B, single-purpose.** This story delivers ONLY: (1) the evidence-bundle EXPORT — a new
> `evidence/bundle.py` with a PURE builder + a frozen `EvidenceBundle` surface that aggregates (by REFERENCE)
> the FR29 sections (the 4.1 negative-assurance verdict + scope statement + disclaimer + stamp, the coverage
> ledger + deep-%, the verdict-ordered redacted findings, the 4.2 integrity-lint report, bundle metadata) and
> serializes them through the single 1.1 canonical serializer; (2) the NO-SOURCE-RETENTION guarantee — the
> bundle is structurally incapable of holding source/secret bytes (only locations + redacted indicators), with
> the MANDATORY sentinel-planted no-source-retention test (AI-E3-1 RED-then-green); (3) the bundle-completeness
> proof (every FR29 section present); (4) the no-over-claim inheritance (the 4.1 framing preserved into the
> export); (5) the import-isolation + byte-stability + order-independence + secret-safe discipline. It does NOT
> build, and MUST NOT pull forward: the **CI-blocking randomized-canary secret-containment property suite**
> over `{ledger, evidence, logs, traces, verdict envelope}` (FR28 enforcement / NFR-S1 / AR9 — **Story 4.4**,
> `tests/security/test_apaa_secret_containment.py` — THIS story ships its OWN per-story containment test, NOT
> the durable CI property suite); ANY change to the **4.1 wrapper / 4.2 lint / 1.6 verdict gate / 1.2 ledger /
> 2.2 coverage report / 1.1 serializer / 1.3 store** frozen contracts (all reused verbatim); a **second
> serializer / a coupling to `minions_core/governance/evidence.py`** (APAA's bundle is self-contained); the
> **adversarial Prosecutor** (FR19 — Epic 6); the **HITL escalation / decision record** (FR23/FR24 — Epic 6);
> the **operated-service-path end-to-end no-retention proof on a real customer repo** (Story 7.x dogfood — THIS
> story proves the EXPORTED bundle is source-free, not the full operated-service retention lifecycle). It does
> NOT add a NEW HTTP route / FastAPI surface / UI (§3.7), and does NOT add a mandatory pipeline stage or a
> `cli.py` subcommand (DN-WIRING — a `--export` CLI is fenced to 7.x / DF). Export the bundle, prove no source
> is retained, prove every section is present, then stop.

**AC1 — A completed audit exports an evidence bundle carrying the verdict, coverage ledger, findings, scope statement, and integrity report (FR29 — the bundle-completeness driver)**
**Given** a completed audit (an `AuditResult` from `run_audit_detailed` — verdict + `ordered_findings` +
`negative_assurance` wrapper + the persisted `.apaa/` tree) and the 4.2 `IntegrityReport` for that tree
**When** the PURE `build_evidence_bundle(...)` folds them
**Then** `evidence/bundle.py` produces a frozen `EvidenceBundle` carrying: (a) the **negative-assurance
verdict** (the 4.1 `NegativeAssuranceVerdict` — `verdict`, `exit_code`, `deep_ratio: Fraction`,
`materiality_bar`, `scope_statement`, `assurance_statement`, `disclaimer`); (b) the **coverage ledger** —
every file's depth state + the per-depth counts + the exact-`Fraction` deep-% (REUSED from the 2.2
`CoverageReport` / the 1.2 ledger); (c) the **findings** — the verdict-impact-ordered `ordered_findings`
(FR33 ordering preserved), each carrying locators + `rule_id`/`recording_id` + `advisory` +
`contained_secret` indicator + masked excerpt ONLY; (d) the **scope statement** (the 4.1 wrapper's
`scope_statement` — examined / sampled / NOT-covered + critical narration); (e) the **referential-integrity
report** (the 4.2 `IntegrityReport` — `consistent` + sorted findings + per-kind counts); (f) **bundle
metadata** — `schema_version`, `apaa_version`, the audited `commit`, the `materiality_bar`
**And** the bundle is honest + populated for ALL THREE verdicts (`RELEASE_READY` / `NOT_READY_FOR_RELEASE` /
`INSUFFICIENT_COVERAGE`); a bundle-completeness test runs over a fixture with ≥1 of EVERY section present
(verdict + ≥1 ledger entry across multiple depths + ≥1 finding + the scope statement + the integrity report)
and is demonstrated RED if any section is silently dropped from the bundle (AI-E3-1).

**AC2 — The exported bundle retains NO audited source byte and NO secret value (the security keystone, FR29, NFR-S3, NFR-S1)**
**Given** a fixture / cartridge repo with a **planted sentinel source byte** (a distinctive
`EVIDENCE_SENTINEL_<token>` string in a source file's body) AND a **planted sentinel secret value** (a
distinctive `PLANTED...`-style hardcoded secret), audited end-to-end with the bundle exported
**When** the `EvidenceBundle` is serialized (via the single 1.1 `canonical.dumps_bytes`) and (if persisted)
written to disk
**Then** the sentinel source byte AND the sentinel secret value are **ABSENT** from the serialized bundle
bytes AND from any persisted bundle artifact AND from the operated-service working state the export touched
(searched as UTF-8 bytes; the distinctive `EVIDENCE_SENTINEL`/`PLANTED` token is absent in any encoding the
export wrote) — the bundle carries only locations + redacted indicators (mirroring 2.5)
**And** redaction is NOT silent suppression: the bundle IS non-empty, the verdict + scope statement are
present, AND the secret finding IS present (with `contained_secret: true` + the masked indicator + the correct
locator — so a consumer sees a secret was found WITHOUT the secret leaking)
**And** the MANDATORY no-source-retention test is demonstrated RED against a deliberate violation (a builder
variant that copies a source excerpt / the secret value into a bundle field → the test FAILS), then green on
the real source-free builder (AI-E3-1 keystone-fixture-adequacy — the planted sentinel proves the absence is
real, not vacuous). **The dedicated CI-blocking randomized-canary property suite over
`{ledger, evidence, logs, traces, verdict envelope}` is Story 4.4 — this AC is the per-story producer proof,
not that durable suite.**

**AC3 — The bundle is structurally incapable of holding source/secret bytes (the moat, NFR-S1/S3, the 2.5 structural precedent)**
**Given** the `EvidenceBundle` model (+ its nested section models) definition
**When** its fields are inspected
**Then** NO field holds a file's source bytes / a raw source excerpt / a secret value — every leaf is a
repo-relative POSIX locator / id / closed-enum kind / a redacted-or-masked indicator / a deterministic
statement / a `Fraction` / `int` / `bool` (the 2.5 structural argument: the ABSENCE of a value field is the
moat, not a redaction pass at serialization time) — so even a future caller cannot route a source byte into
the bundle
**And** this is asserted by a test that inspects the model schema / fields for any field that could carry raw
source (and confirms the findings the bundle exports come from the already-redacted 2.5 `Recording` surface,
which has no value field) — a non-ASCII café/Cyrillic file path in a locator round-trips intact (AI-E1-1).

**AC4 — The bundle preserves the 4.1 negative-assurance framing — NO over-claim is introduced by the export (FR17, the no-over-claim inheritance)**
**Given** the bundle exported for EACH of the three verdicts
**When** the serialized bundle (the disclaimer + assurance statement + any rendered text) is inspected
**Then** the language is the REUSED 4.1 scope-bounded negative assurance verbatim — a `RELEASE_READY` bundle
states "no blocking findings within the assessed scope" (NOT "certified" / "correct" / "proven defect-free" /
"passed"); the export introduces NO new verdict language of its own (it exports the 4.1 `disclaimer` +
`assurance_statement` constants/fields, it does not re-author them) — asserted by a forbidden-phrase scan over
the serialized bundle (the 4.1 AC2 set, e.g. `{"certif", "is correct", "proven", "guarantee", "defect-free",
"bug-free", "passed"}`, case-insensitive)
**And** this is demonstrated RED if the bundle were to inject a certification phrase, then green (AI-E3-1) —
the forbidden-phrase set is the same one 4.1 locked.

**AC5 — The bundle is frozen, no-`float`, deterministic, secret-safe, schema-versioned; serializes via the single 1.1 serializer; persists via the EXISTING shell if persisted (NFR-M2, NFR-A1, AR4, NFR-S1, NFR-S5, AR11, FR25)**
**Given** a built evidence bundle
**When** it is inspected / serialized / (optionally) persisted
**Then** it is a frozen Pydantic v2 model (`frozen=True, extra="forbid"`, localized
`EVIDENCE_BUNDLE_SCHEMA_VERSION`) with ALL leaves `str` / `int` / `bool` / `Fraction` (rendered `"num/den"`
by the 1.1 serializer) — **NO `float` anywhere** (the canonical serializer rejects it), NO volatile
`run_id`/`created_at` in the hashed payload (NFR-D3 — the stamp lives in the envelope if persisted), NO
absolute host path / `repo_path` / source / secret byte (NFR-S1/S3), verified by an AI-E1-1-style assertion
that no source / secret / absolute-host-path byte appears in the serialized bundle (and a non-ASCII
café/Cyrillic path round-trips intact)
**And** the bundle is serialized THROUGH the single 1.1 `canonical.dumps_bytes` (no second `json.dumps`; the
AST gate enforces it); its collections (findings, ledger entries, integrity findings) are SORTED / order-fixed
deterministically so the bundle is byte-stable + order-independent
**And** IF the bundle is persisted (optional, additive — DN-WIRING), the persist goes through
`ApaaStoreWriter.write_payload("state", payload, schema_version=..., producer="apaa.evidence.bundle")` — bytes
are `EnvelopeWriter.build(...)` → `store/canonical.dumps_bytes` (single serializer), filename content-addressed
`<content_hash>.json` (AR11), the `ApaaStorePaths` `is_relative_to` containment check guards the path (NFR-S5),
the envelope `prev_hash` chains (NFR-A1), the point-in-time stamp is the envelope `created_at` (NFR-D3, never
hashed), and re-reading via `store/reader.py` reconstructs an EQUAL bundle + round-trips byte-identically
(NFR-P1).

**AC6 — The same audit result exports a byte-identical, order-independent bundle (NFR-P1, the determinism keystone)**
**Given** the SAME `AuditResult` + `IntegrityReport` exported twice, and the same inputs presented with the
findings / ledger entries / integrity findings in different orderings
**When** the bundle is built + serialized on each path
**Then** the bundle's canonical payload bytes are BYTE-IDENTICAL across the two builds and across input
orderings (the builder sorts/fixes order deterministically — no set/dict iteration-order reliance, no clock,
no float)
**And** this is demonstrated RED if the bundle is made to depend on input order (e.g. emit findings in
arrival order instead of the verdict-impact order / unsorted) → the byte-identity assertion FAILS, then green
(AI-E3-1) — and a resumed-run audit result (the 3.4 path) exports the same bundle as an uninterrupted run of
equivalent budget (the 4.1 wrapper it reads is already resume-byte-identical).

**AC7 — The new pure logic is PURE, frozen-contract, deterministic, typed-error, import-isolated; the whole suite green; mypy clean; ≤1200 lines (NFR-D2, NFR-P1, AR8, AR10, M1, M2)**
**Given** the new `EvidenceBundle` model (+ nested section models) + the PURE `build_evidence_bundle` builder
(+ any export/serialize helper) in `minions_core/apaa/evidence/bundle.py`
**When** they are imported and exercised in unit tests
**Then** the builder + the model build + the render perform NO source re-read, NO filesystem I/O in the PURE
core, NO clock read (`datetime.now`/`time.time` — the stamp is the envelope `created_at`, set by the impure
writer IF persisted), NO `uuid4`/`os.getpid()`/`random`, NO LLM/network call, NO dict/`set`-iteration-order
reliance — they are PURE functions over the in-memory `AuditResult` + `IntegrityReport` (the ONLY I/O is the
optional impure persist through the 1.3 writer)
**And** the new models are frozen Pydantic v2 (`frozen=True, extra="forbid"`, localized `schema_version` — the
1.1/1.2/1.6/4.1/4.2 precedent); NO `float` anywhere (ratios are exact `Fraction`s REUSED from the verdict;
counts are `int`; flags are `bool`; locators/kinds/details/statements are `str`); any JSON rendering routes
through `store/canonical.dumps` (single 1.1 serializer — no second `json.dumps`); the bundle's collections are
SORTED / order-fixed so the bundle is byte-stable + order-independent
**And** a malformed input (a non-`AuditResult`, a non-`IntegrityReport`, a non-`str` `commit`/`apaa_version`,
or an `AuditResult` missing the 4.1 `negative_assurance` wrapper) raises a typed `EvidenceBundleError` (a
`ValueError` subclass mirroring `NegativeAssuranceError` / `IntegrityLintError` / `ExhaustionError`) — never a
silent coerce / bare `except: pass` / `print()` in library code (AR10); any export-stage failure in a pipeline
context degrades to the existing typed `PipelineError` (exit `1`), never an uncaught traceback
**And** the new module is appended to `_MODULES_UNDER_GUARD` in `tests/apaa/test_no_web_imports.py` (extend, do
NOT fork) and importing it does NOT transitively import `fastapi`/`uvicorn`/`starlette` or any LLM/api module
(assert absence from `sys.modules`); it does NOT import `minions_core.governance.evidence` (the Minions
governance bundle — APAA's is self-contained)
**And** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` passes (including the
new `tests/apaa/test_evidence_bundle.py`: AC1 the section completeness over all three verdicts [demonstrated
RED]; AC2 the MANDATORY no-source-retention sentinel test [planted source byte + secret value ABSENT while the
bundle is non-empty + the secret finding present; demonstrated RED]; AC3 the structural no-source-field
assertion [+ non-ASCII path round-trip]; AC4 the no-over-claim forbidden-phrase scan [demonstrated RED]; AC5
frozen no-`float` secret-safe [no abs-path/source/secret byte] + single-serializer + the round-trip if
persisted; AC6 byte-identity + order-independence [demonstrated RED]; AC7 purity [AST scan] / frozen /
typed-error [malformed inputs] / FastAPI-free + no-governance-evidence import); `mypy` is clean on the new +
edited modules; the new source file is ≤1200 lines (NFR-M1) and cites its
`APAA-FR-29`/`APAA-NFR-S3`/`APAA-NFR-S1`/`AR*` drivers in the module docstring. **Test area `APAA-EVIDENCE`**
(`TC-APAA-EVIDENCE-001-NN` — the natural area for `evidence/`; confirm/lock the next free index in the
docstring, distinct from the existing test areas) plus any e2e additions under `APAA-PIPELINE`. The 4.1
wrapper / 4.2 lint / 1.6 gate / 1.2 ledger / 2.2 coverage report / 1.1 serializer / 1.3 store contracts are
UNCHANGED (verify NO working-tree diff to those frozen surfaces). The mandatory test files MUST exist + pass
BEFORE the story flips to `status: review` (AI-E3-2 / AI-E2-1).

## Tasks / Subtasks

- [x] **Task 0 — Verify the existing reuse surface + LOCK the bundle section sources against the REAL records** (AC: 1, 2, 3, 5)
  - [x] Re-read `verdict/negative_assurance.py` — confirm `NegativeAssuranceVerdict` fields (`verdict`,
        `exit_code`, `deep_ratio: Fraction`, `materiality_bar`, `scope_statement`, `assurance_statement`,
        `disclaimer`) + `DISCLAIMER`. **Lock:** the bundle EXPORTS this wrapper (the FR29 verdict + scope
        statement + disclaimer); verify NO working-tree diff at the end.
  - [x] Re-read `store/integrity.py` — confirm `lint_referential_integrity(reader) -> IntegrityReport` +
        `IntegrityReport` fields (`findings`, `consistent`, per-kind counts). **The bundle INCLUDES this report;
        REUSE the lint, do NOT re-walk references.**
  - [x] Re-read `verdict/verdict_gate.py::AuditVerdict` (`ordered_findings`, `counts_by_depth`, `deep_ratio`,
        `exit_code`) + `ledger/recording.py::Recording` (`recording_id`, `rule_id`, `locators`, `advisory`,
        `contained_secret` indicator — confirm there is NO raw-value/source field) + `ledger/coverage_report.py`
        (the 2.2 `CoverageReport` per-depth surface) + `ledger/coverage_ledger.py` (`CoverageLedgerEntry`
        file_path/depth). **Lock the reuse decision:** export findings + the coverage ledger from these
        already-redacted surfaces; confirm NONE carries source bytes (the structural moat).
  - [x] Re-read `pipeline.py::AuditResult` (`verdict`, `locators`, `floor_report`, `negative_assurance`) +
        the producer tokens (`pipeline.py:172-199`) + `run_audit_detailed`. **Lock the bundle's source-of-truth:**
        fold over the in-memory `AuditResult` (deterministic, no re-read drift) + run the 4.2 lint over the
        persisted tree for the integrity section. Re-read `store/{canonical,envelope,writer,paths,reader}.py` —
        confirm `created_at` is the point-in-time stamp + excluded from the content hash (NFR-D3).
  - [x] Confirm the bundle is SEPARATE from `minions_core/governance/evidence.py` (do NOT import / couple).
- [x] **Task 1 — The frozen `EvidenceBundle` model (+ nested section models) + the typed `EvidenceBundleError`** (AC: 1, 3, 5, 7)
  - [x] In NEW `minions_core/apaa/evidence/bundle.py`: define a frozen `EvidenceBundle` (`frozen=True,
        extra="forbid"`, localized `EVIDENCE_BUNDLE_SCHEMA_VERSION`) aggregating BY REFERENCE: the 4.1
        `NegativeAssuranceVerdict` (verdict + scope statement + disclaimer + materiality + deep-%); a coverage
        section (per-file `(file_path, depth, justification?)` + per-depth counts + deep-% `Fraction`, REUSING
        the 2.2 surface); a findings section (the verdict-ordered `Recording`s — locators + ids + advisory +
        `contained_secret` indicator + masked excerpt ONLY); the 4.2 `IntegrityReport`; metadata
        (`schema_version`, `apaa_version`, `commit`, `materiality_bar`). **NO field that can hold a source byte /
        raw excerpt / secret value (AC3 structural moat). NO `repo_path` / abs-path. NO float.** Reuse the
        `Fraction → "num/den"` canonical encoding + a `to_canonical_payload` re-installing live `Fraction`
        leaves (the 1.6/3.3/4.1 precedent).
  - [x] Define a localized `EvidenceBundleError` (`ValueError` subclass, mirroring `NegativeAssuranceError` /
        `IntegrityLintError`). Cite `APAA-FR-29`/`APAA-NFR-S3`/`APAA-NFR-S1`/`AR4`/`AR8`/`AR10` + the locked
        test area `APAA-EVIDENCE` in the module docstring; document the section sources + the no-source-retention
        argument + the separateness from the Minions governance bundle.
- [x] **Task 2 — The PURE `build_evidence_bundle` builder + the canonical-payload/export surface** (AC: 1, 2, 4, 6, 7)
  - [x] PURE `build_evidence_bundle(result: AuditResult, integrity_report: IntegrityReport, *, commit: str,
        apaa_version: str) -> EvidenceBundle` — folds the EXISTING records: the 4.1 wrapper from
        `result.negative_assurance` (raise `EvidenceBundleError` if absent), the coverage section from the
        verdict/ledger surface, the verdict-ordered redacted findings, the 4.2 report verbatim, the metadata.
        Honest + populated for ALL THREE verdicts; the disclaimer + assurance statement are REUSED verbatim from
        4.1 (no re-authored verdict language — AC4). Typed `EvidenceBundleError` on a malformed/missing-wrapper
        input (AR10). NO source re-read, NO clock, NO uuid/random, NO float, NO set/dict-order reliance — sort /
        order-fix every collection (AC6).
  - [x] Add `bundle_to_canonical_payload(...)` (re-install the live `Fraction` leaves) routed through the single
        1.1 `canonical.dumps_bytes` (no second `json.dumps`).
- [x] **Task 3 — (Optional, additive, DN-WIRING) persist helper** (AC: 5) — only if it makes the bundle inspectable on disk cheaply
  - [x] IF persisted: a thin `_persist_evidence_bundle` → `write_payload("state", ...,
        producer="apaa.evidence.bundle")` via the EXISTING writer (content-addressed, containment-checked,
        single serializer; the point-in-time stamp is the envelope `created_at`). PURELY ADDITIVE (the 4.1
        `_persist_negative_assurance` precedent) — existing artifact bytes UNCHANGED. NO mandatory pipeline stage
        / NO new HTTP route / NO `cli.py` change. If a persist is not warranted, the testable deliverable is the
        in-memory bundle + its serialized bytes (lock the decision in the Dev Agent Record).
- [x] **Task 4 — Tests (AI-E3-1: the no-source-retention keystone PLANTS a real sentinel + demonstrates RED before trusting)** (AC: 1, 2, 3, 4, 5, 6, 7)
  - [x] `tests/apaa/test_evidence_bundle.py` (`APAA-EVIDENCE`, `TC-APAA-EVIDENCE-001-NN` — lock the next free
        index) — AC1 section completeness over all three verdicts [demonstrated RED if a section is dropped]; AC3
        the structural no-source-field assertion [+ non-ASCII path round-trip]; AC4 the no-over-claim
        forbidden-phrase scan [demonstrated RED]; AC5 frozen no-`float` secret-safe + single-serializer; AC6
        byte-identity + order-independence [demonstrated RED]; AC7 purity AST scan / frozen / typed-error
        (malformed / missing-wrapper inputs) / FastAPI-free + no-governance-evidence import.
  - [x] **The MANDATORY no-source-retention test** (AC2 — a dedicated
        `tests/apaa/test_evidence_bundle_no_source_retention.py` OR an asserted section here): PLANT a
        DISTINCTIVE sentinel source byte (`EVIDENCE_SENTINEL_<token>` in a source file body) AND a planted
        secret value (the 2.5 `PLANTED...` precedent, via the `hardcoded_secret` cartridge or a fixture); run the
        FULL `run_audit_detailed` + export the bundle (+ persist if persisted); assert BOTH sentinels are ABSENT
        from the serialized bundle bytes (+ any persisted bundle artifact + the bundle-touched working state, as
        UTF-8) WHILE the bundle is non-empty AND the secret finding is present (`contained_secret` + masked +
        locator). **Demonstrate it RED against a deliberate violation** (a builder variant that copies a source
        excerpt / the secret value into a bundle field → the test FAILS), then green. Document the RED-then-green
        in Completion Notes. (Mirror `tests/apaa/test_secret_containment.py` — the 2.5 producer proof — for the
        sentinel + `_all_apaa_bytes` pattern; this is the per-story producer proof, NOT the 4.4 CI property suite.)
  - [x] Round-trip test (IF persisted): `test_evidence_bundle_roundtrip.py` (write_payload→reader: equal bundle
        + byte-identical; content-addressed filename; envelope `prev_hash` chained; `created_at` present in the
        envelope but absent from the hashed payload; no abs-path/source byte).
  - [x] (Optional e2e) extend `tests/apaa/test_pipeline_signature_demo.py` (`APAA-PIPELINE`) — e2e: the bundle is
        present + correct on `RELEASE_READY` / `NOT_READY_FOR_RELEASE` / `INSUFFICIENT_COVERAGE` runs; the
        no-source-retention property holds e2e. (If the AC2 sentinel test over a real `run_audit` tree already
        covers this, the e2e extension may be redundant — lock the decision.)
- [x] **Task 5 — Extend the import-isolation gate** (AC: 7)
  - [x] Append `minions_core.apaa.evidence.bundle` to `_MODULES_UNDER_GUARD` in
        `tests/apaa/test_no_web_imports.py` (extend, NOT fork); confirm it stays green (no
        `fastapi`/`uvicorn`/`starlette`/LLM/api transitive import AND no `minions_core.governance.evidence`
        import). Confirm the single-serializer AST gate (`test_canonical_single_serializer.py`) stays green (no
        direct `json.dumps` in the new module).
- [x] **Task 6 — Run + mypy + the pre-`review` test-existence precondition** (AC: all)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → all pass.
  - [x] `mypy` clean on the new + edited modules (`python run_mypy_per_file.py` or scoped).
  - [x] **AI-E3-3:** if a NEW defer is filed, file it append-only in
        `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (no existing defer targets THIS story; no closure
        obligation here).
  - [x] **AI-E3-2 / AI-E2-1 GATE:** all mandatory test files exist + pass BEFORE the `review` flip; Dev Agent
        Record filled completely (no blank placeholders); document the AI-E3-1 RED-then-green keystone-fixture
        demonstrations (the no-source-retention sentinel; the bundle-completeness; the no-over-claim). Verify NO
        working-tree diff to the frozen surfaces (`verdict/negative_assurance.py`, `store/integrity.py`,
        `verdict/verdict_gate.py`, `ledger/{coverage_ledger,coverage_report,recording}.py`, the 1.1 store spine).

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **Every section already ships — this is an ADDITIVE export, NOT a new producer of audit data (the scope
  crux).** The 4.1 wrapper produces the verdict + scope statement + disclaimer; the 4.2 lint produces the
  integrity report; the 1.6 gate produces the ordered findings; the 1.2/2.2 surface produces the coverage
  ledger. **Do NOT re-implement, re-derive, or fork any of them.** The net-new is the FR29 assembly: a thin
  additive bundle that READS the existing records and serializes them through the single 1.1 serializer. Resist
  building anything the 4.1/4.2/1.6/2.2 code already does.
- **NO source retention is the security keystone (FR29 / NFR-S3 — the whole point of the story).** The
  exported bundle must contain NO audited source-code byte and NO secret value — only locations + redacted
  indicators. This mirrors the 2.5 producer-side redaction discipline + the 2.4/2.5/2.6 containment: the
  findings the bundle exports ALREADY carry no source (2.5 made the `Recording` structurally value-free), and
  the bundle adds no field that could carry source. **The moat is structural (the absence of a value field),
  not a redaction pass at serialization time** — the same argument 2.5 used (no value field on
  `Recording`/`Locator`). The MANDATORY no-source-retention test (AC2) plants a sentinel source byte AND a
  sentinel secret and proves both ABSENT from the serialized bundle while the bundle is non-empty + the secret
  finding present (redaction ≠ suppression). Plant a DISTINCTIVE sentinel (so its absence is a real proof, not
  a vacuous one) and demonstrate the test RED against a leaking builder before trusting it (AI-E3-1).
- **APAA's bundle is SEPARATE from Minions' `governance/evidence.py` (the no-coupling rule).** Minions has its
  own governance evidence bundle (decision ledger / policy traces / A2A audit). APAA's evidence bundle is a
  DIFFERENT artifact for an APAA *audit*. Do NOT import, fork, or couple to it. APAA consumes-not-owns shared
  LEAF layers (the 1.1 serializer / 1.3 store / cost guardrails by import per AR7) but owns its own
  audit-evidence bundle. The import-isolation gate asserts the new module does not import
  `minions_core.governance.evidence`.
- **The point-in-time stamp is the envelope `created_at`, NOT a hashed payload field (NFR-D3, the determinism
  landmine — IF persisted).** Same as 4.1: putting a wall-clock timestamp INSIDE the canonical payload would
  make the content hash non-reproducible (the AR4 byte-diff landmine; `datetime.now` is forbidden in the write
  path). If the bundle is persisted, the stamp is the 1.1 envelope's `created_at` (already excluded from the
  content hash). The pure builder NEVER reads a clock; the impure writer sets `created_at`. The exported
  bundle's "as-of" stamp is inherited from the 4.1 wrapper's persisted envelope `created_at` (the audit's
  point-in-time) — do NOT invent a second clock read.
- **Reuse the EXISTING `deep_ratio` + counts + wrapper + lint report — do NOT re-derive (AR4 / §3.3).** The
  deep-% is `AuditVerdict.deep_ratio` / the 4.1 wrapper's `deep_ratio` (exact `Fraction`); the per-depth counts
  are `AuditVerdict.counts_by_depth` / the 2.2 surface; the verdict language is the 4.1 `disclaimer` +
  `assurance_statement`; the integrity report is the 4.2 `IntegrityReport`. The bundle REUSES all by reading
  them — no parallel computation, no re-declared thresholds, no re-authored disclaimer.
- **No floats — ever (AR4/NFR-P1).** All bundle leaves are `str`/`int`/`bool`/`Fraction` (rendered `"num/den"`).
  The 1.1 serializer rejects `float` as the determinism backstop. Ratios are exact `Fraction`s reused from the
  verdict/wrapper.
- **Pure/impure separation (master rule, AR8).** The bundle model + `build_evidence_bundle` + the
  canonical-payload render are PURE — over the in-memory `AuditResult` + `IntegrityReport`; they never open a
  source file, read a clock, or call an LLM. The IMPURE shell is the OPTIONAL persistence WRITE (the 1.3 writer
  + the envelope `created_at`). The 4.2 lint's enumerate-and-read is the impure shell that produces the
  `IntegrityReport` the builder takes as an input — run it at the call site, not inside the pure builder.
- **Determinism: sorted/order-fixed collections, no clock/uuid/random (NFR-P1, the 3.5 cross-env discipline).**
  The bundle is a pure deterministic function of its inputs. The findings preserve the verdict-impact order
  (FR33 — already ordered by the gate); the ledger entries + integrity findings are sorted (the integrity
  report is already sorted by 4.2). Same audit result → byte-identical bundle. No clock, no uuid, no random, no
  set/dict iteration-order reliance.
- **The 4.4 work is OUT of scope (the primary downstream fence).** The CI-blocking randomized-canary
  secret-containment property suite over `{ledger, evidence, logs, traces, verdict envelope}`
  (`tests/security/test_apaa_secret_containment.py`, FR28 enforcement / NFR-S1 / AR9) is **Story 4.4** — this
  story ships its OWN per-story no-source-retention test (a planted sentinel proof, the 2.5 precedent), NOT the
  durable CI property suite. If tempted to build a randomized-canary harness / a `tests/security/` CI-blocking
  suite — STOP, that is 4.4. (The 4.4 suite will EXTEND coverage to the evidence bundle this story produces —
  so a clean, structurally-source-free bundle here makes 4.4's job a verification, not a fix.)
- **The operated-service-path end-to-end no-retention lifecycle is fenced to Story 7.x (the dogfood).** NFR-S3
  ("customer source is never retained AFTER an audit completes") is the broader operated-service lifecycle
  guarantee the 7.x dogfood exercises end-to-end on a real repo. THIS story's per-story producer discipline is
  narrower + testable: the EXPORTED bundle retains no source, and the export reads no source into a retained
  field. Do NOT attempt to prove the full operated-service teardown here.
- **Error/degradation → typed, never crash (AR10).** A malformed input (a non-`AuditResult`, a
  non-`IntegrityReport`, a non-`str` `commit`/`apaa_version`, or an `AuditResult` whose `negative_assurance` is
  `None`) → a typed `EvidenceBundleError` (a `ValueError` subclass localized to the module, mirroring
  `NegativeAssuranceError`/`IntegrityLintError`/`ExhaustionError`) — never a silent coerce / bare `except: pass`
  / `print()` in library code. Any export-stage failure in a pipeline context degrades to the existing typed
  `PipelineError` (exit `1`), never an uncaught traceback.

### Project Structure Notes

- **NEW module:** `minions_core/apaa/evidence/bundle.py` (the architecture-locked home,
  `architecture.md:448-449` — the `evidence/` sub-package, FR29). The `evidence/` package may need an
  `__init__.py` if it does not yet exist (it is a new sub-package). PURE — joins `_MODULES_UNDER_GUARD`.
- **UPDATE (scope-fenced, OPTIONAL):** `minions_core/apaa/pipeline.py` — ONLY if a thin additive
  `_persist_evidence_bundle` is warranted (the 4.1 `_persist_negative_assurance` precedent at `pipeline.py:611`;
  the producer-token block at `pipeline.py:172-199`). Verify `pipeline.py` stays ≤1200 lines (it was ~1006 at
  4.1; budget any addition — prefer in-place additive functions). If no persist, `pipeline.py` is UNCHANGED.
- **REUSE verbatim (verify NO working-tree diff):** `verdict/negative_assurance.py`, `store/integrity.py`,
  `verdict/verdict_gate.py`, `ledger/{coverage_ledger,coverage_report,recording}.py`,
  `store/{canonical,envelope,writer,paths,reader}.py`, `models.py::AuditRequest`/`AuditResult`,
  `cost/exhaustion.py`. Do NOT import `minions_core/governance/evidence.py`.
- **NEW tests:** `tests/apaa/test_evidence_bundle.py` (`APAA-EVIDENCE` area, `TC-APAA-EVIDENCE-001-NN`), the
  MANDATORY `tests/apaa/test_evidence_bundle_no_source_retention.py` (or an asserted AC2 section in the main
  file), `tests/apaa/test_evidence_bundle_roundtrip.py` (IF persisted); extend
  `tests/apaa/test_no_web_imports.py` and (optionally) `tests/apaa/test_pipeline_signature_demo.py`
  (`APAA-PIPELINE`). Confirm the next free `TC-APAA-EVIDENCE-001-NN` index (this is the first test file in the
  `APAA-EVIDENCE` area — lock the area + starting index in the new module docstring). Reuse the 2.5
  `tests/apaa/test_secret_containment.py` sentinel + `_all_apaa_bytes` pattern + the `hardcoded_secret`
  cartridge for the no-source-retention proof.
- **No CLI change** (DF-3-4-A `--resume` / a `--export` flag stay deferred — out of scope). No new HTTP route /
  FastAPI surface / UI (§3.7).

### Testing Standards (APAA)

- Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` (the `PYTHONIOENCODING`
  prefix avoids the cp1252 emoji crash on Windows — project memory). `mypy` via `python run_mypy_per_file.py`
  or scoped to the new + edited modules.
- **Verification ID format:** `TC-APAA-EVIDENCE-001-NN` (the new area for `evidence/`; confirm/lock the next
  free index in the module docstring). E2e additions continue the `APAA-PIPELINE` area.
- **AI-E3-1 keystone-fixture-adequacy (the marquee Epic-3 lesson, applied to BOTH the security keystone and the
  completeness keystone):** every keystone fixture contains ≥1 element of every class its assertion preserves,
  and is demonstrated RED against a deliberate violation before it is trusted. The no-source-retention test
  plants a REAL distinctive sentinel (source byte + secret value) and proves its absence — never a vacuous
  "absence of a word that was never present" assertion.
- **AI-E1-1 non-ASCII discipline:** a café/Cyrillic file path in a locator round-trips intact (explicit UTF-8);
  the standing cross-env determinism suite (3.5) discipline (sorted, float-free, clock-free) applies to the
  bundle surface.
- **The three structural gates stay green:** import-isolation (`test_no_web_imports.py`, extend
  `_MODULES_UNDER_GUARD`), single-serializer AST gate (`test_canonical_single_serializer.py`), file-size
  (≤1200 lines).

### References

- Epic: `_bmad-output/design-artifacts/ArgusAgent/epics.md` — Epic 4 / Story 4.3 (FR29; NFRs S1/S3/A2/A3).
- PRD: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` — FR29 (evidence-bundle export, no source retention),
  FR28 (producer redaction), NFR-S1 (no source/secret bytes in evidence), NFR-S3 (no source retained on the
  operated-service path), NFR-D2/D3/P1/A1/M1/M2.
- Architecture: `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — `evidence/bundle.py` (the FR29 home,
  package tree §Project Structure), the Security/Containment patterns (producer-side redaction; all writes via
  containment), the Reuse/Import patterns (leaf modules only; no `api.*`), AR4/AR8/AR10/AR11.
- Prior stories: 4.1 (`stories/4-1-negative-assurance-verdict-semantics.md` — the wrapper the bundle exports),
  4.2 (`stories/4-2-referential-integrity-lint-of-on-disk-state.md` — the lint report the bundle includes),
  2.5 (`stories/2-5-hardcoded-secret-detector-producer-side-redaction.md` — the producer-side redaction +
  sentinel-containment test precedent), 2.2 (the coverage-report surface), 1.1/1.2/1.3/1.6 (the spine).
- Source: `minions_core/apaa/verdict/negative_assurance.py`, `minions_core/apaa/store/integrity.py`,
  `minions_core/apaa/verdict/verdict_gate.py`, `minions_core/apaa/ledger/{coverage_ledger,coverage_report,recording}.py`,
  `minions_core/apaa/pipeline.py` (`AuditResult`, producer tokens, `_persist_negative_assurance`),
  `minions_core/apaa/store/{canonical,envelope,writer,paths,reader}.py`.
- Test precedent: `tests/apaa/test_secret_containment.py` (the 2.5 sentinel + `_all_apaa_bytes` no-leak
  pattern), `tests/apaa/test_no_web_imports.py` (`_MODULES_UNDER_GUARD`).

## Dev Agent Record

### Context Reference

- Story drafted by the BMAD Scrum Master (create-story) on 2026-06-28 from epics.md + PRD + architecture.md +
  the done 4.1/4.2/2.5 stories + the live `negative_assurance.py` / `integrity.py` / `pipeline.py` surfaces.

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, implement) — 2026-06-28.

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py` → 742 passed (721 → 742).
- `python -m mypy minions_core/apaa/evidence/bundle.py minions_core/apaa/evidence/__init__.py
  minions_core/apaa/pipeline.py` → clean on the new + edited modules (the only residual errors are the
  pre-existing `radon.*` import-untyped notes in `detectors/tool_runner.py`, transitively imported by
  `pipeline.py` — not introduced by this story; the 4.2 review recorded `pipeline.py` mypy-clean under the
  same condition).
- Structural gates: `test_no_web_imports.py` (extended `_MODULES_UNDER_GUARD` + the new
  no-governance-evidence-import assertion), `test_canonical_single_serializer.py` (AST gate — no direct
  `json.dumps` in `evidence/bundle.py`) both green.

### Completion Notes List

- **NEW pure `minions_core/apaa/evidence/bundle.py`** — the FR29 evidence-bundle export. A frozen
  `EvidenceBundle` (`frozen=True, extra="forbid"`, localized `EVIDENCE_BUNDLE_SCHEMA_VERSION`) AGGREGATES BY
  REFERENCE the already-redacted surfaces: the 4.1 `NegativeAssuranceVerdict` (verdict + scope statement +
  disclaimer + materiality + deep-%), the 2.2 `CoverageReport` (per-file depth states + per-depth counts +
  exact-`Fraction` deep-%), the verdict-impact-ordered 1.6 `Recording` findings (locators + ids + advisory
  + `contained_secret` indicator ONLY — no value field), the 4.2 `IntegrityReport`, and metadata
  (`schema_version`, `apaa_version`, `commit`, `materiality_bar`). PURE `build_evidence_bundle(result,
  integrity_report, *, commit, apaa_version)` folds the in-memory records (duck-typed against `AuditResult`
  to avoid a circular `pipeline` import); `bundle_to_canonical_payload` / `bundle_to_canonical_bytes`
  re-install LIVE `Fraction` leaves and route through the single 1.1 `canonical.dumps_bytes` (no second
  `json.dumps`); OPTIONAL impure `persist_evidence_bundle` writes content-addressed to `state/` via the 1.3
  writer with producer token `apaa.evidence.bundle`. Typed `EvidenceBundleError` (a `ValueError` subclass).
- **The no-source-retention MOAT is STRUCTURAL (AC3)** — every `EvidenceBundle` leaf is a repo-relative
  POSIX locator / id / closed-enum kind / redacted indicator / deterministic statement / `Fraction` / `int`
  / `bool`. No field holds a source byte / raw excerpt / secret value (the ABSENCE of a value field is the
  moat, the 2.5 argument). NO `repo_path` / abs-path. NO `float`. Verified by a model-field-inspection test
  + the no-coupling-to-`governance/evidence.py` import gate.
- **Additive `AuditResult.coverage_report` (pipeline.py)** — the 2.2 `CoverageReport` is built in the SHARED
  `_assemble_and_persist` fold (so fresh == resumed) and exposed PURELY in-memory (DERIVABLE from the
  ledger, NOT a new persisted artifact — the `floor_report` precedent), so a run's persisted `.apaa/` bytes
  are BYTE-IDENTICAL to 4.1/4.2 (AC6). `pipeline.py` 1160 lines (≤1200). `bundle.py` 334 lines (≤1200).
- **AI-E3-1 RED-then-green keystone-fixture demonstrations (documented):**
  - *No-source-retention (AC2):* the NEW `cartridges/evidence_sentinel` plants a DISTINCTIVE source
    sentinel (`EVIDENCE_SENTINEL_zXqW7vKpLmNrTaBcDeF1234567890ABCDEF`) AND the 2.5 secret sentinel
    (`PLANTEDxAbCd...`). The full `run_audit_detailed` + bundle export + persist proves BOTH sentinels (and
    the bare `EVIDENCE_SENTINEL` / `PLANTED` tokens) are ABSENT from the serialized bundle bytes, the
    persisted bundle artifact, AND the whole `.apaa/` working state — WHILE the bundle is non-empty + the
    secret finding IS present (`rule_id == hardcoded_secret`, correct locator). **RED demonstrated** two
    ways: (1) the committed `test_no_source_retention_test_is_red_against_a_leaking_builder` injects the
    sentinel into a payload field and asserts the SAME byte-absence check FAILS on the leak; (2) a manual
    leaking-builder variant (copying the source excerpt into `commit`) was run and confirmed the green
    bundle has no sentinel while the leaking variant does.
  - *Bundle-completeness (AC1):* a fixture spans ≥1 of every section over all three verdicts (RELEASE_READY
    / NOT_READY_FOR_RELEASE / INSUFFICIENT_COVERAGE) with a multi-depth ledger + ≥1 finding; **RED**
    demonstrated by `test_completeness_is_red_if_a_section_is_dropped` (a dropped 4.1 wrapper / coverage
    report raises `EvidenceBundleError`, never silently dropped).
  - *No-over-claim (AC4):* the 4.1-locked forbidden-phrase set (`certif`/`is correct`/`proven`/`guarantee`/
    `defect-free`/`bug-free`/`passed`, case-insensitive) scanned over all three serialized bundles = zero
    hits; **RED** demonstrated by `test_no_over_claim_scan_is_red_on_an_injected_phrase`.
  - *Determinism (AC6):* byte-identity across two builds + order-independence across shuffled
    ledger/integrity inputs; **RED** demonstrated by `test_order_dependence_would_be_red` (arrival-order
    render diverges).
- **Scope fences honored:** NO CI-blocking randomized-canary property suite (that is Story 4.4 — this ships
  the per-story producer proof only); NO change to the 4.1 wrapper / 4.2 lint / 1.6 gate / 1.2 ledger / 2.2
  coverage report / 1.1 serializer / 1.3 store frozen contracts; NO coupling to
  `minions_core/governance/evidence.py`; NO new HTTP route / FastAPI surface / UI; NO mandatory pipeline
  stage / `cli.py` subcommand (DN-WIRING — the persist helper is a standalone library, not wired). No new
  defer filed (AI-E3-3: no closure obligation, no scope expansion).
- **Test area APAA-EVIDENCE** (`TC-APAA-EVIDENCE-001-01..20` in `tests/apaa/test_evidence_bundle.py`, the
  first file in the new area). 20 tests, all green; AC2 mandatory no-source-retention test included in this
  file (not a separate file). AI-E3-2 / AI-E2-1 test-existence gate honored before the `review` flip.

### File List

- NEW `minions_core/apaa/evidence/__init__.py` — the new `evidence/` sub-package shell.
- NEW `minions_core/apaa/evidence/bundle.py` — the FR29 evidence-bundle export (frozen `EvidenceBundle`,
  PURE `build_evidence_bundle`, canonical render, optional persist, typed `EvidenceBundleError`).
- EDIT `minions_core/apaa/pipeline.py` — additive `AuditResult.coverage_report` field built in the shared
  `_assemble_and_persist` fold (in-memory only, not persisted; byte-identical persisted state).
- NEW `tests/apaa/test_evidence_bundle.py` — AC1–AC7 (`TC-APAA-EVIDENCE-001-01..20`), incl. the mandatory
  AC2 no-source-retention sentinel test (RED-then-green).
- NEW `tests/apaa/cartridges/evidence_sentinel/src/config.py.txt` — the planted-sentinel cartridge (source
  sentinel + secret sentinel).
- EDIT `tests/apaa/test_no_web_imports.py` — extended `_MODULES_UNDER_GUARD` with
  `minions_core.apaa.evidence.bundle` + a new `test_evidence_bundle_does_not_import_minions_governance_evidence`.

## Senior Developer Review (AI)

**Reviewer:** claude-opus-4-8 (BMAD code-review gate, adversarial) — 2026-06-28
**Outcome:** PASS (iteration 1) — status `review` → `done`.

### Scope reviewed
NEW `minions_core/apaa/evidence/bundle.py` (frozen `EvidenceBundle`, PURE
`build_evidence_bundle`, `bundle_to_canonical_payload`/`_bytes`, optional
`persist_evidence_bundle`, typed `EvidenceBundleError`), `evidence/__init__.py`,
the additive in-memory `AuditResult.coverage_report` in `pipeline.py`, NEW
`tests/apaa/test_evidence_bundle.py` (20 tests, `TC-APAA-EVIDENCE-001-01..20`),
NEW `tests/apaa/cartridges/evidence_sentinel/`, and the extended
`tests/apaa/test_no_web_imports.py`.

### Verification performed (independent)
- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/test_import_paths.py`
  → **742 passed** (104s), matching the DAR (721 → 742).
- `mypy minions_core/apaa/evidence/bundle.py evidence/__init__.py` → clean.
- Single-serializer AST gate (`test_canonical_single_serializer.py`) green; the
  import-isolation gate green (incl. the NEW no-governance-evidence-coupling
  subprocess assertion, `TC-APAA-EVIDENCE-001-20`).
- File sizes: `bundle.py` 334 lines, `pipeline.py` 1160 lines (both ≤1200).

### Keystone scrutiny — NO SOURCE RETENTION (the security moat)
Traced every leaf of `EvidenceBundle` and every aggregated surface; the moat is
**structural** and holds:
- `EvidenceBundle` leaves: `schema_version`/`apaa_version`/`commit`/
  `materiality_bar` (str), `negative_assurance` (NegativeAssuranceVerdict —
  str/int/bool/Fraction + ScopeStatement of int/bool/sorted repo-relative path
  tuples), `coverage` (CoverageReport — file_path/depth-token/claim-flag/
  recording-ids/counts/Fraction), `findings` (1.6 `Recording`s — recording_id/
  rule_id/advisory/depth/claim/`Locator`{file_path,start_line,end_line,ast_span}),
  `integrity_report` (IntegrityFinding — kind/locator/referent/producer/detail,
  detail built from locator + error-class token only). **No field on any leaf
  can hold a source byte, a raw excerpt, a secret value, or an absolute host
  path.** No `float` anywhere.
- The secret finding it exports is value-free at the source: `secret_scan.py`
  computes `_evidence_for(match)` then DISCARDS the raw value; the `Recording`'s
  `FindingDraft` carries only file_path/line-span/rule_id/advisory — the
  `masked`/`contained_secret` evidence is in-memory-only (2.5) and never attached
  to the exported `Recording`. So `bundle.findings` cannot carry the secret.
- The AC2 keystone test plants a REAL distinctive source sentinel
  (`EVIDENCE_SENTINEL_zXqW7vKpLmNrTaBcDeF...` as an identifier in a source body)
  AND the secret sentinel (`PLANTEDxAbCd...`) via the NEW `evidence_sentinel`
  cartridge, runs the full `run_audit_detailed` + export + persist, and proves
  BOTH (and the bare `EVIDENCE_SENTINEL`/`PLANTED` tokens) ABSENT from the
  serialized bundle bytes, the persisted artifact, AND the whole `.apaa/` tree —
  while the bundle is non-empty and the secret finding IS present at
  `src/config.py`. RED is demonstrated (`...-19`) by injecting the sentinel into
  a payload field and asserting the same byte-absence check fails — non-vacuous.

### Other invariants confirmed
- **Self-contained:** the no-coupling-to-`minions_core.governance.evidence`
  assertion runs in a clean subprocess (cannot false-pass on a prior import) and
  is green.
- **Determinism:** single 1.1 serializer (LIVE `Fraction → num/den` re-installed,
  no second `json.dumps`); byte-identity across two builds + order-independence
  across shuffled ledger/integrity inputs proven, RED demonstrated on arrival-order.
- **Additive:** `coverage_report` is built in the shared `_assemble_and_persist`
  fold (fresh==resumed) and exposed in-memory only — NOT persisted (the
  `floor_report` precedent), so persisted `.apaa/` bytes are byte-identical to
  4.1/4.2.
- **Typed error / purity:** `EvidenceBundleError` on every malformed/missing
  input (missing wrapper, missing coverage, wrong-typed section/finding, non-str
  commit/version); AST purity scan green; PURE (no clock/uuid/random/I/O).
- **No over-claim:** the 4.1-locked forbidden-phrase set scanned over all three
  serialized verdicts = zero hits; RED on an injected phrase.

### Findings
- **[Low] `tests/apaa/test_evidence_bundle.py:613` (`test_persist_round_trips_to_an_equal_bundle`)**
  — the round-trip proves payload byte-identity (`envelope.payload ==
  canonical.loads(bundle_to_canonical_bytes(bundle))`) but does not reconstruct
  an `EvidenceBundle` from the read-back payload. AC5 wording mentions "reconstructs
  an EQUAL bundle". Non-blocking: persistence is optional/unwired this story and
  the bundle ships no deserializer; byte-identity is the load-bearing guarantee.
  Suggested fix (optional, future): if a `from_canonical_payload` is ever added,
  assert model equality too.
- **[Informational] frozen-surface no-diff** could not be verified via `git diff`
  because the entire APAA tree is still untracked (`??`) — not yet committed.
  Confidence comes instead from the full prior-story suite staying green (742) and
  no edits to those modules in the File List. Not a defect.

No High/Medium issues. No unresolved decision-needed/patch findings. No new defer
filed (AI-E3-3: no closure obligation, no scope expansion).

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-06-28 | 0.1 | Initial context-filled story draft (create-story) — FR29 evidence-bundle export with the no-source-retention keystone; Tier-B; scope-fenced (4.4 CI property suite + operated-service lifecycle out of scope) | Scrum Master |
| 2026-06-28 | 0.2 | dev-story (implement) — shipped the FR29 evidence-bundle export: NEW pure `evidence/bundle.py` (frozen `EvidenceBundle` aggregating BY REFERENCE the 4.1 wrapper + 2.2 coverage report + 1.6 ordered findings + 4.2 integrity report + metadata, through the single 1.1 serializer; structural no-source/secret moat; typed `EvidenceBundleError`; optional 1.3-shell persist). Additive in-memory `AuditResult.coverage_report` (byte-identical persisted state). AI-E3-1 RED-then-green keystones (no-source-retention planted source sentinel + secret via the NEW `evidence_sentinel` cartridge; completeness; no-over-claim; determinism). Import-isolation gate extended (+ no-coupling-to-governance-evidence). 742 passed; mypy clean on new+edited modules; `bundle.py` 334 / `pipeline.py` 1160 ≤1200; frozen surfaces untouched. Status → review. | Dev (claude-opus-4-8) |
