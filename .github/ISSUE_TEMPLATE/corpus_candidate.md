---
name: Corpus candidate — nominate a repository with real defects
about: Help make the precision gate evaluable. Read the note below first.
title: "[CORPUS] "
labels: ["corpus", "precision-gate"]
---

**Context, because this ask is unusual.** Argus's ≥80% precision gate is currently *unevaluable*
rather than unmet: run against five mature repositories, the detector emitted 4,284 advisory
findings and promoted **zero** to verdict-eligible. Precision is `TP / (TP + FP)`, so an empty
population gives an undefined ratio rather than a low one. Mature, heavily-exercised code cannot
supply a denominator — code with real, findable defects can.

### The repository

- URL:
- Licence:
- Primary language:

### Why you think Argus would find something real here

Tests that do not assert, unreachable functions, suppressed warnings — whatever you have noticed.

### Are you connected to it?

Maintainer, contributor, or unaffiliated. All three are fine; it just needs recording.

> **Process note.** Candidates are pre-registered and sealed at a pinned commit *before* Argus is
> run against them. That ordering is what makes the resulting evidence worth anything, so please do
> not run Argus against a repository you are about to nominate.
