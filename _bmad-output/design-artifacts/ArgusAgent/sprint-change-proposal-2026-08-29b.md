# Sprint Change Proposal — 2026-08-29b

**Facilitator:** Amelia (Developer) · **Project Lead:** XAgent007 · **Project:** ArgusAgent
**Workflow:** Correct Course (`bmad-correct-course`) · **Mode:** Incremental
**Measured at HEAD:** `e9a8c1e` · **Status:** APPROVED 2026-08-29
**Supersedes nothing.** Second proposal of 2026-08-29; `sprint-change-proposal-2026-08-29.md`
(the PRECISION/`UNEVALUABLE` proposal) is untouched and unaffected by this one.

---

> ## ⛔ READ FIRST — WHAT THIS DOCUMENT DOES NOT DO
>
> It clears, softens, promotes and re-scopes **NOTHING** on the verdict or precision surfaces.
> `PRECISION_GATE_THRESHOLD` stays `4/5`, `VALIDATION_SET_FLOOR_N` stays 5, `INSTRUMENT_STATUS`
> stays `NOT_INDEPENDENTLY_VALIDATED`, `protocol_cleared` stays `False`, no corpus member is
> ratified or re-weighted, no finding's `verdict_eligible` moves, and `DF-13-5-A`'s one round
> stays UNSPENT. **No `argus/` byte changes.** No FR or NFR is amended, added or removed. No
> schema, no verdict, no shipped contract.
>
> It also **does not reopen Epic 20** and changes **no story status** under it.
>
> ⚠️ It does **not** make any advisory mechanism blocking — that exit is explicitly closed below.

---

## 1. Issue Summary

### 1.1 What triggered this

Two signals were brought to the workflow, and measurement showed them to be **one issue with two
symptoms**:

1. **Epic 20's reach gap.** All four stories (20.1–20.4) delivered `done`, and none of the three
   capabilities they built is reachable by any operator.
2. **Epic 17's unwritten process items.** `AI-E17-9`, `-10`, `-11`, `-13` — three of them `high`
   priority, two of them on their **THIRD raise** — all still `open`, all owned by the loop or the
   Architect rather than by any story, so no story would ever pick them up.

### 1.2 The core problem — stated precisely

**Issue type:** misunderstanding of a governing rule's *operational* requirements — not, as the
Epic 20 retrospective frames it, a delivery failure.

The reach gap is **real and already fully disposed in every artifact**. The PRD amended FR38/FR39/
FR40 to `library-seam` on 2026-08-28; the ledger filed `DF-20-1-A`/`-2-A`/`-3-A` with a recorded
prior-art grep; `architecture.md` §J was added; the retrospective's headline answer was struck and
corrected in place. **Nothing in that record needs fixing.**

The live problem sits **upstream** of it:

> **An ADVISORY report that no named party reads at a named moment is not a control.**
> `scripts/check_meta_drift.py` has flagged every epic the anti-drift rule has ever bound. It was
> right every time. Nothing read it. Epic 20's seed carried **no `Capability delivered:` field at
> all**, so nothing forced the honest entry — *"nothing a user can reach"* — **at seed time**. Had
> CD-2 been read when that seed was written, the reach gap surfaces **before four stories were
> built**. Instead it surfaced at retrospective, after.

The reach gap is the **symptom**. The unconsumed advisory signal is the **cause**.

### 1.3 Evidence

**(a) The reach gap — measured, not read.** At HEAD `e9a8c1e`:

- `grep` for importers of `argus.remediation`, `argus.adapters.lsp`, `argus.parsers` anywhere else
  in `argus/` → **exit 1, zero hits**.
- **No** `argus/cli.py` reference to any of the three.
- `[project.scripts]` is `argus` / `argus-agent` / `repo-audit` → `argus.cli:main`, plus the FR35
  MCP alias. **Nothing else.**

**(b) The cause — the rule has been breached by every epic it has ever bound.** Produced by running
`scripts/check_meta_drift.py` on 2026-08-29:

| Epic | stories | product-traced | process-traced | share | budget | seed fields |
|---|---|---|---|---|---|---|
| 17 | 5 | 1 | 4 | 80% | 20% | both present |
| 18 | 4 | 1 | 3 | 75% | 20% | both present |
| 19 | 6 | 0 | 6 | 100% | 20% | `Covers:` names no FR/NFR driver |
| 20 | 4 | 0 | 4 | **100%** | 20% | ⛔ **no `Capability delivered:` field at all** |

**Four for four over budget. Not one recorded a response.** Epic 20's 100% is the worst
process-derived share on record — the prior high-water mark was Epic 16 at 86%.

