---
name: argus-agent-audit
description: ArgusAgent Repository Assurance Audit skill. Performs evidence-backed, AST-grounded repository audits across architecture, security, performance, requirements, and testing.
---

# ArgusAgent Audit Skill (`/audit`)

Use this skill when the user asks to audit a repository, evaluate release-readiness, check code quality, analyze architecture, scan for security leaks, or generate evidence-backed audit reports.

## Core Capabilities

1. **Deterministic Assurance**: Driven by tree-sitter AST parsing, pure verdict math (`RELEASE_READY`, `NOT_READY_FOR_RELEASE`, `INSUFFICIENT_COVERAGE`), and hash-chained `.apaa/` evidence stores.
2. **Graph-Derived Partitioning**: Auto-partitions large codebases into $\le 40$-file / $15\text{k}$-LOC units to maintain high attention density.
3. **12-Phase Progression**: Guided workflow from Orientation (`00`) to Verdict (`11`).
4. **Slash Commands**:
   - `/audit` - Run full pipeline
   - `/audit architecture` - Audit subsystem dependencies & call graph
   - `/audit security` - Scan secret leaks & containment
   - `/audit subsystem <name>` - Target specific module/subsystem
   - `/audit report` - Render 12 developer markdown reports
   - `/audit resume` - Resume interrupted state from on-disk cache

## Execution Protocol

1. Load target repository @ pinned commit.
2. Run intake & stack detection (`radon` + `tree-sitter`).
3. Build call graph and partition repository into bounded audit units.
4. Execute zero-token breadth scanners and AST deep auditing.
5. Compute pure verdict gate over coverage ledger.
6. Export non-repudiable evidence bundle and human-facing markdown reports.
