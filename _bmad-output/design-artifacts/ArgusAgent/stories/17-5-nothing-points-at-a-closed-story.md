---
baseline_commit: b8eaeee
---

# Story 17.5: Nothing points at a closed story

Status: review

<!-- Contexted 2026-08-26 at HEAD `b8eaeee` (branch `docs/merge-strategy-decision`, 21 ahead of
     `origin/master`) by the create-story workflow (Opus 5). `git status --porcelain` is EMPTY at
     contexting — unusually, the peer session has nothing staged. That will not stay true; stage by
     explicit path and never `git add -A`.

     EVERY FIGURE IN SECTION 0 WAS PRODUCED BY EXECUTION AGAINST THIS TREE AT `b8eaeee`, not read
     out of `epics.md`. `epics.md`'s Epic 17 section was written 2026-08-24, BEFORE Epic 18 ran and
     BEFORE Stories 17.1-17.4 ran. It is STALE in six separate places that this story's ACs correct,
     and its headline count of "six entries" is a SUBSET of the measured population, not the
     population. The parsers used are the ledger's own committed analyzers
     (`tests/test_governance_record_integrity.ledger_closed_ids` / `story_closure_claims`), driven
     over the live `deferred-work.md` and `sprint-status.yaml`.

     THE ONE THING THAT MAKES THIS STORY DIFFERENT FROM 17.1-17.4: IT CHANGES NO RESULT.
     The criterion (`scripts/precision_preregistration.py`, `f906d04`), the specification
     (`successor-vacuity-predicate-specification.md`) and the measurement
     (`validation-corpus/successor/successor-reach-record.json`) are FROZEN. This story rewrites
     POINTERS and records DISPOSITIONS. A pointer rewrite is not a disposition and a disposition is
     not a re-measurement; the ACs below keep those three things apart on purpose. -->

## Story

As the **Engineering Lead**,
I want **every ledger entry, planning note and shipped-module comment that points at a story or an epic which has since closed re-pointed at what is actually true — and anything genuinely still open to say so, in its own body, with a live owner**,
so that **work with no container stops being recorded as work that is already scheduled, and a guard stops the class recurring.**

### What this story IS

Three deliverables, and they are separable:

1. **The dispositions.** Each entry that this story is chartered to touch receives a **dated,
   append-only note under its OWN bullet block** in `deferred-work.md` — not in a table 900 lines
   away — recording one of exactly three honest outcomes: **DISPOSED** (with the evidence),
   **RE-HOMED** (to a live owner), or **STILL OPEN with a corrected pointer**.
2. **The shipped-module comment corrections.** The forward references to Story 6.2 in `argus/**`
   name the real owner, with no behaviour change.
3. **The guard** — `TC-ArgusAgent-DOCS-001-80` — asserting that no ledger entry affirmatively points
   its `target_story` at a story `sprint-status.yaml` records as `done`, landing over a **dated,
   shrink-only registry** of the historical population it found, and driven RED at the real seam.

### What it is NOT

⛔ **It is not a re-measurement.** Epic 17's measured outcome is `UNEVALUABLE` and this story does
not touch it, soften it, or re-run it. `scripts/precision_preregistration.py` stays **BYTE-FROZEN**;
`TC-ArgusAgent-PRECISION-001-140` stays unmoved; `successor-reach-record.json` stays byte-unchanged.

⛔ **It is not a mass closure.** The measured population of entries pointing at `done` stories is
**far larger than the six `epics.md` names** (§0.2). Disposing of entries this story has not verified
would be `AI-E12-3`'s defect — resolving entries in prose rather than against evidence — committed
inside the story written to stop it. The unverified remainder is **REGISTERED, not resolved**, with a
named owner (`AI-E9-8`).

⛔ **It does not rewrite a signed record.** §3.4 evidence immutability holds: the 2026-08-21 research,
the Epic-18 retrospective, the 2026-08-24 charter section and `epics.md`'s prior text stand as
written. Corrections are DATED APPENDS beside them.

⛔ **It spends no round.** `DF-13-5-A` stays **OPEN and UNSPENT**. No corpus member is ratified, no
third-party source is fetched, no finding becomes verdict-eligible.

⛔ **It is not a performance story and not an adjudication.** `DF-AUD-DETECT-C` gets a corrected
pointer and a live owner, never a disposition (§0.5).

---

## Acceptance Criteria

### AC1 — The population is MEASURED, and the epic's count is corrected against it

**Given** `epics.md` states that **six** open ledger entries name Story 6.2, and that this story's
subject is "nothing points at a closed story"
**When** the dev agent enumerates, **by execution over the live `deferred-work.md` and
`sprint-status.yaml`**, every canonical entry block whose own `- target_story:` field resolves to a
story key `sprint-status.yaml` records as `done`
**Then** the story record states the measured counts and reconciles them with the epic's six —
**re-deriving §0.2's figures rather than copying them**, and recording any difference with the line
numbers that produce it.

**Given** the measured population is larger than six
**Then** the excess is **partitioned and registered**, not silently absorbed and not silently dropped:
every measured id is either (a) dispositioned by this story, or (b) named in the guard's landing
registry with its reason. ⛔ **No measured id may be absent from both.**

### AC2 — The six 6.2-pointed entries get dispositions IN THEIR OWN BODIES

**Given** `DF-12-2-D`, `DF-12-3-A`, `DF-14-1-A`, `DF-16-7-A`, `DF-16-7-B` and `DF-INV-VACUOUS-A` each
carry a `- target_story:` naming Story 6.2 — a story that is `done`, whose retrospective is signed,
and whose story file carves dataflow out explicitly
**And given** the 2026-08-24 charter section already re-homed all six **in a table**, while
`AI-E18-10` records the residual defect in terms: *"all six entries still read `target_story: NONE`
in their own bodies … a reader of the ledger alone cannot see it"*
**When** this story completes
**Then** each of the six carries a **dated, append-only note under its own bullet block** naming its
live owner, in the same form as the `DF-AUD-DETECT-D` / `DF-INV-VACUOUS-B` notes already in this
ledger — and the note states what Epic 17 actually delivered for it, which is **not** what
`epics.md` promised (AC5).

**Given** `DF-1-7-B` is disposed and correctly names 6.2 as the story that discharged it
**Then** it is **LEFT BYTE-UNTOUCHED**. ⛔ Re-homing it would falsify a signed record. Its exclusion
is asserted by the guard's own registry, not left to a reviewer's memory.

**Given** `DF-12-3-A` reads as disposed to `ledger_closed_ids` only because of a **half-closure**
line (§0.4)
**Then** its note states which half is disposed and which half is open, so the entry's true state is
readable without running an extractor.

### AC3 — The Epic-18 scheduling pointers become disposition pointers

**Given** the 2026-08-24 charter section scheduled `DF-AUD-DETECT-A`/`-B`/`-E`/`-F` to Epic 18
stories and `-D` to Story 17.3
**And given** all five of those stories are now `done` and all five entries now carry terminal
dispositions in the ledger (§0.5)
**When** this story completes
**Then** the epic's AC — *"`DF-AUD-DETECT-A`/`-B`/`-E`/`-F` are pointed at Epic 18 and `-D` at this
epic's Story 17.3 — scheduling notes only"* — is recorded as **DISCHARGED AND SUPERSEDED**: a
scheduling note pointing at completed work is the exact defect this story exists to end, and the
replacement is a dated pointer naming each entry's disposing story and fix sha.

**Given** Story 17.3's Completion Notes record this hand-off explicitly and demand *"a DISPOSITION
POINTER naming this note's sha instead of a schedule"*
**Then** `2db5ce0` is named for `DF-AUD-DETECT-D`, and the hand-off is recorded as honoured.

**Given** `DF-AUD-DETECT-C` was deliberately NOT scheduled and Story 17.3 explicitly declined to
disposition it
**Then** it receives a **corrected pointer and a live owner only** — `AI-E18-10`'s destination
decision stays the Governance Owner's act. ⛔ **No disposition, no severity change, no status change.**

### AC4 — Four named modules, and the measured set is wider than four

