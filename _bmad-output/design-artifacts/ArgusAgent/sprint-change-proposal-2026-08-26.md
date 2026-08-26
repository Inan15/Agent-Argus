# Sprint Change Proposal — 2026-08-26

**Author:** XAgent007 (Engineering Lead) · **Workflow:** `bmad-correct-course` · **Mode:** batch
**Trigger:** operator-directed; **no story**. The Epic 17 roll-up (`75ea6e4`) closed `epics.md` at
Epic 18 with every epic `done`, and `AI-E17-4` names this workflow by name as the required next act.
**HEAD at authoring:** `75ea6e4` (clean tree)
**Scope:** `AI-E17-4`, `AI-E17-8`, `AI-E17-7`

> ⛔ **STATUS: AWAITING OPERATOR APPROVAL.** Nothing here is filed, ratified, adjudicated or
> scheduled. No epic is added to `epics.md` and no key is added to `sprint-status.yaml` until this
> proposal is approved.
>
> ⛔ **THIS PROPOSAL RATIFIES NO CORPUS MEMBER, WRITES NO DISPOSITION AND EDITS NO PROTOCOL BYTE.**
> `adjudication-record.json`, `precision-validation-protocol.md` and `tests/corpus/_manifest.py` are
> byte-unchanged by the act of writing it.
>
> ⚠️ **`DF-13-5-A` IS NOT SPENT HERE, AND WHETHER STORY 19.2 WOULD SPEND IT IS AN OPEN QUESTION
> PUT TO THE OPERATOR IN §3.4 — NOT ANSWERED IN THIS DOCUMENT.**

---

## 1. Issue Summary

### What triggered this

Epic 17 ended with its own headline capability unreached. Story 17.4 ran the single pre-registered
measurement and the frozen fold returned **`UNEVALUABLE`** — not `NOT_MET`, which would have been a
result, but *unevaluable*, which is the absence of one. The Epic 17 retrospective recorded the cause
as two independent blockers (`AI-E17-4`) and recommended this workflow be run **before any future
epic proposes to promote a successor predicate**.

The three action items in scope share one root: **the acts that would unblock them are operator acts,
and there is no container in the plan that can hold an operator act.** `epics.md` ends at Epic 18
(3,763 lines); `sprint-status.yaml` records epics 1–18 and every story `done`, with **41 open action
items, 13 of them `critical`**.

### The core problem, stated precisely

*Category: technical limitation discovered during implementation — compounded by a planning gap.*

**Both `UNEVALUABLE` arms are true simultaneously, and clearing either one alone changes only which
arm the fold reports.** The fold order is fixed by pre-registration §2.5 — resolution floors, then
the denominator, then the two joint conditions — so it returns on the first shortfall and the second
stays invisible until the first is cleared.

### Evidence — measured at `75ea6e4` by execution, not quoted

**Blocker 1 — the sealed partition and the ratified members do not overlap.**

| observation | value |
|---|---:|
| `VALIDATION_CORPUS` members | 21 |
| members with `eligible_for_n = True` (the ratified set) | **5** |
| ratified set vs `PRE_SEAL_MEMBER_IDS` | **identical** |
| `SEALED_PARTITION_TABLE` rows | 14 (**6 `sealed`**, 8 `open`) |
| sealed members with `eligible_for_n = True` | **0** |
| **sealed ∩ ratified** | **∅ (empty)** |

The five ratified members are `ai-body-runtime`, `agent-markovich`, `minions`, `xagents-webapp`,
`agent-smith` — all pre-seal. The six sealed members are `aws-aws-sam-cli`, `celery-celery`,
`certbot-certbot`, `conda-conda`, `getsentry-sentry-python`,
`googleapis-google-auth-library-python` — all `eligible_for_n = False`. Protocol §5's
*gate-evidence-drawn-from-the-sealed-partition* condition therefore reads **FAILED over the very
population a successor is measured on**, and only a protocol **§6 R2 operator act** can move it:
*"choosing which repositories are legitimate members, and fetching third-party source, are not
autonomous acts."*

