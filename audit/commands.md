# ArgusAgent Slash Commands Reference

| Command | Purpose |
|---|---|
| `/audit` | Execute the full 12-phase repository audit pipeline |
| `/audit repo` | Execute intake, inventory, and graph partitioning |
| `/audit architecture` | Reconstruct architecture and cross-subsystem call graphs |
| `/audit security` | Run secret scanners, entropy check, and containment tests |
| `/audit requirements` | Perform requirements traceability & assertion density check |
| `/audit performance` | Analyze complexity metrics & radon CC scores |
| `/audit testing` | Run vacuous test detector & test-to-SUT reachability analysis |
| `/audit subsystem <name>` | Perform focused deep audit on specified subsystem |
| `/audit report` | Render the 12 developer markdown reports |
| `/audit resume` | Deterministically resume audit from on-disk state |
