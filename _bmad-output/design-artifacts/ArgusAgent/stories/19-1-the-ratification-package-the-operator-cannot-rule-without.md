---
baseline_commit: 83ecc8d
---

# Story 19.1: The ratification package the operator cannot rule without

Status: ready-for-dev

<!-- Contexted 2026-08-26 at HEAD `83ecc8d` (branch `docs/merge-strategy-decision`, 36 ahead of
     `origin/master`) by the create-story workflow (Opus 5).

     ⛔ THE TREE IS NOT CLEAN AT CONTEXTING, AND THE ONE MODIFIED PATH IS THIS SESSION'S OWN.
     `git status --porcelain` shows `M _bmad-output/design-artifacts/ArgusAgent/epics.md` — a
     same-day correction to Story 19.6's byte-invariant clause, made BY MEASUREMENT during this
     contexting (§0.8). It is disclosed here rather than swept into this story's first commit.
     ⛔ Stage by explicit path; never `git add -A`.

     EVERY FIGURE IN §0 WAS READ OFF THIS TREE BY EXECUTION at `83ecc8d`, not copied from
     `epics.md`, from `sprint-change-proposal-2026-08-26.md`, or from the Epic-17 retrospective.
     The manifest was IMPORTED and its rows dumped field by field; all six sealed pins were probed
     with `git cat-file -e <sha>^{commit}` at their real checkout paths; every tree was walked with
     `git ls-tree -r` at the pin; the ledger's byte state was re-counted; the TC-id families were
     re-scanned for their maxima.

     ⛔⛔ THE PREMISE THAT MOVED, AND IT IS THE REASON THIS STORY IS FEASIBLE AT ALL:
     **THE SIX SEALED CHECKOUTS ARE ALREADY ON DISK.** `epics.md` was written this morning
     assuming the worksheet's finding-count column might not be reachable without a fetch — and
     `argus/precision/gate_yield.py::YIELD_PROVENANCE_DISCLOSURE` says in shipped prose that the
     sealed partition's yield is *"UNMEASURABLE without fetching third-party source, which is a
     protocol §6 R2 operator act no agent may take"*. **Measured at HEAD: all six are present under
     `D:/_bench/`, fetched by the operator during Story 15.1, and all six pins are reachable.**
     The disclosure is about what THIS REPOSITORY can see by itself — which is nothing, on CI —
     and NOT about what this machine holds. ⛔ §0.4 states the distinction in terms, because a dev
     that misreads it will either refuse a feasible story or fetch something it must not.

     FOUR PREMISES SHARPENED AGAINST WHAT `epics.md` ASSUMES:

       (1) §0.2 — ⛔ **MOST OF THE PACKAGE ALREADY EXISTS IN THE MANIFEST.** `epics.md` names five
           columns as though all five were unbuilt. Measured: `repository_url`, `commit_sha`,
           `licence` (with its tracked-at-the-pin evidence), `primary_language`, `provenance`,
           `eligible_for_n`, `ineligible_reason` AND a per-member `adjudication_caveat` are ALL
           already carried, for all six, in `tests/corpus/_manifest.py`. ⛔ Re-deriving them is the
           AR7 / `DN-3` / `DF-8-5-C` one-derivation defect, and `AI-E17-5` — raised against exactly
           this class, twice in Epic 17 — requires the search be RECORDED before any new
           derivation is written.

       (2) §0.6 — ⛔ **STORY 15.1 ALREADY MEASURED THESE SIX AT THESE PINS.** Its selection table
           records, per candidate, test-file and co-occurrence counts, strict/loose figures, a
           history span in days and the licence path. Those are prior measurements at the SAME
           shas. ⛔ Re-verify them; do not re-derive them, and do not silently supersede them.

       (3) §0.5 — ⛔ **THE FINDING COUNT HAS EXACTLY ONE PRODUCER**, and it already exists:
           `scripts/audit_validation_corpus.py` with `--checkout-root` / `--member-path` /
           `--snapshot-root`. A second walker is a second derivation of the same question.

       (4) §0.0 — ⛔ **CI HAS NOT RUN AND CANNOT BE WAITED FOR.** PR #9 is open against `master`;
           GitHub Actions entered a **major outage at 2026-08-26 15:11:58 UTC** and every run
           queued against this branch since has recorded `steps: 0`. ⛔ This story may NOT treat a
           green local suite as cross-platform evidence (`AI-E17-3`, and the standing rule in
           §2.4).

     ⛔ NOTHING HERE RATIFIES A MEMBER, FETCHES A THIRD-PARTY SOURCE, FLIPS AN `eligible_for_n`,
     SPENDS `DF-13-5-A`'s ROUND, ADJUDICATES A ROW, ADDS A PROTOCOL ROW, OR MAKES ANY FINDING
     VERDICT-ELIGIBLE. `precision-validation-protocol.md` and `adjudication-record.json` are
     BYTE-FROZEN by this story. -->

