---
title: "Product Brief Distillate: APAA (AI Project Assurance Audit)"
type: llm-distillate
source: "product-brief-apaa.md"
created: "2026-06-17"
purpose: "Token-efficient context for downstream PRD creation — captures detail beyond the 1-2 page executive brief."
inputs:
  - _bmad-output/brainstorming/brainstorming-session-2026-06-16-201450.md
  - _bmad-output/design-artifacts/APAA/research-market-2026-06-17.md
  - _bmad-output/design-artifacts/APAA/research-domain-2026-06-17.md
  - _bmad-output/design-artifacts/APAA/research-technical-2026-06-17.md
---

# APAA — Detail Pack (for PRD creation)

## Product identity
- **APAA = AI Project Assurance Audit.** Commercial positioning: "AI Software Assurance Platform / AI Release Readiness Auditor." Internal codename retained; commercial subtitle carries the market-tested framing.
- **Posture (one line):** assurance, not code review — *bounded, evidenced, independent*. Repo URL in → coverage-grounded, negative-assurance release-readiness verdict out.
- **Stance vs Minions:** same DNA (filesystem contracts, adversarial review layers, frozen schemas, hash-chained ledger, escalation discipline), OPPOSITE stance — Minions = intrinsic / process-time / insider; APAA = extrinsic / repo-time / outsider cold-reading an unknown repo where **coverage honesty is the central problem**.
- **Headless** (like Minions): no UI. Verdicts + evidence are artifacts / API surfaces. (A landing-page "paste a repo URL" runner is marketing surface, not a product UI.)
- **Hosts:** Claude Code Skill (parallel) + Cline (sequential) fallback. **Sequential is canonical; parallel is a pure speedup that must produce byte-identical on-disk state.**

## Core IP & moat (PRD must center these)
- **Coverage ledger** = the core IP. Fixed enum: `audited_deep` / `audited_shallow` / `tool_scanned_only` / `inferred` / `skipped`. **Verdict is a PURE FUNCTION of the ledger.**
  - `audited_deep` requires a **grounded claim** = a structured finding citing specific symbols / line ranges **validated against the repo AST** (NOT free text). Unverifiable claim → auto-downgrade to `audited_shallow`. (Comprehension proxy: silence ≠ deep.)
  - `inferred` (docstrings/README/narrative) can **NEVER** satisfy a verdict gate (anti evidence-poisoning).
- **Moat = AI-specific defect detection**, led by **vacuous-test detection**: "tests pass" downgraded unless they assert meaningfully. V1 = heuristic (assertion-density + mock-ratio), advisory-framed, **precision-tuned over recall**. V2 = mutation-testing-grade.
- **Signature demo / V1 success criterion:** `GitHub: green · Sonar: green · APAA: 🔴 tests appear vacuous`.
- **Negative assurance, scope-bounded:** "No release-blocking findings within the audited coverage envelope" — NEVER "the code is correct." Verdict ships with `scope_statement`, materiality bar, disclaimer, point-in-time stamp. Borrow audit vocabulary (SOC2/ISO/financial/DO-178C) **as analogy, never legal claim**.
- **Dual-register verdict output:** audit-grade negative-assurance artifact PLUS plain-English ship-readiness line ("Ship-readiness: BLOCKED — 3 vacuous tests, coverage 62% deep") for the engineer ICP.
- **Trust frontier (named openly):** auditor is itself an LLM → risk = shallow read mis-graded as deep. Defended 3 ways: AST-grounded claims, adversarial **Prosecutor** (paid to break the verdict), **defect cartridges** (empirical detector measurement).

