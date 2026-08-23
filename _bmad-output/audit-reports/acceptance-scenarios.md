# Acceptance scenario results

Measured at `76ee9fa` by `scripts/acceptance_scenarios.py`.

**6 of 6 scenarios agree across all three surfaces.**

Each scenario runs the shipped CLI end to end and checks that the process
exit code, the stdout machine summary and the rendered `final-verdict.md`
all describe the same outcome. No expected verdict is hardcoded, so a
legitimate detector improvement does not make this sheet red — only a
disagreement between what the tool did and what it said it did.

| scenario | what a user is doing | verdict | exit | blocking | agree |
|---|---|---|---:|---:|---|
| `python-only` | Audits a small pure-Python project with no flags at all — the first-run path. | RELEASE_READY | 0 | 0 | yes |
| `polyglot-with-grammars` | Audits a Python + JavaScript + TypeScript project with the grammars installed. | RELEASE_READY | 0 | 0 | yes |
| `unparseable-source-degrades` | Audits a project containing a file the parser cannot read. | INSUFFICIENT_COVERAGE | 3 | 0 | yes |
| `deep-audit-no-provider` | Passes --deep-audit with no model provider configured. | INSUFFICIENT_COVERAGE | 3 | 0 | yes |
| `scope-application` | Restricts assessment to application code, holding tests out. | RELEASE_READY | 0 | 0 | yes |
| `action-flag-set` | Runs the exact flag set the published GitHub Action passes. | RELEASE_READY | 0 | 0 | yes |

## Coverage, and what it excludes

- `python-only` — default invocation - the configuration most first-time users hit
- `polyglot-with-grammars` — the multi-language claim the installer's [languages] extra sells
- `unparseable-source-degrades` — honest degradation - an unreadable file must never count as deeply audited
- `deep-audit-no-provider` — opt-in deep pass degrading rather than silently claiming deep coverage
- `scope-application` — the scope split - held-out files must be disclosed, never silently dropped
- `action-flag-set` — argus-student-audit.yml - the published consumer path

**Not covered.** The published Action is exercised through its flag set, not
through a real Actions runner. The deep pass is exercised only in its
provider-unconfigured degradation, because release evidence must not depend
on a paid third party. Both gaps are real and are named so this page is never
read as broader than it is.

The existing gates are unchanged and still block. This page is the release
decision they inform; it does not replace one of them.

