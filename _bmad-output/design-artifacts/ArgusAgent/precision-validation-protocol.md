# APAA Precision Validation Protocol (V1)

> **Status:** committed V1 deliverable (Story 6.6 / Epic 6 — Trust Substrate). This is the
> durable §3.4 source of truth for **HOW** the APAA precision number is judged — recorded
> **before** the ground-truth schema is frozen, so the externalization gate is defensible
> (a documented adjudication method, not an ad-hoc count). Drivers: **APAA-FR-20** (precision
> measurement over the defect-cartridge substrate), the PRD **≥80%-precision externalization
> gate**, the **OI1 LOCK** (N=5, phased 3→5, precision over findings, provisional below N=5).
>
> **OI1 honesty keystone (read twice):** this protocol governs a gate that is **PROVISIONAL**
> until the corpus reaches the locked **N=5** floor with this protocol applied and the
> per-metric pass/fail recorded cleared. As of Story 6.6 the corpus is **below N=5**, so the
> computed precision number is an **EARLY / PROVISIONAL signal**, NOT a cleared gate.
> Over-claiming a cleared ≥80% gate from a thin corpus is the exact failure mode this lock
> forbids — honest, measured coverage is APAA's whole thesis.

---

## 1. Purpose & scope

> ### ⚖️ AMENDMENT 2026-08-16 (Story 13.1) — **which corpus this protocol governs**
>
> **This protocol specified the wrong corpus, and the PRD governs.** §5 below fixed the gate's
> floor at *"N ≥ 5 distinct labeled **planted-defect cartridges**"* while the PRD specifies
> *"N ≈ 5–10 **real** XAgents repos"* (`prd.md:196`) judged *"genuinely real by an **independent
> senior engineer**"* (`prd.md:191`). Those were never reconciled — for three epics the project
> carried **two corpora** and a gate that did not say which one it was measured over.
>
> **They are not two opinions about one quantity. They are two different quantities:**
>
> | | Cartridge corpus | Real-repository corpus |
> |---|---|---|
> | Measures | **Recall** against known plants — did we find what we hid? | **Precision** on unplanted code — is a blocking finding real? |
> | Denominator | Golden keys the team authored | Findings the tool emitted on code nobody planted |
> | Gates externalization? | **No** | **Yes** — this is the ≥80% gate |
> | Status | Delivered, CI-asserted (FR20) | Specified 2026-08-16; **populated by operator ratification**, adjudicated in Story 13.2 |
>
> **DECISION (2026-08-16, Story 13.1 / DN-1): the PRD governs.** The ≥80%-precision
> externalization gate is measured over the **repository corpus**. The rejected alternative was
> to let this protocol govern and amend the PRD down to cartridges — which would make the
> externalization gate clearable by a corpus the team authored, planted, and wrote the answers
> to. That is the "measure your own homework" failure Epic 13 exists to remove.
>
> **The cartridges are NOT demoted.** They are re-labelled as the **recall** instrument they
> always were (FR20, delivered and CI-asserted), and they keep doing exactly what they do today.
> Nothing in `tests/cartridges/` changes. What changes is what they are *evidence of*.
>
> Amended below: §1 (substrate), §4 (method), §5 (thresholds), §6 (phased plan). §2 (roles),
> §3 (budget) and §7 (honesty invariants) are **unchanged** — the corpus moved, the method and
> the invariants did not. Per §3.4 evidence immutability the original text is **struck, never
> erased**.

APAA's externalization thesis stands or falls on a **measured, defensible** precision number.
This protocol fixes:

1. **WHO validates** (the adjudicating role).
2. The **expert-hours/repo** budget.
3. The **precision-adjudication method** (sample size, who judges a 🔴 "genuinely real", how a
   borderline finding is resolved).
4. The **per-metric pass/fail** thresholds (≥80% precision, the false-positive ceiling, the
   N=5 corpus floor).
5. The **phased-population plan** (3→5, who labels each new cartridge, when the gate flips to
   non-provisional).

The **mechanized substrate** this protocol governs:

> **PATH CORRECTION 2026-08-16 (Story 13.1 / AC6.1).** All three paths below were struck and
> re-pointed. The originals — ~~`tests/apaa/cartridges/_registry.py`~~,
> ~~`minions_core/apaa/precision/replay_harness.py`~~, ~~`tests/apaa/test_precision_replay.py`~~
> — named locations that **do not exist**, verified by execution on this tree. They were moved
> by the 2026-08-03 APAA→Argus separation, thirteen days before this correction, and the
> document governing the gate went on pointing at every instrument it governs. A protocol that
> cannot locate its own substrate cannot govern an adjudication.

- **Recall ground truth (golden keys):** `tests/cartridges/_registry.py::CARTRIDGE_REGISTRY`
  — a frozen `CartridgeSpec` tuple, each row carrying `required_findings` (the golden key, a SET
  of value-free `GoldenFinding = (rule_id, verdict_eligible, advisory)`), a `kind ∈
  {planted_defect, clean_control, holdout, trap, no_crash}`, `max_blocking`, and the
  `VALIDATION_SET_FLOOR_N = 5` floor. *(Amended 2026-08-16: this is the **recall** substrate.
  It is not the population the ≥80% gate is measured over — see the amendment above.)*
- **🆕 Gate ground truth — the validation set (the population the ≥80% gate is measured over):**
  `tests/corpus/_manifest.py::VALIDATION_CORPUS` *(added 2026-08-16, Story 13.1 / AC3a)* — a
  frozen `CorpusMemberSpec` tuple, each row carrying a repository URL, a **pinned commit sha**,
  a licence, a primary language, a provenance (`independent` | `self` | `superseded`) and
  `eligible_for_n` with a **required reason when false**. Membership is **closed**: a repository
  that is not in the manifest is not in `N`, and an unregistered member raises rather than
  resolving. The floor is **derived** (`eligible_member_count()` against the **same**
  `VALIDATION_SET_FLOOR_N`) — one floor constant, two populations; a second floor is what
  produced two corpora in the first place.
- **Precision harness (the number):** `argus/precision/replay_harness.py::compute_precision`
  — a PURE, zero-LLM-token fold that diffs the emitted findings against the golden keys into
  TP/FP/FN and computes precision = TP / (TP + FP) as an exact `Fraction` (a `"num/den"` string
  ratio — never a float, AR4). **Unchanged by the 13.1 amendment**: the arithmetic is the same
  whichever corpus supplies the findings, and forking it per corpus is exactly what AR7 forbids.
- **Test driver:** `tests/test_precision_replay.py` (area `ArgusAgent-PRECISION`) — stages each
  registry cartridge, audits it via the deterministic `run_audit_detailed`, and feeds the emitted
  findings to the harness. The manifest's own guards are `tests/test_validation_corpus.py`
  (`TC-ArgusAgent-PRECISION-001-21`..`-30`).
- **🆕 The adjudication record (the ground truth for the repository corpus):**
  `argus/precision/adjudication.py::AdjudicationRecord`, committed at
  `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-record.json`
  *(added 2026-08-16, Story 13.2 / AC3)* — append-only, machine-readable, **in git**. One row per
  emitted **blocking finding**, carrying the shared `finding_match_key` identity, the corpus
  member, ≥1 locator (FR13), the disposition, the adjudicator id, the date, a reason, and a
  `supersedes` field for corrections. §2 already states that the harness derives TP/FP
  *mechanically from the golden key* and that the humans adjudicate *the golden key itself*; a
  real repository has no golden key, so **this record IS the golden key for the repository
  corpus** and the existing fold computes precision from it
  (`adjudication.fold_adjudicated_precision`, which reuses `precision_fraction`,
  `gate_is_provisional`, `PRECISION_GATE_THRESHOLD` and `precision_gate_status_for` — one
  arithmetic, two populations). Guards: `TC-ArgusAgent-PRECISION-001-32`..`-51`.

