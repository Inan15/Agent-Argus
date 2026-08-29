# Sprint Change Proposal — 2026-08-29

**The FR34 precision gate is UNEVALUABLE, not unmet — and the disclosure does not say so**

| | |
|---|---|
| **Raised by** | XAgent007, 2026-08-29 |
| **Prepared by** | Correct Course workflow (`bmad-correct-course`) |
| **Working tree** | `master` @ `be28bc9` |
| **Scope classification** | **Change A — Moderate** (disclosure accuracy). **Change B — Major** (new epic + operator ratification act). |
| **Approval** | ⬜ APPROVED ⬜ AMENDED ⬜ REJECTED — signature/date: ______________ |

> ⛔ **Read this before anything else. This proposal does not clear, soften, schedule or re-scope
> the ≥80% precision gate.** `PRECISION_GATE_THRESHOLD` stays `4/5`. `VALIDATION_SET_FLOOR_N` stays
> `5`. All seven §5 conditions stay, in their order, with their verdicts. No member is dropped,
> re-weighted or narrowed. Protocol §5 and Story 13.3 / AC5 forbid moving any of those in response
> to a failed measurement, and nothing below asks to.

---

## 1. Issue Summary

> **A note on wording in this document.** When describing THIRD-PARTY repositories it avoids the
> registered ArgusAgent readiness phrase that `TC-ArgusAgent-DOCS-001-21` scans for — the one
> pairing "production" with "ready" — and says *heavily-exercised* or *hardened by real use*
> instead. Using that phrase about someone else's tree, inside a document the citation rule scans,
> would demand a gate citation for a statement that was never about this tool: the `DF-9-2-B`
> false-subject class arriving from the opposite direction. The scan is deliberately a blunt
> substring match and is right to be; the fix is to say what was meant.
>
> This note itself tripped the scan on its first draft, which quoted the phrase in order to say it
> was being avoided. Recorded rather than silently fixed — it is a small live demonstration that a
> blunt scan cannot read intent, which is the same property that makes it trustworthy.

### 1.1 What was observed

The operator observed that the ≥80% finding-precision gate looks unreachable in practice, on two
grounds: mature open-source repositories have already been hardened by years of real use, so genuine
defects are rare;
and Argus's detectors are AST/static, surfacing structural signals whose status as "real issues" is
an adjudication judgement rather than a fact.

### 1.2 The measurement that confirms it — already in this repository

This is not a new hypothesis. It is a recorded measurement, and the project reached it first:

- **Epic 14's corrected detector, run across all five ratified corpus members** (`architecture.md`
  §Gate-decision enforcement, Story 13.5 / AC5): **1,960 in-scope source files at the pinned shas,
  5,129 test functions scored, 4,284 advisory findings emitted, and ZERO promoted to
  verdict-eligible.**
- **The PRD already states the consequence in one sentence** (`E-PRD/prd.md` L190): *"The expected
  outcome of the re-run is `UNEVALUABLE`, not `CLEARED` … an empty precision denominator is
  `UNEVALUABLE` by construction. A fix that removes the findings removes the measurement, not the
  shortfall."*
- **`DF-16-1-A`** records, measured by two independent instruments, that the maximum achievable
  distinct verdict-eligible **rule-class count is 1**.

Precision is `TP / (TP + FP)`. A population of mature, heavily-exercised repositories yields a
near-empty verdict-eligible set by construction, so the ratio is not low — it is **undefined**. The
gate's recorded outcome is therefore `BLOCKED` with §5's precision condition `UNEVALUABLE`; it is
**not** `NOT_CLEARED`, and the project built a closed three-member vocabulary
(`CLEARED` / `NOT_CLEARED` / `BLOCKED`) precisely so those two could never be confused.

### 1.3 The defect this exposes

**The FR34 disclosure is less honest than the machinery behind it.** Every user-facing surface
carries:

