# Epic 13 Retrospective — INTERIM — Earn the Gate: remove the disclosure by measuring, not by deleting (Argus repo)

**Date:** 2026-08-17 · **Facilitator:** Amelia (Developer) · **Project Lead:** XAgent007
**Epic:** 13 — *Earn the Gate* · **Stories:** 2 of 3 `done`, 1 `ready-for-dev` and BLOCKED · **Retrospective:** ⚠️ **INTERIM — NOT the epic's retrospective**
**Mode:** generated autonomously by the `bmad-dev-loop` orchestrator's retrospective worker. The stock workflow's party-mode WAITs were **not** performed — there was no user in the session. Every section below is synthesised from the evidence on disk, and every figure is either attributed to the agent who measured it or re-measured in this session and marked as such.

---

> ## ⛔ THIS IS AN INTERIM RETROSPECTIVE. IT DOES NOT CLOSE EPIC 13.
>
> **It covers Stories 13.1 and 13.2 only.** Story 13.3 — *Record the result, and let it decide*, the
> story that computes the four protocol §5 conditions and therefore the only story that can change the
> tool's stated status — is `ready-for-dev` and **blocked on one human act that has not happened**.
>
> **The decisive story of this epic has not run.** Any conclusion drawn here about whether Epic 13
> achieved its purpose is therefore **unavailable**, not merely provisional. `epic-13-retrospective` is
> written to an **in-flight** value in `sprint-status.yaml`, deliberately not `done`, so that the
> dev-loop cannot later roll `epic-13` up to `done` on the strength of a retrospective that never saw
> the epic's decisive story. **A FINAL pass is required after 13.3 completes** — see §11 for exactly
> what it must cover that this document cannot.
>
> **The epic's stated purpose, quoted:** *"The ≥80% finding-precision gate is cleared on evidence, or it
> is recorded as **not cleared** and the disclosure stays … **It is the only work in this plan that can
> remove the tool's provisional status, and it is not a build task.**"* As of this document the
> measurement has **not** been taken and the disclosure **stays**. Nothing in Epic 13 to date has moved
> the gate, and 13.2 went out of its way to make sure it could not.

> **Release status as of 2026-08-17: NOT ESTABLISHED for publication purposes.** Re-measured live in this
> session, read-only: `git tag -l` returns nothing, `gh release list` returns nothing, `gh repo view`
> reports `PRIVATE`, and `pyproject.toml` carries `version = "0.1.0"`. `DF-12-9-A` act (1)
> (`git push origin master`) is performed and `origin/master` is `b04dc1a`; acts (2)–(5) are
> **UNPERFORMED**; act (6) is `DN-2` and act (7) is `DN-1`, out of scope.

> **Reading rule inherited from Epics 8–12, and it binds this document too.** Where a figure was
> measured by a dev or a reviewer and not re-run here, it is attributed to them. Where it was
> re-measured in this session, it says so. No figure in this document is copied from a plan.

---

## 1. Epic Summary & Delivery Metrics

| | |
|---|---|
| **Stories `done`** | 2 of 3 — 13.1, 13.2 |
| **Stories blocked** | 1 — 13.3, `ready-for-dev`, blocked on `DF-13-2-A` |
| **Review iterations** | 13.1: 2 (9 findings, 1 dismissed, 8 resolved, 0 deferred, 0 loosened) · 13.2: 1 (clean PASS, no High/Medium) |
| **Gate movement** | **None.** `protocol_cleared` is `False` and has never been `True` anywhere in `argus/**` — re-verified this session by grep over the package |
| **Protocol §5 conditions met** | **1 of 4.** N = 5 ≥ 5 holds (13.1). ≥80% precision is **UNEVALUABLE**; clean-repo blocking-FP is **NOT APPLICABLE** with its reason recorded; no adjudication run is recorded |
| **Adjudication record** | 31 rows, **31 `UNADJUDICATED`**, zero judgements, `adjudicator` `null` on every row, `expert_hours` `null` ("NOT RECORDED", never zero), `protocol_version` `V1.3` — re-parsed this session |
| **Local suite** | 1585 passed / 0 failed / 0 skipped (Windows, attributed to the 13.2 dev and re-confirmed by the 13.2 reviewer) |
| **CI** | Green on `b04dc1a`, both workflows, all three legs — 1581 passed / 4 skipped per leg. Run `31986854738` at sha `b04dc1a` |
| **Outward-facing acts** | Two pushes to `origin/master` (`ae54234`, `b04dc1a`). No tag, no release, no visibility change |

**What the epic actually delivered, stated precisely.** 13.1 decided *what the validation set is* — the
PRD governs, cartridges are re-labelled as the FR20 **recall** instrument, the architecture's last OPEN
input is closed by decision at all three sites — and then built it: **N = 5 repositories, all five
byte-reproducible across two runs, 31 blocking findings**. 13.2 built the **instrument** that turns those
31 findings into a precision figure: a committed, append-only, machine-readable adjudication record with a
closed vocabulary that raises on a malformed disposition, an exhaustiveness fold, a determinism
precondition evaluated *before* the ratio, and protocol V1.3 deciding that the unit of adjudication is the
**finding**.

**What it did not deliver, by design.** The **judgement**. 13.2's AC7 is the human act, and the story
halted there rather than supplying it. That is the correct outcome and it is examined in §2.1.

---

## 2. What Went Well

### 2.1 The instrument/judgement separation held under pressure — this is the epic's best result so far

The single most consequential thing that happened in Epic 13 is something that *did not* happen: **no
agent supplied a judgement in order to make a gate computable.**

The pressure was real and specific. 13.2 delivered a fold that returns `Unevaluable` with residual 31; a
guard that goes red on an unadjudicated record; and a story whose AC7 could only be marked complete by a
human. Populating 31 dispositions would have made every downstream guard go green — and, as `DF-13-2-A`
records in its own words, *"would clear the externalization gate on evidence that does not exist, and every
guard downstream — including Story 13.3's — would agree that it had."* The ledger entry names the
temptation and refuses it in the same paragraph.

**Why this is not merely compliance.** The 13.2 code review (Sonnet, three adversarial layers, no shared
context) independently re-parsed the record and confirmed 31 rows, 100% unadjudicated, `adjudicator` null
on every row — *"matches the dev's claim exactly"* — and then ruled AC7's HALT a **legitimate designed
terminal state** rather than an unmet AC waved through, on the ground that the story's ESCALATION section
designed the outcome **before** dev-story ran. This project has now produced two independent instances of
the same discipline (12.9/AC9 and 13.2/AC7), and the second is the stronger of the two: 12.9 halted on an
act an agent *could* have performed, 13.2 halted on one that is definitionally a human's.

### 2.2 13.2 reproduced three gate-flip defects verbatim before fixing them, and the flip path was reachable without a single adjudicated finding

The three defects, all found by execution during create-story and all reproduced on the implementation sha:

1. **Empty denominator certifies.** A corpus emitting nothing returned `precision = 1/1`, passed the ≥4/5
   threshold and rendered `gate_status → "cleared"` — measured at 0 TP / 0 FP / 8 FN.
2. **Wrong N.** `compute_precision` derived `n` from `populated_planted_defect_count()` and ignored the
   injected registry: a **2-member** population still reported **N = 7 ≥ floor 5**.
