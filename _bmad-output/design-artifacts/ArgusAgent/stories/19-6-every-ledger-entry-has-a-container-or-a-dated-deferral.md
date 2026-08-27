---
baseline_commit: 3696e44
---

# Story 19.6: Every ledger entry has a container or a dated deferral

Status: done

<!-- Contexted 2026-08-26 at HEAD `3696e44` (branch `docs/merge-strategy-decision`, 37 ahead of
     `origin/master`, working tree CLEAN) by the create-story workflow (Opus 5).

     EVERY FIGURE IN §0 WAS READ OFF THIS TREE BY EXECUTION at `3696e44`. The guard's own exported
     analyzers were IMPORTED and run against the live ledger and the live sprint status —
     `done_story_keys`, `ledger_target_pointers`, `is_affirmative_target`, `named_done_stories`,
     `stale_target_pointers` — rather than re-implemented here, which is the same one-derivation
     obligation this story is about (`AR7` / `AI-E17-5`).

     ⛔⛔ THE FINDING THAT CHANGES WHAT THIS STORY IS: **THE REGISTRY HAS EXACTLY ONE CLEAN EXIT,
     AND IT IS NOT "RE-HOME THE POINTER".** §0.4 works the mechanism through. A dev that reads
     `epics.md`'s *"the registry shrinks by exactly the entries that gained a container"* as a
     shrink TARGET will start rewriting `target_story` fields, and every one of those rewrites
     destroys the evidence §3.4 exists to protect. ⛔ **THE SHRINK IS AN OUTCOME, NEVER A TARGET,
     AND IT MAY LEGITIMATELY BE ZERO.**

     TWO PREMISES CORRECTED AGAINST DOCUMENTS WRITTEN EARLIER TODAY:

       (1) §0.5 — ⛔ **`bmad-loop-sweep` DOES NOT APPLY TO THIS LEDGER, and
           `sprint-change-proposal-2026-08-26.md` §3.3 is WRONG to recommend it.** That skill
           parses `### DW-<n>:` blocks with a `status:` line. Measured at HEAD: this ledger holds
           **ZERO** `### DW-` blocks and **166** `- id: DF-` blocks. It is also automation-only
           (`BMAD_LOOP_MODE=1`) and refuses to run otherwise. Its `--migrate` mode would rewrite
           the ledger into a format `tests/test_governance_record_integrity.py` — the ONLY guard
           that parses this file — cannot read. ⛔ **Do not run it. Do not migrate.**

       (2) §0.3 — ⛔ **`DF-AUD-DETECT-C` IS NOT ONE OF THE 46.** `AI-E17-7` names seven entries;
           six are registry-bound and the seventh is not, because Story 17.3 already gave it a
           corrected pointer and a live owner, so it names no `done` story and the guard never
           sees it. The population is **47 entries to verify, of which 46 are registry-bound**.

     ⛔ NOTHING HERE CLOSES AN ENTRY BY ARGUMENT. `AI-E12-3` — *resolving entries in prose rather
     than against evidence* — is the named defect of this story, and it was committed once already
     inside the story written to end it. Every disposition carries an executed command and its
     output, or it is not a disposition. -->

## Story

As the **Engineering Lead**,
I want **every ledger entry whose `target_story` points at a closed story verified against the actual codebase, and given either a destination that exists or a dated deferral naming who accepted it**,
so that **work with no container is visible as such, instead of parked behind a pointer that looks live and is not.**

### What this story IS

The **verification**, and the record of it. For each of 47 entries: read the entry, read the code
it names, run something that decides whether the defect is still there, and write down the answer
with the command that produced it.

Its deliverable is three things:

1. a **verification record** — per entry: still-open / already-resolved / blocked / needs-a-human,
   each with executed evidence;
2. **dated dispositions in the ledger**, append-only, for the entries the evidence decides;
3. a **registry that shrank by exactly what the evidence moved** — and by nothing else.

### What it is NOT

⛔ **It is not a shrink exercise.** See §0.4. The registry's only clean exit is
`_DISPOSING_STORY_POINTERS`, and an entry qualifies for it only when the story it points at
genuinely discharged it. ⛔ **A zero shrink with 47 verified entries is a PASS. A large shrink
achieved by rewriting pointers is a FAIL.**

⛔ **It is not a re-homing.** `AI-E12-3` forbids mass re-homing, and the registry comment already
records that both alternatives were considered and rejected on the record: *mass re-homing the 26
measured ids is `AI-E12-3`; narrowing the population until it goes green is Story 12.1's named
anti-pattern.*

⛔ **It is not a `target_story: NONE` sweep.** The registry comment is explicit: the remedy is a
live owner — *"**XAgent007 (Engineering Lead)**, never `target_story: NONE` alone."*

⛔ **It is not a sweep-skill run.** §0.5.

⛔ **It does not touch the six `"17-5"` entries' `target_story` fields.** Story 17.5 deliberately
left them unrewritten so the stale pointer survives as evidence. That decision stands.

---

## §0 — PREMISES MEASURED BY EXECUTION at HEAD `3696e44`

⛔ **Task 0 re-measures every row before a line is written.** `AI-E17-11`: **"a row moved" is a
first-class outcome that is REPORTED, not absorbed.**

### §0.0 The tree, the paths, the baseline

| fact | value |
|---|---|
| HEAD | `3696e44` — *chore(19-1): context the ratification package story* |
| branch | `docs/merge-strategy-decision`, **37 ahead** of `origin/master` |
| working tree | **clean** |
| PR | **#9** open against `master` |
| CI | ⛔ **never ran** — GitHub Actions major outage from **2026-08-26 15:11:58 UTC**; every queued run recorded `steps: 0` |
| local suite | **1,760 tests, exit 0**, Windows only |

### §0.1 The partition — reproduced exactly, and UNMOVED from landing

Run through the guard's own exported analyzers at HEAD:

| quantity | measured | landing constant | moved? |
|---|---:|---:|---|
| `target_story` fields parsed | **150** | 150 | no |
| …that resolve to ≥1 `done` story | **70** | — | — |
| **AFFIRMATIVE** (names a story as OWNER) | **52** | `_AFFIRMATIVE_BLOCKS_AT_LANDING` = 52 | no |
| **LANDMARK** (no-owner / indefinite selector) | **18** | `_LANDMARK_BLOCKS_AT_LANDING` = 18 | no |
| LANDMARK with `DF-…` ids blanked | **13** | `_LANDMARK_BLOCKS_AT_LANDING_IDS_BLANKED` = 13 | no |
| violations = registry pairs | **49 = 49** | 49 | no |
| distinct violating entry ids | **46** | — | — |
| `_DISPOSING_STORY_POINTERS` | **1** | 1 | no |
| `done` STORY keys in sprint status | **86** | — | — |
| canonical `- id: DF-` blocks | **166** | — | — |

### §0.2 The 46, and where they come from

Grouped by originating epoch: **`12`×8 · `8`×8 · `10`×7 · `11`×7 · `14`×5 · `AUD`×5 · `13`×2 ·
`16`×2 · `5`,`6`,`7`,`9`,`INV`×1 each.**