## Story

As the **Engineering Lead**,
I want **one worksheet carrying, for each of the six sealed bench members, the facts a protocol §6 R2 ratification actually turns on — assembled from what is already recorded and measured only where nothing is**,
so that **the operator act in Story 19.2 is a judgement on measured evidence rather than on a list of six repository names.**

### What this story IS

The **evidence package**, and nothing else. It reads the manifest, re-verifies Story 15.1's prior
figures at the same pins, measures the two columns nobody has measured, and writes one record the
operator can rule from. **Then it STOPS.**

Its deliverable is three things and they are separable:

1. a **worksheet record** under `validation-corpus/ratification/`, machine-readable, with a
   companion human worklist in the `blocking-worklist.md` / `silent-class-worklist.md` house form;
2. a **guard** that reads the committed record and the manifest — never the corpus — so it is
   green on the ubuntu matrix with no checkouts present;
3. a **stated boundary**: the record says, in its own fields, that it ratifies nothing and that
   `eligible_member_count()` is unchanged at **5**.

### What it is NOT

⛔ **It is not the ratification.** Protocol §6 R2 is verbatim: *"choosing which repositories are
legitimate members, and fetching third-party source, are not autonomous acts."* Story 19.2 is the
operator act and it is filed `operator-act`, not `backlog`. This story produces the input to it.

⛔ **It is not a fetch.** The six checkouts are already on disk (§0.4). This story reads them. It
opens no socket, and AC2.3 asserts that structurally over the module's AST rather than promising it
in prose — the `-141` precedent.

⛔ **It is not a recommendation.** The worksheet reports what each member IS. It carries no
`recommended`, `admit`, `score` or `rank` field, and no prose arguing for admission. A worksheet
that ranks the candidates has pre-empted the operator act it exists to serve.

⛔ **It is not an adjudication and it is not a yield measurement.** No finding is judged TP or FP.
The finding count is a **population size**, and `YIELD_PROVENANCE_DISCLOSURE`'s own first sentence
is the rule this story inherits: *"A POPULATION SIZE IS NOT A YIELD FORECAST."*

⛔ **It is not Story 19.6.** The 46 stale `target_story` pointers are 19.6's by name. This story
writes **zero** ledger entries unless it finds something new, in which case AC6 applies.

---

## §0 — PREMISES MEASURED BY EXECUTION at HEAD `83ecc8d`

⛔ **Task 0 re-measures every row of this section before a line is written.** Per `AI-E17-11`, **"a
row moved" is a first-class outcome that is REPORTED, not absorbed.** Epic 17 ran this two-pass in
5 of 5 stories and it found real drift in 4 of them.

### §0.0 The tree, the paths, the baseline

| fact | value |
|---|---|
| HEAD | `83ecc8d` — *docs(19): file Epic 19 — a container for the operator acts* |
| branch | `docs/merge-strategy-decision`, **36 ahead** of `origin/master`, upstream now set |
| working tree | `M …/epics.md` — **this session's own** same-day correction to 19.6 (§0.8) |
| PR | **#9** open against `master` |
| CI | ⛔ **never ran.** GitHub Actions major outage from **2026-08-26 15:11:58 UTC**; run `32985552326` and its rerun both recorded `steps: 0` across all three matrix legs |
| local suite | **1,760 tests, exit 0**, Windows only |

### §0.1 The six sealed members — pins probed, trees walked

Every row measured at HEAD with `git cat-file -e <sha>^{commit}` and `git ls-tree -r --name-only`:

