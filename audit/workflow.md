# Agent-Argus Audit Workflow Engine Specification

The Agent-Argus workflow follows a strict 12-phase audit pipeline.

```
00-Orientation ──> 01-Bootstrap ──> 02-Intelligence ──> 03-Planning ──> 04-Mapping
                                                                              │
11-Verdict <── 10-Reporting <── 09-Cross-Validation <── 08-Subsystem <── 07-Arch <── 06-Reqs <── 05-Tooling
```

## Phase Descriptions

- **00-Orientation**: Ingest repository root, commit hash, and operator constraints.
- **01-Bootstrap**: Initialize state directory (`.apaa/` or `.argus/`), load toolchains (`radon`, `tree-sitter`).
- **02-Intelligence**: High-level repository inventory, LOC calculation, language composition.
- **03-Planning**: Construct graph-derived partition plan ($\le 40$ files / $15\text{k}$ LOC units).
- **04-Mapping**: Build AST code graph, call trees, and component boundaries.
- **05-Tooling**: Run zero-token breadth scanners (radon, secret scans, entropy checks).
- **06-Requirements**: Extract verifiable requirements & traceability markers.
- **07-Architecture**: Reconstruct architectural topology, boundary seams, and cut edges.
- **08-Subsystem-Review**: Perform deep-read audit on bounded partitions.
- **09-Cross-Validation**: Execute Prosecutor cut-edge pass to verify cross-partition defects.
- **10-Reporting**: Render 12 developer reports from standardized templates.
- **11-Verdict**: Compute pure-function verdict gate and export signed evidence bundle.