**Given** `epics.md` names four modules carrying stale forward references to Story 6.2
**When** the dev agent greps `argus/**` at HEAD
**Then** the measured forward-reference set is recorded (§0.6: **12 sites across 7 modules**, of
which the epic names 5 sites across 4), and **every measured forward-reference site is corrected** to
name the real owner — with **no behaviour change** and `argus/**` otherwise byte-unchanged.

**Given** `argus/detectors/assertion_strength.py:64` was created by **Story 17.3 on 2026-08-25** and
repeats the identical stale sentence
**Then** the story record states plainly that the defect **reproduced itself inside Epic 17, one
story before the story written to end it** — the same shape `DF-16-6-D` counted eight times.

**Given** three reference classes are NOT the defect and must survive byte-identical
**Then** each is carved out **by name and by line** and left untouched:

  (a) **TRUE HISTORICAL** references — `argus/pipeline.py:9/35/43/55/115`, `pipeline_persist.py:13`,
      `pipeline_stages.py:138`, `argus/verdict/prosecutor.py:29/50/227` — statements about what 6.2
      **did**, which are correct;

  (b) **BEHAVIOUR-BEARING STRINGS** — `argus/ledger/depth_semantics.py:134/138` (a `DEPTH_SEMANTICS`
      payload a user reads) and `argus/ledger/recording.py:77` (a pydantic `Field(description=...)`
      that reaches the emitted schema). ⛔ Editing either is a behaviour change and is **out of scope
      for a comment story**; both are recorded in the ledger instead;

  (c) `tests/**` references, which this story does not sweep.

**Given** the correction moves `argus/**` bytes
**Then** `TC-ArgusAgent-DOGFOOD-001-49`..`-52` require a dogfood regeneration at a truthful
provenance sha, in **its own commit**, exactly as Story 17.3 did at `7e72d91` (§0.7). ⛔ **This is a
KNOWN cost, not a discovery, and the story is not complete without it.**

### AC5 — Epic 17's actual outcome replaces Epic 17's promised outcome

**Given** Story 17.4's recorded outcome is **`UNEVALUABLE`** — sealed contributing members **0**,
below the resolved floor of **3**; `measured_precision` **null**; 1,032 walked / 0 skipped;
S1-eligible **85** across **3** contributing members; and `S1` shipped **ADVISORY**, promoting **0 of
1,032**
**When** this story completes
**Then** every document that assumes Epic 17 would deliver a promoted successor predicate carries a
**dated correction naming what actually happened**, and the ones measured at contexting are corrected
by name:

| surface | the stale claim | measured at `b8eaeee` |
|---|---|---|
| `epics.md:346` | *"Epic 17 **repairs** FR10's detector"* | S1 is ADVISORY; the verdict-eligible stage still promotes 0 of 1,032 |
| `epics.md` Epic 17 header | *"Capability delivered: … replacing a mock-provenance vacuity signal"* | nothing was replaced at the verdict layer |
| `epics.md` Epic 17 `**Covers:**` | lists `DF-INV-VACUOUS-A`, `DF-14-1-A`, `DF-16-7-A`, `DF-16-7-B`, `DF-12-2-D`, `DF-12-3-A` | none of the six was delivered by Epic 17; only `DF-AUD-DETECT-D` and `DF-INV-VACUOUS-B` were |
| `epic-18-retro-2026-08-25.md:480` | *"Epic 17 has no retrospective because Epic 17 has not run"* | 17.1-17.4 are `done` |
| `epic-18-retro-2026-08-25.md:523`-`:527` | *"before its first story is contexted"* | four stories are contexted and delivered |
| `epic-18-retro-2026-08-25.md:580` | *"`DF-AUD-DETECT-D` OPEN — Story 17.3 — an epic that has not started"* | terminal disposition at `2db5ce0` |

**Given** §3.4 evidence immutability
**Then** the Epic-18 retrospective and the 2026-08-21 research are **NOT rewritten**: their
corrections are recorded once, dated, in `deferred-work.md`, naming the stale statements by line.
`epics.md` receives a dated correction note in the form it already uses at `:339` and `:341`.

**Given** `scripts/precision_preregistration.py:14` reads *"Epic 17 is about to move the
verdict-eligible population"* — an optimistic sentence that is now false
**Then** it is **NOT EDITED**. The module is byte-frozen by Story 17.1 and
`TC-ArgusAgent-PRECISION-001-140`; the sentence is evidence of when it was written. ⛔ **The story
record must say this explicitly so a later editor cannot "tidy" it into a guard failure.**

### AC6 — The guard, and it is scoped by measurement rather than by wish

**Given** the defect class this story exists to end
**When** `TC-ArgusAgent-DOCS-001-80` runs
**Then** it fails if any canonical `deferred-work.md` entry block's own `- target_story:` field
**affirmatively names** a story key `sprint-status.yaml` records as `done`, and is not registered.

**Given** a naive reading of that rule is RED against **47** entry blocks today (§0.2)
**Then** the guard's population is **narrowed by stated rule, never by convenience**, and the two
narrowings are asserted with positive controls over synthetic input:

- **affirmative form only** — a field reading `NONE — no story exists after 9.2` or `NONE — the next
  story that edits X` mentions a done story as a **landmark**, not as an owner, and is not a
  violation. **23** blocks are excluded by this rule and the count is asserted;
- **the disposing-story form is not a violation** — an entry naming the story that discharged it
  (`DF-1-7-B` → 6.2) is the one true pointer shape, and is excluded by name.

⛔ **THE GUARD MUST NOT DECIDE OPENNESS WITH `ledger_closed_ids`, AND THE REASON IS MEASURED, NOT
ARGUED** (§0.4): that extractor reports **42** disposed ids at HEAD, and **two of them are false
positives on entries this very story handles** — `DF-13-5-A` (`deferred-work.md:4752` and `:5752`)
and `DF-12-3-A` (`:4292`, a half-disposition). The three triggering sentences are quoted in §0.4 with
the verb elided, for the reason AC9 gives. ⛔ **Building the openness test on it would import a
known-defective predicate into the guard written to end a defect class.**
`DF-16-6-D` is the senior record on this question and its position — *"the extractor is correct and
essentially unimprovable … the record is what is wrong, every single time"* — is followed here.

**Given** `AI-E11-1` guard adequacy
**Then** `-80` names its observable, is driven **RED at the real seam** (a synthetic ledger fragment
built in `tmp_path`, never against the committed ledger), generates at least one adversarial variant
from the live corpus with a count asserted, and carries a `> 0` non-vacuity floor so a broken parser
goes red rather than silently green.

### AC7 — The registry can only shrink, and it is not an amnesty

**Given** the guard lands over a repository that predates it
**Then** the historical population is registered **BY NAME with a date, an owner and a reason** — the
`_UNBACKED_AT_LANDING` / `_EXEMPT_BY_DESIGN` pattern this project already uses — and `-80` fails if a
registered pair becomes clean, so the registry **can only shrink**.

**Given** two alternatives
**Then** both are rejected on the record: **mass re-homing** (resolving entries this story never
verified — `AI-E12-3`), and **narrowing the population until it goes green** (Story 12.1's named
anti-pattern, and `test_module_size_ceiling.py::_REMEDY` forbids the shape).

**Given** `AI-E9-8`
**Then** the registry names a human owner — **XAgent007 (Engineering Lead)** — never
`target_story: NONE` alone.

### AC8 — The rule is registered where rules live

**Given** `TC-ArgusAgent-DOCS-001-77` asserts *"a rule in a test is not a rule"*
**When** `-80` lands
**Then** `architecture.md` §Enforcement gains a **Stale-target-story enforcement** block in the
established form (rule text · enforcing module · test ids), and `-77`'s anchor tuple is extended to
assert it — additively, with `len(anchors) >= 15` still holding and no existing anchor removed.

**Given** the ids already taken
**Then** the new id is **`TC-ArgusAgent-DOCS-001-80`** — `-79` is the highest `ArgusAgent-DOCS` id in
the tree (measured) — and it lands in **`tests/test_governance_record_integrity.py`** (322 lines;
ceiling 1200), whose cohesion is exact: every guard in it closes over the governance documents.
⛔ **No id is renumbered.**

### AC9 — The record cannot trip the guard that watches records