| member_id | pinned sha | checkout | reachable | files @ pin | `.py` @ pin |
|---|---|---|---|---|---|
| `aws-aws-sam-cli` | `5b6ebdba5866` | `D:/_bench/samcli` | ✅ | 3,919 | 1,703 |
| `celery-celery` | `2c42237d3757` | `D:/_bench/celery` | ✅ | 823 | 419 |
| `certbot-certbot` | `abf9d1b2e143` | `D:/_bench/certbot` | ✅ | 1,252 | 366 |
| `conda-conda` | `ad60271d8409` | `D:/_bench/conda` | ✅ | 2,164 | 447 |
| `getsentry-sentry-python` | `064542dd2cbd` | `D:/_bench/sentrypy` | ✅ | 639 | 499 |
| `googleapis-google-auth-library-python` | `2ea24b034367` | `D:/_bench/gauth` | ✅ | 374 | 192 |

⛔ **The checkout directory names do NOT match the `member_id`s** (`samcli` ≠ `aws-aws-sam-cli`).
The mapping above is the one `--member-path` needs, and getting it wrong has cost a cycle before —
`agent-smith` lives one level deeper than its sibling members and Story 17.4 §0.6 records it as a
known trap.

### §0.2 ⛔ THE MANIFEST ALREADY CARRIES MOST OF THE PACKAGE — do not re-derive it

Dumped field by field from `tests.corpus._manifest.VALIDATION_CORPUS` at HEAD. All six sealed rows
carry **every** field below, populated:

- `repository_url`, `commit_sha`, `primary_language` (all six: `python`), `provenance` (all six:
  `independent`)
- `licence` — **with its evidence**, e.g. `"Apache-2.0 — 'Apache License' (LICENSE, tracked at the
  pin)"`. The licence column of the worksheet is a **citation**, not a new lookup.
- `eligible_for_n` — **`False` for all six**
- `ineligible_reason` — all six: `"candidate - awaiting operator ratification (protocol section 6
  R2)"`
