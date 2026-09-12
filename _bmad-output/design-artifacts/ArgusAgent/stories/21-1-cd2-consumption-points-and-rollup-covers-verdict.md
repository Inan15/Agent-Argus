---
baseline_commit: fd56de3f8e63a6ab0784a5a727fb1afbdfea3262
---

# Story 21.1: Register the Two §CD-2 Consumption Points and the Roll-Up `Covers:` Verdict

Status: review

<!-- Contexted 2026-09-07 at HEAD `fd56de3f8e63a6ab0784a5a727fb1afbdfea3262` (branch
     `story/21-1-cd2-consumption-points-and-rollup-covers-verdict`, cut from `dev`) by Eunomia
     (XAgents-Assistant, work order wq-039), NOT by the bmad-create-story workflow — that
     workflow was not run for this story; this file was authored by hand from the Epic 21 seed
     (`epics.md` §"Story 21.1", commit `fd56de3`) and the sprint-status backlog entry
     (`21-1-cd2-consumption-points-and-rollup-covers-verdict: backlog`). No code, test, or
     `argus/` byte has been touched to produce this file. The dev-loop state machine
     (`.claude/skills/bmad-dev-loop/SKILL.md` §3) treats `backlog` -> (create-story) ->
     `ready-for-dev` as one step, so the sprint-status entry for this story is moved to
     `ready-for-dev` in the same change that adds this file — nothing else on the tracker
     is touched.
-->

## Story

As the **dev-loop orchestrator, at the moment an epic's `Covers:` list is about to be trusted**,
I want **the `check_meta_drift.py` §CD-2 advisory reader to have two named consumption points —
an epic ENTRY gate that HALTs on a missing `Capability delivered:` / `Covers:` field, and a
roll-up step that re-derives every `Covers:` id against its on-disk status before `epic-<id>`
is set `done`** ,
so that **an epic cannot close on a `Covers:` list falsified by its own execution (the defect
Story 17.5 found and hand-corrected, per AI-E17-13), and the encoding regression the seed
tripped over (`check_meta_drift.py`'s advisory path crashing instead of exiting 0 on a clean
parse) cannot recur.**

## Acceptance Criteria

Copied verbatim from the Epic 21 seed (`epics.md`, "### Story 21.1", commit `fd56de3`) — this
story does not restate them in different words:

1. `bmad-dev-loop` §3 gains an **epic ENTRY** gate: the seed's `**Capability delivered:**` and
   `**Covers:**` fields must be present (or `Nothing` + dated ruling) → else **HALT**; and a
   `META-DRIFT:` verdict is recorded in the epic's first story.
2. `bmad-dev-loop` §3 roll-up **re-derives every `Covers:` id against its on-disk status** and
   records a per-id verdict before `epic-<id> = done`; an unmet list forces a dated §3.4
   correction in `epics.md`.
3. ⛔ The entry gate HALTs on **missing fields only**; the `check_meta_drift.py` read **never**
   HALTs and **never** becomes blocking — asserted by a test that the advisory path exits 0 on
   a clean parse.
4. `DF-DRIFT-UNREAD-A` is filed with its prior-art grep recorded.

## Tasks / Subtasks