**Blocker 2 — the adjudicated denominator for any successor class is zero.**

| observation | value |
|---|---:|
| rows in `adjudication-record.json` | 31 |
| distinct `rule_id` | **1 — `vacuous_test_ast`** (the *incumbent*) |
| dispositions | **26 FP · 5 BORDERLINE · 0 TP** |
| adjudicated rows of **any successor class** | **0** |
| authors of all 31 live judgements | `XAgent007 (Engineering Lead)` — derived `NOT_INDEPENDENT` |

`precision_fraction(0, 0)` is `None`; the fold returns `UNEVALUABLE` on an empty denominator
(`AI-E11-1` — an empty adjudicated population is never a flattering 100%). Creating successor-class
rows is a **named-human act** under protocol §4; `AdjudicationRow.__post_init__` raises
`UnregisteredAdjudicator` if a machine attempts it, and `UNADJUDICATED` is the only member an
automated producer may write.

**A third fact, and it sharpens `AI-E17-8`.** Protocol §2's **External adjudicator** tie-break is
**unfilled** — Engineering Lead is XAgent007, QA Lead is Veer Pratap Singh (named 2026-08-22), and
§4's ladder terminates at the empty third rung. The base rate of reaching it is **not** low: the one
comparable population produced **5 borderlines in 31 rows (16%)**. Story 17.4 avoided the ladder only
by adjudicating nothing, which no story that must produce a ratio can repeat.

### A second issue, found while assessing impact

**`AI-E17-7` names seven homeless entries. The measured population is 46.**

`tests/test_governance_record_integrity.py::_POINTS_AT_DONE_AT_LANDING` — the shrink-only registry
`TC-ArgusAgent-DOCS-001-80` enforces — carries **49 pairs across 46 distinct ids**. Exactly **6** are
tagged `"17-5"` (`DF-12-2-D`, `DF-12-3-A`, `DF-14-1-A`, `DF-16-7-A`, `DF-16-7-B`,
`DF-INV-VACUOUS-A`); the other **43 are tagged `"unverified"`** and have never been measured against
the codebase at all. The ledger holds **166 canonical entry blocks**. `DF-AUD-DETECT-C` — the
seventh entry in `AI-E17-7` — is *not* in the registry: it received a corrected pointer and a live
owner but explicitly no disposition.

⛔ **The registry can only shrink.** `-80` fails if a registered pair becomes clean *and* fails
immediately on any affirmative stale pointer not listed. So giving an entry a container is never a
documentation-only edit: it requires a paired edit to the registry in the same commit, or the suite
goes red.

---

## 2. Impact Analysis

### Epic impact

| Epic | Assessment |
|---|---|
| Epics 1–18 | All `done`. **None is reopened by this proposal.** No completed work is invalidated. |
| Epic 17 | Its charter is already corrected in place under `epics.md` §3.4 (Story 17.5). Its `Covers:` list named six ledger entries, **none delivered** — all six are still open. No further correction proposed. |
| **A new epic is required** | Checklist §2.2 branch *"add new epic to address the issue"*. There is no other viable container: every existing epic is closed, and re-opening a closed epic to hold new work is the `DF-8-5-C` defect class in planning form. |

### Story impact

No existing story changes. The work is **new**, and two of its six units are **not dev stories at
all** — they are operator acts that a `bmad-dev` subagent is structurally forbidden from performing.
This is the crux: filing them as ordinary `backlog` stories would hand a dev agent a task it must
refuse, which is how Story 13.1 produced an ESCALATION and how 17.4 produced a HALT.

### Artifact conflicts