3. **Vacuous clean-repo condition.** §5's *"0 clean-repo blocking false positives"* was **vacuous over a
   repository corpus**, because `_is_clean_repo` needs an empty golden key and `max_blocking == 0`.

Composed, those three meant a 2-member corpus that emitted nothing would report **cleared** the moment
`protocol_cleared=True` was passed — and 13.2 is the story that produces the value 13.3 passes. Finding
this *before* the instrument shipped, rather than after a figure was published, is the whole argument for
the §0.1 premise re-measurement discipline.

**All three were closed additively, and additivity was proven, not asserted:** the Epic 6.6 / 7.1 contract
tests (`DOGFOOD-001-11`/`-12`, `PRECISION-001-08`/`-09`) pass **byte-unedited**.

### 2.3 The protocol amendment was checked for loosening by an adversary, and came back tightened

V1.3 amended §1/§2/§3/§4/§5 and decided the adjudication unit. An amendment to the very protocol that
governs the gate, written by the story that will be measured against it, is the most obvious place in this
project for a goalpost to move. It was independently checked and the review's finding is worth quoting in
substance: strike-never-erase preserved; the **N ≥ 5 floor and the 80% threshold literals unchanged**; the
clean-repo condition **not weakened** (made explicit and `NOT APPLICABLE` rather than falsely satisfied);
and the finding-level unit is **stricter** than the rejected per-class alternative — 31 rows versus a
denominator of **one**, because all 31 blocking findings on this corpus are a single rule class.

A per-class fold would have made the gate turn on one judgement. The story chose the harder denominator.

### 2.4 The AI-E12-6 ledger-claim guard landed, found 19 unbacked claims on its first run, and then fired on its own story

`TC-ArgusAgent-DOCS-001-78` — the guard the Epic-12 retrospective ranked #7, *"before 13.2 files its
adjudication record"* — landed inside 13.2 and immediately found **19 unbacked closure claims across 15
story files, out of 47 claims total, spanning Epics 1–12**. It was registered as a **dated, owned,
shrinking** registry rather than an amnesty; two entries were removed the same day.

Then it fired on 13.2's own Completion Notes. The story's record says so in its own voice: *"The guard's
author was its first subject, which is the most useful possible evidence that it is not vacuous."* Against
this project's dominant defect class — vacuous guards — a rule that catches its own author on its first
run is the strongest available non-vacuity evidence, and it was obtained for free.

### 2.5 Four guards went red on 13.2's full run and every one was a guard working

`DOCS-001-46` caught a second unregistered `protocol_cleared=True` test file. `RELEASE-001-11` forced a
deliberate decision about a new module naming the repository-only tree. `DOCS-001-54` caught four stale
published built-artifact figures in `README.md`/`CHANGELOG.md`. `DOCS-001-78` caught its own story.
**None was loosened; none was allowlisted.** Four reds, four real defects, zero threshold movements.

### 2.6 13.1's review found the guard that was enforcing a falsehood

All three review layers independently raised the same HIGH finding: the corpus figure was stale at
**N = 0** in `prd.md`, `precision-validation-protocol.md`, all three `architecture.md` resolution sites and
`DF-13-1-A`, while the manifest returned **5**. The sharpest part is not the staleness — it is that
`TC-ArgusAgent-DOCS-001-75` **required the literal `"N = 0 eligible members"` in `prd.md`**. A guard
written to protect the record was **enforcing the falsehood and holding the suite green**. It now derives
the count from the manifest and was proven red against a planted sixth member.

That is the input-side twin of the vacuous-guard class, caught at the one moment it mattered most.

---

## 3. Challenges & Growth Areas

### 3.1 🔴 A story file turned `master` red, and the loop has no gate that could have caught it — because in this repository story files are TESTED ARTIFACTS

**The sequence, measured.** Dev and Review both finished green (1585 local passes). The **SM phase** then
authored `stories/13-3-record-the-result-and-let-it-decide.md`. **Nothing re-ran the suite.** The commit
(`ae54234`) was pushed. `audit-ci` failed on ubuntu / py3.12: `1 failed, 1580 passed, 4 skipped`, the
failure being `TC-ArgusAgent-DOCS-001-78`. Fixed forward in `b04dc1a`; CI is now green on both workflows,
all three legs.

**The root cause is structural, and it is a property of this repository specifically.** Guards read
`stories/*.md`. `TC-ArgusAgent-DOCS-001-78` globs the stories directory and asserts ≥40 files for
non-vacuity; `TC-ArgusAgent-DOCS-001-22` globs the artifact directory for `epic-*-retro-*.md`. **Story
files and retrospectives are inputs to the test suite.** But the dev-loop's phase order is
Dev → Review → SM(next story), and **the suite gate sits on the two phases that do not write the tested
artifact, not on the one that does.** The gate is on the wrong side of the write.

This is not a near-miss and it is not a one-off: it is the first time the SM phase's write was
*consequential*, and it went straight to `origin/master` because nothing stood between them. **This
document is the second instance** — writing this retrospective into the artifact directory turns
`TC-ArgusAgent-DOCS-001-22` red on landing, for exactly the same reason. That was anticipated and handled
(§3.2), which is only possible because this worker knew to look.

**AI-E13-1.**

### 3.2 🔴 This retrospective is itself a tested artifact, and the registration that keeps it green consumed the last line of headroom in the file that registers it

`TC-ArgusAgent-DOCS-001-22` resolves `epic-*-retro-*.md` against the artifact directory and fails on
anything unregistered. The Epic-12 retrospective **predicted this red about itself** (its §6 SD-3) and
**AI-E12-1's second half** asked for the permanent fix: *"make the registration part of the retrospective
step's own definition of done, so the next epic does not rediscover this."*

**Measured this session, and then performed:** `-22` was confirmed RED against this document before
registration and GREEN after — the registration is one line, and `_status_assertions()` returns **zero**
for this document, so the registration is inert against every other assertion in `-21`. That is
AI-E12-1's second half discharged **in practice** for the first time.

**And it uncovered the next blocker.** `tests/test_evidence_citation.py` measured **1199 / 1200** lines
before this session. The registration puts it at **exactly 1200** — passing, because
`TC-ArgusAgent-MAINT-001-03` pins that 1200 passes and 1201 fails, but with **zero headroom**. **The FINAL
Epic-13 retrospective cannot be registered without splitting that module first.** A step whose definition
of done is now known will be blocked by a ceiling the moment it runs.

Recording this as a challenge rather than a triumph is deliberate: the fix worked, and it worked by
consuming the last unit of a budget nobody was watching.

**AI-E13-2.**

### 3.3 🟠 The guard that fired has a latent sharp edge — and the finding it produced was a FALSE POSITIVE

`story_closure_claims` (`tests/test_governance_record_integrity.py:58-72`) is **line-scoped by design** and
sweeps **every** `DF-*` id on any line carrying a closure verb. Its own docstring states the assumption it
relies on: *"a closure claim and its id are written on the same line in every record this repository has
produced."*

