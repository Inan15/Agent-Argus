---
baseline_commit: 7b7b2a0f995fc5ae2bd8c1ce6133a2277804b95b
---

# Story 21.3: Split the Fix-Round Budget by Finding Class

Status: ready-for-dev

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

_Not yet worked — this file was produced by a decomposition pass (wq-579), not a dev pass._

### Debug Log References

### Completion Notes List

### File List
