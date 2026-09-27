---
baseline_commit: 7b7b2a0f995fc5ae2bd8c1ce6133a2277804b95b
---

# Story 21.4: Correct Epic 20's Seed in Place and Close the Loop

Status: backlog

<!-- Contexted 2026-09-21 at HEAD `7b7b2a0f995fc5ae2bd8c1ce6133a2277804b95b` by a headless
     decomposition pass (XAgents-Assistant, work order wq-579), NOT by the interactive
     bmad-create-story elicitation flow — that skill's discovery/elicitation steps need a human
     in the loop this dispatch does not have. This file is authored by hand from the Epic 21 seed
     (`epics.md` §"Story 21.4", commit `fd56de3`) and the sprint-status backlog entry
     (`21-4-correct-epic-20-seed-in-place: backlog`), following the shape Story 21.1 already
     established for this epic.

     Left at `backlog`, NOT advanced to `ready-for-dev` like 21.2 and 21.3: this story has a real
     prerequisite (see Dev Notes) on the other three Epic 21 stories reaching a delivered state,
     and the dev-loop state machine's `backlog -> ready-for-dev` step is meant for a story that is
     actually next, not one that is blocked by design. No code, test, or `argus/` byte has been
     touched to produce this file. -->

## Story

As the **Product Owner / Scrum Master, closing out Epic 21 without reopening Epic 20**,
I want **Epic 20's seed in `epics.md` corrected in place — `**Capability delivered:**` (`Nothing`
+ dated ruling) and `**Covers:**` added, with the pre-correction `check_meta_drift.py` reporter
output frozen verbatim beside the correction — and `AI-E17-9`, `-10`, `-11`, `-13` closed against
their now-delivered destinations**,
so that **the non-conformant seed that triggered this whole corrective epic is brought into the
§3.4 struck-not-deleted correction form Story 17.5 already established, without pretending Epic 20
was ever reopened or any of its story statuses changed.**

## Acceptance Criteria

Copied verbatim from the Epic 21 seed (`epics.md`, "### Story 21.4", commit `fd56de3`) — this
story does not restate them in different words:

1. Epic 20's seed carries `**Capability delivered:**` (`Nothing` + dated ruling) and `**Covers:**`,
   with the **pre-correction reporter output frozen verbatim**.
2. Epic 20 is **not** reopened and no story status changes.
3. `AI-E17-9`, `-10`, `-11`, `-13` are closed against their delivered destinations.

## Tasks / Subtasks

- [ ] Task 1: Correct Epic 20's seed in `epics.md` in the §3.4 struck-not-deleted form (AC: #1, #2)
  - [ ] Locate Epic 20's seed block in `epics.md` and apply a dated in-place correction, same
        form Story 17.5 used on Epic 17's header: strike the goal line and correct it to "build
        the three mechanisms as library seams", per `sprint-change-proposal-2026-08-29b.md` §4.1.
  - [ ] Add `**Capability delivered:**` — ⛔ "NOTHING A USER CAN REACH", with the HEAD `e9a8c1e`
        measurement, the `library-seam` dispositions, and the three `DF-20-*` ids, entered under
        the dated operator ruling of 2026-08-29 (`sprint-change-proposal-2026-08-29b.md`).
  - [ ] Add `**Covers:**` — FR38 (20.2) · FR39 (20.3) · FR40 (20.1). State plainly, not slipped
        past, that this `Covers:` line is retroactive (FR38/39/40 were admitted to the contract
        on 2026-08-28, after the seed was written) and will flip Epic 20 to product-traced in the
        next `check_meta_drift.py` report — that flip is not the breach being corrected.
  - [ ] Add a correction block **freezing the pre-correction `check_meta_drift.py` reporter
        output verbatim** (the exact three lines quoted in
        `sprint-change-proposal-2026-08-29b.md` §1.3(b)), so the before/after is auditable rather
        than silently overwritten. Per `meta-drift-baseline.md`'s own warning: a row may never be
        added to silence a finding — the frozen verbatim block is what keeps that honest.
  - [ ] Confirm no `epic-20` key or any `20-*` story key in `sprint-status.yaml` changes status as
        part of this task — this is a seed-text correction only, not a reopening.