Precision is **measured over FINDINGS, not repos**: the ground-truth is a SET of expected
findings per cartridge, so 5 repos with sufficient findings support a defensible 80% number.
*(Unchanged and re-affirmed 2026-08-16 — this is an OI1 invariant (§7). The 13.1 amendment moves
which **population** supplies the findings; it does not make the gate a count of repositories.
`N ≥ 5` is a floor on the corpus, and precision is still a ratio over findings drawn from it.)*

---

## 2. WHO validates (the adjudicating role)

| Role | Responsibility |
|---|---|
| **Engineering Lead** (primary adjudicator) | Owns the precision gate. Reviews every emitted finding the harness classifies as a **false positive (FP)** on a clean / trap / no-crash repo, and every **false negative (FN)** on a labeled cartridge. Makes the final net-new-vs-known-limitation call. |
| **QA Lead** (second reviewer) | Independently judges whether each disputed 🔴 (blocking finding) is "genuinely real" (a true positive a human auditor would also raise) vs a false accusation. Required for any cartridge whose golden key is **added or changed**. |
| **External adjudicator** (tie-break, optional) | Resolves a borderline finding when the Engineering Lead and QA Lead disagree (see §4 borderline resolution). For V1 this MAY be a third internal reviewer; for an externalization sign-off it SHOULD be outside the implementing team. |

A finding's classification (TP/FP/FN) is **mechanically derived** by the harness from the golden
key; the human roles above adjudicate the **golden key itself** — i.e. whether a given expected
finding (or its absence) is correct — not the arithmetic.

> ### ⚖️ AMENDMENT 2026-08-16 (Story 13.2 / AC2, AC3) — **attribution is asserted, not assumed**
>
> §2 named three **roles** and no **holders**, and nothing checked that a recorded judgement came
> from one. Both halves are now mechanical.
>
> **Named holders, as of 2026-08-16** (`sprint-status.yaml:414`/`:416`;
> `deferred-work.md::DF-7-2-A`):
>
> | Role | Holder | State |
> |---|---|---|
> | **Engineering Lead** (primary adjudicator) | **XAgent007** | ✅ named — the start condition for Story 13.2 |
> | **QA Lead** (second reviewer) | **Veer Pratap Singh** | ✅ **named 2026-08-22** by XAgent007 — see the dated block below. Filled **ahead of** Story 16.7 rather than during it |
> | **External adjudicator** (tie-break) | *unfilled* | required only on persistent disagreement (§4) |
>
> **The rule:** every disposition on the adjudication record carries an `adjudicator` id of the
> form `"<who> (<role>)"`, and `<role>` **must be one of the three roles in the table above**. An
> unattributed disposition is a **failure**, not a gap — enforced at construction by
> `AdjudicationRow.__post_init__` (raises `UnregisteredAdjudicator`), asserted by
> `TC-ArgusAgent-PRECISION-001-42`, which also cross-checks the registered role tuple against
> **this table** in both directions so the code and the protocol cannot drift apart.
>
> **The converse is enforced too, and it is the load-bearing half.** The vocabulary member
> `UNADJUDICATED` is the ONLY one an automated producer may write, and a row carrying it **must
> carry no adjudicator and no date**. A machine that began filling in the named human's
> judgements would therefore fail at construction rather than at review. *An autonomous story
> that tags its own findings TP has measured nothing and has produced the exact artifact Epic 13
> exists to make impossible.*

> ### 👤 DATED BLOCK — 2026-08-22 — **THE QA LEAD ROLE IS FILLED: Veer Pratap Singh**
>
> **This block sits under the existing V1.3 and adds NO change-log row**, because nothing in the
> protocol's *method* changed — §2's three roles, §3's budget, §4's ladder and §5's seven conditions
> are all byte-unchanged. What changed is a **holder cell**. Adding a `V1.4` row would re-stamp
> `protocol_version` across the 31 committed judgements of 2026-08-17, which is exactly the act
> `§3.4` forbids; the change-log head is therefore unmoved and
> `TC-ArgusAgent-PRECISION-001-45` / `-63` are untouched. This is the **fourth** dated block under
> V1.3.
>
> **Who, and when.** **Veer Pratap Singh** fills the **QA Lead (second reviewer)** role, named by
> **XAgent007 (Engineering Lead)** on **2026-08-22**. Dispositions authored in this role carry the
> `adjudicator` id **`"Veer Pratap Singh (QA Lead)"`** — the role string must match
> `PROTOCOL_ADJUDICATOR_ROLES` exactly or `AdjudicationRow.__post_init__` raises
> `UnregisteredAdjudicator` at construction.
>
> **Why it was filled BEFORE the story that needs it, and not during.** Story 16.7 adjudicates a
> 36-member class, and the only comparable population — the 2026-08-16 set of 31 — produced **5
> borderlines**, so roughly six are expected. §4's ladder terminates at this role. **A role filled
> mid-adjudication is a role filled to unblock a result**, and it would be indistinguishable, on the
> record, from a role filled to obtain one. Filling it in advance, in its own act, is what keeps the
> two apart. This is the same discipline as the 2026-08-17 pre-registration and the bench's
> pick-before-you-look rule, applied to staffing.
>
> ⛔ **What this does NOT do.** It adjudicates nothing, promotes nothing, and moves no threshold. It
> does **not** fill the **External adjudicator** tie-break, which stays *unfilled* — so a borderline
> on which the Engineering Lead and QA Lead **persistently disagree** still has nowhere to go, and a
> story reaching that step must STOP and report the rows rather than resolve them by default. It
> makes **no claim of independence for an externalization sign-off**: §2 records that the tie-break
> "SHOULD be outside the implementing team" for that purpose, and that bar is untouched here.
> Whether any given adjudication was independent is Story **16.5**'s question to record, not this
> block's to assert.

---

## 3. Expert-hours/repo budget

- **Per planted-defect / holdout cartridge:** ≤ **2 expert-hours** to author + label the golden
  key (the SET of `GoldenFinding` rows) and confirm each expected finding is one a human auditor
  would genuinely raise. A holdout cartridge is labeled **author-blind** (the labeler does not
  tune any detector to it).
- **Per clean-control / trap / no-crash cartridge:** ≤ **1 expert-hour** to confirm the repo is
  genuinely clean (golden key empty, `max_blocking == 0`) and that any emitted finding on it is a
  true false-positive (the R6 denominator).
- **Per gate-flip adjudication run (the full corpus at N≥5):** ≤ **4 expert-hours** for the
  Engineering Lead + QA Lead to review the harness's per-cartridge rows, adjudicate every FP/FN,
  and record the per-metric pass/fail.

The budget is a ceiling, not a target; a cartridge that needs more than its budget to label
honestly is a signal the cartridge is ambiguous and SHOULD be reworked or deferred, not forced.

> ### ⚖️ AMENDMENT 2026-08-16 (Story 13.2 / AC5) — **the actual hours are a FIELD, not prose**
>
> The three budgets above are unchanged. What is added is that the **actual** expert-hours of a
> gate-flip adjudication run are recorded as `expert_hours` on the adjudication record — an exact
> `Fraction` (AR4, never a float) — and compared against the ≤ 4-hour ceiling by
> `adjudication.expert_hours_report()`, **which returns a sentence and gates nothing**. So the
> next run is scheduled on evidence rather than on the estimate.
>
> **Exceeding the ceiling is NOT a failure**, and this is stated mechanically because the
> temptation runs the other way: §3 already says the budget is *"a ceiling, not a target"* and
> that an overrun *"is a signal the cartridge is ambiguous"*. The overrun and **what made it
> expensive** are recorded. **Never trim the adjudication to fit the estimate** — that trades a
> measurement for a number, in the one measurement this project's externalization claim rests on.
> `TC-ArgusAgent-PRECISION-001-50` asserts the ≤4h figure in the code equals the one in this
> section (single source under assertion, `AI-E9-7`), and `-51` asserts an overrun reports rather
> than fails.
>
> **`expert_hours = null` means NOT RECORDED, never zero.** A zero would claim the work took no
> time; `null` says it has not happened. As of 2026-08-16 it is `null`: Story 13.2 delivered the
> instrument and escalated the run (AC7).