**Given** `TC-ArgusAgent-DOCS-001-78`'s `story_closure_claims` is line-scoped and anchored to the
verbs `CLOSED` / `Closes` / `closes` / `Closed by this story`
**And given** this epic has already tripped it twice during contexting, and `DF-16-6-D` counts
**eleven** instances of the class across Epics 12, 16 and 17
**When** this story writes its record and its ledger notes
**Then** the authoring rule is **mechanised, not remembered**: before each commit the dev agent runs
`-78`'s own exported analyzers over the changed story file and the changed ledger, and asserts
(a) every id `story_closure_claims` extracts from this story file is present in
`ledger_closed_ids(deferred-work.md)` **in the same commit**, and (b) `ledger_closed_ids` gains no id
this story did not intend to add. ⛔ **A disposition verb and an id on one physical line, where the
ledger holds no disposition, turns `-78` RED for the whole repository.**

**Given** the same rule applies to future editors of these ACs
**Then** the story record states the authoring rule in terms — *never write a disposition verb on a
line that also carries a `DF-` id unless the ledger backs it in that same commit* — so the guard
cannot be re-introduced by a later tidy-up. This AC is the reason no acceptance criterion above
writes a disposition verb beside `DF-12-2-D`, `DF-14-1-A`, `DF-16-7-A`, `DF-16-7-B` or
`DF-INV-VACUOUS-A`.

### AC10 — Byte invariants, staging discipline, and the escalation clause

**Given** `deferred-work.md` carries a **lone-CR byte invariant** (607,244 bytes · **1 CR** · 0 CRLF
at `b8eaeee`) and is append-only for dispositions
**Then** every write is a pure append inside the target entry's block, the CR count is **1** before
and after, and the byte count is reported. ⛔ **`sed -i` is forbidden on every artifact file** — GNU
sed on this host flattens CRLF file-wide.

**Given** `sprint-status.yaml` must hold exactly **1,264 lines / 1,264 CR**
**Then** it is verified after every edit.

**Given** a **concurrent peer session commits to this same branch**
**Then** every commit stages **explicit paths**. ⛔ **`git add -A` is forbidden.**

**Given** local gates are Windows-only and CI runs an ubuntu matrix
**Then** every file read in new code passes `encoding="utf-8"` explicitly, no test resolves a path by
`os.sep`, and the story record states that the evidence is LOCAL.

**Given** anything forces a write outside the declared write set (§2.1)
**Then** it is **ESCALATED and recorded** in the story record before it is taken, in the form
`DN-17-3-16` established — never absorbed silently.

---

## Tasks / Subtasks

- [x] **Task 1 — Re-measure §0 at HEAD before writing a line** (AC1)
  - [x] Re-derive the entry-block population, the 47/23 partition and the 6.2 set from the live
        `deferred-work.md` + `sprint-status.yaml`. Record any drift from §0.2 with line numbers.
  - [x] Re-grep `argus/**` for `6.2` / `6-2-` and re-derive the 12-site / 7-module forward-reference
        set of §0.6. Re-classify each site as forward / historical / behaviour-bearing.
  - [x] Re-run `ledger_closed_ids` and confirm the false positives at `:4292`, `:4752`, `:5752`.
  - [x] Confirm `git diff --quiet f738df0 HEAD -- argus/` is still empty (the dogfood baseline).
- [x] **Task 2 — The ledger dispositions, ONE dated section, pure append** (AC2, AC3, AC5)
  - [x] Append a dated `## Story 17.5 dispositions — 2026-08-26` section AND an append-only note
        under each of the six entries' own bullet blocks. Both, not either.
  - [x] Record the Epic-18 / 17.3 scheduling pointers as discharged-and-superseded, naming each
        disposing story and fix sha.
  - [x] Record `DF-AUD-DETECT-C`'s corrected pointer and live owner. No disposition.
  - [x] Record the six Epic-17-outcome corrections of AC5's table, by document and line.
  - [x] Record the two behaviour-bearing carve-outs of AC4(b) as OPEN observations with owners.
  - [x] Verify: 1 CR, 0 CRLF, pure append (`+n / -0`), byte count reported.
- [x] **Task 3 — The module comment corrections** (AC4)
  - [x] Correct all 12 forward-reference sites. Leave (a)/(b)/(c) byte-identical.
  - [x] Prove no behaviour change: full suite green, and `git diff --stat argus/` shows only
        comment/docstring lines.
- [x] **Task 4 — Regenerate the dogfood artifacts** (AC4, its own commit)
  - [x] `python scripts/regenerate_dogfood_artifacts.py`; confirm
        `TC-ArgusAgent-DOGFOOD-001-49`..`-52` green and the cited provenance sha is a real ancestor
        of HEAD.
- [x] **Task 5 — The guard** (AC6, AC7, AC8)
  - [x] Add `TC-ArgusAgent-DOCS-001-80` to `tests/test_governance_record_integrity.py` with a pure,
        exported analyzer; the affirmative-form and disposing-story narrowings each with a positive
        control; the `> 0` non-vacuity floor; the generated adversarial variant with an asserted count.
  - [x] Drive it RED at the real seam against a synthetic ledger fragment under `tmp_path`.
  - [x] Land `_POINTS_AT_DONE_AT_LANDING` with the measured population, date, owner and per-entry
        reason, plus the shrink assertion.
  - [x] Register the rule in `architecture.md` §Enforcement and extend `-77`'s anchors.
- [x] **Task 6 — The record, and the guard that watches records** (AC9, AC10)
  - [x] Run `-78`'s exported analyzers over this story file and the ledger before each commit.
  - [x] Full local suite + `mypy argus` + `bandit` + coverage; state that the evidence is
        Windows-only.
  - [x] Verify `sprint-status.yaml` at 1,264 lines / 1,264 CR.

---

## Dev Notes

### §0 — MEASURED AT `b8eaeee`, 2026-08-26. Re-derive before trusting.

#### §0.1 The tree

- `deferred-work.md`: 7,686 lines · **607,244 bytes** · **1 CR** · 0 CRLF · **169** canonical
  `- id: DF-…` entry blocks · **205** lines mentioning `target_story`.
- `sprint-status.yaml`: **1,264 lines / 1,264 CR** · **122** `development_status` keys, of which
  **119** are `done`. The only non-`done` keys are `epic-17: in-progress`,
  `17-5-nothing-points-at-a-closed-story: backlog` and `epic-17-retrospective: backlog`.
  ⛔ **This story is the last unstarted story in the plan.** Every story key it could point at is
  `done`, which is precisely why the defect class is at its maximum here.
- `argus/**` is byte-unchanged since `f738df0`, and `minions-dogfood-proof.md` cites
  `f738df0ce9d55f10c4b785e7046b12479454bf2d`. The dogfood artifacts are CURRENT at contexting.

#### §0.2 ⛔ THE COUNT IS NOT SIX. Measured partition of `- target_story:` fields.

Of the 169 canonical entry blocks, **70** have a `- target_story:` field that resolves to at least
one story key `sprint-status.yaml` records as `done`. Partitioned by the FORM of the field:

| partition | blocks | what it means |
|---|---:|---|
| **AFFIRMATIVE** — the field names a done story as the OWNER of remaining work | **47** | the real defect surface |
| **LANDMARK** — the field reads `NONE` / `the next story that…` / `coupled to…` and mentions a done story only as a reference point | **23** | ⛔ **not a violation.** A guard that reddens on these is measuring English, not pointers |

Of the **47** affirmative blocks, **24 blocks / 23 distinct ids** are not reported disposed by
`ledger_closed_ids`: `DF-1-7-B`, `DF-8-1-A`, `DF-AUD-APAA-C`, `DF-AUD-APAA-D`, `DF-10-4-B` (two
blocks), `DF-AUD-APAA-A`, `DF-11-2-A`, `DF-11-2-B`, `DF-11-4-A`, `DF-11-4-B`, `DF-11-4-D`,
`DF-12-1-A`, `DF-12-1-B`, `DF-12-1-C`, `DF-12-2-C`, `DF-12-2-D`, `DF-12-7-B`, `DF-6-6-A`,
`DF-13-2-A`, `DF-14-1-A`, `DF-14-3-D`, `DF-16-7-A`, `DF-16-7-B`, `DF-INV-VACUOUS-A`.

