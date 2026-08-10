# Sprint Change Proposal — 2026-08-10b

**Project:** ArgusAgent (formerly APAA — AI Project Assurance Audit)
**Author:** Correct Course workflow (`bmad-correct-course`), incremental mode
**Requested by:** XAgent007
**Trigger type:** Strategic pivot (second — supersedes the unsigned proposal of the same date)
**Change scope classification:** **MAJOR** — fundamental replan (PM / Architect involvement)
**Status:** **APPROVED by XAgent007, 2026-08-10 — all 16 edits APPLIED to all four artifacts**

> **Supersedes [sprint-change-proposal-2026-08-10.md](sprint-change-proposal-2026-08-10.md).**
> That proposal was **never signed** — its §6 approval box is still ⬜ and only its
> `sprint-status.yaml` edit ever landed. Verified on this tree: `FR34` has **0 occurrences** in
> `prd.md` and `addendum.md` (the highest FR is FR33); the PRD frontmatter `amendments` block's
> last entry is **2026-08-03**; Epic 11 is **absent from `epics.md`**. Its text is retained
> unedited (§3.4 evidence immutability) and is not rewritten by this document.

---

## 1. Issue Summary

### 1.1 What triggered this

Not a story. An **operator strategic pivot**, raised 2026-08-10 while reviewing the prior
proposal, rejecting the shape that proposal recommended:

> *"No provisional demos, only utility which helps end users and students."*

The 2026-08-10 proposal solved *"how do we ship pre-gate without lying"* by adding a **permanent**
disclosure (FR34) and a 7-story disclosed release. The operator's requirement is a **complete 1.0
that earns the removal of the disclaimer** and delivers real utility on first run.

A second operator correction, applied throughout this document:

> **"Student" is a context, not a skill level.**
> Students are developers. What the tertiary persona lacks is not ability — it is **institutional
> support**: no procurement, no compliance mandate, no internal champion, no colleague who already
> knows the tool. Design for **unassisted first-run utility because there is no one to ask**, not
> because the user is inexperienced.

### 1.2 Problem statement

Epics 10 and 11 as planned address **honesty** and address it well. They do not address
**usefulness**, and the gap is not a missing feature — it is a **delivery gap on capabilities that
already exist in the tree**:

1. **The deep-audit seam is built and unwired.** `DeepAuditSeam` (`argus/audit/deep_audit.py:91`)
   is referenced only from `argus/audit/*` and `argus/dogfood/proof_run.py` — **never from
   `argus/pipeline.py`**.
2. **The memoization store is built and unwired.** `argus/cache/memo_store.py` exists;
   `argus/pipeline.py` never imports it. FR27 and NFR-D1 are therefore specified but undelivered.
3. **The README promises an integration that does not ship.** `README.md:138-150` claims
   *"ArgusAgent registers slash commands in your AI coding assistant (Claude Code, Cursor,
   Cline, etc.)"* and lists seven. `pyproject.toml:59-62` ships **three console aliases** all
   pointing at `argus.cli:main`. There is **no MCP server, no packaged skill, and no registration
   mechanism** anywhere in the tree. The real CLI is one `audit` subcommand plus 13 flags.
4. **Terminal outcomes are dead ends.** `INSUFFICIENT_COVERAGE` — the outcome a public user is
   most likely to receive — states what was not assessed and names no next action.

### 1.3 Evidence

All figures measured in place on this tree at HEAD `00c8d1b`, not inferred.

| Fact | Evidence |
|---|---|
| Deep-audit seam orphaned | `DeepAuditSeam` at `argus/audit/deep_audit.py:91`; grep for `deep_audit`/`llm_adapter` in `argus/pipeline.py` returns **zero hits** |
| Memoization orphaned | `argus/cache/memo_store.py` present; no import from `argus/pipeline.py` |
| Agent integration absent | No MCP server in tree; `pyproject.toml:59-62` = 3 console scripts → `argus.cli:main`; no packaged command assets |
| README CLI example is broken | `argus --budget 500 --materiality critical` omits the `audit` subcommand and the required `repo` positional |
| README install path is false | *"INTERIM — resolve straight from this repository at a tag"*; `git tag -l` is **empty** |
| Precision gate not cleared | `protocol_cleared: bool = False` at `argus/precision/replay_harness.py:223`; never passed `True` at any call site |
| Corpus is N=1 and self-referential | Story 8.5 re-derived the dogfood as a self-audit of `argus/`; the independent Minions run *"can never be re-derived in this repository"* and the ledger calls the replacement *"a materially weaker evidence class … not independent corroboration of anything"* |
| NFR-M1 breached | `argus/pipeline.py` = **1331 lines** against a cap of **1200** |
| Default install is Python-only | The 9 non-Python grammars sit in the optional `[languages]` extra |
| Privacy posture clean | Egress confined to `argus/audit/open_llm_adapter.py` behind the opt-in `[llm]` extra; committed import gates; no telemetry; MIT |

