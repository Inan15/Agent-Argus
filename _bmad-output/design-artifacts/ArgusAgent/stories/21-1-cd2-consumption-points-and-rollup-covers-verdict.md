---
baseline_commit: fd56de3f8e63a6ab0784a5a727fb1afbdfea3262
---

# Story 21.1: Register the Two §CD-2 Consumption Points and the Roll-Up `Covers:` Verdict

Status: ready-for-dev

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

- [ ] Task 1: Add the epic ENTRY gate to `.claude/skills/bmad-dev-loop/SKILL.md` §3 (AC: #1)
  - [ ] State the gate as a precondition on the state-machine table or its surrounding prose:
        before a `backlog` epic's first story may route to `bmad-sm`, `epics.md`'s seed for
        that epic must carry a non-empty `**Capability delivered:**` and `**Covers:**` (or
        `Capability delivered: Nothing` plus a dated ruling citation, per the Epic 21 and
        Epic 20 precedent) — else **HALT**.
  - [ ] Require that the epic's first story records a `META-DRIFT:` verdict line (the
        `check_meta_drift.py` read for that epic, taken at the same HEAD the story was
        contexted at).
  - [ ] Keep the gate worded as **HALT on missing fields only** — it must not become a judgment
        call on whether the capability or coverage stated is *correct*; that question belongs
        to the roll-up (AC #2), not the entry.

- [ ] Task 2: Add the roll-up `Covers:` re-derivation to `.claude/skills/bmad-dev-loop/SKILL.md`
      §3 (AC: #2)
  - [ ] Before the orchestrator writes `epic-<id> = done` (§3's existing "Then set `epic-<id> =
        done` yourself" step), require it to read the epic's `**Covers:**` line from `epics.md`,
        resolve each id against its current on-disk status (a sprint-status story key, a
        `deferred-work.md` entry, or another named destination), and record a per-id verdict
        (met / unmet) before writing `done`.
  - [ ] State the unmet-list consequence: any id not delivered forces a dated §3.4 correction in
        `epics.md` (the same form Story 17.5 used by hand for AI-E17-13) rather than a silent
        `done`.
  - [ ] Cite AI-E17-13 and Story 17.5's hand correction as the evidence this rule generalizes
        from (both already in `deferred-work.md` / `epics.md` — no new research needed).

- [ ] Task 3: Prove the advisory path never blocks (AC: #3)
  - [ ] Add or extend a test asserting `python scripts/check_meta_drift.py` exits `0` on a clean
        parse of the current `epics.md` (a "cannot read its inputs" nonzero exit is the only
        legitimate nonzero case, per the module's own docstring at
        `scripts/check_meta_drift.py:1-12`).
  - [ ] Cover the encoding regression named in the Epic 21 seed commit (`fd56de3`): a
        `**Capability delivered:**` value beginning with a non-cp1252-encodable character (the
        seed used `⛔`, U+26D4) must not crash `report_epics`'s `print(f"      capability:
        {cap[:64]}")` (`scripts/check_meta_drift.py:150`) on a default Windows console; either
        the print path degrades gracefully or the test pins `PYTHONIOENCODING=utf-8` and says
        why in a comment.
  - [ ] Confirm this test lands as a **new** assertion, not a relaxation of any existing one —
        the entry gate (Task 1) is allowed to HALT; the advisory reader itself is not.

- [ ] Task 4: File `DF-DRIFT-UNREAD-A` (AC: #4)
  - [ ] Add an entry to `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` in that
        file's existing entry form (epic, id, action, owner, destination, priority, status) —
        follow the shape already used for `AI-E17-*` entries in `sprint-status.yaml`'s
        `action_items:` block, or `deferred-work.md`'s own entries if its schema differs; check
        the file's current schema before writing, do not assume it matches
        `sprint-status.yaml`'s.
  - [ ] Record the prior-art grep in the entry body: `check_meta_drift.py` (the advisory
        mechanism) existed and fired correctly across Epics 17, 18, 19 and 20 — four
        consecutive epics — and its report was read by no one before Epic 21 named the gap.
        Cite the specific evidence (AI-E17-13, Story 17.5) that shows the signal fired and was
        not acted on.
  - [ ] Name a destination and owner consistent with the other `dev-loop orchestrator`-owned
        entries already in the `action_items:` block (e.g. AI-E17-13's own row).

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

Not yet started.

### Debug Log References

### Completion Notes List

### File List

### Review Findings