- `adjudication_caveat` — a per-member arms-length statement (*"THIRD-PARTY and arms-length: Argus
  was never developed against it, no Argus author has contributed to it…"*). ⛔ This field exists
  **precisely** to carry what an adjudicator must know before judging, and it is already written.

⛔ **`AI-E17-5` APPLIES AND IS NOT OPTIONAL.** Before writing any new function that answers a
factual question about a member, grep `argus/` and `scripts/` for an existing exported derivation
of that question and **record the command and its result in the Dev Agent Record**. This obligation
was raised against two Epic-17 stories that cited the one-derivation doctrine *by name in their own
text* and forked it anyway.

### §0.3 sealed ∩ ratified is EMPTY — re-verified, and it does not move here

`eligible_member_count()` = **5**; the ratified set is exactly `PRE_SEAL_MEMBER_IDS`
(`ai-body-runtime`, `agent-markovich`, `minions`, `xagents-webapp`, `agent-smith`).
`SEALED_PARTITION_TABLE` holds 14 rows — **6 `sealed`, 8 `open`** — and all 14 are
`eligible_for_n = False`. **Intersection: `[]`.**

⛔ **This story does not move it, and AC2 asserts that it did not.** Only a §6 R2 operator act can.

### §0.4 ⛔ THE FETCH BOUNDARY, STATED IN TERMS

`gate_yield.YIELD_PROVENANCE_DISCLOSURE` says the achievable yield over the sealed partition is
*"UNMEASURABLE without fetching third-party source, which is a protocol §6 R2 operator act no agent
may take"*. **That sentence is true and this story does not contradict it.** It describes what the
repository can establish **by itself** — on CI, in a fresh clone, there are no checkouts and the
answer is genuinely unmeasurable.

**On this machine the source is already present**, fetched by the operator during Story 15.1 and
still on disk at the same paths. Reading source an operator already fetched is **not** fetching.

⛔ **THE LINE, SO IT CANNOT BE MISREAD:** if a member's checkout is absent, or its pin is
unreachable, the story **records that member as UNMEASURED with the reason** and moves on. It does
**not** clone, pull, fetch, or reach the network to repair it. That is AC2.3, and it is asserted
over the module's AST.

### §0.5 ⛔ THE ONE PRODUCER FOR THE FINDING COUNT

`scripts/audit_validation_corpus.py`. ⛔ **The flags below were read off `main()` at HEAD, not
guessed** — an earlier draft of this section invented `--member-path`, which **does not exist**:

```
python scripts/audit_validation_corpus.py \
  --checkout-root D:/_bench \
  --map aws-aws-sam-cli=samcli --map celery-celery=celery ... \
  --only <member_id> \
  --snapshot-root D:/_argus_snap \
  --output-name <NOT the default>
```

| flag | what it actually is |
|---|---|
| `--checkout-root` | **required** — the directory containing the checkouts, *"resolved per member by `--map`"* |
| `--map MEMBER_ID=RELATIVE_PATH` | repeatable; this is the §0.1 mapping (`aws-aws-sam-cli=samcli`, …) |
| `--only` | repeatable; audit only these members |
| `--snapshot-root` | where pinned snapshots are materialised |
| `--output-name` | ⛔ **defaults to `adjudication-set.json`** |

⛔ **`--output-name` IS A LOADED GUN.** Its default is `adjudication-set.json`, and
`validation-corpus/adjudication-set.json` is a **committed artifact**. Running this producer with
default flags **overwrites it**. Pass an explicit `--output-name` under the ratification prefix, and
`git status` the artifact directory after every run.

⛔ **Do not write a second walker.** ⛔ **Use a SHORT `--snapshot-root`** — the flag's own help says
a member's deepest in-scope path is ~104 characters and the default temp root can push the absolute
path past `MAX_PATH`, and the failure mode is *"a partially-extracted tree derives clean"*: it fails
**silently, in the dangerous direction**. `aws-aws-sam-cli` is the largest tree here at 3,919 files
and is the likeliest to trip it. The help text's own suggestion is `D:/_argus_snap`.

### §0.6 Story 15.1 measured these six at these pins — cite, then re-verify

15.1's selection table records per candidate: test-file count / co-occurrence count, strict/loose
figures, history span in days, and the licence path — read at the same `D:/_bench/*` paths and the
same pins. Example row, verbatim: `aws-aws-sam-cli … PASS 497 / 215 … PASS 215 / 218 … PASS 3294 …
PASS Apache-2.0 (LICENSE)`.

⛔ **Re-verify at Task 0 rather than trusting.** These figures are ~11 days old and `AI-E17-11`'s
whole point is that a row that moves must be reported. If one moved, say so loudly.

### §0.7 The next free ids, measured by scan

| family | max in tree | next free |
|---|---:|---|
| `TC-ArgusAgent-PRECISION-001-*` | 152 | **153** |
| `TC-ArgusAgent-DOCS-001-*` | 80 | **81** |
| `TC-ArgusAgent-DETECT-001-*` | 152 | **153** |
| `TC-ArgusAgent-AUDIT-001-*` | 74 | **75** |

### §0.8 Byte invariants — re-measured, and one of them was WRONG in `epics.md`

| file | CRLF | lone LF | lone CR |
|---|---:|---:|---:|
| `deferred-work.md` | **0** | **8,225** | **1** — at line **5569**, byte offset **425,623** |
| `epics.md` | 3,903 | 0 | 0 |
| `sprint-status.yaml` | 1,402 | 0 | 0 |

⛔ **`deferred-work.md` is LF-uniform, NOT CRLF-uniform.** Story 19.6's AC in `epics.md` said
otherwise and named line 5459; both halves were wrong and were **corrected in place on 2026-08-26**
during this contexting, with the original struck and not erased. An edit that "normalised" this
file to CRLF would rewrite all 8,225 line endings while appearing to preserve the invariant.

⛔ **Edit in binary mode.** Text mode eats the lone CR. `grep -n` and `splitlines()` **agree** that
it sits at 5569 and disagree only on the file TOTAL — 8,225 against 8,226 — which is why every §0
line citation must say which view it used (`AI-E17-10`).

### §0.9 ⛔ GUARDS THIS STORY'S OWN DELIVERABLE WOULD RED (`AI-E17-1`)

| guard | fires when | ruling |
|---|---|---|
| `TC-ArgusAgent-DOCS-001-22` | a `sprint-change-proposal-*.md` or `epic-*-retro-*.md` lands unregistered | ⛔ **Only if** the worklist is named to match those globs. **It must not be.** Put it under `validation-corpus/ratification/`, matching neither pattern — as `blocking-worklist.md` and `silent-class-worklist.md` already do. |
| `TC-ArgusAgent-DOCS-001-80` | a ledger `target_story` points at a `done` story | ✅ unaffected — this story writes no ledger entry |
| any guard reading `eligible_member_count()` | the count moves off 5 | ✅ **must stay 5.** If it moves, this story has performed an operator act and AC6 applies. |

### §0.10 What is already true and must NOT be re-done

- The manifest schema is CLOSED (`MANIFEST_FIELDS`) and `-22` checks it in both directions. ⛔ Do
  not add a field to carry worksheet output — the record is a **separate artifact**.
- `NEVER_ELIGIBLE_FIELDS` makes adding an adoption/popularity field a **failure**, not a silent
  extension. The worksheet inherits that: no stars, no downloads, no run counts.
- `SOURCING_RULE` already states that the sourcing channel is *"not recorded as evidence because it
  is not evidence"*. ⛔ The worksheet records no sourcing channel.

---

## §1 — THE DECISIONS THIS STORY MAKES, AND WHY

### §1.1 The worksheet is a RECORD, not a report

It goes under `validation-corpus/ratification/` beside `adjudication-record.json` and
`silent-class-record.json`, in their shape: a closed schema, a per-member row list, and provenance
fields naming the HEAD it was produced at. **Rationale:** every prior operator-facing artifact in
this repository is a machine record with a human worklist beside it, and a fourth shape would be a
fourth thing to guard.

### §1.2 ⛔ The record carries NO recommendation, and that is the load-bearing decision

**Rejected alternative:** a `recommended: true/false` column, or an ordering by size or yield.
**Why rejected:** §6 R2 reserves *"choosing which repositories are legitimate members"* to the
operator. A worksheet that ranks has made the choice and left the operator a rubber stamp — the
2026-08-22 discipline applied to evidence rather than to staffing: *a role filled to unblock a
result is indistinguishable, on the record, from a role filled to obtain one.*

### §1.3 UNMEASURED is a first-class row value

A member whose checkout is absent or whose pin is unreachable gets a row saying so, with the
reason. ⛔ **It is not dropped from the record.** `ai-body-runtime` contributing **zero** findings
and remaining a member of the population is the standing precedent (`POPULATION_DERIVATION`): *a
member that contributes nothing is a member the ratio was measured over, not a member quietly
dropped from the denominator.*

### §1.4 What this story does NOT fix, named so it is not mistaken for fixed

- The **External adjudicator** (§2 of the protocol) stays **unfilled**. That is `AI-E17-8` and it
  blocks 19.4, not this story.
- `DF-13-5-A` stays **OPEN and UNSPENT**, and whether 19.2 would spend it is an operator ruling
  owed **before** 19.2 — deliberately not answered here or in the proposal.
- The gate stays **BLOCKED**; `protocol_cleared` stays `False`.

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ Guard vacuity — this project's signature defect

A guard over an empty record passes. **Every assertion must carry a non-vacuity precondition**:
assert the row count is 6 before asserting anything per-row, and assert the extractor found a
non-zero number of fields before comparing them. `TC-ArgusAgent-PRECISION-001-46`'s treatment (the
record holds 31 findings across 1 rule class, and a per-class fold would gate on a denominator of
1) is the worked example.