- [x] Task 1: Add the epic ENTRY gate to `.claude/skills/bmad-dev-loop/SKILL.md` §3 (AC: #1)
      — **DONE. Owner applied the preserved text by hand 2026-09-08. See Dev Agent Record.**
  - [x] State the gate as a precondition on the state-machine table or its surrounding prose:
        before a `backlog` epic's first story may route to `bmad-sm`, `epics.md`'s seed for
        that epic must carry a non-empty `**Capability delivered:**` and `**Covers:**` (or
        `Capability delivered: Nothing` plus a dated ruling citation, per the Epic 21 and
        Epic 20 precedent) — else **HALT**.
  - [x] Require that the epic's first story records a `META-DRIFT:` verdict line (the
        `check_meta_drift.py` read for that epic, taken at the same HEAD the story was
        contexted at).
  - [x] Keep the gate worded as **HALT on missing fields only** — it must not become a judgment
        call on whether the capability or coverage stated is *correct*; that question belongs
        to the roll-up (AC #2), not the entry.

- [x] Task 2: Add the roll-up `Covers:` re-derivation to `.claude/skills/bmad-dev-loop/SKILL.md`
      §3 (AC: #2) — **DONE. Owner applied the preserved text by hand 2026-09-08. See Dev Agent Record.**
  - [x] Before the orchestrator writes `epic-<id> = done` (§3's existing "Then set `epic-<id> =
        done` yourself" step), require it to read the epic's `**Covers:**` line from `epics.md`,
        resolve each id against its current on-disk status (a sprint-status story key, a
        `deferred-work.md` entry, or another named destination), and record a per-id verdict
        (met / unmet) before writing `done`.
  - [x] State the unmet-list consequence: any id not delivered forces a dated §3.4 correction in
        `epics.md` (the same form Story 17.5 used by hand for AI-E17-13) rather than a silent
        `done`.
  - [x] Cite AI-E17-13 and Story 17.5's hand correction as the evidence this rule generalizes
        from (both already in `deferred-work.md` / `epics.md` — no new research needed).

- [x] Task 3: Prove the advisory path never blocks (AC: #3)
  - [x] Add or extend a test asserting `python scripts/check_meta_drift.py` exits `0` on a clean
        parse of the current `epics.md` (a "cannot read its inputs" nonzero exit is the only
        legitimate nonzero case, per the module's own docstring at
        `scripts/check_meta_drift.py:1-12`). Done as
        `test_advisory_path_exits_zero_on_a_clean_parse_of_the_real_repo` (and the `--json`
        sibling), run against a real subprocess with `PYTHONUTF8`/`PYTHONIOENCODING` explicitly
        stripped so the assertion cannot pass merely because this workspace's own tooling forces
        UTF-8 (`windows-environment.md` requires `PYTHONUTF8=1` for every `uv run`).
  - [x] Cover the encoding regression named in the Epic 21 seed commit (`fd56de3`): a
        `**Capability delivered:**` value beginning with a non-cp1252-encodable character (the
        seed used `⛔`, U+26D4) must not crash `report_epics`'s `print(f"      capability:
        {cap[:64]}")` (`scripts/check_meta_drift.py:150` at baseline) on a default Windows
        console. Chose the **durable fix** the seed commit itself named as the right one
        ("the DURABLE fix belongs in the script (encode defensively)"): added
        `_console_safe()` to `scripts/check_meta_drift.py` and routed `cap[:64]` through it
        before the print. Reproduced the original crash first (bare `uv run python -c
        "print('⛔ ...')"` with no `PYTHONUTF8`/`PYTHONIOENCODING` set → real
        `UnicodeEncodeError`, exit 1, on this machine's default `cp1252` stdout), then proved the
        fix with a strict-`cp1252` `sys.stdout` stand-in
        (`test_console_safe_survives_a_leading_non_cp1252_glyph`), then proved non-vacuity by
        temporarily reverting the one-line wiring and confirming exactly the two regression
        tests fail with the real `UnicodeEncodeError`, then restored it and confirmed green again.
  - [x] Confirm this test lands as a **new** assertion, not a relaxation of any existing one —
        no test file for `check_meta_drift.py` existed before this story (confirmed absent at
        this story's baseline commit); nothing pre-existing was touched or weakened.

- [x] Task 4: File `DF-DRIFT-UNREAD-A` (AC: #4)
  - [x] Add an entry to `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`. Checked the
        file's current schema before writing (per this task's own instruction): it is CC-3
        (id · origin_story · owner · target_story|sunset_date · category · severity), NOT
        `sprint-status.yaml`'s `action_items:` shape (epic, id, action, owner, destination,
        priority, status) — the two are genuinely different, confirmed by reading both. Filed as
        a new dated `## Deferred from:` section (pure append, `deferred-work.md`'s own
        convention), with explicit CC-3 fields plus prose matching the file's most recent entry
        style.
  - [x] Recorded the prior-art grep in the entry body: `check_meta_drift.py` existed and fired
        correctly across Epics 17, 18, 19 and 20 — four consecutive epics — and its report was
        read by no one before Epic 21 named the gap. Cited `AI-E17-13` and Story 17.5's hand
        correction as the evidence the signal fired and was not acted on.
  - [x] Named the destination and owner consistent with `AI-E17-13`'s own row: `dev-loop
        orchestrator (the epic ENTRY gate and the roll-up step, bmad-dev-loop/SKILL.md §3)`. The
        entry also states plainly, per this repo's own "no bookkeeping lie" convention
        (`AI-E17-12`'s precedent), that Tasks 1 and 2 are **not yet landed** — see Dev Agent
        Record.

---

## Dev Notes

### What this story is, and is not
- This is a **process-derived, corrective** story inside a **process-derived, corrective**
  epic (Epic 21). Its own seed says so: `epics.md` records `Capability delivered: NOTHING A
  USER CAN REACH` for the whole epic, entered under the dated operator ruling of 2026-08-29
  (`sprint-change-proposal-2026-08-29b.md`), per §Enforcement. Story 21.1 inherits that framing
  — it does not manufacture a product capability to justify itself.
- **Zero `argus/` bytes are touched by this story.** Every change lands in
  `.claude/skills/bmad-dev-loop/SKILL.md`, `scripts/check_meta_drift.py`'s test coverage, and
  `deferred-work.md`. Confirm this stays true through implementation — if a change is found to
  need an `argus/` edit, that is itself a scope signal and should be raised, not absorbed
  silently.
- **Do not resolve `bmad-dev-loop-pack/files/skills/bmad-dev-loop/SKILL.md`** (the packaged
  copy under `bmad-dev-loop-pack/`) as part of this story unless the epic's seed or a later
  ruling says the pack must track the installed skill 1:1 — the ENTRY gate and roll-up
  behavior described by the AC target the **installed** skill
  (`.claude/skills/bmad-dev-loop/SKILL.md`), which SKILL.md §1 point 6 already names as this
  repo's source of truth over any upstream/pack copy.

### Source Tree Components to Touch
- `.claude/skills/bmad-dev-loop/SKILL.md` [MODIFY]: §3 gains the epic ENTRY gate and the
  roll-up `Covers:` re-derivation step.
- `scripts/check_meta_drift.py` or its test file [MODIFY/NEW]: a test proving the advisory path
  exits 0 on a clean parse, including the non-ASCII `Capability delivered:` case.
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` [MODIFY]: new entry
  `DF-DRIFT-UNREAD-A`.

### Prior Art Already on Disk (read before writing anything)
- `epics.md` §"Epic 21" (line 3933) and §"Story 21.1" (line 3957) — the seed and its AC,
  quoted verbatim above.
- `sprint-status.yaml` `action_items:` block, id `AI-E17-13` (search for that id) — the
  observation this story exists to fix: nothing re-derives an epic's `Covers:` list at roll-up,
  and Story 17.5 had to correct Epic 17's falsified header by hand because it happened to be
  chartered to look.
- `scripts/check_meta_drift.py` — the existing advisory reader. `report_epics()` (line 124) is
  the function whose `Capability delivered:` print (line 150) crashed on a cp1252 console per
  the Epic 21 seed commit message; `classify()` (line 86) is where `Covers:`/`Capability
  delivered:` are parsed out of `epics.md`.
- Epic 21 seed commit `fd56de3` (`git show fd56de3`) — names the regression this story's AC #3
  routes to it, and states it is not yet fixed durably (only worded around, in the seed text
  itself).
- `deferred-work.md` — checked for a schema this story's Task 4 must follow; no
  `DF-DRIFT-UNREAD-*` id exists there yet as of this story's baseline commit.

### No prior story in this epic to build on
Epic 21 has four seeded stories (21.1–21.4) and no story files existed for any of them before
this one. This is the first. There is no "Previous Story Intelligence" section to carry
forward, unlike the Epic 20 stories this file's shape is patterned on.

### Sequencing note carried from the seed
The Epic 21 seed commit records that the same latent `cp1252` encoding break exists in the
proposal's drafted Epic 20 correction text, routed to Story 21.4. Story 21.1's AC #3 test
should be written so Story 21.4 can point at it rather than re-deriving its own.

### References
- [Epic 21 seed, Story 21.1](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/epics.md#L3957)
- [sprint-change-proposal-2026-08-29b.md](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-29b.md)
- [check_meta_drift.py](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/scripts/check_meta_drift.py)
- [bmad-dev-loop SKILL.md §3](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/.claude/skills/bmad-dev-loop/SKILL.md#L61)
- [deferred-work.md](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/deferred-work.md)
- [Epic 21 seed commit fd56de3](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent) — `git show fd56de3`

---

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5 (Cadmus, XAgents-Assistant, work order wq-039), 2026-09-08.

### Debug Log References

**HALT on Task 1 and Task 2 — a real, confirmed tooling/permission blocker, not a story defect.**

Before implementing, this story was judged on its own merits per wq-039's instruction: the four
Acceptance Criteria were checked verbatim against `epics.md` §"Story 21.1" (line 3957) and matched
exactly; every Dev Notes line reference was checked against the live files (`scripts/check_meta_
drift.py`'s `report_epics`/`cap[:64]` print, `deferred-work.md`'s actual current schema, the
`AI-E17-13` action_items row) and all held; the story's own hedge on Task 4 ("check the file's
current schema before writing, do not assume it matches sprint-status.yaml's") was independently
confirmed necessary — the two schemas really do differ. No contradiction or gap was found in the
story content itself. Judgment: **genuinely ready for dev.**

Implementation then hit a real environment blocker on Task 1: both the `Edit` and the `Write`
tool were **permission-denied** on `.claude/skills/bmad-dev-loop/SKILL.md` — confirmed twice with
`Edit` and once with `Write`, all three attempts returning an explicit tool-permission denial (not
a file-not-found, not a git error, not a story-content problem). `Edit` and `Write` both succeeded
without issue on every other file this story touches (`sprint-status.yaml`,
`scripts/check_meta_drift.py`, `deferred-work.md`, this story file — all in the same repository,
same session, same agent), which isolates the denial to this specific path rather than to the
repository or the tool generally. No deny rule for this path was found in
`.claude/settings.local.json` (the only settings file in this repo) or in the caller's
`.claude/settings.json`, so this reads as harness-level protection of `.claude/skills/**` rather
than a project-configured rule — plausibly deliberate, since skill files are themselves executable
instructions and a repo-local dev agent silently rewriting the orchestrator's own state-machine
prose is exactly the kind of self-modification a harness would want to gate. Per this agent's own
operating rule ("you should not attempt to work around this denial... if you believe this
capability is essential to complete the request, STOP and explain"), no further routing around it
(e.g. a raw shell write) was attempted after the second confirmation.

**Consequence for Task 1 and Task 2**: both require edits inside
`.claude/skills/bmad-dev-loop/SKILL.md` §3 (the epic ENTRY gate and the roll-up `Covers:`
re-derivation) and neither could be made. The exact prose this agent intended to add is preserved
below so the next dev agent (or the owner, editing directly) does not have to re-derive it:

> **Epic ENTRY gate (checked once, before a `backlog` epic's first story routes to `bmad-sm`).**
> Read that epic's seed block in the epics artifact (`epics.md` in this project): its
> `**Capability delivered:**` and `**Covers:**` fields must both be present — or, when the epic
> delivers nothing a user can reach, `**Capability delivered:** Nothing` (or `NONE`) plus a dated
> operator ruling cited in the same seed block. If either field is missing outright → **HALT**,
> naming the epic and the missing field; do not spawn `bmad-sm`. When the gate passes, require
> that the epic's first story records a `META-DRIFT:` verdict line: the project's advisory
> meta-work drift reader's output for that epic (this project's is `scripts/check_meta_drift.py`;
> discover the equivalent the same way §1 discovers workflow commands if a project configures a
> different one), read at the same HEAD the story is contexted at. This gate HALTs on **missing
> fields only** — it is never a judgment call on whether the stated capability or coverage is
> *correct*; that question belongs to the roll-up re-derivation, not the entry. The advisory
> reader itself never HALTs and never becomes blocking here or anywhere else in this loop — it is
> read, not enforced. *(Insert immediately before "For the current target story key, read its
> status and route:" in §3, keeping the file generic/portable per its own §0 promise — hence the
> parenthetical about discovering an equivalent reader rather than hardcoding the path.)*
>
> **Roll-up addition, inside the existing "Epic-level:" paragraph, as a new step 2 (renumbering
> the existing step 2 "Then set `epic-<id> = done`..." to step 3):** *"Roll-up `Covers:`
> re-derivation (before writing `done`). Read the epic's `**Covers:**` line from `epics.md` and
> resolve each id it names against its current on-disk status — a `sprint-status.yaml` story key,
> a `deferred-work.md` entry, or another destination the id itself names. Record a per-id verdict
> (met / unmet) as part of this step. If any id is unmet, do not write `epic-<id> = done` silently:
> the unmet list forces a dated §3.4 correction in `epics.md` first (the same form Story 17.5 used
> by hand for `AI-E17-13`), and only then does the epic close."*

**What was done instead, and why it stands on its own.** Task 3 and Task 4 do not touch
`.claude/skills/**` and are genuinely independent of Task 1/2 (Task 3 is a test against
`scripts/check_meta_drift.py`'s existing, already-shipped advisory behaviour; Task 4 is a ledger
filing). Both were completed and verified in full rather than left undone alongside 1 and 2 —
per wq-039's own framing, a blocked task is "a real finding, not a failure," and finishing the
unblocked, independent work is not the same as building around the blocker. Task 3 additionally
found and fixed a **real, reproduced regression**: with `PYTHONUTF8`/`PYTHONIOENCODING` unset (the
default in a bare child process on this machine — confirmed: `sys.stdout.encoding` is `cp1252`),
`report_epics`'s `print(f"      capability: {cap[:64]}")` crashes with `UnicodeEncodeError` when
the capability text contains a non-cp1252-encodable character within the first 64 characters —
reproduced directly (`print('⛔ ...')` under a bare `uv run python -c`) before writing any
fix, exactly matching the Epic 21 seed commit's (`fd56de3`) own account of the original break. Per
that commit's own stated preference ("the DURABLE fix belongs in the script (encode
defensively)"), the durable fix was chosen over the test-only "pin PYTHONIOENCODING and say why"
alternative the Dev Notes also permitted: added `_console_safe()` and routed `cap[:64]` through it.
Non-vacuity of the new regression tests was verified by temporarily reverting the one-line wiring,
confirming exactly the two tests that should fail did (with the real `UnicodeEncodeError`, not a
mocked one), then restoring the fix and confirming all six tests pass again.

**Update, 2026-09-08 (Cadmus, XAgents-Assistant, wq-083) — Task 1 and Task 2 now DONE.** The
`.claude/skills/**` Edit/Write denial above is harness-level, confirmed independently a second and
third time the same night (Aeacus, then Neo's own primary session), not specific to this agent or
this dispatch — no workaround exists from any agent context. The owner applied the two preserved
prose blocks above directly to the live file by hand through Iris. Neo caught one real gap in the
owner's first manual paste: the original file's own step 2 ("Then set `epic-<id> = done`... yourself
...") had been dropped outright instead of renumbering to step 3, per the preserved instruction
above; the owner fixed it with a third small paste. Cadmus re-read the live file for this update and
confirms all three pieces are present, correctly ordered, and match: the Epic ENTRY gate (line 62)
is the preserved text verbatim, inserted immediately before "For the current target story key, read
its status and route:" as specified; the roll-up re-derivation (line 77, item 2 of the "Epic-level:"
list) is the preserved text verbatim, including the word "first" in "...correction in `epics.md`
first (the same form Story 17.5 used by hand for `AI-E17-13`)..."; and item 3 (line 78, "Then set
`epic-<id> = done` yourself (write to sprint-status, preserving comments) and advance to the next
epic.") is the file's own original step 2 prose, genuinely just renumbered, not rewritten or altered
— it reads coherently as the list's closing step and its wording matches what the Debug Log
References above already described as the pre-existing text. Tasks 1 and 2 are complete. No further
action needed on `.claude/skills/bmad-dev-loop/SKILL.md` from any agent; per this workspace's
Windows-environment rule, that path stays Edit/Write-denied at the harness level for every agent and
any future change to it must go through the owner the same way.

Also fixed as a prerequisite, unrelated to story content: `ArgusAgent/.venv` was a Linux-origin
`uv` environment (`pyvenv.cfg` named a WSL Python), unusable on native Windows and the reason `uv
run` failed with a permission error trying to remove its `lib64` symlink. Removed and re-synced
(`uv sync --extra dev`) to a native Windows venv before any test could run. Not part of this
story's scope; noted so a future session does not re-diagnose it.

`sprint-status.yaml`'s `21-1-...` key was moved `ready-for-dev` → `in-progress` per
`bmad-dev-story` SKILL.md step 4 before work began. As of this 2026-09-08 update (Cadmus, wq-083),
all four tasks are now complete (Tasks 1 and 2 landed via the owner's manual paste, see above), so
per `bmad-dev-story` SKILL.md step 9 ("if any task is incomplete → HALT — complete remaining tasks
before marking ready for review"; now satisfied since nothing is incomplete), the story's Status is
set to `review` in both this file and `sprint-status.yaml`. `epic-21`'s own status (still `backlog`)
is left untouched — that transition belongs to the SM phase per SKILL.md §3 ("the SM marks
`epic-<id>` → `in-progress` on the epic's first story"), not to this round, same as originally
noted.

### Completion Notes List

- Story judged genuinely ready for dev on its own merits (ACs and Dev Notes verified against
  live files); not a rubber stamp.
- Task 1, Task 2: **DONE** (2026-09-08 update). `.claude/skills/bmad-dev-loop/SKILL.md` is
  Edit/Write-denied at the harness level for every agent (confirmed independently three times).
  The owner applied the preserved prose by hand; Neo caught and the owner fixed one manual-paste
  gap (a dropped renumbered step); Cadmus re-verified the final live text matches, in order, and
  is unaltered elsewhere at the edit site.
- Task 3: **DONE.** `tests/test_check_meta_drift.py` (6 tests, all passing); found and durably
  fixed the real §CD-2 encoding regression named in the Epic 21 seed commit
  (`scripts/check_meta_drift.py`'s new `_console_safe()`); non-vacuity of the regression tests
  verified by reverting and restoring the fix.
- Task 4: **DONE.** `DF-DRIFT-UNREAD-A` filed in `deferred-work.md` (pure append, `CR` byte
  invariant unchanged: 1 before and after; `LF` 8516 → 8558), CC-3 fields, prior-art grep
  recorded, honest note that Tasks 1–2 are not yet landed.
- Full regression suite run twice (before and after all changes): `pytest -q` exit `0` both
  times, only the one pre-existing, unrelated skip (`tests/test_naming_consistency.py:151`,
  "got empty parameter set"). `mypy scripts/check_meta_drift.py tests/test_check_meta_drift.py`
  clean. `bandit -r` on both touched files: 0 Medium/High.
- Story moved to `review` (2026-09-08 update) — all 4 tasks now complete, per the workflow's own
  Definition of Done (SKILL.md step 9). Not yet re-screened by an independent reviewer: the story
  itself flags that `.claude/skills/bmad-dev-loop/SKILL.md`'s final state (three manual pastes in
  one evening) should get one more adversarial look before this closes for real.
- Nothing in `argus/` touched (confirmed by `git diff --stat`); the story's own "Zero `argus/`
  bytes are touched by this story" constraint holds.

### File List

- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` [MODIFY] — `21-1-...` key
  `ready-for-dev` → `in-progress`.
- `scripts/check_meta_drift.py` [MODIFY] — added `_console_safe()`; routed the
  `**Capability delivered:**` print through it (§CD-2 encoding regression, durable fix).
- `tests/test_check_meta_drift.py` [NEW] — 6 tests for AC #3 (no prior test file for this
  module existed).
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` [MODIFY] — pure append,
  `DF-DRIFT-UNREAD-A` (AC #4).
- `_bmad-output/design-artifacts/ArgusAgent/stories/21-1-cd2-consumption-points-and-rollup-covers-verdict.md`
  [MODIFY] — this file: Status, Tasks/Subtasks, Dev Agent Record.
- `.claude/skills/bmad-dev-loop/SKILL.md` [MODIFY, by the owner, not by any agent] — Epic ENTRY
  gate and roll-up `Covers:` re-derivation added (Task 1, Task 2), 2026-09-08. See Dev Agent
  Record for the harness-level denial that required this, and the manual-paste gap Neo caught and
  the owner fixed.

### Review Findings
