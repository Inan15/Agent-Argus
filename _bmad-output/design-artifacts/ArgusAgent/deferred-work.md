# APAA deferred-work

APAA-local deferred-work register (the APAA sub-project is self-contained; this is
kept separate from the Minions platform `implementation-artifacts/deferred-work.md`).
Append-only. Entries carry the six mandatory CC-3 fields
(id · origin_story · owner · target_story|sunset_date · category · severity).

## Deferred from: code review (2026-06-21)

- **DF-1-3-A** — Reader does not assert content-addressed filename == internal `content_hash`.
  `minions_core/apaa/store/reader.py:105`. Defense-in-depth beyond AC6: the required
  tamper case (payload mutated, stale `content_hash`) IS detected; a renamed/misfiled
  artifact whose filename stem diverges from its internal `content_hash` is silently
  accepted. Suggested fix: when the locator stem is a 64-hex sha, assert it equals the
  verified `content_hash`, raising `StoreIntegrityError` on mismatch.
  - id: DF-1-3-A
  - origin_story: 1-3-apaa-store-writer-reader-filesystem-containment
  - owner: Security Owner
  - target_story: epic-4-secret-containment-property-suite-ci-blocking
  - category: security
  - severity: 🟢
  - **INTEGRITY GAP CLOSED 2026-06-27 by story 4-2-referential-integrity-lint-of-on-disk-state**
    (append-only cross-reference note — the original entry above is NOT rewritten, §3.4
    evidence immutability). The filename-stem-vs-internal-`content_hash` gap DF-1-3-A
    flagged is now caught by the referential-integrity lint as a typed
    `filename_content_hash_mismatch` `IntegrityFinding` in
    `minions_core/apaa/store/integrity.py::_resolve_references` — for every
    content-addressed `state/` / `findings/` `<sha>.json` artifact, the lint asserts the
    filename stem equals the envelope's internal `content_hash` (recomputed/verified via
    the REUSED 1.3 `read_envelope` / `compute_content_hash` over the payload only), so a
    renamed / misfiled artifact surfaces (TC-APAA-STORE-001-91, demonstrated RED via the
    sha-stem-check-dropped weakened resolver at TC-APAA-STORE-001-92). `assignments/<id>`
    manifests are keyed by `partition_id` (not a payload sha) and are EXCLUDED from the
    sha-stem check (TC-APAA-STORE-001-93) — they are verified by the plan→assignment
    resolution instead. NOTE: the lint lands this as a LINT FINDING (not a reader-time
    raise), keeping the 1.3 `read_envelope` contract frozen — DF-1-3-A's
    `target_story: epic-4-secret-containment-property-suite-ci-blocking` (Story 4.4) may
    still elect a CI-blocking enforcement of the lint; the integrity GAP itself is closed
    here.

- **DF-1-3-B** — Containment `_is_contained` LOGIC mirrored, not imported, from the
  importable `WorkspaceArtifactWriter._is_contained` staticmethod.
  `minions_core/apaa/store/paths.py:65`. Thin-wrap of logic is explicitly authorized
  (architecture Decision F) and the two impls are currently byte-identical, but a future
  hardening of the canonical check could silently diverge from the APAA mirror.
  Suggested fix: import + reuse the canonical staticmethod, OR add a parity test pinning
  logical equivalence over the same escape-vector matrix.
  - id: DF-1-3-B
  - origin_story: 1-3-apaa-store-writer-reader-filesystem-containment
  - owner: Security Owner
  - target_story: epic-4-referential-integrity-lint-of-on-disk-state
  - category: security
  - severity: 🟢
  - **LEFT OPEN 2026-06-27 by story 4-2-referential-integrity-lint-of-on-disk-state**
    (append-only note — the original entry above is NOT rewritten, §3.4). The 4.2 lint
    REUSES `ApaaStorePaths` containment (every enumerate-and-read goes through the
    containment-checked resolver, NFR-S5) but adds NO new/second containment
    implementation, so the lint did not naturally touch the `paths.py::_is_contained`
    ↔ `WorkspaceArtifactWriter._is_contained` mirror this defer concerns. Adding the
    parity test would not exercise the lint's code path (it pins a 1.3 invariant, not a
    4.2 one), so per the story's "do NOT expand scope to chase it if it does not fit
    cleanly" guidance the 🟢 parity test is LEFT OPEN; a future `target_story` (a
    `store/paths.py` hardening or the 4.4 secret-containment suite) is the cleaner home.
    The shared invariant (`is_relative_to`, never `str.startswith`) remains pinned by the
    existing containment + import-isolation gates.

- **DF-2-3-B** — Persisted `.apaa/` run-state records operator designation INTENT, not
  the computed critical set. `minions_core/apaa/pipeline.py:265`. The run-state persists
  `request.to_provenance_payload()` (raw `critical_paths`/`excluded_critical_paths`), but
  NOT the computed `CriticalSubsystemSet` (final paths + per-path `origins` +
  `designated_but_unmatched`). The exclusion lever IS auditable (operator intent is
  recorded), and the negative-assurance narration of which critical subsystems were/weren't
  covered is explicitly Epic-4 Story 4.1 scope — non-blocking for V1. Suggested fix: when
  Story 4.1 lands the negative-assurance scope statement, persist the computed
  `CriticalSubsystemSet` (origins + designated_but_unmatched) so a reader can distinguish an
  override of a genuine heuristic hit from a no-op exclude.
  - id: DF-2-3-B
  - origin_story: 2-3-critical-subsystem-identification-operator-designation
  - owner: QA Lead
  - target_story: epic-4-negative-assurance-verdict-semantics
  - category: governance
  - severity: 🟢
  - **CLOSED 2026-06-27 by story 4-1-negative-assurance-verdict-semantics** (append-only
    closure note — the original entry above is NOT rewritten, §3.4 evidence immutability).
    The computed `CriticalSubsystemSet` (final `paths` + per-path `origins` +
    `designated_but_unmatched`) is now persisted additively to `.apaa/state/` via the
    EXISTING `ApaaStoreWriter.write_payload("state", ...,
    producer="apaa.pipeline.critical_subsystems")` in the shared `_assemble_and_persist`
    fold (`pipeline.py::_persist_critical_subsystems`) — content-addressed, single 1.1
    serializer, containment-checked, round-trips equal (TC-APAA-VERDICT-001-20/21). A
    reader can now distinguish an override of a genuine heuristic hit (`origins` =
    `heuristic`) from an operator force (`operator_designated`) and from a no-op exclude
    (the suggested fix). The operator-INTENT provenance the run already persisted is
    UNCHANGED (additive). The negative-assurance scope statement narrates which critical
    subsystems were / were NOT examined deeply from this set
    (TC-APAA-PIPELINE-001-32/33).

- **DF-3-4-A** — The resume entrypoint is library-only in V1 — no operator-facing
  `--resume` CLI flag. `minions_core/apaa/cli.py` (unchanged). Story 3.4 shipped
  `resume_audit_detailed` / `resume_audit` in `pipeline.py` (exercised by tests), but the
  thin `argparse` `--resume` wiring was deferred to keep `cli.py` unchanged this story and
  to settle the in-tree `.apaa/`-vs-drift ergonomics (resume re-loads the repo at the pin
  and the loader refuses a drifted tree, so V1 resume requires the `.apaa/` store OUTSIDE
  the audited working tree via an injected reader/writer). Non-blocking — the resume
  MECHANISM is fully tested. Suggested fix: add a thin `--resume` flag (wiring only, no
  logic — AR2/NFR-M1) that routes to `resume_audit` + the `.gitignore`d-`.apaa/` operator
  ergonomics, in a follow-up story.
  - id: DF-3-4-A
  - origin_story: 3-4-resumability-from-on-disk-apaa-state
  - owner: Delivery Orchestrator
  - target_story: epic-7-minions-full-repo-partition-budget-sizing-plan
  - category: process
  - severity: 🟢

## Deferred from: code review (2026-06-28)

