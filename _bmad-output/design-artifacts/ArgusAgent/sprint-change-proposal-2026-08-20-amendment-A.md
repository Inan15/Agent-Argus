# Sprint Change Proposal — 2026-08-20 · Amendment A

**Amends:** `sprint-change-proposal-2026-08-20.md` — ✅ **APPROVED by XAgent007, 2026-08-20**
(`7f54506` authored it, `0a6e121` recorded approval as a separate act). Epic 16 is **in flight**:
story 16.1 is drafted and `argus/precision/gate_decision.py` carries uncommitted work. **This
document does not edit one byte of the parent and does not touch anything Epic 16 is holding.**
**Project:** ArgusAgent
**Author:** Drafted at operator request following a three-round adversarial review of the product
thesis, 2026-08-20
**Requested by:** XAgent007
**Trigger type:** Scope discovery. The parent proposal is **correct within its frame** and this
document does not contest it. What the review established is that the frame is narrower than the
product objective, and that **four already-built capabilities are stranded behind a blocker that
has since been removed**.
**Change scope classification:** **MAJOR** — two epics created, one pre-condition gate imposed on an
unscheduled direction, one post-V1 NFR proposed for activation
**Status:** ⏳ **AWAITING OPERATOR APPROVAL.** The parent's approval does not extend to this document.

> **Nothing under `argus/` or `tests/` was modified to produce this document.** Every figure below is
> re-verified at HEAD `0a6e121` or read from committed artifacts. The reproduction in the appendix was
> executed at `ef41449`; the two commits since are **docs-and-registry only** (`git show --stat`
> confirms nothing under `argus/` changed), so the result stands for the committed detector surface.
> The audited repo's `.argus/` output was removed and its `git status` returned to baseline. **This
> document measures nothing new about the validation corpus, spends no bench round, and clears
> nothing.**

---

## 0. What this document is for, in one paragraph

The parent proposal creates Epic 16 to harden the ≥80% precision gate and then spend the one
permitted bench round on the `vacuous_test_ast` class. That is the right next move and **this
amendment leaves it entirely intact**. What this document adds is the surrounding scope the parent
could not have known it was missing: that **FR23 / FR24 / FR26 / FR29 are built, tested and merely
unwired**, and that the structural blocker which stranded them — `pipeline.py` at 1,331 lines against
NFR-M1's 1,200 — **was removed by Story 12.1 and now measures 1,111**. It further imposes an explicit
evidence-and-economics gate in front of the capability-model direction (FR38+), so that a large
architectural pivot cannot begin before the detector lifecycle has been demonstrated end to end even
once.

---

## 1. What the review established, with its evidence

### 1.1 The requirement set is 30:3

Of **FR1–FR37**, four (FR23 / FR24 / FR26 / FR29) carry 2026-08-11 amendments, leaving **33 live
requirements**. Classified by subject:

| Group | Requirements | n |
|---|---|---|
| Intake & scoping | FR1 · FR2 · FR3 · FR4 | 4 |
| Coverage ledger & depth | FR5–FR9 · FR36 | 6 |
| Verdict & disclosure | FR15–FR18 · FR33 · FR34 · FR37 | 7 |
| State & reproducibility | FR25 · FR27 · FR28 · FR31 · FR32 | 5 |
| Finding integrity | FR13 · FR14 | 2 |
| Self-validation | FR19 · FR20 | 2 |
| Cost governance | FR21 · FR22 | 2 |
| Invocation surfaces | FR30 · FR35 | 2 |
| **Defect detection** | **FR10 · FR11 · FR12** | **3** |

