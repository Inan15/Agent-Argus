# APAA — Technical Research (Feasibility & Prior Art)

**Date:** 2026-06-17
**Purpose:** Validate APAA's key technical bets, surface the hard/unproven ones, and recommend a V1 architecture grounded in 2025–2026 prior art.

## Feasibility — Validated

- **Filesystem-as-contract + stateless subagents:** Claude Code subagents are stateless by design (fresh context per call, only final message returns); Skills are themselves filesystem artifacts. Coordinating exclusively through `.apaa/` files matches the documented isolation/return-channel pattern; **resumability falls out of statelessness**.
- **Tools-do-breadth / LLM-does-depth:** SAST has low detection but low FP; LLMs have high detection but high FP. **Ensemble beats either alone** (ITEQS 2026; arXiv 2508.04448).
- **Prompt caching economics:** Anthropic cache reads **0.1× base (90% off)**, writes 1.25×/2×; break-even after 1 hit; real deployments report **59–70% cost reduction**. Multi-perspective passes over one partition are an ideal cache-hit shape.
- **Token-free pre-flight estimation:** `cloc`/`tokei`/`scc`/`radon` emit fast deterministic LOC + complexity (scc even computes COCOMO); local tokenizers (tiktoken, Anthropic SDK) count tokens with **zero inference**. Calibrated LOC→token multipliers are sound.
- **Mutation testing as v2 / "test the auditor":** field-standard ground truth for suite quality; the **defect-cartridge idea is literally mutation testing applied to the auditor** — a known, defensible methodology.
- **Tiered model routing (cheap triage → premium deep-read):** matches production agentic tools (Greptile v3 on the Claude Agent SDK, Cursor, Amp).

## Feasibility — Risks (the hard bets)

- **Reproducibility ("same repo + version ⇒ same verdict") — the HARDEST bet.** 2025 research is unanimous: **temperature 0 is not deterministic** (FP non-associativity, GPU kernel/batch nondeterminism, API load-balancing across hardware). Claude dropped to **~20% identical-output** rate on longer/open-ended prompts. A bit-identical verdict is **not achievable**; only a **STABLE** verdict (via memoization + structured outputs) is realistic.
- **`audited_deep` as a comprehension proxy:** an emitted claim proves output was produced, not that the file was comprehended; LLMs confidently hallucinate. The claim-emission gate raises the bar over file-open but doesn't guarantee understanding.
- **Context budgeting at 40 files / 15k LOC:** even well under the window, **context rot is real** — Chroma's 18-model study (incl. Claude Opus 4) shows ALL models degrade as input grows; "lost in the middle" worsens past ~50% fill. 15k LOC in one agent risks mid-context blind spots → budget may need to be tighter.
- **Seam auditor reading only interfaces:** partitioning loses global dataflow; defects emerging only from cross-partition interaction (and invisible at the declared interface) can be **systematically missed** — the known weakness of divide-and-conquer vs graph-based whole-repo tools.
- **Vacuous-test heuristics (assertion density, mock ratio):** cheap and directionally useful but **weak proxies** — high assertion density can still be vacuous; high mock ratio is legitimate in some suites. Expect real FP/FN until the v2 mutation layer.
- **Cline sequential fallback:** capable (plan/act, model-agnostic) but human-in-the-loop and sequential — lacks Claude Code's parallel subagent isolation, so `.apaa/` coordination must run single-threaded without losing coverage guarantees.

## Prior Art & Tools

| Tool / technique | Relevance |
|---|---|
| Greptile v3 (Claude Agent SDK) / Sourcegraph Amp / Cursor | Production agentic repo-comprehension — multi-hop over a code graph, git-history tracing. Prior art for APAA's deep-read agent; **graph/structural context beats naive RAG at scale**. |
| ast-grep / Probe / tree-sitter | Syntactic (not string) search; Anthropic replaced Claude Code's vector DB with grep+structural search in 2025. APAA's breadth layer should use **AST/structural search, not embeddings**. |
| AST-derived code graphs / Graph-RAG (RANGER, LogicLens) | AST graphs more reliable than LLM-extracted KGs for codebase QA — the principled way to define partitions + identify true cross-partition seams. |
| Mutation frameworks (PITest/mutmut/cosmic-ray) | Field-standard "test the tests"; surviving mutants reveal missing assertions — basis for v2 vacuous-test detection AND defect-cartridge CI self-validation. |
| scc / tokei / cloc / radon + tiktoken / Anthropic token-count SDK | Deterministic LOC, complexity, COCOMO, local token counts — substrate for the token-free pre-flight estimator + partition sizing. |
| Anthropic prompt caching + content-addressed memoization | 0.1× cache reads make multi-perspective passes cheap; `hash(inputs+agent-version+model+params)` memoization is the only credible path to cross-run determinism — caching does **double duty (cost AND reproducibility)**. |

