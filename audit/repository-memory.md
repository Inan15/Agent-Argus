# Agent-Argus Repository Memory Specification

Repository Memory maintains persistent facts across audit phases to eliminate redundant rediscovery.

## Schema Components

1. **Repository Facts**: Key stack parameters, framework versions, LOC breakdown.
2. **Architecture Facts**: Identified entrypoints, API layers, database models, background queues.
3. **Subsystem Index**: Mapping of files to cohesion clusters and boundary interfaces.
4. **Dependency Graph**: Inter-module import dependencies and cut edges.
5. **Evidence Graph**: Linked findings with AST locator spans and rules.
6. **Coverage Ledger**: Per-file depth state (`audited_deep`, `audited_shallow`, `tool_scanned_only`, `inferred`, `skipped`).
7. **Risk Register**: Active blocking and advisory findings sorted by criticality.
