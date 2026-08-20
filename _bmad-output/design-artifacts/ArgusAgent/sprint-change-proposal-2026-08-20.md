# Sprint Change Proposal — 2026-08-20

**Project:** ArgusAgent (formerly APAA — AI Project Assurance Audit)
**Author:** Orchestrator (`bmad-dev-loop`), acting on the Epic 15 retrospective's SD-1/SD-2/SD-5/SD-6
**Requested by:** XAgent007
**Trigger type:** Plan exhaustion with the gate unevaluable. Epic 15 closed 2026-08-19 having made
the gate *evaluable in principle* — a 14-repository bench carrying the defect class — and having
deliberately stopped short of using it. `epics.md` ends at Epic 15, so the work that would spend
that bench has no container.
**Change scope classification:** **MAJOR** — one epic created; **and an amendment to protocol §5,
the ≥80%-precision externalization gate itself**, in the STRENGTHENING direction only
**Status:** ✅ **APPROVED by XAgent007, 2026-08-20.** The document was authored and committed
(`7f54506`) in the `AWAITING OPERATOR APPROVAL` state, and approval was taken as a **separate,
later act** — recorded here in place, with §6 carrying both dates so the two are not collapsed. The
distinction is the whole point of §4.3: the gate amendment could not be authored and approved in one
motion by the party proposing it.

> **Nothing under `argus/` or `tests/` was modified to produce this document**, and no detector was
> run over any candidate. Every figure below is read from committed artifacts — chiefly
> `validation-corpus/gate-decision-record.json` at HEAD `ef41449` — or from `git`. The one edit this
> document lands alongside itself is its own registration in `_STATUS_DOCUMENTS`, which
> `TC-ArgusAgent-DOCS-001-22` requires in the same commit because it closes in both directions.
> **This proposal measures nothing new and clears nothing. It decides what may be spent, on what,
> and in which order.**

---

## 0. What this document is for, in one paragraph

The corrected detector reads the five-member validation corpus and emits **zero** blocking findings.
That is not a shortfall — it is an **empty denominator**, and the gate records it as `BLOCKED` with
the corpus-read proof that distinguishes *"measured nothing"* from *"never looked"*. The reason is
established without running the detector: the corpus barely contains the defect class. Epic 15 built
a bench that does. But spending that bench under the gate **as currently written** would buy a
number a sceptical third party is entitled to discount to nothing — because the gate does not
require the score to be broad, does not hold anything back, does not require the tool to find
anything, and is adjudicated by the person who wrote the tool. This proposal creates **Epic 16**,
which closes three of those four mechanically **before** the bench is spent, then spends it once.

---

## 1. Issue Summary

### 1.1 The measured state of the gate

Read from `gate-decision-record.json` (`decided_on: 2026-08-18`, `protocol_version: V1.3`):

| §5 condition | State | Evidence |
|---|---|---|
| Precision ≥ 80% (exact `Fraction`) | **UNEVALUABLE** | `precision.evaluable = False`; empty emitted population |
| Clean-repo blocking FP == 0 | Met over the **cartridge** corpus (`clean_repo_fp = 0`, 2 clean members, 10 folded); **NOT APPLICABLE** over the repository corpus | `clean_repo_evidence.note` |
| Corpus floor N ≥ 5 | **MET** (`corpus.n = 5`, `floor_n = 5`) | ratified 2026-08-16 under Story 13.1 / AC3b |
| Adjudication run recorded cleared | **False** — 31 rows, zero judgements, `expert_hours = null` | `adjudication_record` |

**Outcome: `BLOCKED`** — explicitly *not* a §5 outcome, and the record forbids it ever being
rendered as *"the gate did not clear"*.

The corpus-read proof is what makes the zero a measurement: **5 members audited at their pinned
shas** and proved byte-for-byte against the git object database, **1,960** in-scope source files
scanned, **828** test files identified, **5,129** test functions scored, **1,249** files flagged,
**4,284 advisory and 0 blocking** findings emitted.

### 1.2 Why the corpus returns zero — established without running Argus

Story 15.1 measured, by text patterns only with `argus.detectors` structurally banned from the
harness: across **315** Python test files at three pins, the files carrying **both** a mock binding
**and** a mock assertion number **1** under the strict predicate and **6** under a looser one. Both
predicates are recorded verbatim and the conclusion is invariant to the choice.

The bench Epic 15 selected carries **2,316** test files and **614** co-occurrence files. That is an
order-of-magnitude fact and, as Story 15.1 states in terms, **not a prediction of yield**.

### 1.3 The four holes — why spending the bench under the current gate is bad value

**H-1 · The gate never requires the score to be broad.** The last adjudicated population was **31
findings drawn from 2 of 5 ratified members across 1 distinct rule class** (`minions` 24,
`agent-smith` 7; three members contributed zero). The record computes `concentration.is_concentrated
= True` and states plainly that it is *"derived — not a threshold and not a distribution
requirement"*. **A gate can therefore clear on a denominator from one repository and one rule
class.** Every input to a breadth threshold is already computed; nothing enforces one.

