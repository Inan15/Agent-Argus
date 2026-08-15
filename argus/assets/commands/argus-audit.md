---
description: Audit this repository with Argus and report the release-readiness verdict.
---

<!-- argus-command-asset: v1 -->

Run the deterministic Argus release-readiness audit over the repository in the current
working directory. Report the verdict token, the process exit code and the coverage
figures exactly as the command prints them; do not restate them as a judgement of your
own, and do not describe a file the audit did not assess.

<!-- argus:instrument-status -->

```bash
argus audit .
```