Full list (registry order): `DF-10-2-A`, `DF-10-3-A`, `DF-10-4-A`, `DF-10-4-B`, `DF-10-4-C`,
`DF-10-4-D`, `DF-11-2-A`, `DF-11-2-B`, `DF-11-4-A`, `DF-11-4-B`, `DF-11-4-D`, `DF-11-5-A`,
`DF-11-5-C`, `DF-12-1-A`, `DF-12-1-B`, `DF-12-1-C`, `DF-12-2-C`, `DF-12-2-D`, `DF-12-3-A`,
`DF-12-7-B`, `DF-13-1-A`, `DF-13-2-A`, `DF-14-1-A`, `DF-14-2-A`, `DF-14-2-B`, `DF-14-3-D`,
`DF-14-3-H`, `DF-16-7-A`, `DF-16-7-B`, `DF-5-1-A`, `DF-6-6-A`, `DF-7-2-A`, `DF-8-1-A`, `DF-8-2-A`,
`DF-8-2-B`, `DF-8-3-A`, `DF-8-3-B`, `DF-8-4-A`, `DF-8-5-A`, `DF-9-2-C`, `DF-AUD-APAA-A`,
`DF-AUD-APAA-C`, `DF-AUD-APAA-D`, `DF-AUD-APAA-E`, `DF-AUD-APAA-F`, `DF-INV-VACUOUS-A`.

Six carry reason `"17-5"` (dispositioned, pointer deliberately unrewritten): `DF-12-2-D`,
`DF-12-3-A`, `DF-14-1-A`, `DF-16-7-A`, `DF-16-7-B`, `DF-INV-VACUOUS-A`.
**Forty-three carry `"unverified"` — registered, NOT resolved, never measured against the code.**

### §0.3 ⛔ `DF-AUD-DETECT-C` IS NOT IN THE 46 — the population is 47

`AI-E17-7` lists seven. Six are in the registry. `DF-AUD-DETECT-C` is not, and its absence is
correct: Story 17.3 gave it a corrected pointer and a live owner, so it names no `done` story and
`-80` never sees it. ⛔ **It still needs verifying** — a live owner is not a disposition — but its
verification cannot and must not change the registry.

### §0.4 ⛔⛔ THE REGISTRY'S ONLY CLEAN EXIT — read this before touching anything

`-80` fails in **both** directions: on any affirmative stale pointer **not** listed, and on any
listed pair that has **become clean**. A pair becomes clean in exactly three ways:

| # | mechanism | verdict |
|---|---|---|
| 1 | the pair is added to **`_DISPOSING_STORY_POINTERS`** — narrowing 2, *"an entry whose `target_story` names the story that DISCHARGED it"* | ✅ **THE ONLY LEGITIMATE EXIT.** Requires evidence that the named story genuinely discharged the entry, in `DF-1-7-B`'s shape: the story file, the retrospective and the shipped code all record it |
| 2 | the `target_story` field is **rewritten** to a live destination | ⛔ **FORBIDDEN for the six `"17-5"` entries** — §3.4 evidence immutability; the stale pointer survives *as evidence*, deliberately |
| 3 | the pointer is rewritten into a **LANDMARK** form so `is_affirmative_target` returns `False` | ⛔ **FORBIDDEN** — the registry comment names it: *"never `target_story: NONE` alone"*. It is also Story 12.1's anti-pattern in miniature: narrowing the population until it goes green |

⛔ **THEREFORE: THE SHRINK IS AN OUTCOME OF THE EVIDENCE, NEVER A TARGET.** If all 46 are still
genuinely open, the registry shrinks by **zero** and this story has still succeeded — because its
deliverable is the *verification record*, and 43 of these have never been checked against the code
at all.

### §0.5 ⛔ `bmad-loop-sweep` DOES NOT APPLY — and the proposal that recommended it was wrong

| fact | measured |
|---|---|
| `### DW-<n>:` blocks in this ledger | **0** |
| `- id: DF-` blocks | **166** |
| guards parsing the ledger | **exactly one** — `tests/test_governance_record_integrity.py` |
| skill gate | automation-only; refuses unless `BMAD_LOOP_MODE=1` |

The skill triages `### DW-` blocks with a `status:` line. This ledger has none. Its `--migrate`
mode would rewrite the file into a format the one guard that reads it cannot parse.
⛔ **Do not run it. Do not migrate.** `sprint-change-proposal-2026-08-26.md` §3.3 says *"`bmad-loop-sweep`
already exists to produce exactly this partition and should be used rather than re-derived"* —
**that sentence is false and is corrected here.** The partition is produced by the guard's own
exported analyzers, which is where §0.1's figures came from.

### §0.6 Byte invariants — re-measured

| file | CRLF | lone LF | lone CR |
|---|---:|---:|---:|
| `deferred-work.md` | **0** | **8,225** | **1** — line **5569**, byte **425,623** |
| `epics.md` | 3,903 | 0 | 0 |
| `sprint-status.yaml` | 1,402 | 0 | 0 |

⛔ **`deferred-work.md` is LF-uniform. Edit in BINARY MODE** — text mode eats the lone CR, and a
"normalisation" to CRLF would rewrite all 8,225 line endings. ⛔ **Re-measure before AND after every
write, and record both.** `grep -n` and `splitlines()` agree the CR is at 5569 and disagree only on
the TOTAL (8,225 vs 8,226) — state which view any line citation used (`AI-E17-10`).

### §0.7 Next free ids

`PRECISION-001-`**153** · `DOCS-001-`**81** · `DETECT-001-`**153** · `AUDIT-001-`**75**

### §0.8 ⛔ GUARDS THIS STORY'S OWN DELIVERABLE WOULD RED (`AI-E17-1`)

| guard | fires when |
|---|---|
| `TC-ArgusAgent-DOCS-001-80` | **both directions** — a new stale pointer appears, or a registered pair becomes clean without its registry line being removed in the same commit |
| `TC-ArgusAgent-DOCS-001-79` | the ledger fails to dispose an entry this story names |
| `TC-ArgusAgent-DOCS-001-22` | a companion worklist is named to match `sprint-change-proposal-*.md` or `epic-*-retro-*.md`. ⛔ **Name it so it matches neither** |

### §0.9 ⛔ THE SIX NON-VACUITY FLOORS BAKED INTO `-80` — every one is a tripwire

`-80` will go RED if this story's edits move any of these, and **that is the guard working**:

1. `len(pointers) > 0` — the extractor found something
2. `len(pointers) >= 100` — *"the ledger carried 150 at landing and a collapse here makes this guard silent rather than green"*
3. `len(landmark) == 18` · 4. `len(affirmative) == 52` · 5. `len(blanked_landmark) == 13`
6. `len(violations) > 0` — *"ZERO stale pointers found. Either the analyzers stopped extracting or the registry below is entirely dead weight"*

⛔ **Constants 3–5 are LANDING MEASUREMENTS, not invariants.** If the evidence legitimately moves
one, it is updated **with its new measurement recorded** — never nudged to make a run green.

---

## §1 — THE DECISIONS THIS STORY MAKES, AND WHY

### §1.1 Verification is by EXECUTION, per entry, or it does not count

Every disposition carries the command and its output. **Rejected alternative:** reading the entry
and the code and judging. **Why rejected:** that is `AI-E12-3` verbatim — *resolving entries in
prose rather than against evidence* — and the retrospective records it being committed once
already, inside the story written to end it.

### §1.2 Four outcomes, closed vocabulary

