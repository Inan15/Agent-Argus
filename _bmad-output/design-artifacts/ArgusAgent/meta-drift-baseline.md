# Meta-drift baseline — measured 2026-08-23 at `bbe1524`

> ⛔ **DO NOT ADD ROWS TO SILENCE A NEW FINDING.**
>
> This file records the state of the tree on the day the anti-drift rules were
> proposed. It exists so that `scripts/check_meta_drift.py` can distinguish
> pre-existing conditions from new ones — nothing more. Adding a row because a
> fresh finding is inconvenient converts the advisory report into a rubber stamp
> and defeats the entire mechanism.
>
> A row may be added ONLY by a story that says it is adding one, with the
> operator ruling that authorised it cited on the row.

## Scope of the baseline

Epics **1 through 16** are pre-rule. `check_meta_drift.py` never classifies them,
and no finding in this file is a defect claim against the work that produced them.
Their provenance is evidence (§3.4 evidence immutability), not debt.

## Measured, 2026-08-23

| plane | files | lines |
|---|---:|---:|
| product / application source (`argus/**.py`) | 95 | 33,578 |
| tests (`tests/**.py`) | 132 | 67,935 |
| process + gate scripts (`scripts/**`) | 9 | 4,639 |
| governance prose (`_bmad-output/**.md`) | 134 | 108,190 |
| committed rulebook | **0** | **0** |

- Guard ids in `tests/`: **1,251**. Named in a commit message: **40**. Named in
  governance prose: **282**. Named nowhere outside their own file: **967 (77%)**.
- Test files, monotonic: 55 (2026-07-29) → 125 (2026-08-23). **Zero** test files or
  scripts deleted in 189 commits.
- Retrospective action items registered in `sprint-status.yaml`: **73**, of which
  **53+ open**. File size: **938 KB**.
- Deferred-work entries: **~100 ids**, 26 CLOSED / 14 OPEN with an explicit status.
- `argus/cli.py` and `argus/commands/`: **0 lines changed** in the last **128 commits**
  (since `40cdb3c`, 2026-08-16). Over those 128 commits `argus/` changed by 8,486
  lines, of which **6,483 (76%) are `argus/precision/`** — the project's own gate
  machinery, unreachable from `argus.cli`. Detectors: 1,879.
- Modules unreachable from `argus.cli`: `argus/precision/` (6,851 lines, 11 modules),
  `argus/governance/` (673 lines), `argus/dogfood/` (2,185 lines).

## Baselined conditions (pre-existing, not new findings)

| id | condition | measured |
|---|---|---|
| `MDB-1` | Epics 13–16 carry no `**Capability delivered:**` field | 4 epics |
| `MDB-2` | Epics 13–16 `**Covers:**` lines name no FR/NFR driver | 4 epics |
| `MDB-3` | Epic 16 process-derived story share | 86% (6 of 7) |
| `MDB-4` | Guard ids with no recorded fire history | 967 of 1,251 |
| `MDB-5` | `DN-3` restated across documents | 48 |
| `MDB-6` | `argus/governance/` importers outside its own package | 0 |
| `MDB-7` | `§3.4 evidence immutability` — citations vs. defining section | 144 vs. 0 |