⛔ **The epic's "six" is a strict subset of twenty-three.** It is not wrong — it is the subset Epic 17
is competent to judge. **Seventeen further entries point at closed Epic 8-14 work and belong to epics
this story has no standing to reopen.** That is exactly why AC7 registers them instead of resolving
them.

**Exactly 7 entries name Story 6.2 in their `target_story`**, and the seventh is the one that must
not move:

| entry | field at | reads |
|---|---:|---|
| `DF-1-7-B` | `:174` | `6-2-full-python-ast-grounding-of-audited-deep-claims` — ⛔ **the one true pointer.** Do not touch |
| `DF-12-2-D` | `:3333` | *"6-2-style claim-grammar work — the story that gives the deep pass a declared…"* |
| `DF-12-3-A` | `:3400` | *"the same 6.2-style claim-grammar work `DF-12-2-D` already names"* |
| `DF-14-1-A` | `:4484` | *"**6-2** (full multi-construct AST grounding / dataflow provenance)"* |
| `DF-16-7-A` | `:5788` | *"**6.2** (`6-2-full-python-ast-grounding-of-audited-deep-claims`) — the full…"* |
| `DF-16-7-B` | `:6210` | *"**(a)** stays **6.2** with `DF-16-7-A`"* |
| `DF-INV-VACUOUS-A` | `:6259` | *"**6.2** (`argus` dataflow / scope-resolved grounding) — as a SCOPE CHANGE"* |

#### §0.3 The 2026-08-24 charter section already did half of this — and `AI-E18-10` named the residual

`deferred-work.md:7185`-`:7433` (*"Epic 17 / Epic 18 re-homing and scheduling — 2026-08-24"*) already
carries §(a)'s six-row re-homing table, §(b)'s scheduling table, the 2026-08-21 research correction,
and the four-module note. ⛔ **Do not re-file any of it — cite it.**

**What it did NOT do, and what this story owes**, in the Epic-18 retrospective's own words
(`AI-E18-10`, 2026-08-25): *"all six entries still read `target_story: NONE` in their own bodies
because §3.4 correctly forbids rewriting them, so the schedule is visible only in the 2026-08-24
proposal's table — a reader of the ledger alone cannot see it."* AC2's per-entry append is that
finding's remedy, and the ledger already has the right form for it: `DF-AUD-DETECT-D` at `:6726`,
`DF-INV-VACUOUS-B` at `:6331`, `DF-AUD-DETECT-E` at `:6807`, `DF-AUD-DETECT-F` at `:7000` — every one
a dated bullet appended **under the entry it disposes**.

#### §0.4 ⛔ `ledger_closed_ids` IS DEFECTIVE FOR THIS QUESTION, MEASURED

Run over the live ledger it returns **42** ids. Two entries this story handles are false positives:

⚠️ **THE VERB IS ELIDED AS `[v]` IN EVERY QUOTE BELOW, DELIBERATELY** (AC9). Reproducing it beside
the id would make this very table a closure claim against two entries it is documenting as OPEN —
the defect demonstrating itself inside its own evidence, for the twelfth time.

| id | line | why the extractor is fooled | truth |
|---|---:|---|---|
| `DF-13-5-A` | `:4752` | a FUTURE CONDITIONAL — *"… `[v]` when 13.5 records its outcome"* | **OPEN and UNSPENT** |
| `DF-13-5-A` | `:5752` | a NEGATION the lookbehind misses — *"Neither `[v]` anything."*; `_NEGATED` knows `not`/`never`/`cannot be`/`is not`/`none is`/`no entry is`/`un`, and **not** `Neither` | **OPEN and UNSPENT** |
| `DF-12-3-A` | `:4292` | a HALF-disposition — *"the DISCLOSURE half is `[v]` 2026-08-16; the MECHANISM half is re-recorded"* | **half open** |

⛔ **This is the ninth-through-eleventh instance of `DF-16-6-D`'s counted class, measured a third
time.** `DF-INV-LEDGER-A` (`:7324`) proposes fixing the **extractor**; `DF-16-6-D` (senior,
2026-08-23) says the opposite — *"the record is what is wrong, every single time"* — and also carries
an ordering hazard `DF-INV-LEDGER-A` did not know about: repairing the analyzer **unmasks** a
surviving instance and turns the full suite RED, so the record must be wrapped first. ⛔ **This story
reconciles neither and repairs neither.** It refuses to build `-80` on top of the contested predicate,
and records the measurement as evidence for whoever does reconcile them.

#### §0.5 The detector-audit entries are already disposed — the pointers are what is stale

`ledger_closed_ids` and the per-entry notes agree at HEAD:

| entry | state | disposing story / sha |
|---|---|---|
| `DF-AUD-DETECT-A` | terminal | Story 18.1 |
| `DF-AUD-DETECT-B` | terminal | Story 18.2 |
| `DF-AUD-DETECT-D` | terminal | Story 17.3, fix sha `2db5ce0` (`:6726`) |
| `DF-AUD-DETECT-E` | terminal | Story 18.3, fix sha `9e3fdc2` (`:6807`) |
| `DF-AUD-DETECT-F` | terminal | Story 18.4, fix sha `0ba6a98` (`:7000`) |
| `DF-AUD-DETECT-C` | **OPEN** (`:6664`, `target_story: NONE`) | ⛔ **not scheduled, not dispositioned.** `AI-E18-10` asks the Governance Owner for a destination |
| `DF-INV-VACUOUS-B` | terminal | Story 17.2, *moot-by-replacement* (`:6331`) |
| `DF-13-5-A` | **OPEN and UNSPENT** | 17.4's trigger observation at `:4920`-`:4970`; condition 1 did not fire, condition 2 `2026-11-22` not re-dated |

⛔ **So `epics.md`'s AC — "point `-A`/`-B`/`-E`/`-F` at Epic 18 and `-D` at 17.3, scheduling notes
only" — is now a request to point five entries at five closed stories.** Executing it literally would
CREATE the defect this story exists to end. AC3 replaces it with disposition pointers, and the
substitution must be recorded as a deliberate correction of the epic, not a quiet deviation.

#### §0.6 The module forward references: 12 sites, 7 modules — the epic names 5 across 4

**FORWARD — asserted as 6.2's FUTURE scope. These are the defect** (`epics.md` names the first five):

| # | site | text |
|---|---|---|
| 1 | `argus/detectors/provenance_scan.py:55` | *"real assertion provenance is Story 6.2's (`DF-14-1-A`)"* |
| 2 | `argus/audit/deep_pass.py:93-94` | *"That is Story 6.2's full claim-grammar grounding…"* |
| 3 | `argus/audit/deep_pass.py:314` | *"Full claim-grammar grounding is Story 6.2's"* |
| 4 | `argus/audit/deep_audit.py:23` | *"The full Python AST-grounding of deep claims is Story 6.2"* |
| 5 | `argus/audit/__init__.py:13` | *"The deep AST-grounding logic is Story 6.2."* |
| 6 | `argus/detectors/assertion_strength.py:64` | ⛔ **created by Story 17.3, 2026-08-25** — *"real assertion provenance is Story 6.2's"* |
| 7 | `argus/audit/deep_audit.py:103` | *"the later (6.2) AST-grounding validator will consume"* |
| 8 | `argus/audit/ports.py:81` | *"deferred to the 6.2-shared deep-audit pipeline"* |
| 9 | `argus/detectors/vacuous_test.py:6` | *"full multi-construct grounding is Story 6.2"* |
| 10 | `argus/detectors/vacuous_test.py:81` | *"Full dataflow/scope-resolved grounding is Story 6.2."* |
| 11 | `argus/detectors/vacuous_test.py:134` | *"real assertion provenance is Story 6.2's"* |
| 12 | `argus/detectors/vacuous_test.py:867` | *"Story 6.2 owns real assertion provenance"* |

⛔ **Site 6 is the finding that matters most.** The stale sentence was copied into a **brand-new
module by Story 17.3, one story before the story chartered to remove it**, in an epic whose charter
names the defect. That is not carelessness; it is `DF-16-6-D`'s lesson again — *"knowing about it does
not prevent it"* — and it is the strongest available argument for AC6's guard existing at all.

**NOT the defect — carve out by name:**