**The 13.3 story wrote a markdown TABLE ROW packing seven ids of mixed disposition onto one line.** The
closure verbs belonged to `DF-8-4-D` / `DF-8-5-C` / `DF-9-2-C`. `DF-8-4-C` was swept in beside them. The
`_NEGATED` pattern recognises *"not closed"*, *"never closed"*, *"cannot be closed"* — it does **not**
recognise *"remain open and unowned by decision"*, which is what that row actually said.

**`DF-8-4-C` was, and remains, correctly OPEN and unowned by decision** — `deferred-work.md:1649-1657`,
re-read this session: *"DF-8-4-B and DF-8-4-C remain open and unowned **by decision**, which is a
disposition, not a drift."*

**The response was correct and should be recorded as such.** The record was reworded to one id per line.
**The guard was deliberately NOT weakened and nothing was allowlisted** — the `_UNBACKED_AT_LANDING`
registry can only shrink, and adding an entry to silence a false positive would have converted a shrinking
registry into a parking lot. Rendered meaning is identical: same seven ids, same dispositions, same dates,
same evidence.

**The residual risk, stated plainly: any future multi-id summary row reproduces this.** And summary rows
are exactly what a retrospective's re-derived open-items list wants to be — this document's §10 is written
one-id-per-line for precisely that reason.

