---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - argus/verdict/verdict_gate.py
  - argus/detectors/vacuous_test.py
  - argus/detectors/secret_scan.py
  - argus/detectors/orphan_code.py
  - argus/detectors/tool_runner.py
  - _bmad-output/design-artifacts/ArgusAgent/stories/16-4-ratify-run-adjudicate-and-let-the-arithmetic-decide.md
  - _bmad-output/design-artifacts/ArgusAgent/deferred-work.md
workflowType: 'research'
lastStep: 6
addendum: 'gap-2-closed-by-measurement-2026-08-22'
correction: 'widening-estimate-falsified-2026-08-22'
research_type: 'technical'
research_topic: 'ArgusAgent detector categories — state of the art, optimization paths, and competitive landscape'
research_goals: 'Identify what could raise verdict-eligible yield and precision across all four detector categories, so the DF-13-5-A round decision (HALT-1) is taken against evidence rather than assumption.'
user_name: 'XAgent007'
date: '2026-08-21'
web_research_enabled: true
source_verification: true
---

# Research Report: technical

**Date:** 2026-08-21
**Author:** XAgent007
**Research Type:** technical

---

## Research Overview

This report examines all four ArgusAgent detector categories — vacuous/assertion-free test detection, secret scanning, orphan/dead-code detection, and tool-failure & traceability signals — across three dimensions: current state of the art, optimization paths toward verdict-eligible promotion, and the competitive landscape. It was commissioned to inform the `DF-13-5-A` round decision (HALT-1 on Story 16.4) with evidence rather than assumption, and every external finding is mapped onto ArgusAgent's shipped contract rather than assessed generically.

The central conclusion is that ArgusAgent's precision gate is blocked by an **empty verdict-eligible population**, not by poor precision — and the emptiness has a mechanical cause independent of corpus size. The current promotion predicate (fact (b)) requires that no call to the code under test has its result consumed, which makes it structurally blind to weakly-constrained results (`assert r is not None`) while catching only wholly-ignored ones. Industry evidence identifies weak assertions as the most frequent defect in machine-written tests, so the rule is blind precisely where the defect population is largest and growing. Supporting findings establish that competitor precision figures (tsDetect 96%, PyNose 94%) measure definition-conformance and are not comparable to ArgusAgent's human-adjudicated defect-reality score; that `AR8`/`NFR-D2` do not block stronger corroboration because Architecture Decision E's port-and-recording pattern already generalises; and that credential verification — the most-advertised competitor technique — is permanently excluded by the project's own security contract.

The recommended sequence is to close a zero-cost research gap first (measure the weak-assertion versus ignored-result split across the existing 4,284-finding advisory population), carry that result into HALT-1, and prioritise Story 6.2's dataflow grounding — extended to grade assertion *strength* — ahead of any corpus expansion. Full findings, the ranked promotion backlog, risk assessment and research gaps are in the Research Synthesis section below.

---

## Technical Research Scope Confirmation

**Research Topic:** ArgusAgent detector categories — state of the art, optimization paths, and competitive landscape

**Research Goals:** Identify what could raise verdict-eligible yield and precision across all four detector categories, so the `DF-13-5-A` round decision (HALT-1) is taken against evidence rather than assumption.

**Technical Research Scope:**

- Architecture Analysis — detection algorithms, corroboration models, promotion criteria
- Implementation Approaches — how competing tools decide "report vs. stay quiet"
- Technology Stack — AST / dataflow / mutation / entropy / verification substrates per category
- Integration Patterns — CI gating, exit-code contracts, SARIF, pre-commit, PR annotation
- Performance Considerations — cost per repo, latency, determinism, false-positive economics
- **Competitive Study (added)** — named tools per category, precision claims, and how they justify them
- **Optimization Study (added)** — concrete advisory → verdict-eligible promotion paths, ranked by yield-per-effort

**Research Methodology:**

- Current web data with rigorous source verification
- Multi-source validation for any claim load-bearing on a promotion recommendation
- Confidence levels applied; vendor claims labelled as vendor claims, distinct from peer-reviewed measurement
- Findings mapped to ArgusAgent's shipped contract (`depth_supported is not None`, the FR16 four-row table, cross-cutting #6) rather than offered as generic advice

**Standing question carried through every step:** *does this raise verdict-eligible yield, and would it survive the false-accusation moat?*

**Scope Confirmed:** 2026-08-21

---

## Technology Stack Analysis

> **Template adaptation, stated openly.** The standard step-02 sections (relational/NoSQL databases, cloud providers, container orchestration) do not apply: ArgusAgent is a filesystem-contained, zero-network, zero-token deterministic analyser (AR8 purity, NFR-D2). Those sections are replaced by **Analysis Substrates**, **Detection Technique Stack**, and **Evidence & Interchange Formats**, which are the real "stack" decisions in this domain. A deliberate deviation, not an omission.

### Analysis Substrates

The substrate sets the ceiling on what any detector in the category can ever prove. Four are in industrial use, in ascending order of resolving power and cost:

- **Incremental parser substrates** — **tree-sitter** offers a uniform C API across a growing language set, with high-performance incremental parsing and robust error recovery: the property that lets one engine reach many languages without a per-language frontend. This is ArgusAgent's substrate (Story 1.4). Its structural limit is that it yields a **syntax** tree, not a resolved semantic graph — callee identifiers arrive unbound to definitions.
- **Native per-language AST substrates** — **Vulture** parses with Python's own `ast` module. Higher per-language fidelity, zero multi-language reach.
- **Resolved semantic graph substrates** — **CodeQL** compiles code into a queryable database supporting cross-file, cross-procedural reasoning. **SonarSource** analysers sit between.
- **Pattern / lexical substrates** — **Semgrep** (syntax-aware pattern matching) and the regex-plus-entropy engines underpinning every mainstream secret scanner.

