# Story 13.3: Record the result, and let it decide

Status: ready-for-dev

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
| the seven ledger ids *"as of 2026-08-10b"* (`DF-6-7-A`, `DF-8-4-B` bytes-example half, `DF-8-4-C`, `DF-8-4-D`, `DF-8-5-B`, `DF-8-5-C`, `DF-9-2-C`) | ❌ **MOVED.** Measured: `DF-6-7-A` **CLOSED by disposition** (invocation half still open) · `DF-8-4-D` **CLOSED 2026-08-15** · `DF-8-5-C` **CLOSED 2026-08-16** · `DF-9-2-C` **CLOSED** (already-true, verified) · `DF-8-4-B` / `DF-8-4-C` remain **open and unowned by decision** · `DF-8-5-B` recurs as the artifact-currency bootstrap |

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

- [ ] **Task 0 — Confirm the precondition, by execution (AC: 1)**
  - [ ] Load the committed record; report `counts()`, `len(rows)`, the adjudicator set, `expert_hours`
  - [ ] Assert `protocol_version == change_log_head_version(protocol_text)`
  - [ ] Run `fold_adjudicated_precision` and record `evaluable`, `exhaustiveness`, `determinism`
  - [ ] **Decide the terminal state NOW and record it**: `CLEARED` / `NOT_CLEARED` / `BLOCKED`.
        If `BLOCKED`, AC4 and AC5 are not performed and the reason is recorded — **do not
        compute a decision anyway**
- [ ] **Task 1 — Re-measure every §0 / §0.1 / §0.3 premise on YOUR baseline (AC: all)**
  - [ ] Re-run the §0.1 reproductions; record actual output in Debug Log §1
  - [ ] Re-measure every cited line number before citing it; record confirmations *and* divergences
- [ ] **Task 2 — Build the decision instrument (AC1, AC2, AC3)**
  - [ ] Closed three-outcome vocabulary that **raises** on an unregistered member
  - [ ] The four §5 conditions computed individually, each with its measured value and verdict
  - [ ] Clean-repo FP: fold the **cartridge** corpus explicitly, or record NOT APPLICABLE with its
        reason — **never count it met by default** (protocol §5 names 13.3 by name)
  - [ ] Fold via `fold_adjudicated_precision`; arithmetic via the shared objects. **No second fold**
  - [ ] Non-vacuity floor asserted **first**, before any other assertion
- [ ] **Task 3 — Commit the gate-decision record (AC3)**
  - [ ] Every field derived; nothing hand-typed; `argus.store.canonical` only
  - [ ] In git (**not** `.argus/`); asserted with `git ls-files`, not a path check
  - [ ] NFR-S1: locators + counts + rule-id provenance only; reuse the locator regex
- [ ] **Task 4 — The CLEARED branch (AC4) — perform ONLY if Task 0 returned `CLEARED`**
  - [ ] Pass `protocol_cleared` from a production `argus/**` site; expect `-46` RED
  - [ ] Flip `INSTRUMENT_STATUS`; edit the four static surfaces; **assert** the five render sites
        need no edit rather than assuming it
  - [ ] **Correct `INSTRUMENT_DISCLOSURE_VALIDATED`'s corpus name**; answer `-58`'s red by
        correcting the pin, never by keeping the false subject
  - [ ] **Prove `-46` is not vacuous** with the flip in place — the story's highest-risk clause
  - [ ] Update the PRD gate-status sites **found by content**; enumerate what you changed
  - [ ] Disposition `DF-12-7-B`; record that clearing authorises **attested externalization only**
- [ ] **Task 5 — The NOT-CLEARED branch (AC5) — perform ONLY if Task 0 returned `NOT_CLEARED`**
  - [ ] Record which conditions failed, their measured values, and what would close each
  - [ ] Prove the disclosure stayed: `-46` green, `protocol_cleared` still never `True`, the four
        static surfaces **byte-unchanged**
  - [ ] **Prove no threshold moved**: `git diff` on the protocol shows additions/strikes only and
        the §5 literals are byte-unchanged