**The decision this retrospective is asked to make, and does not have the authority to take alone:**
whether per-id scoping (each `DF-*` matched against the closure verb nearest it, with a **generated
adversarial variant** proving the narrower predicate can still fire) should be scheduled, or whether the
**one-claim-per-line convention is the ruling**. Both are defensible. Per-id scoping removes a class of
false positives at the cost of a more complex predicate over prose — and this project has already had to
narrow one such predicate away from manufacturing false accusations (12.3's refutation rule, cited in the
guard's own comments). The convention is cheaper and is already written down in 13.3's AC7. **Neither is
chosen here; the item is filed with an owner so it is chosen deliberately rather than by the next
accident.** **AI-E13-3.**

### 3.4 🔴 The precision denominator is concentrated in the one corpus member the record itself calls the least transferable evidence — MEASURED THIS SESSION, recorded nowhere

This was not in any story record, any review, or the ledger. It was found by parsing the committed
adjudication record in this session:

| Corpus member | Blocking findings in the denominator | Share |
|---|---|---|
| `minions` | 24 | 77.4% |
| `agent-smith` | 7 | 22.6% |
| `ai-body-runtime` | 0 | — |
| `agent-markovich` | 0 | — |
| `xagents-webapp` | 0 | — |

**All 31 are a single rule class: `vacuous_test_ast`.**

Now set that beside what 13.1 recorded about the corpus in its own voice: `minions` carries the
**OVERFITTING caveat** — *"Argus was developed against it, began life inside it as `minions_core/apaa/`,
Story 7.2 ran over it, so a high score there is the least transferable evidence"* — and `xagents-webapp` is
*"the real multi-language test (810 TS files vs a Python-built detector suite)"*.

**The consequence, and it is a gap between a floor's intent and its mechanism.** Protocol §5's `N ≥ 5`
condition is satisfied by **member count**, and it is genuinely satisfied — five real repositories, all
byte-reproducible, none authored by Argus. But the **precision ratio** will be computed over findings from
**two** members, **77% of them from the member the record itself names as the least transferable
evidence**, and **100% from one detector**. The three members that most diversify the corpus — including
the only real multi-language test — contribute **nothing** to the denominator.

**This is not an argument to amend §5, and this document does not propose amending it.** It is an argument
that the limitation must be **recorded before the adjudication runs**, not discovered after a figure
exists. The reason is the project's own rule, applied symmetrically: *a failed measurement is not a reason
to amend the threshold*. The mirror of that rule is that **a passed measurement's limitations must be on
the record before the result is known**, because a limitation surfaced after an ≥80% result reads as an
excuse, and a limitation surfaced after a shortfall reads as goalpost-moving. Right now the figure is
unknown, which makes this the only moment when stating it costs nothing.

**AI-E13-5.** Flagged as a significant discovery in §6 SD-1.

### 3.5 🟠 The release's front-door proof runs on no CI leg, and is held by Windows-local runs only

`TC-ArgusAgent-RELEASE-001-25`..`-28` (`tests/test_installed_artifact.py`) are the **fresh-environment,
installed-artifact** proofs: the entry points are exercised, the artifact *audits* rather than merely
imports, the agent entry point works as shipped, and there is a positive control plus a named
`Unevaluable`. They are the claim a first publication rests on.

**They SKIP on every CI leg.** Re-measured this session from run `31986854738` at sha `b04dc1a` — the
4 skips in today's green runs are these four, with the skip reason quoted by the guard itself:

> *"NOT EVALUATED — `uv` is not on PATH, so the wheel could NOT be installed into a fresh environment and
> nothing about the INSTALLED distribution was checked … Install uv, or run this guard where the release
> workflow runs it."*

`audit-ci.yml` sets up Python across a 3.10/3.11/3.12 matrix and **never provisions `uv`**. So the local
Windows run shows 1585 passed / 0 skipped and every CI leg shows 1581 passed / **4 skipped** — and the four
that differ are precisely the four that would substantiate a publication.

**This is the standing project hazard in its purest form:** local gates are Windows-only, CI runs an ubuntu
matrix, and the divergence is silent because a skip is not a failure. The guard is not vacuous — it refuses
honestly and says why. It is simply never given the chance to run where it counts. **AI-E13-7.**

### 3.6 🟠 A stale instruction is live in the tracker, and this retrospective was instructed to propagate it

`sprint-status.yaml`'s 13-3 entry carries the instruction: *"The retro must state H0 is STILL UNOWNED."*

**Measured: that is a stale surface, and 13.3's own §0 analysis measured it first.** H0's ownership was
**CLOSED 2026-08-10b** via the **pre-authorised option (b)** — the operator records that filing H1–H4
against the Minions backlog is their own step, taken outside this workflow. Re-verified this session at
`epics.md:2642-2643` and `deferred-work.md:1575-1588`; `epics.md:30` frontmatter carries the same. The
instruction's ancestor is the `sprint-status.yaml` header note dated **2026-08-09**, which **predates** the
closure. Story 10.5 had **already** recorded a correction to a brief that said otherwise.

**This document does not propagate it.** §10 states the substance that *is* current instead.

**The instructive part is not that a note went stale — it is where it went stale.** It went stale in the
**tracker**, which is the one document every phase of the loop reads and which no guard checks for
currency. `deferred-work.md` is append-only and guarded. `prd.md`, `architecture.md` and `epics.md` are
swept by `test_v1_commitment_closure.py` and by the citation guards. `sprint-status.yaml`'s prose header —
the thing that hands instructions to workers — is checked by nothing. A worker that took its instruction
literally would have published a statement three stories out of date, in the document whose entire purpose
is to state plainly what remains open.

### 3.7 🟡 Epic 13's dependency on Epic 12 was declared satisfied by a decision nobody has recorded taking

The epic text reads **"Depends on Epic 12 (a published tool whose findings are worth adjudicating)."**
Nothing is published — re-verified this session. The Epic-12 retrospective raised exactly this as its
SD-1 and asked for a ruling (**AI-E12-2**): *authorise `DF-12-9-A` act by act, or record a dated decision
that Epic 12 closes unpublished, and re-take the risk acceptance with a new date naming Epic 13.*

**Epic 13 then ran anyway, through two stories, without either arm being taken.** In substance the epic
did not need publication — the corpus is five repositories the operator named, and adjudicating findings
does not require anyone to have installed the tool. So the dependency as written was **wrong**, not
unsatisfied. But *"the dependency turned out to be unnecessary"* is a finding that should be **recorded**,
and instead it was resolved by nobody noticing. The next plan that writes a dependency will be trusted
exactly as much as this one was.

---

## 4. Key Insights

1. **A test suite that reads prose has moved its blast radius into the authoring phases, and the phase
   order has not caught up.** Story files and retrospectives are inputs to guards here. That is a
   deliberate and good design — it is how governance claims get checked at all. Its cost is that **every
   phase that writes prose is now a phase that can break the build**, and the loop currently gates only
   the phases that write code. Two instances in two days (§3.1, §3.2).

2. **A guard's stated assumption is a contract with future authors, and nobody signed it.**
   `story_closure_claims` documents its line-scoping honestly, in its own docstring. The 13.3 author wrote
   a table row anyway — not carelessly, but because a table row is the natural shape for a seven-id
   summary and the assumption lived in a Python docstring nobody reads while writing markdown. **A
   documented assumption is not an enforced one.** The fix that landed (reword the prose) is correct and
   does not generalise; the decision about which side should bear the constraint is still open (§3.3).

3. **The strongest evidence produced by this epic is negative.** No judgement was fabricated; no threshold
   moved; no guard was loosened; four reds were four real defects; a false positive was fixed by
   correcting the record rather than by narrowing the rule. This project's thesis is that a claim nobody
   checks is a defect — and the epic that could most easily have manufactured a checkable claim declined
   to.

4. **`N ≥ 5` counts members; precision counts findings; the corpus satisfies the first and is thin on the
   second.** The floor was written to buy breadth and the mechanism buys membership. 77% of the
   denominator comes from the repository Argus grew inside. That is a real limitation of a real corpus and
   the corpus is still the best one this project has ever had — the failure would be to let it go on the
   record unstated (§3.4).

5. **A tracker that hands instructions to workers needs the same currency discipline as the documents it
   tracks.** The stale H0 instruction survived because `sprint-status.yaml`'s prose is the one governance
   surface with no guard over it, and it is the surface with the most direct influence on what the next
   worker does (§3.6).

6. **"Blocked on a human act" is a stable, honest terminal state, and this project can now hold it.**
   `DF-13-2-A` describes a delivered instrument awaiting a judgement, severity 🟠 rather than 🔴 explicitly
   *because nothing false is published*. The epic can sit here indefinitely without decaying into a
   falsehood. That is a property worth naming — most projects cannot stop here without something starting
   to lie.

---

## 5. Previous-Retro Follow-Through — Epic-12 retro → Epic-13 execution

Fourteen action items were committed on 2026-08-15. Each is re-measured below; nothing is copied from the
Epic-12 document's own status.

| Item | Committed | Measured 2026-08-17 |
|---|---|---|
| **AI-E12-1** | Register the Epic-12 retro in `_STATUS_DOCUMENTS`; make registration the retro step's DoD | ✅ **BOTH HALVES.** First half was already landed (`test_evidence_citation.py:125`). Second half **discharged in practice by this session** (§3.2) and filed as a written rule in **AI-E13-2** |
| **AI-E12-2** | Authorise `DF-12-9-A` act by act; re-take the risk acceptance naming Epic 13 | ❌ **NOT ADDRESSED.** Act (1) performed (three times, incl. `ae54234`, `b04dc1a`); acts (2)–(5) carry no dated authorisation **or refusal**; no new dated risk acceptance names Epic 13. Carried forward as **AI-E13-6** |
| **AI-E12-3** | Dispose the four ledger entries closed only in prose | ✅ **COMPLETED IN 13.2.** All four ruled **by execution**: `DF-8-3-A` CLOSED; `DF-10-4-A` CLOSED with its divergence stated; `DF-10-4-B` **NOT delivered** — re-recorded OPEN with a named owner, and two false story records corrected; `DF-12-3-A` split |
| **AI-E12-4** | Rule on `DF-11-4-D` / `AI-E11-6` — marked done, measurably not done | ❌ **NOT ADDRESSED.** Re-measured: no impact-rank vocabulary exists in `argus/` or `tests/`; the ledger's last touch predates Epic 13. The **(S)** arm never triggered because no Epic-13 story edited `_NOTE_SECTIONS`; the **(H)** arm was not taken. Carried forward as **AI-E13-9** |
| **AI-E12-5** | Register the guard-adequacy clause + Epic-11's two orphaned rules in §Enforcement | ✅ **COMPLETED IN 13.2**, at the fourth request, with the input-side twin. Verified: `GUARD-ADEQUACY` present in `architecture.md` |
| **AI-E12-6** | Land the ledger-claim cross-check guard before 13.2 files its record | ✅ **COMPLETED IN 13.2**, in the story it was scheduled for. Found 19 unbacked claims on its first run and fired on its own story (§2.4) |
| **AI-E12-7** | Generalise the closed-vocabulary rule from three flags to a standard | ⏳ **PARTIAL / not advanced by Epic 13.** `ClosedVocabulary` uses exist in `argus/cli.py`; no general §Enforcement rule was added this epic |
| **AI-E12-8** | Make the resumed-session integrity check standing | ❌ **NOT ADDRESSED.** No interruption occurred in Epic 13, so the gap stayed invisible again — the same luck the Epic-12 retro named |
| **AI-E12-9** | Give `DF-10-2-A` its dated decision | ⏳ **PARTIALLY ADVANCED, in the honest direction.** 13.1 / DN-6 **corrected the entry by measurement**: the premise held for three of four languages — Rust extracts `struct_item` and misses only functions because the vocabulary entry `fn_item` is not a node type `tree-sitter-rust` emits (the real one is `function_item`); C/C++ match `function_definition` then drop it for having no `name` field. Rust stays ineligible on the **narrower correct ground**. The **detector half remains OPEN, owned, unscheduled**; `target_story` is still `NONE`. Fifth consecutive retrospective to name it |
| **AI-E12-10** | Make the create-story premise re-measurement a gate, not a convention | ⏳ **STILL A CONVENTION — and it went 3-for-3 again.** 13.1 (§0 "nine-for-nine"), 13.2 ("ten-for-ten"), 13.3 ("eleven-for-eleven"), each finding material staleness. Eleven consecutive successes is a strong argument for the convention and no argument at all that it is enforced |
| **AI-E12-11** | Give the dogfood artifact-currency bootstrap to the worker that hits it | ✅ **EVIDENCE OF USE.** 13.2 committed the `argus/` delta (`e991a00`) and regenerated the artifacts through their own renderers as a **separate** commit (`4c6c76d`), which is exactly the prescribed sequence. No dev pass ended with an artifact-currency guard red |
| **AI-E12-12** | Dispose the untracked root artifacts before act (5) | ❌ **NOT ADDRESSED.** Re-measured by `git status`: **all six still present and untracked** — `.bmad-drift-audit/`, `_bmad-output/audit-reports/ollama-audit/`, `.../run-demo/`, `.../self-audit/`, `argusdemo/`, `bmad-dev-loop-pack/`. Carried forward as **AI-E13-8** |
| **AI-E12-13** | Confirm or overturn FR23's `library-seam` de-scope — "last chance" | ❌ **NOT ADDRESSED, and its stated precondition has now expired.** `prd.md:554` still carries `target_story: NONE — unscheduled`, *"to be scheduled once 12.1 lifts the NFR-M1 gate."* **12.1 lifted it**: `argus/pipeline.py` measures **1111** lines against the 1200 cap, re-counted this session. Reason (a) for the deferral no longer exists; only reason (b) — unattended CI has no human to answer a default-STOP gate — survives, and that is a design question, not a capacity fence. Carried forward as **AI-E13-10** |
| **AI-E12-14** | Record only, no owner, on purpose | ✅ Honoured. The equivalent courtesy for Epic 13 is **AI-E13-11** |

**Score: 5 completed, 3 partial, 6 not addressed.** The pattern is sharp and worth naming without blame:
**every item that was assigned to a story got done, and every item that was assigned to a human decision
did not.** AI-E12-3, -5, -6 and -11 all landed inside 13.2. AI-E12-2, -4, -12 and -13 all require somebody
to decide something and none moved. This is the same shape as `DF-13-2-A` itself, and it is the shape of
the epic's whole blocker: **this project executes work reliably and accumulates decisions.**

---

## 6. Significant-Discovery Alerts

### 🚨 SD-1 — The precision denominator is 77% drawn from the corpus member the record calls the least transferable evidence, and 100% from one detector

Measured this session; recorded in no story, review or ledger entry. 24 of 31 findings are `minions` (which
carries the OVERFITTING caveat), 7 are `agent-smith`, and three members — including the only real
multi-language test — contribute zero. All 31 are `vacuous_test_ast`.

**Why it changes the plan for 13.3 and for the adjudication that precedes it.** 13.3 computes §5's four
conditions and reports a result. If the result is ≥80%, the sentence that replaces the disclosure will be
read as *"Argus's blocking findings are ≥80% real."* The measurement that supports it will be *"one
detector, on two repositories, 77% of it on the repository Argus grew inside."* Both statements can be
true simultaneously, and the second must be attached to the first **at the moment the first is written**.

**Recommendation — NOT applied, and explicitly not a threshold amendment.** Before the adjudication runs,
record the concentration as a stated limitation of whatever figure emerges: in the adjudication record's
own limitations surface, or in protocol §7's honesty invariants. **Do not change §5.** Do not require
distribution retroactively. Just make it impossible for the figure to be published without its shape
beside it. **AI-E13-5.**

### 🚨 SD-2 — Epic 13 has no successor, so its retrospective is the last scheduled moment a human reads the ledger

`epics.md` ends at Epic 13. There is no Epic 14 to preview and no next epic to prepare for. Several
`DF-*` and `AI-*` entries name *"the next retrospective"* or *"the last epic in the plan"* as their
destination — `DF-12-9-A`'s `target_story` says in as many words: *"The Epic-12 retrospective is the next
scheduled moment a human reads this file."*

**That destination is running out.** After Epic 13's FINAL retrospective there is no scheduled reader.
Items with `target_story: NONE` and no successor epic do not become closed; they become unwatched.

**Recommendation — NOT applied.** Before Epic 13 closes, every `target_story: NONE` entry needs either a
named successor destination (a maintenance track, a dated review, a change proposal) or an explicit dated
acceptance that it is carried indefinitely. This is a re-plan-adjacent decision and belongs to the
operator, not to this worker. **AI-E13-12.**

### 🚨 SD-3 — Making the repository public renders the entire `_bmad-output/` tree world-readable, including this document

`DF-12-9-A` act (5) is *"making the repository public — irreversible in effect."* The Epic-12 retro
correctly framed it as a **disclosure decision** rather than a deployment step. Epic 13 sharpens it,
because Epic 13 is the epic that writes the most candid material this project has produced.

**What becomes world-readable at act (5):** `deferred-work.md` (327 KB of open defects with named owners
and unowned risks), every retrospective including this one, `epics.md`'s H0–H4 handoff with its
🚩 unowned-action markers, the corpus limitations recorded per member — including the sentence naming
`minions` as *"the least transferable evidence"* — and the 31-row worklist naming findings in five named
XAgents repositories.

**None of that is dishonest and most of it is a credit to the project.** The point is the opposite of
concealment: this is an unusually well-documented set of self-criticisms, some of it about repositories
other than this one, and **nobody has yet decided to publish it.** Act (5) publishes it as a side effect
of publishing the code. **That is a decision that should be taken deliberately, not inherited.**
**AI-E13-6** covers it; **AI-E13-8** (the six untracked directories) must land before it, not after.

### ⚠️ SD-4 — Tagging and removing the caveats must land as ONE change, and the guard already enforces this

`TC-ArgusAgent-DOCS-001-55`/`-55b` — the tag-state guard — was **deliberately widened to every registered
release surface BEFORE any tag exists**, so that act (2)/(3) *"turns all four pins on three surfaces RED at
once instead of converting two of them into published falsehoods invisibly."* Confirmed present in
`tests/test_built_distribution.py:726,775`.

**The operational consequence, stated so nobody meets it by surprise:** the moment `git tag v0.1.0` runs,
the suite goes red across 4 pins on 3 surfaces, and it stays red until the caveat text is updated. **Tag
and caveat removal must be one atomic change.** A tag pushed on its own leaves `master` red — and per §3.1
this repository has just demonstrated it will push before it discovers that.

### ⚠️ SD-5 — `DF-10-2-A` is now on its fifth consecutive retrospective

Fourth was Epic 12. 13.1 advanced it by **correcting it** — the premise was wrong for one of four
languages and Rust stays ineligible on narrower, correct ground. The dated decision is still not made and
`target_story` is still `NONE`. Carried as **AI-E13-9**'s sibling; see the follow-through table.

---

## 7. Action Items — concrete, owned, with a real destination

*Per `AI-E9-8`: no operator act is asserted onto an invented story id. Where the destination is a human
decision, `target_story` stays `NONE` and the owner is named instead.*

| Id | Action | Owner | DoD | Class | Sev |
|---|---|---|---|---|---|
| **AI-E13-1** | **Put a suite gate on the phase that writes `stories/*.md`.** In this repository story files are TESTED ARTIFACTS (`DOCS-001-78` globs `stories/*.md`; `DOCS-001-22` globs `epic-*-retro-*.md`), and the loop's only suite gates sit on Dev and Review — the two phases that do not write them. Preferred: the SM/create-story phase ends by running the guard modules that read prose (`python -m pytest tests/test_governance_record_integrity.py tests/test_evidence_citation.py`) and cannot hand off red. Second: a pre-push gate running the full suite. **Must be platform-neutral** — specify it as a `python -m pytest` invocation, not a shell script, because local gates are Windows and CI is an ubuntu matrix | **dev-loop orchestrator** (the phase rule) + **XAgent007** (if the pre-push arm is chosen) | No phase that writes into `stories/` or the artifact directory can hand off without a green run of the prose-reading guards; the invocation is identical on Windows and ubuntu | process | 🔴 |
| **AI-E13-2** | **Split `tests/test_evidence_citation.py` before the FINAL Epic-13 retrospective is written.** It stands at **exactly 1200/1200** after this session's registration. `MAINT-001-03` pins 1201 as a failure, so the next status document cannot be registered at all. Move `_STATUS_DOCUMENTS` + `-21`/`-22` to a new module (12.8's cohesion-split precedent) or move the registry to a data file. **Do not shave the file to fit** and do not add an `_EXEMPT_BY_DESIGN` entry — 12.1's rule requires a date, an owner and a ledger id, and this is a structural problem, not an exemption case. **Also: write AI-E12-1's second half down as a rule** — the retrospective step's DoD includes registering its own output, which this session performed but no document yet requires | **Engineering Lead** (the split) + **dev-loop orchestrator** (the DoD line) | `test_evidence_citation.py` is under the ceiling with headroom for at least two further registrations; the retrospective step's definition of done names the registration | technical | 🔴 |
| **AI-E13-3** | **Rule on `story_closure_claims`' line-scoping — schedule the narrowing, or make the convention the ruling.** Arm (a): per-id scoping, each `DF-*` matched against the closure verb nearest it, **with a generated adversarial variant proving the narrower predicate can still fire** (the guard's existing non-vacuity pattern). Arm (b): a dated entry recording that **one claim per line is the convention**, with the residual risk named — any future multi-id summary row reproduces the 13.3 false positive. **Not both, and not neither.** The guard is not to be weakened and no id is to be allowlisted under either arm | **Engineering Lead** | Either `story_closure_claims` is per-id scoped with a generated adversarial variant in the suite, **or** `deferred-work.md` carries a dated entry stating the convention and its residual risk. Referenced from the guard's docstring either way | process | 🟠 |
| **AI-E13-4** | **Adjudicate the 31 rows.** The one act that unblocks 13.3 and the epic. At the cited locators, per protocol §4 (full-corpus exhaustive, not sampled; borderline → locator re-examination → golden-key correction → external tie-break), with **actual expert-hours recorded** against §3's ceiling — recorded, not enforced. Then re-run `scripts/build_adjudication_record.py`. `DF-13-2-A` | **XAgent007** — Engineering Lead, protocol §2 primary adjudicator. **No agent may supply this** (`DN-6`) | `adjudication-record.json` carries a live TP/FP disposition and an adjudicator id on all 31 rows, `expert_hours` non-null; `exhaustiveness()` returns evaluable | precision gate | 🔴 |
| **AI-E13-5** | **Record the denominator's shape BEFORE the adjudication runs (SD-1).** 24/31 `minions` (overfitting caveat), 7/31 `agent-smith`, 0 from the other three, 100% one rule class. State it as a limitation of whatever figure emerges, in the record's own limitations surface or protocol §7's honesty invariants. **Explicitly NOT an amendment to §5 and not a change to any threshold in either direction.** Doing it now costs nothing because the figure is unknown; doing it after reads as an excuse or as goalpost-moving depending on the result | **XAgent007** (Governance Owner) with the **Engineering Lead** | The concentration figures are on the record, dated, before any disposition is written; §5's literals are byte-unchanged | governance | 🔴 |
| **AI-E13-6** | **Decide `DF-12-9-A` acts (2)–(5), each with a dated authorisation or a dated refusal — `AI-E12-2` carried forward, now partly answered.** Act (1) is performed (three times). Acts (2) tag, (3) push tag, (4) GitHub Release, (5) make public are unperformed and carry neither authorisation nor refusal. **Act (5) is a disclosure decision** (SD-3): it makes the whole `_bmad-output/` tree world-readable, including the ledger, this document and the unowned-risk statements. **And re-take the risk acceptance with a new date naming Epic 13** — the 2026-08-11 acceptance has now silently covered three epics. If Epic 13 is to complete unpublished, **say so in the entry** | **XAgent007** — the only party with the credentials. `target_story: NONE`, deliberately | Each of acts (2)–(5) carries an explicit dated authorisation or refusal; a new dated risk acceptance names Epic 13; the act-(5) disclosure question is answered in its own words | delivery | 🔴 |
| **AI-E13-7** | **Provision `uv` in `audit-ci.yml` so `RELEASE-001-25`..`-28` stop skipping on every CI leg.** These are the fresh-environment installed-artifact proofs — the front-door claim of any publication — and they are currently held by **Windows-local runs only**. They are the 4 skips in today's green runs. Use the standard `uv` setup action so all three matrix legs provision it identically; the guard already refuses honestly and names the fix in its own skip message | **Engineering Lead** | `audit-ci.yml` provisions `uv`; the four `RELEASE-001-25`..`-28` ids **pass** rather than skip on 3.10, 3.11 and 3.12; the local/CI pass counts reconcile | technical | 🟠 |
| **AI-E13-8** | **Dispose the six untracked root artifacts — `AI-E12-12` carried forward, unmoved.** Re-measured: `.bmad-drift-audit/`, `_bmad-output/audit-reports/{ollama-audit,run-demo,self-audit}/`, `argusdemo/`, `bmad-dev-loop-pack/`. None is reached by `pytest`, a corpus glob or the dogfood partitioner — which is exactly why nothing will catch them. **Before act (5), not after**: at the moment the repository goes public, what is *not* tracked stops being the question and what *is* becomes it | **XAgent007** (operator) | Each is deleted, tracked deliberately, or `.gitignore`d with a stated reason | governance | 🟠 |
| **AI-E13-9** | **Rule on `DF-11-4-D` / `AI-E11-6` (`AI-E12-4` carried forward) and give `DF-10-2-A` its dated decision (`AI-E12-9`, fifth consecutive retrospective).** For the first: no impact-rank vocabulary exists, the **(S)** arm never triggered because no Epic-13 story edited `_NOTE_SECTIONS`, and it remains marked done while being measurably not done — **which is the worst of the three available states**, because a falsely closed item is the one nobody rechecks. For the second: 13.1 corrected the premise by measurement; what is still missing is the dated decision, and `target_story` is still `NONE` | **XAgent007** (Governance Owner) / **Engineering Lead** | `DF-11-4-D` carries either a rank property in `-16` or a dated acceptance of the narrative convention **with its cost**; `DF-10-2-A`'s `target_story: NONE` is replaced by a destination or a dated *"the disclosure is sufficient for V1"* entry | governance | 🟠 |
| **AI-E13-10** | **Confirm or overturn FR23's `library-seam` de-scope — `AI-E12-13` carried forward, and its own stated precondition has now expired.** `prd.md:554` defers it *"once 12.1 lifts the NFR-M1 gate"*; 12.1 lifted it — `argus/pipeline.py` is **1111** lines against the 1200 cap, re-counted this session. Deferral reason (a) is gone; only reason (b) (unattended CI has no human to answer a default-STOP gate) survives, and that is a design question. FR24/`DF-10-5-C` moves with it. **Epic 13 is the last epic in the plan**, so overturning means a correct-course proposal and this is the last scheduled moment to raise it | **XAgent007** (Governance Owner) | A dated entry in the PRD amendment block confirming the de-scope **on the surviving reason**, or a correct-course proposal | governance | 🟡 |
| **AI-E13-11** | **RECORD ONLY, no owner, on purpose: Epic 13's review record is not a quality trend in either direction.** Two stories, one clean first-pass and one two-iteration pass whose nine findings were all real and all resolved. **The more informative number is that both stories' most consequential outcomes were things that did NOT happen** — no fabricated judgement, no moved threshold, no loosened guard. A pass rate measures what the gate looks at, and this epic's gate was mostly looking at whether anyone would make something up. This exists so that if the trend is ever cited, the reader knows what it does and does not measure — the courtesy `AI-E9-10`, `AI-E10-10`, `AI-E11-12` and `AI-E12-14` paid before it | **Record only — no owner, on purpose** | **This retrospective.** DoD: none | governance | 🟢 |
| **AI-E13-12** | **Give every `target_story: NONE` entry a destination before Epic 13 closes (SD-2).** `epics.md` ends at Epic 13; several ledger entries name *"the next retrospective"* or *"the last epic in the plan"* as their reader, and after Epic 13's FINAL retrospective there is no scheduled reader. Items do not become closed when the plan runs out — they become unwatched. Each needs a named successor destination (a maintenance track, a dated review, a change proposal) or an explicit dated acceptance that it is carried indefinitely. **Recommended, not applied:** assigning destinations across the ledger is a re-plan and belongs to the operator | **XAgent007** (Governance Owner) | Every open entry with `target_story: NONE` carries a successor destination or a dated indefinite-carry acceptance | governance | 🟠 |