- **TRUE HISTORICAL:** `pipeline.py:9/35/43/55/115`, `pipeline_persist.py:13`,
  `pipeline_stages.py:138`, `verdict/prosecutor.py:29/50/227`. These record what 6.2 **did** and are
  correct.
- **BEHAVIOUR-BEARING** (⛔ **out of scope for a comment story; file, do not edit**):
  `ledger/depth_semantics.py:134/138` (`DEPTH_SEMANTICS` payload strings a user reads) and
  `ledger/recording.py:77` (a pydantic `Field(description=...)` that reaches the emitted schema —
  `tests/test_recording_schema.py` / `test_verdict_schema_bump.py` sit on it).
- **BORDERLINE, recorded not swept:** `ledger/coverage_ledger.py:27/171` and
  `ledger/depth_semantics.py:37/41` are stale in the OTHER direction — they defer to 6.2 work that
  6.2 actually delivered (`pipeline_stages.py:138`). A different defect; record it, do not fix it here.

**Headroom** (`_CEILING = 1200`): `provenance_scan.py` 1,099 · `vacuous_test.py` 897 ·
`deep_pass.py` 558 · `assertion_strength.py` 500 · `depth_semantics.py` 337 · `ports.py` 178 ·
`recording.py` 144 · `deep_audit.py` 112 · `audit/__init__.py` 20. All comfortable; a same-length
rewrite costs nothing.

#### §0.7 The dogfood tax is real and it is mandatory

`tests/test_dogfood_artifact_currency.py` (`TC-ArgusAgent-DOGFOOD-001-49`..`-52`) asserts:
*"`git diff --quiet <cited-sha> HEAD -- argus/` is empty"*. ⛔ **A one-character docstring edit under
`argus/**` reddens it.** The remedy is committed and named:
`python scripts/regenerate_dogfood_artifacts.py`, in its own commit, citing a truthful provenance sha
that is an ancestor of HEAD — Story 17.3's `8516297` and `7e72d91` are the two worked examples.

⚠️ **`README.md` / `CHANGELOG.md` are NOT affected.** `DN-17-3-16` moved them because the module COUNT
changed (95 → 96) and `TC-ArgusAgent-DOCS-001-54` re-derives it from a freshly built wheel. A comment
edit changes no file count and no entry count, so both files stay out of the write set. ⛔ **Verify
this rather than assume it** — if a figure moves, it is an AC10 escalation.

#### §0.8 Guard id allocation

Highest `TC-ArgusAgent-DOCS-001-*` in the tree: **`-79`**. Next free: **`-80`**. Host:
`tests/test_governance_record_integrity.py` (322 / 1200 lines), which already holds `-77`, `-78`,
`-79` and whose stated cohesion is *"every guard below closes over the governance documents rather
than over code"*. ⛔ **No id is renumbered** — `-77`..`-79` are cited from `architecture.md:648`/`:964`,
from `deferred-work.md` and from five test modules.

---

### §1 — Decisions taken at contexting (`DN-17-5-*`)

- **`DN-17-5-1` — the guard is `TC-ArgusAgent-DOCS-001-80` in the existing governance module.**
  *Rejected:* a new module (`-77`'s cohesion argument applies unchanged and the host has 878 lines of
  headroom); a new verification area (renumbering risk for zero benefit).
- **`DN-17-5-2` — the guard's population is the AFFIRMATIVE form of a canonical `- target_story:`
  field, and both narrowings carry positive controls.** *Rejected:* every line mentioning
  `target_story` (RED on 105 lines, most of them prose *about* staleness — a guard that reddens on
  its own documentation); every affirmative block without the disposing-story exclusion (RED on
  `DF-1-7-B`, the one true pointer in the file).
- **`DN-17-5-3` — openness is NOT decided by `ledger_closed_ids`.** Measured: false positives on two
  entries this story handles (§0.4). *Rejected:* reusing it (imports a contested, known-defective
  predicate); repairing it here (`DF-16-6-D` holds the senior contrary position AND an ordering
  hazard — reconciling them is a governance act, not a story task).
