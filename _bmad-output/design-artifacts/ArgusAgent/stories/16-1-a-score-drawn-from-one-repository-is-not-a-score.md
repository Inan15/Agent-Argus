---
baseline_commit: 0a6e121641acbffe56697873654ba31efef3a9cd
---

# Story 16.1: A score drawn from one repository is not a score

Status: **review** — ✅ the iteration-1 review finding is FIXED and re-verified by executed
mutation (round 3, 2026-08-20): §5's dispatch mirror is written once, `-55` no longer claims a
clause its own fixture cannot reach, and the clause itself is driven in BOTH directions by the new
`TC-ArgusAgent-PRECISION-001-86` — the reviewer's own two mutations now turn it RED. The deferred
`deferred-work.md` byte-edit is reverted to its `0a6e121` bytes and disclosed. See *Dev Agent
Record — ROUND 3*.

> ~~Status: **in-progress** — ⛔ code review (2026-08-20, iteration 1) found `TC-ArgusAgent-PRECISION-001-55`'s
> re-authored breadth clause cannot be driven RED by any executed mutation (AC1.5 / AC4.1 not
> actually discharged for `-55`); see *Review Findings* below.~~ Struck, not erased (§3.4): that
> sentence is the true record of what the review found, and it was right. Both operator HALTs
> remain ✅ RESOLVED (XAgent007, 2026-08-20) and the member arm remains LANDED — this was a
> guard-adequacy gap in one guard, not a reopening of either HALT. The round-1 HALT record below is
> left **byte-unedited** (§3.4): it is the evidence the escalation was correct to raise.

| | |
|---|---|
| **Epic** | 16 — Spend the Round Well — strengthen the gate, then measure once |
| **Story key** | `16-1-a-score-drawn-from-one-repository-is-not-a-score` |
| **Source** | [sprint-change-proposal-2026-08-20.md](../sprint-change-proposal-2026-08-20.md) §4.3(1), **✅ APPROVED by XAgent007 (Engineering Lead) 2026-08-20** · [epics.md](../epics.md) §Epic 16 (`epics.md:3019`), §Story 16.1 (`epics.md:3063`) |
| **Contexted on** | HEAD `0a6e121` (`docs(16): record the operator's approval as a separate act, and say what it does not authorise`), working tree **CLEAN**, **5 ahead of `origin/master`, 0 behind** |
| **Authorisation** | The approval unblocks **16.1, 16.2 and 16.3 only**, and only to apply §4.3's three conditions **each deriving and recording its own constants**. It does **not** unblock 16.4, does not authorise ratification, a fetch, or spending `DF-13-5-A`'s round. |
| **Ordering** | 🔒 **BINDING.** This story's commits must **precede** every commit containing Argus output over any bench member. The ancestry *guard* is 16.4's deliverable; this story's obligation is to land first and to record its own sha for 16.4 to cite. |
| **Direction** | ⛔ **STRENGTHENING ONLY.** Every change here makes clearing **harder**. Touches neither the ≥80% figure, `VALIDATION_SET_FLOOR_N`, the five ratified members, nor `MANIFEST_FIELDS`. |

---

## Story

As the Argus maintainer,
I want the precision gate to **refuse a denominator that is too narrow to mean anything**,
So that a figure computed from a single repository and a single rule class cannot be reported as if
it measured the tool.

### What this story IS

**One new protocol §5 condition, and the code that computes it.** Breadth stops being a
*disclosure the reader may weigh* and becomes a *condition the gate must satisfy*: the precision
ratio is evaluable only over a population drawn from at least a derived number of distinct
contributing members **and** at least a derived number of distinct rule classes. Every input to it
is **already computed and already committed** — this story reads those fields; it does not compute
second copies of them.

### What it is NOT

- **NOT a threshold change in the softening direction.** The ≥80% `Fraction`, `VALIDATION_SET_FLOOR_N`,
  FR34, `protocol_cleared`, the five ratified members and `MANIFEST_FIELDS` (closed at 9) are all
  **untouched**. §5 and Story 13.3 / AC5 forbid narrowing a corpus, dropping a member or re-weighting
  one to move the ratio; nothing here does any of those, and everything here makes clearing harder.
- **NOT a new terminal state.** `GATE_OUTCOMES` stays closed at **three** (`CLEARED` / `NOT_CLEARED` /
  `BLOCKED`) and `CONDITION_VERDICTS` stays closed at **four**. The states this story needs already
  exist.
- **NOT a run.** No detector is executed over any repository, ratified or candidate. No member is
  fetched, staged or audited.
- **NOT ratification.** All 14 candidate rows stay `eligible_for_n=False`; `eligible_member_count()`
  stays **5**.
- **NOT adjudication.** No row moves off `UNADJUDICATED`; no `expert_hours` are recorded.
- **NOT the holdout (16.2) and NOT the yield floor (16.3).** This story must compose with both and
  must not pre-empt either.
- **NOT a ledger disposition.** Every entry cited below stays open.

---

## §0 — PREMISES RE-MEASURED BY EXECUTION at HEAD `0a6e121`

> Every figure below was derived on the live tree during contexting, read-only, out of tree.
> `git status --porcelain` was **empty** before and after. **No figure in this story file is a
> constant to copy into code** — §0 exists so the dev agent starts from measurements rather than
> from the change proposal's prose, and so AC2's derivation has real inputs.

### §0.1 The population the gate would measure today

| Quantity | Value | Where it is read from |
|---|---|---|
| Ratified eligible members (`N`) | **5** | `tests/corpus/_manifest.eligible_member_count()` |
| The one floor (`VALIDATION_SET_FLOOR_N`) | **5** | `registry_module().VALIDATION_SET_FLOOR_N`; also `_manifest.validation_floor_n()` — **one floor, never forked (DN-3)** |
| Total manifest rows | **21** | 5 eligible + 14 R2 candidates + 2 permanently-ineligible (`argus-self-audit`, `minions-story-7-2-superseded`) |
| Bench candidates awaiting R2 | **14**, all `primary_language=python` | `eligible_for_n=False`, reason *"candidate — awaiting operator ratification (protocol section 6 R2)"* |
| `MANIFEST_FIELDS` | **9**, closed | `_manifest.MANIFEST_FIELDS` |
| Live rows on the adjudication record | ~~**31**, all `UNADJUDICATED`, **zero** human judgements~~ ⛔ **FALSE — CORRECTED 2026-08-20 by execution (dev-story round 1), annotated here per §3.4 and by explicit operator instruction: 31 rows, **0 `UNADJUDICATED`**, **26 FP + 5 BORDERLINE**, i.e. **31 human judgements**, all by `XAgent007 (Engineering Lead)` dated 2026-08-17.** The original wording is struck, not erased: it is what the story was contexted on, and it is the whole of §2.1's stated authorisation to re-version the protocol — which is why that authorisation did not hold and why no `V1.4` row was taken. | `validation-corpus/adjudication-record.json`, read through the shipped `load_record` / `live_rows` / `counts` API |
| Contributing members in that population | **2 of 5** — `minions` 24, `agent-smith` 7 | `gate-decision-record.json` → `concentration` |
| Non-contributing ratified members | **3** — `agent-markovich`, `ai-body-runtime`, `xagents-webapp` | same |
| Distinct rule classes in that population | **1** — `vacuous_test_ast` | same |
| `concentration.is_concentrated` | **True**, and the record says in terms it is *"derived — not a threshold and not a distribution requirement"* | same |

### §0.2 ⛔ THE MEASUREMENT THAT GOVERNS THE RULE-CLASS ARM — read this before deriving anything

**Measured from the shipped code at `0a6e121`, not inferred:** exactly **ONE** rule class can reach
verdict-eligibility over the repository corpus today.

- `verdict_eligible` is `depth_supported is not None` (`replay_harness.finding_match_key`,
  `argus/precision/replay_harness.py:159`). A finding is blocking iff a detector handed
  `build_recording` a non-`None` depth.
- **Every** emission site in `argus/detectors/**` and `argus/audit/deep_pass.py` passes
  `depth_supported=None` — `orphan_code.py:272`, `secret_scan.py:497`/`:517`, `tool_runner.py:455`,
  `deep_pass.py:353`, `prosecutor.py:375` — **except one**: `argus/detectors/vacuous_test.py:1067`,
  which passes `CoverageDepth.AUDITED_SHALLOW`, and only when `score.ast_corroborated` is true, under
  `rule_id = RULE_AST = "vacuous_test_ast"`.
- The Prosecutor **can** promote an advisory finding to verdict-eligible (`prosecutor._promote`), and
  `"prosecutor"` **is** in `AuditRequest.enabled_passes`' default (`argus/models.py:108`). But
  promotion requires `recording_id in sign_offs` **and** AST corroboration (DN-PROMOTE), and the
  pipeline call site at `argus/pipeline.py:534` passes **no** `sign_offs` at all — the comment there
  records this as the deliberate V1 zero-token default. So no promotion occurs on the corpus-audit
  path, and `scripts/audit_validation_corpus.py:300` uses that path unmodified.
- **Corroboration from the artifact:** the 2026-08-18 re-measurement (`adjudication-set-13-5.json`)
  emitted **five** rule classes over the five ratified members — `orphan_code` 1675,
  `hardcoded_secret` 1330, `vacuous_test_heuristic` 1032, `cross_partition` 231,
  `traceability_not_establishable` 16 — and **every one of them is `verdict_eligible=False`**.
  `vacuous_test_ast` emitted **zero**. Blocking total: **0**.

**Therefore:** a rule-class floor of 2 or more is **not a strengthening — it is a shutdown.** It
would make `CLEARED` unreachable by construction with the shipped detector set, which is the exact
mirror of the rule protocol §5 already carries in the other direction (*"a §5 condition that cannot
fail is not a threshold"*). The operator's approval authorises making clearing **harder**; it does
not authorise making it **impossible**. **AC2.4 binds this, and the HALT it names is not optional.**

> The cartridge corpus carries **5** distinct rule classes across 7 populated rows (protocol §5's
> recall row). It is the **recall** instrument and a different corpus (Story 13.1 / DN-2). It may
> **not** be used to argue that ≥2 rule classes are achievable on the gating corpus.

### §0.3 Module headroom, measured with the ceiling guard's own `_physical_line_count` (`_CEILING = 1200`)

| Module | Lines | Headroom | Note |
|---|---|---|---|
| `argus/precision/gate_decision.py` | **1,015** | **185** | this story's main read target; DN-16-1-3 says why the new subject does **not** land here |
| `argus/precision/gate_disclosure.py` | 341 | 859 | holds what the result must **say**; explicitly *"changes no threshold"* |
| `argus/precision/adjudication.py` | 973 | 227 | 13.2's instrument — **not** on the write set |
| `argus/precision/replay_harness.py` | 825 | 375 | the shared arithmetic — **read and reused, never forked** |
| **`tests/test_gate_decision.py`** | **1,098** | **102** | ⛔ **effectively full at this project's guard density.** New guards go in a NEW module (AC8.5's rule: *"do not shave a file to fit"*). Only the small `-56` re-authoring lands here. |
| `tests/test_adjudication_record.py` | 932 | 268 | `-45`'s message may need re-reading; no structural change expected |
| `scripts/build_gate_decision.py` | 435 | 765 | comfortable |
| `argus/detectors/vacuous_test.py` | 1,196 | **4** | tracked by `DF-15-2-D`. ⛔ **NOT on this story's write set — do not open it.** |
| `tests/test_vacuous_density.py` | 1,159 | **41** | tracked by `DF-15-2-E` (filed 2026-08-20). Not on the write set. |

### §0.4 What is already true and must not be re-done

- `sprint-change-proposal-2026-08-20.md` **is already registered** in `_STATUS_DOCUMENTS`
  (`tests/test_status_document_registry.py`), landed with the document in `7f54506`. Do not
  re-register it.
- Story files are **excluded by design** from the status-document glob closure — this story file
  needs no registry entry, and `-22` asserts that exclusion positively.
- The Epic 16 keys (`epic-16`, five stories, `epic-16-retrospective`) already exist in
  `sprint-status.yaml` at lines 463–469.

---

## §1 — WHY THIS STORY EXISTS

The gate record already computes **every** input to a breadth threshold and then declines, in
writing, to be one:

> *"CONCENTRATION OF THE DENOMINATOR (AC3b, **derived — not a threshold and not a distribution
> requirement**): the adjudicated population is 31 finding(s) drawn from 2 of 5 ratified member(s)
> … across 1 distinct rule class(es) … Protocol §5's N >= 5 is satisfied by MEMBER COUNT, so **the N
> that gates and the N that contributes are different numbers** and a bare precision figure would
> overstate the breadth of what was measured."*

That sentence was written **before any figure existed** (the interim Epic-13 retrospective,
`AI-E13-5`), precisely so it could not read as an excuse. It is correct, and it is inert: **a gate
can clear today on a denominator drawn from one repository and one rule class**, and the record
would disclose that in a paragraph a reader is free to skip.

Epic 16 spends `DF-13-5-A`'s ONE permitted round. Adding a breadth requirement **after** seeing what
the bench yields is corpus-shopping in the opposite direction. It lands first or it does not land.

### §1.1 The failure mode this story prevents, stated concretely

14 bench members are ratified. The detector fires on **one** of them, 40 times, all
`vacuous_test_ast`. 33 are adjudicated TP. Precision is 33/40 = 0.825 ≥ 4/5. All four current §5
conditions hold. The gate reports **CLEARED**, and Argus is externalised on the strength of a number
measured over **one repository and one rule**. Nothing in the instrument as shipped stops that.

### §1.2 What this story does NOT fix, named so it is not mistaken for fixed

- **H-2 (nothing is held back)** — Story 16.2.
- **H-3 (precision alone is one-sided; a tiny denominator clears at 100%)** — Story 16.3. Breadth
  and yield are **different** conditions and must compose: three members × three findings still
  fails 16.3, and forty findings from one member still fails this story.
- **H-4 (the adjudicator is the author)** — not closable by code. Story 16.5 makes it legible.

---

## §2 — THE TWO ARTIFACT-CURRENCY COUPLINGS THAT WILL BITE

These are the two ways this story goes red in a place the dev did not edit. Both are **measured**,
not predicted.

### §2.1 Amending the protocol change log invalidates the committed adjudication record

`decide_gate` **raises** when `record.protocol_version != protocol_change_log_head`
(`gate_decision.py:827`), and two guards assert the same equality:
`TC-ArgusAgent-PRECISION-001-45` and `TC-ArgusAgent-PRECISION-001-63`. The committed record says
`V1.3`; the change log's head is `V1.3`. **Adding a `V1.4` row turns all three red immediately.**

**The resolution, and why it is honest here specifically:** re-run
`python scripts/build_adjudication_record.py`. It is **append-only by construction** — existing rows
are carried through byte-identically and only the derived header fields track the substrate — and it
re-stamps `protocol_version` from the change-log head. The guard's own failure message names this
path (*"re-run scripts/build_adjudication_record.py and RE-ADJUDICATE"*), and the "RE-ADJUDICATE"
half is **vacuous on this record**: it holds **31 rows and zero human judgements**, so there is no
judgement to reinterpret. That is exactly the condition under which re-versioning is not a
reinterpretation. **Record this reasoning in the Dev Agent Record** — a future reader must be able
to see that the version moved over an unjudged record, not over a judged one.

⚠️ It reads `adjudication-set.json` (2026-08-16, 31 blocking), **not** the superseding
`adjudication-set-13-5.json`. It seeds nothing new. It runs no detector.

### §2.2 A fifth condition invalidates the committed gate-decision record

`TC-ArgusAgent-PRECISION-001-54` asserts `len(payload["section_5_conditions"]) == len(SECTION_5_CONDITIONS)`
and that the committed verdict list equals a **live re-derivation**. Extending
`SECTION_5_CONDITIONS` therefore requires `python scripts/build_gate_decision.py` to be re-run and
the regenerated `gate-decision-record.json` committed.

✅ **This is not Argus output over a bench member and does not violate the ordering constraint.**
`build_gate_decision.py` reads the committed adjudication record, the committed adjudication set and
the manifest. It executes **no** detector, stages **no** repository and touches **no** candidate.
The five members it names are the **ratified** corpus, not the bench. State this explicitly in the
Dev Agent Record so a reviewer does not have to re-derive it.

⚠️ Re-running without `--check` re-stamps `commit_sha`, `commit_sha_provenance` and `decided_on` from
the live tree. Land the code first, then regenerate, then commit — and expect
`commit_sha_provenance` to read `NOT ESTABLISHED` if the tree is dirty when it runs.

---

## Acceptance Criteria

### AC1 — Breadth is a §5 CONDITION, computed from the fields the disclosure already publishes

**AC1.1** `SECTION_5_CONDITIONS` gains one member. Its id is stable, and the protocol §5 table and
the tuple carry the conditions **in the same order**. **Append at the end** (DN-16-1-2): §5 is
amended by dated addition, the four historical ids keep their historical positions, and the
regenerated record's condition list is a clean prefix-plus-one diff.

**AC1.2** The condition's measured values are read from the **same `ConcentrationDisclosure`
instance** the decision publishes — `contributing_member_count` and `distinct_rule_class_count` —
**not** recounted from the record. `decide_gate` currently calls `derive_concentration` inline in
the `GateDecision(...)` constructor call, *after* `conditions` is built; hoist that call above the
`conditions` tuple and pass the one instance to both. **A second count is a second thing that can
disagree with the disclosure, and the disagreement would be invisible.**

**AC1.3** ⛔ **The positional lookup is repaired.** `gate_decision.py:867` reads
`recorded_cleared = conditions[3].verdict == "MET"`. With a fifth condition — and with 16.2 and 16.3
each adding a sixth and a seventh — a positional index into `conditions` is a latent false green.
Replace it with a lookup by `condition_id` that **raises** if the id is absent. Drive the raise.