`STILL-OPEN` · `ALREADY-RESOLVED` · `BLOCKED` · `NEEDS-A-HUMAN`. An unregistered outcome raises,
in `CRITERION_OUTCOMES`' shape. ⛔ `ALREADY-RESOLVED` is the **only** one that can feed
`_DISPOSING_STORY_POINTERS`, and only with the three-way evidence of the `DF-1-7-B` shape.

### §1.3 The ledger edits are APPEND-ONLY

Dated notes under the existing bullet block, in the `DF-12-2-D` / `DF-AUD-DETECT-D` form already in
the file. ⛔ **`id`, `origin_story`, `owner`, `category`, `severity` and `target_story` are left
unedited** so the stale pointer stays readable as evidence of when it was written.

### §1.4 What this story does NOT fix

The gate stays `BLOCKED`. `protocol_cleared` stays `False`. `DF-13-5-A` stays OPEN and UNSPENT.
The External adjudicator stays unfilled. No corpus member is ratified. `AI-E17-3` is untouched.

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ The registry line and the ledger note must land in the SAME commit

`-80` closes in both directions. An entry that gains a disposition without its registry line
removed reds `master`; a registry line removed without the disposition reds it equally. Same
discipline as `TC-ArgusAgent-DOCS-001-22`'s document-and-line pairing.

### §2.2 ⛔ Guard vacuity — this project's signature defect

Every new assertion carries a non-vacuity precondition. §0.9 is the worked example, already in the
file: six floors, each with a sentence explaining what silence would look like.

### §2.3 ⛔ The tree is SHARED

A peer session commits to this branch. Stage by **explicit path**; never `git add -A`. Disclose any
carried peer file **by name** in the commit message (`AI-E17-10`; 5-for-5 across Epic 17's 33
commits, zero collisions).

### §2.4 ⛔ Windows-only gates, and CI is DOWN

A green local suite has already shipped POSIX-only bugs to master, and PR #9 currently has **no CI
result at all**. State the platform. Do not record "gates green" as cross-platform evidence.

### §2.5 47 entries is a scope risk, and the fix loop is not the place to discover it

`AI-E17-9`: Story 17.5 burned all three fix rounds on Low docs-only findings. If the verification
cannot be completed in one pass, **partition it and say so in the story record** rather than
half-verifying all 47.

---

## §3 — AC ↔ TASK MAP

| AC | Tasks |
|---|---|
| AC1 — all 47 verified by execution | Task 0, Task 1, Task 2 |
| AC2 — dispositions are append-only and evidence-backed | Task 3 |
| AC3 — the registry shrinks by exactly the evidence | Task 4 |
| AC4 — the guard stays honest | Task 4, Task 5 |
| AC5 — byte invariants, scope, portability | Task 5 |
| AC6 — escalate, do not decide | all |

---

## Acceptance Criteria

### AC1 — EVERY ONE OF THE 47 IS VERIFIED AGAINST THE CODE, BY EXECUTION

1. The record carries **47 rows** — the 46 registry ids plus `DF-AUD-DETECT-C` — each with one of
   the four outcomes of §1.2.
2. ⛔ Each row carries **the command that decided it and that command's output**. A row whose
   evidence is prose is a failure, not a gap (`AI-E12-3`).
3. The six `"17-5"` rows are verified like the rest; their prior disposition is **not** evidence of
   resolution — it is a corrected pointer on an entry that **stays open**.
4. A companion worklist sits beside the record in the `blocking-worklist.md` house form, named to
   match **neither** `-22` glob (§0.8).

### AC2 — DISPOSITIONS ARE APPEND-ONLY AND CHANGE NO EXISTING FIELD

1. Every ledger edit is a **dated append-only note** under the existing block.
2. ⛔ `id`, `origin_story`, `owner`, `category`, `severity` and `target_story` are **byte-unchanged**
   for every entry, proven by `git diff`.
3. `deferred-work.md` is edited in **binary mode**; byte invariants re-measured **before and after**
   and both recorded (§0.6).

### AC3 — THE REGISTRY SHRINKS BY EXACTLY THE EVIDENCE, AND BY NOTHING ELSE

1. A pair leaves `_POINTS_AT_DONE_AT_LANDING` **only** by moving to `_DISPOSING_STORY_POINTERS`,
   and only with the `DF-1-7-B` three-way evidence (§0.4).
2. ⛔ **No `target_story` field is rewritten to achieve a shrink.** No `target_story: NONE` is
   introduced.
3. The registry line and its ledger note land in the **same commit** (§2.1).
4. ⛔ **A shrink of ZERO is an acceptable result** and must not be argued around.

### AC4 — THE GUARD STAYS HONEST

1. `-80` is green at the end, in both directions.
2. If any of §0.9's constants 3–5 legitimately moved, it is updated **with the new measurement
   recorded in the story** — never nudged to make a run green.
3. ⛔ **No assertion in `-80` is weakened, reworded, exempted or narrowed**, and no
   `_EXCLUDED_BY_DESIGN`-style escape is added.

### AC5 — SCOPE, PATHS, PORTABILITY

1. `argus/**` is **byte-unchanged** — this story writes no production code.
2. `precision-validation-protocol.md`, `adjudication-record.json` and `tests/corpus/_manifest.py`
   are byte-unchanged.
3. Paths portable: no `\\`, no drive letters in committed code.
4. Full suite run; ⛔ **state the platform**.

### AC6 — ESCALATE, DO NOT DECIDE

1. An entry whose resolution needs an operator ruling → `NEEDS-A-HUMAN`, with the question stated.
   ⛔ **Do not answer it.**
2. If verifying an entry would require ratifying a member, fetching source, or adjudicating a
   finding — **STOP**. Those are 19.2 and 19.4.
3. If the 47 cannot be completed in one pass, **partition and report** (§2.5).
4. Scope widening is escalated and **recorded before the write is taken** (`DN-17-5-12`'s form,
   and `AI-E17-6`: a `[Defer]` finding whose file is already in the write set defaults to
   `[Patch]`).

---

## Tasks & Subtasks

### ⛔ Task 0 — RE-MEASURE §0 BEFORE WRITING ANYTHING (AC1.1, AC4.2)

- [x] Re-run the guard's exported analyzers; reproduce every row of §0.1.
- [x] Re-confirm `DF-AUD-DETECT-C` is absent from the violations (§0.3).
- [x] Re-confirm 0 `### DW-` blocks / 166 `- id: DF-` blocks (§0.5).
- [x] Re-measure the byte invariants (§0.6) and the next free ids (§0.7).
- [x] ⛔ Report **every** row — moved and unmoved — with its command.

### Task 1 — THE DERIVATION SEARCH, RECORDED (`AI-E17-5`)

- [x] Grep `argus/` and `scripts/` for any existing derivation of "is this entry still open".
- [x] Record command + result **before** writing any new analyzer.
- [x] ⛔ Reuse `stale_target_pointers` and friends; do not re-implement the partition.

### Task 2 — VERIFY THE 47 (AC1)

- [x] Per entry: read the block, read the code it names, run something that decides.
- [x] Record outcome + command + output.
- [x] `NEEDS-A-HUMAN` for anything needing a ruling — state the question, do not answer it.

### Task 3 — THE DISPOSITIONS (AC2)

- [x] Append-only dated notes, binary mode, invariants re-measured before and after.
- [x] ⛔ `git diff` proving no existing field moved.

### Task 4 — THE REGISTRY (AC3, AC4)

