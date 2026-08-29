---
name: False positive — Argus flagged something it should not have
about: Argus reported a finding on code that is fine. These are the most valuable reports.
title: "[FP] "
labels: ["false-positive", "detector"]
---

**Why this matters:** Argus is built to gate CI. A tool that cries wolf gets removed from the
pipeline, so a false positive is at least as serious as a missed defect.

### The code that was flagged

Please paste the smallest snippet that still reproduces it.

```
```

### What Argus said

The finding, and the `rule_id` if you have it (`vacuous_test_ast`, `orphan_code`, ...).

```
```

### Why it is not a real problem

One or two sentences on why this code is correct as written.

### Environment

- Argus version (`argus --version`):
- Language of the flagged file:
- Install method: pip pin / standalone binary / clone