> "This notice is removed only when the >=80% precision gate is met; nothing else removes it."

That sentence describes a pending pass/fail that is merely late. It does **not** say the gate is
currently unevaluable, that the corrected detector promoted zero findings across the ratified
corpus, or that a countable closure path exists. A reader meeting only this sentence cannot
distinguish *"judged and fell short"* from *"never measurable"* — which is exactly the distinction
Story 13.3 / AC1 introduced `BLOCKED` to preserve, and which `NOT ESTABLISHED` preserves for release
status one document over.

The surfaces affected are the enumerated FR34 set: `README.md`, `CHANGELOG.md`,
`pyproject.toml [project].description`, `action.yml description:`, the four rendered report
artifacts, the CLI human register, and the MCP routes.

### 1.4 Why the conditions are right and the gate still cannot fire

*(Amended 2026-08-29 before approval. The first draft read "seven conditions over an empty set is
rigour applied to nothing," which lands as a criticism of delivered work. It is not one, and the
sharper point is not adversarial — it is about ordering.)*

Epics 16.1, 16.2 and 16.3 each added a §5 condition — **breadth**, **seal**, **yield** — taking the
set from four to seven. **Each was necessary and each was proven necessary by execution**, not
argued: three findings from a single member returned `CLEARED` at precision `1/1` with all six prior
conditions `MET`. Without those three additions, the first population that did produce a denominator
could have cleared the gate on evidence too narrow, too small, or drawn from code the detector had
been tuned against. They are the reason a future `CLEARED` will be worth something.

The observation is about **sequence, not quality**: those three conditions govern *what a denominator
must look like to count*, and the denominator has been empty throughout. So the gate is now
well-defended and still unable to fire. **The remaining work is orthogonal to them — it is to
produce a population at all, at which point all seven conditions do exactly the job they were built
for.** Change B does that, and none of the three is weakened, reordered or re-scoped by it.

---

## 2. Impact Analysis

### 2.1 Epic impact

| Epic | Status | Impact |
|---|---|---|
| 13 (clear the gate) | delivered; gate `BLOCKED` | Not reopened. Its decision record stands and is byte-reproducible. |
| 14 (fix the instrument) | done | Not reopened. Its measurement is the evidence for this proposal. |
| 16 (§5 conditions 5–7) | done | Not reopened, not weakened. |
| **NEW epic (Change B)** | proposed | Corpus evaluability. Depends on an operator ratification act. |

### 2.2 Artifact conflicts

| Artifact | Change |
|---|---|
| `argus/verdict/negative_assurance.py` | Disclosure constant states the recorded gate state. |
| `E-PRD/prd.md` | FR34 amended by dated addition: the disclosure must publish the outcome, not only the threshold. |
| `architecture.md` | Registration note appended under Gate-decision enforcement. |
| `README.md`, `CHANGELOG.md`, `docs/first-run.md`, `pyproject.toml`, `action.yml` | Re-render the disclosure. |
| `deferred-work.md` | New entry for the corpus-evaluability finding. |

### 2.3 Technical impact

