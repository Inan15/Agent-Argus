---
description: Audit this repository with Argus and render the four developer markdown reports.
---

<!-- argus-command-asset: v1 -->

Run the Argus audit over the repository in the current working directory and write its
markdown reports into `./argus-reports`. FOUR report types are rendered, and only four —
`final-verdict`, `coverage-ledger`, `security-review` and `architecture-review`. Report
the verdict token, the exit code and the paths that were written; each report states, in
its own text, what the audit did and did not assess.

<!-- argus:instrument-status -->

```bash
argus audit . --report-dir ./argus-reports --reports final-verdict,coverage-ledger,security-review,architecture-review
```
