---
stepsCompleted:
  - step-01-init
  - step-02-discovery
  - step-02b-vision
  - step-02c-executive-summary
  - step-03-success
  - step-04-journeys
  - step-05-domain
  - step-06-innovation
  - step-07-project-type
  - step-08-scoping
  - step-09-functional
  - step-10-nonfunctional
  - step-11-polish
  - step-12-complete
releaseMode: phased
visionInsights:
  nearVision: 'APAA gives XAgents teams a repeatable, deterministic release-readiness verdict — decision-support they gate their own release on — backed by a coverage ledger that is scope-bounded evidence of what was examined (negative assurance), defensible to a VP or a regulator.'
  northStar: 'Coverage-grounded assurance becomes the default expectation for AI-built software (the way "did your tests pass?" is today). [explicitly long-term]'
  differentiator:
    wedge: 'coverage ledger + vacuous-test detection + signature demo: GitHub green · Sonar green · APAA 🔴 tests appear vacuous'
    durableMoat: 'proven-not-asserted depth (self-audit: AST-grounded depth [Python V1, multi-language V2] + Prosecutor + cartridges) makes audited_deep TRUE → compounds into proprietary concordance/precision/cartridge corpus (credibility flywheel)'
    selfAuditFraming: 'co-load-bearing in moat story; translated to outcomes in value prop ("coverage % you can defend" + "🔴 that does not cry wolf"); near-zero-token determinism story (NOT an LLM-spend multiplier)'
  coreInsight: 'every other tool silently implies "I looked at everything" (unfalsifiable); APAA makes audit confidence falsifiable + negative assurance ("no blocking findings within audited envelope", never "correct")'
  whyNow: 'generation commoditizing → value moved to verification; measurable AI-code-quality crisis (~1.7x issues, 110k+ surviving issues); EU AI Act high-risk bites 2026-08-02; "AI release-readiness assurance" category still unclaimed'
  settledDecisions:
    - 'open-attestation-standard = V4-seeded ambition, one line, NOT foregrounded (schemas already versioned/hashed/additive)'
    - 'Exec Summary leads with the demo moment; mechanics as proof beneath'
    - '≥80%-precision externalization gate elevated as the honesty keystone'
  languageGuards:
    - 'decision-support, not decision-maker (human gates the release; de-risks M2 liability)'
    - 'repeatable/deterministic across repos (standardization hook)'
    - 'negative-assurance phrasing: "evidence of what was examined", never "evidence it is compliant"'
classification:
  projectType: developer_tool
  projectTypePrimary: 'Headless developer-tool / CLI Skill (Claude Code Skill + .apaa/ convention, Cline sequential fallback)'
  projectTypeSecondary: 'contract-producer (frozen schemas + exit-codes)'
  domain: 'AI software assurance / DevTools (compliance-adjacent)'
  complexity: high
  projectContext: greenfield
  contextNote: 'brownfield-adjacent — reuses Minions infra (ADR #18 ledger, permission tiers, budget guardrails, adapter_portability, deterministic orchestration); dogfoods on the Minions repo'
  headless: true
  scope: 'V1 (90-day MVP): coverage honesty + release-readiness verdict + vacuous-test moat; V2–V4 roadmap appendix'
  positioningNote: 'APAA is mechanically an attestation / evidence generator (repo -> defensible verdict + coverage ledger)'
  requiredSections:
    - 'data_schemas + error_codes + api_docs (contracts only: envelope + finding/coverage_ledger/verdict/decision_record)'
    - 'verification methodology (defect cartridges + lightweight Prosecutor)'
    - 'cost-governance NFR'
  outOfScopeV1:
    - endpoint_specs
    - auth_model
    - rate_limits
    - SDK
    - versioning
  skipSections:
    - ux_ui
    - visual_design
    - user_journeys
  carryForwardFlags:
    - 'evidence depth = V1 functional req (not gated by compliance-mapping deferral)'
    - 'governed/gated pipeline stage (HITL STOP/PROCEED + cost gate), not a lightweight linter'
    - 'V1 NFR constraints: source-retention + determinism/audit-trail'
  decisionProvenance:
    type: 'P1 chosen over P3 (true co-primary) on scope-creep resistance'
    domain: 'D3 synthetic chosen over D1 (scientific) on phase placement of compliance'
    scope: 'S1 (V1 + roadmap appendix) chosen over S3 (V1+V2); additive-only schema evolution covers contract-spanning'
inputDocuments:
  - _bmad-output/design-artifacts/APAA/product-brief-apaa.md
  - _bmad-output/design-artifacts/APAA/product-brief-apaa-distillate.md
  - _bmad-output/design-artifacts/APAA/research-market-2026-06-17.md
  - _bmad-output/design-artifacts/APAA/research-domain-2026-06-17.md
  - _bmad-output/design-artifacts/APAA/research-technical-2026-06-17.md
  - _bmad-output/brainstorming/brainstorming-session-2026-06-16-201450.md
  - _bmad-output/project-context.md
  - CLAUDE.md
documentCounts:
  briefs: 2
  research: 3
  brainstorming: 1
  projectDocs: 2
workflowType: 'prd'
---

# Product Requirements Document - APAA (AI Project Assurance Audit)

**Author:** XAgent007
**Date:** 2026-06-17

## Executive Summary

`GitHub: green · Sonar: green · APAA: 🔴 tests appear vacuous`

That one line is the product. AI agents now write software faster than any team can verify it, and the tools meant to help quietly make the problem worse: an AI code reviewer that says "looks good" almost never tells you **how much of the repo it actually looked at**. APAA (AI Project Assurance Audit) closes that gap. You point it at a repository built by AI agents or spec-driven development, and it returns a **coverage-grounded, release-readiness verdict** — *"No release-blocking findings within the audited coverage envelope"* — never the lie that "the code is correct."

**Near-term vision (V1):** APAA gives XAgents teams a **repeatable, deterministic** release-readiness verdict — **decision-support they gate their own release on**, never a tool that decides for them — backed by a coverage ledger that is **scope-bounded evidence of what was examined** (negative assurance), defensible to a VP or a regulator. **North Star:** coverage-grounded assurance becomes the default expectation for AI-built software — the way "did your tests pass?" is today.

**The problem it solves.** Three things are simultaneously true about AI-generated code: the defects are real and measurable (~1.7× more issues than human-written; 110,000+ surviving AI-introduced issues counted in production repos, Feb 2026); the tools that should catch them are either trusted blindly or so noisy they're ignored (SAST at 40–60% false positives, a passing AI-written test taken at face value); and **no one can say how much was actually checked**. The result is a credibility gap — a green check mark that means "some tool ran," not "this is safe to ship" — exactly when regulated buyers increasingly need *defensible evidence* that AI-built code was genuinely examined.

