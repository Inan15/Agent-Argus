---
baseline_commit: 7b7b2a0f995fc5ae2bd8c1ce6133a2277804b95b
---

# Story 21.2: Write Down the Shared-Tree Staging Protocol and the Premise Re-Measurement Phase

Status: ready-for-dev

<!-- Contexted 2026-09-21 at HEAD `7b7b2a0f995fc5ae2bd8c1ce6133a2277804b95b` by a headless
     decomposition pass (XAgents-Assistant, work order wq-579), NOT by the interactive
     bmad-create-story elicitation flow — that skill's discovery/elicitation steps need a human
     in the loop this dispatch does not have. This file is authored by hand from the Epic 21 seed
     (`epics.md` §"Story 21.2", commit `fd56de3`) and the sprint-status backlog entry
     (`21-2-staging-protocol-and-premise-remeasurement-phase: backlog`), following the shape
     Story 21.1 already established for this epic. No code, test, or `argus/` byte has been
     touched to produce this file. Per the dev-loop state machine
     (`.claude/skills/bmad-dev-loop/SKILL.md` §3), `backlog` -> (create-story) -> `ready-for-dev`
     is one step, so the sprint-status entry for this story moves to `ready-for-dev` in the same
     change that adds this file — nothing else on the tracker is touched by this pass. -->

## Story

As the **project's Architect, at the point where two action items on their third raise
(`AI-E17-10`, `AI-E17-11`) are proven in execution but written down nowhere**,
I want **`architecture.md` §Enforcement to carry two new rules — shared-tree staging enforcement
and premise re-measurement enforcement as a named phase — each cited by at least one existing
story rather than re-derived**,
so that **the next story that needs either practice reads a rule instead of re-discovering it
from scratch, and the practice stops depending on the accident of which story happened to
re-invent it.**

## Acceptance Criteria

Copied verbatim from the Epic 21 seed (`epics.md`, "### Story 21.2", commit `fd56de3`) — this
story does not restate them in different words:

1. `architecture.md` §Enforcement carries **Shared-tree staging enforcement** — explicit-path
   staging, carried files disclosed by name, byte invariants re-measured before and after —
   including the working-tree/blob split and the `grep -n` vs `splitlines()` divergence after
   `deferred-work.md` line 5573.
2. `architecture.md` §Enforcement carries **Premise re-measurement enforcement** as a **named
   phase with a three-outcome verdict form**, `A ROW MOVED` being first-class and REPORTED.
3. One story cites each rule rather than re-deriving it.
4. ⚠️ Sequenced against the in-progress `AI-E10-5`, which edits the same section: both land, or
   10-5 is explicitly left untouched and re-measured.

## Tasks / Subtasks