**Exactly three requirements describe a defect the tool looks for**: vacuous tests, hardcoded
secrets, orphan code — and FR12 is Tier B. The 30 is a classification and two rows are arguable; the
3 is not. This follows correctly from the founding brief (*"an outsider cold-reading an unknown repo
where coverage honesty is the central problem"*) and is not a delivery failure. It is a **thesis
observation**: coverage honesty is a property of the auditor, and the stated product objective is a
property of the audited system.

### 1.2 The blocker that stranded four requirements is gone

The 2026-08-11 amendments do **not** say FR23 / FR24 / FR26 / FR29 are unbuilt. They say the
opposite, and name the shared cause:

| FR | Module | Built | Tested | Reachable from `cli.py` |
|---|---|---|---|---|
| FR23 | `argus/governance/escalation.py` | ✅ | `tests/test_hitl_escalation.py` | ❌ |
| FR24 | `argus/governance/decision_record.py` | ✅ | ✅ | ❌ — *"no importer at all inside `argus/`"* |
| FR26 | `argus/store/integrity.py` | ✅ | `tests/test_store_integrity_lint.py` | ❌ — importers themselves unreachable |
| FR29 | `argus/evidence/bundle.py` | ✅ | `tests/test_evidence_bundle.py` | ❌ — *"no `argus` CLI subcommand exports a bundle"* |

All four amendments name the same fence: *"the call site lands in `pipeline.py`, which is fenced to
Story 12.1."* **Measured at HEAD `0a6e121`:**

```
argus/pipeline.py           1,111   ← was 1,331; NFR-M1 cap is 1,200
argus/pipeline_stages.py      512   ← the Story 12.1 extraction
argus/pipeline_persist.py     268
```

**Story 12.1 landed. The mechanical fence is lifted and the amendments' own re-entry condition —
`target_story: NONE — unscheduled, to be scheduled once 12.1 lifts the NFR-M1 gate` — is satisfied.**

`tests/test_v1_commitment_closure.py` is a live tripwire on this text: it turns **red** the day a seam
becomes reachable while the FR still says it is not. Wiring without amending the FR text breaks the
build by design.

### 1.3 One half of FR23's blocker is NOT mechanical

Stated so the wiring work is not underestimated. The FR23 amendment gives **two** reasons, and only
the first is now discharged:

> (b) the V1 default path is **unattended CI** (Journeys 3 and 5) with **no human to answer a
> default-STOP gate**, so a naive wiring would deadlock every automated audit — *the design question
> 12.1's enabler must answer, not a line of plumbing.*

**That design question is still open and is the harder half.** §3.1 below scopes it as the first
story of the wiring epic, not as an afterthought.

### 1.4 FR23 is non-negotiable core

The §Cut-Order marks **FR23 non-negotiable core; only FR24 is [Tier B]**, and
`implementation-readiness-report-2026-08-03.md:365` already flagged FR23 as stranded in a slippable
epic. Any sequence that places FR23 behind unbuilt speculative work demotes a non-negotiable-core
capability below features that do not exist. This amendment therefore schedules the wiring **ahead of
all new capability work**, and in parallel with Epic 16.

---

## 2. What this amendment does NOT disturb

- **Epic 16 stands exactly as approved, and is already in flight.** Story 16.1 is drafted and
  `argus/precision/gate_decision.py` / `tests/test_gate_condition_lookup.py` carry uncommitted work.
  **Nothing in this document touches the precision or adjudication surface**, so neither epic
  proposed here can collide with work in progress. The three mechanical strengthenings
  (H-1 breadth floor, H-2 holdout, H-3 yield floor), the H-4 independence disclosure, the operator
  R2 act, the single permitted round. **Not one clause is contested.**
- **§4.3's protocol §5 amendment is untouched**, in scope and in direction.
- The **≥80% threshold**, `VALIDATION_SET_FLOOR_N = 5`, the five ratified members, `MANIFEST_FIELDS`
  at 9, FR34 and `protocol_cleared` remain untouched by this document as well.
- **No ledger entry is dispositioned.** `DF-12-2-B`, `DF-12-2-D`, `DF-13-5-A`, `DF-15-2-D` and
  everything Epic 15 cited stay open.
- **No bench round is spent, no candidate ratified, no row moved off `UNADJUDICATED`.**

**The review's conclusion about Epic 16 is that it is correct and should proceed.** Epic 16 *is* the
first detector family's lifecycle run; it does not need replacing, only surrounding.

---

## 3. New scope

### 3.1 Epic 17 (NEW) — Activate the four stranded capabilities

**Runs in parallel with Epic 16. Shares no file with it.**

Epic 16 touches the precision/adjudication surface. This epic touches `pipeline.py` (1,111 lines,
**89 lines of headroom**) and `cli.py`. Neither epic touches `argus/detectors/vacuous_test.py`
(1,196 / 1,200, **4 lines**), which the parent §2.3 correctly identifies as requiring a split before
any edit.

**17.1 — Resolve the execution-policy question before wiring anything.** Decide what a default-STOP
means on an unattended path. The recommended shape, which requires **no change to the frozen
`Verdict` enum**:

```
Verdict (3 members, frozen)   ×   EscalationOutcome (NOT_TRIGGERED | STOP | PROCEED)
```

`escalation.py` already models `escalation_fires` / `resolve_escalation` with default-STOP and
time-boxed park-at-STOP; `DecisionRecordWriter` already records the decision. Execution context then
decides what a STOP *does* — CI maps it to a non-zero exit and machine-readable evidence, an
interactive operator is prompted, an external approval system is called — without a fourth verdict.

> ⚠️ **A fourth verdict member is a wire-contract change, not a policy layer.** `Verdict` is a closed
> enum of **exactly three** members (`RELEASE_READY` / `NOT_READY_FOR_RELEASE` /
> `INSUFFICIENT_COVERAGE`), *"pinned by a committed test so adding/removing/renaming a verdict fails
> the build"*, mapped to exit codes 0 / 2 / 3 under the AR3 wire contract. Adding one requires an
> additive `schema_version` bump and is integrator-visible. **The design above is recommended
> precisely because it avoids that.** If the operator prefers a `REVIEW_REQUIRED` member instead, it
> belongs in §3.3's Step 0 contract work, not in a wiring story.

**17.2 — FR26**, `lint_referential_integrity` into the run path. Smallest surface, no CLI change.
**17.3 — FR29**, an evidence-bundle CLI subcommand (the parent's Story 12.8 fence applies).
**17.4 — FR23 / FR24**, the escalation gate and decision record, under 17.1's policy.
**17.5 —** Amend the four FR texts to state what is now reachable, in the same commit, or
`test_v1_commitment_closure.py` turns red.

**Why this is high-confidence work:** the implementations exist, are typed, and carry passing tests.
This is integration, not invention — with 17.1 as the one genuine design story.

**FR29 forward-compatibility.** Design the bundle payload as an additive `schema_version` v2 carrying
`capabilities: []` from the outset. If §3.3's direction is later approved, the bundle extends rather
than migrates; if it is not, an empty list costs nothing. This is a deliberate versioned change, not
a free extension point.

### 3.2 Epic 18 (NEW) — Family A, the second detector family, through the full lifecycle

Three AST-exact detectors with **no dependency on the resolved call graph, non-code intake, or the
LLM path**, in **new modules** that do not touch `vacuous_test.py`:

- `stub_body` — a definition whose entire body is `pass` / `...` / a bare `raise NotImplementedError`
  / a lone `return None`, where the signature, annotations or docstring promise behaviour.
- `placeholder_value` — canned returns, fixture literals and placeholder constants on a production
  path.
- `swallowed_error` — `except: pass`, `except Exception: pass`, empty `finally`.

This family is chosen for three reasons and no others: it needs **no** blocked infrastructure, it is
the family closest to the originally reported failure (a substantially incomplete repository
returning `RELEASE_READY` with zero blocking findings), and it is the **cheapest possible second
subject** for the lifecycle this program needs to demonstrate.

**Each detector ships advisory, with its own bench and adjudication, before any promotion is
discussed.** `DF-13-5-A`'s pre-registered fallback — ***"the answer is a better detector, not a bigger
bench"*** — is the authority for this epic existing at all, and it is why Epic 18 builds a detector
rather than requesting more corpus for the existing one.

> ⚠️ **OPEN QUESTION FOR THE OPERATOR — §5.1.** Family A needs corpus members carrying the
> *completeness* defect class. The existing five ratified members and fourteen candidates were
> selected against the *vacuous-test* class. Whether a completeness corpus (a) consumes
> `DF-13-5-A`'s single permitted expansion round, (b) constitutes a **separate corpus for a separate
> defect class** governed by its own protocol section, or (c) is disallowed until Epic 16 concludes,
> **is a ruling this document does not take.** Drafting Epic 18's stories before that ruling risks
> writing acceptance criteria that the protocol forbids.

### 3.3 The FR38 gate — a pre-condition, not a schedule

The review proposes a capability-centric direction (FR38–FR46: capability as a first-class audited
entity, capability ingestion, requirement-to-code traceability, acceptance-criteria conformance,
error-path coverage, architecture conformance, abstraction utility, operational readiness,
implementation completeness). **This amendment does not schedule any of it, and does not propose it
as a requirement.** It records the direction and imposes a gate.

**FR38 work does not begin until all of the following are true:**

1. **Two detector families have DEMONSTRATED the full lifecycle** — detector, bench, adjudication,
   measured precision and recall, understood false-positive behaviour, results recorded, and an
   explicit promotion decision recorded. Epic 16 discharges family 1; Epic 18 discharges family 2.
   **"Demonstrated" is not "promoted."** A family measuring precision 42% and being REJECTED has
   discharged this condition in full: the lifecycle ran, produced a number, and the number decided.
   That is a successful experiment and the gate must read it as one — otherwise the gate silently
   becomes a requirement that detectors succeed, which is not what it is for.
2. **Execution cost is measured for both**, per §4.
3. **The FR34 disclosure has been meaningfully evaluated.** *Not* "has been removed" — `BLOCKED` is a
   permitted and possibly correct outcome. The requirement is that the team knows **why**.
4. **Step 0 contract work is specified** — see below.

**The gate has two branches, and the second one is the reason it exists.** A gate with only a pass
branch cannot fail, and this repository has already named that defect class about itself: *"a rule
that is stated, locally asserted, and structurally unable to see the one place it is broken."*

| Outcome | Condition | Course |
|---|---|---|
| **GO** | Conditions 1–4 discharged, and **at least one** family promoted to blocking | FR38 Step 0 design begins |
| **NO-GO — correct course** | Conditions 1–4 discharged, but **both** families rejected on precision | **Fix detection before building over it.** A capability graph inherits the trustworthiness of the detectors feeding it; building one over two rejected families propagates the distrust rather than resolving it. Re-enter at detector design, not at FR38. |
| **NOT YET** | Any of conditions 1–4 undischarged | Gate is not evaluable. Not a failure — say so and continue the outstanding work. |

The middle row is a real, reachable outcome and must not be treated as a formality. `DF-13-5-A`'s
pre-registered answer — ***"the answer is a better detector, not a bigger bench"*** — is the same
instinct applied one level up: **a better detector, not a bigger architecture.**

**Step 0, required before any FR38 implementation, not after.** FR15 states the verdict is *"a pure
function of the coverage ledger."* FR16 is a frozen decision table. Making a capability the unit of
assurance either amends FR15 or folds the capability graph into the ledger; it cannot be done as an
implementation refactor. Required: amend FR15 and FR16, define capability-level verdict semantics,
define how `CoverageLedger` remains the evidence substrate beneath rather than being replaced, bump
`schema_version`, and **explicitly prohibit a parallel confidence derivation**.

That last clause is load-bearing. The evidence vocabulary already exists:

```
EvidenceKind (DEEP_READ | TOOL_BREADTH_ONLY | NARRATIVE_ONLY | UNGRADABLE)
        → classify_depth() → CoverageDepth (5 closed states)
        + FR8: inferred evidence can NEVER satisfy a verdict gate
```

`NARRATIVE_ONLY → INFERRED` is already the "capability claimed only in a README" case, already with a
hard rule attached. A second axis (`STRONG / PARTIAL / WEAK / NONE / UNRESOLVED`) would fork a
derivation, which **AR7 forbids** and which is precisely the architectural drift this tool exists to
find in other people's repositories. **One claim, one canonical derivation path.**

---

## 4. Assurance economics — activating a post-V1 NFR rather than inventing a metric

The review asked whether Argus can consume more LLM budget than the AI development effort it audits.
**The measurement machinery for this already exists and is already targeted.**

`argus/cost/budget_governor.py::baseline_ratio` computes NFR-C1 — *"the audit's cost as a fraction of
the audited repo's build-cost proxy"* — as an exact reduced `Fraction`, persisted canonically,
reproducible, total-safe on an empty repo. Its docstring states the target and its own status
plainly:

> *"V1 MEASURES and REPORTS this; it does NOT assert / gate on the **≤10–20% target** (a post-V1
> goal)."*

**The ≤10–20% figure the review proposed is already the written NFR-C1 target.** No new metric is
required. What is proposed is **activating the gate on an NFR that is already measured**, in the
strengthening direction, consistent with the parent §2.2's framing.

**Two limitations, stated rather than glossed:**

1. **`total_credits` is not tokens.** V1 credits are a deterministic zero-token proxy — `files_indexed`
   + `python_files` + `detector_passes × 3` — because *"the LLM dispatch port is Epic 6, so V1 cost is
   a deterministic PROXY, not a billed LLM total."* Real token accounting has a seam
   (`deep_pass._sum_credits` folds `LLMRecording.credits_used` as exact `Fraction` strings) but no
   supply, because `DF-12-2-D` keeps `delivered_count` at 0.
2. **`build_cost_proxy` is total physical LOC, not AI development spend.** So the existing ratio
   answers *"audit work-units per line of repository"* — it does **not** answer *"Argus tokens versus
   the coding agent's tokens."* Answering that needs a second denominator supplied through the FR35
   agent-integration surface. **The plumbing exists; the specific denominator does not.**

   **Recorded as a future FR35 dependency, NOT proposed as a requirement by this document:** an
   incremental-assurance-cost ratio (agent development spend as denominator, Argus assurance spend as
   numerator). One caveat must travel with it from the start — **a denominator supplied by the coding
   agent is a number reported by the thing being audited.** Development spend is *context* rather
   than a *conclusion*, so it clears this section's reuse principle, but it must be recorded as
   **disclosed, unverifiable input** and never rendered as measured fact. A ratio is only as honest
   as its denominator, and this one cannot be independently derived.

**Proposed as gate criteria for §3.3, to be recorded now and measured during Epics 16 and 18:**

| Measured per family | Source |
|---|---|
| Precision, recall, false-positive rate | Epic 16 adjudication machinery, reused |
| `baseline_ratio` (NFR-C1) | `budget_governor.baseline_ratio`, already computed |
| Wall-clock and CPU | new, cheap |
| LLM tokens | 0 for Families 1 and A — **both are zero-token**, which is itself the finding |

> ⚠️ **SCOPE OF WHAT THE TWO-FAMILY GATE PROVES — read before quoting any number it produces.** The
> gate validates the economics of **deterministic** assurance ONLY. Families 1 and A consume zero LLM
> tokens, so a favourable result establishes that *this* class of detector is cheap. It establishes
> **nothing** about FR41 (acceptance-criteria conformance), capability ingestion, or any future
> semantic family, all of which are LLM-mediated and none of which are measured here.
>
> **The sentence this guard exists to prevent:** *"We measured Argus at 10% of development cost."*
> What would have been measured is that **two zero-token detector families** cost very little. Any
> LLM-mediated family must establish its **own** token and cost budget before implementation is
> promoted beyond experimental scope. A number earned on deterministic passes may not be carried
> across to semantic ones — that is exactly the over-claim this tool exists to catch elsewhere.

**The architectural principle this implies, recommended for adoption:** deterministic analysis is the
default execution engine and the LLM is the exception, invoked only to adjudicate candidates a cheap
pass has already nominated. This is not a new design — `deep_pass.run_deep_pass` already targets only
files the run claims `audited_deep`, i.e. a nominated candidate set, never a free read of the
repository. Making it an explicit stated principle prevents FR41 (acceptance-criteria conformance)
from being built as a whole-PRD, whole-repository read, which is where a token monster would
otherwise be created.

A second principle worth recording if the FR35 surface is extended: **reuse context, never reuse
conclusions.** Argus may accept a changed-file list, requirement set or test locations from a coding
agent, but must derive its own evidence. An auditor that accepts the claim it was asked to verify has
stopped being one.

---

## 5. Rulings this document does not take

**5.1 The Family A corpus question.** §3.2's warning box. Requires an operator ruling before Epic 18
stories can be written.

**5.2 Whether the FR38 direction is adopted at all.** §3.3 is a gate on a direction, not an approval
of it. FR38–FR46 are **not proposed as requirements** by this document and appear in no FR register.

**5.3 Whether Epic 17 or Epic 18 goes first.** The three epics are **implementation-independent but
programmatically coupled by the §3.3 gate** — the precise phrasing matters and "independent" alone
would be wrong. They share no file, so neither can collide with work in progress; but Epic 18 is
coupled to Epic 16 in two ways that survive that: **both** are required to discharge gate condition 1,
and §5.4's corpus ruling may depend on what Epic 16's run returns. **Epic 17 is the only genuinely
uncoupled one** — it discharges no gate condition and blocks nothing. 17 is higher-confidence
(integration of already-tested code); 18 is closer to the reported failure. The operator's call.

**5.4 Whether Epic 18 may be drafted before Epic 16 concludes.** §5.1's corpus ruling may depend on
what Epic 16's run returns. Drafting 18's stories first risks acceptance criteria the protocol
forbids; drafting them after costs a cycle. This document recommends waiting, and does not decide.

---

## 6. What is explicitly NOT in scope

- **No change to Epic 16**, in any clause.
- **No detector is written, split or edited** by this document. `vacuous_test.py` is untouched.
- **No FR is added, amended or dispositioned** by this document. The §1.2 FR text amendments are
  scheduled as story 17.5; they are not made here.
- **No bench round is spent. No candidate ratified. No adjudication performed.**
- **No `Verdict` member added.** §3.1 recommends the design that avoids one.
- **FR38–FR46 are not requirements** and are not proposed as such.
- **NFR-C1 is not gated by this document** — activation is proposed as an Epic 16/18 measurement and
  a §3.3 gate criterion, both subject to approval.

---

## 7. Required companion edits, if approved

1. `epics.md` — Epic 17 and Epic 18 containers with their Covers lines.
2. `sprint-status.yaml` — story entries at `backlog`, plus retrospectives.
3. `deferred-work.md` — a `DF-` entry for §5.1's unresolved corpus question, owned and targeted.
4. **`tests/test_status_document_registry.py` — register THIS document.** `TC-ArgusAgent-DOCS-001-22`
   requires registration in the same commit. The parent's own registration landed in `7f54506` and
   the file is now clean against HEAD, so this needs a **new** entry. **Observe RED before and GREEN
   after**, per the parent's §4.5 precedent.
5. No edit to `precision-validation-protocol.md` beyond the parent's proposed §4.3.

---

## 8. Approval

| | |
|---|---|
| **Parent proposal** | ✅ Approved 2026-08-20 (`0a6e121`) — **unchanged and uncontested by this document** |
| **Epic 16** | 🔵 In flight — **untouched by this document** |
| **This amendment** | ⏳ Awaiting approval — **independent of the parent** |
| **Approver** | XAgent007 |
| **Drafted / re-verified** | 2026-08-20 at `0a6e121` |

Approving this document authorises the creation of Epics 17 and 18 and the recording of the §3.3
gate. It does **not** authorise any code change, any FR amendment, any bench expenditure, or the
FR38 direction. It does not commit, stage or push anything.

---

## Appendix — Reproduction of the reported failure

Executed 2026-08-20 against `XAgents/Minions` at HEAD, default flags. `.argus/` output was removed
afterwards and that repository's `git status` returned to baseline.

```
verdict=RELEASE_READY  deep_ratio=182/495  blocking_findings=0
assessed_deep_ratio=26/29  scope=application  held_out=292
```

**1,599 findings were produced. Every one was `advisory: true`.**

| rule_id | count |
|---|---|
| `orphan_code` | 843 |
| `vacuous_test_heuristic` | 516 |
| `hardcoded_secret` | 151 |
| `cross_partition` | 75 |
| `traceability_not_establishable` | 14 |

A finding is verdict-blocking **iff** `depth_supported is not None`. Traced across every
`build_recording` call site in `argus/`, **exactly one** ever sets it —
`vacuous_test.py:1065`, and only when `corroborated` is true. No `vacuous_test_ast` finding was
produced on this repository, so `blocking_findings` was 0 and the run returned `RELEASE_READY`.

**The tool behaved exactly as specified.** No requirement it holds was violated. That is the finding.