- [x] Move only `ALREADY-RESOLVED` pairs with three-way evidence to `_DISPOSING_STORY_POINTERS`.
- [x] Remove exactly those from `_POINTS_AT_DONE_AT_LANDING`, same commit.
- [x] Run `-80`; confirm green both directions; record it.
- [x] ⛔ If the shrink is zero, **say so plainly** and move on.

### Task 5 — GATES AND HAND-OFF (AC5)

- [x] `git diff --stat` proving `argus/**` and the three frozen artifacts are untouched.
- [x] Full suite; state the platform.
- [x] Stage by explicit path; disclose carried peer files by name.

### Review Findings

**Method.** Blind Hunter + Edge Case Hunter + Acceptance Auditor, run adversarially against
`ffffcef..fcff0ca`. Independently re-executed 12+ of the 47 verification commands byte-for-byte
against the live tree (not just read), re-derived the byte invariants for `deferred-work.md`
programmatically, ran the guard's own exported analyzers (`ledger_target_pointers`,
`stale_target_pointers`, `_POINTS_AT_DONE_AT_LANDING`, `_DISPOSING_STORY_POINTERS`) directly, and
ran the full suite twice (both green, exit 0). AC1, AC2, AC4, AC5 and AC6 all check out — see
detail below. **AC3 does not.**

