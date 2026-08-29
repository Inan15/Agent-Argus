# Agent-Argus Slash Commands Reference

**These are the commands that ship.** The set below is not maintained by hand: it is the
`argus/assets/commands/` tree, which `argus install-commands` places into your assistant's
configuration directory, and `TC-ArgusAgent-ASSETS-001-06` fails the build if this table and
that tree ever disagree — in either direction.

| Command | Purpose | The invocation it runs |
|---|---|---|
| `/argus-audit` | Run the full deterministic release-readiness audit and report the verdict | `argus audit .` |
| `/argus-audit-security` | Run the security pass alone (secret scan + containment) | `argus audit . --passes security` |
| `/argus-audit-report` | Run the audit and render the four developer markdown reports | `argus audit . --report-dir ./argus-reports --reports …` |

Every command above is a file in the packaged asset tree, and every `argus …` line inside
those files is handed to the real `argus` argument parser by `TC-ArgusAgent-DOCS-001-28`, so
a command that would fail for you fails the build first.

---

## What this table used to say, and why it changed (§3.4 — struck, not deleted)

*Corrected 2026-08-15 (Story 12.7 / FR35).* This file previously listed **ten** commands
while `README.md` listed **seven** and `audit/skill.md` listed **six** — three published
lists, three different sets, and none of them was delivered by anything. Four of them could
not resolve to any invocation the tool accepts:

~~| `/audit repo` | Execute intake, inventory, and graph partitioning |~~
~~| `/audit architecture` | Reconstruct architecture and cross-subsystem call graphs |~~
~~| `/audit requirements` | Perform requirements traceability & assertion density check |~~
~~| `/audit performance` | Analyze complexity metrics & radon CC scores |~~
~~| `/audit testing` | Run vacuous test detector & test-to-SUT reachability analysis |~~
~~| `/audit subsystem <name>` | Perform focused deep audit on specified subsystem |~~
~~| `/audit resume` | Deterministically resume audit from on-disk state |~~

- `repo`, `requirements` and `performance` name no capability the CLI exposes:
  `_ALL_PASSES` has no such token and `generate_reports` renders no such report.
- `architecture` is a **report**, not a pass — it is produced by `/argus-audit-report`, so a
  separate command whose only difference is a report filter would be a second, narrower
  spelling of one capability (AR7).
- `testing` resolves under a different spelling already (`--passes vacuous`).
- `subsystem <name>` needs a scoping capability that does not exist;
  `--critical-subsystem` *designates a path critical*, it does not narrow the audit.
- `resume` has a real engine (`pipeline.resume_audit`) and **no CLI entrance of any kind**,
  filed as `DF-3-4-A` and open since Story 3.4. Building one is fenced to a later story; a
  command that cannot run is removed from the docs, not implemented under cover of a
  documentation fix.

The report count was published as **12** here and in `README.md`, as **8** elsewhere in
`README.md`, while `argus/reports/generator.py::generate_reports` renders **four** —
`final-verdict`, `coverage-ledger`, `security-review` and `architecture-review`. Four is the
measured number and the one this file now states.