Verbatim reporter output for Epic 20, before any correction:

```
!!Epic 20  stories=4   product-traced=0   process-traced=4   (100%, budget 20%)
    !!**Covers:** names no FR/NFR driver — the epic seed traces to process provenance only
    !!epic seed carries no **Capability delivered:** field
```

**(c) The Epic 17 items are genuinely unwritten — verified, not assumed.**

| Item | Claim | Measured at HEAD `e9a8c1e` |
|---|---|---|
| `AI-E17-10` | staging protocol "written nowhere" (3rd raise) | ✅ no `explicit-path` / `git add -A` / byte-invariant text anywhere in `architecture.md` §Enforcement |
| `AI-E17-11` | two-pass not a named phase (3rd raise) | ✅ no `two-pass` / `Task 0` in `architecture.md`; absent from `bmad-dev-loop/SKILL.md` |
| `AI-E17-13` | no `Covers:` re-derivation at roll-up | ✅ `SKILL.md:225` — roll-up writes `epic-<id> = done` **and nothing else** |
| `AI-E17-9` | no docs-only fix-round lane | ✅ `SKILL.md:96-100` caps at 3 with **no** finding-class distinction |

⛔ **`AI-E17-13` would not have saved Epic 20.** It re-derives an epic's `Covers:` list; Epic 20
had **no `Covers:` line to re-derive**. Only CD-2 catches a *missing* field. Both are needed;
neither substitutes for the other.

**(d) Why "make it blocking" is not the remedy.** The ADVISORY disposition is a **locked decision
with recorded evidence**: a blocking prose-parser produces false failures that abort legitimate
work, and `TC-ArgusAgent-DOCS-001-78` went RED three times from prose in a single day
(`epic-14-retro-2026-08-18.md` §3.4). **The mechanism was correct and unread. It is the reading
that is missing, not the red light.**

---

## 2. Impact Analysis

### 2.1 Epic Impact

| # | Finding |
|---|---|
| **Epic 20** | `done` and closed with its retrospective. **NOT reopenable and not reopened.** Its seed is retrospectively non-conformant and receives a dated in-place correction in the §3.4 struck-not-deleted form — the same form Story 17.5 used on Epic 17's header. No story status changes. |
| **Remaining epics** | **None exist.** Epic 20 is the last epic in `epics.md`. |
| **Backlog** | **Empty.** `sprint-status.yaml` has three non-`done` items, all `AI-E10-*` human-decision rows — none is a story. |
| **Resequencing** | N/A — nothing to resequence. |
| **New epic** | **Required.** All new work lands in a new **Epic 21**; FR38/FR39/FR40 have no other home (`target_story: NONE — unscheduled` for all three). |

⚠️ **The empty backlog makes this a uniquely cheap moment to fix the rule** — there are no
downstream epics to disturb — and it is also the **last** such moment before the next delivery epic
is planned under a rule that has never once been enforced.

### 2.2 Artifact Conflicts

| Artifact | Verdict | Detail |
|---|---|---|
| **PRD** (`E-PRD/prd.md`) | ✅ **No conflict — DO NOT EDIT** | FR38/39/40 already amended, disposed `library-seam` and cross-referenced 2026-08-28. MVP untouched: all three are `[Post-V1]`; the V1 sentence still binds every unmarked item. |
| **Architecture** | `[!]` Action-needed | §Enforcement lacks the `AI-E17-10` staging protocol and the `AI-E17-11` named two-pass phase. §J (FR38–40) is correct as written. |
| **UI/UX** | `[N/A]` | No UX artifact — headless CLI/MCP. "No IDE plugin" already restated precisely at `prd.md:452`. |
| **`epics.md`** | `[!]` Action-needed | Epic 20 seed missing both required fields; new Epic 21 seed needed. |
| **`bmad-dev-loop/SKILL.md`** | `[!]` Action-needed | No CD-2 read point, no roll-up `Covers:` verdict, no docs-only fix-round lane. |
| **`deferred-work.md`** | `[!]` Action-needed | Cause finding not filed. |
| **`sprint-status.yaml`** | `[!]` Action-needed | Epic 21 entries; `AI-E17-*` status flips. |
| **`tests/test_status_document_registry.py`** | `[!]` **Action-needed** | `TC-ArgusAgent-DOCS-001-22` is closed over `sprint-change-proposal-*.md`. **This document must be registered in the same commit that adds it** — `-22` closes in BOTH directions. |

### 2.3 Technical Impact

**Zero `argus/` bytes.** No code, no schema, no verdict surface, no CI pipeline, no deployment
artifact. Every change lands in planning artifacts, the dev-loop skill, and one registry test.