---

## 8. Critical-Path Items — what stands between here and the FINAL retrospective

1. 🔴 **AI-E13-4 — the adjudication.** Nothing else on this list unblocks 13.3, and nothing an agent can do
   advances it. `DF-13-2-A`. Everything that could be prepared has been prepared: the instrument, the
   guards, the 31-row worklist with locators, the append-only record, the three-outcome terminal
   vocabulary in 13.3. **This is a decision and a judgement, not work.**
2. 🔴 **AI-E13-5 — record the denominator's shape first.** This must land **before** AI-E13-4, not after.
   It is the only item on this list with a hard ordering constraint against the adjudication, and the
   ordering is the entire point (§3.4).
3. 🔴 **AI-E13-2 — split `test_evidence_citation.py`.** The FINAL Epic-13 retrospective **cannot be
   written and registered** until this lands. Blocking, mechanical, and discovered by this session.
4. 🔴 **AI-E13-1 — gate the prose-writing phase.** Until it lands, every SM and retrospective write can
   red `master`, and this loop pushes before it discovers that.
5. 🟠 **AI-E13-7 — provision `uv` in CI.** Should land before any publication decision, so that the
   installed-artifact proof is held by more than one Windows laptop.
6. 🟠 **AI-E13-8 — the six untracked directories.** Before `DF-12-9-A` act (5), not after.
7. 🔴 **AI-E13-6 — decide acts (2)–(5).** Independent of the gate: it is a separate authorisation, and
   clearing the precision gate authorises **attested externalization and nothing else**.