**Who it serves.** Primary (V1): the internal XAgents platform owner — Engineering Lead / Delivery Orchestrator running audits on XAgents-built repos, with the first dogfood target being **Minions itself**. Secondary (standalone path): the regulated enterprise (banks, healthcare, telecom, automotive, aerospace) needing defensible AI-code sign-off evidence for its EU AI Act / ISO 42001 / SOC 2 readiness story.

**Why now.** Generation is commoditizing and value has moved downstream to *verification* ("verification is the new bottleneck"); the AI-code-quality crisis is measurable and publicized; **EU AI Act high-risk obligations bite August 2, 2026**; and the "AI release-readiness assurance" category is **still unclaimed** — incumbents sort into find-more-bugs, find-vulns, check-my-tests, or govern-my-models, and none ships a coverage-grounded release verdict.

### What Makes This Special

APAA is an **assurance** tool, not an AI code reviewer or a security scanner — categories it deliberately avoids. Its differentiation is a two-layer claim:

- **The wedge (what wins the first look):** a **machine-verifiable coverage ledger** plus **AI-specific defect detection led by vacuous-test detection**. Every file lands in a fixed-enum ledger (`audited_deep` / `audited_shallow` / `tool_scanned_only` / `inferred` / `skipped`), and the verdict is a **pure function** of that ledger — it literally cannot be minted without enough `audited_deep` evidence. The vacuous-test detector catches what AI agents *specifically* produce: passing tests that assert nothing. *Honesty is mechanical, not promised.*
- **The durable moat (why a fast-follower can't copy it):** *proven, not asserted, depth.* `audited_deep` requires a **grounded claim validated against the repo's AST** (Python in V1; multi-language in V2) — silence auto-downgrades to shallow. An adversarial **Prosecutor** is paid to prove the verdict unearned, and **defect cartridges** (minimal repos with one planted defect + a golden key, CI-asserted) empirically measure what the detectors catch. Run on real repos, this discipline compounds into a proprietary **concordance / precision / cartridge corpus** no competitor can replicate from the demo. This self-audit is near-zero-token determinism work — *not* an LLM-spend multiplier.

**The core insight:** every other AI-review tool silently implies *"I looked at everything."* It didn't — and that unfalsifiable claim is the gap. APAA makes audit confidence **falsifiable**, and adopts **negative assurance** ("no blocking findings *within the audited envelope*," never "correct") — the same humility that makes financial audits credible and the correct legal/commercial posture. To the user, the self-audit is invisible; what they buy is its output — *a coverage % you can defend to your VP* and *a 🔴 that doesn't cry wolf*. The honesty keystone is explicit: **APAA must hit ≥80% finding-precision before any externalization conversation.** (The coverage-ledger schema is versioned, content-hashed, and additive-only from day one, keeping a V4 "open attestation standard" ambition alive at zero V1 cost — seeded, not foregrounded.)

## Project Classification

- **Project Type:** Headless **developer-tool / CLI Skill** (a Claude Code Skill + committed `.apaa/` filesystem convention, with a sequential Cline fallback) — primary; **contract-producer** (frozen JSON schemas + deterministic exit-codes) — elevated secondary. **Headless-only** — verdicts and evidence are artifacts and API surfaces, never screens (no UI/UX). Hosted-runner / API surface (endpoints, auth, rate-limits, SDK, versioning) is explicitly **out of V1**.
- **Domain:** AI software assurance / DevTools, compliance-adjacent. Compliance (EU AI Act / ISO 42001 / SOC 2) is a **secondary/roadmap** driver in V1, not the headline.
- **Complexity:** **High** — driven by determinism-as-a-requirement, self-auditing, and liability posture (not merely regulated buyers).
- **Project Context:** **Greenfield** product, **brownfield-adjacent** in engineering — it reuses proven Minions infrastructure (hash-chained ledger ADR #18, permission tiers, budget guardrails, `adapter_portability`, deterministic orchestration) and dogfoods on the Minions repo.
- **Scope:** This PRD specifies **APAA V1 — the 90-day MVP** (coverage honesty + release-readiness verdict + the vacuous-test moat). V2–V4 are captured as a roadmap appendix, not V1 commitments.

## Success Criteria

The V1 bar is deliberately an **evidence bar, not a usage bar** — success is whether a designated senior engineer independently trusts APAA's verdicts, not user counts or revenue. **The one bar that gates externalization: ≥80% finding-precision. Everything commercial waits behind it.**

### User Success
*(User = the Engineering Lead / Delivery Orchestrator running APAA on an XAgents repo.)*
- **Repeatable "aha":** on a repo with hidden defects, APAA surfaces ≥1 real issue every other tool called green — and **shows its evidence** (`APAA 🔴`, repeatable).
- **Actionable, not a hedge:** a plain-English line (*"BLOCKED — 3 vacuous tests, coverage 62% deep"*) the user acts on while retaining the decision (decision-support, not decision-maker).
- **Answers the VP question** — *"how much did it actually look at?"* — from the coverage ledger.
- **No cry-wolf:** a 🔴 is credible enough to forward to the team, not mute.

### Business Success
*(V1 = readiness-to-externalize, not revenue.)*
- **Externalization gate cleared:** ≥80% finding-precision on the validation set.
- **Credibility flywheel turning (measurable):** each dogfood run emits ≥1 reusable asset — audit report, concordance label, calibration datum, or (on a miss) a new defect cartridge.
- **Strategic question answered:** APAA auditing Minions resolves *"does Minions have an audit agent?"* with a real artifact.

### Technical Success
- **Verdict is a pure function of the ledger** — unit-tested vs synthetic ledgers, **0 LLM tokens**.
- **Coverage gates enforced:** `RELEASE_READY` requires **≥60% `audited_deep` + all critical subsystems `audited_deep` + 0 blocking findings**; `inferred` can never satisfy a gate; **below 20% coverage APAA emits `INSUFFICIENT_COVERAGE` ("not assessed") — never a default `NOT_READY`** (low coverage is APAA's limitation to report, not the repo's failure to bear).
- **Reproducible verdict** via **local content-addressed memoization** of recorded findings (cache key = content-hash + model checkpoint + APAA version → a re-run returns the *recorded* result). Content-hashing *addresses* artifacts; memoization *reproduces* them.
- **Self-audit green in CI:** V1 cartridges (vacuous test, hardcoded secret, orphan function — 3 = full V1 / Tier B; the cut-order floor is 2) detected vs golden keys; integrity lint passes; secrets redacted before storage.
- **Honest degradation:** budget ceiling halts → marks `skipped` → downgrades → reports truthfully; tool failure becomes a *finding*, never a crash.
- **Runs on the least-capable host:** the sequential code path produces **byte-identical on-disk state** (determinism test, host-independent — not contingent on Cline hardware).

### Measurable Outcomes
| Metric | Target |
|---|---|
| **Finding precision** (🔴 judged genuinely real by an independent senior engineer) | **≥ 80%** (precision tuned over recall) |
| **Verdict concordance (asymmetric)** | **Zero false-`RELEASE_READY`** on the validation set (the fatal error); false-blocks bounded but acceptable |
| **Moat hit-rate** | **≥ 1** real issue other tools missed, **on repos known to contain hidden defects** (0 on a genuinely clean repo is *correct*, not a miss) |
| **Reproducibility** | 100% (same repo + version → same verdict) |
| **V1 cost outcome** | a full APAA audit of Minions completes within a pre-set budget ceiling $X, and the ceiling demonstrably halts + downgrades when breached |
| **Validation set** | **N ≈ 5–10** real XAgents repos, starting with **Minions** |
| **Validation protocol (a V1 deliverable)** | defines who validates, expert-hours/repo, the **precision-adjudication method** (sample size, who judges a 🔴 "genuinely real"), and per-metric pass/fail |

## Product Scope

### MVP — APAA V1 (90-day)
Two layers, both required (trustworthy **and** demoable). Sequential-canonical, filesystem state under `.apaa/`, deterministic throughout.
- **V1 Core:** shared **envelope** (schema_version + content-hash determinism + secret-redaction) · schemas **finding ① / severity.rubric ② / coverage_ledger ③ / verdict ⑧ / decision_record ④ (minimal)** · `standards_refs[]` field + **CWE-required-on-security findings** (day-one additive; rich mapping → V2) · **pure-function verdict gate** · **referential-integrity lint** · **human STOP/PROCEED escalation** with **R1 pattern-matched (not LLM-judgment) escalation, default-STOP** · crude **budget ceiling** (Cost *Governance*) · stack detection + partitioning (≤40 files / 15k LOC) · `work_manifest` **concept** (minimal assignment = file-list = the auditor's **permission boundary**; full schema → V3) · **Python AST-grounded `audited_deep` claims**.
- **V1 Differentiator:** heuristic **vacuous-test detector** (assertion-density + mock-ratio, precision-tuned, advisory-framed) · **defect-cartridge framework** (cartridges #1–3, CI-asserted) · **lightweight Prosecutor** (one pass, final verdict gate only).
- **Proof:** dogfood run against **Minions itself**.

### V1 Design Invariants (forward-compatibility — constraints, not added scope)
- **Envelope determinism** is golden-tested + human-gated before any consumer (a bug here cascades to V1 reproducibility, the G4 cache, and the G1 substrate).
- **Grounded-claim validation is a stack-agnostic interface** (`claim → validated?`), Python = impl #1 — so V2 multi-language is additive, not a core rewrite.
- **Reserve `partition_id`** in the coverage ledger (always `"root"` in V1) for the V2 seam auditor.
- **Frozen invariant declared now:** curated memory (G3, ships V4) **never touches the verdict/decision path**.
- **APAA specifies the cost/memory consumption-contracts** it will need from Minions (a)/(d)/(e).

### Growth Features (V2)
Bidirectional traceability (orphan code + silent req gaps) · Production-Readiness-Review checklist · standards mapping (CWE/ASVS/ISO 25010/SLSA) · **multi-language** AST grounding · **mutation-grade** vacuous-test detection · **seam / interface auditor** (+ honest V1 limitation: *no cross-partition seam analysis in V1*) · **holdout-cartridge rotation** + promote-a-miss · **multi-perspective adversarial panel** (Blind Hunter / Edge-Case Hunter / Acceptance Auditor — V1's single-auditor + lightweight Prosecutor is the deliberate cheap version) · **host-capability manifest** (`adapter_portability`, enables the parallel speedup) · **governance hardening** (proof-of-read / paste-back on high-stakes gates — anti-rubber-stamp, risk H1; matters at externalization scale, not for V1's single senior operator) · **consume the Minions Cost-Optimization layer (d)** for scaled audits (*APAA does not build L1–L4 — it calls them*).

### Vision (V3–V4)
- **V3 — Cost Intelligence (consume, don't own):** integrate the Minions **Cost-Estimation Primitive (a)** in retro mode (audit-cost estimation + per-auditor admission control); APAA owns only its audit-spend policy. **Mechanism-independent of V2; estimation targets scale with shipped audit modes.**
- **V4 — Assurance platform (consume, don't own):** consume the Minions **Memory/Knowledge layer (e)** (G1 log substrate · G2 CQRS projection engine · G3 curated memory · G4 cross-run cache) and contribute APAA's surfaces — the **audit-report = an APAA CQRS projection**, the **cartridge/calibration corpus** in the shared substrate, and **APAA's own IP, the coverage-ledger as an open attestation standard**. Distribution: operated-service-first → hosted repo-URL runner; adjacent markets (M&A, insurer underwriting, agent-vendor certification).

### Dependencies / Cross-product Boundary
**Generic Minions agent-infrastructure layers** (usable by all minions; none APAA scope; consume-not-own per §3.3):
- **(a) Cost-estimation primitive** — APAA consumes **V3** (retro mode). Verified `minions_core/cost/` gap.
- **(d) Cost-Optimization layer (L1–L4)** — APAA consumes **V2** (scale). L2/L3/L4 partly already in `minions_core` (provider tiers + cost-attribution; changed-file scoping; `MINIONS_LLM_PROMPT_CACHE_ENABLED`).
- **(e) Memory/Knowledge layer (G1–G4)** — APAA consumes **V4**. G1 generalizes the ADR #18 ledger to all agent activity; G3 stays out of the verdict path; G4 extends the within-run prompt cache to cross-run.

**Minions front-door / operator features** (Product-Operator facing; **APAA does NOT consume**): **(b)** Forward build quoting (PERT P10/P50/P90, E1–E3) · **(c)** EVM cost control (BAC/AC/EV/CV/EAC, hash-chained cost ledger ADR #18, F1–F3).

**APAA-local boundaries** (deliberately *not* consuming a shared layer, to keep V1 and the verdict unblocked): the V1 **Cost-Governance ceiling**; the verdict-**reproducibility floor = V1's own local content-addressed memoization** (the shared G4 cross-run cache is a later optimization, never the sole guarantee — a safety-critical assurance guarantee must not depend on an external cache APAA doesn't control).

**⚠️ Roadmap risk:** V2/V3/V4 introduce cross-product dependencies on (d)/(a)/(e); **V1 is unaffected**. **📝 Minions-PRD action:** record (a)+(d)+(e) [infra layers] + (b)+(c) [front-door] as Minions epics/features — each a candidate to scope on Minions' own track (not auto-committed; justify against the backlog + verified-gap discipline).

## User Journeys

APAA is **headless** — these are operator and system-to-system workflows. The "interface" is a CLI invocation, the `.apaa/` artifact tree, a verdict + deterministic exit code, and (later) an API. No screens.

### Journey 1 — Priya, Engineering Lead (primary · success path): "the false-green catch"
**Situation.** Priya's team ships an AI-agent-built service. GitHub checks are green, SonarQube is green — yet last quarter a "fully tested" module failed in production because the tests passed but asserted nothing. She no longer trusts the green.
**Opening scene.** She points APAA at the repo: `apaa audit ./service` (headless, no UI). APAA detects the stack, partitions the repo within budget, and starts auditing.
**Rising action.** She watches the `.apaa/` ledger fill — files moving to `audited_deep` (each with a grounded, AST-validated claim), some to `tool_scanned_only`, a few to `skipped`. No black box: she can read exactly what was examined.
**Climax.** The verdict lands: `🔴 BLOCKED — 3 tests appear vacuous (0 meaningful assertions, 14 mocks); coverage 62% deep` — the line GitHub and Sonar never produced. The finding cites file, line range, and the assertion-density/mock-ratio evidence, advisory-framed (not a confident accusation).
**Resolution.** She forwards it, the vacuous tests get fixed, she re-runs: `✅ RELEASE_READY within the audited envelope`. She made the ship call; APAA gave her defensible evidence. New reality: the green check means something again.
*Reveals:* CLI invocation · stack detection + partitioning · coverage ledger + AST-grounded claims · vacuous-test detector (advisory, evidence-bearing) · negative-assurance verdict · re-run/idempotency.

### Journey 2 — Priya again (primary · edge case): "honest about its own limits"
**Situation.** Next repo is a 300k-LOC monolith with poor docs (the ~70% real-world case) and a tight token budget.
**Rising action.** Halfway through, APAA hits the budget ceiling. It does **not** push on or fabricate.
**Climax.** It **stops**, marks the remainder `skipped`, and reports `INSUFFICIENT_COVERAGE — assessed 18% deep; no repo-wide verdict rendered (floor: 20%)`. The poor docs surface as a *finding* ("traceability not establishable"), not a crash; a tool that errored mid-run is downgraded to a finding too.
**Resolution.** Priya isn't delighted — but she **trusts** it more, not less. She raises the budget and re-runs incrementally. The honesty *is* the product.
*Reveals:* budget-governance ceiling (halt → skip → downgrade → report) · `INSUFFICIENT_COVERAGE` floor verdict · tool-failure-as-finding · resumability from on-disk state.

### Journey 3 — Marcus, Delivery Orchestrator (operations): "a repeatable gate across the fleet"
**Situation.** Marcus owns release-readiness across a dozen XAgents repos. He needs a gate he can **standardize** on — same input, same answer, every time, affordable to run.
**Rising action.** He wires `apaa audit` as a CI step keyed to the verdict's **exit code**, with a per-audit budget ceiling, and runs it twice on an unchanged repo.
**Climax.** Byte-identical verdict both times (local content-hash determinism) — a number he can put in a dashboard and trust not to flake; the ceiling means no audit surprises him on cost.
**Resolution.** He gates merges to `main` on `APAA == RELEASE_READY`, with `INSUFFICIENT_COVERAGE` routing to human review (never a silent pass *or* a false block). New reality: an auditable, repeatable release gate across the fleet.
*Reveals:* deterministic/reproducible verdict · exit-code wire contract · CI integration as a headless step · per-audit budget governance · `INSUFFICIENT_COVERAGE → human review` routing.

### Journey 4 — Dana, Head of Quality at a regulated enterprise (secondary · operated-service): "evidence I can show a regulator"
**Situation.** Dana's bank ships AI-generated code under EU AI Act scrutiny. She can't install a stranger's tool on her source, and she needs *defensible* evidence, not a green badge.
**Rising action.** Via the operated-service path, an XAgents engineer runs APAA and hand-delivers an **evidence bundle** — coverage ledger, scope statement ("examined X, sampled Y, did not cover Z"), findings with redacted excerpts, and the negative-assurance verdict + disclaimer + point-in-time stamp. Source is never retained.
**Climax.** Her legal team reads "no release-blocking findings *within the audited coverage envelope*" and recognizes the **audit-grade humility** — scope-bounded, never a compliance guarantee. It's evidence of *what was examined*, framed honestly.
**Resolution.** The bundle feeds her ISO 42001 / SOC 2 readiness story as a code-artifact evidence layer. New reality: inspectable proof, not a self-assessment.
*Reveals:* evidence-bundle / scope-statement artifact · secret redaction in stored excerpts · negative-assurance verdict semantics + disclaimer + point-in-time stamp · source-retention guarantee (operated-service).

### Journey 5 — The CI pipeline / orchestrating agent (API · system-to-system, headless): "repo in, verdict out"
**Situation.** An automated pipeline (or a Minions Flow Orchestrator) must gate a release with **no human in the loop** at run time.
**Rising action.** It invokes APAA headlessly against a repo at a pinned commit, passing a budget and a materiality bar. APAA writes the `.apaa/` artifact tree and emits a structured **verdict artifact + deterministic exit code**.
**Climax.** The pipeline reads the exit code: `RELEASE_READY` → proceed; `BLOCKED` → halt + attach findings; `INSUFFICIENT_COVERAGE` → escalate to a human STOP gate (never auto-proceed). Every decision is machine-consumable and reproducible.
**Resolution.** The release pipeline now carries a coverage-grounded gate another system can act on. New reality: assurance becomes a pipeline primitive, not a manual review.
*Reveals:* headless invocation contract (repo + commit + budget + materiality → verdict artifact + exit code) · machine-readable `.apaa/` artifacts · deterministic exit-code semantics · human-STOP escalation on the non-deterministic case · commit-pinned reproducibility.

### Journey Requirements Summary
| Capability area | Forced by |
|---|---|
| **Headless invocation contract** (repo+commit+budget+materiality → verdict artifact + exit code) | J1, J5 |
| **Stack detection + partitioning** (≤40 files/15k LOC) | J1, J2 |
| **Coverage ledger + AST-grounded `audited_deep` claims** | J1, J3 |
| **Vacuous-test detector** (advisory, evidence-carrying, precision-tuned) | J1 |
| **Negative-assurance verdict** (+ scope statement, disclaimer, point-in-time, materiality bar) | J1, J4, J5 |
| **`INSUFFICIENT_COVERAGE` floor + honest degradation** (halt→skip→downgrade→report; tool-failure-as-finding) | J2, J3, J5 |
| **Budget-governance ceiling** | J2, J3 |
| **Deterministic/reproducible verdict + exit-code wire contract** | J3, J5 |
| **CI integration as a headless gated step** (+ `INSUFFICIENT_COVERAGE`→human-STOP routing) | J3, J5 |
| **Evidence bundle + secret-redacted excerpts + source-retention** (operated-service) | J4 |
| **Resumability from on-disk `.apaa/` state** | J2 |
| **Defect cartridges / self-audit** (the trust substrate behind every verdict) | all |

## Domain-Specific Requirements

APAA operates in **AI software assurance** — a compliance-*adjacent* domain. It is **not** a certified attestation service; it produces a **code-artifact evidence layer** that *feeds* a buyer's compliance story. Every requirement below is filtered through the negative-assurance, no-over-claim posture.

### Compliance & Regulatory
- **Negative-assurance framing is mandatory, not stylistic.** Verdicts borrow the *language and posture* of mature assurance disciplines (financial audit's "presents fairly, in all material respects"; SOC 2 scope+period; ISO/DO-178C rigor) **strictly as analogies, never as claims APAA has earned**. SOC 2 / "reasonable assurance" are CPA-owned terms; APAA must not imply certification. Every verdict ships a `scope_statement`, a materiality bar, a `disclaimer`, and a point-in-time stamp.
- **Standards anchoring (phased).** **V1:** `standards_refs[]` field (format-validated, e.g. `^CWE-\d+$`) + **CWE required on every security-category finding** (the cheapest, most mechanical, highest-stakes mapping). **V2:** broader mapping to OWASP ASVS, NIST SSDF, SLSA, ISO/IEC 25010.
- **EU AI Act as forcing function, not a claim.** High-risk obligations (Aug 2, 2026) are *why* regulated buyers need defensible AI-code evidence — APAA's coverage ledger plugs into their EU AI Act / ISO 42001 / SOC 2 *readiness* artifacts; it does **not** itself certify conformance.
- **Liability surface (M2).** A release verdict is a liability surface. Disclaimers, scope boundaries, and point-in-time stamps are non-negotiable on every emitted verdict.

### Technical Constraints
- **Determinism / reproducibility is a hard requirement** (not an optimization). Honest reframe: bit-identical LLM output is infeasible even at temp 0; APAA guarantees a **deterministic coverage ledger + pure-function verdict**, made stable across runs by **content-addressed memoization** with the model checkpoint pinned into the key (a model rotation = a deliberate re-audit event).
- **Secret containment.** Audited repos contain secrets. APAA **redacts excerpts before storage** (`excerpt_redacted` + `contained_secret`); prompt/response/source bytes must **never** leak into the ledger, evidence bundle, logs, or exception traces — mirroring Minions §3.8 secret-masking. The **operated-service path carries an explicit source-retention guarantee** ("we never retain your source").
- **The auditor is itself an LLM (the trust frontier).** Risk = a shallow read mis-graded as deep. Defended by AST-grounded `audited_deep` claims (silence → downgrade), the adversarial Prosecutor, and self-validating defect cartridges.
- **Hostile / low-quality-repo robustness.** Coverage gaming (criticality detected by *content*, not filename) and evidence poisoning (**`inferred` narrative can never satisfy a verdict gate**). ~70% of real repos have poor docs → that becomes a *finding* ("traceability not establishable"), never a crash.
- **Permission tiers (stateless agents).** Auditor agents read only their assigned files (`work_manifest` = permission boundary); coordination is file-mediated through `.apaa/`. (V4 Reports Agent is read-only.)
- **Headless-only.** No UI; all output is artifacts, deterministic exit codes, and (later) API surfaces.

### Integration Requirements
- **Stack-agnostic ingest:** cold-reads any repo, detects stack + toolchain, and offloads breadth to **zero-token deterministic tools** (`cloc`/`radon`/linters/SAST) so LLM spend goes only to depth (L1).
- **Portability:** runs on the **least-capable host (Cline, sequential)**; parallel execution is a byte-identical speedup (V2 host-capability manifest).
- **CI / pipeline integration:** headless gated step keyed to the verdict exit code; `INSUFFICIENT_COVERAGE` routes to a human STOP gate.
- **Minions reuse (brownfield-adjacent):** hash-chained ledger patterns (ADR #18), permission tiers, budget guardrails, `adapter_portability`; later consumes the shared Minions layers (a)/(d)/(e).

### Risk Mitigations (domain-specific)
- **Over-claim / credibility erosion** → negative-assurance + scope statements + **precision tuned over recall** + the **≥80%-precision gate before any externalization**.
- **False accusation** (a wrong 🔴 is a public credibility hit, the moat's most lethal failure) → advisory framing + evidence-carrying findings (counts, not verdicts) + precision-tuned detectors.
- **Hostile repo** (coverage gaming, evidence poisoning) → content-based criticality + `inferred`-never-satisfies-a-gate.
- **Cartridge overfitting (M1)** → holdout-cartridge rotation + promote-a-miss-to-a-cartridge (**V2**).
- **Reproducibility misunderstanding** → ship the honest reframe in the docs (system-level determinism, not LLM repeatability).
- **Liability** → mandatory disclaimers + point-in-time stamps on every verdict.

## Innovation & Novel Patterns

### Detected Innovation Areas
1. **Machine-verifiable coverage ledger (the core IP).** APAA makes *audit confidence itself falsifiable* — the verdict is a **pure function** of a fixed-enum ledger that cannot be minted without `audited_deep` evidence. Every other tool leaves "how much did I examine?" as an **unstated, unfalsifiable implication**. The new paradigm: *honesty is mechanical, not promised.*
2. **Negative assurance applied to a code release.** Borrowing the financial-audit / SOC 2 *posture* — "no release-blocking findings *within the audited coverage envelope*," never "the code is correct" — is a **novel cross-pollination** of a mature assurance discipline onto AI-built software. The humility is the innovation: it earns trust by refusing to over-claim.
3. **Vacuous-test detection as an AI-specific defect class.** Generic auditors catch what *humans* get wrong; APAA targets what *AI agents specifically produce* — passing tests that assert nothing. Treating "the tests pass" as **untrustworthy until proven meaningful** (assertion-density + mock-ratio in V1, mutation-grade in V2) is a defect category the incumbent clusters don't name.
4. **The auditor audits itself.** **Defect cartridges** (minimal repos with one planted defect + a golden key, CI-asserted) are *mutation testing applied to the auditor*, and an adversarial **Prosecutor** is paid to break the verdict. A tool built to detect over-confidence **refuses to exempt itself**.
5. **Deterministic assurance over a non-deterministic substrate.** APAA does *not* promise the LLM repeats itself (infeasible); it guarantees a **deterministic ledger + pure-function verdict** stabilized by content-addressed memoization. Reproducibility becomes a property of the *system*, not the model.
6. **(V4 ambition, seeded now) the coverage-ledger as an open attestation standard** — alongside SBOM / SLSA / in-toto. Turning the *format* into infrastructure is the most ambitious novelty; deliberately seeded via schema discipline, not built in V1.

### Market Context & Competitive Landscape
The assurance category is **unclaimed**. Incumbents sort cleanly into four buckets, none of which ships a coverage-grounded release verdict: **AI code-review bots** (CodeRabbit, Greptile, Qodo — per-PR comments, trust the green tests); **SAST/quality scanners** (SonarQube, Snyk, CodeQL — 40–60% false positives, pattern-bound to human idioms, findings not a decision); **mutation/test-quality tools** (Stryker, PIT — language-siloed dev tooling, no verdict/ledger — they *validate* the vacuous-test thesis but leave the auditor-product space open); and **AI-governance platforms** (Credo AI, Holistic AI — govern *models and paperwork*, not the *code* an agent shipped — complementary, not competitive). Timing: generation has commoditized (value moved to verification) and **EU AI Act high-risk obligations bite Aug 2, 2026** — a felt assurance gap with no incumbent owner.

### Validation Approach
The innovation is validated **empirically, not asserted** — fitting for a tool whose thesis is "evidence over trust":
- **Defect cartridges + holdout rotation** measure what the detectors actually catch (the auditor's own mutation score), CI-asserted; real-world misses become new cartridges.
- **The ≥80% finding-precision bar** on **N ≈ 5–10 real XAgents repos** (starting with the **Minions dogfood**) is the gate before any externalization.
- **Verdict concordance** (asymmetric: zero false-`RELEASE_READY`) against an independent senior engineer's release decision.
- **The moat demo as a success criterion**, not just a demo: `GitHub green · Sonar green · APAA 🔴 tests appear vacuous`, made repeatable.

### Risk Mitigation
- **Heuristic precision too low (false accusation = lethal)** → advisory framing + evidence-carrying findings + precision-over-recall tuning; **fallback** = "review these N tests," never "IS vacuous"; mutation-grade detection is the V2 accuracy fallback.
- **Coverage ledger reads as a disclaimer** → the visceral vacuous-test demo makes value concrete; the ledger is the proof beneath it.
- **Self-audit seen as navel-gazing** → translated to outcomes (precision you trust, coverage you can defend).
- **Category-creation cost** (buyers don't shop for "AI software assurance") → ride the **vacuous-test wedge that needs no category education**, sold to the accountable buyer burned by a false-green.
- **Open-standard premature** → seeded-not-foregrounded; schemas disciplined now, standard pursued only after V1 earns trust.
- **Incumbent encroachment** (a SAST vendor bolts on "coverage honesty") → moat is the **compounding concordance/precision/cartridge corpus**, not the framing — copyable wedge, uncopyable flywheel.

## Developer Tool (Headless Skill) — Specific Requirements

### Project-Type Overview
APAA ships as a **headless Claude Code Skill** (Cline sequential fallback) that cold-reads a repository and emits a coverage-grounded verdict. It is simultaneously a **contract-producer**: its durable output is a set of **frozen JSON artifacts** under `.apaa/` plus a **deterministic exit code**. There is no UI, IDE plugin, or visual surface (headless-only); integrators consume artifacts and exit codes. **Stack-agnostic** by construction (V1 deep AST-grounding = Python, `claim_emitted` proxy elsewhere); hosts = Claude Code (parallel) + Cline (sequential-canonical). Distribution in V1 = the Skill + a committed (git-ignorable) `.apaa/` convention, plus the operated-service evidence-bundle path; a hosted repo-URL runner is V4.

### Technical Architecture Considerations
- **Filesystem-as-contract substrate.** All state lives under `.apaa/` (`state/ · assignments/ · findings/ · decisions/`); stateless auditor agents coordinate **only through files** — making runs resumable, portable, and host-agnostic.
- **Sequential-canonical execution.** One auditor at a time is the canonical model; parallel (Claude Code) must produce **byte-identical on-disk state** (a pure speedup). A **host-capability manifest** (V2) selects the scheduling strategy without changing the contracts.
- **Frozen contracts + shared envelope.** Every artifact is wrapped in an envelope (`schema_version` · content-addressed `id` · `content_hash` over payload-only · `prev_hash` chaining · `producer` · `apaa_version`); volatile fields (`run_id`, `created_at`) are excluded from the hash → identical inputs ⇒ identical hash ⇒ reproducible verdict. Schemas evolve **additive-only**.
- **Permission tiers.** An auditor's `work_manifest` (file-list) **is** its read permission boundary; it cannot read off-scope.

### API / Contract Surface *(the elevated contract-producer dimension)*
- **Headless invocation contract:** `repo + commit + budget + materiality_bar` **in** → `verdict artifact + .apaa/ tree + deterministic exit code` **out**.
- **Exit-code wire contract** (house style, mirrors Minions gates): a stable mapping for `RELEASE_READY` / `BLOCKED` / `INSUFFICIENT_COVERAGE` / crash — machine-consumable by a CI gate.
- **V1 schema set:** `envelope`, `finding` ①, `severity.rubric` ②, `coverage_ledger` ③, `verdict` ⑧, `decision_record` ④ (minimal) + the referential-integrity lint. (Hosted HTTP API / auth / rate-limits / SDK / versioning are explicitly **out of V1** → V4.)

### Code Examples & Migration
- **Examples = executable defect cartridges** (#1 vacuous test, #2 hardcoded secret, #3 orphan function), each with a golden expected-findings key, asserted in CI — they double as the conformance suite.
- **"Migration guide" = the additive-only schema-evolution policy**: new fields only, `schema_version` bumped, content-hash determinism preserved — so a V2/V3 consumer never forces a breaking change.

### Implementation Considerations
- **Token-free core first.** Stack detection, the ledger mechanics, the pure-function verdict gate, and the integrity lint are deterministic and unit-testable with **zero LLM tokens** before any model is called.
- **Determinism is golden-tested** (envelope canonicalization) and human-gated before any consumer — the single highest-leverage correctness item.
- **Reuse Minions infra** (brownfield-adjacent): ADR #18 hash-chained ledger patterns, permission tiers, budget guardrails, `adapter_portability`.
- **Secret-safe by construction:** redact excerpts before storage; never let source/secret bytes reach the ledger, evidence, logs, or traces.

**Skipped (headless):** `visual_design`, `store_compliance`.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy
- **MVP type: a problem-solving / validated-learning MVP**, not a feature MVP. Mantra: **prove organizations trust a coverage-grounded verdict BEFORE building anything else.** Trust is the product.
- **Minimum-useful = the two-layer V1:** coverage honesty (trustworthy) **+** the vacuous-test moat (demoable). Either alone fails.
- **"Has potential" moment:** the repeatable `GitHub green · Sonar green · APAA 🔴 tests appear vacuous` demo on the **Minions dogfood**.

### V1 has two grades — name which one you mean
- **Tier A — demo-grade (signature-demo core):** envelope + `finding`/`coverage_ledger`/`verdict` + pure-function verdict gate + heuristic vacuous-test detector + **cartridges #1 (vacuous) & #2 (secret)** + cost-governance ceiling + secret redaction. Proves the *concept*.
- **Tier B — validation-grade (externalization-ready):** Tier A **+** cartridge #3 (orphan) + Python AST-grounding + lightweight Prosecutor + `decision_record` (minimal) + integrity lint + the **Minions dogfood** + reproducibility + honest degradation. **Tier B is what clears the ≥80%-precision externalization gate.**
- *(`severity.rubric` is a V1 **config constant**, not a frozen schema, until severities need to vary.)*

### MVP Must-Have (full V1 = Tier B) and Journeys
Full detail in §Product Scope. Journeys served: J1 (false-green catch), J2 (honest degradation), J3 (repeatable gate), J5 (headless invocation); J4 (regulated evidence bundle) via the operated-service path.

### Cut-Order (pre-agreed; what slips if 90 days is tight)
The cut-order trades **Tier B → Tier A**, and is honest that **the ≥80%-precision externalization gate slips with it** (a cut V1 is demo-grade, not externalization-ready):
- **Non-negotiable core (never cut):** envelope + `finding`/`ledger`/`verdict` + verdict gate + vacuous detector + **2 cartridges (vacuous + secret)** + cost ceiling. *(Floor is 2, not 1 — Tier A ships redaction, and cartridge #2 is its only validator; cutting it would ship an unvalidated security path.)*
- **Slide order → V1.5:** (1) **Python AST-grounding** (keep the `claim_emitted` floor); (2) lightweight **Prosecutor**; (3) **cartridge #3 (orphan)**; (4) `decision_record` (but still **log the STOP**); (5) **integrity lint** (keep it if J2/resume is a V1 demo).
- **Last thing cut:** the **Minions dogfood** — it *is* the proof.

### V1 Schema-Design Invariant (keeps the cut clean)
`coverage_ledger` accepts a **`claim_emitted` (unvalidated) claim**, with AST-validation as an **optional strengthening flag — never a hard schema requirement** — so AST-grounding can slide to V1.5 without breaking the contract. (Severity enum lives **inline in `finding`**, not as a `$ref` to the config rubric.)

### Resource Shape (honest about research vs engineering)
- **90 days delivers Tier A (demo-grade) with high confidence.** The **≥80%-precision bar is an evidence-gated milestone, NOT a calendar deliverable** — precision tuning is an empirical loop with unknown convergence, not a schedulable build task.
- **Three milestones:** M1 Deterministic spine *(+ front-load: cartridge #1 + a tiny real-repo precision harness + a thin 1-file→1-finding→verdict e2e slice — moving the research & integration risk forward)* → M2 Findings engine + moat → M3 Verdict trust + full Minions dogfood.
- **Team: small but *senior*** — determinism, security (redaction), AST, and empirical tuning are not junior-parallelizable.

### Post-MVP
Phases V2–V4 are defined in **§Product Scope** (Growth Features / Vision) and its **§Dependencies / Cross-product Boundary** — not duplicated here.

### Risk Mitigation Strategy
- **Technical:** envelope-determinism cascade → golden-test + human gate (highest-leverage item); vacuous precision too low → advisory framing + precision-tuning + "review these N" fallback; Python-only AST → stack-agnostic validator interface (V2 multi-language additive). **Riskiest assumption:** that the heuristics clear ≥80% precision — de-risked by front-loading the cartridge precision harness in M1.
- **Market:** category-creation cost → ride the vacuous-test wedge (no category education); incumbent encroachment → the compounding corpus is the moat, not the framing.
- **Resource:** the cut-order is the contingency; **precision-non-convergence fallback** → tighten to higher-precision advisory OR pull mutation-testing forward from V2, **accepting the timeline may extend** if precision research runs long.

### Open inputs (flagged, not blockers)
Exact **team headcount**, the **budget-ceiling `$X`**, and **N** for the validation set (5–10) — resolved in the delivery/functional detail, not the scope decision.

## Functional Requirements

> **Capability contract (V1).** This is binding: a capability not listed here will not exist in V1 unless explicitly added. Items marked **[Tier B]** are the validation-grade additions over the demo-grade core (per §Project Scoping); everything else is non-negotiable core. Capabilities beyond V1 live in §Product Scope (V2–V4) and are out of this contract.

### Repository Intake & Partitioning
- **FR1:** An operator can submit a repository at a pinned commit for audit through a headless invocation.
- **FR2:** APAA can detect the repository's technology stack and available toolchain without operator configuration.
- **FR3:** APAA can partition the repository into bounded audit units within a declared budget.
- **FR4:** APAA can identify critical subsystems (and an operator can designate them) so coverage gates can require them to be examined deeply.

### Coverage Ledger & Grounded Evidence
- **FR5:** APAA can record every file's audit depth in a fixed-enum coverage ledger (`audited_deep` / `audited_shallow` / `tool_scanned_only` / `inferred` / `skipped`).
- **FR6:** APAA can require an emitted claim before grading a file `audited_deep` (silence downgrades to `audited_shallow`).
- **FR7:** APAA can validate a deep claim against source structure (Python AST in V1) and downgrade an unverifiable claim. **[Tier B]**
- **FR8:** APAA can exclude `inferred` (narrative/doc) evidence from satisfying any verdict gate.
- **FR9:** An operator can read exactly which files were examined deeply, shallowly, tool-scanned, inferred, or skipped.

### Defect Detection (cartridge-validated)
- **FR10:** APAA can detect tests that appear vacuous (low assertion-density / high mock-ratio) and report them as **advisory** findings carrying their evidence counts.
- **FR11:** APAA can detect hardcoded secrets and report them with the secret value redacted.
- **FR12:** APAA can detect orphan / dead code (no referencing requirement or caller). **[Tier B]**
- **FR13:** APAA can attach at least one verifiable locator to every finding, or reject the finding.
- **FR14:** APAA can convert a tool failure or unestablishable-traceability condition into a finding rather than a crash.

### Release-Readiness Verdict
> **Verdict vocabulary (canonical).** The negative-assurance ladder runs `RELEASE_READY` → … → `NOT_READY_FOR_RELEASE`; **`BLOCKED` is the demo shorthand for a blocking (`NOT_READY`) outcome** — the two names denote one concept. **`INSUFFICIENT_COVERAGE`** is a distinct *not-assessed* state (coverage below the 20% floor), **not** a blocking verdict. Downstream artifacts use this vocabulary.

- **FR15:** APAA can compute a release-readiness verdict as a pure function of the coverage ledger.
- **FR16:** APAA can emit a verdict only when coverage gates are met (≥60% deep + all critical subsystems deep + 0 blocking findings), and emit `INSUFFICIENT_COVERAGE` below the 20% floor — never a default block.
- **FR17:** APAA can express every verdict in negative-assurance terms with a scope statement, materiality bar, disclaimer, and point-in-time stamp.
- **FR18:** An integrator can consume the verdict as a deterministic exit code and a machine-readable artifact.
- **FR33:** APAA can order findings by verdict impact — surfacing verdict-blocking findings before non-blocking ones — so a blocking 🔴 is never buried beneath lower-severity noise (serves the "actionable / no cry-wolf" success criteria; alarm-fatigue defense, risk H2).

### Self-Audit & Trust
- **FR19:** APAA can run an adversarial Prosecutor pass that challenges whether the ledger justifies the verdict and downgrades an unearned verdict. **[Tier B]**
- **FR20:** APAA can validate its own detectors against defect cartridges with golden expected-findings keys, asserted in CI.

### Cost Governance
- **FR21:** An operator can set a budget ceiling for an audit.
- **FR22:** APAA can halt on budget exhaustion, mark the remainder `skipped`, downgrade coverage, and report honestly — never fabricating or silently overrunning.

### Governance, Escalation & Evidence Integrity
- **FR23:** APAA can halt at a human STOP/PROCEED gate on a pattern-matched escalation condition, defaulting to STOP — and on gate timeout (no response within a configured window) it **parks at STOP, never auto-PROCEEDs** (time-boxed-gate default, Q-A).
- **FR24:** APAA can record a human escalation decision in an append-only decision record (and log the STOP even if the record is deferred). **[Tier B]**
- **FR25:** APAA can wrap every artifact in a content-hashed, schema-versioned envelope.
- **FR26:** APAA can verify referential integrity of its on-disk state (no dangling references). **[Tier B]**
- **FR27:** APAA can reproduce the same verdict for the same repository and APAA version.
- **FR28:** APAA can redact secrets from stored excerpts and never emit source/secret bytes into ledgers, evidence, logs, or traces.
- **FR29:** An operator can export an evidence bundle (coverage ledger, scope statement, findings, verdict); the operated-service path retains no source.

### Invocation & Resumability (headless)
- **FR30:** An integrator can invoke APAA headlessly with `repo + commit + budget + materiality_bar` and receive a verdict artifact + exit code.
- **FR31:** APAA can resume an interrupted audit from its on-disk `.apaa/` state.
- **FR32:** APAA can run to completion on a sequential (least-capable) host, producing byte-identical on-disk state to a parallel run.

## Non-Functional Requirements

### Determinism & Reproducibility *(the keystone quality attribute)*
- **NFR-D1:** Given the same repository at the same commit and the same APAA version, APAA produces an **identical verdict and identical coverage ledger — 100% reproducibility** across runs, achieved by **local content-addressed memoization** of recorded findings (key = content-hash + model checkpoint + APAA version; a cache hit returns the recorded result). This is the mechanism — *not* an assumption that the LLM repeats itself (bit-identical LLM output is infeasible). The shared cross-run cache (Minions layer **e**, V4) is a later optimization, never V1's sole guarantee.
- **NFR-D2:** The verdict gate and coverage-ledger mechanics are deterministic and testable with **zero LLM tokens** (pure functions over recorded findings).
- **NFR-D3:** Artifact content hashes cover the **canonical payload only** (excluding volatile `run_id`/`created_at`), so identical inputs yield identical hashes (a determinism golden-test gates the envelope before any consumer).

### Security & Data Protection
- **NFR-S1:** Source code, prompts, responses, and API-key bytes **never** appear in coverage ledgers, evidence bundles, logs, OTLP spans, exception traces, or any response — enforced by a security test suite that **blocks CI on failure** (mirrors Minions §3.8 / `tests/security/`).
- **NFR-S2:** Secret values detected in audited code are **redacted before storage**; the stored form carries a `contained_secret` flag without the secret value.
- **NFR-S3:** On the operated-service path, **customer source is never retained** after an audit completes.
- **NFR-S4:** An auditor agent can read **only** the files in its work-manifest (permission boundary); off-scope reads are impossible.
- **NFR-S5:** All filesystem writes are **containment-checked** (no path traversal, symlink, or sibling-prefix escape), reusing Minions workspace-containment patterns.

### Cost Efficiency *(the scariest risk — token economics)*
- **NFR-C1:** A baseline full audit costs a **bounded fraction of the audited repo's build cost** (tracked target ≤ 10–20% baseline; ~1% for V2 incremental diff-scoped runs). V1 measures and reports the baseline.
- **NFR-C2:** An audit **never exceeds its declared budget ceiling**; on exhaustion it halts deterministically with no silent overrun.
- **NFR-C3:** Deterministic, **zero-token tools perform breadth** so LLM spend is reserved for depth.

### Reliability & Honest Degradation
- **NFR-R1:** A tool/parse failure or unestablishable-traceability condition **degrades to a recorded finding or coverage downgrade — never an uncaught crash or a fabricated result.**
- **NFR-R2:** An interrupted audit is **fully resumable** from on-disk `.apaa/` state with no loss of prior coverage.

### Portability
- **NFR-P1:** APAA runs to completion on the **least-capable host (Cline, sequential)**, producing **byte-identical on-disk state** to a parallel-capable host; parallel is a pure speedup.
- **NFR-P2:** The audit is **stack-agnostic by construction** (deep AST-grounding = Python in V1; `claim_emitted` proxy elsewhere); no host- or stack-specific logic in the ledger/verdict core.

### Auditability & Evidence Integrity
- **NFR-A1:** Every artifact is wrapped in a **schema-versioned, content-hashed, prev-hash-chained envelope**; schemas evolve **additive-only**.
- **NFR-A2:** Referential integrity of on-disk state is **verifiable** (no dangling references). **[Tier B]**
- **NFR-A3:** Every verdict carries a **scope statement, materiality bar, disclaimer, and point-in-time stamp** (negative-assurance, no over-claim).

### Scale Envelope *(V1 bounds — not user-growth scalability)*
- **NFR-SC1:** V1 audits operate within a **bounded context budget** (target ≤ 40 files / 15k LOC per audit unit; hard ceiling ≤ 60 / 25k); larger repos partition into units. Full **10k → 500k LOC** scaling (multi-partition + seam auditor) is **V2**.

### Maintainability
- **NFR-M1:** No single source file exceeds **1200 lines** (mirrors Minions §3.2); business logic stays out of entrypoints (strict modularity).
- **NFR-M2:** Frozen contracts are validated (**Pydantic v2 + JSON Schema**) and evolve **additive-only**.

**Skipped (justified):** *Accessibility* (headless — no UI/WCAG surface); *user-growth scalability* (V1 is internal; replaced by the repo-scale envelope NFR-SC1).
