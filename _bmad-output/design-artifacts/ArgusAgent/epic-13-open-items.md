# Epic 13 — the re-derived OPEN-ITEMS list

> **What this is.** Story 13.3 / AC7's committed deliverable: the list of what remains open,
> **re-derived by execution on this tree**, as an INPUT to the Epic-13 retrospective. It is
> **not** the retrospective — `epic-13-retrospective` is its own sprint-status item, and a story
> that graded its own epic would be the shape this epic exists to delete (13.3 / DN-5).
>
> **Re-derived, not copied.** `epics.md` Story 13.3's fifth AC says so in its own words: *"The
> retrospective re-derives this list at the time it is written rather than copying it — the point
> is that it is measured, not that it matches this sentence."* Every line below was measured on
> **HEAD `6c59115`, 2026-08-17**, by executing the ledger's own analyzers, reading the manifest,
> and querying the CI API. **Four of the epic AC's own example items were measurably stale**, and
> two of the story file's §0 premises were stale too; the corrections are recorded here beside
> the substance rather than silently adopted.

**One sentence, plainly, because it is the sentence this AC exists to force:**
**a cleared gate authorises ATTESTED externalization and is NOT plan closure.** The Epic-9
retrospective declared the plan FINAL once already and Epic 10 had to reopen it. On this tree the
gate is not even cleared — see §1.

---

## 1. The gate itself — `BLOCKED`, and what that does and does not mean

Measured by execution, from the committed
`validation-corpus/gate-decision-record.json` (every figure derived, none typed):

| Protocol §5 condition | Verdict | Measured |
|---|---|---|
| precision ≥ 80% (exact `Fraction`) | **UNEVALUABLE** | the run is not exhaustively adjudicated, so no ratio was computed |
| clean-repo blocking FP == 0 | **MET** | measured over the FR20 **cartridge** corpus, folded through `compute_precision`, naming the clean members it folded — evaluated explicitly, never counted met by default (protocol §5 as amended 2026-08-16 names Story 13.3 by name) |
| N ≥ 5 | **MET** | derived from `tests/corpus/_manifest.eligible_member_count()` |
| the adjudication run is recorded cleared | **FAILED** | the run is not exhaustive |

**Outcome: `BLOCKED`, not `NOT_CLEARED`.** The named human (**XAgent007**, Engineering Lead)
adjudicated on **2026-08-17** and every one of the 31 emitted blocking findings now carries a
human disposition — **zero remain `UNADJUDICATED`**. But **5 came back `BORDERLINE`**, and
protocol §4 states in its own text that `BORDERLINE` *"makes the run non-exhaustive until it
resolves"*. §4's ladder — locator re-examination → golden-key correction → **external tie-break**
— has therefore **not terminated**, and protocol §2 records the QA-Lead and external-adjudicator
roles as **unfilled**.

> ⚠️ **`BLOCKED` is not a §5 outcome and must never be restated as *"the gate did not clear"*.**
> That sentence is true, useless, and indistinguishable downstream from an honest measured
> shortfall. A gate that did not clear because findings were judged and enough were false is a
> **measurement**; a gate whose adjudication has not terminated is an **absence**.

**Recorded because a reader is owed it, and recorded as a BOUND rather than as a decision:** over
**every admissible completion** of the 5 residual findings the threshold is unreachable —
resolving all five as TP, the most favourable outcome available, gives **5/31**, still below
**4/5**. That does **not** promote `BLOCKED` to `NOT_CLEARED`: the residual is a human's
unfinished act, and an incomplete measurement stays an incomplete measurement however its
arithmetic is trending.

**Concentration of the measured population, disclosed (13.3 / AC3b, `AI-E13-5`), derived:** the 31
findings are drawn from **2 of the 5** ratified members and from **one** rule class; **3 ratified
members contributed zero findings**. §5's `N ≥ 5` is satisfied by member COUNT — *the N that gates
and the N that contributes are different numbers*. This is **disclosed, never corrected**:
narrowing the corpus to improve the ratio is the threshold change AC5 forbids, wearing a hat.

