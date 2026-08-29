# Contributing to Agent-Argus

Thank you for looking. This document is short on ceremony and long on **specific jobs**, because
"contributions welcome" tells nobody what to actually do.

Before anything else, two things that will save you an afternoon:

- **Run the tests first.** `pytest tests/` should be green before you change anything. If it is not
  green on a clean checkout, that is a bug and worth an issue on its own.
- **Read [§ House rules](#house-rules) before your first pull request.** This repository has a few
  conventions that are unusual, load-bearing, and enforced by tests. A PR that ignores them fails in
  ways that look mysterious.

---

## Named jobs — pick one

### 1. Break a detector (attack cases)

**The most useful thing you can do.** Argus's detectors live in [`argus/detectors/`](argus/detectors/):
`vacuous_test`, `assertion_strength`, `orphan_code`, `provenance_scan`, `secret_scan`,
`secret_suppression`, `vacuous_vocabulary`.

Find code that *should* be flagged and isn't (a false negative), or code that is flagged and
shouldn't be (a false positive). Open an issue with the smallest reproducing file you can write.

A false positive is at least as valuable as a false negative here: Argus is designed to gate CI, so
crying wolf is the failure mode that gets a tool removed from a pipeline.

### 2. Write a defect cartridge

Cartridges are the self-audit harness: small fixture repositories with a known answer, in
[`tests/cartridges/`](tests/cartridges/). Two kinds, and both are wanted:

- a **defect cartridge** — contains a specific planted defect, and Argus must find it;
- a **clean control** — contains no defect, and Argus must stay silent. Clean controls are rarer and
  more valuable, because they are what catch over-eager detectors.

Follow an existing cartridge's layout. Cartridges measure **recall**, deliberately — see job 5 for
why that distinction matters.

### 3. Add a language

Ten grammars ship in the default install (Python, JavaScript, TypeScript, Go, Rust, Java, C, C++,
Ruby, PHP). Adding an eleventh means a tree-sitter grammar dependency plus an entry in
[`argus/shared/grammar_status.py`](argus/shared/grammar_status.py) and
[`argus/shared/source_languages.py`](argus/shared/source_languages.py).

A guard fails at edit time if a language is added to the tool but not to the packaged dependency
list, so you will be told if you miss half of it. That guard is doing you a favour — a grammar
missing from the default install is classified as a **packaging defect, not a user error** (NFR-P3).

### 4. Add a host for the packaged assistant commands

The host registry in [`argus/commands/hosts.py`](argus/commands/hosts.py) is deliberately **closed**
and currently has exactly one verified entry: Claude Code. An entry is added only once its exact
configuration directory and its exact resulting command spelling have been verified on a real
machine. If you use a different assistant and can verify both, that is one reviewed registry entry.

### 5. Adjudicate findings, or nominate a corpus repository

This is the one that moves the project's hardest open problem, so it needs context.

Argus carries a mandatory disclosure saying its finding precision has not been independently
validated. That notice is removed only when a ≥80% precision gate is met. The gate is currently
**unevaluable, not unmet**: run against the five ratified mature repositories, the corrected
detector read 1,960 source files, scored 5,129 test functions, emitted 4,284 advisory findings, and
promoted **zero** to verdict-eligible. Precision is `TP / (TP + FP)`; with an empty numerator and
denominator the ratio is undefined rather than low.

Two ways to help, and they are different:

- **Nominate a repository** with real, findable defects — code where tests exist but do not test,
  where functions are unreachable, where assertions do not assert. Agent-generated code is the
  richest source. Candidates are pre-registered and sealed *before* Argus is run against them, so
  nominating one is an act with real evidential weight.
- **Adjudicate**. Judge emitted findings true or false positive against the written protocol.
  Adjudication by someone outside the implementing team is worth strictly more than adjudication by
  the author — the current record derives as `NOT_INDEPENDENT`, because all 31 live judgements were
  authored by the tool's own author.

Neither of these is a code change, and both matter more than most code changes.

### 6. Documentation

The README is long because it doubles as an audit record. If you found something confusing, say so
in an issue — "I could not work out how to X" is a legitimate and useful report.

---

## House rules

These are unusual. They are also enforced, so please read them once.

### Claims are measured, not asserted

If you write that something is true, the repository will generally want a way to check it. A claim
about a workflow run cites the run **and the sha it covers**. A claim about repository state cites
the command that measured it, with a date. A claim with neither is recorded as `NOT ESTABLISHED` —
which is a first-class, acceptable state here, not a failure.

### Corrections are struck, never erased

When a statement turns out to be wrong, the convention (`architecture.md` §3.4) is to strike it
through and write the correction beside it, dated — not to delete it. The record that something was
wrong is what makes the correction auditable. You will see `~~struck text~~` followed by a
🔧 or 🔴 correction block throughout the codebase and docs. Please follow it.

### Values are derived, not typed

If a number or a string can be computed from the code, compute it. Hand-typed copies of derived
facts drift, and several guards exist specifically to catch that. If you find yourself typing a
count, a version, a file list or a status that something else already knows, that is a signal.

### Tests may be strengthened, never loosened

If a guard fails, the fix is the code or the claim — not the guard. Weakening an assertion to make a
change land is the one thing that will get a PR rejected on principle. If a guard is genuinely
wrong, say so explicitly in the PR and explain why; that conversation is welcome.

### Line endings and byte invariants

Some committed artifacts are byte-asserted. Do not reformat files you are not changing, and do not
let an editor normalise line endings across a whole file. If a diff shows every line changed,
something has rewritten the file's endings.

---

## Pull requests

1. Open an issue first for anything larger than a typo — it saves you writing code that turns out to
   be a locked design decision.
2. Keep the change and its tests in the same commit; keep mechanical regenerations in a separate one.
3. Run `pytest tests/`, `mypy argus`, and `bandit -r argus --severity-level medium` before pushing.
4. Describe what you **measured**, not only what you changed.

## Security

Please do not open a public issue for a security problem. See [SECURITY.md](SECURITY.md).

## Licence

By contributing you agree that your contributions are licensed under the
[MIT License](LICENSE).