- **`DN-17-5-4` — the measured historical population lands in a dated, shrink-only registry with a
  named owner.** *Rejected:* mass re-homing 23 entries this story never verified (`AI-E12-3`);
  narrowing the population until green (Story 12.1's anti-pattern).
- **`DN-17-5-5` — the module set is WIDENED from the epic's 4 to the measured 7, and three reference
  classes are carved out by name.** *Rejected:* correcting only the 4 the epic names — it would leave
  site 6, the one created inside this very epic, in place; sweeping the behaviour-bearing strings —
  that is a behaviour change wearing a comment story's clothes.
- **`DN-17-5-6` — the dogfood regeneration is its own commit and is part of the story, not
  follow-up.** *Rejected:* folding it into the comment commit (17.3's precedent separates them, and a
  mixed commit makes the "no behaviour change" claim unverifiable by diff).
- **`DN-17-5-7` — Epic 17's outcome corrections are DATED APPENDS; the Epic-18 retrospective and the
  2026-08-21 research are not rewritten** (§3.4). The corrections live once, in `deferred-work.md`,
  naming the stale statements by line, with a dated note in `epics.md` in the form it already uses.
  *Rejected:* editing the retrospective (a signed record); leaving the claims standing (the task this
  story exists for).
- **`DN-17-5-8` — `scripts/precision_preregistration.py` stays BYTE-FROZEN**, including its now-false
  line 14. `TC-ArgusAgent-PRECISION-001-140` and the `f906d04` ancestry argument depend on it.
  ⛔ **Stated in the record so a later editor does not "correct" it into a RED suite.**
- **`DN-17-5-9` — the disposition-verb rule is mechanised, not remembered** (AC9), following Story
  17.3 §2.5's precedent, which caught its own first draft RED before it reached disk.
- **`DN-17-5-10` — `DF-AUD-DETECT-C` gets a corrected pointer and an owner, never a disposition.**
  Story 17.3 declined it explicitly; `AI-E18-10` assigns the destination decision to the Governance
  Owner. *Rejected:* dispositioning it here (it is a performance entry and this is not a performance
  story); leaving it pointing at nothing (`AI-E13-12`).
- **`DN-17-5-11` — `DF-13-5-A` stays OPEN and UNSPENT.** No round is spent, no member ratified, no
  third-party source fetched. 17.4's trigger observation at `:4920` is cited, never re-evaluated.

### §2 — Guardrails

#### §2.1 Declared write set

`_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (append only) ·
`_bmad-output/design-artifacts/ArgusAgent/epics.md` (dated correction note only) ·
`_bmad-output/design-artifacts/ArgusAgent/architecture.md` (§Enforcement registration) ·
`_bmad-output/design-artifacts/ArgusAgent/stories/17-5-nothing-points-at-a-closed-story.md` ·
`_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` ·
`tests/test_governance_record_integrity.py` ·
the 7 `argus/**` modules of §0.6 (comments/docstrings only) ·
the dogfood artifacts regenerated by `scripts/regenerate_dogfood_artifacts.py`.

⛔ **Nothing else.** Anything further is an AC10 escalation, recorded before it is taken.

#### §2.2 Frozen, and not negotiable

`scripts/precision_preregistration.py` · `successor-vacuity-predicate-specification.md` ·
`validation-corpus/**` including `successor/successor-reach-record.json` ·
`TC-ArgusAgent-PRECISION-001-135`..`-152` · `adjudication-record.json` · every retrospective ·
`research/technical-argusagent-stage-mismatch-measurement-2026-08-24.md` ·
`_UNBACKED_AT_LANDING`'s 17 rows · every `argus/**` line outside §0.6's forward set.

#### §2.3 Environment

Windows-only local gates; CI runs an ubuntu matrix. Every new file read passes `encoding="utf-8"`
explicitly — the artifact tree carries non-ASCII and an inherited host locale is the exact defect
class that turned a CI run red. No test may resolve a path by `os.sep` or assume a drive letter.
State in the record that the evidence is LOCAL.

#### §2.4 Grep the ledger before filing

`deferred-work.md` usually already knows. Cite prior art (`DF-16-6-D`, `DF-INV-LEDGER-A`,
`AI-E18-10`, `AI-E13-12`, `AI-E12-3`, `AI-E12-6`, `AI-E9-8`) or you will re-file it. Two of the
2026-08-24 audit session's three self-corrections would have been prevented by one grep of this file
before filing; that is recorded in §(d) of the 2026-08-24 charter section and it applies here too.

### §3 — Previous story intelligence

- **17.1** froze the criterion (`scripts/precision_preregistration.py`, `PREREGISTRATION_COMMIT_SHA`
  `f906d04`, `MAX_FALSE_ACCUSATION_EXPOSURE` 26). Byte-frozen; `TC-ArgusAgent-PRECISION-001-140` must
  not move. It assigned **every** re-homing and scheduling note to this story by name (`DN-17-1-9`).
- **17.2** specified `S1` and disposed of `DF-INV-VACUOUS-B` as moot-by-replacement. It wrote
  **exactly one** ledger entry and left the rest here, *"because splitting a re-homing across two
  stories is how an append-only ledger becomes unreadable."*
- **17.3** landed `S1` as **ADVISORY** code (`argus/detectors/assertion_strength.py`), disposed of
  `DF-AUD-DETECT-D` at `2db5ce0`, recorded a span-scan cost reduction (10,056 → 9,680 calls, −3.7%)
  as a disclosure with `DF-AUD-DETECT-C` untouched, and **recorded the hand-off to this story in
  terms**. Its §2.5 is the authoring rule AC9 mechanises. Its guard `-146` part (2) was later amended
  by operator decision under 17.4; a dated note on the 17.3 story file records it.
- **17.4** ran the measurement **once**: `UNEVALUABLE`; sealed contributing members **0** below a
  floor of **3**; `measured_precision` **null**; 1,032 walked / 0 skipped; S1-eligible **85** across
  **3** contributing members (minions 54, agent-smith 28, agent-markovich 3); 1 rule class. It
  recorded `DF-13-5-A`'s trigger as an OPEN observation with the round **UNSPENT**, and wrote exactly
  one ledger note. ⛔ **The story files of 17.1-17.4 are authoritative over `epics.md`, which predates
  them all.**

### §4 — Git intelligence

Last commits: `b8eaeee` (17.4 review PASS → done) · `f3f2bbd` (17.4 operator amendment + ledger
observation) · `5bf27ca` (17.4 measurement + guards) · `0b4bfd8` (17.4 producer) · `682b074` /
`7e72d91` / `f738df0` / `ea2c2f5` / `8516297` / `90b5235` / `2db5ce0` (17.3). **The commit shape to
copy is 17.3's:** one structural commit, one feature commit, one artifact-regeneration commit, one
record commit — each staging explicit paths. `8715b7f` was written by the **peer session** on this
same branch, which is the standing reason `git add -A` is forbidden.

### Project Structure Notes

- Story files live in `{implementation_artifacts}/stories/`, **not** at the artifacts root — the
  workflow's `default_output_file` default is overridden by the on-disk convention every prior story
  follows, and `TC-ArgusAgent-DOCS-001-78` globs `stories/*.md` to build its population.
- Story files are **LF-only** (0 CR). `deferred-work.md` is LF-only **except one lone CR**;
  `sprint-status.yaml` is CRLF. All three invariants are asserted, not assumed.
- New guards go in `tests/`, flat, one module per cohesive rule; `argus/**` is never edited to make a
  guard pass.
- `scripts/check_meta_drift.py` classifies Epic 17 (`CUTOFF_EPIC = 17`) and would read this story as
  process-derived. It is **advisory only** — no test and no CI job runs it — and `meta-drift-baseline.md`
  must **not** gain a row for it.

### References

- [Source: epics.md#Epic 17 — Story 17.5] — the ACs this story supersedes in three places, with the
  corrections recorded (AC3, AC4, AC5).
- [Source: deferred-work.md#Epic 17 / Epic 18 re-homing and scheduling — 2026-08-24] (`:7185`-`:7433`)
  — §(a) the six-row re-homing table, §(b) the scheduling table, the 2026-08-21 research correction,
  `DF-INV-WHEEL-A`, `DF-INV-LEDGER-A`.
- [Source: deferred-work.md#Deferred from: the 2026-08-24 detector-suite audit] (`:6377`-`:7184`) —
  `DF-AUD-DETECT-A`..`-F` and their dispositions.
- [Source: deferred-work.md] `:4292` `:4752` `:5752` (the extractor false positives) ·
  `:4920`-`:4970` (17.4's `DF-13-5-A` observation) · `:6331` `:6654` `:6726` `:6807` `:7000` (the
  disposition form to copy).
- [Source: epic-18-retro-2026-08-25.md#AI-E18-10] — the readability finding AC2 remedies; and `:480`,
  `:523`-`:527`, `:580`, the three stale Epic-17 statements.
- [Source: architecture.md#Enforcement — Ledger-claim cross-check enforcement] — the registration form
  AC8 follows.
- [Source: tests/test_governance_record_integrity.py] — `_CLOSURE_VERB`, `_NEGATED`, `_DF_ID`,
  `story_closure_claims`, `ledger_closed_ids`, `_UNBACKED_AT_LANDING` and its shrink assertion.
- [Source: tests/test_dogfood_artifact_currency.py] — the `git diff --quiet <sha> HEAD -- argus/`
  property and `REGENERATION_COMMAND`.
- [Source: stories/17-3-grade-what-the-assertion-constrains.md#§2.5] — the disposition-verb rule and
  the explicit hand-off to this story.
- [Source: stories/17-4-run-it-once-and-let-the-pre-registered-criterion-decide.md] — the frozen
  measurement and the carve-out naming this story's six re-homings.
- [Source: validation-corpus/successor/successor-reach-record.json] — `UNEVALUABLE`, and every figure
  AC5 corrects the documents against.

### Questions saved for the end (none block implementation)

1. `DF-INV-LEDGER-A` vs `DF-16-6-D` remains unreconciled and is a **Governance Owner** act, not a
   story task. This story records a third independent measurement of the class and takes no side
   beyond declining to build on the contested predicate.
2. `AI-E16-7` (the External adjudicator) is still unfilled. It is a stated precondition of Story 17.4,
   which has already run and recorded `UNEVALUABLE` without reaching it; it is **not** a precondition
   of this story.
3. Whether the 17 out-of-epic registered entries get a sweep of their own is the Epic-17
   retrospective's call, and `AI-E13-12` already says every `target_story: NONE` entry needs a
   destination before its epic closes.

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context), `bmad-dev-story` round 1 — implement. Baseline `b8eaeee`.

### Debug Log References

Five commits, each staging **explicit paths** (a peer session commits to this branch; `git add -A`
was never used, nothing was amended and nothing was rebased):

| # | sha | what |
|---|---|---|
| 1 | `c9d856f` | `docs` — the ledger dispositions and the `epics.md` corrections |
| 2 | `ca65230` | `fix` — the 12 module comment corrections (`Evidence-partition: none`) |
| 3 | `45faf41` | `chore` — the dogfood regeneration, its own commit, at provenance `ca65230` |
| 4 | `fc234da` | `test` — `TC-ArgusAgent-DOCS-001-80` and the `architecture.md` registration |
| 5 | *this* | `docs` — this record and the `sprint-status.yaml` transition |

⛔ **AC9 was MECHANISED, not remembered, and it was run before every one of those commits.** A
throwaway harness imported `-78`'s own exported analyzers and asserted, against
`git show b8eaeee:…deferred-work.md` as the baseline: `ledger_closed_ids` = **42 before, 42 after,
identical set, zero gained and zero lost**; `story_closure_claims` over this story file = **`()`**;
and, over `-78`'s whole `stories/*.md` population, zero unregistered unbacked claims and zero stale
`_UNBACKED_AT_LANDING` rows. That is why no acceptance criterion, no ledger note and no commit
message in this arc writes a disposition verb on a line that also carries a `DF-` id.

### Completion Notes List

#### The headline, stated first

⛔ **NOTHING THAT WAS OPEN AT `b8eaeee` WAS DISPOSED OF BY THIS STORY.** A pointer rewrite is not a
disposition. The honest tally, by outcome:

| outcome | count | which |
|---|---:|---|
| **DISPOSED** (an open entry ruled terminal here) | **0** | — |
| **RE-HOMED** to a live owner, entry STAYS OPEN | **6** | `DF-12-2-D`, `DF-12-3-A`, `DF-14-1-A`, `DF-16-7-A`, `DF-16-7-B`, `DF-INV-VACUOUS-A` |
| **LEFT OPEN with a corrected pointer**, no disposition | **1** | `DF-AUD-DETECT-C` |
| **DISPOSITION POINTER** recorded for an ALREADY-terminal entry | **5** | `DF-AUD-DETECT-A`/`-B`/`-D`/`-E`/`-F` |
| **LEFT BYTE-UNTOUCHED by rule** | **1** | `DF-1-7-B` — the one true pointer |
| **REGISTERED, not resolved** (shrink-only, owner XAgent007) | **43 rows / 40 ids** | `_POINTS_AT_DONE_AT_LANDING` |

#### AC1 — the population was RE-DERIVED, and §0.2 did not fully reproduce

Measured by execution at `b8eaeee` over the live `deferred-work.md` + `sprint-status.yaml`, never
transcribed. **169** canonical entry blocks; **150** carry a `- target_story:` field; **122**
`development_status` keys of which **119** `done`; **70** blocks whose own `- target_story:` line
resolves to ≥ 1 `done` story key; **7** entries naming Story 6.2. Those figures reproduce §0.2
exactly.

⚠️ **Three figures did NOT, and the drift is recorded with the lines that produce it** rather than
absorbed — §(a) of the ledger section carries the full reconciliation:

- **AFFIRMATIVE / LANDMARK measured 52 / 18**, against §0.2's **47 / 23**.
- **The not-reported-disposed subset measured 28 blocks / 26 ids**, against §0.2's *"24 blocks / 23
  distinct ids"* — and §0.2's own enumeration lists **24** distinct ids, two of which (`DF-10-4-B`,
  `DF-12-1-A`) carry two blocks each, so its list already implies 26 blocks. The prose figure and
  the list beneath it disagree; the measured set is a strict SUPERSET of the list.
- **Two ids §0.2 missed, named:** `DF-8-3-B` (`:652` → `8-4-tell-integrators-what-changed`) and
  `DF-14-3-H` (`:5285` → `13-5-re-measure-the-gate-against-the-corrected-instrument`). ⚠️ The second
  was **predicted in terms by `DF-16-5-A`'s own body at `:5820`** — *"Pinning it to a story nobody
  has written yet is how `DF-14-3-H`'s `target_story: 13-5` went stale"* — and it went stale anyway,
  because nothing was watching. That sentence is the single best argument for AC6's guard.
- ⚠️ **A fourth drift, small and worth one line because it makes a line-cited record
  unreproducible:** the ledger holds a **lone CR byte** inside a code span at line **5459**.
  `grep -n` does not treat it as a break; Python's `str.splitlines()` does. §0 mixes the two
  conventions — its `:6726` / `:6807` / `:7000` / `:7185` / `:6331` are `grep -n`, its `:5788` /
  `:6210` / `:6259` / `:5752` are `splitlines()`. This record and the ledger section use `grep -n`
  throughout and say so.

⛔ **The AC1 partition holds with nothing left over:** every one of the 52 affirmative blocks is
either dispositioned here (6), excluded by a stated narrowing the guard asserts by name
(`DF-1-7-B`), or registered in `_POINTS_AT_DONE_AT_LANDING` with a reason (49 pairs). No measured id
is absent from both.

#### AC2 / AC3 — the dispositions, in their own bodies

Each of the six carries a **dated append-only note under its own bullet block**, in the
`DF-AUD-DETECT-D` / `DF-INV-VACUOUS-B` form, naming its live owner (**XAgent007, Engineering
Lead**), its corrected destination (a scope change argued through `bmad-correct-course`, on
`DF-16-7-B`'s precedent — never a story or epic that has already run), and **what Epic 17 actually
delivered for it, which in every one of the six cases is nothing**. `DF-12-3-A`'s note states which
half is disposed (the DISCLOSURE half, 2026-08-16, `:4292`) and which half is open (the MECHANISM
half), so the entry's true state is readable without running an extractor.

⚠️ **`AI-E18-10`'s wording is corrected rather than repeated.** It records the six as *"still
read `target_story: NONE` in their own bodies"*. Measured: **not one of the six reads `NONE`** — all
six carry an AFFIRMATIVE pointer at 6.2 or at 6.2-style work, which is a **stronger** form of the
same defect. The substance of the finding reproduces exactly and its remedy is delivered.

`epics.md`'s scheduling AC is recorded as **DISCHARGED AND SUPERSEDED**, deliberately and on the
record: all five `DF-AUD-DETECT-*` entries were already terminal and all five stories are `done`, so
executing *"scheduling notes only"* literally would have pointed five entries at five closed stories
— creating the defect the story exists to end. Replaced by disposition pointers naming `2db5ce0`
(`-D`, honouring Story 17.3's recorded hand-off in its own terms), `9e3fdc2` (`-E`) and `0ba6a98`
(`-F`). `DF-AUD-DETECT-C` received a corrected pointer and a live owner **only**.

#### AC4 — 12 sites, 7 modules, no behaviour change

All 12 forward-reference sites of §0.6 reproduced at HEAD and all 12 are corrected to name the real
owner. ⛔ **`argus/detectors/assertion_strength.py:64` was created by Story 17.3 on 2026-08-25**
carrying the identical stale sentence — the defect reproducing itself one story before the story
chartered to end it, inside an epic whose charter names it. `git diff argus/` is **comment and
docstring lines only** (+35 / −17 across 7 files), the full suite is green, and
`argus/detectors/provenance_scan.py` is held **line-count-NEUTRAL at 1,099**, deliberately below the
1,100 band Story 17.3 also held it under. The three carve-outs are byte-identical.

⚠️ **Two scope notes, recorded rather than absorbed.**

1. **A THIRTEENTH forward-reference site §0.6 did not enumerate:** `argus/ledger/recording.py:68`,
   the docstring twin of the behaviour-bearing `:77`. It is a comment and would have been in scope.
   It was **deliberately NOT edited**: correcting it while the identical sentence stands four lines
   below in a pydantic `Field(description=…)` that reaches the emitted schema would leave the module
   internally inconsistent, which is worse than leaving both. Recorded in the ledger with its line
   so the pair moves together. ⛔ This is a DECISION, not an omission.
2. **One line was corrected that §0.6 did not list:** `argus/audit/deep_pass.py`'s *"Filed as
   `DF-12-2-D` with an owner and a target story."* It carries no `6.2` reference so it is not in the
   12, but leaving it would have left the module asserting a target story four lines under a
   sentence saying the work is unscheduled. It is inside the declared write set (§2.1 names the
   module), so it is a scope note and **not** an AC10 escalation.

`TC-ArgusAgent-DOGFOOD-001-49`..`-52` reddened exactly as predicted and were repaired by
`python scripts/regenerate_dogfood_artifacts.py` in its own commit at provenance `ca65230`, a real
ancestor of HEAD: 96 tracked source files (unchanged), total LOC **34,513 → 34,531 (+18)** — exactly
the comment delta. ⚠️ **`README.md` / `CHANGELOG.md` were VERIFIED not to move rather than assumed**
(§0.7): the wheel module count is 96 before and after, so `TC-ArgusAgent-DOCS-001-54` re-derives the
same figure and both files stay out of the write set. `DN-17-3-16` did not recur.

#### AC5 — Epic 17's actual outcome, as DATED APPENDS

All six stale surfaces are corrected once, dated, by document and line, in `deferred-work.md` §(e),
with two `> **Correction, 2026-08-26**` blocks in `epics.md` in the form it already uses at `:339`
and `:341`. ⛔ **The Epic-18 retrospective and the 2026-08-21 research were NOT rewritten** (§3.4) —
their stale statements are named by line, not edited. ⛔ **`scripts/precision_preregistration.py`
is BYTE-FROZEN and verified so (`git diff --quiet b8eaeee HEAD` is empty), including its now-false
line 14** — *"Epic 17 is about to move the verdict-eligible population"*. The record says this
explicitly, in the ledger and here, so a later editor cannot "tidy" the sentence into a RED
`TC-ArgusAgent-PRECISION-001-140`.

#### AC6 / AC7 / AC8 — the guard

`TC-ArgusAgent-DOCS-001-80`, in `tests/test_governance_record_integrity.py` (322 → **829** of
1,200), over five pure exported analyzers. **49 live violations, 49 registry pairs.**

- ⛔ **It never calls `ledger_closed_ids`.** The reason is measured, not argued, and was reproduced
  independently at `b8eaeee`: 42 ids, of which `DF-13-5-A` (`:4752` future conditional; `:5751` a
  `Neither …` negation the `_NEGATED` lookbehind does not know) and `DF-12-3-A` (`:4292`
  half-disposition) are false positives on entries this very story handles. **Instances 9–11 of
  `DF-16-6-D`'s counted class, measured a third time.** Neither `DF-INV-LEDGER-A` nor `DF-16-6-D` is
  reconciled or repaired here.
- **Both narrowings carry positive controls over synthetic input and an asserted count** — LANDMARK
  **18** blocks; disposing-story `DF-1-7-B` → Story 6.2 excluded **by name** in
  `_DISPOSING_STORY_POINTERS` and asserted there, so AC2's *"asserted by the guard's own registry,
  not left to a reviewer's memory"* is literally true.
- **An extra invariant that makes the narrowing safe**, and it is the drift of AC1 turned into an
  assertion: the AFFIRMATIVE population is **52 whether or not `DF-` ids are blanked** out of a
  field value before story references are resolved, even though the total moves 70 → 65 and the
  landmark count 18 → 13. If that stops holding, the guard is measuring the ledger's naming scheme
  rather than its pointers, and it goes red.
- **`AI-E11-1` discharged:** non-vacuity asserted first and at every stage (`> 0` done keys, `> 0`
  pointers, `≥ 100` pointers, `> 0` violations); the rule driven RED at the **real seam** against
  synthetic ledger fragments written under `tmp_path` and read back with `encoding="utf-8"` stated
  explicitly — ⛔ **never against the committed ledger**, which a peer session is appending to; and
  the adversarial variant **GENERATED** from the live 49-violation set with its count asserted.
  Driven RED three further ways in memory before commit (unregistered offender / stale registry row
  / narrowing removed): all three fire, and no mutation touched disk.
- **AC7:** the registry is dated **2026-08-26**, owned by **XAgent007 (Engineering Lead)**
  (`AI-E9-8`), reasons drawn from a closed two-value vocabulary the guard asserts, and it **can only
  shrink** — `-80` fails if a registered pair becomes clean. Both alternatives are rejected on the
  record. The unverified remainder is **40 distinct ids** spanning Epics 5–14 plus the
  `DF-AUD-APAA-*` family — wider than §0.2's *"seventeen"*, which is itself a consequence of the
  wider measured population.
- **AC8:** `architecture.md` §Enforcement gains a **Stale-target-story enforcement** block in the
  established rule-text · enforcing-module · test-ids form, and `-77`'s anchor tuple is extended
  **additively** — four new anchors, no existing anchor removed, `len(anchors)` 22 → 26, `>= 15`
  still asserted. ⛔ **No id was renumbered.**

#### AC10 — invariants, staging, environment

- `deferred-work.md`: **607,244 → 647,941 bytes**, **1 CR / 0 CRLF** before and after, **pure append
  `+479 / −0`**. `epics.md`: pure append `+46 / −0`, CRLF uniform (3,717 → 3,763 = CR count).
  `architecture.md`: `+2 / −0`, CRLF uniform (1,416 → 1,418). `sprint-status.yaml`: **1,264 lines /
  1,264 CR**, verified after every edit; only this story's status value and `last_updated` moved.
  Each `argus/**` module's own line-ending convention was preserved byte-for-byte.
- **Staging:** every commit staged explicit paths. ⛔ `git add -A` was never used; nothing authored
  by the peer session was amended, rebased or touched.
- **Portability:** every file read in new code passes `encoding="utf-8"` explicitly; no new test
  resolves a path by `os.sep` or assumes a drive letter; the guard's synthetic fixtures carry
  non-ASCII deliberately so a locale-dependent read would fail rather than pass quietly.
- ⚠️ **THE EVIDENCE IS LOCAL (Windows).** This branch is unpushed, `git branch -r --contains HEAD`
  is empty, and there is **no CI evidence at any sha in this arc**. CI runs an ubuntu matrix
  (`DF-INV-DELIVERY-A` / `AI-E16-3`).
- **Write set:** `git diff --name-only b8eaeee HEAD` returns exactly §2.1's declared set and nothing
  else. ⛔ **No AC10 escalation was required.** §2.2's frozen list is verified byte-unchanged:
  `scripts/precision_preregistration.py`, `validation-corpus/**` (including
  `successor/successor-reach-record.json`), `adjudication-record.json`, every retrospective, the
  2026-08-24 research document, `_UNBACKED_AT_LANDING`'s 17 rows, and every `argus/**` line outside
  §0.6's forward set.
- ⛔ **`DF-13-5-A` stays OPEN and UNSPENT** — `branch_taken` NEITHER, `members_ratified` NONE,
  `round_state` UNSPENT, `protocol_edit` NONE, the `2026-11-22` backstop NOT re-dated. No corpus
  member ratified, no third-party source fetched, no row adjudicated, no finding promoted, and
  `meta-drift-baseline.md` gained no row.

#### Local gates (LOCAL, Windows only — no CI evidence at any sha in this arc)

`python -m pytest` — **1,760 passed / 0 failed** in 276.89 s · `python -m mypy argus` — **Success,
96 source files** · `python -m bandit -r argus --severity-level medium` — **exit 0** ·
`--cov=argus --cov-fail-under=80` — **95.87 %**.

### File List

| path | change |
|---|---|
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | modified (pure append: six per-entry notes, the `DF-AUD-DETECT-C` note, and the dated *"Story 17.5 dispositions — 2026-08-26"* section) |
| `_bmad-output/design-artifacts/ArgusAgent/epics.md` | modified (two dated `Correction, 2026-08-26` blocks; pure append) |
| `_bmad-output/design-artifacts/ArgusAgent/architecture.md` | modified (§Enforcement — Stale-target-story enforcement) |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` | modified (regenerated) |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` | modified (regenerated) |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` | modified (regenerated) |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | modified (this story's status value + `last_updated` only) |
| `_bmad-output/design-artifacts/ArgusAgent/stories/17-5-nothing-points-at-a-closed-story.md` | modified (this record) |
| `tests/test_governance_record_integrity.py` | modified (`TC-ArgusAgent-DOCS-001-80`, five exported analyzers, `_DISPOSING_STORY_POINTERS`, `_POINTS_AT_DONE_AT_LANDING`; `-77` anchors extended) |
| `argus/detectors/provenance_scan.py` | modified (comment only, line-count neutral) |
| `argus/detectors/assertion_strength.py` | modified (comment only) |
| `argus/detectors/vacuous_test.py` | modified (comments only) |
| `argus/audit/deep_pass.py` | modified (comments only) |
| `argus/audit/deep_audit.py` | modified (comments only) |
| `argus/audit/ports.py` | modified (comment only) |
| `argus/audit/__init__.py` | modified (comment only) |

### Change Log

| date | version | change | by |
|---|---|---|---|
| 2026-08-26 | 0.1.0 | Contexted at `b8eaeee`; `backlog` → `ready-for-dev`. | `bmad-create-story` (Opus 5) |
| 2026-08-26 | 0.2.0 | Round 1 implement. Six entries RE-HOMED in their own bodies with live owners; `DF-AUD-DETECT-C` given a corrected pointer and an owner only; five already-terminal entries given disposition pointers replacing the superseded scheduling AC; Epic 17's `UNEVALUABLE` outcome recorded against six surfaces as dated appends; 12 forward references corrected across 7 `argus/**` modules with the dogfood artifacts regenerated in their own commit; `TC-ArgusAgent-DOCS-001-80` landed with a dated shrink-only 49-pair registry and registered in `architecture.md` §Enforcement. **Nothing open was disposed of.** `ready-for-dev` → `in-progress` → `review`. | `bmad-dev-story` (Opus 5) |