## Context-Scale Findings (500k LOC reality)

- Every frontier model degrades monotonically as input grows — **context rot is architectural** (RoPE long-term decay), not a training gap newer models fix.
- "Lost in the middle" (Liu et al., Stanford/TACL): 30%+ accuracy drops on mid-context info; U-shaped favoring of start+end holds below ~50% fill, then recency dominates — even a half-full window has reliability cliffs.
- A 500k+ LOC repo cannot be reasoned over in any single context — **partition-and-budget is mandatory**, the same conclusion production tools reached (index + retrieve + multi-hop).
- Divide-and-conquer multi-agent (arXiv 2505.20625) is the validated scaling pattern but shifts the failure mode to **cross-partition information loss** — exactly what the seam auditor must cover and the hardest part to make complete.
- For coding agents, context rot is cited as the **primary failure mode** — per-agent budgets should be conservative, inputs ordered with highest-risk files at the edges.

## Cost & Determinism

- Prompt caching: reads 0.1×, writes 1.25×/2×, break-even at 1 hit; multi-perspective passes over a fixed partition are near-ideal (partition = cached prefix, perspective = cheap delta). Documented 59–70% savings.
- Tiered routing + diff-scoped (BASE...HEAD) incremental audits compound the savings.
- Determinism is the binding constraint — **"same version ⇒ same verdict" bit-for-bit is infeasible**; content-addressed memoization converts reproducibility from "pray the LLM repeats" into "cache hit returns the recorded result."
- Token-counting for estimation is free + deterministic → the **pre-flight estimate is exact-by-construction**; variance lives entirely in actual generation.
- ⚠️ Cache correctness caveat: **pin model checkpoint/version into the cache key** (Anthropic rotates silently) or stale verdicts leak across model updates — treat a model rotation as a cache-busting re-audit event.

## Technical Recommendations for V1

1. **Make reproducibility honest and achievable.** Do NOT promise bit-identical verdicts. Promise (a) a deterministic coverage-ledger + pure-function verdict given recorded findings, and (b) **stable** verdicts via content-addressed memoization (cache the findings; re-runs at the same key return the recorded result). Make model-checkpoint part of the cache key; a model rotation = re-audit event.
2. **Harden `audited_deep`.** Require the emitted claim to be **structured and grounded** — cite specific symbols/line ranges validated against the AST, not free-text. An unverifiable claim downgrades the file to `audited_shallow`. Turns the comprehension proxy into something falsifiable.
3. **Build an AST/code-graph index FIRST;** drive partitioning + seam discovery from it (tree-sitter/ast-grep), not directory layout — the graph defines true cross-partition edges so the seam auditor reads the actual interaction surface. Use grep/structural search, not embeddings.
4. **Set per-agent budgets conservatively** (treat 15k LOC as an upper bound), order inputs with highest-risk files at the context edges, and record a `context_pressure` signal so over-budget partitions auto-downgrade from `audited_deep`.
5. **Ship the defect-cartridge CI self-test as a Day-1 gate** — the only empirical defense of the coverage claims; doubles as calibration source for vacuous-test heuristics + LOC→token multipliers. A cartridge miss = release blocker.
6. **Ship vacuous-test detection as explicitly-labeled v1 heuristics that FLAG (not assert);** design the ledger so the v2 mutation layer can supersede the flags without a schema change. Lean on SAST/linters for breadth; reserve premium deep-reads for files the cheap triage + tools flag; diff-scope incremental runs.