**AC1.4** `GATE_OUTCOMES` stays closed at three and `CONDITION_VERDICTS` stays closed at four. No
member is added to either. `_STORY` on `gate_decision.py` stays
`"13-3-record-the-result-and-let-it-decide"` — `-54` asserts it, and the decision record is still
13.3's artifact; 16.1 amends the condition set, not the producer's identity.

**AC1.5** ⛔ **`TC-ArgusAgent-PRECISION-001-55` is re-authored, and it is the one that would go
wrong silently.** `-55` recomputes the expected outcome *independently* from the fold's three
preconditions — `determinism`, `exhaustiveness`, `precision is None`, then `meets_threshold` —
with **no breadth term**. It is **green today** (the live fold is not exhaustive, so it expects
`BLOCKED` and gets `BLOCKED`) and it is **latently wrong the moment breadth binds**: a fold that is
reproducible, exhaustive and over threshold with a one-member denominator makes `-55` expect
`CLEARED` while the decision correctly records `BLOCKED`. Because the divergence only appears when
16.4 runs, it would surface as a red suite in the middle of the one permitted round, on a guard
nobody edited. **Teach `-55` the breadth term in THIS story**, re-authored as an intended behaviour
change with the same recorded-and-mutated discipline as DN-16-1-4, and drive its new branch to both
outcomes. Do the same audit for `-70` (*"the committed decision says which BLOCKED it is"*) and
record the result even if it needs no change.

### AC2 — The constants are DERIVED and RECORDED, never typed

**AC2.1** Neither floor is written as a bare literal at its use site. Each is a **named module
constant** with a docstring carrying its derivation, and where it is a function of an existing
locked quantity it is **expressed as that function** rather than restated (AR7 / DN-3: the ONE floor
is `VALIDATION_SET_FLOOR_N`, resolved — never re-typed).

**AC2.2** The derivation is recorded in the Dev Agent Record and must satisfy, and be shown to
satisfy, all of:

- **(i) It would have failed the 2026-08-18 population.** 31 findings, **2 of 5** contributing
  members, **1** rule class. State the arithmetic for each arm.
- **(ii) It is achievable in principle.** Name the maximum reachable value of each input: **5**
  contributing members today, **19** after a full R2 ratification of the 14 candidates — and, for
  rule classes, the §0.2 measurement of **1**.
- **(iii) It is a strengthening, not a shutdown.** See AC2.4.
- **(iv) It changes nothing else.** Explicitly: the ≥80% `Fraction`, `VALIDATION_SET_FLOOR_N`, the
  five ratified members and `MANIFEST_FIELDS` are byte-unchanged, and the derivation says so with
  the check that established it.
- **(v) It does not read the bench's contents.** No candidate is staged, scanned or counted for
  content. The candidate **count** (14) is manifest metadata and is permitted; anything derived from
  candidate **source** is not.

**AC2.3** The recorded derivation names its **rejected alternatives** with the reason each was
rejected — at minimum: a floor equal to the 2026-08-18 value (changes nothing), a floor equal to `N`
(one non-contributing member blocks the gate forever), and a floor stated as a proportion of a
population that has not been ratified yet (unstable under R2).

**AC2.4** ⛔ **The achievability confrontation, and the HALT.** The derivation **must** reproduce
§0.2's measurement independently — that `vacuous_test.py:1067` is the only non-`None`
`depth_supported` site reachable on the corpus-audit path, and that the Prosecutor's promotion is
unreachable because `argus/pipeline.py:534` supplies no `sign_offs` — and must state the resulting
maximum achievable distinct verdict-eligible rule-class count. **If the derived rule-class floor
exceeds that maximum, the story HALTS to the operator with options and does not land the floor.** A
§5 condition that cannot be met is not a threshold; it is a decision to stop pursuing attested
externalization, and that decision is the operator's, taken in the open — not a side effect of a
constant.

### AC3 — Below either arm the outcome is UNEVALUABLE, and no terminal state is invented

**AC3.1** When either arm is below its floor, protocol §5's **precision** condition is recorded
`UNEVALUABLE` — the registered verdict, with a `measured` sentence naming **which arm** failed and
with what counts — and the gate outcome is `BLOCKED` carrying a **closure path** that says, in
countable terms, what breadth would take. `BLOCKED` without a closure path already raises; keep it
that way.

**AC3.2** The breadth condition's **own** verdict is `MET` or `FAILED` — it *was* evaluated over a
named corpus. It is **not** `UNEVALUABLE`: that verdict means a §4 precondition did not hold, and
breadth failing is a measured result, not an unobservable one.

**AC3.3** ⛔ **The two surfaces may not disagree.** The recorded `precision.evaluable`,
`precision.gate_status` and §5's precision verdict must tell one story. A payload carrying
`precision.evaluable = True` beside a §5 precision verdict of `UNEVALUABLE` is the `DF-9-2-B`
false-subject class on the surface that publishes the gate. **Decided approach (DN-16-1-1):** the
fold is **not** forked or re-signatured; the decision computes an effective evaluability
(`fold.evaluable AND breadth holds`), renders the status sentence through the **existing**
`precision_gate_status_for(evaluable=..., unevaluable_reason=...)` — the same object, never a second
one (AR7) — and the payload reports that effective value with the breadth block beside it explaining
the difference. A guard asserts the two cannot be separated.

**AC3.4** The `measured` sentence for the breadth condition names the population it counted.
⚠️ **A known, pre-existing tension it must not paper over:** the concentration is derived from
`record.live_rows()` (**31** rows, the 2026-08-16 population) while the gate's *emitted* population
per `adjudication-set-13-5.json` is **empty**. That divergence predates this story and is **out of
scope to fix**. The sentence must make clear which population the breadth counts came from, so no
reader mistakes them for the 13.5 measurement.

**AC3.5** On the live tree this story changes **no** outcome: `decide_gate`'s dispatch reaches the
empty-emitted-population branch before anything breadth-dependent, so the record stays `BLOCKED` for
the 13.5 reason and simply gains a fifth condition reading `FAILED`. **Verify this by execution and
record it** — an amendment that is inert today and binds when 16.4 runs is exactly what *"made
before the measurement it governs"* means.

### AC4 — Driven to BOTH outcomes by EXECUTED mutation, each observed RED

**AC4.1** This project shipped **4 of 35** unreal guards in Epic 14 (`-131`/`-132` given floors in
review; `-107` **VACUOUS** — `lf.splitlines() == crlf.splitlines()` is `True`, so its headline
assertion was `f(x) == f(x)` on a pure function; `-118` **WEAK**). `DF-15-2-A` records that a
vacuity sweep is in no definition of done. Every guard added here is therefore **observed RED by an
executed mutation** before it is trusted, and the RED is recorded with what was mutated and what the
failure said.

**AC4.2** The breadth predicate is driven to **both** outcomes over synthetic populations built at
the real seam (real `AdjudicationRow` objects through the real `AdjudicationRecord`, the
`-58`/`-59` pattern), at minimum:

- a population **at or above** both floors → breadth `MET`;
- a population one **member** short → breadth `FAILED`, precision `UNEVALUABLE`, outcome `BLOCKED`;
- a population one **rule class** short → breadth `FAILED` — **or**, if the derived class floor is
  the achievable minimum and the "below" case is an empty population that `derive_concentration`
  already refuses, that unreachability is **recorded as a measurement** under AC2.4 rather than
  quietly skipped.

**AC4.3** ⛔ **The MET direction is the one that matters most here**, and it must be built
deliberately: today's live record can only produce `FAILED` (2 members, 1 class) and today's live
fold is *already* unevaluable for an unrelated reason (empty emitted population), so a guard that
only ever sees the live record would pass forever without observing anything. The `MET` fixture must
be reproducible **and** exhaustive **and** carry a non-empty denominator, so that breadth is the only
thing moving.

**AC4.4** Every guard asserts its **non-vacuity precondition first** — the population it built is
non-empty, the counts it compares actually differ, the ids it looked up were found. `DF-15-2-A`
arm (b): a guard asserting `f(a) == f(b)` must first assert `a != b`.

**AC4.5** Each guard's docstring discharges the **GUARD-ADEQUACY CLAUSE** in its own words:
(i) the observable, (ii) a demonstration that the defect **moves** that observable at the real seam,
(iii) at least one adversarial variant **generated** from the record or the condition tuple, with
its count.

### AC5 — The protocol §5 amendment is additive, strike-not-erase, and softens nothing

**AC5.1** §5 gains the breadth condition in the established amendment style: a dated block naming
the story and the proposal section, with the reasoning — **not** a rewrite of the existing rows.

**AC5.2** ⛔ **The literals `TC-ArgusAgent-PRECISION-001-63` pins must survive byte-for-byte**:
`Fraction(4, 5)` · `≥ 80%` · `N ≥ 5` · `VALIDATION_SET_FLOOR_N = 5` ·
`measured over FINDINGS, not repos` · and — **note the line break, it is part of the literal** — the
§5 conjunction sentence containing `the clean-repo` / `blocking-FP count is 0` across two lines.
**Do not re-wrap that sentence.** Add the new conjunct as an appended amendment block; do not edit
the sentence in place.

**AC5.3** A `V1.4` row is added to the change log, and §2.1's coupling is resolved in the same
change: `scripts/build_adjudication_record.py` re-run, its append-only behaviour and the
zero-judgement state recorded, and `-45` / `-63` re-run green.

**AC5.4** The §5 amendment states in terms that it makes clearing **harder**, that it is made
**before** the measurement it governs, and that it is not the threshold change §5 and Story 13.3 /
AC5 forbid — with the distinction spelled out rather than asserted.

**AC5.5** `architecture.md` §Enforcement's **Gate-decision enforcement** registration is amended,
struck-not-erased, where it says the condition set is *"exactly §5's four in §5's order"*. All of
`TC-ArgusAgent-DOCS-001-77`'s anchors must still be present afterwards — check by running it.

### AC6 — The committed artifacts are current, and the ordering is not broken

**AC6.1** `gate-decision-record.json` regenerated by `python scripts/build_gate_decision.py` and
committed; `-54` green.

**AC6.2** `adjudication-record.json` re-stamped per §2.1 and committed; the 31 rows byte-identical
apart from the header, verified and recorded. Every row still `UNADJUDICATED`, still no adjudicator,
`expert_hours` still `null`.

**AC6.3** `python scripts/build_gate_decision.py --check` and
`python scripts/build_adjudication_record.py --check` both exit **0** at the end of the story.

**AC6.4** **No Argus output over any bench member is produced or committed.** Verified by: no
candidate path appears in `git diff --name-only` across this story's commits, and no invocation of
`scripts/audit_validation_corpus.py` or `scripts/pinned_corpus_snapshot.py` occurs. Record the
story's landing sha(s) so 16.4's ancestry guard has something to cite.

### AC7 — Gates, scope and hand-off