- [ ] Task 1: Add the shared-tree staging enforcement rule to `architecture.md` §Enforcement (AC: #1)
  - [ ] Append after the section's existing content (pure append, per the sprint-change
        proposal's own §4.2 instruction: "No existing rule is modified") — state explicit-path
        staging (`git add <path>`, never `git add -A`), carried peer files disclosed by name in
        the commit message, and byte invariants re-measured before and after every write.
  - [ ] Include the working-tree/blob split (`core.autocrlf` makes the working tree CRLF while
        every committed blob stays LF) and the `grep -n` (8516 lines) vs `splitlines()` (8517)
        divergence at `deferred-work.md` line 5573, per `sprint-change-proposal-2026-08-29b.md`
        §2.4 and §4.2.1.
  - [ ] Cite the evidence already on record rather than re-deriving it: 5 of 5 Epic-17 stories,
        disclosure used twice (`DN-17-2-11`, `DN-17-4-19`), independently verified by reviewers
        with `git show --stat` / `git diff`, zero collisions across 33 commits against three
        inside Story 16.7 alone.

- [ ] Task 2: Add the premise re-measurement enforcement rule to `architecture.md` §Enforcement (AC: #2)
  - [ ] State it as a **named phase** (not an ambient habit) with a **three-outcome verdict
        form**: `reproduced` | **`A ROW MOVED`** | `could not measure` — `A ROW MOVED` is
        first-class and must be **reported**, never silently absorbed into the story's other
        findings.
  - [ ] Cite the evidence already on record: practised 5 of 5 Epic-17 stories, found real drift
        in 4 of 5; Story 17.5 corrected its own SM on three figures (52/18 vs 47/23; 28 blocks/26
        ids vs 24/23, against a going-in assumption of "six") and found two missed ledger ids
        (`DF-8-3-B`, `DF-14-3-H`); `DF-16-5-A` predicted `DF-14-3-H` going stale and it went
        stale anyway because nothing was watching.

- [ ] Task 3: Wire each rule to a citing story rather than leaving it to be re-derived (AC: #3)
  - [ ] Identify (or, if none yet exists, note in this story's Dev Agent Record) at least one
        story file that references the new staging rule by name/section instead of restating its
        content.
  - [ ] Same for the premise re-measurement rule.

- [ ] Task 4: Resolve the `AI-E10-5` sequencing collision before writing to §Enforcement (AC: #4)
  - [ ] Read `AI-E10-5`'s current status and target text in `sprint-status.yaml`
        (`action_items:`, epic 10) before editing `architecture.md` §Enforcement — it is recorded
        `in-progress` and edits the same section (the closure-over-enumeration rule, successor to
        `AI-E9-7`).
  - [ ] Land both edits together if `AI-E10-5`'s text is ready, or land this story's two rules as
        a clean append leaving `AI-E10-5`'s target text untouched and re-measure its status
        afterward — either way, state which choice was made and why in this story's Dev Agent
        Record; do not silently overwrite or silently ignore the other edit.

---

## Dev Notes

### What this story is, and is not
- This is a **process-derived, corrective** story inside a **process-derived, corrective** epic
  (Epic 21) — see [[Story 21.1]]'s own framing, which this story inherits unchanged:
  `epics.md` records `Capability delivered: NOTHING A USER CAN REACH` for the whole epic, entered
  under the dated operator ruling of 2026-08-29 (`sprint-change-proposal-2026-08-29b.md`).
- **Zero `argus/` bytes are touched by this story.** Every change lands in `architecture.md` and
  whichever story file Task 3 wires as the citing example. If a change is found to need an
  `argus/` edit, that is a scope signal to raise, not to absorb silently.
- No independent prerequisite on another Epic 21 story: this story's two rules do not require
  `21-1-cd2-consumption-points-and-rollup-covers-verdict` to be `done` first — they land inside
  `architecture.md` §Enforcement, a different artifact from the `bmad-dev-loop/SKILL.md` surface
  21.1 touches. The only sequencing constraint that matters is `AI-E10-5` (Task 4), which is a
  same-file collision, not a cross-story dependency.

### Source Tree Components to Touch
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` [MODIFY]: §Enforcement gains the two
  new rules (pure append after the existing content, per the sprint-change proposal's instruction
  not to modify any existing rule).
- Whichever story file is chosen for Task 3's citation [MODIFY, if needed]: add a one-line
  reference to the new rule rather than restating it.

### Prior Art Already on Disk (read before writing anything)
- `epics.md` §"Epic 21" (line 3933) and §"Story 21.2" (line 3965) — the seed and its AC, quoted
  verbatim above.
- `sprint-change-proposal-2026-08-29b.md` §4.2 (items 1–2) — the exact rule text and evidence
  this story's two Enforcement additions are drawn from; §2.4 for the byte-invariant detail.
- `sprint-status.yaml` `action_items:` block, ids `AI-E17-10` and `AI-E17-11` — the two items
  this story discharges (both on their third raise per the seed).
- `sprint-status.yaml` `action_items:` block, id `AI-E10-5` — the in-progress item that edits the
  same section; read its current status before touching §Enforcement (Task 4).
- [[Story 21.1]] (`21-1-cd2-consumption-points-and-rollup-covers-verdict.md`) — the first story in
  this epic; read for the shape this file is patterned on (baseline-commit framing, AC copied
  verbatim from the seed, Dev Agent Record left for the implementing agent).

### References
- [Epic 21 seed, Story 21.2](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/epics.md#L3965)
- [sprint-change-proposal-2026-08-29b.md §4.2](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-29b.md)
- [architecture.md](file:///d:/ProjectX/XAgents/XAgents/ArgusAgent/_bmad-output/design-artifacts/ArgusAgent/architecture.md)

---

## Dev Agent Record

### Agent Model Used

_Not yet worked — this file was produced by a decomposition pass (wq-579), not a dev pass._

### Debug Log References

### Completion Notes List

### File List