| Artifact | Impact |
|---|---|
| `epics.md` | **Add Epic 19.** No existing epic text edited. |
| `sprint-status.yaml` | Add `epic-19` + story keys at `backlog`; add the two operator-act keys in a form that is visibly not `backlog` (see §4.3). |
| `precision-validation-protocol.md` | **§2 holder table only, via a DATED BLOCK — no change-log row.** See §3.2; this is the load-bearing finding of the analysis. |
| `tests/corpus/_manifest.py` | `eligible_for_n` flips for ratified sealed members — **operator act output**, never a dev edit. |
| `adjudication-record.json` | Gains successor-class rows — `UNADJUDICATED` from the machine, dispositions from named humans only. |
| `deferred-work.md` | Append-only notes (§3.4 evidence immutability). ⚠️ Carries a **lone CR at line 5459**; every edit must be made in **binary mode** and both byte invariants re-measured before and after. |
| `tests/test_governance_record_integrity.py` | `_POINTS_AT_DONE_AT_LANDING` shrinks by exactly the entries that gained a container. |
| **PRD (`E-PRD/prd.md`)** | **No amendment proposed.** The ≥80% externalization gate is not wrong and the MVP is not overscoped — the gate is honestly `BLOCKED`, which is the behaviour it was built to have. |

### Technical impact

No production code path changes. `argus/**` is untouched by Stories 19.1, 19.3 and 19.6; 19.5 runs the
already-shipped frozen fold. **No finding becomes verdict-eligible by anything proposed here** — S1
stays ADVISORY, and `argus/detectors/vacuous_test.py:796` stays byte-unchanged.

⚠️ **A live dependency this proposal does not own.** `AI-E17-3` records that **no CI evidence exists
at any sha in Epic 17**: `origin/docs/merge-strategy-decision` is `[gone]`, `origin/master..HEAD` is
33 commits, and `audit-ci.yml` fires on `master`/`main` only, `ubuntu-latest`, Python 3.10/3.11/3.12.
Every gate figure this repository quotes has been observed on **one Windows machine**. Epic 19 would
add guards to the same unvalidated tree. **This is not solved by Epic 19 and should be taken first.**

---

## 3. Recommended Approach

### 3.1 Selected path: **Hybrid** — Option 1 (add an epic) gated in front by two operator acts

| Option | Verdict |
|---|---|
| **1 — Direct Adjustment** | ⚠️ **Viable only as an epic addition.** No open epic exists to add a story to. Effort: Medium. Risk: Low. |
| **2 — Rollback** | ❌ **Not viable.** Nothing is wrong with the delivered work. 17.4's `UNEVALUABLE` was the *correct* output of a correctly frozen fold. Rolling anything back would destroy evidence and unblock nothing. |
| **3 — PRD MVP Review** | ❌ **Not viable as a remedy, and rejected on principle.** Reducing the gate's scope until it evaluates is Story 12.1's named anti-pattern (*narrowing the population until it goes green*). The gate should stay where it is and stay `BLOCKED` until real evidence moves it. |

**Justification.** The blocking prerequisites are *acts*, not *code*. An epic of dev stories placed in
front of an unperformed operator act buys a second `UNEVALUABLE` — which is precisely what `AI-E17-4`
warns against. So the sequencing is inverted from the normal loop: **the operator acts come first and
the dev stories are built to stop at them**, each producing the package the human needs and then
halting, in the shape Story 13.1's ESCALATION and 17.4's HALT already established.

### 3.2 `AI-E17-8` — **fill the role; do NOT pre-record a stuck-pair rule**

`AI-E17-8` offers two legs. **The analysis says they are not equally available, and the retrospective
did not distinguish them.**

- **Filling the External adjudicator is a HOLDER-CELL change** — a **dated block under V1.3, adding
  no change-log row**, exactly as the 2026-08-22 block that filled the QA Lead and the 2026-08-23
  block that derived independence. Two precedents, both clean. §2 already permits *"for V1 this MAY
  be a third internal reviewer"*.