## Scope — phasing (LOCKED by brainstorm + expert review)
**V1 (90-day MVP) — "coverage honesty + release-readiness verdict + vacuous-test moat".** Sequential-canonical, `.apaa/` filesystem state, deterministic.
- V1 CORE (trustworthy): shared `envelope` (schema_version, content_hash, prev_hash, artifact_type) + schemas **finding ① / coverage_ledger ③ / verdict ⑧** + minimal **decision_record ④** + **integrity lint (H4)** + pure-function verdict gate + human STOP/PROCEED escalation + **budget ceiling (Cost Governance / L5-lite)**.
- V1 DIFFERENTIATOR (demoable): **vacuous-test heuristic (#10 cheap)** + **defect-cartridge framework** + **lightweight Prosecutor (verdict-gate only)**.
- **Delivery cut order if 90d slips:** non-negotiable core = envelope + 3 schemas + verdict gate + heuristic detector + 1 cartridge + cost ceiling. First to slide → Prosecutor + 2nd/3rd cartridges (V1.5). **Last cut = Minions dogfood (it is the proof).**
- **3 milestones:** M1 (d0-30) deterministic spine, token-free, unit-tested; M2 (d31-60) findings engine + THE MOAT (cartridges #1-3 CI-asserted); M3 (d61-90) verdict trust + dogfood Minions + reproducibility check.
- **V1 explicitly OUT:** cost intelligence/estimator, traceability, PRR, rich standards mapping, parallel exec, memory/CQRS, any UI.

**V2:** bidirectional traceability (#13), Production Readiness Review checklist (#8), standards mapping (CWE/ASVS/ISO-25010/SLSA), full mutation-grade vacuous-test detection.
**V3:** cost intelligence — deterministic pre-flight estimator (D1-5), EVM (F1-3), forward customer quoting (E1-3), self-calibrating corpus.
**V4:** append-only agent-log substrate (G1), CQRS Reports Agent / report-as-product (G2), curated memory (G3), content-addressed cache (G4), multi-agent ecosystem, **coverage-ledger as open attestation standard**.

## The 8 self-audited Stage-0 frozen contracts (schema detail for PRD)
Shared **envelope** wraps every artifact: `{schema_version (additive-only), artifact_type, id (content-addressed/deterministic), content_hash (over PAYLOAD ONLY — excludes volatile run_id/created_at), prev_hash (unified chaining), producer, apaa_version, run_id (hash-excluded), created_at (hash-excluded)}`. **Determinism invariant:** content_hash over canonical payload only → identical inputs ⇒ identical hash ⇒ cache hit ⇒ reproducible verdict.
1. **finding** — ≥1 verifiable locator or REJECTED; `excerpt_redacted` + `contained_secret` (secrets masked before storage); `standards_refs` format-validated (`^CWE-\d+$`…), **CWE required when category==security**; `prosecutor_verdict`.
2. **severity.rubric** — 4 levels {critical,high,medium,low}, each with `blocks_verdict` bool.
3. **coverage_ledger + verdict gates** — KEYSTONE. status enum (above); `audited_deep` requires `claim_emitted`; verdict = PURE FUNCTION; `inferred` cannot satisfy any gate; thresholds: **RELEASE_READY ≥60% deep + ALL critical-subsystem deep + 0 blocking findings; NO repo-wide conclusion below 20% coverage**.
4. **decision_record** — append-only; ≥2 options mandatory; `escalation {resolved, ESCALATED_STOP}` + `escalation_match` (pattern/AST-matched, NOT LLM judgment; defaults STOP).
5. **work_manifest** — `= permission scope` (an agent may NOT read beyond `files_to_read`); passes; `model_tier {cheap_triage, premium_deep}`; perspective_count; checkpoint_reestimate. **V1 = minimal assignment (file-list = permission boundary); full frozen schema = V3 when estimator consumes it.**
6. **cost_estimate** — deterministic; mode {retro_audit, forward_build}; tokens PERT {p10,p50,p90}; `rate_snapshot` (raw tokens + rates → derived money); `corpus_density.n_comparable_runs` + confidence thresholds; `valid_until` + `disclaimer`. **(V3.)**
7. **cost_ledger_event** — append-only hash-chained EVM; event_type {baseline,actual,rebaseline,overrun_gate,underrun_report}; BAC/AC/EV/CV/EAC; priced delta; gate_outcome. **(V3.)**
8. **verdict** — verdict enum DEFINED as negative assurance; `scope_statement`; coverage_summary; blocking_findings; `valid_as_of` (point-in-time, SOC2 Type-I analog); apaa_version; `disclaimer`.
- **Plus referential-integrity lint (H4)** — deterministic zero-token; fails on any dangling manifest_ref / requirement_version / evidence file (filesystem has no FKs).
- **Self-audit closed 3 CRITICAL holes:** C1 no schema_version, C2 secret-leak-via-excerpt, C3 determinism hole (non-deterministic IDs/timestamps in payload).

## Technical constraints & decisions (from technical research)
- **Reproducibility = HONEST reframe (load-bearing).** Bit-identical LLM output is INFEASIBLE (temp 0 ≠ deterministic; FP/GPU/load-balancing nondeterminism; ~20% identical on long prompts). APAA promises: deterministic ledger + pure-function verdict + **STABLE via content-addressed memoization** (cache findings; re-run at same key returns recorded result). **Model checkpoint MUST be in the cache key** (Anthropic rotates silently → model rotation = re-audit event).
- **Context rot is real even within budget.** ALL frontier models (incl. Claude Opus 4) degrade as input grows; "lost in the middle" past ~50% fill. → per-agent budgets conservative (target ≤40 files/15k LOC, hard ≤60/25k); order inputs with highest-risk files at context EDGES; record `context_pressure` → over-budget partitions auto-downgrade from `audited_deep`.
- **Build an AST/code-graph index FIRST** (tree-sitter / ast-grep) to drive partitioning + seam discovery — NOT directory layout. Use grep/structural search, NOT embeddings (matches Anthropic's 2025 shift away from vector DB in Claude Code). The graph defines true cross-partition edges → the **seam auditor** reads the real interaction surface (closes the divide-and-conquer blind spot — the biggest feasibility risk).
- **Tools do breadth, LLM does depth** (L1): SAST/linters remove ~40-60% of files from LLM depth; ensemble beats either alone. **Tiered routing** (L2): cheap triage model risk-flags → premium only on flagged. **Diff-scoped incremental** (L3, BASE...HEAD ~1%). **Prompt caching** (L4): Anthropic reads 0.1×/writes 1.25×-2×, break-even at 1 hit, real 59-70% savings; multi-perspective passes over one partition = ideal cache shape.
- **Token-free pre-flight estimation** (V3): cloc/tokei/scc/radon + local tokenizer (tiktoken / Anthropic count-tokens) → exact-by-construction; variance lives in generation only. **If estimator burned inference it eats itself.**
- **Cost napkin:** 500k LOC ≈ ~5M tokens/read; naïve multi-pass × perspective × prosecutor ≈ 20-50M input tokens. Levers cut ~10-50×. Target: full baseline audit ≈ 10-20% of build cost; incremental ≈ ~1%.
- **Defect cartridges = Day-1 CI gate** (not a nicety): only empirical defense of coverage claims; doubles as calibration for heuristics + LOC→token multipliers; a cartridge MISS = release blocker. Rotating **holdout** set defends against cartridge overfitting.
- **Tool-failure policy:** never fabricate → downgrade coverage + raise the failure as a finding. Same shape for budget-exhaustion (stop, mark `skipped`, downgrade, report honestly).

## Reusable Minions patterns to PORT (engineering reuse, not fork)
- Hash-chained ledger (ADR #18) → coverage ledger, cost ledger, agent-log substrate.
- Permission tiers / A2A → `work_manifest` ≡ permission scope.
- `budget_guardrails` (runtime evaluate/enforce) → L5 budget ceiling (NOTE: Minions has NO pre-flight estimator — see D5 below).
- `runtime/adapter_portability.py` → host capability manifest (detect Claude-Code-parallel vs Cline-sequential; identical contracts).
- `MINIONS_LLM_PROMPT_CACHE_ENABLED` → L4 cross-perspective cache.
- Diff-scoped changed-file gate + provider-tier cost-attribution → L2/L3.
- §3.3 deterministic-and-auditable orchestration; §3.8 secret masking → `excerpt_redacted`/`contained_secret`.
- bmad-code-review adversarial layers (Blind Hunter / Edge Case Hunter / Acceptance Auditor) + APAA-novel **Prosecutor**.
- L5-E13 "engineer a guard, don't rely on vigilance" → promote real-world misses to new cartridges.

## GTM / distribution (captured for PRD's go-to-market section)
- **Internal-first, externalize-by-packaging-not-rewrite.** Keep filesystem contracts clean + stack-agnostic.
- **First customers path:** (S0) dogfood Minions → sibling XAgents repos (code.i, Cline, DevMate). (S1) operated-SERVICE for 2-3 warm-intro design-partner regulated teams — hand them the evidence bundle (dissolves install + trust-our-source friction). (S2) wedge on a single incident class: "a passing test that asserts nothing shipped to prod." (S3) partner-channel via Credo AI / Holistic AI (they own model-governance buyer, lack code-evidence layer). (S4) hosted GitHub App / CI action AFTER ≥80% precision proven.
- **Buyer = Engineering Lead / Head of Quality burned by a false-green** (accountable, not merely productive). Negative assurance is a value prop for the accountable.
- **External entry must be zero-install:** hosted "point at repo URL" runner / GitHub App / CI action. `.apaa/` git-ignorable by default; evidence bundle = detached artifact. "We never retain your source" + air-gapped/local-run story = table stakes for regulated ICP.
- **Trial-cost guardrail in V1 GTM scope:** hard per-audit spend ceiling + coarse "this repo ≈ $X" preview — needed even though full estimator is V3.
- **Adjacent high-value markets (roadmap, named in brief):** M&A/vendor due-diligence; insurer/underwriting signal; AI coding-agent certification ("audited-by-APAA" conformance mark).
- **The Credibility Flywheel:** every Minions release → APAA verdict → (1) public corpus of real reports, (2) detector-calibration ground truth, (3) verdict-concordance labels (proprietary), (4) growing cartridge benchmark.

## Validation / success metrics (trust = the product)
- Run on N≈5-10 real XAgents repos (start: Minions + siblings); designated senior engineer independently reviews each verdict.
- **Finding precision ≥80%** of 🔴 blocking findings judged real (precision > recall — a false accusation is a public credibility hit; a miss is a quiet gap).
- **Verdict concordance** with human's independent release decision.
- **Moat hit-rate:** real issues other tools missed; a genuinely-clean repo with zero such findings is a CORRECT outcome (not a quota).
- **Reproducible verdict:** same repo + same APAA version → same verdict (via memoization, per honest reframe).
- Hit the precision bar BEFORE any externalization conversation.

## Market intelligence (from research — preserve for PRD)
- AI-coding-agent market ~$9.8-11.0B annualized (Apr 2026); Gartner +1,445% multi-agent enterprise inquiries.
- Quality gap: AI code ~1.7× more issues; 110k+ surviving AI-introduced issues (Feb-2026 study); CSA flags AI-CVE surge.
- Bottleneck moved generation → assurance ("verification is the new bottleneck"); 2026 "quality tax" = senior eng 10-15 hrs/wk on brittle AI tests.
- Coverage already felt as misleading; code-review-tool FP fatigue (Sonar 40-60%, Snyk FP 6.8/10) → buyers want a VERDICT not another findings firehose.
- EU AI Act high-risk obligations bite **Aug 2, 2026** (timing hook — but frame APAA as "evidence that feeds readiness," NOT "satisfies the regulation").
- Category whitespace real: incumbents = "find more bugs" (CodeRabbit/Greptile/Qodo) / "find vulns" (Sonar/Snyk/Semgrep) / "check my tests" (Stryker/PIT, language-siloed) / "govern my models" (Credo/Holistic, not the code artifact). None ships a coverage-grounded release verdict.

## Competitive deltas (per cluster)
- **vs review bots:** they comment on a diff + trust green tests; APAA audits whole repo, downgrades vacuous tests, issues a defensible verdict + coverage ledger.
- **vs SAST:** not a scanner; doesn't add to 40-60% FP pile; covers AI-specific defects pattern-matching SAST structurally misses.
- **vs mutation tools:** language-siloed dev tooling; APAA operationalizes the insight stack-agnostically into an automated release audit with an auditable record.
- **vs AI governance (Credo/Holistic):** they govern models/paperwork; APAA audits the shipped code — COMPLEMENTARY, integration not competition.
- **vs manual PRR/QA:** replaces 10-15 hrs/wk human babysitting with deterministic, repeatable, machine-verifiable audit + coverage honesty.

## Rejected / deferred ideas (don't re-propose at the wrong phase)
- **Forward customer quoting (E1-3) + EVM (F1-3) + estimator (D1-5):** DEFERRED to V3 ("cost estimation is becoming its own product"). V1 keeps ONLY a crude budget ceiling (Cost Governance). Naming "Cost Governance vs Cost Intelligence" is the creep-proof boundary.
- **Memory (G3) / CQRS reporting platform (G2) / cache (G4):** V4. Memory MUST stay OUT of the verdict-critical path (else two identical repos diverge — reproducibility break).
- **Traceability (#13) / PRR (#8) / rich standards mapping:** V2 (doc-dependent + expensive; ~70% of repos can't support traceability → becomes a finding, not a crash).
- **Bit-identical reproducibility:** REJECTED as infeasible → replaced by deterministic-ledger + memoized-stable verdict.
- **Renaming headline verdict to "NO BLOCKING FINDINGS (audited scope)":** OPEN (accepted-alt-on-table for rubber-stamp defense; not locked).

## Open questions (unresolved — for PRD to resolve)
- Operational definition of "critical subsystem" (who declares it; how `% deep` is computed — file count vs LOC vs risk-weighted).
- Exact Prosecutor mechanism (another LLM? same nondeterminism concerns recurse).
- Precision ≥80% achievability with V1 heuristics alone (no pilot data yet; mutation testing is V2).
- Validation protocol specifics (named validator, expert-hours/repo, pass/fail rule per metric) — flagged as a V1 deliverable.
- Whether/when to commit to the open-standard play (venues: OpenSSF, CWE/ASVS, in-toto/SLSA, CSA).
- Headless-invariance vs a landing-page audit-runner — confirm the runner counts as marketing surface, not a §3.7 UI violation if APAA inherits Minions' headless rule.

## Independent / NOT-APAA-scope
- **Minions pre-flight cost-estimator epic (D5):** a Minions enhancement on Minions' OWN backlog (verified gap: `minions_core/cost/` has budget_guardrails + worker_billing + CostAttributionEngine, and `subtask_decomposer.py` emits only `estimated_parallel_factor` — NO deterministic pre-flight per-worker cost estimate). Different product, different track, NOT gated by APAA V3. One design, dual home.