### §2.2 ⛔ The run is LOCAL-ONLY; the guard must not be

CI has no `D:/_bench`. ⛔ **The measurement is a recorded act with its command in the story record,
never a committed test.** Every committed guard reads the **committed record** and the **manifest**,
and must be green on ubuntu with no checkouts present.

### §2.3 ⛔ The tree is SHARED

A peer session commits to this same branch. Stage by **explicit path**; never `git add -A`. If a
peer file must ride along (`sprint-status.yaml` cannot be split), **disclose it by name in the
commit message** — the practice was 5-for-5 across Epic 17's 33 commits with zero collisions,
against three collisions inside Story 16.7 alone (`AI-E17-10`).

### §2.4 ⛔ Local gates are Windows-only, CI is an ubuntu matrix — and CI is DOWN

A green local suite has already shipped POSIX-only bugs to master. Right now PR #9 has **no CI
result at all** because of the Actions outage. ⛔ **Do not record "gates green" as though it were
cross-platform evidence.** State the platform. `AI-E17-3` is open and this story does not close it.

### §2.5 The byte invariants, again, because they are the easiest thing to lose

Binary mode for `deferred-work.md`. Re-measure **before and after** every write, and record both
measurements. See §0.8.

---

## §3 — AC ↔ TASK MAP

