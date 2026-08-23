# Argus — first run

> Instrument status: Argus's finding precision has not been independently validated. Its
> findings rest on the Argus dogfood corpus, a self-audit of this repository with no human
> true-positive/false-positive adjudication behind it. This notice is removed only when Epic
> 13's human adjudication clears the >=80% precision gate; nothing else removes it.

**This page is repository documentation.** It is *not* packaged in the wheel — the
distribution ships `argus/**` only — so it lives here, in the git repository, and the link
from [`README.md`](../README.md) is how you reach it. The verdict vocabulary, the exit codes
and every `argus …` command line on this page are checked by a test against the code, not
transcribed from it. The rest is prose: where a command is documented but is not an exercised
capability, this page says so at that command rather than here.

It covers exactly five things: install, your first audit, reading the ledger, what each
verdict means, and — only if you opt into the deep pass — how to configure a provider. For the full integration surface — CI, the GitHub Action, the report types,
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

> ⚠️ **This command does not resolve today.** Tag `v0.1.0` has not been created or pushed
> (`git tag -l` is empty at this commit), so `pip` cannot find the ref and the install
> fails. It is the documented shape, not an exercised capability. `README.md` carries the
> full caveat.

**And it would not resolve even with the tag**, which this page used to leave to `README.md`
and now states where you meet the command (Story 12.9 / AC4):

Repository visibility, MEASURED 2026-08-15 by `gh repo view Inan15/Agent-Argus --json
visibility,isPrivate` -> `PRIVATE` / `isPrivate: true`. What that costs a consumer, stated
plainly: while it stays private the pinned install cannot resolve for anybody — tag or no
tag — without a read credential carried in the URL
(`git+https://<credential>@github.com/...`), and a GitHub Release on a private repository is
not publicly resolvable either. Making the repository public is an outward-facing operator
act that has not been taken. This is a dated measurement, not a standing claim: re-run the
command above before relying on it.

Until then, the form that works today is a clone plus `pip install -e .`.

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
`--deep-audit` is the only thing that turns it on. If you intend to pass it, read §5 first —
it carries a limitation worth knowing before you configure a paid provider.

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

## 5. Configuring a provider (only if you opt into `--deep-audit`)

**Skip this section unless you are passing `--deep-audit`.** A default run needs no key, no
endpoint and no account, and transmits nothing. Everything below is inert until the flag is
present on the command line.

> ⚠️ **Read this before you configure a paid provider.** The bundled adapter does not return
> the model's answer in the field the pass requires, so a correctly configured provider still
> yields **zero** delivered deep reads today: every dispatch — including a fully successful one
> against a healthy provider — degrades as `empty-response`, and the files are recorded
> `audited_shallow`. The request really is sent and a paid provider really will bill for it.
> This is a known limitation of the shipped adapter (`DF-12-2-D`), not a misconfiguration on
> your side, and no value of the variables below changes it. Configure this to exercise the
> egress path; do not configure it expecting depth.

### The three variables

Credentials are read from the environment only — there is no config file, no CLI flag and no
keyring. The adapter reads them when it is constructed, and it is constructed only by
`--deep-audit`.

| Variable | What it sets | Default if unset |
|---|---|---|
| `OPENAI_BASE_URL` / `OLLAMA_HOST` / `OLLAMA_URL` | The provider endpoint. **First non-empty wins.** | none — the pass degrades |
| `OPENAI_API_KEY` | Sent as an `Authorization: Bearer` header | the literal `mock-key` |
| `ARGUS_LLM_MODEL` / `OLLAMA_MODEL` | The model id | `gpt-4o-mini` |

**The endpoint variable is the switch, not the key.** With all three endpoint variables unset,
no adapter is constructed at all: the run says so on stderr, records a
`deep_pass_degraded:provider_unconfigured` finding per file, and downgrades their coverage. If
you export `OPENAI_API_KEY` alone and nothing appears to happen, this is why. Argus refuses to
construct the adapter in that state on purpose — an adapter with no endpoint returns a
synthetic recording that is indistinguishable from a real one, so refusing is what keeps a
fabricated deep read out of the verdict.

**Setting these variables is not consent.** They are configuration and nothing else. With
`--deep-audit` absent, the module that reads them is never imported and no adapter exists,
whatever the environment holds.

### An OpenAI-compatible endpoint

```bash
export OPENAI_BASE_URL=https://api.openai.com
export OPENAI_API_KEY=sk-...
export ARGUS_LLM_MODEL=gpt-4o-mini
argus audit . --deep-audit
```

**Omit the `/v1` suffix.** The adapter appends `/v1/chat/completions` to whatever you set, so
the near-universal habit of exporting a base URL ending in `/v1` produces a doubled path and a
404 — which reaches you as a `dispatch-failed` degradation, not as a configuration error.

### A local Ollama endpoint

```bash
export OLLAMA_HOST=http://localhost:11434
export ARGUS_LLM_MODEL=llama3.1
argus audit . --deep-audit
```

No key is needed locally; the `mock-key` default is sent and ignored. Note the request timeout
is 10 seconds and is not configurable, which a cold local model can exceed.

### What this path does not reach

The live pass speaks one dialect: OpenAI-style chat completions with `Bearer` auth. The
Anthropic API is not reachable this way — it expects an `x-api-key` header and an
`anthropic-version` header, neither of which the adapter sends. The `litellm` multi-provider
layer in the `[llm]` extra is not used by this path either; the pass constructs its adapter
with litellm disabled, so installing that extra widens nothing here.

### What leaves your machine

Repo-relative file paths, a tier hint, and a prompt-template version. File contents are not
sent, and neither are secrets. Before the first byte, the run prints what will be transmitted
and the scheme and host of the recipient — the full URL is never echoed, because a URL can
carry a token in its userinfo or query string.
