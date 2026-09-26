---
baseline_commit: 7b7b2a0f995fc5ae2bd8c1ce6133a2277804b95b
---

# Story 21.3: Split the Fix-Round Budget by Finding Class

Status: review

<!-- Contexted 2026-09-21 at HEAD `7b7b2a0f995fc5ae2bd8c1ce6133a2277804b95b` by a headless
     decomposition pass (XAgents-Assistant, work order wq-579), NOT by the interactive
     bmad-create-story elicitation flow — that skill's discovery/elicitation steps need a human
     in the loop this dispatch does not have. This file is authored by hand from the Epic 21 seed
     (`epics.md` §"Story 21.3", commit `fd56de3`) and the sprint-status backlog entry
     (`21-3-fix-round-budget-by-finding-class: backlog`), following the shape Story 21.1 already
     established for this epic. No code, test, or `argus/` byte has been touched to produce this
     file. Per the dev-loop state machine (`.claude/skills/bmad-dev-loop/SKILL.md` §3),
     `backlog` -> (create-story) -> `ready-for-dev` is one step, so the sprint-status entry for
     this story moves to `ready-for-dev` in the same change that adds this file — nothing else on
     the tracker is touched by this pass. -->

## Story

As the **dev-loop orchestrator, at the point where a story's fix-round budget is spent**,
I want **`bmad-dev-loop` §4 to count `exec_iteration` and `docs_iteration` separately, each
capped at 3, with a round classed DOCS-ONLY only if every file it names is non-executable and any
mixed round counted as EXECUTABLE**,
so that **a run of Low, prose-only findings cannot silently spend the same three-round margin a
genuine executable defect needs (the failure mode Story 17.5 hit: all three rounds spent on
docs-only findings, the last one labelled "LAST PERMITTED FIX ROUND", leaving nowhere for a real
defect to go had one surfaced at iteration 3).**

## Acceptance Criteria

Copied verbatim from the Epic 21 seed (`epics.md`, "### Story 21.3", commit `fd56de3`) — this
story does not restate them in different words:

1. `bmad-dev-loop` §4 counts `exec_iteration` and `docs_iteration` separately, each capped at 3.
2. A round is DOCS-ONLY iff every file it names is non-executable; a **mixed round counts as
   EXECUTABLE**.
3. Story 17.5's three Low docs-only rounds are cited as the evidence.

## Tasks / Subtasks

- [ ] Task 1: Split the fix-round counter in `.claude/skills/bmad-dev-loop/SKILL.md` §4 (AC: #1)
  - [ ] Read §4's current fix-loop prose and pseudocode (the single `iteration` counter capped
        at 3) before editing, per this repo's own re-measurement convention — do not assume the
        cap or its current wording without checking the live file first.
  - [ ] Replace the single counter with two: `exec_iteration` and `docs_iteration`, each
        independently capped at 3, so a docs-only round does not consume the budget an
        executable-finding round needs.
  - [ ] ⚠️ `.claude/skills/bmad-dev-loop/SKILL.md` is Edit/Write-denied at the harness level for
        every agent, confirmed independently three times during Story 21.1's implementation (see
        that story's Dev Agent Record). If the same denial recurs here, preserve the exact
        intended prose in this story's Dev Agent Record (the pattern Story 21.1 used) rather than
        attempting a workaround, and report the blocker rather than silently absorbing it.

