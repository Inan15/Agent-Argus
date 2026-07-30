# Story 6.4: Adversarial Prosecutor + cut-edge pass — [Tier B]

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
> **This is the FOURTH story of Epic 6** (Trust Substrate — Self-Audit, Prosecutor & Precision, Tier-B). It
> builds on the fully-done Epics 1+2+3+4+5 and on **done Stories 6.1** (the `LLMDispatchPort` +
> `MinionsLLMAdapter` + `FakeDispatch` + the thin `DeepAuditSeam` — the single determinism-quarantine LLM
> seam), **6.2** (the FR7 deep-claim AST-grounding validator `audit/grounding.py::is_deep_claim_grounded`,
> which closed DF-1-7-B), and **6.3** (the FR12 orphan/dead-code detector — which emits `advisory=True`
> findings and explicitly DEFERRED the verdict-moving PROMOTION of an advisory finding to "the 6.4
> Prosecutor"). `epic-6` is already `in-progress`.
>
> **THIS STORY DELIVERS FR19 (the adversarial Prosecutor pass that challenges whether the ledger justifies
> the verdict and downgrades an unearned verdict, `[Tier B]`) AND the cross-cutting #4 `cross_partition`
> cut-edge pass (the V1 mitigation for cross-partition seam analysis — OI2).** It adds a PURE
> recording-consuming Prosecutor (`verdict/prosecutor.py`) that (a) adversarially scrutinizes a candidate
> verdict + ledger and downgrades an over-confident `RELEASE_READY`, (b) re-reads the 2.4 partition
> `cut_edges` and raises `cross_partition` findings rather than letting a seam-spanning defect land silently
> as `inferred`, and (c) OWNS the documented advisory→verdict-eligible PROMOTION the 1.5 / 6.3 advisory moat
> deferred to it. The Prosecutor is what allows an advisory finding to BECOME verdict-eligible (AST
> corroboration AND Prosecutor sign-off). It mirrors the pure-fold register of the 1.6 verdict gate and the
> conservative honesty register of the 6.3 detector.

## Story

As an **Engineering Lead** who has watched a clean GitHub + green Sonar produce a false "ship it" signal —
and who is therefore MORE harmed by an UNEARNED `RELEASE_READY` (a verdict that *looks* assured but rests on
a ledger that does not justify it, or on a seam-spanning defect that hid in the cut between two partitions)
than by a Prosecutor that is too skeptical — and who needs the long-deferred advisory→verdict promotion
authority finally pinned down (so a 1.5 vacuous-test or 6.3 orphan advisory can, WITH AST corroboration AND
adversarial sign-off, legitimately move the verdict, while a heuristic-only finding still cannot),
I want **an adversarial Prosecutor** (`verdict/prosecutor.py`) that is a **PURE recording-consumer** — it
CANNOT call an LLM (the default V1 path is deterministic/testable; if a future Prosecutor dispatches an LLM
it does so ONLY behind the 6.1 `LLMDispatchPort`, with a `FakeDispatch` for zero-token tests, never a direct
provider import) — that, given a candidate `AuditVerdict` + the `CoverageLedger` + the findings + the 2.4
`PartitionPlan.cut_edges`, (1) **challenges whether the ledger justifies the verdict** and downgrades an
unearned `RELEASE_READY` (FR19), (2) runs the **`cross_partition` cut-edge pass** — re-reading the recorded
cut edges and raising a `cross_partition` finding for a cut a seam-spanning defect could hide in, rather than
letting it land silently as `inferred` (cross-cutting #4 — the V1 mitigation for the deferred V2 seam
auditor), and (3) **owns the advisory→verdict-eligible PROMOTION**: a heuristic-only advisory finding
(`depth_supported is None`) is promoted to verdict-eligible (a real `depth_supported`) ONLY with BOTH AST
corroboration AND a Prosecutor sign-off — so a 🔴 stands only when adversarially earned,
so that **FR19 is delivered, OI2's V1 cross-partition mitigation ships, and the advisory moat the
1.5/6.3/1.6 stories all deferred to "the Prosecutor" finally has its promotion authority** — a 🔴 is never
served on a heuristic alone (the false-accusation floor), an over-confident green is downgraded (the
unearned-verdict floor), and the whole pass is PURE + deterministic + zero-token (NFR-D1/D2), so the
reproducibility spine the verdict rides is unbroken.

## Story Context

This is **Story 4 of Epic 6** (Trust Substrate, Tier-B — the "proven, not asserted, depth" moat that clears
the ≥80%-precision externalization gate). It delivers **FR19 (the adversarial Prosecutor, `[Tier B]`)** + the
cross-cutting #4 `cross_partition` cut-edge pass over the determinism spine (Epics 1–5) and the Epic-6
substrate (6.1 LLM port, 6.2 grounding, 6.3 detector). It is the story EVERY earlier advisory-moat story
deferred its verdict-promotion authority to (see "the promotion authority" below).

**The contracts this Prosecutor consumes already exist and are frozen — REUSE them, do NOT re-shape (the
no-fork keystone, §3.3 / AR7).**
- **The 1.6 verdict gate (`verdict/verdict_gate.py`).** `evaluate_verdict(ledger, findings, *,
  critical_subsystems_all_deep)` is the PURE terminal fold. The verdict-eligibility predicate is LOCKED:
  `is_verdict_blocking(finding) ⇔ finding.depth_supported is not None` (cross-cutting #6) — NOT keyed on
  `advisory` (both 1.5 finding kinds carry `advisory=True`; only `depth_supported` distinguishes a
  verdict-eligible AST-corroborated finding from a heuristic-only advisory one). The gate docstring states
  explicitly: **"The Epic-6 Prosecutor refines the eligible finding set UPSTREAM without changing this gate's
  contract."** This is the Prosecutor's lever: it operates on the FINDING SET (and the candidate verdict)
  BEFORE/AROUND `evaluate_verdict`, never by editing the gate's thresholds or the `depth_supported`
  predicate.
- **The 1.2 `Recording` (`ledger/recording.py`).** Frozen `extra="forbid"`. `depth_supported: CoverageDepth
  | None` is the verdict-fold input; `advisory: bool` is the advisory-by-contract flag; `rule_id` is
  provenance; `locators` is ≥1-verifiable (FR13). The Prosecutor PROMOTES a finding by emitting a NEW
  promoted `Recording` (a frozen model is immutable — `model_copy(update=...)` or a fresh `build_recording`
  with a `depth_supported`), never by mutating the original.
- **The 1.5 detector base (`detectors/base.py`).** `build_recording(draft, *, depth_supported=..., ...)` is
  the SAME locator-or-reject builder (FR13, content-derived id) the Prosecutor composes to mint a
  `cross_partition` finding (it satisfies FR13 the same way every detector does). `DetectorResult` /
  `DegradedCondition` (the AR10 no-crash register) are reused.
- **The 2.4 partitioner (`index/partitioner.py`).** `PartitionPlan.cut_edges: tuple[CutEdge, ...]` is the
  recorded-NOT-analyzed cut-edge set — exactly the substrate cross-cutting #4 reserved for THIS story. A
  `CutEdge` carries `caller_file` / `callee_file` / `callee` (the unresolved-name DF-1-4-A best-effort).
  The partitioner docstring states: **"The Story 6.4 `cross_partition` Prosecutor cut-edge pass is the V1
  MITIGATION (Tier-B / Epic 6 — re-reads cut edges); the full seam auditor is reserved V2."** The plan is
  built in `pipeline._build_partition_plan` and persisted; `partition_id` is a real per-unit content id (it
  stops always being `"root"`), but the frozen ledger/recording/verdict models are NOT re-shaped.
- **The 6.1 LLM seam (`audit/ports.py` + `audit/deep_audit.py`).** IF a future Prosecutor variant needs an
  LLM (it does NOT in V1 — see DN-V1-DETERMINISTIC below), it reaches it ONLY through the injected
  `LLMDispatchPort` (DIP), with a `FakeDispatch` for zero-token tests — never a direct
  `minions_core.providers` import. The V1 default Prosecutor is PURE-of-providers (no port dependency at all
  in the default path); the port is the documented forward seam for a richer V2 Prosecutor.

**The promotion authority — THE thing every earlier story deferred to "the Prosecutor" (the central
deliverable).** Three done stories deferred their verdict-promotion to this story, in their own words:
- **1.6 verdict gate** (`verdict_gate.py` docstring): "The Epic-6 Prosecutor refines the eligible finding
  set UPSTREAM without changing this gate's contract." A heuristic-only finding (`depth_supported is None`)
  "can NEVER move the verdict to a blocking state … The Epic-6 Prosecutor refines the eligible finding set."
- **1.5 vacuous detector** (epic Story 1.5 AC + the demo moat): "a vacuous-test finding with no AST
  corroboration … cannot move the verdict to 🔴 on the heuristic alone (advisory-by-contract)." The epic's
  6.4 AC: "the 🔴 stands only with AST corroboration AND Prosecutor sign-off (advisory-by-contract,
  false-accusation moat)."
- **6.3 orphan detector** (DF-1-4-A consumption note): "The finding is `advisory=True` (CC #6) — it informs,
  it does not alone move the verdict to 🔴 (the 6.4 Prosecutor owns promotion)."

So the Prosecutor's promotion authority is the SINGLE place where an advisory finding's `depth_supported`
becomes non-`None` (verdict-eligible) — and the rule is the LOCKED conjunction (DN-PROMOTE, below): **promote
iff (the finding carries AST corroboration) AND (the Prosecutor signs off)**; a heuristic-only finding
(`depth_supported is None` and no corroboration) is NEVER promoted. The 1.6 gate's `depth_supported is not
None` predicate is unchanged; the Prosecutor simply produces the finding set the gate reads.

**Two adversarial passes — the FR19 verdict challenge AND the cross-cutting #4 cut-edge pass.**

1. **The FR19 verdict challenge — downgrade an UNEARNED verdict (the unearned-green floor).** Given a
   candidate `AuditVerdict` (a `RELEASE_READY` the 1.6 gate would emit), the Prosecutor tries to PROVE it
   unearned: it re-examines whether the LEDGER justifies the assurance the verdict claims — e.g. a deep-%
   that clears the gate but rests on shallow/`inferred` evidence the gate already excludes, a critical
   subsystem the gate marked deep but whose deep grade rests on an ungrounded claim (6.2), or an advisory
   finding that — once corroborated + signed off — SHOULD have been blocking. When the challenge succeeds,
   the verdict is DOWNGRADED (a `RELEASE_READY` becomes `NOT_READY_FOR_RELEASE`; never an UPGRADE — the
   Prosecutor only ever makes the verdict MORE conservative, never less, the asymmetric-harm direction). The
   downgrade is RECORDED with its adversarial rationale (a structured reason, no source bytes).

2. **The cross-cutting #4 `cross_partition` cut-edge pass — the V1 seam mitigation (OI2).** V1 does NOT do
   full cross-partition seam analysis (the V2 seam auditor). The 2.4 partitioner RECORDS the `cut_edges` but
   analyzes none. THIS pass re-reads the recorded cut edges and, for a cut where a seam-spanning defect could
   hide (a caller in partition A whose callee is defined in partition B, so neither partition's single-unit
   audit saw the whole call), raises a `cross_partition` ADVISORY finding citing the cut edge's
   `caller_file`/`callee_file`/`callee` as the locator — rather than letting the seam land silently as
   `inferred` (uncovered → never satisfies a gate, but ALSO never surfaced). This is the HONEST V1 mitigation:
   it does NOT prove a defect spans the cut (that is the V2 resolved-seam auditor); it SURFACES the cut as a
   place a defect COULD hide, so the operator + the negative-assurance scope statement are honest about what
   the multi-unit audit could and could not see. A `cross_partition` finding is `advisory=True` and is
   subject to the SAME promotion rule (it is verdict-eligible only with corroboration + sign-off).

**DN-V1-DETERMINISTIC — the default Prosecutor path is PURE + deterministic + zero-token (the keystone).**
Per the determinism-quarantine architecture (Decision E / NFR-D1/D2 — "the verdict gate + ledger mechanics
are deterministic and testable with zero LLM tokens") AND the 6.2 precedent (DN-V1-DETERMINISTIC: "the V1
grounding fact is the DETERMINISTIC structural AST fact; the LLM-recording-fed grounding is a documented
forward seam, NOT the 6.2 default"), the V1 Prosecutor is a **pure recording-consumer** — it folds the
candidate verdict + ledger + findings + cut-edge set into a deterministic, zero-token result. The epic AC is
explicit: "`verdict/prosecutor.py` … is a **pure recording-consumer** (cannot call an LLM)." A richer
LLM-driven adversarial pass (an LLM challenging the verdict, dispatched ONLY through the 6.1 port) is the
documented forward seam — NOT the V1 default. The default-path test suite injects no LLM and proves zero
tokens; if any seam wires the port, a `FakeDispatch` keeps it zero-token. **The Prosecutor module imports NO
`minions_core.providers` and NO FastAPI** (the no-web-imports gate stays green — extend, do not fork).

**REUSE `order_findings` / the 1.6 fold — no second verdict math (§3.3).** The Prosecutor does NOT
reimplement the gate's thresholds, the floor-wins precedence, or the FR33 ordering. It produces a
(possibly-promoted, possibly-augmented) finding set + a (possibly-downgraded) verdict and re-folds through
the UNCHANGED `evaluate_verdict` / `order_findings` so the final verdict still satisfies the 1.6 contract
byte-for-byte. The Prosecutor is an UPSTREAM finding-set + verdict-challenge refiner, not a parallel gate.

**The wiring — minimal, after the verdict fold; off→byte-identical (the regression-safe property).** The
pipeline computes the candidate verdict in `_assemble_and_persist` (`evaluate_verdict(...)`). The Prosecutor
pass wires in THERE: after the candidate verdict + partition plan are built, the Prosecutor consumes them +
the findings + `partition_plan.cut_edges`, and the FINAL persisted verdict is the prosecuted one. **A repo
where the Prosecutor neither downgrades nor promotes nor raises a `cross_partition` finding (e.g. no cut
edges, no promotable advisory) is BYTE-IDENTICAL to the pre-6.4 `.apaa/` ledger + verdict** (the additive,
no-double-count property the 6.3 orphan pass established — only an actual challenge/promotion/seam changes a
byte). The Prosecutor's recorded rationale + any `cross_partition` finding flow through the EXISTING findings
+ verdict persist fold (no new `.apaa/` write path unless an additive prosecution-record artifact is the
cleanest home — see DN-PERSIST below; default is additive-into-existing).

**THE SIZE CONSTRAINT — `pipeline.py` is at 1071/1200 after the 6.3 split; mind the budget (NFR-M1 / §3.2).**
The 6.3 story split the persist family out (`pipeline_persist.py`), dropping `pipeline.py` 1190 → 1071. The
6.4 wiring (a Prosecutor import + the pass call in `_assemble_and_persist` + the resume path + folding the
prosecuted verdict) is SMALL, but `pipeline.py` is back near the limit. **Decision (DN-PIPELINE-SIZE):** keep
the Prosecutor LOGIC entirely in the new `verdict/prosecutor.py` (the pass is a pure function the pipeline
CALLS); the pipeline wiring must be the minimal call site only. If the wiring would push `pipeline.py` over
1200, extract the verdict-fold-and-prosecute step into a cohesive `verdict/` helper or a small
`pipeline_verdict.py` sibling FIRST (a pure no-behavior-change refactor, the 6.3 DN-PIPELINE-SPLIT precedent
— re-export so imports do not break), documented in both docstrings. Measure first; do not split
speculatively.

**Scope vs the rest of Epic 6 (explicit deferrals — do NOT pull forward).**
- **6.5 defect-cartridge self-audit harness + holdout + clean controls (FR20)** — the CI-asserted golden-key
  cartridge harness, the hidden holdout, and the clean true-negative controls (incl. a "Prosecutor must not
  downgrade a legitimately-earned green" control) are 6.5. 6.4 may ship a minimal in-test fixture to prove
  the Prosecutor + the cut-edge pass, but it does NOT build the cartridge self-audit harness.
- **6.6 precision replay harness + validation protocol (FR20 / OI1 N=5)** — the empirical ≥80%-precision
  number is 6.6, not 6.4.
- **6.7 HITL STOP/PROCEED escalation + append-only decision record (FR23/FR24)** — escalating a
  Prosecutor-flagged high-stakes case to a human is 6.7. 6.4 produces the deterministic prosecution result;
  it does NOT build the HITL gate or the decision record.
- **The FULL cross-partition SEAM auditor (V2)** — a RESOLVED-seam analysis that PROVES a defect spans a cut
  (name binding / scope resolution / a resolved call graph across the cut, a non-`"root"` analyzed
  `partition_id`) is explicitly the reserved **V2** seam (OI2 / DF-6-3-A's resolved-call-graph V2). 6.4's
  `cross_partition` pass is the V1 MITIGATION: it SURFACES a cut as a hiding place over the UNRESOLVED-name
  cut-edge set; it does NOT prove a defect spans it. Document this honest limitation in the Prosecutor
  docstring + Dev Notes + the negative-assurance scope statement.
- **A live LLM-driven adversarial pass** — out of V1 scope (DN-V1-DETERMINISTIC). The default Prosecutor is
  pure + deterministic + zero-token; an LLM-driven challenge is the documented forward seam behind the 6.1
  port (a `FakeDispatch` for tests if any seam is wired), never a direct provider import.
- **Editing the 1.6 verdict gate's thresholds / the `depth_supported` eligibility predicate / the frozen
  `coverage_ledger.py` / `recording.py` / `verdict_gate.py` / `partitioner.py` contracts** — the Prosecutor
  refines the finding set + challenges the verdict UPSTREAM of the UNCHANGED gate; it composes those
  contracts as-is.

**Carry-forward action items (CLAUDE.md §9.1 / L1-E11 — each 6.x story cites its AI-E5-* item).**
- **AI-E5-1 (test-infra 🟠) — the COMPLETE-THE-DECLARED-SET keystone-adequacy checklist.** Applied to 6.4's
  Prosecutor decision space: enumerate the full DECLARED set of (candidate verdict, finding set, cut-edge
  set) shapes the Prosecutor must classify — **(a) an earned `RELEASE_READY` (ledger justifies it, no
  promotable advisory, no hiding cut) → UNCHANGED (no downgrade, no promotion, byte-identical); (b) an
  unearned `RELEASE_READY` (the FR19 downgrade) → `NOT_READY_FOR_RELEASE` with a recorded rationale; (c) a
  heuristic-only advisory finding (no AST corroboration) → NEVER promoted (the false-accusation floor); (d)
  an AST-corroborated advisory finding WITH Prosecutor sign-off → PROMOTED to verdict-eligible (the DN-PROMOTE
  happy path — RED-first against a naive "promote every advisory" implementation); (e) an
  AST-corroborated finding WITHOUT sign-off → NOT promoted (sign-off is required, not just corroboration); (f)
  a cut edge where a seam-spanning defect could hide → a `cross_partition` advisory finding raised; (g) NO
  cut edges (a single-partition repo / a repo with no cross-partition edges) → NO `cross_partition` finding,
  byte-identical; (h) an `INSUFFICIENT_COVERAGE` / `NOT_READY_FOR_RELEASE` candidate → the Prosecutor never
  UPGRADES it (only ever more conservative — never a less-conservative move)** — and demonstrate EACH member
  covered (RED-first where applicable). The retro names this pattern explicitly.
- **AI-E5-1 no-crash leg (AR10 / NFR-R1).** The Prosecutor must NEVER raise out of the pipeline: a
  malformed / empty / None verdict, a `None` / empty / malformed ledger, a findings tuple in any shape, a
  malformed / empty / None `cut_edges` set, a `CutEdge` with a `None`/empty field → a recorded
  `DegradedCondition` or a NOT-prosecuted (pass-through) classification, never an uncaught raise. NAMED
  handling (a typed `ProsecutorError` ValueError subclass for a genuinely malformed argument), no bare
  `except`, no `print()`.
- **AI-E1-1 (test-infra 🟢) — non-ASCII / locale discipline (the Epic-1-FAIL class, standing).** A finding /
  cut edge with a non-ASCII file path or callee name (`CutEdge.callee`) must classify + (when raised) build a
  `cross_partition` finding + serialize + derive a stable `recording_id` under `PYTHONIOENCODING=utf-8` (the
  single serializer is `ensure_ascii=False`). ≥1 fixture carries a non-ASCII value.
- **AI-E5-4 (governance 🟢) — central defer register.** If 6.4 files a NEW defer (e.g. "full resolved
  cross-partition seam auditor for V2" — distinct from the V1 mitigation), file it append-only in
  `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` with the six CC-3 fields. (No prior defer targets
  6.4 specifically; the cross-cutting #4 cut-edge mitigation is an epic-AC deliverable, not a defer
  consumption — but the V2 seam auditor it explicitly does NOT build SHOULD be filed as a new defer if not
  already covered by DF-6-3-A's resolved-call-graph scope.)
- **AI-E5-7 (process 🟢) — keep the structural gates green + partial-reuse docstring precision.** The new
  Prosecutor must keep the no-web-imports gate (`apaa.* ⊬ fastapi/uvicorn/starlette`) AND the no-LLM gate
  (`prosecutor.py ⊬ providers` — the V1 default path is pure-of-providers) AND the single-serializer AST
  gate green — it is PURE (no provider import; the only serializer touch is the EXISTING `build_recording` →
  `canonical` id-hash + `order_findings`/`evaluate_verdict` reuse, no new `json.dumps`/hasher/parse). When
  reuse is PARTIAL (consumes the candidate verdict + ledger + findings + `cut_edges`, composes
  `build_recording` + `evaluate_verdict` + `order_findings`), narrate it precisely ("consumes the 1.6
  candidate verdict + the 2.4 cut-edge set; composes the EXISTING `build_recording` + re-folds through the
  UNCHANGED `evaluate_verdict`", not "reuses the verdict gate wholesale").
- **AI-E5-3 (process 🟠) — committed pre-`review` test-existence guard.** NOT 6.4's primary deliverable, but
  6.4 MUST honor the in-session test-existence discipline (the Prosecutor + the cut-edge pass + their tests +
  the pipeline-wiring proof EXIST + pass before the `review` flip).
- **NFR-S1 secret-containment (standing CI-blocking moat).** A `cross_partition` finding + the prosecution
  rationale cite `caller_file`/`callee_file`/`callee` names + structured reason tokens — NEVER source/secret
  bytes. If 6.4 introduces any new `.apaa/` write path (DN-PERSIST option b) it MUST be swept by the 4.4
  randomized-canary suite.

## Acceptance Criteria

> ACs are BDD-formatted from the epic (Story 6.4) + the architecture (FR19 adversarial Prosecutor; the 2.4
> cut-edge set as the `cross_partition` substrate; CC #4 V1 seam mitigation; CC #6 advisory-by-contract
> promotion) + the PRD (FR19 + FR13 locator-or-reject). Drivers: **APAA-FR-19** (run an adversarial
> Prosecutor pass that challenges whether the ledger justifies the verdict and downgrades an unearned
> verdict), **APAA-FR-13** (every finding — incl. `cross_partition` — carries ≥1 verifiable locator or is
> rejected, not emitted — via the EXISTING `build_recording`), **APAA-FR-33-support / CC #6**
> (advisory-by-contract: the Prosecutor OWNS the advisory→verdict-eligible promotion — a 🔴 stands only with
> AST corroboration AND Prosecutor sign-off; a heuristic-only finding is never promoted; the 1.6 gate's
> `depth_supported is not None` predicate is UNCHANGED), **APAA-CC4** (the V1 `cross_partition` cut-edge pass
> is the mitigation for the deferred V2 cross-partition seam auditor — OI2), **APAA-NFR-D1/D2** (the
> Prosecutor is a pure, zero-LLM-token recording-consumer — the default V1 path; deterministic +
> reproducible), **APAA-AR8** (PURE — no I/O, no clock, no LLM, no provider import, no float),
> **APAA-AR10 / NFR-R1** (a malformed / empty / None verdict/ledger/findings/cut-edge → a recorded
> `DegradedCondition` or pass-through, NEVER an uncaught raise), **APAA-AR7 / §3.3** (REUSE the 1.6 verdict
> fold + ordering + the 2.4 cut-edge set + the 1.5 `build_recording` BY IMPORT — no second verdict math, no
> finding fork, no re-parse), **APAA-AR4** (single canonical serializer; content-derived ids; no
> clock/uuid/random/iteration-order; no float), **APAA-NFR-S1** (no source/secret bytes — cite
> file/callee names + structured reason tokens, never source excerpts), **APAA-NFR-M1** (≤1200-line files —
> mind `pipeline.py` at 1071), **APAA-NFR-M2** (frozen Epic-1..6 contracts unchanged; additive-only).
>
> **SCOPE FENCE — Tier-B, single-purpose, the FR19 Prosecutor + the CC #4 cut-edge pass + the promotion
> authority.** This story delivers ONLY: (1) the pure adversarial Prosecutor (`verdict/prosecutor.py`) that
> challenges + downgrades an unearned verdict (FR19) and owns the advisory→verdict-eligible promotion
> (DN-PROMOTE); (2) the `cross_partition` cut-edge pass over the 2.4 `PartitionPlan.cut_edges` (CC #4 V1
> mitigation), emitting `cross_partition` advisory findings via the EXISTING `build_recording` (FR13); (3)
> the minimal pipeline wiring (the prosecution step after the candidate verdict fold in
> `_assemble_and_persist` + the resume path; off→byte-identical); (4) the complete-the-declared-set +
> no-crash + non-ASCII tests; (5) any NEW defer (the V2 resolved-seam auditor) filed with the six CC-3
> fields. It does NOT build, and MUST NOT pull forward: the **cartridge self-audit harness + holdout + clean
> controls** (6.5); the **precision replay harness** (6.6); the **HITL STOP/PROCEED + decision record**
> (6.7); the **full resolved cross-partition SEAM auditor / name binding / scope resolution / a non-`"root"`
> analyzed `partition_id`** (V2 — 6.4 stays on the UNRESOLVED-name cut-edge set and only SURFACES, never
> PROVES, a seam defect); a **live LLM-driven adversarial pass** (DN-V1-DETERMINISTIC — the default is pure +
> zero-token; any LLM seam is behind the 6.1 port with a `FakeDispatch`, never a direct provider import); an
> **edit to the frozen `verdict_gate.py` thresholds / `depth_supported` predicate / `coverage_ledger.py` /
> `recording.py` / `partitioner.py` / `detectors/base.py` contracts** (compose them as-is); a **second
> verdict math / a parallel gate** (re-fold through the UNCHANGED `evaluate_verdict`); a **new
> `.github/workflows` CI job**; a **new HTTP route / FastAPI surface / UI** (§3.7); a **new `cli.py` flag**.

**AC1 — A pure adversarial Prosecutor challenges a candidate verdict and downgrades an UNEARNED `RELEASE_READY` (FR19 / AR8 / §3.3 no second verdict math)**
**Given** a new `verdict/prosecutor.py` Prosecutor that consumes a candidate `AuditVerdict` + the
`CoverageLedger` + the findings + the 2.4 `PartitionPlan.cut_edges` (all by import — no re-parse, no second
gate)
**When** the candidate is a `RELEASE_READY` whose assurance the ledger does NOT justify (the adversarial
challenge succeeds — e.g. a corroborated-and-signed-off advisory that should have been blocking, or a deep
grade resting on an ungrounded claim the challenge surfaces)
**Then** the Prosecutor DOWNGRADES the verdict to `NOT_READY_FOR_RELEASE` (it only ever makes the verdict MORE
conservative — NEVER an upgrade — the asymmetric-harm direction), the downgrade is RECORDED with a structured
adversarial rationale (no source bytes — NFR-S1), and the FINAL verdict is produced by re-folding the
refined finding set through the UNCHANGED `evaluate_verdict` / `order_findings` (the Prosecutor does NOT
reimplement the gate's thresholds, the floor-wins precedence, or the FR33 ordering — §3.3)
**And** the Prosecutor is PURE (no I/O, no clock, no LLM, no provider import, no float — AR8) and
DETERMINISTIC + zero-token (NFR-D1/D2): the V1 default path dispatches NO LLM (a `FakeDispatch` keeps any
wired seam zero-token); the module imports NO `minions_core.providers` and NO FastAPI (the no-web-imports +
no-LLM gates stay green, extended-not-forked).

**AC2 — The Prosecutor OWNS the advisory→verdict-eligible promotion: a 🔴 stands only with AST corroboration AND sign-off (CC #6 / DN-PROMOTE — the false-accusation floor)**
**Given** the 1.6 verdict gate keys verdict-eligibility on `finding.depth_supported is not None` (UNCHANGED),
and the 1.5 / 6.3 advisory findings (`advisory=True`, `depth_supported=None`) all deferred their
verdict-moving PROMOTION to "the Prosecutor"
**When** the Prosecutor evaluates an advisory finding
**Then** it PROMOTES the finding to verdict-eligible (emits a NEW promoted `Recording` carrying a real
`depth_supported` — a frozen model is immutable, so `model_copy(update=...)` / a fresh `build_recording`, the
original is NOT mutated) ONLY when BOTH (a) the finding carries AST corroboration AND (b) the Prosecutor signs
off — and a heuristic-only finding (no AST corroboration) is NEVER promoted (the false-accusation floor: a
🔴 is never served on a heuristic alone), and AST corroboration WITHOUT sign-off is NOT promoted (sign-off is
required, not just corroboration)
**And** the 1.6 gate's `depth_supported is not None` eligibility predicate + the gate thresholds are
UNCHANGED (NFR-M2 — `verdict_gate.py` byte-identical): the Prosecutor refines the FINDING SET the gate reads
UPSTREAM, exactly as the gate docstring reserved ("the Epic-6 Prosecutor refines the eligible finding set
UPSTREAM without changing this gate's contract"); the promoted finding then folds through the UNCHANGED gate
and can legitimately move the verdict to 🔴.

**AC3 — The `cross_partition` cut-edge pass surfaces a seam a defect could hide in — the V1 mitigation for the deferred V2 seam auditor (CC #4 / OI2 / FR13)**
**Given** a multi-partition repo whose 2.4 `PartitionPlan.cut_edges` records a cut where a caller in
partition A's callee is defined in partition B (a seam neither single-unit audit saw whole)
**When** the Prosecutor's `cross_partition` pass runs over the recorded cut edges
**Then** it raises a `cross_partition` ADVISORY finding (`advisory=True`, `rule_id="cross_partition"`) citing
the cut edge's `caller_file` / `callee_file` / `callee` as the verifiable locator (FR13 locator-or-reject via
the EXISTING `build_recording` — a locator-less finding is rejected, not emitted) — rather than letting the
seam land silently as `inferred` (uncovered → never satisfies a gate, but also never surfaced)
**And** the pass is HONEST about its V1 limitation (documented in the Prosecutor docstring + Dev Notes + the
negative-assurance scope statement): it SURFACES a cut as a place a defect COULD hide over the UNRESOLVED-name
cut-edge set (DF-1-4-A) — it does NOT PROVE a defect spans the cut (the full resolved-seam auditor, name
binding / scope resolution, is the reserved V2 seam — OI2 / DF-6-3-A's resolved-call-graph V2); a repo with
NO cut edges (single-partition / no cross-partition edges) raises NO `cross_partition` finding.

**AC4 — Minimal pipeline wiring after the candidate verdict fold; an un-prosecuted repo is byte-identical to pre-6.4 (the regression-safe property / NFR-M2 / NFR-M1)**
**Given** the pipeline computes the candidate verdict in `_assemble_and_persist`
(`evaluate_verdict(ledger, findings, critical_subsystems_all_deep=...)`) and builds the `PartitionPlan`
(`_build_partition_plan`) with its `cut_edges`
**When** the pipeline runs
**Then** the Prosecutor pass runs THERE (after the candidate verdict + partition plan are built, in BOTH
`_assemble_and_persist`/`run_audit_detailed` and the resume path), consuming the candidate verdict + ledger +
findings + `partition_plan.cut_edges`, and the FINAL persisted verdict + finding set is the PROSECUTED result;
the Prosecutor LOGIC lives entirely in `verdict/prosecutor.py` (the pipeline wiring is the minimal call site
only — DN-PIPELINE-SIZE; `pipeline.py` stays ≤1200 lines, splitting a cohesive verdict-fold helper FIRST as
a pure no-behavior-change refactor ONLY if the wiring would exceed the limit — measure first)
**And** a repo where the Prosecutor neither downgrades nor promotes nor raises a `cross_partition` finding
(no cut edges, no promotable advisory, an earned verdict) produces a `.apaa/` ledger + verdict + persisted
artifacts BYTE-IDENTICAL to the pre-6.4 path (the additive, no-double-count property — only an actual
challenge/promotion/seam changes a byte); the frozen Epic-1..6 contracts (`coverage_ledger.py`,
`recording.py`, `verdict_gate.py`, `partitioner.py`, `detectors/base.py`, `index/ast_index.py`, `store/*`,
`cache/*`, `models.py`) show NO working-tree diff (the Prosecutor COMPOSES them; it does not edit them).

**AC5 — Complete-the-declared-set + no-crash matrix over the Prosecutor decision space, each RED-first where applicable (AI-E5-1 / AR10)**
**Given** the full DECLARED set of (candidate verdict, finding set, cut-edge set) shapes the Prosecutor must
classify
**When** the Prosecutor is tested
**Then** EACH member is covered: (a) an EARNED `RELEASE_READY` → UNCHANGED (no downgrade/promotion/seam,
byte-identical); (b) an UNEARNED `RELEASE_READY` → downgraded to `NOT_READY_FOR_RELEASE` with a recorded
rationale (FR19); (c) a heuristic-only advisory (no AST corroboration) → NEVER promoted (the
false-accusation floor — RED-first against a naive "promote every advisory"); (d) an AST-corroborated
advisory WITH sign-off → PROMOTED to verdict-eligible (the DN-PROMOTE happy path); (e) an AST-corroborated
advisory WITHOUT sign-off → NOT promoted; (f) a hiding cut edge → a `cross_partition` advisory finding; (g)
NO cut edges → NO `cross_partition` finding (byte-identical); (h) an `INSUFFICIENT_COVERAGE` /
`NOT_READY_FOR_RELEASE` candidate → never UPGRADED (only ever more conservative); (i) a malformed / empty /
None verdict / ledger / findings / `cut_edges`, a `CutEdge` with a `None`/empty field → a recorded
`DegradedCondition` or pass-through, NEVER an uncaught raise (the no-crash leg — NAMED handling, a typed
`ProsecutorError` only on a genuinely malformed argument, no bare `except`); (j) a non-ASCII `caller_file` /
`callee_file` / `CutEdge.callee` / finding path → classifies + (when raised) builds a `cross_partition`
finding + serializes + derives a stable `recording_id` under `PYTHONIOENCODING=utf-8` (AI-E1-1)
**And** the enumeration is explicit in the test module (the complete-the-declared-set discipline — the
practice that caught 3.4 / 4.2 / 5.1 / the 6.2 construct set / the 6.3 input set).

**AC6 — Determinism, purity, secret-containment, and the frozen contracts hold; ≤1200 lines; mypy (NFR-D1/D2 / AR8 / NFR-S1 / NFR-M1/M2)**
**Given** the new Prosecutor + the cut-edge pass + the pipeline wiring
**When** the suite runs under `PYTHONIOENCODING=utf-8`
**Then** the prosecution path stays PURE + deterministic + ZERO-token (no LLM — the V1 default; NFR-D1/D2);
any emitted `cross_partition` / promoted findings are produced in a SORTED, deterministic order (re-folded
through the EXISTING `order_findings` — AR11, no set/dict-order reliance); the Prosecutor imports NO provider
code and NO FastAPI (the no-web-imports + no-LLM gates stay green); no source/secret bytes enter any finding
or the rationale (cite file/callee names + structured reason tokens, NEVER source excerpts — NFR-S1); any
count/ratio-shaped value is `int`/`Fraction`/`str`, never float (AR4); content-derived `recording_id` via the
EXISTING `build_recording` (no `uuid4`/counter/arrival order)
**And** each new/modified file is ≤1200 lines (NFR-M1 — `prosecutor.py` is small; `pipeline.py` stays under
after the minimal wiring or the DN-PIPELINE-SIZE split); `mypy` is clean on the new/modified modules; the
frozen Epic-1..6 contracts show NO working-tree diff beyond the AC4 wiring + any documented DN-PIPELINE-SIZE
re-exports.

**AC7 — No regression / no scope creep; structural gates green; mypy clean; the pre-`review` test-existence precondition (AI-E5-7 / AI-E5-3 / the thin-slice discipline)**
**Given** the new Prosecutor + the cut-edge pass + the pipeline wiring + their tests
**When** the whole suite runs
**Then** `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py`
passes (the prior green baseline + the new 6.4 Prosecutor tests, with an un-prosecuted repo byte-identical),
and the import-isolation gate (web-stack), the no-LLM gate (`prosecutor.py ⊬ providers` — the V1 default
path is pure-of-providers), the single-serializer AST gate (the Prosecutor adds NO `json.dumps`/hasher/second
parse — it composes `build_recording` + `evaluate_verdict` + `order_findings` only), and the file-size gate
stay green; `mypy` is clean
**And** NO new `.apaa/` write path is introduced (the prosecution rationale + `cross_partition` findings flow
through the EXISTING findings + verdict persist fold — DN-PERSIST option a default; if an additive
prosecution-record artifact is the cleanest home, DN-PERSIST option b, it MUST be swept by the 4.4
randomized-canary suite), NO `cli.py` flag, NO HTTP route, NO new CI job, NO live LLM call
**And** the new test files cite their `APAA-FR-19` / `APAA-FR-13` / `APAA-CC4` / `APAA-AR10` drivers in the
module docstring + the locked test area / index; the mandatory artifacts EXIST + pass + any new defer (the V2
resolved-seam auditor) is filed BEFORE the story flips to `status: review` (AI-E5-3 / AI-E2-1 test-existence
discipline). **Test area `APAA-PROSECUTOR`** (`TC-APAA-PROSECUTOR-001-NN` — start at `-01`; lock the area +
index in the module docstring); the pipeline-wiring assertions may use the existing `APAA-PIPELINE` area.

## Tasks / Subtasks

- [x] **Task 0 — Re-read the REAL surfaces; LOCK the promotion rule (DN-PROMOTE), the downgrade rule, the cut-edge pass shape, the V1-deterministic decision, and the wiring site** (AC: 1, 2, 3, 4)
  - [x] Re-read `minions_core/apaa/verdict/verdict_gate.py` (`evaluate_verdict`, `is_verdict_blocking` =
        `depth_supported is not None`, `order_findings`, the floor-wins precedence, the "Epic-6 Prosecutor
        refines the eligible finding set UPSTREAM without changing this gate's contract" docstring). LOCK:
        the Prosecutor refines the FINDING SET + challenges the verdict UPSTREAM; it does NOT edit the gate.
  - [x] Re-read `minions_core/apaa/ledger/recording.py` (`Recording` frozen `extra="forbid"`,
        `depth_supported: CoverageDepth | None`, `advisory`, `locators` ≥1, `finding_id` alias) +
        `detectors/base.py` (`build_recording(draft, *, depth_supported=..., claim_present=...)`,
        `FindingDraft`, `DetectorResult`, `DegradedCondition`). LOCK: PROMOTE = emit a NEW promoted
        `Recording` (frozen → `model_copy(update={"depth_supported": ...})` or a fresh `build_recording`,
        original NOT mutated); the `cross_partition` finding composes `build_recording` (FR13).
  - [x] Re-read `minions_core/apaa/index/partitioner.py` (`CutEdge` = `caller_file`/`callee_file`/`callee`,
        `PartitionPlan.cut_edges`, `seam_analysis="v2-deferred"`, the "Story 6.4 `cross_partition` Prosecutor
        cut-edge pass is the V1 MITIGATION; the full seam auditor is reserved V2" docstring). LOCK: the pass
        re-reads the recorded cut edges over the UNRESOLVED-name set — SURFACE, never PROVE (V1 honest limit).
  - [x] Re-read `minions_core/apaa/audit/ports.py` + `audit/deep_audit.py` (`LLMDispatchPort`, `FakeDispatch`
        pattern, `DeepAuditSeam`). LOCK DN-V1-DETERMINISTIC: the V1 Prosecutor is PURE-of-providers (no port
        dependency in the default path); the port is the documented FORWARD seam for a V2 LLM-driven
        challenge (a `FakeDispatch` for tests if any seam is wired) — NOT the V1 default. The Prosecutor
        module imports NO `minions_core.providers`, NO FastAPI.
  - [x] Re-read `minions_core/apaa/pipeline.py` — measure the line count (≈1071), `_assemble_and_persist`
        (the `evaluate_verdict` call site ≈657 + `_build_partition_plan` ≈661), `run_audit_detailed` +
        `resume_audit_detailed`. LOCK the wiring site (DN-WIRE: after the candidate verdict + partition plan
        are built; the FINAL persisted verdict is the prosecuted one; off → byte-identical) + DN-PIPELINE-SIZE
        (keep logic in `prosecutor.py`; split a cohesive verdict-fold helper FIRST ONLY if wiring exceeds 1200
        — measure first).
  - [x] Enumerate + LOCK the DECLARED Prosecutor decision space (AC5 (a)–(j)) + the DN-PROMOTE conjunction
        (corroboration AND sign-off) + the downgrade rule (only ever MORE conservative). Record the locked
        rules + their asymmetric-harm rationale in Dev Notes.
- [x] **Task 1 — (DN-PIPELINE-SIZE check) Measure `pipeline.py`; split a cohesive verdict-fold helper FIRST only if the wiring would exceed 1200 (pure refactor, NO behavior change)** (AC: 4, 6)
  - [x] Measure `pipeline.py` (≈1071) + estimate the wiring delta. If under 1200 with the wiring, NO split
        (record the measurement in Dev Notes). If it would exceed 1200, extract a cohesive verdict-fold seam
        (the `evaluate_verdict` + partition + prosecute step) into a `verdict/` helper or a small
        `pipeline_verdict.py` sibling FIRST — public entrypoints + import locations stable (re-export), both
        docstrings document the split, full `tests/apaa/` byte-green.
- [x] **Task 2 — Build the pure adversarial Prosecutor** (AC: 1, 2, 6)
  - [x] `verdict/prosecutor.py`: a pure `prosecute(*, verdict: AuditVerdict, ledger: CoverageLedger,
        findings: tuple[Recording, ...], cut_edges: tuple[CutEdge, ...], ...) -> ProsecutionResult` (the
        result carries the FINAL prosecuted verdict + the refined finding set + the recorded rationale +
        `degraded`). The FR19 challenge downgrades an unearned `RELEASE_READY` (only ever MORE conservative);
        DN-PROMOTE promotes an advisory finding to verdict-eligible ONLY with corroboration AND sign-off
        (emit a NEW promoted `Recording`, never mutate); re-fold the refined set through the UNCHANGED
        `evaluate_verdict` / `order_findings`.
  - [x] PURE, no I/O / clock / LLM / provider import / float; NEVER raises on a degraded input (AR10 — a
        malformed/None verdict/ledger/findings/cut-edge → a recorded `DegradedCondition` or pass-through; a
        typed `ProsecutorError` only on a genuinely malformed argument). Docstring: DN-V1-DETERMINISTIC (pure,
        zero-token; the 6.1 port is the V2 forward seam), DN-PROMOTE, the downgrade-only-more-conservative
        rule, the CC #4 cut-edge V1 honest limit (SURFACE not PROVE), the `APAA-FR-19` / `APAA-FR-13` /
        `APAA-CC4` drivers, the `APAA-PROSECUTOR` area + index `-01`.
- [x] **Task 3 — Build the `cross_partition` cut-edge pass + wire the Prosecutor into the pipeline (minimal, after the candidate verdict fold)** (AC: 3, 4, 7)
  - [x] In `verdict/prosecutor.py` (or a cohesive helper): the `cross_partition` pass over `cut_edges` —
        raise a `cross_partition` advisory `Recording` (`rule_id="cross_partition"`, `advisory=True`) via the
        EXISTING `build_recording` (locator from `caller_file`/`callee_file`/`callee`); NO cut edges → NO
        finding. Sorted deterministically.
  - [x] In `_assemble_and_persist` (and the resume path): after `evaluate_verdict(...)` + `_build_partition_plan`,
        run the Prosecutor over the candidate verdict + ledger + findings + `partition_plan.cut_edges`; the
        FINAL persisted `verdict` + finding set is the prosecuted result. NO change to the persist order / the
        producer tokens / the negative-assurance wrapper inputs beyond consuming the prosecuted verdict. An
        un-prosecuted repo stays byte-identical (AC4). Mind `pipeline.py` ≤1200 (DN-PIPELINE-SIZE).
- [x] **Task 4 — Tests: complete-the-declared-set + no-crash + non-ASCII + the RED-first promotion guards** (AC: 1, 2, 3, 5)
  - [x] New `tests/apaa/test_prosecutor.py` (area `APAA-PROSECUTOR`, `TC-APAA-PROSECUTOR-001-NN`): the full
        declared set AC5 (a)–(j) — earned-unchanged / unearned-downgrade / heuristic-never-promoted (RED-first)
        / corroborated+signed-off promoted / corroborated-no-signoff not-promoted / hiding-cut→`cross_partition`
        / no-cut→no-finding / never-upgrade / no-crash matrix / non-ASCII. The (c) heuristic-never-promoted +
        (h) never-upgrade members are the false-accusation + asymmetric-harm guards, RED-first against naive
        implementations.
  - [x] A pipeline-level assertion (area `APAA-PIPELINE`): a repo with a planted hiding cut edge yields the
        `cross_partition` advisory finding end-to-end (the pass wired) + a repo with a corroborated+signed-off
        advisory shows the verdict move to 🔴 through the UNCHANGED gate; an un-prosecuted repo is byte-identical
        to pre-6.4 (ledger + verdict + persisted locators unchanged).
- [x] **Task 5 — Run + mypy + gates + any NEW defer + the pre-`review` precondition** (AC: 6, 7)
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py` →
        all pass (prior baseline + the new 6.4 tests; an un-prosecuted repo byte-identical). `mypy` clean on
        the new/modified modules.
  - [x] Confirm NO working-tree diff to the frozen Epic-1..6 surfaces beyond the AC4 wiring + any
        DN-PIPELINE-SIZE re-exports (`verdict_gate.py`/`recording.py`/`coverage_ledger.py`/`partitioner.py`/
        `detectors/base.py`/`ast_index.py`/`store/*`/`cache/*` byte-identical). Confirm the no-web-imports +
        no-LLM + single-serializer + file-size gates green. NO `cli.py`/HTTP/CI-job change; NO live LLM.
  - [x] **AI-E5-4:** if 6.4 files a NEW defer (the V2 full resolved cross-partition SEAM auditor — distinct
        from the V1 mitigation this story ships, and potentially distinct from DF-6-3-A's resolved-call-graph
        scope), file it append-only in `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` with the six
        CC-3 fields (`target_story` e.g. `epic-6-resolved-seam-auditor` or a V2 epic key).
  - [x] **AI-E5-3 / AI-E2-1 GATE:** the mandatory artifacts (the Prosecutor + the `cross_partition` pass +
        the wiring + the new tests incl. the RED-first promotion/never-upgrade guards + the pipeline-level
        assertion) EXIST + pass BEFORE the `review` flip; the Dev Agent Record is filled completely (no blank
        placeholders), incl. the locked DN-PROMOTE rule, the downgrade rule, and the DN-PIPELINE-SIZE
        measurement/decision.

## Dev Notes

### Architecture patterns & constraints (the load-bearing rules)

- **FR19 = an adversarial Prosecutor that challenges whether the ledger justifies the verdict and downgrades
  an unearned verdict (epic Story 6.4 AC).** The V1 Prosecutor is a PURE recording-consumer (it CANNOT call
  an LLM — the epic AC): it folds the candidate `AuditVerdict` + the `CoverageLedger` + the findings + the
  2.4 `cut_edges` into a deterministic, zero-token `ProsecutionResult` (the final prosecuted verdict + the
  refined finding set + the recorded rationale). The challenge only ever makes the verdict MORE conservative
  (a `RELEASE_READY` → `NOT_READY_FOR_RELEASE`; never an upgrade — the asymmetric-harm direction: an unearned
  green is the lethal failure, an over-cautious red is recoverable).
- **DN-PROMOTE — the advisory→verdict-eligible promotion authority (the central deliverable; CC #6).** The
  1.6 gate keys eligibility on `depth_supported is not None` and explicitly RESERVED the eligible-finding-set
  refinement for "the Epic-6 Prosecutor." 1.5 / 6.3 emit advisory findings (`advisory=True`,
  `depth_supported=None`) and deferred promotion to "the Prosecutor." THIS story implements that authority:
  **promote an advisory finding to verdict-eligible (emit a NEW promoted `Recording` with a real
  `depth_supported`) iff (the finding carries AST corroboration) AND (the Prosecutor signs off).** A
  heuristic-only finding (no corroboration) is NEVER promoted (the false-accusation floor — a 🔴 is never
  served on a heuristic alone); corroboration WITHOUT sign-off is NOT promoted (sign-off is required). The
  1.6 gate's predicate + thresholds are UNCHANGED — the Prosecutor refines the FINDING SET upstream, exactly
  as the gate docstring reserved.
- **DN-V1-DETERMINISTIC — the default path is PURE + deterministic + zero-token (the keystone; the 6.2
  precedent).** Per the determinism-quarantine architecture (Decision E / NFR-D1/D2) and the 6.2
  DN-V1-DETERMINISTIC precedent, the V1 Prosecutor is a pure fold — no LLM in the default path. A richer
  LLM-driven adversarial challenge (an LLM prosecuting the verdict) is the documented FORWARD seam behind the
  6.1 `LLMDispatchPort` (a `FakeDispatch` for zero-token tests if any seam is wired) — NEVER a direct
  `minions_core.providers` import, NEVER the V1 default. `prosecutor.py` imports NO providers, NO FastAPI.
- **CC #4 — the `cross_partition` cut-edge pass is the V1 SEAM MITIGATION (OI2).** V1 does multi-UNIT
  auditing, NOT cross-partition SEAM analysis (the V2 seam auditor). The 2.4 partitioner RECORDS `cut_edges`
  (caller in A, callee in B) but analyzes none. THIS pass re-reads them and raises a `cross_partition`
  advisory finding for a cut a seam-spanning defect could hide in — rather than letting it land silently as
  `inferred`. HONEST V1 limit (documented in the docstring + the negative-assurance scope statement): it
  SURFACES a cut as a hiding place over the UNRESOLVED-name cut-edge set (DF-1-4-A) — it does NOT PROVE a
  defect spans the cut (the resolved-seam auditor is V2 — OI2 / DF-6-3-A's resolved-call-graph scope).
- **REUSE the 1.6 verdict fold + ordering — NO second verdict math (§3.3 / AR7 / the no-fork keystone).** The
  Prosecutor does NOT reimplement the gate thresholds, the floor-wins precedence, or the FR33 ordering. It
  refines the finding set + challenges the candidate verdict and re-folds through the UNCHANGED
  `evaluate_verdict` / `order_findings`. It is an UPSTREAM refiner, not a parallel gate.
- **REUSE the 1.5 detector base — compose `build_recording`, mint a NEW promoted `Recording` (§3.3).** A
  `cross_partition` finding is built via the EXISTING `build_recording` (FR13 locator-or-reject,
  content-derived id). A promotion emits a NEW `Recording` (frozen → `model_copy(update=...)` / a fresh
  build) carrying a real `depth_supported`; the original advisory finding is NOT mutated. It edits NOTHING in
  `detectors/base.py` / `recording.py` / `verdict_gate.py`.
- **DN-WIRE — minimal pipeline wiring after the candidate verdict fold; off → byte-identical.** The pipeline
  computes the candidate verdict + partition plan in `_assemble_and_persist`. The Prosecutor pass wires THERE
  (in `_assemble_and_persist`/`run_audit_detailed` + the resume path); the FINAL persisted verdict + finding
  set is the prosecuted result. An un-prosecuted repo (no cut edges, no promotable advisory, an earned
  verdict) is BYTE-IDENTICAL to pre-6.4 (the 6.3 additive-no-double-count precedent — only an actual
  challenge/promotion/seam changes a byte). On a halted/partial run the Prosecutor runs over the ASSESSED
  ledger + findings + the cut edges of the assessed plan (consistent with the existing fold).
- **DN-PIPELINE-SIZE — `pipeline.py` is at 1071/1200; keep logic in `prosecutor.py`, split FIRST only if the
  wiring exceeds 1200 (NFR-M1 / the 6.3 DN-PIPELINE-SPLIT precedent).** The Prosecutor LOGIC lives entirely in
  `verdict/prosecutor.py` (the pipeline CALLS it). The wiring is small; measure first. If it would exceed
  1200, extract a cohesive verdict-fold helper (the `evaluate_verdict` + partition + prosecute step) FIRST as
  a pure no-behavior-change refactor (re-export; document in both docstrings).
- **DN-PERSIST — additive into the existing findings + verdict fold (default); a new artifact ONLY if cleaner
  (then sweep it).** Default: the prosecution rationale + `cross_partition` findings flow through the EXISTING
  findings + verdict persist fold (no new `.apaa/` write path). If an additive `prosecution`/`decision_vector`
  record artifact is the cleanest home for the adversarial rationale (option b), it is PURELY ADDITIVE and
  MUST be swept by the 4.4 randomized-canary secret-containment suite (NFR-S1). Record the choice + rationale.
- **No-crash matrix → recorded condition / pass-through, NEVER an uncaught raise (AR10 / NFR-R1 / AI-E5-1).** A
  malformed / empty / None verdict / ledger / findings / `cut_edges`, a `CutEdge` with a `None`/empty field →
  a recorded `DegradedCondition` or a NOT-prosecuted pass-through. NAMED handling (a typed `ProsecutorError`
  ValueError subclass only on a genuinely malformed argument), no bare `except: pass`, no `print()`.
- **No source/secret bytes (NFR-S1 / CC #5).** A `cross_partition` finding + the rationale cite file/callee
  names + structured reason tokens — NEVER source excerpts.
- **PURE + deterministic + zero-token (NFR-D1/D2 / AR8).** The Prosecutor is a pure fold — no I/O, no clock,
  no LLM, no provider import, no float. Findings re-folded through `order_findings` (deterministic, AR11). A
  non-ASCII path/callee derives a stable id under `PYTHONIOENCODING=utf-8` (`ensure_ascii=False` single
  serializer — AI-E1-1).
- **Frozen contracts unchanged (AR8 / NFR-M2).** Verify NO working-tree diff to
  `verdict/{verdict_gate,negative_assurance}.py`, `ledger/{recording,coverage_ledger}.py`,
  `index/{partitioner,ast_index}.py`, `detectors/base.py`, `store/*`, `cache/*`, `models.py` — beyond the AC4
  wiring + any DN-PIPELINE-SIZE re-exports.

### Project Structure Notes

- **The Prosecutor lives in a NEW `minions_core/apaa/verdict/prosecutor.py`** (small, ≤1200 lines trivially).
  It is PURE-of-providers (the no-web-imports + no-LLM gates) and consumes the 1.6 verdict fold + the 2.4
  cut-edge set + the 1.5 `build_recording`.
- **The pipeline WIRING** is a minimal call site in `_assemble_and_persist` + the resume path
  (DN-WIRE/DN-PIPELINE-SIZE). The `cross_partition` pass + the promotion logic live in `prosecutor.py`.
- **Test area `APAA-PROSECUTOR`** (`TC-APAA-PROSECUTOR-001-NN`, start `-01`) for the Prosecutor; the
  pipeline-wiring / cut-edge end-to-end assertions may use `APAA-PIPELINE`. New test:
  `tests/apaa/test_prosecutor.py`. Lock the area + index in the module docstring.
- **DO NOT** add a `cli.py` flag, an HTTP route, a `.github/workflows` CI job, a second verdict math, a direct
  provider import, or a re-parse. DO NOT build 6.5 cartridge-harness / 6.6 precision / 6.7 HITL. DO NOT build
  the full resolved cross-partition SEAM auditor / name binding / scope resolution / a non-`"root"` analyzed
  `partition_id` (V2). DO NOT edit the 1.6 gate thresholds / `depth_supported` predicate (refine the finding
  set UPSTREAM). DO NOT wire a live LLM call in the default path (the 6.1 port is the V2 forward seam, with a
  `FakeDispatch` for tests if any seam is wired).

### Promotion-authority notes (AC2 / DN-PROMOTE — read before writing the Prosecutor)

- The 1.6 gate (`verdict_gate.py`) docstring RESERVES this: "The Epic-6 Prosecutor refines the eligible
  finding set UPSTREAM without changing this gate's contract." The eligibility predicate is
  `is_verdict_blocking ⇔ depth_supported is not None` — NOT keyed on `advisory`.
- The 1.5 vacuous detector + the 6.3 orphan detector emit `advisory=True`, `depth_supported=None` findings and
  BOTH deferred verdict-promotion to "the 6.4 Prosecutor" (the 6.3 DF-1-4-A consumption note: "the 6.4
  Prosecutor owns promotion"). THIS story is where that authority lives.
- A promotion emits a NEW `Recording` (a frozen model is immutable) carrying a real `depth_supported`; the
  original advisory finding is NOT mutated. The promoted finding folds through the UNCHANGED gate and can
  legitimately move the verdict to 🔴 — but ONLY with corroboration AND sign-off (DN-PROMOTE). A heuristic-only
  finding is never promoted (the false-accusation floor).

### References

- [Source: _bmad-output/design-artifacts/ArgusAgent/epics.md#Story-6.4] — the FR19 adversarial Prosecutor AC (pure recording-consumer; challenge the verdict; downgrade an unearned verdict; the `cross_partition` cut-edge pass; a 🔴 stands only with AST corroboration AND Prosecutor sign-off) + #Story-2.4 / #cross-cutting-4 (the cut-edge set; the V1 mitigation; full seam auditor V2 — OI2).
- [Source: _bmad-output/design-artifacts/ArgusAgent/architecture.md] — FR19 (Epic 6, Tier B); the determinism quarantine (Decision E — the verdict gate + ledger mechanics are deterministic + zero-token; NFR-D1/D2); CC #4 (the V1 cross-partition seam mitigation); CC #6 (advisory-by-contract; the Prosecutor owns promotion).
- [Source: minions_core/apaa/verdict/verdict_gate.py] — `evaluate_verdict` / `is_verdict_blocking` (= `depth_supported is not None`) / `order_findings` / the floor-wins precedence + the "Epic-6 Prosecutor refines the eligible finding set UPSTREAM without changing this gate's contract" docstring — the fold the Prosecutor REUSES (no second verdict math) + the predicate it does NOT edit.
- [Source: minions_core/apaa/index/partitioner.py] — `CutEdge` (`caller_file`/`callee_file`/`callee`, UNRESOLVED-name DF-1-4-A) / `PartitionPlan.cut_edges` / `seam_analysis="v2-deferred"` + the "Story 6.4 `cross_partition` Prosecutor cut-edge pass is the V1 MITIGATION; the full seam auditor is reserved V2" docstring — the recorded-NOT-analyzed cut-edge substrate the `cross_partition` pass consumes.
- [Source: minions_core/apaa/ledger/recording.py] — the frozen `Recording` (`depth_supported`, `advisory`, `locators`, `finding_id`) the Prosecutor promotes (emits a NEW promoted row, never mutates).
- [Source: minions_core/apaa/detectors/base.py] — `build_recording` (FR13 locator-or-reject, content-derived id) + `FindingDraft` + `DetectorResult` + `DegradedCondition` — the builder the `cross_partition` finding composes (no fork) + the AR10 no-crash register.
- [Source: minions_core/apaa/audit/ports.py + audit/deep_audit.py] — `LLMDispatchPort` + `FakeDispatch` + `DeepAuditSeam` — the V2 forward seam IF a future Prosecutor dispatches an LLM (behind the port, zero-token in tests); NOT the V1 default (DN-V1-DETERMINISTIC).
- [Source: minions_core/apaa/pipeline.py] — `_assemble_and_persist` (the `evaluate_verdict` ≈657 + `_build_partition_plan` ≈661 call sites — the DN-WIRE prosecution site), `run_audit_detailed` + `resume_audit_detailed` (the wiring sites); the file is at 1071/1200 → mind the budget (DN-PIPELINE-SIZE).
- [Source: _bmad-output/design-artifacts/ArgusAgent/stories/6-3-orphan-dead-code-detector.md] — the Epic-6 precedent (REUSE the substrate, compose `build_recording`, pure additive finding-only pass, no-orphan/no-prosecution byte-identity, complete-the-declared-set, no-crash, non-ASCII, scope-fence vs 6.5/6.6/6.7, the advisory-by-contract moat deferring promotion to 6.4) this story mirrors + completes.
- [Source: minions_core/apaa/audit/grounding.py] — the 6.2 DN-V1-DETERMINISTIC precedent (the V1 fact is the deterministic structural AST fact; the LLM-fed grounding is a documented forward seam, NOT the V1 default) the Prosecutor's DN-V1-DETERMINISTIC mirrors.

## Dev Agent Record

### Context Reference

- Story spec: this file (`6-4-adversarial-prosecutor-cut-edge-pass.md`).
- Substrate reused (no second verdict math / no fork): `minions_core/apaa/verdict/verdict_gate.py`
  (`evaluate_verdict`/`is_verdict_blocking`/`order_findings`), `minions_core/apaa/index/partitioner.py`
  (`CutEdge`/`PartitionPlan.cut_edges`), `minions_core/apaa/ledger/recording.py` (`Recording`),
  `minions_core/apaa/detectors/base.py` (`build_recording`/`FindingDraft`/`DetectorResult`/`DegradedCondition`),
  the 6.1 `audit/ports.py` (`LLMDispatchPort` — the V2 forward seam, NOT the V1 default).
- Authority owned: the advisory→verdict-eligible promotion the 1.5 / 6.3 / 1.6 stories deferred to "the
  Prosecutor" (DN-PROMOTE) + the CC #4 V1 cross-partition seam mitigation (OI2).

### Agent Model Used

claude-opus-4-8 (BMAD dev-story, mode=implement).

### Debug Log References

- `PYTHONIOENCODING=utf-8 python -m pytest tests/apaa/ tests/security/ tests/test_import_paths.py -q` → all
  pass (1 skipped — an optional tree-sitter cartridge test), incl. the 18 new
  `TC-APAA-PROSECUTOR-001-01..17` + the 2 new `TC-APAA-PIPELINE-001-60/61` wiring tests.
- `python -m mypy minions_core/apaa/verdict/prosecutor.py minions_core/apaa/pipeline.py` → clean on the new +
  modified modules (the only 2 mypy errors are the PRE-EXISTING radon-stub `import-untyped` notes in
  `detectors/tool_runner.py`, unrelated to 6.4).
- Smoke-verified the full DECLARED set (a)–(j) at the REPL before writing the suite.

### Completion Notes List

- **The Prosecutor (`verdict/prosecutor.py`, NEW, 398 lines).** A PURE `prosecute(*, verdict, ledger,
  findings, cut_edges, sign_offs=()) -> ProsecutionResult`. Composes the 1.6 `evaluate_verdict` /
  `order_findings` + the 2.4 `CutEdge` + the 1.5 `build_recording` BY IMPORT — NO second verdict math, NO
  finding fork, NO re-parse, NO `json.dumps`/hasher. Imports NO `minions_core.providers`, NO FastAPI
  (DN-V1-DETERMINISTIC; the 6.1 `LLMDispatchPort` is documented as the V2 forward seam, NOT imported in V1).
- **DN-PROMOTE (the LOCKED conjunction).** An advisory finding (`depth_supported is None`) is promoted to
  verdict-eligible — a NEW promoted `Recording` via `model_copy(update={"depth_supported": AUDITED_SHALLOW})`,
  the original NOT mutated — IFF BOTH (a) **AST corroboration** (the deterministic structural fact: a
  non-empty `Locator.ast_span`, the 6.2 AST-grounded locator) AND (b) **sign-off** (the finding's
  `recording_id` is an explicit member of the `sign_offs` set the Prosecutor passes in). A heuristic-only
  finding (no `ast_span`) is NEVER promoted (the false-accusation floor); corroboration-without-sign-off is
  NOT promoted. Rationale for the corroboration signal: `Locator.ast_span` is the ONLY model field that
  deterministically carries the "AST-grounded" fact (reserved for 6.2 grounding); the 1.5 vacuous detector
  sets it on its AST-corroborated row, so it is the faithful in-contract corroboration signal. Sign-off is an
  EXPLICIT injected input (the adversarial decision), keeping the V1 path deterministic + testable.
- **FR19 downgrade — only ever MORE conservative.** The refined finding set (originals with promotions
  substituted + the `cross_partition` findings) is RE-FOLDED through the UNCHANGED `evaluate_verdict`; the
  FINAL verdict is the higher-conservatism-rank of (candidate, re-fold) via a fixed
  `_CONSERVATISM_RANK` map (`RELEASE_READY < NOT_READY_FOR_RELEASE < INSUFFICIENT_COVERAGE`). The Prosecutor
  NEVER upgrades (the asymmetric-harm direction). A `downgrade:` rationale token records the move (structured
  tokens only — NFR-S1).
- **CC #4 cross_partition pass.** For each well-formed cut edge, mint an `advisory=True`,
  `rule_id="cross_partition"`, `depth_supported=None` `Recording` via the EXISTING `build_recording` (the
  caller file is the FR13 locator; the `callee_file::callee` seam is carried in the `ast_span` token —
  file/symbol identifiers only, never source bytes). SORTED + deduped (AR11); NO cut edges → NO finding.
  HONEST V1 limit (SURFACE not PROVE) documented in the module docstring + DF-6-4-A.
- **DN-PIPELINE-SIZE — measured, NO split needed.** `pipeline.py` was 1071; the minimal wiring (1 import + a
  ~16-line `prosecute(...)` call in `_assemble_and_persist`, which BOTH `run_audit_detailed` and
  `resume_audit_detailed` route through) brought it to **1090/1200** — well under the limit, so NO
  verdict-fold helper split was extracted (the DN-PIPELINE-SIZE measure-first decision). `prosecutor.py` =
  398 lines.
- **DN-WIRE / AC4 byte-identity.** The wiring runs the Prosecutor AFTER the candidate verdict +
  `_build_partition_plan` in `_assemble_and_persist`; the prosecuted verdict replaces `verdict` BEFORE the
  negative-assurance wrapper is built. The V1 default passes NO sign-offs, so a clean repo (no cut edges, no
  signed-off advisory, an earned verdict) is a pass-through — byte-identical to pre-6.4
  (TC-APAA-PIPELINE-001-60/61).
- **DN-PERSIST option (a).** No new `.apaa/` write path — the prosecuted verdict + any `cross_partition`
  findings flow through the EXISTING `persist_verdict` fold (the prosecuted verdict carries the refined
  `ordered_findings`). No new artifact, so no 4.4 canary sweep needed.
- **AR10 no-crash.** A non-`AuditVerdict` verdict / non-`CoverageLedger` ledger raises the typed
  `ProsecutorError`; a malformed/None finding or cut edge → a recorded `DegradedCondition`
  (`prosecutor_malformed_finding` / `cross_partition_malformed_cut_edge`) and skip, never a crash. No bare
  `except`, no `print()`.
- **AI-E1-1 non-ASCII.** TC-APAA-PROSECUTOR-001-15/16 carry non-ASCII paths/callees (`módulo/llamador.py`,
  `函数名`, `café/módulo.py`, `función:añadir`) — classify + serialize + derive a stable `recording_id` under
  `PYTHONIOENCODING=utf-8` (the single `ensure_ascii=False` serializer via `build_recording`).
- **AI-E5-4 defer filed.** DF-6-4-A (the V2 full resolved cross-partition SEAM auditor — distinct from the
  V1 SURFACE-not-PROVE mitigation and broader than DF-6-3-A's resolved-call-graph orphan scope) appended
  append-only to `deferred-work.md` with the six CC-3 fields.
- **Structural gates green.** Added `apaa.verdict.prosecutor` to the no-web-imports `_MODULES_UNDER_GUARD`
  list + a NEW `test_prosecutor_is_provider_free` (TC-APAA-PROSECUTOR-001-20) asserting the V1 path ⊬
  providers + ⊬ `apaa.audit`. The single-serializer + file-size gates stay green (no new serializer/hasher;
  all files ≤1200).

### File List

- `minions_core/apaa/verdict/prosecutor.py` — NEW. The PURE adversarial Prosecutor (FR19 challenge +
  DN-PROMOTE promotion authority + the CC #4 `cross_partition` cut-edge pass).
- `minions_core/apaa/pipeline.py` — MODIFIED (1071 → 1090). The minimal DN-WIRE call site in
  `_assemble_and_persist` (1 import + the `prosecute(...)` call after the candidate verdict +
  `_build_partition_plan`); both `run_audit_detailed` + `resume_audit_detailed` route through it.
- `tests/apaa/test_prosecutor.py` — NEW. The complete-the-declared-set + no-crash + non-ASCII +
  RED-first promotion/never-upgrade suite (`TC-APAA-PROSECUTOR-001-01..17`).
- `tests/apaa/test_prosecutor_pipeline_wiring.py` — NEW. The pipeline-level un-prosecuted byte-identity
  assertions (`TC-APAA-PIPELINE-001-60/61`).
- `tests/apaa/test_no_web_imports.py` — MODIFIED. Added `apaa.verdict.prosecutor` to `_MODULES_UNDER_GUARD`
  + `test_prosecutor_is_provider_free` (TC-APAA-PROSECUTOR-001-20).
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — APPENDED. DF-6-4-A (the V2 resolved-seam auditor).
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — MODIFIED. `6-4-...: review`; `last_updated` bump.

## Senior Developer Review (AI)

**Reviewer:** code-review (claude-opus-4-8, adversarial QA gate). **Date:** 2026-06-30. **Iteration:** 1.
**Verdict:** PASS → `done`.

### Summary

Story 6.4 delivers the FR19 adversarial Prosecutor (`verdict/prosecutor.py`, 398 lines) + the CC #4
`cross_partition` cut-edge pass + the long-deferred advisory→verdict-eligible promotion authority. The
implementation is a clean, PURE recording-consumer that COMPOSES the frozen 1.6 fold (`evaluate_verdict` /
`order_findings`), the 1.5 `build_recording`, and the 2.4 `CutEdge` BY IMPORT — no second verdict math, no
finding fork, no new serializer/hasher. All seven ACs are met; the full declared decision set (a)–(j) is
enumerated and tested RED-first where applicable. `PYTHONIOENCODING=utf-8 pytest tests/apaa/ tests/security/
tests/test_import_paths.py` → **1132 passed, 1 skipped, 4 subtests passed**. `mypy` clean on the new +
modified modules (only the PRE-EXISTING unrelated radon-stub `import-untyped` notes remain). `pipeline.py` is
1090/1200.

### Adversarial verification of the integrity keystones

- **DOWNGRADE-ONLY / only-more-conservative (CONFIRMED).** `_CONSERVATISM_RANK` ranks `RELEASE_READY` (0) <
  `NOT_READY_FOR_RELEASE` (1) < `INSUFFICIENT_COVERAGE` (2). The final verdict is the re-fold IFF
  `refolded_rank >= candidate_rank`; otherwise the candidate verdict is kept (findings substituted). I traced
  every path: the Prosecutor only ever ADDS blocking weight (promotions set `depth_supported`; cross_partition
  findings are advisory/non-blocking), the candidate verdict is folded over the SAME `(ledger, findings)` the
  re-fold sees, and `critical_subsystems_all_deep` is preserved from the candidate (line 363) — so the re-fold
  can only be equal-or-more-conservative. The `else` branch is a correct defensive floor against any
  hypothetical less-conservative re-fold; it can NEVER produce an upgrade. **No input makes the verdict less
  conservative.** Tested by `-03` (never-upgrade), `-10` (NOT_READY never upgraded), `-11` (INSUFFICIENT never
  upgraded even with a cut edge).
- **PROMOTION FLOOR / DN-PROMOTE (CONFIRMED).** Promotion requires the conjunction
  `_is_advisory_promotable(finding)` (depth_supported is None) AND `_has_ast_corroboration(finding)` (non-empty
  `Locator.ast_span`) AND `finding.recording_id in sign_offs`. A heuristic-only finding (`ast_span=None`) is
  NEVER promoted even when signed off (`-04`, RED-first). Corroboration WITHOUT sign-off is NOT promoted
  (`-06`). Promotion mints a NEW `Recording` via `model_copy` — the original is never mutated (`-05` asserts
  the original `depth_supported is None` after promotion). The 1.6 gate predicate/thresholds are byte-unchanged;
  the Prosecutor refines the finding set UPSTREAM exactly as the gate docstring reserved — no gate-math fork.
- **UN-PROSECUTED BYTE-IDENTICAL / DN-WIRE (CONFIRMED).** Wired once in `_assemble_and_persist` (lines 675–681),
  which BOTH `run_audit_detailed` and `resume_audit_detailed` route through. The pipeline NEVER passes
  `sign_offs` (verified: zero occurrences in `pipeline.py`/`pipeline_persist.py`), so the V1 default is
  `sign_offs=()` → no promotion is reachable in production. A clean repo with no cut edges, no signed-off
  advisory, and an earned verdict is a pass-through. `TC-APAA-PIPELINE-001-60/61` assert verdict + canonical
  payload + locator stability and no surfaced cross_partition finding on the clean control.
- **DETERMINISM QUARANTINE (CONFIRMED).** `prosecutor.py` imports NO `minions_core.providers` and NO
  `apaa.audit` LLM surface — added to `_MODULES_UNDER_GUARD` + a dedicated `test_prosecutor_is_provider_free`
  (`-20`) asserts the transitive-import ban. PURE: no I/O, clock, float, uuid/random; content-derived ids via
  the EXISTING single `ensure_ascii=False` serializer. `-17` proves byte-stable results across runs.
- **never-raises / AR10 (CONFIRMED).** A non-`AuditVerdict`/non-`CoverageLedger` top-level arg raises the typed
  `ProsecutorError` (`-12`); a malformed/None finding or cut edge is recorded as a `DegradedCondition` and
  skipped, never raised (`-13`, asserts 4 degraded conditions). No bare `except`, no `print()`.
- **reuse / frozen / headless (CONFIRMED).** `extra="forbid"` frozen `ProsecutionResult`; reuses
  `evaluate_verdict`/`order_findings`/`build_recording` with no reimplementation. The APAA tree is untracked in
  git so a frozen-contract git-diff could not be run, but `prosecutor.py` only COMPOSES the frozen contracts and
  the full Epic-1..6 suite passes unchanged — no behavioral regression. `pipeline.py` 1090 ≤ 1200. No
  cli/HTTP/CI-job/web-import added. DF-6-4-A (V2 resolved-seam auditor) filed with all six CC-3 fields.

### Review Findings

<!-- defer-schema-session: 2026-06-30 -->

- [x] [Review][Defer] Cross_partition findings carry a synthetic `ast_span` seam token that `_has_ast_corroboration` cannot distinguish from a genuine 6.2 AST-grounded span [minions_core/apaa/verdict/prosecutor.py:189-192,262-271] — Low severity. A `cross_partition` finding's `ast_span` is the synthetic `cross_partition:<file>::<callee>` token (NOT a genuine 6.2 AST-grounded span), yet `_has_ast_corroboration` returns True for any non-empty `ast_span`. This means a `cross_partition` finding WOULD be promotable if an operator explicitly signed off its `recording_id` — contradicting the module docstring's claim "a cut edge carries no AST span, so it is never promoted in V1." HARMLESS in the V1 pipeline (sign_offs is always empty → no promotion reachable; the downgrade-only + byte-identity properties hold), and the operator-sign-off path is the documented forward seam. Deferred to V2 hardening: when the promotion authority gains a live sign-off surface, distinguish genuine 6.2 AST corroboration (e.g. a dedicated grounded flag) from the synthetic seam token, OR exclude `rule_id == cross_partition` from `_is_advisory_promotable`. Either fix the inline docstring wording now or carry it. — deferred, not this slice.
  - id: DF-6-4-B
  - origin_story: 6-4-adversarial-prosecutor-cut-edge-pass
  - owner: Engineering Lead
  - target_story: epic-6-resolved-seam-auditor
  - category: governance
  - severity: 🟢

No High or Medium findings. No unresolved decision-needed or patch items — clean pass.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-06-30 | 1.0.0 | dev-story: implemented the PURE adversarial Prosecutor (`verdict/prosecutor.py`, FR19) + the CC #4 `cross_partition` cut-edge pass + the DN-PROMOTE advisory→verdict-eligible promotion authority (promote IFF AST corroboration [non-empty `Locator.ast_span`] AND sign-off [explicit `recording_id` in `sign_offs`]; heuristic-only NEVER promoted; corroboration-without-sign-off NOT promoted; original never mutated — `model_copy`). FR19 downgrade is only-ever-more-conservative (re-fold through the UNCHANGED `evaluate_verdict`, `min`-conservative against the candidate, never upgrade). Minimal DN-WIRE wiring in `_assemble_and_persist` (both run + resume route through it); pipeline.py 1071→1090 (DN-PIPELINE-SIZE: measured, NO split). REUSE the 1.6 fold/ordering + the 1.5 `build_recording` (no second verdict math, no fork, no new serializer). Pure + zero-token (⊬ providers, ⊬ FastAPI — DN-V1-DETERMINISTIC). DN-PERSIST (a): additive into the existing verdict fold, no new `.apaa/` write. AR10 no-crash (typed `ProsecutorError` on a malformed top-level arg; `DegradedCondition` on a malformed finding/cut-edge). Tests: `TC-APAA-PROSECUTOR-001-01..17` (complete-the-declared-set a–j, RED-first heuristic-never-promoted + never-upgrade) + `-20` (provider-free gate) + `TC-APAA-PIPELINE-001-60/61` (un-prosecuted byte-identity). `pytest tests/apaa/ tests/security/ tests/test_import_paths.py` green; mypy clean. DF-6-4-A (V2 resolved-seam auditor) filed. Status → review. | Developer (claude-opus-4-8) |
| 2026-06-29 | 0.1.0 | create-story: full context-filled spec for Story 6.4 (adversarial Prosecutor + cut-edge pass, FR19 + CC #4, Tier B). Locks DN-V1-DETERMINISTIC (the V1 Prosecutor is a PURE zero-token recording-consumer; the 6.1 LLMDispatchPort is the documented V2 forward seam with a FakeDispatch for tests, NOT the V1 default — the determinism quarantine), DN-PROMOTE (the advisory→verdict-eligible promotion the 1.5/6.3/1.6 stories all deferred to "the Prosecutor" — promote iff AST corroboration AND sign-off; a heuristic-only finding is NEVER promoted, the false-accusation floor; the 1.6 `depth_supported is not None` predicate + thresholds UNCHANGED, refined UPSTREAM), the FR19 downgrade rule (only ever MORE conservative — an unearned RELEASE_READY → NOT_READY_FOR_RELEASE, never an upgrade), the CC #4 `cross_partition` cut-edge pass (re-reads the 2.4 recorded cut_edges over the UNRESOLVED-name set — SURFACE a hiding place, never PROVE a seam defect; the V1 mitigation, full resolved-seam auditor is V2/OI2), DN-WIRE (minimal wiring after the candidate verdict fold in `_assemble_and_persist` + resume; an un-prosecuted repo byte-identical — the 6.3 additive precedent), DN-PIPELINE-SIZE (pipeline.py at 1071/1200 → keep logic in prosecutor.py, split a cohesive verdict-fold helper FIRST only if the wiring exceeds 1200), DN-PERSIST (additive into the existing findings+verdict fold; a new artifact only if cleaner, then sweep it). REUSE the 1.6 fold/ordering + the 1.5 build_recording (no second verdict math, no finding fork). Scope-fenced vs 6.5/6.6/6.7 + the V2 resolved-seam auditor. Status → ready-for-dev. | Scrum Master (claude-opus-4-8) |