**`expert_hours` is `null` and stays null.** Protocol §3 treats it as a **report, never a gate**,
so a null is honest and a zero would claim the work took no time rather than that it was not
reported. No agent may supply it.

---

## 2. The Minions handoff — H0 is OWNED; H1–H4 are still NOT FILED

⚠️ **Two stale surfaces corrected, not propagated:**

- **The epic AC's own example — *"H0 is owned but H1–H4 are still NOT FILED"* — is ✅ CORRECT** on
  this tree. `epics.md:2642-2643` closed H0 on **2026-08-10b** via the pre-authorised **option
  (b)** (the operator files outside this workflow); `deferred-work.md:1575-1588` records the same;
  `epics.md:30` carries it in frontmatter.
- **`sprint-status.yaml`'s header note *"H0 (who FILES that handoff) is still UNOWNED"* is ❌
  STALE.** It is dated **2026-08-09** and predates the 2026-08-10b closure. Story 10.5 already
  recorded a correction to a brief that said otherwise (`deferred-work.md:2203-2205`). **It is
  corrected in place by this story rather than propagated.**

**The substance, which is NOT stale and is the whole point of the instruction:**

- **H1–H4 are still NOT FILED.** H0's closure records ownership of the *filing act*; it explicitly
  does **not** mean the handoff items exist in any backlog.
- **Assumption A5 remains ⚠️ UNSUPPORTED** (`epics.md:1427`): Minions lands on row 4 → exit `3`,
  which still fails an unconfigured blocking CI gate.
- **H3's blocking-vs-advisory policy decision is UNMADE** (`epics.md:2689`), and it is the
  precondition for wiring the CI gate at all.
- **This repository's CI cannot verify any of the Minions integration.** Nothing in `tests/`
  exercises it; the integration is planned-and-relocated only.

---

## 3. CI evidence — ⚠️ the story file's premise was STALE, and the correction is a partial one

**Measured 2026-08-17 by querying the workflow API** (`gh run list --workflow=audit-ci.yml`):

| Sha | Epic | audit-ci conclusion | When |
|---|---|---|---|
| `c027e16` | 13 (13.3 context) | ✅ success | 2026-08-17T02:52Z |
| `be35c7f` | 13 (interim retro) | ✅ success | 2026-08-17T02:45Z |
| `b04dc1a` | 13 | ✅ success | 2026-08-17T02:04Z |
| `ae54234` | 13 | ❌ **failure** | 2026-08-17T01:33Z |
| `bc55e36` | 12 | ✅ success | 2026-08-15T22:39Z |