**H-2 · Nothing is held back.** The cartridge corpus has an author-blind holdout
(`holdout_vacuous`). The repository corpus that actually gates has **none**. If all 14 bench members
are adjudicated and the detector is then tuned, no untouched population remains to show the tool was
not shaped to fit its own exam.

**H-3 · Precision alone is one-sided.** `UNEVALUABLE` closed the *emit-nothing* hole, but a detector
emitting three ultra-safe findings scores 100% and is useless. Recall is diagnostic-only by the OI1
lock. Nothing establishes that the tool **finds** things at a rate worth shipping.

**H-4 · The adjudicator is the author.** Protocol §2 names **XAgent007** as Engineering Lead and
primary adjudicator; **QA Lead is unfilled** and **External adjudicator is unfilled**. §2 already
says that for an externalization sign-off the tie-break *"SHOULD be outside the implementing team"*.
This is the one hole no internal rigour closes.

> **H-1, H-2 and H-3 are closable by code, before the bench is spent. H-4 is not.** It is a
> statement about who is in the room, and it governs how loudly the result may be advertised — not
> whether the arithmetic is right.

### 1.4 The constraint that makes ordering non-negotiable

`DF-13-5-A`, answered **2026-08-17 before any number existed**, permits **exactly ONE**
bench-expansion round and names the fallback if it returns zero. Epic 15 selected without consuming
it; the round is **UNSPENT**. Adding breadth and holdout requirements *after* seeing what the bench
yields is corpus-shopping in the other direction. **They land first or they do not land.**

---

## 2. Impact Analysis

### 2.1 Epic impact

- **Epics 1–15:** unchanged, undisturbed, not reopened. All retrospectives stay signed.
- **Epic 16 (NEW):** the container SD-5 identified as missing.
- No epic is redefined; no story in any closed epic is amended.

### 2.2 Severity

**MAJOR**, and stated precisely so the classification is not read as alarm: the *gate definition*
changes. §5 gains conditions. It gains them in the **strengthening** direction only.

> **This is not the threshold change §5 and Story 13.3 / AC5 forbid.** Those forbid *narrowing the
> corpus, dropping a member, or re-weighting one to move the ratio* — changes that make clearing
> **easier**, made in response to a failed measurement. Every change here makes clearing **harder**,
> and each is made **before** the measurement it governs. The ≥80% figure itself is **untouched**,
> the five ratified members are **untouched**, and `VALIDATION_SET_FLOOR_N` stays **5**.

### 2.3 Blast radius — NFR-M1's 1,200-line ceiling, measured at HEAD `ef41449`

| File | Lines | Headroom | Note |
|---|---|---|---|
| `argus/detectors/vacuous_test.py` | 1,196 | **4** | `DF-15-2-D`; a split is a precondition of any detector edit |
| `tests/test_vacuous_density.py` | 1,159 | **41** | **no ledger entry exists** — filed by §4.4 |
| `tests/test_evidence_citation.py` | 1,076 | 124 | post-13.4 split |
| `tests/test_status_document_registry.py` | 338 | 862 | this document's registration lands here |

Epic 16 as scoped touches **neither** of the two tight files: the breadth floor, the holdout split
and the yield floor live in the precision/adjudication surface, not in the detector. If any story
finds it must edit `vacuous_test.py`, the split is its first task, not an afterthought.

### 2.4 What is explicitly NOT in scope

- **No R2 ratification.** Choosing which candidates become members stays an operator act.
- **No detector run over any candidate** by this document.
- **No adjudication.** No row moves off `UNADJUDICATED`.
- **The ≥80% threshold, `VALIDATION_SET_FLOOR_N`, FR34 and `protocol_cleared`** are untouched.
- **`MANIFEST_FIELDS` stays closed at 9**; all 14 candidate rows stay `eligible_for_n=False`.
- **No ledger entry is dispositioned.** Everything Epic 15 cited stays open.
- **The Minions handoff (H0–H4)** is untouched and still not filed.

---

## 3. Recommended Approach

### 3.1 Options evaluated

| # | Option | Verdict |
|---|---|---|
| 1 | **Spend the round now, under the gate as written** | ❌ Buys a number with four known discounts on it, and the round cannot be re-spent. Fastest path to a figure nobody outside the team should believe. |
| 2 | **Strengthen the gate first (H-1..H-3), then spend the round once** | ✅ **SELECTED.** The three closable holes are closed by code, before any result exists to bias the choice. |
| 3 | **Fix H-4 first (recruit an independent adjudicator), then 2** | ⚠️ Correct but not schedulable by this document — it needs a second person. Folded in as a disclosure requirement rather than a blocker. |
| 4 | **Abandon the attested tier; ship disclosed-only permanently** | ❌ Discards a bench that took the one permitted round to assemble. Remains the honest fallback if Epic 16's run returns `UNEVALUABLE` again. |

### 3.2 Selected — Option 2, with H-4 recorded rather than solved