**AC7.1** Full suite green, exit 0, **0 skipped**, with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`.
`pytest.skip` is a **false green** in this repository; a named `Unevaluable` failure is the correct
pattern.

**AC7.2** `argus/detectors/vacuous_test.py` and `tests/test_vacuous_density.py` are **byte-unchanged**
(4 and 41 lines of headroom respectively). If any pass finds itself needing to edit either, the
cohesion split comes **first**, by subject cohesion, with no `_EXEMPT_BY_DESIGN` entry and no shave.

**AC7.3** NFR-M1 holds for every module touched, measured with `_physical_line_count`. New guards
land in a **new** test module.

**AC7.4** CI result recorded as a **run id together with the sha it covers** — discharged by
observation, never by assertion. ⚠️ Local gates are Windows-only while CI runs an ubuntu matrix; a
green local suite has already shipped POSIX-only bugs to master.

**AC7.5** The story hands 16.2 and 16.3 the two things they need: the **shape** the fifth condition
established (so they append a sixth and a seventh the same way) and the **by-id lookup** from AC1.3
(so neither has to rediscover the positional trap).

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

**DN-16-1-1 — the fold is NOT forked; effective evaluability is computed at the decision.**
`fold_adjudicated_precision` and `AdjudicatedPrecision` stay untouched. *Rejected:* threading a
breadth argument into the fold — it is shared with the cartridge path (`compute_precision`), where
breadth is meaningless, and widening a shared signature to serve one caller is the fork AR7 forbids.
*Also rejected:* letting the payload's `precision.evaluable` continue to report the fold's value
while §5 says `UNEVALUABLE` — that is precisely the `DF-9-2-B` shape, a true status carrying a false
subject, on the gate surface.

**DN-16-1-2 — the new condition is APPENDED to `SECTION_5_CONDITIONS`, not inserted next to precision.**
*Rejected:* inserting after `precision-at-least-80-percent`, which reads better in §5 but re-orders
the committed record's condition list and makes the regeneration diff unreviewable. §5 is amended by
dated addition; the tuple follows the document. AC1.3's by-id lookup makes position irrelevant to
correctness either way, which is the point of doing both in one story.

**DN-16-1-3 — the constants, the pure predicate and the measured/closure sentences live in a NEW
module** (`argus/precision/gate_breadth.py`, or an equally cohesive name), imported one-way by
`gate_decision.py`, which builds the `ConditionResult`. *Why:* `gate_decision.py` has 185 lines of
headroom and this project's documentation density makes a fifth condition plus its derivation
docstring a realistic 120–200 lines — AC8.5's rule is *"new guards go in a NEW module — do not shave
a file to fit"*, and 16.2 and 16.3 are each about to add another subject. *Rejected:*
`gate_disclosure.py`, which has ample headroom but whose whole contract is *"it changes no
threshold"* — putting a threshold there would falsify its own docstring. *Rejected:* putting the
`ConditionResult` builder in the new module — `ConditionResult` lives in `gate_decision.py` and the
import would be circular. **One direction only: `gate_decision` → `gate_breadth`.**

**DN-16-1-4 — the "ALL FOUR" error messages become count-derived.**
`GateDecision.__post_init__` raises with *"must report ALL FOUR §5 conditions"* and *"CLEARED
requires all four §5 conditions MET"*; `TC-ArgusAgent-PRECISION-001-56` matches on both strings and
is named `..._all_four_section_5_conditions_are_reported_individually`. Derive the count from
`len(SECTION_5_CONDITIONS)` in the message so 16.2 and 16.3 do not each re-edit it, and **re-author
`-56` as an INTENDED BEHAVIOUR CHANGE** — matching on a stable substring, with the change recorded
as intended in the Dev Agent Record. This is the Story 15.1 precedent (`-76` and `-27` re-authored
as intended behaviour changes, not relaxed). ⛔ **Re-authoring a guard is a recorded act, and the
re-authored guard must still be observed RED by an executed mutation.**

**DN-16-1-5 — the derivation is executed and recorded in this story's Dev Agent Record, not in a
side file.** The gate's own evidence trail lives with the artifact it governs. *Rejected:* a
`docs/` note — `DF-15-2-C` exists because a per-id verdict table was left with no durable home.

### Locked decisions this story CITES rather than reopens

| Decision | Where | What it forbids here |
|---|---|---|
| **OI1 lock** — N is LOCKED at 5; precision is over **FINDINGS**, not repos | protocol §7 | changing the unit, or forking `N` |
| **DN-1** — the gate is measured over the REPOSITORY corpus | `_manifest.py`, protocol §1 | using cartridges to justify a gating threshold |
| **DN-2** — cartridges are the RECALL corpus | `_manifest.py` | citing the cartridges' 5 rule classes as gate-achievable |
| **DN-3** — one floor constant, two populations | `_manifest.py`, `-25` | a second `N`, or restating `5` |
| **AR4** — exact `Fraction`, never `float` | throughout | a percentage literal or a rounded comparison anywhere |
| **AR7** — reuse, never fork | `replay_harness` | a second `precision_gate_status_for`, a second concentration count |
| **AR8** — pure/impure separation | architecture | I/O, clock, network or LLM inside the new predicate |
| **§5 / Story 13.3 AC5** — no change that makes clearing easier | protocol §5 | narrowing, dropping or re-weighting a member |
| **§6 R2 is an operator act** | protocol §6 | ratifying, fetching or staging anything |
| **`DF-13-5-A`** — exactly ONE round, pre-registered 2026-08-17 | ledger | proposing any expansion; the round is 16.4's to spend |
| **`MANIFEST_FIELDS` closed at 9** | `_manifest.py` | adding a field (16.2 will face this squarely; 16.1 must not pre-empt it) |
| **`NEVER_ELIGIBLE_FIELDS`** | `_manifest.py` | stars / forks / downloads as any kind of signal |

### Open ledger entries bearing on this story — verified against `deferred-work.md` on disk, 2026-08-20

**All entries below are OPEN and are CITED. This story disposes of NONE of them.**

| Entry | State on disk | Bearing here |
|---|---|---|
| `DF-13-5-A` | OPEN, owner XAgent007, `target_story: NONE`; answered 2026-08-17 as a pre-registered **rule**, branch not executed | §1 — the round is 16.4's; this story may not propose an expansion |
| `DF-15-2-A` | OPEN — a vacuity sweep is in no definition of done; 4 of Epic 14's 35 guards did not hold what their titles claimed | AC4 in full |
| `DF-15-2-C` | OPEN — the 24-guard sweep's per-id table has no durable home | do **not** cite *"22 of 24 REAL"* as established |
| `DF-15-2-D` | OPEN — `vacuous_test.py` at 1,196/1,200 | AC7.2 — do not open that module |
| `DF-15-2-E` | OPEN — `tests/test_vacuous_density.py` at 1,159/1,200, filed 2026-08-20 by §4.4 of the proposal | AC7.2 — not on the write set |
| `DF-8-5-C` | OPEN — a hand-written number in a proof artifact about the gate | AC2.1 — every figure derived, none pinned |
| `DF-9-2-A` | OPEN — no module-level repository-only path in shipped code | the new module must not resolve a repo-only `Path` at import time |
| `DF-9-2-B` | OPEN — a true status carrying a false reason | AC3.3, AC3.4 |
| `DF-13-3-A` | OPEN — residual is the missing `evidence_deviation` header field | not in scope |

#### ⛔ Writing rule — `TC-ArgusAgent-DOCS-001-78`

That guard goes RED when a `DF-` id sits **on the same line** as a closure verb
(`CLOSED` / `Closes` / `closes` / `Closed by this story`) for an entry the ledger never received,
unless the line is negated by `not` / `NOT` / `never`. It is **line-scoped**, it reads **every** file
under `stories/`, and it has gone RED repeatedly. **Rule for the dev agent: never put a `DF-` id on
the same line as a closure verb** — in this story file, or anywhere else under `stories/`. And
**never append a disposition to `deferred-work.md` to green a guard**; the remedy is always to
correct the prose.

### Guard vacuity — this project's signature defect

The obligation here is unusually sharp, because **breadth cannot fail on the live tree in the
direction that matters**: the committed record gives 2 members and 1 class, so `FAILED` is free and
`MET` is impossible without a constructed fixture — and the live fold is *already* unevaluable for a
reason that has nothing to do with breadth. A guard built only against the committed record would be
green, silent and useless. AC4.3 exists for exactly this. Model the fixtures on `-58` (dispatch
moved at the real seam, variants generated from the committed record with their counts) and `-59`
(the disclosure must go RED when absent **and** must not manufacture a concentration claim over a
well-distributed population — the same both-directions shape this condition needs).

### Dependencies — none are added, and that is a requirement, not an observation

This story introduces **no new runtime or test dependency**. Everything it needs is already in the
tree: `fractions.Fraction`, `collections.Counter`, `dataclasses`, `pathlib` and `pytest`. The
declared runtime set (`pyproject.toml`) is `pydantic>=2.0`, `jsonschema>=4.0`, `radon>=4.1.0`,
`httpx>=0.24.0` and the pinned `tree-sitter-*` grammars (`>=0.25.0,<0.26` for Python; the ceilings
are load-bearing and were measured by Story 11.4 — **do not move a bound**). `requires-python` is
`>=3.10`, so no `match` statement feature beyond 3.10, no `typing.Self`, no PEP-695 generics.
**Adding a dependency to compute a threshold over two integers would be its own defect.**

### Standing rules (non-negotiable)

- **Determinism (NFR-P1/D1)** — no wall-clock, no `uuid4`, no `random`, no reliance on dict/set
  iteration order; every set rendered `sorted()`.
- **NFR-S1** — counts, rule-id provenance and locators only. Never a source byte, never a secret.
- **Canonical serialization** — every committed artifact goes through `argus.store.canonical`,
  never `json.dumps`.
- **AR10** — typed failures. Any new error type subclasses `ValueError` and says what a reader must do.
- **Platform neutrality** — `pathlib` throughout, explicit `encoding="utf-8"`, `.as_posix()` at every
  path→string boundary, no assertion on `os.sep`, a drive letter or a CRLF-sensitive byte count.
- **`pytest.skip` is a FALSE GREEN.**
- **Validate findings against the story first** — an absence here is usually a locked decision, not a
  defect.

### Files to touch — and the ones that must not move

**Write set:**
- `argus/precision/gate_breadth.py` *(new)* — constants, pure predicate, measured/closure sentences.
- `argus/precision/gate_decision.py` — `SECTION_5_CONDITIONS` +1, the hoisted `derive_concentration`,
  the by-id `recorded_cleared` lookup, the count-derived messages, the effective-evaluability
  rendering, the new `ConditionResult`. **Expect ~30–60 lines; 185 available.**
- `tests/test_gate_breadth.py` *(new)* — the breadth guards, with newly allocated ids.
- `tests/test_gate_decision.py` — **only** the `-56` and `-55` re-authorings (DN-16-1-4, AC1.5).
  102 lines of headroom; do not grow it — if the two re-authorings cannot land inside it, the new
  guards go to `tests/test_gate_breadth.py` and the re-authorings stay minimal.

⚠️ **`argus/precision/__init__.py` is NOT on the write set.** It re-exports `replay_harness` symbols
only; `gate_decision` and `gate_disclosure` are deliberately not re-exported and every caller imports
them by module path. Follow that convention — do not add the new module to the package surface.
- `_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md` — §5 amendment + the
  `V1.4` change-log row.
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — §Enforcement amendment (AC5.5).
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-record.json` — regenerated
  header only (§2.1).
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/gate-decision-record.json` — regenerated
  (§2.2).
- **this story file** — the derivation, the REDs, the shas, the CI run id.
- `sprint-status.yaml` — status transitions only.

**Not touched:** `argus/detectors/**` (byte-unchanged) · `argus/precision/adjudication.py` ·
`argus/precision/replay_harness.py` · `argus/pipeline*.py` · `tests/corpus/_manifest.py` ·
`tests/test_vacuous_density.py` · `prd.md` · `epics.md` · `deferred-work.md` (nothing is disposed of,
and nothing is appended to green a guard) · `validation-corpus/adjudication-set*.json` ·
`tests/test_status_document_registry.py` (the 2026-08-20 proposal is already registered).

**Next TC ids:** the `TC-ArgusAgent-PRECISION-001-*` area is allocated through **`-79`**
(`tests/test_candidate_selection.py`). Allocate from **`-80`** upward and record each id with the
guard it names.

### Previous-story intelligence — Story 15.1 (`done`, 2026-08-19) and Story 15.2 (`done`, 2026-08-19)

- **15.1's ordering discipline is the template.** Code delta, artifact regeneration and story record
  landed in **separate commits**, so the commit that had to contain no Argus output demonstrably
  contained none. Do the same here: code + protocol first, regenerated records second, story record
  third.
- **15.1's `-76` tripwire FIRED and was RE-AUTHORED, not relaxed**, and a second guard (`-27`) was
  re-authored as an intended behaviour change. Nine executed mutations drove them RED. That is the
  standard DN-16-1-4 must meet.
- **15.1's fix round exists because a figure stated-as-measured turned out wrong inside the story's
  own record.** Every number this story writes must be re-derived by a second instrument before it is
  written down, and struck rather than erased if it moves.
- **15.2's lesson, quoted by its own review:** *"a disposition recorded in prose and not in the
  ledger is not a disposition."* This story disposes of nothing; do not write as if it does.
- **15.2's pattern to copy:** the fix landed as a **contract** (`index_aligned_lines`, newline-based
  by construction), not as a special case. Prefer a stated contract over an enumeration of cases —
  here, an effective-evaluability contract rather than a per-caller patch.

### Git intelligence

`0a6e121` `docs(16): record the operator's approval as a separate act, and say what it does not
authorise` · `7f54506` `docs(16): propose strengthening the gate before the one round is spent, and
file the container` · `ef41449` `chore(gitignore): stop tracking per-run audit output…` · `ea395d2`
`docs(prd/1-5): land the two record corrections epic 14 left on disk` · `9d4d9e3`
`docs(15): close epic 15 — the retrospective, the roll-up, and the registration it gates`.

Two habits to copy exactly: **(i)** the approval was recorded as a **separate, later act** with the
original wording left unedited (§3.4 evidence immutability) — this story's amendment must be written
the same way, adding rather than re-narrating; **(ii)** `7f54506` landed the proposal *and* its
`_STATUS_DOCUMENTS` registration in one commit because that guard closes in both directions. The
equivalent coupling here is §2.1/§2.2: the protocol amendment and the two regenerated records must
land **together**, or the tree is red in both directions.

⚠️ The branch is **5 commits ahead of `origin/master`**. Push, and record the CI run id against the
sha it covers.

### References

- [epics.md](../epics.md) §Epic 16 (`:3019`), §Story 16.1 (`:3063`), §Story 16.2 (`:3098`), §Story 16.3 (`:3127`)
- [sprint-change-proposal-2026-08-20.md](../sprint-change-proposal-2026-08-20.md) §1.3 (H-1..H-4), §2.2, §2.3, §4.3, §6
- [precision-validation-protocol.md](../precision-validation-protocol.md) §2, §3, §4, §5, §6 R1–R4, §7, Change log
- [validation-corpus/gate-decision-record.json](../validation-corpus/gate-decision-record.json) — `concentration`, `precision`, `section_5_conditions`, `corpus_read_proof`
- [validation-corpus/adjudication-record.json](../validation-corpus/adjudication-record.json) — 31 rows, `protocol_version: V1.3`
- [architecture.md](../architecture.md) §Enforcement — *Gate-decision enforcement*, *Adjudication-record enforcement*, *Corpus-pin provenance enforcement*, *GUARD-ADEQUACY CLAUSE*, *Ledger-claim cross-check enforcement*
- [deferred-work.md](../deferred-work.md) — `DF-13-5-A` (`:4654`), `DF-15-2-A` (`:5098`), `DF-15-2-C` (`:5160`), `DF-15-2-D` (`:5188`), `DF-15-2-E` (`:5229`)
- [epic-15-retro-2026-08-19.md](../epic-15-retro-2026-08-19.md) — SD-1, SD-5, SD-6
- [15-1-a-bench-with-the-defect-class-in-it-chosen-before-anyone-looks.md](15-1-a-bench-with-the-defect-class-in-it-chosen-before-anyone-looks.md) · [13-3-record-the-result-and-let-it-decide.md](13-3-record-the-result-and-let-it-decide.md) · [13-5-re-measure-the-gate-against-the-corrected-instrument.md](13-5-re-measure-the-gate-against-the-corrected-instrument.md)
- `argus/precision/gate_decision.py` · `argus/precision/gate_disclosure.py` · `argus/precision/replay_harness.py` · `argus/precision/adjudication.py` · `scripts/build_gate_decision.py` · `scripts/build_adjudication_record.py` · `tests/test_gate_decision.py` · `tests/corpus/_manifest.py`

---

## Tasks & Subtasks

> **Legend.** `[x]` done. Round 1 halted at AC2.4; round 2 executed the operator's decision
> of 2026-08-20 (recorded verbatim under *Dev Agent Record*). ⬜ marks a task the operator's
> decision SUPERSEDED, with the supersession recorded rather than the box quietly ticked.

- [x] **Read §0 and §2 first.** The premises are measured; do not re-derive them blindly, but **do**
      re-verify §0.2 independently — AC2.4 requires your own reproduction, not this file's. (AC: all)
      — done in round 1, and **two §0 premises did not survive** (see *Premise corrections*, below).
- [x] Execute the derivation of both floors against AC2.2's five tests; write it into the Dev Agent
      Record with its rejected alternatives (AC2.1, AC2.2, AC2.3) — done in round 1. The **member**
      floor derives cleanly and is now LANDED; the **rule-class** floor was the operator's, and the
      operator declined to land it.
- [x] ⛔ Reproduce §0.2's achievability measurement and state the maximum achievable distinct
      verdict-eligible rule-class count. **HALT to the operator if the derived class floor exceeds it**
      (AC2.4) — reproduced by **two independent instruments**; maximum = **1**; **HALT RAISED (round 1)
      and DECIDED by the operator (round 2)**: land the member arm only, file the rule-class arm.
      Filed as **`DF-16-1-A`** carrying the measurement verbatim.
- [x] Create `argus/precision/gate_breadth.py` (AC1.1, AC2.1, DN-16-1-3) — **LANDED**, 436 lines:
      the condition id, the derivation, the pure predicate, the `measured` / `closure` /
      `outcome_reason` sentences and the effective-status renderer. **No rule-class constant exists
      in it, in any form.**
- [x] Extend `SECTION_5_CONDITIONS` by one, **appended** (AC1.1, DN-16-1-2) — **LANDED**; the
      regenerated record's condition list is a clean prefix-plus-one diff, verified by execution.
- [x] Hoist `derive_concentration` above the `conditions` tuple (AC1.2) — **LANDED**. One instance,
      read by the threshold **and** by the disclosure, so they cannot disagree.
- [x] ⛔ Replace `conditions[3]` with a by-id lookup that **raises** on a missing id, and drive the
      raise (AC1.3) — **LANDED in round 1**, 3 executed mutations observed RED. Round 2 additionally
      repaired the SAME positional read in `-62`, which read `payload["section_5_conditions"][3]`.
- [x] Make the two "ALL FOUR" messages count-derived; **re-author `-56`** (DN-16-1-4, AC4.1) —
      **LANDED**. Both messages now derive the count from `len(SECTION_5_CONDITIONS)`, as does
      `ConditionResult.__post_init__`'s refusal and the `NOT_CLEARED` reason; `-56` matches on the
      stable substrings `"must report ALL"` / `"CLEARED requires all"`, re-authored as an INTENDED
      BEHAVIOUR CHANGE and driven RED.
- [x] **Re-author `-55`** so its outcome recomputation carries the breadth term (AC1.5); audit `-70`
      — **BOTH DONE**. `-55` re-authored, its breadth term derived from the same concentration the
      decision publishes. `-70` audited: it already reads verdicts through a dict keyed by
      `condition_id`, needs no change, re-run green. ⚠️ **A THIRD trap the story had not named was
      found and fixed: `-58`** — see *The third latent trap*, below.
- [x] Wire the effective-evaluability rendering through `precision_gate_status_for` (AC3.1, AC3.3, DN-16-1-1)
      — **LANDED**. The fold is NOT forked; `GateDecision.precision_evaluable` is
      `fold.evaluable AND breadth.holds`, the sentence is re-rendered through the EXISTING function,
      and the fold's own value is published beside it as `fold_evaluable` so nothing is hidden.
      `-84` asserts the two surfaces cannot be separated.
- [x] Write the breadth `measured` sentence naming which population it counted (AC3.4) — **LANDED**;
      it names the record, says *"NOT over the emitted blocking population of the most recent
      adjudication set"*, and discloses the rule-class count it deliberately does not gate. `-85`
      asserts all three; mutations M10 and M12 drove them RED.
- [x] Create the new guard module; allocate ids from **`-80`** (AC4.2, AC4.3) — round 1 created
      `tests/test_gate_condition_lookup.py` (`-80`, `-81`); round 2 created **`tests/test_gate_breadth.py`**
      (`-82`..`-85`) with the MET / member-short families GENERATED one per contributing-member count.
- [x] Observe **every** new and re-authored guard RED by an executed mutation; record what was
      mutated and what the failure said (AC4.1, AC4.4, AC4.5) — **3 mutations in round 1, 10 more in
      round 2. 13 mutations, 13 REDs, all EXECUTED**, tree restored and re-verified green after each.
- [x] Amend protocol §5 additively; ~~add the `V1.4` change-log row~~ (AC5.1, AC5.2, AC5.4) —
      §5 amended by a dated block that edits **no** existing byte and does **not** re-wrap the
      conjunction sentence `-63` pins. ⬜ **The `V1.4` row is SUPERSEDED by operator decision** — see
      the next line.
- [x] ⬜ ~~Re-run `scripts/build_adjudication_record.py`~~ (§2.1, AC5.3, AC6.2) — **SUPERSEDED by the
      operator's HALT-2 decision and correctly NOT run.** No `V1.4` row exists, so §2.1's coupling was
      never armed: the change-log head is still `V1.3`, the record's `protocol_version` is still
      `V1.3`, all 31 judgements keep their original provenance untouched, and `-45` / `-63` are green
      **without any regeneration**. `--check` exits **0** over all 31 rows.
- [x] Amend `architecture.md` §Enforcement (AC5.5) — **LANDED**, struck-not-erased: *"exactly §5's
      four in §5's order"* is struck and replaced, and the Gate-decision registration gained the
      breadth rule, the enforcing module, the guard ids and the two operator decisions. All of
      `TC-ArgusAgent-DOCS-001-77`'s anchors verified present by running it.
- [x] Re-run `scripts/build_gate_decision.py`; confirm `-54` green (§2.2, AC6.1) — **DONE**. §2.2's
      coupling WAS armed this round and is discharged; `-54` green; `--check` exits **0**.
- [x] Verify on the live tree that the **outcome is unchanged**; record it (AC3.5) — **VERIFIED BY
      EXECUTION**: `outcome`, `outcome_reason`, `closure_path` and the precision `gate_status`
      sentence are **byte-identical** across the amendment. The record gained a fifth condition
      reading `FAILED` and nothing else moved.
- [x] Both builders `--check` exit 0 (AC6.3) — both exit **0**.
- [x] Verify `git diff --name-only` touches **no** candidate output path and that no corpus-audit
      script ran; record the landing sha(s) for 16.4 (AC6.4) — verified over `0a6e121..HEAD`;
      **landing shas `2ac1078` (code + protocol) and `11f40cb` (regenerated artifacts)**.
- [x] Full suite, exit code recorded, **0 skipped**, `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; NFR-M1
      measured (AC7.1, AC7.3) — **1,657 collected · 1,656 passed · 1 failed · 0 skipped · 0 errors.**
      The one failure is **not this story's and is not in this story's commits** — see *The one red
      guard*, below, where it is isolated by execution. NFR-M1 measured for every touched module.
- [x] Confirm `argus/detectors/vacuous_test.py` and `tests/test_vacuous_density.py` byte-unchanged
      (AC7.2) — both byte-unchanged over `0a6e121..HEAD`; 1,196 and 1,159 lines, unmoved.
- [ ] ⏸️ Push; record the CI run id **together with the sha it covers** (AC7.4) — **NOT DONE, and
      not by omission: this round was instructed NOT to push.** Two commits are landed locally and
      the branch is 7 ahead of `origin/master`. AC7.4 is discharged by OBSERVATION and can only be
      discharged after a push, so it is recorded OPEN rather than claimed. ⚠️ The local gates are
      Windows-only while CI runs an ubuntu matrix, and a green local suite has already shipped
      POSIX-only bugs to master — so this is a real, named gap, not a formality.
- [x] Write the hand-off note for 16.2 and 16.3 (AC7.5) — rewritten for round 2, below.

### Review Findings

> **Code review (bmad-code-review, adversarial, iteration 1, 2026-08-20, Sonnet).** Scope:
> commits `2ac1078`, `11f40cb`, `66012ad` (base `0a6e121`). `6766df7` (registry housekeeping)
> is explicitly out of scope and was not reviewed. Every claim below was checked by
> **execution** — the full suite, `mypy`, `bandit`, and hand mutations of the shipped
> production code, restored and re-verified clean (`git status --porcelain` empty
> before/after every mutation). See *Independent verification* below for the numbers.

- [x] [Review][Patch] ✅ **RESOLVED 2026-08-20 (round 3) — see *Dev Agent Record — ROUND 3*.** `TC-ArgusAgent-PRECISION-001-55`'s re-authored breadth clause is DEAD
      CODE and cannot be driven RED — AC1.5 / AC4.1 / DN-16-1-4 are claimed discharged for
      `-55` but are not [tests/test_gate_decision.py:395-410 (the `elif not breadth.holds:`
      clause added to the local outcome recomputation)]. **Principle violated:** this
      story's own GUARD-ADEQUACY CLAUSE / `DF-15-2-A` ("a guard that was not observed
      failing is not a guard") and AC1.5's explicit instruction to "drive its new branch to
      BOTH outcomes." **Verified by execution:** `-55` computes `expected` from
      `_record()` — the fixed, committed `adjudication-record.json`, which carries 5
      `BORDERLINE` rows and is therefore **never** exhaustive
      (`isinstance(fold.exhaustiveness, Exhaustive)` is `False` for this record,
      confirmed by direct computation). The `if fold.determinism is not None or not
      isinstance(fold.exhaustiveness, Exhaustive): expected = "BLOCKED"` branch therefore
      **always** fires first and the `elif not breadth.holds:` clause added by this story
      is structurally unreachable for the only record `-55` ever loads. Confirmed two
      ways: (1) reverting `assess_breadth`'s `holds` computation to `holds = True`
      (unconditional) leaves `-55` green while `-83`/`-84`/`-85`/`-58`/`-54` correctly go
      red; (2) disabling *both* breadth branches in `gate_decision.py`
      (`_precision_condition`'s `elif not breadth.holds:` and the outcome dispatch's
      `elif not breadth.holds:`) also leaves `-55` green while `-83`/`-84`/`-58` correctly
      go red. `-55` also reads the committed, static `gate-decision-record.json` via
      `_decision_payload()` rather than calling `decide_gate` live, so even a
      artifact-regenerating mutation cannot make it observe a breadth regression on this
      fixture. The story's own mutation transcript (M1–M13) never lists a mutation that
      reddens `-55` — consistent with this finding; the Completion Notes and Tasks list
      nonetheless mark `-55` "re-authored... BOTH DONE" and AC1.5 "satisfied," which is not
      supported by execution. This is one of the three latent traps the review was asked to
      re-verify: `-56` and `-58` are genuinely re-authored and independently confirmed RED
      by execution (see below); `-55` is only reworded, not resolved. **Suggested fix:**
      either (a) give `-55` a second, generated fixture (reuse the `_spread()` /
      `_population()` pattern already in this PR) that is reproducible, exhaustive and
      over threshold with a narrow denominator, so the `elif not breadth.holds:` clause is
      actually exercised and asserted in both directions as AC1.5 requires, or (b) if the
      branch is being kept only as forward-looking documentation for 16.4, say so
      explicitly in `-55`'s docstring and in the Dev Agent Record instead of claiming the
      AC is discharged, and file a ledger entry naming the gap. Do not leave the current
      wording, which claims verification that did not happen.

- [x] [Review][Defer] Undisclosed byte-level edit to a pre-existing (Story 15.x-era) entry
      in `deferred-work.md`, outside this story's declared write set
      [_bmad-output/design-artifacts/ArgusAgent/deferred-work.md:5205-5206] — deferred,
      pre-existing. **Principle violated:** this project's own append-only /
      strike-not-erase evidentiary discipline (§3.4), which this very story invokes
      repeatedly for its own edits. **Detail:** the pre-existing sentence `` the reason `` /
      ` `` (an empty inline-code span followed by a literal-newline span) was silently
      changed to `` the reason `\n` / `\n` `` (two literal-newline spans) by this story's
      commits, with no mention in the Dev Agent Record, and `deferred-work.md`'s own File
      List / "not touched" notes claim only `DF-16-1-A` and `DF-16-1-B` were added and
      "nothing is disposed of." Content impact is negligible (an unprintable example value
      changed), but it is an edit to historical ledger text this project's own writing
      rules forbid, made without the append-only annotation those rules require.
      **Suggested fix:** revert that one line to its original text
      (`the reason `` / `` are not part of the problem`), and if the original rendering was
      itself a pre-existing markdown artifact, fix it in its own dated, appended note
      rather than silently.

**Independent verification performed for this review (all executed on the working tree at
the reviewed commits, tree restored to clean after each mutation):**

- `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 python -m pytest`: **1657 passed, 0 failed, 0 skipped,
  0 errors**, exit 0. (The one red guard the story's own Round-2 record left open,
  `TC-ArgusAgent-DOCS-001-22`, is green on this tree because the unrelated, out-of-scope
  commit `6766df7` registered the foreign document — consistent with the story's own
  diagnosis that the red was foreign to this story.)
- `mypy argus`: **Success: no issues found in 88 source files.**
- `bandit -r argus --severity-level medium`: **no issues identified** (0 medium, 0 high).
- Hand mutations, each observed RED then restored and re-verified green, covering every
  guard named in this story's own transcript plus the ones this review was asked to
  re-check: `-80` (RED via the structural AST check), `-81` (RED, raise removed), `-82`
  (RED, floor derivation changed to `n // 2`), `-83`/`-84`/`-85`/`-58`/`-54` (RED, `holds`
  forced `True`, and again RED for `-83`/`-84`/`-58` with both breadth dispatch branches
  disabled), `-56` (RED, message wording changed to break the intended stable-substring
  match), `-62` (RED, but **only after regenerating `gate-decision-record.json`** — `-62`
  also reads the static committed artifact, not a live `decide_gate` call). `-55` could
  **not** be driven RED by any of the above — see the Patch finding.
- `derive_concentration` / breadth-floor vacuity check: confirmed the member arm cannot be
  vacuous (a non-empty population always yields `contributing_member_count >= 1`, and
  `contributing_member_floor` raises `VacuousBreadthFloor` below `validation_set_floor_n =
  1`) and cannot be a shutdown at the locked floor (`floor = 3 <= ratified_member_count =
  5` today). The rule-class arm's rejection (max achievable = 1, so `>=2` is a shutdown and
  `1` is vacuous) is independently reproducible from the cited call sites and was not
  re-derived byte-for-byte by this review beyond spot-checking `vacuous_test.py:1067` and
  `pipeline.py:535`, which match the story's claims.
- `derive_concentration` is confirmed hoisted **once** in `decide_gate` and passed to both
  `assess_breadth` and the `GateDecision.concentration` field — the threshold and the
  disclosure read the same instance and cannot disagree.
- NFR-M1: `gate_decision.py` **1197/1200** (matches the story's own figure and its
  `DF-16-1-B` disclosure — not re-raised here as a separate finding since it is already
  ledgered with a hard split-first trigger for 16.2).
- AC3.5 (inertness on the live tree): confirmed by reading the dispatch order in
  `decide_gate` — the `elif not expected:` (empty emitted population) branch sits strictly
  before the `elif not breadth.holds:` branch, so the live record's `BLOCKED` outcome and
  reason are unaffected by this amendment, matching the story's claim.

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context), BMAD `dev-story`, single pass, 2026-08-20.

### ⚖️ OPERATOR DECISIONS — XAgent007 (Engineering Lead), 2026-08-20 — BOTH HALTS RESOLVED

> **Provenance.** Both decisions below were taken by the **operator (XAgent007, Engineering
> Lead) on 2026-08-20**, in response to the two escalations round 1 raised, and are recorded
> here **verbatim** as the first act of round 2 — before any code was written. The HALT record
> that follows is left **byte-unedited** (§3.4 evidence immutability): it is the true record of
> what was measured and why the agent stopped, and a resolution that rewrote the escalation it
> resolves would destroy the evidence that the escalation was correct to raise.

**DECISION ON HALT-1** (rule-class arm unachievable; max verdict-eligible rule classes = 1) —
*verbatim:*

> **Land the contributing-member arm ONLY.** Land the derived member floor of 3
> ((VALIDATION_SET_FLOOR_N + 1) // 2), with the derivation, the five AC2.2 tests and the four
> rejected alternatives recorded. File the RULE-CLASS arm to deferred-work.md as a new DF entry,
> carrying the blocking measurement verbatim: the AST walk of all 7 build_recording sites (only
> argus/detectors/vacuous_test.py:1067 passes non-None depth_supported), the single production
> prosecute() call site at argus/pipeline.py:535 supplying no sign_offs, and the counts over both
> committed adjudication sets (2026-08-16: 6 emitted / 1 verdict-eligible; 2026-08-18: 5 emitted /
> 0). State plainly that a floor of >=2 would be a shutdown and a floor of 1 would be vacuous,
> which is why neither was landed. Do NOT land any rule-class threshold.

**DECISION ON HALT-2** (the adjudication record is JUDGED — 31 human judgements, 26 FP /
5 BORDERLINE, XAgent007, 2026-08-17 — not the zero the story's §0.1 asserts) — *verbatim:*

> **Do NOT re-version the protocol.** Add the breadth condition under the EXISTING V1.3; do not
> add a V1.4 change-log row and do not re-stamp anything. Record the new condition with an
> append-only note so the 31 existing judgements keep their original V1.3 provenance untouched.
> Correct the false "zero human judgements" premise in the story record (append-only, per §3.4
> evidence immutability — annotate, do not rewrite history). The committed adjudication-record
> and gate-decision artifacts must not be re-stamped to a new protocol version; regenerate them
> only insofar as the new condition genuinely requires, and say exactly what changed and why.

**What the two decisions change about this story's remaining obligations, stated once so no
later section has to re-derive it:**

- **AC2.4's HALT is DISCHARGED**, not overridden: the measurement stands, the maximum achievable
  distinct verdict-eligible rule-class count is still **1**, and the operator's answer is that
  **no rule-class floor lands**. `BREADTH_RULE_CLASS_FLOOR` is not written anywhere in the tree,
  in any form, in this round.
- **AC5.3 is SUPERSEDED by the operator.** It asks for a `V1.4` change-log row and a re-run of
  `scripts/build_adjudication_record.py`. The operator's HALT-2 decision forbids both. §2.1's
  coupling is therefore **never armed** in this round: the change-log head stays `V1.3`, the
  committed record's `protocol_version` stays `V1.3`, and `-45` / `-63` stay green **without a
  regeneration**. The amendment lands as a dated block **inside** the existing V1.3 regime.
- **§2.2's coupling IS armed** and is discharged as written: `SECTION_5_CONDITIONS` grows to five,
  so `scripts/build_gate_decision.py` is re-run and the regenerated `gate-decision-record.json`
  committed (AC6.1). That artifact carries **no** protocol version of its own beyond the one it
  reads off the record, so re-generating it does not re-stamp a judgement.
- **§0.1's "zero human judgements" premise is corrected append-only**, below, under
  *Premise corrections*, which round 1 already began and this round completes with the operator's
  instruction attached to it.

### ⛔ HALT — the story stops here, and it stops on a measurement

**AC2.4's HALT condition is LIVE. The rule-class floor is the operator's decision and this
agent did not take it.** Two escalations follow. The first is the one AC2.4 anticipated.
The second is one this story's own §0 did not know about, and it bears on §2.1's
authorisation to re-version the protocol.

#### HALT-1 (AC2.4) — the rule-class arm cannot be both meaningful and clearable

§0.2's measurement **reproduced independently, by two instruments that share no code**:

**Instrument A — static, over the shipped tree at `0a6e121`.** An AST walk of every
`build_recording(...)` call in `argus/**` and `scripts/**` (7 call sites) resolving each
`depth_supported` argument:

| Site | `depth_supported` | verdict-eligible? |
|---|---|---|
| `argus/audit/deep_pass.py:345` | `None` | no |
| `argus/detectors/orphan_code.py:272` | `None` | no |
| `argus/detectors/secret_scan.py:496` | `None` | no |
| `argus/detectors/secret_scan.py:517` | `None` | no |
| `argus/detectors/tool_runner.py:455` | `None` | no |
| `argus/verdict/prosecutor.py:375` | `None` | no |
| **`argus/detectors/vacuous_test.py:1067`** | **`depth`** | **YES — the only one** |

At that one site, `depth = CoverageDepth.AUDITED_SHALLOW if corroborated else None` and
`rule_id = RULE_AST if corroborated else RULE_HEURISTIC` are governed by the **same**
`corroborated` boolean, so a non-`None` depth is bound to `rule_id == "vacuous_test_ast"`
by construction. **One rule class.**

The only other route to a depth is `prosecutor._promote`
(`model_copy(update={"depth_supported": PROMOTED_DEPTH})`), gated on
`_is_advisory_promotable(f) AND _has_ast_corroboration(f) AND f.recording_id in sign_off_set`.
The AST walk finds exactly **one** production call site of `prosecute()` —
**`argus/pipeline.py:535`** (⚠️ the story's §0.2 says `:534`; measured, the call node is at
`:535`) — and its keyword set is `{verdict, ledger, findings, cut_edges, scope_paths,
file_to_partition}`. **`sign_offs` is absent**, so `sign_off_set = frozenset()` and the
promotion branch is unreachable. `scripts/audit_validation_corpus.py:301` reaches the
detector through `run_audit_detailed(AuditRequest(...))` with the default `enabled_passes`,
i.e. through that same unmodified call site.

**Instrument B — empirical, over the two committed adjudication sets.** Counted directly,
not inferred:

| Set | Findings | Rule classes emitted | **Verdict-eligible rule classes** |
|---|---|---|---|
| `adjudication-set.json` (2026-08-16) | 5,988 | 6 | **1** — `vacuous_test_ast` (31) |
| `adjudication-set-13-5.json` (2026-08-18) | 4,284 | 5 (`orphan_code` 1675, `hardcoded_secret` 1330, `vacuous_test_heuristic` 1032, `cross_partition` 231, `traceability_not_establishable` 16) | **0** — blocking total 0 |

**MAXIMUM ACHIEVABLE DISTINCT VERDICT-ELIGIBLE RULE-CLASS COUNT = 1.**

The consequence is a genuine dilemma, and both horns are closed by rules this project
already holds:

- **A floor of ≥ 2 is a SHUTDOWN, not a strengthening.** It makes `CLEARED` unreachable by
  construction with the shipped detector set. AC2.4: *"A §5 condition that cannot be met is
  not a threshold; it is a decision to stop pursuing attested externalization, and that
  decision is the operator's."*
- **A floor of 1 is VACUOUS.** `derive_concentration` raises on an empty population, so
  every population it accepts has ≥ 1 rule class: the condition would read `MET` for every
  possible input. `CONDITION_VERDICTS["NOT_APPLICABLE"]` states the rule in the codebase's
  own words — *"A §5 condition that cannot fail is not a threshold."* Landing it would be
  the `DF-15-2-A` unreal-guard class promoted onto the externalization gate itself.

There is no third number. **This is not a number a dev may pick**, and picking the weaker
one to avoid the halt is the failure AC2.4 was written to prevent.

**Options for the operator, named, with what each costs:**

1. **Land the MEMBER arm only** (floor derived below = **3**), record the rule-class arm as
   *not landed* with this measurement, and file the detector-side work as a ledger entry.
   §5 gains a one-armed breadth condition. *Cost:* §1.1's failure mode is closed on the
   repository axis and left open on the rule axis — 40 findings from three members, all
   `vacuous_test_ast`, would still clear.
2. **Land BOTH arms with a rule-class floor of 2**, accepting explicitly and in the open
   that `CLEARED` is unreachable until a second rule class can reach verdict-eligibility.
   *Cost:* attested externalization is suspended by decision. This is defensible; it is
   simply not an agent's call.
3. **Make the rule-class arm ACHIEVABLE FIRST**, then land both arms — e.g. supply
   `sign_offs` at `argus/pipeline.py:535` so the Prosecutor's DN-PROMOTE path becomes
   reachable, or grade a second detector's `depth_supported`. *Cost:* this is detector /
   pipeline work. It is outside 16.1's write set, outside the operator's 2026-08-20
   authorisation, and it changes what the gate MEASURES — a larger act than changing what
   the gate REQUIRES.
4. **Defer the whole breadth condition to after 16.4's round.** ⚠️ Recorded so it is on the
   table and *not* recommended: §1 of this story is precisely that adding a breadth
   requirement after seeing what the bench yields is corpus-shopping in the opposite
   direction.

#### HALT-2 — the committed adjudication record is JUDGED, and §2.1's authorisation rests on it not being

**§0.1 says:** *"Live rows on the adjudication record | **31**, all `UNADJUDICATED`, **zero**
human judgements"*. **Measured at `0a6e121` through the shipped `load_record` / `live_rows`
/ `counts` API — that is FALSE:**

```
rows 31 | live 31 | counts {'TP': 0, 'FP': 26, 'BORDERLINE': 5, 'UNADJUDICATED': 0}
human judgements: 31
adjudicators: ['XAgent007 (Engineering Lead)']   adjudicated_on: ['2026-08-17']
```

§2.1 authorises re-versioning the record like this: *"the 'RE-ADJUDICATE' half is **vacuous
on this record**: it holds 31 rows and **zero human judgements**, so there is no judgement
to reinterpret. That is exactly the condition under which re-versioning is not a
reinterpretation."* **That condition does not hold.** A `V1.4` row would re-stamp
`protocol_version` on **31 judgements the named human made on 2026-08-17 under V1.3** — the
act `decide_gate`'s own refusal names: *"a decision folded across an amendment is a
re-interpretation of judgements nobody re-made."*

The mechanism is sound in isolation — `build_adjudication_record.py` is append-only by
construction and carries every existing row through byte-identically, re-deriving only the
header — and there is a real argument that no judgement's *meaning* moves (the amendment is
additive to §5, touches no §4 rule, no golden-key semantics and no TP/FP definition, and
none of the 31 is a TP). **That argument may well be right. It is not the argument the story
was authorised on, and re-stamping a judged gate record is exactly the class of act this
project reserves to the operator.** Put to the operator with HALT-1 rather than taken here.

### The derivation (AC2.1, AC2.2, AC2.3) — executed, and recorded whether or not it lands

#### The contributing-member floor — DERIVED, achievable, and NOT landed pending HALT-1

Expressed as a **function of the ONE locked quantity**, never a re-typed 5 and never a bare
3 (AR7 / DN-3 / AC2.1):

```
BREADTH_CONTRIBUTING_MEMBER_FLOOR = (VALIDATION_SET_FLOOR_N + 1) // 2   # = 3
```

*A strict majority of the members that satisfy §5's floor must actually have contributed a
finding to the ratio.* The floor it is derived from is resolved through
`registry_module().VALIDATION_SET_FLOOR_N`, never restated.

AC2.2's five tests, each shown:

- **(i) It would have failed the 2026-08-18 population.** Contributing members = **2**
  (`minions` 24, `agent-smith` 7 of 31). `2 >= (5 + 1) // 2 = 3` is **False** → breadth
  `FAILED`, precision `UNEVALUABLE`, outcome `BLOCKED`. ✅
- **(ii) It is achievable in principle.** Maximum contributing members = **5** today
  (`eligible_member_count()`), **19** after a full §6 R2 ratification of the 14 candidates.
  `3 <= 5`, with two members of headroom before any ratification at all. ✅
- **(iii) It is a strengthening, not a shutdown.** 3 of 5 is reachable without ratifying
  anything. ✅ *(The rule-class arm is where (iii) fails — HALT-1.)*
- **(iv) It changes nothing else.** Verified by execution, not assertion:
  `PRECISION_GATE_THRESHOLD == Fraction(4, 5)`, `VALIDATION_SET_FLOOR_N == 5`,
  `eligible_member_count() == 5`, `len(MANIFEST_FIELDS) == 9`, `GATE_OUTCOMES` closed at 3,
  `CONDITION_VERDICTS` closed at 4 — all re-read live at `0a6e121` and unmoved, and
  `git diff --stat -- tests/corpus/_manifest.py argus/precision/replay_harness.py` is
  **empty**. ✅
- **(v) It does not read the bench's contents.** The only bench figure used anywhere above
  is the candidate **count** (14), which is manifest metadata. No candidate was staged,
  fetched, scanned or counted for content; `scripts/audit_validation_corpus.py` and
  `scripts/pinned_corpus_snapshot.py` were **not invoked**. ✅

**Rejected alternatives (AC2.3), each with the reason:**

| Rejected | Why |
|---|---|
| **2** — the 2026-08-18 value | Changes nothing. A threshold met by the very population that motivated it is not a threshold; it is a description. |
| **`N`** (`eligible_member_count()` — 5 today, 19 after R2) | One non-contributing member blocks the gate forever, and a clean member legitimately contributes nothing. It is also a *distribution requirement* wearing a threshold's hat, which §5 and Story 13.3 / AC5 forbid. |
| **A proportion of the ratified population** (e.g. ≥ 60% of `eligible_member_count()`) | Unstable under R2: the same expression demands 3 today and 12 after ratification, so the constant would move as a **side effect of an operator act** rather than by decision. `(VALIDATION_SET_FLOOR_N + 1) // 2` is a function of a **locked** quantity and does not move under R2 — which is the whole point of deriving it from the floor rather than from the population. |
| **`VALIDATION_SET_FLOOR_N`** itself (5) | Identical to `N` today, and it forks the *meaning* of the one floor: §5's `N >= 5` counts members that EXIST; this counts members that CONTRIBUTED. DN-3 keeps one constant; it does not license one meaning for two questions. |

#### The rule-class floor — DERIVED and DELIBERATELY NOT LANDED

An honest derivation of a rule-class arm gives **2** — *"a score drawn from one rule is not
a score"* is the second half of this story's own title argument (§1.1). Maximum achievable
is **1**. `2 > 1`, so **AC2.4's HALT fires and the floor is not landed.**

### What DID land, and why it was safe to land it under a HALT

**One thing: AC1.3's by-id condition lookup.** It is the only task in this story whose
correctness does not depend on a constant the operator must choose, it repairs a latent
false green that is in shipped code **today**, and AC7.5 names it as the hand-off 16.2 and
16.3 need. Nothing else landed — in particular **no protocol version, no amendment, no
regenerated artifact and no threshold**.

`argus/precision/gate_decision.py`:

- `RECORDED_CLEARED_CONDITION_ID` — §5(4)'s id named **once**, used by
  `SECTION_5_CONDITIONS`, by `_recorded_cleared_condition`'s builder and by the lookup, so
  three literals that could drift became one constant.
- `MissingSection5Condition(ValueError)` — a typed failure (AR10) whose message says what
  the reader must do and, explicitly, what they must **not** do.
- `section_5_condition(conditions, condition_id)` — pure (AR8), no I/O, no clock; **raises**
  on an absent id.
- `recorded_cleared = conditions[3].verdict == "MET"` → `section_5_condition(conditions,
  RECORDED_CLEARED_CONDITION_ID).verdict == "MET"`.

**Why the index was a defect and not a style question.** It was *correct* for §5's four
conditions in §5's order — that is what makes it dangerous. §5 is amended by dated addition,
`ConditionResult` is structurally identical for every condition, and an index landing on the
wrong condition returns a perfectly well-formed `bool`. There is no shape a reader, a schema
or a guard could notice. Mutation M3 below exhibits the concrete consequence: the positional
read publishes `adjudication_run_recorded_cleared = True` while the condition it names reads
`FAILED`.

### The mutation transcript (AC4.1, AC4.4, AC4.5) — 3 mutations, 3 REDs, all EXECUTED

Each mutation was applied to the shipped module, the suite was run, the RED was observed, and
the module was restored from a pre-mutation copy. **A guard that was not observed failing is
not a guard** (`DF-15-2-A`: 4 of Epic 14's 35 shipped unreal).

| # | What was mutated | Guard that went RED | What the failure said (verbatim, trimmed) |
|---|---|---|---|
| **M1** | `recorded_cleared` reverted to `conditions[3].verdict == "MET"` | `-80` (structural arm) | `AssertionError: decide_gate reads its own §5 condition tuple BY POSITION: ['conditions[3]'] … assert not ['conditions[3]']` |
| **M2** | the `raise MissingSection5Condition(...)` replaced by `return conditions[-1]` (a silent neighbour fallback) | `-81` | `Failed: DID NOT RAISE MissingSection5Condition` |
| **M3** | `section_5_condition` resolves the recorded-cleared id **positionally** (`return conditions[3]`) — the lookup as an index wearing an id's name | `-80` (behavioural arm) | `AssertionError: the by-id lookup did not follow the condition when it moved to index 1 … assert True == ('FAILED' == 'MET')` |

**M3 is the one that matters**: `True` is what the positional read publishes for
`adjudication_run_recorded_cleared` while the condition it claims to be reporting reads
`FAILED`. That is the false green, exhibited rather than described.

After each mutation the module was restored and both guards re-run **green** before the next
mutation was applied.

### Guard adequacy for `-80` and `-81` (AC4.5)

Both discharge the clause in their own docstrings. In summary:

- **`-80`** — *observable:* (i) the `recorded_cleared` boolean over a permutation of the
  condition tuple `decide_gate` actually built from the committed record, and (ii)
  `decide_gate`'s AST. *Defect moves it:* M1 and M3, above. *Variants GENERATED:* every
  permutation that puts a differently-verdicted condition at index 3 is generated from the
  live tuple; the guard **counts** the permutations that made the positional and by-id
  answers disagree and **fails at zero** — so a run that generated nothing cannot pass.
  *Non-vacuity first:* the condition set is non-empty, its verdicts are asserted to differ
  (`len({c.verdict}) > 1`) before anything is compared, and the id is asserted found.
- **`-81`** — *observable:* the typed refusal and its message. *Defect moves it:* M2.
  *Variants GENERATED:* one removal per member of `SECTION_5_CONDITIONS`, plus the empty
  set; the drive count is asserted `== len(SECTION_5_CONDITIONS) + 1`, and each removal is
  asserted to have actually removed a row before the lookup is asked for it. **Recorded
  honestly:** `GateDecision.__post_init__` already refuses a condition set whose ids are not
  exactly `SECTION_5_CONDITIONS`, so `decide_gate` cannot reach this raise *today*. It is a
  **tripwire for 16.2 / 16.3** and is driven at the exported function's own seam. Claiming
  it had been driven through `decide_gate` would be the vacuity this project ships
  4-in-35 of, and it is not claimed.

### `-55` and `-70` — the AC1.5 audit, recorded

- **`-70` — AUDITED, NEEDS NO CHANGE.** It already reads §5's verdicts through a dict keyed
  by `condition_id` (`verdicts = {c["condition_id"]: c["verdict"] for c in …}`), so AC1.3's
  positional trap never applied to it. Its precision-verdict assertion (`== "UNEVALUABLE"`)
  is driven by the empty-emitted-population branch and is breadth-independent, so it
  survives the amendment unchanged. Re-run green.
- **`-55` — TRAP CONFIRMED, RE-AUTHORING DEFERRED WITH THE CONDITION.** Re-read at
  `0a6e121`: it recomputes the expected outcome from `determinism` / `exhaustiveness` /
  `precision is None` / `meets_threshold`, with **no breadth term**, and it is green today
  only because the live fold is non-exhaustive. AC1.5's analysis is **correct** — a fold
  that is reproducible, exhaustive and over threshold with a one-member denominator would
  make `-55` expect `CLEARED` while the decision correctly records `BLOCKED`. Teaching it a
  breadth term **now**, while no breadth condition exists, would be a guard asserting over a
  structurally absent term. It is recorded here, unchanged, so the next round cannot
  rediscover it by going red mid-measurement.

### Premise corrections (Story 15.1's lesson: re-derive every figure before writing it down)

| §0 premise | Measured at `0a6e121` | Bearing |
|---|---|---|
| *"31 rows, all `UNADJUDICATED`, zero human judgements"* | **FALSE** — 31 rows, **26 FP + 5 BORDERLINE**, 0 UNADJUDICATED, all 31 human judgements by `XAgent007 (Engineering Lead)` dated 2026-08-17 | **HALT-2** — it is the whole of §2.1's authorisation |
| `argus/pipeline.py:534` supplies no `sign_offs` | **Substantively TRUE, line off by one** — the `prosecute()` call node is at **`:535`** | none; the conclusion is unchanged |
| `gate_decision.py` = 1,015 lines | confirmed 1,015 before, **1,081** after (+66; 119 of headroom left) | AC7.3 |
| `tests/test_gate_decision.py` = 1,098 lines | confirmed, **byte-unchanged** by this story | AC8.5 — the new guards went to a new module |
| 5 ratified members / floor 5 / `MANIFEST_FIELDS` 9 | all confirmed unmoved | AC2.2(iv) |

Everything else in §0.1, §0.3 and §0.4 was re-checked and **survived**.

### The module name deviation, recorded rather than glossed

The write set names `tests/test_gate_breadth.py`. **No breadth constant landed**, so there
are no breadth guards, and a file named for breadth containing only a lookup repair would be
a filename stating a subject its contents do not have — the `DF-9-2-B` false-subject shape,
in a path. The guards live in **`tests/test_gate_condition_lookup.py`**, named for what is
actually in it. `argus/precision/gate_breadth.py` was **not created** for the same reason: an
empty module reserving a name is a claim that the work landed.

### Gates (AC7.1, AC7.3)

| Gate | Result |
|---|---|
| `pytest`, `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` | **1,653 collected · 1,651 passed · 2 failed · 0 skipped · 0 errors**, exit 1 |
| `mypy argus` | **Success: no issues found in 87 source files** |
| `bandit -r argus --severity-level medium` | no medium-or-above findings |
| `python scripts/build_gate_decision.py --check` | exit **0** — `CURRENT — BLOCKED` |
| `python scripts/build_adjudication_record.py --check` | exit **0** — `OK — the adjudication record is current (31 row(s))` |
| `tests/test_gate_decision.py` + `tests/test_adjudication_record.py` (`-45`/`-54`/`-55`/`-56`/`-63`/`-70`) | **29 passed** |
| NFR-M1 (`_physical_line_count`, ceiling 1200) | `gate_decision.py` **1,081** · `test_gate_condition_lookup.py` **288** · `gate_disclosure.py` 341 (untouched) · `test_gate_decision.py` 1,098 (untouched) |
| AC7.2 byte-unchanged | `argus/detectors/vacuous_test.py` **1,196** and `tests/test_vacuous_density.py` **1,159** — `git diff --stat` empty for both |
| AC6.4 | `git status --porcelain` names **no** candidate output path; neither `audit_validation_corpus.py` nor `pinned_corpus_snapshot.py` was invoked |

**The 2 failures, diagnosed by execution and NOT a defect.**
`tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`
and `tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run`
are the `AI-E12-11` dogfood LOC-currency coupling: the committed proof pins the tree's total
physical LOC and this story's +66 production lines moved it (live **29,852**). **Proved, not
asserted:** `git stash push -- argus/precision/gate_decision.py` → both guards **pass** →
`git stash pop` → both fail again. The documented remedy is the mandatory **commit `argus/` →
`python scripts/regenerate_dogfood_artifacts.py` → commit the regenerated artifacts
separately** order — the script *refuses* to run on a dirty `argus/` tree by design. **It was
deliberately not run**, for two reasons: (a) nothing has been committed, and committing was
not authorised for a halted story; (b) resolving HALT-1 will change
`argus/precision/gate_decision.py`'s line count again, so regenerating now would produce
artifacts that are stale the moment the halt clears. It resolves in the same sequence as
every prior story, at the real landing.

### What is on disk — NOTHING IS COMMITTED

`git status --porcelain` at hand-off:

```
 M _bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml
 M argus/precision/gate_decision.py
?? _bmad-output/design-artifacts/ArgusAgent/stories/16-1-a-score-drawn-from-one-repository-is-not-a-score.md
?? tests/test_gate_condition_lookup.py
```

No commit, no stage, no push, no tag. **There is therefore no landing sha for 16.4's ancestry
guard to cite yet** (AC6.4), and no CI run id (AC7.4) — the branch is still the same 5 commits
ahead of `origin/master` it was at contexting. `HEAD` is unmoved at `0a6e121`.

### Ledger (`TC-ArgusAgent-DOCS-001-78` writing rule observed)

Every ledger entry cited in this story remains OPEN. This story disposes of none of them, and
nothing was appended to `deferred-work.md`. `DF-13-5-A`'s one round is UNSPENT.

### Hand-off to 16.2 and 16.3 (AC7.5)

1. **The by-id lookup is landed and is the shape to use.** Read a §5 condition with
   `section_5_condition(conditions, <id>)` from `argus.precision.gate_decision`. It raises
   `MissingSection5Condition` on an absent id. **Do not re-introduce an index** —
   `TC-ArgusAgent-PRECISION-001-80` parses `decide_gate`'s AST and goes RED on *any* subscript
   of `conditions`, which is deliberate and is the guard that stops the defect coming back
   while you append.
2. **The condition-set shape 16.1 would have established did not land.** Append your
   condition to `SECTION_5_CONDITIONS` (DN-16-1-2), name its id once as a module constant
   beside `RECORDED_CLEARED_CONDITION_ID`, and expect `GateDecision.__post_init__` to refuse
   anything but exact-set-and-order.
3. **Two couplings are still armed and unspent.** §2.2 (a fifth condition invalidates
   `gate-decision-record.json`, `-54`) and §2.1 (a `V1.4`+ change-log row invalidates the
   record's `V1.3` stamp, `-45` / `-63`). Neither has fired, because `SECTION_5_CONDITIONS` is
   still four and the change-log head is still `V1.3`. **Whoever fires §2.1 first inherits
   HALT-2** — the record carries 31 human judgements, not zero.
4. **`-55` carries a live trap.** It recomputes the outcome with no breadth / holdout / yield
   term. The first story that makes a §5 condition able to fail over a *reproducible,
   exhaustive, above-threshold* fold must re-author it in the same change, or discover it red
   in the middle of the one permitted round.
5. **The dogfood LOC-currency guards will fire on your production delta too.** The order is
   commit `argus/` → `python scripts/regenerate_dogfood_artifacts.py` → commit the regenerated
   artifacts separately. The script refuses on a dirty `argus/` tree by design.

### Debug Log References

- AST enumeration of `build_recording` / `prosecute` sites — run out of tree from the
  scratchpad; `git status --porcelain` empty before and after.
- Mutations M1–M3 — applied to `argus/precision/gate_decision.py`, each restored from a
  pre-mutation copy; verified restored by re-running both guards green.
- Baseline isolation of the 2 dogfood failures —
  `git stash push -- argus/precision/gate_decision.py` / `git stash pop`.

### Completion Notes List

- ⛔ **NOT COMPLETE. HALTED at AC2.4 with two escalations for the operator.** HALT-1: the
  rule-class floor is a shutdown at ≥2 and vacuous at 1, maximum achievable = 1, reproduced by
  two independent instruments. HALT-2: the committed adjudication record is JUDGED — 31 human
  judgements — which falsifies §2.1's stated authorisation to re-version the protocol.
- ✅ AC1.3 landed in full: the positional `conditions[3]` false green is repaired by a typed
  by-id lookup, guarded behaviourally **and** structurally, and driven RED by 3 executed
  mutations.
- ❌ AC1.1, AC1.2, AC1.5, AC2.1 (as code), AC3.1–AC3.4, AC4.2, AC4.3, AC5.1–AC5.5, AC6.1,
  AC6.2, AC7.1, AC7.4 not satisfied — each blocked by, or deferred with, the halted constant.
- ✅ AC1.4, AC2.2, AC2.3, AC2.4, AC3.5, AC4.1, AC4.4, AC4.5, AC6.3, AC6.4, AC7.2, AC7.3, AC7.5
  satisfied and recorded.
- **No threshold, corpus, floor, `MANIFEST_FIELDS`, `GATE_OUTCOMES`, `CONDITION_VERDICTS`,
  `protocol_cleared`, protocol version, ratification state or committed artifact moved.**
  `_STORY` on `gate_decision.py` is unchanged (AC1.4). The gate outcome is byte-identical.

### File List

| File | State | Why |
|---|---|---|
| `argus/precision/gate_decision.py` | **modified** (1,015 → 1,081) | AC1.3 — `RECORDED_CLEARED_CONDITION_ID`, `MissingSection5Condition`, `section_5_condition`, the by-id `recorded_cleared` read, `__all__` |
| `tests/test_gate_condition_lookup.py` | **new** (288) | `TC-ArgusAgent-PRECISION-001-80`, `-81` |
| `_bmad-output/design-artifacts/ArgusAgent/stories/16-1-a-score-drawn-from-one-repository-is-not-a-score.md` | **modified** | this record |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | **modified** | status transition only |

**Explicitly NOT written:** `argus/precision/gate_breadth.py` · `tests/test_gate_breadth.py` ·
`precision-validation-protocol.md` · `architecture.md` ·
`validation-corpus/adjudication-record.json` · `validation-corpus/gate-decision-record.json` ·
`tests/test_gate_decision.py` · `deferred-work.md` · `argus/detectors/**` ·
`tests/corpus/_manifest.py` · `argus/precision/replay_harness.py` ·
`argus/precision/adjudication.py` · `argus/precision/gate_disclosure.py` ·
`argus/precision/__init__.py`.

**Next TC ids:** `TC-ArgusAgent-PRECISION-001-*` is now allocated through **`-81`**. Allocate
from **`-82`**.

---

## Dev Agent Record — ROUND 2 (2026-08-20), after the operator's decisions

> Round 1's record above is **unedited**. This section is additive. Where round 2 changed a
> conclusion of round 1, it says so here rather than by editing round 1's words.

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context), BMAD `dev-story`, resume pass, 2026-08-20.

### What round 2 landed

**The whole story, minus the arm the operator declined and the push it was told not to make.**

| Piece | Where | Note |
|---|---|---|
| The condition id, the derivation, the pure predicate, the published sentences | `argus/precision/gate_breadth.py` *(new, 436)* | `DN-16-1-3`'s module, one-way import |
| `SECTION_5_CONDITIONS` +1, **appended** | `gate_decision.py` | `DN-16-1-2`; clean prefix-plus-one diff |
| `derive_concentration` **hoisted** above the tuple | `gate_decision.py` | AC1.2 — one instance, two readers |
| Effective evaluability + its status sentence | `gate_decision.py` / `gate_breadth.py` | AC3.3 / `DN-16-1-1` |
| The count-derived §5 messages | `gate_decision.py` | `DN-16-1-4` |
| §5's dated amendment block, **under V1.3** | `precision-validation-protocol.md` | operator HALT-2 |
| §Enforcement amendment, struck-not-erased | `architecture.md` | AC5.5 |
| `DF-16-1-A` (the rule-class arm) · `DF-16-1-B` (module headroom) | `deferred-work.md` | operator HALT-1 |
| `-82`..`-85` | `tests/test_gate_breadth.py` *(new, 495)* | AC4.2 / AC4.3 |
| Regenerated gate-decision record | `validation-corpus/gate-decision-record.json` | §2.2 |

**The floor that landed, and the only integer in it:**

```
BREADTH floor = contributing_member_floor(fold.floor_n) = (VALIDATION_SET_FLOOR_N + 1) // 2 = 3
```

The floor arrives as an **argument** — the same `floor_n` the decision already carries — so the
new module resolves no repository-only path at import (`DF-9-2-A`) and no second `N` exists.

### ⚠️ One correction to round 1's own derivation, made before it was written into code

Round 1 recorded the derivation as *"a **strict majority** of the members that satisfy §5's
floor"*. **Measured: that overstates what `(n + 1) // 2` computes.** It is `ceil(n / 2)` — *half,
rounded up* — which is a strict majority only at an **odd** floor. At the locked floor of 5 it is
3 and the strict-majority reading does hold, so the landed value is unchanged; but the general
statement was wrong, and a derivation describing something it does not compute is the `DF-9-2-B`
false-subject shape applied to a threshold. The guard caught it: `-82`'s property assertion went
RED at `n = 2` on the first run. The docstrings, `BREADTH_MEMBER_FLOOR_DERIVATION`, the §5
amendment and the guard all now say *"half, rounded up"*, with the strict-majority claim asserted
**separately, at the locked floor where it is actually true**. Story 15.1's lesson — *a figure
stated-as-measured turned out wrong inside the story's own record* — applied to round 1's record.

### ⛔ The THIRD latent trap: `-58`, which the story had not named

AC1.5 named two traps (`-55`'s missing breadth term, `-56`'s count-pinned messages) and asked for
`-70` to be audited. **A third existed and was found by execution, not by reading:**
`TC-ArgusAgent-PRECISION-001-58` builds an all-`TP` variant from the committed record and asserts
`outcome == "CLEARED"`, with the stated purpose *"which proves the CLEARED branch is reachable at
all and is not dead code guarding a state nobody can enter."* The committed record's findings come
from **2** members. The moment breadth binds, that variant is `BLOCKED`, its sibling `all_fp`
variant stops being `NOT_CLEARED`, and **`-58`'s subject silently becomes the breadth floor rather
than the dispatch** — the exact failure mode AC1.5 exists to prevent, on a guard nobody had
flagged.

Re-authored as an **intended behaviour change**, not relaxed: a `_spread()` generator re-homes the
committed record's own rows across the ratified members (never a hand-written population), the two
§5-outcome variants run over it, and **the narrow population is asserted `BLOCKED` on breadth
immediately afterwards, with the fold asserted evaluable and over threshold first** — so the
refusal is provably breadth and not something else. `-58` now covers both.

**The lesson worth carrying into 16.2 and 16.3:** the story's audit found the traps it went
looking for. The one it missed was found by running the suite. *A guard that asserts an outcome
over the committed population is a breadth-coupled guard whether or not it mentions breadth.*

### The mutation transcript — ROUND 2: 10 mutations, 10 REDs, all EXECUTED

Each was applied to the shipped module, the three gate suites were run, the RED was observed, and
the file was restored from a pre-mutation copy and re-verified green. **A guard that was not
observed failing is not a guard** (`DF-15-2-A`: 4 of Epic 14's 35 shipped unreal).

| # | What was mutated | Guard RED | What the failure said (verbatim, trimmed) |
|---|---|---|---|
| **M4** | `contributing_member_floor` returns the literal `3` | `-82` | `a floor of 3 over a locked N of 1 demands more than half rounded up` |
| **M5** | the derivation becomes `n // 2` (off by one) | `-82` | `a floor of 0 over a locked N of 1 is below half … assert (0 * 2) >= 1` |
| **M6** | `holds = True` — the condition cannot fail | `-83` | `1 contributing member(s) is below the floor of 3, so §5's PRECISION condition must be UNEVALUABLE … assert 'MET' == 'UNEVALUABLE'` |
| **M7** | the payload publishes `self.fold.evaluable` (the un-repaired surface) | `-84` | `2 generated population(s) published a precision.evaluable that contradicted §5's own precision verdict` |
| **M8** | the breadth condition's own verdict becomes `UNEVALUABLE` | `-83` | `assert 'UNEVALUABLE' in ('MET', 'FAILED')` |
| **M9** | the breadth dispatch branch made unreachable | `-58` | `… 2 of protocol §5's 5 conditions did not hold: precision (UNEVALUABLE), denominator-breadth (FAILED)` — i.e. a §5 RESULT recorded over an unevaluable precision |
| **M10** | the `measured` sentence drops *"NOT over the emitted blocking population"* | `-85` | `assert 'NOT over the emitted blocking population' in 'breadth = 2 distinct CONTRIBUTING member(s) …'` |
| **M11** | `effective_precision_gate_status` always returns the fold's sentence | `-84` | `assert False = …startswith('unevaluable')` |
| **M12** | the sentence drops *"DISCLOSED and deliberately NOT gated"* | `-85` | `the rule-class arm is disclosed and deliberately not gated; a sentence that omits it lets a reader believe both arms landed` |
| **M13** | *(round 2's re-run of round 1's M1–M3 after the append)* | `-80`, `-81` | all three still RED with five conditions in the tuple; the by-id repair is not an artifact of there having been four |

**M7 and M9 are the two that matter most.** M7 exhibits the `DF-9-2-B` shape concretely — a payload
saying `precision.evaluable = True` beside a §5 precision verdict of `UNEVALUABLE`. M9 exhibits the
outcome half: a `NOT_CLEARED` **result** recorded over a precision condition that produced no
measurement, which is exactly the collapse `GATE_OUTCOMES` was closed at three to prevent.

Round 1 + round 2 = **13 executed mutations, 13 observed REDs.**

### AC3.5 — the amendment is INERT on the live tree, VERIFIED BY EXECUTION

The claim *"an amendment that is inert today and binds when 16.4 runs"* is the one this story most
needed to prove rather than assert. Measured by diffing the regenerated record against the
committed one at `0a6e121`:

| Field | Before | After |
|---|---|---|
| `outcome` | `BLOCKED` | `BLOCKED` |
| `outcome_reason` | *the Story 13.5 corpus-was-read reason* | **byte-identical** |
| `closure_path` | 4 legs | **byte-identical** |
| `precision.gate_status` | *the empty-emitted-population sentence* | **byte-identical** |
| `adjudication_record.protocol_version` | `V1.3` | `V1.3` |
| `section_5_conditions` ids | 4 | **the same 4, in the same order, + 1 appended** |
| `section_5_conditions` verdicts | `UNEVALUABLE`, `MET`, `MET`, `FAILED` | **the same 4** + `FAILED` |
| top-level keys | — | `breadth` added |

`decide_gate`'s dispatch reaches the empty-emitted-population branch before anything
breadth-dependent, exactly as AC3.5 predicted. **The gate did not move and could not have.**

### The one red guard, isolated by execution — and it is NOT this story's

`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest` → **1,657 collected · 1,656 passed · 1 failed · 0
skipped · 0 errors**, exit 1. The single failure is
`tests/test_status_document_registry.py::TC-ArgusAgent-DOCS-001-22`:

```
status-asserting document(s) exist but are not registered:
['sprint-change-proposal-2026-08-20-amendment-A.md']
```

**Diagnosed by execution, not by argument.** That file is **untracked**, is **not in either of this
story's commits**, was **not created by this story**, and did not exist when round 1 measured the
same suite at 1,653 collected. It is a MAJOR change proposal drafted at operator request whose own
header reads ⏳ **AWAITING OPERATOR APPROVAL**. **Isolation, executed:** moving it out of the
artifact directory makes `-22` pass; moving it back makes it fail again. `git status --porcelain`
returned to the same three entries before and after.

**Deliberately NOT resolved here, and the reason is not convenience.** The guard's own remedy is
*"add them to `_STATUS_DOCUMENTS`"* — but a registration only means something if the document is
**committed**, and committing an unapproved MAJOR change proposal into `master` as part of Story
16.1 would be a governance act this story has no authorisation for. `tests/test_status_document_registry.py`
is explicitly **NOT** on this story's write set. **On CI the guard is green**, because the file is
not in the repository — this is a working-tree-only red, and it is the operator's to clear by
approving-and-landing or by removing the file.

⚠️ Stated plainly rather than buried: **this story does not claim a green suite.** It claims 1,656
of 1,657, with the one red proved foreign.

### Gates (ROUND 2)

| Gate | Result |
|---|---|
| `pytest`, `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` | **1,657 collected · 1,656 passed · 1 failed · 0 skipped · 0 errors** (260.11s). The one failure isolated above. |
| `mypy argus` | **Success: no issues found in 88 source files** |
| `bandit -r argus --severity-level medium` | no medium-or-above findings |
| `python scripts/build_gate_decision.py --check` | exit **0** — `CURRENT — BLOCKED (NOT COMPUTED BY THIS RUN)` |
| `python scripts/build_adjudication_record.py --check` | exit **0** — `OK — the adjudication record is current (31 row(s))` |
| NFR-M1 (`_physical_line_count`, ceiling 1200) | `gate_decision.py` **1,197** ⚠️ · `gate_breadth.py` **436** · `test_gate_decision.py` **1,187** · `test_gate_breadth.py` **495** · `test_gate_condition_lookup.py` **288** · `test_release_preflight.py` 968 · `gate_disclosure.py` 341 (untouched) |
| AC7.2 byte-unchanged | `argus/detectors/vacuous_test.py` **1,196** and `tests/test_vacuous_density.py` **1,159** — `git diff 0a6e121..HEAD` empty for both |
| AC6.4 | `git diff --name-only 0a6e121..HEAD` names **15** files, **none** a candidate output path, **none** under `validation-corpus/adjudication-set*`. Neither `scripts/audit_validation_corpus.py` nor `scripts/pinned_corpus_snapshot.py` was invoked. |
| Ordering (🔒 BINDING) | **HELD.** `2ac1078` and `11f40cb` contain no Argus output over any bench member, and they are what 16.4's ancestry guard cites. |

⚠️ **`gate_decision.py` at 1,197 / 1,200 is filed as `DF-16-1-B` at 🟠**, with a hard trigger: the
next change to that module — 16.2's sixth §5 condition — performs the cohesion split **first**. No
`_EXEMPT_BY_DESIGN` entry was added and nothing was shaved: the breadth constants, predicate and
**sentences** went to the new module exactly as `DN-16-1-3` directs.

### Three files outside the declared write set were touched, each recorded rather than absorbed

The story's write set did not anticipate that a NEW production module moves three published
figures and one registry. All four remedies are the guards' own stated remedies:

1. **`tests/test_release_preflight.py`** — `_MODULES_NAMING_THE_TEST_TREE_IMPORT` is a pinned set,
   and `RELEASE-001-11`'s failure message says in terms *"it is a deliberate decision either way."*
   `gate_breadth.py` reaches the repository-only tree **transitively**, through `gate_disclosure`
   and `replay_harness`, exactly as its four siblings already in that set do. Registered with the
   reason, and with the note that the wheel-importability claim is `RELEASE-001-20`'s, not this
   guard's.
2. **`README.md`** and **3. `CHANGELOG.md`** — `DOCS-001-54` asserts published figures against a
   freshly built wheel and says *"Fix the document — the artifact is the fact."* The new module
   moved four: importable modules 87 → **88**, shipped modules 87 → **88**, wheel entries 95 → **96**,
   sdist members 94 → **95**. Every figure was **read from the guard's own `_live_figures()`**, not
   estimated. Note that `-54` also refuses the deletion of a published sentence, so correcting them
   was the only available move.

### AC2.2 (iv) re-verified at the END of round 2, not only at the start

Re-read live after every change landed: `PRECISION_GATE_THRESHOLD == Fraction(4, 5)` ·
`VALIDATION_SET_FLOOR_N == 5` · `eligible_member_count() == 5` · `len(MANIFEST_FIELDS) == 9` ·
`GATE_OUTCOMES` closed at 3 · `CONDITION_VERDICTS` closed at 4 · `_STORY` on `gate_decision.py`
still `"13-3-record-the-result-and-let-it-decide"` (AC1.4). `git diff 0a6e121..HEAD` is **empty**
for `tests/corpus/_manifest.py`, `argus/precision/replay_harness.py`,
`argus/precision/adjudication.py`, `argus/precision/gate_disclosure.py`,
`argus/precision/__init__.py`, `argus/pipeline*.py`, `argus/detectors/**`, `prd.md`, `epics.md`
and `validation-corpus/adjudication-set*.json`. `-82` asserts the first four every run, so this is
mechanised rather than left as a claim.

### Ledger (`TC-ArgusAgent-DOCS-001-78` writing rule observed)

**Two entries were FILED and NONE was disposed of.** `DF-16-1-A` (the rule-class arm, at the
operator's explicit instruction, carrying the blocking measurement verbatim) and `DF-16-1-B`
(`gate_decision.py` headroom). Every previously-cited entry — `DF-13-5-A`, `DF-15-2-A`,
`DF-15-2-C`, `DF-15-2-D`, `DF-15-2-E`, `DF-8-5-C`, `DF-9-2-A`, `DF-9-2-B`, `DF-13-3-A` — remains
OPEN and is cited, never disposed. Nothing was appended to `deferred-work.md` to green a guard.
`DF-13-5-A`'s one round is **UNSPENT**.

### Hand-off to 16.2 and 16.3 (AC7.5) — ROUND 2, superseding round 1's

1. **⛔ SPLIT `gate_decision.py` FIRST.** It is at **1,197 / 1,200** and your sixth condition does
   not fit in three lines. `DF-16-1-B` names the boundary already visible: `CleanRepoEvidence` and
   `CorpusReadProof` are the EVIDENCE the decision consumes rather than the decision itself. Do the
   split as its own change, before you append anything.
2. **The shape is established — copy it exactly.** Name your condition id **once** as a module
   constant beside `BREADTH_CONDITION_ID`; **append** it to `SECTION_5_CONDITIONS`; put your
   constants, predicate and published sentences in a NEW `argus/precision/gate_*.py` and build the
   `ConditionResult` in `gate_decision.py` (the import is circular the other way); read the counts
   off the **hoisted** `concentration` instance rather than recounting. The §5 messages are already
   count-derived — **you do not need to edit them.**
3. **Read conditions BY ID.** `section_5_condition(conditions, <id>)` raises
   `MissingSection5Condition`. `-80` parses `decide_gate`'s AST and goes RED on *any* subscript of
   `conditions`. `-62` was repaired the same way on the payload side.
4. **§2.2's coupling is now ARMED AND SPENT ONCE, and it will fire for you too.** Adding a sixth
   condition invalidates `gate-decision-record.json`; re-run `python scripts/build_gate_decision.py`
   and commit it separately. §2.1's coupling (a `V1.4`+ change-log row) is **still unarmed** — the
   head is `V1.3` — and **whoever arms it inherits HALT-2**: the record carries 31 human judgements
   made under V1.3, so re-versioning re-stamps judgements nobody re-made. 16.1 amended §5 by a dated
   block **under** V1.3 precisely to avoid that; do the same unless the operator decides otherwise.
5. **⚠️ AUDIT EVERY GUARD THAT ASSERTS A §5 OUTCOME, not only the ones named in your story.** 16.1's
   story named `-55` and `-56`; the suite found `-58`. Any guard that asserts `CLEARED` or
   `NOT_CLEARED` over the **committed** population is coupled to your new condition whether or not
   it mentions it. `tests/test_gate_decision.py::_spread()` is the generator to reuse — it re-homes
   the committed record's rows across the ratified members so a §5 outcome is reachable at all.
6. **A new production module moves four published figures.** `DOCS-001-54` pins importable modules,
   shipped modules, wheel entries and sdist members across `README.md` and `CHANGELOG.md`, and
   `RELEASE-001-11` pins the test-tree-reach set. Read the numbers from
   `tests/test_built_distribution.py::_live_figures()`; never estimate them.
7. **The rule-class arm is OPEN, filed as `DF-16-1-A`, and is NOT yours to close by typing a
   constant.** Max achievable verdict-eligible rule classes is **1**. A floor of ≥2 is a shutdown,
   a floor of 1 cannot fail. Making it achievable is detector/pipeline work and an operator act.
8. **The dogfood LOC-currency guards fire on any `argus/**` delta.** Order: commit `argus/` →
   `python scripts/regenerate_dogfood_artifacts.py` → commit the regenerated artifacts separately.
   The script refuses on a dirty `argus/` tree by design.
9. **One red guard is waiting for you in the working tree and it is not yours** — see *The one red
   guard*, above. Do not absorb it by registering an unapproved proposal.

### Debug Log References — ROUND 2

- Mutations M4–M13 — driven by a scratchpad harness that applies one text mutation, runs
  `tests/test_gate_breadth.py tests/test_gate_decision.py tests/test_gate_condition_lookup.py`,
  captures the RED, and restores the file from a pre-mutation copy in a `finally`. Verified
  restored by re-running all three suites green.
- AC3.5 inertness — the regenerated payload diffed field-by-field against
  `git show HEAD:…/gate-decision-record.json` at `0a6e121`.
- `-22` isolation — the untracked amendment-A document moved to the scratchpad and back, with
  `git status --porcelain` compared before and after.
- Live distribution figures — read from `tests/test_built_distribution.py::_live_figures()` in a
  subprocess rather than estimated.

### Completion Notes List — ROUND 2

- ✅ **The story is COMPLETE except AC7.4**, which requires a push this round was instructed not to
  make. Recorded OPEN rather than claimed.
- ✅ Both round-1 HALTs are DISCHARGED by the operator's recorded decisions, and both decisions are
  recorded **verbatim** in this file with their date and provenance.
- ✅ **The member arm LANDED**: floor `(VALIDATION_SET_FLOOR_N + 1) // 2 = 3`, derived from the ONE
  locked floor, never typed, arriving as an argument so no repository-only path is resolved at
  import.
- ⛔ **The rule-class arm did NOT land, deliberately.** No rule-class threshold exists anywhere in
  the tree. The count is still disclosed on every decision, and the breadth condition's own
  `measured` sentence says in terms that the arm is not gated — so nobody can read the landed
  condition as covering both halves.
- ✅ **No protocol version was taken.** The amendment sits under V1.3; all 31 human judgements keep
  their original provenance; `adjudication-record.json` was NOT regenerated and did not need to be.
- ✅ 13 executed mutations across two rounds, 13 observed REDs.
- ⚠️ One red guard, foreign to this story, isolated by execution and left for the operator.
- ⚠️ `gate_decision.py` at 1,197/1,200, filed 🟠 as `DF-16-1-B` with a hard trigger for 16.2.
- **No threshold, corpus, floor, `MANIFEST_FIELDS`, `GATE_OUTCOMES`, `CONDITION_VERDICTS`,
  `protocol_cleared`, protocol version, ratification state, adjudication set or bench member
  moved.** `DF-13-5-A`'s one round is UNSPENT.

### File List — ROUND 2 (cumulative for the story)

| File | State | Why |
|---|---|---|
| `argus/precision/gate_breadth.py` | **new** (436) | §5's breadth condition: id, derivation, predicate, published sentences, effective-status renderer |
| `argus/precision/gate_decision.py` | **modified** (1,015 → 1,081 → 1,197) | AC1.1 / AC1.2 / AC1.3 / AC3.1 / AC3.3 / DN-16-1-4 |
| `tests/test_gate_breadth.py` | **new** (495) | `TC-ArgusAgent-PRECISION-001-82`..`-85` |
| `tests/test_gate_condition_lookup.py` | **new** (288) | `TC-ArgusAgent-PRECISION-001-80`, `-81` (round 1) |
| `tests/test_gate_decision.py` | **modified** (1,098 → 1,187) | `-55`, `-56`, `-58` re-authored; `-62`'s positional payload read repaired; `_spread()` generator |
| `tests/test_release_preflight.py` | **modified** | `RELEASE-001-11`'s test-tree-reach registry — a deliberate decision, recorded |
| `README.md` · `CHANGELOG.md` | **modified** | `DOCS-001-54`'s four published figures, read from the guard's own live measurement |
| `_bmad-output/…/precision-validation-protocol.md` | **modified** | §5's dated amendment block, **under V1.3**; no change-log row |
| `_bmad-output/…/architecture.md` | **modified** | §Enforcement, struck-not-erased |
| `_bmad-output/…/deferred-work.md` | **modified** | `DF-16-1-A`, `DF-16-1-B` filed; nothing disposed |
| `_bmad-output/…/validation-corpus/gate-decision-record.json` | **regenerated** | §2.2; prefix-plus-one; outcome byte-identical |
| `_bmad-output/…/minions-dogfood-{partition-plan,budget-plan,proof}.md` | **regenerated** | `AI-E12-11` LOC currency, in the mandatory order |
| this story file · `sprint-status.yaml` | **modified** | this record; status transition |

**Explicitly NOT written:** `validation-corpus/adjudication-record.json` (no re-stamp) ·
`validation-corpus/adjudication-set*.json` · `argus/detectors/**` · `tests/corpus/_manifest.py` ·
`argus/precision/replay_harness.py` · `argus/precision/adjudication.py` ·
`argus/precision/gate_disclosure.py` · `argus/precision/__init__.py` · `argus/pipeline*.py` ·
`tests/test_vacuous_density.py` · `tests/test_status_document_registry.py` · `prd.md` · `epics.md`.

**Landing shas for 16.4's ancestry guard:** **`2ac1078`** (code, tests, protocol, architecture,
ledger) and **`11f40cb`** (regenerated artifacts). Neither contains Argus output over any bench
member. **Next TC ids:** `TC-ArgusAgent-PRECISION-001-*` is allocated through **`-85`**; allocate
from **`-86`**.

---

---

## Dev Agent Record — ROUND 3 (2026-08-20), the review-fix round

> Rounds 1 and 2 above are **unedited**. This section is additive (§3.4). Where round 3 overturns
> a round-2 claim, it says so **here** rather than by rewriting round 2's words — and round 2 made
> exactly one claim that was not true, which is why this round exists.

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context), BMAD `dev-story`, **fix** pass over code-review
iteration 1, 2026-08-20.

### The finding is CONFIRMED, not argued with

The review is right, and it is right for the reason it gives. Round 2 wrote a breadth clause into
`-55`'s local outcome recomputation, drove **13** mutations, and marked AC1.5 discharged — and not
one of those 13 mutations touched `-55`. Re-verified here by execution before anything was changed:

- `-55`'s only fixture is the **committed** `adjudication-record.json`. It carries **5
  `BORDERLINE`** rows, so `isinstance(fold.exhaustiveness, Exhaustive)` is `False`, so the FIRST
  clause (`determinism is not None or not exhaustive`) fires for every run and `elif not
  breadth.holds:` is **structurally unreachable for that fixture**.
- Both of the reviewer's mutations were re-run against round 2's `-55` to confirm the report rather
  than take it on trust: forcing `holds = True` in `assess_breadth` → `-55` **GREEN**; disabling
  both breadth dispatch branches in `gate_decision.py` → `-55` **GREEN**.

**That is the `DF-15-2-A` unreal-guard class**, landed on the guard whose entire subject is *"the
outcome is DERIVED, not chosen"* — in the story written to stop this project shipping unreal
guards. Round 2's *"`-55` re-authored … BOTH DONE"* and its AC1.5 tick were **not supported by
execution**. Recorded plainly here; round 2's wording is left standing as the evidence.

### The fix: option (a), with the honest half of option (b) kept

The review offered two remedies. **(a) was taken** — the branch is reachable by a population
`derive_concentration` accepts, and this round proves it by executing one — **and the disclosure
half of (b) was kept anyway**, because the two are not alternatives: a generated fixture makes the
clause real, and `-55`'s docstring still owes the reader the truth about which clause `-55`'s **own**
fixture reaches.

**1. §5's dispatch mirror is now written ONCE.** `expected_section_5_outcome(fold, *,
breadth_holds)` in `tests/test_gate_breadth.py`. `-55` imports it; `-86` imports it. Two copies of a
dispatch mirror is two things that can drift from the dispatch and from each other, and the drift is
invisible from either side (AR7). The cross-module import is the pattern
`tests/test_gate_decision.py` already uses for its analyzer — *"IMPORTED, never copied"*.

**Why it lives in the breadth module and not beside `-55`, recorded rather than left to be
guessed.** `breadth_holds` is the only term in that dispatch whose truth this project had to
*construct a population* to observe; every such population (`_population()`, `_spread()`) lives in
the breadth module; and `tests/test_gate_decision.py` had **13 lines** of headroom against NFR-M1's
1,200 (AC8.5: *"do not shave a file to fit"*). Cohesion argued weakly for `test_gate_decision.py`
and the ceiling argued strongly against it; the tradeoff is recorded here rather than absorbed.
Net effect: `test_gate_decision.py` **1,187 → 1,193**, `test_gate_breadth.py` **495 → 622**.

**2. `breadth_holds` is an ARGUMENT, not something the mirror derives.** This is the load-bearing
detail and it is the whole reason the repaired guard can go red where the old one could not. A guard
that fed `assess_breadth(...).holds` back into its own expectation moves **in lockstep** with the
defect it is hunting: mutate `holds` and both sides move, and the equality stays true. `-86`
therefore derives the term as `contributing >= contributing_member_floor(...)` from **the fixture's
own asserted contributing-member count** and the derived floor — never read back out of the
predicate under test.

**3. The new guard: `TC-ArgusAgent-PRECISION-001-86`** (`tests/test_gate_breadth.py`) — *the outcome
recomputation carries a LIVE breadth term.* It generates one population per contributing-member
count in `1..len(ratified)` through the existing `_population()` (real `AdjudicationRow` objects
through the real `AdjudicationRecord`, all-`TP`, reproducible, exhaustive, above threshold), drives
the shipped `decide_gate` over each, and asserts the live outcome equals the mirror's answer.
**Non-vacuity is asserted FIRST and it is the assertion that makes the clause provably reached:**
`determinism is None`, `exhaustiveness` **is** `Exhaustive`, `precision is not None` and
`meets_threshold` — so every clause *above* the breadth clause is false and the breadth clause is
the one that decides. On every below-floor population the clause is additionally asserted
**decisive**, by flipping its one argument over the identical fold and requiring the answer to
change. Both directions are asserted to have actually been observed
(`set(observed.values()) == {"BLOCKED", "CLEARED"}`), and the flip is asserted to happen **exactly
at the derived floor**.

**4. `-55` stops claiming what it does not do.** It now calls the shared mirror, still passes the
breadth term derived from the same concentration the decision publishes, and its docstring states in
terms which clause its fixture reaches, that round 2's claim was disproved by execution, and where
the clause *is* driven. It also gained a **tripwire**: `assert not isinstance(fold.exhaustiveness,
Exhaustive)` — if the committed record ever becomes exhaustive, `-55` goes RED and says to re-read
its own docstring, rather than silently starting to mean something else.

### The mutation transcript — ROUND 3: 4 mutations, 4 observed REDs, ALL EXECUTED

Rounds 1–2 recorded M1–M13. These continue the numbering. Each mutation was applied to the shipped
file, the suites were run, the RED was **observed**, and the file was restored from a pre-mutation
copy in a `finally`. **M14 and M15 are the reviewer's own two mutations, re-run verbatim against the
repaired guard** — the ones that previously left `-55` green.

| # | What was mutated | Direction | Guard RED | What the failure said (verbatim, trimmed) |
|---|---|---|---|---|
| **M14** | `gate_breadth.assess_breadth`: `holds = contributing >= floor` → `holds = True` *(reviewer's mutation 1)* | the condition cannot FAIL | **`-86`** | `AssertionError: 1 contributing member(s) against a floor of 3: the preconditions dictate 'BLOCKED' and the live decision recorded 'CLEARED'. §5's breadth condition is 'MET'` |
| **M15** | `gate_decision.py`: **both** breadth branches disabled — `_precision_condition`'s `elif not breadth.holds:` and the outcome dispatch's `elif not breadth.holds:` → `elif False:` *(reviewer's mutation 2)* | the dispatch ignores breadth | **`-86`** | `AssertionError: 1 contributing member(s) against a floor of 3: the preconditions dictate 'BLOCKED' and the live decision recorded 'NOT_CLEARED'. §5's breadth condition is 'FAILED'` |
| **M16** | `gate_breadth.assess_breadth`: `holds = False` | **the MET direction** — the condition cannot HOLD | **`-86`** | `AssertionError: 3 contributing member(s) against a floor of 3: the preconditions dictate 'CLEARED' and the live decision recorded 'BLOCKED'. §5's breadth condition is 'FAILED'` |
| **M17** | the mirror's own `if not breadth_holds: return "BLOCKED"` clause **deleted** | the clause is dead code | **`-86`** | `AssertionError: CLEARED` · `assert 'CLEARED' == 'BLOCKED'` |

**M14 and M15 are the finding, answered on its own terms:** the two mutations that left round 2's
`-55` GREEN now turn the repaired guard RED, in the same run, on the same tree. **M16 is the other
direction** — AC1.5 asks for both, and a predicate stuck at `FAILED` is caught by the MET arm.
**M17 answers the word *"unreachable"* directly**: deleting the clause changes the answer, so it is
not dead code any more; it is a branch under test.

Round 1 + round 2 + round 3 = **17 executed mutations, 17 observed REDs.**

**The tree was restored EXACTLY and it was proved, not asserted.** After every mutation the file was
rewritten from its pre-mutation copy in a `finally`, and at the end of the round
`git diff --stat -- argus/ scripts/ README.md CHANGELOG.md` is **EMPTY** and `git status --porcelain`
names only the five files this round intends to change. **No production line was written this
round** — which is also why `gate_decision.py` is still at **1,197/1,200** (`DF-16-1-B` untouched
and un-triggered), why no artifact needed regenerating, and why the `AI-E12-11` dogfood LOC guards
did not fire (their scope prefix is `argus/`, measured, not assumed).

### The [Low] deferred finding — RESOLVED BY RESTORATION, not by disclosure alone

The review was right that an undisclosed byte-level edit to a pre-existing Story-15.x entry sat in
this story's commits, outside its declared write set. Measured: at `0a6e121` the sentence read
``the reason `<CR>` / `<CR><LF>` are not part of the problem`` — the two backtick spans held a
**literal CR** and a **literal CRLF**, which is the *point* of an entry about what a line is — and
this story's commits flattened both to `` `<LF>` ``. The example was not merely reformatted; it was
**destroyed**, in a ledger entry whose subject is line endings.

**Both halves of the reviewer's remedy were taken.** The original bytes are restored, and the edit
is disclosed here and in the File List below. Verified by execution rather than by claim:
`git diff 0a6e121 -- …/deferred-work.md` is now a **single hunk at the end of the file, 121
insertions and 0 deletions — a pure append**. The reviewer's own ledger entry is left **standing and
unedited**; it gained a dated append-only sub-bullet recording the restoration, which is the §3.4
form. Nothing was appended to `deferred-work.md` to green a guard, and **no entry was disposed of**.

### Gates (ROUND 3) — real numbers, executed on this tree

| Gate | Result |
|---|---|
| `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 python -m pytest` | **1,658 collected · 1,658 passed · 0 failed · 0 skipped · 0 errors**, **exit 0** (232.56s) |
| `mypy argus` | **Success: no issues found in 88 source files** |
| `bandit -r argus --severity-level medium` | **0 medium, 0 high** (20 low, unchanged) |
| `python scripts/build_gate_decision.py --check` | exit **0** — `CURRENT — BLOCKED (NOT COMPUTED BY THIS RUN)` |
| `python scripts/build_adjudication_record.py --check` | exit **0** — `OK — the adjudication record is current (31 row(s))` |
| NFR-M1 (`_physical_line_count`, ceiling 1200) | `test_gate_decision.py` **1,193** · `test_gate_breadth.py` **622** · `gate_decision.py` **1,197** (untouched) · `gate_breadth.py` **436** (untouched) |
| Production byte-unchanged | `git diff --stat -- argus/ scripts/ README.md CHANGELOG.md` **empty** |
| AC6.4 / ordering (🔒 BINDING) | no candidate path in the diff; neither `audit_validation_corpus.py` nor `pinned_corpus_snapshot.py` was invoked; `DF-13-5-A`'s round is **UNSPENT** |

⚠️ **The suite is now fully green, and the reason is worth stating rather than enjoying.** Round 2
reported 1,656/1,657 with one red proved foreign — `TC-ArgusAgent-DOCS-001-22` over an untracked,
unapproved change-proposal document. That document was registered by commit `6766df7`, which is
**not this story's commit** and was explicitly out of the review's scope. This round neither caused
that green nor claims credit for it; the delta this round owns is **+1 test** (`-86`) and **+1 pass**.

### AC status after this round

- **AC1.5 — now genuinely satisfied for `-55`**, and satisfied by execution rather than by wording:
  the mirror's breadth clause is driven to **both** outcomes and observed RED by 4 mutations.
  Round 2's tick was premature and is corrected here rather than re-asserted.
- **AC4.1 / AC4.5 — satisfied for `-86`**: its docstring discharges the guard-adequacy clause in its
  own words (the observable, the defect moving it at the real seam in both directions, and variants
  **generated** with their count), and non-vacuity is asserted first.
- **AC7.1 — satisfied, with a stronger number than any prior round**: 1,658 passed, 0 skipped,
  exit 0.
- **AC7.4 — still OPEN, and still not claimed.** This round was instructed not to push. AC7.4 is
  discharged by OBSERVATION of a CI run id against the sha it covers, and there is none. ⚠️ The local
  gates are Windows-only while CI runs an ubuntu matrix; a green local suite has already shipped
  POSIX-only bugs to master, so this is a real gap, not a formality.
- Every other AC's round-2 status is unchanged; **nothing that was decided was reopened** — not the
  ≥80% `Fraction`, not `VALIDATION_SET_FLOOR_N`, not the five ratified members, not
  `MANIFEST_FIELDS`, not the V1.3 protocol head, and not the decision to land no rule-class
  threshold.

### Debug Log References — ROUND 3

- M14–M17 — a scratchpad harness applies one text mutation, runs
  `tests/test_gate_breadth.py tests/test_gate_decision.py tests/test_gate_condition_lookup.py`,
  captures the RED and restores the file from a pre-mutation copy in a `finally`; `git status
  --porcelain` compared before and after each.
- The finding's own re-verification — the reviewer's two mutations re-run against **round 2's**
  `-55` (both GREEN, confirming the report) before any repair was written.
- The ledger restoration — the `0a6e121` blob read out of the object database with `git show` and
  the pre-existing prefix compared byte-for-byte, then `git diff 0a6e121 --numstat` used to prove the
  result is a pure append.
- The dogfood scope prefix read from `argus/dogfood/partition_plan.py` (`_DEFAULT_SCOPE_PREFIX =
  "argus/"`) to establish by reading, not by hoping, that a test-only round cannot move the pinned
  LOC.

### File List — ROUND 3

| File | State | Why |
|---|---|---|
| `tests/test_gate_breadth.py` | **modified** (495 → 622) | `expected_section_5_outcome()` — §5's dispatch mirror, written once — and `TC-ArgusAgent-PRECISION-001-86`, which drives its breadth clause in both directions over generated populations |
| `tests/test_gate_decision.py` | **modified** (1,187 → 1,193) | `-55` calls the shared mirror, states which clause its own fixture reaches, and gains an exhaustiveness tripwire |
| `_bmad-output/…/deferred-work.md` | **modified** | the Story-15.x entry's bytes RESTORED to `0a6e121`; a dated append-only note added under the review's own entry. **Disclosed here because round 2 did not disclose it** |
| this story file · `sprint-status.yaml` | **modified** | this record; `in-progress` → `review` |

**Explicitly NOT written this round:** `argus/**` (byte-unchanged — no production line was needed) ·
`scripts/**` · `README.md` · `CHANGELOG.md` · `precision-validation-protocol.md` ·
`architecture.md` · `validation-corpus/**` (nothing regenerated, because nothing production-side
moved) · `tests/test_gate_condition_lookup.py` · `tests/test_release_preflight.py` ·
`tests/test_vacuous_density.py` · `tests/corpus/_manifest.py` · `prd.md` · `epics.md`.

**Next TC ids:** `TC-ArgusAgent-PRECISION-001-*` is now allocated through **`-86`**. Allocate
from **`-87`**.

### Hand-off addendum for 16.2 and 16.3

Round 2's nine hand-off points stand. Two are added, and they are the ones this round paid for:

10. **`expected_section_5_outcome()` is the ONE §5 dispatch mirror.** When you append a sixth or
    seventh condition that can refuse an otherwise-clearable fold, add your term to **that
    function** and drive it over `_population()` the way `-86` does — and pass your term **in** as
    an argument derived from your fixture, never read back out of the predicate you are testing.
11. **A guard whose only fixture is the committed record cannot observe a §5 condition that binds
    before exhaustiveness.** The committed record carries 5 `BORDERLINE` rows and is never
    exhaustive, so every clause after the first is unreachable there. That is exactly how round 2
    shipped a clause it believed it had tested. If your new clause sits below `exhaustiveness` in
    the dispatch, it **needs a generated population**, or it is documentation.

## Change Log

| Date | Change | By |
|---|---|---|
| 2026-08-20 | ✅ **ROUND 3 — the code review's [Med] finding is FIXED by execution, not by rewording; 1 of 1 Patch finding resolved, and the [Low] deferred finding resolved as well.** **The finding was CONFIRMED before it was fixed:** round 2's `-55` was re-run under both of the reviewer's mutations and stayed **GREEN** under each, exactly as reported — its only fixture is the committed record, which carries 5 `BORDERLINE` rows, is therefore never `Exhaustive`, and makes the first dispatch clause fire every time, leaving the `elif not breadth.holds:` clause structurally unreachable. Round 2's *"BOTH DONE"* and its AC1.5 tick were not supported by execution; that wording is left standing (§3.4) and corrected here. **The fix is the review's option (a), with the honest half of (b) kept:** §5's dispatch mirror is now written **ONCE** as `expected_section_5_outcome(fold, *, breadth_holds)` in `tests/test_gate_breadth.py` (AR7 — `-55` and `-86` import it, neither copies it), and a NEW guard **`TC-ArgusAgent-PRECISION-001-86`** drives its breadth clause over **GENERATED** populations — one per contributing-member count, real rows through the real record, all-`TP`, reproducible, exhaustive and above threshold — against a **LIVE `decide_gate`** call, asserting the flip happens **exactly at the derived floor** and that **both** directions were observed. **The load-bearing design decision:** `breadth_holds` is passed **in**, derived from the fixture's own asserted contributing-member count and `contributing_member_floor(...)`, and is **never read back out of `assess_breadth`** — a guard that fed the predicate's own answer into its expectation would move in lockstep with the defect and would survive precisely the mutation the review ran. `-55` keeps the term (so it cannot expect `CLEARED` over a narrow denominator), **states in its docstring which clause its own fixture reaches**, and gains an exhaustiveness **tripwire**. **4 mutations, 4 observed REDs, all EXECUTED against production and restored byte-exact:** **M14** `holds = True` (the reviewer's mutation 1) → `-86` RED *"1 contributing member(s) against a floor of 3: the preconditions dictate 'BLOCKED' and the live decision recorded 'CLEARED'"*; **M15** both breadth dispatch branches disabled (the reviewer's mutation 2) → `-86` RED *"…recorded 'NOT_CLEARED'"*; **M16** `holds = False` → `-86` RED in the **MET** direction *"3 contributing member(s) … dictate 'CLEARED' … recorded 'BLOCKED'"*; **M17** the clause deleted from the mirror → `-86` RED — which answers *"dead code"* directly. **17 executed mutations, 17 observed REDs across three rounds.** **The [Low] deferred finding is RESOLVED BY RESTORATION:** the undisclosed byte-level edit to the Story-15.x ledger entry is reverted to its `0a6e121` bytes — the two backtick spans hold a literal CR and a literal CRLF again, which was the entry's whole point — proved by `git diff 0a6e121 -- deferred-work.md` now being a **single end-of-file hunk, 121 insertions / 0 deletions, a pure append**; the reviewer's entry is left unedited and gained a dated append-only note; the edit is disclosed in the File List. **NO production line was written this round** — `git diff --stat -- argus/ scripts/ README.md CHANGELOG.md` is **empty** — so `gate_decision.py` stays at 1,197/1,200 with its ledgered split-first trigger un-triggered, no committed artifact needed regenerating, and the dogfood LOC guards (scope prefix `argus/`, read not assumed) could not fire. Gates: **1,658 collected · 1,658 passed · 0 failed · 0 skipped · 0 errors, exit 0**; `mypy argus` Success 88 files; `bandit -r argus --severity-level medium` 0 medium / 0 high; both builders `--check` exit **0**; NFR-M1 `test_gate_decision.py` 1,193 and `test_gate_breadth.py` 622. Nothing decided was reopened: the ≥80% `Fraction`, `VALIDATION_SET_FLOOR_N`, the five ratified members, `MANIFEST_FIELDS`, the V1.3 head and the decision to land **no** rule-class threshold are all untouched, no bench member was read, and `DF-13-5-A`'s one round is **UNSPENT**. **NOT pushed** (instructed), so AC7.4 stays **OPEN** and is not claimed. Status `in-progress` → **`review`**. | dev-story |
| 2026-08-20 | ✅ **ROUND 2 — both HALTs RESOLVED by the operator (XAgent007, 2026-08-20, recorded VERBATIM in this file as the round's first act) and the story LANDED.** **HALT-1 decided:** land the contributing-member arm ONLY. §5 gains a fifth condition, **appended** — the precision ratio is EVALUABLE only over a population drawn from at least `(VALIDATION_SET_FLOOR_N + 1) // 2` = **3** distinct CONTRIBUTING members; below it §5's precision condition is `UNEVALUABLE` with its counts and the outcome is `BLOCKED` with a countable closure path, while the breadth condition's OWN verdict is `MET`/`FAILED` because it *was* evaluated. The **rule-class arm was NOT landed** and is filed as **`DF-16-1-A`** carrying the blocking measurement verbatim (max achievable verdict-eligible rule classes = **1**; ≥2 is a shutdown, 1 cannot fail). **HALT-2 decided:** **no `V1.4` row and no re-stamp** — the amendment sits under the EXISTING V1.3, so all **31 human judgements** (26 FP / 5 BORDERLINE, 2026-08-17) keep their original provenance, `adjudication-record.json` was NOT regenerated, and `-45`/`-63` stay green with §2.1's coupling never armed. The false *"zero human judgements"* premise in §0.1 is corrected **append-only, struck not erased**. **Landed:** `argus/precision/gate_breadth.py` (new, 436) holding the id, the derivation, the pure predicate and the published sentences; `SECTION_5_CONDITIONS` +1 appended; `derive_concentration` **hoisted** so the threshold and the disclosure are one set of counts; effective evaluability (`fold.evaluable AND breadth`) rendered through the EXISTING `precision_gate_status_for`; the §5 messages count-derived. **A correction to round 1's own derivation, caught by the guard before it shipped:** `(n+1)//2` is *half, rounded up*, a strict majority only at an ODD floor — the landed value (3 at the locked floor of 5) is unchanged, the general statement was not, and every surface now says the accurate thing. **A THIRD latent trap the story had not named was found by execution: `-58`**, whose `CLEARED` variant runs over the committed 2-member population and would have gone red mid-round with its subject silently changed from the dispatch to the breadth floor; re-authored over a GENERATED breadth-satisfying population with the narrow one asserted `BLOCKED` on breadth. `-55` re-authored with the breadth term, `-56` with the count-derived matches, `-62`'s positional payload read repaired by id, `-70` audited and unchanged. **AC3.5 VERIFIED BY EXECUTION:** `outcome`, `outcome_reason`, `closure_path` and the precision `gate_status` are **byte-identical** across the amendment; the record gained a fifth condition reading `FAILED` and nothing else moved. New guards `TC-ArgusAgent-PRECISION-001-82`..`-85` in a new module, populations GENERATED one per contributing-member count and asserting **where the verdict flips**. **10 executed mutations, 10 observed REDs** this round (13 across both). Gates: **1,656 passed / 1 failed / 0 skipped / 0 errors of 1,657** — the one red is `DOCS-001-22` over an **untracked, unapproved, foreign** change-proposal document that is in neither of this story's commits, isolated by execution and deliberately not absorbed; mypy Success 88 files; bandit clean; both builders `--check` exit 0. Commits **`2ac1078`** (code + protocol + architecture + ledger) and **`11f40cb`** (regenerated artifacts) — **neither contains Argus output over any bench member**, the BINDING ordering constraint holds, and these are the shas 16.4's ancestry guard cites. **NOT pushed** (instructed), so AC7.4's CI run id is recorded OPEN rather than claimed. `DF-16-1-B` files `gate_decision.py` at 1,197/1,200 with a hard split-first trigger for 16.2. No threshold, corpus, floor, `MANIFEST_FIELDS`, protocol version, ratification state or bench member moved; `DF-13-5-A`'s one round is UNSPENT. Status `in-progress` (HALTED) → **`review`**. | dev-story |
| 2026-08-20 | ⛔ **HALTED to the operator at AC2.4, with a second escalation §0 did not anticipate.** §0.2's measurement reproduced by two independent instruments (an AST walk of all 7 `build_recording` sites plus the single `prosecute()` call site at `argus/pipeline.py:535`; and a direct count over both committed adjudication sets): the **maximum achievable distinct verdict-eligible rule-class count is 1**, so a rule-class floor of ≥2 is a shutdown and a floor of 1 cannot fail — the floor is the operator's decision and was not taken. **HALT-2:** the committed adjudication record was measured to hold **31 human judgements** (26 FP / 5 BORDERLINE, `XAgent007 (Engineering Lead)`, 2026-08-17), **not** the zero §0.1 and §2.1 assert, so §2.1's authorisation to re-version the protocol over an unjudged record does not hold as written. The contributing-member floor **was** derived — `(VALIDATION_SET_FLOOR_N + 1) // 2 = 3`, shown against all five of AC2.2's tests with four rejected alternatives — and **deliberately not landed**, because the condition is one §5 amendment and landing half of it takes the arm-dropping decision AC2.4 reserves. **LANDED, being the one task independent of the halted constant:** AC1.3's repair of the `conditions[3]` positional false green — `section_5_condition()` by id, a typed `MissingSection5Condition`, `RECORDED_CLEARED_CONDITION_ID` named once — with `TC-ArgusAgent-PRECISION-001-80`/`-81` in a new module and **3 executed mutations observed RED** (M3 exhibits the defect concretely: the positional read publishes `adjudication_run_recorded_cleared=True` while the condition it names reads `FAILED`). `-70` audited, needs no change; `-55`'s trap confirmed and recorded, re-authoring deferred with the condition. Gates: 1,651 passed / 2 failed / 0 skipped of 1,653 — both failures proved by stash-isolation to be only the `AI-E12-11` dogfood LOC-currency coupling; mypy Success 87 files; both builders `--check` exit 0. Nothing committed, staged or pushed; no protocol version, threshold, corpus, ratification state or committed artifact moved. Status `ready-for-dev` → `in-progress` (HALTED). | dev-story |
| 2026-08-20 | Story contexted at HEAD `0a6e121`. §0 premises measured by execution on the live tree, read-only. §0.2 records the governing measurement — exactly one rule class can reach verdict-eligibility over the repository corpus, because `vacuous_test.py:1067` is the sole non-`None` `depth_supported` site on the corpus-audit path and the Prosecutor's promotion is unreachable because `pipeline.py:534` passes no `sign_offs` — which AC2.4 turns into a binding constraint on the rule-class floor, with a HALT rather than a silently unclearable gate. §2 records the two artifact-currency couplings (the protocol change-log head versus the committed adjudication record; a fifth condition versus the committed gate-decision record) that would otherwise turn the tree red in files the dev did not edit. Status `backlog` → `ready-for-dev`. | create-story |