- [ ] Task 2: Define the DOCS-ONLY / EXECUTABLE classification rule (AC: #2)
  - [ ] State the rule precisely: a round is DOCS-ONLY **iff every file it names is
        non-executable**; if even one file in the round is executable (code, tests, scripts —
        anything that runs), the whole round counts as EXECUTABLE and increments
        `exec_iteration`, not `docs_iteration`.
  - [ ] Confirm this is stated where the fix-loop routes findings to a round (§4), not left
        implicit or inferable only from the counter split in Task 1.

- [ ] Task 3: Cite the evidence already on record (AC: #3)
  - [ ] Cite Story 17.5's three Low, docs-only fix rounds — the last one labelled "LAST PERMITTED
        FIX ROUND" — as the concrete case this rule prevents recurring, per
        `sprint-change-proposal-2026-08-29b.md` §4.3 (item 3b).

---

## Dev Notes

### What this story is, and is not
- This is a **process-derived, corrective** story inside a **process-derived, corrective** epic
  (Epic 21) — see [[Story 21.1]]'s own framing, which this story inherits unchanged:
  `epics.md` records `Capability delivered: NOTHING A USER CAN REACH` for the whole epic, entered
  under the dated operator ruling of 2026-08-29 (`sprint-change-proposal-2026-08-29b.md`).
- **Zero `argus/` bytes are touched by this story.** The only file this story's AC names is
  `.claude/skills/bmad-dev-loop/SKILL.md` §4.
- No prerequisite on another Epic 21 story: this story's §4 change is independent of Story 21.1's
  §3 change (different subsection of the same file) and independent of Story 21.2's
  `architecture.md` change. It can be dispatched in any order relative to those two.

### Source Tree Components to Touch
- `.claude/skills/bmad-dev-loop/SKILL.md` [MODIFY]: §4 gains the split `exec_iteration` /
  `docs_iteration` counters and the DOCS-ONLY/EXECUTABLE classification rule.

### Prior Art Already on Disk (read before writing anything)
- `epics.md` §"Epic 21" (line 3933) and §"Story 21.3" (line 3973) — the seed and its AC, quoted
  verbatim above.
- `sprint-change-proposal-2026-08-29b.md` §4.3 (item 3b) — the exact rule text and the Story 17.5
  evidence this story's change is drawn from.
- `sprint-status.yaml` `action_items:` block, id `AI-E17-9` — the item this story discharges
  ("no docs-only fix-round lane").
- [[Story 21.1]] (`21-1-cd2-consumption-points-and-rollup-covers-verdict.md`) Dev Agent Record —
  read first for the confirmed `.claude/skills/bmad-dev-loop/SKILL.md` Edit/Write harness denial
  and the pattern used to preserve intended prose across the blocker (preserved text handed to the
  owner, applied by hand). Task 1 is very likely to hit the identical denial on the same file.

### References
- [Epic 21 seed, Story 21.3](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/epics.md#L3973)
- [sprint-change-proposal-2026-08-29b.md §4.3](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-29b.md)
- [bmad-dev-loop SKILL.md §4](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/.claude/skills/bmad-dev-loop/SKILL.md)
- [Story 21.1 Dev Agent Record — the SKILL.md harness denial](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/stories/21-1-cd2-consumption-points-and-rollup-covers-verdict.md)

---

## Dev Agent Record

### Agent Model Used

Claude Sonnet 5, XAgents-Assistant, work order wq-593, 2026-09-21.

### Debug Log References

**HALT on all three tasks — a real, confirmed harness-level blocker, not a story defect.**

Read `.claude/skills/bmad-dev-loop/SKILL.md` §4 (lines 84-121) at this story's baseline before
attempting anything, per this story's own Task 1 instruction. Confirmed the current text: a single
`iteration` counter (line 101: `iteration ← iteration + 1 for this story`), capped at 3 (line 102:
`if iteration > MAX_FIX_ITERATIONS (default 3): HALT`), with no finding-class distinction anywhere
in the fix-loop block. This matches the story's own description exactly.

All three ACs require editing this same file/section, and this dispatch's own global rules state
plainly, without qualification: "`.claude/settings.json` and `.claude/skills/**` are not yours to
edit, in any repo" — listed under "Things that will be refused. Do not spend a turn discovering
them." That is the same file this story names, so no `Edit`/`Write` attempt was made against it;
per that same rule's instruction, a known refusal is not worth spending a turn to rediscover. This
is independently corroborated by [[Story 21.1]]'s Dev Agent Record (lines 211-226 of that file),
which confirmed the identical denial three separate times, across three different agents/sessions
(Cadmus via `Edit` twice and `Write` once; then reconfirmed by Aeacus and by Neo's own primary
session the same night), on this exact path — a harness-level block, not a per-session or
per-agent fluke, and not something a fourth confirmation would add evidence to.

Per this story's own Task 1 instruction ("If the same denial recurs here, preserve the exact
intended prose ... rather than attempting a workaround, and report the blocker"), no workaround
(raw shell write, alternate tool, etc.) was attempted. The exact intended replacement for §4's fix
loop block (lines 100-103 of the live file) is preserved below for the owner or a future dev pass
with edit access to apply directly:

> ```
>       fix loop (only entered from a non-pass review):
>         classify this round: DOCS-ONLY iff every file named in this round's Review Findings is
>         non-executable (docs, prose, comments, story files — nothing that runs); if even one
>         named file is executable (code, tests, scripts, configs that execute), the whole round
>         counts as EXECUTABLE even when most of its findings are docs-only.
>         if round is EXECUTABLE: exec_iteration ← exec_iteration + 1 for this story
>         if round is DOCS-ONLY:  docs_iteration ← docs_iteration + 1 for this story
>         if exec_iteration > MAX_FIX_ITERATIONS (default 3) OR
>            docs_iteration > MAX_FIX_ITERATIONS (default 3): HALT (visible, named, state which
>            counter tripped and why)
>         spawn bmad-dev (mode=fix); verify(review)  → spawn bmad-review; verify(done|in-progress)
>           → repeat until pass or either cap trips
> ```
>
> Insert immediately below this a one-line citation of the evidence (AC #3), e.g.: *"Story 17.5
> hit exactly this failure mode: three Low, docs-only fix rounds spent the single shared counter's
> whole budget, the third labelled 'LAST PERMITTED FIX ROUND', leaving no margin had a genuine
> executable defect surfaced at iteration 3 (`sprint-change-proposal-2026-08-29b.md` §4.3, item
> 3b). Splitting the counters by finding class prevents a run of Low, prose-only findings from
> silently spending the budget a real defect needs."*

This replaces the two-line block at the current lines 101-102 (the `iteration ← iteration + 1` /
`if iteration > MAX_FIX_ITERATIONS` pair) with the classify-then-branch block above; no other line
in §4 needs to change for AC #1 and #2. AC #3 is the citation line appended immediately after.

### Completion Notes List

- Story judged genuinely ready for dev on its own merits: all three ACs verified against the live
  `epics.md` seed and the live `SKILL.md` §4 text before starting; no contradiction or gap found in
  the story content itself.
- Tasks 1, 2, 3: **BLOCKED**, not done. All three ACs land in the same harness-denied file
  (`.claude/skills/bmad-dev-loop/SKILL.md`); this dispatch's own global rules independently confirm
  the denial ("`.claude/skills/**` are not yours to edit, in any repo"), consistent with the three
  prior confirmations recorded in [[Story 21.1]]'s Dev Agent Record. No workaround attempted, per
  the story's own instruction. Exact intended prose preserved above for manual application.
- Zero `argus/` bytes touched (nothing in this story names an `argus/` path to begin with).
- Unlike Story 21.1, no task in this story is independent of the blocked file — there is no
  partial-completion path available to an agent here. The whole story is currently only
  actionable by the owner applying the preserved text by hand, the same route Story 21.1 used.

### File List

- `_bmad-output/design-artifacts/ArgusAgent/stories/21-3-fix-round-budget-by-finding-class.md`
  [MODIFY] — this file: Status, Dev Agent Record.
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` [MODIFY] — `21-3-...` key
  `ready-for-dev` → `in-progress`, with the blocker noted inline.
- `.claude/skills/bmad-dev-loop/SKILL.md` — **NOT MODIFIED** (harness-denied; see Debug Log
  References for the preserved intended prose).

### Verification Pass (wq-939, 2026-09-26)

The block preserved above (wq-593) was applied to the live `.claude/skills/bmad-dev-loop/SKILL.md`
§4 by Neo, by script, on Zero's direct instruction after the Edit/Write harness denial recurred a
fourth time — recorded in `company/skills-edit-grant-and-settings-overrule-2026-09-26.md`
(XAgents-Assistant). This pass verified the live result against the three ACs and against the
backup left beside it (`SKILL.md.bak-2026-09-26-154358`):

- **AC1** (exec_iteration / docs_iteration, each capped at 3) — met. Live §4 lines 105-109:
  `if round is EXECUTABLE: exec_iteration ← exec_iteration + 1`, `if round is DOCS-ONLY:
  docs_iteration ← docs_iteration + 1`, `if exec_iteration > MAX_FIX_ITERATIONS (default 3) OR
  docs_iteration > MAX_FIX_ITERATIONS (default 3): HALT`.
- **AC2** (DOCS-ONLY iff every named file is non-executable; any executable file makes the round
  EXECUTABLE) — met. Live §4 lines 101-104 state the rule exactly, in the fix-loop's routing step
  as Task 2 required, not left implicit.
- **AC3** (citation to `sprint-change-proposal-2026-08-29b.md` §4.3, item 3b) — met. Live §4 lines
  112-117, a comment block citing that section/item and the Story 17.5 failure mode by name.
- Diff against the backup (`diff --strip-trailing-cr`, to discount the CRLF/LF byte-invariant
  noted elsewhere in this project's records): the only change is lines 101-103 (backup) →
  101-117 (live) — exactly the block above, plus a one-line provenance prefix on the citation
  comment ("Story 21.3 (2026-09-26, applied by Neo on Zero's instruction of the same day)."). No
  unrelated line in the file differs.
- **§5, §6, §9 consistency check**: all three still name `MAX_FIX_ITERATIONS` with the same
  default (3), consistently. Two lines still read as if a single counter exists — §5's worker-spawn
  contract (`bmad-review`: `story_key`, `story_file`, `iteration` — singular) and §6's halt
  description ("a story failed review `MAX_FIX_ITERATIONS` times" — a cumulative-count framing,
  where the live rule is either counter individually exceeding the cap). **Judged not required by
  AC1's letter**, which scopes the counting requirement to §4 only, and not fixed here: fixing them
  requires the same Edit/Write-bypass route §4's own change needed (confirmed still refused this
  pass — see below), which this dispatch was not separately instructed to invoke for a second time
  on unscoped lines. Flagged for the owner as a documentation-consistency gap, not a defect in AC1.
  §9's config line (`MAX_FIX_ITERATIONS` default 3) needs no change — it declares one constant the
  live rule already applies independently to both counters.
- **`.bak` deletion**: not done. `Edit`/`Write` on `.claude/skills/**` is still refused at the
  harness level this pass (confirmed again on this exact path, consistent with three prior
  confirmations across Story 21.1 and this story's own wq-593 pass) — a real, reconfirmed refusal,
  not a workaround-worthy gap. The backup file remains on disk beside `SKILL.md` pending the owner
  deleting it directly (the same route Neo used to apply the block itself).
- **Git-tracking finding (new, not anticipated by this story or its brief): `.claude/` is
  git-ignored repo-wide** (`.gitignore` line 31, under "IDE / Tooling"), and
  `.claude/skills/bmad-dev-loop/SKILL.md` has zero history on any branch
  (`git log --all -- .claude/skills/bmad-dev-loop/SKILL.md` returns nothing) — it has never been a
  tracked file in this repository. The applied §4 change therefore **cannot be committed** by any
  normal `git add`; only this story file and `sprint-status.yaml` are being committed by this pass.
  Committing the skill content itself would require `git add -f` against a directory this repo's
  own `.gitignore` groups with `.vscode/`/`.idea/` as local tooling config, which is a policy
  question for the owner, not a call this pass makes unilaterally. This does not affect the
  runtime behavior of the loop (the file is live on disk and will be read by any orchestrator
  session on this machine); it means the change has no commit hash of its own and will not survive
  a fresh clone.