Epic 16 lands the three mechanical strengthenings, **each proved by executed mutation before it is
trusted**, then takes the operator act, runs, adjudicates and lets the arithmetic decide. H-4 is
handled by making the gate record state, mechanically, whether its adjudication was independent —
so a non-independent result cannot be quoted as if it were independent.

### 3.3 Effort, risk, timeline

- **16.1–16.3** are self-contained and autonomous; no operator act, no third-party fetch.
- **16.4** is blocked on the R2 operator act and carries the ≤4 expert-hour adjudication budget
  (a **report**, never a gate — §3 as amended).
- **Principal risk:** the run returns `UNEVALUABLE` or below 80% anyway. That is a permitted
  outcome, the round is then spent, and `DF-13-5-A`'s pre-registered answer applies: **the answer is
  a better detector, not a bigger bench.** Epic 16 must not be read as licence to expand again.

---

## 4. Detailed Change Proposals

### 4.1 `epics.md` — 1 edit

Insert **Epic 16** immediately before the `## Minions-Repo Handoff` section. Five stories, with a
**binding ordering constraint**: 16.1, 16.2 and 16.3 must land in commits that **precede** every
commit containing Argus output over any bench member, evidenced by git ancestry exactly as Story
15.1's `TC-ArgusAgent-PRECISION-001-75` already evidences its own.

### 4.2 `sprint-status.yaml` — 7 entries

`epic-16` plus five stories at `backlog`, plus `epic-16-retrospective` at `backlog` — created **with
the epic**, closing for good the structural gap the Epic 14 retrospective had to patch twice (epics
14 and 15 were both created without their retrospective key).

### 4.3 `precision-validation-protocol.md` — §5 amendment ⚠️ **PROPOSED, NOT APPLIED**

Three conditions added to §5, struck-not-erased in the established style, on approval:

1. **Denominator breadth floor.** Precision is evaluable only over a population drawn from **≥3
   distinct contributing members** and **≥2 distinct rule classes**. Below either, the outcome is
   `UNEVALUABLE` — the state already exists and already forces the gate provisional. This promotes
   `concentration.is_concentrated` from a disclosure to a threshold; every input is already computed.
2. **Sealed holdout.** A pre-committed, sha-ordered split of the ratified bench, opened exactly
   once. The gate is computed over the sealed partition; tuning happens only against the open one.
3. **Yield floor.** A run that promotes nothing on a bench selected *because* it carries the defect
   class is a finding about the detector, not a pass. Recorded as a condition, not a diagnostic.

**Numbers to be fixed by the story that implements each, derived and recorded — never typed.** This
document deliberately proposes the *shape* and leaves the constants to measurement.

### 4.4 `deferred-work.md` — 1 new entry

**`DF-15-2-E`** — `tests/test_vacuous_density.py` sits at 1,159/1,200 with **no ledger entry at
all**, while its sibling `vacuous_test.py` (1,196) has `DF-15-2-D`. The Epic 15 retrospective found
this as SD-6. Filed with an owner; not fixed here.

### 4.5 `tests/test_status_document_registry.py` — 1 entry

`"sprint-change-proposal-2026-08-20.md"` added to `_STATUS_DOCUMENTS`, with the verification
recorded in its comment: `-22` observed **RED** against this document before the line and **GREEN**
after, on the live tree. **Committed together with this document** — `-22` closes in both directions.

---

## 5. Implementation Handoff

1. **Operator approves or rejects this document** — §4.3 amends the gate and nothing proceeds without it.
2. On approval, the dev loop drives **16.1 → 16.2 → 16.3** autonomously.
3. **STOP.** 16.4 opens with the R2 operator act: ratify some or all of the 14 candidates. Not autonomous.
4. Run, adjudicate under §4, recompute `decide_gate`, let the arithmetic decide.
5. **16.5** stamps the independence status onto the record whatever the number is.
6. Epic 16 retrospective.

---

## 6. Approval

| Field | Value |
|---|---|
| **Proposed** | 2026-08-20, orchestrator (`bmad-dev-loop`), committed `7f54506` |
| **Approved by** | ✅ **XAgent007 (Engineering Lead), 2026-08-20** — a separate act after the commit above, not a self-approval folded into authoring |
| **What approval authorises** | Stories **16.1, 16.2 and 16.3** to apply §4.3's three §5 conditions, each deriving and recording its own constants. It does **NOT** authorise 16.4: that story still opens by halting on the protocol §6 **R2** operator act. |
| **What approval does NOT authorise** | Any softening. The ≥80% figure, `VALIDATION_SET_FLOOR_N`, FR34, `protocol_cleared` and the five ratified members stay untouched; the three new conditions may only make clearing **harder**. |
| **Gate moved by this document** | **None.** `protocol_cleared` is `False` and has never been `True`. Approval moves no gate — it schedules the work that changes how the gate is evaluated. |
| **`DF-13-5-A` round** | **UNSPENT.** Epic 16 story 16.4 is where it is spent, after a second, separate operator act. |