- [ ] Task 2: Close `AI-E17-9`, `-10`, `-11`, `-13` against their delivered destinations (AC: #3)
  - [ ] For each of the four ids, confirm its discharging story (`AI-E17-13`→21.1, `AI-E17-10`
        and `AI-E17-11`→21.2, `AI-E17-9`→21.3) actually reads `done` in `sprint-status.yaml`
        before flipping the action item's own `status:` field to `done` — this is exactly the
        roll-up `Covers:` re-derivation Story 21.1 built (§CD-2 roll-up step), applied here by
        hand at the epic-21 level since the dev-loop orchestrator's own roll-up does this for the
        epic's `Covers:` line, not for `sprint-status.yaml`'s separate `action_items:` block.
  - [ ] If any of the four is not yet `done` when this task runs, do **not** flip it — record
        which remain open and why, and leave epic-21 itself un-rolled-up until they are. A
        bookkeeping lie here repeats exactly the failure `AI-E17-13` exists to prevent.
  - [ ] ⛔ Leave `AI-E17-12` untouched — it is `record-only`, deliberately unassigned, per
        `sprint-change-proposal-2026-08-29b.md` §4.5. Closing it would be a bookkeeping lie.

---

## Dev Notes

### What this story is, and is not
- This is a **process-derived, corrective** story inside a **process-derived, corrective** epic
  (Epic 21) — see [[Story 21.1]]'s own framing, which this story inherits unchanged:
  `epics.md` records `Capability delivered: NOTHING A USER CAN REACH` for the whole epic, entered
  under the dated operator ruling of 2026-08-29 (`sprint-change-proposal-2026-08-29b.md`).
- **Zero `argus/` bytes are touched by this story.** Every change lands in `epics.md` and
  `sprint-status.yaml`'s `action_items:` block.
- **This is the epic's closing story** — its own name says "close the loop". Task 2 cannot be
  done honestly until the other three stories' deliverables actually exist on disk; see the hard
  prerequisite below.

### Hard prerequisites — all three currently unsatisfied
This story genuinely depends on the rest of the epic, not just conventionally:
1. **Prerequisite:** Story `21-1-cd2-consumption-points-and-rollup-covers-verdict` must read
   `done` — it discharges `AI-E17-13` (Task 2 of this story) and, per that story's own "Sequencing
   note carried from the seed" (Dev Notes), its `_console_safe()` fix is what lets this story
   print/handle Epic 20's correction text safely if that text contains the same non-cp1252 `⛔`
   character the seed commit already named as a live hazard. As of this story's baseline commit,
   `21-1-...` reads `review`, not `done` — not yet independently re-screened per its own Dev Agent
   Record.
2. **Prerequisite:** Story `21-2-staging-protocol-and-premise-remeasurement-phase` must read
   `done` — it discharges `AI-E17-10` and `AI-E17-11` (Task 2 of this story).
3. **Prerequisite:** Story `21-3-fix-round-budget-by-finding-class` must read `done` — it
   discharges `AI-E17-9` (Task 2 of this story).

Task 1 (the Epic 20 seed correction itself) does **not** strictly require the above — it is
self-contained text-correction work. Only Task 2 (closing the four `AI-E17-*` ids) and the story's
own "close the loop" framing require the other three. An implementing agent may choose to do Task
1 early and hold Task 2 for last, but should not mark this story `done` while any of the three
prerequisites above is unmet, per this repo's "no bookkeeping lie" convention (`AI-E17-12`'s own
precedent).

### Source Tree Components to Touch
- `_bmad-output/design-artifacts/ArgusAgent/epics.md` [MODIFY]: Epic 20 seed correction, §3.4
  struck-not-deleted form.
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` [MODIFY]: `action_items:` status
  flips for `AI-E17-9`, `-10`, `-11`, `-13` (each only once its discharging story reads `done`).

### Prior Art Already on Disk (read before writing anything)
- `epics.md` §"Epic 21" (line 3933) and §"Story 21.4" (line 3980) — the seed and its AC, quoted
  verbatim above.
- `sprint-change-proposal-2026-08-29b.md` §4.1 (Epic 20 seed correction) and §1.3(b) (the exact
  verbatim reporter output to freeze).
- `meta-drift-baseline.md` — the warning that a row may never be added to silence a finding;
  governs how the frozen-verbatim block must be written.
- Epic 17's own header — the §3.4 struck-not-deleted precedent this story's Task 1 follows,
  applied by Story 17.5.
- [[Story 21.1]] (`21-1-cd2-consumption-points-and-rollup-covers-verdict.md`) — both for the shape
  this file is patterned on and for its "Sequencing note carried from the seed" (Dev Notes),
  which names this story by number as the consumer of its `_console_safe()` fix.

### References
- [Epic 21 seed, Story 21.4](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/epics.md#L3980)
- [sprint-change-proposal-2026-08-29b.md §4.1, §1.3(b)](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-29b.md)
- [meta-drift-baseline.md](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/meta-drift-baseline.md)
- [Story 21.1 — Sequencing note carried from the seed](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/stories/21-1-cd2-consumption-points-and-rollup-covers-verdict.md)

---

## Dev Agent Record

### Agent Model Used

_Not yet worked — this file was produced by a decomposition pass (wq-579), not a dev pass._

### Debug Log References

### Completion Notes List

### File List