The story file's §0 recorded *"CI evidence: NOT ESTABLISHED for any Epic-10/-11/-12/-13 sha
(`audit-ci.yml`'s latest run covers `00c8d1b`, 2026-08-09)"*. **That is no longer true and the
correction is recorded rather than the claim repeated.** ⚠️ **What remains open:** the newest
CI-verified sha is **`c027e16`**, which is **behind** the adjudication commit `6c59115` and behind
this story's delta. **CI evidence is therefore NOT ESTABLISHED for the adjudication itself, nor
for the gate decision this story commits** — and one Epic-13 sha (`ae54234`) is a recorded CI
**failure**. Local gates here are **Windows-only** while CI runs an ubuntu matrix; a local green
is necessary and never sufficient (`architecture.md` §H).

---

## 4. Ledger — measured id by id, one disposition per line

⚠️ **Four of the seven ids the epic AC lists *"as of 2026-08-10b"* had moved by the time 13.3 was
contexted, and the story file's own AC7 table is therefore also a snapshot.** Re-measured on
`6c59115` by executing `tests/test_governance_record_integrity.ledger_closed_ids` over the ledger:

- `DF-6-7-A` — ✅ the ledger carries a CLOSED disposition (2026-08-11, FR23); the *invocation*
  half remains open under its own record.
- `DF-8-4-B` — ⛔ the ledger's own text rules it **remains open and unowned _by decision_**
  (`deferred-work.md:1649-1657`, a locked disposition). ⚠️ **Measurement caveat:** the analyzer
  reports it as carrying a closure disposition; that is a line-scoped extractor artifact, not a
  real closure. **Do not schedule it and do not act on the analyzer here.**
- `DF-8-4-C` — ⛔ **remains open and unowned _by decision_**, same locked disposition (confirmed
  by the analyzer: no closure disposition). Do not schedule it.
- `DF-8-4-D` — ✅ the ledger carries a CLOSED disposition (2026-08-15).
- `DF-8-5-B` — ♻️ recurs as the **artifact-currency bootstrap** (with `DF-10-4-D`), not as a
  pending item. Applied again by this story, because `argus/**` moved.
- `DF-8-5-C` — ✅ the ledger carries a CLOSED disposition (2026-08-16, against evidence).
- `DF-9-2-C` — ✅ the ledger carries a CLOSED disposition.

**Measured ledger totals on `6c59115`:** 82 distinct `DF-*` ids appear in the ledger; **31** carry
a closure disposition; **51** do not. The `DF-*` entries this story is directly accountable to:

- `DF-13-2-A` — **OPEN, and its residual has SHRUNK but not vanished.** The adjudication run it
  was filed for **HAS HAPPENED**: all 31 findings judged by XAgent007 on 2026-08-17, **0
  `UNADJUDICATED`**. What remains is a **different, smaller thing** — the 5 `BORDERLINE` findings
  whose §4 ladder has not terminated. Re-stated with what remains, **not closed** (13.3 / AC8.2).
- `DF-13-3-A` — **FILED by this story.** The unreachable `agent-smith` pinned sha (see §5).
- `DF-13-3-B` — **FILED by this story.** `-46` goes vacuous on a derived `protocol_cleared`
  (AC4(d)), which stays open because AC4 was not performed in the `BLOCKED` branch.
- `DF-12-7-B` — **OPEN, NOT dispositioned by this story.** AC4(f) assigns it to the CLEARED
  branch; the branch did not fire, so nothing about an installed command asset went stale and
  closing it here would be a closure in prose rather than against evidence (`AI-E12-3`).
- `DF-12-9-A` — **OPEN and untouched.** Nothing outward-facing: `git tag -l` is empty and this
  story pushed nothing.
- `DF-6-6-A` / `-P1` / `-P2` / `DF-7-2-A` — re-stated with what remains, **not closed**.

---

## 5. Filed by this story, with named owners (`AI-E9-8`)

- **The `agent-smith` pinned sha `9ab774d7bf5d61da552c61094b2d478f72dfbb6d` is UNREACHABLE**, and
  its 7 findings were adjudicated against a **reconstruction** (`origin/development` `d9bb793`),
  not against the audited tree. **Consequence, recorded:** the adjudication record's
  `reproducibility_verified: True` (measured 2026-08-16) is **no longer re-verifiable for that
  member**, and byte-identity with the audited source cannot be established. ⚠️ **All 5 residual
  `BORDERLINE` findings are `agent-smith` findings**, so the member whose evidence surface is a
  reconstruction is exactly the member whose ladder has not terminated. Filed as **`DF-13-3-A`**,
  owner **XAgent007 (Engineering Lead)**.
- **`TC-ArgusAgent-DOCS-001-46` goes VACUOUS on a derived `protocol_cleared` flag.** Reproduced by
  execution this session. Filed as **`DF-13-3-B`**, owner **XAgent007 (Engineering Lead)**,
  target: whoever performs the flip, **in the same change** (13.3 / AC4(d)).

---

## 6. What a reader must not conclude from this document

- **Not that the gate failed.** It was not measured to a §5 outcome at all.
- **Not that the gate is close.** The derived bound says no completion of the residual reaches the
  threshold — but the residual is unjudged, and an unjudged finding is not a result.
- **Not that Epic 13 is finished.** The retrospective is a separate sprint-status item and this
  file is its input.
- **Not that clearing would be plan closure.** Clearing authorises **attested externalization and
  nothing else** — not commercial, enterprise, regulated or operated-service use, each of which
  carries its own preconditions — and it is not a publish act.