### 2.4 Byte invariants (re-measured 2026-08-29 at HEAD `e9a8c1e`)

| File | Working tree | Note |
|---|---|---|
| `epics.md` (3931), `architecture.md` (1442), `sprint-status.yaml` (1434) | **CRLF-uniform** | 0 lone CR |
| `deferred-work.md` | **LF-only + exactly ONE lone CR** | `grep -n` line **5573**, inside a backtick literal — **prose content describing CR/LF, not stray whitespace.** Must survive byte-exact. |
| `bmad-dev-loop/SKILL.md` | LF-only | 0 lone CR |
| `tests/test_status_document_registry.py`, this document | CRLF-uniform | — |

⛔ **The lone CR makes `grep -n` (8516 lines) and `splitlines()` (8517) disagree by exactly 1 for
every line after 5573.** All ledger citations in this document are **`grep -n`**. This is not
theoretical: during this very session a Python `read_text()` call silently translated that CR under
universal-newline handling and reported every tail line one higher, until it was caught by
cross-checking against `grep -n`.

⚠️ **`core.autocrlf` makes the working tree CRLF while every committed blob is LF.** A measurement
must name which view it took.

---

## 3. Recommended Approach

**Selected: Option 1 — Direct Adjustment, scoped to the CAUSE rather than the symptom.**
Approved by XAgent007, 2026-08-29.

| Option | Verdict | Reason |
|---|---|---|
| **1. Direct Adjustment (cause-scoped)** | ✅ **SELECTED** · Effort **Medium** · Risk **Low** | Fixes the unconsumed signal, discharges four action items proven in execution, corrects the non-conformant seed. Touches no `argus/` byte and no shipped contract. |
| 2. Direct Adjustment + wire one capability | ❌ Not taken · Effort High · Risk **Medium** | The FR29/FR23 precedent shows CLI-surface work lands in `pipeline.py`, measured **1331 lines against the NFR-M1 cap of 1200** and byte-fenced to Story 12.1. Wiring a surface before that gate lifts repeats the fence that has held FR23/FR24/FR26/FR29 since 2026-08-11. |
| 3. Rollback (remove unreachable code) | ❌ Not taken · Effort Medium · Risk Medium | Discards built, typed and tested work that the PRD explicitly seeds into a V2 developer-surface roadmap item. FR40's removal exit stays open and unscheduled on its own terms. |
| 4. MVP / scope review | ❌ Not taken · Effort High | The V1 line is not in question. This would re-derive conclusions the 2026-08-28 amendment already reached. |

**Timeline impact:** none to any shipped commitment. Epic 21 is planning-artifact work on an empty
backlog.

**Risk of NOT doing it:** the next delivery epic is planned under a rule that has been breached
four times out of four with no response, and the mechanism that would say so still has no reader.

---

## 4. Detailed Change Proposals

All five were reviewed individually in Incremental mode and **approved** by XAgent007.

### 4.1 `epics.md` — Epic 20 seed correction

Dated in-place correction, §3.4 struck-not-deleted form. Goal line struck and corrected to *"build
the three mechanisms as library seams"*. Adds:

- `**Capability delivered:**` — ⛔ **"NOTHING A USER CAN REACH"**, with the HEAD `e9a8c1e`
  measurement, the `library-seam` dispositions and the three `DF-20-*` ids. `Nothing` is entered
  under the dated operator ruling of 2026-08-29 (this document), as §Enforcement requires.
- `**Covers:**` — FR38 (20.2) · FR39 (20.3) · FR40 (20.1).
- A ⛔ correction block **freezing the pre-correction reporter output verbatim**.

⚠️ **Stated rather than slipped past:** the `Covers:` line is true but **retroactive** — FR38/39/40
were admitted to the contract on 2026-08-28, after the seed was written — and adding it **will flip
Epic 20 to product-traced in the next report.** That is **not** the breach being cured. The frozen
verbatim output is what keeps the flip auditable. `meta-drift-baseline.md`'s warning stands: **a row
may never be added to silence a finding.**

### 4.2 `architecture.md` §Enforcement — three new rules

Pure append after line 1174, before `## Project Structure & Boundaries`. **No existing rule is
modified**, so the in-progress `AI-E10-5` closure-over-enumeration edit can land independently.

1. **Shared-tree staging enforcement** (`AI-E17-10`, 3rd raise). Explicit-path staging, never
   `git add -A`; carried peer files disclosed **by name** in the commit message; byte invariants
   re-measured before and after every write. Evidence: 5 of 5 Epic-17 stories, disclosure used
   twice (`DN-17-2-11`, `DN-17-4-19`) and independently verified by reviewers with `git show
   --stat` / `git diff` — **zero collisions across 33 commits, against three inside Story 16.7
   alone.** Includes the working-tree/blob split and the `grep -n` ↔ `splitlines()` divergence.