---

## 4. Precision-adjudication method

> **AMENDED 2026-08-16 (Story 13.1) — the method is unchanged; the corpus it runs over is not.**
> Every clause below applies **to the repository corpus** when adjudicating the ≥80% gate, and
> continues to apply to the cartridge corpus when adjudicating recall. The one clause that needs
> restating for real repositories is the golden-key one: **a real repository has no golden key.**
> On a cartridge, "genuinely real" is decided against a SET the team authored; on a real
> repository there is nothing to diff against, so **every blocking finding is adjudicated
> individually by the named human** under the ladder below, and the TP/FP judgment *is* the
> ground truth rather than a comparison against one. This is why the gate needs a human and why
> Story 13.2 cannot be autonomous.
>
> The finding identity used to record each adjudication is the **existing** 6.6
> `finding_match_key` — `(rule_id, verdict_eligible, advisory)` — reused unchanged, so an
> adjudicated real-repository finding and a cartridge finding mean the same thing by "the same
> finding" (DN-MATCH-KEY-REUSE; no second, divergent key).

- **Sample size.** Precision is computed over the **FULL** populated corpus (every registry row),
  not a sample — the corpus is small enough (≤ ~10 cartridges) to adjudicate exhaustively. Every
  emitted finding is classified; nothing is sampled out. *(Amended 2026-08-16: the same
  exhaustive rule holds for the repository corpus — every **blocking** finding Argus emits on a
  member is adjudicated, none is sampled out. Advisory findings are recorded but are not false
  accusations and do not enter the precision denominator, matching `compute_precision`'s
  existing classification and the 6.5 `max_blocking == 0` floor.)*
- **Who judges a 🔴 "genuinely real".** A blocking (verdict-eligible) finding on a labeled
  planted-defect cartridge is "genuinely real" iff it is in that cartridge's golden key AND the
  **QA Lead** confirms a human auditor would raise it. A blocking finding on a **clean / trap /
  no-crash** repo is, by definition, a **false positive** (the R6 false-accusation floor) — no
  adjudication can rescue it; it depresses precision in the denominator.
- **Borderline resolution.** When the Engineering Lead and QA Lead disagree whether an emitted
  finding is a TP or an FP:
  1. Re-examine the cited **locator** (FR13 — every finding carries ≥1 verifiable locator). If the
     locator does not point at a genuine defect, the finding is an **FP**.
  2. If the locator points at a real concern but the finding's `rule_id` / advisory shape mismatches
     the golden key, the **golden key** is corrected (≤ 2 expert-hours) and re-run — the harness is
     deterministic, so the re-run is byte-reproducible.
  3. If disagreement persists, the **external adjudicator** (§2) breaks the tie. The decision and
     rationale are recorded append-only in this protocol's change log AND in
     `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` if it surfaces a detector gap.
- **Determinism precondition.** Adjudication is only valid over a **byte-reproducible** harness run
  (NFR-P1): the harness MUST produce identical per-cartridge rows + precision ratio across two runs
  over the same corpus before any pass/fail is recorded. *(Amended 2026-08-16: over the repository
  corpus this is the **existing** check — `scripts/audit_validation_corpus.py` audits each member
  twice at its pinned sha and records `byte_reproducible_across_two_runs` per member. A second
  reproducibility check is **not** authored; the result is read off the adjudication set and
  carried on the record as `reproducibility_verified` + `reproducibility_source`, and
  `fold_adjudicated_precision` evaluates it **first**, before exhaustiveness and before the ratio.
  A non-reproducible run makes the adjudication **invalid and says so**, rather than carrying
  dispositions that rest on nothing.)*

> ### ⚖️ AMENDMENT 2026-08-16 (Story 13.2 / AC2) — **WHAT ONE "FINDING" IS, decided BEFORE the run**
>
> **The defect.** §7 locks *"precision is measured over **FINDINGS**, not repos"*, while
> `compute_precision` takes `emitted_keys_by_cartridge: dict[str, frozenset[MatchKey]]` and
> computes `tp = len(tp_keys)` — a count of distinct `(rule_id, verdict_eligible, advisory)`
> **CLASSES**. Those are two different quantities and the divergence is not marginal:
> `minions-dogfood-proof.md` reports `hardcoded_secret` ×**26** and `orphan_code` ×**92** as one
> row each, and on the superseded Minions population `hardcoded_secret` ×**2289** collapses to a
> single key — three orders of magnitude between the locked quantity and the computed one. On the
> ratified 13.1 corpus, **31 blocking findings across two members are ONE class**
> (`vacuous_test_ast`), so a per-class fold would compute precision over a denominator of 1.
>
> **DECISION (2026-08-16, Story 13.2 / DN-2a): the unit is the FINDING.** §7 is an OI1 invariant
> whose own heading says do not soften it, and the alternative — amending §4/§5/§7 to say *class*
> — would redefine the gate's denominator downward in the story that measures it. Rejected for
> that reason and recorded here rather than in a story file.
>
> **What the finding identity IS.** `(member_id, rule_id, verdict_eligible, advisory, locator)`.
> The shared 6.6 `finding_match_key` is **reused unchanged** and stays derivable from every row
> (`AdjudicationRow.match_key`), so DN-MATCH-KEY-REUSE holds — no second, divergent identity. The
> two added coordinates are what distinguish two findings *of the same class*, which is the whole
> content of "per finding".
>
> **What that means for the arithmetic, stated because the obvious reuse is wrong.** The
> golden-key **diff** in `compute_precision` classifies by class MEMBERSHIP, so a class present in
> the golden key contributes its entire multiplicity as TP. On a real repository one rule class
> routinely holds both real and false findings — and a membership diff cannot express *"this class
> is 20 TP and 4 FP"*. Adding a multiplicity map to `compute_precision` was considered and
> **rejected**: it would carry the multiset faithfully and still assign all 24 to whichever side
> the class landed on. So the repository fold counts dispositions directly, and what is shared —
> and MUST stay shared — is the **arithmetic**: `precision_fraction`, `gate_is_provisional`,
> `PRECISION_GATE_THRESHOLD` and `precision_gate_status_for` are the same objects both folds use.
> **One arithmetic, two populations.** The cartridge fold remains per-class and is correct there:
> a cartridge's golden key is authored per class, and that fold measures **recall**, not the gate.
>
> **Ordering is MECHANICAL, not a promise.** *"The protocol is amended BEFORE the run, never
> reinterpreted during it"* is enforced: the adjudication record carries `protocol_version`, and
> `TC-ArgusAgent-PRECISION-001-45` asserts it equals the **current head** of this document's
> change log (parsed by `adjudication.change_log_head_version`). **A record adjudicated under a
> superseded protocol FAILS** — so an amendment made after dispositions were recorded turns the
> suite red instead of quietly re-interpreting them.
>
> **Exhaustiveness is proven, not asserted** (AC4). `AdjudicationRecord.exhaustiveness()` requires
> every emitted finding to carry exactly **one live** TP/FP disposition (superseded rows excluded).
> `BORDERLINE` — *looked at, could not decide* — is a **first-class outcome**, not an absence: it
> records that a human spent the time and that the ladder above has not terminated, and it makes
> the run **non-exhaustive** until it resolves. Any residual makes the run **`Unevaluable`,
> recorded with the residual count** — never a pass over the adjudicated subset. The guard
> asserts it extracted **> 0** rows before asserting anything about them; an empty population is
> itself `Unevaluable`, because a guard that silently iterates an empty record passes forever.

---

## 5. Per-metric pass/fail thresholds