| AC | Tasks |
|---|---|
| AC1 — the worksheet exists and is complete | Task 0, Task 2, Task 3 |
| AC2 — nothing is ratified, nothing is fetched | Task 1, Task 2, Task 5 |
| AC3 — the guard is real and non-vacuous | Task 4 |
| AC4 — reuse, never re-derive | Task 0, Task 1 |
| AC5 — scope, paths, portability | Task 5 |
| AC6 — escalate, do not decide | all |

---

## Acceptance Criteria

### AC1 — THE WORKSHEET CARRIES EVERY SEALED MEMBER, AND EVERY COLUMN THE OPERATOR NEEDS

1. A machine record under `validation-corpus/ratification/` carries **exactly 6 rows**, one per
   `sealed` member of `SEALED_PARTITION_TABLE`, keyed by `member_id`.
2. Each row carries: `repository_url`, `commit_sha`, `licence`, `primary_language`, `provenance`,
   `eligible_for_n`, `ineligible_reason`, `adjudication_caveat` — **read from the manifest, not
   re-looked-up** — plus `checkout_path`, `pin_reachable`, `files_at_pin`, `python_files_at_pin`,
   and `heuristic_findings_at_pin`.
3. A human worklist sits beside it in the `blocking-worklist.md` house form. ⛔ Its filename
   matches **neither** `sprint-change-proposal-*.md` nor `epic-*-retro-*.md` (§0.9).
4. A member that cannot be measured carries `UNMEASURED` **with its reason** and is **not dropped**
   (§1.3).
5. ⛔ **No row carries a recommendation, rank, score or ordering by desirability** (§1.2).

### AC2 — NOTHING IS RATIFIED AND NOTHING IS FETCHED

1. `eligible_member_count()` is **5** before and after, asserted by execution in the story record.
2. `tests/corpus/_manifest.py`, `precision-validation-protocol.md` and `adjudication-record.json`
   are **byte-unchanged**, proven with `git diff --stat`.
3. ⛔ The producing module **reaches no network**, asserted **structurally over its AST** in the
   shape `TC-ArgusAgent-PRECISION-001-141` already uses — not promised in prose.
4. The record states in its own fields that it ratifies nothing and that `eligible_for_n` moved for
   no member.

### AC3 — THE PRIOR MEASUREMENTS ARE RE-VERIFIED, AND ANY MOVEMENT IS REPORTED

1. Story 15.1's per-candidate figures are re-checked at the same pins (§0.6).
2. ⛔ **A row that moved is REPORTED, not absorbed** (`AI-E17-11`) — named, with both values and the
   command that measured it.
3. Every §0 row is re-measured at Task 0 and the result recorded, including the rows that did not
   move.

### AC4 — REUSE, NEVER RE-DERIVE

1. The finding count comes from `scripts/audit_validation_corpus.py` (§0.5). No second walker.
2. ⛔ For **every** new function answering a factual question, `argus/` and `scripts/` are grepped
   for an existing exported derivation and **the command and its result are recorded in the Dev
   Agent Record** (`AI-E17-5`).

### AC5 — THE GUARD IS COMMITTED, NON-VACUOUS, AND PORTABLE

1. A guard at the next free id (§0.7) reads the **committed record** and the **manifest** — never
   the corpus — and is green on ubuntu with no checkouts present.
2. It carries an explicit **non-vacuity precondition** (§2.1): it fails if the record holds zero
   rows, and it fails if the extractor parsed zero fields.
3. It is proven **RED before and GREEN after** by execution, with both results recorded.
4. Paths are portable: no `\\`, no drive letters in committed code. The `D:/_bench` root is a
   **command-line argument**, never a constant.

### AC6 — ESCALATE, DO NOT DECIDE

1. If measuring a member would require a fetch, a clone, or any network access — **STOP**, record
   the member `UNMEASURED`, and report it. Do not repair it.
2. If `eligible_member_count()` moves off 5, or any `eligible_for_n` flips — **STOP**. An operator
   act has been performed by accident.
3. If the worksheet's evidence would change the answer to the `DF-13-5-A` question, **record the
   observation and STOP.** That ruling is the operator's and is owed before 19.2.
4. Scope widening is escalated and **recorded before the write is taken**, in `DN-17-5-12`'s form.

---

## Tasks & Subtasks

### ⛔ Task 0 — RE-MEASURE §0 BEFORE WRITING ANYTHING (AC3.3, AC1.1)

