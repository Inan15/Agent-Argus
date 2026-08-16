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
  over the same corpus before any pass/fail is recorded.

---

## 5. Per-metric pass/fail thresholds

| Metric | Pass threshold | Source |
|---|---|---|
| **Precision** (TP / (TP + FP) over findings) | **≥ 80%** — checked as the EXACT `Fraction` `precision >= Fraction(4, 5)` (no float rounding) | PRD ≥80%-precision externalization gate; `PrecisionResult.meets_threshold` |
| **False-positive ceiling on clean repos** | **0 blocking** false positives on any `clean_control` / `trap` / `no_crash` repo (`clean_repo_fp == 0` for blocking findings) | R6 false-accusation floor; the 6.5 `max_blocking == 0` contract |
| **Corpus floor** | ~~**N ≥ 5** distinct labeled planted-defect (+ holdout) cartridges (`populated_planted_defect_count() >= VALIDATION_SET_FLOOR_N`)~~ **STRUCK 2026-08-16 (Story 13.1 / DN-1) — this named the wrong corpus.** Replaced by: **N ≥ 5** eligible members of the **validation set** — independent real repositories (`_manifest.eligible_member_count() >= VALIDATION_SET_FLOOR_N`, i.e. `meets_validation_floor()`). The **same** `VALIDATION_SET_FLOOR_N = 5` is reused, never forked (DN-3). **Measured 2026-08-16: N = 0 — NOT MET.** | OI1 LOCK; PRD §Validation Approach (`N ≈ 5–10` real repositories); `VALIDATION_SET_FLOOR_N = 5` |
| **Recall over planted defects** *(added 2026-08-16 — this is what the cartridges gate)* | the FR20 cartridge harness stays green: every golden key emitted, `max_blocking == 0` on every clean control. **Not** a threshold on the externalization gate — a **diagnostic of the detectors**, reported alongside. Measured 2026-08-16: **7 populated rows across 5 distinct rule classes.** | FR20; `tests/cartridges/_registry.py`; `distinct_rule_class_count()` |
| **Recall** (TP / (TP + FN)) | reported as a **diagnostic** (not gated in V1) — a low recall is a coverage signal, but the externalization gate is **precision** (the OI1 lock) | `PrecisionResult.recall_ratio` |

**The gate is CLEARED iff ALL of:** precision ≥ 80% (exact Fraction) **AND** the clean-repo
blocking-FP count is 0 **AND** N ≥ 5 **AND** this protocol's adjudication run is recorded cleared.
If ANY fails, the gate stays **PROVISIONAL** and the harness reports the number as an early signal.

> **Status as of 2026-08-16 (Story 13.1), measured by execution — not one of the four holds.**
> `N = 0` eligible validation-set members; no adjudication run has occurred; `protocol_cleared`
> has never been passed `True` anywhere in the tree (`argus/precision/replay_harness.py:226`
> defaults it `False`). **Story 13.1 satisfies none of these four conditions and does not try
> to.** It decides *which corpus the gate is measured over* and builds the manifest that makes
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
| 2026-08-16 | V1.1 | **Corpus amendment (Story 13.1 / DN-1) — the PRD governs.** §5's corpus floor named `N ≥ 5` labeled **planted-defect cartridges** while the PRD specified `N ≈ 5–10` **real repositories**; the two were never reconciled and the gate did not say which population it was measured over. Decided: the ≥80%-precision externalization gate is measured over the **repository corpus**, because a gate clearable by a corpus the team authored, planted and answered is not an externalization gate. The cartridges are **re-labelled, not demoted** — they remain the FR20 **recall** instrument, CI-asserted, and nothing in `tests/cartridges/` changed. Amended §1 (substrate + the new `tests/corpus/_manifest.py` gate ground truth), §4 (method applies to both corpora; a real repository has no golden key, so every blocking finding is adjudicated individually), §5 (corpus-floor row struck and re-pointed; recall row added), §6 (the repository corpus's R1–R4 plan added beside the retained cartridge history). §2 roles, §3 budget and §7 invariants **unchanged**. **Also corrected:** all three §1 substrate paths were dead (`tests/apaa/cartridges/_registry.py`, `minions_core/apaa/precision/replay_harness.py`, `tests/apaa/test_precision_replay.py` — none exists; moved by the 2026-08-03 separation). Measured state at amendment: validation-set `N = 0`, floor NOT met, no adjudication run, `protocol_cleared` never `True`. | Developer (dev-story, Story 13.1) |
| 2026-06-30 | V1 | Initial committed protocol (Story 6.6). Fixes WHO validates (Engineering Lead / QA Lead / external tie-break), expert-hours/repo budget, the precision-adjudication method (full-corpus exhaustive, borderline resolution via locator re-examination → golden-key correction → external tie-break), the per-metric pass/fail (≥80% precision exact-Fraction, 0 clean-repo blocking FP, N≥5 floor, recall diagnostic), and the phased-population plan (3→5, who labels, when the gate flips). Recorded BEFORE the ground-truth schema is frozen. Gate reported PROVISIONAL (corpus below N=5). | Developer (Amelia) |