| Metric | Pass threshold | Source |
|---|---|---|
| **Precision** (TP / (TP + FP) over findings) | **≥ 80%** — checked as the EXACT `Fraction` `precision >= Fraction(4, 5)` (no float rounding) | PRD ≥80%-precision externalization gate; `PrecisionResult.meets_threshold` |
| **False-positive ceiling on clean repos** | **0 blocking** false positives on any `clean_control` / `trap` / `no_crash` repo (`clean_repo_fp == 0` for blocking findings). **⚠️ AMENDED 2026-08-16 (Story 13.2 / AC1c) — this condition must NAME the corpus it is measured over.** `_is_clean_repo` requires an **empty golden key AND `max_blocking == 0`** (`replay_harness.py`), and **no repository-corpus member has either** — so over the population that actually gates externalization the condition was **vacuously 0 for every possible input**, and reporting it as one of the four met conditions would have been a false green of the strongest kind. **A §5 condition that cannot fail is not a threshold.** Resolved additively rather than by softening: it remains a **real threshold over the CARTRIDGE corpus**, where `compute_precision` measures it and reports `clean_repo_fp_applicable=True` naming the clean members it folded; and over the **repository corpus** it is recorded **NOT APPLICABLE with its reason** (`AdjudicatedPrecision.clean_repo_fp_note`), never as satisfied. Story 13.3 must therefore evaluate this condition against the cartridge corpus explicitly, or record it not-applicable — it may not count it as met by default. Guards: `TC-ArgusAgent-PRECISION-001-36` and `-37`. | R6 false-accusation floor; the 6.5 `max_blocking == 0` contract |
| **Corpus floor** | ~~**N ≥ 5** distinct labeled planted-defect (+ holdout) cartridges (`populated_planted_defect_count() >= VALIDATION_SET_FLOOR_N`)~~ **STRUCK 2026-08-16 (Story 13.1 / DN-1) — this named the wrong corpus.** Replaced by: **N ≥ 5** eligible members of the **validation set** — independent real repositories (`_manifest.eligible_member_count() >= VALIDATION_SET_FLOOR_N`, i.e. `meets_validation_floor()`). The **same** `VALIDATION_SET_FLOOR_N = 5` is reused, never forked (DN-3). ~~**Measured 2026-08-16: N = 0 — NOT MET.**~~ **Superseded the same day: the operator ratified five members under Story 13.1 / AC3b — `N = 5`, floor MET** (struck, not erased: the zero was the state at the moment the corpus definition was decided, before ratification). **Floor met ≠ gate cleared** — see the status note below §5. | OI1 LOCK; PRD §Validation Approach (`N ≈ 5–10` real repositories); `VALIDATION_SET_FLOOR_N = 5` |
| **Recall over planted defects** *(added 2026-08-16 — this is what the cartridges gate)* | the FR20 cartridge harness stays green: every golden key emitted, `max_blocking == 0` on every clean control. **Not** a threshold on the externalization gate — a **diagnostic of the detectors**, reported alongside. Measured 2026-08-16: **7 populated rows across 5 distinct rule classes.** | FR20; `tests/cartridges/_registry.py`; `distinct_rule_class_count()` |
| **Recall** (TP / (TP + FN)) | reported as a **diagnostic** (not gated in V1) — a low recall is a coverage signal, but the externalization gate is **precision** (the OI1 lock). **⚖️ AMENDED 2026-08-20 (Story 16.3 / AC2) — this row is NOT softened and NOT rewritten; the sentence before this marker is byte-unchanged and recall stays UNGATED and DIAGNOSTIC. What is added is a boundary, so no future reader can read a recall gate into §5's seventh condition.** §5 gained, the same day, a **YIELD** condition: `detector-yield-verdict-eligible-population-floor`. **What it IS:** a floor on the **DENOMINATOR of the precision ratio** — the number of verdict-eligible findings the ratio is computed over — DERIVED from the gate threshold's own arithmetic as `ceil(q / (q − p))` over `PRECISION_GATE_THRESHOLD = p/q`, i.e. **the smallest denominator at which "≥ 80%" is not silently "100%"** (= **5** at the shipped 4/5). It is a statement about the **RESOLUTION of the measurement that was taken**. **What it is NOT:** a floor on **recall**, on **coverage**, or on **any estimate of `FN`**; it makes no claim about defects the detector MISSED, and it does not re-open the OI1 lock. The distinction turns entirely on **where the number comes from**: this floor's only inputs are the threshold and the counted population. ⛔ A floor derived instead from **how much of the defect class the bench carries** — e.g. *"the sealed partition holds 431 co-occurrence files, so expect at least X"* — would estimate `FN` from a text proxy and gate on it. **That would be recall by another name, it WOULD re-open OI1, and it is an OPERATOR ESCALATION, not an implementation choice.** The boundary is enforced **structurally**, not promised: `TC-ArgusAgent-PRECISION-001-99` walks `argus/precision/gate_yield.py`'s own AST and fails if the module imports any recall symbol or references any `FN` / co-occurrence / bench-content quantity, and the guard is itself driven RED by adversarial variants that add one. Line 312's *"Recall over planted defects"* row governs the **cartridge** corpus and is **untouched**; §7's OI1 invariants are **untouched** (they carry no recall bullet). | `PrecisionResult.recall_ratio` |

**The gate is CLEARED iff ALL of:** precision ≥ 80% (exact Fraction) **AND** the clean-repo
blocking-FP count is 0 **AND** N ≥ 5 **AND** this protocol's adjudication run is recorded cleared.
If ANY fails, the gate stays **PROVISIONAL** and the harness reports the number as an early signal.

> **⚖️ AMENDED 2026-08-20 (Story 16.1 / AC1; sprint change proposal 2026-08-20 §4.3(1), approved
> by XAgent007 2026-08-20) — A FIFTH CONDITION: THE DENOMINATOR MUST BE BROAD ENOUGH TO MEAN
> SOMETHING.** The sentence above is **not edited** and its conjunction is not re-wrapped (§3.4:
> amend by dated ADDITION, strike rather than erase). The new conjunct is stated here and is
> **APPENDED** to the condition set, so §5's four historical conditions keep their historical
> positions and their ids.
>
> **The new condition.** The precision ratio is **EVALUABLE only over a population drawn from at
> least `(VALIDATION_SET_FLOOR_N + 1) // 2` — i.e. `ceil(N_floor / 2)`, which at the locked floor
> of 5 is **3** — DISTINCT CONTRIBUTING members** of the ratified repository validation set. Below
> that, §5's **precision** condition is recorded `UNEVALUABLE` with the counts that made it so, and
> the gate outcome is `BLOCKED` with a countable closure path. The breadth condition's **own**
> verdict is `MET` or `FAILED` — it *was* evaluated, over a named population. Condition id:
> `denominator-breadth-contributing-members`. Guards:
> `TC-ArgusAgent-PRECISION-001-82`..`-85`.
>
> **Why.** §5's `N >= 5` is satisfied by MEMBER COUNT while the ratio is computed over whichever
> members actually emitted a blocking finding — *the N that gates and the N that contributes are
> different numbers*. The committed gate record has DISCLOSED that since 2026-08-17 and has been
> unable to act on it: as shipped, a gate could report **CLEARED** on a figure measured over **one
> repository**, and the record would say so in a paragraph a reader is free to skip. A disclosure
> the reader may weigh is not a condition the gate must satisfy.
>
> **This is a STRENGTHENING, and the distinction from a forbidden threshold change is spelled out
> rather than asserted.** §5 and Story 13.3 / AC5 forbid any change that makes clearing EASIER —
> narrowing a corpus, dropping a member, re-weighting one, or moving a threshold to fit a result.
> This condition can only make clearing **harder**: every population that cleared before this
> amendment either still clears or is now `BLOCKED`, and no population that failed before can pass
> because of it. It touches **nothing else**: the ≥ 80% `Fraction`, `VALIDATION_SET_FLOOR_N = 5`,
> the five ratified members, `MANIFEST_FIELDS` (closed at 9), `GATE_OUTCOMES` (closed at three) and
> `CONDITION_VERDICTS` (closed at four) are all byte-unchanged, verified by execution. And it is
> made **BEFORE the measurement it governs** — `DF-13-5-A`'s one permitted round is UNSPENT — which
> is the whole point: adding a breadth requirement after seeing what the bench yields would be
> corpus-shopping in the opposite direction.
>
> **⛔ The RULE-CLASS arm was DERIVED and deliberately NOT LANDED, by operator decision (XAgent007,
> 2026-08-20).** An honest breadth condition has two arms — *not one repository* and *not one
> rule*. Measured at `0a6e121` by two independent instruments (an AST walk of all seven
> `build_recording` call sites, of which only `argus/detectors/vacuous_test.py:1067` passes a
> non-`None` `depth_supported`, with the Prosecutor's promotion path unreachable because the single
> production `prosecute()` call site at `argus/pipeline.py:535` supplies no `sign_offs`; and a
> direct count over both committed adjudication sets — 2026-08-16: 6 rule classes emitted, **1**
> verdict-eligible; 2026-08-18: 5 emitted, **0**): **the maximum achievable distinct
> verdict-eligible rule-class count is 1.** A floor of **≥ 2 would be a SHUTDOWN**, not a
> strengthening — it would make `CLEARED` unreachable by construction with the shipped detector
> set — and a floor of **1 could not fail for any admissible input**, which this protocol already
> refuses in its own words above: *"A §5 condition that cannot fail is not a threshold."* Neither
> was landed. The rule-class count is still **DISCLOSED** on every decision. The detector-side work
> that would make the arm achievable is filed on the deferred-work ledger as **`DF-16-1-A`**, and
> landing a rule-class floor remains an operator decision taken in the open.
>
> **⚠️ NO CHANGE-LOG VERSION WAS TAKEN, and that is deliberate (operator decision, 2026-08-20).**
> This amendment sits **under the existing V1.3**. The committed adjudication record holds **31
> human judgements** (26 FP / 5 BORDERLINE, `XAgent007 (Engineering Lead)`, 2026-08-17) made under
> V1.3. Adding a `V1.4` row would re-stamp `protocol_version` across all 31 — precisely the act
> `decide_gate`'s own refusal names: *"a decision folded across an amendment is a re-interpretation
> of judgements nobody re-made."* The amendment is additive to §5, touches no §4 rule, no golden-key
> semantics and no TP/FP definition, so no judgement's MEANING moves; the version therefore does
> not move either, the 31 judgements keep their original V1.3 provenance untouched, and
> `TC-ArgusAgent-PRECISION-001-45` / `-63` stay green without any record being regenerated. Only
> `gate-decision-record.json` was regenerated, because the condition SET it publishes grew.

