# Story 13.3: Record the result, and let it decide

Status: review

<!-- Created 2026-08-17 by create-story. Every premise below was re-measured BY EXECUTION on
     HEAD 411d891 before this file was written; see §0. Two defects in the flip path and two
     stale figures in the honesty-critical documents were found BY EXECUTION and are reproduced
     verbatim in §0.1 and §0.2 — read those first. The ONE input this story needs DOES NOT
     EXIST YET; see the BLOCKING PREREQUISITE immediately below. Validation is optional — run
     bmad-create-story:validate for a second pass before dev-story. -->

## Story

As a developer relying on Argus,
I want its stated status to match its measured status,
So that the disclosure disappears only when it has stopped being true.

This is the **third and last** story of **Epic 13 — Earn the Gate**, and the only one that
**decides**. 13.1 decided what the corpus is and built it (N=5, ratified). 13.2 built the
instrument and recorded 31 blocking findings. **13.3 computes the four §5 conditions over the
adjudicated record and lets the arithmetic decide** — it does not adjudicate, it does not tune,
and it does not choose the answer it would prefer.

`epics.md:2485`: *"13.1 -> 13.2 -> 13.3, strictly sequential. No parallelism — each story's
output is the next one's input."*

### What it is NOT

- **It does not adjudicate anything.** Not one disposition. `AdjudicationRow.__post_init__`
  raises if an `UNADJUDICATED` row carries an adjudicator id, so an agent that started filling
  in the named human's judgements fails at construction — but the constraint is not the
  guard, it is the point of the epic. Only **XAgent007** (protocol §2 Engineering Lead) judges.
- **It does not amend a threshold.** Not `Fraction(4, 5)`, not `VALIDATION_SET_FLOOR_N = 5`, not
  §5's table, not §7's OI1 bullets — **in either direction, for any reason, whatever the
  outcome**. *A failed measurement is the measurement working.*
- **It does not "decide" from an unmeasured record.** An `Unevaluable` fold is **not** a
  not-cleared result. See AC1: three terminal states, never two.
- **It does not publish.** No tag, no push, no release, no visibility change. `DF-12-9-A` stays
  OPEN and untouched. ⚠️ Measured: `origin/master` is `bc55e36`, **13 commits behind HEAD** —
  the entire Epic-13 delta is unpushed. **That is the correct state. Do not "fix" it.**
- **A cleared gate is not plan closure.** Clearing authorises **ATTESTED externalization and
  nothing else**. The epic-9 retrospective declared the plan FINAL once already and Epic 10 had
  to reopen it (AC7).

---

## ⛔ BLOCKING PREREQUISITE — the required input DOES NOT EXIST on this tree

**Measured by execution on `411d891`, 2026-08-17** (`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-record.json`):

```
rows: 31   counts: {'TP': 0, 'FP': 0, 'BORDERLINE': 0, 'UNADJUDICATED': 31}
adjudicator on every row: null        expert_hours: null (NOT RECORDED, never 0)
protocol_version: V1.3  ==  change-log head: V1.3     reproducibility_verified: True
validation_set_population_n(): 5      floor_n: 5

fold_adjudicated_precision(...)  ->  precision=None  precision_ratio='NOT COMPUTED BY THIS RUN'
                                     evaluable=False  meets_threshold=False  provisional=True
                                     exhaustiveness=UNEVALUABLE (residual 31 of 31)
                                     clean_repo_fp_applicable=False
                                     gate_status='unevaluable (…NEITHER cleared NOR met…)'
fold(..., protocol_cleared=True) ->  provisional STILL True, gate STILL 'unevaluable'
```

**This story's required input is a record containing human TP/FP judgements. There are none.**
13.2's AC7 is recorded `Unevaluable`, residual 31, filed as **`DF-13-2-A`** — a legitimate
pre-designed terminal escalation, ruled so by 13.2's code review, because the judgement is the
named human's act (`precision-validation-protocol.md` §2; adjudicator **XAgent007**, Engineering
Lead) and **no agent may supply it**.

**This is a locked project decision, not a gap.** `deferred-work.md` (the `DF-6-6-A` / `-P1` /
`-P2` / `DF-7-2-A` block, `target_story:` clause) states it in the ledger's own words:

> *"**NOT re-homed to 13.3: 13.3 computes over an adjudicated record and cannot begin without
> one.**"*

### The closure path, in three steps — step 3 is this story

1. **XAgent007 adjudicates the 31 blocking findings** TP/FP at each cited locator under protocol
   §4 as amended (V1.3, unit = the **finding**), and records the actual expert-hours.
   Human-readable worklist: `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/blocking-worklist.md`
   (24 `minions` + 7 `agent-smith`, all `vacuous_test_ast`).
2. **`scripts/build_adjudication_record.py` is re-run** to append the judged rows
   (append-only; a correction supersedes, never rewrites).
3. **THIS STORY computes the four §5 conditions** over that record and records the decision.

### If you are the dev agent and step 2 has NOT landed

Do **AC1, AC2, AC3, AC6, AC7 and AC8** in full — the decision instrument, both branches proven
against synthetic fixtures, the stale-figure corrections, the re-derived open-items list, the
ledger — and mark **AC4/AC5 (the decision itself) `BLOCKED — input absent`**, recorded with the
residual count and the closure path above, following the **Story 12.9 / AC9** and **Story 13.2 /
AC7** precedent where a halt is the *designed* terminal state and does not block the story's pass.

> **The one thing that must not happen.** Do **not** run the fold over the 31 `UNADJUDICATED`
> rows and record *"the gate did not clear"*. That sentence is TRUE and USELESS and
> **INDISTINGUISHABLE DOWNSTREAM** from an honest measured shortfall. It would let Epic 13
> terminate with a number nobody measured, on the one gate this whole plan exists to measure. An
> honest BLOCKED is a better outcome than a green story — and it is the outcome this file is
> designed to make easy.

---

## Acceptance Criteria

### AC1: THREE terminal states, never two — a vacuous run BLOCKS, it does not decide

**Given** the fold over the committed record today returns `evaluable=False` with residual 31
(reproduced verbatim above), and **provisional stays `True` even when the caller passes
`protocol_cleared=True`** — so a run today produces a defensible-looking "not cleared" that
rests on **zero** judgements

**Then** this story's first act is a **precondition check over the committed record**, and the
decision surface distinguishes **three** outcomes, each a distinct value in a **closed
vocabulary that RAISES on an unregistered member** (the `DF-10-4-E` exhaustive-dispatch shape,
as 12.5 / 12.8 / 13.2 already do):

| Outcome | When | Consequence |
|---|---|---|
| **`CLEARED`** | all four §5 conditions hold over an exhaustively adjudicated, byte-reproducible record | AC4 |
| **`NOT_CLEARED`** | the measurement **RAN** — reproducible **and** exhaustive **and** non-empty denominator — and **≥1 §5 condition FAILED** | AC5. **This is a result.** |
| **`BLOCKED`** | the record is not exhaustively adjudicated, or not reproducible, or the denominator is empty | **NOT a §5 outcome.** HALT the decision, record the residual + the closure path |

**And** `BLOCKED` may never be rendered, serialized, summarised or committed as *"the gate did
not clear"*, in any artifact, in any wording. **A shortfall and an absent measurement are
different claims** — `scripts/release_preflight.py:159`'s `Refusal` / `Unevaluable` / pass
three-outcome discipline is the precedent, reused rather than re-invented (13.2 / DN-5), and
`AdjudicationUnevaluable` is already a **type** so no call site can treat it as falsy by
forgetting to look.

**And** the check is **mechanical**: `record.determinism_precondition()` first (§4's last
bullet — *"before any pass/fail is recorded"*), then `record.exhaustiveness(...)`, then the
ratio. `fold_adjudicated_precision` already evaluates them in exactly that order — **call it,
do not re-implement it.**

**And non-vacuity is mandatory** (`AI-E11-1`, the `-39` argparse-internals precedent): the
decision producer asserts it extracted **> 0** rows and **> 0** expected finding ids before
asserting anything about them. *A decision function that silently folds an empty record returns
a confident answer forever, and here that answer is the externalization gate.*

### AC2: The four §5 conditions are computed AS WRITTEN — each one individually, each with its own evidence

**Given** `precision-validation-protocol.md` §5: *"**The gate is CLEARED iff ALL of:** precision
≥ 80% (exact Fraction) **AND** the clean-repo blocking-FP count is 0 **AND** N ≥ 5 **AND** this
protocol's adjudication run is recorded cleared."*

**Then** each is computed and reported **separately**, with its measured value and its verdict —
never as one boolean:

1. **Precision ≥ 80%** — the **exact `Fraction`** comparison `precision >= PRECISION_GATE_THRESHOLD`
   (`Fraction(4, 5)`). **No float, no rounding, no percentage literal** (AR4). Reuse
   `precision_fraction` / `PRECISION_GATE_THRESHOLD` / `gate_is_provisional` /
   `precision_gate_status_for` — the same objects both existing folds use (AR7; 13.2 / DN-2b).
   **Authoring a second threshold or a second arithmetic is the fork this codebase has refused
   three times.**
2. **0 clean-repo blocking false positives** — ⚠️ **protocol §5 as amended by 13.2 binds THIS
   STORY BY NAME:** *"Story 13.3 must therefore evaluate this condition against the cartridge
   corpus explicitly, or record it not-applicable — **it may not count it as met by default**."*
   Measured: over the repository corpus `clean_repo_fp_applicable` is **`False` by construction**
   (`_is_clean_repo` needs an empty golden key **AND** `max_blocking == 0`; no repository member
   has either). So either fold the **cartridge** corpus through `compute_precision` — which
   reports `clean_repo_fp_applicable=True` and **names the clean members it folded** — and carry
   that number, or record **NOT APPLICABLE with its reason**. **Counting it satisfied is the
   strongest available false green.**
3. **N ≥ 5** — from `validation_set_population_n()` → `tests/corpus/_manifest.eligible_member_count()`
   through the declared lazy edge. Measured **5**. **One floor** (`VALIDATION_SET_FLOOR_N`),
   never forked (13.1 / DN-3).
4. **The adjudication run is recorded cleared** — derived from the **committed record**, per the
   architecture §Enforcement *Adjudication-record enforcement* rule (added 2026-08-16 by 13.2):
   *"the >=80%-precision externalization gate may be cleared only from a COMMITTED, append-only,
   machine-readable adjudication record in which every emitted blocking finding carries exactly
   ONE LIVE disposition attributed to a human role §2 registers."* **Never from a caller's
   assertion.** ⚠️ Deriving it has a consequence that is AC4(d)'s whole subject — read it before
   you write the call.

**And** §7's **OI1 honesty invariants are NOT softened**, and nothing is adjusted post hoc.
**Any diff that moves `Fraction(4, 5)`, `VALIDATION_SET_FLOOR_N`, §5's table, or §7's bullets in
the loosening direction is a story failure regardless of the outcome** — including "clarifying"
the denominator, re-defining the unit (V1.3 locked it as the **FINDING**), or excluding a member
that judged badly. Prove it: `git diff` on `precision-validation-protocol.md` shows **additions
and strikes only**, and the §5 `N >= 5` and `>= 4/5` literals stay **byte-unchanged**.

### AC3: The decision is a COMMITTED, DERIVED, machine-readable record — no figure in it is hand-written

**Given** `DF-8-5-C`'s defect class — *a hand-written number in a proof artifact about the very
gate this epic measures* — and `AI-E9-7` (never publish a prose copy of a pinned constant)