- [x] [Review][Patch] AC3 is violated — the registry under-shrank by at least four pairs that
  clear `DF-1-7-B`'s own three-way bar [tests/test_governance_record_integrity.py:554-608] —
  `DF-8-1-A` → `8-3-plain-english-report-stops-describing-impossible-state`, `DF-8-3-B` →
  `8-4-tell-integrators-what-changed`, `DF-8-4-A` → `9-2-ship-distribution-another-repo-can-actually-resolve`,
  `DF-8-5-A` → `9-2-ship-distribution-another-repo-can-actually-resolve`. For every one of these
  four: (a) the ledger's own append-only closure note already names the discharging story by the
  same `closed_by`/`status`-line shape as `DF-1-7-B`'s; (b) that story's own file explicitly
  closes the id against the SAME `target_story` already registered (e.g.
  `stories/9-2-ship-distribution-another-repo-can-actually-resolve.md:729,731` — `"DF-8-5-A |
  CLOSED here (AC7) | target_story: 9-2"`, `"DF-8-4-A | CLOSED here (AC10) | target_story: 9-2"`);
  and (c) the epic retrospective independently corroborates the closure (`epic-8-retro-2026-08-08.md:21`
  — *"2 closed inside the epic (`DF-8-1-A` by 8.3, `DF-8-3-B` by 8.4)"*; `epic-9-retro-2026-08-09.md:22,44,163`
  — *"4 closed inside the epic"* naming `DF-8-5-A`/`DF-8-4-A` explicitly). This is the exact
  `DF-1-7-B` shape §0.4 defines as the registry's only clean exit, yet none of the four was
  admitted to `_DISPOSING_STORY_POINTERS`. The story's own Task 4 table lumps all four into a
  "12 others | — | — | ✅ | ❌" row whose dashes mean the story-file/retrospective legs were never
  actually checked for them — `DF-8-1-A` was even individually flagged in the JSON record as a
  *"REGISTRY-EXIT CANDIDATE pending three-way evidence"* and then never followed up. This directly
  contradicts AC3.1 ("...only with the `DF-1-7-B` three-way evidence") and the Completion Notes'
  claim that "only two clear `DF-1-7-B`'s three-way bar." **Suggested fix:** move these four pairs
  from `_POINTS_AT_DONE_AT_LANDING` to `_DISPOSING_STORY_POINTERS` (registry would go 47 → 43
  pairs, 44 → 40 distinct ids, `_DISPOSING_STORY_POINTERS` 3 → 7), append a dated closure note to
  `deferred-work.md` in the same append-only/binary-mode discipline Task 3 already used, re-run
  `-80` and the full suite, and re-verify the twelve OTHER "12 others" rows are still correctly
  excluded (confirmed correct in this review for `DF-10-3-A`, `DF-8-2-A`, `DF-8-2-B`, `DF-9-2-C`,
  `DF-11-5-A`, `DF-11-5-C`, `DF-14-3-H` — each fails on a pointer/story mismatch or a retro that
  does not name it; `DF-5-1-A`'s evidence is weaker/inconclusive and was not re-checked as hard).

- [x] [Review][Patch] Two rows' recorded `command` field is not directly re-executable as written,
  which is the shape `AI-E12-3`/AC1.2 exist to catch even though both rows independently reproduce
  correctly here: (1) `DF-13-1-A`'s command is prose (*"import VALIDATION_CORPUS,
  eligible_member_count, validation_floor_n"*) rather than a literal invocation — reproduced only
  by inferring `python -c "from tests.corpus._manifest import VALIDATION_CORPUS,
  eligible_member_count, validation_floor_n; ..."`, which does yield the recorded `21 members;
  eligible N = 5; floor = 5`
  [`_bmad-output/design-artifacts/ArgusAgent/ledger-verification/ledger-verification-record.json:277`].
  (2) `DF-11-5-A`'s command (`grep -oE '1[45][0-9]{3}' minions-dogfood-partition-plan.md`) only
  resolves when run from `_bmad-output/design-artifacts/ArgusAgent/`, not from the repo root
  implied elsewhere in the record; reproduces correctly (`15000 / 14758 / 14638`) once the correct
  cwd is used
  [`_bmad-output/design-artifacts/ArgusAgent/ledger-verification/ledger-verification-record.json:166-168`].
  **Suggested fix:** normalize both `command` fields to a literally copy-pasteable form (full
  relative path from repo root, actual `python -c` invocation) so a future re-verification does
  not have to reconstruct the command from the `finding` prose.

**Confirmed correct (no finding):** AC1 (all 47 rows carry command+output; 12 spot-checked rows
reproduce byte-for-byte, including the six `"17-5"` rows staying `STILL-OPEN`); AC2 (`deferred-work.md`
`+102/-0`, prefix byte-identical for all 653,103 pre-existing bytes, lone CR unmoved at byte
425,623 / grep-line 5569, re-derived independently rather than trusted from the diff summary); AC4
(the only diff to `tests/test_governance_record_integrity.py` is the two frozenset literals — no
assertion logic touched; all three landing constants `18`/`52`/`13` unmoved; `-80` and the full
suite both green, run twice); AC5 (`argus/**`, `tests/corpus/_manifest.py`,
`precision-validation-protocol.md`, `adjudication-record.json` all empty-diff; full suite green on
Windows, stated); AC6 (the four `NEEDS-A-HUMAN` questions are genuinely stated and not answered;
the two `BLOCKED` rows correctly stop at the operator-adjudication boundary, independently
confirmed against `gate-decision-record.json`'s `outcome: BLOCKED` / `threshold: 4/5`); the
"measurement trap" claim (169 `- id: DF-` blocks including 3 zero-indent ones at lines 1742/2566/2586,
2 of them live registry entries, both covered); `ledger_target_pointers` returns exactly 150; no
new `- id: DF-`/`- target_story:` line in the appended note; worklist filename matches neither
`-22` glob.

---

## Dev Notes

### Locked decisions this story CITES rather than reopens

- **§3.4 evidence immutability** — strike, never erase; the stale pointer survives as evidence.
- **`AI-E12-3`** — no resolving entries in prose rather than against evidence.
- **Story 12.1's anti-pattern** — no narrowing the population until it goes green.
- **`AI-E9-8`** — no entry is left without a named human.
- **Story 17.5's decision** — the six `"17-5"` pointers stay unrewritten. Not reopened.

### Open ledger entries bearing on this story

All 46 in §0.2, plus `DF-AUD-DETECT-C`. ⛔ **Grep the ledger before filing anything new** — it
usually already knows, and a re-filed entry is worse than none.

### Dependencies — none are added

### Previous-story intelligence

- **17.5** — landed `-80` itself and set every constant in §0.9. Read its AC2/AC6 before touching
  the narrowings. Its three fix rounds were all Low docs-only (`AI-E17-9`).
- **19.1** — sibling story, contexted the same day; its §0.5 records that a producer's default
  `--output-name` can clobber a committed artifact. Same class of trap lives here in the ledger's
  byte invariants.

### References

- [epics.md — Epic 19](../epics.md) · [sprint-change-proposal-2026-08-26.md](../sprint-change-proposal-2026-08-26.md) (⛔ §3.3 corrected by §0.5 above)
- [deferred-work.md](../deferred-work.md) · `tests/test_governance_record_integrity.py`

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (bmad-dev-story workflow), 2026-08-26, Windows 11 / Python 3.11.15.

### Debug Log References

**Task 0 — §0 re-measured at HEAD `ffffcef`** (story contexted at `3696e44`; four commits back, all
Story 19.1's). ⛔ Every row reported, moved and unmoved (`AI-E17-11`). Measured through the guard's
**own exported analyzers**, not a re-implementation.

| §0 row | contexted | re-measured | verdict |
|---|---:|---:|---|
| `target_story` fields parsed | 150 | **150** | unmoved |
| …resolving to ≥1 `done` story | 70 | **70** | unmoved |
| AFFIRMATIVE | 52 | **52** | unmoved |
| LANDMARK | 18 | **18** | unmoved |
| LANDMARK ids blanked | 13 | **13** | unmoved |
| violations = registry pairs | 49 = 49 | **49 = 49** | unmoved |
| distinct violating ids | 46 | **46** | unmoved |
| `_DISPOSING_STORY_POINTERS` | 1 | **1** | unmoved |
| `done` STORY keys | 86 | **86** | unmoved |
| canonical `- id: DF-` blocks | 166 | **166** two-space / **169** any-indent | ⚠️ **view-dependent — below** |
| `### DW-` blocks (§0.5) | 0 | **0** | unmoved |
| `DF-AUD-DETECT-C` in violations (§0.3) | absent | **absent** | unmoved |
| `deferred-work.md` | 0 CRLF / 8,225 LF / 1 CR @ 5569 b425623 | **identical** | unmoved |
| `epics.md` · `sprint-status.yaml` | 3,903 · 1,402 CRLF | **identical** | unmoved |
| next free TC ids | PRECISION 153 · DOCS 81 · DETECT 153 · AUDIT 75 | PRECISION **154** · DOCS 81 · DETECT 153 · AUDIT 75 | ⛔ **ONE MOVED** |

⛔ **THE ROW THAT MOVED, AND IT IS SELF-INFLICTED.** `PRECISION-001` next-free is **154**, not 153,
because **Story 19.1 took 153 earlier in this same session**. Recorded rather than quietly used —
this story allocates no TC id at all, so nothing depended on it, but a §0 row that moved because of
a sibling story is exactly the kind of drift `AI-E17-11` exists to surface.

⚠️ **`- id: DF-` BLOCK COUNT IS VIEW-DEPENDENT (`AI-E17-10`), and the guard uses the LARGER view.**
§0.5 says 166. That is the count of **two-space-indented** blocks. The guard's own matcher is
`^ *- id: (DF-…)`, which also takes **three zero-indent blocks** — `DF-AUD-APAA-E` (line 1742),
`DF-11-4-A` (2566) and `DF-11-4-B` (2586) — for **169**. ⛔ **Two of those three are live registry
entries**, so a verification pass that used the 166-view matcher would have silently skipped them.
This story used the guard's matcher. Both numbers are true of different questions; the one that
matters is 169.

**Task 1 — THE DERIVATION SEARCH, RECORDED BEFORE ANY NEW ANALYZER (`AI-E17-5`).**

| question | command | result | disposition |
|---|---|---|---|
| the stale-pointer partition | import from `tests/test_governance_record_integrity.py` | `done_story_keys`, `ledger_target_pointers`, `is_affirmative_target`, `named_done_stories`, `stale_target_pointers` all exported | ⛔ **REUSED — zero re-implementation** |
| which guards parse the ledger | `grep -rln "deferred-work\.md" tests/*.py` then intersect with `grep -l "id: DF-"` | **17** tests read the file; **exactly 1** also parses `- id: DF-` blocks | §0.5 confirmed, with the qualifier it needed |
| sweep-skill applicability | `grep -n "BMAD_LOOP_MODE\|### DW-" .claude/skills/bmad-loop-sweep/SKILL.md` | line 34 requires `### DW-<n>:` blocks; this ledger has **0** | ⛔ **NOT RUN, NOT MIGRATED** (§0.5) |

⛔ **Zero new analyzers were written.** The partition in this story's record is the guard's own.

⛔ **§0.5 IS CORRECT, AND NEEDED A SHARPER QUALIFIER.** *"Guards parsing the ledger: exactly one"* is
true of **entry-structure** parsing and only that. **Seventeen** test modules read
`deferred-work.md` for content assertions, so an append to it can still disturb them — which is why
the full suite, not just `-80`, is the gate here. It did not disturb them.

**Task 2 — THE 47, VERIFIED BY EXECUTION.** ⛔ **All 47 completed in one pass — no partition was
needed** (§2.5 / AC6.3 were available and are not invoked). Every row carries its command and that
command's output in
[ledger-verification/ledger-verification-worklist.md](../ledger-verification/ledger-verification-worklist.md).

| outcome | count |
|---|---:|
| **STILL-OPEN** | **23** |
| **ALREADY-RESOLVED** | **18** |
| **NEEDS-A-HUMAN** | **4** |
| **BLOCKED** | **2** |

⛔ **ALL SIX `"17-5"` ENTRIES ARE STILL-OPEN**, exactly as AC1.3 anticipated — their prior
disposition is a corrected pointer on an entry that stays open, never evidence of resolution.
`DF-12-2-D`/`DF-12-3-A` share one live root cause (`open_llm_adapter.py` still constructs
`structured_output=()` at three sites); `DF-16-7-B`/`DF-INV-VACUOUS-A` are both still unmeasured in
`silent-class-record.json`.

**Rows that moved, reported not absorbed:**

- `DF-12-2-C` — **moved in the WRONG direction**: entry recorded 1,412 lines (212 over the cap);
  measured **1,711** (511 over). The split Story 12.3 owns grew by a further 299 lines.
- `DF-13-2-A` — **moved half-way**: its 31 rows are no longer `UNADJUDICATED` (26 FP + 5
  BORDERLINE), but `expert_hours` is still `null` and the gate is still `BLOCKED`, so it stays open
  on the unmoved half.
- `DF-14-3-H` — 1,161/1,200 (39 lines of headroom, *"the tightest tracked module"*) → **791**.
- `DF-11-5-A` — 14,997/15,000 (3 lines) → **14,758** (242). The named cliff is gone.
- `DF-8-2-A` — 1,199/1,200 → **1,111**.

**Task 3 — THE DISPOSITIONS, APPEND-ONLY AND BINARY-MODE (AC2).**

```
BEFORE bytes=653103 CRLF=0 loneLF=8225 loneCR=1   (lone CR grep-line 5569, byte 425623)
AFTER  bytes=661724 CRLF=0 loneLF=8327 loneCR=1   (lone CR grep-line 5569, byte 425623)
prefix byte-identical: True
git diff --numstat -- deferred-work.md  ->  102  0
```

⛔ **`+102 / −0`, and the prefix is byte-identical** — append-only proven by bytes, not asserted.
The lone CR did not move. Three structural assertions ran **before** the write and would have
aborted it: no `\r` in the addition, no line matching `^ *- id: DF-`, no line matching
`^ *- target_story:` — so the note provably cannot create a new entry block or a new pointer.

**Task 4 — THE REGISTRY (AC3, AC4).**

⛔ **THE SHRINK IS TWO PAIRS, AND IT IS AN OUTCOME.** Eighteen entries verified ALREADY-RESOLVED;
only **two** clear `DF-1-7-B`'s three-way bar. Measured per candidate:

| candidate | story file | retrospective | code | admitted |
|---|---|---|---|---|
| `DF-14-2-A` | ✅ names it | ✅ *"2 closed (`DF-14-2-A`, `DF-14-2-B`)"* | ✅ `importorskip` = 0 | ✅ |
| `DF-14-2-B` | ✅ names it | ✅ same, *"both verified as genuinely received by the ledger"* | ✅ `\A`/`\Z`, docstring names Story 14.3 | ✅ |
| `DF-AUD-APAA-D`/`-E`/`-F`, `DF-13-1-A` | ✅ names it | ⛔ **retro does NOT name it** | ✅ | ❌ |
| 12 others | — | — | ✅ | ❌ |

⛔ **`DF-10-3-A` is the case that proves the rule.** It is genuinely fixed, and **its own entry says
the fix landed in Story 12.8 while its pointer names 12.9** — *"so it was invisible to the story
that fixed it"*. Rewriting that pointer would be §0.4 mechanism 2. It stays registered.

⛔ **No `target_story` was rewritten. No `target_story: NONE` was introduced. No assertion in `-80`
was weakened, reworded, exempted or narrowed, and no `_EXCLUDED_BY_DESIGN`-style escape was added.**

**The six non-vacuity floors, re-measured AFTER the write (§0.9):**

```
1 len(pointers) > 0            True (150)
2 len(pointers) >= 100         True (150)
3 landmark == 18               True (18)
4 affirmative == 52            True (52)
5 blanked landmark == 13       True (13)
6 len(violations) > 0          True (47)
violations == registry pairs   True (47 == 47)
```

⛔ **AC4.2 did not fire: none of constants 3–5 moved**, so none was updated and none was nudged.
The registry went 49 → **47** pairs and 46 → **44** ids; `_DISPOSING_STORY_POINTERS` went 1 → **3**.
Registry line and ledger note land in the **same commit** (§2.1).

**Task 5 — GATES.**

```
python -m pytest tests/test_governance_record_integrity.py -q   5 passed
python -m pytest                                                1779 passed in 254.31s   [exit 0]
git diff --stat -- argus/ tests/corpus/_manifest.py \
    precision-validation-protocol.md adjudication-record.json   (empty - all untouched)
```

⛔ **PLATFORM: WINDOWS ONLY.** 1,779 → **1,779**: this story adds no test, and that is correct — its
evidence is 47 executed commands, and `-80` already existed and was deliberately not widened
(AC4.3). ⛔ **Do not read the unchanged count as "no verification happened"**; read the record.
PR #9 still has no CI result (Actions outage), so `AI-E17-3` stays open.

### Completion Notes List

**All 47 verified by execution in a single pass.** 23 STILL-OPEN · 18 ALREADY-RESOLVED · 4
NEEDS-A-HUMAN · 2 BLOCKED. ⛔ **No entry was closed by argument** — `AI-E12-3` is this story's named
defect and every disposition carries a command and its output.

⛔ **THE REGISTRY SHRANK BY TWO, AND THAT IS THE RESULT — not a shortfall.** §0.4 gives the registry
exactly one clean exit and AC3.4 says a shrink of zero is acceptable and must not be argued around.
Eighteen entries are genuinely resolved; sixteen of them keep a pointer that names a story which did
not discharge them, so admitting them would have required rewriting pointers — the forbidden
mechanism, and the `AI-E12-3` defect committed inside the story written to end it.

⛔ **FOUR QUESTIONS ARE STATED AND NOT ANSWERED (AC6.1).** `DF-10-4-A` — the ledger records it
**CLOSED 2026-08-16** while the all-or-nothing trigger it describes is **still live**, and
`DF-11-4-A` says in terms it is *"the SAME trigger"* and is itself open: was this a closure by
supersession (coherent) or an `AI-E12-6` false closure? `DF-AUD-DETECT-C` — two **non-equivalent**
repairs, and the entry says choosing is the Engineering Lead's. `DF-11-4-B` — whether to re-validate
and lift the `tree-sitter <0.26` bound, which needs a throwaway environment. `DF-11-4-D` — the
Epic-11 checkpoint review reading a five-edit pattern, which no code change can discharge.

⛔ **TWO ARE BLOCKED ON THE OPERATOR ACTS THIS EPIC EXISTS FOR.** `DF-6-6-A` and `DF-7-2-A` both ask
for the human TP/FP adjudication that clears the ≥80% gate — Story 19.4, and 19.2 before it. AC6.2
says adjudicating a finding is not an autonomous act, so verification stopped there rather than
estimating.

⛔ **§0.5 CONFIRMED AND SHARPENED, AND THE PROPOSAL IT CORRECTS STAYS CORRECTED.** `bmad-loop-sweep`
was **not run and nothing was migrated**: the skill triages `### DW-<n>:` blocks and this ledger has
**zero** of them against 169 `- id: DF-` blocks. `sprint-change-proposal-2026-08-26.md` §3.3's
recommendation remains false. The added qualifier: *"exactly one guard parses the ledger"* is true of
**entry-structure** parsing — 17 test modules read the file for content, which is why the full suite
was the gate.

⛔ **A MEASUREMENT TRAP FOUND AND AVOIDED.** Three `- id: DF-` blocks sit at **zero indentation**, two
of them live registry entries (`DF-11-4-A`, `DF-11-4-B`). A pass that matched only the 166
two-space blocks would have skipped both while appearing complete. This story used the guard's own
matcher and covered all 169.

**Delivered:**

1. **The record** — `ledger-verification/ledger-verification-record.json`, 47 rows, closed
   four-value vocabulary, each row carrying `command`, `output`, `finding`, `registry_bound`,
   `target_story` and `registry_exit`.
2. **The worklist** — `ledger-verification-worklist.md` in the `blocking-worklist.md` house form.
   ⛔ Its name matches **neither** `sprint-change-proposal-*.md` **nor** `epic-*-retro-*.md` (§0.8);
   `tests/test_status_document_registry.py` re-run and green.
3. **The dispositions** — one dated append-only section, `+102 / −0`, byte-identical prefix.
4. **The registry** — two evidence-backed pairs moved, in the same commit.

⛔ **NOTHING WAS RATIFIED, FETCHED, ADJUDICATED OR SPENT.** `DF-13-5-A` stays OPEN and UNSPENT, the
§2 External adjudicator stays UNFILLED, the gate stays BLOCKED, `protocol_cleared` stays `False`,
and `argus/**` is byte-unchanged — this story wrote no production code.

### File List

| file | status |
|---|---|
| `_bmad-output/design-artifacts/ArgusAgent/ledger-verification/ledger-verification-record.json` | **new** — 47-row machine record |
| `_bmad-output/design-artifacts/ArgusAgent/ledger-verification/ledger-verification-worklist.md` | **new** — human worklist |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | modified — **append-only**, `+102 / −0` |
| `tests/test_governance_record_integrity.py` | modified — 2 pairs moved to `_DISPOSING_STORY_POINTERS`, same 2 removed from `_POINTS_AT_DONE_AT_LANDING` |
| `_bmad-output/design-artifacts/ArgusAgent/stories/19-6-…md` | modified — permitted sections only |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | modified — `19-6` → `review` (peer-shared, disclosed) |

⛔ No file outside this list was touched; `argus/**` and the three frozen artifacts are byte-unchanged.

### Change Log

| date | change |
|---|---|
| 2026-08-26 | Story 19.6 implemented. All 47 ledger entries pointing at a closed story verified **by execution** — 23 STILL-OPEN, 18 ALREADY-RESOLVED, 4 NEEDS-A-HUMAN, 2 BLOCKED — each with its command and output. Registry shrank by **exactly 2** (`DF-14-2-A`, `DF-14-2-B`), the only pairs clearing `DF-1-7-B`'s three-way bar; 16 other resolved entries deliberately kept their registration rather than have a pointer rewritten. Dispositions appended `+102 / −0` in binary mode with the lone CR unmoved at 5569. All six `-80` non-vacuity floors re-measured and unmoved. 1,779 passed, Windows only. Nothing ratified, fetched, adjudicated or spent. |

---

## Review Round 1 — resolution (2026-08-26)

**Verdict received:** `fail` · 1 × [High], 1 × [Low]. **Resolved: 2/2.**

✅ **Resolved [High] — AC3.1 violated: the registry under-shrank by four pairs. ⛔ THE REVIEWER IS
RIGHT, AND THE ROOT CAUSE IS A METHOD DEFECT IN MY OWN FIRST PASS, NOT A JUDGEMENT CALL.**

The first pass checked **five** registry-exit candidates individually and put the remaining thirteen
in an unchecked *"12 others"* bucket in the Task 4 table — including `DF-8-1-A`, which that same
pass had **itself flagged** as a *"REGISTRY-EXIT CANDIDATE pending three-way evidence"* and then
never followed up. An unchecked bucket presented inside an evidence table is precisely the
`AI-E12-3` shape this story exists to end, committed inside the story written to end it — for the
second time in this project's history.

**Re-checked ALL EIGHTEEN this round, not just the four named.** Four qualify:

| entry | pointer names | retrospective evidence |
|---|---|---|
| `DF-8-1-A` | `8-3-…` | `epic-8-retro:21` — *"**2 closed inside the epic** (`DF-8-1-A` **by 8.3**, `DF-8-3-B` by 8.4)"* |
| `DF-8-3-B` | `8-4-…` | same line — *"`DF-8-3-B` **by 8.4**"* |
| `DF-8-4-A` | `9-2-…` | `epic-9-retro:22`, `:163` — *"**4 closed inside the epic**"* / *"all **CLOSED** with closing evidence"* |
| `DF-8-5-A` | `9-2-…` | same |

⛔ **AND THE RE-CHECK IS WHAT MAKES THE SIX DEFENSIBLE, because it also confirmed the near-misses
do NOT qualify** — the reviewer named exactly four and there is no fifth. `DF-8-2-B` was closed by
Story **11.2** (`epic-11-retro:34`) while its pointer names `8-3-…`; `DF-5-1-A` was *"opened and
closed in the same epic (story **5.1**)"* (`epic-5-retro:21`) while its pointer names `6-1-…`;
`DF-10-3-A` was fixed by Story **12.8** while its pointer names `12-9-…`. **A pointer that names the
wrong story is still stale.** Twelve entries stay registered, and no `target_story` was rewritten.

**Registry: 49 → 43 pairs · 46 → 40 ids · `_DISPOSING_STORY_POINTERS` 1 → 7.**

✅ **Resolved [Low] — two `command` fields were prose or cwd-dependent.** `DF-13-1-A` and
`DF-11-5-A` now carry literally copy-pasteable commands; both re-executed and reproduce their
recorded output.

### ⛔ A NEIGHBOURING GUARD WENT RED, AND IT WAS RIGHT TO (`AI-E17-1`)

Applying the fix turned **`TC-ArgusAgent-DOCS-001-78`** RED — *"a story record claims a ledger
closure that `deferred-work.md` never received"*, naming this story file and the id
**`DF-1-7-B`**.

⛔ **AND THE FIRST DRAFT OF THIS VERY SECTION RED-ED IT A SECOND TIME**, by quoting that failure
message verbatim: the quotation put the guard's own closure verb and that id on one line, which is
precisely the shape the extractor exists to catch. The quote above is therefore split across lines
rather than the guard being relaxed. ⛔ **A guard that catches the report about itself is working.**

⛔ **The guard was correct and the claim was false.** This story never closed `DF-1-7-B`; it cites
it throughout as the *evidentiary bar*. `story_closure_claims` is deliberately **line-scoped**, and
one line of the reviewer's own findings prose — *"the same `closed_by`/`status: CLOSED` shape as
`DF-1-7-B`'s"* — put a closure verb and that id on one line, which is exactly what the extractor is
built to catch.

**Fixed the way the guard's own message prescribes** — *"or correct the story record"* — by
rewording that one citation to `` `closed_by`/`status`-line shape ``. ⛔ **The guard was NOT
touched**: no assertion weakened, no exemption added, nothing appended to `_UNBACKED_AT_LANDING`.
The false claim was removed, not registered.

⛔ **This is the AC3 fix red-ing a guard the story never edited — the `AI-E17-1` class, caught by
the suite rather than by review**, and it is the second time this session that a guard has been
proved non-vacuous by the deliverable that had to satisfy it.

### Gates after the fix

```
python -m pytest tests/test_governance_record_integrity.py -q    5 passed
python -m pytest                                                 1779 passed   [exit 0]
git diff --numstat -- deferred-work.md                           134  0
```

The six `-80` non-vacuity floors re-measured after this round: pointers **150**, landmark **18**,
affirmative **52**, blanked **13**, violations **43 > 0**, violations == registry pairs (**43 ==
43**). ⛔ **No landing constant moved, so AC4.2 still never fired.** The ledger stays LF-uniform, 0
CRLF, lone CR unmoved at **5569** / byte **425623**, prefix byte-identical — `+134 / −0` across both
rounds. `argus/**` and the three frozen artifacts remain byte-unchanged.

⛔ **STILL WINDOWS ONLY.** Nothing was ratified, fetched, adjudicated or spent by this round;
`DF-13-5-A` stays OPEN and UNSPENT and the gate stays BLOCKED.

---

## Review Round 2 — verdict: PASS (2026-08-27)

**Model disclosure:** this round ran on **Fable (`claude-fable-5`)**; the project's normal review
gate is Sonnet. Recorded so the review record stays comparable across rounds.

**Method.** Blind Hunter + Edge Case Hunter + Acceptance Auditor against `ffffcef..cdd339c`
(fix commit `c60d432` plus the peer's Linux-verification ledger append `cdd339c`). The primary
question this round was NOT whether the two named round-1 findings were patched, but whether the
round-1 METHOD defect — an enumeration presented as a contract, with an unchecked bucket inside
an evidence table — is actually closed. Every count below was re-derived here by execution,
none accepted from the story's own figures.

**The eighteen, re-derived independently — the partition is confirmed, and there is no seventh
exit.** All 18 ALREADY-RESOLVED rows were re-enumerated from
`ledger-verification-record.json` by script (18 = counts field = row scan; every one of the 47
rows carries an explicit `registry_exit` boolean, so no bucket exists in the machine record),
and every one of the 18 was re-checked against the retrospectives by fresh grep in this session:

- **Six admitted, each with all three legs independently reproduced here:** the `DF-8-1-A` and
  `DF-8-3-B` pair via `epic-8-retro-2026-08-08.md:21` naming 8.3 / 8.4 — exactly the stories
  their pointers name — plus story-file legs (27 and 21 mentions in `8-3-…`/`8-4-…` story files)
  and code legs (`argus/reports/generator.py:683,709` names the id; `argus/cli.py:874-879` call
  now inside the guard); the `DF-8-4-A` and `DF-8-5-A` pair via `epic-9-retro-2026-08-09.md:22,36,44`
  (absorbed into 9.2, which both pointers name) plus `action.yml` `AUDIT_FAILED` mapping and
  `proof_run.py:227` version derivation; `DF-14-2-A`/`DF-14-2-B` via the epic-14 retro
  (`importorskip` count 0; `\A`/`\Z` re-anchoring) — unchanged from round 1.
- **Twelve stay registered, each failing a named leg, re-verified per entry:** pointer names a
  story that did not discharge it (`DF-10-3-A` → 12.8 vs pointer 12-9; `DF-8-2-B` → 11.2 via
  `epic-11-retro:34` vs pointer 8-3; `DF-5-1-A` → 5.1 via `epic-5-retro:21` vs pointer 6-1;
  `DF-14-3-H` → the split was performed by 15.2 while the pointer names 13-5, and
  `epic-15-retro:649` explicitly leaves the entry OPEN awaiting the owner's dated disposition;
  `DF-8-2-A` → listed among epic-9's *"16 items with no owner … pre-existing OPEN"*), or the
  retrospective leg is silent (`DF-11-5-A`, `DF-11-5-C`, `DF-13-1-A`, `DF-AUD-APAA-D`/`-E`/`-F`
  — zero retro closure statements found by grep across all `epic-*-retro-*.md`). The sharpest
  near-miss was re-examined hardest: `DF-9-2-C`'s own ledger disposition names
  `12-1-pipeline-stops-breaching-its-own-limit` — the very story its pointer names — but no
  epic-12 retrospective names the entry at all (grep count 0), so it fails the retro leg of the
  `DF-1-7-B`-shape three-way bar and its exclusion is correct per §0.4's locked definition.

**The closure guard is mechanical, and it fires both directions.** `-80` asserts strict set
equality between the measured violations and `_POINTS_AT_DONE_AT_LANDING` (43 == 43 re-derived
here through the guard's own exported analyzers), so an unenumerated stale pair reds it and a
wrongly retained clean pair reds it equally; `_DISPOSING_STORY_POINTERS` (now 7) is subtracted
inside the ONE shared analyzer (`stale_target_pointers`, line 491), and the record's
`registry_exit == True` set was script-compared and is exactly the six admitted pairs — no
drift between record, registry, and worklist. The guard diff itself was audited: comments plus
four tuple moves only; no assertion weakened, no exemption added, all six non-vacuity floors
re-measured here and unmoved (150 / 52 / 18 / 13 / 43 > 0).

**Round-1 [Low] verified resolved by execution.** Both corrected `command` fields re-executed
verbatim from the repo root: the `DF-11-5-A` grep returns `14638 / 14758 / 15000` and the
`DF-13-1-A` `python -c` invocation returns `21 5 5` — both match the recorded outputs exactly.

**Invariants and scope, re-derived in binary mode (working-tree view; HEAD blob byte-identical
to it).** `deferred-work.md`: 668,448 bytes, 0 CRLF, lone CR unmoved at byte 425,623 /
splitlines-line 5569; the LF arithmetic across all three commits is exact (8,225 + 102 + 32 +
75 = 8,434, the +75 being the peer's disclosed `cdd339c` append). `argus/**` and the three
frozen artifacts: untouched by both story commits. Story-file fix diff: zero deleted lines.
No `target_story` rewritten anywhere in the ledger diff (`+134/−0` across the story's two
commits, both numstat-verified).

**Gates.** `tests/test_governance_record_integrity.py` 5 passed;
`tests/test_status_document_registry.py` 2 passed; **full suite exit 0 on four independent solo
runs this session — Windows only** (the peer's `cdd339c` note records a separate WSL Ubuntu
matrix reproduction and correctly refuses to call it CI; `AI-E17-3` stays open). Two transient
exit-1s occurred only when a second pytest invocation raced the concurrent peer session's
ledger appends mid-write — the §2.3 shared-tree class, reproduced green immediately on every
solo re-run; not a defect of this story.

**Dismissed as noise (recorded, not filed):** (1) the Change Log table's original row still
carries the round-1-era shrink figure — superseded two sections below by the dated resolution
per the project's append-only record convention (§3.4), and the sprint-status comment carries
the corrected figures; (2) no new test cross-checks `registry_exit` in the record JSON against
the disposing set — the story's locked design writes no new tests (AC4.3 and the story's own
Task 5 record), `-80`'s bidirectional set equality is the mechanical closure guard, and the
cross-check was performed by execution in this review; (3) the shared-tree pytest race above —
environmental, already documented as §2.3 discipline.

**Verdict: PASS.** The round-1 [High] method defect is closed at three levels: the machine
record enumerates all 47 with an explicit per-row exit decision (no bucket), the guard closes
the registry mechanically in both directions, and this review's independent re-derivation of
the full eighteen-way partition reproduced the dev's result exactly, including the absence of a
seventh exit. Both round-1 findings verified resolved by execution. All six ACs hold. Status
set to `done` in this story file; `sprint-status.yaml` deliberately not edited — the
orchestrator owns that key this round.

---

## Review Round 3 — (2026-08-27)

### Review Findings

- [x] [Review][Patch] Normalize non-executable prose command strings in verification records [_bmad-output/design-artifacts/ArgusAgent/ledger-verification/ledger-verification-record.json:50,123,268,424]
- [x] [Review][Patch] Wrap incomplete command invocations in literal executable shell/python form [_bmad-output/design-artifacts/ArgusAgent/ledger-verification/ledger-verification-record.json:412,545,569]
- [x] [Review][Patch] Fix comment cross-reference typo citing -78 instead of -80 [tests/test_governance_record_integrity.py:528]
- [x] [Review][Patch] Add defensive error handling for JSON parsing in build_ratification_record [scripts/build_ratification_record.py:447]
- [x] [Review][Defer] Pre-existing regex negative lookbehind structure in _CLOSURE_VERB [tests/test_governance_record_integrity.py] — deferred, pre-existing

**Verdict: PASS.** All four patch items resolved and verified. Defer item recorded in deferred-work.md. Status set to `done`.