> **⚖️ AMENDED 2026-08-20 (Story 16.2 / AC3; sprint change proposal 2026-08-20 §4.3(2), approved
> by XAgent007 2026-08-20) — A SIXTH CONDITION: THE EVIDENCE THAT GATES MUST COME FROM A
> PARTITION THE TOOL WAS NEVER TUNED AGAINST.** This is the **second** dated block under V1.3 and
> it edits **no existing byte**: the conjunction sentence above is not re-wrapped, the fifth
> condition's block is untouched, and the new conjunct is **APPENDED** to the condition set so §5's
> five historical conditions keep their historical positions and their ids.
>
> **The problem, stated as the change proposal states it (H-2).** *"Nothing is held back. The
> cartridge corpus has an author-blind holdout (`holdout_vacuous`). The repository corpus that
> actually gates has none. If all 14 bench members are adjudicated and the detector is then tuned,
> no untouched population remains to show the tool was not shaped to fit its own exam."* §6's
> phased plan and §3's author-blind labelling give the cartridge corpus that protection. The
> repository corpus has **no golden key a labeler could be blinded to**, so the equivalent
> protection has to be an **ordering**: a partition decided and frozen, in code and in git, before
> any detector output over any member of it exists.
>
> **THE PARTITION RULE, frozen 2026-08-20 and stated here in full.** Every member of the corpus
> lies in exactly one of **three** partitions — `sealed`, `open`, `pre-seal` — assigned by two
> conjuncts, in this order:
>
> 1. **PRIOR-OUTPUT OVERRIDE.** A member over which Argus output already existed when the seal was
>    taken is **`pre-seal`**, unconditionally, whatever its sha says. *A member that has already
>    been run over cannot be a holdout, and a rule capable of sealing one would manufacture a fake
>    holdout.* The set is DERIVED from the `members[]` arrays of the committed adjudication sets,
>    not typed: guard `TC-ArgusAgent-PRECISION-001-88`.
> 2. **THE BISECTION.** Every other member is **`sealed`** iff `int(commit_sha, 16) % 2 == 1` — the
>    parity of the pinned object name read as an integer — and **`open`** otherwise.
>
> The rule is executable code in ONE place (`argus/precision/gate_seal.py::partition_of`), pure,
> and its derivation and rejected alternatives are recorded WITH it. A member's partition is
> **structurally readable off its manifest row** (`CorpusMemberSpec.partition`) and is **DERIVED,
> never stored**: it cannot be changed without changing the **pin**, which changes which bytes are
> audited, is visible in the diff, and is refused at construction. **`MANIFEST_FIELDS` stays CLOSED
> at 9** — a derived property is not a dataclass field.
>
> **⛔ SET-RELATIVE RULES WERE REJECTED ON A DECISIVE GROUND.** Sorting by sha and alternating the
> index would produce a partition that **re-partitions silently** when the operator ratifies eleven
> members instead of fourteen — removing one member shifts every subsequent index — so it is
> *re-derivable after the fact to a different answer*, which is exactly what "pre-committed"
> forbids. A per-row function of the pin is stable under every ratification subset: **each member's
> partition is already determined and publishable today**, so §6 **R2** can change the partition's
> SIZE but never a MEMBER'S partition.
>
> **The new condition.** The precision ratio is **EVALUABLE only over a population drawn from at
> least `(VALIDATION_SET_FLOOR_N + 1) // 2` — the SAME derived floor §5's breadth condition uses,
> **3** at the locked floor of 5 — DISTINCT CONTRIBUTING members lying in the `sealed` partition**.
> Below that, §5's **precision** condition is recorded `UNEVALUABLE` with the counts that made it
> so, and the gate outcome is `BLOCKED` with a countable closure path. The seal condition's **own**
> verdict is `MET` or `FAILED` — the provenance of the evidence *was* established, over a named
> population; `UNEVALUABLE` would tell a reader it was unknown, which is a different and false
> claim. Condition id: `gate-evidence-drawn-from-the-sealed-partition`. Guards:
> `TC-ArgusAgent-PRECISION-001-87`..`-94`.
>
> **The floor is 16.1's, RESOLVED and not forked.** §5 now carries one derived member floor read by
> two conditions: breadth asks *how many distinct members contributed*, the seal asks *how many of
> those were members the tool was never tuned against*. A second, seal-specific constant was
> rejected — DN-3's one-floor rule, and two floors is how two corpora happened in the first place.
>
> **⛔ IT PARTITIONS; IT DOES NOT NARROW, and the distinction is the whole of §5's own prohibition.**
> `VALIDATION_SET_FLOOR_N` stays **5**, `eligible_member_count()` stays **5**, no member is dropped,
> re-weighted or made ineligible, no `adjudication_caveat` is edited, and **every finding from every
> partition stays recorded and stays disclosed** — the seal governs what may **GATE**, never what is
> **REPORTED**. Both narrowing designs (filtering the record's rows to sealed members; deriving the
> concentration over the sealed subset alone) were tested by execution and both `raise` on the
> committed population, which is the correct refusal: a filter NARROWS, which §5 and Story 13.3 /
> AC5 forbid, while a CONDITION REQUIRES, which is a strengthening. Every population that cleared
> before this amendment either still clears or is now `BLOCKED`; no population that failed before
> can pass because of it.
>
> **⛔ WHAT §6 R2 MUST NOW WEIGH, COUNTED IN ADVANCE RATHER THAN DISCOVERED AFTER.** Sealed ∩
> ratified is currently **∅**, so the condition reads `FAILED` today and that is correct: the gate
> cannot clear on evidence that predates the seal. It is **satisfiable** — the bench holds six
> sealed candidates against a floor of three, slack three, and all six clear Story 15.1's
> co-occurrence floor — but only by an act §6 **R2** takes: **at least THREE members of the
> `sealed` partition must be ratified, and each must contribute at least one adjudicated finding.**
> **Ratifying only `open`-partition members leaves this condition permanently `FAILED`.** That is
> honest, it is countable, and the operator is told it here, before the act.
>
> **A POST-SEAL DETECTOR CHANGE MUST SAY WHICH PARTITION ITS EVIDENCE CAME FROM.** Any commit
> touching a declared detector-tuning path that is not an ancestor of the seal commit carries a
> machine-checkable trailer `Evidence-partition: sealed | open | none`. This is a **disclosure, not
> a prohibition**: the value of a holdout is the *comparison across partitions*, and the comparison
> is only possible if each change says which side it learned from. The rule is written down in
> `argus/precision/gate_seal.py::SEAL_CITATION_RULE` and enforced against real git history by
> `TC-ArgusAgent-PRECISION-001-93` / `-94`.
>
> **OPENING THE SEALED PARTITION IS A SINGLE RECORDED ACT, NEVER A SIDE EFFECT.** The seal is
> opened only by a §6 **R2**-class operator act, recorded in this protocol as a further dated block
> naming who took it, when, and which members moved — the same act class that ratifies a member.
> **Running the harness does not open it, cannot open it, and no code path in this repository opens
> it**: the partition is derived from pins, the pins are frozen, and Story 16.2 added no writer.
> An agent may not take this act.
>
> **⚠️ NO CHANGE-LOG VERSION WAS TAKEN — the same operator decision of 2026-08-20, applied again.**
> This amendment sits under the existing **V1.3** beside the fifth condition's block. The 31 human
> judgements of 2026-08-17 keep their original V1.3 provenance untouched; adding a `V1.4` row would
> re-stamp `protocol_version` across all 31 and re-interpret judgements nobody re-made. The
> amendment is additive to §5, touches no §4 rule, no golden-key semantics and no TP/FP definition,
> so no judgement's MEANING moves. `TC-ArgusAgent-PRECISION-001-45` / `-63` stay green and
> `adjudication-record.json` was **not** regenerated. Only `gate-decision-record.json` was, because
> the condition SET it publishes grew — and regenerating it executes **no** detector, stages **no**
> repository and touches **no** candidate.

