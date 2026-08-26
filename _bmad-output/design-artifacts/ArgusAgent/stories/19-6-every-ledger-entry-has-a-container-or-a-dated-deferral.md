---
baseline_commit: 3696e44
---

# Story 19.6: Every ledger entry has a container or a dated deferral

Status: ready-for-dev

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

- [ ] Re-run the guard's exported analyzers; reproduce every row of §0.1.
- [ ] Re-confirm `DF-AUD-DETECT-C` is absent from the violations (§0.3).
- [ ] Re-confirm 0 `### DW-` blocks / 166 `- id: DF-` blocks (§0.5).
- [ ] Re-measure the byte invariants (§0.6) and the next free ids (§0.7).
- [ ] ⛔ Report **every** row — moved and unmoved — with its command.

### Task 1 — THE DERIVATION SEARCH, RECORDED (`AI-E17-5`)

- [ ] Grep `argus/` and `scripts/` for any existing derivation of "is this entry still open".
- [ ] Record command + result **before** writing any new analyzer.
- [ ] ⛔ Reuse `stale_target_pointers` and friends; do not re-implement the partition.

### Task 2 — VERIFY THE 47 (AC1)

- [ ] Per entry: read the block, read the code it names, run something that decides.
- [ ] Record outcome + command + output.
- [ ] `NEEDS-A-HUMAN` for anything needing a ruling — state the question, do not answer it.

### Task 3 — THE DISPOSITIONS (AC2)

- [ ] Append-only dated notes, binary mode, invariants re-measured before and after.
- [ ] ⛔ `git diff` proving no existing field moved.

### Task 4 — THE REGISTRY (AC3, AC4)

- [ ] Move only `ALREADY-RESOLVED` pairs with three-way evidence to `_DISPOSING_STORY_POINTERS`.
- [ ] Remove exactly those from `_POINTS_AT_DONE_AT_LANDING`, same commit.
- [ ] Run `-80`; confirm green both directions; record it.
- [ ] ⛔ If the shrink is zero, **say so plainly** and move on.

### Task 5 — GATES AND HAND-OFF (AC5)

- [ ] `git diff --stat` proving `argus/**` and the three frozen artifacts are untouched.
- [ ] Full suite; state the platform.
- [ ] Stage by explicit path; disclose carried peer files by name.

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

### Debug Log References

### Completion Notes List

### File List