_Confidence: HIGH — substrate taxonomy corroborated across tool documentation and the GitHub static-analysis paper._
_Source: [Incremental Parsing Using Tree-sitter](https://tomassetti.me/incremental-parsing-using-tree-sitter/) · [Static Analysis at GitHub (ACM)](https://dl.acm.org/doi/fullHtml/10.1145/3487019.3487022) · [tree-sitter-analyzer](https://pypi.org/project/tree-sitter-analyzer/1.7.1/)_

**Finding with direct bearing on ArgusAgent.** The unresolved-name-graph limitation recorded as `DF-1-4-A` is **not an ArgusAgent defect — it is the industry-standard position.** SonarQube's own `S2699` ("Tests should include assertions") explicitly *does not perform cross-file analysis*, and Sonar documents this as the acknowledged cause of its false positives, with the recommended workaround being a naming convention (`assert*` prefix) rather than deeper analysis. ArgusAgent's conservative under-claiming on the same substrate is a **stricter** response to the same constraint than the market leader's.

_Confidence: HIGH — Sonar's own rule documentation and community threads._
_Source: [SonarQube S2699 rule](https://next.sonarqube.com/sonarqube/coding_rules?open=java%3AS2699&rule_key=java%3AS2699) · [Sonar community FP thread](https://community.sonarsource.com/t/rule-s2699-tests-should-include-assertions-assertions-stored-in-a-separate-file/109286)_

### Detection Technique Stack, by Category

| Category | ArgusAgent today | Industry technique set | Independent corroboration substrate available? |
|---|---|---|---|
| Vacuous tests | assertion-density + mock-ratio heuristic → two-fact AST provenance shape | named-assertion-library recognition; test-smell taxonomies; **mutation testing** | **Yes — mutation testing yields dynamic ground truth** |
| Secrets | regex families + Shannon entropy, advisory-only | same, **plus live credential verification** | **Yes — API verification** |
| Dead code | unresolved-name reachability, conservative | native-AST reachability + entry-point config + confidence scoring | **Yes — runtime coverage / production telemetry** |
| Tool failure & traceability | recorded as an advisory finding | typically a build failure or a SARIF notification, not a finding | N/A — a run-state fact, already certain |

**The single most consequential pattern in this table:** in three of four categories the industry has an **independent, non-heuristic fact** available that ArgusAgent does not currently consume — and ArgusAgent's own promotion contract (`depth_supported is not None`) is precisely a demand for such a fact.

### Development Tools and Platforms

**Test-smell / assertion detection.** **tsDetect** (Java, 21 smells), **PyNose** (Python, 19 smells, PyCharm plugin), **TEMPY** (Python), **SoCRATES** (Scala), **xNose** (C#), **RAIDE** and **DARTS** (Java, with refactoring). A systematic mapping study identifies 22+ frameworks across languages. Critically, **all are advisory smell reporters — none carries a release-gating verdict**, which is the market gap ArgusAgent occupies.

_Confidence: HIGH — peer-reviewed mapping study plus individual tool papers._
_Source: [Test Smell Detection Tools: A Systematic Mapping Study (EASE '21)](https://dl.acm.org/doi/10.1145/3463274.3463335) · [tsDetect (ESEC/FSE '20)](https://dl.acm.org/doi/10.1145/3368089.3417921) · [PyNose (arXiv 2108.04639)](https://arxiv.org/pdf/2108.04639)_

**Mutation testing.** **PIT/PITest** (Java, de-facto standard), **Stryker** (JS/TS and others), **mutmut**, **MutPy**, **Cosmic Ray**, **Mutatest** (Python). Mutation testing is the only technique in the category that answers *"would this test detect a defect?"* by execution rather than structural inference — and it specifically catches **weak assertions**, which is exactly ArgusAgent's target defect class.

_Confidence: HIGH for the technique; MEDIUM for relative tool effectiveness (comparative studies disagree by workload)._
_Source: [Stryker Mutator docs](https://stryker-mutator.io/docs/) · [Static and Dynamic Comparison of Mutation Testing Tools for Python (SBQS '24)](https://dl.acm.org/doi/10.1145/3701625.3701659)_

**Secret detection.** **TruffleHog** (700+ detectors with active API verification), **Gitleaks** (speed, pre-commit), **detect-secrets** (Yelp), **GitHub Secret Scanning** + push protection, **SpectralOps**, **GitGuardian/ggshield**, **Semgrep Secrets**, **Nosey Parker**.

_Confidence: HIGH — detector count and verification semantics taken from the project's own repository documentation._
_Source: [TruffleHog repository](https://github.com/trufflesecurity/trufflehog)_

**Dead-code detection.** **Vulture** (Python, `ast`-based, confidence-scored 60%/100%, whitelist suppression), **Knip** (JS/TS, manifest + entry-point aware, auto-fix), **ts-prune**, **unimported**, plus platform inspections in **IntelliJ**, **SonarQube**, and **CodeQL**.

_Confidence: HIGH for mechanism; MEDIUM for the FP counts cited in step 05 (single practitioner study, not peer-reviewed)._
_Source: [Dead code tool comparison](https://www.pistack.xyz/posts/2026-06-19-dead-code-detection-tools-knip-ts-prune-vulture-unimported/) · [Practitioner scan of Flask/FastAPI and 7 other repos](https://dev.to/duriantaco/python-dead-code-i-scanned-flask-fastapi-and-7-other-popular-repos-heres-what-i-found-5c1c)_

### Evidence and Interchange Formats

- **Interchange** — **SARIF 2.1.0** is the ecosystem-standard result format and the ingestion path into GitHub code scanning. It carries a `notifications` channel for tool-execution conditions distinct from `results` — the structural equivalent of ArgusAgent's `tool_runner` findings, which ArgusAgent currently models as findings instead.
- **State** — content-addressed stores and pinned-object reads (ArgusAgent's approach) are unusual in this market; most competitors are stateless per-run scanners with server-side history.
- Traditional storage tiers (SQL, NoSQL, in-memory, warehousing) and cloud/container/serverless platform tiers are **not applicable** to a filesystem-contained deterministic analyser and are deliberately not surveyed.

_Confidence: MEDIUM — SARIF notification semantics not yet verified against the specification; flagged for step-03 verification._

### Technology Adoption Trends

- **Migration pattern — from matching to proving.** The clearest cross-category trend is displacement of pure pattern-matching by an **independent verifying fact**. TruffleHog's verification, Vulture's confidence tiers, and mutation testing all instantiate the same move: pair a cheap high-recall signal with an expensive high-precision confirmation, and report the tiers separately. ArgusAgent's advisory / verdict-eligible split is the **same architecture**, implemented before the market converged on it — but with only one confirmation mechanism wired (AST provenance shape), applied to only one of four categories.
- **Emerging.** LLM-assisted test-smell detection is an active research front with mixed reported results and no determinism story — directly incompatible with NFR-D2 as written.
- **Legacy / declining.** Entropy-only secret detection, and binary (unconfidenced) dead-code reporting, are both documented as the dominant false-positive sources in their categories.
- **Community signal.** The recommended production posture in secret scanning is explicitly **tiered** — fast scanner at pre-commit, verifying scanner in CI, platform scanner as backstop — a market validation of severity tiering over single-verdict reporting.

_Confidence: MEDIUM-HIGH — trend synthesis across multiple secondary comparisons plus primary tool documentation._
_Source: [Evaluating LLMs in Detecting Test Smells (arXiv 2407.19261)](https://arxiv.org/pdf/2407.19261) · [A Comparative Study of Software Secrets Reporting by Secret Detection Tools (ESEM 2023)](https://arxiv.org/abs/2307.00714)_


---

## Integration Patterns Analysis

> **Template adaptation, stated openly.** The standard step-03 sections (REST/GraphQL/gRPC, message brokers, service mesh, saga patterns, CQRS) describe distributed-system integration and do not apply to a headless single-process analyser. They are replaced by **Invocation & Gating Contracts**, **Result Interchange**, **Tiered Deployment Interoperability**, **Agent Integration**, and **Integration Security** — the last of which turns out to carry the decisive constraint for this entire research effort.

### Invocation and Gating Contracts

The category's equivalent of "API design" is the **process contract** a CI system reads.

- **Exit-code contracts.** ArgusAgent ships `AuditVerdict.exit_code` of `0` / `2` / `3`, with `1` reserved for crash (`argus/cli.py:310`, `_CRASH_EXIT_CODE`). `main()` returns the code and the console wrapper calls `sys.exit(main())`, keeping the gate testable without process exit. This three-plus-crash shape is stricter than the market norm, where most scanners collapse to `0`/non-zero and cannot distinguish *"I found something"* from *"I could not see enough to judge"*.
- **Severity-threshold gating.** The dominant competitor pattern is a `--severity-threshold` / `--fail-on` flag that lets the consumer pick the blocking line. ArgusAgent deliberately does **not** expose this: the blocking line is fixed by the FR16 decision table and cross-cutting #6. That is a defensible product stance (the consumer cannot weaken the moat) but it is also the reason ArgusAgent's yield problem cannot be solved by configuration.
- **Pre-commit vs CI vs platform.** The secret-scanning market has converged on a three-tier posture — fast scanner at pre-commit, verifying scanner in CI, platform scanner as backstop. ArgusAgent currently occupies only the CI tier.

_Confidence: HIGH for ArgusAgent's own contract (read from source); MEDIUM-HIGH for the market norm (multiple secondary comparisons)._
_Source: [Gitleaks vs TruffleHog vs GitHub Secret Scanning](https://secrails.com/blog/trufflehog-vs-gitleaks-github-secret-scanning-guide) · [Secret scanning tool comparison](https://safeguard.sh/resources/blog/best-secrets-detection-tools-compared-2026)_

### Result Interchange

**SARIF 2.1.0 (OASIS) is the ecosystem standard** and the ingestion path into GitHub code scanning. The specification draws a distinction that maps directly onto an open ArgusAgent design question:

- A **result** is *"a reporting item that describes a condition present in an artifact"* (spec §3.27).
- A **notification** is *"a reporting item that describes a condition encountered by a tool during its execution"* (spec §3.58), carried on `invocation.toolExecutionNotifications` (§3.20.21) and `invocation.toolConfigurationNotifications` (§3.20.22).

**Finding.** ArgusAgent's `tool_runner` findings — tool failure and unestablishable traceability — are, by this definition, **notifications, not results**. They describe conditions encountered by the tool, not conditions present in the audited artifact. ArgusAgent models them as advisory findings instead. This is an interoperability divergence, and it independently corroborates the existing decision to keep them non-blocking: they are not results at all in the ecosystem's vocabulary, so promoting them to verdict-eligible would be a category error rather than a threshold change.

_Confidence: HIGH — quoted from the OASIS specification._
_Source: [SARIF 2.1.0 specification (OASIS)](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html) · [SARIF schema](https://github.com/oasis-tcs/sarif-spec/blob/main/sarif-2.1/schema/sarif-schema-2.1.0.json) · [GitHub SARIF support](https://docs.github.com/en/enterprise-server@3.0/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning)_

### Agent Integration

ArgusAgent publishes an **MCP server exposing exactly one tool** (`argus/mcp/protocol.py`, DN-3), whose `inputSchema` is *derived* from `argus.cli.build_parser` rather than hand-written — so the agent-facing contract cannot drift from the CLI it fronts. The server offers tools only: no resources, no prompts, no sampling. A guard refuses to publish an empty schema, on the reasoning that a silently empty walk would publish a tool that accepts nothing.

This is a materially stronger agent-integration story than the competitor set, where MCP exposure is typically a wrapper script. It matters for the optimization study because **an agent consumer reads the tool description before deciding to call it** — which is why the FR34 disclosure and the egress statement are carried in the description rather than only in output.

_Confidence: HIGH — read from source._

### Integration Security Patterns — the decisive constraint

This section carries the single most important finding of the research so far.

**ArgusAgent's egress posture (NFR-S6):** *"no source code, prompt or repository content leaves the machine on the default path"* (`argus/audit/deep_pass.py:4`). Exactly one opt-in seam exists — `deep_audit`, off by default — and its published statement reads:

> *"`deep_audit` is the ONLY opt-in to egress and is off by default, always. Setting it true SENDS REPOSITORY METADATA TO A THIRD-PARTY PROVIDER, and the run states what will be transmitted and to which provider on stderr before the first byte leaves. **No credential is accepted, stored or read by this surface.**"*

**The competing technique:** TruffleHog's verification works by *authenticating the candidate credential against the real provider API* — a `GetCallerIdentity` call for AWS, a test request to Stripe for a Stripe key. Verification therefore **requires network egress and transmits the candidate secret itself to a third party**. Documented consequences include inability to run in air-gapped or restricted CI without allowlists, and the possibility of tripping rate limits or alerting on the target service.

**The collision, stated precisely.** Adopting verification-based promotion for the secrets detector would require transmitting exactly the bytes that `NFR-S1`, `NFR-S2` and `FR28` guarantee never leave the producer — the guarantee that Story 4.4's CI-blocking randomized property suite exists to enforce — and would do so on a path the published MCP description asserts accepts no credential at all. It is not a threshold change or a new flag. **It contradicts the product's stated security contract at three independent points simultaneously.**

_Confidence: HIGH — ArgusAgent constraints read from source; TruffleHog mechanism from the vendor's own engineering write-up plus the project repository._
_Source: [How TruffleHog Verifies Secrets (vendor)](https://trufflesecurity.com/blog/how-trufflehog-verifies-secrets) · [TruffleHog repository](https://github.com/trufflesecurity/trufflehog) · [TruffleHog verification and egress constraints](https://appsecsanta.com/trufflehog)_

**Consequence for the optimization study.** The most attractive promotion candidate identified in step 02 — secret verification, the technique with the cleanest independent fact and the strongest market validation — is **architecturally unavailable to ArgusAgent without either abandoning NFR-S6/S1/S2 or building a second opt-in egress seam that carries live credentials.** This must be carried into step 04 as a hard constraint, not an implementation detail. The ranked backlog in step 06 will reflect it.


---

## Architectural Patterns and Design

> **The central question of this research, stated plainly:** every independent corroborating fact identified in step 02 is produced *outside* a pure, read-only, zero-egress analyser. Verification needs the network; mutation testing and coverage need execution. `AR8` forbids I/O in the core and `NFR-D2` requires a deterministic, zero-token result. Is corroboration therefore architecturally impossible for ArgusAgent — or is there a shipped pattern that already resolves it?

### System Architecture Patterns

**The determinism-quarantine pattern (ports and adapters), already shipped.** ArgusAgent has solved this exact problem once, for the LLM. Architecture Decision E, quoted in `argus/audit/ports.py`:

> *"the `LLMDispatchPort` is the only seam between the pure core and the non-deterministic LLM substrate; everything downstream is pure folds over recordings."*

The structure is: a `typing.Protocol` port (DIP) that is **pure-importable** — carrying the Protocol, frozen request/response DTOs and typed errors, and nothing else (no provider import, no web framework) — with the impure adapter quarantined in a single module (`minions_llm_adapter`). Redaction is a **property of the producer, not a post-filter**: the recording DTO *has no field that could hold source bytes*.

**This generalises.** The pattern does not care whether the non-deterministic substrate is an LLM, a mutation engine, or a coverage run. Any of them can be quarantined behind a port whose output is a **recording**, after which the verdict fold stays exactly as pure as it is today. The determinism claim survives intact because the recording is a *recorded input*, and a pure fold over a fixed recording is byte-reproducible by construction — which is precisely how ArgusAgent already treats the coverage ledger.

**And the fit is better than the LLM's.** Mutation testing at a pinned tree with a fixed seed is *deterministic and reproducible* in a way an LLM never is. It therefore satisfies protocol §4's determinism precondition natively, rather than needing the two-run reproducibility check bolted around it.

_Confidence: HIGH — pattern read directly from shipped source and its architecture citations._

**The architectural conclusion:** corroboration is **not** blocked by `AR8`/`NFR-D2`. It is blocked by the *cost and risk* of the specific substrate. Those differ enormously by category, and conflating them is the error to avoid.

### Design Principles and Best Practices

- **Advisory-by-contract (cross-cutting #6).** ArgusAgent's split — cheap high-recall signal reported advisory, expensive independent fact required for a blocking verdict — is now the market-convergent design. TruffleHog's verified/unverified/unknown triple, Vulture's 60%/100% confidence tiers, and the pre-commit/CI/platform tiering of secret scanning are all instances of the same principle. ArgusAgent implemented it before the convergence and enforces it more strictly than any competitor found.
- **Conservative default as a moat.** The rule that when evidence is insufficient the finding does **not** gain eligibility (*"a false 🔴 is the lethal failure; a real vacuous test left advisory is tolerable"*) is the inverse of the market's dominant failure. The measured consequence of the opposite choice: a dead-code tool reporting 644 issues of which 52 were real *"trains you to ignore static analysis entirely."*
- **The principle ArgusAgent is missing.** Competitors pair a strict tier with a *deliberately generous* one and let the consumer see both. ArgusAgent does this too — but only one of its four categories has a strict tier wired at all, so three categories are permanently advisory not by judgement but by absence of a mechanism.

_Confidence: HIGH for the principle mapping; MEDIUM for the 644/52 figure (single practitioner study)._
_Source: [Dead code detection practitioner study](https://dev.to/duriantaco/python-dead-code-i-scanned-flask-fastapi-and-7-other-popular-repos-heres-what-i-found-5c1c) · [Exposing dead code: detection strategies](https://vfunction.com/blog/dead-code/)_

### Scalability and Performance Patterns

The historic objection to mutation testing is cost, and the market has answered it with **incremental analysis**.

- **StrykerJS incremental mode** tracks code and test changes, runs mutation testing only on changed code, and still emits a full report.
- Reported practical envelope: a typical 200-line PR generates roughly **40–80 mutations**, and running the relevant test subset against them takes **minutes rather than hours**; with incremental mode plus parallel execution, **1–5 minutes per PR** for most codebases.
- The standard adoption posture is tiered by cadence: incremental on PRs, full runs nightly or weekly.

_Implication for ArgusAgent:_ a mutation-evidence pass would be economically viable **only** in the incremental/changed-code posture, never as a full-corpus sweep across a five-to-eight member validation bench. This is a genuine constraint on how such evidence could ever be gathered for the precision gate, and it is discussed further in step 06.

_Confidence: HIGH for the mechanism (vendor documentation); MEDIUM for the timing figures (vendor and practitioner sources, workload-dependent)._
_Source: [Announcing StrykerJS incremental mode](https://stryker-mutator.io/blog/announcing-incremental-mode/) · [Stryker incremental docs](https://stryker-mutator.io/docs/stryker-js/incremental/) · [Mutation testing in CI: practical cadence](https://autotomy.dev/blog/mutation-testing-takes-4-hours-how-do-teams-actually-use-it-in-ci/)_

### Integration and Communication Patterns

The recording-as-contract pattern is what makes the quarantine safe, and it has a property worth naming: **the DTO's shape is the security control.** `LLMRecording` cannot leak source bytes not because a filter removes them but because no field exists to hold them. Any future evidence port should be designed the same way — a `MutationRecording` carrying *mutant killed/survived counts and identifiers*, with no field capable of holding audited source.

This also answers a question the optimization study would otherwise have to ask: whether consuming external evidence forces ArgusAgent to retain third-party source. It does not, provided the recording DTO is designed under the same producer-side-redaction rule.

_Confidence: HIGH — read from source._

### Security Architecture Patterns

Three candidate substrates, three sharply different risk postures. **This is the section that separates them.**

| Substrate | What it requires | Risk class | Verdict |
|---|---|---|---|
| **Credential verification** | transmit the candidate secret to a third-party API | violates `NFR-S6` egress, `NFR-S1`/`NFR-S2`/`FR28` containment, and the published MCP statement that no credential is accepted | ⛔ **Architecturally excluded** |
| **Mutation testing** | execute the audited repository's test suite | **arbitrary third-party code execution** on the auditing host | ⚠️ Available only behind sandboxing + opt-in |
| **Coverage / telemetry** | execute the audited repository, or instrument its production | same execution risk, plus a dependency on the audited party's runtime | ⚠️ Same class; additionally impractical for a third-party validation bench |

**The execution risk is not a formality for this project.** ArgusAgent's entire operating model is reading **pinned git objects** without executing anything — `ls-tree` + `cat-file`, every staged byte proved against the pinned blob. Running `celery`'s or `conda`'s test suite to obtain mutation evidence is a categorically different security posture from reading their bytes: it grants arbitrary code execution to the audited party, on the machine performing the audit. Any such pass needs container or VM isolation as a precondition, not as a hardening step.

_Confidence: HIGH — ArgusAgent's read-only model verified in source; execution risk is a general property of mutation and coverage tooling._

### Data Architecture Patterns

- **Recordings as the only inputs to the fold.** Every gate arm — breadth, seal, yield, precision — already folds over recorded rows rather than live computation. Adding a new evidence class means adding a new recording type, not a new computation path in the gate.
- **Content-addressed, supersede-never-erase.** The 13.5 precedent (`adjudication-set-13-5.json` superseding by name, the prior set retained byte-unchanged) is the correct model for any future evidence artifact, and it is unusual in this market: competitors are stateless per-run scanners with server-side history.
- **Pinned-object reads.** Reading from the git object database rather than the working tree is a genuine architectural differentiator; no competitor surveyed proves staged bytes against a pinned blob.

_Confidence: HIGH — read from source and prior story records._

### Deployment and Operations Architecture

- **Opt-in seam as the deployment unit.** `deep_audit` establishes the shipped precedent: off by default, always; a disclosure on stderr naming what will be transmitted and to which provider *before the first byte leaves*. Any evidence port should ship the same way — default off, disclosed at dispatch, and absent from `sys.modules` on the default path (the existing `NFR-S6` import guard pattern).
- **Cadence tiering.** The market runs cheap checks per-commit and expensive corroboration on a slower cadence. ArgusAgent's single-invocation model has no cadence concept, which is why an expensive evidence pass has nowhere natural to live today.
- **The zero-change path exists and should be ranked.** Not every improvement requires crossing the purity boundary: **Story 6.2's full dataflow / scope-resolved grounding** (`DF-14-1-A`) strengthens fact (b) *inside* the pure core, with no port, no execution, no egress and no new risk posture. It is the only candidate on the table that changes nothing architecturally — and it is already scheduled.

_Confidence: HIGH — 6.2 and `DF-14-1-A` verified in the repository's own records._


---

## Implementation Approaches and Technology Adoption

### Competitive Precision Landscape — the numbers, and why they are not comparable

| Tool | Category | Precision | Recall | What the number was measured against |
|---|---|---|---|---|
| **tsDetect** | test smells (Java) | **96%** avg (85–100% by smell) | **97%** avg (90–100%) | curated benchmark of 65 unit-test files with known instances of 19 smell types |
| **PyNose** | test smells (Python) | **94.0%** weighted | **95.8%** | agreement with human raters across 19 smell types |
| **GitHub Secret Scanning** | secrets | **75%** | — | ESEM 2023 study, 9 tools |
| **Gitleaks** | secrets | **46%** | **88%** | same study |
| **SpectralOps** | secrets | — | **67%** | same study |
| **TruffleHog** | secrets | — | **52%** | same study |
| **"Commercial X"** | secrets | **25%** | — | same study |
| **Vulture** | dead code | not reported as a rate | — | practitioner scan: **260 false positives on Flask alone** |
| **ArgusAgent** (pre-Epic-14 rule) | vacuous tests | **0%** (0 TP / 26 FP / 5 borderline) | — | **named-human adjudication over a 5-repository ratified corpus** |
| **ArgusAgent** (corrected rule) | vacuous tests | **UNEVALUABLE** | — | 0 blocking findings of 4,284 emitted |

⛔ **The most important observation in this research: these numbers measure different things, and reading them as a league table is the error the whole study exists to prevent.**

- tsDetect's 96% and PyNose's 94% answer *"did the tool correctly apply its own definition of the smell?"* They are **definition-conformance** scores, measured against curated benchmarks or rater agreement.
- ArgusAgent's 0-of-26 answers *"did a named human, adjudicating under a written protocol, judge this a real defect worth blocking a release for?"* That is a **defect-reality** score.

A tool can score 96% on the first and near-zero on the second, because correctly identifying a test as matching a smell definition says nothing about whether the smell is a defect. **No competitor surveyed is held to ArgusAgent's standard, because no competitor gates a release on the answer.** ArgusAgent's disappointing number is not evidence that it detects worse than tsDetect; it is evidence that it measured something the category does not measure.

_Confidence: HIGH for the figures (peer-reviewed sources and the project's own record); the comparability analysis is this report's own reasoning, offered as analysis, not as a cited finding._
_Source: [tsDetect (ESEC/FSE 2020)](https://dl.acm.org/doi/10.1145/3368089.3417921) · [tsDetect technical paper](https://testsmells.org/assets/publications/FSE2020_TechnicalPaper.pdf) · [PyNose (arXiv 2108.04639)](https://arxiv.org/pdf/2108.04639) · [Secret detection comparative study (ESEM 2023)](https://arxiv.org/abs/2307.00714) · [Dead-code practitioner scan](https://dev.to/duriantaco/python-dead-code-i-scanned-flask-fastapi-and-7-other-popular-repos-heres-what-i-found-5c1c)_

### Testing and Quality Assurance — the industry baseline for false positives

The context in which ArgusAgent's ≥80% bar should be read:

- Static analysis false-alarm rates reach **up to 90%**; roughly **35%–91%** of warnings reported as bugs are unactionable.
- In a large-scale study across 30 open-source Java projects, **56% of SAST warnings were never addressed** in project history.
- Under manual validation, **only 19.5% of "actionable" warnings represented real bugs**.
- High false-positive rates are consistently shown to undermine developer trust and reduce continued use.

**ArgusAgent's ≥80% precision floor is therefore roughly four times the manually-validated real-bug rate of mainstream static analysis.** It is an exceptionally demanding bar, self-imposed, and — on the evidence of §0.6's zero yield — currently unmet not because precision is low but because the population is empty.

_Confidence: HIGH — multiple peer-reviewed and preprint sources in agreement on the order of magnitude._
_Source: [Do Developers Use SAST Tools Out of the Box? (ACM)](https://dl.acm.org/doi/fullHtml/10.1145/3674805.3690750) · [Recommending Valid Actionable Warnings (arXiv 2511.12229)](https://arxiv.org/html/2511.12229) · [Mitigating False Positive Static Analysis Warnings](https://www.researchgate.net/publication/375259352_Mitigating_false_positive_static_analysis_warnings_Progress_challenges_and_opportunities)_

### Technology Adoption Strategies — mutation evidence, and a contested premise

If mutation testing is the corroborating fact for the vacuous-test rule, the strength of that fact must be established rather than assumed. **The literature is genuinely split.**

- **Just et al. (FSE 2014)** — 357 real faults across 5 open-source applications totalling ~321,000 LOC, with both developer-written and generated suites: mutant detection is **positively and significantly correlated** with real fault detection, *independently of code coverage*.
- **Papadakis et al. (ICSE 2018)** — using CoreBench and Defects4J: the correlations reported in prior work are **confounded by test-suite size**, and when suite size is controlled for, all correlations between mutation score and real fault detection are **weak**.

_Confidence: HIGH that the dispute exists and is unresolved; the reconciliation below is this report's analysis._

**Reconciliation, offered as analysis rather than citation.** The Papadakis critique targets *suite-level aggregate mutation scores* as a proxy for suite quality — and ArgusAgent would not be making that claim. The claim a vacuous-test corroborator needs is narrower and more local: *"this specific test function executed the code under test and killed none of the mutants introduced into it."* That is a direct per-test observation of non-detection, not a statistical inference from an aggregate score, so the suite-size confound Papadakis identifies does not obviously apply. **This distinction is load-bearing and has not been verified against the literature** — it is flagged as a research gap in step 06, not presented as settled.

_Source: [Are Mutants a Valid Substitute for Real Faults? (FSE 2014)](https://homes.cs.washington.edu/~rjust/publ/mutants_real_faults_fse_2014.pdf) · [Are Mutation Scores Correlated with Real Fault Detection? (ICSE 2018)](https://dl.acm.org/doi/pdf/10.1145/3180155.3180183)_

### Development Workflows and Tooling

The consumption pattern across all four categories is **tiered by cost and cadence**, never single-shot:

- fast, cheap, high-recall checks at pre-commit (Gitleaks; linters);
- expensive corroboration in CI, often incremental and changed-code-only (TruffleHog verified; Stryker incremental at 1–5 min/PR);
- full corroboration on a slow cadence (nightly/weekly full mutation runs);
- platform-level backstop (GitHub secret scanning, code scanning via SARIF).

ArgusAgent's single-invocation model has no cadence concept, which is the operational reason an expensive evidence pass has nowhere natural to live today.

_Confidence: HIGH — consistent across vendor documentation and practitioner sources._
_Source: [Stryker incremental](https://stryker-mutator.io/docs/stryker-js/incremental/) · [Mutation testing cadence in CI](https://autotomy.dev/blog/mutation-testing-takes-4-hours-how-do-teams-actually-use-it-in-ci/) · [Secret scanner tiering](https://secrails.com/blog/trufflehog-vs-gitleaks-github-secret-scanning-guide)_

### Team Organization and Skills

ArgusAgent's protocol §2 registers three adjudicator roles and records **two of them (QA Lead, external adjudicator) as unfilled**. This is not incidental to the precision programme — protocol §4's borderline ladder terminates at roles that do not exist, which means a `BORDERLINE` finding has no defined resolution path and correctly renders a round `Unevaluable`.

**No competitor has this problem, because no competitor adjudicates.** The staffing requirement is a direct consequence of choosing defect-reality measurement over definition-conformance measurement. Any future round that can produce borderlines needs at least the QA Lead role filled before the run, not during it.

_Confidence: HIGH — from the project's own protocol and story records._

### Cost Optimization and Resource Management

- **Adjudication is the dominant cost**, and it is human. Protocol §3 sets a ≤4-hour ceiling, recorded as a report and explicitly *never* as a gate, with overruns recorded alongside what made them expensive.
- **Mutation evidence is affordable only incrementally** — 40–80 mutants for a 200-line change, minutes not hours — and correspondingly **unaffordable as a full sweep across a multi-repository bench**, which is exactly the shape a precision gate needs.
- **This is a structural tension, not a tuning problem:** the cheap form of mutation evidence (incremental, changed-code) produces evidence about *a diff*, while the precision gate needs evidence about *a corpus*.

_Confidence: MEDIUM-HIGH — cost figures are vendor/practitioner sourced and workload-dependent._

### Deployment and Operations Practices

Any evidence port should replicate the shipped `deep_audit` posture exactly: off by default always; a disclosure naming what will be transmitted or executed, emitted before the first byte or first process; absent from `sys.modules` on the default path; and a recording DTO with no field capable of holding audited source. Mutation and coverage passes additionally require container or VM isolation as a precondition, since both execute third-party code on the auditing host.

### Risk Assessment and Mitigation

| Risk | Severity | Mitigation |
|---|---|---|
| Secret verification breaches `NFR-S6`/`S1`/`S2`/`FR28` | 🔴 Critical | Do not implement. Excluded architecturally, not deferred. |
| Mutation/coverage evidence executes third-party code | 🟠 High | Container/VM isolation as precondition; opt-in seam; disclosed before execution |
| Mutation-as-ground-truth rests on contested literature | 🟠 High | Establish the narrow per-test claim against the literature **before** building; do not inherit the aggregate-score claim |
| Borderline ladder terminates at unfilled roles | 🟠 High | Fill the QA Lead role before any round capable of producing borderlines |
| Adopting a competitor's precision figure as a benchmark | 🟡 Medium | Never compare definition-conformance scores to defect-reality scores; the report states the distinction explicitly |
| Incremental mutation evidence cannot serve a corpus-level gate | 🟡 Medium | Recognised as structural; treat as a constraint on gate design, not a tooling choice |

---

## Technical Research Recommendations

### Implementation Roadmap

**Tier 1 — no architectural change, already scheduled.**
Complete **Story 6.2** (full dataflow / scope-resolved grounding, `DF-14-1-A`). It strengthens fact (b) inside the pure core: no port, no execution, no egress, no new risk posture, no security review, no new adjudicator role. It is the only candidate that changes nothing architecturally and is already specified.

**Tier 2 — cheap, high-value, non-detector.**
Re-classify `tool_runner` output as SARIF **notifications** rather than results, and emit SARIF alongside the native artifact. Improves interoperability and aligns the vocabulary with the ecosystem. Does not touch the moat.

**Tier 3 — architecturally coherent but expensive.**
A `MutationEvidencePort` on the shipped `LLMDispatchPort` pattern — pure Protocol, quarantined adapter, recording DTO with no source-bearing field, opt-in and disclosed, sandboxed execution. **Do not start** until the narrow per-test claim is established against the literature and the isolation story is designed.

**Excluded — not deferred.**
Credential verification for the secrets detector. It contradicts the published security contract at three independent points and cannot be reconciled by configuration.

### Technology Stack Recommendations

- **Keep tree-sitter.** The multi-language reach is a genuine differentiator and the substrate is not the binding constraint; the predicate is.
- **Do not adopt LLM-based smell detection.** Incompatible with `NFR-D2` as written, and the research results are mixed.
- **If mutation evidence is ever built,** consume an existing engine's output (Stryker/PIT/mutmut) as a recording rather than implementing mutation in-tree.

### Skill Development Requirements

Fill protocol §2's **QA Lead** role before any round that can produce borderlines. The external adjudicator role can remain unfilled provided the ladder is never allowed to reach it — but that must be a designed property, not an accident.

### Success Metrics and KPIs

- **Verdict-eligible yield per 1,000 test functions scored** — the metric that actually gates, currently 0 per 4,284.
- **Adjudicated precision** — retain the ≥80% `Fraction`, unmoved.
- **Definition-conformance precision** — worth tracking *separately* so ArgusAgent can state a number comparable to tsDetect/PyNose without conflating it with the gate.
- **Expert hours per adjudicated finding** — already recorded as a report; keep it a report.


---

# The Empty Population: Why ArgusAgent's Gate Cannot Clear, and What Would Change That

## Executive Summary

ArgusAgent's precision gate is blocked, and the ordinary reading is that the detector is not accurate enough. **That reading is wrong, and this research establishes why.** The gate is blocked because the verdict-eligible population is *empty* — 0 blocking findings out of 4,284 emitted across five ratified repositories — and an empty population is not a precision failure. It is a yield failure, and yield failures have entirely different causes and entirely different remedies.

Three findings, each measured rather than argued, explain the emptiness and reframe the decision in front of the project. **First**, ArgusAgent is held to a measurement standard no competitor in its category is held to: tsDetect's 96% and PyNose's 94% precision are *definition-conformance* scores against curated benchmarks, while ArgusAgent's 0-of-26 is a *defect-reality* score from named-human adjudication. These numbers are not comparable, and treating the disparity as a quality gap is a category error. **Second**, the architecture already contains the pattern needed to consume independent corroborating evidence — Architecture Decision E's determinism quarantine — so `AR8` purity and `NFR-D2` determinism are *not* the barrier to stronger corroboration; substrate cost and execution risk are. **Third**, and most consequentially, the current verdict-eligible predicate is **structurally blind to the most frequent real-world instance of the defect it targets.** Fact (b) requires that *no* call to the code under test has its result consumed. A test that weakly constrains a real result — `assertIsNotNone`, `length > 0`, `toBeDefined` — consumes it, and therefore can never be corroborated, however worthless the assertion. Industry research identifies precisely these weak assertions as the single most frequent defect in AI-generated tests. **ArgusAgent's blocking rule catches ignored results and is deliberately blind to worthless ones.**

The strategic implication is direct. The pre-registered fallback in `DF-13-5-A` says that a disappointing round means *"a materially better detector — NOT a bigger bench."* This research identifies what "materially better" means concretely, and finds that the highest-value change requires no new architecture, no execution sandbox, no egress seam, no additional adjudicator role, and no competitor technology: grade assertion *strength* over the code under test, which is the substance of the already-scheduled Story 6.2 dataflow grounding.

**Key Technical Findings**

- **The verdict-eligible rule is blind to weak assertions by construction** — fact (b)'s "no SUT call consumed" clause excludes the most frequent instance of the target defect class. This mechanically explains the zero yield.
- **Competitor precision figures are not comparable to ArgusAgent's** — definition-conformance (tsDetect 96%, PyNose 94%) versus defect-reality (ArgusAgent, human-adjudicated). No competitor gates a release, so none is measured this way.
- **ArgusAgent's ≥80% bar is roughly 4× the manually-validated real-bug rate of mainstream static analysis**, where 35–91% of warnings are unactionable and only ~19.5% of "actionable" warnings are real bugs.
- **Corroboration is not blocked by the purity rules.** Architecture Decision E's port-and-recording pattern generalises; the real constraints are execution risk and cost, which differ sharply by substrate.
- **Credential verification is architecturally excluded, not merely deferred** — it contradicts `NFR-S6`, `NFR-S1`/`S2`/`FR28`, and the published MCP egress statement simultaneously.
- **The unresolved-name-graph limitation (`DF-1-4-A`) is the industry-standard position**, not an ArgusAgent weakness: SonarQube's equivalent rule does not perform cross-file analysis either, and recommends a naming convention as the workaround.
- **`tool_runner` findings are SARIF *notifications*, not results** — keeping them non-blocking is a correct category judgement, independently corroborated by the OASIS specification.
- **Mutation testing as ground truth rests on contested literature** (Just 2014 vs Papadakis 2018), and the narrower per-test claim ArgusAgent would need has not been established.

**Technical Recommendations**

1. **Complete Story 6.2 (dataflow / scope-resolved grounding) and extend it to assertion *strength*, not only provenance shape.** Highest yield, zero architectural change, already scheduled.
2. **Do not spend the `DF-13-5-A` round on a bigger bench before the predicate changes.** The round measures a rule that cannot see the dominant defect instance; a larger corpus of the same blindness returns the same zero.
3. **Exclude credential verification permanently and record it as excluded**, so it is not periodically rediscovered as an option.
4. **Emit SARIF, and reclassify `tool_runner` output as notifications.** Cheap, standards-aligned, moat-neutral.
5. **Fill protocol §2's QA Lead role before any round capable of producing borderlines**, since §4's ladder currently terminates at an unfilled role.

---

## Table of Contents

1. Research Introduction and Methodology — *this section*
2. Technology Stack Analysis — *see §Technology Stack Analysis above*
3. Integration Patterns Analysis — *see §Integration Patterns Analysis above*
4. Architectural Patterns and Design — *see §Architectural Patterns and Design above*
5. Implementation Approaches and Technology Adoption — *see §Implementation Approaches above*
6. Cross-Cutting Synthesis: The Blindness Finding
7. Competitive Positioning
8. Ranked Promotion Backlog
9. Risk Assessment
10. Future Outlook
11. Methodology, Source Verification and Research Gaps
12. Conclusion

---

## 1. Research Introduction and Methodology

### Research Significance

The defect class ArgusAgent targets is becoming more common, not less. Industry analysis of AI-generated test suites finds that **weak assertions are the most frequent issue** — checks such as `toBeDefined`, `not None`, or `length > 0` that execute the code under test but tolerate wrong values. A controlled study of mutation-feedback test generation measured a vanilla LLM prompt at a **53% mutation score** on HumanEval-Java, unchanged after four iterations without mutation feedback, rising to **89.5%** once mutation feedback was supplied. Tests that run code without meaningfully constraining it are the characteristic failure mode of machine-written tests, and machine-written tests are an increasing share of the corpus.

This makes ArgusAgent's thesis more valuable over time — and makes the blindness identified in §6 more costly, because the growth is concentrated exactly where the current predicate cannot look.

_Confidence: MEDIUM-HIGH — practitioner and vendor analyses in agreement; the MutGen figures are single-study._
_Source: [Mutation Testing for AI-Generated Code](https://www.augmentcode.com/guides/mutation-testing-ai-generated-code) · [Reviewing AI-Generated Tests](https://qaskills.sh/blog/reviewing-ai-generated-tests-checklist-2026) · [Mutation Testing for Agent-Written Code](https://www.awesome-testing.com/2026/08/mutation-testing-for-agent-written-code)_

### Research Methodology

- **Scope** — four detector categories: vacuous tests, secrets, orphan/dead code, tool-failure & traceability. Each examined for state of the art, optimization paths, and competitive landscape.
- **Data sources** — peer-reviewed papers (FSE, ICSE, ESEM, EASE, SBQS), the OASIS SARIF specification, primary vendor documentation, and practitioner measurements, plus direct reading of ArgusAgent's own shipped source.
- **Analysis framework** — every external finding mapped onto ArgusAgent's shipped contract (`depth_supported is not None`, the FR16 four-row table, cross-cutting #6) rather than assessed generically.
- **Verification** — vendor claims labelled as vendor claims; contested literature presented as contested; this report's own reasoning explicitly separated from cited findings.
- **Standing question** — *does this raise verdict-eligible yield, and would it survive the false-accusation moat?*

### Goals and Achieved Objectives

**Original goal:** identify what could raise verdict-eligible yield and precision, so the HALT-1 decision rests on evidence.

**Achieved:**
- A mechanical explanation for the zero yield (§6) that does not depend on corpus size.
- A demonstration that the purity constraints do not block corroboration (§Architectural Patterns).
- A permanent exclusion, with reasons, of the most-advertised competitor technique.
- A ranked backlog separating changes that need architecture from changes that do not.
- Two named research gaps that must close before any Tier-3 work begins.

---

## 6. Cross-Cutting Synthesis: The Blindness Finding

This is the central result of the research, and it is derived from ArgusAgent's own shipped predicate rather than from any external source.

**Fact (b) holds** iff at least one call to the code under test is **discarded**, **no** such call is **consumed**, and at least one assertion references a mock-bound name. The module states the consequence in terms:

> *"a test that constrains the real SUT result — however many mocks it builds, however weak the constraint — can never be corroborated, so it can never take a build to 🔴 on this rule."*

That clause was a deliberate, correct decision: it makes fact (b) independent of the heuristic's own inputs, and it was the Story 14.1 conformance repair that replaced a corroborator agreeing with its own input in 2,527 of 2,529 cases. **Nothing in this research suggests it should be loosened.**

But its consequence is now measurable against the industry's own defect taxonomy:

| Defect shape | Example | Consumed? | Verdict-eligible under fact (b)? |
|---|---|---|---|
| Result **ignored**, assertions on a mock | `add(1,2)` called, `fake.assert_called()` | No | ✅ Yes |
| Result **weakly constrained** | `r = add(1,2); assert r is not None` | **Yes** | ❌ **Never** |
| Result **wrongly constrained** | `r = add(1,2); assert len(r) > 0` | **Yes** | ❌ **Never** |
| Result **correctly constrained** | `r = add(1,2); assert r == 3` | Yes | ❌ No (correct) |

Rows 2 and 3 are defects. Row 4 is not. **Fact (b) cannot distinguish them, because "consumed" is a structural property that ignores what the assertion actually asserts.** And rows 2 and 3 are, on the industry evidence, the most frequent real-world instance of the defect class.

**This explains the zero yield mechanically, without reference to corpus size or corpus composition.** It also predicts that ratifying three more repositories would return approximately the same result — because the population that the rule *can* see (results called and thrown away entirely) is genuinely rare in mature codebases, while the population it *cannot* see is common and growing.

**What "materially better detector" means, concretely.** The upgrade is not a bigger bench or a new substrate. It is a predicate that grades **assertion strength over the SUT result** — distinguishing `assert r == 3` from `assert r is not None` — which requires exactly the dataflow and scope resolution that Story 6.2 (`DF-14-1-A`) is already chartered to deliver. The current predicate approximates "the assertion does not constrain the result" with "the result is not used at all"; 6.2's grounding is what would let it stop approximating.

_Confidence: HIGH for the predicate analysis (read from shipped source); MEDIUM-HIGH for the frequency claim (practitioner analyses, not peer-reviewed measurement)._

---

## 7. Competitive Positioning

**Where ArgusAgent leads.**

- The **only** tool surveyed in the test-quality category that renders a release-gating verdict rather than reporting smells.
- **Advisory-by-contract** enforced structurally — a heuristic-only finding cannot reach a blocking verdict regardless of flags, which no competitor guarantees.
- **Pinned-object reads** with per-byte blob verification; no competitor surveyed proves staged bytes against a pin.
- A **three-state exit contract** (`0`/`2`/`3` plus crash) distinguishing "found something" from "could not see enough to judge" — most scanners collapse to zero/non-zero.
- **Derived MCP schema** so the agent-facing contract cannot drift from the CLI.
- **Human adjudication under a written protocol**, with hours recorded as a report rather than a gate.

**Where ArgusAgent trails.**

- **Yield.** Every competitor reports abundantly; ArgusAgent reports nothing verdict-eligible. The market's problem is too many findings; ArgusAgent's is none.
- **Single-category strictness.** Three of four detectors have no strict tier at all — advisory by absence of mechanism, not by judgement.
- **No cadence model.** Competitors tier by cost (pre-commit / CI / nightly); ArgusAgent has one invocation, so expensive evidence has nowhere to live.
- **No SARIF.** Excludes ArgusAgent from the standard code-scanning ingestion path.
- **Unfilled adjudicator roles**, which cap what any round can conclude.

**The honest summary:** ArgusAgent is a more rigorous instrument than anything in its category, measuring a harder question, and currently finding nothing. Rigour is not the problem; reach is.

---

## 8. Ranked Promotion Backlog

Ranked by yield-per-effort, with architectural cost stated.

| # | Change | Yield impact | Architectural cost | Risk | Status |
|---|---|---|---|---|---|
| **1** | **Story 6.2 dataflow grounding, extended to assertion strength** | **High — addresses the blindness directly** | **None** — inside the pure core | Low | Already scheduled (`DF-14-1-A`) |
| **2** | SARIF emission + `tool_runner` → notifications | None (interop only) | Minimal | Low | Not scheduled |
| **3** | Track definition-conformance precision separately from gate precision | None (comparability only) | Minimal | Low | Not scheduled |
| **4** | `MutationEvidencePort` on the Decision-E pattern | High, if the per-test claim holds | Moderate — new port, adapter, recording DTO | **High** — executes third-party code | Blocked on two research gaps |
| **5** | Coverage/telemetry corroboration for dead code | Moderate | Moderate | High — same execution class | Not recommended for a third-party bench |
| **6** | Credential verification for secrets | High in principle | — | **Critical** | ⛔ **Excluded, not deferred** |

**On item 1 versus item 4.** Item 4 is the more powerful corroborator in the abstract; item 1 is the better decision now. Item 1 changes nothing architecturally, is already specified, needs no sandbox, no egress seam, no new role, and no unresolved literature question — and it targets the defect population that item 4 would also have to reach. Item 4 should not begin until §11's gaps close.

---

## 9. Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Spending the `DF-13-5-A` round before the predicate changes | 🔴 Critical | The round is single-use; §6 predicts the same zero from a larger bench. Sequence the predicate first. |
| Credential verification breaching the security contract | 🔴 Critical | Exclude permanently and record the exclusion |
| Loosening fact (b) to raise yield | 🔴 Critical | Fact (b)'s asymmetry is correct; the fix is a *finer* predicate, never a weaker one |
| Mutation evidence executing third-party code | 🟠 High | Container/VM isolation as precondition; opt-in; disclosed before execution |
| Building on the contested mutation-score premise | 🟠 High | Establish the narrow per-test claim first (§11 gap 1) |
| Borderline ladder terminating at an unfilled role | 🟠 High | Fill QA Lead before any round that can produce borderlines |
| Reading competitor precision as comparable | 🟡 Medium | Distinction documented; track both metrics separately |

---

## 10. Future Outlook

**Near term (1–2 years).** AI-written tests continue to grow as a share of test corpora, and weak assertions remain their characteristic defect. Mutation testing continues moving from research into mainstream CI on the strength of incremental modes. Demand for *verdict-bearing* rather than *advisory* test-quality tooling should rise, because advisory findings do not constrain machine-written code the way a gate does.

**Medium term (3–5 years).** The corroboration pattern — cheap signal plus independent expensive confirmation, reported in separate tiers — is likely to become the category default. ArgusAgent already has this architecture; the question is whether it wires more of its categories into it before competitors adopt the pattern with more yield behind it.

**Innovation opportunity, specific to this project.** Nothing surveyed grades assertion *strength* against dataflow from the code under test and gates on it. Test-smell detectors classify structure; mutation testing measures outcomes by execution. A static, deterministic, execution-free assertion-strength grader would be genuinely novel — and it is what §6 identifies as the highest-value change. That is a defensible position rather than a catch-up move.

---

## 11. Methodology, Source Verification and Research Gaps

**Primary sources** — OASIS SARIF 2.1.0 specification; ArgusAgent's own source (`verdict_gate.py`, `vacuous_test.py`, `secret_scan.py`, `orphan_code.py`, `tool_runner.py`, `ports.py`, `protocol.py`, `cli.py`); peer-reviewed papers at FSE 2014/2020, ICSE 2018, ESEM 2023, EASE 2021, SBQS 2024; TruffleHog and Stryker project documentation.

**Secondary sources** — practitioner measurements and vendor comparisons, used for order-of-magnitude claims and explicitly labelled as such.

**Quality assurance** — every load-bearing claim carries a confidence level. Contested literature is presented as contested. This report's own reasoning (the comparability analysis in step 05, the per-test mutation claim, the blindness derivation in §6) is marked as analysis and distinguished from cited findings.

**⛔ Research gaps — both must close before Tier-3 work begins.**

1. **The narrow per-test mutation claim is unverified.** This report argues that Papadakis's suite-size confound targets aggregate scores and may not apply to a per-test survived-mutant observation. That argument has not been checked against the literature and must be, before any `MutationEvidencePort` is designed.
2. **The frequency claim rests on practitioner sources.** The assertion that weak-assertion tests substantially outnumber ignored-result tests in mature codebases is well-supported for AI-generated code but not measured for the general corpus. It is directly measurable against ArgusAgent's existing 4,284-finding advisory population, at zero cost and with no round spent — **and doing so would test §6's central prediction before any bench decision is taken.**

**Limitations.** No new measurement was performed over any corpus member; the ESEM 2023 secret-scanner figures may not reflect verified-mode operation; competitor precision figures come from the tools' own evaluations and are not independently reproduced here.

---

## 12. Conclusion

### Summary of Key Findings

ArgusAgent's gate is blocked by an **empty population**, not by poor precision, and the emptiness has a mechanical cause: the verdict-eligible predicate can only see tests that discard the result of the code under test, while the dominant real-world defect is a test that *keeps* the result and constrains it worthlessly. Every other finding follows from this. The competitor comparison is not a like-for-like gap but a difference in what is being measured. The architectural constraints are real but not binding on corroboration. The most-advertised competitor technique is permanently unavailable. And the highest-value improvement requires no new architecture at all.

### Strategic Impact

The pre-registered rule in `DF-13-5-A` — *"a materially better detector, NOT a bigger bench"* — is vindicated by this research, and given concrete content for the first time. "Materially better" means grading assertion strength over the code under test. That is Story 6.2's territory, it is already scheduled, and it needs no round spent to begin.

### Next Steps

1. **Close research gap 2 first — it is free.** Measure the weak-assertion versus ignored-result split across the existing 4,284-finding advisory population. It tests §6's prediction, costs nothing, spends no round, and requires no ratification.
2. **Carry the result into the HALT-1 decision.** If §6 holds, ratifying a larger bench measures a rule that cannot see the defect, and the round is better preserved.
3. **Sequence Story 6.2 ahead of any further corpus expansion.**
4. **Record the credential-verification exclusion** so it is not rediscovered.
5. **Defer all Tier-3 work** until both gaps close.

---

**Research Completion Date:** 2026-08-22
**Research Period:** current comprehensive technical analysis
**Source Verification:** all load-bearing claims cited; confidence levels applied throughout
**Technical Confidence Level:** High for findings derived from shipped source and peer-reviewed work; Medium where practitioner sources carry the claim, marked inline

---

# ADDENDUM — Research Gap 2 CLOSED by measurement, 2026-08-22

**Status of this addendum.** The six-step workflow completed 2026-08-22 with two open research gaps. **Gap 2 is now closed by execution.** Gap 1 (the narrow per-test mutation claim) remains open and unverified. This addendum is appended after workflow completion and is dated separately so the record shows what was research and what was measurement.

## What was run, and what was NOT

**Run:** a read-only characterisation of the 1,032 `vacuous_test_heuristic` findings recorded in `validation-corpus/adjudication-set-13-5.json` (the 2026-08-18 corpus-read run). Each flagged test function was read **from its member's pinned git object** (`git show <pin>:<path>`), parsed, and bucketed by *why* corroboration failed. Script preserved at [`measure-vacuous-population-split.py`](measure-vacuous-population-split.py).

⛔ **NOT run, and deliberately so:** no detector was executed over any corpus member; no adjudication set, finding, verdict, disposition or gate artifact was produced or modified; no member's working tree was read or mutated; nothing under `validation-corpus/` was written; no sealed candidate was touched, fetched or ratified. `DF-13-5-A`'s round is **UNSPENT**. This is a characterisation of findings that already existed, not a new run.

⚠️ **A correction to the research document's own claim.** §11 Gap 2 stated the measurement was available "at zero cost" against the existing advisory population. That was **partly wrong**: the stored findings carry only `rule_id`, `verdict_eligible`, `advisory`, `locators` and the adjudication fields — **no evidence counts**. The split could not be read off the artifact and had to be re-derived from pinned source. The cost was still near-zero and required no operator act, but the original claim was inaccurate as written and is corrected here rather than quietly restated.

## Method

Buckets use the **shipped frozen vocabularies** — `_CORROBORATION_ASSERTION_CALLEES` (23 names) and `_MOCK_CALLEES` (10 names) — imported, never re-typed, so "assertion callee" and "mock callee" mean exactly what the detector means by them.

| Bucket | Definition |
|---|---|
| **A** | no SUT call at all — nothing to corroborate |
| **B** | at least one SUT call discarded, none consumed — **the shape fact (b) can corroborate** |
| **C1-strong** | SUT result reaches an assertion using equality/containment (`assertEqual`, `assertIn`, `assert x == y`, …) |
| **C1-weak** | SUT result reaches an assertion using **only** a unary tolerance check (`assertIsNotNone`, `assertTrue`, `assertIsInstance`, bare `assert x`, …) |
| **C2** | SUT result consumed but never reaching any assertion |

A first version of the classifier was **discarded as flawed**: `ast.walk` on a `FunctionDef` traverses its `decorator_list`, so `@pytest.mark.parametrize(...)` was counted as a consumed SUT call. Python sets `FunctionDef.lineno` to the `def` line, placing decorators outside the detector's definition span, so v2 walks the function **body only**. The flaw inflated bucket C; it is recorded here because the uncorrected figure (98.7% consumed) was measured before the error was caught.

## Result — 1,032 classified, 0 unresolved

| Bucket | Count | Share |
|---|---:|---:|
| C1-strong — result properly constrained | **604** | 58.5% |
| C2 — result consumed, never asserted on | **244** | 23.6% |
| C1-weak — result constrained only by a tolerance check | **170** | 16.5% |
| **B — result discarded → CORROBORABLE** | **6** | **0.6%** |
| A — no SUT call | 8 | 0.8% |

| Derived figure | Value |
|---|---|
| **Invisible-but-suspect** (C1-weak + C2) | **414 (40.1%)** |
| **Corroborable ceiling** (B) | **6 (0.6%)** |
| **Blindness ratio** | **69×** |

Per member: `minions` 648 (C1w 96 / C1s 398 / C2 145 / B 1 / A 8) · `agent-smith` 295 (54 / 155 / 81 / 5 / 0) · `agent-markovich` 72 (19 / 35 / 18 / 0 / 0) · `xagents-webapp` 17 (1 / 16 / 0 / 0 / 0) · `ai-body-runtime` 0.

## What this establishes

1. **The blindness finding is confirmed, and quantified at 69×.** 414 flagged tests are plausibly defective and structurally invisible to fact (b); 6 are even eligible for corroboration.
2. **The corroborable ceiling across the entire five-member ratified corpus is SIX** — against a yield floor of **five**. The 2026-08-18 run promoted **0** of those 6, because fact (b) additionally requires a mock-bound assertion and none of the six carried one.
3. **The heuristic is not noise.** 58.5% of flagged tests do properly constrain the SUT result — correctly flagged by density/mock-ratio, correctly left advisory. The heuristic's advisory tier is doing its job; the promotion predicate is what cannot reach the defects.
4. **The population the round would sample is measured, not assumed.** Three additional repositories of similar composition would be expected to add roughly 3–4 corroborable candidates, of which the historical promotion rate is 0 of 6.

## Bearing on HALT-1

Fixing the predicate to reach C1-weak and C2 would expose **414 candidates from the corpus already on disk** — no ratification, no third-party fetch, no round spent, no operator act. Expanding the bench under the current predicate samples a population measured at **0.6% corroborable**, from which the observed promotion rate is **zero**.

This is direct evidence for the sequencing already implied by `DF-13-5-A`'s own pre-registered rule: **a materially better detector, not a bigger bench.**

## Limitations — stated, not buried

- The classifier is **independent**, approximating the shipped predicate using its vocabularies. It is **not** the shipped predicate, and its bucket boundaries are this report's judgement.
- The weak/strong split depends on which callees count as tolerance checks. `assertRegex` was classed weak; that is arguable.
- **C1-strong does not mean the test is good** — an `assertEqual` against a wrong expected value is still a bad test. It means the test *constrains* the result and is therefore out of scope for a vacuity rule.
- Only the **heuristically flagged** population (1,032) was classified, not all 5,129 scored functions.
- `pytest.raises` is absent from the frozen assertion table, so a `with pytest.raises(...)` call counts as a SUT call — faithful to the shipped predicate, but worth knowing.
- **No claim is made that any of the 414 is a true positive.** That is an adjudication, and adjudication is a human act under protocol §4. This measurement counts shapes, not defects.

---

# CORRECTION — the proposed widening does NOT survive revalidation, 2026-08-22

**Status.** The addendum above proposed widening fact (b) from *"result discarded"* to *"result unobserved"* and estimated the reachable population at **250**. Revalidation against the **shipped predicate** falsifies that estimate. The figure is **6**. This correction is recorded in full rather than the estimate quietly restated, because the estimate was used to argue a sequencing decision.

## How it was revalidated

The addendum's classifier was hand-rolled and approximated the detector's notions. This revalidation instead calls the **shipped** `argus.detectors.provenance_scan.provenance_evidence()` — the exact function `VacuousTestScore.ast_corroborated` calls — over all 1,032 flagged functions, with span edges from a real `build_ast_index` over blobs materialised from each member's pinned object. Script: [`revalidate-fact-b-widening.py`](revalidate-fact-b-widening.py).

**The harness was validated in BOTH directions before its numbers were believed:**

| Direction | Check | Result |
|---|---|---|
| Negative | shipped fact (b) over the real population must reproduce the recorded **0** blocking findings | **0** ✅ |
| Positive | the project's own `_CORROBORATED_FIXTURE` control must still promote through this harness | `disc=2 cons=0 mref=1`, corroborated **True** ✅ |

The positive control is not optional. `mock_referencing_assertions` measured **0 across all 1,032 findings**, which would make the negative check pass trivially if the harness simply could not compute that field. It can; the zero is real.

## Measured, against the shipped predicate

| Clause | Count of 1,032 |
|---|---:|
| no SUT call at all (`disc=0, cons=0`) | 8 |
| at least one **discarded** SUT call | **676** |
| **zero consumed** SUT calls | **14** |
| at least one **mock-referencing assertion** | **0** |
| `sut_result_is_discarded` (`disc≥1 ∧ cons=0`) | **6** |
| full shipped fact (b) | **0** |

## What was wrong, and why

**The addendum's `C2` bucket (244) used a weaker notion of "consumed" than the shipped predicate.** The shipped scan additionally counts as CONSUMED: a call inside a `pytest.raises` / `assertRaises` / `pytest.warns` block (DN-3 — *raising IS the observation*), a call that cannot be located in the source text (*unresolvable is not evidence*), an off-span edge, and any call whose receiver chain is rooted at a mock-bound name is not a SUT call at all. Under those rules the 244 collapses: only **14** findings have zero consumed SUT calls.

**The addendum's `B` bucket (6) happens to be correct** — it agrees with the shipped `sut_result_is_discarded` count exactly.

## What DOES survive, and is newly established

1. **The mock-referencing clause is dead on this corpus — 0 of 1,032.** Not one flagged test carries an assertion referencing a mock-bound name. Removing that clause alone moves promotions from **0 → 6**, which crosses the yield floor of 5. It is a small, precise, measurable change. It is also **thin**: six findings, from five repositories, against a historical adjudication base rate of 0 TP.
2. **The binding constraint is the SCOPE of `consumed == 0`, not the word "discarded".** 676 findings have at least one discarded SUT call; only 14 have zero consumed ones. The clause is evaluated over the **whole test function**, so a single observed call anywhere — including a `pytest.raises` or an unreadable one — withholds corroboration from the entire test. Reaching the suspect population requires making the discarded/observed judgement **per call**, which is a real design change dependent on Story 6.2's dataflow, **not** a cheap predicate edit.
3. **The blindness finding itself is unaffected.** The flagged population is still dominated by tests whose SUT result is consumed, and fact (b) still cannot reach them. What changed is the *cost of the fix*, not the diagnosis.

## Consequence for the sequencing argument

The addendum argued: *fixing the predicate exposes 414 candidates already on disk, versus expanding the bench which samples a 0.6%-corroborable population.* **The first half of that is now withdrawn.** No cheap predicate edit exposes 414, or 250. The defensible restatement:

> Removing the provably-dead mock-referencing clause moves the corroborable population from 0 to 6 at negligible cost and risk. Reaching the ~40% suspect population requires per-call observation analysis, which is Story 6.2 work and is **not** cheap. Neither path is a reason to spend the round *now*, but neither is as cheap as the addendum implied.

**No sprint change proposal was written on the falsified basis.**

## Limitation of this correction

The 6 findings that a de-clausing would promote have **not** been adjudicated, and this correction makes no claim about their truth. The historical base rate over an analogous population is 0 TP / 26 FP. Six promotions is one above the yield floor, which means the resulting precision measurement would rest on a population of six — statistically fragile even if every one were adjudicated true.