> **⚖️ AMENDED 2026-08-20 (Story 16.3 / AC1; sprint change proposal 2026-08-20 §4.3(3), approved
> by XAgent007 2026-08-20) — A SEVENTH CONDITION: A RATIO OVER THREE FINDINGS NEVER FACED THE
> BAR IT IS PUBLISHED AGAINST.** This is the **third** dated block under V1.3 and it edits **no
> existing byte**: the conjunction sentence above is not re-wrapped, the fifth and sixth
> conditions' blocks are untouched, and the new conjunct is **APPENDED** to the condition set so
> §5's six historical conditions keep their historical positions and their ids.
>
> **The hole, PROVED by execution rather than argued.** Story 13.2's `UNEVALUABLE` closed the
> case of an **empty** denominator and Story 13.5 made *"the corpus was read and nothing was
> promoted"* expressible. Neither closes the **tiny** one. Driven through the shipped
> `decide_gate` at `1ecf618`, a population of **exactly three findings — one per sealed member,
> all adjudicated TP — returned `CLEARED`** at precision `1/1`, with all six §5 conditions
> reporting `MET` and an outcome sentence reading *"Clearing authorises ATTESTED
> externalization."* So did four. **Three findings. All correct. Cleared.**
>
> **The new condition.** The precision ratio is **EVALUABLE only over a VERDICT-ELIGIBLE
> population of at least `ceil(q / (q − p))` adjudicated findings**, for the gate threshold
> `PRECISION_GATE_THRESHOLD = p/q` in lowest terms — **which at the locked 4/5 is 5**. Below that
> floor, §5's **precision** condition is recorded `UNEVALUABLE` with the counts that made it so,
> and the gate outcome is `BLOCKED` with a countable closure path. The yield condition's **own**
> verdict is `MET` or `FAILED`, never `UNEVALUABLE` — the population *was* counted. Condition id:
> `detector-yield-verdict-eligible-population-floor`. Guards:
> `TC-ArgusAgent-PRECISION-001-95`..`-100`. It **composes** with the fifth and sixth conditions
> and replaces neither: quantity without breadth still fails, and breadth without quantity now
> fails too — both driven, in both directions, at the real seam.
>
> **Why THAT number, and why it is not typed.** At a denominator `d` the largest number of false
> positives a population can carry and still clear is `max{ k : (d − k)/d ≥ p/q }`. Executed over
> the shipped threshold that count is **0 at d = 1, 2, 3 and 4**, and **1 at d = 5**. **Below a
> denominator of five, the ≥ 80% gate is silently a 100% gate**: a detector that emits three
> findings and gets all three right has not cleared an 80% bar, it has cleared a bar it never
> faced — and the record publishes the figure as though it had. The floor is the smallest
> denominator at which the threshold means the thing it is written as. ⛔ It is stated in the
> **general form** because `ceil(q / (q − p))` equals `q` **only when `q − p == 1`**: at `5/7` the
> floor is 4 and at `7/9` it is 5, verified against brute force. Writing `threshold.denominator`
> would be correct by coincidence at exactly the one threshold shipped, which is Story 16.1's
> *"strict majority"* correction repeated one story later. **⚠️ `VALIDATION_SET_FLOOR_N` is also
> 5 and the equality is a COINCIDENCE, disclosed rather than leaned on**: one counts members that
> must EXIST, the other is the smallest denominator at which a ratio threshold is the threshold it
> is written as, and coupling them would move a §5 threshold as a side effect of a corpus-floor
> change. The floor is likewise **not** resolved from the breadth/seal floor of 3 — a different
> quantity from a different source — and both of those are left byte-unchanged.
>
> **It is NOT vacuous, and the check ran from two directions.** *"A §5 condition that cannot fail
> is not a threshold"* is this protocol's own sentence, above. (i) `derive_concentration` raises
> on an empty population, so a floor of **1** could never fail. (ii) The smallest population that
> passes **both** breadth and the seal is **3**, so a floor of **2 or 3** could never FIRE — every
> population it would block is already blocked upstream. The derived floor of **5 fires on exactly
> the sizes 3 and 4**, which are precisely the two measured as wrongly `CLEARED` above. The
> derivation and the vacuity bound agree from two directions that share no reasoning.
>
> **This is a STRENGTHENING and it can only make clearing HARDER**, verified by execution: a
> population returning `CLEARED` at sizes 3 and 4 before this amendment returns `BLOCKED` after
> it, every population that cleared before either still clears or is now `BLOCKED`, and **no**
> population that failed before can pass because of it. It touches **nothing else**: the ≥ 80%
> `Fraction`, `VALIDATION_SET_FLOOR_N = 5`, `eligible_member_count() == 5`, the five ratified
> members, `MANIFEST_FIELDS` (closed at 9), `GATE_OUTCOMES` (closed at three), `CONDITION_VERDICTS`
> (closed at four), the sealed partition table and the breadth/seal floors are all byte-unchanged.
> It governs what may **GATE**, never what is **REPORTED**: every finding from every member stays
> recorded and stays disclosed. And it is made **BEFORE the measurement it governs** —
> `DF-13-5-A`'s one permitted round is **UNSPENT** — which is the whole point.
>
> **⛔ IT IS NOT A RECALL CONDITION, and the OI1 row above is amended in terms rather than left to
> be inferred.** `recall = TP / (TP + FN)` requires `FN`, which is unknowable over a repository
> corpus (*"a real repository has no golden key"*, V1.1). This condition's only inputs are the
> **counted verdict-eligible population** and the **gate threshold**; it carries no `FN` term, no
> estimate of one, and no quantity describing what the bench contains. It is a claim about the
> **resolution of the measurement taken**, never about what was missed. The boundary is enforced
> **structurally** by `TC-ArgusAgent-PRECISION-001-99`, which walks `gate_yield.py`'s own AST. A
> floor derived instead from bench content *would* be recall with an estimated denominator and is
> an **operator escalation**. See §5's Recall row, amended the same day.
>
> **⚠️ THE PRE-ROUND DISCLOSURE, owed BEFORE `DF-13-5-A`'s ONE round is spent, not after.**
> Counted out of the committed `adjudication-set-13-5.json` (2026-08-18, post-Epic-14): the
> **corrected** detector emitted **4,284 findings across all five ratified members and promoted
> ZERO** to verdict-eligible — 0 blocking. The only population that ever exceeded this floor was
> the 2026-08-16 set of **31**, produced under the **pre-Epic-14 corroboration rule that Epic 14
> REFUTED**, and adjudicated **0 TP / 26 FP / 5 BORDERLINE**. A yield above this floor has been
> achieved exactly once and was achieved **entirely by false positives**. The achievable yield over
> the **sealed** partition is **UNMEASURABLE** without fetching third-party source, which is a §6
> **R2** operator act — so it is recorded as **unmeasured, not as impossible**: a search for a
> STRUCTURAL cap on promoted findings found **none** (the corroboration path emits one finding per
> flagged test function and admits no *k*). **On the only evidence that exists, the likely outcome
> of the one pre-registered round is `BLOCKED` on yield** — which `DF-13-5-A`, answered 2026-08-17
> **before any number existed**, already routes to option **(b)**: the FR34 disclosure stands for
> V1.5 and the next attempt requires *"a materially better detector — NOT a bigger bench."* This
> condition is therefore not a new hurdle; it is **that stopping rule made arithmetic**, because
> without it a round yielding **three** would route to `CLEARED` while a round yielding **zero**
> routes to option (b) — two destinations for a materially identical result. The disclosure is
> carried **on the condition itself** (`YIELD_PROVENANCE_DISCLOSURE`), and every figure in it is
> RE-DERIVED from the committed artifacts by `TC-ArgusAgent-PRECISION-001-100`.
>
> **⚠️ NO CHANGE-LOG VERSION WAS TAKEN — the same operator decision of 2026-08-20, applied a
> third time.** This amendment sits under the existing **V1.3** beside the fifth and sixth
> conditions' blocks. The 31 human judgements of 2026-08-17 keep their original V1.3 provenance
> untouched; adding a `V1.4` row would re-stamp `protocol_version` across all 31 and re-interpret
> judgements nobody re-made. The amendment is additive to §5, touches no §4 rule, no golden-key
> semantics and no TP/FP definition, so no judgement's MEANING moves.
> `TC-ArgusAgent-PRECISION-001-45` / `-63` stay green and `adjudication-record.json` was **not**
> regenerated — asserted byte-unchanged. Only `gate-decision-record.json` was, because the
> condition SET it publishes grew — and regenerating it executes **no** detector over any bench
> member, stages **no** repository and touches **no** candidate.
>
> **INERT ON THE LIVE TREE, verified at the producing seam.** The committed population is 31,
> above the floor of 5, so the yield condition reads **`MET`** and the committed decision is still
> `BLOCKED` for the **Story 13.5** reason — the corpus was read and nothing was promoted — and not
> for a yield reason. ⛔ A reader must not take that `MET` as *"the detector currently yields 31"*;
> see the pre-round disclosure above, which the condition's own `measured` sentence carries.

