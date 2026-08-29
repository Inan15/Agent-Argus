---
name: argus-agent-audit
description: Agent-Argus Repository Assurance Audit skill. Performs evidence-backed, AST-grounded repository audits across architecture, security, performance, requirements, and testing.
---

# Agent-Argus Audit Skill

Use this skill when the user asks to audit a repository, evaluate release-readiness, check code quality, analyze architecture, scan for security leaks, or generate evidence-backed audit reports.

## Core Capabilities

1. **Deterministic Assurance**: Driven by tree-sitter AST parsing, pure verdict math (`RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`), and hash-chained `.apaa/` evidence stores.
2. **Graph-Derived Partitioning**: Auto-partitions large codebases into $\le 40$-file / $15\text{k}$-LOC units to maintain high attention density.
3. **12-Phase Progression**: Guided workflow from Orientation (`00`) to Verdict (`11`).
4. **Shipped commands** — the packaged asset tree (`argus/assets/commands/`), placed by
   `argus install-commands`, and asserted equal to this list in both directions by
   `TC-ArgusAgent-ASSETS-001-06`:
   - `/argus-audit` — run the full deterministic audit and report the verdict (`argus audit .`)
   - `/argus-audit-security` — the security pass alone (`argus audit . --passes security`)
   - `/argus-audit-report` — the audit plus the **four** developer markdown reports

   *Corrected 2026-08-15 (Story 12.7 / FR35 — §3.4, struck not deleted.)* This list
   previously named six commands, none of which was delivered by anything, and it was the
   third of three published lists that disagreed with each other (`README.md` listed seven,
   `audit/commands.md` listed ten). ~~`/audit`, `/audit architecture` — audit subsystem
   dependencies & call graph, `/audit security`, `/audit subsystem <name>` — target specific
   module/subsystem, `/audit report` — render 12 developer markdown reports, `/audit resume`
   — resume interrupted state from on-disk cache.~~ `architecture` is a **report**, not a
   pass, and is produced by `/argus-audit-report`; `subsystem <name>` needs a scoping
   capability that does not exist; `resume` has an engine but no CLI entrance at all
   (`DF-3-4-A`, open since Story 3.4). The report count was published as **12** here and as
   **8** and **12** in `README.md`, while `generate_reports` renders **four**.

## Execution Protocol

1. Load target repository @ pinned commit.
2. Run intake & stack detection (`radon` + `tree-sitter`).
3. Build call graph and partition repository into bounded audit units.
4. Execute zero-token breadth scanners and AST deep auditing.
5. Compute pure verdict gate over coverage ledger.
6. Export non-repudiable evidence bundle and human-facing markdown reports.