---

## 9. Readiness Assessment

**Read the two questions separately. They are not the same question and Epic 13 only touches one of them.**

| Dimension | State, measured 2026-08-17 |
|---|---|
| **Story completion** | 2 of 3. 13.3 `ready-for-dev`, blocked |
| **The precision gate** | **NOT CLEARED, and unevaluable.** 1 of protocol §5's 4 conditions holds. `protocol_cleared` is `False` and has never been `True`. The disclosure stays |
| **Testing & quality** | Local suite 1585 passed / 0 failed / 0 skipped (Windows). CI green on `b04dc1a`, both workflows, all three legs, 1581 passed / **4 skipped** per leg. **The 4 skips are the installed-artifact proofs** (§3.5) |
| **`mypy` / `bandit`** | Clean, 84 source files; 19 Low / 0 Medium / 0 High. Attributed to the 13.2 dev and independently re-confirmed by the 13.2 reviewer |
| **CI coverage of HEAD** | ✅ **Established** — and this is an improvement over Epic 12, where no run covered the release commit. 13.3's story text records CI coverage as *"NOT ESTABLISHED … latest run covers `00c8d1b`"*; that statement was true when written and is **now superseded** by run `31986854738` at sha `b04dc1a` |
| **Publication / outward-facing acts** | **Act (1) performed. Acts (2)–(5) unperformed, unauthorised and unrefused.** No tag, no release, repository `PRIVATE`, version `0.1.0`. This is an **authorisation** question, not a build question — the dossier has been complete since Story 12.9 and nothing further can be prepared |
| **Codebase health** | Sound. `argus/pipeline.py` 1111/1200; the three near-full test modules remain the standing constraint, and one of them (`test_evidence_citation.py`) reached the ceiling exactly during this session (§3.2) |
| **Unresolved blockers carried forward** | `DF-13-2-A` (🟠, the adjudication) · `DF-12-9-A` (🟡, seven acts, four undecided) · `DF-8-4-B`/`DF-8-4-C` (open and unowned **by decision** — a disposition, not a gap) · `DF-10-2-A`, `DF-11-4-D`, `DF-10-5-C`, `DF-3-4-A`, `DF-12-7-A`, `DF-10-3-B`, `DF-10-3-C` — all `target_story: NONE`, see SD-2 |