- [ ] **Task 6 — Correct the stale PRD corpus figures (AC6) — in EVERY branch**
  - [ ] `prd.md:176` (*N=1*) and `:373` (*N=0*) corrected from the derived count; strike, never erase
  - [ ] The NOT-CLEARED status text at those sites preserved verbatim unless Task 4 fired
  - [ ] `TC-ArgusAgent-DOCS-001-75` stays **derived**; prove it still moves
- [ ] **Task 7 — Emit the re-derived open-items list (AC7)**
  - [ ] **Re-derive** H0/H1–H4, A5, H3 and every open `DF-*` from the tree — **do not copy** the
        epic AC's list, the tracker header, or §0's table
  - [ ] Record the two measured corrections: H0 **is owned**; four of the seven listed ids **moved**
  - [ ] One sentence: a cleared gate authorises attested externalization and **is not plan closure**
  - [ ] Do **not** write the retrospective
- [ ] **Task 8 — Ledger and documents (AC8)**
  - [ ] `deferred-work.md` `+n / -0`; every claimed closure backed **in the same commit**
  - [ ] In `BLOCKED`: re-state `DF-13-2-A` / `DF-6-6-A`* / `DF-7-2-A` with what remains; file the
        13.3 entry with a **named owner**
  - [ ] Register any new invariant in architecture §Enforcement in the model form
- [ ] **Task 9 — Gates and hand-off**
  - [ ] `pytest` / `mypy` / `bandit` with **actual numbers**, labelled **LOCAL**; CI **NOT ESTABLISHED**
  - [ ] NFR-M1 re-measured on every touched file (**three are effectively full**)
  - [ ] If `argus/**` moved: commit → regenerate the three dogfood artifacts → commit separately
  - [ ] Nothing outward-facing; re-assert by execution (`git tag -l`, remote unmoved). **Do not push**

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

### Debug Log

### Completion Notes

### File List

### Review Findings

<!-- The reviewer writes findings HERE, in this file, not only into sprint-status.yaml (AI-E12-10). -->

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-08-17 | v0.1 | Story contexted. Premises re-measured **by execution** on `411d891`. **The required input does not exist**: the committed adjudication record holds **31 rows, all `UNADJUDICATED`, zero judgements, no adjudicator** — and the ledger already locks the consequence (*"13.3 computes over an adjudicated record and cannot begin without one"*), so the story is written with a **three-outcome** terminal vocabulary (`CLEARED` / `NOT_CLEARED` / `BLOCKED`) that refuses to let a vacuous fold be recorded as a shortfall. **Two defects found by execution:** `INSTRUMENT_DISCLOSURE_VALIDATED` names *"the Argus dogfood corpus"* — the self-audit 13.1 excluded from N, i.e. the cleared statement would rest on the corpus that cannot clear it (`DF-9-2-B`'s class, and `DOCS-001-58` pins it); and `protocol_cleared_call_sites` matches **only a literal `True`**, so deriving the flag — the correct design, and what the architecture's adjudication-record rule demands — makes `TC-ArgusAgent-DOCS-001-46` **vacuous at the exact moment the gate flips**. **Four stale references corrected:** the tracker's PRD `L118/L130/L141/L302` were correct at `f677e90` and now point at unrelated headings (live sites enumerated by content); `prd.md:176` (*N=1*) and `:373` (*N=0*) contradict `:196` (*N=5*) on this tree; the tracker header's *"H0 is STILL UNOWNED"* was closed **2026-08-10b via option (b)** (the substance — H1–H4 NOT FILED, A5 UNSUPPORTED, H3 unmade — is unchanged and is the point); and four of the epic AC's seven `DF-*` ids have moved. Baseline: pytest **1585 collected, exit 0**; mypy **clean, 84 files**; bandit **19 Low / 0 Med / 0 High**. `protocol_cleared` still never `True`; `origin/master` 13 commits behind; nothing published. | Scrum Master (create-story) |
