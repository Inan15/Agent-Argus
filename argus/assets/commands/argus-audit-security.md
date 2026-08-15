---
description: Run only the Argus security pass over this repository (secret scan + containment).
---

<!-- argus-command-asset: v1 -->

Run the Argus audit with the security pass alone, over the repository in the current
working directory. This narrows the audit rather than deepening it: the other
deterministic passes do not run, so the coverage figures the command prints describe a
narrower assessment. Report the verdict token, the exit code and the coverage figures
exactly as the command prints them.

<!-- argus:instrument-status -->

```bash
argus audit . --passes security
```