2. **Premise re-measurement enforcement** (`AI-E17-11`, 3rd raise). A **named phase** with a
   **three-outcome verdict form** — `reproduced` | **`A ROW MOVED`** | `could not measure` — where
   `A ROW MOVED` is first-class and **REPORTED, never absorbed**. Evidence: practised 5 of 5,
   found real drift in 4 of 5; 17.5 corrected its own SM on three figures (52/18 vs 47/23; 28
   blocks/26 ids vs 24/23, against a going-in assumption of *"six"*) and found two missed ledger
   ids (`DF-8-3-B`, `DF-14-3-H`). `DF-16-5-A` **predicted `DF-14-3-H` going stale and it went
   stale anyway, because nothing was watching.**
3. **Advisory-signal consumption enforcement** (the cause). Every advisory mechanism must name
   **who** reads it, **when**, and **where the verdict is recorded**; an accepted finding is
   recorded as **ACCEPTED with a reason**, never left silent. ⛔ Explicitly does **not** grant any
   advisory mechanism blocking power.

### 4.3 `bmad-dev-loop/SKILL.md` — three sub-changes

- **3a · §3 epic ENTRY + ROLL-UP.** Entry: seed must carry both fields (or `Nothing` + dated
  ruling) → else **HALT**; plus a recorded `META-DRIFT:` verdict. Roll-up: **re-derive every
  `Covers:` id against its on-disk status** and record a per-id verdict before `epic-<id> = done`;
  an unmet list forces a dated §3.4 correction. *(Evidence: Epic 17's header named six ledger ids
  and **none of the six was delivered — all six are still open**, caught only because one story
  happened to be chartered to look.)*
  ⛔ **Deliberate asymmetry:** entry **HALTs** on missing fields (a mechanical, unambiguous fact);
  the `check_meta_drift.py` read **never** HALTs (its predicates read prose and judge). That split
  is what keeps the locked ADVISORY decision intact.
- **3b · §4 fix loop.** `exec_iteration` and `docs_iteration` counted **separately**, each capped
  at 3. DOCS-ONLY iff every file named is non-executable; **a mixed round counts as EXECUTABLE.**
  *(Evidence: Story 17.5 spent all three rounds — the last labelled "LAST PERMITTED FIX ROUND" —
  on **Low, docs-only** findings. Every outcome was right, but the epic's most document-heavy story
  burned its entire safety margin on prose form, so a genuine defect at iteration 3 would have had
  nowhere to go.)*
- **3c · Operating notes.** Roll-up write permission extended to the `Covers:` correction; explicit
  staging and byte-invariant re-measurement added as standing notes.

### 4.4 `deferred-work.md` — `DF-DRIFT-UNREAD-A`

New dated section appended at end (`grep -n` 8516). Records the four-epic breach table, names
itself the **cause** behind `DF-20-1-A`/`-2-A`/`-3-A`, closes the "make it blocking" exit with its
evidence, and carries the six mandatory CC-3 fields.

**Prior art, grepped before filing** (`check_meta_drift`, `meta-drift`, `anti-drift`, `CD-2`,
`RD-1`, `Capability delivered`, `advisory`, `unread`): **one hit, `grep -n` 8062**, in §(e), a
table row recording that Epic 17's `Capability delivered:` claim was **false**. That is a
**different** defect — a *present* field making an *untrue* claim; this entry records a field
**absent entirely** and a finding **read by no one**. Cited, not duplicated; that entry stays open
on its own terms.

⚠️ **Id reconciliation:** first drafted as `DF-21-1-A`, changed to **`DF-DRIFT-UNREAD-A`** because
`origin_story` records where a finding was *discovered* — a correct-course, not a story that does
not yet exist. Follows the `DF-INV-VACUOUS-A` / `DF-AUD-APAA-C` precedent.

### 4.5 New Epic 21 (`epics.md` + `sprint-status.yaml`)

**Epic 21: Give The Advisory Signal A Reader — write down what is already proven.**

| Story | Delivers | Discharges |
|---|---|---|
| 21.1 | Two §CD-2 consumption points + roll-up `Covers:` verdict | `DF-DRIFT-UNREAD-A`, `AI-E17-13` |
| 21.2 | Staging protocol + premise re-measurement phase in §Enforcement | `AI-E17-10`, `AI-E17-11` |
| 21.3 | Fix-round budget split by finding class | `AI-E17-9` |
| 21.4 | Epic 20 seed corrected in place; loop closed | — |