**Then** a committed, machine-readable **gate-decision record** exists, carrying at minimum: the
**outcome** (AC1's closed vocabulary), **each of the four §5 conditions** with its measured value
and its individual verdict, the **corpus** it was computed over (member ids + pinned shas, from
the manifest — not typed), the **adjudication record** it folded (path + row count + protocol
version), the **protocol version** (asserted `==` change-log head), the **adjudicator**, the
**expert-hours report** (`expert_hours_report()` — a report, never a gate), the **commit sha**,
and the **date**.

**And** it goes through **`argus.store.canonical`** (`dumps_bytes` / `dumps`) — the one
serializer (AR4). Never `json.dumps`.

**And** it is a **committed repository artifact**, beside 13.1's and 13.2's under
`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/`. ⚠️ **`.gitignore:19` ignores
`.argus/`** — *gate evidence that is not in git is not evidence* (13.2 / DN-3). Assert it with
`git ls-files`, not with a path check: a path assertion passes for an ignored file
(`TC-ArgusAgent-PRECISION-001-40`'s precedent).

**And** `NFR-S1` holds absolutely: rule-id provenance, locators and counts only. **No source
byte, no secret value, no absolute host path, no drive letter, no backslash** — reuse
`adjudication.py`'s locator regex rather than writing a second one.

**And** the fold is **`fold_adjudicated_precision`**. Do not author a second fold, a second
precision function, or a second gate-status renderer. `precision_gate_status_for` is **extended,
never forked** (the 6.5 marker convention, held since Story 6.5).

### AC3b: The result DISCLOSES THE CONCENTRATION OF ITS OWN DENOMINATOR — in both branches

> **Added 2026-08-17 by the INTERIM Epic-13 retrospective (`AI-E13-5`), deliberately BEFORE the
> figure exists.** Recorded now because after adjudication any limitation attached to the result
> reads as an excuse if it fails and as goalpost-moving if it passes. **This changes no
> threshold.** §5's four conditions, the ≥80% `Fraction`, the `N ≥ 5` floor, the unit, the corpus
> definition and every §7 invariant are **untouched**, and the protocol is **NOT amended** — the
> change-log head stays **V1.3** so the committed adjudication record remains valid under
> `TC-ArgusAgent-PRECISION-001-45` and **no re-adjudication is forced**. This binds what the
> result must *say*, never what it must *reach*.

**Given** the denominator is concentrated, measured over the ratified corpus at `be35c7f`:
**24 of 31 blocking findings (77.4%) come from ONE member — `minions`**, which Story 13.1 itself
labels *the least transferable evidence* under its overfitting caveat; **7 of 31** come from
`agent-smith`; **ZERO** come from the remaining three ratified members, including the only real
multi-language test; and **31 of 31 are a single rule class** (`vacuous_test_ast`).

**Then** §5's `N ≥ 5` is satisfied by **member count** while the ratio is computed over **two
members and one detector**, and a bare precision figure would therefore overstate the breadth of
what was measured — the *N* that gates and the *N* that contributes are different numbers.

**Then** the gate-decision record of AC3 and **every surface that publishes the figure** carry a
**concentration statement** naming, at minimum: the **contributing member count vs. the ratified
member count**, the **per-member finding counts**, and the **distinct rule-class count** of the
adjudicated population. It is **DERIVED** — from the manifest and the adjudication record, through
`argus.store.canonical` — and **never typed**: this is `DF-8-5-C`'s defect class and `AI-E9-7`
applies with full force. The figures above are the state at authoring time and are **not** to be
pinned as literals.

**And it applies in BOTH branches.** If the gate CLEARS, the concentration rides with the cleared
status wherever AC4 writes it — a cleared gate measured over two members and one detector is
still measured over two members and one detector. If it does NOT clear, it rides with AC5's
shortfall report.

**And it is guarded in both directions** (the `-55b` convention): with the corpus as it stands the
guard must go **RED** if the statement is absent or contradicts the derived counts; and driven
over a synthetic well-distributed population the same predicate must **NOT** manufacture a
concentration claim. A caveat that cannot be absent is not an observation.

**And it is NOT a distribution requirement.** Do not amend §5 to require members to contribute, do
not drop or re-weight a member, and do not narrow the corpus to improve the ratio. The
concentration is **disclosed**, not corrected — correcting it by changing the population is the
threshold change AC5 forbids, wearing a different hat.

### AC4: IF CLEARED — the flip, and the guard that MUST NOT go vacuous at the moment it fires

Every clause below is conditional on AC1 returning **`CLEARED`**. If it returns `NOT_CLEARED` or
`BLOCKED`, **nothing in AC4 is performed** and that is recorded as the reason.

**(a) `protocol_cleared=True` is passed from a production `argus/**` call site**, and
`TC-ArgusAgent-DOCS-001-46` goes **RED**. *That red is the guard working* — the test says so in
its own docstring (`tests/test_instrument_disclosure.py:602-625`). It is answered by **REPLACING
the disclosure**, never by widening `_PROTOCOL_CLEARED_TEST_EXEMPTIONS` (which is a **test-side**
set and would not apply anyway).

**(b) `INSTRUMENT_STATUS` becomes `InstrumentStatus.VALIDATED`** and every surface renders the
cleared statement. The surfaces, **enumerated by measurement, not by memory** (the Story 10.2
precedent: a site list that named 4 of 7 and omitted FR7):

| Kind | Site | Action |
|---|---|---|
| **Render (single-sourced — no edit needed; ASSERT that, do not assume it)** | `argus/cli.py:844` · `argus/commands/installer.py:448` (short) · `argus/mcp/protocol.py:569` and `:603` · `argus/reports/generator.py:890` | all call `render_instrument_disclosure(INSTRUMENT_STATUS)`; flipping the constant propagates |
| **Static copy (MUST be edited)** | `README.md` (full) · `CHANGELOG.md` (full) · `pyproject.toml` `[project].description` (short) · `action.yml` `description:` (short) | `_DISCLOSURE_SURFACES`, `tests/test_instrument_disclosure.py:145-169` |
| **MCP** | `argus/__init__.py` · `argus/mcp/__init__.py` · `argus/mcp/protocol.py` · `argus/mcp/server.py` · `pyproject.toml` | `_MCP_DISCLOSURE_SURFACES`, `:198-204` |

**(c) ⚠️ MEASURED DEFECT IN THE CLEARED TEXT ITSELF — do not publish it as written.**
`INSTRUMENT_DISCLOSURE_VALIDATED` (`argus/verdict/negative_assurance.py:191-196`) says the gate
was measured *"over the **Argus dogfood corpus**"*. **That is the self-audit corpus 13.1
EXCLUDED from N** (`provenance: self`, `eligible_for_n: False`) — the one corpus that
structurally cannot clear this gate. Shipping it unchanged would state that the cleared gate
rests on the corpus that did not clear it: the **`DF-9-2-B` false-subject class** Story 11.5
corrected on the *other* member of this same two-member vocabulary. **The text must name the
corpus that actually cleared it** (the ratified validation set + the adjudication record + the
run). ⚠️ `TC-ArgusAgent-DOCS-001-58` (`tests/test_built_distribution.py:1163+`) asserts
`"Argus dogfood corpus" in text` for **BOTH** constants and **will go RED** — that red is a
**stale pin**, answered by correcting the guard to assert the real corpus, **never** by keeping
the false subject to keep a test green.

**(d) 🚨 THE VACUITY PROOF — this is the clause the tracker's *"a test asserting the guard has
not gone vacuous"* names, and it is the single highest-blast-radius item in the story.**

**Measured:** `protocol_cleared_call_sites` (`tests/test_instrument_disclosure.py:353-372`) is an
`ast` walk that records a site **only** when the keyword value `isinstance(value, ast.Constant)
and value.value is True` — i.e. **only a literal `True`**.

**Consequence, stated so it is not discovered after the fact:** if AC2(4) derives the flag —
`protocol_cleared=decision.adjudication_recorded_cleared`, which is the *correct* design and what
the architecture rule demands — then `protocol_cleared_call_sites` returns `()`,
`TC-ArgusAgent-DOCS-001-46` **STAYS GREEN WHILE THE GATE FLIPS**, and the one guard tying the
declared instrument status to the harness becomes vacuous **at the exact moment it matters**.
This project has recorded that class of defect eleven times in Epic 12 alone.

**Then**, in the cleared branch, a committed guard proves the observable **actually moves**:
either the production site passes the literal `True` (and `-46`'s production scan is asserted
**non-empty**), **or** the flip is derived by design and `-46`'s closure is extended to see a
derived flag — with the extension proven **RED at the real seam by the live flip**, not against
a reconstruction. Either way the story discharges the **GUARD-ADEQUACY CLAUSE** (architecture
§Enforcement, registered 2026-08-16 by 13.2 / AC8.4): **(i)** the observable is named, **(ii)**
the defect is demonstrated to move it at the real seam, **(iii)** ≥1 adversarial variant is
**GENERATED** from the record/registry it closes over, with its count, rather than hand-listed.
And its **input-side twin**: *a guard over the SHAPE of an input is not a guard over its EFFECT.*

**(e) The PRD is updated with the corpus and the run that cleared it — at sites found BY
CONTENT, never by line number.**

⚠️ **The tracker's and epic's `L118 / L130 / L141 / L302` are STALE.** Measured: they were
correct at **`f677e90` (2026-08-03)**; on HEAD they resolve to `## Executive Summary`,
`**Why now.**`, `## Project Classification` and a journey note. *A story that edits four line
numbers would edit four wrong lines.* **Live gate-status sites, measured on `411d891`
(re-measure — your own edits move them):**

| Line | Content anchor |
|---|---|
| **139** | *"APAA must hit ≥80% finding-precision before any **attested** externalization"* (the honesty keystone) |
| **159** | *"The one bar that gates attested externalization: ≥80% finding-precision."* + *"usage is not evidence"* |
| **176** | **"Attested-externalization gate … Current status (2026-08-10): NOT CLEARED"** ← the primary status site |
| **191 / 196** | Success-metric rows: finding precision ≥80% (GOVERNING) · validation set (already carries `N = 5`) |
| **223** | *"mandatory self-disclosure (FR34) while the ≥80% gate remains uncleared"* |
| **350** | risk row — *"the ≥80%-precision gate before any externalization"* |
| **373** | *"The ≥80% finding-precision bar on N ≈ 5–10 real repositories …"* ← the second status site |
| **438 / 445 / 454** | Tier B *"externalization-ready"* · the cut-order trade · *"an evidence-gated milestone, NOT a calendar deliverable"* |
| **475** | the `N`-for-the-validation-set open-question row (struck by 13.1) |
| **542-543** | **FR34's replace-never-delete clause** and *"Not a permanent state"* |

**Enumerate the set you actually change, and record the enumeration.** Per FR34 (`prd.md:542`)
the disclosure is **REPLACED by the cleared status, NEVER DELETED**: *"The surface never becomes
silent, and the enforcing test never becomes vacuous."*

**(f) `DF-12-7-B` is dispositioned.** Its `target_story` is **13.3** by name: an *installed*
command asset goes stale the moment `INSTRUMENT_STATUS` flips, and nothing tells the user. Close
it, or re-home it with a named owner and a reason (`AI-E9-8` forbids leaving an entry ownerless).

**(g) Clearing authorises ATTESTED externalization and NOTHING ELSE** — recorded at every site
that could be read as more. It does **not** by itself authorise commercial, enterprise,
regulated or operated-service use, each of which carries its own preconditions; and it is **not**
a publish act — `DF-12-9-A` stays OPEN and untouched, no tag, no push, no visibility change.

### AC5: IF NOT CLEARED — that IS the result, and the threshold does not move

**Given** protocol §5 and `epics.md` Story 13.3: *"**A failed measurement is not a reason to
amend the threshold** — it is the measurement working."*

**Then** the outcome is **recorded as the result**, and the record names, per failing condition:
its **measured value**, the **threshold it missed**, and **what would close it** in countable
terms (e.g. *"precision is 22/31; 3 further findings would have to be TP rather than FP, or the
corpus would need M additional adjudicated members"*) — derived, never estimated in prose.

**And the disclosure STAYS**, mechanically and provably: `INSTRUMENT_STATUS` is unchanged,
`protocol_cleared` is still never passed `True` from `argus/**`, `TC-ArgusAgent-DOCS-001-46` is
still **green**, and every surface in AC4(b) is **byte-unchanged**.

**And no threshold, floor, unit, corpus definition or §7 invariant is amended.** Do not narrow
the corpus, drop a member, re-classify a `verdict_eligible` flag, or reinterpret the unit. If the
outcome is uncomfortable, **that is what an honest gate feels like**.

### AC6: The PRD's MEASURED STATE is corrected in BOTH branches — strike, never erase

**Given** the corpus figure at two PRD sites is **stale on HEAD** and disagrees with a third:

| Site | Says | Measured on HEAD |
|---|---|---|
| `prd.md:176` | *"the corpus stands at **N=1** and is a self-audit"* | **N = 5**, independent repositories |
| `prd.md:373` | *"the eligible corpus is **`N = 0`**, measured"* | **N = 5** — this was true when 13.1's DN-1 was written and false by the end of the same day |
| `prd.md:196` | *"the operator RATIFIED five members … `N = 5` … the floor is MET"* | ✅ correct |

**Then** both stale sites are corrected against the **derived** count
(`eligible_member_count()` → 5), **never hand-typed**, struck-not-erased with the date and the
reason (§3.4), citing 13.1 / AC3b's ratification.

**And this happens in BOTH branches.** Correcting a stale measured figure is **not** weakening a
disclosure: in the `NOT_CLEARED` / `BLOCKED` branches the **NOT CLEARED status at those sites is
preserved verbatim** and only the *measured corpus state* moves. *A number that understates is
still a hand-written number in the document about the gate this epic measures —* `DF-8-5-C`'s
class, in prose, at the site that matters most.

**And** `TC-ArgusAgent-DOCS-001-75` (`tests/test_validation_set_decision.py:193+`) derives its
expectation from the manifest (`f"N = {live_n} eligible members" in prd or f"N = {live_n}" in
prd`). **Keep it derived.** If the correction makes it pass for a *new* reason, prove the guard
still moves — this exact guard is cited in the architecture's GUARD-ADEQUACY registration as
having *"REQUIRED a stale literal (`N = 0`) and so enforced a falsehood while staying green."*

### AC7: The open-items list is RE-DERIVED, not copied — a cleared gate is not plan closure

**Given** `epics.md` Story 13.3's fifth AC: *"this epic's retrospective states plainly what
remains open, rather than letting a cleared gate read as plan closure … **The retrospective
re-derives this list at the time it is written rather than copying it** — the point is that it
is measured, not that it matches this sentence."*

**Then** this story emits the **re-derived open-items list** as a committed input for the
retrospective, and **does not write the retrospective** (`epic-13-retrospective` is its own
sprint-status item).

⚠️ **Both halves of the AC's own example list are MEASURABLY STALE. Re-derive; do not copy
either — including from this table.**

| Claim as written | Measured on `411d891` |
|---|---|
| *"H0 is owned but H1–H4 are still NOT FILED"* (epics AC) | ✅ **H0 IS OWNED** — `epics.md:2642-2643` closed it 2026-08-10b via the pre-authorised **option (b)** (the operator files outside this workflow); `deferred-work.md:1575-1588` records the same, and `epics.md:30` frontmatter carries it. Story 10.5 **already** recorded a correction to a brief that said otherwise (`deferred-work.md:2203-2205`) |
| *"H0 (who FILES that handoff) is still **UNOWNED**"* — `sprint-status.yaml` header note | ❌ **STALE SURFACE.** That note is dated **2026-08-09** and **predates** the 2026-08-10b closure. **Do not propagate it.** Correct it or cite the closure beside it |
| the seven ledger ids the AC lists *"as of 2026-08-10b"* | ❌ **FOUR HAVE MOVED.** Measured id by id below |

**The seven ids, one per line — measured on `411d891`.** ⚠️ **Write each id's disposition on
its OWN line, here and in your Dev Agent Record.** `TC-ArgusAgent-DOCS-001-78`'s extractor
(`story_closure_claims`, `tests/test_governance_record_integrity.py:58-72`) is **line-scoped**
by design and documents the contract it relies on: *"a closure claim and its id are written on
the same line in every record this repository has produced."* A single line that pairs a closure
verb with an id whose disposition differs reads as a claim the ledger never received — and the
guard is **correct** to fail it.

| Ledger id | Measured on `411d891` |
|---|---|
| `DF-6-7-A` | ✅ **CLOSED** by disposition, 2026-08-11 (FR23) — the *invocation* half remains open under its own record |
| `DF-8-4-B` (bytes-example half) | ⛔ **remains open and unowned _by decision_** — `deferred-work.md:1649-1657`, a **locked disposition**. Do not schedule it, do not close it |
| `DF-8-4-C` | ⛔ **remains open and unowned _by decision_** — same locked disposition. Do not schedule it, do not close it |
| `DF-8-4-D` | ✅ **CLOSED** 2026-08-15 — an internal defect is now distinguishable from an expected degradation |
| `DF-8-5-B` | ♻️ recurs as the **artifact-currency bootstrap** (with `DF-10-4-D`), not as a pending item — see AC8.7 |
| `DF-8-5-C` | ✅ **CLOSED** 2026-08-16 against evidence — the generator no longer renders a literal |
| `DF-9-2-C` | ✅ **CLOSED** — already true on arrival; verified by measurement, no change made |

**And the substance the instruction protects — which is NOT stale and must be stated plainly:**
**H1–H4 are still NOT FILED**; **assumption A5 remains ⚠️ UNSUPPORTED**; **H3's
blocking-vs-advisory policy decision is unmade**; this repository's CI **cannot verify any of the
Minions integration**; and **CI evidence is NOT ESTABLISHED** for any Epic-10/-11/-12/-13 sha
(`audit-ci.yml`'s latest run covers `00c8d1b`, 2026-08-09). Plus whatever the re-derivation finds
open at the time it runs — including `DF-13-2-A` if the adjudication has still not happened.

**And one sentence, plainly:** *a cleared gate authorises attested externalization and is not
plan closure.* The epic-9 retrospective declared the plan FINAL once already and Epic 10 had to
reopen it. **Do not repeat that error.**

### AC8: Ledger, guards, gates and hand-off

1. **`deferred-work.md` is append-only** — `git diff --numstat` must be **`+n / -0`**.
2. In the **`BLOCKED`** terminal state, `DF-13-2-A` and `DF-6-6-A` / `-P1` / `-P2` / `DF-7-2-A`
   are **re-stated with what remains, never closed**, and a 13.3 entry is filed for the
   outstanding decision with a **named owner** (`AI-E9-8` — never `target_story: NONE` without
   one).
3. **Every `DF-*` closure this story's record claims must be backed by the ledger IN THE SAME
   COMMIT.** `TC-ArgusAgent-DOCS-001-78` — the `AI-E12-6` guard 13.2 landed — checks exactly
   this and **found 19 unbacked claims on its first run**, one of them in 13.2's own Completion
   Notes. Its `_UNBACKED_AT_LANDING` registry may only **SHRINK**: a listed entry that becomes
   backed **fails**.
4. **Every new guard satisfies the GUARD-ADEQUACY CLAUSE** (architecture §Enforcement) and **no
   guard is narrower than its AC** (`AI-E8-6`).
5. **NFR-M1 ≤ 1200 lines** on every touched file. Measured headroom — **three files are
   effectively full**: `tests/test_evidence_citation.py` **1199 (1 left)** ·
   `tests/test_built_distribution.py` **1198 (2 left)** · `tests/test_instrument_disclosure.py`
   **1194 (6 left)** · `tests/test_dogfood_proof.py` 1106 · `argus/cli.py` 1139 ·
   `argus/pipeline.py` 1111. **New guards go in a NEW module** (12.8's cohesion-split
   precedent). **Do not shave a file to fit**, and do not add an `_EXEMPT_BY_DESIGN` entry
   without a date, an owner and a `deferred-work.md` id.
6. **Nothing outward-facing** (`DF-12-9-A`, `AI-E12-2`): no tag, no push, no release, no
   visibility change — **re-asserted by execution at hand-off** (`git tag -l`, remote unmoved).
   ⚠️ `origin/master` is **13 commits behind** HEAD and that is correct; do not push.
7. **If `argus/**` moves, the `DF-8-5-B` / `DF-10-4-D` artifact-currency bootstrap applies**
   (`AI-E12-11`): commit the `argus/` delta → regenerate `minions-dogfood-proof.md`,
   `-partition-plan.md`, `-budget-plan.md` through their **own renderers** → commit the
   regeneration **separately**. Never edit a generated artifact by hand.

---

## Developer Context & Guardrails

### §0 — Premise re-measurement (this project's create-story control; eleven-for-eleven since Epic 11)

Measured **2026-08-17 on `411d891`** (HEAD), **by execution**. Per the Epic-11 retro §3.2
refinement and `AI-E12-10`, **confirmations are recorded as well as divergences.**
**Re-measure on your own baseline (Task 1)** — nothing here is inherited.

| Premise, as `epics.md` / `sprint-status.yaml` state it | Re-measured on `411d891` | Consequence |
|---|---|---|
| 13.1 and 13.2 are `done` | ✅ **HOLDS.** `sprint-status.yaml:415`/`:416`; both code-reviewed PASS | The sequential precondition on the *stories* is met |
| The adjudication record contains human judgements | ❌ **IT CONTAINS NONE.** 31 rows, **31 `UNADJUDICATED`**, `adjudicator: null` on every row, `expert_hours: null` | 🚨 **THE BLOCKING PREREQUISITE.** AC1 |
| *"13.3 computes the four §5 conditions"* | ✅ **HOLDS as the mandate** — and the ledger adds the precondition in its own words: *"NOT re-homed to 13.3: **13.3 computes over an adjudicated record and cannot begin without one**"* | **An absence here is a LOCKED DECISION, not a gap** |
| *"`protocol_cleared` … `replay_harness.py:223` — currently `False`, never set `True` to date"* | ⚠️ **TRUE IN SUBSTANCE, DRIFTED IN COORDINATE.** `compute_precision` is at **`:354`**; `protocol_cleared: bool = False` at **`:358`**. 13.1 said `:222`/`:226`; 13.2 confirmed the same drift | Same class the tracker keeps reproducing. **Never cite a line number you did not just measure** |
| `protocol_cleared` is never `True` from `argus/**` | ✅ **CONFIRMED.** Zero production call sites; `TC-ArgusAgent-DOCS-001-46` green; the test-side exemption set names **4** files | AC4(a)/(d) |
| §5's four conditions, measured today | **1 of 4 holds.** N=5 ≥ 5 ✅ · precision **UNEVALUABLE** ❌ · clean-repo FP **NOT APPLICABLE** over the repo corpus ❌ · adjudication run recorded cleared ❌ | AC2 |
| `fold_adjudicated_precision` exists and orders the §4 preconditions correctly | ✅ **CONFIRMED by execution.** determinism → exhaustiveness → ratio; `provisional` stays `True` even with `protocol_cleared=True` | **REUSE IT.** AC1/AC3 |
| The record's `protocol_version` equals the change-log head | ✅ **BOTH `V1.3`.** `change_log_head_version()` derives it; `TC-ArgusAgent-PRECISION-001-45` fails any mismatch | **Amending the protocol invalidates the record.** AC2 |
| `reproducibility_verified` (§4's NFR-P1 precondition) | ✅ **`True`**; 5/5 members byte-reproducible across two runs (13.1's existing check, carried onto the record) | `determinism_precondition()` → `None`. Do not add a second check |
| `INSTRUMENT_DISCLOSURE_VALIDATED` is ready to publish | ❌ **IT NAMES THE WRONG CORPUS** — *"over the **Argus dogfood corpus**"*, the self-audit 13.1 excluded from N (`eligible_for_n: False`) | 🚨 **AC4(c).** The `DF-9-2-B` false-subject class, on the other member of the same vocabulary |
| `TC-ArgusAgent-DOCS-001-46` will notice the flip | ❌ **NOT IF THE FLAG IS DERIVED.** `protocol_cleared_call_sites` matches only `ast.Constant` **`is True`** | 🚨 **AC4(d).** The guard goes vacuous exactly when it matters |
| PRD `L118/L130/L141/L302` are the gate-status sites | ❌ **STALE.** Correct at `f677e90` (2026-08-03); on HEAD → `## Executive Summary`, `**Why now.**`, `## Project Classification`, a journey note | 🚨 **AC4(e).** Find the sites **by content** |
| The PRD states the live corpus size | ❌ **TWO SITES DISAGREE WITH A THIRD.** `:176` *"N=1 … a self-audit"* · `:373` *"`N = 0`, measured"* · `:196` *"`N = 5` … floor is MET"* | 🚨 **AC6** |
| *"H0 is STILL UNOWNED"* (`sprint-status.yaml` header, 2026-08-09) | ❌ **FALSE ON THIS TREE.** H0 **CLOSED 2026-08-10b** via option (b) — `epics.md:30`, `:2642-2643`; `deferred-work.md:1575-1588`. Story 10.5 recorded the same correction already | **AC7.** The substance — **H1–H4 NOT FILED**, A5 UNSUPPORTED, H3 unmade — is unchanged and IS the point |
| The epic AC's seven `DF-*` ids are current | ❌ **FOUR HAVE MOVED** (see AC7's table) | **AC7 — re-derive** |
| `.argus/` is gitignored; `_bmad-output/` is tracked | ✅ **CONFIRMED.** `.gitignore:19` | AC3 — assert with `git ls-files` |
| Nothing has been published | ✅ **HOLDS.** `git tag -l` **empty**; `origin/master` = `bc55e36`, **13 behind** HEAD | AC8.6. **Do not push** |
| Baseline gates on `411d891` | ✅ **MEASURED BY EXECUTION.** `pytest` **1585 collected**, full run **exit 0** (0 failed / 0 error / 0 skipped) · `mypy argus` **clean, 84 source files** · `bandit -r argus` **19 Low / 0 Medium / 0 High** (confidence 0/6/13) | Report **deltas against these exact numbers**, never "all green". **A skip appearing is a regression signal** |
| Test-id high-water marks | Measured: `PRECISION-001-`**52** · `DOCS-001-`**79** · `DOGFOOD-001-`**55** · `RELEASE-001-`**30** · `HITL-001-`**31** · `CARTRIDGE-001-`**15** · `MAINT-001-`**05** | Continue from these: `PRECISION-001-53+`, `DOCS-001-80+`. **Opening a new area needs a recorded reason** |
| NFR-M1 headroom | `test_evidence_citation` **1199 (1 left)** · `test_built_distribution` **1198 (2)** · `test_instrument_disclosure` **1194 (6)** · `test_dogfood_proof` 1106 · `cli.py` 1139 · `pipeline.py` 1111 · `adjudication.py` 923 · `replay_harness.py` 786 · `negative_assurance.py` 579 | 🚨 **Three files are effectively full.** New guards go in a **NEW** module |
| A `project-context.md` exists | ❌ **NONE** (searched `**/project-context.md`) | `architecture.md`, `precision-validation-protocol.md`, the ledger and this file **are** the context |

### §0.1 — THE TWO WAYS THIS STORY CAN PRODUCE A FALSE RESULT

Both are reachable today. Both are the story's first job.

**(1) The vacuous decision.** Run the fold over the committed record right now and you get a
clean, confident, fully-green `provisional=True` / `"unevaluable"`. Write that down as *"the gate
did not clear"* and Epic 13 terminates with a **conclusion drawn from zero judgements**, in
wording no downstream reader can distinguish from a real measured shortfall. **The 31 rows say
`UNADJUDICATED` for a reason — 12.6 / DN-8: an `UNADJUDICATED` row that says so beats a `TP` row
that guessed, and a `BLOCKED` outcome that says so beats a `NOT_CLEARED` that inferred.**

**(2) The vacuous guard.** `-46` is the only mechanism connecting the *declared* instrument
status to the *computed* gate state (they are deliberately not coupled by import —
`negative_assurance.py:221-237` explains why). It closes over `protocol_cleared_call_sites`,
which sees **only a literal `True`**. Derive the flag — which is the right design — and the
guard silently stops seeing anything, forever, starting with the commit that flips the gate.
**Reproduce it before you fix it:**

```python
from tests.test_instrument_disclosure import protocol_cleared_call_sites
protocol_cleared_call_sites("f(x, protocol_cleared=True)")      # -> (1,)   seen
protocol_cleared_call_sites("f(x, protocol_cleared=decision.cleared)")  # -> ()   INVISIBLE
protocol_cleared_call_sites("f(x, protocol_cleared=bool(1))")   # -> ()   INVISIBLE
```

That is AC4(d)'s RED, and it is available **now**, in either branch.

### §0.2 — The guards that will go RED on you, and what each red means

| Guard | Trips when | The correct response |
|---|---|---|
| `TC-ArgusAgent-DOCS-001-46` (`test_instrument_disclosure.py:602`) | any `argus/**` call passes a **literal** `protocol_cleared=True`; or the test-side exemption set drifts **in either direction** | **CLEARED branch only.** *That red is the guard working* — REPLACE the disclosure with `InstrumentStatus.VALIDATED`'s text on every registered surface. **Never widen the exemptions.** In the other branches this must stay **GREEN** |
| `TC-ArgusAgent-DOCS-001-58` (`test_built_distribution.py:1163`) | either disclosure constant stops containing `"Argus dogfood corpus"` | **CLEARED branch.** A **stale pin**, not a defect in your change — correct the guard to assert the corpus that actually cleared the gate. See AC4(c) |
| `TC-ArgusAgent-DOCS-001-75` (`test_validation_set_decision.py:193`) | the PRD stops stating the **live derived** eligible-member count, or drops a required amendment marker | Correct the PRD **from the manifest**, never by typing a number. AC6 |
| `TC-ArgusAgent-PRECISION-001-45` | the record's `protocol_version` ≠ the protocol change-log head | You amended the protocol after the record was built. **Amend BEFORE, never during** (13.2 / AC2) |
| `TC-ArgusAgent-DOCS-001-78` (`test_governance_record_integrity.py`) | this story's record claims a `DF-*` closure the ledger never received; or `_UNBACKED_AT_LANDING` grows / a listed entry becomes backed | Back the claim **in the same commit**, or do not make it. AC8.3 |
| `TC-ArgusAgent-MAINT-001-01..-05` (`test_module_size_ceiling.py`) | any tracked `.py` crosses **1200** lines — it closes over `git ls-files`, so a file is swept the moment it is `git add`-ed | **Split for cohesion (12.8). Do not shave.** An exemption needs a reason, a date, an owner and a ledger id |
| `TC-ArgusAgent-RELEASE-001-11` (`test_release_preflight.py`) | a new `argus/**` module **names** the repository-only tree | Register it as a **deliberate** decision with the reason it is safe (13.2's precedent for `adjudication.py`) |
| `TC-ArgusAgent-DOGFOOD-001-03` (`test_dogfood_plan.py`) | total tracked `argus/` LOC moves and the committed partition plan cites the old figure | The `DF-8-5-B` / `DF-10-4-D` bootstrap. Commit → regenerate → commit separately. **Never edit the artifact** |

### §0.3 — THE INVENTORY: what exists to decide WITH

| Instrument | Lives at | State on `411d891` |
|---|---|---|
| The fold from human dispositions → precision | `argus/precision/adjudication.py:839` `fold_adjudicated_precision` | ✅ Exists, correct order, `AdjudicatedPrecision` return. **REUSE — do not fork** |
| Exhaustiveness (§4) with the non-vacuity floor | `adjudication.py:574` `AdjudicationRecord.exhaustiveness` | ✅ Exists. Returns `Exhaustive` \| `AdjudicationUnevaluable(residual_count, adjudicated_count, residual_finding_ids)` |
| Determinism precondition (§4 last bullet) | `adjudication.py:624` `determinism_precondition` | ✅ Exists, reuses 13.1's per-member check. **Do not add a second** |
| The shared arithmetic | `replay_harness.py:283` `PRECISION_GATE_THRESHOLD` · `:289` `precision_fraction` · `:308` `gate_is_provisional` | ✅ **One arithmetic, two populations** (AR7). Never a second threshold |
| The gate-status renderer (3 outcomes) | `replay_harness.py:704` `precision_gate_status_for` | ✅ `unevaluable` / `provisional` / `cleared`; **raises** on `(evaluable=False, provisional=False)` and on `(precision=None, provisional=False)`. **Extend, never fork** |
| N for the repository corpus | `adjudication.py:753` `validation_set_population_n()` → `_manifest.eligible_member_count()` | ✅ **5.** One floor (`VALIDATION_SET_FLOOR_N`), never forked |
| Clean-repo FP over the **cartridge** corpus | `replay_harness.py:354` `compute_precision` → `clean_repo_fp_applicable` + the named clean members | ✅ Exists. **This is where AC2(2) gets a real number, if it gets one** |
| Expert-hours report | `adjudication.py:764` `expert_hours_report` | ✅ A **report**, never a gate. `None` → *"NOT RECORDED"*, never `0` |
| Both corpora, measured | `replay_harness.py:626` `measure_validation_corpus` → `ValidationCorpusMeasurement.corpus_note()` | ✅ Every field read off the substrate. **Absence ≠ breakage**; only `ImportError` is absence |
| The canonical serializer | `argus/store/canonical.py` `dumps_bytes` / `dumps` | ✅ **The only serializer** (AR4). Never `json.dumps` |
| Disclosure vocabulary + render | `negative_assurance.py:124` `InstrumentStatus` · `:183`/`:191` the two texts · `:238` `INSTRUMENT_STATUS` · `render_instrument_disclosure` | ✅ Two members, exhaustive, **raises** on an unregistered one. ⚠️ The `VALIDATED` text names the **wrong corpus** — AC4(c) |
| The committed adjudication record | `…/validation-corpus/adjudication-record.json` | ⚠️ **31 rows, ZERO judgements.** The BLOCKING PREREQUISITE |
| Human dispositions | **nowhere** | ⛔ **XAgent007 supplies them. No agent may.** |
| **The gate-decision record** | **nowhere** | ⛔ **This story builds it** |

### Files to touch

**NEW** — decide repository-only vs. shipped **deliberately** and record the reason. `tests/` and
`_bmad-output/` are **absent from the built distribution** (`DF-9-2-A`); anything in `argus/**`
that reaches them must go behind the existing lazy edges and resolve **no path at module level**,
or the wheel cannot import — `tests/test_built_distribution.py` is the guard that catches it,
and only after a wheel is built.

| Path (indicative) | Purpose |
|---|---|
| the gate-decision module | AC1–AC3. Closed three-outcome vocabulary that **raises**; the four §5 conditions individually; calls `fold_adjudicated_precision`, never a second fold |
| the committed decision artifact | AC3. **In git**, beside 13.1/13.2's artifacts — `.argus/` is ignored (`.gitignore:19`) |
| a **NEW** guard module | AC1–AC4. 🚨 Must be new: `test_evidence_citation.py` **1199/1200**, `test_built_distribution.py` **1198/1200**, `test_instrument_disclosure.py` **1194/1200** |

**UPDATE — read each completely before editing.**

| Path (lines) | What it does today | What must be preserved |
|---|---|---|
| `argus/precision/adjudication.py` (923) | the record, the two §4 preconditions, the fold, the hours report | **Additive only**, defaults preserving today's behaviour (13.2 / DN-2). **277 lines of NFR-M1 headroom** — a large addition belongs in a new module |
| `argus/precision/replay_harness.py` (786) | the shared arithmetic + the 3-outcome renderer | **One arithmetic, one renderer.** `Fraction` only, never a float. `protocol_cleared` **never defaulted `True`** |
| `argus/verdict/negative_assurance.py` (579) | `InstrumentStatus` (2 members, exhaustive, raises) · the four disclosure constants · `INSTRUMENT_STATUS` | **CLEARED branch only.** The negation form, the two-member vocabulary and *"nothing else removes it"* are load-bearing; the `VALIDATED` **corpus name** is wrong and must change (AC4(c)) |
| `tests/test_instrument_disclosure.py` (1194 — **6 left**) | `-46`'s closure, the surface registries, `protocol_cleared_call_sites` | AC4(d) may need `-46`'s closure widened. **6 lines of headroom** — put the new guard in a new module and import the analyzer |
| `tests/test_built_distribution.py` (1198 — **2 left**) | `-58` pins both disclosure texts to *"Argus dogfood corpus"* | **CLEARED branch:** correct the pin. **2 lines of headroom** |
| `E-PRD/prd.md` (616) | the gate-status sites listed in AC4(e) | **Strike, never erase.** Sites found **by content**. `test_v1_commitment_closure.py` (1708, NFR-M1-exempt) and `test_spec_claim_scope.py` both close over this file — expect reds and read them |
| `precision-validation-protocol.md` (426) | §5 thresholds (`:305`) · §7 OI1 (`:397`) · the V1.3 change log (`:419`) | **§5 literals and §7 bullets byte-unchanged** unless the outcome is recorded there. Any amendment appends to the change log **and invalidates the record's version pin** (`PRECISION-001-45`) — so amend **before** the decision, or not at all |
| `_bmad-output/…/deferred-work.md` (4354) | append-only ledger | **`+n / -0`.** AC8.1–8.3 |
| `_bmad-output/…/architecture.md` (1372) | §Enforcement (`:944`) — the model form is *rule text + enforcing module + test ids*; **count the rules yourself, do not cite a number** | Register a 13.3 rule in **that exact form** if a new invariant lands. Strike, never delete |
| `README.md` · `CHANGELOG.md` · `pyproject.toml` · `action.yml` | the four static disclosure copies | **CLEARED branch only.** Compared against the constants by `-47`/`-48`/`-51` |

### Locked decisions this story must CITE rather than reopen

| Locked | Where | Consequence here |
|---|---|---|
| **13.3 computes over an ADJUDICATED record and cannot begin without one** | `deferred-work.md`, `DF-6-6-A`/`DF-7-2-A` block | **The BLOCKING PREREQUISITE. An absence is a locked decision, not a gap** |
| **No agent adjudicates; `UNADJUDICATED` is the only member an automated producer may write** | 13.2 / DN-6; protocol §2; `AdjudicationRow.__post_init__` | Never write a disposition. Not one |
| **The unit of adjudication is the FINDING, not the rule class** | protocol V1.3 / 13.2 DN-2a; §7 OI1 | 31 findings, 1 class. A per-class fold would gate on a denominator of **1** |
| **The PRD governs the corpus; cartridges are the RECALL instrument** | 13.1 / DN-1; `prd.md:191`/`:196`; protocol §5 (struck row) | Recall is **diagnostic only** and never gates |
| **One floor, two populations** — `VALIDATION_SET_FLOOR_N = 5`, never forked | 13.1 / DN-3 | AC2(3) |
| **One arithmetic, shared not forked** | 13.2 / DN-2b; AR7 | AC2(1) |
| **Precision is an exact `Fraction`, rendered `"num/den"`** | AR4; `_ratio_string` | No float, no rounding, no percentage literal |
| **`protocol_cleared` is passed by the harness CALLER, never defaulted** | `replay_harness.py:358` | AC4(a). And **only** in the cleared branch |
| **Three outcomes, `Unevaluable` is a TYPE not a flag** | 13.2 / DN-5; `release_preflight.py:159` | AC1 |
| **§3.4 evidence immutability — supersede, strike, never erase** | architecture §3.4; protocol §3.4 | Every document edit here |
| **Adjudication-record enforcement — the gate may be cleared ONLY from a committed record** | architecture §Enforcement (13.2 / AC3) | AC2(4) |
| **GUARD-ADEQUACY CLAUSE + its input-side twin** | architecture §Enforcement (13.2 / AC8.4) | Every new guard. AC4(d) |
| **Ledger-claim cross-check — a claimed closure the ledger never received fails CI** | architecture §Enforcement (13.2 / AC8.2) | AC8.3 |
| **`AI-E9-7` / single-source** — never publish a prose copy of a pinned constant | architecture §Enforcement | Every figure in every artifact is **derived** |
| **`AI-E9-8`** — never leave an entry without a named human | Epic-9 retro | AC8.2 |
| **`AI-E8-6`** — a guard narrower than its own AC is a breach | Epic-8 retro | AC8.4 |
| **`NFR-S1`** — no source or secret bytes in any artifact | architecture §G; the 4.3/4.4 CI-blocking canary suite | AC3 |
| **`DF-9-2-A`** — `tests/` and `_bmad-output/` are absent from the built distribution | `replay_harness.py:90-121` | Lazy edges only; no module-level path resolution |
| **`DF-10-4-E`** — an exhaustive dispatch RAISES on an unregistered member | 12.5 / 12.8 / 13.2 | AC1's outcome vocabulary |
| **Nothing outward-facing** | `DF-12-9-A`; `AI-E12-2` | AC8.6 |

### Decisions taken by this story (record each in the Dev Agent Record with its rejected alternative)

- **DN-1 — `BLOCKED` and `NOT_CLEARED` are different outcomes, and the vocabulary says so.**
  *Rejected alternative:* a boolean `cleared: bool`. It is the cheapest possible design and it
  **erases the distinction this entire epic exists to preserve** — a gate that did not clear
  because 31 findings were judged and 12 were false is a *measurement*; a gate that did not clear
  because nobody judged anything is an *absence*. One boolean cannot tell a reader which happened,
  and every downstream surface would inherit the ambiguity.
- **DN-2 — the decision is DERIVED from the committed record, never asserted by a caller.**
  Follows the architecture's Adjudication-record enforcement rule. *Rejected alternative:* a
  human-supplied `protocol_cleared=True` literal in production. Today *"the only thing standing
  between this repository and a false cleared claim is a human's decision not to pass that
  flag"* (13.2 / §0.1) — a derived flag removes that. ⚠️ **It also blinds `-46`; that is
  AC4(d), and it must be closed in the same change, not after it.**
- **DN-3 — the four §5 conditions are reported individually, each with its measured value.**
  *Rejected alternative:* a single conjunction. §5's clean-repo condition is currently NOT
  APPLICABLE over the gating corpus; a conjunction would swallow that fact into a `False` (or,
  worse, a vacuous `True`) and the protocol amendment 13.2 wrote **specifically forbids** counting
  it met by default.
- **DN-4 — the stale PRD corpus figures are corrected in BOTH branches.** *Rationale, recorded
  because it looks like scope:* the tracker's *"IF NOT CLEARED … the disclosure STAYS"* protects
  the **status**, not a **stale measurement**. `prd.md:176` (*N=1*) and `:373` (*N=0*) contradict
  `:196` (*N=5*) **on this tree, today**, in the document that carries the honesty keystone — the
  `DF-8-5-C` class in prose. Leaving them would be preserving a falsehood in the name of
  preserving a disclosure. **The NOT-CLEARED status text at those sites is preserved verbatim.**
  *Rejected alternative:* defer to a follow-up story — no story would own it, and `AI-E9-8`
  forbids an ownerless entry.
- **DN-5 — this story emits the retrospective's open-items list; it does not write the
  retrospective.** `epic-13-retrospective` is its own sprint-status item. *Rejected alternative:*
  writing the retro here — it would be the story grading its own epic, the shape this epic
  exists to delete.
- **DN-6 — no new third-party dependency.** The stdlib (`fractions`, `dataclasses`, `pathlib`,
  `hashlib`, `re`) plus what is already pinned and this project's own serializer. *Adding a
  dependency to the story whose entire subject is the credibility of a measurement is a decision
  that needs a recorded reason, not a convenience.*

### Toolchain and external facts, verified on this machine 2026-08-17

- HEAD **`411d891`**; `origin/master` **`bc55e36`**, **13 commits behind** (the Epic-13 delta is
  unpushed — correct, and not this story's business). `git tag -l` **empty**. Working tree
  carries six untracked non-source artifacts (`.bmad-drift-audit/`, `argusdemo/`,
  `bmad-dev-loop-pack/`, three `_bmad-output/audit-reports/` folders) — **`AI-E12-12` owns them;
  do not sweep them**, and never let one enter the corpus.
- Python **3.11** via `uv run --python 3.11`. Gates are **LOCAL** — `architecture.md` §H: a local
  run is necessary, never sufficient, and is labelled **LOCAL**.
- ⚠️ **CI evidence: NOT ESTABLISHED** for any Epic-10/-11/-12/-13 sha (`audit-ci.yml`'s latest
  run covers `00c8d1b`, 2026-08-09). Record it; it is not something this story can close.
- ⚠️ **Local gates are Windows-only here; CI runs an ubuntu matrix. A green local suite has
  already shipped POSIX-only bugs to master.** Everything this story writes must be
  **platform-neutral**: `pathlib` throughout, `encoding="utf-8"` explicit on every read,
  `newline="\n"` explicit on every write, `.as_posix()` at every path→string boundary, and no
  drive letter / backslash / absolute path / `..` in any recorded locator (reuse
  `adjudication.py:216`'s regex — it rejects all four at construction time). **No test may
  assert on `os.sep`, a Windows path, or a CRLF-sensitive byte count.**
- **The suite must not reach the network** (13.1 / DN-5, inherited).
- **No `project-context.md` exists** in this repository.

### Previous story intelligence — traps already paid for; do not pay again

From 13.1, 13.2 and Epics 10–12:

1. **The §0 re-measurement is not ceremony.** It has caught a materially wrong premise in every
   story since Epic 11. This time: two stale PRD corpus figures, four stale PRD line references,
   a stale `H0 UNOWNED` claim in the tracker header, four moved ledger ids, a cleared-disclosure
   text naming the wrong corpus, and a guard that goes blind on a derived flag. **Re-measure on
   your own baseline (Task 1)** — §0 was measured before you started.
2. **A hand-transcribed number drifts, every single time.** One file (`argus/pipeline.py`) has had
   **three different line counts** recorded across three documents. `replay_harness.py`'s
   `protocol_cleared` line has now drifted **twice** in three stories. **Derive every figure.**
3. **13.2 landed underneath the tracker's own text.** `replay_harness.py` went 391 → 786;
   test-id marks moved twice. Rebase onto what is there; never overwrite an amendment you did not
   make (§3.4 makes overwriting a **defect**, not a merge conflict).
4. **The artifact-currency bootstrap bites whenever `argus/**` moves** (`AI-E12-11`; ten of
   Epic 12's 28 commits, and again in 13.2). Commit the `argus/` delta → regenerate → commit the
   regeneration separately.
5. **Commit each story's delta as the story closes** (`AI-E10-7`). Do not implement into one
   dirty working tree.
6. **A story record that claims a ledger closure the ledger never received is the live defect
   class** — 13.2's own guard found **19**, including one in 13.2's own Completion Notes, which
   it corrected in place rather than quietly. Expect it to read *your* record too.
7. **The resumed-session integrity check** (`AI-E11-11` / `AI-E12-8`): if this session resumed
   after a transport error, re-derive state from the tree before continuing. A dev agent already
   died mid-story once and left a partially-applied change.
8. **12.6 / DN-7** — need a helper from a `_`-prefixed API? **Promote it to public**; never reach
   through. (`protocol_cleared_call_sites` is already public — use it, do not copy it.)
9. **12.6 / DN-8** — a false registry entry is worse than a coy one. Applied here: **a `BLOCKED`
   outcome that says so beats a `NOT_CLEARED` that inferred.**

### Testing requirements

- **Gates, all run locally before hand-off, all reported with ACTUAL numbers** (never "all
  green"): `pytest` full suite — baseline **1585 collected, exit 0, 0 failed / 0 error /
  0 skipped**; `mypy argus` — **clean, 84 source files**; `bandit -r argus` — **19 Low /
  0 Medium / 0 High**. Label them **LOCAL** and record that **CI evidence is NOT ESTABLISHED**.
  **A skip appearing is a regression signal.**
- **Test ids continue from the measured marks:** `PRECISION-001-53+`, `DOCS-001-80+`,
  `DOGFOOD-001-56+`, `RELEASE-001-31+`. Opening a new area needs a recorded reason.
- **RED-then-green is mandatory evidence, at the REAL SEAM** (`AI-E11-1` clause ii). For each new
  guard capture in the Debug Log: the observable, the planted or live defect, the RED output, the
  fix, the GREEN output. Specifically —
  - **AC1**: fold the *live* record (31 `UNADJUDICATED`) → the outcome must be **`BLOCKED`**, and
    a synthetic fully-adjudicated fixture must give `CLEARED` / `NOT_CLEARED` as its numbers
    dictate. **Generate** the adversarial variants **from the committed record** (remove one
    disposition; make one `BORDERLINE`; set `reproducibility_verified=False`; empty the expected
    population) — not hand-written. 13.2 proved each of these seams already: reuse its fixtures
    rather than inventing parallel ones.
  - **AC2**: a `Fraction`-vs-float divergence must be **demonstrated** (e.g. a ratio that passes
    as a float and fails as a `Fraction`, or vice versa) — not asserted.
  - **AC4(d)**: the §0.1 (2) snippet is your RED and it is available **now, in either branch**.
    It must go from *"guard sees nothing"* to *"guard sees the flip"*.
  - **AC5/AC6**: a fixture whose numbers fall short must produce a `NOT_CLEARED` record naming
    the failing condition **and what would close it**, with the disclosure surfaces asserted
    **byte-unchanged**.
- **Non-vacuity is mandatory on every guard that walks a record or a document**: assert it
  extracted **> 0** items before asserting anything about them (the `-39` precedent). *A guard
  that silently iterates an empty gate-decision record passes forever, and here that guard is the
  one protecting the externalization gate.*
- **Determinism**: reuse `determinism_precondition()` / 13.1's per-member check. **Never a second
  reproducibility check.**
- **Platform neutrality**: every new test must pass on ubuntu. No `os.sep`, no drive letter, no
  CRLF-sensitive byte count, no `Path` compared to a hand-built string.

---

## Tasks & Subtasks

- [x] **Task 0 — Confirm the precondition, by execution (AC: 1)**
  - [x] Load the committed record; report `counts()`, `len(rows)`, the adjudicator set, `expert_hours`
  - [x] Assert `protocol_version == change_log_head_version(protocol_text)`
  - [x] Run `fold_adjudicated_precision` and record `evaluable`, `exhaustiveness`, `determinism`
  - [x] **Decide the terminal state NOW and record it**: `CLEARED` / `NOT_CLEARED` / `BLOCKED`.
        If `BLOCKED`, AC4 and AC5 are not performed and the reason is recorded — **do not
        compute a decision anyway**
- [x] **Task 1 — Re-measure every §0 / §0.1 / §0.3 premise on YOUR baseline (AC: all)**
  - [x] Re-run the §0.1 reproductions; record actual output in Debug Log §1
  - [x] Re-measure every cited line number before citing it; record confirmations *and* divergences
- [x] **Task 2 — Build the decision instrument (AC1, AC2, AC3)**
  - [x] Closed three-outcome vocabulary that **raises** on an unregistered member
  - [x] The four §5 conditions computed individually, each with its measured value and verdict
  - [x] Clean-repo FP: fold the **cartridge** corpus explicitly, or record NOT APPLICABLE with its
        reason — **never count it met by default** (protocol §5 names 13.3 by name)
  - [x] Fold via `fold_adjudicated_precision`; arithmetic via the shared objects. **No second fold**
  - [x] Non-vacuity floor asserted **first**, before any other assertion
- [x] **Task 3 — Commit the gate-decision record (AC3)**
  - [x] Every field derived; nothing hand-typed; `argus.store.canonical` only
  - [x] In git (**not** `.argus/`); asserted with `git ls-files`, not a path check
  - [x] NFR-S1: locators + counts + rule-id provenance only; reuse the locator regex
- [ ] **Task 4 — NOT PERFORMED. The branch did not fire** — Task 0 returned **`BLOCKED`**, and AC4's
      own first line makes every clause below conditional on `CLEARED`. Left unchecked deliberately:
      checking it would claim work that must not have happened.
  - [ ] Pass `protocol_cleared` from a production `argus/**` site; expect `-46` RED
  - [ ] Flip `INSTRUMENT_STATUS`; edit the four static surfaces; **assert** the five render sites
        need no edit rather than assuming it
  - [ ] **Correct `INSTRUMENT_DISCLOSURE_VALIDATED`'s corpus name**; answer `-58`'s red by
        correcting the pin, never by keeping the false subject
  - [ ] **Prove `-46` is not vacuous** with the flip in place — the story's highest-risk clause
  - [ ] Update the PRD gate-status sites **found by content**; enumerate what you changed
  - [ ] Disposition `DF-12-7-B`; record that clearing authorises **attested externalization only**
- [ ] **Task 5 — NOT PERFORMED. The branch did not fire** — Task 0 returned **`BLOCKED`**, not
      `NOT_CLEARED`. ⚠️ Its three subtasks were nevertheless DISCHARGED where they apply to every
      non-cleared branch, and the evidence is in the Debug Log: the failing/unevaluable conditions
      are recorded with their measured values and their countable closure paths on the committed
      decision record; `-46` is green and `protocol_cleared` is still never passed `True` from
      `argus/**`; the four static disclosure surfaces are byte-unchanged; and `git diff` shows the
      protocol document **untouched**, so the §5 literals are byte-unchanged by construction.
  - [ ] Record which conditions failed, their measured values, and what would close each
  - [ ] Prove the disclosure stayed: `-46` green, `protocol_cleared` still never `True`, the four
        static surfaces **byte-unchanged**
  - [ ] **Prove no threshold moved**: `git diff` on the protocol shows additions/strikes only and
        the §5 literals are byte-unchanged
- [x] **Task 6 — Correct the stale PRD corpus figures (AC6) — in EVERY branch**
  - [x] `prd.md:176` (*N=1*) and `:373` (*N=0*) corrected from the derived count; strike, never erase
  - [x] The NOT-CLEARED status text at those sites preserved verbatim unless Task 4 fired
  - [x] `TC-ArgusAgent-DOCS-001-75` stays **derived**; prove it still moves
- [x] **Task 7 — Emit the re-derived open-items list (AC7)**
  - [x] **Re-derive** H0/H1–H4, A5, H3 and every open `DF-*` from the tree — **do not copy** the
        epic AC's list, the tracker header, or §0's table
  - [x] Record the two measured corrections: H0 **is owned**; four of the seven listed ids **moved**
  - [x] One sentence: a cleared gate authorises attested externalization and **is not plan closure**
  - [x] Do **not** write the retrospective
- [x] **Task 8 — Ledger and documents (AC8)**
  - [x] `deferred-work.md` `+n / -0`; every claimed closure backed **in the same commit**
  - [x] In `BLOCKED`: re-state `DF-13-2-A` / `DF-6-6-A`* / `DF-7-2-A` with what remains; file the
        13.3 entry with a **named owner**
  - [x] Register any new invariant in architecture §Enforcement in the model form
- [x] **Task 9 — Gates and hand-off**
  - [x] `pytest` / `mypy` / `bandit` with **actual numbers**, labelled **LOCAL**; CI **NOT ESTABLISHED**
  - [x] NFR-M1 re-measured on every touched file (**three are effectively full**)
  - [x] If `argus/**` moved: commit → regenerate the three dogfood artifacts → commit separately
  - [x] Nothing outward-facing; re-assert by execution (`git tag -l`, remote unmoved). **Do not push**

---

## ⛔ ESCALATION — the input this story cannot give itself

**AC1, AC2, AC3, AC6, AC7 and AC8 are fully autonomous. AC4 and AC5 are gated on an input that
does not exist**, and the boundary is the reason Epic 13 exists.

The gap is **one bounded, explicit act by a named person**, not an open-ended block:

1. **XAgent007 adjudicates the 31 blocking findings** TP/FP at each cited locator under protocol
   §4 as amended (V1.3, unit = the **finding**). Worklist: `validation-corpus/blocking-worklist.md`.
2. **Records the actual expert-hours** (protocol §3's ≤4h is a **ceiling, not a target**; an
   overrun is *recorded, not failed*).
3. **A QA-Lead second and/or external tie-break** only if a borderline finding requires one (§4)
   — both roles are unfilled, and filling them is itself an operator act.
4. **`scripts/build_adjudication_record.py` is re-run** to append the judged rows.

Then this story runs to completion and the arithmetic decides.

> **The one thing that must not happen.** Do not invent a disposition. Do not infer one from a
> rule id, a locator, a detector's confidence, or a prior story's prose. Do not let a model
> "pre-classify for the human to confirm". **And do not fold the unadjudicated record and write
> down "the gate did not clear"** — that is the same falsehood wearing the clothes of a result.
> A fabricated or vacuous decision would settle the externalization gate on evidence that does
> not exist, and every guard downstream would agree that it had. **`BLOCKED`, recorded with its
> residual count and its closure path, is the correct and complete answer to a question nobody
> has answered yet.**

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context), via the BMAD `dev-story` workflow.

### Debug Log

**§1 — Task 0/1: every §0 premise re-measured BY EXECUTION on this baseline (`6c59115`).**
Confirmations *and* divergences, per `AI-E12-10`. **Six premises had moved since the story
was contexted on `411d891`, and one of them changes the outcome.**

| Premise, as the story file records it | Re-measured on `6c59115` | Consequence |
|---|---|---|
| The adjudication record contains **no** judgements (31 `UNADJUDICATED`) | ❌ **SUPERSEDED.** `counts() = {'TP': 0, 'FP': 26, 'BORDERLINE': 5, 'UNADJUDICATED': 0}`; adjudicator `XAgent007 (Engineering Lead)` on all 31 rows, `adjudicated_on: 2026-08-17` | ⛔ The BLOCKING PREREQUISITE is **discharged**. The judgement exists |
| `expert_hours` is `null` | ✅ **HOLDS** — still `null`, and left null. §3 treats it as a report, never a gate | No figure was invented |
| `protocol_version == change_log_head_version()` | ✅ **BOTH `V1.3`** | The record's pin holds; the protocol was not amended |
| `reproducibility_verified` | ✅ **`True`**; `determinism_precondition()` → `None` | §4's first precondition passes |
| `validation_set_population_n()` / floor | ✅ **5 / 5** | §5's floor condition MET |
| The fold over the live record is **EVALUABLE** with denominator 26 *(asserted by the orchestrator's spawn brief, not by the story file)* | ❌ **FALSE, MEASURED.** `fold.evaluable is False`; `exhaustiveness` → `AdjudicationUnevaluable(residual_count=5, adjudicated_count=26)` | 🚨 **The outcome is `BLOCKED`, not `NOT_CLEARED`.** See §2 |
| `protocol_cleared` never `True` from `argus/**` | ✅ **CONFIRMED.** Production scan empty, before and after this story | AC5 |
| `TC-ArgusAgent-DOCS-001-46` will notice a derived flip | ❌ **CONFIRMED BLIND** — reproduced verbatim, §3 below | `DF-13-3-B` |
| PRD `:176` *"N=1 … a self-audit"* and `:373` *"`N = 0`, measured"* | ❌ **BOTH STALE**, contradicting `:196`'s `N = 5` on the same tree | AC6, corrected |
| *"H0 is STILL UNOWNED"* (`sprint-status.yaml` header, 2026-08-09) | ❌ **STALE**, superseded 2026-08-10b | AC7, corrected beside it |
| **CI evidence NOT ESTABLISHED for any Epic-10/-11/-12/-13 sha** | ❌ **STALE.** `gh run list --workflow=audit-ci.yml`: **success** on `c027e16`, `be35c7f`, `b04dc1a`, `bc55e36`; **failure** on `ae54234` | ⚠️ Still NOT established for the adjudication commit or this delta — see §7 |
| `origin/master` is `bc55e36`, 13 commits behind | ❌ **MOVED** — `origin/master` is now `c027e16`. Someone pushed between contexting and this run. **Not this story's business and not reverted**; `git tag -l` is still empty and this story pushed nothing | AC8.6 |
| Baseline gates | ✅ `pytest` **1585 collected**, **3 FAILED** (`PRECISION-001-39` / `-47` / `-52`) · `mypy` clean **84** files · `bandit` **19 Low / 0 Med / 0 High** | The three reds are AC4/AC5 work, §4 |
| Three test files effectively full | ✅ **CONFIRMED** — 1199 / 1198 / 1194 of 1200 | New guards went in a NEW module |

---

**§2 — Task 0: the terminal state, decided by execution and NOT by preference.**

The fold over the committed record, run before anything was written:

```
counts()      {'TP': 0, 'FP': 26, 'BORDERLINE': 5, 'UNADJUDICATED': 0}
determinism   None                              (§4 precondition 1: SATISFIED)
exhaustiveness UNEVALUABLE — 5 of 31 emitted finding(s) carry no live TP/FP disposition
evaluable     False
precision     None      precision_ratio 'NOT COMPUTED BY THIS RUN'
```

⚠️ **The spawn brief directed `NOT_CLEARED` on the premise that "the denominator is 26
(non-zero), so the fold is EVALUABLE". The premise is false as measured**, and the
divergence is recorded rather than adopted. `AdjudicatedPrecision.evaluable` is the
conjunction of **three** conditions — reproducible **AND** exhaustive **AND** non-empty
denominator — and only the first and third hold. AC1's own table makes *"the record is not
exhaustively adjudicated"* a **`BLOCKED`** condition **by name**, and protocol §4 says it
in its own text: `BORDERLINE` *"makes the run non-exhaustive until it resolves"*. §4's
ladder — locator re-examination → golden-key correction → **external tie-break** — has not
terminated for 5 findings, and §2 records the QA-Lead and external-adjudicator seats as
**unfilled**.

Recording `NOT_CLEARED` would have published a **measured shortfall** over an adjudication
nobody finished — §0.1(1)'s falsehood, in the direction the story did not anticipate. The
outcome is **`BLOCKED`**, and Tasks 4 and 5 were therefore not performed.

**What is recorded ANYWAY, because a reader is owed it, and recorded as a BOUND and not as
a decision:** over **every** admissible completion of the 5 residual the threshold is
unreachable — all five as TP gives **5/31**, below **4/5**. `ResidualCompletionBound`
carries it, in exact `Fraction` arithmetic through the shared `precision_fraction`, and
`TC-ArgusAgent-PRECISION-001-60` pins the one thing that must never follow from it: an
unreachable threshold does **not** promote `BLOCKED` to `NOT_CLEARED`.

---

**§3 — RED-then-GREEN, at the real seam, per guard.**

**(a) `§0.1 (2)` — the AC4(d) blind spot, reproduced verbatim on this tree:**

```
protocol_cleared_call_sites("f(x, protocol_cleared=True)")             -> (1,)   seen
protocol_cleared_call_sites("f(x, protocol_cleared=decision.cleared)") -> ()     INVISIBLE
protocol_cleared_call_sites("f(x, protocol_cleared=bool(1))")          -> ()     INVISIBLE
protocol_cleared_call_sites("f(x, protocol_cleared=False)")            -> ()     (correctly)
```

**RED confirmed.** It is **not fixed here** — AC4(d) assigns the fix to the CLEARED branch,
which did not fire, and extending `-46`'s closure without a live flip to prove it RED
against would be a fix proven against a reconstruction, which the GUARD-ADEQUACY clause
explicitly refuses. **What this story did instead is refuse to open the hole:**
`decide_gate` computes `adjudication_run_recorded_cleared` from the committed record — as
the architecture's Adjudication-record enforcement rule demands — and then passes the
**literal `False`** into the fold. Filed as **`DF-13-3-B`**, owner XAgent007, target: the
story that performs the flip, **in the same change**.

**(b) `TC-ArgusAgent-PRECISION-001-58` — every outcome REACHED, variants GENERATED from the
committed record.** RED first in every case; the first run failed on `missing_one`
returning `CLEARED`, which was the guard finding a real defect in its own fixture:
appending a superseding row to 30 of 31 rows no longer leaves a residual now that row 0
carries a committed `FP`. Corrected to drop the finding's rows entirely while leaving it in
the expected population — **which is the real seam**, and the reason the producer derives
the expected population from `adjudication-set.json` rather than from the record. The same
defect was present in `-47` and was corrected there too.

**(c) `TC-ArgusAgent-PRECISION-001-57` — the `Fraction`-vs-float divergence, DEMONSTRATED
not asserted.** The first attempt searched for a divergent `n/d >= 0.8` pair and found
none in range — recorded as a RED, because a guard asserting a property it never observed
is the defect this project files. The real divergences were then demonstrated, both of them
exactly what AR4 bans: `Fraction(4, 5) >= 0.8` is **`False`** (the double nearest 0.8 is
strictly greater than 4/5, so a float threshold **refuses a measured precision of exactly
80%** — a false RED at the boundary); and `round(100 * 199 / 250) >= 80` is **`True`** while
`Fraction(199, 250) < Fraction(4, 5)` — a false GREEN from a rounded percentage literal. The
divergent pair is **searched for**, not hand-picked, so the guard survives a legitimate
threshold move.

**(d) `TC-ArgusAgent-PRECISION-001-59` — the concentration disclosure, guarded in BOTH
directions** (the `-55b` convention). Over the live corpus the predicate fires and the
derived counts are compared against an independent count taken in the test. Driven over a
**synthetic well-distributed** population — every ratified member, three rule classes — it
must **not** fire, and it does not. *A caveat that cannot be absent is not an observation.*
Not one of the story's authoring-time figures (24 / 7 / 0 / single class) appears as a
literal anywhere in the module or the guard (`DF-8-5-C` / `AI-E9-7`).

**(e) `TC-ArgusAgent-PRECISION-001-64` — a true status carrying a FALSE reason, found by
execution.** `precision_gate_status_for`'s unevaluable branch rendered *"precision
DENOMINATOR EMPTY — no finding entered TP+FP over this population"* **beside a denominator
of 26**. That was the only way to be unevaluable when 13.2 wrote it, and it stopped being
true the moment a human recorded a `BORDERLINE`. `DF-9-2-B`'s false-subject class, on the
surface that publishes the externalization gate. Fixed **additively**: `unevaluable_reason`
defaults to the exact prior wording (asserted, so every pre-13.3 caller's bytes are
unmoved — NFR-P1), and the fold now supplies the precondition that actually failed.

**(f) `TC-ArgusAgent-PRECISION-001-39` / `-47` / `-52` — the three reds inherited from the
adjudication commit.** All three asserted `total_unadjudicated == len(record.rows) == 31`.
13.2 encoded *"nothing is adjudicated yet"* as a permanent invariant when it was a
**transient state**, so all three failed on the exact event they existed to wait for. Each
was **re-derived, not deleted and not trivially satisfied**, and each is still able to fail:
`-39` now asserts the attribution partition in both directions (a human disposition carries
a §2-registered adjudicator and a date; an `UNADJUDICATED` row carries neither); `-47`
computes the expected residual set independently and requires `exhaustiveness` to agree with
it, in both directions; `-52` derives the residual from the record's own live dispositions,
keeps the load-bearing claim (`protocol_cleared=True` from a caller cannot flip a
non-exhaustive record), adds a reconciliation between the denominator and the adjudicated
count, and **fails loudly with a re-derivation instruction** if its subject ever vanishes.

---

**§4 — AC2, condition by condition, each with its own evidence.**

1. **precision ≥ 80%** — **UNEVALUABLE.** No ratio was computed, because §4's exhaustiveness
   precondition does not hold. The comparison, when it happens, is the exact `Fraction`
   `precision >= PRECISION_GATE_THRESHOLD`; no float, no rounding, no percentage literal.
2. **clean-repo blocking FP == 0** — **MET**, and **measured**, not assumed. Protocol §5 as
   amended names Story 13.3 by name and forbids counting it met by default, so
   `scripts/build_gate_decision.py` stages and audits **every** cartridge through the
   unmodified pipeline and folds the result through `compute_precision`, which reports
   `clean_repo_fp_applicable=True` and **names the clean members it folded**: `clean_control`
   and `tool_breadth`, **0** blocking false positives. The repository corpus's NOT-APPLICABLE
   reason is carried alongside on `CleanRepoEvidence.note`, so both populations are visible.
3. **N ≥ 5** — **MET.** `validation_set_population_n()` → `eligible_member_count()` = **5**,
   floor `VALIDATION_SET_FLOOR_N` = **5**. One floor, never forked.
4. **the adjudication run is recorded cleared** — **FAILED**, derived from the committed
   record and never from a caller: the record is git-tracked ✅, byte-reproducible ✅, every
   live judgement attributed to a §2-registered role ✅, **exhaustive ❌**.

`GateDecision.__post_init__` refuses to construct a `CLEARED` decision carrying any non-`MET`
condition — §5's *"it may not count it as met by default"* made unexpressible.

---

**§5 — AC5's obligations, discharged where they apply to every non-cleared branch.**

- **The disclosure STAYED, mechanically.** `git diff` over `argus/verdict/negative_assurance.py`,
  `pyproject.toml` and `action.yml` is **empty**; `README.md`'s disclosure paragraph is
  untouched (see §7); `INSTRUMENT_STATUS` is unchanged; the `argus/**` production scan for
  `protocol_cleared=True` is **empty**; `TC-ArgusAgent-DOCS-001-46` is green.
  `TC-ArgusAgent-PRECISION-001-62` now ties the declared status to the **committed decision**
  and moves in both directions.
- **No threshold moved, in either direction.** `git diff` over
  `precision-validation-protocol.md` is **empty** — the document was not touched at all, so
  §5's literals and §7's OI1 bullets are byte-unchanged by construction, and the change-log
  head is still **V1.3**, so the record's `protocol_version` pin holds and no re-adjudication
  was forced. `TC-ArgusAgent-PRECISION-001-63` asserts the document and the shipped constants
  against each other so a future drift on either side goes red.
- **The corpus was not narrowed, no member was dropped or re-weighted, no
  `verdict_eligible` flag was re-classified, and the unit is still the FINDING.**

---

**§6 — Gates, LOCAL, with actual numbers.** ⚠️ `architecture.md` §H: a local run is
necessary and **never sufficient**. These ran on **Windows only**; CI runs an ubuntu matrix.

| Gate | Baseline (`6c59115`) | This delta | Δ |
|---|---|---|---|
| `pytest` | 1585 collected, **3 failed**, 0 skipped | **1597 collected, 1596 passed, 1 failed, 0 skipped** | +12 tests; the 3 inherited reds fixed; **1 remaining red, named in §7** |
| `mypy argus` | clean, 84 source files | **clean, 86 source files** | +2 modules |
| `bandit -r argus` | 19 Low / 0 Med / 0 High | **19 Low / 0 Med / 0 High** | unchanged |
| NFR-M1 | 3 files at 1199 / 1198 / 1194 | `gate_decision` **851** · `gate_disclosure` **341** · `replay_harness` **825** · `adjudication` **952** · `test_gate_decision` **900** · `test_adjudication_record` **859** · `build_gate_decision` **318** | all under 1200; no file shaved |

**No skip appeared** — the story names a skip as a regression signal, and there is none.

---

**§7 — ⚠️ ONE RED REMAINS, and it is NOT fixed, deliberately.**

`TC-ArgusAgent-DOCS-001-54` (`tests/test_built_distribution.py`) fails:

```
README.md publishes a stale figure for 'wheel_entries': it says 92,
the freshly built artifact measures 94. Fix the document — the artifact is the fact.
```

`README.md` also states `argus_agent-0.1.0.tar.gz`, **91 files**, which the artifact now
measures at **93**. Both figures moved because this story added two modules to `argus/**`,
so the staleness is **this story's doing**, not the operator's.

**It was not fixed because `README.md` carries an UNCOMMITTED external edit made outside
this workflow** — measured: **+122 / −404**, a substantial rewrite that removes several
§3.4 struck-not-erased corrections. This session was instructed not to touch, stage, commit,
revert or regenerate that file, and it did none of those. `README.md` is the **only** file in
the working tree left unstaged and uncommitted, exactly as it was found.

**The remedy is two tokens, in one paragraph, at `README.md:83`:**
`…py3-none-any.whl\`, 92 entries)` → **94**, and `…tar.gz\`, 91 files)` → **93**. The
paragraph is *"the one place this README states those two numbers"* by its own text, so
nothing else needs to move, and the disclosure paragraph is not involved.

**Owner: XAgent007 (Engineering Lead)** — it is one edit inside a file only the operator can
safely reconcile, and it is FILED as `DF-13-3-C` so it is not carried only in this story's
prose. Recorded rather than worked around, because silently editing an operator's unreviewed
rewrite to make a gate green is the precise instinct this story exists to refuse — and it
would have mixed an agent's change into a diff nobody has read yet.

---

**§8 — Not done, and why (recorded rather than silently skipped).**

- **AC4 (a)–(g): NOT PERFORMED.** Every clause is conditional on `CLEARED`. `DF-12-7-B` is
  therefore not dispositioned: nothing about an installed command asset went stale, and there
  is nothing to rule against. `INSTRUMENT_DISCLOSURE_VALIDATED`'s wrong-corpus defect
  (AC4(c)) is **real and confirmed on this tree** and is left standing with the constant
  itself unpublished — correcting the text of an unused constant, and re-pinning
  `TC-ArgusAgent-DOCS-001-58` to match, would land a change nobody can prove RED at the real
  seam until the flip happens.
- **The retrospective was NOT written** (DN-5). `epic-13-open-items.md` is its committed
  **input**; `epic-13-retrospective` remains its own sprint-status item and still needs a
  FINAL pass.
- **`evidence_deviation` on the adjudication record: a measured divergence, recorded not
  fixed.** All 7 `agent-smith` row reasons say *"see `evidence_deviation` on this record"* and
  **the record's closed schema has no such field** — the reasons point at something that is
  not there. The adjudication record is the named human's committed artifact and is
  append-only; rewriting its header is not this story's act. Recorded on `DF-13-3-A`.

### Completion Notes

**The gate decision is `BLOCKED`, it is committed, and it is derived.** The named human
adjudicated all 31 emitted blocking findings on 2026-08-17 — the prerequisite Epic 13 was
built around is discharged — but 5 came back `BORDERLINE`, protocol §4's ladder has not
terminated for them, and §2's tie-break seats are unfilled. So the run is **not exhaustive**,
`fold.evaluable` is **False**, and **no §5 outcome was taken**. `BLOCKED` is a third terminal
state precisely so this cannot be written down as *"the gate did not clear"*: a shortfall and
an incomplete measurement are different claims, and downstream nothing can tell them apart
once the wording collapses them. **The orchestrator's brief directed `NOT_CLEARED` on a
premise (`evaluable=True`, denominator 26) that measurement falsifies; the divergence is
recorded in Debug Log §2 and was not adopted.**

**Everything the outcome permits was still done in full.** The decision instrument exists as
a closed three-outcome vocabulary that raises; §5's four conditions are computed
**individually**, each with its measured value, its own verdict from a closed verdict
vocabulary, and a countable *"what would close it"*; §5's clean-repo condition is **measured
explicitly over the cartridge corpus** rather than counted met by default, naming the two
clean members it folded; and the committed record carries the corpus with pinned shas, the
adjudicators, the protocol version asserted against the change-log head, the expert-hours
report, the residual, the closure path and the AC3b concentration disclosure — every field
derived, none typed, through `argus.store.canonical`, tracked in git and asserted so with
`git ls-files`.

**The disclosure stayed and nothing was tuned.** `INSTRUMENT_STATUS` is unchanged,
`protocol_cleared` is still never passed `True` from `argus/**`, the four static disclosure
surfaces are byte-unchanged, and `precision-validation-protocol.md` was **not touched at
all** — so §5's literals and §7's invariants are byte-unchanged by construction and the
record's version pin still holds.

**Two defects were found by execution and one was fixed.** The gate-status sentence published
*"DENOMINATOR EMPTY"* beside a denominator of 26 — fixed additively, default byte-identical.
The `-46` blind spot on a derived `protocol_cleared` was reproduced and **not opened**:
`decide_gate` passes the literal `False`, and the fix is filed for whoever performs the flip.

**One red remains and is named, not worked around** — `TC-ArgusAgent-DOCS-001-54`, because
this story's two new modules moved `README.md`'s wheel/sdist figures and `README.md` carries
an uncommitted operator rewrite this session was instructed not to touch. The exact two-token
remedy is in Debug Log §7 with a named owner.

### File List

**New**

- `argus/precision/gate_decision.py`
- `argus/precision/gate_disclosure.py`
- `scripts/build_gate_decision.py`
- `tests/test_gate_decision.py`
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/gate-decision-record.json`
- `_bmad-output/design-artifacts/ArgusAgent/epic-13-open-items.md`

**Modified**

- `argus/precision/adjudication.py`
- `argus/precision/replay_harness.py`
- `tests/test_adjudication_record.py`
- `tests/test_release_preflight.py`
- `CHANGELOG.md`
- `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md`
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md`
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
- `_bmad-output/design-artifacts/ArgusAgent/stories/13-3-record-the-result-and-let-it-decide.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` *(regenerated, separate commit)*
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` *(regenerated, separate commit)*
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` *(regenerated, separate commit)*

**Deliberately NOT modified**

- `README.md` — uncommitted external edit, operator-owned. See Debug Log §7.
- `_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md` — untouched.
- `argus/verdict/negative_assurance.py`, `pyproject.toml`, `action.yml` — byte-unchanged.
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-record.json` — the
  named human's committed, append-only artifact.

### Review Findings

<!-- The reviewer writes findings HERE, in this file, not only into sprint-status.yaml (AI-E12-10). -->

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-08-17 | v1.0 | **The decision is recorded, and the outcome is `BLOCKED` — not `NOT_CLEARED`, and the distinction is the entire point of AC1.** The BLOCKING PREREQUISITE is **discharged**: the named human (**XAgent007**, Engineering Lead) adjudicated **all 31** emitted blocking findings on 2026-08-17 — **0 TP / 26 FP / 5 BORDERLINE / 0 UNADJUDICATED**, `expert_hours` still `null` (a report, never a gate, and no agent may invent one). **But the run is NOT exhaustive.** Protocol §4 states in its own text that `BORDERLINE` — *"looked at, could not decide"* — *"makes the run non-exhaustive until it resolves"*; five ladders (locator re-examination → golden-key correction → **external tie-break**) have not terminated, and §2 records the QA-Lead and external-adjudicator seats as **unfilled**. Measured: `exhaustiveness` → `Unevaluable(residual=5, adjudicated=26)`, `fold.evaluable` → **`False`**. AC1's table makes *"not exhaustively adjudicated"* a **`BLOCKED`** condition by name, so **no §5 outcome was taken**, and `BLOCKED` is never rendered as *"the gate did not clear"*. ⚠️ **The orchestrator's spawn brief directed `NOT_CLEARED` on the premise that the fold was EVALUABLE with denominator 26; measurement falsifies the premise, the divergence is recorded in Debug Log §2, and it was NOT adopted** — recording a measured shortfall over an adjudication nobody finished is §0.1(1)'s falsehood in the direction the story did not anticipate. **Everything the outcome permits was done in full:** a closed-membership three-outcome vocabulary that RAISES (`argus/precision/gate_decision.py`); §5's four conditions computed **individually**, each with its measured value, its verdict from a closed verdict vocabulary and a countable closure path — precision **UNEVALUABLE**, clean-repo blocking-FP **MET** *(measured explicitly over the CARTRIDGE corpus through `compute_precision`, naming the two clean members it folded, because §5 as amended names 13.3 by name and forbids counting it met by default)*, N≥5 **MET** (derived, 5), adjudication-run-recorded-cleared **FAILED**; a committed, git-tracked, fully DERIVED `gate-decision-record.json` through `argus.store.canonical`; and **AC3b's concentration disclosure, derived and never typed** — 31 findings from **2 of 5** ratified members, **3 contributed zero**, **1** rule class — guarded in BOTH directions (`-59` fires on the live corpus and must NOT fire over a synthetic well-distributed one). A **derived completion bound** records that no resolution of the 5 residual reaches the threshold (all-TP gives **5/31** < **4/5**) — recorded as a **BOUND, not a decision**; `-60` pins that it may not promote `BLOCKED`. **The disclosure STAYED and nothing was tuned:** `INSTRUMENT_STATUS` unchanged, `protocol_cleared` still never `True` from `argus/**` (`decide_gate` passes the **literal `False`** so `DOCS-001-46` is not blinded), the four static surfaces byte-unchanged, and `precision-validation-protocol.md` **not touched at all** — §5's literals and §7's OI1 bullets byte-unchanged by construction, change-log head still **V1.3**, record pin intact, no re-adjudication forced. **Two defects found by execution:** the gate-status sentence published *"DENOMINATOR EMPTY"* beside a denominator of 26 (`DF-9-2-B`'s false-subject class) — fixed **additively**, default byte-identical for every pre-13.3 caller; and `-46`'s blind spot on a derived flag — **reproduced and deliberately not opened**, filed as `DF-13-3-B` for whoever performs the flip. **Three inherited RED guards re-derived, not deleted and not trivially satisfied** (`PRECISION-001-39`/`-47`/`-52`): 13.2 encoded *"nothing is adjudicated yet"* as a permanent invariant when it was transient, so all three failed on the event they existed to wait for; each now asserts the property it actually protected, derived from the record, and each can still fail. **Ledger `+165 / -0`:** `DF-13-3-A` filed (the `agent-smith` pinned sha `9ab774d7` is UNREACHABLE — its 7 findings were adjudicated against the `d9bb793` reconstruction, so `reproducibility_verified` is no longer re-verifiable for that member, and **all 5 residual `BORDERLINE` findings are that member's**) and `DF-13-3-B` filed; `DF-13-2-A` re-stated with residual **5** instead of 31; `DF-12-7-B` **not** dispositioned (AC4(f) is CLEARED-branch work). PRD's two stale corpus figures corrected against the **derived** count, struck not erased, NOT-CLEARED status preserved verbatim (AC6). **`epic-13-open-items.md` emitted** (AC7, re-derived by execution; the retrospective is **not** written here). ⚠️ **Story premise corrected: CI evidence is now PARTIALLY established** — `audit-ci.yml` succeeded on `c027e16`/`be35c7f`/`b04dc1a`/`bc55e36` and **failed** on `ae54234`; the newest verified sha is still **behind** the adjudication commit, so CI evidence remains **NOT ESTABLISHED** for the adjudication or this delta. **Gates LOCAL** (Windows-only; CI is an ubuntu matrix): `pytest` **1597 collected / 1596 passed / 1 failed / 0 skipped**, `mypy` **clean, 86 source files**, `bandit` **19 Low / 0 Medium / 0 High**. ⚠️ **The one red is named, not worked around:** `TC-ArgusAgent-DOCS-001-54` — this story's two new modules moved `README.md`'s wheel/sdist figures (92→94, 91→93), and `README.md` carries an **uncommitted operator rewrite** (+122/−404) this session was instructed not to touch, stage, commit or revert. Two-token remedy and named owner in Debug Log §7. Nothing outward-facing: `git tag -l` empty, no push, no tag, no release. | Developer (dev-story, Story 13.3) |
| 2026-08-17 | v0.1 | Story contexted. Premises re-measured **by execution** on `411d891`. **The required input does not exist**: the committed adjudication record holds **31 rows, all `UNADJUDICATED`, zero judgements, no adjudicator** — and the ledger already locks the consequence (*"13.3 computes over an adjudicated record and cannot begin without one"*), so the story is written with a **three-outcome** terminal vocabulary (`CLEARED` / `NOT_CLEARED` / `BLOCKED`) that refuses to let a vacuous fold be recorded as a shortfall. **Two defects found by execution:** `INSTRUMENT_DISCLOSURE_VALIDATED` names *"the Argus dogfood corpus"* — the self-audit 13.1 excluded from N, i.e. the cleared statement would rest on the corpus that cannot clear it (`DF-9-2-B`'s class, and `DOCS-001-58` pins it); and `protocol_cleared_call_sites` matches **only a literal `True`**, so deriving the flag — the correct design, and what the architecture's adjudication-record rule demands — makes `TC-ArgusAgent-DOCS-001-46` **vacuous at the exact moment the gate flips**. **Four stale references corrected:** the tracker's PRD `L118/L130/L141/L302` were correct at `f677e90` and now point at unrelated headings (live sites enumerated by content); `prd.md:176` (*N=1*) and `:373` (*N=0*) contradict `:196` (*N=5*) on this tree; the tracker header's *"H0 is STILL UNOWNED"* was closed **2026-08-10b via option (b)** (the substance — H1–H4 NOT FILED, A5 UNSUPPORTED, H3 unmade — is unchanged and is the point); and four of the epic AC's seven `DF-*` ids have moved. Baseline: pytest **1585 collected, exit 0**; mypy **clean, 84 files**; bandit **19 Low / 0 Med / 0 High**. `protocol_cleared` still never `True`; `origin/master` 13 commits behind; nothing published. | Scrum Master (create-story) |