Change A is a constant plus propagation; the disclosure renderer (`render_instrument_disclosure`)
is already pure, single-sourced and exhaustive over `InstrumentStatus`, so no new mechanism is
needed. `InstrumentStatus` stays **CLOSED at two** — this proposal does not add a third member;
the gate's own three-member outcome vocabulary already carries the detail and must not be
duplicated into the instrument enum (that enum's docstring warns against exactly this).

---

## 3. Recommended Approach

**Direct Adjustment** for Change A. **New epic** for Change B. No rollback. No MVP reduction.

### Change A — the disclosure publishes the gate's recorded outcome

The notice states what `gate-decision-record.json` already holds: the outcome, the precision
condition's verdict, and the countable closure path. The threshold, the corpus and all seven
conditions are untouched.

### Change B — make the gate EVALUABLE by fixing the population, never the threshold

The gate requires verdict-eligible findings to have a denominator. The corpus is five mature,
heavily-exercised repositories. **Argus detects code written to look done; mature OSS is code that
is done.** The instrument is being measured against the one population it was not built to find
anything in.

Note the alignment, which is the argument for this rather than a workaround: the product's stated
wedge is **agent-generated code**, which is precisely where vacuous tests, orphan code and weak
assertion strength are dense. The population that would produce a denominator is the same
population the product is for.

**Why this is not goalpost-moving, stated explicitly because the rule is strict.** §5 and Story
13.3 / AC5 forbid moving the threshold and forbid NARROWING the population in response to a
shortfall — *"a filter NARROWS … while a CONDITION REQUIRES."* Change B moves neither. It **adds**
sealed members to an existing corpus at an unchanged bar, under the pre-registration and seal
discipline the repository already owns (`scripts/precision_preregistration.py`, the `sealed` /
`open` / `pre-seal` partition from Story 16.2, and the operator ratification act from 13.1 / AC3b).
Members must be selected and sealed **before** the detector is run against them, or the seal
condition refuses them — which is the guarantee that makes this an honest broadening rather than a
hunt for a favourable sample.

### Explicitly rejected alternatives

| Alternative | Why rejected |
|---|---|
| Lower `PRECISION_GATE_THRESHOLD` below 4/5 | Goalpost-moving in response to a failed measurement. §5 / 13.3 AC5. |
| Replace precision with false-alarm rate | Different metric answering a different question; would retire the honesty keystone by substitution. |
| Count the defect cartridges toward the gate | PRD L205: *"the planted-defect cartridges measure recall, not this."* They are not corpus members by design. |
| Add an eighth §5 condition | The gate is already unevaluable; further conditions cannot make an empty denominator measurable. |
| Add a third `InstrumentStatus` member | The outcome vocabulary already exists on `GateDecision`; duplicating it into the instrument enum repeats the run-grade/instrument-status confusion that enum warns against. |

---

## 4. Detailed Change Proposals

### 4.1 `argus/verdict/negative_assurance.py` — the disclosure constant

**OLD**

```
"Beta: Argus's finding precision has not been independently validated. Its findings rest on the
Argus dogfood corpus, a self-audit of this repository. Treat findings as a prompt to look, not a
verdict. This notice is removed only when the >=80% precision gate is met; nothing else removes it."
```

**NEW** (framing plus the recorded state; every disclosed fact retained, the pinned phrases
`has not been independently validated`, `rest on the Argus dogfood corpus, a self-audit of this `
and `removed only when` preserved)

```
"Argus's audit is deterministic and reproducible by construction. Argus's finding precision has not
been independently validated, so treat a finding as a prompt to look rather than as a verdict; its
findings rest on the Argus dogfood corpus, a self-audit of this repository. The >=80% precision gate
is currently recorded BLOCKED with its precision condition UNEVALUABLE — the corpus was read and no
finding was promoted to verdict-eligible, so the ratio has an empty denominator rather than a low
value. This notice is removed only when the >=80% precision gate is met; nothing else removes it."
```

**Rationale.** The last sentence is unchanged and still binding. The added sentence stops a reader
inferring a late pass/fail from an unevaluable one, and it is the same discipline `NOT ESTABLISHED`
applies to release status.

### 4.2 `E-PRD/prd.md` — FR34, amended by dated addition

> **AMENDED 2026-08-29.** FR34's disclosure obligation extends from the THRESHOLD to the RECORDED
> OUTCOME: every enumerated surface must publish the gate's outcome from the closed
> `CLEARED`/`NOT_CLEARED`/`BLOCKED` vocabulary and the verdict of §5's precision condition, not the
> threshold alone. ⛔ The ≥80% threshold, corpus membership, and all seven §5 conditions are
> UNCHANGED; this amendment adds a disclosure duty and removes none.

### 4.3 `architecture.md` — registration under Gate-decision enforcement

> **AMENDED 2026-08-29 — the disclosure inherits the outcome vocabulary.** The rule: an FR34 surface
> that names the gate must also name its recorded OUTCOME and the precision condition's VERDICT.
> Measured on the day it landed: the shipped notice said only *"removed only when the >=80%
> precision gate is met"* while `gate-decision-record.json` held `BLOCKED` / `UNEVALUABLE` and Epic
> 14's corrected run had promoted 0 of 4,284 findings — so the surface a stranger reads could not
> express the distinction `BLOCKED` was introduced to preserve.

### 4.4 New epic — Corpus evaluability (Change B)

**Goal:** make §5's precision condition evaluable at an unchanged threshold.

1. **Pre-register** selection criteria for defect-bearing members before any candidate is audited
   (`scripts/precision_preregistration.py`).
2. **Ratify** candidates by operator act (13.1 / AC3b precedent). Sealed partition assignment is a
   pure function of the pinned sha and must precede any Argus output over them.
3. **Run and adjudicate**, disclosing concentration as 13.3 / AC3b requires.
4. **Name a second adjudicator.** Story 16.5 derives independence as `NOT_INDEPENDENT` — 31 of 31
   live judgements authored by XAgent007, who is also the tool's author. Protocol §2 says the
   external sign-off *"SHOULD be outside the implementing team."* A gate cleared by its own author
   will not persuade the audience the gate exists for. This is a hiring/recruiting act, not a build
   task, and it should start now because it has the longest lead time.

**Exit condition:** §5's precision condition returns a verdict other than `UNEVALUABLE` — whatever
that verdict is. **Clearing the gate is not an acceptance criterion of this epic.** An evaluable
`NOT_CLEARED` is a success; it is a measurement where today there is none.

---

## 5. Implementation Handoff

| Change | Scope | Route to | Deliverable |
|---|---|---|---|
| A — disclosure publishes the outcome | Moderate | Developer (`bmad-dev-story`) | Constant + propagation to the enumerated surfaces; PRD/architecture amendments; suite green |
| B — corpus evaluability | Major | PM / Architect, then operator | New epic; pre-registration; ratification act; second adjudicator |

**Success criteria for A:** every enumerated FR34 surface renders the outcome and the precision
condition verdict; `TC-ArgusAgent-DOCS-001-43`/`-47`/`-49`/`-51` and the over-claim scan stay green;
`INSTRUMENT_STATUS` unchanged and still guarded; no §5 condition, threshold or corpus member moved.

**Success criteria for B:** §5's precision condition is evaluable; the ratio is computed over a
sealed, pre-registered, breadth- and yield-satisfying population; the outcome is recorded whatever
it is.

**Out of scope for both:** clearing the gate; changing the threshold; changing corpus membership by
removal or re-weighting; adding an `InstrumentStatus` member.

---

## 6. Approval

⬜ APPROVED ✅ **AMENDED** ⬜ REJECTED

**Approved as amended by XAgent007, 2026-08-29.** Approval was given in-session ("amend and
proceed"); it is recorded here by the agent that drafted the proposal rather than signed by the
operator's own hand, and that distinction is stated rather than smoothed over — a recorded
attribution is not a signature, and a reader auditing this later should know which one this is.

**The one amendment taken before approval:** §1.4 was rewritten. The draft read *"seven conditions
over an empty set is rigour applied to nothing,"* which reads as a criticism of Epics 16.1–16.3.
That is not the finding. Each of those three conditions was proven necessary by execution and each
is the reason a future `CLEARED` will mean anything; the real observation is about **sequence** —
they govern what a denominator must look like, and there has been no denominator. Nothing else in
this proposal changed.

*A proposal that amends FR34 — the PRD's most-elevated constraint — is not in force until this box
is marked. The 2026-08-10 proposal's §6 box was never marked and only its sprint-status edit landed;
that precedent is why this section exists.*