**The honest one-line assessment:** the epic has built everything it can build and is waiting on the one
input no agent may supply. Nothing false is published; nothing is over-claimed; nothing has decayed. It can
wait here indefinitely without becoming a lie — and that is the property the epic was designed for.

---

## 10. The open-items list, RE-DERIVED — because a cleared gate is not plan closure

*Required by `epics.md` Story 13.3's fifth AC. Re-derived from the tree on 2026-08-17, not copied — from
the AC's own example list, from `sprint-status.yaml`'s header, or from 13.3's table.*
*Written **one id per line**, deliberately, per §3.3.*

**On the Minions handoff — the substance, with the stale wording corrected:**

- **H0 (who FILES the handoff) is OWNED.** Closed 2026-08-10b via the pre-authorised **option (b)**:
  filing is the operator's own step, taken outside this workflow. `epics.md:2642-2643`,
  `deferred-work.md:1575-1588`, `epics.md:30`. ⚠️ **`sprint-status.yaml`'s 2026-08-09 header note saying
  H0 *"is still UNOWNED"* is a STALE SURFACE and is not propagated here** (§3.6).
- **H1–H4 are still NOT FILED.** Ownership was the gap that closed; filing is not the same act and has not
  happened.
- **Assumption A5 remains ⚠️ UNSUPPORTED.** The Epic-8 amendment stops Minions being falsely accused; it
  does not make Minions pass.
- **H3's blocking-vs-advisory policy decision is UNMADE.** Post-amendment Minions lands on
  `INSUFFICIENT_COVERAGE`, exit `3`, which still fails an unconfigured CI step by design.
- **This repository's CI cannot verify any of the Minions integration.** Unchanged and by design.

**Ledger entries — measured id by id, one per line:**