- [ ] Re-probe all six pins with `git cat-file -e <sha>^{commit}`; re-walk each tree.
- [ ] Re-dump the six manifest rows field by field; confirm §0.2's claim that the package is
      already carried.
- [ ] Re-measure `eligible_member_count()`, the sealed/ratified intersection, and the byte
      invariants of §0.8.
- [ ] Re-scan the four TC-id families for their maxima.
- [ ] ⛔ Record the result of **every** row — moved and unmoved — with the command used.

### Task 1 — THE DERIVATION SEARCH, RECORDED (AC4.2)

- [ ] For each factual question the worksheet answers, grep for an existing derivation.
- [ ] Record command + result in the Dev Agent Record **before** writing any new function.

### Task 2 — THE RECORD (AC1.1, AC1.2, AC1.4, AC1.5, AC2.4)

- [ ] Build the closed schema; populate from the manifest; leave the two measured columns empty.
- [ ] ⛔ Assert no recommendation/rank/score field exists.

### Task 3 — THE TWO MEASURED COLUMNS (AC1.2, AC1.4)

- [ ] Run `audit_validation_corpus.py` per member with a **SHORT** `--snapshot-root` and an
      **explicit `--output-name`** under the ratification prefix (§0.5).
- [ ] ⛔ `git status` `validation-corpus/` after the FIRST run, before doing the other five —
      confirm `adjudication-set.json` is untouched. The default `--output-name` would clobber it.
- [ ] Record the exact command per member in the story record.
- [ ] Any member that fails to measure → `UNMEASURED` + reason.

### Task 4 — THE GUARD (AC5)

- [ ] Write it at the next free id; non-vacuity precondition first.
- [ ] Drive it **RED** against the tree before the record lands; record the failure text.
- [ ] Land the record; confirm **GREEN**; record it.

### Task 5 — SCOPE, GATES, HAND-OFF (AC2.1, AC2.2, AC5.4, AC6)

- [ ] `git diff --stat` proving the three frozen artifacts are untouched.
- [ ] Full suite; ⛔ **state the platform** — Windows only unless CI has recovered (§2.4).
- [ ] Stage by explicit path; disclose any carried peer file by name.
- [ ] Re-measure byte invariants after every write.

---

## Dev Notes

### Locked decisions this story CITES rather than reopens

- Protocol **§6 R2** — ratification and fetching are operator acts. Not reopened.
- **AR7 / DN-3 / DF-8-5-C** — one derivation per factual question.
- **`POPULATION_DERIVATION`** — a member contributing nothing stays in the denominator.
- **`NEVER_ELIGIBLE_FIELDS` / `SOURCING_RULE`** — adoption, popularity and sourcing channel are
  not evidence and are not fields.
- **2026-08-20 operator decision** — a decision folded across an amendment re-interprets judgements
  nobody re-made. No protocol row is added here.

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

`DF-13-5-A` (OPEN, UNSPENT — declined twice, most recently 2026-08-24 at `7edf74e`).
The six `"17-5"`-tagged entries and the 43 `"unverified"` pairs are **19.6's**, not this story's.
⛔ Grep the ledger before filing anything new — it usually already knows.

### Dependencies — none are added, and that is a requirement

No new package, no new import outside the standard library and what `argus/` already carries.

### Previous-story intelligence

- **17.4** — the closest analogue: a local-only measurement over pinned checkouts, whose guards
  read the committed record rather than the corpus. Its §0.6 is the template for §0.1 here, and its
  `agent-smith`-lives-one-level-deeper trap is why §0.1 spells out the path mapping.
- **17.5** — three fix rounds, all Low and docs-only, consuming the entire safety margin
  (`AI-E17-9`). Keep prose findings out of the fix loop where the AC does not require the form.
- **15.1** — chose this bench before anyone looked, and measured these six at these pins. Its
  figures are the re-verification target.

### References

- [epics.md — Epic 19](../epics.md) · [sprint-change-proposal-2026-08-26.md](../sprint-change-proposal-2026-08-26.md)
- [precision-validation-protocol.md §2, §4, §6](../precision-validation-protocol.md)
- `tests/corpus/_manifest.py` · `scripts/audit_validation_corpus.py` · `scripts/candidate_selection.py`
- `argus/precision/gate_yield.py` — `YIELD_PROVENANCE_DISCLOSURE` (§0.4)

---

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
