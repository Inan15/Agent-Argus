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
    durableMoat: 'proven-not-asserted depth (self-audit: AST-grounded depth [~~Python V1, multi-language V2~~ **AST grounding delivered in V1 for every language in `argus/shared/source_languages.py`** — *amended 2026-08-10, Story 10.2; capability delivered by `sprint-change-proposal-2026-07-28.md`*] + Prosecutor + cartridges) makes audited_deep TRUE → compounds into proprietary concordance/precision/cartridge corpus (credibility flywheel)'
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
  - _bmad-output/design-artifacts/ArgusAgent/product-brief-apaa.md
  - _bmad-output/design-artifacts/ArgusAgent/product-brief-apaa-distillate.md
  - _bmad-output/design-artifacts/ArgusAgent/research-market-2026-06-17.md
  - _bmad-output/design-artifacts/ArgusAgent/research-domain-2026-06-17.md
  - _bmad-output/design-artifacts/ArgusAgent/research-technical-2026-06-17.md
  - _bmad-output/brainstorming/brainstorming-session-2026-06-16-201450.md
  - _bmad-output/project-context.md
  - CLAUDE.md
documentCounts:
  briefs: 2
  research: 3
  brainstorming: 1
  projectDocs: 2
workflowType: 'prd'
updated: 2026-08-03
amendments:
  - date: 2026-08-03
    scope: 'FR16 + FR4 (contract change) — verdict decision table reordered so findings are evaluated before coverage; INSUFFICIENT_COVERAGE widened to cover a zero-findings unmet gate; critical-set eligibility predicate added'
    signal: _bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-03.md
    approvedBy: XAgent007
    sections: ['Technical Success (coverage gates enforced)', 'Verdict vocabulary (canonical)', 'FR16', 'FR4']
  - date: 2026-08-10
    scope: 'V1.5 public release — the ≥80%% precision gate becomes absolute for ATTESTED externalization and DEFERRED for a free public release under two binding FR34 conditions (enforced disclosure + a committed programme to clear it, Epic 13); tertiary independent-developer persona added; local agent-integration surface admitted (stdio MCP + command assets), hosted network surfaces still V4; V1.5 phase defined; FR34/FR35/FR36/FR37 and NFR-S6/NFR-P3 added. The gate remains NOT CLEARED and this amendment does not clear it.'
    signal: _bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-10b.md
    approvedBy: XAgent007
    sections: ['What Makes This Special', 'Success Criteria', 'Project Classification', 'Product Scope (V1.5)', 'User Journeys (J6)', 'Developer Tool (distribution, skips)', 'FR34', 'FR35', 'FR36', 'FR37', 'NFR-S6', 'NFR-P3']
  - date: 2026-08-11
    scope: >-
      standards_refs[] + CWE-required-on-security-findings is RECLASSIFIED V1 -> V2 at ALL THREE measured sites,
      struck-not-deleted: (1) Product Scope V1 Core, (2) Compliance & Regulatory 'Standards anchoring (phased)' --
      a SECOND, independently-binding V1 site carrying the ^CWE-\d+$ format commitment, named in no planning
      document between 2026-08-03 and 2026-08-11 -- and (3) Growth Features (V2), where the merge into the
      pre-existing 'standards mapping (CWE/ASVS/ISO 25010/SLSA)' item is recorded AT THE DESTINATION so the
      reclassification cannot read as 'it was always V2'. Journey 4 gains a dated consequence note naming FR11 as
      the one security-category finding producer the gap applies to. FR23/FR24/FR26/FR29 are amended
      struck-not-deleted to record that each is DELIVERED AS A LIBRARY SEAM with no production call site reachable
      from argus/cli.py, with owners, reasons and the cut-order cost of FR23's de-scope stated. No code ships: the
      finding schema version is unchanged and argus/** is byte-unchanged. The >=80% precision gate remains NOT
      CLEARED and this amendment does not clear it.
    signal: _bmad-output/design-artifacts/ArgusAgent/stories/10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1.md
    approvedBy: XAgent007
    sections: ['Product Scope (V1 Core)', 'Compliance & Regulatory (Standards anchoring)', 'Growth Features (V2)', 'User Journeys (Journey 4)', 'FR23', 'FR24', 'FR26', 'FR29']
---

# Product Requirements Document - APAA (AI Project Assurance Audit)

**Author:** XAgent007
**Date:** 2026-06-17 · **Amended:** 2026-08-03 (FR16 / FR4 — see frontmatter `amendments` and `addendum.md`)

## Executive Summary

`GitHub: green · Sonar: green · APAA: 🔴 tests appear vacuous`

That one line is the product. AI agents now write software faster than any team can verify it, and the tools meant to help quietly make the problem worse: an AI code reviewer that says "looks good" almost never tells you **how much of the repo it actually looked at**. APAA (AI Project Assurance Audit) closes that gap. You point it at a repository built by AI agents or spec-driven development, and it returns a **coverage-grounded, release-readiness verdict** — *"No release-blocking findings within the audited coverage envelope"* — never the lie that "the code is correct."

**Near-term vision (V1):** APAA gives XAgents teams a **repeatable, deterministic** release-readiness verdict — **decision-support they gate their own release on**, never a tool that decides for them — backed by a coverage ledger that is **scope-bounded evidence of what was examined** (negative assurance), defensible to a VP or a regulator. **North Star:** coverage-grounded assurance becomes the default expectation for AI-built software — the way "did your tests pass?" is today.

**The problem it solves.** Three things are simultaneously true about AI-generated code: the defects are real and measurable (~1.7× more issues than human-written; 110,000+ surviving AI-introduced issues counted in production repos, Feb 2026); the tools that should catch them are either trusted blindly or so noisy they're ignored (SAST at 40–60% false positives, a passing AI-written test taken at face value); and **no one can say how much was actually checked**. The result is a credibility gap — a green check mark that means "some tool ran," not "this is safe to ship" — exactly when regulated buyers increasingly need *defensible evidence* that AI-built code was genuinely examined.

**Who it serves.** Primary (V1): the internal XAgents platform owner — Engineering Lead / Delivery Orchestrator running audits on XAgents-built repos, with the first dogfood target being **Minions itself**. Secondary (standalone path): the regulated enterprise (banks, healthcare, telecom, automotive, aerospace) needing defensible AI-code sign-off evidence for its EU AI Act / ISO 42001 / SOC 2 readiness story. **Tertiary (V1.5, free public tier): the independent developer** — students, solo builders, OSS maintainers, and small teams — building with a coding agent and needing to know whether the code that agent just wrote is actually tested. This persona is defined by **context, not skill level**: no procurement, no compliance mandate, no internal champion, and no colleague who already knows the tool. Scoped **exclusively to the unattested free tier** — verdicts are decision-support for their own work, never assurance evidence, and **their usage does not advance the precision gate**. *(Amended 2026-08-10b.)*

**Why now.** Generation is commoditizing and value has moved downstream to *verification* ("verification is the new bottleneck"); the AI-code-quality crisis is measurable and publicized; **EU AI Act high-risk obligations bite August 2, 2026**; and the "AI release-readiness assurance" category is **still unclaimed** — incumbents sort into find-more-bugs, find-vulns, check-my-tests, or govern-my-models, and none ships a coverage-grounded release verdict.

### What Makes This Special

APAA is an **assurance** tool, not an AI code reviewer or a security scanner — categories it deliberately avoids. Its differentiation is a two-layer claim:

- **The wedge (what wins the first look):** a **machine-verifiable coverage ledger** plus **AI-specific defect detection led by vacuous-test detection**. Every file lands in a fixed-enum ledger (`audited_deep` / `audited_shallow` / `tool_scanned_only` / `inferred` / `skipped`), and the verdict is a **pure function** of that ledger — it literally cannot be minted without enough `audited_deep` evidence. The vacuous-test detector catches what AI agents *specifically* produce: passing tests that assert nothing. *Honesty is mechanical, not promised.*
- **The durable moat (why a fast-follower can't copy it):** *proven, not asserted, depth.* `audited_deep` requires a **grounded claim validated against the repo's AST** (~~Python in V1; multi-language in V2~~ **delivered in V1 for every language enumerated in `argus/shared/source_languages.py`** — *amended 2026-08-10, Story 10.2; the capability shipped via `sprint-change-proposal-2026-07-28.md` with no story and no amendment, `DF-AUD-APAA-D`*) — silence auto-downgrades to shallow. An adversarial **Prosecutor** is paid to prove the verdict unearned, and **defect cartridges** (minimal repos with one planted defect + a golden key, CI-asserted) empirically measure what the detectors catch. Run on real repos, this discipline compounds into a proprietary **concordance / precision / cartridge corpus** no competitor can replicate from the demo. This self-audit is near-zero-token determinism work — *not* an LLM-spend multiplier.

**The core insight:** every other AI-review tool silently implies *"I looked at everything."* It didn't — and that unfalsifiable claim is the gap. APAA makes audit confidence **falsifiable**, and adopts **negative assurance** ("no blocking findings *within the audited envelope*," never "correct") — the same humility that makes financial audits credible and the correct legal/commercial posture. To the user, the self-audit is invisible; what they buy is its output — *a coverage % you can defend to your VP* and *a 🔴 that doesn't cry wolf*. The honesty keystone is explicit: **APAA must hit ≥80% finding-precision before any *attested* externalization** — any use in which a verdict is presented as assurance evidence (commercial, enterprise, regulated, or operated-service). **Status: NOT CLEARED.** A *free public distribution* may precede the gate only under the two binding conditions of FR34: the tool's own unvalidated status is mechanically disclosed on every user-facing verdict surface, **and** a scheduled programme to clear the gate is committed and in flight. Absent either condition the bar is absolute. *(Amended 2026-08-10b.)* (The coverage-ledger schema is versioned, content-hashed, and additive-only from day one, keeping a V4 "open attestation standard" ambition alive at zero V1 cost — seeded, not foregrounded.)

## Project Classification

- **Project Type:** Headless **developer-tool / CLI Skill** (a CLI + committed `.apaa/` filesystem convention, a local agent-integration surface, and a sequential fallback host) — primary; **contract-producer** (frozen JSON schemas + deterministic exit-codes) — elevated secondary. **Headless-only** — verdicts and evidence are artifacts and machine surfaces, never screens (no UI/UX).
  **Excluded from V1/V1.5 — *hosted network* surfaces:** a hosted repo-URL runner and any HTTP API (endpoints, auth, rate-limits, published SDK, API versioning) remain **V4**.
  **Admitted in V1.5 — the *local* agent-integration surface** *(added 2026-08-10b)*: an MCP server and packaged assistant command assets, so a coding agent can invoke an audit and read the verdict. This is **not** a relaxation of the exclusion above; it is bounded by four binding constraints:
  1. **Local transport only** — stdio. No network listener is opened, no port is bound.
  2. **No HTTP stack.** The `argus.* ⊬ fastapi` import-isolation gate holds unchanged, and ADR #20's *"downstream of the HTTP/A2A boundary — takes no A2A token, registers no route"* classification is preserved verbatim.
  3. **No new authority.** The surface invokes the same pure `AuditRequest → AuditVerdict` path as the CLI, under the same work-manifest permission boundary (NFR-S4). It grants no capability the CLI does not already have.
  4. **No credential handling.** It accepts and stores no keys, tokens, or accounts.

  The distinction is *local process* versus *hosted service*: the excluded surface is one that runs somebody else's audit on somebody else's machine. This one runs the user's audit on the user's machine and speaks a protocol instead of a shell.
- **Domain:** AI software assurance / DevTools, compliance-adjacent. Compliance (EU AI Act / ISO 42001 / SOC 2) is a **secondary/roadmap** driver in V1, not the headline.
- **Complexity:** **High** — driven by determinism-as-a-requirement, self-auditing, and liability posture (not merely regulated buyers).
- **Project Context:** **Greenfield** product, **brownfield-adjacent** in engineering — it reuses proven Minions infrastructure (hash-chained ledger ADR #18, permission tiers, budget guardrails, `adapter_portability`, deterministic orchestration) and dogfoods on the Minions repo.
- **Scope:** This PRD specifies **APAA V1 — the 90-day MVP** (coverage honesty + release-readiness verdict + the vacuous-test moat). V2–V4 are captured as a roadmap appendix, not V1 commitments.

## Success Criteria

The V1 bar is deliberately an **evidence bar, not a usage bar** — success is whether a designated senior engineer independently trusts APAA's verdicts, not user counts or revenue. **The one bar that gates attested externalization: ≥80% finding-precision. Everything commercial waits behind it — without exception.** A free public release is permitted ahead of the bar under FR34's two conditions (enforced disclosure + a committed programme to clear it); it confers no attested status, and **usage is not evidence** — adoption cannot advance the precision gate, only adjudicated findings can. *(Amended 2026-08-10b.)*

### User Success
*(Primary user = the Engineering Lead / Delivery Orchestrator running APAA on an XAgents repo.)*
- **Repeatable "aha":** on a repo with hidden defects, APAA surfaces ≥1 real issue every other tool called green — and **shows its evidence** (`APAA 🔴`, repeatable).
- **Actionable, not a hedge:** a plain-English line (*"BLOCKED — 3 vacuous tests, coverage 62% deep"*) the user acts on while retaining the decision (decision-support, not decision-maker).
- **Answers the VP question** — *"how much did it actually look at?"* — from the coverage ledger.
- **No cry-wolf:** a 🔴 is credible enough to forward to the team, not mute.

**Tertiary user success (independent developer, free tier).** *Added 2026-08-10b.* The bar is **unassisted first-run utility** — not because the user is inexperienced, but because **there is no one to ask.** An internal user has a colleague who knows the tool; a public user has the tool's own output and nothing else.
- **No dead ends.** Every terminal outcome — including `INSUFFICIENT_COVERAGE` — names why it was reached and the next action that changes it, **in the tool's own output**. A developer with no internal support cannot be sent to a wiki. A verdict the user cannot act on from what's on screen is a product failure, not an honest result.
- **Reachable from the agent.** The audit is invocable from inside the coding assistant that wrote the code, and the verdict is machine-readable enough for that agent to act on without a human relaying it.
- **Works on their stack out of the box.** The default public install grounds the languages a developer actually uses; degraded coverage caused by a missing optional grammar is a packaging defect, not a user error.
- **Free and private by default.** The default run costs nothing, requires no account or key, and sends no source code anywhere. Any run that would transmit source is opt-in and says so before it runs.

### Business Success
*(V1 = readiness-to-externalize, not revenue.)*
- **Attested-externalization gate:** ≥80% finding-precision on the validation set. **Current status (2026-08-10): NOT CLEARED** — `protocol_cleared` is `False` and has never been set `True`; ~~the corpus stands at N=1 and is a self-audit, not an independent run~~. Clearing it is scoped as **Epic 13**. *(Amended 2026-08-10b.)* — **CORPUS FIGURE CORRECTED 2026-08-17 (Story 13.3 / AC6, `DF-8-5-C`'s class in prose).** The struck clause was the measured state on 2026-08-10 and was false from 2026-08-16 onward; it is struck rather than erased because it was the state the sentence around it was written in (§3.4). **Measured now, derived from `tests/corpus/_manifest.eligible_member_count()` and never typed: `N = 5` eligible members — five independent real repositories, operator-RATIFIED under Story 13.1 / AC3b**, all five byte-reproducible across two runs. **The NOT-CLEARED status above is unchanged and is not weakened by this correction:** the corpus floor is ONE of protocol §5's four conditions, and Story 13.3 recorded the decision over the committed adjudication record as **`BLOCKED`** — 26 of the 31 emitted blocking findings carry a live TP/FP disposition from the named human (XAgent007, 2026-08-17) and **5 remain `BORDERLINE` with protocol §4's ladder unterminated**, so the run is NOT exhaustively adjudicated and no §5 outcome was taken. `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/gate-decision-record.json` carries the derivation, the per-condition verdicts and the closure path. ⚠️ **Concentration of the measured population, disclosed (Story 13.3 / AC3b):** the 31 findings come from **2 of the 5** ratified members and from a **single rule class**; §5's `N ≥ 5` is satisfied by member COUNT, so the N that gates and the N that contributes are different numbers.
- **Credibility flywheel turning (measurable):** each dogfood run emits ≥1 reusable asset — audit report, concordance label, calibration datum, or (on a miss) a new defect cartridge.
- **Strategic question answered:** APAA auditing Minions resolves *"does Minions have an audit agent?"* with a real artifact.

### Technical Success
- **Verdict is a pure function of the ledger** — unit-tested vs synthetic ledgers, **0 LLM tokens**.
- **Coverage gates enforced:** `RELEASE_READY` requires **≥60% `audited_deep` + all critical subsystems `audited_deep` + 0 blocking findings**; `inferred` can never satisfy a gate; **an unmet coverage gate emits `INSUFFICIENT_COVERAGE` ("not assessed") — never a default `NOT_READY`** — whether coverage fell below the 20% floor or merely short of the 60% / critical-subsystem bar with nothing found (low coverage is APAA's limitation to report, not the repo's failure to bear). `NOT_READY_FOR_RELEASE` is reserved for **≥1 verdict-blocking finding**.
- **Reproducible verdict** via **local content-addressed memoization** of recorded findings (cache key = content-hash + model checkpoint + APAA version → a re-run returns the *recorded* result). Content-hashing *addresses* artifacts; memoization *reproduces* them.
- **Self-audit green in CI:** V1 cartridges (vacuous test, hardcoded secret, orphan function — 3 = full V1 / Tier B; the cut-order floor is 2) detected vs golden keys; integrity lint passes; secrets redacted before storage.
- **Honest degradation:** budget ceiling halts → marks `skipped` → downgrades → reports truthfully; tool failure becomes a *finding*, never a crash.
- **Runs on the least-capable host:** the sequential code path produces **byte-identical on-disk state** (determinism test, host-independent — not contingent on Cline hardware).

### Measurable Outcomes
| Metric | Target |
|---|---|
| **Finding precision** (🔴 judged genuinely real by an independent senior engineer) | **≥ 80%** (precision tuned over recall) — *(Confirmed as GOVERNING 2026-08-16, Story 13.1 / DN-1: this row, not `precision-validation-protocol.md` §5, defines the corpus the gate is measured over. The adjudicator is the named human XAgent007; the planted-defect cartridges measure **recall**, not this.)* |
| **Verdict concordance (asymmetric)** | **Zero false-`RELEASE_READY`** on the validation set (the fatal error); false-blocks bounded but acceptable |
| **Moat hit-rate** | **≥ 1** real issue other tools missed, **on repos known to contain hidden defects** (0 on a genuinely clean repo is *correct*, not a miss) |
| **Reproducibility** | 100% (same repo + version → same verdict) |
| **V1 cost outcome** | a full APAA audit of Minions completes within a pre-set budget ceiling $X, and the ceiling demonstrably halts + downgrades when breached |
| **Validation set** | **N ≈ 5–10** real XAgents repos, ~~starting with **Minions**~~ — *(Amended 2026-08-16, Story 13.1 / DN-1.* **This row GOVERNS**, and `precision-validation-protocol.md` §5's conflicting `N ≥ 5` **labeled cartridges** floor was struck: two corpora, never reconciled, decided in favour of real repositories because a gate clearable by a corpus the team planted and answered is not an externalization gate. *The Minions start is struck as unachievable, not as unwanted:* the Story 7.2 Minions run *"can never be re-derived in this repository"* (`deferred-work.md:832-836`) and Story 8.5 replaced it with a self-audit of `argus/`. **Membership is now closed and machine-readable** — `tests/corpus/_manifest.py`, with pinned shas, licences, provenance and recorded exclusions; the floor is derived, reusing `VALIDATION_SET_FLOOR_N = 5`. ~~**Measured 2026-08-16: N = 0 eligible members** — the corpus is specified and empty, awaiting operator ratification (13.1/AC3b)~~ **superseded the same day: the operator RATIFIED five members under 13.1/AC3b, so `N = 5` eligible members and the floor is MET.** Each was measured before admission (pin resolved, language mix folded through `source_languages.py`, licence checked) and audited through the unmodified pipeline, all five byte-reproducible; **31 blocking findings** await human adjudication (13.2). The struck figure is kept because it was the state the *decision* was taken in. **The gate is NOT cleared:** the floor is one of four §5 conditions and the other three are unmet.*) |
| **Validation protocol (a V1 deliverable)** | defines who validates, expert-hours/repo, the **precision-adjudication method** (sample size, who judges a 🔴 "genuinely real"), and per-metric pass/fail |

## Product Scope

### MVP — APAA V1 (90-day)
Two layers, both required (trustworthy **and** demoable). Sequential-canonical, filesystem state under `.apaa/`, deterministic throughout.
- **V1 Core:** shared **envelope** (schema_version + content-hash determinism + secret-redaction) · schemas **finding ① / severity.rubric ② / coverage_ledger ③ / verdict ⑧ / decision_record ④ (minimal)** · ~~`standards_refs[]` field + **CWE-required-on-security findings** (day-one additive; rich mapping → V2)~~ **— reclassified to V2 on 2026-08-11 by Story 10.5 (DN-1); merged into §Growth Features (V2)'s existing standards-mapping item, see frontmatter `amendments`** · **pure-function verdict gate** · **referential-integrity lint** · **human STOP/PROCEED escalation** with **R1 pattern-matched (not LLM-judgment) escalation, default-STOP** · crude **budget ceiling** (Cost *Governance*) · stack detection + partitioning (≤40 files / 15k LOC) · `work_manifest` **concept** (minimal assignment = file-list = the auditor's **permission boundary**; full schema → V3) · **Python AST-grounded `audited_deep` claims**.
- **V1 Differentiator:** heuristic **vacuous-test detector** (assertion-density + mock-ratio, precision-tuned, advisory-framed) · **defect-cartridge framework** (cartridges #1–3, CI-asserted) · **lightweight Prosecutor** (one pass, final verdict gate only).
- **Proof:** dogfood run against **Minions itself**.

### V1 Design Invariants (forward-compatibility — constraints, not added scope)
- **Envelope determinism** is golden-tested + human-gated before any consumer (a bug here cascades to V1 reproducibility, the G4 cache, and the G1 substrate).
- **Grounded-claim validation is a stack-agnostic interface** (`claim → validated?`), Python = impl #1 — ~~so V2 multi-language is additive, not a core rewrite.~~ **and the additive multi-language implementations are delivered in V1, exactly as the interface predicted; the enumerated set is `argus/shared/source_languages.py`.** *(Amended 2026-08-10, Story 10.2; delivered by `sprint-change-proposal-2026-07-28.md`.)*
- **Reserve `partition_id`** in the coverage ledger (always `"root"` in V1) for the V2 seam auditor.
- **Frozen invariant declared now:** curated memory (G3, ships V4) **never touches the verdict/decision path**.
- **APAA specifies the cost/memory consumption-contracts** it will need from Minions (a)/(d)/(e).

### V1.5 — The Public Release *(added 2026-08-10b)*

**The cut-order's V1.5 (§Cut-Order) is vacant** — Tier B shipped complete and nothing slid. V1.5 is therefore defined here as the **first public distribution**, not as a catch-up phase.

V1.5 adds **no new assurance capability.** The verdict, the ledger, the detectors, and the determinism spine are V1 as delivered. What it adds is **reach and usability**: the tool becomes installable by someone outside XAgents, invocable from the agent that wrote the code, and honest about its own status while its precision is unvalidated.

- **Reach:** public index distribution · marketplace action · local agent-integration surface (FR35).
- **Usability:** actionable terminal output (FR37) · a default install that grounds the languages users actually write · reproducible re-runs via the already-specified memoization path (FR27 / NFR-D1).
- **Depth on request:** the opt-in LLM-backed deep pass (FR36), off by default.
- **Honesty about the instrument:** mandatory self-disclosure (FR34) while the ≥80% gate remains uncleared.

**V1.5 does not clear the attested-externalization gate and does not attempt to.** Clearing it is a separate, committed programme (§Success Criteria; Epic 13) resting on an independent corpus and human adjudication — neither of which is a build task, and neither of which V1.5 delivers.

**Unchanged by V1.5:** V2 growth features, V3 cost intelligence, and V4 assurance-platform / hosted-runner scope are exactly as recorded. V1.5 borrows nothing from them.

### Growth Features (V2)
Bidirectional traceability (orphan code + silent req gaps) · Production-Readiness-Review checklist · standards mapping (CWE/ASVS/ISO 25010/SLSA) · ~~**multi-language** AST grounding ·~~ **mutation-grade** vacuous-test detection · **seam / interface auditor** (+ honest V1 limitation: *no cross-partition seam analysis in V1*) · **holdout-cartridge rotation** + promote-a-miss · **multi-perspective adversarial panel** (Blind Hunter / Edge-Case Hunter / Acceptance Auditor — V1's single-auditor + lightweight Prosecutor is the deliberate cheap version) · **host-capability manifest** (`adapter_portability`, enables the parallel speedup) · **governance hardening** (proof-of-read / paste-back on high-stakes gates — anti-rubber-stamp, risk H1; matters at externalization scale, not for V1's single senior operator) · **consume the Minions Cost-Optimization layer (d)** for scaled audits (*APAA does not build L1–L4 — it calls them*).

> *(Amended 2026-08-10, Story 10.2 / AC1.2 — `DF-AUD-APAA-D`.)* **multi-language AST grounding is struck from this V2 list because it is delivered in V1**, by `sprint-change-proposal-2026-07-28.md`, which shipped the capability with no story and no specification amendment. Struck, not deleted (§3.4 evidence immutability). The set delivered in V1 is not restated here as a hand-typed list — it is `argus/shared/source_languages.py`, pinned by `tests/test_multilanguage_audit.py`. **Every other item on this line is untouched and remains V2.** A delivered capability left on the growth roadmap double-counts the work; `tests/test_spec_claim_scope.py` now fails if one reappears.

> *(Amended 2026-08-11, Story 10.5 / AC1.3 — a **recorded merge**, not a new bullet.)* The *standards mapping (CWE/ASVS/ISO 25010/SLSA)* item above is unchanged in wording and **already existed**; what changed is that **a V1 commitment was reclassified into this V2 item** on 2026-08-11 — the `standards_refs[]` field plus CWE-required-on-every-security-category-finding, with its `^CWE-\d+$` format validation, struck from §Product Scope V1 Core **and** from §Compliance & Regulatory. It is recorded **here, at the destination**, for a reason that is the exact inverse of Story 10.2's: 10.2 found a *delivered* capability still sitting on the growth roadmap, which **double-counts** the work; an *undelivered* V1 item absorbed silently into an existing V2 item would **under-count** it, and would leave no trace that anything had ever been promised for V1. Reclassification must be discoverable from the destination and must never read as *"it was always V2"*.

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

> ⚠️ **Known trade, recorded 2026-08-11 (Story 10.5 / AC2) — what Dana's bundle does NOT carry.** In V1 a security-category finding carries **no standards reference**: no `standards_refs[]` field and no CWE id, because that commitment was reclassified to V2 on this date (§Compliance & Regulatory, §Product Scope V1 Core). The evidence bundle is therefore **weaker compliance evidence than §Compliance & Regulatory previously implied** — Dana's legal team must map findings to CWE themselves. **Exact scope of the gap:** V1's one security-category finding producer is **FR11** (hardcoded-secret detection), so this applies to FR11's findings and to no others; FR10's vacuous-test findings and FR12's orphan-code findings are not security-category. **This does not make any user worse off today than the standing gate already permits:** Journey 4 is the attested / operated-service path, and the ≥80% finding-precision gate holds it at **NOT CLEARED** (§Business Success; Epic 13 owns clearing it). ⛔ **Nothing here clears, softens, schedules or re-scopes that gate**, and this note must not be read as doing so. **The re-entry point:** V2's *standards mapping (CWE/ASVS/ISO 25010/SLSA)* item, into which the V1 commitment was merged; filed as `DF-10-5-D` in `deferred-work.md` so it is discoverable from the ledger rather than only from this paragraph.

### Journey 5 — The CI pipeline / orchestrating agent (API · system-to-system, headless): "repo in, verdict out"
**Situation.** An automated pipeline (or a Minions Flow Orchestrator) must gate a release with **no human in the loop** at run time.
**Rising action.** It invokes APAA headlessly against a repo at a pinned commit, passing a budget and a materiality bar. APAA writes the `.apaa/` artifact tree and emits a structured **verdict artifact + deterministic exit code**.
**Climax.** The pipeline reads the exit code: `RELEASE_READY` → proceed; `BLOCKED` → halt + attach findings; `INSUFFICIENT_COVERAGE` → escalate to a human STOP gate (never auto-proceed). Every decision is machine-consumable and reproducible.
**Resolution.** The release pipeline now carries a coverage-grounded gate another system can act on. New reality: assurance becomes a pipeline primitive, not a manual review.
*Reveals:* headless invocation contract (repo + commit + budget + materiality → verdict artifact + exit code) · machine-readable `.apaa/` artifacts · deterministic exit-code semantics · human-STOP escalation on the non-deterministic case · commit-pinned reproducibility.

### Journey 6 — Sam, independent developer (tertiary · free tier): "is what my agent just wrote actually tested?"
**Situation.** Sam is building a project largely with a coding agent. It generates quickly and it generates tests, and the suite is green. Sam has no reason to trust the green — the agent wrote the code *and* the tests, and nothing external has checked whether those tests examine anything. There is no CI team, no staff engineer, and no budget. Whatever Sam learns has to come from a tool Sam can run alone.
**Opening scene.** Sam installs from the public index and invokes the audit from inside the coding assistant — the same session that wrote the code. No account, no key, no configuration. The default run is free, offline, and sends no source anywhere.
**Rising action.** The audit grounds what it can against the repo's AST and records the rest honestly. The output is not a score: it is a ledger stating which files were examined deeply, which were tool-scanned, and which were skipped — plus findings against the tests themselves. The tool also discloses its own status: its finding-precision has not yet been independently validated, and it says so without being asked.
**Climax.** Several of the agent-written tests are reported as appearing vacuous, each carrying its evidence — assertion counts, mock ratios, and whether the test body reaches the code under test at all. This is the thing Sam's green suite could never have surfaced, and it arrives on a free run.
**Resolution.** The verdict names the coverage it did *not* achieve and the single next action that changes it — an opt-in deeper pass, scoped and budget-capped, which Sam runs against the one subsystem that matters. Sam fixes the tests, re-runs, and the result is reproducible. The agent that wrote the code reads the verdict and acts on it directly. **New reality:** the loop that generated the code now contains something that checks it, and Sam can say what was examined and what was not.
*Reveals:* public-index install · agent-integration surface (MCP + command assets) · free, offline, zero-key default run · vacuous-test findings with evidence on the default path · coverage ledger as the honest remainder · **actionable terminal output — every outcome names its next action** · opt-in budget-governed deep pass · mandatory self-disclosure of unvalidated precision (FR34) · reproducibility.

> ⚠️ **Measured dependency, recorded rather than assumed.** Whether a default-path vacuous finding is **verdict-blocking** or **advisory-only** is a measurement, not a design choice: heuristic-only findings are advisory by contract, and verdict-eligibility requires AST grounding. This journey deliberately does **not** presume the answer — it holds either way, because the value Sam receives is the evidence-bearing finding plus the honest remainder, not the enum. **Epic 12's deep-audit story owns the measurement and must record it as a yes or a no. A "no" escalates; it does not soften this journey.**

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
| **Agent-integration surface** (MCP + packaged command assets; local stdio, no network listener) | **J6** |
| **Actionable terminal output** (every outcome names why it was reached and the next action that changes it) | **J6** |
| **Mandatory self-disclosure of unvalidated precision** (FR34, mechanically enforced, removable only on measurement) | **J6** |

## Domain-Specific Requirements

APAA operates in **AI software assurance** — a compliance-*adjacent* domain. It is **not** a certified attestation service; it produces a **code-artifact evidence layer** that *feeds* a buyer's compliance story. Every requirement below is filtered through the negative-assurance, no-over-claim posture.

### Compliance & Regulatory
- **Negative-assurance framing is mandatory, not stylistic.** Verdicts borrow the *language and posture* of mature assurance disciplines (financial audit's "presents fairly, in all material respects"; SOC 2 scope+period; ISO/DO-178C rigor) **strictly as analogies, never as claims APAA has earned**. SOC 2 / "reasonable assurance" are CPA-owned terms; APAA must not imply certification. Every verdict ships a `scope_statement`, a materiality bar, a `disclaimer`, and a point-in-time stamp.
- **Standards anchoring (phased).** **V1:** ~~`standards_refs[]` field (format-validated, e.g. `^CWE-\d+$`) + **CWE required on every security-category finding** (the cheapest, most mechanical, highest-stakes mapping)~~ **— reclassified to V2 on 2026-08-11 by Story 10.5 (DN-1). The `^CWE-\d+$` FORMAT commitment moves with it. This was a SECOND, independently-binding V1 site, in a different section and a different sentence shape from the §Product Scope one, and it was named in no planning document between 2026-08-03 and 2026-08-11; amending only one site would have left this PRD self-contradicting.** **V2:** broader mapping to OWASP ASVS, NIST SSDF, SLSA, ISO/IEC 25010.
- **EU AI Act as forcing function, not a claim.** High-risk obligations (Aug 2, 2026) are *why* regulated buyers need defensible AI-code evidence — APAA's coverage ledger plugs into their EU AI Act / ISO 42001 / SOC 2 *readiness* artifacts; it does **not** itself certify conformance.
- **Liability surface (M2).** A release verdict is a liability surface. Disclaimers, scope boundaries, and point-in-time stamps are non-negotiable on every emitted verdict.

> *(Amended 2026-08-11, Story 10.5 / AC1 — the `standards_refs[]` decision, reasoned rather than asserted.)* **The V1 standards commitment is reclassified to V2 at both of the sites that bound it** (here and §Product Scope V1 Core), and merged into the existing V2 *standards mapping (CWE/ASVS/ISO 25010/SLSA)* item. **Four reasons, in the order they carry weight.** (a) The 2026-08-03 case *for* shipping it was explicitly that it is *"far cheaper now than after the finding schema is frozen"* (`implementation-readiness-report-2026-08-03.md` F2). The `finding` schema is **now frozen, content-hashed and shipped** under NFR-A1/NFR-M2 additive-only — **the premise expired.** (b) A persisted `standards_refs[]` widens the persisted and redaction surface (NFR-S1/S2) that Epic 4 spent a whole story bounding. (c) The audience it serves is **Journey 4 / attested, operated-service use**, which the ≥80% finding-precision gate holds **NOT CLEARED** regardless — so shipping the field today serves **no reachable user**. (d) The binding capability contract (§Functional Requirements) never listed it, so by the contract its absence in the code was already correct; what was wrong was this document. The decision is **reversible at the cost of a spec amendment** and costs nothing to revisit in V2. **This also disposes the F2/CWE half of `AI-E8-9` — and only that half:** `AI-E8-9`'s F4 (`SC-E`), F10 (`architecture.md`) and D1 (config drift) are **still open and are not Story 10.5's.** The consequence for Dana is recorded at §User Journeys → Journey 4; the V2 re-entry point is filed as `DF-10-5-D`. `tests/test_v1_commitment_closure.py` fails if either site loses its strike.

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
- **The ≥80% finding-precision bar** on **N ≈ 5–10 real repositories** is the gate before any **attested** externalization. ⚠️ **The Minions dogfood no longer counts toward N** — Story 8.5 re-derived it as a self-audit of `argus/`, and the record states the independent run *"can never be re-derived in this repository."* The corpus is therefore **N=1 and self-referential**; Epic 13 rebuilds it from independent repositories. *(Amended 2026-08-10b.)* **Further amended 2026-08-16 (Story 13.1 / DN-1): this bullet GOVERNS the gate's corpus**, and `precision-validation-protocol.md` §5's conflicting cartridge floor was struck. Membership is now closed and machine-readable — `tests/corpus/_manifest.py` — with the exclusions recorded **in the manifest itself**: the `argus/` self-audit (`provenance: self`) and the superseded Minions run (`provenance: superseded`, not re-derivable here) are both `eligible_for_n: False` with reasons, and the cartridges are not members at all because they measure recall. ~~N=1 and self-referential~~ is corrected by that accounting: ~~**the eligible corpus is `N = 0`, measured**~~ — the self-audit was never eligible, so counting it as "N=1" overstated a corpus that has always held zero independent members. **SUPERSEDED 2026-08-17 (Story 13.3 / AC6): `N = 5` eligible members, measured** — the `N = 0` was true when Story 13.1's DN-1 decision was taken and false by the end of the same day, when the operator RATIFIED five independent real repositories under 13.1 / AC3b. The figure is derived from `tests/corpus/_manifest.eligible_member_count()` and is never hand-typed (`AI-E9-7`); the zero is struck, not erased, because it was the state the corpus DEFINITION was decided in (§3.4). **The ≥80% bar above is still NOT CLEARED and this correction does not move it:** the floor is one of protocol §5's four conditions, and Story 13.3's committed gate decision is **`BLOCKED`** — the adjudication run is not exhaustive (5 of 31 findings `BORDERLINE`, §4's ladder unterminated), so no §5 outcome was taken. **Disclosed with the figure (13.3 / AC3b):** the 31 adjudicated findings are drawn from **2 of the 5** ratified members and one rule class — *the N that gates and the N that contributes are different numbers*, and this is disclosed, never corrected by narrowing the corpus.
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
APAA ships as a **headless Claude Code Skill** (Cline sequential fallback) that cold-reads a repository and emits a coverage-grounded verdict. It is simultaneously a **contract-producer**: its durable output is a set of **frozen JSON artifacts** under `.apaa/` plus a **deterministic exit code**. There is **no UI and no visual surface** (headless-only); integrators consume artifacts, exit codes, and the local agent-integration surface. **Stack-agnostic** by construction (~~V1 deep AST-grounding = Python, `claim_emitted` proxy elsewhere~~ **deep AST-grounding is delivered in V1 for every language enumerated in `argus/shared/source_languages.py`; the `claim_emitted` proxy carries anything outside that set, or any file whose grammar is absent** — *amended 2026-08-10, Story 10.2; delivered by `sprint-change-proposal-2026-07-28.md`*); hosts = Claude Code (parallel) + Cline (sequential-canonical). **Distribution.** *(Amended 2026-08-10b.)*

| Phase | Channel | Status |
|---|---|---|
| V1 | The committed (git-ignorable) `.apaa/` convention | Delivered |
| V1 | Operated-service evidence-bundle path | Delivered |
| **V1.5** | **PyPI** — `pip install argus-agent`, the primary public channel | **In scope** |
| **V1.5** | **GitHub Marketplace** — the composite action | **In scope, gated** on the `action.yml` input-interpolation fix |
| **V1.5** | **MCP server** — shipped in the same distribution as an entry point, no separate channel | **In scope** |
| **V1.5** | **Assistant command assets** — packaged files an installer places in the host's config | **In scope** |
| Deferred | Desktop application stores (Microsoft Store et al.) | **Deferred, not rejected** — requires MSIX/equivalent, a bundled runtime, a store identity, a published privacy-policy URL, and an age rating. **None exists.** Reopening requires un-skipping `store_compliance` first |
| Deferred | OS package managers (Winget / Chocolatey / Homebrew / Snap) | **Deferred** — each adds an independent packaging and update contract with no current owner |
| **V4** | Hosted repo-URL runner | Unchanged |

**"No IDE plugin" is retained in substance and restated precisely:** APAA ships no editor extension, no language server, and no rendered surface. The command assets are *configuration files* that teach an assistant to invoke the CLI; the MCP server is a *local stdio process*. Neither renders anything, and both are bounded by the four constraints in §Project Classification.

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

**Skipped (headless):** `visual_design`, `store_compliance`. *(Both **re-validated 2026-08-10b** against the V1.5 channel set and both **remain correctly skipped**.)*
- `visual_design` — no rendered surface is introduced. The agent-integration surface is a protocol and a set of config files.
- `store_compliance` — **conditionally skipped, with the reopening condition pre-committed:** it covers desktop-application-store obligations (store identity, age rating, content policy, bundled-runtime licensing, update channel). PyPI and GitHub Marketplace impose none of these. **This skip must be un-skipped, and its requirements scoped, before any desktop-store channel enters a sprint** — the condition is recorded here so the decision cannot be made implicitly by a packaging story.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy
- **MVP type: a problem-solving / validated-learning MVP**, not a feature MVP. Mantra: **prove organizations trust a coverage-grounded verdict BEFORE building anything else.** Trust is the product.
- **Minimum-useful = the two-layer V1:** coverage honesty (trustworthy) **+** the vacuous-test moat (demoable). Either alone fails.
- **"Has potential" moment:** the repeatable `GitHub green · Sonar green · APAA 🔴 tests appear vacuous` demo on the **Minions dogfood**.

### V1 has two grades — name which one you mean
- **Tier A — demo-grade (signature-demo core):** envelope + `finding`/`coverage_ledger`/`verdict` + pure-function verdict gate + heuristic vacuous-test detector + **cartridges #1 (vacuous) & #2 (secret)** + cost-governance ceiling + secret redaction. Proves the *concept*.
- **Tier B — validation-grade (externalization-ready):** Tier A **+** cartridge #3 (orphan) + Python AST-grounding + lightweight Prosecutor + `decision_record` (minimal) + integrity lint + the **Minions dogfood** + reproducibility + honest degradation. **Tier B is the engineering precondition for clearing the ≥80%-precision gate — necessary, not sufficient.** Tier B is delivered; the gate is not cleared. Clearing it additionally requires an independent corpus and human adjudication (Epic 13), neither of which is a build task. *(Amended 2026-08-10b.)*
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
- **Technical:** envelope-determinism cascade → golden-test + human gate (highest-leverage item); vacuous precision too low → advisory framing + precision-tuning + "review these N" fallback; ~~Python-only AST → stack-agnostic validator interface (V2 multi-language additive)~~ **Python-only AST → stack-agnostic validator interface; the additive multi-language implementations are delivered in V1 (`argus/shared/source_languages.py`), so this mitigation is discharged rather than pending** *(amended 2026-08-10, Story 10.2; delivered by `sprint-change-proposal-2026-07-28.md`)*. **Riskiest assumption:** that the heuristics clear ≥80% precision — de-risked by front-loading the cartridge precision harness in M1.
- **Market:** category-creation cost → ride the vacuous-test wedge (no category education); incumbent encroachment → the compounding corpus is the moat, not the framing.
- **Resource:** the cut-order is the contingency; **precision-non-convergence fallback** → tighten to higher-precision advisory OR pull mutation-testing forward from V2, **accepting the timeline may extend** if precision research runs long.

### Open inputs (flagged, not blockers)
~~Exact **team headcount**, the **budget-ceiling `$X`**, and **N** for the validation set (5–10) — resolved in the delivery/functional detail, not the scope decision.~~

✅ **All three closed 2026-08-10b.**

| Input | Resolution |
|---|---|
| **Team headcount** | **Moot.** Delivery is agent-driven through the SM → Dev → Review cycle with named human gates at adjudication (Epic 13) and release status (Story 10.1). Headcount was never the scheduling unit; expert-hours at the gates are — budgeted at ≤4 per full adjudication run (`precision-validation-protocol.md` §3). |
| **Budget-ceiling `$X`** | **Resolved as OI3, LOCKED — the resolution is "there is no default."** `ceiling_credits: int \| None`, no numeric default, `None` = no ceiling configured, `0 → None`. The operator sets it per target; sizing is empirical per audited repository (Story 7.1). A numeric default was **deliberately refused**: a wrong default silently truncates an audit, the failure NFR-C2 exists to prevent. |
| **`N` for the validation set** | ~~**Assigned, not answered — owned by Story 13.1.** The PRD (§Validation Approach, `N ≈ 5–10` real repositories) and `precision-validation-protocol.md` §5 (`N ≥ 5` labeled cartridges) specify **different corpora** and were never reconciled. 13.1 decides which governs and amends the loser.~~ ✅ **ANSWERED 2026-08-16 by Story 13.1 (DN-1) — by DECISION, not by implementation.** **The PRD governs:** `N ≈ 5–10` **real repositories**, floor `N ≥ 5`. The protocol's cartridge floor was struck and the cartridges re-labelled as the FR20 **recall** instrument they always were (nothing in `tests/cartridges/` changed). Reason: the two documents specified different **quantities** — recall against defects the team planted versus precision on code nobody planted — and only the second can gate externalization. Membership is now a closed, machine-readable manifest (`tests/corpus/_manifest.py`) with pinned shas and recorded exclusions; the floor is derived from the **same** `VALIDATION_SET_FLOOR_N = 5` rather than forked. **Measured at decision time: `N = 0` eligible members**, so the floor was **NOT met**. **Updated the same day: AC3b was ratified by the operator and the corpus now holds `N = 5` eligible members — the floor is MET.** The gate nevertheless remains **NOT CLEARED**: reaching the floor is one of four §5 conditions, and the adjudication run, the ≥80% figure and the zero-clean-repo-FP condition are all still outstanding. Deciding what the corpus *is* is not the same act as building it (13.1/AC3b) or adjudicating it (13.2). |

## Functional Requirements

> **Capability contract (V1).** This is binding: a capability not listed here will not exist in V1 unless explicitly added. Items marked **[Tier B]** are the validation-grade additions over the demo-grade core (per §Project Scoping); everything else is non-negotiable core. Capabilities beyond V1 live in §Product Scope (V2–V4) and are out of this contract.

### Repository Intake & Partitioning
- **FR1:** An operator can submit a repository at a pinned commit for audit through a headless invocation.
- **FR2:** APAA can detect the repository's technology stack and available toolchain without operator configuration.
- **FR3:** APAA can partition the repository into bounded audit units within a declared budget.
- **FR4:** APAA can identify critical subsystems (and an operator can designate them) so coverage gates can require them to be examined deeply. **A file APAA can never grade `audited_deep` is ineligible for the heuristically-derived critical set** — a gate no run can satisfy is not a gate, and an unsatisfiable one trains operators to ignore every gate. *(Amended 2026-08-03.)*
  - **Eligibility (heuristic set):** exclude files that are `audited_shallow` by construction — test files (which are the *subject* of the vacuous-test pass, never a target of deep grounding) and clean-parsed zero-definition modules.
  - **Operator designation is exempt.** An explicit `--critical-subsystem` designation keeps its conservative behaviour, including for a path that matches nothing: a human saying "this matters" must still be able to withhold `RELEASE_READY`.
  - An operator can exclude a subtree from the critical set by prefix, not only by exact path.

### Coverage Ledger & Grounded Evidence
- **FR5:** APAA can record every file's audit depth in a fixed-enum coverage ledger (`audited_deep` / `audited_shallow` / `tool_scanned_only` / `inferred` / `skipped`).
- **FR6:** APAA can require an emitted claim before grading a file `audited_deep` (silence downgrades to `audited_shallow`).
- **FR7:** APAA can validate a deep claim against source structure ~~(Python AST in V1)~~ (**AST grounding is delivered in V1 for every language enumerated in `argus/shared/source_languages.py` — that module is the SOURCE OF TRUTH, deliberately not a hand-typed list here**) and downgrade an unverifiable claim. **[Tier B]** *(Amended 2026-08-10, Story 10.2 — `DF-AUD-APAA-D`. The capability shipped via `sprint-change-proposal-2026-07-28.md` with no story and no amendment; FR7 is the binding contract, so it is corrected to what the code does.)*
  - **What "grounded" buys, stated at the boundary rather than implied.** A language is grounded when its tree-sitter grammar is installed and the file parses: the file becomes `ast_eligible` and its claims can be checked against a real AST. Pinned language-by-language by `tests/test_multilanguage_audit.py` (`TC-ArgusAgent-INTAKE-003-07`..`-09`), which fails if a language in the source-of-truth map has no grounding fixture — so language #11 cannot be added unpinned.
  - **Enumerable ≠ deeply auditable**, the boundary `argus/shared/source_languages.py:27-32` already draws. A file whose grammar is absent is still read and graded; it simply cannot reach `audited_deep`. It degrades to `ast_eligible=False` with a named reason token — never a silent drop, never a false deep claim (AR10).
  - **Measured shortfall, filed not omitted (`DF-10-2-A`):** C, C++, Ruby and Rust ground but currently extract **no definitions**, because the definition-node vocabulary was written against Python's. A file in those four therefore parses but has no function or class for the depth gate to stand on. Recorded here so this contract is not read as promising more than `TC-ArgusAgent-INTAKE-003-09` measures.
- **FR36:** An operator can enable an **LLM-backed deep-audit pass** that produces grounded claims beyond the zero-token path. **[Tier B]** *(Added 2026-08-10b.)*
  - **Off by default, always.** The default run is zero-token, offline, requires no key or account, and transmits nothing. Enabling requires explicit operator action per invocation.
  - **Egress is disclosed before it occurs:** the invocation states what will be transmitted and to which provider, before the first byte leaves.
  - **Governed by the existing ceiling.** Spend flows through FR21/FR22 — the ceiling halts, marks the remainder `skipped`, downgrades coverage, and reports honestly. No new cost-governance mechanism is introduced.
  - **Determinism is preserved** by the FR27/NFR-D1 memoization path — a re-run returns the recorded result. Enabling this pass must not make the verdict irreproducible.
  - **Degradation is honest:** an unavailable, erroring, or budget-halted provider downgrades coverage and records a finding (NFR-R1). It never produces a false deep claim and never crashes.
- **FR8:** APAA can exclude `inferred` (narrative/doc) evidence from satisfying any verdict gate.
- **FR9:** An operator can read exactly which files were examined deeply, shallowly, tool-scanned, inferred, or skipped.
- **FR37:** APAA can state, on every terminal outcome, **why that outcome was reached and the next action that changes it**. *(Added 2026-08-10b.)*
  - **Enumerated over the full verdict vocabulary** — `RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`, and the `AUDIT_FAILED` non-verdict — pinned by a test that **fails on an unenumerated outcome**.
  - **`INSUFFICIENT_COVERAGE` is the load-bearing case:** it must name the specific gate that went unmet (floor, ratio, or critical subsystem) and the action that would change it. "Not assessed" without a remedy is honest and useless.
  - **Self-contained.** The next action is present in the tool's own output. A user with no colleague and no internal wiki must not be sent elsewhere to interpret a verdict.
  - **Names what was never examined, not only what scored low.** Coverage ratios describe the files that **entered** the audit. A file class excluded at ingestion never enters the denominator at all, so no ratio can disclose it. Every verdict states **which file classes were not ingested** — distinguishing three populations: **never ingested** (suffix outside the auditable set), **ingested but held out** of the assessed population, and **assessed**. This extends FR17's scope statement, which requires a scope but does not require the *ingestion boundary* to appear in it.
  - **Does not soften a verdict.** This requirement governs *explanation*, never *classification*: no outcome may be reworded, upgraded, or hedged to seem more actionable. FR16's decision table is untouched.

### Defect Detection (cartridge-validated)
- **FR10:** APAA can detect tests that appear vacuous (low assertion-density / high mock-ratio) and report them as **advisory** findings carrying their evidence counts.
- **FR11:** APAA can detect hardcoded secrets and report them with the secret value redacted.
- **FR12:** APAA can detect orphan / dead code (no referencing requirement or caller). **[Tier B]**
- **FR13:** APAA can attach at least one verifiable locator to every finding, or reject the finding.
- **FR14:** APAA can convert a tool failure or unestablishable-traceability condition into a finding rather than a crash.

### Release-Readiness Verdict
> **Verdict vocabulary (canonical).** The negative-assurance ladder runs `RELEASE_READY` → … → `NOT_READY_FOR_RELEASE`; **`BLOCKED` is the demo shorthand for a blocking (`NOT_READY`) outcome** — the two names denote one concept, and it asserts exactly one thing: **APAA found something**. **`INSUFFICIENT_COVERAGE`** is a distinct *not-assessed* state — "I did not examine enough to vouch" — and is **not** a blocking verdict. It is reached two ways: coverage below the 20% floor, **or** an unmet coverage / critical-subsystem gate with **zero blocking findings** (amended 2026-08-03). The two states are never interchangeable: a verdict that asserts a defect APAA did not find is a false accusation, the failure mode cross-cutting concern #6 exists to prevent. Downstream artifacts use this vocabulary.

- **FR15:** APAA can compute a release-readiness verdict as a pure function of the coverage ledger.
- **FR16:** APAA can emit `RELEASE_READY` only when coverage gates are met (≥60% deep + all critical subsystems deep + 0 blocking findings), can emit a blocking verdict **only on the strength of a finding it actually made**, and reports every other outcome as `INSUFFICIENT_COVERAGE` — never a default block. *(Amended 2026-08-03; see the decision table below.)*

  **FR16 decision table (binding, evaluated in order).** Findings are evaluated before coverage, so a coverage shortfall can never be reported as a defect:

  | # | Condition | Verdict | Exit |
  |---|---|---|---|
  | 1 | `assessed_total == 0` or `assessed_ratio < 1/5` | `INSUFFICIENT_COVERAGE` | 3 |
  | 2 | `blocking_findings >= 1` | `NOT_READY_FOR_RELEASE` | 2 |
  | 3 | `assessed_ratio >= 3/5` **and** all critical subsystems `audited_deep` | `RELEASE_READY` | 0 |
  | 4 | otherwise — zero blocking findings, a coverage or critical-subsystem gate unmet | `INSUFFICIENT_COVERAGE` | 3 |

  Row 4 is the amendment: the case it covers previously fell through to `NOT_READY_FOR_RELEASE`, which asserted a defect APAA had not found. **Nothing becomes a silent pass** — exit `3` still fails an unconfigured CI step, and Journeys 3 and 5 already route it to human review, never to auto-proceed. The verdict must disclose which row fired and the assessed population it was computed over.
- **FR17:** APAA can express every verdict in negative-assurance terms with a scope statement, materiality bar, disclaimer, and point-in-time stamp.
- **FR18:** An integrator can consume the verdict as a deterministic exit code and a machine-readable artifact.
- **FR33:** APAA can order findings by verdict impact — surfacing verdict-blocking findings before non-blocking ones — so a blocking 🔴 is never buried beneath lower-severity noise (serves the "actionable / no cry-wolf" success criteria; alarm-fatigue defense, risk H2).
- **FR34:** APAA can disclose its own validation status on **every** user-facing verdict surface, and cannot emit a verdict on a surface that omits it. *(Added 2026-08-10b.)*
  - **Content:** the tool's finding-precision validation state (validated / **not independently validated**) and the corpus it rests on.
  - **Mechanical enforcement, not editorial discipline:** the surface set is **enumerated in a committed test that fails on an unenumerated member** — a new verdict surface must either carry the disclosure or fail CI. A disclosure that depends on an author remembering is not a disclosure.
  - **Distinct from FR17, and both apply.** FR17 bounds the scope of *this audit* ("no blocking findings within the audited envelope"). FR34 bounds the credibility of *the tool itself* ("its precision has not been independently validated"). An audit can be perfectly scoped and still be produced by an unvalidated instrument.
  - **Removable only on measurement, and replaced rather than deleted:** when the ≥80% gate clears, the disclosure is **replaced** by a statement of the cleared status and the corpus that cleared it. The surface never becomes silent, and the enforcing test never becomes vacuous.
  - **Not a permanent state.** FR34 exists because the gate is deferred, not waived. It is coupled to a committed programme to clear it (§Success Criteria, Epic 13); if that programme is abandoned, the free public tier is withdrawn rather than the disclosure.

### Self-Audit & Trust
- **FR19:** APAA can run an adversarial Prosecutor pass that challenges whether the ledger justifies the verdict and downgrades an unearned verdict. **[Tier B]**
- **FR20:** APAA can validate its own detectors against defect cartridges with golden expected-findings keys, asserted in CI.

### Cost Governance
- **FR21:** An operator can set a budget ceiling for an audit.
- **FR22:** APAA can halt on budget exhaustion, mark the remainder `skipped`, downgrade coverage, and report honestly — never fabricating or silently overrunning.

### Governance, Escalation & Evidence Integrity
- **FR23:** ~~APAA can halt at a human STOP/PROCEED gate on a pattern-matched escalation condition, defaulting to STOP — and on gate timeout (no response within a configured window) it **parks at STOP, never auto-PROCEEDs** (time-boxed-gate default, Q-A).~~ **Amended 2026-08-11, Story 10.5 / AC4.3 (DN-3) — disposed `library-seam`. WHAT IS DELIVERED:** the pattern-matched escalation evaluator (`argus/governance/escalation.py` — `escalation_fires` / `resolve_escalation`), the R1 rule and trigger model, the default-STOP resolution semantics including the time-boxed park-at-STOP, and `DecisionRecordWriter` — all built, typed and proven by **`tests/test_hitl_escalation.py`**. **WHAT IS DEFERRED: its INVOCATION.** No code path reachable from `argus/cli.py` calls it; measured 2026-08-11 by a static import walk, `governance/escalation.py` has exactly one importer inside `argus/` and that importer is itself unreachable. **An audit an operator can run today never reaches a STOP gate.** Corrected to what the code does, following the FR7 (Story 10.2) and FR30 (Story 10.3) precedent: FRxx is the binding contract, so it is corrected rather than left to be discovered. **THE REASON, BOTH HALVES:** (a) every call site lands in `argus/pipeline.py`, measured **1331 lines against the NFR-M1 cap of 1200** and byte-fenced to **Story 12.1**; and (b) the V1 default path is **unattended CI** (Journeys 3 and 5) with **no human to answer a default-STOP gate**, so a naive wiring would deadlock every automated audit — the design question 12.1's enabler must answer, not a line of plumbing. **THE COST THIS INCURS, STATED NOT HIDDEN:** the §Cut-Order marks **FR23 non-negotiable core** — only FR24 is **[Tier B]** — and `implementation-readiness-report-2026-08-03.md:365` already flagged FR23 as stranded in a slippable epic. **This amendment de-scopes a non-negotiable-core capability's invocation to an unscheduled story, and a de-scope that hides its own cost is the defect Epic 10 exists to close.** Owner **XAgent007 (Governance Owner)**; `target_story: NONE — unscheduled`, to be scheduled once 12.1 lifts the NFR-M1 gate. Ledger: `DF-6-7-A`, closed by this disposition. Enforced by `tests/test_v1_commitment_closure.py`, which turns **red** the day the seam becomes reachable and this text still says it is not.
- **FR24:** ~~APAA can record a human escalation decision in an append-only decision record (and log the STOP even if the record is deferred). **[Tier B]**~~ **Amended 2026-08-11, Story 10.5 / AC4.4 — disposed `library-seam`, and NEVER FILED BEFORE TODAY.** `DecisionRecordWriter` (`argus/governance/decision_record.py`) is built, typed and test-proven, and has **no importer at all inside `argus/`** — its only trace in the package is a prose mention in `store/integrity.py`. It follows FR23 by construction: **a decision record has nothing to record until the gate it records for is invoked.** Owner **XAgent007 (Governance Owner)**; `target_story: NONE — unscheduled`, to be scheduled together with FR23 once Story 12.1 lifts the `pipeline.py` NFR-M1 gate. Ledger: `DF-10-5-A`.
- **FR25:** APAA can wrap every artifact in a content-hashed, schema-versioned envelope.
- **FR26:** ~~APAA can verify referential integrity of its on-disk state (no dangling references). **[Tier B]**~~ **Amended 2026-08-11, Story 10.5 / AC4.4 — disposed `library-seam`, and NEVER FILED BEFORE TODAY.** `lint_referential_integrity` (`argus/store/integrity.py`, NFR-A2) is built and proven by `tests/test_store_integrity_lint.py`, and is imported only by `dogfood/proof_run.py` and `evidence/bundle.py` — **both themselves unreachable from `argus/cli.py`**, so **no audit an operator can run lints its own on-disk state.** *"It has tests"* is not evidence of delivery. Owner **XAgent007 (Governance Owner)**; `target_story: NONE — unscheduled`; the call site lands in `pipeline.py`, fenced to Story 12.1. Ledger: `DF-10-5-B`.
- **FR27:** APAA can reproduce the same verdict for the same repository and APAA version.
- **FR28:** APAA can redact secrets from stored excerpts and never emit source/secret bytes into ledgers, evidence, logs, or traces.
- **FR29:** ~~An operator can export an evidence bundle (coverage ledger, scope statement, findings, verdict); the operated-service path retains no source.~~ **Amended 2026-08-11, Story 10.5 / AC4.4 — disposed `library-seam`, and NEVER FILED BEFORE TODAY.** This is the sharpest of the four, because **the FR text names the operator and no operator can do it**: `build_evidence_bundle` / `persist_evidence_bundle` (`argus/evidence/bundle.py`) are built and proven by `tests/test_evidence_bundle.py`, **no `argus` CLI subcommand exports a bundle**, and the only importer in the package is `dogfood/proof_run.py`. Journey 4's hand-delivered bundle is produced by the dogfood harness, not by a surface Dana's engineer can invoke. Owner **XAgent007 (Governance Owner)**; `target_story: NONE — unscheduled`; delivering it needs a CLI surface, which is **Story 12.8's** fence. Ledger: `DF-10-5-C`. ⛔ The **source-retention guarantee** in the struck text is **unchanged and still binding** — this amendment narrows the *invocability* claim only.

### Invocation & Resumability (headless)
- **FR30:** An integrator can invoke APAA headlessly with ~~`repo + commit + budget + materiality_bar`~~ **the accepted invocation surface** and receive a verdict artifact + exit code. *(Amended 2026-08-10, Story 10.3 — `DF-AUD-APAA-E`. The original four parameters described the surface as Story 1.7 LOCKED it; six further flags entered the shipped parser afterwards and were specified in no binding document, so the capability contract understated the capability. Original wording struck rather than deleted, §3.4.)*
  - **The accepted surface is `argus/cli.py::build_parser` — that function is the SOURCE OF TRUTH, deliberately not a hand-typed list here.** The `source_languages.py` precedent FR7 set on 2026-08-10 applies for the same reason: a prose copy of an enumerable fact drifts, and a hand-typed count is the next instance of the AI-E9-7 class.
  - **What this contract commits to are the CATEGORIES**, each of which must remain expressible through the headless invocation: the **determinism pin** and its **release-gate enforcement** (a run can be made to refuse a non-git, dirty or drifted tree); the **cost ceiling** (OI3 — no numeric default, `0`/omitted means no ceiling); the **materiality bar**; **operator designation** of the critical set, in both directions (FR4); **audit-pass selection** and **report selection**, both narrowing-only and both disclosed; **security-finding suppression**, bounded by the §G suppression threat model and never able to reach a live production key; and the **assessed-population scope** (FR33-support).
  - **Equality between this contract and the parser is pinned by test**, in both directions, by `tests/test_invocation_contract.py` (`TC-ArgusAgent-CLI-001-35`..`-41`): a flag the parser accepts and no document specifies fails, and a flag a document names and the parser rejects fails. A capability not listed in this contract still will not exist in V1 (the §Capability contract preamble is unchanged) — what changed is that "listed" is now machine-checked rather than asserted.
- **FR31:** APAA can resume an interrupted audit from its on-disk `.apaa/` state.
- **FR32:** APAA can run to completion on a sequential (least-capable) host, producing byte-identical on-disk state to a parallel run.
- **FR35:** A coding agent can invoke an audit and consume the verdict through a **local agent-integration surface**, without a human relaying it. *(Added 2026-08-10b.)*
  - **Two shipped forms:** an **MCP server** (stdio transport) and **packaged assistant command assets** the installer places in the host's configuration.
  - **Bounded by the §Project Classification constraints:** stdio only — no network listener is opened and no port is bound; no HTTP stack, preserving the `argus.* ⊬ fastapi` import-isolation gate and ADR #20; no credentials accepted or stored.
  - **No new authority.** It invokes the same pure `AuditRequest → AuditVerdict` path as the CLI, under the same work-manifest permission boundary (NFR-S4). Any capability reachable through this surface is reachable through the CLI, and the converse is not required.
  - **Verdict parity is asserted, not assumed:** the same repository at the same commit produces the same verdict through either surface, pinned by test.

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
- **NFR-S6:** **No source code, prompt, or repository content leaves the machine on the default path.** *(Added 2026-08-10b.)* Third-party transmission occurs **only** through the explicitly enabled FR36 deep pass, is **disclosed before the first byte is transmitted**, and names the provider that will receive it. The agent-integration surface (FR35) opens **no network listener and binds no port**. Both properties are enforced by committed gates in the shape of the existing import-isolation tests — an egress path reachable without opt-in fails CI.

### Cost Efficiency *(the scariest risk — token economics)*
- **NFR-C1:** A baseline full audit costs a **bounded fraction of the audited repo's build cost** (tracked target ≤ 10–20% baseline; ~1% for V2 incremental diff-scoped runs). V1 measures and reports the baseline.
- **NFR-C2:** An audit **never exceeds its declared budget ceiling**; on exhaustion it halts deterministically with no silent overrun.
- **NFR-C3:** Deterministic, **zero-token tools perform breadth** so LLM spend is reserved for depth.

### Reliability & Honest Degradation
- **NFR-R1:** A tool/parse failure or unestablishable-traceability condition **degrades to a recorded finding or coverage downgrade — never an uncaught crash or a fabricated result.**
- **NFR-R2:** An interrupted audit is **fully resumable** from on-disk `.apaa/` state with no loss of prior coverage.

### Portability
- **NFR-P1:** APAA runs to completion on the **least-capable host (Cline, sequential)**, producing **byte-identical on-disk state** to a parallel-capable host; parallel is a pure speedup.
- **NFR-P2:** The audit is **stack-agnostic by construction** (~~deep AST-grounding = Python in V1; `claim_emitted` proxy elsewhere~~ **deep AST-grounding is delivered in V1 for every language enumerated in `argus/shared/source_languages.py`, which is the source of truth; the `claim_emitted` proxy carries anything outside that set or any file whose grammar is absent** — *amended 2026-08-10, Story 10.2 / `DF-AUD-APAA-D`; delivered by `sprint-change-proposal-2026-07-28.md`*); no host- or stack-specific logic in the ledger/verdict core. **The language conditional remains confined to `argus/index/`** — widening the grounded set changed one map and one entry-point table, and touched neither `ledger/` nor `verdict/`, which is the property this NFR actually asserts.
- **NFR-P3:** **The default public installation grounds the languages the tool claims to support.** *(Added 2026-08-10b.)* A user who installs through the primary public channel and audits a repository in a documented supported language receives that language's grounding **without discovering an optional extra**. Coverage degraded by a grammar absent from the default install is a **packaging defect**, not a user error or an honest limitation — and is reported as such. Where a language is deliberately not in the default install, its absence and the reason are stated in the tool's own output at the point the file is downgraded.

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