### 1.4 Three defects found during this analysis

**(a) The multi-language site enumeration has been wrong twice.**
Story 10.2's AC1 originally named **4** sites. The 2026-08-10 proposal "corrected" it to **7** and
was **itself incomplete**, omitting PRD **L174**, **L317** and **L375**. Measured list is **10**:
PRD L23, L116, L174, L180, L317, L375, L398 (FR7), L476 (NFR-P2) + architecture L220, L237.

**(b) The validation set is defined twice, incompatibly.**

| Source | Definition |
|---|---|
| PRD L161 | *"N ≈ 5–10 **real** XAgents repos"* |
| PRD L156 | findings *"judged genuinely real by an **independent senior engineer**"* |
| `precision-validation-protocol.md` §5 | *"N ≥ 5 labeled planted-defect **cartridges**"*, `VALIDATION_SET_FLOOR_N = 5` |

These measure different quantities. **Cartridges measure recall** against known plants — that is
FR20, already delivered and CI-asserted. **Precision measures how often a 🔴 on unplanted code is
real.** Only the second gates externalization.

Architecture L152-154 called the validation-set input *"the one open input that gates an
ARCHITECTURE choice"* and it is **still marked OPEN at L328** — it was closed by **implementation**
(Story 6.6's protocol) rather than by **decision**, and the PRD was never reconciled.

**(c) A V1 Core commitment was never delivered and never recorded as deferred.**
PRD §Product Scope **L168** commits `standards_refs[]` + CWE-required-on-security-findings to
**V1 Core**, *"day-one additive."* Measured: **zero occurrences** of
`standards_ref` / `cwe` / `asvs` / `owasp` anywhere in `argus/**/*.py`; `FindingDraft`
(`argus/detectors/base.py:63-87`) carries no standards field of any kind.

**Root cause — the two sections disagree.** §Product Scope commits it; **the binding FR contract
never lists it** (no FR1–33 mentions standards mapping). L384 states *"a capability not listed
here will not exist in V1 unless explicitly added"* — so by the **binding** contract its absence is
correct, and by §Product Scope it is a missed V1 commitment. No story ever built it because no
story reads §Product Scope for capabilities.

This is the **exact inverse of (a)/DF-AUD-APAA-D**: that is a capability shipping without a spec;
this is a spec with no capability. **Same root cause** — a claim living in a section no story reads.
Not release-blocking for the tertiary audience; material for **Journey 4 (regulated enterprise)**,
where a security finding without a CWE reference is weaker compliance evidence.

### 1.5 V2 roadmap sweep — what else leaked into V1

Prompted by the operator asking what other previously-implemented V2 work was unaccounted for.
Every §Product Scope V2 Growth Feature (L180) was swept against `argus/**`:

| V2 feature | In `argus/`? |
|---|---|
| **Multi-language AST grounding** | ✅ **SHIPPED** — 10 grammars. Owned by Story 10.2 |
| Seam / interface auditor | ❌ Not shipped, and **honestly marked** |
| Mutation-grade vacuous detection | ❌ Absent |
| Multi-perspective adversarial panel | ❌ Absent |
| Host-capability manifest / `adapter_portability` | ❌ Absent |
| Holdout-cartridge rotation | ❌ Not in `argus/` (cartridge fixtures in `tests/` are the V1 §H design) |
| Production-Readiness-Review checklist | ❌ Absent |
| Consume Minions Cost-Optimization layer (d) | ❌ Absent |
| Bidirectional traceability | Partial — the shipped half is **V1** (FR12, FR14) |

**Result: multi-language is the only V2 capability that leaked, and Story 10.2 already owns it.**

Two V1 invariants **verified holding**, not assumed:

- **Seam analysis is deferred honestly.** `argus/index/partitioner.py:233-238` records
  `seam_analysis="v2-deferred"` as a fixed marker and the cut-edge set as *"recorded, NOT
  analyzed."*
- **The `partition_id` V1 invariant holds.** PRD L175 requires always `"root"` in the coverage
  ledger. `_DEFAULT_PARTITION_ID = "root"` at `coverage_ledger.py:57` and `recording.py:53`;
  `pipeline.py:910` and `:1189` pass it explicitly. The per-unit sha256 ids in
  `dogfood/partition_plan.py` belong to the **work manifest**, a different contract, correctly
  separated.

---

## 2. Impact Analysis

### 2.1 Epic impact

| Epic | Status | Impact |
|---|---|---|
| **Epics 1–7** | done | **None** — signed retrospectives, not reopened (§3.4) |
| **Epic 8** | done | **None** |
| **Epic 9** | done | **None** |
| **Epic 10** | backlog, 0/4 | **Not redefined; extended to 5.** All four stories survive and all four are release-relevant. Story 10.2's AC1 corrected to the measured 10-site list. **New Story 10.5** adjudicates the §1.4(c) `standards_refs` conflict — same epic because it is the same defect class |
| **Epic 11** | backlog (registered in tracker only) | **Redefined** — 7 stories → 5, narrowed to *Release Integrity* |
| **Epic 12** | *new* | **9 stories** — The Useful Tool, ending in the publish |
| **Epic 13** | *new* | **3 stories** — Earn the Gate |
| **Minions Handoff H1–H4** | not epics | **None. H0 remains UNOWNED** |

**Total: 22 stories to a published 1.0 with the gate cleared** — 4 already planned, 18 new.

### 2.2 Story impact

**Epic 11 renumbering** (recorded so the superseded tracker entries stay traceable):

| Superseded | Now | Change |
|---|---|---|
| 11.1 | **11.1** | Scope changed — gains the expiry clause |
| 11.2 | **absorbed into 12.2** | Measured as a precondition of the work rather than as a standalone spike |
| 11.3 | **11.2** | Unchanged |
| 11.4 | **11.3** | Unchanged |
| 11.5 | **11.4** | Unchanged |
| 11.6 | **11.5** | Gains the README slash-command falsehood |
| 11.7 | **12.9** | **Moved** — publishing at the end of Epic 11 would ship a safe tool nobody wants |

### 2.3 Artifact conflicts

| Artifact | Amendments | Sites |
|---|---|---|
| **PRD** | 7 edits | L118/L130/L141/L302/L351 · L107/L132-137 · L122 · L317/L340 · after L236 + summary · FR34–37 · after L178 + NFR-S6 + NFR-P3 |
| **Architecture** | 4 edits | L148-151 · L306-309 + L312 + L328 · L223-230 + L487 + L403 · after L250 + L271-274 + §E |
| **epics.md** | 4 edits | Story 10.2 AC1 · **Story 10.5 (new)** · Epic 11 (replace) · Epics 12 and 13 (new) |
| **sprint-status.yaml** | 1 edit | Header DELTA NOTE + `development_status` L255-263 replaced |
| **UI/UX** | **N/A** | No artifact; headless classification **retained** |

### 2.4 Technical impact

| Area | Impact | Story |
|---|---|---|
| `argus/pipeline.py` | **1331/1200 — extraction becomes a GATE, not an enabler** | 12.1 |
| `argus/pipeline.py`, `argus/audit/**` | Deep-audit seam wired, opt-in | 12.2 |
| `argus/pipeline.py`, `argus/cache/**` | Memoization wired (delivers FR27/NFR-D1) | 12.3 |
| `argus/reports/**`, `argus/cli.py` | FR34 disclosure · FR37 actionable output | 11.1, 12.4 |
| `argus/mcp/**` *(new)*, `argus/assets/commands/**` *(new)* | FR35 agent-integration surface | 12.6, 12.7 |
| `argus/detectors/vacuous_test.py:198` | Word-separator fix + near-miss corpus | 11.2 |
| `action.yml:74,78,79,80,126` | **Five** `${{ inputs.* }}` sites → `env:` binding | 11.3 |
| `argus/index/ast_index.py` | Runtime `tree-sitter` assertion · grammar diagnosis | 11.4, 10.4 |
| `argus/precision/replay_harness.py:87-90, :223` | Lazy `_registry` import · `protocol_cleared` | 11.5, 13.3 |
| `pyproject.toml` | Grammar defaults · MCP entry point | 12.5, 12.6 |
| `.github/workflows/release.yml` | Index publish extension | 12.9 |
| `README.md`, `CHANGELOG.md`, `docs/` | Truth repairs · first-run surface | 11.5, 12.7, 12.8 |

### 2.5 Status change from the superseded proposal

**`argus/pipeline.py`'s NFR-M1 breach now has an owner.** The 2026-08-10 note recorded 1331/1200
and recommended the extraction *"as an ENABLER, not a gate."* That was correct while nothing was
landing in the file. **Stories 12.2 and 12.3 both land in it**, so it becomes **Story 12.1, first
in Epic 12** — including the repo-wide sweep test (~10 lines) that would have caught 131 lines of
silent drift. NFR-M1 is enforced per-module and ad hoc (`tests/test_cache_invalidation.py:690`,
`tests/test_cartridge_selfaudit.py:472`) with **no assertion covering `pipeline.py`**. Closes or
re-scopes DF-8-2-A, DF-8-3-A, DF-8-3-C, which all gate on the extraction.

### 2.6 Latent architecture gap that becomes live

Architecture §E (L277-278) justified **not** building fallback, circuit-breaking and cost
attribution on the grounds they came *"for free"* from the Minions orchestrator. **Story 9.1
removed that orchestrator** and nothing re-derived the reasoning. Costless today because the deep
path is unwired; **a live gap the moment Story 12.2 wires it**, and it would present as flaky
audits rather than as an obvious defect. Story 12.2's NFR-R1 acceptance criteria now supply it.

---

## 3. Recommended Approach

### 3.1 Options evaluated

| Option | Effort | Risk | Verdict |
|---|---|---|---|
| **1 — Direct Adjustment** | High | Med | **Viable but insufficient** — carries the code work; cannot amend a PRD capability contract or admit a new product surface |
| **2 — Rollback** | — | — | **Not viable** — nothing to roll back; Epics 1–9 done with signed retros; §3.4 forbids rewriting |
| **3 — PRD MVP Review** | Med | Med | **Required** — audience, distribution, capability contract and the externalization precondition all change |

### 3.2 Selected: **Hybrid — Option 3 → Option 1**

Amend the contract first, then carry the work. Same shape as 2026-08-03 and 2026-08-10.

### 3.3 The keystone decision: deferred under conditions, not waived

The gate is **not waived** and **not permanently split**:

- **Attested externalization** — any use in which a verdict is presented as assurance evidence
  (commercial, enterprise, regulated, operated-service). **Absolute. Status: NOT CLEARED.**
- **Free public release** — permitted ahead of the gate **only** under FR34's **two** binding
  conditions: (a) the tool's unvalidated status is **mechanically disclosed** on every user-facing
  verdict surface, **and** (b) a **committed programme to clear the gate** is in flight.

Condition (b) is the difference from the superseded proposal, and it is the whole substance of the
operator's instruction. **Epic 13 is that programme.** If it is abandoned, the free public tier is
**withdrawn** rather than the disclosure.

**Stated plainly: this is still a loosening of the PRD's most-elevated constraint.** The original
wording — *"before any externalization conversation"* — admits no exception. The counterweights
are FR34's mechanical enforcement, Story 11.4's guard on the false-green direction specifically,
and Epic 13's committed schedule with a symmetric fail branch.

### 3.4 Scope decisions

| Decision | Value | Rationale |
|---|---|---|
| **Deep audit default** | **OFF, opt-in `--deep`** | Default-on would trade away the free default, the clean privacy posture (NFR-S6) and NFR-D1 determinism simultaneously, and would fail on first run for any user without a key |
| **Release sequencing** | **Staged** | Publish at the end of Epic 12; Epic 13's corpus builds in parallel |
| **Agent integration** | **Both** — MCP server + command assets | MCP is the tool-calling path; command assets are what the README already promises |
| **MCP transport** | **stdio only** | Preserves the headless classification, ADR #20, and the `argus.* ⊬ fastapi` gate by construction rather than by discipline |
| **Channels** | Public index + GitHub Marketplace | Unchanged from 2026-08-10. Desktop stores, OS package managers deferred **with reasons**; hosted runner remains V4; `store_compliance` skip **re-validated and remains correct** |

### 3.5 Timeline and risk

**22 stories**, of which 4 are already planned. **Epic 13 gates on human review time, not
engineering throughput** — the protocol budgets ≤4 expert-hours for a full adjudication run at
N≥5, but the corpus must be built first.

**Principal risks:**

1. **The adjudicator is still unnamed.** DF-7-2-A has been open and unowned since Epic 7 and was
   restated as unowned by Story 9.2 and by the superseded proposal. **Epic 13 cannot start
   without a named human**, and this is written as a start condition, not a note.
2. **Story 12.2 may measure that a verdict-blocking finding is not reachable on a default run.**
   A measured "no" is reported and escalated — never a licence to loosen a gate or soften
   Journey 6. It is scheduled early precisely so this surfaces before listing copy is written.
3. **Story 13.1 may be resolved the cheap way.** Adopting the cartridge reading would clear the
   externalization gate on synthetic corpora Argus's own team authored — repeating the
   self-referential-evidence problem that already cost the Minions run. This is why 13.1 is a
   **decision story with a recommendation of record**, not an implementation detail.

**Compression available:** dropping the marketplace channel removes Story 11.3's precondition role
and de-scopes 12.9; shipping MCP-only removes Story 12.7. Minimum viable path is **20 stories**.

---

## 4. Detailed Change Proposals

All 16 were reviewed incrementally and **approved by XAgent007 on 2026-08-10**.

### 4.1 PRD (7 edits)

| # | Section | Change |
|---|---|---|
| **1** | L118, L130, L141, L302, L351 | The ≥80% gate becomes **absolute for attested use, deferred under two conditions** for a free release. Status recorded factually as **NOT CLEARED**. **Five sites, because the superseded proposal edited two of five** |
| **2** | L107, L132-137 | **Independent-developer** persona (context, not skill level), scoped to the unattested tier + the *"usage is not evidence"* guard. Four tertiary success criteria: **no dead ends · reachable from the agent · works on their stack · free and private by default** |
| **3** | L122 §Project Classification | **Admits the local agent-integration surface**, which L122 currently forbids. Four binding constraints: stdio only · no HTTP stack · no new authority · no credential handling. **Hosted runner + HTTP API remain V4** |
| **4** | L317, L340 | V1.5 channel table with **excluded channels and their reasons**; `store_compliance` skip **re-validated**, reopening condition pre-committed |
| **5** | after L236 + summary | **Journey 6 — Sam, independent developer.** Resolves **usefully** without claiming the gate is cleared. Carries an explicit measured-dependency warning owned by Story 12.2. Three rows added to the Journey Requirements Summary |
| **6** | §Functional Requirements | **FR34** (self-disclosure, temporary, mechanically enforced) · **FR35** (agent integration) · **FR36** (opt-in deep audit) · **FR37** (actionable output). Full text below |
| **7** | after L178 + NFRs | **§V1.5 — The Public Release** (adds no assurance capability) · **NFR-S6** (default path transmits nothing) · **NFR-P3** (default install grounds what it claims) |

**FR34** — APAA can disclose its own validation status on **every** user-facing verdict surface,
and cannot emit a verdict on a surface that omits it. Surface set **enumerated in a committed test
that fails on an unenumerated member**. Distinct from FR17: FR17 bounds *this audit's* scope,
FR34 bounds *the instrument's* credibility. **Removable only on measurement**, and **replaced
rather than deleted** when the gate clears. **Not a permanent state** — coupled to Epic 13; if the
programme is abandoned, the free tier is withdrawn rather than the disclosure.

**FR35** — A coding agent can invoke an audit and consume the verdict through a **local
agent-integration surface**: an **MCP server (stdio)** and **packaged command assets**. Bounded by
the §Project Classification constraints. **No new authority** — same pure
`AuditRequest → AuditVerdict` path, same NFR-S4 permission boundary. **Verdict parity** pinned by
test.

**FR36** — An operator can enable an **LLM-backed deep-audit pass**. **[Tier B]** **Off by
default, always** — the default run is zero-token, offline, key-free, transmits nothing. **Egress
disclosed before the first byte.** Spend flows through the **existing** FR21/FR22 ceiling.
Determinism preserved via FR27/NFR-D1. Degradation is honest (NFR-R1) — never a false deep claim,
never a crash.

**FR37** — APAA can state, on every terminal outcome, **why it was reached and the next action that
changes it**. Enumerated over the full verdict vocabulary, **test fails on an unenumerated
outcome**. `INSUFFICIENT_COVERAGE` names the specific unmet gate with measured figures.
**Self-contained** in the tool's own output. **Does not soften a verdict** — governs explanation,
never classification; FR16's decision table is untouched.

### 4.2 Architecture (4 edits)

| # | Section | Change |
|---|---|---|
| **8** | L148-151 | **Grade flag trigger corrected.** It read *"if FR7 is cut"* — **FR7 was not cut** (Story 6.2 delivered its validator) yet the flag is live. Separates **run grade** (per run, removed by engaging `--deep`) from **instrument status** (per version, removed only by Epic 13). Merging them would mislabel deep runs and make the disclosure look user-switchable |
| **9** | L306-309, L312, L328 | §I Packaging: stale `minions[apaa]` **struck** with a pointer to H1; measured shipped package recorded; **`tree-sitter <0.26` promoted to the architecture as load-bearing**; V1.5 channels; verified privacy posture. Driver namespace FR1–33 → **FR1–37**. §Still OPEN records **how** the validation-set input closed — by implementation, not by decision |
| **10** | L223-230, L487, L403 | **Second entry point.** Both surfaces construct the same `AuditRequest` and consume the same `AuditVerdict`; MCP is an **adapter layer**, dependency arrow inward only. Five testable constraints. Command assets are **data, not code** |
| **11** | after L250, L271-274, §E | Memoization recorded as **specified-but-unwired** with the **10.2-before-12.3 wiring order** and its rationale. §E's `minions_llm_adapter` / `LLMProviderOrchestrator` path **struck** — superseded by Story 9.1; live path is `open_llm_adapter.py::OpenLLMAdapter`. **The inherited-resilience rationale no longer holds** (§2.6). Deep audit **off by default** |

### 4.3 Epics (3 edits)

| # | Change |
|---|---|
| **12** | **Story 10.2 AC1 → the measured 10-site list**, plus a closing test that greps for the unamended claim shape (hand-counting has been wrong twice) |
| **13** | **Epic 11 redefined** — *Release Integrity*, 5 stories. No story in this epic publishes anything |
| **14** | **Epics 12 and 13 added** — 9 and 3 stories |
| **16** | **Story 10.5 added to Epic 10** — adjudicates the §1.4(c) `standards_refs`/CWE conflict |

**Story 10.5 — A V1 commitment is delivered, or it is explicitly not V1.**
**Given** §Product Scope L168 commits `standards_refs[]` + CWE-on-security-findings to V1 Core
while **no FR lists it** and **zero occurrences** exist in `argus/**`
**Then** it is **decided** — an FR is added and the field ships, **or** §Product Scope is amended to
V2, dated and reasoned. **Leaving the two sections in disagreement is not an acceptable outcome.**
**And** the consequence for **Journey 4** is recorded either way — a security finding with no
standards reference is weaker compliance evidence, and that should be a known trade.
**And** a **sweep confirms whether any other §Product Scope V1 Core item is missing from FR1–37**,
each result recorded — one instance found by accident implies the class was never checked.

*Recommendation of record: decide it **V2**. Adding a standards field now expands the frozen
`finding` schema and the redaction surface for an audience not asking for it. The **sweep** AC
stands regardless of which way the decision goes.*

**Epic 11 — Release Integrity (5).** 11.1 disclosure with an expiry · 11.2 polyglot classification
· 11.3 action input interpolation · 11.4 grammar false-green guard · 11.5 artifact completeness +
README truth.

**Epic 12 — The Useful Tool (9).** 12.1 pipeline extraction + repo-wide NFR-M1 sweep *(enabler,
first)* · 12.2 deep audit wired opt-in *(carries the absorbed measurement)* · 12.3 memoization
wired *(depends on 10.2)* · 12.4 actionable output · 12.5 polyglot by default · 12.6 MCP server ·
12.7 command assets · 12.8 the tool explains itself · **12.9 publish + cite the gate (last)**.

**Epic 13 — Earn the Gate (3).** 13.1 decide the validation set and build it · 13.2 adjudicate,
**by a named human** · 13.3 record the result and let it decide.

### 4.4 sprint-status.yaml (1 edit)

**Edit 15** — header DELTA NOTE (2026-08-10b) superseding but not rewriting the 2026-08-10 note,
plus `development_status` entries for Epics 11 (replaced), 12 and 13. The note restates **H0**,
**DF-7-2-A** and the **uncleared gate** as open, and records both defects from §1.4.

---

## 5. Implementation Handoff

### 5.1 Scope classification: **MAJOR**

Amends the PRD's classification, personas, journeys, success criteria, distribution phasing and
capability contract; admits a new product surface. Routes to **Product Manager / Solution
Architect**, not to a Developer agent.

### 5.2 Recipients

| Role | Deliverable |
|---|---|
| **Product Manager** | Apply PRD edits **1–7**; add the 2026-08-10b entry to the PRD frontmatter `amendments` block |
| **Solution Architect** | Apply architecture edits **8–11** |
| **Product Owner / SM** | Apply epics edits **12–14**; apply the `sprint-status.yaml` edit **15** |
| **Developer agents** | Execute Epic 10 → 11 → 12 → 13 via the normal SM → Dev → Review cycle. **No Epic 12 story starts before Epics 10 and 11 complete** |
| **Named human (UNASSIGNED)** | **DF-7-2-A adjudication.** Now scoped as Epic 13 — **but the adjudicator is still unnamed, and Story 13.2 does not start until they are named in `sprint-status.yaml`** |
| **Named human (UNASSIGNED)** | **H0** — filing the Minions handoff H1–H4. **Still UNOWNED** |

### 5.3 Success criteria

1. All 11 PRD/architecture edits applied, dated, and attributed to this proposal.
2. Epic 11 redefined; Epics 12 and 13 registered; Epic 10 unchanged except the 10.2 AC correction
   and the added Story 10.5.
2b. **Story 10.5's `standards_refs` decision is made explicitly and dated**, and its §Product-Scope
   sweep is run — not left as the one instance that happened to be noticed.
3. **FR34 enforced by a committed test before any publish step runs.**
4. Story 12.2's reachability measurement recorded as a yes or a no — **a "no" escalates, it does
   not soften Journey 6.**
5. Story 13.1's corpus decision made **explicitly and dated** — not resolved by implementation.
6. Release status cites an executed CI run id on the released commit, or is recorded **NOT
   ESTABLISHED**.
7. The marketplace channel does not ship before Story 11.3 lands.
8. **Epic 13 completes with the gate either cleared on evidence or recorded NOT CLEARED with the
   disclosure retained.** A failed measurement is not a reason to amend the threshold.

### 5.4 Explicitly out of scope

Desktop application stores · OS package managers · hosted runner · HTTP API · clearing the attested
gate by any means other than measurement · reopening Epics 1–9 · the repository-wide
`minions_core/apaa/` → `argus/` rename of the architecture package tree (recorded at §Package tree,
scoped out) · filing the Minions handoff (H0).

---

## 6. Approval

| Item | Value |
|---|---|
| **Proposal date** | 2026-08-10 |
| **Supersedes** | `sprint-change-proposal-2026-08-10.md` (unsigned) |
| **Edits reviewed** | 16 of 16, incremental mode |
| **Edits approved** | 16 of 16 |
| **Change scope** | MAJOR |
| **Operator approval of the complete proposal** | ✅ **APPROVED — XAgent007, 2026-08-10** |
| **Application status** | ✅ **APPLIED 2026-08-10** — PRD (22 substitutions incl. frontmatter `amendments`), architecture (10), epics.md (3 + Epic 11/12/13 insertion), sprint-status.yaml (header note + Epics 10/11/12/13). YAML re-parsed clean; 22 stories across 4 epics verified on disk. **This proposal did not stop at handoff — the failure that killed 2026-08-10.** |

**Approving this proposal authorises:** deferring the ≥80% externalization gate for a free public
release under two binding conditions; adding a third product audience; admitting a local
agent-integration surface; recording public distribution as V1.5; extending Epic 10 by one story;
and opening three epics (11 redefined, 12 and 13 new) — **18 new stories in total**.

**It does not authorise:** presenting any ArgusAgent verdict as assurance evidence; describing the
≥80% precision gate as cleared; or removing the FR34 disclosure by any route other than Epic 13's
measurement. **That gate remains NOT CLEARED, and this proposal does not clear it.**