> **⚖️ AMENDED 2026-08-16 (Story 13.2 / AC1b) — a FOURTH terminal state existed and was reported
> as the first.** The sentence above enumerates *cleared* and *provisional*. Measured by execution
> on `bc55e36`: a corpus emitting **nothing at all** (0 TP / 0 FP / 8 FN) returned
> `precision=1/1` — the *"no false positive emitted"* convention — `provisional=False`, and a gate
> string reading **"cleared"**, the moment any caller passed `protocol_cleared=True`. **An empty
> denominator is not an 80% result; it is no result.** The outcome is now **`UNEVALUABLE`,
> recorded with its counts**: `precision_evaluable=False`, `meets_threshold` forced `False`, the
> gate forced provisional, and a gate-status string that says `unevaluable` and neither *cleared*
> nor *met*. `precision_gate_status_for(evaluable=False, provisional=False)` **raises**. Guards:
> `TC-ArgusAgent-PRECISION-001-34` and `-35`. The three-outcome discipline is
> `scripts/release_preflight.py`'s (`Refusal` / `Unevaluable` / pass), reused rather than
> re-invented. *A green run that silently skipped the measurement is worse than a red one.*

> **Status as of 2026-08-16 (Story 13.1), measured by execution — ONE of the four now holds.**
> ~~`N = 0` eligible validation-set members~~ → **`N = 5`, the corpus floor is MET** (ratified and
> audited under AC3b; the struck zero was the state when the corpus definition was decided
> earlier the same day). The other three do **not** hold: no adjudication run has occurred, no
> ≥80% figure has been computed, and the clean-repo blocking-FP condition is unevaluated —
> `protocol_cleared` has never been passed `True` anywhere in the tree
> (`argus/precision/replay_harness.py:226` defaults it `False`). **A met floor is the weakest of
> the four conditions and the easiest to mistake for progress toward the gate: it says the
> corpus is big enough to argue over, not that the argument has been had.** **Story 13.1
> satisfies one of these four conditions and does not try to satisfy the rest.** It decides *which corpus the gate is measured over* and builds the manifest that makes
> the adjudication possible; clearing the gate is Story 13.2's human adjudication and 13.3's
> computation. Any change that lets a cleared gate be *stated* before that adjudication has run
> is a defect, not progress.

---

## 6. Phased-population plan (3 → 5)

> **AMENDED 2026-08-16 (Story 13.1).** The plan below describes the population of the
> **cartridge** corpus. It is retained because it is the true record of what happened, and
> because that population is still the recall substrate — but it is **no longer the plan for the
> externalization gate**, because the gate is measured over the repository corpus (§1
> amendment). Steps 1–2 are history and completed; **step 3 was satisfied for the cartridges
> and does not satisfy the gate**; step 4 is unchanged and still the only way the gate flips.
>
> **The repository corpus is populated on a different plan (Story 13.1 / AC3b → 13.2 → 13.3):**
>
> | Step | What | Who | State 2026-08-16 |
> |---|---|---|---|
> | R1 | Specify membership: a closed, machine-readable manifest with pinned shas and recorded exclusions | autonomous (Story 13.1 / AC3a) | ✅ **DONE** — `tests/corpus/_manifest.py` |
> | R2 | **Ratify** the member list, then stage and audit each at its pinned sha | **operator act** — Engineering Lead (XAgent007). Choosing which repositories are legitimate members, and fetching third-party source, are not autonomous acts | ⛔ **NOT PERFORMED** — Story 13.1 / AC3b; see the story's ESCALATION |
> | R3 | Adjudicate every blocking finding TP/FP under §4 | **named human** — Engineering Lead, QA-Lead second | ⛔ Story 13.2 |
> | R4 | Compute precision over the adjudicated findings; flip the gate only if all four §5 conditions hold | mechanical, over R3's record | ⛔ Story 13.3 |
>
> **No step may be skipped or simulated.** Populating the manifest with plausible repository
> names to make a count look met would be the worst available outcome in the story that defines
> the corpus, and is why R2 is an explicit operator gate rather than a task.

The corpus is populated **PHASED 3 → 5** (OI1):

1. **M1 (Story 6.5 — DONE).** Front-loaded **3 + 1** labeled cartridges:
   `vacuous_basic`, `hardcoded_secret`, `orphan_basic` (planted defects) + `holdout_vacuous`
   (the author-blind overfitting-defense holdout). Plus the clean denominator rows
   (`clean_control`, `evidence_sentinel` trap, `tool_breadth` no-crash) and the non-ASCII
   `nonascii_unicode` planted defect.