`sprint-status.yaml`: six new keys after line 548 (`epic-21: backlog`, four stories `backlog`,
`epic-21-retrospective: optional`). `AI-E17-9`/`-10`/`-11`/`-13` flip `open` → `in-progress` with a
comment naming the targeting story.

⛔ **`AI-E17-12` stays `open` and untouched** — it is `record-only`, deliberately unassigned, and
closing it would be a bookkeeping lie.

> ### ⚠️ EPIC 21 IS ITSELF 100% PROCESS-DERIVED, AND SAYS SO BEFORE THE REPORTER DOES
>
> stories=4, product-traced=0, process-traced=4 — **the same shape as Epic 20**, and the exact
> metric this correction exists to fix. It is nonetheless rule-conformant **by the rule's own
> words**: *"work over budget is scheduled as a named corrective epic, not forbidden."* Epic 21
> **is** that named corrective epic, and it carries the dated operator ruling §Enforcement
> requires. Its `Capability delivered:` is an honest **`Nothing`** — making it the **first epic
> ever measured against the new step-0 gate, which it passes by declaring rather than omitting.**
>
> ⛔ **It sets no precedent for a delivery epic.** The next non-corrective epic is held to 20%.

---

## 5. Implementation Handoff

### 5.1 Scope classification: **MODERATE**

Backlog reorganization plus governance-rule authorship. It is **not Minor** — it creates an epic,
amends `architecture.md` §Enforcement and changes orchestrator behaviour. It is **not Major** — no
FR/NFR moves, no MVP question is reopened, no architecture decision is overturned, and the PRD is
explicitly untouched.

### 5.2 Routing

| Recipient | Responsibility |
|---|---|
| **Product Owner / Scrum Master** | Epic 21 seed into `epics.md`; `sprint-status.yaml` keys; `AI-E17-*` status flips. Story 21.1 first — it installs the gate the rest are measured by. |
| **Architect** | The three §Enforcement rules (4.2). ⚠️ Sequence against in-progress `AI-E10-5`, which edits the same section: land both, or leave 10-5 untouched and re-measure. |
| **Developer (dev-loop maintainer)** | `SKILL.md` 3a/3b/3c; `DF-DRIFT-UNREAD-A`; the Epic 20 seed correction. |
| **XAgent007 (Governance Owner)** | Owns the two `Nothing` rulings (Epic 20's and Epic 21's) that this document dates. **Retains the three unscheduled FR38/FR39/FR40 decisions — none is resolved here.** |

### 5.3 Success criteria

1. `scripts/check_meta_drift.py` still **exits 0** and is still ADVISORY — a test asserts the
   advisory path never blocks.
2. `bmad-dev-loop` HALTs on an epic seed missing `Capability delivered:` — demonstrated RED against
   a seed with the field removed, GREEN on the live tree.
3. Roll-up emits a per-id `Covers:` verdict read from disk before any `epic-<id> = done`.
4. `architecture.md` §Enforcement carries all three rules; one story cites each rather than
   re-deriving it.
5. `AI-E17-9`, `-10`, `-11`, `-13` reach `done` against their stated destinations.
6. **`TC-ArgusAgent-DOCS-001-22` is GREEN** with this document registered.
7. Byte invariants hold: `deferred-work.md` still LF-only with exactly one lone CR at 5573; the
   CRLF-uniform artifacts still 0 lone CR.

### 5.4 What is deliberately left open

- **FR38 / FR39 / FR40 remain `library-seam`, `target_story: NONE — unscheduled`.** This proposal
  schedules none of them. FR40's two exits — wire it to an API the indexer does not expose, or
  remove it — both stay open and unchosen.
- **`DF-10-2-A` remains OPEN.** C, C++, Ruby and Rust still extract zero definitions; Epic 20
  closed nothing there, and neither does this.
- **`AI-E10-1`, `-2`, `-4`, `-6`** are untouched human decisions.
- **`AI-E17-12`** stays `record-only` and unassigned.

---

## 6. Approval

**Reviewed incrementally and approved by XAgent007 on 2026-08-29**, edit by edit — all five edit
proposals approved (`a`), with the `DF-21-1-A` → `DF-DRIFT-UNREAD-A` reconciliation adopted at
Edit 4 and the Epic 20 `Covers:` retroactivity accepted with the pre-correction reporter output
frozen verbatim.

**Approval is ATTRIBUTED in-session, not cryptographically signed** — stated about itself rather
than smoothed over, following the form of `sprint-change-proposal-2026-08-29.md` §6.