- `DF-13-2-A` — **OPEN**, owned by XAgent007, the critical path. The adjudication has not happened.
- `DF-12-9-A` — **OPEN**, owned by the Engineering Lead. Act (1) performed; acts (2)–(5) undecided.
- `DF-8-4-B` (bytes-example half) — **remains open and unowned _by decision_**, `deferred-work.md:1649-1657`. A locked disposition. Not a gap.
- `DF-8-4-C` — **remains open and unowned _by decision_**, same locked disposition. Not a gap, and **not** the subject of any closure claim by any story.
- `DF-10-2-A` — **OPEN**, detector half owned and unscheduled; premise corrected by 13.1 / DN-6; fifth consecutive retrospective.
- `DF-11-4-D` — **marked done and measurably not done**; no impact-rank vocabulary exists. See AI-E13-9.
- `DF-10-5-C` — **OPEN**, `target_story: NONE`; FR29 needs a CLI surface.
- `DF-3-4-A` — **OPEN**, re-stated and not re-filed across three stories.
- `DF-10-3-B` and `DF-10-3-C` — both **OPEN**, both `target_story: NONE`.
- `DF-12-7-A` — **OPEN**, unscheduled by 12.7 / DN-2.
- `DF-6-6-A`, `DF-6-6-A-P1`, `DF-6-6-A-P2`, `DF-7-2-A` — **OPEN**, re-recorded by 13.2 with their remaining
  scope, none left pointing at a run that has happened. They close with AI-E13-4 and not before.

**Additionally open, and not on any prior list — found by this retrospective:**

- The **denominator concentration** (SD-1) is unrecorded anywhere. Filed as AI-E13-5.
- The **prose-writing phase has no suite gate** (§3.1). Filed as AI-E13-1.
- `tests/test_evidence_citation.py` is at **exactly 1200/1200** (§3.2). Filed as AI-E13-2.
- The **`story_closure_claims` line-scoping decision** (§3.3) is unmade. Filed as AI-E13-3.
- **Nothing schedules a reader for `target_story: NONE` after Epic 13** (SD-2). Filed as AI-E13-12.

**And one sentence, plainly, because the epic's own AC asks for it:** *clearing the precision gate would
authorise **attested externalization** and nothing else — not a release, not commercial, enterprise,
regulated or operated-service use, and **not plan closure**.* The Epic-9 retrospective declared the plan
FINAL once already and Epic 10 had to reopen it. **This document does not repeat that error, and neither
should the FINAL pass — the list above is longer than it was, not shorter.**

---

## 11. Why this pass is INTERIM, and what the FINAL pass must cover

**What this document could NOT assess, because 13.3 has not run:**

1. **Whether the epic achieved its purpose.** The purpose is a measurement. It has not been taken.
2. **The measured precision figure**, and therefore whether the disclosure is replaced or stays.
3. **Whether the flip path behaves correctly at the moment it fires.** 13.3's §0.1 records **two defects
   found by execution and still live**: (a) `INSTRUMENT_DISCLOSURE_VALIDATED` names *"the Argus dogfood
   corpus"* — the self-audit 13.1 **excluded** from N — so a cleared statement would rest on the corpus
   that cannot clear it; (b) `protocol_cleared_call_sites` matches **only a literal `True`**, so deriving
   the flag — the correct design, and what the architecture's adjudication-record rule demands — makes
   `TC-ArgusAgent-DOCS-001-46` **vacuous at the exact moment the gate flips**. Both are reproducible now,
   in either branch. **Neither has been exercised, because the branch has not been taken.**
4. **Whether `expert_hours` came in under protocol §3's ceiling**, and therefore whether the next run can
   be scheduled on evidence rather than on the estimate. Currently `null` — "NOT RECORDED", never zero.
5. **Whether `DF-6-6-A` / `-P1` / `-P2` / `DF-7-2-A` were closed or re-scoped with reasons**, per 13.2's
   AC. They are re-recorded, not closed, and close only with the adjudication.
6. **The epic's own AC7 deliverable** — the re-derived open-items list as 13.3 computes it. §10 above is
   this worker's re-derivation and is **not** a substitute for the story's.

**The FINAL pass must additionally verify:**

- That the three-outcome terminal vocabulary (`CLEARED` / `NOT_CLEARED` / `BLOCKED`) was honoured, and
  specifically **that a vacuous fold was never recorded as a measured shortfall**.
- That AI-E13-5's limitation record landed **before** the dispositions were written, and that §5's
  literals are byte-unchanged in either direction.
- That AI-E13-1 through AI-E13-3 landed, since all three are blockers on the FINAL pass itself.
- That `epic-13-retrospective` moves from its in-flight value to `done` **only then**, and that `epic-13`
  moves to `done` **only after that**.

---

## 12. Commitments & Next Steps

**Commitments recorded here:** 12 action items (1 record-only), 7 critical-path items, 5
significant-discovery alerts, 0 preparation tasks for a next epic — **there is no next epic** (SD-2).

> ⚠️ **ORDERING HAZARD FOR WHOEVER COMMITS THIS SESSION'S WRITES — the same shape as SD-4.**
> This session produced three writes: **this document**, its one-line registration in
> `tests/test_evidence_citation.py::_STATUS_DOCUMENTS`, and the `sprint-status.yaml` update. **They
> must land in ONE commit.** `TC-ArgusAgent-DOCS-001-22` asserts the closure in *both* directions:
> an unregistered document fails, **and a registered document the globs cannot find also fails**
> (*"registered document(s) are no longer found by the globs … either they were deleted (§3.4:
> records are superseded, never erased) or the patterns drifted"*). Committing the test change
> without this document therefore reds `master` just as surely as committing this document without
> the test change — which is the §3.1 defect a third time, in the opposite direction. Verified green
> together on this tree: full suite **1585 passed / 0 failed / 0 skipped**.

**In order:**

1. **AI-E13-5** — record the denominator's shape. Before the adjudication, not after. Costs nothing now.
2. **AI-E13-4** — **XAgent007 adjudicates the 31 rows.** The only act that unblocks the epic, and the only
   one no amount of further work can advance.
3. **AI-E13-2** and **AI-E13-1** — the two mechanical blockers on the FINAL retrospective, both discovered
   this session, both cheap, both blocking.
4. **AI-E13-6** — decide `DF-12-9-A` acts (2)–(5), including the act-(5) disclosure question. Independent
   of the gate.
5. **AI-E13-3**, **AI-E13-7**, **AI-E13-8**, **AI-E13-9**, **AI-E13-10**, **AI-E13-12** — as scheduled by
   their owners.
6. **Then, and only then, the FINAL Epic 13 retrospective.**

---

*Amelia (Developer): "Two stories done, one blocked, and the blocked one is the only one that decides
anything. The team built an instrument capable of measuring the thing this project has claimed for
thirteen epics that it would measure — and then refused to make up the number that would have made it
read as finished. That refusal is the epic's result so far, and it is a better result than a fabricated
figure would have been. The gate is where it always was: waiting on one person to look at 31 findings and
say which are real."*

*Charlie (Senior Dev): "And a story file turned master red because we test our prose and gate our code.
That one's on the loop, not on anyone in it."*

*Alice (Product Owner): "Nothing published, nothing over-claimed, nothing decayed. We can wait here. Let's
not wait here by accident."*