2. **Story 6.6 (THIS story — the harness + this protocol).** Stands up the precision harness over
   whatever the corpus holds, authors this protocol, and reports the gate **PROVISIONAL**. It does
   **not** manufacture cartridges merely to flip the gate.
3. **Phase to N ≥ 5 (continues into the dogfood / a follow-up).** Grow to **5 distinct
   planted-defect cartridge classes** with sufficient findings. **Who labels each new cartridge:**
   the **Engineering Lead** authors the cartridge + the golden key (≤ 2 expert-hours, §3); the
   **QA Lead** independently confirms each expected finding is genuinely real (§4). A holdout
   cartridge is labeled author-blind.
4. **When the gate flips to non-provisional.** Only when **all four** §5 conditions hold AND the
   adjudication run is recorded — at which point the harness caller passes `protocol_cleared=True`
   to `compute_precision`, `PrecisionResult.provisional` becomes `False`, and the gate-status
   string says "cleared". The flip decision is recorded in the originating story's Change Log + Dev
   Notes AND here. **6.6 does not flip the gate** (the corpus is below N=5).

The ground-truth schema is **designed for N=5 with NO harness refactor**: a new labeled cartridge
is a `CartridgeSpec` registry row + a `*.py.txt` template drop-in; `compute_precision` iterates the
registry mechanically (the 6.5 DN-REGISTRY additive promise, which 6.6 must not regress).

---

## 7. Honesty invariants (the OI1 lock — do NOT soften)

- **N is LOCKED at 5** (V1 gate floor). The schema + harness are DESIGNED for 5.
- **Population is PHASED 3 → 5.** 6.6 computes the number + authors this protocol + reports
  PROVISIONAL; physically reaching 5 may continue into the dogfood / a follow-up.
- **Precision is measured over FINDINGS, not repos** (TP / (TP + FP) over finding counts).
  *(RE-AFFIRMED and made true 2026-08-16, Story 13.2 / AC2 — **not softened**. This invariant was
  stated here and contradicted by the implementation, which counted rule CLASSES. The §4
  amendment decides the unit is the **finding**, defines the finding identity, and routes the
  repository fold through a per-finding record. Nothing in this bullet is weakened; what changed
  is that it is now enforced by `TC-ArgusAgent-PRECISION-001-46` (the record holds 31 findings across 1
  rule class, and a per-class fold would gate on a denominator of 1) rather than asserted.)*
- **The ≥80% gate is PROVISIONAL below N=5** — surfaced via the harness's `provisional` flag and
  the gate-status string (which REUSES / extends the 6.5 `precision_gate_status()` marker
  convention; no forked second marker).
- **No over-claim.** The harness never silently flips the gate to cleared; below N=5 (or with the
  protocol pass/fail not recorded cleared) the number is reported as an EARLY/PROVISIONAL signal.
- **No source/secret bytes** (NFR-S1). The golden keys + the precision result carry only counts +
  rule-id provenance + the fixed-precision ratio string — never a planted secret / source value.

---

## Change log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-08-16 | V1.3 | **The unit of adjudication is DECIDED, the adjudication record is REGISTERED, and three defects that let the gate be cleared without a single adjudicated finding are CLOSED (Story 13.2 / AC1–AC6).** Amended §1 (the adjudication record is added as the repository corpus's ground truth), §2 (named role holders + attribution asserted at construction; `UNADJUDICATED` is the only member an automated producer may write and it must carry no adjudicator), §3 (actual expert-hours are a `Fraction` field on the record, compared to the ≤4h ceiling **as a report, never a gate**), §4 (**the unit is the FINDING** — §7's locked quantity upheld against an implementation that counted rule CLASSES, on a corpus where 31 blocking findings collapse to 1 class; plus the exhaustiveness rule, the non-vacuity floor, the reuse of the EXISTING reproducibility check, and a mechanical `protocol_version` == change-log-head ordering guard), §5 (**a fourth terminal state, `UNEVALUABLE`** — measured: 0 TP / 0 FP returned `precision=1/1`, `provisional=False` and a gate string reading *"cleared"*; and the clean-repo blocking-FP row now **names its corpus**, because `_is_clean_repo` can never be true for a repository-corpus member and a condition that cannot fail is not a threshold). §6 and §7 are **unchanged and re-affirmed** — §7's *"precision over FINDINGS"* is upheld, not softened. **The gate did not move and could not have:** `protocol_cleared` is still `False` and still never passed `True` from `argus/**`; the record holds **31 `UNADJUDICATED` rows and zero judgements**; AC7 (the run itself) is **HALTED awaiting the named adjudicator** and the record reports `Unevaluable` with residual 31. | Developer (dev-story, Story 13.2) |
| 2026-08-16 | V1.2 | **Corpus POPULATED, and the V1.1 row's measured state corrected (Story 13.1 / AC3b; raised by code review R1).** The V1.1 row below records *"validation-set `N = 0`, floor NOT met"*, which was true when it was written and false by the end of the same story: the operator (XAgent007) ratified **five** members — `ai-body-runtime`, `agent-markovich`, `minions`, `xagents-webapp`, `agent-smith` — each measured before admission and audited through the unmodified `run_audit_detailed`, all five **byte-reproducible across two runs**. `N = 5`, **floor MET**. The V1.1 text is struck-not-erased per §3.4. **The gate is NOT cleared and moved no closer to cleared:** the floor is one of four §5 conditions; the adjudication run, the ≥80% figure and the clean-repo blocking-FP condition are all outstanding, and `protocol_cleared` has still never been `True`. **31 blocking findings** (24 `minions` + 7 `agent-smith`, all `vacuous_test_ast`) are the population Story 13.2 must adjudicate. **Why this row exists at all:** the V1.1 figure was a hand-written measurement that went stale inside its own story while the *derived* surfaces tracked reality correctly — the `DF-8-5-C` defect class, in prose. `TC-ArgusAgent-DOCS-001-75` now derives the count from the manifest instead of pinning it as a literal. | Developer (code-review iteration 1, Story 13.1) |
| 2026-08-16 | V1.1 | **Corpus amendment (Story 13.1 / DN-1) — the PRD governs.** §5's corpus floor named `N ≥ 5` labeled **planted-defect cartridges** while the PRD specified `N ≈ 5–10` **real repositories**; the two were never reconciled and the gate did not say which population it was measured over. Decided: the ≥80%-precision externalization gate is measured over the **repository corpus**, because a gate clearable by a corpus the team authored, planted and answered is not an externalization gate. The cartridges are **re-labelled, not demoted** — they remain the FR20 **recall** instrument, CI-asserted, and nothing in `tests/cartridges/` changed. Amended §1 (substrate + the new `tests/corpus/_manifest.py` gate ground truth), §4 (method applies to both corpora; a real repository has no golden key, so every blocking finding is adjudicated individually), §5 (corpus-floor row struck and re-pointed; recall row added), §6 (the repository corpus's R1–R4 plan added beside the retained cartridge history). §2 roles, §3 budget and §7 invariants **unchanged**. **Also corrected:** all three §1 substrate paths were dead (`tests/apaa/cartridges/_registry.py`, `minions_core/apaa/precision/replay_harness.py`, `tests/apaa/test_precision_replay.py` — none exists; moved by the 2026-08-03 separation). Measured state at amendment: validation-set `N = 0`, floor NOT met, no adjudication run, `protocol_cleared` never `True`. | Developer (dev-story, Story 13.1) |
| 2026-06-30 | V1 | Initial committed protocol (Story 6.6). Fixes WHO validates (Engineering Lead / QA Lead / external tie-break), expert-hours/repo budget, the precision-adjudication method (full-corpus exhaustive, borderline resolution via locator re-examination → golden-key correction → external tie-break), the per-metric pass/fail (≥80% precision exact-Fraction, 0 clean-repo blocking FP, N≥5 floor, recall diagnostic), and the phased-population plan (3→5, who labels, when the gate flips). Recorded BEFORE the ground-truth schema is frozen. Gate reported PROVISIONAL (corpus below N=5). | Developer (Amelia) |
