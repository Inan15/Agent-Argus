# Argus — first run

> Instrument status: Argus's own finding precision has not been independently validated. Its
> findings rest on the Argus dogfood corpus, a self-audit of this repository with no human
> true-positive/false-positive adjudication behind it. This notice is removed only when Epic
> 13's human adjudication clears the >=80% precision gate; nothing else removes it.

**This page is repository documentation.** It is *not* packaged in the wheel — the
distribution ships `argus/**` only — so it lives here, in the git repository, and the link
from [`README.md`](../README.md) is how you reach it. The verdict vocabulary, the exit codes
and every `argus …` command line on this page are checked by a test against the code, not
transcribed from it. The rest is prose: where a command is documented but is not an exercised
capability, this page says so at that command rather than here.

It covers exactly four things: install, your first audit, reading the ledger, and what each
verdict means. For the full integration surface — CI, the GitHub Action, the report types,
the assistant commands — read [`README.md`](../README.md). There is no tutorial here; the
tool's own `--help` and its own output are the reference, by design (FR37: what you need to
do next is in the output you are already holding).

---

## 1. Install

```bash
pip install "argus-agent @ git+https://github.com/Inan15/Agent-Argus.git@v0.1.0"
```

`argus-agent` is not on a package index. The command above resolves it straight from this
repository at a tag.

> ⚠️ **This command does not resolve today.** Tag `v0.1.0` has not been created or pushed, so
> `pip` cannot find the ref and the install fails. It is the documented shape, not an
> exercised capability. `README.md` carries the full caveat, including what a private
> repository costs a consumer's CI.

Every supported language grammar is in the default install. If a grammar is missing or will
not load, the run says so on stderr and names the package that would fix it — a lower
coverage number is never left to look like a judgement about your code.

## 2. Your first audit

```bash
argus audit .
```

No flags are required. Argus audits whatever source state is present — a git repository at a
commit, a dirty working tree, or a plain directory with no git metadata at all — and records
which of those it examined.

Two streams, and they do different jobs:

- **stdout** is the machine contract. One line: `verdict=<TOKEN> deep_ratio=<num/den>
  blocking_findings=<n>`, plus the assessed scope when the audit was narrowed. Parse this.
- **stderr** is the human register: the ship-readiness block, what each disclosure means, and
  what to do next.

Nothing is transmitted anywhere. The deep, LLM-backed pass is off by default, always, and
`--deep-audit` is the only thing that turns it on.

To see every accepted argument with its default:

```bash
argus audit --help
```

To write the Markdown reports as well:

```bash
argus audit . --report-dir ./argus-reports
```

`--reports` selects which report types are rendered and does nothing on its own — reports are
written only when `--report-dir` is set, and the run tells you if you asked for one without
the other.

## 3. Reading the ledger

Every audited file is graded, and the grades are counted rather than averaged:

- **`audited_deep`** — the file parsed cleanly, has at least one real function or class, and
  every enabled deterministic detector ran over it. On a default run this is a structural and
  deterministic assurance grade, **not** a comprehension grade; the run says so in those words.
- **`audited_shallow`** — examined, but not gradeable deeply. Test files are shallow by
  construction: they are the *subject* of the vacuous-test pass, never a target of deep
  grounding.
- **`skipped`** — examined and ungradable (an unparseable file, or a file beyond the budget
  ceiling). It stays in the denominator. Argus never fabricates a grade to improve a ratio.

`deep_ratio` is `audited_deep / total`, printed as an exact fraction and never as a rounded
percentage. The default `--coverage-scope application` holds test files out of the assessed
population and discloses that it did; both ratios are printed either way, and the coverage
floor is re-applied *inside* the scope, so narrowing can never lower a bar.

The written ledger and the verdict artifact live under `.argus/` in the audited repository.

## 4. What each verdict means

| Verdict | Exit | What it says |
|---|---|---|
| `RELEASE_READY` | `0` | No blocking problems found, and enough of the code was examined deeply to say so. |
| `NOT_READY_FOR_RELEASE` | `2` | At least one verdict-blocking finding must be resolved. This is a statement about the code. |
| `INSUFFICIENT_COVERAGE` | `3` | Too little was examined deeply to make a call, **or** a coverage / critical-subsystem gate was unmet with nothing found. This is a statement about the audit, not about the code — the human register distinguishes the two cases in words. |
| *(no verdict)* | `1` | The audit did not complete, so no verdict exists. The run names the typed cause and what to do about it; if it says `INTERNAL DEFECT`, that is a bug in Argus rather than a problem with your repository, and it names where to report it. |

Exit `1` is reserved and is never a verdict. A command line the parser rejects also exits
`1` — a rejected invocation ran no audit, so publishing an assessment for it would be a
statement about a run that never happened.

`RELEASE_READY` is a bounded claim: it says the enabled deterministic passes found nothing
blocking within the assessed population. It is never a claim that the code is correct, and
the instrument-status notice at the top of this page bounds how much weight it carries.