- **DF-5-1-A** — The `prompt-template version` closure input enumerated in architecture
  §77 ("content-hash + model checkpoint + **prompt-template version** + tool versions +
  budget/materiality + work-manifest scope + detector-set content-hash") has NO slot in
  `RecordingProducingClosure` (`minions_core/apaa/cache/key.py:172`). In V1 Tier-A there is
  NO live LLM (the deep path is heuristic/claim-proxy), so there is no prompt template to
  fold today — this is correctly out of V1 scope, like the model-checkpoint placeholder.
  BUT unlike `model_checkpoint` (which was given a stable placeholder key slot precisely to
  avoid a future silent-staleness hole), the prompt-template version was given NO slot.
  When Epic-6 Story 6.1 wires the live LLM dispatch, a prompt-template change would NOT move
  the cache key → a stale result computed under a different prompt could be served — the
  exact silent-cache-staleness failure mode this story's canary exists to prevent. The
  `CACHE_KEY_SCHEMA_VERSION` bump lever + the additive `extra="forbid"` model permit a clean
  6.1 addition, so this is a forward-coupling documentation/seam gap, not a V1 correctness
  bug. Suggested fix (6.1): add a `prompt_template_version` field to `RecordingProducingClosure`
  (mirroring the `model_checkpoint` placeholder/slot pattern + a perturbation-matrix leg),
  fold it in `_closure_payload`, and bump `CACHE_KEY_SCHEMA_VERSION`. Interim (this story, a
  doc-only note): add a key.py docstring forward-note that prompt-template version is an
  Epic-6 LLM-path closure input deliberately deferred to 6.1.
  - id: DF-5-1-A
  - origin_story: 5-1-cache-key-derivation-recording-producing-closure-ci-canary
  - owner: Engineering Lead
  - target_story: 6-1-llm-dispatch-port-minions-orchestrator-adapter
  - category: process
  - severity: 🟡
  - **CLOSED 2026-06-28 by story 5-1 (dev-story fix iter-1)** (append-only closure
    note — the original entry above is NOT rewritten, §3.4 evidence immutability).
    Rather than the interim doc-only mitigation, the reviewer's full suggested fix was
    applied THIS round: `RecordingProducingClosure` now carries a
    `prompt_template_version` field (mirroring the `model_checkpoint` DN-PLACEHOLDER
    slot), defaulting to the stable V1 sentinel `V1_PROMPT_TEMPLATE_VERSION =
    "v1-no-prompt-template"` and shaped for a clean ADDITIVE Epic-6 Story 6.1
    substitution of the real captured prompt-template version. It is folded into
    `_closure_payload`, and `CACHE_KEY_SCHEMA_VERSION` was bumped `1 → 2` (the golden
    key was regenerated to `2628b9a6…550ca87` — a documented intentional
    invalidation). A bidirectional canary leg was added (`prompt_template_version` in
    `_PERTURBATIONS` → key changes; it is also covered by the `_key_ignoring`
    keystone-adequacy RED demo), plus a placeholder-default test
    (TC-APAA-CACHE-001-21) and a drift-seam test (TC-APAA-CACHE-001-22). The
    silent-cache-staleness hole at 6.1 (a prompt-template change not moving the key)
    is closed: two prompt-template values now derive two keys. 783 passed, mypy clean,
    structural gates green. Epic-6 Story 6.1 substitutes the real captured value into
    the existing slot (no key-shape change).

## Back-filled from: story-file register (2026-06-29) — AI-E5-4 central-register back-fill

- **DF-1-7-B** — Interim Python deep over-grading. The pipeline graded EVERY
  cleanly-parsed non-test Python file `audited_deep` purely on claim-PRESENCE
  (`pipeline.py::_grade_non_test_python` → `grade_entry(proposed_depth=AUDITED_DEEP,
  claim_present=True)` — the FR6 proxy, originally recorded at `pipeline.py:149`).
  That over-graded a file as deep merely because it parsed, not because its claim was
  verified, inflating the deep-% the 1.6 verdict gate reads. The full Python AST
  GROUNDING of `audited_deep` claims (FR7) was deferred to Epic 6. This entry
  previously lived ONLY in the 1-7 story line; it is back-filled here per AI-E5-4 (the
  story-file copy is retained as evidence; the original is NOT rewritten — §3.4).
  - id: DF-1-7-B
  - origin_story: 1-7-cli-invocation-contract-pipeline-signature-demo-vacuous-test-cartridge
  - owner: Engineering Lead
  - target_story: 6-2-full-python-ast-grounding-of-audited-deep-claims
  - category: process
  - severity: 🟡
  - **CLOSED 2026-06-29 by story 6-2-full-python-ast-grounding-of-audited-deep-claims**
    (append-only closure note — the original entry is NOT rewritten, §3.4). The FR7
    AST-grounding gate is now live: the new PURE provider-free validator
    `minions_core/apaa/audit/grounding.py::is_deep_claim_grounded` (the stack-agnostic
    `claim → validated?` interface, Python = impl #1) computes a deterministic
    structural grounding fact over the PRE-BUILT 1.4 `AstIndexEntry` — GROUNDED iff ≥1
    real `Definition` (DN-GROUND-RULE; no re-parse / no second tree-sitter/ast/radon
    call — AR7/§3.3). `pipeline.py::_grade_non_test_python` now passes
    `claim_present=(claim_emitted AND claim_grounded)` into the UNCHANGED 1.2
    `grade_entry` (DN-GROUNDED — `coverage_ledger.py` byte-identical), so a clean-parse
    ZERO-definition module (constants-only / re-export / docstring-only) downgrades to
    `audited_shallow` instead of being over-graded `audited_deep`. The over-grading is
    demonstrated RED-then-green (TC-APAA-AUDIT-001-50: the interim `claim_present=True`
    shape grades a zero-def file deep — RED; the validator downgrades it — GREEN) and
    the verdict migration is observable end-to-end (TC-APAA-PIPELINE-001-41: a
    zero-def-only repo now lands INSUFFICIENT_COVERAGE / exit 3 instead of clearing the
    floor). The migration is HONEST: every cartridge SUT (`calculator.py`, `adder.py`,
    `multiplier.py`, `config.py`, `café_calc.py`, `guard.py`, `модуль_секрет.py`, …) has
    ≥1 real def → stays GROUNDED → `audited_deep`, so the signature-demo moat is
    PRESERVED (TC-APAA-PIPELINE-001-40: `calculator.py` stays deep → deep-% 1/2 →
    NOT_READY_FOR_RELEASE / BLOCKED 🔴 / exit 2 unchanged). The V1 grounding fact is the
    DETERMINISTIC structural AST fact; the LLM-recording-fed grounding is a documented
    forward seam, NOT the 6.2 default (DN-V1-DETERMINISTIC) — the pipeline default path
    stays PURE + zero-token + deterministic (NFR-D1/D2). Web + no-LLM import gates
    extended-not-forked (the pipeline pulls the pure validator but NO LLM dispatch
    surface; TC-APAA-AUDIT-001-47); frozen Epic-1..5 contracts byte-identical; full
    declared-set + no-crash matrix + non-ASCII covered (TC-APAA-AUDIT-001-46..58).

## Back-filled from: story-file register (2026-06-29) — AI-E5-4 central-register back-fill (story 6.3)

- **DF-1-4-A** — Edge-set richness is unresolved-name only (no scope binding).
  `index/ast_index.py:186-231` — the 1.4 `CodeEdge` captures the bare callee
  identifier / trailing attribute with NO name binding, NO scope resolution, NO
  import resolution. This is the documented, AC-sanctioned V1 substrate (Epic-6
  owns the resolved call graph), so it is NOT a defect — recorded only so the
  downstream 1.5 / Epic-6 consumers know the edge set is unresolved. This entry
  previously lived ONLY in the 1-4 story line; it is back-filled here per AI-E5-4
  (the story-file copy is retained as evidence; the original is NOT rewritten —
  §3.4).
  - id: DF-1-4-A
  - origin_story: 1-4-tree-sitter-ast-index-repo-intake-python-stack-detection
  - owner: Engineering Lead
  - target_story: epic-6-orphan-dead-code-detector
  - category: other
  - severity: 🟢
  - **CONSUMED 2026-06-29 by story 6-3-orphan-dead-code-detector** (append-only
    consumption note — the original entry is NOT rewritten, §3.4). The Story 6.3
    FR12 orphan / dead-code detector
    (`minions_core/apaa/detectors/orphan_code.py::OrphanCodeDetector`) consumes the
    SAME pre-built 1.4 `definitions`/`edges` (no re-parse — AR7/§3.3) and computes a
    CONSERVATIVE name-reachability fact OVER the unresolved-name graph. **What the
    unresolved substrate CAN prove:** a definition whose `name` appears as NO
    `CodeEdge.callee` anywhere in the whole index is a *candidate* orphan. **What it
    CANNOT prove (so the rule stays silent):** which def a callee resolves to, so a
    name-collision (two defs share a name; any one referenced) makes BOTH NOT-orphan;
    and reachability via dunders / `__all__` / `test_*` / framework-registry /
    dynamic-dispatch hooks the bare-callee edges cannot see, handled by a locked
    EXCLUSION set (`ORPHAN_EXCLUSION_NAMES` + structural `__x__` + `test_*`). The
    asymmetric-harm bar (a false dead-code deletion ≫ a missed orphan) locks the rule
    toward silence: when in doubt → NOT-orphan, NEVER a false dead-code accusation.
    The finding is `advisory=True` (CC #6) — it informs, it does not alone move the
    verdict to 🔴 (the 6.4 Prosecutor owns promotion). HONEST limitation (documented
    in the detector docstring, the 1.5 register): the detector grounds REACHABILITY
    over an UNRESOLVED-name graph — LOW recall (it can miss an orphan a resolved graph
    would catch), HIGH precision (it does not falsely accuse live code, the asymmetric
    priority); requirement-traceability is NOT established in V1 (the 2.6 register).
    Proven by the complete-the-declared-set suite (TC-APAA-ORPHAN-001-01..17,
    including the RED-first name-collision guard TC-APAA-ORPHAN-001-05) + the
    end-to-end pipeline wiring (TC-APAA-PIPELINE-001-50..52, incl. the no-orphan
    byte-identity AC4). A **resolved call graph for higher orphan recall** is the
    deferred V2 / Epic-6-depth work this defer originally named — filed below as a
    NEW append-only defer.

- **DF-6-3-A** — Resolved call graph (name binding / scope / import resolution) for
  higher orphan recall. The Story 6.3 detector grounds orphan reachability over the
  1.4 UNRESOLVED-name edge set (DF-1-4-A), which is deliberately conservative (LOW
  recall, HIGH precision): a name-collision or any framework/dynamic reachability the
  bare-callee edges cannot see resolves to NOT-orphan. A V2 resolved call graph (name
  binding + scope + import resolution) would raise recall — surfacing orphans the
  name-match graph conservatively keeps silent — WITHOUT relaxing the
  no-false-accusation moat. This is Epic-6-depth / V2 work, out of scope for the V1
  Tier-B FR12 slice.
  - id: DF-6-3-A
  - origin_story: 6-3-orphan-dead-code-detector
  - owner: Engineering Lead
  - target_story: epic-6-resolved-call-graph
  - category: other
  - severity: 🟢

- **DF-6-4-A** — Full resolved cross-partition SEAM auditor (V2). The Story 6.4
  `cross_partition` cut-edge pass is the V1 MITIGATION (OI2 / CC #4): it re-reads the
  2.4 `PartitionPlan.cut_edges` over the UNRESOLVED-name set (DF-1-4-A) and SURFACES a
  cut a seam-spanning defect COULD hide in (an advisory `cross_partition` finding) —
  it does NOT PROVE a defect spans the cut. A V2 resolved-seam auditor (name binding /
  scope resolution / a resolved call graph across the cut, a non-`"root"` analyzed
  `partition_id`) would PROVE a seam-spanning defect rather than merely surface the
  cut as a hiding place — distinct from the V1 SURFACE-not-PROVE mitigation, and
  related to but broader than DF-6-3-A's resolved-call-graph scope (that defer targets
  orphan recall; this targets cross-partition seam proof). This is Epic-6-depth / V2
  work, out of scope for the V1 Tier-B FR19 slice.
  - id: DF-6-4-A
  - origin_story: 6-4-adversarial-prosecutor-cut-edge-pass
  - owner: Engineering Lead
  - target_story: epic-6-resolved-seam-auditor
  - category: other
  - severity: 🟢

## Deferred from: code review (2026-06-30)

- **DF-6-4-B** — `_has_ast_corroboration` cannot distinguish a genuine 6.2 AST-grounded
  `Locator.ast_span` from the synthetic `cross_partition:<file>::<callee>` seam token a
  `cross_partition` finding carries, so a signed-off `cross_partition` finding WOULD be
  promotable — contradicting the `prosecutor.py` docstring claim that a cut edge "is never
  promoted in V1." HARMLESS in the V1 pipeline (the pipeline never passes `sign_offs`, so no
  promotion is reachable and the downgrade-only + un-prosecuted byte-identity properties hold);
  the operator-sign-off promotion surface is the documented forward seam. V2 hardening: when a
  live sign-off surface lands, distinguish genuine AST corroboration from the synthetic seam
  token (a dedicated grounded flag) OR exclude `rule_id == cross_partition` from
  `_is_advisory_promotable`. Low severity; not in scope for the V1 Tier-B FR19 slice.
  - id: DF-6-4-B
  - origin_story: 6-4-adversarial-prosecutor-cut-edge-pass
  - owner: Engineering Lead
  - target_story: epic-6-resolved-seam-auditor
  - category: governance
  - severity: 🟢

## Deferred from: dev-story (2026-06-30)

<!-- defer-schema-session: 2026-06-30 -->

- **DF-6-6-A** — Grow the corpus to N=5 DISTINCT defect-rule classes + run the human
  validation-protocol adjudication so the ≥80%-precision gate can flip from PROVISIONAL
  to cleared. Story 6.6 stood up the PURE precision replay harness
  (`minions_core/apaa/precision/replay_harness.py::compute_precision`) + the committed
  validation protocol (`precision-validation-protocol.md`) and computed an EARLY/PROVISIONAL
  precision of `1/1` over the current corpus (6 TP / 0 FP / 0 FN — no false BLOCKING
  accusation; clean repos legitimately emit only advisory findings). HONEST LIMITATION
  (the OI1 keystone, NOT softened): `populated_planted_defect_count()` returns `5` cartridge
  ROWS, but those span only THREE distinct defect-rule CLASSES (`vacuous_test_ast` ×3 —
  vacuous_basic/holdout_vacuous/nonascii_unicode, `hardcoded_secret` ×1, `orphan_code` ×1).
  The gate therefore STAYS PROVISIONAL: `compute_precision` defaults `protocol_cleared=False`
  and 6.6 did NOT flip the marker — the flip requires (a) a corpus of genuinely distinct
  labeled defect classes with sufficient findings AND (b) a recorded human Engineering-Lead +
  QA-Lead adjudication run per the validation protocol §4/§5, neither of which 6.6 performs
  (6.6 must not manufacture cartridges nor fabricate a cleared adjudication). The harness +
  schema are DESIGNED for N=5 with no refactor (a new cartridge = a registry row + a
  `*.py.txt` drop-in). Closing this defer = grow the labeled corpus + run the adjudication +
  pass `protocol_cleared=True` at the call site. Related to the Epic-7 Minions dogfood
  (empirical precision over a REAL repo), but distinct: this is the CARTRIDGE-corpus gate flip.
  - id: DF-6-6-A
  - origin_story: 6-6-precision-replay-harness-validation-protocol
  - owner: Engineering Lead
  - target_story: epic-7-minions-dogfood-precision
  - category: process
  - severity: 🟠

## Deferred from: dev-story (2026-07-01)

<!-- defer-schema-session: 2026-07-01 -->

- **DF-6-7-A** — Wire the PURE HITL escalation gate + the append-only decision-record writer
  into the LIVE pipeline / CLI invocation. Story 6.7 delivered the deterministic resolution +
  the record contract as a LIBRARY seam (`minions_core/apaa/governance/escalation.py::escalation_fires`/
  `resolve_escalation` + `governance/decision_record.py::DecisionRecordWriter.append`), fully
  proven by `tests/apaa/test_hitl_escalation.py` — but per the story scope fence (DN-NO-PROD-CHANGE-FROZEN)
  it did NOT change the frozen straight-line `pipeline.py` dataflow, add a `cli.py --escalate`/
  `--decision` flag, or add a live async/blocking human-wait transport / notification / webhook /
  queue (that human-input transport is the caller's concern — the gate is a pure resolution over
  `(escalation_condition, optional_human_decision, timeout_elapsed)`). The AC proof needed NO live
  pipeline invocation, so no minimal seam was added. Closing this defer = decide the escalation-rule
  configuration source, add the minimal pipeline call site + a CLI decision flag, and (AI-E5-4 named
  target) land it as part of the Epic-7 Minions dogfood proof run, which is the first live consumer.
  The V1 escalation is PATTERN-MATCHED only; an LLM-driven escalation adjudicator remains a documented
  forward seam behind the 6.1 `LLMDispatchPort`, NEVER the V1 default (the FR23 lock).
  - id: DF-6-7-A
  - origin_story: 6-7-hitl-stop-proceed-escalation-append-only-decision-record
  - owner: Delivery Orchestrator
  - target_story: epic-7-minions-dogfood-proof-run
  - category: process
  - severity: 🟢

## Progress note: dev-story (2026-07-02) — story 7.1 DF-6-6-A autonomous half advanced

<!-- defer-schema-session: 2026-07-02 -->

- **DF-6-6-A-P1** — DF-6-6-A AUTONOMOUS half advanced (append-only progress note; the
  original DF-6-6-A entry above is NOT rewritten, §3.4 evidence immutability). Story 7.1
  discharged the AUTONOMOUS corpus-growth half of DF-6-6-A: the labeled synthetic corpus
  now spans **5 DISTINCT defect-rule CLASSES** (up from 3), by appending TWO NEW
  distinct-class cartridges to `tests/apaa/cartridges/_registry.py::CARTRIDGE_REGISTRY`
  (REUSE the frozen `CartridgeSpec`/`GoldenFinding` SHAPE — a registry ROW + a `*.py.txt`
  template drop-in, no harness refactor / no forked registry): (1) `vacuous_heuristic_basic`
  (kind=planted_defect, class `vacuous_test_heuristic` — a heuristically-vacuous test with a
  SUT call but NO assertion and NO mock, so the Tier-A AST corroboration is withheld and the
  finding stays advisory / verdict-ineligible; a DISTINCT class from `vacuous_test_ast`); and
  (2) `cross_partition_seam` (kind=holdout, class `cross_partition` — a 45-file cohesion chain
  whose oversized component the REAL 2.4 `partition_repository` splits under the DEFAULT
  NFR-SC1 limits, producing a REAL `CutEdge` that the REAL 6.4 Prosecutor cut-edge pass emits
  as an advisory `cross_partition` finding through the UNMODIFIED `run_audit_detailed`). Both
  rule_ids were CONFIRMED-emitted over a staged cartridge by running the real pipeline (NOT
  assumed) — NEVER a synthetic rule_id no detector produces. The 6.6 `compute_precision`
  roll-up runs over the grown corpus UNCHANGED and each new class produces its OWN TP
  (verified TC-APAA-DOGFOOD-001-09; distinct-class count is 5, not a collision-collapsed
  count — TC-APAA-DOGFOOD-001-10). The current honest count: `distinct_rule_class_count() == 5`
  (`cross_partition`, `hardcoded_secret`, `orphan_code`, `vacuous_test_ast`,
  `vacuous_test_heuristic`); `populated_planted_defect_count() == 7` labeled ROWS.
  **The OI1 keystone HOLDS (NOT softened):** the ≥80%-precision gate STAYS PROVISIONAL —
  `compute_precision` defaults `protocol_cleared=False`, 7.1 did NOT flip the marker, and
  the `precision_gate_status()` marker still reads "provisional". The HUMAN TP/FP
  adjudication over REAL dogfood findings (the DF-6-6-A HUMAN half) is still OPEN — it is
  performed in 7.2 + an explicit human step, and ONLY it may clear the gate. 7.1 grows the
  substrate autonomously; it does NOT present a cleared gate from a synthetic corpus.
  - id: DF-6-6-A-P1
  - origin_story: 7-1-minions-full-repo-partition-budget-sizing-plan
  - owner: Engineering Lead
  - target_story: epic-7-minions-dogfood-precision
  - category: process
  - severity: 🟠

## Progress note + defer: dev-story (2026-07-02) — story 7.2 dogfood EXECUTED + human adjudication filed

<!-- defer-schema-session: 2026-07-02 -->

- **DF-6-6-A-P2** — DF-6-6-A EXECUTION half advanced (append-only progress note; the
  original DF-6-6-A entry + the 7.1 DF-6-6-A-P1 note above are NOT rewritten, §3.4
  evidence immutability). Story 7.2 (the APAA CAPSTONE) EXECUTED the Minions dogfood: it
  ran the frozen `pipeline.run_audit_detailed` (REUSED — no fork) over the REAL Minions
  platform source (135 git-tracked `minions_core/` modules over 36712 LOC, the 7.1 4-unit
  plan, materialized into a clean on-pin snapshot via the 6.5 `stage_cartridge` pattern)
  under `budget = $X = 843` (the 7.1 empirical ceiling). The run FITS within `$X` (V1
  deterministic total 675 credits, `ceiling_reached is False`) and DEMONSTRATES the 3.2
  halt (a ceiling below the total breaches). It produced a real verdict
  (`NOT_READY_FOR_RELEASE` / exit 2, deep-% `13/15`, 0 verdict-eligible/blocking findings)
  + a SIGNED source-free evidence bundle (REUSING the 4.3 `build_evidence_bundle` /
  `persist_evidence_bundle` + the 1.1 prev-hash-chained envelope + the 4.2 integrity lint
  — consistent) + a reproduced `GitHub green · Sonar green · APAA 🔴` signature demo + a
  100%-reproducibility check (byte-identical verdict + bundle bytes across two runs) +
  the honest `grade: demo-heuristic-only` red-team flag. The REAL dogfood findings are laid
  out ADJUDICATION-READY (3 advisory finding CLASSES — `cross_partition` ×332,
  `hardcoded_secret` ×2289, `orphan_code` ×285 — each mapped onto the 6.6 `finding_match_key`
  identity `(rule_id, verdict_eligible, advisory)` with sample locators) in
  `minions-dogfood-proof.md`, so the later human Eng-Lead + QA-Lead TP/FP adjudication can
  clear the ≥80%-precision gate on REAL data. **The OI1 keystone HOLDS (NOT softened):** the
  ≥80%-precision gate STAYS PROVISIONAL — `protocol_cleared` NOT flipped, the
  `precision_gate_status()` marker NOT flipped, NO ≥80% number presented as authoritative /
  cleared, and the Tier-A heuristic-only run is NOT presented as externalization evidence.
  The HUMAN TP/FP adjudication (the DF-6-6-A HUMAN half — the ONLY step that may clear the
  gate) is still OPEN → the new DF-7-2-A defer below.
  - id: DF-6-6-A-P2
  - origin_story: 7-2-execute-minions-audit-proof-artifact-evidence-bundle-signature-demo
  - owner: Engineering Lead
  - target_story: epic-7-minions-dogfood-precision
  - category: process
  - severity: 🟠

- **DF-7-2-A** — Run the HUMAN TP/FP adjudication over the REAL 7.2 dogfood findings to
  clear the ≥80%-precision gate. Story 7.2 EXECUTED the dogfood + laid the REAL Minions-repo
  findings ADJUDICATION-READY (the 3 advisory finding classes in `minions-dogfood-proof.md`
  §6, each with `rule_id` + verdict-eligibility + sample locators, mapped onto the 6.6
  `finding_match_key` shape). Per the OI1 honesty keystone (operator epic-boundary decision
  2026-07-02) the human TP/FP adjudication is the ONLY step that may clear the gate, and it
  is a HUMAN step OUT of scope for the autonomous story. Closing this defer = an Eng-Lead +
  QA-Lead tag each finding class TP/FP per `precision-validation-protocol.md` §4/§5 over the
  REAL dogfood finding set, record the per-metric pass/fail, and (only if the adjudicated
  precision genuinely reaches ≥80% over ≥5 distinct classes) pass `protocol_cleared=True`
  into the 6.6 `compute_precision` + flip the 6.5 `precision_gate_status()` marker. Until
  then the gate stays PROVISIONAL — the autonomous story NEVER fabricates or softclaims a
  cleared gate. DF-6-7-A (live HITL-escalation wiring into the pipeline/CLI) remains OPEN
  and is NOT closed by 7.2 (DN-ESCALATION — out of scope; the dogfood does NOT wire the 6.7
  escalation into the live invocation).
  - id: DF-7-2-A
  - origin_story: 7-2-execute-minions-audit-proof-artifact-evidence-bundle-signature-demo
  - owner: QA Lead
  - target_story: epic-7-minions-dogfood-precision
  - category: process
  - severity: 🟠


## Deferred from: repository audit (2026-07-04)

Multi-pass Minions repository audit (2026-07-04), PASS 3, surfaced APAA orphan/theater items
beyond the already-tracked DF-6-7-A (governance/escalation wiring) and DF-5-1-A (cache-key schema).
Recorded as tracked deferrals; APAA is a CLI-only, self-disclosed "demo-heuristic-only" tool, so
severities are weighted down. Heading is intentionally NOT "code review" (this is an audit, not a
`/bmad-code-review` session) so the defer-schema gate does not enforce; the six fields are carried
voluntarily for consistency.

- **DF-AUD-APAA-A** — The `cache/` sub-package (`cache/key.py`, `cache/memo_store.py`,
  `cache/invalidation.py`) is ORPHAN relative to the shipped `run_audit`/CLI path: `MemoStore` is
  never constructed and `derive_cache_key`/`invalidate_rejections` have no non-test caller, so no
  cache HIT/MISS ever occurs and the AR6 "false-red served forever" prevention cannot run
  (self-disclosed Epic-6 seam: `cache/invalidation.py:66` "the live trigger is Epic-6"). Two theater
  sub-notes: `invalidate_rejections()` reads a `RejectionLedger` nothing populates -> returns `()`
  unconditionally; `RejectionLedger._write` (`cache/invalidation.py:262`) forks a direct `write_bytes`
  while its docstring claims `ApaaStoreWriter` reuse (dead `self._writer`). Close = wire the cache
  layer when the first live consumer (the Epic-7 dogfood proof run) needs it, mirroring DF-6-7-A; or
  explicitly mark it permanent library-only.
  - id: DF-AUD-APAA-A
  - origin_story: 7-2-execute-minions-audit-proof-artifact-evidence-bundle-signature-demo
  - owner: Delivery Orchestrator
  - target_story: epic-7-minions-dogfood-proof-run
  - category: process
  - severity: 🟢

- **DF-AUD-APAA-B** — `read_in_scope` (`index/partitioner.py:631`), the NFR-S4 manifest-scoped read
  primitive whose docstring asserts "an off-scope read is IMPOSSIBLE through it," has NO production
  caller: the live pipeline reads sources via `pipeline._read_source`/`compute_loc_by_file`, so the
  manifest read-boundary is UNENFORCED at runtime (the security guarantee is proven only in
  `tests/apaa/test_partitioner.py`). Also `partition_plan.clears_floor` (`dogfood/partition_plan.py:353`)
  is a `Fraction(n, n) >= floor` tautology, unconditionally `True` — a per-unit coverage-floor "check"
  that can never fail. Close = route the live pipeline read path through `read_in_scope` (or document
  why the boundary is unenforceable in V1) and replace the tautological floor check with a real assertion.
  - id: DF-AUD-APAA-B
  - origin_story: 7-2-execute-minions-audit-proof-artifact-evidence-bundle-signature-demo
  - owner: Governance Owner
  - target_story: epic-7-minions-dogfood-proof-run
  - category: governance
  - severity: 🟡

## Deferred from: code review of 8-1-findings-before-coverage-binding-decision-table (2026-08-04)

- **DF-8-1-A** — A row-4 (`INSUFFICIENT_COVERAGE`, zero blocking findings, a coverage or
  critical-subsystem gate unmet) run still renders the pre-amendment false-accusation sentence in the
  persisted `final-verdict.md`: `argus/reports/generator.py:339` emits
  `> [!CAUTION] Repository is NOT ready for release — deep coverage `2/5` is below the `3/5` release
  threshold.` six lines below `- **Final Verdict**: **`INSUFFICIENT_COVERAGE`** (Exit Code `3`)`, and
  `render_ship_readiness` (`argus/reports/plain_english.py:109`) heads the same document with
  `Ship-readiness: NOT ASSESSED — too little of the code was examined deeply`, which is false for row 4
  (plenty was examined; nothing was found). Reproduced by the reviewer on a synthetic 2-deep/5-total
  zero-findings fold. This is CORRECT for Story 8.1 — AC15 explicitly fences the branch change to
  "change no rendered string" and AC18 fences `plain_english.py` — but it means the human surface of a
  clean-but-under-covered repository still ships a self-contradicting artifact, which is the residual
  half of the very defect Epic 8 exists to remove. Close = Story 8.3 / DR-11's report-surface wording
  reconciliation (the row-1-vs-row-4 split and the `plain_english.py` "NOT VOUCHED" branch audit),
  applying D4's own rule (a persisted artifact must not assert a falsehood) to this callout the way
  Story 8.1 applied it to `negative_assurance.py`.
  - id: DF-8-1-A
  - origin_story: 8-1-findings-before-coverage-binding-decision-table
  - owner: Delivery Orchestrator
  - target_story: 8-3 (DR-11 report-surface reconciliation)
  - category: correctness
  - severity: 🟡
  - **CLOSED 2026-08-05 by story 8-3-plain-english-report-stops-describing-impossible-state**
    (append-only closure note — the original entry above is NOT rewritten, §3.4 evidence
    immutability). BOTH halves are fixed, RED-first. (a) `argus/reports/generator.py`'s
    verdict block now has FOUR arms, one per FR16 row: FR16 row 4 got its own arm and no
    longer borrows row 2's sentence, so the measured
    `> [!CAUTION] Repository is NOT ready for release — deep coverage `2/5` is below the
    `3/5` release threshold.` is gone and is replaced by
    `> [!WARNING] Release readiness is NOT VOUCHED — Argus found nothing blocking, but deep
    coverage `2/5` is below the `3/5` release threshold. This is a statement about the
    audit, not about the code.` (b) `argus/reports/plain_english.py::_headline` splits
    `INSUFFICIENT_COVERAGE` on `AuditVerdict.is_below_floor`, so the document headline at
    `generator.py:269` no longer heads a row-4 run with row 1's
    `NOT ASSESSED — too little of the code was examined deeply`. Closing evidence:
    `TC-ArgusAgent-REPORT-002-20` (`tests/test_report_surface_consistency.py`), which was
    demonstrated RED against the pre-fix implementation for BOTH row-4 causes (the 2/5
    coverage cause and the 5/5-deep critical-subsystem cause), plus the four-row
    cross-surface net `TC-ArgusAgent-REPORT-002-21` — the single test that would have
    caught this defect — and `TC-ArgusAgent-REPORT-002-12`/`-13` on the human register.
    The unreachable `NOT VOUCHED` predicate DR-11 also named is gone: its prose relocated
    to row 4 (where it is true) and the impossible `NOT_READY_FOR_RELEASE ∧ blocking == 0`
    input is now the typed `ShipReadinessError`, proven unreachable by the 270-fold
    exhaustive sweep `TC-ArgusAgent-REPORT-002-10` (0 occurrences, re-derived in place).

## Deferred from: code review of 8-2-critical-subsystem-gates-operator-can-actually-satisfy (2026-08-05)

- **DF-8-2-A** — `argus/pipeline.py` ends Story 8.2 at **1199 lines against the NFR-M1 cap of 1200**, so
  the next line added to it breaches the standard. This is NOT a defect in the 8.2 delta: the story
  explicitly forbade a new module ("No new module. Everything is an edit to two existing source files"),
  the dev complied, condensed the `_critical_ineligibility` docstring rather than dropping the reasoning,
  and recorded the consequence in the Completion Notes. Recorded here so the constraint is discovered at
  planning time rather than at edit time. The underlying pressure is real: `pipeline.py` already owns
  intake wiring, per-file detection (`_detect_per_file`), grading, scope resolution
  (`_assessment_scope_paths`), assembly/persistence (`_assemble_and_persist`) and the resume path, and
  `_critical_ineligibility` is a cohesive derived-fact helper that best practice would site next to the
  predicates it composes. Close = extract a shell-helper module (e.g. `argus/pipeline_facts.py` carrying
  `_critical_ineligibility` and its siblings) as the FIRST act of whichever story next edits
  `pipeline.py`, rather than adding to it. Reviewer verified no other `argus/` source file exceeds the
  cap (next largest: `argus/dogfood/proof_run.py` 749).
  - id: DF-8-2-A
  - origin_story: 8-2-critical-subsystem-gates-operator-can-actually-satisfy
  - owner: Delivery Orchestrator
  - target_story: 8-3 (or the first story after 8.2 that edits `argus/pipeline.py`)
  - category: maintainability
  - severity: 🟢
  - **CARRIED FORWARD, NOT CLOSED — 2026-08-05, story 8-3** (append-only note; the entry
    above is NOT rewritten, §3.4). Story 8.3 did not edit `argus/pipeline.py` at all (its
    AC14 fenced the file and its AC8 reached the AST index through the `ast_index`
    argument `generate_reports` already receives), so the close condition — "extract a
    shell-helper module as the FIRST act of whichever story next edits `pipeline.py`" —
    never triggered. The file is still **1199 lines**, byte-identical to its post-8.2
    state, and the extraction remains owed by the next story that genuinely edits it.

- **DF-8-2-B** — Two entries in `_UNAMBIGUOUS_TEST_SUFFIXES` (`argus/detectors/vacuous_test.py:195-199`)
  are written **without a word separator** — `"test.java"` and `"spec.rb"` rather than
  `"_test.java"`/`"Test.java"` and `"_spec.rb"` — so tier 2 of `is_test_file` claims ordinary production
  files whose basename merely *ends* with those letters. Reviewer-confirmed: `svc/latest.java` and
  `svc/myspec.rb` both return `is_test_file(...) == True` with
  `is_test_classification_content_dependent(...) == False`, i.e. classified as tests by name alone, with
  **no** content check available to correct it (that is what tier 2 means). Since Story 8.2 they have a
  second consumer: such a file leaves the heuristic critical set and is disclosed under the reason
  `test_file`. **This is NOT a defect in the 8.2 delta.** The suffix table is byte-identical at
  `9109e16` and untouched by this story — the reviewer's 2 567-comparison differential proof shows the
  old and new `is_test_file` agree exactly on these paths — and it is not a false green relative to what
  Argus can actually grade, because the GRADING stage misclassifies them identically (they are
  `audited_shallow`, never `audited_deep`), so AC7's "the two stages cannot disagree" invariant still
  holds. Zero instances in this repository (no `.java`/`.rb` sources among the 147 indexed files), so the
  exposure is latent and lands only on a polyglot target repo. Close = add the missing separators and
  pin the near-miss corpus (`latest.java`, `myspec.rb`, `attest.py`, `greatest.py`) in
  `tests/test_vacuous_detector.py` beside `TC-ArgusAgent-DETECT-001-85`/`-95`.
  - id: DF-8-2-B
  - origin_story: 8-2-critical-subsystem-gates-operator-can-actually-satisfy
  - owner: Delivery Orchestrator
  - target_story: 8-3 (or the first story that edits `argus/detectors/vacuous_test.py`)
  - category: correctness
  - severity: 🟢
  - **CARRIED FORWARD, NOT CLOSED — 2026-08-05, story 8-3** (append-only note; the entry
    above is NOT rewritten, §3.4). The `target_story` is conditional and its condition did
    not fire: story 8.3 READ `is_test_file` / `is_test_classification_content_dependent`
    (reusing them rather than forking a second predicate, AC8) but did not edit
    `argus/detectors/vacuous_test.py`, which stayed on its AC14 fence and is byte-identical
    to its post-8.2 state. Still zero live instances in this repository.

## Deferred from: implementation of 8-3-plain-english-report-stops-describing-impossible-state (2026-08-05)

- **DF-8-3-A** — Neither human surface can tell an operator that the FR16 critical-subsystem
  clause was satisfied **VACUOUSLY** — i.e. that the eligibility filter (FR4/DR-5, Story 8.2)
  emptied the heuristic critical set rather than that every designated critical file reached
  `audited_deep`. Story 8.2's D5 handed the positive prose to 8.3/DR-11; Story 8.3 examined it
  and DECLINED it deliberately (its **D5**), for three converging reasons recorded there: the
  epic's own 8.3 AC block asks only that the critical-paths section render correctly for an
  empty set and that the `--exclude-critical` guidance stop being wrong (both delivered by its
  AC7); the information does not exist on `AuditVerdict` (`critical_subsystems_all_deep=True`
  with an empty `critical_subsystems_not_deep` is IDENTICAL for "the set was emptied by the
  filter" and "there were never any criticals" — only
  `CriticalSubsystemSet.heuristic_excluded_ineligible` distinguishes them); and getting that
  disclosure map into the report needs a new argument on `generate_reports` threaded from
  `argus/pipeline.py:793`, i.e. an edit to a file at 1199 of the 1200-line NFR-M1 cap, which
  **DF-8-2-A** says must trigger a module extraction first. Re-deriving the vacuity inside
  `generator.py` from `ast_index` is categorically forbidden (a §3.3/AR7 fork of the
  eligibility filter). This is an OMISSION, not a falsehood: `TC-ArgusAgent-PIPELINE-002-07`
  proves no surface asserts the vacuous positive, and Story 8.3's
  `TC-ArgusAgent-REPORT-002-18` additionally pins that an empty critical set renders nothing
  at all. Close = thread `CriticalSubsystemSet` (or just its `heuristic_excluded_ineligible`
  map) into `generate_reports`/`render_final_verdict_report` and name the vacuity in prose,
  AFTER the DF-8-2-A shell-helper extraction has made room in `pipeline.py`.
  - id: DF-8-3-A
  - origin_story: 8-3-plain-english-report-stops-describing-impossible-state
  - owner: Delivery Orchestrator
  - target_story: the story that performs the DF-8-2-A `pipeline.py` extraction
  - category: correctness
  - severity: 🟢

## Deferred from: code review of 8-3-plain-english-report-stops-describing-impossible-state (2026-08-06)

- **DF-8-3-B** — `argus/reports/plain_english.render_ship_readiness` can now RAISE (the Story 8.3
  `ShipReadinessError`, AR10), but `argus/cli.py` calls it at `:292` **outside** the `try/except ValueError`
  that wraps `run_audit(request)` at `:271-276`. A raise at that site would therefore escape `main()` as an
  uncaught traceback rather than the typed, secret-safe exit `1` the AR10 / NFR-R1 degradation contract
  requires. It is masked whenever `--report-dir` is set — the pipeline then calls `generate_reports` →
  `render_final_verdict_report` → `render_ship_readiness` *inside* `run_audit`, so the raise is caught — but
  `report_dir` defaults to empty, so the default `argus audit <path>` invocation has no guard. Story 8.3's
  `TC-ArgusAgent-CLI-001-32` monkeypatches `cli.run_audit` itself, so it proves the AC's letter
  ("`cli.py:272` catches `ValueError` → exit 1") without ever exercising the real raise site. **Not a live
  defect:** the reviewer proved the triggering state (`NOT_READY_FOR_RELEASE` with
  `blocking_finding_count == 0`) has no producer — `AuditVerdict` has exactly one construction site
  (`verdict_gate.py:651`), no persisted verdict is ever rehydrated, and the prosecutor's `model_copy`
  updates only `ordered_findings` — so this is defence-in-depth, not an operator-visible bug. **Not fixable
  in Story 8.3:** its AC14 fences `argus/cli.py` as must-not-modify. Close = widen the `try` to cover the
  summary-line + ship-readiness block (or move the render inside it) and add a test that lets the REAL
  `render_ship_readiness` raise on the way out of `main()` with no `--report-dir`.
  - id: DF-8-3-B
  - origin_story: 8-3-plain-english-report-stops-describing-impossible-state
  - owner: Delivery Orchestrator
  - target_story: 8-4 (or the first story that edits `argus/cli.py`)
  - category: correctness
  - severity: 🟢

- **DF-8-3-C** — The ast-index → application/test partition is now written twice. Story 8.3's AC8 correctly
  REUSED the predicate (`is_test_file(path, ast_entry=…)`) rather than forking a second classifier, and the
  reviewer confirmed the two call sites agree — but the plumbing around it is duplicated verbatim:
  `argus/pipeline.py:686-694` builds `{e.file_path: e for e in index.entries} if index is not None else {}`
  and filters `ledger.entries`, and `argus/reports/generator.py:86-93` now builds
  `{entry.file_path: entry for entry in (getattr(ast_index, "entries", ()) or ())}` and filters
  `ledger.entries` the same way. Two spellings of the same derivation, in two modules, with the report's
  APPLICATION denominator and the verdict's assessed population depending on them staying identical — which
  is precisely the disagreement class AC8 was raised to remove one level down. **Not fixable in Story 8.3:**
  its AC14 fences BOTH `argus/pipeline.py` (DF-8-2-A, 1199/1200 lines) and `argus/detectors/vacuous_test.py`
  (DF-8-2-B), which are the only two sensible homes for the shared helper. Close = add one helper beside
  `is_test_file` in `argus/detectors/vacuous_test.py` (e.g.
  `partition_application_files(ledger_entries, ast_index) -> tuple[list, int]`) and call it from both sites,
  as part of the story that performs the DF-8-2-A extraction.
  - id: DF-8-3-C
  - origin_story: 8-3-plain-english-report-stops-describing-impossible-state
  - owner: Delivery Orchestrator
  - target_story: the story that performs the DF-8-2-A `pipeline.py` extraction
  - category: maintainability
  - severity: 🟢

## Deferred from: dev of 8-4-tell-integrators-what-changed (2026-08-06)

- **RS-4b** — The bulk `minions_core` provenance sweep across `argus/`. Story 8.4 fixed the package FRONT
  DOOR only (`argus/__init__.py`, RS-4a); every other stale reference remains. **Measured in place on this
  tree** with `grep -rn "minions_core" argus/ --include=*.py`, excluding `__pycache__` and the foreign
  Epic-9-owned `argus/audit/minions_llm_adapter.py`: **15 references across 8 files** —
  `audit/deep_audit.py:21` · `audit/ports.py:4` · `cost/budget_governor.py:15` ·
  `dogfood/partition_plan.py:481,490,554` · `dogfood/proof_run.py:52,53,486,597,609,610` ·
  `governance/escalation.py:35` · `store/envelope.py:25` · `verdict/prosecutor.py:36`.
  ⚠️ **This is NOT a prose-only sweep.** Six of the fifteen, across five `lines.append(...)` call sites,
  emit the stale path INTO GENERATED Markdown artifacts rather than into a docstring:
  `partition_plan.py:481` and `:554` (the two "AUTO-GENERATED by" banners naming
  `minions_core/apaa/dogfood/partition_plan.py`, on the partition plan and the budget plan),
  `partition_plan.py:490` (the provenance line naming `minions_core/` and `minions_core/apaa/`),
  `proof_run.py:597` (the proof artifact's "AUTO-GENERATED by" banner naming
  `minions_core/argus/dogfood/proof_run.py`) and
  `proof_run.py:609-610` (the scope paragraph). A docstring/comment-only pass would miss all five, and the
  committed artifacts they produce would keep regenerating stale. (`proof_run.py:486` is a third kind
  again — an operator-visible `DogfoodProofError` message.) The remaining nine are genuine
  docstring/comment prose.
  ⚠️ **Sequencing constraint — this sweep must FOLLOW Story 8.5.** The generators above produce
  `minions-dogfood-partition-plan.md`, `minions-dogfood-budget-plan.md` and `minions-dogfood-proof.md`,
  which are **Story 8.5 / DR-10's** deliverable (8.5 re-derives them, and `tests/test_dogfood_proof.py`
  carries a committed-artifact rot check that compares them against a live run). Editing the generators
  before 8.5 re-derives would either break that rot check or force 8.5 to re-derive twice. Close = sweep
  the 15 references after 8.5 lands, re-derive the three generated artifacts in the same change, and keep
  the rot check green.
  - id: RS-4b
  - origin_story: 8-4-tell-integrators-what-changed
  - owner: Delivery Orchestrator
  - target_story: 9-2-ship-distribution-another-repo-can-actually-resolve (after 8-5-re-derive-proof-evidence-matches-tool)
  - category: maintainability
  - severity: 🟢

- **DF-8-4-A** — `action.yml` publishes a CRASHED run as an under-covered one. The composite action maps the
  audit exit code to its `verdict` output as `0 → RELEASE_READY`, `2 → NOT_READY_FOR_RELEASE`,
  **`else → INSUFFICIENT_COVERAGE`**. That `else` also swallows exit **`1`** — the AR10 typed-failure code,
  which means the run produced NO verdict at all — and publishes it downstream as
  `verdict=INSUFFICIENT_COVERAGE`, i.e. a *ran-and-under-covered* result. A consuming workflow cannot
  distinguish "Argus examined the repo and could not vouch" from "Argus never produced a verdict", so a
  crash reads as a completed audit. `INSUFFICIENT_COVERAGE` is also, per the PRD, a **not-assessed** state
  rather than a failure, which makes the mislabel an over-claim in the direction this epic exists to
  remove. **Pre-existing, not introduced by Epic 8:** exit `1` predates the FR16/FR4 amendment and the
  amendment changed no exit-code VALUE. **Not fixable in Story 8.4:** `action.yml` is untracked, foreign
  and Epic-9-owned, a concurrent session is editing it, and Story 8.4's AC12 fences it — filing it is
  exactly what the register is for. Close = give exit `1` its own arm (an explicit
  `verdict=AUDIT_FAILED`-style value, or fail the step outright) rather than letting it fall into the
  `else`; decide the output vocabulary with the packaging/distribution work that owns this file.
  - id: DF-8-4-A
  - origin_story: 8-4-tell-integrators-what-changed
  - owner: Delivery Orchestrator
  - target_story: 9-2-ship-distribution-another-repo-can-actually-resolve
  - category: correctness
  - severity: 🟢

- **DF-8-3-B — CLOSURE NOTE (append-only; the original entry above is NOT rewritten).** Closed by Story
  8.4. The `try/except ValueError` in `argus/cli.py::main` was widened to span the summary-line print and
  the ship-readiness render, rather than wrapping `run_audit(request)` alone — so the render is now inside
  the guard on the default no-`--report-dir` path. Widening (rather than moving the render) was chosen
  deliberately: it leaves the write ORDER of the two registers unchanged, so every non-raising run is
  byte-identical on both stdout and stderr, and the frozen stdout-summary goldens
  (`TC-ArgusAgent-CLI-001-30` / `-31`) still pass unchanged. Closing test:
  **`TC-ArgusAgent-CLI-001-33`** (`tests/test_cli.py::test_cli_degrades_when_the_real_renderer_raises_on_the_way_out`)
  — it does NOT monkeypatch the raise: `run_audit` is stubbed to RETURN the one verdict FR16 cannot
  produce, and the REAL `render_ship_readiness` raises the REAL `ShipReadinessError` at the real call site,
  with no `--report-dir`. Demonstrated RED-first against the pre-fix `cli.py`, where it failed with an
  uncaught `argus.reports.plain_english.ShipReadinessError` escaping `main()`. Post-fix `main()` returns
  `1` with a secret-safe stderr line (no traceback, no host path, no source bytes).


---

## Deferred from: code review of story 8-4-tell-integrators-what-changed (2026-08-06)

Three items raised by code-review **iteration 2** and routed to `defer`. None is an AC failure for Story
8.4 — all 13 ACs were assessed MET and R1-R4 independently confirmed fixed. These are recorded so the
rot-check's remaining blind spots do not become invisible once the epic closes.

- **id:** `DF-8-4-B`
  **origin_story:** `8-4-tell-integrators-what-changed`
  **owner:** Delivery Orchestration
  **target_story:** the first story after 8.5 that edits `tests/test_release_note.py` (or Epic-9 `9-2`, whichever fires first)
  **category:** test-adequacy
  **severity:** 🟢
  The AC9 rot check pins what the code *renders* and the schema constants it *imports*, but pins **no prose**
  in `CHANGELOG.md`. Verified by mutation: deleting the entire *"Do I need to change anything?"* section, the
  entire *"Defaults: `--coverage-scope`"* section (the only warning that a pipeline must now pass
  `--coverage-scope repository`), the content-address *"your pinned artifact path moved"* warning, and the
  *"If you call `render_ship_readiness()` directly, it can now raise."* line each leave the whole module
  **green**; so does corrupting the published before/after artifact-bytes example. Every **consumer-action**
  claim in the note is therefore unpinned. AC9 enumerates what must be pinned and prose sections are not on
  that list, so this is hardening, not a breach — but it is the largest remaining route to the silent rot
  AC9 names as its own failure mode. **Suggested close:** a section-presence assertion over each `###`
  heading and each `- **You …** →` bullet, plus an equality check of the published bytes example against
  `CriticalSubsystemSet().model_dump(mode="json")` (verified byte-accurate today, so it would pass on
  arrival).

- **id:** `DF-8-4-C`
  **origin_story:** `8-4-tell-integrators-what-changed`
  **owner:** Delivery Orchestration
  **target_story:** the first story that edits `argus/reports/generator.py`'s critical-subsystems section
  **category:** documentation-completeness
  **severity:** 🟢
  `CHANGELOG.md:180-182` summarises the `### Critical subsystems below \`audited_deep\`` change (*"now
  renders on every row … its lead sentence is row-dependent"*) without quoting a before/after pair. Measured
  HEAD vs live over a non-empty critical set: HEAD emitted on **every** row `These withheld \`RELEASE_READY\`
  (FR16). Each must reach \`audited_deep\`, or be removed from the critical set with \`--exclude-critical\` if it
  is not genuinely critical.`; live emits a **row-dependent** lead (row 2: *"Not the reason for this verdict
  — that is stated in the callout above. Listed because the clause is still unmet …"*) **plus a wholly new
  FR4/DR-5 exemption paragraph on every row**. AC4's *"at minimum"* list is satisfied, so this is a
  completeness gap rather than a breach — but a consumer grepping `final-verdict.md` gets no quotable
  before/after for a paragraph that changed on every affected run.

- **id:** `DF-8-4-D`
  **origin_story:** `8-4-tell-integrators-what-changed`
  **owner:** Engineering
  **target_story:** the first story that edits `argus/cli.py::main`'s exception handling
  **category:** error-handling-precision
  **severity:** 🟢
  The `except ValueError` at `argus/cli.py:295-299` catches the **base** class while the comment beside it
  enumerates five typed subclasses. Pydantic's `ValidationError` is a `ValueError` subclass, so a genuine
  internal validation bug is reported as an expected, typed *"audit failed"* degradation instead of
  surfacing. **Pre-existing** — the same clause wrapped `run_audit` at HEAD; Story 8.4's widening added only
  the two `print` calls, so the newly-swallowed surface is `ShipReadinessError` plus stream/encoding errors.
  The encoding half is tracked separately as review finding **D1** on the story, which is a live decision,
  not a deferral. **Suggested close:** catch the named subclasses explicitly.

---

## Deferred from: dev of 8-5-re-derive-proof-evidence-matches-tool (2026-08-07)

**APPEND-ONLY.** Nothing above this line was edited, reordered or deleted. Story 8.5 (DR-10) re-derived the
three committed dogfood artifacts and both verdict-report directories so that no published Argus artifact
contradicts the FR16/FR4 contract Epic 8 shipped. The notes below record what that re-derivation did to
work already filed here.

### Progress note — DF-6-6-A / DF-7-2-A must now adjudicate against a DIFFERENT artifact

`minions-dogfood-proof.md` has been REGENERATED. Its §6 finding population is no longer the Story-7.2
Minions one, because the generator's `enumerate_tracked_sources` defaults to `scope_prefix="argus"` — it
audits **this repository's own `argus/` package**, and Minions source is not in this repository (RS-1).
The QA-Lead work `DF-7-2-A` describes is defined over the Minions population, so it must be read against
the preserved copy, not the live file.

Measured 2026-08-07 by running the shipped generators in place at HEAD `be9d744`:

| Adjudication class | Story-7.2 Minions run (preserved) | Re-derived Argus SELF-audit (live) |
|---|---|---|
| `cross_partition` | 332 | **2** |
| `hardcoded_secret` | 2289 | **22** |
| `orphan_code` | 285 | **77** |
| Total findings emitted | 2906 | **101** |
| Source files audited / LOC | 135 / 36712 | **69 / 18206** |
| Verdict | `NOT_READY_FOR_RELEASE` (exit `2`) | **`RELEASE_READY` (exit `0`)**, row `row_3_gates_met` |

- The Minions finding classes survive **only** at
  `minions-dogfood-proof-story-7-2-superseded.md` (RS-3 supersede-don't-erase; the original body is
  preserved verbatim beneath a hand-authored header). They can never be re-derived in this repository.
- The re-derived proof is a **SELF-audit of Argus** and says so in §1. It is a materially weaker evidence
  class than the independent run it supersedes, and it is not independent corroboration of anything.
- `DF-6-6-A` / `DF-6-6-A-P1` / `DF-6-6-A-P2` / `DF-7-2-A` all stay **OPEN** and are **not** rewritten. The
  only change is which file the human adjudication reads. The >=80%-precision gate stays PROVISIONAL:
  `protocol_cleared` was never passed `True` and the 6.5 marker was not flipped.

### Progress note — RS-4b, measured: 6 of 15 references CONSUMED, 9 remain

Story 8.5 consumed exactly the references that are **emitted into a committed `.md` artifact**; it left
every reference that only ever reaches a Python reader. Re-measured on this tree after the change with
`grep -rn "minions_core" argus/ --include=*.py` (excluding `__pycache__` and the Epic-9-owned
`argus/audit/minions_llm_adapter.py`):

- **CONSUMED (6 of 15)** — `dogfood/partition_plan.py:481, 490, 554` and `dogfood/proof_run.py:597, 609,
  610`, i.e. the three `AUTO-GENERATED by ...` banners, the `- Source files (tracked ...)` provenance line
  and the proof's scope paragraph. `argus/dogfood/partition_plan.py` now contains **zero** `minions_core`
  references. The banners now name the real modules `argus/dogfood/partition_plan.py` and
  `argus/dogfood/proof_run.py`, and a committed test (`TC-ArgusAgent-DOGFOOD-001-36`) resolves **every**
  path each artifact cites against the filesystem.
- **REMAINING (9 of 15)** — `audit/deep_audit.py:21` · `audit/ports.py:4` · `cost/budget_governor.py:15` ·
  `dogfood/proof_run.py:52, 53` (module docstring) · `dogfood/proof_run.py:632` (the `DogfoodProofError`
  operator message; this line was `:486` before the change — the line number moved, the string did not) ·
  `governance/escalation.py:35` · `store/envelope.py:25` · `verdict/prosecutor.py:36`. All nine are
  docstring / comment / operator-message prose; none reaches a committed artifact.
- Additionally, the bare-word *"Minions"* SUBJECT claims, which were never on RS-4b's list of 15 and were
  wholly Story 8.5's, are now gone from all three artifacts. Exactly one occurrence of the word survives
  in `minions-dogfood-proof.md`, in the sentence pointing a reader at the preserved Story-7.2 record — a
  true historical statement, not a claim that Minions source was audited.
- **RS-4b's sequencing constraint is now satisfied** (it required the sweep to FOLLOW Story 8.5). Its
  remaining scope is the 9 references above. RS-4b stays **OPEN** and its entry above is **not** rewritten.

### Inversion F5 — the originating operator command, re-run at BOTH scopes (2026-08-07)

The command that triggered the FR16/FR4 amendment (`sprint-change-proposal-2026-08-03.md`) recorded
`verdict=NOT_READY_FOR_RELEASE deep_ratio=11/28 blocking_findings=0`. Re-run after Stories 8.1-8.4, on the
working tree:

```
$ python -m argus.cli audit .                             # default scope (application)
verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=76
exit 0

$ python -m argus.cli audit . --coverage-scope repository # the population the symptom was measured under
verdict=INSUFFICIENT_COVERAGE deep_ratio=57/149 blocking_findings=0
exit 3
```

**The reported symptom — a blocking verdict carrying zero findings — is NOT reproducible at either
scope.** The whole-repository branch, which is the one that used to render `NOT_READY_FOR_RELEASE`, now
renders row 4 → `INSUFFICIENT_COVERAGE` / exit `3`. Recorded here so the evidence outlives the story file.

### New defers

- **DF-8-5-A** — The signed evidence bundle stamps a version token that contradicts the shipped package.
  `argus/dogfood/proof_run.py` defines `DOGFOOD_ArgusAgent_VERSION = "1.43.0"` and passes it to
  `build_evidence_bundle(..., argus_version=...)`, so it is written into the SIGNED, content-hashed
  evidence bundle as `argus_version`. Measured on this tree: `pyproject.toml:7` declares
  `version = "0.1.0"` and `argus/__init__.py:59` declares `__version__ = "0.1.0"`. The bundle therefore
  carries a provenance claim about which Argus built it that no shipped artifact supports — a falsehood
  inside signed evidence, which is a worse place for one than prose. **Deliberately NOT fixed by Story
  8.5:** changing the token changes the bundle's content hash, and therefore the content hash the proof
  artifact publishes as its signature; and the version token belongs with the packaging/release work that
  owns `pyproject.toml`. **Close =** source the value from `argus.__version__` instead of a module
  literal, re-derive the proof artifact in the same change, and update `TC-ArgusAgent-DOGFOOD-001-34`'s
  `assert DOGFOOD_ArgusAgent_VERSION == "1.43.0"` pin along with it rather than around it.
  - id: DF-8-5-A
  - origin_story: 8-5-re-derive-proof-evidence-matches-tool
  - owner: Delivery Orchestrator
  - target_story: 9-2-ship-distribution-another-repo-can-actually-resolve
  - category: provenance-correctness
  - severity: 🟠

- **DF-8-5-B** — The committed-artifact rot checks re-break on any commit that changes `argus/**`
  composition, and nothing warns before they do. Three tests compare a committed `.md` against a LIVE
  derivation over the working tree: `TC-ArgusAgent-DOGFOOD-001-03` (asserts `Unit count: N` and each
  `partition_id[:12]`), `-06` (asserts `str(sized_ceiling)`), and `-20` (asserts the live verdict token +
  exit code). **Measured mechanism:** a `partition_id` is a sha256 over its unit's sorted member paths, so
  adding, removing or merely re-balancing one file under `argus/` changes it; `sized_ceiling` is
  `total_credits × 5/4` where `total_credits` folds `files_indexed + python_files + detector_passes`, so
  it moves with the file count; the verdict moves with the ledger. **Measured history:** `-03` and `-06`
  were RED across four consecutive commits (`ae5f00c` … `be9d744`) before this story, and `-20` joined
  them at `be9d744` when the Epic-8 delta moved the live verdict. Story 8.5's own work had to re-derive
  these artifacts **three times** for the same reason — every edit to `argus/dogfood/*.py` changed
  `total_loc` and the figures derived from it. The failure mode is therefore structural, not incidental:
  the checks are correct, but they make every `argus/**` change a two-step change, and a developer who
  does not know that reads three unexplained reds. **Close =** either a documented regeneration entry
  point named in the failure message of all three assertions, or a CI step that regenerates and fails on
  a diff — so the remedy is discoverable from the red output. Do **not** close it by loosening an
  assertion.
  - id: DF-8-5-B
  - origin_story: 8-5-re-derive-proof-evidence-matches-tool
  - owner: Engineering
  - target_story: the first story after Epic 9 that edits `tests/test_dogfood_plan.py` or `tests/test_dogfood_proof.py`
  - category: developer-experience
  - severity: 🟢

---

## Deferred from: code review of 8-5-re-derive-proof-evidence-matches-tool, iteration 1 (2026-08-07)

**APPEND-ONLY.** Nothing above this line was edited, reordered or deleted. Review iteration 1 returned
`CONCERNS` with five **Low** findings. Three were fixed in code (the unmatched `argus/tests/` exclusion
prefix plus the directory-blind citation guard; the `0`-as-absent live-sizing sentinel; the fatal-on-any-
read-failure critical-set read-back and its missing >1-match guard). The remaining two are recorded here,
because the review's own remedy for each was a ledger id rather than a code change.

### New defers

- **DF-8-5-C** — The published proof artifact states a precision-corpus figure of **N=0** that is measurably
  wrong. `argus/dogfood/proof_run.py:764-765` calls `precision_gate_status_for(precision=Fraction(0, 1),
  n=0, provisional=True, ...)` **unconditionally** — the arguments are literals, not a measurement of the
  corpus — and the resulting string is rendered verbatim into `minions-dogfood-proof.md:87` as
  *"precision=0/1 over FINDINGS not repos; N=0 labeled cartridges populated, floor N=5"*. **Measured today
  by calling the shipped registry** (`tests/cartridges/_registry.py`, imported and executed, not read off a
  document): `distinct_rule_class_count() == 5` and `populated_planted_defect_count() == 7`. So the
  artifact publishes `N=0` about a corpus that holds 5 distinct rule classes across 7 populated rows.
  **Direction matters:** the figure **UNDERSTATES** — it makes the provisional gate look further from its
  `N>=5` floor than it is, so it cannot be read as an over-claim and it cannot make a gate look cleared. It
  is nonetheless a number in a proof artifact that no one measured, which is the exact defect class Epic 8
  exists to delete. **Deliberately NOT fixed by Story 8.5:** the story's own Known-red carve-out directs
  *"Do NOT fix it here … File it (AC8)"*, and wiring the real counts touches the 6.5/6.6 precision surface
  (`precision_gate_status()` / the cartridge registry) that no AC in Epic 8 owns; changing the rendered
  string also changes the committed artifact, so it must land with a regeneration. **Recorded because the
  decision was previously only in a closing story's Completion Notes**, and `DF-6-6-A-P1` / `DF-7-2-A`
  record the corpus counts but say nothing about the published artifact rendering `N=0` — verified at
  `deferred-work.md:362-394`. **Close =** pass the measured `distinct_rule_class_count()` /
  `populated_planted_defect_count()` (or an explicit "corpus not consulted by this run" token) into
  `precision_gate_status_for`, regenerate `minions-dogfood-proof.md` in the same change, and keep
  `protocol_cleared=False` and the `provisional=True` framing untouched — this is a correctness fix to a
  reported number, never a step toward clearing the gate.
  - id: DF-8-5-C
  - origin_story: 8-5-re-derive-proof-evidence-matches-tool
  - owner: Engineering
  - target_story: the first story that edits the 6.5/6.6 precision surface (`argus/precision/**` or the
    cartridge registry) after the human `DF-7-2-A` adjudication
  - category: published-figure-correctness
  - severity: 🟢

- **DF-8-5-D** — `argus/dogfood/proof_run.py` carries five responsibilities in one module and is now
  **1196 / 1200 lines (4 lines of headroom)** against the NFR-M1 ceiling. **Measured composition:** module
  constants + the typed `DogfoodProofError`, five frozen value dataclasses (`AdjudicationRow`,
  `CostSummary`, `ScopeDisclosure`, `CriticalClauseDisclosure`, `DogfoodProofRun`), the impure
  git/snapshot/store shell (`enumerate_tracked_sources`, `materialize_snapshot`,
  `_read_critical_subsystem_set`, `run_dogfood`, `build_dogfood_proof`), the pure cost accountant
  (`cost_summary`, `adjudication_rows`), and ~390 lines of pure renderer (`render_proof_markdown` and its
  six `_render_*` / `_*_clause` helpers). That is an SRP/SoC violation held together only by the AR8
  pure/impure narration in its docstring. It grew 749 → 1154 in Story 8.5 and 1154 → 1196 across review
  iteration 1; **the next edit of any size breaches NFR-M1**, which is why this is filed rather than
  observed. **The extraction was considered and rejected TWICE and the rejection stands for Story 8.5:**
  AC13 does not authorise a restructure, and the final story of an epic whose subject is "no surprises" is
  the wrong place for one. **The blocker previously recorded (a circular import) is softer than stated and
  is corrected here:** extracting the pure renderers to `argus/dogfood/proof_render.py` needs the five
  dataclasses moved to a sibling (e.g. `argus/dogfood/proof_types.py`) and **re-exported** from
  `proof_run.py`, which preserves the public import surface — every existing
  `from argus.dogfood.proof_run import ...` keeps working — with no cycle. **A second, MEASURED constraint
  the closing story discovered:** the dogfood plans over `argus/**` itself, so adding a module changes the
  partition input set, and `TC-ArgusAgent-DOGFOOD-001-18` pins `unit_count >= 3` while this tree yields
  **exactly 3** — the extraction must therefore regenerate all three committed dogfood artifacts in the same
  change and re-measure the unit count, and a drop to 2 units is a finding to report, never a licence to
  loosen the assertion. **Close =** perform that extraction with the re-export shim, regenerate the three
  artifacts, and keep both modules under 1200 lines.
  - id: DF-8-5-D
  - origin_story: 8-5-re-derive-proof-evidence-matches-tool
  - owner: Engineering
  - target_story: the first story that edits `argus/dogfood/proof_run.py` for any reason
  - category: maintainability
  - severity: 🟠

---

## Deferred from: 9-2-ship-distribution-another-repo-can-actually-resolve (2026-08-08) — THE LAST STORY IN THE PLAN

**APPEND-ONLY.** Nothing above this line was edited, reordered or deleted.

> **Read this section differently from every other one in this register.** Story 9.2 is the last story of
> Epic 9 and the last story in the entire ArgusAgent plan. **There is no successor story to inherit a
> deferral.** Every `target_story` below that names "the first story that…" is now a conditional pointing at
> a story that does not exist and may never exist. Where that is the case it is said explicitly, because an
> item that reads like a handoff and is in fact abandoned is worse than an item marked abandoned: the first
> costs someone a search, the second costs them nothing. §5 of the Epic-8 retrospective established that
> items framed as handoffs evaporate while items attached to a named deliverable land; this section is
> written to make the evaporation visible rather than to prevent it, which is not in a story's power.

### Closed by this story

- **DF-8-5-A — CLOSED.** `argus/dogfood/proof_run.py` now reads
  `DOGFOOD_ArgusAgent_VERSION = _ARGUS_VERSION` with `from argus import __version__ as _ARGUS_VERSION`;
  the module literal `"1.43.0"` is gone. **Closing evidence, measured in place, not asserted:**
  (a) RED-first, through the shipped path — an evidence bundle was built with the pre-fix constant and
  persisted, and the resulting `.argus/state/<hash>.json` read
  `envelope.argus_version = "0.1.0"` while `envelope.payload.argus_version = "1.43.0"` (AGREE = False);
  post-fix the same path yields `0.1.0` on both levels (AGREE = True).
  (b) The dogfood bundle content hash moved
  `a1e76c01cbd29241a928f71b724b4c4c01d1211e0a4ae8a6e266386f811e0c0e` (which matched the committed
  `minions-dogfood-proof.md:57` signature line exactly, re-derived rather than read off the document) →
  `b3588816088920936de7a3fea17eaba747f7ad3c1af1ff93b0f4f4474acb6dc6` from the version fix alone →
  `da17b0fe19d121a4414ea542e8b9061abc73eca549aadb45b178cfc1fced89fc` after the DF-8-5-D extraction
  changed the audited population. The artifact was regenerated so it publishes the last of these.
  (c) `TC-ArgusAgent-DOGFOOD-001-34` was updated THROUGH the fix — it now asserts
  `DOGFOOD_ArgusAgent_VERSION == argus.__version__` rather than a second copy of the value — and its
  adjacent comment, which claimed the provenance was "the pyproject version token" while the code carried
  a literal that disagreed with pyproject, was corrected.
  (d) New enumerated guards: `TC-ArgusAgent-DOCS-001-14` (the three version-bearing surfaces agree) and
  `TC-ArgusAgent-DOCS-001-15` (an AST sweep of all 71 `argus/**` modules permits exactly ONE semver
  literal, at `argus/__init__.py`), so a fourth version literal goes RED.
  - id: DF-8-5-A
  - closed_by: 9-2-ship-distribution-another-repo-can-actually-resolve
  - closed_on: 2026-08-08
  - status: CLOSED

- **DF-8-5-D — CLOSED.** `argus/dogfood/proof_run.py` was split into three modules with a re-export shim.
  **Measured line counts:** `proof_run.py` 1196 → **679**, new `argus/dogfood/proof_render.py` **447**,
  new `argus/dogfood/proof_types.py` **207**; all three under the NFR-M1 1200 ceiling. (The three do not
  sum to 1196 + headers: the DF-8-5-A fix added 3 lines, the shim adds an import block, and each new
  module carries its own docstring and `__all__`.)
  **Corrections to this entry's own text, measured rather than inherited:**
  (a) The entry estimates the renderer at "~390 lines"; **measured it is 391** (`:809-1199` of the
  pre-split file).
  (b) The entry says "the next edit of any size breaches NFR-M1". The DF-8-5-A fix is **+3 lines net**
  and left the module at **1199/1200** — it FIT. The NFR-M1 fence did **not** force this extraction; the
  `target_story` did ("the first story that edits `argus/dogfood/proof_run.py` for any reason"), together
  with the absence of any later story. This correction matters because the fence narrative implies the
  work was unavoidable; it was not — it was *chosen*, on the ledger's instruction and because deferring it
  here means dropping it.
  (c) The entry warns that `unit_count` may drop to 2. **It did not: it held at 3**, measured on the real
  tree after the extraction. What moved instead was **every one of the three `partition_id`s** —
  `2c0f52f60457`/`681c496d09ed`/`973f3f199d1c` → `085854c90586`/`477ef77d7b65`/`bde14bbf3bcf` — because
  a `partition_id` is a sha256 over its unit's sorted member paths and adding two modules re-balanced all
  three units. A simulation over an isolated copy had predicted only ONE id would move; the real split
  moved three. The prediction was directionally right and numerically wrong, which is exactly why the
  measurement was repeated on the real tree.
  **Closing evidence:** the pure-move was proven by rendering the SAME `DogfoodProofRun` before and after
  the extraction and comparing bytes — **9927 → 9927 bytes byte-identical** for a real dogfood run, and
  **55101 → 55101 bytes byte-identical** across six synthetic runs covering every renderer branch (scope
  present/absent, critical clause not-captured / not-retrieved / vacuous / non-empty / not-satisfied,
  ceiling pair with and without a live sizing). New tests `TC-ArgusAgent-DOGFOOD-001-45`..`-48` pin the
  `__all__` import surface (fails on removal as well as on a broken import), the re-export IDENTITY
  (`proof_run.X is proof_types.X` — `==` would not catch a fork), the three line counts, the structural
  purity of both new modules, and the externalization-guard text.
  **One deliberate content change, disclosed rather than folded into "pure move":** the artifact's
  provenance banner now reads ``AUTO-GENERATED by `argus/dogfood/proof_render.py`
  (`render_proof_markdown`, re-exported from `argus/dogfood/proof_run.py`, which orchestrates the run)``.
  Leaving it naming only `proof_run.py` would still have resolved — and would still have pointed a reader
  at a file that no longer contains the generator. This is the ONLY difference between the pre- and
  post-extraction renders; it was made after the byte-identity proof was captured, not before.
  **Second disclosed move:** `DOGFOOD_EXTERNALIZATION_GUARD` moved from `proof_run.py` to
  `proof_render.py` because the renderer is its only consumer and leaving it behind would have forced
  `proof_render → proof_run`, i.e. the cycle the shim exists to avoid. Its text is byte-identical and is
  now pinned by an equality assertion (`TC-ArgusAgent-DOGFOOD-001-48`), so Story 9.2 / AC12's "unchanged"
  is verified rather than asserted.
  - id: DF-8-5-D
  - closed_by: 9-2-ship-distribution-another-repo-can-actually-resolve
  - closed_on: 2026-08-08
  - status: CLOSED

- **DF-8-4-A — CLOSED.** `action.yml`'s exit-code map is now explicit over the complete space
  `{0, 2, 3, 1, anything else}`. Exit `1` has its own arm and renders `verdict=AUDIT_FAILED`, and the
  catch-all renders the same failure token rather than a verdict token, so an unmapped future exit code
  can never surface as an assessment. **Vocabulary decision and why:** `AUDIT_FAILED` was chosen over
  failing the step outright because a composite action that dies takes the consumer's ability to branch
  with it — a caller that wants to tolerate a tooling failure and a caller that wants to block on one need
  different behaviour, and only the caller knows which they are. A new `assessed` output (`true` for
  0/2/3, `false` otherwise) gives them the boolean without string-matching, and the `1`/unmapped arms emit
  a GitHub `::error::` annotation so the failure is visible even when the step is tolerated.
  `outputs.verdict` and `outputs.exit-code` descriptions were rewritten; they had documented only three
  codes and never mentioned `1`. `strict` stays `"false"` (see the fenced note below).
  - id: DF-8-4-A
  - closed_by: 9-2-ship-distribution-another-repo-can-actually-resolve
  - closed_on: 2026-08-08
  - status: CLOSED

- **RS-4b — CLOSED.** All nine remaining `minions_core` references under `argus/**` were swept:
  `audit/deep_audit.py:21`, `audit/ports.py:4`, `cost/budget_governor.py:15`, `dogfood/proof_run.py:52`,
  `:53`, `:666` (the operator-visible `DogfoodProofError` message), `governance/escalation.py:35`,
  `store/envelope.py:25`, `verdict/prosecutor.py:36`. **The stale line reference in this register's own
  RS-4b entry (`proof_run.py:632`, corrected to `:666` by AI-E8-7) is closed out by the sweep rather than
  re-filed with a fourth line number** — the reference no longer exists at any line.
  **One of the nine was not merely stale but FALSE:** `cost/budget_governor.py:15` claimed
  "AR7 (reuse ``minions_core.cost.budget_guardrails`` BY IMPORT)" while the module actually imports
  `argus.shared.budget_guardrails` (vendored by the repo separation). It now names the real module.
  A tenth, identical false claim in `tests/test_no_web_imports.py:89` was corrected in the same pass and
  is disclosed here because it is outside RS-4b's stated `argus/**` scope.
  **The two decoys were left standing** — `argus/audit/minions_llm_adapter.py:5` and `:29` are Story 9.1's
  TRUE NEGATIVE statements about a dependency that no longer exists, and deleting them would delete the
  documentation of RS-1/IN-2.
  **Closing evidence:** `grep -rn "minions_core" argus/ --include=*.py` (excluding `__pycache__`) now
  returns exactly those two lines and nothing else. Two new guards make it an enumerated space:
  `TC-ArgusAgent-STORE-001-109` walks all 71 modules and fails on any occurrence outside an allowlist that
  contains exactly `argus/audit/minions_llm_adapter.py` (and fails if the allowlisted count changes, so
  the negative statements cannot be silently deleted either), and `TC-ArgusAgent-STORE-001-110` requires
  every surviving occurrence to sit in a line that DENIES the dependency — so the allowlist cannot be
  repurposed into a smuggling route for a real provenance claim.
  **Bare-word "Minions" (NOT `minions_core`, and NOT RS-4b):** bounded to `argus/dogfood/**` per the
  story's D10 and swept there — measured per file, `proof_run.py` 13 → 1, `partition_plan.py` 6 → 0,
  `dogfood/__init__.py` 2 → 0 (20 removed). Historical statements that are TRUE were kept (the superseded Story-7.2 run over
  the Minions platform really did happen, and `proof_render.py` still cites it). The remaining
  occurrences elsewhere under `argus/**` are explicitly OUT OF SCOPE and are filed as `DF-9-2-B` below.
  - id: RS-4b
  - closed_by: 9-2-ship-distribution-another-repo-can-actually-resolve
  - closed_on: 2026-08-08
  - status: CLOSED

- **DF-8-4-B — PARTIALLY CLOSED (heading half closed; bytes-example half explicitly left OPEN).**
  Its `target_story` reads "the first story after 8.5 that edits `tests/test_release_note.py` (or Epic-9
  `9-2`, whichever fires first)"; **both clauses fired**, because AC6 had to update
  `TC-ArgusAgent-DOCS-001-01`'s `"## Unreleased"` pin. **Closed:** `TC-ArgusAgent-DOCS-001-16` registers
  every `###` section of `CHANGELOG.md` as an enumerated, ORDERED space — a removed section fails, an
  unregistered added section fails, and a reordering fails. **Deliberately NOT closed:** the suggested
  bytes-example equality check. The note already carries byte-for-byte equality assertions over the
  surfaces that matter — the FR16 decision table, the ship-readiness headlines, the `final-verdict.md`
  callouts and the persisted assurance sentences, via `TC-ArgusAgent-DOCS-001-03`..`-06` — so a second
  generic bytes check would add duplication rather than coverage. **This half now has no owner** (see
  below).
  - id: DF-8-4-B
  - closed_by: 9-2-ship-distribution-another-repo-can-actually-resolve (heading half only)
  - closed_on: 2026-08-08
  - status: PARTIALLY CLOSED — bytes-example half OPEN and UNOWNED

### Opened by this story

- **DF-9-2-A** — 🟠 **Five shipped module files cannot be imported from the built distribution.**
  MEASURED, not inferred: `python -m build` produced `argus_agent-0.1.0.tar.gz` (75 files) and
  `argus_agent-0.1.0-py3-none-any.whl` (76 entries = **71** `argus/**` modules + 5 `dist-info`). Each of
  those 71 modules was imported in its own clean subprocess with the wheel's contents on `sys.path` and
  this repository **removed** from it: **66 of the 71 import. Five do not:**
  `argus/precision/__init__.py`, `argus/precision/replay_harness.py`, `argus/dogfood/proof_types.py`,
  `argus/dogfood/proof_render.py`, `argus/dogfood/proof_run.py` — all with
  `ModuleNotFoundError: No module named '_registry'`. **Single cause:**
  `argus/precision/replay_harness.py:87-90` inserts `<repo>/tests/cartridges` onto `sys.path` and
  unconditionally imports `_registry` from it; `tests/` is not in the distribution and should not be.
  Everything else is that one import reached transitively (`argus/precision/__init__.py` re-exports it,
  and the dogfood modules import `MatchKey` from it).
  ⚠️ **Figure corrected at code-review iteration 1 (2026-08-09), stated rather than quietly swapped.**
  This entry first read *"65 of the 69 shipped modules import"* and named only four broken modules. `69`
  was the **pre-split** module count — the tree has been 71 since this same story's AC8 landed — and the
  four-module list omitted `argus/precision/replay_harness.py`, the module that actually contains the
  offending import, while the committed pin `_NOT_IMPORTABLE_FROM_DISTRIBUTION` correctly listed five.
  The replacement figures above were **re-measured from scratch**, not re-derived from the old sentence.
  The disposition below is unchanged: only the numbers were wrong.
  **Pre-existing, verified not assumed:** the identical import exists at HEAD `7be90f7`
  (`git show 7be90f7:argus/precision/replay_harness.py`), and the pre-split `proof_run.py` imported
  `argus.precision.replay_harness` at its line 127. The Story-9.2 split did not create the defect and did
  not widen the consumer surface — the two new modules fail only because they re-export what already
  failed. **Nothing that imported before imports less now.**
  **Not fixed here, deliberately:** `argus/precision/**` is FENCED by Story 9.2 / AC15, and the fix is a
  behavioural change to the precision substrate inside a release story with no mandate over it.
  **Impact is bounded and stated:** IN-1/IN-3 need `argus audit`, and the whole CLI path imports and RUNS
  from the wheel (`argus --help` exit `0`; `argus audit <fixture>` → `RELEASE_READY`, exit `0`, executed
  from a working directory that is not this repository). What a consumer cannot do from the distribution
  alone is re-run Argus's own dogfood proof generator, which is a self-audit tool, not a consumer feature.
  README.md and CHANGELOG.md both state this split explicitly rather than leaving it to be discovered.
  **Close =** make the registry import lazy or optional in `replay_harness.py` (import inside the function
  that needs it, or degrade to an explicit "no labelled corpus available" state), then re-measure the
  importable count from a freshly built wheel and update `_NOT_IMPORTABLE_FROM_DISTRIBUTION` in
  `tests/test_release_preflight.py` — which is pinned in BOTH directions, so a fix that leaves the record
  stale goes RED.
  - id: DF-9-2-A
  - origin_story: 9-2-ship-distribution-another-repo-can-actually-resolve
  - owner: Engineering
  - target_story: **NONE — no story exists after 9.2.** This needs a named human to schedule it.
  - category: packaging-correctness
  - severity: 🟠

- **DF-9-2-B** — 🟢 **Bare-word "Minions" subject claims outside `argus/dogfood/**`.** Story 9.2's D10
  bounded the subject-claim sweep to `argus/dogfood/**` (where the modules were being rewritten anyway).
  **Measured:** the bare word ran 45 times across 17 `argus/**` modules at HEAD `7be90f7` and runs **25
  times across 15** now — 20 removed, all inside `argus/dogfood/**` (`proof_run.py` 13 → 1,
  `partition_plan.py` 6 → 0, `dogfood/__init__.py` 2 → 0), with 2 kept there deliberately because they
  are TRUE historical statements about the superseded Story-7.2 run (`proof_run.py:5`,
  `proof_render.py:71`). ⚠️ The story context stated 44 across 17; re-measured in place it is 45. Of the
  25 that remain, 2 are those deliberate keeps and **23 are elsewhere under `argus/**`** — historical
  narration in
  modules Story 9.2 did not touch (e.g. `cost/budget_governor.py`'s "the Minions `BudgetPolicy` fields are
  `float`", which is a true statement about the vendored guardrail's shape). They are not falsehoods of the
  RS-4b class and none of them names a package that no longer exists; they are simply subject language
  inherited from the monorepo. Sweeping them is an unbounded prose pass, which is why RS-4b was scoped away
  from them in the first place. **Close =** a bounded prose pass that reads each one and decides whether it
  is a true historical statement (keep) or a false subject claim (rewrite) — never a blanket replace.
  - id: DF-9-2-B
  - origin_story: 9-2-ship-distribution-another-repo-can-actually-resolve
  - owner: Engineering
  - target_story: **NONE — no story exists after 9.2.**
  - category: documentation-accuracy
  - severity: 🟢

- **DF-9-2-C** — 🟢 **`argus/dogfood/__pycache__/*.pyc` are tracked in git.** Measured with
  `git ls-files argus/dogfood/`: three compiled `.cpython-312.pyc` files are committed even though
  `.gitignore:2` lists `__pycache__/` (the ignore rule cannot affect already-tracked paths). They do not
  reach the partition plan — `enumerate_tracked_sources` filters by `_SOURCE_SUFFIXES`, which is why
  `source_file_count` is 71 and not 74 — and they were not added or touched by Story 9.2. Filed rather
  than fixed because `git rm --cached` on tracked paths is a repository-hygiene change outside this
  story's scope, and because a silent deletion of tracked files during a release story is precisely the
  kind of unannounced side effect Epic 8 exists to prevent. **Close =** `git rm --cached` the three paths
  in a change that says so.
  - id: DF-9-2-C
  - origin_story: 9-2-ship-distribution-another-repo-can-actually-resolve
  - owner: Engineering
  - target_story: **NONE — no story exists after 9.2.**
  - category: repository-hygiene
  - severity: 🟢

### Re-recorded as OPEN and, after this story closes, UNOWNED

> Each of the following keeps its original entry text, unedited. What is recorded here is that its
> `target_story` no longer resolves to anything. This is the honest outcome of ending a plan with items in
> the register, and it is materially better than performing a large risky refactor inside a release story
> to avoid writing an uncomfortable sentence (Story 9.2 / D11).

- **DF-8-5-C — OPEN, and knowingly REPUBLISHED unchanged by this story.** `proof_run.py`'s
  `precision_gate_status_for(precision=Fraction(0, 1), n=0, provisional=True, ...)` literals were
  re-rendered verbatim into the regenerated `minions-dogfood-proof.md`, which again publishes
  "N=0 labeled cartridges populated, floor N=5" while the shipped registry measures
  `distinct_rule_class_count() == 5` and `populated_planted_defect_count() == 7`. **It UNDERSTATES**, so it
  makes the provisional gate look FURTHER from its floor than it is and can never make a gate look
  cleared. Not fixed here because its `target_story` names the 6.5/6.6 precision surface **after the human
  `DF-7-2-A` adjudication**, which has not occurred, and because `argus/precision/**` is fenced by AC15.
  **Reprinting it while naming it is the honest act; reprinting it silently was the failure mode.**
  Owner after 9.2: **none.**
- **DF-8-5-B — OPEN.** Its `target_story` reads "the first story **after Epic 9**", so it was never
  Story 9.2's to close — but 9.2 hit exactly the pain it describes: `TC-ArgusAgent-DOGFOOD-001-03` and
  `-06` were verified RED against the committed artifacts before regeneration (all three live
  `partition_id`s absent from the committed plan; `443` absent from the committed budget plan) and green
  after. **Whether 9.2 made the remedy discoverable: NO, and deliberately so.** The entry asks for a named
  regeneration entry point in the failure message of all three assertions, or a CI regenerate-and-diff
  step. Neither was added: the first edits assertion text in tests this story must not weaken, and the
  second adds a CI job with a ~2-minute dogfood run to a release story. What 9.2 DID add is a documented
  regeneration sequence in its story record (source edits → tests → stage → regenerate → re-run), which is
  a story artifact and not the discoverable-from-red-output remedy the entry asks for. Owner after 9.2:
  **none.**
- **DF-8-4-C** and **DF-8-4-D** — OPEN. Their targets (`reports/generator.py`'s critical-subsystems
  section; `cli.py::main`'s exception handling) are inside Story 9.2's AC15 fence and were not opened.
  Owner after 9.2: **none.**
- **DF-8-2-A**, **DF-8-3-A**, **DF-8-3-C** — OPEN, and all three gate on the `argus/pipeline.py`
  extraction. Measured today: `pipeline.py` is **1199 / 1200 lines**, one line from the NFR-M1 ceiling.
  Story 9.2 FENCED it (D11) — the extraction is a second unrelated restructure inside a release story, it
  touches the module that produces every verdict, and nothing in IN-0 requires it. **Consequence, stated
  plainly: the next edit of any size to `pipeline.py` breaches NFR-M1, and there is no story queued to
  perform the extraction.** Owner after 9.2: **none.**
- **DF-6-6-A**, **DF-6-6-A-P1**, **DF-6-6-A-P2**, **DF-7-2-A** — OPEN and NOT rewritten by this story.
  `DF-7-2-A` is the human Eng-Lead + QA-Lead TP/FP adjudication that is the only thing that can clear the
  ≥80%-precision gate. It has not happened. Owner: a named human, as it always was.
- **DF-6-7-A** — OPEN (HITL wiring), untouched.

### The register as a whole, after Story 9.2 closes

**Nobody is looking after this.** Epic 9 is the last epic; there is no Epic 10, no next sprint in this
tracker, and no story whose `target_story` clause will fire. Twelve entries remain OPEN
(`DF-6-6-A`, `-P1`, `-P2`, `DF-6-7-A`, `DF-7-2-A`, `DF-8-2-A`, `DF-8-3-A`, `DF-8-3-C`, `DF-8-4-C`,
`DF-8-4-D`, `DF-8-5-B`, `DF-8-5-C`), plus the bytes-example half of `DF-8-4-B` and the three items this
story opened (`DF-9-2-A`, `DF-9-2-B`, `DF-9-2-C`). **Each needs a named human to schedule it or an
explicit decision to abandon it.** Neither is a thing an autonomous story can do, and pretending
otherwise by re-targeting them at a hypothetical future story would be the evaporation §5 of the Epic-8
retrospective described.

**H0 is NOT in this register and was NOT filed by this story.** `epics.md:1693-1699` records that no story
in this breakdown owns filing the Minions-repo handoff H1–H4, that H0 is **UNOWNED**, and that "a handoff
nobody files is a handoff that does not exist". It was escalated as readiness-report **F5 (LIVE)** on
2026-08-03 and re-raised as **AI-E8-10** on 2026-08-08. Story 9.2 did not create it, claim it, or close
it. Two related facts are restated once so they are not lost when this repository's plan closes:
assumption **A5** is ⚠️ **Unsupported** — after the FR16/FR4 amendment the Minions repository is expected
to land on row 4 → exit `3`, which still fails an unconfigured blocking CI gate, so **H3** needs a policy
decision before that gate can be made blocking — and **IN-1** must be an optional extra
(`minions[argus]`-shaped), never a base dependency, because Minions declares `dependencies = []`.

---

## Deferred from: code review of story 9-2-ship-distribution-another-repo-can-actually-resolve (2026-08-09)

Appended by the code-review gate, iteration 1. Append-only: nothing above this heading was edited,
reordered or deleted. One item only — every other review finding is an actionable `[Review][Patch]`
item inside the story file and is being fixed in this story, not deferred.

- **DF-9-2-D** — 🟢 **`action.yml` interpolates a consumer-supplied action input into shell source.**
  `action.yml:127` runs `if [ "${{ inputs.strict }}" = "true" ]`, expanding the composite action's
  `strict` input into the `run:` body before `bash` parses it. A consumer who sets `strict` to a crafted
  value executes shell in the calling workflow's job. **Pre-existing and out of the 9.2 delta, verified
  not assumed:** the line is byte-identical to HEAD `7be90f7`; Story 9.2 rewrote the exit-code `case`
  arm immediately above it (DF-8-4-A / AC10) and did not touch this line. Deferring it was the correct
  scoping call — widening a release story into an unrelated hardening pass on the consumer-facing action
  is the scope creep AC15's fences exist to prevent.
  **Close =** bind the input through `env:` (`env:\n  STRICT: ${{ inputs.strict }}`) and compare
  `"$STRICT"`; do the same sweep over every other `${{ inputs.* }}` occurrence in `action.yml` in one
  pass, and add a guard test that fails on any `${{ inputs.` appearing inside a `run:` block.
  - id: DF-9-2-D
  - origin_story: 9-2-ship-distribution-another-repo-can-actually-resolve (code review, iteration 1)
  - owner: Engineering
  - target_story: **NONE — no story exists after 9.2.** Needs a named human to schedule it, exactly as
    DF-9-2-A/B/C do.
  - category: security-hardening
  - severity: 🟢

## Deferred from: repository audit (2026-08-09)

- **DF-AUD-APAA-C** — A release status was asserted over a gate that had never executed.
  `sprint-change-proposal-2026-07-28.md:63` records *"Upgraded from NEEDS TARGETED REWORK to
  READY FOR RELEASE!"*, evidenced by a LOCAL pytest run (`:55`, "916 PASSED"). Item 6 of that
  same proposal CREATED `.github/workflows/audit-ci.yml`; its only run on `master`
  (`30774175196`) is `failure`, dying at the `bandit` step in 40s — before pytest was ever
  reached — because `bandit -r argus` exits 1 on any severity and this tree carries 18 benign
  Low findings. A second, independent break: `pytest --cov` was invoked while `pytest-cov` was
  absent from the `[dev]` extra, so the `--cov-fail-under=80` gate could not run either. Both
  were repaired 2026-08-09 and a clean-venv reproduction of every step passes on 3.12; the
  repair is NOT the deferred item. Close = adopt the Story 10.1 evidence standard: a release
  status cites an executed gate (CI run id) or is recorded NOT ESTABLISHED, and the 2026-07-28
  record is corrected in place, dated and reasoned (§3.4 evidence immutability — never a
  silent rewrite).
  - id: DF-AUD-APAA-C
  - owner: Delivery Orchestrator
  - target_story: 10-1-release-status-must-cite-evidence
  - category: process
  - severity: 🟠

- **DF-AUD-APAA-D** — Multi-language AST grounding shipped in V1 while every specification
  still designates it V2, and its determinism provenance is wrong for non-Python repos. The
  capability entered via `sprint-change-proposal-2026-07-28.md:18` (*"user intent requested…
  multi-language auditing capability"*) with no story and no PRD/architecture amendment; PRD
  L23/L180 and architecture L220/L237 were never updated. Consequences: (a) the V2 roadmap
  double-counts delivered work; (b) `index/ast_index.py:311` records ONE `grammar_version`
  resolved from `tree-sitter-python` for a 10-language index, so a Go/Rust/JS grammar change
  would not move the R3 cache key — the identical silent-cache-staleness failure mode
  DF-5-1-A already flags for `prompt_template_version`, and the architecture's R3 key
  (L77-78, L201) was DESIGNED for a single grammar, making this a design change not a defect
  fix; (c) the `[languages]` extra is documented in neither README nor CHANGELOG, so a
  consumer cannot discover it. Drift direction is an UNDERSELL — no false capability claim
  reached a consumer. Close = Story 10.2: amend PRD + architecture (incl. R3), make
  provenance per-grammar BEFORE the Epic-5 store is wired (free now, needs a
  `CACHE_KEY_SCHEMA_VERSION` bump and migration later), and document the extra.
  - id: DF-AUD-APAA-D
  - owner: Engineering Lead
  - target_story: 10-2-multi-language-grounding-is-v1-in-the-specs
  - category: process
  - severity: 🟡

- **DF-AUD-APAA-E** — Four CLI flags are accepted by the shipped parser and specified
  nowhere. `--passes`, `--skip-pass`, `--ignore-path`, `--ignore-pattern` have ZERO occurrences
  across epics, stories, PRD, addendum, both prior change proposals, CHANGELOG and README,
  while FR30 and architecture L226 specify four parameters and Story 1.7 declares the flag
  names LOCKED. They entered in the root commit `084c6a7` (the 426-file separation seed) and
  `b05fa4c`, so no gate ever saw them. They were also entirely INERT until 2026-08-09 — every
  production call site dropped the `request` argument — so no consumer can depend on their
  behaviour and neither blessing nor removal is a behavioural break. Two of them
  (`--ignore-path`, `--ignore-pattern`) suppress SECURITY findings with no threat model. Close
  = Story 10.3: rule on each flag (bless with ACs + CHANGELOG entry, or remove), require a
  threat model before blessing either suppression flag, and pin parser-vs-contract equality
  with a test so the two cannot diverge again.
  - id: DF-AUD-APAA-E
  - owner: Governance Owner
  - target_story: 10-3-invocation-contract-says-what-the-cli-accepts
  - category: governance
  - severity: 🟡

- **DF-AUD-APAA-F** — A grammar that fails to LOAD is reported as a grammar that is MISSING.
  `index/ast_index.py:266` catches `(ImportError, Exception)` and returns `None`, so an
  uninstalled grammar and an installed-but-broken one (ABI mismatch, corrupt build) both
  surface as `grammar_missing_<lang>` — and the remedy the report gives an operator ("install
  the package") is wrong in the second case. The tuple is redundant (`Exception` subsumes
  `ImportError`), which hides that the catch is total; it is the only bare `except: …pass` in
  `argus/`, a shape AR10 and Story 4.3 explicitly forbid. Degradation itself is correct — the
  file is recorded `ast_eligible=False`, never a false deep claim — so this is a
  diagnosis-quality defect, not a correctness one. Close = Story 10.4: split the arms, add a
  distinct broken-grammar reason token, and pin both tokens with a test.
  - id: DF-AUD-APAA-F
  - owner: Engineering Lead
  - target_story: 10-4-a-grammar-that-fails-to-load-names-why
  - category: process
  - severity: 🟢