- **Pre-recording what a stuck pair does is a METHOD change to §4's ladder** — which requires a
  **V1.4 change-log row**, which **re-stamps `protocol_version` across the 31 committed judgements of
  2026-08-17**. That is the act §3.4 forbids and the locked operator decision of 2026-08-20 names:
  *"a decision folded across an amendment is a re-interpretation of judgements nobody re-made."*
  `refuse_protocol_drift()` would additionally refuse any constant that is not the change-log head.

**Recommendation: fill the role with a named third internal reviewer, in its own dated act, BEFORE
Story 19.4 is drafted** — never during an adjudication, per the 2026-08-22 discipline (*"a role
filled mid-adjudication is a role filled to unblock a result, and would be indistinguishable, on the
record, from a role filled to obtain one"*). ⛔ This buys V1 tie-break capacity only; it makes **no**
claim of independence for an externalization sign-off, where §2's *"SHOULD be outside the implementing
team"* bar is untouched.

### 3.3 `AI-E17-7` — widen from 7 to 46, and pair every container with a registry shrink

Give the six `"17-5"` entries and `DF-AUD-DETECT-C` a destination in Story 19.6, and **measure the 43
`"unverified"` pairs in the same pass** — they are the same defect, unmeasured. ~~`bmad-loop-sweep`
already exists to produce exactly this partition and should be used rather than re-derived.~~

> ⛔ **CORRECTED 2026-08-26, SAME DAY, BY MEASUREMENT — the struck sentence above is FALSE (§3.4:
> struck, never erased).** Found while contexting Story 19.6 at `3696e44`. `bmad-loop-sweep`
> triages `### DW-<n>:` blocks carrying a `status:` line. **This ledger holds ZERO of them,
> against 166 `- id: DF-` blocks.** The skill is also automation-only — it refuses to run unless
> `BMAD_LOOP_MODE=1` — and its `--migrate` mode would rewrite `deferred-work.md` into a format
> that `tests/test_governance_record_integrity.py`, **the only guard that parses this file**,
> cannot read. ⛔ **Do not run it. Do not migrate.**
>
> **What produces the partition instead:** the guard's own exported analyzers —
> `done_story_keys`, `ledger_target_pointers`, `is_affirmative_target`, `named_done_stories`,
> `stale_target_pointers`. Every figure in this document's §1 came from them, and Story 19.6's
> §0.1 reproduces all of them unmoved. That is the one derivation; there is no second one to
> reach for.
>
> ⚠️ **A second thing this section understated.** The registry's only clean exit is a pair
> moving to `_DISPOSING_STORY_POINTERS` with three-way evidence. Rewriting a `target_story` is
> forbidden for the six `"17-5"` entries by §3.4, and `target_story: NONE` is forbidden by the
> registry's own comment. **The shrink named in §5's success criteria is therefore an OUTCOME of
> the evidence and never a target, and a shrink of zero is an acceptable result.**

### 3.4 ⛔ Open question the operator must rule on before 19.2 starts

**Does ratifying already-manifested sealed bench members under §6 R2 spend `DF-13-5-A`'s one
pre-registered bench-expansion round?** The entry has been DECLINED twice (2026-08-24, `7edf74e`) and
is **OPEN and UNSPENT**. Ratifying members already in the manifest is arguably *not* an expansion —
but it is close enough that this document **will not decide it by implication**. A dated ruling is
required, either way, before Story 19.2 is taken.

---

## 4. Detailed Change Proposals

### 4.1 `epics.md` — append Epic 19

```
## Epic 19: Give The Operator Acts A Container — then let the fold decide · *Argus repo*

**Covers:** AI-E17-4, AI-E17-8, AI-E17-7, AI-E16-7, AI-E16-1
**Charter:** Epic 17 froze a criterion and measured it once, and the measurement returned
UNEVALUABLE because two blocking prerequisites are OPERATOR ACTS with no container. This epic is
that container. It does NOT promote a successor predicate, and it may end with NOT_MET.
```

⛔ **The `Covers:` list is re-derived from `deferred-work.md` on disk at roll-up, per `AI-E17-13`**,
before `epic-19: done` may be written — the rule Epic 17's own falsified header produced.

### 4.2 Proposed stories

| # | Story | Kind | Stops at |
|---|---|---|---|
| **19.1** | *The ratification package the operator cannot rule without* — for each of the 6 sealed members: pinned sha, licence, language, size, and the finding count the shipped detector produces at that sha, in one worksheet | autonomous | the operator act; ratifies nothing, fetches nothing |
| **19.2** | **⛔ RATIFY SEALED MEMBERS** — flip `eligible_for_n` for the members the operator admits | **OPERATOR ACT** (§6 R2) | — |
| **19.3** | *The successor-class adjudication worklist* — run S1 over the ratified-and-sealed population, emit `UNADJUDICATED` rows with locators | autonomous | cannot write a disposition — construction raises |
| **19.4** | **⛔ ADJUDICATE THE SUCCESSOR-CLASS SAMPLE** — Engineering Lead + QA Lead, tie-break available | **NAMED-HUMAN ACT** (§4) | — |
| **19.5** | *Re-run the frozen fold and let it decide* — no re-freezing, no re-derivation of the criterion | autonomous | records `MET`/`NOT_MET`/`UNEVALUABLE` **whatever it is** |
| **19.6** | *Every ledger entry has a container or a dated deferral* — the 6 + `DF-AUD-DETECT-C` + the 43 unverified | autonomous + operator rulings | registry shrinks by exactly what gets one |

⛔ **19.5 may return `NOT_MET`, and that is a success of this epic, not a failure.** An epic that can
only succeed by producing a passing number is the artifact Epic 13 exists to make impossible.

### 4.3 `sprint-status.yaml`

Add `epic-19: backlog`, the four autonomous story keys at `backlog`, and **19.2 / 19.4 under a status
that is visibly not `backlog`** — proposed `operator-act` — so the dev loop cannot pick them up. If a
new status member is unacceptable, the alternative is to omit them from `development_status` entirely
and carry them as dated action items; **what is not acceptable is filing an operator act as
`backlog`.**

### 4.4 `precision-validation-protocol.md`

One **dated block under V1.3**, naming the External adjudicator holder and date. **No change-log row.
No byte of §1–§7 edited.** This is the sixth such block.

---

## 5. Implementation Handoff

**Scope classification: MAJOR** — a new epic plus two protocol-level operator acts. Routed to
**Product Manager / Solution Architect**, not to a developer.

| Act | Owner | Sequence |
|---|---|---|
| Rule on `DF-13-5-A` (§3.4) | XAgent007 (Governance Owner) | **first — blocks 19.2** |
| Name the External adjudicator | XAgent007 (Engineering Lead) | **before 19.4 is drafted** |
| Approve Epic 19 + file it | XAgent007 + Architect | after the two rulings |
| Take the CI/merge decision (`AI-E17-3`) | XAgent007 | **independent, and overdue** |
| Draft 19.1 / 19.3 / 19.5 / 19.6 | `bmad-sm` → `bmad-dev` → `bmad-review` | after filing |

### Success criteria

1. Every one of `AI-E17-4`, `AI-E17-8`, `AI-E17-7` carries **either** a container **or** a dated
   acceptance naming who accepted it. *Both are acceptable outcomes.*
2. `_POINTS_AT_DONE_AT_LANDING` shrinks by exactly the entries that gained a container — no mass
   re-homing (`AI-E12-3`), no narrowing to green (Story 12.1's anti-pattern).
3. The fold is re-run once and its outcome recorded **whatever it is**.
4. `protocol_cleared` remains `False` unless all four §5 conditions genuinely hold.

### ⛔ What approving this proposal does NOT authorise

Spending `DF-13-5-A`. Ratifying any member. Writing any disposition. Editing any protocol byte
outside the §2 dated block. Promoting S1 out of ADVISORY. Moving any threshold.
